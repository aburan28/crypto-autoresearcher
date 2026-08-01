# P1514 nonlinear apolar operation theorem receipt v2

## Versioned correction

Status:
`CORRECTED_SCOPED_NEGATIVE_SUPPLIED_MOMENTS_AND_ENUMERATIVE_CONSTRUCTORS__STRUCTURED_CONSTRUCTOR_OPEN`

This record preserves and narrows
`nonlinear_apolar_operation_theorem.md` at SHA-256
`4093e48132d96706db1155c44a8ab0f82de5ae997885df56b6ba1074022f297e`.
The original formulas are reproducible, but two interpretations were too broad:

1. The Janovitz-Freireich et al. degree formula is a sufficient Macaulay degree
   bound under its hypotheses. It is not asserted to be the least degree for every
   structured relation fiber.
2. A two-plus-three meet-in-the-middle route has a `B^3` right deck and `B^3`
   enumeration time in the frozen direct implementation. It has `B^3` resident
   memory only when that deck is materialized. A streamed or external-memory route
   must retain its time and I/O charges, but it must not be assigned materialized
   memory automatically.

The v1 producer and audit remain immutable diagnostics. They are not evidence for
the two universal readings rejected here.

## Preserved functional theorem

For a reduced target fiber `S_R`, a faithful source functional can be written

```text
Lambda_R(f) = sum_{z in S_R} w_z f(z),  w_z != 0.
```

Given enough supplied moments, flat extension and border-basis algorithms can
recover its finite multiplication algebra. For nonreduced fibers, one functional
recovers the full multiplicity algebra only if `ann(Lambda_R)=I_R`; otherwise it
represents a proper Gorenstein quotient and a charged multi-functional replacement
is required.

This is a decoder theorem. Laurent-Mourrain flat extension and Mourrain's border-
basis algorithm both begin with truncated functional or multi-index sequence values.
They do not construct relation-weighted moments from `(E,F,R)`.

## Corrected direct-source route

The canonical moments are source-weighted sums:

```text
Lambda_R(X1^a1 ... X5^a5)
  = sum_{(j1,...,j5) in S_R}
      c(j1)^a1 ... c(j5)^a5.
```

A direct five-tuple implementation visits `B^5` states. The frozen two-plus-three
implementation generates `B^2` and `B^3` partial-sum decks. Consequently:

- materializing the right deck costs `B^3` time and memory;
- streaming all right-deck entries costs `B^3` generation time but can use less
  resident memory, with buffering, ordering, I/O, and repeated passes charged;
- applying this direct enumerative route to `Theta(B)` relation targets costs
  `B^4=N^0.8` time.

These are costs of the admitted direct implementations, not a lower bound against
all five-sum, convolution, streaming, or structured source reporters. In particular,
the memory conclusion is now conditional on materialization. The required promotion
threshold remains `B^1.25` time per relation query and `B^2.25` peak memory for the
complete `N^0.45` cap.

## Corrected Macaulay route

Freeze the same favorable dense five-code-variable model: five degree-`B`
membership equations and one degree-`2` relation equation. Applying Theorem 3.5's
`s>m` sufficient bound gives

```text
k = 5B-3,
delta = 5B-2.
```

Instantiating Definition 3.8 at that bound uses
`Delta=max(delta-1,2D)` and therefore at least the coordinate set through
`delta-1=5B-3` in this particular safe-bound construction. Its nullspace vector has

```text
binomial(5B+2,5) = Theta(B^5)
```

coordinates before the subsequent nullspace, moment, trace, and multiplication-
matrix operations.

The valid conclusion is:

```text
the cited generic safe-degree dense Macaulay instantiation fails the cost gate.
```

The invalid conclusion, rejected here, is:

```text
every structured Macaulay or quotient constructor needs that cutoff or B^5 state.
```

A system-specific proof may establish condition (1), a quotient basis, or a sparse/
multihomogeneous representation at a smaller degree. No such proof is currently
known for the source-labelled recursive-`S3` fiber, and any proposed replacement
must charge its construction, source inverse, `B` relation targets, and blind
descent. Its absence is an open mechanism gap, not a lower bound.

## Corrected route table

| Route | Corrected status |
|---|---|
| Supplied flat moments | Decoder positive control; public-input constructor missing |
| Supplied multi-index sequence | Decoder positive control; public-input constructor missing |
| Direct `B^5` source sum | Scoped negative for the enumerative implementation |
| Materialized `B^2` plus `B^3` join | Scoped time and memory negative |
| Streamed `B^3` right-deck enumeration | Scoped time negative; memory not automatically `B^3` |
| Dense Macaulay at cited sufficient degree | Scoped representation negative |
| System-specific low-degree/sparse quotient | Open |
| New structured nonlinear moment oracle | Open |

## Decision

No checked route supplies the explicit IDEA-133 public-input constructor, exact
all-strata source inverse, and complete `lambda,mu<=0.45`. The full P1514 claim is
therefore still not reproduced and the candidate remains `inconclusive`.

The preserved scoped negatives are now exactly:

- treating supplied moments or sequences as a constructor;
- direct `B^5` source enumeration;
- the frozen materialized or fully enumerated two-plus-three implementations; and
- the cited sufficient-degree dense Macaulay instantiation.

Open scope includes structured five-sum algorithms, streamed memory/time tradeoffs,
system-specific low-regularity or sparse quotient constructions, and genuinely new
nonlinear moment oracles. No arithmetic-circuit lower bound, generic Shoup-bound
improvement, relation campaign, factor-log solve, blind descent, or ECDLP
breakthrough is claimed.

## Primary sources

- Monique Laurent and Bernard Mourrain, [A Sparse Flat Extension Theorem for Moment Matrices](https://arxiv.org/abs/0812.2563).
- Bernard Mourrain, [Fast algorithm for border bases of Artinian Gorenstein algebras](https://arxiv.org/abs/1705.01328).
- I. Janovitz-Freireich, B. Mourrain, L. Ronyai, and A. Szanto, [On the computation of matrices of traces and radicals of ideals](https://arxiv.org/abs/0901.2778), especially the sufficient bounds in Theorems 3.4-3.5 and the construction in Definitions 3.8-3.10.

## Exactly one next executable action

Run a fresh independent audit that rejects both the universal-minimum reading of
the sufficient Macaulay cutoff and the unconditional `B^3` memory reading of a
streamed meet-in-the-middle route, while preserving the exact arithmetic formulas
and narrower route decisions above.
