# TASK-20260801-068 — DUTY: THE SUPERSESSION DIFF AND THE FOUR-CHANGE CAP

RTB-068, reviewer role served by red-team. Independence is PROCEDURAL and not
model-level: this harness resolves author and reviewer to the same model, so
every number below was RECOMPUTED from the archived arrays and every structural
claim RE-DERIVED from driver source and RE-TESTED BY EXECUTION, never accepted
by reading. This session authored, executed, validated and froze nothing under
review and did not serve TASK-20260801-054.

## 0. Binding verified against Git before anything else

| item | expected | observed | verdict |
|---|---|---|---|
| `reading_rule.yaml` sha256 | `8bcb196f…c979f1d` | `8bcb196fa620503c736da307281325d17bb3dc8b0299407b24b584067c979f1d` | BIT-IDENTICAL, unedited |
| `reading_rule.yaml` vs commit `1026150f` | no diff | `git diff 1026150f HEAD --` empty | UNMODIFIED |
| `specification.yaml` sha256 | `0d6c946f…86d1cda` | matches | UNFAULTED |
| `specification.yaml` vs `ba1567ee` | no diff | empty | UNMODIFIED |
| `lpf001_driver.py` sha256 | `786aeb05…4722d65` | matches | UNMODIFIED |
| `reading_rule_v2.yaml` at `9515f6a1` | — | `b633eaf1837ec876ffb7a52bdc6450baba8b1bb4d253dce3d8f3e6e13a7de328`, identical to worktree | HASH-BOUND |
| `9515f6a1` changed paths | 2 | `reading_rule_v2.yaml` + `snapshot_commit_receipt.json`, 2235 insertions, 0 deletions | SCOPE CLEAN |

Ancestry, all confirmed by `git merge-base --is-ancestor`:
`ba1567ee` → `104d32fa` → `aaf7672c` → `9515f6a1` → `HEAD`, and `1026150f` →
`9515f6a1`. No rewrite, no rebase over a pushed run record.

## 1. Method

I loaded both YAML documents, flattened them to path→scalar maps with
whitespace normalisation, and enumerated (a) paths only in RR-LPF-1, (b) paths
only in RR-LPF-2, (c) paths in both whose value differs. I then ran targeted
equality assertions on every block the handoff names. Nothing below is read off
the file's own `change_register`.

Raw counts: **34 paths removed, 313 paths added, 49 paths changed in value.**
The 313 additions and most of the 34 removals are the four permitted changes,
their audit blocks, and record identity; the analysis is below.

## 2. Field-by-field confirmation that nothing outside the cap moved

Every one of these is a machine equality test on the loaded objects, not a
reading:

