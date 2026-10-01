# BRIEF: review of the elliptic-curve goal portfolio and a fresh ideation round on six under-served ECC lanes

Date: 2026-09-30. Top-level session on branch `claude/elliptic-curve-goals-3bfz9x`,
base `980abd8feec6429d1e7abb17618fe37bd10bd8a0` (= `origin/main` at session start;
branch and `main` were identical when this brief was written).
User request (verbatim intent): "review and propose more ideas for the elliptic
curve related goals".

This file is the shared handoff context for six idea-generator lanes. It is a
working analysis, NOT a ledger record: it changes no status, approves nothing,
and every number in it is a pointer to the record or tool output that carries
it. Lane cards are in `handoffs/`; the per-lane record extracts the generators
read are in `context/`; generator reports go to `reports/`.

## 0. Authority and prohibitions (bind every lane)

- Proposals only (AGENTS.md "Standing user authorization"). No hypothesis, no
  experiment contract, no approval, no status change. Designing is not
  approving, and filing is not designing.
- NEVER edit an existing record. New proposals go to
  `ledger/proposals/<pre-minted id>.yaml` only. IDs are assigned in section 5;
  never mint or invent one. An unused id is returned in the lane report.
- No runs. Generators have no shell. Never report an imagined outcome, timing,
  or statistic; "expected cost" is an order-of-magnitude estimate labelled as
  such (AGENTS.md rules 5 and 9).
- Citations carry provenance `recalled | retrieved | kb | internal`
  (`templates/research-records.md`, "Citation provenance"). `retrieved` only if
  you actually fetched and read the source this session with WebFetch.
  **The `crypto-kb` retrieval index is EMPTY in this container**
  (`CRYPTO_KB_QDRANT_URL=:memory:`, checked 2026-09-30), so `kb` provenance is
  unavailable this round; use `Grep` over `knowledge/` and `ledger/` instead
  and say so in `prior_art.searched`. A proposal whose only literature is
  recalled is `novelty_status: unverified` — the honest default.
- Every idea carries a `prior_art` block positioned against the known-results
  map (`context/frontier-map-*.md`, rendered at the commit in
  `context/frontier-map-rendered-at.txt`); `rows_checked` must name real
  `KR-*` rows. The dispatcher runs `tools/build_frontier_map.py --match` on
  every returned idea and sends back any whose top hit is a row it did not cite.
- Premature closure is a failure mode symmetric with overclaiming
  (`docs/inventor-protocol.md`); a closure needs a named, measured obstruction.
  `dominated_by` may be `null` only after checking every frontier row; an
  unchecked `null` is a fabrication.

## 1. The ECC portfolio as of the base commit (the review)

Membership is the declared set in `orchestration/research-priority.yaml`
(read through `tools/ecc_priority.py`); nothing below is inferred from a
prefix.

### 1a. Goal records: 61, of which 46 active

| status | n | goals |
| --- | --- | --- |
| active | 46 | 20 `SCURVE` per-curve audits; ECDLP-001, ECDLP-bbc21f, ECDLP2M-001, CRYPTO-001, PATH-001, ENDO-001, ECTD-001, AUXIN-a93442, DREG-001, SDEG-001, SIG-001, MONO-001, RELN-001, ICEX-001, ICPERF-e6b6a4, SATIC-c49b77, SEMBIN-5078bc/cbf422/fcb7a2, FROB-6333a9, GFPN-380702, SSI-001, SSIQ-001, ECQ-2298dc, ECQ-e72c0b, ECRANK-002 |
| draft (never activated) | 7 | CSIDH-001, ECDSA-001, EDDSA-001, PAIR-001, SQISIGN-001, SQISIGN-002, TECDSA-001 |
| completed | 6 | ICLIFT-001, XEDN-001/002/003, ECQ-001, ECRANK-001 |
| closed_at_budget | 2 | P13-001, ECQ-002 |

### 1b. Dispatch health of the 46 active goals (`tools/goal_portfolio_health.py`, 2026-09-30)

