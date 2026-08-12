"""Calibrate Groebner cost versus factor-base size F.

The measured ideal is <S3(x1,x2,x_R), fV(x1), fV(x2)> with deg fV = F, so F — not
the field size — drives the cost. This sweeps F at three fixed field sizes to
expose that, and to size the scaled sweep (see fb_scaled_sweep.py and README.md).

Run:  TMPDIR=/Volumes/Volume/tmp python3 <this file>
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # workspace root

from harness.semaev import measure_s3_decomposition  # noqa: E402
from harness.toycurve import generate_instance  # noqa: E402

BITS = (8, 10, 12)
FACTOR_BASES = (14, 24, 32, 48, 64)

print(f"{'bits':>4} {'p':>7} {'F':>5} {'F^2/2p':>7} {'gb_secs':>9} {'size':>5} "
      f"{'maxdeg':>6} {'trivial':>7} {'decomp':>6}")
for bits in BITS:
    inst = generate_instance(seed=1, field_bits=bits)
    p = inst.p
    for F in FACTOR_BASES:
        t0 = time.time()
        m = measure_s3_decomposition(inst, factor_base_size=F)
        wall = time.time() - t0
        print(f"{bits:>4} {p:>7} {F:>5} {F * F / (2 * p):>7.3f} "
              f"{m.groebner_seconds:>9.3f} {m.groebner_basis_size:>5} "
              f"{m.groebner_basis_max_degree:>6} {str(m.is_trivial_ideal):>7} "
              f"{str(m.decomposition_found):>6}", flush=True)
        if wall > 60:
            print(f"     (cell took {wall:.0f}s — stopping this row)", flush=True)
            break
