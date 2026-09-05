# General polynomial solver selection with ML

A complete, bounded software benchmark: generate polynomial systems, measure
solver configurations, train two selectors, evaluate held-out inputs, save JSON
checkpoints, and independently check the resulting artifacts. It runs locally
or as an AutoLab-compatible Harbor task. A CPU is sufficient.

This package implements general computational algebra on small synthetic
systems. It does not implement curve/isogeny search, summation-polynomial
decomposition, or discrete-log solving. Its results do not establish that any
elliptic curve is easier to attack. The frozen software scope and acceptance
criteria are in [PROTOCOL.md](PROTOCOL.md).

The native and Docker runs already executed, including measured outcomes and
artifact locations, are recorded in [VALIDATION.md](VALIDATION.md).
The complete original run artifacts and trained models are included in the
[example archive](examples/README.md), so they are available from a fresh checkout.

## Run locally

Use Python 3.11 or later on Linux or macOS. From the repository root:

```sh
python3 -m venv /private/tmp/polynomial-ml-venv
/private/tmp/polynomial-ml-venv/bin/python -m pip install -r tasks/polynomial_solver_ml/environment/requirements.txt
/private/tmp/polynomial-ml-venv/bin/python tasks/polynomial_solver_ml/run_local.py run \
  --profile quick --output runs/polynomial_ml/my-first-run
/private/tmp/polynomial-ml-venv/bin/python tasks/polynomial_solver_ml/run_local.py verify \
  runs/polynomial_ml/my-first-run
```

On Linux, use `/tmp/polynomial-ml-venv` in place of `/private/tmp/...`. If the
pinned dependencies are already installed, `python3` can run the wrapper
directly. Output directories must be new: the runner refuses to overwrite an
existing run. The verifier is read-only and must use the source version named
by the manifest. The run command also saves a sibling
`my-first-run.verification.json` receipt containing the manifest hash and
verification duration.

The quick profile measures **23 systems × 4 actions = 92 subprocesses**, with
one repetition per action. `--profile standard` measures **58 × 4 = 232
subprocesses**, with two repetitions each. Both profiles use one child at a
time. Defaults are `--seed 20260904`, `--fit-seed 0`, `--steps 1200`,
`--action-timeout 5`, and `--budget-seconds 600`. These are bounded software
runs; there is no unattended campaign loop. Individual solver timeouts are
censored and charged twice their limit (PAR-2). Other failures stop the run and
preserve a failed manifest plus available logs. Incomplete runs never pass
verification.

## What is trained

The input is a pair of polynomials in two variables over a small prime field.
The fixed schedules use primes from 7 through 23, and input validation bounds
primes at 31. All systems have a planted root. Three families are used for
training: dense quadratics, sparse cubics, and triangular systems. Validation
and test use different primes from training. Dense cubics form an additional
held-out family. Features include support size, degrees, mixed-term fractions,
coefficient summaries and field size; they exclude roots, instance identity,
family names and split labels.

| Action | Gröbner method | Monomial order |
|---|---|---|
| 0, fixed baseline | Buchberger | lex |
| 1 | F5B | lex |
| 2 | Buchberger | grevlex |
| 3 | F5B | grevlex |

Each action constructs a basis through SymPy's public API, then finds roots by
exhaustively evaluating that basis on the small finite-field grid. A separate
scalar modular evaluator enumerates all roots of the original equations.
Agreement is required for every completed action. Exhaustive grid evaluation
is a correctness baseline, not an efficient general root-extraction algorithm.

The supervised selector is ridge regression on log costs, with λ = 1 and an
unpenalized intercept. The RL selector is a **one-step contextual bandit**:
softmax REINFORCE with sampled actions, fixed learning rate 0.05, and
row-centered/normalized negative log-cost rewards. It trains offline using the
complete measured training table. This is not a multi-step RL environment, and
the full cost of collecting labels is reported. Normalization and model
weights are fitted from training rows only; no validation or test tuning occurs.
Prediction greedily chooses the minimum predicted cost or maximum policy logit.

Comparators are the fixed baseline, the best fixed action on training rows,
seeded uniform selection, the exact expected cost of uniform selection, and a
retrospective oracle. The oracle sees outcomes and is not deployable.

