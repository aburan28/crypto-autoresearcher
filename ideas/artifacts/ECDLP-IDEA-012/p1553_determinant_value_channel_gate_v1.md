# P1553 determinant-value channel gate V1

## Status and claim boundary

- Record type: unreviewed theorem-only producer and operation audit
- Owner: `P1553` / `ECDLP-IDEA-012`
- Candidate allocation: none; this receipt does not create `P1554`
- Evidence scale: exact determinant-section, weighted-contraction, value-mask,
  and represented-cost derivations; literature comparison; no experiment
- Review state: `review_required`; not independently verified
- Claim labels: `model-bound`, `novelty-unverified`
- Contract, solver, fixture, timing run, relation campaign, or toy scalar: none
- Breakthrough claim: none
- Disposition:
  `UNREVIEWED_SCOPED_PRODUCER__FROBENIUS_STICKELBERGER_VALUE_FACTORIZATION_RECONSTRUCTED__LINEAR_BOX_CONTRACTIONS_ARE_O_B_BUT_NOT_ZERO_REPORTERS__BOUNDED_VALUE_MASKS_REQUIRE_DECK_VALUE_ANNIHILATORS__ELLIPTIC_ROW_MODE_AT_POWER_K_IS_6K_NOT_FULL_SYMMETRIC_POWER__UNIVERSAL_FERMAT_MASK_HAS_B5_ROW_MODE_IF_EXPANDED__SHORT_POWERING_STAYS_POINTWISE_IN_THE_SOURCE_ALGEBRA__STANDARD_PRODUCT_NORM_AND_DISPLACEMENT_ROUTES_MERGE_WITH_P1513_P1551_IDEA041_IDEA071__CURVE_COMPRESSED_DECK_VALUE_ANNIHILATOR_CONTRACTION_AND_SOURCE_UNRANKING_UNSUPPLIED__NO_NEW_CANDIDATE__INCONCLUSIVE`

This receipt narrows P1553's open determinant-value exception.  It does not
claim an unrestricted circuit lower bound.

The six-row determinant has two exact pieces of favorable structure.  First,
the Frobenius--Stickelberger formula factors its section into a group-sum
factor and pairwise diagonal factors.  Second, multilinearity makes every
separately linear box contraction computable from six aggregate rows in
`O(B)` field operations.  Neither operation reports determinant zeros.

The exact zero mask `1-D^(p-1)` does report zeros.  Its short powering syntax,
however, is pointwise on the full six-deck source algebra.  Contracting before
powering introduces cross-tuple terms; powering before contracting retains the
source-index diagonal.  The standard explicit realizations therefore return
to P1551's source-product traffic or P1513's product/norm traffic.

There is one correction to an easy but invalid negative argument.  The
`k`-th row powers on an elliptic normal curve do not require the full
`Sym^k(F_p^6)` payload.  They factor through `H^0(E,L^k)`, of dimension `6k`.
At `k=p-1=Theta(B^5)` even that corrected mode is too large, but a
deck-specific mask of degree only `Theta(B)` would not be excluded by row-mode
size alone.  A successor must actually construct such a compact value
annihilator, contract it without a source quotient, and unrank exact signed
sources.  No audited record supplies those three operations.

## Hash-bound inputs

| Binding | SHA-256 |
|---|---|
| P1553 six-list incidence gate | `ca79b115a952ac610d8ec18a18e3efd9aeef4c283d79f4d0c293012507136f57` |
| P1539 independent alternant audit | `634e5a7d2847e849a2e46178f31500f19109e9a9d88a2bf8c70d1f0afe4d467a` |
| P1551 finite-domain selector-circuit gate | `5f1bd9c12ca700074c9cd327f6539bc880ec60b27431dc5f34e23b0a12f6c68f` |
| P1513 V3 authoritative scope correction | `407e3c7da6345f156f7c6bcaa75749e16b6184735d32be4b6e4aca69427763d5` |
| Rejected IDEA-071 Cauchy-displacement reporter | `27c6880d52b310f03c1d532b3ed68d9e192576b01815d3003501187a64571b5e` |
| Rejected IDEA-041 elliptic Cauchy chord locator | `6df4d8e1fba934810614274ee3a9bc0cb68e69b0b6e65e9d796488d54f82c26f` |
| Rejected IDEA-260 Fay source recursion | `11822dc7edcbb5edbf52da89fd3bd2f5573b2ae45e736724d6007b598fb6b24d` |

