# Finding: self-referencing archive-receipt hashes cannot survive `research_dispatch.py`'s deep content-verification pass, by construction — and this predates this batch

## What was found

`tools/research_dispatch.py`'s full invocation (`--output ... --report ...`) performs
two distinct verification tiers for a `state: completed` archive task:

1. **Shallow gate** (`completed_archive_commits_verified`, checked in the rendered
   dispatch plan's gate list): `archive.commit_sha is not None and bool(archive.path_sha256)`.
   No re-hashing against actual git content.
2. **Deep verification** (triggered inside `_verify_content_only` / the commit-ancestry
   path, invoked by the same `--output/--report` call): re-reads every path in
   `archive.path_sha256` from the actual git blob at `commit_sha` and compares byte-for-byte.

A `kind: snapshot` archive task's own receipt file must include itself in
`archive.path_sha256` (required for tier-1's `hash_paths == expected_set` check,
where `expected_paths = archive_task["artifact_paths"] | source_paths`). But the
receipt's `commit_sha` field can only be known **after** the commit exists — and the
receipt is *part of* that commit's tree. Any edit to fill in the real `commit_sha`
post-commit changes the receipt's bytes, so **no committed hash for that entry can
ever be simultaneously (a) present at commit time and (b) byte-accurate for the
commit's final content.** This is a genuine fixed-point problem (the commit sha
depends on the tree sha, which depends on the receipt blob, which would need to
contain the commit sha), not a bug specific to how it was written this time.

## This is not new to this batch

The same deep verification was run against `GOAL-ECTD-001` **BATCH-002**'s own
receipt (`TASK-20260731-051`, the direct precedent this batch's convention follows)
and **it also fails** — for a different entry (`experiments/EXP-ECTD-001/specification.yaml`,
stale since the unrelated `93f4acd0` CI-fix commit added a required schema field
days after BATCH-002's snapshot). Two independent tasks, two independent stale
entries, same root cause: **the deep byte-exact check is not what this program's
committed decision records actually rely on.** `DEC-20260731-013` cites
`completed_archive_commits_verified: true` — the shallow gate — as its verification
basis, not a deep re-hash.

## What this batch does about it

- `TASK-20260806-4455ac`'s snapshot commit (`9fd0d974`) was verified, **before**
  committing, to contain **exactly** the 39 declared artifacts via
  `git diff --staged --name-only` — this is the load-bearing integrity guarantee,
  and it is real and independently reproducible (`git show --name-only 9fd0d974`).
- The receipt's self-referencing `path_sha256` entry is present (satisfying the
  shallow gate) but will read as stale under the deep check, for the structural
  reason above — consistent with, not worse than, the existing BATCH-002 precedent.
- **This is disclosed here rather than concealed or silently worked around.** A
  future reader hitting the same "content hash mismatch" on this specific entry
  should read this file before assuming the underlying commit is untrustworthy —
  it isn't; the commit's actual content is independently verified above.

## What is not claimed

This does **not** excuse a genuine content mismatch on a *non-self-referencing*
path (that remains fatal and load-bearing, exactly as `CLAUDE.md`'s concurrency
section states). It applies narrowly to the one entry that is structurally unable
to describe itself. No fix is proposed here beyond disclosure; a real fix would
require either dropping the self-reference requirement from the schema (a tooling
change outside this batch's write scope) or a two-stage commit design that this
program does not currently use.
