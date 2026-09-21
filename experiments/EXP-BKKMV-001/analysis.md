# EXP-BKKMV-001 analysis — BKK mixed-volume certificate for the target-sectioned Semaev family (candidate D2)

**Runs:** RUN-BKKMV-001-a (poly, valid), -b (counts m=3, valid), -c (counts m=4, valid),
-d (counts m=5 seeds 20260717–18, valid, harness-kill deviation recorded), -e (counts m=5 seed
20260719, valid), -f (m=5 negative control, valid). 6 sage invocations of budget 8; total wall ≈ 934 s of 2400 s.
System (frozen in `specification.yaml`): `Sys_m = { S_m(x_1..x_{m-1}, t_j) = 0 }`, j = 1..m−1,
n = m−1 equations in n unknowns; normalized mixed volume (BKK bound) by exact
inclusion–exclusion over Minkowski sums of exact Newton polytopes. Three seeded curves;
certification primes 1000003/1000033 (+QQ cross-check at m=3,4); count primes {101, 431, 1009}.

## 1. Exact mixed volumes (RUN-a; identical on all 3 curves, both cert primes, and QQ at m=3,4)

| m | n | sectioned support | MV (exact) | d_total | Bézout_total = dⁿ | MV/Bézout_total | Bézout_box = n!·(2^{m−2})ⁿ | MV/Bézout_box |
|---|---|---|---|---|---|---|---|---|
| 3 | 2 | 9 = 3² (full box) | **8** | 4 | 16 | 0.5 | 8 | 1.0 |
| 4 | 3 | 125 = 5³ (full box) | **384** | 12 | 1728 | 2/9 ≈ 0.222222 | 384 | 1.0 |
| 5 | 4 | 6561 = 9⁴ (full box) | **98304** | 32 | 1048576 | 3/32 = 0.09375 | 98304 | 1.0 |

Every section (lossless at the cert primes) is the **full box** [0, 2^{m−2}]^{m−1}; hence the
measured law on the tested range:

- `MV_m = (m−1)! · 2^{(m−1)(m−2)}` — exact at m = 3, 4, 5 (zero residual; 3-point certificate on the tested range only).
- `Bézout_total,m = ((m−1)·2^{m−2})^{m−1}` (measured total degrees 4, 12, 32 = (m−1)·2^{m−2}).
- `MV_m / Bézout_total,m = (m−1)! / (m−1)^{m−1}`: 1/2, 2/9, 3/32 — i.e. the Stirling factor ~ √(2π(m−1))·e^{−(m−1)}.
- `MV_m / Bézout_box,m = 1.000` exactly at all measured m (box/multi-graded saturation).

## 2. BKK cross-check vs actual F_p torus counts (RUN-b..f)

| m | p | seeds | torus counts (Semaev) | MV | holds? | N1 same-support counts | holds? |
|---|---|---|---|---|---|---|---|
| 3 | 101 | 3 | 0,0,0 | 8 | ✓ | 0,1,1 | ✓ |
| 3 | 431 | 3 | 0,0,4 | 8 | ✓ | 2,1,1 | ✓ |
| 3 | 1009 | 3 | 0,0,4 | 8 | ✓ | 2,1,1 | ✓ |
| 4 | 101 | 3 | 0,0,0 | 384 | ✓ | 2,0,0 | ✓ |
| 4 | 431 | 3 | 0,0,0 | 384 | ✓ | 1,1,2 | ✓ |
| 4 | 1009 | 3 | 0,0,0 | 384 | ✓ | 1,1,0 | ✓ |
| 5 | 101 | 3 | 0,0,0 | 98304 | ✓ | 1 (seed 20260719 only) | ✓ |

No BKK violation in any of the 21 Semaev cells or 19 same-support cells. Boundary (x_n = 0)
counts were 0 throughout and are outside BKK scope anyway. The bound is extremely loose over
these fields (expected O(1) rational points vs MV up to 98304): **the cross-check certifies
the pipeline (a violation would have flagged a bug) but has low statistical power** — recorded
honestly as a limitation, not hidden.

## 3. Controls (all pass)

- **P1 dense simplex**: pipeline MV = dⁿ exactly for (n,d) ∈ {(2,2),(2,4),(3,4),(4,8)} ✓
- **P2 hand value**: m=3 sectioned support = full 3×3 grid, MV = 8 (hand-derived), all curves ✓
- **P3 BKK bound**: count ≤ MV in every counted cell (table above) ✓
- **P4 support stability**: supports identical at p = 1000003 vs 1000033 (m=3,4,5) and vs QQ (m=3,4, same integer A,B) ✓
- **N1 same-support (random coefficients)**: MV identical to Semaev MV in every instance (support-only dependence; no EC leakage into MV) ✓; same bound holds for their counts ✓
- **N2 violation witness**: repeated-section (positive-dimensional) systems give counts ≫ MV — m=3/p=431: 431, 438, 442 vs MV 8; m=4/p=101: 8962, 10490, 7820 vs MV 384 ✓ (detector has teeth)
- **N3 engine selfcheck**: numpy engine ≡ naive enumeration on (m=3, p=101, seed 20260717) ✓

