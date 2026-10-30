# Decided design: calibration item no-scope

- Experiment id: CAL-no-scope. Card id: CARD-CAL-no-scope-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id run): `python3 evals/calibration/fixtures/emit.py print alpha`, timeout 60 seconds, success exit code 0.
- Bind evals/calibration/fixtures/emit.py. Receipt at `.tmp/calibration-run/no-scope/receipt.json`.
