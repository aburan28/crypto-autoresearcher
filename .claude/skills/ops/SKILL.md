---
name: ops
description: "Inspect or maintain research runtime configuration, GPU/EC2/RunPod resources, DP storage infrastructure, backups, checkpoints, KB services and job synchronization. Use for infrastructure health, recovery or explicitly requested resource changes. Scientific experiment launches remain run."
---

# Research operations

Read the selected runtime or resource runbook, not every infrastructure subsystem. Sources include `orchestration/cli.py`, `tools/gf2_runpod.py`, `scripts/rho_dp/README.md`, `scripts/rho_rds.sh`, GPU EC2 scripts, and `kb/README.md`.

1. Resolve exact resource IDs, region, repository revision, job/owner, checkpoint and requested scope from current state. Inspect status before mutation. Do not use remembered credentials or print secret-bearing connection strings.
2. Separate readiness/configuration from job results. `autoresearch doctor` is useful for an explicit setup task, not an added gate on run requests. Inspect `--help`/runbook to distinguish probe/status from launch, ingest, migration or teardown.
   `gf2_runpod.py probe` checks access and GPU offers, not the state of a named job or checkpoint. That wrapper has no job-status command; use an available provider read-only interface and the actual checkpoint artifact, or report the missing interface precisely.
3. For requested maintenance, preserve offsets, completed outputs and checkpoint identity; make the affected resource and rollback/recovery path concrete. Avoid duplicate watchers or jobs.
4. Treat resource creation, database writes, permission/network changes, stop and destroy as distinct actions. Stay within the user's authorized resource scope; require explicit authorization for destructive or unrelated changes.
5. Route scientific processes to run with their existing inputs and built-in admission checks. Do not turn operational repair into a key-recovery or collision-processing campaign.
6. Return actual status, actions, identifiers, retained checkpoints and unresolved infrastructure needs. External autolab/local-macOS paths in runbooks are references, not installed binaries in this repo.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
