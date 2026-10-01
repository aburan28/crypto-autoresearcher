# EXP-QSP-82a906 implementation provenance

Written for TASK-20260917-66ec2b. No number, table, or JSON value is read
from `analysis/qsp-ecc2k130/explore/`. `gf2rc.c` is a GF(2)[X] root counter
and is not copied here; the C resultant is original to this directory.

- `f2arith.py`: bit-packed F_2[X] and F_{2^n} arithmetic. Carry-less
  multiply is the standard sparse-operand loop (same algorithm as many
  GF(2) codes in this repo; re-authored, not imported).
- `i2_python.py`: interpolation Sylvester over F_{2^n} (Newton form).
- `i1_sylvester.c`: Bareiss determinant of the Sylvester matrix over F_2[X].
- `chain.py`: frozen S_3 / xi=1 expansion and phi-composition.
- `i3_gcd.py`: bivariate content-primitive Euclidean algorithm via
  pseudo-remainder, used only when the eliminant is identically zero.
- `runlib.py`, `driver.py`: stage runner and AGENTS.md companions.

I1 and I2 do not share a determinant implementation.
