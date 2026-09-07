import sys, time, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.rrg_null import run_rrg_null

for n, s in [(1000, 3), (5000, 5), (20000, 10)]:
    t0 = time.time()
    res = run_rrg_null(n, s, d=3, num_starts=500, rng=random.Random(42))
    print(f"n={n} s={s} -> {res} time={time.time()-t0:.2f}s")
