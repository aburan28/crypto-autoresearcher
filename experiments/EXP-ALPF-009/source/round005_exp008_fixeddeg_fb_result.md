# EXP-008: Fixed-Degree Membership Factor Base -- Result

## Experiment
**Date:** Sat May 30 23:04:40 2026  
**Seed:** 42  
**Meter validated:** True  

## Hypothesis
A factor base whose membership is cut by a polynomial of FIXED low degree independent
of |FB| (trace-zero over F_{p^2}/F_p, norm-1, subfield) can stop D_reg from growing
with |FB|, potentially giving a genuine asymptotic lever over Pollard rho.

## Null Hypothesis
The FB-constraint degree still grows with |FB|, OR relations do not descend to the
F_p ECDLP (wrong subgroup), so no asymptotic gain exists.

## Meter Status
**METER_VALID = True**  
All EXP-008 first-fall results are TRUSTWORTHY.
  - POS-A fires: True (d_ff=4, D_reg=7)
  - NEG-1 quiet: True  
  - NEG-2 quiet: True  

## FB-Constraint Degree vs |FB| (Key Table)

| FB Type | Constraint | Degree d_FB | Grows with |FB|? |
|---------|-----------|-------------|----------------|
| trace-zero (Weil) | 2*u0_i + u1_i*Tr(w) = 0 | **1 (FIXED)** | NO |
| subfield | u1_i = 0 | **1 (FIXED)** | NO |
| norm-1 (Weil) | u0_i^2 + u0_i*u1_i*Tr(w) + u1_i^2*N(w) = 1 | **2 (FIXED)** | NO |
| x-interval baseline | prod(xi - xj) = 0 | **= |FB| (GROWS)** | YES |

**FINDING:** All three fixed-degree candidates have d_FB that is INDEPENDENT of |FB|.
This is the key lever sought since round 1.

## Subgroup Descent Gate (Critical Gate)

| FB Type | Frac in E(F_p) | Descends? |
|---------|---------------|----------|
| subfield (positive ctrl) | 1.000 | YES |
| trace-zero | 0.000 | NO (BLOCKED) |
| norm-1 | 0.007 | NO (BLOCKED) |

### Why Trace-Zero Descends to Wrong Subgroup

OBSERVATION: Points with Tr(x)=0 in E(F_{p^2}) are NOT in general F_p-rational.
Specifically: Tr(x)=0 means x+x^p=0 => x^p=-x. In the basis {1,w} with x=u0+u1*w,
this gives 2*u0 + u1*(w+w^p) = 0 (degree-1 Weil constraint), but u0 != 0 in general.
Thus x is NOT in F_p (since F_p elements have u1=0).

The trace-zero SUBGROUP T(F_{p^2}) = {P in E(F_{p^2}) : Tr_{p^2/p}(P) = O}
has order n_Fq / n_Fp (roughly). Its intersection with E(F_p) is generically trivial.
Therefore: a relation P1+...+Pm = Q in E(F_{p^2}) with Pi in T(F_{p^2})
DOES NOT imply k*P = Q in E(F_p) unless all Pi happen to be F_p-rational.

**SUBGROUP DESCENT OBSTRUCTION**: The trace-zero and norm-1 fixed-degree FBs
live in the WRONG subgroup of E(F_{p^2}). Relations in E(F_{p^2}) do not
descend to the target F_p ECDLP.

## D_reg Comparison Table

| Method | m | d_FB | D_reg (formula) | Grows with |FB|? |
|--------|---|------|-----------------|----------------|
| TZ/Weil (m=2) | 2 | 1 | ~7 (FIXED) | NO |
| x-interval (m=2, L=4) | 2 | 4 | 10 | YES |
| x-interval (m=2, L=8) | 2 | 8 | 18 | YES |
| x-interval (m=2, L=16) | 2 | 16 | 34 | YES |
| x-interval (m=2, L=32) | 2 | 32 | 66 | YES |

## Verdict

**SCOPED_NEGATIVE -- d_FB fixed, D_reg fixed, BUT descent blocked**

**Controls outcome:** POSITIVE_CTRL=PASS(subfield_descends), NEGATIVE_CTRL=trace_zero_frac=0.000_norm1_frac=0.007_DESCENT_BLOCKED

## What This Rules Out

- The trace-zero factor base in E(F_{p^2}) as a direct drop-in replacement for the
  interval FB in the F_p ECDLP: relations do not descend to E(F_p).
- The norm-1 factor base has the same obstruction.
- SCOPED: this ruling applies to the SPECIFIC attack model where we use the
  F_{p^2} trace-zero/norm-1 subgroup and require descent to E(F_p).

## What This Does NOT Rule Out

- A modified attack that works NATIVELY in E(F_{p^2}) without requiring descent
  (solving ECDLP over F_{p^2} directly -- but E(F_{p^2}) has larger group order,
  making rho harder too, so this is not obviously useful).
- A hybrid: use trace-zero points to generate relations modulo the trace-zero
  SUBGROUP, then lift to E(F_p) via the norm map or a descent argument.
- Other representations where fixed-degree membership and descent BOTH hold.
- The subfield FB (x in F_p) DOES descend, but reduces to standard E(F_p) arithmetic
  with d_FB=1 -- though this means |FB| is limited to n_Fp (all of E(F_p)), which
  is not a useful factor base restriction in practice.

## Next Three Pushes

1. **Conservative**: Hybrid trace-zero/subfield FB -- use SUBFIELD FB (d=1, descends)
   with a membership constraint that stays degree 1 AND limits the FB to a
   structured subset of E(F_p). Check if any algebraic criterion (endomorphism orbit,
   Frobenius constraint) gives degree-1 membership on E(F_p) directly.

2. **Representation-changing**: Work in E(F_{p^2}) natively. The trace-zero
   subgroup has order n_Fq/n_Fp; its ECDLP is a SEPARATE problem. Investigate
   whether index calculus in E(F_{p^2}) [trace-zero subgroup has order ~p, so
   rho is still ~p^{1/2}] gives sub-rho via the degree-1 FB membership -- but
   this is then a DIFFERENT ECDLP (over F_{p^2}), not the F_p target.

3. **High-risk speculative**: Descent via WEIL RESTRICTION. Weil-restrict E(F_{p^2})
   to an abelian surface A over F_p. The trace-zero subgroup becomes a sub-abelian
   variety. Investigate whether the degree-1 membership on this sub-variety, combined
   with index calculus on A (not E), gives a sub-rho algorithm. This requires index
   calculus on abelian surfaces, which is known to be hard but not impossible.

## Limitations

- TOY-SCALE: p in range 2^7..2^11. All degree results are exact at toy scale.
- The 'D_reg stays fixed' result for TZ/Weil is a theoretical analysis (semiregular
  formula) not a GB solve. Actual D_reg may differ if the system is not semiregular.
- The subgroup descent obstruction is EXACT (mathematical, not empirical).
- This experiment uses m=2 summands (S_3). For m=3 (S_4), the Weil-restricted
  S_4 was not computed (too expensive symbolically); degrees are theoretical estimates.

## Artifacts

- Code: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round005_exp008_fixeddeg_fb.sage
- Log: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round005_exp008_fixeddeg_fb.log
- JSON: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round005_exp008_fixeddeg_fb_result.json
- MD: /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round005_exp008_fixeddeg_fb_result.md