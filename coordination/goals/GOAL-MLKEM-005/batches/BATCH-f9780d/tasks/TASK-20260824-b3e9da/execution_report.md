# Execution report — TASK-20260824-b3e9da (RT-CTRL-1 matched pair)

Goal GOAL-MLKEM-005 · batch BATCH-f9780d · role executor.
Observations only. No interpretation, no hypothesis movement, no ledger record.

## Provenance

- Batch-opening snapshot commit: `2fe7dfebb4e3697aca14753a10b3214de7c9eeee`
- Branch: `claude/ml-kem-dsa-hqc-frodokem-ideas-jfti8o`
- Working tree at dispatch: clean (`git status --porcelain` empty)
- Runner sha256 (verified before AND after both attempts, unchanged):
  `bc0524ee432a2327bc4a5cfff5d8f5d79b590d37b2f38ea428c78af5abb25035` — matches
  `task_card.what_to_run.script_sha256`.
- Strategies sha256 (verified before AND after, unchanged):
  `f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18` — matches
  `task_card.what_to_run.strategies_sha256`.
- Nothing in `write_scope` other than the deliverables below was written; nothing
  outside `write_scope` was written; nothing was committed.

## Interpreter and environment

    /tmp/claude-0/-home-user-crypto-autoresearcher/15de1654-2503-5954-afd1-67e6db6674e9/scratchpad/sagevenv/bin/python

- Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]
- fpylll 0.6.4 (`.../sagevenv/lib/python3.11/site-packages/fpylll/__init__.py`)
- numpy 2.4.6
- Platform Linux-6.18.44-fc-v21-x86_64-with-glibc2.39, 4 CPUs, 16075 MiB RAM
- Peak observed RSS of the solver process: ~175 MB (single-threaded, ~100% of one core)
- No package was installed; no venv was created; the declared interpreter was used as given.

## Requested vs. serving policy

