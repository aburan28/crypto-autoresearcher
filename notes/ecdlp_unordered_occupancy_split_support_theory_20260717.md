# Unordered Occupancy and Split-Support Theory for Recursive Point Decomposition

> **Red-team correction.** The multiset ceiling and asymptotic symmetry correction below remain valid. The original 128-target numerical match did not validate finite Poisson occupancy for a sign-complete base: exact support is governed by additional inverse-cancellation classes. See `experiments/EXP-ECDLP-ENERGY-001/interpretation-amendment-v2.md`.

Date: 2026-07-17

## Scope and claim boundary

This note formalizes the next recursive point-decomposition experiment suggested by `EXP-ECDLP-ENERGY-001` and `notes/coordinate_decomposition_theories_20260717.md`. It does not claim novelty.

The formal statements below concern finite sumsets, explicit split tables, and explicitly defined recursive compiler models. The random-occupancy statements are labeled `HEURISTIC`. The existence of useful coordinate-defined, source-tagged, or otherwise succinct recursive compilers remains `OPEN`.

Nothing here is an impossibility claim for prime-field ECDLP. In particular, the restricted table bounds do not cover arbitrary algebraic algorithms, nonuniform fixed-curve circuits, isogeny or representation changes, Gröbner/SAT methods, quantum algorithms, or data structures outside the stated access model.

## 1. Definitions

Let `G = <G_0>` be a cyclic group of prime order `q`, written additively. Let

\[
F=\{P_1,\ldots,P_B\}\subseteq G
\]

be a set of `B` distinct group elements. Unless stated otherwise, an `m`-term decomposition permits repeated use of a factor-base point and asks whether

\[
Q=P_{i_1}+\cdots+P_{i_m}.
\]

Define the multiset domain

\[
\mathcal M_m(F)=\left\{(n_1,\ldots,n_B)\in\mathbb Z_{\ge 0}^B:
\sum_i n_i=m\right\}
\]

and its sum map

\[
\sigma_m(n_1,\ldots,n_B)=\sum_i n_iP_i.
\]

The `m`-fold support is

\[
mF=\operatorname{im}(\sigma_m).
\]

For a uniformly random target `Q` in `G`, define the exact target-existence probability

\[
\epsilon_m(F)=\Pr[Q\in mF]=\frac{|mF|}{q}.
\]

This probability is a property of the final support. Representation multiplicity can help witness recovery after a target is in the support, but it does not by itself increase target coverage.

For a split `m=a+b`, write

\[
U=aF,\qquad V=bF,\qquad u=|U|,\qquad v=|V|.
\]

Then `mF=U+V`. A complete split compiler must decide whether `U` intersects `Q-V` and must return leaf witnesses for a matching pair of partial sums.

## 2. Why multiset occupancy comes before ordered-tuple occupancy

### Theorem 1: deterministic multiset ceiling

`THEOREM`.

For every finite subset `F` of `G`, with repetition allowed,

\[
|\mathcal M_m(F)|=\binom{B+m-1}{m}
\]

and

\[
|mF|\le \min\left(q,\binom{B+m-1}{m}\right).
\]

Consequently, any method using this exact `F` and exactly `m` terms that succeeds on an `epsilon` fraction of uniform targets must satisfy

\[
\binom{B+m-1}{m}\ge \epsilon q.
\]

#### Proof

Stars and bars counts the nonnegative multiplicity vectors of total weight `m`. Because `G` is abelian, every ordered tuple in `F^m` maps first to its multiplicity vector and only then to a group sum. Thus `mF` is the image of a domain of size `binomial(B+m-1,m)`, giving the support bound. Uniform-target success is exactly `|mF|/q`. ∎

### Consequence for `B^m`

`THEOREM` as a factorization statement; `HEURISTIC` when converted into an occupancy law.

