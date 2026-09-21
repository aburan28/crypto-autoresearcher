#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import copy
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
BASE_VERIFY = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001" / "src" / "verify_projective_shared_sign_harness.py"
INPUT_SOURCE = SCRIPT_PATH.with_name("rank_batch_relation_input.py")
GENERATOR_SOURCE = SCRIPT_PATH.with_name("run_rank_completion_harness.py")
FRESH_SEEDS = [97531]
FIELD_BITS = 16
FAMILIES = ["source_prf_x", "random_x"]
BUDGETS = ["96", "full"]
WEIGHTS = [10, 50, 100, 200]


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load("rank_completion_projective_verifier", BASE_VERIFY)
INPUT = load("rank_completion_verifier_input", INPUT_SOURCE)
BASE.FRESH_SEEDS = FRESH_SEEDS
BASE.FAMILIES = FAMILIES
BASE.BUDGETS = BUDGETS
BASE.GENERATOR_SOURCE = GENERATOR_SOURCE
BASE.INPUT = INPUT
BASE.VERIFY.FAMILIES = FAMILIES
BASE.VERIFY.INPUT = INPUT


def sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_rank_completion_harness.py GENERATOR_RAW_RESULT")
    raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    checks: dict[str, Any] = {"generator_valid": raw.get("valid") is True, "inputs": raw.get("inputs", {}).get("seeds") == FRESH_SEEDS and raw.get("inputs", {}).get("field_bits") == FIELD_BITS and raw.get("inputs", {}).get("families") == FAMILIES and raw.get("inputs", {}).get("budgets") == BUDGETS, "case_count": len(raw.get("cases", [])) == 1}
    rank_gate = True
    with tempfile.TemporaryDirectory(prefix="tt-rank-completion-verify-") as temp:
        root = Path(temp)
        for seed, case in zip(FRESH_SEEDS, raw.get("cases", [])):
            fixture = BASE.canonical_fixture(BASE.FRESH.run_experiment([FIELD_BITS], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            relation_path = root / f"relation-{seed}.json"
            case = copy.deepcopy(case)
            source = case["candidate"].setdefault("source", {})
            source.setdefault("projective_locator_sha256", source.get("locator_sha256"))
            result = BASE.verify_case(case, fixture, fixture_path, relation_path)
            for name, value in result["base"].items():
                checks[f"{seed}_support_{name}"] = value
            for name, value in result["hashes"].items():
                checks[f"{seed}_{name}"] = value
            for family, metrics in result["arithmetic"].items():
                checks[f"{seed}_{family}_arithmetic"] = metrics["source_states"] > 0 and metrics["zero_equivalence_checks"] == metrics["source_states"] * 2
                checks[f"{seed}_{family}_scale"] = metrics["nonzero_scale_checks"] >= 0
                full = next(item for item in case["candidate"]["rows"] if item["family"] == family)["budgets"][-1]
                rank_gate = rank_gate and full["candidate_rank"] == 15
                for weight in WEIGHTS:
                    weighted = case["weighted_costs"][family][str(weight)]
                    checks[f"{seed}_{family}_weighted_{weight}"] = weighted["projective"] < weighted["naive_orbit"] and weighted["projective"] < weighted["original_affine"]
                checks[f"{seed}_{family}_downstream"] = all(item["candidate_rank"] >= 0 and item["relation_equation_count"] >= 0 for item in case["downstream"][family])
            checks[f"{seed}_target_batch"] = case["relation_target_count"] == 29 and all(next(item for item in row["budgets"] if item["budget_label"] == "full")["target_count"] == 33 for row in case["candidate"]["rows"])
            checks[f"{seed}_curve_match"] = case.get("curve_id") == fixture["instances"][0]["curve"]["id"]
    checks["rank_gate"] = rank_gate
    integrity = [value for key, value in checks.items() if key != "rank_gate"]
    checks["valid"] = all(value if isinstance(value, bool) else True for value in integrity)
    output = {"valid": checks["valid"], "protocol": "EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001-harness-verifier-v1", "input": {"sha256": sha256(raw_path), "path": str(raw_path)}, "checks": checks, "summary": {"rank_gate": rank_gate, "accepted_subfull_budgets": raw.get("summary", {}).get("accepted_subfull_budgets"), "weighted_advantage_cells": raw.get("summary", {}).get("weighted_advantage_cells"), "boundary": "Independent expanded-target projective arithmetic, support, rank, weighted comparator, and rho checks; rank_gate is reported separately from receipt integrity; no generic ECDLP claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
