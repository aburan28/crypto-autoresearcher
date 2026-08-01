# IDEA-121 Direct KU Circuit-Reduction Gate

Status: `SCOPED_NEGATIVE_STANDARD_KU_EMBEDDINGS_NEW_OUTPUT_SENSITIVE_OPERATION_OPEN`

This receipt executes IDEA-121's remaining direct Kedlaya-Umans action. It
freezes the exact input/output interface and charges the four standard ways of
presenting the shared circuit to modular composition, power projection, or
triangular-set norm algorithms. All four restore at least cubic base-field or
bit traffic. This is a format-and-dimension obstruction for those reductions,
not an arithmetic-circuit lower bound and not evidence against every possible
specialized common-factor extractor.

## Frozen Interface

Let `K=F_p`, let `B=N^(1/5)`, and set `n=Theta(B^2)`. The input is

```text
T(U), F(U) in K[U],                         deg(T)=deg(F)=Theta(B),
H(U,W)=product_(i,j) P_(i,j)(U,W),          B^2 constant-degree leaves,
N_T(W)=Res_U(T(U),H(U,W)),                  deg(N_T)=Theta(B^3),
N_F(W)=Res_U(F(U),H(U,W)),                  deg(N_F)=Theta(B^3).
```

The required output is the squarefree common factor

```text
G(W)=gcd(N_T(W),N_F(W)),                    expected deg(G)=Theta(B),
```

together with multiplicity, target, factor-start, both transition pairs,
sign, chart, and exact elliptic replay. The output must be obtained from the
one product circuit, not from `B` specialized P1510 products or either dense
norm.

The rho comparison is

```text
Pollard rho = N^(1/2+o(1)) = B^(5/2+o(1)).
```

Since `p=N^(1+o(1))`, factors polynomial in `log(p)` are `B^o(1)` in the
campaign exponent accounting.

## What A KU Call Actually Receives

Kedlaya-Umans modular composition takes dense univariate polynomials over a
specified finite coefficient ring. Its general finite-ring theorem costs
roughly the number of ring coordinates times `log(|R|)`; modular power
projection is the transpose of the same dense linear map and retains the same
coefficient ring and coordinate widths. It does not accept a bivariate product
circuit plus an instruction to emit only a nonlinear gcd.

Poteaux and Schost make the dimension charge explicit for triangular sets. If
`A=K[Y_1,...,Y_s]/<calT>` has vector-space dimension `delta`, multiplication,
inversion, and norm computation cost `delta^(1+epsilon) log(p)` up to stated
polylogarithmic terms. Modular composition and power projection with output
parameter dimension `delta_e` cost `(delta+delta_e)^(1+epsilon) log(p)`. The
near-linearity is in the represented quotient dimension, not in the final
factor degree.

## Route A: Coefficients In The Selector Algebra

For the target selector define

```text
R_T = K[U]/(T),                             dim_K(R_T)=Theta(B).
```

Reducing the shared circuit modulo `T` makes `H_T(W)` a degree-`n` polynomial
over `R_T`. A standard degree-`n` KU instance therefore has `Theta(n)` ring
coordinates, each containing `Theta(B)` base-field coordinates:

```text
dense input/output width = n * dim_K(R_T) = Theta(B^3).
```

Equivalently, `|R_T|=p^Theta(B)`. Substituting `d=n=Theta(B^2)` into the KU
finite-ring bit bound gives, for every fixed positive `epsilon`,

```text
d^(1+epsilon) log(|R_T|)
    = B^(2+2*epsilon) * Theta(B log p)
    = B^(3+2*epsilon+o(1)).
```

Letting `epsilon` tend slowly to zero does not remove the factor `B` in
`log(|R_T|)`. The same calculation holds for `R_F=K[U]/(F)`. Constructing the
dense `R_T[W]` coefficient vector from the `B^2` leaves already writes
`Theta(B^3)` base-field coordinates, before norm, gcd, multiplicity, or source
work.

**Decision:** a KU call over the selector coefficient algebra is a cubic
route, not a degree-`B^2` base-field route.

