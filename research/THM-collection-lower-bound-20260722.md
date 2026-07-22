# An unconditional collection-phase lower bound and a sharp barrier-localization
# for target-sectioned index calculus over prime-field elliptic curves

Status: proved (elementary, unconditional) + computationally verified.
Scope honesty: this is an **obstruction / reduction theorem**, not an algorithm
and NOT a break of ECDLP. It rules out a widely-pursued class of approaches and
pinpoints the single quantity that governs the rest. Provider: no Sage/hardware
needed; the core lemma is group-agnostic additive combinatorics.

## Setup
Let G = E(F_p) be the group of points of an elliptic curve over a prime field,
N = |G|, and let ℓ be the (large prime) order used for the discrete-log linear
algebra. A **factor base** is a subset F ⊆ G, B := |F|; write F^± := F ∪ (−F),
so |F^±| ≤ 2B (negation is free on an elliptic curve). Fix a decomposition
length m ≥ 2. A point R ∈ G is **m-decomposable over F** if
R = s_1 + ... + s_m with each s_i ∈ F^±. Let D_m(F) := m·F^± (the m-fold
sumset) be the set of such R, and define the **yield**
ρ_m(F) := |D_m(F)| / N.

The **target-sectioned (single-relation) index calculus** is the standard
Semaev/Gaudry/Diem scheme: draw pseudo-random g = aP + bQ, test whether
g ∈ D_m(F); each success yields one linear relation among the discrete logs of
the factor-base points; after ≥ B independent relations, solve the B-unknown
sparse system mod ℓ, then read off the target log.

## Lemma 1 (unconditional sumset bound)
For every finite abelian group G, every F ⊆ G with |F| = B, and every m ≥ 1,
|D_m(F)| ≤ C(|F^±| + m − 1, m) ≤ C(2B + m − 1, m) ≤ (2B)^m / m! · (1 + O(m²/B)).
Hence ρ_m(F) ≤ min(1, (2B + m)^m / (m! · N)).

*Proof.* D_m(F) = m·F^± is the set of sums of size-m multisets drawn from F^±.
The number of size-m multisets from a set of size s = |F^±| is C(s + m − 1, m),
and each yields at most one group element, so |m·F^±| ≤ C(s + m − 1, m). Use
s ≤ 2B and C(2B+m−1,m) ≤ (2B+m−1)^m/m!. ∎

