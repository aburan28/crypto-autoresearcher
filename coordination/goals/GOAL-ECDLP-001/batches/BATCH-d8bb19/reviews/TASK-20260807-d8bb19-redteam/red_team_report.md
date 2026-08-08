# Red-Team Report: BATCH-d8bb19 — Challenge to "No Viable Mechanism" for SG-ECDLP-002

**Task ID:** TASK-20260807-d8bb19-redteam
**Batch ID:** BATCH-d8bb19
**Date:** 2026-08-07
**Role:** Red Team (independent adversarial review)
**Policy:** review-adversarial (xhigh reasoning, independent session)

---

## Summary

The idea generator recommends closing SG-ECDLP-002 on the basis of four obstructions across three proposals. I assess that **three of the four obstructions are structurally sound** and the closure recommendation is **substantively correct in its bottom line** — ordinary F_p-isogeny transfer cannot improve on Pollard rho for generic prime-field ECDLP. However, the report contains **one significant overclaim**, **two moderate imprecisions**, and **one unexamined mechanism** that the idea generator should have addressed before recommending closure.

**Overall assessment:** The conclusion is directionally correct but the closure recommendation is **premature by one evidentiary step**: the within-class uniformity obstruction (IDEA-ISO-f9b2d3) is empirical, not proven, and its toy-scale test has not been run. The other three obstructions are solid. The closure should be **scoped** to the three proven obstructions, with the within-class uniformity held as `unverified` until the toy-scale experiment confirms it.

---

## Objections

### Objection R1: The "within-class uniformity" obstruction is empirical, not proven
**Severity: SIGNIFICANT**

IDEA-ISO-f9b2d3 asserts that "DLP difficulty is uniform within an ordinary isogeny class" and lists this as a closure obstruction. The basis is:

> "All known DLP algorithms (Pollard rho, BSGS, index calculus, GLV, MOV, GHS) depend only on [trace-determined parameters]. No algorithm is known that depends on j or the model."

This is an **empirical claim** ("no known algorithm"), not a theorem. The idea generator acknowledges this (assumption H1, "rigorous_support: None") but then treats the obstruction as closure-grade. This is a category error: an untested heuristic assumption cannot bear a closure conclusion.

**What's actually proven:**
- N, embedding degree, CM discriminant, and trace are isogeny-class invariants (theorem: Tate/Honda-Tate).
- All *currently known* DLP algorithms key on these invariants.

**What's NOT proven:**
- That no future algorithm could exploit j-invariant-dependent structure.
- That the Weierstrass model carries no exploitable information (ISO-EXP-A2 tested this at toy scale and found nothing, but toy-scale negatives are not theorems).

**The ISO_GOAL_isogenous_weak_curve.md document** (an independent prior analysis) reaches the same conclusion but is more careful: it labels the result `RESTRICTED THEOREM` for the invariant part and `O-1 coefficient-level early fall — tested, CLOSED for the toy class; not a theorem at crypto scale` for the model-dependent part. The idea generator should have adopted this distinction.

**Falsification route:** A future algorithm that exploits the conductor f (which varies within the class) or the j-invariant to speed up DLP would invalidate this obstruction. No such algorithm is known, but the absence of one is not a proof of impossibility.

**Remedy:** The within-class uniformity obstruction should be labeled `unverified` (toy-scale test pending) rather than `closure`. The other three obstructions are sufficient for a scoped closure.

---

### Objection R2: The GLV lattice analysis in IDEA-ISO-7f3e2d conflates two different speedup regimes
**Severity: MODERATE**

The proposal states:

> "The GLV endomorphism has norm ~ sqrt(|D|) ~ sqrt(p), giving a 2D lattice with determinant N ~ p and short vector norm ~ sqrt(p*N) ~ p. The 2D Pollard rho cost is p^{1/2} = SAME as standard rho."

This is correct in its conclusion (GLV gives no exponent improvement for generic D) but the lattice analysis is imprecise:

