# EXP-BKKMV-002 analysis — m=6 mixed-volume law check (candidate D2 continuation, task BKKM6)

**Runs:** RUN-BKKMV-002-a (validate, valid, 39/39 controls), -b (m=6 @ p=1000003, 3 seeds, valid),
-c (m=6 @ p=1000033, 3 seeds + determinism, valid), -d (BKK counts m≤5 + N2/N3, valid).
4 sage invocations of budget 10; total run wall ≈ 291.6 s of 3300 s (plus dev probes ≈ 322 s,
of which 290 s was the killed symbolic-feasibility probe — infrastructure, see §5).
System and law frozen in `specification.yaml`; the law tested is the EXP-BKKMV-001 certificate
`MV_m = (m−1)!·2^((m−1)(m−2))` with `MV/Bezout_box = 1` (full-box sectioned supports).

## 0. The m=6 instrument (why it is a measurement, not a fit)

Brute support enumeration of the symbolic S_6 is infeasible (dev/probe_symbolic6: one sectioned
resultant ran > 276 s without completing and was killed — censored, infrastructure). Per the D2
mitigation (research_directions_20260717.md line 670) the experiment uses the **fiberwise/recursive
structure**: for each section t_j, `f_j(x_1..x_5) = Res_X(A, B_j)` with `A = S_5(x_1..x_4, X)`
(deg_X 8) and `B_j = S_3(x_5, t_j, X)` (deg_X 2). The engine evaluates A's nine X-coefficients on a
17⁴ tensor grid by exact modular tensor contraction of the exact S_5 coefficient tensor,
computes f_j on the 17⁵ grid by the exact formal-Sylvester identities (companion-matrix form
`b_2^8·det(A(C_B))` plus the two degenerate-b_2 forms — all verified against the formal 10×10
Sylvester determinant on 6000 random instances in dev/probe_kernel.sage, K1/K2a/K2b pass), then
recovers **all 1,419,857 coefficients exactly** by tensor-grid interpolation mod p (K4 round-trip
pass). The support is the exact nonzero set of the true sectioned polynomial mod p — no sampling,
no fitting, no floating point in the certification path.

Engine certification before any m=6 number was trusted (RUN-a):
- **P4a**: fiberwise supports == symbolic supports **exactly** in all 12 validation cells
  (m = 3,4,5 × 3 seeds @ p=1000003, and m = 3,4,5 @ p=101 seed 20260717), including the lossy
  p=101 m=5 cell whose supports [6531, 6549, 6549, 6533] with 12–30 interior holes were matched
  point-for-point. Engine seconds per m=5 section: 0.03.
- **P5a**: all 6561 grid values of an m=5 section == per-point formal Sylvester determinants
  computed from independent Sage substitutions (0 mismatches).

## 1. Measured m=6 numbers vs prediction (RUN-b, RUN-c; 6 instances = 3 curves × 2 primes)

| quantity | prediction (law) | measured (all 6 instances) | residual |
|---|---|---|---|
| sectioned support per section | full box [0,16]⁵ = 1,419,857 | 1,419,857 (28 of 30 sections); 1,419,797 and 1,419,827 on two sections (hull-interior losses, corners intact) | 0 (see §6) |
| corners present (hull = box) | 32/32 every section | **32/32 on all 30 sections** | 0 |
| **MV_6** | **125,829,120** | **125,829,120 on 6/6 instances** | **0** |
| d_total sectioned | 80 | 80 (every section, incl. both lossy ones) | 0 |
| Bezout_total = dⁿ | 3,276,800,000 | 3,276,800,000 | 0 |
| Bezout_box = 5!·16⁵ | 125,829,120 | 125,829,120 | 0 |
| MV/Bezout_box | 1.0 | **1.0 exactly on 6/6** | 0 |
| MV/Bezout_total | 0.0384 | 24/625 = 0.0384 exactly on 6/6 | 0 |

MV by exact inclusion-exclusion over the 31 subset Minkowski sums of the certified hull boxes,
cross-checked by the box permanent (equal in every instance). Section t-values per the EXP-BKKMV-001
stream formula (m=6): e.g. seed 20260717/p=1000003: t = [729778, 153347, 488561, 735750, 739084];
tries per slot 1–4 (QR/duplicate rejections only; no corner-deficit retries were needed anywhere —
run notes empty in both runs).

## 2. Growth law extended to m=6 (promotion-gate arithmetic, D2 gate)