Controls include a known sign-dependent learning problem, a constant-cost
problem requiring exactly zero bandit updates, and a separate fit with
per-row shuffled training action costs. The shuffle run is a diagnostic,
without a finite-sample threshold declaring a learner successful or unsuccessful.

## Artifacts and interpretation

| Artifact | Contents |
|---|---|
| `config.json`, `cases.json` | Frozen parameters and deterministic input systems |
| `measurement_order.json` | Seeded order of all case/action measurements |
| `labels.jsonl`, `logs/` | Every completed/censored action and raw child output |
| `models.json` | Both plain-JSON checkpoints, feature names and training IDs |
| `evaluation.json` | Selections, individual costs, split means and speedups |
| `controls.json` | Positive, constant and shuffled-label controls |
| `report.md` | Readable performance comparison and full cost accounting |
| `manifest.json` | Status, actual timestamps, dependency versions, source/artifact SHA-256 hashes |

The primary measured cost is median symbolic construction + Gröbner basis
construction + root-grid extraction time. Component timings, process startup
overhead, label collection, feature extraction, fitting, inference and controls
are accounted for separately. These are noisy microbenchmarks with one fit
seed, and every reported speedup is restricted to its declared split.
There is no speedup requirement for software acceptance. Check whether a
learner beats **the best fixed training action**, not just action 0.

Final basis degree, root count, zero-dimensionality and peak process RSS are
recorded. Intermediate degree growth, operation counts, search-node counts and
degree of regularity are **not measured**. Local macOS memory checking records
RSS and checks it after the solve returns; Linux children apply a 2 GiB
address-space limit. Harbor additionally limits the container to 2 GiB.

The verifier regenerates inputs, checks hashes and complete roots, deterministically
replays fitting from training rows, replays controls, and separately recomputes
metric arithmetic. Hashes detect artifact corruption; they do not authenticate
timings against a malicious producer. A run is bound to its recorded source
and numerical environment, so retain that version when replaying checkpoints.

To use a saved checkpoint in Python, put `environment/` on `PYTHONPATH`, load
`models.json` with `json.load`, build a NumPy array of `instances.features(case)`
for validated cases, and call `learning.select(checkpoint, features)`. The
returned `ridge` and `bandit` arrays contain action IDs from the table above.
No Python object deserialization is needed.

For example, after extracting the bundled examples as described above:

```sh
PYTHONPATH=tasks/polynomial_solver_ml/environment python3 - <<'PY'
import json
from pathlib import Path
import numpy as np
from polynomial_ml.instances import make_case, features
from polynomial_ml.learning import select
from polynomial_ml.solver import ACTIONS

root = Path('runs/polynomial_ml/bundled-examples/native')
model = json.loads((root / 'models.json').read_text())
case = make_case(p=17, family='dense_quadratic', seed=42, index=0, split='demo')
choices = select(model, np.asarray([features(case)], dtype=float))
for learner, action_ids in choices.items():
    action = int(action_ids[0])
    print(learner, action, ACTIONS[action])
PY
```

This predicts a solver configuration without retraining or running the solver.

## Harbor harness and tests

The task uses the Harbor directory contract accepted by the local AutoLab task
collection. From the repository root, with Harbor and Docker available:

```sh
harbor run -p tasks/polynomial_solver_ml -a oracle -n 1 -k 1 -r 0 \
  --jobs-dir runs/polynomial_ml/harbor --job-name my-first-harbor-run
python3 -m pytest -q tasks/polynomial_solver_ml/tests
```

The dedicated `polynomial-solver-ml` GitHub Actions workflow also runs these
tests and a fresh quick-profile run on task changes, retaining its outputs as
the `polynomial-solver-ml-run` workflow artifact.

The oracle executes `solution/solve.sh`. `tests/test.sh` runs the software
tests, verifies `/app/output/run`, and writes a reward of 1 only after success.
Harbor exports the complete output directory with the trial artifacts. Reward
is binary software completion, not a competitive optimization score. A new
container build downloads the pinned packages; the task container runs with
internet disabled. The base image is `python:3.11-slim` rather than a pinned
digest; Harbor retains build/job receipts and the run records actual versions.

This standalone task does not dispatch through the repository's ECDLP research
ledger or change any hypothesis status. The implementation-worker envelope is
in `engineering-handoff.yaml`.
