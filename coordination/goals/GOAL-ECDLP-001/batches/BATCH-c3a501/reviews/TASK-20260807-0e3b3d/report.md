---
task_id: TASK-20260807-0e3b3d
batch_id: BATCH-c3a501
role: reviewer
policy_requested: review-adversarial
reasoning_effort: xhigh
independent_session: true
reviewed_artifacts:
  - KN-FIND-194294
  - KN-FIND-ac28ed
  - KN-FIND-ff4a46
reviewed_at: '2026-08-07'
---

# Independent Review — KN-FIND Promotion Candidates

## Scope

Review of three KN-FIND candidates drafted by TASK-20260806-a4b58a for YAML
frontmatter conformance, mathematical correctness, and overclaiming. This
review does not transition any research state; promotion is a Coordinator
ledger action.

---

## KN-FIND-194294 — Halving-query oracle equivalence

### YAML frontmatter

**Verdict: PASS with one observation.**

All required fields present and well-typed: `id`, `type`, `title`, `tags`,
`confidence`, `evidence_level`, `source_refs`, `internal_refs`,
`proof_status`, `added`, `superseded_by`. The id uses a random 6-hex suffix
per AGENTS.md rule 14. The `repair_target` field is absent (not needed; this
is a standalone finding, not a repair of an existing record). No schema
deviation.

### Mathematical correctness

**Verdict: ERROR in stated formula; equivalence conclusion is correct.**

The record defines O_D(Q) = x([2^{-1}]Q) and then claims
"O_D([2^{-1}]Q) = x(Q) recovers the target x-coordinate in one call."
This is internally inconsistent with the definition:

- By the stated definition, O_D(P) = x([2^{-1}]P) for any input P.
- Therefore O_D([2^{-1}]Q) = x([2^{-1}][2^{-1}]Q) = x([4^{-1}]Q) ≠ x(Q).
- The correct recovery formula is O_D([2]Q) = x([2^{-1}][2]Q) = x(Q).

The high-level claim — that O_D and O_x are algebraically equivalent (each
recoverable from the other in polynomial time) — is correct:

- **O_D from O_x**: Given x(Q), compute x([2^{-1}]Q) by solving the
  duplication formula (degree-4 in x). This is O_x → O_D.
- **O_x from O_D**: Query O_D on [2]Q to obtain x(Q). This is O_D → O_x.

The equivalence and the NON-SIMULABLE (Tier 3) classification inheritance
are sound. The error is confined to the illustrative formula in the
"Specifically" clause, which has the scalar direction inverted.

**Severity**: Minor. Does not affect the classification conclusion or the
non-claims. Should be corrected before promotion to avoid a mathematical
inaccuracy in a record carrying `confidence: proved` and
`evidence_level: theorem`.

**Required correction**: Replace "O_D([2^{-1}]Q) = x(Q)" with
"O_D([2]Q) = x(Q)" in the Statement section (line 19 of the finding file).

### Overclaiming check

**Verdict: PASS.**

- Explicitly disclaims any sub-rho enabling/disabling claim. ✓
- States the x-oracle sub-rho question is OPEN. ✓
- States no experiment ran. ✓
- Provenance correctly identifies the superseded prior disposition and
  cites the review audit that corrected it. ✓

No overclaiming detected.

### Per-artifact verdict

**CONDITIONAL PASS** — promotion warranted contingent on correcting the
formula error in the Statement. The correction is a one-line fix that does
not alter the finding's substance, classification, or non-claims.

---

## KN-FIND-ac28ed — Exact-arithmetic corrections to BKK K* table

### YAML frontmatter

**Verdict: PASS.**

All required fields present and well-typed. The id uses a random 6-hex
suffix per AGENTS.md rule 14. `source_refs` correctly cites KN-FIND-c7d31e
(the BKK speedup theorem being corrected). No schema deviation.

### Mathematical correctness

**Verdict: CONCERN on the specific numerical example; general claim is
plausible.**

The record claims that `200/0.1 = 2000.0000000000005 in double precision`
causes ceil to return 2001 instead of 2000. Under standard IEEE 754
double-precision arithmetic:

- The double nearest 0.1 is 0.10000000000000000555... (slightly above 0.1).
- 200 / 0.1_double = 1999.999999999999889... (slightly below 2000).
- The nearest double to this quotient is exactly 2000.0 (the error
  ~1.11e-13 is less than half an ULP at 2000, which is ~1.14e-13).
- Therefore ceil(200.0 / 0.1) = 2000 in standard double arithmetic.

The specific numerical example as stated does not reproduce under a
straightforward reading. However:

- The general phenomenon of IEEE-float ceil artifacts causing off-by-one
  errors is well-known and real.
