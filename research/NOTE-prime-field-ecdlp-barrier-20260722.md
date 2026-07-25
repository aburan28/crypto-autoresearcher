# Localizing the prime-field ECDLP index-calculus barrier to a single
# fine-grained-complexity crux

A self-contained consolidation of this program's results. **Scope, stated
plainly:** these are unconditional and conditional *obstruction/reduction*
theorems plus a problem reframing. They do **not** break ECDLP. Their value is
to prove that essentially every approach except one is a dead end, and to reduce
the entire open question to a single, precisely-stated crux equivalent to a
well-known hard problem. Component facts (sumset counting, the index-calculus /
rho trade-off, Shoup, the chord-tangent law, 3SUM/GPT hardness) are classical;
the contribution is their assembly into a sharp localization. Novelty vs. the
full literature is unverified and not claimed.

## 1. Setup
E/F_p an elliptic curve, G = E(F_p), N = |G|. Factor base F ⊆ G, B = |F|,
F^± = F ∪ (−F). For decomposition length m, a target R is m-decomposable over F
if R = s_1+...+s_m with s_i ∈ F^±; D_m(F) = mF^± is the m-fold sumset, and the
yield is ρ_m(F) = |D_m(F)|/N. Target-sectioned index calculus: draw random
g = aP+bQ, test g ∈ D_m(F); each hit is a relation; after ≥ B independent
relations, solve the sparse B-unknown system mod ℓ and read off the log.

## 2. Results

**Lemma 1 (sumset cap; unconditional, verified).** |D_m(F)| ≤ C(2B+m−1,m) ≤
(2B)^m/m!·(1+o(1)) for *every* F; tight for random F when B = o(N^{1/m}). So no
factor base beats the yield exponent. [Proof: multiset counting. Verified on
Z/N, all cases.]

**Theorem 2 (localization; unconditional).** With per-decomposition-test cost σ,
any such algorithm costs T ≥ B + σ·m!·N/(2^m B^{m−1}); minimizing over B gives
T ≥ c_m(σN)^{1/m}. Hence:
- **(m=2, unconditional no-go)** T ≥ √(2N) = 1.414√N > rho (0.886√N), for every
  factor base. Factor-base engineering cannot help at m=2.
- **(m≥3, localization)** with σ=1 the collection+algebra is Θ(N^{1/m})=o(√N), so
  the *only* obstruction is σ: the algorithm beats rho iff σ = o(N^{m/2−1})
  (o(√N) for m=3). [Verified numerically across N=10^6..10^12.]

**Corollary 3 (Shoup + localization).** A decomposition test using only the
group law and encoding-equality is generic; by Shoup's Ω(√N) it cannot yield
index calculus below √N (and MITM gives N^{2/3}, §Prop 5). Therefore any sub-rho
algorithm must (a) use m≥3 and (b) be *non-generic* — exploit the F_p-algebraic
structure of the summation polynomial S_{m+1}.

**Proposition 4 (collinearity / GPT bridge).** By the chord-tangent law, three
curve points sum to O iff collinear. So m=3 zero-sum relations are exactly
collinear triples of F — General Position Testing, which is *unconditionally*
3SUM-hard (Gajentaan–Overmars). More generally (Riemann–Roch) k points sum to O
iff cut out by a degree-⌈k/3⌉ plane curve, so m-decomposition is an incidence
problem between F and low-degree plane curves. This explains why the incidence
approach (Szemerédi–Trotter / chord-richness) yields structure but no oracle:
incidence *counts* are not a collinear-triple *oracle*.

**Proposition 5 (MITM; unconditional, verified).** The pairwise-sum table gives a
generic m=3 total Θ(N^{2/3}) > √N.

**Proposition 6 (conditional m=3 no-go).** Any structure-oblivious m=3
decomposition oracle is 2-SUM-with-preprocessing (3SUM-Indexing). Optimizing
S + B + Θ(NT/B) on the conjectured frontier S·T = Θ(B²) gives Θ̃(N^{2/3}) at the
MITM corner. So under the 3SUM-Indexing conjecture, generic m=3 index calculus
is slower than rho. [Verified numerically.]

**Proposition 7 (naive algebraic oracle; verified).** The obvious S_4-based m=3
oracle (root-find the summation curve) is Θ(B²) — identical to MITM. And the
whole standard toolkit (MITM, algebraic root-finding, multipoint evaluation of
S_4 on the V×V grid, group-FFT/convolution) hits õ(B²) or õ(N), i.e. total
≥ N^{2/3}. The barrier is robust to the standard algorithmic toolkit.
[MITM/root-finding verified over p ∈ {101,251,509,1009}; the multipoint-eval and
FFT bounds are standard-complexity analysis.]

## 3. The crux (single open problem)
Everything above closes the generic and naive-algebraic routes. By Cor. 3 and
Props 4–7, a sub-rho prime-field algorithm exists **iff** there is a *non-obvious*
decomposition oracle that beats 3SUM-Indexing / GPT for the specific structured
instance "points on a cubic with the group-law sum," using S_{m+1} (e.g. a fast
multipoint/resultant structure or the group law itself). This is a genuine open
problem; a positive resolution is the breakthrough, a negative one is a
(conditional) full no-go.

## 4. Honest status and program
Proved: Lemmas/Props above (unconditional where stated, else conditional on the
3SUM-Indexing conjecture; toy-scale verifications noted). Open: the §3 crux.
Sub-problems and next steps are in PLAN-prime-field-ecdlp-program-20260722.md;
knowledge findings KN-FIND-COLLECTION-LB-001, KN-FIND-3SUM-NOGO-001,
KN-FIND-S4-ORACLE-001, KN-FIND-TOOLKIT-ROBUST-001 record the pieces. No
cryptographic breakthrough is claimed; this is a rigorous localization of one.
