# Red-team notes — TASK-20260803-bc2f41

Verdict: `blocking_objections`, scoped to the planned direct comparison of the
batch-1 full-secret score table with `MATZOV.Nf`. The committed batch-1 table
remains usable as a toy measurement of that narrower object.

## Session-state discrepancy

At the beginning of this session, both
`TASK-20260803-535d15/report.yaml` and the entire assigned
`TASK-20260803-bc2f41` directory returned “File not found.” None of
`rt_analysis.py` through `rt_analysis5.py`, or their `.out` files, was present.
I therefore re-ran none of them and cite no value from them. This is recorded as
`unable_to_check`, not as mathematical evidence.

Later, while this review was running, `TASK-20260803-535d15` appeared with a
`draft: true` working-tree report and two scripts. I read it because the task
prompt required the validator report, but did not treat that mutable,
uncommitted early draft as durable evidence. The final validator report
described by the prompt was still unavailable to this review.

The promised `/tmp/sagevenv` and `/tmp/lattice-estimator` paths were also
absent. No sieve was re-run. I retrieved `estimator/lwe_dual.py` read-only from
the exact pinned commit:

`https://raw.githubusercontent.com/malb/lattice-estimator/3e48ef421ec256afddb3e7d2249a77eab6e9ba12/estimator/lwe_dual.py`

I read `MATZOV.Nf` and its caller but did not invoke `Nf` or perform batch 2's
numerical comparison. The source states:

```text
k_lat = params.n - k_fft - k_enum
...
N = (
    exp(4 * (lsigma_s * pi / params.q) ** 2)
    * exp(k_fft / 3.0 * (params.Xs.stddev * pi / p) ** 2)
    * (k_enum * cls.Hf(params.Xs) + k_fft * log(p) + log(1 / mu))
)
...
red_cost_model.short_vectors(beta, N=N, d=k_lat + m, ...)
...
T_guess = ... * (2 ** (k_enum * H)) *
          (cls.T_fftf(k_fft, p) + cls.T_tablef(N))
```

That is the source basis for OBJ-1.

## Frozen snapshot verification

Commands:

```text
git status --short --branch
git rev-parse --verify HEAD
git branch --show-current
git cat-file -t 8cc51677f7202e9f9b85efdf834860254798abf4
```

Output, verbatim:

```text
## cursor/launch-mlkem-harness-78fd
1d90dfd6507571c8758deeb3fcb5a7dbad628d5c
cursor/launch-mlkem-harness-78fd
commit
```

Command:

```text
git merge-base --is-ancestor 8cc51677f7202e9f9b85efdf834860254798abf4 HEAD
git show -s --format='%H %P %s' 8cc51677f7202e9f9b85efdf834860254798abf4
```

Output, verbatim:

```text
8cc51677f7202e9f9b85efdf834860254798abf4 abc344ac0745f2e115464a5391624da0b96744b1 snapshot: BATCH-d2a728 first sieve measurement (TASK-20260803-aa727e archiving e53ce2)
```

I ran `sha256sum` over all six producer files and
`git diff --exit-code 8cc516... -- <producer-task-dir>`. The diff was empty.
Hash output, verbatim:

```text
99763183a5822f6a6ed5820b484c5f78f777be58aa7f54ed9f60c0fce7e7456b  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/rebuild_transcript.txt
c93d41f8b02085e37e7e62c5b6c7e2ff54c349bc38044d8f29650c4769937c7f  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/measure_scores.py
892991c43a602e370b46dc30d40e8bc6b4840f0f9692890f202b422f41bf3642  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json
82cf8006ef1b0221b276bd30a3c12cbf83ed69648bbf2d6c2b545ee7b1325c39  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/results.json
56848a46cc8544793d2b86419d5c58d0601456b6d7acb5ceb3fc944acc663459  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/report.md
d92002139a3f3ebebbe8c6fd2d7efea9946b67ceae427a04cdabfe3df94e7fd8  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/receipt.json
```

## Raw-score recomputation

