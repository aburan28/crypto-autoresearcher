# P1539 Abel-Jacobi evaluation-minor gate

## Record status

- Candidate root: `ECDLP-IDEA-012`
- Focus experiment proposed: `P1539`
- Rerank predecessor: terminal-inconclusive `P1538`
- Artifact class: producer theorem-only interface and semantic-rerank receipt
- Decision:
  `UNREVIEWED_EXACT_INTERFACE__COLOURED_DECOMPOSITION_IFF_SINGULAR_EVALUATION_MINOR__COMPLEMENT_FACTORIZATION_EQUIVALENT__SUB_B1_25_ZERO_MINOR_LOCATOR_UNSUPPLIED`
- Evidence scale: exact genus-one line-bundle, evaluation-code, source-interface,
  and cost derivation; no experiment
- Claim labels: `heuristic`, `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract, verifier, solver, finite-field fixture, relation campaign, or toy run: none

The surviving IDEA-012 operation can be made exact without a quotient algebra. For a
target point `R`, put

```text
L_R = O_E((m-1)O + R).
```

Riemann-Roch gives `dim H^0(E,L_R)=m`. After choosing a public basis, evaluate its
sections at every factor-base point. An `m`-tuple of distinct points sums to `R` if
and only if the corresponding `m x m` evaluation minor is singular. Repeated points
use confluent evaluation jets. For five public colour decks this produces five
`B x 5` target-dependent row blocks, and an exact coloured decomposition is a
singular transversal minor containing one row from each block.

This is a useful representation change: one target predicate is compiled into
`Theta(B)` field elements instead of a `B^5` quotient or tuple table. It is not yet
an algorithm. Ordinary rank computation sees only the rank of the complete stacked
matrix, not which transversal minor vanishes. Exterior source labels restore pair,
triple, or full tuple state; standard AG-code decoding starts from a syndrome or
received word, whereas this problem asks for an unknown minimum-support dual word in
a target-dependent code. The complement-section factorization proposed by IDEA-012
is exactly equivalent to this zero-minor search.

At `m=5` and `B=N^(1/5)`, a locator with target-dependent cost at most `B^1.25`
would fit the favorable relation-collection rectangle: `B` constant-density rows
would cost at most `B^2.25=N^0.45` before rank defects and factor-log completion.
No such locator is supplied here. P1539 should therefore be queued as a theorem-only
audit of one concrete operation, not authorized as an experiment and not described
as a breakthrough.

## Frozen inputs and hashes

```text
IDEA-012 aggregate complement-divisor compression hypothesis
aef88ea4ba5053c214325396a6bfebdcbf0d3ce15f8454fb29336cfa3d185363

IDEA-014 elliptic-code error-locator descent control
4e09c3f9990a0c6af4e191cad4112fc580391b51b53e61a27755ba5731d43744

IDEA-052 elliptic wedge-witness hypothesis
7f16d0c18548de91e2ec6ad2f909d36bbea2012854bceee0a85c0957be29669e

IDEA-052 source-labelled wedge derivation
a0e4d797513a60a8d71ef00a7fb3dbd133acf2f74b1308533562d99d84a1b969

P1515 R1-R11 independent source-router audit
7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e

