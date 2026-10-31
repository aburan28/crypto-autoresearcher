# Non-cohort A/A control production and canonical-store delivery

- **Status:** `open`
- **Kind:** implementation gap; access/tool limit
- **Affected work:** GOAL-NISTSEED-ab8949; RQ-NISTSEED-ac8851; prospective EXP-NISTSEED-6886da; BATCH-62db73
- **Next action owner:** Coordinator, prospective packet and real-boundary binding; TASK-20261025-ad9d68 is complete
- **Last updated:** 2026-10-27

## Problem

The future fixed 21-order ECPP comparison cannot yet be admitted. The non-cohort A/A producer is now implemented and archived with passing mocked tests, but the separate scientific packet and bound real A/A boundary are absent. Current-host runtime availability is unverified, and canonical-store delivery still has the public HTTP 403 access refusal.

The public runner `cohort_runner.py` accepts only `--index` in `[0,20]`, and a non-cohort A/A fixture cannot lawfully be fabricated by reusing an out-of-range or cohort input. `cohort_checker.aa_compare` requires two complete schema documents, each with a fixture exactly `{id, public_input}`, and rejects cohort identifiers. The frozen protocol requires an A/A engineering control before scientific launch. A canonical-store push was refused at S3 HeadObject HTTP 403; existing hydrated runtime bytes remain hash-bound public inputs, but the refusal cannot be represented as storage success.

## Evidence and uncertainty

