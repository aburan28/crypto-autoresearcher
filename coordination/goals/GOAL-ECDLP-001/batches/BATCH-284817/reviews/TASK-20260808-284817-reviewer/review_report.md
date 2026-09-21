# BATCH-284817 Reviewer Report

**Task ID:** TASK-20260808-284817-reviewer  
**Date:** 2026-08-08  
**Policy:** review-adversarial (xhigh reasoning effort)  
**Independent session:** yes  
**Reviewer role:** reviewer  
**Records reviewed:**
- IDEA-20260808-3f8a2b (direct cost comparison experiment)
- IDEA-20260808-7c4e9d (true-null control analysis)
- TASK-20260808-284817-idea/idea_report.md
- DEC-20260808-6a7ac4
- BATCH-284817/batch.yaml
- EV-ECDLP-65b004.yaml (evidence record cited by DEC-20260808-6a7ac4)
- Red-team report (TASK-20260808-284817-redteam)
- Validator report (TASK-20260808-284817-validator)

---

## Executive Summary

Both proposals are directionally correct and address the next_actions from DEC-20260808-6a7ac4. However, each contains significant defects that require revision before execution. The proposals are not independent: IDEA-20260808-7c4e9d's closure recommendation cites a cost reduction that IDEA-20260808-3f8a2b has not yet measured. The proposals must be executed sequentially, not in parallel.

**Overall verdict: REVISE**

---

## Per-Proposal Verdicts

### IDEA-20260808-3f8a2b: **REVISE**

### IDEA-20260808-7c4e9d: **REVISE**

---

## Detailed Assessment

### IDEA-20260808-3f8a2b: Direct Cost Comparison

#### What the proposal does well

1. **Honest novelty status.** Correctly self-identifies as `replication_with_charged_metric`, not a new mechanism. This is accurate and consistent with the inventor protocol's Pareto honesty requirement.

2. **Charged cost model.** Provides explicit field-operation counts per arm:
   - Arm A: 2 · |F|^m operations
   - Arm B: |F|^2 + |F| + 2 · candidates_verified operations
   
   This addresses the red-team's MODERATE objection from DEC-20260808-6a7ac4 that required a cost model before any "speedup" claim.

3. **Explicit falsification conditions.** Three quantitative thresholds:
   - cost_ratio >= 1.0 falsifies the hypothesis
   - candidates_verified / |F|^2 >= 0.9 falsifies the MITM filtering claim
   - field_operations_B > rho_cost shows the method is worse than Pollard rho

4. **Scope honesty.** Explicitly states:
   - Toy scale only (7-8 bit primes, m=3)
   - Constant factor only (no asymptotic improvement)
   - No path to crypto-scale
   - Dominated by Pollard rho on every axis

5. **Pseudo-replication correction.** Correctly identifies n=8 independent groups, not n=40 cells, as the correct unit of analysis.

#### Objections

**OBJ-R1: The claim conflates MITM cost reduction with oracle cost reduction (SIGNIFICANT)**

The proposal's title states: "testing whether the oracle reduces work per relation found."

But the cost model reveals that the cost reduction comes almost entirely from the **MITM structure**, not from the oracle. The arithmetic:

- Arm A: 2 · |F|^3 operations (triple-nested loop)
- Arm B: |F|^2 + 2 · candidates_verified operations (double-nested loop + verification)

For p=101, b=0.4, |F|=12:
- Arm A: 2 · 12^3 = 3,456 operations
- Arm B: 12^2 + 2·52 = 248 operations
- Cost ratio: 0.072 (14x speedup)

The 14x speedup comes from replacing O(|F|^3) with O(|F|^2). This is the standard MITM tradeoff. The oracle's contribution is limited to the value of `candidates_verified`, which the data shows is 52 for oracle queries vs ~16 for random queries (Arm C). The oracle *increases* candidates_verified by ~3x, not decreases it.

**The proposal tests "whether MITM with oracle queries reduces work compared to exhaustive search," not "whether the oracle reduces work."** These are different questions. The oracle does not reduce work; it redirects it.

