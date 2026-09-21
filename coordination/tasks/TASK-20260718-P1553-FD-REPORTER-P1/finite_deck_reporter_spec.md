# P1553 finite-deck determinant reporter specification P1

## Classification and verdict

- Task: `TASK-20260718-P1553-FD-REPORTER-P1`.
- Role: Idea Generator.
- Artifact type: theorem-only finite-domain representation audit.
- Status: `incomplete_scoped_reduction`.
- Labels: `theorem-only`, `non-run`, `model-bound`, `novelty-unverified`.
- Positive operation: none. No coefficient-complete reporter passes every gate.
- Allocation: no P1554, idea record, contract, solver, fixture, experiment, or
  status change is proposed or created.
- Cryptanalytic result: no relation campaign, relation-rank theorem, factor-log
  solve, blind descent, scalar recovery, Shoup-bound improvement, or ECDLP
  breakthrough is claimed.

The exact finite-deck tensor has a strong post-mask compression: its TT ranks
are matched-endpoint counts and its CP rank is at most the number of relation
tuples. That compression is a property of the already-located support. The
known constructors either enumerate a central `B^3` endpoint/source object or
require the matched endpoints or source tuples as pivots. Consequently the
P1553 residual reduces, in the audited interfaces, to one exact weighted
endpoint-coefficient and source-unranking operation. This is a sharper
interface, not a construction and not a lower bound against untested circuits.

No experiment, timing run, solver, relation query, fixture, or IDEA-133
verifier was executed.

## Frozen task and read scope

The task-card container and canonical task object at intake are:

| Input | SHA-256 |
|---|---|
| `coordination/dispatch_queue.json` | `00701a4ebc18938a9ac251cbab906897cf9dc596d975191b6602e139c1d27f53` |
| canonical sorted `TASK-20260718-P1553-FD-REPORTER-P1` object plus newline | `975b2ebd198b97da61e5faf3f77526a91dd62e9c72b30d79dd7c0cf5bf1febb5` |

Every task-card `read_scope` input is bound below.

| Read-scope input | SHA-256 |
|---|---|
| `AGENTS.md` | `4b9810aaa2c96a9e8d7db097d6abfc8cbeb24038df3a09e98f0beb4c23a6d362` |
| `ideas/artifacts/ECDLP-IDEA-012/p1553_determinant_value_channel_audit_r1.md` | `5073e39388792ea9cd8a4f7a1fe19f33f2799e59aa85f898148c9712bb963669` |
| `coordination/tasks/TASK-20260718-P1553-DV-AUDIT-R1/static_audit.md` | `dc147bd70028a04ff8cc2211bbc15db148a9ee6b4a882fe5ca550bb2780d4b67` |
| `coordination/tasks/TASK-20260718-P1553-DIVISOR-RT-R1/divisor_gate_notes.md` | `3df3476d1562253e6587c3139935990e431b4342c1a2f6d48bd67ab117907d84` |
| `ideas/artifacts/ECDLP-IDEA-195/p1551_finite_domain_selector_circuit_gate.md` | `5f1bd9c12ca700074c9cd327f6539bc880ec60b27431dc5f34e23b0a12f6c68f` |
| `ideas/artifacts/ECDLP-IDEA-158/p1534_r1_independent_audit.md` | `6a2c96f41552f91ab6d6ddc4801d6e4f958cf5845f6f81676de7f4db89653c53` |
| `ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3_audit_v2.md` | `407e3c7da6345f156f7c6bcaa75749e16b6184735d32be4b6e4aca69427763d5` |
| `ideas/rejected/ECDLP-IDEA-156_combinatorial_nullstellensatz_source_self_reduction_hypothesis.md` | `228c2d55df137225c92f2a14afca188d09bc8917ced63b6c4d4ac2027accda39` |
| `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md` | `ab36b80667d444a6be41439b89e8c133f2ef3e8fdeef0babb8408cccea84399e` |
| `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md` | `a9529076339b09b881d4504de45c132219352d4e0edc282cc0d2d955577ea1b1` |
| `ledger/FINDING-PF-IC-001.md` | `477c2a821363e041f5e3d6a2e183cd4c351affd08f89a576902b537b846fe487` |
| `focus/current_plan.json` | `65048074479b6010efcc17c13b674bb7758bb1f6cd97ca68c02ae68c770ccc43` |

