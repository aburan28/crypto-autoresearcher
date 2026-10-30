# Decided design: calibration item two

- Experiment id: CAL-two. Card id: CARD-CAL-two-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py print one`, timeout 60 seconds, success exit code 0.
- Command 2 (id step-2): `python3 evals/calibration/fixtures/emit.py print two`, timeout 90 seconds, success exit code 0, stdout to `.tmp/calibration-run/two/two.txt`.
- Receipt at `.tmp/calibration-run/two/receipt.json`. Write scope: `.tmp/calibration-run/two/` only.
- Bind evals/calibration/fixtures/emit.py.
