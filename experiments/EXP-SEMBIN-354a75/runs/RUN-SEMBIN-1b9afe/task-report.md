# Executor task report — TASK-20260913-4df669

| | |
|---|---|
| Experiment | EXP-SEMBIN-354a75 (frozen, `approved`, `approved_by: DEC-20260913-ebd639`) |
| Execution authorized by | DEC-20260913-1a9c83 |
| Hypothesis | H-SEMBIN-c5b2e0 |
| Run | RUN-SEMBIN-1b9afe |
| Role | executor — observations only |
| Validity | `completed_valid` |
| Wall clock | 827.3 s of a 3600 s budget |
| Peak RSS | 0.50 GB in-process high-water; 1.04 GB as the `RUSAGE_CHILDREN` upper bound. Budget 4 GB, self-imposed ceiling 3 GB |
| Cores | 1 of the ~2 requested |
| Configurations | 180 of a 200-run cap |

This report records observations. It states no conclusion about any curve, writes
no evidence record, moves no hypothesis status, and declares no heuristic
validated or refuted. The frozen prediction was scored exactly as written before
any diagnostic decomposition was formed, and the two are kept in separate
sections below so that the diagnosis cannot be mistaken for a re-scoring.

---

## 1. What ran, and what the contract's stopping rules did

All nine declared cells ran **exhaustively**. **No cell is UNREACHED**, and no
sampling was substituted for enumeration inside any cell. The enumeration
domain size `|V|^t` for each cell is recorded below for completeness even
though none hit a cap.

| cell | tk−n | \|V\| | \|V\|^t (enumeration domain) | point multisets C(L+t−1,t) | reached |
|---|---|---|---|---|---|
| n13 m4 t4 k4 | +3 | 16 | 65 536 | 7 315 | exhaustively |
| n15 m5 t3 k3 | −6 | 8 | 512 | 10 | exhaustively |
| n17 m3 t3 k6 | +1 | 64 | 262 144 | 47 905 | exhaustively |
| n19 m3 t3 k7 | +2 | 128 | 2 097 152 | 457 310 | exhaustively |
| n21 m3 t3 k7 | 0 | 128 | 2 097 152 | 457 310 | exhaustively |
| n12 m6 t6 k2 | 0 | 4 | 4 096 | 210 | exhaustively |
| n20 m2 t2 k10 | 0 | 1 024 | 1 048 576 | 477 753 | exhaustively |
| n22 m2 t2 k11 | 0 | 2 048 | 4 194 304 | 2 104 326 | exhaustively |
| n24 m2 t2 k12 | 0 | 4 096 | 16 777 216 | 8 191 128 | exhaustively |

Nine cells × 2 subspace variants × 2 curve-coefficient modes × 5 seeds = 180
configurations, 2000 target draws per configuration per target population, plus
a sampling-free exact pass over the **whole** target population in every cell
and a per-R exhaustive pass over the whole population in the four cells where
that fits.

`L` is the number of F_q-rational factor-base points, i.e. points of E(F_q)
whose x-coordinate lies in V. It is **not** `|V|`, and that distinction turns
out to carry most of this run's arithmetic.

### The one stopping rule that fired

**A measured ratio above 1 halts for diagnosis and is never reported as a
finding.** This rule **FIRED**. Six of nine cells returned a Semaev-variant
ratio whose 95% interval lies strictly above 1, and two of them (n17, n21) stay
above 1 under the exact-multiset class count too. The run was halted and
diagnosed before any claim was formed; the diagnosis is section 8 and
`ratio-above-1-diagnosis.txt`. **No ratio above 1 is reported as a finding
anywhere in this package.**

The other four rules did not fire:

- **eq. (11) reproduces the published decimals.** Checked against **all 33**
  `P_theoretical` entries of the frozen transcription of Tables 1–2, not only
  the four cells in this window. All 33 match to four decimals; maximum
  absolute error 9.871e−05. Only 10 of 33 match under *rounding*, which
  identifies the paper's convention as **truncation**. No procedure defect.
- **Matched null does not return below 1.** 45 realizations, all 45 intervals
  contain 1. Detail in section 7.
- **Known-false class count shifts by t!.** Exactly, in λ. Detail in section 7.
- **No cell hit its cap; no cell outside tk−n ∈ [−6,+6] was added.**

---

## 2. Measured ratio, 95% interval, per cell, per presentation, per class-count variant

