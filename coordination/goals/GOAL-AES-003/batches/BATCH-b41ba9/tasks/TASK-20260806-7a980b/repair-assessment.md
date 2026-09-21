# Repair Assessment — TASK-20260804-d7d0ec stamp-stream gap

**Repair task:** TASK-20260806-7a980b (BATCH-b41ba9, GOAL-AES-003)
**Assessment date:** 2026-08-06
**Role:** executor (assessment is a recommendation only; the Coordinator decides)
**Write scope:** `coordination/goals/GOAL-AES-003/batches/BATCH-b41ba9/tasks/TASK-20260806-7a980b/`
**Read-only source (immutable, never edited):** `coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/`
**Governing decision:** `ledger/decisions/DEC-20260804-73977c.yaml`, rationale D-3

---

## 0. Purpose and immutability statement

DEC-20260804-73977c D-3 finds that RANK 1 (TASK-20260804-d7d0ec) completion is
unsupported: `budget_stamps.jsonl` ends at `preregistration_written` with no
run-section or finish stamp, and `RESULTS.json` lacks `completion_gate` /
`halted_on_budget`. The measurement content itself validates (independent
Validator TASK-20260804-91d27e). D-3 requires a scoped repair task to add the
missing stamps truthfully (with the reconstruction basis per event) or create a
superseding record, before RANK 1 is treated as complete.

This assessment enumerates every absent normative stamp, states what evidence
today supports an honest reconstruction of each, classifies each event as
(i) amended-stampset / bounded-interval, (ii) superseding completion record, or
(iii) neither (point-time fabrication, prohibited by rule 9), and recommends a
repair device. **No file under `BATCH-713991/tasks/TASK-20260804-d7d0ec/` is
edited or will be edited (rule 4).** All repair artifacts are new files in this
task's write scope.

---

## 1. Evidence inventory (what exists today, all UTC)

| anchor | event | time (UTC) | source |
|---|---|---|---|
| A0 | start stamp: declared 2400 s, binding_stop | 01:14:16Z / 01:54:16Z | budget_stamps.jsonl L1 |
| A1 | section matrix_verification | 01:16:40Z | budget_stamps.jsonl L2 |
| A2 | section instrument_write | 01:18:00Z | budget_stamps.jsonl L3 |
| A3 | section instrument_pin | 01:20:30Z | budget_stamps.jsonl L4 |
| A4 | section preregistration_written (**last stamp present**) | 01:21:30Z | budget_stamps.jsonl L5 |
| A5 | nibble_decay.c mtime | 01:27:08Z | filesystem |
| A6 | nibble_decay (binary) mtime | 01:27:14Z | filesystem |
| A7 | PREREGISTRATION.md mtime | 01:28:55Z | filesystem |
| A8 | raw_M1_r4.jsonl, raw_M1_r5.jsonl mtime | 01:32:30Z | filesystem |
| A9 | raw_CTRL_r4.jsonl, raw_CTRL_r5.jsonl, raw_M1_r6.jsonl mtime | 01:32:31Z | filesystem |
| A10 | raw_CTRL_r6.jsonl mtime | 01:32:32Z | filesystem |
| A11 | raw_M1_r6_rand.jsonl, raw_CTRL_r6_rand.jsonl mtime | 01:33:02–03Z | filesystem |
| A12 | RESULTS.json mtime | 01:33:49Z | filesystem |
| A13 | budget_stamps.jsonl mtime (**content still ends at A4**) | 01:34:10Z | filesystem |
| A14 | binding_stop (declared) | 01:54:16Z | budget_stamps.jsonl L1 |

**Raw-file structure (all 8 arms, verified today):** each `raw_*.jsonl` is
42 lines = 1 matrix-gate header + 40 trial records + 1 `summary` line. The
summary line is emitted only after the 40-trial loop completes (it aggregates
the loop), so a file containing its summary line is proof the arm's loop
finished before that file's final write. Summary aggregates match
`RESULTS.json` `arms` exactly (e.g. M1 r6: 6/40 n_0mod8, 0/40 occ16; CTRL r6
rand: 4/40; M1 r4: 40/40 n_0mod8, 40/40 occ16).

**Cross-file consistency (established, not re-litigated):** the independent
Validator (TASK-20260804-91d27e) recomputed every count from the raw receipts
with no disagreement; `RESULTS.json` `parser_check` also asserts a full
jsonl parse + aggregate recomputation. Content is valid.

**Budget facts:** `runs_used: 8` ≤ `maximum_runs: 30`; every artifact mtime
(≤ 01:33:49Z) is well inside the declared window [01:14:16Z, 01:54:16Z]. The
run completed naturally; the budget was never the constraint.

---

## 2. Missing events and reconstruction basis

Numbering M01–M20 (re-done from the actual files; the prior session wrote
nothing, so no prior numbering exists to preserve). "bounded" = the event's
time is reconstructable only as an interval, never as a point instant.

### 2.1 Per-arm run-section starts — M01–M08

