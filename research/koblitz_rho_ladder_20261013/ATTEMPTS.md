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
