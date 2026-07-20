# P1548 torsor deck-orbit router theorem gate

## Status and claim boundary

- Record type: independent theorem-only gate
- Root hypothesis: `ECDLP-IDEA-010`
- Candidate: `P1548`
- Claim: `CLM-P1548-TORSOR-DECK-ORBIT-ROUTER`
- Evidence scale: exact invariant-field, quotient, rational-section,
  orbit-pushforward, bounded rational-branch, and explicit-catalog statements;
  algorithmic-selector scope screen; no experiment
- Contract state: no IDEA-010 contract was drafted, approved, or executed
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__GENERIC_DECK_INVARIANTS_FACTOR_THROUGH_QUOTIENT__TRANSITIVE_FIBER_ORBIT_LABEL_IS_BASE_DATA__NONTRANSITIVE_ORBIT_LABEL_MOVES_BRANCH_TO_INTERMEDIATE_QUOTIENT__CONNECTED_NONTRIVIAL_COVER_HAS_NO_RATIONAL_SECTION__RATIONAL_TARGET_COMPATIBLE_SELECTOR_IS_MISSING_SECTION_OR_TRIVIALIZATION__FIXED_RATIONAL_BRANCH_HAS_O_B_SPARSE_CAPTURE__EXPLICIT_BRANCH_CATALOG_CONSERVES_COVERAGE_AND_WORK__ORBIT_ATOM_PUSHFORWARD_COLLAPSES_TO_BASE_IMAGE_AND_MULTIPLICITY__PUSHFORWARD_CERTIFICATE_DOES_NOT_LOCATE_KNOWN_LOG_RELATION__LANG_TRIVIALITY_OVER_FINITE_FIELD_DOES_NOT_TRIVIALIZE_FUNCTION_FIELD_FAMILY__NONALGEBRAIC_ROOT_ORDERING_AND_COMPACT_GROWING_DEGREE_ROUTER_UNCLASSIFIED__INCONCLUSIVE`

For a generically Galois cover with deck group `Gamma`, every rational
`Gamma`-invariant is a function on the quotient. When the quotient is `E`, a
canonical label for the whole geometric deck orbit contains no branch data
beyond the base point. If the deck group is not transitive on a generic fiber,
the orbit label is instead a point of the intermediate quotient `X/Gamma`; the
branch problem has moved to that cover of `E`, not disappeared.

A rational representative selector would be a rational section of the cover.
An integral connected finite cover of degree greater than one has no such
section: at the generic point it would embed its degree-`d` function field into
the base function field while fixing the base. Equivalently, a section of the
generic torsor is a trivialization. This closes rational branch formulas, not
arbitrary finite-field programs. A program can choose the least encoded root,
for example, without defining a rational map as the target varies. Such a rule
may still spend degree-sized work, and a rule that selects a factor-base-
favorable root may solve the target-local branch problem itself, but no general
arithmetic-circuit lower bound is proved here.

For every fixed rational divisor branch, the P1546 support-incidence argument
applies directly on `X`: an atom base of size `B` captures only `O(B)` source
targets up to the branch degree. Explicitly scanning more branches raises
coverage and branch work together. Orbit atoms also push down to their base
image with orbit/stabilizer multiplicity, so they do not create extra distinct
ECDLP columns. IDEA-010 supplies no compact nonalgebraic or growing-degree
router that escapes these boundaries, and no experiment is authorized.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-010_torsor_deck_orbit_descent_hypothesis.md`:
  `315f2b6e62df24fa300cec72190fc2bc1c3e42f4aea074ef78eac7c461745c56`
- `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r11_independent_audit.md`:
  `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`
- `ideas/artifacts/ECDLP-IDEA-160/p1544_r1_independent_audit.md`:
  `db68ae68e99952656db3c4b179b94770f73972f2429f240c579879ea0502782f`
- `ideas/artifacts/ECDLP-IDEA-002/p1546_projected_smoothness_counting_gate.md`:
  `f64cc45b05cc74364d87eec69f54ecda79100274c0b498103a6492fa61c62702`
- `ideas/artifacts/ECDLP-IDEA-004/p1547_prime_to_p_jet_coordinate_gate.md`:
  `bfdeb57b686ade5c4a3db1c99d0f4fde3f1d193bb7becb7f4703bc7381a5b2b9`

P1515 supplies the exact target-local source-router boundary. P1544 supplies
the torsion-offset orientation control for coprime division fibers. P1546
supplies the fixed rational-branch sparse-capture and explicit-catalog work
theorems. They are not extended here to arbitrary compact nonalgebraic circuits.

