# TASK-20260729-046 — Independent validation of the committed EXP-STR-004 run package

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** validator — **independent session required, non-originating**
- **Depends on:** TASK-20260729-045
- **Archived by:** TASK-20260729-048
- **Report id:** `VAL-20260729-003` (cite by path and task id everywhere)
- **Budget:** 3600 s, 4 GB
- **Inference policy:** `review-adversarial` (xhigh, independent session); a gap
  is recorded in `degraded_requirements`, **never silently downgraded**

## Objective

Verify, **before any interpretation is taken**, that the committed EXP-STR-004
run package is a valid and admissible research receipt, and return PASS or FAIL
with `blocks_ledger_record` set **explicitly**.

**An invalid or incomplete run set goes back to the Executor with concrete
defects listed. It is not evidence.**

## Method

- **Recompute, do not read.** Write your **own** measurement code from the
  frozen specification and re-derive the primary cells rather than re-running the
  committed driver. Re-running the same blob is a determinism check, not an
  independence check — NARROW-6 and RC-F record exactly that distinction, and it
  is why RC-F is still undischarged.
- **Check the matched base-row budget yourself.** This is the control
  EXP-STR-003's arm E lacked and that UC-2 required of the successor. If the two
  arms did not consume the same budget at any cell, **name the cell** and mark
  the comparative criteria there **unevaluable**.
- **Check every set, not every count.** Recompute the predicted and measured
  misalignment sets at every named cell and compare **member by member**. A
  cardinality match with a different member set is `cardinality_only_agreement`
  and is reported **as a disagreement**. This failure has recurred five times in
  this program by RT31-5's count, twice inside artifacts that had already passed
  independent review.
- **Re-verify a named sample of decomposition certificates with your own code**,
  independently of both the driver and the Sage verifier. State how many and
  **which ones by name**.

## Validity checks to itemise

Expected run count exactly 28, no extras and no missing identifiers; every
manifest schema-complete against the AGENTS.md artifact policy; every instance
parameter recomputed from the committed generator and compared; raw-to-summary
agreement leaf by leaf with the maximum absolute difference reported; control
comparability across arms — identical cell label, B, m, curve, derived seed and
**identical base-row budget** within each cell.

Artifact-policy items one by one: distinct non-overlapping per-run timing
windows; `numpy.__version__` in every `raw-result.json`; one agreeing set of
harness code hashes across all 28; non-empty stdout and stderr; requested
policy, resolved model, `model_verified`, fallback status and degraded
requirements.

**Verify the receipt against Git** and re-derive every path SHA-256 **from the
Git blobs at that commit**, not from the working tree. If a git command does not
finish — the volume is at 99% and `git fsck` has already timed out on it —
**report the check as unfinished. An unfinished check is never a PASS.**

## Output discipline

Set `blocks_ledger_record` explicitly and state what would change it. List every
**required narrowing** as a numbered item in words the Coordinator can adopt
**verbatim**.

Apply no resume condition, take no disposition, change no status, create no
evidence, decision or knowledge record, and interpret no measurement. Say so in
your report.

**Make no commit and stage nothing.** Your artifacts are committed by
TASK-20260729-048 and by nothing earlier — the dispatching session committed the
post-execution review artifacts **one commit early in BATCH-012 and again in
BATCH-013**, and this constraint exists to stop a third occurrence.

Model independence is unavailable and is not claimed; assert **session**
independence. Name explicitly anything not reached inside the cap.
