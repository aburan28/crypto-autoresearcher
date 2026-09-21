# Repair Map — TASK-20260905-5bf422

- kind: repair-map
- status: design_only_not_frozen_not_authorized
- recorded_at: 2026-09-05
- role: idea-generator
- task: TASK-20260905-5bf422 | batch: BATCH-169639 | goal: GOAL-AES-003 | question: RQ-AES-003
- candidate: IDEA-20260904-6aed0b
- mandate: DEC-20260905-7d0311, handoff `ledger/handoffs/TASK-20260905-5bf422.yaml`
- archived_by: TASK-20260905-bd2cf5
- id_note: Self-descriptive label. NO identifier was minted via `tools/allocate_id.py`
  in this session: minting writes allocator state outside this task's write_scope,
  which the task constraints forbid.
- companion deliverables:
  - `coordination/goals/GOAL-AES-003/batches/BATCH-169639/tasks/TASK-20260905-5bf422/superseding-design.yaml` (121,331 bytes)
  - `coordination/goals/GOAL-AES-003/batches/BATCH-169639/tasks/TASK-20260905-5bf422/superseding-budget.json` (21,145 bytes)

Supersession (package, by explicit reference; snapshot commit `8616e32c7`):

| superseded artifact (IMMUTABLE, read-only, never edited) | disposition |
|---|---|
| `coordination/goals/GOAL-AES-003/batches/BATCH-a019c8/tasks/TASK-20260905-5d22e9/execution-design.yaml` | superseded in full by `superseding-design.yaml` |
| `coordination/goals/GOAL-AES-003/batches/BATCH-a019c8/tasks/TASK-20260905-5d22e9/execution-budget.json` | superseded in full by `superseding-budget.json` |
| `coordination/goals/GOAL-AES-003/batches/BATCH-a019c8/tasks/TASK-20260905-5d22e9/outcome-sentence-map.md` | carried forward UNCHANGED by explicit immutable reference (design `outcome_sentence_map`) |

This map indexes the repairs; the design YAML is the binding-text carrier; the
budget JSON is its machine-readable mirror. This map authorizes nothing, changes
no status, and is not evidence. ZERO ARMS were executed; no existing file was
modified; no git command was run; no ledger write occurred.

## 1. Binding-list choice (RT4-SR-1) — the one-line answer

**The ACTUAL immutable YAML `arm_table` of TASK-20260905-5d22e9 at `8616e32c7`
is adopted as the ONE committed (seed, armid) list**: committed verbatim in
`superseding-design.yaml` `arm_plan.arm_table` and transcribed tuple-for-tuple
into `superseding-budget.json` `arms` — identical in both directions BY
CONSTRUCTION, with no contingency clause of any kind in either artifact.

The committed list (17 tuples; position = committed run order; every arm cell
(1,1), 2^30 trials, r as shown, PIN-T0):

| pos | arm_id | kind | k | r | seed | armid |
|----|--------|------|---|---|------|-------|
| 1 | FM-A00 | ramp_zero_anchor | 0 | 5 | 531001 | 5 |
| 2 | FM-N01 | r6_null_object | – | 6 | 531201 | 1 |
| 3 | FM-K4-1 | k4_primary | 4 | 5 | 531101 | 4 |
| 4 | FM-K16-1 | k16_primary | 16 | 5 | 531102 | 8 |
| 5 | FM-N02 | r6_null_object | – | 6 | 531202 | 1 |
| 6 | FM-K4-2 | k4_primary | 4 | 5 | 531103 | 4 |
| 7 | FM-K16-2 | k16_primary | 16 | 5 | 531104 | 8 |
| 8 | FM-K8-1 | k8_secondary_report_only | 8 | 5 | 531109 | 6 |
| 9 | FM-N03 | r6_null_object | – | 6 | 531203 | 1 |
| 10 | FM-K4-3 | k4_primary | 4 | 5 | 531105 | 4 |
| 11 | FM-K16-3 | k16_primary | 16 | 5 | 531106 | 8 |
| 12 | FM-N04 | r6_null_object | – | 6 | 531204 | 1 |
| 13 | FM-K4-4 | k4_primary | 4 | 5 | 531107 | 4 |
| 14 | FM-K16-4 | k16_primary | 16 | 5 | 531108 | 8 |
| 15 | FM-K8-2 | k8_secondary_report_only | 8 | 5 | 531110 | 6 |
| 16 | FM-N05 | r6_null_object | – | 6 | 531205 | 1 |
| 17 | FM-N06 | r6_null_object | – | 6 | 531206 | 1 |

### Justification