**Required fix:** Reframe the title and claim to accurately reflect what the experiment tests. Example: "testing whether MITM with oracle queries reduces work compared to exhaustive search (not whether the oracle itself reduces work)."

**Severity: SIGNIFICANT.** The claim misframes the experiment's actual test.

---

**OBJ-R2: The comparison against Arm C should be primary, not secondary (SIGNIFICANT)**

The proposal's primary comparison is Arm B (oracle MITM) vs Arm A (exhaustive search). But this comparison conflates two effects:
1. The MITM structure (O(|F|^3) → O(|F|^2))
2. The oracle's query strategy (structured vs random)

To isolate the oracle's marginal contribution, the proposal should compare Arm B (oracle MITM) against Arm C (random MITM). This comparison holds the MITM structure constant and varies only the query strategy.

The data already shows the oracle's marginal contribution:
- Arm B candidates_verified: 52 (deterministic)
- Arm C candidates_verified: ~16 (varies with seed)

The oracle increases candidates_verified by ~3x. This is the oracle's actual effect: it makes the MITM filtering *less* efficient, not more. The oracle queries are structured (they hit the hash table more often), so more candidates survive to verification.

**Required fix:** Add a primary comparison: Arm B vs Arm C. This answers: "Does the oracle reduce candidates_verified compared to random queries?" The answer is no; it increases them. This is the honest result.

**Severity: SIGNIFICANT.** The proposal's primary comparison does not isolate the oracle's effect.

---

**OBJ-R3: The t-test is unnecessary given the deterministic effect size (MODERATE)**

The proposal plans a one-sided t-test at alpha=0.05 to test whether mean(cost_ratio) < 1.0. But the effect size is so large (10x-30x reduction, cost_ratio ~ 0.03-0.09) that the result is arithmetically certain. The cost reduction is deterministic given the algorithmic structure, not a statistical effect subject to noise.

The t-test would be meaningful if cost_ratio were close to 1.0 (e.g., 0.9 vs 1.1), but at 0.07, the result is not in doubt. Statistical testing is not applicable here.

**Required fix:** Remove the t-test. Replace with a simple statement: "The cost reduction is deterministic given the algorithmic structure (O(|F|^3) → O(|F|^2)); statistical testing is not applicable."

**Severity: MODERATE.** The t-test misframes the result as uncertain when it is actually deterministic.

---

**OBJ-R4: The cost model does not capture hash table overhead (MODERATE)**

The cost model counts field operations (E.add calls) but does not count:
- Hash table construction (inserting |F|^2 entries)
- Hash table lookups (|F| queries, each requiring a hash computation and dictionary lookup)
- Memory allocation for the hash table
- Cache effects (Arm A is sequential; Arm B has random access patterns)

At toy scale (|F| = 12-27), these overheads are negligible. The wall-clock data confirms this: Arm B runs in 0.0001s vs Arm A's 0.0012-0.0016s, consistent with the field-operation ratio.

However, the proposal's scope statement says "no path to crypto-scale," which implicitly acknowledges that the cost model may not scale. The objection is that the cost model's limitations should be stated explicitly as a confounder, not just as a crypto-scale extrapolation issue.

**Required fix:** Add a confounder: "The cost model counts field operations but does not count hash table construction, lookup overhead, memory allocation, or cache effects. At toy scale these are negligible; at larger scales they may dominate. This cost model is valid only at toy scale."

**Severity: MODERATE.** The cost model's limitations should be stated explicitly.

---

**OBJ-R5: The Pollard rho comparison is framed as a baseline, not a dominance statement (MINOR)**

The proposal compares the x-oracle MITM against Pollard rho as an "upper bound on what's achievable." But this is not a fair comparison:
- Pollard rho is O(sqrt(N)) time, O(1) memory
- The x-oracle MITM is O(|F|^m) time, O(|F|^2) memory

For the tested parameters, rho is 2-3 orders of magnitude faster. This is not a "baseline comparison"; it is a statement that the x-oracle MITM is not competitive with the best known generic algorithm.

The proposal's `dominated_by` field correctly states the relationship. The objection is that the minimal_test section frames the rho comparison as a "baseline" rather than a "dominance statement."

