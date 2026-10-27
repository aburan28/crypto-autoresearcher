# Non-cohort A/A control production and canonical-store delivery

- **Status:** `open`
- **Kind:** implementation gap; access/tool limit
- **Affected work:** GOAL-NISTSEED-ab8949; RQ-NISTSEED-ac8851; prospective EXP-NISTSEED-6886da; BATCH-62db73
- **Next action owner:** Executor, TASK-20261025-ad9d68
- **Last updated:** 2026-10-25

## Problem

The future fixed 21-order ECPP comparison cannot yet be admitted because the public runner accepts only frozen cohort indices while the public checker’s A/A path compares—but does not produce—two non-cohort control fixtures; separately, canonical-store delivery has a public HTTP 403 access refusal.

The public runner `cohort_runner.py` accepts only `--index` in `[0,20]`, and a non-cohort A/A fixture cannot lawfully be fabricated by reusing an out-of-range or cohort input. `cohort_checker.aa_compare` requires two complete schema documents, each with a fixture exactly `{id, public_input}`, and rejects cohort identifiers. The frozen protocol requires an A/A engineering control before scientific launch. A canonical-store push was refused at S3 HeadObject HTTP 403; existing hydrated runtime bytes remain hash-bound public inputs, but the refusal cannot be represented as storage success.

## Evidence and uncertainty

- **Observed:** TASK-20261024-b17301 archived the six cohort runner/checker implementation artifacts at snapshot `68904e9b80c21785f1b17e6dfdb0e01b7aaf5a04`.
- **Observed:** guarded V9 static/mock tests reported 9 methods, 0 failures, 0 errors, no original-boundary attempts, `named_orders_executed: 0`, and `legacy_program_executed: false`.
- **Observed:** `artifact-store-push-v1.json` records the HeadObject 403 and preserved hydrated runtime/PDF bytes.
- **Derived:** current A/A comparison has no source-bound producer for two fresh public non-cohort executions.
- **Missing capability:** a fixed-input A/A producer with control-validity gating before equality comparison.
- **What this does not establish:** no named-order legacy behavior, no primality result, no historical selector, no curve weakness, and no ECDLP conclusion.

## What would unblock it

- [ ] TASK-20261025-ad9d68 delivers a source-bound public-prime-101 A/A producer whose static/mock tests pass the exact real `cohort_checker.aa_compare` path and reject invalid identical pairs.
- [ ] TASK-20261025-5dd15e archives those five artifacts with exact source hashes.
- [ ] A later scientific packet states a lawful raw-artifact storage route without bypassing the recorded public 403.

These conditions establish only an A/A-control implementation prerequisite. They remain insufficient for scientific packet approval, named-order execution, independent replay, historical attribution, or a cryptanalytic conclusion.

## Next discriminating step

- **Action:** implement and mock-test the fixed non-cohort A/A producer under TASK-20261025-ad9d68.
- **Inputs and controls:** public 101 newline input; archived runner/checker interfaces; unchanged runtime/kernel/Data bindings; public storage-refusal record.
- **Execution limits and stop condition:** maximum_runs 0; no `execute_case`, VM, QEMU, legacy executable, storage push, or cohort input. Any such invocation is a refusal.
- **Outcomes and next actions:** a passing mocked implementation permits later prospective packet design only. An invalid fixture, mismatch, or access refusal remains an engineering/access obstruction.
- **Recheck trigger:** archived completion of BATCH-62db73 or an actual authorized storage-access receipt.

## Resolution and history

Unresolved.

## 2026-10-27: independently confirmed validity-before-equality defect

Status remains open. The producer snapshot ec8225d815b0bcb278a0a36666c19b4449224b12 is preserved. Independent failed engineering review TASK-20261027-344233, archived at 85f5fc840546531001affebd4658fbc9aea0bd5e, records 40 PASS and 1 FAIL. Its checks.json losslessly retains the complete 86,096-byte parent execution record, SHA-256 999bf168150105b3bec3484d7bedf797855d05ab0dbfdb2b4b1fd2248efce7ab. Scientific execution counts remain zero in that review.

Observed: two identical schema-valid documents with first-step n=101, D=-1, h=0 and Pratt list [103], bound to text '101 -1 0 103 0 0', reached A/A equal:true. Their certificate root semantics are invalid. This confirms a validity defect in the document-only admission helper; equality does not establish either control's validity. It does not show named-order legacy behavior or explain an omission.

Required exit criteria before repeating this approach: independently validate each A/A control from retained raw certificate, raw checker body, framing/status and exact custody; reject the archived mismatched-root case and a malformed raw-checker-body case at semantic validity before equality; pass an independently invoked ordinary existing build_pair control; remove or restrict any document-only route unable to establish these obligations. Preserve the reviewed snapshot and all raw outcomes. A single special-case root rejection is insufficient.

Four independent obligations remain UNRUN: actual driver-to-checker invocation; quiet CLI after process exit; runner secondary-parser injection; existing A/A build_pair invocation. Producer self-tests or source ordering do not discharge them. Each needs explicit guarded ownership, actual retained outcomes and independent assessment.

Separate obstruction: BATCH-921b7b/DEC-20261027-9eed13 owns the dual-archive custody reconciliation. Its published tasks are prospective and their scopes remain reserved. Do not duplicate that work, overwrite either A/A lineage, alter PR2602/2612 heads or refresh hashes without a prospective versioned correction. Custody reconciliation alone does not resolve the confirmed semantic defect. A future additive integration design must incorporate that lane's actual deliverables and preserve all four independent obligations.

Separate publication observation: the actual PR-scoped artifacts check returned exit 1 with one finding. The archived integration report.pdf is 66,299 bytes, SHA-256 76cf75a35f818482bf71c5f966794128d7b559debb272c00cc317cbe0ce42bb0, above the 65,536-byte DATA_EXT threshold. followup-routing/artifact-policy-observation.json retains the finding and combined-output qualification; symbolic HEAD and separate stdout/stderr were not instrumented. Preserve the completed PDF bytes and snapshot binding. Any prospective canonical-store migration requires authorized ownership, an actual content-identical object/manifest receipt and additive archive handling. No upload has occurred. This publication obligation is distinct from the A/A semantic defect and recorded S3 HTTP403.

The point-first fixed-x source imports neither the ECPP runner nor its A/A producer. Its independent main-based successor need not import the ECPP PDF or source lineage. It must establish its own native raw-artifact custody, source provenance and lawful serial claim. This does not resolve the ECPP problem. The full historical/predictive commonality requirement, all 21 identities and broader 69-position limits remain unchanged.
