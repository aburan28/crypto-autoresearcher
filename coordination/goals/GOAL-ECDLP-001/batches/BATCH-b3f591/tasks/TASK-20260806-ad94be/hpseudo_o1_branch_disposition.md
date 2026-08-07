# o(1)-Branch Disposition for the Corrected H-PSEUDO Biconditional
**Task:** TASK-20260806-ad94be, BATCH-b3f591, GOAL-ECDLP-001
**Step:** 1 of IDEA-20260805-62ef74 dispatch
**Inputs:** TASK-20260805-004 oracle analysis, DEC-20260806-08b9ed (item 2), KN-FIND-9d2f56
**Date:** 2026-08-06

---

## Context

DEC-20260806-08b9ed (item 2) rescinds the "UNCONDITIONALLY" label on the L[1/2, sqrt(2)]
claim and treats the corrected H-PSEUDO biconditional as a **disjunction-with-o(1)-leaf
to PROVE**, not as an established iff. This document states the two candidate readings of
the o(1) leaf, names the deciding evidence, and gives a preliminary disposition for review.

The corrected biconditional (TASK-20260805-004, Q4):

> ∃F [chain-complex C_R^F is sub-rho (β_1 < sqrt(N))]  ↔  ∃F [H-PSEUDO fails for F
> (yield(F) > heuristic)]

KN-FIND-9d2f56 (Betti-Yield Duality) states:

> EITHER β_1(C_R^S) ≥ Ω(sqrt(N))  OR  ⟨r_2^S(R)⟩ = o(1)

The o(1) leaf is the "⟨r_2^S(R)⟩ = o(1)" (negligible average yield) case in this
disjunction.

---

## Two Candidate Readings

### Reading 1: o(1) leaf as sub-rho chain-complex direction

The o(1) yield case is a **genuine structural alternative** in the chain-complex
landscape. Under this reading:

- When yield is o(1) (negligible), the chain complex is provably non-sub-rho
  (β_1 ≥ sqrt(N)). This is the complementary case to sub-rho.
- The duality partitions the space cleanly: sub-rho complex ↔ above-heuristic yield,
  with o(1) yield being the complement (non-sub-rho).
- The corrected biconditional's **forward direction** (sub-rho → H-PSEUDO fails) is
  established by KN-FIND-9d2f56: sub-rho requires yield above baseline, which requires
  H-PSEUDO to fail.
- The **backward direction** (H-PSEUDO fails → sub-rho) remains open: above-heuristic
  yield is necessary but not sufficient for sub-rho β_1.
- The o(1) leaf is the chain-complex direction where the complex is non-sub-rho, and it
  makes the duality exhaustive.

### Reading 2: o(1) leaf as notation artifact

The o(1) in KN-FIND-9d2f56 is a **proof-technique artifact** rather than a genuine
structural branch. Under this reading:

- The proof sketch establishes β_1 ≥ B - r_2(R) ≥ B - B^2/N (when yield is at the
  heuristic level r_2(R) ≈ B^2/N). This is a **continuous bound** in B, not a clean
  dichotomy.
- For B > sqrt(N), the bound gives β_1 ≥ B - B^2/N ≈ B >> sqrt(N), so β_1 is always
  >> sqrt(N) at heuristic yield. The "duality" only gives a non-trivial constraint when
  B is close to sqrt(N).
- For B < sqrt(N), the bound β_1 ≥ B - B^2/N is weaker than sqrt(N), so the duality's
  claim that β_1 ≥ Ω(sqrt(N)) does not follow from the sketch alone.
- The proof sketch shows yield ≥ B^2/N (AT heuristic) when β_1 < sqrt(N), not yield
  **strictly above** heuristic. The duality's claim of "above heuristic" requires a
  strict inequality not established in the sketch.
- The "o(1) yield" case is not a separate structural branch but a regime where the bound
  β_1 ≥ B - B^2/N becomes vacuous (B^2/N approaches B).
- Under this reading, the corrected biconditional's forward direction is only a
  **one-directional implication** (sub-rho → yield ≥ heuristic), and the clean iff
  cannot be recovered without a tighter analysis.

---

## Deciding Evidence

The deciding evidence is the **proof sketch in KN-FIND-9d2f56** (lines 31-39):

