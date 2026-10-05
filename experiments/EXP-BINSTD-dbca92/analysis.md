# Analysis: EXP-BINSTD-dbca92 (H-BINSTD-b334a6)

Review plan: `experiments/EXP-BINSTD-dbca92/review/review-plan.yaml`
(`REVIEW-BINSTD-dbca92-20261003`), written before this analysis.
Producer: TASK-20261003-82801d (design snapshot TASK-20261003-af8678;
run tip `a4be73fa6b` / PR #1714). Approval: DEC-20261003-419f13.
Predecessor: EV-BINSTD-53bc6d / EXP-BINSTD-6fd454 / DEC-20261003-9d938d
(inconclusive). Parent: EV-BINSTD-d3a6be / EXP-BINSTD-871156 /
DEC-20261003-963219 (O-SUPPORT / replicate). Decision target:
**replicate** of EV-BINSTD-d3a6be (FORALL floors_met + in-band under
third catalog seed; 3-point (r_Tr, N_nl) support is non-degenerate).
No Stage-2 (unauthorized / not run). No KN-FIND. No re-run of
EXP-BINSTD-871156. No break; no exponent; no n≥131 transfer. Amazon
Bedrock unused.

## Observation

**Validity (J1).** Two run directories under `runs/`:

| run | stage | outcome | check.py | bedrock |
| --- | --- | --- | --- | --- |
| RUN-BINSTD-e9a229 | 0 | O-STAGE0-OK | OK | NOT_USED |
| RUN-BINSTD-f9b3bb | 1 | O-SUPPORT | OK | NOT_USED |

Both have `manifest.yaml`, `raw-result.json`, `environment.json`,
`command.txt`, stdout, and `check.stdout.log`. Status `completed` on
both; claims `break: false`, `exponent_move: false`. Within
`maximum_runs: 4`. Required Stage-0 freeze files, Stage-1
panels/control-table, and `RESULTS.md` present. Independent `check.py`
OK on both run dirs. Catalog seed `202610034821` ∉ `{202610038196,
202610038782, 202610039715}` — not a re-run of EXP-BINSTD-871156 /
6fd454 / 8196d7.

Producer protocol-deviations (infra, not math): TASK claim refused
because dispatch_queue used `status:ready`; origin/main not merged at
run time due to disk. This review merged `origin/main` into
`cursor/review-binstd-dbca92-stages01-ed0c` (merge-commit `a90e0db9fb`).
Infra ≠ falsification; labeled observation stands after re-verify.

**Stage 0 (J2).** Frozen `spearman_band: -0.7`, `catalog_seed:
202610034821`, admission gates `distinct_rTr_min: 3` /
`distinct_Nnl_min: 2`, encoder pin with twin Trace-rank / N_nl meters.
Stage-1 panel catalogs: n17_l3 size 28, n17_l4 size 33 (both ≥24).
Stage-0 raw: `twin_ok: true`, outcome `O-STAGE0-OK`. Freeze prescreen
already records n17_l3 and n17_l4 `prescreen_distinct_rTr: [0, 1, 2]`
and `prescreen_distinct_Nnl: [15, 16, 17]` — (17,4) third-rank present
before Stage 1 (contrast EV-BINSTD-53bc6d prescreen `[0, 1]`).

**Stage 1 (J3).** Panels from `stage1/panels.json` (`twin_fail: false`
both cells). Spearman recomputed as average-rank Pearson on row
`(r_Tr, N_nl)` vectors; distinctness is set cardinality.

| cell | ρ (reported) | ρ (blind recompute) | CI95 | distinct_rTr | distinct_Nnl | floors_met | in_band |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | −0.9369373625903697 | −0.9369373625903697 | [−1.0, −0.8006…] | 3 | 3 | true | true |
| n17_l4 | −0.9999999999999999 | −0.9999999999999999 | [−1.0, −1.0…] | 3 | 3 | true | true |

n17_l3 unique pairs (4): `(0,17)×15`, `(1,16)×11`, `(0,16)×1`,
`(2,15)×1`. r_Tr ∈ {0,1,2}, N_nl ∈ {15,16,17}. Not 1–1 (r_Tr=0 maps
to {16,17}); ρ is strictly below −0.70, not a collapsed −1.

n17_l4 unique pairs (3): `(0,17)×29`, `(1,16)×3`, `(2,15)×1`. Mapping
is 1–1 and **strictly anti-monotone** (0→17, 1→16, 2→15). Floors are
met at the **minimum** distinct_rTr=3. The CI `[−1,−1]` is cluster
imbalance (29/33 rows at `(0,17)`), not pair degeneracy. Non-majority
rows: `shift_s9/s10/s12` at (1,16); `rand_div_32` at (2,15). Every
row `twin_ok`. Control table: `any_twin_fail: false`; shuffled-linear
null is Stage 2 (not authorized). Package label in RESULTS.md /
Stage-1 raw: **O-SUPPORT**.

## Comparison

Against pre-registered HEUR-BINSTD-878222-H1 / H-BINSTD-b334a6
distinguishable_outcomes, EV-BINSTD-53bc6d NA-2 successor, and parent
EV-BINSTD-d3a6be:

- Twin agreement: **holds** (no O-ARTIFACT).
- Stage 0 freeze: **holds** (band −0.70; catalog ≥24; seed ∉ forbidden
  triple).
- distinct_rTr≥3 / distinct_Nnl≥2 floors: **hold on both Stage-1
  cells**, including (17,4) where EV-BINSTD-53bc6d had distinct_rTr=2.
- Band polarity after floors: both cells ρ ≤ −0.70 (**in band**) →
  package **O-SUPPORT** by protocol.
- Blind Spearman/distinctness recompute: **identical** to producer
  panels.
- 3-point Spearman at (17,4): **non-degenerate** (three distinct 1–1
  anti-monotone pairs). Not the trivial/collapsed Spearman that the
  review-plan prior reserved for **inconclusive**.
- Proves-too-much controls: support/KN-FIND/exponent, reject_scoped,
  Stage-2 expand under this card, and treating infra/disk as math —
  all refused.
- Independent recapture of parent FORALL O-SUPPORT (EV-BINSTD-d3a6be,
  seed 202610038196) under seed 202610034821: **achieved** at
  {(17,3),(17,4)}. EV-BINSTD-53bc6d remains inconclusive on seed
  202610039715 and is not rewritten.
- No break / exponent / n≥131 transfer in producer artifacts.

## Inference

The Stages 0–1 package is **valid** and correctly labelled
**O-SUPPORT**. Third catalog seed 202610034821 recovers
distinct_rTr≥3 at (17,4) (floors at the minimum of 3) and then meets
the frozen Spearman ≤ −0.70 band on both Stage-1 cells. The (17,4)
ρ=−1.0 / CI[−1,−1] reading is a perfect rank correlation on a
**non-degenerate** 3-pair anti-monotone support with heavy majority
mass at (0,17), the same qualitative 3-value pattern as parent
EV-BINSTD-d3a6be — usable as independent-seed replication, not as an
exponent or KN-FIND. Official decision: **replicate** (of
EV-BINSTD-d3a6be). Hypothesis `approved → analyzed`. Strength
**preliminary** (toy n=17; 3-point unbalanced support; seed 6fd454
still inconclusive; coordinator-direct PD-1). Do **not** support. Do
**not** reject_scoped. Do **not** KN-FIND. Do **not** run Stage-2
under this card (unauthorized). Do **not** re-run EXP-BINSTD-871156.
Producer O-SUPPORT remains observation; this Coordinator decision is
the official transition.

## Limitation

- Toy n=17 only under authorized Stages 0–1; no transfer to n≥131.
- n17_l4 floors met at the minimum (3 distinct r_Tr / 3 distinct
  N_nl); 29/33 rows sit at (0,17), so bootstrap CI collapses to
  [−1,−1] even though the three pairs are non-degenerate.
- Seed dependence remains: EXP-BINSTD-6fd454 / EV-BINSTD-53bc6d
  (seed 202610039715) still O-INCONCLUSIVE at (17,4).
- Stage-2 shuffled-linear null and n∈{19,23} panels not run (not
  authorized under DEC-20261003-419f13 / this trial-plan).
- Coordinator-direct review; no independent validator/red-team
  session this round (PD-1). RESULTS.md opened before the review-plan
  file landed (PD-2); J3 quantities recomputed from panels.json.
- certificate.kind none / measurement package — no solve certificate.
- Strength preliminary — insufficient for support or KN-FIND
  promotion.
- No break; no exponent claim; no AUXIN; Bedrock unused.
