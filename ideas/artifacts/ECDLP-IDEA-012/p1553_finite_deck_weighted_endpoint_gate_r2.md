# P1553 finite-deck weighted-endpoint gate R2

## Classification

- Owner: existing P1553/P1513/P1551/P1516 frontier; no P1554.
- Evidence: theorem-only producer plus independent red team; no run.
- Status: `REVISE_SCOPED_REDUCTION`.
- Labels: `theorem-only`, `non-run`, `model-bound`,
  `novelty-unverified`.
- Cryptanalytic result: no relation campaign, independent relation-rank
  theorem, factor-log solve, scalar-blind descent, Shoup-bound improvement,
  or ECDLP breakthrough.

This closeout replaces the finite-deck count residual in the P1553 R1
value-channel audit by a strictly weaker decision interface. On every admitted
subdeck, an exact target-labelled relation-existence bit is enough to recover
one signed source by deterministic bisection. Exact counts, zero
multiplicities, characteristic polynomials, and primitive source idempotents
are stronger than necessary.

No such decision operation is constructed inside the required cost rectangle.
The narrow surviving question is the typed `Query2P1` operation below.

## Hash-bound review chain

| Receipt | SHA-256 |
|---|---|
| `ideas/artifacts/ECDLP-IDEA-012/p1553_determinant_value_channel_audit_r1.md` | `5073e39388792ea9cd8a4f7a1fe19f33f2799e59aa85f898148c9712bb963669` |
| `coordination/tasks/TASK-20260718-P1553-FD-REPORTER-P1/candidate_report.yaml` | `3c518d458895c5422b89202d912b090a309962999b29e6406c48c961135958cc` |
| `coordination/tasks/TASK-20260718-P1553-FD-REPORTER-P1/finite_deck_reporter_spec.md` | `fd12ff17055a108ef31e58b2fb813feb1b8dc8eb2950db127a7a623e69a4d77f` |
| `coordination/tasks/TASK-20260718-P1553-TENSOR-RT-R1/red_team_report.yaml` | `0a48143e4b5a25fad52200abf7d43f7094ef18af6df0348ea9aa987ecd15002d` |
| `coordination/tasks/TASK-20260718-P1553-TENSOR-RT-R1/tensor_rank_notes.md` | `c3df381e726745ee3b8b09ceb9273201b22b62ed2d0776c556d63908b30bfbdc` |

The producer verdict is `incomplete_scoped_reduction`. The independent
red-team verdict is `REVISE_SCOPED_REDUCTION`. Both allocate no contract,
solver, fixture, experiment, shared status change, or breakthrough claim.

## Frozen interface

Let the prime-order subgroup have order `N=p^(1+o(1))`, and set

```text
B=N^(1/5).
```

For six source-labelled coloured decks, let

```text
v(A)=(1,x(A),y(A),x(A)^2,x(A)y(A),x(A)^3),
D(A_1,...,A_6)=det(v(A_1),...,v(A_6)),
M(A_1,...,A_6)=1-D(A_1,...,A_6)^(p-1).
```

On the checked pairwise-disjoint affine stratum, `M=1` exactly when the six
signed points sum to `O`. For a fixed target `R`, freeze the sixth row at
`v(-R)` so that `M_R` reports five-source relations summing to `R`.

Repeated cross-colour support, infinity, tangent, vertical, alternate-chart,
and nonreduced cases are not absorbed into this biconditional. A global
reporter must either preserve the checked stratum under every restriction or
supply an exact confluent predicate and charge its costs.

The intermediate target rectangle remains

```text
setup, state, campaign work <= B^(9/4+o(1)),
fresh-target and restriction query <= B^(5/4+o(1)).
```

Passing the rectangle is not sufficient for ECDLP promotion: relation density,
independent rank, factor logs, identical scalar-blind target descent, output,
verification, bit time, and bit memory remain mandatory.

## Exact tensor controls

### Pre-mask determinant tensor

Across an ordered cut of `s` colours, the determinant flattening factors
through the perfect exterior-power pairing

```text
Lambda^s(F_p^6) x Lambda^(6-s)(F_p^6) -> Lambda^6(F_p^6).
```

When every coloured row deck spans `F_p^6`, the exact ordered TT ranks of the
campaign determinant are

```text
[6,15,20,15,6].
```

Consequently its CP rank obeys

```text
20 <= rank_CP(D) <= 720.
```

The lower bound is the central flattening rank and the upper bound is the
Leibniz decomposition; no exact CP-rank claim is made.

For a fixed nonzero target row, the form factors through the five-dimensional
quotient `F_p^6/<v(-R)>`. If every projected colour deck spans that quotient,
the exact ordered TT ranks are

