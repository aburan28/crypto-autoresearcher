# EXP-INCB-001 analysis — D3: incidence-richness ceiling for EC chord arrangements

**Canonical run:** `RUN-INCB-001-b` (valid). `RUN-INCB-001-a` retained, marked invalid (serializer defect in 4 non-primary fields; statistical content verified identical to RUN-b — see Deviations).
**Protocol:** `specification.yaml` (frozen). p ∈ {211, 1009, 4099}; seeds 20260717..20260722 (6/6 completed, no timeout; wall ≈ 5 s total).
**Curves (seeded, ordinary):** p=211: y²=x³+7x+62, n=210, B grid [8]; p=1009: y²=x³+921x+976, n=984, B grid [10, 16]; p=4099: y²=x³+211x+1972, n=4056, B grid [8, 16, 28]. (Grid rule: round-half-up of n^1/4, n^1/3, n^2/5, deduped, B ≥ 8; at p=211 the 1/4- and 1/3-power points fall below 8 and are excluded by the A2 rule, leaving one cell.)
**Semantics:** FB = x-set of size B (A2 semantics); incidence point set = all lifts (±y), M = 2B. Arrangement = all distinct lines through pairs of distinct points (verticals included; tangents excluded). c_r = # lines with exactly r points. τ̂ = −OLS slope of log c_r vs log r over {r ≥ 2 : c_r > 0}; null if < 2 support points. z = |τ̄_ec − τ̄_rand| / √(se_ec² + se_rand²).

## Measured results (6 seeds per cell; τ̂ = mean ± SE, k = # fittable seeds)

| p | B | M | τ̂ EC | τ̂ random | τ̂ grid | z_ec_vs_rand | c̄₃ EC | c̄₃ random | c̄₃ grid | excess ratio c₃ |
|---|---|---|---|---|---|---|---|---|---|---|
| 211 | 8 | 16 | 9.05 ± 0.53 (k=4) | 9.55 ± 0.62 (k=6) | 2.517 ± 0 (k=6) | **0.611** | 2.0 | 2.67 | 4.0 | 0.75 |
| 1009 | 10 | 20* | 11.06 ± 0.09 (k=3) | 12.50 ± 0.34 (k=5) | 2.958 ± 0.04 (k=6) | **4.079** | 1.0 | 1.0 | 8.2 | 1.0 |
| 1009 | 16 | 32* | 12.04 ± 0.52 (k=6) | 11.75 ± 0.38 (k=6) | 3.086 ± 0.01 (k=6) | **0.441** | 4.0 | 4.33 | 27.7 | 0.92 |
| 4099 | 8 | 16 | null (k=0) | null (k=0) | 2.517 ± 0 (k=6) | n.c. | 0.0 | 0.0 | 4.0 | n/a |
| 4099 | 16 | 32 | 13.57 ± 0 (k=4) | 14.00 ± 0.83 (k=4) | 3.092 ± 0 (k=6) | n.c. (surrogate 0.52) | 1.33 | 1.33 | 28.0 | 1.0 |
| 4099 | 28 | 56 | 14.11 ± 0.74 (k=6) | 13.38 ± 0.22 (k=6) | 3.295 ± 0 (k=6) | **0.954** | 6.0 | 6.83 | 80.0 | 0.88 |

*one seed (20260721, p=1009) hit a y=0 (2-torsion) x, giving M=19/31 for that instance; controls matched to actual M. n.c. = not computable as predeclared (see below).

## Gate arithmetic (candidate D3 quantitative promotion gate: z > 3 at ALL three sizes p)

| cell | z | > 3? |
|---|---|---|
| (211, 8) | 0.611 | no |
| (1009, 10) | 4.079 | yes — direction τ̂_ec < τ̂_rand (EC profile shallower); see caveat |
| (1009, 16) | 0.441 | no |
| (4099, 8) | not computable (no 3-rich line in either family, all 6 seeds → no fittable exponent) | no |
| (4099, 16) | not computable as predeclared (se_ec = 0: the 4 fittable EC seeds give identical τ̂); surrogate |Δ|/se_rand = 0.52 | no |
| (4099, 28) | 0.954 | no |

**Gate result: NOT crossed.** Only 1 of 6 cells exceeds 3 SE, at the smallest-B cell of the middle prime; the all-three-sizes condition fails decisively (p=211: 0.611; p=4099: ≤ 0.954). Caveat on the (1009, 10) crossing: c̄₃ is identical for EC and random there (1.0 vs 1.0; excess ratio 1.0). The z = 4.08 arises because only k=3 EC seeds are fittable (the 3 with c₃ = 2) vs k=5 random seeds (mostly c₃ = 1), and the 3 EC τ̂ values happen to be near-identical (se = 0.09). It is a conditioning-on-c₃>0 / low-count artifact of the fit at mean c₃ = 1, not a measured richness difference; the first-moment metric (c̄₃) shows none.