| id | arm | bounded interval | basis |
|---|---|---|---|
| M01 | raw_M1_r4.jsonl | [01:21:30Z, 01:32:30Z] | lower bound = A4 (last stamp before the run section); upper bound = A8 (file exists) |
| M02 | raw_M1_r5.jsonl | [01:21:30Z, 01:32:30Z] | same |
| M03 | raw_M1_r6.jsonl | [01:21:30Z, 01:32:31Z] | upper bound = A9 |
| M04 | raw_M1_r6_rand.jsonl | [01:21:30Z, 01:33:02Z] | upper bound = A11 |
| M05 | raw_CTRL_r4.jsonl | [01:21:30Z, 01:32:31Z] | upper bound = A9 |
| M06 | raw_CTRL_r5.jsonl | [01:21:30Z, 01:32:31Z] | upper bound = A9 |
| M07 | raw_CTRL_r6.jsonl | [01:21:30Z, 01:32:32Z] | upper bound = A10 |
| M08 | raw_CTRL_r6_rand.jsonl | [01:21:30Z, 01:33:03Z] | upper bound = A11 |

**Classification: (i) amended-stampset, bounded interval.** The exact start
instant of each arm is not recoverable (no per-arm clock stamp exists); the
interval is honest and tight. Arm order within the window is not recoverable
from 1 s-granularity mtimes and is NOT asserted.

### 2.2 Per-arm finishes — M09–M16

| id | arm | bounded interval | basis |
|---|---|---|---|
| M09 | raw_M1_r4.jsonl | [01:21:30Z, 01:32:30Z] | summary line present ⇒ loop completed before file final write (A8) |
| M10 | raw_M1_r5.jsonl | [01:21:30Z, 01:32:30Z] | same |
| M11 | raw_M1_r6.jsonl | [01:21:30Z, 01:32:31Z] | summary present; upper bound A9 |
| M12 | raw_M1_r6_rand.jsonl | [01:21:30Z, 01:33:02Z] | summary present; upper bound A11 |
| M13 | raw_CTRL_r4.jsonl | [01:21:30Z, 01:32:31Z] | summary present; upper bound A9 |
| M14 | raw_CTRL_r5.jsonl | [01:21:30Z, 01:32:31Z] | summary present; upper bound A9 |
| M15 | raw_CTRL_r6.jsonl | [01:21:30Z, 01:32:32Z] | summary present; upper bound A10 |
| M16 | raw_CTRL_r6_rand.jsonl | [01:21:30Z, 01:33:03Z] | summary present; upper bound A11 |

**Classification: (i)** — amended-stampset, bounded interval. The summary line
is the strongest structural evidence: it is printed only after the 40-trial
loop completes, so the file mtime is a valid upper bound on the arm's
completion.

### 2.3 Finish stamp — M17

**Bounded interval:** [01:33:03Z, 01:33:49Z] — after the last raw file (A11)
and at/before RESULTS.json's write (A12). **Basis:** RESULTS.json exists and
its mtime is the last artifact write; the finish stamp would have been
recorded after the final arm and before/at the report write. **Classification:
(i)** — amended-stampset, bounded interval.

### 2.4 halted_on_budget — M18

**Reconstructable value: `false` (precise, not an interval).** Every artifact
mtime ≤ 01:33:49Z (A12) < binding_stop 01:54:16Z (A14); the run completed
naturally inside the 2400 s window; `runs_used 8 ≤ 30`. The honest statement
is "halted_on_budget: false — the run finished ~20 min before the binding
stop; the budget was never the constraint." **Classification: (i)** — the
amended stampset records the value with this basis. (No point-time
fabrication: the value is a fact supported by the mtime chain.)

### 2.5 Binding-stop checkpoint — M19

**Bounded:** the checkpoint would record that the binding stop was checked and
not reached. Value is supported: all mtimes < 01:54:16Z. The instant of the
check is not recoverable; honest form is "binding_stop not reached; last
artifact 01:33:49Z < 01:54:16Z". **Classification: (i)** — amended-stampset,
bounded interval.

### 2.6 RESULTS.json completion_gate — M20

**Not reconstructable in place.** `RESULTS.json` is immutable (rule 4); the
missing `completion_gate` / `halted_on_budget` fields cannot be added to it.
The gate VALUE is, however, derivable from the evidence chain: content
validated by the independent Validator (TASK-20260804-91d27e) and by
`parser_check`; all 8 arms complete (42-line files with summary lines);
budget not exhausted (8/30 runs, ~20 min slack). **Classification: (ii)** —
the gate must be carried by a superseding completion record (or a
`completion_gate` field in the amended stampset), never by editing
RESULTS.json.

### 2.7 Summary of classification

- M01–M19: **(i)** amended-stampset, bounded interval (M18 as a precise
  `false`).
- M20: **(ii)** superseding completion record (gate derivable, placement
  must be a new record).
- **No event falls into (iii).** Every missing event has a bounded or precise
  reconstruction basis from today's evidence; no event requires inventing a
  point-instant timestamp, which rule 9 prohibits.

---

## 3. Repair-device candidates (cost / risk)

