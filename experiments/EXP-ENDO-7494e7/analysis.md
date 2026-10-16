# Analysis: EXP-ENDO-7494e7 / RUN-ENDO-795989

Coordinator review under DEC-20261016-4f3a1a. Evidence record EV-ENDO-7628a0; correction CORR-20261016-ac9fc8. Hypothesis H-ENDO-f58749; idea IDEA-20261016-15a6fc; question RQ-ENDO-476761; goal GOAL-ENDO-001. Snapshot TASK-20261016-d4363d at `7f631b5a0`. Independent validation TASK-20261016-35d324 (`experiments/EXP-ENDO-7494e7/validation/TASK-20261016-35d324.md`, run A, verdict passed). Ledger archive TASK-20261016-5c0f78.

All costs are modelled M_eq = M + S counts (curvesweep, S = 1 M). No timing, no ECDLP, rho or exponent statement.

## Validity (checked before interpretation)

| check | result | source |
|:--|:--|:--|
| expected run count | 1 expected, 1 present (RUN-ENDO-795989) | spec `maximum_runs: 1`; manifest |
| manifest | `validity: valid`; 9 rows, 0 errors; row set equals check.py's nine frozen names; frozen arguments equal the spec | manifest.yaml; validator A1 |
| seeds and inputs | seed 20261016; source rows sha256 `0576225d…` as frozen | manifest; validator A1 |
| raw / summary agreement | rows.jsonl equals `raw["rows"]`; 10 receipt and 2 manifest digests match | validator A1 |
| dirty flag | `repository_dirty: true` from the untracked `harness/endosweep/isobench/`, which no module of this run imports; a clean-tree re-run from `c45d9a596` reproduced all 9 rows (excluding `seconds`) and stdout byte for byte | validator A1 |
| controls | control+ascent and control-/mnt/mnt5/1 pass; 7 of 7 combined routes verified on 8 scalars | validator A2 |
| record defects | one-shot under-charge of 29-32 M_eq per call (CORR-20261016-ac9fc8); environment hashes cover isoglv.py only; no peak-memory record | validator A1, A4 |

The run set is valid and complete. The pricing defect does not invalidate it; it is corrected by record, and the raw records stay immutable.

## Observation

- **O1 Controls.** control+ascent: D_K -3; the combined node is the j = 0 crater over one degree-11 step, unit GLV 1777.8 M_eq; route verified 8/8, degree 11; against E's model persistent +36.43 %, one-shot +32.57 %. control-/mnt/mnt5/1: 0 cheaper-class candidates, combined null, no combined_vs_* figure.
- **O2 Combined route against GLV on E** (raw `combined_vs_glv_on_E`; corrected column from CORR-20261016-ac9fc8, validator A4):

  | curve | D_K | GLV on E | GLV on E' | conversion | persistent | one-shot (recorded) | one-shot (corrected) |
  |:--|--:|--:|--:|--:|--:|--:|--:|
  | GOST 2001 test curve | -915 | 2132.5 | 2005.5 | 48.0 | +5.96 % | +3.71 % | ≤ +2.20 % |
  | mnt/mnt3/1, mnt3/3 | -139 | 1466.5 | 1304.7 | 48.0 | +11.03 % | +7.76 % | ≤ +5.78 % |
  | mnt/mnt5/2, mnt5/3 | -211 | 2131.4 | 1890.5 | 48.0 | +11.30 % | +9.05 % | ≤ +7.55 % |
  | other/Tom-384 | -619 | 3233.8 | 2850.8 | 48.0 | +11.84 % | +10.36 % | ≤ +9.46 % |

  Every combined route is a degree-5 path verified on 8 of 8 scalars.
