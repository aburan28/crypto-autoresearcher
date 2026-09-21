# Falsification review — RT-20260730-125 / BATCH-038

**Task:** TASK-20260730-125 (red-team) · **Goal:** GOAL-SSI-001 · **Batch:** BATCH-038
**Snapshot under review:** `4ea1dc198b241943592f1b6185f3111018b466a5` (parent `32b689ea6`, bound at HEAD `9c926f1c2`)
**Producer:** TASK-20260730-123 composition/aggregation schema ledger package
**Verdict:** CONFIRM — scoped to the narrow disposition only; **blocking on next-batch direction** (search-fatigue gate).
**Inference:** requested `review-adversarial` (handoff requires `review-xhigh`); resolved **Cursor Agent (Claude Opus 4.8)**, `fallback_used: true` (GPT Sol family unavailable), independent session. **Not** a goal-closure quorum attestation.

---

## 1. Snapshot integrity — verified independently

| Check | Result |
| --- | --- |
| `parent_sha` in receipt vs `git rev-parse 4ea1dc198^` | `32b689ea6…` = `32b689ea6…` **match** |
| Changed paths in archive commit | exactly **11** = 10 producer sources + `snapshot-receipt.json`; none outside `BATCH-038/` |
| CollimationSieve / `ledger/` / BATCH-022 touched by archive commit | **none** |
| sha256 of each declared producer path via `git show 4ea1dc198:<path>` | **all 10 match** the receipt |
| `composition_aggregation_harness` re-run (`python3 -m …run_harness`, scratch copy) | **5/5 OK**, receipt reproduced **byte-identical** |
| Repo working tree | clean (harness re-run done on an out-of-repo scratch copy; no producer artifact mutated) |

The snapshot is a durable, faithful commit of the reviewed artifacts. The committed receipt still carries `commit_sha: null` / `verification.status: pending_post_commit` — the same non-blocking pattern flagged in RT-20260730-121; Git ancestry + path-scope + hash checks establish the snapshot regardless (objection `RECEIPT-PENDING-POST-COMMIT`).

## 2. Producer claims — checked, not trusted

- **39 items; wired_symbolic=25, checklist_only=1, not_instantiated=9, not_supported=4, deferred=0.** Independently recounted from the ledger YAML: family split 6/5/5/4/5/14 and status split 25/1/9/4/0, identity `25+1+9+4+0 = 39`. **Confirmed.**
- **QM-MEMORY-MAP: `global_memory_bound_schema_partial` → `composition_aggregation_schema_partial`; clearance:false.** Structured fields keep `reconciled:false`, `clearance:false`, `query_memory_cleared:false`. **Confirmed as a status rename, not a clearance.**
- **Disposition `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`; QM-STOPPING FAIL retained; zero compute.** Confirmed in `classification.yaml`, `mutation_status.yaml`, harness receipt.
- **No invented `composition_operator` / `aggregation_factor` / numerics.** Independent full walk of all 39 items: every `composition_operator`, `aggregation_factor`, `global_memory_bound`, `numeric_width`, `peak_byte_bound`, charge, and `tau` value field is `null`/`unresolved`/`not_instantiated`/`not_supported`. **Zero invented numeric assignments.** The claim is TRUE for this snapshot.
- **No CollimationSieve API invention.** `composition_law_api`, `peak_aggregation_api`, `global_fc0_memory_bound_api` are `false`; `composition_law_api` appears only as a `not_supported` placeholder field; `collimation_sieve_negative_control` = `host_gap_certified_retained_untouched`, `apis_invented:false`. **Confirmed.**
- **ttm-v2 not equated to BATCH-014.** `ttm_v2_scope.equated_to_batch014:false`, `usable_as_global_tau:false`, supplies neither operators nor factors. **Confirmed.**

## 3. Positive control (RT-121 style) — detector fires, with a coverage gap

Fault injection against `check_no_invented_numerics` (scratch copy):

| Injected mutation | Detector |
| --- | --- |
| `aggregation_factor = 2.0` | **DETECTED** |
| `composition_operator = 3` | **DETECTED** |
| `query_memory_cleared = true` | **DETECTED** (forbidden_true) |
| `tau_invented = true` | **DETECTED** (forbidden_true) |
| `global_memory_bound = 123456` | **MISSED** (harness stays green) |
| `numeric_width = 4096` | **MISSED** |
| `peak_byte_bound = 99999` | **MISSED** |

