# Bounded completion attempt for two 239-bit twist orders

Frozen 2026-10-23 UTC before this attempt. This is separate from the feature
family in `PROTOCOL.md`; no result of factorization will be retrofitted into
that family's calibrated score.

The prior bounded PARI/GP 20-second probe left the quadratic-twist orders for
published prime239v2 (block 2320) and passed-over block 2682 incompletely
factored. P-224 block 1485 was later completed in
`research/nist_seed_selection_followup_20261016/`. These are the two remaining
cases in that probe.

Read the exact orders and residuals from the pinned `traits.json` input used
by `analyze.py`. For each of these two rows only, call the installed PARI/GP
`factor` with a 128 MiB GP stack and a 300-second process timeout. Record
command, version, stdout, stderr, exit code, elapsed wall time and timeout
status, one immutable output record per row. On returned factors, call GP
`isprime` for each and independently multiply factors back to the exact twist
order. A completed factorization adds a twist diagnostic, not an ordinary
ECDLP advantage or a historical selection rule. A timeout is censored and
leaves the factorization unknown. No parameter tuning or retry belongs to
this round.