**Required fix:** Change the framing in minimal_test from "compare against Pollard rho baseline" to "confirm that the x-oracle MITM is dominated by Pollard rho."

**Severity: MINOR.** The framing is slightly misleading but does not affect the conclusion.

---

### IDEA-20260808-7c4e9d: True-Null Control Analysis

#### What the proposal does well

1. **Correct identification of Arm C as the true-null control.** The proposal correctly recognizes that Arm C (random-from-F_p MITM) is the true-null control suggested by the red team in DEC-20260808-6a7ac4. This is a valuable insight: the experiment already contains the control, so no new compute is needed.

2. **Honest novelty status.** Correctly self-identifies as `analysis_of_existing_data`, not a new experiment.

3. **Zero compute cost.** The analysis reuses existing data from EXP-SEMAEV-f48dd1.

4. **Closure recommendation.** Provides a named obstruction and forward guidance, consistent with the inventor protocol's closure standard.

#### Objections

**OBJ-R6: The closure recommendation cites a prediction, not a measurement (SIGNIFICANT)**

The proposal's closure recommendation cites cost_B < cost_A as evidence. But this cost reduction has not yet been measured; it is predicted based on the algorithmic structure. IDEA-20260808-3f8a2b is the experiment that would measure it.

The closure recommendation is based on:
1. Y_A = Y_B (already measured, confirmed) ✓
2. cost_B < cost_A (predicted, not yet measured) ✗

This violates the inventor protocol's requirement that closure be based on evidence, not prediction. If IDEA-20260808-3f8a2b were to show cost_B >= cost_A (unlikely given the arithmetic, but possible if the cost model is revised to include hash table overhead), the obstruction would be incorrect.

**Required fix:** Defer the closure recommendation until IDEA-20260808-3f8a2b has been executed and the cost reduction has been confirmed. Alternatively, state explicitly that the closure recommendation is conditional on the cost comparison experiment confirming cost_B < cost_A.

**Severity: SIGNIFICANT.** The closure recommendation is premature.

---

**OBJ-R7: The named obstruction is a restatement, not a structural argument (MODERATE)**

The inventor protocol requires: "A negative result claiming a lane is dead needs a named obstruction, an argument, and forward guidance naming what remains open."

The proposal's named obstruction is: "constant-factor cost reduction at toy scale, dominated by Pollard rho, no path to crypto-scale, no asymptotic improvement."

But this is not an obstruction; it is a restatement of what we already knew:
- Y_A = Y_B was confirmed by DEC-20260808-6a7ac4
- Both arms are O(|F|^m) was known from the algorithmic structure
- Dominated by Pollard rho was known from the complexity analysis

A true obstruction would explain **why** the lane is dead in terms of a structural barrier. For example:
- "The MITM structure inherently provides only constant-factor cost reduction because it replaces O(|F|^3) with O(|F|^2), which is a polynomial speedup, not an exponential one. The x-oracle cannot change this because it only affects the query strategy, not the algorithmic structure."
- "The x-oracle cannot beat Pollard rho because the MITM framework is fundamentally a search optimization over a finite space, not a structural attack on the discrete logarithm problem."

The proposal's obstruction is a summary of evidence, not a structural argument. It does not explain why the x-oracle MITM cannot be improved or extended; it only states that the current implementation is dominated by Pollard rho.

**Required fix:** Replace the summary of negative results with a structural argument. Example: "The MITM structure inherently provides only constant-factor cost reduction because it replaces O(|F|^3) with O(|F|^2). The x-oracle cannot change this because it only affects the query strategy, not the algorithmic structure. The lane is dead because the MITM framework is a search optimization, not a structural attack on ECDLP."

**Severity: MODERATE.** The proposal meets the letter of the inventor protocol but not the spirit.

---

**OBJ-R8: The closure is scoped too broadly (MODERATE)**

The proposal recommends closing "the x-oracle sub-question of RQ-ECDLP-002." But the experiment only tests:
- m=3 (not m=4, m=5, or other values)
- Prime fields F_p with p in {101, 103, 107, 211} (not binary fields, not extension fields)
- One specific MITM strategy (2-way split: left half = P1, right half = P2+P3)
- One specific oracle type (x-coordinate oracle)

