# Recovery report — TASK-20260907-5b8740

Custody/preservation task only. Zero scientific runs, zero status changes,
no ICEX measurement authorized or performed. Working tree checked at repo
HEAD `51dbb8ed15fb0ff5b4a2b5b19c3ab1158700ba6f`; the two files shown as
locally modified by `git status` (`.github/workflows/claude-pr-review.yml`,
`.github/workflows/claude.yml`) are pre-existing and unrelated to any path
touched by this task — nothing this task read or wrote is dirty.

All bytes below were obtained with `git show <rev>:<path>` (read-only Git
object inspection) exactly as authorized for the revisions/paths named in
`source-git-evidence.json`, `intake.md`, and this task's read_scope. No
`checkout`/`reset` was run, and no historical object was edited.

## Method

Every entry in `preservation-package.json` records `source_revision`, `path`,
`sha256` (of the recovered bytes), `content_base64` (the exact recovered
bytes), `current_counterpart_sha256` (the sha256 of the same path at current
HEAD, where one exists), and `content_difference_from_current` (an explicit
statement of identity or difference). All sha256 values below were
independently recomputed by this task with `sha256sum` over `git show`
output; none are copied from prior records without recomputation, except
where explicitly marked "as declared" for comparison purposes.

## What was recovered, and from where

### 1. DEC-20260731-003 at the cited revision `e948de55e0590f9c8ccbeed4f13996039e8353db`

`git show e948de55e0590f9c8ccbeed4f13996039e8353db:ledger/decisions/DEC-20260731-003.yaml`
recovers the **historical ICEX protocol-PASS coordinator decision**
(`decision: support`, target_ids `GOAL-ICEX-001`, `RQ-ICEX-001`,
`TASK-20260731-021`, `TASK-20260731-023`), sha256
`7005cefbdb2c411650c2c5db21da47c39cbdb2af737796a6e50b3d852ac0043f`. This
matches the sha256 that commit e948de55's own
`coordination/.../TASK-20260731-024/ledger-receipt.json` declared for this
exact path at commit time (verified from the e948de55 copy of that receipt,
also in the package). **This is the only surviving copy of these decision
bytes anywhere in this clone's history**: the current file at
`ledger/decisions/DEC-20260731-003.yaml` (sha256 `404d25d0...`) has since
been completely overwritten by an unrelated `GOAL-MLKEM-003` / `H-MLKEM-011`
decision (first appears via `7d639bb4f` "Archive GOAL-MLKEM-003 dual-attack
campaign...", later schema-corrected by `3e610197d` / `CORR-20260731-003`,
merged to main via `487d94a3d` / `0f944733a`).

### 2. Current DEC-20260731-015

