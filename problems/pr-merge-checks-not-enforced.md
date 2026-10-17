# PR merge checks are not enforced on main

- **Status:** `open`
- **Kind:** repository governance and CI implementation gap; administrator access/authorization may be needed for the settings change.
- **Affected work:** [AGENTS.md merge rule](../AGENTS.md#concurrency-many-agents-many-worktrees), [mandatory progress-fidelity gate](../AGENTS.md#mandatory-progress-fidelity-gate), [progress-fidelity workflow](../.github/workflows/progress-fidelity.yml), and PRs [#2322](https://github.com/aburan28/crypto-autoresearcher/pull/2322), [#2323](https://github.com/aburan28/crypto-autoresearcher/pull/2323), and [#2324](https://github.com/aburan28/crypto-autoresearcher/pull/2324).
- **Next action owner:** repository administrator for GitHub settings; PR author and reviewer for verifying the restored gate.
- **Last updated:** 2026-10-17 UTC.

## Problem

The repository contract requires the current PR head to have all required and applicable checks complete before merge, and requires `progress-fidelity` CI through branch protection. On 2026-10-17 UTC, three consecutive PRs merged before checks finished. GitHub reported `main` as unprotected, no active repository rulesets, and Actions disabled. The workflow file exists, but these settings do not enforce or run it. A passing check seen after merge does not satisfy the pre-merge rule.

This is a delivery-integrity issue for changes to the ICPERF goal and any other PR on `main`. It does not alter the scientific status of any run or prove an error in the merged content.

## Evidence and uncertainty

- **Observed:** `gh pr view 2322 --json number,mergedAt,mergedBy,statusCheckRollup` reported merge at `2026-10-17T05:52:17Z` by `app/cursor`; Cursor Automation completed at `05:52:36Z` and Cursor Security Agent at `05:55:39Z`.
- **Observed:** the same query for #2323 reported merge at `06:00:56Z` by `app/cursor`; Cursor Automation completed at `06:01:27Z` and Cursor Security Agent at `06:04:32Z`.
- **Observed:** the same query for #2324 reported merge at `06:04:34Z` by `app/cursor`; Cursor Approval Agent completed at `06:05:13Z`, Cursor Automation at `06:05:23Z`, and Cursor Security Agent at `06:09:32Z`.
- **Observed:** `gh api repos/aburan28/crypto-autoresearcher/branches/main` reported `protected: false` and required status checks `enforcement_level: off`, with empty checks and contexts. `gh api 'repos/aburan28/crypto-autoresearcher/rulesets?includes_parents=true'` returned `[]`. `gh api repos/aburan28/crypto-autoresearcher/actions/permissions` reported `enabled: false`. The [workflow source](../.github/workflows/progress-fidelity.yml) declares a `progress-fidelity` job for `pull_request`, but it did not appear in the three PR check rollups.
- **Derived or proved:** the cited check completion timestamps are after their respective merge timestamps. The current branch settings cannot require status checks. The reported Actions setting prevents the repository workflow from running under that setting.
- **Suspected explanation:** the merge automation and absent branch gates together allowed premature merges. Its exact internal trigger and permissions are unverified; inspect its configuration and audit log before assigning a narrower cause.
- **Missing capability:** authorized repository-setting changes and a controlled PR showing the resulting gate in operation.
- **What this evidence does not establish:** it does not establish that the late checks would have failed, that `app/cursor` bypassed an enabled rule, or that all historical PRs had the same timing. The three late checks eventually reported success, but none was complete when its PR merged.

## What would unblock it

- [ ] With repository-administrator authorization, enable Actions for this repository and configure a branch protection rule or ruleset on `main` that requires the exact `progress-fidelity` job context plus every applicable pre-merge check named by the repository contract. Prevent apps and actors that merge PRs from bypassing pending or failed requirements.
- [ ] On a controlled PR, verify the current-head `progress-fidelity` check actually runs, branch protection rejects merge while a required check is pending or failed, and a merge commit succeeds only after all required and applicable checks pass. Record PR URL, head SHA, check-run IDs and timestamps, rule configuration, and merge timestamp.

These conditions would establish enforcement for the tested configuration and PR path. They would not retroactively make earlier merges compliant, validate any scientific claim, or replace review of future changes. Settings may later drift and should be monitored.

## Next discriminating step

- **Action or proof obligation:** inspect the `app/cursor` merge configuration and GitHub audit log, then apply an authorized protection configuration and exercise one controlled PR through pending, failed, and successful required-check states.
- **Inputs and controls:** current `main` rule/Actions settings, the three PR timelines above, the workflow's exact job name, and a PR with an identified current head. Include a negative control where a required check is pending or failing.
- **Execution limits and stop condition:** use a reversible repository-setting change under owner authorization; do not merge the control PR until every applicable check passes. Do not disable or rerun a check to obtain green.
- **Outcomes and next actions:** if pending/failed checks block merges and all required checks run at current head, close this specific gate after an independently inspected receipt. If an app still merges early, inspect bypass permissions and keep the problem open. If Actions or settings cannot be changed, retain the access limit and avoid claiming compliant pre-merge verification. An unavailable check is an infrastructure result, not a success.
- **Recheck trigger:** repository-setting authorization, a new PR merge, or a change to the merge app/ruleset.

A planned step is not a completed test. Repository settings are not changed by this record.

## Resolution and history

Unresolved. This record names an observed delivery-integrity obstruction; merging the record does not repair enforcement. The three source PRs remain merged with their original check timelines intact.
