# TASK-20260719-041 revised multigraded-dual theorem gate

## Record boundary

- Role: idea-generator producer gate; only the Coordinator may change an
  official hypothesis or research status.
- Inputs: `TASK-20260719-039`, independent `TASK-20260719-040`, the BATCH-008
  package, and the P1553 exact-predicate correction.
- Primary control added: Mario Maican,
  [*The Relevant Domain of the Hilbert Function of a Finite Multiprojective
  Scheme*](https://arxiv.org/abs/2408.03477), arXiv:2408.03477v2,
  Theorem 5 and Corollary 6.
- Evidence class: theorem, interface, representation, and complete-cost audit;
  no experiment or empirical observation.
- Authorization: no new ID, proposal, contract, implementation, fixture,
  solver, or compute.
- Scope: the exact cited grammar and its literal natural dense five-deck
  realization, not every sparse, black-box, or elliptic-specific algorithm.

## Corrected semantic ownership and sufficient interface

The permitted operation does not require direct atomization. Its fingerprint is

```text
restricted target-ideal coefficients
  -> exact restriction-stable existence bit
  -> O(log B) charged canonical self-reduction
  -> one labelled singleton and final group verification
  -> independent rows, factor logs, and unchanged masked descent.
```

The existing P1553/Query2P1 residual under IDEA-012 owns the weakest exact
conditional-predicate interface. IDEA-156 is the closest canonical control for
conditional nonvanishing followed by source self-reduction; IDEA-138 controls
the search-to-decision wrapper after such a predicate is supplied. The legacy
P1551 aggregation/unranking artifact is stored under IDEA-195, but current
canonical IDEA-195 has a distinct non-Cartesian intertwiner fingerprint. The
P1553 gate permits counts and multiplicities, but requires only the exact bit

```text
z_(R,I_1,...,I_5)=1[C_(R,I_1,...,I_5) != 0]
```

for every canonical dyadic restriction, followed by `O(log B)` charged
restriction queries and singleton verification.

`ECDLP-IDEA-133` remains the owner of the stronger optional route through a
distinguished faithful functional, multiplication algebra, and direct
reduced/nonreduced atomization. Those outputs are sufficient, not mandatory,
for the corrected existence-bit route. No new semantic owner or ID is needed.

## Cummings--Hauenstein: exact positive and exact boundary

Let `R=C[x_1,...,x_N]`; the source's `N` counts polynomial variables, not the
ECDLP order. For an admissible `M`-grading, grading matrix `A`, homogeneous
ideal `I=<f_1,...,f_t>`, and requested grade `a`, Theorem 3.2 decomposes

```text
D_0(I)=direct_sum_a D_0^a(I).
```

Corollary 3.6 gives the coefficient-derived recursion

```text
C_0^a(I)={delta in D_0^a :
          Phi_i(delta) in D_0^(a-Ae_i)(I) for every i},
D_0^a(I)={delta in C_0^a(I) :
          delta(f_j)=0 for generators of degree a}.
```

`SortLatticePoints(A,B_h,a)` orders all predecessor grades in the saturated,
pointed weight cone. `DualSpace(a,I,A,B_h)` constructs the closedness
preimages, imposes generator nullspace equations, and returns a basis of
`D_0^a(I)`. Proposition 3.4 states

```text
dim_C D_0^a(I)=H_I(a).
```

This is a real coefficient-to-Hilbert-component operation, not a decoder that
starts from supplied moments. An arbitrary basis is enough to obtain its
dimension; no distinguished `Lambda_R`, multiplication matrices, point
section, or primary/nilpotent decomposition is needed merely to test whether
that dimension is zero.

The paper nevertheless works over `C`. It gives no positive-characteristic
dual construction and no arithmetic, bit, memory, component-count,
saturation, point-extraction, restriction-reuse, or output-sensitive
complexity theorem. Its proof-of-concept identifies lattice enumeration as the
most expensive ordering step and leaves complexity analysis to future work.

## Maican control: a conditional exact nonemptiness route

Let `X` be a finite, possibly nonreduced subscheme of a multiprojective space
over an algebraically closed field, and let `I_X` be its multihomogeneous
defining ideal. For each projective factor, let `r_i` be the regularity index
of the scheme-theoretic projection of `X` to that factor.

Maican Theorem 5 states, in particular,

```text
H_X(a)=length(X) whenever a_i >= r_i for every i.
```

If `s_i` is the length of that projection, Corollary 6 supplies the safe
coordinatewise bound

```text
a_i >= s_i-1 for every i  ==>  H_X(a)=length(X).
```

Thus, conditional on an exact saturated restricted-fiber scheme `X_I`, known
projection-length bounds, and a valid coefficient-to-dual implementation over
the working field, Cummings--Hauenstein Proposition 3.4 and Maican give

```text
z_I = 1[dim D_0^a(I_X)>0]
    = 1[H_X(a)>0]
    = 1[length(X_I)>0].
```

This is enough for the P1553 self-reduction interface. Nonreduced length and
multiplicity may contribute to `H_X(a)`, but no local primary decomposition is
needed for the zero-versus-nonzero decision.

Maican is a primary stabilization control, not a construction supplied by
Cummings--Hauenstein. It assumes the defining ideal of the finite scheme and
does not build or saturate the elliptic restricted-fiber ideal, port the dual
recursion to `F_p`, prove group-source semantics, or bound its cost.

## Conditions still missing from an exact constructor

### Saturation and the empty-fiber case

The input must be the Cox-irrelevant-saturated defining ideal `I_X`, or an
equivalent construction with a proved torsion bound. An empty homogenized
fiber can leave irrelevant torsion in an unsaturated quotient, making
`H_I(a)>0` at low grades even though the multiprojective scheme is empty.

For every canonical restriction the route must prove that irrelevant
saturation yields the unit ideal exactly when the fiber is empty, and charge
the saturation or unit test. Only then does the zero Hilbert component give a
sound empty-fiber bit. Maican's finite-scheme theorem cannot be applied to an
arbitrary unsaturated presentation as though this step were automatic.

### Projection bounds and exact relation semantics

For five square-free restricted deck polynomials of cardinalities `b_i<=B`,
the deck-coordinate projection lengths satisfy `s_i<=b_i`, so `a_i=B-1` is a
safe uniform deck-coordinate bound for a nonempty finite scheme. Any
recursive-S3 auxiliary projective blocks require their own proved projection
bounds, or a charged elimination to the five deck blocks.

The saturated scheme must satisfy the exact biconditional

```text
length(X_(R,I_1,...,I_5))>0
  iff a valid labelled group source exists in I_1 x ... x I_5.
```

Geometric points over an algebraic closure, projective points at infinity,
extension-only auxiliary points, sign collisions, repeated components, and
exceptional recursive-S3 strata must not create false bits. Final singleton
group verification is required, but it does not repair a predicate whose
earlier restriction branches admit algebraic false positives.

### Finite-field port

Maican works over a fixed algebraically closed field and its Hilbert statement
can be applied after base change from `F_p`; graded dimensions are preserved by
field extension. Cummings--Hauenstein's factorial-normalized differential
grammar is stated over `C`, however. The route still needs a proved `F_p`
version, for example via a valid bounded-degree or divided-power/Hasse-dual
formulation, including exceptional-characteristic conditions and coefficient
costs. Maican does not supply that port.

## Type distinctions retained

Definition 2.9 and Proposition 2.11 construct `D_y(I)` at a supplied affine
centre `y`; this can verify local multiplicity but is not the source-blind
existence predicate.

Lemma 4.7 constructs a right inverse `Psi_g` for the differential operator
`Phi_g(delta)(f)=delta(gf)`. Theorem 4.8 computes components of the colon ideal
`I:g`. The target relation fiber instead uses

```text
I_R=I_deck+<g_R>,
D_0^a(I_R)=D_0^a(I_deck) intersect D_0^a(<g_R>)
```

by Corollary 4.3. A dyadic restriction may be represented by rebuilding its
deck generators or, with a supplied complementary factor, by a colon; the
source proves no compact restriction data structure or reuse cost. Every one
of the `O(log B)` restricted sum-ideal queries must be constructed and charged.

## Natural five-`P^1` representation control

Use the natural Cox grading

```text
R_col=k[X_1,Z_1,...,X_5,Z_5],
deg X_i=deg Z_i=e_i in Z^5.
```

For five square-free size-`B` deck equations of degrees `B e_i`, the deck-only
quotient has

```text
H_(R_col/I_deck)(d)=product_(i=1)^5 min(d_i+1,B).
```

At Maican's safe deck grade `d=(B-1,...,B-1)`, both the ambient component and
deck quotient have exact dimension `B^5`. At `d=(B,...,B)`, where all deck
generators enter directly, the ambient component has `(B+1)^5` coordinates and
the quotient still has dimension `B^5`. The literal positive-orthant recursion
through that grade also visits `(B+1)^5` predecessor grade labels.

Therefore the literal dense/natural implementation materializes
`Theta(B^5)` data before deciding the target-specific Hilbert bit. This is a
representation-scoped control. It does not prove that every existence
algorithm must use this grade or representation. Sparse bases, black-box
nullspaces, early stabilization, alternate gradings, or an elliptic-specific
predicate may avoid it; neither Cummings--Hauenstein nor Maican constructs or
rules out such an escape.

## Complete-path costs

Set the ECDLP order `N_grp=B^5`. The frozen gates are

```text
setup + retained state + complete B-row campaign <= B^(9/4+o(1)),
complete fresh relation/source or masked target  <= B^(5/4+o(1)).
```

For the literal dense route, one worst-case existence component costs at least
its `Theta(B^5)` representation traffic. The `O(log B)` charged restrictions
needed to recover a singleton therefore cost `B^(5+o(1))`; `Theta(B)` rows cost
`B^(6+o(1))`; and a fresh scalar-blind `Q+[t]P` source costs
`B^(5+o(1))`. Retaining the natural component also costs `Theta(B^5)` state.
These charges exclude nullspace arithmetic, coefficient bits, saturation,
auxiliary elimination, all-strata handling, and verification, which can add
work. They miss the frozen gates only for the displayed literal
representation, not as a broad lower bound.

After verified five-sparse independent rows exist, sparse factor-log solving
may be granted `B^(2+o(1))` time, `B^(1+o(1))` memory, and independent log
verification. No rank or constant-success-density theorem is supplied. The
same exact restriction predicate and singleton recovery must work for the
fresh masked target; known scalar labels cannot answer its existence queries.

## One verdict

```text
REVISE_AND_DEFER_THE_EXISTENCE_BIT_ROUTE__CUMMINGS_HAUENSTEIN_PLUS_MAICAN_GIVE_A_CONDITIONAL_COEFFICIENT_TO_NONEMPTINESS_PATH__NO_SATURATED_ALL_STRATA_FP_CONSTRUCTOR_OR_SUBRHO_COST_THEOREM_IS_PROVED__PRESERVE_SPARSE_ADAPTIVE_EXCEPTIONS
```

This producer recommendation is not an official status transition. The
earlier direct-atomization requirement is withdrawn. The corrected unresolved
operation is an exact, restriction-stable Hilbert nonvanishing predicate at a
proved safe grade, over `F_p`, with empty fibers and all strata handled and the
full self-reduction, row, rank, factor-log, and masked-descent costs charged.
The literal dense realization fails the cost rectangles, while the scoped
sparse/adaptive exception remains open.

## Exactly one next action

1. Snapshot the revised gate and submit it for independent review.
