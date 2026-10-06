"""EXP-PFDR-011cd0 analysis (EC-9): P0 design, blinded calibration, unmasking, Stage R'.

    analyze_relcensus.py p0        --archived-runs DIR --bundles 02_bundles.jsonl --curves curves.jsonl.gz --out RUN_DIR
    analyze_relcensus.py calibrate --runs-dir VIEW --design design.json --out RUN_DIR
    analyze_relcensus.py unmask    --runs-dir VIEW --design design.json --calibration calibration.json
                                   --calibration-sha256 SHA --out RUN_DIR
    analyze_relcensus.py stage-r   --runs-dir VIEW --analysis R16/analysis.json --out RUN_DIR17 --step calibrate
    analyze_relcensus.py stage-r   --runs-dir VIEW --analysis R16/analysis.json --out RUN_DIR17 --step unmask
                                   --calibration-sha256 SHA      (R17: calibrate on the stage's randoms and
                                   known-null with A unread, pin, then unmask)
    analyze_relcensus.py grel      --runs RUN ... --out grel-report.json   (G-REL equality gate only)

Imports NO crypto_autoresearcher module.  The relation recount below is written from the
specification's CC-1..CC-3 and shares no code with harvest.py.  The same file serves R11, R15,
R16 and R17 (pinned before R11).

Blinding (analysis.two_step_blinding).  `calibrate` reads, from every rows / harvest-rows file,
ONLY lines whose arm (extracted from the raw line text by a regular expression, BEFORE any JSON
parse) is random_*, known_null_* or known_log; every other line is skipped unparsed, and every
arm seen is logged in arm-read-log.json.  `p0` reads only EXP-PFDR-1b78f7 random arms (same
filter) and design quantities.  `grel` compares the harvester's in-process relation counts with
this file's recount for every retained-row instance and reports equality only (no count).

Interpretation choices, fixed here before any data of this experiment (implementation-notes.yaml
lists them):
  * TB relations are carried by (base, tail) pairs only (CC-4: a relation is counted in each
    class whose PAIRS carry it; two tails sharing an x form a TT pair).
  * Model means (L1 first moment, L2 generic multiplicity): TT pairs E'(E'-1)/N, TB pairs
    2E's/N, SS pairs X(X-1)/N; relations = pairs / M with M = C(2h, h)/2 (TT) or h + 1 (TB),
    h = (m + 1) // 2; SS relations = pairs / Mbar(m).  E' = formally distinct stored tails (the
    random arms' own table blocks in R15/R16; the exact stored-tail count of the table builder,
    h = 2: s^2, h = 3: 4 C(s+2, 3) - 2 C(s+1, 2), at design time).
  * G-NB-R: NB with mean mu and variance D mu (gamma-Poisson; Poisson when D = 1).  Planted excess:
    Poisson-planted A = NB(mu, D) + Poisson((kappa - 1) mu); compound-planted adds
    NB((kappa - 1) mu, D) instead; kappa < 1 (A-INT only) thins NB(mu, D) binomially.
  * z with SD_null = 0: 0 if C_A == C_R, +inf / -inf otherwise (same rule in data and simulation).
  * Simulation seeds: every simulation of seed family i starts from
    numpy.random.default_rng(numpy.random.SeedSequence([0x011cd0, i])), i = 0..4.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = "/home/user/crypto-autoresearcher"
SEED_ROOT = 0x011CD0
N_SEED_FAMILIES = 5
REPS_PER_FAMILY = 20000
CLASSES = ("TT", "TB", "SS")
FAM1_ARMS = ("subgroup", "small_x", "dickson")
FAM1_CM = (("TT", 3), ("TT", 4), ("TT", 5), ("SS", 3), ("SS", 4), ("SS", 5), ("TB", 3))
FAMILY_OF = {"subgroup": "SUB", "small_x": "SUB", "known_null_sub": "SUB", "planted_sub": "SUB",
             "random_sub_r0": "SUB", "random_sub_r1": "SUB", "random_sub_r2": "SUB",
             "dickson": "DICK", "known_null_dick": "DICK",
             "random_dick_r0": "DICK", "random_dick_r1": "DICK", "random_dick_r2": "DICK"}
RANDOMS = {"SUB": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
           "DICK": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}
KNOWN_NULL = {"SUB": "known_null_sub", "DICK": "known_null_dick"}
STRUCT_OF_FAMILY = {"SUB": ("subgroup", "small_x"), "DICK": ("dickson",)}
RUNGS = (20, 22, 24, 26, 28, 30, 32)
BAND = (30, 32)
KAPPA_TARGET = {("TT", 3): 1.15, ("TT", 4): 1.15, ("TT", 5): 1.15, ("SS", 3): 1.15,
                ("SS", 4): 1.15, ("SS", 5): 1.15, ("TB", 3): 1.5}
XREL_GRID = [round(1 + i / 100, 2) for i in range(101)] + [2.5, 3.0, 5.0]
H_OF_M = {3: 2, 4: 2, 5: 3}
MGEN = {"TT": {2: 3, 3: 10}, "TB": {2: 3, 3: 4}}
PANEL_OF_CLASS = {"TT": "table", "TB": "table", "SS": "search"}
CARRY1 = ("subgroup", "TT", 3, 28)
P0_D_FACTOR = {"TT": 1.2, "TB": 1.2, "SS": 1.5}
RAISE_MULTIPLIERS = (1.25, 1.5, 2.0, 2.5, 3.0)
KI, RI = 1 << 40, (1 << 40) + 1
ARM_RE = re.compile(r'"arm": "([A-Za-z0-9_]+)"')
COVERAGE_DESIGNS = 2000
COVERAGE_BOOT_INNER = 200
BOOT_REPS = 20000
POWER_REPS_PER_FAMILY = 4000


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def absp(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(REPO, p)


def dump(path: str, obj) -> None:
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=_json_default)


def _json_default(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        f = float(o)
        return f if math.isfinite(f) else str(f)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, float) and not math.isfinite(o):
        return str(o)
    raise TypeError(type(o))


def fin(x):
    """JSON-safe float (inf/nan as strings)."""
    if x is None:
        return None
    x = float(x)
    return x if math.isfinite(x) else str(x)


# ==========================================================================================
# blinded line reader

class ArmLog:
    def __init__(self) -> None:
        self.files: dict = {}

    def note(self, path: str, arm: str | None, read: bool) -> None:
        f = self.files.setdefault(path, {"read": Counter(), "skipped_unparsed": Counter()})
        f["read" if read else "skipped_unparsed"][arm or "<no arm field>"] += 1

    def as_json(self) -> dict:
        out = {}
        for p, f in self.files.items():
            out[p] = {"read": dict(f["read"]), "skipped_unparsed": dict(f["skipped_unparsed"])}
        return out

    def parsed_arms(self) -> set:
        return {a for f in self.files.values() for a in f["read"]}


def blinded_allowed(arm: str | None) -> bool:
    return arm is not None and (arm.startswith("random_") or arm.startswith("known_null_")
                                or arm == "known_log")


def iter_lines(path: str, allowed=None, log: ArmLog | None = None):
    """Yield parsed JSON records; with `allowed`, a line is parsed only if allowed(arm) where
    arm is read from the RAW line text (no JSON parse before the filter)."""
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if not line.strip():
                continue
            if allowed is not None:
                mm = ARM_RE.search(line)
                arm = mm.group(1) if mm else None
                ok = allowed(arm)
                if log is not None:
                    log.note(path, arm, ok)
                if not ok:
                    continue
            yield json.loads(line)


def key5(r: dict) -> tuple:
    m = r.get("m")
    if m is None and str(r.get("method", "")).startswith("ic_m"):
        m = int(r["method"][4:])
    return (r.get("bits"), r.get("curve"), m, r.get("arm"), r.get("mode"))


# ==========================================================================================
# CC-1..CC-3 recount (independent of harvest.py)

def row_vector(r: dict, N: int) -> dict:
    v = {}
    for i, c in r["coeffs"]:
        c %= N
        if c:
            v[i] = (v.get(i, 0) + c) % N
            if not v[i]:
                del v[i]
    k = r["kcoef"] % N
    if k:
        v[KI] = k
    h = r["rhs"] % N
    if h:
        v[RI] = h
    return v


def monic_of(v: dict, N: int):
    if not v:
        return None
    items = sorted(v.items())
    inv = pow(items[0][1], N - 2, N)
    return tuple((i, c * inv % N) for i, c in items)


def sign_of(v: dict, N: int):
    items = sorted(v.items())
    if items[0][1] * 2 > N:  # lexicographically smaller of v and -v (first nonzero coordinate)
        return tuple((i, (N - c) % N) for i, c in items)
    return tuple(items)


def formal_of(v: dict, N: int, formal_kind: str) -> bool:
    """CC-2.  Generic and planted arms: empty formal basis.  known_log: span{e_j - j e_1}
    with 1-based logs (0-based index i has log i + 1): v formal iff kcoef = rhs = 0 and
    sum_i v_i (i + 1) = 0 mod N."""
    if formal_kind in (None, "none"):
        return False
    if KI in v or RI in v:
        return False
    if formal_kind == "known_log":
        return sum(c * (i + 1) for i, c in v.items()) % N == 0
    raise ValueError(f"formal basis {formal_kind!r} not supported by this recount")


def recount(rows: list[dict], N: int, cls: str, formal_kind: str = "none",
            sign_only_pairs: bool = False, keep_sets: bool = False) -> dict:
    """Relations of one (instance, class, scope) from its retained star rows (CC-1).

    x-groups: rows sharing their first element; the group's star rows in row order.  Pair
    (1, j) carries row_j; pair (i, j), 2 <= i < j, carries row_j - row_i (TT, SS).  TB: only
    the (base, tail) star pairs.  Zero vectors (formal duplicates) dropped."""
    groups: dict = defaultdict(list)
    order = []
    for r in rows:
        if r["class"] != cls:
            continue
        g = json.dumps(r["elements"][0], sort_keys=True)
        if g not in groups:
            order.append(g)
        groups[g].append(row_vector(r, N))
    mult: Counter = Counter()
    sign: set = set()
    star: set = set()
    pairs = zero = 0
    for g in order:
        vs = groups[g]
        for j, vj in enumerate(vs):
            rels = [(True, vj)]
            if cls != "TB":
                for vi in vs[:j]:
                    d = dict(vj)
                    for i, c in vi.items():
                        nv = (d.get(i, 0) - c) % N
                        if nv:
                            d[i] = nv
                        else:
                            d.pop(i, None)
                    rels.append((False, d))
            for is_star, d in rels:
                pairs += 1
                mo = monic_of(d, N)
                if mo is None:
                    zero += 1
                    continue
                mult[mo] += 1
                sign.add(sign_of(d, N))
                if is_star:
                    star.add(mo)
    nonformal = sum(1 for mo in mult if not formal_of(dict(mo), N, formal_kind))
    hist = Counter(mult.values())
    out = {"relations_distinct": len(mult), "relations_distinct_sign": len(sign),
           "relations_nonformal": nonformal, "R_star": len(star),
           "multiplicity_histogram": {str(k): hist[k] for k in sorted(hist)},
           "relation_pairs": pairs, "relation_pairs_zero": zero,
           "pairs_from_rows": sum(len(v) * (len(v) + 1) // 2 if cls != "TB" else len(v)
                                  for v in groups.values()),
           "groups": len(groups)}
    if keep_sets:
        out["_monic"] = set(mult)
    return out


# ==========================================================================================
# model means

def stored_tails(s: int, h: int) -> int:
    if h == 2:
        return s * s
    if h == 3:
        return 4 * math.comb(s + 2, 3) - 2 * math.comb(s + 1, 2)
    raise ValueError(h)


def mu_pairs(cls: str, N: int, Ep: float | None = None, s: int | None = None,
             X: int | None = None) -> float:
    if cls == "TT":
        return Ep * (Ep - 1) / N
    if cls == "TB":
        return 2.0 * Ep * s / N
    return X * (X - 1) / N


def mu_rel_model(cls: str, m: int, N: int, Ep=None, s=None, X=None, mbar_ss=None) -> float:
    p = mu_pairs(cls, N, Ep, s, X)
    if cls == "SS":
        return p / mbar_ss
    return p / MGEN[cls][H_OF_M[m]]


# ==========================================================================================
# small statistics helpers (no scipy)

def _betacf(a: float, b: float, x: float) -> float:
    MAXIT, EPS, FPMIN = 400, 3e-16, 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > FPMIN else FPMIN)
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > FPMIN else FPMIN)
        c = 1 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > FPMIN else FPMIN)
        c = 1 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        de = d * c
        h *= de
        if abs(de - 1) < EPS:
            break
    return h


def betainc_reg(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    bt = math.exp(lbt)
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def t_cdf(t: float, df: float) -> float:
    x = df / (df + t * t)
    p = 0.5 * betainc_reg(df / 2, 0.5, x)
    return 1 - p if t > 0 else p


def t_quantile(q: float, df: float) -> float:
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def kolmogorov_p(D: float, n: int) -> float:
    """Asymptotic Kolmogorov survival with Stephens' small-n correction."""
    if D <= 0:
        return 1.0
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * D
    s = 0.0
    for k in range(1, 200):
        term = 2 * (-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam)
        s += term
        if abs(term) < 1e-14:
            break
    return min(1.0, max(0.0, s))


def ks_against_sample(obs: np.ndarray, sim: np.ndarray) -> dict:
    """One-sample KS of obs against the empirical distribution of a large simulated sample,
    with ties handled by F(x) and F(x-) (conservative for discrete laws)."""
    sims = np.sort(sim)
    o = np.sort(obs)
    n = len(o)
    F_le = np.searchsorted(sims, o, "right") / len(sims)
    F_lt = np.searchsorted(sims, o, "left") / len(sims)
    ecdf_hi = np.arange(1, n + 1) / n
    ecdf_lo = np.arange(0, n) / n
    D = float(max(np.max(ecdf_hi - F_le), np.max(F_lt - ecdf_lo), 0.0))
    return {"n": n, "D": D, "p": kolmogorov_p(D, n), "sim_sample": int(len(sims))}


def poisson_cdf(k: int, mu: float) -> float:
    if k < 0:
        return 0.0
    if mu <= 0:
        return 1.0
    term = math.exp(-mu)
    s = term
    for i in range(1, k + 1):
        term *= mu / i
        s += term
        if term < 1e-300 and i > mu:
            break
    return min(1.0, s)


