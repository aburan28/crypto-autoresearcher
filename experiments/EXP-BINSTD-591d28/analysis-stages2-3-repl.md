# Analysis — EXP-BINSTD-591d28 Stages 2–3 replication (H-BINSTD-5fdceb)

Review plan: `experiments/EXP-BINSTD-591d28/review/review-plan-stages23-repl.yaml`
(`REVIEW-BINSTD-591d28-stages23-repl-20261003`), written before this analysis.
Producer: TASK-20261003-154cfb. Snapshot: TASK-20261003-500456 at tip
`07859e6910e3c0d4ffc682b4674797ea905d92fc`. Prior weaken: EV-BINSTD-2f89cc /
DEC-20261003-ef74c5. Admission: DEC-20261003-d4e5ea /
AMD-EXP-BINSTD-591d28-20261003-stages23-repl. Amazon Bedrock: NOT SELECTED.

## Observation

- **RUN-BINSTD-2b5b2c** (Stage 2 repl): `status=output_validated`,
  `check_returncode=0`, `outcome=O-STAGES-2-PARTIAL`. Wall ≈ 598 s class
  (receipt span); peak RSS ≈ 15.5 MB. `master_seed=2026100391`.
  `sample_e_budget={4:262144, 5:65536, 6:16384}` (4× denser than prior).
  Artifacts under `stage2-repl/`. `amazon_bedrock=NOT SELECTED`.
  - P1 (poly): l=4 est=null (0 genuine; pred=3072; e_hits=22/2621440);
    l=5 est=1706.666… pred=24576; l=6 est=0.0 pred=196608.
    `lift_agreement_stage1=1.0` on all three poly rows.
  - P3: l=4 compare undefined; l=5 P3_ge_poly=true; l=6 P3_ge_poly=true.
- **RUN-BINSTD-453b8d** (Stage 3 repl): `status=output_validated`,
  `check_returncode=0`, `outcome=O-NEGATIVE`. Wall ≈ 50.2 s; peak RSS ≈
  46.7 MB. `p1_band_hits`: l=5 ratio_to_pred≈0.06944 in_band=false; l=6
  ratio=0.0 in_band=false (≥2 out-of-band). `p4_null_holds=true`
  (Koblitz mean=1.0; ordinary mean≈1.00013). Artifacts under `stage3-repl/`.
  `RESULTS-stages2-3-repl.md` outcome `O-NEGATIVE`.
- Prior science package (`stage2/`, `stage3/`, `RESULTS-stages2-3.md`,
  RUN-BINSTD-d4a2b8 / 3849a9 / f7ca97) left immutable.
- Claims: break/exponent_move/deployed_attack all false. No Magma/Sage/
  AUXIN/Bedrock.

## Comparison

- Blind re-derivation of band ratios from Stage-3 repl raw-result
  (sources_allowed only; not stages23.py):
  - l=5: 1706.666…/24576 = 0.06944… ∉ [0.25, 4]
  - l=6: 0/196608 = 0.0 ∉ [0.25, 4]
  Matches producer `in_band=false` on both scored cells → O-NEGATIVE rule
  (≥2 of band_hits out of band) fires.
- Directional agreement with prior EV-BINSTD-2f89cc package:
  - prior l=5 ≈0.1389 → repl ≈0.0694 (still out of band; denser sample
    does not move into [1/4,4])
  - prior l=6 =0.0 → repl =0.0
- Independent seed (2026100391 ≠ 2026092731) + 4× e-budget satisfies
  DEC-20261003-ef74c5 next_action replication gate.
- P3 ≥ poly where defined; P4 null holds — neither rescues H1 when P1
  band fails (proves-too-much objects).
- l=4 remains unscored in both packages (zero genuine) — not part of the
  rejected scored-cell scope.

## Inference

- Valid replication science package: 2b5b2c + 453b8d.
- Together with prior d4a2b8 + 3849a9, the empirical_only O-NEGATIVE at
  scored P1 cells is **replicated**.
- Direction: **contradicts** H-BINSTD-5fdceb clause (C) / H1 at tested
  RC-1 toy scale for scored l∈{5,6} under sampled e-space.
- Official decision: **reject_scoped** — strength **replicated**.
  Scope: clause (C) H1 factor-4 band at n=17, m=3, scored l∈{5,6} only.
  Does **not** reject dimension certificate (A) from EV-BINSTD-f0a4ab.
  Does **not** assert anything about n=131 transfer, deployed curves, or
  exponents.
- Promote KN-FIND for the scoped negative boundary.

## Limitation

- Enumeration mode remains **sampled** e-space (`count_is_lower_bound`);
  ratios are estimator-based, not exhaustive counts — declared
  `empirical_only`.
- l=4 P1 est undefined (zero genuine) under both seeds/budgets.
- PD-1: no independent validator/red-team session for this replication
  review (Coordinator-inline joints); replication across two packages
  carries the adversarial load for reject_scoped eligibility.
- Toy n=17 only; no transfer of H1 rejection to n=131 without a new
  contract.
- No break / exponent / deployed-curve claim. Bedrock unused.
