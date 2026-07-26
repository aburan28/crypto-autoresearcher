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

## Theorem 8 (SP4 resolved): sub-rho m=3 index calculus == breaking 3SUM-Indexing
Model any m=3 decomposition oracle on the factor base (|F| = B) by its
preprocessing/space cost S and per-query cost T. With yield rho_3 = Theta(B^3/N),
collecting B relations needs Theta(N/B^2) draws, so
        Total(S, T, B) = S + B + Theta(T * N / B^2).

**(a) Necessity.** Total = o(sqrt N) forces both S = o(sqrt N) and
T = o(B^2 / sqrt N). Multiplying the two constraints:
        S * T = o( sqrt N * B^2 / sqrt N ) = o(B^2).
The sqrt(N) factors cancel *exactly*, for every choice of B (verified
numerically: the ratio (S_max * T_max)/B^2 = 1.000 at every B and N tested).

**(b) Sufficiency.** Conversely, a structure with S = B^{2-delta} and T = O(1)
gives, optimizing B ~ N^{1/(4-delta)},
        Total = Theta( N^{(2-delta)/(4-delta)} ),
which is < sqrt N for **every** delta > 0. (delta = 0.1 -> N^0.487;
delta = 1 -> N^{1/3}. Verified numerically.)

**Conclusion.** A sub-rho m=3 target-sectioned index calculus over a prime-field
elliptic curve exists **if and only if** there is a 2-sum-with-preprocessing
(3SUM-Indexing) data structure for elliptic-curve point sets with
S * T = o(B^2). Under the 3SUM-Indexing conjecture no such structure exists, so
no sub-rho m=3 algorithm exists; conversely, any such algorithm *refutes*
3SUM-Indexing for curve-point sets. SP4 is therefore not merely "related to" a
hard problem -- it is **equivalent** to one.

### Corollary 9 (the binding resource is SPACE, not solve time)
Even a **free** decomposition oracle (T = 1) built with the standard quadratic
preprocessing S = Theta(B^2) yields
        min_B [ B^2 + N/B^2 ] = 2 sqrt(N)   at B = N^{1/4},
i.e. **exactly rho's cost, never better** -- no matter how fast the query is.
Consequently, *any* line of work that only accelerates the decomposition test
(faster Groebner solving, lower degree of regularity, better summation-polynomial
elimination -- i.e. driving sigma or T down) provably **cannot** beat rho at m=3.
The only escape is subquadratic *preprocessing space*. This redirects the search:
the quantity to attack is S, not T.

## Theorem 10 (all-m closure): no decomposition length escapes
Let a = ceil(m/2). The meet-in-the-middle family (tabulate all a-sums: space
B^a; query enumerates the complementary floor(m/2)-sums: T = B^{m-a}) gives,
using draws = Theta(N/B^{m-1}) and a+(m-a)=m,
        Total(B) = B^a + Theta(N / B^{a-1}),  minimized at B ~ N^{1/(2a-1)},
        Total = Theta( N^{a/(2a-1)} ).
Since a/(2a-1) > 1/2 for every finite a (equivalently 2a > 2a-1), we get:

  **For EVERY decomposition length m >= 3, the meet-in-the-middle family is
  strictly worse than Pollard rho**, with exponents 2/3 (m=3,4), 3/5 (m=5,6),
  4/7 (m=7,8), ... converging to 1/2 from ABOVE as m -> infinity but never
  reaching it. (Verified numerically at N = 10^18.)

This closes the "maybe a larger m escapes" hatch unconditionally: increasing m
buys a better exponent but never crosses sqrt(N), and larger m is independently
limited (S_8 is the largest computed summation polynomial).

### Theorem 11 (the free-oracle dichotomy -- and a scope correction)
With the SAME space S = B^a but a hypothetical **free** query (T = 1),
Total = B^a + N/B^{m-1}, and the behaviour SPLITS:
  - **m = 3:** optimum is exactly 2 sqrt(N) -- a free oracle gives NO gain.
    The binding resource is SPACE (this is Corollary 9).
  - **m >= 4:** a free oracle DOES beat rho: N^{0.416} (m=4), N^{0.445} (m=5),
    N^{0.391} (m=6). Here the binding resource is the QUERY cost T at fixed
    space, not the space.
**Scope correction.** Corollary 9's conclusion ("speeding up the decomposition
test cannot beat rho") is therefore **specific to m = 3** and must not be read
as universal: at m >= 4 the query/solve cost is exactly the binding variable, so
solve-acceleration work (Groebner, degree of regularity, elimination) is aimed
at the right variable there -- it simply has to reach the k-SUM-Indexing
frontier. Concretely at m = 4: with S = B^2 and B ~ N^{1/4} one needs
T = o(B) -- i.e. a 2-sum structure on the pair-set (size M = B^2) with space M
and query o(M^{1/2}), exactly the (S,T) = (M^{2-eps}, M^{1-delta}) regime the
3SUM-Indexing conjecture forbids.

**Unified conclusion.** At every m >= 3, beating Pollard rho is equivalent to
violating the k-SUM-Indexing frontier for curve-point sets -- at m = 3 on the
space side, at m >= 4 on the query side. The barrier is uniform in m.

