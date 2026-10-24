# Joint small-root baseline and executable decomposition remain unverified

- **Status:** investigating
- **Kind:** instrument-accounting defect under independent review; implementation and proof gaps; publication approval limit
- **Affected work:** [small-root lead](../knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coppersmith-smallroot-semaev.yaml); [audit](../research/joint_smallroot_reach_20261024/report.md); the user's reach-cost and verified prime-field IC improvement objective
- **Next action owner:** coordinator; prepared blind review TASK-20261024-da3810 has not been dispatched
- **Last updated:** 2026-10-24

## Problem

We cannot establish a verified improvement of prime-field IC from the proposed
joint small-root method because its historical numerical baseline needs
reconciliation and no independently validated optimized-shift/root-extraction
oracle has been integrated and compared with a frozen IC pipeline.

The exact diagnostic objects are integer S3 with a=2,b=3, its joint four-leaf
tree with xQ=5, and finite triangular shifts. They are not subgroup instances,
random-target trials, or complete DLP solves. The original objective remains
the complete reach-cost tradeoff and a verified improvement over the current
prime-field IC baseline; software checks alone do not meet it.

## Evidence and uncertainty

- **Observed:** the historical `--validate --m 4` command reproduces its 0.8408
  constant and passes its seven univariate calibrations. Its ten tests pass.
  The successor software tests include independent symbolic expansion, exact
  coefficient-matrix determinants, finite row-power enumeration, joint row
  construction, and root-divisibility controls. See the linked report and raw
  diagnostic files for exact revisions and commands.
- **Derived:** N triangular rows with modulus exponent sum q and column
  exponents s_i have determinant p^q times product(X_i^s_i). Divisibility p^t
  gives the determinant-level budget t*N-q. The legacy code uses q. At t=1
  for the 13-column S3 fixture these are 1 and 12 respectively. This is a
  scoped arithmetic/software finding awaiting independent blind review, not
  a closure of any attack family.
- **Missing capability:** an applicable external optimized-shift theorem or
  implementation for the actual joint system; root extraction and its success
  measurements; random-target relation yield/rank; fully charged matched IC
  and rho measurements. The inspected external AsymptoticBounds package
  requires SageMath; its applicability to this joint system is not established
  by reading its README and two source files. The Ryan artifact page returned
  HTTP 403 in this environment; that failure is an access observation only.
- **Publication:** automatic approval review refused the GitHub push as an
  external publication without explicit authorization. No workaround was
  attempted. Local work continued. The repository's independent-dispatch
  rule requires published inputs, so the prepared blind review was not run.
- **What this does not establish:** optimality of the tested shift families,
  impossibility of better decomposition, a validated replacement for 0.8408,
  a root-recovery rate, or an IC speedup. Equal-bound finite volume is not a
  certificate for arbitrary weighted bounds. Dense matrix entry counts are
  structural proxies; they are not actual peak memory or total solver cost.

## What would unblock it

- [ ] Authorize publication of the concrete local branch; publish the snapshot
  and perform the prepared independent derivation before promoting the correction.
- [ ] Reconcile baseline normalization, exact determinant arithmetic, applicable
  shift family, LLL/norm losses, and root-extraction assumptions.
- [ ] Produce a real optimized joint construction, and test its bounds and
  verified root recovery on planted public synthetic instances under a frozen
  executable protocol; state the lattice reduction and memory costs.
- [ ] Integrate the candidate and compare complete cold IC cost on matched
  random-target subgroup instances with a frozen verified IC baseline and the
  matched rho reference. Include misses, duplicates, rank, linear algebra,
  verification, setup, failures, and independent replay.

Meeting the accounting conditions permits a sound experiment; it does not
guarantee an improvement. The last condition is necessary to satisfy the user's
full objective. A stage gain remains scoped to that stage until end-to-end cost
moves.

## Next discriminating step

- **Action:** complete the blind determinant derivation in TASK-20261024-da3810,
  then bind a theorem-backed optimized joint shift construction to this same
  budget convention before selecting a root-recovery panel.
- **Inputs and controls:** exact t=1 S3 coefficient matrix; univariate finite
  and asymptotic controls; historical frozen outputs; three-equation candidate
  matrices; generic-support and actual-coefficient distinctions.
- **Limits:** this session computed finite union-support candidates at t=1..3
  and combinatorial total-degree counts at t=1,2,3,8,16. These are diagnostic
  scope limits, not campaign spending caps. No scientific trial was launched.
- **Outcomes:** agreement qualifies the software accounting; disagreement
  requires an additive correction before any benchmark. A feasible optimized
  construction motivates a frozen recovery test. An unavailable theorem or
  tool remains an implementation/access gap, not negative mathematical evidence.
- **Recheck trigger:** publication authorization or a checked applicable joint
  shift construction/root-extraction implementation.

## Resolution and history

2026-10-24: additive audit and candidate finite accounting prepared locally;
historical code and closure outputs retained. Independent review and the original
pipeline-improvement requirement remain unresolved.