P1538 bounded-state local-norm closure audit
2a25ed9ed8eef5518229752a5c439c515255eb810bc01f99e7f0987531b52174
```

The IDEA-012 execution contract remains `review_required` and unapproved. It is not
run or amended by this receipt. Its focal four-source toy arm is not promoted into
the current five-source asymptotic gate.

## 1. Frozen elliptic divisor convention

Let `k=F_p`, let `E/k` be an ordinary elliptic curve with origin `O`, and let
`G=<P>` have prime order `N=p^(1+o(1))`. For a degree-`m` divisor

```text
D = (P_1)+...+(P_m)
```

define the Abel-Jacobi coordinate

```text
AJ_m(D) = P_1+...+P_m in E.
```

The standard isomorphism `Pic^m(E) -> E` sends the line-bundle class of `D` to
`AJ_m(D)`. Equivalently,

```text
D ~ (m-1)(O)+(R)  iff  AJ_m(D)=R.               (1)
```

This statement is geometric and sign-complete: `P_i` denotes the actual signed
elliptic point. An x-only implementation must retain both lifts and verify signs, or
use five signed colour decks from the start.

## 2. Public target line bundle

For a public target `R in G`, define

```text
L_R = O_E((m-1)(O)+(R)).                         (2)
```

It has degree `m`. Since `E` has genus one and `m>0`, Riemann-Roch gives

```text
h^0(E,L_R)=m,
h^1(E,L_R)=0.                                    (3)
```

Choose a deterministic public basis

```text
s_(R,1),...,s_(R,m) of H^0(E,L_R).
```

The basis may change with `R`; every basis-construction and exceptional chart is
charged. For each rational point `A` outside a chosen trivialization pole, form the
evaluation row

```text
v_R(A) = (s_(R,1)(A),...,s_(R,m)(A)) in k^m.     (4)
```

Changing the local trivialization scales a row by a nonzero scalar. Changing the
section basis right-multiplies every row by one invertible matrix. Neither operation
changes which square minors vanish.

## 3. Exact evaluation-minor theorem

Let `A_1,...,A_m` be distinct geometric points and put

```text
D_A = (A_1)+...+(A_m).
```

The following are equivalent:

1. `A_1+...+A_m=R` on `E`;
2. `D_A ~ (m-1)(O)+(R)`;
3. `L_R(-D_A)` is trivial;
4. `H^0(E,L_R(-D_A))` is nonzero;
5. the evaluation map

   ```text
   ev_A : H^0(E,L_R) -> direct_sum_(i=1)^m (L_R)|_(A_i)
   ```

   has nonzero kernel; and
6. in any public basis and local trivializations,

   ```text
   det(v_R(A_1),...,v_R(A_m)) = 0.               (5)
   ```

Proof: (1) and (2) are the genus-one Abel-Jacobi identification. Statements (2)
and (3) are the definition of `L_R`. A degree-zero line bundle on a genus-one curve
has a nonzero global section exactly when it is trivial, giving (3) iff (4).
The kernel of `ev_A` is `H^0(E,L_R(-D_A))`, giving (4) iff (5). Both vector spaces
in the evaluation map have dimension `m`, so noninjectivity is determinant
vanishing, giving (5) iff (6).

The proof is valid over the algebraic closure. For rational points and a rational
line bundle, the determinant and its vanishing are defined over `k`. It is an exact
relation predicate, not a relation finder.

## 4. Repeated points require confluent rows

If `A_i=A_j`, repeating the ordinary evaluation row makes determinant (5) vanish
identically, even when the divisor with multiplicity does not have class `R`. Ordinary
rows therefore create false positives on repeated-source strata.

For

```text
D_A = sum_t n_t(A_t),   sum_t n_t=m,
```

replace the `n_t` repeated rows at `A_t` by the order-`0,...,n_t-1` local jets of
the basis sections. The resulting confluent evaluation map is the restriction to
the length-`m` subscheme `D_A`; its kernel remains

```text
H^0(E,L_R(-D_A)).
```

Thus the confluent determinant has the same biconditional for every multiplicity.
Five disjoint public colour decks avoid equal point identities on the rainbow branch,
but a complete algorithm must still freeze the policy for repeated x-coordinates,
sign pairs, `O`, tangencies, and rejected nonrainbow relations.

## 5. Five-colour matrix interface

Freeze five disjoint public signed decks

```text
F_1,...,F_5 subset G,   |F_i|=Theta(B),
```

and put `m=5`. For each target `R`, construct the five public matrices

```text
V_(R,i) = (v_R(A) : A in F_i) in k^(B x 5).      (6)
```

For one row index `a_i` from each colour, theorem (5) gives

```text
det(V_(R,1)[a_1],...,V_(R,5)[a_5])=0
iff
F_1[a_1]+...+F_5[a_5]=R.                         (7)
```

Consequently the exact P1539 online problem is:

```text
INPUT:  five target-dependent B x 5 evaluation blocks;
OUTPUT: every accepted singular transversal 5 x 5 minor and its five row labels,
        or a certified miss under the frozen simple-fiber policy.             (8)
