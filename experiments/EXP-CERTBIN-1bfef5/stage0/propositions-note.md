# Propositions B and F — EXP-CERTBIN-1bfef5 Stage-0 note

Frozen before any Stage-1 closure. Observational instrument note only;
not a machine-checked proof artifact.

## Proposition B (exact)

For fixed set V and target x_R, changing the F_2-basis of the field or of V
leaves "1 in M_D" and "1 in W_D" invariant for every D. Both changes induce
degree-preserving ring automorphisms of B = F_2[v]/(v_i^2+v_i) that fix the
constant 1, so Macaulay/mutant membership of 1 is unchanged.

## Proposition F (exact)

If V is Frobenius-stable then W_D(x_R^{2^i}) is the image of W_D(x_R) under
the induced automorphism. One certificate per Frobenius orbit therefore
transfers and verifies on the conjugates.

## Arm-(a) identity control (Stage 1)

Re-descend the 144 archived RC-1 targets (U62+S62+C20) under a random
polynomial-V basis and a normal field basis; require exact label / iteration /
dimension agreement with RUN-CERTBIN-c417e0 for M_4 and W_4 (288/288).

## Thresholds (empirical Stage 2; not opened under this card)

- E-SET: W_4 rates on V_N and V_S both >= 0.90 (CP95)
- E-POLY: either structured W_4 rate <= 0.50
- MIXED: otherwise

Amazon Bedrock: NOT SELECTED.