`git show HEAD:ledger/decisions/DEC-20260731-015.yaml` recovers the **current**
content at this path: an unrelated `GOAL-ECDLP-001` BATCH-021 (`EXP-DS-001`,
RC-21 non-execution, `decision: pause`) coordinator decision, sha256
`744a0d2009339a1989d58b9dcee8d2e230c9358104ce9ab5bc50b7b1b97584be`.
`git log --all --oneline -- ledger/decisions/DEC-20260731-015.yaml` shows
**exactly one commit ever wrote this path**, `df07272db` ("coord:
GOAL-ECDLP-001 BATCH-021 RC-21 non-execution; remint TASK-057 NOT APPROVED"),
whose content is this same ECDLP record. No ICEX-content object was ever
committed at this path — see "Unresolved / could not be recovered" below.

### 3. The exact original goal blob, and its remap provenance

`ledger/goals/GOAL-ICEX-001.yaml` was recovered at **four** relevant
revisions, plus current HEAD, to reconstruct the "goal blob mismatch [that]
accompanies ID mapping" named in `intake.md`:

| revision | sha256 | next_action decision citation |
|---|---|---|
| `35e8d4e2` (parent of the archive commit) | `f0e9b91a...` | (pre-archive; no ICEX decision cited yet) |
| `e948de55` (the archive commit itself) | `f83f3c9a...` | `DEC-20260731-003 / EV-ICEX-001` |
| `b1dfd9865` ("remap colliding ledger IDs") | `9f031a9e...` | `DEC-20260731-011 / EV-ICEX-001` |
| `91e404845` ("remap DEC IDs after #75") | `04e78f67...` | `DEC-20260731-015 / EV-ICEX-001` |
| `HEAD` (current) | `a2047eba...` | (in `prior_selection.next_action` prose) `DEC-20260731-015 / EV-ICEX-001` |

**The mismatch, precisely stated and independently verified:**
`coordination/goals/GOAL-ICEX-001/batches/BATCH-001/dispatch_queue.json`
carries an `archive` block for `TASK-20260731-024` that **declares** (plans)
the expected post-commit sha256 of `ledger/goals/GOAL-ICEX-001.yaml` as
`04e78f671eeac78ca8ae87bcc95c00bfc25ebc96185f511ee2b26b4a36c95e7b`. This task
recomputed sha256 over `git show` at every commit that ever touched this
path and found that value matches **only** the `91e404845` blob — a commit
that postdates `e948de55` by two subsequent ID-remap merges. What was
**actually** committed at `e948de55` (the commit the archive block was
supposedly describing) has sha256 `f83f3c9a...`, which is what
`coordination/.../BATCH-1104d5/source-git-evidence.json`'s recorded
`path_hashes` (the *measured*, post-commit field, as opposed to the
*declared* `path_sha256` field) independently confirms. In short: the
archive's **declared** hash for the goal blob describes a state of the file
that did not exist yet at commit time and only came to exist after two later
ID-collision remap merges; the **actual** committed state was different and
is separately preserved. Both are included in the package, verifiably.

**The ID-mapping chain** (three sequential collisions on the same day,
2026-07-31): `GOAL-ICEX-001.yaml`'s next_action citation for the ICEX
protocol-PASS decision moved `DEC-20260731-003` → `DEC-20260731-011` (at
`b1dfd9865`) → `DEC-20260731-015` (at `91e404845`), while the underlying
`ledger/decisions/*.yaml` file at the original id (`-003`) was never renamed
to follow the citation. Each intermediate id the citation moved to was
**already independently claimed by unrelated content** before or by the time
of the remap:
- `DEC-20260731-011.yaml` (current HEAD) is a `GOAL-ECTD-001` BATCH-001
  decision (sha256 `5191a1d1...`), and its own `prior_id_collision_note`
  field records it was itself moved here from a colliding `DEC-20260731-006`.
- `DEC-20260731-015.yaml` (current HEAD) is the `GOAL-ECDLP-001` BATCH-021
  decision described in item 2 above.
- `DEC-20260731-003.yaml` (current HEAD) is the `GOAL-MLKEM-003` decision
  described in item 1 above.

None of these three collisions were caused by this recovery task; all three
predate it and are recovered here exactly as committed.

### 4. Other historical/current archive artifacts (byte-identical, verified)

The following were recovered at both their cited historical revision and
current HEAD and found **byte-for-byte identical** (same sha256 at both
revisions — full values are in `preservation-package.json`):
- `ledger/evidence/EV-ICEX-001.yaml` (`c6bc3a3d...`)
- `coordination/goals/GOAL-ICEX-001/batches/BATCH-001/tasks/TASK-20260731-023/red_team_report.yaml` (`312c0707...`)
- `coordination/goals/GOAL-ICEX-001/batches/BATCH-001/tasks/TASK-20260731-023/falsification_review.md` (`4b1d57b1...`)
- `coordination/goals/GOAL-ICEX-001/batches/BATCH-001/archives/TASK-20260731-022/snapshot-receipt.json` (`7147cd96...`)
- `coordination/goals/GOAL-ICEX-001/batches/BATCH-001/tasks/TASK-20260731-021/ic_exponent_protocol.yaml` (`36843909...`)
- `coordination/goals/GOAL-ICEX-001/batches/BATCH-001/tasks/TASK-20260731-021/protocol_design_note.md` (`b7bd62aa...`)

`coordination/goals/GOAL-ICEX-001/batches/BATCH-001/archives/TASK-20260731-024/ledger-receipt.json`
**differs** between `e948de55` and current HEAD: the historical version
declares `record_ids: ["EV-ICEX-001", "DEC-20260731-003", "GOAL-ICEX-001"]`
with `ledger/decisions/DEC-20260731-003.yaml` hashed at `7005cefb...`
(consistent with what was actually committed at e948de55); the current
version instead declares `record_ids: ["EV-ICEX-001", "DEC-20260731-015",
"GOAL-ICEX-001"]` with `ledger/decisions/DEC-20260731-015.yaml` hashed at
`05627e11dac0014ec866683d349942d07682f0a3d1f9e2a0a68917a2e3beeebc` — a value
that, per item below, does not match any actual object ever committed at
that path. This receipt file was therefore edited after its original commit
(by the same `b1dfd9865`/`91e404845` remap merges) to follow the ID
relabeling, without a corresponding object ever being created at the new
path. `git log` on this path confirms three touching commits:
`e948de55` (create), `b1dfd9865`, `91e404845` (both remaps).

`coordination/goals/GOAL-ICEX-001/batches/BATCH-001/dispatch_queue.json`
(current == original; sha256 `7e308a325818c217c458bd9689e796b18eafaeb5f5e43bf0160aabdca0099c46`)
matches both `intake.md`'s stated "Original SHA256" and the
`historical_queue_sha256` pin recorded in the current `GOAL-ICEX-001.yaml`'s
`integrity_recovery_20260907` block, and is byte-identical to this batch's
own captured copy at `coordination/goals/GOAL-ICEX-001/batches/BATCH-1104d5/original-dispatch-queue.json`
(also included). No drift found.

## Unresolved / could not be recovered

**`ledger/decisions/DEC-20260731-015.yaml` containing the ICEX protocol-PASS
content was never actually committed anywhere in this clone's git history**
(reachable or unreachable). `git log --all -- ledger/decisions/DEC-20260731-015.yaml`
returns exactly one commit, and its content is the unrelated
`GOAL-ECDLP-001` record described above. Per this task's constraints, this
is reported as an infrastructure/custody fact and **not** treated as
negative evidence about anything scientific, and no substitute or fabricated
object was created in its place.

As a purely diagnostic, clearly-labeled check (not stored as a "recovered"
artifact, and not a claim that such a file was ever committed): taking the
byte-exact e948de55 `DEC-20260731-003.yaml` content and changing only the
`id:` field to `DEC-20260731-015` reproduces the hash `05627e11...` that the
archive block/receipt declared for that path exactly:

```
git show e948de55e0590f9c8ccbeed4f13996039e8353db:ledger/decisions/DEC-20260731-003.yaml \
  | sed 's/id: DEC-20260731-003/id: DEC-20260731-015/' | sha256sum
# 05627e11dac0014ec866683d349942d07682f0a3d1f9e2a0a68917a2e3beeebc
```

This explains the declared hash as a planned single-field id substitution
that the archiving process apparently intended but never actually executed
against the real file path — it does not manufacture or assert the
existence of a historical object, and this derived byte string is recorded
in `preservation-package.json`'s `unresolved[0].diagnostic_note_not_a_recovery`
field only, separate from and never mixed into the `entries` array of
actually-recovered git objects.

**Remedy** (not performed by this task; outside Executor authority and this
task's write_scope): a Coordinator correction record could mint a fresh ID
for the ICEX PASS decision, cite this preservation package and the e948de55
blob as source content, and update `GOAL-ICEX-001.yaml`'s `next_action`
accordingly — an additive correction, never an edit of `e948de55`,
`DEC-20260731-003.yaml`, or `DEC-20260731-015.yaml` as they stand today.

## Controls run

- **Compare all original hashes before and after**: every historical entry's
  sha256 was recomputed directly from `git show` output in this session (not
  copied from any prior record) and cross-checked against declared values in
  `source-git-evidence.json` / `original-dispatch-queue.json` / the BATCH-001
  archive blocks; all matches and mismatches are stated explicitly above and
  in `preservation-package.json`.
- **Independent Git blob comparison**: all paths above were re-fetched with
  a second, independent `git show`/`sha256sum` pass immediately before
  writing the final package (see `finalize.py` output in this session); no
  value in the package was taken from a single unverified read.
- **Intentional bad-hash/path-map rejection control**: this task did not
  substitute, retarget, or "fix" any hash or path mapping. Every declared
  hash mismatch found (e.g. `05627e11...` not matching any real object;
  `04e78f67...` matching a later commit than the one it was declared for) is
  reported as a mismatch, not corrected, remapped, or silently resolved.

## No scientific action taken

- `scientific_runs = 0`. No experiment was run, no hypothesis/goal/experiment
  status was changed, and no ICEX measurement was authorized or implied by
  this recovery.
- `original_byte_changes = 0`. No historical byte recovered above was
  altered; all are reproduced verbatim as base64 in `preservation-package.json`
  and independently re-hashable from that field alone.
- This report and the package record observations and provenance only;
  interpretation of what corrective ledger action (if any) should follow
  is left to the Coordinator, per this task's authority boundary.

## Model / session provenance

- Requested policy (per this task's handoff `inference` block):
  `executor-implementation`, `reasoning_effort: null` (medium per
  `orchestration/model-policies.yaml`'s role table), `fallback_allowed:
  false`, `degraded_allowed: false`.
- Runtime: Claude Code (this session), model `claude-sonnet-5` (as stated in
  this runtime's own system context). This task did not attempt to probe or
  invent an independent model-identity verification beyond what the runtime
  itself reports; no fallback occurred and none is claimed.
- Session reference: `session_01NV1n82ki22i5u8Db7JPpWj`.
- Repo HEAD at execution time: `51dbb8ed15fb0ff5b4a2b5b19c3ab1158700ba6f`.
- No Bedrock backend was used or requested.

## Completion gate check (per handoff)

- "All original source bytes remain unchanged and original failures are
  explicitly retained" — met: nothing under `ledger/`, `coordination/goals/GOAL-ICEX-001/batches/BATCH-001/`,
  or the cited historical commits was modified; the RC-type mismatches found
  are recorded, not repaired.
- "Artifacts report measured hashes and per-path provenance or explicit
  unavailable-source impediments" — met: every entry in
  `preservation-package.json` carries a measured sha256 and a
  `content_difference_from_current` note; the one genuinely unavailable
  object is reported by name, revision, and remedy above.
- "No experiment run, scientific transition, historical completion
  normalization or independent-review fabrication occurred" — met: zero
  runs, zero status changes, and this report explicitly declines to
  characterize any prior review outcome as passed/failed beyond what the
  cited records themselves already state.
