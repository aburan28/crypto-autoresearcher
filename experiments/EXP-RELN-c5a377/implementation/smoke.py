"""Smoke check (implementation only), protocol v4: two driver dry runs on the
smallest fixture (b16-s13, smallest q) in the smoke namespace, then a summary
of identities, controls, run-record conformance and agreement. The summary
omits every treatment delta reading, ER-null delta input and subcritical-rule
input, and never calls the verdict rule.

AMD-20260929-cc7226 FX-6: every smoke budget differs from every frozen A1/A2
budget of the trial plan (all nine fixtures); a clash is refused here and in
driver.py. Output goes under smoke/v4/; the earlier smoke/dry/ and
smoke/smoke_summary.json are immutable and never rewritten.

  DRYRUN-v4-tiny      A1'=64,  A2'=256,  4 null replicates, 2 rho targets
  DRYRUN-v4-controls  A1'=400, A2'=1500, 8 null replicates, 4 rho targets
                      (enough relations that LP log recovery determines logs,
                      so the scrambled known false is exercised)

  python3 smoke.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import driver  # noqa: E402
import fixtures  # noqa: E402

SMOKE_DIR = HERE / "smoke" / "v4"
DRY_DIR = SMOKE_DIR / "dry"
FIXTURE = "b16-s13"
CONFIGS = {"DRYRUN-v4-tiny": (64, 256, 4, 2), "DRYRUN-v4-controls": (400, 1500, 8, 4)}
RUN_KEYS = ("id", "experiment_id", "status", "code", "environment", "inputs", "timing", "result")


def check_budgets(plan: dict, configs=CONFIGS) -> list:
    frozen = driver.frozen_budgets(plan)
    return sorted((rid, a) for rid, (a1, a2, _, _) in configs.items() for a in (a1, a2) if a in frozen)


def summarize(run_dir: Path) -> dict:
    import yaml
    raw = json.loads((run_dir / "raw-result.json").read_text())
    man = yaml.safe_load((run_dir / "manifest.yaml").read_text())
    run = man["run"]
    out = {"run_dir": str(run_dir.relative_to(HERE)), "manifest_status": run["status"],
           "namespace": run["inputs"]["namespace"], "C7_readings": run["inputs"]["admission_readings_C7"],
           "run_record": {
               "top_level_run_block": isinstance(run, dict),
               "required_keys_present": all(k in run for k in RUN_KEYS),
               "protocol_version": run["protocol_version"],
               "protocol_records": {k: v["sha256"] for k, v in run["inputs"]["protocol"]["records"].items()},
               "files_present": {f: (run_dir / f).is_file() for f in
                                 ("manifest.yaml", "command.txt", "environment.json", "stdout.log",
                                  "stderr.log", "raw-result.json")},
               "command_txt": (run_dir / "command.txt").read_text().strip(),
               "environment_dependencies": json.loads((run_dir / "environment.json").read_text())["dependencies"],
               "environment_sage_version": json.loads((run_dir / "environment.json").read_text())["sage_version"]},
           "cells": []}
    for c in raw["cells"]:
        row = {"fixture_id": c["fixture_id"], "ns": c["ns"], "procedure_defects": c["procedure_defects"],
               "peak_rss_bytes_self": c["peak_rss_bytes"],
               "peak_rss_bytes_wait4": next(m["peak_rss_bytes"] for m in man["driver"]["cells"]
                                            if m["fixture_id"] == c["fixture_id"]),
               "L": c["header"]["L"], "scan_size": c["header"]["scan_size"], "budgets": []}
        for b in c["budgets"]:
            g = b["graph"]
            kp = b["known_positive"]
            row["budgets"].append({
                "budget": b["budget"], "attempts": b["attempts"], "outcome_counts": b["outcome_counts"],
                "identities": {
                    "cycle_rank_eq_gf2_dimension": g["cycle_rank_identity_ok"],
                    "horton_size_eq_cycle_rank": b["horton"].get("size_identity_ok"),
                    "horton_all_even_degree": b["horton"].get("all_even_degree"),
                    "charged_total_eq_setup_plus_attempts": b["accounting_audit"]["recomputed_total_group_ops"]
                    == b["charged"]["total_group_ops"]},
                "controls": {
                    "rewire_replicates": len(b["null_rewire"]["replicates"]),
                    "rewire_identity_ok": all(r["cycle_rank_identity_ok"] for r in b["null_rewire"]["replicates"]),
                    "er_replicates_feasible": b["null_er"]["feasible"],
                    "known_positive": kp["status"],
                    "known_positive_gate_min_V": kp.get("gate_min_V"),
                    "known_positive_V_at_or_above_gate_min": (kp.get("gate_min_V") is not None
                                                             and kp.get("V", 0) >= kp["gate_min_V"]),
                    "known_false": b["known_false"]["status"],
                    "known_false_inconsistent_rows": b["known_false"]["recovery"]["inconsistent_rows"],
                    "known_false_verification_failures": b["known_false"]["recovery"]["verification_failures"],
                    "treatment_recovery_verification_passed": b["recovery"]["verification_passed"],
                    "treatment_nontrivial_determined": b["recovery"]["nontrivial_determined"],
                    "accounting_audit_accepted": b["accounting_audit"]["accepted"],
                    "audit_replayed": b["accounting_audit"]["n_replayed"],
                    "audit_replay_mismatches": b["accounting_audit"]["replay_mismatches"],
                    "relations_certified": b["accounting_audit"]["relations_certified"],
                    "certificate_failures": b["accounting_audit"]["certificate_failures"]}})
        rs = c["rho"]["summary"]
        row["rho"] = {"n_targets": rs["n_targets"], "n_solved_verified": rs["n_solved"],
                      "n_failed": rs["n_failed"]}
        out["cells"].append(row)
    return out


def main():
    plan = json.loads((HERE / "trial-plan-v2.json").read_text())
    clash = check_budgets(plan)
    if clash:
        print(f"REFUSED: smoke budgets equal frozen A1/A2 budgets: {clash}", file=sys.stderr)
        return 2
    summary_path = SMOKE_DIR / "smoke_summary.json"
    if summary_path.exists():
        print(f"REFUSED: {summary_path} exists (smoke records are immutable)", file=sys.stderr)
        return 2
    DRY_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"fixture": FIXTURE, "protocol_version": driver.PROTOCOL_VERSION,
               "note": "smoke namespace only; budgets differ from every frozen A1/A2; no delta, ER-null "
                       "delta, subcritical-rule input or verdict metric reported",
               "frozen_budgets_checked": sorted(driver.frozen_budgets(plan)), "runs": {}}
    for rid, (a1, a2, reps, rho_t) in CONFIGS.items():
        code = driver.main(["--smoke-dry-run", "--run-id", rid, "--runs-dir", str(DRY_DIR),
                            "--dry-fixture", FIXTURE, "--dry-a1", str(a1), "--dry-a2", str(a2),
                            "--dry-replicates", str(reps), "--dry-rho-targets", str(rho_t)])
        s = summarize(DRY_DIR / rid)
        s["driver_exit_code"] = code
        summary["runs"][rid] = s
    summary_path.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(summary_path, fixtures.sha256_file(summary_path))
    return 0 if all(r["driver_exit_code"] == 0 for r in summary["runs"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
