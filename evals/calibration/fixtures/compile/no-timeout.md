# Decided design: calibration item no-timeout

- Experiment id: CAL-no-timeout. Card id: CARD-CAL-no-timeout-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id run): `python3 evals/calibration/fixtures/emit.py print alpha`, success exit code 0.
- Bind evals/calibration/fixtures/emit.py. Receipt at `.tmp/calibration-run/no-timeout/receipt.json`. Write scope: `.tmp/calibration-run/no-timeout/` only.
