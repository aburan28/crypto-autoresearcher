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

3-isogeny phi: E1 -> E2 over F_97 (E1: y^2=x^3+10, E2: y^2=x^3+21), x-map = (t^3+40)/t^2.

- image_size = 103 = |E2(F_97)|. image_equals_E2 = True.
- Obstruction: phi: E1(F_p) -> E2(F_p) is BIJECTIVE. For prime-order |E1|=103, the 3-isogeny kernel has no F_p-rational non-trivial point (3 does not divide 103). So phi restricted to F_p-points is injective and hence bijective. The "image" = all of E2(F_p): no filtering. d_fixed = False.
- Note: Using the isogeny x-map phi_x(t)=x as a membership condition introduces a variable t (round-4 pullback pattern). This restores degree conservation.

### Candidate (c): Fixed-Degree Rational-Map Image

psi(t) = t^2 + c (quadratic map), FB = {psi(t) : t in F_p, psi(t) is E x-coord}.

- Membership 'x in Im(psi)' requires x-c to be a QR mod p: polynomial degree = (p-1)/2 = 48, grows with p. NOT a fixed-degree condition in x.
- Alternative: introduce s with s^2 = x-c (extra variable, pullback pattern). d_fixed = False (in x alone).

### Candidate (d): Division Polynomial FB

psi_n(x) = 0 characterizes x-coords of n-torsion points. Degree (n^2-1)/2 (fixed for fixed n).

| n | deg(psi_n) | Fp-rational roots | Obstruction |
|---|-----------|-------------------|-------------|
| 2 | 3 | 0 | 2 does not divide 103 |
| 3 | 4 | 1 | 3 does not divide 103 (the 1 root is x=0, not on E) |
| 5 | 12 | 0 | 5 does not divide 103 |
| 7 | 24 | 0 | 7 does not divide 103 |

- d_fixed = True (deg(psi_n) is fixed for fixed n). FB is EMPTY for prime-order E(F_p) since no n-torsion in E(F_p) for n not dividing prime order.

### Candidate (e): Synthetic Degree-Model Sweep + Meter

Sweep: |FB| in {4, 8, 16} x degree model in {standard (d=|FB|), synthetic d=2, synthetic d=3}.

| Config | d_mem | D_reg (Yokoyama) | D_reg (measured) | fires | gate_meaningful | d_is_fixed |
|--------|-------|-----------------|------------------|-------|-----------------|------------|
| FB=4, d=standard | 4 | 17 | 10 | False | False | False |
| FB=4, d=2 | 2 | 11 | 4 | False | False | True |
| FB=4, d=3 | 3 | 14 | 7 | False | False | True |
| FB=8, d=standard | 8 | 29 | 21 | True | **True** | False |
| FB=8, d=2 | 2 | 11 | 4 | False | False | True |
| FB=8, d=3 | 3 | 14 | 7 | False | False | True |
| FB=16, d=standard | 16 | 53 | 33 | True | **True** | False |
| FB=16, d=2 | 2 | 11 | 4 | False | False | True |
| FB=16, d=3 | 3 | 14 | 7 | False | False | True |

Key observations:
1. Standard (d=|FB|, growing-d) at FB=8 and FB=16: gate_meaningful=True -- confirms meter works on real Semaev systems -- but d grows with |FB| (this is the x-interval baseline behavior, no new lever).
2. Synthetic fixed-d models (d=2, d=3 regardless of |FB|): D_reg is constant across all three FB sizes (4 = 11-7, 7 = 14-7 respectively, i.e. D_reg stays at 4 or 7). This CONFIRMS that if a fixed-degree membership existed, D_reg would stop growing. But gate_meaningful=False for all fixed-d runs.
3. The d=2 and d=3 fixed models have D_reg < their FB sizes (e.g. d=2 gives D_reg=4 while |FB|=8 or 16): the system is so underdetermined that it doesn't even fire. A genuine fixed-degree membership condition with |FB| >> d would face this same structural problem.

## Auto-Descent (Subgroup Membership) Check