```text
[5,10,10,5],
```

and `10 <= rank_CP(D_R) <= 120`.

These constant ranks construct the determinant-value tensor. They do not
construct its Fermat zero mask or locate a relation.

### Post-mask relation tensor

For a cut `S|S^c` on the checked Cartesian stratum, group partial tuples by
their endpoint sums. Let `r_S` be the number of endpoint values represented on
both sides with opposite signs. The exact flattening rank is

```text
rank Flat_S(M)=r_S.
```

If `Z` is the number of source-labelled relations, then

```text
max_S r_S <= rank_CP(M) <= Z.
```

Endpoint multiplicities enlarge all-ones blocks without increasing each
block's rank. Equality with `Z` holds when one cut separates all relation
paths into distinct endpoints.

This low rank is normally a description of the already-known endpoint
intersection. Sparse CP factors that enumerate relation paths are not a
support-independent constructor. A dense campaign TT with matched-endpoint
rank `Theta(B)` still carries `Theta(B^3)` core state at the middle cuts.

The independent audit corrects the blanket version of that statement:
structured collision-heavy decks can have a public sparse transition TT and
exact convolution before relation support is known. For arithmetic-progression
decks, an `O(B)` endpoint dictionary and polynomial convolution give an exact
reporter. Their endpoint support is only `O(B)`, so a blind target hits with
probability about `B/N=B^-4`; the resulting `B^4` target trials, missing
known-log rank, and missing factor-log path erase the ECDLP advantage.

### Fermat power and Schur products

Entrywise Fermat powering gives

```text
D^[p-1]=J-M.
```

Across each cut,

```text
max(0,r_S-1) <= rank Flat_S(D^[p-1]) <= r_S+1.
```

Symmetric-power bounds and repeated-squaring TT/CP constructions are valid
upper bounds, but standard squaring multiplies ranks before exact
recompression. Contracting before powering introduces cross-source terms and
changes the polynomial. Failure of these standard constructions is not a
lower bound against a support-independent exact recompressor or pivot rule.

## Exact finite-field encoding controls

### Split FFE projector

In the split five-source algebra `A=Map(F_1 x ... x F_5,F_p)`, let `d_R` be
the determinant-value function. Then

```text
m_R=1-d_R^(p-1)
```

is an idempotent relation projector. Its multiplication operator has

```text
rank(m_(m_R)) = dim im(m_(m_R)) = number of source-labelled relations,
Tr(m_(m_R)) = number of relations mod p.
```

For injective actual-point decks, every fixed-target restricted count is at
most `B^4<p`, so the trace is the integer count if the operator is actually
constructed. Standard split-algebra representation has dimension `B^5`; the
balanced explicit aggregation route costs `B^3`. These identities are exact
FFE controls, not a succinct evaluator.

### Characteristic norm

The characteristic norm `Norm(T-d_R)` records the number of zero coordinates
as its `T`-adic order. The zero bit of the dynamically restricted
`Norm(d_R)` therefore realizes exact relation existence on the checked
stratum. Standard norm construction still enumerates `B^3` to `B^5`
complementary source state. A target-uniform, restriction-aware succinct norm
or equivalent decision circuit remains open and unconstructed.

## Minimal source-replay theorem

Define

```text
Exists(R,I_1,...,I_5)=1
```

exactly when the target-labelled restricted Cartesian product
`I_1 x ... x I_5` contains a valid relation.

Assume `Exists` is exact and subset-stable for the admitted predicate. Start
from one positive parent query. Bisect one active colour. Query its left
child; retain it if positive, otherwise retain the right child, which must be
positive because the parent is the disjoint union of its children. Repeat in
all five colours. After

```text
sum_i ceil(log_2 |F_i|)=O(log B)
```

queries, every deck is a singleton. Verify the resulting signed elliptic sum.

Thus an exact existence bit is sufficient for one-source replay. Exact counts
are useful for counting or multiplicity enumeration but are not needed for
bisection. Duplicate source labels can invalidate the simple `B^4<p` count
bound while leaving exact existence meaningful. False determinant zeros can
misroute bisection, so all-strata exactness or a charged complete
false-positive recovery protocol remains mandatory.

This is a conditional search-to-decision reduction already owned by the
P1513/P1551/P1516 and IDEA-138/156/199 operation families. It is not a new
algorithm.

## Typed surviving residual: Query2P1

Partition the five sources as `2+2+1`. The build interface is

```text
BuildPairIndex(F_1,F_2), BuildPairIndex(F_3,F_4).
```