The two declared dependencies were `completed` in the frozen queue. This
report does not mutate their receipts or the queue.

## 1. Typed finite-deck model

Let `E/F_p` contain the public prime-order subgroup `G=<P>` of order
`N=p^(1+o(1))`, and put

```text
B=N^(1/5).
```

For a relation campaign, let `F_1,...,F_5` be labelled signed factor decks and
let `F_6` be a labelled deck of known-log targets, all of size `Theta(B)`.
For one fresh target `R`, freeze the sixth row to the signed point dictated by
the P1553 convention. A deck label, not merely an x-coordinate, identifies an
actual signed point and its public source dictionary entry.

Let

```text
V=F_p^6,
v(A)=(1,x(A),y(A),x(A)^2,x(A)y(A),x(A)^3),
D(A_1,...,A_6)=det(v(A_1),...,v(A_6)).
```

The scalar formula is evaluated in one coherent affine frame. Its zero set is
frame invariant, and on P1553's checked pairwise-disjoint stratum,

```text
D(A_1,...,A_6)=0  iff  A_1+...+A_6=O.
```

The exact Fermat mask is

```text
M(A_1,...,A_6)=1-D(A_1,...,A_6)^(p-1).
```

It is a relation indicator only on that checked stratum. If repeated
cross-colour points are admitted, repeated determinant rows create automatic
zeros unrelated to the Abel sum. A passing all-strata operation must either
enforce and charge the frozen disjoint-deck/target/mask rebuild policy or
supply a globally confluent determinant and complete charts.

For exact finite-domain arithmetic, use the labelled split algebras

```text
A_i=Map(F_i,F_p) isomorphic to F_p^B,
A_S=tensor_(i in S) A_i,
dim(A_S)=B^|S|.
```

The fixed-target source algebra is `A_[5]`, of dimension `B^5`; the direct
campaign algebra is `A_[6]`, of dimension `B^6`. Polynomial quotients by
squarefree deck polynomials are equivalent split presentations only after the
signed dictionaries and exceptional charts are carried separately.

## 2. Exact pre-mask CP and TT ranks

### 2.1 Six-deck determinant tensor

Let `T_D` be the order-six deck tensor with entries

```text
T_D[j_1,...,j_6]=D(A_(1,j_1),...,A_(6,j_6)).
```

For an arbitrary cut `S | S^c`, `|S|=s`, the determinant factors through the
perfect wedge pairing

```text
Lambda^s(V) x Lambda^(6-s)(V) -> Lambda^6(V) isomorphic to F_p.
```

Therefore the exact flattening rank is

```text
rank Flat_S(T_D)
= rank of the wedge pairing restricted to
  span{wedge_(i in S) v(A_(i,j_i))}
  x span{wedge_(i not in S) v(A_(i,j_i))}
<= binomial(6,s).
```

If every coloured row deck spans `V`, both wedge spans are full and the ranks
are exactly

```text
s:                         1   2   3   4   5
generic ordered TT rank:   6  15  20  15   6.
```

The CP rank is the CP rank of the alternating six-tensor after full-rank mode
embeddings. The task needs no unproved exact value; the coefficient-complete
bounds are

```text
20 <= rank_CP(T_D) <= 6! = 720
```

under the same full-span hypothesis. The lower bound is the central
flattening rank; the upper bound is the public Leibniz expansion. Thus the
pre-mask predicate tensor has a public constant-rank representation and
`O(B)` factor storage.

### 2.2 One fixed target

Fix a nonzero target row `r=v(-R)`. The alternating five-linear form

```text
D_R(A_1,...,A_5)=det(v(A_1),...,v(A_5),r)
```

descends to the volume form on `V/<r>`, of dimension five. If every projected
factor deck spans that quotient, the ordered TT ranks are exactly

```text
s:                         1   2   3   4
generic ordered TT rank:   5  10  10   5,
```

and

```text
10 <= rank_CP(T_(D_R)) <= 5! = 120.
```

Again this is an exact, publicly constructed compact predicate. It evaluates
one supplied tuple; it does not aggregate its zeros.

## 3. Schur powers and row-mode contraction

