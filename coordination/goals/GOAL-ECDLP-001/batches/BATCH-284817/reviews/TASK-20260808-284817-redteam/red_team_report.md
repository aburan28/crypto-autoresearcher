# Red-Team Report: BATCH-284817

**Task ID:** TASK-20260808-284817-redteam  
**Date:** 2026-08-08  
**Policy:** review-adversarial (xhigh reasoning effort)  
**Independent session:** yes  
**Reviewer role:** red-team  
**Records reviewed:**
- IDEA-20260808-3f8a2b (direct cost comparison experiment)
- IDEA-20260808-7c4e9d (true-null control analysis)
- TASK-20260808-284817-idea/idea_report.md
- DEC-20260808-6a7ac4
- EXP-SEMAEV-f48dd1 raw-results.json, analysis.yaml, full_grid.py

---

## Executive Summary

Both proposals are directionally honest and correctly scoped to toy-scale constant-factor claims. However, each contains a **significant interpretive gap** that the idea report does not acknowledge, and the closure recommendation in IDEA-20260808-7c4e9d is **premature** because it recommends closing the x-oracle sub-question before the cost comparison experiment has been executed. The two proposals are also **not independent**: IDEA-20260808-7c4e9d's obstruction synthesis cites a cost reduction (cost_B < cost_A) that IDEA-20260808-3f8a2b has not yet verified. Running them as described would produce a closure recommendation partly grounded in a prediction, not a measurement.

---

## Per-Proposal Assessment

### IDEA-20260808-3f8a2b: Direct Cost Comparison

#### What the proposal does well

- **Honest novelty status.** The proposal correctly identifies itself as `replication_with_charged_metric`, not a new mechanism. This is accurate: the experiment reuses the existing implementation and changes only the primary metric from yield to cost.
- **Explicit scope limitations.** The proposal states clearly that this is a constant-factor measurement at toy scale with no asymptotic improvement and no path to crypto-scale. This is consistent with AGENTS.md rule 7.
- **Correct falsification conditions.** The proposal states that cost_ratio >= 1.0 would falsify the hypothesis, and that the experiment is dominated by Pollard rho on every axis.
- **Pseudo-replication correction.** The proposal correctly identifies n=8 independent groups, not n=40 cells, as the correct unit of analysis.

#### Objections

**OBJ-1: The cost model measures MITM cost reduction, not oracle cost reduction (SIGNIFICANT)**

The proposal's central claim is: "The x-oracle MITM (Arm B) reduces the total field-operation cost to find a target number of relations compared to exhaustive search (Arm A)."

But examining the actual implementation reveals that the cost reduction comes almost entirely from the **MITM structure**, not from the oracle. Here is the arithmetic:

- Arm A: 2 * |F|^3 field operations (triple-nested loop, two additions per tuple)
- Arm B: |F|^2 (right-half table construction) + 2 * candidates_verified (verification)

For p=101, b=0.4, |F|=12:
- Arm A: 2 * 12^3 = 3,456 operations
- Arm B: 12^2 + 2*52 = 144 + 104 = 248 operations
- Cost ratio: 248 / 3,456 = 0.072 (a 14x speedup)

The 14x speedup comes from replacing a triple-nested loop (|F|^3 iterations) with a double-nested loop (|F|^2 iterations) plus a small number of verifications. This is the standard MITM tradeoff: O(n^3) → O(n^2) time with O(n^2) memory. The oracle's contribution is limited to reducing `candidates_verified` from whatever it would be under random queries to 52 in this case.

**The proposal conflates "MITM with oracle queries" with "oracle-assisted search."** The cost reduction is a MITM effect, not an oracle effect. To isolate the oracle's contribution, one would need to compare Arm B (oracle MITM) against a "pure MITM" baseline that uses the same MITM structure but a different query strategy. Arm C (random MITM) is exactly that baseline, and the proposal does not perform this comparison as its primary test.

