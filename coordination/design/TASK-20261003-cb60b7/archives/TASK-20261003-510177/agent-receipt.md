# Agent receipt — EXP-CERTBIN-1bfef5 Stages 0–1 (retry)

- **branch**: `cursor/run-certbin-1bfef5-stages01-ed0c`
- **tip SHA**: `0057dbebeb189c279c1fe655cb2738b05da7b06b`
- **snapshot archive**: TASK-20261003-510177 @ commit `62d229ed2c4214807dfaae7f0ea72caf407404bc`
- **cloud agent**: bc-66d00895-a4c2-5040-b939-79f0ca9b740b (retry after bc-935698de abort)
- **PR**: not created (403 standing instruction)

## Runs

| RUN id | Stage | Outcome | Notes |
|--------|-------|---------|-------|
| RUN-CERTBIN-ae7b9c | 0 | completed_valid / output_validated | Propositions/pin freeze |
| RUN-CERTBIN-d4f1ee | 1 | O-IMPEDIMENT / output_validated | IMP-ARM-A-BASIS-SWAP; instrument gates passed; not negative evidence |

Run IDs were minted at unlock in frozen `trial-plan-v1.json` and executed on the cbae tip before this retry. This session did **not** rewrite those completed run records; it completed flat→`manifest_v2.yaml` + `tools/run_supersession_registry.yaml` (`superseded_id_null: true`) and the snapshot archive.

## Schema completion

- `experiments/EXP-CERTBIN-1bfef5/runs/RUN-CERTBIN-ae7b9c/manifest_v2.yaml`
- `experiments/EXP-CERTBIN-1bfef5/runs/RUN-CERTBIN-d4f1ee/manifest_v2.yaml`
- Registry entries with `superseded_id_null: true`

## next_action

`/review-evidence` for EXP-CERTBIN-1bfef5 Stages 0–1 (RUN-CERTBIN-ae7b9c, RUN-CERTBIN-d4f1ee).

No Bedrock/AUXIN.
