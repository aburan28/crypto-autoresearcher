# P1539 R1 independent Abel-Jacobi minor-locator audit

## Record status

- Candidate: `P1539`
- Root hypothesis: `ECDLP-IDEA-012`
- Artifact class: independent theorem-only reconstruction, route screen, and
  terminal candidate disposition
- Decision:
  `INDEPENDENTLY_VERIFIED_EXACT_EVALUATION_INTERFACE__TARGET_BUNDLE_TRANSLATES_TO_FIXED_COLOURED_5SUM__PUBLISHED_INDEXING_AND_WAGNER_CONTROLS_MISS_B2_25_B1_25_RECTANGLE__NONHOMOMORPHIC_LOCATOR_UNSUPPLIED__INCONCLUSIVE`
- Evidence scale: exact divisor, line-bundle, translation, alternant, kSUM
  reduction, and asymptotic accounting; no experiment
- Claim labels: `heuristic`, `model-bound`, `novelty-unverified`
- Contract, verifier, solver, finite-field fixture, relation campaign, or toy
  run: none
- Breakthrough claim: none

The producer's determinant biconditional is correct on the distinct-point
stratum, and its confluent evaluation-map statement is the correct interface
for effective divisors with multiplicity. The independent audit adds a
stronger normalization. If the target subgroup has prime order `N != 5`, put

```text
T = [5^(-1) mod N] R.
```

Then the target bundle `L_R=O_E(4O+R)` is a translate of `L_0=O_E(5O)`, and
every target row is projectively equivalent to a fixed degree-five embedding
row evaluated at `A-T`. Thus P1539 is exactly the coloured elliptic five-sum
query

```text
A_1+...+A_5=R,
```

written as a singular-transversal-minor problem. The thin matrices compile the
predicate but do not create a new target code or discard any point information.

The direct `2+3`, `3+2`, `4+1`, B-target six-list, current kSUM-indexing,
neutral-mask/Wagner, standard AG-code, exterior, and generic solver routes all
miss the required target-independent setup/state `B^2.25` and per-target query
`B^1.25`, or consume the missing witness as input. This is a scoped route
screen, not an unconditional lower bound against every nonlinear field
algorithm. No qualifying locator was found, so P1539 is independently audited
inconclusive rather than negative.

## Frozen evidence and hashes

```text
P1539 producer gate
99227d06594cc50395b368dbef1da602085fc07a9e9a9f39e117682b991c4263

IDEA-012 aggregate complement-divisor hypothesis
aef88ea4ba5053c214325396a6bfebdcbf0d3ce15f8454fb29336cfa3d185363

IDEA-014 elliptic-code locator control
4e09c3f9990a0c6af4e191cad4112fc580391b51b53e61a27755ba5731d43744

IDEA-052 source-labelled wedge control
a0e4d797513a60a8d71ef00a7fb3dbd133acf2f74b1308533562d99d84a1b969

P1515 R1-R11 independent source-router audit
7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e

P1538 bounded-state local-norm audit
2a25ed9ed8eef5518229752a5c439c515255eb810bc01f99e7f0987531b52174

IDEA-057 prime-order composable-bucket theorem
524a59c1728bcbea804ac4be42ace5a965b68a6332e85d941829b89e04fc4225

IDEA-057 Kummer trace/norm correction gate
81a025925063937f4a496e0f6b0618b32525b1c176627449bdbd8eb96dd2f947
```

The IDEA-012 contract remains `review_required` and unapproved. This audit does
not execute, amend, or authorize it.

## 1. Independent reconstruction of the evaluation theorem

Let `E/k` be an elliptic curve with origin `O`, and let

```text
D_A=(A_1)+...+(A_m),
L_R=O_E((m-1)O+R).
```

For `m>0`, genus-one Riemann-Roch gives

```text
h^0(E,L_R)=m,
h^1(E,L_R)=0.
```

The Abel-Jacobi identification `Pic^m(E) -> E` gives

```text
D_A ~ (m-1)O+R  iff  A_1+...+A_m=R.              (1)
```

