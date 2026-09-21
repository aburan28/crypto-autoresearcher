# A1 — ECDLP index calculus: factor bases, decomposition, coverage, relation supply, linear algebra

Catalogue slice A1, dated 2026-08-05. Anchors: `KN-OPEN-001`, `KN-OPEN-003`,
`KN-OPEN-007`, `KN-OPEN-020`. This is a **catalogue**, not a ledger record: no
`IDEA-*.yaml` is filed here, no ID is minted, no status is changed.

## Standing conditions on every entry below

- **No novelty adjudication.** eprint/arxiv are unreachable from this
  environment. Nothing here is claimed to be new and nothing is dismissed as
  known. Every appeal to outside work is labelled an **unverified
  recollection** and may not be used as evidence (AGENTS.md rule 5).
- **Baseline.** Pollard rho at `c·sqrt(N)` group operations, `O(1)` memory.
  Prime-field index calculus has **no** known advantage (`KN-OPEN-001`) and this
  program's one support verdict for it was **retracted** (`EV-IC-002`, for
  revising a success criterion after the prior criterion was seen to fail). No
  entry below assumes an advantage.
- **Refuted-on-sight screens already applied.** (i) Mean decomposition yield is
  exactly `C(B+m-1,m)/N` for *every* base of size `B` (`KN-FIND-007`), so no
  entry argues mean yield; only coverage, relation **rank**, recognizability and
  **solve cost** appear. Coverage headroom is capped at `1.582`. (ii) The
  generic-fibre Frobenius/monodromy census is not used as a relation-rate
  instrument: `S_m` splits completely on the factor-base locus at every `m`
  (`KN-FIND-c41ea9`), so the statistic is constant where relation search lives.
- **Environment.** SageMath is unavailable and cannot be installed. Every test
  below is pure Python integer/`GF(p)` arithmetic, with `sympy` (present,
  1.14.0) used only for resultants. No entry is environment-blocked.
- **Claim ceiling.** Zero-compute entries top out at `derivation` (a checkable
  argument, never "proved"); measured entries top out at claim tier `toy`
  (`docs/claims-and-verification.md`). Stated per entry.

## Object-first framing (`docs/inventor-protocol.md` §§1–2)

Established families in this slice, **declared off-limits as the primary lens**:
(F-a) the relation vector over a fixed factor base; (F-b) the solving
degree / Gröbner descent on Semaev systems; (F-c) sumset coverage counting
(already worked: `KN-FIND-007`, `IDEA-20260801-021`); (F-d) the Frobenius
cycle-type census of the summation cover (closed as an instrument,
`KN-FIND-c41ea9`).

Candidate **tracked objects** used below instead, each with its
lossy-projection status:

| # | Tracked object | Lossy? | What is discarded, and why it still propagates |
|---|---|---|---|
| O1 | The **residual summand** `Q = R − (P_{i1}+…+P_{i,m−1})` of a partial decomposition | yes | forgets which `m−1` base elements were used, keeps only their sum; the group law makes the retained part propagate deterministically |
| O2 | The **half-sum** of a split decomposition | yes | forgets the ordered tuple, keeps the group element; addition is associative/commutative so the projection is compatible |
| O3 | The **free-relation lattice** `ker(Z^B → G)` restricted to vectors writable without search | yes | forgets all relations requiring search; closed under `Z`-linear combination |
| O4 | The **multiplicity function** `c_D(r)` viewed as coverage-vs-collision mass | yes | forgets which multisets collide, keeps the counts; conserved under the KN-FIND-007 double count |
| O5 | The **sparsity hypergraph** of the relation matrix (which columns each row touches) | yes | forgets the coefficient values entirely, keeps incidence; elimination fill-in depends only on incidence |
| O6 | The **rank increment** per harvested relation | yes | forgets the relation, keeps only the span; span propagates deterministically under adjunction |
| O7 | The pair (**SLP length**, **algebraic degree**) of the membership predicate | yes | forgets the point set, keeps two complexity measures; both are computable from the description alone |

Objects failing the lossy-projection test and therefore **not** proposed: the
raw tuple `(P_{i1},…,P_{im})` (nothing discarded — a change of coordinates);
the pair `(sum, product)` of `x`-coordinates of a decomposition (recoverable as
roots of a quadratic, the `KN-LIT-7595` worked failure).

`KN-OPEN-019` is open: this program has **no** written object-enumeration for
the ECDLP, so the table above is a **sketch, not a taxonomy**, and no entry
below claims completeness over objects.

---

### A1-1. The free-partial-relation route is Pollard rho wearing a factor base

**Claim.** In a prime-order group there is no cheap "large prime" stage.
Partial relations — `m−1` base points plus one unconstrained residual summand
`Q` — are *free* (`O(m)` group additions each, no solve at all), but `Q` is a
uniform group element, so the cycle/collision stage needs `Θ(sqrt(N))`
partials; steering `Q` into a prescribed second-tier set of size `L` costs
`Θ(N/L)` rejected trials per accepted partial, giving `Θ(N)` total. Both
branches reproduce or exceed rho, and the collision branch **is** a rho variant
(walk = "add `m−1` base points"), reproducible at `≈ m·sqrt(N)` with `O(1)`
memory under distinguished points. `IDEA-20260803-fa9839` names large-prime
harvesting (its `HEUR-AT-3`) as the one ingredient that could explain the
extension-field exponent and asks whether it ports to prime fields; this is a
direct answer with a named obstruction.

**Mechanism.** Tracks object **O1**. In factoring, "large prime" is meaningful
because the prime set is *size-ordered*: a smooth-with-one-large-prime relation
is exponentially more likely than a fully smooth one, and the large prime lives
in a bounded range. `E(F_p)` has no norm, no size order on group elements and
no multiplicative hierarchy; the residual `Q` of a random partial decomposition
is equidistributed over the whole group. Enlarging the second tier buys yield
and costs cycle count one-for-one, and constraining `Q` cheaply is exactly the
constrained-decomposition problem you started from.

**Minimal discriminating test.** Zero compute for the accounting; one cheap
measurement for the only escape. Measure the **collision time** of the map
`(i_1,…,i_{m−1}) ↦ sum of base points`, as a walk in `G`, against
`sqrt(pi·N/2)`, at `N ≈ 2^14/2^16/2^18` for `m ∈ {3,4,5}` and for the
factor-base geometries already implemented in `EXP-FB3-001`. If partial sums
concentrate (effective range `< N`), collisions arrive early and the route is
*better* than rho by that factor.

**Null object / control.** The identical collision-time measurement on (a) a
uniform random walk in `G` and (b) a matched random factor base. Plus the
cross-lane control shared by batch B1: re-run the same accounting over
`F_{q^n}` with the subfield base — the derivation must **not** produce a
no-go there, since index calculus demonstrably works in that setting.

