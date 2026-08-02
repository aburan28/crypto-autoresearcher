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
BASE_VERIFY_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "src" / "verify_orbit_quotient_replication_harness.py"
BASE_GENERATOR_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "src" / "run_orbit_quotient_replication_harness.py"
LOCATOR_SOURCE = SCRIPT_PATH.with_name("shared_sign_locator.py")
GENERATOR_SOURCE = SCRIPT_PATH.with_name("run_shared_sign_replication_harness.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VERIFY = load("shared_sign_base_verifier", BASE_VERIFY_SOURCE)
BASE = VERIFY.BASE
INPUT = VERIFY.INPUT
FRESH = VERIFY.FRESH
FRESH_SEEDS = VERIFY.FRESH_SEEDS
FAMILIES = VERIFY.FAMILIES
BUDGETS = ["32", "44", "full"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    def normalize(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: normalize(child) for key, child in item.items() if key not in {"wall_seconds", "total_wall_seconds"}}
        if isinstance(item, list):
            return [normalize(child) for child in item]
        return item
    return normalize(value)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_shared_sign_replication_harness.py GENERATOR_RAW_RESULT")
    raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    checks = {"generator_valid": raw.get("valid") is True, "inputs": raw.get("inputs", {}).get("seeds") == FRESH_SEEDS and raw.get("inputs", {}).get("budgets") == BUDGETS and raw.get("inputs", {}).get("families") == FAMILIES, "case_count": len(raw.get("cases", [])) == len(FRESH_SEEDS)}
    old_generator = VERIFY.GENERATOR_SOURCE
    old_locator = VERIFY.LOCATOR_SOURCE
    old_budgets = VERIFY.BUDGETS
    VERIFY.GENERATOR_SOURCE = GENERATOR_SOURCE
    VERIFY.LOCATOR_SOURCE = LOCATOR_SOURCE
    VERIFY.BUDGETS = BUDGETS
    with tempfile.TemporaryDirectory(prefix="tt-shared-sign-verify-") as temp:
        root = Path(temp)
        for seed, case in zip(FRESH_SEEDS, raw.get("cases", [])):
            fixture = canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            relation_path = root / f"relation-{seed}.json"
            transformed = copy.deepcopy(case)
            transformed["candidate"]["protocol"] = "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001-candidate-v1"
            result = VERIFY.verify_case(transformed, fixture, fixture_path, relation_path)
            for name, value in result.items():
                checks[f"{seed}_{name}"] = value
            checks[f"{seed}_curve_match"] = case.get("curve_id") == fixture["instances"][0]["curve"]["id"]
            for row in case.get("candidate", {}).get("rows", []):
                for budget in row.get("budgets", []):
                    ops = budget.get("candidate_quotient_ops", {})
                    advice = budget.get("candidate_advice", {})
                    accounting = (
                        int(ops.get("paired_source_calls", -1)) == int(advice.get("source_orbit_cache_entries", -2))
                        and int(ops.get("paired_source_calls", -1)) == int(ops.get("paired_shared_inversions", 0)) + int(ops.get("paired_fallback_calls", 0)) + int(ops.get("paired_identity_calls", 0))
                    )
                    checks[f"{seed}_{row.get('family')}_{budget.get('budget_label')}_paired_accounting"] = accounting
    VERIFY.GENERATOR_SOURCE = old_generator
    VERIFY.LOCATOR_SOURCE = old_locator
    VERIFY.BUDGETS = old_budgets
    checks["valid"] = all(checks.values())
    output = {"valid": checks["valid"], "protocol": "EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001-harness-verifier-v1", "input": {"sha256": sha256(raw_path), "path": str(raw_path)}, "checks": checks, "summary": {"accepted_subfull_budgets": raw.get("summary", {}).get("accepted_subfull_budgets"), "boundary": "Independent fixture and orbit partition regeneration, lifted witness checks, paired-operator hash checks, and matched rho certificates; no generic ECDLP or exponent claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
