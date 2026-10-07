# Analysis: EXP-CERTBIN-1bfef5 Stage 2 (H-CERTBIN-4d3853) — O-E-POLY

Review plan: `experiments/EXP-CERTBIN-1bfef5/review/review-plan-stage2-o-e-poly.yaml`
(`REVIEW-CERTBIN-1bfef5-STAGE2-O-E-POLY-20261003`), written before this
analysis. Producer: TASK-20261003-737cc7. Snapshot: TASK-20261003-820d6d.
Run-branch tip: `644d299cf7`. Stage-2 admit: DEC-20261003-ed98c2 /
AMD-20261003-894083; live RUN reallocation: AMD-20261003-d292c9.
Stage-1 precondition: EV-CERTBIN-f218ae / DEC-20261003-b8f938
O-ARM-A-PASS 288/288 (cited; not re-run). Prior Stage-2 void:
EV-CERTBIN-383c07 / DEC-20261003-c7e6d1 / RUN-CERTBIN-9dcb6d
(immutable). Decision target under recorded prior: **expand**,
**refine**, or **inconclusive** depending on AMD-rescope band clearance.
Composed outcome: **replicate** (first unreplicated admissible
O-E-POLY; clears band; not support). No break; no exponent; no
ECC2K-130; no Bedrock/AUXIN. No re-run this tick. Stages 0–1 not
re-run. Archive-S62 transfer observational only.

## Observation

**Validity (J1).** One new Stage-2 run directory:
`RUN-CERTBIN-a93cf9`. Has `manifest.yaml`, additive `manifest_v2.yaml`,
`raw-result.json`, `environment.json`, `command.txt`,
`execution-receipt.json`, `check.stdout.log` = `PASS`, `stage2-result.json`,
`per-set-summary.json`, `per-set-rows.json`, `RESULTS.md`. Receipt status
`output_validated`; producer status `completed_valid`; outcome
`O-E-POLY`. Within `maximum_runs: 4`. Required Stage-2 artifacts under
`stage2/` present and byte-mirrored in the run directory
(`live==run stage2-result.json`). Amazon Bedrock not used.
`certificate.kind: engine_eval_orbit`. Producer claims: `break: false`,
`exponent_move: false`. Amendment binding: `AMD-20261003-d292c9` /
`stage2_admit_by: DEC-20261003-ed98c2`. Stage-1 precondition cited:
O-ARM-A-PASS 288/288 / EV-CERTBIN-f218ae / DEC-20261003-b8f938.
`RUN-CERTBIN-b76bbc` directory **absent** (infra launch failure; not a
validated run; not overwritten — AMD C-1 / P-4).

**O-E-POLY arithmetic (J2) — blind row re-derivation.**

| quantity | blind recount from `per-set-rows.json` | producer |
| --- | --- | --- |
| V_N U62 W_4 | 28/62 ≈ 0.451612903225806 | 0.451612903225806 |
| V_R U62 W_4 | 21/62 ≈ 0.338709677419355 | 0.338709677419355 |
| V_S_octic1 U62 W_4 | 17/62 ≈ 0.274193548387097 | 0.274193548387097 |
| V_S_octic2 U62 W_4 | 35/62 ≈ 0.564516129032258 | 0.564516129032258 |
| V_S_min | min(octic1, octic2) ≈ 0.2742 | 0.274193548387097 |
| U62 M_4 all sets | 0/62 | 0 |
| soundness_violations | 0 on V_N/V_R/V_S_octic1/V_S_octic2 | 0 |
| S62_refuted_count (obs.) | V_N 24; V_R 25; V_S_octic1 22; V_S_octic2 28 | matches |
| Seed / cell | seed=2026092691; n_targets=144; curve_B=126251; normal_alpha=3 | agrees |

Thresholds: `E_POLY_max=0.5`, `E_SET_min=0.9`. Since V_N ≈ 0.4516 ≤ 0.5
and V_S_min ≈ 0.2742 ≤ 0.5, and soundness holds, producer label
**O-E-POLY** matches H / AMD-894083 C-3–C-4 / AMD-d292c9 C-2.

