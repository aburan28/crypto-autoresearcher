# DDH Conditional Proof Attempt for H-PSEUDO

**Task:** TASK-20260804-100  
**Goal:** GOAL-ECDLP-001  
**Batch:** BATCH-080  
**Analyst role:** Mathematical analyst  
**Source decision:** DEC-20260804-0f010f (BATCH-079)

---

## Setup

**H-PSEUDO (H-PSEUDO-83817b):** For F = small-x factor base in E(F_p),

    max_{k≠0} |Σ_{P∈F} e^{2πi k·DL_G(P)/N}| ≤ C(p) · √B

where B = |F|, N = |E(F_p)|, DL_G(P) ∈ Z/N is the discrete log of P base G, and
C(p) ~ p^{0.079} empirically (BATCH-079: C = 4.32 at p = 100003, 5-point fit).

**DDH assumption (standard form):** For any PPT adversary A,

    |Pr[A(G, [a]G, [b]G, [ab]G) = 1] - Pr[A(G, [a]G, [b]G, [c]G) = 1]| = negl(log p)

with a, b, c uniform in Z/N and G a generator of E(F_p). Equivalently: given [k]G,
the scalar k is computationally indistinguishable from uniform in Z/N.

**The question:** Does DDH hardness on E(F_p) imply H-PSEUDO?

---

## Q1: Does standard DDH imply H-PSEUDO?

**No.** The argument is structural and does not depend on the specific curve.

DDH is a *computational* assumption: it asserts that no PPT algorithm, given an elliptic
curve group element [k]G, can distinguish k from a uniform element of Z/N with non-negligible
advantage. This is a statement about the *hardness of computation*.

H-PSEUDO is an *information-theoretic* property: it asserts that a specific fixed real number

    S_k(F) := Σ_{P∈F} e^{2πi k·DL_G(P)/N}

satisfies |S_k(F)| ≤ C(p) · √B for every non-zero k ∈ Z/N. The set F and the generator G
are fixed; the DL values {DL_G(P) : P ∈ F} are specific integers in Z/N — they are not
random variables from any perspective. S_k(F) is a fixed complex number that either satisfies
the bound or does not, regardless of what any algorithm can compute.

**Computational assumptions cannot imply information-theoretic bounds** — they are orthogonal
kinds of statement. A function can be computationally hard to invert on any input while still
having highly structured (non-uniform) values on structured inputs. For a concrete illustration:
one could in principle have a curve E where DL_G(P) = (x(P) mod N) for all P (an entirely
artificial but illustrative map), making S_k huge while ECDLP might still be hard by other means.
DDH hardness does not exclude such scenarios because DDH bounds only what algorithms can *find*,
not what values *exist*.

**Conclusion Q1:** Standard DDH does not imply H-PSEUDO. The implication fails for reasons of
type, not merely proof technique.

---

## Q2: Structural difference — distribution vs. computation

This section makes the gap precise.

### What DDH actually controls

DDH bounds the *advantage of any PPT algorithm* in a distinguishing game. The implication is:

    DDH holds ⟹ no PPT algorithm can compute DL_G(P) for a random P with non-negligible advantage.

### What H-PSEUDO actually requires

H-PSEUDO requires a bound on max_k |S_k(F)| where F is the *deterministic* set of points
whose x-coordinate is below a threshold t:

    F = { P ∈ E(F_p) : x(P) < t }

This is a fixed set determined entirely by (E, G, t). Its DL values {DL_G(P) : P ∈ F} are
fixed integers with no randomness. The character sum S_k(F) is a fixed complex number.

### The key asymmetry

DDH applies to *random* inputs. The DL values of small-x points are *not* random — they are
determined by the algebraic structure of E(F_p) and the choice of generator G. Even if G is
chosen uniformly at random (which changes the labeling of points but not the curve), once G is
fixed, the DL values are fixed.

A conceptual way to see the gap: DDH would remain true on a curve where all small-x points
happened to have DL values forming an arithmetic progression in Z/N (a highly structured,
non-pseudorandom set). This would violate H-PSEUDO while leaving DDH intact, because the
arithmetic progression structure is not something an efficient algorithm can exploit to *invert*
a single DL, yet it makes S_k(F) as large as B (not O(√B)).