## Frozen interface

Let

```text
E/F_p be ordinary,
H=<P> subset E(F_p),
ord(P)=N prime,
N=p^(1+o(1)),
Q=[x]P.
```

Let

```text
pi:X->E
```

be a public finite generically separable cover with `X` integral and normal.
Let `Gamma` be a finite group of deck transformations over `E`, acting
faithfully on the function field `L=F_p(X)`. Put

```text
K=F_p(E),
K subset L,
Z=X/Gamma,
F_p(Z)=L^Gamma.
```

The full Galois case has `[L:K]=|Gamma|` and `Z=E` generically. In the partial
deck case, `Z->E` may retain degree greater than one.

A successful relation branch must take a known source scalar `a`, set
`R=[a]P`, and return a certified upstairs divisor relation supported on one
target-independent atom base. Its pushforward must be a row in one frozen
downstairs logarithm system after zero and duplicate images are removed. Blind
descent must apply the same cover, atom base, selector, and branch rule to
`Q+[t]P` without target-trained advice.

## Deck-invariant quotient theorem

The faithful action of `Gamma` on `L` gives

```text
L/L^Gamma Galois,
[L:L^Gamma]=|Gamma|.
```

Consequently every rational deck-invariant

```text
f in L^Gamma
```

is a rational function on `Z`. If `Z=E`, then

```text
L^Gamma=K.
```

Thus an invariant scalar, tuple of invariants, orbit polynomial, symmetric list
of branch coordinates, norm, trace, discriminant, or canonical serialization
whose coordinates are rational invariant functions factors through the base
point. It can certify the whole fiber orbit but cannot select one point of it.

This statement is about rational algebraic output. A serialized list containing
every branch can of course distinguish the orbit as a finite set, but its
payload contains the fiber. It must charge the number and representation size
of those branches.

## Nontransitive orbit reduction

If `|Gamma|<[L:K]`, a generic `Gamma`-orbit is only part of the fiber. Its
rational invariant label lies on the intermediate quotient `Z`, and

```text
[F_p(Z):K]=[L:K]/|Gamma|
```

in the generic faithful separable case. Selecting a `Gamma`-orbit above
`R in E` is therefore selecting a point in the fiber of `Z->E`. The deck
quotient reduces the branch degree but does not supply the remaining branch.

Iterating subgroup quotients yields a tower of intermediate covers. A complete
chain reaches `E` only after every residual branch is selected or every orbit is
retained. Naming the chain is not a target-local selection algorithm.

## Rational section obstruction

Suppose a rational map

```text
s:E-->X
```

satisfies `pi*s=id` on a dense open. At generic points, rational maps and
function fields reverse direction. The section gives a `K`-algebra map

```text
s^*:L->K
```

whose composition with the inclusion `K->L` is the identity. Since `L` is a
field, `s^*` is injective. It is also `K`-linear, so an injection of the finite
`K`-vector space `L` into the one-dimensional space `K` forces

```text
[L:K]=1.
```

Therefore an integral connected finite cover of degree greater than one has no
rational section. For a generic `Gamma`-torsor, a section is equivalently a
trivialization. A proposed rational target-compatible representative must
therefore expose which assumption makes the cover split, which component it
uses, or which orientation/trivialization it supplies.

This does not say that every finite fiber lacks an `F_p` point. It also does not
say that a computer cannot choose a root by a field-dependent ordering. It says
that such a rule is not a rational section of the nontrivial connected family.

## Lang control is not a family selector

Lang's theorem concerns the surjectivity of the Lang map on a connected
algebraic group over a finite field and, in a standard application, rational
points on torsors over `Spec(F_p)` under connected groups. IDEA-010 instead
needs a compatible selector over the varying generic base point of `E`, hence
over the function field `F_p(E)`, and its deck group is generally finite rather
than connected.

A rational point on one specialized fiber does not produce a rational section
of `X->E`. Applying Lang's theorem to certify fiber nonemptiness, where
applicable, supplies neither branch consistency nor sparse relation density.

## Orbit-atom pushforward collapse

Let `x` be a point of `X` with stabilizer `Gamma_x`. The full orbit divisor is

```text
D_x=sum_(gamma in Gamma/Gamma_x) [gamma x].
```

Every orbit point has the same base image. Therefore

```text
pi_*(D_x)=|Gamma:Gamma_x| [pi(x)]
```