1. **The mandate names the artifact.** The handoff's BINDING-LIST CHOICE says
   "adopt the governing YAML arm_table ... the YAML is the governing record".
   This adopts the YAML's actual committed rows.
2. **RT4-SR-1's exact correction text matches this table**, not the
   parenthetical: "FM-K8-1 seed 531109; positions 10/11/13/14 seeds
   531105/531106/531107/531108".
3. **J-D1's F-1/F-2 per-arm diffs** describe this table as the governing one
   and the superseded mirror's rows as the defect (armid 4 on the k = 16 and
   k = 8 arms; a run-order-shifted seed column at positions 8/10/11/13/14).
4. **Seat convention** (design `arm_plan.seats_armid_convention`, from
   IDEA-20260903-8f26ac): k = 4 -> armid 4, k = 8 -> armid 6, k = 16 -> armid 8,
   r = 6 null -> armid 1, k = 0 anchor -> armid 5. This table satisfies the
   convention on all 17 rows (self-check S5f); the superseded mirror's rows
   violated it on six arms.
5. **Invariance.** The seed MULTISET is identical under either candidate
   mapping (531001 once; 531101..531110 once each; 531201..531206 once each),
   so no arm's exposure, run order, gate constant, price, or statistic changes:
   the choice fixes which tuple each named arm runs under, not what is run in
   aggregate. The requirement is ONE list, mechanically derivable, mirrored
   exactly — not a particular list.

### Flagged for Coordinator attention (deviation 1)