1. For GLV with a single endomorphism φ of norm ||φ||, the decomposition is k = k₁ + k₂λ where |k₁|, |k₂| ≤ √N · (||φ||/√p)^{1/2} approximately. For ||φ|| ~ √p (generic D), this gives |k₁|, |k₂| ~ N^{1/2}, and the 2D search space has size ~ N, so 2D rho costs N^{1/2} = same as standard rho. **Correct.**

2. For special D (class number 1, small |D|), ||φ|| is small (e.g., ||φ|| ~ 1 for j=0 with cube roots of unity), giving |k₁|, |k₂| ~ N^{1/2} / p^{1/4}, and the 2D search space has size ~ N / p^{1/2}, so 2D rho costs ~ N^{1/2} / p^{1/4}. For N ~ p, this is ~ p^{1/4}, which IS an exponent improvement. **The idea generator acknowledges this but labels it "constant-factor speedup," which understates the special-case improvement.**

The conclusion (no improvement for generic D) is correct, but the special-case analysis should have been more precise: for j=0, j=1728, the GLV speedup IS an exponent change (from 1/2 to 1/4), not merely a constant factor. This doesn't change the closure (these curves are excluded by standard selection), but it's a factual error in the proposal.

---

### Objection R3: The extension-field isogeny cost bound Ω(p^{k/2}) is not tight for all k
**Severity: MODERATE**

IDEA-ISO-a4c8e1 states:

> "The cost of finding an F_{p^k}-isogeny between arbitrary curves is Ω(p^{k/2}) for any known algorithm."

This bound is derived from the supersingular isogeny problem and random-graph hitting-time heuristics. However:

1. **For supersingular curves over F_{p^2}**, the isogeny graph has degree ℓ+1 and ~ p vertices. The diameter is O(log p), and finding a path of length d costs O(ℓ^d). For d = O(log p), this is O(p^{log ℓ / log p}) which is polynomial in p for fixed ℓ. But this is for SUPERSINGULAR curves, not ordinary curves.

2. **For ordinary curves over F_{p^k}**, the isogeny graph structure depends on the CM discriminant D. For large k, the curve E/F_{p^k} may have a different CM discriminant than E/F_p (the Frobenius over F_{p^k} is π^k, not π). The isogeny graph over F_{p^k} could have different expansion properties.

3. **Galbraith 2024 (ePrint 2024/924)** shows that for P-256's flat volcano (conductor f=1), the isogeny bridge is cheap: Õ(q^{1/4}) ≈ 2^64. This is for F_p-isogenies, not extension-field isogenies, but it shows that the isogeny-finding cost can be much less than the random-graph heuristic suggests for special graph structures.

The Ω(p^{k/2}) bound is correct for generic ordinary curves over F_{p^k} with the random-graph heuristic, but it's not a theorem. The idea generator should have acknowledged this uncertainty.

**However:** Even if the bound is loose by a polynomial factor, the extension-field bridge still costs at least Ω(p^{k/2 - ε}) for some small ε, which is still ≥ Ω(p^{1/2}) for k ≥ 1. So the conclusion (no improvement over rho) is robust to the imprecision.

---

### Objection R4: The idea generator did not consider isogeny-based DLP on the isogeny graph itself
**Severity: MINOR**

The three proposals all frame the isogeny graph as a *bridge* to a special curve where DLP is easier. But there's a different approach: could the *structure of the isogeny graph itself* be exploited to solve DLP?

For example:
- The isogeny graph is a Ramanujan graph (optimal expander). Could spectral properties of the graph be used to decompose the DLP?
- The graph has a natural random walk. Could a random-walk-based algorithm (similar to Pollard rho but on the isogeny graph) be faster than rho on the group?
- The graph's automorphism group (the class group) acts on the graph. Could this symmetry be exploited?

This is a different mechanism from isogeny transfer, and it's arguably out of scope for the idea generator's task (which was to propose revised isogeny-transfer mechanisms). But the idea generator's Appendix A ("What Was Not Proposed") should have mentioned it as a residual open direction.

**Assessment:** This is a minor omission. The isogeny-graph-as-target (rather than bridge) approach is speculative and has no known mechanism. It doesn't affect the closure recommendation.

---

### Objection R5: The dominated_by / sota_delta calculations are correct
**Severity: None (confirmation)**

