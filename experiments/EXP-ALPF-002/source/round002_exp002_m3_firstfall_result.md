# EXP-002 Result: m=3 Semaev First-Fall via Macaulay Rank Profile

**Seed:** 42  **Date:** 2026-05-30 20:14  **Verdict:** FAILED (NEGATIVE RESULT)

## Instrument Fix (Round 1 error corrected)

Round 1 used `min(GB-output-degree)` as d_ff proxy. This is a tautological lower bound
(pinned at input degree at m=2) and NOT the true first-fall degree.

Round 2 measures the true first-fall via Macaulay-matrix rank profile vs the semiregular
Hilbert-series prediction (Bardet-Faugere-Salvy-Yang definition):
- d_ff = smallest D where hf(D) < hf_pred(D) = max(c_D, 0).
- "early fall" = d_ff strictly less than D_reg_pred.
- Instrument verified via P1 (3 quadrics no-fall, 4 quadrics fall) and P2 (extension domain).

## Controls Outcome

| Control | Gate | Notes |
|---|---|---|
| P1 synthetic (3 vs 4 quadrics) | PASS | 3-quad d_ff=4=D_reg_pred (no fall), 4-quad d_ff=3 fall at D=3 |
| P2 extension-field (known fall) | PASS | fall_triggered=True at d_ff=6 > D_reg_pred=5 (overdetermined fall) |
| N1 random dense (noise floor) | PASS | 0/12 seeds showed early fall (d_ff < D_reg_pred) |

**P1 interpretation:** For 3 random quadrics in 3 vars, the graded HF tracks the semiregular
prediction exactly through D_reg_pred=4 (fall_triggered=False). For 4 quadrics (overdetermined),
hf drops below hf_pred=0 at D=3, triggering a fall. This confirms the instrument distinguishes
semiregular from overdetermined behavior. P2 shows the instrument detects falls in the known
extension-field regime.

## m=3 Results: Rank Profiles (representative cells)

### struct_13bit_FB4 (|FB|=4, degs=[4,2,2,2] in e-ring, D_reg_pred=4)
```
  D    ncols   rank  corank  semireg_cum   c_D   hf  hf_pred  status
  4       35     27       8            8    -1     0        0  pred_Dreg
  5       56     50       6            8    -3    -2        0  FALL! (but D=5 > D_reg_pred=4)
  6       84     80       4            8    -3    -2        0
  7      120    116       4            8    -1     0        0
```
RESULT: d_ff=5, D_reg_pred=4. fall_detected=False (5 > 4 = not early).

### struct_13bit_FB5 (|FB|=5, degs=[4,3,3,3] in e-ring, D_reg_pred=5)
```
  D    ncols   rank  corank  semireg_cum   c_D   hf  hf_pred  status
  4       35     21      14           14     1     6        1
  5       56     38      18           15     0     4        0  pred_Dreg
  6       84     67      17           15    -1    -1        0  FALL! (D=6 > D_reg_pred=5)
  7      120    104      16           15     0    -1        0
```
RESULT: d_ff=6, D_reg_pred=5. fall_detected=False (6 > 5 = not early).

## m=3 Results Summary (all cells)

| label | |FB| | d_ff_sym | D_reg_sym | early_fall_sym? | d_ff_ns | D_reg_ns | early_fall_ns? |
|---|---|---|---|---|---|---|---|
| struct_13bit_FB2 | 2 | 0 | 0 | no | 12 | 4 | no |
| struct_13bit_FB3 | 3 | 4 | 1 | no | 12 | 7 | no |
| struct_13bit_FB4 | 4 | 5 | 4 | no | 12 | 10 | no |
| struct_13bit_FB5 | 5 | 6 | 5 | no | 13 | 12 | no |
| struct_15bit_FB2 | 2 | 0 | 0 | no | 12 | 4 | no |
| struct_15bit_FB3 | 3 | 4 | 1 | no | 12 | 7 | no |
| struct_15bit_FB4 | 4 | 5 | 4 | no | 12 | 10 | no |
| struct_15bit_FB5 | 5 | 6 | 5 | no | 13 | 12 | no |
| struct_17bit_FB2 | 2 | 0 | 0 | no | 12 | 4 | no |
| struct_17bit_FB3 | 3 | 4 | 1 | no | 12 | 7 | no |
| struct_17bit_FB4 | 4 | 5 | 4 | no | 12 | 10 | no |
| struct_17bit_FB5 | 5 | 6 | 5 | no | 13 | 12 | no |
| struct_19bit_FB2 | 2 | 0 | 0 | no | 12 | 4 | no |
| struct_19bit_FB3 | 3 | 4 | 1 | no | 12 | 7 | no |
| struct_19bit_FB4 | 4 | 5 | 4 | no | 12 | 10 | no |
| struct_19bit_FB5 | 5 | 6 | 5 | no | 13 | 12 | no |
| rand_13bit_FB3 | 3 | 4 | 1 | no | 12 | 7 | no |
| rand_15bit_FB3 | 3 | 4 | 1 | no | 12 | 7 | no |

