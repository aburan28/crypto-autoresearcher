# Protocol design note — TASK-20260725-685

## Purpose
Frozen **review-only** toy validation protocol under certificate contract
`1.0.0-review`, discharging DEC-20260722-005 / GOAL-ECDLP-001 next_action pins:
public fixture, sealed empty-or-pilot schedule template, independent verifier
artifact hash, and group-operation type vocabulary.

## Inference
- requested_policy: research-sol-max
- resolved_model_id: cursor-grok-4.5-high-fast
- fallback_used: true
- authorization_ref: AMEND-PATH-001-001

## Authorization (non-negotiable)
No implementation or experiment is authorized by this design. Executable campaigns
require independent review PASS on this protocol package. Schema PASS on
EV-ECDLP-004 is not empirical validation of any fixture or probability assumption.

## Design choices
1. **Empty-or-pilot schedule** — sealable finite template with all root fields
   named; concrete `schedule_sha256` deferred to a later sealing step after review.
2. **Verifier hash** — field obligation pinned; concrete hash filled when the
   verifier artifact is frozen (blocking residual from TASK-20260722-014).
3. **Group-op vocabulary** — explicit enum inside the schedule object.
4. **Full-cost vector** — `no_scalarization: true`; additive vs non-additive
   split preserved; ownership rules invalidate conservation on double-count.
5. **Nine planted controls** — carried forward from the certificate contract.

## Open obligations (not defects of this design card)
- Concrete `fixture_sha256` bytes for FIXTURE-ECDLP-TOY-RANKFAIL-001
- Concrete `independent_verifier_artifact_sha256`
- Concrete sealed schedule hash after pilot contents are chosen

These are **post-PASS execution-prep** items, not licenses to run now.

## Claim boundary
Toy-tier conservation methodology only. Not an attack improvement, ECDLP lower
bound, breakthrough, or crypto-scale result. Supersedes failed_infrastructure
card TASK-20260725-611 (non-mathematical).
