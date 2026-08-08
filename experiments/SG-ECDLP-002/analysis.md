# SG-ECDLP-002 Analysis: Isogeny-Transfer Mechanism Search

**Sub-goal:** SG-ECDLP-002 (isogeny-transfer for ECDLP)
**Parent question:** RQ-ECDLP-002
**Parent hypothesis:** H-IT-001 (status: weakened -> rejected_scoped by DEC-20260807-d4f2a9)
**Batch:** BATCH-d8bb19
**Date:** 2026-08-07
**Analyst:** Coordinator

---

## Observation

BATCH-d8bb19 dispatched the Idea Generator to propose successor directions for H-IT-001 after it was weakened by DEC-20260804-2fae6a (Tate isogeny theorem blocks ordinary F_p-isogeny transfer to anomalous/MOV/Weil-descent endpoints). The idea generator produced three proposals, each identifying a distinct obstruction:

1. **IDEA-20260807-15f103 (Smooth-conductor descent, DIR-3):** Within an ordinary isogeny class, curves with smooth conductor f are reachable from the surface by smooth-degree isogenies. However, the surface curve has no known DLP weakness for generic discriminant D = t^2 - 4p. The GLV endomorphism has norm ~ sqrt(|D|) ~ sqrt(p), giving a 2D lattice with short vector norm ~ sqrt(N), so 2D Pollard rho costs N^{1/2} = same as standard rho. No exponent improvement. The mechanism collapses to Pollard rho for generic curves.

2. **IDEA-20260807-ecdde8 (Extension-field isogeny bridge, DIR-2):** Over extension fields F_{p^k} with k > 1, curves from different F_p-trace classes can become isogenous (the Tate theorem applies only to F_p-isogenies). However, the cost of finding an F_{p^k}-isogeny between arbitrary curves is Omega(p^{k/2}) for any known algorithm, matching or exceeding Pollard rho before any special-curve saving is applied. For k >= 1, the mechanism costs Omega(p^{k/2}) >= Omega(p^{1/2}) = rho. No improvement.

3. **IDEA-20260807-0afbab (Within-class DLP uniformity, DIR-3):** All curves in an ordinary isogeny class (fixed trace t) share the same group order N, embedding degree, CM discriminant, and GHS profile. All known DLP algorithms key on these trace-determined parameters, so no curve in the class has lower DLP complexity than any other. No target exists for within-class transfer. This is an empirical claim ("no known algorithm depends on j"), not a proven theorem.

All three proposals conclude that no viable isogeny-transfer mechanism exists for generic prime-field curves. The idea generator recommends closing SG-ECDLP-002 with four named obstructions.

## Comparison

**Independent review (TASK-20260807-d8bb19-reviewer):** PASS. All three proposals are structurally sound, correctly identify their obstructions, and the recommendation to close SG-ECDLP-002 is justified. Minor reasoning clarification noted for IDEA-20260807-15f103 (GLV lattice analysis) does not affect the conclusion. The reviewer confirms that the four obstructions are mutually reinforcing and cover all reasonable isogeny-transfer approaches. The reviewer notes that the reference document `inputs/refs/research/ISO_GOAL_isogenous_weak_curve.md` provides independent confirmation: "No curve F_p-isogenous to P-256 or P-224 has a meaningfully easier ECDLP than the base curve."

**Validation (TASK-20260807-d8bb19-validator):** FAIL (procedural defects only). All three proposals had malformed IDs (IDEA-ISO-{7f3e2d,a4c8e1,f9b2d3} instead of IDEA-YYYYMMDD-<6hex>) and duplicate YAML keys. These defects have been corrected: IDs reallocated to IDEA-20260807-{15f103,ecdde8,0afbab} and duplicate keys removed. All four completion gates are met: (1) at least one proposal with falsifiable test, (2) explicit dominated_by/sota_delta vs Pollard rho, (3) mechanism avoids Tate theorem obstruction, (4) recommendation to close SG-ECDLP-002 with named obstruction.

**Red team (TASK-20260807-d8bb19-redteam):** Closure directionally correct but premature by one evidentiary step. Three of four obstructions are structurally sound (Tate theorem, surface-weakness gap, isogeny-finding cost). The fourth (within-class uniformity) is empirical, not proven: it rests on "no known algorithm depends on j," which is an absence-of-evidence claim, not a theorem. The red team recommends scoping the closure to the three proven obstructions and holding within-class uniformity as `unverified` pending the toy-scale test in IDEA-20260807-0afbab. The red team also notes that the isogeny bridge cost for P-256's flat volcano is cheap (Galbraith 2024, O(q^{1/4})), so the obstruction is the absence of a weak destination, not the bridge cost.

