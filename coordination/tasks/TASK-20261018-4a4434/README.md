# Prospective custody repair for four approved ECDLP plans

The only edits to existing records append eight exact supervisor artifact paths to each of four original executor tasks' `artifact_paths` in `queue.json`. Frozen specifications, trial plans, implementations, task IDs, previous decisions, archive blocks and previous claims/releases are unchanged. The prior queue bytes and before/after hashes are retained under `prior/` and `amendment.json`.

The exact `tools/experiment_execution.py:GENERATED` list is:

- `launch.json`
- `execution-receipt.json`
- `command.txt`
- `environment.json`
- `stdout.log`
- `stderr.log`
- `check.stdout.log`
- `check.stderr.log`

The original `manifest.yaml` and `raw-result.json` remain declared. Exit codes belong to the generated execution receipt; the current supervisor declares no separate `exit-status` artifact. Existing snapshot tasks already read the entire experiment directory, and the native archive validator automatically includes every producer artifact. No old archive record needed an edit.

The four native dispatchers exit 0 and report all eleven gates true, including complete archive coverage. They offer the original unclaimed executor tasks. Native supervisor `status` exits 0 and reports the original trials planned. These read-only checks do not establish committed/published readiness or an authorized live claim.

## Validation failures and the actual archive gate

Full checkout was materialized; `git fetch origin main && git merge origin/main` reported already up to date. The required full `validate_ledger.py` preflight reports 163 validation errors beyond 1210 grandfathered errors. Its complete output is retained in `gates/ledger-post.*`; none of the errors may be hidden by a sparse diagnostic override or baseline expansion. The initial preparation treated that global failure as a blanket publication block. That interpretation is corrected here: coordinate SKILL step2 requires the validator and hygiene checks to be rerun, but does not explicitly require unrelated historical errors to be repaired before an administrative archive. `gates/scoped-delta-check.json` records zero errors on the modified paths. No sparse override, baseline expansion or validator suppression is used. The existing scientific approvals are unchanged.

The native `research_dispatch.GitRepositoryVerifier.verify_archive` gate requires a reachable commit, its actual first parent, exactly the declared changed paths, matching SHA-256 content for each file, and the archive/record IDs in the commit message. It does not inspect whole-ledger validation status. The isolated administrative archive must pass that gate; its receipt does not claim global validation green. Publication and a fresh executor claim remain separate actions owned by the root session.

`experiment_preapproval.py --experiment EXP-ECDLP-bfbe6f` refuses a new approval of an already approved canonical contract. This repair requests no new scientific approval and changes no specification byte; the existing committed command-based route is retained. No runbook migration or scientific reapproval is fabricated.

Coordinator policy resolution returned `anthropic:claude-opus-5-5`, effort high, with model ID unverified. No inference call to that provider was made or claimed. The actual preparation role is the parent-dispatched Coordinator subagent in the current Codex runtime. Conductor was unavailable (exit127, command not found).

## Native launch handoff after a lawful published repair

All commands run from crypto-autoresearcher. Replace `ACTUAL_EPOCH` with the new claim's returned epoch. Do not use `--force`, bypass admission, reuse a failed claim, overwrite old releases, or declare a completion before the original checker's retained artifacts exist.

| Experiment | Original executor task | Original run ID |
|---|---|---|
| EXP-ECDLP-bfbe6f | TASK-20261012-e25b3e | RUN-ECDLP-8f5190 |
| EXP-ECDLP-5f4f14 | TASK-20261012-d5e2f4 | RUN-ECDLP-42444c |
| EXP-ECDLP-3c166b | TASK-20261012-5cb5e4 | RUN-ECDLP-4a3ca0 |
| EXP-ECDLP-20ac31 | TASK-20261012-cf6c84 | RUN-ECDLP-08e0d9 |

For each matching `EXP` and `TASK`:

```sh
python3 tools/research_dispatch.py experiments/EXP/queue.json --ready-only --claims refs
python3 tools/goal_lanes.py claim experiments/EXP/queue.json TASK \
  --as executor-ideas-20261018 --ttl-minutes 10 --publish
# Fetch published origin refs if the claim publisher did not refresh them.
python3 tools/experiment_execution.py run \
  --plan experiments/EXP/trial-plan.json \
  --owner executor-ideas-20261018 --epoch ACTUAL_EPOCH
python3 tools/goal_lanes.py release experiments/EXP/queue.json TASK \
  --as executor-ideas-20261018 --outcome ACTUAL_OUTCOME \
  --note ACTUAL_OBSERVATION --publish
```

The supervisor independently requires unchanged committed inputs, a current admitted task, a live owner/epoch and a claim visible in origin tracking refs. The source checker remains the plan's checker. A failed control is retained scientific output with its own validity; an admission or infrastructure failure is not a mathematical negative.