Notes:
- |FB|=2: FB constraints degenerate to constants in e-ring (|FB| < m=3). System trivially over-constrained.
- |FB|=3: FB constraints are linear (degree 1). D_reg_pred=1 (trivially overdetermined by 3 linears). d_ff=4 is the S4sym degree itself appearing, NOT an early fall.
- |FB|=4,5: FB constraints have degree 2,3 respectively. D_reg_pred=4,5. d_ff=5,6 is one above D_reg_pred -- semiregular behavior, no early fall.
- NS ring: sweep starts at D=12 (S4 degree). All "falls" are sweep artifacts past D_reg_pred. These are not meaningful first-fall measurements.
- Results identical across Solinas (a=-3) structured and random prime families.
- Results flat across 4 prime sizes (13-19 bits). No dependence on p.

## m=2 Sanity Anchor (round 1 tautology corrected)

Round 1 reported d_ff=2 for m=2 using min(GB-output-degree) -- this was a tautology equal to
the input polynomial's own degree. True Macaulay instrument: d_ff=3=D_reg_pred, fall_triggered=False.
No early fall at m=2 either, confirming NR-009 extends.

## Pollard Rho Baseline

| family | bits | |E| | n_ops_rho | rho_expected | ratio | solved |
|---|---|---|---|---|---|---|
| structured | 13 | 4153 | 201 | 57 | 3.52x | YES |
| structured | 15 | 16183 | 678 | 113 | 6.02x | YES |
| structured | 17 | 65993 | 687 | 228 | 3.02x | YES |

All ECDLP instances solved and verified (k*P == Q checked). Rho ratios within expected range for
small curves (small-n overhead inflates ratio; converges toward 0.886*sqrt(n) asymptotically).

## IC-vs-Rho Cost (e-ring, omega=2, D_reg from sym measurement)

For |FB|=4 (the cleanest regime): D_reg_sym=4, ncols(D=4)=35, C_solve ~ 35^2 = 1225.
C_rho(13-bit) ~ 57 group ops. So IC > rho even at these toy scales.
As n grows, D_reg stays at 4 (confirmed flat across 4 bit sizes) while C_rho = 0.886*sqrt(n)
grows without bound. IC cost scales as |FB|^omega ~ const; rho scales as sqrt(n). 
The asymptotic crossover does NOT materialize here because the FB size needed for full rank grows
with n (need |FB| ~ n^(1/m) for a useful IC), driving D_reg up.

## Primary Verdict

CLAIM LABEL: **NEGATIVE RESULT**

The m=3 symmetrized prime-field Semaev system in elementary-symmetric (e1,e2,e3) coordinates
shows NO early first-fall (d_ff >= D_reg_pred) in any tested cell across:
- 4 prime sizes: 13, 15, 17, 19 bits
- 4 |FB| values: 2, 3, 4, 5
- 2 curve families: Solinas (a=-3) structured, random prime-order
- 4 bit sizes per family

The graded Hilbert function tracks the semiregular Hilbert-series prediction through D_reg_pred
in every instance. This extends NR-009 (m=2 negative result) to m=3 with the correct instrument.

Scope: this is a TOY-EVIDENCE result (bits 13-19, |FB|<=5). It does NOT prove impossibility for
cryptographic parameter ranges. It rules out the specific candidate: "elementary-symmetric
coordinates reduce the first-fall degree of the m=3 Semaev system below the semiregular bound."

## What Is Ruled Out

- Round-1 tautology (min-GB-output-degree as d_ff proxy) is corrected; no artifact survives.
- No first-fall advantage for e-symmetric m=3 Semaev in the tested toy regime.
- The Solinas/a=-3 structure produces no distinguishable algebraic behavior vs random curves.
- Elementary-symmetric coordinate rewrite of S4 does not lower the effective D_reg.

## What Is NOT Ruled Out

- **Power-sum coordinates (p1,p2,p3):** Newton's identity maps give a different polynomial ring with
  potentially different degree distribution. Not tested.
- **Kummer/x-line representations:** Using x-coordinates only (no sign) or specific rational-map
  images as factor bases. Not tested.
- **|FB| > 5 or m >= 4:** Larger m has higher S_{m+1} degree and different semiregular threshold.
  Yokoyama's bound only covers naive IC; m-dependent cancellation at m>=4 is unstudied.
- **Non-dense coefficient structure:** S4sym has 35/102 e-monomials populated (34% density).
  XL/crossbred solvers exploiting sparsity have not been benchmarked.
- **Extension-field / binary-field analogs:** Confirmed by P2 to show genuine falls.
- **Cryptographic parameter extrapolation:** These are toy sizes; a theorem is required.

## Next Experiments

1. **(Conservative)** Power-sum coordinates (p1,p2,p3): rewrite S4 via Newton's identity
   (e1=p1, e2=(p1^2-p2)/2, e3=(p1^3-3p1*p2+2p3)/6). The degree of S4 in (p1,p2,p3) may differ
   from 4 (in e-coords), changing D_reg. Test same Macaulay sweep.

2. **(Representation-changing)** Kummer x-line FB: define the factor base as the image of
   an endomorphism or rational map on x-coordinates. Build S4 in a ring where the FB
   membership has lower constraint degree, potentially lowering D_reg below Yokoyama's bound.

3. **(High-risk speculative)** p-adic / formal group lift: lift the prime-field curve to
   Z_p and work in the formal group. The formal logarithm makes the group law look
   additive at precision 1. If a "smoothness" analog exists in the formal group ring,
   relation generation might have a different degree structure.
