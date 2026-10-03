# Analysis — EXP-BINSTD-8bdf86 Stages 0–1 (TASK-20261003-ea8901)

Review plan: `experiments/EXP-BINSTD-8bdf86/review/review-plan.yaml`
(REVIEW-BINSTD-8bdf86-20261003). Snapshot tip: `d132620d210834a6290169ac6f5676517d841f4d`
(TASK-20261003-83b2f0). Producer: TASK-20261003-56695d. Approval:
DEC-20261003-555f72. Scope: n=17 stub only. No re-run. No Bedrock.

## Observation

- Two scientific runs under `runs/`:
  - Stage 0 `RUN-BINSTD-ebac66`: `status=completed_valid`,
    `outcome=S0-FREEZE-OK`, `certificate.kind=none`, seed
    `0x202610010FCBE2`. On-disk `stage0/{freeze,preregistered-predictions,solver-pin}.json`
    present; raw-result `artifact_sha256` fields recorded.
  - Stage 1 `RUN-BINSTD-5cb940`: `status=completed_valid`,
    `outcome=E-NO-TAU-CLOSED-AT-ELL`, `certificate.kind=none`.
    `admissible_dimensions=[0,1,8,9,16,17]`; both cells ℓ=3 and ℓ=4
    labeled `E-NO-TAU-CLOSED-AT-ELL` with `ratio=null`,
    `status=structural`, `band_applicable=false`.
- `implementation/check.py` re-run this review: both run dirs
  `{"ok": true}` with matching stage/outcome.
- `RESULTS.md` matches Stage-1 overall outcome and per-cell labels;
  band=1.25; solver pin `exhaustive_fb_sum_m3_stdlib_gf2`.
- Stage 0 freeze records ℓ∈{3,4}, n_stage1=17, target_count=40,
  authorized_stages=[0,1], Stage 2 not authorized.
- No Bedrock. No Magma/Sage/AUXIN. No break / exponent / n≥131 attack
  text in manifests, raw-results, or RESULTS.md.
- No yield ratio was invented for a non-admissible cell (SR-STRUCT held).

## Comparison

- Blind re-derivation of admissible φ-invariant dims at n=17 (from the
  quantity statement alone; **not** from `run.py` / stage1 JSON):
  - `ord_17(2)=8` ⇒ `x^17-1=(x+1)·Φ_17` with Φ_17 splitting into
    `(17-1)/8=2` irreducibles of degree 8 over F_2.
  - Irreducible degrees `{1,8,8}`; subset sums
    `{0,1,8,9,16,17}`.
  - Matches `stage1/admissible-phi-dims.json` exactly; ℓ∈{3,4} absent.
- Contract comparison: hypothesis limb (i) (structural emptiness when
  ℓ ∉ admissible) is the observed outcome for both frozen cells; limb
  (ii) (≥1.25 band on admissible cells) was **not applicable** — zero
  admissible cells in the frozen ℓ panel at n=17.
- Domain check (advisory, not a Stage-2 run): the same ℓ∈{3,4} panel is
  also empty at n∈{23,31} under the same cyclotomic gate
  (n=23 → `{0,1,11,12,22,23}`; n=31 → multiples of 5 ± optional 1).
  Authorizing Stage 2 with unchanged ℓ∈{3,4} would reproduce
  E-NO-TAU-CLOSED-AT-ELL at every cell — not a yield measurement.

## Inference

- Validity of the Stages 0–1 run set is acceptable for a **refine**
  decision: schema, Stage-0-before-Stage-1, check.py, claim boundary,
  and honest structural labeling hold.
- H-BINSTD-5a212b **structural limb** is observationally confirmed at
  the n=17 / ℓ∈{3,4} stub: both cells correctly gate as
  E-NO-TAU-CLOSED-AT-ELL.
- HEUR-BINSTD-0fcbe2-H1's ≥1.25 **yield band remains untested** — not
  supported, not falsified. Structural emptiness is scope, not band
  falsification (PTM-2 / contract falsification_criterion).
- Preferred official transition: **refine**; H/EXP `approved` →
  `analyzed`; strength **preliminary**; no KN-FIND; exactly one
  next_action: re-target the frozen ℓ panel onto admissible
  φ-invariant dims (e.g. ℓ∈{8,9} at n=17, or ℓ∈{5,6} at n=31) via
  protocol amendment / successor design before any yield comparison.
  Do **not** authorize Stage 2 with ℓ∈{3,4}.

## Limitation

- Single unreplicated Stages 0–1 package; certificate.kind=none.
- Coordinator-direct review (PD-1); same-session authoring (PD-2).
- Yield arms never executed (structural stop) — no R_τ / R_open.
- n=17 stub only; Stage 2 (n∈{23,31} + Boolean null) not in this package.
- No break; no exponent; no n≥131 transfer; no Bedrock.
