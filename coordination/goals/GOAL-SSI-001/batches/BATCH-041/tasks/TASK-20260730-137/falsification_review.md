# Falsification review — BATCH-041 / TASK-20260730-137 (red-team)

- Reviews: TASK-20260730-135 (QM-STOPPING §6 item-1 host-independence reduction)
- Snapshot under review: `1c87431dcb846117112cd49b3d3f89d2918d5fbf` (bind `15a186e833e09a548053269b35fcf572ab6a30f8`)
- Report: `RT-20260730-137` · Role: red-team · Independent session: true
- Resolved model: Cursor Agent (Claude Opus 4.8), authorized fallback, `model_verified:false`
- **Verdict: CONFIRM_SCOPED** (no blocking objection; five non-blocking objections OBJ-1…OBJ-5)

## 0. Mandate

I was asked to try to break, specifically: fake OUTCOME-R (esp. BATCH-012 local
kernel inflation / invented mixing-collision bounds), fake OUTCOME-D / §4
closure without discharged ∀-hosts, a ninth unverified re-record disguised as
disposition, illicit QUERY_MEMORY / QM-STOPPING clearance, MEMORY-MAP advance,
fake-τ, CollimationSieve API invention, BATCH-014 equation, breakthrough /
completion, and a pause without concrete revisit conditions. I ran the
reproduction and independent citation probes below; I could not make any of
those failures stick. The claim survives as a bounded neither_pause with
REV-1/REV-2.

## 1. What I reproduced independently

**Snapshot ancestry + hashes.** `git` confirms `1c87431dc` has parent
`47a40c336` (equal to the recorded `parent_sha` and producer
`git_revision_at_execution`), changes exactly 12 files (11 producer artifacts +
`snapshot-receipt.json`), and the bind commit `15a186e83` has parent
`1c87431dc`. I recomputed sha256 for all 12 archive-block paths directly from
`git show 1c87431dc:<path>`; every hash matches the dispatch_queue
`path_sha256` block (and the pending receipt's `source_path_sha256` for the
producer set). No scope expansion.

**Harness.** From `coordination/goals/GOAL-SSI-001/batches/BATCH-041/tasks`,
created a temporary empty `TASK-20260730-135/__init__.py` solely for the module
path, ran `python3 -m TASK-20260730-135.reduction_harness.run_harness`, then
deleted that undeclared file. Result: **20/20 OK**, exit 0,
`harness_receipt.json` sha256
`cbbbb78bd1fdaba54b221e4730ba9fe0a9cc80f842e2b6d38e83c0c9f94fe61c`
unchanged (byte-stable vs snapshot). Producer tree clean afterward.

**Citation / content spot-check (load-bearing for neither_pause).** All six Prop
citation paths exist on disk. Content checks:

- BATCH-031 `tau_schema_stopping_ledger.yaml`: `transition_kernel`,
  `independence_conditions`, `uniform_success_lower_bound` are `null`;
  OBL-TI-transition_kernel / OBL-TI-independence_conditions /
  OBL-TI-uniform_success_lower_bound are `status: not_supported`.
- BATCH-012 `process_extraction.md`: explicit local recursive-sieve kernel only;
  rejects invented end-to-end process completion; no uniform progress/tail bound
  / end-to-end stopping law.
- BATCH-030 history-uniform progress law: `not_supported`;
  `supplies_global_history_uniform_stopping: false`.
- BATCH-021 `verify_interface.yaml`: `invents_tau: false`,
  `clears_QM_STOPPING: false`.
- DEC-20260730-038 next action matches this batch's neither/pause-with-revisit
  obligation.

BATCH-022 scaffold remains unmodified (no dirty scaffold paths under the pin).

## 2. The seven falsification attacks I ran, and why they failed

**Attack A — fake OUTCOME-R via BATCH-012 local kernel inflation.** Producer
records PROP-LOCAL `committed_status: local_only_not_end_to_end_tau` and
`discharges_outcome_R: false`, citing the process_extraction refusal of
end-to-end stopping-law completion. Harness injection
`test_local_prop_discharges_r_rejected` fails any ledger that marks PROP-LOCAL
as discharging R. Independent read of BATCH-012 confirms the inflation would
violate OUTCOME-R requirement N. **Failed to break.**

