"""Shared loaders for the TASK-20260929-69b7c5 red-team attacks (EXP-PFDR-7c8bf2 Stage 0).

Reads ONLY the committed package at commit 1a037688c through a detached worktree
(RT-1).  Imports no solver module: stats.py is loaded by file path (RT-5).
Nothing is written outside the red-team write scope; every script writes its
outputs next to itself in attacks/out/.

Row selection re-implements specification P2/P3 from the frozen text (series are
(file, m, fb) on engine mitm, rows with ok true, min_index twins never fitted).
It is cross-checked against the archived floor-rows.jsonl.gz / fits.json by
check_pipeline.py so that every attack runs on exactly the archived series.
"""
from __future__ import annotations

import atexit
import gzip
import importlib.util
import json
import math
import os
import random
import resource
import sys
import time
from collections import OrderedDict, defaultdict

import numpy as np

_T0 = time.time()


@atexit.register
def _report_resources():  # machine-protection record (RT-6): peak RSS and wall time
    ru = resource.getrusage(resource.RUSAGE_SELF)
    sys.stderr.write("[resources] peak_rss_mb=%.1f cpu_s=%.1f wall_s=%.1f\n"
                     % (ru.ru_maxrss / 1024.0, ru.ru_utime + ru.ru_stime, time.time() - _T0))

WT = os.environ.get(
    "PFDR_WT",
    "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-stage0-1a037688c")
RESULTS = os.path.join(WT, "src", "crypto_autoresearcher", "index_calculus", "results")
RUN_DIR = os.path.join(WT, "experiments", "EXP-PFDR-7c8bf2", "runs", "RUN-PFDR-7c8bf2-stage0")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

FILES = [
    "sweep-minfill-20260926.jsonl.gz",
    "sweep-arity-minfill-20260926.jsonl.gz",
    "sweep-arity67-20260928.jsonl.gz",
    "sweep-mitm-20260926.jsonl.gz",
    "sweep-arity-20260926.jsonl.gz",
]
SERIES = OrderedDict([
    ("S3-smallx-filtered", ("sweep-minfill-20260926.jsonl.gz", 3, "small_x")),
    ("S3-random-filtered", ("sweep-minfill-20260926.jsonl.gz", 3, "random")),
    ("S3-subgroup-filtered", ("sweep-minfill-20260926.jsonl.gz", 3, "subgroup")),
    ("S3-smallx-unfiltered", ("sweep-arity-minfill-20260926.jsonl.gz", 3, "small_x")),
    ("S4-smallx", ("sweep-arity-minfill-20260926.jsonl.gz", 4, "small_x")),
    ("S5-smallx", ("sweep-arity-minfill-20260926.jsonl.gz", 5, "small_x")),
    ("S6-smallx", ("sweep-arity67-20260928.jsonl.gz", 6, "small_x")),
    ("S7-smallx", ("sweep-arity67-20260928.jsonl.gz", 7, "small_x")),
])
# Curve sets sharing (bits, curve) instances (checked in check_pipeline.py).
CURVE_SET = {
    "S3-smallx-filtered": "filtered", "S3-random-filtered": "filtered",
    "S3-subgroup-filtered": "filtered", "S3-smallx-unfiltered": "unfiltered",
    "S4-smallx": "unfiltered", "S5-smallx": "unfiltered", "S6-smallx": "unfiltered",
    "S7-smallx": "unfiltered",
}
REPS, SEED, LEVEL = 2000, 0, 0.95


def model_value(m: int) -> float:
    """F-2 / F-3 model value: 0 at odd m, 1/(2m) at even m."""
    return 0.0 if m % 2 else 1.0 / (2 * m)