| bucket | n | goals |
| --- | --- | --- |
| ready (a Ready Task with no claim) | 1 | SEMBIN-fcb7a2 |
| batch_complete (waiting on a Coordinator checkpoint + next batch) | 28 | 19 SCURVE goals; CRYPTO-001, ECTD-001, PATH-001, RELN-001, SDEG-001, ECQ-e72c0b, ECRANK-002, ENDO-001, MONO-001 |
| blocked (gated / claimed / deferred; an ordinary state) | 13 | DREG-001, SATIC-c49b77, SEMBIN-5078bc, SEMBIN-cbf422, ECDLP-001, ECDLP-bbc21f, FROB-6333a9, GFPN-380702, SCURVE-137bd9, SSI-001; and three with no `dispatch_queue_path` on the head (ECQ-2298dc, ICPERF-e6b6a4, SSIQ-001) |
| needs_repair (dispatch itself fails) | 4 | AUXIN-a93442 (archive task TASK-20260930-84d19f declares a content_at_commit binding without `archive.commit_sha`); ECDLP2M-001 (`ledger/decisions/DEC-20260930-8de5ba.yaml` owned by two tasks); ICEX-001 and SIG-001 (legacy archive tasks TASK-20260731-024 / TASK-20260725-712 whose commits do not change exactly their declared artifacts) |

Reading: the portfolio's bottleneck is not ideation. Twenty-eight goals are
waiting for a checkpoint, four have integrity defects in their queues, and only
one has something dispatchable now. The three `needs_repair` entries dated
2026-09-30 (AUXIN, ECDLP2M) are fresh and are the first thing `/coordinate`
should look at; the two legacy ones (ICEX, SIG) have been carried since July.

### 1c. Open ECC ideas: 94, in 21 questions, heavily concentrated

`python3 tools/ecc_priority.py --open-ideas` (status `proposed`, no hypothesis
or experiment citing them): BINSTD 27, ECDLP 14, DREG 11, CERTBIN 10, ICPERF 8,
SEMBIN 5, GFPN 5, CRYPTO 3, NISTBIN 2, OAKLEY 2, SATIC 2, and one each in FROB,
CSIDH, PFDR, QSP, SSI. Under instruction 3 these are ranked design work already
owed; **this round does not add to BINSTD, CERTBIN, DREG, ICPERF or SEMBIN**,
which together hold 61 of the 94.

