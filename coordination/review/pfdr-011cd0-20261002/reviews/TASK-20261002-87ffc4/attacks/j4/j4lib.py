"""TASK-20261002-87ffc4 red team, J4 / J8 / PTM: this reviewer's own implementation of the
frozen A-CAL generator G-NB-R, the CC-8 statistic, A-INT and the controls, written from the
specification text (readings in attacks/j4/00-readings-before-computing.yaml). Standard
library + numpy only; no import of analyze_relcensus.py or any engine module.

Data source: the compact per-instance extract written by attacks/common/extract_rows.py from
the archived canonical rows (R12 table, R13 search).
"""
from __future__ import annotations

import gzip
import json
import math
import os
from collections import defaultdict

import numpy as np

WT = os.environ.get("RT_WT", "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/"
                    "wt-pfdr011cd0-5753edf2e")
EXP = os.path.join(WT, "experiments", "EXP-PFDR-011cd0")
DESIGN = os.path.join(EXP, "runs", "RUN-PFDR-011cd0-p0-design", "attempt-3", "design.json")
EXTRACT = os.environ.get("RT_EXTRACT", "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/"
                         "scratchpad/rt-87ffc4/extract.jsonl.gz")

RUNGS = (20, 22, 24, 26, 28, 30, 32)
BAND = (30, 32)
RANDOMS = {"SUB": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
           "DICK": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}
KNOWN_NULL = {"SUB": "known_null_sub", "DICK": "known_null_dick"}
STRUCT = {"SUB": ("subgroup", "small_x"), "DICK": ("dickson",)}
FAM_OF = {"subgroup": "SUB", "small_x": "SUB", "dickson": "DICK", "known_null_sub": "SUB",
          "known_null_dick": "DICK", "planted_sub": "SUB"}
FAM1_CM = (("TT", 3), ("TT", 4), ("TT", 5), ("SS", 3), ("SS", 4), ("SS", 5), ("TB", 3))
FAM1_ARMS = ("subgroup", "small_x", "dickson")
H_OF_M = {3: 2, 4: 2, 5: 3}
MGEN = {"TT": {2: 3, 3: 10}, "TB": {2: 3, 3: 4}}
PANEL = {"TT": "table", "TB": "table", "SS": "search"}
TARGET = {("TT", 3): 1.15, ("TT", 4): 1.15, ("TT", 5): 1.15, ("SS", 3): 1.15, ("SS", 4): 1.15,
          ("SS", 5): 1.15, ("TB", 3): 1.5}
CARRY = ("subgroup", "TT", 3, 28)
GRID = [round(1 + i / 100, 2) for i in range(101)] + [2.5, 3.0, 5.0]
TA1_LABEL = "SS m 4 P0 inputs estimated at 22-24 bits; TA-1 assumed, not verified by P0"


def load_design():
    return json.load(open(DESIGN))


def curve_list(design, panel, m, b):
    n = design["final_n"][panel][str(m)][str(b)]
    return list(range(10, 10 + n))


def load_extract(path=EXTRACT):
    rows = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            r = json.loads(line)
            rows[(r["bits"], r["curve"], r["m"], r["arm"], r["mode"])] = r
    return rows


def count_of(rec, cls):
    if rec is None or rec.get("status") != "completed_valid":
        return None
    if cls == "SS":
        return rec["SSx"]["n"]
    return rec[cls]["n"]


def mu_model(rec, cls, m):
    """L1 first moment with L2's generic multiplicity (TT/TB), per instance."""
    N, Ep, s = rec["N"], rec["Ep"], rec["s"]
    h = H_OF_M[m]
    if cls == "TT":
        return Ep * (Ep - 1) / N / MGEN["TT"][h]
    if cls == "TB":
        return 2.0 * Ep * s / N / MGEN["TB"][h]
    raise ValueError(cls)


class Group:
    def __init__(self, key, curves, randoms, mj, D, D_hat, extra=None):
        self.key = key
        self.curves = curves
        self.randoms = randoms  # (n, 3) observed
        self.mj = np.asarray(mj, dtype=float)
        self.D = float(D)
        self.D_hat = D_hat
        self.extra = extra or {}

    @property
    def M(self):
        return float(self.mj.sum())


