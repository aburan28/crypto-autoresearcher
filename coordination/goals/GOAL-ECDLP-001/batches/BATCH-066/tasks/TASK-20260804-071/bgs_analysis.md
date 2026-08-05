# BGS Spectral Gap Analysis for Prime-Field ECDLP

**Task**: TASK-20260804-071  
**Batch**: BATCH-066  
**Role**: Mathematical Analyst  
**Decision context**: DEC-20260804-1bf901 (BGS direction rationale)  
**Recorded**: 2026-08-04

---

## Setup: BGS theorem and abelian groups

### The Bourgain-Gamburd theorem (2008)

Let `S ⊆ SL_2(F_p)` be a fixed symmetric generating set of bounded size (i.e., `|S| = O(1)`
independent of `p`). The Cayley graph `Cay(SL_2(F_p), S)` is a family of **expanders**: the
spectral gap of the normalized adjacency operator is bounded away from zero uniformly in `p`.
Concretely, there exists `ε > 0` (depending on `S` but independent of `p`) such that:

```
λ₁ ( Cay(SL₂(F_p), S) ) ≥ ε   for all primes p.
```

Here `λ₁` denotes the second eigenvalue of the normalized adjacency operator, and "spectral
gap" means `1 - λ₁ ≥ ε > 0`. The consequence for random walks: the random walk on
`SL_2(F_p)` driven by `S` mixes in `O(log |SL_2(F_p)|) = O(log p)` steps.

The extension by Bourgain-Gamburd-Sarnak (2010) establishes the same expander property for
Cayley graphs of thin subgroups `Γ < SL_2(Z)` reduced modulo `q` (for square-free `q`),
and connects the spectral gap to sieve methods in number theory.

**Crucial hypothesis**: BGS requires the group to be **non-abelian** (specifically, not
virtually solvable). The theorem exploits non-abelian multiplication to produce "expander
collisions" — additive energy concentration is used to show that random walks escape any
fixed proper subgroup exponentially fast. This is precisely the mechanism that fails for
abelian groups.

### What "spectral gap" means for abelian groups: Fourier analysis

For an **abelian** group `A` of order `N`, the Cayley graph `Cay(A, S)` has a completely
explicit spectral theory via Pontryagin duality. The eigenfunctions of the adjacency
operator are the characters `χ : A → ℂˣ`, and the eigenvalue of `χ` is:

```
λ_χ = (1/|S|) Σ_{s ∈ S} χ(s)
```

For `A = Z/N` (the cyclic group, written additively), the characters are
`χₘ(x) = exp(2πimx/N)` for `m = 0, 1, ..., N-1`. For a symmetric generating set
`S = {g₁, -g₁, g₂, -g₂, ..., gₖ, -gₖ}` (so `|S| = 2k`), the eigenvalue of `χₘ` is:

```
λₘ = (1/k) Σᵢ cos(2πm gᵢ / N)
```

The spectral gap of `Cay(Z/N, S)` is `1 - max_{m ≠ 0} |λₘ|`.

**Key calculation for the simplest case** (`S = {G, -G}`, `k=1`):

For `G = 1` (standard generator): `λₘ = cos(2πm/N)`. The maximum for `m ≠ 0` is
achieved at `m = 1` (or `m = N-1`), giving `λ_max = cos(2π/N)`.

Spectral gap `= 1 - cos(2π/N) ≈ 2π²/N² → 0` as `N → ∞`.

The mixing time of this walk is `Θ(N²)`. In general, for a bounded generating set of
size `|S| = 2k = O(1)`, the spectral gap satisfies:

```
Spectral gap = 1 - max_{m ≠ 0} |(1/k) Σᵢ cos(2πm gᵢ/N)|  ≤  C·k/N²
```

for some absolute constant `C`, by the Poincaré inequality (the Cheeger constant of
`Cay(Z/N, S)` is `O(1/N)`, giving a spectral gap of `O(1/N²)`). The mixing time is
therefore `Ω(N²/k²) = Ω(N²)` for fixed `k`.

