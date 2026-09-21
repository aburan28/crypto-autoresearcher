# Audit note: what this session actually read, what it could not reach, and what it did not do

Task: `TASK-20260825-169adc` — Coordinator audit of lane closure L5 of `DEC-20260824-b7557b`.
Batch: `BATCH-4d5406`. Goal: `GOAL-ECQ-2298dc`. Date: 2026-08-25.
Decision issued: `DEC-20260825-a74c9e`.
Requested policy: `coordinator-orchestration-code`. Model that answered: `claude-opus-5`.
`fallback_used: false`. Reasoning effort `high`. The policy was honoured; no downgrade was taken.

**This note claims nothing about the mathematics and is not progress toward C1.** It exists so the
audit's basis can be checked rather than trusted.

---

## 1. Read in full, at their committed paths, in this session

| path | what it supplied |
| --- | --- |
| `ledger/handoffs/TASK-20260825-169adc.yaml` | the binding envelope: objective, recorded prior, five boundaries, write_scope, budget |
| `ledger/decisions/DEC-20260824-b7557b.yaml` | the record under audit — all 1258 lines, in two paged reads |
| `ledger/goals/GOAL-ECQ-2298dc/goal.yaml` | objective, C1/C2, closure rule, pause conditions, odds assessment, the single next_action |
| `coordination/goals/GOAL-ECQ-2298dc/inputs/RETRIEVAL-elkies-rank17.md` | addendum 2 (the L5 measurement), the exponent-drop hazard, the ranked substitutes |
| `coordination/goals/GOAL-ECQ-2298dc/inputs/SCOPING-recomputation-lane.md` | the transcription criterion, the Galois-module re-reading, the K3 ceiling, the OSCAR inventory, the Kihara paywall |
| `agents/coordinator.md` | authority, the closure gate, refutation-artifact order, review architecture |
| `AGENTS.md` | core rules 6, 9 and 12; the inventor-protocol obligations; review architecture and the proves-too-much control; durable-commit and retrieval policy |
| `CLAUDE.md` | runtime binding, ID contract, concurrency rules (delivered as system context) |

## 2. Read in part, at named passages

| path | passage |
| --- | --- |
| `docs/inventor-protocol.md` | §3 "Controls before belief" and §4 "The closure standard", read in full; §§1, 2, 5–8 not read (their binding content reaches this record through `AGENTS.md` "Inventor protocol" and `agents/coordinator.md`) |
| `templates/research-records.md` | the `coordinator_decision` schema and the `knowledge_promotion` contract |
| `tools/validate_ledger.py` | `REQUIRED`, `check_obstruction`, `OBSTRUCTION_REQUIRED`, `GOAL_STATUSES`, `GOAL_REQUIRED`, `load_goal_documents` (checkpoint-shard merge), `check_goals` |
| `docs/claims-and-verification.md` | "Refutation artifacts: proof before rejection" |
| `ledger/goals/GOAL-ENDO-001/checkpoints/BATCH-de621d.yaml` | read as a shape exemplar for the checkpoint shard; nothing from its content is cited |

## 3. NOT read, and why — this is the load-bearing half of the note

**`docs/inventor-protocol.md` was read only at §3 and §4.** Every `inputs_to_read` entry of the
handoff was opened; that one was opened at two named sections rather than in full. Sections 1, 2
and 5–8 were not read, and their binding content reaches this record second-hand through
`AGENTS.md` "Inventor protocol" (which enumerates the four obligations and section 8's
`proof_search_map` gate) and `agents/coordinator.md`. Nothing in the decision cites a clause of
§§1–2 or §§5–8, and a reviewer should treat any such reasoning, if found, as second-hand.

**No primary mathematical source was read.** This session had **no network access**. In particular:

- `arXiv:math/0502439` (Kloosterman) — **could not be opened**. The transcription of the surface
  used in the superseded L5 measurement therefore **remains unverified**, exactly as it was. The
  audit does not depend on the transcription being right or wrong: defect A1 is a statement about
  the *inference*, which fails on any model.
- `arXiv:0709.2908` (Elkies) — **could not be opened**. The rank-17 K3 reading used at A6 comes
  from `SCOPING-recomputation-lane.md` and is flagged in the decision's `limitations` as being no
  stronger than that reading.
- `arXiv:2003.00077` (Elkies–Klagsbrun), nominated as `CTL-POSITIVE-CONTROL` — **could not be
  opened**. If it proves unusable at Stage 0, the protocol requires the run to stop and report;
  no substitute control may be chosen after the fact.