def table_arity(m: int) -> int:
    return max(1, min(m - 1, (m + 1) // 2))


def load_stats():
    path = os.path.join(WT, "src", "crypto_autoresearcher", "index_calculus", "stats.py")
    spec = importlib.util.spec_from_file_location("rt69b7c5_stats", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_file(name: str) -> list[dict]:
    with gzip.open(os.path.join(RESULTS, name), "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


_CACHE: dict = {}


def all_rows() -> dict[str, list[dict]]:
    if "rows" not in _CACHE:
        _CACHE["rows"] = {n: load_file(n) for n in FILES}
    return _CACHE["rows"]


def series_rows(name: str, lo: int = 12, hi: int = 32) -> list[dict]:
    """Rows of one P3 primary series in file order (the order analyze_floor passes)."""
    f, m, fb = SERIES[name]
    out = []
    for r in all_rows()[f]:
        if r["method"] != f"ic_m{m}" or r["fb"] != fb or r.get("engine") != "mitm" or not r["ok"]:
            continue
        if lo <= r["bits"] <= hi:
            out.append(r)
    return out


def ratio(r: dict, S: float | None = None, rel: float | None = None, N: float | None = None) -> float:
    S = r["s3_solves"] if S is None else S
    rel = r["relations"] if rel is None else rel
    N = r["N"] if N is None else N
    return S / (0.5 * math.sqrt(rel * N))


def xs_ys(rows, yfun=None, xfun=None):
    yfun = yfun or (lambda r: math.log2(ratio(r)))
    xfun = xfun or (lambda r: r["log2N"])
    return [xfun(r) for r in rows], [yfun(r) for r in rows], [r["bits"] for r in rows]


def ols(xs, ys):
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    xm = x.mean()
    b = float(((x - xm) * (y - y.mean())).sum() / ((x - xm) ** 2).sum())
    a = float(y.mean() - b * xm)
    return b, a


class FastBoot:
    """Exact linear-algebra form of stats.bootstrap_slope for a FIXED design.

    stats.bootstrap_slope draws its resampling indices from random.Random(seed)
    and they depend only on the strata (groups, in first-appearance order), not on
    ys.  The bootstrap OLS slope of replicate b is linear in ys: slope_b = W[b] @ y.
    Precomputing W reproduces the frozen procedure for every synthetic y on the
    same design; check_pipeline.py and j4_coverage.py verify equality with the
    literal function.
    """

    def __init__(self, xs, groups, reps=REPS, seed=SEED, level=LEVEL):
        self.xs = np.asarray(xs, float)
        n = len(xs)
        strata = defaultdict(list)
        for i, g in enumerate(groups):
            strata[g].append(i)
        rng = random.Random(seed)
        W = np.zeros((reps, n))
        for b in range(reps):
            idx = [rng.choice(members) for members in strata.values() for _ in members]
            xi = self.xs[idx]
            xm = xi.mean()
            sxx = ((xi - xm) ** 2).sum()
            np.add.at(W[b], idx, (xi - xm) / sxx)
        self.W = W
        tail = (1 - level) / 2
        self.klo = int(math.floor(tail * (reps - 1)))
        self.khi = int(math.ceil((1 - tail) * (reps - 1)))

    def slope(self, Y):
        """Y: (n,) or (K, n) -> OLS slope(s)."""
        Y = np.atleast_2d(np.asarray(Y, float))
        xc = self.xs - self.xs.mean()
        return (Y - Y.mean(axis=1, keepdims=True)) @ xc / (xc @ xc)

    def interval(self, Y, chunk=2000):
        """Y: (K, n) -> (slope, lo, hi) arrays of length K, exactly as stats.bootstrap_slope."""
        Y = np.atleast_2d(np.asarray(Y, float))
        slopes = self.slope(Y)
        los, his = [], []
        for s in range(0, Y.shape[0], chunk):
            B = Y[s:s + chunk] @ self.W.T  # (k, reps)
            B = np.partition(B, [self.klo, self.khi], axis=1)  # exact order statistics
            los.append(B[:, self.klo])
            his.append(B[:, self.khi])
        return slopes, np.concatenate(los), np.concatenate(his)


def stratified_boot_generic(fit, rows_by_group, reps=REPS, seed=SEED, level=LEVEL):
    """Stratified percentile bootstrap of an arbitrary statistic `fit(list_of_indices)`.

    Resampling scheme identical to stats.bootstrap_slope (random.Random(seed), strata in
    first-appearance order, rng.choice per member); `fit` receives the resampled index list.
    """
    strata = defaultdict(list)
    for i, g in enumerate(rows_by_group):
        strata[g].append(i)
    rng = random.Random(seed)
    boots = []
    for _ in range(reps):
        idx = [rng.choice(members) for members in strata.values() for _ in members]
        v = fit(idx)
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            boots.append(v)
    boots.sort()
    tail = (1 - level) / 2
    return boots[int(math.floor(tail * (len(boots) - 1)))], boots[int(math.ceil((1 - tail) * (len(boots) - 1)))]


def dump(name: str, obj) -> str:
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True, default=float)
    return path