The kernel of restriction to the length-`m` divisor `D_A` is

```text
ker(H^0(E,L_R) -> H^0(D_A,L_R|D_A))
  = H^0(E,L_R(-D_A)).                             (2)
```

The line bundle in (2) has degree zero. It has a nonzero section exactly when
it is trivial. Both spaces in the restriction map have dimension `m`, so (1)
and (2) imply

```text
A_1+...+A_m=R
iff the length-m evaluation map is singular.      (3)
```

For distinct points, any basis and local trivializations turn (3) into the
ordinary determinant in the producer. For multiplicity `n` at one point, the
length-`n` local restriction is represented by evaluation and derivative rows
of orders `0,...,n-1`; this is the confluent determinant. The construction is
basis-independent up to a nonzero determinant and trivialization-independent
up to nonzero row factors.

This verifies the producer theorem as an exact predicate interface. It does not
verify a locator.

## 2. Target-bundle translation theorem

Assume the target lies in a cyclic prime subgroup `G` of order `N != 5`. Let

```text
L_0 = O_E(5O),
T   = [5^(-1) mod N]R,
tau_c(A)=A+c.
```

For a point divisor, pullback satisfies

```text
tau_c^*(Q)=(Q-c).
```

Therefore

```text
tau_(-T)^*(5O)=5(T),
AJ_5(5(T))=5T=R.                                  (4)
```

The degree-five divisors `5(T)` and `4O+R` have the same Abel-Jacobi class, so

```text
L_R ~= tau_(-T)^* L_0.                            (5)
```

If `s_1,...,s_5` is a fixed basis of `H^0(E,L_0)`, then
`s_j after tau_(-T)` is a basis of the pullback in (5). Up to one public basis
change and nonzero row scalings, the P1539 row obeys

```text
v_R(A) ~= v_0(A-T).                               (6)
```

Consequently

```text
det(v_R(A_1),...,v_R(A_5))=0
iff det(v_0(A_1-T),...,v_0(A_5-T))=0
iff (A_1-T)+...+(A_5-T)=O
iff A_1+...+A_5=R.                                (7)
```

The exceptional subgroup `N=5` is constant size and irrelevant to an
asymptotic cryptographic family. For every target family of interest, division
by five is one public scalar multiplication.

Equation (7) removes a possible false source of novelty. The target-dependent
line bundle does not define an unrelated code at each target. It is the fixed
degree-five embedding evaluated on five uniformly translated decks.

## 3. Fixed elliptic alternant

For a short Weierstrass model in characteristic greater than three, one public
basis of `H^0(E,O_E(5O))` is

```text
1, x, y, x^2, x*y.                                (8)
```

The pole orders at `O` are `0,2,3,4,5`. Thus the normalized distinct-point
minor is the fixed elliptic alternant

```text
det [1, x_i, y_i, x_i^2, x_i*y_i]_(i=1,...,5).   (9)
```

Its vanishing away from collision divisors is exactly the zero-sum condition.
Frobenius-Stickelberger formulae factor the corresponding alternant into
collision terms and a group-sum term, but do not select rows.

The projective row map in (8) is injective: on the affine chart it explicitly
contains `x` and `y`, and `O` is the remaining projective point. Hence a row is
a constant-size encoding of the original signed elliptic point, not a smaller
bucket label. This does not prove a time lower bound, but it shows that the thin
matrix itself has not compressed the search entropy or introduced an auxiliary
target coordinate.

## 4. Repeated-point boundary

There are two exact policies.

1. If the five colour decks are disjoint as signed point sets, every rainbow
   tuple is distinct and (9) is exact. Relations with repeated factor points are
   deliberately excluded; their density and rank effect must be charged.
2. If colours are occurrence-labelled copies of one point set, ordinary rows
   create false dependencies when two colours select the same point. The row of
   derivative order needed at that point depends on the selected multiplicity
   pattern. One fixed `B x 5` ordinary block per colour is therefore not an
   all-strata confluent compiler without additional jet blocks and a public
   tuple-dependent confluence rule.