| m | n | sectioned support | MV (exact) | d_total | Bézout_total | MV/Bézout_total | Bézout_box | MV/Bézout_box |
|---|---|---|---|---|---|---|---|---|
| 3 | 2 | 9 = 3² | 8 | 4 | 16 | 1/2 | 8 | 1.0 |
| 4 | 3 | 125 = 5³ | 384 | 12 | 1,728 | 2/9 | 384 | 1.0 |
| 5 | 4 | 6,561 = 9⁴ | 98,304 | 32 | 1,048,576 | 3/32 | 98,304 | 1.0 |
| **6** | **5** | **1,419,857 = 17⁵** | **125,829,120** | **80** | **3,276,800,000** | **24/625** | **125,829,120** | **1.0** |

- log2 MV: 3.000, 8.585, 16.585, **26.907** → increments +5.585, +8.000, **+10.322** bits/step
  (= log2(5·2⁸) = log2 1280 exactly at the new step).
- log2 Bézout_total: 4.000, 10.755, 20.000, **31.609** → increments +6.755, +9.245, **+11.609** —
  strictly larger than MV's at all three measured steps.
- MV/Bézout_total: 1/2, 2/9, 3/32, **24/625** = (m−1)!/(m−1)^(m−1) at m=6 (120/3125 reduced) —
  the exact Stirling-form decay persists at the 4th point.
- log2 MV / log2 Bézout_total: 0.750, 0.798, 0.829, **0.851** (< 1, increasing toward 1, as before).
- MV/Bézout_box: 1.000, 1.000, 1.000, **1.000** — box saturation persists at m=6.

The 3-point certificate is now a **4-point certificate on the tested range m ∈ {3,4,5,6}**, zero
residual, 3 curves × 2 cert primes at m=6 (12 section polynomials per curve-prime pair… 5 sections
× 6 instances = 30 measured sections). It still does not prove the law for m ≥ 7 (theorem-track).

## 3. Controls (all pass)

- **P1 dense simplex**: pipeline MV = dⁿ exactly for (n,d) ∈ {(2,2),(2,4),(3,4),(4,8)} ✓
- **P2 hand value**: m=3 sectioned support = full 3×3 grid, MV = 8, all curves ✓
- **P4a engine cross-validation**: 12/12 exact support matches fiberwise vs symbolic (§0) ✓
- **P4b two-prime hull stability**: box conclusion + MV_6 identical at p=1000003 and p=1000033,
  all 3 seeds ✓ (literal supports differ in hull-interior positions on two sections — expected
  finite-p coefficient vanishing, pre-registered adaptation; hulls stable)
- **P4c determinism**: (seed 20260717, p=1000003, slot 1) recomputed in RUN-c: same t = 729778,
  same bitmap sha256 as RUN-b ✓
- **P5 value spot-checks**: P5a 6561/6561 (m=5 full grid); P5b 48/48 seeded-random grid points at
  m=6 vs per-point formal Sylvester determinants from independent Sage substitutions, at both
  cert primes (0 mismatches) ✓
- **P3 BKK bound (real sectioned systems, m ≤ 5)**: m=4 p=101 ×3 seeds: torus counts 0,0,0 ≤ 384 ✓;
  m=5 p=101 seed 20260717: torus count 0 ≤ 98,304 ✓ (count took 75.5 s). m=6 counts **censored
  pre-registration** (enumeration > 10¹⁰ point-evals; MV_6 = 1.26×10⁸ makes it near-vacuous).
- **N1 same-support**: random-coefficient MV == Semaev MV in all 12 classical cells (m=3,4,5) ✓;
  at m=6 the MV engine consumes supports only, so coefficient-independence is structural (recorded).
- **N2 violation witness**: repeated-section m=3 p=431 count 431 ≫ MV 8 ✓ (detector teeth)
- **N3 engine selfcheck**: numpy == naive at (m=3, p=101) ✓
- **P6 symbolic cross-check**: **CENSORED** (infrastructure): dev/probe_symbolic6's single
  sectioned symbolic resultant did not complete within the 290 s harness cap (S_5 build 3.6 s,
  resultant started at 13.9 s, killed at 290 s). Not evidence about the hypothesis. Engine
  certification above stands in its place.

## 4. Cost model (what m=6 takes fiberwise; what m=7 would take)

