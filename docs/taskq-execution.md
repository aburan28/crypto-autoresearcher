# Executing runs on the taskq queue

`taskq` (aburan28/crypto, `taskq/`) is a shared Redis queue whose worker pods run
a command at a pinned commit and return a write-once `taskq.task-result/v1`
document with the worker's own measurements. `harness/taskq_bridge.py` and
`tools/taskq_run.py` let an Executor run a planned experiment run there and get
back an ordinary run package in `experiments/<EXP>/runs/<RUN>/`, with the same
files and manifest fields `harness/runner.py` writes.

This is execution plumbing only. **It does not replace Coordinator approval.**
Submit only a run the Coordinator has already approved, for an experiment
whose contract is frozen. A task id is not an approval, and a finished task is
not evidence until the usual snapshot archive and review have accepted it. The
bridge allocates no ids and writes no ledger records.

## Executor workflow

```sh
# 1. The commit the worker will run must be pushed. The CLI refuses a dirty tree,
#    because the worker runs the COMMIT and not your working copy.
python3 tools/taskq_run.py spec   EXP-X RUN-X-01 -- python3 harness/run_x.py --seed 7   # inspect
python3 tools/taskq_run.py submit EXP-X RUN-X-01 --queue cpu --timeout 900 \
    -- python3 harness/run_x.py --seed 7
#    (--repetitions N makes it a benchmark; --worker-verify requests the
#     worker's advisory certificate check.)

# 2. Wait. Waiting out a local timeout is not an outcome; the task keeps running.
python3 tools/taskq_run.py wait T-...

# 3. Write the run package. This refuses to overwrite an existing RUN directory.
python3 tools/taskq_run.py package T-... EXP-X RUN-X-01 [--artifact-root /mnt/taskq-artifacts]
#    Offline, from the worker's result mirror plus the task record (get_task) as JSON:
python3 tools/taskq_run.py package --result-file r.json --task-file t.json EXP-X RUN-X-01
```

Each spec carries `source.repo: crypto-autoresearcher`,
`labels: {experiment, run, submitted_by}`, and
`idempotency_key: "<EXP>/<RUN>"`. Re-submitting the same run returns the
first task instead of running it twice.

The command writes `metrics.json` and, if it claims a solve,
`certificate.json` into `$TASKQ_OUTPUT_DIR`, using the certificate format in
[claims-and-verification.md](claims-and-verification.md). A benchmark writes
them under `run-<i>/`.

## What the package records

| file | from the result |
|---|---|
| `command.txt` | argv, cwd, env, setup, and `source.resolved_commit` |
| `environment.json` | the result's `environment` plus `worker` |
| `stdout.log` / `stderr.log` | the `_taskq_logs/*` artifacts, sha256- and size-checked before use |
| `raw-result.json` | per-run metrics, `summary`, the re-verified certificate, the full taskq result and spec |
| `manifest.yaml` | the runner.py fields, plus a `taskq` block with task_id, attempt, fence, spec_sha256, queue, worker, status, outcome_class, and the artifact hashes |

Timing and resources come from the worker's measurement: the sum of timed
(non-warmup) wall seconds, `timing_source: taskq-worker`, the peak `max_rss_kb`,
and user+sys CPU. None of these are supplied by the caller. Setup (build) time
is recorded separately as `setup_wall_seconds`.

## Status mapping

| taskq status (outcome_class) | manifest `status` | `result.valid` |
|---|---|---|
| `succeeded` (completed), no claim or verified claim | `completed_valid` | true |
| `succeeded` or `failed`, claim fails this repo's verification | `completed_invalid` (invalid_measurement) | false |
| `failed` (completed, nonzero exit) | `failed` | false |
| `timeout` / `cancelled` / `infra_error` (not_completed) | `failed_infrastructure` | false |

No row produces a negative observation. A `not_completed` task and a crash are
never negative mathematical evidence (AGENTS.md rule 3), and their
`invalid_reason` says so.

Certificates are re-verified on the submitter side by `runner._verify` and
`runner._cairn_cross_check`, the same functions `write_run` calls. A claim
that fails is then `completed_invalid`, which is `write_run`'s own rule.
`harness/runner.py` is not modified, because locked plans pin it by sha256.
The bridge therefore mirrors the few lines of `write_run` that sequence those
calls, and a test holds them equal to `write_run`'s output. A worker
`verification` block (from
`--worker-verify` on a worker that supports it) is **advisory**. It is
recorded, and any disagreement with this repo's verdict is listed under
`taskq.worker_verification`, but it never sets the status.

Every refusal happens before the run directory is created. The bridge refuses
when:

- the RUN directory already exists;
- the result fails the schema;
- the spec hash, labels, idempotency key or resolved commit do not match;
- an artifact fails its sha256 or size check;
- the cairn cross-check disagrees with this repo's verdict.

## MCP server

Agents can also submit through the taskq MCP server. Configure it per machine
with a Redis URL:

```json
{"mcpServers": {"taskq": {"command": "taskq", "args": ["mcp"],
  "env": {"TASKQ_REDIS_URL": "redis://..."}}}}
```

It is deliberately **not** in the committed `.mcp.json`, because without a
Redis URL the server fails to start. Whatever submits the task, the package
step must still go through `tools/taskq_run.py package`, so that this repo's
verification decides the run.

The schemas vendored in `harness/taskq_schemas/` are byte copies of
aburan28/crypto `taskq/taskq/schemas/*.v1.json` at `a2968daa`. Refresh them
when the protocol version changes.
