# Infrastructure-diagnosis findings: EXP-FROB-d8aa37 stage0 whole-environment restarts

Non-scientific, operational finding. Produced by the dispatching session in
response to DEC-20260921-8aa5cf's NA-4 escalation, which converted the
long-standing, sixteen-times-reaffirmed NA-4 recommendation into an explicit
evidentiary precondition on any eighteenth genuine launch attempt: before
that authorization, the dispatching session must supply either (a) actual
infrastructure-diagnosis findings, specifically addressing whether the
trial's own `memory_mb=8192` footprint under Sage is a plausible proximate
cause of the restarts, or (b) an explicit, concrete disclosure of why such
findings could not be obtained.

This note supplies (a) to the extent obtainable in this environment, and
(b) for the one specific piece that is categorically unobtainable here.

## What was checked, and when

Checked immediately after detecting the seventeenth restart (the one that
killed `RUN-FROB-6d29ae`, v21), on the freshly-booted environment, before
any further work in this cycle: `dmesg`, `journalctl -k -b 0`, `free -h`,
`/proc/meminfo`, `/sys/fs/cgroup/memory.max` and
`/sys/fs/cgroup/memory/memory.limit_in_bytes`, `/sys/fs/cgroup/**/*memory*event*`,
`/sys/fs/cgroup/memory.stat` (grepped for `oom`), `last reboot` (wtmp),
`/proc/1/cmdline`, `/proc/1/status`, `ps -ef`, and the current session's own
environment variables.

## Finding 1 (structural, definitive): no forensic log survives any restart here, by construction

- `journalctl -k -b 0` reports "No journal files were found." `ps -ef` shows
  no `systemd-journald` process running at all in this container, despite
  the `journalctl`/`systemctl` binaries being present. Logs are simply not
  being collected or persisted in this environment.
- `dmesg` contains only the current boot's own ~2.5 seconds of kernel
  messages (timestamps `[1.09]` through `[2.85]`), starting fresh from the
  Firecracker init handoff. The kernel ring buffer does not survive a
  restart; there is no historical dmesg to inspect.
- `last reboot` shows only `wtmp begins Tue Feb 17 02:02:53 2026` with no
  reboot records logged since -- wtmp is not being written to across
  restarts either.

**Consequence**: retrospective OOM-killer / eviction / scheduler-preemption
diagnosis at each of the seventeen historical restart timestamps, as NA-4
asked for, was never obtainable in this environment and will not become
obtainable on any future cycle under this same configuration. This is not a
one-off access failure; it is a structural property of how this container
is provisioned (no persistent journal, no dmesg carried across restarts,
no wtmp updates). This is disclosure (b) for that specific piece of NA-4's
ask.

## Finding 2 (mechanistic, from the current boot): the WHOLE microVM is recreated, not just the trial process

- `/proc/1/cmdline` on the fresh boot is
  `/process_api --firecracker-init --addr 0.0.0.0:2024 ...` -- PID 1 itself,
  the container's own init, is the Firecracker init handoff process, with a
  fresh start time matching the boot (`ps -ef` shows PID 1's STIME as the
  same `21:39` as the restart).
- This means each restart recreates the entire microVM, init included, not
  merely the Sage/driver-v2.py process tree within a persisting container.
  An in-guest OOM-killer event ordinarily targets the highest-scoring
  process and leaves the container's own init running; it does not restart
  init itself. What is observed here -- init itself relaunching with a
  fresh PID-1 start time -- is the signature of an external, platform-level
  microVM restart (host-level lifecycle action: maintenance, fleet
  rebalancing, or the session/container reclaim this runtime's own
  documentation describes as normal for these ephemeral environments), not
  an in-guest resource-exhaustion kill of one process.
- This environment's own system prompt states containers "the container is
  reclaimed after a period of inactivity (or when the session ends)" --
  this session was under active, ~5-minute-cadence polling throughout
  RUN-FROB-6d29ae's lifetime, so a naive inactivity reclaim keyed only on
  elapsed wall-clock time is a plausible external mechanism independent of
  the trial's own memory footprint, though this cannot be confirmed without
  access to the orchestrator's own logs, which this session does not have.

## Finding 3 (static configuration, immediately post-restart): no memory ceiling close to 8GB

- `free -h` on the fresh boot: 15Gi total, 654Mi used, 12Gi free, 15Gi
  available, 0B swap.
- `/proc/meminfo`: `MemTotal: 16481980 kB` (~16GB), `MemAvailable:
  15811656 kB` (~15GB) at boot, before the trial process starts.
- `/sys/fs/cgroup/memory/memory.limit_in_bytes` reads `9223372036854771712`
  -- effectively unbounded (no meaningful cgroup memory cap is configured
  for this container).
- `/sys/fs/cgroup/**/*memory*event*` and `memory.stat`'s own `oom` lines:
  no matches -- no cgroup-level OOM accounting is present to check, which
  is consistent with Finding 1 (nothing here persists across a restart to
  inspect after the fact) rather than evidence either way about what
  happened during the run itself.
- With ~16GB total and no visible cap near 8GB, the trial's declared
  `memory_mb=8192` leaves roughly half the container's total memory as
  headroom under its own static configuration. This does not rule out a
  transient in-guest memory spike immediately before a given restart (no
  telemetry survives to check that directly, per Finding 1), but nothing in
  the container's static memory configuration makes `memory_mb=8192`
  structurally tight against a hard limit.

## Conclusion supplied to the coordinator (finding (a), to the extent obtainable)

The evidence obtainable in this environment -- the whole-microVM-level init
respawn (Finding 2) together with the absence of any near-8GB memory
ceiling in the static configuration (Finding 3) -- is more consistent with
an external, platform-driven whole-environment restart than with an
in-guest OOM-kill triggered by the trial's own `memory_mb=8192` Sage
footprint. This is not proof: no direct telemetry survives any of the
seventeen historical restarts to confirm the proximate trigger with
certainty (Finding 1), and that gap is structural to this environment, not
a one-time omission. Monitoring-cadence reliability (the third strand NA-4
asked about) was separately addressed operationally in this lane by
widening from a 5-minute to a 15-minute check cadence only after roughly
three hours of confirmed continuous health, and narrowing back to 5-minute
checks immediately on detecting each restart -- this keeps the honestly
disclosed detection-gap bounded without requiring an external timeout
wrapper on the trial process itself.

## Provenance

- Recorded by: dispatching session, immediately after detecting the
  seventeenth whole-environment restart (the one that ended
  `RUN-FROB-6d29ae`).
- Not a scientific record; carries no claim about H-FROB-73df22 in either
  direction. Cited by the coordinator dispatched for the next
  (eighteenth-attempt) admission cycle, per DEC-20260921-8aa5cf's NA-4.
