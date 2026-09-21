# Repair Report — TASK-20260806-7fcdf8 (dual-device RANK-1 stamp repair)

**Task:** TASK-20260806-7fcdf8 (BATCH-6fe3c2, GOAL-AES-003)
**Role:** executor
**Date:** 2026-08-07 (UTC)
**Governing decision:** DEC-20260804-73977c, rationale D-7 (adopts the dual-device
repair: amended successor stampset + superseding completion record)
**Assessment:** `coordination/goals/GOAL-AES-003/batches/BATCH-b41ba9/tasks/TASK-20260806-7a980b/repair-assessment.md`
**Write scope:** `coordination/goals/GOAL-AES-003/batches/BATCH-6fe3c2/tasks/TASK-20260806-7fcdf8/`
**Immutable tree (read-only, rule 4):** `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/`

---

## 1. Source files read (read-only)

| file | purpose |
|---|---|
| `coordination/goals/GOAL-AES-003/batches/BATCH-b41ba9/tasks/TASK-20260806-7a980b/repair-assessment.md` | M01–M20 definitions, A0–A14 anchors, intervals, classification |
| `coordination/goals/GOAL-AES-003/batches/BATCH-b41ba9/tasks/TASK-20260806-7a980b/repair-recommendation.json` | machine-readable event/basis summary (cross-check) |
| `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/budget_stamps.jsonl` | original stream (5 lines, ends at `preregistration_written` = A4) |
| `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/RESULTS.json` | arms aggregates, `parser_check`, budget block (`runs_used: 8`, `maximum_runs: 30`) |
| `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/PREREGISTRATION.md` | frozen predictions (content context) |
| `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/raw_{M1,CTRL}_r{4,5,6}[_rand].jsonl` (8 files) | 42-line structure, summary lines, mtimes (anchors A8–A11) |
| `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/nibble_decay.c`, `nibble_decay` | mtimes (anchors A5, A6) |
| `ledger/decisions/DEC-20260804-73977c.yaml` | D-3 (defect), D-7 (adopts dual-device repair) |

