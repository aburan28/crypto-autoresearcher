# Structural Ingredient Search for Prime-Field ECDLP

**Task**: TASK-20260804-068  
**Batch**: BATCH-065  
**Role**: Mathematical Analyst  
**Context decision**: DEC-20260804-13fd70  
**Recorded**: 2026-08-04

---

## Q1: SVP Superlattice Transfer Analysis

### Setup

The Gao-Feng-Hu paper (KN-LIT-b875db) solves SVP on a lattice `L` by constructing a
random superlattice `Γ ⊃ L`. Specifically: pick a prime `p`, take a random index-`p`
sublattice `M` of the dual `L*`, and set `Γ = M*`. Two structural facts carry the proof:

- **Containment**: every vector of `L` lies in every possible `Γ` (since `L = L** ⊂ M* = Γ`
  whenever `M ⊂ L*`).
- **Suppression**: non-target short dual vectors survive with probability `≈ 1/p`, preventing
  the superlattice from inheriting `L*`'s short-vector structure.

The algorithm draws samples from the Gaussian `D_{Γ,t}` (cheap, because `Γ` is smooth
at scale `t = √2·s`) and keeps the shortest nonzero vector that lies in `L` (cheap to
check, since membership in `L` is testable). The SVP bottleneck shifts from "sample `D_{L,t}`
below the smoothing parameter" to "draw enough superlattice samples until one lands in `L`",
and the probability that a sample from `D_{Γ,t}` lies in `L` is roughly `det(Γ)/det(L) = 1/p`.

### Proposed transfer to ECDLP

**The DLP lattice.** For ECDLP in a group of order `N` with generator `G` and target `Q = [k]G`,
the standard "DLP lattice" is the rank-2 sublattice of `Z^2`:

```
L_DLP = { (a,b) ∈ Z^2 : [a]G = [b]Q } = { (a,b) : a ≡ bk (mod N) }
```

A basis is `{(N, 0), (k, -1)}`. This lattice has `det(L_DLP) = N` and shortest vector
`v* = (k mod N, -1)` of norm `‖v*‖ ≈ N^{1/2}` (for random `k`).

**Proposed superlattice move.** Construct a random index-`p` superlattice `Γ ⊃ L_DLP`
using the Gao-Feng-Hu construction. The superlattice has `det(Γ) = N/p`.

**Claim to examine**: the shortest vector of `Γ` might be much shorter than `N^{1/2}`,
giving a route to recover `k`.

### Analysis: why the transfer fails

**Obstacle 1: The target vector `(k,-1)` is not preserved under the construction.**

In SVP, the goal is to find *any* short vector of `L` — and the key structural fact is that
every vector of `L` lies in every possible `Γ`. The algorithm can therefore simply keep the
shortest superlattice sample that happens to land in `L`.

For ECDLP, the goal is specifically to find the vector `(k,-1)` (or a scalar multiple that
reveals `k`). The containment property `v ∈ L ⊂ Γ` still holds: `(k,-1) ∈ L_DLP ⊂ Γ` for
every superlattice constructed from `L_DLP`. So `(k,-1)` is present in `Γ`. **But this is
exactly the same fact as saying `(k,-1) ∈ L_DLP` — it gives no new information.**

**Obstacle 2: The superlattice has a shorter basis, but its shortest vector is not
generically `(k,-1)`.**

Since `det(Γ) = N/p`, by the Minkowski bound the shortest vector of `Γ` satisfies
`λ_1(Γ) ≲ (N/p)^{1/2}`. For `p ≈ N^{1/3}`, this gives `λ_1(Γ) ≲ N^{1/3}`. This is
asymptotically shorter than `λ_1(L_DLP) ≈ N^{1/2}`. The superlattice does have shorter
vectors — but those shorter vectors are *random elements of `Γ \ L_DLP`*, not related to `k`.

To recover `k`, the algorithm would need a sample from `D_{Γ,t}` that lies in `L_DLP` —
but the probability of that event is `≈ det(Γ)/det(L_DLP) = 1/p` (by exactly the counting
argument in Gao-Feng-Hu). So the number of superlattice samples needed is `≈ p`. If
`p = N^{1/3}`, the total cost is `N^{1/3}` Gaussian samples, each requiring a membership
test for `L_DLP`.

**Obstacle 3: The membership test for `L_DLP` requires knowing `k`.**

