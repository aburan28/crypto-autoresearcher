# THM-INCBARRIER2 — The chord-profile identity, the energy certificate, the norm-ladder to α = 1/2, and the exact cross-cancellation barrier

**Task:** TASK-20260724-LEMINC (theory track, attack on THM_INCBARRIER1 §8 OPEN GAP G1: fixed/adversarial-F richness certification at B = p^α, α ≤ 1/2).
**Date:** 2026-07-24. **Author:** executor (LEMINC).
**Inputs read:** research/THM_INCBARRIER1.md (esp. §5, §8 G1/G3), ledger/DEC-20260722-006.yaml, research/verification/thm_incbarrier1_check.sage (reused primitives, read-only).
**Verification artifact:** `research/verification/thm_incbarrier2_check.py` → `research/verification/thm_incbarrier2_check_output.json` (**148 checks, 0 failures**; pure Python + numpy, deterministic, wall < 1 s; every formula marked ✓ verified exactly on all three ledger curves; toy scale p ∈ {211, 1009, 4099}, rule 7 applies — no crypto-scale empirical claim).
**Honesty contract:** identical to THM_INCBARRIER1 — every statement labeled **PROVED** / **CONJECTURE** / **OPEN GAP** / **HEURISTIC**. Unlike THM1 §5, the main results here use **no black box at all**: the Weil bound is not used anywhere in this note (it appears only as a comparison baseline and in one numerical consistency check). All theorem statements are scale-free; all ✓ checks are toy-scale.

---

## 0. Status summary

| # | Statement | Label |
|---|---|---|
| A1 | Chord profile r(x) and the exact identity S = Σ_{x∈F} r(x) = 6T₃ + 2d (d = tangent-degenerate pairs) | **PROVED** (§2; ✓ 21/21 factor bases incl. AP) |
| A2 | Profile identity: T₃(F) = μ̃ + (1/6)·Σ_{x∈F} δ(x), μ̃ = BT/(6L) − d/3, δ = r − r̄ | **PROVED** (§2; ✓ 21/21, exact Fractions) |
| A3 | Second moment: N₂ = Σ_x r(x)² = 2E₁ − Σ_{g∈G[2]∖{O}} A'(g)² (E₁ = restricted additive energy; the 2-torsion correction was **discovered by a verification failure**, §8) | **PROVED** (§2; ✓ 21/21) |
| A4 | **Energy certificate (deterministic, per-instance, black-box-free):** \|T₃(F) − μ̃\| ≤ (1/6)·√(B·Ñ₂), Ñ₂ = N₂ − T²/L = \\|δ\\|₂². Trivial energy E₁ ≤ M³ recovers exactly the worst-case scale (2/3)B²; flat energy (Ñ₂ ≤ cM²) gives (√c/3)·B^{3/2} | **PROVED** (§2; ✓ 21/21) |
| A5 | The certificate **never loses** to THM1's Weil bound (Ñ₂ ≤ 2M³ ≤ 4pM² unconditionally), and beats it by Θ(√p) whenever the profile is flat; measured cert/Weil ∈ [0.003, 0.13] on 21 instances | **PROVED** (§2) + ✓ |
| B | **Norm ladder:** under the profile-moment hypothesis H(k): \\|δ\\|_{2k}^{2k} ≤ C_k·M^{2k}/L^{k−1}, certification T₃ = μ̃(1+o(1)) holds for B/L^{(k+1)/(2k+1)} → ∞, i.e. α > (k+1)/(2k+1): k=1 → **2/3**, k=2 → **3/5**, k→∞ → **1/2** | **PROVED implication** (§3) |
| C | **Ceiling of the entire norm/moment family: α = 1/2.** At B = ⌊p^{1/2}⌋ the target \|Σ_F δ\| = o(√p) is below every norm scale: L²-Cauchy–Schwarz and every Hölder rung give Θ(p^{3/4}), the k→∞ ladder limit is exactly α = 1/2, and the sup-norm bound is ≥ c·√p since \\|δ\\|_∞ ≥ \\|δ\\|₂/√L = Θ(1). Below α = 1/2 every norm bound fails polynomially. Cross-x sign cancellation of δ on F is *necessary*, not just sufficient | **PROVED method barrier** (§3) |
| D | The group-AP family saturates the certificate: Ñ₂(AP) = (32/3)B³ + O(B² + B⁴/L), and certificate/deviation → 8/(3√6) ≈ 1.089 as B → ∞ (tightness → 3√6/8 ≈ 0.919; measured 0.84 → 0.90 increasing at B = 8/16/28) | **PROVED** (§4) + ✓ |
| E | Unconditional character-sum lower bounds: Σ_{ψ≠0}\|U(ψ)\|² ≥ T²(p−L)/L = M⁴(1+o(1)); max_{ψ≠0}\|U(ψ)\| ≥ T·√((p−L)/(L(p−1))) ≈ M²/√p; Σ_{ψ≠0}\|U\|^{2k} ≥ (T²(p−L)/L)^k/(p−1)^{k−1} | **PROVED** (§3; ✓ k = 1, 2) |
| F | Formalization of the needed cancellation, three equivalent forms + the θ-quality scale: a bilinear bound \|Σ_{ψ≠0} F̂(ψ)Û(ψ)\| = O(p^{1−θ}B^{3/2+o(1)}) certifies α > (2−2θ)/3. Harvesting (α ∈ [1/5, 2/5]) needs θ ∈ [2/5, 7/10]; per-character Weil is θ = −1/2; Parseval+flatness is θ = 0 | **PROVED** equivalences (§5) |
| C1 | Uniform-x profile flatness: Ñ₂ = Θ(M²) w.h.p. (measured Ñ₂/M² ∈ [2.51, 4.26] on 18 uniform-x instances); same for H(2) with a decreasing trend in λ = M²/L (measured \\|δ\\|₄⁴/(M⁴/L) ∈ [16, 608]) | **CONJECTURE** (§6; toy-scale evidence) |
| C2 | The x-side (profile) route strictly dominates the character-side route of THM1 §5 for this problem — exact centering, no black box, sharper bound | **PROVED** (as comparison of proved bounds, §2–3) |