The `B^m` ordered tuples are not `B^m` independent chances to hit a target. Permuting an ordered tuple leaves its sum unchanged. A multiset with multiplicities `n_1,...,n_B` has

\[
\frac{m!}{\prod_i n_i!}
\]

ordered realizations, all producing the same group element before any additional additive collisions are considered.

If `B` is much larger than `m`, then

\[
\binom{B+m-1}{m}\sim \frac{B^m}{m!}.
\]

Therefore a constant-occupancy design based on `B^m` of order `q` misses the first-order factor `m!`. The corresponding factor-base scale is

\[
B\asymp (m!\lambda q)^{1/m}
\]

when the desired occupancy parameter is `lambda`.

### Heuristic 1: unordered random-map occupancy

`HEURISTIC`, not a theorem about random elliptic-curve factor bases.

If the `N_m=binomial(B+m-1,m)` multiset sums behaved as independent uniform samples from `G`, then

\[
\mathbb E|mF|=q\left(1-\left(1-\frac1q\right)^{N_m}\right)
\]

and hence

\[
\epsilon_m(F)\approx 1-e^{-N_m/q}.
\]

For `N_m/q` much smaller than one, this reduces to `epsilon_m(F) approximately N_m/q`.

`EXP-ECDLP-ENERGY-001` showed that the ordered-tuple model is invalid for target existence, but its 128-target sample was too small to validate the multiset-Poisson formula. Exact sign-complete supports were `456`, `456`, and `2668`, below ordinary multiset counts `792`, `792`, and `4368` because inverse-pair cancellation identifies additional formal classes. The Poisson expression remains a sizing heuristic to calibrate against exact support, not a validated experimental law.

## 3. Caveats to the multiset model

### 3.1 Repeated points and source multiplicity

The count `binomial(B+m-1,m)` already permits repeated use of a point. If the intended decomposition requires `m` distinct factor-base points, the domain size is instead `binomial(B,m)`.

The symbol `B` must count distinct group points, not source parameters. If a rational map, coordinate predicate, or union construction emits the same point more than once, those duplicate source descriptions do not create new target support. They may create additional witnesses or source tags, but occupancy must be computed after point deduplication.

Including the identity permits cost-free padding and changes exact-length semantics. The next experiment should either exclude the identity or report exact-length and at-most-`m` support separately.

### 3.2 Signs and inverse pairs

For a sign-complete set `F=-F` of cardinality `B`, Theorem 1 still applies literally. It can nevertheless be loose because every inverse pair gives

\[
P+(-P)=0,
\]

creating systematic collisions and allowing shorter decompositions to be padded by cancellation pairs.

For a sign-canonical base `A={P_1,...,P_b}` with no inverse pair in `A`, exactly `m` independently signed leaves reduce to a net coefficient vector `c` in `Z^b` satisfying

\[
\|c\|_1\le m,
\qquad
\|c\|_1\equiv m\pmod 2.
\]

The number of such coefficient vectors is

\[
D(b,m)=\mathbf 1_{2\mid m}+
\sum_{\substack{1\le j\le m\\j\equiv m\ (2)}}
\sum_{k=1}^{\min(b,j)}
2^k\binom{b}{k}\binom{j-1}{k-1}.
\]

This is an upper bound on signed target support; distinct coefficient vectors can still collide in `G`. It is the appropriate first domain count when cancellation-equivalent signed words are canonicalized. Counting `2^m binomial(b+m-1,m)` treats many cancellation-equivalent words as independent and is not valid for target-existence occupancy.

The next experiment must report both conventions explicitly:

- sign-complete point-set size and multiset count;
- sign-canonical orbit count and net-coefficient count `D(b,m)`.

### 3.3 Cancellations and representation multiplicity

Large representation counts can arise from permutations, repeated leaves, inverse padding, or genuine additive collisions. Only the last category could indicate useful nontrivial additive structure, and even then it may reduce rather than increase final support.

