# Paired Correlation Test — TASK-20260804-cbf6e2
**BATCH-1be68e / GOAL-MLKEM-004 — Batch 5 of 6**

states_a_finding: false  
compared_against_matzov_nf: false  
rule12_status: UNMET and UNWAIVED

---

## Objective

This task implements a paired discrimination test between two competing hypotheses:

- **H1 (QEMU environmental artifact):** Run-to-run quality fluctuations in the QEMU
  x86_64 environment drive the variance inflation observed in Batch 3
  (ratio_correct = 1.3916, p = 0.001). If so, environmental quality affects _all_
  cosine-score sums equally, and T_N_correct and T_N_null computed from the _same_
  sieve vectors should covary strongly. Prediction: **Pearson r ≈ 1.0**.

- **H2 (genuine sieve-vector correlation):** The variance inflation reflects a true
  structural correlation in the sieve vectors' joint distribution, tied to the correct
  secret. The term `x·e + y·(s − s*)` decorrelates T_N_null from T_N_correct
  run-to-run. Prediction: **Pearson r ≈ 0**.

For each of 50 runs, the script ran one bgj1_sieve realisation and then scored the
_same_ set of sieve vectors against both the correct secret `s` and a wrong secret
`s_wrong`, yielding paired (T_N_correct_i, T_N_null_i) observations.

---

## Run Summary

| Parameter | Value |
|---|---|
| n_runs_requested | 50 |
| n_runs_completed | **50** (all succeeded) |
| instance_seed | 20260803001 |
| fpylll_seed | 20260803005 |
| wrong_secret_seed | 20260804999 |
| siever_seeds_expression | `numpy.random.default_rng(20260804003).integers(0, 2**32, size=50).tolist()` |
| n_coords_different (s_wrong vs s) | 23 out of 25 |
| N_vectors per run (constant) | 17 919 |

---

## Correlation Statistics

| Statistic | Value |
|---|---|
| **Pearson r** | **0.4395** |
| Pearson p-value | 0.00141 |
| Spearman rho | 0.4648 |
| Spearman p-value | 0.000673 |
| OLS regression slope (TN_null ~ TN_correct) | 0.5463 |
| OLS regression intercept | 20.38 |

---

## Variance Statistics

| Statistic | Value |
|---|---|
| Var[T_N_correct] | 9 096.8 |
| Var[T_N_null] | 14 058.6 |
| Var[T_N_diff] (T_N_correct − T_N_null) | 13 216.1 |
| N_vectors_run0 | 17 919 |
| single_score_var_correct (run-0) | 0.32934 |
| single_score_var_null (run-0) | 0.44572 |
| Predicted Var[T_N_diff] (Cov=0 approx) | 13 888.3 |
| var_TN_diff / predicted_var_diff | 0.9516 |

Mean(T_N_correct) = 7549.97  
Mean(T_N_null) = 4144.997

---

## Interpretation (observation only — no finding)

**Pre-registered thresholds:**
- r ≥ 0.8 → consistent with H1 (environmental artifact — run quality covaries both)
- r ≤ 0.3 → consistent with H2 (genuine sieve correlation — decorrelated by wrong secret term)

**Observed:** r = 0.4395 (p = 0.0014)

The observed correlation is statistically significant but **intermediate** — it is neither
≥ 0.8 nor ≤ 0.3. It falls in the range that the pre-registered thresholds do not cleanly
assign to either H1 or H2.

**Variance structure observations:**

- Var[T_N_diff] / predicted_var_diff ≈ 0.9516 — approximately consistent with
  independence of the two score streams given the sieve vectors (a ratio near 1.0
  is expected when Cov[score_c, score_n] ≈ 0 per vector).

- However, Var[T_N_correct] < Var[T_N_null] (9 097 vs 14 059). Under pure H2
  (genuine signal), one expects Var[T_N_correct] > Var[T_N_null] because the correct
  secret produces a structured phase. The observed ordering is the reverse.

- The OLS slope 0.546 < 1.0, consistent with a partial correlation rather than full
  co-movement.

**This is an observation. The Coordinator assesses the implication.**

---

## Rule 12 Status

**Rule 12: UNMET and UNWAIVED**

This task does not claim a breakthrough, closure result, or contradiction of established
evidence records. No independent `review-breakthrough` at `max` effort has been obtained
or is claimed.

---

## Anomalies and Deviations

- **Cross-run covariance not directly measured:** The `predicted_var_diff` uses the
  Cov=0 approximation (N₀ × (Var[score_c] + Var[score_n])). The actual per-vector
  cross-covariance Cov[score_correct_j, score_null_j] was not retained from run-0
  scores arrays. This is noted in `paired_results.json` under `variance_stats.note_predicted_var_diff`.

- **New commits during run:** The repository HEAD advanced from `9a3996af5` to
  `fb39ed9b4` during the ~11-minute Docker execution. The script is self-contained
  and imports no code from the repository; the run is reproducible from the committed
  task directory and the Docker image.

- **No deviations from pre-registered protocol** were observed otherwise. All 50
  siever seeds ran to completion with N=17919 vectors each (constant, as expected for
  this LWE instance).

---

## Artifact Inventory

| File | Description |
|---|---|
| `paired_test.py` | Experiment script |
| `rebuild_transcript.txt` | Full Docker build and run log |
| `paired_results.json` | Per-run T_N_correct / T_N_null + correlation + variance stats |
| `report.md` | This file |
| `receipt.json` | Parameters, seeds, git commit, file hashes |