**Falsifier.** Pre-registered: measured collision time `≤ 0.5·sqrt(pi N/2)`
systematically across sizes and geometries kills the closure (and is a positive
result — an effective range below `N`). Also killed if the accounting is shown
to admit a fourth branch, i.e. a way to sample decompositions conditioned on
`Q ∈ tier-2` at cost `o(N/L)` without a constrained solve.

**Cost.** implementation low, compute low.

**Ceiling.** A closure at the `docs/inventor-protocol.md` §4 standard for the
partial-relation escape route only — named obstruction (no size hierarchy on
group elements), argument (three exhaustive branches), forward guidance (the
route survives only if constrained decomposition sampling gets cheaper, which
is `KN-OPEN-001` restated more sharply). `derivation` level; the collision
measurement is `toy`. It closes **nothing** about `KN-OPEN-001` itself.

**Kills-it-early.** Check on paper whether the residual `Q` is uniform: if the
`m−1`-sum map has an image materially smaller than `G` for some admissible
base, the "uniform residual" premise fails and the whole entry must be
re-scoped before any run.

---

### A1-2. Algebra-free meet-in-the-middle decomposition costs exactly `N^{1/2+1/m}` — and its `D_trial` depends on `B`, which the filed arity-threshold optimizer assumes it does not

**Claim.** Two statements. (i) Point decomposition needs no algebra at all: a
meet-in-the-middle split finds an `m`-term decomposition in `B^{⌈m/2⌉}` time and
`B^{⌊m/2⌋}` memory. Optimizing `B` against the conservation-forced success
probability gives total relation cost `(m!N)^{(m+1−⌊m/2⌋)/m}`, i.e. `N^{1/2+1/m}`
at even `m` and `N^{1/2+3/(2m)}` at odd `m`, with memory `≈ N^{1/2}` — dominated
by rho on **both** axes at every finite `m`, approaching rho only as `m → ∞`.
This is a *baseline reproduction*, and it fixes the exact bar the algebra must
clear: the summation-polynomial solve must beat MITM enumeration by `N^{1/m}` at
arity `m` merely to reach parity with rho. (ii) **Successor audit of
`IDEA-20260803-fa9839`**: MITM supplies a universal achievable `D_trial = B^{⌈m/2⌉}`
that is a *function of `B`*, whereas that proposal's optimizer
`B* = [(m−1)m!N·D_trial/(2c_LA)]^{1/(m+1)}` treats `D_trial` as constant in `B`.
At `m = 9` the two disagree qualitatively: the threshold `d < (m−3)/4` reads
"wins" at `d = 5/9`, while the direct substitution `D = B^5` gives relation cost
`m!N/B^3 = N^{0.7}`, a loss. Either the optimizer needs a `B`-dependence clause
or its positive readings are unusable.

**Mechanism.** Tracks object **O2**. Split the `m` summands into halves, table
the `B^{⌊m/2⌋}` half-sums, enumerate the `B^{⌈m/2⌉}` complements of the target,
claw-find. Success probability per target is the KN-FIND-007 mean
`min(1, B^m/(m!N))`, exactly and geometry-independently. Expected total for `B`
relations is `B·B^{⌈m/2⌉}·m!N/B^m`, monotone decreasing in `B` for `m ≥ 4`, so
the optimum sits at the coverage boundary `B^m = m!N`. Under van Oorschot–Wiener
golden-collision search the memory can be traded down, giving `time ≈ A^{3/2}/w^{1/2}`
with `A = B^{⌈m/2⌉}` — the same memory-honesty accounting the target profile
requires (`docs/target-result-profile.md` A8).

**Minimal discriminating test.** Zero compute. (1) Derive the exponent
symbolically and verify numerically at `m = 3..12` to `1e-12`. (2) Substitute
`D_trial = B^{⌈m/2⌉}` into `fa9839`'s two-term model and check whether its
optimizer and its `d < (m−3)/4` threshold survive; report the signed
disagreement at `m = 4..10`. (3) Emit the `(time, memory)` pair at every `m`
plus the vOW tradeoff curve.

**Null object / control.** The nearby-object control: run the identical MITM
accounting over `F_{q^n}` with `B = q`, `m = n`. It must **not** return "worse
than rho at every `n`", because index calculus works there — if it does, the
accounting is wrong rather than the lane closed. Second control: recompute with
the naive independent-uniform yield estimate in place of the exact conservation
mean; the exponent must not move (only the constant may).

**Falsifier.** The exponent does not verify symbolically; or the MITM
substitution *does* satisfy `fa9839`'s optimizer stationarity (in which case
there is no audit finding and the entry collapses to (i)); or the
extension-field control returns a no-go.

**Cost.** implementation low, compute none.

**Ceiling.** `derivation`. An exact, unconditional-within-the-cost-model
statement that the algebra-free lane is Pareto-dominated by rho at every arity,
plus a quantified bar (`N^{1/m}`) for what the algebra must buy. It establishes
**no** prime-field advantage and closes `KN-OPEN-001` in neither direction.

**Kills-it-early.** Recheck `B·C/p_s` at `m = 4` by hand against `EV-IC-002`'s
committed `B = 14, m = 2` configuration: if the formula does not reproduce the
committed reachable-set bound `4·C(14,2) + 2·14 = 392` under the same counting
convention, the counting convention is wrong and everything downstream is void.

---

### A1-3. There is no descent stage — the omission flagged as making the two-term model a lower bound is identically zero

**Claim.** For point-decomposition index calculus over a **prime-order**
subgroup, the "descent" stage that `IDEA-20260803-fa9839` lists as an omitted
cost does not exist as a separate stage. Relations are collected by decomposing
random points `R_j = [a_j]P + [b_j]Q`; the target's own logarithm falls out of
the same linear system. Even in the variant where a distinguished target must be
decomposed separately, the charge at the two-term optimum `B* = N^{1/(m+1)}` is
`m!N/B*^m · D = N^{1/(m+1)}·D`, against relation collection at
`N^{2/(m+1)}·D` — smaller by exactly `N^{1/(m+1)}`, so no exponent moves. This
**repairs** a stated confounder: `fa9839` records that omitting descent makes its
model a lower bound, "the safe direction for no-go readings and the UNSAFE
direction for any positive reading". If descent is zero, positive readings become
safe on that axis, which changes how every threshold row may be quoted.

**Mechanism.** Tracks the stage graph of the algorithm rather than a
mathematical object; the content is bookkeeping, and bookkeeping is where this
program's binding constraint sits. Prime order removes the sub-base recursion
that makes descent expensive in NFS-style algorithms: there is no smaller
subgroup, no smoothness hierarchy, and rerandomizing the target `T → T + [r]P`
is exact and free, so a failed attempt costs one attempt and nothing else.