with the corresponding residue-degree factors outside the rational-point
case. Norms of functions obey the same invariant collapse at the divisor
level. Ramification and stabilizers change multiplicities; they do not create
new base support.

Hence `B_up` upstairs orbit atoms yield at most the number of distinct
downstairs images as logarithm columns. Repeated images, conjugate branches,
sign variants, and stabilizer variants are duplicate columns after pushforward.
If the orbit multiplicity is invertible modulo `N`, it is a known coefficient;
if it vanishes modulo `N`, the row is unusable. Neither case creates a new
source logarithm.

## Pushforward verifies but does not locate

Given a certified upstairs relation, pushforward gives a correct downstairs
relation. This is a verifier and representation map. It does not locate a
sparse upstairs witness for a prescribed `R`.

Enumerating atom tuples first has the familiar known-log defect. Their
pushforward sum is a public point of `E`, but its scalar relative to `P` is not
known. Using it as the left side of a base-log row requires solving the source
ECDLP. Starting from a known scalar avoids that defect but restores the
target-local upstairs relation problem.

## Fixed rational-branch sparse capture

Fix one rational branch of the complete upstairs reducer. On a dense open it
defines a nonconstant map

```text
sigma:E-->X^(m)
```

to a bounded symmetric power. If every support component were constant, the
pushforward divisor would be constant and could not represent the varying
source point. Thus the universal support incidence has a component nonconstant
over `X`. Let its degree over `X` be `Delta`.

For an upstairs atom set `A` of size `B_up`, the same incidence count as P1546
gives

```text
#{R in E(F_p): supp(sigma(R)) subset A}
  <= Delta*B_up+O(1).
```

The exceptional term contains poles, ramification, repeated points, branch
boundaries, and special divisors. For fixed cover geometry and a fixed rational
reducer grammar, `Delta=N^o(1)`.

If a degree-`d` cover projects the atoms to `B` distinct E columns, then

```text
B_up<=d*B+O(d).
```

For fixed `d`, one rational branch therefore captures only `O(B)` source
targets up to constants.

## Explicit branch catalogs conserve work

Suppose `T` preregistered rational branches are available. Their union captures
at most

```text
O(T*Delta*d*B)
```

source scalars. Scanning all `T` branches costs `T` evaluations per target.
Even granting that every success is valid and independent, collecting `B`
known-log rows requires

```text
Omega(N/(Delta*d))
```

branch evaluations, and one blind target descent requires

```text
Omega(N/(Delta*d*B)).
```

For fixed bounded `d` and `Delta`, relation collection is linear and target
descent is `N/B`. Sampling branch-target pairs rather than scanning the catalog
gives the same work fraction. A table mapping source points to successful
branches has `Omega(N)` incidences when it covers a constant fraction of the
source line.

These are branch-evaluation and explicit-table bounds. They do not prove a
lower bound for a compact circuit that routes directly to a successful branch.

## Nonalgebraic selector boundary

Finite-field programs can break geometric symmetry by representation choices.
Examples include choosing the least integer encoding of a root, using a fixed
factorization convention, or branching on bit predicates of coordinates. Such
rules need not agree with any rational map over the algebraic closure and are
not closed by the rational-section theorem.

Three cases remain controls unless made explicit:

1. A selector computes all roots and orders them. Its degree-sized output and
   comparison work are charged.
2. A selector chooses an arbitrary easy root independent of the atom base.
   No sparse-capture advantage follows; a distribution theorem and blind
   target evidence are still required.
3. A selector chooses an atom-supported or reducible branch. That predicate is
   the target-local relation router itself and must be specified and costed,
   not assumed from the existence of a successful branch.

No general lower bound against the third case is claimed. A compact arithmetic
or Boolean circuit could in principle distinguish branches without an explicit
table. IDEA-010 gives no such circuit, source inverse, or complete cost.

## Growing-degree boundary

Write

```text
d=N^alpha,
Delta=N^kappa.
```

The favorable one-branch capture envelope becomes

```text
T_rel>=N^(1-alpha-kappa-o(1)),
T_desc>=N^(1-alpha-kappa-beta-o(1)).
```

These expressions are not a complete algorithm and do not prove failure.
Explicit equations, full fibers, orbit lists, or branch catalogs must pay their
degree-sized representation and output. A special cover and selector represented
by compact circuits may avoid materializing all degree-`d` data. It remains
outside scope until the circuits, field representation, applicability density,
branch ambiguity, atom images, source inverse, output, verification, and state
are published.

## Complete cost receipt

