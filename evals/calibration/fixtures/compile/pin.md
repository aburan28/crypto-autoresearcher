# Decided design: calibration item pin

- Experiment id: CAL-pin. Card id: CARD-CAL-pin-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2.
- Command 1 (id step-1): `python3 evals/calibration/fixtures/emit.py print pinned`, timeout 30 seconds, success exit code 0.
- Receipt at `.tmp/calibration-run/pin/receipt.json`. Write scope: `.tmp/calibration-run/pin/` only.
- Pin the commit. Bind evals/calibration/fixtures/emit.py.
