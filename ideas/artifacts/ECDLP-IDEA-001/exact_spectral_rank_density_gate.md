# IDEA-001 exact spectral rank/density gate

Status:
`SCOPED_NEGATIVE_EXACT_LINEAR_TARGET_UNIFORM_SPECTRAL_FACTOR_WITH_ONE_WITNESS__NONLINEAR_MULTIROW_ROUTER_OPEN`

This is a theorem-only producer receipt. No contract, character table, tensor,
curve fixture, relation search, or timing run was created. It screens the exact
target-uniform low-rank mechanism stated by IDEA-001; it is not a lower bound
against arbitrary nonlinear arithmetic circuits or implicit multirow source
routers.

## Frozen incidence interface

Let `G=<P>` have prime order `N`, let `F subset G` be a target-independent
factor base of size

```text
B = N^beta,
```

and let `m>=2` be fixed. Over any coefficient field, define the exact ordered
incidence tensor

```text
I(R;x_1,...,x_m) = 1 if R=x_1+...+x_m, and 0 otherwise,
```

for `R in G` and `(x_1,...,x_m) in F^m`. Signs, unordered tuples, repeated
points, and Kummer projection change constant multiplicities or the source
index set but not the argument below once the admitted source convention is
frozen.

IDEA-001 asks for an exact target-uniform separated character factorization
with retained components and one verified decomposition returned for each
successful known-log target. Write

```text
I(R;x) = sum_(j=1)^r A_j(R) B_j(x).
```

Every additive-character or ordinary linear low-rank factorization has this
form after its public feature maps are fixed.

## Theorem 1: flattening rank equals endpoint support

Flatten `I` with target rows and source-tuple columns. The column indexed by a
tuple `x` is the standard basis vector

```text
e_(x_1+...+x_m).
```

Therefore

```text
rank(I_(R|x)) = |mF|,
```

where `mF` is the set of attainable group endpoints. Indeed, the distinct
columns are exactly the distinct standard basis vectors indexed by `mF`, and
those vectors are linearly independent.

Every exact separated factorization consequently satisfies

```text
r >= |mF|.
```

This is an exact rank identity, not a toy rank extrapolation. A character basis
may evaluate a full-rank operator quickly in a special representation, but it
cannot call the operator low rank or retain fewer than `|mF|` explicit linear
components.

## Theorem 2: one-witness rank/density tradeoff

Put

```text
S = |mF|.
```

A uniformly sampled known-log target lies in the attainable support with
probability `S/N`. Under the favorable assumption that every supported target
returns one useful independent relation row, collecting `B` rows requires at
least

```text
L_rel >= B*N/S
```

target attempts in expectation. Failed targets, duplicate rows, and rank loss
can only increase this quantity.

Any implementation that explicitly retains the `r` linear components and
explicitly handles the one-witness target attempts therefore has the favorable
work/state lower envelope

```text
W >= max(S, B*N/S).
```

Minimizing over the unknown support size gives

```text
W >= sqrt(B*N) = N^((1+beta)/2).
```

At the campaign value `beta=1/5`, the optimum exponent is

```text
(1+beta)/2 = 3/5,
```

strictly above Pollard rho and the Shoup generic boundary. A large endpoint
support forces linear rank; a small endpoint support lowers relation density by
the reciprocal amount.

The bound is deliberately favorable: it charges neither factorization
construction beyond the retained components, nor witness recovery, source
output, exceptional charts, failed verification, factor-log linear algebra,
blind descent, or memory traffic.

## Multirow and implicit-batch boundary

The theorem matches IDEA-001's stated one-decomposition-per-target linear-rank
API. Two operation classes remain outside it.

First, one successful endpoint may return many independently useful source
rows. Such a successor must expose and charge those rows and prove their matrix
rank. For an explicit `m`-tuple source scan, the expected row supply per uniform
target is `B^m/N`, so obtaining `B` rows still examines

```text
N/B^(m-1)
```

targets on average; at `m=3,beta=1/5` this is again `N^(3/5)`. A genuinely
sublinear multirow source generator is a different nonlinear operation.

Second, a succinct structured target batch might be processed without touching
each target separately. To escape this receipt, the algorithm must map that
implicit batch directly to exact source rows; an FFT of a materialized
`N`-character table, a retained component list, aggregate relation counts, or a
post-hoc witness search does not qualify. This exception is the current
P1515-style nonlinear support/witness router, not the linear rank hypothesis
that IDEA-001 proposed.

## Relation to frozen controls

- P1422 found full pair-state rank for every tested additive-character kernel
  and cubic-or-worse recall-preserving false-positive output.
- P1423 found full ordinary rank even after the exact rational subtraction
  phase was compiled into Cauchy-derivative structure; the nonlinear character
  consumer remained missing.
- IDEA-165 shows that a bounded-degree rational quotient either retains
  quadratic generic pair support, grows exact source lists, or requires the
  same target-local router.
- P1515 states the surviving five-source target-router rectangle: setup at most
  `B^2.25`, query at most `B^1.25`, exact all-strata sources, and complete
  relation/rank/descent accounting.

The finite controls are consistent with the theorem but are not used to prove
it.

## Scoped decision

An exact target-uniform **linear low-rank** character factorization with one
witness per successful target cannot supply IDEA-001's claimed sub-rho path.
The producer branch is scoped negative even before its original promotion
thresholds are tested.

This receipt does not rule out:

1. a nonlinear transposed operation on a succinct target batch;
2. an output-sensitive multirow source generator with proved relation rank;
3. a list-specific finite-field correction that changes support rather than
   linearly refactoring the incidence tensor; or
4. an arithmetic circuit whose cost is not proportional to exact linear rank
   and which returns exact sources without materializing target attempts.

Every survivor must still be generic over the ordinary prime-field curve
family, preserve all signs and exceptional strata, and establish complete time
and memory exponents below `1/2`. A rank identity, count, valid relation, or toy
scalar is not a breakthrough.

## Independent review checklist

1. Verify that each source-tuple column is one standard endpoint basis vector.
2. Verify `rank(I_(R|x))=|mF|` over any coefficient field.
3. Verify the favorable one-witness attempt count `B*N/|mF|`.
4. Minimize `max(S,B*N/S)` and recover `N^((1+beta)/2)`.
5. Confirm that implicit target batching and multirow nonlinear source routing
   remain outside scope.
6. Confirm that no toy P1422/P1423 observation is used as theorem evidence.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>
