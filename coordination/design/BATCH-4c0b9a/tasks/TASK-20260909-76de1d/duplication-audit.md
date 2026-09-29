# Duplication audit: public embedding-degree transfer-gate calibration ladder

**Task:** `TASK-20260909-76de1d`  
**Idea under design:** `IDEA-20260805-cc4c2c`  
**Draft records:** `H-ECDLP-d9b1f3`, `EXP-ECDLP-a1a142`  
**Result:** **Inconclusive — no novelty or non-duplication claim**

## Candidate mechanism

The candidate is a bounded instrument contract, not a proposed ECDLP solver:

1. recompute the least positive public embedding degree `k` from `(p, r)`;
2. retain a strict boundary between that arithmetic classification and any
   claim that a named transfer applies;
3. preserve `forced`, `measured`, and `unavailable` costs as distinct typed
   values; and
4. require a known-false asserted-`k` control and toy/cryptographic scale
   separation before any later implementation is reviewed.

## Audit method and result

This design task was not authorized to search or retrieve literature, inspect
the full proposal/experiment inventory, or inspect a source corpus. No primary
source was read. No repository-wide duplicate query or knowledge-base result is
available in this artifact.

Terms such as MOV, Smart, anomalous, supersingular, generic, intermediate
embedding degree, L-function, and transfer attack are **recalled** pointers.
They do not establish that this instrument is new, known, adapted, equivalent
to an existing proposal, or distinct from a prior instrument. The audit does
not cite them as support.

Accordingly:

```yaml
novelty_status: unverified
dominated_by: unverified
sota_delta: unverified
duplicate_status: inconclusive
```

## Minimum discriminating comparison for a later audit

A later, separately authorized duplication audit must compare this contract
against source-bound candidate records and retrieved primary literature using
the following row fields:

| Field | Required comparison question |
| --- | --- |
| Objective | Does the other work build a public-input **gate instrument**, or assert/measure a transfer attack? |
| Verified predicate | Does it require least-positive `k` recomputation from pinned `(p,r)`? |
| Applicability boundary | Does it explicitly prevent family labels or low `k` from becoming transfer claims? |
| Cost typing | Does it preserve forced, measured, and unavailable values without coercion? |
| Controls | Does it include a known-false/proves-too-much asserted-`k` control and a scale-mixing refusal? |
| Scale | Are toy and cryptographic inputs separated, with no security extrapolation? |
| Custody | Are source provenance, public inputs, artifact hashes, and future execution requirements bound? |
| Evidence status | Is the comparison backed by read source bytes and `retrieved` citations? |

The comparison must set `dominated_by` only after it has actual time, memory,
and data/query vectors with compatible labels and scales. Until then a null or
negative dominance conclusion would be fabricated.

## Expected overlap and decisive distinction

It is plausible that existing work already uses embedding degrees, transfer
preconditions, or special curve classes. That plausible overlap is not
evidence; no source was read here.

The decisive distinction, if later source comparison supports it, would be
operational rather than mathematical: this proposal is limited to a
fail-closed calibration and custody gate and contains no reduction theorem,
solver, attack estimate, or deployment-security conclusion. If another
source-bound record already supplies the same finite predicate, typed cost
model, controls, and custody boundary for the same purpose, this candidate is
duplicative and should be superseded or linked rather than independently
promoted.

## Preconditions before a duplicate result may be recorded

1. Retrieve primary sources or source-bound internal records and retain their
   hashes, locators, and provenance.
2. Compare the exact contract rows above, including control semantics rather
   than title or keywords alone.
3. Keep mathematical facts, implementation features, and custody features in
   separate columns.
4. Record every unmatched field and every unresolved proposition as
   `inconclusive`.
5. Do not claim novelty, adaptation, known status, Pareto superiority, or lack
   of duplication from recalled background or a lexical hit.