All three proposals correctly identify Pollard rho at exponent 1/2 as the dominating algorithm. The sota_delta calculations are correct:
- IDEA-ISO-7f3e2d: time_exponent 1/2 (same as rho), no improvement. ✓
- IDEA-ISO-a4c8e1: time_exponent k/2 ≥ 1/2 (worse than or equal to rho). ✓
- IDEA-ISO-f9b2d3: time_exponent 1/2 (same as rho for all curves in class). ✓

The cost model is honest and correct.

---

### Objection R6: The Tate theorem obstruction is absolute
**Severity: None (confirmation)**

The Tate isogeny theorem is an unconditional theorem: two ordinary elliptic curves over F_p are F_p-isogenous if and only if they have the same trace of Frobenius. There are no edge cases, no heuristic assumptions, and no known exceptions. This obstruction is solid.

---

## Hidden Assumptions

The "no viable mechanism" conclusion rests on the following hidden assumptions:

1. **A1 (empirical):** No future DLP algorithm exploits j-invariant or conductor-dependent structure. This is the within-class uniformity assumption (Objection R1).

2. **A2 (heuristic):** The random-graph hitting-time heuristic correctly predicts isogeny-finding cost over extension fields. This could fail if the ordinary isogeny graph over F_{p^k} has unexpected structure (Objection R3).

3. **A3 (scope):** The question is restricted to ordinary F_p-isogenies on prime-field curves. Supersingular isogenies, isogenies over extension fields of the target curve (not the base field), and non-isogeny approaches are out of scope. This is correctly stated in the proposals.

4. **A4 (implicit):** The target is generic prime-field ECDLP (not special families like anomalous, MOV, or pairing-friendly curves). This is correctly stated.

Assumptions A3 and A4 are explicit and correct. Assumptions A1 and A2 are heuristic and should be labeled as such in any closure decision.

---

## Mechanisms the Idea Generator Missed

### M1: Isogeny-graph spectral methods
As noted in Objection R4, the idea generator did not consider exploiting the spectral properties of the isogeny graph itself (rather than using the graph as a bridge). This is speculative but should have been mentioned as a residual open direction.

### M2: Isogeny-based index calculus augmentation
The idea generator's Appendix A mentions "isogeny-augmented index calculus" as already explored. But the specific question of whether isogeny walks can *reduce the factor base size* for index calculus on the isogeny graph (rather than the group) was not addressed. This is a different mechanism from isogeny transfer and might warrant a separate proposal.

### M3: Kani-based constructions
The Kani theorem (on canonical lifts and Serre-Tate coordinates) provides a way to construct isogenies between curves with different traces over extension fields. This is related to IDEA-ISO-a4c8e1 but uses a different mathematical machinery. The idea generator did not consider this.

**Assessment:** None of these mechanisms are likely to yield an improvement over rho, but they should have been mentioned in the Appendix as residual open directions to avoid premature closure of the broader research space.

---

## Specific Answers to Red-Team Questions

### Q1: Is the Tate theorem obstruction absolute, or are there edge cases?
**Absolute.** The Tate isogeny theorem is unconditional. No edge cases. The only "edge case" is supersingular curves (trace 0 for p > 3), but these are in a different isogeny class from ordinary curves and are unreachable via F_p-isogenies.

### Q2: Could supersingular isogenies provide a viable path?
**No.** Supersingular curves have trace 0 (for p > 3), which is different from the trace of any ordinary curve. The Tate theorem blocks F_p-isogenies between ordinary and supersingular curves. Extension-field isogenies (F_{p^k} with k > 1) can connect them, but the cost is Ω(p^{k/2}) ≥ Ω(p) (IDEA-ISO-a4c8e1), which is worse than rho.

### Q3: Could composite-order groups or pairing-friendly curves offer a different angle?
**Not within the isogeny-transfer framework.** The group order N and embedding degree k are isogeny-class invariants (they depend only on the trace t and the prime p). You cannot transfer to a composite-order group or a pairing-friendly curve via isogeny unless you're already on one. This is a consequence of the Tate theorem and the definition of embedding degree.