Write `D^[q]` for the entrywise `q`-th power. Across an `s | 6-s` cut, the
pre-mask determinant has wedge rank `c_s=binomial(6,s)`. Taking the `q`-th
power of the wedge pairing gives the explicit symmetric-power bound

```text
rank Flat_s(D^[q])
<= min(B^s, B^(6-s), binomial(q+c_s-1,c_s-1)).             (1)
```

If `R_D` is any public CP upper bound for `D`, multinomial expansion gives

```text
rank_CP(D^[q]) <= binomial(q+R_D-1,R_D-1), R_D<=720.       (2)
```

For the fixed-target five-tensor, replace `c_s` by `binomial(5,s)` and
`R_D` by `120`. Equations (1)-(2) are constructors, but at `q=p-1` they are
far larger than the finite-grid caps and supply no useful contraction.

The elliptic row-mode reduction is real. With `L=O_E(6O)`, the pure `q`-th
power of one row factors through

```text
H^0(E,L^q), dim H^0(E,L^q)=6q.
```

Hence one unary deck mode has represented dimension at most

```text
min(B,6q).
```

At `q=p-1`, the global target mode is `B^(5+o(1))`; restriction to a fixed
deck caps one unary mode at `B`. Neither statement contracts the other four
or five source axes. A standard balanced merge still reaches a three-deck
object.

Two fixed powers are exact positive controls:

```text
q=1: weighted determinant contraction in O(B),
q=2: [t_1...t_6] det(sum_i t_i C_i),
     C_i=sum_A w_i(A)v(A)v(A)^T, also O(B).
```

Both contractions assign zero to true relations and can cancel on
nonrelations. They are not mask contractions.

Repeated squaring does not repair this. Hadamard multiplication multiplies CP
or TT ranks before exact recompression. Squaring after a scalar contraction
introduces cross-source terms. Recompressing the `p-1` power to its eventual
finite-deck rank requires either a source-sized flattening, a diagonal source
projector, or the support-sensitive operation derived below.

## 4. Exact post-mask ranks

The post-mask tensor has much smaller data-dependent rank than equations
(1)-(2) suggest. This fact is exact and must not be confused with a
constructor.

### 4.1 Arbitrary six-deck cuts

For a cut `S | S^c`, define the two endpoint maps

```text
sigma_S(j_S)=sum_(i in S) A_(i,j_i),
sigma_(S^c)(j_(S^c))=sum_(i not in S) A_(i,j_i).
```

Let

```text
H_S={g in G:
     sigma_S^(-1)(g) is nonempty and
     sigma_(S^c)^(-1)(-g) is nonempty},
r_S=|H_S|.
```

After grouping rows and columns by endpoint, the flattening of the relation
mask is a direct sum of one all-ones rectangle for every `g in H_S`:

```text
Flat_S(M)
= sum_(g in H_S)
    1_(sigma_S=g) 1_(sigma_(S^c)=-g)^T.                   (3)
```

The row and column supports of distinct summands are disjoint, so over every
characteristic

```text
rank Flat_S(M)=r_S.                                      (4)
```

For the ordered TT, the five exact ranks are `r_[1]`, ..., `r_[5]`. Let
`Z` be the number of labelled campaign relations. Delta tensors for the
actual source tuples give

```text
max_S r_S <= rank_CP(M) <= Z.                            (5)
```

If some cut assigns a distinct matched endpoint to every relation tuple, then
`r_S=Z` and the CP rank is exactly `Z`. In the random-support control,
`E[Z]=Theta(B)` and `E[r_S]=Theta(B)` for balanced admitted cuts, but that is
a heuristic/model-bound density statement, not a deterministic constructor.

### 4.2 Fixed-target cuts

For one target `R`, let

```text
M_R[j_1,...,j_5]
=1-D_R(A_(1,j_1),...,A_(5,j_5))^(p-1),
Z_R=sum_j M_R[j].
```

For every cut `S | [5]\S`, define `H_(R,S)` by matching the two partial sums
to `R`, and put `r_(R,S)=|H_(R,S)|`. The same block proof gives

```text
rank Flat_S(M_R)=r_(R,S),
max_S r_(R,S) <= rank_CP(M_R) <= Z_R.                    (6)
```

Four chosen factor points determine at most one fifth point, hence

```text
0 <= Z_R <= B^4 < p
```

