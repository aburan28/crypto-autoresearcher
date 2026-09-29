# EXP-ECDLP-abf981 -- finite-yaml-lock-v1 integration (source-v2)

Status: engineering integration only. No scientific execution occurred under
this task (TASK-20260908-1a8f4c, authorized by DEC-20260908-195f0f). Zero
run directories were created under `experiments/EXP-ECDLP-abf981/runs/`.

## What changed and what did not

- `experiments/EXP-ECDLP-abf981/source/run_model_comparison.py` is
  **unmodified**. Its `main()` still refuses a scientific `--cell`/
  `--run-dir` invocation with `locked_runner_integration_unresolved` and
  exit code 2 (line ~1124-1128 at the version bound by
  `partial-disposition.json.partial_artifacts[0].sha256`). Only
  `--mechanical-check` (zero scientific runs) executes.
- `experiments/EXP-ECDLP-abf981/specification.yaml` is **unmodified**; its
  two `run_bindings` reservations (`p11` -> `RUN-ECDLP-56d8aa`, `p23` ->
  `RUN-ECDLP-591253`) are preserved exactly.
- New: `harness/finite_yaml_locked_v1.py` -- the shared adapter (also used by
  EXP-ECDLP-2cb7f8) implementing `validate_lock`/`execute_locked` against a
  NEW `schemas/finite-yaml-lock-v1.schema.json`.
- New: `experiments/EXP-ECDLP-abf981/source-v2/locked_entry.py` -- an
  additive entry wrapper that imports the archived kernel's `finite_payload`
  and `scientific_artifact_data` by exact file path, and defines
  `run_locked_models_cell` as the one future admitted call site. This
  function is dead code with respect to this task: nothing here or in
  `tests/test_finite_yaml_locked_v1.py` calls it.
- New: `experiments/EXP-ECDLP-abf981/source-v2/planned-execution.json` --
  a prospective (non-`execution_plan`, non-authorizing) description of how a
  real lock would eventually bind to the two frozen reservations above.

## Why the old high-level runner is not reused

`src/crypto_autoresearcher/runner.py`'s `run_experiment` (and its supporting
`_load_approval_context`/`_post_run_checks`) require `specification.json`,
`contract.md`, and the legacy `execution-approval.schema.json`/
`runner-receipt.schema.json` envelope, whose `run_id`/`experiment_id`
patterns are numeric-only (`RUN-[A-Z0-9-]+-[0-9]{3,}`,
`EXP-[A-Z0-9-]+-[0-9]{3,}`) -- they reject `RUN-ECDLP-56d8aa` and
`RUN-ECDLP-591253` outright. This is exactly
DEC-20260908-b423e1's `RUNNER-INTEGRATION-CONTRACT` and
`RUNNER-IDENTIFIER-COMPATIBILITY` findings. `harness/finite_yaml_locked_v1.py`
does not call `run_experiment`; it reuses only the low-level primitives named
in DEC-20260908-195f0f's `engineering_successor.integration` (`_run_child`,
`_locked_resource_policy`, `_protocol_path`, `_sha256`, `_ProtocolFile`,
`_protocol_files_unchanged`, `_tree_clean_except`) after reading their actual
signatures in `src/crypto_autoresearcher/runner.py`.

`harness/runner.py`'s `write_run`/`run_wrapped` are also not reused: that
module has no LOCKED interface, and its `_inference_block` fallback
(`requested_policy: "executor-terra"`) is a different, harness-wide default
provenance label -- using it here would misattribute this task's actual
`executor-implementation` session. `finite_yaml_locked_v1.py` writes its own
`native_launch_receipt`/`launch_authority` fields from the caller-supplied,
externally verified lock and claim instead.

## Reserved identifiers -- unchanged

| cell | run_id | run_directory |
| --- | --- | --- |
| p11 | `RUN-ECDLP-56d8aa` | `experiments/EXP-ECDLP-abf981/runs/RUN-ECDLP-56d8aa` |
| p23 | `RUN-ECDLP-591253` | `experiments/EXP-ECDLP-abf981/runs/RUN-ECDLP-591253` |

Neither directory exists after this task. `harness/finite_yaml_locked_v1.py`'s
`validate_lock` refuses (no-clobber) if either ever does.

## Companion output filenames -- prospective only

DEC-20260908-195f0f's `additional_future_output_contract` prospectively adds
`command.txt`, `environment.json`, `stdout.log`, `stderr.log`, and
`raw-result.json` to a FUTURE real run's output allowlist, alongside the
seven names `scientific_artifact_data` already owns (`raw-results.json`,
`map-certificates.json`, `relation-certificates.json`,
`polynomial-systems.json`, `control-results.json`, `costs.json`,
`execution-report.md`) plus `manifest.yaml`. This task creates none of them in
a real run directory; `tests/test_finite_yaml_locked_v1.py` exercises the
adapter's own manifest/command/environment/stdout/stderr/raw-result writing
only inside disposable synthetic fixture directories under
`coordination/pending-ideas/BATCH-855d5d/integration/tasks/
TASK-20260908-1a8f4c/scratch/`.

## Unresolved before any real run

1. A Coordinator-published `expected_sha256` trust anchor for an actual lock
   instance (this task fabricates none; every lock used in testing is a
   synthetic fixture with a locally computed hash the test itself checks
   against, never presented as a real authorization).
2. The companion-file allowlist amendment referenced above.
3. Independent operational QA (TASK-20260908-2d3b01, per
   DEC-20260908-195f0f `successor_ids`).
4. Separate scientific-run authorization; `scientific_execution_authorized`
   is `false` in every lock this adapter version accepts, by schema
   (`const: false`) and by a direct code check in `validate_lock`.
