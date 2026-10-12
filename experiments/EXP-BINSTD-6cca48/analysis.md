# Analysis — EXP-BINSTD-6cca48 Stages 0–1

**Hypothesis:** `H-BINSTD-0f9bf7`  
**Runs:** `RUN-BINSTD-c2d2c4` (Stage 0), `RUN-BINSTD-6dad8a` (Stage 1)  
**Producer tip cited:** `91c26f868f5df480089ac5f5793a257b0ae189f7`  
**Snapshot:** `TASK-20261003-a31872`  
**Approval:** `DEC-20261003-4da874`  
**Review plan:** `experiments/EXP-BINSTD-6cca48/review/review-plan.yaml`  
**Amazon Bedrock:** NOT SELECTED

---

## Observation

- Stage 0 `RUN-BINSTD-c2d2c4`: `execution-receipt.json` status
  `output_validated`; `check.stdout.log` = `PASS`; return codes 0;
  `raw-result.json` outcome **S0-FREEZE-OK**, status `completed_valid`;
  `manifest_v2.yaml` `result.valid: true`; wall ≈0.11 s; Bedrock unused;
  `certificate.kind: none`; claims break/exponent_move/rho_competitive
  all false.
- Stage 0 artifacts frozen under `stage0/`:
  `affordability-table.json` (five cells + derived ratios),
  `preregistered-predictions.json` (`frozen_before_stage1: true`,
  expected `O-ARITH-OK`), `forward-condition-disclaimer.json`
  (`no_rho_claim`, `stages_2_to_5_not_authorized`),
  `dependency-gate.json` (7ab503 H1 not required for Stages 0–1),
  `closed-form-pin.json` (`closed_form_source_sha256` =
  `6545e27f3005bf5b62542d57c36b11e1f77b4f85aefdf562e106c2558fb0737d`).
- Stage 1 `RUN-BINSTD-6dad8a`: receipt `output_validated`; check `PASS`;
  `raw-result.json` outcome **O-ARITH-OK**,
  `leaf_count_table_match: true`, `admissibility_all_ok: true`,
  `ratio_koblitz_m4_to_anchor: 1.7297295654142422`,
  `ratio_null_m4_to_anchor: 63.999992489815654`;
  `RESULTS.md` labels **O-ARITH-OK**; control-table
  `cells_frozen_match_live`, `closed_form_pin_ok`,
  `forward_disclaimer_present`, `no_cdcl` all true.
- Recompute table: every cell `leaves_match: true` and admissibility
  matches expected (anchor n=null admissible; (4,8,37) and (5,6,29)
  admissible).
- Exactly two scientific runs (≤ `maximum_runs: 3`). No Magma/Sage/
  AUXIN/CDCL artifacts under this card. Snapshot
  `TASK-20261003-a31872` binds Stage 0–1 bytes before this review.

## Comparison

- Blind re-derivation this review (from `(m,l,mu[,n])` alone, without
  reading `run.py` / `RESULTS.md` / Stage-1 recompute as authorities):

  | cell | recomputed leaves | frozen | match | admissible |
  |---|---:|---:|---|---|
  | anchor_m3_l8 | 2796203 | 2796203 | yes | true |
  | null_m4_l8_n37 | 178956971 | 178956971 | yes | true |
  | koblitz_m4_l8_n37 | 4836675 | 4836675 | yes | true |
  | null_m5_l6_n29 | 8947849 | 8947849 | yes | true |
  | koblitz_m5_l6_n29 | 308547 | 308547 | yes | true |

- Ratios vs anchor: koblitz/anchor = 1.7297295654142422 (≤ 1.73);
  null/anchor = 63.999992489815654 (≈ 64.0). Agree with Stage-0
  `derived_ratios` and Stage-1 raw-result within relative 1e-9 of
  preregistered predictions.
- Closed-form pin: live `run.py` closed-form block sha256 equals frozen
  pin and Stage-0 raw-result `closed_form_source_sha256`.
- Producer labels S0-FREEZE-OK / O-ARITH-OK agree with independent
  arithmetic; no O-ARITH-FAIL / O-ARTIFACT signal.

## Inference

- The Stages 0–1 package is valid and supports H-BINSTD-0f9bf7’s
  **scoped arithmetic corollary**: the Stage-0-frozen affordability
  table evaluates exactly under independent recomputation, with the
  stated Koblitz vs null ratios and admissibility truths.
- Official decision path: **support** at strength **preliminary**
  (single unreplicated freeze+recompute; Coordinator-direct review
  PD-1; same implementation). Hypothesis `approved`→`supported`;
  experiment `approved`→`analyzed`.
- HEUR-BINSTD-493606-H1 (arithmetic evaluation identity) is
  corroborated at the frozen toy cells as a derivation check; this
  does **not** validate IDEA-20260922-7ab503 H1 at m=4, nor any
  CDCL completion claim.
- No break; no exponent move; no rho competitiveness; no n≥131
  transfer; Stages 2–5 remain unauthorized.
- Knowledge promotion not warranted at preliminary strength.

## Limitation

- Toy / derivation tier only (`n=37`, `n=29` table cells; integer ops).
- Same `implementation/run.py` produced Stage 0 and Stage 1; not an
  independent reimplementation.
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- O-ARITH-OK is not evidence that an m=4 CNF-XOR cell will complete
  or approach Pollard rho; dependency gate freezes that reading.
- Proposal Stages 2–5 (anchor run, m=4/m=5 CDCL) need a later
  authorization decision.
- Strength preliminary — insufficient for KN-FIND promotion under
  the support ∧ (replicated|strong) gate.