A vector `(a,b) ∈ Z^2` lies in `L_DLP` if and only if `a ≡ bk (mod N)` — which is
precisely what we are trying to determine. Testing membership in `L_DLP` *is* solving
the DLP. There is no polynomial-time membership oracle for `L_DLP` unless `k` is known.

In the SVP setting, membership in `L` is testable in polynomial time because `L` is given
by an explicit basis. `L_DLP` is *not* given by an explicit basis in the ECDLP setting:
the basis `{(N,0), (k,-1)}` contains `k` as a parameter we are trying to find.

**Obstacle 4: The DLP lattice is the wrong object.**

The Gao-Feng-Hu machinery applies to an arbitrary full-rank lattice `L` given explicitly.
`L_DLP` is not explicitly given; it is implicitly defined by the DLP relation. Constructing
a superlattice of `L_DLP` requires knowing `k` (to write down the lattice), and if `k` is
known, the DLP is already solved.

One might try to work with the publically-known lattice `L_0 = {(a,b) : aN ≡ 0 (mod N)}`,
i.e. `Z^2` itself scaled by `N`. But then `det(L_0) = N^2` and `L_DLP` is an *index-N*
sublattice of `L_0`, not a superlattice — the containment direction is reversed.

### Verdict on Q1

**No transfer.** The Gao-Feng-Hu superlattice technique does not provide a route to
prime-field ECDLP speedup. The failure is structural:

1. `L_DLP` cannot be constructed without knowing `k`.
2. Membership in `L_DLP` cannot be tested without knowing `k`.
3. The shorter vectors of a superlattice `Γ ⊃ L_DLP` are elements of `Γ \ L_DLP` and
   carry no DLP information.
4. Even if one could construct `Γ`, recovering `k` from `Γ`-samples would require `≈ p`
   trials to produce a sample in `L_DLP`, at which point one is back to a variant of
   Pollard-rho with a different constant.

The methodological schema (construct a random object of controlled shape that contains the
target) requires that the target object be explicitly available and the membership test be
cheap. Neither holds for `L_DLP`.

**Transferable insight (narrow scope):** If an explicit rank-2 lattice related to ECDLP
could be constructed from public data alone — without knowing `k` — and if that lattice's
shortest vector were DLP-related, then the Gao-Feng-Hu sampling strategy could potentially
apply. No such lattice is known; this is equivalent to restating gap G-2 in DEC-20260804-13fd70.

---

## Q2: 2025-2026 Literature Search Results

### Search methodology

The following search terms were applied to `knowledge/literature/`:

- `ECDLP`, `elliptic.*discrete`, `prime.*field.*DLP`, `birthday.*exponent`, `sub-rho`
- Cross-filtered with `year: 2025` and `year: 2026`
- Additional manual inspection of the bulk-seeded 2026-07-24 entries (KN-LIT-1324 through
  KN-LIT-1400 range)

### Items found: 2025-2026 papers bearing on ECDLP

**1. KN-LIT-1331** — "A New Method for Solving Discrete Logarithm Based on Index Calculus"  
(Jianjun Hu, ePrint 2025/015, year 2025)

- Claims an improved Index Calculus algorithm for discrete logarithms over prime fields,
  described as extending the prior "IICA" by considering "integer down" cases.