```

The endpoint-to-predicate compiler in (6) has only `Theta(B)` field elements for
fixed `m`. This is the representation gain that was implicit in IDEA-012. The
`B^5` candidate set has not disappeared; it is represented by the minors of a thin
matrix.

## 6. Exact complement-section equivalence

Let the union factor-base divisor be

```text
F_tot = sum_(A in F_1 union ... union F_5) (A)
```

with canonical section `sigma_F` of `O_E(F_tot)`. If an accepted source divisor
`D<=F_tot` has degree five and class `L_R`, put `C=F_tot-D`. Then

```text
O_E(C) = O_E(F_tot) tensor L_R^(-1)
```

and there are nonzero sections `sigma_D,sigma_C`, unique up to reciprocal scaling,
such that

```text
sigma_F = sigma_D * sigma_C.                     (9)
```

Conversely, any factorization (9) with `div(sigma_D)` effective of degree five has

```text
div(sigma_D)+div(sigma_C)=F_tot,
```

so `D=div(sigma_D)` is a five-point sub-divisor of the factor base. Requiring
`sigma_D in H^0(E,L_R)` is exactly the Abel-Jacobi target condition.

Therefore the aggregate section/complement operation is not a second source of
compression. It is equivalent to finding a singular minor in (6), or equivalently a
rank-one factor of the fixed section (9) in the target line-bundle class. Complement
duality sends `(D,R)` to `(F_tot-D,AJ(F_tot)-R)` and does not select `D`.

For positive degrees, the relevant section dimensions are

```text
h^0(L_R)=5,
h^0(O(F_tot) tensor L_R^(-1))=5B-5,
h^0(O(F_tot))=5B.                                (10)
```

An explicit multiplication map has linear size in `B`, but its affine preimage of
`sigma_F` contains many tensors. The required point is a decomposable tensor whose
five-zero divisor is colour-valid. A linear solve or aggregate count does not perform
that rank-one/source extraction.

## 7. Elliptic normal-curve and determinant control

For fixed `R`, the row map in (4) is the elliptic normal-curve embedding associated
with the dual line bundle, up to the usual projective identifications. Equation (7)
is the finite-field algebraic form of the hyperplane-section group law: five points
on the degree-five elliptic normal curve lie on one hyperplane exactly when their sum
has the prescribed class.

Frobenius-Stickelberger determinant formulae are an exact positive control for this
factorization. They explain why the determinant has a group-sum zero factor together
with collision factors. They do not locate a zero minor among five sparse public row
sets. Evaluating a determinant after its five rows are supplied is constant work and
receives no source-router credit.

## 8. Evaluation-code interpretation and its limit

Evaluating `H^0(E,L_R)` on the union factor base gives a target-dependent elliptic
evaluation code of length `Theta(B)` and dimension five. A five-row dependency is a
weight-five word in the dual code; colour validity restricts it to one coordinate from
each block.

This is adjacent to rejected IDEA-014 but not identical to its assumed decoder input.
Standard error-locator decoding begins with a received word or syndrome generated from
an error pattern. P1539 receives no error word: it must find an unknown minimum-support
dual word in a code whose line-bundle class changes with `R`. Supplying the syndrome,
locator, or support is the decomposition oracle.

A qualifying code algorithm must therefore be a direct low-weight dual-word locator
for the structured target code, not a decoder replay on planted errors.

## 9. Exterior, Pfaffian, and split controls

For arbitrary row vectors in `k^5`, a `2+3` split writes the determinant as the
perfect wedge pairing

```text
Lambda^2(k^5) x Lambda^3(k^5) -> Lambda^5(k^5).  (11)
```

The value spaces have constant dimensions, but the source-labelled pair and triple
catalogues have sizes `Theta(B^2)` and `Theta(B^3)`. IDEA-052 proves the corresponding
source-label principle in the four-source case: exact wedge coefficients are the pair
surface, and antisymmetry loses repeats without confluent or coloured repair.

Precomputing `B^2` target-dependent pair wedges is permitted by the P1539 setup cap,
but scanning `B^3` triples per query or retaining their labels fails. A Pfaffian,
matchgate, or Pluecker identity on supplied rows only changes the constant-dimensional
predicate. It must still name a locator that avoids the source catalogues.

The ordinary `2+3` elliptic meet-in-the-middle control has the same sizes. Hashing a
pair or triple by a nonhomomorphic coordinate does not preserve complement lookup; a
homomorphic hash on the prime-order group is constant or injective. These are controls,
not a proof against every structured zero-minor data structure.

## 10. Separation from P1538

P1538 closes explicit target-uniform linear transfer states through an exact
rank/density envelope. The P1539 matrix is target-dependent and its proposed locator is
nonlinear in the rows: it asks whether one of many fixed-size minors is zero and returns
the row labels. The explicit transfer theorem does not by itself lower-bound this
operation.

Conversely, writing all minors as one exterior tensor or all target matrices as a
linear transfer restores the P1538 state and source-label controls. P1539 survives only
as a direct nonlinear zero-minor locator on the thin target matrix.

## 11. Favorable complete-cost rectangle

Put

```text
B=N^(1/5),   m=5.
```

Under the favorable random-coloured-support heuristic, the expected number of
five-source tuples for a random target is `Theta(B^5/N)=Theta(1)`. Public colouring
changes this by only a constant and makes a generic rainbow source a simple ordered
tuple.

Let target-independent setup and state be `B^s,B^mu_s`, target-matrix construction be
`B^c`, zero-minor location and exact row output be `B^kappa`, reciprocal simple-fiber
density be `N^delta`, independent-rank loss be `N^r`, factor-log completion be
`N^ell,N^ell_m`, and target ambiguity be `N^u`. The favorable complete exponents obey

```text
lambda = max(s/5,
             1/5 + delta + max(c,kappa)/5 - r,
             ell,
             delta_t + max(c,kappa)/5 + u,
             1/5),

