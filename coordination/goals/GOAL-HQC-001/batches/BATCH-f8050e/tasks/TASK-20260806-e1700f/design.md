# Design: V3 planted-correlation control arm for OPEN-6 (TASK-20260806-e1700f)

Written and frozen **before** `planted_arm_v3.py` is run on any data (including
before the authorized runs and before any smoke run at reduced scale).
`run_manifest.yaml` records file-timestamp ordering as evidence this was not
written after seeing results, the same discipline `design.md` used in the V1
(`TASK-20260806-e19f6c`) and V2 (`TASK-20260806-047535`) arms.

## 0. What this document is for, and what changed from V2

Both independent reviewers of the V2 arm (Validator `TASK-20260806-01a340`,
Red Team `TASK-20260806-ae74c4`), converging without conferring, found that
V2's demonstrated "17/17 MATCH, 100% boundary-shift detection" rests on
**two fixed, hand-searched, worst-case templates** (`S_TEMPLATE`,
`FAIL_TEMPLATE`). Because a two-fixed-template construction can only ever
express `{0%, 100%}` detection at the population level (the Red Team's own
argument, `red_team_report.md` Section 2), it cannot measure a calibrated
detection RATE. The Red Team independently measured the natural
single-position "read-one-early" flip rate on Bernoulli(0.35) content — this
campaign's own stated proxy for realistic crypto-like noise density
(`design.md` V2 Section 3.2) — at **~8.8% unconditional, ~19.6%
margin-conditioned** (`EV-HQC-9a30d3`), 5-11x lower than V2's 100%.