- **Observed:** TASK-20261024-b17301 archived the six cohort runner/checker implementation artifacts at snapshot `68904e9b80c21785f1b17e6dfdb0e01b7aaf5a04`.
- **Observed:** guarded V9 static/mock tests reported 9 methods, 0 failures, 0 errors, no original-boundary attempts, `named_orders_executed: 0`, and `legacy_program_executed: false`.
- **Observed:** `artifact-store-push-v1.json` records the HeadObject 403 and preserved hydrated runtime/PDF bytes.
- **Historical assessment, 2026-10-25:** the A/A comparator then lacked a source-bound producer. This implementation gap is superseded by the archived package below, without claiming real repeatability evidence.
- **Observed, 2026-10-27:** TASK-20261025-ad9d68 and TASK-20261025-5dd15e are released completed. Snapshot `f80cf4fbf023f4d1722062d458d5d4b72ed9bcfb`, parent `54838684121586697ad7c38354bac45cf6e26578`, contains exactly the five implementation artifacts and precommit receipt. All six Git-blob and current-path SHA-256 values match the queue and postcommit verification. Metadata commit `691837c4aff048b7c299f0f8a5d4a5a5bc54fcd1` was merged through [PR #2607](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2607) at `6464133bfc8d76771c523bfb6bc3c56763b747b4`.
- **Observed:** the archived test report records eight passing mocked tests, zero named orders and no legacy execution. `build_pair` has no default real boundary or CLI; the mocked boundary is not a real A/A execution.
- **Current-host availability limit:** `/tmp/crypto-autoresearcher-nistseed-recovery-20261027` lacks the ignored `.work/build-v4/ECPP/Ecpp/Data` and `.work/qemu-runtime` directories, and this Linux host lacks `/opt/homebrew/bin/qemu-system-i386`. This says nothing about availability of bound bytes elsewhere or changes to their public manifests. All 18 frozen runner repository-source hashes still match.
- **Missing contract:** no canonical specification, protocol or trial plan exists for EXP-NISTSEED-6886da. The [read-only post-completion design assessment](../coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/post-completion-design-20261027.json) preserves `experiment_preapproval`'s `approvable: false` diagnosis and its 27 missing-contract/binding blockers. These diagnose an absent prospective packet, not an experimental failure.
- **What this does not establish:** no named-order legacy behavior, no primality result, no historical selector, no curve weakness, and no ECDLP conclusion.

## What would unblock it

- [x] TASK-20261025-ad9d68 delivered the source-bound public-prime-101 A/A producer and eight passing mocked tests archived in the completion checkpoint. This records producer-task completion; the later independent review below identifies a validity-before-equality defect and remains unsatisfied.
- [x] TASK-20261025-5dd15e archives those five artifacts with exact source hashes.
- [ ] A separate prospective packet binds a real non-cohort A/A boundary, validity checks before equality, independent replay, full controls, protocol, trial plan and review/archive coverage; its exact prospective bytes pass preapproval before approval is recorded.
- [ ] Before claiming current-host runnable admission, a separately authorized route provides and verifies the required existing Data/runtime/emulator identities. No hydration, VM, or storage operation is authorized by this record.
- [ ] A later scientific packet states a lawful raw-artifact storage route without bypassing the recorded public 403.

These conditions establish only an A/A-control implementation prerequisite. They remain insufficient for scientific packet approval, named-order execution, independent replay, historical attribution, or a cryptanalytic conclusion.

## Next discriminating step

- **Action:** Coordinator completes the separate source-only prospective packet and binds its real non-cohort A/A boundary; do not repeat the completed producer task.
- **Inputs and controls:** public 101 newline input; archived runner/checker interfaces; unchanged runtime/kernel/Data bindings; public storage-refusal record.
- **Execution limits and stop condition:** this continuation is source/protocol work only; no `execute_case`, VM, QEMU, legacy executable, storage operation, or cohort input. Any required real execution belongs to a later approved `/run`, outside `/coordinate`.
- **Outcomes and next actions:** exact prospective preapproval can qualify only its bound bytes for subsequent Coordinator approval/archive; a refusal leaves the missing fields or identities explicit. Neither outcome establishes scientific readiness or a cohort result by itself.
- **Recheck trigger:** a complete prospective packet, verified current-host availability, or a new separately authorized storage-access receipt. The public 403 is not bypassed or converted to success.

## Resolution and history

Open. Mocked implementation and its source custody are complete; real-boundary/packet admission, current-host availability and canonical delivery remain distinct unresolved requirements. See the [completion checkpoint](../ledger/goals/GOAL-NISTSEED-ab8949/checkpoints/BATCH-62db73-20261027-completion.yaml). No scientific conclusion or goal completion criterion is asserted.

The implementation-completion checkpoint above and the later independent failed review below are distinct observations. The problem remains open.

## 2026-10-27: independently confirmed validity-before-equality defect

Status remains open. The producer snapshot ec8225d815b0bcb278a0a36666c19b4449224b12 is preserved. Independent failed engineering review TASK-20261027-344233, archived at 85f5fc840546531001affebd4658fbc9aea0bd5e, records 40 PASS and 1 FAIL. Its checks.json losslessly retains the complete 86,096-byte parent execution record, SHA-256 999bf168150105b3bec3484d7bedf797855d05ab0dbfdb2b4b1fd2248efce7ab. Scientific execution counts remain zero in that review.

Observed: two identical schema-valid documents with first-step n=101, D=-1, h=0 and Pratt list [103], bound to text '101 -1 0 103 0 0', reached A/A equal:true. Their certificate root semantics are invalid. This confirms a validity defect in the document-only admission helper; equality does not establish either control's validity. It does not show named-order legacy behavior or explain an omission.

Required exit criteria before repeating this approach: independently validate each A/A control from retained raw certificate, raw checker body, framing/status and exact custody; reject the archived mismatched-root case and a malformed raw-checker-body case at semantic validity before equality; pass an independently invoked ordinary existing build_pair control; remove or restrict any document-only route unable to establish these obligations. Preserve the reviewed snapshot and all raw outcomes. A single special-case root rejection is insufficient.

Four independent obligations remain UNRUN: actual driver-to-checker invocation; quiet CLI after process exit; runner secondary-parser injection; existing A/A build_pair invocation. Producer self-tests or source ordering do not discharge them. Each needs explicit guarded ownership, actual retained outcomes and independent assessment.

Separate obstruction: BATCH-921b7b/DEC-20261027-9eed13 owns the dual-archive custody reconciliation. Its published tasks are prospective and their scopes remain reserved. Do not duplicate that work, overwrite either A/A lineage, alter PR2602/2612 heads or refresh hashes without a prospective versioned correction. Custody reconciliation alone does not resolve the confirmed semantic defect. A future additive integration design must incorporate that lane's actual deliverables and preserve all four independent obligations.

Separate publication observation: the actual PR-scoped artifacts check returned exit 1 with one finding. The archived integration report.pdf is 66,299 bytes, SHA-256 76cf75a35f818482bf71c5f966794128d7b559debb272c00cc317cbe0ce42bb0, above the 65,536-byte DATA_EXT threshold. followup-routing/artifact-policy-observation.json retains the finding and combined-output qualification; symbolic HEAD and separate stdout/stderr were not instrumented. Preserve the completed PDF bytes and snapshot binding. Any prospective canonical-store migration requires authorized ownership, an actual content-identical object/manifest receipt and additive archive handling. No upload has occurred. This publication obligation is distinct from the A/A semantic defect and recorded S3 HTTP403.

The point-first fixed-x source imports neither the ECPP runner nor its A/A producer. Its independent main-based successor need not import the ECPP PDF or source lineage. It must establish its own native raw-artifact custody, source provenance and lawful serial claim. This does not resolve the ECPP problem. The full historical/predictive commonality requirement, all 21 identities and broader 69-position limits remain unchanged.