| block | result |
|---|---|
| `bands` (both cells, all 7 ids, `lower`/`upper`/`certifying`/`struck`/`band_edge_in_null_sd`) | **IDENTICAL** |
| `null_spread` (both cells, all 7 ids, all 6 fields) — all 28 entries | **IDENTICAL** |
| `identity_binomial_cut` | **IDENTICAL (4)** |
| `identity_binomial_cut_record.cuts_computed_for_all_three_readings` | **IDENTICAL** |
| `band_provenance.per_comparison_false_fire_probability` | **IDENTICAL (0.01990049751243781)** |
| `limb_b_decidability_map.frozen_absolute_band` | **IDENTICAL (`[0.125, 8.0]`)** |
| `limb_b_decidability_map.rows` (all 10 rows, all 6 fields) | **IDENTICAL** |
| `certifying_set_retained` / `_ids_retained` / `_ids_struck` | **IDENTICAL** |
| `branch_structure.precedence` | **IDENTICAL** |
| all six branch `condition` strings | **IDENTICAL** (and identical to `specification.yaml` under whitespace normalisation) |
| all six branch `disposition` strings | **IDENTICAL** (and identical to the specification) |
| branch id ORDER `L-0, L-1, L-5, L-2, L-3, L-4` | **IDENTICAL**, and identical to the specification's own order |
| `forbidden_in_every_branch` — the eight-item list | **BYTE-IDENTICAL, eight items, no ninth** |
| `null_probability_of_reaching_L2.band_leg` (0.800995 / 0.817910 / 0.980100 and every derivation string) | **IDENTICAL** |
| `end_to_end` `point_estimate: 0.818`, `interval: [0.789, 0.980]`, `interval_derivation` | **IDENTICAL** |
| `null_probability_of_the_other_branches` (L_3 ≈0.001, L_4 ≈0.18) | **IDENTICAL** |
| `r_u_leg` (0/200, rule-of-three 0.015, derivation) | **IDENTICAL** |
| `top_rung_movement_table_gamma_0_05` — all 28 values | **IDENTICAL**, and all 28 recomputed from the archive at exact equality |
| both gamma ladders (0.0005 … 0.05) | **IDENTICAL**, and identical to `specification.yaml` `LPF-LADDER-SMOOTH` / `LPF-LADDER-ROUGH` |
| both Bsm ladders (65536/1626/256/84/40 and 1048576/10321/1024/256/102) | **IDENTICAL**, and identical to the driver's `BSM_LADDER` |
| STRIKE-1 and STRIKE-2 as strikes; STRIKE-2 justification | **UNCHANGED** (STRIKE-2 verbatim; STRIKE-1's strike stands, only its justification restated = change (b)) |
| the D9 whole-ladder strike of ROUGH / KS-DICK / bits 20 | **PRESERVED, including its moving γ=0.02 rung** |
| `tail_deep_disposition` parts a/b/c — every value, both verdicts | **IDENTICAL** |
| `certified_ladders` — 28 ladders × 3 fields | **3 field differences, all `moving_rungs`; 25 lists character-identical; 0 status changes** |

### The eight-item `forbidden_in_every_branch` list

Verified **byte-identical** as a list-of-strings equality, eight elements, same
order. The author states a drafted ninth bullet was REMOVED. I cannot observe a
removal that leaves no trace in the frozen artifact, and I say so plainly: what
I can and do verify is the *effect* claimed — the list has eight items, no
ninth, and the two prohibitions this supersession introduces (no deliverable may
say a frozen plant family CANNOT place mass in the deep tail; no per-cell
maximum planted Z may be cited as a bound) live at
`STRIKE-1.what_this_forbids_being_said_RESTATED.newly_forbidden` and D1-v2 part
(iii), i.e. inside change (b), and are absent from this list. **The claim's
verifiable content holds.** The claim about the draft is unverifiable from the
snapshot and is recorded as unverifiable rather than accepted.

### Folded-scalar re-wrapping

Confirmed as pure normalisation: after `re.sub(r'\s+',' ',s)` every block the
file declares copied compares equal, with the enumerated exceptions in §4. No
flow-mapping key order changed.

## 3. The three changed lists, and their independent regeneration

I regenerated all 28 raw flag sets myself from the 210 archived rows, addressing
each row by its own `family` / `gamma_rung` / `field_bits` / `statistic_id`
fields (not by position), and independently re-derived the flag column itself
from `|LPF_movement_shift_in_null_sd| >= 1`.

- 210 rows, **0 disagreements** between the archived flag and `|shift| >= 1`.
- 210 expected addresses, **0 missing, 0 extra, 0 duplicates**.
- **28 of 28 published `raw_flag_sets_all_28` entries reproduce exactly.**
- **28 of 28 `certified_ladders` entries equal (raw set if certified, `[]` if
  STRUCK)** — zero deviations.
- **28 of 28 certified-or-STRUCK statuses equal (`certified` iff the γ=0.05 flag
  is true)** — zero deviations.

The three differences, each row re-read in full and each shift recomputed:

| id | ladder | RR-LPF-1 | RR-LPF-2 | archived shift | flag | direction |
|---|---|---|---|---|---|---|
| DIFF-1 | ROUGH / RATE-u=2 / bits 16 | `[0.005,0.01,0.02,0.05]` | `[0.01,0.02,0.05]` | −0.8821222632527359 | false | **against** the experiment |
| DIFF-2 | ROUGH / KS-DICK / bits 16 | `[0.01,0.02,0.05]` | `[0.02,0.05]` | −0.9379576220999121 | false | **against** |
| DIFF-3 | SMOOTH / RATE-u=3 / bits 20 | `[0.002,…]` | `[0.001,0.002,…]` | +1.5724157930250209 | true | **in favour** |

Running the same audit against RR-LPF-1 reproduces RTB-054-1 exactly: 2
unsupported entries (DIFF-1, DIFF-2) and 2 omitted flag-true rungs (DIFF-3 and
the D9 struck ladder). The count `3` and `25 unchanged` are correct.

## 4. Enumeration of everything beyond the four changes, with classification

Nothing below moves a number, band, spread, edge, cut, branch string,
probability, strike, ruling or certified/STRUCK status. I verified that
mechanically, and I verified whether each altered carried string is
append-only.

**A — record identity (not a change):** `id` RR-LPF-1→RR-LPF-2, `batch_id`,
`frozen_by_task`, `archived_by_task`, `reviewed_by_task`, `authority` (names the
new approval gate), the section ids `STOP-`/`CERT-`/`TAIL-`/`LIMBB-`/`ALT-CLASS-`
`RR052→RR066`, `ATTAIN-RR-LPF-1→-2`, and the file's self-references
("no branch of RR-LPF-**2** reads STAT-TAIL-DEEP"). Unavoidable for a new record.

**B — append-only annotations (not a change):** verified as strict prefix
extensions of the RR-LPF-1 string — `certified_ladders.note`,
`STRIKE-1.measured_basis`, `D2`, `D5`, `stop_condition_check[CERT-LPF-1
exhaustion].result`, `the_zero_margin_stated_plainly`,
`driver_shape_conformance.intended_shape`, plus wholly new sibling annotations
(`copied_from`, `strike_status`, `copied_unchanged`, `preserved_at_this_supersession`,
`reference_note_added_at_this_supersession` ×2,
`labelling_imprecision_carried_not_repaired`, `attestation_renewed…`,
`d5_restated_for_this_file`, `forbidden_list_copied_byte_for_byte`,
`consistency_with_change_a`, `d2_caveat_travels`, `d6_caveat_travels`,
`the_stated_reason_is_wrong_and_is_carried_unrepaired`,
`reviewer_recomputation_carried`, `the_deviation_the_reviewer_bound`).
Every one of these RECORDS a TASK-20260801-054 finding and REPAIRS NOTHING; the
file three times explicitly refuses to patch a frozen figure "because that would
be a fifth change" (RTB-054-4's numbers, RTB-054-5's probabilities, RTB-054-7's
mislabelled margin). That refusal is the correct discipline and I credit it.

