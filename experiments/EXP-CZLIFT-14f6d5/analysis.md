# EXP-CZLIFT-14f6d5: analysis

Hypothesis H-CZLIFT-27a184 · Question RQ-CZLIFT-b9f765 · Goal GOAL-CZLIFT-1516d5
Runs RUN-CZLIFT-ca7450 (trial ladder-h1e5, hmax 1e5) and RUN-CZLIFT-b1dce4 (trial ladder-h3e5, hmax 3e5)
Evidence EV-CZLIFT-b6fe48 · Decision DEC-20261023-6931ab (weaken) · Tier toy
Reviews: reports/validation-20261022/validation_report.yaml (VAL-20261022-2dd0e7, passed); reports/redteam-20261023/redteam_report.yaml (RT-20261023-174849; R1, R2 and PTM-1 break)
Earlier observation record: DEC-20261009-44c288

This note keeps Observation, Comparison, Inference and Limitation separate. Its Inference section holds the derivation note D1-D4 that EV-CZLIFT-b6fe48 cites as `proof_status: derivation`. Items E1-E2 are empirical and post hoc, and they are labelled as such.

## Observation

### Validity (checked before any interpretation)

- Run count: 2 of 2 planned trials ran (trial-plan.json: ladder-h1e5 -> RUN-CZLIFT-ca7450, ladder-h3e5 -> RUN-CZLIFT-b1dce4). No unplanned run exists. This is within maximum_runs 4.
- Receipts: both are `output_validated`, with returncode 0 and check_returncode 0. plan_sha256 is 1248daec... on both, and the authority commit is 08ee02a391.
- Schema and custody: both manifests are complete for the run schema. All six specification-required artifacts are present. 20/20 artifact hashes match execution-receipt.json and the ledger receipt (VAL J1). Contract and source files are byte-identical from freeze to snapshot. dirty is false.
- Seeds: `seed: null` and `deterministic: true`, as the specification requires (`seeds: []`). This is exhaustive enumeration, not sampling.
- Raw/summary agreement: every frozen metric, count, coverage cell, H_half table and secondary slope recomputes exactly. Layer A covers cell arithmetic from raw. Layer B is the validator's own enumeration, own #E(F_p) and own reductions; it has 0 mismatches (VAL J2). The red team's positive control reproduces every grid count and every distinct count (0 mismatches in 480 cells).
- Controls:
  - C1: the rank-7 curve's counts and cells equal lane-1 RUN-CZLIFT-74f172 and RUN-CZLIFT-490b33. This holds, verified by the validator; check.py does not test it.
  - C2: point re-verification and the H = 300 recount. These ran, but the recount is vacuous on the record curves, where N(300) = 1, which is O only.
  - C3: rank labels are lower bounds. This holds in the records. The validator certified rank >= 8 and rank >= 9 from the sources' points, and rank >= 7 for the overlap curve.
- Amendments: experiments/EXP-CZLIFT-14f6d5/amendments/ holds only .gitkeep, so no protocol amendment exists.
- Certificates: no solve or relation is claimed, so no certificate applies.
- Verdict: the run set is admissible evidence.

### Recorded values (raw-result.json, manifests)

N_E(H) counts the rational points of naive x-height max(|a|, d^2) <= H, with O and ±P counted separately.

| H | 10 | 30 | 100 | 300 | 1e3 | 3e3 | 1e4 | 3e4 | 1e5 | 3e5 |
|---|---|---|---|---|---|---|---|---|---|---|
| 382623908456a1 [0,0,0,-10012,346900], rank >= 7 | 7 | 17 | 65 | 113 | 187 | 329 | 527 | 783 | 1155 | 1559 |
| Grunewald-Zimmert 1977 [1,-1,1,-6494556985832,6351402068900282539], rank >= 8 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 5 | 11 |
| Brumer-Kramer 1977 [1,-1,1,-1608154463,25555312501831], rank >= 9 | 1 | 1 | 1 | 1 | 3 | 7 | 29 | 113 | 215 | 311 |

RUN-CZLIFT-ca7450 is identical up to 1e5. The absolute discriminants are 1.2244e13, 1.0488e38 and 1.5947e28 respectively.

