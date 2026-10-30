# Cost-bridge admission and execution boundary

Finish and publish the current main merge first. This package changes no canonical queue or claim itself. Preserve all prior artifacts.

1. Copy the four staged handoffs to ledger/handoffs/. Apply queue-append.json additively to the existing BATCH-a99822 queue. Reconcile only TASK-20261029-5148ef to completed from actual release578ee282f2 and verified archivea39158715d; preserve every other field and both old review statuses. Never redispatch it.
2. Validate the merged queue using native research_dispatch with GitRepositoryVerifier. Publish this package, new canonical handoffs and queue before claiming the producer. Existing lane and max_concurrent1 remain unchanged.
3. Read native Ready with --claims refs. Claim TASK-20261029-2e3655; root owns only its seven declared research outputs. Implement the exact reference contract and symbolic cost bridge, then run only the fixed correctness suite. No comparison/sweep/benchmark or old run replay is authorized. Publish exact source and actual software receipt before release.
4. Claim and complete snapshot TASK-20261029-dcc96c, with actual commit, first parent and all producer/receipt hashes verified. Only then claim reviewer TASK-20261029-58d7a7.
5. Spawn one fresh task_name costbridge_blind_reviewer, modelgpt-6.1-sol, effortxhigh, fork_turns none, sending blind-brief.md and exact read/write scope only. The brief supplies metadata conventions. Never disclose new producer proof/status/results or parent research discussion. The reviewer must first seal precode-derivation.md with actual clock/hash before reading any code/test source, then audit only the specified files and retain both phase attestations. No separate pre-code archival/timestamp authentication is claimed; no software or scientific execution occurs in the reviewer task.
6. Preserve actual sealed review/attestation, run the unchanged native checker with --no-addenda and this review-plan.yaml against that sole actual attestation, then release truthfully. Failed gates remain failed; this package grants no automatic replacement or checker repair.
7. Claim TASK-20261029-bd67d5 only after actual review completion/native readiness. Coordinator writes DEC-20261029-266f95 and five report/manifest files; root renders/inspects PDF. Native ledger archive binds six direct artifacts plus three review-source artifacts. No status or goal promotion is preapproved.

Readiness command:
`python3 tools/research_dispatch.py coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/dispatch_queue.json --ready-only --claims refs`

Actual reviewer check:
`python3 tools/check_review_independence.py --no-addenda --plan coordination/prime_sat_costbridge_20261029/review-plan.yaml --reports research/prime_sat_costbridge_20261029/TASK-20261029-58d7a7/attestation.yaml`

The eventual scientific solver comparison is not admitted here. It needs a new EXP, fixed output/cost contract, frozen implementation and protocol, native approvable preapproval, published approval and ready state. No repeated PNEXT trial and no closure claim are authorized.
