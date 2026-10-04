# RUN-RELN-141a86-stage0c-minimality: implementation notes and deviations

## Summary

Implements TASK-20260907-6333af / DEC-20260907-2a3727: (1) per-level
checkpointing added to the lean enumerator, demonstrated to survive a real
`SIGKILL`; (2) targeted-minimality structural recovery attempted for INV-1,
INV-7 p_fail, INV-8 (all three cleared) and INV-7 p_exist (attempted, still
open, resource_exhaustion).

## Step 1: checkpointing

`experiments/EXP-RELN-141a86/source/grammar_engine_checkpoint.py` is a new,
additive file. It duplicates `grammar_engine_lean.enumerate_lean`'s
algorithm verbatim (same `_register` logic, same calls into the unchanged
`grammar_engine.py` for `canonicalize`/`node_count`/`numeric_fingerprint`,
same hash-based dedup via `grammar_engine_lean._hash_string` /
`_hash_fingerprint`) and adds exactly one behaviour: after every complexity
level finishes building, the cumulative level-report list is written to a
single fixed-path checkpoint file via write-to-temp-then-`os.fsync`-then-
`os.replace`-then-directory-`fsync`. Neither `grammar_engine.py` nor
`grammar_engine_lean.py` was modified.

A self-test (`python3 grammar_engine_checkpoint.py`, also step 3 of
`command.txt`) confirms the checkpointed enumerator produces IDENTICAL
`by_complexity_counts` to the unchanged `grammar_engine_lean.enumerate_lean`
on `degree_table` at `max_complexity=6`.

A REAL kill test (step 4 of `command.txt`) launched a live worker process,
let it run for 6 seconds (long enough to complete 5 complexity levels of a
6-leaf pack), sent it `kill -9` from the parent shell, confirmed the process
was actually dead via `ps -p <pid>`, and then read the checkpoint file back
in a fresh Python process (no reliance on any in-memory state from the
killed process). Result: the checkpoint file contained 5 complete,
well-formed level records with correct cumulative counts and timestamps; no
`--out` result file existed (which only a clean exit writes); no leftover
`.tmp-<pid>` file existed (confirming the atomic-rename discipline leaves no
half-written artifact observable after a hard kill). This is the demonstration
required by the handoff's completion gate.

## Step 2: targeted minimality

For each of the three primary targets, `target_enumerate_worker_checkpoint.py`
ran `grammar_engine_checkpoint.enumerate_lean_checkpointed` with
`max_complexity = canonical_complexity - 1` (8 for INV-1 and INV-7 p_fail,
9 for INV-8 -- NEVER the target's own canonical complexity, which is exactly
the blind-search method that had already failed twice), under the same
external-monitor discipline used in the prior repair run (continuous
`/proc` RSS polling every 2s, external hard wall-clock cap of 6000.0s,
external hard memory cap of 13.0 GB, internal worker soft caps of
11.0 GB / 5700.0s checked only between completed levels).

All three completed CLEANLY within the 6000s cap -- this is the key new
result relative to the two prior blind-search attempts, which both got stuck
inside construction of the target level itself (level 9, 9, 10) and never
finished. Searching one level *below* the target is measurably smaller: level
8 of the two 6-leaf packs (INV-1, INV-7 p_fail) completed in ~1780-1900
seconds each, and level 9 of the 4-leaf `degree_table` pack (INV-8) completed
in ~1796 seconds. None of the three found any numerical match to the target
at any level up to the searched maximum (checked via the target's own
numeric-fingerprint hash on the SAME fixed sample grid the frozen engine
already uses for all algebraic-duplicate dedup throughout this contract --
this is the equivalence relation used to decide "matches", consistent with
how the engine's own dedup and the prior repair run's `target_fp_hash`
mechanism already worked; it was not newly invented for this run).

INV-7 p_exist (canonical complexity 11, requiring level <=10 on the SAME
6-leaf `enum_xclass_signed_m2` pack that only just barely completed level 8
for p_fail) was attempted anyway, since ~94 minutes had been spent on the
first three targets and substantial time remained. It completed levels 1-8
exhaustively (identical level-8 form count to p_fail's own run, 3,314,145,
as expected since both start from the same leaf set and pack) with no match,
then was killed by the external monitor's 6000.0s hard wall-clock cap while
still constructing level 9. Extrapolating from the measured level 7->8 growth
factor (~7.5x) and the measured per-candidate cost at level 8
(roughly 486 candidates/second), level 9 alone is estimated to require on
the order of 12-14 hours of additional wall clock, and level 10 roughly
9-10x that again -- this was judged not worth a longer single-attempt
extension in this session, consistent with the handoff's own expectation
that p_exist would likely remain open. This is `resource_exhaustion`, never
a negative or positive result.

## Step 2(b): direct construction