asymptotically. Therefore the field trace of `M_R`, if computed, is the exact
integer count. The random-support control predicts `Z_R=Theta(1)` for a
typical target, but worst-case output and failed targets remain charged.

### 4.3 Rank of the Fermat power itself

On the finite deck,

```text
D^[p-1]=J-M,
```

where `J` is the all-ones rank-one tensor. At every cut,

```text
max(0,r_S-1) <= rank Flat_S(D^[p-1]) <= r_S+1,
rank_CP(D^[p-1]) <= Z+1.                                 (7)
```

The exact rank in (7) depends on whether unmatched row or column endpoint
blocks exist and, in the fully matched case, on the rank of the resulting
`J_r-I_r` core. This does not affect the gate: the dramatic rank collapse is
caused by the zero-support incidence itself.

## 5. Representation existence is not construction

The exact low-rank statements lead to three different storage receipts.

1. A support CP decomposition stores one delta product per relation. Sparse
   storage is `O(Z)` labels; ordinary dense CP factors use `O(BZ)` field
   entries. For a random-control six-deck campaign this is at most `B^2`, but
   every CP term already names a relation tuple.
2. A dense TT with ranks `r=Theta(B)` has internal core storage
   `Theta(B*r^2)=Theta(B^3)`, above the setup/state cap. A sparse path TT can
   store `O(Z)` nonzeros, but its paths again are the source tuples.
3. Minimal endpoint-block factors in (3) require the matched sets `H_S` and
   the occurrence lists on both sides. At the fixed-target central `2|3` cut,
   the standard constructor builds `B^2` pair endpoints and a target-dependent
   `B^3` triple side. At the six-deck central `3|3` cut, it builds or streams
   `B^3` endpoints on a side.

Consequently:

- CP or sparse-TT rank discovered after enumerating support receives no
  reporter credit;
- TT-SVD or exact rank recompression touches source-sized unfoldings in the
  direct representation;
- TT-cross or CP-cross requires a certified nonzero pivot or a pivot-search
  rule, which is already a source locator for this sparse tensor; and
- a general dense CP decomposition does not by itself provide a nonzero-entry
  algorithm. Cancellation among its terms must be resolved and charged.

The small post-mask ranks remain useful positive structure. They sharpen the
missing operation to a constructor-and-query problem rather than proving that
compact representations do not exist.

## 6. Finite-deck annihilator variants

The universal mask `1-T^(p-1)` has public coefficients and `O(log p)`
pointwise circuit depth. A deck-specific alternative can be written from the
complete attained nonzero value set

```text
S_R={D_R(j):D_R(j)!=0},
h_R(T)=product_(z in S_R)(1-T/z).
```

Then `h_R(0)=1` and `h_R(D_R(j))=0` on every nonrelation. This proves
representation existence, not a gain:

- constructing `S_R` or the coefficients of `h_R` is unsupplied without the
  fivefold determinant value image;
- one coherent degree-six slice already has `Omega(B)` attained nonzero
  values in the audited generic frame;
- the full fixed-target image can occupy field scale;
- contracting `h_R(D_R)` requires all of its determinant moments or an
  equivalent finite-domain operation; and
- a new target has a new value image, with no `B^(5/4)` coefficient update.

Prefix-specific degree-`Theta(B)` slice annihilators do not help: their
coefficients depend on the other four or five source choices, restoring the
prefix/source table. The minimal polynomial of multiplication by `D_R` is an
equivalent value-image object in the explicit `B^5` algebra.

## 7. Quotient, Frobenius, trace, and norm interfaces

### 7.1 Split quotient and Frobenius

In `A_[5]`, let `d_R` be the determinant element and

```text
m_R=1-d_R^(p-1).
```

Because `A_[5]` is a product of copies of `F_p`, Frobenius is the identity on
every element. Repeated squaring constructs `m_R` pointwise; it does not mix
source coordinates.

Multiplication by `m_R` is an idempotent projector. Exactly,

```text
rank(m_(m_R))=Tr_(A_[5]/F_p)(m_R)=Z_R mod p,
im(m_(m_R)) isomorphic to Map({relation tuples},F_p).
```

Since `Z_R<p`, its trace is the exact count. Restricting the five coordinate
multiplication operators to this image would recover the complete labelled
solution algebra and all source coordinates. This is an exact FFE
count-and-source formulation.

