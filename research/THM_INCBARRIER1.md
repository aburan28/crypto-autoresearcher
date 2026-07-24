# THM-INCBARRIER1 — EC-chord richness ceiling: exact moments in the uniform-x model, the proved phase diagram, the AP excess family, and the character-sum barrier

**Task:** TASK-20260718-THMINC (theory track, candidate D3 proof attempt; companion to EXP-INCB-001 / EV-INCB-001, DEC-20260718-012).
**Date:** 2026-07-18. **Author:** executor (THMINC).
**Inputs read:** ledger/EV-INCB-001.yaml, EV-INC-001.yaml, DEC-20260718-012.yaml, experiments/EXP-INCB-001/analysis.md + instrument source + RUN-INCB-001-b/raw.json (read-only), research_directions_20260717.md (A2 §, D3 §).
**Verification artifact:** `research/verification/thm_incbarrier1_check.sage` → `research/verification/thm_incbarrier1_check_output.json` (231 checks, 0 failures; every formula below marked ✓ was verified exactly on all three ledger curves).
**Honesty contract:** every statement is labeled **PROVED** (full proof given or elementary derivation + exact verification), **CONJECTURE** (precise statement, no proof), **OPEN GAP** (what exactly is missing), or **HEURISTIC** (unproved estimate used only for orientation). One standard black box (the Weil bound for mixed character sums on E) is used, and only inside §5, where it is flagged; nothing else non-elementary is used anywhere. No claim here is a crypto-scale empirical claim (rule 7); the theorems are scale-free statements about an explicit random model, verified at toy scale p ∈ {211, 1009, 4099}.

---

## 0. Status summary

| # | Statement | Label |
|---|---|---|
| T1 | Richness of an EC x-set chord arrangement collapses to one number: r ≥ 4 is impossible (Bezout), c₃ = T₃, c₂ = C(M,2) − 3T₃, #lines = C(M,2) − 2T₃ | **PROVED** (§2; ✓ on all 36 recorded instances) |
| T2 | T₃(F) = 2·X(F) − Y(F): every collinear x-triple carries exactly 2 point-triples, except the Klein-four triple (z = 3 curves) which carries exactly 1 | **PROVED** (§2; ✓ 36/36 instances) |
| T3 | Full-group count: T₃^full = (n² − 6n + 5 + 3z + 2t)/6, z = #2-torsion x's, t = #order-3 points | **PROVED** (§3; ✓ vs independent enumeration, all 3 curves) |
| T4 | Uniform-x model: E[T₃] = T₃^full·(B)₃/(L)₃ and an exact closed variance; hence the **phase diagram**: B = p^α with α < 1/3 ⟹ T₃ = 0 w.h.p.; α = 1/3 ⟹ O(1) non-concentrated (Poisson regime); α ∈ (1/3, 1/2) ⟹ T₃ = μ(1+o(1)) in probability. I_EC = I_generic·(1+o(1)) in this model | **PROVED** (§3; exact moments ✓ per cell) |
| T5 | Worst case is Θ(worst-case bound): T₃(F) ≤ 2B(B−1)/3 for all F, and the group-AP family achieves T₃ = 2⌊(B−1)²/4⌋ ≈ B²/2, an excess factor ≈ 3n/(8B) over the generic mean — so the ceiling is NOT uniform over F; the excess trivializes (rank defect) | **PROVED** (§4; ✓ exact counts on all 3 curves) |
| T6 | The recorded 15–35% c₃ deficit vs the uniform-x first-moment heuristic is explained: the heuristic h = C(M,2)(B/L)/3 provably overstates the exact random-x mean by h/μ ≈ 1 + 3/B (measured 1.43/1.32/1.19/1.43/1.18/1.10 at the six cells); vs the exact mean the data sit at z ∈ [−0.58, +0.38]. A negative o-term is **not** a character-sum prediction: no sign is forced, and the provable character-sum error scale exceeds the signal by 10²–10⁴× at these sizes | **PROVED** parts (§6) + interpretation |
| T7 | Character-sum certification of the ceiling for a *fixed* F is impossible with current techniques at harvesting scales: the direct Weil/Fourier method certifies |T₃ − main| < main only for B = Ω(p); an optimistic (unproved) fourth-moment input would still cap at B ≳ p^{2/3}; harvesting needs B = p^{1/5..2/5} | **PROVED** method barrier (§5, modulo one flagged standard black box) + **OPEN GAP** G1 |
| C1 | Poisson limit at α = 1/3: T₃ ⇒ Poisson(μ), μ ≈ 4/3 | **CONJECTURE** (§8) |
| C2 | The ceiling also holds for cryptographically standard structured F (e.g., x-intervals), not only uniform-x F | **CONJECTURE** (§8; model gap, not measured here) |