Use the frozen P1548 model

```text
lambda=max(c,alpha,kappa_rep,beta+u+b+delta+o,2*beta,
           u+b+delta_t+o,beta+v,v),
mu=max(s,beta,kappa_rep,o).
```

For fixed cover degree and a fixed rational selector, the exact capture theorem
gives relation exponent at least one and target exponent at least `1-beta`.
Explicit branch catalogs cannot lower either after branch evaluations are
charged. Orbit atoms produce at most their distinct projected E columns. A full
branch-incidence table has state exponent one when it covers a constant fraction
of the source line.

No compact nonalgebraic or growing-degree selector remains to receive favorable
parameters. IDEA-010 supplies no construction `c`, compact representation
`kappa_rep`, selector work `u`, branch work `b`, relation and target densities
`delta,delta_t`, output `o`, verification `v`, or state `s` for such an
operation. Missing exponents are not assigned optimistic zeros.

## Independent findings

1. Rational deck invariants factor through the geometric quotient.
2. If the generic deck action is transitive and `X/Gamma=E`, an invariant orbit
   label is base data and contains no branch orientation.
3. If the deck action is not transitive, orbit selection is a branch problem on
   the intermediate quotient `X/Gamma->E`.
4. A connected nontrivial finite cover has no rational section; a section of the
   generic torsor is a trivialization.
5. Lang triviality over a finite base field does not provide a section over the
   function-field family or orient a finite deck group.
6. An orbit atom pushes forward to one base image with known orbit/stabilizer
   multiplicity; duplicate upstairs atoms do not add E-column rank.
7. Pushforward verifies an upstairs relation but does not locate a known-log
   sparse witness for a prescribed source point.
8. Every fixed rational divisor branch captures at most
   `O(Delta*B_up)` sparse-atom targets.
9. Explicit branch catalogs conserve coverage and evaluation work; fixed
   bounded degree gives linear relation collection and `N/B` blind descent.
10. Nonalgebraic finite-field root ordering, compact branch-selection circuits,
    and compact growing-degree routers remain unclassified, but IDEA-010
    supplies none with a source inverse and complete cost.

## Disposition and next action

P1548 is terminal inconclusive within generically transitive deck-invariant
quotients, partial intermediate quotients, rational representative sections,
generic torsor trivializations, orbit atoms, fixed rational divisor branches,
explicit branch catalogs, tuple-first pushforwards, and Lang-triviality claims.
Preserve IDEA-010, P1515, P1544, P1546, P1547, and this receipt. Do not draft or
execute a fiber-enumeration contract.

Exactly one next action: rerank outside invariant quotients, rational sections,
fixed algebraic branches, explicit branch catalogs, and relation-only
pushforwards. Bind one mechanism-distinct P1549 theorem question. Reopening
IDEA-010 requires an explicit compact nonalgebraic or growing-degree selector
circuit, its target-independent branch predicate, source inverse, projected
rank, identical blind target descent, and complete bit costs in the proposal.

No generic-prime ECDLP recovery, relation campaign, factor-log solve, blind
descent, below-rho algorithm, Shoup-bound improvement, or breakthrough is
established.

## Primary references

1. The Stacks Project, *Invariant functions*, especially the quotient condition
   that quotient functions are the invariant functions,
   <https://stacks.math.columbia.edu/tag/04A9>.
2. The Stacks Project, Lemma 9.21.6, a finite faithful group action gives the
   Galois extension `L/L^Gamma` of degree `|Gamma|`,
   <https://stacks.math.columbia.edu/tag/09I3>.
3. The Stacks Project, Lemma 20.4.2, a torsor is trivial exactly when it has a
   section, <https://stacks.math.columbia.edu/tag/02FN>.
4. The Stacks Project, Theorem 33.4.1, dominant rational maps and function
   fields, <https://stacks.math.columbia.edu/tag/0BXM>.
5. S. Lang, *Algebraic Groups Over Finite Fields*,
   <https://wstein.org/papers/bib/Lang-Algebraic_Groups_Over_Finite_Fields.pdf>.
6. V. Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   <https://www.shoup.net/papers/dlbounds1.pdf>.

These sources establish the invariant-quotient, finite-group fixed-field,
torsor-section, rational-map, finite-field algebraic-group, and generic controls.
The fixed-branch sparse-capture and explicit-catalog deductions are imported
only in their independently audited P1546 scope. None supplies the missing
compact nonalgebraic target-compatible deck router or a complete generic-prime
sub-rho ECDLP path.