Its standard constructor has dimension `B^5`. A short circuit for the
diagonal entries does not compute the projector trace, image basis, primitive
idempotents, or simultaneous source decomposition. Constructing the small
image after locating its support is the same post-support compression as the
CP/TT factors.

### 7.2 Trace and transposed operations

The desired count is the linear functional

```text
Z_R=Tr_(A_[5]/F_p)(1-d_R^(p-1)).                         (8)
```

For `q=1,2`, special determinant identities evaluate related traces in
`O(B)`, but they have the wrong zero orientation. For `q=p-1`, standard power
projection, transposed modular composition, or trace algorithms are charged
in the represented quotient dimension `B^5`. Writing `Tr` after a compact
powering circuit omits the nonpointwise constructor in (8).

### 7.3 Norm and characteristic norm

The standard norm

```text
Norm_(A_[5]/F_p)(d_R)=product_j D_R(j)
```

is zero exactly when a relation exists on the checked stratum. It returns no
count and no source. The characteristic norm

```text
Chi_R(T)=Norm_(A_[5]/F_p)(T-d_R)
```

has `T`-adic order exactly `Z_R`, and its zero eigenspace is the solution
algebra. Thus a specialized circuit that constructs the relevant valuation,
restriction updates, and source idempotents would pass the semantic gate.

The standard product, resultant, multiplication-matrix, Krylov, quotient, and
post-hoc source-jet realizations retain `B^5`, `B^4`, or `B^3` represented
traffic as recorded by P1513/P1534/P1551. A product circuit's high divisor or
pole degree is not a circuit-size lower bound. A genuinely succinct
specialized characteristic norm remains an explicit exception.

### 7.4 Extension trace and norm

Moving the same split deck values to an extension field does not aggregate
source indices. Field trace repeats/scales coordinate values and field norm
changes their scalar encoding. It does not compute the source-algebra trace
in (8), the endpoint coefficient, or a signed source inverse. Any pairing or
character orientation supplied by an extension must be represented and
charged separately.

## 8. Endpoint convolution normal form

Let `F_p[G]` have basis `[A]` and multiplication `[A][B]=[A+B]`. For binary
or field weights `w_i` define

```text
U_i(w_i)=sum_(A_(i,j) in F_i) w_i(j)[A_(i,j)].
```

Then the exact conditional target count is

```text
C_R(w_1,...,w_5)
=[R] product_(i=1)^5 U_i(w_i).                           (9)
```

For `w_i=1`, equation (9) equals the determinant Fermat-mask trace (8) on the
checked stratum. Square-zero x/y or labelled marker channels give source
moments, but moments select a source only after uniqueness or a complete
conditioning protocol is established.

The standard endpoint realizations are:

| Representation | Exact content | Charged boundary |
|---|---|---|
| Point basis | Public insertion and exact convolution | `2+3` source split has `B^3` triple traffic |
| Full endpoint vector | Every target coefficient available | `N=B^5` modes and state |
| Character basis | Diagonal convolution | hidden scalar/pairing orientation or all `N` modes |
| Pair table | `B^2` exact signed pair endpoints | fits setup, but complementary triple query is `B^3` |
| Ranked subset or source DP | exact supplied-source coefficients | explicit subset/source deck; IDEA-199 control |
| Triangular dynamic evaluation | exact after a supplied source algebra | constructor/leaf degree; IDEA-266 control |
| Conditional coefficient formula | exact self-reduction if callable | the coefficient oracle itself; IDEA-156 control |

No read-scope artifact supplies a noncharacter, nonenumerative evaluator for
(9). ECFFT-style auxiliary evaluation does not diagonalize addition in the
arbitrary prime-order target group. This report claims no lower bound against
a new endpoint representation.

## 9. Fresh-target and restriction updates

Substituting a new target row into the pointwise determinant/Fermat circuit is
constant syntax work plus `O(log p)` arithmetic depth. This is not the target
update that the task requires. The missing update is the contraction of all
five source axes.

In endpoint form, the target-independent object is

```text
U=U_1(1)U_2(1)U_3(1)U_4(1)U_5(1),
Z_R=[R]U.
```

