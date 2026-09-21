# IDEA-098 compressed-navigator gate v1

Status:
`OPEN_REPRESENTATION_SEPARATION__KNOWN_KSUM_CONTROLS_FAIL`

This is a theorem-only, literature-backed preflight receipt. No P1515 contract,
prototype, relation campaign, or experiment was run. The receipt sharpens the
only exception left open by `squarefree_source_gate.md`: a target-independent
compressed grammar with a target-local exact navigator. It does not prove that
such a grammar exists or that it is impossible.

## Frozen five-source interface

Let `G=<P>` have prime order `N`, let the signed factor alphabet have size
`Theta(B)`, and set

```text
B = N^(1/5).
```

For a public target `R`, the navigator must return exact signed source tuples

```text
(a_1,...,a_5) in A^5,
a_1 + ... + a_5 = R,
```

including repetitions, infinity charts, sign-fixed points, output collisions,
and nonreduced strata. Ordering and global-sign conventions may change constant
factors but not the exponents below.

The target-independent grammar has setup time and peak state `B^s`. One target
query, including exact source lifting and independent elliptic verification,
has time and working state `B^q`, apart from charged output.

The random known-scalar campaign needs `Omega(B)` targets at this balance: the
five-source deck has `Theta(B^5)=Theta(N)` members and hence constant average
fiber size, while factor-log rank requires `Theta(B)` source rows. Therefore
the optimistic complete time floor is

```text
lambda >= max(s/5, (1+q)/5, 2/5, 1/5),
```

where `2/5` is the favorable sparse factor-log solve allowance. Before blind
descent, failures, and output multiplicity are charged, the P1515 cap
`lambda<=0.45` already requires

```text
s <= 2.25,
q <= 1.25.
```

These are necessary gates, not a sufficiency claim.

## Control 1: explicit two-versus-three indexing

Let `A_2` and `A_3` be the source-labelled pair-sum and triple-sum multisets.
They have sizes `Theta(B^2)` and `Theta(B^3)` before output collisions.

Two direct orientations are available:

| stored side | setup | per-target scan | complete campaign floor |
|---|---:|---:|---:|
| `A_2` | `B^2` | `B^3` | `B^4 = N^0.8` |
| `A_3` | `B^3` | `B^2` | `B^3 = N^0.6` |

The second line includes `B` target queries. Both retain exact sources, but both
miss the P1515 gate. Hashing, sorting, or replacing points by recursive-`S3`
endpoint encodings does not alter these dimensions if the corresponding side is
still materialized or scanned.

Batching the `B` known targets turns the task into one source-labelled six-list
sum instance: three source entries on one side and two source entries plus a
target on the other. The standard meet-in-the-middle control materializes
`Theta(B^3)` states. This is a `N^0.6` control, not a lower bound against every
field-specific representation.

## Control 2: current `kSUM`-indexing tradeoffs

Dinur and Golovnev define `kSUM`-Indexing so a query asks for `k-1` input values
whose sum is the target. Their 2026 Theorem 2 gives, for input length `n` and
`0<=delta<=1`, the upper bound

```text
S = soft-O(n^(k-0.5-delta)),
T = soft-O(n^delta),
```

with preprocessing time `soft-O(n^(k-1))`.

A five-source query is their `k=6` case with `n=B`, so even granting an
optimistic transfer from integer addition to source-labelled elliptic addition,

```text
S = soft-O(B^(5.5-delta)),
T = soft-O(B^delta),
preprocessing = soft-O(B^5).
```

The smallest setup exponent in the theorem's range is `s=4.5` at `delta=1`.
This is twice the permitted `s<=2.25` exponent, while preprocessing itself is
the full universal source-deck exponent.

The asymmetric theorem gives the same warning. For the `A_2`/`A_3` split with
list lengths `n=B^2` and `m=B^3`, its bound

```text
S = soft-O(n^(1.5-delta) * m) = soft-O(B^(6-2*delta)),
T = soft-O(n^delta) = soft-O(B^(2*delta)).
```

Keeping `q<=1.25` forces `delta<=5/8` and hence `s>=4.75`. At `delta=1`, setup
falls only to `B^4` and query rises to `B^2`. Neither point approaches the
P1515 rectangle.