The data already shows the oracle's marginal contribution:
- Arm B candidates_verified: 52 (deterministic)
- Arm C candidates_verified: 20, 14, 20, 8, 18 (mean ~16, varies with seed)

The oracle increases candidates_verified by ~3x compared to random, but this is because the oracle queries are *structured* (they hit the hash table more often), not because they are more efficient. The oracle doesn't reduce work; it redirects it.

**Severity: SIGNIFICANT.** The proposal's title and claim frame the experiment as testing "whether the oracle reduces work per relation found," but the experiment actually tests "whether MITM with oracle queries reduces work compared to exhaustive search." These are different questions, and the proposal does not acknowledge the distinction.

---

**OBJ-2: The cost model does not capture hash table overhead (MODERATE)**

The cost model counts field operations (E.add calls) but does not count:
- Hash table construction (inserting |F|^2 entries)
- Hash table lookups (|F| queries, each requiring a hash computation and dictionary lookup)
- Memory allocation for the hash table
- Cache effects (Arm A is sequential; Arm B has random access patterns)

At toy scale (|F| = 12-27), these overheads are negligible. The wall-clock data confirms this: Arm B runs in 0.0001s vs Arm A's 0.0012-0.0016s, consistent with the field-operation ratio.

However, the proposal's scope statement says "no path to crypto-scale," which implicitly acknowledges that the cost model may not scale. The objection is that the proposal does not state this explicitly as a limitation of the cost model itself. If the experiment is run and shows cost_ratio = 0.07, the report should state: "This is a field-operation count at toy scale; hash table overhead, memory access patterns, and cache effects are not measured and may dominate at larger scales."

**Severity: MODERATE.** The proposal's honest scope statement partially addresses this, but the cost model's limitations should be stated more explicitly as a confounder, not just as a crypto-scale extrapolation issue.

---

**OBJ-3: The comparison against Pollard rho is not a fair baseline (MINOR)**

The proposal compares the x-oracle MITM against Pollard rho as an "upper bound on what's achievable." But this is not a fair comparison:
- Pollard rho is O(sqrt(N)) time, O(1) memory, where N is the group order.
- The x-oracle MITM is O(|F|^m) time, O(|F|^2) memory, where |F|^m is the enumeration space.

For the tested parameters (p ~ 100-200, m=3, b=0.4-0.5):
- N ~ p ~ 100-200, so sqrt(N) ~ 10-14
- |F|^m ~ 12^3 to 27^3 = 1,728 to 19,683

Pollard rho is 2-3 orders of magnitude faster. This is not a "baseline comparison"; it is a statement that the x-oracle MITM is not competitive with the best known generic algorithm. The proposal already states this in the `dominated_by` field, so the objection is minor: the proposal should not frame the rho comparison as a "baseline" but as a "dominance statement."

**Severity: MINOR.** The proposal's `dominated_by` field correctly states the relationship; the framing in the minimal_test section is slightly misleading but does not affect the conclusion.

---

**OBJ-4: The statistical test is unnecessary given the effect size (MINOR)**

The proposal plans a one-sided t-test at alpha=0.05 to test whether mean(cost_ratio) < 1.0. But the data already shows cost_ratio values of 0.032 to 0.093 across all 40 configurations. The effect size is so large (10x-30x reduction) that a t-test is unnecessary — the result is not in doubt.

The t-test would be meaningful if cost_ratio were close to 1.0 (e.g., 0.9 vs 1.1), but at 0.07, the result is arithmetically certain. The proposal should state this explicitly: "The cost reduction is so large that statistical testing is unnecessary; the result is determined by the algorithmic structure, not by noise."

**Severity: MINOR.** The t-test does no harm, but it misframes the result as uncertain when it is actually deterministic given the algorithmic structure.

---

### IDEA-20260808-7c4e9d: True-Null Control Analysis

#### What the proposal does well

