# TASK-20260812-655fe9 — LEDGER ARCHIVE (runs alone, after both reviews)

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           coordinator
    policy         coordinator-orchestration-code      effort high
    state          queued
    depends_on     TASK-20260812-55056b, TASK-20260812-696cd4
    archive kind   ledger   sources  the same two reviews
    budget         5400 s wall clock, 2 GB, 1 run
    claim tier     TOY

## Identifier provenance

Minted 2026-08-12 by the dispatching session and **two-scope confirmed** —
worktree `--check` (well-formed and free) **plus** a bounded sweep of the 25
most-recently-updated origin branches (0 hits). Recorded as two-scope confirmed
and **not** as `--check` alone: `--check` answers from the working tree only
(DEC-20260812-15d3b2 defect (b)), which is exactly how EV-MLKEM-9346bb and
DEC-20260809-afe29b were reported FREE while already occupied on a pushed
branch. **A passing `--check` is necessary and not sufficient.** Closes declared
gap G-1.

## Declared path set — SIX PATHS BEFORE THE PROBE EXTENSION

    archives/TASK-20260812-655fe9/ledger-receipt.json              (own)
    ledger/evidence/EV-MLKEM-aa39ad.yaml                           (own)
    ledger/decisions/DEC-20260812-781961.yaml                      (own)
    ledger/goals/GOAL-MLKEM-005.yaml                               (own)
    reviews/TASK-20260812-55056b/validation_report.yaml            (source)
    reviews/TASK-20260812-696cd4/red_team_report.md                (source)

**It is six and not twenty-seven** because TASK-20260812-b53c2f already
committed the twenty-one rider paths. **Do not re-declare them here**:
re-declaring an already-committed path yields a commit whose change set is
*smaller* than its declared set, which is the MISSING half of the same equality
test D1, D2 and D3 failed.

**Extend this set before staging by exactly the probe script and probe output
paths the two reviews list in their reports — and by nothing else** (declared
gap G-3, still open). If the knowledge-promotion gate is met, one
`knowledge/findings/KN-FIND-*.md` path is minted at close and added to **both**
`artifact_paths` and `archive.record_ids`. `dispatch_queue.json` is deliberately
not in this set.

## Reserved records

`EV-MLKEM-aa39ad` and `DEC-20260812-781961` are **RESERVATIONS, NOT CLAIMS**.
Neither exists; reserving them presumes nothing about this batch's outcome. If
BATCH-4ed139 closes without producing an evidence record, **leave them unused
and say so** rather than writing an empty record to fill a reserved slot.

## The obligations this archive alone carries

* **Confirm, do not repeat from memory**, the validity work done at the two
  producer snapshots: read the `TASK-20260812-b581a8` and `TASK-20260812-b53c2f`
  receipts, confirm each records change-set equality and its per-producer
  validity check, and record that confirmation. Then verify this archive's own
  sources — the two review reports — against their completion gates.
* **Name the frozen termination branch that fired**, quote the PREREG-1 clause,
  state what it licenses and forbids. Do not re-read the clause. If the evidence
  cannot discriminate, the decision is `inconclusive` and says so plainly.
* If **T-F1FAIL** fired: close the **admissibility-gate LANE** with its named
  obstruction, evidence, budget, test boundary, remaining uncertainty and a
  concrete successor or revisit condition — and state explicitly that **closing
  the LANE retires the LANE, never the goal**.
* Make the **C-1 ruling** from rider (i) and narrow the phrase **by reference**
  in EV-MLKEM-9346bb, DEC-20260809-afe29b and the goal checkpoint **without
  editing any of them**; all three are immutable.
* Fill `knowledge_promotion` — a promotion, or a concrete `not_warranted` reason.
* Exactly **one** `next_action` on the goal record, prior text retained verbatim
  under a `superseded_*` key, plus one `batch_log` entry naming the decision and
  evidence IDs, **all three prior archive commits** (`-1ed548` notarizing
  PREREG-1, `-b581a8` the lead, `-b53c2f` the riders) and both reviews.
* Merge `origin/main` (never rebase); **run the post-commit verifier before the
  push, not after**; then push and open or refresh the PR naming every new
  record. `knowledge/INDEX.md` is not staged, written or regenerated.

## Prohibitions carried

Do not run TASK-20260809-60f9cc again on any branch. Do not re-mint
EV-MLKEM-9346bb, DEC-20260809-afe29b, EV-MLKEM-e45478 or DEC-20260812-15d3b2.
Do not edit either BATCH-9e3584 review wave's reports, evidence, decisions,
KN-FIND-2a35aa, or any producer artifact — all immutable, every narrowing by
reference. `reject_scoped` on a single unreplicated empirical-only run is
forbidden. CLAIM TIER TOY.
