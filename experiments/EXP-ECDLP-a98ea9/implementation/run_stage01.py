"""Driver: Stage 0 then Stage 1 for EXP-ECDLP-a98ea9."""
from __future__ import annotations

import io
import json
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import runrecord
import stage0
import stage1

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXP = HERE.parent
MODEL_ID = "cursor-grok-4.6"


def _run_stage(name, fn, run_id, extra_artifacts, params, seeds):
    run_dir = EXP / "runs" / run_id
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    t0 = time.time()
    ok = True
    err = None
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            fn()
    except SystemExit as exc:
        ok = exc.code in (0, None)
        err = f"SystemExit({exc.code})"
    except Exception as exc:
        ok = False
        err = repr(exc)
        stderr_buf.write(f"\n{err}\n")
    wall = time.time() - t0
    raw_path = run_dir / "raw-result.json"
    if raw_path.exists():
        raw = json.loads(raw_path.read_text())
        validity = raw.get("validity", "valid" if ok else "failed_infrastructure")
        reason = raw.get("validity_reason", err or "stage returned")
    else:
        validity = "failed_infrastructure"
        reason = err or "no raw-result.json"
    runrecord.write_run_record(
        run_dir=run_dir,
        stage=name,
        command=f"python3 {HERE.name}/{fn.__module__.split('.')[-1]}.py",
        params=params,
        seeds=seeds,
        validity=validity,
        validity_reason=reason,
        wall_clock_s=wall,
        stdout=stdout_buf.getvalue(),
        stderr=stderr_buf.getvalue(),
        raw_result_file="raw-result.json",
        model_id=MODEL_ID,
        repo_root=REPO,
        extra_artifacts=extra_artifacts,
    )
    return validity, reason, wall


def main() -> None:
    v0, r0, w0 = _run_stage(
        "0",
        stage0.main,
        "RUN-ECDLP-a98ea9-S0",
        extra_artifacts={"transport_lemma": "transport-lemma.md"},
        params={"stage": 0, "compute": False},
        seeds={},
    )
    print(f"Stage 0: {v0} ({w0:.3f}s) {r0}")
    if v0 != "valid":
        raise SystemExit(1)
    v1, r1, w1 = _run_stage(
        "1",
        stage1.main,
        "RUN-ECDLP-a98ea9-S1",
        extra_artifacts={"static_provenance": "static-provenance-check.json"},
        params={
            "stage": 1,
            "precisions": [1, 2, 3, 4],
            "samples_per_curve": stage1.SAMPLES_PER_CURVE,
            "bit_ladder": stage1.BIT_LADDER,
        },
        seeds={"declared": stage1.SEEDS},
    )
    print(f"Stage 1: {v1} ({w1:.3f}s) {r1}")
    if v1 != "valid":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