**Bottom line for G1:** the fixed/adversarial-F question is *exactly* the statement that the centered chord profile δ has small bias on its own generating set (§2). The moment/norm family — which THM1 §5.4 conjectured to cap at p^{2/3} via character fourth moments — in fact ladders on the **x-side** all the way to **α = 1/2** (Theorem B), and provably cannot cross it (Theorem C). What remains for α ≤ 1/2 is a single, precisely quantified cancellation statement (Theorem F); the exact inputs that would close it are named in §5.3.

---

## 1. Setup and notation

As in THM_INCBARRIER1 §1: E/F_p: y² = f(x) = x³ + ax + b, ordinary; n = #E(F_p); X_E = {x : f(x) square or 0}, L = |X_E|, n = 1 + 2L − z; F ⊂ X_E, |F| = B; 𝒫 = {P : x(P) ∈ F} (x-saturated by construction), M = |𝒫| = 2B − z_F.

**New definitions (the chord profile):**

- r(x) = #{(P,Q) ∈ 𝒫² : P ≠ Q, P + Q ≠ O, x(P+Q) = x}, for x ∈ X_E (r := 0 outside X_E).
- T = Σ_x r(x) (total mass); r̄ = T/L; δ(x) = r(x) − r̄ (centered profile).
- N₂ = Σ_x r(x)²; Ñ₂ = N₂ − T²/L = Σ_x δ(x)² = \\|δ\\|₂².
- A'(g) = #{(P,Q) ∈ 𝒫² : P ≠ Q, P + Q = g} for g ∈ G ∖ {O}; E₁ = Σ_{g≠O} A'(g)² (restricted additive energy: quadruples (P,Q,P',Q'), P≠Q, P'≠Q', with P+Q = P'+Q' ≠ O).
- d = #{unordered pairs {P,−2P} ⊂ 𝒫, 3P ≠ O} (tangent-degenerate pairs; note {P,−2P} is counted whenever both points lie in 𝒫 regardless of labeling — see §8 for a counter bug this note's verification caught).
- U(ψ) = Σ_{(P,Q) ∈ 𝒫², P≠Q, P+Q≠O} ψ(−x(P+Q)) for additive characters ψ of F_p (THM1's convention, with vertical pairs excluded — a convention difference from THM1 §5.1 that does not affect any bound there; recorded per rule 9).

**P1.0 (mass formula, PROVED, ✓ 21/21).** T = M(M−1) − 2(B − z_F). *Proof:* ordered pairs (P,Q), P≠Q: M(M−1); those with P+Q = O are exactly the vertical pairs (P,−P), P ≠ −P: 2(B − z_F) of them. ∎

## 2. The profile identity and the energy certificate (mission part (a))

**P2.1 (A1, PROVED).** S := Σ_{x∈F} r(x) = 6T₃ + 2d.
*Proof.* If (P,Q) is ordered with x(P+Q) ∈ F, then R := P+Q ≠ O and −R ∈ 𝒫 (x-saturation). Either −R ∉ {P,Q}: then {P,Q,−R} is a 3-rich triple, and each unordered triple contributes exactly its 6 ordered pairs; or −R = P (⇔ Q = −2P, 3P ≠ O): the tangent-degenerate pairs, each contributing exactly its 2 orderings. Both cases are disjoint and exhaustive. ∎ ✓ 21/21 factor bases (18 uniform-x + 3 AP), including instances with d > 0 and with a 2-torsion x ∈ F.

**P2.2 (A2, the exact profile identity, PROVED).** With μ̃ := BT/(6L) − d/3,
T₃(F) = μ̃ + (1/6)·Σ_{x∈F} δ(x).
*Proof.* T₃ = S/6 − d/3 (P2.1) and S = Σ_F (r̄ + δ) = B·r̄ + Σ_F δ = BT/L + Σ_F δ. ∎ ✓ 21/21, exact.
*Centering note:* μ̃ is the *correct* main term per instance — it absorbs exactly the X_E-support conditioning that THM1 §5.1 flagged ("the ψ≠0 sum is typically as large as the p-main-term itself"). Comparison with THM1's uniform-x mean μ = T₃^full(B)₃/(L)₃: averaging P2.2 over uniform F gives μ = μ̃ + (d − E[d])/3, so |μ − μ̃| = O(d) with d ≤ B exactly computable in O(M) time per instance (E[d] ≈ 2B²/L — HEURISTIC). For α > 1/2 this discrepancy is o(μ) automatically; at α ≤ 1/2 it is part of the adversarial richness itself (structured F can have d = Θ(B)).

**P2.3 (A3, second moment, PROVED).** A' is even: A'(−g) = A'(g) for all g ≠ O (the involution (P,Q) ↦ (−P,−Q) is a bijection on the counted pairs, since 𝒫 = −𝒫). Hence r(x) = A'(g) + A'(−g) = 2A'(g) whenever x(g) = x with g ≠ −g; but the fiber over a 2-torsion point is a singleton: if 2g = O, g ≠ O, then g = −g and r(x(g)) = A'(g). Therefore
N₂ = 2E₁ − Σ_{g ∈ G[2] ∖ {O}} A'(g)². ∎
✓ 21/21 — the correction term was **discovered** when the naive identity N₂ = 2E₁ failed by exactly 16 = 4² = A'(g)² on instance (4099, 28, s=99) (one 2-torsion g with A'(g) = 4); §8 records this per rule 8, mirroring THM1's Klein-four discovery.

