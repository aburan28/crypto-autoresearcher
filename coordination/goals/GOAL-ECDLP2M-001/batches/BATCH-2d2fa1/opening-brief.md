# Opening brief: EXP-QSP-70b731 custody successor re-ruling, 2026-10-02 (session rm3mrv)

The top-level session wrote this brief before dispatching the Coordinator
subagent. It carries the result of DEC-20260929-01ea31 NA-3, which the
subagent cannot compute because it has no shell. It is not a record; the
Coordinator's decision is.

## 1. Why now

Slot 1 of GOAL-ECDLP2M-001 has been held, unopened, for the EXP-QSP-70b731
custody successor since DEC-20260928-157d40. That hold has been carried
through DEC-20260928-65c6d7 R-CUSTODY, DEC-20260929-01ea31 R-CUSTODY
(FINDING-QSP-DOUBLE-DECLARATION), DEC-20260929-1eded2, DEC-20260929-54dcd8 and
DEC-20260929-7257b2.

Slot state now:
- Live claims, 2026-10-02 after git fetch: 2 of 3.
  - TASK-20260929-749b50: the BATCH-35bdda lane-B v3 producer. It has returned
    and is fixing one YAML scalar.
  - TASK-20261002-23efd5: the BATCH-f435ab NISTBIN v3 producer, running.
- Slot 1 is free.

DEC-20260929-01ea31 NA-3 named the recheck that has to come before any
custody opening. The session has now performed it (section 2).

## 2. DEC-20260929-01ea31 NA-3 result

The session read queue metadata and file NAMES only (`git ls-files`). No run
file was opened.

**(a) The four QSP queues.** `research_dispatch.py --claims refs`
(2026-10-02) gives the same result for each:

| Queue | Gates passed | Ready card | Live claims |
|---|---|---|---|
| BATCH-2c4a9c | 11 | TASK-20260921-9f84a3 | 0 |
| BATCH-9dbda3 | 11 | TASK-20260921-f80a35 | 0 |
| BATCH-ed05f2 | 11 | TASK-20260921-a504da | 0 |
| BATCH-ee209c | 11 | TASK-20260921-de261e | 0 |

The branch `exec/qsp-70b731-run-20260921` is still at 8164cc5b96, unchanged
since 2026-09-21. There is no bus reply from coordinator-qsp-run-20260921 to
MSG-20260929-fb57f1 or to any earlier pointer. Its last bus messages are
MSG-20260921-*.

**(b) Paths under `experiments/EXP-QSP-70b731/runs/` on main, by name only.**
There are 158 files: `.gitkeep` plus 16 `RUN-QSP-*` directories with 8 to 11
files each.

Which queue card declares each path (in `artifact_paths`, exact or as a
directory prefix), and whether any archive binds it (receipt or queue
`path_sha256`):
- **.gitkeep (1 file).** Declared by BATCH-93320c TASK-20260918-53664e
  (completed). Bound by TASK-20260920-e51da0 (receipt; queue commit
  2bf438ddde).
- **130 files** (e.g. RUN-QSP-097ecd/*). Declared by three queued executor
  cards: BATCH-9dbda3 TASK-20260921-f80a35, BATCH-ed05f2 TASK-20260921-a504da
  and BATCH-ee209c TASK-20260921-de261e. Bound by nothing.
- **11 files** (RUN-QSP-1df59e/*). Declared by 9dbda3 f80a35 and ee209c
  de261e. Bound by nothing.
- **8 files** (RUN-QSP-715b58/*). Declared by 9dbda3 f80a35 and ed05f2
  a504da. Bound by nothing.
- **8 files** (RUN-QSP-cec70a/*). Declared by ed05f2 a504da only. Bound by
  nothing.

**Correction to FINDING-QSP-DOUBLE-DECLARATION.** BATCH-2c4a9c's run card
TASK-20260921-9f84a3 does NOT declare any of these files. Its
`artifact_paths` name `RUN-QSP-12a389/*`, and no such directory exists on
main. The 157 run files that do exist are each already declared by one to
three queued executor cards in the OTHER three QSP queues. None of those
cards was ever claimed or completed, and no archive binds any run file. The
double ownership that 01ea31 feared from a successor already exists between
the QSP lane's own queues.

**(c) Do the tools refuse a path declared by two queues?**
- `research_dispatch.py` refuses double ownership only WITHIN one queue
  (`tools/research_dispatch.py` line 881, "artifact path {path} is owned by
  both {previous_owner} and {task}"). Each QSP queue renders with all 11
  gates passing despite the cross-queue declarations, so cross-queue double
  declaration is NOT refused.
- `validate_ledger.py` raises no double-declaration error. The 122-error
  baseline contains only schema errors on the run manifests ("expected
  top-level key 'run'").

## 3. What the Coordinator must rule (R-CUSTODY re-ruling)

1. Does section 2 change FINDING-QSP-DOUBLE-DECLARATION, and does the slot-1
   hold continue, open, or get released? Record reasons, recheck and revisit
   per CLAUDE.md rule 9. Use the original R-CUSTODY preconditions in
   DEC-20260928-157d40, DEC-20260928-65c6d7 and DEC-20260929-01ea31.
2. If it opens: the custody successor's chain needs lifting, by name, the
   `experiments/EXP-QSP-70b731/runs/` excluded read, which TASK-20260928-cdf0a4
   imposed on its validator card only. It also needs a ruling on how its
   snapshot binds run files that three queued cards already declare.
   Options include a binding supersession ruling on those cards, or a
   content_first snapshot declaring the paths with the prior declarers named.
   Any such ruling is the Coordinator's; this brief proposes nothing.
3. If it does not open: say what clears the hold and what the slot does
   meanwhile. The portfolio orders from DEC-20260929-7257b2 and
   DEC-20260929-54dcd8 are S1 v4 (54dcd8 CH-B) and then U-HOLDH.

## 4. Pre-minted ids (`allocate_id.py --next`, all `--check` OK)

- BATCH-2d2fa1
- DEC-20261002-86a7e0, DEC-20261002-e0aa2b, DEC-20261002-f8314c
- TASK-20261002-0e76e7, -230174, -345dbd, -5e1246, -7eb899, -84621d, -9a734c,
  -ba36a5, -f65334

Name any you leave unused. This brief sits in the BATCH-2d2fa1 directory as
the session's working choice.

## 5. Excluded reads still binding unless your decision lifts one by name

- experiments/EXP-QSP-70b731/runs/ (content); file names are given above
- experiments/EXP-FROB-30006a/
- ref origin/cursor/semaev-2015-audit-program-5b8b
- PR #1377
- branch cursor/ecdlp2m-revision-design-3d1a