All analysis below used system `python3` and NumPy against the committed
`raw_scores.json`. The inline scripts were not saved because the task card
declares exactly two artifacts. The first attempt failed before producing any
number:

```text
Traceback (most recent call last):
  File "<stdin>", line 6, in <module>
KeyError: 'candidate_type'
```

I corrected my own field name (`type`, not `candidate_type`) and re-ran from
the beginning. Output, verbatim:

```text
q N candidate_matrix targets 127 17919 (33, 25) 8
MAIN_lwe_sigma2 correct n 1 mean 0.427375248 min 0.427375248 max 0.427375248 sd_candidates NA
MAIN_lwe_sigma2 uniform n 16 mean 0.003852458 min -0.007076431 max 0.013875303 sd_candidates 0.006056076
MAIN_lwe_sigma2 secretdist n 8 mean 0.290615127 min 0.265095467 max 0.321653623 sd_candidates 0.023960290
MAIN_lwe_sigma2 nearmiss n 8 mean 0.424960348 min 0.423492450 max 0.426723784 sd_candidates 0.001083285
NULL_uniform_target correct n 1 mean 0.003297795 min 0.003297795 max 0.003297795 sd_candidates NA
NULL_uniform_target uniform n 16 mean 0.001121211 min -0.010194445 max 0.010103209 sd_candidates 0.005035300
NULL_uniform_target secretdist n 8 mean 0.008283203 min 0.004940421 max 0.010558442 sd_candidates 0.002156639
NULL_uniform_target nearmiss n 8 mean 0.003365180 min 0.001632489 max 0.004075420 sd_candidates 0.000856888
candidate_difference_rank_mod_q 25
MAIN_lwe_sigma2 recovered_Y_phase_mismatches 0
NULL_uniform_target recovered_Y_phase_mismatches 0
Y_allzero_rows 0
analytic_candidate_expectation_CBD_eta2 0.008567388975
analytic_candidate_expectation_uniform_Zq 0.000000000000
analytic_difference 0.008567388975
naive_vector_iid_SE_difference 0.004499038022
naive_vector_iid_z 1.904271
g_cb_sd 0.602249638741 nonzero_phi 17919
```

The analytic formula used for a CBD(eta=2) candidate was

```text
E_c cos(2*pi*(u-y.c)/q)
 = cos(2*pi*u/q) * product_j cos(pi*y_j/q)^4.
```

The uniform-candidate expectation is exactly zero whenever `y != 0 mod q`.

Further vector-residue and phase-regime output, verbatim:

```text
recovered_centered_Y_norm_mismatches 0
recovered_Y_absmax 10 norm2_y_min_median_max 43 128.0 242
MAIN_lwe_sigma2 analytic_CBD_eta2_candidate_mean 0.288132147 uniform_candidate_mean_exact 0.000000000
NULL_uniform_target analytic_CBD_eta2_candidate_mean 0.008567389 uniform_candidate_mean_exact 0.000000000
DECAY_sigma0.5 analytic_CBD_eta2_candidate_mean 0.656883642 uniform_candidate_mean_exact 0.000000000
DECAY_sigma1 analytic_CBD_eta2_candidate_mean 0.580925244 uniform_candidate_mean_exact 0.000000000
DECAY_sigma4 analytic_CBD_eta2_candidate_mean 0.010865262 uniform_candidate_mean_exact 0.000000000
DECAY_sigma8 analytic_CBD_eta2_candidate_mean -0.002367316 uniform_candidate_mean_exact 0.000000000
DECAY_sigma16 analytic_CBD_eta2_candidate_mean -0.006271879 uniform_candidate_mean_exact 0.000000000
DECAY_uniform_error analytic_CBD_eta2_candidate_mean 0.005350191 uniform_candidate_mean_exact 0.000000000
stored_x_dot_e_centered_min_max_sd_fraction_abs_lt_q4 -63 63 25.632809482 0.766895474
stored_x_dot_e_is_main_correct_phase True
```

Direct target means, ranks and emitted-cosine check, verbatim:

```text
MAIN_lwe_sigma2 correct 0.427375248 wrong_mean 0.180820097 rank 1/33
NULL_uniform_target correct 0.003297795 wrong_mean 0.003472701 rank 18/33
DECAY_sigma0.5 correct 0.949239764 wrong_mean 0.002925867 rank 1/5
DECAY_sigma1 correct 0.841150399 wrong_mean 0.003311377 rank 1/5
DECAY_sigma4 correct 0.018270934 wrong_mean -0.000436008 rank 1/5
DECAY_sigma8 correct 0.004641033 wrong_mean 0.003168578 rank 3/5
DECAY_sigma16 correct -0.003712118 wrong_mean -0.000214976 rank 4/5
DECAY_uniform_error correct 0.008976983 wrong_mean 0.003230569 rank 1/5
rounded_emitted_cosines_checked 1290168 outside_rounding_tolerance 0
```

The `sigma=2` wrong mean is the producer's deliberately mixed 32-candidate
pool. I reproduce it but do not use it as one statistical population.

## Independent audit of the allegedly unauditable membership certificate

From candidate phase differences,

```text
t(c)-t(s) = -y.(c-s) mod q.
```

The 32-by-25 candidate-difference matrix has rank 25, so it recovers every
`y mod q`; centered residues reproduce every emitted `norm2_y`, making the
integer `y` unique. For each vector and each of eight targets,
`x.b = t(s)+y.s mod q`. Stacking those equations under `A^T x=y` gives a
33-by-35 rank-33 system. I enumerated its two free residues and selected
solutions matching emitted `norm2_x`.

Five-row pilot output, verbatim:

```text
rank_A_transpose_mod_q 25
candidate_difference_rank_mod_q 25
combined_A_and_8_target_rank 33 free_dimension 2 free_columns [33, 34]
vector 0 linear_consistent True norm2_x 105 matching_short_residue_solutions 1 first_solution_absmax 3
vector 1 linear_consistent True norm2_x 126 matching_short_residue_solutions 1 first_solution_absmax 5
vector 2 linear_consistent True norm2_x 122 matching_short_residue_solutions 1 first_solution_absmax 5
vector 3 linear_consistent True norm2_x 122 matching_short_residue_solutions 1 first_solution_absmax 4
vector 4 linear_consistent True norm2_x 134 matching_short_residue_solutions 1 first_solution_absmax 5
```

Full 17,919-row output, verbatim:

```text
combined_linear_rank 33 free_dimension 2 consistent_rows 17919
norm_search_vectors 17919 zero_solution_rows 0 multiple_solution_rows 0 unique_solution_rows 17919 search_seconds 3.990
recovered_certificate_membership_residue_mismatches 0
recovered_all_target_candidate_phase_mismatches 0
recovered_X_norm_mismatches 0 X_absmax 10
unwrapped_x_dot_e_min_max_sd -104 102 26.234720875
wrapped_x_dot_e_min_max_sd -63 63 25.632809482
wrap_count_fraction 265 0.014788772
unwrapped_fraction_abs_lt_q4 0.766616441 wrapped_fraction_abs_lt_q4 0.766895474
```

Therefore the direct-vector omission is poor design, but “unauditable in
principle” is not reproduced. Surjectivity of `A^T` ignores the phase and norm
constraints also present in the archive.

## D7 candidate-class controls

Uniformly translating the entire CBD candidate cloud preserves its internal
shape but removes the privileged origin. Seed `2026081301`; output, verbatim:

```text
translation_seed 2026081301 n_translations 4096
untranslated_CBD_population_mean 0.008567388975
translated_mean_sd -0.000037631008 0.004577971474
translated_quantiles_0.025_0.5_0.975 -0.009129335371 -0.000121866519 0.009149978673
untranslated_z_against_translation_distribution 1.879658
fraction_abs_translated_ge_abs_untranslated 0.064453125
```

I also permuted the association between fixed null phase `x.b` and the CBD
characteristic weight. Seed `2026081304`; output, verbatim:

```text
pairing_seed 2026081304 permutations 4096
mean_cos_xb 0.010190259760 mean_CBD_characteristic_weight 0.853672504984
actual_paired_mean 0.008567388975 product_of_means 0.008699144575
permuted_pairing_mean_sd 0.008700036696 0.000157433092
actual_pairing_z -0.842566
```

This is the independent basis for my D7 judgement. The final validator's exact
`+0.008655`, `+0.000026`, and `52 sigma` remain `unable_to_check`; the available
raw data supports the class effect but shows its mechanism is candidate-prior
Fourier mass acting on one fixed population baseline.

## Shared-error dependence and nearby-object control

Using reconstructed `X`, I drew 4,096 fresh rounded-Gaussian error vectors at
sigma 2 (seed `2026081302`) and measured variance of the mean score over all
17,919 rows. This is an exploratory full-secret-score control, not an Nf
comparison. First output, verbatim:

```text
error_resample_seed 2026081302 replicates 4096 sigma 2.0
aggregate_mean_across_error_replicates 0.405356291526
aggregate_sd_shared_error 0.088546436132
aggregate_sd_if_vector_scores_independent 0.004404343235
variance_design_effect_shared_vs_independent 404.184690
nominal_N 17919 independence_equivalent_N 44.333693
archived_single_error_aggregate 0.427375248239
```

I then independently permuted coordinates and signs within every `X` row,
preserving every exact row norm and coefficient multiset but destroying the
lattice/sieve direction relationships. Seeds `2026081302` and `2026081303`;
output, verbatim:

```text
matched_null_norm_mismatches 0
sieve_X aggregate_mean 0.405356291526 sd_shared 0.088546436132 sd_independent 0.004404343235 design_effect 404.184690 equiv_N 44.333693
permuted_signed_X aggregate_mean 0.405503305705 sd_shared 0.088332494672 sd_independent 0.004403589011 design_effect 402.371705 equiv_N 44.533450
error_seed 2026081302 null_seed 2026081303 replicates 4096
```

The match is a controlled null. The large absolute ratio is not identified as
sieve-specific; it is dominated by the shared 35-dimensional error input and
its radial fluctuations. Batch 2 needs an actual-minus-null statistic and
instance/database clusters, not a row-wise z-score.

## Adapter probe

Command:

```text
python3 -m orchestration.adapter doctor --probe
```

Output, verbatim:

```text
OK    configuration loaded (sha256:8b02ddbb61f31bb58bb003238357bb00)
      policies: /workspace/orchestration/model-policies.yaml
      providers: /workspace/orchestration/providers.yaml
      bindings: /workspace/orchestration/model-bindings.yaml
WARN  anthropic: $ANTHROPIC_API_KEY unset (backend unusable)
WARN  fireworks: $FIREWORKS_API_KEY unset (backend unusable)
WARN  fireworks-anthropic: $FIREWORKS_API_KEY unset (backend unusable)
OK    local: no credentials required
WARN  local: model probe failed: network error listing models at http://localhost:8000/v1/models: [Errno 111] Connection refused
WARN  openai: $OPENAI_API_KEY unset (backend unusable)
WARN  openrouter: $OPENROUTER_API_KEY unset (backend unusable)
WARN  zai: $ZAI_API_KEY unset (backend unusable)
WARN  zai: unverified model ids for coordinator-orchestration-code, coordinator-orchestration, research-deep, review-adversarial, executor-implementation, executor-mechanical, review-breakthrough — run with --probe
WARN  zai-anthropic: $ZAI_API_KEY unset (backend unusable)
WARN  zai-anthropic: unverified model ids for coordinator-orchestration-code, coordinator-orchestration, research-deep, review-adversarial, executor-implementation, executor-mechanical, review-breakthrough — run with --probe
```

No resolved model id is claimed.

## Scope

- No ML-KEM break or security proof.
- No FIPS 203 parameter set affected or cleared.
- No crypto-scale validation.
- No status change to any `EV-*` or `KN-*` record.
- Rule 12 remains unmet and unwaived.
- No git write command was run. The Coordinator archive task owns durability.
