# Repair report — TASK-20260909-cb6cc7

Clears the two RUN-ECDLP-e962f6-007 residuals (identity binding + missing
`raw-result.json`) left by repair TASK-20260909-ba7fcb, so that
`tools/validate_ledger.py` and `tools/test_run_supersession.py` report zero
RUN-007 errors on the PR #1058 lane branch (`runs/EXP-ECDLP-e962f6-20260909`).

- Task: `TASK-20260909-cb6cc7` (`ledger/handoffs/TASK-20260909-cb6cc7.yaml`)
- Approving decision: `DEC-20260909-57441e` (verdict d, `approve_scoped_followup_repair`)
- Executor: opencode session `run-e962f6-20260909`, policy `executor-implementation`
- Date: 2026-09-09
- Nature: administrative integrity repair only. No science, no status change,
  no re-scoring, no reruns.

## Method

Two residuals, two fixes:

1. **Missing `raw-result.json`** — data-only fix. Wrote the disclosure file
   `experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-007/raw-result.json`
   containing exactly `{"status":"RAW_RESULT_NOT_CAPTURED","no_rerun":true}`
   (52 bytes, no trailing newline, matching the sibling `raw-result.json`
   convention and the 2026-08-08 pattern). The defective run produced no
   results; the file discloses that rather than fabricating a result.

