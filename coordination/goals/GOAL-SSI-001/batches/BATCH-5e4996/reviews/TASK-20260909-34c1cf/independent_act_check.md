# Independent ACT Check — TASK-20260909-34c1cf (BATCH-5e4996, GOAL-SSI-001)

Role: **Validator** (independent session). Policy: `review-adversarial`,
reasoning `xhigh`. This is a review record: it asserts only about the
integrity of the enactment ACT package, its controls, and its stated metrics —
nothing about the mathematics of the ECDLP/SSI target.

**Overall verdict: HOLD** (J1–J5 all HOLD).

---

## Capability check (STEP 0)

Full shell surface available (`bash`, `shasum`, `python3`, `git`). No
reduced-surface refusal. All mechanical re-derivations were performed in the
pre-approved scratch directory `/Volumes/SSD990/llm/tmp/opencode/ssi-34c1cf`.

## Write-path discrepancy (recorded, not a deviation)

The launching prompt named a `tasks/TASK-20260909-34c1cf/` path; the dispatch
queue's `write_scope` and `artifact_paths` name
`reviews/TASK-20260909-34c1cf/`. The task_card says the queue handoff governs,
and the campaign convention (cf. predecessor `BATCH-60d6b9
reviews/TASK-20260906-ba0284/`) is `reviews/`. I wrote to the queue
`write_scope`. Recorded as a discrepancy, not a deviation.

## Digest re-verification

All **10** snapshot paths (9 producer artifacts + snapshot receipt) match the
`dispatch_queue.json` `path_sha256`. Snapshot commit
`7c24aaeff9e0e0298604b74947c7235450b43dd7` is reachable. Frozen baseline
hashes (v1 spec `c5cc16f7…`, `cost_model.py` `714e6366…`) match the queue.

---

## J1 — Enacted v2 text + P-7 binding + blind re-derivation + OBJ-A → **HOLD**

I computed `structural_diff(v1, enacted)` **before** reading the producer's
`structural_diff_rerun_receipt` results. My result is **6 entries**:

1. `VALUE CHANGED .experiment.version`
2. `REMOVED .experiment.metrics[5].crossover memory log2(w*) per (p, overhead c), analytic`
3. `ADDED .experiment.metrics[5].crossover memory log2(w*) per (p, overhead c)`
4. `ADDED .experiment.model_definition.vow_charging_law`
5. `ADDED .experiment.controls[0].anchor_semantics`
6. `ADDED .experiment.controls[0].anchor_reachability`

This matches the producer's recorded 6-entry set **entry-for-entry**. The
enacted artifact is byte-identical to the O6 splice except a 15-line provenance
header and the version line. **P-7 binding holds.**

**OBJ-A** (null object): `structural_diff(v1, v1)` = 0 (not the declared set);
old `metrics[5]` key present, `vow_charging_law`/`anchor_*` absent, version 1 →
**NON-CONFORMING** as declared. ✓

**AF-2/AF-3 position** (flagged by the receipt): AF-2 and AF-3 are
decision-level resolutions, not contract fields. The enacting decision resolves
them in its own text, so the structural diff correctly shows no trace of them
in the contract. The AF-3 pre-enactment check (all three key paths exist;
status `prospective_and_frozen`; `in_force` absent; the law satisfies all three
clause_2 invariants, re-derived crossover equation matches) confirms the
decision-level resolution is sound. **I uphold the position.**

## J2 — Six NA-2 resolutions + W_1 attack → **HOLD**

All six NA-2 items are resolved in the enacting decision's **own text**, with
**no overreach** (it moves no hypothesis status, enacts the companion
unaltered, lifts no prohibition):

- (i) CF-10 RAW_PATH placement + travels-with clause
- (ii) F-7 scoped to the frozen transcript
- (iii) F-2/F-3 by successor record + RT-2 CF-22
- (iv) RT-6, RT-9(a), RT-12
- (v) RT-4 licensing + W_1 attack
- (vi) AF-1, AF-2, AF-3, AF-4, F-J2-1

