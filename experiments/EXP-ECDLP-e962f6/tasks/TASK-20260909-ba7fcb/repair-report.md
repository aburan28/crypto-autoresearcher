# Repair report — TASK-20260909-ba7fcb

Post-archive run-manifest schema-conformance repair of the eight committed run
manifests of EXP-ECDLP-e962f6 (snapshot `09de8800d0`, branch
`runs/EXP-ECDLP-e962f6-20260909`).

- Task: `TASK-20260909-ba7fcb` (`ledger/handoffs/TASK-20260909-ba7fcb.yaml`)
- Executor: opencode session `run-e962f6-20260909`, policy `executor-implementation`
- Date: 2026-09-09
- Nature: administrative integrity repair only. No science, no status change,
  no re-scoring, no reruns.

## Method

Each of the eight committed `manifest.yaml` files (immutable, snapshot
`09de8800d0`) is repaired by a NEW hash-pinned superseding record
`manifest_v2.yaml` in the same run directory, registered in
`tools/run_supersession_registry.yaml` (append-only). The superseding record
transcribes every recorded value value-identical into the ledger's nested
`run:` shape; where a value was not recorded, it writes an explicit null with
a reason. Nothing is inferred, recomputed, or re-scored.

Mechanical verification (python3 + yaml + hashlib, run against all eight
pairs after the writes):

- every transcribed field value-identical to the source manifest
  (`command`, `git.*`, `code.*`, `environment`, `seeds`, `params`,
  `inference`, `timing`, `exit_code`, `protocol_deviations`, `artifacts`,
  `working_directory` where present, and the carried `run:` header fields);
- `run.supersedes.prior_manifest_path` / `prior_manifest_sha256` match the
  actual file and the registry entry;
- `run.code.command` equals `command.txt`; `run.environment` equals
  `environment.json`;
- `run.result.metrics.summary_sha256` / `raw_result_sha256` equal the actual
  companion file hashes (runs 001–006, 008).

Result: all eight pairs OK.

## Per-run mapping (old flat field → new nested field)

Common to all eight runs (flat top-level siblings of `run:` → nested `run:`):

| Old (flat, top-level) | New (nested under `run:`) |
|---|---|
| `command` | `run.code.command` |
| `git.commit` | `run.code.commit` |
| `git.branch` | `run.code.branch` |
| `git.dirty` | `run.code.dirty` |
| `git.status_porcelain` | `run.code.status_porcelain` |
| `working_directory` (runs 002–008) | `run.code.working_directory` |
| `code.source_dir` | `run.code.source_dir` |
| `code.source_sha256` | `run.code.source_sha256` |
| `code.reference_instrument` | `run.code.reference_instrument` |
| `environment` (8 fields) | `run.environment` (identical; equals `environment.json`) |
| `seeds` | `run.inputs.seeds` |
| `params` | `run.inputs.parameters` |
| `inference` | `run.inference` |
| `timing` (`started_at`, `finished_at`, `wall_clock_seconds`, `peak_rss_bytes`) | `run.timing` (identical) |
| `timing.peak_rss_bytes` | `run.resources.peak_rss_bytes` (transcribed, not recomputed) |
| `exit_code` | `run.exit_code` |
| `protocol_deviations` | `run.protocol_deviations` |
| `artifacts` | `run.artifacts` |
| `run.id` / `run.experiment_id` / `run.status` / `run.kind` / `run.stage` / `run.failure_class` / `run.validity` / `run.validity_reason` / `run.note` | carried forward unchanged under `run:` |

New fields added by the repair (all explicit, none inferred):

- `run.inputs.curve_id: null` + `curve_id_note` — no curve id was recorded;
  this is a numerical experiment on a finite group, not a curve-specific run.
- `run.inputs.seed: null` + `seed_note` — no seed was recorded.
- `run.resources.cpu_seconds: null` + reason — not recorded.
- `run.result.metrics` — sha256-bound pointer to `summary.json` +
  `raw-result.json` (runs 001–006, 008); `null` + `metrics_note` (RUN-007,
  no results produced).
- `run.result.valid` — `true` (runs 001–006, 008, transcribed from
  `validity: true`); `null` (RUN-007, no validity determination was recorded).
- `run.result.invalid_reason: null` — no invalid reason was recorded.
- `run.result.validity_reason` — transcribed from `run.validity_reason`.
- `run.result.certificate: {kind: none, verified: null, verifier: null, note}`
  — kind is honest: no certificate kind was recorded in any source manifest.
- `run.supersedes: {prior_manifest_path, prior_manifest_sha256, precedence}`.
- `run.schema_repair: {task_id, no_rerun: true, method, field_provenance}`.

Per-run sha256 (before → after):

