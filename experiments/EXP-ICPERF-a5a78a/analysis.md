# Analysis: EXP-ICPERF-a5a78a Stages 0–1 (H-ICPERF-71a809)

Review plan: `experiments/EXP-ICPERF-a5a78a/review/review-plan.yaml`
(`REVIEW-ICPERF-a5a78a-20261003`), written before this analysis.
Producer: TASK-20261003-6bb6ee. Snapshot archive: TASK-20261003-64c8e0.
Decision target: **refine** (Stage 1 O-IMPEDIMENT — WDSat not on PATH;
scientific ratios unread). Never reject_scoped / weaken on infrastructure
(AGENTS.md rule 3; EXP/H O-IMPEDIMENT). No break; no IC-vs-rho; no
exponent; Amazon Bedrock unused.

## Observation

**Validity (J1).** Two run directories under `runs/`:
- completed_valid: `RUN-ICPERF-1dfd2f` (Stage 0) — outcome `S0-FREEZE-OK`;
  execution-receipt `output_validated`; check.stdout
  `{"ok": true, "stage": 0, "outcome": "S0-FREEZE-OK"}`
- failed_infrastructure: `RUN-ICPERF-7d6356` (Stage 1) — outcome
  `O-IMPEDIMENT`; reason `WDSat binary not found on PATH`; check.stdout
  `{"ok": true, "stage": 1, "outcome": "O-IMPEDIMENT"}`

Both runs carry producer `manifest.yaml` / `manifest.json` /
`raw-result.json` / `environment.json` / `command.txt` / logs plus
additive `manifest_v2.yaml` (schema completion only; prior flat
manifest sha256 preserved). Raw-result stage outcomes agree with
RESULTS.md and check.stdout. Certificate kind: `none` (measurement /
impediment; no discrete_log / key_recovery). Amazon Bedrock: NOT
SELECTED on receipts and RESULTS. Plan sha256
`d5c54df567f36abc8cd052dd55c69255d86dafe44bbb02fe5414fba44e9c6130`
matches trial-plan-v1.json binding in receipts. This host still has no
`wdsat` on PATH (`command -v wdsat` empty) — proves-too-much control for
the impediment reason holds.

**Stage 0 (J2).** Frozen artifacts present:
- `stage0/V_E_census.md` + `.json` — cells (17,6)/(19,6)/(21,7)
- `stage0/a79052-membership-e-null.md` + `.json` — membership + E-NULL
- `stage0/preregistered-predictions.json` — ratio bands / baseline c

Raw-result sha256 bindings match on-disk bytes:
- predictions → `preregistered-predictions.json`
  (`c41ef21053120b54484a42aad9145c96446de97f22a35bb9d8ec66486f824070`)
- census → `V_E_census.md`
  (`85e537eb02d9a6cc5469738e81457c0935737c338e7632ac347a63a4d9419d0c`)
- a79052 → `a79052-membership-e-null.md`
  (`e5f0d8c2d32020a831f7813d8fe3e27c7d10be60171e3bd50e0824fb73d201df`)

Census rows (instrument curve A=B=1):

| cell | \|V\| | \|V_E\| | \|V_E\|/\|V\| | \|Δ from 1/2\| |
|------|-------|---------|---------------|----------------|
| (17,6) | 64 | 32 | 0.500000 | 0.000000 |
| (19,6) | 64 | 32 | 0.500000 | 0.000000 |
| (21,7) | 128 | 59 | 0.460938 | 0.039062 |

Blind re-derivation (sizes only, from JSON): `|V|=2^l` holds;
`V_E_over_V` and `abs_delta_from_half` recompute exactly; all three
ratios lie in H1 band [0.4, 0.6] — Stage 0 does **not** fire the H1
falsification condition.

a79052 arm: `holds_for_all_nonzero` is **false** for both `a=0` and
`a=1` on F_{2^{17}}^* (failures sampled; 131071 checked). E-NULL
verdict: **E-NULL-OPEN** (oracle-A source present; no sampling campaign).
Producer JSON field `membership.reading` hardcodes “Identity holds…”
while measured flags are false — disclosed prose/measured disagreement;
md file reports the False flags correctly. Asserts nothing about
leaf-count predictions.

**Stage 1 (J3).** `stage1/panel.json`: `status=O-IMPEDIMENT`,
`wdsat_path=null`, `scientific_ratios_read=false`,
`baseline_c_reproduced=null`. No unconstrained/constrained conflict
ratios, decisions, or wall_s panels were read. Allowed Stage-1 terminal
under the frozen contract and H distinguishable outcome `O-IMPEDIMENT`.

**Scope (J4).** claim_tier remains measurement / toy cells only. No
n≥131, no deployed-curve, no IC-vs-rho, no exponent move, no Bedrock.

## Comparison

| prediction (frozen) | observed | status |
| --- | --- | --- |
| Stage 0 freeze before Stage 1 | predictions + census + a79052 present; Stage 1 after | pass |
| \|V\|=2^l on primary cells | 64/64/128 | pass |
| \|V_E\|/\|V\| in [0.4, 0.6] (H1 band) | 0.50 / 0.50 / 0.4609 | pass (not falsified) |
| a79052 membership / E-NULL recorded | False/False + E-NULL-OPEN | recorded |
| Stage 1 baseline c medians 0.945/0.971/0.974 | unread (no WDSat) | deferred |
| Conflict ratios in [6,8] / [7.5,8.5] | unread | deferred |
| Missing WDSat → O-IMPEDIMENT (not falsifier) | O-IMPEDIMENT | pass (contract) |

Distinguished outcome: **O-IMPEDIMENT**. Not O-GAIN / O-PROP-DOMINATES /
O-UNSOUND / O-NOT-SIDE / O-ARTIFACT (none of those metrics were read).

## Inference

Stage 0 freezes the worksheet that Stage 1 was supposed to score against.
Census balance at the three toy cells is consistent with H1’s band; that
is a scoped unreplicated observation, **not** support of (C)–(E).

Stage 1 did not measure leaf-count ratios because WDSat is absent from
PATH. Under AGENTS.md rule 3 and the EXP/H falsification text, that is
**infrastructure**, not negative mathematical evidence against
H-ICPERF-71a809. Do not weaken, do not reject_scoped, do not invent
ratios.

Official decision: **refine** — install or pin a WDSat binary on PATH
(or amend the instrument binding), preserve the frozen Stage-0 artifacts,
re-run Stage 1 under the same trial plan, then re-review. Hypothesis
status `approved → analyzed`. Evidence strength **inconclusive**. No
KN-FIND promotion.

a79052 membership False-for-both-a and the hardcoded `reading` string
are a Stage-0 instrument/seam finding to carry into a later amendment if
ranked; they do not authorize a math call on (B)–(E) in this package.

## Limitation

- Toy cells only; no cryptographic n; no transfer claim.
- Stage 1 scientific metrics entirely unread (WDSat PATH).
- a79052 membership identity as coded failed for a∈{0,1}; E-NULL-OPEN;
  producer JSON `reading` disagrees with measured flags.
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- Single unreplicated Stages 0–1 package; strength inconclusive.
- Shared GOAL-ICPERF-e6b6a4 head not edited (concurrent-lane hygiene).
- Amazon Bedrock unused; no Magma/Sage/AUXIN success path.
