# Decided design: calibration item print

- Experiment id: CAL-print. Card id: CARD-CAL-print-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py print alpha`, timeout 60 seconds, success exit code 0.
- Receipt at `.tmp/calibration-run/print/receipt.json`. Write scope: `.tmp/calibration-run/print/` only.
- Bind evals/calibration/fixtures/emit.py.