- Shioda's degree-829,440 statement — **not checked at source**. Used only to establish that the
  descent gap *can* be total, never that it typically is.

**Run records were not re-read at their paths.** `RUN-ECQ-f5af06-v2-A-certify` and
`RUN-ECQ-f5af06-v2-B-extension` are cited through `DEC-20260824-b7557b` and `DEC-20260824-5246b7`.
Their figures are **producer-reported on an unvalidated run set**. The proves-too-much control in
§4 of the derivation note is deliberately built to survive that: it needs only that the 31
generators are large (~33 digits) and the frozen box is small (8 digits).

**`ledger/decisions/DEC-20260824-5246b7.yaml` was not opened.** Its content reaches this audit
through `DEC-20260824-b7557b`, whose authoring Coordinator read it in full and says so.

**The knowledge corpus was not queried.** The retrieval MCP tools (`search_knowledge`,
`get_context`, `get_source`, `find_related`) were **not in this session's tool surface**. No claim
here rests on the corpus, and under AGENTS.md's retrieval policy the absence of a search result is
not available as support for anything. No `kb` citation appears in the decision, and no `recalled`
citation appears anywhere.

## 4. What this session could not execute

**No shell.** Tool surface: `Read`, `Grep`, `Glob`, `Write`, `Edit`, `SendMessage`. Consequences,
each handled and none papered over:

1. **`tools/allocate_id.py` could not be run.** `DEC-20260825-a74c9e` was minted and `--check`
   verified **by the orchestrating session at this session's request**, with the verbatim output
   of both commands relayed back (`occurrences across the union (9414 identifier-bearing paths
   scanned): 0`). No identifier was invented and no state was grepped for "the next free number".
2. **`tools/validate_ledger.py` could not be run, and no clean result is claimed on its behalf.**
   The decision's `next_actions` require the archiving session to run it on the merged tree.
3. **Nothing was computed.** Every quantitative statement in the decision is read from committed
   records, with exactly one exception, stated as such: the Shioda-Tate bound `rank MW <= 10d - 2`
   was checked by hand against both independently known anchors — `d = 1 -> 8` (the `E_8` maximum
   for a rational elliptic surface) and `d = 2 -> 18` (the K3 maximum already recorded at
   `DEC-20260824-b7557b` E4). Both agree, which is what licenses its use at `d = 3` and `d = 4`.

## 5. Budget and boundaries, as consumed

| declared | consumed |
| --- | --- |
| wall clock 3600 s | within budget; no cap bound |
| experiment runs: 0 | **0** |
| searches authorised: 0 | **0** |
| write_scope: 3 paths | 4 files, all inside scope (listed below) |
| commits | **none — this session did not commit anything** |

Files written, all within `write_scope`:

- `ledger/decisions/DEC-20260825-a74c9e.yaml` (new)
- `ledger/goals/GOAL-ECQ-2298dc/checkpoints/BATCH-4d5406.yaml` (new, write-once)
- `ledger/goals/GOAL-ECQ-2298dc/goal.yaml` (edited: `current_batch_note`,
  `lane_closure_supersessions`, `decision_ids`, `updated_at` — **`status` and `next_action`
  untouched**)
- this directory: `DERIVATION-L5-bound-direction.md` and this note

Nothing outside `write_scope` was written. `DEC-20260824-b7557b` was **not** edited.

## 6. Prompt versus envelope

The dispatching prompt and `ledger/handoffs/TASK-20260825-169adc.yaml` were compared on every
binding point: objective, the five boundaries, the immutability of `DEC-20260824-b7557b`, the
treatment of the un-run L5 measurement, the authority granted and withheld, `write_scope`, budget,
the requested inference policy, and the identifier-minting instruction. **No divergence was found,
and none is reported as a defect.**

One departure exists but it is not between prompt and envelope: `BATCH-4d5406` and this task were
created under a goal whose committed decision reads "DO NOT DISPATCH FURTHER WORK UNDER
GOAL-ECQ-2298dc. No batch, no experiment, no producer task." That is recorded in full, and
attributed to the orchestrating session, at `DEC-20260825-a74c9e.procedure_deviation`.

## 7. The boundary, restated because it is the thing most easily lost

Nothing read, written or concluded in this task produced a curve, a point, a family, a
specialisation, or one unit of Mordell-Weil rank. **C1 is unmet and is not advanced.**
`GOAL-ECQ-2298dc` remains `blocked` with its single next action unchanged. Reopening lane L5 is
not a result; the lane contains no object this program holds, and its own next step is approved at
Stage 0 only and dispatched nowhere.
