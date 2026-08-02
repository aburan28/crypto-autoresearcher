# BATCH-016 ttm-v2 frame-trace and panel audit

Task TASK-20260730-033 executes the frozen two-row panel and does not modify the
preregistered artifacts. It performs no curve, isogeny, quantum-circuit,
concrete HashDRBG, recovery, or object-lifetime computation.

## Snapshot gate and provenance

Live Git verifies that 11682c481d315f25961ed0520983cd2c947ca919 is HEAD, is an ancestor of the working tree,
and contains the exact TASK-031 paths with the recorded SHA-256 values. The
committed TASK-032 receipt remains unchanged and still says commit_sha: null
and pending_post_commit. That stale receipt state is preserved rather than
silently rewritten; the live commit/path/hash checks are recorded in all
allowed artifacts.

Requested policy: executor-terra. This direct Codex session resolved as GPT-5;
the exact backend identifier is not exposed and model_verified is false.
fallback_used is true because executor-terra was not runtime-resolved or
probe-verifiable; the approved amendment permits fallback. The evaluator is
deterministic and model-independent.

## Method

The audit exhaustively enumerates finite BaseDraw sequences, applies the frozen
adaptive requested-length rules, applies reduce-mod-parent on every labeled
return, and enumerates every enabled LeftIndex/RightIndex pair. At internal
S=2, a first-attempt discard enables exactly one same-level retry. At internal
S=5, a discard is retained as an out-of-policy terminal and is not retried.
The zero-progress test is the preregistered S=2 condition that every q-bin is
below threshold; an ordinary selected-index discard is not zero-progress.

All-zero traces use exact uniform-repeat vectors: value 0 and count 64 means the
full length-64 zero vector. Every event carries call_history, tape_position,
phase, r, retry_count, and requested_length. Wrong-phase symbols are retained
as unavailable.

## All-zero-tape traces

| Row | Frames | Tape symbols | Final position | Terminal |
|---|---:|---:|---:|---|
| [1,2,4] | 7 | 12 | 12 | root_keep_return |
| [1,2,5,8] | 15 | 25 | 25 | root_keep_return |

Both canonical zero paths have no discard, retry successor, or horizon event.
The exhaustive audit still checks the retry state wherever a discard enables it.

## Exhaustive S=2 audit

### Row [1,2,4]

| requested length | distinct pre-collimation pairs | zero-progress pairs | discarded index outcomes | minimum conditional keep |
|---:|---:|---:|---:|---:|
| 1 | 4 | 0 | 0 | 1 |
| 3 | 4 | 0 | 0 | 1 |
| 4 | 4 | 0 | 0 | 1 |

Reachable S=2 requested lengths are [1, 3, 4].
No reachable S=2 pair is zero-progress; jointly_reachable and recurrent are
false. No first-attempt S=2 discard occurs, so no retry successor is enabled.

### Row [1,2,5,8]

| requested length | distinct pre-collimation pairs | zero-progress pairs | discarded index outcomes | minimum conditional keep |
|---:|---:|---:|---:|---:|
| 1 | 239 | 0 | 0 | 1 |
| 2 | 887 | 0 | 229 | 5/6 |
| 3 | 1636 | 0 | 2067 | 7/9 |
| 4 | 2338 | 0 | 2405 | 7/9 |

Reachable S=2 requested lengths are [1, 2, 3, 4].
No reachable S=2 pair is zero-progress. First-attempt ordinary discard outcomes
total 4701; retry is enabled at
requested lengths [2, 3, 4]. A second discard is reachable, so
retry_horizon_exhausted is an explicit terminal branch. These are local exact
fractions for the finite state set, not concrete probabilities.

## Unexpected states and BATCH-015 qualification

For [1,2,5,8], non-designated S=5 contexts at requested lengths 2, 3, and 4
have ordinary discard outcomes. They are preserved as out-of-policy blockers,
not silently retried. No such S=5 context exists in [1,2,4].

BATCH-015 remains a static type-consistency diagnosis: ttm-v1 stopped at the
undefined return-modulus boundary before S=2 collimation. This ttm-v2 result
does not retroactively make BATCH-015 literal recursive execution. The
BATCH-014 static [1,2,4] enumeration is not claimed to share ttm-v2's
post-coercion state space.

## QUERY_MEMORY and C2

QUERY_MEMORY remains unreconciled with QM-STOPPING, QM-MEMORY-MAP, and QM-ERROR.
C2 remains live. The finite exclusion of the declared S=2 zero-progress class
does not provide a global stopping law; ordinary retries, concrete randomness,
broader schedules, recovery memory, and the final error map remain open. C3
remains limited to the scoped lexical simulator-PhaseVector subcase.

## Claim boundary and reproduction

Disposition: FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED.

The artifacts support only the fixed two-row ttm-v2 finite audit and exact
trace/state observations. They do not support numeric security, a
cryptanalytic breakthrough, or goal completion. The evaluator was an inline
Python 3.13.1 command under the five-file write scope;
no persistent runner, stdout log, stderr log, or extra artifact was written.
The frozen ttm-v2 document supplies the transition formulas; machine output
and all trace events are retained in the companion YAML artifacts.