Active ECC goals whose questions carry ZERO open ideas: AUXIN, ENDO, ECTD,
MONO, RELN, ICEX, SDEG, SIG, SSIQ, ECRANK, ECQ, all twenty SCURVE, and the
ECDLP questions RQ-ECDLP-001/165d4b/4fcbd3/623a32/912694/c1b7b1/f0a7b0. In
most of these the September ideation rounds' proposals were consumed into
`specified` hypotheses (e.g. AUXIN's three 2026-09-05/06 ideas → 9 H-AUXIN
records; ECTD's eleven → 17 H-ECTD records), so "zero open ideas" means the
lane is waiting on design/approval, not that nobody has thought about it.

### 1d. Two findings for the Coordinator (advisory; no record changed here)

1. **Classification gap.** `GOAL-ENDO-001` is ECC, but its fourteen lane
   questions carry non-ECC area tokens (`RQ-ICINV-475b5e`, `RQ-VOLC-f6253b`,
   `RQ-JINV-8fc13a`, `RQ-EQIC-8cb959`, `RQ-EQLA-0d3f40`, `RQ-EWALK-8fa147`,
   `RQ-TORS-8c7b79`, `RQ-CANL-63098f`, `RQ-CLGP-b99df5`, `RQ-MODEL-e61cb2`,
   `RQ-GGMB-6eaabc`, `RQ-MTGT-2cabee`, `RQ-INSTR-f8faa0`; `RQ-PAIR-21313f` is
   the one ECC token). `tools/ecc_priority.py --classify RQ-JINV-8fc13a` says
   `non-ECC`, so the twelve `proposed` JINV ideas of 2026-08-07/11 (and any
   under the other twelve tokens) are invisible to the instruction-3 worklist.
   The same holds for the `TLD`/`CREP`/`XOR` tokens under the prime-field ECDLP
   goals. Remedy is one edit to `orchestration/research-priority.yaml`
   (`ecc_areas`), which is a policy change and is therefore left to a
   Coordinator decision rather than made here.
2. **Draft goals.** Seven ECC goals (the signature schemes, the pairing curves,
   CSIDH and both SQIsign goals) have sat in `draft` with 13–48 `specified`
   hypotheses each and no batch ever opened. Under "ECC first" they are ranked
   ahead of every non-ECC goal the moment they activate; nothing in this brief
   activates them, and this round files no ideas under them because their
   existing specified hypotheses are unexecuted.

## 2. Lane selection and what was deliberately not selected

Selected: lanes with an active goal (or user-named question) where the open
proposal pool is empty or nearly so AND where a genuinely new proposal could
change what the next batch does — biased, per `docs/target-result-profile.md`,
toward exponent-moving mechanisms and decisive deployed-parameter verdicts.

| lane | card | questions | why now |
| --- | --- | --- | --- |
| L1 | TASK-20260930-1500bc | RQ-SSIQ-9702af (+ RQ-SSI-001 context) | the program's exemplar lane; five levers analyzed, latest run deferred at an environment gate; no open SSIQ idea |
| L2 | TASK-20260930-34b1ce | GOAL-ENDO-001 lanes: RQ-ECDLP-912694, RQ-JINV-8fc13a, RQ-ICINV-475b5e, RQ-GGMB-6eaabc, RQ-INSTR-f8faa0 (+ the other nine) | fourteen lanes, several with no proposal at all; the gating lane ICINV unadjudicated |
| L3 | TASK-20260930-56a5c7 | RQ-AUXIN-f8d8c0 | decisive deployed-parameter verdict lane; one experiment queued, three ideas consumed, no open idea |
| L4 | TASK-20260930-5c3258 | RQ-LHW-1877bb, RQ-GRUMPY-964876, RQ-ECDLP-78dbc5 | user-named generic-group targets with sound verifiers; twelve proposals filed 2026-09-06, two hypotheses analyzed |
| L5 | TASK-20260930-9479a0 | RQ-ECDLP-623a32, RQ-ECDLP-4fcbd3, RQ-ECDLP-c1b7b1, RQ-ECDLP-165d4b (+ RQ-PFDR-ae2fba) | the central prime-field target; the object-frame constraint block exists precisely so ideation here does not regress to a known family |
| L6 | TASK-20260930-a1877b | RQ-ECDLP-f0a7b0, RQ-SATIC-1ae57a | user-directed SAT/SMT push (2026-09-05); SATIC goal blocked on an instrument classification, two open ideas |

Not selected, with the reason: BINSTD/CERTBIN/NISTBIN/OAKLEY/SEMBIN/ICPERF/
GFPN/QSP (61 open ideas already; the 2026-09-26 round covered them); ECTD
(eleven proposals already, and its next action is a scope decision, not an
idea); FROB (nine proposals, two tracks in flight); RELN/SIG/SDEG (twelve
proposals in the lane; their goals wait on activation residuals); ECRANK/ECQ
(twelve proposals; ECRANK-002 has two lanes in flight, ECQ-2298dc waits on a
human action); MONO (blocked on a measured review gap, DEC-20260904-67cde4);
SCURVE ×20 (next step is executing the filed audit plans); the seven draft
goals (section 1d).

## 3. Record form (bind every lane)

Copy the schema in `agents/idea-generator.md` "Required output" exactly, plus
the fields the program's recent records carry — use
`ledger/proposals/IDEA-20260926-89886c.yaml` as the exemplar of form (not of
content). Required on every record:

- `id` (pre-minted), `question_id`, `added: '2026-09-30'`, `status: proposed`,
  `approved_by: null`, `title`, `class`, `claim`, `mechanism`,
  `novelty_status` ∈ {known, adaptation, speculative, unverified};
- `origin` with `kind: generator_search`, `date`, `scope` naming this lane's
  TASK id, and `overlap_review` naming the existing proposals and hypotheses
  read (the lane's `context/` file lists them) and why this record is not one
  of them;
- `citations` with provenance on every entry; `verified_by: null` iff recalled;
- `assumptions`, `proof_search_map` (all four audits, or a
  `not_applicable_reason`), `predictions` with metrics and minimum effects,
  `minimal_test` with `design`, `controls`, `required_metrics` — the design
  must be a concrete cell (curve, field size, parameters, seeds rule, sample
  sizes, outcome table, falsification threshold fixed now);
- `falsification_conditions`, `confounders`, `interpretation_limits`;
- `heuristic_assumptions` (numbered, each with `rigorous_support` and a
  `validation_plan`), `target_complexity` (time and memory exponents vs
  `best_known`, `hidden_overhead`, `tradeoff_note`);
- `estimated_cost`, `recommended_priority` with `priority_rationale`;
- `dominated_by` and `sota_delta` per `docs/inventor-protocol.md` section 5;
- `prior_art` per `templates/research-records.md` "Prior art on ideas":
  `frontier_map: knowledge/frontiers/ecdlp`, `rows_checked` (real KR-* ids
  from `context/frontier-map-*.md`), `nearest` (≥1 entry with `ref`,
  `provenance`, `relation`, `delta`) or `none_found_after`, and `searched`;
  for a lane whose map has no bearing (L1 isogenies, parts of L2) use
  `frontier_map: not_applicable` with `not_applicable_reason` AND still name
  the nearest KN-* entries;
- `first_deliverable`, `next_gate`, `discriminated_from`, `source_refs`,
  `id_allocation_provenance` (the sentence in the exemplar, with this lane's
  TASK id).

Quality bar (from `agents/idea-generator.md`): an idea must discriminate
between at least two explanations, name what each outcome would mean, and
state exponents; "faster" is not a claim. An idea that only polishes a
logarithmic cofactor says so and says whether it is a required building block
of an exponent-moving idea. Aim for three ideas per lane of which at least one
is exponent-first in ambition (even if its honest expected outcome is a method
ceiling); a lane that cannot find three honest candidates files fewer and
returns the ids.

## 4. Shared context every lane reads

- `AGENTS.md` (core rules, target profile, inventor protocol summary),
  `agents/idea-generator.md`, `docs/inventor-protocol.md`,
  `docs/target-result-profile.md`, `templates/research-records.md`
  (sections "Prior art on ideas", "Citation provenance").
- `context/frontier-map-generic-rho.md`, `context/frontier-map-index-calculus.md`
  (the ECDLP known-results map, 48 rows), and `knowledge/frontiers/ecdlp/README.md`.
- `context/<lane>.md`: the lane's question records verbatim, its goal head(s),
  and the full list of existing hypotheses and proposals in the lane with
  status and title. **Read the proposal list before writing; a new record
  that restates one of them is returned.**
- `docs/object-frame-ideation.md` (L2 and L5 paste its section 3 block into
  their constraints; every lane that proposes a tracked object applies it).
- `docs/ecdlp-literature-review-20260926.md` and
  `docs/recent-cryptanalysis-literature-20260926.md` (what the program read
  this month; the second names the June–September 2026 results that changed
  the agenda).
- `python3 tools/obstruction_registry.py --debt` output (2026-09-30): 60
  negative evidence records carry no obstruction block; the ECC-relevant ones
  are EV-ECDLP-284817/3dc2db/65b004/b3e847/fd61e4, EV-ECTD-8c098d, EV-ENDO-001,
  EV-FALSIFY-0ed0d9/2a5e46/40291d/67150b/89e414/d07ef4, EV-IT-511f3d,
  EV-MONO-08a31f/7d24fe/b84b24, EV-SEMBIN-4614e7/d40877/f4408c, EV-SIG-001/008,
  EV-XEDN-001. Recovering one measured obstruction from its cited runs and
  re-reading it as a resource is itself a valid proposal (idea-generator.md,
  "Obstructions as generative material").

## 5. Identifier assignment (minted with `tools/allocate_id.py --next`, each confirmed with `--check` on 2026-09-30)

| lane | handoff | idea ids |
| --- | --- | --- |
| L1 SSIQ | TASK-20260930-1500bc | IDEA-20260930-024033, IDEA-20260930-0d7c7d, IDEA-20260930-27b6c1 |
| L2 ENDO | TASK-20260930-34b1ce | IDEA-20260930-39ad61, IDEA-20260930-5b9e0d, IDEA-20260930-655544 |
| L3 AUXIN | TASK-20260930-56a5c7 | IDEA-20260930-68326c, IDEA-20260930-6bde2d, IDEA-20260930-704e43 |
| L4 GENERIC | TASK-20260930-5c3258 | IDEA-20260930-750de2, IDEA-20260930-79abd9, IDEA-20260930-79c17d |
| L5 REPR | TASK-20260930-9479a0 | IDEA-20260930-8e3b75, IDEA-20260930-9620c8, IDEA-20260930-a6491b |
| L6 CONSTRAINT | TASK-20260930-a1877b | IDEA-20260930-b26bbc, IDEA-20260930-ba8184, IDEA-20260930-c5466b |

Spare, unassigned (used only if a lane's report asks and the dispatcher
re-checks them): IDEA-20260930-c680ba, -cc88c6, -d2a10b, -d6fa76, -e44ca6,
-f8b697; TASK-20260930-b4ba3f, -cb720a.

## 6. What happens after the lanes return

The dispatching session (this one) verifies each record against section 3,
runs `python3 tools/build_frontier_map.py --match "<claim + mechanism>"` and
`python3 tools/validate_ledger.py`, sends incomplete records back to the lane
that wrote them (never repairs them itself), commits the accepted records and
this directory in one commit naming the six handoff ids, pushes the branch,
and reports to the user. Filing under this brief approves nothing: every
accepted record enters `python3 tools/ecc_priority.py --open-ideas` as ranked
design work for the next `/coordinate` selection point, where it competes with
the 94 already there.

## 7. Corrections (2026-10-01, dispatching session)

Recorded additively; the text above is left as written so the dispatch it
drove stays auditable.

1. **The lane-context extractor under-reported GOAL-ENDO-001.** The L2 lane
   (TASK-20260930-34b1ce) found by literal grep that nine of the goal's
   fourteen lane questions, listed in `context/L2-ENDO.md` with zero
   proposals and zero hypotheses, are heavily populated. Re-counted by the
   dispatcher at `1abae22c8` over `ledger/proposals/` + `ledger/ideas/` and
   `ledger/hypotheses/`, by `question_id`:

   | question | proposals (status `proposed`) | hypotheses |
   | --- | --- | --- |
   | RQ-JINV-8fc13a | 40 (40) | 32 |
   | RQ-ICINV-475b5e | 24 (23) | 19 |
   | RQ-INSTR-f8faa0 | 23 (23) | 14 |
   | RQ-VOLC-f6253b | 21 (21) | 10 |
   | RQ-MTGT-2cabee | 19 (19) | 10 |
   | RQ-CLGP-b99df5 | 19 (19) | 10 |
   | RQ-EQIC-8cb959 | 17 (17) | 9 |
   | RQ-CANL-63098f | 17 (17) | 11 |
   | RQ-PAIR-21313f | 17 (17) | 10 |
   | RQ-EWALK-8fa147 | 16 (16) | 6 |
   | RQ-MODEL-e61cb2 | 16 (16) | 7 |
   | RQ-TORS-8c7b79 | 15 (15) | 8 |
   | RQ-EQLA-0d3f40 | 14 (14) | 6 |
   | RQ-GGMB-6eaabc | 14 (14) | 2 |
   | RQ-ECDLP-912694 | 5 (5) | 5 |
   | **total** | **277 (276)** | **159** |

   Cause: the extractor selected records by a hand-listed subset of question
   ids and by area token, not by the goal head's `question_ids` list. The
   sentence in section 2 ("fourteen lanes, several with no proposal at all")
   and the L2 card's instruction to "prefer lanes with no open proposal" were
   therefore wrong; the L2 report documents the lane choices it made instead
   and the two near-duplicates it caught and dropped. Section 1c's statement
   that ENDO carries zero open ECC ideas remains literally true only because
   those 276 `proposed` records sit under non-ECC area tokens — which makes
   finding 1d.1 (the classification gap) larger than stated: it hides roughly
   two hundred and seventy `proposed` records under one active ECC goal, not a
   dozen. `IDEA-20260930-655544` (L2) proposes the extractor control.
2. **`ledger/ideas/` is a second proposals directory** (18 records;
   `tools/ecc_priority.py` reads both). The dispatcher's first existence check
   looked only in `ledger/proposals/` and wrongly told lane L3 that
   `IDEA-20260831-ccb587` did not exist; the lane resolved it correctly.
3. **Prior-art `nearest` refs.** Section 3 did not say that
   `prior_art.nearest[].ref` accepts only `KR-*` rows and `KN-*` entries
   (`templates/research-records.md`; `tools/validate_ledger.py`
   `check_prior_art`). Lanes L2, L3 and L6 cited `IDEA-*`/`CORR-*` ids, ledger
   paths or URLs there and were each returned once for that single fix; the
   displaced pointers moved to `citations` and `discriminated_from`.
4. **Dispatch log.** All six lanes were first launched on 2026-09-30 and
   terminated by an API spend limit before any file was written; relaunched
   2026-10-01 after the reset. L1 and L4 were then terminated by a
   content-safeguards classifier false positive on the session model and
   relaunched on a different model under the cards' `fallback_allowed: true`,
   with `fallback_used: true` and the reason recorded in their reports.
   Records are therefore filed with `added: '2026-10-01'` under ids minted
   2026-09-30.
5. **Filing in two commits, not one (deviation from section 6).** At 03:30 UTC
   on 2026-10-01 every running lane was terminated by an API session limit
   (resets 06:50 UTC) after writing its records. Fourteen records were on
   disk and all fourteen pass the dispatcher's acceptance check; the full
   ledger validator then rejected two of them on one rule — `novelty_status:
   adaptation` with `recalled` citations (`IDEA-20260930-6bde2d`,
   `IDEA-20260930-8e3b75`; the honest label is `unverified`). Because the
   container is ephemeral, the twelve clean records are filed now
   (L2 ×3, L3 ×2, L4 ×3, L5 ×1, L6 ×3) and the two held records are filed
   after their own lanes relabel them; L4's lane report (which carries its
   `fallback_used: true` note — recorded in item 4 meanwhile) and lane L1,
   which never got to write, follow after the reset. Filing approves nothing.
