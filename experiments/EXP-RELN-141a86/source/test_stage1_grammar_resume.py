"""
Regression test for stage1_grammar_driver.py's checkpoint-resume path
(TASK-20260907-8fd098 continuation, this dispatch's fix).

stage1_grammar_driver.py's main() previously always initialized
`checkpoint_levels = []` and never read enumeration-checkpoint.json /
pareto-fronts-raw.json back in on startup, even though it writes both
progressively (one complexity level at a time, via write_all_checkpoints())
as it completes each level. This meant every container-restart relaunch
re-scored every complexity level from 1, even when levels were already
fully committed to disk. This test proves the fix: a killed-and-relaunched
run (a) actually skips re-scoring already-completed levels and (b) produces
results byte-identical to an uninterrupted run.

Real kill-and-resume test, same rigor as stage1_e_arm_holdout.py's
self_test_reproduce_committed_n14(): runs the ACTUAL driver subprocess
twice against copies of the REAL cached own-enumeration and E-arm-holdout
data (no synthetic/fabricated data) --

  Run A (control): stage1_grammar_driver.py --out-dir <A> --max-complexity 4,
    uninterrupted end to end.
  Run B (resume): stage1_grammar_driver.py --out-dir <B> --max-complexity 4,
    launched, polled until enumeration-checkpoint.json shows
    highest_level_completed >= --kill-after-level, SIGKILLed (not a clean
    shutdown -- exactly what a container restart does to this environment's
    background jobs), then relaunched with the IDENTICAL command over the
    SAME --out-dir.

Assertions:
  1. B's second invocation actually logs a "RESUME: enumeration state
     rebuilt" line (the resume path activated, not merely a from-scratch
     run that happened to finish fast).
  2. B's second-launch log segment (everything after the RESUME line)
     contains NO fit/score log lines for the already-completed complexity
     levels -- i.e. those levels were genuinely skipped, not re-scored.
  3. A and B's enumeration-checkpoint.json `levels_completed` records are
     identical for every level (same new_registered count at every level --
     proves the re-derived enumeration is exactly the original one).
  4. A and B's pareto-fronts-raw.json `front_state` dicts are IDENTICAL
     (deep equality) for every target and every complexity level -- resumed
     levels reloaded verbatim, later levels re-derived and re-fit, and must
     match bit-for-bit since the underlying enumeration and cached target
     data are the same and the fitter/scorer are deterministic.

Run (uses the real cached data already produced by the live
RUN-RELN-141a86-stage1-grammar run -- read-only, never modifies it):

  python3 test_stage1_grammar_resume.py \
      --cache-source ../runs/RUN-RELN-141a86-stage1-grammar
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVER = os.path.join(HERE, "stage1_grammar_driver.py")


def _read_json(path):
    with open(path) as f:
        return json.load(f)


def _wait_for_level(ckpt_path: str, level: int, timeout_s: float, poll_s: float = 0.2) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if os.path.exists(ckpt_path):
            try:
                data = _read_json(ckpt_path)
            except (json.JSONDecodeError, OSError):
                data = None
            if data is not None:
                levels = data.get("levels_completed", [])
                highest = max((lc["complexity"] for lc in levels), default=0)
                if highest >= level:
                    return True
        time.sleep(poll_s)
    return False


def run_case(out_dir: str, cache_source: str, max_complexity: int,
             kill_after_level, log_prefix: str):
    os.makedirs(out_dir, exist_ok=True)
    for fname in ("own-enumeration-cache.jsonl", "e-arm-holdout-cache.jsonl"):
        src = os.path.join(cache_source, fname)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(out_dir, fname))
        else:
            raise RuntimeError(
                f"cache-source {cache_source!r} is missing {fname} -- this test "
                f"requires the REAL cached data from a run directory, never "
                f"synthetic data.")

    cmd = [sys.executable, DRIVER, "--out-dir", out_dir,
           "--max-complexity", str(max_complexity),
           "--wall-clock-cap-seconds", "999999"]
    ckpt_path = os.path.join(out_dir, "enumeration-checkpoint.json")

    stdout1 = os.path.join(out_dir, f"{log_prefix}-launch1-stdout.log")
    stderr1 = os.path.join(out_dir, f"{log_prefix}-launch1-stderr.log")
    with open(stdout1, "w") as so, open(stderr1, "w") as se:
        proc = subprocess.Popen(cmd, stdout=so, stderr=se, cwd=HERE, start_new_session=True)

    try:
        if kill_after_level is not None:
            reached = _wait_for_level(ckpt_path, kill_after_level, timeout_s=180)
            if not reached:
                proc.kill()
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    pass
                raise RuntimeError(
                    f"{log_prefix}: driver did not reach complexity "
                    f"{kill_after_level} within timeout; cannot run kill test.")
            # Real SIGKILL: exactly what a container restart delivers to this
            # environment's unattended background jobs -- no clean shutdown,
            # no chance to flush anything beyond what write_all_checkpoints()
            # already committed for the last fully-completed level.
            os.kill(proc.pid, signal.SIGKILL)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                raise RuntimeError(f"{log_prefix}: process did not die after SIGKILL")

            stdout2 = os.path.join(out_dir, f"{log_prefix}-launch2-stdout.log")
            stderr2 = os.path.join(out_dir, f"{log_prefix}-launch2-stderr.log")
            with open(stdout2, "w") as so2, open(stderr2, "w") as se2:
                proc2 = subprocess.Popen(cmd, stdout=so2, stderr=se2, cwd=HERE, start_new_session=True)
            rc = proc2.wait(timeout=600)
            if rc != 0:
                with open(stderr2) as f:
                    tail = f.read()[-4000:]
                raise RuntimeError(f"{log_prefix}: resumed process exited nonzero ({rc}); stderr tail:\n{tail}")
        else:
            rc = proc.wait(timeout=600)
            if rc != 0:
                with open(stderr1) as f:
                    tail = f.read()[-4000:]
                raise RuntimeError(f"{log_prefix}: uninterrupted process exited nonzero ({rc}); stderr tail:\n{tail}")
    finally:
        if proc.poll() is None:
            proc.kill()

    return _read_json(ckpt_path), _read_json(os.path.join(out_dir, "pareto-fronts-raw.json"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-source", required=True,
                     help="Directory containing REAL own-enumeration-cache.jsonl and "
                          "e-arm-holdout-cache.jsonl (e.g. the live "
                          "RUN-RELN-141a86-stage1-grammar run directory). Read-only: "
                          "this test only reads from it, never writes.")
    ap.add_argument("--max-complexity", type=int, default=4)
    ap.add_argument("--kill-after-level", type=int, default=2)
    ap.add_argument("--keep-temp", action="store_true",
                     help="Do not delete the temp run directories on exit (for inspection).")
    args = ap.parse_args()

    tmp_ctx = tempfile.TemporaryDirectory(prefix="stage1-resume-test-")
    tmp = tmp_ctx.name
    try:
        dir_a = os.path.join(tmp, "A_uninterrupted")
        dir_b = os.path.join(tmp, "B_kill_and_resume")

        print(f"[test] Run A (uninterrupted, max_complexity={args.max_complexity}) -> {dir_a}")
        ckpt_a, front_a = run_case(dir_a, args.cache_source, args.max_complexity,
                                    kill_after_level=None, log_prefix="A")
        print(f"[test] Run A done: highest_level_completed={front_a.get('highest_level_completed')}")

        print(f"[test] Run B (kill after level {args.kill_after_level}, then resume, "
              f"max_complexity={args.max_complexity}) -> {dir_b}")
        ckpt_b, front_b = run_case(dir_b, args.cache_source, args.max_complexity,
                                    kill_after_level=args.kill_after_level, log_prefix="B")
        print(f"[test] Run B done: highest_level_completed={front_b.get('highest_level_completed')}")

        # Assertion 1: resume path actually activated.
        log_b_path = os.path.join(dir_b, "driver-progress.log")
        with open(log_b_path) as f:
            log_text = f.read()
        resume_lines = [l for l in log_text.splitlines() if "RESUME: enumeration state rebuilt" in l]
        assert resume_lines, (
            f"FAIL: no 'RESUME: enumeration state rebuilt' line found in {log_b_path} "
            f"-- resume path did not activate on the second launch.")
        print(f"[test] PASS (1/4): resume activated -- {resume_lines[-1]}")

        # Assertion 2: the second launch did not re-log fit lines for the
        # already-completed levels. driver-progress.log is shared/appended
        # across both launches in the same out_dir BY DESIGN (exactly like a
        # real container restart), so isolate the second launch's lines by
        # slicing from the RESUME marker onward.
        resume_idx = log_text.index("RESUME: enumeration state rebuilt")
        second_launch_text = log_text[resume_idx:]
        for lvl in range(1, args.kill_after_level + 1):
            marker = f"complexity={lvl} n_eval"
            assert marker not in second_launch_text, (
                f"FAIL: second launch re-scored already-completed complexity {lvl} "
                f"(found {marker!r} after the RESUME marker) -- resume is re-doing "
                f"expensive fit/score work it should have skipped.")
        print(f"[test] PASS (2/4): second launch did not re-score complexity "
              f"1..{args.kill_after_level}")

        # Assertion 3: enumeration re-derivation is exactly the original one.
        # Compare (complexity, new_registered) pairs only -- elapsed_seconds_total
        # is real wall-clock elapsed-since-process-start and is EXPECTED to
        # differ between an uninterrupted run and a killed-and-relaunched run
        # (the relaunch's clock restarts at 0); it is not part of the
        # determinism claim.
        def _levels_shape(ckpt):
            return [(lc["complexity"], lc["new_registered"]) for lc in ckpt["levels_completed"]]
        shape_a, shape_b = _levels_shape(ckpt_a), _levels_shape(ckpt_b)
        assert shape_a == shape_b, (
            "FAIL: enumeration-checkpoint.json levels_completed (complexity, "
            f"new_registered) pairs differ between uninterrupted run A and "
            f"kill-and-resume run B:\nA={shape_a}\nB={shape_b}")
        print(f"[test] PASS (3/4): enumeration-checkpoint.json levels_completed identical "
              f"(same new_registered count at every level): {shape_a}")

        # Assertion 4: fit/score results are byte-identical.
        assert front_a["front_state"] == front_b["front_state"], (
            "FAIL: pareto-fronts-raw.json front_state differs between uninterrupted "
            "run A and kill-and-resume run B -- resume did not reproduce byte-identical "
            "fit/score results.")
        print("[test] PASS (4/4): pareto-fronts-raw.json front_state identical for every "
              "target and complexity level (resumed levels reloaded verbatim, later "
              "levels re-derived and re-fit to the SAME result)")

        print("[test] ALL PASS: stage1_grammar_driver.py checkpoint-resume is correct "
              "and byte-identical to an uninterrupted run.")
        return 0
    finally:
        if args.keep_temp:
            print(f"[test] --keep-temp set: run directories left at {tmp}")
            tmp_ctx._finalizer.detach()  # prevent auto-cleanup on exit
        tmp_ctx.cleanup() if not args.keep_temp else None


if __name__ == "__main__":
    sys.exit(main())
