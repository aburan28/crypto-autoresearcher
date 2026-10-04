# TASK-20260907-ad00af recovery report

Custody/preservation only. Zero scientific runs. Zero status changes to any
hypothesis, goal, or experiment. No commits were made by this task; all
outputs are written under this task's exclusive write_scope.

## Session / model provenance

- Role: executor (this task card, `TASK-20260907-ad00af`).
- Requested policy per handoff: `executor-implementation` (`reasoning_effort:
  null` in the handoff; per `AGENTS.md` model-policy table this policy maps
  to `effort: medium` under the Claude Code runtime).
- Runtime: Claude Code (`claude-sonnet-5`, session
  `session_01NV1n82ki22i5u8Db7JPpWj`), invoked as a subagent of the parent
  Coordinator session. `fallback_used`/`degraded_allowed` were not exercised;
  no Bedrock backend was used. This is the actual resolved runtime as
  observed in this conversation; no separate model-verification call was
  made or is claimed.
- Repository state at recovery: `HEAD=79b01b2ba08419c8e2c59cfa82ecf723da9d900f`,
  working tree clean (`git status --porcelain` empty) at the time of
  recovery. All git operations performed were read-only inspection
  (`git show`, `git cat-file -e`, `git rev-list --parents`, `git diff-tree`,
  `git merge-base --is-ancestor`, `git log --oneline`) against the two
  revisions named in `source-git-evidence.json` and `intake.md`
  (`5298c29a29cebfae12c6884fe9e88f8ad8dd4c01`,
  `281a70a3cb0bbc9b75121330ab590e150f8cd402`) plus their parents where needed
  to verify parent-sha claims. No checkout, reset, or historical edit was
  performed.

## What was recovered, and from where

All 13 archive artifacts named across `intake.md` and
`source-git-evidence.json`, plus the BATCH-1f4d53 control copy of the
original queue, were successfully recovered. **No source object was
unavailable.** Every entry below is present in
`preservation-package.json` under `recovered_entries[]`, with its own
`source_revision`, `path`, historical sha256, current sha256, and
byte-for-byte base64 content.

### snapshot002 (`5298c29a29cebfae12c6884fe9e88f8ad8dd4c01`)

- Confirmed a real, reachable commit: ancestor of `HEAD`, first parent
  `6c6fce7d33896c1f7641f477eb1b5880ebcb623d` — this **matches** the
  `parent_sha` declared in both the current `dispatch_queue.json` archive
  block and the `snapshot-receipt.json`.
- Recovered files (all readable, all hashes independently recomputed with
  `git show <rev>:<path> | sha256sum`):
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/archives/TASK-20260731-002/snapshot-receipt.json`
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/tasks/TASK-20260731-001/discovery_readiness_screen.yaml`
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/tasks/TASK-20260731-001/literature_screen_notes.md`
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/tasks/TASK-20260731-001/websearch_receipts.json`
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/tasks/TASK-20260731-001/crossref_receipts.json`
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/dispatch_queue.json` (the ORIGINAL SOURCE QUEUE)
  - `ledger/goals/GOAL-MLKEM-002.yaml` (the UNRELATED extra diff named in the batch objective)
- All four `TASK-20260731-001` artifact hashes match exactly what
  `snapshot-receipt.json` / the dispatch queue's `archive.path_sha256`
  already declared. `discovery_readiness_screen.yaml`,
  `literature_screen_notes.md`, `websearch_receipts.json`, and
  `crossref_receipts.json` are byte-identical between the historical commit
  and the current working tree.

### ledger004 (`281a70a3cb0bbc9b75121330ab590e150f8cd402`)

- Confirmed a real, reachable commit: ancestor of `HEAD`. **Its true first
  parent, per `git rev-list --parents`, is
  `bd10a8f231d439d1ad918c31761bf41d283b915c`** — a commit titled "research:
  bind BATCH-013 snapshot-receipt commit_sha". This does **not** match the
  `parent_sha` currently recorded in `ledger-receipt.json`
  (`27ef824afe59fda596734ee070703e6a4aac11c8`, a different, also-real commit
  titled "research: bind BATCH-013 ledger-receipt and GOAL verified commit").
  See "Exact-diff failure" below.
- Recovered files (all readable):
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/archives/TASK-20260731-004/ledger-receipt.json`
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/tasks/TASK-20260731-003/falsification_review.md`
  - `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/tasks/TASK-20260731-003/red_team_report.yaml`
  - `ledger/decisions/DEC-20260731-002.yaml`
  - `ledger/evidence/EV-CRYPTO-013.yaml`
  - `ledger/goals/GOAL-CRYPTO-001.yaml`
- `falsification_review.md`, `red_team_report.yaml`, `DEC-20260731-002.yaml`,
  and `EV-CRYPTO-013.yaml` are byte-identical between the historical commit
  and the current working tree — the FINAL_NO_CANDIDATE / CONFIRM verdicts
  and their supporting text are unchanged.
