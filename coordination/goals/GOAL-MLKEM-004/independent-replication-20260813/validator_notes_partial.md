# TASK-20260803-535d15 validation notes

Verdict: `ADMISSIBLE_WITH_DEFECTS`.

Quantitative-claim counts: 30 `reproduced`, 1 `not_reproduced`, 4
`unable_to_check`. The raw phases and scores are admissible. A future
comparison that pools candidate classes is not.

I read the required contracts and context first: `AGENTS.md`,
`agents/validator.md`, `docs/inventor-protocol.md` (including sections 3 and
6), `GOAL-MLKEM-004.yaml`, `KN-TECH-14efa5`, `KN-TECH-797223`,
`KN-OPEN-016`, and the complete task card. I did not read the concurrent Red
Team task's output.

## 1. Frozen snapshot and artifacts

Command:

```text
git branch --show-current && git rev-parse HEAD && git merge-base --is-ancestor 8cc51677f7202e9f9b85efdf834860254798abf4 HEAD && git status --porcelain
```

Output:

```text
cursor/launch-mlkem-harness-78fd
7d2f23d83e7d8d9abbe7ac52b9aad48f871d67e0
?? coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/
```

The ancestry check exited 0. The only dirt is this validator's declared write
scope.

Command:

```text
git show --no-ext-diff --format='commit=%H%nparent=%P%nsubject=%s' --name-status 8cc51677f7202e9f9b85efdf834860254798abf4
```

Output:

```text
commit=8cc51677f7202e9f9b85efdf834860254798abf4
parent=abc344ac0745f2e115464a5391624da0b96744b1
subject=snapshot: BATCH-d2a728 first sieve measurement (TASK-20260803-aa727e archiving e53ce2)

A	coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/archives/TASK-20260803-aa727e/snapshot_receipt.json
A	coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/measure_scores.py
A	coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json
A	coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/rebuild_transcript.txt
A	coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/receipt.json
A	coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/report.md
A	coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/results.json
```

Command:

```text
sha256sum <the six producer artifacts>
```

Output:

```text
99763183a5822f6a6ed5820b484c5f78f777be58aa7f54ed9f60c0fce7e7456b  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/rebuild_transcript.txt
c93d41f8b02085e37e7e62c5b6c7e2ff54c349bc38044d8f29650c4769937c7f  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/measure_scores.py
892991c43a602e370b46dc30d40e8bc6b4840f0f9692890f202b422f41bf3642  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json
82cf8006ef1b0221b276bd30a3c12cbf83ed69648bbf2d6c2b545ee7b1325c39  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/results.json
56848a46cc8544793d2b86419d5c58d0601456b6d7acb5ceb3fc944acc663459  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/report.md
d92002139a3f3ebebbe8c6fd2d7efea9946b67ceae427a04cdabfe3df94e7fd8  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/receipt.json
```

All match the receipt. `git diff --exit-code 8cc51677... --
<producer-task-dir>` was empty. Execution revision
`d2f521875cc889eb4c2b3338a91e4c574263fe43` exists and is an ancestor of the
snapshot.

The archive receipt uses a two-commit binding. The receipt inside the snapshot
has sha256 `ca212cb3ede3fc6f89f0296494fe50924a3328e2ae5e9e850b34104f12e875cf`
and null commit fields. Binding commit
`f11808ed56a8fa3ee36b6ac988593b5843ced96a` updates it to the current receipt,
sha256 `63674e261ae50507c55f02ad4ee3819117bcf0a8a4724f586242e01b754cb9a3`,
which names the snapshot and parent. Both commits are reachable.

The producer's dirty-tree boolean is inaccurate. Its own transcript preserves:

```text
$ git -C /home/user/crypto-autoresearcher status --porcelain
?? coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/
```

The receipt calls this `dirty_tree: false` with an explanatory note. Exact
snapshot hashes mitigate the content risk, but the boolean should have been
true.

## 2. Independent raw-only recomputation

Script:

`scripts/recompute_raw.py`

Command:

```text
python3 coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/scripts/recompute_raw.py coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json
```

Key output from the final run:

```text
all_seed_checks True
array_score_checks {'length_failures': [], 'max_serialized_cosine_error': 0.0, 'phase_arrays_checked': 96, 'score_arrays_checked': 72, 'serialized_cosine_mismatches_at_6dp': 0, 'serialized_score_values_checked': 1290168}
ranks [1, 1, 1, 1, 3, 4, 1]
decay_wrong_means [0.0029258668012663623, 0.003311377012517655, 0.003852457719622023, -0.00043600791311706447, 0.0031685781621091794, -0.0002149761597415085, 0.0032305693217537608]
```

Directly from `raw_scores.json`, not `results.json`:

```text
parameters: m=35 n=25 d=60 q=127 N=17919
candidate counts: correct=1 uniform=16 centered-binomial=8 near-miss=8
secret range: [-2,2]
main error: sd=1.9285185177927089 infnorm=4
norm2_v: min=218 median=315 max=329
```

All seeded reconstructions passed: `A`, `s`, the main error and target, all 33
candidates, the uniform null target, and every decay error and target.

The serialized `scores_cos` values are six-decimal values. Every one of
1,290,168 values equals `round(cos(2*pi*t/127),6)` exactly. All 96 phase arrays,
72 score arrays, and four per-vector arrays have length 17,919.

Raw recomputation of report section 4:

```text
NULL nominal: mean=0.0032977945913256657 rank=18/33
NULL uniform: n=16 mean=0.0011212105742688181 min=-0.010194445458095131 max=0.010103209403288892 sd=0.005035299653076203
NULL CBD eta2: n=8 mean=0.008283202502740719 min=0.004940421205224745 max=0.010558442094790932 sd=0.002156638672322441
NULL near-miss: n=8 mean=0.0033651800088191526 min=0.0016324893585895838 max=0.004075419508021937 sd=0.0008568880843008163
NULL nominal z relative to all wrong candidate means: -0.03702768040162744

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

The finite-sigma decay is monotone. The uniform-error row is not an additional
ordered sigma point. Its `+0.00898`, rank `1/5`, is not residual LWE signal;
the class-control below shows that comparing one centered-binomial candidate
to four uniform candidates systematically favors the former.

The statement "indistinguishable by sigma=8" cannot be independently checked
as an inferential claim because the report defines no test or equivalence
margin. The numerical closeness is real.

## 3. Secret-leakage audit

I read `measure_scores.py` line by line.

- `A`, `s`, and `e` are generated from the instance RNG; `b=A*s+e mod q`.
- The dual basis uses only `A`, `q`, `m`, and `n`.
- LLL and g6k use independent recorded seeds.
- `s` is never passed to the basis, LLL, Siever, coefficient extraction,
  basis reconstruction, or vector selection.
- Scoring uses one common function for all candidates.
- The correct candidate has no index-dependent numerical bonus. It scores
  highly because correctness removes the `y*(s-s')` term.
- `s` is also used to create eight declared `s+e_j` near misses and the decay
  LWE targets.

The near misses do not compromise the sieve or correct score. They do have a
designed structural advantage over independent wrong candidates: the phase
changes by one coordinate of `y`. They are a local-sensitivity control and
must not be pooled with uniform or independent centered-binomial wrong
candidates as if all wrong candidates were exchangeable.

## 4. Null shape and candidate-class dependence

The archived null fixes `A`, sieve vectors, candidate set and scoring, and
replaces `b` by an independent uniform vector. This correctly removes the LWE
relation to the named secret while holding the measured pipeline fixed. It is
a paired conditional null.

A null that regenerates `A` and the vector population would test a different
axis: instance-to-instance and sieve-population-specific artifacts. That axis
is absent. Inventor-protocol section 3 requires an identical measurement on a
random object of the same shape. The fixed-population uniform-`b` null satisfies
the narrow secret-ranking control, but not the population-randomization axis.

Script:

`scripts/null_class_control.py`

Command:

```text
python3 coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/scripts/null_class_control.py coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json --seed 5351520260813 --n-per-class 4096 --chunk-size 128
```

Output:

```json
{
  "candidate_dimension": 25,
  "candidate_seed": 5351520260813,
  "centered_binomial_eta2": {
    "max": 0.016600427637011337,
    "mean_of_candidate_means": 0.008567390088564938,
    "mean_standard_error": 4.099599081854844e-05,
    "median": 0.008703327331269873,
    "min": -0.001174758560867656,
    "n_candidates": 4096,
    "q05": 0.004018403833348186,
    "q95": 0.012647524545826723,
    "sd_of_candidate_means_ddof1": 0.0026237434123871
  },
  "chunk_size": 128,
  "class_difference_cbd_minus_uniform": 0.00838382295177089,
  "class_difference_over_standard_error": 90.40514090373581,
  "class_difference_standard_error": 9.27361305779951e-05,
  "n_per_class": 4096,
  "null_target": "NULL_uniform_target",
  "q": 127,
  "recovery_check": {
    "archived_null_phase_values_recomputed": 591327,
    "max_abs_centered_y": 10,
    "mismatches": 0
  },
  "uniform_Zq": {
    "max": 0.019206357576758166,
    "mean_of_candidate_means": 0.000183567136794048,
    "mean_standard_error": 8.318244196574448e-05,
    "median": 0.0001893400820266688,
    "min": -0.01708052065168374,
    "n_candidates": 4096,
    "q05": -0.008438476854305422,
    "q95": 0.00902626963346222,
    "sd_of_candidate_means_ddof1": 0.005323676285807647
  }
}
```

This is a material class effect on a target with no LWE signal. The null is
approximately centered for uniform candidates but shifted positive and
narrower for centered-binomial candidates. It does not mean the nominal secret
was recovered. It means candidate classes are not exchangeable, so batch 2
must use class-matched/stratified null baselines.

## 5. Certificate and recoverability

Modular results from `recompute_raw.py`:

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

For each vector, candidate phase differences satisfy

`t(c_j)-t(c_0) = -y*(c_j-c_0) mod q`.

The candidate-difference matrix has full rank, so this recovers `y mod q`.
The tiny norm makes its centered integer lift unique and all `norm2_y` values
match. The phase table gives only eight independent target equations for 35
`x` coordinates. Even after adding `A^T x=y`, two linear degrees of freedom
remain. Because `A^T` is surjective, any `y` residue has some `x` preimage.
Thus recovered `y` alone cannot falsify membership. `norm2_x` could be used in
an additional existential short-`x` consistency search over the two remaining
degrees of freedom, but even a witness would not identify or bind the
producer's omitted original `x`. The original-pair certificate therefore
remains unable to check.

## 6. Instrument rebuild and independent population reconstruction

The producer did not rebuild from scratch. It honestly reported a pre-existing
Python-3.11.15 venv and `Requirement already satisfied`.

I polled the Coordinator's rebuild:

```text
tmux -f /exec-daemon/tmux.portal.conf ls
```

Output:

```text
autosave: 1 windows (created Thu Aug 13 15:32:22 2026)
instrument-rebuild2: 1 windows (created Thu Aug 13 15:29:04 2026)
```

`/tmp/instrument_rebuild.log` records a genuine separate Coordinator rebuild:

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

I did not perform or claim that rebuild.

My first two functional-check commands failed because I asked for version
attributes that this passagemath package does not expose:

```text
AttributeError: module 'sage.all' has no attribute '__version__'
```

then:

```text
AttributeError: module 'sage' has no attribute '__version__'
```

These are validator command errors, not instrument failures. The corrected
command used package metadata and exited 0:

```text
python 3.12.3
numpy 2.5.2
passagemath-standard 10.8.9
series 1 + x + x^2 + x^3 + x^4 + x^5 + O(x^6)
fpylll 0.6.4
g6k 0.1.2 /tmp/sagevenv/lib/python3.12/site-packages/g6k/__init__.py
kernels ['gauss_sieve', 'bgj1_sieve', 'bdgl_sieve', 'hk3_sieve', 'nv_sieve']
```

Script:

`scripts/reproduce_measurement.py`

Command:

```text
timeout 600 /tmp/sagevenv/bin/python coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/scripts/reproduce_measurement.py coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json
```

Output:

```json
{
  "phase_comparison": {
    "phase_arrays_checked": 96,
    "phase_value_mismatches": 0,
    "x_dot_e_main_mismatches": 0
  },
  "population": {
    "expected_N": 17919,
    "membership_violating_entries": 0,
    "norm_mismatches": {
      "norm2_v": 0,
      "norm2_x": 0,
      "norm2_y": 0
    },
    "reconstructed_N": 17919,
    "vector_sha256_little_endian_int64": "8988dce8b8162656f0008e6dac14b01fcd86b00dcb3b6af8cd5a0c267bdf0d6c",
    "zero_vectors": 0
  },
  "run": {
    "algorithm": "bgj1_sieve",
    "fpylll_seed": 20260803005,
    "g6k_seed": 469431436621,
    "sieve_seconds_current_container": 10.070361852645874,
    "threads": 1,
    "total_seconds_current_container": 10.297475814819336
  },
  "runtime": {
    "fpylll": "0.6.4",
    "g6k": "0.1.2",
    "numpy": "2.5.2",
    "passagemath_standard": "10.8.9",
    "platform": "Linux-6.12.94+-x86_64-with-glibc2.39",
    "python": "3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]"
  },
  "scientific_content_match": true
}
```

Every target reported zero mismatches: MAIN and NULL each had shape
`33 x 17919`; each of the six decay targets had shape `5 x 17919`.

This is exact scientific-content reproduction, not bit-identical file
reproduction. The producer used Python 3.11.15, numpy 2.4.6 and passagemath
10.8.7. The current rebuild uses Python 3.12.3, numpy 2.5.2 and passagemath
10.8.9. Timing leaves also differ. That infrastructure drift is not evidence
against the measurement.

The independent reconstruction strongly corroborates the membership claim but
does not make the original omitted `x` vectors observable, so the original
archive certificate remains `unable_to_check`.

## 7. No forbidden comparison or finding

Search results show `MATZOV` only in prohibitory prose in `measure_scores.py`
and `report.md`. The executable source imports no estimator module.
`results.json` and `receipt.json` contain:

```text
"states_a_finding": false
"compared_against_assumed_law": false
```

I did not use `/tmp/lattice-estimator` and did not compare against `MATZOV.Nf`.

## 8. Model probe

Command:

```text
python3 -m orchestration.adapter doctor --probe
```

Output summary:

```text
OK    configuration loaded
WARN  anthropic: $ANTHROPIC_API_KEY unset
WARN  fireworks: $FIREWORKS_API_KEY unset
WARN  local: model probe failed: network error listing models at http://localhost:8000/v1/models: [Errno 111] Connection refused
WARN  openai: $OPENAI_API_KEY unset
WARN  openrouter: $OPENROUTER_API_KEY unset
WARN  zai: $ZAI_API_KEY unset
WARN  zai-anthropic: $ZAI_API_KEY unset
```

Therefore `model_verified: false` and `resolved_model_id: null`.

## 9. Final report checks

Command/output:

```text
yaml_ok True
metric_status_counts {'reproduced': 30, 'unable_to_check': 4, 'not_reproduced': 1}
declared_counts {'reproduced': 30, 'not_reproduced': 1, 'unable_to_check': 4, 'total': 35}
verdict passed ADMISSIBLE_WITH_DEFECTS
```

Script syntax check:

```text
ast_ok 3 ['null_class_control.py', 'recompute_raw.py', 'reproduce_measurement.py']
```

No `git add`, `git commit`, `git push`, or other Git write was run.
