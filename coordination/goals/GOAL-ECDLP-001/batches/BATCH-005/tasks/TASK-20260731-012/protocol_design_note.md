# Protocol design note — TASK-20260731-012 (activation pin)

## Purpose

Pin the concrete independent verifier artifact and freeze precommit activation
fields for GOAL-ECDLP-001 under certificate contract `1.0.0-review`, discharging
the BATCH-004 / EV-ECDLP-012 / DEC-20260725-025 **activation residual**
`PRECOMMIT_VERIFIER_HASH_MISSING`. This is a review-only activation package, not
an experiment license.

## Inference

- requested_policy: research-sol-max
- resolved_model_id: cursor-grok-4.5-high-fast
- fallback_used: true
- authorization_ref: AMEND-PATH-001-001
- Equivalence to research-sol-max is not claimed.

## What changed vs BATCH-004 residual

BATCH-004 (TASK-20260725-697, snapshot `9b17754e23a1`) already froze:

- `fixture_sha256 = 4c82f5e43efce185a2ecbf2cbcc24b6da7a1bddadd1176007427be350494c4a8`
- `schedule_sha256 = be41eb8d016f049d31a3f2ce5bdeda94fb60548b9108311bddca5ede9f9f2279`
- nine planted controls, full-cost honesty, group-op vocabulary in schedule

Those pins are **reused unchanged** (no defect found).

What BATCH-004 left as activation blockers:

1. `independent_verifier_artifact_sha256: null` → hard-fail
   `PRECOMMIT_VERIFIER_HASH_MISSING`
2. Snapshot / `verified_before_execution` unset for execution sealing

This task supplies:

1. Concrete `independent_verifier.py` and pins
   **`independent_verifier_artifact_sha256 = 3b7d932b7cfb41dbdbfa5fd91dc802765a8000a440e71603ab75152393e668ef`**
   (sha256 of that file’s exact bytes).
2. Frozen precommit fields in `activation_package.yaml`, including verifier
   identity, the non-null hash, and documented BATCH-004 design-snapshot
   reference paths (`9b17754e23a1` / parent / receipt), with
   **`verified_before_execution: false`**.

`PRECOMMIT_VERIFIER_HASH_MISSING` is **discharged** by the non-null hash pin.
The sealed BATCH-004 schedule JSON remains immutable and may still echo
`null` internally; the authoritative activation pin is this package.

## Gate interaction after this pin

| Gate | Status after this package |
| --- | --- |
| `PRECOMMIT_VERIFIER_HASH_MISSING` | Discharged (non-null, hash-bound) |
| `PRECOMMIT_SNAPSHOT_UNVERIFIED` | Still blocking (`verified_before_execution: false`; design snapshot ≠ execution seal) |
| `PRECOMMIT_SCHEDULE_UNSEALED` | Still blocking (sealable schedule not yet sealed for execution) |
| Separate Coordinator ledger authorization | Still required before any implementation/run |

## Claim boundary (toy / review-only)

Maximum claim: toy-tier conservation methodology and activation-pin
completeness for a later sealed public/toy campaign. Not an attack
improvement, ECDLP lower bound, breakthrough, solution, or crypto-scale
result. No fabricated runs or empirical conservation measurements.

## What is still NOT authorized

- Implementation or Executor admission
- Relation collection, linear algebra, descent, or any solve campaign
- Live keys, private targets, or cryptanalytic attack work
- Setting `verified_before_execution: true`
- Treating this pin, or a future review PASS on it, as auto-execution license

Separate Coordinator ledger authorization remains mandatory before any
executable campaign.
