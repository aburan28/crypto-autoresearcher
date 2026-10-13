# Attempt log

This file preserves setup and execution failures as well as the successful
run. It is append-only within this exploratory round.

1. The first native-harness build attempt failed because `cargo` was absent
   from `PATH`.
2. Installing Rust with `rustup` produced a non-fatal attempt to update the
   read-only `/home/agent/.profile`; an explicit toolchain installation under
   `/tmp/koblitz-{cargo,rustup}` then succeeded.
3. A one-target diagnostic of the older `ic rho` interface at degrees
   11, 13, 17, 19, 23, 29, and 31 completed and verified. It was not retained
   as inferential data. It exposed tiny subgroups/high cofactors at degrees
   29 and 31 and motivated the explicit subgroup-size eligibility rule and
   the use of `ecbench`'s phase counters.
4. The frozen run below had not started when this protocol and spec were
   committed.
5. The first frozen-run launch attempt used `/usr/bin/time`; that executable
   was absent, so the shell returned 127 before `ecbench` started and before
   an output session directory was created.
6. The unchanged frozen spec then ran with the shell's `time` keyword.
   Session `ECBS1h5a5461ff22d7` completed all 10,752 planned executions in
   8m12.471s wall time. Its status counts are 10,752 `verified` and zero in
   every other outcome category. The raw-record SHA-256 sealed by the session
   is `d82f6319a75e16d0185323b69e2e4b0760f2753510ec45f026b7004148a49a3c`.
7. A full deterministic replay audit then reproduced all 10,752 executions
   with zero problems in 8m6.856s wall time. The preserved audit receipt has
   SHA-256
   `74bfadbd5c6d3e0da09fc826dc5323365db5361577008d5ea5a31a7747b71cb7`.