This V3 arm keeps V1/V2's exchangeable position-marking mechanism unchanged
(so `log2_A_k(k)` remains exactly closed-form, re-derived independently in
Section 2 below, and reproduces V1/V2's frozen table digit-for-digit) but
**replaces the fixed-template step with per-position, per-trial rejection
sampling from Bernoulli(0.35)**: for every block position that needs a given
intended label (fail/succeed), draw a fresh 128-bit Bernoulli(0.35) candidate,
decode it with the REAL `decode_blocks`, and accept it only if the true
decode matches the intended label; otherwise redraw. This keeps `S_t = M_t`
exactly (only label-matching content is ever used, by construction) while
making the realized bit content genuinely heterogeneous across positions and
trials, unlike V2's two fixed templates.

Two distinct deliverables follow from this single construction:

1. **Main run** (`planted_results.json`): the same MATCH/MISMATCH check
   against the closed-form `log2_A_k(k)` that V1/V2 performed, now using the
   heterogeneous rejection-sampled ensemble.
2. **Detection-rate experiment** (`detection_results.json` /
   `detection_rate_report.md`): a SEPARATE injected-defect experiment that
   measures a detection RATE (with a confidence interval) for the
   boundary-shift defect class, directly comparable to the Red Team's
   ~8.8%/~19.6% baselines (`EV-HQC-9a30d3`).

These are reported as two distinct authorized runs (`runs_authorized: 2`),
never conflated.

## 1. Parameters (order-matched to PS-R3, unchanged from V1/V2)

| quantity | value | source |
|---|---|---|
| `n_e` | 56 | PS-R3 (`stage_a.py` `PARAM_SETS`) |
| `n_2` | 128 | PS-R3, `dup=1` |
| `dup` | 1 | PS-R3 |
| `N = n_e * n_2` | 7168 | PS-R3 |
| `L` (block length) | `N // n_e = 128` | **RULE-2**: computed as `N // n_e` in code, never `n_2*dup`; asserted equal to `N_2` as a sanity gate |
| `m` (narrative parity only) | 17 | PS-R3 |
| `k_max` | 18 | PS-R3 |
| reported cells | `k = 2..18` (17 cells) | matches PS-R3/V1/V2 |
| content distribution | i.i.d. Bernoulli(0.35) per bit, rejection-sampled per position/trial | this campaign's own stated "realistic crypto-like noise density" proxy, `design.md` V2 Section 3.2, and the Red Team's own naturalness-measurement distribution (`EV-HQC-9a30d3`) |
| `T_MAIN` (main run) | 500,000 | Section 6 (budget-derived, see calibration) |
| `T_DET_A` (detection, interior-position component) | 2,000,000 | Section 6 |
| `T_DET_B` (detection, full-ensemble component) | 100,000 | Section 6 |
| jackknife batches (main run) | 200 (`N_JACK_BATCHES`) | reused constant, `measure.py` line 92 |

## 2. The planted joint law (position-marking mechanism — unchanged from V1/V2)

Independently re-derived here (identical construction to V1/V2; expected to,
and does, reproduce their frozen table exactly, because — as V1/V2 already
argued — the marginal law of `S_t = sum_j F_j` depends only on WHICH
positions are marked fail, never on WHAT bit content realizes "fail" vs.
"succeed" at a position; this remains true whether that content is
homogeneous (V1), two fixed templates (V2), or a rejection-sampled
heterogeneous ensemble (V3, this task)):

For every trial `t`, independently:

1. Draw `M_t` uniformly from `{17, 18, 19}` (probability 1/3 each) — the
   number of the `n_e = 56` blocks marked "planted-fail" this trial.
2. Choose the set of `M_t` failing block POSITIONS as a uniformly random
   size-`M_t` subset of `{0, ..., 55}` (every subset of that size equally
   likely, independent across trials). This gives the INTENDED label
   `block_fail[t, j] ∈ {0,1}` for every position `j`.
3. Because every subset of size `M_t` sums to `M_t`, `S_t := sum_j
   block_fail[t,j] = M_t` exactly, on every trial, REGARDLESS of what
   content is later generated to realize each label.

```
mu_bar_k = E[C(S,k)] / C(n_e,k) = E[C(M,k)] / C(n_e,k)
         = (1/3) * ( C(17,k) + C(18,k) + C(19,k) ) / C(56,k)      for k = 2..18

q        = E[S] / n_e = E[M] / n_e = (17+18+19)/3 / 56 = 18/56 = 9/28

log2_A_k(k) = log2( mu_bar_k ) - k * log2( q )
```

### 2.1 Planted `log2_A_k(k)` table (exact, independently recomputed, matches V1/V2's frozen table digit for digit)

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

`q = 9/28 = 0.32142857142857145`. `planted_arm_v3.py` recomputes this exact
table itself (same closed form, `fractions.Fraction` arithmetic) at the top
of every run, before any trial is sampled, and asserts bit-for-bit agreement
with the frozen table above.

## 3. The rejection-sampling content construction

### 3.1 Definition

For a position with intended label `ℓ ∈ {0 (succeed), 1 (fail)}`:

1. Draw a candidate 128-bit block `c` i.i.d. Bernoulli(0.35) per bit.
2. Decode `c` with `decode_blocks` (single-block call, `n_e=1`).
3. If the decoded `F == ℓ`, ACCEPT `c` as this position's realized content.
   Otherwise REDRAW (go to 1).

This is applied **independently to every one of the 56 positions in every
trial**, using the intended label `block_fail[t,j]` already fixed by Section
2's position-marking mechanism (the marking mechanism runs first, cheaply,
with zero decode calls; only the CONTENT realizing each label is
rejection-sampled). Because `decode_blocks` folds and decodes each of the
`n_e` blocks in a trial independently (`stage_a.py` line 296: the WHT/argmax
step operates along the last axis after a per-block reshape, with no
cross-block term), a block accepted in isolation (`n_e=1` decode) decodes
identically when later assembled into a full 56-block trial and decoded
again — this is asserted, not merely assumed, by the same fail-closed
`F == block_fail` self-check V1/V2 used (Section 4).

This construction keeps `S_t = M_t` exactly (Section 2), because only
label-matching content is ever used — the marginal law of `S_t` is untouched
by rejection sampling, exactly as it was untouched by V1's homogeneous
blocks or V2's two fixed templates.

### 3.2 Pre-registration calibration (NOT charged to this task's budget, same convention as V1/V2's throughput/template-search calibration)

Conducted in scratch space
(`/tmp/.../scratchpad/bench_v3.py`, `bench_v3b.py`), using the SAME
sha256-pinned `decode_blocks` import (`06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`)
the authorized script uses:

**Acceptance probability.** Over 2,000,000 i.i.d. Bernoulli(0.35) 128-bit
candidates, decoded with the real `decode_blocks`:

