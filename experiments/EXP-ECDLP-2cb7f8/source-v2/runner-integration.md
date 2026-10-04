# EXP-ECDLP-2cb7f8 -- finite-yaml-lock-v1 integration (source-v2)

Status: engineering integration only. No scientific execution occurred under
this task (TASK-20260908-1a8f4c, authorized by DEC-20260908-195f0f). Zero
run directories were created under `experiments/EXP-ECDLP-2cb7f8/runs/`.

## What changed and what did not

- `experiments/EXP-ECDLP-2cb7f8/{run.py,group_oracle.py,incidence.py,
  presentation_inventory.py}` are **unmodified**. `run.py`'s `main()` still
  refuses with `UNRESOLVED_CANONICAL_RUNNER_INTERFACE` (exit code 2, via
  `parser.exit(2, ...)`) for every invocation; it creates no run directory
  and performs no scientific computation. `run_case`'s own six-gate check
  (`canonical_lock_verified`, `scientific_authority_verified`,
  `claim_verified`, `source_snapshot_verified`, `semantic_gate_verified`,
  `memory_limit_enforced`, all required `True` in `manifest_context`) and its
  `'bedrock' in encoded_context` refusal are untouched -- this wrapper adds
  none of `run_case`'s own gates and removes none of them.
- `experiments/EXP-ECDLP-2cb7f8/specification.yaml` is **unmodified**; its
  five reserved `run_id`/`run_directory` bindings are preserved exactly, as
  is `run.py`'s own `BINDINGS` tuple (`(case_id, p, curve_constant, run_id)`
  quadruples) that `config_checked` validates against.
- New: `experiments/EXP-ECDLP-2cb7f8/source-v2/locked_entry.py` -- defines
  `run_locked_case` (dead code w.r.t. this task; imports the archived
  `run_case` by exact file path and calls nothing else) and
  `validate_recovery_case_inventory`/`validate_recovery_case_arms`, which
  implement DEC-20260908-195f0f's `metric_interpretation.required_checks`
  synthetic metadata-only test: reordered/deleted case IDs, duplicate IDs,
  and one-case-different B/I arm inventories are all rejected. No scientific
  field or section is evaluated by either function.
- New: `experiments/EXP-ECDLP-2cb7f8/source-v2/planned-execution.json` -- a
  prospective description of how a real lock would eventually bind to the
  five frozen reservations, including which of `run_case`'s twelve frozen
  `ARTIFACT_NAMES` are preserved.

## Recovery-case inventory (DEC-20260908-195f0f `metric_interpretation`)

The twelve frozen case IDs (`c2_nonzero_c3_nonzero`, `c2_nonzero_c3_zero`,
`c2_zero_h_degree_2`, `c2_zero_h_degree_1`, `c2_zero_h_degree_0`,
`root_y_two_nonzero`, `root_y_zero`, `root_y_absent`, `residual_constant`,
`residual_nonconstant`, `O_present`, `O_absent`) are reproduced verbatim as
`locked_entry.RECOVERY_CASE_IDS`, in the same order as the decision. This is
"a protocol declaration obtained by enumerating this written list, not an
experimentally measured quantity" (partial-disposition.json
`inventory_size_semantics`); `tests/test_finite_yaml_locked_v1.py` exercises
`validate_recovery_case_inventory`/`validate_recovery_case_arms` only against
this static list and deliberately mutated copies of it -- never against any
B/I comparison computed from an actual scientific run, since none occurred.

## Why the old high-level runner is not reused

Same reasoning as `experiments/EXP-ECDLP-abf981/source-v2/runner-integration.md`:
`src/crypto_autoresearcher/runner.py`'s `run_experiment` requires
`specification.json`/`contract.md` and the legacy numeric-only
`RUN-[A-Z0-9-]+-[0-9]{3,}` identifier pattern, which rejects all five of
this experiment's reserved run IDs (`RUN-ECDLP-3c6277`, `RUN-ECDLP-413b2a`,
`RUN-ECDLP-b0a390`, `RUN-ECDLP-d7d29d`, `RUN-ECDLP-e2e77c`) --
DEC-20260908-b423e1's `RUNNER-IDENTIFIER-COMPATIBILITY` finding.
`harness/finite_yaml_locked_v1.py` reuses only the named low-level
primitives from that module, not `run_experiment` itself.

## Reserved identifiers -- unchanged

| case_id | p | curve_constant | run_id |
| --- | --- | --- | --- |
| E5 | 5 | 1 | `RUN-ECDLP-3c6277` |
| E7 | 7 | 1 | `RUN-ECDLP-413b2a` |
| E11 | 11 | 1 | `RUN-ECDLP-b0a390` |
| E17 | 17 | 1 | `RUN-ECDLP-d7d29d` |
| N0-Eprime5 | 5 | 2 | `RUN-ECDLP-e2e77c` |

None of the five `experiments/EXP-ECDLP-2cb7f8/runs/RUN-ECDLP-*` directories
exist after this task.

## Companion output filenames -- prospective only, and no collision

`run.py`'s twelve frozen `ARTIFACT_NAMES` already include `stdout.txt` and
`stderr.txt`. The adapter's own prospective companion names use the
DISTINCT `stdout.log`/`stderr.log` spelling precisely so a future real run
can carry both the instrument's own frozen text logs and the adapter's
companion logs without either name colliding or being silently replaced,
per DEC-20260908-195f0f's `additional_future_output_contract.preservation`.
This task creates neither set of files in any real run directory.

## Unresolved before any real run

1. A Coordinator-published `expected_sha256` trust anchor for an actual lock
   instance per case (none fabricated by this task).
2. The companion-file allowlist amendment.
3. Independent operational QA (TASK-20260908-2d3b01).
4. A real, independently-verifiable wiring for `run_case`'s six required
   `manifest_context` gates -- this wrapper does not invent evidence for
   them; `run_locked_case` passes through whatever a future caller supplies,
   and `run_case` itself still refuses if any gate is not exactly `True`.
5. Separate scientific-run authorization; `scientific_execution_authorized`
   is `false` in every lock this adapter version accepts.
