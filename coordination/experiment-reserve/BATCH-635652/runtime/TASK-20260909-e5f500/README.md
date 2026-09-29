# Native group-OOM source correction — `TASK-20260909-e5f500`

This eight-file package is an additive source successor to the seven files at
`ae1e0ffd286ce70ed781b923554a75a5faf375d0`. It implements the correction
approved by `DEC-20260909-a86941` and preserves the original three future
controls exactly. It contains no live Docker, cgroup, mount, credential,
process-migration, memory-pressure, or scientific result.

`host.py` is the prospective host entry. It requires the exact cached image and
uses `docker create --pull never` with a unique task label, private PID
namespace, no network, a read-only root, `ALL` capabilities dropped and only
`SETUID`/`SETGID` restored, no-new-privileges, one CPU, 32 PIDs, an 8 GiB outer
memory/no-swap profile, and the one frozen `/sys/fs/cgroup` bind. It copies an
in-memory tar containing only hash-pinned `container.py` and `supervisor.py`;
there is no repository or host-code mount. It constructs `ContainerInspection`
from the full JSON returned by exact-ID Docker and image inspections. Only after
that independent inspection matches does it start attached with the public task
ID, full container ID, and fixed case ID on stdin.

Every host command retains argv, stdin size/digest, UTC boundaries, process and
terminal fields, stdout, stderr, timeout state, and session fields. After the
container stops, the host inspects its exact ID and collects complete timestamped
logs. A clean result requires a complete inner cleanup, attach exit 0, outer
exit 0, `Running=false`, and `OOMKilled=false`. Any missing/malformed inner
report, failed inner cleanup, watchdog, outer OOM, or unclean terminal state
causes exact-ID termination and inspection before exact-ID removal. The
original failure remains first and secondary custody failures are appended.

`container.py` reads exactly one bounded JSON identity line from stdin. It does
not accept caller-built inspection facts. Its native entry constructs the
descriptor cgroup adapter and POSIX worker transport only after the task, full
ID, and case are valid.

`supervisor.py` verifies Linux and cgroup2 twice: `fstatfs` must return
`CGROUP2_SUPER_MAGIC`, and `/proc/self/mountinfo` must identify the exact mount
as a writable cgroup2 mount. `/proc/self/cgroup` must name exactly one accepted
full-ID Docker path. All traversal uses directory descriptors, `O_NOFOLLOW`,
fixed child names, and fixed read/write filename allowlists. Partial child
creation rolls back; a failed rollback is explicit incomplete custody for the
outer host to contain.

The worker starts behind a real one-way release plus membership-ack control
pipe. The parent drains its bounded event pipe while polling wait status and
worker counters, so a full event pipe cannot deadlock the child. Writes loop
across interruptions and short writes. Malformed, truncated, oversized, or
failed reports cannot become complete custody. Every known main child is
signalled only by its exact retained handle when needed, waited, reaped, and has
all descriptors/state closed even after fork, release, migration, or report
failures.

For the small group-OOM control, the dropped worker owns its auxiliary child and
cleans/reaps it on ordinary failures. It emits the exact auxiliary PID and waits
for the supervisor to verify both direct members in `guard-worker` before it can
emit `before_allocation`. The supervisor polls `memory.events` at bounded cadence
and requires final-minus-baseline increments of at least one
`oom_group_kill` and two `oom_kill`, a SIGKILL terminal for the direct worker,
and an empty worker subgroup. Inner evidence stops at “pending outer”; only the
host terminal inspection can classify `oom_observed`.

The fixed cases remain:

| Case | Worker profile | Required future terminal observation |
| --- | --- | --- |
| `exact_profile` | 8 GiB, zero swap, group 1 | post-drop profile and membership readback, exit 0 |
| `group_zero_refused` | 8 GiB, zero swap, requested group 0 against required group 1 | typed `memory_guard_unavailable`, exit 42, no auxiliary or allocation |
| `small_group_oom` | 64 MiB, zero swap, group 1 | both members verified before pressure, direct worker SIGKILL, counter increments, empty subgroup, clean inner and outer supervisor custody |

`tests.py` runs production logic with fixed injected Docker/cgroup/mount and
failure observations. Its only native effects are five sequential, current-user
POSIX child fixtures for pipe draining, membership acknowledgement, canonical
signal naming, wait/reap, and failure cleanup. Each has a three-second parent
watchdog, at most one live fixture child, and no more than 128 KiB deliberate
payload. All PIDs and terminal records are embedded in `check-receipt.json`.

The source task reserves one final suite of at most 128 cases within the
640-case total and uses one nested test worker. The parent watches that worker's
resident memory against 2 GiB and records the exact Darwin limitation: this host
refuses lowering `RLIMIT_AS` with `ValueError: current limit exceeds maximum
limit`, so no address-space hard cap is claimed. `-B` and
`PYTHONDONTWRITEBYTECODE=1` prevent bytecode artifacts.

Passing these checks establishes only source and bounded process-custody
properties. Local cgroup2 bind writability and delegation, all three live guard
cases, experiment arithmetic runtimes, and scientific measurement remain
unexecuted. The next action is Coordinator snapshot task
`TASK-20260909-90f2b9`, followed by a fresh independent complete source review.
