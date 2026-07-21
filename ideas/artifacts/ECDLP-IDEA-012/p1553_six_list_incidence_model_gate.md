# P1553 six-list Abel-Jacobi incidence-model gate

## Status and claim boundary

- Record type: independent theorem-only representation and positive-algorithm gate
- Root hypothesis: `ECDLP-IDEA-012`
- Candidate: `P1553`
- Claim: `CLM-P1553-SIX-LIST-ABEL-JACOBI-INCIDENCE`
- Evidence scale: exact genus-one Abel-Jacobi, length-two secant, exterior
  incidence, source-dictionary, explicit-representation, and published-algorithm
  cost derivations; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Contract, solver, fixture, timing run, relation campaign, or toy scalar: none
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_CANDIDATE__ON_THE_CHECKED_DISJOINT_POINT_STRATUM_PAIR_WEDGE_ZERO_INCIDENCE_IS_THE_PULLBACK_OF_THREE_PAIR_ENDPOINT_SUM__ABEL_FIBERS_ARE_P1_AND_ADD_NO_ZERO_PREDICATE_INFORMATION__OVERLAP_COMPONENTS_EXCLUDED_BY_PRELOGGED_DECK_AND_MASK_REBUILD__EXPLICIT_PAIR_TABLES_FIT_B2_BUT_PAIR_PAIR_OR_TRIPLE_CATALOGUES_RESTORE_B4_OR_B3_TRAFFIC__GENERIC_FIRST_CAMPAIGN_HIT_IS_B5_OVER_2_AND_CAMPAIGN_COMPLETE_SUPPORT_IS_B3_IN_THE_RANDOM_OCCUPANCY_CONTROL__PRIME_ORDER_EXACT_COMPOSABLE_BUCKETS_ARE_CONSTANT_OR_INJECTIVE__CURRENT_KSUM_INDEXING_INCIDENCE_AND_DENSE_MULTIPOINT_ALGORITHMS_MISS_B9_OVER_4_B5_OVER_4__STANDARD_RESULTANT_NORM_ROUTES_RETURN_TO_P1513_P1551__SUCCINCT_COMMON_NORM_DETERMINANT_VALUE_CIRCUITS_AND_ARBITRARY_DATA_STRUCTURES_OPEN__INCONCLUSIVE`

P1553 supplies no endpoint-only batch locator. Its exact result is a useful
normal form: after grouping six pairwise distinct coloured points into three
pairs, the vanishing of the three Pluecker bivectors depends only on the three
pair sums on `E`. The length-two secant surface is a `P^1`-bundle over that Abel
endpoint. For two fixed pair divisors, the vanishing hyperplane restricted to
third divisors disjoint from the first four points is exactly the required Abel
fiber restricted to the same open set.

The full hyperplane section also contains overlap components: a third secant
sharing an evaluation row with either fixed pair wedges to zero automatically.
P1553 does not erase that exception. Its campaign freezes pairwise disjoint
actual point decks and rebuilds a target or mask before evaluation if it hits a
factor point. The Abel normal form is exact on that admitted stratum.

Thus the pair-wedge geometry does not define a finer zero-incidence problem than
three-list sum on the pair endpoints. It can still be a computational
representation of that problem: exact nonzero determinant values vary with
choices of rows and a new circuit might exploit those values. The theorem below
does not rule that out.

Within the frozen grammar, every checked route either reduces to current kSUM
or 3SUM-indexing, materializes at least the original `B^3` triple separator (or
a larger pair-pair object), uses a dense coefficient representation, or names
the unconstructed succinct common-norm/source operation. A first generic
collision between the two campaign triple domains costs `B^(5/2)=N^(1/2)`;
this already misses `B^(9/4)=N^0.45`. Recovering the `Theta(B)` random-control
campaign rows by sampled support reaches `B^3`.

This is a theorem about the explicitly admitted representations and operations.
It is not an arithmetic-circuit, Boolean-circuit, cell-probe, incidence, kSUM,
Shoup, or ECDLP lower bound. No below-rho algorithm or Shoup-bound improvement
is established.

## Hash-bound inputs

| Binding | SHA-256 |
|---|---|
| `AGENTS.md` | `3f3f2797ee98eeb07754780dd3e8b30c2f221937a87504b99c4359f35d7cbc6c` |
| `focus/focus_queue_20260717.json` at freeze | `51d4edc7b4ed5dd5e0c9c31d7fb761291e76d0a5ad5bd92b37d99242303748b4` |
| P1539 evaluation-minor gate | `99227d06594cc50395b368dbef1da602085fc07a9e9a9f39e117682b991c4263` |
| P1539 independent audit | `634e5a7d2847e849a2e46178f31500f19109e9a9d88a2bf8c70d1f0afe4d467a` |
| P1506 source-labelled wedge | `a0e4d797513a60a8d71ef00a7fb3dbd133acf2f74b1308533562d99d84a1b969` |
| P1552 mechanism frontier | `7518bbaade077ec3610a150b67f7e6c1411f2e62fb193e31bf053a568162ad86` |
| IDEA-057 composable-bucket theorem | `524a59c1728bcbea804ac4be42ace5a965b68a6332e85d941829b89e04fc4225` |
| IDEA-057 Kummer trace/norm gate | `81a025925063937f4a496e0f6b0618b32525b1c176627449bdbd8eb96dd2f947` |
| P1513 common-norm route screen | `9ec1a5010d7774ee74ff8af7d910bced915cec76213ddd5beca1b7c7aac5c8a8` |
| P1551 finite-domain circuit gate | `5f1bd9c12ca700074c9cd327f6539bc880ec60b27431dc5f34e23b0a12f6c68f` |
| P1515 independent audit | `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e` |
| 302--313 dedup closeout | `5102a9a9887999b508948c02d92be02e615d3c0ce80e89d8330bc215e8ade95b` |
| 302--313 independent red team | `33ba71e4c826a6f1b5781f3fc3a590f66c9226f5e7d35d86a2613257ae3c6942` |

The concurrent cohort closes exact IDs `302`--`313` as twelve scoped
rejections. It leaves 17 active, 27 deferred, and 269 rejected records, nine
active contracts, and 71 retired contracts. Its independent live-tail review
agrees that P1553 is theorem-only and supplies no batch locator.

## 1. Frozen ECDLP and six-list interfaces

Let

```text
E/F_p be an ordinary elliptic curve,
G=<P> subset E(F_p),
|G|=N prime,
N=p^(1+o(1)),
B=N^(1/5).
```

Freeze five public coloured signed factor decks

```text
F_1,...,F_5 subset G,  |F_i|=Theta(B),
```

with exact point dictionaries, disjoint source labels, and a checked policy that
the five decks are pairwise disjoint as sets of actual elliptic points. Factor
deck generation is repeated and charged if the policy fails. This chooses the
disjoint-point branch permitted by the queue; it does not claim that ordinary
pair wedges cover cross-pair repetitions.

For relation collection, freeze a known-log deck

```text
T={R_j=[r_j]P : 1<=j<=Theta(B)}.
```

The signed sixth-point deck `-T` is checked distinct from itself and from every
factor deck; colliding targets are replaced before the campaign. For blind
descent, the public mask `t` is resampled if `-(Q+[t]P)` is a factor point.
These checks use only public group equality. Their random-control failure
probabilities are negligible in the frozen regime, while every rebuild is
charged.

The campaign problem is

```text
A_1+A_2+A_3+A_4+A_5-R_j=O,  A_i in F_i.       (1)
```

There are `B^6/N=Theta(B)` expected coloured rows under the random occupancy
control. One accepted row includes all five signed sources and known right-hand
side `r_j`; endpoint validity alone is insufficient.

For one scalar-blind masked target, put

```text
R=Q+[t]P
```

for public random `t`, and replace `R_j` in (1) by `R`. A successful source row
recovers a scalar candidate after factor logs are known. The target path must use
the same source inverse and exceptional-stratum rules as the known-log path.

The favorable intermediate rectangle is

```text
target-independent setup/state <= B^(9/4+o(1)),
all B known-log relation work    <= B^(9/4+o(1)),
one fresh masked-target query    <= B^(5/4+o(1)).   (2)
```

Pair tables of size `B^2=N^0.4` fit the state bound. A `B^3=N^0.6`
separator does not.

## 2. Exact length-two secant interface

Put

```text
L=O_E(6O),
V=H^0(E,L)^*,
dim(V)=6.
```

For a point `A`, the P1539 evaluation row is a representative

```text
v(A) in V.
```

For an effective length-two divisor or subscheme `D`, let `W_D` be the
two-dimensional image of the dual restriction map

```text
H^0(E,L) -> H^0(D,L|D).
```

Surjectivity follows from `deg(L(-D))=4` and genus-one Riemann-Roch. Choose the
Pluecker representative

```text
x_D in Lambda^2(V).
```

If `D=(A)+(B)` with `A!=B`, then `x_D` is represented by
`v(A) wedge v(B)`. If `D=2(A)`, the second row is the order-one local jet at
`A`. This is the confluent diagonal of `Sym^2(E)`, not two identical ordinary
rows.

Define the degree-two Abel map

```text
pi: Sym^2(E) -> Pic^2(E) ~= E,
pi((A)+(B))=A+B.                                (3)
```

For each `S in E`, the fiber is the complete linear system of the corresponding
degree-two line bundle. Riemann-Roch gives `h^0=2`, hence

```text
pi^(-1)(S) ~= P^1.                              (4)
```

This includes nonreduced divisors on the diagonal as geometry. The discrete
campaign below uses the checked reduced, pairwise-disjoint open stratum.

## 3. Abel-pullback theorem for pair-wedge incidence

Let `D_1,D_2,D_3` be effective length-two subschemes with pairwise disjoint
support, and choose their Pluecker representatives `x_1,x_2,x_3`. Then

```text
x_1 wedge x_2 wedge x_3 = 0 in Lambda^6(V)
  iff pi(D_1)+pi(D_2)+pi(D_3)=O on E.           (5)
