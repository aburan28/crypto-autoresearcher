# Methodological note — EXP-BINSTD-a3cfee Stage 0

Task `TASK-20261001-3d2adf`. Written BEFORE any Stage-1 yield comparison.

## Instrument

- Field: F_2^17 with irreducible trinomial modulus (n=17 primary).
- Curve: Y^2 + XY = X^3 + 1 (ordinary binary Koblitz analog).
- Normal basis: powers of β=3 under Frobenius; HW measured in that basis
  (Bailey-style type-2 analog at toy scale — not the ECC2K-130 constants).
- Walk: P ← σ^j(P) ⊕ P with j = ((HW(x)/2) mod 8) + 3.
- DP predicate: HW_normal(x) ≤ c=4.
- Pool size N=96; attempts/arm=250.
- Group order |E| = 130972 (exact trace count).

## Arms

1. **DP_walk**: Bailey walk until DP; byte-identical seed replay required.
2. **uniform**: size-matched random curve points.
3. **HW_filter_only**: rejection sample HW≤c without walk (isolates filter).

## Semaev m=2 yield

For each attempt, sample random R on E; search P,Q in pool with P+Q=R;
certificate.kind=`decomposition` re-verified on a fresh schoolbook Field/Curve.

## Modeled baseline

E[count] ≈ N²/(2·|G|)·attempts = 8.7958 (H1 band [0.7, 1.4]).

## Claim boundary

No deployed-curve break, no exponent move, no n=131 transfer of toy ratios.
KN-LIT-661e97 n=131 figures are context only.
