# Experiment reserve observation

Source: `759fa5693d9f7ed77ef7e0c7f3520d0feb91f5a3`. This is an administrative inventory and rank proposal. It approves no protocol and claims no research result.

**Current supply: 3 approved experiments awaiting implementation, 7 additional designs awaiting readiness review, and 0 confirmed scientific tasks ready for dispatch.** The scheduling objective is a reserve of at least 8 independently justified, protocol-ready experiments, with 2 active critical experiments by default and at most 3. The objective has not yet been met.

The repository has 413 open ECC ideas. Generating more proposals is lower priority than repairing integrity and completing existing experiment contracts. Counts from raw `status` fields are insufficient: the three approvals below are additive records while their immutable original specifications retain earlier metadata.

| Rank | Experiment | Readiness | Next gate |
|---:|---|---|---|
| 1 | `EXP-ECDLP-1b1b99` — Charged CM auxiliary maps | approved_implementation_pending | The existing implementation queue selects TASK-20260906-2f2a56 first. Complete reuse assessment, implementation, independent implementation review and launch lock. |
| 2 | `EXP-ECDLP-910fcd` — Tate-character and decoder costs | approved_implementation_pending | Implementation TASK-20260906-681152 depends on TASK-20260906-ebfb30; independent implementation review and launch lock follow. |
| 3 | `EXP-ECDLP-651b94` — Rho partition and spectral controls | approved_implementation_pending | Implementation TASK-20260906-9393c3 depends on TASK-20260906-cb2dfb; independent implementation review and launch lock follow. |
| 4 | `EXP-ECDLP-184fc4` — Coordinate-function DL spectra | design_readiness_review_pending | Complete Coordinator readiness review of definitions, finite-sample thresholds, seeds/cell counts and proof-search map; freeze implementation and review handoffs before approval. |
| 5 | `EXP-ECDLP-0c717c` — Factor-base sumset envelopes | design_readiness_review_pending | Complete Coordinator readiness review, including the subgroup-contained positive control and claimed null normalization; freeze cell and run accounting and handoffs. |
| 6 | `EXP-ECDLP-1e6502` — P-adic digit census | design_readiness_review_pending | Freeze and independently check the p-adic instrument self-checks and spectral definitions; reconcile the planned cell count and all failure branches before approval. |
| 7 | `EXP-ECDLP-2c3d20` — Walk partition and itinerary concentration | design_readiness_review_pending | Complete blocking Stage 0 derivations and partition-library freeze; verify stationary centering, finite-sample controls and reused spectrum interfaces before approval. |
| 8 | `EXP-PFDR-782085` — Exact top-kernel survival panel | design_readiness_review_pending | Resolve portable memory guard, failure capture, and native grading/zero-top-form interface from DEC-20260906-280035; that decision explicitly withholds this panel. |
| 9 | `EXP-PFDR-25057c` — Certified degree ladder | design_readiness_review_pending | Same unresolved definition/runtime prerequisites as EXP-PFDR-782085; verify upper-bound applicability and require a new approval decision before launch. |
| 10 | `EXP-ECDLP-709063` — Memory-constrained BSGS baseline | design_readiness_review_pending | Resolve Stage 0 supersession search and the EXP-ECDLP-4320a7 shared-instance binding; freeze seeds, table representation and enforceable memory guard; review the stochastic baseline criterion before approval. |

The claimed-reference dispatcher passed all gates for `coordination/representation-approval-20260906-421e2f/implementation_queue.json` and selected only `TASK-20260906-2f2a56`. This is a zero-measurement implementation task; its local queue readiness does not override the failing global ledger gate. No claim was acquired and no worker was launched.

The initial ledger check found 50 new errors in 24 existing files. BATCH-0af092 targets 42 source-recoverable errors. The eight `RUN-ECDLP-5cad48-S2` errors remain outside that packet because inspected artifacts lack run-time Git provenance. Archive commit `25fa9abc266b362a40a0ccc0a396a9c25b24f334` is a snapshot, not proof of the execution commit. Missing data must remain missing.

The PFDR panels remain explicitly withheld by DEC-20260906-280035: its preceding audit evaluated zero fixtures. They cannot be counted as approved or ready. Two already-run candidates, EXP-ENDO-c6c7a7 and EXP-ECDLP-a26bde, were excluded to avoid duplicate execution.

Source hashes, frozen estimate disclosures, per-candidate ranking rationale and exact next actions are in `inventory.json`. Time and CPU estimates remain advisory; scientific sample counts and machine limits remain binding. Refill after a committed result/review checkpoint by reranking this reserve; no scheduled background automation is created here.

**Recorded next action — Coordinator:** execute the published BATCH-0af092 repair packet, recheck unresolved 5cad48 provenance and ledger validity, then admit the already-approved representation implementation chain. Independent review and actual launch locks remain prerequisites to measurements.
