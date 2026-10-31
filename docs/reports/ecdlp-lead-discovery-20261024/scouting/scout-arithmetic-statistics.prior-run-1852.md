# Scout dossier: arithmetic statistics against the named ECDLP bottlenecks

Field: arithmetic statistics. That covers Cohen–Lenstra, Sato–Tate (vertical and horizontal), Chebotarev, Katz–Sarnak, Deligne/Katz equidistribution, CM-point and isogeny-volcano statistics, and Bhargava-style averaging.
Scout run: 2026-10-24.
Write scope: only `scout/` under the session scratchpad. No repository was edited.
Provenance tags: `retrieved` means I fetched and read the source in this session. `recalled` means from memory, not checked. `internal` means a repository record. `measured-here` means a number I computed in this session with the scripts in `scout/scripts/` (toy scale, not a repo run).

## 0. Result in one paragraph

On prime-order curves this field's default use is closed. That use is "pick instances or factor bases whose decomposition counts deviate from the random model". Two facts close it:

- KN-FIND-007 conservation fixes the mean yield at a given base size.
- Markov's inequality gives P(c(R) ≥ 1) ≤ E[c(R)], so a deviation can only lower the hit rate. The only exception is the known coverage cap of 1.582.

Arithmetic statistics still decides three open leads, cheaply. Each decision is a closure or an instrument, not a speed-up.

- **C1 (B7, prime field), a theorem.** It is a Weil–Deligne bound on the Kummer sheaf of the Miller function, tensored with the Lang-torsor character sheaf. The Miller primitive U = f_{N,P}^{1/N} has character correlation with Z/N of at most 2√p + 2. The bound depends only on the support of div f mod e, not on its degree. Measured here: max |S|/√p = 2.019, 2.020, 2.014 against the bound 2.020/2.020/2.014. The N | p−1 control peaks at the full 333/333. This decides the discriminator of `LEAD-TRF-miller-cocycle-nonhom-transfer` (equidistribution and character correlation). Smart-ratio success is covered only for d ≲ p^{1/4}.
- **C2 (exotic/B7 instrument, prime field), completion plus Kohel–Shparlinski.** Any coordinate statistic φ(x) has log-character advantage at most ||φ̂||₁·(3√p+1)/N. Measured here: L1 exponents are Thue–Morse 0.400, Rudin–Shapiro 0.496, and LSB or a single digit O(log p). Every statistic with exponent below 1/4 is closed for any sub-rho HNP conversion. Thue–Morse is capped at β ≥ 0.1, which is not enough to close it. Rudin–Shapiro is unconstrained, so the census measurement is still required for those two.
- **C3 (B3 instrument, prime field with cofactor), the cofactor-coset counting law.** The yield of a whole-group small-abscissa base is K_G/(r/2), with E[K_G] = B(B−1+t)/|S| and t = #E(F_p)[2].
  - It reproduces the "unexplained" ℓ = 2 volcano floor deficit on the v2.1 data. Closed form 33/35 = 0.9429; exact K_G 0.9428; measured 0.9417 (14 classes).
  - It reproduces the ℓ = 3 null, including the 3-torsion contrast class l3-s1011.
  - It is consistent with the model τ spread above a target-sampling floor (null p95 0.045–0.071).
  - The χ² of cofactor-class counts against uniform reads χ²/df 0.94–1.09 over 25 classes.
  - It gives the identity N0 = 2·K_G + B (80/80 of the E3a rows). That identity explains E3a's unexplained slope excess: predicted 1.044, measured 1.054 OLS.
  - The gain is exactly 0 on prime-order curves.

The mechanism is internal (E3a, `research/generator_effect_ic_20261019`, v1 data). What is new here is the closed form, the v2.1 check, and the slope identity. The lead row is stale.

No exponent-moving (tier X gain) candidate survived inside this field. The killed list in §5 records why for each sub-area searched.

**B1 and B2 (prime-field oracle and solving degree): nothing from this field touches them.** The attempts were K4, K7 and K8 (and K2, K6). All die on F1 (the Weil threshold), F2 (conservation and Markov), or a total-cost-≈ p count.

C3 has zero effect on Table B, which uses prime-order curves. Its bottleneck is the selection lead; B3 is context only.

Correction from the advisor pass:
- C1 proves the equidistribution and character-correlation parts of H1. Smart-ratio success is proven only for d ≲ p^{1/4}.
- C3 decides LEAD-STR-class-representative-ic-selection only. The m = 3 lead LEAD-ICP-isogeny-transported-relation-yield needs the m = 3 ceiling.

## 1. Inputs read