def poisson_sf_ge(n: int, mu: float) -> float:
    """P(Poisson(mu) >= n)."""
    if n <= 0:
        return 1.0
    if mu <= 0:
        return 0.0
    # sum from n upward in log space
    lt = -mu + n * math.log(mu) - math.lgamma(n + 1)
    s, t, i = 0.0, math.exp(lt), n
    while True:
        s += t
        i += 1
        t *= mu / i
        if t < 1e-18 * max(s, 1e-300) and i > mu:
            break
        if i > n + 100000:
            break
    return min(1.0, s)


# ==========================================================================================
# G-NB-R simulation engine

def draw_counts(rng, means: np.ndarray, D: float, size: tuple) -> np.ndarray:
    """NB with mean `means` (broadcast on the last axis) and variance D * mean; Poisson at D == 1.
    Zero means give zero counts."""
    means = np.asarray(means, dtype=float)
    out = np.zeros(size + means.shape, dtype=np.int64) if means.ndim else np.zeros(size, dtype=np.int64)
    if means.ndim == 0:
        if means <= 0:
            return out
        if D <= 1.0:
            return rng.poisson(float(means), size=size)
        return rng.negative_binomial(float(means) / (D - 1), 1.0 / D, size=size)
    pos = means > 0
    if not pos.any():
        return out
    mp = means[pos]
    if D <= 1.0:
        out[..., pos] = rng.poisson(mp, size=size + mp.shape)
    else:
        out[..., pos] = rng.negative_binomial(mp / (D - 1), 1.0 / D, size=size + mp.shape)
    return out


class Group:
    """One (family, class, m, rung) of the generator: per-curve null means m_j and D."""

    def __init__(self, key: tuple, curves: list, mj: list, D: float, masks: dict | None = None):
        self.key = key
        self.curves = list(curves)
        self.mj = np.asarray(mj, dtype=float)
        self.D = float(D)
        self.masks = {"all": np.ones(len(self.curves), dtype=bool)}
        for k, v in (masks or {}).items():
            self.masks[k] = np.asarray(v, dtype=bool)

    def M(self, mask="all") -> float:
        return float(self.mj[self.masks[mask]].sum())


