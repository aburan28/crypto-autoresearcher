# Recovery Report — TASK-20260907-de49ed

**Role:** executor (custody/preservation task, zero scientific runs, zero status changes)
**Goal / Batch:** GOAL-MCE-001 / BATCH-538e87
**Deliverables:** `preservation-package.json` (this directory), this report.

## Session / model provenance (recorded honestly, no fabricated verification)

- Runtime: Claude Code, `CLAUDE_CODE_VERSION=2.1.42`, remote/cloud entrypoint.
- Model: Claude Sonnet 5 (`claude-sonnet-5`), per this session's system context. No Bedrock backend was used or invoked.
- `AUTORESEARCH_POLICY` / `AUTORESEARCH_BACKEND` were **not set** in this session's environment — the resolved
  policy/backend pair could not be read from those variables. Requested policy per the dispatch queue handoff is
  `executor-implementation` (`inference.reasoning_effort: null` in the handoff). Observed environment variable
  `CLAUDE_EFFORT=medium`, consistent with `executor-implementation`'s documented `medium` effort in
  `CLAUDE.md`'s model-policy table, but this is an inference from the environment, not a value read from
  `AUTORESEARCH_POLICY`. No `fallback_used` occurred; no degradation was requested or applied.
- Session id: `CLAUDE_CODE_SESSION_ID=56f4436d-5b61-5b51-83c2-1b43c31a613e`; remote session
  `cse_01NV1n82ki22i5u8Db7JPpWj`.
- Repo state at start of this task: `HEAD=eee9ec41f02b045a893fe166da9e621b71256d8f` on branch
  `claude/run-experiments-uq9jiv`. `git status` showed the working tree **dirty**: two pre-existing modified
  files (`.github/workflows/claude-pr-review.yml`, `.github/workflows/claude.yml`) not touched by this task, plus
  untracked task-output directories from other concurrent goals
  (`GOAL-ENDO-001/.../BATCH-4acfee/tasks/`, `GOAL-MLKEM-005/.../BATCH-203eff/tasks/`,
  `GOAL-SIG-001/.../BATCH-0c2d2a/tasks/`) — none of these are within this task's `read_scope` or `write_scope`
  and none were read, edited, or relied upon. This task wrote **only** the two declared artifacts under
  `coordination/goals/GOAL-MCE-001/batches/BATCH-538e87/tasks/TASK-20260907-de49ed/`.
- No commit was made by this task, per the hard constraints.

## Method

All historical bytes were recovered read-only via `git show <commit_sha>:<path>`, restricted to exactly the
commits named in `source-git-evidence.json` (and one additional commit, `86eeab38b752256e141e9bcd3583c438801e0957`,
identified via `git log --follow` as the commit that actually introduces the TASK-20260809-c30f26 receipt — see
below). No `git checkout`, `reset`, or historical edit was performed. Every commit and its declared parent was
independently confirmed to exist as a reachable git object (`git cat-file -t`, `git merge-base --is-ancestor …
HEAD`) and to carry the commit message and parent recorded in `source-git-evidence.json` (`git log -1 --format='%H
%P %s'`). All three commits are ancestors of the current `HEAD`.

sha256 was computed directly from the recovered bytes in this session (`hashlib.sha256` over the exact
`git show` stdout, and over the exact current on-disk bytes for current-state counterparts) — never copied from
a prior claim without independent recomputation.

## Per-field provenance

### 1. `openingc30f26` — the missing-at-commit receipt finding (CONFIRMED)

- **Commit cited as the archive:** `3e3ec063e47bcc80b615d13684d03c567b69af66` (parent
  `25fdf4fc8b683b47b003da8959dfcc233ac7097e`), message "coord: GOAL-MCE-001 open BATCH-73a1b7 — complete the
  arXiv:2304.14757 boundary correction by supersession". Verified to exist and match the declared parent/message.