| Run | `manifest.yaml` (immutable) | `manifest_v2.yaml` (new) |
|---|---|---|
| RUN-ECDLP-e962f6-001 | `d64ab9a7310de255083bb624470edb563f3ffb15e4eab91dae68f7627eb180f0` | `80bd57e45008812e9066176474cab0f54a751dc84afa0346e83c64e57a635635` |
| RUN-ECDLP-e962f6-002 | `8f1309b8af17f5e7c8830d2441792f3c1ccba6e8cccd3daf0539904885638783` | `16e78d614094e230f0887bed2d8ba5578518975d1d3ddd6451eb78c8079b2b1b` |
| RUN-ECDLP-e962f6-003 | `615e2ebf5d88f59ac9246947cebcfd05273768e541dd7aef5e3e7d851fa8bf84` | `993c673a8dc533806ab32840350ad20f78b28d57e23b51d248f18e24e0dcff3f` |
| RUN-ECDLP-e962f6-004 | `f28fc26f143cfc72bfea179d1e08e3b18d966ce132261604d7ec9868f1746ef9` | `7448e1d1972e8b2064aa2a78e1287cccf0e13ce93e92b8b0595013c1698f2044` |
| RUN-ECDLP-e962f6-005 | `96c9e844605fade4747320dfd707738b09ce098cfe3ee2a934980cbe5b5475c1` | `f89145a4bce8725d333ea432e7263143189ca1b5cf32bed61adc937b3d477eed` |
| RUN-ECDLP-e962f6-006 | `293b8c2ac0117ea364390caae965224a3abe6647c4569eb838f9906836121044` | `f9ab0c804b8c9a399f7332bd8cd91e52391e4a3c396b38afe509c5dcb28bae1e` |
| RUN-ECDLP-e962f6-007 | `64fb587ad9ea3b31cbec6e42b9c1f3d3a713408bd324411c32c583d79e1b540c` | `313ff5530a9cc19357fc4e78e30ae032905509795544d89a660f9bd6783cf2a3` |
| RUN-ECDLP-e962f6-008 | `bfa9b20d73691b0cf7e1fc7cbb572b7888f8885549a736f408f4c8d514bca592` | `797c044f48e2fb803abee91ced615195d5ea563a1c8479255ee16520c674b4b3` |

## RUN-007 (defective run) — preserved as recorded

- `status: unknown`; `kind`/`stage`/`failure_class`/`validity`/
  `validity_reason`/`note` null as recorded; `exit_code: 1`.
- The recorded defect (implementation error, path bug, `FileNotFoundError` —
  see `stderr.log`) is preserved verbatim; the run is not re-scored and no
  result is asserted.
- `id`: the immutable manifest declares `id: null`. The superseding record
  declares `id: RUN-ECDLP-e962f6-007`, recovered from the run directory name
  and the program's own committed references (the note in
  RUN-ECDLP-e962f6-008's manifest; TASK-20260909-ba7fcb), with an
  `id_provenance` block recording the recovery.
- `seeds: {}`, `params: {}`, `source_sha256: {}` transcribed as recorded (the
  driver crashed before recording them).
- `artifacts` list transcribed as recorded, with `artifacts_note`:
  `raw-result.json` and `summary.json` are named in the recorded list but do
  not exist in the run directory; that discrepancy is part of the recorded
  defect and is preserved, not repaired.

## RUN-008 (re-read run) — role carried forward unchanged

The re-read role is carried forward unchanged: `run.note` transcribed
verbatim, and the registry entry's notes state the same.

## Validator results

Pre-repair baseline (`python3 tools/validate_ledger.py`, before any write):
exit 1, 67 new errors, all in the eight manifests:

- RUN-001..006, 008: 8 each (missing `run.code`/`environment`/`inputs`/
  `timing`/`result`, `code.commit`, `code.command`, `certificate.kind`) = 56
- RUN-007: 11 (the same 8 + `bad run id None` + missing `raw-result.json`
  artifact + `certificate.kind`)

Post-repair (`python3 tools/validate_ledger.py`, after all writes), full
stdout:

```
FAIL: 2 new validation error(s):

  - experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-007/manifest.yaml: registered superseded run manifest declares run id None, but the supersession registry entry is for 'RUN-ECDLP-e962f6-007'
  - experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-007/manifest_v2.yaml: run directory missing artifact 'raw-result.json'
note: 1210 grandfathered legacy error(s) suppressed by tools/validate_ledger_baseline.txt
note: 103 frozen root-level ledger records were indexed; 371 legacy run manifest(s) were indexed; 979 legacy schema issue(s) remain read-only
note: 71 superseded run manifest(s) routed to their superseding records by tools/run_supersession_registry.yaml; both records stay hash-pinned
note: 156 archived schema record(s) routed to complete replacements by tools/schema_supersession_registry.yaml; both records stay hash-pinned
```

- 65 of the 67 baseline errors are resolved; nothing else regressed (no other
  new errors anywhere in the ledger).
