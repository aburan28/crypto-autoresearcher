# TASK-20260823-827765 — high-ceiling low-content stratum: pre-filtered enumeration, rank search, and the owed null objects

- Experiment: **EXP-ECQ-0e0cbb** (pre-registered, frozen before this producer started)
- Hypothesis: **H-ECQ-0ed5c8** · Goal: GOAL-ECQ-002 · Batch: BATCH-8b08ef (batch 4 of a declared maximum of 4)
- Runs: `experiments/EXP-ECQ-0e0cbb/runs/RUN-ECQSTR-827765-{001,002,002S,003,004,005,006,007,008,009,010,011}`

## 0. The branch that fired

**BRANCH C.** Coverage of the target stratum is **138/146 = 0.9452**, coverage of the
BATCH-541940 unfinished set is **38/5549 = 0.0068**, and overall coverage is
**176/5695 = 0.0309**. Branch B requires coverage 1.00 of both; it is not available.
Branch A requires a certified rank-≥12 curve strictly below the benchmark read at run
time; the best certified rank-≥12 height reached was **118.22777364040874**, which is
**+38.8991** above that benchmark, so branch A did not fire either.

Under branch C **nothing here says the lever is closed, that the stratum is empty, or
that the construction cannot reach the benchmark.** The coverage fraction and the
population count *are* the result.

Branch C's own pre-declared informativeness test, computed rather than asserted:
34 measured fibres lie below the benchmark, **all of them below naive height 80** and
therefore *outside* every band of the pre-registered reference rate
(0.002 on [80,90), 0.006 on [90,100), 0.044 on [100,120)). Expected successes at
certified rank ≥ 12 over the searched sub-benchmark set is therefore **0.0000**,
observed is 0, and P(observing zero) ≈ 1.0000. The expected count is below 3 — indeed
below 1 — so the zero is, in the words the contract mandates,
**"consistent with the measured rate and not informative about it"**. It is not a
bounded negative and is not reported as one.

**NO CELL HAS BEEN TAKEN.** Not on any metric, at any rank threshold, in four batches.
`cell_taken` is false on every row of `best_candidates.json`. Rank ≥ 31 over Q remains
an open world record (30, Alpoge–Howell 2026) and nothing here is progress toward it.
Nothing was submitted to the ICARM endpoint and no network call was made.

## 1. The pre-filter went first, and it is sound

`RUN-ECQSTR-827765-003`. The squarefree-discriminant pre-filter was applied **before any
height evaluation, any Mestre–Nagao ordering and any rank search** — one squarefreeness
test on the degree-20 finite discriminant, `Res(DD, DD') ≠ 0`, decided as
`deg gcd(DD, DD') = 0`. The resultant was additionally formed explicitly on a sample in
`RUN-ECQSTR-827765-001` and agrees with the gcd predicate on every row.

| quantity | value |
| --- | --- |
| admissible families entering the filter | 16754 |
| retained | 106 |
| discarded | 16648 |
| measured cost | 16.2466 s total, **0.970 ms per tuple** |

**Soundness, proved and then checked.** `deg gcd(DD, DD')` equals
`Σ_finite deg(v)(N_v − 1)`; for a multiplicative fibre `m_v = N_v` so the term is exact,
and for every additive Kodaira type in characteristic 0 `m_v = N_v − 1` so the term
*overstates* the true reducible contribution. Additivity among the repeated fibres is
detected by one further gcd against `a4`; when it is present the family is **retained**
and marked undecidable-cheaply. The filter therefore cannot discard a ceiling-≥13 family
*by construction*. CTL-PREFILTER-SOUNDNESS then checked it empirically over the **whole**
enumeration rather than a sub-box: full fibre censuses were computed for all 16754
families, discarded ones included, giving **105 families of ceiling ≥ 13 and 0 false
negatives**, and the cheap ceiling agreed with the full census on **16753/16753** decided
families. The Euler check `Σ deg·v_disc = 24 = 12d` failed on **0 of 16754**.

