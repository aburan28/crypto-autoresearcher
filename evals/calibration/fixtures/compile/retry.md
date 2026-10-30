# Decided design: calibration item retry

- Experiment id: CAL-retry. Card id: CARD-CAL-retry-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py exit 0`, timeout 60 seconds, success exit code 0, retry only on exit code 75, at most 2 attempts.
- Receipt at `.tmp/calibration-run/retry/receipt.json`. Write scope: `.tmp/calibration-run/retry/` only.
- Bind evals/calibration/fixtures/emit.py.