- `ledger/goals/GOAL-CRYPTO-001.yaml` is **not** byte-identical between the
  historical commit and current working tree. This is expected and is not a
  defect: the goal record has been legitimately amended repeatedly since
  2026-07-31 (budget amendments, a 2026-08-18 hold-audit note, and the
  2026-09-07 `integrity_recovery_20260907` block). Historical sha256
  `6cde05e8d5aa686045df31d32ffd95c9718aa751bd79e87e550cb08767adb21e`; current
  sha256 `02865c12dbbddb105efe8d05f9a0ae2f26db1f3132ee63060e99a2426e6defa7`.

## The frozen first defect (dispatch double-ownership) — NOT waived

`intake.md`'s "Frozen first defect" reads: *"dispatch error: non-archive task
TASK-20260731-001 is assigned to both TASK-20260731-002 and
TASK-20260731-004."* Independently confirmed against the **current**
`coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/dispatch_queue.json`:

- `TASK-20260731-002.archive.source_task_ids == ["TASK-20260731-001"]`
- `TASK-20260731-004.archive.source_task_ids == ["TASK-20260731-001", "TASK-20260731-003"]`

Both archive tasks still claim `TASK-20260731-001` as a source. This defect
is **still present** in the current dispatch queue and is recorded here
exactly as found. It is not resolved, remapped, or waived by this task, per
the `TASK-20260907-ad00af` handoff constraint. The current
`dispatch_queue.json` itself documents (in a 2026-08-29 `diagnosis_note` on
the `TASK-20260731-004` archive block) that this was diagnosed as a
genuine schema-evolution gap between the 2026-07-31 authoring rules and the
current `tools/research_dispatch.py` rules, and left unrepaired pending a
Coordinator decision on whether legacy content-first archives are exempt or
need a superseding correction record. That diagnosis note is preserved
verbatim in `preservation-package.json`; this report does not adjudicate it.

## The old exact-diff failure — NOT waived, NOT corrected

A **second, distinct** exact-diff failure was found and independently
verified while recovering ledger004, in
`coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/archives/TASK-20260731-004/ledger-receipt.json`.
Comparing the historical committed blob (`git show 281a70a3cb...:<path>`)
against the current working-tree file:

| field | historical (committed at 281a70a3cb...) | current (working tree) | independently verified against git |
|---|---|---|---|
| `parent_sha` | `bd10a8f231d439d1ad918c31761bf41d283b915c` | `27ef824afe59fda596734ee070703e6a4aac11c8` | historical value is **correct** (matches `git rev-list --parents`); current value is **wrong** — it is a real commit but not this commit's first parent |
| `commit_sha` | `null` | `281a70a3cb0bbc9b75121330ab590e150f8cd402` | current value is correct (this commit's own sha) — a legitimate stub fill-in |
| `artifact_sha256["ledger/goals/GOAL-CRYPTO-001.yaml"]` | `6cde05e8d5aa686045df31d32ffd95c9718aa751bd79e87e550cb08767adb21e` | `6a44f65becaf8266de6a1357d84228c800b52cf7a9a857295b545306a371c154` | historical value is **correct** (matches `git show 281a70a3cb...:ledger/goals/GOAL-CRYPTO-001.yaml \| sha256sum`); current value is **wrong** — matches neither the historical git blob nor the current working-tree file |

All other `artifact_sha256` entries in the same file
(`falsification_review.md`, `red_team_report.yaml`,
`DEC-20260731-002.yaml`, `EV-CRYPTO-013.yaml`) are unchanged and correct in
both historical and current versions.

**This is recorded exactly as found and is not corrected, softened, or
waived by this task.** No hash retargeting was performed; the incorrect
current values are preserved in `preservation-package.json` alongside the
correct historical values and the independent git re-derivation, so the
discrepancy is checkable by any reader without trusting this report.

## Control: intentional bad-hash/path-map rejection

As an explicit control, the claim "`27ef824afe59fda596734ee070703e6a4aac11c8`
is the first parent of `281a70a3cb0bbc9b75121330ab590e150f8cd402`" (i.e. the
value currently recorded in `ledger-receipt.json`) was tested directly
against `git rev-list --parents -n1 281a70a3cb0bbc9b75121330ab590e150f8cd402`.
The claim was **rejected**: git's real answer is `bd10a8f231d439d1ad918c31761bf41d283b915c`.
This confirms the recovery method does not accept a bad path/hash mapping on
trust, and that the mismatch identified above is a genuine finding, not a
transcription slip on my part.

## The unrelated GOAL-MLKEM-002 extra diff — explicitly inventoried