**The filter is an efficiency heuristic and never an impossibility claim.** The
Shioda–Tate ceiling bounds the *generic* rank over Qbar(T); a specialisation over Q is at
least the generic rank and can exceed it (KN-FIND-6b3e17). No claim whatever is made that
a discarded family cannot host a rank-12 specialisation over Q.

## 2. The enumeration, and why the population count is a complete count

Box declared in code before any count was read:
**B1** exhaustive, every canonical primitive integer 6-tuple of spread 5 ≤ m ≤ 80 —
*enlarged beyond* the spread-≤74 census; **B2** sampled, spread uniform in [81, 3000],
3 000 000 tuples tested, `random.Random(20260823)`.

Accounting, with two assertions inside the run requiring that nothing is lost to a
difference between attempted and measured:

| bucket | count |
| --- | --- |
| tuples tested (B1 24 040 016 + B2 3 000 000) | 27 040 016 |
| rejected, not primitive | 832 573 |
| rejected, φ ≠ 0 (inadmissible) | 26 189 691 |
| rejected, duplicate canonical | 444 |
| **admissible canonical tuples** | **17 308** |
| of those: enumerated and censused | 16 754 |
| of those: degenerate (discriminant vanishes identically in T, not an elliptic surface) | 554 |
| of those: refused for `deg_x r ≠ 4`, or attempted-not-measured | 0 |

### LEMMA L1 — the target stratum is enumerated completely, not sampled

For six reals, `P2 = Σ_i (a_i − ā)² = (1/6) Σ_{i<j} (a_i − a_j)² ≥ m²/6` with `m` the
spread, by keeping only the pair realising the spread. Hence
`log P2 < 6 ⟹ m² < 6e⁶ = 2420.57… ⟹ m ≤ 49`. B1 runs to spread 80, so **B1 contains every
admissible canonical integer 6-tuple with log P2 < 6, over all of Z⁶ up to the
construction's exact translation, scaling and reflection symmetries.** The identity and
the bound were checked numerically on 2000 random tuples (max identity error 0, zero
violations), and the largest spread actually observed with log P2 < 6 was **28**, well
inside the bound.

### THE POPULATION COUNT, AND THE PRE-REGISTERED PREDICTION IT FALSIFIES

> **Families with Shioda–Tate ceiling ≥ 13 and log P2 < 6: 2.**
> `[0, 2, 8, 9, 11, 14]` (ceiling 13, log P2 4.9652, spread 14) and
> `[0, 6, 12, 14, 15, 23]` (ceiling 13, log P2 5.7473, spread 23).

The pre-registered prediction was **≥ 200**. H-ECQ-0ed5c8's own falsification clause
therefore fires: *"THE POPULATION CLAIM IS FALSIFIED if the enlarged, pre-filtered box
yields fewer than 200 families of ceiling ≥ 13 at log P2 < 6."*

By Lemma L1 this is stronger than a box result. **Enlarging the spread box cannot
populate the stratum, because low content bounds the spread.** The 2 families are not
2-in-this-box; they are 2 in all of Z⁶ up to the construction's symmetries. The untested
region is untestable by this enumeration — which is itself a measured statement about the
construction and is reported as one, exactly as the falsification clause requires. The
thresholds were **not** changed after the count came in: ceiling ≥ 13 and log P2 < 6 stand
as frozen, no `protocol_amendment` was made, and none is claimed.

Ceilings over the enumeration, each computed from the family's own fibre configuration and
never from the generic K3 bound: 9 → 16 607, 13 → 91, 11 → 6, 5 → 20, 7 → 16, 15 → 14.
Ceiling ≥ 13 at any content: 105. Families with log P2 < 6 at any ceiling: 309. The
steerable quantity is recorded per family as the number of **reducible finite fibres**;
`fibre_type_at_infinity` is read from the place at infinity's own valuations and reported
as the near-constant it is, never as a stratifying column. BATCH-541940's section-3 column
is not reproduced.

## 3. The rank search

