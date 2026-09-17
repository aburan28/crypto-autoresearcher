# RUN-SEMBIN-595308 — status: RUNNING (interim snapshot)

This package is being written by two worker processes (workerA: reproduction +
off-diagonal cells; workerB: separation cells). Files under `worker*/cells/`
are append-only (`results.jsonl`, `progress.log`) or write-once per instance.
The run is NOT complete: no `manifest.yaml` or `task-report.md` exists yet, and
nothing here is an official run record until the completing snapshot commit
adds them and this file is superseded by the manifest's `status`.
Interim commits exist only so an ephemeral container cannot lose measured cells.