- Coverage (frozen definition):
  - Median 1.041919 over 131 cells (RUN-CZLIFT-ca7450) and 1.042439 over 156 cells (RUN-CZLIFT-b1dce4).
  - frac_above_1.5 = frac_below_0.5 = 0 on both runs.
  - Of the frozen cells, the rank-7 curve supplies 99 and 109, BK 32 and 47, and GZ none.
- H_half on the record curves (RUN-CZLIFT-b1dce4): BK reaches half coverage at H = 3e4 for p = 103 and 149, at 1e5 for p = 211 and 293, and at 3e5 for p = 419. GZ never does.
- No record-curve H_half at p >= 1000. The rank-7 curve resolves H_half at p = 1193, 1697 and 2417.
- Growth slopes, (1e5 / 3e5): rank-7 3.18 / 3.22; GZ 4.62 / 6.38, which are 2- and 3-point fits; BK 8.86 / 8.31.
- The frozen success criterion reads met on both trials, and no frozen falsification clause fires. This repeats DEC-20261009-44c288, recomputed by VAL-20261022-2dd0e7.

### Reviewer values (read by key from committed review artifacts)

- DISC-1 (VAL): the recorded coverage summary applies a saturation filter (model_distinct <= 0.9 N_p) and takes the upper median. Neither the specification nor the hypothesis states either rule. Under the hypothesis's own cell set (N >= 30, no filter) the medians are 1.038875 (144 cells) and 1.038043 (176 cells), and every cell ratio lies in [0.99659, 1.25932].
- Elkies-Watkins low-conductor rows (red team, rt_summary_output.json; rank labels are lower bounds):

  | row | N_E(1e5) | N_E(3e5) | N_E(1e6) |
  |---|---|---|---|
  | rank >= 8 | 1027 | 1505 | 2149 |
  | rank >= 9 | 1023 | 1529 | 2281 |
  | rank >= 10 | 743 | 1163 | – |
  | rank >= 11 | 665 | 1021 | – |

  The rank-7 curve has N_E(1e6) = 2153.
- Coefficient-matched random curves, N_E(3e5), 12 curves per size: at the rank-7 curve's size, median 1 and maximum 9; at BK's size and at GZ's size, maximum 1.
- Translation mutations x = x' + t, all preserving the discriminant, N_E(1e5) / N_E(3e5):

  | curve | t | N_E(1e5) | N_E(3e5) |
  |---|---|---|---|
  | rank-7 | 0 | 1155 | 1559 |
  | rank-7 | 1e3 | 527 | 775 |
  | rank-7 | 1e4 | 273 | 373 |
  | rank-7 | 1e5 | 151 | 187 |
  | rank-7 | 1e6 | 3 | 5 |
  | GZ | 0 | 5 | 11 |
  | GZ | 1536898 | 29 | 59 |
  | GZ | 1634797 | 23 | 41 |
  | BK | 0 | 215 | 311 |
  | BK | 1e6 | 13 | 17 |

- Rank-0 objects: 11a1 has N_E = 3 at H = 10 and 5 for H = 30..3e5 (validator and red team agree). 210e2 = [1,0,0,-1070,7812], torsion Z/2 x Z/8, has N_E = 16 for H = 300..3e5 (red team).
- Coverage, against the RUN-CZLIFT-b1dce4 cells, 400 replicates each (rt_coverage_null_output.json):
  - Nested uniform-point null: median statistic 1.0008 ± 0.0017 (1 sd); 0 of 400 replicates at or above the observed 1.0424.
  - Same-height-rationals null: 1.0277 ± 0.0040; 0 of 400 at or above 1.0424. For BK alone (observed 1.0271), 79.5 percent of replicates are at or above it.
  - Top 32 cells: observed collisions 4969; uniform 6142 ± 39; same-height rationals 3751 ± 57.
