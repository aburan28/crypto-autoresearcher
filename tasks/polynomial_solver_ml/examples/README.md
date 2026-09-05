# Previously executed example runs

`validated-runs.zip` preserves the original byte contents of two successful
software runs, their trained checkpoints, and the Harbor test/job receipts.
These are general synthetic polynomial benchmarks, not research-ledger records.
The archive's SHA-256 is in `validated-runs.zip.sha256`.

Extract into a new directory from the repository root:

```sh
python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile
output = Path('runs/polynomial_ml/bundled-examples')
output.mkdir(parents=True, exist_ok=False)
with ZipFile('tasks/polynomial_solver_ml/examples/validated-runs.zip') as archive:
    archive.extractall(output)
print(output)
PY
```

The archive contains:

- `native/`: the macOS run, including `models.json`, `cases.json`, `report.md`,
  complete measurements, logs and manifest.
- `harbor/`: the Linux container run with the same artifact layout.
- `native.verification.json`, `harbor.verification.json`: original verification
  receipts bound to each run manifest.
- `harbor-job/result.json`: one successful trial, zero exceptions, reward 1.0.
- `harbor-verifier/`: the 36-test result, verifier receipt and reward.

Read either `report.md` directly or load its checkpoint with `learning.select`.
To attempt complete replay of a run with the matching source and numerical
environment, use:

```sh
python3 tasks/polynomial_solver_ml/run_local.py verify runs/polynomial_ml/bundled-examples/native
```

Model fitting is replayed exactly. Different Python/NumPy/platform combinations
may produce floating-point differences; an exact-replay failure in a different
environment does not invalidate the original receipt. Generate a fresh run on
your machine for locally measured costs and a locally verified checkpoint.

All archived file contents retain their original hashes and timestamps inside
the JSON receipts. Nothing in the archive was regenerated for publication.
