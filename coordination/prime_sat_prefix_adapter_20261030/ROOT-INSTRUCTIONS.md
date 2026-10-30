# Prospective adapter admission — root execution steps

Four fresh tasks reuse BATCH-a99822 and its serial capacity. All prior tasks stay unchanged; prior TASK-20261029-5a7c65 is already completed. No EXP record, new lane, H/EV/KN or goal transition is created. Coordinator prepared only this directory. No software suite has run.

1. Review and validate the exact staged package:

```text
/home/ec2-user/prime-sat-research-venv/bin/python -B coordination/prime_sat_prefix_adapter_20261030/apply_queue.py --check
```

Apply only as root after the check succeeds; this copies four fresh handoffs and appends four tasks, preserving every old task:

```text
/home/ec2-user/prime-sat-research-venv/bin/python -B coordination/prime_sat_prefix_adapter_20261030/apply_queue.py --apply
```

Commit/push all admission files and canonical handoffs/queue before implementation or execution. No future result/DEC is prefilled.

2. Read native Ready, then claim the producer using actual native ownership:

```text
/home/ec2-user/prime-sat-research-venv/bin/python tools/research_dispatch.py coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/dispatch_queue.json --ready-only --claims refs
/home/ec2-user/prime-sat-research-venv/bin/python tools/goal_lanes.py claim coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/dispatch_queue.json TASK-20261030-08faf8 --as executor-prime-prefix --session prime-prefix-producer --ttl-minutes 60 --publish
```

Root owns the four producer paths under research/prime_sat_prefix_adapter_20261030. Implement actual generic and legacy-wrapper callables; preserve frozen source bytes. Run exactly the contract suite with PYTHONDONTWRITEBYTECODE=1:

```text
/home/ec2-user/prime-sat-research-venv/bin/python -B research/prime_sat_prefix_adapter_20261030/test_adapter.py --receipt research/prime_sat_prefix_adapter_20261030/producer-results.json
```

This captures direct old verify_search compatibility internally. Never call old test_encoding/controls/verify/solve/refute/census/reference or construct a SAT solver. Retain every actual attempt and hash. Publish before truthful release:

```text
/home/ec2-user/prime-sat-research-venv/bin/python tools/goal_lanes.py release coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/dispatch_queue.json TASK-20261030-08faf8 --as executor-prime-prefix --expected-epoch <ACTUAL_EPOCH> --outcome completed --publish
```

Use failed rather than completed if the actual completion gate fails. No automatic replacement/retry of a frozen target.

3. Read Ready, claim snapshot TASK-20261030-6ad2ee as coordinator-prime-prefix/session prime-prefix-snapshot/TTL60. Write producer-snapshot-receipt.json from actual source/receipt outcomes. Commit/push its exact five-path union from software-contract.json, bind native content_at_commit using actual commit, first parent and logical hashes, validate the binding, publish and release. No placeholder archive hash counts as completion.

4. Read Ready, claim TASK-20261030-8e7037 as reviewer-prime-prefix/session prime-prefix-independent/TTL60. Spawn fresh prefix_adapter_reviewer with requested gpt-6.1-sol/xhigh and fork_turns none under inference-amendment.yaml. Give reviewer-brief.md, fixed contract, exact whitelist and actual runtime/claim metadata. Do not send producer new tests/results/README or future review outcomes. Reviewer writes four declared files and runs only its specified command.

5. After actual seal, publish four review artifacts and run the unchanged native gate:

```text
/home/ec2-user/prime-sat-research-venv/bin/python tools/check_review_independence.py --no-addenda --plan coordination/prime_sat_prefix_adapter_20261030/review-plan.yaml --reports research/prime_sat_prefix_adapter_20261030/TASK-20261030-8e7037/attestation.yaml
```

Retain every actual failure and exact receipt. Release truthfully, read Ready, then claim ledger TASK-20261030-2e1cb1 as coordinator-prime-prefix/session prime-prefix-ledger/TTL60. Coordinator may synthesize DEC-20261030-676356 and report sources only after the actual review/gate and claim. Root renders/inspects PDF, fills actual manifest custody and native checkpoint facts, and binds/publishes the exact ten-path ledger union. Keep artifacts over the native threshold in the native store, preserving logical content identities. Final outcomes and model provenance must be observed, not assumed.

The graph/report scope is already reserved in the handoff; no extra report-scope amendment is needed. Keep the report compact and preserve all historical outcomes. The prior native checkpoint and readback passed at facd03aaf7; new transport/publication outcomes still require actual receipts. A later solver experiment or arbitrary-trail proof interface needs its own admission.