```
β_1 = |S| - rank(∂_2) where ∂_2: C_2 → C_1 is the boundary map
rank(∂_2) ≤ |C_2| = r_2(R) (number of S-decompositions of R)
β_1 ≥ B - r_2(R) ≥ B - B^2/N (when yield ≤ B/N)
For sub-rho: β_1 < sqrt(N) requires B - B^2/N < sqrt(N)
  → B^2/N > B - sqrt(N) ~ B for B >> sqrt(N)
  → r_2(R) ≥ B^2/N for most R
```

**Key observations:**

1. The bound β_1 ≥ B - B^2/N is **continuous in B** and only gives β_1 ≥ Ω(sqrt(N))
   when B ≥ sqrt(N) (roughly). For B < sqrt(N), the bound is weaker than sqrt(N).

2. The proof uses rank(∂_2) ≤ r_2(R), which is an **upper bound** on the rank. The
   actual β_1 could be larger if the boundary map has less than full rank. The duality's
   claim that β_1 ≥ Ω(sqrt(N)) when yield is o(1) requires a **lower bound** on β_1,
   not an upper bound on rank.

3. The proof shows r_2(R) ≥ B^2/N (yield AT heuristic) when β_1 < sqrt(N), not yield
   **strictly above** heuristic. The gap between "at" and "above" is not bridged in the
   sketch.

4. The duality as stated (EITHER β_1 ≥ Ω(sqrt(N)) OR yield = o(1)) is a **clean
   dichotomy**, but the proof sketch does not establish this dichotomy for all B. The
   o(1) leaf is not a separate branch but a regime where the bound becomes vacuous.

**The deciding bound:** β_1 ≥ B - B^2/N. This bound is necessary but not sufficient for
the clean duality. The o(1) leaf's status depends on whether this bound can be tightened
to establish the dichotomy for all B, or whether the dichotomy is a simplification of a
more nuanced relationship.

---

## Preliminary Disposition

**Recommendation: Reading 2 (notation artifact) is the more defensible preliminary
disposition, but neither reading is established.**

**Rationale:**

- The proof sketch's bound β_1 ≥ B - B^2/N does not establish the clean dichotomy
  claimed by KN-FIND-9d2f56. The o(1) leaf is not a genuine structural branch but a
  regime where the bound becomes vacuous.
- The forward direction (sub-rho → yield ≥ heuristic) is supported by the proof sketch,
  but the strict inequality (yield > heuristic) and the backward direction (H-PSEUDO
  fails → sub-rho) are not established.
- The corrected biconditional should be treated as a **one-directional implication**
  (sub-rho → yield ≥ heuristic) with the backward direction open, unless the proof
  sketch can be tightened.

**What the review should decide:**

1. **Accept** Reading 2 and treat the o(1) leaf as a proof artifact. The corrected
   biconditional is then a one-directional implication, and the backward direction is an
   open question for the re-formalization.

2. **Narrow** Reading 2 by restricting the duality to a specific regime (e.g., B ≥ N^{1/2+ε})
   where the bound β_1 ≥ B - B^2/N does give β_1 >> sqrt(N). In this regime, the duality
   is non-trivial, but it does not hold universally.

3. **Reverse** to Reading 1 if the review can identify a tighter analysis that establishes
   the clean dichotomy for all B. This would require a lower bound on β_1 (not just an
   upper bound on rank) that gives β_1 ≥ Ω(sqrt(N)) when yield is o(1).

**This is a disposition, not a closure.** No hypothesis is proposed, no status transition
is claimed, and no proof of either reading is asserted. The review should accept, narrow,
or reverse this disposition based on whether the proof sketch can be tightened.

---

## Non-Claims

- No new hypothesis is introduced.
- No status transition is proposed.
- No proof of either reading is claimed.
- No fabricated bounds, citations, or run ids.
- No DEC or LEMMA id is minted.
- This document is heuristic-conditional: the disposition depends on the proof sketch's
  tightness, which is not established.

---

*Disposition by TASK-20260806-ad94be, BATCH-b3f591, GOAL-ECDLP-001.*
*Sources: TASK-20260805-004, DEC-20260806-08b9ed, KN-FIND-9d2f56.*