- ATLAS.md (all families), KRMAP.md, object-frame-ideation.md §1–3, idea-generator heuristics and obstruction section, target-result-profile, IC LEADERBOARD tables A/B and phases.
- Lead YAMLs for every SO code touched (quoted below).
- IDEA-20261017-e3a6f1 (Miller primitive), IDEA-20260921-1ec106 (digit characters), IDEA-20261016-09fd08 (zeta-defect).
- crypto `research/isogeny-volcano-cost-v2_20261017` (README, PROTOCOL, analysis/*.json, classes/*/curves.jsonl, spec.json).
- crypto `research/generator_effect_ic_20261019` (README, PLAN, n0.json).
- Code: `prime_factor_base`, `PairTable::build_negation_folded`, `exact_decomposition_ceiling`.

## 2. Field-level framing: where arithmetic statistics can and cannot bite

**F1, the Weil threshold.** IC operates at |F|^m ≈ N with m ≥ 2, so |F| ≤ N^{1/2} ≈ p^{1/2}. Per-target decomposition counts c(R) = #{(P_i) ∈ F^m : ΣP_i = R} are incomplete sums of length about √p or less. Deligne/Katz, Bombieri and Kohel–Shparlinski give nothing there: the error √p·log p is at least the main term. This is the same wall that closed all six analytic routes of KN-FIND-e7a3b1 (`LEAD-EXO-dl-character-sum-pseudorandom`).

**F2, conservation and Markov.** For any base of size B on a prime-order group, E_R[c(R)] = binom(B+m−1, m)/N. P(c ≥ 1) ≤ E[c]. So instance or base selection by count statistics cannot raise the per-attempt hit rate above the mean. The coverage gain over Poisson is capped at 1/(1−e^{−1}) = 1.582 (KN-FIND-007). This closes the field's stated charge on prime-order curves.

**F3, what remains.** Two places are left.
- Complete sums over the whole group G. Deligne applies, with conductor bounds. This gives C1 and C2: closures of transfer and statistic leads.
- Group-structure statistics on curves with cofactor. This gives C3: an exact law for yield across volcano levels and models.

## 3. Candidates

### C1. Kummer-conductor bound closes the Miller-primitive transfer (B7, prime field)

**Ingredient (theorem).** Take a smooth projective curve X/F_p and a finite set S ⊂ X. Let 𝓕 be a rank-1 lisse sheaf on X∖S, tamely ramified, and geometrically nontrivial. Then |Σ_{x∈(X∖S)(F_p)} t_𝓕(x)| ≤ (2g − 2 + |S|)·√p.

Sources: Weil/Deligne via Grothendieck–Ogg–Shafarevich (Deligne, SGA 4½ "Sommes trig."; Weil II; recalled). For elliptic curves, the case "additive character of a function times a group character" is Kohel–Shparlinski, ANTS 2000, LNCS 1838, Cor. 1. That statement is retrieved as quoted in Ahmadi–Shparlinski, arXiv:1302.4210v3, Lemma 1: Σ_{n∈Z_T} ψ(x(nG)) χ(nG) ≪ q^{1/2}. A multiplicative-character analogue over E(F_p) appears in the Springer chapter doi:10.1007/11863854_24. I retrieved its abstract; the authors are unconfirmed and the theorem was not read.

