# IDEA-098 squarefree source-shelling gate

Status:
`SCOPED_NEGATIVE_EXPLICIT_UNIVERSAL_FACET_DECK__COMPRESSED_TARGET_NAVIGATOR_OPEN`

This is a theorem-only producer receipt. No contract or experiment was run. It
closes an explicit source-biconditional Stanley-Reisner complex, an explicit
facet dictionary, and a shelling that exposes the universal source deck before
target filtering. It does not close a genuinely implicit target-local navigator
whose construction and queries avoid that deck.

## Frozen interface

Let

```text
G = <P> ~= Z/NZ
```

where `N` is prime. Let `F` be a target-independent factor base of size

```text
B = N^beta,
```

and fix relation arity `m >= 2`. The P1515 arm uses `m in {3,4,5}` and its
main five-source gate uses `m=5`.

Write `A` for the signed factor alphabet. Up to identity and sign-fixed
constant-size exceptions,

```text
|A| = 2B + O(1) = Theta(B).
```

The unordered source deck with repetitions is

```text
D_m = Multiset_m(A),
M_m = |D_m| = binomial(|A|+m-1,m) = Theta(B^m).
```

Using ordered tuples, removing global sign, or separating exceptional charts
changes only a constant factor for fixed `m`. Every `s in D_m` has a public
elliptic output

```text
sigma(s) = sum_(a in s) a in G.
```

The factor-log campaign samples known random scalars `r`, forms
`R_r=[r]P`, and asks for exact source tuples in `sigma^(-1)(R_r)`. A usable
relation row must retain the source coefficients and the known right-hand side
`r`. Enumerating a source tuple first and computing its point does not reveal
the discrete logarithm of that point.

The admitted explicit P1515 representation has all of the following:

1. one target-independent flat Grobner degeneration of the source-labelled
   universal graph;
2. a squarefree initial ideal with a Stanley-Reisner complex;
3. a facet-to-source biconditional, including signs, repetitions, infinity,
   and nonreduced source strata; and
4. an explicit facet list, explicit source annotation, or shelling traversal
   that exposes every universal facet before or while matching known targets.

## Lemma 1: the universal source graph has `Theta(B^m)` labelled points

The graph

```text
Gamma_m = {(s,sigma(s)) : s in D_m}
```

contains exactly one point for each labelled source multiset, even when two
different sources have the same elliptic output. Therefore its source-labelled
degree is at least

```text
M_m = Theta(B^m).
```

Collisions in the output coordinate do not identify graph points because the
source inverse is required to be biconditional. Nonreduced or boundary strata
can add multiplicity or components; they cannot remove the `M_m` reduced
source-labelled points.

## Lemma 2: a squarefree degeneration does not compress explicit source facets

A homogeneous Grobner degeneration preserves the Hilbert function and degree.
If its squarefree initial ideal is source-biconditional, each source-labelled
component has multiplicity one and is represented by a distinct maximal facet.
Consequently an explicit universal Stanley-Reisner representation has at least

```text
M_m = Theta(B^m)
```

source facets. Shellability supplies an order on those facets. It does not make
their explicit list shorter.

This is the precise degree-preservation consequence used below. It does not say
that every fixed target fiber contains all `M_m` facets.

### Affine sanity check

There is an additional representation warning for an unhomogenized
zero-dimensional ideal. If a squarefree monomial ideal

```text
J subset k[x_1,...,x_n]
```

is zero-dimensional, then some power of every `x_i` lies in `J`. Since `J` is
radical, every `x_i` lies in `J`, so

```text
J = (x_1,...,x_n)
```

and the quotient has degree one. Thus an affine fiber of degree greater than
one cannot have a squarefree monomial initial ideal in the same variables.
Homogenization or polarization can produce a nontrivial Stanley-Reisner
complex, but then its degree-one components/facets must still carry the
preserved degree and source labels.

## Lemma 3: known-scalar target yield

For `R in G`, let

```text
d_R = |sigma^(-1)(R)|.
```

Every source has one output, hence

```text
sum_(R in G) d_R = M_m.
```

For a uniformly sampled known scalar `r`, the point `[r]P` is uniform in `G`,
so

```text
E[d_[r]P] = M_m/N.
```

For `T` frozen random known-scalar targets, the expected total number of exact
source rows returned, before deduplication and rank loss, is

```text
E[X_T] = T*M_m/N.
```

Rank `B` requires at least `B` returned rows. Markov's inequality therefore
gives

```text
Pr[rank B] <= Pr[X_T >= B] <= T*M_m/(N*B).
```

Any constant-success campaign in this frozen random-target model requires

```text
T = Omega(N*B/M_m) = Omega(N/B^(m-1)).
```

This lower bound is deliberately favorable: it counts every source as a fresh
independent row, charges no failed lift, and ignores linear dependencies.

An algorithm that selects target scalars using their hidden membership in the
source-output image must separately construct a scalar-labelled image index.
Such an index already contains the source-output discrete-log information that
the relation campaign is trying to obtain and is not free preprocessing.

## Theorem: explicit universal facets miss rho for every fixed arity

An explicit universal facet list or one complete shelling traversal requires

```text
Omega(M_m) = Omega(B^m)
```

work merely to expose the source-biconditional facets. Even if all known targets
are batched and the deck is streamed exactly once, target generation and lookup
also require `Omega(T)` work. Lemma 3 gives the optimistic lower bound

```text
W_explicit = Omega(B^m + N/B^(m-1)).
```

