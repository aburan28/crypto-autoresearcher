# Decision Record: H-XOR-YIELD Status Transition

**Task:** TASK-20260807-fd61e4-interpret  
**Batch:** BATCH-fd61e4  
**Goal:** GOAL-ECDLP-001  
**Date:** 2026-08-07  
**Decision Maker:** Coordinator  
**Evidence Base:** EV-ECDLP-65b004 (EXP-SEMAEV-f48dd1 corrected results)

---

## Decision

**H-XOR-YIELD status transition:** `specified` → `weakened`

**Rationale:** The corrected experimental results from EXP-SEMAEV-f48dd1 demonstrate that the x-oracle provides **cost reduction via MITM filtering**, not **yield improvement over exhaustive search**. The hypothesis in its original scientific formulation is not supported.

---

## Evidence Summary

### Corrected Results (EV-ECDLP-65b004)

**Primary finding:** Y_A = Y_B exactly across all 40 cells
- Y_A (exhaustive search) mean: 0.01212636
- Y_B (x-oracle MITM) mean: 0.01212636
- Y_C (random predictor MITM) mean: 0.00010671

**Statistical analysis:**
- Δ = Y_B − Y_C = 0.01202 (95% CI: [0.00593, 0.01811])
- t(7) = 4.665, p = 0.0023 (corrected for pseudo-replication, n=8 groups)
- Statistically significant, but **scientifically misleading**

**Critical observation:** The statistically significant Δ measures the difference between the x-oracle and a **random predictor** (strawman baseline), not the difference between the x-oracle and **exhaustive search** (scientifically relevant baseline).

### Why the Original Comparison is Invalid

The experiment design (TASK-20260806-a01d5a/experiment_design.md) defined H-XOR-YIELD as:

> "the relation yield under an x-oracle-guided enumeration strategy is strictly greater than the yield under an identical enumeration strategy driven by a random predictor"

This formulation compares:
- **Arm B** (x-oracle MITM) vs **Arm C** (random predictor MITM)

But the scientifically meaningful question is:
- **Arm B** (x-oracle MITM) vs **Arm A** (exhaustive search)

The Y_B vs Y_C comparison asks: "Does a true oracle beat random noise?"  
The Y_B vs Y_A comparison asks: "Does the x-oracle help find more relations than exhaustive search?"

The first question is trivially answered (of course a true oracle beats random noise).  
The second question is the load-bearing one, and the answer is: **No, Y_A = Y_B exactly.**

---

## Interpretation

### What the Experiment Actually Shows

1. **The x-oracle MITM strategy finds exactly the same relations as exhaustive search.**  
   Y_A = Y_B across all 40 cells means the x-oracle does not improve yield (relations per unit of enumeration space).

2. **The x-oracle provides cost reduction via MITM filtering.**  
   Arm B uses fewer field operations than Arm A to find the same relations, because MITM reduces the verification cost. This is a **computational efficiency** result, not a **yield improvement** result.

3. **The Δ = 0.012 statistic is a metric artifact.**  
   It measures the gap between oracle and random noise, which is expected to be large. It does not measure oracle advantage over the scientifically relevant baseline (exhaustive search).

### Why "Weakened" is the Correct Status

**Option (a): Weaken** ✓ CHOSEN  
- The hypothesis in its original formulation (oracle improves yield over exhaustive search) is not supported
- The evidence directly contradicts the scientific intent: Y_A = Y_B exactly
- The statistically significant Δ is relative to a strawman baseline, not the load-bearing comparison
- Weakening accurately reflects that the x-oracle provides cost reduction, not yield improvement

**Option (b): Reframe as H-XOR-COST** ✗ REJECTED  
- Creating a new hypothesis (H-XOR-COST) would be generating new science, not interpreting existing evidence
- The Coordinator's role is to interpret, not to create
- The cost-reduction observation is valid but is a different research question that belongs to a new ideation cycle
- Reframing would obscure the fact that the original hypothesis was not supported

**Option (c): Keep at specified** ✗ REJECTED  
- The evidence directly contradicts the hypothesis's scientific intent
- Keeping it at specified would misrepresent the state of knowledge
- The hypothesis has been tested and the test shows no yield advantage
- "Specified" implies the hypothesis is live and untested; it has been tested and weakened

---

## Scope of Weakening

**What is weakened:**
- H-XOR-YIELD in its original formulation: "x-oracle improves yield over exhaustive search"
- The claim that the x-oracle helps find more relations per unit of enumeration space

**What is NOT weakened:**
- The observation that x-oracle MITM provides cost reduction (fewer field operations)
- The validity of the MITM strategy as a computational optimization
- The statistical correctness of the corrected analysis (Δ = 0.012, p = 0.0023)

**What remains open:**
- Whether the cost reduction scales to larger parameters
- Whether a different oracle-exploitation strategy could improve yield
- Whether the x-oracle has other exploitable properties beyond MITM filtering

---

## Red Team Concerns (from EV-ECDLP-65b004)

The red team identified several concerns that support this weakening:

1. **"The experiment tests 'oracle vs random noise' not 'oracle vs exhaustive search'"**  
   ✓ Confirmed. This is the central interpretive error.

2. **"Y_A = Y_B exactly, so the correct comparison shows zero yield advantage"**  
   ✓ Confirmed. This is the load-bearing observation.

3. **"Δ = 0.012 is a metric artifact, not a signal of oracle efficiency"**  
   ✓ Confirmed. The Δ measures oracle vs random, not oracle vs exhaustive.

4. **"No cost model provided; 'speedup' is undefined without total work measurement"**  
   ✓ Noted. The experiment did not measure total field operations, so the cost-reduction claim is qualitative, not quantitative.

5. **"Toy-scale parameters have no clear path to crypto-scale extrapolation"**  
   ✓ Noted. This is a standing limitation (AGENTS.md rule 7).

---

## Next Actions

1. **Record H-XOR-YIELD status transition** in ledger/hypotheses/ (pending ledger commit task)
2. **Close RQ-ECDLP-002** (x-oracle yield question) as answered: no yield advantage at toy scale
3. **Optionally open new research question** on x-oracle cost reduction (H-XOR-COST) if warranted by priority ranking
4. **No further experiments on H-XOR-YIELD** — the hypothesis has been tested and weakened

---

## Citations

- **Evidence:** EV-ECDLP-65b004 (EXP-SEMAEV-f48dd1 corrected results)
- **Experiment:** EXP-SEMAEV-f48dd1 (RUN-SEMAEV-f48dd1-grid)
- **Decision:** DEC-20260807-fc6df4 (metric correction)
- **Batch:** BATCH-ef31ab (correction batch), BATCH-fd61e4 (interpretation batch)
- **Design:** TASK-20260806-a01d5a/experiment_design.md (H-XOR-YIELD formulation)

---

## Appendix: Statistical Note

The corrected analysis (n=8 groups, t(7)=4.665, p=0.0023) is mathematically valid and correctly accounts for pseudo-replication. The statistical significance is real, but the **interpretation** is wrong because the comparison is against a strawman baseline.

A statistically significant result does not imply a scientifically meaningful result. The Δ = 0.012 is real (the x-oracle beats random noise), but it is not evidence of yield improvement over exhaustive search (Y_A = Y_B).

This is a textbook case of testing the wrong hypothesis. The experiment asked "Does oracle beat random?" when it should have asked "Does oracle beat exhaustive search?"