**Minimal discriminating test.** Zero compute. Write both accountings —
"relations from random `[a]P+[b]Q`" and "relations plus a separate target
descent" — and verify symbolically that the exponents agree at
`B* = N^{1/(m+1)}` for `m = 3..10`. Enumerate the variants in which descent
*does* reappear (two-tier bases, shrinking bases, target-dependent bases) and
charge each explicitly.

**Null object / control.** Apply the same argument to a **composite**-order
group, where Pohlig–Hellman gives a genuine sub-base recursion; the argument
must **not** carry there. A repair that survives a setting where descent
provably exists is not tracking descent.

**Falsifier.** A variant is exhibited inside the point-decomposition family
where descent costs `≥ N^{2/(m+1)}·D`; or the two accountings disagree
symbolically at any `m` in range. Either kills the "identically zero" reading and
leaves the confounder standing.

**Cost.** implementation low, compute none.

**Ceiling.** `derivation`; it removes one caveat from an existing model and
asserts nothing about ECDLP hardness. Depends on `fa9839`'s two-term charge,
which that proposal's own evidence records as **not tight** (it misses the
recalled extension-field exponent by `2/(n(n+1))`); the repair inherits that gap
in full and must say so wherever it is quoted.

**Kills-it-early.** Check whether any relation-collection scheme in the corpus
(`EXP-IC-001`, `EXP-SUBRES-001`) actually decomposes a *fixed* target rather
than random `[a]P+[b]Q` points. If the implemented schemes do fix the target,
the "no descent" reading applies to a different algorithm than the one measured.

---

### A1-4. The multi-target window: index calculus can beat multi-target rho only for a bounded batch size, and composing that with the preprocessing frontier forces per-target cost above `N^{1/3}`

**Claim.** Against the correct multi-target baseline `c·sqrt(KN)` for `K`
targets (van Oorschot–Wiener; Kuhn–Struik — recorded in `EV-IC-002` OBS-9 as
**absent from this corpus**, which is why the comparison has never been made),
an index calculus with precomputation `P` and per-target cost `D` wins for some
`K` **iff** `P < c²N/(4D)`, with the advantage maximised at exactly
`K* = c²N/(4D²)`, and rho winning again for all `K > c²N/D²`. The window is
therefore two-sided and closed in `K` — amortisation has a **ceiling**, which
this program has never written down. Composing with the preprocessing lower bound
`S·T² = Ω̃(N)` (`KN-LIT-013`, restated `KN-TECH-005`) at `S = B`, `T = D` gives
`B ≳ N/D²`, hence `P ≥ c_LA B² ≳ N²/D⁴`, hence `D ≳ N^{1/3}`, hence
`K* ≲ N^{1/3}` and a total of `≈ N^{2/3}` — which is exactly where multi-target
rho sits at that `K`. The two tie on the frontier at `S = T = N^{1/3}`.

**Mechanism.** Tracks the amortised cost curve rather than a group object. The
lever is that rho's *total* grows as `sqrt(K)` while index calculus's grows as
`K`, so index calculus can only live in a middle window; the window's existence
condition and its optimum both fall out of one stationarity computation. The
composition with the preprocessing frontier is the exponent-relevant half: it
says the batch route lands *on* the known frontier rather than beneath it.

**Minimal discriminating test.** Zero compute. Derive `K*` and the feasibility
condition symbolically; verify numerically at `m = 3..8`,
`N ∈ {2^160, 2^224, 2^256, 2^384}` with `c_LA`, `c_rho` pinned **before** any
number is computed; emit the `(K, advantage)` curve and the composed `D ≳ N^{1/3}`
consequence with every constant shown.

**Null object / control.** Two. (1) Recompute with the *single*-target baseline
`c·sqrt(N)`: the window must become one-sided (no upper limit in `K`), otherwise
the multi-target term is not doing the work claimed. (2) The extension-field
control: instantiate at `N = q^n`, `B = q`, `m = n` and check the window is
non-empty there.

**Falsifier.** `K*` or the feasibility condition does not verify symbolically;
or the composed bound does not reduce to the `S = T = N^{1/3}` tie (an arithmetic
identity, so a point prediction that can fail); or the sign of the window flips
under the declared `c_LA`, `c_rho` ranges, in which case the rows are
sign-indeterminate and unusable.

**Cost.** implementation low, compute none.

**Ceiling.** `derivation`. **Explicitly conditional**: `S·T² = Ω̃(N)` is a
*generic-group* preprocessing bound, and index calculus is precisely a
non-generic algorithm, so the composition does not bind it. The honest reading
is inverted and is the interesting one: an index calculus with `B·D² ≪ N` would
be a *demonstration of non-generic structure*, and this entry pins the exact
quantity to watch. It closes nothing.

**Kills-it-early.** Confirm from `KN-LIT-013`/`KN-TECH-005` as held in this
corpus whether the bound is stated for the generic group model and whether `S`
is measured in group elements. If `S` is measured in bits, the composition's
exponent changes and must be redone before anything is emitted.

---

### A1-5. Cayley–Bacharach free-relation census: plane interpolation supplies no relation it did not already know

**Claim.** For a factor base cut out on `E` by plane curves, the supply of
relations obtainable **without search** is exactly one per irreducible component
of the defining locus, and no more. Precisely: the projective linear system of
degree-`k` plane curves through any `3k` points of `E` has dimension `≥ k(k−3)/2`,
and the subsystem of degree-`k` curves *containing* `E` (the useless ones,
`E·H` with `deg H = k−3`) has dimension **exactly** `k(k−3)/2`. The two counts
coincide identically for every `k ≥ 1`. So a curve meeting `E` in a prescribed
`3k`-subset of the factor base, and in nothing else, exists **iff** that subset
already sums to `O` — i.e. iff the relation was already true. Interpolation is
therefore not a relation source; it is a relation *verifier*.

**Mechanism.** Tracks object **O3**. Over a finite field `Pic⁰(E)` is finite, so
*every* relation is realised by a rational function — "realisable by a function"
cannot be the notion of cheapness. The right notion is "writable without search",
and the dimension count above is exactly the obstruction to writing one down. The
`k = 1` case is the classical three-collinear-points fact; the general case is the
Cayley–Bacharach jump. The one genuinely free relation is the whole intersection
divisor: `E ∩ Z(f)` sums to `O` for any `f` not containing `E`, giving
`r_free ≥ 1`, and `≥ (number of components meeting E properly)` for a reducible
predicate — which quantifies one of `KN-OPEN-020`'s four named escapes ("multiple
constructible predicates") as a *bounded* bonus rather than an open threat.

