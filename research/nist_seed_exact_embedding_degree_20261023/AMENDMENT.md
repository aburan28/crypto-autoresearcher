# Operational amendment after failed first launch

2026-10-23 UTC. The frozen protocol's 1 GiB address-space limit could not be
installed by `resource.setrlimit(RLIMIT_AS, ...)` on this macOS host. The
first launcher stopped in `preexec_fn` before the worker started, as recorded
in `runs/exact-20261023T1810Z/failure.json`; it produced no curve results.
A direct control showed `ValueError: current limit exceeds maximum limit` for
both the attempted 1 GiB soft/hard address-space setting and a 1 GiB soft
limit with the inherited hard limit. This is an operating-system admission
failure, not an embedding-degree observation.

The replacement launcher keeps the frozen 120-second per-case watchdog and
uses a 10 ms process resident-size watchdog at 1 GiB. It records sampled peak
RSS and stops a child exceeding the limit. Sampling is not a kernel hard cap,
so the record will not claim a strict instantaneous memory bound. The exact
arithmetic, inputs, controls, thresholds and interpretation are unchanged.
The replacement run uses a fresh write-once directory and source commit.
