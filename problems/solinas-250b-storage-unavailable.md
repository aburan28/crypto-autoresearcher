# Full-data storage for the250-billion point campaign is unavailable

- **Status:** `investigating`
- **Kind:** resource limit and missing outbound storage identity
- **Affected work:** [250-billion protocol](../tasks/solinas_250b/PROTOCOL.md)
- **Next action owner:** runtime storage configuration for full retention; aggregate execution in this task
- **Last updated:** 2026-10-14

## Problem

The full compact250-billion dataset cannot be persisted in the current
filesystem, and no managed AWS identity is currently configured for S3.
Execution must have a declared data destination or explicitly selected bounded
aggregate retention before starting the scientific streams.

## Evidence and uncertainty

- **Observed:** `df -h /workspace` reports a32 GB filesystem with about550 MB
  free. Earlier scientific raw data and archives are preserved. Managed runtime
  revision121 reports current observations, unrestricted enforced HTTP policy,
  no secrets/runtime variables/outbound identities. A new scientific run has
  not been launched. [Preparation/protocol](../tasks/solinas_250b/PROTOCOL.md).
- **Derived:** the prior1.52 GB compact raw dataset for5.91 billion observations
  scales to roughly64 GB for250 billion; actual rare-frame volume can vary.
  A~70 GB full-data reservation is an admission estimate, not a guaranteed bound.
- **Missing capability:** a larger writable filesystem, working S3 identity
  for immutable data objects/checksum reads, or explicit aggregate-mode choice.
- **What this does not establish:** no result about elliptic-curve distributions,
  prime families or ECDLP. A storage dependency is not a mathematical obstruction.

## What would unblock it

- [ ] Larger writable data filesystem admitted by the runner, or configured
  S3 identity that can upload and confirm SHA256/length in `crypto-autoresearcher`.
- [x] Alternatively, selection of the declared bounded aggregate mode,
  accepting that individual measured bit strings will not all be stored.
- [x] Source/input freeze and successful engineering checks before launch.

Satisfying these permits the exact fixed campaign to begin; it establishes no
scientific outcome and does not eliminate later storage/compute interruptions.

## Next discriminating step

- **Action:** launch the prepared aggregate campaign under the October14 “Go”
  instruction with the runner's unchanged admission checks; retain the full-data
  storage gap for later arbitrary ML feature searches.
- **Inputs/controls:** fixed3 candidates, actual/random generators,62 R+63 C
  coefficient/step-x matched models; fresh public seed.
- **Limits/stop:** exactly250 billion observations; source/config/storage fixed;
  operational failure preserves partial attempts and stops new scheduling.
- **Outcomes:** successful storage admission starts the study; missing connection
  or insufficient capacity remains an execution dependency, not negative science.
- **Recheck trigger:** actual aggregate admission, or larger/configured storage.

## Resolution and history

2026-10-12: storage question requested while preparing an agent-free streaming
runner and checking exact sample counts. Unresolved. No old data was deleted,
no unconfigured identity substituted, and no official research status changed.

2026-10-14: current managed runtime revision128 is connected and reports no
configured secrets, runtime variables or outbound identities. The filesystem
still has about550 MB free. User instruction “Go” was accompanied by the
announced aggregate fallback if full storage remained unavailable. The exact
250-billion measurement target and count-based inference are preserved. Full
compact data for later arbitrary ML searches remain unavailable; aggregate
mode does not resolve that retention requirement. Source freeze/push and actual
runner admission are the next actions; no scientific execution is claimed here.

2026-10-14 launch: source/input freeze was committed and pushed as
`068797c4d5d59c9e73531f751e820c9250fe7c9a` before sampling. The runner
admitted aggregate storage and three workers. The first immutable publication
snapshot records16 completed chunks,150,994,944 observations,0 failures, and
an equal number of native finite/on-curve checks. See the
[launch snapshot](../tasks/solinas_250b/publication/launch-20261014/progress-at-snapshot.json)
and [launch/runtime metadata](../tasks/solinas_250b/publication/launch-20261014/launch.json).
The count-based campaign is running and resumable; full compact data for later
arbitrary ML remain unavailable. This resolves the execution-destination
dependency for aggregate mode, not the full-retention requirement. No official
research status or mathematical claim is changed.