The closure should be scoped to the exact tested configuration: "The x-oracle MITM with m=3, 2-way split, x-coordinate oracle, over prime fields at toy scale, provides only constant-factor cost reduction and is dominated by Pollard rho."

The proposal's `interpretation_limits` section acknowledges this: "The obstruction is specific to the x-oracle MITM mechanism. Other oracle types or search strategies are not addressed." But the closure recommendation does not reflect this limitation.

**Required fix:** Change the closure recommendation from "close the x-oracle sub-question of RQ-ECDLP-002" to "close the x-oracle MITM with m=3, 2-way split, x-coordinate oracle, over prime fields at toy scale."

**Severity: MODERATE.** The closure recommendation should be scoped to the exact tested configuration.

---

**OBJ-R9: Unexplored directions within the x-oracle lane are not addressed (MODERATE)**

The proposal states: "Other mechanisms and methodologies remain open." But it does not enumerate the unexplored directions within the x-oracle lane:
- Different m values (m=4, m=5): The MITM structure could be extended to m=4 with a 2-way split or a 3-way split. The cost reduction might scale differently.
- Different oracle types: y-coordinate oracle, full-point oracle, or a combination. The x-oracle is just one possibility.
- Different curve families: Binary fields F_{2^n}, extension fields F_{p^k}. The Tate obstruction may not apply in the same way.
- Different MITM strategies: 3-way split, 4-way split, or hybrid strategies. The 2-way split is just one option.

The inventor protocol requires: "forward guidance naming what remains open." The proposal's forward guidance is generic ("other mechanisms remain open") rather than specific.

**Required fix:** Add a section listing the unexplored directions within the x-oracle lane and state whether they are worth exploring or are blocked by known obstructions. For example:
- "Different m values: Not tested. The MITM structure could be extended to m=4, but the cost reduction may not scale because the hash table size grows as O(|F|^2) regardless of m."
- "Different oracle types: Not tested. The y-coordinate oracle or full-point oracle may provide different query patterns, but the fundamental MITM structure remains the same."
- "Different curve families: Not tested. Binary fields or extension fields may have different algebraic structure, but the MITM framework is generic and applies to any group."

**Severity: MODERATE.** The forward guidance should be specific, not generic.

---

## Cross-Proposal Objections

**OBJ-R10: The two proposals are not independent (SIGNIFICANT)**

IDEA-20260808-7c4e9d's obstruction synthesis cites cost_B < cost_A as evidence, but this cost reduction has not yet been measured. IDEA-20260808-3f8a2b is the experiment that would measure it. The two proposals are therefore not independent: the closure recommendation in IDEA-20260808-7c4e9d depends on the result of IDEA-20260808-3f8a2b.

The idea report recommends proceeding with both proposals in parallel:
1. Run IDEA-20260808-3f8a2b (5 minutes of compute)
2. Synthesize IDEA-20260808-7c4e9d (zero compute)

But the synthesis in step 2 cites a prediction from step 1, not a measurement. If step 1 were to show cost_B >= cost_A (unlikely but possible), the synthesis in step 2 would be incorrect.

**Required fix:** Execute the proposals sequentially, not in parallel:
1. Run IDEA-20260808-3f8a2b and confirm cost_B < cost_A
2. Then synthesize IDEA-20260808-7c4e9d using the confirmed cost reduction
3. Then recommend closure

**Severity: SIGNIFICANT.** The proposals should be executed sequentially to ensure the closure recommendation is based on evidence, not prediction.

---

## Assessment Against Completion Gates

### Gate 1: At least one proposal with falsifiable experimental test and charged cost model

**PASS.** IDEA-20260808-3f8a2b provides:
- Three falsifiable predictions with quantitative thresholds
- Three explicit falsification conditions
- Charged cost model: field operations per arm
- Statistical test (though unnecessary, per OBJ-R3)

### Gate 2: Explicit dominated_by / sota_delta vs Pollard rho and vs exhaustive search

