# Decided design: calibration item fresh

- Experiment id: CAL-fresh. Card id: CARD-CAL-fresh-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py write .tmp/calibration-run/fresh/session/log.txt start`, timeout 120 seconds, success exit code 0.
- Receipt at `.tmp/calibration-run/fresh/receipt.json`. Write scope: `.tmp/calibration-run/fresh/` only.
- Bind evals/calibration/fixtures/emit.py. The directory `.tmp/calibration-run/fresh/session/` must not exist before the run.
