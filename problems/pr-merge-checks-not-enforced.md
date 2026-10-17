# PR merge checks are not enforced on main

- **Status:** `open`
- **Kind:** repository governance and CI implementation gap; administrator access/authorization may be needed for the settings change.
- **Affected work:** [AGENTS.md merge rule](../AGENTS.md#concurrency-many-agents-many-worktrees), [mandatory progress-fidelity gate](../AGENTS.md#mandatory-progress-fidelity-gate), [progress-fidelity workflow](../.github/workflows/progress-fidelity.yml), and PRs [#2322](https://github.com/aburan28/crypto-autoresearcher/pull/2322), [#2323](https://github.com/aburan28/crypto-autoresearcher/pull/2323), [#2324](https://github.com/aburan28/crypto-autoresearcher/pull/2324), [#2327](https://github.com/aburan28/crypto-autoresearcher/pull/2327), [#2329](https://github.com/aburan28/crypto-autoresearcher/pull/2329), [#2331](https://github.com/aburan28/crypto-autoresearcher/pull/2331), [#2333](https://github.com/aburan28/crypto-autoresearcher/pull/2333), [#2334](https://github.com/aburan28/crypto-autoresearcher/pull/2334), [#2335](https://github.com/aburan28/crypto-autoresearcher/pull/2335), and [#2337](https://github.com/aburan28/crypto-autoresearcher/pull/2337).
- **Next action owner:** repository administrator for GitHub settings; PR author and reviewer for verifying the restored gate.
- **Last updated:** 2026-10-17 UTC.

## Problem

The repository contract requires the current PR head to have all required and applicable checks complete before merge, and requires `progress-fidelity` CI through branch protection. On 2026-10-17 UTC, several PRs merged before checks finished. GitHub reported `main` as unprotected, no active repository rulesets, and Actions disabled. The workflow file exists, but these settings do not enforce or run it. A passing check seen after merge does not satisfy the pre-merge rule.

This is a delivery-integrity issue for changes to the ICPERF goal and any other PR on `main`. It does not alter the scientific status of any run or prove an error in the merged content.

## Evidence and uncertainty

- **Observed:** `gh pr view 2322 --json number,mergedAt,mergedBy,statusCheckRollup` reported merge at `2026-10-17T05:52:17Z` by `app/cursor`; Cursor Automation completed at `05:52:36Z` and Cursor Security Agent at `05:55:39Z`.
- **Observed:** the same query for #2323 reported merge at `06:00:56Z` by `app/cursor`; Cursor Automation completed at `06:01:27Z` and Cursor Security Agent at `06:04:32Z`.
- **Observed:** the same query for #2324 reported merge at `06:04:34Z` by `app/cursor`; Cursor Approval Agent completed at `06:05:13Z`, Cursor Automation at `06:05:23Z`, and Cursor Security Agent at `06:09:32Z`.
- **Observed, later recurrence:** `gh pr view 2327 --json mergedAt,mergeCommit,mergedBy,statusCheckRollup` reported merge at `06:34:33Z` by `app/cursor`; Cursor Automation completed at `06:35:12Z` and Cursor Security Agent at `06:36:46Z`. Both later checks reported success, but both were pending at merge. Its check rollup also lacked `progress-fidelity`.
- **Observed, distinct recurrence:** PR #2329 head `39efd16d4a5a4ad7e3667056bed4c90d635fdf15` merged at `07:00:02Z` as `ce38eab4a68ecc332901cfd0aba6dd64b630a1bf`. Cursor Approval completed `SUCCESS` at `06:56:44Z`, Security completed `SUCCESS` at `06:59:49Z`, and Cursor Bugbot completed `NEUTRAL` at `06:56:32Z` because its usage limit prevented review. This PR did wait for Security, but its rollup had no `progress-fidelity` job and the neutral Bugbot was not a successful review. The record does not establish that Bugbot was a required context.
- **Observed, later recurrences:** PR #2331 merged at `07:09:55Z`; its Cursor Security Agent completed `SUCCESS` at `07:10:02Z`, seven seconds after merge. PR #2333 merged at `07:21:04Z` as `37b04d2b1799170113cfebb05435c69cc124571b`; a `gh pr view` check after merge still showed its Cursor Security Agent `IN_PROGRESS`, while the Approval Agent completed `SUCCESS` at `07:21:35Z`, also after merge. Neither rollup contained `progress-fidelity`. PR #2333 incorporated a reviewer-authored correction to the problem record before merge, but that does not make its pending checks complete.
- **Observed, distinct timing:** PR #2334 merged at `07:31:24Z` as `e77976711749bcfa144b737a9f34b05691f7d840`. Cursor Security completed `SUCCESS` before merge at `07:28:59Z`, while Cursor Automation completed `SUCCESS` at `07:31:39Z`, fifteen seconds after merge. Its rollup again lacked `progress-fidelity`. The record does not establish whether Cursor Automation was a required context, but the repository's own merge rule covers all applicable checks.
- **Observed, later recurrence:** PR #2335 merged at `07:36:29Z` as `ef6d8d5c977361f3512ed331e1f5cde2f4a3bf79`. Cursor Automation completed `SUCCESS` at `07:36:52Z` and Cursor Security completed `SUCCESS` at `07:38:44Z`, both after merge. Its Approval Agent completed `SUCCESS` at `07:35:55Z`, and Bugbot was `NEUTRAL` from a usage limit. The rollup again lacked `progress-fidelity`.
- **Observed, later recurrence:** PR #2337 head `09b0c11580403687dd07b21b6d93308673c20a0f` merged by `app/cursor` at `08:03:05Z` as `b61168fa3b7a5b99b432cc6e1866c1fb9c7c0ea4`. Its Approval Agent and Cursor Automation completed `SUCCESS` before merge, while Cursor Security completed `SUCCESS` at `08:05:24Z`, two minutes and nineteen seconds after merge. The rollup again lacked `progress-fidelity`; Bugbot was `NEUTRAL` from a usage limit.
- **Observed:** `gh api repos/aburan28/crypto-autoresearcher/branches/main` reported `protected: false` and required status checks `enforcement_level: off`, with empty checks and contexts. `gh api 'repos/aburan28/crypto-autoresearcher/rulesets?includes_parents=true'` returned `[]`. `gh api repos/aburan28/crypto-autoresearcher/actions/permissions` reported `enabled: false`. The [workflow source](../.github/workflows/progress-fidelity.yml) declares a `progress-fidelity` job for `pull_request`, but it did not appear in the three PR check rollups.
- **Derived or proved:** the cited check completion timestamps are after their respective merge timestamps. The current branch settings cannot require status checks. The reported Actions setting prevents the repository workflow from running under that setting.
- **Suspected explanation:** the merge automation and absent branch gates together allowed premature merges. Its exact internal trigger and permissions are unverified; inspect its configuration and audit log before assigning a narrower cause.
- **Missing capability:** authorized repository-setting changes and a controlled PR showing the resulting gate in operation.
- **What this evidence does not establish:** it does not establish that the late checks would have failed, that `app/cursor` bypassed an enabled rule, or that all historical PRs had the same timing. The cited late checks eventually reported success, but none was complete when its PR merged. PR #2329 had a different timeline: its Security review passed before merge, while the required progress-fidelity workflow remained unavailable and Bugbot's neutral result did not inspect the diff.

## What would unblock it

- [ ] With repository-administrator authorization, enable Actions for this repository and configure a branch protection rule or ruleset on `main` that requires the exact `progress-fidelity` job context plus every applicable pre-merge check named by the repository contract. Prevent apps and actors that merge PRs from bypassing pending or failed requirements.
- [ ] On a controlled PR, verify the current-head `progress-fidelity` check actually runs, branch protection rejects merge while a required check is pending or failed, and a merge commit succeeds only after all required and applicable checks pass. Record PR URL, head SHA, check-run IDs and timestamps, rule configuration, and merge timestamp.

These conditions would establish enforcement for the tested configuration and PR path. They would not retroactively make earlier merges compliant, validate any scientific claim, or replace review of future changes. Settings may later drift and should be monitored.

## Next discriminating step

- **Action or proof obligation:** inspect the `app/cursor` merge configuration and GitHub audit log, then apply an authorized protection configuration and exercise one controlled PR through pending, failed, and successful required-check states.
- **Inputs and controls:** current `main` rule/Actions settings, the PR timelines above, the workflow's exact job name, and a PR with an identified current head. Include a negative control where a required check is pending or failing.
- **Execution limits and stop condition:** use a reversible repository-setting change under owner authorization; do not merge the control PR until every applicable check passes. Do not disable or rerun a check to obtain green.
- **Outcomes and next actions:** if pending/failed checks block merges and all required checks run at current head, close this specific gate after an independently inspected receipt. If an app still merges early, inspect bypass permissions and keep the problem open. If Actions or settings cannot be changed, retain the access limit and avoid claiming compliant pre-merge verification. An unavailable check is an infrastructure result, not a success.
- **Recheck trigger:** repository-setting authorization, a new PR merge, or a change to the merge app/ruleset.

A planned step is not a completed test. Repository settings are not changed by this record.

## Resolution and history

Unresolved. This record names an observed delivery-integrity obstruction; merging the record does not repair enforcement. The three source PRs remain merged with their original check timelines intact.

2026-10-17 UTC: PR #2327 supplied a fourth observed early merge on the same app path. Its later checks passed, which does not change their pending state at merge time. The enforcement exit criteria remain unmet.

2026-10-17 UTC: PR #2329 merged after Security succeeded, but without an Actions-run `progress-fidelity` job or branch protection; Bugbot was neutral from a usage limit. This is a gate-enforcement recurrence, not another early-Security example.

2026-10-17 UTC: PRs #2331 and #2333 supplied two further early-merge observations. The #2333 review agent corrected one report sentence before merge, while its Approval and Security checks were incomplete at the merge timestamp. The enforcement exit criteria remain unmet.

2026-10-17 UTC: PR #2334 waited for Security but merged before Cursor Automation completed. This timing is recorded separately from the missing required `progress-fidelity` gate.

2026-10-17 UTC: PR #2335 merged while both Automation and Security were pending; their later success does not satisfy the pre-merge gate.

2026-10-17 UTC: PR #2337 merged while Security was pending. Its later success does not repair the early merge or the absent progress-fidelity gate.