Under the favorable random simple-rainbow model, rejecting repeated signed
points changes density by only `1+O(1/B)`. That is a model-bound density
statement, not an all-strata theorem. The P1539 locator may use the disjoint
simple policy, but it may not credit ordinary duplicate-row singularities.

## 5. Exact reduction to coloured five-sum

Let the fixed signed decks be `F_1,...,F_5`. By (6)-(7), receiving the five
target matrices is computationally equivalent, up to `O(B)` public group and
field operations, to receiving the shifted decks

```text
F_i-T={A-T:A in F_i}
```

and finding one element from each whose sum is zero. The row labels recover the
source points directly. Thus the P1539 online operation is precisely

```text
COLOURED-5SUM(G;F_1,...,F_5,R).                   (10)
```

An algorithm can still exploit the finite-field encoding of `G`; (10) is not a
claim that it is confined to generic group operations. It does mean that any
claimed gain must name a new coordinate-specific five-sum locator. Rephrasing
the same points as code columns, normal-curve rows, hyperplane sections, or
complement factors does not supply one.

## 6. Direct split and indexing controls

The source-labelled direct routes have the following costs, ignoring
polylogarithmic factors and retaining exact labels.

| Route | Target-independent state | Per-target work | Disposition |
|---|---:|---:|---|
| enumerate five tuples | `B` | `B^5` | fails query |
| store two-sums, scan three-sums | `B^2` | `B^3` | state passes, query fails |
| store three-sums, scan two-sums | `B^3` | `B^2` | both fail the rectangle |
| store four-sums, scan one deck | `B^4` | `B` | query passes, state fails |
| source-labelled wedge `2+3` | `B^2` plus triple stream | `B^3` | same as meet in the middle |

The constant dimensions of `Lambda^2(k^5)` and `Lambda^3(k^5)` do not change
the number of labelled source entries. An ordinary determinant, Pfaffian,
Pluecker pairing, or kernel computation costs constant work only after its
rows or source wedges have been selected.

No interpolation between the table rows is inferred to be impossible. The
table is the exact explicit-route control.

## 7. Current kSUM-indexing control

Dinur and Golovnev's 2026 revision defines `kSUM-Indexing` as preprocessing one
list of length `n` so that a query returns `k-1` input elements summing to the
challenge. P1539 has five source choices, so it corresponds to `k=6` after a
constant-size colour encoding.

Their Theorem 2 gives, for `0<=delta<=1`,

```text
S = soft-O(B^(5.5-delta)),
T = soft-O(B^delta),
preprocessing = soft-O(B^5).                     (11)
```

At `delta=1`, (11) already uses `B^4.5` advice for query `B`; its preprocessing
also exceeds the P1539 setup cap. The simpler four-sum table uses `B^4` state
and `B` query, which still misses the `B^2.25` state gate.

A second reduction groups two pairs. Put

```text
U=F_1+F_2,
V=F_3+F_4,
|U|,|V|=Theta(B^2).
```

For each `A_5`, query whether `U+V` contains `R-A_5`. Applying the 2026
3SUM-indexing theorem at list length `n=B^2` gives

```text
S = soft-O(B^(5-2*delta)),
one 3SUM query = soft-O(B^(2*delta)),
one P1539 target = soft-O(B^(1+2*delta)).         (12)
```

The P1539 query gate forces `delta<=1/8`, and then (12) has
`S>=B^(19/4)=B^4.75`; preprocessing the pair-indexing instance alone costs
`B^4`. This is worse than the permitted state/setup rectangle.

These are upper-bound comparisons. Known unconditional adaptive
3SUM-indexing lower bounds are far too weak to prove P1539 impossible. The
audit therefore records a current-algorithm miss, not a lower bound.

## 8. B-target campaign control

Relation collection needs about `B` independent known-right-hand-side rows in
the favorable model. Freeze a known target deck

```text
Rset={R_1,...,R_B}.
```

The whole campaign is a coloured six-list problem

```text
A_1+...+A_5-R_j=O.                               (13)
```

