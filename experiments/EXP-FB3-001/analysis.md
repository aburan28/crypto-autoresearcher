# EXP-FB3-001 analysis — factor-base geometry battery, exact counting

**Experiment:** EXP-FB3-001 version 1 (approved, DEC-20260717-002) under
amendment EXP-FB3-001-AMD-001 (approved). **Task:** TASK-20260724-228.
**Hypothesis:** H-FB3-001. **Question:** RQ-FB3-001.

**Runs:** `RUN-FB3-001-CTRL` (controls), `RUN-FB3-001-N14`, `RUN-FB3-001-N16`,
`RUN-FB3-001-N18` (measurement), `RUN-FB3-001-FAMILY` (aggregation). All five
runs terminal and `valid`. Implementation note:
`implementation/implementation.md`. Analytic arm: `conservation.md`.

**What was measured.** The exact number of `m = 3` multiset decompositions of
**every** target in the group, for six pre-registered factor-base geometries at
`N ~ 2^14, 2^16, 2^18`, on 4 generated curves per size with 4 replicate seeds,
against a matched-random permutation null of 200 draws per cell.

**What was not measured.** The cost of *finding* a decomposition. This battery
measures decomposition yield and coverage only; the index-calculus cost sits in
the point-decomposition solve, which is untouched here. Discrete logs of
factor-base points are known **by construction, for measurement only** — nothing
below is a step of an attack and no cost, speedup, or attack claim is derived
from that availability.

---

## 1. Port fidelity against the recorded H016/H017 statistics (reported first)

Required before any family verdict (handoff constraint). Source:
`inputs/h100_session/h016_base_yield.json`. Control block D of
`RUN-FB3-001-CTRL`: **17 of 17 checks pass on each of the 4 recorded cells.**

| check | result |
|---|---|
| group order recomputed from recorded `(p,a,b)` by exact character sum | `8329, 14143, 128857, 113621` — **exact match** to all four recorded `N` |
| order prime, inside the Hasse interval | yes, all four |
| recorded `theory_mean_triples_per_target` vs `C(B+2,3)/N` | **exact match** to `1e-12` on all four cells (the prior harness used the same conservation constant) |
| recorded per-base `total` vs `mean_per_target * 800`, and vs the sum of the recorded per-target counts | consistent, all four cells, all three bases |
| recorded `qr_vs_random.ratio`, `sm_vs_random.ratio` | reproduced from the recorded means to `1e-9` |
| recorded `perm_null.mean_band_95` | reproduced as the 2.5/97.5 percentiles of the recorded `null_means` to `1e-9` |
| recorded `qr_emp_p_two_sided` | **convention identified exactly**: `2*min(#{null>=obs}, #{null<=obs})/n`, reproducing `0.40, 0.90, 0.44, 0.76` on the nose |
| H017 small-multiples base re-derived exactly (`{1,...,B}`) and pushed through the recorded 800-target sampling protocol | recorded sampled means `0.0475, 0.09625, 0.34, 0.0` all inside the reconstructed 95% sampling bands |
| matched-random reconstruction (100 exact bases per cell) vs recorded `random` and `qr` sampled means | both inside the reconstructed band on all four cells; band overlaps the recorded permutation band |

Two fidelity findings worth recording:

* **The prior harness's own "theory mean" is the conservation constant.** The
  recorded `theory_mean_triples_per_target` equals `C(B+2,3)/N` exactly in all
  four cells. The identity of `conservation.md` was therefore already implicit
  in the H016 record; this experiment makes it explicit and tests its
  consequences.
* **The prior sampled estimator was extremely unstable for concentrated bases.**
  The H017 small-multiples geometry has an exact mean-yield ratio of exactly
  `1.000000` and an exact coverage ratio of `0.0126` (2^14) to `0.0021` (2^18).
  Its recorded 800-target sampled ratio ranged from `0.0000` to `1.7895` across
  the four recorded curves. Both extremes are inside the reconstructed sampling
  band. Amendment change AMD-2 (exact counting) removes precisely this
  variance, and the port-fidelity control shows the prior numbers were correct
  *given* their protocol.

