# TASK-20260901-d88346 — Binding-supplement report

**Resolves**: validator finding F-VAL4c225b-1 (MEDIUM), route 1 of DEC-20260901-1fc2f5.
**Goal**: GOAL-AES-002 · **Question**: RQ-AES-002 · **Batch**: BATCH-241d37 (item 4)
**Subject**: BATCH-286bcd's opening commit
**Artifact class**: PROSE_REPORT (SC-3 closed vocabulary)
**Covering manifest**: `batch-286bcd-opening-binding-supplement.yaml` (same directory)

This report is BOOKKEEPING. It asserts nothing about AES at any round count, states
no margin, makes no state-of-the-art comparison, and cites no recalled literature
figure. An archive-coverage gap is infrastructure signal, never negative mathematical
evidence.

---

## 1. Result in one paragraph

BATCH-286bcd's opening commit is `6223df070bba437c27d05e4b293a710d0b8bad93`
(parent `5583bebdb2042ca57400f6b62993d6c90468344b`). It added **22 files**, all with
change type `A`, 3463 insertions and 0 deletions. The dispatcher-authoritative archive
binding — `dispatch_queue.json`'s `tasks[TASK-20260901-d10bc6].archive.path_sha256` —
declares 3 paths, of which only **2** are in the opening commit (`batch.yaml` and
`budget-accounting/F2-reconciliation.yaml`); the third is the snapshot receipt itself,
which lives in the snapshot commit, not the opening commit. **20 paths** in the opening
commit therefore carried no machine-checked hash pin: `dispatch_queue.json`, 9 task
cards, and 10 ledger handoffs. **F-VAL4c225b-1's count of 20 is independently confirmed,
not copied.** Of the 22 paths, **21 are byte-identical at HEAD**; the single difference
is `dispatch_queue.json`, exactly as anticipated.

## 2. Method, with the verbatim commands run

Commit identification (two independent routes, agreeing):

```sh
# route A — from BATCH-286bcd's own dispatch_queue.json archive block
#   tasks[TASK-20260901-d10bc6].archive.parent_sha == 6223df070bba437c27d05e4b293a710d0b8bad93
# route B — confirm that sha directly
git log -1 --format='%H%n%P%n%an%n%ad%n%s' 6223df070
git show --stat  --format='%H %P' 6223df070bba437c27d05e4b293a710d0b8bad93
git show --name-status --format=''  6223df070bba437c27d05e4b293a710d0b8bad93
git show --name-only  --format=''   6223df070bba437c27d05e4b293a710d0b8bad93 | grep -c .   # -> 22
```

Per-path hashing, run at the shell for all 22 paths and then re-run in-process over the
identical bytes (`git show <rev>:<path>` stdout through Python `hashlib.sha256`); both
passes agreed on every value:

```sh
git show 6223df070bba437c27d05e4b293a710d0b8bad93:<path> | sha256sum   # at the opening commit
git show HEAD:<path>                                     | sha256sum   # at HEAD
git cat-file -e HEAD:<path>                                            # presence at HEAD
```

At-HEAD values are read from **committed git blobs**, never from the working tree. That
matters here: two other producer tasks were running in this same tree, and `git status
--short` showed their in-flight edits (see §6). Reading blobs makes those edits
incapable of contaminating any number in this report.

Corroborating history for the one differing path:

```sh
git log      --oneline 6223df070..HEAD -- .../BATCH-286bcd/dispatch_queue.json
git rev-list --count   6223df070..HEAD -- .../BATCH-286bcd/dispatch_queue.json   # -> 5
git diff     --numstat 6223df070..HEAD -- .../BATCH-286bcd/dispatch_queue.json   # -> 86  42
```

No hash in either deliverable was copied from an existing receipt or inferred. Where a
receipt value is reproduced, it is labelled a cross-check and both values are shown.

## 3. The 22 paths, and the 2/20 split

