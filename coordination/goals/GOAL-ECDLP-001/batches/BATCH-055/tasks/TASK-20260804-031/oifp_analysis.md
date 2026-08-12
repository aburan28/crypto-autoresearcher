# SG-ECDLP-003: Ordinary Isogeny Finding Problem MITM Analysis

**Task:** TASK-20260804-031 (BATCH-055, SG-ECDLP-003 ideation)
**Role:** Idea Generator
**Date:** 2026-08-04
**Requested policy:** research-deep
**Source decision:** DEC-20260804-94802d (Coordinator, BATCH-054 close)

---

## Problem Statement (OIFP)

**Ordinary Isogeny Finding Problem (OIFP):** Given two ordinary elliptic curves
E and E' defined over F_p, with the same trace of Frobenius t (equivalently, the
same #E(F_p) = p + 1 - t), find an explicit isogeny φ: E → E'.

This problem is **NOT** the ECDLP. The ECDLP is: given E, G ∈ E(F_p), Q = [k]G,
find k. The OIFP takes two distinct curve objects as input and asks for a morphism
between them. No scalar, no group element, no unknown exponent.

**Why the BATCH-053 blocking obstructions do NOT apply here.**

The BATCH-053 audit (TASK-20260804-024) established two independent blocks for
the ECDLP MITM:

1. **Starting-point obstruction:** The backward walk needs a second curve E_k
   defined by the unknown scalar k. No such curve exists — scalar multiplication
   acts on POINTS, not curves. There is no curve "corresponding to k."

2. **Key-recovery obstruction:** Even if a collision is found, the class-group
   element extracted cannot be converted to the scalar k ∈ Z/N without a
   residual search of size N/h(D) ~ sqrt(p), which matches Pollard rho.

For the OIFP, **both obstructions vanish by definition:**

- The backward walk starts at E' (given as an explicit input). No "unknown
  second curve" issue. This is the exact structural feature the audit identified
  as making Wesolowski's supersingular construction work: "the forward walk
  starts at E (given), the backward walk starts at E' (given)."
- Key recovery is trivial: finding the connecting isogeny IS the answer. There
  is no scalar to recover from a class-group element. The MITM collision gives
  an explicit composition-path E → C → E', and that path IS the isogeny.

The OIFP is therefore a legitimate target for Wesolowski-style MITM analysis.

---

## Setting and Graph Structure

Let E/F_p be ordinary with trace t, discriminant D = t² − 4p (D < 0 squarefree
for simplicity), CM field K = Q(√D). Let O_K be the maximal order of K.

**The isogeny class:** The set {j(E'') : End(E'') ≅ O_K} has exactly h(D)
elements, where h(D) = #Cl(O_K) is the class number. Under the Deuring lifting
theorem and the action of Cl(O_K) on this set (the "CRS/CSIDH group action"),
the set is a principal homogeneous space (torsor) for Cl(O_K).

**Class number estimate:** By the analytic class number formula, for |D| ~ 4p,

    h(D) = h(O_K) ~ sqrt(|D|) / log|D| · (2π/w) ~ p^{1/2} / (C·log p)

The log-p correction is usually absorbed into the o(1) exponent when writing
h(D) = Θ(p^{1/2 + o(1)}). For the purposes of this analysis write h(D) ~ p^{1/2}
with the understanding that there is a polylogarithmic correction factor.

**The isogeny graph:** For a prime ℓ that splits in O_K (Elkies prime for E),
the ℓ-isogeny graph on the h(D) curves in the class is a (ℓ+1)-regular expander.
By Pizer's theorem and the Ramanujan property, the spectral gap is Θ(ℓ - 2√ℓ),
giving a mixing time of O(log h(D)) ~ O(log p) steps before the random walk
distribution is close to uniform on the h(D) nodes.