def build_groups(rows, design, rho1_mode="per_family"):
    """(fam, cls, m, rung) groups from the random arms. rho1_mode: 'per_family' (this
    reviewer's primary reading) or 'pooled' (I-10)."""
    out = {}
    rho1 = {}
    # rho1 per (fam, cls, m, b) and pooled per (cls, m, b)
    for cls in ("TT", "TB"):
        for m in (3, 4, 5):
            for b in RUNGS:
                tot_o = tot_m = 0.0
                per = {}
                for fam in ("SUB", "DICK"):
                    o = mm = 0.0
                    for c in curve_list(design, "table", m, b):
                        for arm in RANDOMS[fam]:
                            rec = rows.get((b, c, m, arm, "table"))
                            n = count_of(rec, cls)
                            if n is None:
                                continue
                            o += n
                            mm += mu_model(rec, cls, m)
                    per[fam] = o / mm if mm > 0 else None
                    tot_o += o
                    tot_m += mm
                rho1[("pooled", cls, m, b)] = tot_o / tot_m if tot_m > 0 else None
                for fam in per:
                    rho1[(fam, cls, m, b)] = per[fam]
    drops = []
    for cls in ("TT", "TB", "SS"):
        panel = PANEL[cls]
        for m in (3, 4, 5):
            for b in RUNGS:
                for fam in ("SUB", "DICK"):
                    curves, R, mus = [], [], []
                    arms_all = RANDOMS[fam] + (KNOWN_NULL[fam],) + STRUCT[fam] + (
                        ("planted_sub",) if (fam == "SUB" and m == 3 and panel == "table") else ())
                    for c in curve_list(design, panel, m, b):
                        bad = [a for a in arms_all
                               if count_of(rows.get((b, c, m, a, panel)), cls) is None]
                        if bad:
                            drops.append((fam, cls, m, b, c, bad))
                            continue
                        recs = [rows[(b, c, m, a, panel)] for a in RANDOMS[fam]]
                        curves.append(c)
                        R.append([count_of(x, cls) for x in recs])
                        if cls != "SS":
                            mus.append(float(np.mean([mu_model(x, cls, m) for x in recs])))
                    R = np.array(R, dtype=float).reshape(-1, 3)
                    s2 = R.var(axis=1, ddof=1) if len(R) else np.zeros(0)
                    nb = R.mean(axis=1) if len(R) else np.zeros(0)
                    D_hat = float(s2.sum() / nb.sum()) if len(R) and nb.sum() > 0 else None
                    D = max(D_hat if D_hat is not None else 1.0, 1.0)
                    if cls == "SS":
                        mj = [float(R.mean()) if len(R) else 0.0] * len(curves)
                        r1 = None
                    else:
                        r1 = rho1[(fam if rho1_mode == "per_family" else "pooled", cls, m, b)] or 0.0
                        mj = [r1 * x for x in mus]
                    out[(fam, cls, m, b)] = Group((fam, cls, m, b), curves, R, mj, D, D_hat,
                                                  {"rho1": r1, "mu_model_mean": float(np.mean(mus)) if mus else None})
    return out, rho1, drops


def arm_counts(rows, g, arm, cls, m, b):
    panel = PANEL[cls]
    return np.array([count_of(rows.get((b, c, m, arm, panel)), cls) for c in g.curves], dtype=float)


def cc8(CA, CR, Q):
    V = max(Q, CR)
    SD = math.sqrt(V * 4.0 / 3.0)
    if SD > 0:
        z = (CA - CR) / SD
    else:
        z = 0.0 if CA == CR else (math.inf if CA > CR else -math.inf)
    return {"C_A": CA, "C_R": CR, "sum_s2": Q, "V": V, "SD_null": SD,
            "kappa_rel": CA / CR if CR > 0 else None, "z": z}


def observed_cell(rows, groups, arm, cls, m, rungs, fam=None, randoms_override=None):
    """CC-8 on the data. randoms_override: list of three arm names to use as the randoms."""
    fam = fam or FAM_OF[arm]
    CA = CR = Q = 0.0
    per_curve = []
    for b in rungs:
        g = groups[(fam, cls, m, b)]
        A = arm_counts(rows, g, arm, cls, m, b)
        if randoms_override:
            R = np.stack([arm_counts(rows, g, a, cls, m, b) for a in randoms_override], axis=1)
        else:
            R = g.randoms
        CA += float(A.sum())
        CR += float(R.mean(axis=1).sum())
        Q += float(R.var(axis=1, ddof=1).sum())
        per_curve.append((b, A, R))
    out = cc8(CA, CR, Q)
    out["per_curve"] = per_curve
    return out


# ------------------------------------------------------------------------------------------
# simulation

def draw(rng, mean, D, size):
    """NB(mean, variance D*mean) (Poisson at D <= 1); mean may be an array (last axis)."""
    mean = np.asarray(mean, dtype=float)
    if D <= 1.0:
        return rng.poisson(mean, size=size)
    return rng.negative_binomial(mean / (D - 1.0), 1.0 / D, size=size)


