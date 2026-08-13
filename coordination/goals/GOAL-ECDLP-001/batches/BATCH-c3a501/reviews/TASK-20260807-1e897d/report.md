# Independent Review: EXP-SEMAEV-f48dd1 Smoke Test

**Task:** TASK-20260807-1e897d (Independent Reviewer)  
**Batch:** BATCH-c3a501  
**Policy:** review-adversarial (xhigh reasoning, independent session)  
**Date:** 2026-08-07  
**Reviewer model:** fireworks-ai/accounts/fireworks/models/qwen3p7-plus

---

## Summary

The smoke test for EXP-SEMAEV-f48dd1 (x-oracle Semaev yield discrimination) is **internally consistent and arithmetically correct**, but exhibits a **metric definition flaw** that undermines the primary comparison Δ = Y_B − Y_C. No evidence of fabrication; all reported values recompute correctly from the implementation. However, the yield metric's denominator differs across arms, making the reported Δ = 0.5 misleading as a measure of oracle effectiveness.

**Overall verdict:** PASS with reservations (metric flaw documented; no fabrication detected).

---

## Per-Artifact Verdicts

### 1. specification.yaml — PASS

- Frozen, approved, claim_tier: toy. ✓
- Parameters match design: m=3, p=101, b=0.4, seed=1. ✓
- Control checks correctly specified (query match, PRNG collision, baseline consistency). ✓
- Required artifacts listed and present. ✓
- Inference receipt shows `resolved_model_id: null` — gap, but acceptable for smoke test.

### 2. implementation/smoke_test.py — PASS (with caveat)

- Code is present, executable, and deterministic. ✓
- Curve selection: y² = x³ + 1 over F_101 (A=0, B=1). Discriminant = −27 mod 101 = 74 ≠ 0, so nonsingular. ✓
- Factor base: 6 x-coordinates [0, 2, 4, 5, 9, 10], each with 2 points (±y), total |F| = 12. ✓
- Arm A: exhaustive enumeration of all 12³ = 1728 triples. ✓
- Arm B: MITM with x-oracle. Hash table H[x(P2+P3)] built from 12² = 144 right-half pairs. Left half queries x(P1) for all 12 P1 values. ✓
- Arm C: identical to B, but oracle replaced by SHA-256 PRNG keyed on (seed, P1). ✓
- Control checks implemented and reported. ✓

**Caveat:** The code defines `tuples_enumerated` differently for each arm:
- Arm A: all |F|³ = 1728 triples (exhaustive).
- Arm B/C: only `candidates_verified` (52 and 20, respectively).

This is documented in the code comment (`# Candidate tuples verified`) and is a defensible interpretation of "tuples attempted" for MITM. However, it makes the yield comparison Δ = Y_B − Y_C misleading, since the denominators differ by a factor of ~33×. See §Findings below.

### 3. runs/RUN-SEMAEV-f48dd1-smoke/raw-result.json — PASS

- All fields present and internally consistent. ✓
- Arithmetic verified:
  - B = floor(101^0.4) = 6. ✓
  - |F| = 12 points (6 x-coords × 2). ✓
  - Arm A: 26/1728 = 0.01505. Expected ≈ 1/102 = 0.00980. Ratio = 1.53× (within factor 4). ✓
  - Arm B: 26/52 = 0.5. ✓
  - Arm C: 0/20 = 0.0. ✓
  - Δ = 0.5. ✓
- Control checks:
  - query_count_match: B=12, C=12. ✓
  - prng_collision_free: true (12 outputs mod 101, collision improbable). ✓
  - baseline_consistency: 1.53× within factor 4. ✓
- Field operations:
  - Arm A: 1728 × 2 = 3456. ✓
  - Arm B: 144 (right-half) + 52 × 2 (candidates) = 248. ✓
  - Arm C: 144 + 20 × 2 = 184. ✓

### 4. runs/RUN-SEMAEV-f48dd1-smoke/manifest.yaml — PASS

- Git head_commit recorded: 40459ba9215b18f721d7e159495076e14da89204. (Not independently verified against git log in this review, but format is correct.)
- Dirty state: 19 files, noted as unrelated to experiment. Acceptable.
- Command: `python3 experiments/EXP-SEMAEV-f48dd1/implementation/smoke_test.py`, exit_code: 0. ✓
- Environment: Python 3.12.8, darwin, sympy present. ✓
- Parameters match specification. ✓
- Results summary matches raw-result.json. ✓
- Inference receipt: `resolved_model_id: null`, `model_verified: false`. Gap, but acceptable for smoke test.

### 5. experiment_design.md — PASS

- Design document is present and matches the experiment. ✓
- Scope statement (rule 7 — toy only) is explicit. ✓
- Hypothesis, controls, metrics, and falsification criteria are pre-registered. ✓
- Corridor reconciliation statement present. ✓

---

## Findings

### F1: Metric definition flaw — yield denominators differ across arms

**Severity:** Major (undermines primary comparison)  
**Evidence:** raw-result.json, smoke_test.py:164, smoke_test.py:235