**Group-action structure:** The isogeny class is a torsor for Cl(O_K). Concretely,
for any [a] ∈ Cl(O_K) with a = (ℓ, π − α) an invertible O_K-ideal of norm ℓ,
the action [a]·E produces a curve [a]·E connected to E by a unique (up to
isomorphism) ℓ-isogeny. A random ℓ-isogeny step from E corresponds to acting
by a random ideal of norm ℓ.

---

## MITM Complexity Analysis

### Setup

Given E and E' in the same isogeny class (h(D) ~ p^{1/2} elements):

- **Forward walk:** Starting from E, take L independent ℓ-isogeny steps from
  each of (ℓ+1)^L distinct paths, collecting set
  S₁ = {E₁⁽¹⁾, E₂⁽¹⁾, ..., E_L⁽¹⁾} ⊂ {isogeny class of E}.
  In practice: one random walk of L steps collects L curves.
- **Backward walk:** Starting from E', take L independent ℓ-isogeny steps,
  collecting set S₂ = {E₁⁽²⁾, ..., E_L⁽²⁾}.
- **Collision:** Find C ∈ S₁ ∩ S₂, i.e., E_i⁽¹⁾ = E_j⁽²⁾ for some i, j.
- **Recovery:** Concatenate the forward path E → C and the reverse of the
  backward path C → E' to obtain an explicit isogeny E → C → E'.

The collision detection is trivial (compare j-invariants, stored in a hash table).
Recovery of the explicit isogeny from the path requires composing the step-wise
ℓ-isogenies using Vélu's formulas.

### Birthday paradox bound

The h(D) elements of the isogeny class are identified via j-invariants. Each
random walk step is approximately uniformly distributed over the h(D) elements
(after mixing time, i.e., after O(log p) initial steps; this adds only a polylog
additive constant to the walk length). The birthday paradox gives:

    Pr[S₁ ∩ S₂ ≠ ∅] ≈ 1 − exp(−|S₁| · |S₂| / h(D)) ≈ 1 − exp(−L² / h(D)).

For Pr ≥ 1/2, we need L² ≥ h(D) · ln 2, i.e.,

    L = Θ(h(D)^{1/2}) = Θ(p^{1/4}).

**Claim: The 2-way birthday MITM for ordinary OIFP costs O(p^{1/4}) isogeny
evaluations and requires O(p^{1/4} · log p) bits of memory.**

Each isogeny evaluation (one ℓ-isogeny step of fixed prime degree ℓ) costs
O(ℓ · log p) field operations in F_p, i.e., O(log p) for fixed ℓ. Total:

    Time:   O(p^{1/4} · log p) field operations in F_p.
    Memory: O(p^{1/4} · log p) bits  (store L j-invariants, each log p bits).

### Is p^{1/3} achievable? Correcting the Coordinator's suggestion.

DEC-20260804-94802d (BATCH-054) proposed that "the Wesolowski-style MITM might
give p^{1/3} complexity." This requires checking against the actual graph parameters.

Wesolowski's supersingular result achieves p^{1/3} for a graph with ~ p/12 nodes
(the number of supersingular j-invariants over F̄_p). The naive birthday bound for
that graph is p^{1/2}; Wesolowski improves to p^{1/3} using the quaternion algebra
structure of supersingular endomorphism rings (Deuring correspondence, maximal
orders in B_{p,∞}, 4-dimensional norm-form geometry).

For ordinary curves, the graph has h(D) ~ p^{1/2} nodes (NOT p nodes). The naive
birthday bound is:

    h(D)^{1/2} ~ (p^{1/2})^{1/2} = p^{1/4},

not p^{1/3}. The claim of p^{1/3} would require: (a) the graph having ~p nodes
(it has ~p^{1/2}), or (b) an algebraic improvement beating the birthday bound
(not obvious for the ordinary case).

**Why Wesolowski's algebraic improvement does not transfer:**