Measured per m=6 instance (RUN-b/c): total ≈ 15–17 s = symbolic S_5 build ≈ 13.7 s (dominant) +
A-tensor contraction ≈ 1 s + 5 sections × ≈ 0.3–0.5 s (values + interpolation) + MV < 0.1 s.
The fiberwise engine is > 100× cheaper than the (censored) symbolic resultant path at m=6.
**m=7 estimate (not attempted, out of scope):** the blocker is the A-tensor of S_6 itself
(symbolic S_6 infeasible per the probe); it would have to be built fiberwise too (interpolate
S_6's own tensor from sectioned values on a 33⁵ grid, then 6 sections on 33⁶ grids; bitmaps of
33⁶ ≈ 1.29×10⁹ bits ≈ 161 MB packed per section). Plausible at ~10–30× the m=6 cost but with
> 100× memory pressure; no budget impact claimed here — recorded as the cost model required by
the handoff's censoring clause (which was not triggered: m=6 completed).

## 5. Deviations from protocol (all recorded)

1. **Section policy adapted** (pre-registered in specification.yaml): the EXP-BKKMV-001
   lossless-vs-projection acceptance test requires the unsectioned S_6 projection (infeasible);
   replaced by corner-presence acceptance with a ≤12-candidate fallback per slot. All 30 slots
   accepted corner-complete candidates; fallback never triggered (tries > 1 were QR/duplicate
   rejections only).
2. **P6 censored** (§3): single-section symbolic resultant > 276 s, killed by harness cap.
   Infrastructure event, not evidence (rule 5).
3. **m=6 torus counts censored** (pre-registered; BKK cross-check carried by m=4 ×3 and m=5 ×1
   real systems).
4. **QQ cross-check at m=6 not done** (handoff: "QQ or two-prime if cheap"): two-prime stability
   delivered on all 3 seeds; QQ interpolation would need rational reconstruction of 1.4M
   coefficients — not cheap.
5. **Unsectioned S_6 support not computed** (symbolic S_6 infeasible per probe); the m≤5
   saturation dichotomy stands on the EXP-BKKMV-001 record. As partial m=6 evidence: the
   union of the 5 sectioned supports is the full box [0,16]⁵ in every instance (union_missing
   = 0), so the unsectioned projection is box-saturated even if the unsectioned support is not.
6. **Git HEAD moved during the task** (99693e3b at spec time → 9df2118d at run time): the
   concurrent coordinator session committed independently; this executor made no commits and
   wrote only inside experiments/EXP-BKKMV-002/ and ledger/EV-BKKMV-002.yaml. run_meta records
   git_commit = 9df2118d, dirty_tree = true.

## 6. Unexpected observations (rule 8)

- **First coefficient-vanishing at certification primes**: 2 of 30 m=6 sections lost hull-interior
  monomials — seed 20260719/p=1000003/sec3 (t = 927047): 60 of 1,419,857; seed 20260718/p=1000033/sec1
  (t = 16713): 30. EXP-BKKMV-001 saw zero losses at cert primes for m ≤ 5 (1.4M coefficients, each a
  degree-≤16 polynomial in t, makes O(10–60) losses per section likely at p ~ 2^20 — the
  pre-registered expectation matched quantitatively). Both events left all 32 corners intact;
  hulls and MV unchanged; the lost positions are prime/section-specific (no structural pattern
  evident in the recorded first-8 lists). This is exactly the m=5/p=101 phenomenon of
  EXP-BKKMV-001 surfacing at large p for the first time — relevant to the theory track: sections
  are box-saturated **as hulls** at finite p, while literal support saturation is a
  characteristic-0/generic-t statement.
- **Unsectioned S_5 at p=101 loses support too**: RUN-a records unsectioned support 54,477 < 54,777
  (cert-prime value) at p=101 — small-p structural vanishing inside the unsectioned polynomial,
  previously only recorded for sections.
- **Full-box bitmaps are byte-identical across all lossless sections and instances**
  (sha256 c21a67725eb9…) — trivially expected (same box shape), recorded for the validator.
- The m=6 P5b engine values agreed with the formal Sylvester ground truth on all sampled points
  at both primes, including points where a_8(x_1..x_4) = 0 (formal-vs-actual degree factor
  b_2 handled per K1) — no anomaly.

## 7. Validity

`valid`. All controls pass (39/39, 1/1, 2/2, 6/6 across RUN-a..d); no invalidation rule triggered;
the one infrastructure event (symbolic-probe kill) is recorded and touched no artifact. Toy scope
only: primes ≤ 1009 for counts, ~2^20 for certification; nothing here is a crypto-scale claim
(rule 7). The m=6 measurement closes exactly the pre-registered scope: 3 seeded curves ×
p ∈ {1000003, 1000033}, m = 6, target-sectioned Semaev systems.