**This is the quantitative version of the obstruction**: no bounded-size fixed generating
set can make the random walk on `Z/N` mix in fewer than `Θ(N^{2-o(1)})` steps.
The only way to get mixing time `O(log N)` on `Z/N` is to use `|S| = Θ(N)` generators —
which trivially solves the problem (you've enumerated all of `Z/N`).

---

## Why BGS doesn't apply to E(F_p) (abelian, prime order)

### The group structure

For a prime-order elliptic curve `E` over `F_p` with `#E(F_p) = N` (where `N ≈ p` is
prime by assumption), the group of rational points is:

```
E(F_p) ≅ Z/N
```

This is the cyclic group of prime order `N`. It is the **simplest non-trivial abelian
group**: no proper non-trivial subgroups, no non-abelian structure whatsoever.

### Failure modes

**Failure 1: Virtual solvability**

The BGS theorem requires that `S` does not generate a virtually solvable group. For
`A = Z/N`, any symmetric generating set `S` generates `Z/N` itself (if it generates at
all), which is cyclic and hence abelian, hence trivially solvable. Every subgroup of `Z/N`
is cyclic (prime order, so every non-trivial subgroup is `Z/N` itself). The BGS mechanism
does not engage.

**Failure 2: Additive energy concentration**

BGS proves the spectral gap by showing that if `S` generates `SL_2(F_p)`, then the
"additive energy" `E(S^{(t)}, S^{(t)})` cannot remain large as `t` grows (the product
set `S^{(t)}` undergoes non-abelian mixing). This argument relies on the non-commutativity
of matrix multiplication. For `Z/N`, the set `S^{(t)}` (the `t`-fold sumset) is a union
of arithmetic progressions, and it grows only as fast as its structure allows — which for
a fixed generating set of size 2 is linear: `|{g₁ t : t = 0,...,T}| = T+1` for the first
`T < N` steps. Additive energy is *persistently* concentrated.

**Failure 3: Character sum bounds**

The non-trivial part of BGS is showing that all non-trivial characters of `F_p^2 \to ℂˣ`
(i.e., matrix trace characters) give eigenvalues bounded away from 1. For `Z/N`, the
non-trivial characters are the Fourier modes `χₘ` for `m ≠ 0`, and `λₘ = cos(2πm/N)`
which approaches 1 for small `m/N`. There is no analogue of the BGS character-sum bound
in the abelian case; the abelian character sum *is* the eigenvalue, and it is not bounded
away from 1 by anything other than the generator-frequency condition.

### Quantitative summary

| Walk | Group | Mixing time | BGS applicable? |
|------|-------|-------------|-----------------|
| Bounded `S`, `|S|=O(1)` | `SL_2(F_p)` | `O(log p)` | YES (BGS 2008) |
| Bounded `S`, `|S|=O(1)` | `E(F_p) ≅ Z/N` | `Θ(N²)` | NO |
| Large `S`, `|S|=Θ(N)` | `E(F_p) ≅ Z/N` | `O(log N)` | Trivially (enumerates Z/N) |

For the ECDLP setting with `N ≈ 2^{256}`, "mixing time `Θ(N²)`" is catastrophically worse
than birthday (`O(N^{1/2})`). The abelian structure of `E(F_p)` is not an obstacle to be
worked around — it is a fundamental incompatibility with the BGS framework.

### Formal obstruction statement

**Proposition**: For any symmetric set `S ⊆ Z/N` with `|S| = d ≤ N/2`, the spectral
gap of `Cay(Z/N, S)` satisfies:

```
1 - λ₁ ≤  4π² d² / N²
```

**Proof sketch**: The spectral gap equals `min_{f ⊥ 1} Var(Tf) / Var(f)` where `T` is
the walk operator. Taking the test function `f(x) = exp(2πix/N)`, one gets
`Var(Tf) / Var(f) ≤ |λ₁|² ≤ (1 - 2π²/N²)²` for `d=1`. For general `d`, Cheeger-type
estimates give gap `≤ O(d²/N²)`. QED.

**Corollary**: Any random walk on `Z/N` with `|S| = O(1)` fixed generators has mixing
time `Ω(N²)`. Achieving mixing time `T_mix < N^{1/2}` (sub-birthday) requires `|S| = Ω(N^{3/4})`.
But `|S| = Ω(N^{3/4})` means the generating set has `Θ(N^{3/4})` distinct elements of
`Z/N` already — constructing it is at least as hard as computing Θ(N^{3/4}) scalar
multiples of `G`, which is already much more expensive than birthday.

**Conclusion**: BGS expander results provide zero improvement over birthday paradox for
`E(F_p) ≅ Z/N`. The abelian structure of the group is the blocking obstruction.

---

## Additive combinatorics (sum-product) and ECDLP factor bases

### Bourgain's sum-product theorem

The BGS paper cites, and uses as a tool, Bourgain's sum-product theorem for `F_p`:

**Theorem (Bourgain 2003, Bourgain-Katz-Tao 2004)**: For any set `A ⊆ F_p` with
`p^δ ≤ |A| ≤ p^{1-δ}` (for some `δ > 0`), there exists `ε = ε(δ) > 0` such that:

```
max( |A + A|, |A · A| ) ≥ |A|^{1+ε}
```

This says that a set `A` cannot simultaneously be "additively closed" and
"multiplicatively closed" (unless it is close to a subfield, which `F_p` doesn't have for
prime `p`).

### Can sum-product help the ECDLP factor base?

The ECDLP factor base `F ⊆ E(F_p)` consists of points `P = (x_P, y_P)` with
`x_P < B` (x-coordinate smaller than threshold `B`). In terms of `F_p`-arithmetic,
the x-coordinates form a set `A_x = {x_P : P ∈ F} ⊆ [0, B-1] ⊂ F_p` with
`|A_x| ≈ B` (Hasse theorem: roughly `B` points have x-coordinate below `B`).

**Question**: Does sum-product enlargement of `A_x` translate into more relations in
`E(F_p)`?

**Analysis**:

The sum-product theorem says `|A_x + A_x|` or `|A_x · A_x|` is superlinear in `|A_x|`.
However, the operation relevant to ECDLP is **elliptic curve addition** of *points*, not
addition of their x-coordinates. The x-coordinate of `P + Q` is:

```
x_{P+Q} = ((y_Q - y_P) / (x_Q - x_P))² - x_P - x_Q      [for P ≠ Q]
```

This is a rational function of `(x_P, y_P, x_Q, y_Q)` over `F_p`. It does not
correspond to `x_P + x_Q` or `x_P · x_Q` — the "set enlargement" from sum-product
applies to the x-coordinates under `F_p`-addition and multiplication, not to EC point
addition.

**The yield evidence**: BATCH-062/063 (EV-YIELD-e1adbf, EV-YIELD-ca4b02) measured the
actual Semaev decomposition yield for factor-base points and found yield = heuristic
prediction within measurement noise. There is no super-heuristic signal from any
arithmetic-combinatorial structure in the factor base. This is the empirical confirmation
that sum-product-type enlargement does not translate into improved ECDLP yield.

**Theoretical reason**: Semaev's decomposition probability depends on how often a random
point `Q ∈ E(F_p)` decomposes as `Q = P₁ + P₂ + ... + Pₘ` with each `Pᵢ ∈ F`. The
distribution of `Q` over `E(F_p)` is uniform (by assumption), and the factor-base
structure is fixed. The probability is:

```
Pr[Q ∈ F + F + ... + F (m times)] ≈ |F|^m · m! / N · (correction terms)
```

The dominant term is `|F|^m / N`, which is purely a counting quantity. Sum-product
enlargement affects `|A_x + A_x|` (the size of the sumset in `F_p`), but the EC point
addition `F + F` is a *different* map — it does not preserve the x-coordinate additive
structure. The number of EC points with x-coordinate in `A_x + A_x` is approximately
`|A_x + A_x|` (by Hasse), but the set `{P + Q : P, Q ∈ F}` (EC addition) has
x-coordinates given by the rational map above, not by `A_x + A_x`.

**Conclusion on sum-product**: Bourgain's sum-product theorem applies to `F_p`-arithmetic
(field addition and multiplication), not to elliptic curve group addition. The structural
expansion predicted by sum-product for `A_x` does not imply any expansion in the EC group
law sense. The yield measurements confirm this: EC addition of factor-base points gives
exactly heuristic yield, with no additive-combinatorics bonus.

### BGS thin-set distribution bounds

DEC-20260804-1bf901 proposes the "thin-set approach": find `S ⊆ E(F_p)` with
`|S| = N^α` and "above-random equidistribution properties". Let us examine what
this could mean.

A set `S ⊆ Z/N` equidistributes under the random walk on `Cay(Z/N, {G, -G})` with rate
determined by the character sums `Σ_{s ∈ S} exp(2πims/N)` for `m ≠ 0`. "Above-random"
equidistribution would mean these character sums are smaller than expected for a random
set of size `|S|`.

For a set `S` defined by x-coordinate smallness (`x_P < B`), the character sums of
interest are exponential sums over elliptic curve points with bounded x-coordinate.
These are studied by Shparlinski and others; the known bounds are of the form
`|Σ_{P ∈ F} e(m x_P/p)| ≤ C |F|^{1/2} p^{1/4}` (Weil-type). These bounds give
*square-root cancellation*, not above-random cancellation. Square-root cancellation means
the set looks random (same order as a random set of size `|F|`), not that it looks better.

**No thin-set candidate** of sub-birthday size has been identified whose character sums
cancel faster than square-root. The heuristic yield evidence from BATCH-062/063 is
consistent with this: EC points with small x-coordinate behave as a random subset of
`E(F_p)` for the purposes of Semaev decomposition.

---

## Can any BGS-type result give sub-birthday ECDLP?

### The birthday bound as a spectral lower bound

The birthday bound `Θ(√N)` for ECDLP comes from the collision argument on `Z/N`:

- Two walks of length `L` on `Z/N` collide (same group element) with probability
  `≈ L²/N`.
- Setting `L = Θ(√N)` gives constant collision probability.
- This argument is *tight* for group-theoretic algorithms (GGM lower bound).

The random walk perspective: the birthday paradox is equivalent to saying that a random
walk of length `L = o(√N)` on `Z/N` has visited fewer than `N^{1/2}` distinct elements.
For the walk to produce a collision in `L < √N` steps, the visited set of size `L` must
have a *double collision* — i.e., two points in the walk must be identical. For a random
walk on `Z/N` with a bounded generator, the probability that positions at times `i` and
`j` (`i < j`) collide is exactly `1/N` (since the walk step is uniform over a fixed
subset). The expected number of collisions in a walk of length `L` is `L²/(2N)`.

For this to exceed 1 (i.e., a collision to be likely), we need `L = Θ(√N)`.

**No expander structure changes this**: even if the walk mixed in `O(log N)` steps
(hypothetical), the *collision probability* between any two positions is still `1/N`.
Expander mixing says that after `O(log N)` steps the walk is close to the uniform
distribution — but a uniformly random point in `Z/N` collides with any fixed point with
probability `1/N`. The birthday bound `Θ(√N)` is a **birthday collision counting
argument**, not a mixing-time argument. Faster mixing does NOT reduce the collision
threshold.

**This is a crucial distinction**: BGS-type mixing bounds change the mixing time of a
random walk (how quickly it reaches near-uniform distribution), but the ECDLP collision
threshold is not about mixing time. It is about the number of *distinct values* the walk
takes before a collision. For a walk on a group of order `N`, this is `Θ(√N)` regardless
of mixing time.

Formally: Let `W = (W_0, W_1, ..., W_L)` be a walk on `Z/N`. Define the event
`Collision_L = {∃ i < j ≤ L : W_i = W_j}`. Then:

```
Pr[Collision_L] = 1 - ∏_{j=1}^{L} (1 - j/N) ≈ 1 - e^{-L²/(2N)}
```

This probability approaches 1 when `L ≈ √N`, and this formula holds for ANY walk on `Z/N`
where each step is independently uniform over a generating set, regardless of the size or
structure of the generating set. The expander property controls the *distribution* after
many steps, not the *collision probability* between specific pairs of steps.

**Conclusion**: Even if someone proved a BGS-type spectral gap for `E(F_p) ≅ Z/N` with
bounded generators (which is false, as shown above), it would NOT imply a sub-birthday
ECDLP algorithm. The birthday bound is a collision counting argument orthogonal to spectral
gap / mixing time.

### The Pollard-rho algorithm as a random walk

Pollard-rho already exploits the birthday paradox on `Z/N` optimally:
- Walks in `E(F_p)` of length `L = Θ(√N)` using Floyd's cycle-finding (or similar).
- Mixing of the walk is unnecessary — what matters is the number of distinct values visited.
- The walk uses a single generator (a pseudo-random function on `E(F_p)`), and the
  birthday collision threshold is `Θ(√N)` regardless of the walk's spectral properties.

BGS ideas cannot improve on Pollard-rho for `E(F_p)` because:
1. `E(F_p) ≅ Z/N` has no non-trivial spectral gap for bounded generators (established above).
2. Even if it did, the birthday collision threshold is `Θ(√N)` independent of mixing.

---

## Isogeny graph exception: Pizer graphs vs. volcano graphs

The analysis above applies to random walks on `E(F_p)` as an abelian group. There is a
separate question about random walks on **isogeny graphs** (graphs whose vertices are
elliptic curves and edges are isogenies). This is a different object.

### Supersingular isogeny graph (Pizer)

For **supersingular** elliptic curves over `F_p`, the `ℓ`-isogeny graph (for prime `ℓ`)
is an `(ℓ+1)`-regular graph on `≈ p/12` vertices. Pizer (1990) proved that this graph is
a **Ramanujan graph** — i.e., all non-trivial eigenvalues satisfy `|λ| ≤ 2√ℓ`, which is
the optimal expander bound. The mixing time of a random walk on the supersingular isogeny
graph is `O(log p)`.

This is the graph underlying the BGS/expander structure that is relevant to isogeny-based
cryptography (e.g., CSIDH security analysis). The spectral gap is:

```
1 - λ₁ ≥ 1 - 2√ℓ/(ℓ+1)  > 0   (independent of p)
```

**Relevance to prime-field ECDLP**: None direct. The supersingular isogeny graph connects
different curves over `F_p`, not different points on a single curve. A random walk on this
graph computes a random isogenous curve starting from `E`, which is a problem in the
*space of curves* not the *group of points* on `E`. The ECDLP asks about a specific
relationship between points on `E(F_p)`, not about paths in the isogeny graph.

To use the supersingular isogeny expander for ECDLP, one would need a mechanism that
converts a random isogeny walk (which mixes the *curve* in `O(log p)` steps) into
information about the *discrete logarithm* on the starting curve `E`. No such mechanism
is known, and it would require relating the isogeny graph structure (defined over the space
of j-invariants) to the group structure of `E(F_p)` (defined by points on a fixed `E`).
These are different mathematical objects.

### Ordinary isogeny graph (volcano structure)

For **ordinary** elliptic curves, the `3`-isogeny graph was the subject of BATCH-057/058
(EXP-OIFP-0ca0c9, H-OIFP-097d1a). The key structural finding from the red team report
(RT-20260804-620979):

- Ordinary 3-isogeny graphs have **volcano structure**: a "crater" cycle with trees
  hanging below each vertex.
- The volcano graph has **hierarchical bottlenecks** — to move between subtrees, the walk
  must pass through the crater, creating `O(h(D))` mixing time barriers (where `h(D)` is
  the class number, roughly `√p`).
- This is **NOT** a Ramanujan/expander graph. The spectral gap of the ordinary volcano
  graph satisfies:

    ```
    1 - λ₁(volcanic) = O(1/h(D)) = O(1/√p) → 0
    ```

  The mixing time is `Ω(h(D)) = Ω(√p)`, which is not `O(log p)`.

- The BATCH-057/058 experimental evidence (RT-20260804-620979, NOTE-3) shows collision
  steps scaling as `√(class_size)` — consistent with ordinary birthday on the class graph,
  not with expander mixing.

**Concrete structural reason for the non-expander property**: The `3`-isogeny graph for
ordinary curves has degree exactly 2 (not 4). The volcanic tree part of the graph has
no edges between leaves, creating isolated subtrees. The Cheeger constant of a tree is
`Ω(1/diameter)`, and the diameter of the volcano is `Θ(log h(D))` (the depth of the
tree), so the bottleneck is at the crater transition. The spectral gap of the volcano
graph goes to 0 with `h(D)`, precisely the opposite of an expander.

### Summary of isogeny graph comparison

| Graph | Spectral gap | Expander? | ECDLP relevance |
|-------|-------------|-----------|-----------------|
| Supersingular `ℓ`-isogeny (Pizer) | `Ω(1)` (Ramanujan) | YES | Unrelated to ECDLP point arithmetic |
| Ordinary volcano `ℓ`-isogeny | `O(1/√p)` | NO | Points on `E(F_p)` ≠ curves near `E` |
| `E(F_p) = Z/N` Cayley graph | `O(1/N²)` | NO | Direct ECDLP object, spectral gap negligible |

No isogeny graph structure provides a sub-birthday spectral mechanism for prime-field ECDLP.

---

## Assessment and verdict

### Q1: Does the BGS spectral gap apply to E(F_p)?

**No.** `E(F_p) ≅ Z/N` is abelian of prime order. The BGS theorem applies exclusively to
non-abelian groups (specifically, non-virtually-solvable groups). For any bounded
generating set `S` with `|S| = O(1)`, the Cayley graph `Cay(Z/N, S)` has spectral gap
`1 - λ₁ = Θ(1/N²) → 0`. The mixing time is `Θ(N²)`, which is far worse than even the
birthday bound `Θ(√N)`. BGS machinery does not engage for abelian groups.

### Q2: Can sum-product / additive combinatorics give sub-birthday ECDLP?

**No.** Bourgain's sum-product theorem applies to `F_p`-arithmetic (addition and
multiplication of scalars), not to elliptic curve group law (addition of points). The
x-coordinate of `P + Q` is a complicated rational function of `(x_P, x_Q)` that does
not correspond to `F_p`-addition or multiplication. The empirical yield measurements
(BATCH-062/063: EV-YIELD-e1adbf, EV-YIELD-ca4b02) confirm that no super-heuristic yield
arises from factor-base points with small x-coordinate. The additive-combinatorics bonus
that sum-product guarantees for `F_p`-sets does not transfer to the EC group law.

