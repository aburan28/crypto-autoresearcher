# P1553 finite-deck tensor red-team notes R1

## Classification

- Task: `TASK-20260718-P1553-TENSOR-RT-R1`.
- Role: Red Team.
- Evidence: theorem-only reconstruction and adversarial controls; no run.
- Terminal verdict: `REVISE_SCOPED_REDUCTION`.
- Labels: `theorem-only`, `non-run`, `model-bound`,
  `novelty-unverified`.
- Allocation: no P1554, idea record, contract, solver, fixture, experiment,
  status change, or IDEA-133 execution.
- Cryptanalytic result: no relation campaign, rank theorem, factor-log solve,
  blind descent, scalar recovery, Shoup-bound improvement, or ECDLP
  breakthrough.

The producer's pre-mask wedge ranks, post-mask matched-endpoint ranks, and
fixed-target count-to-source reduction reconstruct in their declared checked
stratum. Two interface claims require correction.

1. Exact counts are sufficient but not necessary for one-source replay. A
   target-labelled, subset-stable exact **existence bit**, including the zero
   bit of a dynamically restricted determinant norm, supports the same
   deterministic `O(log B)` bisection. It need not return zero multiplicity,
   a characteristic polynomial, or source idempotents.
2. A sparse TT need not always be a post-support list of relation paths.
   Collision-heavy structured decks can have a public partial-sum automaton
   whose sparse cores are constructed before support is known. An exact
   arithmetic-progression control gives a coefficient-complete reporter
   inside the advertised rectangle, but its endpoint support is only `O(B)`;
   known-log relation density and blind-target density then fail far above
   rho, and no independent factor-log path follows.

No constructor for arbitrary useful prime-field factor decks survives. The
correct residual is therefore weaker and wider than FD-WEC: a target-uniform,
dynamically restricted exact relation-existence data structure, count
reporter, or equivalent specialized norm, together with the complete ECDLP
path. Failure to construct it here is not a lower bound.

The requested sharpened `2+2+1` test reaches the same terminal boundary.
Two source-labelled `B^2` pair-sum divisors fit preprocessing, including all
dyadic node-pair variants up to logarithmic factors. In every standard
realization, however, a target-labelled coefficient or zero-valuation query
either constructs a `B^4` pair-pair convolution or takes a norm over a
`B^3` pair-plus-singleton algebra. This is the standard P1513/P1551 route and
P1516's still-missing target-local router. A typed specialized
characteristic-norm/decision circuit that avoids both objects remains open;
no such circuit is constructed here.

No experiment, timing run, solver, relation query, finite-field fixture, or
IDEA-133 verifier was executed.

## Frozen task and read scope

The current task-card container and canonical card at intake are bound as
follows.

| Input | SHA-256 |
|---|---|
| `coordination/dispatch_queue.json` | `68af0963cb8a23c392476dc8e935bf556cda6dac0d958c74ba7f1913e09af9ce` |
| compact sorted task object plus newline (`jq -S -c`) | `e1451ec65999b0bac194e045f431ad9aaf7113cd59d50c539f9865c9b0afff39` |

Every path in the task-card `read_scope` is hash-bound below.