**P2.4 (A4, the energy certificate, PROVED).** For every factor base F:
|T₃(F) − μ̃| ≤ (1/6)·√(B·Ñ₂) ≤ (1/6)·√(2B·E₁).
*Proof.* |Σ_{x∈F} δ(x)| ≤ √B·(Σ_{x∈F} δ²)^{1/2} ≤ √B·\\|δ\\|₂ (Cauchy–Schwarz over F ⊂ X_E); Ñ₂ = \\|δ\\|₂² = N₂ − T²/L (expanding δ = r − r̄); Ñ₂ ≤ N₂ ≤ 2E₁ (P2.3). ∎ ✓ 21/21 (measured tightness: uniform-x 0.003–0.13; AP 0.84–0.90, §4).

**P2.5 (properties, PROVED).**
(i) *Worst case recovered exactly:* A'(g) ≤ M for each g (Q = g − P is determined by P), so E₁ ≤ M·T ≤ M³ and the certificate gives |T₃ − μ̃| ≤ (1/6)√(2B·M³) = (1/6)·4B²·(1+o(1)) = (2/3)B²(1+o(1)) — the leading term of THM1's proved worst-case bound 2B(B−1)/3. The certificate thus *interpolates* between the worst case (energy Θ(M³)) and the generic case (energy O(M²)).
(ii) *Never worse than Weil (unconditional):* THM1 P5.3 gave |T₃ − [M(M−1)B/(6p) − d/3]| ≤ M√(pB)/3 (black box). Our certificate satisfies Ñ₂ ≤ 2M³ ≤ 4pM² (since M ≤ n ≤ 2p for p ≥ 7), hence (1/6)√(B·Ñ₂) ≤ (1/3)M√(pB): the certificate is *never worse*, is elementary (no black box), and centers at the correct μ̃ rather than the p-uniform main term (which misses the X_E conditioning by ≈ μ itself). Under flatness (Ñ₂ = O(M²)) the certificate is sharper by Θ(√p). Measured cert/Weil: 0.014–0.071 (uniform-x), 0.064–0.13 (AP). ✓
(iii) *Certificate threshold:* with Ñ₂ ≤ c·M², |T₃ − μ̃| ≤ (√c/3)B^{3/2}(1+o(1)), which is o(μ̃) iff B/L^{2/3} → ∞ — **certification for α > 2/3**. Constants: at B = K·L^{2/3} the error ratio is ≈ √c/(2K^{3/2}), below 1 iff K > (c/4)^{1/3} ≈ 0.96 at the measured c ≈ 3.5 — so the certificate is already nontrivial marginally below B = L^{2/3} and genuinely sharp only in the regime B/L^{2/3} → ∞.