Full per-path table with `sha256_at_opening_commit`, `sha256_at_head`,
`previously_pinned_by_dispatcher_authoritative_archive_block` and
`newly_bound_by_this_supplement` is in the covering manifest's `paths:` list. Composition:

| group | count | previously pinned | newly bound here |
| --- | ---: | ---: | ---: |
| `batch.yaml` | 1 | 1 | 0 |
| `budget-accounting/F2-reconciliation.yaml` | 1 | 1 | 0 |
| `dispatch_queue.json` | 1 | 0 | 1 |
| task cards (`task-cards/TASK-20260901-*.md`) | 9 | 0 | 9 |
| ledger handoffs (`ledger/handoffs/TASK-20260901-*.yaml`) | 10 | 0 | 10 |
| **total** | **22** | **2** | **20** |

The 9 task cards are for 1af5d9, 2166bd, 354ef5, 420f4b, 4c225b, 5a44cc, a5374b, d08b9f,
d10bc6. The 10 handoffs are those nine plus `TASK-20260901-a666e6.yaml` — the opening
task's own handoff, which is why handoffs outnumber cards by one (a666e6 has no card in
this commit).

## 4. The one path that differs at HEAD, and why

`coordination/goals/GOAL-AES-002/batches/BATCH-286bcd/dispatch_queue.json`

- at `6223df070`: `82656617c041f897f7f98a1f15570e310b743a300528a2eb40fd17241baa0b30`
- at `HEAD` (`719413f0fdad2a5434d141281484183b6981f82b`): `84349034bedb1afaff10ba256acaf67a7ccdd383ad59008fda7969b138044efc`

EXPECTED, and benign. Five commits modified it between the opening commit and HEAD:
`74c913a68`, `4e776e8cb`, `81ceb161e`, `e1fd730ae`, `abea11252` — four recording task
completions and one a pre-archive fix for TASK-20260901-2166bd's outcome plus a
`dispatch_queue.json` hash-pin bug. Net 86 insertions / 42 deletions. This is a living
state-tracker, and its mutability is precisely why it was never a good hash-pin target:
any pin of its current bytes would have gone stale on the campaign's very next queue
update. What this supplement binds is its **opening-commit bytes only** — a statement
that stays true forever because the commit is immutable.

The remaining **21 of 22** paths are byte-identical at HEAD.

## 5. Cross-checks, and one observation outside this task's scope

**Cross-check against the standalone receipt.** The file
`archives/TASK-20260901-d10bc6/snapshot-receipt.json` *does* enumerate all 21 non-self
opening paths, and **every one of its 21 declared hashes matches this task's independent
computation at the opening commit** (`all_receipt_cross_checks_agree: true`). That is a
clean corroboration of the content, and it is why the validator could report no live
content-integrity problem. It does not close the finding: F-VAL4c225b-1 is about the
**machine-checked** binding in `dispatch_queue.json`'s archive block, which
`tools/research_dispatch.py` verifies and which lists 3 paths. The standalone receipt's
own text names that queue block as the authoritative binding. So 20 paths were described
in a receipt but never machine-checked — the gap is real, and narrower than a
content-integrity problem.

