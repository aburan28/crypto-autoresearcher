# Adversarial Review — C_t Minimality Lemma (TASK-20260805-008)
**Reviewer:** independent review session (validator role, Coordinator-authorized)
**Review date:** 2026-08-05
**Reviewed record:** TASK-20260805-008 `ct_minimality_lemma.md`
**Requested policy:** review-adversarial (executed in session; see provenance)

---

## Verdict: ACCEPT WITH QUALIFICATIONS

The theorem's clauses (a)–(e) and Lemmas 1–5 are logically sound under the
stated definitions. The corrections C1–C7 are correct and genuinely improve
on the BATCH-121 framing. Three qualifications (below) must be recorded with
any promotion.

---

## 1. Clause-by-clause attack

### Lemma 1 (identification, one query). Sound.
Direct from definitions; no group operations required. No issue.

### Lemma 2 (non-simulability, Tier 3). Sound with a caveat on the witness.
The same-curve two-secret witness is the strongest part of the formalization:
two instances (E, G, [k1]G) and (E, G, [k2]G) with x([k1]G) < t <= x([k2]G) are
GGM-indistinguishable (labels are uniform random injections; group oracle
answers depend only on the abstract group law). C_t answers differently on the
queried handle. This is a genuine witness.

**Objection Q1 (adaptive query order).** The proof treats the transcript as
if the adversary queried a single handle. In the actual GGM, the adversary
may query many handles [j]G before the "target" handle. Shoup-style
indistinguishability holds by the random-label argument regardless of query
order: labels are independent uniform, so transcripts are identically
distributed. The witness remains valid. Qualification: the lemma states this
for the *single-query transcript family*; the multi-query case is covered by
the same argument but is not written out. Minor, record with promotion.

**Objection Q2 (randomized simulator).** A randomized simulator S that answers
randomly could be "correct on both" with probability 1/2 per query — the lemma
claims no *deterministic* or *randomized* simulator can be correct on both.
Strictly, the claim "no randomized simulator can be correct on both" needs
the distributional statement: S's answers are independent of the instance,
so its success probability is 1/2 per query, i.e. it fails the
identically-distributed requirement of Definition 4. The lemma's parenthetical
"(or randomized)" is asserted, not proven; the definition of simulability as
"answers distributed identically to O's" resolves it, but the lemma should
cite Definition 4 explicitly. Qualification: wording only; the definition
carries the argument.

### Lemma 3 (one bit necessary). Sound.
F_t and complement non-empty → both answer values occur → constant oracle
fails; 1 bit is minimal. No issue.

### Lemma 4 (uniqueness in order-based class). Sound.
The forcing argument {x : O(P)=1} ∩ X(E) = [0,t) ∩ X(E) correctly derives
τ ≡ t or complement. Correct.

### Lemma 5 (antichain; no strictly weaker identifier). Sound and the most
valuable correction. The four-function observation (predecessors of a
non-constant 1-bit oracle are {0,1,O,¬O}) is correct and kills the vacuous
"minimality" reading. The antichain argument via points A,B,C with
x < s, s <= x < t, x >= t is a valid incomparability witness. No issue.

### Theorem 1 / Corollary. Sound as a conjunction.
The scope honesty in Section 4.4 (identification task, not IC complexity) is
correct and required. Section 4.2's random-hash counterexample table is
correct: g = h∘x identifies F_t with probability 2^{-N}, so "minimality
without the order-based qualifier" is false as claimed.

---

## 2. Corrections C1–C7: assessment

| Correction | Verdict | Note |
|---|---|---|
| C1 (minimality vacuous) | correct | Key correction; the four-function predecessor observation settles it |
| C2 (antichain, not chain) | correct | "Weakest" has no chain meaning; well-argued |
| C3 (fixed-C_t binary search false) | correct | The family {C_s} is required; BATCH-121's "O(log p) adaptive calls" was wrong |
| C4 (same-curve witness; degeneracy condition) | correct | Strictly stronger than the two-curve witness; exact condition F_t ∉ {∅, E(F_p)} |
| C5 (identification vs IC conflation) | correct | Necessary scope repair |
| C6 (any 1-bit threshold) | correct | Only the matching threshold identifies that F_t |
| C7 (y-dependent oracles) | correct | The sign oracle is a genuine counterexample to "all non-simulable are f(x)" |

No correction overreaches; each narrows the claim rather than inflating it.

---

## 3. Third-party check: does the lemma contradict anything in the ledger?

Cross-checked against:
- H-PSEUDO-83817b: no interaction — lemma is unconditional (Section 3 remark
  confirmed; H-PSEUDO appears only in "explicitly unused").
- KN-FIND-9d2f56 (Betti-Yield): no conflict; different level (chain complex
  vs oracle task).
- BATCH-060 three-tier taxonomy: C_t classified Tier 3 consistently with the
  elliptic-net oracle precedent.

No contradiction found.

---

## 4. Qualifications (must travel with any promotion)

1. **Q1**: Lemma 2's multi-query transcript case is asserted but not written
   out; the argument is the same but should be explicit before promotion to
   KN-FIND.
2. **Q2**: "no randomized simulator" in Lemma 2 is carried by Definition 4's
   distributional requirement, not proven in-text; the wording should cite
   Definition 4 there.
3. **Q3**: The theorem does not claim anything about adaptive multi-query
   information orders (Section 4.5) — correct, but the corollary's phrase
   "minimal non-simulable order-based oracle" could be misread as a global
   claim by downstream readers; a sentence tying the corollary back to the
   one-bit-per-point usage would harden it.

---

## 5. Verdict

**ACCEPT WITH QUALIFICATIONS.** The lemma is sound, its corrections are
right, and its scope discipline is exemplary. Qualifications Q1–Q3 are
presentation-level; none threatens the argument. Recommended: promote to
KN-FIND after Q1/Q2 wording is addressed in the promoting record.