| Read-scope input | SHA-256 |
|---|---|
| `AGENTS.md` | `4b9810aaa2c96a9e8d7db097d6abfc8cbeb24038df3a09e98f0beb4c23a6d362` |
| `agents/red-team.md` | `7ae9372d518fba2b9868eccf1d99102cde1ac6dae2d7bb593971d264314893f5` |
| `ideas/artifacts/ECDLP-IDEA-012/p1553_determinant_value_channel_audit_r1.md` | `5073e39388792ea9cd8a4f7a1fe19f33f2799e59aa85f898148c9712bb963669` |
| `coordination/tasks/TASK-20260718-P1553-FD-REPORTER-P1/candidate_report.yaml` | `3c518d458895c5422b89202d912b090a309962999b29e6406c48c961135958cc` |
| `coordination/tasks/TASK-20260718-P1553-FD-REPORTER-P1/finite_deck_reporter_spec.md` | `fd12ff17055a108ef31e58b2fb813feb1b8dc8eb2950db127a7a623e69a4d77f` |
| `ideas/artifacts/ECDLP-IDEA-195/p1551_finite_domain_selector_circuit_gate.md` | `5f1bd9c12ca700074c9cd327f6539bc880ec60b27431dc5f34e23b0a12f6c68f` |
| `ideas/artifacts/ECDLP-IDEA-158/p1534_r1_independent_audit.md` | `6a2c96f41552f91ab6d6ddc4801d6e4f958cf5845f6f81676de7f4db89653c53` |
| `ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3_audit_v2.md` | `407e3c7da6345f156f7c6bcaa75749e16b6184735d32be4b6e4aca69427763d5` |
| `ideas/rejected/ECDLP-IDEA-136_folded_wronskian_branch_rank_condenser_hypothesis.md` | `0be49c9f63e1474ba900385d1d4e608aef851f20245f6d0a8315218552870446` |
| `ideas/rejected/ECDLP-IDEA-138_sumcheck_source_self_reduction_hypothesis.md` | `e99daa8a7993266ae86dd9574d122d0b00e9cd897c5673937c6bb8534192af13` |
| `ideas/rejected/ECDLP-IDEA-156_combinatorial_nullstellensatz_source_self_reduction_hypothesis.md` | `228c2d55df137225c92f2a14afca188d09bc8917ced63b6c4d4ac2027accda39` |
| `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md` | `ab36b80667d444a6be41439b89e8c133f2ef3e8fdeef0babb8408cccea84399e` |
| `ledger/FINDING-PF-IC-001.md` | `477c2a821363e041f5e3d6a2e183cd4c351affd08f89a576902b537b846fe487` |
| `focus/current_plan.json` | `65048074479b6010efcc17c13b674bb7758bb1f6cd97ca68c02ae68c770ccc43` |

The producer dependency was complete at handoff. This report does not mutate
the producer receipts or any shared queue, ledger, focus, idea, or contract
state.

The user-requested sharpened comparison added the following supplemental
read-only controls after intake.

| Supplemental input | SHA-256 |
|---|---|
| `ideas/artifacts/ECDLP-IDEA-068/p1513_common_norm_route_screen.md` | `9ec1a5010d7774ee74ff8af7d910bced915cec76213ddd5beca1b7c7aac5c8a8` |
| `ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3.md` | `ce24397ea1686d081dac51b790fcfdf09f17e0a714dc0e8fef399fbb97c2d551` |
| `ideas/artifacts/ECDLP-IDEA-165/pair_sum_quotient_theorem.md` | `18cebc9c209c6ba0d705e43da7f921885e60d3436b201375e306e14f4ae0bdb2` |
| `ideas/deferred/ECDLP-IDEA-165_fixed_rational_pair_sum_quotient_unranking_hypothesis.md` | `bd627e407a49a9f943bed794bd37d876addebe3ee7fc7abbd262c3dc3e9b3bb5` |

## 1. Typed model and scope

Let `G=<P>` have public prime order `N=p^(1+o(1))` and put

```text
B=N^(1/5).
```

Let the six coloured decks consist of labelled actual signed points. On the
checked pairwise-disjoint affine stratum define

```text
v(A)=(1,x(A),y(A),x(A)^2,x(A)y(A),x(A)^3),
D(A_1,...,A_6)=det(v(A_1),...,v(A_6)),
M=1-D^(p-1).
```

The reconstruction assumes that the determinant biconditional is valid on
the whole Cartesian product being queried:

```text
M(A_1,...,A_6)=1 iff A_1+...+A_6=O.                    (1)
```

For a fixed target `R`, freeze the sixth row at `-R`; then (1) reports
`A_1+...+A_5=R`. Cross-colour repeated points, infinity, alternate charts,
tangencies, vertical cases, and nonreduced conventions are not silently
absorbed into (1). A false determinant zero can divert a decision-to-source
replay away from a genuine relation, so a passing global route must either
maintain the checked stratum under every restriction or supply an exact
all-strata predicate.

The count bound below also assumes each colour is a set of distinct actual
points. If one actual point has labelled multiplicity `m_i(A)` in a colour,
the producer's `B^4` argument acquires the maximum missing-colour
multiplicity. This does not hurt an exact existence bit, but it can destroy
the no-wrap count argument.

## 2. Pre-mask determinant ranks

Let `V=F_p^6`. Across a cut `S|S^c`, with `|S|=s`, the determinant pairs

```text
Lambda^s(V) x Lambda^(6-s)(V) -> Lambda^6(V).
```

If `W_S` and `W_(S^c)` are the spans of the coloured decomposable wedges, the
flattening rank is exactly the rank of this pairing restricted to
`W_S x W_(S^c)`. Hence

```text
rank Flat_S(D) <= binomial(6,s).                         (2)
```

If every coloured evaluation deck spans `V`, multilinearity implies that
the coloured decomposable wedges span the full exterior powers. The pairing
is perfect, so the ordered generic TT ranks are exactly