A balanced `3+3` meet in the middle materializes or streams two lists of size
`B^3`, giving `B^3` campaign work and ordinary `B^3` state. Space-reduction
variants may lower resident memory, but this explicit control retains
`B^3=N^0.6` work. The P1539 favorable campaign cap is

```text
B * B^1.25 = B^2.25 = N^0.45.                   (14)
```

Thus batching all required targets improves the naive `B^4` repeated
per-target split to `B^3`, but remains a factor `B^0.75` above (14).

## 9. Neutral-mask representation screen

Known-scalar masks initially look more promising. Replace a source point `A`
by labelled representations such as

```text
A=(A+U)-U,
```

where `U=[u]P` has known scalar. Mismatched masks do not invalidate a relation:
their net scalar can be moved to the known right-hand side. This can create
many exact labelled representations without knowing `log_P(A)`.

However, the representation count alone is not Wagner's speedup. A Wagner tree
must progressively filter partial sums while guaranteeing that an earlier
cancellation remains meaningful at later merges. If that guarantee depends
only on exact bucket labels, equality of labels is a group congruence. The
IDEA-057 theorem proves that on the prime-order subgroup every such label is
constant or injective. There is no proper exact quotient chain.

The alternatives reproduce already frozen controls:

- a scalar-bit or residue bucket requires the unknown discrete logarithm;
- a point-encoding or `x`-coordinate prefix is nonhomomorphic and does not
  preserve prior cancellations;
- restoring all failed branches needs a correction/source table whose size and
  access are charged;
- Kummer trace/norm of a pair is exactly the normalized `S3` branch polynomial,
  and deck composition is the recursive resultant/norm with pair leaves and
  provenance restored; and
- same-field isogeny kernels preserving the near-`p` prime subgroup have only
  subpolynomial rational multiplicity and duplicate factor-log columns.

Therefore neutral masks do not supply P1539's missing locator. A genuinely new
list-specific nonhomomorphic correction remains outside this scoped screen and
would require a support law, exact source inverse, and complete costs.

## 10. Code, MinRank, and algebraic solver screen

The target evaluation code has dimension five and length `Theta(B)`. A
singular transversal is a coloured weight-five dual word. Standard decoding
starts from a received word or syndrome whose error support generated the
syndrome. P1539 has no such input. Supplying the syndrome, kernel vector,
vanishing section, or support consumes the desired decomposition.

Calling (9) a MinRank instance has the same boundary. Generic MinRank,
Groebner, resultant, FFE, tensor, or code software receives a polynomial system
whose discrete variables or source-product ideal represent the `B^5` row
choices. A backend improvement after this representation is materialized is
not the missing locator.

The complement-section factorization is also exact but equivalent. A linear
multiplication map can verify a supplied decomposable factor; finding its
colour-valid rank-one preimage is (10).

## 11. Complete-cost consequence

At

```text
B=N^(1/5),
```

the producer's exact matrix construction has target cost `B^(1+o(1))`. That
positive remains below the gate. Every complete explicit locator screened here
has at least one of the following observed costs:

```text
per-target query B^2 or B^3,
target-independent state B^3 or B^4,
B-target campaign work B^3,
current kSUM-index preprocessing B^4 or B^5,
or supplied source/syndrome state.
```

The favorable requirement remains

```text
setup,state <= B^2.25,
query <= B^1.25,
complete time,memory exponents <= 0.45.           (15)
```

No route reaches (15), so no density, factor-log rank, sparse solve, or masked
descent credit is available. Even a locator meeting (15) would still need
those independent completion theorems before it could support an ECDLP claim.

## 12. Scope corrections to the producer

The independent audit preserves the producer with three refinements.

1. The target matrices are not merely target-dependent thin matrices; they are
   translated evaluations of one fixed elliptic alternant when `N != 5`.
2. The five-block ordinary-row interface is exact on the disjoint simple
   stratum. All-strata repeated support needs tuple-dependent confluent jets and
   is not supplied by those blocks alone.