### Q3: Can any BGS-type result give sub-birthday ECDLP?

**No.** There are two independent reasons:

1. **No spectral gap exists** for `E(F_p) ≅ Z/N` with bounded generators (abelian
   obstruction, proved above). Any BGS analogue would require the group to be non-abelian.

2. **Spectral gap is irrelevant to birthday collision**: the birthday bound `Θ(√N)` is a
   collision-counting argument, not a mixing-time argument. Even hypothetically, if a
   walk on `Z/N` mixed in `O(log N)` steps (impossible with bounded generators, but
   hypothetical), the collision probability between any pair of walk positions would still
   be `1/N`, and a collision would still require `Θ(√N)` steps. The birthday threshold
   does not depend on spectral gap.

### On the BGS-thin-set proposal in DEC-20260804-1bf901

DEC-20260804-1bf901 (bgs_direction_rationale) proposed: "if a structured subset
`S ⊆ E(F_p)` equidistributes faster than `N/|S|` under random isomorphisms, it might
provide a structural advantage that exceeds the birthday bound." This proposal rests on
a misidentification of the relevant quantity:

- "Faster than N/|S| equidistribution" means the walk reaches near-uniform distribution
  in fewer than `N/|S|` steps. This is a *mixing time* property.
- The birthday bound is a *collision counting* property: it depends on `|S| × |S| / N`,
  not on mixing time.