**One item could not be reproduced bit-exactly, by construction:** the H016 QR
base was built by an r-adding walk whose RNG stream, index function, and start
point are not recorded. A same-family reconstruction (r = 20,
`c_j in [1, 2^10)`, recorded seed) puts the recorded QR sampled mean inside the
reconstructed band on all four cells, but this is a distributional comparison,
not a replay. The QR geometry appears only in the exploratory section (§6),
never as a pre-registered cell.

## 2. Controls

| control | scope | verdict |
|---|---|---|
| Closed-form total (`sum_r c(r)` = closed form of the cell's typing pattern) | every structured, null, and exploratory cell in all three size runs: **67 784 checks** | **pass**, 0 failures |
| Counter verification against literal brute-force enumeration, on the **full per-target count vector** | 46 cases, 148 assertions (`N in {211,307,401,503,1009}`, `B in {5,8,13,20}`, adversarial additively-structured bases, both typed patterns) | **pass** |
| Independent recount of measured cells (direct multiset enumeration + FFT route) | 43 cells per size run (all structured cells + first 5 null draws per label) | **pass** |
| FFT rounding margin | worst `max abs(value - round(value))` over the campaign: `5.5e-12` against a `0.25` safety threshold | **pass** |
| Curve order and dlog-table verification | 12 of 12 generated curves: order prime, in Hasse interval, `N*G = O` by an independent double-and-add path, enumeration closes at `N`, exactly `(N-1)/2` distinct x, `x`/`y` pairing, bijective log table, 20 seeded spot checks | **pass** |
| Greedy incremental sumsets vs brute force, step by step; held-out leakage | `Sigma_3` from the counts equals brute force; internal tallies match; first-step gain provably maximal; selection function has no access to the held-out mask | **pass** |
| Rational-reconstruction height: enumerated minimum over representations vs continued-fraction convergents | all `p = 16381` values of `x`, 0 disagreements | **pass** |
| H017 log-space claim (`dedup(x(jG)) = {1..B}`) | verified on a real curve | **pass** |
| Port fidelity (§1) | 4 recorded cells x 17 checks | **pass** |
| Reproduction from the recorded command at the recorded revision | `RUN-FB3-001-N14` and `RUN-FB3-001-N18` re-run: bit-identical raw results except wall-clock fields | **pass** |
| Feasibility | 6 pre-registered geometries x 3 sizes x 4 curves x 4 seeds = 288 cell records: **288 measured, 0 infeasible, 0 invalid**. In the exploratory section only, 4 of 48 `qr_walk_H016` records are `infeasible` (see §6). | n/a |

## 3. Primary metric: exact mean-yield ratio, Holm-corrected across the 8-cell family

Family = 6 new geometries + 2 prior cells (H016 QR, H017 small multiples), one
Holm-Bonferroni correction per size, `alpha = 0.05`, family size 8 at every size
(prior-cell slots retained even where censored, which is conservative).
Permutation p-values use `(r+1)/(n+1)` with 200 draws (floor `0.00498`;
`8 x 0.00498 = 0.0398 < 0.05`, so the test is able to reject — see deviation D1).
"Family-wise CI" is the `99.375% = 1 - 0.05/8` bootstrap CI across the 16
replicates (4 curves x 4 seeds), which is conservative relative to Holm.

Absolute scale, for orientation: the exact mean is
`C(B+2,3)/N = 1.1146 / 1.0755 / 1.0436` at `2^14 / 2^16 / 2^18`, and the
matched-random exact coverage is `0.6734 / 0.6594 / 0.6480`.

| geometry | 2^14 ratio | 2^16 ratio | 2^18 ratio | family-wise CI at 2^18 | p_holm (all sizes) | slope vs log2 N | slope CI95 |
|---|---|---|---|---|---|---|---|
| `high_bit_interval` | `1.000000` | `1.000000` | `1.000000` | `[1.000000, 1.000000]` | `1.000` | `0.0` | `[-3.8e-17, 3.8e-17]` |
| `small_height` | `1.000000` | `1.000000` | `1.000000` | `[1.000000, 1.000000]` | `1.000` | `0.0` | `[-3.8e-17, 3.8e-17]` |
| `coset_union` | `1.000000` | `1.000000` | `1.000000` | `[1.000000, 1.000000]` | `1.000` | `0.0` | `[-3.8e-17, 3.8e-17]` |
| `mixed_two_base` (typed) | `0.372639` | `0.370000` | `0.374919` | `[0.374919, 0.374919]` | `0.0398` **rejected, deficit** | `+0.000570` | `[0.000219, 0.000921]` |
| `asymmetric_sizing` (typed, `(8,1,1)`) | `0.034190` | `0.041821` | `0.041980` | `[0.041980, 0.041980]` | `0.0398` **rejected, deficit** | `+0.001948` | `[0.001887, 0.002008]` |
| `greedy_optimized` (held-out half) | `0.955409` | `0.971719` | `0.980631` | `[0.979477, 0.981536]` | `0.0398` **rejected, deficit** | `+0.006306` | `[0.005686, 0.006941]` |
| `prior_H016_qr_base` (recorded, sampled) | `0.9629` | censored | censored | n/a | `1.000` | not applicable (recorded at 2^14, 2^17) |
| `prior_H017_small_multiples` (recorded, sampled) | `0.3609` | censored | censored | n/a | `0.0495` **rejected, deficit** | not applicable |

Prior-cell detail (recorded protocol: 800 sampled targets, not exact counting):
H016 QR sampled ratios `1.0470 / 0.8788` at 2^14 and `1.0461 / 0.9299` at 2^17,
per-curve p `0.386 / 0.871 / 0.455 / 0.802`; H017 small multiples sampled ratios
`0.2550 / 0.4667` at 2^14 and `1.7895 / 0.0000` at 2^17. The 2^17 cells are
outside the growth-arm sizes and enter no per-size family; they are reported for
completeness of the F3 accounting.

**Every Holm rejection in the family is a deficit.** No cell at any size has a
mean-yield ratio above 1. The three untyped geometries sit at exactly 1 with
zero-width CIs and point-mass nulls — the mathematically forced value
(`conservation.md`, consequences (i) and (ii)). The three rejections are the
three predicted escape routes, and each is fully accounted for:

* `mixed_two_base` and `asymmetric_sizing` are compared against the frozen
  "matched random base, same size" control, which is untyped at the same **total**
  `B`. Their deficits are the exact closed-form typing penalty of consequence
  (iv): measured `0.3749` versus the predicted `6/16 = 0.375` for the (1,2)
  pattern, and `0.0420` for the `(8,1,1)` split whose closed form is
  `B1*B2*B3 / C(B+2,3)`. Against a **same-typing** matched-random control both
  have a mean ratio of exactly `1.000000` at every rung and every size, i.e.
  there is no element-geometry effect in either cell — only a size/typing effect.
  Their positive slopes are the ceiling arithmetic of splitting `B` into integer
  sub-bases (the deficit shrinks slightly as `B` grows), not a growing advantage.
* `greedy_optimized` is evaluated on the held-out half. Its whole-group total
  obeys the identity exactly; the greedy shifts count mass onto the training half
  (training mean ratio `1.0446 / 1.0283 / 1.0194`), and the held-out mean is
  correspondingly starved. The held-out deficit shrinks toward 1 with `N`
  (slope `+0.0063`), i.e. the overfitting weakens as the group grows.

## 4. Secondary metric: exact coverage (the H017 starvation diagnostic)

Per AMD-5, coverage is reported with the direction of every deviation stated,
and a coverage **deficit is not a success** under the frozen criterion.
Holm across the same 8-cell family on the coverage ratio rejects only
`mixed_two_base` and `asymmetric_sizing` (both deficits) at every size; all four
other geometries have `p_holm = 1.000`.

| geometry | 2^14 | 2^16 | 2^18 | family-wise CI at 2^18 | per-size permutation p (mean) | slope | slope CI95 |
|---|---|---|---|---|---|---|---|
| `high_bit_interval` | `0.99878` | `1.00376` | `0.99891` | `[0.99852, 0.99922]` | `0.53 / 0.41 / 0.66` | `+0.000033` | `[-0.00073, +0.00083]` |
| `small_height` | `0.99984` | `1.00108` | `0.99965` | `[0.99844, 1.00101]` | `0.65 / 0.33 / 0.52` | `-0.000047` | `[-0.00062, +0.00053]` |
| `coset_union` | `0.99645` | `1.00013` | `1.00121` | `[0.99976, 1.00245]` | `0.39 / 0.77 / 0.45` | `+0.001189` | `[+0.000086, +0.00226]` |
| `mixed_two_base` | `0.49661` | `0.50145` | `0.49794` | `[0.49179, 0.50324]` | `0.005` (deficit) | `+0.000333` | `[-0.00284, +0.00358]` |
| `greedy_optimized` | `1.00770` | `1.00647` | `1.00299` | `[1.00105, 1.00456]` | `0.47 / 0.30 / 0.28` | `-0.001176` | `[-0.00196, -0.00037]` |
| `asymmetric_sizing` | `0.05551` | `0.06683` | `0.06611` | `[0.06597, 0.06626]` | `0.005` (deficit) | `+0.002651` | `[+0.00257, +0.00273]` |

Two entries are above 1 and need care, because they are the only above-1
numbers anywhere in the battery:

* **`greedy_optimized`, +0.30% coverage at 2^18** (`+0.77%` at 2^14). The
  family-wise CI excludes 1 at all three sizes, yet the per-cell permutation
  p-value is `0.28-0.47`. Both statements are correct and measure different
  things: each individual cell sits only about one null standard deviation above
  its own matched-random draws, but the same small excess appears in nearly all
  16 replicates, so the CI of the *mean* ratio is tight. The direction is an
  advantage; the **slope is negative and its CI excludes 0**, so the excess
  decays with `N` (`+0.77% -> +0.65% -> +0.30%`). The greedy training half
  behaves as designed (`+8.9% / +5.9% / +3.9%` coverage) and the transfer gap
  (`0.0544 / 0.0346 / 0.0235`) shows that nearly all of that gain does not
  transfer, also decaying with `N`.
* **`coset_union`, +0.12% coverage at 2^18.** The per-size family-wise CI
  contains 1 at every size, and the per-size permutation p-values are
  `0.39-0.77`, so no per-size effect is detectable; the marginally
  0-excluding slope is a drift of size-by-size deviations that are individually
  null. The geometry is also heterogeneous by construction: the frozen rule
  takes the largest divisor `d` of `p-1` with `d <= B`, which gave
  `d = 45, 12, 6, 45` at 2^14 and `d = 4, 42, 6, 107` at 2^18 — on the `d = 4`
  curve the base is a union of 59 tiny cosets, i.e. effectively a pseudorandom
  set. This is the frozen definition behaving as written, recorded rather than
  repaired.

The concentration statistic shows where the geometry-dependence actually lives:
ratios `1.0017` (high-bit), `1.0011` (small height), `0.9963` (coset) at 2^18
versus `0.1437` (mixed, primary typing), `6.67` (mixed, secondary typing),
`0.0018` (asymmetric), and `1224` for the exploratory exact H017 recomputation.

## 5. Growth arm

Slopes are OLS fits of the per-replicate ratio against `log2 N` over the 48
replicate points (3 sizes x 16), with percentile CIs from 2000 bootstrap
resamples drawn within each size (§3, §4 tables). Two summary observations:

* On the **primary metric** the only nonzero slopes belong to cells whose ratio
  is *below* 1 at every size; the slopes are positive because the deficits
  shrink, not because any advantage grows. No geometry has a ratio above 1 at
  any size, so no slope can be "in the alive direction".
* On the **secondary coverage metric** no geometry has both a per-size CI
  excluding 1 in the advantage direction and a positive slope excluding 0. The
  one geometry with a consistent advantage direction (`greedy_optimized`) has a
  significantly **negative** slope; the one geometry with a positive slope
  excluding 0 (`coset_union`) has no per-size effect at all.

## 6. Exploratory replication (outside the pre-registered family)

Exact recomputations of the two prior-cell geometries. These cannot satisfy the
frozen success criterion (frozen invalidation rule) and are reported separately.

| arm | metric | 2^14 | 2^16 | 2^18 |
|---|---|---|---|---|
| `qr_walk_H016` (same-family reconstruction, n = 12/16/16) | mean-yield ratio | `1.000000` | `1.000000` | `1.000000` |
| | coverage ratio | `0.99227` | `0.99186` | `0.99055` |
| | concentration ratio | `1.0256` | `1.0293` | `1.0347` |
| `small_multiples_H017` (exactly determined) | mean-yield ratio | `1.000000` | `1.000000` | `1.000000` |
| | coverage ratio | `0.01261` | `0.00510` | `0.00205` |
| | concentration ratio | `188.2` | `480.0` | `1223.7` |

Four of the 48 `qr_walk_H016` records are `infeasible`: on curve 1 at 2^14 the
deterministic r-adding walk entered a cycle after collecting 22 of the required
47 QR points, and because the walk is keyed to the curve seed (not the replicate
seed) all four replicate seeds fail identically. The recorded H016 file carries
an `attempts` field, which suggests the original harness retried on such a
failure; no retry-on-cycle mechanism was added here, because that would mean
altering an arm after seeing its outcome. The 2^14 row of the table below is
therefore the mean over 3 curves (12 records) instead of 4. This affects only
the exploratory section; no pre-registered cell is involved.

The exact recomputation reproduces both prior conclusions and sharpens them: the
QR base is indistinguishable from matched random in yield and carries a ~1%
coverage deficit; the small-multiples base has the *same* exact mean yield as a
random base of the same size and loses coverage by a factor of 79 (2^14) to 487
(2^18), a deficit that grows with `N`. Neither result contradicts
`experiments/EXP-FB-001/analysis.md` ("factor-base structure is not a scaling
lever"; yield tracks the combinatorial `|FB|^3/N`): the exact accounting shows
*why* yield tracks `|FB|^3/N` — it is forced to, exactly, for every base of that
size. EXP-FB-001 measured that at sampled resolution over `d in {6,...,12}` on
`p ~ 2^14`; this battery reproduces it as an identity at three sizes.

The symmetric-convention arm (`D u (-D)`) is reported in `conservation.md` §3.

## 7. Verdict against the frozen criteria

Quoted verbatim from `specification.yaml`.

> **success_criterion:** At least one geometry with Holm-adjusted yield ratio CI
> excluding 1 AND a growth slope vs log N excluding 0 in the alive direction
> across 2^14..2^18 (exponent-relevant; triggers a larger-N confirmation arm and
> feeds base selection for EXP-R6-001).

**Not met. 0 of 6 geometries.** Operationalisation, declared before execution:
"alive direction" means ratio > 1, an advantage over matched random, because the
hypothesis statement is about "a rate whose advantage over a matched random base
GROWS with N"; the Holm-adjusted CI is taken as the family-wise
`1 - 0.05/8` bootstrap CI. Per geometry: `high_bit_interval`, `small_height`,
`coset_union` — CI is exactly `[1,1]` and the slope is exactly 0;
`mixed_two_base`, `asymmetric_sizing`, `greedy_optimized` — CI excludes 1 and
the slope excludes 0, but the ratio is below 1 at every size, so the effect is a
deficit and the direction clause fails. Under the secondary coverage metric
(which the criterion does not name) no geometry satisfies both clauses either
(§4, §5).

> **falsification_criterion:** All geometries within CIs / permutation bands at
> every N, or every nonzero effect constant across N: scoped KILL of the F3
> family — "no signal seen at reachable scale," with the family-wise correction
> reported.

**The clauses of the falsification criterion are satisfied on the tested scope,
with one qualification the Coordinator should weigh.** Three of the six
geometries are inside their permutation bands at every `N` (in fact exactly at
the null value, provably). The other three have nonzero effects that are *not*
constant across `N` — but every one is a deficit whose magnitude is predicted in
closed form by the pre-registered analytic arm, and their `N`-dependence is the
integer arithmetic of matched sizing, not a mechanism. So the literal reading of
"every nonzero effect constant across N" is not met, while the substance — "no
signal seen at reachable scale" — is: **no geometry produced any advantage at
any size on the primary metric, and the one sub-1% advantage anywhere in the
battery (greedy held-out coverage) decays with `N`.** The family-wise correction
is reported in §3 and §4. The official transition is the Coordinator's; this is
the executor's observation.

Additional observation for the record (AGENTS rule 8): the primary metric is
*mathematically incapable* of showing a matched-size geometry effect, and this
was established before execution (`conservation.md`, pre-registered as AMD-3).
The battery's informative channel is therefore the count **distribution** —
coverage and concentration — where structure only ever cost coverage, except for
the two sub-1% cases in §4.

## 8. Claim boundaries

* **Curve family / field type:** generated prime-field curves `E/F_p` in short
  Weierstrass form, prime group order, 4 curves per size, 12 curves total. Curve
  parameters, seeds, and per-curve acceptance counts are in each run's
  `curves` block.
* **Bit sizes tested:** `N ~ 2^14, 2^16, 2^18` (`14 <= field_bits <= 18`).
  **Claim tier: `toy`** (`docs/claims-and-verification.md`: field size <= 32
  bits). Nothing here supports any statement about medium or cryptographic
  curves, and no crypto-scale extrapolation is made.
* **Convention:** `m = 3`, unsigned multisets of three factor-base points,
  targets uniform over the whole group, matched size `B = ceil((6N)^(1/3))`
  (`B = 46-47 / 74 / 117`). Other `m`, signed conventions, weighted counting, or
  restricted target sets are untested; the symmetric-convention arm shows the
  constant is convention-bound.
* **Measured quantity:** number of existing decompositions per target, and the
  induced coverage and concentration. **Not** the cost of finding a
  decomposition, not solving degree, not relation-collection throughput, not any
  end-to-end cost. A null result here closes the **yield channel** of the F3
  family on the tested scope; it says nothing about the solving channel.
* **Discrete logs known by construction**, used only to count. Two further
  consequences: the `greedy_optimized` base is *selected* using the full
  discrete-log table, so that construction is not available to an attacker at
  all — it measures what an oracle-aided base could achieve, which makes its
  sub-1% decaying coverage excess an upper bound of an unrealisable kind, not an
  attack step.
* **Known confounders / limitations:** the 4 replicate seeds do not resample the
  deterministic geometries (only the null estimate and the seeded arms vary), so
  the 16-replicate bootstrap is partly pseudo-replicated; a curve-cluster
  bootstrap over the 4 true independent instances is reported alongside every
  primary CI in `RUN-FB3-001-FAMILY`. The `coset_union` geometry degenerates on
  curves where `p-1` has no divisor near `B`. Prior cells enter the family as
  *sampled* statistics at 2^14 and 2^17 and are censored at 2^16 and 2^18.
* **Resource limits:** 175.4 s total run wall clock, 231 MB peak RSS, 5 runs,
  against a budget of 7200 s / 6 GB / 12 runs. No run was censored or truncated
  by a budget limit.
* **Negative-result phrasing** (`docs/evidence-and-reproducibility.md`): no
  improvement meeting the predefined threshold was observed over the tested
  instances, parameters, counting convention, and resource budget.