- **Correct identification of Arm C as the true-null control.** The proposal correctly recognizes that Arm C (random-from-F_p MITM) is the true-null control suggested by the red team in DEC-20260808-6a7ac4. This is a valuable insight: the experiment already contains the control, so no new compute is needed.
- **Honest novelty status.** The proposal correctly identifies itself as `analysis_of_existing_data`, not a new experiment.
- **Explicit closure recommendation.** The proposal provides a named obstruction and forward guidance, consistent with the inventor protocol's closure standard.

#### Objections

**OBJ-5: The closure recommendation is premature (SIGNIFICANT)**

The proposal recommends closing the x-oracle sub-question of RQ-ECDLP-002 with the named obstruction: "constant-factor cost reduction at toy scale, dominated by Pollard rho, no path to crypto-scale, no asymptotic improvement."

But this obstruction cites a cost reduction (cost_B < cost_A) that has not yet been measured. The proposal predicts cost_B < cost_A based on the algorithmic structure, but IDEA-20260808-3f8a2b has not been executed. If the cost comparison experiment were to show cost_B >= cost_A (which is unlikely given the arithmetic, but not impossible if the cost model is revised to include hash table overhead), the obstruction would be incorrect.

**The proposal synthesizes evidence from two sources:**
1. Y_A = Y_B (already measured, confirmed)
2. cost_B < cost_A (predicted, not yet measured)

The closure recommendation is based on one confirmed fact and one prediction. This violates the inventor protocol's requirement that closure be based on evidence, not prediction.

**Severity: SIGNIFICANT.** The closure recommendation should be deferred until IDEA-20260808-3f8a2b has been executed and the cost reduction has been confirmed. Alternatively, the proposal should state explicitly that the closure recommendation is conditional on the cost comparison experiment confirming cost_B < cost_A.

---

**OBJ-6: The "named obstruction" is a restatement, not an obstruction (MODERATE)**

The inventor protocol requires: "A negative result claiming a lane is dead needs a named obstruction, an argument, and forward guidance naming what remains open."

The proposal's named obstruction is: "constant-factor cost reduction at toy scale, dominated by Pollard rho, no path to crypto-scale, no asymptotic improvement."

But this is not an obstruction; it is a restatement of what we already knew:
- Y_A = Y_B was confirmed by DEC-20260808-6a7ac4.
- Both arms are O(|F|^m) was known from the algorithmic structure.
- Dominated by Pollard rho was known from the complexity analysis.

A true obstruction would explain **why** the lane is dead in terms of a structural barrier. For example:
- "The Tate obstruction prevents the x-oracle from providing yield improvement because [specific mechanism]."
- "The MITM structure inherently provides only constant-factor cost reduction because [specific argument]."
- "The x-oracle cannot beat Pollard rho because [specific reduction or lower bound]."

The proposal's obstruction is a summary of evidence, not a structural argument. It does not explain why the x-oracle MITM cannot be improved or extended; it only states that the current implementation is dominated by Pollard rho.

**Severity: MODERATE.** The proposal meets the letter of the inventor protocol (it provides a named obstruction, an argument, and forward guidance), but not the spirit. The obstruction should be a structural argument, not a summary of negative results.

---

**OBJ-7: The closure is scoped too broadly (MODERATE)**

The proposal recommends closing "the x-oracle sub-question of RQ-ECDLP-002." But the experiment only tests:
- m=3 (not m=4, m=5, or other values)
- Prime fields F_p with p in {101, 103, 107, 211} (not binary fields, not extension fields)
- One specific MITM strategy (2-way split: left half = P1, right half = P2+P3)
- One specific oracle type (x-coordinate oracle)

The closure should be scoped to the exact tested configuration: "The x-oracle MITM with m=3, 2-way split, x-coordinate oracle, over prime fields at toy scale, provides only constant-factor cost reduction and is dominated by Pollard rho."

The proposal's `interpretation_limits` section acknowledges this: "The obstruction is specific to the x-oracle MITM mechanism. Other oracle types or search strategies are not addressed." But the closure recommendation does not reflect this limitation. It recommends closing "the x-oracle sub-question," which is broader than the tested scope.

