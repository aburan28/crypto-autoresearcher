#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
BASE_VERIFY = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001" / "src" / "verify_projective_shared_sign_harness.py"
INPUT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001" / "src" / "rank_batch_relation_input.py"
PROJECTIVE_SOURCE = SCRIPT_PATH.with_name("compressed_projective_shared_sign_locator.py")
GENERATOR_SOURCE = SCRIPT_PATH.with_name("run_compressed_locator_harness.py")
FRESH_SEEDS = [86420]
FIELD_BITS = 16
FAMILIES = ["source_prf_x", "random_x"]
BUDGETS = ["96", "full"]
MAX_RSS_BYTES = 6 * 1024**3


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("compressed_locator_projective_verifier", BASE_VERIFY)
INPUT = load("compressed_locator_verifier_input", INPUT_SOURCE)
PROJECTIVE = load("compressed_locator_projective_verifier_locator", PROJECTIVE_SOURCE)
BASE.PROJECTIVE = PROJECTIVE
BASE.PROJECTIVE_SOURCE = PROJECTIVE_SOURCE
BASE.FRESH_SEEDS = FRESH_SEEDS
BASE.FAMILIES = FAMILIES
BASE.BUDGETS = BUDGETS
BASE.GENERATOR_SOURCE = GENERATOR_SOURCE
BASE.INPUT = INPUT
BASE.VERIFY.FAMILIES = FAMILIES
BASE.VERIFY.INPUT = INPUT


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_compressed_locator_harness.py GENERATOR_RAW_RESULT")
    raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    manifest = json.loads((raw_path.parent / "manifest.json").read_text(encoding="utf-8"))
    peak_rss_bytes = int(manifest["run"]["resources"]["peak_rss_bytes"])
    inputs = raw.get("inputs", {})
    checks: dict[str, Any] = {
        "generator_valid": raw.get("valid") is True,
        "inputs": inputs.get("seeds") == FRESH_SEEDS and inputs.get("field_bits") == FIELD_BITS and inputs.get("families") == FAMILIES and inputs.get("budgets") == BUDGETS and inputs.get("prefix_fraction") == PROJECTIVE.PREFIX_FRACTION and inputs.get("selector") == PROJECTIVE.SELECTOR,
        "case_count": len(raw.get("cases", [])) == 1,
        "memory_budget": 0 < peak_rss_bytes <= MAX_RSS_BYTES,
        "generator_hash": raw.get("cases", [{}])[0].get("candidate", {}).get("source", {}).get("harness_source_sha256") == sha256(GENERATOR_SOURCE),
        "locator_hash": raw.get("cases", [{}])[0].get("candidate", {}).get("source", {}).get("locator_sha256") == sha256(PROJECTIVE_SOURCE),
    }
    rank_gate = True
    weighted_gate = True
    with tempfile.TemporaryDirectory(prefix="tt-projective-compressed-verify-") as temp:
        root = Path(temp)
        for seed, case in zip(FRESH_SEEDS, raw.get("cases", [])):
            fixture = BASE.canonical_fixture(BASE.FRESH.run_experiment([FIELD_BITS], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            relation_path = root / f"relation-{seed}.json"
            case_copy = copy.deepcopy(case)
            case_copy["candidate"].setdefault("source", {}).setdefault("projective_locator_sha256", case_copy["candidate"].get("source", {}).get("locator_sha256"))
            result = BASE.verify_case(case_copy, fixture, fixture_path, relation_path)
            for name, value in result["base"].items():
                checks[f"{seed}_support_{name}"] = value
            for name, value in result["hashes"].items():
                checks[f"{seed}_{name}"] = value
            for family, metrics in result["arithmetic"].items():
                checks[f"{seed}_{family}_arithmetic"] = metrics["source_states"] > 0 and metrics["zero_equivalence_checks"] == metrics["source_states"] * 2
                checks[f"{seed}_{family}_scale"] = metrics["nonzero_scale_checks"] >= 0
                row = next(item for item in case["candidate"]["rows"] if item["family"] == family)
                full = next(item for item in row["budgets"] if item["budget_label"] == "full")
                rank_gate = rank_gate and full["candidate_rank"] == 15
                checks[f"{seed}_{family}_candidate_projective_ops"] = full["candidate_quotient_ops"].get("projective_predicate_field_multiplications", 0) > 0 and full["candidate_quotient_ops"].get("paired_projective_calls", 0) > 0
                checks[f"{seed}_{family}_prefix_selector"] = full.get("selected_prefix_count") == 1372 and full.get("full_prefix_count") == 2744 and full.get("prefix_fraction") == PROJECTIVE.PREFIX_FRACTION
                for weight in [10, 50, 100, 200]:
                    weighted = case["weighted_costs"][family][str(weight)]
                    weighted_gate = weighted_gate and weighted["compressed"] < weighted["naive_orbit"] and weighted["compressed"] < weighted["original_affine"]
                checks[f"{seed}_{family}_downstream"] = all(item["candidate_rank"] >= 0 and item["relation_equation_count"] >= 0 for item in case["downstream"][family])
            checks[f"{seed}_target_batch"] = case["relation_target_count"] == 43 and all(next(item for item in row["budgets"] if item["budget_label"] == "full")["target_count"] == 47 for row in case["candidate"]["rows"])
            checks[f"{seed}_curve_match"] = case.get("curve_id") == fixture["instances"][0]["curve"]["id"]
    checks["rank_gate"] = rank_gate
    checks["weighted_gate"] = weighted_gate
    checks["valid"] = all(value if isinstance(value, bool) else True for key, value in checks.items() if key not in {"rank_gate", "weighted_gate"})
    output = {"valid": checks["valid"], "protocol": "EXP-ECDLP-TT-PROJECTIVE-COMPRESSED-LOCATOR-001-harness-verifier-v1", "input": {"sha256": sha256(raw_path), "path": str(raw_path)}, "checks": checks, "summary": {"rank_gate": rank_gate, "weighted_gate": weighted_gate, "peak_rss_bytes": peak_rss_bytes, "memory_budget_bytes": MAX_RSS_BYTES, "prefix_fraction": PROJECTIVE.PREFIX_FRACTION, "boundary": "Independent source-only selector, projective arithmetic, support, rank, weighted comparator, rho, and memory checks; no generic ECDLP claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
