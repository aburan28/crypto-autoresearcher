# Coordinator defect: the notarization archive's receipt rides outside the commit it describes

Recorded 2026-08-11 by the Coordinator adjudicating BATCH-9e3584.
Adjudication: `../../COORDINATOR-ADJUDICATION-20260811.md`.
Sibling defect: `../TASK-20260809-4d928d/COORDINATOR-DEFECT.md`.

This file records a defect in **archive bookkeeping**. It adjudicates no
scientific proposition, moves no hypothesis, and promotes nothing. Claim tier
stays TOY.

## 1. What the contract required

`TASK-20260809-91cf76` is a snapshot archive with
`archive.source_task_ids = [TASK-20260809-4011dd]`.
`tools/research_dispatch.py:564` computes its binding set as

```
expected_paths = archive_task.artifact_paths  UNION  source.artifact_paths
```

which for this task is exactly **three** paths:

1. `coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-4011dd/prereg.md`
2. `coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-4011dd/prereg_sha256.txt`
3. `coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260809-91cf76/snapshot-receipt.json`

`GitRepositoryVerifier.verify_archive` (`tools/research_dispatch.py:1073-1089`)
requires the declared commit to change **exactly** that set — no more, no fewer.
The receipt must therefore ride in the same commit as the artifacts it declares.

## 2. What was committed instead

Reported by the harness-driving session that ran the commands; I hold no shell
and did not re-run git. Commit shas and parents are as recorded in the immutable
`snapshot-receipt.json` beside this file.

| commit | changes | receipt inside? |
| --- | --- | --- |
| `1aa7db53` (parent `3d5dd80a`) | exactly the 2 pre-registration files | no |
| `c034ef38` | exactly the 28 producer files | no |
| `502d15a0` | both snapshot receipts + `dispatch_queue.json` | (both receipts, no sources) |

So the binding set of three paths is split across `1aa7db53` (paths 1, 2) and
`502d15a0` (path 3). No single commit changes exactly the declared set, and the
strict-binding branch of the verifier refuses.

### Two distinct defects, and only the second is terminal

- **D1, incomplete bookkeeping.** `dispatch_queue.json` still carries
  `archive.commit_sha: null`, `archive.parent_sha: null`, `archive.path_sha256: {}`
  for this task, although the committed receipt carries all three. That is why
  the observed failure is `completed archive task TASK-20260809-91cf76 requires
  archive.commit_sha`, raised at `research_dispatch.py:572-576` **before git is
  consulted at all**. D1 on its own would be trivially repairable by copying the
  committed receipt's fields into the queue.
- **D2, structural and terminal.** Fill the queue honestly and the verifier gets
  further and then fails harder, at `research_dispatch.py:1086` with
  `missing ['.../archives/TASK-20260809-91cf76/snapshot-receipt.json']`. That is
  the real defect, and section 4 shows it cannot be repaired.

I verified D1 and the path arithmetic myself by reading
`dispatch_queue.json`, the receipt, and `tools/research_dispatch.py` in this
session. I verified nothing with git.

## 3. What is NOT damaged

- **Content.** Both declared artifacts match their recorded `sha256` at `HEAD`
  exactly — part of the 30-for-30, zero-mismatch check the harness-driving
  session performed across all five task directories.
- **The evidentiary property this archive exists to establish is intact and is
  independently checkable by five means that do not involve the dispatch queue:**
  `1aa7db53` precedes `c034ef38` in branch history; the frozen text is absent at
  `1aa7db53`'s parent `3d5dd80a`; `git log --all --follow` returns exactly one
  commit for it; the notarizing commit is an ancestor of `HEAD`; and all four
  producers verified the notarized blob in both directions at runtime and would
  have aborted on mismatch (each `results_*.json` `prereg_verification` block).
  All of these are the harness-driving session's measurements, and every one of
  them is a check the Validator's own completion gate independently requires.