All conclusions below are scoped to these bytes.  The P1513 producer and first
audit remain `REVISE`; only its V2 scope correction is used as authoritative.

## 1. Frozen six-row value interface

Let

```text
E/F_p be ordinary, char(F_p)>7,
G=<P> subset E(F_p), |G|=N prime,
B=N^(1/5), N=p^(1+o(1)),
L=O_E(6O), V=H^0(E,L)^*, dim(V)=6.
```

Freeze the same six pairwise-disjoint actual-point decks used by P1553.  Five
are coloured factor decks and the sixth is either a known-log target deck or
the translated one-target deck.  Repeats across colours are excluded by the
charged rebuild policy.  This receipt does not claim an ordinary determinant
for repeated occurrences; a successor admitting them must use one global
length-six confluent convention.

Choose a basis `s_1,...,s_6` of `H^0(E,L)` and one nonzero local frame at every
admitted deck point.  Write

```text
v(A)=(s_1(A),...,s_6(A)),
D(A_1,...,A_6)=det(v(A_1),...,v(A_6)).           (1)
```

A basis change multiplies every value by one public nonzero scalar.  Rescaling
the frame at a deck point multiplies every tuple containing that point by its
unary nonzero scale.  The zero set is invariant; an unnormalized nonzero value
is not.

On the disjoint stratum, P1553 proves

```text
D(A_1,...,A_6)=0 iff A_1+...+A_6=O.              (2)
```

The problem is to determine whether exact nonzero values in (1), rather than
only (2), enable a source-complete batch operation inside
`B^(9/4)` setup/campaign work and `B^(5/4)` fresh-target work.

## 2. Frobenius--Stickelberger value factorization

Over the complex uniformization, take `A_i` to correspond to `u_i`.  The
Frobenius--Stickelberger formula for six rows gives, up to a basis constant,

```text
det(1,wp,wp',wp'',wp''',wp'''')(u_1,...,u_6)
  = c * sigma(u_1+...+u_6)
      * product_(i<j) sigma(u_i-u_j)
      / product_i sigma(u_i)^6.                 (3)
```

Using the Weierstrass equation and a triangular basis change gives the
degree-six elliptic-normal basis

```text
1, x, y, x^2, x*y, x^3.                         (4)
```

Thus (3) is the analytic trivialization of an algebraic line-bundle statement:
the determinant section on `E^6` has the group-sum pullback and the fifteen
pair diagonals as its zero divisor, with the expected frame factors.  The
formula is consistent with (2) after the diagonals are removed.

This statement must not be overread in finite characteristic.  A prime form is
a section with line-bundle and frame data, not a globally supplied scalar
function on `E x E`.  The finite-field algorithm must provide and charge any
charts, extensions, trivializations, pair tables, and denominator handling.
On the frozen finite disjoint decks, supplied pairwise units can be tabulated
in `O(B^2)` words per colour pair, which fits setup.  Their existence does not
give a batch zero reporter.

Equation (3) has two consequences.

1. Nonzero determinant values contain group-sum data multiplied by nonzero
   pairwise gauge factors; they do not define a finer zero set.
2. Fay, Cauchy, and displacement identities that only refactor these supplied
   values are semantic controls unless they also aggregate zeros and return
   sources.

This is the precise merge with IDEA-041, IDEA-071, and IDEA-260.  The
factorization is exact positive algebra, not a new candidate operation.

## 3. Exact `O(B)` linear-contraction identity

For arbitrary public unary weights `w_i:F_i->F_p`, multilinearity gives

```text
sum_(A_i in F_i)
  (product_i w_i(A_i))*D(A_1,...,A_6)

 = det(
     sum_(A in F_1) w_1(A)v(A),
     ...,
     sum_(A in F_6) w_6(A)v(A)
   ).                                            (5)
```

The six aggregate rows cost `O(B)` field operations and constant state beyond
the input decks.  Equivalently, the six-way determinant tensor has the exact
Leibniz decomposition

```text
D=sum_(pi in S_6) sign(pi)*product_i s_(pi(i))(A_i),
```

so its Cartesian tensor rank is at most `6!=720`.  In the three-pair form,
the value is the fixed trilinear volume form on three copies of
`Lambda^2(V)`.