```text
6, 15, 20, 15, 6.                                      (3)
```

The central flattening gives a CP lower bound of 20. The Leibniz expansion
gives a public 720-term CP decomposition. Therefore

```text
20 <= rank_CP(D) <= 720.                                (4)
```

This is a bound, not an exact CP-rank determination.

For fixed nonzero target row `r=v(-R)`, the five-linear form factors through
`V/<r>`, which has dimension five. If every projected colour deck spans the
quotient, the exact ordered TT ranks are

```text
5, 10, 10, 5,                                           (5)
```

and

```text
10 <= rank_CP(D_R) <= 120.                              (6)
```

Equations (2)-(6) reconstruct. They make a supplied-tuple determinant
compact; they do not aggregate its zero set.

## 3. Post-mask flattenings and collision fibres

For any cut `S|S^c`, define the partial endpoint maps

```text
sigma_S(j_S)=sum_(i in S) A_(i,j_i),
sigma_(S^c)(j_(S^c))=sum_(i not in S) A_(i,j_i).
```

Let `H_S` be the set of endpoints attained on the left whose negatives are
attained on the right, and let `r_S=|H_S|`. Under (1), grouping rows and
columns by endpoints gives

```text
Flat_S(M)=sum_(g in H_S)
  1_(sigma_S=g) 1_(sigma_(S^c)=-g)^T.                  (7)
```

The row and column supports of distinct summands are disjoint. Each summand
is a nonzero rank-one all-ones block, so over every characteristic

```text
rank Flat_S(M)=r_S.                                     (8)
```

Endpoint collisions change block sizes, not the rank contribution of a
matched block. If the left and right multiplicities are `a_g,b_-g`, the
number of labelled relations is

```text
Z=sum_(g in H_S) a_g*b_(-g),                            (9)
```

whereas the flattening rank is only the number of matched endpoints. Thus a
collision-heavy fibre may have `Z` much larger than `r_S`.

The TT ranks in one ordering are the corresponding prefix-cut values `r_S`.
Delta tensors for the labelled relation tuples and the flattening lower
bound give

```text
max_S r_S <= rank_CP(M) <= Z.                           (10)
```

If one cut has one distinct matched endpoint for each relation tuple, then
`r_S=Z` and equality holds in (10). Otherwise (10) can be very loose.

For one fixed target, exactly the same proof gives

```text
rank Flat_S(M_R)=r_(R,S),
max_S r_(R,S) <= rank_CP(M_R) <= Z_R.                   (11)
```

With injective colour sets, four points determine at most one fifth point,
so

```text
0 <= Z_R <= B^4 < p                                    (12)
```

eventually. Thus a computed field-valued binary-subdeck count lifts to the
exact integer count. This positive statement reconstructs.

## 4. Exact rank of the Fermat power

On the finite deck,

```text
D^[p-1]=J-M.                                            (13)
```

Rank subadditivity immediately gives the producer's valid bounds

```text
max(0,r_S-1) <= rank Flat_S(D^[p-1]) <= r_S+1,
rank_CP(D^[p-1]) <= Z+1.                                (14)
```

The flattening can be sharpened. Let `a` and `b` be the numbers of attained
left and right endpoint groups, and let `r=r_S`. After compressing each
nonempty endpoint block to its indicator, the core is

```text
K=1_a*1_b^T-P,
```

where `P` is an `r`-edge partial matching. Let `u=a-r` and `v=b-r` be the
numbers of unmatched groups. Then, for the current asymptotic range `r<p`,

```text
rank K = r+1  if u>0 and v>0,
rank K = r    if exactly one of u,v is positive,
rank K = r    if u=v=0 and r>=2,
rank K = 0    if u=v=0 and r=1,
rank K = 1    if r=0.                                  (15)
```

In the fully matched case the core is `J_r-I_r`; in a general
characteristic its rank drops by one when `p` divides `r-1`. Here the cut
ranks are below `p`, so only the displayed `r=1` exception occurs.

Equations (13)-(15) confirm that the post-power collapse is endpoint-support
sensitive. They do not show how to construct the matching.

## 5. Schur powers and recompression

If a flattening of `D` has rank `c_s=binomial(6,s)`, the `q`-th Hadamard
power of a rank decomposition yields

```text
rank Flat_s(D^[q]) <=
  min(B^s,B^(6-s),binomial(q+c_s-1,c_s-1)).              (16)
```

A public CP decomposition with `R_D<=720` similarly gives