Bottom line for D3: in the uniform-x model — which is *exactly* the model EXP-INCB-001 sampled — the generic ceiling is no longer toy evidence but a **theorem with an exact variance certificate** (T4). The residual genuinely open question is the fixed/adversarial-F statement, and §5 quantifies precisely why character sums cannot reach it (gap of ~p^{1/6}–p^{1/10} in the set-size exponent, depending on the method).

---

## 1. Model and notation

- E/F_p: y² = f(x) = x³ + ax + b, ordinary; n = #E(F_p); G = E(F_p).
- X_E = {x ∈ F_p : f(x) is a square, including 0}; L = |X_E|. Point count identity: n = 1 + 2L − z, where z = #{x : f(x) = 0} ∈ {0,1,3} (✓ all curves).
- t = #{P ≠ O : 3P = O} (rational order-3 points; they come in ± pairs sharing an x, so t is even).
- Factor base (A2 semantics): F ⊂ X_E, |F| = B; lift set 𝒫 = {P ∈ G : x(P) ∈ F}, M = |𝒫| = 2B − z_F, z_F = #{x ∈ F : f(x) = 0}.
- Arrangement: all lines through pairs of distinct points of 𝒫. c_r = # lines containing exactly r points of 𝒫.
- T₃(F) = #{unordered triples {P,Q,R} ⊂ 𝒫, distinct, P+Q+R = O} — the number of 3-rich chord lines (see T1).
- A *valid x-triple* is a 3-subset {x₁,x₂,x₃} ⊂ X_E with lifts P₁,P₂,P₃ (some choice of signs) summing to O. V = # valid x-triples of the full group; X(F) = # of those contained in F.
- Uniform-x model: F a uniform random B-subset of X_E. Note (verified from the instrument source, `ec_points`): EXP-INCB-001's seeded factor bases are exactly uniform B-subsets of X_E (rejection sampling of distinct lifting x's), so this model **is** the experiment's sampling model.

Ledger curves (rebuilt ✓ identical to raw.json): p=211: y²=x³+7x+62, n=210, L=105, z=1, t=2, V=3571, T₃^full=7142. p=1009: y²=x³+921x+976, n=984, L=493, z=3, t=2, V=80198, T₃^full=160395. p=4099: y²=x³+211x+1972, n=4056, L=2029, z=3, t=2, V=1368902, T₃^full=2737803.

## 2. Structural collapse of the richness profile (T1, T2) — PROVED

**P2.1 (T1, Bezout collapse).** A line in ℙ² meets the cubic E in exactly 3 points counted with multiplicity; a non-vertical line therefore contains at most 3 points of E(F_p), and a vertical line at most 2. Hence for any x-set lift set 𝒫: c_r = 0 for all r ≥ 4; every 3-rich line corresponds to exactly one unordered triple {P,Q,R} ⊂ 𝒫 with P+Q+R = O, so c₃ = T₃; and the pair-counting identity C(M,2) = Σ_lines C(r_line, 2) gives, with v = # vertical pairs (= #x ∈ F with f(x) ≠ 0) and d = # tangent-degenerate pairs ({P,−2P}, 3P ≠ O):

- c₂ = C(M,2) − 3T₃,  #lines = C(M,2) − 2T₃.

