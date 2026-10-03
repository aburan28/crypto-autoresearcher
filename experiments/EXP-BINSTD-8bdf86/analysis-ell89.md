# Analysis — EXP-BINSTD-8bdf86 ell89 Stages 0–1 (TASK-20261003-68bcf5)

Review plan: `experiments/EXP-BINSTD-8bdf86/review/review-plan-ell89.yaml`
(REVIEW-BINSTD-8bdf86-ell89-20261003). Snapshot tip:
`8efed7dea288e827a4889aec8b768180b6b55e02` (TASK-20261003-221650).
Producer: TASK-20261003-0a1f1b. Amendment:
AMD-EXP-BINSTD-8bdf86-20261003-ell89. Approval: DEC-20261003-8b3da8.
Prior refine: EV-BINSTD-3685c4 / DEC-20261003-2425f3. Scope: n=17 /
ℓ∈{8,9} stub only. No re-run. No Bedrock.

## Observation

- Two scientific runs under `runs/` for the ell89 amendment:
  - Stage 0 `RUN-BINSTD-6f1bcc`: `status=completed_valid`,
    `outcome=S0-FREEZE-OK`, `certificate.kind=none`. On-disk
    `stage0-ell89/{freeze,preregistered-predictions,solver-pin}.json`
    present; freeze records `ells=[8,9]`, `band=1.25`, `n_stage1=17`,
    `target_count=40`, `solver_pin=exhaustive_fb_sum_m3_stdlib_gf2`,
    `authorized_stages=[0,1]`.
  - Stage 1 `RUN-BINSTD-43abd4`: `status=completed_valid`,
    `outcome=E-TAU-NOT-RICHER`, `certificate.kind=none`.
    `admissible_dimensions=[0,1,8,9,16,17]`; cells:
    - ℓ=8: `ratio=0.4`, `hits_tau=16`, `hits_open=40`,
      `cell_label=E-TAU-NOT-RICHER`, `status=ok`,
      `band_applicable=true`, `both_arms_nonzero=true`,
      `meets_band=false`.
    - ℓ=9: `ratio=1.0`, `hits_tau=40`, `hits_open=40`,
      `cell_label=E-TAU-NOT-RICHER`, `status=ok`,
      `band_applicable=true`, `both_arms_nonzero=true`,
      `meets_band=false`.
- `implementation/check.py` re-run this review: both run dirs
  `{"ok": true}` with matching stage/outcome.
- `RESULTS-ell89.md` matches Stage-1 overall outcome and per-cell
  labels; band=1.25; solver pin unchanged.
- v1 package (`stage0/`, `stage1/`, `RESULTS.md`, RUN-BINSTD-ebac66 /
  RUN-BINSTD-5cb940) remains on disk as immutable prior structural
  history under DEC-20261003-2425f3.
- No Bedrock. No Magma/Sage/AUXIN. No break / exponent / n≥131 attack
  text in manifests, raw-results, or RESULTS-ell89.md.

## Comparison

- Blind re-derivation of admissible φ-invariant dims at n=17 (from the
  quantity statement alone; **not** from `run.py` / stage1-ell89 JSON):
  - `ord_17(2)=8` ⇒ `x^17-1=(x+1)·Φ_17` with Φ_17 splitting into
    `(17-1)/8=2` irreducibles of degree 8 over F_2.
  - Irreducible degrees `{1,8,8}`; subset sums
    `{0,1,8,9,16,17}`.
  - Matches `stage1-ell89/admissible-phi-dims.json`; ℓ∈{8,9} admissible
    (PTM-1).
- Blind re-derivation of ratios from published hits (not from run.py):
  - ℓ=8: R_τ=16/40=0.4, R_open=40/40=1.0, ratio=0.4 < 1.25 →
    E-TAU-NOT-RICHER.
  - ℓ=9: R_τ=40/40=1.0, R_open=40/40=1.0, ratio=1.0 < 1.25 →
    E-TAU-NOT-RICHER.
  - Matches `stage1-ell89/yield-matrix.json` and RESULTS-ell89.md.
- Contract comparison: hypothesis limb (ii) (≥1.25 band on admissible
  cells) fails at both frozen ell89 cells under the exhaustive pin.
  This is scoped band failure of HEUR-BINSTD-0fcbe2-H1 at the tested
  toy cells — not a structural emptiness reading (contrast EV-BINSTD-3685c4).

## Inference

- Validity of the ell89 Stages 0–1 run set is acceptable for a
  **weaken** decision: schema, Stage-0-before-Stage-1, check.py, claim
  boundary, and honest yield labeling hold.
- H-BINSTD-5a212b / HEUR-BINSTD-0fcbe2-H1's ≥1.25 yield band is
  observationally **not met** at n=17 / ℓ∈{8,9} under
  `exhaustive_fb_sum_m3_stdlib_gf2` with target_count=40: max observed
  ratio is 1.0 (ℓ=9); ℓ=8 is 0.4.
- Preferred official transition: **weaken**; H `analyzed` → `weakened`;
  specification-ell89 `approved` → `analyzed`; strength **preliminary**
  (single unreplicated empirical_only package + PD-1/PD-2); proof_status
  **empirical_only**; do **not** `reject_scoped` (PTM-2); no KN-FIND.
  Exactly one next_action: **replicate** Stage-1 yield arms (new seed /
  independent check under the same frozen pin and ℓ panel) before any
  reject_scoped or Stage-2 authorization.

## Limitation

- Single unreplicated ell89 Stages 0–1 package; certificate.kind=none.
- Coordinator-direct review (PD-1); same-session authoring (PD-2).
- Toy tier; n=17 stub only; Stage 2 (n∈{23,31} + Boolean null) not in
  this package.
- Exhaustive m=3 FB-sum pin is an admitted toy pin, not XOR-SAT; pin
  choice may dominate the yield reading.
- No break; no exponent; no n≥131 transfer; no Bedrock.