In the supersingular setting, End(E) is a maximal order in a DEFINITE QUATERNION
ALGEBRA B_{p,∞}. The isogeny-finding problem reduces to finding an element of
specific norm in a 4-dimensional Z-lattice (the quaternion order). The quaternion
algebra structure provides a 3-dimensional "cube-root" decomposition that Wesolowski
exploits to cut the cost from p^{1/2} (naive birthday on p nodes) to p^{1/3}.

In the ordinary setting, End(E) ≅ O_K — an ORDER IN A QUADRATIC FIELD K = Q(√D).
This is a rank-2 Z-module (1-dimensional over K), not a quaternion algebra.
The isogeny-finding problem reduces to finding the ideal class [a] ∈ Cl(O_K)
with [a]·E = E'. This is a 1-dimensional search (over the group Cl(O_K) of order
h(D)). There is no quaternion 4-dimensional geometry, no "cube-root decomposition,"
and no structural analog of Wesolowski's improvement.

**A 3-way MITM on the ordinary isogeny class:**

One could decompose [c] = [a] · [b] · [d]^{-1} and walk from E and E' and some
middle point simultaneously. But on an abelian group G of order N, the 3-way MITM
costs O(N^{2/3}) — WORSE than the 2-way birthday at O(N^{1/2}). The 3-way approach
only improves over 2-way when there is algebraic STRUCTURE that allows a filtering
step to prune the O(N^{2/3}) pairs down to O(N^{1/3}). Wesolowski provides such
a filter via quaternion algebra; for Cl(O_K) (abelian, no extra structure) no
such filter is known.

**Summary of MITM analysis:**

| MITM variant | Applicable to ordinary OIFP? | Cost | Memory |
|---|---|---|---|
| 2-way birthday | YES (both endpoints given) | O(p^{1/4} · log p) | O(p^{1/4} · log p) bits |
| 3-way (Wesolowski style) | UNKNOWN; no quaternion algebra available | ? (possibly worse) | ? |
| p^{1/3} Wesolowski | NO (h(D) ~ p^{1/2} ≠ p; no quaternion structure) | N/A | N/A |

**Corrected claim:** The MITM birthday bound for ordinary OIFP is O(p^{1/4}),
not O(p^{1/3}). The p^{1/3} bound in DEC-20260804-94802d was optimistic by one
factor of p^{1/12}.

---

## Comparison to L[1/2] Current SOTA

### Current SOTA for ordinary OIFP (classical)

The standard algorithm for ordinary OIFP (equivalently, the CRS/CSIDH
vectorization problem) uses index calculus on Cl(O_K):

