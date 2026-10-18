# Legacy stage-0 ECDLP trial manifests fail native admission

- **Status:** resolved for native reproduction of the four named worksheet scopes
- **Kind:** implementation gap; separate director access/tool limit
- **Affected work:** [four original/successor mappings](../coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/mapping.json), [GOAL-ECDLP-001](../ledger/goals/GOAL-ECDLP-001/goal.yaml)
- **Next action owner:** Coordinator archives/publishes the scoped implementation resolution; independent scientific assessment remains separate
- **Last updated:** 2026-10-18

## Problem

The four frozen stage-0 worksheet drivers write `run_id` and metrics but omit the current canonical run fields, so successful original processes cannot yield native `output_validated` receipts. The affected original experiments are EXP-ECDLP-bfbe6f, EXP-ECDLP-5f4f14, EXP-ECDLP-3c166b and EXP-ECDLP-20ac31. Their exact toy curves, samples, seeds and criteria remain fixed in their original specifications.

## Evidence and uncertainty

- **Observed:** [retained original receipts and hashes](../coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/gates/original-attempts.json). RUN-ECDLP-8f5190 has driver/checker exits 0 but native `invalid_output`: its manifest lacks id, status, code, environment, inputs, timing and result, including commit/command and certificate.kind. Other original receipts are retained as they actually arrive; no failed receipt is edited.
- **Derived:** `experiment_execution.trial_state` keeps invalid attempts `needs_reconciliation`. The CLI offers status/run/report, with no command that retroactively validates that attempt. `docs/experiment-execution.md` requires additive contracts/successors; native preapproval refuses an already-approved canonical specification. A protocol amendment alone therefore cannot grant native in-place reapproval.
- **Missing capability:** a new, source-bound adapter producing a canonical outer manifest while preserving old driver/checker/raw bytes, plus complete native-approved successor packages. Nine synthetic adapter tests have passed without invoking the four scientific censuses; full successor trials remain unexecuted at design time.
- **Access/tool limit:** the configured director backend reports ANTHROPIC_API_KEY unset and model IDs unverified. The allowed implementation-tier route is retained; no mechanical runbook, director inference or model binding is fabricated.
- **What this does not establish:** no failure of a mathematical hypothesis, security result, ECDLP attack, new negative theorem or measured pipeline improvement follows from a manifest defect. A schema-valid envelope alone also does not prove computation or independent scientific correctness.

## What would unblock it

- [x] Native prospective preapproval reports approvable:true for the exact four new successor specifications/plans/handoffs/queue after their review_required drafts, source and lane are committed and published.
- [x] Exact approved-byte archives verify against Git, are published, and ordinary selection reports each successor ready.
- [x] Under fresh native claims, all four new successor trials retain original raw bytes/metrics, pass the unchanged original checker controls and the native canonical-manifest gate, with complete source/provenance/output hashes.
- [x] Every original invalid receipt/artifact remains immutable and the new reports label original deterministic readings as in-sample calibration; no scientific interpretation status changes.

Meeting these conditions establishes a compatible reproduction route for these four exact worksheets. Scientific review, execution-proof integration and broader ECDLP conclusions remain separate obligations.

## Next discriminating step

- **Action:** publish the new review_required drafts/source/lane, then run the four exact native preapproval packets in [BATCH-7ddcd6](../coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/preapproval/). Only accepted exact final bytes may be approved, archived and dispatched.
- **Inputs and controls:** original hash-bound driver, checker, plan and specification; one fresh deterministic driver pass and two fixed original-checker recomputations; preserved raw/legacy-manifest identities; command/source/tamper/no-overwrite controls.
- **Execution limits:** one newly allocated run per successor, memory256MiB in its plan, queue concurrency1; no old slot is reused and no campaign spending cap is introduced.
- **Outcomes:** accepted metadata allows the exact reproduction route; schema/provenance/checker failure retains a new invalid attempt and names the adapter defect; infrastructure refusal carries no mathematical reading.
- **Recheck trigger:** native preapproval/publication/readiness completion and the first successor execution receipts.

## Resolution and history

2026-10-18: original driver/checker processes exposed the native manifest defect. A role-separated Executor implemented a new adapter and synthetic failure tests; the Coordinator prepared four review_required successor packages. Unresolved: no full successor trial or scientific promotion is claimed.


## Scoped implementation resolution (DEC-20261018-6b8340)

All four original worksheet scopes now have a fresh native `output_validated` reproduction: EXP-ECDLP-4bb0ef, EXP-ECDLP-087aea, EXP-ECDLP-11c54d and EXP-ECDLP-5d6ec1. Their exact raw and legacy-manifest bytes match their original actual outputs. [Machine-readable comparisons](../reports/ideas_execution_20261018/final-native-worksheets/four-valid-reproductions.json) name each original/new EXP/RUN, status, return codes and hashes. [All nine actual attempts](../reports/ideas_execution_20261018/final-native-worksheets/all-nine-attempts.json) preserve the four original invalid manifests and the intermediate infrastructure failure. [Raw archives](../reports/ideas_execution_20261018/final-native-worksheets/raw-archives.json) are published before derived reports.

The first metadata attempt failed before its scientific driver because Git threaded lstat could not start under 256 MiB. [The retained diagnostic](../coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/runtime/git-preload-index-diagnostic.json) found process-local `core.preloadIndex=false` succeeds under that same limit. The three untouched approved sibling slots used that environment setting; the consumed first slot was preserved, and a separate prospectively approved EXP/RUN/TASK encoded the same setting in both exact argv arrays. No source, fixture, count, memory limit or native gate was altered.

The terminal void-source archive proposal encountered an actual native duplicate-ownership refusal. [The refusal](../coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/first-successor-failure/void-route-refusal.json) remains retained. A distinct zero-run Coordinator preservation producer archived only the eight existing immutable native files through the ordinary full queue/Git verifier; four unproduced adapter outputs remain absent. The failed scientific task is never reclassified completed.

This resolves the metadata-compatible reproduction route for these four exact worksheets only. It does not repair the original immutable manifests, score the slope fixture, provide independent scientific review, resolve the standalone integer-only seed schema discrepancy, or complete the audit's unspecified original eighteen contracts. The local director binding is still unusable; no mechanical runbook, inference compatibility or formal execution proof is claimed. Full-ledger validation remains207 errors with zero-delta admission/approval checks; native scoped gates passing is not global ledger success.