The scalar-progression control in `EXP-ECDLP-ENERGY-001` is the relevant counterexample: pair energy increased and intermediate supports shrank, while five-term coverage nearly vanished. Thus pair concentration is not a sufficient surrogate for final target existence.

Every run should separate:

- number of distinct leaf multisets;
- number of sign-canonical net coefficient vectors;
- number of distinct partial sums at every node;
- multiplicity caused by permutation and cancellation;
- residual multiplicity caused by other sum collisions.

### 3.4 Nonrandom factor bases

The random-map heuristic assumes away the dependencies that the experiment is trying to exploit. Multiset sums sharing leaves are dependent even when `F` is sampled randomly. Coordinate-defined sets can add algebraic dependencies; sign-complete sets add exact inverse dependencies; progressions and unions can add structured collisions.

Therefore `N_m/q` is a necessary scale and a random-control predictor, not a sufficient prediction for a structured `F`. The exact primary metric remains `|mF|/q`, or a statistically controlled target-sampling estimate when exact enumeration is infeasible.

## 4. Necessary support and split-table conditions

### Theorem 2: split-support product bound

`THEOREM`.

For `m=a+b`,

\[
mF=aF+bF=U+V
\]

and

\[
|mF|\le \min(q,uv).
\]

If `U=V`, commutativity sharpens the domain ceiling to

\[
|U+U|\le \min\left(q,\binom{u+1}{2}\right).
\]

Thus success probability at least `epsilon` requires

\[
uv\ge \epsilon q,
\]

or `binomial(u+1,2) >= epsilon q` when the two split supports are the same set.

#### Proof

The sum map from `U x V` to `G` has image `U+V`, so its image has at most `uv` elements. When `U=V`, it factors through unordered pairs with repetition. ∎

This bound is necessary, not sufficient: many split pairs can collide on the same final sum.

### Restricted theorem 3: explicit flat split-table compiler

`RESTRICTED THEOREM` in the following model.

Assume the compiler:

1. materializes every distinct element of `U` and `V`;
2. stores at least one exact leaf witness for every materialized partial sum;
3. answers a query by scanning every element of the smaller support, forming its complement, and performing exact membership lookup in the larger support;
4. uses no routing oracle, compressed generator, false-negative filter, or batch sharing.

For distinct materialized tables, the compiler uses at least

\[
S_{\mathrm{entries}}\ge u+v
\]

support records and

\[
T_{\mathrm{probes}}\ge \min(u,v)
\]

complement probes per target. If `U=V` and the same table is reused, the entry floor is `u`, while the exhaustive scan still has `u` probes.

Under storage and query budgets `S_max` and `T_max`, necessary conditions for this flat compiler include

\[
uv\ge\epsilon q,
\qquad
u+v\le S_{\max},
\qquad
\min(u,v)\le T_{\max},
\]

with the preceding balanced-table adjustment when `U=V`.

These are not lower bounds for succinct recursive compilers. A compiler may store only one side, enumerate the other from a circuit, route queries to selected buckets, or batch work across targets. Such an escape must charge the generation, routing, false-candidate, witness-lifting, and memory-traffic costs that replace the omitted table entries.

### Necessary conditions at every recursive node

Let a recursive split tree have node `w` with children `x,y`, and let `A_w=A_x+A_y`. Write `n_z=|A_z|`. Then every node satisfies

\[
n_w\le n_xn_y,
\]

with the unordered-pair correction when the child supports coincide. Any claimed compressed recursion must report `n_z` for every node, not only aggregate advice size.

It must also provide:

- completeness: every claimed covered target has a path through the compiled supports;
- soundness: each returned path reconstructs the target by exact group arithmetic;
- witness liftability: every support or compressed-state record can be expanded to factor-base leaves;
- explicit failure semantics: false negatives, false positives, and unsupported targets are distinguished;
- preprocessing separation: factor-base construction, compilation, and per-target query costs are not merged.