**W_1 attack** (target: the adopted RT-4 ruling): **substantive, not
ceremonial.** It names a counterfactual (had the routing decision's RT-4
disposition been a conjunction-plus-relocation instead of a disjunction,
POSITION 2 would follow), cites its anchor (R1/R2 of the ruling and the
disjunction in `DEC-20260905-3b8e94`), and states where it bites (R1 reads
RT-4's scope off its suggested repair rather than its finding sentence; R2
turns on the word "or"). It honestly concedes that on the committed bytes the
disjunction is present, so the ruling stands. It converges with the ruling's
own W_1 weakest point (expected) but is an independent identification of the
load-bearing premise.

## J3 — Companion package: exactly 3 changes + OBJ-B → **HOLD**

My own `diff -u` (frozen → amended) = **3 hunks**, each mapping to a named
change, **no fourth**:

- `change_1_output_path_repair` (CF-10): sites 1a L82-86 + 1b L323
- `change_2_clause_3_serialization`: site 2 L302 — **per-field** (inside
  `results["per_field"][...]`)
- `change_3_clause_4_reachability`: site 3 L303-305

My digests (frozen `714e6366…`, amended `072d293f…`) match the companion and
the queue. `runs/` is untouched (only `RUN-WESOVOW-001`,
`RUN-WESOVOW-201692-001`; no `-002`); frozen tree clean; snapshot commit
reachable with exactly 10 paths. Companion enacted **unaltered**,
**inspection-only** (no run authorization).

**OBJ-B** (null object): a scratch companion missing `change_3` → my checklist
caught it (`change_3` False, others True). ✓

## J4 — Tier compliance + escalation + controls → **HOLD**

Tier compliant (`review-adversarial` / `xhigh` / independent session). **No
escalating limb.** The AF-4 interval ruling is a coordination ruling about the
temporal scope of the contract's requirements, **not** a claim about what the
licence evidences (the plan's element_4 residual). Controls hold.

## J5 — Leaks/citations + re-scan + OBJ-C → **HOLD**

My re-scan over all nine producer artifacts: the governed decimals / `512` /
`2^80` appear **only** in inherited verbatim content (frozen `cost_model.py`
`FIELD_SIZES`/`PAPER_PAIRS`), the companion leak scan (scan commands + verbatim
quotations), the enacted spec (inherited `field_sizes`/C1), or verbatim
prohibition restatements. **No new governed content introduced.** `P=512` /
`w=2^80` appear only in category-10 restatements and policy meta-text.

Both prohibition limbs appear **verbatim** in the draft decision and the
companion package; status is `RETAINED IN FULL, BOTH LIMBS. NOT LIFTED, NOT
NARROWED, NOT WIDENED.` All lift-language tokens are in non-lift contexts.
**No lift performed or implied.**

**OBJ-C** (null object): a planted governed-shape token (`107.5`) → the scan
extracted it; it is named by **none** of the eleven categories → flagged
**UNACCOUNTED-FOR** (the literal STOP-and-report rule would fire). ✓

**Coordinator adjudications (both upheld as SOUND):**
- ACT (63eb35) `INHERITED-FROZEN-CONTENT`: the `512` field-size value and
  `PAPER_PAIRS` decimals are inherited verbatim from the frozen
  `cost_model.py`, not new leaks. The act's leak scan honestly reports the
  `field_sizes_log2p 512` as unaccounted-for (inherited from frozen v1).
- Companion (8b3cce) F-1/F-2/F-3: the same inherited verbatim content from
  `cost_model.py:59-66`, not new leaks.

---

## Procedure deviations

- **PD-1** (recorded discrepancy, not a deviation): prompt `tasks/` path vs
  queue `reviews/` path; wrote to the queue `write_scope`.
- **PD-2** (disclosed read outside nominal read_scope): opened
  `BATCH-2e6130 protocol_amendment.yaml` (the AF-3 pointed-to record) for the
  J1 AF-3 pre-enactment check. A committed coordination record, not frozen tree
  or `inputs/`.

## Validity

**valid.** All five joints HOLD; all three null objects behave as declared; all
10 snapshot digests match. No experiment executed (`maximum_runs = 0` honored;
`cost_model.py` never invoked). Nothing under `inputs/` or the frozen tree was
written.
