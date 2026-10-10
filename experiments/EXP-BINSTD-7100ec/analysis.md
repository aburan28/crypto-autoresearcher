# Analysis — EXP-BINSTD-7100ec Stage 0

**Hypothesis:** `H-BINSTD-72f0cc`  
**Run:** `RUN-BINSTD-ce7db2`  
**Producer tip cited:** `86ec7d95c2`  
**Review plan:** `experiments/EXP-BINSTD-7100ec/review/review-plan.yaml`  
**Amazon Bedrock:** NOT SELECTED

---

## Observation

- `execution-receipt.json` status `output_validated`; `check.stdout.log` =
  `PASS`; `returncode` 0; `check_returncode` 0; trial
  `stage0-curveblind-census`.
- `raw-result.json`, `manifest.yaml`, and `RESULTS.md` agree on outcome
  **O-C1-COUNTEREXAMPLE**, `c1_counterexamples: 94`, `c2_pass: true`,
  `c3_pass: true`, claims break/exponent/security_verdict all false,
  Bedrock unused.
- Stage-0 artifacts present: `preregistered-predictions.json` (C1 predicted
  counterexample count 0; C2 targets; C3 sign floors), `c1-census.json` /
  `.md` / inclusion rules, `c2-rho-table.json`, `c3-delta-table.json`,
  `support-restatement-cafcf1.md`, `c07598-section.md`.
- C1 census (archived): `scanned_files` 21192; `candidate_count` 2936;
  `counterexample_count` 94; method string =
  `grep markers + ab_cost heuristic; not a substitute for human audit`;
  every listed hit carries reason
  `heuristic: a/b appears in cost phrasing outside lambda_x`.
- C2: max `|gap - prereg|` = 0.004364… bits (tol 0.05); n=17 fixture
  continuous ≈(226.87, 55.03) vs expected (227, 55), `pass: true`.
- C3: `blind_all_positive_ge_3_6: true`;
  `aware_relation_all_negative_mag_ge_3_1: true`; branch labels present
  (`baseline_inherit`, `relation_dominated_m_fold`, `LA_dominated_m2`
  reported column only).
- Support restatement note recorded; no HB1-2 Weil trigger asserted.
- No Magma/Sage/AUXIN; no Stage 1+; no solve/relation certificate claimed
  (`certificate.kind` absent / none).

## Comparison

- Preregistered C1 counterexample count was **0**; observed heuristic count
  is **94** → producer O-C1-COUNTEREXAMPLE path fires under the frozen
  Stage-0 instrument.
- Blind re-derivation this review: `0.5*log2(163) = 3.67436…` vs prereg
  3.67 (`|err|≈0.00436`); n=17 continuous negation/tau ≈(226.82, 55.01)
  rounds to fixture (227, 55). Matches archived C2 table within tol.
- C3 signs match preregistered floors on the primary blind and
  relation-dominated aware branches for all five FIPS `m`.
- Sample heuristic hits include English-article phrasing
  (`depends on a curve…`), affirmative blindness
  (`reads neither a nor b…`), and coefficient-adjacent vanishing language
  (`depends on (a, b) only through their vanishing`). Instrument disclosure
  already refuses human-audit substitution.

## Inference

- Under the **declared Stage-0 ab_cost heuristic**, C1’s universal
  prediction (zero counterexamples in the freeze corpus) does **not** hold;
  the contracted label is O-C1-COUNTEREXAMPLE. This weakens confidence in
  C1 *as measured by that instrument*, not as a derivation-certified
  rejection of every filed binary IC cost law.
- C2 and C3 arithmetic claims re-verify; they are not weakened by this
  package.
- The HOLD-B five-IC-column consequence is conditioned on C1 holding; under
  O-C1-COUNTEREXAMPLE it does **not** fire. Ten-column fan is retained
  pending named, audited exceptions (hypothesis F-C1 / O-C1-COUNTEREXAMPLE
  meaning).
- Strength is preliminary: single unreplicated producer package;
  Coordinator-direct review (PD-1); proof basis `empirical_only` for the
  C1 adverse reading. Per claims-and-verification, unreplicated
  empirical-only refutation → **weaken** + audit/replication, **not**
  `reject_scoped`.

## Limitation

- C1 counterexamples are heuristic string hits, not verified cost-formula
  dependence on Weierstrass `a`/`b` outside `lambda_x`/`r`.
- Corpus freeze is timestamped; later-filed laws are out of scope by
  hypothesis assumption.
- No independent validator/red-team round (PD-1).
- Composition/indexing claim only: no break, no exponent, no security
  verdict, no transfer of C1 instrument noise into a cryptanalytic
  conclusion.
- Shared `GOAL-ECDLP2M-001.yaml` not edited (concurrent-lane hygiene);
  operative next action lives on the decision record.