mu     = max(mu_s/5,1/5,ell_m,u).                (12)
```

The explicit matrix compiler plausibly has `c=1+o(1)` after basis formulas and all
field operations are charged. Before an experiment is even considered, a passing
theorem must prove

```text
s,mu_s <= 2.25,
c <= 1.25,
kappa <= 1.25,
lambda,mu <= 0.45.                               (13)
```

With constant density and rank gain, `B` queries at cost `B^1.25` give
`B^2.25=N^0.45`. Sparse factor-log linear algebra costs at least `B^2=N^0.4` under
the favorable model. A `B^2` per-query locator instead gives `B^3=N^0.6` and fails.

No density or rank theorem is inferred from the determinant identity. Every missed
target, duplicate row, nonrainbow tuple, sign branch, repeated point, and failed
verification remains charged.

## 12. Exact theorem gate

A passing P1539 operation must provide all of the following before code or fixtures:

1. deterministic formulas for bases of `H^0(E,L_R)` and all five evaluation blocks,
   including `R=O`, poles, signs, tangencies, and confluent repeated-point rows;
2. a target-independent data structure of setup and memory at most `B^2.25`;
3. an explicit nonlinear algorithm that receives (6), finds every accepted singular
   transversal minor under the frozen simple-fiber policy, and costs at most `B^1.25`;
4. a proof that its retained keys, cells, code syndromes, wedge coordinates, or advice
   do not contain `B^3` triples, a target-indexed source table, or scalar coordinates;
5. exact conversion of row indices to signed elliptic points and independent sum replay;
6. a simple-rainbow density and independent factor-log rank theorem or separately
   frozen evidence plan; and
7. the identical locator on fresh masks `Q+[t]P`, followed by verified scalar recovery
   and complete equations (12)-(13).

An identity for one supplied minor, a global matrix rank, a count of zero minors, a
planted syndrome, a source-labelled wedge tensor, or a line-bundle factorization after
`sigma_D` is supplied fails the gate.

## 13. Route dispositions

| Route | Producer disposition |
|---|---|
| Target line bundle `L_R` and `B x 5` evaluation blocks | exact `Theta(B)` predicate compiler |
| Distinct five-source determinant biconditional | exact |
| Confluent repeated-source determinant | exact interface; implementation unsupplied |
| Aggregate section/complement factorization | exactly equivalent to source factor/minor search |
| Frobenius-Stickelberger determinant | exact predicate factorization, no locator |
| Ordinary stacked-matrix rank | aggregate-only; does not identify a zero minor |
| Standard AG-code error locator | consumes a syndrome/error word; source input missing |
| Source-labelled exterior or Pfaffian tensor | `B^2/B^3` split or full source state |
| Direct `2+3` meet in the middle | `B^2` setup and `B^3` target work in the explicit control |
| Explicit linear transfer of all targets | P1538 rank/density control |
| Nonlinear sub-`B^1.25` structured zero-minor locator | exact surviving operation; no algorithm supplied |

## 14. Producer decision

The active corpus rerank selects IDEA-012 because this exact interface is both outside
the exhausted transfer/integrability family and tied directly to the five-source
summation bottleneck. The producer decision is

```text
UNREVIEWED_EXACT_INTERFACE__COLOURED_DECOMPOSITION_IFF_SINGULAR_EVALUATION_MINOR__COMPLEMENT_FACTORIZATION_EQUIVALENT__SUB_B1_25_ZERO_MINOR_LOCATOR_UNSUPPLIED
```

The positive result is the `Theta(B)` target predicate compiler, not a witness oracle.
The unresolved operation is now precise: locate and source-label a singular coloured
transversal minor of five thin evaluation blocks in `B^1.25` work. IDEA-014, IDEA-052,
P1515, and P1538 provide the planted-syndrome, source-wedge, generic router, and linear
transfer controls.

No relation campaign, factor-log solve, blind descent, generic-order result,
Shoup-bound improvement, or breakthrough exists.

## Exactly one next action

Independently audit this P1539 gate. Reconstruct the genus-one evaluation-minor and
confluent-jet theorems, then either give one explicit elliptic-normal-curve zero-minor
locator inside setup/state `B^2.25` and query `B^1.25` with exact row-source output and
complete costs, or sign a scoped no-candidate receipt after the complement-factor,
AG-code, wedge/Pfaffian, generic kSUM-indexing, and `2+3` controls are charged. Do not
approve or execute the IDEA-012 contract, build a solver, or generate a toy fixture.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.
- Milne, *Elliptic Curves*, divisors, Riemann-Roch, and the genus-one Picard/group
  identification: <https://www.jmilne.org/math/Books/EC2.pdf>.
- Frobenius and Stickelberger, *Zur Theorie der elliptischen Functionen*:
  <https://doi.org/10.1515/crll.1877.83.175>.
- Frobenius and Stickelberger, 2026 English translation and digitization:
  <https://arxiv.org/abs/2603.27466>.
- Pellikaan, *On decoding by error location and dependent sets of error positions*:
  <https://doi.org/10.1016/0012-365X(92)90567-Y>.
- Golovnev, Guo, Horel, Park, and Vaikuntanathan, *Data Structures Meet
  Cryptography: 3SUM with Preprocessing*: <https://arxiv.org/abs/1907.08355>.
- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*, v2:
  <https://arxiv.org/abs/2410.16784>.

These sources support the divisor, determinant, code, and generic preprocessing
controls. None supplies the required sub-`B^1.25` singular-transversal-minor locator,
complete signed source inverse, factor-log rank, blind descent, or generic-prime ECDLP
improvement.
