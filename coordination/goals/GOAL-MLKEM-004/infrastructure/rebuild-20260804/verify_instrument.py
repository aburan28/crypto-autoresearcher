"""Verify the rebuilt instrument against KN-TECH-14efa5's own recorded numbers."""
import sys
import time

print("python:", sys.version.replace("\n", " "))

import sage
import sage.all
from sage.all import PowerSeriesRing, QQ

print("sage.__version__:", sage.version.version)
print("sage.all resolves to:", sage.all.__file__)
R = PowerSeriesRing(QQ, "x")
x = R.gen()
print("PowerSeriesRing discriminator:", 1 + x + R.O(6) if False else (1 + x).add_bigoh(6))

import fpylll
from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
from fpylll.fplll.bkz_param import Strategy
from fpylll.algorithms.bkz2 import BKZReduction

print("fpylll:", fpylll.__version__)

FPLLL.set_random_seed(20260803005)
A = IntegerMatrix.random(60, "qary", q=3329, k=30)
M = GSO.Mat(A)
M.update_gso()
print("fpylll dim60 qary q=3329 ||b0|| before: %.1f" % (M.get_r(0, 0) ** 0.5))
t0 = time.time()
strategies = [Strategy(b) for b in range(41)]
param = BKZ.Param(block_size=30, strategies=strategies, max_loops=4, flags=BKZ.MAX_LOOPS)
BKZReduction(A)(param)
M2 = GSO.Mat(A)
M2.update_gso()
print("fpylll dim60 BKZ-30 x4 ||b0|| after:  %.1f  (%.2fs)" % (M2.get_r(0, 0) ** 0.5, time.time() - t0))

from g6k import Siever
from g6k.siever_params import SieverParams

print("g6k imported OK")
FPLLL.set_random_seed(20260803005)
B = IntegerMatrix.random(50, "qary", q=3329, k=25)
LLL.reduction(B)
t0 = time.time()
g = Siever(B, SieverParams(threads=1, seed=469431436621))
g.initialize_local(0, 0, 50)
g("gauss")
print("g6k dim50 gauss_sieve db: %d vectors (%.2fs)" % (len(g), time.time() - t0))
print("kernels:", [k for k in ("gauss", "bgj1", "bdgl", "hk3", "nv")])
