# Analysis — EXP-BINSTD-8bdf86 ell89r1 Stages 0–1 (TASK-20261003-6e0c8a)

Review plan: `experiments/EXP-BINSTD-8bdf86/review/review-plan-ell89r1.yaml`
(REVIEW-BINSTD-8bdf86-ell89r1-20261003). Snapshot tip:
`c39a3d5e4cc750a837d6339d2ff28f3209c67619` (TASK-20261003-55e2ca).
Producer: TASK-20261003-70af1e. Amendment:
AMD-EXP-BINSTD-8bdf86-20261003-ell89r1. Approval: DEC-20261003-e97263.
Prior weaken: EV-BINSTD-0db227 / DEC-20261003-637059. Scope: n=17 /
ℓ∈{8,9} stub only. No re-run. No Bedrock. No Stage 2 with ℓ∈{3,4}.

## Observation

- Two scientific runs under `runs/` for the ell89r1 amendment:
  - Stage 0 `RUN-BINSTD-f4d6e3`: `status=completed_valid`,
    `outcome=S0-FREEZE-OK`, `certificate.kind=none`. On-disk
    `stage0-ell89r1/{freeze,preregistered-predictions,solver-pin}.json`
    present; freeze records `ells=[8,9]`, `band=1.25`, `n_stage1=17`,
    `target_count=40`, `solver_pin=exhaustive_fb_sum_m3_stdlib_gf2`,
    `authorized_stages=[0,1]`, `seed=8999122336642658`.
  - Stage 1 `RUN-BINSTD-a2a24c`: `status=completed_valid`,
    `outcome=E-TAU-NOT-RICHER`, `certificate.kind=none`.
    `admissible_dimensions=[0,1,8,9,16,17]`; cells:
    - ℓ=8: `ratio=0.5`, `hits_tau=20`, `hits_open=40`,
      `cell_label=E-TAU-NOT-RICHER`, `status=ok`,
      `band_applicable=true`, `both_arms_nonzero=true`,
      `meets_band=false`.
    - ℓ=9: `ratio=1.0`, `hits_tau=40`, `hits_open=40`,
      `cell_label=E-TAU-NOT-RICHER`, `status=ok`,
      `band_applicable=true`, `both_arms_nonzero=true`,
      `meets_band=false`.
- `implementation/check.py` re-run this review: both run dirs
  `{"ok": true}` with matching stage/outcome.
- `RESULTS-ell89r1.md` matches Stage-1 overall outcome and per-cell
  labels; band=1.25; solver pin unchanged.
- Seed independence: ell89 freeze seed `9049049433885666` ≠ ell89r1
  freeze seed `8999122336642658`.
- Prior ell89 package (`stage0-ell89/`, `stage1-ell89/`,
  `RESULTS-ell89.md`, RUN-BINSTD-6f1bcc / RUN-BINSTD-43abd4; ratios
  0.4 and 1.0) remains on disk as immutable prior under
  EV-BINSTD-0db227 / DEC-20261003-637059.
- v1 package (`stage0/`, `stage1/`, `RESULTS.md`, RUN-BINSTD-ebac66 /
  RUN-BINSTD-5cb940) remains immutable structural history under
  DEC-20261003-2425f3.
- No Bedrock. No Magma/Sage/AUXIN. No break / exponent / n≥131 attack
  text in manifests, raw-results, or RESULTS-ell89r1.md.

## Comparison

- Blind re-derivation of admissible φ-invariant dims at n=17 (from the
  quantity statement alone; **not** from `run.py` / stage1-ell89r1 JSON):
  - `ord_17(2)=8` ⇒ `x^17-1=(x+1)·Φ_17` with Φ_17 splitting into
    `(17-1)/8=2` irreducibles of degree 8 over F_2.
  - Irreducible degrees `{1,8,8}`; subset sums
    `{0,1,8,9,16,17}`.
  - Matches `stage1-ell89r1/admissible-phi-dims.json`; ℓ∈{8,9} admissible
    (PTM-1).
- Blind re-derivation of ell89r1 ratios from published hits (not from
  run.py):
  - ℓ=8: R_τ=20/40=0.5, R_open=40/40=1.0, ratio=0.5 < 1.25 →
    E-TAU-NOT-RICHER.
  - ℓ=9: R_τ=40/40=1.0, R_open=40/40=1.0, ratio=1.0 < 1.25 →
    E-TAU-NOT-RICHER.
  - Matches `stage1-ell89r1/yield-matrix.json` and RESULTS-ell89r1.md.
- Replication agreement with prior ell89 (EV-BINSTD-0db227 /
  RUN-BINSTD-43abd4):
  - ell89: ℓ=8 ratio 0.4, ℓ=9 ratio 1.0; both E-TAU-NOT-RICHER.
  - ell89r1: ℓ=8 ratio 0.5, ℓ=9 ratio 1.0; both E-TAU-NOT-RICHER.
  - Direction agrees at both cells; max ratio across both packages is
    1.0 < 1.25; band unmet on every admissible cell measured.
- Contract comparison: hypothesis limb (ii) / HEUR-BINSTD-0fcbe2-H1
  (≥1.25 band on admissible cells) fails at both frozen ℓ∈{8,9} cells
  under the exhaustive pin on two independent seeds. This is scoped
  band failure — not a structural emptiness reading (contrast
  EV-BINSTD-3685c4 for ℓ∈{3,4}).

## Inference

- Validity of the ell89r1 Stages 0–1 run set is acceptable.
- Combined with EV-BINSTD-0db227, two independent Stage-1 packages
  (distinct seeds) both read E-TAU-NOT-RICHER at both admissible cells.
  That meets the replication bar DEC-20261003-637059 NA-1 set for
  considering `reject_scoped` at the toy scope.
- Preferred official transition: **reject_scoped** of
  HEUR-BINSTD-0fcbe2-H1's ≥1.25 yield band at the exact tested scope
  (n=17, ℓ∈{8,9}, exhaustive_fb_sum_m3_stdlib_gf2, band 1.25,
  target_count=40); H `weakened` → `rejected` (scoped); specification-
  ell89r1 `approved` → `analyzed`; strength **replicated**;
  proof_status **empirical_only**; promote **KN-FIND** boundary.
  Do **not** authorize Stage 2 with ℓ∈{3,4}. No n≥131 transfer.
  Exactly one next_action: portfolio successor that does not reopen
  this scoped band without a new pin/contract.

## Limitation

- certificate.kind=none; empirical_only yield rates under an admitted
  toy exhaustive m=3 pin (not XOR-SAT).
- Coordinator-direct review (PD-1); same-session authoring (PD-2).
- Toy tier; n=17 stub only; Stage 2 not in this package and not
  authorized with ℓ∈{3,4}.
- Rejection is scoped to the tested (n,ℓ,pin,band) cells only —
  pin-sensitivity and other admissible dims remain open as separate
  contracts.
- No break; no exponent; no n≥131 transfer; no Bedrock; no AUXIN.
