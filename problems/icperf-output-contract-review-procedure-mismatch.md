# Prime63 m=2 output-contract review procedure mismatch

- **Status:** `open`
- **Kind:** review procedure and checker-contract mismatch; separate from the implementation/output obstruction
- **Affected work:** [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [TASK-20261025-b2e2cd](../ledger/handoffs/TASK-20261025-b2e2cd.yaml), [TASK-20261025-6d007d](../ledger/handoffs/TASK-20261025-6d007d.yaml), [DEC-20261025-5b84e8](../ledger/decisions/DEC-20261025-5b84e8.yaml), [new split plan](../coordination/review/icperf-prime63-m2-output-contract-v2-remedy-20261025/review-plan.yaml)
- **Next action owner:** Coordinator for exact-session admissions and archive; independent Validators for B1 and O1–O3
- **Last updated:** 2026-10-25

## Problem

Prospective source acceptance for the prime63 m=2 no-science output-contract bridge cannot use the first independent Validator round because its frozen plan and truthful single-task attestation fail two pinned review-independence checks. This is a review-procedure obstruction for TASK-20261020-f237a2 source and its canned fixtures. It does not establish a source defect or change the historical EXP-ICPERF-515ae3 invalid_output finding.

## Evidence and uncertainty

- **Observed:** The blind derivation was committed before candidate source reads at `932e5d00147cc206a5a15144f5001d928c3d5259`. Report and attestation followed at `2d2bbd835c`. [TASK-20261025-6d007d snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-ac3c38/archives/TASK-20261025-6d007d/snapshot-receipt.json) binds all three review outputs at `9eb226fb6a87b8e66c8befd7d0149b0d42c0c90e`; separate receipt introduction `d87d1a3652dbbc1766c72d51174c6c69ac91660c` and GitRepositoryVerifier passed. The pinned checker reported exactly two failures: no rationale for nonempty `blindness.lifted_for` in the frozen plan, and six `blind_from` paths present in the same task's honest final `sources_read` after unblinding.
- **Observed, limited:** The Validator's archived report gives O1/O2/O3 holds on tested canned engineering cases, including two complete outputs, four invalid controls and extra single-field mutations. Its [attestation](../coordination/review/icperf-prime63-m2-output-contract-v2-20261025/TASK-20261025-b2e2cd/attestation.yaml) expressly records the failed procedure check. Those observations are retained, but this round cannot authorize source acceptance.
- **Derived from checker source:** `tools/check_review_independence.py` checks a rederivation task's entire declared `sources_read` against `blind_from`; it has no temporal exception for reads after a same-task seal. Its supported addenda retain the frozen broad lift and do not add the missing legacy `blindness.rationale`. A phase-split addendum could reassign blind derivation but would leave the first failure.
- **Suspected explanation:** The single-task plan modeled a temporal blind-then-unblind workflow that the mechanical checker represents as an all-time read exclusion. The seal chronology supports separation in time, but cannot make the existing composition PASS.
- **Missing capability:** A fresh honest independent review composition that passes its frozen plan, complete release/snapshot custody and the pinned checker, followed by Coordinator interpretation.
- **What this evidence does not establish:** No scientific solver correctness, relation yield, rank, certificate, complete IC cost, speedup or rho comparison follows. The historical run remains invalid_output; bounded censored observations remain censored.

## What would unblock it

- [ ] Commit/push the [fresh split plan](../coordination/review/icperf-prime63-m2-output-contract-v2-remedy-20261025/review-plan.yaml) and its handoffs before either new Reviewer runs. The blind B1 task `TASK-20261025-0cc64e` must use an exact independent review-adversarial xhigh session, derive from the frozen trial plan and standard supervisor, list every source read, never read any listed `blind_from` file, and publish a worked sealed report/attestation with a completed release.
- [ ] In a distinct admitted independent session after B1 release, task `TASK-20261025-cbcdc5` must challenge O1/O2/O3 on the hash-bound ten-file source/fixture snapshot, run only disposable no-science supervisor controls, keep the historical run unchanged, state one verdict per joint and preserve any BREAKS reproducer. It must not read B1 or prior failed review outputs before sealing.
- [ ] Archive both exact review outputs through `TASK-20261025-ab627a` and verify the receipt. The pinned `check_review_independence.py --no-addenda --plan <new-plan> --reports <B1-attestation> <O1-O3-attestation> --expected-plan-sha256 <frozen-digest>` must PASS on truthful read lists; independently verify exact sessions, seal/release order and substantive controls. A later Coordinator decision may accept only the engineering source scope if all gates hold.

These conditions are sufficient only to make an engineering acceptance decision reviewable. Fresh scientific protocol preapproval, a real run and complete cost measurements remain separate.

## Next discriminating step

- **Action or proof obligation:** Archive the zero-Ready successor packet, then obtain and admit an exact fresh B1 independent session without changing the plan or old reports.
- **Inputs and controls:** Frozen trial plan and standard supervisor for B1; complete `blind_from` list includes candidate bytes, producer report, prior review and current negative decision. O1/O2/O3 reviewer later tests missing/empty, digest, raw-member, historical-invalid and canned-certificate known-false objects. Both attestations list real reads.
- **Execution limits and stop condition:** One review task at a time under batch max_concurrent 1; zero scientific solver trials. Stop on identity mismatch, forbidden read, failed control, missing release, archive mismatch or checker failure. Do not rewrite frozen artifacts to force PASS.
- **Outcomes and next actions:** Valid B1 plus full report and PASS permit Coordinator engineering source assessment. BREAKS with reproducer prompts source correction under fresh IDs. Another procedure failure prompts a new scoped plan/correction. Infrastructure failure leaves reviewer admission blocked without source inference.
- **Recheck trigger:** Publication of new split packet, each session admission, each reviewer release, snapshot verification or checker result.

A planned review is not a completed finding. The active goal and scientific statuses remain unchanged.

## Resolution and history

Unresolved as of 2026-10-25. The original outputs and failed checker result are retained immutably; `DEC-20261025-5b84e8` freezes the new procedure. Completing this record or its PR does not accept the source.