```text
rank_CP(D^[q]) <= binomial(q+R_D-1,R_D-1).               (17)
```

For a fixed target, replace `6` by `5` and `R_D` by 120. These are explicit
upper-bound constructors. At `q=p-1` they are much larger than the finite
grid caps.

Repeated squaring applies Hadamard products before recompression. Multiplying
TT or CP descriptions multiplies their ranks in the standard construction.
Contracting first and then squaring is invalid because it introduces
cross-source terms. A standard exact recompression either touches a large
unfolding or needs support-sensitive pivots. This screens those named routes.

It does not prove that all exact recompression circuits must expose the
matching. A nonstandard support-independent recompressor, dynamic tensor
cross with a proved source-free pivot rule, or specialized finite-grid
identity remains open.

## 6. Dense versus sparse TT construction

In the favorable six-deck random-support control, all nontrivial post-mask
TT ranks are `Theta(B)` in expectation. A conventional dense TT then has
internal cores of size

```text
Theta(B*r_(k-1)*r_k)=Theta(B^3).                         (18)
```

A delta-path CP or TT made after enumerating `Z=Theta(B)` relations is small,
but it already names the desired sources. TT-SVD on the explicit tensor and
generic TT-cross with supplied nonzero pivots receive no reporter credit.

That conclusion must be representation-qualified. A sparse transition TT
may encode a public partial-sum law rather than a list of completed relation
paths. Its states are partial endpoints and its core transitions are

```text
(g,A) -> g+A.
```

For arbitrary decks, the central state set can have `Theta(B^3)` endpoints,
which restores the standard merge. For a structured small-sumset deck, the
state set and transition operator can be much smaller and constructible
without locating any relation. Section 10 gives an exact example. Thus

```text
support-delta sparse TT  !=  public transition-automaton sparse TT.
```

The producer's post-support warning is valid for its support-delta and
generic endpoint-block constructors, but not as a statement about every
sparse TT.

## 7. FFE projector, trace, and image

In the split source algebra

```text
A_[5]=tensor_i Map(F_i,F_p) isomorphic to F_p^(B^5),
d_R=(D_R(j))_j,
m_R=1-d_R^(p-1),
```

`m_R` is an idempotent. Multiplication by it has one diagonal 1 for each
checked relation tuple. Therefore

```text
rank_Fp(m_(m_R))=Z_R,
Tr_(A_[5]/F_p)(m_R)=Z_R mod p,
im(m_(m_R))=Map({relation tuples},F_p).                  (19)
```

With (12), the trace lifts to the exact integer count. Restricting the five
coordinate multiplications to the image and splitting primitive idempotents
would recover all labelled coordinates. This exact FFE formulation passes.

Frobenius is coordinatewise identity in the split `F_p` algebra. A short
pointwise circuit for `m_R` does not by itself compute (19), form an image
basis, or split idempotents. Direct quotient, multiplication-matrix, trace,
power-projection, and image constructions retain represented dimension
`B^5` in the named models.

However, image construction is not necessary for one source if a
restriction-stable decision or count interface is available. Consequently
the FFE image is one exact source route, not the minimal semantic gate.

## 8. Characteristic norm correction

The ordinary norm is

```text
Norm(d_R)=product_j D_R(j).                              (20)
```

On the checked stratum, it is zero exactly when a relation exists. The
characteristic norm

```text
Chi_R(T)=Norm(T-d_R)
```

has `T`-adic order `Z_R`. Both statements reconstruct. The producer then
requires a specialized characteristic norm to return zero multiplicity or
count and construct source idempotents. That is stronger than necessary for
one-source replay.

Define a dynamically restricted decision interface

```text
Preprocess(F_1,...,F_5) -> S
Exists(S,R,I_1,...,I_5) -> {false,true},                (21)
```

where `I_i` is a canonical dyadic subset and `Exists` is true exactly when
the restricted Cartesian product contains a valid relation. A restricted
version of (20), followed by an exact zero test, implements (21). Starting
from a true parent, bisect one active colour. Keep the left child if its bit
is true; otherwise keep the right child, which must be true because the
parent is the disjoint union of the two children. Continue through all five
colours. This uses

```text
sum_i ceil(log_2 |F_i|)=O(log B)                        (22)
```

decision calls and ends at one labelled singleton tuple.

No count, zero multiplicity, `Chi_R(T)`, projector image, or primitive
idempotent is needed for (22). Exact signed dictionary replay and elliptic
verification remain mandatory. To prevent a false determinant zero from
choosing a dead branch, (21) must be exact for the admitted all-strata
predicate, not merely for a superset with false positives.