### C1 — Amended successor stampset file
A new file (e.g. `budget_stamps.repaired.jsonl`) in this task's write scope,
one JSONL line per event M01–M20, each carrying the event, the bounded
interval or precise value, and the reconstruction basis (the anchors above).
A header line declares it a reconstructed successor to the immutable
`budget_stamps.jsonl`, not the original stream.
- **Cost:** low — one small file (~20 lines), no edits to immutable files.
- **Risk:** (a) it is a reconstruction, not a primary stamp — it must be
  labeled as such and must not be presented as the original stream; (b) the
  Coordinator must accept bounded-interval stamps as satisfying the
  completion claim; (c) alone it does not carry the completion gate for
  RESULTS.json (M20) unless a `completion_gate` field is added to it.

### C2 — Superseding completion record
A new record (e.g. `completion-record.json`) declaring TASK-20260804-d7d0ec
complete, naming the exact data-validation chain as the basis for the CONTENT
(independent Validator TASK-20260804-91d27e recomputation; `parser_check`;
summary-line vs `arms` cross-consistency) and the reconstructed stampset as
the basis for the TIMING (reconstructed-at-bounded-precision, per section 2).
Carries `completion_gate: passed`, `halted_on_budget: false`.
- **Cost:** low (one file).
- **Risk:** (a) completion is the strongest claim — it must be scoped
  precisely ("content validated; timing reconstructed at bounded precision"),
  never presented as a primary stamp stream; (b) alone it leaves the stamp
  stream itself unrepaired — the D-3 defect ("stamps end at
  preregistration_written") remains visible unless the reconstruction is
  embedded or referenced; (c) Coordinator approval required.

### C3 — Both (amended stampset + superseding completion record)
The two devices above as a pair.
- **Cost:** two small files.
- **Risk:** minimal beyond either alone; the devices are complementary —
  the stampset repairs the event-level stamp stream (D-3's named defect),
  the completion record carries the gate-level claim (M20) that cannot live
  in RESULTS.json. This is the only candidate that fully closes both halves
  of D-3.

### C4 — No-repair
Leave RANK 1 not-complete.
- **Cost:** zero.
- **Risk:** contradicts D-3's explicit instruction (a repair task must add
  the stamps or a superseding record before RANK 1 is treated as complete);
  the Validator-confirmed content would never be able to claim completion;
  the goal's RANK 1 checkpoint stays open despite valid data. Not
  recommended.

**Authority:** all candidates except C4 require Coordinator approval; the
Coordinator alone may treat RANK 1 as complete (only the Coordinator changes
official research state). This assessment is a recommendation only.

---

## 4. Recommendation

**Primary candidate: C3 — both the amended successor stampset and the
superseding completion record.**

Justification:
1. The two defects are distinct and neither device alone closes both:
   (a) the stamp stream ends before the run section (D-3's named defect) —
   repaired by the amended stampset; (b) RESULTS.json lacks the completion
   gate and is immutable — carried only by a superseding record. The
   stampset alone leaves M20 open; the completion record alone leaves the
   stamp stream unrepaired.
2. Every one of the 20 events has a truthful reconstruction basis (section
   2); no event requires fabrication, so the pair is fully honest.
3. Cost is minimal (two small files in this task's write scope) and risk is
   bounded: both are new records, clearly labeled as reconstructed at
   bounded precision, and neither touches the immutable files.
4. If the Coordinator prefers a single device, the completion record is the
   more load-bearing of the two (it carries the gate), but the stampset is
   the more faithful repair of the named defect; the pair is recommended
   over either alone.

---

## 5. Unexpected observations (rule 8 — recorded, not discarded)

1. **budget_stamps.jsonl mtime (01:34:10Z) is later than every raw file and
   RESULTS.json (01:33:49Z), yet its content ends at preregistration_written
   (01:21:30Z).** The producer touched the stamps file after the run
   completed without appending run stamps. This is consistent with D-3 but
   is itself an anomaly: the file was rewritten at the end of the session
   and the run-section/finish stamps were lost in that rewrite. The
   reconstruction must not treat the stamps file's mtime as a run event.
2. **RESULTS.json `recorded_at` (01:26:00Z) predates every raw file mtime
   (01:32:30Z+) and its own mtime (01:33:49Z) by ~6–7 minutes.** The
   producer string cannot be the true write time. It does not affect the
   content (Validator-confirmed), but it is not usable as a timing anchor
   and must be disclosed wherever the reconstruction cites timing.
3. **The run finished ~20 minutes before binding_stop** (01:33:49Z vs
   01:54:16Z); the budget was never the constraint, so the completion claim
   does not depend on a halt decision.

---

## 6. References

- DEC-20260804-73977c (D-1, D-3) — `ledger/decisions/DEC-20260804-73977c.yaml`
- TASK-20260804-d7d0ec artifacts (immutable, read-only):
  `budget_stamps.jsonl`, `RESULTS.json`, `PREREGISTRATION.md`,
  `raw_{M1,CTRL}_r{4,5,6}[_rand].jsonl` (8 files), `nibble_decay.c`,
  `nibble_decay`
- Validator TASK-20260804-91d27e (content validation, established context)
- Companion machine-readable file: `repair-recommendation.json` (same
  directory)