This is a real fast operation, but it is the wrong operation.  A zero tuple
contributes zero to (5), exactly as if it were absent.  Nonzero tuples can
cancel, and a box with no relation can have zero contraction while a box with
a relation can have nonzero contraction.  Per-point frame rescaling changes
the contraction while preserving every relation.  Therefore recursive
conditioning on whether (5) vanishes is not a source-biconditional locator.

The same defect applies to a constant number of linear determinant moments,
derivatives, or Cauchy-displacement summaries.  They are aggregate checksums,
not zero counts or source rows.

## 4. Polynomial value masks and a necessary degree gate

Let `h(T) in F_p[T]`.  An exact zero-count transform on a frozen value set must
satisfy

```text
h(0)=1,
h(z)=0 for every attained nonzero determinant value z.   (6)
```

Fix five generic admitted points.  In the affine frame, the sixth-point map

```text
f(A)=D(A_1,...,A_5,A)
```

is a nonconstant element of `L(6O)`, hence a rational map of degree at most
six.  On any sixth deck of `B` distinct points it takes at least `ceil(B/6)`
distinct values.  If that slice contains its one disjoint complement zero,
then every polynomial satisfying (6) on the slice has

```text
deg(h) >= ceil(B/6)-1.                           (7)
```

Equation (7) is only a necessary degree statement.  It does not prove that a
degree-`Theta(B)` mask is expensive, and it does not show that one polynomial
works for all five-point prefixes.  In fact the union of attained values over
the whole six-deck box can be much larger.  Under the random-value control,
`B^6` values thrown into `p=Theta(B^5)` field elements cover essentially all
of `F_p`, because the average occupancy is `Theta(B)`.  That heuristic makes
the universal mask

```text
chi(D)=1-D^(p-1)                                (8)
```

the relevant control.  This occupancy statement is `heuristic` and
`model-bound`, not a deterministic value-set theorem for structured decks.

For an explicitly supplied nonzero value set `S`, the circular positive
control

```text
h_S(T)=product_(z in S)(1-T/z)                  (9)
```

satisfies (6).  Constructing `S` by enumerating determinant values already
loses.  A mechanism-new successor would have to derive a compact `h_S` from
the public decks without listing the six-fold value image.

## 5. Elliptic row-mode correction

It is incorrect to charge the full dimension
`binomial(k+5,5)` for every `k`-th row moment.  The evaluation rows lie on the
degree-six elliptic normal curve.  The multiplication map sends

```text
Sym^k H^0(E,L) -> H^0(E,L^k),
```

and every pure row power `v(A)^(tensor k)` factors through the dual of the
image.  Riemann--Roch gives

```text
dim H^0(E,L^k)=6k, k>=1.                        (10)
```

For unary weights define the compressed row moment

```text
M_(i,k)=sum_(A in F_i) w_i(A)*ev_A^(k)
         in H^0(E,L^k)^*.                       (11)
```

The power sum

```text
S_k=sum_(A_i in F_i) (product_i w_i(A_i))*D(A_1,...,A_6)^k
```

is a six-way contraction of the six vectors (11) against the restriction of
the `k`-th determinant-power invariant.  Formula (10) is a genuine curve
compression and must be preserved.

It does not yet give a passing algorithm.

- For the universal Fermat mask, `k=p-1=Theta(B^5)`, so even one explicitly
  expanded row mode has `Theta(B^5)` coordinates.
- For a hypothetical deck mask with `k=Theta(B)`, the row modes themselves fit
  setup, but the six-way determinant-power contraction has not been reduced to
  `B^(9/4)` campaign work or `B^(5/4)` target work.
- Expanding `det^k` before the elliptic restriction is indexed by `6 x 6`
  nonnegative exponent tables with every row and column sum equal to `k`.
  Their ambient family has dimension `(6-1)^2=25`.  That standard expansion is
  far too large, but its size is not a lower bound against a new invariant
  contraction.

The exact residual is therefore not "symmetric powers are large."  It is the
absence of a coefficient-complete algorithm that contracts the restricted
determinant-power invariant, applies an exact deck-wide zero mask, and returns
sources inside the cost rectangle.

## 6. Why short powering does not commute with aggregation

The formal circuit for (8) has `O(log p)` multiplication gates.  Let