The correction does not make the standard norm route fast. A passing norm
bit must support, with all rebuilds charged,

- target-independent preprocessing within `B^(9/4+o(1))`;
- one fresh target and one dyadic restriction query within
  `B^(5/4+o(1))` time and workspace;
- the same checked or globally confluent predicate at every child; and
- the known-target and blind-target campaign without hidden source advice.

Standard products, resultants, multiplication matrices, and quotient norms
retain the P1513/P1534/P1551 `B^3` to `B^5` controls. A succinct dynamically
restricted norm-decision circuit is a real, explicitly preserved exception.

## 9. Endpoint coefficient and source replay

For binary restrictions or weights define

```text
U_i(w_i)=sum_j w_i(j)[A_(i,j)] in F_p[G].
```

Then

```text
C_R(w_1,...,w_5)=[R] product_i U_i(w_i)                 (23)
```

is the exact restricted tuple count modulo `p`. Under the injective checked
deck assumptions, (12) holds for every restriction, so the field value is
zero exactly when the restricted fibre is empty. The producer's deterministic
count-to-source replay is therefore exact and has the query count in (22).

Arbitrary field weights are not existence safe because relation terms can
cancel. The source replay only needs binary indicator weights. Full-deck-only
counts, campaign-unlabelled aggregates, target-fitted preprocessing, or
restriction rebuilds outside the query cap do not support the reduction.

Equation (23) is a stronger oracle than (21): it returns multiplicity, while
(21) returns one bit. Exact count implies exact existence, but the reverse
need not reconstruct the coefficient. Thus FD-WEC is a sufficient residual,
not an equivalent minimal residual for one-source output.

Enumerating every source remains output sensitive. For one source, either
exact count or exact existence removes source unranking as a separate
exponent only after the subset-stable evaluator itself is constructed.

## 10. Adversarial collision-heavy constructive control

The following exact control shows why sparse-TT and norm exceptions must be
preserved. Choose public points `A_i` and define pairwise-disjoint coloured
decks

```text
F_i={A_i+[j]P: 0<=j<B},                                 (24)
```

with offsets chosen so the checked affine stratum holds. Since `N` is much
larger than `5B`, the short integer index sums do not wrap modulo `N`.

For a restricted deck `I_i subseteq {0,...,B-1}`, put

```text
W_i(X)=sum_(j in I_i) X^j.
```

Construct a public dictionary

```text
k -> A_1+...+A_5+[k]P,  0<=k<=5(B-1).                  (25)
```

For a target `R`, return zero if it is absent from (25). If it corresponds
to `k`, then the exact labelled count is

```text
Z_R(I_1,...,I_5)=[X^k] product_i W_i(X).                (26)
```

The dictionary costs `O(B)` group work and state. Five degree-`O(B)`
polynomials can be multiplied in `B^(1+o(1))` field work and `O(B)` state,
so arbitrary dyadic restrictions, a fresh target lookup, exact count, and
the replay in (22) fit inside the `B^(9/4)/B^(5/4)` reporter rectangle.
Central coefficients can have `Theta(B^4)` labelled sources, making this a
genuinely collision-heavy control.

The same construction is a public sparse TT. A state is the accumulated
integer index `k=O(B)`, and a transition adds the current `j`. Dense cores
would have `Theta(B^3)` entries, but each transition core has only
`O(B^2)` nonzeros and admits fast convolution. It is constructed without
listing any completed relation tuple.

This coefficient-complete reporter does not survive the ECDLP gate.

1. The fivefold endpoint support has only `O(B)` public points. A uniform
   known-log or blind target lands in it with probability `O(B/N)=O(B^-4)`.
   One blind hit therefore needs `Omega(B^4)` target trials in the favorable
   model, already `N^(4/5)` before output or verification.
2. If the offsets have known scalar labels, the factor logs are already
   known and relation collection is vacuous. If they do not, the deck logs
   have the affine form `log(A_i)+j`; known-target relations expose only
   low-dimensional offset combinations, not a proved rank-`B` factor-log
   system.
3. Targets selected from (25) have unknown logs unless the same offset
   combination is already known. They cannot be credited as known-log
   relation targets for free.
4. Enlarging the explicit endpoint support to repair target density restores
   the P1525 rank/density and P1551 endpoint-state costs in this linear
   representation. This does not lower-bound a nonlinear data structure.

The control is therefore a constructive exception and a useful mutation,
not a generic-prime ECDLP algorithm.

