# Output-contract review procedure decision

**Decision:** [DEC-20261025-5b84e8](../../../../ledger/decisions/DEC-20261025-5b84e8.yaml) withholds engineering source acceptance and freezes a fresh B1/O1–O3 split review. This is an evidence/procedure review of the no-science prospective prime63 m=2 output bridge. Evidence strength for the first round's *review composition* is insufficient; the claim tier is engineering source behavior, with no ECDLP cost or performance claim.

## Observation

The [first plan](../../../../coordination/review/icperf-prime63-m2-output-contract-v2-20261025/review-plan.yaml) assigned blind derivation and full source review to one Validator. Its derivation was sealed at commit `932e5d00147cc206a5a15144f5001d928c3d5259` before candidate reads. Its [report](../../../../coordination/review/icperf-prime63-m2-output-contract-v2-20261025/TASK-20261025-b2e2cd/report.md) reports O1, O2 and O3 holding in tested canned engineering cases. The [attestation](../../../../coordination/review/icperf-prime63-m2-output-contract-v2-20261025/TASK-20261025-b2e2cd/attestation.yaml) records two pinned checker failures: the plan lacks a rationale for its nonempty broad lift, and its final source list contains six protected paths read after the blind seal. [TASK-20261025-6d007d](../../../../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-ac3c38/archives/TASK-20261025-6d007d/snapshot-receipt.json) binds all three outputs.

## Comparison

The first report describes two `output_validated` canned terminals, four `invalid_output` controls and further single-field mutations. These are producer/reviewer engineering observations under disposable supervisor roots. The historical RUN-ICPERF-eb0d88 remains `invalid_output` and is outside any prospective repair. The diagram marks the two failed *procedure* gates separately from the tested fixture statuses. No scientific measurement, matched IC baseline or rho comparison is present.

## Inference

The temporal seal may show that the first derivation was written before source reads. The pinned checker judges the final per-task read list and the frozen plan, so the first round cannot provide accepted independent composition. An addendum cannot remove the frozen broad lift's missing-rationale failure. The [new plan](../../../../coordination/review/icperf-prime63-m2-output-contract-v2-remedy-20261025/review-plan.yaml) instead assigns B1 to a blind-only Reviewer and O1–O3 to a different full-source Reviewer, with no broad lift. Both tasks remain blocked until exact independent session admissions.

## Limitation

No source acceptance, fresh scientific experiment approval, certificate, solver result, IC rank, end-to-end cost or speedup follows. The earlier positive findings are preserved as bounded diagnostics with failed review procedure. A future mechanical PASS still needs truthful session/read provenance, verified releases, archive custody and substantive Coordinator assessment.

## Next actions

1. Archive this decision, [problem](../../../../problems/icperf-output-contract-review-procedure-mismatch.md), split plan and zero-Ready queue with content-first receipt.
2. Admit a fresh exact independent xhigh B1 session, then a distinct O1–O3 session after B1 release; preserve honest read lists and all controls.
3. Snapshot both outputs, run the pinned independence checker against the exact plan digest and decide only the engineering source scope afterward.

## Canonical graph check

No canonical ECDLP performance or factor-base graph is changed by this procedure decision. I checked the affected experiment report directory and `knowledge/frontiers/ecdlp/index-calculus/` contents. The latter holds knowledge records and no canonical graph source for this procedural gate; earlier experiment review visuals describe scientific/run outcomes and receive no new measured value here. This decision creates a new procedure diagram and PDF, with no scientific quantitative plot because no scientific quantity was measured here.