- Alternatives on the same cells (rt_coverage_output.json):
  - A DL-known arithmetic progression {kG : |k| <= m} gives medians 1.0710 / 1.0825 and frac above 1.5 of 0.0458 / 0.0449. It passes the frozen criterion.
  - Subgroup confinement gives medians 0.934 / 0.927 at index 2, 0.873 / 0.862 at index 3, and 0.818 / 0.802 at index 4. The index-4 alternative passes the frozen criterion in 97.5 / 63 percent of replicates.
- Spearman correlations over the seven rank >= 7 curves:
  - N_E(1e5): -1.00 against log|disc|, -0.40 against the rank lower bound.
  - N_E(3e5): -0.96 against log|disc|, -0.33 against the rank lower bound.
- Canonical-height attribution (red team, rt_heights_output.json, floating point, listed sublattices):
  - Regulators: 3.75 (rank-7), 751 (GZ), 497 (BK).
  - The GZ deficit of 231x at H = 1e5 splits into about 6.3x lattice density and about 37x naive-height window loss.
  - The BK deficit of 5.4x splits into about 2.9x lattice density and about 1.8x window loss.

## Comparison

- Against the frozen success criterion: all four clauses are met on both trials, and no falsification clause fires. The frozen reading stands, and no amendment is made.
- Against the clauses' own power (D1, D2 below):
  - S3 (frac above 1.5 < 0.05) and S4 (no record-curve H_half at p >= 1000) are fixed by the counts and cannot fail for any reductions. So is the upper edge 1.2 of S2.
  - Meeting the criterion therefore carries evidence only through S1 and through S2's lower edge 0.8.
  - The lower edge excludes confinement of index about 4 or more at the median cell. Index 2 and 3 confinement would pass.
- S1 against its controls:
  - The same curve in another model with the same discriminant (rank-7, t = 1e6: 3 / 5) falls below GZ (5 / 11), so falsification clause F1 would fire with no change of curve (D3).
  - Rank-0 curves match or exceed GZ at H = 1e5: 11a1 has 5 and 210e2 has 16 (D4).
  - Only growth in H separates them. GZ goes 1, 3, 5, 11 over H = 1e4..3e5, while 11a1 and 210e2 stay flat.
- Counts against rank and against discriminant:
  - Across seven rank >= 7 curves the count follows |disc| (Spearman -1.00), not rank (-0.40).
  - At matched coefficient size the record curves carry 11 to 311 times the points of generic curves.
  - The BK/rank-7 ratio rises with H: 0.055, 0.144, 0.186, 0.199 at 1e4, 3e4, 1e5, 3e5. The EW rank >= 9 to rank-7 ratio goes 0.886, 0.981, 1.059 at 1e5, 3e5, 1e6. These are the directions a rank-helps-asymptotically reading predicts (E1).
- Coverage against nulls:
  - The observed median lies inside the frozen band and below the attainable maximum.
  - It lies above every uniform band, and above the same-height-rationals band for the pooled cells.
  - BK alone sits inside the same-height-rationals null (E2).
- DISC-1: the coordinator weighs it as benign. Every clause has the same truth value on the hypothesis's own cell set, with wide margin, and the median moves by 0.0030 / 0.0044. It is a specification gap that successor contracts must close.
- Against the coordinator prior: the prior was recorded in TASK-20261023-7b5dc6 before the red team ran. It read the low counts as a regulator effect, with coverage inheriting the a255fc instrument limit. Both readings are confirmed in direction. The prior did not anticipate two things: that N_E(H) depends on the model, and that window loss, not regulator, dominates the GZ deficit.

## Inference

### Derivation note (checkable step by step; a written argument, not a machine-checked proof)

