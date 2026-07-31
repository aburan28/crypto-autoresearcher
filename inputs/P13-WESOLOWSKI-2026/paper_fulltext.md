# THE SUPERSINGULAR ISOGENY PROBLEM IN TIME AND MEMORY p^{1/3+o(1)}

**BENJAMIN WESOLOWSKI**

> Frozen source record. This full text was provided verbatim by the research
> coordinator (repository owner) on 2026-07-24 as the object of independent
> review under GOAL-P13-001. It is preserved here as an immutable input.

## Abstract

We prove that under a plausible heuristic assumption (on the smoothness of certain random integers), the supersingular isogeny problem can be solved in time and memory p^{1/3+o(1)}. This improves upon the previous best complexity of p^{1/2} · (log p)^{O(1)}.

This problem is arguably the central hard problem underlying isogeny-based cryptography, and the cost of its resolution is a major (and often the only) factor in the choice of secure parameters. The impact on concrete parameter sets remains to be clarified, as the asymptotic advantage of the new algorithm is mitigated by a superpolynomial overhead hiding in the o(1) exponent, and by its high memory requirement.

## 1. Introduction

We prove the following theorem.

**Theorem 1.1.** Assuming Heuristic 1, there is a Las Vegas algorithm which, given a supersingular elliptic curve E/F_{p^2}, finds a non-scalar endomorphism α ∈ End(E) \ Z in expected time and memory p^{1/3+o(1)}.

As an immediate corollary, applying the computational reductions [35, Theorem 1] and [35, Proposition 8.5], we deduce the following consequences.

**Corollary 1.2.** Assuming Heuristic 1, there is a Las Vegas algorithm of expected complexity p^{1/3+o(1)} for the supersingular endomorphism ring problem (given E supersingular, find a basis of End(E) — see Problem 2.3) and for the supersingular isogeny problem (given E and E′ supersingular, find an isogeny E → E′ — see Problem 2.4).

These three polynomially-equivalent problems constitute the first entry in The Isogeny Problems [12]. The previous best algorithms to solve them had complexity p^{1/2} · (log p)^{O(1)}, starting with [21]. This complexity had stayed remarkably stable, with subsequent improvements only impacting the logarithmic cofactor [15, 24, 26, 40].

### 1.1. Impact on isogeny-based cryptography

Finding isogenies or endomorphisms of supersingular elliptic curves is arguably the most critical problem in isogeny-based cryptography. The cost of its resolution is a major (and often the only) factor in the choice of secure parameters of schemes of this family, including:

- (Cryptosystems affected by the attack) the CGL hash function [14], the SQIsign digital signature family [7, 19, 20, 22, 34] (currently running in the NIST selection process [1] for post-quantum digital signatures), other signature schemes like GPS signatures [28] and PRISM [5], and the ⊗-MIKE key exchange [39].

The new algorithm does not constitute a complete break of these cryptosystems, but warrants a careful reevaluation of their concrete security parameters. Note that many other isogeny-based schemes remain safely out of range of this algorithm, including:

- (Cryptosystems safe from the attack) all group-action-based constructions like CSIDH [13] and (qt-)Pegasis [17, 18] (used in PQarrots [32], planned to be submitted to the NIST call for multi-party threshold schemes), as well as torsion-based key exchanges like M(D)-SIDH [25], FESTA [9] and POKE [8].

Indeed, other cryptanalytic algorithms dominate the security analysis of these schemes, already imposing a large enough choice for the characteristic p.

While the new algorithm improves the asymptotic cost from p^{1/2} · (log p)^{O(1)} to p^{1/3+o(1)}, the practical impact is still unclear, as the overhead hiding in the o(1) term is superpolynomial, much larger than the previous (log p)^{O(1)} cofactor. The algorithm parallelizes perfectly. However, its memory cost is essentially as high as the complexity p^{1/3+o(1)}, a serious obstacle for any deployment of the algorithm on instances of cryptographic size. It is currently unclear how to reduce the memory cost without increasing the time: the algorithm essentially resolves a claw-finding problem for two sets of size N = p^{1/3+o(1)}. The time-memory tradeoff of van Oorschot–Wiener [43] solves a claw-finding problem of this size in time essentially √(N^3/w) = p^{1/2+o(1)}/w^{1/2} with memory w. This allows one to interpolate between the p^{1/3+o(1)} high-memory algorithm presented here and the classic p^{1/2+o(1)} algorithms with polynomial memory like [21].

Note that the van Oorschot–Wiener algorithm is also parallelizable, leading to an attack in time p^{1/2+o(1)}/(w^{1/2} n) with memory w and n parallel processors. We refer the reader to [3, 16] for extensive practical considerations on the van Oorschot-Wiener algorithm (applied to a different context), and to [29] for similar considerations in the quantum setting (suggesting that quantum computation may only be advantageous to reduce the amount of memory, with the same time complexity).

We compute tentative bounds on the concrete cost of the algorithm in Section 4.1. Note that these estimates make optimistic assumptions on the actual cost of certain steps, hence should not be interpreted as accurate predictions.

### 1.2. Proof-of-concept implementation

