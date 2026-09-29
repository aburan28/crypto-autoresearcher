# RT2-SR-1..4 correction pass — correction-diff

- Task: `TASK-20260904-b88e9a` (batch `BATCH-519c76`, goal `GOAL-AES-003`)
- Role: idea-generator (role contract) served by a general agent under `fallback_allowed: true`
- Date: 2026-09-04
- Method: surgical text substitution by authoring scripts (`rt2_make_design.py`,
  `rt2_make_design2.py`, `rt2_make_pricing.py`); every substituted fragment was
  asserted unique in its source file before replacement; both structured outputs
  were machine-parsed (`yaml.safe_load` / `json.loads`) by the same scripts with
  content assertions. Zero experiment arms, zero instrument contact, zero new
  statistics, no git operations, no modification of any existing file.

## Deliverables

| # | Path (relative to worktree) | Bytes | Parse |
|---|------------------------------|-------|-------|
| A | `coordination/goals/GOAL-AES-003/batches/BATCH-519c76/tasks/TASK-20260904-b88e9a/corrected-design.yaml` | 132428 | `yaml.safe_load` OK |
| B | `coordination/goals/GOAL-AES-003/batches/BATCH-519c76/tasks/TASK-20260904-b88e9a/pooled-exposure-pricing-v2.json` | 99430 | `json.loads` OK |
| C | `coordination/goals/GOAL-AES-003/batches/BATCH-519c76/tasks/TASK-20260904-b88e9a/correction-diff.md` | this file | n/a |

Sources (read-only): `ledger/proposals/IDEA-20260904-06c396.yaml` and
`coordination/goals/GOAL-AES-003/batches/BATCH-e479db/tasks/TASK-20260904-30f2f7/pooled-exposure-pricing.json`.

## RT2-SR-1 — margin rationale rewrite (design pointer + pricing field)

**What changed.** The false claim that `c_margin = chi2_0.95(3)` is "the LARGEST
threshold defined purely from the null law" is dropped. `q = 0.95` is now named
as a *conventional* level choice among the null-law level quantiles
`{0.90, 0.95, 0.975}` that lie below the gate `c_gate = chi2_0.99(3) = 11.344867`;
`chi2_0.975(3) = 9.348404` is disclosed as the larger null-law level quantile
still below the gate; and it is disclosed that the level was fixed in the
revision session with the OBJ-5 calibration arithmetic in view, while no
realized reading and no OBJ-5 outcome enters the threshold VALUE
(`7.814728 = chi2_0.95(3)`, unchanged).

