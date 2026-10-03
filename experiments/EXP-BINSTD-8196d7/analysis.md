# Analysis: EXP-BINSTD-8196d7 (H-BINSTD-b102b7)

Review plan: `experiments/EXP-BINSTD-8196d7/review/review-plan.yaml`
(`REVIEW-BINSTD-8196d7-20261003`), written before this analysis.
Producer: TASK-20261003-7760d0 (snapshot TASK-20261003-41b37a).
Approval: DEC-20261003-7d1fec. Decision target: **inconclusive**
(package O-INCONCLUSIVE from n17_l4 catalog collapse; n17_l3 in-band
does not alone certify FORALL Stage-1 cells). No re-run. No break;
no exponent; no n≥131 transfer. Amazon Bedrock unused.

## Observation

**Validity (J1).** Two run directories under `runs/`:

| run | stage | outcome | check.py | bedrock |
| --- | --- | --- | --- | --- |
| RUN-BINSTD-79fafe | 0 | O-STAGE0-OK | PASS | NOT_USED |
| RUN-BINSTD-4c02c5 | 1 | O-INCONCLUSIVE | PASS | NOT_USED |

Both have `manifest.yaml`, `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `command.txt`, stdout/stderr, and
`execution-receipt.json`. Status `completed` on both; claims
`break: false`, `exponent_move: false`. Within `maximum_runs: 4`.
Required Stage-0 freeze files and Stage-1 panels/control-table and
`RESULTS.md` present. Independent `check.py` PASS on both run dirs.

**Stage 0 (J2).** Frozen `spearman_band: -0.7`, `catalog_seed:
202610038782`, encoder pin with twin Trace-rank / N_nl meters.
`v-catalog.json` carries ≥12 shapes for each Stage-1 cell (n17_l3,
n17_l4) and Stage-2 candidate cells (not authorized). Stage-0 raw:
`twin_ok: true`, outcome `O-STAGE0-OK`. Probe twins agree on both
Stage-1 cells.

**Stage 1 (J3).** Panels from `stage1/panels.json` (catalog_size=12 each;
`twin_fail: false` both cells):

| cell | ρ (reported) | ρ (blind recompute) | CI95 | distinct_rTr | distinct_Nnl | in_band |
| --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | −0.8783100656536799 | −0.8783100656536799 | [−1.0, −0.5976…] | 3 | 3 | true |
| n17_l4 | nan | nan | [nan, nan] | 1 | 1 | false |

n17_l3 r_Tr ∈ {0,1,2}, N_nl ∈ {15,16,17}; every row twin_ok.
n17_l4: every one of 12 shapes has r_Tr=0 and N_nl=17 (Trace-linear
block empty / constant residual count); twin_ok on every row. Control
table notes shuffled-linear null is Stage 2 (not authorized).

## Comparison

Against pre-registered HEUR-BINSTD-878222-H1 / distinguishable_outcomes:

- Twin agreement: **holds** (no O-ARTIFACT).
- Stage 0 freeze: **holds** (band −0.70; catalog ≥12; pin frozen).
- distinct_rTr≥3 floor: **holds on n17_l3; fails on n17_l4** → package
  label **O-INCONCLUSIVE** by protocol (not O-SUPPORT, not O-FAIL-BAND).
- Band polarity on measurable cell: n17_l3 ρ ≤ −0.70 (**in band**), but
  FORALL Stage-1 cells is not decidable while ℓ=4 collapses.
- Proves-too-much controls: supporting on ℓ=3 alone, or calling nan ρ at
  constant ranks a band fail, are both protocol-false — avoided.
- No break / exponent / n≥131 transfer in producer artifacts.

## Inference

The Stages 0–1 package is **valid** and correctly labelled
**O-INCONCLUSIVE**. Trace-rank predicts residual nonlinear clause count
in-band on the single measurable Stage-1 cell (n=17, ℓ=3), but the
second required cell (n=17, ℓ=4) collapses to constant ranks under the
frozen 12-shape catalog on this XOR-SAT pin, so HEUR-H1 is neither
supported nor falsified at the declared FORALL boundary. Official
decision: **inconclusive**. Hypothesis `approved → analyzed`. Do **not**
support. Do **not** weaken / reject_scoped (collapse is the declared
inconclusive floor, not a band falsifier; unreplicated; empirical_only).
Do **not** re-run EXP-BINSTD-8196d7. Successor: design a catalog/pin
refinement that can produce distinct_rTr≥3 at ℓ=4 on this instrument, or
scope the HEUR to cells where that floor is achievable — still toy /
encoding-structure only; Stage-2 null remains unauthorized under this
card.

## Limitation

- Toy n=17 only under authorized Stages 0–1; no transfer to n≥131.
- ℓ=4 Trace-linear block empty on all 12 frozen shapes — catalog
  expansion alone may still be constant if Trace contributes no linears
  at this (n,ℓ,pin); that is a successor-design question, not evidence
  against HEUR beyond the inconclusive floor.
- Stage-2 shuffled-linear null not run (not authorized).
- First unreplicated observation; no independent validator/red-team
  session this round (PD-1).
- certificate.kind absent / measurement package — no solve certificate.
- Strength inconclusive — insufficient for support or KN-FIND promotion.
