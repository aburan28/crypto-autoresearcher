# Decided design: calibration item no-codes

- Experiment id: CAL-no-codes. Card id: CARD-CAL-no-codes-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id run): `python3 evals/calibration/fixtures/emit.py print alpha`, timeout 60 seconds.
- Bind evals/calibration/fixtures/emit.py. Receipt at `.tmp/calibration-run/no-codes/receipt.json`. Write scope: `.tmp/calibration-run/no-codes/` only.
