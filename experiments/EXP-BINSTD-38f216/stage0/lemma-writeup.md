# Corrected iota-stable subspace lemma (Stage 0)

Source of the correction: `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-29b1c5.yaml`,
frozen into H-BINSTD-dba2ab / EXP-BINSTD-38f216 by DEC-20260930-492bf6.
This note writes the corrected steps the contract requires. It is not a new
status change and it does not say the hypothesis is supported.

## Setting

E: y^2 + x y = x^3 + a x^2 + b over F_{2^n}, b != 0. The unique rational
2-torsion point is T = (0, sqrt(b)).

## Step A — translation identity

For an affine point P = (x, y) with x != 0,

    x(P + T) = sqrt(b) / x.

Write iota(x) = sqrt(b) / x on F^*. Squaring is bijective on F_{2^n}, so
iota has exactly one fixed point, beta = b^{1/4}, the unique solution of
x^2 = sqrt(b).

## Step B — corrected classification

Let V be a nonzero F_2-subspace of F_{2^n} with iota(V \ {0}) = V \ {0}.

The nonzero cardinality 2^{dim V} - 1 is odd, and every iota-orbit in F^* has
size 2 except {beta}. Therefore beta lies in V.

The review's corrected stabilizer argument, copied as the Stage 0 steps:

1. For nonzero u, w in V the hypothesis of the original proof produced
   u^2 / w in V. Combined with iota-stability, 1/V = V / sqrt(b), so the
   stabilizer S = {lambda : lambda V = V} contains u^2 / sqrt(b), not u^2.
2. (u/v)^2 lies in S for nonzero u, v in V. Squaring is a bijection of F^*,
   so u/v lies in S.
3. K = span(S) is a subfield F_{2^d}. V = c K for any nonzero c in V.
4. iota-stability forces sqrt(b) / c^2 in K, hence V = b^{1/4} F_{2^d}.

So the nonzero iota-stable F_2-subspaces are exactly

    V_d = b^{1/4} F_{2^d}

for the divisors d of n, one each. V_d is a subfield if and only if b lies in
F_{2^d}.

## Prime rows

If n is prime the only nonzero stable subspaces are

- dim 1: {0, b^{1/4}}, size 2 (equal to F_2 exactly when b = 1),
- dim n: the whole field.

The (subspace factor base, 2-torsion quotient) cell is recorded as
STRUCTURALLY EMPTY on those rows. The certificate used here is this
classification together with primality of n. That is a structural verdict,
not a measured attack cost.

## Composite rows

For the five audit rows with n = 16k, the subspaces V_d for

    d in {1, 2, 4, 8, k, 2k, 4k, 8k}

are the named objects. Those with b not in F_{2^d} are not subfields. The
cell is recorded OPEN. Pricing that object is outside this experiment.

## What Stage 0 does not say

No exponent moves. No claim that a deployed curve's cost changed. The
per-row table is the classification above applied to degrees in
`analysis/binstd-curve-audit/audit-scan.txt`, plus the ECC2K-130 row named
in the hypothesis (n = 131, b = 1), which is not a line of that scan.