## 11. Sharpened two-pair-divisor `2+2+1` test

### 11.1 Exact typed query

For dyadic restrictions `I_i subseteq F_i`, precompute the two
source-labelled pair-sum divisors

```text
D_12(I_1,I_2)=sum_(a_1 in I_1,a_2 in I_2) [a_1+a_2],
D_34(I_3,I_4)=sum_(a_3 in I_3,a_4 in I_4) [a_3+a_4].    (27)
```

Multiplicities retain every labelled source pair. The exact requested output
is

```text
C_R(I_1,...,I_5)
 =[R] D_12(I_1,I_2)*D_34(I_3,I_4)*D_5(I_5)              (28)
```

in the endpoint group algebra. Expanded by endpoint multiplicity,

```text
C_R=sum_(u+v+a=R) m_12(u)*m_34(v)*m_5(a).               (29)
```

Equation (28) is the target-labelled `2+2+1` endpoint coefficient. On the
checked injective decks it is at most `B^4<p`, so its field value is the exact
integer. Its zero/nonzero status alone supports the replay in (22).

Dyadic pair restrictions do not by themselves break the setup cap. Each leaf
pair occurs in `O(log^2 B)` pairs of dyadic tree nodes, because one leaf has
`O(log B)` ancestors in each colour. Storing every node-pair divisor by
source occurrence therefore costs

```text
O(B^2 log^2 B)                                          (30)
```

per colour pair, within `B^(9/4+o(1))`. A query can select the two required
precomputed pair divisors without rescanning `B^2` leaves. The load-bearing
operation is not pair construction; it is (28).

### 11.2 Standard point-basis and index routes

For generic/Sidon decks both pair-divisor supports have `Theta(B^2)` points.
Given a fifth point `a`, exact evaluation of (28) is a 2SUM query between the
two pair lists at target `R-a`. Hashing one pair list and scanning the other
costs `Theta(B^2)` for one `a`; scanning all `B` fifth points costs

```text
Theta(B^3)                                               (31)
```

per target. Precomputing all pair-pair sums constructs a `B^4` occurrence
object. Current 3SUM-indexing controls at list size `n=B^2` do not meet setup
`n^(9/8)` and query `n^(5/8)`, but those upper bounds are not a lower bound
against a special elliptic data structure.

Source labels do not reduce (31). They make a returned endpoint collision
invertible, while the missing target-local collision locator still has to
find which pair occurrences participate.

### 11.3 Standard divisor and characteristic-norm routes

Let `h_12` be a locally trivialized section with zero divisor
`D_12(I_1,I_2)`, retaining occurrence multiplicity. Over the split
pair-plus-singleton algebra

```text
A_(34,5)=Map(D_34(I_3,I_4) x I_5,F_p),
dim A_(34,5)=Theta(B^3),                                 (32)
```

define

```text
d_R(v,a)=h_12(R-v-a).
```

Then

```text
Norm_(A_(34,5)/F_p)(d_R)
 = product_(v in D_34,a in I_5) h_12(R-v-a)             (33)
```

is zero exactly when (28) is nonzero on the checked stratum. Under compatible
local parameters, the target-deformed characteristic product has zero order
equal to (29): every matching `(v,a)` contributes the multiplicity of the
matching `D_12` endpoint. This is an exact zero-multiplicity normal form.

The standard constructor for (33) represents or streams the `B^3` domain in
(32). Swapping the pair divisors gives the same cost. Composing the two pair
divisors first gives the `B^4` object. Source-marker or Hasse-jet channels
preserve multiplicity and pair labels but do not reduce these standard
dimensions. Complete charts and local trivializations remain charged.

### 11.4 Semantic decision

The sharpened route is already occupied at the operation level, but not
closed as an unrestricted data-structure class.

- P1513's translated-product/common-norm receipts encode the same two
  `B^2` pair circuits plus one `B` selector. Their explicit selector norms
  have degree/state `B^3`; the full pair-pair composed sum has degree `B^4`.
  P1513 expressly leaves a specialized product-circuit locator open.
- P1551 charges (32) as the balanced three-colour source object and records
  (28) as the endpoint-coefficient residual. It does not lower-bound a new
  noncharacter extractor or specialized norm circuit.
- P1516 proves that a fixed bounded-degree pair quotient does not supply the
  target router. Its exact statement expressly preserves an arbitrary
  target-local indexed collision router. Precomputing the source-labelled
  `B^2` pair divisors satisfies its allowed pair-state setup; it does not
  answer the target query.