**Minimal discriminating test.** Toy, pure Python, no Sage. On generated
prime-order curves at `p ≈ 2^12–2^16`: build `F = E ∩ Z(f)` for irreducible `f`
of degree `d = 2,3,4` and for reducible `f` with `2` and `3` components; compute
the rank over `Z/N` of the sublattice of `ker(Z^B → G)` spanned by the
intersection-divisor vectors, and compare against the predicted `r_free`
(= number of proper components). Then, for random `3k`-subsets, solve the
interpolation linear system and record the dimension jump; predicted jump `= 0`
unless the subset sums to `O`.

**Null object / control.** (a) Random `3k` points of `E` **planted** to sum to
`O` — the jump must be exactly `1`. (b) Random `3k` points not so planted — jump
must be `0`. (c) A matched random factor base with no algebraic description, for
which `r_free` should be `0` beyond the trivial. Without (a) the measurement
cannot distinguish "no jumps exist" from "the solver never finds jumps".

**Falsifier.** A dimension jump on a subset whose sum is **not** `O`; or
`r_free > (number of components)` for some tested predicate; or the two dimension
formulas failing to coincide at some `k` (an arithmetic identity, so a point
prediction that can fail).

**Cost.** implementation medium, compute low.

**Ceiling.** `derivation` for the dimension count, `toy` for the census. A §4
closure of the *plane-interpolation* free-relation route only. Forward guidance,
required in the same breath: space curves in higher-dimensional embeddings,
linkage/residual intersections (where the extra `3k − |S|` points are allowed and
*become* the decomposition problem), non-plane curve models (`KN-OPEN-003`), and
predicates with no polynomial description at all are all untouched.

**Kills-it-early.** Verify `k(k−3)/2` against the two counts by hand at
`k = 1,2,3,4` on paper. If they do not coincide at every one of those, there is
no obstruction and the entry is void before any code is written.

---

### A1-6. Coverage and free collisions are exactly complementary — a Sidon base has maximal coverage and zero free homogeneous relations

**Claim.** From the same double count that gives `KN-FIND-007`, for any base `D`
of size `B` and arity `m`:
`(collision mass) := Σ_r (c_D(r) − 1)^+ = C(B+m−1,m) − |mD|`, exactly. Each pair
of distinct multisets with equal sum is a homogeneous relation
`Σ a_i P_i = O` with known coefficients. Hence **free-collision relation supply
and coverage are conserved against each other**: a base that maximises coverage
(a `B_m`/Sidon base, which `EV-FBG-001`'s red team measured at coverage ratio
`1.1071`, attaining `min(1, mean)` exactly) has *zero* collisions and therefore
*zero* free homogeneous relations; a base that maximises collisions (the H017
small-multiples base, measured coverage ratio `0.0021` with concentration
`1224x`) has the maximum. The design axis KN-FIND-007 leaves open — coverage —
is therefore not independent of the rank axis, and the exchange rate is exact.

**Mechanism.** Tracks object **O4**. The total multiset mass is fixed by
conservation; only its split between "targets hit" and "excess multiplicity" is
free. The decision content is the *second* half: collisions are only useful if
they are (i) cheap to find and (ii) informative about the unknown logarithms.
Predicted dichotomy, stated as the falsifiable part: collisions that are cheap
to find are exactly those forced by additive structure already known to the
designer (arithmetic-progression bases, small-multiples bases), and those
relations lie in the span of that structure, so they carry rank but no
information — a base whose logs you know by construction is not a factor base.

**Minimal discriminating test.** Toy, pure Python, reusing the exact counter
already validated in `EXP-FB3-001` (288 cells, counter verified against brute
force on 46 cases). At `N ≈ 2^14/2^16/2^18`, `m = 3`: for each of {random,
Bose–Chowla `B_3`, interval, coset-union, small-multiples, greedy}, report
`(coverage, collision mass, rank over Z/N of the collision-relation lattice,
median cost to find one collision)`. The identity `collisions = C − |mD|` must
hold with deviation exactly `0` in every cell.

**Null object / control.** Matched random base at every size (the null under
which "cheap collisions ⇒ uninformative" must **fail**: a random base's
collisions are informative but cost a birthday search to find). Also a base with
known logs by construction, as the positive control for "cheap and
uninformative".

**Falsifier.** Any cell where the identity deviates from `0` (implementation
error, blocks everything); or — the interesting one — a base with
collision-finding cost `o(sqrt(N))` **and** collision-relation rank `≥ B − O(1)`
whose logarithms are not known by construction. That would be a genuine positive
and would supply free rank at sublinear cost.

**Cost.** implementation low, compute low.

**Ceiling.** `derivation` for the identity, `toy` for the census. It cannot show
a prime-field advantage and does not touch the solve cost, where `KN-FIND-007`
records that the index-calculus cost actually sits.

**Kills-it-early.** Check the identity by hand on one tiny cell (`B = 5`,
`m = 3`, `N = 23`) before any battery. `C(7,3) = 35` must equal
`|3D| + collision mass` exactly.

---

### A1-7. The signed-multiset accounting correction: a free factor `2^m` in relation supply at unchanged linear-algebra dimension — and whether it is free in rank

**Claim.** Every yield figure in this program's index-calculus accounting counts
**unsigned** multisets. Because `log(−P) = −log(P)`, using `±F` gives a base of
`2B` points but still only `B` unknowns: the multiset count becomes
`C(2B+m−1,m) ≈ 2^m·B^m/m!`, so relation supply multiplies by `2^m` while the
linear-algebra dimension is unchanged at `B`. This predicts the *already
measured* anomaly in `EV-SUBRES-001` OBS-6, where the frozen heuristic
`L^5/(5!q)` under-predicted the observed success rate by factors `27.9–41.1` at
`m = 5` against `2^5 = 32`. The correction is a **constant at fixed `m`** and is
stated as such; it moves no exponent. It does move every threshold constant in
`IDEA-20260803-fa9839`'s table, and — per `KN-FIND-c41ea9`'s scope note — a
per-fibre factor of `2` applied once per summation fibre with `m` growing
compounds as `2^{m−1}`, which is not a constant.

**Mechanism.** Tracks object **O4** on the symmetrised base. Two secondary
effects must be charged, and they point in opposite directions: the target space
effectively halves (solving for `−T` solves for `T`), a further factor `2` in
the designer's favour; and relations for `T` and `−T` are the same equation up
to sign, so a negation-closed target stream halves the *distinct* relation
supply. The net is the falsifiable part.

**Minimal discriminating test.** Zero compute for the count; toy compute for the
rank. Recompute the conservation mean over signed multisets and check it
reproduces `EV-SUBRES-001`'s measured ratios to within the reported spread.
Then, at `N ≈ 2^14/2^16`, harvest signed relations and measure the rank curve
against the unsigned one: does the `2^m` supply gain survive as a rank gain, or
does it collapse by the `T ↔ −T` dependency?

