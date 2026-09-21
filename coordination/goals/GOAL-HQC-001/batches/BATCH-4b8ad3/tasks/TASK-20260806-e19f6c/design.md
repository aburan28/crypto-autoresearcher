# Design: planted-correlation control arm for OPEN-6 (TASK-20260806-e19f6c)

Written and frozen **before** `planted_arm.py` is run on any data. `run_manifest.yaml`
records the file-timestamp ordering (`design.md` mtime < `planted_results.json` mtime)
as evidence this was not written after seeing results.

## 0. What this document is for

EV-HQC-b71230's OPEN-6: the validator's exact recomputation on PS-R3 only certifies
arithmetic "from the histogram forward." It cannot distinguish a real anti-correlation
effect from a subtly wrong sampler that reproduces the same signature. This document
derives, in closed form, the TRUE joint failure law of an instance whose answer we
build and therefore already know — then `planted_arm.py` pushes that instance through
the *identical* estimator/jackknife/reporting code path `measure.py` used for PS-R3.
If the pipeline is trustworthy, the recovered `log2_Ahat_k` must land inside the
pipeline's own jackknife interval around the value derived here. If it does not, that
is itself the finding, reported as MISMATCH, with no further interpretation supplied
by this task.

## 1. Parameters (order-matched to PS-R3)

| quantity | value | source |
|---|---|---|
| `n_e` (number of blocks) | 56 | PS-R3 (stage_a.py PARAM_SETS, `ledger/evidence/EV-HQC-b71230.yaml`) |
| `n_2` (bits per block, dup-folded) | 128 | PS-R3, `dup=1` |
| `dup` | 1 | PS-R3 |
| `N` (total bit-vector length) | `n_e * n_2` = 56 * 128 = **7168** | PS-R3 (`N=7168` in stage_a.py) |
| block length used by THIS task's own block-partition code | `L = N / n_e` = 7168 / 56 = **128** | **RULE-2 corrected expression** (coordinator_ruling.yaml). We compute `L` as `N // n_e` in code, never as `n_2 * dup`, even though the two coincide numerically at `dup=1` here (same degeneracy CTRL-IDXMAP's defect hid behind). |
| `m` (pre-specified cell, kept for narrative parity with PS-R3; not used as a firing threshold here) | 17 | PS-R3 |
| `k_max` (highest reported cell) | 18 | PS-R3 (`k_max_at_T=18` at PS-R3@1e7, `amendment_v3.yaml`) |
| reported cells | `k = 2..18` (17 cells) | matches PS-R3's 17-cell report exactly |
| `T` (trials) | 10,000,000 (1e7) | matches PS-R3's allocation |
| jackknife batches | 200 (`N_JACK_BATCHES`) | reused constant, `measure.py` line 92 |

`q_hat_frozen` at PS-R3@1e7 is 0.31994628619715665 (`amendment_v3.yaml`). The planted
law below has population mean `q = 9/28 = 0.321428571...`, a 0.45% relative difference
— order-matched as closely as the closed-form construction below allows without
widening its support (which would weaken the exact-anti-correlation signal; see
Section 5).

## 2. The planted joint law

**Construction (an explicit exchangeable mixture over the block indicators):**

For every trial `t`, independently:

1. Draw `M_t` uniformly from the 3-point set `{17, 18, 19}` (probability 1/3 each).
   This is the number of the `n_e = 56` blocks that will be marked "failing" on this
   trial.
2. Choose the set of `M_t` failing blocks as a **uniformly random size-`M_t` subset**
   of the `n_e` block indices `{0, ..., 55}` — i.e. every one of the
   `C(56, M_t)` subsets of that size is equally likely, and this draw is independent
   across trials.
3. Let `F_j ∈ {0,1}` be the "block failed" indicator: `F_j = 1` iff block `j` was
   chosen in step 2.