**P2.6 (the three equivalent forms of the needed cancellation, PROVED equivalences).** For B = ⌊p^α⌋, α ∈ (0,1), the following are the same statement up to the proved identities:
(i) *profile form:* Σ_{x∈F} δ(x) = o(B³/p) [the exact deviation 6(T₃ − μ̃)];
(ii) *character form:* Σ_{ψ≠0} F̂(ψ)Û(ψ) = o(B³), where Û is U recentered (Fourier transform of δ on X_E);
(iii) *certificate-sufficiency form:* Ñ₂ = o(B⁵/p²) [from P2.4: (1/36)B·Ñ₂ = o(B⁶/p²)].
Form (iii) shows exactly why the L² certificate dies at α = 1/2: it would require Ñ₂ = o(p^{1/2}) while Ñ₂ = Θ(M²) = Θ(p) on any flat instance — off by Θ(√p). ∎

## 3. The norm ladder and its exact ceiling at α = 1/2 (mission part (b))

**P3.1 (B, the ladder theorem, PROVED implication).** Suppose the factor base F satisfies the profile-moment hypothesis
H(k): \\|δ\\|_{2k}^{2k} = Σ_{x∈X_E} δ(x)^{2k} ≤ C_k·M^{2k}/L^{k−1}  (k ≥ 1).
Then |T₃(F) − μ̃| ≤ (C_k^{1/(2k)}/3)·B^{2−1/(2k)}/L^{(k−1)/(2k)}·(1+o(1)), and consequently T₃ = μ̃(1+o(1)) whenever B/L^{(k+1)/(2k+1)} → ∞; in exponent form: **H(k) certifies α > (k+1)/(2k+1).**
*Proof.* Hölder over the support F: |Σ_F δ| ≤ |F|^{1−1/(2k)}·\\|δ\\|_{2k} ≤ B^{1−1/(2k)}·C_k^{1/(2k)}·M/L^{(k−1)/(2k)}; divide by 6 (P2.2) and compare with μ̃ ≈ (2/3)B³/L: ratio = Θ(B^{−1−1/(2k)}·L^{(k+1)/(2k)}), which is o(1) iff B^{(2k+1)/(2k)} ≫ L^{(k+1)/(2k)} iff B ≫ L^{(k+1)/(2k+1)}. ∎
The ladder: k = 1 → α > 2/3 (H(1) is exactly energy flatness Ñ₂ = O(M²) — P2.5(iii)); k = 2 → α > 3/5; k = 3 → 4/7; k → ∞ → **α > 1/2**.
*Remark (x-side vs character-side):* THM1 §5.4's "optimistic fourth moment caps at p^{2/3}" was the *character-side* fourth moment (Hölder pair (4/3, 4) against F̂, whose support is spread over all p characters, costing a factor p^{3/4}B^{1/2}). Working on the **x-side** — where the support F is *known* — the same k = 2 hypothesis costs only B^{3/4}, and yields 3/5 instead. The x-side ladder strictly dominates the character-side ladder for every k. **PROVED** (as a comparison of the two proved bounds).

