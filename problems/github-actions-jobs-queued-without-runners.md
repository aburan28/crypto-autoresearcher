# GitHub Actions jobs remain queued without runner assignment

- **Status:** `open`
- **Kind:** infrastructure scheduling gap; cause unknown; billing visibility limit.
- **Affected work:** [PR #2395](https://github.com/aburan28/crypto-autoresearcher/pull/2395), [PR #2396](https://github.com/aburan28/crypto-autoresearcher/pull/2396), the required [progress-fidelity gate](../docs/progress-fidelity.md), and [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml). The separate [harness-test failure](ci-harness-failures-block-icperf-integration.md) remains after runners start.
- **Next action owner:** Repository owner for Actions billing/runner eligibility visibility; PR author for current-head check and merge follow-through.
- **Last updated:** 2026-10-18.

## Problem

The two ready IC PRs cannot meet the repository's current-head check requirement while GitHub Actions leaves their `ubuntu-latest` jobs queued without runner assignment. The cause is not established. This prevents a compliant merge; it does not classify any IC experiment or imply a solver result.

## Evidence and uncertainty

- **Observed:** At 2026-10-18 04:45–04:49 UTC, the GitHub Actions API reported 11 queued workflow runs and zero `in_progress` runs for this repository. [PR #2395 validate run 39098085581](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39098085581) had `changes` job 117588727342 queued with label `ubuntu-latest` and `runner_id: 0`. [PR #2396 validate run 39097372268](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39097372268) had `changes` job 117586753386 in the same state. Both current-head `progress-fidelity` checks were also queued. At least one other queued run, 34748885987, was created 2026-09-13.
- **Observed controls:** `GET /repos/aburan28/crypto-autoresearcher/actions/permissions` returned `enabled: true`, `allowed_actions: all`. GitHub's official status summary reported `Actions operational` at the time of the query. An ordinary cancellation of the obsolete #2395 run 39094226222 left it queued; force-cancelling that obsolete run completed it as `cancelled`. The current-head runs were preserved.
- **Access limit:** `GET /users/aburan28/settings/billing/actions` returned HTTP 404 with GitHub's message that the token needs the `user` scope. Available Actions minutes and spending-limit state therefore remain unknown to this session.
- **Derived or proved:** Runner assignment has not occurred for the named jobs at the sampled times. The observations do not identify whether billing, account restrictions, GitHub scheduling, or another condition caused the queue.
- **Suspected explanation:** Unknown. An exhausted private-repository Actions allowance is one possibility, not a diagnosis; owner-visible billing state would discriminate it from other causes.
- **Missing capability:** Runner assignment and completed current-head CI checks, plus owner-visible billing or GitHub support evidence if the queue persists.
- **What this evidence does not establish:** It does not show that either PR passes CI, that a queued job may be skipped, or that GitHub's global operational status guarantees this repository can schedule runners.

## What would unblock it

- [ ] Establish the repository/account's GitHub-hosted runner eligibility, including Actions minutes and spending-limit state, through owner-visible settings or GitHub support. Record the actual cause and any authorized remedy; do not infer it from queue duration.
- [ ] Observe the exact current-head `changes` and `progress-fidelity` jobs acquire runners and reach terminal results. Repair any failed applicable checks, then require all applicable current-head checks to pass or legitimately skip before merging either PR.

These conditions would clear the delivery gate only. They would not approve the binary m=8 solver panel, repair the BINSTD certificate-kind records, or establish an end-to-end IC improvement.

## Next discriminating step

- **Action or proof obligation:** Check owner-visible Actions billing/allowance and runner eligibility for this repository, then compare that state with the named queued jobs. The PR author checks the same run IDs at spaced intervals.
- **Inputs and controls:** Preserve current-head SHA and job ID for each PR; compare the enabled Actions permission, GitHub's service status, in-progress count, and the oldest queued run. A billing denial must be observed directly before changing spend or runner configuration.
- **Execution limits and stop condition:** Read-only status and billing checks; no workflow, branch-protection, or runner bypass. Any spending or shared-runner change requires the applicable authorization.
- **Outcomes and next actions:** If allowance is exhausted, prepare an explicit cost and configuration remedy for approval. If allowance exists, use GitHub's job state and support diagnostics to isolate scheduling. If jobs start, inspect their actual test outcomes and continue the existing PR repair path. An inaccessible billing view leaves the cause unknown.
- **Recheck trigger:** Billing/runner-eligibility answer, a job state transition, or the repository's spaced PR check-in interval.

## Resolution and history

2026-10-18: Opened from GitHub Actions API observations above. Both PRs remain unmerged and the cause remains unknown. Recording this problem does not satisfy the merge gate or a research claim.
