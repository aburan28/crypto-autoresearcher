# ICPERF D6 archive commit is unreachable from main

- **Status:** `resolved` (archive ancestry and dispatcher custody only)
- **Kind:** archive and dispatch integrity gap; repository merge behavior.
- **Affected work:** [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [BATCH-e261c2 correction queue](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/dispatch_queue.correction.json), [TASK-20261011-c65ff7 receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/archives/TASK-20261011-c65ff7/snapshot-receipt.json), [EXP-ICPERF-104054](../experiments/EXP-ICPERF-104054/specification.yaml), and the [full-width IC measurement problem](full-width-ic-arity-grid-unmeasured.md).
- **Next action owner:** Coordinator for the separately authorized `BATCH-e261c2` close sidefile; maintainer for the distinct [premerge-check enforcement problem](pr-merge-checks-not-enforced.md).
- **Last updated:** 2026-10-17

## Problem

The D6 correction lane's dispatcher refused its completed `content_at_commit` snapshot archive because the recorded archive commit `d9ce97fd66d68d85bf613a434e7b7259f63f8998` was absent from `main` ancestry after PR #2084. PR #2363 restored the exact commit through a true merge. This resolves the archive admission obstruction at the checked head; the separately authorized lane-close sidefile records the scheduling closure. The exact protocol and scientific workload have not been evaluated by this custody check.

## Evidence and uncertainty

- **Observed:** `python3 tools/research_dispatch.py coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/dispatch_queue.correction.json --ready-only` exited 2 with `archive task TASK-20261011-c65ff7 declared content_at_commit binding requires archive.commit_sha to be an ancestor of HEAD` on 2026-10-16. `git merge-base --is-ancestor d9ce97fd66d68d85bf613a434e7b7259f63f8998 origin/main` exited 1. The commit object exists locally. [PR #2084](https://github.com/aburan28/crypto-autoresearcher/pull/2084) is marked merged, but its GitHub merge commit `358445cb83e4c5b15a44e8ef448bf91673547401` has one parent, `65aa554a3f2b812fba8f490109e9d6f7afae45f1`. The PR's source history included `d9ce97...`; a one-parent merge commit does not carry that source commit into `main` ancestry.
- **Observed scope of content:** The write-once [snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/archives/TASK-20261011-c65ff7/snapshot-receipt.json) names the archive SHA and six content hashes. Its `dispatch_queue.correction.json` was intentionally revised after the archive to fill in `archive.commit_sha` and the receipt hash, as the receipt's `commit_sha_note` explains; its current bytes differ from the archived queue bytes. That expected revision alone does not prove a scientific artifact mismatch.
- **Historical diagnosis:** The `content_at_commit` ancestry precondition and PR #2084's one-parent merge were incompatible for this receipt. The exact server-side merge setting at the time of PR #2084 remains unverified.
- **Repair evidence:** [DEC-20261017-5cd2f9](../ledger/decisions/DEC-20261017-5cd2f9.yaml) authorized a guarded true merge of the historical commit. PR #2363 landed two-parent merge `d1025248750bca9f336c8a7930398ca9d8c70cf4`, with `d9ce97...` now an ancestor. The current queue SHA-256 is `2033d4eee69b01752a6658550b61ef4f57524a615371e2a6812f76aaf5e61e55`; historical receipt SHA-256 is `af20de9182794d1797ff95588ede833e3c74858325a00bae74c125a078bbce3d`. [The independent control-plane replay](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/repair_verification_20261017.json) and [its snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/archives/TASK-20261017-bda291/snapshot-receipt.json) bind these checks. The dispatcher exited 0 with `ready: 0 task(s); deferred: 0`; both correction tasks are completed and the archive task has a completed release. The snapshot commit `3779f4a3b58476abe6b08a916359917430bb2240` and receipt commit `9ca9ea126280c637a44332b7e78b0661dce77ff1` are reachable from this branch. An independent archive check passed.
- **Process check:** Repeated repository settings reads at the recorded time reported merge commits enabled and squash/rebase disabled. PR #2363 nevertheless merged before Approval, Automation and Security checks completed; their later successes do not cure that gate deviation. The separate [premerge-check enforcement problem](pr-merge-checks-not-enforced.md) stays open.
- **What this evidence does not establish:** It says nothing about D6 wall-channel correctness, factor-base quality, point decomposition, or an index-calculus speedup. A queue refusal is not an experiment outcome.

## What would unblock it

- [x] A Coordinator-approved prospective repair preserved the frozen source bytes and made the exact historical archive commit reachable; the post-commit archive and independent replay checks passed with identified task and record IDs.
- [x] The repaired D6 correction queue's `research_dispatch.py --ready-only --claims refs` exited 0; a separate check established both terminal task states and the archive-task release.
- [x] The repository merge configuration and PR #2363's final two-parent merge were checked. The independent premerge-check issue remains open and is outside this ancestry problem.

Meeting these criteria would restore the lane's custody and scheduling semantics. It would not complete EXP-ICPERF-104054, approve the separate factor-base contract, or establish any scientific claim.

## Next discriminating step

- **Completed discriminating check:** In an isolated branch based on then-current `main`, the Coordinator selected and checked an ancestry-preserving merge against the unchanged D6 receipt, queue and dispatcher. The verified route retained the historical binding, so no superseding archive was needed.
- **Inputs and controls:** The two commits above, PR #2084's commit list, the six receipt hashes, and the unchanged correction queue. Use a clean worktree; do not edit the historical receipt, queue revision, or run artifacts to make a check pass.
- **Execution limits and stop condition:** No scientific trials. Stop if the repair would overwrite a frozen record, lose a declared archive path, or require bypassing a failed gate.
- **Outcome and next action:** [DEC-20261017-cb5e8e](../ledger/decisions/DEC-20261017-cb5e8e.yaml) authorizes the write-once lane-close sidefile after its ledger receipt is verified. Future archival PRs still need their own premerge gate and ancestry check.
- **Recheck trigger:** A later dispatcher refusal on this queue, a content-hash mismatch, or a repository merge-policy regression.

This record is not a protocol approval or a scientific result.

## Resolution and history

- 2026-10-16: Opened after exact local dispatcher refusal, ancestry check, and PR #2084 history inspection. Unresolved.
- 2026-10-17: Resolved the scoped ancestry obstruction with PR #2363's two-parent merge, independently replayed dispatcher and archive receipt, and recorded merge settings. [DEC-20261017-cb5e8e](../ledger/decisions/DEC-20261017-cb5e8e.yaml) separately directs lane closure after its own receipt. PR #2363's early check completion remains an unresolved process deviation in the linked problem.
