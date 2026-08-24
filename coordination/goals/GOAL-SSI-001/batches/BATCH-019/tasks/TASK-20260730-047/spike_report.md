# BATCH-019 FC0 lifetime / Verify spike report

Task `TASK-20260730-047` · pin `CollimationSieve@6f9188e4eb5611bcfdf29a3e1ec3cd69a29a50e9` ·
decision `DEC-20260730-016` / evidence `EV-SSI-018` · zero curve / isogeny /
quantum-circuit compute · `maximum_runs: 1`.

## Objective

Attempt the narrowest feasible in-repo hook or stub that would advance
`QM-MEMORY-MAP` / `QM-ERROR` against the pinned host, or emit an explicit
host-gap certificate if the host cannot host Verify / FC0 lifetimes without
invention.

## What was inspected

| Item | Result |
| --- | --- |
| Pin record | `BATCH-012/.../artifact_pin.yaml` → commit `6f9188e4…`, blob SHAs match `git hash-object` on fetched sources |
| Tree at pin | `src/{Main,Phase,Random}.hs` only; empty `test/Spec.hs` |
| `src/Main.hs` | `sieve` / `sieve'` / `collimate`; then histogram / puncture / `probClosest` statistics; `main` prints report |
| `src/Phase.hs` | `Phase` type support |
| `src/Random.hs` | HashDRBG `CryptoRand` wrapper |
| Exports | `module Main (main)` only |

Prior symbolic gates re-read (not re-executed as compute): BATCH-012
`process_extraction.md`, BATCH-013 `recovery_spec.md`, BATCH-017
`lifetime_trace.yaml` + `component_to_F_map.yaml`, BATCH-018 classification
(FAIL control; `QM-STOPPING` still open).

## Attempt outcomes (summary)

Concrete per-check records live in `lifetime_verify_attempt.yaml`.

- `Verify(x,k')`: **absent**
- `W_*` / `R_*` lifetime APIs: **absent**
- FC0 `B_*` schedule: **partial** ambient Haskell only (not FC0)
- `M_tail`: **absent**
- Explicit cleanup / uncompute hooks: **absent** (lexical discard ≠ FC0 cleanup)
- Final key-recovery decision: **absent** (report-only exit)
- Narrowest in-repo stub/hook: **blocked_host_gap**

`puncture` / `probClosest` are probability-summary postprocessing of a
classical `PhaseVector`. They are not recovery, residual-tail search, or
`Verify`.

## Host-gap certificate

Status: **`host_gap_certified`** (see `host_gap_or_impl_status.yaml`).

The pinned host is structurally report-only. Advancing MEMORY/ERROR by writing
a pretend `Verify` or invented `W/R/B/M_tail` wrapper under this task's write
scope would fabricate APIs not present in `CollimationSieve@6f9188e4`, which
the handoff forbids. The honest product of this spike is the checkable gap
certificate, not a partial fake implementation.

## QUERY_MEMORY blockers (honest)

| Blocker | Status after spike |
| --- | --- |
| `QM-STOPPING` | **open** (intentionally not cleared; no τ / joint finiteness invented; BATCH-018 FAIL retained) |
| `QM-MEMORY-MAP` | **open** under `host_gap_certified` — no implemented FC0 lifetimes |
| `QM-ERROR` | **open** under `host_gap_certified` — no Verify; no `F_*` inclusions; no `F_sim→F` |

## Disposition

`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`

Not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW` (lifetimes/Verify still missing).
Not `FC0_UNIFORM_ORACLE_BOUNDARY_UNRESOLVED` (this batch does not diagnose a
uniform-oracle boundary; it certifies a host implementation gap).

## Retained scope limits

- `non_extrapolation: true`
- ttm-v2 retained as finite ideal-choice panel only; **not** equated with BATCH-014
- No numeric security, breakthrough, or goal-completion claim
- Closed IDEA-20260725-001/002/003 not reopened
- Inference: requested `executor-terra`, resolved Cursor Grok, `fallback_used: true`

## Artifacts

1. `spike_report.md` (this file)
2. `host_gap_or_impl_status.yaml`
3. `lifetime_verify_attempt.yaml`
4. `mutation_status.yaml`
5. `classification.yaml`