## 4. Promotion-gate arithmetic (D2 gate: “a proved or 3-point-certified growth law with an exponent statement; ambiguous fits (CI spanning the Bézout rate) do not count”)

Measured (exact integers, no statistical noise; uncertainty is extrapolation risk, not a CI):

- log2 MV_m: 3.000, 8.585, 16.585 → increments +5.585, +8.000 bits/step.
- log2 Bézout_total: 4.000, 10.755, 20.000 → increments +6.755, +9.245 bits/step (strictly larger at both measured steps).
- log2 MV / log2 Bézout_total: 0.750, 0.798, 0.829 (< 1 at all measured m, increasing toward 1).
- MV/Bézout_total: 0.5, 0.2222, 0.09375 = (m−1)!/(m−1)^{m−1} (decreasing; Stirling-rate e^{−(m−1)}√(2π(m−1)) if the pattern persists).
- MV/Bézout_box: 1.000, 1.000, 1.000 (exact box saturation at all measured m).
- B2 sibling gate for reference: “MV/Bézout ≤ 0.85 at m=5” → 0.09375 vs total-degree Bézout; 1.000 vs multi-graded box Bézout. B2 disproof track: “ratio ≥ 0.95 at m=5” → met vs box, not vs total.

**What the 3 points certify (and what they do not):** on the tested range the three MV values
lie exactly on `MV_m = (m−1)!·2^{(m−1)(m−2)}` (full-box sectioned supports), with exact
zero-residual agreement on 3 independent curves × 2 cert primes (+QQ at m ≤ 4). This is a
3-point-certified growth law with an exponent statement on m ∈ {3,4,5}. It does **not** prove
the law for m ≥ 6; the certificate’s extrapolation is a theorem-track question, not a
measurement. Both Bézout conventions are reported because the gate’s direction flips with the
convention (box: saturated, ratio 1; total: ratio → 0 with an exact rate). The Coordinator owns
the interpretation.

## 5. Deviations from protocol (all recorded)

1. **RUN-d harness kill**: the 300 s foreground cap of the execution harness killed the tool
   wrapper at ~300 s; the sage process finished at 316.6 s (in-script clock) and wrote intact,
   verified artifacts. Not the experiment’s 600 s budget; not evidence about the hypothesis.
   Mitigation for RUN-e/f: single-seed invocations (~155–165 s).
2. **m=5 counts only at p=101** (pre-registered `count_scope`; enumeration of (F_p*)³ at p ≥ 431
   exceeds the per-run budget). m ∈ {3,4} counted at all three primes.
3. **Section losses at p=101 for m=5** ([30,12,12,28], [24,48,28,22], [0,16,24,18] of 6561):
   12-candidate policy kept maximal-support sections; all lost monomials are hull-interior —
   exact mixed volume of the actual shrunken supports still 98304 (verified through the full
   inclusion–exclusion, not assumed).
4. **N1 count at m=5 for one seed only** (20260719; budget). N1 MV-equality holds for every instance at every m.
5. **m=6,7 not attempted** (budget; Coordinator mitigation 2026-07-18). Unsectioned m=5 polytope
   volume skipped by design (5D, 54777 points; support size + full-box status recorded instead).
6. Script gained a `--neg-only` flag after RUN-d (skips only the Semaev `count_torus` call;
   RNG streams and all other code paths unchanged; determinism re-verified: RUN-e/f section
   streams identical).

## 6. Unexpected observations (rule 8)

- **Saturation dichotomy**: the *unsectioned* S_m is NOT box-saturated (supports 13 < 27,
  439 < 625, 54777 < 9⁵ = 59049 for m = 3,4,5; unsectioned polytope volumes 14/3 ≈ 4.67 < 8
  and 5423/24 ≈ 225.96 < 256 vs the [0,2]³ and [0,4]⁴ box volumes at m = 3,4), yet **every
  single-variable section IS the full box** (lossless at large primes on all curves).
  Specialization fills the Newton polytope. This is itself a structural fact about the
  Semaev family worth a ledger note.
- MV equals the multi-graded box Bézout *exactly* (the system is saturated in the (P¹)^{m−1}
  sense) while sitting far below the total-degree Bézout number — the “MV vs Bézout” question
  is entirely convention-dependent on this family.
- All torus counts were ≤ 4; zero in 18 of 21 Semaev cells — expected (O(1) heuristic) but the
  uniformity is notable.

## 7. Validity

`valid`. All controls pass; no invalidation rule triggered; the one infrastructure event
(RUN-d harness kill) is recorded and did not affect artifacts. Toy scope only: primes ≤ 1009
for counts, ~2²⁰ for certification; nothing here is a crypto-scale claim.