**First-moment metrics (unaffected by fit conditioning):** excess ratio c̄₃_EC/c̄₃_rand = 0.75, 1.0, 0.92, n/a, 1.0, 0.88 — at or below 1 in every cell. EC 3-rich-line counts also run slightly below their own first-moment prediction C(M,2)·(B/L)/3 at every fittable cell (measured/pred ≈ 0.66–0.85). No curve-specific excess of rich lines is visible in any cell; the consistent mild deficit is within ~2 SE everywhere and is recorded, not explained.

## Controls

- **Negative (random null): PASS.** Measured random-family triple count T vs exact prediction C(M,3)·(p−2)/(p²−2): deviations 0.061, 0.385, 0.694, —, 0.202, 0.123 SE across the 6 cells — all ≤ 3. At (4099, 8) the SE is 0 (T = 0 in all 6 seeds); per-instance expectation 0.137 gives P(all six zero) = e^(−6·0.137) ≈ 0.44 — consistent. No leakage or pipeline artifact.
- **Positive (grid sensitivity): PASS with recorded formula deviation.** The predeclared z_grid > 3 criterion is computable in 2/6 cells: z_grid = 27.8 (1009, 10) and 22.6 (1009, 16). In the other 4 cells the formula is undefined because the deterministic grid has zero seed-variance (se = 0) or the random family has no fittable exponent. Surrogate separations are overwhelming in all 4: |2.517 − 9.549|/0.62 ≈ 11.3 (211); |3.092 − 13.995|/0.83 ≈ 13.2 (4099, 16); |3.295 − 13.376|/0.22 ≈ 46 (4099, 28); and at (4099, 8) c̄₃_grid = 4.0 vs c̄₃_rand = 0.0 with max richness 4 vs 2. The measurement resolves richness excess whenever present.

## Deviations from protocol

1. **RUN-a serializer defect (recorded, corrected).** Script revision 1's JSON default handler `int()`-truncated Sage `RealNumber` values. Corrupted fields: per-instance `wall_ms`, `wall_seconds_total`, `pred_c3_ec`, `pred_c3_ec_mean` (2 resource-timing + 1 secondary prediction + its mean). All hypothesis-relevant content — curves, x-sets, histograms, τ̂ fits, statistics, z scores, gate block — verified **field-identical** between RUN-a and the corrected RUN-b. RUN-a retained with validity_status: invalid; RUN-b is canonical. In-script wall time for RUN-a is unrecoverable (truncated to 0); shell wall time (2.857 s) is recorded.
2. **Positive-control z formula undefined in 4/6 cells** (deterministic grid ⇒ zero variance; or null random fits). Sensitivity evaluated by surrogates as above; the formula, not the measurement, is what failed.
3. **τ̂ is frequently un-fittable at toy scale** (no line with r ≥ 3 ⇒ < 2 support points): (4099, 8) has no fittable EC or random exponent in any seed. This is intrinsic to the frozen primes/B-rule, recorded as scope.

## Unexpected observations (rule 8)

- (a) The serializer defect above (caught only because a timing field was absurdly 0).
- (b) p=1009, seed 20260721: the seeded x-set contains a 2-torsion x (y = 0) at both B = 10 and B = 16, so M = 19/31 instead of 20/32 for that seed; protocol handled it (M recorded per instance; controls matched).
- (c) The (1009, 10) gate-cell crossing described above: a > 3 SE τ̂ separation with identical c̄₃ — a pure fit-conditioning artifact, flagged so it is not read as an excess signal.
- (d) EC 3-rich-line counts fall consistently ~15–35 % below the uniform-x heuristic prediction at all fittable cells (within noise individually; systematic in sign).
- (e) EC arrangements carry exactly B vertical 2-rich lines (the ±y pairs), an x-set-semantics offset that inflates EC c₂ relative to a matched random set; it does not affect r ≥ 3 richness.

## Scope and limitations

Toy primes (p ≈ 2^8–2^12), one seeded ordinary curve per prime, x-set factor bases of B ≤ 28 (M ≤ 56 points), 6 seeds. Richness mass is concentrated at r ∈ {2, 3} at these sizes, so the fitted exponent is effectively a two-point fit dominated by c₃ noise; the exponent comparison and the c̄₃ first-moment comparison agree (no separation beyond noise). Per docs/negative-result semantics: **no improvement meeting the predefined threshold was observed over the tested instances, parameters, and budget** — this closes only the tested scope and says nothing about crypto-scale fields, other curve families, or proved bounds (the candidate's alternative "proved bound" gate path is not attempted here; the theorem note `research/THM_INCBARRIER1.md` named in the candidate's reproduction artifacts is outside this task's file boundaries).

## Reproduction

Exact command (from repo root): `sage experiments/EXP-INCB-001/incbarrier1_richness.sage > experiments/EXP-INCB-001/runs/RUN-INCB-001-b/raw.json 2> experiments/EXP-INCB-001/runs/RUN-INCB-001-b/stderr.txt` — fully deterministic (seeds in `specification.yaml`); re-running regenerates raw.json identically except resource-timing fields. SageMath 10.9, Python 3.14.3, macOS arm64. Wall ≈ 5 s (in-script 0.872 s).