Each index stores source-labelled pair-sum divisors and every canonical dyadic
pair of source restrictions. Every leaf pair belongs to only
`O(log^2 B)` dyadic ancestor pairs, so both indexes require

```text
O(B^2 log^2 B)
```

work and source-occurrence state, within `B^(9/4+o(1))`.

The query interface is

```text
Query2P1(R,I_1,I_2,I_3,I_4,I_5) -> exact Exists.
```

Returning the exact coefficient or exact zero multiplicity is permitted but
stronger than required. The query must work for a fresh target and canonical
dyadic restrictions within `B^(5/4+o(1))` work and workspace, without
constructing a `B^3` complementary pair-plus-singleton object or a `B^4`
pair-pair composed sum.

Writing pair multiplicities as `m_12(u)`, `m_34(v)`, and `m_5(a)`, the exact
coefficient is

```text
C_R = sum_(u+v+a=R) m_12(u)m_34(v)m_5(a).
```

Standard point-basis evaluation scans `B^2` pairs for one fifth point and
costs `B^3` over the fifth deck. Full pair-pair convolution costs `B^4`.
The standard characteristic-norm form lives in the
`Map(D_34 x I_5,F_p)` algebra of dimension `B^3`. Swapping the pair indexes
does not change the bound.

Therefore the two pair indexes pass setup, but no audited standard query
passes the target cap. This is the same operation-level frontier as:

- P1513: translated-product/common-norm selector; standard norm costs `B^3`.
- P1551: endpoint coefficient with explicit `B^3/B^5` aggregation.
- P1516: `B^2` pair state with the target-local collision router missing.

No cited theorem closes arbitrary arithmetic or Boolean circuits, dynamic
data structures, word-RAM or cell-probe structures, randomized exact methods,
special elliptic transforms, or target-specialized characteristic norms.
`Query2P1` is therefore an unconstructed typed exception, not a lower bound
and not P1554.

## Complete-path gate

Even a passing `Query2P1` must still prove all of the following on generic
prime-field inputs:

- exact confluent source replay on every admitted restriction;
- sufficient relation density and `Theta(B)` independent factor-base rows;
- factor-log completion and verification;
- the identical target-uniform operation for scalar-blind `Q+[t]P` descent;
- ambiguity, failure, retry, output, bit-time, and bit-memory accounting;
- complete exponents `lambda,mu <= 0.45`.

None is supplied by the tensor, FFE, norm, or structured-deck controls.

## Disposition

`REVISE_SCOPED_REDUCTION__EXACT_PREMASK_TT_RANKS_AND_CP_BOUNDS__POSTMASK_RANK_IS_MATCHED_ENDPOINT_COUNT_ON_CHECKED_STRATUM__LOW_RANK_NORMALLY_POST_SUPPORT_WITH_STRUCTURED_SMALL_SUMSET_EXCEPTION__FFE_PROJECTOR_AND_NORM_IDENTITIES_EXACT__SUBSET_STABLE_EXISTENCE_BIT_SUFFICES_FOR_O_LOG_B_SOURCE_REPLAY__TWO_DYADIC_SOURCE_LABELLED_B2_PAIR_INDEXES_FIT_SETUP__STANDARD_2_PLUS_2_PLUS_1_QUERIES_RESTORE_B3_OR_B4__QUERY2P1_SPECIALIZED_CHARACTERISTIC_NORM_OR_DECISION_OPERATION_UNSUPPLIED__P1513_P1551_P1516_OPERATION_MERGE__ALL_STRATA_RANK_LOGS_AND_DESCENT_UNSUPPLIED__NO_P1554__NO_RUN__NO_BREAKTHROUGH`.

No contract, solver, fixture, experiment, relation campaign, factor-log solve,
blind descent, scalar recovery, Shoup-bound improvement, or breakthrough is
authorized or claimed.

## Exactly one next action

Under existing P1553/P1513/P1551/P1516 ownership, write one
coefficient-complete theorem-only `Query2P1` interface. Preprocess two
source-labelled dyadic pair-divisor indexes within `B^(9/4+o(1))`; for a
fresh target and dyadic fifth-deck restrictions, return exact relation
existence within `B^(5/4+o(1))` without `B^3` complementary traffic or a
`B^4` composed sum; then prove `O(log B)` bisection, all-strata verification,
relation rank, factor logs, and identical blind descent. Either supply a
specialized restriction-aware characteristic norm or data structure with all
coefficients and costs, or preserve this residual and every unrestricted
circuit/data-structure exception. Create no P1554, contract, solver, fixture,
experiment, or breakthrough claim.
