# BATCH-284817 Idea Generation Report

**Task ID:** TASK-20260808-284817-idea  
**Date:** 2026-08-08  
**Objective:** Design oracle-vs-exhaustive-search yield comparison experiment(s)

## Context

DEC-20260808-6a7ac4 rejected H-XOR-d1a480's claim that the x-oracle improves yield over exhaustive search. The rejection was based on a critical flaw: the experiment tested oracle-vs-random-predictor (Arm B vs Arm C) rather than oracle-vs-exhaustive-search (Arm B vs Arm A). The data showed Y_A = Y_B exactly across all 40 configurations, meaning the x-oracle finds the same relations as exhaustive search, just more efficiently.

## Proposals Generated

### Proposal 1: IDEA-20260808-3f8a2b (Direct Cost Comparison)

**What it tests:**
Whether the x-oracle MITM (Arm B) reduces the total field-operation cost to find relations compared to exhaustive search (Arm A), even though both find the same set of relations (Y_A = Y_B).

**How it works:**
1. Use the existing full_grid.py implementation from EXP-SEMAEV-f48dd1
2. Extract the field_operations metric for Arms A and B across all 40 configurations
3. Compute cost_ratio = field_operations_B / field_operations_A for each configuration
4. Test whether mean(cost_ratio) < 1 with a one-sided t-test at alpha=0.05
5. Compare against Pollard rho baseline

**Cost model:**
- Arm A: 2 * |F|^m operations (two additions per tuple for m=3)
- Arm B: |F|^2 (right-half table) + |F| (left-half queries) + 2 * candidates_verified
- Hypothesis: candidates_verified << |F|^{m-1}, so Arm B's total cost is significantly less

**How it avoids the Y_A = Y_B trap:**
The cost comparison measures cost_per_relation, not yield. Even though Y_A = Y_B, the cost per relation may differ. This is a legitimate measurement of computational efficiency, not yield improvement.

**Expected outcome:**
The experiment will almost certainly confirm that Arm B has lower cost per relation than Arm A (constant-factor speedup). However, this is a cost reduction, not a yield improvement, and both arms are O(|F|^m), dominated by Pollard rho O(sqrt(N)).

**Scope:**
- Toy scale (7-8 bit primes, m=3)
- Measures constant-factor cost reduction
- Does NOT measure asymptotic complexity improvement
- Does NOT measure crypto-scale performance
- Does NOT measure competitive advantage over Pollard rho

**Compute budget:** ≤5 minutes (reuses existing implementation and data)

---

### Proposal 2: IDEA-20260808-7c4e9d (True-Null Control Analysis)

**What it tests:**
Synthesizes existing evidence from EXP-SEMAEV-f48dd1 into a named obstruction for the x-oracle sub-question of RQ-ECDLP-002.

**Key insight:**
Arm C (random-from-F_p MITM) already IS the true-null control suggested by the red team. The experiment already contains all three arms (A, B, C), so no new compute is needed.

**Combined evidence synthesis:**
- Y_A = Y_B: oracle MITM finds same relations as exhaustive (no yield improvement)
- Y_C << Y_A: random MITM finds fewer relations than exhaustive (MITM framework provides no yield advantage)
- delta = Y_B - Y_C > 0: oracle is better than random (real but uninformative)
- cost_B < cost_A (predicted): oracle MITM has lower cost than exhaustive
- Both arms are O(|F|^m), dominated by Pollard rho O(sqrt(N))

**Honest conclusion:**
The x-oracle MITM provides a constant-factor cost reduction at toy scale, with no yield improvement, no asymptotic complexity change, and no path to crypto-scale. This is a named obstruction that closes the x-oracle sub-question of RQ-ECDLP-002.

**Compute budget:** Zero (analysis of existing data)

---

## Recommendation

I recommend proceeding with both proposals:

1. **IDEA-20260808-3f8a2b**: Run the direct cost comparison experiment (5 minutes of compute)
2. **IDEA-20260808-7c4e9d**: Analyze the existing data and synthesize the obstruction (zero compute)

The combined result will almost certainly be a named obstruction that closes the x-oracle sub-question of RQ-ECDLP-002: "constant-factor cost reduction at toy scale, dominated by Pollard rho, no path to crypto-scale, no asymptotic improvement."

This is consistent with the inventor protocol's closure standard: "A negative result claiming a lane is dead needs a named obstruction, an argument, and forward guidance naming what remains open."

## Completion Gates

✓ At least one proposal with falsifiable experimental test and charged cost model  
✓ Explicit dominated_by / sota_delta vs Pollard rho and vs exhaustive search  
✓ Mechanism avoids the exact equality Y_A = Y_B that rejected H-XOR-d1a480  
✗ Recommendation to close RQ-ECDLP-002 with named obstruction (not yet - awaiting experiment results)

## Next Actions

1. Review these proposals (Reviewer task)
2. If approved, execute IDEA-20260808-3f8a2b (Executor task)
3. Synthesize IDEA-20260808-7c4e9d analysis (Coordinator task)
4. Write evidence record and decision (Coordinator task)
5. Close the x-oracle sub-question of RQ-ECDLP-002 with named obstruction
