# Analysis — EXP-BINSTD-591d28 Stages 2–3 (H-BINSTD-5fdceb)

Review plan: `experiments/EXP-BINSTD-591d28/review/review-plan-stages23.yaml`
(`REVIEW-BINSTD-591d28-stages23-20261003`), written before this analysis.
Producer: TASK-20261002-d8df85. Snapshot: TASK-20261003-ccecf4 at tip
`9d2b177ed9f06fd06e641c6f526226bf9f74ed65`. Prior expand: EV-BINSTD-f0a4ab /
DEC-20261003-809d48. Amazon Bedrock: NOT SELECTED.

## Observation

- **RUN-BINSTD-f7ca97** (Stage 2 attempt): `status=invalid_output`,
  `check_returncode=2`. check.stderr reports missing
  `.../wt-run-binstd-591d28-stages23-58c6/.../check.py` (worktree path
  mid-flight). **Infra invalid — not scientific evidence.** Disclosed here;
  science reads from the successful Stage-2/3 runs only.
- **RUN-BINSTD-d4a2b8** (Stage 2): `status=output_validated`,
  `check_returncode=0`, `outcome=O-STAGES-2-PARTIAL`. Wall ≈ 376.2 s;
  peak RSS ≈ 18.4 MB. Sampled e-space P1 fill-in + P3 random-subspace null.
  `amazon_bedrock=NOT SELECTED`.
  - P1 (poly): l=4 est=null (0 genuine; pred=3072); l=5 est=3413.33
    pred=24576; l=6 est=0.0 pred=196608. lift_agreement_stage1=1.0 all.
  - P3: l=4 compare undefined (zero genuine/null); l=5 P3_ge_poly=true
    (est≈6.99e6 ≫ poly); l=6 P3_ge_poly=true (both est 0).
- **RUN-BINSTD-3849a9** (Stage 3): `status=output_validated`,
  `check_returncode=0`, `outcome=O-NEGATIVE`. Wall ≈ 44.8 s; peak RSS ≈
  46.9 MB. `p1_band_hits`: l=5 ratio_to_pred≈0.1389 in_band=false; l=6
  ratio=0.0 in_band=false (≥2 out-of-band). `p4_null_holds=true`
  (Koblitz mean=1.0; ordinary mean≈0.9998). `amazon_bedrock=NOT SELECTED`.
- Stages 0–1 RESULTS.md left immutable (O-STAGES-0-1-COMPLETE).
- Claims: break/exponent_move/deployed_attack all false. No Magma/Sage/
  AUXIN/Bedrock.

## Comparison

- Blind re-derivation of band ratios from Stage-3 raw-result:
  - l=5: 3413.333…/24576 = 0.13888… ∉ [0.25, 4]
  - l=6: 0/196608 = 0.0 ∉ [0.25, 4]
  Matches producer `in_band=false` on both scored cells → O-NEGATIVE rule
  (≥2 of band_hits out of band) fires.
- P3 ≥ poly where defined (l=5,6) — does **not** overturn P1 band failure.
- P4 null holds — Frobenius free-action null consistent; does **not**
  support H1 when P1 is out of band (proves-too-much object).
- Against EV-BINSTD-f0a4ab expand: Stages 2–3 were the first H1 band test;
  they return the falsifying branch at toy scale under sampled e-space.

## Inference

- Valid science package: d4a2b8 + 3849a9. f7ca97 disclosed invalid_output
  (infra) and excluded.
- Direction: **weakens** H-BINSTD-5fdceb clause (C) / H1 at tested RC-1
  toy scale (n=17, m=3, l∈{5,6} scored; sampled e-space).
- Official decision: **weaken** (empirical_only, unreplicated) — next
  action **replicate** Stages 2–3 P1 band under independent seed / denser
  sampling. Do **not** reject_scoped on one unreplicated empirical package.
- Strength: **preliminary**.
- Hypothesis approved→weakened. Experiment Stages 2–3 → analyzed.

## Limitation

- Enumeration mode is **sampled** e-space (`count_is_lower_bound=true`);
  ratios are estimator-based, not exhaustive counts.
- l=4 P1 est undefined (zero genuine) — band scored on l=5 and l=6 only
  in Stage-3 band_hits.
- f7ca97 mid-flight invalid_output is infra noise, not a second scientific
  replicate.
- PD-1: no independent validator/red-team session.
- Toy n=17 only; no transfer of H1 failure to n=131 without a new contract.
- No break / exponent / deployed-curve claim. Bedrock unused.