**Attack B — fake OUTCOME-R via invented mixing / collision / kernel bounds.**
PROP-MIX / PROP-KERNEL / PROP-USB remain null / not_supported under BATCH-031
citations; no numeric mixing-time, collision-distribution, or uniform-success
bound is introduced. Inventing those ingredients would fabricate the missing
Prop (AGENTS rule 9); producer refuses. **Failed to break.**

**Attack C — fake OUTCOME-D / §4 closure without ∀-hosts.** Ledger
`outcome_D_audit` sets `forall_hosts_discharged: false`,
`argument_about_object_not_availability: false`, and names BATCH-019/020 host
gap as availability (not object obstruction). Flags
`named_obstruction` / `meets_inventor_protocol_s4` / `is_closure_claim` /
`dependence_essential_scoped` are all false; harness rejects flipping them to
true. Quantifier-order attack (choosing the absent pin as the ∀-hosts witness)
does not go through. **Failed to break.**

**Attack D — ninth unverified re-record disguised as disposition.** Primary
disposition is `neither_pause` with `qm_stopping_lane: paused_pending_revisit`
and `ninth_unverified_rerecord: false`. The verify-relativity candidate remains
`open_unresolved_not_refuted_not_proven`, but is not re-filed as another
`OBSTRUCTION_ANALYSIS_STATUS: unverified` headline. Harness rejects
`ninth_unverified_rerecord: true`. This matches DEC-038's pause-rather-than-ninth
instruction. **Failed to break** (residual: OBJ-2 notes both revisits are
currently unmet — direction note, not a disguise).

**Attack E — illicit QUERY_MEMORY / QM-STOPPING clearance, MEMORY-MAP advance,
fake-τ, API invention, BATCH-014, breakthrough/completion.** Disposition remains
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`; `query_memory.cleared: false`;
QM-STOPPING retains FAIL; MEMORY-MAP `advanced_this_batch: false` with status
retained; `tau_invented: false`; `joint_finiteness_established: false`;
`gate_B_taken: false`; `collimation_sieve_apis_invented: false`;
`batch014_equated: false`; completion/breakthrough self-check flags false.
Harness injections for clearance, fake-τ, gate B, MEMORY-MAP advance, API
invention, and disposition drift all reject. **Failed to break.**

**Attack F — pause without concrete revisit conditions.** REV-1 (admissible
CollimationSieve pin superseding BATCH-020 `no_admissible_pin`) and REV-2
(committed host-independent Prop meeting OUTCOME-R P,I,F,B,N) are present in
ledger, markdown, classification, and memory_map_status. Harness requires both
ids (`test_missing_revisit_rejected`). **Failed to break.**

**Attack G — snapshot / receipt integrity.** Parent sha, 12-file scope, and all
path hashes match; harness receipt is byte-stable after independent re-run;
temporary module `__init__.py` was removed and did not remain as an undeclared
artifact. **Failed to break.**

## 3. What remains open (not a break)

OBJ-1: harness locks neither_pause (claim-guard, not a three-outcome discovery
verifier). OBJ-2: REV-1/REV-2 are concrete but currently unavailable, so
Coordinator must move to a different QUERY_MEMORY lever rather than re-queue
QM-STOPPING. OBJ-3–OBJ-5 are informational (PROP-KERNEL label nit;
`model_verified:false`; denylist residual).

## 4. Narrowest supported statement

At zero compute, BATCH-041 earns neither OUTCOME-R nor OUTCOME-D from committed
citations, pauses the QM-STOPPING lane with REV-1/REV-2, retains FAIL and
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, and does not clear QUERY_MEMORY,
advance MEMORY-MAP, invent τ/APIs, or claim breakthrough/completion. Nothing
more.

## 5. Recommended Coordinator next action

Ledger-archive as neither_pause; officially pause QM-STOPPING pending REV-1/REV-2;
do not queue another QM-STOPPING reduction while both revisits remain unmet;
next bounded work: a different still-open blocker (prefer QM-ERROR
`f_union_ledger_partial`, or pin-seeking without API invention); no toy width
iteration, no fake-τ gate B, no MEMORY-MAP advance without real widths, no
QUERY_MEMORY clearance, no EXP-SSI-001.