This is a standard exchangeable construction (a mixture, over `M_t`, of the
multivariate-hypergeometric / "fixed total" family): conditional on `M_t = v`, the
`F_j` are the indicator vector of a uniformly random `v`-subset, which has an exact,
closed-form negative pairwise correlation (`Cov(F_i,F_j | M_t=v) = v(v-n_e) /
(n_e^2(n_e-1)) < 0` for `0 < v < n_e`). The extra randomness in `M_t` adds a small
positive contribution to the marginal variance of `S_t = sum_j F_j` but, because its
support is narrow (`{17,18,19}`) and entirely surrounds a value close to
`E[S] = q * n_e`, the population moments below in fact show a very strong *negative*
`log2_A_k` at every `k` — i.e. strong anti-correlation, the same *direction* as
PS-R3's observation (though the true mechanisms are unrelated; nothing here claims to
model or explain PS-R3's mechanism, only to give the pipeline a known-answer target of
the same sign).

**Closed form.** Because `S_t` is *exactly* `M_t` on every trial (every subset of size
`M_t` sums to `M_t`), the population factorial moments have a two-line derivation:

```
mu_bar_k = E[C(S,k)] / C(n_e,k) = E[C(M,k)] / C(n_e,k)
         = (1/3) * ( C(17,k) + C(18,k) + C(19,k) ) / C(56,k)      for k = 2..18

q        = E[S] / n_e = E[M] / n_e = (17+18+19)/3 / 56 = 18/56 = 9/28

log2_A_k(k) = log2( mu_bar_k ) - k * log2( q )
```

