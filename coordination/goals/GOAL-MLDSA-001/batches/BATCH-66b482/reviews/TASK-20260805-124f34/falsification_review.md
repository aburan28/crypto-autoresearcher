# Red Team Falsification Review
## GOAL-MLDSA-001 · BATCH-66b482 · Task TASK-20260805-a44587 Ideation
## Reviewer: TASK-20260805-124f34
## Snapshot commit: 76a53095a184d203348790cac144db4d72bf67b3
## Reviewed: 2026-08-05

---

## Verdict: PASS WITH CONSTRAINTS

Two constraints require Coordinator adjudication before any proposal is dispatched to
experiment design. Three advisory objections are noted but non-blocking. No proposal
is recommended for outright rejection; all five have substantive proof_search_maps
and explicit falsification criteria.

---

## OBJ-1: Pareto honesty — dominated_by null checks

### IDEA-3f7ab2 vs. IDEA-e5c308 (SelfTargetMSIS thematic overlap)

Both proposals address the accuracy of the SelfTargetMSIS hardness estimate:
- IDEA-3f7ab2 re-derives the published cost formula from first principles.
- IDEA-e5c308 validates the structural independence assumption underlying that formula.

These are distinct questions and neither strictly dominates the other. However, a
conditional dependency exists that the ideation report does not state: if IDEA-3f7ab2
finds MSIS dominates by > 50 bits at all parameter sets (its own falsification
criterion), then the independence assumption in IDEA-e5c308 becomes immaterial to
binding security. The Coordinator should sequence 3f7ab2 first and gate e5c308 on
the outcome.

**Ruling on dominated_by:** Both correctly set null. The thematic overlap is advisory,
not blocking.

---

### IDEA-9c1e04 — KN-LIT-3907 preemption (CONSTRAINT C1)

**This is a binding constraint.**

The ideation agent correctly read the KN-LIT-3907 abstract, which states:
> "we perform a concrete security analysis for the case of Dilithium to show that
> the claimed security level is still valid after addressing the gap."

The proposal's own `minimal_discriminating_test` identifies this abstract as matching
Outcome A: "the tightness loss is absorbed at current parameters, and the estimate is
confirmed." The proposal's primary falsification criterion says this outcome falsifies
the concern "at the stated scope."

Yet `dominated_by` is set to null on the grounds that "domination requires an existing
result, not a result that might be in an unread text." This argument is circular:
the agent had access to the local PDF (`downloads/140850158.pdf`) and chose not to
read it, then defended the null on the grounds of non-reading. The inventor protocol
§5 requires checking every row on the frontier, not every row of the frontier that
was convenient to check.

**The mechanistic failure:** IDEA-9c1e04 is a reading task wearing the clothes of a
research proposal. Its minimal discriminating test is "read the relevant section of
KN-LIT-3907 and extract a number." That number is likely already in the paper in a
form that either immediately falsifies the proposal (loss < 5 bits) or reduces it to
a documentation task (write down the formula and its magnitude). In neither case is
a full hypothesis-specification-and-experiment workflow warranted.

**Cheapest discriminating check:** Open `downloads/140850158.pdf`, locate the concrete
security analysis section, extract f(q_s, q_H). If the overhead is < 5 bits at
q_s = 2^64, q_H = 2^64, the proposal's own falsification criterion is satisfied. If
the overhead is > 10 bits, the proposal becomes a low-cost documentation task.

**Coordinator action required (C1):** Dispatch a reading task for KN-LIT-3907
before any hypothesis specification for IDEA-9c1e04.

---

### IDEA-e5c308 — KN-LIT-3907 EasyCrypt scope (CONSTRAINT C2)

IDEA-e5c308 proposes to validate the independence assumption:
> cost_SelfTargetMSIS ≈ cost_MSIS + log₂|C|

KN-LIT-3907 provides a "fully mechanized ROM proof for the CMA-security of Dilithium
in the EasyCrypt proof assistant." A machine-checked security proof encodes the
SelfTargetMSIS reduction as a formal step. If the EasyCrypt mechanization formally
verifies the decomposition as a proof obligation, the "independence assumption" is
already a formally verified theorem in the random-oracle model.

In that case, IDEA-e5c308's experimental validation would be circular confirmation
of a formally proven fact. The experiment retains independent value only if reframed
as: "Does weight-τ sparsity in the challenge set create a BKZ shortcut that the formal
model ignores?" — i.e., a question about practical vs. idealized complexity, not about
whether the decomposition is formally valid.

