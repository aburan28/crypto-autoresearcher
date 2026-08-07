# Independent Review — TASK-20260806-4ebdf1
**Policy:** review-adversarial (xhigh reasoning, independent session)
**Batch:** BATCH-b3f591, GOAL-ECDLP-001
**Date:** 2026-08-06
**Reviewed artifacts:** 4 producer deliverables

---

## Per-Artifact Verdicts

### Producer A: halving_query_equivalence.md
**VERDICT: SURVIVES**

The corrected duplication formula x([2]P) = (x⁴ − 2ax² + a² − 8bx) / (4(x³ + ax + b)) is algebraically correct. I verified independently on y² = x³ + 3x + 7 over F_1009: the formula matches true x([2]P) at all 475 valid x-coordinates with y ≠ 0. The halving query O_D([(q+1)/2]Q) = x(Q) is correct: [2]·[(q+1)/2]Q = [q+1]Q = Q in the order-q subgroup, so one oracle call recovers x(Q).

The BATCH-121 formula error is correctly identified. The equivalence O_D ≡ O_x is properly stated and proved. Non-claims are correctly scoped: no sub-rho claim in either direction.

**Minor concern:** §4.4 hand computation becomes unclear ("let me just verify computationally") but the final result is correct. §2.5 claims the wrong formula agrees at 3 of 475 points; this is consistent with the algebraic analysis (agreements at x = 0 and x² ≡ −a mod p, provided these are valid x-coordinates).

**No overclaiming detected.**

---

### Producer B: knowledge_candidates.md
**VERDICT: SURVIVES**

Three KN-FIND candidates are correctly drafted as candidates (not promoted; promotion requires Coordinator ledger decision). IDs are properly minted with 6-hex suffixes per AGENTS.md rule 14.

- **KN-FIND-194294** (halving-query equivalence): Correctly states the equivalence and inherits O_x's Tier-3 non-simulable classification. Non-claims properly scoped.
  
  *Minor wording concern:* The candidate defines O_D as "on input Q, returns x([2⁻¹]Q)", while Producer A defines O_D(P) = x([2]P). These are algebraically equivalent (same oracle, different input parameterization), but the redefinition could confuse readers. The mathematical content is correct.

- **KN-FIND-ac28ed** (BKK exact-arithmetic corrections): Correctly identifies IEEE-float ceil artifacts (2000 vs 2001, 125 vs 126). K*(BKK) = 96 confirmed correct. Non-claims properly scoped.

- **KN-FIND-ff4a46** (KN-FIND-9d2f56 wording repair): Correctly aligns with DEC-20260806-08b9ed's corrected H-PSEUDO orientation (holding = pseudorandom = AT-heuristic yield; sub-rho requires failure). The repaired corollary explicitly states "necessary condition only", removing the ambiguous sufficiency reading.

**No overclaiming detected.** All candidates correctly note they are not promoted and require Coordinator action.

---

### Producer C: hpseudo_o1_branch_disposition.md
**VERDICT: SURVIVES**

The document correctly analyzes two readings of the o(1) leaf in KN-FIND-9d2f56's disjunction:

- **Reading 1** (genuine structural branch): o(1) yield is a clean alternative to sub-rho.
- **Reading 2** (notation artifact): the bound β₁ ≥ B − B²/N is continuous and does not establish the clean dichotomy for all B.

The recommendation of Reading 2 is well-supported:
1. The proof sketch uses rank(∂₂) ≤ r₂(R), an upper bound on rank, not a lower bound on β₁.
2. The "at heuristic" vs "above heuristic" gap is not bridged in the sketch.
3. For B < √N, the bound β₁ ≥ B − B²/N is weaker than √N, so the dichotomy fails.

The document correctly identifies that only the forward direction (sub-rho → yield ≥ heuristic) is supported; the backward direction (H-PSEUDO fails → sub-rho) remains open.

**Explicitly labeled as a disposition, not a closure.** No status transition is claimed. No hypothesis is introduced. Non-claims are properly scoped.

**No overclaiming detected.**

---

### Producer D: experiment_design.md
**VERDICT: SURVIVES**

The toy-scale experiment design is sound and correctly scoped (rule 7: no crypto-scale claims).

**Strengths:**
1. **Run-matched null object:** Arms B (x-oracle) and C (random predictor) are identical except for oracle response truth value. This satisfies the inventor-protocol "controls before belief" requirement.
2. **Pre-registered falsification criteria:** Three explicit conditions for rejecting H-XOR-YIELD.
3. **MITM strategy is correct:** For m = 4, split into left (P₁, P₂) and right (P₃, P₄); hash table maps x(P₃ + P₄) → tuples; query x(P₁ + P₂) and look up. A hit means P₁ + P₂ = ±(P₃ + P₄); the negative case gives a relation, the positive case is a false positive (correctly accounted for with verification and false-positive rate metric).
4. **Parameter cells are corridor-compatible:** m ∈ {3,4}, p ∈ {101,103,107,211}, b ∈ {0.4,0.5} are from review-backed ranges; no proven-empty corridor is exercised.
5. **Smoke gate and stopping rules are pre-registered.**

**Concerns:**
1. The experiment tests a specific MITM strategy. A negative result (oracle-inert) would not rule out other strategies that might exploit the x-oracle. The design correctly scopes the hypothesis to "under this strategy" but the Coordinator should note that a negative result is strategy-specific, not oracle-wide.
2. The random predictor uses PRNG(key‖P), which is deterministic and collision-free within each run. This is a valid null object, but the PRNG must be cryptographically secure to avoid accidental structure. The design should specify the PRNG algorithm (e.g., AES-CTR, ChaCha20) in the frozen specification.

**No overclaiming detected.** The design correctly states "No result from this experiment, regardless of outcome, is presented as evidence about crypto-scale ECDLP."

---

## Summary

All four artifacts survive adversarial review without overclaiming sub-rho conclusions in either direction. Each artifact:
- Correctly scopes its claims and non-claims.
- Does not assert sub-rho enablement or disablement.
- Properly references the open x-oracle-alone question.
- Does not perform unauthorized state transitions.

**No fabricated runs, statistics, or citations detected.**

**Recommendation:** Accept all four artifacts. Proceed to Coordinator ledger decision on knowledge promotions (Producer B) and experiment approval (Producer D).

---

*Review by TASK-20260806-4ebdf1, independent session, policy review-adversarial.*