Note: the handoff named the assessment under `BATCH-041b14`; the file actually
resides under `BATCH-b41ba9` (matching the dispatch plan's read_scope). No
other discrepancy was found.

## 2. Anchor verification (filesystem, local mtime + 7 h = UTC)

| anchor | event | UTC (assessment) | local mtime observed | match |
|---|---|---|---|---|
| A0 | start / binding_stop | 01:14:16Z / 01:54:16Z | (in budget_stamps.jsonl L1) | ✓ |
| A4 | preregistration_written (last stamp present) | 01:21:30Z | budget_stamps.jsonl L5 | ✓ |
| A5 | nibble_decay.c mtime | 01:27:08Z | 2026-08-05T18:27:08Z | ✓ |
| A6 | nibble_decay mtime | 01:27:14Z | 2026-08-05T18:27:14Z | ✓ |
| A7 | PREREGISTRATION.md mtime | 01:28:55Z | 2026-08-05T18:28:55Z | ✓ |
| A8 | raw_M1_r4, raw_M1_r5 mtime | 01:32:30Z | 2026-08-05T18:32:30Z | ✓ |
| A9 | raw_CTRL_r4, raw_CTRL_r5, raw_M1_r6 mtime | 01:32:31Z | 2026-08-05T18:32:31Z | ✓ |
| A10 | raw_CTRL_r6 mtime | 01:32:32Z | 2026-08-05T18:32:32Z | ✓ |
| A11 | raw_M1_r6_rand 01:33:02Z, raw_CTRL_r6_rand 01:33:03Z | 01:33:02–03Z | 2026-08-05T18:33:02Z / 18:33:03Z | ✓ |
| A12 | RESULTS.json mtime | 01:33:49Z | 2026-08-05T18:33:49Z | ✓ |
| A13 | budget_stamps.jsonl mtime (content still ends at A4) | 01:34:10Z | 2026-08-05T18:34:10Z | ✓ |
| A14 | binding_stop (declared) | 01:54:16Z | budget_stamps.jsonl L1 | ✓ |

Raw-file structure verified: all 8 `raw_*.jsonl` are 42 lines (1 matrix-gate
header + 40 trial records + 1 summary line); summary aggregates match
`RESULTS.json` `arms` exactly (e.g. M1 r6: 6/40 n_0mod8, 0/40 occ16; CTRL r6
rand: 4/40; M1 r4: 40/40 n_0mod8, 40/40 occ16).

## 3. Events transcribed (M01–M20, verbatim from the assessment)

| id | type | value | basis (anchors) |
|---|---|---|---|
| M01 | run_section_start raw_M1_r4.jsonl | [01:21:30Z, 01:32:30Z] | A4, A8 |
| M02 | run_section_start raw_M1_r5.jsonl | [01:21:30Z, 01:32:30Z] | A4, A8 |
| M03 | run_section_start raw_M1_r6.jsonl | [01:21:30Z, 01:32:31Z] | A4, A9 |
| M04 | run_section_start raw_M1_r6_rand.jsonl | [01:21:30Z, 01:33:02Z] | A4, A11 |
| M05 | run_section_start raw_CTRL_r4.jsonl | [01:21:30Z, 01:32:31Z] | A4, A9 |
| M06 | run_section_start raw_CTRL_r5.jsonl | [01:21:30Z, 01:32:31Z] | A4, A9 |
| M07 | run_section_start raw_CTRL_r6.jsonl | [01:21:30Z, 01:32:32Z] | A4, A10 |
| M08 | run_section_start raw_CTRL_r6_rand.jsonl | [01:21:30Z, 01:33:03Z] | A4, A11 |
| M09 | run_section_finish raw_M1_r4.jsonl | [01:21:30Z, 01:32:30Z] | summary line, A8 |
| M10 | run_section_finish raw_M1_r5.jsonl | [01:21:30Z, 01:32:30Z] | summary line, A8 |
| M11 | run_section_finish raw_M1_r6.jsonl | [01:21:30Z, 01:32:31Z] | summary line, A9 |
| M12 | run_section_finish raw_M1_r6_rand.jsonl | [01:21:30Z, 01:33:02Z] | summary line, A11 |
| M13 | run_section_finish raw_CTRL_r4.jsonl | [01:21:30Z, 01:32:31Z] | summary line, A9 |
| M14 | run_section_finish raw_CTRL_r5.jsonl | [01:21:30Z, 01:32:31Z] | summary line, A9 |
| M15 | run_section_finish raw_CTRL_r6.jsonl | [01:21:30Z, 01:32:32Z] | summary line, A10 |
| M16 | run_section_finish raw_CTRL_r6_rand.jsonl | [01:21:30Z, 01:33:03Z] | summary line, A11 |
| M17 | finish_stamp (whole run) | [01:33:03Z, 01:33:49Z] | A11, A12 |
| M18 | halted_on_budget | **false** (precise, not an interval) | A12 < A14; runs_used 8 ≤ 30 |
| M19 | binding_stop_checkpoint | "binding_stop not reached; last artifact 01:33:49Z < 01:54:16Z" | A14; check instant bounded [01:33:49Z, 01:54:16Z] |
| M20 | completion_gate | "passed" (derivable) | Validator TASK-20260804-91d27e, parser_check, summary-vs-arms; carried by completion-record.json (RESULTS.json immutable) |

Classification per assessment section 2.7: M01–M19 = (i) amended-stampset,
bounded interval (M18 precise `false`); M20 = (ii) superseding completion
record. No event falls into (iii); no point-instant timestamp was invented
(rule 9).

## 4. Deliverables produced

1. `budget_stamps.repaired.jsonl` — reconstructed successor stampset, header
   comment + 20 JSON lines (one per event M01–M20), each with
   `"reconstructed": true`, `event`, `type`, `value` (interval `[lo,hi]` or
   precise), and `reconstruction_basis` naming the anchors.
2. `completion-record.json` — superseding completion record for
   TASK-20260804-d7d0ec with `completion_gate: "passed"`,
   `halted_on_budget: false`, `scope: "content verified; timing reconstructed
   at bounded precision"`.
3. `repair-report.md` — this narrative.

## 5. Verification (command outputs)

```
$ ls -la coordination/goals/GOAL-AES-003/batches/BATCH-6fe3c2/tasks/TASK-20260806-7fcdf8/
total 48
-rw-r--r--@ 1 adamburan  staff  6077 Aug  6 21:52 budget_stamps.repaired.jsonl
-rw-r--r--@ 1 adamburan  staff  2889 Aug  6 21:53 completion-record.json
-rw-r--r--@ 1 adamburan  staff  8196 Aug  6 21:53 repair-report.md
```

```
$ python3 -c "import json; [json.loads(l) for l in open('budget_stamps.repaired.jsonl') if not l.startswith('#')]; print('JSONL: 20/20 data lines parse')"
JSONL: 20/20 data lines parse
```

```
$ python3 -m json.tool completion-record.json > /dev/null && echo "completion-record.json parses OK"
completion-record.json parses OK
```

```
$ shasum -a 256 budget_stamps.repaired.jsonl completion-record.json
1b7734855ba9a64de5ebdd4df5275899bf06955daad4b83b17403e8d269e455a  budget_stamps.repaired.jsonl
b0a1ab1a46700ac735abcae23731a8f98a3db4310a5cd5f535ab7557b8381b9e  completion-record.json
```

(The report's own sha256 is not embedded here: it is self-referential — editing
the report to record its hash changes the hash. The authoritative value is
recorded in the executor's final report for this task.)

Additional structural assertions run on the JSONL (all passed): 20 data lines
in order M01..M20; `reconstructed: true` on every line; M18 `value` is the
boolean `false` (precise, not an interval); every interval `value` is a
`[lo, hi]` pair of strings. On the completion record: `completion_gate ==
"passed"`, `halted_on_budget == false`, `scope == "content verified; timing
reconstructed at bounded precision"`, `supersedes == "TASK-20260804-d7d0ec"`.

## 6. Immutability confirmation

No file under `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/`
was created, edited, or deleted. The tree was only read (stat, wc, tail,
json.loads). Its mtimes were captured before and after the work and are
unchanged.

## 7. Unexpected observations (rule 8)

1. The handoff's source path said `BATCH-041b14`; the assessment actually
   lives under `BATCH-b41ba9` (matches the dispatch plan read_scope). Resolved
   by reading the dispatch plan; no content impact.
2. Filesystem mtimes are local time (UTC-7); the assessment's anchors are UTC
   (local + 7 h). All 14 anchors verified consistent.
3. The assessment's own anomalies (A13 stamps-file rewrite; RESULTS.json
   `recorded_at` predating its mtime) are disclosed in the completion record's
   `timing_basis.disclosed_anomalies` and were not used as timing anchors.