Therefore this is not a mechanism-new P1554 candidate. The standard
point/divisor/quotient/norm realizations are P1513/P1551/P1516 controls. The
following typed exception remains logically open:

```text
BuildPairIndex(F_1,...,F_4)
  -> source-labelled dyadic pair-divisor state S,
  work,state <= B^(9/4+o(1));

Query2P1(S,R,I_1,...,I_5)
  -> exact Exists bit, or exact C_R / zero multiplicity,
  work,workspace <= B^(5/4+o(1)),
```

with no `B^3` complementary side, no `B^4` composed sum, fresh-target support,
and exact all-strata replay. A zero bit is sufficient for one source; exact
zero multiplicity is stronger. No identity, recurrence, circuit, or data
structure implementing `Query2P1` is present in the producer or the three
control chains.

This typed exception is sharper than an unnamed characteristic norm but is
still the existing target-router/endpoint-decision residual. It has no rank,
factor-log, or blind-descent consequence until constructed and costed.

## 12. Favorable generic control

Take six independent pairwise-disjoint public decks that behave as uniform
random `B`-subsets of a prime-order group of size `N=B^5`, and condition on
each evaluation deck spanning the required row space.

- The pre-mask ranks are exactly (3), and the fixed-target ranks are (5).
- For one fixed target, `E[Z_R]=B^5/N=1`. With negligible relevant endpoint
  collisions, each nonzero post-mask cut rank equals `Z_R=O(1)`. A dense TT
  would then have only `O(B)` storage **after its support-sensitive factors
  are known**.
- For the six-deck campaign, `E[Z]=B^6/N=B`. At every ordered cut the number
  of matched endpoint groups is `Theta(B)` in the random-support model, so
  the post-mask TT has `Theta(B)` ranks and conventional dense storage
  `Theta(B^3)`.
- Sparse CP/TT support would be output-sized, but finding its first pivot is
  the original rare five-list target query or six-list endpoint intersection.

This favorable model validates the producer's support-versus-construction
warning. It is heuristic/model-bound and proves neither constant success on
the actual decks nor independent relation rank.

## 13. Operation-level comparison

- `P1551`: the pointwise-versus-aggregation boundary and `B^3/B^5` costs
  remain valid in its frozen grammar. The corrected open interface may be a
  dynamically restricted decision bit, not only a full endpoint coefficient
  and source-moment extractor.
- `P1534`: the fivefold FFE kernel/image is exact but has `B^5` represented
  dimension. Kernel idempotents are sufficient, not necessary, once an exact
  restricted singularity decision is callable.
- `P1513`: ordinary product/norm/common-factor and source-jet realizations
  retain their scoped `B^3` to `B^5` costs. The sharpened two-pair-divisor
  query is its `B^3` selector-norm / `B^4` composed-sum normal form;
  specialized product circuits stay open.
- `P1516`: source-labelled `B^2` pair state fits setup, but a fixed pair
  quotient does not construct the `2+2+1` target router. Its explicitly open
  target-local indexed-router arm is exactly the sharpened exception.
- `IDEA-136`: post-support TT/CP recompression or a condenser on supplied
  factors is a supplied-subspace backend. A direct public transition TT for a
  special deck is a distinct constructive control, but does not pass density.
- `IDEA-138`: a transcript or verifier does not compute (21); honest prover
  work remains charged. Search-to-decision is exact only after the decision
  oracle exists.
- `IDEA-156`: conditional coefficient self-reduction is the same source
  bisection at a stronger output interface. Replacing count by exact existence
  is a scope correction, not a mechanism-new candidate.
- `IDEA-199`: dyadic restrictions and endpoint source replay match its
  coefficient-deck residual. An explicit progression convolution is a
  structured-deck positive control; a generic endpoint coefficient data
  structure remains unsupplied.

## 14. Complete cost consequence

For arbitrary useful decks, no audited operation constructs either (21) or
(23) within

```text
setup/state <= B^(9/4+o(1)),
fresh target/restriction query <= B^(5/4+o(1)).          (34)
```

The standard explicit controls remain:

| Route | Setup/state | Fresh target | Result |
|---|---:|---:|---|
| determinant wedge/CP | `B` | supplied tuple only | predicate, no aggregation |
| dense split projector/image | `B^5` | `B^5` | exact count and sources |
| balanced endpoint/source merge | `B^3` | `B^3` | exact, outside (34) |
| generic post-mask dense TT | `B^3` | support dependent | low rank after matching |
| support-delta sparse CP/TT | output sized | support dependent | sources already supplied |
| standard norm/characteristic norm | `B^3` to `B^5` | `B^3` or worse | scoped failure |
| two `B^2` pair divisors plus standard `2+2+1` norm | `B^(2+o(1))` | `B^3` | pair state fits; target query fails |
| progression sparse TT/convolution | `B^(1+o(1))` | `B^(1+o(1))` on hits | exact reporter; density/rank fail |

