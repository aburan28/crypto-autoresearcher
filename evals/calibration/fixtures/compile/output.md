# Decided design: calibration item output

- Experiment id: CAL-output. Card id: CARD-CAL-output-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py write .tmp/calibration-run/output/result.txt done`, timeout 60 seconds, success exit code 0, declared output `.tmp/calibration-run/output/result.txt`.
- Receipt at `.tmp/calibration-run/output/receipt.json`. Write scope: `.tmp/calibration-run/output/` only.
- Bind evals/calibration/fixtures/emit.py.