This is the *exact* estimand (`mubar_k = E[C(S,k)]/C(n_e,k)`, the same estimand
`measure.py`'s comment block cites from the approved contract, `mubar_k =
E[C(S,k)]/C(n_e,k)`) computed on the TRUE population law, not fitted from any sampled
data. `mu_bar_k` and `q` above are exact rationals (`fractions.Fraction`); the table
below converts them to `float64` the same way `measure.py`'s own arithmetic does
(IEEE-754 double), so the reported precision is consistent with what the reused
estimator can itself represent.

### 2.1 Planted `log2_A_k(k)` table (exact, computed 2026-08-06, before any sampling)

| k | mu_bar_k (exact) | mu_bar_k (float) | planted log2_A_k |
|---|---|---|---|
| 2 | 23/231 | 0.09956709956709957 | -0.05332724412846135 |
| 3 | 493/16632 | 0.029641654641654643 | -0.16394044463458357 |
| 4 | 4658/550935 | 0.008454717888680153 | -0.3363079856368989 |
| 5 | 3298/1432431 | 0.002302379660870227 | -0.5755089290487359 |
| 6 | 122/204633 | 0.0005961892754345584 | -0.8873624322504217 |
| 7 | 23/157410 | 0.0001461152404548631 | -1.2785962698872737 |
| 8 | 26/771309 | 3.370892858763479e-05 | -1.7570703364157492 |
| 9 | 17/2337300 | 7.27334959140889e-06 | -2.3320793631074803 |
| 10 | 8/5492655 | 1.4564905314460857e-06 | -3.0147730405328055 |
| 11 | 271/1010648520 | 2.681446562648704e-07 | -3.8187560346206517 |
| 12 | 17/378993195 | 4.4855686656854086e-08 | -4.76097481483005 |
| 13 | 4/595560735 | 6.716359499422003e-09 | -5.8630844320447935 |
| 14 | 113/128045558025 | 8.824983993426585e-10 | -7.153668398603774 |
| 15 | 71/717055124940 | 9.901609727137919e-11 | -8.672097148069227 |
| 16 | 67/7349815030635 | 9.115875667718868e-12 | -10.47587716111893 |
| 17 | 19/29399260122540 | 6.462747674875317e-13 | -12.65660891751783 |
| 18 | 1/31849198466085 | 3.1397964412349716e-14 | -15.382583727766058 |

`q = 9/28 = 0.32142857142857145`.

`planted_arm.py` recomputes this exact table itself (same formula, same
`fractions.Fraction` arithmetic) at the top of its run, before any trial is sampled,
and asserts it reproduces this table bit-for-bit in `float64` — a run-time
reproduction check in the same spirit as `measure.py`'s own INV-NULL bit-identity
gate, but here checking OUR closed form against itself rather than against sampled
Monte Carlo, since the planted law needs no simulation to know exactly.

## 3. How the block-partition / index-map path is exercised

Per the task's binding constraint, the dependency must be injected "at the
block-indicator level... rather than bypassing the block-partition code entirely."
Concretely, per trial (vectorized over a batch of trials):

1. Build the length-`n_e` **block-failure indicator row** `block_fail` via step 2
   above (implemented with a vectorized argsort-of-uniform-keys trick: draw i.i.d.
   `Uniform(0,1)` keys for all `n_e` candidate blocks, rank them, and mark the
   `M_t` lowest-ranked blocks as failing — this realizes an exact uniform draw over
   `M_t`-subsets, a different implementation from `stage_a.py`'s Floyd's-algorithm
   `fixed_weight_support`, but the same *exchangeable, uniform-subset* guarantee).
2. Expand `block_fail` to a **flat length-`N` bit vector** by repeating each block's
   indicator `L` times (`np.repeat(block_fail, L, axis=-1)`), giving a flat array
   structurally analogous to `stage_a.py`'s `bits` array (shape `(B, N)`) before its
   own `bits.reshape(B, n_e, n_2)` call.
3. **Reshape** that flat array into `(batch, n_e, L)` using `L = N // n_e` computed in
   code (RULE-2 fix; never `n_2 * dup`) — the same index-map/gather operation
   `stage_a.py`'s `decode_blocks` performs (`blk = bits.reshape(B, n_e, n_2)`), just
   with our own corrected block length.
4. **Reduce** each block to a recovered failure indicator `F_j = 1[block_sum_j >
   L/2]` — a genuine per-block reduction over the reshaped array (not the real WHT /
   RM decoder, see Section 4), exercised on the SAME reshaped tensor the real decoder
   would consume.
5. Assert `F == block_fail` bit-for-bit (an internal sanity check on our own
   partition code, not a certificate — if this fails the run aborts, fail-closed;
   see `planted_arm.py`'s `assert` in `generate_batch`).
6. `S_t = F.sum(axis=1)`, accumulated into a `(n_e+1,)` histogram, batched into 200
   jackknife batches of `T/200 = 50,000` trials each (dividing evenly, so batch
   boundaries need no `linspace` rounding — the same 200-batch jackknife structure
   `measure.py` uses).

Because a defect in step 3's reshape (e.g. an off-by-one block boundary, or an
interleaved partition, the exact defect classes `CTRL-IDXMAP`'s incidents warned
about) would misalign which flat bit positions are read into which block, the
assertion in step 5 — and, further downstream, the recovered `S_t` histogram and
hence the recovered `log2_Ahat_k` — would depart from the closed-form table in
Section 2.1 if that defect were present. This is exactly the mechanism the red-team
task (`TASK-20260806-21c8da`) is asked to test by injecting such a defect into a COPY
of this arm's own partition code.

### 3.1 What this arm DOES exercise

- Flat-to-`(n_e, L)` block partitioning / reshape with the corrected `L = N/n_e`
  expression (RULE-2).
- A per-block reduction over the reshaped tensor (majority-threshold), structurally
  analogous to (but not identical to) `stage_a.py`'s per-block WHT-argmax reduction.
- Aggregation of block indicators into `S_t` and a `(n_e+1,)` histogram, the exact
  sufficient statistic `measure.py`'s estimator consumes.
- The estimator, ratio-bias structure, and jackknife-variance code `measure.py`
  itself uses (imported/copied verbatim; see `comparison_report.md` for exact line
  citations).
- A 200-batch jackknife identical in count and construction method to PS-R3's.

### 3.2 What this arm does NOT exercise (residuals left in OPEN-6 after this control)

1. **The cryptographic (T)-sampler itself is not run at all.** `stage_a.py` is never
   imported or executed by this task. `CTRStream` (SHA-256 counter-mode PRNG),
   `fixed_weight_support` (Floyd's algorithm for `x,y,r1,r2,e`), `ring_mul_sparse` /
   `ring_mul_dense` (`F_2[X]/(X^n-1)` multiplication), the size-128 fast
   Walsh-Hadamard transform, the `dup`-fold summation, and the lowest-index tie-break
   rule are all untested by this arm. A defect confined to any of those components —
   which is most of PS-R3's actual (T)-arm code — would not be caught here.
2. **Narrower marginal support than PS-R3.** This arm's `S_t` has support of size 3
   (`{17,18,19}`); PS-R3's near-binomial `(T)` arm has support effectively spanning
   most of `{0,...,56}`. A reshape/index defect that only manifests for far-tail `S`
   values, or that depends on the wide dynamic range of block sums the real decoder
   produces, is not exercised.
3. **Homogeneous within-block bits.** The real `(T)` arm's bits vary bit-by-bit
   inside a block (they are the output of ring arithmetic on fixed-weight vectors).
   This arm's blocks are internally homogeneous (all-0 or all-1) by construction, so
   a reshape/index defect that depends on within-block heterogeneity (rather than
   purely on block-boundary alignment) is not exercised.
4. **No sharding / multiprocessing.** PS-R3's `(T)` arm is generated across 8
   multiprocessing shards with disjoint shard IDs; this arm runs its 200 jackknife
   batches sequentially in a single process. Shard-boundary or inter-process
   aggregation defects are not exercised.
5. **CTRL-POSHOM-style between-block covariance is not targeted.** Because
   `measure.py`'s primary estimator is a pure function of the marginal `S_t`
   histogram (verified directly from its code: `hist = np.bincount(S_all, ...)`), the
   *particular* subset chosen in step 2 above does not affect the recovered
   `log2_Ahat_k` at all — only `M_t`'s marginal distribution does. This arm therefore
   is NOT a test of whether `measure.py`'s estimator is sensitive to which blocks
   co-fail (that is CTRL-POSHOM's job, out of this task's scope), only of whether the
   *pipeline as a whole*, run start-to-finish on a known-answer instance built through
   a real block-partition step, recovers the right marginal answer.

None of the above is closed by this task. This is a single control arm for the
*partition/index-map -> S-histogram -> estimator/jackknife* leg of OPEN-6, not a
resolution of it.

## 4. What is reused vs. newly written

Reused (imported unmodified from `measure.py`, cited by exact line number in
`comparison_report.md` after the run): `comb_matrix`, `log2_A_from_hists`,
`N_JACK_BATCHES`, and the batch-histogram + jackknife-SE computation (`measure.py`
lines 730-739), copied verbatim with only local variable names retained (`bh`,
`hist`, `point`, `loo`, `jmean`, `jse`).

Newly written for this task: the planted-law derivation (Section 2), the
block-partition/reduce generator (Section 3), the seed derivation (a fresh
SHA-256-based scheme, distinct `SEED_PREFIX` from `measure.py`'s, so the two tasks'
random streams cannot collide or be mistaken for each other), and the
MATCH/MISMATCH comparison logic (Section 5).

## 5. Comparison rule: MATCH / MISMATCH

`measure.py` does not define a point-estimate-vs-ground-truth confidence interval for
the `(T)` arm (its firing rule instead compares the point estimate against a
*pre-calibrated null quantile table*, which does not exist for this planted law and
would not be the right comparison here — we already know the true value exactly, we
are not testing whether it differs from independence).

This task therefore ADOPTS, explicitly and only for this comparison, the 3-standard-
error convention this campaign already uses elsewhere for consistency checks (e.g.
`measure.py`'s own `NULL_M.TC5_within_3_se_of_one`, and its `T_arm_diagnostics.
three_SE_rel_reference`): for each reported `k`,

```
MATCH   iff  planted_log2_A_k(k)  is within  [ point_k - 3*jackknife_se_k ,
                                                 point_k + 3*jackknife_se_k ]
MISMATCH otherwise
```

using `point_k` and `jackknife_se_k` from the reused jackknife computation
(Section 3, `measure.py` lines 730-739) applied to THIS arm's own sampled histogram.
This is a task-local adoption of an existing campaign convention, not a verbatim rule
transcribed from `measure.py`; `comparison_report.md` states this plainly rather than
presenting it as something already frozen elsewhere.

## 6. Budget plan

Calibration (`/tmp` scratch, not charged as a "shakedown that forces a subsample" —
purely a throughput estimate, 10 chunks of 20,000 trials, ~3.1 core-seconds) measured
≈64,700 trials/core-second for the vectorized partition+reduce step. At that rate,
`T = 1e7` trials costs an estimated ≈155 core-seconds, well inside the 1800
core-second budget authorized for this task. If the full run's actual measured cost
threatens the budget, `planted_arm.py` is instructed to STOP and report the shortfall
explicitly rather than silently truncating `T` (see `planted_arm.py`'s budget guard);
`comparison_report.md` states whichever actually happened.
