# GitHub Actions runner assignment and account gate block CI

- **Status:** `open`
- **Kind:** historical infrastructure scheduling delay with unknown cause; current explicit account billing or spending-limit denial before runner start.
- **Affected work:** [PR #2395](https://github.com/aburan28/crypto-autoresearcher/pull/2395), [PR #2396](https://github.com/aburan28/crypto-autoresearcher/pull/2396), [validation PR #2453](https://github.com/aburan28/crypto-autoresearcher/pull/2453), [PR #2437](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2437), [PR #2439](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2439), the required [progress-fidelity gate](../docs/progress-fidelity.md), and [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml). The separate [harness-test failure](ci-harness-failures-block-icperf-integration.md) remains after runners start.
- **Next action owner:** account owner for Billing & plans diagnosis and remedy; PR author for current-head check and merge follow-through after jobs start.
- **Last updated:** 2026-10-26.

## Problem

A prolonged GitHub Actions queue delayed the two ready IC PRs. Runners later accepted some jobs on both PRs, but the no-assignment symptom recurred on validation PR #2453. Its current-head downstream checks are queued without runners. The original scheduling cause is not established. No affected PR meets the merge gate solely because a local validation passed. This record does not classify any IC experiment or imply a solver result.

On 2026-10-26, a distinct, explicit account gate prevented every sampled current-head check on #2437 and #2439 from starting. GitHub's check annotation gives two possible account causes: failed recent payments or a spending limit needing an increase. This observation does not identify which setting is responsible, and it does not explain the earlier queue.

## Evidence and uncertainty

- **Observed:** At 2026-10-18 04:45–04:49 UTC, the GitHub Actions API reported 11 queued workflow runs and zero `in_progress` runs for this repository. [PR #2395 validate run 39098085581](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39098085581) had `changes` job 117588727342 queued with label `ubuntu-latest` and `runner_id: 0`. [PR #2396 validate run 39097372268](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39097372268) had `changes` job 117586753386 in the same state. Both current-head `progress-fidelity` checks were also queued. At least one other queued run, 34748885987, was created 2026-09-13.
- **Observed controls:** `GET /repos/aburan28/crypto-autoresearcher/actions/permissions` returned `enabled: true`, `allowed_actions: all`. GitHub's official status summary reported `Actions operational` at the time of the query. An ordinary cancellation of the obsolete #2395 run 39094226222 left it queued; force-cancelling that obsolete run completed it as `cancelled`. The current-head runs were preserved.
- **Owner report and access limit:** On 2026-10-18, the user reported that Actions quota is available. This is an account-owner statement, not an API receipt from this session. `GET /users/aburan28/settings/billing/actions` returned HTTP 404 with GitHub's message that the token needs the `user` scope. The exact allowance and spending-limit settings remain unavailable to this session, but exhausted quota is no longer the working explanation.
- **Additional observed setting:** `GET /repos/aburan28/crypto-autoresearcher/actions/permissions/workflow` returned `default_workflow_permissions: read` and `can_approve_pull_request_reviews: false`. This setting controls the workflow token; it does not explain a job waiting for a hosted runner. The runner-groups API query did not return parseable data, so runner-group eligibility remains unverified.
- **Observed transition:** By 2026-10-18 05:39 UTC, #2395 current-head `changes` had acquired a GitHub-hosted runner and passed; its `progress-fidelity` job passed. #2396 current-head `changes` and eight further jobs had acquired GitHub-hosted runners and failed, while its `progress-fidelity` job passed. Additional #2395 jobs were still queued at this sample. The obsolete #2395 run 39098085581 reached `completed/cancelled` at 05:29 UTC.
- **Observed recurrence:** At 2026-10-22 06:35 UTC, [#2453 validate run 39723809656](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39723809656) remained `queued` at current head `f9f8e37bba038ab8b0f1892bc91c5fc71e62ea48`. Its `changes` job had acquired runner `1000381064` and passed at 06:09 UTC, and `progress-fidelity` passed separately. Nine downstream jobs (merge hygiene, four harness shards, two runtime regression jobs, ledger, static checks) had `status=queued`, `runner_id=0` since 06:09:42 UTC. This proves delayed assignment at that sample, not its cause or a test failure. The [PR check-in](https://github.com/aburan28/crypto-autoresearcher/pull/2453#issuecomment-6334433916) preserves the gate.
- **Observed #2396 failure cause:** The completed [validate run 39097372268](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39097372268) logs show `changes` executed `Require a complete CI scope decision` before checkout and the scope script, with `SCOPE_RESULT` and `RUN_LEDGER` unset. The job failed immediately; the dependent jobs failed their scope guards. At this branch head, `.github/workflows/validate.yml` places that assertion first. The #2395 branch places it after the scope script and binds both environment values. This is a CI workflow ordering defect in #2396's inherited branch state; no scientific test result can be inferred from those failed guards.
- **Observed current account gate:** At 2026-10-26 17:08 UTC, [#2437 current-head `changes` job 121723050279](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40365805859/job/121723050279) on `c27d7222d89cac0f792f66945636e198b09878fb` completed `FAILURE` without starting. At 17:12 UTC, [#2439 current-head `progress-fidelity` job 121725154170](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40366394470/job/121725154170) on `3df853b75c0a8d20bf84ca8f776d9fcdb6d387fc` did the same. Both check-run annotations say: "The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings". The 2026-10-18 owner report of available quota does not determine the 2026-10-26 billing state. Neither check evaluated the code or progress-fidelity record.
- **Derived or proved:** Runner assignment was absent at the earlier sample and resumed later. The observations do not identify why it was delayed. The #2396 `changes` log identifies the CI scope-ordering failure, subject to a corrected current-head run. The later #2437/#2439 denial is an explicit account gate, with its two alternatives unresolved.
- **Suspected explanation:** The original delay's cause remains unknown. The current account gate may be payment status or spending limit; this session cannot distinguish them from the check annotation.
- **Missing capability:** Account-owner Billing & plans diagnosis and remedy, followed by completed current-head CI checks on #2437/#2439. Corrected #2396 workflow and runner-eligibility diagnostics for the older #2453 queue remain separately open.
- **What this evidence does not establish:** It does not show that either PR passes CI, that a queued job may be skipped, or that GitHub's global operational status guarantees this repository can schedule runners.

## What would unblock it

- [x] Observe the exact current-head `changes` and `progress-fidelity` jobs acquire runners. #2395 and #2396 did; both `progress-fidelity` jobs passed, and the #2395 `changes` job passed.
- [ ] Observe all applicable current-head checks reach terminal results. Bring the corrected scope-ordering workflow into #2396 and inspect its fresh run; require all applicable current-head checks to pass or legitimately skip before merging either PR.
- [ ] Observe the nine #2453 current-head downstream jobs acquire runners and finish; inspect any actual failure before deciding whether #2453 can merge.
- [ ] If prolonged unassigned jobs recur, establish runner eligibility through owner-visible settings, job diagnostics, or GitHub support. The user reports quota available; record any actual cause and authorized remedy.
- [ ] Have the account owner inspect Billing & plans for the exact current denial on #2437/#2439 and correct the payment or spending-limit condition. Then obtain fresh, applicable current-head checks and inspect their real results before either PR merges.

These conditions would clear the delivery gate only. They would not approve the binary m=8 solver panel, repair the BINSTD certificate-kind records, or establish an end-to-end IC improvement.

## Next discriminating step

- **Action or proof obligation:** Apply the already demonstrated scope-ordering correction to #2396 and validate its fresh run. Check #2395 and #2453 current-head jobs at spaced intervals. If assignment stalls again, compare runner eligibility and scheduling diagnostics with the exact queued job IDs.
- **Inputs and controls:** Preserve current-head SHA and job ID for each PR; compare the enabled Actions permission, GitHub's service status, in-progress count, and the oldest queued run. A billing denial must be observed directly before changing spend or runner configuration.
- **Execution limits and stop condition:** Read-only status and runner checks; no workflow, branch-protection, or runner bypass. Any spending or shared-runner change requires the applicable authorization.
- **Outcomes and next actions:** If jobs finish, inspect their test outcomes and continue the existing PR repair path. If unassigned jobs persist again, use account diagnostics or GitHub support with exact run and job IDs. Do not infer the prior delay's cause from resumed scheduling.
- **Recheck trigger:** Runner-eligibility answer, a job state transition, or the repository's spaced PR check-in interval.
- **Current-denial control:** Do not rerun unchanged jobs while the account gate persists. After an owner-confirmed account change, obtain current-head checks through the normal GitHub Actions route and inspect any code failure separately. An account fix clears only the runner-start gate.

## Resolution and history

2026-10-18: Opened from GitHub Actions API observations above. Both PRs remain unmerged and the cause remains unknown. Recording this problem does not satisfy the merge gate or a research claim.

2026-10-18 05:39 UTC: The user reported available Actions quota. Runners then appeared in both PRs' job records; #2395 passed `changes` and `progress-fidelity`, while #2396 passed `progress-fidelity` but several other jobs failed. The original scheduling cause remains unknown; the remaining merge gates are CI completion and failure repair.

2026-10-18 05:41 UTC: Read #2396's completed failed logs. Its inherited workflow executes the scope assertion before computing scope. #2395 carries the corrected order. #2396 needs that correction and a fresh CI run; the failed guards do not evaluate the IC artifacts.

2026-10-22 06:35 UTC: #2453's current-head validate run had one successful `changes` job and nine downstream jobs queued with no runner. The scheduling cause remains unknown; hosted checks cannot yet certify the local validation report.

2026-10-26 17:08–17:12 UTC: Exact current heads of #2437 and #2439 received GitHub check-run annotations denying job start for payment or spending-limit reasons. This is a new observed account gate, not a retrospective diagnosis of the October 18 or October 22 queues. Both PRs remain subject to required current-head checks.