So the *entire* richness distribution of an EC x-set chord arrangement is determined by the single integer T₃; the "s-rich ceiling" question for s ≥ 4 is vacuous (proved zero), and the experiment's fitted "richness exponent" is structurally a two-point fit over (c₂, c₃). ∎
**Verification:** ✓ on all 36 recorded EC instances of RUN-INCB-001-b: max richness ≤ 3, c₃ = triples_T, and both identities hold exactly (this also renders the recorded confound about "vertical-line c₂ inflation" exact: it is the deterministic +v inside C(M,2) − 3T₃).

**P2.2 (T2, x-triple/point-triple correspondence).** For x₁ ≠ x₂, write P₁, P₂ for lifts; the four sign choices (±P₁, ±P₂) yield at most **two** third-point x-coordinates, x(P₁+P₂) and x(P₁−P₂), since (−P₁)+(−P₂) = −(P₁+P₂) and (−P₁)+P₂ = −(P₁−P₂) have the same x's. A valid x-triple {x₁,x₂,x₃} is generated by each of its 3 pairs, and:
- if no xᵢ is 2-torsion (f(xᵢ) ≠ 0): exactly **2** point-triples {P,Q,R} and {−P,−Q,−R} lie on it;
- if exactly one or two xᵢ are 2-torsion: still exactly 2 point-triples (sign choices collapse in pairs);
- if all three xᵢ are 2-torsion — possible only when z = 3, and then {x₁,x₂,x₃} is unique (the Klein-four triple): exactly **1** point-triple, since each point is its own negative.

Hence T₃(F) = 2·X(F) − Y(F), where Y(F) = 1 iff z = 3 and the Klein x-triple ⊂ F, else 0. In particular T₃(F) = (2/3)·Σ_{pairs {x₁,x₂} ⊂ F} e_F(x₁,x₂) − Y(F), with e_F ∈ {0,1,2} the number of valid third x's in F. ∎
**Verification:** ✓ Σ_pairs e = 3V at all three curves; ✓ per-instance recomputation of T₃ from the recorded x_set alone matches the recorded triples_T on 36/36 instances (including the p=1009 seed-20260721 instance containing a 2-torsion x; ✓ no instance contains the full Klein triple).

**P2.3 (deterministic worst-case bound).** Since e_F ≤ 2: T₃(F) ≤ (2/3)·2·C(B,2) = 2B(B−1)/3 for every F. ∎ (Tightness: §4 — the group-AP family attains 3/4 − o(1) of this bound.)

*Unexpected observation recorded while proving T2 (rule 8):* the first version of the verification script used the naive 2V count for T₃^full and "failed" against the closed form by exactly +1 on both z = 3 curves and 0 on the z = 1 curve — the discrepancy is exactly the Klein-four triple. The closed form (derived independently by inclusion–exclusion over ordered point pairs, which is 2-torsion-correct by construction) is the right statement; the x-triple count needs the −[z=3] correction. Also observed: pairs involving a 2-torsion x have e ≤ 1 (the two candidate slopes are ±λ with equal squares), so 2-torsion x's sit in roughly half as many valid x-triples as generic x's (measured g ≈ 245.7 vs average 488.0 at p=1009; ≈ 1013.7 vs average 2024.0 at p=4099).

## 3. Exact moments in the uniform-x model and the phase diagram (T3, T4) — PROVED

**P3.1 (T3, full-group triple count).** Let A = #ordered pairs (P,Q) ∈ G² such that P, Q, R := −P−Q are distinct and none is O; then T₃^full = A/6. Exclusion sets E1..E6 = {P=O}, {Q=O}, {P=Q}, {Q=−P}, {Q=−2P}, {P=−2Q}, each of size n. Inclusion–exclusion: pairwise intersections sum to 15 + 3z + 3t (the nine singleton intersections, the three 2-torsion families of size z+1, the three 3-torsion families of size t+1), triple intersections to 20 + t, quadruple 15, quintuple 6, sextuple 1. Hence |∪Eᵢ| = 6n − 5 − 3z − 2t and

**T₃^full = (n² − 6n + 5 + 3z + 2t)/6.**