```
P(candidate decodes F=1, "fail")     = 0.211079
P(candidate decodes F=0, "succeed")  = 0.788921
```

(These are properties of the RAW Bernoulli(0.35) population under the real
decoder; they are NOT the same quantity as the planted marginal label
probability `q = 9/28 ≈ 0.3214` from Section 2 — the two happen to be of
similar order but measure different things: one is "how often does random
content decode to fail", the other is "how often is a position LABELED
fail by the marking mechanism". No relationship between them is assumed or
required.)

**Rejection-sampling throughput and draw statistics**, measured on the exact
vectorized construction `planted_arm_v3.py` uses (redraw only rejected
positions each round, one `decode_blocks` call per round over all pending
positions):

| batch shape | blocks | mean draws/accepted block | max draws observed | throughput (trials/core-second, generation only) |
|---|---|---|---|---|
| 5,000 trials x 56 positions | 280,000 | 2.374 | 64 | ~942-1006 |
| 20,000 trials x 56 positions | 1,120,000 | 2.386 | 55 | ~510-622 |
| 3,000 trials x 56 positions, 8 consecutive batches | 1,344,000 | 2.37-2.39 (stable across batches) | — | ~1043 (rejection-sampling only) / ~739 (including the full-trial self-check decode pass) |
| 20,000 trials x 2 positions | 40,000 | 2.376 | 39 | ~39,100-43,300 |
| 100,000 trials x 2 positions | 200,000 | 2.386 | 53 | ~28,600-29,700 |
| 400,000 trials x 2 positions | 800,000 | 2.386 | 65 | ~19,100-20,300 |

Mean draws per accepted block is stable at **~2.38** regardless of batch
size or position count (as expected: it is a property of the per-label
acceptance probabilities above, `0.34*[1/0.211] + 0.66*[1/0.789] ≈ 2.38`
using the planted label mix `q≈0.321` fail / `1-q≈0.679` succeed — this
is reported as a consistency check, not re-derived as a separate estimate).
**This rejection rate is itself reported as a finding**: on average, ~1.4
candidates are discarded for every one accepted (a ~58% rejection rate per
draw), and the ensemble is therefore genuinely resampled/heterogeneous, not
a disguised small fixed set — confirmed independently in Section 3.3.

Full-56-position batches are markedly slower per trial than 2-position
batches (as expected: ~28x more rejection-sampling decode volume per
trial), and throughput per trial degrades somewhat as full-ensemble batch
size grows (942-1006 trials/core-sec at batch 5,000 vs. 510-622 at batch
20,000) — attributed to memory/cache effects in the vectorized WHT step
at larger array sizes, not to the rejection-sampling logic itself. This
motivated the batch-size choice in Section 6 (batch 2,500-3,000, close to
the more favorable end of this range).

**This calibration is not charged to this task's core-second/wall-clock
budget**, the same convention V1's throughput calibration and V2's
throughput/template-search calibration used.

### 3.3 Confirming the ensemble is genuinely heterogeneous, not a disguised fixed set

`planted_arm_v3.py`'s own authorized runs report, for a sample of accepted
content: the number of DISTINCT 128-bit values observed among a random
sample of `min(10,000, T)` accepted blocks (via `sha256` digest dedup) and
the fraction of that sample that repeats any other value in the same
sample. Because each accepted value is drawn from an unconstrained
Bernoulli(0.35) distribution over `2^128` possible outcomes conditioned only
on a global decode-label bit, one specific content value repeating within
a sample of thousands is expected to be effectively never (this is reported
as a direct, cheap distinguishing check against V2's construction, where
100% of "succeed" blocks were bit-identical to one fixed template and 100%
of "fail" blocks to another).

## 4. Main-run generation procedure and MATCH/MISMATCH rule

