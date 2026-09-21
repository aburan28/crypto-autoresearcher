# Comparison report: planted-correlation control arm vs. the PS-R3 pipeline

TASK-20260806-e19f6c / BATCH-4b8ad3 / GOAL-HQC-001 / EXP-HQC-982268.
Role: Executor. Claim tier: **toy**. Observations only — no conclusion is drawn
here about A17, HQC's decoding-failure rate, any standardized parameter set, or
what a MATCH/MISMATCH implies for EV-HQC-b71230; that interpretation belongs to
the Coordinator and the independent reviewers (validator TASK-20260806-9f4b27,
red team TASK-20260806-21c8da).

## 1. What ran

`planted_arm.py`, one authorized run, T = 10,000,000 trials, order-matched to
PS-R3 (`n_e=56`, `n_2=128`, `dup=1`, `N=7168`, `m=17`, `k=2..18`, 200 jackknife
batches). Full derivation and construction: `design.md` (written and frozen
before this run — see Section 6 for the file-timestamp ordering evidence).

## 2. Reused vs. newly written code (exact citation)

Reused **verbatim, unmodified**, from `coordination/goals/GOAL-HQC-001/batches/
BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py` (sha256
`a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`, verified by
`planted_arm.py`'s fail-closed integrity check at run time, see Section 4):

| measure.py lines | symbol | how reused in planted_arm.py |
|---|---|---|
| 213-222 | `comb_matrix(n_e, ks)` | called directly via the imported module (`measure.comb_matrix`), not copied |
| 225-246 | `log2_A_from_hists(H, n_e, ks, C)` | called directly via the imported module (`measure.log2_A_from_hists`), not copied |
| 92 | `N_JACK_BATCHES = 200` | value asserted equal to this task's own `N_JACK_BATCHES` constant at run time; the reused module's value is what the assertion checks |
| 730-739 | the batch-histogram + point-estimate + leave-one-out + jackknife-SE construction (`bh`, `point`, `loo`, `jmean`, `jse`) | **copied verbatim** into `planted_arm.py`'s `main()` (same formula, same variable names `bh`, `hist`, `point`, `loo`, `jmean`, `jse`; the only substitution is that `bh`/`hist` here come from this arm's own generator rather than from `measure.py`'s `S_all`) — this is inline code in `measure.py`'s `main()`, not a standalone function, so verbatim copy (not import) is the only way to reuse it |

Not reused, and not invoked, at all: `stage_a.py` (the real (T) sampler — see
Section 5 and `design.md` Section 3.2 for exactly what that leaves untested),
`binom_pmf`, `null_draws`, `order_stat_interval`, `t_stab`, the `Budget`/`_Stage`
bookkeeping classes, and every phase of `measure.py`'s `main()` other than the
lines cited above (CTRL-ORACLE, NULL-P, the (T)-arm shard loop, CTRL-POSHOM,
CTRL-BS, CTRL-DEC, NULL-M — none of those apply to a planted-law control arm and
none were run or cited as passing here).

Newly written for this task (`design.md` Section 4): the planted-law closed
form (`planted_law()`), the block-partition/reduce generator (`run_batch()`),
the seed derivation (`derive_seed()`, distinct `SEED_PREFIX` from `measure.py`'s
so the two tasks' random streams cannot collide), and the MATCH/MISMATCH
comparison logic.

## 3. CTRL-IDXMAP's L = N/n_e fix, applied here

`coordinator_ruling.yaml` RULE-2 records that `AMD-EXP-HQC-982268-v3`'s
`CTRL-IDXMAP` control used the wrong reference expression `L = n_2*dup`, which
is only degenerate-correct at `dup=1` (PS-R3's own `dup`) and is wrong at
`dup>1` (e.g. PS-A). This task's own block-partition code
(`planted_arm.py`, phase 3) computes the block length as
`L = N // n_e` (never `n_2*dup`), and asserts `L == N_2` as an internal
sanity check (`if L != N_2: raise SystemExit(...)`). This discharges one item
of `DEC-20260806-2947ba`'s resume plan (next_action 4: the pattern of
controls demonstrated only in the regime where their own defect is invisible)
for THIS task's own artifacts only. **It does not repair, re-run, or amend
CTRL-IDXMAP itself** — CTRL-IDXMAP is not run by this task, and the v3
amendment's own defect (RULE-2) remains unrepaired in `BATCH-0a65c0`, exactly
as the coordinator ruling states.

## 4. Fail-closed integrity check

`planted_arm.py`'s `load_measure_module()` reads `measure.py`'s sha256 from
disk and compares it to `MEASURE_PY_EXPECTED_SHA256`, a module-level constant
(not a nested field the check might silently miss, unlike the prior
executor's `path_sha256`-at-the-wrong-nesting defect named in
`EV-HQC-b71230`'s `unresolved_confounds`). Verified to actually abort on a
real mismatch: a deliberate-mismatch dry run (constant temporarily corrupted
to `000...0`, then reverted before the authorized run) exited non-zero with
`FAIL-CLOSED: measure.py sha256 mismatch...` and wrote no `planted_results.json`.
See `run_manifest.yaml`'s `fail_closed_check_verification` for the exact
command and output. The block-partition self-check (`design.md` Section 3
step 5, `run_batch()`'s `assert`) is the second fail-closed gate in this
script; it ran on every one of 2,000 sub-chunks during the authorized run
(200 batches x 10 sub-chunks/batch at `T=1e7`, `sub_chunk=10,000`) and never
fired (see `planted_results.json`
`generation.sub_chunks_block_partition_self_check_passed = 2000`).

## 5. What this arm does and does not exercise

Restated from `design.md` Section 3 (full text there): this arm exercises a
genuine flat-N-bit-vector to `(n_e, L)` reshape with the corrected
`L = N/n_e`, a per-block reduction over that reshaped tensor, aggregation to
`S_t` and a `(n_e+1,)` histogram — the exact sufficient statistic `measure.py`'s
estimator consumes — and then `measure.py`'s own estimator and jackknife code,
unmodified. It does **not** exercise `stage_a.py`'s cryptographic (T)-sampler
at all (no `CTRStream`, no fixed-weight support sampling, no ring
multiplication, no Walsh-Hadamard transform, no multiprocessing sharding), has
a far narrower marginal support (`{17,18,19}`, size 3) than PS-R3's
near-binomial spread, and its blocks are internally homogeneous by
construction rather than bit-heterogeneous like the real decoder's input.
`design.md` Section 3.2 lists five specific residuals this substitution
leaves in OPEN-6; they are not repeated here.

## 6. Pre-registration ordering (file-timestamp evidence)

```
design.md            mtime 2026-08-06T15:48:35Z  (written first, frozen)
planted_arm.py        mtime 2026-08-06T15:51:38Z  (written after design.md)
planted_results.json  mtime 2026-08-06T15:54:33Z  (produced by the authorized run,
                                                    after design.md and after
                                                    planted_arm.py)
```

`design.md`'s Section 2.1 table was written, and is asserted against by
`planted_arm.py` itself at run time (`design_md_reproduction_check`, see
`planted_results.json`), before the authorized run. The recomputed table
matched the frozen one to `<1e-12` on every cell (`mismatched_keys: []`,
`verdict: PASS`) — i.e. the closed form used to grade the run is exactly the
one written down beforehand, not one back-fitted to the outcome.

## 7. Results: MATCH / MISMATCH per k

Comparison rule (`design.md` Section 5, adopted for this task, not a verbatim
`measure.py` rule): **MATCH** iff the planted (exact, closed-form) value of
`log2_A_k(k)` lies within `point_k +/- 3 * jackknife_se_k`, where `point_k` and
`jackknife_se_k` come from the reused jackknife code (Section 2 above) applied
to this arm's own 200-batch histogram.

| k | recovered log2_Ahat_k | planted log2_A_k (exact) | jackknife SE | distance (SE) | verdict |
|---|---|---|---|---|---|
| 2 | -0.053324 | -0.053327 | 1.27e-06 | -2.378 | MATCH |
| 3 | -0.163931 | -0.163940 | 3.92e-06 | -2.367 | MATCH |
| 4 | -0.336289 | -0.336308 | 8.08e-06 | -2.353 | MATCH |
| 5 | -0.575476 | -0.575509 | 1.388e-05 | -2.339 | MATCH |
| 6 | -0.887313 | -0.887362 | 2.146e-05 | -2.322 | MATCH |
| 7 | -1.278525 | -1.278596 | 3.099e-05 | -2.303 | MATCH |
| 8 | -1.756973 | -1.757070 | 4.263e-05 | -2.281 | MATCH |
| 9 | -2.331952 | -2.332079 | 5.658e-05 | -2.257 | MATCH |
| 10 | -3.014610 | -3.014773 | 7.301e-05 | -2.229 | MATCH |
| 11 | -3.818553 | -3.818756 | 9.215e-05 | -2.199 | MATCH |
| 12 | -4.760728 | -4.760975 | 1.142e-04 | -2.164 | MATCH |
| 13 | -5.862788 | -5.863084 | 1.394e-04 | -2.125 | MATCH |
| 14 | -7.153319 | -7.153668 | 1.679e-04 | -2.081 | MATCH |
| 15 | -8.671691 | -8.672097 | 1.999e-04 | -2.033 | MATCH |
| 16 | -10.475411 | -10.475877 | 2.357e-04 | -1.978 | MATCH |
| 17 | -12.656081 | -12.656609 | 2.753e-04 | -1.917 | MATCH |
| 18 | -15.381994 | -15.382584 | 3.188e-04 | -1.850 | MATCH |

**17 / 17 cells MATCH.** `k = m = 17` (PS-R3's pre-specified cell, kept here
for narrative parity only — this arm has no null battery and no firing rule to
be "pre-specified" against) also MATCHes.

## 8. An observation the raw numbers show, reported without interpretation

Every one of the 17 cells' `distance (SE)` is negative and clustered in a
narrow band, roughly -1.85 to -2.38 SE — i.e. the recovered point estimate is
consistently *slightly less negative* (closer to zero) than the exact planted
value, by a broadly similar number of jackknife standard errors at every k.
This is expected to be a **correlated**, not independent, pattern across k:
all 17 cells are computed from the same single `(n_e+1,)` histogram (`hist =
bh.sum(axis=0)`), so a single realized sampling fluctuation in that one
histogram — this run's one draw of 200 batches at T=1e7 from the planted law
— shows up, propagated through the shared estimator, as a same-signed offset
across every k simultaneously. All 17 values nonetheless land inside the
adopted 3-SE band. This is reported as an observation only; no claim is made
here about whether it reflects a general property of the estimator (e.g. a
residual finite-T ratio-bias not fully removed) or is simply what one draw at
this T looks like. A second independent seed, not run here, would be needed
to tell the two apart, and is out of this task's authorized scope (one run,
one seed family, matching PS-R3's own "no replication" boundary).

## 9. Budget

Measured (not modeled): 71.98 core-seconds spent against the 1800 core-second
budget (4.0%), 71.84 wall-seconds against the 2700 s wall-clock budget. No
stage of this run was forced onto a subsample of the planned T=1e7 trials or
the planned 200 jackknife batches; `generation.achieved_equals_planned = true`
in `planted_results.json`. The one calibration/throughput estimate performed
before the authorized run (10 chunks of 20,000 trials, ~3.1 core-seconds, in
`/tmp` scratch, not committed) is reported in `design.md` Section 6 and is not
counted against this task's charged budget below (it ran in scratch, outside
`--out-dir`, and produced no artifact under this task's write scope). The
authorized command was executed three times total during this task with
identical deterministic seeds (~73, ~70, and the final ~72 core-seconds; see
`run_manifest.yaml` `deviations.stage_double_append_bug` for why the third
execution superseded the first two -- a bookkeeping-only bug in this task's
own `budget.stages` diagnostic, found and fixed before delivery). All three
executions' `MEASUREMENT`, `generation`, and `planted_law` JSON fields were
diffed programmatically and found bit-identical, so this is a
reproducibility check, not repeated independent measurement, and only the
final execution's `planted_results.json` is the run of record.

## 10. Scope

ONE planted-correlation control arm, order-matched to PS-R3, T=1e7, one seed
family, no replication. Claim tier: toy. This report states MATCH/MISMATCH
per k and cites what was reused/newly written; it draws no conclusion about
A17, HQC's decoding-failure rate, any standardized parameter set, or what a
MATCH/MISMATCH here implies for EV-HQC-b71230's disposition — those judgments
belong to the Coordinator and the two independent reviewers dispatched after
this task (`TASK-20260806-9f4b27` validator, `TASK-20260806-21c8da` red team).