### Q4: Is the "within-class uniformity" obstruction truly universal, or are there exceptions?
**Not proven universal.** It's an empirical claim based on "no known algorithm depends on j." The ISO_GOAL document tested this at toy scale (ISO-EXP-A2) and found no variation, but toy-scale negatives are not theorems. The obstruction is **likely correct** but should be labeled `unverified` until the toy-scale test in IDEA-ISO-f9b2d3 is run and confirms it.

---

## Recommendations

1. **Do not close SG-ECDLP-002 in full.** The within-class uniformity obstruction is empirical, not proven. The closure should be scoped to the three proven obstructions (Tate theorem, surface-weakness gap, isogeny-finding cost).

2. **Run the toy-scale test for IDEA-ISO-f9b2d3.** This is a low-cost experiment (100 curves at bits=20) that would confirm or falsify the within-class uniformity hypothesis. If confirmed, the closure can be upgraded to include this obstruction.

3. **Label the within-class uniformity as `unverified` in any closure decision.** The other three obstructions are sufficient for a scoped closure, but the fourth should not be claimed as proven.

4. **Acknowledge the Galbraith 2024 result.** The idea generator's report does not mention Galbraith 2024 (ePrint 2024/924), which shows that the isogeny bridge is cheap (Õ(q^{1/4}) for P-256's flat volcano). This is an important point: the obstruction is NOT the cost of walking the graph, but the absence of a weak destination. The idea generator's proposals correctly identify this, but the report should explicitly acknowledge Galbraith 2024 to avoid the impression that the bridge cost is the obstruction.

5. **Add residual open directions to the Appendix.** The idea generator's Appendix A lists five approaches that were "considered and rejected before drafting." It should also list the three mechanisms in M1-M3 above as residual open directions that were not explored in this batch but are not provably dead.

---

## Verdict on Closure Recommendation

**The closure recommendation is directionally correct but premature by one evidentiary step.**

- **Three obstructions are solid:** Tate theorem (unconditional), surface-weakness gap (correct GLV analysis for generic D), isogeny-finding cost (correct random-graph heuristic for k ≥ 2).
- **One obstruction is empirical:** Within-class uniformity (no proven theorem, only "no known algorithm").
- **The conclusion is robust:** Even if the within-class uniformity is falsified at toy scale (unlikely), the other three obstructions still block the isogeny-transfer approach for generic curves.
- **The closure should be scoped:** Close SG-ECDLP-002 for the three proven obstructions, hold the within-class uniformity as `unverified` pending the toy-scale test.

**Final assessment:** The idea generator's work is **substantively correct** and the closure recommendation is **justified in its bottom line** (no viable isogeny-transfer mechanism exists for generic prime-field ECDLP). The report should be revised to (a) label the within-class uniformity as `unverified`, (b) acknowledge Galbraith 2024, and (c) add residual open directions to the Appendix. With these revisions, the closure recommendation is sound.

---

## Objections Summary

| ID | Objection | Severity | Fatal? |
|---|---|---|---|
| R1 | Within-class uniformity is empirical, not proven | SIGNIFICANT | No (other obstructions suffice) |
| R2 | GLV lattice analysis conflates constant-factor and exponent speedup | MODERATE | No (conclusion correct) |
| R3 | Extension-field isogeny cost bound is not tight for all k | MODERATE | No (conclusion robust) |
| R4 | Isogeny-graph spectral methods not considered | MINOR | No (speculative) |
| R5 | dominated_by / sota_delta calculations | None | N/A (confirmed correct) |
| R6 | Tate theorem obstruction | None | N/A (confirmed absolute) |

**Fatal objections:** None. The closure recommendation is substantively correct.

---

## Deliverables

**Report path:** `/Volumes/SSD990/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-001/batches/BATCH-d8bb19/reviews/TASK-20260807-d8bb19-redteam/red_team_report.md`

**Overall assessment:** Closure recommendation is directionally correct but premature by one evidentiary step. Three of four obstructions are structurally sound; the fourth (within-class uniformity) is empirical and should be labeled `unverified` pending toy-scale confirmation. The conclusion (no viable isogeny-transfer mechanism for generic prime-field ECDLP) is robust and justified.