- **Finding, independently re-confirmed:** `git show 3e3ec063e47bcc80b615d13684d03c567b69af66:coordination/goals/GOAL-MCE-001/batches/BATCH-73a1b7/archives/TASK-20260809-c30f26/ledger-receipt.json`
  fails with `fatal: path '...' exists on disk, but not in '3e3ec063e...'`. The receipt genuinely was **not**
  part of this commit's tree.
- **Where it actually enters history:** `git log --follow` on that path shows it was introduced by commit
  `86eeab38b752256e141e9bcd3583c438801e0957` ("GOAL-MCE-001 BATCH-73a1b7: mint SUB-1's dispatch queue; backfill
  TASK-20260809-c30f26's receipt"), the same day, per the receipt's own `written_retroactively_note` field
  (recovered verbatim in `preservation-package.json`). This commit is also the declared `parent_sha` of the next
  batch commit (`92d238396d38a07a4c117acf71a5870be67735c7`), consistent with the sequence.
- **Current state:** the receipt exists on disk today at the same path, sha256
  `562f9f1ac2c6455ee423b2f4b3a4b5eea6c2e22ed7bf3d47a80f925a40c6a8e3`, which matches the value
  `source-git-evidence.json` records for this exact path under `TASK-20260809-c30f26.archive.path_hashes`
  (the same evidence file separately records this path as `null` under its own `path_hashes` block, i.e. the
  evidence-gathering session had already flagged this path as unbindable to the `3e3ec063e` commit — consistent
  with what this task independently re-derived).
- **Both the historical-absence-at-3e3ec063e state and the current backfilled bytes are preserved in
  `preservation-package.json`** (the former as an explicit `historical_recovered: false` entry with the exact
  git error message; the latter as a full base64-encoded byte capture from `86eeab38b752256e141e9bcd3583c438801e0957`
  and from the current working tree, both hashing to the same value).

### 2. `producer3e30b8` — TASK-20260809-3e30b8's snapshot-archived deliverables

- **Commit:** `92d238396d38a07a4c117acf71a5870be67735c7` (parent `86eeab38b752256e141e9bcd3583c438801e0957`),
  message "GOAL-MCE-001 BATCH-73a1b7: snapshot-archive TASK-20260809-3e30b8's claim-class audit deliverables
  (TASK-20260809-0b6630)". Verified reachable and matching.
- All 9 declared paths (`tools/claim_class_audit.py`, `tools/test_claim_class_audit.py`, the 5
  `tools/fixtures/claim_class_evasions/*.md` files, `knowledge/TAG-CLAIM-CLASS-v2.md`, and this commit's own
  `snapshot-receipt.json`) were recovered successfully; every recovered sha256 matches the value declared in
  `source-git-evidence.json`'s `path_hashes` for `TASK-20260809-0b6630`.
- **Current-state comparison:** every one of these paths is byte-identical between the historical commit and the
  current working tree (all `bytes_identical_historical_vs_current: true`), including the three literal
  "execution report" citations inside `tools/claim_class_audit.py` (lines 112, 121) and
  `tools/test_claim_class_audit.py` (line 163) — confirmed unchanged since the original commit.

### 3. `review076a75` / `c8122d` — the CONDITIONAL_PASS review snapshot

- **Commit:** `c85bf16a68e0e683277ad27fb267a9c5425129c7` (parent `469ab6e0e545ca8bc3ac685d17b7cf8a830f0a5f`),
  message "GOAL-MCE-001 BATCH-73a1b7: archive TASK-20260809-076a75's review (CONDITIONAL_PASS)". Verified
  reachable and matching.
- Both declared paths (`review_report.yaml`, this task's own `ledger-receipt.json`) recovered successfully;
  hashes match `source-git-evidence.json`.
- **Verdict independently re-read from the recovered bytes:** `review_report.yaml` line 398 reads
  `verdict: CONDITIONAL_PASS` — confirmed directly, not taken on any prior summary's word.
- Current on-disk copies of both files are byte-identical to the commit (both `bytes_identical...: true`).
- The review's two named required fixes for full PASS (archive a genuine `execution_report` for
  TASK-20260809-3e30b8, or correct the dangling citations; and a stale `dispatch_queue.json` state, since
  corrected) are preserved verbatim inside the recovered `review_report.yaml` and `ledger-receipt.json` bytes.
  **Neither fix has been performed by this task or any other task to date**, and no PASS, upgrade, or
  second-review outcome is asserted anywhere in `preservation-package.json`.

### 4. `execution_report` artifact — existence check

- **Finding: it does not exist.** Confirmed by (a) direct grep of the current working tree for
  `execution_report` near TASK-20260809-3e30b8's context, (b) reading the three literal "execution report"
  prose citations inside `tools/claim_class_audit.py` (lines 112, 121) and `tools/test_claim_class_audit.py`
  (line 163) — all are English-language references to a document, not a file path, and no such file exists
  anywhere in the repository under any plausible name; (c) the already-recovered `ledger-receipt.json` for
  TASK-20260809-c8122d, which records that same Coordinator session's own repository-wide search finding
  "no execution_report artifact scoped to TASK-20260809-3e30b8" (the many `execution_report.yaml/.md` files
  that do exist all belong to other goals' other tasks).
- **Dangling citation locations** (file, line, confirmed at current HEAD and at the historical commit
  `92d238396d38a07a4c117acf71a5870be67735c7`, i.e. present from the moment of the producer's original commit,
  not introduced later): `tools/claim_class_audit.py:112`, `tools/claim_class_audit.py:121`,
  `tools/test_claim_class_audit.py:163`. All recorded in full in `preservation-package.json`'s
  `execution_report_artifact_finding` block.
- **Prospective patch proposal (proposal only — not applied, no live file edited):**
  - Option A: author and archive a genuine `execution_report` artifact for TASK-20260809-3e30b8 reconstructing
    the GATE-A break-attempt log from already-committed evidence (test docstrings, the CONDITIONAL_PASS review's
    own account), disclosing any gap between what the citations imply and what can actually be reconstructed.
  - Option B: amend the three citations to point at what is actually committed (e.g. the specific test class in
    `tools/test_claim_class_audit.py`), per the review's own named fix.
  - Full text of both options is recorded in `preservation-package.json`. **Neither is authorized or performed
    by this task** — this task's `write_scope` excludes `tools/` entirely, and the choice between the two
    options (or a hybrid) is explicitly left to a future Coordinator-approved task.

## Current-state vs. historical mapping differences (all disclosed, none silently absorbed)

Two of the twenty preserved entries have `bytes_identical_historical_vs_current: false`, both are legitimate,
disclosed later edits and neither touches the substance this task was asked to preserve:

1. **`ledger/goals/GOAL-MCE-001/goal.yaml`** — 374 lines added / 49 removed since commit `3e3ec063e`. All of the
   diff is later, disclosed Coordinator edits to the mutable `next_action`/`campaign_budget` fields
   (DEC-20260809-769359, DEC-20260810-4eae48, and the 2026-08-28 user-authorized "Fund every goal" budget
   amendment DEC-20260828-5bf5f2 setting `maximum_batches`/`total_wall_clock_seconds` to `null`). No scientific
   field, hypothesis status, or claim tier was touched by the diff. Full historical and current bytes are both
   preserved in `preservation-package.json`.
2. **`coordination/goals/GOAL-MCE-001/batches/BATCH-73a1b7/dispatch_queue.json`** — current sha256
   `daf021c77354d6840c1df84606e0c0019fb9086c0126aeafe245503100b12c30` matches both `intake.md`'s declared
   "Original SHA256" and `coordination/goals/GOAL-MCE-001/batches/BATCH-538e87/original-dispatch-queue.json`
   byte-for-byte (independently reconfirmed here). It differs from the commit-`3e3ec063e` version because three
   later same-batch Coordinator sessions applied disclosed, inline `coordinator_correction_note` fixes to task
   state/archive-kind/scope on TASK-20260809-c30f26, TASK-20260809-3e30b8, and TASK-20260809-c8122d, all visible
   verbatim inside the recovered current bytes. This is the corrected queue `original-dispatch-queue.json`
   preserves; both the commit-time and corrected bytes are captured.

No hash retargeting, ID remap, or archive bypass was performed to reconcile these differences — both versions'
exact bytes and hashes are preserved side by side, with the difference explained in prose only.

## Explicitly unresolved / could NOT be independently improved (infrastructure facts, not evidence)

- The `execution_report` artifact for TASK-20260809-3e30b8 remains genuinely absent from the repository at
  every inspected revision, including HEAD. This is reported as an absence, not treated as negative evidence
  about the claim-class audit tool's correctness or about Classic McEliece.
- The two fixes required for the CONDITIONAL_PASS review to become a full PASS (execution-report/citation fix;
  the already-corrected stale queue state) remain unresolved except for the queue-state part, which the
  recovered `original-dispatch-queue.json`/current queue shows was already corrected by a subsequent Coordinator
  session — the execution-report/citation fix itself is still open.
- A second, independent review of TASK-20260809-3e30b8's deliverables (required before any PASS/upgrade) has
  not occurred. This task does not perform it, simulate it, or assert any result for it.
- SUB-2 (corpus-wide `superseded_by` policy) and SUB-3 (arXiv-v3 / abstract-provenance seams) remain unallocated
  scope items in BATCH-73a1b7's queue, out of scope for this custody task and not touched.
- No git object named in `source-git-evidence.json` or discovered via `git log --follow` for the c30f26 receipt
  was unreachable, corrupted, or otherwise unrecoverable in this clone — every read attempted in this task
  succeeded except the one deliberate, expected, and confirmed-real absence documented above (the receipt
  missing from `3e3ec063e` itself).

## Controls performed

- **Compare all original hashes before and after:** every recovered historical sha256 was checked against
  `source-git-evidence.json`'s declared `path_sha256`/`path_hashes` for that path; all matched exactly (see
  `preservation-package.json` entries).
- **Independent Git blob comparison:** every commit/parent pair was independently confirmed via `git cat-file -t`
  and `git log -1 --format='%H %P %s'` against the values `source-git-evidence.json` declares, rather than
  trusted from that file alone.
- **Intentional bad-hash/path-map rejection control:** deliberately attempted `git show
  92d238396d38a07a4c117acf71a5870be67735c7:tools/claim_class_audit.py` compared against a hand-computed sha256
  and cross-checked against a **deliberately wrong** hash string (a single flipped hex digit of the declared
  `d3bdbf19cfb0c7e960de980b3678c2e6143589c99079f6001719dbec100eef2e`) to confirm the comparison logic used in this
  task actually rejects a mismatch rather than passing everything unconditionally — the deliberately-corrupted
  hash correctly failed the equality check in the same Python comparison code used for the real entries, before
  being discarded (not written anywhere in the final package).

## Completion gate self-check

- All original source bytes remain unchanged: confirmed — no `git checkout`/`reset`/edit was performed at any
  point; only `git show` (read-only) was used.
- Original failures are explicitly retained: the missing-at-`3e3ec063e` receipt, and the CONDITIONAL_PASS
  verdict with its two named required fixes, are both preserved verbatim, not upgraded or summarized away.
- Artifacts report measured hashes and per-path provenance, or explicit unavailable-source impediments: done for
  all 20 entries in `preservation-package.json`.
- No experiment run, scientific transition, historical completion normalization, or independent-review
  fabrication occurred: confirmed — zero runs, zero ledger/goal/hypothesis edits, no PASS asserted for anything
  that only reached CONDITIONAL_PASS, no second review performed or simulated.
