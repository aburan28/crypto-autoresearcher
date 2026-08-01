# Heuristic 1 of Wesolowski (2026): Routes to Proof or Refutation, Bias Hunt, and Falsifiable Experiments

**Task:** TASK-20260724-P13-HEUR · **Role:** IdeaGenerator_P13HEUR · **Date:** 2026-07-24
**Frozen source under review:** `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` (B. Wesolowski, "The supersingular isogeny problem in time and memory p^{1/3+o(1)}", 2026).
**Scope note (AGENTS.md rule 7):** All small-p discussion below is toy-scale evidence. Nothing here validates or invalidates cryptographic-scale behaviour; it only tests the *model* underlying Heuristic 1.

**Label convention:** every claim is tagged **[PROVEN]** (theorem-level, either in the frozen paper, in retrieved literature, or derived rigorously in-line below), **[HEURISTIC]** (standard but unproven assumption/estimate), or **[SPECULATIVE]** (my conjecture/derivation sketch, not checked at theorem level).

---

## 1. The object of study

**Heuristic 1 (paper §1.5).** For uniformly random supersingular E/F_{p^2}, the degree of the smallest isogeny φ: E → E^{(p)} is B-smooth with probability ≥ u^{−u(1+o(1))}, u = log(p/2)/(3 log B), uniformly for (log p)^ε < u < (log p)^{1−ε}.

**Reformulations (chain of equivalences).**

1. **Two-sided ideal lattice (paper §4.2).** Under Deuring, Hom(E, E^{(p)}) with the degree form is isometric to the unique two-sided ideal P of reduced norm p in O ≅ End(E) ⊂ B_{p,∞}, with quadratic form Nrd/p. The quantity of interest — call it δ_E following [AOV] — is the norm of the shortest vector of P.
2. **Trace-zero rank-3 lattice [PROVEN, AOV Prop. 3.1 + §3].** For degrees n < p/4, every inseparable endomorphism of degree np has trace 0 (since p | nrd ⇒ p | trd, and nrd < p²/4 with nrd ≥ trd²/4 forces trd = 0). Hence δ_E = N1, the first successive minimum of a rank-3 lattice R ⊂ Hom(E, E^{(p)}) whose degree form is Q′ = Q/(4p), where Q is the ternary determinant form of rank-2 sublattices of the Gross lattice O^T. The discriminant of Q′ is p/4.
3. **Gram-matrix identity [PROVEN, AOV §5.1, eq. (7)].** A successive minimal basis of R has Gram matrix N = (N_i diag; off-diagonal x/2, y/2, z/2) with

   p = 4 det N = xyz − N3 x² − N2 y² − N1 z² + 4 N1 N2 N3,   0 ≤ x, y ≤ N1, |z| ≤ N2,   p/4 ≤ N1 N2 N3 ≤ p/2.

   Here N1 = δ_E.
