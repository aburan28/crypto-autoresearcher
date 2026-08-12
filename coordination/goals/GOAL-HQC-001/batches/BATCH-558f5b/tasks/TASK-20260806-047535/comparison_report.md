# Comparison report: V2 planted-correlation control arm (real decode_blocks) vs. the PS-R3 pipeline

TASK-20260806-047535 / BATCH-558f5b / GOAL-HQC-001 / EXP-HQC-982268.
Role: Executor. Claim tier: **toy**. Observations only — no conclusion is
drawn here about A17, HQC's decoding-failure rate, any standardized
parameter set, or what MATCH/MISMATCH or the template-verification result
implies for OPEN-6 / EV-HQC-b71230 / EV-HQC-db1fd9; that interpretation
belongs to the Coordinator and the independent reviewers
(`TASK-20260806-01a340` validator, `TASK-20260806-ae74c4` red team).

## 1. What ran

`planted_arm_v2.py`, **one** authorized run, `T = 1,000,000` trials
(budget-reduced from PS-R3/V1's `T=1e7` — see Section 6), order-matched to
PS-R3 otherwise (`n_e=56`, `n_2=128`, `dup=1`, `N=7168`, `m=17`, `k=2..18`,
200 jackknife batches). Full derivation and construction: `design.md`
(written and frozen before this run — see Section 5 for the file-timestamp
ordering evidence). Unlike the V1 arm (`TASK-20260806-e19f6c`), this run
calls `stage_a.py`'s **real** `decode_blocks` directly on two fixed,
heterogeneous, decision-boundary-adjacent 128-bit templates.

## 2. Reused vs. newly written code (exact citation)

Reused **verbatim, unmodified**, sha256-pinned:

| source file | sha256 | symbol | how reused |
|---|---|---|---|
| `measure.py` (`BATCH-0a65c0/TASK-20260806-cde749`) | `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8` | `comb_matrix(n_e, ks)` (lines 213-222) | called directly via the imported module, not copied |
| same | same | `log2_A_from_hists(H, n_e, ks, C)` (lines 225-246) | called directly via the imported module |
| same | same | `N_JACK_BATCHES = 200` (line 92) | value asserted equal to this task's own constant at run time |
| same | same | batch-histogram + point/loo/jmean/jse jackknife (lines 730-739) | **copied verbatim** into `main()` (same formula, same variable names) |
| `stage_a.py` (`BATCH-6fddee/TASK-20260806-64b506`) | `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405` | `decode_blocks(bits, n_e, n_2, dup)` (line 286) | **called directly** on this arm's constructed `(B, N)` bit array — THE real decoder, including its own `bits.reshape(B, n_e, n_2)` (line 296), fold, WHT, and lowest-index-tiebreak argmax. NOT reimplemented. |
| same | same | `rm17_codewords()` (line 310) | called (via `brute_force_decode`) during template pre-registration verification |
| same | same | `brute_force_decode(bits_block, dup)` (line 323) | called during template pre-registration verification, as an INDEPENDENT (exhaustive minimum-distance) cross-check of `decode_blocks`' output |
| same | same | `wht128(a)` (line 270) | called internally by `decode_blocks`; also called directly by this task's own `wht_margin()` helper, read-only, to compute the WHT-coefficient margin for template selection/reporting |

`measure.py`'s sha256 is **identical** to the value V1's arm pinned
(`a4fd1ecb...`), confirming `measure.py` has not changed since V1's run.

Not reused, not invoked, at all, from `stage_a.py`: `CTRStream`,
`fixed_weight_support`, `ring_mul_sparse`, `ring_mul_dense`,
`support_to_int*`, the `_t_shard`/`_null_m_shard` shard workers, and every
`phase_*` function / `main()` — none of those apply to a planted-law control
arm and none were run or cited as passing here. **This means the
cryptographic `(T)`-sampler itself (`CTRStream`, `fixed_weight_support`,
the ring-arithmetic multiplication that actually produces `e-tilde`) is
still NOT exercised by this arm** — only `decode_blocks` (and, for
verification purposes, `rm17_codewords`/`brute_force_decode`/`wht128`) are.
Stated plainly per this task's binding constraint: **this arm constructs
planted per-block content directly (two fixed templates), rather than
sampling a genuine fixed-weight-support-derived `(T)`-distributed error
vector end-to-end.**

Newly written for this task: the planted-law closed form (`design.md`
Section 2, same construction as V1, independently re-derived), the
near-boundary template search and pre-registered verification (`design.md`
Section 3), the generation procedure built around a direct
`decode_blocks` call (`design.md` Section 4), the seed derivation (a fresh
`SEED_PREFIX`, distinct from both V1's and `measure.py`'s), and the
MATCH/MISMATCH comparison logic.

## 3. What real decoder machinery is, and is not, exercised (stated precisely)

**Exercised:** `decode_blocks`'s own internal
`bits.reshape(B, n_e, n_2)` (the block-partition/reshape step OPEN-6 is
concerned about), the `dup`-fold, the size-128 fast Walsh-Hadamard transform
(`wht128`), and the lowest-index-tiebreak argmax decode rule — all called on
real, heterogeneous, near-boundary block content, not a hand-rolled
substitute and not homogeneous all-0/all-1 blocks. `rm17_codewords()` and
`brute_force_decode()` were also exercised, as an independent verification
of both templates' true decode outcome (Section 4 below).

**NOT exercised:** the SHA-256 counter-mode PRNG (`CTRStream`), Floyd's
fixed-weight-support sampling, the `F_2[X]/(X^n-1)` ring multiplication
(`ring_mul_sparse`/`ring_mul_dense`) that actually derives `e-tilde` from
`(x,y,r1,r2,e)` in the real cryptographic instance, and the 8-shard
multiprocessing structure PS-R3's `(T)` arm uses. This arm's block content
is two FIXED, hand-selected 128-bit templates repeated at every position
carrying that label — not sampled ring-arithmetic output, and not
heterogeneous ACROSS all 56 positions (every "succeed" block is
bit-identical to every other "succeed" block in the same trial and across
all trials; likewise for "fail" blocks). See `design.md` Section 6.2 for the
full, honest residual list.

## 4. Real-decoder template verification (the pre-registered derivation step)

Both templates were verified **before any trial was generated** — first
during design-time exploration (`design.md` Section 3), then **again, at
run time, inside `planted_arm_v2.py` itself** (`verify_templates()`,
`planted_results.json.template_verification`), against the sha256-pinned
`decode_blocks` AND the independent `brute_force_decode`/`rm17_codewords`
exhaustive search:

| template | intended `F` | `decode_blocks` `F` | matches? | `brute_force_decode` `F` (256-codeword exhaustive search) | matches? | agree with each other? | `W` | WHT margin |
|---|---|---|---|---|---|---|---|---|
| `S_TEMPLATE` | 0 (succeed) | False | **YES** | False | **YES** | **YES** | 49 | 4 |
| `FAIL_TEMPLATE` | 1 (fail) | True | **YES** | True | **YES** | **YES** | 50 | 4 |

**No template's true decode ever disagreed with its intended label during
construction, under either decoder.** `verify_templates()`'s overall verdict
was `PASS`; a `FAIL` here would have aborted the run before any trial was
sampled (see `run_manifest.yaml`'s fail-closed-checks list) rather than
being silently used.

**Boundary-index-shift sensitivity** (the concrete, non-Monte-Carlo check
that a V1/V3-class defect has a genuine, non-zero chance of flipping `F_j`
on THESE exact templates — `design.md` Section 3.5, recomputed at run time):

| scenario | template | perturbation | neighbor | unperturbed `F` | perturbed `F` | FLIPPED |
|---|---|---|---|---|---|---|
| read-one-index-early | `S_TEMPLATE` | early | same-label | False | True | **YES** |
| read-one-index-early | `S_TEMPLATE` | early | diff-label | False | True | **YES** |
| read-one-index-late   | `S_TEMPLATE` | late  | same-label | False | False | no |
| read-one-index-late   | `S_TEMPLATE` | late  | diff-label | False | False | no |
| read-one-index-early | `FAIL_TEMPLATE` | early | same-label | True | False | **YES** |
| read-one-index-early | `FAIL_TEMPLATE` | early | diff-label | True | False | **YES** |
| read-one-index-late   | `FAIL_TEMPLATE` | late  | same-label | True | False | **YES** |
| read-one-index-late   | `FAIL_TEMPLATE` | late  | diff-label | True | False | **YES** |

`any_flip_observed = True`. The "early" direction — the literal shape of
both the campaign's V1 (global off-by-one) and V3 (last-block
window-read-early) defect classes — flips **both** templates, under
**both** same-label and different-label neighbor conditions. This is a
genuine, demonstrated (not merely asserted) non-zero chance of a
boundary-index-shift defect being expressed as a decode error — the exact
property the Red Team's injection against V1 proved was analytically
**impossible** (probability exactly 0, for any `T`) under V1's homogeneous
majority-threshold construction.

**What this does and does not establish, stated precisely (see also
`design.md` Section 3.6):** this is a per-template, per-scenario
deterministic fact about these two fixed 128-bit vectors under the real
decoder, checked in isolation. It is not, by itself, a measured detection
RATE of an injected defect against the full 1,000,000-trial `S_t` histogram
and the resulting `log2_Ahat_k` — that experiment, mirroring
`TASK-20260806-21c8da`'s injection against V1, is `TASK-20260806-ae74c4`'s
(red team's) job, not this task's.

## 5. Pre-registration ordering (file-timestamp evidence)

```
design.md             mtime 2026-08-06T16:46:08Z  (written and frozen first)
planted_arm_v2.py      mtime 2026-08-06T16:49:05Z  (written/finalized after design.md)
planted_results.json   mtime 2026-08-06T16:56:41Z  (produced by the authorized run,
                                                     after design.md and planted_arm_v2.py)
```

`design.md` Section 2.1's closed-form table, and Section 3.3's two template
constants, were both written before `planted_arm_v2.py` was run on any
data; the script itself re-derives the planted-law table
(`design_md_reproduction_check`, `mismatched_keys: []`, `verdict: PASS`)
and re-verifies both templates (`template_verification.verdict: PASS`)
against `decode_blocks`/`brute_force_decode` at the very start of its own
execution, before generating a single trial — see
`planted_results.json`.

## 6. Budget: T reduced from 1e7 to 1e6, and the residual observed

**T = 1e7 does not fit this task's 1800 core-second budget when using the
real decoder.** A pre-registration throughput calibration (scratch space,
not charged — `design.md` Section 5) measured **1198 trials/core-second**
for this exact generation procedure, a ~54x slowdown relative to V1's
hand-rolled majority-threshold reduce (~64,700 trials/core-second): running
the actual size-128 fast Walsh-Hadamard transform per block, for all 56
blocks per trial, costs far more than V1's simple bit-sum-vs-threshold
reduce. At 1198 trials/core-second, `T=1e7` would cost ≈8,347 core-seconds —
more than 4.6x this task's budget.

**Planned and achieved `T` = 1,000,000 (a pre-registered, 10x reduction from
PS-R3/V1's `T=1e7`, stated in `design.md` Section 5 BEFORE the run).**
`generation.achieved_equals_planned = True`; no truncation occurred; the
run completed with substantial budget headroom (Section 7).

**The predicted residual, checked against the actual run:** `design.md`
Section 5 pre-registered that a `T=1e6` run's jackknife SEs would scale up
by approximately `sqrt(10) ≈ 3.16x` relative to a `T=1e7` run of the SAME
real-decoder construction, all else equal. Comparing this arm's `k=18`
jackknife SE (`9.598e-04`, Section 7 table below) to V1's `k=18` SE at
`T=1e7` (`3.188e-04`, from V1's `comparison_report.md`) gives a ratio of
**3.01x** — reasonably consistent with the pre-registered `sqrt(10)`
prediction (the two arms are not directly comparable measurements of the
same quantity — V1's SE is for its homogeneous-block construction, this
arm's is for the real-decoder construction — so this is reported as a
rough consistency check on the stated residual, not a formal test).

## 7. Results: MATCH / MISMATCH per k

Comparison rule (`design.md` Section 8, adopted for this task, not a
verbatim `measure.py` rule — same convention V1 used): **MATCH** iff the
planted (exact, closed-form) value of `log2_A_k(k)` lies within
`point_k +/- 3 * jackknife_se_k`, where `point_k` and `jackknife_se_k` come
from the reused jackknife code (Section 2) applied to this arm's own
200-batch histogram, built from the REAL `decode_blocks` output.

| k | recovered log2_Ahat_k | planted log2_A_k (exact) | jackknife SE | distance (SE) | verdict |
|---|---|---|---|---|---|
| 2 | -0.053329 | -0.053327 | 4.116e-06 | 0.361 | MATCH |
| 3 | -0.163945 | -0.163940 | 1.267e-05 | 0.374 | MATCH |
| 4 | -0.336318 | -0.336308 | 2.601e-05 | 0.387 | MATCH |
| 5 | -0.575527 | -0.575509 | 4.452e-05 | 0.401 | MATCH |
| 6 | -0.887391 | -0.887362 | 6.858e-05 | 0.416 | MATCH |
| 7 | -1.278639 | -1.278596 | 9.862e-05 | 0.432 | MATCH |
| 8 | -1.757131 | -1.757070 | 1.351e-04 | 0.448 | MATCH |
| 9 | -2.332162 | -2.332079 | 1.785e-04 | 0.465 | MATCH |
| 10 | -3.014884 | -3.014773 | 2.293e-04 | 0.484 | MATCH |
| 11 | -3.818901 | -3.818756 | 2.880e-04 | 0.502 | MATCH |
| 12 | -4.761160 | -4.760975 | 3.550e-04 | 0.522 | MATCH |
| 13 | -5.863318 | -5.863084 | 4.310e-04 | 0.542 | MATCH |
| 14 | -7.153959 | -7.153668 | 5.164e-04 | 0.563 | MATCH |
| 15 | -8.672455 | -8.672097 | 6.116e-04 | 0.585 | MATCH |
| 16 | -10.476313 | -10.475877 | 7.171e-04 | 0.607 | MATCH |
| 17 | -12.657133 | -12.656609 | 8.331e-04 | 0.629 | MATCH |
| 18 | -15.383209 | -15.382584 | 9.598e-04 | 0.652 | MATCH |

**17 / 17 cells MATCH.** `k = m = 17` (kept for narrative parity only, as in
V1) also MATCHes. `q_hat_measured = 0.32142930357142857` vs.
`q_planted_exact = 0.32142857142857145` (relative difference ≈2.3e-5),
consistent with `S_t = M_t` exactly by construction (Section 2) and the
observed sampling fluctuation of `M_t`'s own draw across 200,000 trials per
support value on average.

## 8. An observation the raw numbers show, reported without interpretation

Every one of the 17 cells' `distance (SE)` is **positive** (`planted - v >
0`, i.e. recovered `log2_Ahat_k` is consistently slightly MORE negative —
farther from zero — than the exact planted value) and grows roughly
monotonically with `k`, from `0.36` SE at `k=2` to `0.65` SE at `k=18`. This
is the OPPOSITE sign pattern from V1's arm, whose 17 cells were all
consistently slightly LESS negative than planted (distance `-1.85` to
`-2.38` SE, V1 `comparison_report.md` Section 8). As with V1, this pattern
is expected to be a **correlated**, not independent, artifact across `k`
(all 17 cells derive from the single shared `(n_e+1,)` histogram of this
one run), reflecting one realized sampling fluctuation propagated through
the shared estimator. All 17 values land comfortably inside the adopted
3-SE band regardless (largest observed distance: 0.652 SE at `k=18`, well
under the 3-SE threshold). This is reported as an observation only; no
claim is made about whether the direction-reversal relative to V1 reflects
anything about the real-decoder construction versus the homogeneous-block
one, an artifact of this run's specific seed, or is simply what one draw at
each respective `T`/construction looks like — a second independent seed,
not run here, is out of this task's authorized scope (one run, one seed
family).

## 9. Fail-closed checks

| check | reads | fired during authorized run? |
|---|---|---|
| `measure.py` sha256 integrity | `MEASURE_PY_EXPECTED_SHA256` vs. `sha256_file(MEASURE_PY)` | no (passed); **demonstrated to abort on a real mismatch** — see `run_manifest.yaml` `fail_closed_check_verification` |
| `stage_a.py` sha256 integrity | `STAGE_A_PY_EXPECTED_SHA256` vs. `sha256_file(STAGE_A_PY)` | no (passed) |
| `N_JACK_BATCHES` cross-check | this task's constant vs. `measure.N_JACK_BATCHES` | no (passed) |
| `L = N/n_e` sanity (RULE-2) | computed `L` vs. declared `N_2` | no (passed) |
| template verification (`decode_blocks` + `brute_force_decode`) | both templates' true decode vs. intended label | no (passed, `verdict: PASS`) |
| planted-law reproduction | recomputed `log2_A_k(k)` table vs. `design.md`'s frozen table | no (passed, `mismatched_keys: []`) |
| block-partition/real-decode self-check (`F == block_fail`) | every one of 200 batches' real `decode_blocks` output vs. the planted `block_fail` pattern | no (passed on all 200 batches; a single failure would have aborted the run) |

## 10. Budget

**Measured** (not modeled): **434.28 core-seconds** spent against the 1800
core-second budget (**24.1%**), 434.26 wall-seconds against the 3600 s
wall-clock budget (**12.1%**). Peak RSS: 559.7 MB (of the 2 GB budget,
**28.0%**). `generation.achieved_equals_planned = True`; no truncation.
Stage breakdown (from `planted_results.json.budget.stages`):

| stage | core-seconds |
|---|---|
| provenance | 0.329 |
| fail_closed_integrity_and_import | 0.025 |
| planted_law_derivation | 0.001 |
| real_decoder_template_verification | 0.007 |
| block_partition_real_decode_generation | 433.905 |
| estimator_and_jackknife_reused_verbatim | 0.007 |

**Executions of the authorized command, reported exhaustively and
consistently with `run_manifest.yaml` (no V1-style discrepancy):**

1. A smoke test at `--trials 2000 --batches 200` (10 trials/batch), run in
   SCRATCH space (`--out-dir /tmp/.../scratchpad/smoke_out`), to catch
   implementation bugs cheaply before spending real budget. Result: ran
   without error, `17/17 MATCH` (trivially, given the tiny `T`).
2. A deliberate-mismatch dry run of the fail-closed `measure.py` sha256
   check: `MEASURE_PY_EXPECTED_SHA256` was temporarily edited in the
   COMMITTED script (`planted_arm_v2.py`, this task's own write scope) to
   an all-zero placeholder, run at `--trials 2000 --batches 200` against a
   SCRATCH `--out-dir`, confirmed to print
   `FAIL-CLOSED: measure.py sha256 mismatch...` to stderr, exit non-zero,
   and write NO `planted_results.json`. The constant was then reverted to
   its correct value (verified in the diff, and re-verified by a second
   smoke run, `17/17 MATCH`) before the authorized run below. See
   `run_manifest.yaml` `fail_closed_check_verification`.
3. **The authorized run**, `T=1,000,000`, `--out-dir .` (this task's own
   directory), producing the committed `planted_results.json`,
   `stdout.log`, `stderr.log`. Run exactly **once**. This is the run of
   record; steps 1-2 above produced no artifact under this task's write
   scope other than the (already-reverted) source file itself, and their
   outputs live in scratch space only.

No calibration, smoke test, or dry run was subsampled from, or substituted
for, the authorized run. The pre-registration throughput calibration
(Section 6, `design.md` Section 5) ran separately in scratch space and is
not counted against this task's charged budget, the same convention V1
used.

## 11. Scope

ONE V2 planted-correlation control arm, order-matched to PS-R3 otherwise,
`T=1,000,000` (budget-reduced from `1e7` — Section 6), one seed family, no
replication. Real `decode_blocks` used directly; two fixed near-boundary
heterogeneous templates, both verified (Section 4) to genuinely decode to
their intended label and to have a demonstrated non-zero chance of flipping
under the campaign's V1/V3 boundary-index-shift defect classes. Claim tier:
**toy**. This report states MATCH/MISMATCH per k, the template-verification
outcome, and what real-decoder machinery is/is not exercised; it draws no
conclusion about A17, HQC's decoding-failure rate, any standardized
parameter set, or what a MATCH/MISMATCH or a passed template verification
here implies for OPEN-6's disposition — those judgments belong to the
Coordinator and the two independent reviewers dispatched after this task
(`TASK-20260806-01a340` validator, `TASK-20260806-ae74c4` red team).