3. The current 2026 kSUM-indexing improvement is a required positive control,
   but its useful advice regime is far above the P1539 cap and it does not
   constitute an impossibility theorem.

These refinements strengthen the semantic reduction without broadening any
negative claim.

## 13. Independent route dispositions

| Route | Independent disposition |
|---|---|
| Genus-one evaluation determinant | verified exact predicate |
| Confluent length-five restriction | verified exact interface; fixed-block all-strata compiler absent |
| Target bundle `L_R` | exact translate of `O_E(5O)` via `T=[5^-1]R` |
| Fixed alternant `{1,x,y,x^2,xy}` | exact and point-injective |
| Singular coloured transversal | exactly coloured elliptic 5SUM |
| Complement section | equivalent rank-one/source extraction |
| `2+3`, `3+2`, `4+1` tables | explicit state/query tradeoffs miss rectangle |
| B-target six-list campaign | `B^3` explicit work control |
| 2026 kSUM-indexing | query-cap advice at least `B^4.5` in theorem; preprocessing `B^5` |
| Pair-grouped 3SUM-indexing | query cap implies `B^4.75` advice; preprocessing `B^4` |
| Neutral known-scalar masks | representations valid; exact Wagner quotient absent |
| Kummer trace/norm repair | recursive `S3` resultant/source control |
| Standard AG-code/MinRank solver | consumes syndrome, support, or materialized source system |
| Nonhomomorphic list-specific locator | outside scoped negatives; no operation supplied |

## 14. Independent decision

The independent decision is

```text
INDEPENDENTLY_VERIFIED_EXACT_EVALUATION_INTERFACE__TARGET_BUNDLE_TRANSLATES_TO_FIXED_COLOURED_5SUM__PUBLISHED_INDEXING_AND_WAGNER_CONTROLS_MISS_B2_25_B1_25_RECTANGLE__NONHOMOMORPHIC_LOCATOR_UNSUPPLIED__INCONCLUSIVE
```

P1539 should become terminal `inconclusive`. Its exact predicate compiler and
translation theorem are retained. Its existence claim remains open because the
audit proves no unconditional lower bound against arbitrary nonlinear
finite-field algorithms. It should not be reopened by changing the basis,
normal-curve model, determinant backend, code decoder, kSUM package, neutral
mask distribution, or table split. Reopening requires one explicit
list-specific field operation that locates exact row labels inside (15).

No relation campaign, factor-log solve, blind descent, generic-prime
below-rho algorithm, Shoup-bound improvement, or breakthrough exists.

## Exactly one next action

Rerank outside the evaluation-minor, explicit kSUM-indexing, and exact
generalized-birthday families. Begin with active `ECDLP-IDEA-011`, but admit a
P1540 successor only after an operation-level audit distinguishes its
scalar-orbit period evaluator from the completed P1530-P1533 type-1/type-2
orbit-label controls and freezes one exact construction-or-degree question. Do
not draft or execute a contract, period table, or toy fixture.

## Primary references

- Milne, *Elliptic Curves*, for genus-one divisors, Riemann-Roch, translation,
  and the Picard/group identification: <https://www.jmilne.org/math/Books/EC2.pdf>.
- Frobenius and Stickelberger, *Zur Theorie der elliptischen Functionen*, for
  the elliptic alternant: <https://doi.org/10.1515/crll.1877.83.175>.
- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*,
  arXiv:2512.04258v2, especially Theorems 1-2 and the `soft-O(n^(k-1))`
  preprocessing statement: <https://arxiv.org/abs/2512.04258>.
- Golovnev, Guo, Horel, Park, and Vaikuntanathan, *Data Structures Meet
  Cryptography: 3SUM with Preprocessing*: <https://arxiv.org/abs/1907.08355>.
- Wagner, *A Generalized Birthday Problem*:
  <https://doi.org/10.1007/3-540-45708-9_19>.
- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.

The references support the exact reduction and current positive controls. None
supplies the required nonhomomorphic source locator, complete rank and descent,
or a generic-prime ECDLP improvement.