### Theorem 4: some growth is necessary

`THEOREM`.

Let `A_k=kF`, `n_k=|A_k|`, and `g_k=n_{k+1}/n_k`. If `|mF| >= epsilon q`, then

\[
\prod_{k=1}^{m-1}g_k=\frac{|mF|}{B}\ge\frac{\epsilon q}{B}.
\]

Consequently at least one level obeys

\[
g_k\ge\left(\frac{\epsilon q}{B}\right)^{1/(m-1)}.
\]

So high final expansion is incompatible with uniformly tiny growth at every level under actual-support compression. It remains compatible with selected compressed levels followed by large cross-expansion, or with succinct representation of a large actual support.

## 5. The success-probability-aware `S T^2` comparison

### Model-bound diagnostic

`HEURISTIC` and `MODEL-BOUND`.

Let:

- `S` be fixed-curve advice size in a declared storage unit;
- `T` be online work per attempted target in a declared operation unit;
- `epsilon=|mF|/q`, or a statistically reported estimate of it;
- `M=epsilon q` be the number of targets covered by the fixed compiler.

If the adopted reference frontier is `S T^2` of order `M`, then the coverage-aware normalized diagnostic is

\[
R_{\mathrm{cov}}=\frac{S T^2}{\epsilon q}.
\]

This explains the `S T^2/(epsilon q)` quantity retained by `EXP-ECDLP-ENERGY-001`: it compares advice and online work with the size of the support actually served, rather than pretending that a low-coverage compiler serves all `q` targets.

This formula is not a theorem for unrestricted ECDLP algorithms, and a value below or above one has meaning only relative to the stated reference model and matched controls.

### Coverage normalization is not expected-success normalization

A fixed compiler covers a fixed subset `mF`. Repeating the same query against the same compiler does not turn an unsupported target into a supported one. Therefore `T/epsilon` is an expected cost per success only when an explicit independent retry mechanism is available, such as independently resampled factor bases or independent compiler schedules.

Under such a retry assumption, expected online work is `T/epsilon`. If each retry also needs fresh advice or preprocessing, that storage and preprocessing must be multiplied or amortized according to the actual schedule. The alternative expression

\[
\frac{S(T/\epsilon)^2}{q}
\]

answers a different question and must not be silently substituted for `R_cov`.

For a batch of `N` targets using one fixed compiler, report preprocessing `P`, total successes `K`, and at least

\[
\frac{P+NT}{N}
\quad\text{and}\quad
\frac{P+NT}{K}
\]

in each declared operation unit. The second quantity is undefined when `K=0`; replacing zero success by `1/N` is a censoring convention and must be labeled rather than presented as measured probability.

### Required units

The raw components must be reported even when a normalized product is shown:

- `S_entries`: number of support, bucket, routing, and witness records, broken down by type;
- `S_bytes`: serialized payload bytes and in-memory resident bytes;
- witness bytes: enough information to recover factor-base leaves, not membership-only storage;
- `T_group`: group additions, doublings, and negations per attempted target and per successful target;
- `T_field`: field multiplications, squarings, inversions, and batch inversions;
- `T_lookup`: hash, sort/merge, bucket, or tree probes;
- memory traffic: bytes read and written per query, plus peak and working-set memory;
- preprocessing: the same operation counts, storage writes, peak memory, and wall time, reported separately;
- probability: target sample count, successes, point estimate for `epsilon`, and a confidence interval;
- baseline: matched random, structured positive control, and Pollard-rho measurements in the same arithmetic implementation.

Numerically, `S T^2/(epsilon q)` carries the semantic unit “storage-unit times operation-unit squared per covered-target count.” Counts may be treated as dimensionless only after fixing a common encoding and primitive-cost model. An entry-based product cannot be compared directly with a byte-based product, and a lookup-based `T` cannot be compared directly with a group-operation-based `T`. At minimum, report separate entry/group-operation, byte/group-operation, and byte-traffic diagnostics.

