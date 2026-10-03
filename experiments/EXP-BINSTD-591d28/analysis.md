# Analysis — EXP-BINSTD-591d28 Stages 0–1

Hypothesis: `H-BINSTD-5fdceb`. Experiment: `EXP-BINSTD-591d28`.
Producer: `TASK-20261003-83db99`. Snapshot: `TASK-20261003-111d25`.
Tip: `3146f2429eeb1cfb10c8a44c72021f0334945128`.
Review plan: `experiments/EXP-BINSTD-591d28/review/review-plan.yaml`
(`REVIEW-BINSTD-591d28-20261003`, written before this analysis).
Amazon Bedrock: NOT SELECTED.

## Observation

- **RUN-BINSTD-c0f26f** (Stage 0): `status=output_validated`,
  `outcome=S0-FREEZE-OK`, `check.py` OK, `returncode=0`,
  `amazon_bedrock=NOT SELECTED`. Wall ≈ 5.2e-4 s; peak RSS ≈ 15.6 MB.
  Frozen: five n=131 balanced cells with dims/excess unknowns; RC-1
  predicted spurious factors 3072 / 24576 / 196608 at l=4/5/6;
  `preregistered-predictions.json` present; Stage-0 `recorded_at`
  2026-10-03T02:50:48Z precedes Stage 1.
- **RUN-BINSTD-35aa8f** (Stage 1): `status=output_validated`,
  `outcome=O-STAGES-0-1-COMPLETE`, `check.py` OK, `returncode=0`,
  `p2_ok=true`, `amazon_bedrock=NOT SELECTED`. Wall ≈ 231.5 s; peak RSS
  ≈ 15.5 MB. Cells l∈{4,5,6}:
  - l=4: mean_genuine=0.0; lift_agreement=1.0; fibre n/a (no genuine e);
    predicted_spurious=3072; `spurious_factor_ratio=null`.
  - l=5: mean_genuine=0.48; lift_agreement=1.0 (4/4);
    mean_ordered_per_unique_e=6.0; predicted=24576; ratio=null.
  - l=6: mean_genuine=1.98; lift_agreement=1.0 (17/17);
    mean_ordered_per_unique_e=5.875; predicted=196608; ratio=null.
- Mode on every cell: `genuine_exact_plus_fibre_diagnostic`. Producer
  note: full e-space/genuine P1 ratio deferred to Boolean e-space
  enumerator (hours-scale at l≥5 per IDEA).
- P2 support census: match=true for l∈{4..9}, including fixture
  [6,11,16] at l=6.
- Claims in both raw results: `break=false`, `exponent_move=false`,
  `deployed_attack=false`.
- Stages 2–3 absent from `trial-plan-v1`; RESULTS.md scopes Stages 0–1
  only under `TASK-20261003-83db99`.
- Run count: 2 ≤ `maximum_runs=4`. No Magma/Sage/AUXIN/Bedrock.

## Comparison

- Blind re-derivation of `dim V^{(k)}=min(k(l-1)+1,n)` at n=17 matches
  producer P2 tables for l∈{4..9}:
  [4,7,10], [5,9,13], [6,11,16], [7,13,17], [8,15,17], [9,17,17].
- Blind re-derivation of `m!·2^{sum dim − ml}` at m=3 yields
  3072 / 24576 / 196608 — exact match to Stage-0 freeze and Stage-1
  predicted columns.
- n=131 cells: e.g. (m,l)=(5,23) → dims [23,45,67,89,111], sum=335 vs
  ml=115, excess=220 — matches formula before field reduction.
- Fibre diagnostic at l=5 equals m!=6 exactly; at l=6 is 5.875 (near
  m!). Consistent with S_m orbit structure on ordered genuine tuples;
  **not** a substitute for the e-space/genuine P1 ratio.
- Subfield baseline (proves-too-much object) remains symbolic: V=F_q
  ⇒ V^{(k)}=V; Stages 0–1 do not claim that slice fails.

## Inference

- Stages 0–1 package is **valid**. Blocking controls for reading later
  P1/P3 hold: P2 exact; lift_agreement=1.0; Stage-0 freeze precedes
  Stage-1 ops.
- Scoped support is for **setup readiness + exact dimension certificate
  (A) at the frozen tables**, not for heuristic H1 (C).
  `spurious_factor_ratio` is null on every cell — H1 band untested.
- Official transition: **expand** to Stages 2–3 under already-approved
  `DEC-20261002-397fcd` via design card `TASK-20261002-d8df85`. Do **not**
  support / weaken / reject_scoped H1 from this package.
- Strength: **preliminary** (unreplicated; Coordinator-direct; PD-1).
- Hypothesis and experiment remain `approved` (H1 / O-* unmeasured).

## Limitation

- Full P1 e-space/genuine ratio deferred; cannot decide
  O-POSITIVE / O-SURPRISE / O-NEGATIVE from Stages 0–1 alone.
- Fibre diagnostic is not the preregistered P1 metric; do not treat
  mean_ordered_per_unique_e ≈ m! as band support.
- Stage 2 (P3 random-subspace null) and Stage 3 (P4 Frobenius / a77711)
  not run; trial-plan-v1 did not admit them.
- No independent validator / red-team session (PD-1).
- Toy scale (n=17 executable; n=131 arithmetic only). No transfer of
  spurious-factor direction to crypto scale without H1 validation.
- No ECDLP break, exponent move, or deployed-attack claim is licensed.

## Procedure deviations

- **PD-1:** Coordinator-direct review without independent
  validator/red-team. Caps strength at preliminary; does not void the
  expand gate for an already-authorized Stages 2–3 protocol.