def sim_group(rng, g, B, arm_D=None, n_arms=0):
    """B replicates of one group: C_R (B,), Q (B,), and n_arms independent arm SUMS (B, n_arms).
    arm_D: dispersion for the arms (default the group's D)."""
    n = len(g.curves)
    if n == 0:
        return np.zeros(B), np.zeros(B), np.zeros((B, n_arms))
    mj = g.mj
    X = draw(rng, mj, g.D, (B, 3, n))
    CR = X.mean(axis=1).sum(axis=1)
    Q = X.var(axis=1, ddof=1).sum(axis=1)
    Darm = g.D if arm_D is None else arm_D
    A = np.stack([draw(rng, g.M, Darm, (B,)) if g.M > 0 else np.zeros(B) for _ in range(n_arms)], axis=1) \
        if n_arms else np.zeros((B, 0))
    return CR, Q, A


def zvec(CA, CR, Q):
    V = np.maximum(Q, CR)
    SD = np.sqrt(V * 4.0 / 3.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (CA - CR) / SD
    return np.where(SD > 0, z, np.where(CA > CR, np.inf, np.where(CA < CR, -np.inf, 0.0)))


def kolmogorov_sf(D, n):
    """Asymptotic Kolmogorov survival with Stephens' modification (own code)."""
    if D <= 0:
        return 1.0
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * D
    s = 0.0
    for k in range(1, 400):
        t = 2.0 * (-1) ** (k - 1) * math.exp(-2.0 * k * k * lam * lam)
        s += t
        if abs(t) < 1e-16:
            break
    return min(1.0, max(0.0, s))


def ks_D_against(obs, ref_sorted):
    """One-sample KS distance of obs against the empirical law of a large reference sample,
    ties handled conservatively (F(x) and F(x-))."""
    o = np.sort(np.asarray(obs, dtype=float))
    n = len(o)
    Fle = np.searchsorted(ref_sorted, o, "right") / len(ref_sorted)
    Flt = np.searchsorted(ref_sorted, o, "left") / len(ref_sorted)
    hi = np.arange(1, n + 1) / n
    lo = np.arange(0, n) / n
    return float(max(np.max(hi - Fle), np.max(Flt - lo), 0.0))


def poisson_cdf(k, mu):
    if k < 0:
        return 0.0
    if mu <= 0:
        return 1.0
    # sum in log space
    lt = -mu
    s = math.exp(lt)
    t = s
    for i in range(1, int(k) + 1):
        t *= mu / i
        s += t
    return min(1.0, s)


def t_quantile(q, df):
    """Student t quantile by bisection on a numerically integrated CDF (own code)."""
    from math import lgamma, exp, log

    def betacf(a, b, x):
        MAXIT, EPS, FPMIN = 500, 3e-16, 1e-300
        qab, qap, qam = a + b, a + 1, a - 1
        c, d = 1.0, 1 - qab * x / qap
        d = 1 / (d if abs(d) > FPMIN else FPMIN)
        h = d
        for mm in range(1, MAXIT + 1):
            m2 = 2 * mm
            aa = mm * (b - mm) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d
            d = 1 / (d if abs(d) > FPMIN else FPMIN)
            c = 1 + aa / c
            c = c if abs(c) > FPMIN else FPMIN
            h *= d * c
            aa = -(a + mm) * (qab + mm) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d
            d = 1 / (d if abs(d) > FPMIN else FPMIN)
            c = 1 + aa / c
            c = c if abs(c) > FPMIN else FPMIN
            de = d * c
            h *= de
            if abs(de - 1) < EPS:
                break
        return h

    def ibeta(a, b, x):
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        bt = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log(1 - x))
        if x < (a + 1) / (a + b + 2):
            return bt * betacf(a, b, x) / a
        return 1 - bt * betacf(b, a, 1 - x) / b

    def cdf(t):
        x = df / (df + t * t)
        p = 0.5 * ibeta(df / 2, 0.5, x)
        return 1 - p if t > 0 else p

    lo, hi = -100.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def jdump(path, obj):
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            f = float(o)
            return f if math.isfinite(f) else str(f)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, tuple):
            return list(o)
        raise TypeError(type(o))

    def clean(o):
        if isinstance(o, float) and not math.isfinite(o):
            return str(o)
        if isinstance(o, dict):
            return {(k if isinstance(k, str) else str(k)): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        return o
    with open(path, "w") as f:
        json.dump(clean(obj), f, indent=1, default=conv)