## 6. High final expansion with compressed intermediate supports

### Open hypothesis

`OPEN`.

There may exist a family of fixed-curve factor bases `F_q`, term counts `m`, and recursive split trees such that:

1. final support remains large, `|mF_q|/q >= epsilon_0 > 0`;
2. selected intermediate nodes have smaller actual support than matched random controls, or large supports have exact succinct representations;
3. membership and witness lifting remain exact;
4. preprocessing, bytes, memory traffic, and success-aware online work improve on the matched random flat compiler;
5. total attack accounting, including relation use, rank, and target descent if claimed, is not hidden.

The first experiment ruled out only the tested x-interval, square-map, and rational-union aggregate sets under its toy protocol. It did not test source-tagged recursive states, `m in {6,8}`, alternative split trees, multi-target routing, or succinct non-table representations.

### Theorem 5: collision-energy support certificate

`THEOREM`.

Let a finite candidate domain `Omega` map to `G`, and let `r(t)` be the number of candidates mapping to `t`. Put `N=|Omega|` and

\[
E=\sum_{t\in G}r(t)^2.
\]

Then

\[
|\operatorname{supp}(r)|\ge\frac{N^2}{E}.
\]

#### Proof

Cauchy-Schwarz gives

\[
N^2=\left(\sum_{t\in\operatorname{supp}(r)}r(t)\right)^2
\le |\operatorname{supp}(r)|\sum_t r(t)^2.
\]

Rearrange. ∎

This supplies a sufficient certificate for expansion when the final collision energy is controlled. It does not make low energy necessary for large support: a distribution can have broad support plus a small number of very heavy points. The experiment should therefore measure exact support and energy rather than using either alone.

### Proof track

1. **Dependency-correct occupancy lemma.** For fixed `m` and a stated random-factor-base model in `Z/qZ`, bound the error between actual multiset occupancy and the independent random-map formula. Classify dependency pairs by shared leaves, repeated leaves, inverse pairs, and equal coefficient relations.
2. **Recursive support theorem.** Apply Theorems 2 and 4 at every candidate split tree and derive the minimum expansion jump required after each compressed node. Add the unordered correction whenever two child supports coincide.
3. **Final-energy certificate.** Use Theorem 5 with the multiset domain and with each split-pair domain. Seek a family whose intermediate collision energies are high enough to compress selected nodes while final collision energy still certifies support of order `q`.
4. **Succinct-compiler model.** Define an exact access model for source-tagged or compositional representations: encoding size, state enumerator, membership oracle, routing oracle, and witness decoder. Prove the advice/query statement only inside that model.
5. **Fixed-curve attack obligations.** If the compiler is promoted beyond decomposition, prove how its witnesses feed relation generation, matrix rank, and individual target descent. High decomposition coverage alone is not a sub-rho ECDLP result.

### Disproof and counterexample track

1. **Small-growth obstruction.** Search for a quantitative small-doubling or recursive-growth condition that forces `|mF|=o(q)`. The scalar progression is the positive control for this obstruction, not evidence against all structured sets.
2. **Cross-component blow-up.** For map unions, test whether source tags cease to compress once all cross-component sums needed for final coverage are included. A degeneration to the flat support table rejects that representation, not succinct compilers in general.
3. **Cancellation artifact.** Compare sign-complete and sign-canonical forms at matched sign-orbit budget. Reject gains caused only by inverse padding, duplicate source descriptions, or permutation multiplicity.
4. **Witness-decoding obstruction.** Construct cases where a succinct membership description exists but recovering leaf witnesses costs at least the flat scan or table. This would rule out the candidate compiler interface while leaving membership-only representations open for other uses.
5. **Success-adjusted reversal.** Try to reverse every apparent storage or query gain after charging `epsilon`, confidence bounds, bytes, memory traffic, preprocessing, and matched Pollard-rho work.
6. **Finite counterexample search.** On small prime-order cyclic groups, enumerate or optimize sets on the Pareto frontier

   \[
   (|2F|,|3F|,\ldots,|mF|)
   \]

   to find either explicit high-final/low-intermediate examples or evidence for a sharper restricted inequality. Any inferred inequality must then be proved or left as a conjecture.