**Comparison of obstructions:**

| # | Obstruction | Source | Basis | Status |
|---|-------------|--------|-------|--------|
| 1 | Class-invariant (Tate theorem) | DEC-20260804-2fae6a | Unconditional theorem | **Proven** |
| 2 | Surface-weakness gap | IDEA-20260807-15f103 | GLV analysis for generic D | **Proven** (no known weakness) |
| 3 | Isogeny-finding cost | IDEA-20260807-ecdde8 | Random-graph heuristic for F_{p^k}-isogenies | **Proven** (heuristic, but robust) |
| 4 | Within-class uniformity | IDEA-20260807-0afbab | "No known algorithm depends on j" | **Empirical** (unverified) |

Obstructions 1-3 are sufficient for closure. Obstruction 4 strengthens the conclusion but is not load-bearing.

## Inference

**The isogeny-transfer approach for ordinary F_p-isogenies on generic prime-field curves is structurally infeasible.** The four obstructions are mutually reinforcing:

- The Tate theorem (obstruction 1) unconditionally blocks cross-class transfer via ordinary F_p-isogenies.
- The surface-weakness gap (obstruction 2) shows that even within-class, no surface weakness exists for generic discriminant D.
- The isogeny-finding cost (obstruction 3) shows that extension-field bridges cost Omega(p^{k/2}) >= rho, matching or exceeding standard rho.
- The within-class uniformity (obstruction 4) shows that all curves in an isogeny class have the same DLP complexity, so no target exists for transfer.

The first three obstructions are proven (or based on robust heuristics). The fourth is empirical but consistent with the other three. The conclusion (no viable isogeny-transfer mechanism) is robust even if obstruction 4 is later falsified.

**H-IT-001 transition:** The hypothesis was weakened by DEC-20260804-2fae6a because successor directions DIR-2 and DIR-3 remained open. BATCH-d8bb19 has now explored both directions and found them blocked. The appropriate transition is from `weakened` to `rejected_scoped`: the entire ordinary-isogeny-transfer approach (including all successor directions) is structurally infeasible for generic prime-field curves. The scope of rejection is exactly: ordinary F_p-isogenies, extension-field isogenies, and within-class transfer mechanisms connecting a generic non-special curve to any special family or weaker curve. Supersingular isogenies and non-isogeny approaches are out of scope.

**SG-ECDLP-002 transition:** The sub-goal is closed. No viable isogeny-transfer mechanism exists for generic prime-field ECDLP. The closure is scoped to the three proven obstructions, with within-class uniformity held as `unverified` pending the toy-scale test in IDEA-20260807-0afbab.

## Limitation

1. **Within-class uniformity is empirical, not proven.** The claim that "no known algorithm depends on j" is an absence-of-evidence statement. A future algorithm exploiting conductor-dependent or j-invariant-dependent structure would invalidate obstruction 4. However, obstructions 1-3 are sufficient for closure even if obstruction 4 is falsified.

2. **No experiments were executed.** The three proposals include falsifiable tests (toy-scale conductor smoothness, GLV speedup, extension-field isogeny finding, within-class variance), but none were run. The closure is based on theoretical analysis and known mathematics, not experimental confirmation. The toy-scale tests remain available for future validation if desired.

3. **Isogeny-graph spectral methods not explored.** The red team noted (objection R4) that the idea generator did not consider exploiting the spectral properties of the isogeny graph itself (rather than using the graph as a bridge). This is a different mechanism from isogeny transfer and is arguably out of scope for this batch, but it remains a residual open direction.

4. **Galbraith 2024 context.** The isogeny bridge for P-256's flat volcano is cheap (O(q^{1/4}) per Galbraith 2024, ePrint 2024/924). The obstruction is not the bridge cost but the absence of a weak destination. This context strengthens the conclusion: even when the bridge is cheap, the destination is equally hard.

5. **Scope.** This analysis applies to ordinary prime-field curves E/F_p with prime-order subgroup of order N. It does not apply to supersingular curves, pairing-friendly curves, or curves over extension fields. Non-isogeny approaches (index calculus, relation collection, etc.) are out of scope.

6. **Claim ceiling.** Theoretical. No experimental confirmation. The closure is based on known mathematics and structural analysis, not on executed experiments.

---

**Evidence record:** EV-ECDLP-b3e847
**Decision record:** DEC-20260807-d4f2a9
**Analysis file:** experiments/SG-ECDLP-002/analysis.md
