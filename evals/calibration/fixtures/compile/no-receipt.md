# Decided design: calibration item no-receipt

- Experiment id: CAL-no-receipt. Card id: CARD-CAL-no-receipt-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id run): `python3 evals/calibration/fixtures/emit.py print alpha`, timeout 60 seconds, success exit code 0.
- Bind evals/calibration/fixtures/emit.py. Write scope: `.tmp/calibration-run/no-receipt/` only.