**Design file** — `idea.sr3_remedy_statement.margin_rationale_pointer`
(rewritten; formerly asserted the margin "is the LARGEST threshold defined
purely from the null law"). The pointer now carries the corrected rationale
summary, names both quantiles, and names `pooled-exposure-pricing-v2.json` as
the corrected pricing companion.

**Pricing file** —
`sr3_remedy.conjunct.margin_rationale_preregistered_from_the_null_law`
(rewritten). Before (core claim): "The 95th percentile of the null reference
law is chosen because it is the LARGEST threshold defined purely from the null
law ... nothing in the choice consults OBJ-5 ... or any realized reading".
After: conventional-level wording as above, including the disclosure that the
remedy *choice* (option (a) over option (b)) was made by comparing
false-positive outcomes on the OBJ-5 calibration family while the threshold
*value* remains the named pre-arm quantile.

**Not changed:** `c_margin` value, `c_gate` value, the SR-3 conjunct statement
itself, any verdict.

## RT2-SR-2 — written-cascade-order routing restatement (pricing file only)

Verified precondition: `IDEA-20260904-06c396.yaml` contains **no occurrence**
of `0.970869` or `0.9981704`, so RT2-SR-2 applies to the pricing file alone
(recorded in `correction_pass_provenance.corrections_applied` of artifact A).

Corrected quantities used (copied, not re-derived, from DEC-20260904-031ed2 /
TASK-20260904-937822): decay power `0.970869 -> 0.952538` with `0.018883`
routing to `FM-OVERDISPERSED`; OBJ-5B comparator `0.9981704 -> 0.989349`
falling to `0.884236` as `phi` runs `1.0 -> 2.0`, with `0.115764` to
`FM-OVERDISPERSED` at `phi = 2.0` (both-points split reading). Wherever the
original Branches-1-5-only values are retained they are explicitly labelled
**CONDITIONAL ON BRANCH H NOT FIRING**.

Restated fields:

- `proves_too_much_routing.note` — correction note added.
- `proves_too_much_routing.objects[3]` (OBJ-4) `.routing` — written-order
  numbers first, former exact value labelled conditional.
- `proves_too_much_routing.objects[3].residual_error_rate_disclosed` —
  conditional-convention label added (values unchanged).
- `proves_too_much_routing.objects[5]` (OBJ-5B) `.routing` — written-order
  numbers first (`0.989349` at `phi = 1.0` falling to `0.884236` at
  `phi = 2.0`; `0.115764` to `FM-OVERDISPERSED`), former `0.9981704` labelled
  conditional; marginal-vs-within-point distinction corrected.
- `sr3_remedy.effect.on_the_decay_branch` — propagated `0.952538` /
  `0.018883`, former value labelled conditional.
- `design_ladder.designs[D-2]` — `power_vs_rho_2_exact_verified` split into
  `power_vs_rho_2_exact_verified_written_cascade_order: 0.952538` and
  `power_vs_rho_2_exact_verified_branches_1_to_5_only_conditional_on_branch_h_not_firing: 0.970869`;
  `.reading` corrected to match.
- `decay_detection_power.exact_values_verified_at_n4_rho2` — `.note` gains the
  convention label; new `.convention` field added;
  `.interaction_with_sr3` corrected.
- `decay_detection_power.headline_reading` — corrected power wording.
- `power_derivation_worksheet.note` — correction note added; D-2 row's
  `superseded_by_exact` split into the two labelled fields.
- `derivation_provenance.cross_validation_summary` — decay-branch entry gains
  the convention label (values unchanged).
- `blind_rederivation_target_list.targets` — "NEW (cross-checks)" entry gains
  the written-order note.
- `blind_rederivation_target_list.expected_disagreements` — corrected to name
  both exact values for the D-2 cell.
- `hand_derivation_caveats` C3 — corrected to name both exact values.
- Top-level metadata: `correction_of`, `correction_task_id`,
  `correction_batch_id`, `rt2_corrections_applied_here`,
  `rt2_corrections_not_applied_here`, `correction_pass_inference` (additive).

**Not changed:** all routing verdicts; OBJ-1..3, OBJ-5A routings; all
thresholds; all committed inputs; all other power cells.

## RT2-SR-3 — glyph fidelity and RAT-5 verbatim placement (design file)

- `idea.verbatim_amend1.text`: restored `U+2212` (`−`) and `U+00D7` (`×`) in
  `hits − threads×HIT_LOG_CAP` (source had ASCII `-`/`*`). Restored block is
  character-identical (folded) to the AMEND-1 statement of
  `ledger/decisions/DEC-20260901-6f9de3.yaml` — script-verified.
- `idea.verbatim_narrowings[NARROW-3].text`: restored em dash `U+2014` in
  `determinism-discipline — exact re-runs`. Character-identical (folded) to
  the NARROW-3 statement of `ledger/decisions/DEC-20260902-7ad3d9.yaml` —
  script-verified.
- `idea.ci_correction_carried`: `text` now quotes RAT-5 **verbatim** (folded
  value character-identical to `ratifications`, id `RAT-5`, of
  `ledger/decisions/DEC-20260903-be4472.yaml` — script-verified), with a
  `quotation_status` field recording the repair. The former carrier paraphrase
  is **moved outside** the verbatim-standing-discipline section to a new
  `idea.ci_correction_carrier_paraphrase` field below the OBJECT-FIRST
  GENERATION divider, its text preserved unchanged and its
  `quotation_status` declaring it a paraphrase.

**Glyph source substitution (procedure deviation):** RT2-SR-3 named
`ledger/proposals/IDEA-20260903-bd730d.yaml` as the copy source. Byte-for-byte
inspection in this session shows that file contains **zero** non-ASCII
characters anywhere (its own verbatim blocks are already ASCII-normalized), so
a byte-faithful copy from it cannot restore the glyphs. The glyphs were
therefore copied from the cited source decision records instead
(DEC-20260901-6f9de3, DEC-20260902-7ad3d9, DEC-20260903-be4472) and verified
character-for-character by the authoring scripts. Disclosed here and in the
provenance block of artifact A.

## RT2-SR-4 — OBJ-5B split points named (pricing file)

`proves_too_much_routing.objects[5].object` (variant B) now names that the
bimodal per-seed split is carried **AT BOTH POINTS (k = 4 and k = 16)** — the
both-points reading consistent with the both-points mean constraint and the
reading used by the entry's written-order routing numbers; the k=4-only
reading is noted as lowering Branch-H capture at `phi = 2.0` without changing
any verdict (per the TASK-20260904-937822 RT2-SR-4 analysis).

## Identity block of corrected-design.yaml

- `id: null` (authorizes nothing; the archive substitutes
  `IDEA-20260904-6aed0b`).
- `superseding: IDEA-20260904-06c396`; `status: proposed`;
  `revision_of: IDEA-20260903-bd730d` retained.
- `id_note` rewritten to itemize RT2-SR-1..4 and to reserve RT2-SR-5.
- Additive: `idea.correction_pass_provenance` (applied/not-applied fixes,
  method, glyph note, inference) and
  `idea.companion_artifacts.pricing_v2_corrected` + `pricing_v2_note`.

## Fields explicitly not changed

- All realized readings (`h(4) = 17`, `h(8) = 13`, `h(16) = 12`), Garwood CI
  `[9.903, 27.219]`, PIN-T0 and all other pinned identifiers.
- `c_margin = 7.814728`, `c_gate = 11.344867`, all branch thresholds.
- The SR-3 conjunct statement, all verdict rules, arm counts, exposures.
- Quantities not named by RT2-SR-1..2 (in particular the written-order
  residual values `0.028488`, `0.000091`, `0.028648`, `0.052924`) were
  deliberately **not** introduced.
- RT2-SR-5 (the Coordinator's adoption trade on the `0.171940` range-wide
  false-plateau bound): untouched, reserved to the execution-gate decision.

## Out-of-scope observations (no action taken)

1. `RT2-SR-5` untouched / reserved per DEC-20260904-031ed2.
2. The pricing file's
   `amend1_arithmetic_at_the_proposed_exposure.saturation_aware_identity`
   carries an ASCII-normalized AMEND-1(a) quotation (`hits - threads*HIT_LOG_CAP`).
   It is NOT named by RT2-SR-3 (which names only the design file's verbatim
   blocks) and is left unchanged.
3. `preregistration-skeleton.md` Section 0 (TASK-20260904-30f2f7) still quotes
   the RAT-5 carrier paraphrase under its verbatim preamble. Not named by the
   four fixes; flagged for a future fidelity pass.
4. `design-revision.yaml` (TASK-20260904-30f2f7) is not itself a deliverable
   of this task and was not directly corrected; its corrections are carried by
   artifacts A and B.
5. The predecessor `ledger/proposals/IDEA-20260903-bd730d.yaml` is already
   fully ASCII-normalized (zero non-ASCII characters); recorded because RT2-SR-3
   named it as the glyph copy source (see deviation above).

## Procedure deviations

1. **Glyph source substitution** (RT2-SR-3): the named copy source
   (`IDEA-20260903-bd730d.yaml`) contains zero non-ASCII characters; glyphs
   were copied from the cited source decision records instead and verified
   character-for-character by script. No content beyond the named glyphs and
   the RAT-5 placement changed as a result.
2. **Additive metadata in both deliverables**: correction-lineage fields
   (`correction_of`, `rt2_corrections_applied_here`, ...), the
   `correction_pass_provenance` block in the design file, the
   `pricing_v2_corrected` companion pointer, and the D-2 power-field split are
   additive disclosures required by the pass; none alters a pre-existing
   quantity.

## Inference provenance

```yaml
requested_policy: research-deep
fallback_used: true
fallback_reason: >-
  The opencode idea-generator role binding is balance-dead in this
  environment; this session was dispatched as a general agent carrying the
  full idea-generator role contract, per the handoff's fallback_allowed: true
  and the DEC-20260903-16bfc2 disclosure rules.
model_verified: false
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
resolved_model_id_note: >-
  Session-reported identifier of the OpenCode model serving this dispatch. No
  adapter probe (python3 -m orchestration.adapter doctor --probe) was executed
  in this session, so this identifier is unverified configuration; recorded
  rather than omitted per AGENTS.md model policy.
degraded_allowed: false
degraded_requirements: []
independent_session: true
```

## Verification appendix

- `corrected-design.yaml`: `yaml.safe_load` OK; 16/16 authoring checks passed
  (unique-marker assertions, glyph identity against DEC sources, RAT-5 folded
  identity, identity-block fields, protected-content checks).
- `pooled-exposure-pricing-v2.json`: `json.loads` OK; 24/24 marker assertions
  and 14/14 content assertions passed; `diff` against the source shows 18
  replaced lines and 25 added lines, nothing else.
