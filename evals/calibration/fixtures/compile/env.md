# Decided design: calibration item env

- Experiment id: CAL-env. Card id: CARD-CAL-env-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py print seeded`, timeout 60 seconds, success exit code 0, environment PYTHONHASHSEED=0.
- Receipt at `.tmp/calibration-run/env/receipt.json`. Write scope: `.tmp/calibration-run/env/` only.
- Bind evals/calibration/fixtures/emit.py.