`source-git-evidence.json`'s recorded diff for the snapshot002 commit lists
`ledger/goals/GOAL-MLKEM-002.yaml` alongside the six GOAL-CRYPTO-001/BATCH-013
paths. Independently reproduced with
`git diff-tree --no-commit-id --name-only -r 6c6fce7d33896c1f7641f477eb1b5880ebcb623d 5298c29a29cebfae12c6884fe9e88f8ad8dd4c01`:
the same seven paths came back, confirming `ledger/goals/GOAL-MLKEM-002.yaml`
really was touched by the same commit that carries the GOAL-CRYPTO-001
snapshot002 archive, even though GOAL-MLKEM-002 is scientifically unrelated
to GOAL-CRYPTO-001. The parent of that commit
(`6c6fce7d33896c1f7641f477eb1b5880ebcb623d`) is itself titled "research: bind
GOAL-MLKEM-002 quorum ledger-receipt commit_sha," which is the likely origin
of the co-mingled diff. `ledger/goals/GOAL-MLKEM-002.yaml`'s bytes are
byte-identical between that historical commit and the current working tree
(sha256 `cac7eb239032ca66ee15e489cc567d9b0fe5e9dba8b6fee5ac812a3dd92aac70` in
both) — the file has not changed since. Full bytes for both revisions are in
`preservation-package.json`. This task does not interpret, resolve, or
comment on GOAL-MLKEM-002's own scientific state beyond this byte-identity
observation, per the read-only/no-interpretation constraint.

## Duplicate ownership preservation

Per instruction, the duplicate ownership described above (`TASK-20260731-001`
claimed by both `TASK-20260731-002` and `TASK-20260731-004`) is preserved
exactly as found in both the historical commit and the current working tree.
No single "clean" owner was fabricated; `preservation-package.json` records
`duplicate_ownership_preserved.still_present_in_current_dispatch_queue:
true`.

## What could NOT be recovered

**Nothing.** Both named revisions (`5298c29a29cebfae12c6884fe9e88f8ad8dd4c01`
and `281a70a3cb0bbc9b75121330ab590e150f8cd402`) exist as real, reachable git
objects in this clone, and every path named against them in
`source-git-evidence.json` / the corresponding receipts was readable via
`git show <rev>:<path>`. Every current-state counterpart file named in
`intake.md`/`source-git-evidence.json` also exists in the working tree. No
missing-revision or unreadable-object impediment was hit, so no recovery
step was stopped. `preservation-package.json.unresolved_or_missing` is an
empty list, recorded as such rather than omitted.

## Metrics (per handoff)

- `original_byte_changes`: 0 (this task performed read-only `git show` /
  inspection only; it modified nothing under `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/`,
  `ledger/`, or any other pre-existing path).
- `scientific_runs`: 0.
- `recovered_file_count`: 14 distinct (revision, path) entries recovered
  into `preservation-package.json.recovered_entries` (7 under snapshot002, 6
  under ledger004, 1 current-state-only control copy), covering all 13
  named historical archive artifacts plus their current counterparts.
- `unresolved_file_count`: 0.
- `hash_mismatch_count`: 2 declared-vs-actual mismatches found and preserved
  as findings (not corrected): (1) `ledger-receipt.json`'s current
  `parent_sha` vs git's actual first parent of `281a70a3cb...`; (2)
  `ledger-receipt.json`'s current `artifact_sha256["ledger/goals/GOAL-CRYPTO-001.yaml"]`
  vs the actual git blob hash at that commit. A third file
  (`ledger/goals/GOAL-CRYPTO-001.yaml` itself, historical-vs-current) differs
  as *expected* legitimate goal-record evolution, not counted as a mismatch.
- `mapping_differences`: recorded per-entry in
  `preservation-package.json.recovered_entries[].mapping_or_content_difference`;
  summarized above.

## Completion gate (per handoff)

- All original source bytes remain unchanged: confirmed — this task made no
  writes outside `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-1f4d53/tasks/TASK-20260907-ad00af/`.
- Original failures explicitly retained: the frozen dispatch double-ownership
  defect and the ledger-receipt.json exact-diff/parent-sha failure are both
  recorded above exactly as found, neither waived nor corrected.
- Artifacts report measured hashes and per-path provenance: yes, in
  `preservation-package.json` and this report; no unavailable-source
  impediment occurred, so none is fabricated.
- No experiment run, scientific transition, historical completion
  normalization, or independent-review fabrication occurred: confirmed. This
  report draws no conclusion about GOAL-CRYPTO-001's FINAL_NO_CANDIDATE
  disposition, GOAL-MLKEM-002's completed status, or any hypothesis; it only
  reports what bytes exist, where, and how they compare.

## Artifact paths produced by this task

- `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-1f4d53/tasks/TASK-20260907-ad00af/preservation-package.json`
- `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-1f4d53/tasks/TASK-20260907-ad00af/recovery-report.md`
