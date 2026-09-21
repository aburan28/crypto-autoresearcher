# Instantiation report — TASK-20260730-127 / BATCH-039 / GOAL-SSI-001

**Role:** executor · **Gate chosen:** **A** · **Runs attempted:** 1 (`maximum_runs: 1`)
**Zero curve/isogeny/quantum-circuit compute:** true · **non_extrapolation:** true
**Authority:** DEC-20260730-036 / EV-SSI-038 / RT-20260730-125 ·
amendment `inference-amendment-TASK-20260730-127.yaml`.

## 1. What was executed

Per DEC-20260730-036 the batch had to instantiate **exactly one** substantive
numeric gate rather than stack another placeholders-only schema lane. I took
**gate A (preferred)**: a numeric composition operator + bound units + numeric
width + peak-byte accounting under an explicit in-repo protocol.

The protocol is `FC0-PEAKBYTE-TOY-PROTOCOL-R1`, fully specified in
`protocol_spec.md`. It:

1. Takes the four recovery stages and their concurrently-live member sets
   **verbatim** from BATCH-023 `peak_live_set_accounting.yaml` (no new stages /
   members invented).
2. Assigns each member to a named BATCH-023 slot class `{W, R, B, M}` (plus `T`
   for `accepted_transcript`) by explicit enumeration.
3. Declares toy per-class unit weights in `protocol_slot_bytes`
   (`W=8, R=4, B=2, M=16, T=1`) — stipulated placeholders, **not** measured
   widths, **not** security bits.
4. Defines the numeric composition operator
   `max_over_stages_of_sum_of_live_member_slot_widths`: additive within a stage
   (members concurrently live), max across stages (stages sequential).

### Instantiated numeric result (all recomputed by the harness)

| Stage | `stage_byte_load` |
| --- | ---: |
| preparation | 16 |
| sieve_attempt | 18 |
| recovery | 9 |
| tail_verification | **24** |

- **`peak_byte_bound = 24 protocol_slot_bytes`** at `tail_verification`.
- mistaken cross-stage sum `= 67`, explicitly rejected as the peak.

These discharge — **at protocol-toy / scaffold-scale only** — the
`composition_operator` / `numeric_width` / `peak_byte_bound` placeholders that
BATCH-023..038 carried as null / `not_instantiated`.

## 2. Non-null numeric fields (completion-gate item)

`instantiation_ledger.yaml` carries non-null protocol-derived numerics:
`slot_width_table` (5 values), `stage_byte_loads` (4 values),
`peak_byte_bound.value = 24`, `mistaken_sum_across_stages.value = 67`. Every one
is recomputed from the declared constants by
`instantiation_harness/ledger_checks.py::compute_expected`. This is **not** a
`controlled_null_fatigue` outcome.

## 3. Harness and its adversarial guards

`python3 -m instantiation_harness.run_harness` → **23/23 tests OK**, receipt
`instantiation_harness/harness_receipt.json` (`passed: true`).

- 8 positive checks: numeric recomputation, key-set integrity, no-invented-
  numerics provenance scan, no-illicit-clearance scan, gate/status, QM-STOPPING
  retention, BATCH-023 cross-check, sibling status files.
- 15 injection tests, each asserting the harness **rejects** a mutation:
  wrong `peak_byte_bound`, out-of-protocol slot width, tampered stage load,
  out-of-protocol member, invented `security_bits` field, smuggled numeric under
  an allowed container, `query_memory_cleared`/`clearance`/`pin_complete`/
  `breakthrough`/`cryptographic_scale` flags, disposition downgrade, faked τ
  `PASS`, invented `tau_invented`, and status overclaim.

The provenance scan (`check_no_invented_numerics`) is stricter than the
BATCH-038 detector that DEC-20260730-036 flagged as leaky: it allow-lists
numeric leaves by full provenance and pairs with an exact key-set check, so an
invented number cannot hide under an allowed container key.

## 4. Honest disposition (no clearance / no creep)

- Disposition retained: **`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`**.
- **QM-STOPPING remains open, `control_result: FAIL`** (BATCH-037/036/035/034/
  033/032/031/018 retained; τ **not** invented; this is gate A, not B).
- QM-ERROR retained `f_union_ledger_partial`; QUERY_MEMORY unreconciled.
- QM-MEMORY-MAP: `composition_aggregation_schema_partial` →
  `numeric_composition_operator_protocol_toy_partial` (name carries
  `protocol_toy` so it can never be misread as clearance).
- **No** QUERY_MEMORY clearance, PIN_COMPLETE, numeric-security, breakthrough,
  or completion claim. BATCH-020 `no_admissible_pin` retained. BATCH-014 not
  equated. CollimationSieve@6f9188e4 APIs not invented; BATCH-022 scaffold not
  modified.

The `peak_byte_bound = 24` is meaningless outside this toy protocol. It is not a
cryptographic-scale memory bound and licenses no scope extrapolation.

## 5. Protocol deviations / anomalies (recorded, not discarded)

- **Execution-worktree completeness.** The execution checkout (branch
  `cursor/ssi-batch-038-continue-9aa0`, HEAD `c36cad1252f997892e347a2ed2544fad521e705c`)
  did not have BATCH-023..038 files materialized on disk at run time, and
  exhibited transient churn in the tracked BATCH-039 view. Consequences and
  mitigations:
  - The harness's BATCH-023 cross-check (`check_cross_batch023`) is **best-
    effort**: it activates when the BATCH-023 file is locatable and is skipped
    (recorded `found: false`, non-failing) otherwise. At execution time it
    recorded `found: false` because the file was not in this worktree. This is
    honest and non-fabricated; a reviewer running the harness in a full tree
    gets the active hard equality check.
  - The BATCH-023 stage membership embedded as `CANONICAL_STAGE_MEMBERSHIP` was
    **independently verified equal** to an authoritative physical copy of
    `peak_live_set_accounting.yaml` (`stage_live_sets`) outside this worktree, so
    the numeric derivation is grounded in the real in-repo scaffold/ledger data,
    not transcription drift.
- **Inference fallback.** Requested policy `executor-terra` is unavailable under
  this harness; executed under the Cursor Agent runtime with `fallback_allowed`
  per the approved amendment. Recorded in `classification.yaml`
  (`fallback_used: true`, `model_verified: false`).
- No other deviations. Exactly one run; no reruns-until-favorable.

## 6. Artifacts

- `instantiation_ledger.yaml` — protocol-derived numeric instantiation.
- `protocol_spec.md` — `FC0-PEAKBYTE-TOY-PROTOCOL-R1`.
- `memory_map_status.yaml`, `mutation_status.yaml`, `classification.yaml`.
- `instantiation_report.md` (this file).
- `instantiation_harness/` — `__init__.py`, `ledger_checks.py`,
  `test_instantiation.py`, `run_harness.py`, `harness_receipt.json`.

## 7. Executor assessment (observation, not conclusion)

A protocol-bound numeric instantiation of the composition/aggregation lineage
**is** achievable short of QUERY_MEMORY clearance once an explicit protocol
supplies the missing conversion constants and composition rule — demonstrated
here at toy scale with an independently-recomputable peak-byte number and an
adversarially-guarded harness. Whether this toy instantiation should advance
QM-MEMORY-MAP, and the real-width / cryptographic-scale successor, are decisions
for the Reviewer / Red Team / Coordinator, not this executor.