def simulate_groups(groups: list[Group], arms_of_group: dict, reps: int, rng) -> dict:
    """Per group: S (reps, 3) random-arm sums and Q (reps,) sum_j s_j^2 for every mask, and the
    null sum of every listed pseudo-arm (reps,).  Fixed order: groups as given, then arms."""
    out = {}
    for g in groups:
        n = len(g.curves)
        res = {"S": {}, "Q": {}, "arm": {}}
        if n == 0:
            for mk in g.masks:
                res["S"][mk] = np.zeros((reps, 3), dtype=np.int64)
                res["Q"][mk] = np.zeros(reps)
        else:
            chunk = max(1, min(reps, 6_000_000 // (3 * n)))
            S = {mk: np.zeros((reps, 3), dtype=np.int64) for mk in g.masks}
            Q = {mk: np.zeros(reps) for mk in g.masks}
            for st in range(0, reps, chunk):
                k = min(chunk, reps - st)
                X = draw_counts(rng, g.mj, g.D, (k, 3))  # (k, 3, n)
                var = X.var(axis=1, ddof=1)  # (k, n)
                for mk, msk in g.masks.items():
                    S[mk][st:st + k] = X[:, :, msk].sum(axis=2)
                    Q[mk][st:st + k] = var[:, msk].sum(axis=1)
            res["S"], res["Q"] = S, Q
        for arm, mk in arms_of_group.get(g.key, []):
            # a sum of NB(m_j / (D - 1), 1 / D) over curves is NB(M / (D - 1), 1 / D)
            res["arm"][(arm, mk)] = draw_counts(rng, np.float64(g.M(mk)), g.D, (reps,))
        out[g.key] = res
    return out


def z_stat(CA, CR, V):
    CA = np.asarray(CA, dtype=float)
    CR = np.asarray(CR, dtype=float)
    V = np.maximum(np.asarray(V, dtype=float), CR)
    SD = np.sqrt(V * 4.0 / 3.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (CA - CR) / SD
    z = np.where(SD > 0, z, np.where(CA > CR, np.inf, np.where(CA < CR, -np.inf, 0.0)))
    return z


def cell_null_parts(sim: dict, parts: list) -> tuple:
    """parts: [(group_key, mask)] -> (C_R, V_raw) arrays over replicates."""
    CR = 0.0
    Q = 0.0
    for gk, mk in parts:
        CR = CR + sim[gk]["S"][mk].mean(axis=1)
        Q = Q + sim[gk]["Q"][mk]
    return np.asarray(CR, dtype=float), np.asarray(Q, dtype=float)


def cell_arm_sum(sim: dict, arm: str, parts: list) -> np.ndarray:
    A = 0
    for gk, mk in parts:
        A = A + sim[gk]["arm"][(arm, mk)]
    return np.asarray(A, dtype=np.int64)


def planted(rng, base: np.ndarray, kappa: float, M: float, D: float, kind: str) -> np.ndarray:
    """Structured-arm count with excess at kappa: base + Poisson((k-1)M) or + NB((k-1)M, D);
    kappa < 1: binomial thinning of base."""
    if kappa == 1.0:
        return base
    if kappa < 1.0:
        return rng.binomial(base, kappa)
    ex = (kappa - 1.0) * M
    if ex <= 0:
        return base
    if kind == "poisson" or D <= 1.0:
        return base + rng.poisson(ex, size=base.shape)
    return base + rng.negative_binomial(ex / (D - 1), 1.0 / D, size=base.shape)


# ==========================================================================================
# cell bookkeeping shared by p0 / calibrate / unmask

def fam1_cells() -> list[tuple]:
    return [(a, c, m) for (c, m) in FAM1_CM for a in FAM1_ARMS]


def cell_id(arm, cls, m, rungs) -> str:
    r = "band" if tuple(rungs) == BAND else "-".join(str(x) for x in rungs)
    return f"{arm}|{cls}{m}|{r}"


def build_groups_from_spec(spec: dict) -> list[Group]:
    gs = []
    for g in spec:
        gs.append(Group(tuple(g["key"]), g["curves"], g["mj"], g["D"], g.get("masks")))
    return gs


def seeded(i: int):
    return np.random.default_rng(np.random.SeedSequence([SEED_ROOT, i]))


def family_sim(groups: list[Group], cells: list[dict], reps: int, i: int, keep_parts=False) -> dict:
    """One seed family: simulate the groups (fixed order), then every cell's null z (and, with
    keep_parts, C_R, V and the arm's null sum)."""
    rng = seeded(i)
    sim = simulate_groups(groups, arms_needed(cells), reps, rng)
    res = {"z": {}, "CR": {}, "V": {}, "A": {}, "rng": rng}
    for c in cells:
        CR, Q = cell_null_parts(sim, c["parts"])
        A = cell_arm_sum(sim, c["arm"], c["parts"])
        res["z"][c["id"]] = z_stat(A, CR, Q)
        if keep_parts:
            res["CR"][c["id"]], res["V"][c["id"]], res["A"][c["id"]] = CR, Q, A
    return res


def run_family_sims(groups: list[Group], arms_of_group: dict, cells: list[dict], reps: int,
                    families=range(N_SEED_FAMILIES), want_arm_null=False):
    """{family: family_sim(...)} for every seed family (z only unless want_arm_null)."""
    return {i: family_sim(groups, cells, reps, i, keep_parts=want_arm_null) for i in families}


def arms_needed(cells: list[dict]) -> dict:
    need = defaultdict(set)
    for c in cells:
        for gk, mk in c["parts"]:
            need[tuple(gk)].add((c["arm"], mk))
    return {k: sorted(v) for k, v in need.items()}


def excess_draw(rng, gbk: dict, cell: dict, kappa: float, kind: str, reps: int) -> np.ndarray:
    """Planted excess of one cell at kappa >= 1 (Poisson- or compound-planted, per group)."""
    ex = np.zeros(reps, dtype=np.int64)
    for gk, mk in cell["parts"]:
        g = gbk[tuple(gk)]
        ex = ex + planted(rng, np.zeros(reps, dtype=np.int64), kappa, g.M(mk), g.D, kind)
    return ex


def power_of_cell(groups_by_key: dict, cell: dict, t: float, kappa: float, reps_per_family: int,
                  families=range(N_SEED_FAMILIES)) -> dict:
    """P(z > t) at kappa under Poisson- and compound-planted excess (seed-averaged)."""
    pw = {"poisson": [], "compound": []}
    gl = [groups_by_key[tuple(gk)] for gk, _ in cell["parts"]]
    for i in families:
        res = family_sim(gl, [cell], reps_per_family, i, keep_parts=True)
        CR, Q, base = res["CR"][cell["id"]], res["V"][cell["id"]], res["A"][cell["id"]]
        rng = res["rng"]  # the seed family's stream continues for the planted excess
        for kind in ("poisson", "compound"):
            z = z_stat(base + excess_draw(rng, groups_by_key, cell, kappa, kind, reps_per_family), CR, Q)
            pw[kind].append(float(np.mean(z > t)))
    return {k: float(np.mean(v)) for k, v in pw.items()} | {"per_family": pw}


def xrel_of_cell(groups_by_key: dict, cell: dict, t: float, reps_per_family: int,
                 families=range(N_SEED_FAMILIES)) -> dict:
    """Smallest kappa on XREL_GRID with simulated P(z > t) >= 0.5 (Poisson- and compound-
    planted); the null draws are shared across the grid within a seed family."""
    gl = [groups_by_key[tuple(gk)] for gk, _ in cell["parts"]]
    powers = {"poisson": np.zeros(len(XREL_GRID)), "compound": np.zeros(len(XREL_GRID))}
    for i in families:
        res = family_sim(gl, [cell], reps_per_family, i, keep_parts=True)
        CR, Q, base = res["CR"][cell["id"]], res["V"][cell["id"]], res["A"][cell["id"]]
        rng = res["rng"]  # the seed family's stream continues for the planted excess
        for kind in ("poisson", "compound"):
            for gi, kappa in enumerate(XREL_GRID):
                z = z_stat(base + excess_draw(rng, groups_by_key, cell, kappa, kind, reps_per_family), CR, Q)
                powers[kind][gi] += float(np.mean(z > t)) / len(families)
    out = {}
    for kind in ("poisson", "compound"):
        hit = [k for k, p in zip(XREL_GRID, powers[kind]) if p >= 0.5]
        out[kind] = hit[0] if hit else None
    xs = [out["poisson"], out["compound"]]
    out["X_rel"] = None if any(v is None for v in xs) else max(xs)
    out["power_curve"] = {kind: [round(float(p), 4) for p in powers[kind]] for kind in powers}
    return out


def tstar_from_sims(fs: dict, fam_ids: list[str], q: float = 0.95) -> dict:
    per = []
    for i, res in sorted(fs.items()):
        mx = np.max(np.vstack([res["z"][cid] for cid in fam_ids]), axis=0)
        per.append(float(np.quantile(mx, q)))
    return {"t": float(np.mean(per)), "per_seed_family": per, "spread": float(max(per) - min(per))}


# ==========================================================================================
# P0 (R11)

ARCH_RUNS = ("RUN-PFDR-1b78f7-census-m3", "RUN-PFDR-1b78f7-census-m4", "RUN-PFDR-1b78f7-census-m5")


def archived_layout(archived_runs: str) -> dict:
    base = absp(archived_runs)
    m3 = os.path.join(base, "RUN-PFDR-1b78f7-census-m3")
    m4 = os.path.join(base, "RUN-PFDR-1b78f7-census-m4", "merged")
    m5 = os.path.join(base, "RUN-PFDR-1b78f7-census-m5")
    return {3: {"rows": os.path.join(m3, "rows.jsonl.gz"), "hfile": os.path.join(m3, "harvest-rows.jsonl.gz")},
            4: {"rows": os.path.join(m4, "rows.jsonl.gz"),
                "hmap": json.load(open(os.path.join(m4, "merge-report.json")))["harvest_rows_map"]},
            5: {"rows": os.path.join(m5, "rows.jsonl.gz"),
                "hmap": json.load(open(os.path.join(m5, "merge-report.json")))["harvest_rows_map"]}}


def random_only(arm: str | None) -> bool:
    return arm is not None and arm.startswith("random_")


def load_archived_random(archived_runs: str, log: ArmLog) -> tuple[dict, dict]:
    """Archived random-arm instance rows, and per instance the CC-1 / CC-1b recounts of every
    (class, scope in {stop, A_fix}) computed while streaming its harvest rows (an instance's rows
    are contiguous in each archived file; a re-entry stops the run).  Only counts are kept."""
    lay = archived_layout(archived_runs)
    rows = {}
    for m in (3, 4, 5):
        for r in iter_lines(lay[m]["rows"], random_only, log):
            rows[key5(r)] = r
    files = defaultdict(set)
    for k in rows:
        b, c, m, arm, mode = k
        if m == 3:
            files[lay[3]["hfile"]].add(k)
        else:
            ent = lay[m]["hmap"].get(json.dumps(["main", m, b, c, arm, mode]))
            if ent:
                files[absp(ent["harvest_rows_file"])].add(k)
    rec = {}

    def finish(k, buf):
        row = rows[k]
        A = row["harvest"]["attempt_budget_A_fix"]
        fk = "known_log" if row["arm"] == "known_log" else "none"
        out = {"retained": {}, "after_A": {}, "rc": {}}
        for cls in CLASSES:
            rs = [r for r in buf if r["class"] == cls]
            out["retained"][cls] = len(rs)
            out["after_A"][cls] = any(r["attempt"] > A for r in rs)
            out["rc"][(cls, "stop")] = recount(rs, row["N"], cls, fk)
            out["rc"][(cls, "A_fix")] = recount([r for r in rs if r["attempt"] <= A], row["N"], cls, fk)
        rec[k] = out

    for f, keyset in sorted(files.items()):
        cur, buf, done = None, [], set()
        for r in iter_lines(f, random_only, log):
            k = key5(r)
            if k != cur:
                if cur is not None:
                    if cur in keyset:
                        finish(cur, buf)
                    done.add(cur)
                if k in done:
                    raise SystemExit(f"non-contiguous instance rows in {f}: {k}")
                cur, buf = k, []
            if k in keyset:
                buf.append(r)
        if cur is not None and cur in keyset:
            finish(cur, buf)
    for k in rows:
        if k not in rec:
            finish(k, [])
    return rows, rec


def archived_complete(row: dict, rc_rec: dict, cls: str, scope: str) -> bool:
    em = row["harvest"][cls]["at_stop"]["rows_emitted"]
    if rc_rec["retained"][cls] == em:
        return True
    if scope == "A_fix":
        return rc_rec["after_A"][cls]
    return False


def p0x(bundles: str, rows: dict, hrows: dict, log: ArmLog) -> dict:
    # hrows: key -> streamed recount record (load_archived_random)
    """P0X: CC-1b recount of every complete archived random-arm (instance, class, scope) of the
    census m3..m5 runs equals 02_bundles.jsonl `relations` (random arms only, filtered on the raw
    line before parsing)."""
    compared, diffs, skipped, flag_diff = 0, [], Counter(), []
    for b in iter_lines(bundles, random_only, log):
        run = b["file"].split("/")[0]
        if run not in ARCH_RUNS:
            skipped["file outside census m3..m5 (card inputs)"] += 1
            continue
        if not b.get("complete"):
            skipped["fixture complete == false"] += 1
            continue
        k = (b["bits"], b["curve"], b["m"], b["arm"], b["mode"])
        row = rows.get(k)
        if row is None:
            diffs.append({"key": list(k), "class": b["class"], "scope": b["scope"], "reason": "instance not found"})
            continue
        scope = "A_fix" if b["scope"] == "A_fix" else "stop"
        mine_complete = archived_complete(row, hrows[k], b["class"], scope)
        if not mine_complete:
            flag_diff.append({"key": list(k), "class": b["class"], "scope": scope})
        rc = hrows[k]["rc"][(b["class"], scope)]
        compared += 1
        if rc["relations_distinct_sign"] != b["relations"]:
            diffs.append({"key": list(k), "class": b["class"], "scope": scope, "reason": "relation count differs",
                          "recount_sign_only": rc["relations_distinct_sign"], "fixture": b["relations"]})
    return {"gate": "P0X", "pass": not diffs and compared > 0, "compared": compared,
            "differences": diffs, "difference_count": len(diffs), "skipped": dict(skipped),
            "completeness_flag_differences": flag_diff,
            "rule": ("CC-1b (sign-only) recount of every fixture row with complete == true, random arm, "
                     "file in census m3..m5; scope stop = all rows, A_fix = rows of attempts <= A_fix; "
                     "relation counts only (pair counts are never compared)")}


def p0_estimates(rows: dict, hrows: dict) -> dict:
    """rho1(class, m), D_R(class, m) with its 95% upper bound, Mbar(m) from the archived random arms
    (census mode, 30-32 bits, complete instances), recounted under CC-1."""
    est = {}
    rng = np.random.default_rng(np.random.SeedSequence([SEED_ROOT, 100]))
    for cls in CLASSES:
        for m in (3, 4, 5):
            scope = "A_fix" if cls == "SS" else "stop"
            per = {}  # (bits, c, fam) -> [(n_rel, mu_model_pairs, pairs_rows, mean_pairs_model)]
            sum_rel = sum_pairs = 0
            inst = []
            for k, row in rows.items():
                b, c, mm, arm, mode = k
                if mm != m or mode != "census" or b not in BAND or row.get("status") != "completed_valid":
                    continue
                if not archived_complete(row, hrows[k], cls, scope):
                    continue
                rc = hrows[k]["rc"][(cls, scope)]
                N = row["N"]
                if cls == "SS":
                    X = row["harvest"]["SS"]["at_A_fix"]["formally_distinct_encodings"]
                    mp = mu_pairs("SS", N, X=X)
                else:
                    Ep = row["harvest"]["table"]["formally_distinct_tails"]
                    mp = mu_pairs(cls, N, Ep=Ep, s=row["fb_size"])
                inst.append({"key": k, "fam": FAMILY_OF[arm], "rel": rc["relations_nonformal"],
                             "pairs_rows": rc["relation_pairs"] - rc["relation_pairs_zero"], "mu_pairs": mp})
                sum_rel += rc["relations_nonformal"]
                sum_pairs += rc["relation_pairs"] - rc["relation_pairs_zero"]
            if not inst:
                est[f"{cls}{m}"] = {"instances": 0}
                continue
            if cls == "SS":
                mbar = sum_pairs / sum_rel if sum_rel else None
                model = [i["mu_pairs"] / mbar if mbar else 0.0 for i in inst]
            else:
                mbar = None
                model = [i["mu_pairs"] / MGEN[cls][H_OF_M[m]] for i in inst]
            rho1 = sum_rel / sum(model) if sum(model) > 0 else None
            # triples (curve, family) of the three randoms
            trip = defaultdict(list)
            for i in inst:
                trip[(i["key"][0], i["key"][1], i["fam"])].append(i["rel"])
            trips = [v for v in trip.values() if len(v) == 3]
            s2 = np.array([np.var(v, ddof=1) for v in trips])
            nb = np.array([np.mean(v) for v in trips])
            D_hat = float(s2.sum() / nb.sum()) if len(trips) and nb.sum() > 0 else None
            ub = None
            if len(trips) >= 2 and nb.sum() > 0:
                idx = rng.integers(0, len(trips), size=(BOOT_REPS, len(trips)))
                with np.errstate(divide="ignore", invalid="ignore"):
                    bs = s2[idx].sum(axis=1) / nb[idx].sum(axis=1)
                bs = bs[np.isfinite(bs)]
                ub = float(np.quantile(bs, 0.95))
            est[f"{cls}{m}"] = {"instances": len(inst), "triples": len(trips), "scope": scope,
                                "rho1": rho1, "D_R_hat": D_hat, "D_R_ub95": ub, "Mbar": mbar,
                                "sum_relations": sum_rel, "sum_pairs_from_rows": sum_pairs}
    return est


def design_groups(curves: list[dict], n_by_rung: dict, est: dict, cls: str, m: int,
                  fam: str) -> list[Group]:
    """P0 groups (family, class, m, rung) at the design curves: means rho1 x model."""
    e = est[f"{cls}{m}"]
    D = max(e["D_R_ub95"] if e.get("D_R_ub95") is not None else 1.0, 1.0) * P0_D_FACTOR[cls]
    out = []
    by_bits = defaultdict(list)
    for r in curves:
        by_bits[r["bits"]].append(r)
    for b in RUNGS:
        n = n_by_rung[b]
        sel = sorted(by_bits[b], key=lambda r: r["curve"])[:n]
        if len(sel) < n:
            raise SystemExit(f"design curves missing at {b} bits: need {n}, have {len(sel)}")
        mj = []
        for r in sel:
            sz = r["sizes"][str(m)]
            s = sz["s_sub"] if fam == "SUB" else sz["s_dick"]
            if cls == "SS":
                mu = mu_rel_model("SS", m, r["N"], X=r["X_fix"], mbar_ss=e["Mbar"])
            else:
                mu = mu_rel_model(cls, m, r["N"], Ep=stored_tails(s, H_OF_M[m]), s=s)
            mj.append(e["rho1"] * mu)
        out.append(Group((fam, cls, m, b), [r["curve"] for r in sel], mj, D))
    return out


def uniform_ECR(curves, n_by_rung, est, cls, m, fam) -> float:
    e = est[f"{cls}{m}"]
    tot = 0.0
    by_bits = defaultdict(list)
    for r in curves:
        by_bits[r["bits"]].append(r)
    for b in BAND:
        for r in sorted(by_bits[b], key=lambda r: r["curve"])[:n_by_rung[b]]:
            sz = r["sizes"][str(m)]
            s = sz["s_sub"] if fam == "SUB" else sz["s_dick"]
            if cls == "SS":
                tot += mu_rel_model("SS", m, r["N"], X=r["X_fix"], mbar_ss=e["Mbar"])
            else:
                tot += mu_rel_model(cls, m, r["N"], Ep=stored_tails(s, H_OF_M[m]), s=s)
    return tot


def family_cells_for(groups_by_key: dict, cms=FAM1_CM, rungs=BAND, arms=FAM1_ARMS) -> list[dict]:
    cells = []
    for (cls, m) in cms:
        for arm in arms:
            fam = FAMILY_OF[arm]
            parts = [((fam, cls, m, b), "all") for b in rungs if (fam, cls, m, b) in groups_by_key]
            cells.append({"id": cell_id(arm, cls, m, rungs), "arm": arm, "cls": cls, "m": m,
                          "parts": parts})
    return cells


def p0_design_sim(curves, n_design, est, reps) -> tuple:
    groups = []
    for (cls, m) in FAM1_CM:
        panel = PANEL_OF_CLASS[cls]
        for fam in ("SUB", "DICK"):
            groups += design_groups(curves, n_design[panel][m], est, cls, m, fam)
    gbk = {g.key: g for g in groups}
    cells = family_cells_for(gbk)
    fs = run_family_sims(groups, arms_needed(cells), cells, reps)
    ts = tstar_from_sims(fs, [c["id"] for c in cells])
    return groups, gbk, cells, ts


def declared_n(spec: dict) -> dict:
    cells = spec["experiment"]["cells"]
    out = {}
    for panel, key in (("table", "table_panel_T"), ("search", "search_panel_S")):
        out[panel] = {}
        for mk, v in cells[key]["curves_per_rung_declared"].items():
            m = int(mk[1:])
            d = {b: v["b20_to_b28"] for b in (20, 22, 24, 26, 28)}
            d[30], d[32] = v["b30"], v["b32"]
            out[panel][m] = d
    return out


def cmd_p0(a) -> int:
    import yaml
    out = absp(a.out)
    for f in ("design.json", "power.json", "p0x-report.json"):
        if os.path.exists(os.path.join(out, f)):
            print(f"refusing: {out}/{f} exists", file=sys.stderr)
            return 3
    log = ArmLog()
    spec = yaml.safe_load(open(absp(a.spec)))
    curves = list(iter_lines(absp(a.curves)))
    rows, hrows = load_archived_random(a.archived_runs, log)
    p0x_rep = p0x(absp(a.bundles), rows, hrows, log)
    p0x_rep["arm_read_log"] = log.as_json()
    p0x_rep["parsed_arms"] = sorted(log.parsed_arms())
    dump(os.path.join(out, "p0x-report.json"), p0x_rep)
    est = p0_estimates(rows, hrows)
    decl = declared_n(spec)
    reps = a.reps
    t0 = now()
    # (3) t*_plan at the declared design
    _, gbk, cells, ts_decl = p0_design_sim(curves, decl, est, reps)
    # (4) power per FAM-1 cell; RULE per (panel, m), evaluated with t*_plan of the declared design
    final_n = {p: {m: dict(d) for m, d in pm.items()} for p, pm in decl.items()}
    rule_log = []
    unattainable = []
    for panel in ("table", "search"):
        for m in (3, 4, 5):
            pcells = [c for c in cells if PANEL_OF_CLASS[c["cls"]] == panel and c["m"] == m]
            chosen = None
            evals = []
            for mult in (1.0,) + RAISE_MULTIPLIERS:
                nb = {b: (math.ceil(mult * decl[panel][m][b]) if b in BAND else decl[panel][m][b]) for b in RUNGS}
                groups_t = {}
                for (cls, mm) in FAM1_CM:
                    if PANEL_OF_CLASS[cls] != panel or mm != m:
                        continue
                    for fam in ("SUB", "DICK"):
                        for g in design_groups(curves, nb, est, cls, m, fam):
                            groups_t[g.key] = g
                pw = {}
                ok = True
                for c in pcells:
                    kt = KAPPA_TARGET[(c["cls"], c["m"])]
                    pr = power_of_cell(groups_t, c, ts_decl["t"], kt, POWER_REPS_PER_FAMILY)
                    governing = min(pr["poisson"], pr["compound"])
                    pw[c["id"]] = {"kappa_target": kt, "poisson": pr["poisson"], "compound": pr["compound"],
                                   "governing": governing}
                    ok = ok and governing >= 0.5
                evals.append({"multiplier": mult, "n_b30": nb[30], "n_b32": nb[32], "all_cells_met": ok,
                              "power": pw})
                if ok:
                    chosen = (mult, nb)
                    break
            if chosen is None:
                mult = 3.0
                nb = {b: (math.ceil(3.0 * decl[panel][m][b]) if b in BAND else decl[panel][m][b]) for b in RUNGS}
                unattainable.append({"panel": panel, "m": m})
            else:
                mult, nb = chosen
            final_n[panel][m] = nb
            rule_log.append({"panel": panel, "m": m, "declared_b30": decl[panel][m][30],
                             "declared_b32": decl[panel][m][32], "chosen_multiplier": mult,
                             "final_b30": nb[30], "final_b32": nb[32], "raised": mult > 1.0,
                             "raise_reason": (None if mult == 1.0 else
                                              "a target cell's predicted power < 0.5 at the declared n "
                                              "(frozen P0 RULE)"),
                             "target_unattainable_by_design": chosen is None, "evaluations": evals})
    # final design: t*_plan, power, X_rel, E[C_R]
    groups_f, gbk_f, cells_f, ts_final = p0_design_sim(curves, final_n, est, reps)
    cell_rep = {}
    design_stop = []
    for c in cells_f:
        kt = KAPPA_TARGET[(c["cls"], c["m"])]
        pr = power_of_cell(gbk_f, c, ts_final["t"], kt, POWER_REPS_PER_FAMILY)
        xr = xrel_of_cell(gbk_f, c, ts_final["t"], POWER_REPS_PER_FAMILY)
        fam = FAMILY_OF[c["arm"]]
        ecr = uniform_ECR(curves, final_n[PANEL_OF_CLASS[c["cls"]]][c["m"]], est, c["cls"], c["m"], fam)
        un = [u for u in unattainable if u["panel"] == PANEL_OF_CLASS[c["cls"]] and u["m"] == c["m"]]
        cell_rep[c["id"]] = {"kappa_target": kt, "power_poisson": pr["poisson"], "power_compound": pr["compound"],
                             "power_governing": min(pr["poisson"], pr["compound"]),
                             "X_rel_poisson": xr["poisson"], "X_rel_compound": xr["compound"],
                             "X_rel": xr["X_rel"], "E_C_R_uniform": ecr,
                             "stated_target": (xr["X_rel"] if un else kt),
                             "target_unattainable_by_design": bool(un)}
        if ecr < 100:
            design_stop.append({"cell": c["id"], "E_C_R_uniform": ecr, "reason": "CC-9: E[C_R] < 100"})
    # curves, jobs, disk and CPU
    by_bits = defaultdict(list)
    for r in curves:
        by_bits[r["bits"]].append(r)
    used = {}
    for panel in ("table", "search"):
        for m in (3, 4, 5):
            for b in RUNGS:
                for r in sorted(by_bits[b], key=lambda r: r["curve"])[:final_n[panel][m][b]]:
                    used[(b, r["curve"])] = r
    jobs = {"table": [], "search": []}
    for m in (3, 4, 5):
        for b in RUNGS:
            n = final_n["table"][m][b]
            for c0 in range(10, 10 + n, 100):
                jobs["table"].append({"m": m, "bits": b, "curve_offset": c0, "curves": min(100, 10 + n - c0)})
            n = final_n["search"][m][b]
            for c0 in range(10, 10 + n, 10):
                jobs["search"].append({"m": m, "bits": b, "curve_offset": c0, "curves": min(10, 10 + n - c0)})
    for b in (20, 24):
        jobs["table"].append({"m": 3, "bits": b, "curve_offset": 10, "curves": 10, "pc1": True})
    disk = expected_disk(final_n, by_bits, est)
    cpu = expected_cpu(final_n)
    if disk["total_bytes_modeled"] > 1.5e9:
        design_stop.append({"reason": "expected package size above 1.5 GB", "bytes": disk["total_bytes_modeled"]})
    design = {"what": "EXP-PFDR-011cd0 P0 design (R11)", "created_at": now(), "started_at": t0,
              "final_n": {p: {str(m): {str(b): v for b, v in d.items()} for m, d in pm.items()} for p, pm in final_n.items()},
              "declared_n": {p: {str(m): {str(b): v for b, v in d.items()} for m, d in pm.items()} for p, pm in decl.items()},
              "rule": rule_log, "target_unattainable_by_design": unattainable,
              "t_star_plan": ts_final, "t_star_plan_declared_design": ts_decl,
              "estimates": est, "cells": cell_rep, "design_stop": design_stop,
              "curves": [used[k] for k in sorted(used)],
              "jobs": jobs, "expected_disk": disk, "expected_cpu": cpu,
              "simulation": {"generator": "G-NB-R (A-CAL) at the design curves, means rho1 x model, "
                                          "D = max(ub95, 1) x 1.2 (TT/TB) or x 1.5 (SS)",
                             "reps_per_seed_family": reps, "seed_families": N_SEED_FAMILIES,
                             "power_reps_per_seed_family": POWER_REPS_PER_FAMILY,
                             "seed_rule": "numpy SeedSequence([0x011cd0, i]), i = 0..4"},
              "p0x_pass": p0x_rep["pass"]}
    dump(os.path.join(out, "design.json"), design)
    dump(os.path.join(out, "power.json"), {"cells": cell_rep, "rule": rule_log, "t_star_plan": ts_final})
    print(json.dumps({"p0x_pass": p0x_rep["pass"], "p0x_compared": p0x_rep["compared"],
                      "t_star_plan": ts_final["t"], "final_n": design["final_n"],
                      "design_stop": design_stop, "unattainable": unattainable}))
    return 0 if (p0x_rep["pass"] and not design_stop) else 1


def expected_disk(final_n, by_bits, est) -> dict:
    """Modeled bytes (not measured): rows x bytes/row of the spec's budget (60 B TT/TB rows,
    100 B SS rows, 3 kB per census row, 1.5 kB per staircase record, 25 B per sampled base point)."""
    tot = {"table_rows": 0.0, "search_rows": 0.0, "census_rows": 0.0, "staircases": 0.0, "bases": 0.0, "pc1": 0.0}
    for m in (3, 4, 5):
        h = H_OF_M[m]
        arms_t = 12 if m == 3 else 11
        for b in RUNGS:
            for r in sorted(by_bits[b], key=lambda r: r["curve"])[:final_n["table"][m][b]]:
                s = r["sizes"][str(m)]["s_sub"]
                Ep = stored_tails(s, h)
                pairs = Ep * (Ep - 1) / r["N"] + 2 * Ep * s / r["N"]
                tot["table_rows"] += arms_t * pairs * 60
                tot["census_rows"] += arms_t * 3000
                tot["staircases"] += arms_t * 3 * 1500
                if r["curve"] % 10 == 0:
                    tot["bases"] += arms_t * s * 25
            for r in sorted(by_bits[b], key=lambda r: r["curve"])[:final_n["search"][m][b]]:
                X = r["X_fix"]
                tot["search_rows"] += 11 * (X * (X - 1) / r["N"]) * 100
                tot["census_rows"] += 11 * 3000
                tot["staircases"] += 11 * 3 * 1500
    for b in (20, 24):
        for r in sorted(by_bits[b], key=lambda r: r["curve"])[:10]:
            s = r["sizes"]["3"]["s_sub"]
            tot["pc1"] += 2 * s * s * 60
    tot["regression_and_checks"] = 5e7
    return {"bytes_by_part_modeled": tot, "total_bytes_modeled": float(sum(tot.values())),
            "label": "modeled (not measured); compressed sizes assumed per row as stated"}


def expected_cpu(final_n) -> dict:
    """Modeled CPU seconds (not measured): table instance 1.0 s (m3 30-32), 0.1 s (m4), 0.3 s (m5),
    0.2 s below 30 bits; search instance 60 s at 30-32 bits, 10 s below."""
    sec = 0.0
    for m in (3, 4, 5):
        tt = {3: 1.0, 4: 0.1, 5: 0.3}[m]
        for b in RUNGS:
            sec += (12 if m == 3 else 11) * final_n["table"][m][b] * (tt if b in BAND else 0.2)
            sec += 11 * final_n["search"][m][b] * (60 if b in BAND else 10)
    return {"cpu_seconds_modeled": sec, "label": "modeled (not measured)"}


# ==========================================================================================
# loading panel data (R15 / R16)

def view_run(runs_dir: str, name: str) -> str:
    return os.path.join(runs_dir, name)


def load_panel(runs_dir: str, run_name: str, allowed, log: ArmLog) -> dict:
    """Canonical rows of a panel run (through the view), arm-filtered before parsing."""
    rd = view_run(runs_dir, run_name)
    rows = {}
    for r in iter_lines(os.path.join(rd, "rows.jsonl.gz"), allowed, log):
        rows[key5(r)] = r
    return rows


def inst_counts(row: dict, cls: str) -> dict | None:
    """CC-7 counts of one instance and class from its harvest block (in-process, G-REL-gated)."""
    if row.get("status") != "completed_valid" or not row.get("harvest"):
        return None
    h = row["harvest"]
    st = h[cls]["at_stop"]
    d = {"N": row["N"], "s": row["fb_size"], "U": h["U"], "irank": st["informative_rank"],
         "R_star_stop": st["R_star"], "log2N": row["log2N"], "fb_kind": row["fb"]}
    if cls == "SS":
        xf = h["SS"]["at_X_fix"]
        d.update({"n": xf["relations_nonformal"], "raw": xf["relations_distinct"],
                  "sign": xf["relations_distinct_sign"], "pairs": xf["pairs_nonformal"],
                  "X": xf["formally_distinct_encodings"], "X_fix": xf["X_fix"], "censored": xf["censored"],
                  "hist": xf["multiplicity_histogram"], "at_stop_relations": st["relations_nonformal"]})
    else:
        d.update({"n": st["relations_nonformal"], "raw": st["relations_distinct"],
                  "sign": st["relations_distinct_sign"], "pairs": st["pairs_nonformal"],
                  "Ep": h["table"]["formally_distinct_tails"], "hist": st["multiplicity_histogram"]})
    return d


def design_curve_lists(design: dict) -> dict:
    """(panel, m, rung) -> list of curve seeds of the final design."""
    out = {}
    for panel in ("table", "search"):
        for m in (3, 4, 5):
            for b in RUNGS:
                n = design["final_n"][panel][str(m)][str(b)]
                out[(panel, m, b)] = list(range(10, 10 + n))
    return out


def size_unmatched_from_design(design: dict) -> dict:
    """CC-6 unmatched_size from design quantities: (arm, m, bits, c) -> True when |F_A| != s."""
    out = {}
    for r in design["curves"]:
        for m in (3, 4, 5):
            sz = r["sizes"][str(m)]
            out[("subgroup", m, r["bits"], r["curve"])] = sz["F_sub"] != sz["s_sub"]
            out[("dickson", m, r["bits"], r["curve"])] = sz["F_dick"] != sz["s_dick"]
    return out


def build_calibration_groups(design: dict, panels: dict, visible_arms: set) -> tuple:
    """Groups (family, class, m, rung) from the random arms (r0..r2) of the realised design:
    CC-6 family-wide drops (failed_infrastructure / missing row of any VISIBLE arm of the family on a
    curve), m_j = rho1_hat(class, m, rung) x mu_model(j) (TT/TB) or the rung mean of the three
    randoms (SS), D = max(D_hat, 1)."""
    clists = design_curve_lists(design)
    groups, info = [], {}
    rho1 = {}
    # rho1_hat(class, m, rung), pooled over both families' randoms
    for cls in ("TT", "TB"):
        for m in (3, 4, 5):
            for b in RUNGS:
                obs = mod = 0.0
                for fam in ("SUB", "DICK"):
                    for c in clists[("table", m, b)]:
                        for arm in RANDOMS[fam]:
                            d = inst_counts(panels["table"].get((b, c, m, arm, "table"), {}), cls)
                            if d is None:
                                continue
                            obs += d["n"]
                            mod += mu_rel_model(cls, m, d["N"], Ep=d["Ep"], s=d["s"])
                rho1[(cls, m, b)] = obs / mod if mod > 0 else None
    for cls in CLASSES:
        panel = PANEL_OF_CLASS[cls]
        mode = "table" if panel == "table" else "search"
        for m in (3, 4, 5):
            for b in RUNGS:
                for fam in ("SUB", "DICK"):
                    arms_vis = [a for a in (RANDOMS[fam] + (KNOWN_NULL[fam],) + STRUCT_OF_FAMILY[fam]
                                            + (("planted_sub",) if (fam == "SUB" and m == 3 and panel == "table") else ()))
                                if a in visible_arms]
                    kept, dropped, rc = [], [], []
                    for c in clists[(panel, m, b)]:
                        bad = []
                        for arm in arms_vis:
                            r = panels[panel].get((b, c, m, arm, mode))
                            if r is None or r.get("status") != "completed_valid":
                                bad.append(arm)
                        if bad:
                            dropped.append({"curve": c, "arms": bad})
                            continue
                        cnt = [inst_counts(panels[panel][(b, c, m, arm, mode)], cls) for arm in RANDOMS[fam]]
                        kept.append(c)
                        rc.append(cnt)
                    n = np.array([[x["n"] for x in cnt] for cnt in rc], dtype=float).reshape(-1, 3)
                    s2 = n.var(axis=1, ddof=1) if len(n) else np.zeros(0)
                    nbar = n.mean(axis=1) if len(n) else np.zeros(0)
                    D_hat = float(s2.sum() / nbar.sum()) if len(n) and nbar.sum() > 0 else None
                    D = max(D_hat if D_hat is not None else 1.0, 1.0)
                    if cls == "SS":
                        mean = float(n.mean()) if len(n) else 0.0
                        mj = [mean] * len(kept)
                        mu_model_list = None
                    else:
                        mu_model_list = []
                        for cnt in rc:
                            mus = [mu_rel_model(cls, m, x["N"], Ep=x["Ep"], s=x["s"]) for x in cnt]
                            mu_model_list.append(float(np.mean(mus)))
                        r1 = rho1[(cls, m, b)] or 0.0
                        mj = [r1 * mu for mu in mu_model_list]
                    g = Group((fam, cls, m, b), kept, mj, D)
                    groups.append(g)
                    info[g.key] = {"curves_design": len(clists[(panel, m, b)]), "curves_kept": len(kept),
                                   "dropped_cc6": dropped, "D_hat": D_hat, "D": D,
                                   "rho1_hat": rho1.get((cls, m, b)) if cls != "SS" else None,
                                   "mu_model_mean": (float(np.mean(mu_model_list)) if mu_model_list else None),
                                   "random_counts": n.tolist()}
    return groups, info, rho1


def cells_all(gbk: dict, unmatched: dict, design: dict) -> dict:
    """Every scored cell: FAM-1 band (21), per-rung FAM-1 (147), known-null band (14) and per-rung
    (98), planted (TT3, TB3; band and per rung), CARRY-1.  Parts carry a mask name when CC-6
    unmatched_size drops curves for the arm."""
    out = {"fam1_band": [], "fam1_rung": [], "kn_band": [], "kn_rung": [], "planted": [], "carry": []}

    def parts_for(arm, cls, m, rungs):
        fam = FAMILY_OF[arm]
        parts = []
        for b in rungs:
            g = gbk.get((fam, cls, m, b))
            if g is None:
                continue
            mk = "all"
            if arm in ("subgroup", "dickson"):
                msk = [not unmatched.get((arm, m, b, c), False) for c in g.curves]
                if not all(msk):
                    mk = f"unmatched:{arm}"
                    g.masks[mk] = np.asarray(msk, dtype=bool)
            parts.append(((fam, cls, m, b), mk))
        return parts

    for (cls, m) in FAM1_CM:
        for arm in FAM1_ARMS:
            out["fam1_band"].append({"id": cell_id(arm, cls, m, BAND), "arm": arm, "cls": cls, "m": m,
                                     "rungs": list(BAND), "parts": parts_for(arm, cls, m, BAND)})
            for b in RUNGS:
                out["fam1_rung"].append({"id": cell_id(arm, cls, m, (b,)), "arm": arm, "cls": cls, "m": m,
                                         "rungs": [b], "parts": parts_for(arm, cls, m, (b,))})
        for fam in ("SUB", "DICK"):
            arm = KNOWN_NULL[fam]
            out["kn_band"].append({"id": cell_id(arm, cls, m, BAND), "arm": arm, "cls": cls, "m": m,
                                   "rungs": list(BAND), "parts": parts_for(arm, cls, m, BAND)})
            for b in RUNGS:
                out["kn_rung"].append({"id": cell_id(arm, cls, m, (b,)), "arm": arm, "cls": cls, "m": m,
                                       "rungs": [b], "parts": parts_for(arm, cls, m, (b,))})
    for cls in ("TT", "TB"):
        out["planted"].append({"id": cell_id("planted_sub", cls, 3, BAND), "arm": "planted_sub", "cls": cls,
                               "m": 3, "rungs": list(BAND), "parts": parts_for("planted_sub", cls, 3, BAND)})
        for b in RUNGS:
            out["planted"].append({"id": cell_id("planted_sub", cls, 3, (b,)), "arm": "planted_sub",
                                   "cls": cls, "m": 3, "rungs": [b], "parts": parts_for("planted_sub", cls, 3, (b,))})
    arm, cls, m, b = CARRY1
    out["carry"].append({"id": "CARRY-1|" + cell_id(arm, cls, m, (b,)), "arm": arm, "cls": cls, "m": m,
                         "rungs": [b], "parts": parts_for(arm, cls, m, (b,))})
    return out


def observed_cell(cell: dict, gbk: dict, panels: dict, arm_override: str | None = None,
                  family_drops: set | None = None) -> dict:
    """CC-8 on the data: C_A, C_R, V, SD_null, kappa_rel, z (+ per-curve counts).  family_drops:
    (family, class, m, rung, curve) dropped from every cell of the family (CC-6), e.g. a structured
    arm's failed_infrastructure seen only at unmasking."""
    arm = arm_override or cell["arm"]
    cls, m = cell["cls"], cell["m"]
    panel = PANEL_OF_CLASS[cls]
    mode = "table" if panel == "table" else "search"
    CA = CR = Q = 0.0
    curves = []
    n_used = 0
    for (fam, _, _, b), mk in cell["parts"]:
        g = gbk[(fam, cls, m, b)]
        msk = g.masks[mk]
        for c, use in zip(g.curves, msk):
            if not use or (family_drops and (fam, cls, m, b, c) in family_drops):
                continue
            a = inst_counts(panels[panel].get((b, c, m, arm, mode), {}), cls)
            rs = [inst_counts(panels[panel][(b, c, m, r, mode)], cls) for r in RANDOMS[fam]]
            if a is None:
                curves.append({"bits": b, "curve": c, "missing_arm": True})
                continue
            nr = [x["n"] for x in rs]
            CA += a["n"]
            CR += float(np.mean(nr))
            Q += float(np.var(nr, ddof=1))
            n_used += 1
            curves.append({"bits": b, "curve": c, "A": a["n"], "randoms": nr})
    z = float(z_stat(CA, CR, Q))
    V = max(Q, CR)
    SD = math.sqrt(V * 4 / 3)
    return {"C_A": CA, "C_R": CR, "V": V, "sum_s2": Q, "SD_null": SD,
            "kappa_rel": (CA / CR if CR > 0 else None), "z": z, "curves_used": n_used,
            "per_curve": curves}


# ==========================================================================================
# calibrate (R15)

def a2r_slope(points: list[tuple]) -> float | None:
    """OLS slope of y on x; None with < 2 points."""
    if len(points) < 2:
        return None
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    xm = x.mean()
    den = ((x - xm) ** 2).sum()
    if den == 0:
        return None
    return float(((x - xm) * (y - y.mean())).sum() / den)


def a2r_point(kappa, CR, SD):
    """y_b = log2(max(kappa_b - 1, SE_b)); undefined (excluded) when C_R == 0."""
    if CR is None or CR <= 0:
        return None
    SE = SD / CR
    v = max(kappa - 1.0, SE)
    if v <= 0:
        return None
    return math.log2(v)


def sim_a2r_slopes(fs_family: dict, rung_cells: list[dict], xs_by_cell: dict) -> np.ndarray:
    """Per replicate null A2R slope of one FAM-1 (A, class, m) from its per-rung cells."""
    reps = None
    ys = []
    xv = []
    for c in rung_cells:
        CR = fs_family["CR"][c["id"]]
        V = np.maximum(fs_family["V"][c["id"]], CR)
        A = fs_family["A"][c["id"]]
        SD = np.sqrt(V * 4 / 3)
        with np.errstate(divide="ignore", invalid="ignore"):
            kap = A / CR
            SE = SD / CR
            y = np.log2(np.maximum(kap - 1.0, SE))
        y = np.where(CR > 0, y, np.nan)
        ys.append(y)
        xv.append(xs_by_cell[c["id"]])
        reps = len(CR)
    Y = np.vstack(ys)  # (rungs, reps)
    X = np.array(xv)[:, None] * np.ones((1, reps))
    ok = np.isfinite(Y)
    cnt = ok.sum(axis=0)
    Xm = np.where(ok, X, 0).sum(axis=0) / np.maximum(cnt, 1)
    Ym = np.where(ok, Y, 0).sum(axis=0) / np.maximum(cnt, 1)
    num = np.where(ok, (X - Xm) * (Y - Ym), 0).sum(axis=0)
    den = np.where(ok, (X - Xm) ** 2, 0).sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = num / den
    return np.where((cnt >= 2) & (den > 0), s, np.nan)


def attach_log2N(groups, panels):
    for g in groups:
        fam, cls, m, b = g.key
        panel = PANEL_OF_CLASS[cls]
        mode = "table" if panel == "table" else "search"
        vals = []
        for c in g.curves:
            r = panels[panel].get((b, c, m, RANDOMS[fam][0], mode))
            vals.append(r["log2N"] if r else float("nan"))
        g.log2N = np.array(vals)


def pc1_check(panels: dict) -> dict:
    """A5R PC-1 on known_log (m 3, 20 and 24 bits, curves 10..19, table mode)."""
    out = {"instances": [], "pass": None}
    ok_all = True
    raw_kl = {"TT": 0, "TB": 0}
    raw_rs = {"TT": 0.0, "TB": 0.0}
    for b in (20, 24):
        for c in range(10, 20):
            r = panels["table"].get((b, c, 3, "known_log", "table"))
            ent = {"bits": b, "curve": c}
            if r is None or r.get("status") != "completed_valid":
                ent["problem"] = "known_log instance missing or not completed_valid"
                ok_all = False
                out["instances"].append(ent)
                continue
            h = r["harvest"]
            checks = r.get("checks") or {}
            ent["G6_Fj_eq_jP"] = checks.get("G6_known_log_Fj_eq_jP")
            ent["G6_formal_rank"] = checks.get("G6_known_log_formal_rank")
            for cls in ("TT", "TB"):
                st = h[cls]["at_stop"]
                ent[cls] = {"raw": st["relations_distinct"], "nonformal": st["relations_nonformal"],
                            "informative_rank": st["informative_rank"]}
                raw_kl[cls] += st["relations_distinct"]
                rr = [panels["table"].get((b, c, 3, a, "table")) for a in RANDOMS["SUB"]]
                vals = [x["harvest"][cls]["at_stop"]["relations_distinct"] for x in rr
                        if x and x.get("status") == "completed_valid"]
                raw_rs[cls] += float(np.mean(vals)) if vals else 0.0
                ok_all = ok_all and st["relations_nonformal"] == 0 and st["informative_rank"] == 0
            ok_all = ok_all and bool(ent["G6_Fj_eq_jP"]) and bool(ent["G6_formal_rank"])
            out["instances"].append(ent)
    ratio = {cls: (raw_kl[cls] / raw_rs[cls] if raw_rs[cls] > 0 else None) for cls in ("TT", "TB")}
    tot_ratio = (sum(raw_kl.values()) / sum(raw_rs.values())) if sum(raw_rs.values()) > 0 else None
    out["raw_over_random_sub_mean"] = ratio
    out["raw_over_random_sub_mean_TT_TB_combined"] = tot_ratio
    ratio_ok = tot_ratio is not None and tot_ratio >= 5
    out["pass"] = bool(ok_all and ratio_ok)
    out["rule"] = ("raw (formal-included) TT+TB relation count of known_log over the mean of "
                   "random_sub_r0..r2 on the same curves >= 5 (per class reported beside); nonformal "
                   "relations == 0 and informative rank of TT and TB == 0 on every instance; G6")
    return out


def cmd_calibrate(a) -> int:
    out = absp(a.out)
    for f in ("calibration.json", "arm-read-log.json", "null-tables.npz"):
        if os.path.exists(os.path.join(out, f)):
            print(f"refusing: {out}/{f} exists", file=sys.stderr)
            return 3
    design = json.load(open(absp(a.design)))
    log = ArmLog()
    panels = {"table": load_panel(a.runs_dir, "RUN-PFDR-011cd0-table", blinded_allowed, log),
              "search": load_panel(a.runs_dir, "RUN-PFDR-011cd0-search", blinded_allowed, log)}
    parsed = log.parsed_arms()
    illegal = sorted(x for x in parsed if not blinded_allowed(x))
    dump(os.path.join(out, "arm-read-log.json"),
         {"what": "R15 arm-read log (two-step blinding): arms parsed vs skipped unparsed, per file",
          "filter": "arm read from the raw line by regex before any JSON parse; parsed only if "
                    "random_*, known_null_* or known_log",
          "files": log.as_json(), "parsed_arms": sorted(parsed),
          "structured_or_planted_arm_parsed": bool(illegal), "illegal_parsed_arms": illegal})
    if illegal:
        print(f"I-7: structured arm parsed: {illegal}", file=sys.stderr)
        return 4
    groups, ginfo, rho1 = build_calibration_groups(design, panels, set(parsed))
    attach_log2N(groups, panels)
    gbk = {g.key: g for g in groups}
    unmatched = size_unmatched_from_design(design)
    cells = cells_all(gbk, unmatched, design)
    reps = a.reps
    t0 = now()
    allc = [c for k in ("fam1_band", "fam1_rung", "kn_band", "kn_rung", "carry") for c in cells[k]]
    fam_ids = [c["id"] for c in cells["fam1_band"]]
    carry_id = cells["carry"][0]["id"]
    xs_by_cell = {c["id"]: (float(np.nanmean(np.concatenate([gbk[gk].log2N[gbk[gk].masks[mk]]
                                                             for gk, mk in c["parts"]])))
                            if c["parts"] else float("nan")) for c in cells["fam1_rung"]}
    fam1_rung_sets = {}
    for (cls, m) in FAM1_CM:
        for arm in FAM1_ARMS:
            fam1_rung_sets[f"{arm}|{cls}{m}"] = [c for c in cells["fam1_rung"]
                                                if c["arm"] == arm and c["cls"] == cls and c["m"] == m]
    fs = {}
    zcarry, slopes = [], defaultdict(list)
    kn_band_z = defaultdict(list)
    kn_rung_z = []
    for i in range(N_SEED_FAMILIES):
        res = family_sim(groups, allc, reps, i, keep_parts=True)
        fs[i] = {"z": {cid: res["z"][cid] for cid in fam_ids}}
        zcarry.append(res["z"][carry_id])
        for c in cells["kn_band"]:
            kn_band_z[c["id"]].append(res["z"][c["id"]])
        kn_rung_z.append(np.concatenate([res["z"][c["id"]] for c in cells["kn_rung"]]))
        for fid, rc in fam1_rung_sets.items():
            slopes[fid].append(sim_a2r_slopes(res, rc, xs_by_cell))
        del res
    ts = tstar_from_sims(fs, fam_ids, 0.95)
    tcarry = tstar_from_sims({i: {"z": {carry_id: zcarry[i]}} for i in range(N_SEED_FAMILIES)}, [carry_id], 0.99)
    t = ts["t"]
    # PC-NULL (known-null arms simulated alongside)
    kn_obs = {c["id"]: observed_cell(c, gbk, panels) for c in cells["kn_band"]}
    K_obs = sum(1 for v in kn_obs.values() if v["z"] > t)
    K_null = np.sum(np.vstack([np.concatenate(kn_band_z[c["id"]]) for c in cells["kn_band"]]) > t, axis=0)
    p_K = float(np.mean(K_null >= K_obs))
    kn_rung_obs = {c["id"]: observed_cell(c, gbk, panels) for c in cells["kn_rung"]}
    obs_z = np.array([v["z"] for v in kn_rung_obs.values()])
    ks = ks_against_sample(obs_z, np.concatenate(kn_rung_z))
    pcnull = {"K_obs": K_obs, "K_null_mean": float(K_null.mean()), "P_K_null_ge_K_obs": p_K,
              "i_pass": p_K >= 0.01, "ks": ks, "ii_pass": ks["p"] >= 0.01,
              "pass": bool(p_K >= 0.01 and ks["p"] >= 0.01),
              "known_null_band_cells": {k: {kk: (fin(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "per_curve"}
                                        for k, v in kn_obs.items()},
              "known_null_rung_z": {k: fin(v["z"]) for k, v in kn_rung_obs.items()},
              "rule": "analysis.PC-NULL_rule: (i) P(K_null >= K) >= 0.01; (ii) KS p >= 0.01 (98 per-rung z)"}
    # predicted X_rel at the realised design
    xrel = {}
    for c in cells["fam1_band"] + cells["carry"]:
        tt = tcarry["t"] if c["id"].startswith("CARRY-1") else t
        xrel[c["id"]] = xrel_of_cell(gbk, c, tt, POWER_REPS_PER_FAMILY)
    a2r = {}
    arrays = {}
    for fid, lst in slopes.items():
        sl = np.concatenate(lst)
        arrays["a2r|" + fid] = sl
        fs_ = sl[np.isfinite(sl)]
        a2r[fid] = {"null_mean": float(fs_.mean()) if len(fs_) else None,
                    "null_q95": float(np.quantile(fs_, 0.95)) if len(fs_) else None,
                    "null_finite": int(len(fs_)), "null_total": int(len(sl))}
    for cid in fam_ids:
        arrays["z|" + cid] = np.concatenate([fs[i]["z"][cid] for i in range(N_SEED_FAMILIES)])
    arrays["famzmax"] = np.concatenate([np.max(np.vstack([fs[i]["z"][cid] for cid in fam_ids]), axis=0)
                                        for i in range(N_SEED_FAMILIES)])
    arrays["z|" + carry_id] = np.concatenate(zcarry)
    nt_path = os.path.join(out, "null-tables.npz")
    np.savez_compressed(nt_path, **arrays)
    pc1 = pc1_check(panels)
    cal = {"what": "EXP-PFDR-011cd0 R15 calibration (two-step blinding, step 1)", "created_at": now(),
           "started_at": t0, "design": a.design, "design_sha256": sha256(absp(a.design)),
           "t_star": ts, "t_carry": tcarry, "PC_NULL": pcnull, "PC_1": pc1,
           "predicted_X_rel_realised_design": xrel, "A2R_null": a2r,
           "null_tables": {"path": os.path.relpath(nt_path, REPO), "sha256": sha256(nt_path)},
           "generators": {"G-NB-R": {"groups": [{"key": list(g.key), "curves": g.curves, "mj": g.mj.tolist(),
                                                 "D": g.D, "log2N": g.log2N.tolist(),
                                                 "masks": {k: v.tolist() for k, v in g.masks.items() if k != "all"}}
                                                for g in groups],
                                      "group_info": {json.dumps(list(k)): v for k, v in ginfo.items()},
                                      "rho1_hat": {f"{k[0]}{k[1]}|{k[2]}": v for k, v in rho1.items()}}},
           "cells": {k: [{"id": c["id"], "arm": c["arm"], "cls": c["cls"], "m": c["m"], "rungs": c["rungs"],
                          "parts": [[list(gk), mk] for gk, mk in c["parts"]]} for c in v] for k, v in cells.items()},
           "simulation": {"reps_per_seed_family": reps, "seed_families": N_SEED_FAMILIES,
                          "seed_rule": "numpy SeedSequence([0x011cd0, i]), i = 0..4 (planted excess continues the stream)",
                          "x_rel_reps_per_seed_family": POWER_REPS_PER_FAMILY},
           "cc6_from_design_unmatched_size": sorted([list(k) for k, v in unmatched.items() if v]),
           "blinding": {"parsed_arms": sorted(parsed), "structured_or_planted_arm_parsed": False}}
    dump(os.path.join(out, "calibration.json"), cal)
    print(json.dumps({"t_star": ts["t"], "t_star_spread": ts["spread"], "t_carry": tcarry["t"],
                      "PC_NULL_pass": pcnull["pass"], "PC_1_pass": pc1["pass"]}))
    return 0


# ==========================================================================================
# unmask (R16)

def load_calibration(path: str):
    cal = json.load(open(path))
    groups = []
    for g in cal["generators"]["G-NB-R"]["groups"]:
        G = Group(tuple(g["key"]), g["curves"], g["mj"], g["D"], g.get("masks"))
        G.log2N = np.array(g["log2N"])
        groups.append(G)
    gbk = {g.key: g for g in groups}
    cells = {k: [{"id": c["id"], "arm": c["arm"], "cls": c["cls"], "m": c["m"], "rungs": c["rungs"],
                  "parts": [(tuple(gk), mk) for gk, mk in c["parts"]]} for c in v]
             for k, v in cal["cells"].items()}
    return cal, groups, gbk, cells


def aint_q(gbk, cell, kappas: list, reps_per_family, families=range(N_SEED_FAMILIES)) -> dict:
    """A-INT primary: for each kappa, q2 = 0.975 and q1 = 0.95 quantiles of |kappa_hat_sim - kappa| / SE_sim
    under G-NB-R with a planted excess at kappa (Poisson-planted; binomial thinning below 1), averaged
    over seed families.  The null draws of a seed family are shared across the kappas."""
    gl = [gbk[tuple(gk)] for gk, _ in cell["parts"]]
    acc = {k: {"q2": [], "q1": []} for k in kappas}
    for i in families:
        res = family_sim(gl, [cell], reps_per_family, i, keep_parts=True)
        CR, Q, base = res["CR"][cell["id"]], res["V"][cell["id"]], res["A"][cell["id"]]
        rng = res["rng"]
        V = np.maximum(Q, CR)
        SD = np.sqrt(V * 4 / 3)
        for key in kappas:
            k = max(float(key), 0.0)
            if k >= 1:
                A = base + excess_draw(rng, gbk, cell, k, "poisson", reps_per_family)
            else:
                A = rng.binomial(base, k)
            with np.errstate(divide="ignore", invalid="ignore"):
                dev = np.abs(A / CR - k) / (SD / CR)
            dev = dev[np.isfinite(dev)]
            acc[key]["q2"].append(float(np.quantile(dev, 0.975)) if len(dev) else float("nan"))
            acc[key]["q1"].append(float(np.quantile(dev, 0.95)) if len(dev) else float("nan"))
    return {k: {"q_two_sided_0975": float(np.mean(v["q2"])), "q_one_sided_095": float(np.mean(v["q1"])),
                "per_family_q2": v["q2"], "per_family_q1": v["q1"]} for k, v in acc.items() if v["q2"]}


def bootstrap_kappa(per_curve: list[dict], rng, reps: int) -> dict:
    """Secondary: paired curve-cluster bootstrap of kappa_rel (curves resampled within rung, same
    indices for every arm), studentized with the n/(n-1) variance correction."""
    by_rung = defaultdict(list)
    for c in per_curve:
        if "A" in c:
            by_rung[c["bits"]].append(c)
    if not by_rung:
        return {}
    A = {b: np.array([c["A"] for c in v], dtype=float) for b, v in by_rung.items()}
    R = {b: np.array([c["randoms"] for c in v], dtype=float) for b, v in by_rung.items()}
    def stat(Asum, Rsum, Qsum):
        V = np.maximum(Qsum, Rsum)
        SD = np.sqrt(V * 4 / 3)
        with np.errstate(divide="ignore", invalid="ignore"):
            return Asum / Rsum, SD / Rsum
    CA0 = sum(a.sum() for a in A.values())
    CR0 = sum(r.mean(axis=1).sum() for r in R.values())
    Q0 = sum(r.var(axis=1, ddof=1).sum() for r in R.values())
    k0, se0 = stat(CA0, CR0, Q0)
    ts = []
    chunk = 1000
    for st in range(0, reps, chunk):
        k = min(chunk, reps - st)
        CA = np.zeros(k)
        CR = np.zeros(k)
        Q = np.zeros(k)
        for b in A:
            n = len(A[b])
            idx = rng.integers(0, n, size=(k, n))
            CA += A[b][idx].sum(axis=1)
            CR += R[b].mean(axis=1)[idx].sum(axis=1)
            Q += R[b].var(axis=1, ddof=1)[idx].sum(axis=1)
        kb, seb = stat(CA, CR, Q)
        with np.errstate(divide="ignore", invalid="ignore"):
            ts.append((kb - k0) / seb)
    tt = np.concatenate(ts)
    tt = tt[np.isfinite(tt)]
    n_tot = sum(len(v) for v in A.values())
    corr = math.sqrt(n_tot / (n_tot - 1)) if n_tot > 1 else 1.0
    if not len(tt) or not np.isfinite(se0):
        return {"kappa": fin(k0)}
    lo = k0 - float(np.quantile(tt, 0.975)) * se0 * corr
    hi = k0 - float(np.quantile(tt, 0.025)) * se0 * corr
    ub = k0 - float(np.quantile(tt, 0.05)) * se0 * corr
    return {"kappa": fin(k0), "ci95": [fin(lo), fin(hi)], "upper95_one_sided": fin(ub),
            "replicates": int(len(tt)), "n_over_n_minus_1": corr}


def coverage_sim(gbk, cell, t_kappas=(1.0, 1.15), designs=COVERAGE_DESIGNS, q_grid=None) -> dict:
    """Coverage of the primary (q interpolated on a kappa grid) and of the secondary bootstrap
    (COVERAGE_BOOT_INNER inner replicates) at kappa = 1 and 1.15, on `designs` synthetic designs."""
    out = {}
    rng = seeded(0)
    grid = np.array(sorted(q_grid)) if q_grid else None
    for kappa in t_kappas:
        cov_p = cov_b = n_ok = 0
        for d in range(designs):
            per_curve = []
            for gk, mk in cell["parts"]:
                g = gbk[tuple(gk)]
                msk = g.masks[mk]
                mj = g.mj[msk]
                Rn = draw_counts(rng, mj, g.D, (3,))  # (3, n)
                An = draw_counts(rng, mj, g.D, ())
                if kappa > 1:
                    An = An + rng.poisson((kappa - 1) * mj)
                for j in range(len(mj)):
                    per_curve.append({"bits": gk[3], "A": int(An[j]), "randoms": Rn[:, j].tolist()})
            CA = sum(c["A"] for c in per_curve)
            CR = sum(np.mean(c["randoms"]) for c in per_curve)
            Q = sum(np.var(c["randoms"], ddof=1) for c in per_curve)
            if CR <= 0:
                continue
            V = max(Q, CR)
            SE = math.sqrt(V * 4 / 3) / CR
            kh = CA / CR
            n_ok += 1
            if grid is not None:
                qs = np.array([q_grid[k] for k in sorted(q_grid)])
                q2 = float(np.interp(kh, grid, qs))
                if abs(kh - kappa) <= q2 * SE:
                    cov_p += 1
            b = bootstrap_kappa(per_curve, rng, COVERAGE_BOOT_INNER)
            ci = b.get("ci95")
            if ci and all(isinstance(x, float) for x in ci) and ci[0] <= kappa <= ci[1]:
                cov_b += 1
        out[str(kappa)] = {"designs": n_ok, "primary_coverage": (cov_p / n_ok if n_ok and grid is not None else None),
                           "bootstrap_coverage": (cov_b / n_ok if n_ok else None)}
    return out


def holm(pvals: dict, alpha: float = 0.05) -> dict:
    items = sorted((p, k) for k, p in pvals.items() if p is not None)
    m = len(items)
    rej = {}
    stop = False
    for i, (p, k) in enumerate(items):
        thr = alpha / (m - i)
        if not stop and p <= thr:
            rej[k] = True
        else:
            stop = True
            rej[k] = False
    return rej


def heuristics(panels: dict, design: dict, gbk: dict, rho1: dict, rng) -> dict:
    """A6R on the random arms r0..r2 (both families) of the 30-32 band; A3R rank ratios on every arm.
    Clusters are curves (each curve carries one random triple per family)."""
    clists = design_curve_lists(design)
    out = {"H1a": {}, "H1b": {}, "H1c": {}, "H5": {}, "multiplicity_histograms": {}, "A3R": {}}
    for (cls, m) in FAM1_CM:
        panel = PANEL_OF_CLASS[cls]
        mode = "table" if panel == "table" else "search"
        ycl, xcl = [], []
        # per curve: sum s^2 and sum nbar over its triples (relations, pairs); sum M, sum M^2
        cur = []
        hist = Counter()
        pit = []
        Ns = []
        for b in BAND:
            for c in clists[(panel, m, b)]:
                y = x = 0.0
                rec = {"s2r": 0.0, "nbr": 0.0, "s2p": 0.0, "nbp": 0.0, "M1": 0, "M2": 0, "trip": 0}
                for fam in ("SUB", "DICK"):
                    cnt = [inst_counts(panels[panel].get((b, c, m, a, mode), {}), cls) for a in RANDOMS[fam]]
                    if any(v is None for v in cnt):
                        continue
                    rl = np.array([v["n"] for v in cnt], dtype=float)
                    pl = np.array([v["pairs"] for v in cnt], dtype=float)
                    rec["s2r"] += float(rl.var(ddof=1))
                    rec["nbr"] += float(rl.mean())
                    rec["s2p"] += float(pl.var(ddof=1))
                    rec["nbp"] += float(pl.mean())
                    rec["trip"] += 1
                    for a, v in zip(RANDOMS[fam], cnt):
                        Ns.append(v["N"])
                        y += v["pairs"]
                        if cls == "SS":
                            x += mu_pairs("SS", v["N"], X=v["X_fix"])
                        else:
                            x += mu_pairs(cls, v["N"], Ep=v["Ep"], s=v["s"])
                        for kk, vv in v["hist"].items():
                            hist[int(kk)] += vv
                            rec["M1"] += int(kk) * vv
                            rec["M2"] += int(kk) * int(kk) * vv
                        if cls != "SS":
                            mj = (rho1.get((cls, m, b)) or 0.0) * mu_rel_model(cls, m, v["N"], Ep=v["Ep"], s=v["s"])
                            u = random.Random(f"pit-011cd0|{b}|{c}|{m}|{a}|{cls}").random()
                            Fm = poisson_cdf(v["n"] - 1, mj)
                            F = poisson_cdf(v["n"], mj)
                            pit.append(Fm + u * (F - Fm))
                if rec["trip"]:
                    cur.append(rec)
                    ycl.append(y)
                    xcl.append(x)
        y, x = np.array(ycl), np.array(xcl)
        n = len(y)
        key = f"{cls}{m}"
        out["multiplicity_histograms"][key] = {str(k): hist[k] for k in sorted(hist)}
        if n >= 2 and x.sum() > 0:
            R = y.sum() / x.sum()
            se = math.sqrt(n / (n - 1) * ((y - R * x) ** 2).sum()) / x.sum()
            tq = t_quantile(0.995, n - 1)
            ci = [R - tq * se, R + tq * se]
            out["H1a"][key] = {"ratio_pairs_over_model": R, "ci99_curve_cluster_t": ci, "curves": n,
                               "df": n - 1, "t_0995": tq, "prediction_interval_P1": [0.90, 1.10],
                               "ci_entirely_outside_prediction": ci[1] < 0.90 or ci[0] > 1.10}
        if n < 2:
            continue
        A = {k: np.array([r[k] for r in cur], dtype=float) for k in ("s2r", "nbr", "s2p", "nbp", "M1", "M2")}
        Nbar = float(np.mean(Ns)) if Ns else float("nan")
        corr = math.sqrt(n / (n - 1))

        def stat_disp(s2, nb):
            return s2.sum() / nb.sum() if nb.sum() > 0 else float("nan")

        def boot(fn):
            vals = []
            for st in range(0, BOOT_REPS, 2000):
                ii = rng.integers(0, n, size=(min(2000, BOOT_REPS - st), n))
                with np.errstate(divide="ignore", invalid="ignore"):
                    vals.append(fn(ii))
            v = np.concatenate(vals)
            return v[np.isfinite(v)]

        def ci99(est, v):
            if not len(v) or not math.isfinite(est):
                return [None, None]
            lo, hi = np.quantile(v, [0.005, 0.995])
            return [float(est + corr * (lo - est)), float(est + corr * (hi - est))]

        DP = stat_disp(A["s2p"], A["nbp"])
        DPpred = (1 - 1 / Nbar) * A["M2"].sum() / A["M1"].sum() if A["M1"].sum() > 0 else float("nan")
        ratio = DP / DPpred if DPpred and math.isfinite(DPpred) else float("nan")
        bv = boot(lambda ii: (A["s2p"][ii].sum(1) / A["nbp"][ii].sum(1))
                  / ((1 - 1 / Nbar) * A["M2"][ii].sum(1) / A["M1"][ii].sum(1)))
        cr = ci99(ratio, bv)
        out["H1b"][key] = {"D_P_hat": DP, "D_P_pred": DPpred, "ratio": ratio, "ci99_ratio": cr,
                           "bootstrap_replicates": int(len(bv)), "prediction_interval_P2": [0.8, 1.25],
                           "ci_entirely_outside_prediction": (None if cr[0] is None else
                                                              (cr[1] < 0.8 or cr[0] > 1.25))}
        DR = stat_disp(A["s2r"], A["nbr"])
        bv = boot(lambda ii: A["s2r"][ii].sum(1) / A["nbr"][ii].sum(1))
        cr = ci99(DR, bv)
        ent = {"relation_dispersion_pooled_within_curve": DR, "ci99": cr, "curves": n,
               "bootstrap_replicates": int(len(bv))}
        if cls == "SS":
            ent["prediction_P3_H5"] = "< 4"
            ent["ci_lower_above_4"] = None if cr[0] is None else cr[0] > 4
            out["H5"][key] = ent
        else:
            ent["prediction_interval_P3"] = [0.8, 1.25]
            ent["ci_entirely_outside_prediction"] = None if cr[0] is None else (cr[1] < 0.8 or cr[0] > 1.25)
            if pit:
                u = np.sort(np.array(pit))
                nn2 = len(u)
                D = float(max(np.max(np.arange(1, nn2 + 1) / nn2 - u), np.max(u - np.arange(0, nn2) / nn2)))
                pks = kolmogorov_p(D, nn2)
                ent["randomized_pit_ks"] = {"n": nn2, "D": D, "p": pks, "rejects_at_1pct": pks < 0.01,
                                            "against": "Poisson(m_j), m_j = rho1_hat(class, m, rung) x mu_model(j)"}
            out["H1c"][key] = ent
    # A3R: rank ratio per instance (R_star >= 10), median per (arm, class, m) with >= 20 qualifying
    acc = defaultdict(list)
    for panel, rows in panels.items():
        for k, r in rows.items():
            b, c, m, arm, mode = k
            if r.get("status") != "completed_valid" or not r.get("harvest"):
                continue
            for cls in (("TT", "TB") if panel == "table" else ("SS",)):
                st = r["harvest"][cls]["at_stop"]
                Rs, U = st["R_star"], r["harvest"]["U"]
                if Rs >= 10:
                    acc[(arm, cls, m)].append(st["informative_rank"] / min(Rs, U))
    for (arm, cls, m), v in sorted(acc.items()):
        out["A3R"][f"{arm}|{cls}{m}"] = {"qualifying": len(v), "median": float(np.median(v)),
                                        "evaluated": len(v) >= 20,
                                        "median_ge_095": float(np.median(v)) >= 0.95 if len(v) >= 20 else None}
    return out


def a_tail(panels: dict) -> list:
    """TB at m = 4, 5 on structured arms: P(Poisson(mu_model) >= n) < 1e-4."""
    out = []
    for k, r in panels["table"].items():
        b, c, m, arm, mode = k
        if m not in (4, 5) or arm not in FAM1_ARMS or r.get("status") != "completed_valid":
            continue
        d = inst_counts(r, "TB")
        mu = mu_rel_model("TB", m, d["N"], Ep=d["Ep"], s=d["s"])
        p = poisson_sf_ge(d["n"], mu)
        if p < 1e-4:
            out.append({"key": list(k), "n": d["n"], "mu_model": mu, "tail_p": p})
    return out


def cc6_report(panels, design, unmatched) -> dict:
    clists = design_curve_lists(design)
    rep = {"unmatched_size": [], "failed_infrastructure": [], "incomplete_cells": []}
    for (b_, c_, m_, arm, mode), r in panels["table"].items():
        if r.get("status") == "failed_infrastructure":
            rep["failed_infrastructure"].append(["table", b_, c_, m_, arm])
    for (b_, c_, m_, arm, mode), r in panels["search"].items():
        if r.get("status") == "failed_infrastructure":
            rep["failed_infrastructure"].append(["search", b_, c_, m_, arm])
    for k, v in unmatched.items():
        if v:
            rep["unmatched_size"].append(list(k))
    return rep


def cmd_unmask(a) -> int:
    out = absp(a.out)
    calp = absp(a.calibration)
    if sha256(calp) != a.calibration_sha256:
        print("refusing: calibration.json does not match the pinned sha256 (I-6)", file=sys.stderr)
        return 3
    for f in ("analysis.json", "cells.jsonl", "heuristics.json"):
        if os.path.exists(os.path.join(out, f)):
            print(f"refusing: {out}/{f} exists", file=sys.stderr)
            return 3
    cal, groups, gbk, cells = load_calibration(calp)
    nt = cal["null_tables"]
    ntp = absp(nt["path"])
    if sha256(ntp) != nt["sha256"]:
        print("refusing: null-tables.npz does not match calibration.json", file=sys.stderr)
        return 3
    tables = np.load(ntp)
    design = json.load(open(absp(a.design)))
    log = ArmLog()
    panels = {"table": load_panel(a.runs_dir, "RUN-PFDR-011cd0-table", None, log),
              "search": load_panel(a.runs_dir, "RUN-PFDR-011cd0-search", None, log)}
    t = cal["t_star"]["t"]
    tc = cal["t_carry"]["t"]
    unmatched = size_unmatched_from_design(design)
    # realised-design check: structured/planted arms failed on kept curves (CC-6 family drop)
    late_drops = []
    for g in groups:
        fam, cls, m, b = g.key
        panel = PANEL_OF_CLASS[cls]
        mode = "table" if panel == "table" else "search"
        for arm in STRUCT_OF_FAMILY[fam] + (("planted_sub",) if (fam == "SUB" and m == 3 and panel == "table") else ()):
            for c in g.curves:
                r = panels[panel].get((b, c, m, arm, mode))
                if r is None or r.get("status") != "completed_valid":
                    late_drops.append({"group": list(g.key), "curve": c, "arm": arm,
                                       "status": None if r is None else r.get("status")})
    # observed cells (structured/planted failures drop the curve from every cell of the family, CC-6;
    # the pinned calibration is not recomputed and the difference is recorded under CC6)
    fdrops = {(d["group"][0], d["group"][1], d["group"][2], d["group"][3], d["curve"]) for d in late_drops}
    rec_cells = []
    obs = {}
    for kind in ("fam1_band", "fam1_rung", "kn_band", "kn_rung", "planted", "carry"):
        for c in cells[kind]:
            o = observed_cell(c, gbk, panels, family_drops=fdrops)
            obs[c["id"]] = o
            rec_cells.append({"kind": kind, "id": c["id"], "arm": c["arm"], "class": c["cls"], "m": c["m"],
                              "rungs": c["rungs"], "C_A": o["C_A"], "C_R": o["C_R"], "V": o["V"],
                              "SD_null": o["SD_null"], "kappa_rel": o["kappa_rel"], "z": fin(o["z"]),
                              "curves_used": o["curves_used"],
                              "curves_design": sum(len(gbk[gk].curves) for gk, _ in c["parts"])})
    # calibrated p (band FAM-1 and CARRY-1 from the pinned null tables)
    pvals = {}
    for c in cells["fam1_band"]:
        zn = tables["z|" + c["id"]]
        pvals[c["id"]] = float(np.mean(zn >= obs[c["id"]]["z"]))
    cc = cells["carry"][0]
    p_carry = float(np.mean(tables["z|" + cc["id"]] >= obs[cc["id"]]["z"]))
    famz = tables["famzmax"]
    max_z = max(obs[c["id"]]["z"] for c in cells["fam1_band"])
    p_family_max = float(np.mean(famz >= max_z))
    exceed = [c["id"] for c in cells["fam1_band"] if obs[c["id"]]["z"] > t]
    deficits = [c["id"] for c in cells["fam1_band"] if obs[c["id"]]["z"] < -t]
    carry_exceed = obs[cc["id"]]["z"] > tc
    # PC-R (planted)
    planted_band = {c["cls"]: c for c in cells["planted"] if c["rungs"] == list(BAND)}
    pcr = {}
    pcr_iii = pcr_iii_check(panels, a.runs_dir)
    for cls, c in planted_band.items():
        o = obs[c["id"]]
        declared = 0
        for (fam, _, m, b), mk in c["parts"]:
            for cv in gbk[(fam, cls, 3, b)].curves:
                r = panels["table"].get((b, cv, 3, "planted_sub", "table"))
                if r and r.get("status") == "completed_valid":
                    rels = r["fb_params"]["planted_relations"]
                    declared += sum(1 for x in rels if x["class"] == cls)
        excess = o["C_A"] - o["C_R"]
        pcr[cls] = {"z": fin(o["z"]), "i_z_gt_tstar": o["z"] > t, "excess": excess,
                    "declared_planted_total": declared,
                    "ii_within_4SD": abs(excess - declared) <= 4 * o["SD_null"], "SD_null": o["SD_null"]}
    pcr_pass_i = all(v["i_z_gt_tstar"] for v in pcr.values())
    pcr_pass_ii = all(v["ii_within_4SD"] for v in pcr.values())
    # A-INT, X_rel, coverage, bootstrap (FAM-1 band and CARRY-1)
    aint = {}
    rng_b = np.random.default_rng(np.random.SeedSequence([SEED_ROOT, 200]))
    for c in cells["fam1_band"] + cells["carry"]:
        o = obs[c["id"]]
        if o["kappa_rel"] is None:
            aint[c["id"]] = {"note": "C_R == 0"}
            continue
        kh = float(o["kappa_rel"])
        grid = [round(0.70 + 0.05 * i, 2) for i in range(17)]
        qall = aint_q(gbk, c, [kh] + [g for g in grid if g != kh], REPS_PER_FAMILY)
        q = qall[kh]
        SE = o["SD_null"] / o["C_R"]
        kq = {g: qall[g]["q_two_sided_0975"] for g in grid if g in qall}
        cov = coverage_sim(gbk, c, q_grid=kq)
        boot = bootstrap_kappa(o["per_curve"], rng_b, BOOT_REPS)
        aint[c["id"]] = {"kappa_rel": o["kappa_rel"], "SE": SE, "q": q,
                         "ci95": [o["kappa_rel"] - q["q_two_sided_0975"] * SE, o["kappa_rel"] + q["q_two_sided_0975"] * SE],
                         "upper95_one_sided": o["kappa_rel"] + q["q_one_sided_095"] * SE,
                         "X_rel_realised": cal["predicted_X_rel_realised_design"].get(c["id"]),
                         "coverage": cov, "bootstrap_secondary": boot}
    # A2R
    a2r = {}
    pv = {}
    for (cls, m) in FAM1_CM:
        for arm in FAM1_ARMS:
            pts = []
            for b in RUNGS:
                cid = cell_id(arm, cls, m, (b,))
                o = obs[cid]
                y = a2r_point(o["kappa_rel"] if o["kappa_rel"] is not None else 0.0, o["C_R"], o["SD_null"])
                c = next(cc_ for cc_ in cells["fam1_rung"] if cc_["id"] == cid)
                x = float(np.nanmean(np.concatenate([gbk[gk].log2N[gbk[gk].masks[mk]] for gk, mk in c["parts"]]))) if c["parts"] else float("nan")
                if y is not None and math.isfinite(x):
                    pts.append((x, y))
            sl = a2r_slope(pts)
            fid = f"{arm}|{cls}{m}"
            nul = tables["a2r|" + fid]
            nul = nul[np.isfinite(nul)]
            p = float(np.mean(nul >= sl)) if (sl is not None and len(nul)) else None
            pv[fid] = p
            a2r[fid] = {"slope": sl, "points": pts, "p_one_sided": p,
                        "null_mean": cal["A2R_null"][fid]["null_mean"], "null_q95": cal["A2R_null"][fid]["null_q95"]}
    hr = holm(pv)
    for k in a2r:
        a2r[k]["holm_reject_005"] = hr.get(k)
    # per-rung calibrated p (rerun of the pinned generator) for FAM-1 per-rung and known-null cells
    rung_cells = cells["fam1_rung"]
    fs = run_family_sims(groups, arms_needed(rung_cells), rung_cells, REPS_PER_FAMILY)
    p_rung = {}
    for c in rung_cells:
        zn = np.concatenate([fs[i]["z"][c["id"]] for i in fs])
        p_rung[c["id"]] = float(np.mean(zn >= obs[c["id"]]["z"]))
    del fs
    rng_h = np.random.default_rng(np.random.SeedSequence([SEED_ROOT, 300]))
    rho1 = {}
    for k, v in cal["generators"]["G-NB-R"]["rho1_hat"].items():
        cm, b = k.split("|")
        rho1[(cm[:2], int(cm[2:]), int(b))] = v
    heur = heuristics(panels, design, gbk, rho1, rng_h)
    tails = a_tail(panels)
    # outcome ids
    gates_ok = bool(a.gates_ok)
    pcnull_ok = cal["PC_NULL"]["pass"]
    pc1_ok = cal["PC_1"]["pass"]
    outcomes = []
    if not gates_ok or not pcr_iii["pass"]:
        outcomes.append("O-INVALID")
    elif not (pcnull_ok and pc1_ok and pcr_pass_i and pcr_pass_ii):
        outcomes.append("O-UNCALIBRATED")
    elif exceed or carry_exceed:
        outcomes.append("O-CANDIDATE")
    else:
        outcomes.append("O-NULL-BOUNDED")
    if "O-INVALID" not in outcomes:
        outcomes.append("O-HEUR")
    extremes = sorted(cells["fam1_band"], key=lambda c: (obs[c["id"]]["kappa_rel"] or 0))
    analysis = {"what": "EXP-PFDR-011cd0 R16 unmasked analysis (two-step blinding, step 2)", "created_at": now(),
                "calibration": {"path": a.calibration, "sha256": a.calibration_sha256},
                "t_star": t, "t_carry": tc, "outcome_ids": outcomes,
                "fam1_cells_z_gt_tstar": exceed, "fam1_deficits_z_lt_minus_tstar": deficits,
                "family_max_z": fin(max_z), "p_family_max": p_family_max,
                "calibrated_p_fam1_band": pvals, "calibrated_p_per_rung": p_rung,
                "CARRY_1": {"z": fin(obs[cc["id"]]["z"]), "t_carry": tc, "z_gt_t_carry": carry_exceed,
                            "calibrated_p": p_carry, "kappa_rel": obs[cc["id"]]["kappa_rel"]},
                "PC_NULL": {"pass": pcnull_ok, "from": "calibration.json"},
                "PC_1": {"pass": pc1_ok, "from": "calibration.json"},
                "PC_R": {"i_pass": pcr_pass_i, "ii_pass": pcr_pass_ii, "iii": pcr_iii, "cells": pcr},
                "A_INT": aint, "A2R": a2r,
                "A_TAIL": {"TB_m45_structured_tail_lt_1e-4": tails,
                           "largest_kappa_cell": {"id": extremes[-1]["id"], "per_curve": obs[extremes[-1]["id"]]["per_curve"]},
                           "smallest_kappa_cell": {"id": extremes[0]["id"], "per_curve": obs[extremes[0]["id"]]["per_curve"]},
                           "per_rung_abs_z_gt_tstar": [c["id"] for c in cells["fam1_rung"]
                                                       if abs(obs[c["id"]]["z"]) > t]},
                "CC6": cc6_report(panels, design, unmatched) | {"late_drops_structured": late_drops},
                "gates_ok_input": gates_ok,
                "interpretation": "none (observations only; outcome ids as computed by the frozen rule)"}
    dump(os.path.join(out, "analysis.json"), analysis)
    with open(os.path.join(out, "cells.jsonl"), "w") as fh:
        for r in rec_cells:
            fh.write(json.dumps(r, default=_json_default) + "\n")
    dump(os.path.join(out, "heuristics.json"), heur)
    print(json.dumps({"outcome_ids": outcomes, "fam1_exceed": len(exceed), "carry_exceed": carry_exceed}))
    return 0


def pcr_iii_check(panels: dict, runs_dir: str) -> dict:
    """PC-R (iii): every planted relation's monic vector is in its instance's relation set (recount
    from the retained table rows)."""
    rd = view_run(runs_dir, "RUN-PFDR-011cd0-table")
    mr = json.load(open(os.path.join(rd, "merge-report.json")))
    need = defaultdict(set)
    for k, r in panels["table"].items():
        if k[3] == "planted_sub" and r.get("status") == "completed_valid":
            ent = mr["harvest_rows_map"].get(json.dumps(list(k)))
            if ent and ent["harvest_rows_file"]:
                need[ent["harvest_rows_file"]].add(k)
    hrows = defaultdict(list)
    for f, keyset in need.items():
        for r in iter_lines(absp(f), lambda arm: arm == "planted_sub"):
            k = key5(r)
            if k in keyset:
                hrows[k].append(r)
    missing, checked = [], 0
    for k, r in panels["table"].items():
        if k[3] != "planted_sub" or r.get("status") != "completed_valid":
            continue
        N = r["N"]
        for cls in ("TT", "TB"):
            rc = recount(hrows.get(k, []), N, cls, keep_sets=True)
            for rel in r["fb_params"]["planted_relations"]:
                if rel["class"] != cls:
                    continue
                v = {i: s % N for i, s in zip(rel["indices"], rel["signs"])}
                checked += 1
                if monic_of(v, N) not in rc["_monic"]:
                    missing.append({"key": list(k), "relation": rel})
    return {"pass": not missing and checked > 0, "planted_relations_checked": checked, "missing": missing}


# ==========================================================================================
# G-REL

def cmd_grel(a) -> int:
    rep = {"gate": "G-REL", "created_at": now(), "runs": {}, "pass": True}
    for run in a.runs:
        rd = absp(run)
        mr = json.load(open(os.path.join(rd, "merge-report.json")))
        rows = {key5(r): r for r in iter_lines(os.path.join(rd, "rows.jsonl.gz"))}
        files = defaultdict(set)
        for k, r in rows.items():
            ent = mr["harvest_rows_map"].get(json.dumps(list(k)))
            if r.get("status") == "completed_valid" and ent and ent["harvest_rows_file"]:
                files[ent["harvest_rows_file"]].add(k)
        compared, mism = 0, []
        for f, keyset in sorted(files.items()):
            byk = defaultdict(list)
            for h in iter_lines(absp(f)):
                k = key5(h)
                if k in keyset:
                    byk[k].append(h)
            for k in sorted(keyset):
                r = rows[k]
                hb = r["harvest"]
                fk = "known_log" if r["arm"] == "known_log" else "none"
                scopes = []
                for cls in CLASSES:
                    st = hb[cls]["at_stop"]
                    nret = sum(1 for h in byk[k] if h["class"] == cls)
                    digested = cls in (hb.get("rows_digest") or {})
                    if not digested and nret == st["rows_emitted"] and "relations_distinct" in st:
                        scopes.append((cls, "at_stop", [h for h in byk[k]], st))
                xf = hb["SS"].get("at_X_fix")
                if xf is not None and "relations_distinct" in xf:
                    pref = [h for h in byk[k] if h["class"] == "SS" and h.get("seq") is not None and h["seq"] < xf["X_fix"]]
                    if len(pref) == xf["rows_emitted"]:
                        scopes.append(("SS", "at_X_fix", pref, xf))
                for cls, scope, hs, blk in scopes:
                    rc = recount(hs, r["N"], cls, fk)
                    compared += 1
                    bad = [f_ for f_ in ("relations_distinct", "relations_distinct_sign", "relations_nonformal",
                                         "R_star", "multiplicity_histogram") if rc[f_] != blk[f_]]
                    if bad:
                        mism.append({"key": list(k), "class": cls, "scope": scope, "fields_differing": bad})
        rep["runs"][os.path.relpath(rd, REPO)] = {"compared_instance_class_scopes": compared,
                                                  "mismatches": mism, "mismatch_count": len(mism)}
        if mism or compared == 0:
            rep["pass"] = False
    rep["rule"] = ("for every completed_valid instance whose class rows are all retained (rows retained == "
                   "rows_emitted; digested classes skipped), and for SS at_X_fix from the rows with seq < X_fix: "
                   "the harvester's relations_distinct, relations_distinct_sign, relations_nonformal, R_star and "
                   "multiplicity histogram equal this file's recount; only equality is reported")
    dump(absp(a.out), rep)
    print(json.dumps({"gate": "G-REL", "pass": rep["pass"],
                      "compared": {k: v["compared_instance_class_scopes"] for k, v in rep["runs"].items()},
                      "mismatches": {k: v["mismatch_count"] for k, v in rep["runs"].items()}}))
    return 0 if rep["pass"] else 1


# ==========================================================================================
# stage-r (R17)

def triggered_cells(an: dict) -> list[dict]:
    """R16's triggers: FAM-1 band cells with z > t*, and CARRY-1 with z > t_carry."""
    out = []
    for cid in an["fam1_cells_z_gt_tstar"]:
        arm, cm, _ = cid.split("|")
        out.append({"id": cid, "arm": arm, "cls": cm[:2], "m": int(cm[2:]), "rungs": list(BAND),
                    "r16_z": None})
    if an["CARRY_1"]["z_gt_t_carry"]:
        arm, cls, m, b = CARRY1
        out.append({"id": "CARRY-1", "arm": arm, "cls": cls, "m": m, "rungs": [b], "r16_z": an["CARRY_1"]["z"]})
    return out


def stage_groups(cell: dict, panel_rows: dict, fam: str) -> tuple[list[Group], dict]:
    """Stage R' groups of one triggered cell from the stage's own randoms (A not read)."""
    cls, m = cell["cls"], cell["m"]
    mode = "table" if PANEL_OF_CLASS[cls] == "table" else "search"
    groups, info = [], {}
    for b in cell["rungs"]:
        curves = sorted({k[1] for k in panel_rows if k[0] == b and k[2] == m and k[4] == mode})
        kept, rc = [], []
        for c in curves:
            arms = list(RANDOMS[fam]) + [KNOWN_NULL[fam]]
            rows = [panel_rows.get((b, c, m, x, mode)) for x in arms]
            if any(r is None or r.get("status") != "completed_valid" for r in rows):
                continue
            kept.append(c)
            rc.append([inst_counts(panel_rows[(b, c, m, x, mode)], cls) for x in RANDOMS[fam]])
        n = np.array([[x["n"] for x in t] for t in rc], dtype=float).reshape(-1, 3)
        s2 = n.var(axis=1, ddof=1) if len(n) else np.zeros(0)
        nb = n.mean(axis=1) if len(n) else np.zeros(0)
        D_hat = float(s2.sum() / nb.sum()) if len(n) and nb.sum() > 0 else None
        D = max(D_hat or 1.0, 1.0)
        if cls == "SS":
            mj = [float(n.mean()) if len(n) else 0.0] * len(kept)
            r1 = None
        else:
            mus = [float(np.mean([mu_rel_model(cls, m, x["N"], Ep=x["Ep"], s=x["s"]) for x in t])) for t in rc]
            obs = float(n.sum())
            mod = 3 * sum(mus)
            r1 = obs / mod if mod > 0 else 0.0
            mj = [r1 * mu for mu in mus]
        g = Group((fam, cls, m, b), kept, mj, D)
        groups.append(g)
        info[json.dumps(list(g.key))] = {"curves_kept": len(kept), "curves_seen": len(curves), "D_hat": D_hat,
                                         "D": D, "rho1_stage": r1}
    return groups, info


def cmd_stage_r(a) -> int:
    """R17.  --step calibrate: t_R per triggered cell from the stage's own randoms (A not read;
    one-sided 0.01), the known-null arm scored against it; writes stage-calibration.json.
    --step unmask (with the pinned sha256): z_R of A, kappa_rel, median rho_rank of A; outcome."""
    out = absp(a.out)
    an = json.load(open(absp(a.analysis)))
    if "O-CANDIDATE" not in an["outcome_ids"]:
        print("refusing: R16 did not report O-CANDIDATE", file=sys.stderr)
        return 3
    trig = triggered_cells(an)
    stage = view_run(a.runs_dir, "RUN-PFDR-011cd0-stage-r")
    if a.step == "calibrate":
        if os.path.exists(os.path.join(out, "stage-calibration.json")):
            print("refusing: stage-calibration.json exists", file=sys.stderr)
            return 3
        log = ArmLog()
        rows = {key5(r): r for r in iter_lines(os.path.join(stage, "rows.jsonl.gz"), blinded_allowed, log)}
        cal = {"what": "EXP-PFDR-011cd0 R17 Stage R' calibration (A not read)", "created_at": now(), "cells": {}}
        for cell in trig:
            fam = FAMILY_OF[cell["arm"]]
            groups, info = stage_groups(cell, rows, fam)
            gbk = {g.key: g for g in groups}
            kn = {"id": "kn|" + cell["id"], "arm": KNOWN_NULL[fam], "cls": cell["cls"], "m": cell["m"],
                  "parts": [(g.key, "all") for g in groups]}
            ac = {"id": cell["id"], "arm": cell["arm"], "cls": cell["cls"], "m": cell["m"],
                  "parts": [(g.key, "all") for g in groups]}
            zs, zk = [], []
            for i in range(N_SEED_FAMILIES):
                res = family_sim(groups, [ac, kn], a.reps, i)
                zs.append(res["z"][ac["id"]])
                zk.append(res["z"][kn["id"]])
            per = [float(np.quantile(z, 0.99)) for z in zs]
            t_R = float(np.mean(per))
            kno = observed_cell(kn, gbk, {PANEL_OF_CLASS[cell["cls"]]: rows})
            cal["cells"][cell["id"]] = {"t_R": t_R, "t_R_per_seed_family": per,
                                        "known_null": {"z": fin(kno["z"]), "C_A": kno["C_A"], "C_R": kno["C_R"],
                                                       "calibrated_p": float(np.mean(np.concatenate(zk) >= kno["z"]))},
                                        "groups": [{"key": list(g.key), "curves": g.curves, "mj": g.mj.tolist(), "D": g.D}
                                                   for g in groups], "group_info": info}
        cal["arm_read_log"] = log.as_json()
        cal["parsed_arms"] = sorted(log.parsed_arms())
        dump(os.path.join(out, "stage-calibration.json"), cal)
        print(json.dumps({k: {"t_R": v["t_R"]} for k, v in cal["cells"].items()}))
        return 0
    calp = os.path.join(out, "stage-calibration.json")
    if sha256(calp) != a.calibration_sha256:
        print("refusing: stage-calibration.json does not match the pinned sha256", file=sys.stderr)
        return 3
    cal = json.load(open(calp))
    rows = {key5(r): r for r in iter_lines(os.path.join(stage, "rows.jsonl.gz"))}
    res_cells = {}
    outcomes = []
    for cell in trig:
        c = cal["cells"][cell["id"]]
        groups = [Group(tuple(g["key"]), g["curves"], g["mj"], g["D"]) for g in c["groups"]]
        gbk = {g.key: g for g in groups}
        ac = {"id": cell["id"], "arm": cell["arm"], "cls": cell["cls"], "m": cell["m"],
              "parts": [(g.key, "all") for g in groups]}
        o = observed_cell(ac, gbk, {PANEL_OF_CLASS[cell["cls"]]: rows})
        ratios = []
        mode = "table" if PANEL_OF_CLASS[cell["cls"]] == "table" else "search"
        for k, r in rows.items():
            if k[3] == cell["arm"] and k[2] == cell["m"] and k[4] == mode and r.get("status") == "completed_valid":
                st = r["harvest"][cell["cls"]]["at_stop"]
                if st["R_star"] >= 10:
                    ratios.append(st["informative_rank"] / min(st["R_star"], r["harvest"]["U"]))
        med = float(np.median(ratios)) if ratios else None
        alive = bool(o["z"] > c["t_R"] and o["z"] > 0 and med is not None and med >= 0.9)
        res_cells[cell["id"]] = {"z_R": fin(o["z"]), "t_R": c["t_R"], "kappa_rel": o["kappa_rel"],
                                 "C_A": o["C_A"], "C_R": o["C_R"], "median_rho_rank": med,
                                 "qualifying_instances": len(ratios), "O_ALIVE_CANDIDATE_condition": alive,
                                 "known_null": c["known_null"]}
        if alive:
            outcomes.append(f"O-ALIVE-CANDIDATE:{cell['id']}")
    if not outcomes:
        outcomes.append("O-NULL-BOUNDED (no triggered cell replicated in R17)")
    rep = {"what": "EXP-PFDR-011cd0 R17 Stage R' analysis", "created_at": now(),
           "stage_calibration_sha256": a.calibration_sha256, "cells": res_cells, "outcome_ids": outcomes,
           "interpretation": "none; TW-ALIVE is reported as fired when any O-ALIVE-CANDIDATE appears"}
    dump(os.path.join(out, "analysis.json"), rep)
    print(json.dumps({"outcome_ids": outcomes}))
    return 0


# ==========================================================================================

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("p0")
    p.add_argument("--archived-runs", required=True)
    p.add_argument("--bundles", required=True)
    p.add_argument("--curves", required=True)
    p.add_argument("--spec", default="experiments/EXP-PFDR-011cd0/specification.yaml")
    p.add_argument("--out", required=True)
    p.add_argument("--reps", type=int, default=REPS_PER_FAMILY)
    c = sub.add_parser("calibrate")
    c.add_argument("--runs-dir", required=True)
    c.add_argument("--design", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--reps", type=int, default=REPS_PER_FAMILY)
    u = sub.add_parser("unmask")
    u.add_argument("--runs-dir", required=True)
    u.add_argument("--design", required=True)
    u.add_argument("--calibration", required=True)
    u.add_argument("--calibration-sha256", required=True)
    u.add_argument("--out", required=True)
    u.add_argument("--gates-ok", type=int, required=True,
                   help="1 iff every invalidating gate of the first gate_rule list passed (from the gate reports)")
    s = sub.add_parser("stage-r")
    s.add_argument("--runs-dir", required=True)
    s.add_argument("--analysis", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--step", choices=("calibrate", "unmask"), required=True)
    s.add_argument("--calibration-sha256", default=None)
    s.add_argument("--reps", type=int, default=REPS_PER_FAMILY)
    g = sub.add_parser("grel")
    g.add_argument("--runs", nargs="+", required=True)
    g.add_argument("--out", required=True)
    a = ap.parse_args()
    if getattr(a, "reps", REPS_PER_FAMILY) < REPS_PER_FAMILY:
        print(f"note: --reps {a.reps} below the frozen minimum {REPS_PER_FAMILY} (fixture exercise only)",
              file=sys.stderr)
    return {"p0": cmd_p0, "calibrate": cmd_calibrate, "unmask": cmd_unmask, "stage-r": cmd_stage_r,
            "grel": cmd_grel}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
