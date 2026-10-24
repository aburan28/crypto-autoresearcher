# Additive correction before arithmetic

The first launch in `attempt1.log` failed while recording the GP version, before
running any factorization. The GP banner is on stderr on this host. `run.py`
now captures both streams and selects the version line by its prefix. The
original run directory remains untouched. The next run uses a distinct path
and the fixed first-stage curve list, controls, limits, and decision policy in
`PROTOCOL.md`. This correction changes no tested mathematical condition.

The second launch in `attempt2.log` failed before GP started because this
Darwin host rejects a 2 GiB `RLIMIT_AS` cap (`setrlimit: invalid argument` was
confirmed separately with `zsh ulimit -v`). The exact source and frozen case
list were preserved. Before a third launch, the resource rule is amended from
an address-space cap to a 1 GiB GP arithmetic stack and a 2 GiB sampled RSS
watchdog that kills the child on exceedance. The 180-second wall limit is
unchanged. This controls host memory without claiming an OS-enforced virtual
address cap. The failed second directory remains untouched.
