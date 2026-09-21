# BATCH-5a3d0a closeout — GOAL-SSI-001

Status: CLOSED. Both deliverables filed and independently reviewed.

## What this batch produced

1. **CORR-20260808-d2568a** (`ledger/corrections/CORR-20260808-d2568a.yaml`)
   — prose-only gloss correcting `EXP-SSI-9b542d/specification.yaml`'s
   `RG-REPRODUCTION-GATE.can_this_control_fail` "NOTE (honest
   limitation...)" clause. Discharges the one required, non-blocking
   follow-up carried from `DEC-20260807-47db22`. No verdict, run, or
   hypothesis-status change.
2. **CORR-20260808-c792f8** (`ledger/corrections/CORR-20260808-c792f8.yaml`)
   — weakens `EV-WESO-001`'s claim that the vOW middle regime "beats
   Delfs-Galbraith at every tested budget w=2^30..2^80 for all five sizes"
   by counterexample (at w=2^30, correctly anchored, the method loses at
   all five sizes) plus a derived five-size crossover table.
3. **DEC-20260808-7ed316** (`ledger/decisions/DEC-20260808-7ed316.yaml`) —
   the Coordinator decision (`weaken`) filing both corrections.

Producer session: Coordinator, direct authorship. Snapshot-committed by the
orchestrating session at `1b93c4733`.

## Independent review

**TASK-20260808-fccbca** — independent Validator review, dispatched
directly by the orchestrating session rather than pre-filed as a handoff
before dispatch (a named process deviation — see
`ledger/handoffs/TASK-20260808-fccbca.yaml`). Delivered from an independent
session reviewing the committed `1b93c4733` snapshot. Full report:
`coordination/goals/GOAL-SSI-001/batches/BATCH-5a3d0a/reviews/TASK-20260808-fccbca/validation_report.yaml`.

**Verdicts: both CONFIRMED WITH CAVEAT.**

- `CORR-20260808-d2568a`: arithmetic and all citations independently
  reproduced exactly. One trivial, immaterial prose slip found: "roughly 92
  times the band's own half-width (0.25 bits)" should read *full-width*
  (0.5 bits) — 46.038672/0.25 ≈ 184, not 92. Left as a noted pending fix
  rather than a new correction record (cheaper option; substance unaffected).
- `CORR-20260808-c792f8`: central refutation (w=2^30 loses to
  Delfs-Galbraith at all five sizes) reproduced **two independent ways**
  — from `cost_model.py`'s `PAPER_PAIRS` literals, and separately from the
  same file's own fitted `opt['log2T']`/`opt['log2M']` values in
  `RUN-WESOVOW-001/raw-result.json` — so it is doubly confirmed and robust
  to anchor choice. The four newly-derived crossover values
  (69.6/77.7/91.8/109.0 at P=384/512/576/768), however, were computed only
  from `PAPER_PAIRS`; recomputing from the model's own fitted `opt` values
  gives 69.2/**81.6**/87.3/102.6 instead. **At P=512 specifically this
  flips the qualitative conclusion** within the tested range
  (w=2^30..2^80): `PAPER_PAIRS` anchor → crossover 77.7, inside the tested
  range (method wins at w=2^80 by +1.15 bits); fitted-`opt` anchor →
  crossover 81.6, outside the tested range (method never wins within it,
  w=2^80 gives −0.82 bits). This anchor choice was undisclosed in the
  correction's text.

## What is now citation-eligible vs. not

- **Citation-eligible now** (within the batch's stated scope — theoretical
  claim_tier, no hypothesis status change, cite alongside the correction,
  `EV-WESO-001`/`EXP-SSI-9b542d` themselves left unedited):
  `CORR-20260808-c792f8`'s central w=2^30 counterexample; its crossover
  values and "never beats DG at any tested budget" verdicts for
  P=384/576/768; all of `CORR-20260808-d2568a`.
- **NOT citation-eligible**: `CORR-20260808-c792f8`'s P=512 crossover value
  and its w=2^80 sign, until the anchor ambiguity is resolved. Recommended
  resolution: rederive from `RUN-WESOVOW-001/raw-result.json`'s own `opt`
  values (not `PAPER_PAIRS`) and file the result as a new record superseding
  the P=512 row (AGENTS.md rule 4 — do not edit `CORR-20260808-c792f8`).

## What was NOT touched (immutable, per AGENTS.md rule 4)

`CORR-20260808-d2568a.yaml`, `CORR-20260808-c792f8.yaml`, and
`DEC-20260808-7ed316.yaml` were reviewed only — neither is edited by this
closeout or by the Validator's review. Neither was found actually wrong
(both CONFIRMED, not REFUTED); the caveats above are additive findings,
not corrections to those records.

## Next action (exactly one to be selected by a future batch)

Four items are now queued, each with a concrete revisit condition recorded
in `ledger/goals/GOAL-SSI-001/goal.yaml`'s `next_action` and (for the first
three) in `DEC-20260808-7ed316.next_actions`:

1. `EV-SSI-59f7a2`'s missing SC-1/SC-3 conditionality (qualitative,
   Coordinator-authorable).
2. `EXP-WESOVOW-001/cost_model.py` line 236's own anchor bug, still
   uncorrected at its source (Executor-scoped: code edit + re-run).
3. `analysis/SSI-ECDLP-SYNTHESIS-20260803.md` line 171's "NIST-III/V retain
   comfortable margins" sentence (now cheaper — upstream source corrected).
4. **New, surfaced by this review**: resolve `CORR-20260808-c792f8`'s P=512
   anchor ambiguity by rederiving that one crossover value from
   `RUN-WESOVOW-001/raw-result.json`'s own `opt` values.

No completion criterion of `GOAL-SSI-001` is met or approached by this
batch. The goal stays `active`.
