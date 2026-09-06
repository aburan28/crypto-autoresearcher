# FINDING-20260904-main-mass-deletion-d5923ae24

**Integrity finding. Not a research result.** A commit merged into `main`
deleted 775 tracked files — immutable ledger records, curated knowledge
entries, write-once merge-event digests, review artifacts, and two tools this
repository's own `CLAUDE.md` mandates — while describing none of it. This
record states what was lost, how it was established, and what this branch did.

- **Recorded at:** 2026-09-04, while merging `origin/main` (`5d7cd2598`) into
  `claude/degree-regularity-polynomial-systems-pssesi` (`6ddbf30bc`)
- **Merge base:** `0d62bb5d874a272da6b2e4e15dbb22111e66d95d`
- **Offending commit:** `d5923ae24949fd92bea5ed808b7b1bb18678198b`
  (author `Dispatch Test <dispatch@example.test>`, 2026-09-04 09:53:41 -0700)
- **Subject:** `research(GOAL-ECDLP-001): open digit-statistic deconfliction (B71-DIGITSTAT-DECONFLICT-20260904-2f7237)`
- **Reached `main` via:** branch `harness-ecdlp-20260904`, merge `9d072bdac`
  (PR #731)

## Establishing the fact

```
$ git diff --name-status d5923ae24^ d5923ae24 | awk '{print $1}' | sort | uniq -c
      5 A
    775 D
     18 M
```

The commit message describes only a deconfliction analysis of three
digit-statistic experiments. It does not mention deleting anything.

Every file `main` lost since the merge base is attributable to that one commit,
with no remainder:

```
$ git diff --name-only --diff-filter=D <merge-base> origin/main | wc -l
755
$ comm -23 <(sort main_deleted.txt) <(sort d5923_deleted.txt) | wc -l
0
```

None of the deleted paths is `.gitignore`d, so this is not the routine removal
of generated artifacts (`knowledge/INDEX.md`, `dispatch_plan.*`):

```
$ git check-ignore --stdin < deleted.txt | wc -l
0
```

## What `main` lost

| family | count |
| --- | --- |
| `coordination/reviews/**` | 221 |
| `experiments/EXP-PFDR-cbdefb/**` | 160 |
| `ledger/hypotheses/*.yaml` | 132 |
| `ledger/handoffs/*.yaml` | 35 |
| `ledger/proposals/*.yaml` | 17 |
| `experiments/EXP-PFDR-4bfc6f/**` | 14 |
| `coordination/goals/**` | 10 |
| `ledger/decisions/*.yaml` | 8 |
| `coordination/events/main/*.yaml` | 7 |
| `ledger/evidence/*.yaml` | 5 |
| `knowledge/**` | 7 |
| `tools/`, `tests/` | 6 |

`ledger/hypotheses` went from 571 records at the merge base to 446 on
`origin/main`.

Decisions and evidence lost:

```
DEC-20260903-7548c0  DEC-20260904-1e27a2  DEC-20260904-28718f  DEC-20260904-36b906
DEC-20260904-63a809  DEC-20260904-8e51d7  DEC-20260904-d47cd2  DEC-20260904-d4a554
EV-PFDR-1394a4  EV-PFDR-99c699  EV-PFDR-acc71a  EV-PFDR-e67f06  EV-PFDR-f71d7f
```

Curated knowledge lost:

```
KN-FIND-0618ab  KN-FIND-64bad4  KN-FIND-b0c3c9
KN-OPEN-02200b  KN-OPEN-2e7514  KN-OPEN-d6ad3f
KN-TECH-1cd4bb
```

Tooling lost:

```
tools/goal_head.py          tools/test_goal_head.py
tools/ledger_summary.py     tools/test_ledger_summary.py
tools/smallroot_reach.py    tests/test_smallroot_reach.py
```

`tools/goal_head.py` and `tools/ledger_summary.py` are the two projections
`CLAUDE.md` ("Reading state: project, never `cat`") and the
`/launch-research-harness` skill require every session to use. While they are
absent from `main`, the mandated way to read portfolio state does not run there.

Also lost: seven write-once `coordination/events/main/*.yaml` merge digests,
which the concurrency contract says sessions read on wake, and this branch's
`coordination/goals/GOAL-AES-002/batches/BATCH-ae07ce/` batch record and task
cards.

## What this branch did

The merge was resolved by **keeping every deleted path**, restored from this
branch's pre-merge `HEAD` (`6ddbf30bc`), which matches the merge base for all
of them. Propagating the deletion was rejected on three grounds:

1. Ledger and knowledge records are immutable; corrections supersede, they do
   not delete (AGENTS.md rule 2). A deletion no record justifies is not a
   correction.
2. The deleting commit gives no rationale for any of it, so there is nothing to
   evaluate as intent — only a diff inconsistent with its own message.
3. `main` without `tools/goal_head.py` cannot serve the reading discipline the
   repository requires of every session.

After restoration, `tools/check_merge_hygiene.py` passes and
`tools/validate_ledger.py` reports 12 errors, **none of them in a restored
file**: five on `ledger/hypotheses/H-CRYPTO-{21e529,7dd003}.yaml`, three on
`ledger/handoffs/TASK-{20260831-52f3df,20260904-a897dc,20260904-c616c0}.yaml`
(all four records new on `origin/main` and untouched here), and four on
`experiments/EXP-ISOU-2ac81f/runs/RUN-ISOU-*/manifest.yaml`, whose blobs are
byte-identical on both branches and were already failing before this merge.
They belong to their owning campaigns and are not repaired here.

## What is still true of `main`

**This branch's restoration does not fix `origin/main`.** Until a merge lands
that restores them, `main` is missing all 755 paths, and any session that
branches from `main` inherits the loss. This branch's PR carries the
restoration; whether it is the right vehicle, or whether a dedicated
restoration PR should land first, is a call for the repository owner.

Anyone auditing this should note that the loss is fully recoverable from git
history — `d5923ae24^` holds every deleted blob — so nothing here is
unrecoverable data loss. It is a live incorrect state on the default branch.

## What this does not claim

Nothing here is evidence about any hypothesis, and none of it reflects on the
research content of `d5923ae24`'s deconfliction analysis, which is preserved
unchanged. This record makes no claim about how the deletion happened; a
stale-worktree `git add -A` would produce exactly this shape, but that is a
conjecture and is not asserted as fact.