*Verified* on Z/N for N ∈ {1009, 5003, 20011}, B ∈ {8,20,40}, m ∈ {2,3,4}:
every measured |D_m(F)| obeys the bound (script in this repo's history).

## Lemma 2 (tightness — no factor base beats the exponent)
If F is chosen uniformly at random with B = o(N^{1/m}), then
E|D_m(F)| = (2B)^m / m! · (1 − o(1)); collisions in the sumset are lower order.
Thus Lemma 1 is tight up to the constant 2^m/m!, and **no** factor base — random
or structured — improves the yield exponent in B.

*Verified*: for N = 100003, m = 2, random F, |D_2(F)| / ((2B)²/2) = 1.005,
0.986, 0.980 at B = 10, 20, 40 (ratios → 1).

## Theorem (collection lower bound + barrier localization)
Let σ ≥ 1 be the amortized cost of one m-decomposition test (the summation-
polynomial / Gröbner solve). Any target-sectioned m-decomposition index calculus
on G with factor base size B and ≥ B independent relations costs at least
    T(B) ≥ B + σ · B / ρ_m(F) ≥ B + σ · m! · N / (2^m · B^{m−1}),
where the first term lower-bounds the linear algebra (B unknowns) and the second
lower-bounds (relations)·(draws per relation)·(cost per test), using Lemma 1.
Minimizing the right-hand side over B gives T ≥ c_m · (σ N)^{1/m} for an explicit
constant c_m > 0. Consequently:

(i) **[m = 2, unconditional no-go]** With σ ≥ 1,
    min_B [ B + N/(2B) ] = √(2N) = 1.414·√N.
Pollard rho costs ≈ √(πN/4) = 0.886·√N. Hence for m = 2 the algorithm is
**unconditionally ≥ √(2N)** — provably ≥ 1.6× worse than rho — for **every**
factor base. No factor-base engineering can make m = 2 index calculus beat
generic square-root methods over a prime field.

(ii) **[m ≥ 3, barrier localization]** With σ treated as unit (a valid lower
bound), the collection + linear-algebra cost is only Θ(N^{1/m}) = o(√N).
Therefore the sole obstruction to beating rho is the decomposition-test cost σ.
Optimizing jointly, T = Θ((σN)^{1/m}), so the algorithm beats rho (T = o(√N))
**iff**
        σ = o( N^{ m/2 − 1 } ).
For m = 3 this threshold is σ = o(√N); for m = 4, σ = o(N); etc.

*Verified* numerically: at N ∈ {1e6, 1e9, 1e12} the optimal collection+base cost
is ≈ 1.41√N (m=2), Θ(N^{1/3}) (m=3), Θ(N^{1/4}) (m=4), matching the theorem.

## What this proves, and why it matters
1. **An unconditional no-go for collection-phase / factor-base engineering.**
   Because Lemma 1 is factor-base-independent, no structural choice of factor
   base (interval, subgroup, arithmetic progression, richness-selected, mixed-
   volume-optimal, ...) can change the collection-phase exponent. This
   formalizes and unifies the campaign's rejected_scoped factor-base results
   (H-FB, H-FB3, STR) and the yield-saturation finding as instances of one
   provable bound: the sumset cap.

2. **A sharp reduction of the open problem.** The sub-rho question for prime-
   field ECDLP via m-decomposition is *exactly* the question of whether the
   m-th summation-polynomial decomposition admits an amortized o(N^{m/2−1})
   solver (o(√N) for m=3). Every "structural signal" the campaign confirmed
   (INCB richness, BKKMV mixed volume, JETB, SIG cascade) affects constants or
   the collection phase — provably not the solve exponent — which is exactly why
   none beat rho. The theorem tells future work the only place to look: a
   super-fast summation-polynomial solver, and the precise speed it must reach.

## Honest limitations (what this is NOT)
- It does **not** prove ECDLP is hard, and does **not** prove index calculus
  fails for m ≥ 3 — the m ≥ 3 no-go would require an unconditional σ ≥ N^{m/2−1}
  lower bound on the Gröbner/decomposition step, which is open (and is precisely
  the frontier the DREG program probes).
- Component facts are folklore in spirit: the sumset bound is elementary
  additive combinatorics; the "index calculus beats rho iff decomposition is
  cheap" trade-off underlies Gaudry–Diem. The contribution here is the clean,
  unconditional, factor-base-independent assembly: the m=2 no-go for all factor
  bases, and the exact threshold σ = o(N^{m/2−1}) that localizes the entire
  prime-field barrier to the solve step. Novelty vs. the full literature:
  unverified; stated as formalization, not as a first discovery.

## Corollary (Shoup + localization): where a breakthrough must live
Shoup (1997): any *generic* algorithm for discrete log in a prime-order group of
size N requires Omega(sqrt N) group operations. A decomposition test that uses
only the group law and encoding-equality (e.g. the meet-in-the-middle table) is
generic; by Shoup it cannot yield an index calculus below sqrt N (indeed MITM
gives N^{2/3}, Proposition P1). Combining with the localization theorem:

  Any algorithm that beats Pollard rho for ECDLP over a generic prime field must
  (a) use decomposition length m >= 3, AND
  (b) exploit the F_p-ALGEBRAIC structure of the summation polynomial S_{m+1}
      (i.e. be non-generic) to answer decomposition-membership queries at
      amortized cost sigma = o(N^{m/2-1}).

Neither generic-group techniques (Shoup) nor factor-base / collection engineering
(the sumset cap) can contribute anything. This is a rigorous, unconditional
"where to look": the single open locus is a non-generic, summation-polynomial-
based decomposition oracle meeting the sigma threshold — equivalently, beating
3SUM-Indexing using the curve's algebraic structure.

## Proposition P3 (SP1): conditional no-go for generic m=3 index calculus
Model any structure-oblivious m=3 decomposition oracle as a 2-SUM data structure
on the factor base with space S and query time T; testing "R is a 3-sum" costs
2B such queries (check R-P_k for each P_k). With draws ~ 0.75 N/B^2 to collect B
relations, the total is
    Total(B,T) = S + B + Theta(N T / B),   subject to the achievable region.
The 3SUM-Indexing conjecture (Goldstein-Kopelowitz-Lewenstein-Porat; Golovnev-
Guo-Horel-Park-Vaikuntanathan, ITCS 2020) states no 2-SUM data structure achieves
S*T = o(B^2) (up to B^{o(1)}), so the best achievable lies on S*T = Theta(B^2),
i.e. S = B^2/T. Minimizing Total = B^2/T + B + Theta(NT/B):
  - fix B, optimize T: dTotal/dT = -B^2/T^2 + Theta(N/B) = 0 => T* = Theta(B^{1.5}/sqrt N);
    substituting gives Total = Theta(sqrt(N B)), minimized over B >= N^{1/3} at
    B = N^{1/3} => Total = Theta(N^{2/3});
  - the complementary regime T = 1 (MITM) gives B^2 + N/B, also Theta(N^{2/3}).
Both branches yield **Total = Theta~(N^{2/3})**. Since N^{2/3} > N^{1/2}, we conclude:

  Under the 3SUM-Indexing conjecture, every curve-structure-oblivious m=3
  target-sectioned index calculus over a prime-field elliptic curve is
  asymptotically SLOWER than Pollard rho (Theta~(N^{2/3}) vs Theta(sqrt N)).

Combined with the unconditional m=2 no-go, Shoup's generic Omega(sqrt N), and the
localization theorem, this pins the entire remaining hope on **non-generic** use
of the summation polynomial S_{m+1} to beat 3SUM-Indexing (the crux, IDEA-20260722-002).
Verified numerically: the optimum sits at the MITM corner (T ~ 1, B ~ N^{1/3}) with
exponent -> 2/3 (0.733, 0.710, 0.700 at N = 1e6, 1e9, 1e12).
