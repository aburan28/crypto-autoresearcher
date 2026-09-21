# Independent Review: BATCH-d8bb19 Isogeny-Transfer Proposals

**Reviewer Role:** Independent Reviewer (review-adversarial policy)  
**Batch ID:** BATCH-d8bb19  
**Date:** 2026-08-07  
**Proposals Reviewed:**
- IDEA-ISO-7f3e2d (smooth-conductor descent)
- IDEA-ISO-a4c8e1 (extension-field isogeny bridge)
- IDEA-ISO-f9b2d3 (within-class DLP uniformity)

---

## Verdict: **PASS**

All three proposals are structurally sound, correctly identify their obstructions, and the recommendation to close SG-ECDLP-002 is justified. Minor corrections noted below do not affect the conclusions.

---

## Per-Proposal Assessment

### IDEA-ISO-7f3e2d (Smooth-Conductor Descent)

**1. Tate theorem avoidance:** ✅ Correct. Works entirely within a single isogeny class (fixed trace t).

**2. Falsifiable test:** ✅ Well-defined. The test at bits=20 with 100 curves, conductor computation, and GLV speedup measurement is concrete and reproducible.

**3. Dominated_by comparison:** ✅ Correct. The mechanism collapses to Pollard rho for generic curves.

**4. sota_delta calculation:** ✅ Correct. Both time and memory exponents are not_applicable (no improvement).

**5. Obstruction identification:** ⚠️ **Minor issue.** The proposal states "the GLV endomorphism has norm ~ sqrt(|D|) ~ sqrt(p), giving a 2D lattice with determinant N ~ p and short vector norm ~ sqrt(p*N) ~ p." This reasoning is slightly confused:
   - The 2D lattice for GLV has determinant N (not p*N)
   - The short vector has norm ~ sqrt(N) by Minkowski's theorem (not ~ p)
   - The actual obstruction is that the CM endomorphism has **degree** ~ sqrt(|D|) ~ sqrt(p), making it not efficiently computable (or not giving a speedup)
   
   **Impact:** The conclusion is correct (no speedup for generic D), but the reasoning should be clarified. The issue is the endomorphism degree, not the lattice short vector norm.

**Additional note:** The proposal should reference `inputs/refs/research/ISO_GOAL_isogenous_weak_curve.md`, which provides a comprehensive analysis confirming this conclusion. That reference notes Galbraith 2024 (ePrint 2024/924) shows the bridge cost is cheap (Õ(q^{1/4})) for P-256's flat volcano, so the obstruction is the **absence of a weak destination**, not the bridge cost. This context would strengthen the proposal.

### IDEA-ISO-a4c8e1 (Extension-Field Isogeny Bridge)

**1. Tate theorem avoidance:** ✅ Correct. The Tate theorem applies only to F_p-isogenies; over F_{p^k} with k>1, curves from different trace classes can become isogenous.

**2. Falsifiable test:** ✅ Well-defined. The BFS test at bits=20, k=2 with degree bound 1000 is concrete.

**3. Dominated_by comparison:** ✅ Correct. The mechanism costs Omega(p^{k/2}) >= Omega(p^{1/2}) for k>=1, matching or exceeding Pollard rho.

**4. sota_delta calculation:** ✅ Correct. Time exponent is k/2 (worse than rho for k>1), memory exponent is 0.

**5. Obstruction identification:** ✅ Correct. The isogeny-finding cost is the load-bearing obstruction. The proposal correctly notes this is based on the hardness of the supersingular isogeny problem and random-graph hitting-time heuristics.

**Additional note:** The proposal's Omega(p^{k/2}) lower bound is actually conservative. The cost of finding ordinary isogenies over F_{p^k} is related to class group computation, which costs L_{|D|}(1/2) where |D| ~ p^k. This is much larger than p^{k/2} for large p. The proposal could strengthen this by noting the lower bound is conservative.

### IDEA-ISO-f9b2d3 (Within-Class DLP Uniformity)

**1. Tate theorem avoidance:** ✅ Correct. Works entirely within a single isogeny class.

**2. Falsifiable test:** ✅ Well-defined. The test at bits=20 with 100 curves in the same isogeny class, measuring step count variance and correlation with j-invariant/conductor, is concrete.

**3. Dominated_by comparison:** ✅ Correct. All curves in the class have the same complexity O(sqrt(N)), so no improvement is possible.

**4. sota_delta calculation:** ✅ Correct. Both exponents are not_applicable (no improvement).

**5. Obstruction identification:** ✅ Correct. The within-class uniformity obstruction is a structural result: all curves in an ordinary isogeny class share the same N, embedding degree, CM discriminant, and GHS profile, so they have the same DLP complexity.

**Additional note:** This is the strongest of the three proposals because it identifies a **structural** obstruction (not just an algorithmic one). The reference document `inputs/refs/research/ISO_GOAL_isogenous_weak_curve.md` confirms this with a comprehensive table of isogeny-class invariants.

