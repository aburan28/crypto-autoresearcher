# BATCH-040 / TASK-20260730-131 — execution report

- Goal: GOAL-SSI-001 · Batch: BATCH-040 · Idea: IDEA-20260729-001 (CSIDH-COLLIMATION-FC0-R2)
- Decision ref: DEC-20260730-037 · Evidence input: EV-SSI-039 · Red-team input: RT-20260730-129
- Role: **executor** (observations only; no state transition, no promotion)
- Git revision at execution: `912e45f90b1a7c77ef9d8c1c7318cba6e7e827dd` (clean tree)
- Maximum runs: 1 · Runs attempted: 1 · Curve/isogeny/quantum compute: **none**

## 1. What was produced (deliverables)

A single bounded, zero-compute batch with two deliverables and an adversarial harness.

**Deliverable 1 — host-integration WIDTH CONTRACT** (`host_width_contract.yaml`):
Specifies, without inventing any value or API:
- the **hooks** that would emit real per-slot widths — all twelve frozen FC0
  lifetime hooks (read from the BATCH-022 scaffold
  `LifetimeRegistry.REQUIRED_HOOK_IDS`), each tagged with object class, the
  stages it is live in, and its `birth_*` signature reference;
- an honest **emission gap**: exactly one hook (`M_tail`) exposes a per-slot
  width-declaration channel (`birth_M_tail(..., width_decl, ...)`), and it is
  **symbolic-only** (the scaffold rejects `numeric_width`). The other eleven
  hooks have **no** width-declaration parameter, so there is currently **no
  emission point** for their real widths. This is recorded as a prerequisite, not
  filled with an invented accessor;
- **units**: every real unit is `null` (unsourced);
- **operator consumption**: the composition operator
  `max_over_stages_of_sum_of_live_member_slot_widths` (the same accounting rule
  instantiated at toy scale in BATCH-039) is specified as a two-level consumer —
  within-stage sum of live members' real widths, across-stage max over
  `state_machine.STAGE_LIVE_SETS` — with `bound_units: null` and `peak.value:
  null`.

Every real per-slot width, unit, and peak is **`null`**, because the only
admissible source — the CollimationSieve host (`6f9188e4…`) — is
host-gap-certified and `no_admissible_pin` (BATCH-020, retained). The toy
peak-byte lane is **not** iterated and no numeric bound is asserted.

**Deliverable 2 — QM-STOPPING obstruction analysis** (`stopping_obstruction_analysis.md`):
Begun to the inventor-protocol §4 standard. Honest disposition: **`unverified`**.
It records the fatigue fact (FAIL retained ≥8 batches is a statement about the
search, not the problem), articulates a **candidate** obstruction
(*Verify-relativity of the stopping time*) as an explicit hypothesis, and shows
via the §8 audits (quantifier order, method ceiling, observation collision) why it
does **not** yet meet the §4 standard — the repeated non-clearance currently
traces to an availability/host gap, which per AGENTS.md rule 5 is not a proven
mathematical obstruction. Forward guidance names what a real obstruction (or its
refutation) must establish. No τ is invented; no closure or clearance is claimed.

**Pre-registered validation/falsification plan** (`validation_falsification_plan.yaml`):
Maps to the inventor-protocol §6 ladder, requires an admissible pin before
execution, registers five concrete falsification conditions (F1–F5) that can fail,
and pre-registers a null-object control (the M-dominance artifact tell from
RT-20260730-129 OBJ-2). `measurement_performed: false`.

## 2. Harness results

`contract_harness/` holds the sourced structural facts independently of the
artifacts and rejects invented/out-of-protocol content.

- **34/34 tests OK**, all 11 checks passed, receipt `passed: true`
  (`contract_harness/harness_receipt.json`).
- Injection tests confirm rejection of: invented real width value / units /
  numeric peak / bound units; a source marked available; out-of-protocol hook or
  stage member; invented `security_bits`; a width channel added to the wrong hook
  or removed from `M_tail`; illicit `query_memory_cleared`; a **novel**
  clearance-like key (`query_memory_solved`, hardening RT OBJ-1); crypto-scale
  relabel; disposition downgrade; pin/API/`admissible_pin`/scaffold-modified
  tamper; operator-id tamper; a plan with measurement performed / no falsification
  condition / no null control; and an obstruction write-up that overclaims a
  closure or omits forward guidance.

## 3. Statuses (retained / recorded)

| Item | Status |
|---|---|
| Disposition | `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` (retained) |
| QM-MEMORY-MAP | `numeric_composition_operator_protocol_toy_partial` (**retained, not advanced**) |
| QM-STOPPING | `remains_open`, control_result **FAIL** (retained incl. BATCH-039) |
| QM-STOPPING obstruction | analysis begun; **`unverified`**; no named §4 obstruction |
| QM-ERROR | `f_union_ledger_partial` (retained) |
| QUERY_MEMORY | `unreconciled` |
| BATCH-020 pin | `no_admissible_pin` (retained) |
| CollimationSieve APIs invented | false · scaffold modified: false · BATCH-014 equated: false |

## 4. Claim boundaries / non-claims

- This is a **host-integration boundary specification** plus a **begun** stopping
  obstruction analysis. It is **not** QUERY_MEMORY clearance, **not** a
  cryptographic-scale memory bound, **not** a MEMORY-MAP advancement, **not** τ /
  joint finiteness, and **not** a security / breakthrough / completion / PIN_COMPLETE
  result.
- No curve/isogeny/quantum compute; EXP-SSI-001 **not** launched. The toy
  peak-byte lane was **not** iterated and no fake-τ gate B was attempted.
- All real widths/units/peaks are `null` (host-gap / no_admissible_pin). No
  CollimationSieve API was invented or called; the BATCH-022 scaffold and the
  `6f9188e4…` pin are untouched.

## 5. Inference / provenance

Requested policy `executor-implementation`; under this Claude Code / Cursor Agent
harness it did not resolve to its intended backend (CLAUDE.md model policy note),
so it ran under the available **Cursor Agent (Claude Opus 4.8)** with
`fallback_used: true` (authorized by handoff `fallback_allowed: true`; no separate
BATCH-040 amendment file is present). `model_verified: false`,
`degraded_allowed: false`, `independent_session: false`. Recorded in
`classification.yaml`.

## 6. Deviations

None from the approved handoff. Note recorded: no BATCH-040
`inference-amendment-*.yaml` exists (prior batches had one); fallback is authorized
by the handoff field and CLAUDE.md and is recorded rather than assumed.

## 7. Artifacts (this task)

- `host_width_contract.yaml`
- `validation_falsification_plan.yaml`
- `stopping_obstruction_analysis.md`
- `memory_map_status.yaml`
- `classification.yaml`
- `contract_report.md`
- `contract_harness/{__init__,ledger_checks,test_contract,run_harness}.py`
- `contract_harness/harness_receipt.json`
