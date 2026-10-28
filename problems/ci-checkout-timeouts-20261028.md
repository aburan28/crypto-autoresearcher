# Validation checks cancelled during checkout

- **Status:** investigating
- **Kind:** CI checkout infrastructure; no checker result
- **Affected work:** [PR #2662](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2662) and [PR #2629](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2629)
- **Next action owner:** author of PR #2662
- **Last updated:** 2026-10-28

## Observations

- On `d3f318f07b07f182d7d27e55d3b6448717ee5e0f`, [parity job 122943000500](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40724224301/job/122943000500)
  began an unfiltered depth-one fetch at 16:15:52 UTC and was cancelled at
  16:25:51, before either parity checker ran. The other 18 checks passed.
- On `62dcb2157fa8a405a7cea66246cec86606802def`, [merge-hygiene job 122954669450](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40725112049/job/122954669450)
  finished its blobless history fetch at 16:36:05 UTC, then remained in full
  checkout until cancellation at 16:45:52. The hygiene checker never ran.
  The aggregate `ledger-and-harness` correctly failed for that cancellation.
- Both jobs declare a ten-minute timeout. The timing is consistent with that
  timeout; the log's cancellation message alone does not name the actor.
  Neither cancellation is evidence of a failed theorem or invalid record.

## Repair and prior-source review

[The checkout action's documented sparse checkout and blob filtering inputs](https://github.com/actions/checkout/tree/v4)
provide an existing mechanism to limit downloaded files. The parity checkers
read both skill surfaces and the applicable paths in
`docs/shared-code.lock.json`. The workflow now includes those complete inputs
and plugin targets, and independently checks Git's tracked skill paths and the
lock before running the unchanged checkers. Absent inputs fail the job.

`tools/check_merge_hygiene.py` reads record contents, routing registries,
trusted goal prefixes and base history. Its full checkout and all checks are
preserved; only that job's total CI timeout increases to 30 minutes. The
existing documentation-only sparse classification is unchanged. Experiment
deadlines, proof checks, baselines and branch protection are unchanged.

## Exit criteria and next check

- Validate both parity checkers on the exact new sparse input selection and
  demonstrate that omitting a tracked skill or locked file fails the guard.
- Obtain successful current-head hosted parity and merge-hygiene results.
  A timeout or validation failure needs diagnosis; do not skip a gate or rerun
  merely to obtain green.
- Merge only after every required and applicable current-head check and review
  gate passes. Refresh the dependent review PR after this repair lands.

Local input checks alone cannot establish GitHub network reliability or a
complete hosted validation result. No historical failure is reclassified.

## Local validation

2026-10-28: A fresh detached sparse worktree using the exact workflow selection
contained all 85 tracked skill paths and all seven shared-code inputs. Both
unchanged checkers passed: 31 skills on both surfaces, seven locked files.
Removing a tracked skill and, separately, a locked source file made the input
guard fail; each was restored before the positive check. Hosted results on the
new PR revision remain pending.