**Conclusion Q2:** The gap between DDH and H-PSEUDO is not a proof technique gap — it is a
categorical mismatch. DDH is about hardness of computation on random inputs; H-PSEUDO is about
the statistical distribution of DL values on a structured input set. No standard reduction
can bridge this gap.

---

## Q3: Stronger assumption — DL as random permutation

### Formulation

Define the "DL-random-permutation" assumption:

    **DL-RP:** The function DL_G: E(F_p) → Z/N is computationally indistinguishable,
    as a whole bijection, from a uniformly random bijection π: E(F_p) → Z/N.

More precisely: for any fixed set F ⊆ E(F_p) and any PPT distinguisher D,

    |Pr[D({DL_G(P) : P∈F}) = 1] - Pr[D({π(P) : P∈F}) = 1]| = negl(log p)

where π is a uniformly random bijection independent of F.

### DL-RP implies H-PSEUDO (with C = O(√log p))

Under DL-RP: the set {DL_G(P) : P∈F} is computationally indistinguishable from a uniformly
random B-element subset S of Z/N. For such a random subset S, standard concentration bounds
(e.g., Hoeffding or Montgomery's large sieve) give:

    Pr[ max_{k≠0} |Σ_{s∈S} e^{2πi ks/N}| > C₀ · √(B log N) ] = o(1)

for an absolute constant C₀. Since log N = O(log p), this gives H-PSEUDO with C = O(√(log p)).

Under DL-RP, if any PPT algorithm could distinguish the actual S_k bound from the random
bound, it could distinguish DL_G from a random permutation, contradicting DL-RP. So H-PSEUDO
holds (in a computational/average-case sense) conditional on DL-RP.

### DL-RP is strictly stronger than DDH

The implication chain is:

    DL-RP ⟹ DDH    (DL-RP implies the DL of a single point looks random, which implies DDH)
    DDH ⟹ DL-RP    (FALSE — DDH gives nothing about the joint distribution of DL on structured sets)

DL-RP requires that the *entire DL map*, as a function from structured inputs to Z/N, is
statistically random. DDH only requires that a *single DL value on a random input* is
computationally hidden. These are categorically different.

DL-RP is not a standard cryptographic assumption. It is closer to modeling DL as a
random oracle — an assumption used in idealized security proofs but not grounded in
standard computational hardness.

### Empirical evidence refutes the statistical form of DL-RP

If DL_G were a truly random bijection, the expected character sum bound would be:

    E[ max_{k≠0} |Σ_{P∈F} e^{2πi k·DL_G(P)/N}| ] ≈ O(√(B log p)) ≈ O(√(B · 60))

At crypto scale (p ~ 2^{256}, log p ~ 177), the random prediction is C ≈ O(√177) ≈ 13.

The empirical data gives C ~ p^{0.079}. At p ~ 100003, p^{0.079} ≈ 2.5. At p ~ 2^{256},
p^{0.079} ≈ 2^{20} ≈ 10^6.

The empirical C at crypto scale far exceeds the random-permutation prediction by many orders
of magnitude. This means the *statistical* (information-theoretic) form of DL-RP fails: the
DL map on small-x points is demonstrably not close to a random permutation in distribution.
The algebraic structure of E(F_p) causes systematic non-uniformity in how DL distributes
over factor-base points.

**Conclusion Q3:** DL-RP implies H-PSEUDO, but DL-RP is not a standard assumption and is
*empirically refuted* in its statistical form by the very data that motivated H-PSEUDO. The
conditional proof via DL-RP would give a weaker bound (C = O(√log p)) than the empirically
observed C ~ p^{0.079}, confirming these are different regimes.

---

## Result: What can be proved and what is the gap?

### Summary table

| Assumption | Type | Implies H-PSEUDO? | Notes |
|---|---|---|---|
| DDH | Computational | No | Categorical mismatch: computational ≠ distributional |
| CDH | Computational | No | Same reason as DDH |
| ECDLP hardness | Computational | No | Same reason |
| DL-RP (computational form) | Computational + distributional | Yes | Non-standard; stronger than DDH |
| DL-RP (statistical form) | Distributional | Yes (C = O(√log p)) | Empirically refuted by BATCH data |
| Weil-type equidistribution | Number-theoretic | Potentially yes | Unconditional; requires new arguments |

### The fundamental gap

No standard cryptographic hardness assumption (DDH, CDH, ECDLP) implies H-PSEUDO. The gap
is not technical — it is a category mismatch between computational hardness and
information-theoretic distribution properties.

To prove H-PSEUDO, one of the following is needed:

**Route A — Unconditional via algebraic geometry:**
Express S_k(F) as a mixed exponential sum over E(F_p) and apply Weil's theorem (Riemann
Hypothesis for function fields) or its generalizations (Katz-Sarnak). This would give
unconditional bounds on |S_k(F)|, but requires reformulating the sum in a form to which
cohomological methods apply, and the resulting bound may be O(√p · log p) rather than O(√B).

