# Analysis — EXP-BINSTD-6f3434 Stages 0–1 (TASK-20261003-6dd362)

Review plan: `experiments/EXP-BINSTD-6f3434/review/review-plan.yaml`
(REVIEW-BINSTD-6f3434-20261003). Snapshot tip:
`b2be1ba6184de3e58924d26036b1cb9a8627aa16` (producer/release
TASK-20261003-9f89f3). Approval: DEC-20261003-bc5802. Scope: n=17 /
ℓ∈{3,4} Stages 0–1 only. No re-run. No Bedrock.

## Observation

- Two runs under `runs/`:
  - Stage 0 `RUN-BINSTD-95b5eb`: `status=completed_valid`,
    `outcome=S0-FREEZE-OK`. On-disk
    `stage0/{schedule-api,preregistered-predictions}.json` present.
    Freeze records `band=0.85`, cells `(n,ℓ)∈{(17,3),(17,4)}`,
    `xorsat_pin=xorsat-pin-BINSTD-6f3434-v1`, seed `20261003161102`,
    and `encoder_probe.xorsat_available=false` already at freeze time.
  - Stage 1 `RUN-BINSTD-970fc9`: `status=failed_infrastructure`,
    `outcome=O-IMPEDIMENT`. `stage1/charged-cost-n17.json` has
    `cells=[]`, reason = live XOR-SAT pin not available; S3/S4 encoder
    paths probed under EXP-BINSTD-89d952 implementation paths; meter
    self-test fixture recorded with note that it asserts nothing about
    HEUR-BINSTD-161102-H1.
- `implementation/check.py` re-run this review: both run dirs
  `{"ok": true}` with matching stage/outcome (Stage 1 ok means the
  impediment labeling is schema-valid, not that HEUR was measured).
- `RESULTS.md` matches: coverage 2/2 `output_validated`; Stage 1
  O-IMPEDIMENT; no E-S4-* scientific label; no break / exponent /
  n≥131 / rho claim.
- Amazon Bedrock: NOT SELECTED on manifests and RESULTS.md.

## Comparison

- Blind re-derivation of meter identity on the published fixture
  numbers only (not from `run.py`):
  - ε = 1/40 = 0.025.
  - C_s4 = 1.0149616425991703 / max(0.4, 0.025) ≈ 2.537404…
  - C_chained = 1.1924238854890683 / max(0.275, 0.025) ≈ 4.336087…
  - ratio = C_s4 / C_chained ≈ 0.585183…; band_decision_ok vs 0.85
    holds arithmetically on the fixture.
  - This confirms the meter formula, **not** HEUR-BINSTD-161102-H1
    (PTM-2 / fixture note).
- Contract comparison: hypothesis falsification_criteria and
  distinguishable outcome O-IMPEDIMENT treat missing solver pin as
  infrastructure. No scientific charged-cost cell completed. HEUR
  0.85 band remains untested (PTM-1).

## Inference

- Validity of the Stages 0–1 package is acceptable for a **refine**
  decision: Stage 0 freeze holds; Stage 1 correctly stops as
  O-IMPEDIMENT; check.py agrees; claim boundary holds; meter_selftest
  is not HEUR evidence.
- H-BINSTD-3b1f2d / HEUR-BINSTD-161102-H1 **untested** at the n=17 /
  ℓ∈{3,4} cells — not supported, not weakened, not rejected.
- Preferred official transition: **refine**; H/EXP `approved` →
  `analyzed`; strength **inconclusive**; direction **neutral**; no
  KN-FIND. Exactly one next_action: provision the live XOR-SAT pin
  named in Stage 0 (`xorsat-pin-BINSTD-6f3434-v1`), then `/run` Stage 1
  charged-cost bake-off under the frozen band/cells. Do **not** treat
  this impediment as negative math evidence.

## Limitation

- Decisive Stage 1 metric unmeasured (pin absent).
- Coordinator-direct review (PD-1); same-session authoring (PD-2).
- Toy tier; n=17 / ℓ∈{3,4} only; Stage 2 not authorized.
- Meter self-test is arithmetic-only and must not be cited as HEUR
  evidence.
- No break; no exponent; no n≥131 / rho transfer; no Bedrock.
