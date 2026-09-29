# TASK-20260803-535d15 validation notes

Verdict: `ADMISSIBLE_WITH_DEFECTS`.

Quantitative-claim counts: 30 `reproduced`, 1 `not_reproduced`, 4
`unable_to_check`. The raw phases and scores are admissible. A later comparison
that pools candidate classes is not.

I read the required contracts and context first: `AGENTS.md`,
`agents/validator.md`, `docs/inventor-protocol.md` sections 3 and 6,
`GOAL-MLKEM-004.yaml`, `KN-TECH-14efa5`, `KN-TECH-797223`,
`KN-OPEN-016`, and the complete task card. I did not read or rely on the
concurrent Red Team task's output.

## 1. Frozen snapshot and artifacts

Command:

```text
git rev-parse HEAD
git merge-base --is-ancestor 8cc51677f7202e9f9b85efdf834860254798abf4 HEAD
git diff --exit-code 8cc51677f7202e9f9b85efdf834860254798abf4 -- \
  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2
```

Output:

```text
f23cd16e84d734308bba52df9d65f23dec585d17
```

Both checks exited 0 with no diff. The producer task is byte-identical to the
Coordinator snapshot and the snapshot is reachable. HEAD moved during
validation because the harness autosaved in-flight artifacts; the producer
directory remained byte-identical across the movement.

The snapshot metadata independently checked as:

```text
commit 8cc51677f7202e9f9b85efdf834860254798abf4
parent abc344ac0745f2e115464a5391624da0b96744b1
```

`sha256sum` on the six producer artifacts:

```text
99763183a5822f6a6ed5820b484c5f78f777be58aa7f54ed9f60c0fce7e7456b  rebuild_transcript.txt
c93d41f8b02085e37e7e62c5b6c7e2ff54c349bc38044d8f29650c4769937c7f  measure_scores.py
892991c43a602e370b46dc30d40e8bc6b4840f0f9692890f202b422f41bf3642  raw_scores.json
82cf8006ef1b0221b276bd30a3c12cbf83ed69648bbf2d6c2b545ee7b1325c39  results.json
56848a46cc8544793d2b86419d5c58d0601456b6d7acb5ceb3fc944acc663459  report.md
d92002139a3f3ebebbe8c6fd2d7efea9946b67ceae427a04cdabfe3df94e7fd8  receipt.json
```

All match `snapshot_receipt.json`.

The producer's dirty-tree boolean is inaccurate. Its transcript preserves:

```text
?? coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/
```

The receipt calls this `dirty_tree: false`. Later exact snapshot hashes mitigate
the content risk, but the boolean should have been true.

## 2. Independent raw-only recomputation

Script: `scripts/recompute_raw.py`

Command:

```text
python3 coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/scripts/recompute_raw.py \
  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json
```

Key output:

```text
all_seed_checks True
array_score_checks {'length_failures': [], 'max_serialized_cosine_error': 0.0,
 'phase_arrays_checked': 96, 'score_arrays_checked': 72,
 'serialized_cosine_mismatches_at_6dp': 0,
 'serialized_score_values_checked': 1290168}
ranks [1, 1, 1, 1, 3, 4, 1]
```

Directly from `raw_scores.json`, not `results.json`:

```text
parameters: m=35 n=25 d=60 q=127 N=17919
candidate counts: correct=1 uniform=16 centered-binomial=8 near-miss=8
secret range: [-2,2]
main error: sd=1.9285185177927089 infnorm=4
norm2_v: min=218 median=315 max=329
```

All seeded reconstructions passed: `A`, `s`, main error and target, all 33
candidates, uniform null, and every decay error and target. Every one of
1,290,168 serialized scores equals `round(cos(2*pi*t/127),6)` exactly. All 96
phase arrays, 72 score arrays, and four per-vector arrays have length 17,919.

Report section 4 recomputation:

```text
NULL nominal: mean=0.0032977945913256657 rank=18/33
NULL uniform: n=16 mean=0.0011212105742688181 min=-0.010194445458095131 max=0.010103209403288892 sd=0.005035299653076203
NULL CBD eta2: n=8 mean=0.008283202502740719 min=0.004940421205224745 max=0.010558442094790932 sd=0.002156638672322441
NULL near-miss: n=8 mean=0.0033651800088191526 min=0.0016324893585895838 max=0.004075419508021937 sd=0.0008568880843008163
NULL nominal z vs wrong means: -0.03702768040162744

finite-sigma correct means:
  sigma .5 = 0.9492397635046343
  sigma 1  = 0.841150398764859
  sigma 2  = 0.4273752482391075
  sigma 4  = 0.01827093367392778
  sigma 8  = 0.004641032721921352
  sigma 16 = -0.0037121178017794575
uniform-error correct mean = 0.008976982516882632
finite-sigma sequence strictly decreasing: true

MAIN correct: mean=0.4273752482391075 rank=1/33
MAIN uniform: n=16 mean=0.003852457719622023 min=-0.007076430831144595 max=0.013875302873029578 sd=0.006056076164423053
MAIN CBD eta2: n=8 mean=0.2906151267124032 min=0.265095467403936 max=0.3216536227694413 sd=0.02396029043728754
MAIN near-miss: n=8 mean=0.4249603478038021 min=0.42349245042232186 max=0.4267237840397771 sd=0.0010832854592754384
x-dot-e: sd=25.632809482010007 range=[-63,63] fraction_abs_lt_q_over_4=0.7668954740777946
MAIN correct phase equals x-dot-e: 17919/17919
```

The finite-sigma decay is monotone. Uniform error is not another ordered sigma
point. Its `+0.00898`, rank `1/5`, is not residual LWE signal; the class control
below shows that one centered-binomial candidate versus four uniform candidates
is confounded.

The report's phrase "indistinguishable by sigma=8" is `unable_to_check` because
it specifies no statistical test, dependence model, or equivalence margin.

## 3. Secret-leakage audit

I read `measure_scores.py` line by line.

- `A`, `s`, and `e` are generated from the instance RNG; `b=A*s+e mod q`.
- The dual basis uses only `A`, `q`, `m`, and `n`.
- LLL and g6k use independent recorded seeds.
- `s` is never passed to the basis, LLL, Siever, coefficient extraction,
  vector reconstruction, or vector selection.
- All candidates use the same scoring function and arithmetic.
- Candidate index 0 gets no numerical bonus. It scores highly because the
  correct value removes the `y*(s-s')` term.
- `s` is also used to create eight declared `s+e_j` near misses and the decay
  LWE targets.

The near misses do not compromise the sieve or correct score. They deliberately
have a structural advantage over independent wrong candidates: the phase
changes by one coordinate of `y`. They are a local-sensitivity control and
cannot be pooled with independent wrong candidates as exchangeable.

## 4. Null shape and class dependence

The archived null fixes `A`, sieve vectors, candidates and scoring, replacing
only `b` with an independent uniform vector. This correctly removes the LWE
relation to the named secret while holding the measured pipeline fixed: a
paired conditional null.

A null that regenerates `A` and the vector population would test a different
axis: instance-to-instance and sieve-population artifacts. That axis is absent.
Inventor-protocol section 3 requires an identical measurement on a random object
of the same shape. The fixed-population uniform-`b` null satisfies the narrow
secret-ranking control, but not the population-randomization axis.

Script: `scripts/null_class_control.py`

Command:

```text
python3 coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/scripts/null_class_control.py \
  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json \
  --seed 5351520260813 --n-per-class 4096 --chunk-size 128
```

Output:

```json
{
  "candidate_seed": 5351520260813,
  "n_per_class": 4096,
  "uniform_Zq": {
    "mean_of_candidate_means": 0.000183567136794048,
    "sd_of_candidate_means_ddof1": 0.005323676285807647,
    "min": -0.01708052065168374,
    "q05": -0.008438476854305422,
    "median": 0.0001893400820266688,
    "q95": 0.00902626963346222,
    "max": 0.019206357576758166
  },
  "centered_binomial_eta2": {
    "mean_of_candidate_means": 0.008567390088564938,
    "sd_of_candidate_means_ddof1": 0.0026237434123871,
    "min": -0.001174758560867656,
    "q05": 0.004018403833348186,
    "median": 0.008703327331269873,
    "q95": 0.012647524545826723,
    "max": 0.016600427637011337
  },
  "class_difference_cbd_minus_uniform": 0.00838382295177089,
  "class_difference_standard_error": 9.27361305779951e-05,
  "class_difference_over_standard_error": 90.40514090373581,
  "recovery_check": {"archived_null_phase_values_recomputed": 591327, "mismatches": 0}
}
```

This is material class dependence on a target with no LWE signal. It does not
mean the nominal secret was recovered. It means candidate classes are not
exchangeable, so batch 2 must use class-matched or stratified null baselines.

## 5. Certificate and recoverability

Output from `recompute_raw.py`:

```text
rank(A^T mod 127) = 25
A^T surjective onto Z_127^25 = true
rank(candidate-difference matrix mod 127) = 25
y mod 127 recovered from phases for all vectors = true
cross-target phase-difference failures = 0
centered y norm matches archived norm2_y = 17919/17919
max abs centered y = 10
rank(8 archived b rows mod 127) = 8
rank([A^T; b rows] mod 127) = 33
x residue linear nullity = 35-33 = 2
```

Candidate phase differences recover `y mod q` because the difference matrix has
full rank. The tiny norm gives the unique centered lift, matching every
`norm2_y`. Because `A^T` is surjective, every recovered y has an x preimage, so
y alone cannot falsify membership. Even after all eight target equations, two
linear degrees of freedom in x remain. `norm2_x` could constrain an existential
short-x search, but no witness could bind the producer's omitted original x.
The original-pair certificate therefore remains `unable_to_check`.

## 6. Rebuild and independent population reconstruction

The producer did not rebuild from scratch. It honestly reported a pre-existing
Python-3.11.15 venv and `Requirement already satisfied`.

I polled the Coordinator rebuild. `/tmp/instrument_rebuild.log` records:

```text
=== consolidated rebuild started 2026-08-13T15:29:04Z ===
$ rm -rf /tmp/sagevenv
[exit 0]
$ python3 -m venv /tmp/sagevenv
[exit 0]
...
Successfully built g6k
Successfully installed g6k-0.1.2
...
g6k import OK
[exit 0]
=== consolidated rebuild finished 2026-08-13T15:31:07Z ===
```

I did not perform or claim that rebuild. I independently verified functionality:

```text
python instrument OK
numpy 2.5.2
passagemath 10.8.9
fpylll 0.6.4
g6k 0.1.2
```

Script: `scripts/reproduce_measurement.py`

Command:

```text
timeout 600 /tmp/sagevenv/bin/python \
  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/scripts/reproduce_measurement.py \
  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json
```

Output:

```text
runtime {'fpylll': '0.6.4', 'g6k': '0.1.2', 'numpy': '2.5.2',
 'passagemath_standard': '10.8.9',
 'platform': 'Linux-6.12.94+-x86_64-with-glibc2.39',
 'python': '3.12.3 ...'}
run {'algorithm': 'bgj1_sieve', 'fpylll_seed': 20260803005,
 'g6k_seed': 469431436621, 'sieve_seconds_current_container': 10.187695264816284,
 'threads': 1, 'total_seconds_current_container': 10.393049955368042}
population {'expected_N': 17919, 'reconstructed_N': 17919,
 'membership_violating_entries': 0, 'zero_vectors': 0,
 'norm_mismatches': {'norm2_v': 0, 'norm2_x': 0, 'norm2_y': 0},
 'vector_sha256_little_endian_int64': '8988dce8b8162656f0008e6dac14b01fcd86b00dcb3b6af8cd5a0c267bdf0d6c'}
phase_summary {'phase_arrays_checked': 96, 'phase_value_mismatches': 0,
 'x_dot_e_main_mismatches': 0}
scientific_content_match True
```

Every target had zero mismatches: MAIN and NULL each `33 x 17919`; each decay
target `5 x 17919`. This is exact scientific-content reproduction, not
bit-identical file reproduction. Environment version drift and timing fields
preclude full-file identity. Under AGENTS rule 5 that is an infrastructure
limitation, not evidence against the measurement.

The reconstruction strongly corroborates membership but does not make omitted
original x vectors observable.

## 7. Forbidden comparison and provenance

`MATZOV` occurs only in prohibitory prose. The executable source imports no
estimator module. `results.json` and `receipt.json` state:

```text
"states_a_finding": false
"compared_against_assumed_law": false
```

I did not use `/tmp/lattice-estimator` or compare against `MATZOV.Nf`.

The model probe output was:

```text
OK    configuration loaded
WARN  anthropic: $ANTHROPIC_API_KEY unset
WARN  fireworks: $FIREWORKS_API_KEY unset
WARN  local: model probe failed at http://localhost:8000/v1/models: connection refused
WARN  openai: $OPENAI_API_KEY unset
WARN  openrouter: $OPENROUTER_API_KEY unset
WARN  zai: $ZAI_API_KEY unset
WARN  zai-anthropic: $ZAI_API_KEY unset
```

Therefore `model_verified: false` and `resolved_model_id: null`.

## 8. Final checks

Final report validation:

```text
metric_status_counts {'reproduced': 30, 'unable_to_check': 4, 'not_reproduced': 1}
declared_counts {'reproduced': 30, 'not_reproduced': 1, 'unable_to_check': 4, 'total': 35}
verdict passed ADMISSIBLE_WITH_DEFECTS
```

No `git add`, `git commit`, `git push`, or other Git write was run.