## Route B: Query-Modular Norm In A Triangular Algebra

Suppose a proposed reduction introduces a monic query polynomial `C(W)` of
degree `q` and asks only for a selector norm modulo `C`. The exact algebra is

```text
A_(T,C) = K[U,W]/(T(U),C(W)),               dim_K(A_(T,C))=Theta(B*q).
```

The triangular-set norm theorem consequently charges

```text
(B*q)^(1+epsilon) log(p)
```

bit operations, up to the theorem's polylogarithmic terms. At the proposed
degree-`B^2` query width, `q=Theta(B^2)`, this is

```text
B^(3+3*epsilon+o(1)),
```

already above `B^(5/2)`. This is the precise selector-lift that the informal
phrase "one degree-B^2 KU operation" omits.

Taking `q=Theta(B)` would reduce the represented dimension to `Theta(B^2)`,
but it is not an algorithm unless `C` is proved to contain `G`. For any supplied
`C`,

```text
gcd(C, N_T mod C, N_F mod C)
```

can recover only common roots already present in `C`. An independent random
modulus has no completeness guarantee, while constructing a degree-`Theta(B)`
`C` divisible by the unknown `G` is exactly the missing output-sensitive
common-factor operation. Crediting `q=deg(G)` therefore assumes the desired
answer as input.

**Decision:** query-modular norm is cubic at the admitted `B^2` query width;
the quadratic-width variant is circular unless a new common-root locator is
supplied.

## Route C: Kronecker Or Primitive-Element Flattening

Flattening `R_T[W]` to one base-field quotient does not erase coordinates. The
selector degree and endpoint degree multiply:

```text
dim_K(R_T[W]/(C or h)) = Theta(B*n) = Theta(B^3)
```

for a degree-`n` endpoint modulus. A primitive representation or Kronecker
encoding therefore yields a degree-`Theta(B^3)` univariate operation. Applying
KU to that flattened object is near-linear in `B^3`, not `B^2`.

**Decision:** primitive-element conversion changes the basis, not the
base-field dimension.

## Route D: Direct Multivariate Multipoint Evaluation

The KU reduction to multivariate multipoint evaluation takes a dense
multivariate polynomial coefficient array. Expanded as a generic bivariate
polynomial of individual degree `Theta(n)`, `H(U,W)` has a potential
`Theta(n^2)=Theta(B^4)` coefficient rectangle. Keeping the `B^2` product leaves
avoids that expansion, but then the standard KU multipoint interface has no
product-circuit input: evaluating all leaves at all selector/query points or
first converting their product to the dense array restores the omitted
traffic.

This does not prove that product circuits can never be handled faster. It
proves only that citing KU's dense multipoint theorem does not supply the
required circuit algorithm.

## Why Power Projection Does Not Remove The Lift

For degree `d`, modular power projection returns `d` values in the same
coefficient ring `R` and is the transpose of the dense modular-composition
linear map. With `d=Theta(B^2)` and `R=R_T`, its represented output alone has

```text
d * dim_K(R_T) = Theta(B^3)
```

base-field coordinates. Transposition preserves this domain/codomain width. It
also remains a linear operation in the transposed argument, whereas
`gcd(N_T,N_F)` and unknown common-root localization are nonlinear. No cited
transposition theorem turns a compact linear projection into an output-
sensitive gcd.

Requesting only `Theta(B)` moments does not locate arbitrary common roots. A
fixed truncation can hide different gcds: for `k<D`, the pairs

```text
(W^D, W^D)                    and
(W^D, W^D + W^k)
```

are identical modulo `W^k`, but their gcds are `W^D` and `W^k`. This is a
generic truncation control, not a claim that every P1513 norm realizes this
pair. It prevents a fixed-jet argument from being promoted without an
additional theorem for the shared elliptic circuit family.

## Locator Versus Source Decoder

This screen isolates the locator as the unresolved operation. If the exact
degree-`Theta(B)` factor `G` were already supplied, marker components could be
reduced in

