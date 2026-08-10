# Orchestrator correction to the TASK-20260810-c64cf0 audit

Recorded 2026-08-10 by the orchestrating session that dispatched
RECON-20260810-001. This note corrects ONE factual item in the audit's
`anomalies` list. It corrects nothing else, and the audit deliverables
themselves are left exactly as the Executor wrote them — this is a
superseding note, not an edit.

## The item

`TASK-20260810-c64cf0`'s terminal report records, under `anomalies`:

> The two untracked dispatch_plan files present at audit start were gone at
> audit end; removed by something outside this session, not by this task.

**That inference is wrong, and the correction matters because "files vanished
from a coordination campaign mid-audit" reads as evidence of concurrent
interference when nothing of the sort happened.**

## What actually happened

Both files still exist and were never deleted:

```
$ ls -la coordination/reconciliation/RECON-20260810-001/
-rw-r--r-- 1 root root  8143 Aug 10 04:49 dispatch_plan.json
-rw-r--r-- 1 root root  1770 Aug 10 04:49 dispatch_plan.md
```

They left `git status` because the ORCHESTRATING SESSION added them to
`.gitignore` while the audit was in flight, in commit `b5d7b266` ("Ignore
reconciliation-campaign dispatch plans"):

```
$ git check-ignore -v coordination/reconciliation/RECON-20260810-001/dispatch_plan.json
.gitignore:147:coordination/reconciliation/*/dispatch_plan.json
```

So the change was made INSIDE this session, by the orchestrator, not outside
it; and the files were made invisible to `git status`, not removed. The
Executor observed the effect accurately and attributed it reasonably given
what it could see — it had no way to observe a `.gitignore` commit landing
underneath it mid-run.

Why it was done: `research_dispatch.py` writes `dispatch_plan.{json,md}` for a
RECON campaign the same way it does for a goal batch, but the repository's
existing ignore globs cover only `coordination/goals/`, so this campaign's
generated plan was landing untracked. Generated artifacts are never committed
here.

## Scope of this correction

- The `anomalies` entry above is SUPERSEDED. Nothing was removed by an outside
  agent and no concurrent interference is evidenced.
- Every other finding in `goal_head_audit.yaml`, `queue_state_audit.yaml` and
  `method.md` stands unamended, including the three remaining anomalies.
- No sha, verdict, count or evidence-strength label anywhere in the audit is
  affected: the two files are generated artifacts of this campaign and are not
  part of any audited goal head or queue entry.

## A limitation this exposes, worth carrying forward

The audit was taken at `bb1c6e47`, but the working tree moved to `b5d7b266`
beneath it. That did not affect any finding here — the change touched only
`.gitignore` — but an audit that reads a live working tree while the
orchestrator commits to it can in principle observe a tree no single commit
ever had. A future audit of this kind should either run against a fixed commit
(`git worktree add` at an explicit sha) or the orchestrator should refrain from
committing for its duration.
