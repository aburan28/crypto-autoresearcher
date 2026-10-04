# Recovery Report — TASK-20260907-7f1799

Goal: GOAL-SIG-001 · Batch: BATCH-0c2d2a
Role: executor (custody/preservation task, zero scientific runs, zero status changes)

## Session / model record (honest, unfabricated)

- Runtime: Claude Code subagent, role `executor`.
- Requested policy per handoff (`inference.policy`): `executor-implementation`.
- Environment variables `AUTORESEARCH_POLICY` / `AUTORESEARCH_BACKEND` were **unset**
  in this session at execution time — no adapter-resolved policy/backend record was
  available to read; this is stated plainly rather than invented.
- Model actually answering this session: Claude Sonnet 5 (model id `claude-sonnet-5`),
  per the runtime's own system identification. No Bedrock. No fallback model was
  invoked and none is claimed.
- Repo HEAD at time of work: `eee9ec41f02b045a893fe166da9e621b71256d8f` (working
  tree carries 3 unrelated pre-existing modified files outside this task's
  write_scope — `.github/workflows/claude-pr-review.yml`,
  `.github/workflows/claude.yml`, and one more — untouched by this task).
- No git checkout, reset, or historical edit was performed. All historical
  reads used `git cat-file -e <rev>`, `git ls-tree -r --name-only <rev>`, and
  `git show <rev>:<path>` only, restricted to the revisions/paths named in
  `source-git-evidence.json` and `intake.md`.

## What was recovered, from where, at what revision

### Revision `fed33c0986e64f2af1fc989931d8c37ef6aa3ef5` (TASK-20260725-712 ledger archive commit; parent `723ae42d254030162d60f043d6b2ef214d2504d9`, both verified present with `git cat-file -e`)

| Path | Recovered | sha256 |
|---|---|---|
| `ledger/evidence/EV-SIG-007.yaml` | yes | `fca156654bbfa3fd0839576454cbd184c074d08ef0882b31c54bde65258232f9` |
| `ledger/evidence/EV-SIG-010.yaml` | **NO — path absent from this commit's tree** | n/a |
| `ledger/decisions/DEC-20260725-028.yaml` | yes | `9d36f874065addf1bf0ce30d6b43891ced564edea47bb4ec86811145edff0f32` |
| `ledger/goals/GOAL-SIG-001.yaml` | yes | `bca8f614b479204560f2daad7f74ce9b97024c62dcddafc6df5f88719fb5ca42` |
| `coordination/.../TASK-20260725-711/red_team_report.yaml` | yes | `37f43ba9d9f2513f92d386db0f9ec139215ef3b996997fa22ebe085ce9d61861` |
| `coordination/.../TASK-20260725-711/falsification_review.md` | yes | `b2be4397a97155f816cad88f61c60cf1cab3d268406ab62fa747212ba6fdf710` |
| `coordination/.../TASK-20260725-712/ledger-receipt.json` | yes | `12650a3fb6377010f8ac0d6720d6fe9a98e081e39b001005c1a2b10a7fe9321f` |

Every recovered hash here **matches exactly** the `path_sha256`/`path_hashes`
values already declared for these paths in `source-git-evidence.json`. No
independent Git blob comparison found a mismatch against the declared values.

### Revision `95c1b4f9a781ae05dbb17b0984e18df388c94589` (TASK-20260725-710 snapshot archive commit; parent `a764af80b18dd53c3c303c992e13314d13034918`, both verified present)

| Path | Recovered | sha256 |
|---|---|---|
| `coordination/.../TASK-20260725-709/d6_null_protocol.yaml` | yes | `69ebeb7ab5a711f417d223209604752c5683ca99cd5929ea1381bc41a64575e0` |
| `coordination/.../TASK-20260725-709/protocol_design_note.md` | yes | `21bd1bf7d5d313a58fbf8d475dcbed37378bffdb62dd1fa7e785ba62599807c6` |
| `coordination/.../TASK-20260725-710/snapshot-receipt.json` | yes | `397552dc68b1b258a24aa8bc2b26da14a8ade6e2e44794ab56c5c08da3fb793e` |

All three match `source-git-evidence.json`'s declared `path_sha256` exactly.

### Current working-tree counterparts (read from disk at task time, not committed by this task)

All of the above paths' current on-disk content was also read and hashed:
`ledger/evidence/EV-SIG-007.yaml`, `ledger/evidence/EV-SIG-010.yaml`,
`ledger/decisions/DEC-20260725-028.yaml`, `ledger/goals/GOAL-SIG-001.yaml`,
`coordination/.../TASK-20260725-711/red_team_report.yaml`,
`coordination/.../TASK-20260725-711/falsification_review.md`,
`coordination/.../TASK-20260725-712/ledger-receipt.json`,
`coordination/.../TASK-20260725-709/d6_null_protocol.yaml`,
`coordination/.../TASK-20260725-709/protocol_design_note.md`,
`coordination/.../TASK-20260725-710/snapshot-receipt.json`, and both
`coordination/.../BATCH-002/dispatch_queue.json` and
`coordination/.../BATCH-0c2d2a/original-dispatch-queue.json`.
All are present and readable; all sha256 values and full base64 bytes for
every one of these are recorded in `preservation-package.json`.

