# Amendment 1 (additive; PROTOCOL.md unchanged)

Written 2026-10-05 after the main analysis and before any amendment data.

## Why
Pre-declared test H2 (seconds) failed the +-3% equivalence margin: lower levels
measured 1.4-3.3% *faster* than the crater in wall-clock time, while step
counts (H2 ops) and the pinned per-step benchmark were equivalent. Breaking
time into ns per group op by chunk shows equal medians at every level
(624-629 ns) and load spikes in individual chunks (up to 1098 ns/op). Three of
the crater's ten chunks were hit (737/900/742 ns/op). A repository `git fetch`
ran concurrently with part of the solve phase. That is an environmental
confound; the main-run seconds data is kept as recorded, not edited or dropped.

## Timing re-test (pre-declared)
- Curves: the crater (negation only and Frobenius) plus the two lowest-id
  curves of each lower level (ids 1, 2, 101, 102, 201, 202).
- 2000 solves per curve-mode, in 20 rounds of 100, round-robin across
  curve-modes, sequential on one pinned core (CPU 0), with no other user
  process running. Seeds 500000 + 100*id + 10*mode + round.
- Test: TOST, mean seconds per solve of each lower level (its two curves
  pooled) vs the crater with negation only, margin +-3%, 90% bootstrap CI.
  Also reported: ns per group op (sum sec / sum ops) per level.
- The H2-seconds verdict in the report is this re-test; the main-run figure is
  reported next to it with the confound stated.
