# PREREGISTRATION — TASK-20260805-080b62 (BATCH-012, GOAL-AES-003)

Written and committed to before any measurement run in this task.

## Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  actual_resolved_model: claude-sonnet-5
  fallback_used: true   # subagent frontmatter under this harness resolves to a
                         # Claude model regardless of the requested policy alias;
                         # see CLAUDE.md "Model policy note"
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
  actual_git_head_at_task_start: c0bb012ac4b236bbdabd30567060e3d2e547f13a
```

Note on `standing_basis`: the task card's stated standing basis
(`0137a051eb5828789eb267fa83c8278086578d4c`) does not match this session's
actual `git rev-parse HEAD` at task start
(`c0bb012ac4b236bbdabd30567060e3d2e547f13a`). Both values are recorded
verbatim rather than silently reconciled; the working tree was clean apart
from the new, untracked `coordination/goals/GOAL-AES-003/batches/BATCH-012/`
directory this task itself is writing into (`git status --porcelain`
confirmed at task start).

## What this task changes

BATCH-011's `rc8probe_ideal.c` (`perm128_init`) sizes its two open-addressed
hash-index tables (`dom_idx`, `rng_idx`) at
`next_pow2_u64(max_pairs * 2 + 16)`, giving load factor ~0.5. This task
changes the multiplier from `2` to `1`
(`next_pow2_u64(max_pairs * 1 + 16)`), giving load factor ~1.0, as a single
line edit inside `perm128_init` only. No other code path is touched.

Computed memory arithmetic (blk128 = 16 bytes; `max_pairs = 4 * trials`;
index slot = 4 bytes, two index arrays):

| log2N | max_pairs | dom+rng (fixed) | idx @ old (x2) | idx @ new (x1) | total @ old | total @ new |
|---|---|---|---|---|---|---|
| 24 | 67,108,864  | 2.147 GB | 2.147 GB | 1.074 GB | 4.295 GB | 3.221 GB |
| 25 | 134,217,728 | 4.295 GB | 4.295 GB | 2.147 GB | 8.590 GB | 6.442 GB |
| 26 | 268,435,456 | 8.590 GB | 8.590 GB | 4.295 GB | 17.180 GB | 12.885 GB |

These figures are re-derived independently in this task (see
`compute_memory_arithmetic` step below) and match the batch objective's
stated numbers exactly. At log2N=26 the dom+rng pair-storage arrays alone
already cost 8.590 GB, exceeding the 8 GB budget before any index-table byte
is counted — 2^26 is therefore NOT reachable under any load-factor tuning of
this data structure. This task targets log2N=25 only.

Machine headroom checked via `free -h` immediately before committing to
log2N=25: 12 GiB `available`, comfortably above the ~6.44 GB estimate.

## Preregistered expected-count context (stated BEFORE any run)

Per BATCH-009's own measured rate (~14 hits per 2^30 trials, EV-AES-e4c091),
the expected excess-event count scales linearly with exposure:

```
expected(2^25) = 14 * (2^25 / 2^30) = 14 / 32 = 0.4375 ~= 0.44
```

This is stated explicitly and in advance: **a 0-1 observed hit at 2^25 in
either arm is the anticipated outcome and does NOT by itself constitute
evidence for or against BATCH-009's cipher-substitution finding.** With an
expected count under 0.5, this task's own run is very unlikely to be
decisive; the honest expectation is that comparison B remains uninformative
after this task, exactly as it was after BATCH-011's 2^24 run, only now for
a documented power reason (not a memory-ceiling reason). This is preregistered
so that a null result at run time cannot later be presented as a surprise or
as evidence of anything beyond "the exposure reached did not produce enough
events to compare."

## Equivalence check plan (proportionate to a data-structure-sizing change)

Since the change is to an internal hash-table sizing constant, not a new code
path, equivalence is checked by re-running BATCH-011's existing 2^24
comparison-B-shaped arms (`RC-B-CMPB-LIVE-R5` params for the live arm baseline
via `rc8probe_ideal` in plain `arm` mode, and `RC-B-CMPB-IDEAL-R5` params via
`armideal` mode) under BOTH the OLD binary (`rc8probe_ideal_old`, built from
an unmodified copy of BATCH-011's `rc8probe_ideal.c`) and the NEW binary
(`rc8probe_ideal`, this task's one-line edit), with byte-identical CLI
arguments and seeds, and diffing the JSON outputs field-for-field. Only the
ideal-permutation (`armideal`) path exercises `perm128`/`perm128_init`, so
that is the arm where a behavioral dependency on index-table sizing (a
defect) would show up; the live-cipher (`arm`) path is unaffected by this
change by construction (it never touches `perm128`) and is re-run only as a
control confirming the binaries are otherwise identical.

If the ideal-permutation arm's output differs between the OLD and NEW
binary at 2^24, this task STOPS and reports the discrepancy as a serious
defect in the original `perm128` construction (index-table sizing affecting
correctness), not merely a memory optimization result — per the task card's
binding instruction.

## Planned runs (all matched exposure, amask=1, smask=1, r=5, per BATCH-011's
comparison-B geometry)

1. Equivalence check at 2^24 (both binaries, both arms: live + ideal).
2. Comparison B at 2^25: live-cipher arm (`rc8probe_ideal` `arm` mode).
3. Comparison B at 2^25: ideal-permutation arm (`rc8probe_ideal` `armideal`
   mode), with peak RSS measured via `/usr/bin/time -v` (or `/proc/<pid>/status`
   `VmHWM` sampled during the run if `/usr/bin/time -v` is unavailable).

## Budget

Wall-clock ceiling: 3600 s from `budget_stamps.jsonl` start stamp. Halting at
that stop is full compliance regardless of how many of the above runs have
completed; any unreached run is reported as unreached, never fabricated.
