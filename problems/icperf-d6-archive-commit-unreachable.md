# ICPERF D6 archive commit is unreachable from main

- **Status:** `investigating`
- **Kind:** archive and dispatch integrity gap; repository merge behavior.
- **Affected work:** [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [BATCH-e261c2 correction queue](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/dispatch_queue.correction.json), [TASK-20261011-c65ff7 receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/archives/TASK-20261011-c65ff7/snapshot-receipt.json), [EXP-ICPERF-104054](../experiments/EXP-ICPERF-104054/specification.yaml), and the [full-width IC measurement problem](full-width-ic-arity-grid-unmeasured.md).
- **Next action owner:** Coordinator for a prospective archive/ancestry repair and verified dispatch replay; repository maintainer for the merge-method setting.
- **Last updated:** 2026-10-16

## Problem

The D6 correction lane's dispatcher refuses its completed `content_at_commit` snapshot archive because the recorded archive commit `d9ce97fd66d68d85bf613a434e7b7259f63f8998` is not an ancestor of the current `main` history. The exact protocol and scientific workload have not been evaluated by this check; it is an archive admission failure. This prevents treating the queue as ready, closing the lane from a verified receipt, or using its nominally open capacity as a justification for a third concurrent ICPERF batch.

## Evidence and uncertainty

- **Observed:** `python3 tools/research_dispatch.py coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/dispatch_queue.correction.json --ready-only` exited 2 with `archive task TASK-20261011-c65ff7 declared content_at_commit binding requires archive.commit_sha to be an ancestor of HEAD` on 2026-10-16. `git merge-base --is-ancestor d9ce97fd66d68d85bf613a434e7b7259f63f8998 origin/main` exited 1. The commit object exists locally. [PR #2084](https://github.com/aburan28/crypto-autoresearcher/pull/2084) is marked merged, but its GitHub merge commit `358445cb83e4c5b15a44e8ef448bf91673547401` has one parent, `65aa554a3f2b812fba8f490109e9d6f7afae45f1`. The PR's source history included `d9ce97...`; a one-parent merge commit does not carry that source commit into `main` ancestry.
- **Observed scope of content:** The write-once [snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-e261c2/archives/TASK-20261011-c65ff7/snapshot-receipt.json) names the archive SHA and six content hashes. Its `dispatch_queue.correction.json` was intentionally revised after the archive to fill in `archive.commit_sha` and the receipt hash, as the receipt's `commit_sha_note` explains; its current bytes differ from the archived queue bytes. That expected revision alone does not prove a scientific artifact mismatch.
- **Derived:** The `content_at_commit` ancestry precondition and the one-parent merge are incompatible for this receipt, even if the source files' current contents are otherwise valid. Whether another archive binding or a merge-ancestry restoration is the right repair has not been decided.
- **Suspected explanation:** PR #2084 was squash-merged despite the repository's merge-commit-only archival rule. This is a repository-integrity hypothesis supported by its one-parent merged commit; the exact server-side merge setting at that time has not been independently recovered.
- **Missing capability:** A verified, reachable archive binding for the D6 correction queue and a replay of the dispatcher's admission check from the repaired head.
- **What this evidence does not establish:** It says nothing about D6 wall-channel correctness, factor-base quality, point decomposition, or an index-calculus speedup. A queue refusal is not an experiment outcome.

## What would unblock it

- [ ] A Coordinator-approved prospective repair preserves all frozen source bytes and records a reachable commit containing the exact archival content, or supersedes the binding with a new write-once archive and correction record. The chosen route must pass the repository's post-commit archive verifier and identify the affected task and record IDs.
- [ ] On a clean head containing that repair, the D6 correction queue's `research_dispatch.py --ready-only` completes without an archive-ancestry or content-binding error; a separate check establishes the terminal task state before `goal_lanes.py close-lane` is used.
- [ ] The repository merge configuration and the PR's final merge method are checked so a later archival PR cannot silently repeat the same orphaning. This is a process fix, not a substitute for the repaired receipt.

Meeting these criteria would restore the lane's custody and scheduling semantics. It would not complete EXP-ICPERF-104054, approve the separate factor-base contract, or establish any scientific claim.

## Next discriminating step

- **Action or proof obligation:** In an isolated branch based on current `main`, test an ancestry-preserving repair against the unchanged D6 receipt and dispatcher. Compare it with a prospective superseding archive; choose a route only after exact path hashes and archive-verifier results are recorded.
- **Inputs and controls:** The two commits above, PR #2084's commit list, the six receipt hashes, and the unchanged correction queue. Use a clean worktree; do not edit the historical receipt, queue revision, or run artifacts to make a check pass.
- **Execution limits and stop condition:** No scientific trials. Stop if the repair would overwrite a frozen record, lose a declared archive path, or require bypassing a failed gate.
- **Outcomes and next actions:** A verified reachable binding permits a new Coordinator decision on lane closure and ICPERF scheduling. A content-hash mismatch needs a new correction/archive path. A continued ancestry refusal keeps this problem open and the lane counted as open.
- **Recheck trigger:** A prospective D6 archive repair or repository merge-policy change.

This record is not a protocol approval or a scientific result.

## Resolution and history

- 2026-10-16: Opened after exact local dispatcher refusal, ancestry check, and PR #2084 history inspection. Unresolved.