Full 73-value T-box, **no height cap and no family cap**. PARI `ellrank` was used only as
a **point search**; every reported rank is a certified lower bound re-derived by
`exact_certify.py` from the exhibited points in integer/Fraction arithmetic, with no
floating point in any certification. `pari_ellrank_r_low`, `r_high` and the alarm status
are carried into every ICARM-format row. Rank equality is never claimed.

**Alarm discipline.** The alarm was 20 s throughout — the same instrument and the same
alarm as BATCH-541940, under which the pre-registered reference rate was measured. Per the
contract, **an alarmed fibre counts as attempted-not-measured in the coverage denominator,
never as a searched fibre that found nothing.**

| set | coverage | by ceiling class |
| --- | --- | --- |
| **A — target stratum** (2 families × 73 t) | **138/146 = 0.9452** | ceiling 13: 138/146 = 0.9452 |
| **B — BATCH-541940 unfinished** | **38/5549 = 0.0068** | ceiling 13: 0/4670 = 0.0000 · ceiling 15: 38/879 = 0.0432 |
| overall | **176/5695 = 0.0309** | |

SET A's first pass (`RUN-…-004`) reached 136/146 with 10 PARI alarms; `RUN-…-005`
re-attempted those 10 at a 90 s alarm and recovered 2 more before its own wall clock
stopped it at 6 of 10 retries. The 8 that remain are all large-|t| fibres.
**This is an infrastructure outcome. It bounds coverage and is not negative mathematical
evidence.**

SET B was stopped by wall clock after 53 of 5549 pairs at roughly 9.6 s per pair, with 15
alarms; the residual is dominated by exactly the large-|t| fibres that alarm, which is why
it was unsearched in the first place.

### The "2114" figure, disclosed rather than assumed

DEC-20260823-ee9162 R4(f) records a reviewer's reconstruction of **46 load-bearing
families with 2114 unsearched fibres at 37.0 percent coverage**. *That exact partition
could not be reproduced from the committed BATCH-541940 artifacts by this producer.* What
the committed run records show is **61** distinct ceiling-≥12 families carrying **1459**
searched (family, t) pairs, against **96** ceiling-≥12 families in the census. Rather than
guess which 46 were meant, SET B was taken as the reproducible **superset** — all 96
census families of ceiling ≥ 12 over the full 73-value T-box, minus everything already
searched, giving a denominator of **5549** that contains any 46-family/2114-pair set
whatever its membership. The discrepancy is reported, not resolved by assumption; a
reviewer who can pin the 46 down can recompute the sub-coverage from
`rank_search_coverage.json` directly, since every attempted pair is persisted there with a
status and a reason.

### Certified rank against height

Best certified rank over SET A (the target stratum, at 138/146 coverage) is **11**, at
naive height 77.85764339540441 — below the benchmark, but at rank 11, not 12, and above
the frozen r ≥ 11 frontier value read at run time by +16.350793. **No certified rank-12
fibre was found anywhere in the target stratum.** Given the coverage fraction and the
expected-count arithmetic of §0, that zero is consistent with the measured rate and not
informative about it.

The only certified rank-≥12 fibres this task measured (4 of them) came from SET B, and the
best is at naive height **118.22777364040874**, on **Mestre's own published tuple A**
`(-17,-16,10,11,14,17)` at t = 23 — *not* a tuple this program found. It sits +48.888932
above the frozen r ≥ 12 frontier value read at run time and +38.899099 above the
construction-class benchmark, and it is worse than the campaign's standing best at
certified rank ≥ 12 (86.77369390941135) by +31.454080. **This is a shortfall and is
reported as one, with its exact gaps and no rounding in either direction.**

## 4. Provenance — both keys, plus Cremona

Every reported curve was checked against the frozen snapshot **by `curve_key` and,
independently, by a-invariants**, and against Cremona's tables. Heights were recomputed
from a-invariants alone (absolute difference 0.0 on every reported row) and global
minimality was settled per row.