Per jackknife batch (`SUB_CHUNK` trials, one generation call per batch,
matching V1/V2's per-batch RNG-stream structure):

1. Draw `M_t ~ Uniform{17,18,19}` and a uniform random `M_t`-subset of the 56
   block positions (`block_fail`, boolean array), via the SAME
   argsort-of-uniform-keys vectorized construction V1/V2 used.
2. For every position `(t,j)` in the batch, rejection-sample 128-bit content
   matching `block_fail[t,j]` (Section 3.1), vectorized: redraw only the
   still-pending positions each round.
3. Assemble the flat `(batch, N)` bit tensor from the accepted content.
4. Call `decode_blocks(bits, n_e, n_2, dup)` — THE REAL DECODER, imported
   read-only, sha256-pinned, unmodified — on the FULL assembled trial.
5. Assert `F == block_fail` bit-for-bit (fail-closed self-check). Because
   every position's content was individually verified to decode to its
   intended label BEFORE assembly (step 2), and `decode_blocks` decodes
   blocks independently (Section 3.1), this check is expected to ALWAYS
   pass; a failure would indicate `decode_blocks` is not, in fact,
   block-independent under this arm's exact call pattern — itself a
   reportable finding, and the run aborts rather than reporting a result
   whose premise has failed.
6. `S_t = F.sum(axis=1)`, accumulated into this batch's `(n_e+1,)`
   histogram.

`L = N // n_e` is asserted equal to `N_2` (RULE-2).

After all batches: `measure.py`'s `comb_matrix`/`log2_A_from_hists` (reused
verbatim, sha256-pinned) and the `point`/`loo`/`jmean`/`jse` jackknife block
(reproduced formula-for-formula from `measure.py` lines 730-739, same
convention V1/V2 used) are applied to the accumulated histogram.

**Comparison rule (identical to V1/V2, adopted explicitly, not a verbatim
`measure.py` rule):**

```
MATCH   iff  planted_log2_A_k(k)  is within  [ point_k - 3*jackknife_se_k ,
                                                 point_k + 3*jackknife_se_k ]
MISMATCH otherwise
```

## 5. Detection-rate experiment design

**This is a SEPARATE experiment from the main run, using a fresh, distinct
seed prefix, its own generation, and its own output artifact
(`detection_results.json`).** It measures the FRACTION of positions whose
decoded label `F` flips under a boundary-index-shift perturbation, with a
confidence interval — not merely whether a flip is possible.

### 5.1 The perturbation operator (identical definition to V2's `design.md` Section 3.5, re-implemented here, not sha256-pinned since it is this campaign's own analysis code, not part of the reused `measure.py`/`stage_a.py` pipeline)

```
shift_read_one_early(block, foreign_last_bit):
    out[0]    = foreign_last_bit
    out[1:]   = block[:-1]
```

