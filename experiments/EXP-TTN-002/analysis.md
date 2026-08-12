# EXP-TTN-002 analysis — m=6 bond-rank certificate for the Semaev recursion tensor

**Canonical run:** `RUN-TTN-002-c` (valid). `RUN-TTN-002-a` and `-b` retained as
`valid_with_defect` (control-side defects only — an int64 overflow in one control's
evaluation at p=1009, and an under-corrected degree-drop convention in another; both
caught by the controls themselves, diagnosed, fixed; all measurements identical across
-a/-b/-c; see manifests). 9 cells: `p ∈ {101, 431, 1009}` × seeds `{20260717, 20260718,
20260719}`. 104.8 s wall < 600 s cap; stderr empty; no stopping rule hit.

**Object.** `S_6` := formal-degree Sylvester resultant `Res_X(S_3(x1,x2,X), S_5(X,x3..x6))`
(EXP-TTN-001 definition), per-variable degree `d = 16`, tensor side 17. The full tensor
(17^6 ≈ 24.1M entries) is never materialized; ranks are certified via explicit
Sylvester-structure factorizations:

- **Root bond** `{x1,x2}|{x3,x4,x5,x6}`: the 10×10 Sylvester expansion gives
  `S_6 = Σ_M c^M(x1,x2)·H_M(x3..x6)` over the **45** multisets M of 8 factors from
  `{c0,c1,c2}` (extraction: 95 nonzero (M,K) terms; self-check C2 vs plain GE dets 3/3
  per prime). Hence rank ≤ 45 **by construction**; equality ⟺ both factor families are
  independent, certified by full-rank sampled factor matrices.
- **Child bond** `{x1,x2,x3}|{x4,x5,x6}` (also the m=6 EXP-TTN-001 "balanced split"
  growth-family bond): the balanced recursion `S_6 = Res_X(S_4(x1,x2,x3,X), S_4(X,x4,x5,x6))`
  (identity verified pointwise, control C1) gives `S_6 = Σ_{M,N} s_{MN} a^M b^N` with a
  70×70 integer sign matrix S (221 nonzero terms). Hence rank ≤ 70; with independent
  factor families, rank = rank(S).

## 1. Measured ranks vs the χ(6) = 45 prediction

Identical values in **all 9 cells** (3 primes × 3 seeds; field-size independence holds,
β = 0 continuation of EV-TTN-001):

| bond | split | flattening | law prediction | measured | certificate |
|---|---|---|---|---|---|
| **root** (mechanism bond of the χ law) | {x1,x2}\|{x3..x6} | 289 × 83521 | **45** = C(10,2) | **45** | EXACT: ≤45 structural + rank(CM)=rank(HM)=45 all cells (+ rank(E)=45 minor; CUR exact) |
| **child** (= growth-family balanced split) | {x1,x2,x3}\|{x4,x5,x6} | 4913 × 4913 | law face-value 45; balanced-multiset count 70 = C(8,4) | **68** | rank(E)=68 exact lower bound + form rank rank(W_A·S·W_Bᵀ)=68 in all cells, two independent samples per cell; factor spans 69/70 (one syzygy, §3); rank(S)=70 mod all p and over QQ |
| grandchild (symmetry probe) | {x1..x4}\|{x5,x6} | 83521 × 289 | 45 iff S_6 symmetric | **45** | rank(E)=45 |
| single-var (context) | {x1}\|rest | 17 × 17^5 | 17 (full) | **17** | rank(E)=17 |