**Cremona.** No Cremona check has ever been run in this campaign. PARI's `elldata` package
is not installed in this environment (`ellsearch` and `ellidentify` both fail with *error
opening elldata file*) and no network call is permitted, so a lookup is impossible. What
is possible offline and decisive in one direction is a **conductor bound**: Cremona's
tables enumerate curves of conductor below 500000, so a curve of larger conductor is
provably absent from them. Every reported curve clears that bound by many orders of
magnitude — the rank-12 row has conductor 40503175421600611274191237770937333995 — and
each row records the bound used so the claim is auditable rather than taken. A curve
*inside* the range would have been marked `INCONCLUSIVE_LOOKUP_REQUIRED` and would not
have been reported as novel.

**A frozen board curve was rediscovered, and it is a positive control, not a result.**
Board curve **id 162** (naive height 74.31951471015851) was matched **on both keys** by
target-stratum family `MESTRE-0,6,12,14,15,23` at t = 1. That is priority item (7), and it
is **a strong external positive control on this pipeline — never this program's own
curve.** It is not a Pareto minimum at any rank threshold and appears nowhere in this
report as a best candidate. Board curve id 108 was **not** among this task's measured
fibres.

## 5. The owed null objects

### RT-CONTROL-2 — a rung that actually has no rational sections (`RUN-…-007`)

φ = 0 is a relation among `p_1..p_5` of the roots of q, and for a monic degree-6 q those
depend on the coefficients of x⁵ down to x¹ only — **not** on the constant term. So
changing only the constant term of a treatment family's own q preserves admissibility
*exactly* and preserves the content statistic P2 *exactly*. The rung is that q with one
integer changed, chosen so that q becomes irreducible over Q with Galois group S₆.

Verified, not assumed: `polisirreducible` and `polgalois` were computed per rung (S₆ on
all 13), `n_rational_sections = 0` per rung, φ = 0 and `deg_x r = 4` re-checked
symbolically, and P2 exactly equal to the treatment's. Irreducibility over Q is itself the
proof that **no section pair has a rational trace P + P^σ**: a Galois-stable 2-subset of
the roots would give a rational quadratic factor of q. S₆ in its natural degree-6 action
preserves no partition at all, which is the maximal form of this.

**The 12-sections-against-0 contrast, run for the first time, at exact content matching:**

| | certified rank at the envelope argmin |
| --- | --- |
| rung, 0 rational sections, S₆ (13 generated, 13 measured) | 0 ×12, 1 ×1 |
| treatment, 12 rational sections, identical P2 (13) | 6 ×1, 7 ×2, 8 ×4, 9 ×4, 10 ×1, 11 ×1 |

Rung envelope minima ran 104.783–162.379 against the treatments' 51.070–109.704. Both
figures are from 13 matched pairs and no row was dropped (generated 13, measured 13, 0
refused). RT-CONTROL-2 was stopped by its own time box after 13 rungs of the 106 retained
families, so the contrast is measured on 13 matched pairs and is reported as such.

### The k = 0 proves-too-much object (`RUN-…-009`)

PASS was stated in advance as *"it must NOT come out rank 0."* A k = 0 rung
(q = three irreducible quadratics; 0 rational sections but every conjugate pair
Galois-stable) built from `[0,5,13,27,35,40]` returned **certified rank 5** at its
envelope argmin, envelope minimum 100.987. **PASS.** Any "no rational sections implies no
rational rank" argument fails on it, as it must. 1 of 106 candidates survived the guards
(31 refused for the |a−b| = 2 guard, the remainder for `deg_x r ≠ 4` or measurement
failure); the attrition is disclosed in the deliverable.
`RUN-…-007` reported this control **NOT_RUN** because its candidate loop drew from only
six shuffled tuples and every one failed the guard. That run record stands as written;
`RUN-…-009` supplies the control it missed. **The trace map P + P^σ was not constructed in
either run** — certified rational points of infinite order are exhibited, and their
provenance as such traces is not established here and is not asserted.

### RT-CONTROL-3 — random-curve rank null, and it is mostly a BOUND

Target n = 200 per band, same instrument, same 20 s alarm, ranks certified in exact
arithmetic.