**P3.2 (E, unconditional lower bounds, PROVED, ✓).** For every factor base:
(i) Σ_{ψ≠0} |U(ψ)|² = pN₂ − T² ≥ T²(p−L)/L = M⁴(1+o(1)) (Parseval + convexity of N₂ over the support X_E; measured ratio to the bound: 6.6 at (4099,28) — the bound is correct but not tight).
(ii) max_{ψ≠0} |U(ψ)| ≥ T·√((p−L)/(L(p−1))) ≈ M²/√p — compare the Weil scale 2M√p (THM1's flagged black box): the window [M²/√p, 2M√p] for the maximal character sum is unconditional on the left. Measured: max|U| = 366 at (4099,28), lower bound 123, Weil scale 7171.
(iii) Σ_{ψ≠0} |U(ψ)|^{2k} ≥ (Σ_{ψ≠0}|U|²)^k/(p−1)^{k−1} ≥ (T²(p−L)/L)^k/(p−1)^{k−1} = M^{4k}/p^{k−1}·(1+o(1)) (power mean). ✓ k = 1, 2 numerically.
*Consequence:* the aggregate of the character sums is *forced* to be large; any certification must come from how F̂ correlates with U, i.e. from cross-character structure — no per-character improvement alone can suffice.

**P3.3 (C, the ceiling of the norm family, PROVED method barrier).**
(i) *The ladder limit is 1/2:* (k+1)/(2k+1) ↓ 1/2 as k → ∞, so even H(k) for all k (a sub-Gaussian profile) certifies only α > 1/2.
(ii) *Every norm bound fails at α = 1/2:* at B = ⌊p^{1/2}⌋ the certification target is |Σ_F δ| = o(B³/p) = o(√p). But on any instance with a flat profile (Ñ₂ = Θ(M²)): L²-CS gives √B·\\|δ\\|₂ = Θ(p^{3/4}); substituting B = p^{1/2} into the rung-k bound gives the *same* scale Θ(p^{3/4}) for every fixed k; and the sup-norm bound |Σ_F δ| ≤ B·\\|δ\\|_∞ satisfies \\|δ\\|_∞ ≥ \\|δ\\|₂/√L = √(Ñ₂/L) = Θ(1) (numerically ≈ √28 ≈ 5.3 at the measured constants), so it is ≥ c·√p — already above the target o(√p). Hence **no bound of the form |Σ_F δ| ≤ \\|1_F\\|_q·\\|δ\\|_{q'} (any q, q') can certify α = 1/2 or below**, on any instance whose profile has the flat/Gaussian moment scales (conjecturally all uniform-x instances; the failure of the *bounds* is unconditional given those scales).
(iii) *What remains is exactly sign cancellation:* the residual statement CC(α) for α ≤ 1/2 (P2.6(i)) is a signed-cancellation statement of δ on its own generating set F. ∎

*Observation (recorded, rule 8):* the character-side fourth moment additionally fights a near-total cancellation: at (4099,28), p·E_x = 8.55e13 vs U(ψ₀)⁴ = 8.37e13 — the nontrivial Σ_{ψ≠0}|U|⁴ is only ≈ 2% of p·E_x. On the x-side the centering r̄ is exact (rational), not mod-p-cancellative; this is a second quantitative reason the profile route dominates.

## 4. Tightness on the extremal family (mission part (c) — why the energy restriction is essential)

**P4.1 (D, PROVED + ✓).** For the group-AP factor base of THM1 §4 (F = {x(iP₀) : 1 ≤ i ≤ B}, ord(P₀) > 3B, so 𝒫 = {±iP₀} ≅ ±[1,B] ⊂ Z/ord):
(i) E(±[1,B]) = 16B³/3 + O(B²) (elementary: r_AP(s) = 2B+1−|s| on [−2B,2B], Σ_s r_AP(s)² = (2B+1)(8B²+8B+3)/3; removing 0 and the diagonal/vertical terms costs O(B²)); hence Ñ₂ = 2E₁ − T²/L = **32B³/3 + O(B² + B⁴/L)** = Θ(M³) — the energy is *maximal* in order. Measured Ñ₂/M³: 0.883, 1.099, 1.204 at B = 8/16/28 (approaching (32/3)/8 = 4/3). ✓
(ii) The certificate evaluates to (1/6)√(32/3)·B²(1+o(1)) ≈ 0.544B², against the proved deviation T₃ − μ̃ = B²/2 + O(B + B³/p): **certificate/deviation → 8/(3√6) ≈ 1.089** (tightness → 3√6/8 ≈ 0.919). Measured tightness: 0.840, 0.886, 0.904 — increasing toward the proved limit. ✓
(iii) *Consequence (PROVED):* as a function of the energy, the L² certificate is tight up to the constant 8/(3√6): no bound using only (B, Ñ₂) can improve on it by more than ≈ 9%. Therefore any certification below the worst case *must* restrict the energy (or higher profile moments), and the "log-independence" restriction of THM1 §4 must act *through* profile flatness. Whether log-independence ⇒ flatness is itself provable is OPEN (G4); note the naive route fails: small doubling (large energy) places 𝒫 in an approximate subgroup/AP (Freiman-type structure — HEURISTIC recollection, not re-derived), which plausibly correlates with dlog-collapse, but no implication in either direction is proved.

## 5. Formalization of the needed cancellation and the exact closing inputs (mission parts (a) and (d))

**P5.1 (F, the θ-quality scale, PROVED).** Suppose a bilinear bound of the shape
BIL(θ): |Σ_{ψ≠0} F̂(ψ)·Û(ψ)| ≤ C·p^{1−θ}·B^{3/2}·(log p)^{O(1)}
holds for the factor base F (Û = U centered, equivalently the Fourier transform of δ·1_{X_E}). Then |T₃ − μ̃| ≤ (C/6)·p^{−θ}B^{3/2+o(1)}, which is o(μ̃) iff B^{3/2}p^{−θ} ≪ B³/p, i.e. **BIL(θ) certifies α > (2−2θ)/3.**
*Proof:* P2.2 + Parseval-writing of Σ_F δ; comparison with μ̃ ≈ (2/3)B³/L. ∎
The quality ladder (required θ for target α):

| target α | required θ | status |
|---|---|---|
| 1 (B = Ω(p)) | θ > −1/2 | **attained**: per-character Weil (THM1, black box) |
| 2/3 | θ > 0 | attained **conditionally** on H(1) (Parseval + flatness; this note, no black box) |
| 3/5 | θ > 1/10 | attained conditionally on H(2) (ladder, x-side) |
| → 1/2 | θ → 1/4 | limit of the entire norm family (P3.1, P3.3) |
| 2/5 (harvesting edge) | θ > 2/5 | **no known technique** |
| 1/3 | θ > 1/2 | no known technique |
| 1/5 (harvesting edge) | θ > 7/10 | no known technique |

**P5.2 (the exact residual statement, PROVED formulation).** CC(α): *for the target class 𝒜 of factor bases (e.g. log-independent, or uniform-x),* Σ_{x∈F} δ(x) = o(B³/p) at B = ⌊p^α⌋. Equivalent forms P2.6. For α ≤ 1/2, by P3.3 this is not reducible to any norm of δ; it requires cancellation among the signed values δ(x), x ∈ F. The self-coupling (δ is determined by F) is essential: for F *independent* of δ the bias would be O(√B·\\|δ\\|₂/√L)-scale (THM1 T4 machinery already gives much more); an adversarial F can align with δ only by aligning with its own chord sums — the group-AP is the extremal such self-alignment (§4). Any proof of CC(α) for a structured class must therefore use the coupling, not fight it.

**P5.3 (the exact new inputs that would close α ≤ 1/2, precisely).** Any one of:
- **Input EN(k):** a proof of H(k) for the target class at the Gaussian constants (EN(1): E₁(𝒫) = M⁴/n + O(M²·p^{o(1)})). Certifies α > (k+1)/(2k+1) by P3.1. Status: measured at toy scale (§6); a proof in the uniform-x model is in principle reachable by THM1 §3's configuration-moment machinery (exact first moment of E₁ under hypergeometric F — a finite case classification over x-equality patterns of quadruples; **not carried out here**, G3). Even EN(∞) cannot cross α = 1/2 (P3.3).
- **Input BIL(θ), θ ≥ 1/4:** a Burgess-type bound for the EC chord family — e.g., for interval/x-structured coefficient sequences, cancellation in Σ_{ψ} F̂(ψ)Û(ψ) beating the Parseval scale p·B^{3/2} by p^{1/4+}. No such bound exists at coefficient-set sizes < p^{1/2} in the repo-catalogued literature (Ahmadi–Shparlinski line, catalogued in research_directions_20260717.md:151,707 — *venue unverified, recollection*; those bounds operate at set sizes ≳ p^{1/2+ε}, and θ = 0 in the relevant regime).
- **Input STRUCT:** a structural theorem that log-independence of F implies (i) profile flatness and (ii) non-self-alignment |Σ_F δ| = o(√B·\\|δ\\|₂·(B^{3/2}/p)^{-1}·... ) — precisely: bias below the CS scale by the factor B^{1/α−3/2} of P5.2. No candidate technique; stated for the record.
At harvesting α ∈ [1/5, 2/5]: the required quality is θ ∈ [2/5, 7/10], or equivalently beating the L² scale by B^{1/α−3/2} ∈ [B¹, B^{7/2}]. This is the exact point where the fixed-F ceiling theorem remains blocked — now isolated to a single signed-sum statement with three named input routes.

## 6. Numerical evidence (toy scale; rule 7)

All from `thm_incbarrier2_check_output.json` (148 checks, 0 failures; 18 uniform-x instances over the six EXP-INCB-001 cells × 3 seeds, 3 AP instances, 2 character-sum instances):

- **Identities:** S = 6T₃ + 2d, T = M(M−1) − 2(B−z_F), profile identity, Ñ₂ ≥ 0, certificate — exact on all 21 factor bases (Fraction arithmetic).
- **Flatness (uniform-x):** Ñ₂/M² ∈ [2.51, 4.26] (mean ≈ 3.5) — supports C1(H(1)) with constant ≈ 2–4. The naive unpaired-set prediction ≈ 2; the excess is consistent with the ±paired sampling (A'(g) = A'(−g) doubles diagonal contributions) — HEURISTIC.
- **H(2) (uniform-x):** \\|δ\\|₄⁴/(M⁴/L) ∈ [16, 608], decreasing in λ = M²/L (608 at λ = 0.13 down to 16–90 at λ ≈ 2.4) — consistent with a granularity/overdispersion term that dies out plus a bounded Gaussian constant; the asymptotic constant is **not resolved at these sizes** (C1(H(2)) left as CONJECTURE with this recorded caveat).
- **Certificate vs Weil:** ratio ∈ [0.003, 0.13] on all 21 instances — the elementary certificate outperforms the black-box bound by 8–70× on every measured instance (P2.5(ii) explains why).
- **AP:** Ñ₂/M³ → 4/3, T₃ = 2⌊(B−1)²/4⌋ re-verified, tightness 0.84 → 0.90 (proved limit 3√6/8 ≈ 0.919).
- **Character sums:** Parseval Σ|U|² = pN₂ and Σ|U|⁴ = pE_x to float precision; unconditional lower bounds P3.2 verified with margins; max|U| = 179/366 vs Weil scale 2M√p = 2033/7171 and RMS ≈ 66/123.

## 7. Conjectures and open gaps (precise)

- **C1 (CONJECTURE).** Uniform-x profile flatness: H(k) holds w.h.p. at Gaussian-scale constants C_k for every fixed k (k = 1, 2 measured, §6). If proved for all k: uniform-x fixed-instance certification for all α > 1/2 via P3.1 — still short of T4's α > 1/3 for the *random* model, so C1's value is per-instance *fixed-F* certificates, not the average theorem.
- **C2 (CONJECTURE).** CC(α) holds for log-independent structured F (intervals, pseudorandom x-sets) at some α < 1/2 — equivalently BIL(θ) with θ > 1 − 3α/2 for the corresponding coefficient sequences. No evidence beyond the absence of a self-aligning construction other than the trivializing group-AP/subgroup families.
- **G1' (OPEN GAP, the residual barrier, replacing THM1 G1).** Prove or refute CC(α) for α ≤ 1/2 for a nontrivial class; by P3.3 this is exactly signed cancellation of δ on F. Quantified: need to beat the L² scale by B^{1/α−3/2}.
- **G3 (OPEN GAP, smaller).** Exact first moment (and concentration) of E₁(𝒫) in the uniform-x model via the configuration-moment machinery — a finite case computation; would prove C1(H(1)).
- **G4 (OPEN GAP, structural).** Does log-independence imply profile flatness / non-self-alignment? The Freiman route (large energy ⇒ approximate subgroup ⇒ dlog collapse) is a HEURISTIC recollection, unproved in both directions.
- **G5 (OPEN GAP, noted).** The true maximum of Ñ₂ over F: between Θ(M²) (flat) and Θ(M³) (AP) — the certificate is exact given Ñ₂, so the max-deviation problem reduces to the max-energy problem with alignment.

## 8. Verification appendix and deviation record (rules 8, 9)

- Script: `research/verification/thm_incbarrier2_check.py` (pure Python + numpy; chosen over sage after sage-Integer/Fraction interop failures — the two curve orders were re-verified via the x-table identity n = 1 + 2L − z against THM1's sage-verified rebuild, cited, not re-derived). Output: `..._output.json`, **148 checks, 0 failures**, wall < 1 s.
- **Deviation 1 (script bug, fixed, recorded):** the first d-counter (iterate P, pair with −2P, count if index(P) < index(−2P)) undercounts: pairs with index(P) > index(−2P) are never counted from either side. Caught by the S = 6T₃ + 2d check failing by exactly +16 on the (4099,28) AP instance (true d = 28, counted 20); fixed to a frozenset count; all downstream quantities recomputed. No external record was affected (script-internal, pre-delivery).
- **Deviation 2 (identity refinement, discovered by a FAIL):** the naive identity N₂ = 2E₁ failed by exactly 16 = A'(g)² on (4099,28,s=99), g the unique 2-torsion point with A'(g) = 4. Cause: the ±fiber over a 2-torsion point is a singleton, so r(x(g)) = A'(g), not 2A'(g). The proved identity is P2.3 with the 2-torsion correction. Mirrors THM1's Klein-four discovery; recorded per rule 8.
- **Convention note (rule 9):** U(ψ) here excludes vertical pairs (x(P+Q) undefined); THM1 §5.1's displayed definition is ambiguous on this point (its S-identity implicitly excludes them). No bound in THM1 is affected (O(M) terms only).
- No experiment directories were touched; no ledger writes; read-only use of RUN-INCB-001-b data as routed through THM1's note.

## 9. Boundaries and honesty

- Toy-scale verification only (p ≤ 2^12); the theorems are stated and proved for general p, B; no crypto-scale empirical claim (rule 7). G1' states exactly what a crypto-scale-relevant theorem requires.
- **No black box is used anywhere in this note** (THM1's Weil bound is only a comparison baseline). All proofs are elementary: Bezout-free even — the tools are x-saturation, Cauchy–Schwarz/Hölder, Parseval over F_p, and convexity.
- The conditional certifications (P3.1 ladder) are proved implications; the hypotheses H(k) are proved necessary in the tightness sense (P4.1(iii): no (B, Ñ₂)-only bound improves by > 9%) and measured at toy scale, but not proved for any infinite class — that is C1/G3.
- Literature touchpoints are as catalogued in research_directions_20260717.md:151,707 (recollection, venue unverified); no new external sources are asserted.
- Summary vs THM1: G1 is *not closed*; it is **reduced** — from an unstructured "cross-character cancellation" to (i) an exact per-instance certificate, (ii) a proved ladder reaching α → 1/2 under explicit checkable hypotheses, (iii) a proved ceiling of the whole norm family at α = 1/2, and (iv) three named input statements (EN, BIL, STRUCT) with exact quality thresholds. THM1's heuristic "fourth moment caps at p^{2/3}" is superseded by the proved ladder (2/3 is its k = 1 rung; the family limit is 1/2).