**Cheapest discriminating check:** Consult the KN-LIT-3907 EasyCrypt proof structure
to determine whether the decomposition cost_SelfTargetMSIS = cost_MSIS + log₂|C| appears
as an explicit, verified proof obligation or is handled implicitly by the reduction.

**Coordinator action required (C2):** Confirm EasyCrypt proof scope before dispatching
IDEA-e5c308. If scope confirms the decomposition formally, revise the hypothesis to
the "BKZ shortcut under challenge structure" framing before experiment design.

---

## OBJ-2: Closure standard — Lane B framing (Advisory)

### IDEA-a8d531 and IDEA-2b6f17

Both proposals correctly identify that the Shin DFA (a8d531) and the Jendral glitch
(2b6f17) lie outside all existing formal proofs. The proposals correctly disclaim that
identifying this boundary does not determine whether ML-DSA is insecure under these
fault classes.

**The framing issue:** "Proof coverage gap" implies the existing proofs are incomplete.
They are not incomplete under their stated models — they are correct proofs over adversary
models that, by construction, exclude physical fault adversaries. The Gupta result
(KN-LIT-8ce0b5) is the exception: it extends a formal bound to a *specific* fault class.
The correct framing is:

> "The Gupta methodology (KN-LIT-8ce0b5) establishes the template for formal fault-class
> bounds. An analogous result for challenge-sampling faults (IDEA-a8d531) and nonce-erasure
> faults (IDEA-2b6f17) does not yet exist. This is a missing result, not a gap in an
> existing proof."

This distinction matters for hypothesis specification: a hypothesis claiming "the proof
has a gap" invites a reviewer to check the proof; a hypothesis claiming "no formal
fault bound exists for this class" invites a Gupta-style extension.

**Cheapest discriminating check for IDEA-a8d531:** Determine from KN-LIT-340675 whether
the Shin DFA requires the faulted challenge c to lie in the valid set C for key recovery.
If c ∉ C: the verifier rejects the signature deterministically; the attack requires c ∈ C
and is structurally a challenge-substitution rather than a challenge-corruption. A
challenge-substitution adversary can potentially be modeled in an extended formal framework
(e.g., a signing oracle that accepts attacker-chosen challenges). This changes whether the
"gap" is closable by proof extension or requires a different security model.

