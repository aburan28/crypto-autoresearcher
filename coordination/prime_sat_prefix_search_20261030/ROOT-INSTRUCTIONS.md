# Initial PSEARCH design/implementation admission

This is the first staged packet. Only root applies it, publishes, claims or executes. The implementation runs first under the existing serial lane; design task depends on implementation. No scientific execution is authorized. No second lane, new hypothesis status, final scientific DEC or acceptance is prefilled.

```text
/home/ec2-user/prime-sat-research-venv/bin/python -B coordination/prime_sat_prefix_search_20261030/apply_queue.py --check
/home/ec2-user/prime-sat-research-venv/bin/python -B coordination/prime_sat_prefix_search_20261030/apply_queue.py --apply
```

Commit/push this whole coordination directory, the three newly copied handoffs and canonical queue. Then native Ready and implementation claim:

```text
/home/ec2-user/prime-sat-research-venv/bin/python tools/research_dispatch.py coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/dispatch_queue.json --ready-only --claims refs
/home/ec2-user/prime-sat-research-venv/bin/python tools/goal_lanes.py claim coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/dispatch_queue.json TASK-20261030-9e0c3d --as executor-prime-search --session prime-prefix-search-implementation --ttl-minutes 60 --publish
```

After actual claim, root writes the six source-api.md files and may execute only its four declared synthetic F5 fixture families plus deterministic callback/checker controls. At most four suite invocations, preserve all failures and finite pre-snapshot corrections. Suggested executable contract:

```text
PYTHONDONTWRITEBYTECODE=1 /home/ec2-user/prime-sat-research-venv/bin/python -B research/prime_sat_prefix_search_20261030/test_engine.py --receipt research/prime_sat_prefix_search_20261030/software-integrity.json
```

No p17/p97 EC cell is run in implementation. Root publishes actual source/receipt, releases implementation truthfully using actual epoch, then Ready/claims design TASK-20261030-cb8aee. Coordinator completes the protocol/export/review/admission helpers on the real source and appends the later native experiment executor/raw-snapshot/reviewer/ledger chain. Current config is draft, not permission to run.

Design archive TASK-20261030-08211e must bind only final source plus final approved/frozen design bytes after exact native `experiment_preapproval.py` returns `approvable:true` and root publishes approval. Do not complete it on a mutable draft. Scientific execution additionally requires the actual ordinary ready selector, live ownership and unchanged checkpoint gate. No unlinted runbook is declared; implementation route remains explicit unless a real runbook/card later lint successfully.

Current root baseline is main2165804af6c622d7b71d8893655b28fd93c1996b. All previous task records, immutable sources and statuses stay unchanged. Full portfolio command refused sparse checkout; no override. Requested inference substitution and unverified runtime identity are prospective in inference-amendment.yaml. No independent reviewer has been launched by this packet.
