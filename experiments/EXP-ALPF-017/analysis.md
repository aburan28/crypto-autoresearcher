# Analysis — Autolab prime-field: round008_exp016_efp_fixeddeg_fb

## Observation
NEGATIVE RESULT (SCOPED): No E(F_p)-native fixed-degree membership condition yields (i) d fixed + |FB|-independent, (ii) genuinely useful FB (|FB|>d, nonempty), AND (iii) auto-descent into E(F_p) prime-order subgroup. All four structural candidates (endomorphism, isogeny, rational-map, division-poly) have provable algebraic obstructions on prime-order curves. The standard (d=|FB|, growing-d) approach DOES produce gate_meaningful fires at FB=8 and FB=16 -- confirming the meter works on real syste

Source excerpt / raw summary:

```
# EXP-016 Result: Fixed-Degree-Membership FB on E(F_p)

## Experiment Contract Summary

- Hypothesis: A FB membership condition of degree d FIXED and INDEPENDENT of |FB|, native to E(F_p), exists AND yields a gate-meaningful Semaev system breaking the D_reg growth with |FB|.
- Null hypothesis (H0): Every E(F_p)-native membership condition either selects O(d) points (d grows with |FB|), is trivially satisfied by all of E(F_p) (no filtering), or introduces extra variables restoring degree-conservation.
- Curve: E: y^2 = x^3 + 10 over F_97, |E(F_97)| = 103 (prime), j=0, CM by Z[zeta_3]
- Baseline: x-interval FB with |FB|=B, d=B, D_reg = 3*B + 5 (Yokoyama, m=3, d_S=8)
- Reproduction: sage round008_exp016_efp_fixeddeg_fb.sage

## Meter Self-Validation (ALL PASSED)

| Control | Expected | Observed | Status |
|---------|----------|----------|--------|
| POS-A (3 cubics 3 vars, shared q) | d_ff=4 < D_reg=7, fires | d_ff=4, D_reg=7, fires=True | PASS |
| NEG-1 (generic quadrics 4 vars) | no fire | fires=False | PASS |
| NEG-2 (generic cubics 4 vars) | no fire | fires=False | PASS |
| e-ring m=3 Semaev (spurious) | fires, gate FAILS | fires=True, gate_passes=False | PASS |
| POS-C Weil S_3 over F_{p^2} | fires, gate PASSES | fires=True, gate_passes=True, gate_meaningful=True | PASS |

meter_self_validated = True

## Semaev S4 Construction

S4(x0,x1,x2,x3) = Res_z(S3(x0,x1,z), S3(x2,x3,z)) for S3(u,v,w) the S_3 summation polynomial.
- S4 total degree: 20; individual degrees: (8,8,8,8) -- symmetric in all 4 x_i
- Verified: S4 = 0 on 5 quadruples P0+P1+P2+P3=O from E(F_97)

## Candidate Results

### Candidate (a): CM Endomorphism Eigenset

CM endomorphism phi: (x,y) -> (zeta_3 * x, y) on E with j=0, p=97=1 mod 3.

- phi_is_scalar: True. phi = [56] (scalar multiplication by 56) on all E(F_97).
- eigenset_equals_whole_group: True. The entire group E(F_97) is the eigenset.
- Obstruction: On a prime-order group, End(E(F_p)) = Z, so any F_p-rational endomorphism is a scalar [n]. The "eigenset" at the unique eigenvalue is ALL of E(F_p). Any strict subset has membership polynomial of degree = subset size (grows with |FB|). d_fixed = False.

### Candidate (b): l-Isogeny Image FB

```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
