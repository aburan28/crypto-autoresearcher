# m=51 four-level native-rho benchmark (frozen, unlaunched)

This directory contains the frozen rigorous follow-on to the m=51 deep endpoint
discovery.  The sealed full-range discovery output has been bound into
`deep_selection.json`, and the exact benchmark inputs are committed and covered
by `FROZEN.sha256`.  The benchmark remains **unlaunched** at this freeze point:
there is no admitted deep-endpoint timing, weak-curve finding, or
conductor-causality result in this tree yet.

The prospective plan uses 32 selected P/B edge pairs, all 16 conductor-271 orbits,
all deep Frobenius conjugates, one common native negation action, 12,288
inferential solves, and 8,192 held-out A/A solves.  The single endpoint family
has six pairwise and three predeclared lattice contrasts with delete-one-pair
jackknife and per-draw re-studentized Rademacher max-|T| inference.  The report
also exposes `2I` as the ordinary difference-in-differences, without adding it
as a tenth hypothesis.

For every selected P/B edge, the same Frobenius exponent is applied to the
certified raw `parent_b` and raw `bottom_b`.  The canonical
`bottom_orbit_rep` remains the population identity; it is not substituted for
the raw child coefficient.  Scalar and numeric walk streams are shared across
all four arms as paired common-random-number controls.  This is an explicit
pre-freeze amendment superseding the nonfrozen blueprint's arm/domain-separated
walk streams; each curve still constructs its points and executes its walk
natively.

Calibration matters to interpretation: although rows share stochastic inputs,
only `B-P` has exactly matched target weights in the calibrated estimators.
Other contrasts are balanced CRN comparisons.  Equal-row-weight sensitivity
and per-pair/per-model heterogeneity are descriptive only.  The finite
selected-32 result likewise receives a point estimate and descriptive
distribution, not a selected-set confidence interval.

If the A/A gate passes, the primary family is estimable, and any of the nine
simultaneous 95% intervals strictly excludes zero with `|estimate| >= 0.5` bit,
a conditionally mandatory fixed-panel setup lane runs in the same admitted
execution, after the primary phase has been independently sealed.  It contains
16 fresh inferential setup roots plus the original primary root as a
noninferential matched bridge, 32 blocks and four arms (2,176 solves), uses a
97-distinct-model panel, and enumerates all `2^16` fresh-root sign vectors.  Its
95% critical rank is 62,260 and its exhaustively enumerated
multiplier-reference adjusted p-values use `count/65,536`; this removes Monte
Carlo error but is not exact finite-sample randomization inference.  Conditional
on the frozen SHA-derived-root exchangeability/sign-symmetry model, its n=16
intervals assess directional and practical persistence.  The bridge is
descriptive only.  The sparse fixed-panel/fresh-stream estimand differs from the
calibrated primary estimand, so non-persistence cannot uniquely diagnose the
original setup root and establishes no security weakness, conductor causality,
or transfer.
One conditional attempt is allowed.  A failure preserves the sealed primary as
`primary_complete_robustness_failed` but leaves the mandatory persistence lane
incomplete; it is never resumed or backfilled.  Completed execution with a
non-estimable family is instead sealed as
`primary_complete_robustness_non_estimable` and receives no persistence label.

An admitted runner cross-checks fixed literal scalar/walk RNG vectors between
Python and the compiled C adapter, requires a static ELF with neither
`PT_INTERP` nor `PT_DYNAMIC`, gives children an exact sanitized environment,
and uses Linux subreaper/process-group cleanup with bounded pipe draining.
Post-seal interruption recovery trusts only a freshly reverified on-disk phase
manifest and its bound artifacts, never an in-memory completion flag.
Scientific runner and analyzer entry points require `-I -B` under the exact
empty-then-populated environment in the protocol; analysis loads the verified
run-local frozen source rather than mutable worktree code.
Receipts bind the exact Python command/environment plus Python, NumPy, and
mapped numerical-backend identities and hashes.

Read [`PROTOCOL.md`](PROTOCOL.md) for the full design and
[`TRANSFER_BOUNDARY.md`](TRANSFER_BOUNDARY.md) for what this benchmark cannot
establish.  Endpoint binding and the input freeze are complete; the next
admissible action is the single prespecified scientific execution.