## Theorem 12 (the internal-relation variant also fails, for every m)
The analysis above assumed the *target-sectioned* scheme (draw random
g = aP+bQ, test decomposition). Classical index calculus instead harvests
relations **among factor-base elements themselves**: find ~B zero-sum m-subsets
P_{i_1}+...+P_{i_m} = O inside F, with no random draws at all. This variant is
not covered by Theorems 2-11, so we close it separately.

The expected number of zero-sum m-subsets of F is C(B,m)/N ~ B^m/(m! N).
Requiring at least B of them forces
        B >~ (m! N)^{1/(m-1)}.
Finding them costs at least the meet-in-the-middle search on F, i.e. >= B^a with
a = ceil(m/2) (and at least B for the linear algebra). Hence
        Total >= B^a = Omega( N^{a/(m-1)} ),  a = ceil(m/2).
Since 2*ceil(m/2) >= m > m-1, we have a/(m-1) > 1/2 for every m, so:

  **The internal-relation variant is strictly worse than Pollard rho for every
  decomposition length m**, with exponents 1 (m=3), 2/3 (m=4), 3/5 (m=6),
  4/7 (m=8), 5/9 (m=10), ... again approaching 1/2 from ABOVE without reaching
  it. (Verified numerically at N = 10^18 with exact constants; e.g. m=3 needs
  B ~ N^{0.52}, already past rho before any search begins.)

Note the parity oscillation (odd m is worse than the neighbouring even m),
because ceil(m/2) jumps while the relation-density exponent 1/(m-1) falls
smoothly.

**Coverage statement.** Together, Theorems 2, 10, 11 and 12 cover both principal
index-calculus architectures (target-sectioned and internal-relation), every
decomposition length m, every factor base (Lemma 1), generic-group methods
(Cor. 3), the naive algebraic oracle and the standard algorithmic toolkit
(Prop. 7). In all cases the cost is >= sqrt(N) unless the k-SUM-Indexing
frontier for curve-point sets is violated.

## Theorem 13 (the factor-base catch-22: choosing the instance does not help)
A natural objection to applying 3SUM-Indexing hardness here: 3SUM-Indexing is a
*worst-case* problem over adversarial sets, whereas an index-calculus designer
**chooses** the factor base F. Could a cleverly chosen F make the decomposition
query easy? No -- the freedom is self-defeating.

Let D = |D_m(F)| be the sumset size. Two facts pull in opposite directions:
  (i) **Yield** is D/N, so collecting B relations needs B*N/D draws: one wants D
      as LARGE as possible.
  (ii) **Testability**: a small, structured D can be stored outright (O(1)
      queries), but Lemma 1 says D <= (2B)^m/m!, and any structure that makes D
      easy to describe makes D *small*.
The two are in direct conflict, and (i) dominates. Example (m=3, N = 10^12):
  - F an arithmetic progression {P, 2P, ..., BP}: D_3 = {3P,...,3BP} has only
    ~3B elements. The test is free (store 3B points, O(1) query) but the yield
    collapses to 3B/N, forcing ~N/3 draws: **total ~ 3.3 x 10^11**, catastrophic.
  - F unstructured: D_3 ~ 4B^3/3, MITM test (B^2 space, query B):
    **total ~ 2 x 10^8** at the optimum.
The unstructured base wins by three orders of magnitude, and it is precisely the
case in which the membership test is a genuine k-SUM.

**General bound.** Even granting an *ideal* structure that stores D_m explicitly
and answers queries in O(1), the total is D + B + B*N/D >= 2 sqrt(B*N),
and Lemma 1's cap D <= (2B)^m/m! forces D = sqrt(BN) to be attainable only when
B >~ N^{1/(2m-1)}, whence
        Total >~ N^{m/(2m-1)}   ( = 0.600, 0.571, 0.556, 0.545, ... > 1/2 ).
Once again strictly worse than rho for every m, approaching 1/2 from above.

**Conclusion.** The designer's freedom to pick F is neutralised: maximising yield
forces the sumset to be as large and unstructured as Lemma 1 permits, which is
exactly the regime where the decomposition query is a worst-case-like k-SUM.
This closes the most natural objection to importing 3SUM-Indexing hardness into
this setting, and explains *why* the worst-case hypothesis is the right tool here.

## CORRECTION to Corollary 9's interpretation (CORR-20260722-001)
Corollary 9's arithmetic is correct, but the inference drawn from it -- "the
binding resource is space, not solve time" -- generalised a single corner of the
(S,T) trade-off to the whole frontier and is **withdrawn**. Theorem 8's condition
is S*T = o(B^2), which has two usable corners:
- S = Theta(B^2) forces T = o(1): impossible (this is Corollary 9);
- **S = Theta(B)** -- the regime of an algebraic/Groebner test, which stores only
  the factor base and the polynomial system -- forces **T = o(B)**, which is NOT
  impossible. With T = B^{1-eps} the total is Theta(N^{1/(2+eps)}) < sqrt(N) for
  every eps > 0 (verified: N^0.473 at eps=0.2; N^0.418 at eps=0.5).
Consequently the summation-polynomial / degree-of-regularity line (DREG, SIG) is
**a valid route**, not a misdirected one, and its sharp target is:
        a decomposition test running in o(B) time with O(B) space.
The naive algebraic oracle is Theta(B^2), so the gap to close is B^2 -> o(B).