A dense `U` supports constant-time target lookup only after `B^5` state.
Pair preprocessing uses `B^2`, but a new coefficient still exposes the
`B^3` complementary side. In the global row-mode form, `R -> Z_R` lies in an
explicit target mode of size `6(p-1)=B^(5+o(1))`; interpolation on the `B`
known targets does not determine a fresh target value.

Post-mask CP and TT factors are target-support dependent. Updating from `R`
to `R'` requires new matched endpoint sets unless the producer supplies a
target-uniform recurrence. A rank statement for each target separately does
not bound that recurrence.

Source replay additionally requires restrictions. A passing reporter must
accept the canonical dyadic `0/1` weights used to restrict each deck. A fixed
unweighted coefficient, a campaign-only CP decomposition, or a target-only
norm does not provide those updates.

## 10. Conditional counts and exact signed source replay

The sharp positive interface is the following typed oracle.

```text
Preprocess(F_1,...,F_5) -> S
Count(S,R,w_1,...,w_5) -> exact integer C_R(w_1,...,w_5)
```

Required bounds are:

```text
Preprocess work and peak state <= B^(9/4+o(1)),
one Count query and workspace <= B^(5/4+o(1)).
```

The weights are public binary indicators for nodes of a fixed dyadic deck
partition. The output is target labelled, not an aggregate over the campaign.
Every conditional count is at most `B^4<p`, so its field value has an exact
integer lift.

If this oracle exists, one canonical source is replayed exactly:

1. Query the full decks; return `empty` if the count is zero.
2. Bisect the first active deck and query its left half. Keep the left half if
   its count is nonzero; otherwise keep the right half, whose count is parent
   minus left.
3. Repeat until one labelled index remains, then continue through all five
   colours.
4. Map indices through the signed dictionaries and verify the elliptic sum.

This uses `5 ceil(log_2 B)+O(1)` count queries, so it preserves the
`B^(5/4+o(1))` exponent. It is valid on multiple fibres because every retained
branch has a positive exact count. Recursing into both positive children
enumerates all labelled tuples in output-sensitive `O((Z_R+1)log B)` queries.

### 10.1 Classification of the coordinator count-to-source lemma

The coordinator-side lemma is exact. For arbitrary restricted subdecks
`F_i' subseteq F_i`, four selected points determine at most one fifth point,
so

```text
0 <= Z_R(F_1',...,F_5') <= product of the four largest |F_i'|
                         <= B^4 < p.
```

Thus the field-valued count is zero exactly when the restricted fibre is
empty. Binary partitioning one colour at a time deterministically returns one
labelled singleton tuple in

```text
sum_i ceil(log_2 |F_i|)=O(log B)
```

oracle calls, after which exact signed dictionary replay and elliptic
verification certify the row.

Classification: `deduplicated_conditional_reduction`, not a new
cryptanalytic operation. Search-from-counting by conditional restrictions is
the operation already isolated by IDEA-156's conditional coefficient
self-reduction and P1551's endpoint coefficient/source interface. The new
value here is a P1553-specific correction to the cost ledger: **source
unranking is not a separate exponent once a subset-stable exact count
constructor is supplied**.

The lemma fails to close the reporter on the following scope edges:

- subset indicators, their encoding, and every coefficient/contraction rebuild
  must fit the same query cap; a full-deck-only count is insufficient;
- the count must remain target labelled; an aggregate over `B` campaign
  targets can wrap or conceal which target has a source;
- the same target-independent state and restriction interface must accept a
  fresh blind target inside `B^(5/4)`;
- restrictions preserve, but do not create, the checked pairwise-disjoint
  determinant stratum; cross-colour overlaps still produce false zeros;
- signed dictionaries and final singleton verification remain mandatory; and
- output-sensitive enumeration of every tuple is separately charged when more
  than one source is required.

This is conditional source replay, not a supplied construction. It also does
not repair determinant false positives on overlap strata. A passing all-strata
version must charge complete signed dictionaries, infinity and alternate
charts, repeated occurrences, tangents, verticals, nonreduced fibres,
collision output, and every deck/target/mask rebuild or replace the determinant
by a proven confluent reporter.

The operation in (9) with dyadic weights is the exact finite-deck weighted
endpoint-coefficient oracle already isolated semantically by P1551 and the
rejected IDEA-156/199 records. This task sharpens its tensor and FFE
equivalences; it does not make the oracle mechanism-new.