**Route B — Conditional on an equidistribution assumption:**
Assume a distribution-theoretic statement: "For a random generator G, the DL values
{DL_G(P) : P ∈ F} are equidistributed in Z/N in the sense of Weyl." This is a
distribution assumption, not a computational one, and could be falsified or supported by
the data. The empirical exponent 0.079 provides a quantitative form of partial equidistribution.

**Route C — Connect to L-function zeros:**
The character sum S_k(F) for fixed k is an exponential sum of the form
Σ_{j: x([j]G) < t} e^{2πijk/N}. This can be interpreted via the spectral theory of the DL
map. Bounds on such sums for "almost all" k follow from the Weyl equidistribution theorem
applied to the sequence x([j]G), which in turn follows from irrationality properties of the
eigenvalues of the Frobenius endomorphism. This route is unconditional but gives pointwise
bounds only for generic k.

### What remains unproven

H-PSEUDO in its full form (max over all k, deterministic bound, explicit C(p) ~ p^{0.079})
has no known proof, conditional or unconditional, that follows from standard assumptions.
The empirical constant p^{0.079} itself lacks a theoretical explanation — it is an observation
that points toward genuine algebraic structure not captured by any current proof technique.

---

## Proposed next step

**Immediate (BATCH-080):**
The DDH conditional route is closed by the analysis above. The most tractable next direction
is Route A (unconditional via algebraic geometry), specifically:

1. **Reformulate S_k(F) as a Weil-type sum.** Write

       S_k(F) = Σ_{j=0}^{N-1} e^{2πi kj/N} · 1_{x([j]G) < t}

   and express the indicator 1_{x([j]G) < t} via additive Fourier analysis over F_p, giving

       S_k(F) = Σ_m â_m · T_{k,m}

   where â_m are Fourier coefficients of 1_{[0,t)} and

       T_{k,m} = Σ_{j=0}^{N-1} e^{2πi(kj/N + m·x([j]G)/p)}.

2. **Bound T_{k,m} via Weil.** T_{k,m} is a mixed exponential sum over the group E(F_p).
   For non-trivial (k, m), this is a character sum of an algebraic function on an elliptic
   curve, and Weil's theorem gives |T_{k,m}| ≤ C₁ · √p for some absolute C₁ (degree bound
   from the curve). Rigorously establishing this requires computing the associated ℓ-adic
   sheaf and its conductor.

3. **Combine and assess.** With |T_{k,m}| ≤ C₁ · √p and |â_m| = O(min(1, 1/|m|)) · (t/p),
   bound |S_k(F)| ≤ B + C₁ · √p · O(log p). Compare this bound against the empirical
   C · √B at relevant scales to determine whether the Weil route gives a tight result or
   whether a gap remains between the Weil bound and the empirical bound.

**If Weil bound matches empirical data:** This would constitute an unconditional proof of H-PSEUDO.

**If Weil bound is weaker (O(√p · log p) vs. O(√B)):** Record the gap, examine what additional
structural input (specific properties of the small-x point set under the DL map) would close it,
and consider whether the empirical exponent 0.079 itself has a Weil-theoretic explanation
(e.g., a secondary cancellation from curve-specific geometry).

**Scope note:** This is a pure mathematics task. It does not require further computation
beyond checking the Weil bound magnitude at representative parameters. The BATCH-079 empirical
data is sufficient; no new runs are warranted at this stage.
