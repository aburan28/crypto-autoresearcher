# Prospective group-OOM supervisor — `TASK-20260908-692ab6`

This is a **source-only** package implementing the state machine approved by
`DEC-20260908-a617fa`. It is an infrastructure prerequisite for later bounded
operational verification of the exact worker memory guard. It is not an
operational result, a Docker/cgroup control pass, a scientific execution, or a
claim about any ECDLP experiment.

`container.py` contains only pure frozen-profile validation. It requires a
full, lowercase 64-hex container ID and an independently supplied exact
inspection record before a supervisor can receive any cgroup transport. Its
planned `/host-cgroup` bind is explicitly writable in the future create profile;
whether Docker Desktop actually exposes it writable, and whether the memory
controller is delegated, remains an untested live precondition.

`supervisor.py` runs the one production state machine through injected
container/cgroup/process/clock boundaries. Its prospective live adapters use
directory descriptors with `O_NOFOLLOW`, a fixed filename allowlist, exact
container-path verification, and a fork barrier. The worker profile is written
and read back before the worker is forked, migrated, or released. The helper
moves itself into `guard-supervisor`, keeps the worker in `guard-worker`, then
requires UID/GID 65534, no effective capabilities, and no `oom_score_adj=-1000`
before the worker body can proceed. Its cleanup retains partial transcripts and
only addresses directories and children created under the verified task-owned
subtree.

The three fixed future cases are represented as follows:

| Case | Requested worker profile | Required terminal classification |
| --- | --- | --- |
| `exact_profile` | 8 GiB max, 0 swap, `memory.oom.group=1` | worker readback then exit 0 |
| `group_zero_refused` | 8 GiB max, 0 swap, group `0` | typed `memory_guard_unavailable`, exit 42, no allocation or auxiliary child |
| `small_group_oom` | 64 MiB max, 0 swap, group `1` | direct worker `SIGKILL`, `oom_group_kill >= 1`, `oom_kill >= 2`, unpopulated worker subtree, surviving supervisor |

`tests.py` is the only executable check supplied here. It uses fixed synthetic
ordinary process/container/cgroup observations to run that same supervisor. It
has a pre-reserved final suite of 45 cases within the fixed total 320-case cap,
leaving 275 cases for a future Coordinator-authorized correction if needed. It
captures the one child test command’s terminal status, stdout, stderr, UTC
boundaries, CPU/wall/RSS measurements, and zero yielded session IDs in
`check-receipt.json`. No `.pyc` artifact is allowed under this task directory:
the check uses `-B` and `PYTHONDONTWRITEBYTECODE=1`.

The test suite’s result is source-control evidence only. A snapshot and a fresh
independent source review are still required before the Coordinator may create
a separate live operational handoff. That later handoff must retain the external
host Docker transcript, inspect the exact container ID, recheck the writable
mount and delegation, and never treat a failed availability check as a
scientific result.