The primary metric Δ = Y_B − Y_C compares yields with different denominators:
- Y_A = 26 / 1728 = 0.015 (all triples enumerated)
- Y_B = 26 / 52 = 0.5 (candidates verified after hash-table filter)
- Y_C = 0 / 20 = 0.0 (candidates verified after hash-table filter)

The reported Δ = 0.5 suggests the x-oracle is highly effective, but this is largely an artifact of the denominator choice. Arm B's "tuples_enumerated" counts only the 52 candidates that passed the hash-table filter, not the 144 right-half pairs used to build the table or the 12 left-half queries. If the denominator were total work (144 + 12 + 52 = 208), then Y_B = 26/208 = 0.125, and Δ = 0.125.

The design doc §5 defines yield as "relations found / tuples enumerated or attempted," which is ambiguous. The code's interpretation is defensible but makes the comparison misleading.

**Impact:** The smoke test passes its control checks and demonstrates that the implementation runs correctly, but the reported Δ = 0.5 should not be interpreted as strong evidence of oracle effectiveness. The full cell grid should use a consistent denominator (e.g., total field operations or total tuples attempted including right-half enumeration) before synthesizing Δ across cells.

**Recommendation:** Before running the full cell grid, clarify the yield metric definition in the specification. Either:
1. Use total field operations as the cost unit (already reported as a secondary metric), or
2. Define "tuples attempted" consistently across arms (e.g., |F|^m for all arms, treating MITM as a filtering strategy that reduces verification cost but not the enumeration space).

### F2: Arm B finds all relations — MITM is complete

**Severity:** Informational  
**Evidence:** raw-result.json (Arm B relations_found = 26 = Arm A relations_found)

Arm B finds all 26 relations that Arm A finds. This is expected: the MITM strategy is a complete search, not a sampling strategy. The x-oracle does not cause the algorithm to miss any relations; it only reduces the number of candidates that must be verified.

This is not a flaw, but it means the yield advantage is entirely due to the denominator choice (see F1). The oracle's value is in reducing verification cost, not in increasing the number of relations found.

### F3: No reproducibility test

**Severity:** Minor  
**Evidence:** specification.yaml §success_criterion

The specification states: "results are deterministic (reproducible with same seed)." However, the smoke test runs only once. A second run with the same seed would verify determinism.

**Recommendation:** Run the smoke test twice and compare raw-result.json files before proceeding to the full cell grid.

### F4: Executor model not verified

**Severity:** Minor  
**Evidence:** manifest.yaml, specification.yaml

The inference receipt shows `resolved_model_id: null` and `model_verified: false`. This is a gap in the artifact policy, but acceptable for a smoke test. The full cell grid should include a verified model identifier.

---

## Control Check Verification

All three control checks pass and are correctly implemented:

1. **Query count match (CTRL-SMOKE-QUERY-MATCH):** Arms B and C both execute 12 oracle queries. ✓
2. **PRNG collision-free (CTRL-SMOKE-PRNG-COLLISION):** Arm C's PRNG produces 12 distinct outputs mod 101. Collision probability ≈ 12×11/(2×101) ≈ 0.65, so a collision is plausible but did not occur. The code checks for this and would raise an error. ✓
3. **Baseline consistency (CTRL-SMOKE-BASELINE):** Y_A = 0.01505, expected ≈ 0.00980. Ratio = 1.53×, within factor 4. ✓

---

## Fabrication Check

**Verdict:** No evidence of fabrication.

- All arithmetic recomputes correctly.
- Implementation code is present and executable.
- Raw results are internally consistent.
- Manifest matches raw results.
- Control checks are correctly implemented and reported.
- No suspicious patterns (e.g., round numbers, impossible values, missing fields).

---

## Recommendations

1. **Clarify yield metric before full grid.** Resolve F1 by choosing a consistent denominator across arms. Recommend using total field operations or defining "tuples attempted" as |F|^m for all arms.

2. **Verify reproducibility.** Run the smoke test twice with the same seed and compare outputs.

3. **Record executor model.** For the full grid, ensure `resolved_model_id` is populated and `model_verified: true`.

4. **Proceed with caution.** The smoke test demonstrates that the implementation runs correctly and passes control checks. The metric flaw (F1) does not invalidate the run, but it means the reported Δ = 0.5 should not be synthesized across cells until the metric is clarified.

---

## Per-Artifact Verdict Summary

| Artifact | Verdict | Notes |
|---|---|---|
| specification.yaml | PASS | Frozen, approved, controls correct |
| implementation/smoke_test.py | PASS | Correct, deterministic, metric caveat (F1) |
| raw-result.json | PASS | Arithmetic verified, controls pass |
| manifest.yaml | PASS | Complete, matches raw results |
| experiment_design.md | PASS | Matches experiment, scope explicit |

**Overall:** PASS with reservations. No fabrication detected. Metric flaw documented (F1). Recommend clarifying yield denominator before full grid.