### Model-escape routes

The explicit-table theorem can be escaped by a large support with a small exact circuit, asymmetric splits, source-tagged unions, batch routing, or algebraic membership tests. A structured-generic lower bound would still leave coordinate algebra, rational maps, endomorphisms, isogenies, and other representation changes outside its oracle model. An algebraic-degree obstruction would leave combinatorial or nonuniform data structures outside its model. No single negative experiment here closes all of these routes.

## 7. Requirements for the next experiment

The successor experiment should treat the following as preregistered correctness and interpretation gates:

- choose `B` from `binomial(B+m-1,m)/q`, not `B^m/q`, for `m in {5,6,8}`;
- use monotone prime subgroup orders and multiple seeds;
- deduplicate factor-base points before computing `B`;
- compare sign-complete and sign-canonical schedules using both multiset and net-coefficient domain counts;
- enumerate or independently verify every recursive support size and one leaf witness per support point;
- report split products, unordered balanced-split ceilings, collision energies, maximum multiplicities, and exact final support where feasible;
- compare flat tables with source-tagged or otherwise compressed states without changing the final witness set;
- report `S`, `T`, `epsilon`, `S T^2/(epsilon q)`, preprocessing, bytes, memory traffic, and confidence intervals separately;
- include matched random and scalar-progression controls and an exact arithmetic verifier;
- preserve the distinction between a decomposition compiler, a relation pipeline, and a complete ECDLP algorithm.

## Handoff: Unordered occupancy and split-support theory

### Claim or task

Use symmetry-corrected multiset occupancy and exact recursive support accounting to test whether high final point-decomposition coverage can coexist with cheaper intermediate compilation.

### Status

OPEN

### Assumptions

- `THEOREM`: target existence is bounded by the number of leaf multisets and by the support product at every split.
- `HEURISTIC`: matched random factor bases follow independent unordered occupancy closely enough to serve as a control.
- `MODEL-BOUND`: the `S T^2/(epsilon q)` comparison is a diagnostic for a declared fixed-curve advice/query model, not a universal ECDLP lower bound.
- `UNTESTED`: a source-tagged or compositional representation can compress intermediate access without losing final expansion or witness liftability.

### Evidence so far

- `TOY-EVIDENCE`: unordered five-term occupancy tracked the random controls in `EXP-ECDLP-ENERGY-001`.
- `NEGATIVE RESULT`: the tested coordinate families did not improve the preregistered joint energy, coverage, and offline-cost gate.
- `OBSERVATION`: the scalar progression compressed pair/triple supports but collapsed final target coverage, showing that intermediate concentration alone is insufficient.

### Failure modes

- Shared-leaf, sign, or coordinate dependencies invalidate the random-map occupancy approximation.
- Every compressed intermediate support forces final support below the required `epsilon q`.
- Source-tagged states expand to the same storage and query work as flat tables once cross-component sums are included.
- Membership is cheap but exact leaf-witness recovery dominates.
- A nominal `S T^2` gain disappears after success probability, bytes, memory traffic, preprocessing, and rho are charged.

### Next concrete action

Implement one independently verified successor sweep for `m in {5,6,8}` that computes exact multiset and sign-canonical domain counts, every node support in the chosen split tree, final coverage, witness validity, and the raw `S`, `T`, byte-traffic, and `epsilon` terms before evaluating `S T^2/(epsilon q)`.

### Artifact paths

- `research/ecdlp_unordered_occupancy_split_support_theory_20260717.md`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/notes/coordinate_decomposition_theories_20260717.md`