**D1 (coverage cap; S3 and the upper edge of S2 cannot fail).**
1. Fix a cell with n points reduced into E(F_p), which has N_p points, and write x = n/N_p.
2. The uniform model expects m = N_p(1 - (1 - 1/N_p)^n) ≈ N_p(1 - e^{-x}) distinct residues.
3. Any point set has at most min(n, N_p) distinct residues. So the cell ratio is at most min(x,1)/(1 - e^{-x}).
4. For x <= 1 this bound is x/(1 - e^{-x}) = 1 + x/2 + x^2/12 + ..., which increases with x. For x >= 1 it is 1/(1 - e^{-x}), which decreases. The maximum is e/(e - 1) ≈ 1.582, at x = 1.
5. The bound exceeds 1.5 only for x in (0.875, ln 3 ≈ 1.0986).
6. The frozen cell set depends only on (n, N_p): the conditions are N >= 30 and model <= 0.9 N_p. It is therefore fixed before any reduction is looked at.
7. On RUN-CZLIFT-ca7450 only 6 of 131 cells have a cap above 1.5, and on RUN-CZLIFT-b1dce4 only 7 of 156. So frac above 1.5 is at most 0.046 / 0.045, below 0.05: S3 cannot fail.
8. A median is monotone in each element, so the median ratio is at most the median of the per-cell caps. That is 1.071 / 1.082, attained when every cell is injective (for example by the progression kG). This is below 1.2, so the upper edge of S2 cannot fail.

**D2 (S4 cannot fail).**
1. H_half(p) is the least grid H with distinct/N_p >= 1/2.
2. For p >= 1000, Hasse gives N_p >= p + 1 - 2√p >= 937.75, so N_p/2 >= 468.88.
3. On both record curves, distinct <= n <= N_E(3e5) <= 311 at every H <= hmax.
4. So no record-curve H_half exists at any prime p >= 1000. S4 restates the counts.

**D3 (N_E(H) at finite H is a property of the model, not of the curve).**
1. The substitution x = x' + t, y = y' (Weierstrass change with u = 1, r = t, s = 0) is an isomorphism over Q, with Δ' = u^{-12}Δ = Δ.
2. It therefore preserves the group E(Q), the rank, the torsion, the conductor, minimality, and the Néron-Tate height ĥ. With ĥ it preserves the regulator, and hence the Néron-Lang leading constant c_E. c_E is fixed by |E(Q)_tors|, r and Reg through the volume of a ĥ-ball.
3. The naive x-height H(x) = max(|a|, d^2) of x = a/d^2 is not preserved, because x' = x - t.
4. Asymptotically the naive and canonical heights differ by a model-dependent O(1). That shifts log H by O(1), and (log H + O(1))^{r/2} ~ (log H)^{r/2}, so the leading constant is unchanged.
5. At finite H the shift can dominate. Instance: the rank-7 curve has N_E(1e5) = 1155 in its reduced minimal model and 3 at t = 1e6, which is the same curve with the same discriminant.
6. Hence S1 is well defined only once the model is named; here, the reduced minimal model. Even then, S1 is not a statement about c_E or about rank.
7. The hypothesis's parenthetical "c_E falls with coefficient height although the rank is larger" names an invariant that this observable does not identify at H <= 3e5. The counts are pre-asymptotic: the GZ local exponent 2 dlogN/dloglogH is 17.3 between 1e5 and 3e5, against r = 8.

**D4 (a single-hmax count is rank-blind).**
1. By Mordell-Weil and Northcott, N_E(H) is bounded in H when the rank is 0 and unbounded when the rank is >= 1.
2. The observation N_E(1e5) = 5 has a rank-0 preimage (11a1: torsion Z/5, flat at 5 for H >= 30) and a rank >= 8 preimage (GZ).
3. 210e2 (rank 0) has 16, which exceeds GZ at both trials' hmax.
4. So "record curve below baseline at hmax" also holds with rank-0 baselines. The argument "fewer points at hmax, therefore higher rank does not buy small points" would conclude that a rank >= 8 curve has no more small points than a rank-0 curve, which D4.1 shows is false.
5. The separating observable is growth in H, which the specification marked uninformative.

### Empirical, post hoc (single reviewer implementation, not pre-registered)

- **E1 (discriminant, not rank).**
  - Over seven rank >= 7 curves, N_E(1e5) is perfectly anti-ordered by log|disc| and only weakly related to the rank lower bound.
  - At matched coefficient size the record curves are far richer than generic curves.
  - The record-to-rank-7 ratio rises with H, and EW rank >= 9 overtakes the rank-7 curve by H = 1e6.
  - The canonical-height attribution puts most of the GZ deficit on the naive-height window (about 37x) and a minority on lattice density net of the rank gain (about 6.3x).
  - Reading: these two 1977 models have large discriminants and large regulators, and their small-canonical-height points fall outside the naive window. The data do not say that higher rank buys fewer small points.