```

Proof: the left side is singularity of the length-six restriction map

```text
H^0(E,L) -> H^0(D_1+D_2+D_3,L|D_1+D_2+D_3).
```

Its kernel is `H^0(E,L(-D_1-D_2-D_3))`. This line bundle has degree zero, so it
has a nonzero section exactly when it is trivial. Since `L=O_E(6O)`, triviality
is equivalent to the Abel sum of the length-six divisor being `O`. Additivity of
the Abel map gives (5). The argument uses the confluent restriction map, so it
does not create diagonal false positives.

The disjoint-support hypothesis is essential for this pairwise factorization.
If two `D_i` share a point, their independently constructed restriction-dual
spaces share the order-zero row and the wedge can vanish without the required
length-six Abel sum. A globally confluent determinant would assign higher jets
across all six occurrences, but its `2+2+2` blocks are not three independent
points of the length-two secant surface. P1553 uses the checked deck policy
instead of claiming that stronger identity.

For fixed disjoint `D_1,D_2`, let `S^circ` be the open subset of `Sym^2(E)`
whose support avoids `D_1+D_2`. The four-vector `x_1 wedge x_2` defines a
hyperplane in `P(Lambda^2(V))`, and the exact statement is

```text
H_(D_1,D_2) intersect S^circ
 = pi^(-1)(-pi(D_1)-pi(D_2)) intersect S^circ.  (6)