## 11. Complete cost accounting

### 11.1 Audited realizations

| Route | Setup/state | Fresh target | Campaign or output | Result |
|---|---:|---:|---:|---|
| Public determinant CP/TT | `B` | supplied-tuple evaluation only | no aggregation | compact predicate, not reporter |
| Linear/quadratic moment | `B` | `B`-scale moment update | `B` | exact nonreporter |
| Direct fixed-target split algebra | `B^5` | `B^5` | `B^5` | trace/projector/source exact, fails |
| Direct six-deck split algebra | `B^6` | n/a | `B^6` | campaign exact, fails |
| Balanced explicit source/endpoint merge | at least `B^3` | at least `B^3` | at least `B^3` | fails setup and query |
| Pair plus streamed triple | `B^2` | `B^3` | `B^4` for `B` targets | setup only fits |
| Full endpoint vector/Fourier modes | `B^5` | lookup | `B^5` | fails state |
| Dense post-mask TT, rank `B` control | `B^3` | support dependent | `B^3` | rank does not fit dense cores |
| Sparse post-mask CP/TT | `O(Z)` to `O(BZ)` | support dependent | output sized | relation support already supplied |
| Standard norm/characteristic norm | `B^3` to `B^5` in named controls | `B^3` or worse | source jets/output extra | scoped failure |
| Hypothetical weighted coefficient oracle | `B^(9/4)` | `B^(5/4)` | `B^(9/4)` for `B` targets | unsupplied residual |

The `B^3`, `B^5`, and `B^6` rows are costs of the named representations, not
unrestricted circuit lower bounds.

### 11.2 End-to-end ECDLP ledger

Let setup, query, and their peak-memory exponents in base `B` be
`s,q,m_s,m_q`. Let an independently useful known-target row require
`B^delta` target trials, a blind target require `B^delta_t` trials, target
ambiguity/output cost `B^u`, and factor-log linear algebra use exponents
`ell,ell_m`. A complete path has

```text
lambda_B=max(s, 1+delta+q, ell, delta_t+q+u, 1+output),
mu_B=max(m_s, m_q, ell_m, 1+output, u),
lambda_N=lambda_B/5,
mu_N=mu_B/5.                                             (10)
```

The favorable advertised rectangle sets

```text
s,m_s<=9/4,
q,m_q<=5/4,
delta=delta_t=u=output=0,
ell<=2,
```

so `B` relation targets cost `B^(1+5/4)=B^(9/4)` and sparse factor-log
algebra costs at most `B^(2+o(1))`. This only models a possible
`lambda,mu<=0.45` path. It still requires proofs that:

- `Theta(B)` accepted rows have rank `B-O(1)` rather than duplicate support;
- every row is emitted with exact signed labels and verified;
- the factor-log system is solved and every recovered log is independently
  verified;
- the identical target-independent state and Count operation work for fresh
  `Q+[t]P` masks with charged failures and ambiguity;
- substituting factor logs and removing `t` yields a scalar whose multiplication
  verifies against `Q`; and
- output, field/bit arithmetic, random coins, deck rebuilds, target
  replacements, and live bytes fit (10).

No audited operation reaches the first Count query, so none reaches relation
rank, logs, or descent. The random constant-density model is not evidence for
these missing stages.

## 12. Sharpest scoped reduction

Within the exact disjoint-deck determinant semantics, the following two
interfaces are equivalent for the purpose of source replay up to logarithmic
factors:

1. a coefficient-complete determinant Fermat-mask contraction supporting
   target-labelled dyadic subdeck restrictions; and
2. the weighted endpoint-coefficient oracle (9).

The forward direction is the definition of the mask count. The reverse
direction follows because endpoint equality and determinant zero are
biconditional on the checked stratum, and the dyadic count protocol returns
an exact signed source. A specialized characteristic norm can substitute only
if it supplies the exact zero multiplicity or count, the same restriction and
fresh-target updates, and source idempotents; a bare norm bit is insufficient.

Every audited CP, TT, Schur-power, row-mode, split-quotient, Frobenius, trace,
standard norm, endpoint-convolution, and source-tree realization lands on one
of the following controls:

```text
post-support relation list;
B^3 central endpoint/source traffic;
B^5 fixed-target quotient or endpoint state;
B^6 campaign quotient;
pointwise predicate with no aggregation;
coefficient or source oracle renamed as a constructor.
```