- `requested_policy`: `executor-implementation`
- Serving model actually answering this session: `claude-opus-5` (Claude Code
  subagent `executor`, `effort: medium`, which is the effort
  `executor-implementation` requests per CLAUDE.md's binding table).
- `fallback_used`: not applicable — the session was launched under this role and
  no downgrade was performed. The exact backend/model resolution recorded by
  `orchestration.adapter` was not re-derived by this task; only the runtime fact
  above is asserted.

## Commands, verbatim

Attempt 1 (as dispatched, run via the runtime's background shell):

    cd /home/user/crypto-autoresearcher
    date -u +%Y-%m-%dT%H:%M:%SZ > coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_start_utc.txt
    timeout 21600 /tmp/claude-0/-home-user-crypto-autoresearcher/15de1654-2503-5954-afd1-67e6db6674e9/scratchpad/sagevenv/bin/python \
      coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair.py \
      > .../stdout.log 2> .../stderr.log
    date -u +%Y-%m-%dT%H:%M:%SZ > .../run_end_utc.txt

Attempt 2 (identical invocation, relaunched detached via `setsid nohup` so it
could not be torn down with the runtime's background-shell manager; `timeout`
reduced from 21600 to 17500 s solely so that attempt 1 + attempt 2 stay under the
task's 21600 s ceiling):

    timeout 17500 /tmp/claude-0/-home-user-crypto-autoresearcher/15de1654-2503-5954-afd1-67e6db6674e9/scratchpad/sagevenv/bin/python \
      coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair.py

No argument, input, seed, precision, construction or strategies source differed
between the two attempts. The script itself is byte-identical across both.

## Wall clock

| | attempt 1 (killed) | attempt 2 (run of record) |
| --- | --- | --- |
| start (UTC) | 2026-08-25T05:13:39Z | 2026-08-25T06:21:19Z |
| end (UTC) | 2026-08-25T06:21:08Z (harness kill) | 2026-08-25T11:12:59Z |
| elapsed | 4030 s | 17508 s (exit code 124, `timeout`) |

Cumulative task wall clock: **21538 s**, against the 21600 s hard ceiling — within
budget, and the ceiling is what ended it.

## Cells, exactly as recorded

### Attempt 2 — cell mpfr_bits = 75 (REFERENCE, the contrast)

- `status`: **ERROR**
- `error`: `ReductionError: b'infinite loop in babai'`
- `seed_used`: `452658293` (matches the value forced in the task card)
- `strategies_sha256`: `f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18`
- `strategies_file_used`: the archived in-scope
  `inputs/fplll_strategies_default.json`
- `gso_float_type_used`: `mpfr`
- `outer_lll_reduction_elapsed_seconds`: `498.9597418308258`
- `cell_wall_clock_seconds`: `3051.823137998581`
- `tours`: **not recorded** — the field is only assigned after `bkz(par)` returns,
  and the exception was raised inside it.
- `root_hermite_factor`: **not recorded**, same reason. `b0_norm` likewise absent.

**Where the failure occurred.** `BKZ.Param(...)` did NOT raise. The construction
completed (outer LLL 499 s, mpfr GSO built, `float_type` reported as `mpfr`), the
content-pinned strategies file opened, and the error was raised inside the BKZ
reduction call. This is therefore NOT the
`task_card.outcomes_and_what_each_means.either_errors_at_BKZ_Param` case, which
was declared in advance to be an instrument failure. Reported as observed; the
classification of what it *is* belongs to the Reviewer/Coordinator, not here.

Attempt 1 produced the SAME cell result independently:
`status: ERROR`, `error: ReductionError: b'infinite loop in babai'`,
`seed_used: 452658293`, `outer_lll_reduction_elapsed_seconds: 508.58293199539185`,
`cell_wall_clock_seconds: 2974.328118801117`. Preserved at
`rt_ctrl_1_matched_pair_results.attempt1_killed.json`.

### Attempt 2 — cell mpfr_bits = 100 (RT-CTRL-1, the target)

- `status`: **NO RESULT — budget-exhausted before the cell terminated.**
- Started 2026-08-25T07:12:10Z; still executing after **14 448 s** when the
  task's wall-clock cap terminated the process (`timeout` → SIGTERM, exit 124).
- The process was verified alive and computing throughout: sampled repeatedly at
  ~99.9% CPU, RSS ~175 MB, PID 24314.
- Because the process was signalled rather than returning, the script's
  `except`/`finally` recording path never ran, so this cell has NO entry in
  `rt_ctrl_1_matched_pair_results.json` at all. There is no status, no tours, no
  root-Hermite factor, no `seed_used` and no error string to report for it. None
  of those values are estimated or inferred here.
- Attempt 1's copy of this cell was likewise unterminated: killed by the harness
  at ~1050 s into the cell.

Consequently the matched pair is INCOMPLETE: cell 75 terminated (ERROR), cell 100
did not terminate within budget. None of the four outcomes enumerated in
`task_card.outcomes_and_what_each_means` is realised, because all four presuppose
that both cells reach a terminal status.

## stderr, verbatim

Both attempts: `stderr.log` and `stderr.attempt1_killed.log` are **0 bytes**.
Empty, not omitted.

## stdout, verbatim (attempt 2)

    [06:21:19] cell mpfr_bits=75 (REFERENCE (the contrast)) starting
    [07:12:10] cell mpfr_bits=75 -> ERROR in 3051.8s
    [07:12:10] cell mpfr_bits=100 (RT-CTRL-1 (the target)) starting

The script's final summary block and `wrote ...` line are absent because the
process was signalled during cell 2.

## Reporting marks

- **3600 s mark.** Crossed during attempt 1: at that point cell 75 had terminated
  ERROR at 2974.3 s and cell 100 had been running ~626 s.
- **14400 s mark** (cumulative). Crossed during attempt 2 at ~10370 s into that
  attempt: cell 75 had terminated ERROR at 3051.8 s and cell 100 had been running
  ~7318 s with no output.
- A progress signal covering both marks was sent to the coordinating session
  mid-run. That message is a pointer only and carries no authority.

## Deviations from the dispatched protocol

1. **Attempt 1 was killed by the runtime, not by the budget.** The runtime's
   background-task manager stopped the shell at ~4030 s elapsed — far under the
   21600 s ceiling — while cell 100 was mid-computation. Infrastructure event.
   Per AGENTS.md rule 3 it is not evidence about precision, about the obstruction
   RT-CTRL-1 targets, or about anything mathematical.
2. **Attempt 2 was relaunched detached, with a 17500 s cap.** The only changes
   were the process-detachment mechanism and the `timeout` value, chosen so the
   two attempts together stay under the task's 21600 s ceiling. No experimental
   parameter was touched.
3. **Attempt-1 artifacts were preserved, not overwritten**, as
   `rt_ctrl_1_matched_pair_results.attempt1_killed.json`,
   `stdout.attempt1_killed.log`, `stderr.attempt1_killed.log`,
   `run_start_utc.attempt1_killed.txt`, `killed_at_utc.attempt1.txt`.
   `run_start_utc.txt` / `run_end_utc.txt` carry attempt 2, the run of record.
4. **Nothing was retuned in response to the ERROR.** Construction, seed 452658293,
   both precisions and the strategies source are exactly as dispatched, in both
   attempts.
5. `exit_rc.txt` (`EXIT_RC=124`) is an extra in-scope artifact not named in the
   deliverables list; it records the terminating exit status.

## Unexpected observations, recorded not discarded

- The 75-bit cell cost 3051.8 s here versus the predecessor's cross-container
  2502.74 s figure. Both numbers are stated as measured wall clock in different
  containers under different strategies provenance; no comparison is drawn.
- The 75-bit cell terminated in ERROR under the content-pinned strategies source,
  and did so reproducibly across two independent attempts with matching seed.
- The 100-bit cell ran at least 14 448 s without terminating — at least 4.7x the
  75-bit cell's total time — but since it never terminated, this is a lower bound
  on an unfinished computation and NOT a cost measurement.

## Toy-scale / transfer statement

Everything above is at d=512, beta=55, q=3329, a qary basis with k=d//2, single
seed 452658293, fpylll 0.6.4, one container. It is not a statement about FIPS 203
ML-KEM at any parameter set, and no transfer to any deployed parameter set is
asserted or implied.

## Artifacts (all absolute, all inside write_scope)

- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair_results.json
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair_results.attempt1_killed.json
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_start_utc.txt
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_end_utc.txt
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_start_utc.attempt1_killed.txt
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/killed_at_utc.attempt1.txt
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stdout.log
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stderr.log
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stdout.attempt1_killed.log
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stderr.attempt1_killed.log
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/exit_rc.txt
- /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/execution_report.md

## Certificate

`certificate.kind: none`. This is a pure measurement/timing run. No discrete-log
solve and no factor-base relation is claimed, so no solution certificate is due
under docs/claims-and-verification.md.

## Completion gate

| item | verdict |
| --- | --- |
| all planned runs terminal | **FAIL** — cell mpfr_bits=100 never reached a terminal status; the process was killed at the wall-clock ceiling |
| missing runs explained | PASS — cell 100's absence is explained above with its elapsed time and the terminating signal |
| required artifacts exist | PASS for every deliverable that a terminated cell can produce; cell 100 contributes no record because it never returned |
| raw data and summary agree | PASS — every figure above is quoted from `rt_ctrl_1_matched_pair_results.json`, `stdout.log`, `exit_rc.txt` or the two timestamp files |
| reproducible from recorded command and revision | PASS for cell 75 (reproduced identically across two independent attempts at commit 2fe7dfeb); UNKNOWN for cell 100, which has never terminated |
