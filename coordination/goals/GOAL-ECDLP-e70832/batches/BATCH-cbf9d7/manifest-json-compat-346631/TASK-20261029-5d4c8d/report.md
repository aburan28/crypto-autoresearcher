# Full native manifest JSON representation bridge

The final preparation check passed against the sealed RUN-ECDLP-939237: 51 native logical files and all 39 archive members match their original digests. Original native status remains `invalid_output`, driver exit 0 and checker exit 1. No dataset, status, source, frozen plan or protocol was changed. This is administrative representation work; no ECDLP result is asserted.

Final adapter SHA256: `8165b81bc758d44e9424c51605914b6a89dbeffcde8317f5e8b402c90540bab3`. Final derived full-manifest SHA256: `2c60bea2625d1287a1d827afc496b177e0b17a24bd55f6518b2bd16546c2e755`. Exact original driver text witness remains SHA256 `7898ed6b86985fa31955fa8f21bccdb4deee6cc389165071fbc89d274205de37`. Full native tree equality and original-witness recursive subset comparisons are type-strict. Duplicate JSON/YAML keys, nonfinite values, YAML aliases, timestamp tags and coercive scalar encodings are refused. Twelve fixed parser/type mutants were refused; details and exact command/output hashes are in checks.json.

The actual final preparation verifies original native schema (errors[]), the launch authority, actual commands, approved frozen plan/specification, copied protocol/static inputs, executing source hashes, original execution-receipt artifact hashes, controller duplicate, collection seal, quiescence and termination acknowledgement. It streams the archive and every logical native file, then binds the published identity pointer and modern manifest to the same immutable archive payload, actual raw snapshot and previously recorded full S3 GET proof. It performs no network read itself.

The prepared view descriptor is explicitly `materialized:false`: only its derived JSON manifest exists outside the repository. Root must run `materialize` at a fresh canonical view destination before committing actual provenance. Fourteen already readonly source files can be hardlinked without changing original permissions; the remaining 36 non-manifest roles receive private copies whose permissions alone are changed. These method counts are the actual source-permission classification in the prepared descriptor. JSON replaces only the derived manifest representation. The helper checks all original file bytes again after materialization. Materialization itself has not been run by this producer and filesystem behavior remains for the root and fresh independent reviewer to assess.

The first preparation attempt failed because the helper guessed `spec.yaml`. That failed source and stderr are retained outside, and final code reads the actual `specification` path from the frozen trial plan. A second preparation passed; final code then added explicit stored-byte/payload digest bindings and destination-symlink refusal, and the final preparation passed again. None of these commands created candidate work or host scalar labels, entropy, or references.

Root command after copying the exact adapter/checks/report source files:

```sh
/workspace/classical-ecdlp-endpoint-reuse/runtime-20261028/bin/python \
  coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/manifest-json-compat-346631/TASK-20261029-5d4c8d/adapter.py materialize \
  --repo-root /workspace/classical-ecdlp-validation-ready \
  --destination /workspace/classical-ecdlp-validation-ready/coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/derived-supervisor-views/RUN-ECDLP-939237/manifest-json-v1
```

Root materialization writes final actual view-provenance.json, .gitignore and supervisor/manifest.yaml, plus ignored complete payload view. It invokes neither driver.check nor postrun. The isolated TASK-20261029-5b0e13 snapshot and fresh independent TASK-20261029-3b5feb validation—including unchanged full driver.check—must precede host labels, host entropy or postrun. No inner-transport mode, parser monkeypatch, hidden fallback or fabricated output_validated status is used.

Source review: driver.py, complete_manifest in tools/experiment_execution.py, scoped check_run in tools/validate_ledger.py, docs/artifact-storage.md and installed PyYAML's loader entrypoint; exact source observations are in checks.json. External papers were not fetched for this zero-science format task, and no novelty claim is made. The pre-data calibration resolution literal 1/512 stays unqualified; later analysis must retain signed numerator/all actual draws and the frozen 1800-draw definition.