`direct_construction_check.py` parses each target's known closed-form
expression (from `target-enumeration-raw-results.json`'s `target_expr`
field, transcribed from `candidate-list.yaml`), canonicalizes it, computes
its node count via the UNCHANGED `grammar_engine.node_count`, and verifies
it against the exact control tables carried forward unchanged from
`RUN-RELN-141a86-stage0bcde/control-tables/` (not regenerated), using
`recovery_check.py`'s unchanged `verify_expression_on_table` (a small
disclosed rational-constant search grid, `CONST_SEARCH_GRID`, already
validated in the prior repair run).

All four node counts match their declared canonical complexity EXACTLY (9,
9, 10, 11) and all four are zero-residual: INV-1 (144 real cells, CONST=1),
INV-7 p_fail (15 real cells, 0 free constants), INV-8 (549 real rows,
CONST=(1,2)), INV-7 p_exist (15 real cells, CONST=1, residual
1.1102230246251565e-16 -- IEEE-754 float64 epsilon from evaluating
`1 - p_fail`, not the exact bit pattern `0.0`, reported exactly and treated
as zero-residual under the same 1e-9 tolerance and the same characterization
used identically in both prior runs for this expression).

## Disclosed deviation: a stray re-invocation

After the first three targets completed, the executor launched what was
intended to be a p_exist-ONLY run using
`python3 run_stage0c_minimality_monitor.py --attempt-p-exist-only`. This flag
does not exist in the driver's actual CLI (`sys.argv` check for
`--attempt-p-exist`, not `--attempt-p-exist-only`), so `attempt_p_exist`
evaluated `False` and the driver began re-running ALL FOUR targets in order,
starting with INV-1_mean -- which was already complete and whose files should
never have been touched again.

This was noticed within seconds (by inspecting `ps aux` and the checkpoint
file's freshly-changed timestamp) and the stray processes were killed via
`pkill -9 -f run_stage0c_minimality_monitor.py; pkill -9 -f
target_enumerate_worker_checkpoint.py`. This left
`checkpoint-INV-1_mean.json` overwritten with an incomplete `in_progress`
state (levels 1-5 only). It was immediately regenerated verbatim from
`worker-result-INV-1_mean.json` -- the ORIGINAL run's own immutable final
output, timestamped `2026-09-07T15:57:44Z`, which the stray process never
had time to touch (it never reached a clean exit, so it never wrote to
`--out`).

A SECOND stray worker process for `INV-1_mean` (a race: the child worker
process had already spawned by the time the first `pkill` ran, but a
subsequent, separate stray somehow survived that first `pkill` -- most
likely a second child spawned in the brief window between the `ps aux`
check that showed the parent monitor process and the `pkill` call actually
executing) was discovered still running a few tool-calls later via a direct
`ps aux` check, again overwriting `checkpoint-INV-1_mean.json` (this time to
7 levels). It was killed with a targeted `kill -9 <pid>` (not a pattern-based
`pkill`, to avoid also killing the legitimate, concurrently-running p_exist
worker), and `checkpoint-INV-1_mean.json` was regenerated a second time from
the same untouched `worker-result-INV-1_mean.json`.

No file belonging to INV-7 p_fail, INV-8, or the legitimate p_exist run was
ever touched by this stray invocation. `worker-result-INV-1_mean.json` and
`minimality-search-raw-results.json` (both written by the ONE real,
uninterrupted run of each target) were never touched at any point. The final
`checkpoint-INV-1_mean.json` on disk is, by construction, an exact
transcription of `worker-result-INV-1_mean.json`'s own `levels` array (both
now readable and cross-checked below) and is thus a faithful, if
after-the-fact-reconstructed, checkpoint record of the real run.

**Cross-check**: `worker-result-INV-1_mean.json`'s
`enumeration_result.levels` array and `checkpoint-INV-1_mean.json`'s
`levels_completed` array both list complexities 1 through 8 with identical
`cumulative_registered` counts at every level (verified: level 8 =
3,686,074 in both).

This deviation cost real time (delayed the start of the legitimate p_exist
run by a few minutes) and is recorded here in full per AGENTS.md evidence
discipline; it did not corrupt or lose any measured result.

## Artifacts

- `grammar_engine_checkpoint.py`, `target_enumerate_worker_checkpoint.py`,
  `run_stage0c_minimality_monitor.py`, `direct_construction_check.py`
  (`experiments/EXP-RELN-141a86/source/`, additive, new)
- `checkpoint-{INV-1_mean,INV-7_p_fail,INV-8_d_reg,INV-7_p_exist}.json`
- `worker-result-{INV-1_mean,INV-7_p_fail,INV-8_d_reg}.json`,
  `pexist-search-raw-result.json`
- `memory-timeseries-{INV-1_mean,INV-7_p_fail,INV-8_d_reg,INV-7_p_exist}.json`
- `minimality-search-raw-results.json`, `direct-construction-results.json`
- `recovery-controls.json` (the 5-control table, this run's update)
- `raw-result.json`, `manifest.yaml`, `command.txt`, `environment.json`,
  `stdout.log`, `stderr.log`