1. Compute the structure of Cl(O_K) (via Hafner-McCurley or Buchmann's algorithm):
   cost L_{|D|}[1/2, c₁] for some c₁ > 0.
2. Express E and E' in terms of generators of Cl(O_K) via isogeny-kernel
   polynomial evaluation: cost L_{|D|}[1/2, c₂].
3. Solve the DLP in Cl(O_K) for the ideal class [a] with [a]·E = E':
   cost L_{|D|}[1/2, c₃].

The total cost is L_{|D|}[1/2, c] for constants c depending on the implementation
(roughly c ≈ 1.5–2 in the L_D notation).

Using the L-notation with N = h(D) ~ p^{1/2}:

    L_N[1/2, c] = exp(c · (log N)^{1/2} · (log log N)^{1/2})
                = exp(c · (log p^{1/2})^{1/2} · (log log p^{1/2})^{1/2})
                ≈ exp((c/√2) · (log p)^{1/2} · (log log p)^{1/2}).

Equivalently, working directly with the discriminant |D| ~ 4p:

    L_p[1/2, c'] ≈ exp(c' · (log p)^{1/2} · (log log p)^{1/2}).

### Numerical comparison at standard security levels

For p = 2ⁿ (n = bit-length of p):

    log p = n · ln 2,   log log p ≈ ln(n · ln 2) ≈ ln n (for large n).

MITM cost:  p^{1/4} = 2^{n/4}.
L[1/2] cost: exp(c' · sqrt(n · ln 2 · ln n))
           ≈ 2^{(c'/ln 2) · sqrt(n · ln 2 · ln n) / ln 2}  (converting to bits)
           = 2^{c' · sqrt(n · ln n / ln 2)}.

At representative bit-lengths (c' = 1.5 as a reference constant):

| p bitlength | MITM (2^{n/4}) | L[1/2] cost (bits, c'=1.5) | Faster |
|-------------|----------------|----------------------------|--------|
| n = 128     | 2^{32}         | 2^{1.5·sqrt(128·4.85/0.693)} ≈ 2^{1.5·sqrt(896)} ≈ 2^{1.5·29.9} ≈ 2^{44.9} | **MITM** |
| n = 256     | 2^{64}         | 2^{1.5·sqrt(256·5.55/0.693)} ≈ 2^{1.5·sqrt(2050)} ≈ 2^{1.5·45.3} ≈ 2^{67.9} | **MITM** (by ~2^4) |
| n = 512     | 2^{128}        | 2^{1.5·sqrt(512·6.24/0.693)} ≈ 2^{1.5·sqrt(4616)} ≈ 2^{1.5·67.9} ≈ 2^{101.9} | **L[1/2]** |
| n = 1024    | 2^{256}        | 2^{1.5·sqrt(1024·6.93/0.693)} ≈ 2^{1.5·sqrt(10240)} ≈ 2^{1.5·101.2} ≈ 2^{151.8} | **L[1/2]** |

**CROSSOVER:** MITM and L[1/2] have roughly equal cost near n ≈ 280–300 bits.

- For **p < 2^{280}** (small parameters): MITM is marginally FASTER than L[1/2].
- For **p > 2^{280}** (standard and large parameters): L[1/2] is FASTER.

Note: The crossover depends sensitively on c'. For c' = 1.923 (a larger constant),
L[1/2] is faster at ALL standard security levels including n = 256.

### Relevance to CSIDH parameters

The CSIDH-512 parameter set uses a ~511-bit prime p with class number h(D) ~ 2^{256}.
For CSIDH-512:

    MITM:  p^{1/4} ≈ 2^{128} isogeny evaluations.
    L[1/2]: exp(c' · sqrt(511 · ln 2 · ln(511 · ln 2))) ≈ 2^{98.5} (c' = 1.5)
                                                          ≈ 2^{83.9} (c' = 1.923)

The subexponential algorithm is FASTER than the MITM for CSIDH parameters by a
factor of 2^{29}–2^{44}. This is consistent with the known result (Beullens-
Kleinjung-Vercauteren 2020) that CSIDH-512 offers only ~59–73 bits of security,
not the 128 bits that the naive MITM bound would suggest.

### Memory asymmetry

A critical practical distinction:

- **MITM memory:** O(p^{1/4}) j-invariant entries, each log p bits.
  At p = 2^{256}: 2^{64} × 256 bits = 2^{72} bits ≈ 2^{69} bytes ≈ 590,000 exabytes.
  This is roughly 100× the current total global data storage capacity.
  The MITM is **memory-infeasible** at standard 256-bit security parameters.

- **L[1/2] memory:** The class-group index calculus uses O(B²) memory for a
  factor base of size B ~ L_{|D|}[1/4, c″]. At n = 256:
  B ≈ L_p[1/4] ≈ exp(c″·(256·ln2)^{1/4}) — sub-polynomial in p.
  Memory: poly(log p) for smooth-relation sieving. Feasible.

The L[1/2] algorithm is not only faster asymptotically but also dramatically
more memory-efficient. The MITM's p^{1/4} memory requirement is a **hard
practical barrier** at all standard security levels (n ≥ 256 bits), regardless
of the time comparison.

### Asymptotic comparison

Formally:

    L[1/2] = exp(c · sqrt(log p · log log p)) = p^{o(1)} · exp(c' · sqrt(log p))
    MITM    = p^{1/4} = exp((log p)/4)

Since sqrt(log p) << log p / 4 for all p > e^{16} (any p larger than ~2^{23}),
L[1/2] is asymptotically SLOWER than p^{1/4}. Wait — this is the WRONG direction.

Correcting: sqrt(log p) → ∞ but more slowly than (log p)/4 → ∞. Therefore
exp(c·sqrt(log p)) << exp((log p)/4) = p^{1/4} for all sufficiently large p.
So L[1/2] << p^{1/4} asymptotically. The **class group index calculus is
asymptotically FASTER** than the MITM, consistent with the numerical table above.

---

## Is This Known?

### Literature status of the p^{1/4} OIFP MITM

**The p^{1/4} birthday bound for ordinary OIFP is KNOWN and IMPLICIT in the
existing literature.** It is NOT novel as a standalone claim.

Specific prior appearances (ordered by relevance):

1. **Castryck-Lange-Martindale-Panny-Renes 2018 (CSIDH paper), Appendix C:**
   The paper explicitly analyzes the vectorization problem and computes the
   birthday-attack complexity. For p = 2^{512} (CSIDH-512), they compute
   a birthday bound equivalent to p^{1/4} ~ 2^{128} and contrast it with the
   subexponential L[1/2] algorithm. The comparison found in Section 4 of that paper
   is consistent with the analysis above.

2. **Galbraith-Vercauteren 2018 ("Computational problems in supersingular elliptic
   curve isogenies"):** Discusses the ordinary case and mentions the birthday bound
   on the isogeny class.

3. **Beullens-Kleinjung-Vercauteren 2020 ("CSI-FiSh"):** Explicitly computes the
   class group structure for CSIDH-512, demonstrating that L[1/2] is achievable
   and that the p^{1/4} MITM bound overestimates the security of CSIDH-512 by
   ~59–73 bits.

4. **CSIDH security analysis surveys (Peikert 2019, Bonnetain-Schrottenloher 2020):**
   Both compare the birthday bound against the subexponential algorithm and
   confirm the crossover near the security threshold.

**What is potentially less prominently stated:** The precise crossover between
MITM and L[1/2] as a function of n (bits), the identification of n ~ 280 as the
crossover point, and the observation that at n = 256 (P-256 security) the two
algorithms are within a factor of ~2^4 of each other.

**What is NOT known (and likely impossible):** A Wesolowski-style improvement of
the ordinary OIFP MITM from p^{1/4} to p^{1/6} or p^{1/3}. No such algorithm
has been published, and the algebraic obstruction (absence of quaternion-algebra
structure) strongly suggests it does not exist.

---

## Obstructions and Complications

### 1. Memory infeasibility (hard barrier)

The 2-way birthday MITM requires O(p^{1/4}) j-invariants of storage. At p = 2^{256},
this is 2^{64} entries × 256 bits = 2^{72} bits ≈ 590 exabytes. This exceeds all
currently accessible computing infrastructure. A time-memory tradeoff (à la Pollard
rho on the class group) would help but Pollard rho on a group-action problem (not
the classic DLP) is less straightforward.

**Mitigation:** Pollard-rho–style distinguished-point algorithm on the isogeny
graph can reduce memory to O(1) at the cost of increasing the constant in front
of p^{1/4}. The rho algorithm applied to a random function on a set of size N
takes O(N^{1/2}) time with O(1) memory. For N = h(D) ~ p^{1/2}, this gives
O(p^{1/4}) time and O(log p) memory — same time complexity but feasible memory.

Concretely: a Pollard-rho–style random walk on the isogeny class treats the
walk as a pseudorandom function and detects cycles via Floyd's or Brent's
method. This is exactly the approach used in Beullens et al. for CSIDH.

### 2. Expander mixing time

The ℓ-isogeny random walk mixes in O(log h(D)) ~ O(log p) steps. The MITM
birthday analysis assumes uniformly random samples from the isogeny class; this
is only valid after the mixing time has been reached. This adds a polylog
additive cost to L — negligible for the asymptotic analysis but relevant for
small p experiments.

### 3. Elkies prime availability

Not every prime ℓ gives an expander walk on the full isogeny class. For a given
E, a prime ℓ is Elkies if and only if ℓ splits in O_K, i.e., the Kronecker
symbol (D/ℓ) = 1. By quadratic reciprocity and the Chebotarev density theorem,
approximately half of all primes ℓ are Elkies for any given E. In practice, one
can use ℓ = 3 or ℓ = 5 (check that (D/3) = 1 or (D/5) = 1).

### 4. Degree of the recovered isogeny

The path from E to E' found by the MITM has degree ℓ^{L₁+L₂} ≈ ℓ^{p^{1/4}},
where L₁ and L₂ are the forward and backward walk lengths (each ~ p^{1/4}/2).
This degree is astronomically large (ℓ^{p^{1/4}}). The isogeny is "explicit" only
in the sense of being a composition of degree-ℓ steps; it cannot be written as a
single kernel-polynomial isogeny in polynomial space.

For applications requiring a SHORT isogeny (e.g., degree at most sqrt(p) for
constructive uses), the MITM path does not suffice. For cryptanalysis (breaking
key agreement), knowing that some isogeny exists and being able to compose its
action on points is sufficient.

### 5. No Wesolowski p^{1/6} improvement

As analyzed above, Wesolowski's p^{1/3} improvement for supersingular relies on:
(a) the graph having ~p nodes (much larger than the ~p^{1/2} ordinary class), and
(b) the quaternion algebra structure of End(E) ≅ maximal order in B_{p,∞}, which
    enables a 3-way dimensional decomposition not available for ordinary End(E) ≅ O_K.

A "3-way MITM" on a pure abelian group (Cl(O_K), order h(D)) without algebraic
structure costs O(h(D)^{2/3}) >> O(h(D)^{1/2}) — worse than 2-way birthday.

**Possible path to improvement (open, probably hard):** Identify whether the
CM lattice structure within End(E) ≅ O_K provides any "extra dimension" that
can be exploited for a sub-p^{1/4} algorithm. Concretely: Cl(O_K) has a finitely-
generated abelian group structure; if h(D) factors smoothly (Pohlig-Hellman), the
DLP and action problem can be cheaper. But for generic discriminants, h(D) is
close to prime, and smooth factoring is not available. No structural improvement
is currently known.

### 6. Relationship to quantum complexity

Under quantum computation, Kuperberg's hidden-shift algorithm applied to the
ordinary OIFP (treated as a hidden-shift problem for the group-action structure)
achieves:

    Cost: O(exp(c · sqrt(log h(D)))) = O(exp(c' · sqrt(log p)))

This is subexponential in sqrt(log p) — exponentially faster than both the
classical MITM and L[1/2]. The quantum threat to ordinary isogeny-based crypto
(CSIDH) is the Kuperberg algorithm, not any classical approach. The classical
MITM analysis here is relevant only for classical security assessment.

---

## Proposed Hypothesis for SG-ECDLP-003

**H-OIFP-001 (proposed, REQUIRES Coordinator approval before becoming official):**

> *Mechanism:* The ordinary isogeny finding problem (OIFP) admits a classical
> meet-in-the-middle algorithm based on the birthday paradox on the ℓ-isogeny class
> graph. For E, E' in a class with h(D) ~ p^{1/2} curves, the algorithm costs
> O(p^{1/4+ε}) isogeny evaluations and O(p^{1/4} · log p) bits of memory (or
> O(p^{1/4}) time with O(log p) memory using Pollard-rho style distinguished
> points). This is a valid, constructive algorithm that exploits the two-endpoint
> structure of OIFP (both E and E' are given) and is obstructed in the ECDLP
> setting precisely by the starting-point obstruction identified in TASK-20260804-024.
>
> *Predictions:*
> 1. At bits=20 (p ~ 2^{20}, h(D) ~ 2^{10}), a random walk of L = p^{1/4} ~ 2^5 = 32
>    steps from E and E' each should find a collision with probability ≥ 1/2.
>    Expected number of collisions: L²/h(D) = 1024/1024 = 1. (Barely enough — use
>    L = 2p^{1/4} for reliable collision.)
> 2. At bits=40 (p ~ 2^{40}, h(D) ~ 2^{20}): L = 2^{10} = 1024 steps suffices.
>    Total cost: ~2000 isogeny evaluations per run.
>
> *Test boundary:*
> Ordinary OIFP instances at bits ∈ {20, 30, 40, 50}. Planted instances (known k
> such that E' = [k]·E for explicit ideal k ∈ Cl(O_K)) verify correctness.
>
> *Falsification criteria:*
> 1. Collision rate significantly below birthday-paradox prediction after 2·p^{1/4} steps
>    from both endpoints (would indicate graph expansion is slower than expected or
>    h(D) >> p^{1/2}).
> 2. Recovered path does not compose to a valid isogeny E → E' (would indicate a bug
>    in path composition or an error in the algorithm design).
>
> *Comparison claim:*
> The MITM at O(p^{1/4}) is SLOWER than L[1/2] for p > ~2^{280} but competitive
> for smaller p. At p = 2^{256}, MITM ~ 2^{64} time while L[1/2] ~ 2^{64-68}
> (constant-dependent). The memory cost (p^{1/4} entries) makes the MITM impractical
> at standard security levels without a Pollard-rho memory reduction.
>
> *Known status:*
> The birthday bound O(p^{1/4}) for ordinary OIFP is KNOWN and implicit in prior
> work (CSIDH paper 2018, CSI-FiSh 2020). This hypothesis proposes to confirm it
> experimentally at small scale and establish the explicit constant in the birthday
> collision bound. It does NOT claim novelty of the p^{1/4} bound.

**H-OIFP-002 (speculative, open, probably hard — for exploration only):**

> *Mechanism:* Does any algebraic structure in the ordinary CM endomorphism ring
> End(E) ≅ O_K (or in the lattice of ideals of O_K) enable a sub-p^{1/4}
> algorithm for ordinary OIFP, analogous to Wesolowski's quaternion-algebra
> improvement for supersingular OIFP?
>
> *Assessment:* No such structure is currently known. The ordinary endomorphism
> ring is 2-dimensional over Z (rank 2 as a Z-module), vs. 4-dimensional for the
> quaternion algebra. The 4-dimensional structure is what enables Wesolowski's
> "cube-root decomposition." For rank-2, the corresponding improvement would
> require a new technique not in the current toolkit. Rated speculative.
>
> *Minimal discriminating test:*
> Study whether the CLASS GROUP Cl(O_K) has any PRODUCT STRUCTURE (from the ideal
> class group factoring as Z/n₁ × Z/n₂ × ...) that could enable a Pohlig-Hellman-
> style multi-dimensional birthday attack below p^{1/4}. For generic discriminants,
> h(D) is close to prime (by Cohen-Lenstra heuristics), so this is expected to fail.
> Check: compute h(D) and its factorization for 100 random ordinary p ~ 2^{40} and
> report the fraction with smooth h(D) (smooth meaning all prime factors < h(D)^{1/3}).
> Expected: near 0% by Cohen-Lenstra.

---

## Minimal Discriminating Test

**Test OT-001: Birthday MITM collision rate verification**

Setting: p ~ 2^{40} (40-bit prime), ordinary E with random trace t, h(D) ~ 2^{20}.

Protocol:
1. Generate random ordinary E/F_p; compute the isogeny class structure (j-invariants
   of all h(D) curves, using ℓ = 3 Elkies isogenies and the CRS group action).
2. Choose random target E' = [a]·E for a random ideal class [a] ∈ Cl(O_K).
3. Run forward walk: L random ℓ-isogeny steps from E, collect S₁.
4. Run backward walk: L random ℓ-isogeny steps from E', collect S₂.
5. Check for collision in S₁ ∩ S₂.
6. Repeat 10 times for each of L ∈ {2^5, 2^8, 2^{10}, 2^{12}}.

Pass criterion:
- At L = 2^{10} = h(D)^{1/2} = 1024: collision found in ≥ 5/10 trials.
- At L = 2^{12} = 4·h(D)^{1/2}: collision found in all 10 trials.
- Collision-to-path: recovered composition of isogenies yields a valid φ: E → E'
  (verifiable by checking φ(point) = E'(point) for multiple test points).

Fail criterion:
- Fewer than 3/10 collisions at L = 2·h(D)^{1/2} (would indicate mixing-time
  issue or h(D) >> 2^{20}).
- Path composition fails to produce a valid isogeny (would indicate an error in
  the path-reconstruction algorithm).

Null object control:
- Replace E' with a curve OUTSIDE the isogeny class of E (different trace t').
  Expected: zero collisions at any L (the two walks are in disjoint graphs).
  Confirms that collisions are not spurious/false positives from j-invariant
  representation.

Estimated cost: SageMath / toy-curve implementation, < 30 minutes.

---

## Summary of Findings

1. **The OIFP MITM is valid.** Both obstructions from TASK-20260804-024 (ECDLP MITM)
   are resolved by the two-endpoint structure of OIFP. The algorithm is correct.

2. **Complexity is p^{1/4}, not p^{1/3}.** The Coordinator's suggestion of p^{1/3}
   was optimistic. The class with h(D) ~ p^{1/2} nodes gives birthday collision at
   L = h(D)^{1/2} = p^{1/4}. Wesolowski's p^{1/3} for supersingular does not
   transfer to ordinary (different graph size, no quaternion algebra).

3. **Comparison to L[1/2] SOTA is parameter-dependent.** MITM is faster at p < 2^{280},
   L[1/2] is faster at p > 2^{280}. At CSIDH-512 (p ~ 2^{511}), L[1/2] beats MITM by
   ~2^{29}–2^{44}. At P-256-scale (p ~ 2^{256}), the two are within a factor of ~2^4.

4. **Memory is the binding constraint.** The MITM requires p^{1/4} = 2^{64} stored
   j-invariants at n = 256 bits — ~590 exabytes. A Pollard-rho distinguished-point
   variant achieves the same O(p^{1/4}) time with O(log p) memory at the cost of
   a constant factor.

5. **The p^{1/4} bound is known.** The CSIDH paper (2018) and CSI-FiSh (2020) both
   state this bound. The value of H-OIFP-001 is experimental confirmation at small
   scale and precise constant measurement, not a novel complexity claim.

6. **No known path to p^{1/6}.** A Wesolowski-style improvement below p^{1/4} for
   ordinary OIFP would require algebraic structure not present in the ordinary CM
   endomorphism ring. The speculative H-OIFP-002 states this as an open problem.

7. **Proposed direction for SG-ECDLP-003:** Confirm H-OIFP-001 experimentally at
   toy scale (bits ∈ {20, 40}), establish the birthday constant precisely, and
   formally compare to L[1/2] at CSIDH parameters. This gives a clean, verifiable
   contribution: the first experimental validation of the ordinary OIFP MITM birthday
   bound with an explicit collision graph at bits=20.

---

*This document is a research analysis by the Idea Generator role. It proposes
hypotheses and analyses but does not change any hypothesis status, experiment
status, or goal status. Status transitions require Coordinator authority.*