**Observation, recorded not adjudicated, and NOT in this task's assigned scope.** The
standalone receipt's `commit_sha` reads `2c1aebf21ecfa403c65a2a01be41e43474fe2bdc`,
while the queue's archive block for the same task reads
`a2073bbbfdcb4057ffa2033df2a01ef603087dcc`. Both are real commits with the same parent
(`6223df070`) and the same subject line. `a2073bbb` **is** an ancestor of HEAD;
`2c1aebf2` is **not** — it is the superseded pre-amend commit. This is consistent with
the receipt's own disclosed self-reference/amend limitation
(`verification.status: commit_sha_filled_by_amend_after_initial_commit`, "may be stale by
exactly one amend step"). Content binding is unaffected: the receipt blob's sha256 is
`46ba5f6d5abc9680d81041b243a462e4bc741aad2b604036ed0652db6d38a378` both at `a2073bbb`
and at HEAD, matching the queue block's declared value. Flagged for the Coordinator as an
observation; this task neither repairs it nor rules on it.

## 6. What was NOT modified

`git status --short` at authoring time:

```
 M docs/claims-and-verification.md
 M docs/evidence-and-reproducibility.md
 M tools/validate_ledger.py
?? coordination/goals/GOAL-AES-002/amendments/protocol-amendment-GOAL-AES-002-004.yaml
?? coordination/goals/GOAL-AES-002/batches/BATCH-241d37/tasks/
```

The three modified files are the concurrent write_scope of TASK-20260901-eb81f4 and the
untracked amendment belongs to another concurrent task; neither is this task's work and
neither is a defect attributable here. The only entry belonging to this task is the
untracked `.../BATCH-241d37/tasks/` tree containing its three deliverables. **No file
outside write_scope was modified. No git write command was run — no add, commit, stash,
checkout, restore or worktree.** In particular, BATCH-286bcd's `dispatch_queue.json`,
task cards, handoffs and receipts were read only, never touched: retroactively widening a
completed archive's declared scope would make the dispatcher recompute `expected_paths`
against a commit already verified under the narrower set, the breakage class this
campaign hit in BATCH-2b0fd1's DEF-3.

## 7. Completion gate

| gate item | status |
| --- | --- |
| every path in the opening commit carries a self-computed sha256 at that commit and at HEAD | MET — 22/22, both columns, computed by this task from git |
| previously-pinned vs newly-bound split explicit | MET — §3 table and per-path booleans in the manifest |
| no file outside write_scope modified, proved with `git status --short` | MET — §6 |
| validator's count independently verified rather than assumed | MET — 22 total / 2 pinned / 20 unpinned confirmed; no correction needed |

## 8. Named as OPEN AND UNATTEMPTED (SC-9)

These were not tried, and are recorded as untried — not as screened, tested or negative:

- The other three BATCH-286bcd snapshot receipts (a5374b, 5a44cc, 420f4b) were not
  audited for the same under-declaration pattern. Scope here is the opening commit only.
- No check of whether this pattern recurs in other batches or other goals.
- `tools/research_dispatch.py` was not re-run and its `expected_paths` logic was not
  independently re-derived by this task; the "queue archive block is authoritative"
  reading is taken from the validator's direct code read and the standalone receipt's own
  text. (Reading it was also deliberately avoided as unstable — a concurrent task holds
  overlapping infrastructure files mid-edit.)
- No mechanism was built to make the dispatcher *consume* this supplement. It is a
  descriptive record for Coordinator and human review, not a new machine check.

## 9. Standing constraints

SC-1 stamps in `budget_stamps.jsonl` with genuine `date -u +%s` epochs; not halted on
budget. SC-2 basis: authoring-inclusive session elapsed; compute reported separately and
is 0 — no experiment, solver or measurement was run, only git plumbing reads. SC-3
covering manifest declared, closed class vocabulary used. SC-4/SC-7: no margin is stated
anywhere in this task's deliverables, so the R5 clause is discharged vacuously and
`dominated_by` is correctly absent rather than fabricated. SC-5, SC-6, SC-8: no recalled
literature figure, no state-of-the-art comparison, no reduced-round assertion. SC-9: §8.
SC-10: nothing fabricated; the one thing this task could not verify — the resolved model
identity — is recorded as `model_verified: false`. SC-11: Amazon Bedrock was not
selected, configured, probed, contacted or used.

**Runtime provenance.** Requested policy `executor-implementation`, reasoning effort
`medium`, `fallback_allowed: false`, `degraded_allowed: false`. The model that answered
self-reports as `claude-opus-5` (runtime environment description, not an independent
attestation); recorded rather than silently substituted. No downgrade was performed.
