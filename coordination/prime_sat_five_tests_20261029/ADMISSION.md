# Five-lead exact-test admission

This lane is a finite Stage1 implementation/test package, not completion of the original five performance hypotheses. `design-contract.json` preserves all five questions and each unresolved obligation. No scientific trial has been run by the design Coordinator.

IDs: H-PFIVE-6510c2 / EXP-PFIVE-3ca920 / approval DEC-20261029-0b7870. Executor TASK-20261029-1cb9f8; raw snapshot TASK-20261029-e726a2; independent reviewer TASK-20261029-bc29bd; review/decision archive TASK-20261029-797dd2. One immutable planned run is RUN-PFIVE-c8c614. The four extra allocated run tokens have no workload and must not be treated as four runs.

GOAL-PFDR-fd09e0 already had two open lanes, both materialized from committed bytes. Root authorized max_concurrent 3 solely to admit the third lane BATCH-449a28 without silently closing the other two. This lane's queue has max_concurrent 1 and its actual local scientific execution is serial. No capacity or idle-state inference was made from sparse absence.

Python interpreter: `/home/ec2-user/prime-sat-research-venv/bin/python`.

After all scientific source/config bytes are final, root must first archive the implementation source. The draft command refuses sources absent from or different at HEAD, so the protocol's instrument commit really contains the code it names. Then:

```sh
/home/ec2-user/prime-sat-research-venv/bin/python coordination/prime_sat_five_tests_20261029/prepare_admission.py draft
/home/ec2-user/prime-sat-research-venv/bin/python tools/experiment_protocol.py validate experiments/EXP-PFIVE-3ca920/protocol.json
/home/ec2-user/prime-sat-research-venv/bin/python tools/experiment_protocol.py freeze experiments/EXP-PFIVE-3ca920/protocol.json --commit auto --filed-before-affected-data
/home/ec2-user/prime-sat-research-venv/bin/python coordination/prime_sat_five_tests_20261029/prepare_admission.py bind-frozen
```

Root must archive and push those draft bytes, all bound source/config bytes, goal and lane record on `origin/codex/prime-sat-five-tests-20261029`. The current draft must be at that remote ref. The protocol lists the fixed 7200-second machine watchdog as an explicitly unmeasured planning estimate, not a fabricated timed pilot. No scientific timing preflight occurred.

Then:

```sh
/home/ec2-user/prime-sat-research-venv/bin/python coordination/prime_sat_five_tests_20261029/prepare_admission.py preview
/home/ec2-user/prime-sat-research-venv/bin/python tools/experiment_preapproval.py --packet coordination/prime_sat_five_tests_20261029/preapproval-packet.json
```

Only after `approvable: true`, root can invoke `prepare_admission.py promote`. It reruns the native probe and refuses if any blocker remains; copies the exact preview specification/trial-plan/queue/handoff bytes; and writes the Coordinator approval decision. Root must archive and publish that exact approval package. The ordinary selector `tools/newest_experiments.py --experiment EXP-PFIVE-3ca920 --json` must independently report `execution_state: ready`, followed by live lane/task claim and checkpoint gate, before the run launches. A preapproval result does not replace any of these gates.

The native trial uses driver `--config experiments/EXP-PFIVE-3ca920/config.json --output {run_dir}` and checks `--verify {run_dir}/raw-result.json`. Required driver artifacts are `manifest.yaml` and `raw-result.json`; supervisor output coverage includes launch, execution receipt, command, environment and all stdout/stderr logs. Additional reports/export/figures are required before reporting completion and must have an explicit archive owner.

The queue reserves an independent reviewer and review archive before any claim promotion. No mechanical runbook is represented as linted; new implementation runs use the explicit `executor-implementation` route. Full-ledger KPI/validation tools refuse this sparse checkout; no sparse override is used. That limitation is not a scientific result.