- The actual BKK computation may involve intermediate steps (e.g., a
  summation, a different parameterization, or a reciprocal computed
  separately) whose error accumulation differs from the simple 200/0.1
  division.
- The correction direction (2001 → 2000, 126 → 125) is plausible and
  consistent with exact rational arithmetic giving clean integer results.
- The K*(BKK)=96 confirmation is consistent with the formulas being
  correct and only the floating-point evaluation being at fault.

**Severity**: Moderate. The illustrative numerical example appears
incorrect as stated, but the underlying correction claim is plausible and
the direction is consistent with exact arithmetic. The record would
benefit from either (a) citing the exact code path that produces the
off-by-one, or (b) softening the example to "an IEEE-float ceil artifact
in the evaluation of the K* formula" without the specific decimal
expansion.

### Overclaiming check

**Verdict: PASS.**

- Explicitly disclaims any asymptotic-exponent claim. ✓
- Explicitly states the BKK speedup theorem is confirmed, not invalidated. ✓
- The "provable → model assumption" downgrade for the beta transfer is a
  careful and appropriate scoping statement. ✓
- Non-claims are explicit and proportional. ✓

No overclaiming detected.

### Per-artifact verdict

**CONDITIONAL PASS** — promotion warranted contingent on either verifying
the specific numerical example against the actual BKK computation path, or
softening the example to avoid a potentially incorrect specific decimal
expansion. The correction's direction and substance are sound.

---

## KN-FIND-ff4a46 — Wording repair for KN-FIND-9d2f56

### YAML frontmatter

**Verdict: PASS.**

All required fields present and well-typed. The id uses a random 6-hex
suffix per AGENTS.md rule 14. The `repair_target: KN-FIND-9d2f56` field is
a useful extension identifying the record this repair targets. No schema
deviation.

### Mathematical correctness

**Verdict: PASS.**

This is a wording/framing repair, not a mathematical change. Reviewing the
repair against the target record (KN-FIND-9d2f56):

1. **Theorem body unchanged**: The duality (β_1 ≥ Ω(sqrt(N)) OR yield = o(1))
   is preserved verbatim. ✓
2. **Orientation correction**: KN-FIND-9d2f56's corollary states "H-PSEUDO
   is the algebraic formulation of this requirement," which can be read as
   claiming H-PSEUDO is sufficient for sub-rho. The repaired corollary
   correctly states H-PSEUDO names the baseline whose *failure* is
   necessary for sub-rho. This is the correct logical direction:
   - H-PSEUDO holding = pseudorandom yield = baseline = no structure.
   - Sub-rho requires yield *above* baseline = H-PSEUDO failing.
   - Therefore sub-rho requires ¬H-PSEUDO (necessary, not sufficient). ✓
3. **Neutral stance preserved**: The repaired record explicitly states it
   does not claim whether sub-rho is achievable or whether any factor base
   exceeds the baseline. ✓

The repair is logically correct and eliminates an ambiguity in the
original that could support an overclaim (sufficient → necessary).

### Overclaiming check

**Verdict: PASS.**

- Explicitly disclaims any achievability or impossibility claim for sub-rho. ✓
- Explicitly disclaims any claim about H-PSEUDO holding or failing for
  specific factor bases. ✓
- The repair is strictly a framing correction; no new mathematical claim
  is introduced. ✓
- The "What changes and what does not" table is accurate and transparent. ✓

This record *reduces* overclaiming risk by correcting an ambiguity in
KN-FIND-9d2f56 that could be read as a sufficiency claim.

### Per-artifact verdict

**PASS** — no corrections required. Promotion warranted.

---

## Summary

| Artifact | YAML | Math | Overclaiming | Verdict |
|----------|------|------|--------------|---------|
| KN-FIND-194294 | PASS | ERROR (formula direction) | PASS | CONDITIONAL PASS |
| KN-FIND-ac28ed | PASS | CONCERN (numerical example) | PASS | CONDITIONAL PASS |
| KN-FIND-ff4a46 | PASS | PASS | PASS | PASS |

### Required actions before promotion

1. **KN-FIND-194294**: Correct "O_D([2^{-1}]Q) = x(Q)" →
   "O_D([2]Q) = x(Q)" in the Statement section. One-line fix; does not
   alter substance.
2. **KN-FIND-ac28ed**: Either (a) verify the "200/0.1 =
   2000.0000000000005" claim against the actual BKK code path and cite it,
   or (b) soften the example to avoid the specific decimal expansion and
   state the correction as an IEEE-float ceil artifact without the
   unreproducible numerical detail.

Neither correction affects the findings' substance, classification, or
non-claims. Both are presentational accuracy fixes appropriate for records
carrying `confidence: proved` and `evidence_level: theorem`.