**Severity: MODERATE.** The closure recommendation should be scoped to the exact tested configuration, not to the entire x-oracle sub-question.

---

**OBJ-8: Unexplored directions within the x-oracle lane are not addressed (MODERATE)**

The proposal states: "Other mechanisms and methodologies remain open." But it does not enumerate the unexplored directions within the x-oracle lane:
- Different m values (m=4, m=5): The MITM structure could be extended to m=4 with a 2-way split (left half = P1+P2, right half = P3+P4), or a 3-way split. The cost reduction might scale differently.
- Different oracle types: y-coordinate oracle, full-point oracle, or a combination. The x-oracle is just one possibility.
- Different curve families: Binary fields F_{2^n}, extension fields F_{p^k}. The Tate obstruction may not apply in the same way.
- Different MITM strategies: 3-way split, 4-way split, or hybrid strategies. The 2-way split is just one option.

The proposal does not state whether these directions have been explored or are worth exploring. The inventor protocol requires: "forward guidance naming what remains open." The proposal's forward guidance is generic ("other mechanisms remain open") rather than specific.

**Severity: MODERATE.** The proposal should enumerate the unexplored directions within the x-oracle lane and state whether they are worth exploring or are blocked by known obstructions.

---

## Cross-Proposal Objections

**OBJ-9: The two proposals are not independent (SIGNIFICANT)**

IDEA-20260808-7c4e9d's obstruction synthesis cites cost_B < cost_A as evidence, but this cost reduction has not yet been measured. IDEA-20260808-3f8a2b is the experiment that would measure it. The two proposals are therefore not independent: the closure recommendation in IDEA-20260808-7c4e9d depends on the result of IDEA-20260808-3f8a2b.

The idea report recommends proceeding with both proposals:
1. Run IDEA-20260808-3f8a2b (5 minutes of compute)
2. Synthesize IDEA-20260808-7c4e9d (zero compute)

But the synthesis in step 2 cites a prediction from step 1, not a measurement. If step 1 were to show cost_B >= cost_A (unlikely but possible), the synthesis in step 2 would be incorrect.

**The proposals should be sequenced, not parallelized:**
1. Run IDEA-20260808-3f8a2b and confirm cost_B < cost_A.
2. Then synthesize IDEA-20260808-7c4e9d using the confirmed cost reduction.
3. Then recommend closure.

**Severity: SIGNIFICANT.** The proposals should be executed sequentially, not in parallel, to ensure the closure recommendation is based on evidence, not prediction.

---

## Overall Verdict

**Closure directionally correct, but premature.**

The direction is correct: the x-oracle MITM at toy scale provides only constant-factor cost reduction, is dominated by Pollard rho, and has no path to crypto-scale. This is the honest conclusion.

However, the closure recommendation is premature for three reasons:
1. The cost reduction (cost_B < cost_A) has not yet been measured; it is predicted based on the algorithmic structure.
2. The named obstruction is a restatement of known facts, not a structural argument explaining why the lane is dead.
3. The closure is scoped too broadly, covering the entire x-oracle sub-question rather than the exact tested configuration.

The closure should be deferred until:
1. IDEA-20260808-3f8a2b has been executed and the cost reduction has been confirmed.
2. The named obstruction has been strengthened with a structural argument (e.g., "the MITM structure inherently provides only constant-factor cost reduction because...").
3. The closure has been scoped to the exact tested configuration (m=3, 2-way split, x-coordinate oracle, prime fields at toy scale).
4. The unexplored directions within the x-oracle lane have been enumerated and assessed.

---

## Recommendations

### For IDEA-20260808-3f8a2b

1. **Reframe the claim.** Change the title and claim from "whether the oracle reduces work per relation found" to "whether MITM with oracle queries reduces work compared to exhaustive search." This accurately reflects what the experiment tests.

