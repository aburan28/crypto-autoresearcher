# Analysis: EXP-BINSTD-6fd454 (H-BINSTD-c16539)

Review plan: `experiments/EXP-BINSTD-6fd454/review/review-plan.yaml`
(`REVIEW-BINSTD-6fd454-20261003`), written before this analysis.
Producer: TASK-20261003-de770b (snapshot TASK-20261003-723522).
Approval: DEC-20261003-efb053. Predecessor: EV-BINSTD-d3a6be /
EXP-BINSTD-871156 / DEC-20261003-963219 (replicate). Decision target:
**inconclusive** (package O-INCONCLUSIVE from n17_l4 distinct_rTr=2
floor; n17_l3 in-band does not alone certify FORALL Stage-1 cells).
No re-run of EXP-BINSTD-871156. No Stage-2 expand. No KN-FIND. No
break; no exponent; no n≥131 transfer. Amazon Bedrock unused.

## Observation

**Validity (J1).** Two run directories under `runs/`:

| run | stage | outcome | check.py | bedrock |
| --- | --- | --- | --- | --- |
| RUN-BINSTD-590471 | 0 | O-STAGE0-OK | OK | NOT_USED |
| RUN-BINSTD-710bab | 1 | O-INCONCLUSIVE | OK | NOT_USED |

Both have `manifest.yaml`, `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `command.txt`, stdout/stderr, and
`execution-receipt.json`. Status `completed` on both; claims
`break: false`, `exponent_move: false`. Within `maximum_runs: 4`.
Required Stage-0 freeze files and Stage-1 panels/control-table and
`RESULTS.md` present. Independent `check.py` OK on both run dirs.
Catalog seed `202610039715` ≠ parent `202610038196` ≠ v1
`202610038782` — not a re-run of EXP-BINSTD-871156.

**Stage 0 (J2).** Frozen `spearman_band: -0.7`, `catalog_seed:
202610039715`, admission gates `distinct_rTr_min: 3` /
`distinct_Nnl_min: 2`, encoder pin with twin Trace-rank / N_nl meters.
Stage-1 panel catalogs: n17_l3 size 28, n17_l4 size 32 (both ≥24).
Stage-0 raw: `twin_ok: true`, outcome `O-STAGE0-OK`. Freeze
prescreen already records n17_l4 `prescreen_distinct_rTr: [0, 1]`
(two values) before Stage 1.

**Stage 1 (J3).** Panels from `stage1/panels.json` (`twin_fail: false`
both cells):

| cell | ρ (reported) | ρ (blind recompute) | CI95 | distinct_rTr | distinct_Nnl | floors_met | in_band |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | −0.9369373625903697 | −0.9369373625903697 | [−1.0, −0.806…] | 3 | 3 | true | true |
| n17_l4 | −1.0 | −1.0 | [−1.0, −1.0…] | 2 | 2 | false | false |

n17_l3 r_Tr ∈ {0,1,2}, N_nl ∈ {15,16,17}; every row twin_ok.
n17_l4 r_Tr ∈ {0,1}, N_nl ∈ {16,17}; no r_Tr=2 shape in the 32-shape
frozen catalog; twin_ok on every row. Control table notes
shuffled-linear null is Stage 2 (not authorized). Package label in
RESULTS.md / Stage-1 raw: **O-INCONCLUSIVE**.

Catalog comparison to parent EXP-BINSTD-871156 (observation only; does
not rewrite EV-BINSTD-d3a6be): n17_l3 bases are identical (28/28) to
the parent ℓ=3 catalog; n17_l4 shares 28 of 32 bases with parent's 33,
and the second seed did not recapture a third r_Tr value.

## Comparison

Against pre-registered HEUR-BINSTD-878222-H1 / H-BINSTD-c16539
distinguishable_outcomes and DEC-20261003-963219 NA-2 replication:

- Twin agreement: **holds** (no O-ARTIFACT).
- Stage 0 freeze: **holds** (band −0.70; catalog ≥24; seed ≠ parent/v1).
- distinct_rTr≥3 floor: **holds on n17_l3; fails on n17_l4** → package
  label **O-INCONCLUSIVE** by protocol (not O-SUPPORT, not O-FAIL-BAND).
- Band polarity on measurable cell: n17_l3 ρ ≤ −0.70 (**in band**), but
  FORALL Stage-1 cells is not decidable while ℓ=4 misses the floor.
- Blind Spearman/distinctness recompute: **identical** to producer panels.
- Proves-too-much controls: supporting on ℓ=3 alone, calling ρ=−1.0 at
  two ranks a band fail, expanding Stage-2, promoting KN-FIND, or
  rewriting parent EV-BINSTD-d3a6be as replicated — all refused.
- No break / exponent / n≥131 transfer in producer artifacts.
- Independent-replication of parent FORALL O-SUPPORT: **not achieved**
  at (17,4) under seed 202610039715.

## Inference

The Stages 0–1 package is **valid** and correctly labelled
**O-INCONCLUSIVE**. Trace-rank predicts residual nonlinear clause count
in-band on the single measurable Stage-1 cell (n=17, ℓ=3), but the
second required cell (n=17, ℓ=4) yields only two distinct r_Tr values
under the frozen 32-shape catalog on this XOR-SAT pin, so HEUR-H1 is
neither supported nor band-falsified at the declared FORALL boundary.
Official decision: **inconclusive**. Hypothesis `approved → analyzed`.
Do **not** support. Do **not** weaken / reject_scoped (floors unmet is
the declared inconclusive floor, not a band falsifier). Do **not**
expand Stage-2. Do **not** KN-FIND. Do **not** re-run
EXP-BINSTD-871156. Parent EV-BINSTD-d3a6be remains unreplicated
O-SUPPORT under seed 202610038196 and is not rewritten. Successor:
design a further catalog/pin that can produce distinct_rTr≥3 at ℓ=4
without re-using the three named seeds, or scope the HEUR to cells
where that floor is achievable — still toy / encoding-structure only.

## Limitation

- Toy n=17 only under authorized Stages 0–1; no transfer to n≥131.
- n17_l3 catalog matched parent bases (seed-insensitive geometric/shift
  family) — not an independent ℓ=3 shape sample.
- ℓ=4 under this seed never produced r_Tr=2 (prescreen already [0,1]);
  parent seed 202610038196 did on a 33-shape catalog — seed/catalog
  dependence, not a band falsifier.
- Stage-2 shuffled-linear null not run (not authorized; not expanded).
- Coordinator-direct review; no independent validator/red-team session
  this round (PD-1).
- certificate.kind none / measurement package — no solve certificate.
- Strength inconclusive — insufficient for support or KN-FIND promotion.