```text
A_src=Map(F_1 x ... x F_6,F_p)
```

with pointwise multiplication.  The determinant table is one element of this
split algebra.  Repeated squaring computes (8) cheaply only after the element
of `A_src` is represented.  That algebra has dimension `B^6` for the campaign
and `B^5` for one fixed target.

Contracting to a scalar before a square is invalid:

```text
sum_tau D(tau)^2 != (sum_tau D(tau))^2,         (12)
```

because the right side includes cross terms between distinct source tuples.
Retaining only the diagonal in every multiplication requires the source-index
equality projector, an explicit source quotient, or an equivalent
nonpointwise operation.  A balanced exact source split retains or streams a
three-deck object of size `B^3`.  This is P1551's pointwise-versus-aggregation
boundary in determinant coordinates.

The row-mode route in Section 5 and the split-algebra route here are two
representations of the same choice:

```text
expand the high-degree mask before contraction -> degree/mode traffic;
keep the short circuit before contraction       -> source-index traffic.
```

No theorem here excludes a third representation.  Such a representation must
be written explicitly rather than credited as "fast powering plus trace."

## 7. Product, resolvent, and source-jet controls

A determinant-value product

```text
P(T)=product_(tau in F_1 x ... x F_6)(T-D(tau))
```

has `ord_(T=0) P` equal to the number of zero tuples with multiplicity.  It is
the norm of `T-D` from the split source algebra.  Standard product trees,
resultants, norms, traces, logarithmic derivatives, and gcds either represent
the source algebra, form a balanced `B^3` deck, or rename P1513's succinct
common-norm exception.  A zero multiplicity still does not return the signed
sources without marker channels and unranking.

At a simple zero, cofactors or Hasse derivatives of the determinant recover a
kernel section after the six rows are supplied.  They do not locate the six
rows.  Aggregating those derivatives over hidden tuples is P1536/P1513 source-
jet syntax and retains the same constructor boundary.

The dual projective formulation is also exact.  A singular six-row tuple has a
nonzero section in `P(H^0(E,L))` vanishing on all six points.  Enumerating
sections or five-point prefixes restores the P1539 code/incidence and `B^5`
source controls.  No compact dual-section reporter is derived here.

## 8. Semantic deduplication

| Proposed value operation | Existing operation-level control |
|---|---|
| Frobenius--Stickelberger factorization | P1539 and rejected IDEA-041/071 |
| Cauchy or low-displacement evaluation | rejected IDEA-071; faster evaluator without locator |
| Fay/prime-form source recursion | rejected IDEA-260; marked points are consumed, not found |
| Linear determinant contractions | P1553 low-rank supplied-value control; equation (5) sharpens it |
| Fermat singularity mask | P1536/P1551 pointwise equality projector |
| Determinant product or resolvent | P1513 translated product/common norm |
| Explicit symmetric/source quotient | P1551 represented aggregation |
| Cofactor or source derivative after a hit | P1536/P1513 conditional source jets |
| Generic endpoint coefficient/source oracle | IDEA-012/156/199 missing interface |

No operation above warrants a new candidate ID.  The only potentially distinct
operation would be all of the following at once:

```text
compact public construction of a deck-wide determinant-value annihilator;
curve-compressed nonpointwise contraction without source-product state;
exact count or nonempty predicate immune to field cancellation;
exact signed all-strata source unranking;
the same B^(5/4) masked-target recurrence.
```

No identity, representation, or algorithm currently instantiates that block.
Naming it is not a candidate.

## 9. Complete cost boundary

At `B=N^(1/5)` the checked routes have the following optimistic costs.

| Stage or route | Work/state | Result |
|---|---:|---|
| Six input decks and evaluation rows | `B` | fits |
| Optional pairwise local-frame/unit tables | `B^2` | fits setup; no reporter |
| One weighted linear contraction (5) | `B` | exact checksum; not zero detection |
| Universal mask as explicit elliptic row mode | `p=Theta(B^5)` | fails setup/query |
| Universal mask as pointwise source circuit | `B^6` campaign or `B^5` target domain | fails |
| Balanced source-faithful aggregation | at least current `B^3` control | fails `B^(9/4)` and `B^(5/4)` |
| Standard determinant product/norm | source-product or P1513 traffic | fails or remains unconstructed |
| Relation output | `B` rows | fits only after a locator |
| Optimistic sparse factor-log solve | `B^(2+o(1))` | fits only after independent rank |