With `B=N^beta`, its time exponent is at least

```text
lambda_explicit >= max(m*beta, 1-(m-1)*beta).
```

The minimum over `beta` occurs where the two terms are equal:

```text
beta_star = 1/(2m-1),
min lambda_explicit = m/(2m-1) > 1/2.
```

For the frozen arities:

| arity `m` | `beta_star` | explicit-facet exponent |
|---:|---:|---:|
| 3 | `1/5` | `3/5 = 0.600000...` |
| 4 | `1/7` | `4/7 = 0.571428...` |
| 5 | `1/9` | `5/9 = 0.555555...` |

The five-source explicit-facet route therefore misses Pollard rho and the
P1515 `0.45` gate even under perfect batching, free elliptic verification,
zero lift failures, and full row independence.

If the facet dictionary is resident, its source identities also require
`Omega(B^m log B)` bits, giving peak-state exponent at least `m*beta` up to
logarithmic factors. Streaming can lower resident memory but cannot remove the
`B^m` time term. Rescanning the deck per target is strictly worse.

## Fixed-fiber correction: degree preservation is not a universal per-query bound

For a fixed target `R`, the exact source-labelled fiber has degree `d_R`, not
`M_m`. If a valid projective squarefree initial ideal exists for that fiber,
its source-biconditional facets number `d_R`. All of those facets are already
accepted because `R` was imposed before degeneration.

Therefore the statement

```text
flatness alone forces every target query to enumerate the full B^m deck
```

is false. At `m=5, beta=1/5`, the average fixed-fiber degree is constant. A
target-local squarefree fiber could be output-small. What remains unproved is
how to construct or navigate that fiber from public curve, factor-base, and
target data without first exposing the universal deck, a dense Grobner object,
or an equivalent tuple dictionary.

This correction prevents the explicit-facet theorem from being misreported as
an unconditional algebraic-circuit or data-structure lower bound.

## Disposition of the P1515 mechanisms

The following routes are scoped negative:

1. materialize all universal source facets and hash their elliptic outputs;
2. stream one complete universal shelling against a batch of known targets;
3. store a facet-to-source or output-to-facet dictionary;
4. replace the facet list by an equally long lift-path or source-annotation
   list; and
5. claim compression from squarefree generators while source recovery still
   enumerates all maximal facets.

The following route remains open:

```text
a target-independent compressed grammar with a target-local exact navigator
that reports sigma^(-1)(R) without constructing or traversing D_m
```

For a grammar with setup `B^s` and per-target query `B^q`, the optimistic
relation-campaign time floor is

```text
lambda_grammar >= max(
    s*beta,
    1-(m-1)*beta + q*beta,
    beta
).
```

At the natural five-source balance `beta=1/5`, the P1515 gate
`lambda<=0.45` requires, before linear algebra and descent are charged,

```text
s <= 2.25,
q <= 1.25.
```

The navigator must also return exact signed sources on every exceptional and
nonreduced stratum, prove that no hidden tuple table or target-selected order is
used, and keep its resident state, output, factor-log solve, and blind descent
within the complete `mu,lambda<=0.45` cap.

Squarefreeness and shellability do not provide that navigator. It is the new
operation that a surviving P1515 successor must actually derive.

## Controls and nonclaims

- Knutson-Miller Schubert degenerations are positive controls for genuine
  squarefree shellable initial complexes, not for elliptic source navigation.
- A planted ideal with a supplied facet/source table is a correctness control;
  its table is charged as explicit source advice.
- A target-local Grobner basis whose construction expands the full source deck
  or a dense Macaulay matrix is an explicit/dense control.
- One valid lifted relation, a short monomial-generator list, or a shellable toy
  complex is not relation collection, factor-log recovery, blind descent, or a
  sub-rho ECDLP algorithm.

No P1515 contract was executed. No relation campaign, factor-log solve, blind
descent, generic-group lower-bound improvement, or breakthrough is claimed.
The IDEA-098 and P1515 states remain coordinator-controlled and unchanged until
independent static review.

## Independent review checklist

An independent reviewer should verify:

1. `|D_m|=Theta(B^m)` for the frozen signed multiset convention;
2. source-output collisions do not identify source-labelled graph points;
3. the flat squarefree facet count is asserted only for the explicit universal
   source-biconditional representation;
4. `sum_R d_R=M_m` and the random known-target expectation are correct;
5. constant-success rank `B` requires `T=Omega(N/B^(m-1))` in the frozen
   random-target campaign;
6. minimizing `max(m*beta,1-(m-1)*beta)` gives `m/(2m-1)>1/2`;
7. the affine squarefree zero-dimensional warning is not incorrectly applied
   to a homogenized or polarized projective complex; and
8. the target-local compressed-navigator exception remains explicitly open.

## Exactly one next action

Write a versioned compressed-navigator gate for the recursive `S3` source map:
freeze the grammar interface, prove or refute setup exponent `s<=2.25`, query
exponent `q<=1.25`, exact all-strata source lifting, and absence of a hidden
`Theta(B^5)` facet/output dictionary before any P1515 code or toy run.

## Primary references

- Knutson and Miller, *Grobner geometry of Schubert polynomials*:
  <https://arxiv.org/abs/math/0110058>.
- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.

The first reference supplies the neighboring squarefree Stanley-Reisner and
shellability control; the second supplies the neighboring elliptic relation
representation; the third supplies the generic square-root comparison
boundary. None gives the missing compressed source navigator or a below-rho
prime-field ECDLP algorithm.