| band | reached | certified rank distribution | status |
| --- | --- | --- | --- |
| h ≈ 60 | 200/200 | 0:162, 1:26, 2:10, 3:2 | a distribution |
| h ≈ 70 | 108/200 | 0:97, 1:8, 2:3 | **a bound, not a distribution** |
| h ≈ 80 | 38/200 | 0:37, 1:1 | **a bound** |
| h ≈ 93 | 12/200 | 0:12 | **a bound** |
| h ≈ 100 | 7/200 | 0:7 | **a bound** |

Only the h ≈ 60 band reached n = 200. The four heavier bands are reported as bounds and
must not be read as distributions.

Read together: the S₆ rung's rank distribution (12 of 13 at rank 0) sits with the
random-curve null, and apart from the 12-section treatment at identical content. That is
the contrast the control exists to supply, and it is the first time this campaign has had
it.

## 6. The intercept replication (`RUN-…-010`)

| pass | n | slope | R² | verdict |
| --- | --- | --- | --- | --- |
| reported, under replication | 13391 | 0.8132 | 0.7732 | — |
| **PASS 1** intercepts reused, regression independent (exact rational normal equations; no numpy, no `measure.fit`) | 13391 | **0.813189** | **0.773244** | **REPLICATES** |
| **PASS 2** re-derived from the tuple alone: envelope, breakpoint search, both arm fits and regression all written independently | 200 | 0.847197 | 0.765732 | **REPLICATES** (a sample, not the full population) |

PASS 2's re-derived envelope minima agreed with the census to **absolute difference 0** on
all 200 families, with 0 refused. The comparison the contract asks be kept beside it —
envelope on log content P2 — returns slope 14.688963, R² **0.191652**, reproducing the
0.19165243721035774 figure. The mechanism clause is **not** falsified: R² is 0.773244
against a declared withdrawal threshold of 0.7232.

`RUN-…-008` was the first attempt and **failed**: its "exact" least squares coerced floats
through `limit_denominator(10**12)`, so summing 13391 fractions made the running
denominator the lcm of thousands of unrelated 12-digit integers and it never terminated
inside its budget. It is recorded as an `implementation_error` — the machine was adequate,
the algorithm was wrong — it produced no deliverable, nothing from it is reported
anywhere, and `RUN-…-010` supersedes it.

## 7. What was not reached, and why

- **Full coverage of the target stratum**: 8 of 146 fibres remain attempted-not-measured,
  all at large |t|, from PARI alarms at 20 s and then at 90 s, plus the retry run's own
  wall-clock stop at 6 of 10.
- **The BATCH-541940 unfinished set**: 5511 of 5549 pairs remain attempted-not-measured
  after the 480 s box. Every one is persisted with a status and a reason.
- **RT-CONTROL-3 at n = 200**: reached on one band of five.
- **RT-CONTROL-2 across all 106 retained families**: 13 matched pairs measured.
- **The trace map P + P^σ**: not constructed, on either rung.
- **A Cremona lookup**: impossible offline; replaced by a conductor bound that is decisive
  only in the absent direction, and labelled as such.

All of these are infrastructure or scope outcomes. **None is negative mathematical
evidence** (AGENTS.md rule 5).

## 8. Scope

Everything above is scoped to: Mestre's rank-12 quartic construction; admissible canonical
integer 6-tuples over the declared box; the fixed 73-value T-box with |t| ≤ 800; the ICARM
naive-height convention; rank as a **certified lower bound** from exhibited points;
PARI 2.15.4 / cypari 2.5.6 / Python 3.11.15 on one 4-core machine; and the frozen ICARM
snapshot of 2026-08-23T00:43Z (sha256 118db069…cadc59, 289 curves, sha verified at run
time). Nothing is quantified over all tuples, all spreads or all rational t. Nothing
transfers outside this construction. No ECDLP claim, no speedup claim and no
asymptotic-complexity claim is made or implied.

Stated once more because it is the sentence most likely to be misquoted: under branch C,
**the lever is not closed, the stratum is not empty, and nothing here shows the
construction cannot reach the benchmark.**