**χ(6) arithmetic.** On the mechanism bond family (root of the left-comb recursion,
the family for which the Sylvester-multiset mechanism gives `χ(m) = C(2^{m-3}+2, 2)`),
the law holds **exactly** at m=6: χ(6) = 45 = C(10,2). The extrapolated in-window
slope on that family (3, 6, 15, 45 at d = 2, 4, 8, 16) continues toward asymptotic
exponent 2 (disproof region per DEC-20260718-008's framing): adding the m=6 point,
a 4-point least-squares slope of log₂χ vs log₂d is **1.3043**
(up from 1.1610 on the m ≤ 5 window of EV-TTN-001; two-point m=5→m=6 root slope:
log₂(45/15) = **1.5850**). Still an in-window fit, not an asymptotic statement.

On the **growth-family (3|3 balanced) reading**, the law's face value 45 does **not**
hold at m=6: the measured 3|3 bond rank is 68. m=6 is the first size where the two
readings of the χ law diverge (at m=3,4,5 the growth-family bond equals or matches a
mechanism bond by symmetry: 1|2↔2|1, 2|2, 2|3). The naive balanced-multiset count 70
also fails, because of the syzygy in §3: 70 − 1 (one relation per side) − 1
(degeneracy of the restricted form) = 68. Which of the two drops is the generic
phenomenon at larger m is OPEN (theory follow-up).

## 2. Controls (all pass, 9/9 cells unless noted)

- **P1** S_3 baseline: 20/20 seeded curve-point triples satisfy S_3 = 0 per curve.
- **P2** coefficient paths: S_4 X-coeff path == direct per-point 4×4 Sylvester dets
  (200/200 per cell) and == symbolic formal S_4 (64/64 per cell); S_5 X-coeff path ==
  symbolic formal S_5 (512/512 per cell, staged mod-p-reduced diagonal contraction).
  Symbolic S_4/S_5 term counts 439 / 54 377–54 777 — match EV-TTN-001 exactly.
- **C1** three independent evaluation paths agree: comb expansion == balanced expansion
  at 2048 seeded points per cell (0 mismatches, 9/9 — this also verifies the
  recursion-associativity identity `S_6_comb ≡ S_6_bal` used for the child ≤ 70 bound);
  comb == fully-nested sage resultants (padded to formal degree at each level) 64/64
  per cell, including points with actual-degree drops.
- **C2** extraction self-check: both Sylvester expansions == plain GE determinants,
  3/3 random coefficient points per prime.
- **C3** rank(E_bond) == rank(W_L·FORM·W_Rᵀ) at every cell, both bonds (linear-algebra
  consistency of the certificate machinery).
- **P3** prefix-CUR exact at full rank on E_root in every cell (mirrors EXP-TTN-001 P3).
- **N1** random 96×96 matrices rank 96 every cell; **N2** planted rank-45 bilinear
  forms recovered as 45 every cell.

## 3. Unexpected observations (rule 8)

1. **A universal degree-4 syzygy among S_4's X-coefficient polynomials.** The 70
   products `a^M` (multisets of 4 from `{a_0..a_4}(x1,x2,x3)`, the X-coefficients of
   S_4) satisfy exactly **one** F_p-linear relation — factor-span 69, not 70 — in every
   one of the 9 cells (all primes, all curves), confirmed by a documented redraw
   (128 points, second stream) reproducing the *identical* witness vector in every
   cell, and with the A-side and B-side witnesses identical to each other in every
   cell. Geometrically: the image of (x1,x2,x3) ↦ (a_0:…:a_4) ∈ P⁴ lies on a single
   quartic hypersurface. This phenomenon was invisible at m ≤ 5 (it concerns the
   *balanced* 3|3 bond, first measurable at m=6). The witness vectors are recorded in
   `raw.json` (`child.syzygy_AM/BM`, `redraw.syzygy_AM/BM`).
2. **Two-stage rank drop on the 3|3 bond:** 70 (rank of the Sylvester sign matrix S,
   full over QQ and mod all three primes) → 69 (syzygy on each side) → 68 (the
   restricted bilinear form W_A·S·W_Bᵀ loses one further dimension in every cell).
   Whether the second drop is generic or an artifact of the particular syzygy is open.
3. **The recursion-built formal S_6 behaves fully symmetric** on the tested range:
   the 4|2 bond equals the 2|4 bond (45) in every cell, and comb == balanced at
   18 432 points — consistent with Semaev symmetry persisting through the
   formal-resultant recursion at m=6 (already observed at m=5, EV-TTN-001 child=root=15).
4. **Convention hazard documented:** sage per-point `.resultant()` uses *actual*
   degrees; the formal-degree construction requires padding by `lead(f)^{n-deg g}` at
   *every* nesting level independently (an inner-level drop, e.g. x5 = x6 forcing
   lead (x5−x6)² = 0, carries a different factor than an outer drop). Handled and
   verified pointwise; recorded for future instruments.
5. **Apparatus hazards:** SIGALRM cannot interrupt Singular C-level code (the m=6
   symbolic probe had to be killed at subprocess level); a single-einsum contraction
   without staged mod-p reduction overflows int64 at p=1009 (p^5·59 049 > 2^63).
   Both recorded in the run manifests.
6. **Dense symbolic S_6 probe (infrastructure context, NOT evidence):** S_4 stage
   0.009 s / 439 terms; S_5 stage 3.35 s / 54 477 terms (consistent with EV-TTN-001's
   4.4–5.0 s); the S_6 resultant exceeded a 150 s hard kill — **censored
   (infrastructure)**. No statement about S_6 term count or dense cost is made.

## 4. Scope and limitations

Toy primes p ≤ 2^10; m = 6 only; 3 seeds; ordinary short-Weierstrass prime-field
curves. The root-bond value 45 is an exact certificate (structural upper bound +
exhibited independent factors). The child-bond value 68 is certified by: exact
rank(E) = 68 minor (lower bound), plus form-rank computation under the measured
factor spans (69), with the span values confirmed at two independent point samples
per cell and the C1-verified recursion identity; the residual theoretical gap
(sampled span vs true polynomial span) is bounded by standard Schwartz–Zippel-type
arguments and is recorded, not hidden. No recall/truncation measurements here (that
direction was closed by DEC-20260718-008); this experiment is the rank certificate
only. Per rule 7: nothing here is a crypto-scale statement.
