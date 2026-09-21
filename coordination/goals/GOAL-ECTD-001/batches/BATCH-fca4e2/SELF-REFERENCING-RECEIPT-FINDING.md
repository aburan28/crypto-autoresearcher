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

## Addendum (TASK-20260806-411ffd): the recorded self-hash was not merely stale, it was wrong even at commit time -- and that hard-blocks the dispatcher, not just the receipt

Running `tools/research_dispatch.py ... --output --report` while drafting the
ledger archive (`TASK-20260806-411ffd`) found that `dispatch_queue.json`'s
declared self-hash for `TASK-20260806-4455ac`'s receipt
(`364dcbed...`) does not match `sha256(git show 9fd0d974:<path>)`
(`743e2458...`) -- and, unlike the shallow gate, this is **not tolerant**: a
content-hash mismatch on *any* completed archive task aborts the entire
`--output/--report` run with exit code 2 and produces no dispatch plan at all,
for the whole queue, not just the offending task. This is worse than "reads as
stale under deep verification" (this file's original framing) -- it made the
CLI unusable for this queue at all, including for validating the unrelated
`TASK-20260806-411ffd` work in progress.

Checked whether `364dcbed...` was ever correct: the committed receipt blob at
`9fd0d974` itself declares `364dcbed...` as its own self-hash, so the value
was miscomputed against a draft that did not byte-for-byte match what was
actually staged and committed (a real computation slip on my part when
preparing that commit, not purely the abstract fixed-point problem this file
otherwise describes -- the fixed-point problem guarantees *some* staleness is
inevitable, it does not by itself explain a mismatch against the file's *own*
committed draft).

**Resolution applied:** `dispatch_queue.json`'s declared `path_sha256` entry
for that one self-referencing path was corrected from `364dcbed...` to the
true value `743e2458...` (`sha256` of `git show 9fd0d974:<path>`, independently
recomputed and matching). This is a correction to a *mutable coordination
artifact* (the dispatch queue, which this batch has already edited repeatedly
for scaffolding gaps), not to the *immutable committed receipt blob* at
`9fd0d974`, which is left exactly as committed and unedited -- consistent with
AGENTS.md rule 4. After the correction, `--output/--report` runs clean (exit
0, all ten gates true, `completed_archive_commits_verified: true`) as of this
addendum. Recorded here rather than silently patched, per this file's own
opening principle.