This is an operation-level reduction. It does not prove the weighted
coefficient oracle impossible.

## Explicit untested exceptions

The conclusion does not classify or exclude:

- arbitrary arithmetic, Boolean, word-RAM, cell-probe, or algebraic circuits;
- a noncharacter, nonenumerative exact endpoint coefficient data structure;
- a succinct specialized elliptic product or characteristic-norm circuit with
  public coefficients, dynamic restrictions, and source idempotents;
- a CP/TT constructor with a proved nonzero-pivot and source-query algorithm
  that does not first locate support or materialize `B^3` traffic;
- target-specialized or reporter-family methods whose total advice,
  false-positive verification, update schedule, and source output are fully
  charged;
- special public deck families with proved relation density, independent rank,
  factor-log completion, and blind descent;
- extension-field, pairing, or character orientations whose construction does
  not reveal or assume hidden scalar labels and whose full mode costs fit;
- a globally confluent determinant/FFE reporter for repeated, tangent,
  vertical, infinity, and nonreduced strata; or
- an exact randomized method with a complete zero-error or certified replay
  argument and charged failure probability.

The universal relation-divisor degree lemma does not eliminate these classes.
Failure to construct them here is not a circuit lower bound, generic-group
lower bound, Shoup lower bound, or ECDLP impossibility result.

## Completion-gate receipt

| Required gate | Receipt |
|---|---|
| Public coefficient construction within `B^(9/4)` | fail: mask syntax public; contraction state unsupplied |
| Exact target-labelled count | formula exact; no passing evaluator |
| Fresh-target update within `B^(5/4)` | fail: syntax update only; coefficient contraction unsupplied |
| Exact conditional subdeck counts | reduction exact; oracle unsupplied |
| Exact signed source replay | conditional dyadic protocol exact; reporter and global all-strata predicate unsupplied |
| Pre/post-mask CP and TT accounting | pass as representation theorem, not algorithm |
| Quotient/Frobenius/trace/norm accounting | pass in named models; specialized norm open |
| Endpoint convolution accounting | pass in named models; noncharacter extractor open |
| `Theta(B)` independent rank | unsupplied |
| Factor logs and verification | unsupplied |
| Identical scalar-blind descent | unsupplied |
| Complete `lambda,mu<=0.45` | fail |

## Disposition

```text
INCOMPLETE_SCOPED_REDUCTION__PREMASK_DETERMINANT_HAS_PUBLIC_CONSTANT_CP_AND_
EXACT_GENERIC_TT_RANKS_6_15_20_15_6__FIXED_TARGET_RANKS_5_10_10_5__POSTMASK_
TT_RANK_EQUALS_MATCHED_ENDPOINT_COUNT_AND_CP_RANK_IS_BETWEEN_MAX_CUT_RANK_AND_
RELATION_COUNT__LOW_RANK_IS_POST_SUPPORT__SCHUR_ROW_MODE_FROBENIUS_TRACE_NORM_
AND_ENDPOINT_REALIZATIONS_EXHAUSTED_IN_NAMED_MODELS__STANDARD_CONSTRUCTORS_
RESTORE_B3_B5_OR_B6_TRAFFIC__DYADIC_COUNT_TO_SIGNED_SOURCE_REPLAY_EXACT_IF_
WEIGHTED_ENDPOINT_COEFFICIENT_ORACLE_EXISTS__ORACLE_AND_ALL_STRATA_REPORTER_
UNSUPPLIED__TARGET_UPDATE_RANK_LOGS_AND_DESCENT_UNSUPPLIED__SPECIALIZED_NORM_
NONCHARACTER_CP_TT_AND_UNRESTRICTED_CIRCUIT_EXCEPTIONS_PRESERVED__NO_P1554__
NO_RUN__NO_BREAKTHROUGH
```

Exactly one next action: obtain an independent theorem-only validation of the
rank formulas, the split-projector/endpoint equivalence, the conditional-count
source replay, and the representation-specific cost table. The validator must
either exhibit one public weighted coefficient or specialized characteristic-
norm constructor satisfying every gate, or preserve the scoped reduction and
all exceptions. Do not create P1554, a contract, solver, fixture, experiment,
or breakthrough claim.
