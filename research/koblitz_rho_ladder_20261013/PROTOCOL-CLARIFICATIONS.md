# Frozen-protocol clarifications

Recorded 2026-10-13 after launch and before analysis. These are non-outcome
editorial/accounting clarifications; the grid, samples, seeds, estimands,
bootstrap, and stopping rule did not change.

1. In `PROTOCOL.md`, “the largest selected prime subgroup has at least 20
   bits” should read “every selected prime subgroup has at least 20 bits.”
   The smallest is the `(a=0,m=31)` cell at about 20.46 bits.
2. The high-cofactor stress points are not limited to `m=31`. The frozen
   cells have cofactors 4, 2, 1492, 596, 4, 1894, and 1318 in spec order.
   This does not invalidate a within-prime-subgroup comparison, but it makes
   field degree a deliberately imperfect proxy for subgroup size. Both are
   reported.
3. `counters.walks_capped` counts local trails that hit a per-trail cap and
   restart; a verified overall solve may contain such restarts. These events
   are retained and summarized. The invalidating condition in the frozen
   protocol is an overall timeout, exhaustion, or non-verified solve.
4. Signed-Frobenius and negation counted-GAE values each omit differently
   numerous canonicalisations. Their ratio is therefore a ratio of recorded
   counts, not itself a lower or upper bound on the fully priced cost ratio.
5. The producer session records the binary SHA-256 but this local build did
   not embed Git metadata (`git_commit` and `git_dirty` are null). The source
   revision and clean-worktree observation are preserved as external build
   provenance and must not be described as session-sealed Git metadata.