## The confirmed defect (per-field provenance)

The historical commit `fed33c0986e64f2af1fc989931d8c37ef6aa3ef5` wrote to path
`ledger/evidence/EV-SIG-007.yaml` a YAML document whose body reads
`id: EV-SIG-007` but whose entire content is the D6-null-protocol
review-PASS evidence text — the same text (apart from the `id:` field) that
every other artifact at that revision (`red_team_report.yaml`,
`falsification_review.md`, `DEC-20260725-028.yaml`, `GOAL-SIG-001.yaml`, and
the archive receipt's own `path_sha256` map) calls `EV-SIG-010`. Concretely:

- The bytes at `ledger/evidence/EV-SIG-007.yaml@fed33c0` hash to
  `fca156654bbfa3fd0839576454cbd184c074d08ef0882b31c54bde65258232f9` — the
  **same hash** `source-git-evidence.json` declares for
  `ledger/evidence/EV-SIG-010.yaml`.
- `git show fed33c0:ledger/evidence/EV-SIG-010.yaml` fails
  (`fatal: path ... exists on disk, but not in fed33c0...`), and
  `git ls-tree -r --name-only fed33c0` confirms the path is simply absent from
  that commit's tree. No historical `EV-SIG-010.yaml` blob exists at this
  revision to recover.
- The historical `ledger-receipt.json` for TASK-20260725-712 declares
  `record_ids: ["EV-SIG-007", ...]` and keys `artifact_sha256` on
  `ledger/evidence/EV-SIG-007.yaml`. The **current** on-disk
  `ledger-receipt.json` at the same path instead declares
  `record_ids: ["EV-SIG-010", ...]` and keys `artifact_sha256` on
  `ledger/evidence/EV-SIG-010.yaml`, using the identical hash value
  `fca156654b...`. That means the receipt file was edited in place at some
  point after `fed33c0` to say the correct id/path, without any corresponding
  git history at the cited revisions moving the actual ledger blob to
  `ledger/evidence/EV-SIG-010.yaml`.
- This is exactly the dispatch defect intake.md names verbatim: "archive task
  TASK-20260725-712 commit must change exactly declared archive and source
  artifacts (missing `['ledger/evidence/EV-SIG-010.yaml']`; extra
  `['ledger/evidence/EV-SIG-007.yaml']`)".
- The genuinely-independent measurement record `ledger/evidence/EV-SIG-007.yaml`
  (SIGN21 n=21 measurement, rank_acc=265950 etc.) that exists on disk **today**
  is NOT byte-identical to the fed33c0 blob (current sha256
  `3283e147b9a9f1d53c37835e2cbf8c8c0427a5b9fed527751272de88352e4101` vs.
  historical `fca156654b...`). The current file's own text documents a
  `relocation`/`recreated: v3 2026-07-26` history from `ledger/EV-SIG-007.yaml`
  and cites `CORR-20260802-014` / `DEC-20260802-001` as the repair record for
  its own known schema defect (missing top-level `evidence:` key). This
  executor did **not** attempt to reconstruct, judge, or re-derive that prior
  SIGN21 measurement content; the historical `fed33c0` state of
  `EV-SIG-007.yaml` genuinely was the mislabeled D6-review text, and whatever
  the true pre-`fed33c0` SIGN21 record looked like is outside the two cited
  revisions this task was authorized to inspect.
- The current `ledger/evidence/EV-SIG-010.yaml` on disk (sha256
  `1328576b7d16cbfb6bdfe4e802089ac8503ce1fea865ee89babf943e19a4d3e8`) is
  content-identical to the mislabeled fed33c0 blob **except for the `id:`
  field** (`EV-SIG-010` vs. `EV-SIG-007`). No commit at either cited revision
  shows the corrective write that produced this file at its correct path; it
  postdates both cited revisions and this task did not search beyond them.

## Minor citation-correction drift observed (not defects, recorded for completeness)

Diffing historical vs. current bytes for the producer/review artifacts turned
up only small, later citation fixes, unrelated to the EV-SIG-007/010 path
defect:

- `d6_null_protocol.yaml` / `protocol_design_note.md`: `EV-SIG-006` →
  `EV-SIG-009` (repairs/citation list), and a comment `KN-FIND-011` →
  `KN-FIND-027`.
- `red_team_report.yaml` / `falsification_review.md`: same `EV-SIG-006` →
  `EV-SIG-009` fix, plus `EV-SIG-007` → `EV-SIG-010` in the "next concrete
  action" text (now correctly naming the archived record).
- `DEC-20260725-028.yaml`: `evidence_refs` entry `EV-SIG-007` → `EV-SIG-010`,
  and `KN-FIND-011` → `KN-FIND-027` in `knowledge_promotion.not_warranted`.
- `GOAL-SIG-001.yaml`: extensive later additions (budget amendments, a
  standing "fund every goal" directive block) unrelated to this defect; none
  alter `completion_criteria` or hypothesis status per their own text.
- `snapshot-receipt.json` for TASK-20260725-710: byte-identical historical vs.
  current — no drift.
- `dispatch_queue.json` (BATCH-002) and `original-dispatch-queue.json`
  (BATCH-0c2d2a): byte-identical to each other and both hash to
  `a70fdeb6af16529577e5cced25adb59ced71ba6c55c800cdfce2823da0da698f`, matching
  intake.md's declared "Original SHA256" exactly.

## Controls performed

- **Compare all original hashes before and after**: every historical hash
  recovered via `git show` was compared against the `path_sha256`/`path_hashes`
  values already declared in `source-git-evidence.json`; all matched exactly
  (see tables above). No hash was retargeted or recomputed to match a desired
  answer.
- **Independent Git blob comparison**: `git cat-file -e` confirmed all four
  cited commit shas exist in this clone before any `git show` was attempted;
  `git ls-tree -r --name-only fed33c0...` was used as an independent structural
  check that confirmed `ledger/evidence/EV-SIG-010.yaml` is genuinely absent
  from that tree (not just unreadable by path).
- **Intentional bad-hash/path-map rejection control**: this executor did not
  substitute, remap, or silently correct the observed `EV-SIG-007`/`EV-SIG-010`
  path mismatch anywhere in `preservation-package.json` — the historical blob
  is preserved and reported exactly as committed, under its *actual* path
  (`ledger/evidence/EV-SIG-007.yaml`), with the mismatch against its
  *declared* path (`ledger/evidence/EV-SIG-010.yaml`) called out explicitly as
  a defect rather than silently fixed. No new hash was fabricated for the
  missing historical `EV-SIG-010.yaml`; its entry in `preservation-package.json`
  carries `recovered_bytes_base64: null` and `recovered_sha256: null` with an
  explicit `status: UNAVAILABLE` and reason.

## Explicit unresolved / could-not-recover items

1. **Historical `ledger/evidence/EV-SIG-010.yaml` at revision `fed33c0...`
   does not exist and cannot be recovered.** `git show` fails and
   `git ls-tree` confirms absence from that commit's tree. This is a genuine
   gap in the cited historical record, not a read failure on this executor's
   part — the archive commit never wrote that path. **Checkable remedy**: a
   Coordinator decision could authorize widening the git-history search beyond
   `fed33c0`/`95c1b4f` (e.g., `git log --all --follow -- ledger/evidence/EV-SIG-010.yaml`)
   to find the actual commit that later created the correct-id file, if that
   provenance is wanted; this executor did not perform that broader search
   because it falls outside "the exact revisions ... named in
   source-git-evidence.json."
2. **The true pre-`fed33c0` content of `ledger/evidence/EV-SIG-007.yaml`
   (the SIGN21 measurement record, before it was overwritten by the mislabeled
   D6-review text) was not reconstructed by this task.** It is outside the
   two revisions this task was authorized to inspect, and reconstructing it
   would require judging which prior commit holds the "real" SIGN21 content —
   an evidentiary/historical-repair decision, not a custody-preservation act.
   The current on-disk `EV-SIG-007.yaml` already documents its own recovery
   lineage (`recreated: v3 2026-07-26 ...`) and a still-open schema defect
   under `CORR-20260802-014` / `DEC-20260802-001`; this report defers to that
   documented chain rather than re-deriving it.
3. No other read failures occurred. All other paths named in
   `source-git-evidence.json`, `intake.md`, and the current-state counterparts
   were readable and are recorded in `preservation-package.json`.

## Explicit non-actions (per constraints)

- No experiment was run; `experiment_runs_authorized: 0` was honored.
- No hypothesis, goal, or experiment status was changed.
- No commit was made; all output is confined to this task's declared
  `write_scope`.
- No hash was retargeted, no ID was remapped, no archive was bypassed, and no
  historical completion was fabricated. The `EV-SIG-007`/`EV-SIG-010` path
  mismatch is reported, not corrected.

## Deliverables

- `coordination/goals/GOAL-SIG-001/batches/BATCH-0c2d2a/tasks/TASK-20260907-7f1799/preservation-package.json`
  — 12 entries: 10 fully recovered (historical + current bytes as base64, both
  sha256), 1 explicitly `UNAVAILABLE` (historical EV-SIG-010 at fed33c0), and
  the current EV-SIG-010 counterpart recorded alongside it.
- This report.