Even a passing arbitrary-deck reporter would still need `Theta(B)`
independent known-target relation rows, verified factor logs, and the identical
fresh masked-target interface. Under the optimistic advertised rectangle,
`B` queries cost `B^(9/4+o(1))` and sparse linear algebra can fit `B^(2+o(1))`,
but none of the density, rank, logs, blind descent, ambiguity, output, bit
time, or peak-memory claims is currently proved.

## Explicit exceptions

This report does not classify or exclude:

- a target-uniform, dynamically restricted exact existence data structure;
- a succinct specialized norm-zero circuit whose restrictions and target
  updates fit (34);
- a noncharacter, nonenumerative exact endpoint count or decision structure;
- a support-independent CP/TT constructor or exact recompressor with a proved
  nonzero-pivot and source-query algorithm;
- special deck families with simultaneously proved large target support,
  independent relation rank, factor-log completion, and blind descent;
- reporter families, target specialization, adaptivity, false-positive
  verification, randomized exact methods, and fully charged advice;
- globally confluent determinant/FFE reporters for every collision and
  exceptional stratum; or
- unrestricted arithmetic, Boolean, algebraic, word-RAM, cell-probe, or
  generic-group algorithms.

The `B^3`, `B^5`, and `B^6` costs are receipts for named representations.
They are not tensor-rank, circuit, data-structure, generic-group, Shoup, or
ECDLP lower bounds.

## Terminal verdict

```text
REVISE_SCOPED_REDUCTION__PREMASK_TT_RANKS_6_15_20_15_6_AND_FIXED_TARGET_
5_10_10_5_RECONSTRUCT__CP_BOUNDS_RECONSTRUCT__POSTMASK_FLATTENING_RANK_IS_
MATCHED_ENDPOINT_COUNT_ON_CHECKED_STRATUM__FERMAT_POWER_CORE_SHARPENED__
GENERIC_LOW_RANK_REMAINS_POST_SUPPORT__COLLISION_HEAVY_PROGRESSION_DECK_HAS_
PUBLIC_COEFFICIENT_COMPLETE_SPARSE_TT_CONVOLUTION_BUT_FAILS_TARGET_DENSITY_
AND_FACTOR_LOG_PATH__FFE_PROJECTOR_TRACE_AND_IMAGE_EXACT__COUNT_TO_SOURCE_
REPLAY_EXACT__DYNAMIC_NORM_EXISTENCE_BIT_IS_ALREADY_SUFFICIENT_SO_ZERO_
MULTIPLICITY_AND_IDEMPOTENTS_ARE_NOT_REQUIRED__TWO_SOURCE_LABELLED_B2_PAIR_
DIVISORS_FIT_SETUP_BUT_STANDARD_2_PLUS_2_PLUS_1_POINT_AND_NORM_QUERIES_RESTORE_
B3_OR_B4__ROUTE_DEDUPLICATES_TO_P1513_P1551_P1516_WHILE_TYPED_SPECIALIZED_
QUERY2P1_NORM_DECISION_EXCEPTION_REMAINS_OPEN__ARBITRARY_USEFUL_DECK_EXISTS_
COUNT_OR_NORM_CONSTRUCTOR_TARGET_UPDATE_ALL_STRATA_RANK_LOGS_AND_DESCENT_
UNSUPPLIED__UNRESTRICTED_EXCEPTIONS_PRESERVED__NO_P1554__NO_RUN__NO_
BREAKTHROUGH
```

Exactly one next action: version the P1553 residual from count-only FD-WEC to
the weaker subset-stable `Exists` interface, typed first as `Query2P1` over
two precomputed source-labelled dyadic pair-divisor indexes. Either construct
one target-uniform specialized characteristic-norm/endpoint-decision operation
inside the `B^(9/4)/B^(5/4)` rectangle without a `B^3` complementary side or
`B^4` composed sum, and prove checked/all-strata replay, independent relation
rank, factor logs, and identical blind descent, or preserve the scoped
P1513/P1551/P1516 residual and all circuit/data-structure exceptions. Do not
create P1554, a contract, solver, fixture, experiment, or breakthrough claim.