- **E2 (uniform reduction contradicted at instrument resolution).**
  - Against a uniform null built on the run's own cells, the observed median of 1.0424 lies about 24 null standard deviations above 1.0008, and top-cell collisions are well below the uniform expectation.
  - The frozen band's half-width (0.2) is about 118 null standard deviations, which is why the band could not see this.
  - A same-height-rationals null reproduces most of the excess and covers the BK cells. This is the arithmetic of small-height x mod p (Farey spacing), together with the reduction-homomorphism structure already recorded for lane 1 (EV-CZLIFT-376eee C2, D1-D4).
  - "Reduce uniformly / no structure in E(F_p)" is therefore contradicted as stated. It is not a resource for an attack.

### Reading for H-CZLIFT-27a184

- **Holds as an observation:** the measurable clauses, in the three named reduced minimal models at H <= 3e5. In those models, S1 holds and S2's lower edge holds (no gross confinement). S2's upper edge, S3 and S4 hold vacuously (D1, D2).
- **Not supported:** the hypothesis's interpretation.
  - The c_E parenthetical is not measured (D3).
  - The rank reading is blind (D4) and contradicted by E1.
  - The mechanism's "no structure" is contradicted as stated (E2).
  - The title's generalisation to "rank-record curves" is contradicted by the Elkies-Watkins rows.
- **Decision:** H-CZLIFT-27a184 is weakened.
- **Why not reject_scoped:** no frozen falsification clause fired, E1 and E2 are post hoc, and the D3 and D4 instances are not yet certificates. Rejecting on those grounds would amount to changing the criterion after the outcome.
- **What this does not change:** the obstruction to coverage-based global lifts is the rank-independent counting bound of EV-CZLIFT-376eee. Half coverage needs at least N_p/2 distinct global points, which is Omega(p) enumeration against O(√p) for rho. This run neither strengthens nor weakens that bound.
- **Resource check (EV-CZLIFT-b6fe48):**
  - Elkies-Watkins-style curves, with high rank and small discriminant, are rich in small points. So the lane is not closed for rank-record curves, only for these two 1977 models.
  - The BK H_half slope (0.147) is lower than the rank-7 slope (0.312), consistent with 2/r scaling.
  - Neither reading escapes the counting bound.

## Limitation

- Toy tier only: 16 primes p = 103..20011 (at most 15 bits) and naive x-height <= 3e5. Three named reduced minimal models, of which two are record curves. No transfer or extrapolation assumption is made: nothing here covers other models of these curves, other record curves, c_E, canonical-height counts, lifts whose rank grows with p, E(K), attack cost, or any deployed curve.
- E1 and E2 and the D3 and D4 instances come from one reviewer implementation (rt_lib.py, whose positive control reproduces the run). They were not pre-registered. The EW comparison uses one curve per rank.
- The red-team canonical heights are floating-point doubling limits, and the regulators are of listed sublattices of unknown index. The 6.3x / 37x attribution is approximate.
- Every rank label is a lower bound, including the rank-7 label (Elkies-Watkins footnote 3). "The record curves have larger rank" would need an upper bound on rank(382623908456a1) that no record establishes.
- The two trials are nested deterministic runs that share every point up to 1e5. They are not independent instances.
- check.py imports the driver, verifies only stored point samples, and does not test C1. The manifests omit the per-curve counts and h_half tables. Library versions and peak memory are not recorded.
- DISC-1 (saturation filter, upper median) is unstated in the specification and N_E is undefined there; neither changes a clause. The specification's status_note and the driver docstring give the LMFDB conductor bound as 500000; LMFDB reaches 299,996,953 with maximum rank 5. This is not load-bearing, and a correction record is pending.
- D1-D4 are a written derivation. The counterexample instances (rank-7 at t = 1e6; EW rank >= 9 at H = 1e6) are not yet packaged as certificates re-checked by independent code, so proof_status is `derivation`, not `certificate`.
