"""Implementation smoke check (no scientific output): driver --smoke-dry-run on
b16-s21 in the smoke namespace with small counts, then a FULL audit replay of
every attempt and descent (membership against the exact oracle, exact
operation counts). Reports identities, controls and stage agreement only; the
C-5 ratio, exponent and verdict are never computed here.

  python3 smoke.py --run-id DRYRUN-smoke-001
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit  # noqa: E402
import common  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="DRYRUN-smoke-001")
    ap.add_argument("--runs-dir", default=str(HERE / "smoke" / "driver_dryrun"))
    args = ap.parse_args(argv)
    assert "smoke" in args.run_id
    cmd = ["nice", "-n", "10", sys.executable, str(HERE / "driver.py"), "--smoke-dry-run", "--run-id", args.run_id,
           "--runs-dir", args.runs_dir]
    rc = subprocess.run(cmd).returncode
    run_dir = Path(args.runs_dir) / args.run_id
    summary = {"driver_command": " ".join(cmd), "driver_exit_code": rc, "run_dir": str(run_dir.relative_to(HERE))}
    raw = json.loads((run_dir / "raw-result.json").read_text()) if (run_dir / "raw-result.json").exists() else None
    rep = json.loads((run_dir / "fixture_reproduction.json").read_text())
    summary["fixture_reproduction_byte_identical"] = rep.get("byte_identical")
    summary["sampled_audit_accepted"] = json.loads((run_dir / "audit.json").read_text())["accepted"] \
        if (run_dir / "audit.json").exists() else None
    cells = {}
    full_ok = True
    for entry in (raw or {}).get("cells", []):
        rpath = run_dir / entry["result_path"]
        summary.setdefault("result_sha256_match", True)
        summary["result_sha256_match"] &= common.sha256_file(rpath) == entry["result_sha256"]
        rcpt = json.loads(rpath.read_text())
        res = rcpt.get("result") or {}
        cid = rcpt["task"]["cell_id"]
        c = {"status": rcpt.get("status"), "namespace": res.get("namespace"),
             "peak_rss_bytes_recorded": bool(rcpt.get("peak_rss_bytes"))}
        if rcpt.get("status") == "ok" and res["kind"] != "rho":
            fa = audit.audit_cell(rcpt, full_replay=True)
            full_ok &= fa["accepted"]
            s1 = res["stage1"]
            c.update({
                "m": res["m"], "L": res["factor_base"]["L"], "B": res["factor_base"]["B"],
                "attempts": s1["n_attempts"], "failed_attempts": s1["n_failed_attempts"],
                "relations": s1["n_relations"],
                "full_replay_audit_accepted": fa["accepted"], "full_replay_failures": fa["failures"][:10],
                "attempts_replayed_vs_oracle": fa["stats"]["attempts_replayed"],
                "la_steps_checked": fa["stats"]["la_steps_checked"],
                "logs_verified": res["stage3"]["log_verification"],
            })
            if res["kind"] == "primary":
                import analysis
                try:
                    fxa = analysis.fxa_figure(res)
                    c["fxa_nonverdict_presence"] = {
                        "fields_present": sorted(k for k, v in fxa.items() if v is not None),
                        "cross_check": fxa["cross_check"], "stage1_attempts_substituted": fxa["rj_stage1_attempts"],
                        "descent_attempts_substituted_supplementary": fxa["rj_descent_attempts"],
                        "values": "withheld (smoke)"}
                except Exception as e:  # noqa: BLE001
                    full_ok = False
                    c["fxa_nonverdict_presence"] = {"error": repr(e)}
                c.update({
                    "k_recovered_equals_target": res["stage3"]["k_recovered"] == res["target"]["k"],
                    "la_agrees_dense_reference": res["stage3"]["agrees_dense_reference"],
                    "la_info": res["stage3"]["la_info"],
                    "descents_verified": f"{res['descents']['n_verified']}/{res['descents']['n_descents']}",
                    "descent_attempts_replayed_vs_oracle": fa["stats"]["descent_attempts_replayed"],
                    "stage2_scan_agrees_brute_force": (f"{res['stage2_alpha2']['agreement_with_brute_force']}/"
                                                       f"{res['stage2_alpha2']['n_heldout']}"),
                    "known_false": {k: res["known_false"][k] for k in
                                    ("rows_changed", "la_error", "log_verification_all_ok", "control_passed")},
                })
            if res["kind"].startswith("stage_cost"):
                c["stage2_scan_agrees_brute_force"] = (f"{res['stage2_alpha2']['agreement_with_brute_force']}/"
                                                       f"{res['stage2_alpha2']['n_heldout']}")
            if res["kind"] == "null_randfb":
                c["random_V_matches_interval_size"] = res["factor_base"]["L"] == res["interval_L"]
        elif rcpt.get("status") == "ok":
            c.update({"rho_targets": res["n_targets"], "rho_solved_and_certified": res["n_solved"],
                      "rho_audit_accepted": audit.audit_cell(rcpt)["accepted"]})
        else:
            c["reason"] = rcpt.get("reason")
        cells[cid] = c
    summary["cells"] = cells
    summary["full_replay_audit_accepted"] = full_ok
    summary["verdict_metric"] = "not computed (smoke; handoff forbids reporting it)"
    out = HERE / "smoke" / f"{args.run_id}_summary.json"
    out.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0 if rc == 0 and full_ok and summary["fixture_reproduction_byte_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