**Null object / control.** An arbitrary *unstructured* base of size `2B` with
`2B` unknowns — the matched-size comparison that `KN-FIND-007` forces. The claim
is not that `±F` beats a size-`2B` base on yield (it cannot; the mean is
identical); it is that `±F` gets size-`2B` yield at size-`B` linear-algebra cost.
The control isolates exactly that.

**Falsifier.** The rank curve for signed harvesting matches the unsigned curve
at matched relation count (the `2^m` is then supply without rank and buys
nothing); or the recomputed mean does not reproduce the `EV-SUBRES-001` ratios,
in which case the explanation offered there for its own falsified heuristic is
wrong and must be re-opened.

**Cost.** implementation low, compute low.

**Ceiling.** `toy`, and **constant-factor only** at fixed `m`. Priority is
justified not as an advance but as an accounting repair: it is an input to the
threshold table, and an uncorrected `2^m` is a `16×`–`64×` error in the
comparison the whole lane turns on.

**Kills-it-early.** Confirm `G` has no `2`-torsion (prime order `N` odd), so
`P ≠ −P` and `|±F| = 2B` exactly. If a tested instance has even order the count
is off by the fixed points and the prediction must be restated.

---

### A1-8. Relations needed is `Θ((B/m)·log B)`, not `B` — the coupon-collector term missing from every charged model in this corpus

**Claim.** Harvested relations are `m`-sparse rows over `Z/N`. Full rank requires
every factor-base element to appear in at least one row, so the number of
relations that must be *collected* is at least the coupon-collector threshold
`(B/m)·ln B·(1+o(1))`, not `B`. At `B ≈ 2^42` and `m = 4` that is a factor
`≈ 7`; formally it is `log B / m`. Every relation-collection charge in this
program's models — including `IDEA-20260803-fa9839`'s first term — assumes `B`
relations suffice. This entry can only move a **log cofactor**, and says so
plainly; it is catalogued as a building block because it multiplies the term that
the entire arity threshold balances against, and because the same measurement
answers a sharper question: is the full-rank threshold for these matrices at the
coupon-collector point, or later?

**Mechanism.** Tracks object **O6**. Unverified recollection (not usable as
evidence): for random sparse matrices over a large field, the full-rank threshold
coincides with the coupon-collector threshold, later corrections being `O(1)`
rows. The elliptic relation matrix differs in two ways that could break that —
coefficients are near-`±1` rather than uniform, and the rows are not independent
of the base geometry — so the coincidence must be measured, not assumed.

**Minimal discriminating test.** Toy, pure Python. Generate `m`-sparse relation
matrices over `Z/N` from harvested toy relations at `B ∈ {2^6 … 2^12}`,
`m ∈ {3,4,5}`; record rank as a function of row count; locate the threshold row
count `R*(B,m)` at which rank reaches `B−1`; fit `R*·m/(B ln B)` and test against
`1`.

**Null object / control.** Matrices with the same sparsity pattern but uniform
random nonzero entries in `Z/N` (isolates the coefficient distribution), and
matrices with uniform random *patterns* (isolates the geometry). If the elliptic
matrices match both nulls, the coupon-collector law transfers and the correction
is exactly `log B/m`.

**Falsifier.** `R*` sits at `B(1+o(1))` across the tested range — the
recollection is wrong, the correction is not `log B/m`, and the existing charges
were right. Equally decisive in the other direction: `R*` materially exceeding
`(B ln B)/m` would mean a *super*-logarithmic penalty and would make the
threshold table optimistic.

**Cost.** implementation medium, compute low.

**Ceiling.** `toy`; **log-cofactor only**, never to be presented as exponent
movement. Under `docs/target-result-profile.md` A1 this is explicitly
non-target-class.

**Kills-it-early.** Check whether the harvested rows in `EXP-IC-001`'s committed
records ever leave a column empty at the tested `B = 14`. At `B = 14`,
`ln B / m ≈ 0.66`, so the effect is invisible there and the measurement must run
at larger `B` to say anything at all — verify that before requesting budget.

---

### A1-9. The locality–rank trade: cheap linear algebra needs a local relation hypergraph, locality needs additive structure in the base, and additive structure destroys rank

**Claim.** The `c_LA·B²` linear-algebra charge is not a convention; for any
Krylov method it is forced, because the iteration count is at least the rank
(`B−1`, required for the system to determine the logarithms) and each
matrix–vector product costs `Θ(mB)`. The only escape is non-Krylov sparse
elimination, which beats `B²` **iff** the relation hypergraph has sublinear
separators — nested dissection gives `B^{3/2}` at `O(sqrt(B))` separators. The
claim is a trichotomy: a relation hypergraph with sublinear separators requires
relations to be *local* in some index metric; locality requires the map
`(i_1,…,i_m) ↦ Σ P_{i_j}` to respect that metric, i.e. the base to be an
approximate homomorphic image of a metric group; over a prime-order group the
only such bases are arithmetic-progression-like, whose logarithms are known by
construction and whose relation lattice is correspondingly degenerate. If the
trichotomy fails, the payoff is an **exponent**: with `c_LA·B^{3/2}` the
two-term optimum becomes `T* ≈ (ND)^{3/(2m+1)}` and the arity threshold moves
from `d < (m−3)/4` to `d < (2m−5)/6` — at `m = 4`, from `1/4` to `1/2`, a
doubling.

**Mechanism.** Tracks object **O5**, the incidence pattern alone, with all
coefficient values discarded — a genuinely lossy projection, since fill-in under
elimination depends only on incidence, so the retained part propagates
deterministically through the elimination order. Random `m`-uniform hypergraphs
with `Θ(B)` edges have treewidth `Θ(B)`, so the generic case gives no gain; the
question is entirely whether *structured* bases can induce structured incidence
without inducing degeneracy.

**Minimal discriminating test.** Toy, pure Python. For each base geometry
{random, interval, coset-union, small-multiples, Sidon, greedy} at
`B ∈ {2^6 … 2^12}`: harvest relations, build the incidence graph, run a
minimum-degree ordering and a recursive-bisection (nested-dissection proxy)
ordering, and record **jointly** (fill-in exponent, resulting flop exponent,
rank over `Z/N`). The prediction is a *product* invariance: every geometry with
flop exponent `< 2` shows rank `≪ B`.

**Null object / control.** Matched random base at every size — must show flop
exponent `≈ 2` and rank `B−1`. Second control: a synthetic *planar* sparsity
pattern with random coefficients, to confirm the ordering code actually detects
`B^{3/2}` when it is there. Without that positive control a null result measures
the ordering heuristic, not the hypergraph.

**Falsifier.** A base with measured flop exponent `≤ 1.6` **and** rank `≥ B−O(1)`
and logarithms not known by construction. That refutes the trade and opens an
exponent gain; it is the outcome worth hunting.

**Cost.** implementation medium, compute medium.

