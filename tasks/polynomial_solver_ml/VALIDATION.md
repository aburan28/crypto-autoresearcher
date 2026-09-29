# Executed software validation

This record describes software completion only. No research hypothesis status
was changed, and no mathematical or cryptanalytic claim is made.

The implementation worker used engineering handoff `TASK-20260904-e51c51`.
This integration record is associated with `TASK-20260904-b54f89`. Both IDs were
allocated and checked using `tools/allocate_id.py` before use. These are
engineering references, not research-dispatch approvals.

## Commands actually executed

```sh
python3 -m pytest -q tasks/polynomial_solver_ml/tests
python3 tasks/polynomial_solver_ml/run_local.py run --profile quick --output runs/polynomial_ml/native-e51c51
harbor run -p tasks/polynomial_solver_ml -a oracle -n 1 -k 1 -r 0 --jobs-dir runs/polynomial_ml/harbor --job-name e2e-b54f89
```

The native test run passed **36 tests in 1.61 seconds**. The Harbor verifier
passed the same **36 tests in 1.05 seconds**. Harbor completed **one trial,
zero exceptions, reward 1.0**, with a total job duration of approximately
51 seconds including build/startup, training and verification. The reward is
binary software completion and consistency, not performance.

Both actual quick-profile runs measured **23 systems, 92 completed actions,
zero timeouts**, with exact agreement against independently enumerated original
roots. Each trained on 12 systems using 12 features and four actions, with
1,200 bandit update steps and fit seed 0. Positive and constant-cost controls
passed. All held-out observations, including slower results, are retained.

| Observation | Native macOS | Harbor Linux container |
|---|---:|---:|
| Pipeline elapsed, seconds | 23.650 | 28.854 |
| Model fitting, seconds | 0.0323 | 0.0269 |
| Ridge speedup, test split | 1.025× | 1.000× |
| Bandit speedup, test split | 1.017× | 0.996× |
| Best training-fixed action speedup, test split | 1.012× | 1.000× |
| Ridge speedup, unseen family | 0.988× | 1.000× |
| Bandit speedup, unseen family | 0.988× | 0.995× |

Speedups compare mean selected solve cost against action 0 on the same split.
The test split contains six systems, and the unseen-family split contains two.
The models are fitted separately to each environment's measured costs. These
small and inconsistent differences do not demonstrate a reliable advantage
for either learner. They establish working measurement, training, evaluation
and artifact-verification paths. Inputs are deterministic; timings and
timing-trained checkpoints are machine/run dependent.

## Retained evidence in this workspace

Run outputs live under the repository's ignored `runs/` directory. Preserve
them separately when copying or committing the source package.

For publication, their original byte contents were also bundled in
[`examples/validated-runs.zip`](examples/validated-runs.zip), with extraction
instructions in [examples/README.md](examples/README.md). The archive includes
both complete runs and the Harbor verification/job receipts. Each source and
artifact hash was checked before packaging; the underlying run files were not
modified.

- Native output: `runs/polynomial_ml/native-e51c51/`
- Native verification: `runs/polynomial_ml/native-e51c51.verification.json`
- Native manifest SHA-256: `7b8353d0afeaa25134f5639295610bd045e0c7f5c7d2cb858e3d9ab2f666c447`
- Harbor job result: `runs/polynomial_ml/harbor/e2e-b54f89/result.json`
- Harbor trial: `polynomial_solver_ml__G3VpmgU`
- Harbor output below that trial: `artifacts/polynomial-ml-output/run/`
- Harbor verifier evidence below that trial: `verifier/tests.xml`, `verifier/test-stdout.txt`, `verifier/verification.json`, `verifier/reward.json`
- Harbor run manifest SHA-256: `2244788f89762c4c9ab07dd21d8e01d020be755e114a3f17a0d08eefef3f0636`

Native verification completed at `2026-09-05T03:56:36.990671+00:00`; the
container's initial verification completed at
`2026-09-05T03:58:02.819739+00:00`. These are recorded UTC timestamps, corresponding
to the evening of September 4 in the workspace's America/Los_Angeles timezone.
Both runs used NumPy 2.4.0 and SymPy 1.14.0. Full source hashes, actual Python
versions, component timings and raw child outputs are in the run artifacts.

The standard profile is implemented but was not run end to end in this
validation. Its schedule is covered by unit tests. Tests that inject synthetic
timings exercise failure and integrity paths only; those fixture timings are
not part of either actual run reported above.
