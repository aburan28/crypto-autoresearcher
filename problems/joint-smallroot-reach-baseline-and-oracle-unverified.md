# Joint small-root baseline and executable decomposition remain unverified

- **Status:** investigating
- **Kind:** historical instrument accounting discrepancy; optimized-oracle implementation and proof gaps; admission and CI gates
- **Affected work:** [small-root lead](../knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coppersmith-smallroot-semaev.yaml); [audit](../research/joint_smallroot_reach_20261024/report.md); the user's reach-cost and verified prime-field IC improvement objective
- **Next action owner:** Coordinator task TASK-20261025-b7e32e in disjoint BATCH-3cfef2; prepare the exact weighted joint applicability and experiment-contract preview, with no scientific execution
- **Last updated:** 2026-10-25

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
  scoped arithmetic/software finding with a completed independent mathematical
  derivation and separate parent implementation comparison, not a closure of
  any attack family.
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
  The user subsequently authorized publication; the branch is now in
  [PR #2547](https://github.com/aburan28/crypto-autoresearcher/pull/2547), and the
  prepared blind review has been dispatched. Auto-merge was separately refused
  as outside the publication authorization; the PR remains open.
- **Independent derivation:** [TASK-20261024-da3810](../research/joint_smallroot_reach_20261024/independent-review.md)
  independently derives K=tN-q, the full-box equal-beta determinant limit, and
  the exact 13-column S3 determinant. It did not inspect the producer code or
  artifacts and therefore returns inconclusive on implementation compatibility.
  The [parent addendum](../research/joint_smallroot_reach_20261024/review-20261024/report.md)
  compares the matching finite fixture and keeps this separate from a global
  implementation, optimized-shift, root-extraction or pipeline validation.
- **What this does not establish:** optimality of the tested shift families,
  impossibility of better decomposition, a validated replacement for 0.8408,
  a root-recovery rate, or an IC speedup. Equal-bound finite volume is not a
  certificate for arbitrary weighted bounds. Dense matrix entry counts are
  structural proxies; they are not actual peak memory or total solver cost.

## What would unblock it

- [x] Authorize publication of the concrete local branch and publish the snapshot.
- [x] Perform the prepared independent mathematical derivation; no scientific-state promotion is made.
- [x] Independently derive the finite determinant budget, exact fixture and LLL/norm correction.
- [ ] Reconcile the optimized joint weighted-bound normalization, applicable
  shift family, charged threshold and root-extraction assumptions.
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

- **Action:** use the completed blind determinant derivation in TASK-20261024-da3810
  to bind a theorem-backed optimized joint shift construction to this same budget
  convention before selecting a root-recovery panel.
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
- **Recheck trigger:** completion and verified archival of the published zero-run
  design task TASK-20261025-b7e32e; a checked applicable weighted joint shift
  construction/root-extraction implementation; owner-first shared artifact-tool
  parity and completion of current-head hosted merge checks.

## Resolution and history

2026-10-24: additive audit and candidate finite accounting prepared locally;
historical code and closure outputs retained. Independent review and the original
pipeline-improvement requirement remain unresolved.

2026-10-24 publication continuation: user authorization received; exact branch
history pushed and PR #2547 opened. Prepared independent review dispatched against
published inputs. Auto-merge remains approval-blocked; this is separate from the
mathematical and implementation obligations.

2026-10-24 review continuation: independent mathematical derivation and exact
arithmetic fixture returned. Parent source comparison is recorded separately in
the addendum. No optimized-shift certificate, joint root extraction, scientific
state transition, or verified IC improvement is established.

2026-10-25 readiness continuation: the user explicitly authorized merge, so
the previous approval impediment is resolved. Artifact-policy and draft-tier
CI defects were repaired without weakening enforcement; the artifact workflow
passes and the other applicable checks remain pending. No merge has occurred.
The [new report](../research/joint_smallroot_reach_20261024/readiness-20261025/report.md)
and [PDF](../research/joint_smallroot_reach_20261024/readiness-20261025/report-compact.pdf)
derive the weighted conditional cost model from the archived finite counts.
These three certificate regions do not meet that model's sub-rho condition;
this is not an impossibility claim about improved shifts. The pinned cuso
implementation runs its documented univariate calibration at delta*=1/3.
Its optimal-shift implementation uses Gröbner preprocessing, so bypassing all
such costs has not been established. No joint solver trial was launched.
Two host-goal lanes are already open and an independent Coordinator runtime
receipt remains unavailable in this session. Full-ledger validation reports
106 errors outside the audit's changed paths; no historical records or
validation baselines were altered. The optimized joint oracle and matched
complete IC comparison remain the scientific gaps.
The direct authenticated Codex readiness check exits before initialization
with a read-only filesystem error, as recorded in the
[operational follow-up](../research/joint_smallroot_reach_20261024/readiness-20261025/operational-followup.md).
Two newly inherited main workflows also needed the existing draft-tier guards;
the local checker now reports zero uncovered workflows.

2026-10-25 coordination correction: the failed nested CLI did not establish
that the authenticated managed native Coordinator was unavailable. The
repository's documented native runtime alternative is now in use, with actual
model selection and authentication provenance recorded without claiming an API
catalog probe or an unrelated CLI receipt. Two open lanes also did not establish
two active workers: the inspected producer claims have completed releases.
After full history and historical blobs were fetched, targeted health reports
the old PFDR archive task ready; its earlier missing-artifact report was not
proved queue corruption. No existing lane was closed or taken over.

The new disjoint zero-run design lane BATCH-3cfef2 is registered and
TASK-20261025-b7e32e is published and claimed in
[PR #2557](https://github.com/aburan28/crypto-autoresearcher/pull/2557), under
DEC-20261025-fe4f22. It specifies the first joint workload and applicability
obligations prospectively. It does not approve a scientific trial or resolve the
optimized oracle and matched IC comparison gaps. The audit PR additionally
needs the artifact-tool fix to land in its owning `crypto` repository and mirror
consistently; the exact patch is prepared, but the owner workflow's Conductor
tool is absent here and no owner code was edited. See the
[operational correction](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/setup/additive-operational-correction.md).