- The 2 remaining errors are both RUN-007-specific and are disclosed
  residuals, not suppressions:
  1. **Identity.** The immutable defective manifest declares `id: null` and
     parses normally. The validator's identity recovery
     (`superseded_id_line` / `_malformed_run_header_id`) is exclusively for
     UNPARSEABLE YAML with a literal `run_id: RUN-...` root header:
     `_malformed_run_header_id` returns `None` for any parseable file
     (`tools/validate_ledger.py:1432`), and the `_malformed_superseded_run_id`
     fallback is only reached on YAML parse failure (line 1407). There is no
     production path to bind the identity of a parseable manifest with a null
     id, so registering the supersession (as the handoff mandates) forces the
     identity error.
  2. **Missing artifact.** The defective run produced no results, so
     `raw-result.json` does not exist. The validator's exemption (status in
     `{running, in_progress}` + `raw_result_pending` + kind `none`, lines
     750–757) does not apply to status `unknown` — "terminal/unknown statuses
     ... still owe it" (line 746). This task's write scope forbids adding a
     disclosure file.

Resolution paths (Coordinator decision; outside this task's write scope):

1. Write-scope amendment adding a `raw-result.json` disclosure file to
   RUN-007's run directory (2026-08-08 pattern:
   `{"status": "RAW_RESULT_NOT_CAPTURED", "no_rerun": true}`) — resolves
   residual 2.
2. Validator amendment adding an identity-recovery path for parseable
   manifests with a null id (e.g., directory-name binding for registered
   supersessions) — resolves residual 1.
3. Accept the two disclosed residuals as the terminal state of this repair.

## tools/test_run_supersession.py

Post-repair: **2 failed, 72 passed, 73 subtests passed**. Both failures are
on the RUN-007 entry and are the same identity obstacle
(`AssertionError: None != 'RUN-ECDLP-e962f6-007'`):

- `CommittedRegistryTests::test_committed_supersessions_are_clean`
- `CommittedRegistryTests::test_superseding_record_declares_the_supersession_from_its_own_side`

All other committed supersessions (63 entries) pass.

## Immutability verification

- All eight `manifest.yaml` files byte-identical to snapshot `09de8800d0`
  (sha256 verified before and after; per-run table above).
- All 53 companion files (`command.txt`, `environment.json`, `run-meta.json`,
  `raw-result.json`, `summary.json`, `stdout.log`, `stderr.log`, where
  present) byte-identical before and after: 61 file hashes compared, 0
  mismatches.
- `git status`: only additions — 8 new `manifest_v2.yaml` files, a 159-line
  append to `tools/run_supersession_registry.yaml` (0 lines removed, all at
  end of file), and the new `tasks/TASK-20260909-ba7fcb/` directory. No
  committed byte changed. No commit, push, or PR made by this task.

## No-rerun declaration

No experiment was rerun. No run was re-scored. Every value in every
`manifest_v2.yaml` was read from the committed manifest or its companion
files; nothing was inferred, recomputed, or fabricated.

## Resource usage

Budget: 1800 s wall clock / 2 GB / 0 experiment runs.
Actual: **0 experiment runs**. Work was file reads, YAML/hash verification,
two `validate_ledger.py` invocations, one `pytest` invocation, and file
writes. Wall clock and memory were far under budget (validator and pytest
runs each take seconds; no long-running processes).

## Completion gate status

1. **All eight `manifest_v2.yaml` validate under `check_run` (routed via the
   registry)** — MET for RUN-001..006, 008 (zero errors). For RUN-007 the
   schema portion is met (nested record, id, all `RUN_REQUIRED_TOP` fields,
   `code.commit`, `code.command`, `certificate.kind: none`); the only
   `check_run` error on its `manifest_v2.yaml` is the missing
   `raw-result.json` artifact (residual 2 above).
2. **Each `manifest_v2.yaml` declares the supersession from its own side**
   (`run.supersedes`, exact path + same prior sha256 as the registry entry) —
   MET for all eight (mechanically verified).
3. **Registry carries exactly eight appended records, no other change** —
   MET (`git diff`: 159 insertions, 0 deletions, all at end of file).
4. **`check_run_supersessions` passes for all eight** — MET for seven; NOT
   MET for RUN-007 (identity residual 1 — concrete technical obstacle, no
   production recovery path).
5. **Eight committed manifests byte-identical to `09de8800d0`** — MET.
6. **Companion files exist and are untouched** — MET (61/61 hashes identical).
7. **No new errors relative to the pre-repair baseline** — NOT FULLY MET: 65
   of 67 resolved; two RUN-007-specific errors remain (one re-routed from the
   baseline to `manifest_v2.yaml`, one new from the registration itself).
   Nothing else regressed.
8. **Per-run mapping note present** — MET (this report).
9. **Nothing written outside the declared `write_scope`** — MET
   (`git status` verified).