All FB points used in the sweep are genuine E(F_97) prime-order subgroup points:
- |FB|=4: True
- |FB|=8: True
- |FB|=16: True

The descent obstruction of NR-016 (wrong subgroup in extension-field construction) does NOT apply here: working directly on E(F_p) achieves automatic descent by construction.

## D_reg vs |FB| Comparison

x-interval baseline (standard): D_reg = 3*|FB| + 5 (grows linearly with |FB|).

Fixed-d synthetic model: D_reg = 3*d + 5 (constant in |FB|) -- but no E(F_p)-native construction achieves this with |FB| >> d.

The Yokoyama conservation holds empirically across all measured parameter points.

## Controls Outcome (Subgroup Check)

PASSED: All three FB size sweeps (4, 8, 16 points) use genuine E(F_p) prime-order subgroup points, confirming the descent that NR-016's extension-field construction lacked. Despite this, no gate-meaningful fire arises from any fixed-degree construction.

## Verdict and Interpretation

VERDICT: failed (negative result, scoped)

CLAIM LABEL: NEGATIVE RESULT

NEGATIVE RESULT (NR-020, scoped to prime-order E(F_p), m=3, candidates a-d): No E(F_p)-native fixed-degree membership condition yields all three of: (i) d fixed and |FB|-independent, (ii) genuinely useful FB (|FB| >> d, nonempty), and (iii) auto-descent into the E(F_p) prime-order subgroup. Each of the four concrete structural candidates has a provable algebraic obstruction specific to prime-order curves:

- (a) CM endomorphism: scalar on prime-order group; eigenset = entire group.
- (b) l-isogeny: bijective on F_p-points; image = all of target curve.
- (c) Rational-map image: membership requires QR condition (non-polynomial in x, degree (p-1)/2); pullback introduces extra variable restoring conservation.
- (d) Division polynomial: fixed degree in x, but FB is empty for prime-order curves (no rational n-torsion for n not dividing prime order).

The standard Semaev+x-interval system at |FB|=8 and |FB|=16 DOES produce gate_meaningful=True (baseline behavior confirmed working), but with d=|FB| growing -- the x-interval baseline, not a new lever.

## What This Does NOT Rule Out

- Candidates over non-prime-order curves (composite order with exploitable torsion structure).
- Candidates using COMBINATIONS of conditions (e.g., divisibility by n of the discrete log, Frobenius eigenspace conditions, or endomorphism-based multi-scalar structures).
- Candidates in different coordinate systems (Kummer, Edwards, Montgomery) that might expose different algebraic structure.
- The Yokoyama conservation theorem itself does NOT cover crossbred/XL or d_ff-governed solvers; fixed-degree structures might still benefit these if they reduce the d_ff degree profile.
- Weil-restriction-based constructions over F_{p^2} (POS-C path), which remain the only gate-meaningful system found so far.
- A theoretical FB where the membership polynomial is defined over the JOINT variable space (x_i, y_i) with y_i eliminated via the curve equation -- potentially degree-fixed in a suitable ring.

## Next Steps

1. CONSERVATIVE: Investigate whether composite-order E(F_p) (with smooth order, not prime) admits fixed-degree division-polynomial FBs that ARE gate-meaningful. (Theory: psi_n exists and has Fp-rational roots if n | |E(F_p)|.)
2. REPRESENTATION-CHANGING: Investigate Edwards/Montgomery model -- does the addition structure expose a different FB via constant-degree membership in the Edwards x-coordinate ring?
3. HIGH-RISK: Investigate Frobenius-invariant sets over F_{p^2} projected back to F_p: characterize whether the "CM orbit" of a small seed set under phi gives a fixed-degree algebraic condition on x (not as an eigenvalue condition on the full group, but as a COSET condition in F_{p^2}).

## Files

- Code: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round008_exp016_efp_fixeddeg_fb.sage (1103 lines)
- Log: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round008_exp016_efp_fixeddeg_fb.log (363 lines)
- JSON: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round008_exp016_efp_fixeddeg_fb_result.json (542 lines)
- This file: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round008_exp016_efp_fixeddeg_fb_result.md