**Archive-S62 transfer (observational only).** Per-set
`archive_S62_transfer` shows sat_under_current_V ∈ {34..40} and
unsat_under_current_V ∈ {22..28} of 62. Under AMD C-1/C-2 this does
**not** void the instrument and is **not** upgraded to an ECDLP /
exponent / n≥131 claim.

**Prop F path (not headline).** V_S_octic1 and V_S_octic2 each record
one `orbit_cert_verifications` entry with agreement 17/17
(`engine_eval_orbit`). Observational under this card; not the O-E-POLY
headline.

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break,
no exponent move, no Bedrock. Toy RC-1 cell only. Stages 0–1 / arm-a
not re-run this package.

## Comparison

Against H-CERTBIN-4d3853 distinguishable outcomes and Stage-2 AMD
(894083 + d292c9):

- Stage-1 precondition O-ARM-A-PASS 288/288: **holds** (prior EV; cited;
  not reopened; Stages 0–1 not re-run).
- Current-V soundness (sat ∧ (M_4 or W_4) one): **holds** (0 violations
  all sets) → instrument readable.
- Archive-S62 W_4-one / unsat under new V: **observational** (not
  O-ARTIFACT under AMD C-1).
- O-E-POLY: **met** (V_N ≤ 0.5 and V_S_min ≤ 0.5; arm-(a) prior exact).
- O-E-SET: **not met** (rates ≪ 0.90; E-SET falsified at this cell/seed
  under the empirical trichotomy).
- O-MIXED: **not met** (V_S_min ≤ 0.5 clears E-POLY; V_S_octic2 alone
  ≈0.5645 is above 0.5 but contract uses V_S_min).
- O-ARTIFACT: **not met** (soundness holds; no Prop F orbit failure as
  headline stop).
- O-IMPEDIMENT: **not met** for a93cf9 (completed_valid). b76bbc infra
  failure is infrastructure signal only — not negative math evidence and
  not a scientific outcome of this package.
- Prior voided package EV-CERTBIN-383c07: **unchanged**; same numeric
  rates were unread under O-ARTIFACT; this package is the first
  admissible reading under the localized control.

## Inference

The Stage-2 re-admit package is **valid**. The honest official label is
**O-E-POLY**: under AMD-rescoped control, structured W_4 rates on
archive-U62 clear the ≤0.50 band (V_N≈0.4516, V_S_min≈0.2742) with
soundness intact. This is a first unreplicated toy-cell scientific
reading of the Stage-2 rate trichotomy — it supports the empirical
E-POLY arm at RC-1 under the disclosed rate-scope (AMD C-3: when W_4
matches current-V unsat, the rate equals the fraction of archive-U62
remaining unsat), and it falsifies E-SET at this cell/seed. It does
**not** newly prove or reject Propositions B/F (B remains Stage-1
identity-gate EV-CERTBIN-f218ae; F orbits observational). It does
**not** license break / exponent / ECC2K-130 / n≥131 transfer.
Archive-S62 transfer remains observational only.

Decision: **replicate** (first unreplicated admissible O-E-POLY;
strength preliminary; not support). Recorded prior expected
expand/refine/inconclusive by band clearance; band cleared, but the
first-observation rule prefers replicate before support or boundary
expand — prior partially overturned toward the stricter gate.
Hypothesis and experiment `approved → analyzed`. No KN-FIND.

## Limitation

- Toy RC-1 cell only (n=17, m=2, l=9); no transfer to n≥131 / ECC2K-130.
- First unreplicated admissible Stage-2 rate reading; single seed; no
  independent validator/red-team (review-plan PD-1).
- Rate-scope disclosure: W_4 rates track current-V unsat fraction on
  poly-V-relative archive labels (AMD C-3) — honest measurement, not an
  independent oracle-blind ECDLP quantity.
- V_S_octic2 point rate ≈0.5645 lies between thresholds; V_S_min rule
  selects octic1 for the structured comparison.
- Prop F orbit path observational (`engine_eval_orbit`); not headline.
- Strength preliminary — insufficient for support, reject_scoped, or
  KN-FIND promotion.
- Prior Stage 0–1 and voided Stage-2 RUNs/EVs immutable and not rewritten.
- b76bbc infra failure is not mathematical evidence.
