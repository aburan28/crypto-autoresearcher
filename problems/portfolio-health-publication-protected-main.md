# Portfolio health cache publication cannot bypass protected main

- **Status:** investigating; implementation prepared, activation pending
- **Kind:** stale derived status and CI publication failure
- **Affected work:** [main-health workflow](../.github/workflows/main-health.yml),
  [health cache](../coordination/portfolio_health/latest.json),
  [publication helper](../tools/publish_portfolio_health.py)
- **Next action owner:** validation Coordinator for final-head CI and publication;
  repository owner for workflow activation and Actions PR-creation permission
- **Last updated:** 2026-10-28

## Observed state

At 17:12 UTC, GitHub reported `main-health` (workflow 325838011) as
`disabled_manually`. Its last listed runs were cancelled on October 12.
The committed cache is from October 7. The reason for disabling the workflow
is not established by this inspection.

The active main ruleset 25309459 has no bypass actors and requires strict
`progress-fidelity`, `artifacts`, and
`formal workspace (lake build + axiom audit)` checks. The previous publication
step committed the cache and tried three direct pushes to `main`, then emitted
a warning and exited successfully if all pushes failed. That path cannot
satisfy the current review/check requirements, and success did not establish
that a fresh cache had reached main.

The repository's Actions workflow permission response reports
`can_approve_pull_request_reviews: false`; no GitHub App or PAT secret for PR
publication is configured. Only AWS/artifact credentials were listed. No
credential value was read. Pages and Lean verification are already enabled;
the earlier owner approval to enable those workflows did not explicitly name
this separately disabled workflow or the Actions PR permission.

## Repair

The revised workflow retains the generated cache as a run artifact before
publication. It invokes a helper that checks the cache's source SHA, full
history, full checkout, timestamp, goal count, bucket membership and single-file
scope. It creates a uniquely named branch for the source/run/attempt, commits
only the cache, and opens a normal PR. It never writes directly to main,
force-pushes, rebases, approves or merges. A branch collision requires
reconciliation. A failed push or PR request fails the job, with the prepared
commit/branch receipt in the log and the generated artifact retained.

The existing absolute checks continue to report failures. A cache can describe
unhealthy records; opening its PR does not assert that those records are valid.
Normal current-head checks and review still apply to the cache PR.

A small full-diff preflight avoids recursion: only a nonempty diff consisting
exactly of `coordination/portfolio_health/latest.json` suppresses the next
sweep. A mixed change, rename, empty diff or unresolved parent cannot silently
disable validation. A manual dispatch explicitly requests the full sweep.

## Source review

- The prior workflow, `tools/portfolio_health_cache.py`,
  `tools/goal_portfolio_health.py`, the active ruleset, workflow state and
  Actions permission API were inspected before choosing this repair.
- [GitHub's current workflow-trigger documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
  says `GITHUB_TOKEN`-created or updated PRs can create approval-required
  workflow runs. It is not valid to assume that those checks ran or passed.
  A maintainer must approve any pending workflows, then wait for all gates.
- [Actions repository settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
  govern the combined ability to create and approve PRs. This workflow requests
  PR write permission for creation, but contains no review-approval operation.
- [Workflow enable/disable documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows)
  distinguishes enabling future runs from resuming existing ones.

## Validation and limits

The final 20 regression cases passed using synthetic cache fixtures, real
temporary Git repositories and a local bare remote. They check source binding,
shallow/sparse rejection, unrelated staged and unstaged changes, symlink
rejection, bucket/count consistency, an unchanged remote main, exact single-file
commit scope, fatal API failure with retained branch, collision refusal, and
cache-only scope decisions. The GitHub PR API itself is simulated in these
tests; no live cache publication or remote permission claim follows from them.
The artifact-wiring check initially rejected the additional sparse preflight
job because the consuming job pulled coordination artifacts without an explicit
verification step. The consuming job now verifies those artifacts after its
existing pull; the preflight does not read them.

The current real portfolio sweep is already suspended under Conductor T-746
at source `6e86a2ddeb487d37570075af914f54a8824d8d22`, process group 249611.
Another task holds the exclusive memory-heavy slot. This repair does not
launch a replacement, resume that process, change its inputs, or hand-edit its
output. The workflow's existing 20-minute job limit is retained; whether the
current complete hosted sweep fits that limit remains unverified.

## Exit criteria

- [ ] Merge this repair only after all applicable final-head CI and review gates.
- [ ] Obtain the owner's activation decision for the manually disabled workflow
  and the repository's Actions PR-creation setting, after presenting the tested
  implementation and the combined permission's scope.
- [ ] Reconcile the existing suspended sweep and its ownership before launching
  any new sweep. Never replace an interrupted run solely because it is slow.
- [ ] Observe a complete authorized workflow run, retained cache artifact,
  source/hash-bound cache PR, successful current-head checks, reviewed merge and
  committed-cache readback. Preserve any infrastructure or validation failure.
- [ ] Verify downstream status readers use the intended source/timestamp. This
  cache is operational status, not proof of every historical research claim.