**Ceiling.** `toy` for the measurement; the trichotomy itself is `derivation` and
**scoped**: exact treewidth is NP-hard, so fill-in under two heuristic orderings
is a *proxy*, and a proxy failing to find a separator is not a lower bound. That
caveat must travel with every negative reading.

**Kills-it-early.** Compute the average degree of the incidence graph for the
random base: at `R ≈ B` relations of arity `m`, average degree is `≈ m`. Random
sparse graphs at average degree `≥ 3` are expanders, so if the structured
geometries produce the same degree sequence *and* the same girth distribution as
random, the separator question is settled negatively before any ordering is run.

---

### A1-10. Rank-supply instrument: is the rank axis as inert as the mean-yield axis?

**Claim.** `KN-FIND-007` and `EV-FBG-001` both record, explicitly, that relation
**rank and independence were never measured** and that the metrics "score a
rank-deficient base as tied with a random base of the same size". This entry
builds the missing instrument and states a falsifiable prediction: for every base
geometry whose logarithms are *not* known by construction, the expected rank
increment per harvested relation is indistinguishable from the matched random
base at every relation count — i.e. rank is a **second inert axis**, and of
`KN-FIND-007`'s four surviving arguable axes (coverage, rank, recognizability,
solve cost) only the last two remain live.

**Mechanism.** Tracks object **O6**: the span, forgetting the relations. The
prediction has a reason: a relation row's coefficient pattern is determined by
which base elements were used, and the *identity* of the logarithms enters only
through the target column. Two bases of the same size therefore present the same
row distribution up to relabelling unless the base carries additive structure
that makes rows repeat — which is exactly the degenerate case, and exactly what
`KN-FIND-009` formalises for a different lattice: rank deficiency guarantees
*some* relation, never a *short* or *useful* one, and the governing invariant is
relation-freeness at a threshold rather than a rank count.

**Minimal discriminating test.** Toy, pure Python, sharing the harvester with
A1-8 and A1-9. At `B ∈ {2^6 … 2^10}`, for each geometry, plot rank against
relation count and report the area between that curve and the matched-random
curve, with a permutation null over base relabelling.

**Null object / control.** Matched random base (the primary null) **and** a
planted degenerate base with logarithms `{1,…,B}` (the positive control, which
must show a visible rank defect). A run that cannot detect the planted defect has
no power and its null result means nothing.

**Falsifier.** Any geometry whose rank curve is *above* random at matched
relation count by more than the permutation null allows — a genuine positive,
meaning relation rank **is** a design lever. Symmetrically, if the planted
degenerate base is not detected, the instrument is blind and the entry produces
nothing.

**Cost.** implementation medium, compute low.

**Ceiling.** `toy`. A confirmed inertness result is a **screening rule**, in the
same class as `KN-FIND-007`, and its value is that it retires an axis rather than
that it advances an attack. It is `unverified` as a closure until the argument —
not just the tally — is written.

**Kills-it-early.** Ask on paper whether the harvested row distribution can
depend on the base at all once size is fixed. If a short argument shows it
cannot, the measurement is redundant and the entry converts to a zero-compute
derivation, which is cheaper and stronger.

---

### A1-11. The restriction-of-scalars audit: name the exact ingredient prime fields lack, and charge its absence

**Claim.** The extension-field construction's factor base
`F = {P : x(P) ∈ F_q} ⊂ E(F_{q^n})` imposes **no membership equation at all**:
the unknowns are declared to live in `F_q`, and Weil restriction turns one
`F_{q^n}`-equation into `n` equations over `F_q` in `m−1` unknowns. Membership is
free because it is a *choice of variable domain*, not a constraint. Over `F_p`
there is no proper subfield and no proper `F_p`-subspace, so no analogous domain
restriction exists; membership must be imposed as extra equations, and by Bezout
any plane predicate cutting out `B` points has degree `≥ B/3`, so the
decomposition system's Bezout number carries a factor `(B/3)^{m−1}` that has no
extension-field counterpart. The claim is that this — the absence of restriction
of scalars — is the *single* structural disanalogy, and that every other
ingredient (summation polynomials, conservation-mean yield, sparse linear
algebra) transfers unchanged.

**Mechanism.** Tracks object **O7**. This is the `docs/target-result-profile.md`
A4 move run in reverse: instead of hunting a structural ingredient that converts
a bottleneck into a tractable step, identify precisely which ingredient the
working setting has and the target setting lacks, so that the search for a
substitute is well-posed. Forward guidance falls out immediately: the substitute
would have to be a *ring-theoretic* rather than field-theoretic decomposition of
`F_p` (writing `x = x_1 + x_2·2^k`, which is exactly what interval/"small
height" bases attempt and exactly why they admit no bounded-degree algebraic
description).

**Minimal discriminating test.** Zero compute plus a small symbolic check;
`sympy` resultants only, no Sage. Write `S_3` over `F_{q^2}` explicitly, perform
the restriction of scalars to `F_q` by hand for `m = 3`, and verify that the
factor-base condition contributes **zero** equations of degree `> 1`. Then state,
as a table, each ingredient of the extension-field construction and whether it
has a prime-field analogue, with the Bezout penalty computed for each row.

**Null object / control.** Run the same restriction over `F_{q^n}` for `n = 3`
as a consistency check (the count of restricted equations must be `n`), and — the
load-bearing control — apply the *conclusion* to `F_{q^n}`: the argument must
**not** conclude that extension-field index calculus is obstructed.

**Falsifier.** The restricted membership condition turns out **not** to be free
(i.e. it contributes equations of degree `> 1`), which voids the identification
of the missing ingredient and the entry must be withdrawn rather than re-scoped.
Also falsified if a second, independent disanalogy is exhibited, since the claim
is that this is the *single* one.

**Cost.** implementation low, compute low.

**Ceiling.** `derivation`. It is an explanatory and search-directing result, not
a barrier and not an attack; it asserts nothing about whether a ring-theoretic
substitute exists. Unverified recollection, flagged as such: that this disanalogy
is discussed in the extension-field index-calculus literature. It may not be
cited as prior art or as support.

**Kills-it-early.** Count the variables and equations in the `F_{q^2}` case by
hand before writing any code: `1` equation over `F_{q^2}` in `m−1` unknowns
restricts to `2` equations over `F_q` in `m−1` unknowns. If that count is wrong,
the whole framing is wrong.

---

### A1-12. Predicate menu against the description-degree window — including an audit of whether that window is a constraint on the degree at all

