# Validity correction — RUN-ECQTUP-416e78-002 and RUN-ECQTUP-416e78-009

Run records are immutable. Neither run directory has been edited; this file supersedes the
`status:` line of each manifest by reference, and both runs are retained in full.

## RUN-ECQTUP-416e78-002 — `completed_valid` in its manifest, actually `invalid_measurement`

**What it did.** Scanned 10 694 arbitrary integer 6-tuples through `scripts/tuple_scan.py` and
measured a height envelope for each.

**The defect.** Mestre's construction gives a genus-1 quartic only when `deg_x r = 4`. That is
NOT automatic; it is a codimension-1 condition on the tuple. For the other tuples `r` is a
QUINTIC and `y^2 = r(x,T)` has genus 2. `mestre.quartic_to_weierstrass` and `mestre.quartic_IJ`
pad/truncate their input to five ascending coefficients, so a quintic silently lost its `x^5`
term and every downstream number — Jacobian, minimal model, naive height, envelope, arm fits,
surface degree, Shioda-Tate ceiling — was computed for an object that is not the family's curve.

**Extent.** 10 567 of the 10 694 rows (98.8 %) are affected. The 127 rows with `deg_x_r == 4` are
computed correctly and agree with the corrected run, but the run as a whole is not a valid
measurement of what it claims to measure.

**Classification.** `implementation_error` in `scripts/tuple_scan.py` / `scripts/mestre.py`,
producing an `invalid_measurement` run.

**How it was caught.** By an assertion (`point not on quartic`) raised while transporting
sections for tuple `(0,1,3,7,12,20)`, not by the scan itself. `scripts/tuple_scan_v2.py` now
REFUSES any family with `deg_x_r != 4` and records the refusal.

**Superseded by.** `RUN-ECQTUP-416e78-003` (spread <= 56), `-008` (sampled 57-600), `-010`
(spread 57-74). Nothing from RUN-002 is used in any deliverable except the single reported count
"127 of 10 694 tuples were admissible", which is a property of the tuples and not of the
mis-specified curves.

## RUN-ECQTUP-416e78-009 — `invalid_measurement`, correctly recorded by the harness

Invoked `tuple_scan_v2.py` with `--extra-strata`, a flag that exists only in the superseded
`tuple_scan.py`. `argparse` refused, the process exited 2, no result was produced. Recorded as
`invalid_measurement` with `non-zero exit code 2`. Classification: `implementation_error`
(operator error in the invocation). Superseded by `RUN-ECQTUP-416e78-010`, which is the same
scan with the flag removed and nothing else changed.
