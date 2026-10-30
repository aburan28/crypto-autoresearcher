#!/usr/bin/env python3
"""Schema check for an EXP-ICPERF-283a70 stage-0 observation (version 2).

Exit 0 when the artifacts exist, parse, name this experiment, trial and run,
and carry attack_claimed false. The scientific pass or fail is decided by the
runbook's assertions on raw-result.json, never by this exit code. The run
schema itself is gated by the supervisor (tools/experiment_execution.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-ICPERF-283a70"
SCHEMA = "crypto.autoresearch.exp-icperf-283a70.stage0.v2"
TRIAL_IDS = ("geometric-probe-sample", "ctl-neg-wrong-triple", "ctl-neg-support-zero")
REQUIRED = (
    "trial_id", "run_id", "role", "seed", "p_den", "n_targets", "shifts", "support_min",
    "sample_sum", "sum_squares", "median", "median_split", "cv_sq_num", "cv_sq_den",
    "median_ratio_num", "median_ratio_den", "cv_in_band", "median_ratio_in_band",
    "exact_match", "attack_claimed", "interpreter", "elapsed_seconds",
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check.py RUN_DIR")
    run_dir = Path(sys.argv[1])
    for name in ("manifest.yaml", "raw-result.json", "RESULTS.md"):
        if not (run_dir / name).is_file():
            raise SystemExit(f"missing {name}")
    payload = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise SystemExit("unexpected schema")
    if payload.get("experiment_id") != EXPERIMENT_ID:
        raise SystemExit("unexpected experiment id")
    if payload.get("trial_id") not in TRIAL_IDS:
        raise SystemExit("trial id is not a preregistered trial")
    missing = [key for key in REQUIRED if key not in payload]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    if payload.get("seed") != 20261017 or payload.get("p_den") != 50 or payload.get("n_targets") != 64:
        raise SystemExit("seed, success denominator or sample size is not the freeze")
    if payload.get("attack_claimed") is not False:
        raise SystemExit("raw-result.json must carry attack_claimed false")
    try:
        document = json.loads((run_dir / "manifest.yaml").read_text(encoding="utf-8"))
    except ValueError:
        # The supervisor re-serialises a manifest only if it had to complete it.
        import yaml  # noqa: PLC0415
        document = yaml.safe_load((run_dir / "manifest.yaml").read_text(encoding="utf-8"))
    body = document.get("run") if isinstance(document, dict) else None
    if not isinstance(body, dict):
        raise SystemExit("manifest.yaml has no run envelope")
    if body.get("id") != payload["run_id"] or body.get("experiment_id") != EXPERIMENT_ID:
        raise SystemExit("manifest does not name this run")
    if body.get("trial_id") != payload["trial_id"]:
        raise SystemExit("manifest names another trial")
    if body.get("attack_claimed") is not False:
        raise SystemExit("manifest.yaml must carry attack_claimed false")
    if (body.get("result") or {}).get("certificate", {}).get("kind") != "none":
        raise SystemExit("manifest.yaml must carry result.certificate.kind none")
    text = (run_dir / "RESULTS.md").read_text(encoding="utf-8")
    if "host latency" not in text:
        raise SystemExit("RESULTS.md is missing the claim-boundary sentence")


if __name__ == "__main__":
    main()
