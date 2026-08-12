# Analysis - AutoLab R182 target subresultant

## Observation

R182 restricts the signed kernel `K_P=A_P+vB_P` to each squarefree public target
chart as `R_P=A_P+V_T B_P mod W`. On the imported controls,

```text
Norm(R_P)=0
  iff R_P is a nonunit in F[u]/W
  iff gcd(W,R_P) is nonconstant.
```

The package contains 12 ordinary controls: nine R181 replays and three held-out
seed-18206 controls. It also contains a duplicate-plus-opposite-point control
that forces exactly two x-injective charts.

```text
selected divisor degree sum:                    404
raw / unique retained target count:          80 / 79
remainder coefficient slots / nonzero:   2,962 / 2,962
candidate / noncandidate sources:           253 / 151
unit inverse certificates:                      151
Newton trace projections:                     2,962
```

Every ordinary remainder matrix has full target rank. Direct evaluation,
remainder evaluation, Newton norm reconstruction, gcd tests, inverse
certificates, and candidate-factor comparators agree exactly.

## Cost Interpretation

The represented remainder matrix, `N` degree-`n` trace outputs, noncandidate
inverse certificates, triangular norm, and standard target half-GCD each retain
scale `nN=B^(7/2)`, above the `B^(5/2)` rho proxy. This closes those standard
represented routes only.

## Claim Boundary

- Claim tier: toy.
- The finite density and rank controls are not an asymptotic lower bound.
- No general SLP, circuit, resultant, RAM, or data-structure lower bound follows.
- No factor logs, identical fresh-target descent, complete ECDLP attack,
  Pollard-rho improvement, Shoup improvement, or breakthrough is present.
- The source package passed 24 of 35 obligations; all attack flags remain false.

## Surviving Direction

Construct or refute an SLP-direct determinant-zero or resultant-mod-`U`
algorithm that consumes the compact signed kernel and target charts, emits only
`G_1`, and avoids the represented `nN` remainder, trace, inverse, and norm
bodies in softly `O(n+N)` work. Seed `18206` and a new divisor family are the
next bounded controls.
