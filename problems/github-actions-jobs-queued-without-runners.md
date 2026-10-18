# GitHub Actions jobs remain queued without runner assignment

- **Status:** `open`
- **Kind:** prolonged infrastructure scheduling delay; assignment resumed; original cause unknown.
- **Affected work:** [PR #2395](https://github.com/aburan28/crypto-autoresearcher/pull/2395), [PR #2396](https://github.com/aburan28/crypto-autoresearcher/pull/2396), the required [progress-fidelity gate](../docs/progress-fidelity.md), and [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml). The separate [harness-test failure](ci-harness-failures-block-icperf-integration.md) remains after runners start.
- **Next action owner:** PR author for runner-eligibility diagnostics and current-head check/merge follow-through; repository owner or GitHub support if account-only diagnostics are needed.
- **Last updated:** 2026-10-18.

## Problem

A prolonged GitHub Actions queue delayed the two ready IC PRs. Runners have now accepted jobs on both PRs, so the initial no-assignment symptom has cleared. Current-head CI is still incomplete on #2395 and failing on #2396; the original scheduling cause is not established. Neither PR currently meets the merge gate. This record does not classify any IC experiment or imply a solver result.

## Evidence and uncertainty

- **Observed:** At 2026-10-18 04:45–04:49 UTC, the GitHub Actions API reported 11 queued workflow runs and zero `in_progress` runs for this repository. [PR #2395 validate run 39098085581](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39098085581) had `changes` job 117588727342 queued with label `ubuntu-latest` and `runner_id: 0`. [PR #2396 validate run 39097372268](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39097372268) had `changes` job 117586753386 in the same state. Both current-head `progress-fidelity` checks were also queued. At least one other queued run, 34748885987, was created 2026-09-13.
- **Observed controls:** `GET /repos/aburan28/crypto-autoresearcher/actions/permissions` returned `enabled: true`, `allowed_actions: all`. GitHub's official status summary reported `Actions operational` at the time of the query. An ordinary cancellation of the obsolete #2395 run 39094226222 left it queued; force-cancelling that obsolete run completed it as `cancelled`. The current-head runs were preserved.
- **Owner report and access limit:** On 2026-10-18, the user reported that Actions quota is available. This is an account-owner statement, not an API receipt from this session. `GET /users/aburan28/settings/billing/actions` returned HTTP 404 with GitHub's message that the token needs the `user` scope. The exact allowance and spending-limit settings remain unavailable to this session, but exhausted quota is no longer the working explanation.
- **Additional observed setting:** `GET /repos/aburan28/crypto-autoresearcher/actions/permissions/workflow` returned `default_workflow_permissions: read` and `can_approve_pull_request_reviews: false`. This setting controls the workflow token; it does not explain a job waiting for a hosted runner. The runner-groups API query did not return parseable data, so runner-group eligibility remains unverified.
- **Observed transition:** By 2026-10-18 05:39 UTC, #2395 current-head `changes` had acquired a GitHub-hosted runner and passed; its `progress-fidelity` job passed. #2396 current-head `changes` and eight further jobs had acquired GitHub-hosted runners and failed, while its `progress-fidelity` job passed. Additional #2395 jobs were still queued at this sample. The obsolete #2395 run 39098085581 reached `completed/cancelled` at 05:29 UTC.
- **Observed #2396 failure cause:** The completed [validate run 39097372268](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39097372268) logs show `changes` executed `Require a complete CI scope decision` before checkout and the scope script, with `SCOPE_RESULT` and `RUN_LEDGER` unset. The job failed immediately; the dependent jobs failed their scope guards. At this branch head, `.github/workflows/validate.yml` places that assertion first. The #2395 branch places it after the scope script and binds both environment values. This is a CI workflow ordering defect in #2396's inherited branch state; no scientific test result can be inferred from those failed guards.
- **Derived or proved:** Runner assignment was absent at the earlier sample and resumed later. The observations do not identify why it was delayed. The #2396 `changes` log identifies the CI scope-ordering failure, subject to a corrected current-head run.
- **Suspected explanation:** The original delay's cause remains unknown. The user reports available quota. Current runner assignment argues against an ongoing account-wide runner ban but does not diagnose the prior delay.
- **Missing capability:** Completed #2395 current-head CI checks, corrected #2396 workflow plus a new current-head CI run, and account or GitHub support evidence only if prolonged unassigned jobs recur.
- **What this evidence does not establish:** It does not show that either PR passes CI, that a queued job may be skipped, or that GitHub's global operational status guarantees this repository can schedule runners.

## What would unblock it

- [x] Observe the exact current-head `changes` and `progress-fidelity` jobs acquire runners. #2395 and #2396 did; both `progress-fidelity` jobs passed, and the #2395 `changes` job passed.
- [ ] Observe all applicable current-head checks reach terminal results. Bring the corrected scope-ordering workflow into #2396 and inspect its fresh run; require all applicable current-head checks to pass or legitimately skip before merging either PR.
- [ ] If prolonged unassigned jobs recur, establish runner eligibility through owner-visible settings, job diagnostics, or GitHub support. The user reports quota available; record any actual cause and authorized remedy.

These conditions would clear the delivery gate only. They would not approve the binary m=8 solver panel, repair the BINSTD certificate-kind records, or establish an end-to-end IC improvement.

## Next discriminating step

- **Action or proof obligation:** Apply the already demonstrated scope-ordering correction to #2396 and validate its fresh run. Check #2395's remaining current-head jobs at spaced intervals. If assignment stalls again, compare runner eligibility and scheduling diagnostics with the exact queued job IDs.
- **Inputs and controls:** Preserve current-head SHA and job ID for each PR; compare the enabled Actions permission, GitHub's service status, in-progress count, and the oldest queued run. A billing denial must be observed directly before changing spend or runner configuration.
- **Execution limits and stop condition:** Read-only status and runner checks; no workflow, branch-protection, or runner bypass. Any spending or shared-runner change requires the applicable authorization.
- **Outcomes and next actions:** If jobs finish, inspect their test outcomes and continue the existing PR repair path. If unassigned jobs persist again, use account diagnostics or GitHub support with exact run and job IDs. Do not infer the prior delay's cause from resumed scheduling.
- **Recheck trigger:** Runner-eligibility answer, a job state transition, or the repository's spaced PR check-in interval.

## Resolution and history

2026-10-18: Opened from GitHub Actions API observations above. Both PRs remain unmerged and the cause remains unknown. Recording this problem does not satisfy the merge gate or a research claim.

2026-10-18 05:39 UTC: The user reported available Actions quota. Runners then appeared in both PRs' job records; #2395 passed `changes` and `progress-fidelity`, while #2396 passed `progress-fidelity` but several other jobs failed. The original scheduling cause remains unknown; the remaining merge gates are CI completion and failure repair.

2026-10-18 05:41 UTC: Read #2396's completed failed logs. Its inherited workflow executes the scope assertion before computing scope. #2395 carries the corrected order. #2396 needs that correction and a fresh CI run; the failed guards do not evaluate the IC artifacts.