2. **Null-id identity binding** — requires a validator change (no data-only
   fix exists: the immutable manifest parses normally with `id: null`, and the
   validator's existing recovery paths only handle *unparseable* YAML).
   Implemented the narrow additive path approved by DEC-20260909-57441e:
   - New helper `_null_id_superseded_run_id(path, entry)` in
     `tools/validate_ledger.py`. Fires ONLY when all hold: the entry is a
     registered supersession that explicitly declares
     `superseded_id_null: true` with a non-empty
     `superseded_id_null_provenance`; the file is hash-verified against the
     entry's `superseded_sha256`; the file path matches the entry's
     `superseded_path`; and the run-directory basename equals the registered
     run id. Returns the registered run id; otherwise `None`.
   - `_run_id_of` now calls this helper only on the fall-through where a
     *parseable* manifest yields a null id. Every manifest that is not such a
     registered supersession still returns `None` exactly as before; no
     generalisation of null-id recovery.
   - `load_run_supersessions` carries the two new optional fields through to
     the entry dict (with light well-formedness validation mirroring the
     existing `superseded_id_line` / `superseded_id_extraction` checks).
     Absent on every other entry.

## Rule 15 determination — registry variant used

**Variant used: PRIMARY** — `superseded_id_null: true` +
`superseded_id_null_provenance` appended to the RUN-ECDLP-e962f6-007 registry
entry (the entry was edited, not left untouched).

Rule 15 check (was the RUN-007 entry bound in a completed archive's binding
fields?):

- Searched `coordination/` archives and `ledger/` for the entry's path/sha.
  The RUN-007 entry is **not named** in any completed archive's
  `record_ids`, `artifact_paths`, `write_scope`, or bound commit message.
  No `coordination/` archive or `ledger/` record pins the registry at its
  current sha (`056b8355…`, which contains the RUN-007 entry).
- The only completed archive whose binding field covers the entry's bytes is
  the repair snapshot receipt
  `experiments/EXP-ECDLP-e962f6/tasks/TASK-20260909-ba7fcb/snapshot-receipt.json`
  (commit `022b2a9a79`), whose `path_sha256` pins
  `tools/run_supersession_registry.yaml` at `056b8355…`. That receipt lives in
  `experiments/` (outside the task's `coordination/` + `ledger/` search scope),
  and — decisively — a `path_sha256` pin on the registry file is a
  point-in-time record of the snapshot commit, not a live freeze: the registry
  is a live coordination file the validator reads on every run, and it has been
  modified **10 times** since the earlier completed archive
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-62e0f4/archives/TASK-20260808-711091/snapshot-receipt.json`
  (commit `b1f11cfe71`) pinned it at `e54f920a…`. Rule 15's failure mode
  (permanent breakage via identifier remapping — the archive's declared path/id
  no longer existing in the live tree) does not arise from adding a field to a
  registry entry: the registry path still exists and the pinned commit's tree
  is immutable and still carries the pinned bytes.
- Conclusion: the entry is not bound in the sense that matters for rule 15, so
  the primary variant (edit the entry) is used. The superseding-record
  (`manifest_v2` `id_provenance`) variant was **not** used.

The edit is append-only to the RUN-007 entry: 10 lines added
(`superseded_id_null: true` + a 7-line `superseded_id_null_provenance`), no
other record touched, no line removed (verified by `git diff`).

## Per-file sha256 table

| File | Role | before (HEAD `022b2a9a79`) | after (live) |
|---|---|---|---|
| `experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-007/raw-result.json` | NEW | — (did not exist) | `2d9236f0d2852087fa59372dd000851010681b00049e10ee302afbce66376952` |
| `tools/validate_ledger.py` | EDIT | `f5fcf23c6d2f…` | `27f49693e07804b14ef5962e4fe415810b5e28782568e231b7840e69ac38ca1e` |
| `tools/test_run_supersession.py` | EDIT | `65a8ecd1187d…` | `56b3c5a89d74df32fbbf12a3d74febbe3227fee546bf30a48d46035c0c31f2d9` |
| `tools/run_supersession_registry.yaml` | EDIT | `056b835578f8…` | `efbf9cfdf025a45ce425e3b31da0c33b5de07c2c02a54fda3dc47eec3ee3449f` |
| `experiments/EXP-ECDLP-e962f6/tasks/TASK-20260909-cb6cc7/repair-report.md` | NEW | — (this report) | see snapshot receipt |

Only these four files (plus this report) changed. Nothing else.

## Validator results

Pre-repair baseline (`python3 tools/validate_ledger.py`, before any write):
**4 new errors** — the two RUN-007 residuals plus two pre-existing errors in
the untracked `ledger/decisions/DEC-20260909-57441e.yaml` (see "Pre-existing
out-of-scope errors" below):

```
  - ledger/decisions/DEC-20260909-57441e.yaml: missing required field 'decided_by'
  - ledger/decisions/DEC-20260909-57441e.yaml: knowledge_promotion must be a mapping
  - experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-007/manifest.yaml: registered superseded run manifest declares run id None, but the supersession registry entry is for 'RUN-ECDLP-e962f6-007'
  - experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-007/manifest_v2.yaml: run directory missing artifact 'raw-result.json'
```

Post-repair (`python3 tools/validate_ledger.py`, after all writes), full
stdout:

```
FAIL: 2 new validation error(s):

  - ledger/decisions/DEC-20260909-57441e.yaml: missing required field 'decided_by'
  - ledger/decisions/DEC-20260909-57441e.yaml: knowledge_promotion must be a mapping
note: 1210 grandfathered legacy error(s) suppressed by tools/validate_ledger_baseline.txt
note: 103 frozen root-level ledger records were indexed; 371 legacy run manifest(s) were indexed; 979 legacy schema issue(s) remain read-only
note: 71 superseded run manifest(s) routed to their superseding records by tools/run_supersession_registry.yaml; both records stay hash-pinned
note: 156 archived schema record(s) routed to complete replacements by tools/schema_supersession_registry.yaml; both records stay hash-pinned
```

- **Both RUN-007 residuals are cleared** (the identity error and the missing
  `raw-result.json` error are gone).
- **Nothing else regressed**: the only remaining errors are the two
  pre-existing DEC-file errors, which were present at baseline and are outside
  this task's write scope.

## tools/test_run_supersession.py

Post-repair: **79 tests, all pass** (`Ran 79 tests … OK`).

- The two previously-failing `CommittedRegistryTests`
  (`test_committed_supersessions_are_clean`,
  `test_superseding_record_declares_the_supersession_from_its_own_side`) now
  **pass** — the RUN-007 entry's null id is bound through the narrow path.
- A NEW test class `NullIdSupersessionTests` (5 tests) pins the narrow
  null-id binding:
  - `test_registered_null_id_binds_identity` — fires for the registered
    null-id case (hash-verified, explicit field + provenance, directory
    basename == run id) → returns the run id.
  - `test_unregistered_null_id_does_not_bind` — does NOT fire for an
    unregistered parseable null-id manifest, nor for a registered entry lacking
    the explicit field (the no-generalisation guarantee).
  - `test_null_id_requires_provenance` — refused without a non-empty
    provenance string.
  - `test_null_id_requires_hash_and_directory` — refused on hash mismatch and
    on a wrong run directory.
  - `test_null_id_flag_must_be_literal_true` — refused for `False`, `1`,
    `"true"`, `"yes"`.

Other `validate_ledger.py`-exercising suites re-run to confirm no regression:
`test_validate_ledger` (4 OK), `test_yaml_identity_keys` (7 OK, 1 skipped),
`test_yaml_identity_key_amendment` (5 OK, 1 skipped),
`test_schema_supersession` (11 OK), `test_duplicate_run_ids` (5 OK).
(`test_run_provenance_quarantine` has a pre-existing import-path issue —
`from tools.test_run_supersession import …` with no `tools/__init__.py` —
unrelated to this change.)

## Immutability verification

- All eight `manifest.yaml` files byte-identical to snapshot `09de8800d0`
  (live sha256 == repair-report sha == `git show 09de8800d0:<path>` sha, all
  eight OK).
- All 69 committed files across the eight run directories byte-identical to
  HEAD (`git show HEAD:<path>`): **0 mismatches**.
- The only new run-dir file is `raw-result.json` (RUN-007). No companion file
  was added, removed, or modified.
- `git status`: exactly three modified files
  (`tools/validate_ledger.py`, `tools/test_run_supersession.py`,
  `tools/run_supersession_registry.yaml`) and the new `raw-result.json`; the
  two untracked `ledger/` files (`DEC-20260909-57441e.yaml`,
  `TASK-20260909-cb6cc7.yaml`) are the Coordinator's, not this task's.
- No committed byte changed. No commit, push, or PR made by this task.

## No-rerun declaration

No experiment was rerun. No run was re-scored. The `raw-result.json`
disclosure asserts `no_rerun: true` and `RAW_RESULT_NOT_CAPTURED`; the
validator change binds an identity, it does not alter any recorded value,
status, or result. RUN-007 remains the preserved defective no-result run
(`status: unknown`, `exit_code: 1`, no results); RUN-008 still carries the
actual Stage-2 re-read.

## Resource usage

Budget: 1800 s wall clock / 2 GB / 0 experiment runs.
Actual: **0 experiment runs**. Work was file reads, YAML/hash verification,
`validate_ledger.py` and `unittest` invocations, and file writes. Wall clock
and memory were far under budget (validator and test runs each take seconds;
no long-running processes).

## Completion gate status

1. **`validate_ledger.py` reports zero new errors: both RUN-007 residuals
   cleared, nothing else regressed** — MET. (Two pre-existing DEC-file errors
   remain; see below.)
2. **`test_run_supersession.py`: the two previously-failing
   `CommittedRegistryTests` pass; a NEW unit test pins the narrow null-id
   binding (fires registered / does-not-fire unregistered)** — MET (79/79 OK,
   including 5 new `NullIdSupersessionTests`).
3. **RUN-007 `raw-result.json` contains exactly
   `{"status":"RAW_RESULT_NOT_CAPTURED","no_rerun":true}`; all other companion
   files byte-identical** — MET (52 bytes, exact string; 69/69 committed
   run-dir files byte-identical).
4. **The eight committed `manifest.yaml` files byte-identical to
   `09de8800d0`** — MET.
5. **Nothing written outside `write_scope`** — MET (`git status` verified:
   only the three declared tool files, the declared `raw-result.json`, and this
   task report directory).

## Pre-existing out-of-scope errors (flagged for the Coordinator)

`ledger/decisions/DEC-20260909-57441e.yaml` (the approval decision for this
task, written by the orchestrating session, **untracked**, and **outside this
task's write_scope**) carries two validator errors that were present at
baseline and are not RUN-007 residuals:

1. `missing required field 'decided_by'`
2. `knowledge_promotion must be a mapping` (currently the string
   `not_warranted`)

These are not new and were not introduced by this task. They will keep
`validate_ledger.py` at 2 (not 0) total errors until the Coordinator addresses
the DEC record at archive time. Flagged here so the PR #1058 merge gate is not
surprised; no action was taken on the file because it is outside this task's
`write_scope`.
