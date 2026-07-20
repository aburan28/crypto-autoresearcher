# P1513 Shared Common-Norm Route Screen

Status: `REVISE_STANDARD_ROUTES_ABOVE_RHO_KU_CIRCUIT_REDUCTION_OPEN`

This receipt screens the standard algorithms admitted by the P1513 contract.
It is not a lower bound for arbitrary arithmetic circuits or a resolution of
P1513. One finite-field bit-complexity exception remains explicit.

## Degree Regime

The shared circuit is

```text
H(U,W) = product_(i,j) P_(i,j)(U,W)
```

with `Theta(r^2)` constant-degree bivariate leaves. The selector polynomials
`T(U)` and `F(U)` each have degree `Theta(r)`. Therefore

```text
N_T(W) = Res_U(T,H),
N_F(W) = Res_U(F,H)
```

each have W-degree `Theta(r^3)`, while a relation batch expects only
`Theta(r)` common roots. Pollard rho on `q=Theta(r^5)` is
`Theta(r^(5/2))`.

## Closed Standard Routes

### Specialize Then Multiply

Evaluating the `r^2`-leaf circuit at each of `Theta(r)` roots of either
selector instantiates `Theta(r^3)` leaves. Multipoint evaluation does not help
if it outputs every specialized leaf value: there are already `Theta(r^3)`
such values and source backpointers.

### Expand, Reduce, Or Factor The Norms

Each explicit norm has `Theta(r^3)` coefficients. A product/remainder tree is
quasi-linear in that explicit degree, and any dense gcd or factorization starts
after the cubic vectors exist. Reducing a degree-`r^3` norm modulo a degree-
`r^2` polynomial still reads a cubic dense input.

### Fiber-Product GCD

Let

```text
C = F_p[U,V]/(T(U),F(V)),  dim(C)=Theta(r^2).
```

The componentwise polynomials `H(U,W)` and `H(V,W)` have W-degree
`Theta(r^2)`. A dense representation in `C[W]` therefore has
`Theta(r^4)` base-field slots before half-gcd, subresultants, idempotent
splitting, or source extraction. Keeping the product circuit avoids this state,
but then the dense quotient-ring algorithms do not apply without a new circuit
reduction.

### Truncated Resultants

Moroz and Schost compute `k` local coefficients of a bivariate resultant of
degree bound `d` in soft-`O(kd)` base-field operations. Here `d=Theta(r^2)`.
Even `k=Theta(r)` local coefficients cost soft-`Theta(r^3)`, and a truncation
at a fixed expansion point does not locate `Theta(r)` unknown common roots.
Using a degree-`r^2` quotient modulus raises the direct bound to soft-
`Theta(r^4)`.

### Generic Algebraic Modular Composition

For one degree-`n` modular composition, the 2026 two-relation-matrix algorithm
uses

```text
soft-O(n^alpha),  alpha=(omega+3)/4,
```

under genericity assumptions. In the smallest plausible quotient dimension
`n=Theta(r^2)`, this becomes

```text
soft-O(r^((omega+3)/2)).
```

Strictly beating rho would require `(omega+3)/2 < 5/2`, hence `omega<2`.
Since matrix multiplication has the information-theoretic floor `omega>=2`,
this algorithm family cannot give a strict sub-rho exponent here even before
common-norm and source-recovery overhead. Brent-Kung-style algebraic modular
composition is slower in this regime.

## Open Kedlaya-Umans Exception

Kedlaya and Umans give quasi-optimal finite-field modular composition in a bit-
complexity model, with arbitrary-characteristic algorithms based on lifting,
multimodular reduction, and multidimensional FFTs. A bounded number of degree-
`r^2` modular compositions at `r^(2+o(1))` bit complexity could fit below the
`r^(5/2)` arithmetic target after careful field-bit conversion.

No reduction is presently known here from

```text
(T,F,H circuit)
    -> common factors of Res(T,H),Res(F,H) plus exact source jets
```

to a bounded number of ordinary dense univariate modular compositions. The
published input is a dense coefficient vector, while P1513 must preserve the
`r^2`-leaf bivariate circuit and avoid its `r^3` coefficient/evaluation images.
The common-norm operation, multiplicity stratification, and target/start source
inverse are additional obligations. Therefore Kedlaya-Umans is an open
reduction target, not a positive complexity result for P1513.

## Primary References

- Neiger, Salvy, Schost, and Villard, "Faster modular composition using two
  relation matrices": https://arxiv.org/abs/2601.17422
- Kedlaya and Umans, "Fast Polynomial Factorization and Modular Composition":
  https://doi.org/10.1137/08073408X
- Moroz and Schost, "A Fast Algorithm for Computing the Truncated Resultant":
  https://arxiv.org/abs/1609.04259

These references establish modular-composition and truncated-resultant costs;
none states the P1513 common-norm/source operation.

## Decision

Record a scoped negative for specialization, explicit norms, dense fiber-
product gcd, fixed-point truncated resultants, and the current algebraic
relation-matrix modular-composition family.

Keep P1513 active for exactly one versioned branch: derive a reduction from the
shared bivariate product circuit to a bounded number of Kedlaya-Umans-compatible
degree-`Theta(r^2)` operations while preserving common-factor multiplicity and
all target/start/source labels. If circuit-to-dense conversion, common-norm
reconstruction, or source splitting contains an `Omega(r^(5/2))` term, close
the branch before scaling.