The specific falsifiers named in the mandate (invented operator/factor, illicit clearance) are guarded. But the check named `no_invented_numerics` does **not** scan the `numeric_width` / `peak_byte_bound` / `global_memory_bound` value fields — quantities the batch objective explicitly forbids inventing. **A green harness is not a sufficient witness for the full "no invented numerics" claim** (objection `CONTROL-COVERAGE-GAP`); here the claim is backed by the independent field scan in §2, and downstream ledger prose must cite that scan, not the harness alone.

## 4. What the reported quantity should have done — the search-fatigue tell

Per `docs/inventor-protocol.md` §3–§4, ask what the measured quantity should do as the parameter meant to destroy it increases, and hold closures/progress-claims to the same burden as claims.

BATCH-023 → BATCH-038 form a monotone chain of `*_schema_partial` placeholder lanes (peak_liveset, resource_vector, charge_incidence, retry_cleanup_tail, verify_exit, history_uniform_tail, tau_schema_stopping_fail, width_schema, width_slot_binding, retry_peak_byte, peak_byte_bound, charge_metering, global_memory_bound, and now composition_aggregation). Across all of them:

- the count of `not_instantiated`/`not_supported` value fields — the quantity that **should decay** as the lane makes real progress — **does not decay**; every named numeric value is still `null`/`unresolved`;
- `control_result` stays **FAIL**; QM-STOPPING stays **open**; QUERY_MEMORY stays **unreconciled**;
- the QM-MEMORY-MAP status string has been renamed ≥4 times while naming the same empty fields.

A quantity that stays flat when the parameter meant to move it increases is the canonical artifact/fatigue tell. Under §4, "we named N more obligations" is a fatigue report about the search, not a statement about the problem. RT-20260730-121 already issued the required control `NEXT-MEMORY-MAP-OR-STOPPING-GATE` (instantiate numerics **or** source τ); the program answered with another placeholder lane. **The claim that QM-MEMORY-MAP is *advancing* toward reconciliation is therefore, as a progress claim, `unverified`.**

This is **not** a falsifier of the BATCH-038 artifact — TASK-123 honestly and correctly executed the exact placeholders-only brief the Coordinator handed it, and its narrow disposition is fully supported (verdict CONFIRM). It **is** a binding challenge to the continuation (objection `SEARCH-FATIGUE-SCHEMA-STACKING`, `blocking_for_next_batch_direction`).

## 5. Baseline / Pareto / cost

No solve path, resource vector, time, or memory quantity exists, so Pollard-rho, BSGS, and CollimationSieve comparisons are all inadmissible; van Oorschot–Wiener time–memory interpolation is not engaged. `dominated_by: not_evaluable` (no attack point), `sota_delta: not_claimed`. Total-expected-cost bookkeeping is inapplicable (no attempt-success probability under F). No numeric-security, breakthrough, or completion claim is present or warranted.

## 6. Recommendation for BATCH-039 — one substantive gate

CONFIRM the BATCH-038 artifacts under the `LEDGER-SCOPE-WORDING` control, then **gate BATCH-039 on exactly ONE substantive instantiation, not another placeholder lane**:

- **(A, primary)** Instantiate a numeric **composition operator + bound units + at least one numeric width or peak-byte accounting** under an explicit in-repo protocol — converting the composition/aggregation & global-memory lineage that BATCH-023→038 only deepened symbolically into a checkable numeric artifact; **or**
- **(B, alternative)** **Source-instantiate a Verify-relative τ with joint Q/S/P/C(+H) finiteness** for QM-STOPPING.

Both must remain **zero-curve-compute and fully in-repo**. **Do not** route BATCH-039 to EXP-SSI-001 or any curve/isogeny/quantum-circuit computation (approved, but not the active campaign gate). If BATCH-039 again produces placeholders-only with all value fields null, that outcome must be recorded as a **controlled null / fatigue report at status `unverified`**, not as MEMORY-MAP advancement.

---

### Scope limits
Review limited to snapshot `4ea1dc198` (HEAD `9c926f1c2`), `DEC-20260730-035`, `EV-SSI-037`, and the read-only lineage cited by the producer. No curve/isogeny/quantum/simulator computation was run; the harness re-run was pure YAML/consistency checking on an out-of-repo scratch copy. Conclusions concern only the bounded write-scope schema honesty, FAIL retention, un-cleared QM-MEMORY-MAP advancement to `composition_aggregation_schema_partial`, lineage retention, and open-blocker retention. `maximum_runs: 1`.
