#!/usr/bin/env python3
from __future__ import annotations

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

PREVIOUS_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001" / "src" / "verify_source_aware_replication_harness.py"
SELECTOR_SOURCE = SCRIPT_PATH.with_name("compositional_suffix_selector.py")


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = _load("source_aware_verifier_for_orbit_replication", PREVIOUS_SOURCE)
SELECTOR = _load("compositional_suffix_selector_verifier", SELECTOR_SOURCE)
BASE.SELECTOR = SELECTOR
BASE.SELECTOR_SOURCE = SELECTOR_SOURCE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_compositional_replication_harness.py GENERATOR_RAW_RESULT")
    generator_raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(generator_raw_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "generator_valid": raw.get("valid") is True,
        "inputs": raw.get("inputs", {}).get("seeds") == BASE.FRESH_SEEDS and raw.get("inputs", {}).get("budgets") == BASE.BUDGETS and raw.get("inputs", {}).get("selector") == SELECTOR.SELECTOR_NAME,
        "case_count": len(raw.get("cases", [])) == len(BASE.FRESH_SEEDS),
    }
    with tempfile.TemporaryDirectory(prefix="tt-source-orbit-replication-verify-") as temp:
        temp_root = Path(temp)
        for seed, case in zip(BASE.FRESH_SEEDS, raw.get("cases", [])):
            fixture = BASE._canonical_fixture(BASE.FRESH.run_experiment([14], seed, BASE.FAMILIES, 0.5, 32))
            fixture_path = temp_root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            curve_id = fixture["instances"][0]["curve"]["id"]
            relation_path = temp_root / f"relation-{seed}.json"
            relation_input = BASE.INPUT.write_fixture_record(relation_path, fixture_path, curve_id, BASE.FAMILIES)
            instance = fixture["instances"][0]
            selector_orders = {
                family["family"]: BASE._selector_order(instance["curve"], family)
                for family in instance["families"]
            }
            candidate = case["candidate"]
            original_protocol = candidate.get("protocol")
            candidate["protocol"] = "EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001-candidate-v1"
            candidate_checks = BASE._verify_candidate(case, fixture_path, relation_path, fixture, relation_input, selector_orders)
            candidate["protocol"] = original_protocol
            candidate_checks["orbit_protocol"] = original_protocol == "EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001-candidate-v1"
            candidate_checks["orbit_selector_name"] = candidate.get("config", {}).get("locator") == SELECTOR.SELECTOR_NAME
            rho_checks = BASE._verify_rho(case, fixture, relation_input)
            for name, value in candidate_checks.items():
                checks[f"{seed}_candidate_{name}"] = value
            for name, value in rho_checks.items():
                checks[f"{seed}_rho_{name}"] = value
            checks[f"{seed}_curve_match"] = case.get("curve_id") == curve_id
    checks["valid"] = all(checks.values())
    output = {
        "valid": checks["valid"],
        "protocol": "EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001-harness-verifier-v1",
        "input": {"sha256": _sha256(generator_raw_path), "path": str(generator_raw_path)},
        "checks": checks,
        "summary": {
            "accepted_subfull_budgets": raw.get("summary", {}).get("accepted_subfull_budgets"),
            "boundary": "Independent source-only orbit-selector regeneration, support/witness checks, and direct rho certificate verification for two fresh 14-bit toy curves; no generic ECDLP or exponent claim.",
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

