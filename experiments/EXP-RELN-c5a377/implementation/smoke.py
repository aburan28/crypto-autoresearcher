"""Smoke check (implementation only): two driver dry runs on b16-s11 in the
smoke namespace, then a summary of identities, controls and agreement. The
summary deliberately omits the treatment graph's delta readings and never
calls the verdict rule.

  DRYRUN-tiny      A1'=64,  A2'=256, 4 null replicates, 2 rho targets
  DRYRUN-controls  A1'=249, A2'=751, 8 null replicates, 4 rho targets
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

DRY_DIR = HERE / "smoke" / "dry"
CONFIGS = {"DRYRUN-tiny": (64, 256, 4, 2), "DRYRUN-controls": (249, 751, 8, 4)}


def summarize(run_dir: Path) -> dict:
    raw = json.loads((run_dir / "raw-result.json").read_text())
    import yaml
    man = yaml.safe_load((run_dir / "manifest.yaml").read_text())
    out = {"run_dir": str(run_dir.relative_to(HERE)), "manifest_status": man["status"],
           "namespace": man["namespace"], "C7_readings": man["admission_readings_C7"],
           "cells": []}
    for c in raw["cells"]:
        row = {"fixture_id": c["fixture_id"], "ns": c["ns"], "procedure_defects": c["procedure_defects"],
               "peak_rss_bytes_self": c["peak_rss_bytes"],
               "peak_rss_bytes_wait4": next(m["peak_rss_bytes"] for m in man["cells"]
                                            if m["fixture_id"] == c["fixture_id"]),
               "L": c["header"]["L"], "scan_size": c["header"]["scan_size"], "budgets": []}
        for b in c["budgets"]:
            g = b["graph"]
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
                    "known_positive": b["known_positive"]["status"],
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
    DRY_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"fixture": "b16-s11", "note": "smoke namespace only; no verdict metric reported",
               "runs": {}}
    for rid, (a1, a2, reps, rho_t) in CONFIGS.items():
        code = driver.main(["--smoke-dry-run", "--run-id", rid, "--runs-dir", str(DRY_DIR),
                            "--dry-a1", str(a1), "--dry-a2", str(a2),
                            "--dry-replicates", str(reps), "--dry-rho-targets", str(rho_t)])
        s = summarize(DRY_DIR / rid)
        s["driver_exit_code"] = code
        summary["runs"][rid] = s
    p = HERE / "smoke" / "smoke_summary.json"
    p.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(p, fixtures.sha256_file(p))
    return 0 if all(r["driver_exit_code"] == 0 for r in summary["runs"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
