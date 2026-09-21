# RUN-ICPERF-c9590f — ABORTED LAUNCH, NOT A RUN

This directory is retained because failed attempts are retained. It contains no
measurement, and it must not be read as a third execution of
EXP-ICPERF-66fd51.

## What happened

`bench.py` was launched at `2026-09-15T10:22:40Z` (`launch_time.txt`) and died
inside its own environment probe, before writing `environment.json`, `plan.json`,
or a single row of `results.jsonl`. The traceback is preserved verbatim in
`bench_stderr.log`:

    File "experiments/EXP-ICPERF-66fd51/code/bench.py", line 506, in ver
      return subprocess.run(argv, capture_output=True, text=True, timeout=60)...
    KeyboardInterrupt

The frame it died in is `environment()` probing `Singular --version`. That is
the defect the review of BATCH-51e2aa recorded independently: `bench.py`'s
version probe inherits the parent's stdin, so `Singular --version` waits for
input that never comes and the probe hangs until something interrupts it. Here
the interrupt arrived from the host, not from a person. `bench_stdout.log` is
empty, `logs/` is empty, and nothing else was created.

## What this is, and is not

- **Not evidence, in either direction.** An interrupted process is an
  infrastructure outcome and never a mathematical result (AGENTS.md core rule
  5). It says nothing about any prediction of H-ICPERF-cc4847.
- **Not an execution against the contract's budget.** `EXP-ICPERF-66fd51`
  admits two runs (`AMD-20260915-4ec9b9`, `maximum_runs` 1 -> 2), and both are
  spent: `RUN-ICPERF-305ca3` and `RUN-ICPERF-4ec9b9`, 504 rows each, both
  terminal and both archived. This attempt produced zero rows and no manifest,
  so there is no third run to account for — but the identifier was minted, and
  an unexplained run directory is worse than a disclosed empty one.
- **Not cited by anything.** No ledger record, evidence record, decision, or
  queue entry references `RUN-ICPERF-c9590f`, and none should. It has no
  `manifest.yaml` on purpose: writing one would assert a run happened.

## Why it is kept

The instrument defect it exhibits is scheduled for repair as the first task of
batch 2 (`GOAL-ICPERF-e6b6a4` `next_action`, item 1: "bench.py's version probe,
which hangs on inherited stdin so the run cannot name its own Singular"). This
directory is the cheapest reproduction of that failure mode in the repository,
and the repair should be checked against it.
