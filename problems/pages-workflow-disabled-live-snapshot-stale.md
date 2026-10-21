# Pages workflow disabled and live dashboard snapshot stale

- **Status:** `open`
- **Kind:** deployment configuration and publication-state gap; reason for manual disable is unknown
- **Affected work:** [public dashboard](https://aburan28.github.io/crypto-autoresearcher/), [Pages workflow](../.github/workflows/pages.yml), and [2026-10-21 local dashboard audit](../docs/reports/2026-10-21-ledger-integrity-audit/report.md)
- **Next action owner:** repository owner or Pages maintainer for workflow state and deployment approval
- **Last updated:** 2026-10-21

## Problem

The local dashboard can build, but the public site is not current. On
2026-10-21 UTC, GitHub reported `.github/workflows/pages.yml` as
`disabled_manually`; the public `data/meta.json` identified commit
`bb9e9f01f3f9fcdf6e456acd7e01cd9af6c05bc3` built on
2026-10-11T16:20:19Z. A complete local build on 2026-10-21 at
`46d5a90bcdf1e13f449604eed118b69e9b7071ef` produced 55,218 files and
the current nine-row comparison payload. The reason the workflow was
disabled is unknown. A local build does not update the public dashboard.

## Evidence and uncertainty

- **Observed:** The [read-only state check](../docs/reports/2026-10-21-ledger-integrity-audit/evidence/live-pages-status.json)
  records the GitHub workflow state and the public site's metadata bytes.
  GitHub Actions is enabled for the repository and Pages reports
  `build_type: workflow`; the named workflow is manually disabled. Its most
  recent listed runs were cancelled on 2026-10-12. The [local build report](../docs/reports/2026-10-21-ledger-integrity-audit/evidence/site-build-report.json)
  and [payload check](../docs/reports/2026-10-21-ledger-integrity-audit/evidence/site-payload-check.json)
  record successful local generation, nine benchmark rows, and 24 reader
  parse warnings.
- **Derived or proved:** The live metadata commit differs from the locally
  validated commit. This is a snapshot-freshness fact, not a statement that
  any archived benchmark number is wrong.
- **Suspected explanation:** Unknown. Manual disable could be intentional;
  this audit found no documented reason to treat it as accidental.
- **Missing capability:** A reviewed decision about re-enabling publication,
  followed by a successful hosted Pages build/deploy and live readback.
- **What this evidence does not establish:** It does not show that Pages
  hosting is unavailable, that a new deployment will pass, or that all
  scientific records are validated. The separate full-ledger gate is red.

## What would unblock it

- [ ] Confirm the repository owner's intended Pages publication state and
  resolve the reason for `disabled_manually` before changing workflow state.
- [ ] After authorization and a reviewed current-head change, run the Pages
  workflow to a successful build and deploy, then read back public
  `data/meta.json` and require its commit to match the published main commit.
- [ ] Check the live `data/comparisons.json` for nine pinned primary rows and
  no benchmark error, and display any integrity warnings with their actual
  scope. Do not call a successful deployment a scientific validation.

These conditions would make the hosted reader current and honest. They would
not clear the [162 unsuppressed ledger errors](full-ledger-validation-errors.md),
complete Lean semantic reviews, or replay historical performance.

## Next discriminating step

- **Action or proof obligation:** Inspect the intended workflow state with
  the owner; prepare the exact re-enable and hosted build/deploy action for
  review once the audit and branch checks are available.
- **Inputs and controls:** The current Pages settings, disabled workflow
  state, source commit, successful local build, and live metadata readback;
  compare the hosted payload against the pinned nine-row source and retain
  any failed build log.
- **Execution limits and stop condition:** Do not infer approval from a local
  build. Stop before external publication if approval or required checks are
  missing; keep the current site state explicit.
- **Outcomes and next actions:** A successful current-head deploy closes the
  freshness gap; a failed hosted build yields a specific CI problem; an
  intentional disable remains open until the owner changes direction.
- **Recheck trigger:** Owner publication decision, workflow-state change, or
  a new hosted Pages run and live metadata commit.

## Resolution and history

- 2026-10-21: Opened from a read-only GitHub workflow-state query, public
  metadata fetch, and successful local build. No workflow setting, site, or
  research state changed. Unresolved.