- For `|S| = N^α` and a walk mixing in `T` steps (`T << N/|S| = N^{1-α}`), the walk
  still requires `Θ(√N)` steps for a collision. The faster mixing means the walk samples
  near-uniformly from `E(F_p)` after `T` steps — but two independent near-uniform samples
  from `E(F_p)` collide with probability `1/N`, regardless of how they were generated.

The proposal conflates mixing efficiency (how quickly the walk explores `E(F_p)`) with
collision efficiency (how many steps until two walk positions agree). These are separate
phenomena. BGS addresses mixing, not collisions.

### Verdict: BLOCKED by abelian structure

The BGS/thin-set direction is **blocked** by a combination of two independent obstructions:

**Obstruction 1 (Structural incompatibility)**: The BGS spectral gap theorem requires
non-abelian, non-virtually-solvable groups. `E(F_p) ≅ Z/N` is abelian. No BGS spectral
gap exists for `Z/N` with bounded generators. The mixing time is `Θ(N²)` — two orders
of magnitude worse than birthday.

**Obstruction 2 (Irrelevance of spectral gap to birthday)**: Even if one could somehow
establish an `Ω(1)` spectral gap for `Z/N` (impossible with bounded generators, but
hypothetical), it would not reduce the birthday collision threshold below `Θ(√N)`. The
birthday bound is group-size-dependent, not mixing-time-dependent.

