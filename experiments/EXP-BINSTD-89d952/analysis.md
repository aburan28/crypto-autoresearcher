# Analysis: EXP-BINSTD-89d952 (H-BINSTD-a177b6)

Review plan: `experiments/EXP-BINSTD-89d952/review/review-plan.yaml`
(`REVIEW-BINSTD-89d952-20261001`), written before this analysis.
Producer: TASK-20261001-e15653. Decision target: **refine**
(DO-5 instrument_unavailable — S_4 Boolean degree 6 > frozen Macaulay
D=4; arm_ratio null; Stage 0 gates pass). Never reject_scoped on
infrastructure. No break; no rho claim; no mu-orbit encoding.

## Observation

**Validity (J1).** Four run directories under `runs/`:
- completed_valid: `RUN-BINSTD-260c42` (Stage 0), `RUN-BINSTD-97e1bf`
  (Stage 1 controls enumeration), `RUN-BINSTD-a5d4b9` (Stage 2)
- failed_infrastructure: `RUN-BINSTD-8b78a7` (Stage 1 both-feasibility;
  `termination_reason: instrument_unavailable`)

Every run has `manifest.yaml`, `raw-result.json`, `environment.json`,
`stdout.log`, `command.txt`. Manifests agree with raw-result metrics on
the reported keys checked (Stage 0 gates; Stage 1 degree/instrument flags
and certificate_pass_rate; Stage 2 DO-5). `execution_report` lists the
same three completed + one failed IDs; `invalid: []`. Within
`maximum_runs: 24`. Required stage0 / stage1 (instrument_unavailable +
arm-comparison + controls) / stage2 artifacts present. Amazon Bedrock
not selected. Certificate kinds: Stage 0/feasibility `none`
(`verified: true`); enumeration controls `decomposition`
(`verified: true`, independent curve-summation verifier). Producer
disclosures retained: `data_quality: limited`; degree obstruction
seed-independent so further arm_ratio seeds not run; D=6 probe
non-protocol; no mu encoding; no break/rho claim. Manifests record
`code.dirty: true` at write — disclosed, not treated as invalidation.

**Stage 0 (J2).** Corrected table: all four frozen cells
`match_frozen: true` with `value_recomputed` =
`floor(2**(m*l)/factorial(m))` = 2796202, 178956970, 8947848, 43690.
Inherited /mu column present and labeled `INHERITED_REJECTED` (separate
from RECOMPUTED primary). Cancelation certificate:
`stage0_cancelation_pass: true` with exact identity on all four demo
rows. Stable-V census: `ord_n(2)` recomputed for
`{17,19,23,29,31,37,41}`; n=29 (`ord=28`) and n=37 (`ord=36`) have empty
`mid_dimensions` and
`forbidden_as_frobenius_stable_measurement_cell: true`;
`stage0_census_empty_29_37: true`. Methodological note present. Blind
re-derivation (this review): same four floors; `ord_29(2)=28`,
`ord_37(2)=36`; agree with producer.

**Stage 1 (J3).** Decisive path `instrument_unavailable` (DO-5). Both
arms measure descended S_4 `max_boolean_degree: 6` with identical
degree histograms (deg-6 count 1000); `fits_macaulay_D4: false`;
`macaulay_build_ok: false`. Reason is algebraic (degree > protocol D),
not timeout/OOM. `arm_ratio_ops_median: null`;
`source_mu_alternative_rejected: null`. Enumeration controls:
ordinary `certificate_pass_rate: 1.0` (6108/6108), koblitz `1.0`
(692/692); `no_mu_encoding: true`; forbidden_n_guard n=19.
Curve orders MEASURED: ordinary `#E=523646=2*261823` (l prime);
koblitz `#E=523492=4*130873` (l_hint match). Within-arm V-null
decomposable-target spreads large (ordinary 5718 vs 3012; koblitz 620
vs 1174) — recorded; not interpreted as shape-blindness evidence under
unavailable S_4/W_4. Non-protocol D=6 probe: both arms
`macaulay_build_ok: true`, shape 19×9949 — labeled
`NON_PROTOCOL_D6_PROBE` / not used for arm_ratio.

**Stage 2 (J4).** `DO_outcome_id: DO-5`; `instrument_unavailable: true`;
`macaulay_build_ok_protocol_D4: false`. Analytic Boolean column counts
D4=1941, D6=9949 (blind re-derivation agrees). Further seeds for
arm_ratio not run; reason: degree obstruction seed-independent.
Optimistic 4 GiB D4 memory assumption moot — degree blocked first.
No break / rho claim; no mu encoding.

## Comparison

| prediction (frozen) | observed | status |
| --- | --- | --- |
| Stage 0 table = floor(2^{ml}/m!) | match all 4 cells | pass |
| Cancelation identity | pass | pass |
| n=29,37 empty mid-dim V | empty | pass |
| arm_ratio in [0.8,1.25] OR instrument_unavailable | instrument_unavailable=true; arm_ratio=null | DO-5 (allowed) |
| certificate_pass_rate=1.0 on claimed finds | enum 1.0 both arms; no solver finds | pass (enum) |
| source /mu alternative rejected | null (cannot evaluate without arm_ratio) | deferred |
| No break / rho / mu encoding | flags true | pass |

Distinguished outcome: **DO-5-instrument-unavailable** (hypothesis
`next_decision: checkpoint_defer_H1_no_reject`). Not DO-1 (no arm_ratio),
not DO-2/DO-3 (no measured differential), not DO-4 (Stage 0 passed).

## Inference

Stage 0 HOLD-T corrected accounting and census hold as RECOMPUTED
arithmetic/census observations at the frozen cells and n-list — scoped
support for HEUR-H0 arithmetic only, not for shape-blind cost equality.

Stage 1 cannot measure `arm_ratio` under the frozen S_4/W_4@D=4
instrument because descended Boolean degree is 6 on both arms. That is
infrastructure (instrument_unavailable), **not** negative mathematical
evidence against HEUR-H1 or HEUR-H2 (AGENTS.md rule 3; DO-5). The
non-protocol D=6 probe shows the algebraic degree obstruction is
remediable by raising Macaulay D to ≥6 without claiming any cost result.

Official decision: **refine** — amend protocol to authorize D≥6 (or an
alternate authorized instrument), then re-run Stage 1 arm_ratio under a
versioned `protocol_amendment`. Do not support H1. Do not reject_scoped.
Hypothesis `approved → analyzed`. Experiment `approved → analyzed`.

## Limitation

- Toy tier only (Stage 0 arithmetic; Stage 1 n=19, m=3, l=5).
- Frozen D=4 instrument unreachable; arm_ratio and source-/mu rejection
  untested at this cell.
- D=6 probe is non-protocol — must not be cited as Stage 1 success.
- Within-arm V-null spreads large; interpretation deferred until S_4/W_4
  cost is measurable.
- Coordinator-direct review without independent validator/red-team (PD-1).
- Manifests dirty-at-write; single implementation; unreplicated Stage 0.
- No transfer to n≥131; no break; no rho; no exponent claim.
- Strength inconclusive for H1/H2 — insufficient for support or KN-FIND.