**PASS.** Both proposals explicitly address this:
- `dominated_by`: Pollard rho (0.886·√N time, O(1) memory) and exhaustive search (same relations Y_A = Y_B)
- `sota_delta`: Zero exponent improvement; constant-factor only; exponentially worse than rho
- `target_complexity.best_known`: Cites KN-TECH-001, KN-TECH-006, KN-TECH-018, KN-TECH-031

### Gate 3: Mechanism avoids the exact equality Y_A = Y_B that rejected H-XOR-d1a480

**PASS.** IDEA-20260808-3f8a2b avoids the trap by changing the measured quantity:
- The rejected hypothesis compared yield (Y_A vs Y_B), which showed Y_A = Y_B exactly
- This proposal compares cost (field_operations_A vs field_operations_B), a different metric
- The claim explicitly acknowledges Y_A = Y_B and does not assert yield improvement
- The cost model is charged (field operations, not enumeration-space yield)

### Gate 4: OR recommendation to close RQ-ECDLP-002 with named obstruction

**PASS (conditional).** IDEA-20260808-7c4e9d provides a `closure_recommendation` field with:
- Named obstruction: "constant-factor cost reduction at toy scale, dominated by Pollard rho, no path to crypto-scale, no asymptotic improvement"
- Argument: combined evidence (Y_A = Y_B, Y_C << Y_A, cost_B < cost_A predicted, both dominated by rho)
- Forward guidance: "Other mechanisms and methodologies remain open; the x-oracle MITM is closed"

However, the closure recommendation is premature (OBJ-R6) and should be deferred until IDEA-20260808-3f8a2b has been executed.

---

## Assessment Against DEC-20260808-6a7ac4 Next Actions

### Next Action 1: "A genuine oracle-vs-exhaustive-search yield comparison (Arm A vs Arm B directly, not routed through Arm C) is the natural successor question and is NOT yet designed."

**ADDRESSED (partially).** IDEA-20260808-3f8a2b provides a direct Arm A vs Arm B comparison, but changes the metric from yield to cost. This is a legitimate response to the rejection: the decision rejected the yield claim, not the cost claim. However, the proposal should also include a yield comparison (Y_A vs Y_B) to confirm the exact equality holds in the re-run, even though this is already known.

**Remaining gap:** The proposal does not explicitly state that it will confirm Y_A = Y_B in the re-run. This should be added as a sanity check.

### Next Action 2: "A cost model (field operations or wall-clock, charged per AGENTS.md's artifact policy) is required before any future version of this line of work reports a 'speedup' claim."

**ADDRESSED.** IDEA-20260808-3f8a2b provides an explicit field-operation cost model per arm. This addresses the red-team's MODERATE objection.

### Next Action 3: "The red-team's own suggested control ('Arm D: Random-from-F_p MITM, true null model') is a related but distinct direction."

**ADDRESSED.** IDEA-20260808-7c4e9d correctly recognizes that Arm C already IS the true-null control suggested by the red team. This is a valuable insight.

---

## Validator's Blocking Defect

The validator found a blocking defect: both YAML files contain malformed YAML in the `scope.bit_sizes` field. The error:

```yaml
bit_sizes: [7-8 bits (p in {101, 103, 107, 211})]
```

Should be:

```yaml
bit_sizes: ["7-8 bits (p in {101, 103, 107, 211})"]
```

This defect must be fixed before the proposals can be ingested by downstream tooling. The fix is mechanical and does not affect the substantive content.

---

## Overall Recommendation

**REVISE and approve with conditions.**

Both proposals are directionally correct and address the next_actions from DEC-20260808-6a7ac4. However, each contains significant defects that require revision before execution.

### Required revisions for IDEA-20260808-3f8a2b:

1. **Reframe the claim.** Change the title and claim from "whether the oracle reduces work per relation found" to "whether MITM with oracle queries reduces work compared to exhaustive search." This accurately reflects what the experiment tests.

2. **Add Arm C comparison as primary.** Compare Arm B (oracle MITM) against Arm C (random MITM) to isolate the oracle's marginal contribution. This answers: "Does the oracle reduce candidates_verified compared to random queries?" The honest answer is no; it increases them.

