# TASK-20260729-045 — Snapshot archive of the EXP-STR-004 run package, alone

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** coordinator (archival task — **runs alone**)
- **Depends on:** TASK-20260729-044
- **Archive kind:** snapshot; `source_task_ids: [TASK-20260729-044]`
- **Budget:** 300 s, 2 GB, `maximum_runs: 1` (zero compute)

## Objective

Commit the exact TASK-20260729-044 run package — **174 paths, expanded
literally** — and record a verified post-commit receipt, so both independent
post-execution reviews read an immutable hash-bound package and the run
artifacts **provably predate every interpretation of them**.

## Declared commit set — exactly 174 paths

A **product declaration, not an abbreviation**:

- **168** = the Cartesian product of the **28 run ids** and the **6 file names**
  (`manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`,
  `stderr.log`, `raw-result.json`) under
  `experiments/EXP-STR-004/runs/{run_id}/`.
  Run ids: `RUN-STR-004-{AP,EP}-{L12,L13,L24,L25,L48,L49,L96,L97,L192,L193,X96,X97,A12M3,A13M3}`.
- **6** additional literal paths: `driver/bsweep_driver.py`,
  `driver/verify_certificates.sage`, `results/sweep_summary.json`,
  `results/run_index.json`, `results/certificate_verification.json`, and this
  receipt.

**Expand the declaration literally before staging and write the expansion into
the receipt.** Compare it against the staged set **path by path**.
**BATCH-010 is permanently unrenderable for declaring 7 paths against a
195-path commit, and this card is the one place that failure could recur.**

If the committed and declared sets differ: **do not commit a different set and
do not enlarge the declaration after the fact.** Report the exact difference —
which declared paths are missing, which staged paths are undeclared — and stop.

## Verify before committing

- Exactly **28** run directories, no extras, every one carrying all six files,
  every terminal status present. A count other than 28, or an identifier outside
  the declared list, **stops the card**.
- Nothing under `harness/` is modified — record the verification; if it is,
  **do not commit** and report an evidence-integrity failure.
- Machine-parse every JSON artifact and every `manifest.yaml`.
- Record artifact sizes: total tree size and largest run directory against the
  64 MiB and 2 MiB caps, plus free space remaining after the commit.
- Check for a stale `.git/index.lock` and record what you found. This is the
  largest staged set in the batch and the one most exposed to the hazard.

## Do not stage

Anything under `experiments/EXP-STR-001`, `-002` or `-003`; anything under
`harness/`, `ledger/`, `knowledge/` or `tools/`; **anything under
`.../BATCH-014/reviews/`** — no review has run yet; no AppleDouble sidecar.

## The commit message states facts and no disposition

It must contain `TASK-20260729-045`, `TASK-20260729-044`, `EXP-STR-004`,
`GOAL-ECDLP-001` and `BATCH-014` literally. **It must not state a verdict, a
disposition or an interpretation of any measurement, in the subject line or the
body.** `SUP-BATCH013-A` exists because a commit subject line stated a
disposition reserved for the reviews and the decision — and the subject line is
the part a reader sees first and a log renders alone.

An unfinished git verification is reported as unfinished, never as PASS and
never as FAIL. This receipt lands in the immediately following commit
(INT-BATCH007-T).