**Claim.** `IDEA-20260803-e2f5bd` states an unconditional window: any algebraic
factor base that beats rho has description degree `d < (1/3)(c_rho/c_LA)^{1/2}·N^{1/4}`.
Two things follow, and the second must be checked first. (i) **Audit:** Bezout
gives `B ≤ 3d`, i.e. `d ≥ B/3` — a *lower* bound on `d`. A linear-algebra
constraint `B < X` therefore does not by itself yield `d < X/3`; that step needs
`B = 3d` (every intersection point rational and the base exhausting the
intersection), which the proposal's own null object contradicts, since the
quadratic-residue base has `d ≈ (p−1)/2` with `B ≈ N/2`. If the audit finds the
step used in the unpermitted direction, the "window" is a constraint on `B` alone
and must be restated. (ii) **Menu:** enumerate concrete prime-field membership
predicates and place each in the plane `(SLP length, algebraic degree, |F|)`,
testing whether any lands in the admissible region.

**Mechanism.** Tracks object **O7**. The tension is that the predicate must be
cheap to *evaluate* (so hits are recognisable) and low-degree as a *system* (so
the decomposition solve has something to exploit), and these are different
complexity measures that the quadratic-residue base already shows can diverge by
`N^{3/4}`. Menu rows: interval on `x`; `k`-th power residue; `x` in a prescribed
residue class; the intersection of `E` with a fixed low-degree plane curve; the
image of a low-degree rational map; a hash-defined base with `O(1)` evaluation
and no algebraic description.

**Minimal discriminating test.** Zero compute for the audit; low compute for the
menu. (1) Re-derive the parent's window symbolically and record which direction
of Bezout it uses. (2) For each menu row compute `|F|` exactly at toy `p`, the
minimal plane-curve degree cutting it out (lower-bounded by `|F|/3`, upper bound
by explicit interpolation), and an SLP length for membership. (3) Mark each row
admissible or not against the corrected window.

**Null object / control.** The quadratic-residue base, carried from the parent
as the row where Bezout holds and says nothing. Plus a row where the answer is
known: the `F_{q^n}` subfield line, which must come out **admissible** — a menu
that rejects the one construction known to work is measuring the wrong thing.

**Falsifier.** A menu row with `|F| ≈ N^{1/4}`, polylog SLP length, and system
degree `O(1)` — a genuine positive that would place a prime-field base inside the
window and make the arity threshold a live question rather than a screen. Or the
audit finds the window sound as stated, in which case (i) yields nothing and the
entry reduces to the menu.

**Cost.** implementation low, compute low.

**Ceiling.** `derivation`/`toy`. Successor to `IDEA-20260803-e2f5bd`, and it
inherits every dependency that record declares — including that its parent
`IDEA-20260803-fa9839` records its own two-term model as **not tight**. If
`fa9839`'s baseline-reproduction gate fails, `e2f5bd` is withdrawn and this entry
must be withdrawn with it, not reinterpreted.

**Kills-it-early.** Item (1) is itself the early kill and costs one page of
algebra: establish the direction of the Bezout step before spending anything on
the menu.

---

### A1-13. The index-calculus Pareto table: every configuration placed against rho, BSGS, van Oorschot–Wiener and the preprocessing frontier, in time **and** memory

**Claim.** This lane has no committed `dominated_by` artifact, so every proposal
in it reports domination by assertion. The claim is that a complete table can be
built with zero compute, and that under the two-term model **every**
point-decomposition configuration is Pareto-dominated by rho — because memory is
at least the factor base `B ≥ N^{1/(m+1)}` while rho's is `O(1)`, so index
calculus can win only on time, and its time is `Θ((m!N·D)^{2/(m+1)})` with `D`
free. The table's value is that it makes the *shape* of a non-dominated point
explicit: it must have time below `N^{1/2}` at memory below `N^{1/(m+1)}`, and the
only knob is `D`.

**Mechanism.** Not a new object; it is the `docs/inventor-protocol.md` §5
accounting obligation instantiated for the whole slice, and the
`docs/target-result-profile.md` A8/C13–C15 artifact (cost model, standardised
parameter sets, flagged optimism, hidden overhead, time–memory tradeoff,
parallelisation, affected-vs-safe scope) built once so that later entries cite it
instead of re-asserting.

**Minimal discriminating test.** Zero compute. Rows: rho `(N^{1/2}, O(1))`;
multi-target rho `(sqrt(KN) total, O(1))`; BSGS `(N^{1/2}, N^{1/2})`; vOW
golden-collision `(sqrt(A³/w), w)`; the preprocessing frontier `S·T² = Ω̃(N)`;
algebra-free MITM index calculus from A1-2 `(N^{1/2+1/m}, N^{1/2})`; two-term
index calculus at optimum `((m!ND)^{2/(m+1)}, N^{1/(m+1)})`; and the A1-9 variant
under a `B^{3/2}` linear-algebra charge. Columns: time exponent, memory exponent,
data/queries, parallel behaviour, what is hidden in `o(1)`. Constants pinned
before any row is filled.

**Null object / control.** The table must reproduce two known rows exactly —
BSGS's `(1/2, 1/2)` and the vOW tradeoff — under the *same* accounting used for
the index-calculus rows. A cost model that cannot reproduce the textbook rows is
not measuring the index-calculus rows either.

**Falsifier.** A row that is **not** dominated: any configuration with time
exponent `< 1/2` at memory exponent `< 1/2` under the stated model. That would be
the first non-dominated point in this lane and would be the finding. Conversely,
failure to reproduce the BSGS or vOW rows voids the table.

**Cost.** implementation low, compute none.

**Ceiling.** `derivation`, and explicitly **model-relative**: domination "under
the stated cost model" is not domination in fact, because `D` is free and the
model is known not to be tight. The table may not be quoted as evidence that
prime-field index calculus fails.

**Kills-it-early.** Fill the BSGS row first. If the accounting does not return
`(1/2, 1/2)` from the pinned constants, stop.

---

## Batches