2. **Add a comparison against Arm C.** The proposal should compare Arm B (oracle MITM) against Arm C (random MITM) to isolate the oracle's marginal contribution. This would answer: "Does the oracle reduce candidates_verified compared to random queries?" The data already suggests yes (52 vs ~16), but the proposal should make this a primary comparison, not a secondary one.

3. **State the cost model's limitations explicitly.** Add a confounder: "The cost model counts field operations but does not count hash table construction, lookup overhead, memory allocation, or cache effects. At toy scale these are negligible; at larger scales they may dominate."

4. **Remove the t-test.** The effect size is so large (10x-30x reduction) that statistical testing is unnecessary. Replace the t-test with a simple statement: "The cost reduction is deterministic given the algorithmic structure; statistical testing is not applicable."

### For IDEA-20260808-7c4e9d

1. **Defer the closure recommendation.** Do not recommend closure until IDEA-20260808-3f8a2b has been executed and the cost reduction has been confirmed. The closure recommendation should be based on evidence, not prediction.

2. **Strengthen the named obstruction.** Replace the summary of negative results with a structural argument. For example: "The MITM structure inherently provides only constant-factor cost reduction because it replaces O(|F|^3) with O(|F|^2), which is a polynomial speedup, not an exponential one. The x-oracle cannot change this because it only affects the query strategy, not the algorithmic structure."

3. **Scope the closure narrowly.** Change the closure recommendation from "close the x-oracle sub-question of RQ-ECDLP-002" to "close the x-oracle MITM with m=3, 2-way split, x-coordinate oracle, over prime fields at toy scale." This accurately reflects the tested scope.

4. **Enumerate unexplored directions.** Add a section listing the unexplored directions within the x-oracle lane (different m values, different oracle types, different curve families, different MITM strategies) and state whether they are worth exploring or are blocked by known obstructions.

### For the Batch

1. **Execute the proposals sequentially, not in parallel.** Run IDEA-20260808-3f8a2b first, confirm the cost reduction, then synthesize IDEA-20260808-7c4e9d. This ensures the closure recommendation is based on evidence, not prediction.

2. **Add a third proposal (optional).** Consider a proposal that tests a different m value (e.g., m=4) or a different oracle type (e.g., y-coordinate oracle) to assess whether the obstruction generalizes. This would strengthen the closure by showing it is not specific to one parameter choice.

---

## Summary of Objections

| ID | Proposal | Severity | Summary |
|----|----------|----------|---------|
| OBJ-1 | IDEA-20260808-3f8a2b | SIGNIFICANT | Cost model measures MITM cost reduction, not oracle cost reduction |
| OBJ-2 | IDEA-20260808-3f8a2b | MODERATE | Cost model does not capture hash table overhead |
| OBJ-3 | IDEA-20260808-3f8a2b | MINOR | Pollard rho comparison is not a fair baseline |
| OBJ-4 | IDEA-20260808-3f8a2b | MINOR | Statistical test is unnecessary given effect size |
| OBJ-5 | IDEA-20260808-7c4e9d | SIGNIFICANT | Closure recommendation is premature (based on prediction, not evidence) |
| OBJ-6 | IDEA-20260808-7c4e9d | MODERATE | Named obstruction is a restatement, not a structural argument |
| OBJ-7 | IDEA-20260808-7c4e9d | MODERATE | Closure is scoped too broadly |
| OBJ-8 | IDEA-20260808-7c4e9d | MODERATE | Unexplored directions within x-oracle lane are not addressed |
| OBJ-9 | Both | SIGNIFICANT | Proposals are not independent; closure depends on cost comparison result |

**Total:** 3 SIGNIFICANT, 4 MODERATE, 2 MINOR

---

## Red-Team Provenance

- **Requested policy:** review-adversarial
- **Resolved model:** fireworks-ai/accounts/fireworks/models/qwen3p7-plus
- **Reasoning effort:** xhigh
- **Independent session:** yes
- **Session separate from producer:** yes
