"""Implementation smoke check (no scientific output), protocol v4.

Runs driver --smoke-dry-run on a SYNTHETIC, non-frozen fixture (synthetic.py)
in the smoke namespace with small counts, then a FULL audit replay of every
attempt and descent. AMD-20260929-5a84eb FX-5, both halves:
  * it refuses any run whose cells carry a frozen fixture (checked on every
    cell receipt, whatever the driver did);
  * the summary it writes carries only pass/fail identities, controls and
    audit outcomes: no units, costs, attempt counts, ratios, exponents or
    verdicts (enforced by `assert_no_cost_fields`).

  python3 smoke.py --run-id DRYRUN-smoke-v4-001
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

SMOKE_DIR = HERE / "smoke" / "v4"
FORBIDDEN_KEY_PARTS = ("unit", "cost", "ratio", "exponent", "verdict", "attempt", "seconds", "rss", "bytes")


class FrozenFixtureRefused(RuntimeError):
    pass


def assert_no_cost_fields(obj, path="summary"):
    """Raise if any mapping key names a cost-like quantity (FX-5)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(part in str(k).lower() for part in FORBIDDEN_KEY_PARTS):
                raise ValueError(f"cost-like field {path}.{k} in smoke summary")
            assert_no_cost_fields(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            assert_no_cost_fields(v, f"{path}[{i}]")


def refuse_frozen(fx: dict):
    if common.is_frozen_fixture(fx):
        raise FrozenFixtureRefused(f"smoke refuses frozen fixture {common.fixture_id(fx)} (FX-5)")


def summarize(run_dir: Path, driver_rc: int) -> dict:
    """Pass/fail-only summary of a smoke dry-run directory."""
    raw = json.loads((run_dir / "raw-result.json").read_text()) if (run_dir / "raw-result.json").exists() else {}
    rep_p = run_dir / "fixture_reproduction.json"
    rep = json.loads(rep_p.read_text()) if rep_p.exists() else {}
    aud_p = run_dir / "audit.json"
    s = {"driver_exit_ok": driver_rc == 0,
         "fixture_reproduction_byte_identical": rep.get("byte_identical") is True,
         "sampled_audit_accepted": json.loads(aud_p.read_text())["accepted"] if aud_p.exists() else None,
         "fxa_file_written": (run_dir / "fxa_nonverdict.json").exists(),
         "result_hashes_match": True, "cells": []}
    full_ok = True
    for entry in raw.get("cells", []):
        if not entry.get("result_path"):
            s["cells"].append({"cell": entry["cell_id"], "status": entry.get("status")})
            full_ok = False
            continue
        rpath = run_dir / entry["result_path"]
        s["result_hashes_match"] &= common.sha256_file(rpath) == entry["result_sha256"]
        rcpt = json.loads(rpath.read_text())
        refuse_frozen(rcpt["task"].get("fixture") or {"bits": rcpt["task"]["bits"], "seed": rcpt["task"]["seed"]})
        res = rcpt.get("result") or {}
        refuse_frozen(res.get("fixture") or {})
        c = {"cell": rcpt["task"]["cell_id"], "status": rcpt.get("status"),
             "smoke_namespace": common.is_smoke_ns(res.get("namespace"))}
        if rcpt.get("status") == "ok" and res["kind"] != "rho":
            fa = audit.audit_cell(rcpt, full_replay=True)
            full_ok &= fa["accepted"]
            c.update({"full_replay_audit_accepted": fa["accepted"], "full_replay_failure_count_zero": not fa["failures"],
                      "logs_verified": res["stage3"]["log_verification"].get("all_ok") is True})
            if res["kind"] == "primary":
                kf = res["known_false"]
                c.update({"k_recovered_equals_target": res["stage3"]["k_recovered"] == res["target"]["k"],
                          "la_agrees_dense_reference": bool(res["stage3"]["agrees_dense_reference"]),
                          "descents_all_verified": res["descents"]["n_verified"] == res["descents"]["n_descents"],
                          "stage2_scan_agrees_brute_force": res["stage2_alpha2"]["agreement_with_brute_force"]
                          == res["stage2_alpha2"]["n_heldout"],
                          "known_false_control_passed": bool(kf["control_passed"]),
                          "known_false_verification_failed": not kf["log_verification_all_ok"]})
            if res["kind"].startswith("stage_cost"):
                c["stage2_scan_agrees_brute_force"] = (res["stage2_alpha2"]["agreement_with_brute_force"]
                                                       == res["stage2_alpha2"]["n_heldout"])
            if res["kind"] == "null_randfb":
                c["random_V_matches_interval_size"] = res["factor_base"]["L"] == res["interval_L"]
        elif rcpt.get("status") == "ok":
            c.update({"rho_all_solved_and_certified": res["n_solved"] == res["n_targets"],
                      "rho_audit_accepted": audit.audit_cell(rcpt)["accepted"]})
        else:
            full_ok = False
        s["cells"].append(c)
    s["full_replay_audit_accepted"] = full_ok
    s["fixture"] = "synthetic non-frozen (see run manifest inputs.dry_run.fixture)"
    s["scientific_output"] = "none: no C-5 analysis in smoke"
    assert_no_cost_fields(s)
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="DRYRUN-smoke-v4-001")
    ap.add_argument("--runs-dir", default=str(SMOKE_DIR / "driver_dryrun"))
    ap.add_argument("--summarize-only", action="store_true",
                    help="summarize an existing dry-run directory (driver exit taken from its manifest status)")
    args = ap.parse_args(argv)
    if "smoke" not in args.run_id:
        print("REFUSED: smoke run id must contain 'smoke'", file=sys.stderr)
        return 2
    cmd = ["nice", "-n", "10", sys.executable, str(HERE / "driver.py"), "--smoke-dry-run", "--run-id", args.run_id,
           "--runs-dir", args.runs_dir]
    run_dir = Path(args.runs_dir) / args.run_id
    if args.summarize_only:
        import yaml
        st = yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]["status"]
        rc = 0 if st == "smoke_completed" else 1
    else:
        Path(args.runs_dir).mkdir(parents=True, exist_ok=True)
        with open(Path(args.runs_dir).parent / f"{args.run_id}.driver.log", "w") as log:
            rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT).returncode
    s = summarize(run_dir, rc)
    s["driver_command"] = " ".join(cmd)
    s["summarized_only"] = args.summarize_only
    s["run_dir"] = str(run_dir.relative_to(HERE))
    out = Path(args.runs_dir).parent / f"{args.run_id}_summary.json"
    out.write_text(json.dumps(s, indent=1, sort_keys=True) + "\n")
    print(json.dumps(s, indent=1, sort_keys=True))
    ok = (rc == 0 and s["full_replay_audit_accepted"] and s["fixture_reproduction_byte_identical"]
          and s["sampled_audit_accepted"] and s["fxa_file_written"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