3. **Remove the t-test.** The effect size is so large that statistical testing is unnecessary. Replace with a statement that the cost reduction is deterministic given the algorithmic structure.

4. **Add cost model limitations as a confounder.** State explicitly that the cost model does not capture hash table overhead, memory allocation, or cache effects, and is valid only at toy scale.

5. **Fix YAML syntax.** Quote the string value in `scope.bit_sizes`.

### Required revisions for IDEA-20260808-7c4e9d:

1. **Defer the closure recommendation.** Do not recommend closure until IDEA-20260808-3f8a2b has been executed and the cost reduction has been confirmed. State explicitly that the closure recommendation is conditional on the cost comparison experiment confirming cost_B < cost_A.

2. **Strengthen the named obstruction.** Replace the summary of negative results with a structural argument. Example: "The MITM structure inherently provides only constant-factor cost reduction because it replaces O(|F|^3) with O(|F|^2). The x-oracle cannot change this because it only affects the query strategy, not the algorithmic structure."

3. **Scope the closure narrowly.** Change the closure recommendation from "close the x-oracle sub-question of RQ-ECDLP-002" to "close the x-oracle MITM with m=3, 2-way split, x-coordinate oracle, over prime fields at toy scale."

4. **Enumerate unexplored directions.** Add a section listing the unexplored directions within the x-oracle lane (different m values, different oracle types, different curve families, different MITM strategies) and state whether they are worth exploring or are blocked by known obstructions.

5. **Fix YAML syntax.** Quote the string value in `scope.bit_sizes`.

### Execution order:

Execute the proposals **sequentially**, not in parallel:
1. Run IDEA-20260808-3f8a2b and confirm cost_B < cost_A
2. Then synthesize IDEA-20260808-7c4e9d using the confirmed cost reduction
3. Then recommend closure

This ensures the closure recommendation is based on evidence, not prediction.

---

## Summary of Objections

| ID | Proposal | Severity | Summary |
|----|----------|----------|---------|
| OBJ-R1 | IDEA-20260808-3f8a2b | SIGNIFICANT | Claim conflates MITM cost reduction with oracle cost reduction |
| OBJ-R2 | IDEA-20260808-3f8a2b | SIGNIFICANT | Arm C comparison should be primary, not secondary |
| OBJ-R3 | IDEA-20260808-3f8a2b | MODERATE | t-test is unnecessary given deterministic effect size |
| OBJ-R4 | IDEA-20260808-3f8a2b | MODERATE | Cost model does not capture hash table overhead |
| OBJ-R5 | IDEA-20260808-3f8a2b | MINOR | Pollard rho comparison framed as baseline, not dominance statement |
| OBJ-R6 | IDEA-20260808-7c4e9d | SIGNIFICANT | Closure recommendation cites prediction, not measurement |
| OBJ-R7 | IDEA-20260808-7c4e9d | MODERATE | Named obstruction is a restatement, not a structural argument |
| OBJ-R8 | IDEA-20260808-7c4e9d | MODERATE | Closure is scoped too broadly |
| OBJ-R9 | IDEA-20260808-7c4e9d | MODERATE | Unexplored directions within x-oracle lane are not addressed |
| OBJ-R10 | Both | SIGNIFICANT | Proposals are not independent; closure depends on cost comparison result |

**Total:** 4 SIGNIFICANT, 5 MODERATE, 1 MINOR

---

## Reviewer Attestation

- **Role:** reviewer
- **Requested policy:** review-adversarial
- **Resolved model:** fireworks-ai/accounts/fireworks/models/qwen3p7-plus
- **Reasoning effort:** xhigh
- **Independent session:** true
- **Reviewed record IDs:** IDEA-20260808-3f8a2b, IDEA-20260808-7c4e9d, TASK-20260808-284817-idea, BATCH-284817, DEC-20260808-6a7ac4, EV-ECDLP-65b004
- **Verdict:** REVISE (both proposals require revision before execution; directionally correct but contain significant defects)