The handoff parenthetical (and DEC-20260905-7d0311's F-2 rationale line)
mis-describes the YAML table it recommends: it says "floor seeds 531101-104 and
531106-109 at positions 3,4,6,7,10,11,13,14; report-only k=8 seeds 531105/531110
at positions 8,15". That seed column is the superseded JSON mirror's run-order
assignment (positions 3,4,6,7,8,10,11,13,14,15 taking 531101..531110 in order)
paired with the YAML's armids — a hybrid matching NEITHER artifact. The actual
YAML assigns floor seeds 531101..531108 to the eight primary arms and
531109/531110 to the two k = 8 report-only arms. Recorded in the design's
`procedure_deviations` item 1 and `design_choices_for_coordinator_attention`
item 1, and surfaced here for the focused re-review DEC-20260905-7d0311
requires.

## 2. Finding-by-finding map (handoff repair items (a)-(f))

### (a) RT4-SR-1 (BLOCK, J-D2) / J-D1 F-1 — contradictory committed arm tables (the P5 post-data seam)

- **Defect.** The superseded package carried two conflicting committed arm
  tables; its mirror directed an executor to run 8 of the 10 floor arms at
  (seed, armid) pairs different from the YAML `arm_table`; P5 admissibility
  hung on which list bound — the design's only post-data discretionary path
  (J-D2 RT4-F1).
- **Fix locations.** Design: `arm_plan.arm_table` (`note` + `arms`, lines
  ~688-719 — THE one committed list); `arm_plan.seats_armid_convention` (~617);
  `binding_cascade_text_carried.admissibility_preconditions.p5_one_list_note`
  (~905 — P5 admits no post-data choice of list: there is only one);
  `supersedes.defect_being_repaired` (~63). Mirror: `superseding-budget.json`
  `arms` (lines 44-61) + `machine_readable_mirror_note` (line 22 — agreement BY
  CONSTRUCTION; the superseded mirror's rows bind nothing).
- **Prohibition honored.** No clause of any barred family exists in either
  artifact: nothing directs an executor to harmonize artifacts, to select
  between record states, or to treat one record as prevailing over the other;
  the barred vocabulary has ZERO occurrences in all three deliverables
  (S6a-S6c).
- **Verified.** S4a-S4d (tuple identity, ordered, both directions, set
  equality), S5f.

### (b) J-D1 F-2 — seed derivation rule did not reproduce the committed table

- **Fix locations.** Design: `arm_plan.seed_blocks.derivation_rule` (~632),
  `explicit_enumeration_note` (~656), block lists (~666-669). Mirror:
  `seed_blocks` (lines 72-79).
- **Corrected rule.** PRIMARY FLOOR block 531100 + j, j = 1..8, to the eight
  primary floor arms (k in {4, 16}) in committed run order — positions
  3,4,6,7,10,11,13,14. The two k = 8 REPORT-ONLY arms are OUTSIDE the
  primary-floor assignment (precisely the reading the superseded rule left
  unstated): 531108 + j, j = 1..2 — positions 8,15. NULL block 531200 + j,
  j = 1..6 — positions 2,5,9,12,16,17. Anchor takes committed 531001. Blocks
  pairwise disjoint; disjoint from the committed triple 531001/531002/531004
  except the anchor's declared, seed-inert use of 531001. Arithmetic on
  declared block bases alone; consults no realized reading, outcome, or
  red-team object. The rule is derivation lineage of the committed table, not
  an independent source: one list, two views.
- **Verified.** S3 (mechanical application reproduces all 17 position->seed
  assignments exactly), S5a-S5e.

### (c) J-D1 F-3 — two bound-carrying sentences lacked priced-semantics statements

- **Fix locations (true INLINE carriage).** Design:
  `arm_plan.why_D2_and_not_the_alternatives.vs_D1` (~555-599) — the PRICED
  SEMANTICS of 0.171940 and of the companion 0.018883 are carried inline in
  the sentence itself; and
  `binding_cascade_text_carried.proves_too_much_paper_routing_pre_arm.obligation`
  (~1244-1281) — the OBJ-4 routing sentence carries the priced semantics of
  0.018883 (and 0.171940) inline.
- **Verified.** Text inspection; both sites comply under either the former
  absolute rule or the relaxed rule of item (e).

### (d) RT4-SR-2 (REVISE, J-D2) / J-D1 F-5 — false "exact Garwood" derivation for the G4 threshold

- **Fix locations.** Design:
  `binding_cascade_text_carried.committed_constants.g4_pooled_null_hard_threshold_at_n6`
  (~829); the `gates_evaluated_in_fixed_order.branch_G4_FM_NULL_CONTROL_FAIL`
  text parenthetical (~964+); the U3 use-inventory disclosure inside the same
  committed_constants block. Mirror: `cascade_constants.g4_note` (line 132).
- **Correction.** The THRESHOLD 39 IS KEPT unchanged and unambiguous (the
  conjunct consumes exactly 39; committed round-number hard-gate threshold,
  preregistered pre-arm at n = 6). The FALSE derivation label is REMOVED: 6.5
  is not "the exact Garwood lower bound of the committed single-arm h = 12
  reading". Recorded corrected derivation: exact two-sided 95% Garwood lower
  bound at h = 12 is 6.2006 (implying 38); exact one-sided 95% lower bound is
  6.9242 (implying 42); 39 = 6 x 6.5 sits exactly between the two conventions'
  implications and fires one count LATE against the two-sided-derived
  threshold. Licensing impact bounded: G4 halts compose no sentence, and the
  comparator-setting step restates the cascade against U_null. U3/SR-4
  disclosure carried: third disclosed use of the five committed readings — a
  gate calibration referencing the committed k = 16 reading h = 12, not an
  evidential input; it enters no branch conjunct, no test statistic, no
  equivalence criterion, and no composed sentence.
- **Verified.** V1 ('6.2006', '6.9242' present); text inspection.

### (e) J-D1 F-4 — pointer-form R5-1 sites vs the design's own "not by pointer" rule

- **Remedy chosen: EXPLICIT RELAXATION with recorded rationale** (not
  inlining). Design: `priced_semantics_r5_1.application_rule` (~211) and
  `f4_remediation_choice` (~228).
- **Rationale (recorded, no silent inconsistency).** (1) J-D1 found ~9
  pointer-form sites while R5-1's substance held everywhere — each is an
  explicit named attachment inside the same block/file whose head carries the
  full canonical statement; (2) FIVE sites are inside outcome-sentence-map.md,
  snapshot-archived at 8616e32c7 and IMMUTABLE — they cannot be inlined by any
  repair record, so relaxation is the only remedy covering every site without
  editing an immutable record; (3) J-D1's own F-4 remedy text names this
  option. RELAXED rule: bound-carrying record/registry/map-row text carries
  the canonical statement inline OR by explicit named attachment inside the
  same block/file section whose head carries it. STRICT rule UNCHANGED: every
  COMPOSED SENTENCE of any future execution batch carries the statement
  INLINE. No gate, conjunct, or license boundary is touched. The two BARE
  sites (neither inline nor attached) are repaired separately under item (c).
- **Verified.** Text inspection; mirror's `sentence_level_prices.note` and
  `fp_budget_r5_2` priced-semantics fields comply as explicit named
  attachments.

### (f) RT4-SR-3..RT4-SR-6 — successor disclosures carried into the repaired record

- **RT4-SR-3** (zero-count aliveness edge): design
  `binding_cascade_text_carried.step_5_2_branch_2_FM_DECAY_CONTINUES.zero_count_edge_composition_instruction_rt4_sr3`
  (~1088) + `rt4_successor_disclosures_carried.rt4_sr3_zero_count_aliveness_edge`
  (~1724). Binding composition instruction: if T_k = 0 at either primary point
  and a branch carrying the floor-is-alive statement fires, the composed
  aliveness sentence must be FLAGGED as the carried NARROW-1 standing finding
  and DISCLOSED BESIDE the zero reading (reachable edge (T_4, T_16) = (12, 0),
  ~1.7e-5 under an analytic-null-scale k = 16 rate). Disclosure discipline
  only: no conjunct, routing, or license boundary changes.
- **RT4-SR-4** (halted-batch partial readings): design
  `rt4_successor_disclosures_carried.rt4_sr4_halted_batch_partial_readings`
  (~1736). Standing obligation on successors: any future design citing partial
  primary readings surviving an early-stopped batch as committed planning
  inputs (U1/U3-class uses) must disclose the halt context in its use
  inventory. This design's own U1/U3 uses cite COMPLETED-batch readings
  (EV-AES-868db1, EV-AES-ac5c12 lineage).
- **RT4-SR-5** (transcription-plus-additions provenance): design
  `rt4_successor_disclosures_carried.rt4_sr5_transcription_plus_additions_provenance`
  (~1751). Enumerates exactly the design-owned additions of the superseded
  record (i)-(iv) and of THIS record (v)-(xi), so the binding carrier's
  provenance is exact and any unenumerated discrepancy is a finding against
  this record, resolvable only by a new superseding record.
- **RT4-SR-6** (hygiene): design
  `rt4_successor_disclosures_carried.rt4_sr6_hygiene_items` (~1791), with:
  (a) the original-rule (no-margin-conjunct) plateau bound labelled as such in
  `prohibited_sentence_register.live_values_register` (~1645) and NEVER the
  binding sentence price (binding: 0.171940 with its R5-1 priced semantics;
  the numeral is carried only in the design's register, not in the mirror);
  (b) the Section-A count phrasing corrected — FIVE gate/halt verdicts (G1-G4
  plus FM-INADMISSIBLE-INPUT) plus resource_exhaustion, the six rows of
  Section A — in `outcome_sentence_map.coverage_claim` (~1704) and applied to
  the immutable map by reference via
  `outcome_sentence_map.corrections_applying_by_reference` (~1684);
  (c) the k = 8 kind label harmonized to `k8_secondary_report_only` in BOTH
  artifacts; (d) the U2 instrument-review trigger remains the ONLY causal use
  of k = 8 data, review-facing and never sentence-facing
  (`controls_and_disclosures.report_only_surfaces`, ~1588).

## 3. Self-checks (run in this session)

Record-integrity checks on the committed text of these deliverables — NOT
experiment runs, NOT statistical simulations (zero-arm attestation, design
`zero_arm_attestation`). Script: exact-decimal arithmetic, YAML/JSON parse,
mechanical rule application, tuple comparison, substring scans. Results:

| check | statement | result |
|---|---|---|
| S1 | superseding-design.yaml parses (35 top-level keys, 17 arms) | PASS |
| S2 | superseding-budget.json parses | PASS |
| S3 | derivation rule mechanically reproduces the committed table (17/17 positions) | PASS |
| S4 | ONE list: YAML arm_table vs JSON arms identical tuple-for-tuple, ordered, both directions, set equality, no extras/omissions | PASS (4/4) |
| S5 | seed usage: 531109/531110 only on the k = 8 report-only arms; 531105 only FM-K4-3 (position 10); 17 distinct seeds; blocks pairwise disjoint; seat convention on every row; every arm 2^30 trials | PASS (7/7) |
| S6 | zero hits on the four barred token families named in the handoff's BREAKS-level prohibition (constraint 5), scanned case-insensitively across all three deliverables | PASS (3/3) |
| S7 | numeral discipline: superseded arcsine power-sizing numeral absent from every deliverable; the RAT-5 citation-error figure occurs EXACTLY ONCE design-wide, inside the verbatim `rat_5` quotation (J-D1 check 7: ACCEPTABLE CARRIAGE, mentions-not-uses), zero in mirror and map; every 0.970869 occurrence labelled CONDITIONAL-ON-BRANCH-H-NOT-FIRING | PASS (5/5) |
| FP | exact-decimal pricing arithmetic: 0.171940 + 0.018883 = 0.190823; 8 x 0.171940 = 1.375520; 8 x 0.018883 = 0.151064; sum 1.526584; 17 x 2^30 = 18253611008; 17 x 1620 = 27540; mirror totals and per-arm commitment figures identical across artifacts | PASS (9/9) |
| V | unchanged quantities present verbatim in the design (0.190823, 1.526584, 18253611008, 27540, 29500, 11700, [9.903, 27.219], 0.952538, 0.018883, 0.171940, 0.989349, 0.884236, anchor readings h(4)=17/21 h(8)=13/18 h(16)=12, PIN-T0, AMEND-1, SCOPE-1, NARROW-1..5, RAT-3/4/5, R5-1..3, RT3-SR-1..4, 8616e32c7, corrected G4 constants 6.2006/6.9242) | PASS (2/2) |
| S8 | zero-arm: 0 arms executed, 0 experiment runs authorized/performed; task directory contains exactly task_card.yaml + the three deliverables; no existing file modified; no git command run; no identifier minted; no ledger write; writes confined to write_scope | PASS |

## 4. Procedure deviations (mirror of design `procedure_deviations`)

1. **BINDING-LIST PARENTHETICAL.** The handoff parenthetical and the DEC F-2
   rationale line mis-describe the actual YAML arm_table (Section 1 flag
   above). The actual YAML table was adopted; the mandate's requirement (ONE
   list, mechanically derivable, mirrored exactly) is satisfied. Flagged for
   the Coordinator and the focused re-review.
2. **STALE-SEED CHECK ADAPTED.** The handoff's verification instruction
   ("531105/531110 must appear ONLY as k=8 report-only arms if you adopt the
   recommended list") presupposes the parenthetical's mis-described list.
   Under the adopted actual-YAML list the corresponding check is: 531109 and
   531110 appear ONLY as the k = 8 report-only arms' seeds, and 531105 appears
   ONLY as FM-K4-3's committed seed (primary floor arm, position 10). Both run
   and pass (S5a-S5c).
3. **OUTCOME MAP CARRIED BY EXPLICIT IMMUTABLE REFERENCE** (the handoff's
   named alternative to verbatim reproduction), with the two
   DEC-20260905-7d0311-mandated text-level corrections (RT4-SR-2 derivation
   label; RT4-SR-6 Section-A count phrasing) recorded in the design and
   applying to the map by reference, because the map is snapshot-archived and
   immutable. No map row's trigger, effect, licensed sentence, or prohibition
   changes.
4. **TWO ZERO-SEMANTIC-CHANGE PHRASE SUBSTITUTIONS** in the carried G1 gate
   text and the SR-5 custody-checkpoint text (design `rt4_sr5` item xi),
   replacing the vocabulary the handoff's BREAKS-level prohibition bars with
   "failed re-check / fails to reproduce the committed digest" phrasing, so
   all three deliverables carry zero occurrences of it. Routing
   (FM-GATE-FAIL), bounded attribution, and gate semantics are unchanged.

## 5. Inference provenance (identical block in all three deliverables)

- requested_policy: research-deep
- reasoning_effort: null
- fallback_used: true — the opencode idea-generator role binding is
  balance-dead in this environment (known since DEC-20260903-16bfc2); this
  session was dispatched as a general agent carrying the full idea-generator
  role contract, per the handoff's fallback_allowed: true
- degraded_allowed: false; degraded_requirements: [] (none claimed; whether
  the served reasoning effort matches the research-deep intent cannot be
  verified from inside this dispatch and is not asserted)
- resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
  (session-reported identifier; no adapter probe was executed for this
  session, so it is unverified configuration — recorded rather than omitted
  per AGENTS.md model policy)
- model_verified: false
- independent_session: true

## 6. Value discipline (echo of design `live_values_register`)

- LIVE: per priced arm 0.190823 = 0.171940 + 0.018883 (exact); grand
  ACCOUNTING sum 1.526584 (explicitly not an event probability); written-order
  decay power 0.952538; OBJ-5B comparator routing 0.989349 -> 0.884236 as phi
  runs 1.0 -> 2.0; plateau residual range exactly [0.114124, 0.171940]; exact
  Garwood anchor CI [9.903, 27.219].
- NEVER LIVE: the RAT-5 citation-error figure (single occurrence, inside the
  verbatim quotation that records the error); the superseded arcsine
  power-sizing numeral (not reprinted anywhere); the Branches-1-5-only decay
  power 0.970869 (CONDITIONAL-ON-BRANCH-H-NOT-FIRING label only).
- The original-rule (no-margin-conjunct) plateau bound appears only in the
  design's register under its RT4-SR-6 label and is never the binding
  sentence price.

## 7. What remains gated

This package freezes nothing, authorizes nothing, and changes no status. Per
DEC-20260905-7d0311 the focused re-review is a precondition of any future
authorization: validator re-derivation of the single committed list and the
seed rule, and red-team re-attack of the P5 seam only. Authorization of D-2
(or any successor) remains a SEPARATE committed Coordinator decision that
freezes this design (or a further superseding one) by exact path, write-once
pre-arm.
