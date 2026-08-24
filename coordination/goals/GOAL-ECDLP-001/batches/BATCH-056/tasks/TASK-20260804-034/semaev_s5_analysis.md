# Semaev S_5 BKK Analysis

## Setup

Extending the BATCH-055 BKK analysis from S_3 to S_m at larger m.

Reference: Semaev (2004), "Summation polynomials and the discrete logarithm problem
on elliptic curves." The degree of S_m in each of its m variables is 2^(m-2).

## Degree structure of S_m

| m | deg/var | total_deg | Bezout | BKK_MV | ratio |
|---|---------|-----------|--------|--------|-------|
| 3 | 2       | 4         | 16     | 8      | 0.50  |
| 4 | 4       | 8         | 64     | 32     | 0.50  |
| 5 | 8       | 16        | 256    | 128    | 0.50  |
| 6 | 16      | 32        | 1024   | 512    | 0.50  |
| 7 | 32      | 64        | 4096   | 2048   | 0.50  |

The mixed volume is computed as MV = 2 * (deg_per_var)^2 for the system of two
specialized polynomials {S_m(x1,x2,c1)=0, S_m(x1,x2,c2)=0}, where each
polynomial has Newton polytope equal to the full [0, deg_per_var]^2 square.
The BKK/Bezout ratio is STRUCTURALLY 0.5 at every m.

## Why the ratio is always 0.5

For a 2-variable polynomial system where both polynomials have Newton polytope
equal to the full [0,k]^2 box (integer points in the square), the mixed volume is:

MV([0,k]^2, [0,k]^2) = 2 * Area([0,k]^2) = 2 * k^2

The Bezout bound is (2k)^2 = 4k^2 (using total degree 2k for each polynomial).
Therefore: MV / Bezout = (2k^2) / (4k^2) = 1/2.

This structural factor-2 improvement holds whenever the Newton polytope equals
the full hypercube, which is the case for the Semaev polynomial because S_m
is a complete polynomial of degree k = 2^(m-2) in each of two variables.

## Empirical root count gap (from BATCH-055)

For m=3 (k=2): BKK=8, actual root count=2 (empirical, 20 samples).
The actual count is 4x below BKK. This suggests the Newton polytope, while
equal to the full [0,k]^2 box, has a tighter INNER structure (the coefficients
are not generic — S_m is symmetric and satisfies algebraic identities).

For m=5 (k=8): by extrapolation, actual root count may be ~8 (i.e., BKK/16)
if the gap grows linearly in k. This is speculative without empirical verification.

## Scale-up conclusion

1. **Factor-2 BKK improvement**: Structural, holds at all m. This is a real but
   modest improvement to the Semaev resultant computation.

2. **Beyond BKK**: The empirical root count at m=3 is 4x below BKK (2 vs 8).
   If this gap persists or grows at larger m, the actual sparsity is greater than
   the BKK bound captures. A tighter bound (using the symmetry of S_m) is possible.

3. **Index calculus relevance**: The relevant value of m for current ECDLP index
   calculus is m=7 (Joux-Vitse 2012 used m=7 for 160-bit curves). At m=7:
   Bezout=4096, BKK=2048, factor-2 improvement. If empirical count is ~16 (BKK/128),
   this would represent a ~128x improvement over the BKK-predicted count.

4. **Not exponent-moving**: These improvements reduce the CONSTANT c in the
   exp(c*sqrt(log N * log log N)) subexponential complexity. The functional form
   does not change.

## Minimal next experiment

At m=5 (S_5): specialize S_5(x1,x2,c1)=0 and S_5(x1,x2,c2)=0 for random valid
(c1,c2) pairs, count joint roots empirically over GF(p) for a 20-bit prime p.
Compare to BKK=128 and Bezout=256. If count ~8: significant structural sparsity.