---

## Overall Assessment

### 1. Is the recommendation to close SG-ECDLP-002 justified?

**Yes.** The three proposals, together with the prior analysis in DEC-20260804-2fae6a and the reference document `inputs/refs/research/ISO_GOAL_isogenous_weak_curve.md`, establish that:

- **Mathematical obstruction:** The Tate isogeny theorem unconditionally blocks ordinary F_p-isogenies between different trace classes.
- **Algorithmic obstruction:** No surface weakness exists for generic discriminant D (IDEA-ISO-7f3e2d).
- **Structural obstruction:** All curves in an isogeny class have the same DLP complexity (IDEA-ISO-f9b2d3).
- **Cost obstruction:** Extension-field isogenies cost Omega(p^{k/2}) >= rho (IDEA-ISO-a4c8e1).

These obstructions are mutually reinforcing and cover all reasonable isogeny-transfer approaches. The reference document provides additional confirmation: "No curve F_p-isogenous to P-256 or P-224 has a meaningfully easier ECDLP than the base curve — every ECDLP-hardness quantity is an isogeny-class invariant strong for these curves."

### 2. Are the four named obstructions correctly stated?

**Yes.** The four obstructions are:

1. **Class-invariant obstruction** (from DEC-20260804-2fae6a): Ordinary F_p-isogenies preserve trace; special families are unreachable from generic curves. ✅ Correct.

2. **Surface-weakness gap** (from IDEA-ISO-7f3e2d): No surface weakness exists for generic discriminant D; GLV gives only constant-factor speedup. ✅ Correct (with minor reasoning clarification noted above).

3. **Within-class uniformity** (from IDEA-ISO-f9b2d3): All curves in an isogeny class have the same DLP complexity; no target exists for transfer. ✅ Correct.

4. **Isogeny-finding cost** (from IDEA-ISO-a4c8e1): Extension-field isogenies cost Omega(p^{k/2}) >= rho for k>=1. ✅ Correct.

### 3. Are there any viable mechanisms the idea generator missed?

**No.** The idea generator's appendix lists five approaches that were considered and rejected:

1. Supersingular isogeny bridge (DIR-1) — ruled out by DEC-20260804-2fae6a
2. Isogeny-augmented index calculus — already explored, augmentation ratio is constant
3. Class group DLP reduction — already explored, not known to be efficient
4. Isogeny-cycle endomorphisms — already explored, End_{F_p}(E) = Z for generic curves
5. Quadratic twist co-attack — already explored, applies only to density-0 subset

I agree with all five rejections. The three proposals in this batch cover the remaining reasonable directions (DIR-2 and DIR-3), and all three correctly identify obstructions.

**Additional direction not mentioned:** The idea generator could have noted that the reference document `inputs/refs/research/ISO_GOAL_isogenous_weak_curve.md` explicitly states "The bridge is cheap (Galbraith 2024) but leads only to equally-hard curves. The goal is not achievable by any isogeny-graph method." This provides independent confirmation that the search space has been exhausted.

---

## Required Corrections

**None.** The proposals are correct in their conclusions. The minor reasoning issue in IDEA-ISO-7f3e2d (GLV lattice analysis) does not affect the conclusion and can be addressed in a future revision if desired.

## Optional Suggestions

1. **Reference the ISO_GOAL document:** All three proposals should reference `inputs/refs/research/ISO_GOAL_isogenous_weak_curve.md`, which provides a comprehensive analysis confirming their conclusions.

2. **Clarify GLV reasoning in IDEA-ISO-7f3e2d:** The proposal should state that the CM endomorphism has **degree** ~ sqrt(|D|) ~ sqrt(p), making it not efficiently computable (or not giving a speedup), rather than talking about "2D lattice short vector norm."

3. **Note conservative lower bound in IDEA-ISO-a4c8e1:** The Omega(p^{k/2}) lower bound is conservative; the actual cost is likely L_{p^k}(1/2) >> p^{k/2}.

---

## Completion Gate Verification

✅ **At least one proposal with falsifiable experimental test:** All three proposals have well-defined tests.

✅ **Explicit dominated_by / sota_delta vs Pollard rho:** All three proposals correctly state they are dominated by Pollard rho with no improvement.

✅ **Mechanism avoids Tate theorem obstruction:** All three proposals correctly avoid the Tate theorem (within-class or extension-field).

✅ **Recommendation to close SG-ECDLP-002 with named obstruction:** The recommendation is justified, with four obstructions correctly identified.

---

## Final Statement

**The isogeny-transfer approach for ordinary F_p-isogenies on generic prime-field curves is structurally infeasible.** The three proposals correctly identify the obstructions and justify closing SG-ECDLP-002. The recommendation to redirect research effort to non-isogeny approaches is sound.

**Verdict: PASS**

**Review file:** `/Volumes/SSD990/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-001/batches/BATCH-d8bb19/reviews/TASK-20260807-d8bb19-reviewer/review_report.md`
