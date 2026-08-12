# Protocol design note — TASK-20260725-697

## Purpose

Revised **review-only** toy validation protocol under certificate contract
`1.0.0-review`, repairing TASK-20260725-685 after RT-20260725-687 / DEC-20260725-022
**REVISE**. This card freezes the DEC-20260722-005 / TASK-20260722-014 pins for a
concrete public fixture and a sealable empty-or-pilot schedule instance.

## Inference

- requested_policy: research-sol-max
- resolved_model_id: cursor-grok-4.5-high-fast
- fallback_used: true
- authorization_ref: AMEND-PATH-001-001
- Equivalence to research-sol-max is not claimed.

## Authorization (non-negotiable)

No implementation or experiment is authorized by this design. Independent review
PASS on this revised package is **not** auto-execution license: a separate
Coordinator ledger authorization is required before any implementation task may
be admitted. Schema PASS on EV-ECDLP-004 is not empirical validation of any
fixture or probability assumption.

## What was frozen (pin discharge)

1. **Concrete public fixture** — `FIXTURE-ECDLP-TOY-RANKFAIL-001` at
   `public_fixture.json` with complete curve/group parameters
   (short-Weierstrass over \(\mathbb{F}_{19}\), \(a=0\), \(b=2\)), subgroup order
   \(13\), generator \(G=(4,3)\), factor-base points \(\{G,2G,3G\}\), and
   **`fixture_sha256 = 4c82f5e43efce185a2ecbf2cbcc24b6da7a1bddadd1176007427be350494c4a8`**.
   Prior deferral of fixture bytes was a design defect relative to DEC-20260722-005;
   that defect is closed here.

2. **Sealable empty-or-pilot schedule instance** — JCS-canonical document
   `empty_or_pilot_schedule.json` materializing all
   `preexecution_schedule.required_root_fields` (including empty `attempts: []`,
   `probability_plan`, `resource_schema`, `initial_matrix`, and `precommit`), with
   **`schedule_sha256 = be41eb8d016f049d31a3f2ce5bdeda94fb60548b9108311bddca5ede9f9f2279`**.
   Empty-or-pilot allows empty attempt contents; it does not allow omitting a
   hashable schedule document. Prior checklist-only `schedule_sha256: null` was a
   design defect; that defect is closed here.

3. **Group-operation vocabulary inside the schedule** — the frozen enum
   (`add`, `dbl`, `mixed_add`, `scalar_mul_fixed_window`, `endomorphism_apply`,
   `equality_test`, `encode_decode`) is embedded under
   `resource_schema.group_operations_by_declared_type` in the sealed schedule
   object (not only in accompanying protocol prose).

4. **Verifier hash** — `independent_verifier_artifact_sha256` remains null
   (obligation-only residual allowed by TASK-20260722-014 / RT687-O4) **only**
   because activation hard-fails with first no-go
   `PRECOMMIT_VERIFIER_HASH_MISSING` when the hash is absent at seal time.

5. **Full-cost vector** — `no_scalarization: true`; additive vs non-additive
   split preserved; ownership rules invalidate conservation on double-count;
   `R_gain=0` leaves resource-per-rank undefined.

6. **Nine planted controls** — carried forward unchanged from contract
   `1.0.0-review` with expected terminal codes preserved.

## Residual that still blocks activation (not protocol-fixture pins)

- Concrete `independent_verifier_artifact_sha256` must be pinned before any
  executable campaign; until then, activation fails closed.
- Coordinator snapshot precommit fields (`snapshot_commit_sha`,
  `verified_before_execution`, etc.) remain null until a later authorized
  sealing step after review PASS and separate ledger authorization.

These residuals **block activation**, not the fixture/schedule design pins
discharged above. They are not reclassified as “non-defects” of a PASS-complete
protocol card for the DEC-20260722-005 fixture/schedule obligations.

## Claim boundary

Toy-tier conservation methodology only. Not an attack improvement, ECDLP lower
bound, breakthrough, or crypto-scale result. Supersedes failed_infrastructure
card TASK-20260725-611 (non-mathematical). Revises TASK-20260725-685.