- The entry is a stub generated from PDF first-pages (2026-07-24 bulk seeding pass);
  claims are not independently verified. The abstract language ("first time for the IICA
  to study the optimization...") does not suggest an asymptotic breakthrough — the framing
  is consistent with a cofactor-level improvement.
- **Relevance judgment**: Warrants inspection of the full text. The abstract language gives
  no evidence of a sub-rho result. If the paper provides a genuine sub-rho algorithm, it
  would contradict established GGM lower bounds (R-4 in DEC-20260804-13fd70) unless it
  uses a non-simulable oracle — which must be assessed.

**2. KN-LIT-1351** — "Brace for impact: ECDLP challenges for quantum cryptanalysis"  
(Dallaire-Demers, Doyle, Foo, arXiv 2508.14011, year 2025)

- Title indicates a quantum-cryptanalysis scope. The entry contains no abstract (first-page
  parse failure).
- **Relevance judgment**: Likely about quantum algorithms (Shor-class or resource
  estimation), not classical structural results. Does not bear on the classical structural
  ingredient search. Not relevant to gap G-2.

**3. KN-LIT-b875db** — Gao-Feng-Hu SVP superlattice (year 2026)

- Already analyzed above (Q1). Not an ECDLP result.

### Additional items in the 2025 seeded batch (year 2025, indirectly related)

- **KN-LIT-1350** — "Better Bounds for Finding Fixed-Degree Isogenies via Coppersmith's
  Method" (2025): Relevant to isogeny-path problems, not prime-field ECDLP.
- **KN-LIT-1382** — "Efficient Algorithms for Isogeny Computation on Hyperelliptic Curves"
  (El Baraka, Ezzouak, 2025): Hyperelliptic isogeny algorithms, not prime-field ECDLP.

### Overall finding for Q2

No paper in the 2025-2026 knowledge corpus provides a structural ingredient for prime-field
ECDLP that would satisfy gap G-2. The one directly-relevant 2025 paper (KN-LIT-1331,
ePrint 2025/015) is a stub entry describing an improvement to index calculus that, based
on abstract language, is likely a cofactor-level result. Its full text should be reviewed
to confirm there is no asymptotic claim before this can be closed.

**Caveat on recall**: The bulk seeding pass of 2026-07-24 generated stubs from PDF
first pages; many entries may be underspecified. A corpus-wide search cannot substitute
for a targeted literature survey of arXiv and ePrint in 2025-2026 on "ECDLP lower bound",
"prime-field discrete logarithm algorithm", and "subexponential elliptic curve". The
absence of a result in the current corpus is not evidence that no such result exists
(AGENTS.md knowledge retrieval policy rule 9).

---

## Q3: Wesolowski Pattern Applicability

### The four required components and their ECDLP analogs

**Component 1: Structural bound** (the load-bearing wall)

In Wesolowski: there exists an isogeny `E → E^{(p)}` of degree ≤ `(p/2)^{1/3}`. This is
a theorem (Aubry-Oyono-Vincent, KN-TECH-055 source ref [4]). It bounds the *size* of a
specific search object to `o(p^{1/2})`.

For prime-field ECDLP: the analogous object would be a "minimal decomposition" or
"minimal structural certificate" related to `k`. Candidates examined:

- **Semaev summation polynomial degree**: Fixed per order `m`, does not shrink with `N`.
  The first-fall degree is `O(1)` for fixed `m`, but this is a *negative* structural bound
  — the Bezout bound (R-1 in DEC-20260804-13fd70) says the factor base has O(1) elements
  for fixed-degree predicates, too small for an attack.

- **Shortest path in the isogeny graph**: The ordinary isogeny graph connects curves within
  an isogeny class. For a prime-field curve `E`, its `j`-invariant is fixed; the isogeny
  graph from `E` to itself requires endomorphisms (a different category from the
  supersingular setting). R-5 in DEC-20260804-13fd70 establishes that the scalar domain
  mismatch between ECDLP (scalars in `Z/N`) and ordinary isogeny structures (order `√p`)
  blocks any direct MITM reduction here.

- **DLP lattice structural bound**: The shortest vector of `L_DLP` is `(k,-1)` of norm
  `≈ N^{1/2}`, and this bound is tight — there is no theorem giving a shorter DLP-related
  vector, for the reason that `k` is uniformly random and `‖(k,-1)‖` is concentrated near
  `N^{1/2}`.

- **Hidden structural invariant**: No candidate has been identified in 64 batches of
  systematic search.

**Verdict on Component 1**: No structural bound analogous to the Wesolowski bound exists
for prime-field ECDLP. This is the precise statement of gap G-2 in DEC-20260804-13fd70.
Without Component 1, Components 2-5 have "nothing to bite on" (KN-TECH-055 transfer
note, lines 68-74).

---

**Component 2: Distribution heuristic**

In Wesolowski: the degree of the minimal isogeny is B-smooth with probability
`u^{-u(1+o(1))}` (Heuristic 1, justified by CEP + the structural bound).

For prime-field ECDLP: the Semaev decomposition probability is already a smoothness-type
heuristic — a point decomposes into `m` factor-base elements with probability `≈ B^m/(m!N)`.
This is the correct analog of Heuristic 1 and is the basis of the heuristic subexponential
complexity of index calculus. The distribution heuristic *exists and is validated* at toy
scale (R-2 in DEC-20260804-13fd70; EV-YIELD-e1adbf, EV-YIELD-ca4b02).

**Verdict on Component 2**: Available, but only useful if Component 1 produces a search
object to which the heuristic applies. Without a structural bound that shrinks the object
to size `o(N^{1/2})`, the decomposition probability gives only the known subexponential
(not sub-rho) complexity.

---

**Component 3: Split + meet-in-the-middle**

In Wesolowski: B-smooth degree `d` factors as `d = d_1 · d_2` with both `d_1, d_2 ≤ X ≈ d^{1/2}`.
The split requires multiplicative structure.

For prime-field ECDLP: the scalar `k` is a multiplicative integer, so splitting `k = k_1 · k_2 + r`
(or similar decompositions) is formally possible. Baby-step-giant-step is already a
meet-in-the-middle in exactly this sense, achieving `O(N^{1/2})` by splitting `k` at
`N^{1/2}`. The MITM structure is available, but it cannot beat the birthday bound without
a structural bound that reduces the range of `k_1, k_2` below `N^{1/2}`.

**Verdict on Component 3**: The MITM machinery is present and already in use (Pohlig-Hellman,
BSGS). It is not the bottleneck. The bottleneck is that the range of the split must be
`o(N^{1/2})`, which requires Component 1.

---

**Component 4: Rerandomization with mixing-time bound**

In Wesolowski: a random walk on the 2-isogeny graph of length `O(log p)` rerandomizes the
input curve, with mixing justified by spectral-gap results on expander graphs.

For prime-field ECDLP: the group `E(F_p)` is cyclic of order `N ≈ p`. Adding a random
multiple of `G` re-randomizes `Q` to `Q' = Q + [r]G`, with the new DLP `k' = k + r`.
This *is* a rerandomization and it *is* immediate (no walk needed — the group is abelian,
one step mixes perfectly). So Component 4 is available in a degenerate form.

**Verdict on Component 4**: Rerandomization is trivial and available. Not a bottleneck.

---

### What the Wesolowski pattern requires that prime-field ECDLP lacks

The Wesolowski pattern needs all four components simultaneously. Components 2, 3, and 4
are available for prime-field ECDLP in appropriate analogs. Component 1 — the structural
bound — is not. The pattern therefore does not apply.

The precise gap: a positive structural bound for prime-field ECDLP would say something
like:

> There exists a set `S_k` of size `N^{alpha}` for some `alpha < 1/2`, constructible in
> polynomial time from public data (not requiring knowledge of `k`), such that `k ∈ S_k`.

No such set is known. A "set containing `k`" of size `o(N^{1/2})` that is constructible
without knowing `k` would be a sub-birthday-bound algorithm by itself (just enumerate
`S_k`). The gap is therefore equivalent to the gap between any known classical result and
a sub-rho ECDLP algorithm — they are the same statement.

### On the "smallest natural quantity"

The question asks: what is the "smallest natural quantity" related to the DLP that might
serve as Component 1?

**Candidates and their disqualifications:**

| Candidate | Size | Reason it fails as Component 1 |
|---|---|---|
| Semaev relation degree `m` | O(1) | Bezout no-go: factor base too small (R-1) |
| Decomposition probability denominator | Θ(N) | This *is* the birthday bound, not below it |
| Arakelov height of `Q` on the curve | Θ(log p) | A geometric invariant of the *point*, not of `k` |
| Conductor of the CM field | Θ(sqrt(p)) | Only for CM curves; not a structural bound on `k` |
| `λ_1(L_DLP)` (shortest DLP vector) | Θ(N^{1/2}) | This is the birthday bound itself |
| A "Frobenius cycle length" on E | Θ(N^{1/2}) | Order of Frobenius in E(F_p) is N; no known reduction below N^{1/2} |

None of these gives a quantity of size `o(N^{1/2})` that is (a) computable from public
data without knowing `k` and (b) provably encodes information about `k`.

**Negative structural bound vs. positive structural bound:**

The Semaev heuristic complexity `L_p[1/2, c]` (subexponential in log p) constitutes a
positive structural bound of sorts: it says the search can be organized with `L_p[1/2,c]`
operations by exploiting the smooth-threshold structure of `F_p` as an additive group.
But this bound gives the exponent `1/2` in `exp(c·sqrt(log p · log log p))`, which is
subexponential but *not* sub-rho (sub-rho means polynomial in log p). A positive structural
bound strong enough to close gap G-2 would need to give polynomial — or at least `N^{alpha}`
for `alpha < 1/2` — complexity, which is categorically different.

---

## Overall Assessment and Proposals

### Assessment

**Q1 finding**: The Gao-Feng-Hu superlattice technique does not transfer to prime-field
ECDLP. The transfer is blocked by three independent obstacles: (i) `L_DLP` is not
explicitly given without knowing `k`; (ii) membership in `L_DLP` is not testable without
knowing `k`; (iii) shorter vectors of a superlattice `Γ ⊃ L_DLP` lie in `Γ \ L_DLP` and
carry no `k`-information. The methodological schema (random object containing the target)
requires an explicit target lattice with a tractable membership oracle; neither is available
for `L_DLP`.

**Q2 finding**: No 2025-2026 paper in the current corpus provides the structural ingredient
for prime-field ECDLP. The one directly-relevant entry (KN-LIT-1331, ePrint 2025/015) is
a stub and warrants full-text inspection before the absence can be confirmed. Corpus recall
is incomplete; an external arXiv/ePrint search in 2025-2026 is warranted.

**Q3 finding**: The Wesolowski pattern is not applicable to prime-field ECDLP because
Component 1 (structural bound) is not available. Components 2 (distribution heuristic),
3 (MITM split), and 4 (rerandomization) are all present in appropriate analogs. The
bottleneck is entirely at Component 1 — the absence of a theorem bounding some natural
DLP-related quantity to `o(N^{1/2})`.

### Narrowing the gap (proposals for next steps)

**Proposal A** — Full-text inspection of KN-LIT-1331 (ePrint 2025/015).

Priority: immediate. The entry is a stub. Confirm that the paper's claimed improvement is
cofactor-level (consistent with established results) and does not claim a sub-rho result.
If it claims sub-rho, assess whether it violates the GGM lower bound (R-4) and how.

**Proposal B** — External literature survey for 2025-2026 structural bounds.

Search arXiv and ePrint for papers published 2024-2026 matching: "elliptic curve discrete
logarithm", "prime-order group", "structural lower bound", "birthday bound improvement",
"sub-rho". The corpus is known to be incomplete on this dimension.

**Proposal C** — Formal examination of the "explicit-lattice" obstruction.

The Q1 analysis shows that the explicit-lattice requirement blocks the Gao-Feng-Hu
transfer. A stronger negative result would be: **no lattice technique can improve
prime-field ECDLP below N^{1/2} unless the lattice is constructible from public data alone
without knowing k** — and any such lattice is already subsumed by BSGS. This could be
formalized as a one-paragraph derivation and archived as an evidence record, since it
narrows the space of potential structural ingredients.

**Proposal D** — Search for non-lattice structural bounds.

The program has exhaustively searched algebraic and isogeny-based structural ingredients.
A remaining class is *arithmetic geometry* — specifically, results about the distribution
of discrete logarithms in thin sets (e.g., Heilbronn's theorem, Bourgain-Gamburd type
results on sum-product). These give bounds on the *additive* structure of `{k mod p}` for
random `k`, not the *multiplicative* (DLP) structure. Whether any such bound can be
bootstrapped into a Component-1 structural theorem is unclear but has not been
systematically assessed.

### Pareto assessment

| Direction | Time exponent | Memory | Status |
|---|---|---|---|
| Pollard rho (baseline) | 1/2 | polylog | established |
| Semaev index calculus | subexp(1/2) | subexp(1/2) | established |
| Any known attack improving on 1/2 | — | — | none found |
| Gao-Feng-Hu transfer | blocked (Q1) | — | not viable |
| Wesolowski-pattern analog | blocked (Q3) | — | Component 1 absent |

`dominated_by`: Pollard rho at exponent 1/2 for all classical attacks examined.

### Bottom line

After 64 batches plus this search, the program has not found a structural ingredient for
prime-field ECDLP that would enable a sub-rho algorithm. The Gao-Feng-Hu technique is
methodologically interesting as a pattern but does not transfer. The corpus contains no
2025-2026 paper that provides a structural bound. The Wesolowski pattern requires
Component 1, which does not exist in any known form. Gap G-2 (DEC-20260804-13fd70)
remains open.

The search is *not exhaustive* — Proposal B (external literature survey) and Proposal D
(arithmetic geometry) are unexplored lanes that should be assessed before the gap is
treated as insurmountable.
