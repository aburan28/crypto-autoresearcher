# GOAL-HQC-001 — BATCH-002 opening

- **Goal**: `GOAL-HQC-001` (status `active`)
- **Question**: `RQ-HQC-001`
- **Opened**: 2026-08-02
- **Branch**: `claude/goal-target-hqc-launch-vndegi`
- **Prior batch**: BATCH-001, closed `refine`, `DEC-20260802-344883`,
  `EV-HQC-9906b9`, verified ledger commit `15d447fa`
- **Owner**: coordinator

## 1. Mandate

BATCH-002 executes the single `next_action` recorded by `DEC-20260802-344883`,
in its stated order:

1. **Correct** the RS-S3 minimum distance `49 → 59` by superseding record, and
   apply the `D-6` citation fix to the over-cautious `[EXTRACTION-DAMAGED]`
   marker on SPEC Eq. (13).
2. **File** the corrected `KN-LIT` entries. This — not acquisition — is what
   discharges `RQ-HQC-001.constraints[0]` and unblocks experiment design.
3. **Characterize A17**, the unstated i.i.d. inner-decoder assumption the red
   team found is proved in *neither* primary source.

Steps 1 and 2 are one task; they cannot be separated, because the correction
exists precisely so the filing is correct. Step 3 is a separate task and is
**explicitly not experiment design** — see §4.

## 2. What BATCH-002 is not

It runs **no decoding trial**, makes **no measurement**, designs **no
experiment**, and creates **no hypothesis**. It says nothing about whether
HQC's DFR model is correct in either direction. Claim-tier ceiling stays
**toy**. Nothing here is admissible toward the AGENTS.md rule 13 closure
quorum, for the same reason as BATCH-001: no policy alias resolves under this
harness, so both reviews are independent *sessions* on one model.

## 3. The correction, stated before it is made

`TASK-20260802-6344ed`'s transcription records RS-S3 as `[90, 32, 49]` and
files the inconsistency as a **source** anomaly (X6). It is the
**transcription's own** error. Two independent derivations force 59:

| Route | Derivation | Result |
|---|---|---|
| MDS property | Reed–Solomon codes are MDS, so `d = n − k + 1 = 90 − 32 + 1` | **59** |
| Transcribed `δ` | The same transcription records `δ = 29` for RS-3/RS-S3, and `d = 2δ + 1 = 2·29 + 1` | **59** |

The red team costed the error at **50.7 bits at NIST-5** (2⁻²⁶⁰·⁵¹ against
2⁻²⁰⁹·⁷⁷): uncorrected it would manufacture a false finding that HQC-5 misses
its DFR target by 46 bits. The Coordinator reconfirmed both derivations
independently before opening this batch.

The transcription artifact is **snapshot-committed and immutable**. It is not
edited. `CORR-20260802-3ae664` supersedes it on this point, and the filed
`KN-LIT` entries carry the corrected value from the start — they are new
records being made right the first time, not corrected records.

## 4. Why A17 characterization is not experiment design

`RQ-HQC-001.constraints[0]` forbids designing an experiment until the primary
sources are filed. `TASK-20260802-15971b` therefore stops short of a protocol:
it states A17 formally, searches both primary sources for a proof, and derives
what a violation would do to the bound. That is **analysis of an already-obtained
text**, and it is deliberately scoped so it does not depend on
`TASK-20260802-63b16a` succeeding — the two run concurrently with disjoint
write scopes.

If the filing task fails, the A17 analysis still stands and BATCH-003 can
design against it once filing lands. If A17 turns out to be provable after all,
that is the useful result and the eventual experiment retargets.

A17 is the highest-value surface BATCH-001 found: a load-bearing assumption
that neither the specification nor HQC-RMRS proves is exactly the object
`docs/inventor-protocol.md` says to attack, and it is what `IDEA-20260801-011`
was reaching for without knowing the model.

## 5. Batch composition

| Task | Role | Purpose |
|---|---|---|
| `TASK-20260802-63b16a` | executor | Apply the RS-S3 and Eq. (13) corrections and **file** three `KN-LIT` entries (`KN-LIT-b9e1a8`, `KN-LIT-1c9474`, `KN-LIT-4c1133`); rebuild `knowledge/INDEX.md`. |
| `TASK-20260802-15971b` | executor | Characterize assumption A17: formal statement, proof search in both primary sources, sensitivity derivation. No protocol. |
| `TASK-20260802-a4f56a` | coordinator | Snapshot archive of both producers. Runs alone. |
| `TASK-20260802-32250e` | validator | Filing fidelity, corrected-value propagation, provenance levels, INDEX consistency. |
| `TASK-20260802-caddef` | red-team | Attack the correction, the filing decision, and the A17 characterization. |
| `TASK-20260802-09163b` | coordinator | Ledger archive: `EV-HQC-6fd5b1`, `DEC-20260802-9664c6`, `CORR-20260802-3ae664`, goal checkpoint. Runs alone. |

**This batch writes into `knowledge/` from a producer task, which BATCH-001 did
not.** BATCH-001 used propose-then-file because the content was unreviewed and
carried an unknown defect. That defect is now known and corrected, the content
has been through two independent reviews, and the entries are still
snapshot-frozen before review and only made durable by the ledger archive. The
executor owns the three exact `KN-LIT` paths plus `INDEX.md`; no other task
touches them.

## 6. Merge hygiene at open — a merged PR mid-campaign

**PR #113 was squash-merged into `main` at `6290e316` while BATCH-001 was still
running.** `main` therefore carries an *earlier state of this branch's own
lineage*, not a competing record. Verified before resolving anything:

- `main:ledger/goals/GOAL-HQC-001.yaml` is byte-identical (`73ebb5bf…`) to this
  branch's opening commit `47a684f2`.
- `main:…/BATCH-001/dispatch_queue.json` is byte-identical (`819068f2…`) to this
  branch's commit `3ec55418`, differing from HEAD only by lacking the
  later-added `TASK-20260802-1f2e40` and the terminal task states.
- The only `main`-side commit touching either record is the #113 squash itself.

Resolved to HEAD, and the reasoning recorded in the merge commit. Had either
side been another lane's record, the correct action would have been to stop and
supersede instead.

**Merged, never rebased.** This branch carries three archive receipts whose
commit SHAs are recorded in the queue and re-verified against Git; rebasing
would rewrite those commits and break all three receipts permanently. All three
were re-verified after the merge and still pass.

**A merged PR cannot track new work**, so BATCH-002 opens a new PR rather than
reusing #113.

## 7. Repository state at open

- Base merged from `main`: `669e7368`.
- `tools/validate_ledger.py`: **67** errors above the grandfathered baseline,
  down from 183 at BATCH-001's open because `main` landed substantial schema-debt
  cleanup in between. **Zero** name a `GOAL-HQC-001` record. BATCH-002's
  obligation is to keep that zero.
- All three BATCH-001 archives re-verify post-merge; all ten dispatch gates pass.

## 8. Standing limitation, restated so it is not lost

Both reviews in this batch are independent **sessions** but not independent
**models**. Closing this goal will eventually require three genuinely distinct
backends, and no attestation may ever be synthesized from same-model reviews.