```

The omitted support-overlap locus contributes automatic wedge-zero components
to the full hyperplane section. It is absent from the admitted discrete decks,
not reclassified as a valid relation.

Consequently the admitted special incidence is ruled by the Abel endpoint. The
extra `P^1` coordinate supplies no additional zero/nonzero predicate
information on that stratum.

Equation (5) does not say that the determinant value is a function only of the
three endpoints under every trivialization. Nonzero row scalings and fiber
coordinates can change that value. A value-sensitive batch circuit is therefore
outside the fiber-invariant theorem unless its reduction is written explicitly.

## 4. Exact discrete pair decks and source replay

Use the campaign pairing

```text
X=F_1+F_2,
Y=F_3+F_4,
Z=F_5-T.                                       (7)
```

Each symbol denotes a source-labelled multiset of pair endpoints and has
`Theta(B^2)` entries before duplicate aggregation. The corresponding Pluecker
decks contain the same source pairs. By (5), campaign relations are exactly

```text
x+y+z=O,  x in X, y in Y, z in Z.              (8)
```

On random independent decks, the expected number of nontrivial pair-sum
collisions inside one coloured pair map is

```text
B^4/N=B^(-1).
```

Thus a checked simple-pair policy succeeds with probability `1-O(B^-1)` in the
random-control model. The exact interface still stores a multimap from each
endpoint to all source pairs; it may reject and rebuild a deck whose total
source dictionary exceeds the state contract. Pair injectivity is a checked
control, not an unconditional theorem for adversarial structured decks.

On simple pair support, one endpoint triple in (8) returns its six source
labels, hence the five factor labels and one known target label. On a collision
fiber, every preimage combination must be enumerated and verified. A bit, count,
or unlabelled endpoint does not satisfy source replay.

For a fresh target `R`, the third deck is

```text
Z_R={A_5-R : A_5 in F_5},  |Z_R|=Theta(B),      (9)
```

while `X` and `Y` remain the two target-independent `B^2` decks. Translation is
injective on `F_5`; the online problem is a preprocessed three-sum query with a
size-`B` unknown query universe, not another free `B^2` table.

## 5. Frozen algebraic-preprocessing and incidence grammar

The P1553 scoped theorem admits only the following operations, with every field
element and source word charged.

1. Complete elliptic arithmetic, the fixed basis of `H^0(E,L)`, confluent jets,
   constant-dimensional linear/exterior transforms, and exact projective
   verification.
2. Explicit source-labelled pair tables and Abel endpoint dictionaries of total
   size at most `B^(9/4+o(1))`.
3. Operations on a pair divisor that are invariant on the Abel fiber, including
   endpoint projection, endpoint equality, and zero/nonzero use of (5).
4. Exact globally composable bucket labels and a constant number of deterministic
   hashes whose complete collision/source lists are explicitly retained.
5. Explicit triple catalogues, pair-pair query decks, incidence matrices,
   source-product quotients, dense resultants/norms, coefficient vectors, value
   tables, and their standard product/remainder/gcd algorithms.
6. Published kSUM, kSUM-indexing, preprocessed-3SUM, finite-field incidence, and
   coefficient-vector multipoint-evaluation algorithms, only in their stated
   input and output models.
7. A static point-versus-hyperplane oracle only if its represented build, state,
   query, reporting, and exact source inverse are supplied and charged.

The grammar does not grant a succinct product-circuit multipoint evaluator, an
implicit common norm, an endpoint coefficient oracle, a nonhomomorphic support
router, a determinant-value selector, a root iterator, a cell-probe structure,
an arbitrary arithmetic or Boolean circuit, or target-fitted advice. These are
scope exceptions, not operations with zero cost.

## 6. Fiber-invariant normal form

For every admitted operation whose pair-divisor input is used only through an
Abel-fiber-invariant value, replace that input by its endpoint under `pi`.
Equation (5) preserves every zero-incidence answer, and the explicit pair
dictionary preserves every source preimage. The resulting computation is an
algorithm for (8) with the same asymptotic field work and no more state.

Therefore the secant surface, Grassmannian coordinates, and `P^1` fiber do not
improve any fiber-invariant route in the grammar. Such a route must beat the
three-list endpoint problem itself. This is a semantic normal form, not a lower
bound for endpoint 3SUM and not a statement about value-sensitive circuits.

The prime-order composable-bucket theorem closes the exact Wagner-style quotient
subclass. If bucket equality is preserved under all additions, its fibers are
cosets of a subgroup of `G`; prime order makes the label constant or injective.
A constant label filters nothing, and an injective label retains all `N=B^5`
states. Nonhomomorphic list-specific filters remain outside that theorem.

## 7. Explicit and generic collision controls

The direct six-list split is

```text
L=F_1+F_2+F_3,
R=-(F_4+F_5-T),
|L|=|R|=Theta(B^3).                             (10)
```

Materializing and matching (10) costs `B^(3+o(1))` work and state in the direct
form. It returns the full random-control campaign support of `Theta(B)` rows.
The pair-pair incidence form is worse if expanded: `X x Y` has `B^4` source
queries before testing against `Z`.

If the two triple maps in (10) behave as independent random maps into a universe
of size `N=B^5`, sampling `s` entries on each side gives expected cross
collisions

```text
s^2/N.
```

One first hit therefore appears at

```text
s=N^(1/2)=B^(5/2),                              (11)
```

using a birthday table or a Pollard-style low-memory collision walk. To expose
`Theta(B)` random-control hits by sampled support requires `s=B^3`, matching
the complete triple deck. These occupancy statements are heuristic controls.

Wagner's generic reduction from cyclic-group kSUM to discrete logarithm gives a
generic `Omega(sqrt(N))` first-hit lower bound in a prime-order group. It explains
why (11) is the correct generic comparison, but it does not apply to a
coordinate-sensitive elliptic algorithm. P1553 is searching precisely for such
a nongeneric operation; none is supplied.

For one fixed fresh target, a `2+3` split has domains `B^2` and `B^3` and only
constant expected intersections. Enumerating the smaller side still requires
the full `B^3` complementary scan in the direct endpoint model. A batch of
masked targets can rebalance the domains but does not enter the required
`B^(5/4)` online cap without a preprocessed source router.

## 8. Current kSUM and preprocessing algorithms

No checked published upper bound enters (2).

| Route | Stated or translated cost | P1553 result |
|---|---|---|
| Direct coloured `3+3` | `B^3` work/state | exact campaign control; outside cap |
| Generic first cross-collision | `B^(5/2)` work | rho boundary; outside cap |
| Goldstein--Lewenstein--Porat 6SUM | `O(B^4)` time and `O(B^(2/3))` space in its number-array model | slower than direct separator; almost-linear integer hashing is not a supplied prime-group quotient |
| Lincoln--Vassilevska Williams--Wang--Williams | for `k=6`, the displayed small-space general bounds remain above `B^3` time | number/order self-reduction; no endpoint/source gain |
| Dinur--Golovnev 3SUM-indexing | `T*S=n^2.5` only in the improved range roughly `n^1.5<S<n^1.75` | with `n=B^2`, available state is `B^2.25=n^1.125`, below the range |
| Kasliwal--Polak--Sharma preprocessed universes | quadratic preprocessing, `n^1.5` query | `n=B^2` gives `B^4` preprocessing |
| Kirkpatrick--Kuszmaul--Mathialagan--Vassilevska Williams | quadratic preprocessing, query `n^(1.5+epsilon)`, subquadratic-space tradeoff | `B^4` preprocessing before source reporting |

The number-array kSUM papers use order or almost-linear modular hashes and do not
by themselves instantiate those operations on the hidden scalar orientation of
the prime-order elliptic subgroup. Even granting their stated algorithms as
controls, their translated exponents miss (2).

For the fresh-target form (9), preprocessing the two `n=B^2` pair universes is
allowed only up to `n^1.125`, and the complete query contains `B=n^0.5`
translated third-list points. None of the cited data structures supplies the
required total `B^1.25=n^0.625` query with exact pair-source output.

These comparisons are upper-bound reconstructions. They are not conditional or
unconditional lower bounds for the P1553 instance.

## 9. Incidence and low-rank controls

For `x,y,z in Lambda^2(V)`, the map

```text
(x,y,z) -> x wedge y wedge z
```

is trilinear. For fixed `z`, its values over explicit `X x Y` form an
`M x M` matrix of rank at most `dim Lambda^2(V)=15`, where `M=B^2`. This low
rank makes an already requested value cheap. It does not report which of the
`M^2` entries are zero, and iterating over `M` third-deck points creates
`M^3=B^6` supplied entries.

Equivalently, each `w=x wedge y in Lambda^4(V)` defines a hyperplane against
the third pair deck. There are `M^2=B^4` such query normals if represented.
By (6), the section on the disjoint-support open part of the secant surface is
one Abel fiber restricted to that open set; reporting its intersection with the
admitted discrete third deck is endpoint membership with source replay.

Rudnev's finite-field point-plane theorem bounds the number of incidences in
projective three-space under its dimension, characteristic, and collinearity
hypotheses. It is not an algorithm for constructing or source-reporting the
implicit `B^4` hyperplanes above, and the ambient Pluecker space is different.
Quoting the incidence count as runtime would conflate a combinatorial bound with
a locator.

Even an ideal constant-time static hyperplane-emptiness oracle would need its
build and source reporter charged. Under random endpoint occupancy, a fixed
query fiber contains `M/N=B^-3` expected third-deck points. Sampling independent
pair-pair queries therefore requires `B^3` queries for one expected hit. This is
a random-control calculation, not a lower bound against correlated or batched
special-family queries.

## 10. Product-polynomial and multipoint controls

For an explicit third Pluecker deck `Z`, define the succinct product circuit

```text
F_Z(w)=product_(z in Z) <w,z>,
w in Lambda^4(V),
|Z|=M=B^2.                                      (12)
```

Then `F_Z(w)=0` exactly when the supplied hyperplane contains at least one
third-deck point. Direct evaluation of (12) costs `M` factors per supplied `w`.
Evaluating all `M^2` pair-pair normals costs `M^3=B^6`.

Bhargava--Ghosh--Guo--Kumar--Umans give deterministic multivariate multipoint
evaluation in

```text
(d^m+K)^(1+o(1))*poly(m,d,log p)
```

for an `m`-variate degree-`<d` polynomial supplied as a coefficient vector and
`K` explicit evaluation points. P1553 instead has a product circuit with `M`
linear leaves and an implicit `M^2` query family. Expanding its dense
coefficient vector, or listing all query points, already misses (2). The cited
theorem does not convert this circuit input to an implicit zero reporter.

Restricting (12) to the secant query variety does not establish a passing
algorithm. Its zero locus factors set-theoretically through the Abel endpoint,
returning to (8); its nonzero values can retain fiber-dependent scaling. A
succinct circuit algorithm exploiting those values without explicit query or
coefficient traffic remains outside the grammar.

The endpoint version makes the same open operation transparent. Build a
degree-`M` function or polynomial vanishing on `Z`, then seek zeros among all
`x+y` with `x in X,y in Y`. Computing

```text
gcd(f_X(U), Res_V(f_Y(V), f_Z(-U-V)))            (13)
```

in additive notation, or its exact elliptic addition-law analogue, would solve
the batch if (13) could be reduced modulo `f_X` from its product circuit and
source-unranked within the cap. Standard specialization, explicit norms,
fiber-product gcds, truncated resultants, and relation-matrix modular
composition restore at least the P1513 traffic or the `B^(5/2)` boundary.

P1513 leaves one precise exception: a bounded reduction of the shared product
circuit to Kedlaya--Umans-compatible degree-`B^2` operations, including common
factors, multiplicity, and exact sources. P1551 independently confirms that
standard coefficient-vector norm, trace, power-projection, and modular-
composition syntax does not supply that reduction. P1553 does not rename this
missing common norm as an algorithm.

## 11. Route dispositions inside the grammar

| Route | Exact result | Disposition |
|---|---|---|
| Six-row determinant | exact relation predicate | P1539 duplicate; no locator |
| Three Pluecker pair decks | exact source-labelled representation | P1506 pair surface; no batching |
| Abel projection | exact factorization of zero incidence | reduces to endpoint three-sum |
| `P^1` secant fibers | exact Abel-fiber section on the disjoint-support open stratum | no extra zero-predicate coordinate there; overlap components excluded |
| Explicit pair tables | `B^2` state with checked source dictionaries | fits setup, useful control |
| Explicit pair-pair normals | `B^4` queries | outside cap |
| Explicit campaign triple separator | `B^3` work/state and all random-control rows | outside cap |
| Generic implicit collision | first hit at `B^(5/2)` | rho boundary, outside cap |
| Exact composable bucket | constant or injective | no Wagner quotient filter |
| Current kSUM/indexing structures | stated upper bounds | translated costs outside cap |
| Incidence-count theorem | bounds a supplied geometric incidence set | no implicit source reporter |
| Low-rank trilinear values | cheap supplied entry evaluation | zero-location problem retained |
| Dense multipoint evaluation | fast from coefficient vector and explicit points | input/query representations outside cap |
| Standard norm/resultant/gcd | exact aggregate relation test | P1513/P1551 traffic; source inverse absent |
| Succinct common norm | would be a real batch operation | not constructed; outside grammar |
| Determinant-value-sensitive circuit | may use nonzero fiber data | unrestricted exception |

No row in the table is an endpoint-only locator meeting (2).

## 12. All-strata, rank, and descent red team

1. **Repeated point identities.** Ordinary repeated rows across pair blocks
   would vanish falsely, and independent length-two jets do not repair that
   case. P1553 checks pairwise disjoint actual point decks, replaces colliding
   known targets, and resamples a colliding blind mask before evaluation. A
   successor that admits repeated identities must instead implement one global
   length-six confluent convention and rederive its batching representation.
2. **Signs and Kummer branches.** Every deck contains actual signed points.
   An x-only pair endpoint has two sign branches and does not replace the signed
   source dictionary.
3. **Pair collisions.** The `B^-1` collision estimate is a random-deck control.
   Exact source multiplicities are retained or the deck is rejected and rebuilt.
4. **Infinity, vertical, and tangent charts.** These use complete projective
   addition and length-two restriction charts. No denominator failure is
   discarded as evidence.
5. **Determinant values.** The theorem concerns their zeros. It does not prove
   that exact nonzero values cannot support a faster circuit.
6. **Incidence richness.** A full `P^1` geometric fiber is not a dense discrete
   source fiber. The discrete pair deck has expected occupancy `B^-3` per Abel
   endpoint.
7. **Relation count.** `B` endpoint incidences are not automatically independent
   rows. Duplicate source rows and factor-column aggregation are removed before
   rank is credited.
8. **Factor logs.** At least `Theta(B)` independent verified rows over the actual
   factor columns are required before sparse linear algebra.
9. **Blind descent.** A known-log target deck does not prove a masked-target
   query. The online source inverse in (9) is a separate mandatory gate.
10. **Generic lower bound.** Wagner/Shoup applies only to generic operations.
    The coordinate-sensitive exceptions above remain logically open.

The strongest attack on the negative result is (13): perhaps the special
elliptic addition kernel permits a succinct translated-product norm modulo the
third divisor in nearly `B^2` bit operations. That would fit setup before source
and query costs. No coefficient-complete reduction, multiplicity splitter,
signed source inverse, or fresh-target recurrence is present in P1553 or its
dependencies. It remains an unproved operation, not a survivor.

## 13. Complete ECDLP cost audit

The best explicit campaign path in the frozen interface has the following
optimistic exponents.

| Stage | Work/state | `N` exponent | Gate |
|---|---:|---:|---|
| Five coloured factor decks | `B` | `0.20` | fits |
| Three source-labelled pair tables | `B^2` | `0.40` | fits setup/state |
| First generic campaign incidence | `B^(5/2)` work | `0.50` | fails `0.45` |
| Complete explicit relation campaign | `B^3` work/state | `0.60` | fails |
| Relation output | `B` rows | `0.20` | output alone fits |
| Optimistic sparse factor-log solve | `B^(2+o(1))` | `0.40` | fits if rank exists |
| Direct fresh-target factorization | at least current `B^3` endpoint control | `0.60` | fails query |
| Final source and scalar verification | linear in emitted rows | at most `0.20` | fits after a locator |

The locator dominates before independent rank, factor logs, and masked descent
can be credited. The current complete path has at best the generic `0.50`
first-hit comparison and `0.60` explicit campaign/target controls, not
`lambda,mu<=0.45`. Pollard rho remains the better complete ECDLP algorithm.

The pair-wedge identity, source dictionary, incidence count, or theorem receipt
does not alter that conclusion.

## 14. Scope exceptions preserved

P1553 does not close:

1. a coefficient-complete succinct common-norm or translated-product operation
   for (13) with exact source jets;
2. an arithmetic circuit that exploits nonzero determinant values across Abel
   fibers rather than only zero incidence;
3. a nonhomomorphic list-specific correction with a proved support-law change;
4. an implicit finite-field incidence reporter that generates neither the
   `B^4` query normals nor a `B^3` source catalogue;
5. an arbitrary cell-probe, word-RAM, arithmetic-circuit, or Boolean-circuit
   data structure;
6. a special factor-deck family with a proved nongeneric additive transform,
   exact unknown-log factor columns, full rank, and blind descent;
7. a transfer, cover, extension-field, or isogeny operation outside the frozen
   same-field endpoint grammar; or
8. an algorithm whose representation changes the ECDLP problem and is analyzed
   outside the generic-group model.

Any such successor must name its coefficients and advice, return exact signed
sources on every admitted stratum, handle relation rank and factor logs, invoke
the identical scalar-blind target path, and prove complete bit-time and
bit-memory exponents. Merely pointing to an exception does not satisfy P1553.

## 15. Independent decision

```text
disjoint-support pair-wedge theorem:          pass
Abel P^1-fiber factorization on that stratum: pass
exact source-labelled pair interface:        pass
current positive-algorithm reconstruction:   pass in stated models
endpoint-only operator inside B^9/4,B^5/4:  absent
complete lambda,mu<=0.45 path:               absent
contract or experiment authorization:        no
scoped disposition:                          terminal inconclusive
breakthrough:                                 none
```

The six-list interface remains mathematically open only through the explicit
scope exceptions above. No operation in the frozen grammar is promoted.

## 16. Exactly one next executable action

Under the existing P1513/`ECDLP-IDEA-121` ownership, write one versioned,
theorem-only derivation of a mechanism-new identity for evaluating (13) from
the succinct product circuits modulo `f_X`. The derivation must either give a
bounded reduction to degree-`B^2` finite-field operations with multiplicity,
signed source unranking, and the separate `B^(5/4)` masked-target recurrence,
or prove a scoped circuit-input obstruction identifying the first unavoidable
`B^(5/2)` or `B^3` represented object. Do not assign P1554 or another candidate
ID unless operation-level deduplication proves that the identity is distinct
from P1513, P1515, and P1551. Do not create a contract, solver, fixture, timing
run, or toy relation campaign.

## Primary references checked

- Wagner, *A generalized birthday problem*:
  <https://doi.org/10.1007/3-540-45708-9_19>.
- Goldstein, Lewenstein, and Porat, *Improved Space-Time Tradeoffs for kSUM*:
  <https://arxiv.org/abs/1807.03718>.
- Lincoln, Vassilevska Williams, Wang, and Williams, *Deterministic Time-Space
  Tradeoffs for k-SUM*: <https://arxiv.org/abs/1605.07285>.
- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*:
  <https://arxiv.org/abs/2512.04258>.
- Kasliwal, Polak, and Sharma, *3SUM in Preprocessed Universes: Faster and
  Simpler*: <https://arxiv.org/abs/2410.16784>.
- Kirkpatrick, Kuszmaul, Mathialagan, and Vassilevska Williams,
  *Preprocessed 3SUM for Unknown Universes with Subquadratic Space*:
  <https://arxiv.org/abs/2602.11363>.
- Bhargava, Ghosh, Guo, Kumar, and Umans, *Fast Multivariate Multipoint
  Evaluation Over All Finite Fields*: <https://arxiv.org/abs/2205.00342>.
- Rudnev, *Point-plane incidences and some applications in positive
  characteristic*: <https://arxiv.org/abs/1806.03534>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.
- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>.

These references establish neighboring generic, kSUM, preprocessing,
multipoint, incidence-count, and summation-polynomial results. None claims the
P1553 endpoint-only batch/source operation or a below-rho generic-prime ECDLP
algorithm.