A degree-`Theta(B)` deck-specific mask is not assigned a cost because neither
its construction nor its determinant-power contraction is supplied.  An
unknown term is not credited as zero.

No relation campaign, rank theorem, factor-log solve, blind descent, scalar
recovery, `lambda,mu<=0.45` path, Shoup-bound improvement, or breakthrough
exists.

## 10. Red-team boundaries

1. **Finite-field scalar factorization.**  The sigma/prime-form identity is a
   line-bundle statement.  A successor must supply finite-field charts and
   frames; this receipt does not grant a free global prime form.
2. **Confluent rows.**  The determinant-value factorization here uses P1553's
   disjoint actual-point policy.  Repeated occurrences need one global
   length-six jet convention.
3. **Gauge dependence.**  Nonzero values and their linear sums depend on row
   frames.  Only an explicitly normalized, invariant output receives credit.
4. **Moment cancellation.**  A field-valued sum or count can vanish despite
   nonempty support.  Exact integer bounds, extension channels, or verified
   recursive source output are required.
5. **Low-degree slice versus global mask.**  Equation (7) is not a global value-
   set theorem and is not a circuit lower bound.
6. **Curve compression.**  The correct row-mode dimension is `6k`; claiming
   the full symmetric-power dimension would be an overstatement.
7. **Short high-degree circuits.**  Repeated squaring can be succinct.  The
   missing cost is source-diagonal aggregation, not formal degree alone.
8. **Special decks.**  A proved small determinant-value image could change the
   mask degree.  It must preserve unknown-log columns, relation rank, and blind
   descent, and it remains open.
9. **Unrestricted algorithms.**  Arithmetic circuits, Boolean circuits,
   word-RAM/cell-probe structures, noncharacter transforms, and new invariant
   contractions outside the frozen representations are not lower-bounded.

## 11. Decision

```text
Frobenius--Stickelberger value factorization:       exact positive control
weighted linear determinant contraction in O(B):   exact positive control
linear contraction as zero/source reporter:        fail
full Sym^k row-mode lower bound:                    rejected as overbroad
correct elliptic row-mode dimension 6k:             exact correction
universal Fermat mask, explicitly expanded:         B^5 row mode; outside cap
universal Fermat mask, short pointwise circuit:      source aggregation absent
standard product/norm/displacement routes:           semantic controls
compact deck-value annihilator contraction:         unsupplied
exact all-strata source unranking:                   unsupplied
new candidate or experiment authorization:          no
breakthrough:                                       none
```

The determinant-value exception is narrower but not closed.  P1553 remains
terminal scoped inconclusive in its independently audited grammar.  This V1
producer is `review_required` and must not alter that disposition until an
independent static audit verifies or corrects it.

## Exactly one next action

Obtain an independent theorem-only static audit of this receipt.  The audit
must reconstruct the finite-field line-bundle scope, equation (5), the degree-
six slice bound, the `6k` row-mode correction, and the noncommutation in (12);
it must then either exhibit a coefficient-complete deck-value annihilator,
restricted determinant-power contraction, and exact signed source unranking
inside `B^(9/4)/B^(5/4)`, or preserve the typed residual without creating
`P1554`, a contract, solver, fixture, timing run, or toy campaign.

## Primary references checked

- Frobenius and Stickelberger, *Zur Theorie der elliptischen Functionen*,
  original DOI: <https://doi.org/10.1515/crll.1877.83.175>; 2026 English
  translation: <https://arxiv.org/abs/2603.27466>.
- Onishi, *Determinant Expressions for Hyperelliptic Functions*,
  <https://arxiv.org/abs/math/0105189>.
- Krishna and Makam, *On the tensor rank of 3 x 3 permanent and determinant*,
  <https://arxiv.org/abs/1801.00496>.
- Semaev, *Summation polynomials and the discrete logarithm problem*,
  <https://eprint.iacr.org/2004/031>.

The first two references supply the determinant factorization and the
`1,x,y,x^2,xy,x^3` elliptic basis.  Tensor-rank work concerns a supplied
determinant tensor, not the high-degree zero mask, source aggregation, or
ECDLP descent.  No checked primary source supplies the compact deck-value
annihilator contraction and source-unranking operation isolated above.