```text
K[U,W]/(T(U),G(W))    and    K[U,W]/(F(U),G(W)),
```

each of dimension `Theta(B^2)`. A constant number of P1510 marker/Hasse
components could therefore plausibly remain below rho, subject to the existing
source-biconditional and exceptional-chart checks. This conditional decoder
does not find `G`, and it does not make an unlabeled gcd sufficient.

Conversely, carrying all selector-norm marker components before `G` is known
retains the same cubic selector lift as the unmarked constant component. Source
jets neither repair nor worsen the leading exponent of the screened KU routes;
they remain mandatory after a locator is found.

## Complete Exponent Receipt

| object or route | base-field/bit exponent in `B` | exponent in `N` | decision |
|---|---:|---:|---|
| shared leaf circuit input | `2+o(1)` | `0.4+o(1)` | favorable input control |
| expected common factor output | `1+o(1)` | `0.2+o(1)` | favorable output control |
| hypothetical source decode given `G` | `2+o(1)` | `0.4+o(1)` | conditional only |
| rho | `2.5+o(1)` | `0.5+o(1)` | comparison boundary |
| KU over `K[U]/T`, degree `B^2` | `3+o(1)` | `0.6+o(1)` | fail |
| triangular norm modulo degree `B^2` query | `3+o(1)` | `0.6+o(1)` | fail |
| primitive/Kronecker flattened operation | `3+o(1)` | `0.6+o(1)` | fail |
| dense bivariate KU input rectangle | up to `4+o(1)` | up to `0.8+o(1)` | fail |

The time gate fails before relation density, rank, factor-log solving, failed
batches, or blind descent can be credited. Streaming may lower peak state for
some individual algorithms, but it cannot repair the cubic time recurrence.

## Mutation-Rejection Requirements

An executable gate for this receipt must reject each of the following:

1. charge one operation in `K[U]/T` as one base-field operation;
2. omit `log(|K[U]/T|)=Theta(B log p)` from the KU bit bound;
3. set the query degree to `deg(G)` without supplying a divisible query modulus;
4. claim that an independent random modulus contains every unknown common root;
5. flatten the selector and endpoint variables while retaining only the larger
   degree instead of their product;
6. treat modular power projection as a nonlinear gcd/common-root operator;
7. feed a product circuit to a theorem whose input is a dense coefficient
   array without charging conversion;
8. promote a conditional source decoder given `G` as a common-factor locator.

## Primary References

- Kedlaya and Umans,
  [Fast Polynomial Factorization and Modular Composition](https://users.cms.caltech.edu/~umans/papers/KU08-final.pdf),
  especially Theorems 7.1 and 7.7 and Problem 7.3.
- Poteaux and Schost,
  [Modular Composition Modulo Triangular Sets and Applications](https://cs.uwaterloo.ca/~eschost/publications/mulmodcomp.pdf),
  especially Theorem 1 and the quotient-dimension definition preceding it.
- Neiger, Salvy, Schost, and Villard,
  [Faster Modular Composition](https://arxiv.org/abs/2110.08354), for the
  algebraic base-field modular-composition control.
- Neiger, Salvy, Schost, and Villard,
  [Faster Modular Composition Using Two Relation Matrices](https://arxiv.org/abs/2601.17422),
  for the current algebraic degree-`n` control already screened in P1513 R1.

## Decision Boundary

The standard KU coefficient-ring, query-modular triangular, primitive-element,
dense-multivariate, and transposed-power-projection embeddings are scoped
negative. They do not realize IDEA-121's promised bounded number of genuine
degree-`B^2` base-field operations; each either exposes a cubic represented
algebra or assumes the unknown common factor in its query modulus.

This does **not** rule out a new product-circuit algorithm whose complexity is
near-linear in the `B^2` leaves plus the `B` common output. Such an algorithm
would no longer follow from standard KU as a black box and must supply its own
nonlinear locator recurrence and exact source inverse. No relation collection,
factor logs, blind descent, or generic ECDLP speedup has been produced.