**Cheapest discriminating check for IDEA-2b6f17:** Check KN-LIT-3907's EasyCrypt proof for
whether it explicitly models the signing seed ξ as externally provided or internally generated.
If ξ is assumed internally generated with the scheme's key generation, then the Jendral fault
(which effectively corrupts ξ or the derived ρ') operates at a layer below the proof's trust
boundary. This is a sharper boundary statement than "hedged mode is uncovered": it is "the
proof assumes ξ-honest-generation; the fault corrupts this assumption."

---

## OBJ-3: sota_delta honesty — IDEA-3f7ab2 (Advisory)

The `sota_delta` field for IDEA-3f7ab2 lists:
> "Published SelfTargetMSIS estimates from KN-LIT-056 (Dilithium TCHES 2018):
> ML-DSA-44 ≈ 128-bit, ML-DSA-65 ≈ 192-bit, ML-DSA-87 ≈ 256-bit AES-equivalent."

**Sub-issue 1 (precision):** The numbers 128/192/256-bit are the *target security
levels*, not necessarily the computed SelfTargetMSIS estimates as they appear in the
published table. The actual computed estimates may exceed these targets (providing
margin) or, in a worst case, fall below them. Using target levels as proxy for
computed estimates introduces a possible confusion: the re-derivation is checking
whether the formula reproduces the *table*, not whether the *table* meets the
*target*. If the computed SelfTargetMSIS estimate at ML-DSA-65 is, say, 200 bits
rather than 192 bits, the re-derivation must match 200, not 192.

**Sub-issue 2 (baseline provenance):** KN-LIT-3907's corrected concrete analysis is
the current best-published estimate, not KN-LIT-056's original (2018). The sota_delta
should list KN-LIT-3907 as the primary baseline and KN-LIT-056 as the historical
estimate. Even if the numbers are identical, the provenance chain matters for
reproducibility.

**Cheapest discriminating check:** Before running the re-derivation, look up the
exact SelfTargetMSIS cost entry in KN-LIT-056 Table 2 (or equivalent) and note
whether it equals the target security level or exceeds it. If it exceeds the target,
use that number as the re-derivation baseline.

---

## OBJ-4: proof_search_map completeness audit

All five proposals pass. Each has four non-trivial, non-NA audits:

| Proposal | Baseline Repro | Obs Collision | Quantifier Order | Method Ceiling |
|----------|---------------|---------------|-----------------|----------------|
| 3f7ab2 | PASS | PASS | PASS | PASS |
| 9c1e04 | PASS | PASS | PASS | PASS |
| a8d531 | PASS | PASS | PASS | PASS |
| 2b6f17 | PASS | PASS | PASS | PASS |
| e5c308 | PASS | PASS | PASS | PASS |

No audit field says "N/A" without justification. IDEA-e5c308's method_ceiling
explicitly notes "toy-scale only, no crypto-scale extrapolation," which is a
correct and substantive ceiling statement. No blocking issues found in
proof_search_map completeness.

---

## OBJ-5: Actionability ranking (requires_fips204_body: false claims)

All five proposals correctly claim `requires_fips204_body: false` for ideation
purposes. The ranking by genuine testability using only the academic literature:

### Rank 1: IDEA-9c1e04 (CMA-NMA proof gap impact)
**Test is a reading task.** KN-LIT-3907 PDF available locally. Zero implementation
required. The abstract already partially answers the question; the full text
resolves it completely. **However:** see Constraint C1 — this proposal should be
dispatched as a reading task, not a hypothesis specification. It may self-falsify
upon reading.

### Rank 2: IDEA-a8d531 (Shin DFA placement)
**Three-step corpus placement test** using indexed abstracts. KN-LIT-3907,
KN-LIT-8ce0b5, and KN-LIT-340675 are all available. One additional logical step
(c ∈ C check) clarifies the adversary model boundary. Fully actionable with no
implementation. Recommended for immediate dispatch pending the advisory in OBJ-2.

### Rank 3: IDEA-2b6f17 (Jendral nonce-erasure placement)
**Same structure as a8d531** but requires reading the KN-LIT-3907 proof more
carefully for the deterministic-vs-hedged mode handling. Slightly more work
than a8d531. Actionable with no implementation. Recommended for dispatch with
OBJ-2 advisory noted.

### Rank 4: IDEA-3f7ab2 (SelfTargetMSIS re-derivation)
**Manual arithmetic from KN-LIT-056 Table 2.** Requires reading the Dilithium
paper for exact τ, k, l, q, n values and applying the BKZ cost formula. The
parameter values are flagged as "from memory (unverified)," adding a look-up
step. Low compute, no code. Should be sequenced before IDEA-e5c308.

### Rank 5: IDEA-e5c308 (Toy BKZ comparison)
**Requires BKZ implementation.** Medium implementation work. Not testable from
academic literature alone. Recommend: gate on IDEA-3f7ab2 result; reframe
hypothesis per Constraint C2 before experiment design; implement only after
gates are cleared.

---

## Summary of constraints and actions

| ID | Severity | Proposal | Action required |
|----|----------|----------|----------------|
| C1 | CONSTRAINT | IDEA-9c1e04 | Read KN-LIT-3907 §concrete-security before dispatching |
| C2 | CONSTRAINT | IDEA-e5c308 | Verify EasyCrypt proof scope; reframe if decomposition is proven |
| A1 | ADVISORY | IDEA-3f7ab2 vs e5c308 | Sequence 3f7ab2 first; gate e5c308 on outcome |
| A2 | ADVISORY | IDEA-a8d531, IDEA-2b6f17 | Reframe "gap" as "missing fault-class bound" in hypothesis specs |
| A3 | ADVISORY | IDEA-3f7ab2 | Update sota_delta to list KN-LIT-3907 as current best estimate |

None of C1 or C2 blocks all five proposals simultaneously. IDEA-a8d531 and
IDEA-2b6f17 are the cleanest proposals for immediate dispatch after the OBJ-2
reframing advisory is acknowledged. IDEA-3f7ab2 is ready for dispatch. IDEA-9c1e04
requires the KN-LIT-3907 reading task. IDEA-e5c308 requires the EasyCrypt scope
check and the 3f7ab2 sequencing gate.

---

*Report produced by: TASK-20260805-124f34 (Red Team, independent session)*
*Model: amazon-bedrock/us.anthropic.claude-sonnet-4-6*
*Policy: review-adversarial*
*Artifact paths: coordination/goals/GOAL-MLDSA-001/batches/BATCH-66b482/reviews/TASK-20260805-124f34/red_team_report.yaml, falsification_review.md*