4. **Bound [PROVEN, AOV Thm 4.2 via Cassels's theorem for ternary forms].** δ_E ≤ (p/2)^{1/3} for every ss E; sharp for infinitely many examples ("wisde primes", ~0.5% of primes ≤ 265,207 in their data). This is the paper's Theorem 1.5 (citation [4]).

**What a proof of Heuristic 1 must deliver.** A lower bound P(δ_E is B-smooth) ≥ u^{−u(1+o(1))} averaged over the ~p/12 curves (equivalently over maximal orders up to conjugation — δ_E = δ_{E^{(p)}} since End(E) and End(E^{(p)}) are conjugate orders, so uniform-over-curves ≈ uniform-over-conjugacy-classes; the O(1) extra-automorphism curves are negligible under either weighting). What a refutation must deliver: an exponent gap, i.e., probability ≤ u^{−u(1+c)} for a fixed c > 0 along infinitely many p (or a structural obstruction making smooth minima systematically rarer by more than u^{o(u)}).

---

## 2. Provability routes

### Route (a): shortest-vector statistics of random lattices → smoothness

- **[PROVEN/known]** For Haar-random lattices the distribution of the first successive minimum is well understood (Rogers' mean-value theorem, Schmidt, Södergren, Athreya–Margulis equidistribution of lattice ensembles). The family here is analogous: R is a rank-3 lattice of determinant p/4, so its typical first minimum is a constant times p^{1/3}, matching the AOV bound's scale.
- **[HEURISTIC → gap]** Two mismatches block direct application: (i) our ensemble is *arithmetic and thin* — the number of order types is ~p/12 (class number scale), and the lattices are integral, so N1 is an integer whose factorization is the whole question; Haar techniques say nothing about integrality or smoothness. (ii) Even for genuinely random integral lattices, *no rigorous result on the smoothness of λ1 as an integer exists anywhere in the literature I could retrieve or recall* (unverified recollection: smoothness is not addressed by the random-lattice literature).
- **Verdict:** intractable as stated. A proof along this route would be a standalone breakthrough in arithmetic statistics, comparable in difficulty to smoothness conjectures for polynomial sequences.

### Route (b): averaging over maximal orders via Eichler/Brandt trace formulas + moment methods — **the most promising route**

- **[PROVEN machinery]** The average over supersingular curves of the number of degree-n isogenies E → E^{(p)} is a class-number quantity. Sketch: pairs (E, α ∈ End(E) inseparable, nrd α = np) are counted by Eichler's mass/embedding formula; the trace of the n-th Brandt matrix is a sum over traces t with t² < 4np of Hurwitz class numbers H(4np − t²) times explicit local factors. For n < p/4 only t = 0 survives (|t| ≤ 2√(np) and p | t), so the count is governed by H(4np) — this is exactly the t = 0 phenomenon of Section 1, and the same machinery as [EHL+20, Thm 3.9] (curves adjacent to their conjugate in the ℓ-isogeny graph) and Gross/Zagier-style formulas. Magnitude: H(4np) ~ √(4np)·L(1, χ_{−4np})·(unit factors), and dividing by the mass (p−1)/24 gives an expected count per curve of order **√(n/p)·L(1,χ)**.
- **[HEURISTIC consistency check — the single most useful provable sanity result available]** Summing over n ≤ (p/2)^{1/3}: Σ √(n/p) ~ p^{−1/2}·(p^{1/3})^{3/2} = O(1). So the expected total number of sub-bound conjugate isogenies per curve is O(1), and the expected number with B-smooth degree is ~ const · u^{−u(1+o(1))}. **The first moment coincides with the heuristic's probability.** Heuristic 1 is thus *equivalent* to the statement "P(count ≥ 1) ≈ E[count]", i.e., near-disjointness of the events {∃ conjugate isogeny of degree n} across n, plus mildness of the L-factor fluctuations (Section 3, bias B3).
- **What remains unproven, concretely:** (i) a second-moment bound E[count²] ≤ (1+o(1))E[count] + E[count]², which requires counting *pairs* of trace-0 inseparable endomorphisms of two smooth degrees — i.e., rank-2 sublattices of O^T with prescribed determinant pair; expressible via higher Brandt matrices/genus theory but no ready-made formula retrieved; (ii) control of Σ over B-smooth n of L(1, χ_{−4np}) — needs moments of L(1,χ) weighted by smoothness of the discriminant cofactor.
- **Crucial robustness observation [PROVEN-shape, SPECULATIVE in detail]:** even under GRH-free extremes, L(1, χ_d) ∈ [(log log d)^{−c}, (log log d)^{c}] outside exceptional sets. These fluctuations are polyloglog in p, i.e., **p^{o(1)} = u^{o(u)}** — they cannot change the *exponent shape* u^{−u(1+o(1))}. Therefore the class-number/L-function channel, the only channel with known large fluctuations, **cannot refute Heuristic 1 by itself**. A refutation must come from a *representation-theoretic* obstruction (Section 3, B2 shows the local one is absent) or from strong correlation between the minimum and order arithmetic — neither is currently visible. This materially de-risks the heuristic while leaving it unproven.
- **Verdict:** a realistic (multi-year) analytic-number-theory program with identifiable sub-lemmas; currently the only route that could plausibly reach a conditional (e.g., GRH + Lindelöf-on-average) proof.

### Route (c): the Aubry–Oyono–Vincent data and extremal theory (arXiv:2607.14624, retrieved this session)

- **[PROVEN from retrieved text]** AOV computed δ_E for *all* curves for all p ≤ 22,000, all p with ⌊(p/2)^{1/3}⌋ = 36, and all sieved primes in [22,000, 265,207] passing the necessary condition (their eqs. (7)–(8)); 119 wisde primes ≤ 265,207 (~0.5% of primes). Their sieve (eq. (7)–(8)) reduces candidates by ~90%. For p = 263,429, computing all δ_E took < 35 s once maximal orders were known (order enumeration ~ 2 h on an M2 laptop). Code is public [AOV26, referenced in their paper].
- **Use for Heuristic 1:** this is exactly the ground-truth engine needed for toy-scale discrimination experiments (Section 5, EXP-1). Their extremal theory also shows that *at the top of the range* the lattice is forced near Hermite equality — highly atypical geometry — so statements about δ(p) (the max) must not be conflated with statements about the typical δ_E.
- **[HEURISTIC]** Their conjectures on δ(p) and the finiteness/density of wisde primes (their §6, not fully retrieved) are orthogonal to Heuristic 1's *average* statement but constrain its worst case.

### Route (d): making Canfield–Erdős–Pomerance uniformity rigorous for this family

- **[PROVEN]** CEP (paper's Thm 1.4, ref [10]) is proved only for uniform integers.
- **[HEURISTIC/unverified recollection]** Rigorous smoothness results for deterministic sequences exist but are limited (e.g., Dartyge/Tenenbaum-type results for n²+1 in restricted u-ranges; Friedlander–Iwaniec-type results for special forms). The present family — *the minimum* of a varying ternary quadratic form over a thin arithmetic ensemble — is strictly harder than any of those. (Label: unverified recollection of the literature boundary; no fetched source.)
- **Verdict:** no known path. Treat the random-integer model as an assumption to be *tested* (Section 5), not derived.

---

## 3. Bias hunt: arithmetic effects that could break (or save) the random-integer model

- **B1 [PROVEN] — the j(E) ∈ F_p spike.** If j(E) ∈ F_p then E ≅ E^{(p)}, so δ_E = 1 (perfectly smooth). The number of subfield ss j-invariants is class-number scale ~p^{1/2+o(1)}, versus ~p/12 curves: mass ~p^{−1/2+o(1)}. Negligible for the exponent; *helps* the attack; a fine-grained test of sampling uniformity.
- **B2 [PROVEN, derived here] — no small-prime congruence obstruction.** The degree form Q′ of R has discriminant p/4; hence for every prime ℓ ∤ 2p its mod-ℓ reduction is a *nondegenerate* ternary quadratic form over F_ℓ. A nondegenerate ternary form over a finite field is isotropic (Chevalley–Warning) and represents every residue class mod ℓ. **Therefore there is no forced divisibility of δ_E by small primes, and no forbidden residue class of δ_E mod ℓ (ℓ ∤ 2p), coming from the form itself.** This kills the most naive refutation route ("δ_E is always/never divisible by ℓ"). Note this concerns what a single form can represent; it does not prove equidistribution of the *minimum* across classes — that is what EXP-1/T2 measures.
- **B3 [SPECULATIVE, derivation sketch] — class-number bias *against* smooth degrees (constant factor).** By route (b), the expected number of degree-n conjugate isogenies is proportional to H(4np) ≈ (√(4np)/π)·L(1, χ_{−4np})·w-factors. Write L(1,χ) = Π_ℓ (1 − χ(ℓ)/ℓ)^{−1}. For ℓ ∤ 2np, χ(ℓ) = (−4np/ℓ) = ±1, and E[(1−χ(ℓ)/ℓ)^{−1}] = ℓ²/(ℓ²−1) > 1. For ℓ | n (ramified), χ(ℓ) = 0 and the factor is exactly 1. A B-smooth n has *many* small prime divisors, each demoting its Euler factor from mean ℓ²/(ℓ²−1) to 1. Net effect: smooth degrees carry systematically **fewer** conjugate isogenies than a naive product predicts — a genuine bias against Heuristic 1, of magnitude ≈ Π_{ℓ | n, ℓ small}(1 − ℓ^{−2}) (e.g., ≈ 0.63 for 2·3·5·7 | n). The total bias summed over primes is bounded by Σ_ℓ O(ℓ^{−2}) = O(1): **a constant factor, absorbed by the (1+o(1))**, but large enough to matter for (i) the paper's Section 4.1 concrete-cost numbers, (ii) fine-grained statistical tests — naive Dickman fits at toy p should show a small smoothness *deficit* if B3 is real and the first moment drives the probability. EXP-2 is designed to measure exactly this.
- **B4 [PROVEN + SPECULATIVE] — extremal-lattice constraints.** From eq. (7): if x = y = z = 0 then p = 4N1N2N3, impossible for prime p unless N1 = 1; so extremal Gram matrices have at least one nonzero off-diagonal — no forced factorization of N1 results. Parity: p odd forces xyz + N3x² + N2y² + N1z² ≡ 1 (mod 2); every parity pattern of (N1, N2, N3) remains attainable in some branch (e.g., x odd, y, z even forces only N3 odd; N1 free). **No parity bias on δ_E.** Anecdote (n = 1, not evidence): the flagship wisde prime p = 101,051 has δ_E = 36 = 2²·3² — extremely smooth at the maximum of the range. A systematic look at factorizations of δ(p) over AOV's 119 wisde primes is a cheap add-on (EXP-3).
- **B5 [HEURISTIC] — size-distribution conservatism.** δ_E is typically a constant fraction *below* (p/2)^{1/3} (first minimum of a rank-3 lattice of det p/4 concentrates at constant × p^{1/3}). The heuristic plugs X = (p/2)^{1/3} into u; smaller actual degrees are smoother, so the size channel biases the truth *above* the stated lower bound — safe direction, absorbed in o(1) since log B → ∞.
- **B6 [HEURISTIC] — a model-identification gap in the paper's own Figures 1–2.** The plots compare the empirical CDF of log(largest prime factor) against ρ(u) with u computed from X = (p/2)^{1/3}, i.e., from the *maximum*, not from the actual δ_E of each sample. Two different models — "δ_E ~ uniform integer of size X" vs "δ_E ~ uniform integer of its actual size, with size drawn from the lattice-minimum distribution" — produce nearly indistinguishable curves at this resolution (they differ by a horizontal shift of order log(const)/log B in u). The figures support "no gross bias" but do not discriminate the mechanism; the right-panel zoom on the 500 smoothest samples is the only place the models separate, and no quantitative residual analysis is reported in the text. EXP-1/T1 addresses this with size-conditioned statistics.
- **B7 [PROVEN] — extra automorphisms.** j = 0, 1728 (and the handful of high-automorphism curves) matter only under mass weighting; under uniform-over-curves they are O(1) curves — negligible. For p ≡ 3 (mod 4) (all SQIsign primes), j = 1728 is a subfield ss curve, i.e., part of the B1 spike.
- **B8 [refuted candidate — recorded per AGENTS.md rule 8].** For p ≡ 3 (mod 4), B_{p,∞} = (−1, −p) and one might hope δ_E is forced to be a sum of two squares (via nrd on trace-0 elements = x² + p(y² + z²) with x ≡ 0 (mod p)-type arguments). This fails: reducing x² + p y² + p z² = ℓp mod p only requires ℓ ≡ y² + z² (mod p), and *every* residue mod p is a sum of two squares (each of the two sets of (p+1)/2 squares). No constraint results.
- **B9 [SPECULATIVE] — correlation between δ_E and p mod small primes.** Eq. (7) links p to the full Gram matrix; conditioned on N1 = n it constrains (N2, N3, x, y, z) but imposes no clean condition of the form "p mod ℓ determines n mod ℓ". No exploitable bias identified; EXP-1/T2 will test empirically whether stratifying by p mod ℓ reveals residual structure.

**Bias summary:** the only effects found that are large enough to see are B1 (negligible mass, positive) and B3 (constant factor, negative, testable). Nothing found changes the exponent u^{−u(1+o(1))}; the heuristic's real vulnerability is the unproven disjointness (route b), not an identified arithmetic bias.

---

## 4. Literature scan (only items actually retrieved this session)

- **[AOV] Aubry–Oyono–Vincent, arXiv:2607.14624** (fetched abs page + full HTML, v1, 16 Jul 2026): all results cited in Sections 1–3 above; bound δ_E ≤ (p/2)^{1/3}, Prop. 3.1, eqs. (7)–(8), wisde-prime statistics (119 primes ≤ 265,207; sieve cuts candidates ~90%), computational cost figures, code availability [AOV26].
- **Panny's proof-of-concept** (fetched https://yx7.cc/files/p-one-third.py): SageMath 10.9; attacks p = previous_prime(2^40); B = ⌈e^{(1/3)√ln(p/2)}⌉; uses X = ⌈B·(p/2)^{1/6}⌉ — note this is the *pre-tightening* value; the paper (acknowledging Basso) uses X = B^{1/2}·(p/2)^{1/6} in Algorithm 2. Table built by BFS over j-invariants via classical modular polynomials; success = collision j′ with (j′)^p in table.
- **Wesolowski FOCS 2022 full text** (HAL hal-03340899, fetched via search): Deuring-correspondence conventions (Nrd(I_φ) = deg φ, ideal↔isogeny dictionary) used for the Section 1 reformulation.
- **Context (search-result snippets, not deep-fetched):** NIST advanced SQIsign to Round 3 of the additional signature project on 2026-05-14/19 (quantumcomputingreport.com summary of NIST IR 8610); SQIsign Round-2 spec parameter table (p = 5·2^248−1, 65·2^376−1, 27·2^500−1) confirming the paper's experimental primes are the live parameter sets; Herlédan Le Merdy–Wesolowski arXiv:2309.11912 (OneEnd reductions, snippet).
- **Negative search result:** I found **no independent analysis, commentary, or follow-up work specifically scrutinizing Heuristic 1** (searches for the paper title, "Heuristic 1", smoothness of shortest-vector norms in quaternion ideals, pqc-forum discussion). Absence of evidence, not evidence of absence — the paper appears to be days old relative to this task.
- **Unverified recollection (not cited as source):** standard random-lattice references (Rogers, Södergren, Athreya–Margulis); CEP and Dickman–de Bruijn theory; Dartyge/Tenenbaum on smooth polynomial values; Gross–Zagier/Eichler trace-formula literature. These shaped Routes (a), (b), (d) but no specific figure depends on them.

---

## 5. Proposed falsifiable experiments

### EXP-1 "MINFACT" — discriminate the random-integer model for δ_E against biased alternatives (toy scale, laptop)

- **Mechanism.** If Heuristic 1's justification holds, then conditional on its value, δ_E factors like a uniform random integer of the same size. Any genus/representation constraint, size-model mismatch (B6), or L-factor-driven deficit (B3) produces measurable, signed deviations.
- **Protocol.**
  1. For every prime p in [10³, 22,000] (stratify p mod 4 and p mod 3, 5, 7), enumerate maximal orders of B_{p,∞} (SageMath quaternion-algebra machinery or AOV's published code [AOV26]); compute the Gross lattice, ternary form Q′, and δ_E = N1 by Eisenstein reduction (rank 3 — polynomial, fast: AOV needed < 35 s per p ≈ 2.6·10⁵ post-enumeration).
  2. Record per curve: δ_E, full factorization, δ_E/(p/2)^{1/3}, N2, N3, x, y, z, p mod {2..29}, #Aut, j ∈ F_p flag.
  3. Extension sample: for ~200 primes p ∈ [22,000, 2^28] sample maximal orders via random walks in the ideal-class graph (the paper's §4.2 method) to enlarge the δ_E range.
  4. Comparators computed exactly (no Dickman asymptotics — u is small at toy p): exact Ψ(n, B)/n by enumeration; exact predicted prime-rate of random integers of matching size distribution.
- **Metrics & predictions.**
  - **T1 (size-conditioned smoothness).** For B ∈ {5, 10, 20, 50}, compare empirical P(δ_E B-smooth | δ_E = n) against Ψ(n, B)/n, binned by n. Random model: residuals ≈ 0 across bins. B6-aware variant: also test against Ψ(X,B)/X with X = (p/2)^{1/3} — determines which size model the paper's Figures 1–2 actually support.
  - **T2 (congruence equidistribution).** Distribution of δ_E mod ℓ, ℓ ∈ {2,3,5,7,11}, overall and stratified by p mod ℓ. Prediction (B2, proven): no forbidden classes; prediction (random model): uniform. Deviations with |z| > 3 (χ²) signal genus-level bias.
  - **T3 (prime rate).** Fraction of δ_E that is prime vs exact random-integer prediction given the empirical size distribution. An *excess* of prime minima is the most dangerous deviation for the attack (prime ⇒ not B-smooth until B ≥ δ_E).
  - **T4 (smoothness deficit vs first moment).** Compare empirical smooth fraction to the B3-corrected first-moment prediction Σ_{n B-smooth} H(4np)-based weights (class numbers computed in Sage). If data ≈ B3-corrected prediction but < naive Ψ prediction, the mechanism is confirmed and quantified.
  - **T5 (spike calibration).** Fraction of curves with δ_E = 1 vs predicted ~p^{−1/2} class-number scale (B1); validates the sampler.
- **Test boundary.** p ≤ 2^28; u ∈ [2, 6]; statements apply only to the tested range. Toy-scale falsification of the *model* weakens Heuristic 1's justification globally (the heuristic claims uniformity in p), but toy-scale *confirmation* does not validate cryptographic sizes (AGENTS.md rule 7).
- **Falsification criteria.**
  - Heuristic 1 (as stated, with its (1+o(1))) is **weakened in tested scope** if T1 shows P(B-smooth | δ_E = n) ≤ ½·Ψ(n,B)/n persisting and growing with u across the full p range (an exponent-relevant deficit), or T3 shows prime-minimum rate exceeding the random prediction by > 3σ with the excess growing in p.
  - The *unconditional* random-integer model is **rejected and replaced** (not necessarily fatal to the attack) if T2 reveals forced or forbidden classes, or T4 confirms a stable constant-factor deficit explained by B3 — in which case the refined model (first moment with H(4np) weights) becomes the working hypothesis and the paper's §4.1 concrete-cost table needs a constant-factor correction.
  - Experiment is **invalid** (not evidence) if: sampler fails T5 calibration; Eisenstein reduction not verified against brute-force shortest-vector search at p ≤ 10³; or fewer than 10⁴ (curve, δ_E) records are collected.
- **Budget.** Enumerative phase: ~10³ primes × ≤ hours/p (worst at 22,000) — days on one laptop; sampling phase: hours. Pure SageMath/Python; no special hardware. Stopping rules: stop T1 early if the sign of the residual flips between u-bins (model confusion, redesign); stop whole experiment on any invalid criterion.

### EXP-2 "LMOMENT" — measure the B3 class-number bias directly (supports provability route b)

- **Mechanism.** Route (b) says P(∃ smooth conjugate isogeny) is driven by the first moment Σ_{n B-smooth, n ≤ (p/2)^{1/3}} w(n, p) with w ∝ H(4np)·local factors. B3 predicts w-averaged-over-smooth-n is a constant factor below the naive Ψ-weighted average.
- **Protocol.** For ~50 primes p ∈ [10^4, 10^6]: compute, in SageMath, (i) the exact first moment via Hurwitz class numbers H(4np) (order computations via `sage.schemes.elliptic_curves`/`quadratic_order` class numbers or PARI `qfbclassno`), (ii) the naive prediction Ψ(X,B)/X·(normalization), (iii) the empirical count of (E, smooth conjugate isogeny) from sampled maximal orders as in EXP-1 step 3. Compare (i)/(ii) (theory bias factor) and (iii)/(i) (disjointness factor).
- **Predictions.** B3 true ⇒ (i)/(ii) converges to a constant < 1 (expected 0.5–0.9) stable in p; near-disjointness ⇒ (iii)/(i) → 1 for the rare-event regime.
- **Falsification criteria.** If (iii)/(i) is bounded away from 1 (e.g., ≤ 0.5) across the range while events are rare, the disjointness assumption underpinning Heuristic 1 fails in tested scope — the strongest obtainable toy-scale refutation. If (i)/(ii) → 1, B3 is refuted and naive Dickman comparison is fine at constant level.
- **Boundary/budget.** Same toy-scale caveat; class-number computations at n·p ≤ 10^9 are seconds each in PARI; total budget days.

### EXP-3 "WISDEFACT" (cheap add-on) — factorization of extremal minima

- **Mechanism/question.** Are extremal values δ(p) = ⌊(p/2)^{1/3}⌋ biased smooth (B4 anecdote: 101,051 → 36)?
- **Protocol.** Recompute or extract AOV's 119 wisde primes ≤ 265,207 via their sieve (eqs. (7)–(8) — 1.6 s per prime in their timing) and their published code; factor δ(p); compare largest-prime-factor distribution against random integers of the same size; extend the sieve to p ≤ 10^6.
- **Falsification criterion.** If extremal δ(p) is B-smooth with frequency significantly *above* Ψ prediction (> 3σ), record an unexpected observation (rule 8) and investigate the extremal Gram identity (7) for forced structure; if consistent with Ψ, the B4 anecdote is closed as coincidence.
- **Boundary.** Concerns δ(p) (max over curves), not the distribution Heuristic 1 averages over; results constrain worst-case behaviour only.

---

## 6. Headline conclusions

1. **[HEURISTIC, supported by PROVEN first-moment structure]** Heuristic 1 sits in a favorable position: the proven class-number first moment of smooth-degree conjugate isogenies matches u^{−u(1+o(1))}, so the heuristic is exactly the claim that rare representation events are near-disjoint — the standard shape of a *true-looking* analytic heuristic.
2. **[PROVEN-derived]** Known fluctuation channels (L(1,χ) extremes, size distribution, subfield spike, automorphisms) are all p^{o(1)} or p^{−1/2+o(1)} effects: none can break the exponent. A refutation needs new representation-theoretic input; the naive local-obstruction route is provably absent (B2).
3. **[SPECULATIVE, testable]** The one identified signed bias (B3, ramification of small primes in Q(√(−4np))) is *against* smoothness but O(1) — it matters for the paper's §4.1 concrete-cost table and for interpreting Figures 1–2, not for the asymptotic claim.
4. **[HEURISTIC]** The paper's Figures 1–2 do not discriminate between size models (B6); a size-conditioned re-analysis (EXP-1/T1) on AOV-scale ground truth is the sharpest cheap test.
5. Full proof: route (b) is the only visible path and is a serious research program (second moment for pairs of ternary representations + smooth-weighted L(1,χ) moments); route (a) and (d) are currently intractable.

---

## Sources actually retrieved this session

1. https://arxiv.org/abs/2607.14624 — AOV abstract page (submission date, abstract).
2. https://arxiv.org/html/2607.14624v1 — AOV full text (all numbered results, tables descriptions, timings, code reference [AOV26]).
3. https://yx7.cc/files/p-one-third.py — Panny PoC source (parameters, method).
4. https://hal.science/hal-03340899/document — Wesolowski FOCS 2022 full text (Deuring dictionary conventions).
5. https://quantumcomputingreport.com/nist-advances-nine-post-quantum-digital-signature-candidates-to-third-evaluation-round/amp/ — NIST Round-3 advancement news (SQIsign status, May 2026); snippet via search.
6. https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/round-2/spec-files/sqisign-spec-round2-web.pdf — SQIsign Round-2 spec (parameter table); snippet via search.
7. https://arxiv.org/pdf/2309.11912 — Herlédan Le Merdy–Wesolowski (OneEnd); snippet via search.
