# TASK-20260731-003 — Validator — Independent validation of the NC-2 run package

**Goal** GOAL-P13-001 · **Batch** BATCH-002 · **Role** validator · **Priority** 85
**Depends on** TASK-20260731-001, TASK-20260731-002 · **Archived by** TASK-20260731-005
**Budget** 3600 s wall clock · 4 GB · maximum_runs 1 · **independent session required**

> **The queue governs.** This card mirrors the `handoff` block for
> TASK-20260731-003 in
> `coordination/goals/GOAL-P13-001/batches/BATCH-002/dispatch_queue.json`.

---

## Objective

Decide whether the archived NC-2 run package is **admissible evidence**.

## The one check that matters most

**Recompute the entire fit independently from `raw-timings.json` alone, with
your own code.** Do **not** import, copy or call `fit_analysis.py`: rerunning
the producer's fitting code verifies only that it is deterministic, not that it
is right. Derive the OLS coefficients, both intervals, the residuals and the
goodness-of-fit statistics by your own route, and **report every disagreement
with its size**.

## Verify, item by item, and report each separately

- **Hash bindings** against the TASK-20260731-002 snapshot receipt.
- **Expected run count and cell count** against what was actually produced.
- **Manifest schema completeness** against the contract's required fields.
- **Seed integrity** — every seed present, distinct where it should be, and
  CTRL-DET's re-execution actually reproduced entry counts, table sizes and
  j-invariant **sets**, not merely their cardinalities.
- **Raw/summary agreement** — recompute the summary statistics from the raw
  records and compare.
- **Control comparability** — CTRL-CAL measured on the **same host in the same
  session and interleaved rather than blocked**; CTRL-NULL's quantities really
  `p`-independent as constructed.

**Cardinality is not identity.** Where the producer reports a set, verify the
**members**. A cardinality agreement with a different member set is
`cardinality_only_agreement` and **counts as a disagreement**.

## Honesty constraints are acceptance criteria, not style

Check and report each:

- no **bare `c`** anywhere without its interval, residuals and GOF verdict;
- every margin figure labelled **EXTRAPOLATION** with EA-1..EA-6 attached in the
  same structure, and **EA-3 beside every extrapolated margin**;
- no artifact states or implies the **NIST-I margin was measured**;
- no artifact describes **GAP-1 or GAP-2 as repaired**;
- the producer wrote **no interpretation, disposition or recommendation**.

A violation of any of these is a reportable defect and **affects admissibility**.

## Verify the pre-registration ordering from Git, not from assertion

`experiments/EXP-SSI-002/specification.yaml` and `derivation_note.md` must have
been committed **before** the run artifacts and **not modified afterwards**. If
the ordering cannot be established from the commit graph, **say so** — the
pre-registration is what makes the fired reading meaningful.

## Rules

- **Independent session.** You did not originate the run.
- **Do not edit the producer's artifacts under any circumstance** — not to fix a
  typo, not to complete a missing field, not to repair a broken JSON document.
  A defect is **reported**, never repaired.
- **An invalid or incomplete run set is not evidence.** Report it as INCOMPLETE
  or INVALID with the concrete defects **listed**; do not soften it into
  observations.
- A timeout, crash or infrastructure failure in the producer's run is
  **infrastructure signal, never a negative mathematical result**. Verify the
  producer recorded it that way and did not feed it to a reading.
- **Do not adjudicate the mathematics of the frozen paper.** GAP-1, GAP-2,
  Section 4.1 and Heuristic 1 are carried, not reopened.
- **Issue one terminal verdict**: VALID, VALID-WITH-OBSERVATIONS, INCOMPLETE or
  INVALID, with its basis. Do not hedge across two.
- **Make no commit.** Write only under your own review directory.
- Record provenance honestly, and **state explicitly that model-level
  independence from the producer is unavailable under this harness** — all roles
  resolve to `claude-opus-5`, `model_verified: false` — so your independence is
  session-level and implementation-level at best.
- Bounded card. If you cannot finish, **stop and report a bounded partial
  validation naming exactly what you did not check**. Never report a check you
  did not perform.

## Deliverables

```
.../reviews/TASK-20260731-003/validation_report.yaml
.../reviews/TASK-20260731-003/repro/independent_fit.py          (YOUR code, not the producer's)
.../reviews/TASK-20260731-003/repro/independent_fit_output.json
.../reviews/TASK-20260731-003/repro/stdout_val.txt
.../reviews/TASK-20260731-003/repro/stderr_val.txt
```

## Completion gate

V1–V10 as stated in the queue's `handoff.completion_gate` for this task.
