# Additive correction before arithmetic

The first launch in `attempt1.log` failed while recording the GP version, before
running any factorization. The GP banner is on stderr on this host. `run.py`
now captures both streams and selects the version line by its prefix. The
original run directory remains untouched. The next run uses a distinct path
and the fixed first-stage curve list, controls, limits, and decision policy in
`PROTOCOL.md`. This correction changes no tested mathematical condition.