The correct characterization for the DEC-20260804-1bf901 rationale: the BGS analogy for
ECDLP is a false analogy. BGS works for CSIDH-type problems (random walk on the
*supersingular isogeny graph*, which is non-abelian in its action) but not for
prime-field ECDLP (random walk on `E(F_p) ≅ Z/N`, which is the simplest abelian group).

**Named obstruction**: *Abelian spectral gap obstruction* — For abelian groups of prime
order `N`, no bounded-generator random walk has spectral gap `Ω(1)`, and even an
`Ω(1)` spectral gap would not reduce the birthday collision threshold below `Θ(N^{1/2})`.

**Research disposition**: The BGS/thin-set direction should be recorded as **closed at
the current scope** with this named obstruction. No minimal discriminating experiment is
required; the obstruction is mathematical (not empirical) and does not depend on toy-scale
measurements. The two obstructions above are provable from standard Fourier analysis on
abelian groups (Obstruction 1) and the birthday paradox counting argument (Obstruction 2).

**What remains open (narrow successor)**: The Pizer supersingular isogeny graph is a
genuine BGS-type expander and gives `O(log p)` mixing for walks on the *space of curves*.
Whether any connection exists between this structure and the *discrete logarithm on
points of a fixed curve* is an open question, but it would require an entirely new
mechanism connecting these two different mathematical objects. This is not the BGS
direction as proposed — it would be a new direction requiring its own proposal and
mechanism statement.

---

## References

- Bourgain-Gamburd 2008: "Uniform expansion bounds for Cayley graphs of SL_2(F_p)"
- Bourgain-Gamburd-Sarnak 2010: "Affine linear sieve, expanders, and sum-product"
- Bourgain 2003, Bourgain-Katz-Tao 2004: Sum-product theorem for F_p
- Pizer 1990: "Ramanujan graphs and Hecke operators"
- EXP-OIFP-0ca0c9 / RT-20260804-620979: Ordinary isogeny volcano structure (BATCH-057/058)
- EV-YIELD-e1adbf, EV-YIELD-ca4b02: Semaev yield = heuristic (BATCH-062/063)
- DEC-20260804-1bf901: BGS direction admission decision
- BATCH-065/TASK-20260804-068: Structural ingredient search, Wesolowski pattern analysis
