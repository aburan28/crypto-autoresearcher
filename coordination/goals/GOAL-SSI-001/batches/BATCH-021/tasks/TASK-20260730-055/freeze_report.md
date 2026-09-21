# BATCH-021 FC0 extension-package interface freeze

**Task:** `TASK-20260730-055`  
**Decision / evidence:** `DEC-20260730-018` / `EV-SSI-020`  
**Lane:** IDEA-20260729-001 / CSIDH-COLLIMATION-FC0-R2  
**Compute:** zero curve / isogeny / quantum-circuit  
**Package:** `FC0-EXT-PKG-SSI-001` `v1.0.0-freeze` — `freeze_status: frozen`

## Verdict

In-repo FC0 extension-package interfaces for `Verify(x,k')` and W/R/B/M_tail
lifetime birth/death/cleanup signatures are **frozen** under this task write
scope. This is NEXT-1 from BATCH-020 (`successor_host_pin.yaml`): a
Coordinator-authorized interface freeze so a later executor spike can
implement against a fixed host package.

Disposition retained: **`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`**.

Interfaces frozen ≠ QUERY_MEMORY reconciled. Not `PIN_COMPLETE`. Not
implementation. Not CollimationSieve APIs.

## What was frozen

| Surface | Artifact | Status |
|---|---|---|
| Package identity | `fc0_extension_package.yaml` | `freeze_status=frozen` |
| `Verify(x, k_prime) -> bool` | `verify_interface.yaml` | signature + F_verify channel; no body |
| Lifetime hooks (12) | `lifetime_hooks_interface.yaml` | birth/last-use/cleanup/death for all required classes; none deferred |

Required hooks defined (all twelve): `W_label`, `R_label`, `W_sieve`,
`R_sieve`, `B_input`, `B_attempt`, `B_sieve`, `accepted_transcript`,
`B_post`, `B_recovery`, `M_tail`, `B_candidate` — plus stage live sets and
`F_*` checklist channels from `recovery_spec.md` / `lifetime_trace.yaml`.

## Anchors (read-only)

- `coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/recovery_spec.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-017/tasks/TASK-20260730-039/lifetime_trace.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-020/tasks/TASK-20260730-051/successor_host_pin.yaml`
- `ledger/decisions/DEC-20260730-018.yaml`
- `ledger/evidence/EV-SSI-020.yaml`

## Retained priors

| Prior | Status after this freeze |
|---|---|
| BATCH-020 `no_admissible_pin` | **retained** (external-host screen unchanged) |
| CollimationSieve@6f9188e4 | **host_gap_certified**; APIs not invented |
| ttm-v2 panel | retained as finite ideal-choice; **not** equated with BATCH-014 |
| Closed IDEA-20260725-001/002/003 | not reopened |

## QM blockers

| Blocker | Status after this freeze |
|---|---|
| QM-STOPPING | **open** (no τ / joint finiteness invented; BATCH-018 FAIL retained) |
| QM-MEMORY-MAP | **interfaces_frozen_implementation_pending** — not clearance |
| QM-ERROR | **interfaces_frozen_implementation_pending** — not clearance |

QUERY_MEMORY remains unreconciled. Freezing signatures advances the
construction path for MEMORY-MAP / ERROR but does not instantiate lifetimes,
Verify, or `F_*` probability bounds.

## Explicit non-claims

- Verify / lifetimes **not implemented**
- Not a CollimationSieve@6f9188e4 API surface
- Not QUERY_MEMORY / QM-STOPPING / QM-MEMORY-MAP / QM-ERROR clearance
- Not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`
- No numeric widths, no τ, no security / breakthrough / completion claim
- BATCH-014 not equated

## What would be required next

1. Snapshot-archive this freeze (`archived_by: TASK-20260730-056`).
2. Bounded executor spike implementing against `FC0-EXT-PKG-SSI-001`
   interfaces (still zero numeric-security claim; still no τ invention).
3. Separate QM-STOPPING lane: source-compatible Verify-relative τ and joint
   Q/S/P/C finiteness.

## Inventor-protocol honest accounting (§5)

- **Objects considered:** in-repo FC0 extension package as tracked host
  interface; Verify acceptance predicate; W/R/B/M_tail lifetime object
  schedule from recovery_spec (not CollimationSieve PhaseVector analogues).
- **dominated_by:** `n/a (no result claimed)` — interface freeze only; no
  asymptotic or security improvement claimed.
- **sota_delta:** `0` (no complexity claim; host-interface freeze only).
- **Enumerated closures:** none. This session does not close a mathematical
  lane; it freezes construction interfaces after BATCH-020 certified no
  admissible external pin.
- **Open for next session:** implement Verify + lifetime hooks against this
  frozen package; keep QM-STOPPING open until source-compatible τ exists.

## Inference

- Requested policy: `research-sol-max`
- Resolved model: Cursor Grok
- `fallback_used: true` (authorized by
  `inference-amendment-TASK-20260730-055.yaml`)
- `non_extrapolation: true`
- `maximum_runs: 1`; runs attempted: 1 (this freeze)
- Git commit: not created (worker prohibition)