This literature result is an upper-bound control, not an impossibility theorem.
It also works in a different algebraic setting and does not establish a
source-complete elliptic-group data structure. Its relevance is narrower: the
best checked generic sum-indexing substitution does not supply the missing
compressed navigator.

## Representation-separation gate

A P1515 successor must identify a field-coordinate operation that is absent
from all controls above. Merely presenting group sums with Semaev equations,
choosing a Grobner backend, or renaming sum states as faces does not qualify.

The successor must freeze and prove all of the following before code:

1. **Concrete family.** One target-independent recursive-`S3` ideal, projective
   charts, weight order, squarefree initial complex, and deformation map over
   the relevant prime fields.
2. **Small grammar.** A source-biconditional grammar constructible and resident
   in `B^(2.25+o(1))` time and words, with no generated `A_3`, five-source deck,
   dense Macaulay object, or equivalent lift dictionary.
3. **Target-local navigation.** For every public target, an exact accepted-facet
   query in `B^(1.25+o(1))` time and state, including failed targets and all
   output branches.
4. **Exact lift.** A public inverse from every reported facet through the flat
   family to signed factor-base identities on every exceptional and nonreduced
   stratum, followed by direct elliptic verification.
5. **Non-generic witness.** One proved structural identity used by the grammar
   that is not simulable from black-box group addition, equality, hashing, and
   source tables at the same cost. Otherwise the proposal is only generic
   `kSUM` indexing; a complete below-square-root DLP pipeline would conflict
   with the generic-group boundary rather than evade it.
6. **Full recurrence.** Relation yield, duplicate rows, rank, sparse factor-log
   solve, blind masked descent, ambiguity, verification, and peak memory all
   remain at `lambda,mu<=0.45`.

Any claimed compression that omits source labels, exceptional strata,
preprocessing time, or the target-to-facet routing procedure fails this gate.
A short squarefree generator list is not evidence for a small facet navigator.

## What remains genuinely open

The source deck and current sum-indexing algorithms do not prove that a
recursive-`S3` initial complex lacks a compact target-routing recurrence. The
open mathematical question is therefore narrower than IDEA-098's original
hypothesis:

```text
Does one explicit target-uniform term order expose a recursive-S3
Stanley-Reisner grammar whose target routing and exact source lift satisfy
s<=2.25 and q<=1.25 because of a proved finite-field coordinate identity?
```

No such term order, grammar, recurrence, or identity is presently supplied.
Consequently the surviving lane is `open`, `model-bound`, and
`novelty-unverified`; it has no positive algorithmic evidence.

## Controls and nonclaims

- Explicit pair/triple tables and offline six-list meet-in-the-middle are
  dimension controls.
- Dinur-Golovnev `kSUM`-Indexing is an optimistic current-literature control.
- A planted squarefree complex with a supplied source/facet table is only a
  correctness control; the table is fully charged.
- The `B^2.25/B^1.25` rectangle is a necessary P1515 gate, not a proved lower
  bound for arbitrary algebraic circuits.
- No relation campaign, factor-log solve, blind descent, generic-group lower
  bound improvement, or ECDLP breakthrough is claimed.

## Exactly one next action

Write `recursive_s3_grammar_spec_v1.yaml`: freeze one concrete projective
recursive-`S3` ideal and target-independent weight order, enumerate its grammar
nonterminals symbolically, and derive setup/query/source-lift recurrences against
the `s<=2.25`, `q<=1.25` gate. Reject the version immediately if any recurrence
materializes `B^3` states or uses a post-hoc source dictionary. Do not implement
or time a solver.

## Primary references

- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*, v2:
  <https://arxiv.org/abs/2512.04258>.
- Golovnev, Guo, Horel, Park, and Vaikuntanathan, *Data Structures Meet
  Cryptography: 3SUM with Preprocessing*:
  <https://arxiv.org/abs/1907.08355>.
- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.

The first two references supply sum-indexing controls, the third supplies the
neighboring field-coordinate relation representation, and the fourth supplies
the generic square-root comparison boundary. None supplies the frozen
recursive-`S3` grammar required by this gate.