- **Immutability.** The committed receipt is untouched and must stay untouched.
  This file supersedes by reference, exactly as AGENTS.md rule 4 requires.

## 4. Why the obvious repair is refused

**Revert-and-re-add is refused, and the refusal is the point.** Re-adding
`prereg.md` in a commit made *after* the producers ran would satisfy the
verifier's negative test while destroying the only property the test exists to
establish: that the frozen text provably predates every measurement it governs.
That trade is worse than the defect. I confirm the harness-driving session's
judgement here without qualification.

**History rewriting is forbidden** by AGENTS.md ("Durable research commits") and
by CLAUDE.md; `502d15a0` and its predecessors are pushed.

**No future commit can satisfy this contract**, and that is a property of the
frozen tool rather than an opinion:

- a task's `artifact_paths` must be non-empty (`research_dispatch.py:502` with
  `require_text_list`'s default `allow_empty=False`), so an archive task always
  owns at least one file of its own;
- every artifact path has exactly one owning task (`research_dispatch.py:511-517`),
  so a successor archive cannot borrow the producer's paths as its own;
- therefore the successor's own receipt must ride in the archive commit, and the
  archive commit must also change exactly the source paths — which are already
  committed and cannot be changed again without deleting and re-adding them.

**The content-only fallback is not available and must not be manufactured.**
`_verify_content_only` (`research_dispatch.py:961-1021`) is reached only when the
declared commit does not resolve (`:1029-1034`) or is not an ancestor of `HEAD`
(`:1045-1048`). Neither is true here. Declaring an unreachable sha to reach that
branch would be a fabricated commit binding under AGENTS.md core rule 9. It is
not on the table.

## 5. What supersedes it

Nothing restores this archive task; what supersedes it is a record of what
actually happened plus a conforming successor archive that carries that record:

1. This file and its sibling, plus
   `../../COORDINATOR-ADJUDICATION-20260811.md`.
2. A new coordinator producer task `TASK-20260811-dac670` **(PLACEHOLDER — mint
   with `python3 tools/allocate_id.py --next handoff --date 20260811`, then
   `--check` it)** owning exactly those three files.
3. A new coordinator snapshot archive `TASK-20260811-998fb8` **(PLACEHOLDER, same
   mint)** with `source_task_ids: [TASK-20260811-dac670]`, owning exactly
   `coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/archives/TASK-20260811-998fb8/snapshot-receipt.json`,
   riding in **one new commit that changes exactly those four paths** — the three
   defect/adjudication files and its own receipt. That commit is conforming
   because every path in it is new.
4. **Its receipt body must carry `commit_sha: null`**, because a receipt that
   states its own commit's sha cannot be inside that commit. The real sha goes
   into `dispatch_queue.json`'s `archive` block *after* the commit. This is the
   pattern BATCH-cbe023 used and it is the only pattern this tool accepts; see
   the adjudication, section "The forward fix".

`TASK-20260809-91cf76` itself is set to `failed` in the dispatch queue and its
`archive` block is filled from the committed receipt (2 hashes, `commit_sha
1aa7db53`, `parent_sha 3d5dd80a`) so a later reader can re-derive the defect
mechanically. The task id is **not** reused, remapped, or deleted (AGENTS.md
rule 15).

## 6. Secondary observations, recorded because they were checkable

Read by me from the committed receipt; neither is the blocking defect and
neither is repairable, the receipt being immutable.

- The task's completion gate required that "origin/main was fetched and MERGED
  into the working branch ... the base commit checked and the merge outcome are
  recorded in the receipt" and that the branch be pushed with a PR opened or
  refreshed. **The receipt records neither.** I do not assert that the merge or
  the push did not happen — only that this receipt does not record them. PR
  status: **UNKNOWN to me.**
- Everything the receipt *does* assert about its own verification (recomputed
  sha256, the prereg's structure against the card) is stated as this session's
  own work and is properly attributed, which is the BATCH-cbe023 F-1 lesson
  honoured.