**Statement (C1-Theorem).** Setting:
- E/F_p, G = E(F_p) of prime order N (or N || #E with G the N-part), and gcd(N, p−1) = 1;
- f a rational function on E;
- χ a nontrivial character of F_p^* of order e;
- ψ any character of G.

Let s_e(f) = #supp(div f mod e). If div f ≢ 0 mod e, then

  |Σ_{R ∈ G∖supp} χ(f(R))·ψ(R)| ≤ s_e(f)·√p (+ the |supp| excluded terms).

Proof sketch:
1. ψ is the trace function of the rank-1 lisse sheaf 𝓛_ψ obtained by pushing out the Lang torsor Frob − 1: E → E along ψ.
2. χ∘f is the trace function of the Kummer sheaf 𝓛_χ(f). That sheaf is tamely ramified exactly at supp(div f mod e) and is geometrically nontrivial there.
3. Their tensor product is rank 1, tame, and lisse on E∖supp. Its Euler characteristic is −s_e(f), H^0_c = H^2_c = 0, and the weights are ≤ 1.

The bound does not depend on deg f.

**Corollary (U).** Let U = f_{N,P}^{u} with u = N^{−1} mod (p−1). Then χ∘U = (χ^u)∘f_{N,P}. The divisor N(P) − N(O) ≢ 0 mod e for every e | p−1, because gcd(N, p−1) = 1. So s_e = 2 and every pair (χ ≠ 1, ψ) gives |S(χ, ψ)| ≤ 2√p + 2.

This proves two of the three parts of H1 of IDEA-20261017-e3a6f1 ("ell is equidistributed in Z/(p−1) … uncorrelated with characters of Z/N"). The proven parts are equidistribution of ℓ mod every e | p−1 and correlation with every character of Z/N. These are the lead's own discriminator. The relative size is 2/√p ≈ 2^{−127} at 256 bits, which is the random-function level: a random function gives about √N per character.

The third part is NOT fully covered. That is "Smart-ratio success", the event U(dR) = U(R)^d. It is a Kummer condition on g = ([d]^*f_{N,P})·f_{N,P}^{−d}, and supp(div g mod e) includes [d]^{−1}(P) and E[d], so s_e ≈ 2d² + 2. The theorem therefore bounds it only for d ≲ p^{1/4}. Larger d stays a cheap measurement in the lead's own panel.

**Corollary (degree-free class).** The same bound covers:
- every Miller function f_{n,T} for any n (s_e ≤ 3);
- products of M Miller or line functions (s_e ≤ 3M);
- the "unreduced Tate value";
- "Miller S-unit descent" maps with bounded mod-e support.

A multiplicative transfer can carry linear signal ε ≥ N^{−1/4} only if its divisor has more than about N^{1/4} points of nonzero multiplicity mod e. Heuristic HC1-1: that is the minimum signal any statistical conversion needs to beat rho (1/ε² samples ≤ √N).

**Measured here (toy, `scout/scripts/miller_u_spectrum_v2.py`, output `scout/miller_u_spectrum_v2.out`).** U was evaluated at every point with two independent Miller addition chains (binary, NAF) plus random split chains. The chains agree on 10022/10022, 9914/9914 and 19854/19854 points. Each S(a, b) sums over all of G except O, P and the 2 points no chain evaluated, so the bound is 2√p + 2. There are 10^8 to 4·10^8 character pairs per cell.

| cell | p | N = #E | gcd(N,p−1) | max over a≠0, b of \|S\|/√p | bound (2√p+2)/√p |
|:--|--:|--:|--:|--:|--:|
| theorem | 10007 | 10069 | 1 | 2.019 | 2.020 |
| theorem | 10009 | 9973 | 1 | 2.020 | 2.020 |
| theorem | 20011 | 19927 | 1 | 2.014 | 2.014 |
| control N \| p−1 | 10111 | N = 337, h = 30 | 337 | 333/333 points coherent (\|S\| = 333 = full) | not applicable (Tate pairing alive) |

The bound is attained (2√p is reached by some pair) and never exceeded. The positive control reproduces the pairing peak.

**Consequences.**
- `LEAD-TRF-miller-cocycle-nonhom-transfer` (open_unexamined): its own discriminator reads "Equidistribution at the 1/p rate closes the lead … any character correlation would be the first one-point transfer signal". The theorem decides that discriminator for U → closed_obstructed(theorem). The Smart-ratio success at d > p^{1/4} is recorded as an unproven residual measurement; it does not change the disposition.
- The `zeta-defect` sub-line (IDEA-20261016-09fd08) is NOT covered. Z is F_p-valued, the additive (Artin–Schreier) analogue. Its rational representation involves f_n'(x) with about n² poles, and the Artin–Schreier conductor is degree-dependent, so the bound is vacuous. The residual is stated as open: whether Z is Artin–Schreier-equivalent to a function with few poles.
- `LEAD-EXO-miller-pairing-cocycle` (open_next_step): C1 covers U as a function on G. The K2 route U(kP) = c·r_k·C^{k/N} needs r_k = ψ_{k−1}(P)/ψ_k(P). By the EDS identity r_k/r_{k+1} = x(P) − x(kP), r_k is a k-term prefix product of a conductor-2 function. Obtaining it from kP alone is the EDS-association problem. Lauter–Stange (SAC 2008, recalled) show that problem is ECDLP-equivalent. This is a conditional reduction, not a theorem. The lead's own K2 verification is still owed.

**SO codes touched.** For each, the quoted obstruction.statement and the premise that kept the lead open:

- **SO-PAIR, LEAD-TRF-second-torsion-direction.** "Balasubramanian-Koblitz: for N \|\| #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N \| p^k - 1 … an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N."
  - Premise not covering U: it concerns homomorphic or graph-type transfers, and U is non-homomorphic.
  - C1 closes the non-homomorphic Kummer class. The pairing (k_emb = 1) reappears as the unique exception: the case where div f ≡ 0 mod e makes 𝓛_χ(f) a Lang-torsor character.
- **SO-PADIC, LEAD-TRF-padic-canonical-section.** "… any non-homomorphic section recovers d only at the random 1/p rate. … Scope: non-anomalous prime-field curves, all lifts of E."
  - Premise not covering U: the scope is sections into E(Q_p), not F_p^*-valued maps.
  - C1 is the F_p^*-valued analogue, proven by sheaf theory.
- **SO-GEN, LEAD-EXO-augmented-oracle-ggm.** "Each named oracle is GGM-simulable … so the Shoup lower bound closes its candidate family at exponent 1/2 … Scope: oracles, not resources."
  - Premise not covering U: a U-oracle is not GGM-simulable, because it needs the actual point.
  - C1 replaces simulability with a character-sum bound. This is weaker in that it bounds only linear statistics, and that limit is stated.
- **SO-NET, LEAD-EXO-elliptic-net-eds.** "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead) …"
  - C1 sends the K2/r_k route of the cocycle lead into this obstruction.

**Pair and trichotomy.** The pair is (F_p^*-valued Kummer coordinate R ↦ χ(f(R)), with f = f_{N,P} or any bounded-mod-e-support function; operation set = full translation, tested through the characters of G). Class: coordinate-dependent. U is a function of the representation, and its graph is a change of coordinates. No collision gain is claimed.

**Tier, gain, cost.**
- Tier X: it decides an exponent-tier transfer lead. Predicted gain 0, a closure.
- Heuristic HC1-1 is above. HC1-2: none needed for the theorem itself, which is unconditional for χ ≠ 1 when gcd(N, p−1) = 1.
- Implementation: done at toy scale; filing the derivation and an optional Lean statement is about 1 day. Compute: seconds.

**First discriminating step.** File C1-Theorem as a KN-FIND derivation and replay the lead's own panel: IDEA-20261017-e3a6f1 minimal test, p ≤ 2^20, special and random primes, 30 curves each. Check max_{a≠0,b} |S| ≤ s_e·√p + #excluded, with the N | p−1 cell peaked. Outcome → disposition:
- (a) Every cell ≤ bound and the control peaked → LEAD-TRF-miller-cocycle-nonhom-transfer closed_obstructed(theorem). Best_measured: 2.014–2.020 ≤ 2 + 2/√p.
- (b) Any cell above the bound → an implementation or normalization defect, because the theorem holds. Re-derive before any reading. The disposition stays open_unexamined.
- (c) Control not peaked → instrument invalid.
- For the cocycle lead: exact K2 confirmed → closed_obstructed(theorem, via EDS association). K2 false → U-part closed by C1, with the K1 residue recorded.

**Self-kill risk.**
- Low on correctness: the theorem is textbook, and the toy check is tight.
- Moderate on value: the closure kills a lead nobody expected to work. The zeta-defect residue is not closed.
- Multi-query non-linear uses of U are not bounded by C1. They are bounded only by the general argument of SO-TORS.

### C2. Completion ledger: coordinate statistics vs log bits (exotic and B7 instrument, prime field)

**Ingredient.** Completion. Write φ(x) = Σ_a φ̂(a)·e(ax/p). Then apply the Artin–Schreier ⊗ Lang bound |Σ_{Q∈E(F_p)} e(a·x(Q)/p)·ψ(Q)| ≤ 3√p + 1. Here x has a double pole at O, so the Swan conductor is 2 and χ_c(E∖O) = −1; Kohel–Shparlinski give ≤ 4√p. This yields

  |Σ_{Q∈G} φ(x(Q))·ψ(Q)| ≤ ||φ̂||₁·(3√p + 1) for ψ ≠ 1.

So the advantage of φ(x(kP)) on any log character is at most ||φ̂||₁·3/√p. For log bits, multiply by O(log N). Sources: Kohel–Shparlinski 2000, retrieved via 1302.4210 Lemma 1. The completion technique is Shparlinski's standard bit-security method (recalled; e.g. Boneh–Shparlinski, CRYPTO 2001, on ECDH bits).

**Measured here** (`scout/scripts/digit_l1.py`, `scout/digit_l1.out`): exact normalized Fourier L1 on Z/p for p from 2^12 to 2^22.

| statistic | ‖φ̂‖₁ growth | at p ≈ 2^22 | implied cap on log-character advantage at 256 bits |
|:--|:--|--:|:--|
| Thue–Morse (−1)^{s₂(x)} | p^{0.400} (flat across 6 sizes) | 446 | ≤ 3·p^{−0.100} ⇒ β ≥ 0.1 (does NOT reach 1/4) |
| Rudin–Shapiro | p^{0.496} (≈ √p) | 1931 | vacuous |
| LSB of x | ≈ 0.77·ln p | 10.7 | ≤ ~400/√p ⇒ β ≥ 1/2 − o(1): closed |
| one base-B digit e(d_j(x)/B), B ∈ {16, 256} | O(log p) or bounded | 1.2–6.4 | closed |

**Reading.**
- The lead's HNP converter beats rho iff the advantage is N^{−β} with β < 1/4 (LEAD-EXO-hnp-advice-leakage, "exponent 2*beta vs 1/2").
- Every statistic with ‖φ̂‖₁ ≤ p^{1/4−ε} is therefore closed by theorem: LSB, single digits, residues mod small M, interval and window indicators.
- Thue–Morse is capped at β ≥ 0.1. Its value could still lie in [0.1, 0.25), so measurement is still needed.
- Rudin–Shapiro is unconstrained. Its flat spectrum is exactly the "random level" boundary.
- Prediction for the census (IDEA-20260921-1ec106): the λ readings are Thue–Morse 0.400 (structured, below 1/2) and Rudin–Shapiro ≈ 1/2. This applies if the census λ is this L1 exponent; I have not verified that the census's normalisation matches.

**SO codes touched.**
- **SO-TORS, LEAD-STR-torsion-module-leak.** "A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) … Scope: prime-order G, any l != N."
  - C2 quantifies the "partial information" for any bounded-L1 statistic. Premise extended: the closed lead does not price the information.
- **SO-GEN, LEAD-EXO-augmented-oracle-ggm.** Quoted above, "Scope: oracles, not resources". A coordinate statistic is not one of the named oracles, so it is not covered by simulability. C2 covers it by the L1 bound.
- **LEAD-EXO-dl-character-sum-pseudorandom** (exhausted). "… all six standard analytic proof routes are closed (KN-FIND-e7a3b1) …"
  - Those routes were short sums over a factor base, which is F1 territory.
  - C2 uses complete sums over G and so escapes that premise. It is a different regime and does not contradict that lead.

**Pair and trichotomy.** The pair is (coordinate statistic φ∘x of bounded Fourier L1; operation set = full translation via the characters of G). Class: coordinate-dependent.

**Heuristic HC2-1.** The measured L1 exponents (Thue–Morse 0.400, Rudin–Shapiro 0.496, up to 2^22) persist to 256-bit p. The Thue–Morse value is recalled as ≈ 0.40 from Fouvry–Mauduit / Mauduit–Rivat. The β ≥ 0.1 cap for Thue–Morse depends on HC2-1. The closure for bounded-L1 statistics (LSB, single digits) does not, because their L1 is O(log p) by direct computation.

**Tier, gain, cost.** Tier X, as the instrument for the HNP lead's exponent. Gain 0, a closure for λ < 1/4. Implementation trivial; done.

**First discriminating step.** Add a frozen column ‖φ̂‖₁ to the census harness for every statistic. Admit to measurement only the statistics with exponent ≥ 1/4 (Thue–Morse, Rudin–Shapiro). Measure their log-character advantage at 2^20–2^26 against the cap and a relabelled null. Outcome → disposition:
- Both at random level → LEAD-EXO-coordinate-statistic-leakage: closed_obstructed(theorem) for λ < 1/4, and exhausted_at_scale for Thue–Morse and Rudin–Shapiro. LEAD-EXO-hnp-advice-leakage stays blocked, with its blocker now a theorem for λ < 1/4.
- Rudin–Shapiro or Thue–Morse above random with fitted β < 1/4 → open_next_step and price the HNP conversion; best_measured is that advantage.
- Any statistic above its cap → implementation error.

**Self-kill risk.** High on novelty: the completion technique is classical (Shparlinski). Medium on value: it does not close the two statistics the census actually still owes.

### C3. Cofactor-coset counting law: the volcano ℓ = 2 yield effect is 2-torsion bookkeeping (B3 instrument, prime field)

**Ingredients.**
- Group structure across a 2-volcano. E(F_p)[2^∞] changes level by level: full 2-torsion (t = 4) above the floor, one rational 2-torsion point (t = 2) on the floor. The program's population table records this: Z/n × Z/2 versus cyclic. The theory is Kohel 1996 thesis; Miret–Moreno–Sadornil–Tena–Valls 2006 (recalled).
- Exact class bookkeeping of the negation-folded pair table. I read the code: `prime_factor_base` takes "the size smallest abscissae … both signs", drawn from the whole of E(F_p). `build_negation_folded` stores "one pair per orbit under negation … plus its own double".

**Derivation (C3-Law).** Let s_i = [r]P_i ∈ S, where S is the cofactor part with |S| = h. A table key lies in G iff:
- s_i = −s_j, for the sum P_i + P_j;
- s_i = s_j, for P_i − P_j;
- 2s_i = 0, for the double.

Hence K_G = Σ_{i<j}([s_i = s_j] + [s_i = −s_j]) + Σ_i [2s_i = 0]. Under heuristic HC3-1 (the cofactor components of the B smallest-abscissa points are i.i.d. uniform on S):

  E[K_G] = B(B − 1 + t)/|S|, with t = #S[2] = #E(F_p)[2].

Consequences:
- The yield per probe of a target uniform in G is about K_G/(r/2).
- Floor/crater ratio in a 2-volcano: (B − 1 + t_floor)/(B − 1 + t_crater) = 33/35 = 0.9429 at B = 32.
- ℓ = 3 volcanoes have no change of t across levels, so the ratio is 1. That holds even when the 3-torsion changes, as in l3-s1011.
- Planted 33-vs-32 control: 33(32+t)/(32(31+t)) = 1.0607 / 1.0625 / 1.0635 for t = 4 / 2 / 1.
- Exact identity with E3a: N0 (from `exact_decomposition_ceiling`, m = 2) = 2·K_G + B. Pairs are counted ordered across the ± classes, and the B same-abscissa pairs P + (−P) = O are included.
- Prime-order curves (h = 1): K_G = B² for every model and curve. Level, model and horizontal effects are identically 0.

**Measured here on v2.1** (re-analysis of the 7,760 curve-models from recorded parameters; no new runs). Scripts: `scout/scripts/volcano_kg.py`, `volcano_compare.py`; outputs `scout/volcano_kg_v21.json`, `scout/volcano_compare_v21.out`.

| quantity | prediction | measured (v2.1 analysis) |
|:--|:--|:--|
| ℓ = 2 floor/crater, geometric mean of 14 classes | closed form 0.9429; exact K_G 0.9428 | 0.9417 (pooled H1 0.942 [0.928, 0.956]) |
| per-class ℓ = 2 (e.g. l2-s1001 h=12; s1009; s1014) | 0.904; 0.926; 0.946 | 0.893; 0.926; 0.944 |
| ℓ = 3, geometric mean of 14 classes | closed form 1.000; K_G 1.002 | 1.006 |
| l3-s1011 (3-torsion changes, t = 1 → 1) | 1.019 (K_G) | 1.025 [0.968, 1.085]: "deficit not seen" explained |
| planted control 33/32 | 1.0607 to 1.0635 | 1.061 (ℓ = 2), 1.063 (ℓ = 3) |
| model τ (h > 1 classes) | K_G spread across models 0.027–0.104 | τ_rel 0.048–0.110, consistent class by class above a target-sampling floor. The per-class null p95 is 0.045–0.071 (e.g. l2-s1001 τ 0.101 vs null p95 0.069). The h = 1 classes, predicted 0, measure 0.031–0.041, below their null p95 of 0.045–0.049 |
| vertex-level fit, pooled | slope 1 | slope of ln measured on ln predicted = 0.954, corr 0.665, n = 905 |
| E3a identity N0 = 2K_G + B | exact | 80/80 E3a rows (`scout/n0_identity_check.out`) |
| E3a slope of ln yield on ln N0/r | ≈ N0/(N0−B): predicted OLS 1.044 | E3a 1.054 OLS, 1.064 WLS ("not explained here") |

**Reading.** E3a already showed on v1 that N0 removes the effects. This dossier adds four things:
1. The closed form, which names the 2-torsion of the diagonal and sign classes as the only level-dependent term.
2. Confirmation on the 28-class v2.1 data that the lead's best_measured is quoted from.
3. The l3-s1011 contrast explained.
4. E3a's slope excess explained by the identity.

`LEAD-STR-class-representative-ic-selection` still says "its mechanism is unknown" and plans a 3-arm 24–32-bit study. That row is stale.

**HC3-1 check (measured here, `scout/scripts/volcano_chi2.py`, `scout/volcano_chi2_v21.out`).** For every curve-model I counted the B = 32 base abscissae over the ±-orbits of S and compared the counts with B·|orbit|/h. χ² is summed over all models of a class.
- Result over the 25 classes with h > 1: χ²/df between 0.935 and 1.088. Every model was included.
- One class has upper-tail p = 0.021 (l2-s1009). That is about what 25 tests give by chance.
- Caveat: the expected cell counts are small (≈ 2.7 at h = 12), so the χ² is approximate.
- Reading: consistent with i.i.d. uniform cofactor components.

**Predicted gain (tier I, end to end).** This assumes HC3-1, which the check above found consistent.
- 0 on every prime-order curve: Table B and all deployed curves.
- On cofactor workloads, the existing `PrimeProjectedAbscissaBase`, or E3b's `subgroup=filter`, raises the per-probe hit rate by |S|·B/(B−1+t). That is ×3.66 (h=4, t=4), ×3.88 (h=4, t=2), and ×10.97 (h=12, t=4).
- This is an instrument correction to the volcano IC/rho gap (17–170×), not a B3 lever. The factor is a hit-rate prediction, not an S prediction. E3b must measure complete S against the §5a band, and filter costs about h× more abscissa scans plus one [r] check each.

**SO codes touched.**
- **SO-ALGFB, LEAD-ICP-algebraic-membership-factor-base.** "… mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N) … Scope: prime-order E/F_p, any base of size B."
  - Escaped premise: the scope is prime-order. The volcano curves have h ∈ {1, 2, 4, 7, 8, 9, 12}, so the effect is outside the theorem and does not contradict it.
  - C3-Law is the cofactor extension of conservation. It reduces to binom(B+1, 2)-type conservation at h = 1.
- **SO-ISO, LEAD-STR-isogeny-class-generic-invariance.** "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group …"
  - Premise: generic methods. A whole-group small-abscissa base depends on the full group structure, which is not a class invariant (t changes with the 2-volcano level). Hence the effect exists for IC and not for rho, matching H3.
- **SO-TABLE, LEAD-ICP-generic-table-decomposition.** "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N … Scope: any generic (enumeration/table) decomposition over F_p."
  - The MITM oracle used here is inside that scope. C3 only changes constants within it.

**Pair and trichotomy.** The pair is (whole-group small-abscissa base with signed points; operation set = translation by base elements, targets in G). Class: partial-action (IC Class I). The class-cancelling count is the block system of the cofactor quotient E(F_p) → S.

**First discriminating step.** Fold E3a and this re-analysis into the lead, and replace the 3-arm study with E3b on 4 v2.1 classes: two ℓ=2 classes (h = 4 and h = 12) and two ℓ=3 classes (h = 1 and h = 9). Arms: `prime-abscissa`, `subgroup=filter`, `subgroup=project`, all at B = 32.

Pre-registered predictions:
- filter/current yield = |S|B/(B−1+t), within ±10%;
- floor/crater under filter = 1.000, inside [0.98, 1.02];
- model τ under filter at the h = 1 null;
- at h = 1, the arms are byte-identical.

Outcome → disposition:
- All four hold → LEAD-STR-class-representative-ic-selection becomes closed_obstructed(proof). The proof: "level, model and horizontal IC yield effects are cofactor-coset counting K_G = B(B−1+t)/|S|, identically 0 on prime-order curves".
- Any miss → open_next_step, with the residual ratio as best_measured.

**Scope limit.** C3-Law and the 33/35 closed form are m = 2 (pair table). They do NOT decide LEAD-ICP-isogeny-transported-relation-yield, which uses the arity-3 oracle on P29/P37 conductor-gap curves. That lead needs either:
- the m = 3 class-cancelling ceiling, which E3a's `n0_over_r_m3` already computes; or
- a check that its curves have cofactor 1, in which case the effect is identically 0.

**Costs.** The re-analysis is done in about 1 minute. E3b is about 4 classes × the v2.1 IC arm, a few CPU-hours. Implementation: the projected base already exists, and filter is a small arm.

**Self-kill risk.** High on novelty: the mechanism is internal (E3a). Low on correctness. Value: it saves a pre-registered 24–32-bit study and removes the only positive-looking volcano lead.

## 4. Binary/Koblitz, one line

The C3 law applies verbatim to cofactor binary and Koblitz bases. Ordinary char-2 curves have t = 2, cyclic 2-part. A trace-zero subspace base (`subspace_is_trace_zero`) lands in 2E, so its classes are {0, 2} ⊂ Z/4. For a uniform split, K_G/|F|² is about 1/2 against 1 for a 4E-restricted base.

Check: compute `exact_decomposition_ceiling` on the Table A/C bases before assuming they are G-restricted. LEAD-ICB-cofactor-torsion-quotients covers the quotient side for ECC2K-130. Not investigated further.

## 5. Killed candidates (with reasons)

- **K1. Best-of-K isomorphic model by short-interval point density (vertical Sato–Tate / Davenport–Erdős).** The gain is √(2 ln K/X) in base density, which vanishes with size. The selection costs K·X Legendre symbols, which exceeds the saving at every Table B row. At the family optimum it is ≤ 7% of S at fp24 even for free selection. Dominated.
- **K2. Target preselection by decomposition-count deviation (high additive energy).** Markov gives P(c ≥ 1) ≤ E[c], and the coverage cap is 1.582. Both are known (SO-ALGFB quote above).
- **K3. Chebotarev or Katz–Sarnak cycle-type census on Semaev covers.** SO-MONO, LEAD-ICE-semaev-cover-monodromy: "… on the factor-base locus S_m splits completely with an exact root multiset, so the generic-fibre cycle-type census is a no-go as a relation-rate probe at every m >= 3".
- **K4. Proving Poisson statistics for c(R) in the IC regime (Kurlberg–Rudnick moment method, Deligne).** F1: the box sides are about √p, so the sums are incomplete and no theorem exists. Even a theorem would not move the cost, because of F2.
- **K5. Elliptic sum-product energy bounds (Shparlinski 2008; Ahmadi–Shparlinski 2013, retrieved abstract) to close coincidence harvest.** The known bounds |F|^{3−δ} sit far above the random level 2|F|². They cannot close anything, and κ_rel is about 1.0 anyway.
- **K6. Small-coefficient model selection (u-twist to make (u^4a, u^6b) small, or secp256k1's b = 7) for small-root decomposition.** It helps only in the lifting regime X^4·‖S_3‖ < p. There a mod-p relation is an integer relation on the characteristic-0 model, which LEAD-ICP-char0-lifting-xedni-smoothness closes: "Jacobson-Koblitz-Silverman-Stein-Teske (2000) show xedni does not beat rho …".
- **K7. Target-dependent multiplicative-coset base F_R = {x ∈ c_R μ_d}.** It gives about d decompositions per target at Õ(d) cost, but with no shared basis, so it yields no linear relations. As a known-log pool it is generic (SO-TABLE quote above).
- **K8. Subgroup base with sparse elimination (x₂^d mod S_3 in F_p[x₁][x₂]).** Per target Õ(d) for d²/p decompositions, so total cost is about p at any d. That is worse than rho, and consistent with the measured β_work 0.647 (B2).
- **K9. Ulmer high-rank surfaces y² + xy = x³ − t^d (explicit points) as a relation source.** The target must lie on a section through a prescribed fibre point. That is LEAD-EXO-global-lift-height's open step, and the SO-XEDNI obstruction applies to fixed families.
- **K10. Small-|D| non-unit endomorphism orbit bases (prime field).** LEAD-STR-small-cm-disc-nonunit-endo: "A non-unit alpha of norm n acting as lambda on G has orbit size h = ord_N(lambda) … Only the units of D_0 in {-3, -4} give finite orbits at O(1) cost …". The invariant sets are full orbits.
- **K11. B6 H-invariant rational-function census (Riemann–Roch rank, CM lattice / Hecke equidistribution).** Degree is not the cost measure; straight-line-program length is. The trivial bound deg ≥ h already holds, and the CM-lattice bound is vacuous for h ≤ √|D|. The lead's own toy search suffices.
- **K12. DiPippo–Howe Weil-polynomial counting for the ECC2K-130 Jacobian carrier (B5).** This duplicates the lead's Torelli-rarity heuristic. The toy ladder at n = 11, 13 is the right test.
- **K13. Cohen–Lenstra or Gekeler group-structure selection on prime-order curves.** E(F_p) is cyclic of prime order across the whole class. This is SO-ISO; group structure varies only with a cofactor, and that case is C3.
- **K14. Duke/CM-point equidistribution for LEAD-STR-class-group-ecdlp-bridge.** The bridge is a GGM simulation lemma, and equidistribution adds no handle.

## 6. Citations

| ref | used for | provenance |
|:--|:--|:--|
| Kohel, Shparlinski, "On exponential sums and group generators for elliptic curves over finite fields", ANTS-IV 2000, LNCS 1838, 395–404 | ψ(x(nG))·χ(nG) sum ≪ √q (Cor. 1) | retrieved (bibliographic record via search; statement as quoted in Ahmadi–Shparlinski Lemma 1; primary PDF unreachable, ECONNREFUSED) |
| Ahmadi, Shparlinski, "Exponential sums over points of elliptic curves", arXiv:1302.4210v3 | Lemma 1 (KS Cor. 1); bilinear bounds; sum-product refs | retrieved (pp. 1–4 read) |
| Springer chapter doi:10.1007/11863854_24 | multiplicative-character sums over E(F_p) points (EC-DL binary sequences) | retrieved (abstract via search only; authors unconfirmed) |
| Deligne, SGA 4½ "Sommes trig."; Weil II; Grothendieck–Ogg–Shafarevich; Bombieri 1966 "On exponential sums in finite fields" | C1-Theorem | recalled |
| Lauter, Stange, "The elliptic curve discrete logarithm problem and equivalent hard problems for elliptic divisibility sequences", SAC 2008 | K2/r_k reduction to EDS association | recalled |
| Boneh, Shparlinski, "On the unpredictability of bits of the elliptic curve Diffie–Hellman scheme", CRYPTO 2001 | completion technique (C2) | recalled |
| Mauduit, Rivat; Fouvry, Mauduit (Thue–Morse Fourier L1 ≈ N^{0.40}); Rudin–Shapiro flatness | C2 exponents (my measured values agree) | recalled; exponents measured-here |
| Kohel 1996 thesis; Miret, Moreno, Sadornil, Tena, Valls 2006 | ℓ-Sylow structure by volcano level (C3) | recalled; structure also in program records (internal) |
| research/generator_effect_ic_20261019 (E3a) README/PLAN/n0.json; crypto `exact_decomposition_ceiling`, `prime_factor_base`, `PairTable::build_negation_folded` | N0 mechanism on v1; base and table semantics | internal (read this session; reported as `retrieved` in the structured output) |

## 7. Files

All under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`:
- `scripts/miller_u_spectrum_v2.py`, `miller_u_spectrum_v2.out` (C1 toy check)
- `scripts/digit_l1.py`, `digit_l1.out` (C2)
- `scripts/volcano_kg.py`, `scripts/volcano_compare.py`, `scripts/volcano_chi2.py`, `volcano_kg_v21.json`, `volcano_compare_v21.out`, `volcano_chi2_v21.out`, `n0_identity_check.out` (C3)
- `match.out` (lead_atlas and frontier `--match` for all 9 phrasings)