Ratio = (measured fraction of targets with at least one decomposition) ÷
(eq. (11)'s `1 − exp(−λ)`), pooled over the 20 configurations of each cell,
40 000 target draws per cell per population. Intervals are Wilson score
intervals propagated through the ratio.

### Target population E — R uniform on affine E(F_q), the algorithm's own targets

**single presentation** (eq. (4), one summation polynomial) — and **chained**
(eq. (5), the S_3 chain) is *identical to it at four decimals in every cell*,
because on the E side no target that has a single-presentation solution lacks a
chained one. The two presentations differ in the *count* on 648 targets
(section 6), never in whether the count is zero. **usable** (F_q-rational
solutions only) is likewise identical at the hit-fraction level.

| cell | tk−n | semaev \|V\|^t/t! | exact C(\|V\|+t−1,t) | known-false \|V\|^t |
|---|---|---|---|---|
| n13 m4 t4 k4 | +3 | 1.0252 [1.0096, 1.0410] | 0.7710 [0.7592, 0.7828] | 0.2907 [0.2863, 0.2952] |
| n15 m5 t3 k3 | −6 | 1.2400 [1.0439, 1.4728] | 0.8823 [0.7428, 1.0479] | 0.2080 [0.1751, 0.2471] |
| n17 m3 t3 k6 | +1 | 1.1390 [1.1229, 1.1552] | 1.0956 [1.0801, 1.1112] | 0.3734 [0.3681, 0.3787] |
| n19 m3 t3 k7 | +2 | 1.0181 [1.0080, 1.0281] | 1.0016 [0.9917, 1.0115] | 0.5046 [0.4996, 0.5096] |
| n21 m3 t3 k7 | 0 | 1.1958 [1.1713, 1.2207] | 1.1705 [1.1465, 1.1949] | 0.2904 [0.2845, 0.2965] |
| n12 m6 t6 k2 | 0 | 9.9789 [9.1867, 10.8384] | 0.6823 [0.6281, 0.7411] | 0.0219 [0.0202, 0.0238] |
| n20 m2 t2 k10 | 0 | **0.9024 [0.8905, 0.9144]** | 0.9017 [0.8899, 0.9137] | 0.5617 [0.5543, 0.5692] |
| n22 m2 t2 k11 | 0 | **0.9069 [0.8950, 0.9188]** | 0.9065 [0.8946, 0.9185] | 0.5645 [0.5571, 0.5719] |
| n24 m2 t2 k12 | 0 | **0.9073 [0.8954, 0.9193]** | 0.9071 [0.8952, 0.9191] | 0.5648 [0.5574, 0.5722] |

The three bolded rows are the cells where eq. (11)'s own class-count
approximation is numerically negligible (the exact and Semaev columns agree to
three decimals, because `C(|V|+t−1,t)/(|V|^t/t!)` is 1.0010, 1.0005 and 1.0002
there). They are the only cells whose ratio is not confounded by the
approximation, and all three fall **below** 1 with intervals excluding 1, at
0.902–0.907 across three field sizes.

### Target population T — R_X uniform over the F_q values carrying no rational point

The other half of eq. (11)'s own "random z in F_q" population, represented on
the quadratic twist.

| cell | tk−n | single, semaev | chained, semaev | **usable**, semaev |
|---|---|---|---|---|
| n13 m4 t4 k4 | +3 | 1.1458 [1.1297, 1.1621] | 1.1458 [1.1297, 1.1621] | **0.0000 [0.0000, 0.0003]** |
| n15 m5 t3 k3 | −6 | 1.9129 [1.6654, 2.1969] | 1.9129 [1.6654, 2.1969] | **0.0000 [0.0000, 0.0369]** |
| n17 m3 t3 k6 | +1 | 0.9105 [0.8955, 0.9257] | 0.9105 [0.8955, 0.9257] | **0.0000 [0.0000, 0.0003]** |
| n19 m3 t3 k7 | +2 | 0.9760 [0.9660, 0.9861] | 0.9760 [0.9660, 0.9861] | **0.0000 [0.0000, 0.0002]** |
| n21 m3 t3 k7 | 0 | 0.8341 [0.8130, 0.8557] | 0.8341 [0.8130, 0.8557] | **0.0000 [0.0000, 0.0006]** |
| n12 m6 t6 k2 | 0 | 8.4374 [7.6929, 9.2531] | 8.4374 [7.6929, 9.2531] | **0.0000 [0.0000, 0.0728]** |
| n20 m2 t2 k10 | 0 | 0.9053 [0.8935, 0.9173] | 0.9053 [0.8935, 0.9173] | **0.0000 [0.0000, 0.0002]** |
| n22 m2 t2 k11 | 0 | 0.9080 [0.8961, 0.9200] | 0.9080 [0.8961, 0.9200] | **0.0000 [0.0000, 0.0002]** |
| n24 m2 t2 k12 | 0 | 0.8986 [0.8867, 0.9106] | 0.8986 [0.8867, 0.9106] | **0.0000 [0.0000, 0.0002]** |

The usable column is **exactly zero in every cell, over 180 000 T-side draws**,
and that is structural rather than statistical: a target whose x-coordinate
carries no rational y is not a point of E(F_q), so it cannot be a sum of
rational factor-base points at any t. The single and chained columns are not
zero because the algebraic system does not know about y-rationality. Recorded
because it is the sharpest available statement of the gap between "the
summation system has a solution" and "there is a usable relation": on half of
eq. (11)'s own target population the gap is total.

---

## 3. Zero-decomposition fraction per cell, reported separately from the mean

The contract requires these separately because eq. (11) is a statement about
the zero fraction and a ratio built from means can agree while it disagrees.
E side, pooled, 40 000 draws per cell.

| cell | zero fraction, single | zero, chained | zero, usable | eq. (11)'s 1−P | **mean count, single** | mean, chained | mean, usable |
|---|---|---|---|---|---|---|---|
| n13 m4 t4 k4 | 0.70937 | 0.70937 | 0.70937 | 0.71653 | 0.5825 | 0.4887 | 0.4811 |
| n15 m5 t3 k3 | 0.99677 | 0.99677 | 0.99677 | 0.99740 | 0.0032 | 0.0032 | 0.0032 |
| n17 m3 t3 k6 | 0.67712 | 0.67712 | 0.67712 | 0.71653 | 0.3908 | 0.3908 | 0.3910 |
| n19 m3 t3 k7 | 0.50462 | 0.50462 | 0.50462 | 0.51342 | 0.7016 | 0.7016 | 0.7017 |
| n21 m3 t3 k7 | 0.81642 | 0.81642 | 0.81642 | 0.84648 | 0.2044 | 0.2044 | 0.2044 |
| n12 m6 t6 k2 | 0.98615 | 0.98615 | 0.98615 | 0.99861 | 0.0450 | 0.0387 | 0.0360 |
| n20 m2 t2 k10 | 0.64492 | 0.64492 | 0.64492 | 0.60653 | 0.4953 | 0.4953 | 0.4953 |
| n22 m2 t2 k11 | 0.64318 | 0.64318 | 0.64318 | 0.60653 | 0.5035 | 0.5035 | 0.5035 |
| n24 m2 t2 k12 | 0.64300 | 0.64300 | 0.64300 | 0.60653 | 0.5034 | 0.5034 | 0.5034 |

Two things the contract anticipated are visible here.

First, the zero fraction is **identical across all three presentations in every
cell**, to five decimals, while the means differ (n13: 0.5825 / 0.4887 /
0.4811). A ratio built from means would have reported a presentation effect of
17% at n13 where the directly comparable quantity shows none.

Second, at the three t = 2 cells the realized zero fraction (0.6430–0.6449)
**exceeds** eq. (11)'s 1−P (0.6065) while the realized mean (0.4953–0.5035)
is essentially eq. (11)'s λ = 0.5. The mean is right and the zero fraction is
wrong. That is a statement about the shape of the count distribution, not its
scale, and section 5 measures it.

---

## 4. F_{q^2} \ F_q solutions, and the Lemma 2 side condition

Solutions whose y_i lie in F_{q^2} but not F_q are counted by the algebraic
system and are **not** usable relations. They are counted and reported
separately here and retained per R in `per-R-counts.json`; no count in this run
silently includes or silently excludes them.

E side, pooled over 40 000 draws per cell:

| cell | non-rational solutions, total | targets with ≥1 | share of all counted solutions | Lemma 2 side condition FAILURE fraction | 95% interval |
|---|---|---|---|---|---|
| n13 m4 t4 k4 | 4 279 | 585 | 0.18191 | 0.089950 | [0.087185, 0.092793] |
| n15 m5 t3 k3 | 0 | 0 | 0.00000 | 0.000725 | [0.000505, 0.001041] |
| n17 m3 t3 k6 | 0 | 0 | 0.00000 | 0.017625 | [0.016381, 0.018962] |
| n19 m3 t3 k7 | 0 | 0 | 0.00000 | 0.015825 | [0.014648, 0.017095] |
| n21 m3 t3 k7 | 0 | 0 | 0.00000 | 0.004600 | [0.003983, 0.005312] |
| n12 m6 t6 k2 | 472 | 204 | 0.24712 | 0.015700 | [0.014527, 0.016966] |
| n20 m2 t2 k10 | 0 | 0 | 0.00000 | 0.000000 | [0.000000, 0.000096] |
| n22 m2 t2 k11 | 0 | 0 | 0.00000 | 0.000000 | [0.000000, 0.000096] |
| n24 m2 t2 k12 | 0 | 0 | 0.00000 | 0.000000 | [0.000000, 0.000096] |

**Side-condition outcome.** The Lemma 2 side condition — that the lower systems
`S_{i+1} = 0` for 2 ≤ i < t are unsatisfiable — is evaluated per target and
retained per target. It **fails** on 0.00% to 9.00% of targets depending on
cell, and where it **holds**, Lemma 2's conclusions hold without a single
exception across the whole run: the chained and single counts agree, and the
sum of the non-rational points is the point at infinity or the unique affine
2-torsion point. This was additionally verified against brute-force enumeration
in F_{q^2} at eight small parameter sets in `selftest_yield_core.py`, where the
same check also establishes that **s = 1 never occurs** — a single non-rational
point in a solution is structurally impossible in this construction, so the
non-rational solutions always come in the s ≥ 2 configurations Lemma 2
describes.

**The non-rational share is the quantity under measurement, and it is large
where it is nonzero.** At n13 (t = 4), 18.19% of everything the algebraic
system counts is not a usable relation; at n12 (t = 6), 24.71%. At t = 2 and
t = 3 it is exactly zero for the tested curves and subspaces. A count that had
silently included these would have overstated usable yield at n13 by 22%.

---

## 5. Poisson fit, goodness of fit, and the fitted c(t)

### Fit of the per-R counts (E side, usable presentation, pooled 40 000 draws)

| cell | fitted λ | χ² | dof | p | bins | largest observed count | P(that count or more, under the fit) |
|---|---|---|---|---|---|---|---|
| n13 m4 t4 k4 | 0.4811 | 60 110.2 | 4 | 0 | 6 | 20 | 0 |
| n15 m5 t3 k3 | 0.00323 | — no degrees of freedom | — | — | — | 1 | 1.000 |
| n17 m3 t3 k6 | 0.39085 | 5.912 | 3 | 0.116 | 5 | 5 | 0.889 |
| n19 m3 t3 k7 | 0.70165 | 45.985 | 4 | 2.48e−09 | 6 | 6 | 0.974 |
| n21 m3 t3 k7 | 0.20440 | 5.517 | 2 | 0.063 | 4 | 4 | 0.916 |
| n12 m6 t6 k2 | 0.04505 | 2 357.3 | 1 | 0 | 3 | 10 | 0 |
| n20 m2 t2 k10 | 0.49525 | 1 005.6 | 4 | 2.23e−216 | 6 | 6 | 0.416 |
| n22 m2 t2 k11 | 0.50350 | 1 253.9 | 4 | 3.35e−270 | 6 | 7 | 0.041 |
| n24 m2 t2 k12 | 0.50340 | 1 318.9 | 4 | 2.65e−284 | 6 | 7 | 0.041 |

The fit is rejected at 7 of 9 cells, marginally passed at n17 (p = 0.116) and
n21 (p = 0.063), and undefined at n15 where the mean is 0.003. The direction of
failure is the same everywhere: **excess zeros and a heavy upper tail**. At n13
the fitted Poisson expects 5.77 targets in the "≥ 5" bin and observes 586, and
the largest observed count of 20 has probability 0 under the fit — so both the
bulk and the tail reject, which under tail check 1's own reading points at the
law rather than at a constant.

**The control that makes this interpretable:** the matched null's own realized
counts, pushed through the identical fitting code, **pass** the same test in
every cell — p = 0.962, 0.613, 0.626, 0.679, 0.424, 0.656, 0.216 at the cells
where the fit is defined. The Poisson failure is therefore a property of the
realized curve-and-summation-polynomial counts, not of the counting pipeline or
the statistics code. Whether HEUR-003's Poisson clause survives that is a
reviewer's judgement; this run records the observation and the control.

### Fitted c(t)

HEUR-003 is internally ambiguous here and the ambiguity is **recorded, not
resolved**: its formula names mean `2^{tk−n}·c(t)`, which is the mean of the
**ordered** count, while its calibration clause "c(t) = 1 when eq. (11) is
exact" is true of the **class** count against `2^{tk−n}/t!`. c(t) is therefore
reported once per granularity, each against its own matching model mean. Both
are 1 exactly when eq. (11) is exact. The heuristic and the frozen prediction
were not altered.

| cell | t | c(t), class granularity (usable) | c(t), ordered granularity (single) |
|---|---|---|---|
| n13 m4 t4 k4 | 4 | 1.4433 [1.4064, 1.4802] | 1.0266 [0.9984, 1.0548] |
| n15 m5 t3 k3 | 3 | 1.2384 [1.0250, 1.4518] | 0.8976 [0.7323, 1.0629] |
| n17 m3 t3 k6 | 3 | 1.1729 [1.1544, 1.1914] | 1.1198 [1.1019, 1.1376] |
| n19 m3 t3 k7 | 3 | 1.0526 [1.0400, 1.0652] | 1.0279 [1.0155, 1.0403] |
| n21 m3 t3 k7 | 3 | 1.2266 [1.1998, 1.2533] | 1.1988 [1.1726, 1.2251] |
| n12 m6 t6 k2 | 6 | 25.8840 [23.0962, 28.6718] | 2.1164 [1.8560, 2.3767] |
| n20 m2 t2 k10 | 2 | 0.9905 [0.9753, 1.0057] | 0.9896 [0.9743, 1.0048] |
| n22 m2 t2 k11 | 2 | 1.0070 [0.9914, 1.0226] | 1.0064 [0.9908, 1.0219] |
| n24 m2 t2 k12 | 2 | 1.0068 [0.9912, 1.0224] | 1.0066 [0.9910, 1.0221] |

c(t) is at or just above 1 at t = 2, and **rises** with t at both
granularities. It is not below 1 and not decreasing in t.

---

## 6. The four tail checks

**Tail check 1 — largest observed count against its extreme-value probability
under the fitted Poisson.** Reported in the fit table above, rightmost column.
At n13 and n12 the maximum observed count (20 and 10) has probability 0 under
the fitted law even allowing for 40 000 draws. At n22 and n24 the maximum of 7
sits at p = 0.041. At n17, n19, n21 and n20 the tail is unremarkable
(p = 0.42–0.97), and at n17/n21 the bulk fit also passes — those two cells are
the only ones where the Poisson description survives both checks.

**Tail check 2 — zero fraction separately from the mean.** Section 3. The
load-bearing observation is at the three t = 2 cells, where the realized mean
matches λ = 0.5 within 1% while the realized zero fraction exceeds `exp(−λ)`
by 3.6–3.8 percentage points.

**Tail check 3 — per-R chained-minus-single differences individually, not their
mean.** E side, all cells, 360 000 target draws:

| cell | targets where they differ | ...and the side condition HELD | ...and it FAILED | difference histogram |
|---|---|---|---|---|
| n13 m4 t4 k4 | 519 | **0** | 519 | −6: 235, −8: 143, −7: 59, −9: 50, −10: 21, −11: 9, −12: 2 |
| n12 m6 t6 k2 | 129 | **0** | 129 | −1: 67, −3: 46, −2: 11, −5 and below: 5 |
| all other 7 cells | 0 | 0 | 0 | 0: all draws |

648 differing targets in total. In **every one of the 648** the Lemma 2 side
condition had failed, and in **zero** of them had it held. Every difference is
**negative**: the chain loses solutions relative to the single polynomial and
never gains any, with per-target deficits from 1 to 12. The mean difference is
small and a mean would have hidden the structure entirely — which is the
scenario the contract wrote this check for. Recorded as an observation about
where the two presentations diverge; no verdict on HEUR-004 is drawn here,
though the observation matches its stated form (agreement except on the
measured side-condition failure set) without exception.

**Tail check 4 — the m = t = 2 cells against H-RELN-96e3ba's 2^m-type
discrepancy, stated either way.** H-RELN-96e3ba's mechanism locates a factor
`2^m` in the ratio between an exact mean and the reference exponent
`B^m/(m!·p)`, and attributes it to the factor base being declared as B on-curve
x-coordinates while the search ranges over the `|W| = 2B` points those
x-coordinates lift to. The measurable form of that mechanism is the ratio
between the number of factor-base **points** searched and the `|V|` that eq.
(11) charges, raised to the m-th power. Measured at the m = t = 2 cells, 20
configurations each:

| cell | \|V\| | L over 20 configs (min / max / mean) | L/\|V\| mean | (L/\|V\|)^m | 2^m |
|---|---|---|---|---|---|
| n20 m2 t2 k10 | 1 024 | 977 / 1 087 / 1 017.8 | 0.9939 | 0.9879 | 4 |
| n22 m2 t2 k11 | 2 048 | 1 967 / 2 105 / 2 047.6 | 0.9998 | 0.9996 | 4 |
| n24 m2 t2 k12 | 4 096 | 4 001 / 4 243 / 4 102.0 | 1.0015 | 1.0029 | 4 |

*Stated as a test of H-RELN-96e3ba's mechanism: consistent with it.* That
hypothesis derives the 2^m from `|W|/B = 2`. In these binary cells V is an
F_2-subspace of F_{2^n} chosen without reference to the curve, so only about
half its elements are x-coordinates of rational points and each of those
carries two lifts, giving `L/|V| ≈ 1` rather than 2. The measured
`(L/|V|)^m = 0.988–1.003` is exactly what the mechanism predicts at
`L/|V| ≈ 1`. No 2^m appears, and on that mechanism none should. Independently,
this run's per-cell conservation audit confirms the *counting identity* that
hypothesis's step 3 rests on — total enumerated multisets equal
`C(L+t−1, t)` exactly, with `L` in the role of `2B`, and the total is accounted
for with no remainder as incidences on legal targets plus multisets summing to
infinity plus multisets whose sum has x in V. The identity holds in every
audited cell.

*Stated the other way, as a test of whether eq. (11) itself carries a 2^m
defect: it does not, in the binary setting.* Substituting the number of points
actually searched for `|V|` costs a factor of 0.988–1.003 at m = t = 2, not 4.
So the 2^m-type discrepancy is a property of how a protocol's factor base is
**encoded** relative to eq. (11)'s `|V|`, not of eq. (11)'s probability model.
The discrepancy is real and this run reproduces its mechanism; it is not
located in the formula.

---

## 7. All seven control outcomes, stated separately

**(1) baseline.** PASSED, with a scope note. eq. (11) recomputed against all 33
`P_theoretical` entries of the frozen transcription of Tables 1–2 (the contract
required four). All 33 match to four decimals under truncation; max absolute
error 9.871e−05. Only 10 of 33 match under rounding, identifying the paper's
convention as truncation. As the contract insists: this is **not** evidence
that eq. (11) is right. The paper's probability column is the model's own
output, not an observation, and this control checks only that this program
evaluates the model correctly.

**(2) matched_null.** PASSED. A symmetric random map realized directly over the
exact class count and pushed through the identical counting and ratio pipeline,
five realizations per cell, evaluated exactly over all q targets. All 45
realizations have a 95% interval containing 1. Point estimates span
0.9906–1.0123 with per-cell means 0.9999–1.0079. The most negative point
estimate, 0.9906 at n13, carries the interval [0.9630, 1.0185]. **The pipeline
does not produce a shortfall by itself, so the curve-derived cells are not
void.** The same control also passes the Poisson goodness-of-fit test in every
cell (section 5), which is what separates "the wrong law" from "a bug in the
fitting code".

**(3) nearby_object.** RUN, with the outcome in tail check 3. The single
polynomial eq. (4) counted on the **same** R draws as the matched
presentation. Result: the two presentations never differ in whether a target is
decomposable, and differ in count only inside the Lemma 2 side-condition
failure set, always downward. This is the control that distinguishes "eq. (11)
is the wrong law" from "eq. (11) is right for eq. (4) and the chain loses
solutions", and it points at the former: the chain's losses are confined to a
measured, small, side-condition-failure set and cannot account for the
distributional mismatch in section 5, which is present at full strength in the
single presentation.

**(4) known_false.** PASSED. A deliberately wrong class count `|V|^t` with no
symmetry correction at all. The modelled λ shifts by **exactly t!** in every
cell — measured shift 24, 6, 6, 6, 6, 720, 2, 2, 2 against t! for
t = 4, 3, 3, 3, 3, 6, 2, 2, 2 — to floating-point equality. The pipeline is
therefore fully sensitive to the class count and a discrepancy can be
attributed to it. Recorded honestly: the resulting **P** ratio shifts by less
than t! wherever λ is not small (e.g. 0.6225 rather than 1/2 at the t = 2
cells), because `P = 1 − exp(−λ)` saturates. That is a property of the link
function, not of the class count; λ is the quantity the class count multiplies
and it shifts exactly.

**(5) invalid_input.** PASSED on all four probes. R at the point at infinity
rejected; V not closed under F_2-addition rejected; V of the wrong dimension
rejected; a genuine subspace accepted. None was counted.

**(6) exhaustiveness.** PASSED. Three cells (n15, n12, n13) re-enumerated under
a permuted factor-base ordering: per-R counts identical, and additionally
identical between the histogram path and the independent lookup path. The
enumeration is order-independent, hence complete. The cross-check suite adds
that the histogram visits `C(L+t−1,t)` multisets exactly in all four cells
where it was run.

**(7) lemma2_side_condition.** RUN, with the outcome in section 4. Recorded per
R, together with the F_{q^2}\F_q solution count per R, so the
chained-versus-single comparison has the denominator the contract requires.
Failure fraction 0.0000–0.0900 by cell with intervals; where the condition
holds, its conclusions hold universally; verified against brute-force
enumeration in F_{q^2} at eight small parameter sets.

---

## 8. Diagnosis required by the ratio-above-1 stopping rule

This section exists because the rule fired. It is a **diagnosis, not a
re-scoring**: the frozen prediction is scored as written in section 9, and
nothing here is offered as a substitute comparator.

The ratio of the measured mean to eq. (11)'s λ factors **exactly**, with no
fitting, into four separately computable pieces:

    measured_mean / λ_eq11  =  f_legal · f_multiset · f_base · f_pop

- `f_legal   = incidences / C(L+t−1,t)` ≤ 1 — the fraction of point multisets
  whose sum is a legal target at all; the rest sum to the point at infinity or
  to a point whose x lies in V and is therefore excluded from the target
  population.
- `f_multiset = C(L+t−1,t) / (L^t/t!)` ≥ 1 — the exact multiset count against
  the t!-division approximation.
- `f_base    = (L/|V|)^t` — eq. (11) charges `|V|` x-values where the factor
  base holds `L` rational points.
- `f_pop     = q / |target population|` — eq. (11) divides by q; the
  algorithm's targets are the affine points whose x lies outside V.

Measured over the **whole** target population, so with no sampling error at
all:

| cell | L | \|V\| | f_legal | f_multiset | f_base | f_pop | product | observed | residual |
|---|---|---|---|---|---|---|---|---|---|
| n13 m4 t4 k4 | 19 | 16 | 0.9799 | 1.3471 | 1.9885 | 1.0250 | 2.6907 | 2.6907 | **1.0000000** |
| n15 m5 t3 k3 | 3 | 8 | 0.0000 | 2.2222 | 0.0527 | 0.9918 | 0.0000 | 0.0000 | 0/0 |
| n17 m3 t3 k6 | 65 | 64 | 0.9547 | 1.0466 | 1.0476 | 1.0013 | 1.0481 | 1.0481 | **1.0000000** |
| n19 m3 t3 k7 | 139 | 128 | 0.9785 | 1.0217 | 1.2806 | 1.0018 | 1.2826 | 1.2826 | **1.0000000** |
| n21 m3 t3 k7 | 139 | 128 | 0.9786 | 1.0217 | 1.2806 | 0.9987 | 1.2787 | 1.2787 | **1.0000000** |
| n12 m6 t6 k2 | 5 | 4 | 0.7048 | 9.6768 | 3.8147 | 0.9899 | 25.7516 | 25.7516 | **1.0000000** |
| n20 m2 t2 k10 | 977 | 1 024 | 0.9972 | 1.0010 | 0.9103 | 1.0021 | 0.9105 | 0.9105 | **1.0000000** |
| n22 m2 t2 k11 | 2 051 | 2 048 | 0.9985 | 1.0005 | 1.0029 | 1.0006 | 1.0025 | 1.0025 | **1.0000000** |
| n24 m2 t2 k12 | 4 047 | 4 096 | 0.9993 | 1.0002 | 0.9762 | 0.9999 | 0.9756 | 0.9756 | **1.0000000** |

The attribution closes to 1e−9 in every cell. **There is no unattributed
excess.** Three of the four factors are properties of eq. (11)'s own
approximation rather than of the curve, and all three tend to 1 as `|V|` grows
at fixed t:

- `f_multiset` is closed-form and needs no measurement at all: `C(|V|+t−1,t)`
  against `|V|^t/t!` is 14.77× at `|V| = 4, t = 6`, 1.42× at `|V| = 16, t = 4`,
  1.024× at `|V| = 128, t = 3`, and 1.0002× at `|V| = 4096, t = 2`. A random
  map over the exact class count therefore hits more targets than eq. (11)
  predicts with no curve involved, which the matched null confirms directly:
  its "vs semaev" ratio is 14.78, 1.42, 1.02 in exactly those cells.
- `f_base` is a fluctuation, not a bias. `L = 2r − 1` with r the number of
  x ∈ V carrying a rational point, so `L` has mean about `|V|` and standard
  deviation about `sqrt(|V|)`; the t-th power multiplies the relative
  fluctuation by t. At `|V| = 128, t = 3` a 1σ upward draw (L = 139) inflates
  the mean by 28%. Averaged over the 20 configurations of each t = 2 cell,
  `(L/|V|)^t` is 0.988–1.003 (tail check 4). This is the dominant driver of the
  per-configuration ratio spread, which runs 0.31–0.37 at the t = 2 cells and
  1.76–54.4 at the smallest.
- `f_pop` is within 2.5% of 1 everywhere.

**The one factor that reflects the curve rather than the formula, `f_legal`, is
at or below 1 in every cell without exception**: 0.9993, 0.9985, 0.9972,
0.9799, 0.9786, 0.9785, 0.9547, 0.7048 (and 0 at the degenerate n15).

### The shape-only comparison, which no class-count convention can move

Asking whether eq. (11)'s Poisson zero-probability holds **at the realized
mean** removes every class-count question by construction. Pooled over all 20
configurations per cell, E side:

| cell | \|V\| | t | realized mean | realized P | 1 − exp(−mean) | **f_dispersion** |
|---|---|---|---|---|---|---|
| n12 m6 t6 k2 | 4 | 6 | 0.03595 | 0.01385 | 0.03531 | **0.3922** |
| n15 m5 t3 k3 | 8 | 3 | 0.00323 | 0.00323 | 0.00322 | 1.0016 (mean ≈ 0; uninformative) |
| n13 m4 t4 k4 | 16 | 4 | 0.48110 | 0.29063 | 0.38190 | **0.7610** |
| n17 m3 t3 k6 | 64 | 3 | 0.39098 | 0.32288 | 0.32360 | **0.9978** |
| n19 m3 t3 k7 | 128 | 3 | 0.70175 | 0.49538 | 0.50428 | **0.9823** |
| n21 m3 t3 k7 | 128 | 3 | 0.20442 | 0.18357 | 0.18488 | **0.9929** |
| n20 m2 t2 k10 | 1 024 | 2 | 0.49525 | 0.35507 | 0.39058 | **0.9091** |
| n22 m2 t2 k11 | 2 048 | 2 | 0.50350 | 0.35683 | 0.39559 | **0.9020** |
| n24 m2 t2 k12 | 4 096 | 2 | 0.50340 | 0.35700 | 0.39553 | **0.9026** |

`f_dispersion` is **below 1 in every cell where the mean is non-negligible**.
More targets have zero decompositions than a Poisson of the same realized mean
allows, and the deficit deepens with t: 0.90 at t = 2, 0.98–0.99 at t = 3, 0.76
at t = 4, 0.39 at t = 6. This is the quantity that survives every convention,
and it points downward at every t.

---

## 9. The frozen prediction, scored exactly as written

The prediction in `specification.yaml` is frozen. It is scored here against the
ratio as it defines it, with no substitution. No clause was adjusted and no run
was re-scored.

**Clause 1** — "ratio < 1 with the 95% interval excluding 1 in every cell with
t ≥ 3 and tk−n ∈ [−2,+2], falling short by at least 20%". The qualifying cells
are n17 (t3, +1), n19 (t3, +2), n21 (t3, 0) and n12 (t6, 0). Measured
(E, usable, Semaev variant): 1.1390 [1.1229, 1.1552]; 1.0181 [1.0080, 1.0281];
1.1958 [1.1713, 1.2207]; 9.9789 [9.1867, 10.8384]. **NOT MET.** All four
intervals exclude 1 on the **high** side — the direction opposite to the
prediction. This is the observation that fired the stopping rule; section 8 is
its diagnosis.

**Clause 2** — "the ratio decreasing monotonically as t goes 2 → 3 → 4 at
matched tk−n, with the t = 4 ratio below the t = 2 ratio by at least a factor
of 2". **NOT MET, and partly unavailable.** At matched tk−n = 0 the ratio
*increases* from t = 2 (0.9024, 0.9069, 0.9073) to t = 3 (1.1958) to t = 6
(9.9789). The t = 4 versus t = 2 comparison **cannot be made at matched tk−n**
in the declared cell set: the only t = 4 cell, n13, sits at tk−n = +3 and no
t = 2 cell was declared there. Recorded as unavailable rather than supplied by
adding a cell, which the contract forbids. Compared unmatched, the t = 4 ratio
(1.0252) is *above* the t = 2 ratio, not a factor of 2 below it.

**Clause 3** — "per-R counts Poisson with mean 2^{tk−n}·c(t) and c(t) < 1
decreasing in t". **NOT MET on both halves.** The Poisson fit is rejected at 7
of 9 cells while the matched null passes the identical test at every cell
(sections 5 and 7). c(t) is measured at 0.99–25.88 (class granularity) and
0.90–2.12 (ordered granularity); it is not below 1 except marginally at n20,
and it increases rather than decreases with t.

**Clause 4** — "chained and single counts agreeing per R except on the measured
Lemma-2 failure fraction". **MET**, in a stronger form than stated: the two
presentations agree on every one of the **354 223** E-side targets where the
side condition held, and differ only within the 5 777-target failure set,
always downward (tail check 3).

No amendment to the prediction is requested and none was made. The clauses that
were not met are recorded as not met.

---

## 10. Is HEUR-SEMAEV-2015-4.3 still a sound comparator for EXP-RELN-164ad3?

Stated either way, as the contract requires. EXP-RELN-164ad3's metric M3 uses
HEUR-SEMAEV-2015-4.3 as "the protocol's reported curve" against an exact law
and forces the ratio exact/reported toward 2^m = 4 at small B.

**Sound, in two respects.** The formula this program attributes to Section 4.3
is faithfully transcribed: it reproduces all 33 printed `P_theoretical` values
to four decimals under the paper's own truncation convention, so M3 is
comparing against the right formula, correctly evaluated. And in the mean, once
the number of points actually searched is used in place of `|V|`, eq. (11)'s λ
is accurate to the `f_legal` shortfall alone — 0.07% to 4.5% at this run's
larger cells.

**Not sound, in the specific way M3 currently uses it.** The whole of M3's 2^m
residual is this run's `f_base = (L/|V|)^m`, where the RELN protocol's factor
base is declared as B on-curve x-coordinates but the search ranges over the
`|W| = 2B` points they lift to, while `B` is substituted directly into
`B^m/(m!·p)`. That is an **encoding mismatch between the protocol's factor base
and eq. (11)'s `|V|`**, not a defect in eq. (11)'s probability model. This run
measures the same factor in a setting where `L/|V| ≈ 1` and finds
`(L/|V|)^m = 0.988–1.003` at m = t = 2 — no 2^m. So M3's residual is
attributable to the substitution, and HEUR-SEMAEV-2015-4.3 is a sound
comparator **only** when `|V|` is charged the number of factor-base points the
search actually ranges over. Used without that substitution it is biased low in
the mean by `(|W|/B)^m = 2^m`, which is exactly the discrepancy
H-RELN-96e3ba reports and M3 forces.

**A second caveat, independent of the first.** Even with the mean corrected,
eq. (11)'s link `P = 1 − exp(−λ)` fails the shape test at 7 of 9 cells here
while the matched null passes it, with the failure always in the direction of
excess zeros (section 8's `f_dispersion` ≤ 1). A comparator built on eq. (11)'s
**mean** therefore stands on firmer measured ground than one built on its
**probability**, and M3 compares probabilities.

Per the contract's interpretation limits: EXP-RELN-164ad3 and H-RELN-96e3ba are
immutable, and nothing here edits them. If this observation bears on them the
remedy is a new record and an additive amendment.

---

## 11. The sign of the bias entering stage-1 cost, with its derivation

**The bias is NEGATIVE: eq. (11) UNDERSTATES stage-1 relation-collection cost.
Equivalently it OVERSTATES the decomposition probability, so Semaev's published
stage-1 cost is optimistic.**

### Derivation

**Step 1 — the sign inversion.** Stage-1 cost scales as the number of relations
needed times the cost per trial divided by the probability that a trial
succeeds: `cost ∝ 1/P`. So the sign of the bias in cost is the **opposite** of
the sign of the bias in P. If eq. (11) overstates P, it understates cost.

**Step 2 — which measured factors transfer, and which do not.** Section 8
factors the measured-over-predicted mean ratio exactly into
`f_legal · f_multiset · f_base · f_pop`, with no residual. Three of those four
are toy-window artifacts and do not transfer:

- `f_multiset → 1` as `|V| → ∞` at fixed t. It is `C(|V|+t−1,t)/(|V|^t/t!)`,
  which is `1 + O(t²/|V|)`; already 1.0002 at `|V| = 4096, t = 2`. At a
  cryptographic `|V| = 2^k` with k in the tens it is indistinguishable from 1.
- `f_base = (L/|V|)^t` is a **fluctuation with mean ≈ 1**, not a bias. `L` has
  mean about `|V|` and standard deviation about `sqrt(|V|)`, so the relative
  fluctuation is `O(t·|V|^{-1/2})` and averages out. Measured over 20
  configurations per cell it is 0.988–1.003 at t = 2 and its per-cell spread
  collapses as `|V|` grows (ratio spread 0.31–0.37 at `|V| ≥ 1024` against
  1.76–54.4 at `|V| ≤ 16`).
- `f_pop → 1`: it is `q/|targets|`, within 2.5% of 1 in every cell.

**Step 3 — the two factors that do transfer, and both point the same way.**

- **`f_legal ≤ 1` in every cell without exception** (0.9993 down to 0.7048).
  eq. (11) charges every one of its `|V|^t/t!` classes as a potential hit, but
  a definite fraction of point multisets cannot produce a legal target at all:
  those summing to the point at infinity, and those whose sum has
  x-coordinate in V and is therefore excluded from the target population. Both
  exclusions are structural, are present at every scale, and can only remove
  incidences. Measured at 0.07%–4.5% at the larger cells.
- **`f_dispersion ≤ 1` in every cell where the mean is non-negligible**
  (0.9091, 0.9026, 0.9020 at t = 2; 0.9978, 0.9823, 0.9929 at t = 3; 0.7610 at
  t = 4; 0.3922 at t = 6). eq. (11) converts a mean into a probability through
  the Poisson `1 − exp(−λ)`, which presumes the decompositions of distinct
  targets are independent. The realized counts are over-dispersed: the same
  mean is distributed over fewer targets, so **more** targets have zero
  decompositions than eq. (11) allows. This factor is invariant to every
  class-count convention by construction, and the deficit deepens with t.

Both surviving factors depress P. Their product is the transferable bias, and
it is below 1.

**Step 4 — the direct measurement, at the cells where the artifacts are
numerically negligible.** At n20, n22 and n24 (t = 2, `|V| = 1024, 2048,
4096`), `f_multiset` is 1.0010/1.0005/1.0002 and `f_pop` is ≈ 1.000, so the
Semaev and exact class-count variants agree to three decimals and the measured
ratio is essentially artifact-free. Pooled over 20 configurations each:

> **0.9024 [0.8905, 0.9144], 0.9069 [0.8950, 0.9188], 0.9073 [0.8954,
> 0.9193]** — a 9–10% overstatement of P, stable across three field sizes,
> every interval excluding 1 below.

By step 1 that is a **9–10% understatement of stage-1 cost at t = 2 in this
window**. The direction is not a fit: it is forced by the paper's own
inequality chain `P(n,m,t,k) ≥ P(solve eq. 5)`, and every transferable factor
this run measured respects that inequality.

### Scope, stated explicitly

The **magnitude** (9–10% at t = 2, growing with t at the shape level to 24% at
t = 4 and 61% at t = 6) is claimed **only** over the tested window: binary
curves `y² + xy = x³ + B` with A = 0, n ∈ {12,…,24}, `tk − n ∈ [−6,+6]`,
F_2-subspace factor bases, 180 configurations. It is a toy-tier measurement and
does not transfer.

The **sign** transfers, and it transfers by the paper's own inequality rather
than by any measurement here. Per the contract's own interpretation limit, a
ratio below 1 moves the concrete crossover n and cannot move the asymptotic
exponent `2^{1.6986·sqrt(n·ln n)}`, which absorbs a constant or t-dependent
factor in P identically. Nothing here says anything about Assumption 1 or
Assumption 2: eq. (11) is a probability model and those are degree bounds. No
degree was measured, estimated or assumed anywhere in this run, and no
polynomial system was solved.

---

## 12. Bearing on the eq. (11)-conditional closure (DEC-20260913-74e208 / EV-SEMBIN-1d36a3)

Stated as an observation about the confound, not as a decision, which is not
this role's to make.

That closure rests on eq. (11) as published, and its obstruction block charges
a per-link yield of `k − log2 t` bits. The confound that would invert it is
**realized yield falling short of eq. (11) more at t = m than at t < m**.

**This run cannot invert the closure, and the reason is a cell-set limitation
rather than a measurement.** Eight of the nine declared cells have **t = m**;
the sole `t < m` cell is n15 (m5 t3 k3, tk−n = −6), and it is the degenerate
corner of the window. Its pooled realized yield is 0.0032 against an eq. (11)
prediction of 0.0026, and its sampling-free exact pass — for the B = 1
low-degree configuration, where the factor base holds only L = 3 rational
points — finds **zero** usable relations across all 33 040 targets. There is
therefore no `t < m` anchor with a non-degenerate yield to compare a `t = m`
shortfall against. The comparison the confound requires is **not available in
this cell set**, and I did not add a cell to supply it.

What this run does say about the closure's foundation:

- A `t = m` shortfall is **present and measured** where the class-count
  artifacts are negligible: 9–10% at the three m = t = 2 cells. At the
  shape level it is 24% at m = t = 4 and 61% at m = t = 6.
- **But it is not monotone in t, and that matters here.** The shape deficit
  runs 9–10% at t = 2, then only **0.2–1.8% at the three t = 3 cells**, then
  24% at t = 4 and 61% at t = 6. The t = 3 cells have the *smallest* deficit in
  the whole window. A confound argument that needs "shortfall grows with t = m"
  is not supported by a sequence that dips in the middle, and I have no
  mechanism to offer for the dip.
- In any case growth with `t = m` alone does not invert anything without the
  matched `t < m` arm, because the closure's charge is a *difference* between
  the two.
- Separately, the two transferable factors together (`f_legal · f_dispersion`)
  shift eq. (11)'s yield in this window by **0.142, 0.151 and 0.149 bits at the
  three m = t = 2 cells**, 0.041–0.070 bits at t = 3, **0.423 bits at
  m = t = 4** and **1.855 bits at m = t = 6** — against the closure's charge of
  27.68 to 44.00 bits at the FIPS labels. On the magnitudes measured here the
  correction is a fraction of a bit against tens of bits, so it does not by
  itself threaten the charge; the window is toy and the magnitude does not
  transfer, but the *growth* of that correction with t = m (0.15 → 0.42 → 1.86
  bits) is the part a follow-up would need to bound at scale.

**So: consistent with the closure, not inverting it, and not confirming it
either.** The confound remains open and the measurement that would settle it is
a matched `t < m` versus `t = m` pair at comparable `tk − n` with a
non-degenerate yield — which is a new contract, not something this frozen cell
set can be stretched to cover.

---

## 12a. Protocol deviation, recorded

One deviation. After the measurement and every artifact was complete, I sent a
single agent-bus message pointing the Coordinator at this run package and at
the ratio-above-1 diagnosis. It landed at
`coordination/bus/messages/MSG-20260913-477ddd.yaml`, which is **outside the
handoff's declared `write_scope`** (that scope names only
`experiments/EXP-SEMBIN-354a75/code/` and
`experiments/EXP-SEMBIN-354a75/runs/RUN-SEMBIN-1b9afe/`). The write was
therefore a deviation and is recorded rather than reverted, because a bus
record is write-once and deleting one is the worse of the two faults.

It affects no measurement: it was written after `raw-result.json` and
`per-R-counts.json` were sealed, it contains no number not already in this
report, and under AGENTS.md a message is a pointer and never evidence. It was
**not published** — publishing needs `agent_bus.py sync --push` and the
executor does not push — so it is visible only inside this worktree. The
Coordinator may include that path in its snapshot and publish it, or leave it
and ignore it; the run package is complete without it.

No other departure from the approved protocol occurred. No cell was resized, no
sampling was substituted for enumeration, no cell was added, the specification
was not touched, and the frozen prediction was scored as written.

---

## 13. Unexpected observations

Recorded because AGENTS.md requires it; none was discarded.

1. **Specification annotation mismatch at n15 m5 t3 k3.** `specification.yaml`
   annotates `paper_probability = 0.0009`, but the frozen transcription in
   `inputs/SEMAEV-2015-310/tables.yaml` prints **0.0026** for that cell and
   eq. (11) evaluates to 0.002601. The specification is frozen and was not
   edited; the baseline control is run against the frozen transcription of the
   paper, which is the primary source, and against it eq. (11) reproduces every
   printed value. Recorded rather than silently reconciled. Also captured in
   `raw-result.json` under `unexpected_observations`.

2. **The Poisson shape fails where the null passes.** The per-R count
   distribution is rejected at 7 of 9 cells (p < 1e−8 at 5 of them) while the
   matched null's own realized counts pass the identical test at every cell
   (p = 0.216–0.962). The failure is excess zeros plus a heavy upper tail: at
   n13, 586 of 40 000 targets in the "≥ 5" bin against 5.77 expected, and a
   maximum count of 20 with probability 0 under the fit. Not anticipated at
   this strength.

3. **The chain never gains.** 648 targets out of 360 000 E-side draws where
   chained and single differ; the Lemma 2 side condition had failed in **all
   648** and held in **none**; every difference negative, 1 to 12. The
   per-R retention the contract mandated is exactly what made this visible — a
   mean difference would have shown ≈0.

4. **Usable yield is identically zero on the T-side target population**, over
   180 000 draws in all nine cells, while single and chained yields there are
   0.83–1.91 of eq. (11). Structural, not statistical. It quantifies the gap
   between "the algebraic system has a solution" and "there is a usable
   relation" on the half of eq. (11)'s own `random z in F_q` population that
   carries no rational point.

5. **F_{q^2}\F_q solutions are absent at t = 2 and t = 3 and substantial at
   t = 4 and t = 6** for the tested curves and subspaces — exactly 0 at n15,
   n17, n19, n21, n20, n22, n24, then 18.19% of all counted solutions at n13
   (t = 4) and 24.71% at n12 (t = 6). The cross-check suite confirms the
   machinery does find such solutions at t = 3 where they exist, so the zeros
   are measurements rather than blindness.

6. **`s = 1` never occurs.** A solution with exactly one non-rational point is
   structurally impossible in this construction — confirmed by brute force in
   F_{q^2} at eight small parameter sets. Not stated in the contract; it is why
   the non-rational solutions always appear in the s ≥ 2 configurations
   Lemma 2 describes.

7. **The shape deficit is not monotone in t.** `f_dispersion` is 0.902–0.909
   at t = 2, then **0.982–0.998 at all three t = 3 cells**, then 0.761 at
   t = 4 and 0.392 at t = 6. The middle of the range has the smallest deficit,
   so the departure from eq. (11)'s Poisson link does not simply worsen with t
   in this window. I have no mechanism for the dip and am not proposing one;
   it is recorded because a monotone reading of the t-trend would be wrong and
   the frozen prediction's clause 2 asked for monotonicity.

8. **The paper truncates rather than rounds.** Only 10 of 33 printed
   `P_theoretical` values match eq. (11) under rounding; all 33 match under
   truncation. Incidental, but anyone re-deriving the table needs it.

---

## 14. Completion gate

| gate item | status |
|---|---|
| eq. (11) reproduces the four published decimals | **met** — verified at all 33 printed cells, under truncation |
| matched null returns ratio 1 within its interval | **met** — 45/45 realizations' intervals contain 1 |
| known-false class count shifts the ratio by t! | **met** — exactly, in λ, in all 9 cells |
| exhaustiveness control shows order-independent per-R counts | **met** — 3 cells, two orderings, identical |
| a ratio above 1 halts for diagnosis, never reported as a finding | **fired and honoured** — halted, diagnosed in section 8, reported as a diagnosis |
| every unreached cell recorded with the size of V^t it needed | **met, vacuously** — none unreached; domains recorded anyway |
| no evidence record written, no hypothesis status changed | **met** |
| all planned runs terminal | **met** — 180/180, exit 0, no partial configuration |
| required artifacts present | **met** — section 15 |
| raw data and summaries agree | **met** — summaries regenerated from `raw-result.json`; exact whole-population pass reproduces sampled hit fractions to sampling error |
| result reproduces from the recorded command and revision | **met** — self-tests re-run post-measurement and passing; order-independence control reproduces per-R counts |

---

## 15. Artifact paths for the Coordinator's snapshot commit

Nothing here was committed; per the handoff and `agents/executor.md` the
Coordinator makes the snapshot commit. All paths are inside the declared write
scope.

Run package — `experiments/EXP-SEMBIN-354a75/runs/RUN-SEMBIN-1b9afe/`:

| path | role |
|---|---|
| `manifest.yaml` | run manifest (required by the handoff) |
| `raw-result.json` | machine-readable results, controls, exact measurements, fits (required) |
| `per-R-counts.json` | per-R counts in full, both presentations, all configurations, both populations (required) |
| `command.txt` | exact command and working directory |
| `environment.json` | OS, interpreter, dependency versions, absence of a Gröbner engine |
| `stdout.log` | per-configuration progress log |
| `stderr.log` | empty — nothing was emitted |
| `artifact-digests.json` | wrapper-recorded artifact and code hashes |
| `ratio-above-1-diagnosis.txt` | the diagnosis the stopping rule required |
| `summary-tables-E.txt`, `summary-tables-T.txt` | human-readable tables, both target populations |
| `selftests.txt` | all three self-test suites, re-run after the measurement |
| `task-report.md` | this report |

Code — `experiments/EXP-SEMBIN-354a75/code/`:

| path | provenance |
|---|---|
| `binary_field.py`, `selftest_binary_field.py` | pre-existed on this branch from an earlier interrupted session; reused **unmodified**, self-test re-run and passing before any count was taken |
| `run_wrapper.py` | adapted from `experiments/EXP-SEMBIN-81dc96/code/run_wrapper.py` as the handoff directs |
| `fastfield.py`, `selftest_fastfield.py` | authored for this task — vectorized arithmetic and the twist construction, checked element-by-element against `binary_field.py` |
| `yield_core.py`, `selftest_yield_core.py` | authored for this task — the counting machinery and its independent cross-checks |
| `yield_stats.py`, `yield_null.py` | authored for this task — interval/fit statistics, and the matched-null and known-false realized maps |
| `yield_run.py` | authored for this task — the driver |
| `yield_report.py`, `yield_diagnose.py` | authored for this task — read-only summarizers over the run's own artifacts |

SHA-256 for every file above is recorded in `manifest.yaml` under
`artifacts.code_sha256` and `artifacts.present`.
