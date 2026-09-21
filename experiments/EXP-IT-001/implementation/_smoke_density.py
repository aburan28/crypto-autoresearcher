from sage.all import *
import time, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
import it001_pure as pure
import run_bounded_toy as R

bits = 20
deadline = time.time() + 180
p, err = R.find_p_bits(bits, deadline)
print("p", p, "err", err)
if p is None:
    sys.exit(1)
t = time.time()
ok = spec = 0
for j in range(0, 50000):
    rec = R.retain_j_light(p, bits, j)
    if rec:
        ok += 1
        j_, N, h, order = rec
        det = pure.detect_special(order, p, N)
        if det["any_special"]:
            spec += 1
            if spec <= 5:
                print("special", j_, det, "N", N)
print("50000j time", time.time() - t, "retained", ok, "special", spec)
rate = 50000 / (time.time() - t + 1e-9)
print("est full scan seconds", p / rate)
