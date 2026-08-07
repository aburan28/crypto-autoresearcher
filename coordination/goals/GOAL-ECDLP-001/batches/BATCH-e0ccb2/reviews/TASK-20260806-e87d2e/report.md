# Independent Review — BATCH-121 oracle/H-PSEUDO and multi-target analyses

**Task:** TASK-20260806-e87d2e
**Batch:** BATCH-e0ccb2 (review-only)
**Goal:** GOAL-ECDLP-001
**Role:** Reviewer (independent session)
**Requested policy:** review-adversarial
**Resolved model id:** opencode/deepseek-v4-flash-free

## Scope

Reviewed, without editing:
- `TASK-20260805-004/oracle_hpseudo_analysis.md` (IDEA-20260805-62ef74)
- `TASK-20260805-005/closure_and_multi_target.md` (IDEA-20260805-58b638, IDEA-20260805-0cd03f)
- `DEC-20260805-364e9e` and `DEC-20260805-70450a`
- `BATCH-e0ccb2/batch.yaml`
Supporting (read for grounding): `KN-FIND-9d2f56`, `KN-FIND-c7d31e`, `H-PSEUDO-83817b`, BATCH-060/TASK-20260804-051 `ggm_analysis.md`, the IDEA records in `BATCH-120/TASK-20260805-002/new_ideas_batch120.yaml`.

Verification performed (throwaway arithmetic script, no files persisted, no experiment): symbolic/algebraic check of the duplication formula on the doc's own test curve `y² = x³ + 3x + 7` over F_1009 (950 affine points), replication of the doc's ord_q(2) table, halving-query demonstration on the q = 17 subgroup, re-evaluation of the K* tables, and re-evaluation of the L[1/2, sqrt(2)] numbers.

---

## Claim set 1 — IDEA-62ef74 oracle / H-PSEUDO

### 1a. "Corrected" biconditional: `∃F [chain-complex C_R^F sub-rho] ↔ ∃F [H-PSEUDO fails for F]`

**VERDICT: inconclusive** (not renderable as established; a formal claim to verify, not a confirmed result).

- The orientation fix alone is correct and important: H-PSEUDO-83817b bounds `max_k |hat 1_F(k)| ≤ C sqrt(B)`. *Holding* means DLs are pseudorandom, i.e. yield at the heuristic baseline; *failing* (a large single Fourier coefficient) is what could push yield above baseline. The doc (and DEC-20260805-364e9e) correctly flipped IDEA-62ef74's backwards Direction A. Good.
- **Strongest objection:** the biconditional overstrengthens the source. KN-FIND-9d2f56 (which is itself a sketch-level "proof sketch", claimed `confidence: proved`) states a disjunction: either β_1 ≥ Ω(sqrt(N)) **or** average yield is `o(1)` ("the complex is useless for most targets"), and derives only **one direction** (sub-rho β_1 < sqrt(N) ⇒ above-heuristic yield). The reverse direction "above-heuristic yield for some F ⇒ exists F with β_1 < sqrt(N)" is not contained in that sketch, and the `o(1)` third branch is silently dropped when the doc turns the finding into an iff. The iff also silently moves from "average yield over targets" to "some F". As an iff it is unproven.
- Supporting this verdict: the DEC's own disposition is a **dispatch for formal theorem work**, i.e. the result is explicitly not established. That disposition is appropriate *because* of the defect, not in addition to it.

