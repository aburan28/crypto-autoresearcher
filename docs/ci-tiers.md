# CI tiers, the merge sweeper and lanes (owner, 2026-10-23)

The three repositories (crypto, crypto-autoresearcher, cryptanalysis) opened
about 1,125 PRs from 2026-10-15 to 2026-10-23, up to about 240 a day, and
runners could not keep up: on 2026-10-23 about 1,000 runs were queued in
crypto. The owner asked to cut PR and CI volume, cap a PR at 30 CI checks and
clear PRs faster. The same mechanism is in all three repositories; crypto's
`.github/CI.md` ("CI tiers") has the measurements.

PRs are opened ready for review by default. A draft, opened only when the user
asks for one, runs the fast tier:

| PR state | What runs on each push |
| --- | --- |
| Draft | Fast tier only: `progress-fidelity.yml` (the required check) and `ci-tier.yml` (`tier-gate`; its `full-tier` job skips) |
| Ready for review | Full tier: every applicable workflow, as before |

- Every other workflow with a `pull_request` trigger gates each job on
  `!github.event.pull_request.draft` and lists `ready_for_review` in its PR
  types (label-only triggers are left alone). `.github/scripts/draft_tier_gate.py`
  checks this in `tier-gate`; `--apply` adds it to a new workflow.
- A gated job on a draft reports `skipped`, so the merge sweeper also requires
  a successful `full-tier` check on the head. Heads whose checks all started
  before `ci-tier.yml` reached `main` predate the tiers.
- **Merge sweeper** (`merge-sweeper.yml`, every 30 minutes; report-only until
  `MERGE_SWEEPER_APPLY=true`): merges green, clean, unblocked PRs with a merge
  commit pinned to the checked head. It holds a PR whose head ran more than 30
  checks (`ci:over-budget`). With apply it labels red, conflicted, over-budget
  and `needs-human` PRs `ci:parked` and PRs beyond the 40-PR prioritization cap
  `ci:waiting`. It never changes whether a PR is a draft: PRs stay open and
  ready for review (owner, 2026-10-24), and the labels clear when the blocker
  does.
- **Lanes:** sessions working one study push to `lane/<lane>` with
  `scripts/lane-push.sh <lane>` (merge commits only, retried, never a
  force-push) instead of opening a PR each.
