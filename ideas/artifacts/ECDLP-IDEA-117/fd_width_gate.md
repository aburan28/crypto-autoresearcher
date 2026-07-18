# IDEA-117 / P1511 FD-Width And Iterator Gate

Status: `REVISE_NO_SUB_R1P5_IMPLICIT_ITERATOR_DERIVED`

This is a theorem-preflight receipt, not a run and not a lower bound against
all ECDLP algorithms. It evaluates the exact degree-aware provenance-join
mechanism against the newly verified P1510 source-coded compiler.

## Required Claim

On the frozen ordinary prime-order family `q = Theta(r^5)`, IDEA-117 needs a
complete per-target source query exponent `alpha < 3/2`. With `Theta(r)` rows,
the dense-regime relation cost is `r^(1+alpha)`, which is below Pollard rho
`r^(5/2)` only when `alpha < 3/2`.

P1510 has `alpha=2` for its complete per-target endpoint object. It therefore
cannot satisfy IDEA-117 merely by replacing explicit pair enumeration with a
dense coefficient vector.

## Exact Relational Schema

Let `D` be the oriented factor deck, `|D|=Theta(r)`, and let `T` contain
`Theta(r)` public targets. A five-factor relation is

```text
R_t = P_i + P_j + P_k + P_l + P_m.
```

Introduce serial intermediate points

```text
V = R_t - P_i
W = V - P_j
U = P_k + P_l
W = U + P_m
```

with the constant-size sign charts required when only x-coordinates are
retained. The source-complete natural join is the path

```text
E1(t,i,V) join E2(V,j,W) join E4(U,m,W) join E3(k,l,U).
```

Every transition triple is a quasigroup graph: any two of its point/source
attributes determine the third once the oriented source catalog is fixed.
These are genuine functional dependencies, but they determine intermediate
values only after their source indices are chosen.

The same relation is the source-labelled intersection

```text
A2(t,i,j,W) join A3(k,l,m,W).
```

It is also a six-list zero-sum instance over five copies of `D` and the
negated target list. Rewriting the join does not change this candidate-supply
obligation.

## Input And Output Sizes

For one target:

```text
|E1| = Theta(r)
|A2| = |E1 join E2| = Theta(r^2)
|E3| = Theta(r^2)
|A3| = |E3 join E4| = Theta(r^3).
```

Across `Theta(r)` targets, the complete `A2` union and the target-independent
`A3` relation both have `Theta(r^3)` source rows. The final join is sparse on
the frozen random-support model, with only `Theta(r)` rows needed and expected,
but sparse output does not make either explicit input relation free.

The P1490/P1491 fixtures support the degree model rather than a heavy-bucket
collapse. At selector degrees `r=4,4,7,12`, the exhaustive A3 source counts are
`120,120,560,2600`, with `41,48,238,1168` distinct x-support values. P1505 also
shows that endpoint x alone does not functionally determine provenance: every
endpoint is ambiguous, with maximum canonical multiplicities `8,8,14,24` on
the corresponding two-step cells.

## Closed-Set Finding

The transition FDs close an intermediate point after adjacent source
attributes are fixed. They do not close any unfixed source attribute from a
smaller source subset. Consequently:

- the natural join is already acyclic as a query over explicit transition
  relations;
- a worst-case-optimal or Yannakakis-style join can be linear in explicit
  input plus output;
- the explicit input construction is nevertheless `Theta(r^3)` because E2 is
  generated on `Theta(r^2)` `(V,j)` choices across the target batch and E4 on
  `Theta(r^3)` `(U,m)` choices;
- the FD/closed-set theorem does not supply the missing implicit neighbor
  iterator that avoids those choices.

This is the central correction to the original IDEA-117 framing: the load-
bearing unknown is not an improved join order or a smaller AGM/GLVV output
bound. It is an exact algebraic semijoin iterator that prunes nonincidences
before constructing the explicit transition relations while retaining source
backpointers.

[NPRR](https://arxiv.org/abs/1203.1952) gives worst-case-optimal algorithms in
terms of supplied relation sizes. [Abo Khamis, Ngo, and
Suciu](https://arxiv.org/abs/1604.00111) extends this to functional dependencies
and degree bounds through a closed-set lattice. Neither theorem constructs an
elliptic transition relation that is absent from the input.

## P1510 Integration

For one target, P1510 replaces the explicit A2 source table and P1509's cubic
all-key opening with 15 source-marked coefficient polynomials. The object has
`Theta(r^2)` dense coefficient slots and is constructed in

```text
O(r^2 + r M(r) log r + M(r^2) log r)
```

work and `O(r^2)` state. Its Hasse section recovers provenance after an
endpoint is opened. It does not decide which A2 endpoint lies in A3.

The following exact compositions retain a cubic term:

| Route | Charged object | Bound |
|---|---|---:|
| P1510 once per target | `Theta(r)` dense A2 coefficient vectors | `Theta(r^3)` slots |
| explicit provenance join | A2 target union plus A3 | `Theta(r^3)` input rows |
| dense polynomial semijoin | product of target A2 polynomials or A3 polynomial | degree `Theta(r^3)` |
| pointwise P1491 scan | supplied A3 candidates | `Theta(r^3)` candidates before query cost |
| quotient-module kernel | union endpoint algebra | dimension `Theta(r^3)` |

Fast polynomial multiplication changes logarithmic factors, not these dense
degree or source-row exponents.

## Surface-Pair Reformulation

The A3 side can be partitioned by its first source:

```text
A3 = union_k A2(P_k).
```

Thus P1511 can test whether the P1510 endpoint polynomial for target `R_t`
shares a root with the endpoint polynomial for factor start `P_k`. A common
root gives a complete five-factor row after the two P1510 source sections are
replayed.

This is exact and source-preserving, but it creates `Theta(r^2)` surface-pair
queries across `Theta(r)` targets and `Theta(r)` starts. A fixed pair is a
four-sum membership problem between two size-`Theta(r^2)` pair surfaces.
Generic dense gcd/resultant work is soft-`Theta(r^2)` per pair. No constant or
`o(r^(1/2))` amortized surface-intersection predicate is derived here, so this
reformulation does not pass the campaign bound.

## Decision

IDEA-117's current FD-width mechanism is `REVISE`, not promoted:

1. the exact source-labelled query and its FDs are now explicit;
2. the query is acyclic once its relations are supplied;
3. current exact relation construction or P1510 compression still has
   exponent at least two per target or cubic over the row campaign;
4. no FD theorem supplies the missing source-preserving implicit iterator;
5. no unconditional lower bound against every factorized algebraic semijoin is
   claimed.

Correct joins, P1510 endpoint compilation, endpoint hits, toy full rank, and
toy key recovery remain outside the breakthrough boundary.

## Next Admissible Operation

The only P1511 continuation that is mechanism-distinct is a factorized
source-marked semijoin oracle. It must take P1510-style product circuits for an
A2 surface and the partitioned A3 family, return only their common factors and
source jets, and prove total campaign work `o(r^(5/2))` without expanding a
degree-`Theta(r^3)` polynomial or issuing all surface-pair queries.

If its derivation reduces to dense gcd/resultant input, one P1510 call per
target, an explicit A3 iterator, or generic join execution, P1511 should close
as a scoped negative and the campaign should change representation.