**C — routing→ruled status transitions (not a change):** `OPEN-LPF049-A`,
`OPEN-RR052-A/B/C/D` and `d9_handling.status` move from "UNRESOLVED / ROUTED TO
TASK-20260801-054" to "RULED BY TASK-20260801-054 …". I compared each ruling
string against TASK-20260801-054's own `contract_review.yaml` `rulings` list:
**all six are faithful, none is strengthened, none is re-argued.** The
substantive texts under each item (`reading_1_applied_here`,
`reading_2_not_applied`, `question`, `alternative`, `not_applied_because`) are
byte-identical — the diff shows none of those paths as changed. A ruling
arriving is not the freezer changing a ruling. The routed-items section was
restructured (`open_items_routed_to_TASK_20260801_054` →
`items_ruled_at_TASK_20260801_054_and_not_re_opened` +
`open_items_routed_to_TASK_20260801_068`); I checked the mapping item by item and
**all seven originally-routed items are accounted for** (six ruled, ANOM-LPF052-1
carried at `campaign_items_carried_forward_unchanged`). Nothing dropped.

**D — audit and bookkeeping blocks the register declares (not a change):**
`supersedes`, `change_register`, `MECH-MOVE-RR066`, `raw_flag_sets_all_28`,
`differences_from_RR_LPF_1`, `OPEN-RR066-A`, `defects_owed_from_the_plant_z_validation`
(DEF-065-1..5), `campaign_items_carried_forward_unchanged`,
`quantities_not_recomputable_from_the_archive`, `re_opening_forbidden`,
`source_binding` plant-Z additions. All are evidence trail for changes (a) and
(b) or records of items as owed.

**E — THE CLOSEST CALL: V12 and the AP-3 sentence.** RR-LPF-2 adds
`V12_new_at_this_supersession` to `uncertified_after_this_experiment` and
changes `the_ap_3_sentence` from "CARRYING V1 THROUGH V**11**" to "V1 THROUGH
V**12**". This is the one item that is neither one of the four changes nor
covered by the register's own `what_is_not_a_fifth_change` enumeration, which
lists four kinds of addition and does not list this one.

**My ruling: V12 is inside change (a), not a fifth change.** Grounds:

1. Its content is a strict logical consequence of change (a). It states, on the
   uncertified side, exactly the two rungs change (a) removed from the certified
   side — ROUGH/RATE-u=2/γ=0.005/bits16 and ROUGH/KS-DICK/γ=0.01/bits16 — with
   the two shifts I recomputed (−0.882122, −0.937958, both flags false). It
   asserts nothing the regenerated `certified_ladders` table does not imply.
2. It is strictly CONSERVATIVE. It narrows what may be claimed and adds no
   capability. A cap whose purpose is to stop a repair improving its own
   position is not violated by a clause that worsens that position.
3. RTB-054-1's own `why_it_is_blocking` names ALT-CLASS as the reason the defect
   was blocking — "ALT-CLASS-RR052 declares itself binding and TRAVELS with every
   statement citing this experiment". Leaving the certified-ladder table
   corrected while leaving ALT-CLASS uncorrected would leave the repair
   incomplete in precisely the block the blocking defect named.
4. The AP-3 renumber is mechanical and carries no content.

I record two non-blocking precision defects arising from this (§5, DEF-068-A).

**F — one clarifying edit that the declared normalisation does not cover.**
`top_rung_movement_table_gamma_0_05.provenance` changes "the 210-row table in row
order" → "in **zero-based** row order". I checked the indexing myself: the γ=0.05
blocks are at zero-based rows 49–55, 98–104, 154–160, 203–209 — exactly as
stated. So the clarification is CORRECT and RR-LPF-1's bare wording was
ambiguous (wrong under a 1-based reading). It moves no number and names the
identical row set. But `normalisation_declared` says the only normalisation is
soft line re-wrapping, and this is a content edit to a copied string. Recorded
as DEF-068-B, non-blocking.

**G — one silently dropped sentence, and it was WRONG.** RR-LPF-1's
`d9_handling.finding_restated_with_the_measured_sequence` contained "(rows 199
and 206 of 210 in row order)". RR-LPF-2 deletes that parenthetical and replaces
it with a MECH-MOVE-RR066 cross-check. **I recomputed the indices: the ROUGH /
KS-DICK / bits-20 rows at γ=0.02 and γ=0.05 are zero-based rows 201 and 208 (or
202 and 209 one-based). RR-LPF-1's 199/206 is wrong on either base.** This is a
previously unrecorded factual error in RR-LPF-1, and RR-LPF-2 removed it rather
than quoting it verbatim beside a replacement — which is the OPEN-BATCH024-A
mitigation discipline the file follows everywhere else and which this handoff
requires. Recorded as DEF-068-C, non-blocking: the parenthetical is an
addressing descriptor that certifies nothing, no band, cut, strike, branch or
probability reads it, and I independently re-derived the seven-rung shift
sequence it was pointing at and confirmed it exactly. The repair owed is a
record, not an edit.

## 5. Verbatim-quotation discipline (OPEN-BATCH024-A partial mitigation)

| superseded sentence | quoted verbatim beside replacement? |
|---|---|
| `structural_basis_D1` | YES — `structural_basis_D1_SUPERSEDED_VERBATIM`, byte-identical to RR-LPF-1 |
| `what_this_forbids_being_said` | YES — `…_SUPERSEDED_VERBATIM`, byte-identical |
| `V8_new_at_this_freeze` | YES — `V8_SUPERSEDED_VERBATIM_FROM_RR_LPF_1`, byte-identical |
| d9 row-index parenthetical (199/206) | **NO — deleted without quotation. DEF-068-C.** |
| "The reviewer is asked to recompute all three" | dropped; the recomputation has since happened and is recorded. Acceptable. |
| "The status of the third clause is OPEN-RR052-B and is routed" | dropped; the item is now ruled. Acceptable. |

I verified the three `_SUPERSEDED_VERBATIM` blocks are byte-identical to their
RR-LPF-1 originals under whitespace normalisation. They are.

## 6. Duty verdict

**NO FIFTH CHANGE.** Not one number, band edge, `null_spread` entry, branch
condition, branch disposition, precedence, cut, probability, interval, strike,
ladder, retained/struck set, decidability row, `[0.125, 8.0]` band or
OPEN-item ruling moved outside the four declared changes. Three non-blocking
precision defects are recorded (DEF-068-A/B/C).
