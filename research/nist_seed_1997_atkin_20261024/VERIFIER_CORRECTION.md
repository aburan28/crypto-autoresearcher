# Verifier API correction

The first independent Sage attempt stopped at `ZZ(r).euler_phi()` with an `AttributeError`; Sage exposes this operation as the imported function `euler_phi(r)`. Its original verifier is preserved as `verify_v1.py`, and its started record and traceback remain in `runs/scan-v1/verification_started.json` and `verification_stderr.log`.

The correction imports and calls `euler_phi(r)` and directs the fresh verification receipt into a new, write-once output directory. It changes no protocol metric, input, companion-matrix result, candidate trace set, or cutoff rule. The failed attempt does not independently verify the completed raw scan or say anything about a curve's mathematical properties. Only a subsequent complete replay may do that.