The author is grateful to Lorenz Panny for swiftly developing a proof-of-concept implementation [36] in SageMath [42]. (Available at https://yx7.cc/files/p-one-third.py.)

### 1.3. Previous work

The computational problem of finding isogenies (or, equivalently, endomorphisms) between supersingular elliptic curves can be traced back to Kohel's thesis [30] in 1996: he describes an algorithm of complexity p · (log p)^{O(1)} [30, Theorem 75] for finding endomorphisms. The first claim of a complexity of p^{1/2} · (log p)^{O(1)} for the isogeny problem appears in 2006 in the article [14], where the authors suggest to use a prime p of the order of 2^256 to achieve 128 bits of security — an estimate that has been used up to this day. A memory-free algorithm with the same complexity was proposed in [21]: the Delfs–Galbraith algorithm.

In 2018, the first heuristic reductions [23] show that finding isogenies is essentially equivalent to finding endomorphisms; as a consequence, the earlier algorithms of complexity p^{1/2}·(log p)^{O(1)} extend to the supersingular endomorphism problem. The article [24] (as the later refinement [26]) proposes a different algorithm to compute endomorphisms, and introduce an idea that will prove very fruitful: instead of looking for endomorphisms E → E, they look for two distinct (separable) isogenies φ_i : E → E^{(p)} to the Frobenius conjugate of E, and deduce the endomorphism φ̂_2 ◦ φ_1 ∈ End(E). They show how to find such isogenies in time p^{1/2} · (log p)^{O(1)} by generating random isogenies E → E′ until E′ is "adjacent" to its conjugate E′^{(p)} — an event which occurs with probability O(p^{−1/2}). The idea of using Frobenius conjugates was reused in [40] to accelerate the Delfs–Galbraith algorithm, although still within the p^{1/2} · (log p)^{O(1)} asymptotic.

### 1.4. Overview of the algorithm

The new algorithm starts from the same idea as [24, 26]: finding a separable isogeny φ : E → E^{(p)}, where E^{(p)} is the Frobenius conjugate of E. Then, the composition ϕ ◦ φ ∈ End(E) is an endomorphism of E, where ϕ : E^{(p)} → E is the Frobenius isogeny. Since ϕ◦φ has inseparable degree p (which is not square), it is a non-scalar endomorphism, and we are done.

Finding such a separable isogeny φ : E → E^{(p)} is generally considered a difficult task, and is in fact the bottleneck of the earlier algorithms [24, 26].

However, a recent result [4] proves that there always exists an isogeny E → E^{(p)} of degree at most (p/2)^{1/3}. If one is unlucky, that isogeny could have degree an (unknown) large prime ℓ ≈ (p/2)^{1/3}, and finding it would be prohibitively expensive. However, if the degree factors as a product of small primes (i.e., the degree is smooth), then it factors as φ = η ◦ ψ where both η and ψ are smooth and of much smaller degree ≈ (p/2)^{1/6}. One can then hope to find them by listing smooth isogenies from E and from E^{(p)} of degree ≈ (p/2)^{1/6}, until they "meet in the middle".

To meet this smoothness condition, one can re-randomise the instance of the problem by performing a random walk E → E′, then hoping that the method works for E′, and pulling back the solution to E through the walk. This is where we need a heuristic assumption.

### 1.5. The heuristic assumption

The assumption is of a standard kind: we assume that certain random integers have the same smoothness probability as uniformly random integers of the same size. Such heuristics are ubiquitous in computational number theory, yet notoriously difficult to prove.

**Heuristic 1.** Let p be a prime number, and let E/F_{p^2} be a uniformly random supersingular elliptic curve. The degree of the smallest isogeny φ : E → E^{(p)} is B-smooth with probability at least u^{−u(1+o(1))}, where u = log(p/2)/(3 log(B)) (uniformly as p → ∞, if (log p)^ε < u < (log p)^{1−ε} for a fixed constant ε).

Let us justify this heuristic by showing that u^{−u+o(1)} is indeed the probability one would expect if deg(φ) were to behave like a uniformly random integer of the same size.

**Definition 1.3.** Fix any X, B > 0. An integer is B-smooth if all its prime factors are smaller than B. Write S(X, B) for the set of B-smooth integers smaller than X, and Ψ(X, B) = #S(X, B).

We have the following classical theorem.

**Theorem 1.4 ([10]).** Let X, B > 0, and u = log X / log B. Then, Ψ(X, B) = Xu^{−u(1+o(1))} uniformly as X → ∞, if (log X)^ε < u < (log X)^{1−ε} for a fixed constant ε.

Furthermore, we have the following bound on deg(φ).

**Theorem 1.5 ([4]).** Let E be a supersingular elliptic curve over a finite field F_{p^2}. Then there exists an isogeny from E to E^{(p)} of degree less than or equal to (p/2)^{1/3}.

Combining these two results, Heuristic 1 only asks that the degree of the smallest isogeny E → E^{(p)} has the smoothness probability that one would expect for a random integer of its size. In Section 4, we present computational experiments conducted in SageMath [42] supporting this assumption.

### 1.6. Acknowledgements

The author is grateful to Lorenz Panny for his proof-of-concept implementation [36] of the algorithm, and to Andrea Basso for suggesting a tighter choice of X in Algorithm 2 (replacing B with √B). The author further wishes to thank the entire SQIsign team [1], and the authors of [12] for their feedback and for insightful discussions — including proofreading and suggestions from Luca De Feo, Damien Robert, and Francisco Rodríguez-Henríquez which helped improve the quality of this article.

The author was supported by the European Research Council under grant No. 101116169 (AGATHA CRYPTY), and the Agence Nationale de la Recherche under grants ANR-22-PETQ-0008 (PQ-TLS) and ANR-22-PNCQ-0002 (HQI).

## 2. Preliminaries

### 2.1. Elliptic curves and isogenies

Fix a finite field k of characteristic p > 0, with algebraic closure k̄. An elliptic curve is an abelian variety of dimension 1. Given an elliptic curve E over k, we write E(k) for its group of k-rational points. Given two elliptic curves E1 and E2 over a field k, an isogeny φ : E1 → E2 is a non-constant rational map which is also a group homomorphism E1(k̄) → E2(k̄). Its kernel ker(φ) is a finite subgroup of E1(k̄).

The degree of an isogeny is its degree as a rational map. The isogeny φ is separable if deg(φ) = # ker(φ). Any isogeny φ : E → E′ can be factored as φ = ψ ◦ φ_{E,p^n}, where φ_{E,p^n} : E → E^{(p^n)} is the p^n-Frobenius isogeny, and ψ is separable. We then have deg(φ) = p^n · # ker(φ), and p^n is called the inseparable degree of φ. When deg(φ) = ℓ is a prime number, we say that φ is an ℓ-isogeny. When deg(φ) = 1, then φ is an isomorphism.

Given any finite subgroup G ⊂ E(k̄), there exists a separable isogeny φ : E → E′ such that ker(φ) = G. This isogeny φ is unique up to post-composition by an isomorphism, and we write E/G := E′. For any elliptic curve E and any prime number ℓ, there are ℓ + 1 distinct ℓ-isogenies with domain E, up to post-composition by an isomorphism.

For any non-zero integer m, the multiplication-by-m map [m] : E → E is an isogeny of degree m^2. Any isogeny φ : E → E′ has a unique dual isogeny φ̂ : E′ → E such that φ̂ ◦ φ = [deg(φ)]. The kernel of [m] : E → E is the m-torsion subgroup E[m]. The elliptic curve E is supersingular if E[p^i] = {0} for all i ≥ 0. Any supersingular elliptic curve over k̄ is isomorphic to a curve defined over F_{p^2}. In this article, we only consider supersingular elliptic curves defined over F_{p^2}.

An endomorphism of E is an isogeny E → E, or the zero morphism [0] : E → E. The endomorphism ring End(E) is the collection of all endomorphisms of E. It forms a ring for point-wise addition, and for composition of maps. The map Z → End(E) : m ↦ [m] is an injection, hence we can see Z as a subring of End(E). These elements Z ⊂ End(E) are the scalar endomorphisms of E. When E is supersingular, the ring End(E) is a lattice of rank 4, in which Z is a primitive sublattice.

### 2.2. Computing with isogenies

There exist several ways to encode isogenies. They can be explicitly written down as rational maps, or as composable sequences of rational maps (isogeny paths). Alternatively, they can be indirectly represented by interpolation data (the image of a few points — sufficiently many to determine the isogeny). In studying computational problems involving isogenies, the exact way in which they are represented is often immaterial: all we need is any encoding that allows to store and evaluate the isogeny φ in polynomial time in log(deg(φ)). Such an encoding is called an efficient representation of φ. More formally:

**Definition 2.1 (Efficient representation, following [44, Definition 1.3]).** Let A be a polynomial time algorithm. It is an efficient isogeny evaluator if for any D ∈ {0,1}* such that A(validity, D) outputs ⊤, there exists an isogeny φ : E → E′ (defined over some finite field F_q) such that: (1) on input (curves, D), A returns (E, E′), (2) on input (degree, D), A returns deg(φ), (3) on input (eval, D, P) with P ∈ E(F_{q^k}), A returns φ(P). If furthermore D is of polynomial size in log(deg φ) and log q, then D is an efficient representation of φ (with respect to A).

Any representation D of an isogeny (efficient or not) can be converted to an efficient isogeny representation at the cost of polynomially many evaluations — a consequence of the isogeny interpolation algorithm [11, 31, 38]. This property came to be known as the universality of the interpolation representation (see [41, Lemma 7.3] for a formalisation of this notion, in the more general context of abelian varieties).

### 2.3. Computational problems

Isogeny-based cryptography rests on a variety of computational problems, all equivalent under polynomial-time reductions. The following are some of the most important ones. In these definitions, the isogenies are encoded in any efficient representation.

The following problem is the object of Theorem 1.1.

**Problem 2.2 (OneEnd).** Given a supersingular elliptic curve E defined over F_{p^2}, find an endomorphism in End(E) \ Z.

The following two problems are the objects of Corollary 1.2.

**Problem 2.3 (EndRing).** Given a supersingular elliptic curve E defined over F_{p^2}, find four endomorphisms generating End(E) as a Z-module.

**Problem 2.4 (Isogeny).** Given E and E′ two supersingular elliptic curves defined over F_{p^2}, compute an isogeny φ : E → E′.

These three problems are computational equivalent under probabilistic polynomial-time reductions. This equivalence is the conclusion of a series of advances starting from heuristic reductions in [23], followed by rigorous reductions under the Generalised Riemann Hypothesis in [45], the introduction of OneEnd into the picture in [35], culminating in a larger network of unconditional equivalencies in [33].

## 3. Proof of the main result

**Definition 3.1.** Let E be an elliptic curve, and X, B > 0. We define the set of isogenies L(E, X, B) = {ψ : E → E′ | ψ has cyclic kernel and deg(ψ) ∈ S(X, B)}.

**Lemma 3.2.** For any X > B > 0, we have #L(E, X, B) ≤ Ψ(X, B)X(log(X) + 2).

*Proof.* For any x < X, the number I(x) of isogenies of degree x from E with cyclic kernel is at most x(log(x) + 2) ≤ X(log(X) + 2) (see the proof of [2, Lemma 5.7]). We then have #L(E, X, B) = Σ_{x∈S(X,B)} I(x) ≤ Ψ(X, B)X(log(X) + 2), which concludes the proof. □

**Algorithm 1: Listing B-smooth isogenies**

Require: A supersingular elliptic curve E/F_{p^2}, and parameters B and X.
Ensure: The list L(E, X, B) (Definition 3.1).

1. L ← ∅;
2. for ℓ ≤ B do
3.   for i = 1, . . . , ⌊log_ℓ(X)⌋ do
4.     for ψ ∈ L such that ℓ deg(ψ) ≤ X do
5.       Let E′ be the codomain of ψ : E → E′;
6.       L_{E′,ℓ} ← {(E′′, η) | η : E′ → E′′ is an ℓ-isogeny and ker(η) ⊄ ker(ψ̂)} the list of non-backtracking ℓ-isogenies from E′. Note that at this stage, it is sufficient to represent the isogenies η as sequences of elliptic curves (E0, E1, . . .), where each Ei is ℓ-isogenous to E_{i+1} for some ℓ ≤ B. In particular, one only needs to compute the codomain of each step η (via modular polynomials).
7.       L ← L ∪ {η ◦ ψ | η ∈ L_{E′,ℓ}};
8.     end for
9.   end for
10. end for
11. return L.

**Lemma 3.3.** Algorithm 2 terminates in time Ψ(X, B)·X^{1+o(1)}·B^{O(1)}, where X = B^{1/2}·(p/2)^{1/6}.

*Proof.* From Lemma 3.2, the size of the table L is at most Ψ(X, B)X(log(X)+2) = Ψ(X, B)X^{1+o(1)}. The cost of computing the list (with Algorithm 1) is dominated by the cost, for each batch of (≤)ℓ + 1 new entries, of computing these new entries: the non-backtracking ℓ-neighbors of E′. These are precisely the roots of the modular polynomial Φ_ℓ(j(E′), x) ∈ F_{p^2}[x] (see [27, Section 25.2]). Computing the polynomial Φ_ℓ(j(E′), x) ∈ F_{p^2}[x] and finding its ℓ + 1 roots requires time (B + log p)^{O(1)}. [Footnote: We do not presently investigate the best possible exponent O(1), because this constant will be absorbed in other asymptotics. It is of course critical for a practical deployment of the algorithm. As suggested by Damien Robert, the fastest way to populate the list might be through batched evaluations of these modular polynomials.]

The cost of computing the list is thus at most #L · (B + log p)^{O(1)} = Ψ(X, B)X^{1+o(1)}B^{O(1)}, matching the claimed running time. The cost of the final loop through the table L is dominated by that previous computation. □

**Lemma 3.4.** Suppose that the smallest isogeny E → E^{(p)} is B-smooth. Then, Algorithm 2 returns a separable isogeny φ : E → E^{(p)}.

**Algorithm 2: Finding a separable isogeny to the conjugate**

Require: A supersingular elliptic curve E/F_{p^2}, a parameter 0 < B < p.
Ensure: A separable isogeny α : E → E^{(p)}.

1. X ← B^{1/2} · (p/2)^{1/6};
2. L(E, X, B) ← the list of B-smooth isogenies from E, of cyclic kernel and degree at most X (computed with Algorithm 1);
3. L ← a table containing each entry ψ : E → E′ of L(E, X, B), keyed by the codomain E′ (let us write them as pairs (E′, ψ) ∈ L).
4. for (E′, ψ) ∈ L do
5.   if (E′)^{(p)} is the key of an entry ((E′)^{(p)}, χ) ∈ L then
6.     return χ̂^{(p)} ◦ ψ : E → E^{(p)}; Note that if the entries of L were represented as sequences of elliptic curves (see the note in Algorithm 1), one may want to convert this final isogeny to a more explicit form: using Vélu's formulas for each step, then computing an efficient representation by interpolation.
7.   end if
8. end for
9. return ⊥.

*Proof.* Write deg(φ) = Π_{i=1}^n ℓ_i the degree of φ (where the ℓ_i values are prime numbers smaller than B, not necessarily distinct). From Theorem 1.5, we have that deg(φ) ≤ (p/2)^{1/3}. Let k be the largest index such that Π_{i=1}^k ℓ_i ≤ X = B^{1/2}(p/2)^{1/6}. Let φ = η ◦ ψ be any decomposition of φ such that deg(ψ) = Π_{i=1}^k ℓ_i and deg(η) = Π_{i=k+1}^n ℓ_i. Note that by minimality of φ, it must have cyclic kernel, hence ψ and η also have cyclic kernel. By construction, deg(ψ) ≤ X, and deg(ψ) is B-smooth, and the domain of ψ is E, hence ψ ∈ L(E, X, B).

Now, let us prove that deg(η) ≤ X. If k = n, then deg(η) = 1 ≤ X and we are done. Otherwise, by maximality of k, we have deg(ψ)ℓ_{k+1} > X. Therefore

deg(η) = deg(φ)/deg(ψ) ≤ ℓ_{k+1}(p/2)^{1/3}/X ≤ B(p/2)^{1/3}/(B^{1/2}(p/2)^{1/6}) = B^{1/2}(p/2)^{1/6} = X.

Let χ = η̂^{(p)}. The codomain of η is E^{(p)}, so the domain of χ is E^{(p^2)} = E. Furthermore, deg(χ) = deg(η) is B-smooth and smaller than X, so χ ∈ L(E, X, B).

Finally, φ = η ◦ ψ so the codomain of ψ equals the domain of η; let it be E′. We have proved that both (E′, ψ) and (E′^{(p)}, χ) are entries in the table L, so the algorithm will find a matching entry. □

**Lemma 3.5.** Suppose that E is a uniformly random supersingular elliptic curve over F_{p^2}. Assuming Heuristic 1, Algorithm 2 successfully returns an isogeny with probability at least u^{−u(1+o(1))}, where u = log(p/2)/(3 log(B)).

*Proof.* By Lemma 3.4, the algorithm succeeds when the smallest isogeny E → E^{(p)} is B-smooth, and by Heuristic 1, this probability is at least u^{−u(1+o(1))}, where u = log(p/2)/(3 log(B)). □

**Remark 1.** Lemma 3.5 is a simple lower bound on the probability, and is not expected to be optimal. Indeed, it considers the single smallest isogeny E → E^{(p)}, and estimates its smoothness probability; but there are generally multiple small (non-cyclic) isogenies E → E^{(p)}, and it is sufficient for any one of them to be smooth. This has already been observed experimentally by Panny through his proof-of-concept implementation [36]. While practically relevant, this phenomenon is absorbed in the hidden term of the asymptotic complexity.

*Proof of Theorem 1.1.* The algorithm is described in Algorithm 3. It repeatedly calls Algorithm 2 on uniformly random curves E′, with the smoothness parameter B = e^{(1/3)√log(p/2)} = p^{o(1)}, until a success is hit. We fix the length n of the random walk to ensure that E′ is indistinguishable from uniform. Following [37] or the more explicit [6, Lemma 14], we can ensure that n = O(log(p)).

**Algorithm 3: Finding a non-scalar endomorphism**

Require: A supersingular elliptic curve E/F_{p^2}.
Ensure: A non-scalar endomorphism α ∈ End(E) \ Z.

1. B ← e^{(1/3)√log(p/2)}; Note that in practice, one may instead precompute an optimal choice of B minimizing the total expected cost of the algorithm.
2. while true do
3.   ω ← a non-backtracking random walk φ : E → E′ of length n in the 2-isogeny graph (see the proof for the choice of n);
4.   φ ← the output of Algorithm 2 on input E′ and B;
5.   if φ ≠ ⊥ then
6.     Let ϕ : E′^{(p)} → E′ be the p-Frobenius isogeny from E′^{(p)} to E′^{(p^2)} = E′;
7.     return ω̂ ◦ ϕ ◦ φ ◦ ω;
8.   end if
9. end while

By Lemma 3.5, and thanks to Heuristic 1, the success probability of one attempt is P0 ≥ u^{−u(1+o(1))}, where u = log(p/2)/(3 log(B)) = √log(p/2), hence

P0 = √log(p/2)^{−√log(p/2)(1+o(1))} = p^{−log(√log(p/2))√log(p/2)/log p · (1+o(1))} = p^{o(1)}.

By Lemma 3.3, each attempt takes time Ψ(X, B)X^{1+o(1)}B^{O(1)}, where X = B^{1/2} · (p/2)^{1/6} = p^{1/6+o(1)}. Writing w = log(X)/log(B) = (1/2 log B + 1/6 log(p/2))/log B = 1/2 + (1/2)√log(p/2), Theorem 1.4 implies

Ψ(X, B) = Xw^{−w(1+o(1))} = p^{1/6+o(1)}p^{o(1)} = p^{1/6+o(1)}.

We deduce that each attempt costs Ψ(X, B)X^{1+o(1)}B^{O(1)} = p^{1/6+o(1)}p^{1/6+o(1)}p^{o(1)} = p^{1/3+o(1)}. The total expected cost of Algorithm 3 is therefore this latter quantity multiplied by P0^{−1}, which is p^{1/3+o(1)}, as claimed.

It remains to prove correctness. When a success occurs, we get a separable isogeny φ : E′ → E′^{(p)} (with cyclic kernel). Now, ϕ : E′^{(p)} → E′ is the Frobenius isogeny. We clearly have ϕ ◦ φ ∈ End(E′), and it has inseparable degree p (which is not a square), so it cannot be in the subring Z. In particular, ω̂◦ϕ◦φ◦ω ∈ End(E) is also non-scalar — which concludes the proof. □

## 4. Experimental results

### 4.1. Rough estimation of the concrete cost

Let us estimate a lower bound on the concrete cost of the algorithm (under the assumption that the bound on the success probability derived in Lemma 3.5 is tight). Consider B to be an optimizable parameter, and let X = B^{1/2} · (p/2)^{1/6}. The size of the tables constructed in Algorithm 2 is at least

M = Ψ(X, B)X.

This is derived like the upper bound from Lemma 3.2, but using that the number of isogenies of degree d is at least d. Now, let us be conservative and assume that constructing a table costs a single F_{p^2}-operation per entry, so a total of M F_{p^2}-operations per table. In doing so, we anticipate that Algorithm 1 is not optimal. Now, the memory cost of the algorithm is ≈ M, and its time cost is ≈ M/P0 F_{p^2}-operations, where P0 is the probability of success of one iteration of Algorithm 3. We estimate P0 as in Lemma 3.5.

With these estimates, and optimizing B for best time, we obtain the following costs:

- For log2(p) ≈ 256 (SQIsign NIST-I): ≥ 2^106.5 F_{p^2}-operations and memory ≥ 2^92.5; (previous methods: ≈ 2^128 F_{p^2}-operations and negligible memory);
- For log2(p) ≈ 384 (SQIsign NIST-III): ≥ 2^157.5 F_{p^2}-operations and memory ≥ 2^138.6; (previous methods: ≈ 2^192 F_{p^2}-operations and negligible memory);
- For log2(p) ≈ 512 (SQIsign NIST-V): ≥ 2^204.2 F_{p^2}-operations and memory ≥ 2^181.3; (previous methods: ≈ 2^256 F_{p^2}-operations and negligible memory);
- For log2(p) ≈ 576: ≥ 2^230.9 F_{p^2}-operations and memory ≥ 2^206.0; (previous methods: ≈ 2^288 F_{p^2}-operations and negligible memory);
- For log2(p) ≈ 768: ≥ 2^302.4 F_{p^2}-operations and memory ≥ 2^272.2; (previous methods: ≈ 2^384 F_{p^2}-operations and negligible memory).

We emphasize again that these numbers are obtained via a rough underestimation of the size of the table and the cost of its generation. On the other hand, we are assuming here that the bound of Lemma 3.5 is tight: the above numbers may be overestimating the factor 1/P0 (see Remark 1).

### 4.2. Supporting the heuristic assumption

This section presents computational experiments conducted in SageMath [42] supporting Heuristic 1. Fix a prime number p. Given a random elliptic curve E, computing the degree of the shortest isogeny E → E^{(p)} is generally extremely costly. To perform experiments with large p, we exploit the Deuring correspondence: instead of a random elliptic curve E, we generate a random maximal order O in the quaternion algebra B_{p,∞} ramified at p and ∞. Through the Deuring correspondence, E corresponds to a maximal order O. Then, the lattice of isogenies Hom(E, E^{(p)}) (with the quadratic form deg) is isometric to the unique two-sided ideal P of reduced norm p in O (with the quadratic form Nrd/p).

Therefore, we sample random maximal orders (uniformly random up to conjugation), compute the ideal P, and find the smallest vector in P. Its norm corresponds to the degree of the smallest isogeny E → E^{(p)} for a uniformly random E. We then factor this norm, and record its largest prime factor ℓ. The corresponding isogeny is B-smooth for any B ≥ ℓ.

After gathering a large number of data points, we are then able to compare the probability of the degree being B-smooth against the prediction of Heuristic 1. Our results for 100,000 samples over the field F_{p^2}, p = 5 · 2^248 − 1 (i.e., the security level I of SQIsign [1]) are represented in Figure 1. The same experiment conducted for p = 27·2^500 − 1 (i.e., security level V of SQIsign [1]) with 10,000 samples is represented in Figure 2. In all cases, the data points closely align with the prediction of Heuristic 1.

In the case p = 5·2^248−1, the smoothest sample out of 100,000 is 12589-smooth. The predicted probability to be 12589-smooth is ρ(u) ≈ 1/69232, consistent with the observation.

In the case p = 27 · 2^500 − 1, the smoothest sample out of 10,000 is e^23-smooth. The predicted probability to be e^23-smooth is ρ(u) ≈ 1/3312, consistent with the observation.

**Figure 1.** Cumulative distribution of the logarithm of the largest prime factor dividing the degree of the smallest isogeny E → E^{(p)}, for 100,000 supersingular elliptic curves E/F_{p^2} sampled uniformly at random, for p = 5 · 2^248 − 1 (i.e., the prime used for the first security level of SQIsign [1]). For each abscissa x, the black line plots the proportion of samples which are e^x-smooth. The dotted grey line represents the theoretical prediction ρ(u) ∼ u^{−u(1+o(1))}, where u = log(p/2)/(3x) (with ρ the Dickman-de Bruijn function). The plot on the left represents the whole data, and the plot on the right is a focus on the 500 smoothest isogenies.

**Figure 2.** Same experiments as Figure 1, but for p = 27 · 2^500 − 1 (i.e., security level V of SQIsign [1]). The plot on the left represents the whole data (10,000 samples), and the plot on the right is a focus on the 500 smoothest isogenies.

## References

[1] Marius A. Aardal, Gora Adj, Diego F. Aranha, Andrea Basso, Isaac Andrés Canales Martínez, Jorge Chávez-Saab, Maria Corte-Real Santos, Pierrick Dartois, Luca De Feo, Max Duparc, Jonathan Komada Eriksen, Tako Boris Fouotsa, Décio Luiz Gazzoni Filho, Basil Hess, David Kohel, Antonin Leroux, Patrick Longa, Luciano Maino, Michael Meyer, Kohei Nakagawa, Hiroshi Onuki, Lorenz Panny, Sikhar Patranabis, Christophe Petit, Giacomo Pope, Krijn Reijnders, Damien Robert, Francisco Rodríguez-Henríquez, Sina Schaeffler, and Benjamin Wesolowski. SQIsign. Tech. rep. National Institute of Standards and Technology, 2025. url: https://sqisign.org.

[2] Marius A. Aardal, Andrea Basso, Luca De Feo, Sikhar Patranabis, and Benjamin Wesolowski. "A Complete Security Proof of SQIsign". In: Advances in Cryptology - CRYPTO 2025. Vol. 16005. LNCS. Springer, 2025, pp. 190–222. doi: 10.1007/978-3-032-01887-8_7.

[3] Gora Adj, Daniel Cervantes-Vázquez, Jesús-Javier Chi-Domínguez, Alfred Menezes, and Francisco Rodríguez-Henríquez. "On the Cost of Computing Isogenies Between Supersingular Elliptic Curves". In: SAC 2018. Vol. 11349. LNCS. Springer, 2019, pp. 322–343. doi: 10.1007/978-3-030-10970-7_15.

[4] Yves Aubry, Roger Oyono, and Christelle Vincent. Minimal degree of an isogeny between a supersingular elliptic curve and its conjugate. 2026. arXiv: 2607.14624 [math.NT]. url: https://arxiv.org/abs/2607.14624.

[5] Andrea Basso, Giacomo Borin, Wouter Castryck, Maria Corte-Real Santos, Riccardo Invernizzi, Antonin Leroux, Luciano Maino, Frederik Vercauteren, and Benjamin Wesolowski. "PRISM: Simple and Compact Identification and Signatures from Large Prime Degree Isogenies". In: PKC 2025, Part III. Vol. 15676. LNCS. Springer, 2025, pp. 300–332. doi: 10.1007/978-3-031-91826-1_10.

[6] Andrea Basso, Giulio Codogni, Deirdre Connolly, Luca De Feo, Tako Boris Fouotsa, Guido Maria Lido, Travis Morrison, Lorenz Panny, Sikhar Patranabis, and Benjamin Wesolowski. "Supersingular Curves You Can Trust". In: EUROCRYPT 2023. Vol. 14005. LNCS. Springer, 2023, pp. 405–437. doi: 10.1007/978-3-031-30617-4_14.

[7] Andrea Basso, Pierrick Dartois, Luca De Feo, Antonin Leroux, Luciano Maino, Giacomo Pope, Damien Robert, and Benjamin Wesolowski. "SQIsign2D-West - The Fast, the Small, and the Safer". In: ASIACRYPT 2024, Part III. Vol. 15486. LNCS. Springer, 2024, pp. 339–370. doi: 10.1007/978-981-96-0891-1_11.

[8] Andrea Basso and Luciano Maino. "POKE: A Compact and Efficient PKE from Higher-Dimensional Isogenies". In: EUROCRYPT 2025, Part II. Vol. 15602. LNCS. Springer, 2025, pp. 94–123. doi: 10.1007/978-3-031-91124-8_4.

[9] Andrea Basso, Luciano Maino, and Giacomo Pope. "FESTA: Fast Encryption from Supersingular Torsion Attacks". In: ASIACRYPT 2023, Part VII. Vol. 14444. LNCS. Springer, 2023, pp. 98–126. doi: 10.1007/978-981-99-8739-9_4.

[10] E Rodney Canfield, Paul Erdős, and Carl Pomerance. "On a problem of Oppenheim concerning "factorisatio numerorum"". In: Journal of number theory 17.1 (1983), pp. 1–28.

[11] Wouter Castryck and Thomas Decru. "An Efficient Key Recovery Attack on SIDH". In: EUROCRYPT 2023, Part V. Vol. 14008. LNCS. Springer, 2023, pp. 423–447. doi: 10.1007/978-3-031-30589-4_15.

[12] Wouter Castryck, Luca De Feo, Steven D. Galbraith, Péter Kutas, Krijn Reijnders, and Benjamin Wesolowski. The Isogeny Problems. Cryptology ePrint Archive, Paper 2026/1431. 2026. url: https://eprint.iacr.org/2026/1431.

[13] Wouter Castryck, Tanja Lange, Chloe Martindale, Lorenz Panny, and Joost Renes. "CSIDH: An Efficient Post-Quantum Commutative Group Action". In: ASIACRYPT 2018. Vol. 11274. LNCS. Springer, 2018, pp. 395–427. doi: 10.1007/978-3-030-03332-3_15.

[14] Denis X. Charles, Kristin E. Lauter, and Eyal Z. Goren. "Cryptographic Hash Functions from Expander Graphs". In: Journal of Cryptology 22.1 (2009), pp. 93–113. doi: 10.1007/s00145-007-9002-x.

[15] Maria Corte-Real Santos, Craig Costello, and Jia Shi. "Accelerating the Delfs-Galbraith Algorithm with Fast Subfield Root Detection". In: CRYPTO 2022, Part III. Vol. 13509. LNCS. Springer, 2022, pp. 285–314. doi: 10.1007/978-3-031-15982-4_10.

[16] Craig Costello, Patrick Longa, Michael Naehrig, Joost Renes, and Fernando Virdia. "Improved Classical Cryptanalysis of SIKE in Practice". In: PKC 2020, Part II. Vol. 12111. LNCS. Springer, 2020, pp. 505–534. doi: 10.1007/978-3-030-45388-6_18.

[17] Pierrick Dartois, Jonathan Komada Eriksen, Tako Boris Fouotsa, Arthur Herlédan Le Merdy, Riccardo Invernizzi, Damien Robert, Ryan Rueger, Frederik Vercauteren, and Benjamin Wesolowski. "PEGASIS: Practical Effective Class Group Action using 4-Dimensional Isogenies". In: CRYPTO 2025, Part I. Vol. 16000. LNCS. Springer, 2025, pp. 67–99. doi: 10.1007/978-3-032-01855-7_3.

[18] Pierrick Dartois, Jonathan Komada Eriksen, Riccardo Invernizzi, and Frederik Vercauteren. "sfqt-sfPegasis: Simpler and Faster Effective Class Group Actions". In: EUROCRYPT 2026, Part IV. Vol. 16545. LNCS. Springer, 2026, pp. 636–665. doi: 10.1007/978-3-032-25327-9_22.

[19] Pierrick Dartois, Antonin Leroux, Damien Robert, and Benjamin Wesolowski. "SQIsignHD: New Dimensions in Cryptography". In: EUROCRYPT 2024, Part I. Vol. 14651. LNCS. Springer, 2024, pp. 3–32. doi: 10.1007/978-3-031-58716-0_1.

[20] Luca De Feo, David Kohel, Antonin Leroux, Christophe Petit, and Benjamin Wesolowski. "SQISign: Compact Post-quantum Signatures from Quaternions and Isogenies". In: ASIACRYPT 2020, Part I. Vol. 12491. LNCS. Springer, 2020, pp. 64–93. doi: 10.1007/978-3-030-64837-4_3.

[21] Christina Delfs and Steven D Galbraith. "Computing isogenies between supersingular elliptic curves over F_p". In: Designs, Codes and Cryptography 78.2 (2016), pp. 425–440.

[22] Max Duparc and Tako Boris Fouotsa. "SQIPrime: A Dimension 2 Variant of SQISignHD with Non-smooth Challenge Isogenies". In: ASIACRYPT 2024, Part III. Vol. 15486. LNCS. Springer, 2024, pp. 396–429. doi: 10.1007/978-981-96-0891-1_13.

[23] Kirsten Eisenträger, Sean Hallgren, Kristin E. Lauter, Travis Morrison, and Christophe Petit. "Supersingular Isogeny Graphs and Endomorphism Rings: Reductions and Solutions". In: EUROCRYPT 2018, Part III. Vol. 10822. LNCS. Springer, 2018, pp. 329–368. doi: 10.1007/978-3-319-78372-7_11.

[24] Kirsten Eisenträger, Sean Hallgren, Chris Leonardi, Travis Morrison, and Jennifer Park. "Computing endomorphism rings of supersingular elliptic curves and connections to path-finding in isogeny graphs". In: ANTS XIV: Proceedings of the Fourteenth Algorithmic Number Theory Symposium, Open Book Series 4.1 (2020), pp. 215–232.

[25] Tako Boris Fouotsa, Tomoki Moriya, and Christophe Petit. "M-SIDH and MD-SIDH: Countering SIDH Attacks by Masking Information". In: EUROCRYPT 2023, Part V. Vol. 14008. LNCS. Springer, 2023, pp. 282–309. doi: 10.1007/978-3-031-30589-4_10.

[26] Jenny Fuselier, Annamaria Iezzi, Mark Kozek, Travis Morrison, and Changningphaabi Namoijam. "Computing supersingular endomorphism rings using inseparable endomorphisms". In: Journal of Algebra 668 (2025), pp. 145–189.

[27] Steven D Galbraith. Mathematics of public key cryptography. Cambridge University Press, 2012.

[28] Steven D. Galbraith, Christophe Petit, and Javier Silva. "Identification Protocols and Signature Schemes Based on Supersingular Isogeny Problems". In: ASIACRYPT 2017, Part I. Vol. 10624. LNCS. Springer, 2017, pp. 3–33. doi: 10.1007/978-3-319-70694-8_1.

[29] Samuel Jaques and John M. Schanck. "Quantum Cryptanalysis in the RAM Model: Claw-Finding Attacks on SIKE". In: CRYPTO 2019, Part I. Vol. 11692. LNCS. Springer, 2019, pp. 32–61. doi: 10.1007/978-3-030-26948-7_2.

[30] David Kohel. "Endomorphism rings of elliptic curves over finite fields". PhD thesis. University of California, Berkeley, 1996.

[31] Luciano Maino, Chloe Martindale, Lorenz Panny, Giacomo Pope, and Benjamin Wesolowski. "A Direct Key Recovery Attack on SIDH". In: EUROCRYPT 2023, Part V. Vol. 14008. LNCS. Springer, 2023, pp. 448–471. doi: 10.1007/978-3-031-30589-4_16.

[32] Marius A. Aardal et al. PQarrots: Macaw, Kea and Kakapo; Threshold primitives from isogeny-based group actions. NIST First Call for Multi-Party Threshold Schemes, Preview Writeup. Accessed: July 20 2026. 2026. url: https://csrc.nist.gov/csrc/media/Projects/threshold-cryptography/documents/TCall-1/PQarrots-PW01.pdf.

[33] Arthur Herlédan Le Merdy and Benjamin Wesolowski. "Unconditional Foundations for Supersingular Isogeny-Based Cryptography". In: TCC 2025, Part III. Vol. 16270. LNCS. Springer, 2025, pp. 266–297. doi: 10.1007/978-3-032-12296-4_9.

[34] Kohei Nakagawa, Hiroshi Onuki, Wouter Castryck, Mingjie Chen, Riccardo Invernizzi, Gioella Lorenzon, and Frederik Vercauteren. "SQIsign2D-East: A New Signature Scheme Using 2-Dimensional Isogenies". In: ASIACRYPT 2024, Part III. Vol. 15486. LNCS. Springer, 2024, pp. 272–303. doi: 10.1007/978-981-96-0891-1_9.

[35] Aurel Page and Benjamin Wesolowski. "The Supersingular Endomorphism Ring and One Endomorphism Problems are Equivalent". In: EUROCRYPT 2024, Part VI. Vol. 14656. LNCS. Springer, 2024, pp. 388–417. doi: 10.1007/978-3-031-58751-1_14.

[36] Lorenz Panny. Proof-of-concept implementation of Benjamin Wesolowski's 2026 attack against the OneEnd problem with time complexity p^{1/3+o(1)}. Python script. Accessed: July 20 2026. 2026. url: https://yx7.cc/files/p-one-third.py.

[37] Arnold K Pizer. "Ramanujan graphs and Hecke operators". In: Bulletin of the American Mathematical Society 23.1 (1990), pp. 127–137.

[38] Damien Robert. "Breaking SIDH in Polynomial Time". In: EUROCRYPT 2023, Part V. Vol. 14008. LNCS. Springer, 2023, pp. 472–503. doi: 10.1007/978-3-031-30589-4_17.

[39] Damien Robert. The module action for isogeny based cryptography. Cryptology ePrint Archive, Paper 2024/1556. 2024. url: https://eprint.iacr.org/2024/1556.

[40] Maria Corte-Real Santos, Arthur Herlédan Le Merdy, Joseph Macula, Michael Meyer, Travis Morrison, and Eli Orvis. Algorithms for solving the isogeny problem with oriented elliptic curves. Cryptology ePrint Archive, Paper 2026/1219. 2026. url: https://eprint.iacr.org/2026/1219.

[41] Maria Corte-Real Santos, Etienne Piasecki, and Benjamin Wesolowski. A computational framework for principally polarized abelian varieties and applications. Cryptology ePrint Archive, Paper 2026/1142. 2026. url: https://eprint.iacr.org/2026/1142.

[42] The Sage Developers. SageMath, the Sage Mathematics Software System (Version 10.7). https://www.sagemath.org. Computer software. 2025.

[43] Paul C. Van Oorschot and Michael J. Wiener. "Parallel collision search with cryptanalytic applications". In: Journal of cryptology 12.1 (1999), pp. 1–28.

[44] Benjamin Wesolowski. "Random Walks in Number-theoretic Cryptology". HDR Thesis. ENS Lyon, 2024. url: https://bweso.com/hdr.pdf.

[45] Benjamin Wesolowski. "The supersingular isogeny path and endomorphism ring problems are equivalent". In: 62nd Annual Symposium on Foundations of Computer Science. IEEE Computer Society Press, 2022, pp. 1100–1111. doi: 10.1109/FOCS52979.2021.00109.

*ENS de Lyon, CNRS, UMPA, UMR 5669, Lyon, France*
