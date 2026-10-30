"""Shared helpers for the TASK-20261029-11526b red-team review (J3a, J3b, PTM-1..PTM-5).

Reviewer-written. Reads recorded run artifacts of EXP-PFDR-bb0d26 read-only. Imports nothing from the
producer implementation (the PTM-1 in-process call to run.analyze_records lives in ptm1.py only).
Every statistic below is written from experiments/EXP-PFDR-bb0d26/specification.yaml
/experiment/inputs/statistics and cell_classes; sample variance is the n-1 form ('null sample variances').
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 8))
EXPD = os.path.join(REPO, "experiments", "EXP-PFDR-bb0d26")
JOBS = os.path.join(EXPD, "runs", "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")
REPJOBS = os.path.join(EXPD, "runs", "RUN-PFDR-cd03e2", "toy-rep-jobs.jsonl")
ANALYSIS = os.path.join(EXPD, "runs", "RUN-PFDR-089edc", "analysis.json")
DESIGN = os.path.join(EXPD, "runs", "RUN-PFDR-e44a19", "design.json")
KAT = os.path.join(EXPD, "implementation", "fixtures", "kat.json")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

NULL_REPS = 20
TARGET = 2500
GATES = {"flag_dev": 0.10, "flag_z": 4.0, "null_dev": 0.05, "null_ci_lo": 0.90, "null_ci_hi": 1.10,
         "plant_kappa": 1.15, "plant_z": 4.0, "rep_z": 3.0, "rep_dev": 0.05,
         "cal_sd_lo": 0.75, "cal_sd_hi": 1.25, "cal_mean_abs": 0.35, "valid_min": 0.50, "null_valid_min": 0.80}
REVIEW_NS = "TASK-20261029-11526b"   # namespace of every reviewer RNG; never a curve seed


def rel(path: str) -> str:
    return os.path.relpath(path, REPO)


def review_rng(*labels) -> random.Random:
    d = hashlib.sha256("|".join(map(str, (REVIEW_NS,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


def review_np_rng(*labels) -> np.random.Generator:
    d = hashlib.sha256("|".join(map(str, (REVIEW_NS,) + labels)).encode()).digest()
    return np.random.default_rng(int.from_bytes(d[:16], "big"))


def load_jobs(path: str = JOBS) -> list[dict]:
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def load_analysis() -> dict:
    with open(ANALYSIS) as f:
        return json.load(f)


def load_design() -> dict:
    with open(DESIGN) as f:
        return json.load(f)


def by_cell(recs: list[dict], ok_only: bool = True) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in recs:
        if ok_only and r["status"] != "ok":
            continue
        out.setdefault(r["cell"], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: r["c"])
    return out


def curve_arrays(rs: list[dict], arm: str = "gap_C"):
    """Per-curve arrays: g (structured arm), m (null mean), s2 (null sample variance n-1), nulls (k x 20)."""
    nulls = np.array([r["null_C"] for r in rs], dtype=np.float64)
    g = np.array([r[arm] for r in rs], dtype=np.float64)
    m = nulls.mean(axis=1)
    s2 = nulls.var(axis=1, ddof=1)
    return g, m, s2, nulls


def cell_stats_np(g, m, s2):
    S, M, V = float(g.sum()), float(m.sum()), float(s2.sum())
    sd = math.sqrt(V * (1 + 1 / NULL_REPS)) if V > 0 else None
    return {"S": S, "M": M, "V": V, "kappa": S / M if M > 0 else None,
            "z": (S - M) / sd if sd else None, "sigma_kappa": sd / M if (sd and M > 0) else None}


def bootstrap_ci(g, m, B: int, rng: np.random.Generator):
    n = len(g)
    idx = rng.integers(0, n, size=(B, n))
    ks = g[idx].sum(axis=1) / m[idx].sum(axis=1)
    ks.sort()
    return [float(ks[int(0.025 * B)]), float(ks[int(0.975 * B) - 1])], float(ks.std(ddof=1))


def classify(M, kappa, z, ci, plant_ok: bool = True):
    """Frozen first-match classes for a complete cell (spec cell_classes)."""
    if M < TARGET:
        return "inconclusive_underpowered"
    if not plant_ok:
        return "inconclusive_plant_not_recovered"
    if abs(kappa - 1) >= GATES["flag_dev"] and abs(z) > GATES["flag_z"]:
        return "flagged"
    if abs(kappa - 1) < GATES["null_dev"] and GATES["null_ci_lo"] <= ci[0] and ci[1] <= GATES["null_ci_hi"]:
        return "null"
    return "intermediate"


# ---------------------------------------------------------------- reviewer-written counting kernel

def count_CD(X, p: int) -> tuple[int, int]:
    """C = sum_s binom(m_s, 2), D = #{s : m_s >= 1}, m_s over unordered pairs of distinct labels."""
    X = np.asarray(X, dtype=np.int64)
    n = len(X)
    if len(np.unique(X)) != n:
        raise ValueError("labels not distinct")
    if p <= (1 << 21) and n * (n - 1) // 2 >= p // 4:
        cnt = np.zeros(p, dtype=np.int64)
        for i0 in range(0, n - 1, 512):
            i1 = min(n - 1, i0 + 512)
            parts = [(X[i] + X[i + 1:]) % p for i in range(i0, i1)]
            cnt += np.bincount(np.concatenate(parts), minlength=p)
        return int((cnt * (cnt - 1) // 2).sum()), int((cnt > 0).sum())
    sums = np.concatenate([(X[i] + X[i + 1:]) % p for i in range(n - 1)]).astype(np.int64)
    sums.sort()
    if len(sums) == 0:
        return 0, 0
    b = np.flatnonzero(np.diff(sums)) + 1
    runs = np.diff(np.concatenate(([0], b, [len(sums)])))
    return int((runs * (runs - 1) // 2).sum()), int(len(runs))


def brute_CD(X, p: int) -> tuple[int, int]:
    mult: dict[int, int] = {}
    X = list(map(int, X))
    for i in range(len(X)):
        for j in range(i + 1, len(X)):
            s = (X[i] + X[j]) % p
            mult[s] = mult.get(s, 0) + 1
    return sum(v * (v - 1) // 2 for v in mult.values()), len(mult)


# ---------------------------------------------------------------- label universe (reviewer-written)

def powmod_vec(base: np.ndarray, e: int, p: int) -> np.ndarray:
    """Vectorized base^e mod p for p < 2^31 (products < 2^62 fit in int64)."""
    base = np.asarray(base, dtype=np.int64) % p
    res = np.ones_like(base)
    while e:
        if e & 1:
            res = (res * base) % p
        base = (base * base) % p
        e >>= 1
    return res


def in_L(x: np.ndarray, p: int, a: int, b: int) -> np.ndarray:
    """x in L iff f(x) = x^3 + a x + b is a nonzero square mod p (Euler criterion)."""
    x = np.asarray(x, dtype=np.int64) % p
    f = ((x * x % p) * x + a * x + b) % p
    return (f != 0) & (powmod_vec(f, (p - 1) // 2, p) == 1)


def uniform_labels(n: int, p: int, a: int, b: int, rng: np.random.Generator, exclude=None) -> np.ndarray:
    """n distinct uniform labels of L (x uniform in [0, p), kept when in L, repeats skipped)."""
    taken = set() if exclude is None else set(map(int, exclude))
    out: list[int] = []
    while len(out) < n:
        cand = rng.integers(0, p, size=max(64, 3 * (n - len(out))))
        cand = cand[in_L(cand, p, a, b)]
        for x in cand.tolist():
            if x not in taken:
                taken.add(x)
                out.append(x)
                if len(out) == n:
                    break
    return np.array(out, dtype=np.int64)


def phi(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2))


def _clean(o, sig: int = 10):
    if isinstance(o, dict):
        return {str(k): _clean(v, sig) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v, sig) for v in o]
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        x = float(o)
        if not math.isfinite(x):
            return None
        return float(f"{x:.{sig}g}")
    return o


MAX_BYTES = 64 * 1024


def write_json(name: str, obj, sig: int = 10) -> str:
    """Floats rounded to `sig` significant digits, compact one-line-per-top-key layout; refuses > 64 KiB."""
    path = os.path.join(OUT, name)
    obj = _clean(obj, sig)
    lines = ["{"]
    keys = sorted(obj.keys())
    for i, k in enumerate(keys):
        lines.append(json.dumps(k) + ":" + json.dumps(obj[k], sort_keys=True, separators=(",", ":"))
                     + ("," if i < len(keys) - 1 else ""))
    lines.append("}")
    text = "\n".join(lines) + "\n"
    if len(text.encode()) > MAX_BYTES:
        raise ValueError(f"{name} would be {len(text.encode())} bytes > 64 KiB")
    with open(path, "w") as f:
        f.write(text)
    return path
