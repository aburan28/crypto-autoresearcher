# Decided design: calibration item codes

- Experiment id: CAL-codes. Card id: CARD-CAL-codes-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py exit 1`, timeout 45 seconds, success exit codes 0 and 1.
- Receipt at `.tmp/calibration-run/codes/receipt.json`. Write scope: `.tmp/calibration-run/codes/` only.
- Bind evals/calibration/fixtures/emit.py.