- **O3 Corollary arm** (`model_change_vs_glv_on_E`), one-shot: -34.05 % (GOST), -25.24 % (mnt3), -26.50 % (mnt5), -30.31 % (Tom-384); persistent -31.80, -21.96, -24.25, -28.82 %. mnt5/1 (control): -42.62 % one-shot.
- **O4 Tail check.** Every `glv_on_E` row equals research/endosweep_curves_20261006/curves.json in element, order, chain cost, GLV M_eq and ratio (GOST 1.4342, mnt3 1.4313, mnt5 1.4636, mnt5/1 1.3984, Tom-384 1.5252).
- **O5 Build attempts.** mnt5/2: two neighbours built 3 elements and verified 0, then the third succeeded; mnt5/3: one failure, then success; mnt3/1 and mnt3/3: two failures each, then success; GOST and Tom-384: the first attempt succeeded. The validator placed every failing neighbour on a descending 5-edge and every success on a horizontal one. This is proved for mnt5: an order of conductor divisible by 5 in Q(√-211) has no element of norm 55. It is observed by exhaustive closed-walk search for mnt3, with level assignment resting on the volcano structure theorem, which is recalled and not retrieved. The run itself records these only as edge observations.
- **O6 Independence.** The six population positives come from four isogeny classes. mnt5/2 and mnt5/3 both route to j(mnt5/1), the negative control, and their combined GLV (1890.5) equals mnt5/1's own GLV on E. mnt3/1 and mnt3/3 both route to j(mnt3/2) (1304.7). All three mnt5 curves share p and #E, as do all three mnt3 curves.

## Comparison (against the frozen contract)

- **Success criterion**: valid run, both controls pass, at least one population curve with a GLV arm has a verified combined route with combined_vs_glv_on_E oneshot_gain > 0 at S = 1 M. Met on the recorded figures (six rows, four classes). Still met under CORR-20261016-ac9fc8: every corrected gain is positive, the largest being Tom-384 at ≤ +9.46 % and the smallest GOST at ≤ +2.20 %.
- **Corollary** (model_change_vs_glv_on_E ≤ 0, predicted near -0.2 to -0.4): holds on all six, -0.252 to -0.341 one-shot.
- **Prediction, persistent combined_vs_glv_on_E in (0, 13 %]**: +5.96 % to +11.84 %, inside.
- **Prediction, one-shot lower than persistent by about 1 to 3 % of glv_M_eq**: recorded 1.48 to 3.27 points; corrected 2.38 (Tom-384), 3.75 (GOST, mnt5) and 5.25 (mnt3) points. Above the band on three of four classes. Non-gating; recorded as a miss.
- **Prediction, GOST the most likely to compose if its cheapest candidate uses 5-edges**: it composed on its first 5-neighbour. "5 | f_pi may make some 5-edges vertical" (mnt3, mnt5, Tom-384): 4 of the 6 rational 5-edges of E descend on each (validator A3).
- **Against the index-calculus baseline and the matched rho**: not applicable; known-scalar k·P cost.

## Inference

- **I1** At the modelled tier, a model change and the chain 2-GLV compose on four isogeny classes: on a horizontal 5-neighbour with an a = -3 model, the 2-GLV is cheaper than the 2-GLV on E by 5.96 % to 11.84 % persistent. With the route charged and the input-format term restored, it is cheaper by at most 2.20 % to 9.46 % one-shot.
- **I2** In every class tested, the neighbours that did not carry the chain were descending ones; the successes were horizontal, as the hypothesis's mechanism expects.
- **I3** The deciding one-shot column of the run is under-charged, and its corrected signs rest on a written derivation, not an executed instrument. The positives are four classes, the mnt5 pair routes to the negative-control curve, and GOST's margin is thin. A corrected-pricing re-run should precede support and should seed any timed bench's prediction.
- **I4** Whether any of this survives in wall-clock is unmeasured. EXP-ENDO-33a1ee timed only BADA55-VPR-224, which has no GLV arm. There, 27 % of the modelled one-shot saving survived.

## Limitation

- **L1** Modelled counts in one cost model; only short-Weierstrass cheaper classes; no Edwards or Montgomery targets for the combined arm.
- **L2** One deterministic pass; candidate cap 12; build_limit 3; build_seconds 900; |D_K| ≤ 2·10^6; ell ≤ 13, depth 2, 64 nodes.
- **L3** Corrected one-shot values are a validator derivation pending a re-run (CORR-20261016-ac9fc8). The corrected `combined_vs_E_model_baseline` one-shot figures in that record are Coordinator arithmetic from recorded values.
- **L4** Four classes, not six (O6).
- **L5** The run certifies no f_E for any neighbour; edge classification is the validator's (proved for mnt5, observed for mnt3).
- **L6** The model_change arm is copied from RUN-ENDO-d7cb69 (reviewed in EV-ENDO-fb5823), not recomputed.
- **L7** Heuristics H1-H3 of the idea are not validated. No peak-memory record.