**Verification:** ✓ equals the independent x-pair enumeration 2V − [z=3] at all three curves (7142, 160395, 2737803). ∎

**P3.2 (T4a, exact mean).** Uniform B-subset F ⊂ X_E: each valid x-triple is included with probability (B)₃/(L)₃ (falling factorials), so

**E[T₃] = T₃^full·(B)₃/(L)₃ ≈ (4/3)·B³/n·(1 + O(1/B) + O(1/n)).** ∎

**P3.3 (T4b, exact variance).** Let W₂ = #pairs of distinct valid x-triples sharing 2 x's, W₁ sharing exactly 1, W₀ sharing 0. Then W₂ = #{π : e(π) = 2} (e ≤ 2 by P2.2), W₁ = Σ_x C(g(x),2) − 2W₂ with g(x) = #valid triples containing x, W₀ = C(V,2) − W₁ − W₂, and with X = X(F):

E[X²] = V·(B)₃/(L)₃ + 2W₂·(B)₄/(L)₄ + 2W₁·(B)₅/(L)₅ + 2W₀·(B)₆/(L)₆,  Var(X) = E[X²] − E[X]²,

and Var(T₃) = 4·Var(X) exactly when z ≠ 3; when z = 3 the Klein correction T₃ = 2X − Y gives Var(T₃) = 4Var(X) − 4Cov(X,Y) + Var(Y) with the exact covariance computed from e(π), g(x) restricted to the Klein triple (formulas in the verification script; numerically negligible, ≤ 10⁻⁴ relative). ∎
**Verification:** ✓ exact per-cell values (table below). (The script's first run caught and fixed an ordered-vs-unordered pair-counting slip in E[X²]; the final values are exact Fractions, not floats.)

**P3.4 (T4c, concentration / phase diagram).** From e ≤ 2 and g(x) ≤ 2(L−1): W₂ ≤ C(L,2), W₁ ≤ L·C(2(L−1),2) = O(L³); and the W₀ term is *negative* after subtracting E[X]² ((B)₆/(L)₆ < [(B)₃/(L)₃]² since B < L), so it can be dropped for an upper bound. With V ≈ L²/3 (from P3.1):

Var(X)/E[X]² ≤ 1/E[X] + 36/B + 9/B² = O(1/μ + 1/B),  μ = E[X].

Since |T₃ − 2X| ≤ 1 pointwise (P2.2), Chebyshev gives, for B = ⌊p^α⌋, L ∼ p/2:
- **α < 1/3:** E[T₃] ≈ (4/3)p^{3α−1} → 0, so T₃ = 0 w.h.p. (Markov). **PROVED.**
- **α = 1/3:** E[T₃] → 4/3; relative variance = Ω(1): T₃ is an O(1), non-concentrated random variable (Poisson regime; see C1). **PROVED** (non-concentration).
- **α ∈ (1/3, 1/2):** E[T₃] → ∞ and relative variance → 0: **T₃(F)/μ → 1 in probability**, i.e. T₃ = μ·(1 + O_p(1/√μ + 1/√B)). **PROVED.**

**Corollary (I_EC = I_generic + o-term, in the uniform-x model).** Total incidences I_EC(F) = 2c₂ + 3c₃ = 2C(M,2) − 3T₃ (P2.1). For α ∈ (1/3, 1/2): T₃ = O_p(B³/n) = o_p(B²), so I_EC = 2C(M,2)·(1 − O_p(B/n)); the same computation for a uniform random M-point set gives I_generic = 2C(M,2)·(1 − O_p(M/p)) (its rich-line correction is ≈ 3T₃^rand with T₃^rand ≈ C(M,3)/p, the same order as the EC μ — consistent with the experiment's EC ≈ random first moments). The relative difference I_EC − I_generic is the o-term, governed entirely by T₃. **PROVED in the uniform-x model.** ∎

*Reading for harvesting (m=3):* at the supply-optimal scale B ≈ n^{1/3}, T₃ is an O(1) random variable — the 3-rich relation supply per factor base is intrinsically O(1), with an exact distribution, not merely a small mean. This quantifies A2's recorded "adverse supply arithmetic" and is the exact reason the experiment's (4099,8) cell had no fittable exponent at all.

**Exact per-cell moments vs the EXP-INCB-001 measurements (✓ script):**

| p | B | μ = E[T₃] (exact) | sd(T₃) (exact) | heuristic h | h/μ | measured mean (6 seeds) | z vs exact model |
|---|---|---|---|---|---|---|---|
| 211 | 8 | 2.1335 | 1.9003 | 3.0476 | 1.4284 | 2.000 | −0.172 |
| 1009 | 10 | 0.9697 | 1.3606 | 1.2847 | 1.3248 | 1.000 | +0.055 |
| 1009 | 16 | 4.5252 | 2.8865 | 5.3645 | 1.1858 | 4.000 | −0.446 |
| 4099 | 8 | 0.1103 | 0.4677 | 0.1577 | 1.4300 | 0.000 | −0.578 |
| 4099 | 16 | 1.1029 | 1.4703 | 1.3038 | 1.1821 | 1.333 | +0.384 |
| 4099 | 28 | 6.4520 | 3.5249 | 7.0829 | 1.0979 | 6.000 | −0.314 |

All six 6-seed means lie within ±0.6 exact-model standard errors of μ. (z uses SE = sd/√6; the seeds are independent uniform-x draws, so the exact model applies to the mean directly.)

## 4. The group-AP excess family (T5) — PROVED

**P4.1.** Let P₀ ∈ G have order ord, and 3B < ord. Let F = {x(iP₀) : 1 ≤ i ≤ B} (the x's are distinct since i < ord/2). Valid x-triples in F ↔ unordered {i,j} with 1 ≤ i < j, i + j ≤ B (the sign conditions ±i ± j ± k ≡ 0 (mod ord) reduce to i + j = k because |±i ± j ± k| < 3B < ord). Hence

**T₃(F_AP) = 2·⌊(B−1)²/4⌋ = B²/2 + O(B),**

versus the generic mean μ ≈ (4/3)B³/n: an **excess factor ≈ 3n/(8B)**, e.g. ≈ (3/4)n^{2/3} at B = n^{1/3}. Comparison with P2.3: T₃(F_AP)/[2B(B−1)/3] → 3/4 — the worst-case bound is attained up to the constant 3/4. ∎
**Verification:** ✓ exact equality T₃ = 2⌊(B−1)²/4⌋ on all three curves with a point of order > 3B+3 (p=211, B′=8, ord=42: T₃ = 24; p=1009, B′=16, ord=164: T₃ = 112; p=4099, B′=28, ord=507: T₃ = 364); measured excess factors 11.2 / 24.8 / 56.4 over the exact generic mean at the same B.

**Consequences (honest, two-sided):**
1. The "ceiling" is **not uniform over F**: structured factor bases provably violate it by a factor Θ(n/B). The experiment's grid positive control (c₃ up to 80) is the same phenomenon.
2. The excess **trivializes**: on a group-AP factor base every element's discrete log is a known multiple of log P₀, so the relation lattice collapses (rank defect); the excess carries no harvesting value. Any useful excess theorem must therefore be restricted to "log-independent" F — and certifying *that* is exactly the character-sum problem of §5.
3. What the barrier can legitimately claim is the average-case/concentration statement of §3 (now proved in the uniform-x model), not a worst-case statement.

## 5. The character-sum attack and its exact barrier (T7) — PROVED method barrier + OPEN GAP

**P5.1 (exact Fourier identity).** Let ψ range over the additive characters of F_p, F̂(ψ) = Σ_{u∈F} ψ(u) (so |F̂(ψ₀)| = B, Σ_ψ|F̂(ψ)|² = pB). Let S = Σ_{(P,Q)∈𝒫², P≠Q} 1_F(x(P+Q)). Counting gives S = 6T₃ + 2d (d = # tangent-degenerate unordered pairs as in §2); Fourier inversion gives S = M(M−1)·B/p + (1/p)·Σ_{ψ≠ψ₀} F̂(ψ)·U(ψ) with U(ψ) = Σ_{(P,Q)∈𝒫², P≠Q} ψ(−x(P+Q)). Hence the **exact** identity

T₃ = [M(M−1)B/(6p) − d/3] + (1/(6p))·Σ_{ψ≠ψ₀} F̂(ψ)·U(ψ).  ∎

Note the framing consequence: averaging this identity over uniform F must reproduce P3.2's μ ≈ (4/3)B³/n ≈ **twice** the bracketed p-main-term — so the ψ≠0 sum is *typically as large as the p-main-term itself* (it carries the X_E-support conditioning). "Small error term" is provably the wrong frame; the error term is where the number theory lives.

**P5.2 (non-separability lemma).** For ψ ≠ ψ₀ over a **prime** field, U(ψ) does not factor: there are no functions g, h on G with ψ(x(P+Q)) = g(P)h(Q) for all P ≠ Q. *Proof:* the addition law gives x(P+Q) = λ² − x_P − x_Q with λ = (y_Q−y_P)/(x_Q−x_P). If such a factorization existed, then for fixed Q₁ ≠ ±Q₂ the quotient ψ(x(P+Q₁) − x(P+Q₂)) would be constant in P (where defined); over F_p a nontrivial additive character is injective, so x(P+Q₁) − x(P+Q₂) would be constant in P — but as P → −Q₁ the first term has a pole and the second is finite. ∎ So single-sum Weil bounds cannot reach U(ψ); bilinear machinery is forced.

**P5.3 (the Weil-scale bound and why it is vacuous).** Complete over G: 1_𝒫 = Σ_ρ a(ρ)ρ with Σ_ρ|a(ρ)|² = M/n. Substituting and using Σ_P ρ(P)σ(−P) = n·[ρ=σ]:

U(ψ) = n·Σ_σ a(σ)²·W(ψ,σ),   W(ψ,σ) = Σ_{Q∈G} σ(Q)·ψ(−x(Q)).

**Black box (the only non-elementary input in this note, flagged):** the Weil/Deligne bound for mixed character sums on E gives |W(ψ,σ)| ≤ 2√p for ψ ≠ ψ₀ (standard genus-1 constant; not re-derived here). Then |U(ψ)| ≤ n·(M/n)·2√p = 2M√p, and with Σ_{ψ≠ψ₀}|F̂(ψ)| ≤ p√B (Cauchy–Schwarz + Parseval):

**|T₃ − [M(M−1)B/(6p) − d/3]| ≤ M√(pB)/3.**  **PROVED** (modulo the flagged black box).

Compare with the signal μ ≈ (4/3)B³/n: the bound certifies |error| < signal only when B ≳ (n√p/2)^{2/3} ≈ 0.63·p. Per-cell provable error scale vs signal (✓ script): **102.7×, 690.6×, 299.5×, 8756.8×, 2476.8×, 980.1×** at the six toy cells — the certificate is vacuous by 2–4 orders of magnitude. At the harvesting regime B = p^{1/5..2/5} the gap is a power of p. ∎

**P5.4 (even optimistic improvements stay short).** *HEURISTIC (unproved):* if one could prove the expected fourth-moment scale Σ_{ψ≠ψ₀}|U(ψ)|⁴ = O(M⁴ + pM³) (the diagonal count of x-additive quadruples — in principle combinatorially computable like §3's W's, but with a geometric diagonal term we did not control), Hölder would give |error| ≲ p^{1/2}M^{3/4}·B-scale and the certification threshold would improve only to B ≳ p^{2/3}. Published bilinear-sum bounds on elliptic curves (Ahmadi–Shparlinski line, as catalogued in research_directions_20260717.md:151,707 — *venue unverified in the repo; treated as recollection*) operate at set sizes ≳ p^{1/2+ε}. All routes stop at least a p^{1/10}-factor (and up to p^{1/6}) above the harvesting regime in the set-size exponent.

**OPEN GAP G1 (precise).** Prove or disprove: for B = ⌊p^α⌋, α ∈ (0, 1/2), and *every* (or even: uniform random) F ⊂ X_E with the log-independence property excluded in §4, |T₃(F) − μ| = o(μ) as p → ∞. By P5.1–P5.3 this requires a bound on (1/p)Σ_{ψ≠0}F̂(ψ)U(ψ) beating the Weil scale by a factor ≫ p^{1/2−α+δ} on average over ψ — i.e., cancellation *across* characters, or fourth/higher moments of U with diagonal control — no known technique reaches α ≤ 1/2 for this bilinear form. This is the exact point where the proof of a fixed-F ceiling theorem is blocked.

## 6. The recorded 15–35% c₃ deficit: resolution (T6) — PROVED + interpretation

DEC-20260718-012 recorded (rule 8): "EC c3 runs 15–35% below the uniform-x first-moment prediction at all fittable cells (~2 SE, unexplained)", and asked whether a negative o-term is the expected character-sum behavior at these sizes.

**P6.1 (the heuristic provably overstates the exact mean).** The instrument's per-instance prediction is h = C(M,2)·(B/L)/3 (pair count × x-density ÷ 3 — a with-replacement approximation). The exact uniform-x mean (P3.2) is μ = T₃^full·(B)₃/(L)₃. Their ratio is exact arithmetic:

h/μ = B(2B−1)·(L−1)(L−2) / [3·T₃^full·(B−1)(B−2)] ≈ B(2B−1)/[2(B−1)(B−2)] ≈ 1 + 3/B + O(1/B² + 1/n),

i.e. h overstates μ by ≈ +43% (B=8), +32% (B=10), +19% (B=16), +10% (B=28) — the same sign and essentially the same magnitude as the recorded deficit. Measured exact values (✓ script): 1.4284, 1.3248, 1.1858, 1.4300, 1.1821, 1.0979. Two proved sources inside the correction: (i) C(2B,2) counts the vertical pairs and tangent-degenerate pairs that can never generate a 3-rich line (P2.1's v and d); (ii) the with-replacement pair count vs the hypergeometric (B)₃/(L)₃. ∎

**P6.2 (residual vs the exact mean is noise).** Replacing h by the exact μ, the six measured 6-seed means sit at z = −0.172, +0.055, −0.446, −0.578, +0.384, −0.314 (exact-model SEs, table in §3): |z| < 0.6 everywhere, mixed signs (3 negative, 2 positive, 1 near 0). Nothing systematic survives the correction. ∎

**Answer to the coordinator's question.** No — a negative o-term is *not* the expected character-sum behavior at these sizes, for three independent reasons:
1. **No sign is forced.** The character-sum term in P5.1 is a signed sum of ~p terms; general theory (P5.3) bounds its modulus but predicts no definite sign. A *systematic* negative bias would itself have been a structure claim requiring proof.
2. **No character-sum effect of either sign is resolvable at these sizes.** The provable error scale exceeds the signal by factors 10²–10⁴ (per-cell table in §5); any character-sum contribution is far below the noise floor of provable analysis and of the measurements.
3. **The observed deficit is fully accounted for without character sums**: the proved finite-B correction P6.1 (factor h/μ) plus exact-model fluctuation P6.2.

*Precision note (honesty, rule 9):* the EV/analysis phrase "below at all fittable cells, 0.66–0.85" is slightly imprecise on the recorded numbers themselves: recomputed per-cell ratios measured/h are {0.656, 0.778, 0.746, 0.0, **1.023**, 0.847} — the (4099,16) cell is marginally *above* the heuristic (1.333 vs 1.3038). The systematic-below reading holds in 4 of 5 nonzero cells and was within ~2 SE individually; the exact-model analysis above supersedes it.

## 7. What this means for D3 (and A2)

- The uniform-x model is exactly the experiment's sampling model, so T4 **upgrades the toy ceiling evidence to a proved in-model theorem**: for uniform-x factor bases with B = p^α, α ∈ (1/3, 1/2), the 3-rich chord supply concentrates at the generic mean with an exact variance certificate; for α ≤ 1/3 it is O(1)/zero w.h.p. There is no excess harvesting channel in this model at any scale (T4 + P2.1: s ≥ 4 channels are identically zero).
- The worst case is genuinely richer (T5, factor Θ(n/B)) but provably trivializing; an "excess opening" would have to live on log-independent structured F, which is exactly where character sums are needed — and where they are provably (today) powerless (T7/G1).
- For A2: relation supply from 3-rich chords at B ≈ n^{1/3} is an O(1) Poisson-regime variable per factor base; the supply arithmetic recorded in A2's cost model is now backed by an exact distribution, not a heuristic mean.

## 8. Conjectures and open gaps (precise)

- **C1 (CONJECTURE).** At B = ⌊p^{1/3}⌋ (more generally B³/n → λ), T₃(F) converges in distribution to Poisson with mean T₃^full·(B)₃/(L)₃ (→ 4λ/3·…). The moment machinery of §3 extends in principle (higher W-analogues); not carried out here.
- **C2 (CONJECTURE).** The ceiling also holds for standard structured factor bases (x-intervals with the lifting filter, pseudorandom x-sets), i.e. C2 = "G1 is true for the sets index calculus actually uses." No measurement of interval-type F was in scope; the experiment sampled uniform-x F only.
- **G1 (OPEN GAP).** Fixed-F ceiling at B = p^α, α ≤ 1/2 — blocked at exactly the cross-character cancellation of §5 (quantified: need to beat 2M√p per-character Weil scale by ≫ p^{1/2−α+δ} on average over ψ, or control higher moments of U with geometric diagonals).
- **G2 (OPEN GAP, smaller).** Exact worst-case constant: T₃(F) ≤ 2B(B−1)/3 proved; group-AP achieves 3/4 of it asymptotically. The true maximum over F is undetermined (constant between 3/4 and 1).
- **G3 (OPEN GAP, methodological).** The fourth moment Σ|U(ψ)|⁴ (x-additive quadruples on E) — a clean combinatorial-geometric count whose diagonal term we did not control; a bound of the expected shape would push the certified range to B ≳ p^{2/3} (still short of harvesting).

## 9. Verification appendix

- Script: `research/verification/thm_incbarrier1_check.sage` (sage, deterministic; wall ≈ 3 min; single run after two debug iterations of the script itself — no experiment directories touched, no ledger writes).
- Output: `research/verification/thm_incbarrier1_check_output.json` — **231 checks, 0 failures**, including: curve rebuild == recorded curves (3/3); group-count identity n = 1+2L−z (3/3); Σe = 3V (3/3); T₃^full closed form == Klein-corrected enumeration (3/3); Bezout r ≤ 3, #lines/c₂/c₃ identities, and independent T₃ recomputation from recorded x-sets (36/36 instances × 5 checks); Klein-triple absence from every recorded factor base; AP build and AP closed count (2⌊(B′−1)²/4⌋) exact on all three curves.
- The two intermediate script "failures" that led to the Klein-four discovery are recorded in §2 (rule 8); the ordered/unordered variance slip found and fixed during the same verification is recorded in §3 (script-internal, pre-delivery; no impact on any external record).

## 10. Boundaries and honesty

- Toy-scale verification (p ≤ 2^12) anchors every ✓; the theorems are stated and proved for general p, B in the uniform-x model, but no crypto-scale empirical claim is made (rule 7).
- The single non-elementary input (Weil bound for mixed sums, |W(ψ,σ)| ≤ 2√p) is used only in §5's method-barrier statement and is flagged there; everything else is elementary.
- Literature references are as catalogued in research_directions_20260717.md:151,707 (Stevens–de Zeeuw arXiv:1609.06284; Vinh 2011; Bourgain–Katz–Tao 2004; Rudnev 2018; Iosevich et al. arXiv:2303.00330; Ahmadi–Shparlinski, venue unverified); no venues beyond the repo's own catalog are asserted.
- Nothing here is evidence about crypto-scale ECDLP; G1 states exactly what a crypto-scale-relevant theorem would require.