**Minimal discriminating test:** formalize KN-FIND-9d2f56's corollary direction-by-direction; decide the `o(1)` branch fate for a factor base with above-heuristic yield (does the rank bound β_1 ≥ B − B²/N vs B − r_2 relax enough? at which B/N regime?). This is mathematics, not compute — matches the DEC's dispatch. If the reverse direction fails, the corrected claim in the DEC (and in DEC-20260805-4c1e8b's finding field) must be narrowed from "iff" to "⇒".

### 1b. "Unconditional" Semaev IC complexity L[1/2, sqrt(2)] ≈ 2^61.7 vs 2^128

**VERDICT: reject the unqualified "unconditional" label; the arithmetic is fine.**

- Rechecked: N=2^256, L[1/2, sqrt(2)] = exp(sqrt(2)·sqrt(lnN·lnlnN)) ≈ 4.15e18 ≈ 2^61.85 ≪ 2^128. The doc's exponent (≈2^61.7) and the DECT claim that it is well below the sqrt(N) reference are arithmetically correct.
- **Strongest objection:** the O/number is "unconditional" in label but heuristic in substance. Semaev IC's L[1/2,·] is a *heuristic* complexity: it assumes (i) the relation-yield equality of form B^m/N for random targets (the principal), (ii) within-budget solvability of the summation polynomial, (iii) a smoothness-like factorisation model, and (iv) in the GCD+C model the factor-base construction cost. The very same document covers itself: Q1 line 22 says "Semaev IC with heuristic yield achieves …"; Q2's own analysis spends paragraphs on yield modifications. You cannot declare the summary "UNCONDITIONALLY" after conditioning the derivation on a heuristic.
- The DEC propagating "UNCONDITIONALLY" (DEC-20260805-364e9e line 14, YAML line 7) is an overclaim that must not survive into any evidence record.

**Minimal discriminating experiment:** none needed over the prevent; the fix is a wording/robustness correction: re-state as "conditional on the Semadev IC heuristics". If the program later wishes to *claim* unconditionality, that is a separate theorem about lower bounds — requiring its own proof, not a restatement.

### 1c. C_t is Tier-3 non-simulable; and "the C_t premise suffices for sub-rho in GGM+C_t"

**VERDICT on the classification: pass.** C_t reads the concrete x-coordinate ordering; the non-simulability follows by the same encoding-witness argument already used for the control encoding oracle in BATCH-060 (`P → x(P)` NON-SIMULABLE). The doc's witness (two curves, same group order, same labels, differing C_t answers) is the correct family of argument, even if the paragraph is informal. No new experiment needed — consistent with the guidance in Q3.

**VERDICT on the sufficiency premise: not established.**
- **Strongest objection:** the equivalence claim "GGM+C_t IC is complexity-equivalent to the concrete IC (O(1) overhead per relation)" silently drops the *factor-base construction* step. In the concrete model the factor base `{P: x(P)<B}` is built by enumerating x and computing y — public, algebraic, O(sqrt·poly) work. In GGM+C_t the adversary has only handles produced by the group law and 1-bit tests; a factor-base element with the required x will be tested among group multipliers with only ~B/|G| sampling acceptance, so assembling |B| = all elements isn't O(1) per element. Which concede exactly what changes the complexity. The doc's own null-object control (random group) acknowledges C_t alone is not sufficient; the "EC structure" must be granted separately — which is precisely the enumeration capability the doc never accounts for.
- On the sub-rho side: even after (b), the "unconditional" and the "C_t suffices" claims cannot both hold; this compounds the 1b overclaim: **without** the enumeration gap resolved, the honest statement is "GGM+C_t IC with heuristic yield *and* factor-base construction granted is (heuristically) within L[1/2,√2]".

**Minimal discriminating experiment:** at toy scale (p=1009, e.g. q≈17..107 subgroups), instrument a GGM+C_t simulator (handles + group-law + 1-bit threshold queries) and measure the query cost to *assemble* a factor-base set of landmark B and a coordinate ground-truth model; if the C_t-only construction is super-constant per element, the "O(1) overhead" equivalence is falsified in the doc's own model.

---

## Claim set 2 — IDEA-20260805-58b638: doubling oracle on door

**VERDICT: REJECT** — the closure argument as documented is not sound, and the recorded disposal relies on its wrong arguments.

- **(i) The one-query halving triviality.** `O_D(P) = x([2]P)`; the adversary constructs `H = [2^{-1}](σ)Q` via group law (scalar multiple by (q+1)/2, integer double-and-add), and then `O_D(H) = x([2]·[2^{-1}]) = x(Q)` in **one** oracle query. I executed exactly this on the doc's own 128 curve: q = 17 subgroup; G an order-17 point, Q=[3]G; H=[2^{-1}]Q=(26,717) computed by group-law multiples; x := double-and-add and one O_D query returns x(Q)=897. Chain of the doc's chain argument (A.8 "to collapse the chain you need 2^t ≡ 1 (mod q), i.e. t = ord_q(2)". That step presumes the only sensible strategy is iterating forward doublings; it is structurally wrong — you query the oracle *invariant* (at the point whose double is Q). 
- **(b) Consequence: O_D ≡ x-coordinate oracle.** Because the adversary can precompute [2^{-1}]Q freely, `O_D(Q-point) = x(P)` and, conversely, x-oracle computes `x([2]P)` for `O_D(P)`. So O_D and the x-coordinate oracle are **equivalent**, not merely `O_D ⊆ x-oracle`.
- **Is the "barrier confirmed" closure sound?** **No — it is void against the companion doc's own classification.** The companion doc(1c) classifies the x-coordinate/encoding oracle as **NON-SIMULABLE (Tier-3, encoding-dependent)**. Since O_D ≡ x-oracle, the doubling oracle is *likewise* non-simulable — but the doubling-closure doc claims (A.1, A.3, summary item 1) that O_D is "GGM-simulable". That is the exact inverse: the document simultaneously asserts what its premise contradicts. Precisely: "O_D = f(x(P)); O_D carries exactly the information that knowing x(P) would carry, and no more" — the "no more" is true, but instead of proving harmlessness it shows O_D is a *non-simulable in extensional oracle*. In that case the barrier claim that O_D "doesn't give a sub-rho attack" cannot be derived by the doc's simulability argument; it must be derived by a different result (namely: does the x-coordinate oracle alone — i.e. the concrete-model x-query — yield sub-pre-rho? — that's just the open IC question, unconcluded).
- **ord_q(2) = Ω(sqrt(q)) generically?** The *Toy-verified claim* is genuine: I replicated the doc's complete Table A row by row on the doc's five (a,b) pairs + the test curve: N ∈ {952, 1064, 1008, 994, 1070, 1044}, q ∈ {17,19,7,71,107,29}, ord_q(2) ∈ {8,18,3,35,106,28}, all ≥ sqrt(q). The empirical claim is honest. The **justification** however is misattributed: "Shoup's generic lower bound applied to a multiplicative group ⇒ expected order = Θ(q)" — Shoup is about query complexity of DLP, not about the order of a fixed integer element mod a random prime; and "Artin's conjecture proved conditionally by Hooley" is the *primitive root* claim (order = q−1), a much stronger property — it does not prove the *asymptotic rare-small-orders* statement that the doc needs. The statement itself (rare small ord_q(2) modulo a random q, typical value ≥ √q) is plausible, is loosely supported by toy data here, and has known precursors — but it is heuristic/folklore, not "proved" and not what the citations say.
- **why does closure break even more:** even if ord_q(2) had been astronomically small, the chain is unnecessary; the halving query renders the whole ord_q(2) route moot.

**Minimal discriminating experiment:** (already effectively executed as part of this review). On the doc's own test curve with q=17: (1) compute the single-query halving recovery of x(Q), (2) count the number of O_D queries needed vs. ord_q(2); demonstrate 1 ≪ 8. As the committed record, the toy experiment the DEC-20260805-596 exposed in 2h should be re-run is now turned around: instead of "confirming the barrier" it is the discriminating test that the closure's main instrument (chain cost ≈ ord_q(2)) fails at its own toy scale.

**The doubling formula part is reviewed separately under claim set 4.**

---

## Claim set 4 — the doubling closed-form and its "verified at all points" claim

**VERDICT: REJECT** — the formula as printed, and the "verified at all affine points" statement, are both false.

- **The exact formula in the doc (TASK-20260805-0095 line U1 / §A.2):**
  `x([2]P) = [(3x_P² + a)² − 8b·x_P] / [4(x_P³ + a·x_P + b)]`
  is **wrong**. The correct identity (which the task prompt and my derivation agree on):
  `x([2]P) = (x_P⁴ − 2a·x_P² + a² − 8·b·x_P) / (4(x_P³ + a·x_P + b))`.
  They differ by `(3x²+a)² − (x⁴ − 2ax²+a²) = 8x⁴ + 8a x² = 8x²(x²+a)`, which vanishes only at x = 0 and x² = −a, i.e. generically.
- **Earlier failure:** I scanned all 950 affine points of `y² = x³+3x+7` over F_1009: the doc's formula disagrees with the actual `x([2]P)` (computed by the tangent-slope definition) at **944/950** points; the correct formula (above) agrees at **all** 950. For example x=2: x(2P)=678451→ 323; doc formula gives 662; correct formula 323. The doc's claim "evaluated at all affine points … confirmed to match x([2]P)" is therefore **not credible** against the number it prints: either the check was never run on the printed formula, in which case the committed "verified" sentence is fabricated (rule 9), or it was run and the correlation to the correct formula was mis-recorded. Either way the artifact does not support its own claim.
- Note the source IDEA file itself has the same error: first formula `(x⁴+2ax²+4bx+a²−4ab)/…` and the so-called "corrected" `((3x²+a)²−8bx)/…` are both wrong; the numeric mismatches I found for the first form across all 950 points.
- The only thing that survives is the structural property that drives the (wrong) conclusion: `x([2])` is a rational function of x(P) **alone** (y² → x³+ax+b substitution removes y). That fact is true and is used to justify the halving — which is exactly what destroys the closure.

**Minimal discriminating experiment:** print a symbolic/naive check at two curves on the toy curve (e.g. doubly x=2,5,10) with the doc's formula and the correct one; the mismatch appears instantly (already quantified: 944/950). This is a one-ointment check, and the doc's "verified at all points" fails it.

---

## Claim set 3 — Multi-target BKK crossover

**VERDICT: PASS** (formula verified; "approved for experiment design" is sound) with two corrections.

- `K*(BKK) = ceil(s·β/(1 − t·β))`, β = 2/(m+1), need `t·β < 1` ↔ `t < (m+1)/2`, region `t ∈ [1, (m+1)/2)`: verified. The algebra is the lattice condition (S' + k·T' < k·√N, S' = s·β·√N, T' = t·β·√N → k > s·β/(1−t·β)).
- **Example line m=5, s=200, t=0.9: K*(BKK) = ceil(66.666…/0.7) = 96 — CORRECT.** K*(std) = ceil(200/(1−0.9)) = **2000 exactly** (rational 200/(10/10)·… = 2000.0), but the doc (and the DEC) print **2001** in all three t=0.9,s=200 rows. This is an IEEE-float artifact `200/0.1 = 2000.0000000000002 → ceil → 2001`. Exact arithmetic gives 2000. A minor but concrete error in the headline example (one-off, non-cumulative; the 0.048 ratio and all other 18 rows check out).
- **Soundness of "approved for experiment design":** yes. The K* equation is a provable mutual ratio *given* the premise `S_rel(BKK)/S_rel(std) = T_desc(BKK)/T_desc(std) = β`; that premise is a modeling assumption — exactly what EV-SEMAEV-7f7d22 pre-register (measure S_rel-ratio and K* vs. K* reality, with the null object). The doc's "provable, not heuristic" (B.7, line 261) overstates slightly: the arithmetic is provable; the transfer of β to *both* channels is the experimental hypothesis, and the theorem KN-FIND-c7d31e's γ_retention = (m+1)/2^m × 2^(m−1) speedup is derived for the *factor-base membership predicate*, which is why the experiment value is needed. The claimed scope (constant-factor only, exponent unchanged) is correct and honestly stated.
- Minor: the table states "216×,(m+1)/2)" possibly a rescue interval wording: t ∈ [1,(m+1)/2) list in §B.5 is right — the doc prints "rescue t in range" as `[1, 2·4)` for m=3 = 2·(3+1)/2? Actually with β=2/4=0.5.... for m=3, 1/β = 2.0, the doc's `[1,2.00)` is right; nothing to fix there.

**Minimal discriminating experiment:** the pre-registered EV-SEMAEV-7f7d22 — run it with exact rational arithmetic for K* (kill the float-`ceil` artifact) and measure `S_rel/B` and `T_desc` ratios on the 5 toy curves at ~16–24 bits. Also, pin 2000 vs 2001 in the reference table.

---

## Disposition review for DEC-20260805-364e9e

| Decision | Verdict | Grounds |
|---|---|---|
| Reject IDEA-20260805-58b638 ("barrier confirmed: simulable, ord_N(2)=Ω(√N), no sub-rho") | **NOT as stated — supersede.** | The two premises of the doctrine are both false/wrong: (i) `O_D` is **not** simulable — it is equivalent to the x-coordinate oracle, which the companion doc (and BATCH-060) itself score as *non-simulable Tier-3*; (ii) the ord_q(2) chain has the halving query — a single O_D at `[2⁻¹]Q` returns x(Q) (verified). The *conclusion* "O_D supplies no *new* sub-rho capability beyond the x-oracle /standard IC" is plausibly true **on a different argument** (x-oracle-alone is not known to be sub-r-scratch-rho), but that reconstruction is not in the record, so the decision must be re-reasoned/supr approach. |
| Dispatch IDEA-20260805-62ef74 for formal theorem work | **Survives**, with amended evidence: the dispatch to theorem-formal where the biconditional must prove/c identify the `o(1)` third-branch in the source ground and the "UNCONDITIONALLY" statement must be dropped from the record (heuristic conditional). A dispatch is the correct action precisely because these are the unsettled claims. |
| Approve IDEA-20260805-0cd03f for experiment design (EV-SEMAEV-7f7d22 reserved) | **Survives.** K* formula verified (2001→2000 float-atan fix) and the experiment is pre-registered with null/control; sound. |
| H-PSEUDO orientation correction (holding=heuristic; chain-sub-ρ requires failure) | **Correct in substance.** Consistent with H-PSEUDO-83817b's own statement (holding = pseudorandom = bounded Fourier). The **cashed** (biconditional) is unproven — see 1b/1a. |

**Overall:** DEC-20260805-364e9e does **not** survive as committed: the IDEA-62ef74 real, the 2021 rejection of IDEA-58b638, and the ''unconditional'' remains the strongest/internally contradictory defects. The remedy is a superseding evidence + decision (as BATCH-e0ccb2's ledger archive is positioned to do) — not a retraction of the historical records.

---

## Summary of verdicts

| Claim set | Verdict | Strongest objection |
|---|---|---|
| 1a corrected biconditional | inconclusive | overstrengthened KN-FIND-9d2f (the `o(1)` branch, reverse direction omitted) |
| 1b "unconditional L[1/2,√2]=2^61.7" | reject-the-label / heuristic-conditional | self-contradicted by the doc's own "with heuristic yield" |
| 1c C_t Tier-3 classification | pass | — |
| 1c C_t premise suffices for sub-rho | not sufficient / revise | factor-base construction in literal GGM+C_t not O(1): enumeration gap |
| 2 doubling oracle | **reject** | halving query: `O_{D}([1]^{-1}Q)` reveals x(Q) in one query ⇒ O_D ≡ x-oracle (non-simulable), chain/barrier void |
| 4 doubling closed-form + "verified at all points" | **reject** | printed formula wrong (944/950 mismatch on F_1009); "verified" claim contradicted/fabricated |
| 3 multi-target BKK | **pass** | K⋅ 96 correct, K*(std) 2001 is a float artifact (exact 2000 delta, not arithmetic) |

No experiment was run; the arithmetic/library checks above are review-time verification of committed records (throwaway scripts, safe temp), none written to the repo.