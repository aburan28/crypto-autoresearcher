# Analysis: EXP-BINSTD-871156 (H-BINSTD-6d5b4a)

Review plan: `experiments/EXP-BINSTD-871156/review/review-plan.yaml`
(`REVIEW-BINSTD-871156-20261003`), written before this analysis.
Producer: TASK-20261003-321876 (snapshot TASK-20261003-84cd29).
Approval: DEC-20261003-a16e9b. Predecessor: EV-BINSTD-56dda7 /
EXP-BINSTD-8196d7. Decision target: **replicate** (package O-SUPPORT
at strength preliminary; first unreplicated positive). No re-run.
No break; no exponent; no n≥131 transfer. Amazon Bedrock unused.

## Observation

**Validity (J1).** Two run directories under `runs/`:

| run | stage | outcome | check.py | bedrock |
| --- | --- | --- | --- | --- |
| RUN-BINSTD-e717e6 | 0 | O-STAGE0-OK | OK | NOT_USED |
| RUN-BINSTD-2fe6ed | 1 | O-SUPPORT | OK | NOT_USED |

Both have `manifest.yaml`, `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `command.txt`, stdout/stderr, and
`execution-receipt.json`. Status `completed` on both; claims
`break: false`, `exponent_move: false`. Within `maximum_runs: 4`.
Required Stage-0 freeze files and Stage-1 panels/control-table and
`RESULTS.md` present. Independent `check.py` OK on both run dirs.
Catalog seed `202610038196` ≠ forbidden v1 `202610038782` — not a
re-run of EXP-BINSTD-8196d7.

**Stage 0 (J2).** Frozen `spearman_band: -0.7`, `catalog_seed:
202610038196`, admission gates `distinct_rTr_min: 3` /
`distinct_Nnl_min: 2`, encoder pin with twin Trace-rank / N_nl meters.
Stage-1 panel catalogs: n17_l3 size 28, n17_l4 size 33 (both ≥24).
Stage-0 raw: `twin_ok: true`, outcome `O-STAGE0-OK`.

**Stage 1 (J3).** Panels from `stage1/panels.json` (`twin_fail: false`
both cells):

| cell | ρ (reported) | ρ (blind recompute) | CI95 | distinct_rTr | distinct_Nnl | floors_met | in_band |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n17_l3 | −0.9369373625903697 | −0.9369373625903697 | [−1.0, −0.826…] | 3 | 3 | true | true |
| n17_l4 | −0.9999999999999999 | −0.9999999999999999 | [−1.0, −1.0…] | 3 | 3 | true | true |

Every measured row has twin_ok (r_Tr_a=r_Tr_b, N_nl_a=N_nl_b). Control
table notes shuffled-linear null is Stage 2 (not authorized). Package
label in RESULTS.md / Stage-1 raw: **O-SUPPORT**.

## Comparison

Against pre-registered HEUR-BINSTD-878222-H1 / distinguishable_outcomes
and successor floors after EV-BINSTD-56dda7:

- Twin agreement: **holds** (no O-ARTIFACT).
- Stage 0 freeze: **holds** (band −0.70; catalog ≥24; new seed ≠ v1).
- Admission floors: **hold on both Stage-1 cells** (repairs parent
  EV-BINSTD-56dda7 ℓ=4 constant-rank collapse under this new catalog).
- Band polarity FORALL Stage-1 cells: both ρ ≤ −0.70 → package
  **O-SUPPORT** by protocol.
- Blind Spearman/distinctness recompute: **identical** to producer panels.
- Proves-too-much controls: support/KN-FIND on unreplicated first package,
  n≥131 transfer, and rewriting parent EV-BINSTD-56dda7 are all refused.
- No break / exponent / n≥131 transfer in producer artifacts.

## Inference

The Stages 0–1 package is **valid** and correctly labelled **O-SUPPORT**
at the declared toy Stage-1 boundary under the rank-diverse catalog:
admission floors are met and Spearman(r_Tr, N_nl) is in-band on both
(17,3) and (17,4). That is a scoped encoding-structure observation only.
Because this is the **first unreplicated** positive package
(coordinator-direct review; no independent validator/red-team), the
official decision is **replicate**, not support. Evidence strength
**preliminary**. Hypothesis `approved → analyzed`. Do **not** promote
KN-FIND. Do **not** re-run EXP-BINSTD-871156. Parent EV-BINSTD-56dda7
remains O-INCONCLUSIVE under its own v1 catalog and is not rewritten.
Next: independent replication (new EXP / independent meter reimplementation
/ second diversity seed under a frozen contract), then consider expand
(Stage-2 shuffled-linear null) only after replication; support remains
gated on replicated strength.

## Limitation

- Toy n=17 only under authorized Stages 0–1; no transfer to n≥131.
- n17_l4 ρ≈−1.0 rests on only three distinct r_Tr / N_nl values — extreme
  Spearman with small support is an unresolved confound for replication.
- Stage-2 shuffled-linear null not run (not authorized).
- First unreplicated observation; no independent validator/red-team
  session this round (PD-1).
- Measurement package — no solve certificate; certificate_refs empty.
- Strength preliminary — insufficient for support or KN-FIND promotion.
- Shared XOR-SAT pin; a different pin needs a new idea/contract.