Constraints respected: at most 3 concurrent non-archive tasks; disjoint write
scopes (one directory per batch under the batch's own artifact path); no batch
edits a shared ledger record.

### B1 — Charged-accounting closures (zero compute)

- **Objective.** Decide whether *any* accounting-level route — partial
  relations, algebra-free meet-in-the-middle, descent, multi-target amortisation
  — changes the comparison against rho, and repair the two accounting defects
  found in the filed models along the way.
- **Ideas.** A1-1, A1-2, A1-3, A1-4.
- **Why this grouping.** One shared kill-check, applied identically to all four:
  the **extension-field nearby-object gate** — every derivation is re-run over
  `F_{q^n}` with the subfield base, and any derivation that produces a no-go
  *there* is wrong rather than conclusive, because index calculus demonstrably
  works there. All four are also zero-compute and all four are successors to or
  audits of `IDEA-20260803-fa9839`, so they share its dependency: if that
  proposal's baseline-reproduction gate fails, A1-2's audit limb and A1-3's
  repair are withdrawn together.
- **Budget.** No compute beyond exact arithmetic and symbolic differentiation.
  One analyst-session; the only real cost is the blocking bibliographic subtask
  A1-4 inherits (the multi-target rho constant, which `EV-IC-002` OBS-9 records
  as absent and explicitly declines to assert — it must stay unasserted or be
  transcribed from a primary source).
- **What it decides.** Whether the large-prime escape named as the missing
  ingredient ports to prime fields; the exact bar the algebra must clear
  (`N^{1/m}` at arity `m`); whether descent is a real omitted cost or identically
  zero; and whether batch amortisation has a ceiling. A clean sweep here retires
  four routes at the cost of one session.

### B2 — Exact factor-base identities (toy enumeration, `N ≤ 2^18`)

- **Objective.** Complete the conservation picture on the axes `KN-FIND-007`
  leaves open, and correct the signed-multiset accounting error that
  `EV-SUBRES-001` already measured without naming.
- **Ideas.** A1-5, A1-6, A1-7.
- **Why this grouping.** One shared instrument: the exact sumset/multiset
  counter already built and independently validated for `EXP-FB3-001` (288 cells,
  counter verified against brute force on 46 cases, per-cell closed-form totals
  67 784 checks / 0 failures). All three are exact-counting statements over the
  complete target space at `N ≤ 2^18`, all three have an arithmetic identity as
  their own first falsifier, and all three fail together if the counting
  convention is wrong.
- **Budget.** Low compute (the existing battery ran 288 cells); pure Python, no
  Sage. Implementation is mostly reuse.
- **What it decides.** Whether free relations can be constructed rather than
  searched for (A1-5, expected negative with a named obstruction); the exact
  exchange rate between coverage and free collisions (A1-6); and whether the
  program's yield accounting is wrong by `2^m` (A1-7). Together they determine
  whether the *coverage* axis is finally exhausted.

### B3 — Relation rank and the linear-algebra exponent (toy matrices)

- **Objective.** Decide whether the `c_LA·B²` charge is forced, and whether
  relation rank is a design lever or a second inert axis.
- **Ideas.** A1-8, A1-9, A1-10.
- **Why this grouping.** One shared instrument — a relation-matrix generator
  plus rank-over-`Z/N` and elimination-ordering measurement — and one shared
  kill-check: a **planted positive control** in every run (a planted degenerate
  base for rank, a synthetic planar sparsity pattern for fill-in). All three are
  null results unless their planted controls fire, so they must be built and
  audited together or none of their negatives mean anything. Depends on B2 for
  the harvester.
- **Budget.** Medium compute: `B` up to `2^12`, exact linear algebra mod `N`,
  two ordering heuristics. Hours, not days; pure Python.
- **What it decides.** The one genuinely **exponent-moving** question in this
  slice: if A1-9's trade is false, the linear-algebra exponent drops to `3/2` and
  the arity threshold moves from `d < (m−3)/4` to `d < (2m−5)/6` — a doubling at
  `m = 4`. If the trade holds, `B²` is established as forced within the tested
  scope and the threshold table is stable.

### B4 — Description complexity and the frontier table (zero compute)

- **Objective.** Fix what a prime-field factor base is allowed to look like, and
  commit the lane's `dominated_by` artifact.
- **Ideas.** A1-11, A1-12, A1-13.
- **Why this grouping.** Shared object (**O7**, the description-complexity pair)
  and a shared dependency: all three quote a linear-algebra exponent, so all
  three must be emitted **parameterised** in it and re-read once B3 returns.
  A1-12's audit is the shared kill-check — if the parent's window is not a
  constraint on the degree, both A1-12's menu and A1-13's admissibility column
  change shape.
- **Budget.** Zero compute apart from small `sympy` resultant work for the
  `F_{q^2}` restriction and exact toy counts for the menu rows. One session.
- **What it decides.** Whether the single structural disanalogy with the
  extension-field setting is restriction of scalars (A1-11); whether any concrete
  prime-field predicate lands in the admissible window (A1-12); and whether any
  index-calculus configuration is non-dominated in the Pareto sense (A1-13).
- **Sequencing.** B1 and B4 are zero-compute and independent and may run
  concurrently; B2 precedes B3 (shared harvester); B4's tables are re-read after
  B3 rather than re-derived. Never more than three of the four in flight.

---

## Honest accounting (`docs/inventor-protocol.md` §5)

- **Objects considered.** O1–O7 above, plus two rejected by the lossy-projection
  test (raw decomposition tuple; `(sum, product)` of `x`-coordinates).
- **Depth of verified structure.** None. This catalogue contains **no measured
  result and no completed derivation**. Every exponent, identity and dimension
  count stated above is a *pre-registered prediction to be verified*, several of
  them arithmetic identities that can fail. Nothing here has been run.
- **`dominated_by`.** `n/a (no result claimed)`. No algorithm is proposed and no
  Pareto point is asserted by this document. The frontier rows against which any
  future result from this slice must be checked are enumerated in A1-13, and
  filling that table is itself one of the catalogued ideas — until it is filled,
  no entry in this slice may report `dominated_by: null`.
- **`sota_delta`.** Zero on every ECDLP cost axis: no attack, no measurement, no
  exponent moved in either direction. The instrument delta, if B1–B4 complete,
  would be four accounting repairs, two exact identities, one exponent-relevant
  linear-algebra decision, and the lane's first committed frontier table.
- **Enumerated closures.** None asserted. A1-1, A1-2 and A1-5 are *candidate*
  closures at the §4 standard — each names an obstruction, an argument and
  forward guidance — but each is unverified until its minimal test runs, and each
  closes one route rather than the lane. Per `docs/inventor-protocol.md` §4 and
  `KN-TECH-056`, "we screened `N` mechanisms" is a fatigue report; this document
  does not claim to have closed anything, and it does **not** conclude that this
  target is saturated.
- **Open directions for the next session.** (a) `KN-OPEN-019` — the ECDLP
  object-enumeration — remains unwritten, so the object table above is a sketch
  and this slice cannot support a saturation argument; (b) the ring-theoretic
  substitute for restriction of scalars named in A1-11's forward guidance;
  (c) constrained decomposition sampling — "sample a decomposition conditioned on
  all summands lying in a prescribed set, cheaper than meet-in-the-middle" — which
  A1-1 and A1-2 both reduce to and which is `KN-OPEN-001` in its sharpest form;
  (d) curve models and symmetries (`KN-OPEN-003`) are untouched by this slice;
  (e) the resultant-tree bond-rank question (`KN-OPEN-007`) is touched only
  obliquely, through A1-9's incidence-structure lens, and deserves its own slice.
- **Novelty status of this document.** `unverified` throughout. The corpus and
  ledger were grepped (`knowledge/`, `ledger/proposals/`, `ledger/evidence/`);
  external literature was **not** checked, because eprint and arxiv are
  unreachable from this environment. No entry is claimed novel and no entry is
  dismissed as known.