i.e., the block drops its own true last bit and gains a foreign bit (from a
neighboring position's last bit) at the front — the literal shape of both
the V1 (global off-by-one) and V3 (last-block-early) defect classes named by
this campaign.

A position's decode is said to **FLIP** if `decode_blocks(perturbed) !=
decode_blocks(unperturbed)` — equivalently here, since unperturbed content
is rejection-sampled to match its intended label exactly, `perturbed_F !=
intended_label`.

### 5.2 Component A — interior single-position rate (primary, directly comparable to the Red Team's ~8.8%/~19.6% baselines)

Uses positions 9 and 10 (an interior pair, avoiding the array boundary
effects at position 0 or 55; position 10 mirrors the Red Team's own
"position-generality probe", `red_team_report.md` Section 1). For each
trial:

1. Draw the FULL 56-position label array (`block_fail`, Section 2) — needed
   so that positions 9 and 10's labels retain the correct joint/pairwise
   structure the real marking mechanism induces, even though content is
   only generated for these two positions.
2. Rejection-sample content ONLY for positions 9 and 10 (Section 3.1) —
   this is what makes Component A cheap (Section 3.2's 2-position throughput
   figures apply).
3. Compute the WHT margin of position 10's accepted content (`top1 - top2`
   of `|wht128(...)|`, reusing `stage_a.py`'s `wht128` directly, sha256-pinned
   — the identical quantity V2's `design.md` Section 3.1 defined, and the
   quantity the Red Team's naturalness measurement conditioned on).
4. Apply `shift_read_one_early` to position 10's content under TWO distinct
   foreign-bit sources, reported SEPARATELY (this is a disclosed
   methodological choice, not a single number, precisely because it is the
   axis the Red Team's V2 review flagged as the likely source of a
   rejection-sampling bias — see Section 7):
   - **`paired_neighbor`**: foreign bit = the LAST bit of position 9's own
     accepted (rejection-sampled, label-matching) content in the SAME
     trial. This is the ensemble-faithful variant: it is what an actual
     56-position tiled V3 trial would show if positions 9 and 10 were
     adjacent (they are).
   - **`independent_foreign_bit`**: foreign bit = a FRESH, independent
     Bernoulli(0.35) draw, NOT conditioned on any decode label. This
     replicates the Red Team's own stated methodology
     (`red_team_report.md` Section 2: "natural single-position
     'read-one-early' flip rate (random foreign bit)") as closely as this
     arm's own record of that methodology allows, isolating the
     REJECTION-SAMPLING-OF-THE-TARGET-BLOCK effect as the sole
     methodological difference from the Red Team's own number.
5. Redecode the perturbed content (single-block `decode_blocks` call) and
   record `flipped = (perturbed_F != intended_label)` for every trial, under
   both foreign-bit variants.
6. Report, for each foreign-bit variant, and additionally restricted to the
   subset of trials where position 10's margin `<= 4` (V2's templates'
   margin, and the Red Team's own conditioning threshold):
   - point estimate `p_hat = flips / T_DET_A`
   - a Wilson score 95% CI and a normal-approximation `±3 SE` interval
     (the campaign's own 3-SE convention, Section 4)
   - explicit numeric comparison against the Red Team's 8.8%
     (unconditional) and 19.6% (margin-conditioned) figures.

### 5.3 Component B — full-ensemble global and last-block-only rates (supplementary, matches the campaign's own named "global off-by-one" / "last-block-early" defect shapes exactly)

Uses the SAME full 56-position generation as the main run (Section 4,
steps 1-3), on a separate, smaller `T_DET_B`. For each trial, TWO
perturbation variants are applied and redecoded, using the ACTUAL
tiled-neighbor content (the `paired_neighbor` convention from Component A,
since this component's whole point is to reflect the real tiled
construction):

- **global** (V1-named class): `shift_read_one_early` applied to EVERY one
  of the 56 positions simultaneously (position `j`'s foreign bit = position
  `j-1 mod 56`'s own accepted last bit). Reports the flip rate over all
  `56 * T_DET_B` position-level observations.
- **last-block-only** (V3-named class): the same shift applied ONLY to
  position 55 (foreign bit = position 54's own accepted last bit). Reports
  the flip rate over `T_DET_B` observations (one per trial).

### 5.4 What this experiment does NOT establish

- It does not measure a detection rate at the level of the full-arm
  `log2_Ahat_k` ESTIMATOR statistic (that is what the MAIN run's own
  histogram-based MATCH/MISMATCH answers, for the UN-perturbed construction
  only — this task does not inject a defect into the main run's own
  reported histogram; Section 0 requires these stay separate deliverables).
- The `paired_neighbor` and `independent_foreign_bit` numbers, and the
  margin-conditioned subset, are reported as DISTINCT figures, not averaged
  or otherwise combined into one number, because they are not measuring
  exactly the same thing (Section 7 discusses the comparability caveats
  precisely).

## 6. Budget: calibration-informed choice of T, and the residual this leaves

Using Section 3.2's calibration (uncharged): full-ensemble generation at the
planned batch size (~2,500-3,000 trials/batch) sustains **~740-1,000
trials/core-second including the self-check decode pass**; 2-position
generation sustains **~19,000-43,000 trials/core-second** depending on
batch size.

| item | planned T | estimated cost (core-seconds) | basis |
|---|---|---|---|
| main run (Section 4) | 500,000 | ≈500,000 / 740 ≈ 676 | conservative end of the full-ensemble throughput range (batch 3,000, including self-check) |
| detection Component A (Section 5.2) | 2,000,000 | ≈2,000,000 / 19,500 ≈ 103, x~2 for both foreign-bit variants' extra redecode pass ≈ 150-200 | conservative end of the 2-position throughput range |
| detection Component B (Section 5.3) | 100,000 | ≈100,000 / 740 ≈ 135, x~1.5 for the two perturbation redecode passes ≈ 200 | same basis as main run |
| **total estimated (both authorized runs)** | — | **≈1,050-1,150 of 1,800 authorized (≈58-64%)** | leaves headroom for provenance, estimator, jackknife, JSON I/O, and wall-clock variance |

**Budget allocation between the two authorized runs** (this task's own
allocation, not itself a coordinator-approved split, recorded here for
audit): main run guarded against **1,000 core-seconds / 1,800 wall-clock
seconds**; detection run guarded against **800 core-seconds / 1,500
wall-clock seconds**; sums to the task's authorized 1,800 core-seconds and
comfortably inside the 3,600-second wall-clock budget for two sequential
script invocations. If the actual measured cost of either run differs
materially from this estimate, `planted_arm_v3.py`'s wall-clock budget guard
(matching V1/V2's `WALL_BUDGET` pattern) stops the run and reports the
shortfall as an INFRASTRUCTURE outcome, never a silently truncated result.
The achieved `T` for both runs is reported honestly in
`planted_results.json`/`detection_results.json` and `run_manifest.yaml`,
whichever it turns out to be — this design section states an ESTIMATE, not
a guaranteed target.

**Residual this leaves, stated plainly (same discipline as V1/V2 Section
5):** at `T_MAIN=500,000` (smaller than V2's `T=1,000,000`, itself already
a 10x reduction from PS-R3/V1's `T=1e7`), jackknife SEs on the main run are
wider than V2's; the per-cell SE is reported explicitly in
`planted_results.json` so this is checkable, not asserted. At
`T_DET_A=2,000,000`, the expected SE on a proportion near 8-20% is small
(≈0.02-0.03 percentage points at 1,000,000-2,000,000 samples), comfortably
enough to distinguish a result an order of magnitude different from the
Red Team's baselines, but not enough to certify agreement to sub-percent
precision if the true rate is close to the boundary of what a few
thousand samples could already resolve — the achieved CI width is reported
explicitly rather than asserted adequate.

## 7. What this arm exercises and what it still does not (honest disclosure, matching V1/V2's pattern)

### 7.1 Newly exercised, relative to V2

- Rejection-sampled, genuinely heterogeneous per-position, per-trial content
  (Section 3), replacing V2's two fixed templates — confirmed distinct via
  Section 3.3's duplicate-check.
- A detection RATE, with a confidence interval, for the boundary-shift
  defect class, directly comparable in number to the Red Team's ~8.8%/~19.6%
  baselines (Section 5).
- The observed rejection rate itself (~58% of draws discarded, ~2.38 mean
  draws per accepted block) is reported as a finding about how "natural" vs.
  "searched" this ensemble is (Section 3.2).

### 7.2 Still NOT exercised (residuals carried forward from V1/V2, restated precisely)

1. **The cryptographic `(T)`-sampler is still not run at all.** `CTRStream`,
   `fixed_weight_support`, `ring_mul_sparse`/`ring_mul_dense`, and the
   multiprocessing shard structure remain entirely untested by this arm.
   This arm constructs planted per-block content via REJECTION SAMPLING
   from an i.i.d. Bernoulli(0.35) PROXY distribution, verified only against
   the decode label — not by sampling a genuine
   fixed-weight-support-derived `(T)`-distributed error vector end-to-end.
   Rejection sampling is a stronger control than V2's fixed templates along
   the content-heterogeneity axis, but it is still not the real sampler.
2. **Narrower marginal support than PS-R3.** `S_t`'s support is still the
   3-point set `{17,18,19}`, versus PS-R3's near-binomial spread over most
   of `{0,...,56}` (same residual V1/V2 named).
3. **REJECTION-SAMPLING BIAS is a live, named, un-closed concern, not
   merely a theoretical one — this design deliberately does NOT claim it is
   absent.** Conditioning accepted content on "true decode matches the
   intended label" necessarily changes the accepted population's margin
   distribution relative to an UNCONDITIONED Bernoulli(0.35) draw (the Red
   Team's own naturalness-measurement population). Section 3.2's own
   acceptance-probability numbers already show label and raw-decode
   probability are not the same quantity; whether the accepted subpopulation
   is systematically closer to (survivorship bias toward easier detection)
   or farther from (bias toward harder detection) the WHT decision boundary
   than the Red Team's unconditioned figures is exactly what
   `detection_rate_report.md` reports empirically (accepted-population
   margin statistics, compared numerically against the Red Team's
   min=0/median=8.0/mean=10.70/max=60/38.8%-margin≤4 figures), and exactly
   what `TASK-20260806-7008de` (this batch's Red Team dispatch) is charged
   with probing independently. This design does not resolve the question;
   it instruments it.
4. **No sharding/multiprocessing.** Single-process generation, unlike
   PS-R3's 8-shard `(T)` arm.
5. **CTRL-POSHOM-style between-block covariance is still not targeted** by
   the MAIN run's own MATCH/MISMATCH statistic, for the same reason
   V1/V2 noted: `measure.py`'s primary estimator is a pure function of the
   marginal `S_t` histogram.
6. **The detection-rate experiment measures block-level flip rate, not the
   full-arm `log2_Ahat_k` estimator's response to an injected defect.** A
   high (or low) block-level flip rate is suggestive but is a different
   statistic from what the campaign's estimator would show if a defect were
   injected into a full run and re-measured end-to-end (that full
   injection-into-the-estimator experiment is what the Red Team did for V1
   and V2's OWN fixed-template constructions, `TASK-20260806-21c8da`,
   `TASK-20260806-ae74c4` Section 1; this task's Component A/B measure the
   PER-BLOCK flip rate that would feed such an experiment, not the
   estimator-level consequence itself, given this task's budget).

None of the above is closed by this task. This is a single control arm for
the *real decode_blocks reshape/decode -> S-histogram -> estimator/jackknife*
leg of OPEN-6, now with genuinely heterogeneous planted content and a
measured (not merely possible) detection rate — a strictly stronger control
than V2 along the heterogeneity/calibration axis both reviewers named, but
not a resolution of OPEN-6, and not a resolution of the rejection-sampling
bias question either (Section 7.2 item 3).

## 8. What is reused vs. newly written

Reused (imported unmodified, sha256-pinned):

- From `measure.py`
  (`a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`):
  `comb_matrix` (lines 213-222), `log2_A_from_hists` (lines 225-246),
  `N_JACK_BATCHES` (line 92, cross-checked), and the batch-histogram +
  point/loo/jmean/jse jackknife block (lines 730-739), copied verbatim with
  the same variable names, exactly as V1/V2 did.
- From `stage_a.py`
  (`06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`):
  `decode_blocks` (line 286), `wht128` (line 270, both called directly by
  this task for margin computation AND internally by `decode_blocks`).
  NOT reused: `CTRStream`, `fixed_weight_support`, `ring_mul_sparse`/
  `ring_mul_dense`, `support_to_int*`, `rm17_codewords`/
  `brute_force_decode` (V2 used these to cross-verify its two FIXED
  templates; this arm's rejection sampling verifies EVERY accepted block
  directly against `decode_blocks` at generation time instead, which is a
  per-block guarantee rather than a per-template one, so the
  `brute_force_decode` cross-check is not needed here — its ABSENCE is a
  disclosed, deliberate scope choice, not an oversight), the `(T)`/NULL-M
  shard workers, and every phase function (`phase_oracle`,
  `phase_contract_checks`, `phase_smoke`, `phase_calibrate`, `main`).

Newly written for this task: the rejection-sampling content construction
(Section 3), the detection-rate experiment design (Section 5), the
Wilson-score/normal-approximation CI computation, the seed derivation (fresh
`SEED_PREFIX`s, distinct from V1's, V2's, and `measure.py`'s), and the
MATCH/MISMATCH comparison logic (Section 4, identical rule to V1/V2, applied
to this arm's own histogram).

## 9. Pre-registration ordering

This document, including Section 2's frozen table, Section 3's rejection
sampling definition, Section 5's detection-rate experiment design (including
the exact two foreign-bit variants and the margin-conditioning rule), and
Section 6's planned `T` values, was written and frozen BEFORE
`planted_arm_v3.py` was run on any real (non-scratch, non-calibration) data.
`run_manifest.yaml` records file-timestamp evidence for this ordering, the
same discipline V1/V2 used.
