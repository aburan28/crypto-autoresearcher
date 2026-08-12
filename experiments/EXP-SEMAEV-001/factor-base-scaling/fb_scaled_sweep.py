"""Scaled factor-base sweep: keep the S_3 measurement non-degenerate as p grows.

With F fixed, decomposition probability ~ F^2/(2p) decays as 1/p, the target stops
decomposing, and the Groebner metrics collapse to the trivial ideal {1} — a
degenerate measurement, not a cheap solve. Scaling F = ceil(sqrt(p)) holds the
probability near 0.5, which is what makes a cost trend versus field size
measurable at all. See README.md for the recorded results and caveats.

Matched context: rho baseline group operations on the same instance.

Run:  TMPDIR=/Volumes/Volume/tmp python3 <this file>
Takes ~4 min, dominated by the two bits=16 cells (~112 s each). Do NOT pipe
through `tail` — it buffers until exit and hides the incremental rows.
"""
import math
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # workspace root

from harness import rho  # noqa: E402
from harness.semaev import measure_s3_decomposition  # noqa: E402
from harness.toycurve import generate_instance  # noqa: E402

BITS = (8, 10, 12, 14, 16)
SEEDS = (1, 2)

print(f"{'bits':>4} {'seed':>4} {'p':>7} {'F':>5} {'F^2/2p':>7} {'gb_secs':>9} "
      f"{'size':>5} {'maxdeg':>6} {'trivial':>7} {'decomp':>6} {'rho_ops':>8}")
rows = []
for bits in BITS:
    for seed in SEEDS:
        inst = generate_instance(seed=seed, field_bits=bits)
        p = inst.p
        F = math.ceil(math.sqrt(p))
        m = measure_s3_decomposition(inst, factor_base_size=F)
        base = rho.solve(inst)
        rows.append((bits, p, F, m.groebner_seconds, m.decomposition_found))
        print(f"{bits:>4} {seed:>4} {p:>7} {F:>5} {F * F / (2 * p):>7.2f} "
              f"{m.groebner_seconds:>9.3f} {m.groebner_basis_size:>5} "
              f"{m.groebner_basis_max_degree:>6} {str(m.is_trivial_ideal):>7} "
              f"{str(m.decomposition_found):>6} {base.group_operations:>8}", flush=True)

print("\n--- cost versus field size (mean over seeds) ---")
prev = None
for bits in BITS:
    rs = [r for r in rows if r[0] == bits]
    if not rs:
        continue
    mean_p = statistics.mean(r[1] for r in rs)
    mean_gb = statistics.mean(r[3] for r in rs)
    ndec = sum(1 for r in rs if r[4])
    line = (f"  bits={bits:>2}  F={rs[0][2]:>4}  mean_gb={mean_gb:>9.3f}s"
            f"  decomposed {ndec}/{len(rs)}")
    if prev:
        pp, pg = prev
        if pg > 0:
            line += (f"   exponent in p: "
                     f"{math.log(mean_gb / pg) / math.log(mean_p / pp):>5.2f}")
    print(line)
    prev = (mean_p, mean_gb)
