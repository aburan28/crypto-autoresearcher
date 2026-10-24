"""EXP-PFDR-bb0d26: pair-sum coincidence census of x-label sets of rank-r log-GAP bases.

Frozen-contract driver (specification.yaml is the authority; this file is bound by
sha256 in trial-plan.json). Standard library plus PyYAML (manifest writing), the
vendored copy of src/crypto_autoresearcher/index_calculus/curve.py and the C kernel
labelsum.c. Toy generated prime-order curves only (p below 2^31).

Subcommands:
  trial       one supervised trial of trial-plan.json (--run-dir --run-id --trial-id --plan)
  design      write design.json from the closed-form sizing rule
  selftest    instrument gate C1/C7: selftest.json and design.json
  census-toy  main or replication block of the cells in design.json -> toy-<block>-jobs.jsonl
  analyze     frozen statistics, classes, toy reading and headline -> analysis json + flags.json

Counting convention: for a set X of n distinct labels in F_p, m_s = #{{u, v}: u != v,
u + v = s mod p}, C(X) = sum_s binom(m_s, 2), D(X) = #{s : m_s >= 1}.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import functools  # noqa: E402
import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import random  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402
from concurrent.futures.process import BrokenProcessPool  # noqa: E402
from fractions import Fraction  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import curve as ec  # noqa: E402  (vendored, sha256-pinned)

EXP = "EXP-PFDR-bb0d26"
HYPOTHESIS_ID = "H-PFDR-727bfc"

# ---------------------------------------------------------------- design constants
BITS = (20, 24, 28)
RANKS = (1, 2, 3)
NS = (256, 512, 1024, 2048, 4096)
NULL_REPS = 20
TARGET = 2500                 # powered iff M >= TARGET; also the sizing target
SAFETY = 1.5
N_MIN, N_MAX = 50, 2000
P_REF_FACTOR = 0.75           # p_ref = 0.75 * 2^bits
PLANT_FRACTION = 0.30
PLANT_M_MIN = 4               # plant size m searched in [4, n/2]
HALF_BOX_NUM, HALF_BOX_DEN, HALF_BOX_PAD = 102, 100, 8   # |H(r,T)| >= ceil(1.02 n) + 8
SEED_BLOCK = {"main": 8_100_000, "rep": 8_200_000, "selftest": 8_900_000}
BOOT_B = 2000
BOOT_PCT = (2.5, 97.5)
KERNEL_TIMEOUT_S = 3600
WORKERS = 4
GCC_FLAGS = ["-O2", "-std=c11"]
SELFTEST_MAX_BITS = 20        # blindness guard: the selftest block never builds a design-size curve

GATES = {
    "cal_sd_lo": 0.75, "cal_sd_hi": 1.25, "cal_mean_abs": 0.35,   # calibration gate over powered cells
    "plant_kappa": 1.15, "plant_z": 4.0,                          # plant recovery
    "flag_dev": 0.10, "flag_z": 4.0,                              # flagged: |kappa-1| >= and |z| >
    "null_dev": 0.05, "null_ci_lo": 0.90, "null_ci_hi": 1.10,     # null class
    "rep_z": 3.0, "rep_dev": 0.05,                                # replication survival
    "valid_min": 0.50, "null_valid_min": 0.80,                    # O-INVALID below, O-NULL at/above
    "anomaly_lo": 0.8, "anomaly_hi": 1.25,                        # null_mean_over_formula anomaly list (not a gate)
}
CLASSES = ("invalid", "inconclusive_underpowered", "inconclusive_plant_not_recovered",
           "flagged", "null", "intermediate")
VALID_CLASSES = ("null", "flagged", "intermediate")
OUTCOMES = ("O-INVALID", "O-STRUCT", "O-PENDING-REPLICATION", "O-NULL", "O-MIXED")
HEADLINES = {"O-STRUCT": "FALSIFY_SCOPED", "O-INVALID": "NOT_EVIDENCE", "O-NULL": "SUPPORT_SCOPED"}
KINDS = ("gap", "plant")      # job arms besides the always-built null arm

TRIAL_TABLE = (
    {"id": "selftest", "stage": "selftest", "block": None,
     "artifacts": ("manifest.yaml", "raw-result.json", "selftest.json", "design.json"),
     "memory_mb": 2048, "watchdog_seconds": 3600, "depends_on": (), "inputs_from": (), "output": None},
    {"id": "census-toy-main", "stage": "census", "block": "main",
     "artifacts": ("manifest.yaml", "raw-result.json", "toy-main-jobs.jsonl"),
     "memory_mb": 4096, "watchdog_seconds": 43200, "depends_on": ("selftest",),
     "inputs_from": ("design",), "output": None},
    {"id": "analyze-main", "stage": "analyze", "block": None,
     "artifacts": ("manifest.yaml", "raw-result.json", "analysis-main.json", "flags.json"),
     "memory_mb": 2048, "watchdog_seconds": 3600, "depends_on": ("census-toy-main",),
     "inputs_from": ("design", "main"), "output": "analysis-main.json"},
    {"id": "census-toy-rep", "stage": "census", "block": "rep",
     "artifacts": ("manifest.yaml", "raw-result.json", "toy-rep-jobs.jsonl"),
     "memory_mb": 4096, "watchdog_seconds": 43200, "depends_on": ("analyze-main",),
     "inputs_from": ("design", "flags"), "output": None},
    {"id": "analyze-final", "stage": "analyze", "block": None,
     "artifacts": ("manifest.yaml", "raw-result.json", "analysis.json", "flags.json"),
     "memory_mb": 2048, "watchdog_seconds": 3600, "depends_on": ("census-toy-rep",),
     "inputs_from": ("design", "main", "rep"), "output": "analysis.json"},
)


def _rng(*labels: object) -> random.Random:
    """Seeded stream: random.Random(sha256(EXP + '|' + '|'.join(labels)))."""
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


# ---------------------------------------------------------------- design table

def mu_ref(bits: int, n: int) -> float:
    """Random-set mean count at a mid-range prime: 3 binom(n,4) / (0.75 * 2^bits)."""
    return float(3 * math.comb(n, 4) / (Fraction(P_REF_FACTOR) * 2 ** bits))


def n_curves(bits: int, n: int) -> int:
    """clamp(ceil(SAFETY * TARGET / mu_ref), N_MIN, N_MAX), in exact rational arithmetic."""
    need = Fraction(SAFETY) * TARGET * Fraction(P_REF_FACTOR) * 2 ** bits / (3 * math.comb(n, 4))
    return max(N_MIN, min(N_MAX, math.ceil(need)))


def cells() -> list[dict]:
    out = []
    for bits in BITS:
        for r in RANKS:
            for n in NS:
                out.append({"cell": f"b{bits}-r{r}-n{n}", "bits": bits, "r": r, "n": n,
                            "mu_ref": mu_ref(bits, n), "n_curves": n_curves(bits, n)})
    return out


def design_table() -> dict:
    return {"experiment": EXP,
            "rule": (f"n_curves = clamp(ceil({SAFETY} x {TARGET} / mu_ref), {N_MIN}, {N_MAX}); "
                     f"mu_ref = 3 binom(n, 4) / p_ref; p_ref = {P_REF_FACTOR} x 2^bits"),
            "toy_cells": cells()}


def design_bytes() -> bytes:
    return (json.dumps(design_table(), indent=1, sort_keys=True) + "\n").encode()


# ---------------------------------------------------------------- curves and labels

@functools.lru_cache(maxsize=48)
def get_curve(bits: int, block: str, c: int):
    return ec.generate_prime_order_curve(bits, seed=SEED_BLOCK[block] + c)


def in_label_universe(E, x: int) -> bool:
    """x in L = {x : f(x) = x^3 + a x + b is a nonzero square mod p}."""
    f = E.rhs(x)
    return f != 0 and pow(f, (E.p - 1) // 2, E.p) == 1


def universe_size(E) -> int:
    return (E.order - 1) // 2


def null_builder(E, n: int, rng: random.Random) -> list[int]:
    """n distinct uniform labels of L: x uniform in [0,p), kept when in L, repeats skipped."""
    if n > universe_size(E):
        raise ValueError("n exceeds the label universe")
    out: list[int] = []
    seen: set[int] = set()
    while len(out) < n:
        x = rng.randrange(E.p)
        if x in seen or not in_label_universe(E, x):
            continue
        seen.add(x)
        out.append(x)
    return out


def half_box_size(r: int, T: int) -> int:
    return ((2 * T + 1) ** r - 1) // 2


def labels_needed(n: int) -> int:
    """ceil(1.02 n) + 8 in integer arithmetic."""
    return -(-(HALF_BOX_NUM * n) // HALF_BOX_DEN) + HALF_BOX_PAD


def half_box_T(r: int, n: int) -> int:
    """Least integer T with |H(r,T)| = ((2T+1)^r - 1)/2 >= ceil(1.02 n) + 8."""
    need, T = labels_needed(n), 1
    while half_box_size(r, T) < need:
        T += 1
    return T


def half_box_vectors(r: int, T: int):
    """Coefficient vectors in [-T,T]^r with first nonzero entry positive, lexicographic,
    each coordinate ascending from -T."""
    for v in itertools.product(range(-T, T + 1), repeat=r):
        for e in v:
            if e != 0:
                if e > 0:
                    yield v
                break


def gap_builder(E, r: int, n: int, rng: random.Random, keep_vectors: bool = False):
    """Rank-r log-GAP label set. Returns (labels, meta, status); status is 'ok' or
    'degenerate' (half-box exhausted before n labels; labels is then None)."""
    pts = [E.random_point(rng) for _ in range(r)]
    T = half_box_T(r, n)
    tabs = []
    for P in pts:
        pos = {0: None, 1: P}
        for k in range(2, T + 1):
            pos[k] = E.add(pos[k - 1], P)
        tab = {}
        for k in range(1, T + 1):
            tab[k] = pos[k]
            tab[-k] = E.neg(pos[k])
        tab[0] = None
        tabs.append(tab)
    labels: list[int] = []
    seen: set[int] = set()
    enumerated = dup = inf = 0
    first = last = None
    vectors = []
    for v in half_box_vectors(r, T):
        enumerated += 1
        Q = None
        for tab, ci in zip(tabs, v):
            Q = E.add(Q, tab[ci])
        if Q is None:
            inf += 1
            continue
        x = Q[0]
        if x in seen:
            dup += 1
            continue
        seen.add(x)
        labels.append(x)
        vectors.append(list(v))
        if first is None:
            first = list(v)
        last = list(v)
        if len(labels) == n:
            break
    meta = {"T": T, "enumerated": enumerated, "duplicate_skips": dup, "infinity_skips": inf,
            "first": first, "last": last}
    if keep_vectors:
        meta["vectors"] = vectors
        meta["points"] = pts
    if len(labels) < n:
        return None, meta, "degenerate"
    return labels, meta, "ok"


def gap_slow(E, pts: list, r: int, n: int) -> tuple[list[int], int, int]:
    """Slow path of the log-GAP builder: every label recomputed with Curve.mul."""
    T = half_box_T(r, n)
    vecs = sorted(v for v in itertools.product(range(-T, T + 1), repeat=r)
                  if next((e for e in v if e != 0), 0) > 0)
    labels, seen, dup = [], set(), 0
    for v in vecs:
        Q = None
        for ci, P in zip(v, pts):
            Q = E.add(Q, E.mul(ci, P))
        if Q is None:
            continue
        if Q[0] in seen:
            dup += 1
            continue
        seen.add(Q[0])
        labels.append(Q[0])
        if len(labels) == n:
            break
    return labels, dup, T


def planted_builder(E, n: int, rng: random.Random, null_C: list[int], internal_fn):
    """True label AP of m labels plus n - m uniform random labels of L not in the AP.
    m is the least integer in [4, n/2] with internal(m) >= PLANT_FRACTION x mean null count,
    internal(m) = C of the m AP labels alone. Returns (labels, meta)."""
    p, m_cap = E.p, n // 2
    if m_cap < PLANT_M_MIN:
        raise ValueError("n too small for a plant")
    x0 = rng.randrange(p)
    w = rng.randrange(1, p)
    ap: list[int] = []
    k = 0
    while len(ap) < m_cap:
        x = (x0 + k * w) % p
        if in_label_universe(E, x):
            ap.append(x)
        k += 1
        if k > p:
            raise ValueError("AP exhausted the field")
    thr = PLANT_FRACTION * (sum(null_C) / len(null_C))
    cache: dict[int, int] = {}

    def internal(m: int) -> int:
        if m not in cache:
            cache[m] = internal_fn(ap[:m])
        return cache[m]

    lo, hi = PLANT_M_MIN, m_cap
    if internal(hi) < thr:
        m, feasible = hi, False
    elif internal(lo) >= thr:
        m, feasible = lo, True
    else:
        while hi - lo > 1:             # internal(m) is nondecreasing in m (a superset adds pairs only)
            mid = (lo + hi) // 2
            if internal(mid) >= thr:
                hi = mid
            else:
                lo = mid
        m, feasible = hi, True
    labels = ap[:m]
    used = set(labels)
    while len(labels) < n:
        x = rng.randrange(p)
        if x in used or not in_label_universe(E, x):
            continue
        used.add(x)
        labels.append(x)
    return labels, {"m": m, "internal": internal(m), "feasible": feasible, "m_cap": m_cap}


# ---------------------------------------------------------------- kernel

def build_kernel(out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    exe = os.path.join(out_dir, "labelsum")
    subprocess.run(["gcc", *GCC_FLAGS, "-o", exe, os.path.join(HERE, "labelsum.c")], check=True)
    return exe


def run_kernel(kernel: str, p: int, sets: list[list[int]]) -> list[tuple[int, int, int, int]]:
    """(n, pairs, C, D) per label set."""
    lines = [str(p)] + [f"{len(s)} " + " ".join(map(str, s)) for s in sets]
    proc = subprocess.run([kernel], input="\n".join(lines) + "\n", capture_output=True, text=True,
                          timeout=KERNEL_TIMEOUT_S, check=True)
    out = [tuple(map(int, ln.split())) for ln in proc.stdout.strip().splitlines()]
    if len(out) != len(sets):
        raise RuntimeError(f"kernel returned {len(out)} lines for {len(sets)} sets")
    return out


def brute_CD(labels: list[int], p: int) -> tuple[int, int]:
    """Pure-Python reference count (dictionary), used by selftest and as a slow path."""
    mult: dict[int, int] = {}
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            s = (labels[i] + labels[j]) % p
            mult[s] = mult.get(s, 0) + 1
    return sum(m * (m - 1) // 2 for m in mult.values()), len(mult)


# ---------------------------------------------------------------- jobs

def _blind_guard(block: str, cell: dict) -> None:
    if block == "selftest" and cell["bits"] > SELFTEST_MAX_BITS:
        raise ValueError("selftest block is limited to bits <= %d" % SELFTEST_MAX_BITS)


def job(kernel: str, cell: dict, block: str, c: int, kinds: tuple = KINDS) -> dict:
    """One (cell, block, curve index) record; a pure function of the key except 'seconds'."""
    t0 = time.time()
    _blind_guard(block, cell)
    bits, r, n, cid = cell["bits"], cell["r"], cell["n"], cell["cell"]
    rec = {"cell": cid, "block": block, "c": c, "p": None, "a": None, "b_coef": None, "N": None,
           "bits": bits, "r": r, "n": n, "status": "ok", "null_C": None, "null_D": None,
           "gap_C": None, "gap_D": None, "gap_meta": None, "plant_m": None, "plant_internal": None,
           "plant_C": None, "plant_D": None, "plant_feasible": None}
    try:
        E, _ = get_curve(bits, block, c)
        rec.update(p=E.p, a=E.a, b_coef=E.b, N=E.order)
        gap_ok, gap_labels = True, None
        if "gap" in kinds:
            gap_labels, meta, st = gap_builder(E, r, n, _rng("gap", block, cid, c))
            rec["gap_meta"] = meta
            if st != "ok":
                rec["status"], gap_ok = "degenerate", False
        if gap_ok:
            sets = [null_builder(E, n, _rng("null", block, cid, c, k)) for k in range(NULL_REPS)]
            if gap_labels is not None:
                sets.append(gap_labels)
        if gap_ok:
            res = run_kernel(kernel, E.p, sets)
            rec["null_C"] = [x[2] for x in res[:NULL_REPS]]
            rec["null_D"] = [x[3] for x in res[:NULL_REPS]]
            if "gap" in kinds:
                rec["gap_C"], rec["gap_D"] = res[NULL_REPS][2], res[NULL_REPS][3]
            if "plant" in kinds:
                pl, pm = planted_builder(E, n, _rng("plant", block, cid, c), rec["null_C"],
                                         lambda ls: run_kernel(kernel, E.p, [ls])[0][2])
                pres = run_kernel(kernel, E.p, [pl])[0]
                rec.update(plant_m=pm["m"], plant_internal=pm["internal"], plant_C=pres[2],
                           plant_D=pres[3], plant_feasible=pm["feasible"])
    except subprocess.TimeoutExpired:
        rec["status"] = "failed_infrastructure:kernel_timeout"
    except subprocess.CalledProcessError as e:
        rec["status"] = f"failed_infrastructure:kernel_exit_{e.returncode}"
    except MemoryError:
        rec["status"] = "failed_infrastructure:memory"
    except Exception as e:  # a crash is failed_infrastructure, never a metric value
        rec["status"] = f"failed_infrastructure:exception_{type(e).__name__}"
    rec["seconds"] = round(time.time() - t0, 3)
    return rec


def _failed_record(cell: dict, block: str, c: int, why: str) -> dict:
    return {"cell": cell["cell"], "block": block, "c": c, "bits": cell["bits"], "r": cell["r"],
            "n": cell["n"], "status": f"failed_infrastructure:{why}", "seconds": 0.0}


def load_jsonl(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _done_keys(path: str) -> set:
    keys = set()
    if os.path.exists(path):
        for r in load_jsonl(path):
            if r.get("status") in ("ok", "degenerate"):
                keys.add((r["cell"], r["block"], r["c"]))
    return keys


def _run_jobs(kernel: str, todo: list, out_path: str, kinds: tuple = KINDS, workers: int = WORKERS) -> None:
    """Run (cell, block, curve) jobs on a process pool, appending one record per job in completion order.
    A broken pool (a killed worker) turns every in-flight job into a failed_infrastructure record and
    the pool is rebuilt; a failed key is retried by a later invocation (only ok/degenerate keys are done)."""
    from concurrent.futures import FIRST_COMPLETED, wait
    done = _done_keys(out_path)
    todo = [t for t in todo if (t[0]["cell"], t[1], t[2]) not in done]
    todo.sort(key=lambda t: (-t[0]["n"], t[0]["cell"], t[2]))     # largest n first for load balance
    print(f"jobs to run: {len(todo)} (already done: {len(done)})", flush=True)
    it, written, inflight = iter(todo), 0, {}
    pool = ProcessPoolExecutor(max_workers=workers)
    with open(out_path, "a") as f:
        def emit(rec):
            nonlocal written
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            f.flush()
            written += 1
            if written % 500 == 0 or written == len(todo):
                print(f"  {written}/{len(todo)}", flush=True)

        def fill():
            while len(inflight) < 4 * workers:
                t = next(it, None)
                if t is None:
                    return
                inflight[pool.submit(job, kernel, t[0], t[1], t[2], kinds)] = t
        fill()
        while inflight:
            finished, _ = wait(list(inflight), return_when=FIRST_COMPLETED)
            broken = False
            for fut in finished:
                cell, block, c = inflight.pop(fut)
                try:
                    emit(fut.result())
                except BrokenProcessPool:
                    broken = True
                    emit(_failed_record(cell, block, c, "worker_crash"))
                except Exception as e:
                    emit(_failed_record(cell, block, c, f"exception_{type(e).__name__}"))
            if broken:
                for fut, (cell, block, c) in list(inflight.items()):
                    emit(_failed_record(cell, block, c, "worker_crash"))
                    inflight.pop(fut)
                pool.shutdown(wait=False, cancel_futures=True)
                pool = ProcessPoolExecutor(max_workers=workers)
            fill()
    pool.shutdown(wait=True)


# ---------------------------------------------------------------- statistics

def _div(a, b):
    return a / b if b and b > 0 else None


def _sd(V: float):
    return math.sqrt(V * (1 + 1 / NULL_REPS)) if V > 0 else None


def zcal_of(rs: list[dict]):
    """Null replicate 0 as a pseudo-structured set against replicates 1..19 (variance factor 1 + 1/19)."""
    pS = sum(r["null_C"][0] for r in rs)
    pM = sum(statistics.fmean(r["null_C"][1:]) for r in rs)
    pV = sum(statistics.variance(r["null_C"][1:]) for r in rs)
    return (pS - pM) / math.sqrt(pV * (1 + 1 / (NULL_REPS - 1))) if pV > 0 else None


def plant_stats(rs: list[dict]) -> dict:
    """Plant recovery statistics on the planted and null arms only."""
    rs = sorted(rs, key=lambda r: r["c"])
    M = sum(statistics.fmean(r["null_C"]) for r in rs)
    V = sum(statistics.variance(r["null_C"]) for r in rs)
    Pl = sum(r["plant_C"] for r in rs)
    sd = _sd(V)
    return {"curves": len(rs), "M": M, "V": V, "plant_kappa": _div(Pl, M),
            "plant_z": (Pl - M) / sd if sd else None,
            "plant_feasible_all": all(r["plant_feasible"] for r in rs)}


def formula_mean(n: int, p: int) -> float:
    return 3 * math.comb(n, 4) / p


def cell_stats(rs: list[dict], seed: str, with_gap: bool = True) -> dict:
    """Frozen per-cell statistics; records are sorted by curve index first (R7)."""
    rs = sorted(rs, key=lambda r: r["c"])
    n = len(rs)
    means = [statistics.fmean(r["null_C"]) for r in rs]
    dmeans = [statistics.fmean(r["null_D"]) for r in rs]
    M = sum(means)
    V = sum(statistics.variance(r["null_C"]) for r in rs)
    S = sum(r["gap_C"] for r in rs) if with_gap else None
    sd = _sd(V)
    out = {"curves": n, "S": S, "M": M, "V": V, "kappa": _div(S, M) if with_gap else None,
           "z": (S - M) / sd if (with_gap and sd) else None,
           "z_cal": zcal_of(rs), "ci95": None, "d_ratio": None, "d_ci95": None}
    pl = plant_stats(rs)
    out.update({k: pl[k] for k in ("plant_kappa", "plant_z", "plant_feasible_all")})
    fm = sum(formula_mean(r["n"], r["p"]) for r in rs)
    out["null_mean_over_formula"] = _div(M, fm)
    if with_gap:
        gC = [r["gap_C"] for r in rs]
        gD = [r["gap_D"] for r in rs]
        out["d_ratio"] = _div(sum(gD), sum(dmeans))
        rng = _rng("boot", seed)
        bk, bd = [], []
        for _ in range(BOOT_B):
            idx = [rng.randrange(n) for _ in range(n)]
            m = sum(map(means.__getitem__, idx))
            md = sum(map(dmeans.__getitem__, idx))
            if m > 0:
                bk.append(sum(map(gC.__getitem__, idx)) / m)
            if md > 0:
                bd.append(sum(map(gD.__getitem__, idx)) / md)
        for key, bs in (("ci95", bk), ("d_ci95", bd)):
            if bs:
                bs.sort()
                out[key] = [bs[int(BOOT_PCT[0] / 100 * len(bs))], bs[int(BOOT_PCT[1] / 100 * len(bs)) - 1]]
        for tag, par in (("kappa_even", 0), ("kappa_odd", 1)):
            sel = [i for i, r in enumerate(rs) if r["c"] % 2 == par]
            out[tag] = _div(sum(gC[i] for i in sel), sum(means[i] for i in sel))
    return out


def classify(st: dict) -> tuple[str, bool, bool]:
    """(class, powered, planted_recovered) for a complete cell, first matching class in order."""
    powered = st["M"] >= TARGET
    planted = bool(st["plant_feasible_all"] and st["plant_kappa"] is not None
                   and st["plant_kappa"] >= GATES["plant_kappa"]
                   and st["plant_z"] is not None and st["plant_z"] > GATES["plant_z"])
    k, z, ci = st["kappa"], st["z"], st["ci95"]
    if not powered:
        return "inconclusive_underpowered", powered, planted
    if not planted:
        return "inconclusive_plant_not_recovered", powered, planted
    if k is not None and z is not None and abs(k - 1) >= GATES["flag_dev"] and abs(z) > GATES["flag_z"]:
        return "flagged", powered, planted
    if k is not None and ci is not None and abs(k - 1) < GATES["null_dev"] \
            and GATES["null_ci_lo"] <= ci[0] and ci[1] <= GATES["null_ci_hi"]:
        return "null", powered, planted
    return "intermediate", powered, planted


def calibration_gate(zs: list[float]) -> dict:
    cal = {"n": len(zs), "mean": statistics.fmean(zs) if zs else None,
           "sd": statistics.pstdev(zs) if len(zs) > 1 else None}
    cal["pass"] = bool(cal["sd"] is not None and GATES["cal_sd_lo"] <= cal["sd"] <= GATES["cal_sd_hi"]
                       and abs(cal["mean"]) <= GATES["cal_mean_abs"])
    return cal


def reading(cal_pass: bool, frac_valid: float, classes: list[str], surv: list[bool],
            pending: list[bool]) -> str:
    valid = [c for c in classes if c in VALID_CLASSES]
    if not cal_pass or frac_valid < GATES["valid_min"]:
        return "O-INVALID"
    if any(surv):
        return "O-STRUCT"
    if any(pending):
        return "O-PENDING-REPLICATION"
    if valid and all(c == "null" for c in valid) and frac_valid >= GATES["null_valid_min"]:
        return "O-NULL"
    return "O-MIXED"


def headline_of(outcome: str) -> str:
    return HEADLINES.get(outcome, "INCONCLUSIVE")


def _ok_by_curve(recs: list[dict], cell: str, planned: int) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for r in recs:
        if r["cell"] == cell and r["status"] == "ok" and 0 <= r["c"] < planned and r["c"] not in out:
            out[r["c"]] = r
    return out


def replication_of(cell: dict, row: dict, rep_recs: list[dict] | None) -> dict:
    planned = cell["n_curves"]
    mine = [x for x in (rep_recs or []) if x["cell"] == cell["cell"]]
    if not mine:
        return {"status": "not_run", "curves": 0, "survives": False}
    okc = _ok_by_curve(mine, cell["cell"], planned)
    if len(okc) < planned:
        return {"status": "incomplete", "curves": len(okc), "survives": False}
    st = cell_stats(list(okc.values()), cell["cell"] + "|rep")
    same = (st["kappa"] - 1) * (row["kappa"] - 1) > 0
    surv = bool(same and st["z"] is not None and abs(st["z"]) > GATES["rep_z"]
                and abs(st["kappa"] - 1) >= GATES["rep_dev"])
    return {"status": "complete", "curves": st["curves"], "kappa": st["kappa"], "ci95": st["ci95"],
            "z": st["z"], "S": st["S"], "M": st["M"], "V": st["V"], "survives": surv}


def analyze_records(design_cells: list[dict], main: list[dict], rep: list[dict] | None,
                    stage: str = "final") -> dict:
    rows, zc = [], []
    for cell in design_cells:
        okc = _ok_by_curve(main, cell["cell"], cell["n_curves"])
        row = {k: cell[k] for k in ("cell", "bits", "r", "n")}
        row["n_curves"] = cell["n_curves"]
        if len(okc) < cell["n_curves"]:
            row.update(cls="invalid", curves=len(okc), powered=None, planted_recovered=None,
                       replication=None, reason="fewer ok main-census records than n_curves")
            rows.append(row)
            continue
        st = cell_stats(list(okc.values()), cell["cell"] + "|main")
        cls, powered, planted = classify(st)
        row.update(st)
        row.update(cls=cls, powered=powered, planted_recovered=planted, replication=None)
        if powered and st["z_cal"] is not None:
            zc.append(st["z_cal"])
        rows.append(row)
    cal = calibration_gate(zc)
    cmap = {c["cell"]: c for c in design_cells}
    for row in rows:
        if row["cls"] == "flagged":
            row["replication"] = replication_of(cmap[row["cell"]], row, rep)
    classes = [r["cls"] for r in rows]
    frac = sum(c in VALID_CLASSES for c in classes) / len(rows) if rows else 0.0
    flagged = [r["cell"] for r in rows if r["cls"] == "flagged"]
    surv = [bool(r["replication"] and r["replication"]["survives"]) for r in rows if r["cls"] == "flagged"]
    pend = [r["replication"]["status"] != "complete" for r in rows if r["cls"] == "flagged"]
    outcome = reading(cal["pass"], frac, classes, surv, pend)
    slopes = {}
    for bits in BITS:
        for rk in RANKS:
            pts = [(math.log2(r["n"]), math.log(r["kappa"])) for r in rows
                   if r["cls"] in VALID_CLASSES and r["bits"] == bits and r["r"] == rk
                   and r["kappa"] is not None and r["kappa"] > 0]
            if len(pts) >= 3:
                mx = statistics.fmean(t for t, _ in pts)
                my = statistics.fmean(v for _, v in pts)
                sxx = sum((t - mx) ** 2 for t, _ in pts)
                slopes[f"b{bits}-r{rk}"] = sum((t - mx) * (v - my) for t, v in pts) / sxx
    powered_rows = [r for r in rows if r["powered"] and r.get("z") is not None]
    big = max(powered_rows, key=lambda r: abs(r["z"]), default=None)
    bad = [x for x in main + (rep or []) if x["status"] != "ok"]
    return {"experiment": EXP, "stage": stage, "outcome": outcome, "headline": headline_of(outcome),
            "calibration": cal, "fraction_valid": frac, "flagged_cells": flagged,
            "secondary_slope_logkappa_per_log2n": slopes,
            "largest_abs_z": {"cell": big["cell"], "z": big["z"]} if big else None,
            "powered_cells": len(powered_rows),
            "plant_infeasible_cells": [r["cell"] for r in rows if r.get("plant_feasible_all") is False],
            "null_mean_anomalies": [r["cell"] for r in rows if r.get("null_mean_over_formula") is not None
                                    and not GATES["anomaly_lo"] <= r["null_mean_over_formula"] <= GATES["anomaly_hi"]],
            "failed_jobs": [{"cell": x["cell"], "block": x["block"], "c": x["c"], "status": x["status"]}
                            for x in bad],
            "reading_note": ("O-PENDING-REPLICATION at analyze-final: the replication did not run; read as "
                             "O-MIXED pending repair" if stage == "final" and outcome == "O-PENDING-REPLICATION"
                             else None),
            "cells": rows}


# ---------------------------------------------------------------- subcommands

def _write_json(path: str, obj) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")


def cmd_design(a) -> None:
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "design.json"), "wb") as f:
        f.write(design_bytes())
    print("design.json written:", len(cells()), "cells")


def cmd_build(a) -> None:
    print("built", build_kernel(a.out))


# hand-built set with exactly one coincidence (2 + 8 = 4 + 6); p = 1009
HAND_P, HAND_SET = 1009, [1, 2, 4, 6, 8, 16]


def selftest_checks(kernel: str) -> list[dict]:
    checks: list[dict] = []

    def add(name, expected, observed):
        checks.append({"name": name, "expected": expected, "observed": observed,
                       "pass": expected == observed})

    n = 40
    # (1) kernel == brute force on null, log-GAP r = 1, 2, 3 and planted sets (45 sets)
    for bits in (12, 14, 16):
        for c in range(3):
            E, _ = get_curve(bits, "selftest", c)
            nulls = [null_builder(E, n, _rng("st-null", bits, c, k)) for k in range(NULL_REPS)]
            sets = {"null": nulls[0]}
            for rk in RANKS:
                sets[f"gap{rk}"] = gap_builder(E, rk, n, _rng("st-gap", bits, c, rk))[0]
            nc = [x[2] for x in run_kernel(kernel, E.p, nulls)]
            sets["plant"] = planted_builder(E, n, _rng("st-plant", bits, c), nc,
                                            lambda ls, E=E: run_kernel(kernel, E.p, [ls])[0][2])[0]
            for kind, ls in sets.items():
                k = run_kernel(kernel, E.p, [ls])[0]
                add(f"kernel-vs-brute:{kind}:b{bits}:c{c}", list(brute_CD(ls, E.p)), [k[2], k[3]])
    # (2) log-GAP builder == slow path (Curve.mul), order, distinctness, half-box bound
    for rk, (bits, c) in zip(RANKS, ((12, 0), (14, 1), (16, 2))):
        E, _ = get_curve(bits, "selftest", c)
        lab, meta, st = gap_builder(E, rk, n, _rng("st-slow", rk), keep_vectors=True)
        slow, dup, T = gap_slow(E, meta["points"], rk, n)
        add(f"builder-vs-slow:r{rk}", [slow, dup, T], [lab, meta["duplicate_skips"], meta["T"]])
        vecs = list(half_box_vectors(rk, T))
        add(f"builder-order:r{rk}", sorted(vecs) == vecs and len(set(vecs)) == len(vecs), True)
        vs = meta["vectors"]
        add(f"builder-vectors-in-order:r{rk}", [vs == sorted(vs), {tuple(v) for v in vs} <= set(vecs)],
            [True, True])
        add(f"distinct-labels:r{rk}", len(set(lab)) == len(lab) == n, True)
        add(f"half-box-bound:r{rk}",
            [half_box_size(rk, T) >= labels_needed(n), T == 1 or half_box_size(rk, T - 1) < labels_needed(n)],
            [True, True])
    # (3) forced tiny curve with n above the half-box / label universe -> degenerate
    E, _ = get_curve(8, "selftest", 0)
    add("degenerate-half-box", "degenerate", gap_builder(E, 2, 200, _rng("st-degenerate"))[2])
    # (4) hand-built set with exactly one planted coincidence is found with count 1
    k = run_kernel(kernel, HAND_P, [HAND_SET])[0]
    add("hand-built-one-coincidence", [1, 14], [k[2], k[3]])
    # (5) label scaling identity: u^2 X has the same C and D (12 sets)
    for i in range(12):
        bits = (14, 16)[i % 2]
        E, _ = get_curve(bits, "selftest", 3 + i % 3)
        rng = _rng("st-scale", i)
        X = null_builder(E, n, rng)
        u = rng.randrange(2, E.p)
        Y = [x * u * u % E.p for x in X]
        a1, a2 = run_kernel(kernel, E.p, [X, Y])
        add(f"scaling-identity:{i}", [a1[2], a1[3]], [a2[2], a2[3]])
    # (6) design table: 45 cells, anchors, cap not reached, byte-identical rewrite
    d = cells()
    add("design-cell-count", 45, len(d))
    by = {(c["bits"], c["n"]): c["n_curves"] for c in d}
    add("design-anchor-b28-n256", 1440, by[(28, 256)])
    add("design-anchor-b28-n512", 89, by[(28, 512)])
    add("design-cap-not-reached", True, all(c["n_curves"] < 2000 for c in d))
    add("design-bytes-deterministic", True, design_bytes() == design_bytes())
    return checks


def cmd_selftest(a) -> bool:
    """Instrument gate C1/C7. a.build is a directory holding the compiled kernel, or None."""
    import shutil
    import tempfile
    tmp = None
    if getattr(a, "build", None):
        kernel = os.path.join(a.build, "labelsum")
    else:
        tmp = tempfile.mkdtemp(prefix="bb0d26-build-")
        kernel = build_kernel(tmp)
    try:
        checks = selftest_checks(kernel)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    ok = all(c["pass"] for c in checks)
    os.makedirs(a.out, exist_ok=True)
    _write_json(os.path.join(a.out, "selftest.json"), {"pass": ok, "checks": checks})
    cmd_design(argparse.Namespace(out=a.out))
    print(f"selftest {'PASS' if ok else 'FAIL'} ({len(checks)} checks)")
    return ok


def cmd_census(a) -> None:
    os.makedirs(a.out, exist_ok=True)
    with open(a.design) as f:
        design = json.load(f)
    only = None
    if a.block == "rep":
        if not a.flags:
            raise SystemExit("census-toy --block rep needs --flags (flags.json of analyze-main)")
        with open(a.flags) as f:
            only = set(json.load(f)["flagged_cells"])
    todo = [(c, a.block, i) for c in design["toy_cells"] if only is None or c["cell"] in only
            for i in range(c["n_curves"])]
    out_path = os.path.join(a.out, f"toy-{a.block}-jobs.jsonl")
    open(out_path, "a").close()          # an empty jobs file is the recorded result when nothing is flagged
    import shutil
    import tempfile
    tmp, kernel = None, getattr(a, "kernel", None)
    if not kernel:
        tmp = tempfile.mkdtemp(prefix="bb0d26-build-")
        kernel = build_kernel(tmp)
    try:
        _run_jobs(kernel, todo, out_path, KINDS, getattr(a, "workers", WORKERS) or WORKERS)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


def cmd_analyze(a) -> dict:
    with open(a.design) as f:
        design = json.load(f)
    main = load_jsonl(a.main)
    rep = load_jsonl(a.rep) if getattr(a, "rep", None) and os.path.exists(a.rep) else None
    final = bool(getattr(a, "rep", None))
    an = analyze_records(design["toy_cells"], main, rep, "final" if final else "main")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    _write_json(a.out, an)
    _write_json(os.path.join(os.path.dirname(os.path.abspath(a.out)), "flags.json"),
                {"flagged_cells": an["flagged_cells"]})
    print("outcome", an["outcome"], "| headline", an["headline"], "| cells", len(an["cells"]),
          "| flagged", len(an["flagged_cells"]), "| calibration", an["calibration"])
    return an


# ---------------------------------------------------------------- supervisor trial entry

RUNS_DIR = os.path.normpath(os.path.join(HERE, "..", "runs"))


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit() -> tuple[str | None, bool | None]:
    try:
        c = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True, text=True, check=True)
        d = subprocess.run(["git", "status", "--porcelain", "--", HERE], cwd=HERE, capture_output=True,
                           text=True, check=True)
        return c.stdout.strip(), bool(d.stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return None, None


def code_hashes() -> dict:
    return {os.path.relpath(os.path.join(dp, fn), HERE): _sha256(os.path.join(dp, fn))
            for dp, dns, fns in os.walk(HERE) if "__pycache__" not in dp
            for fn in sorted(fns) if fn.endswith((".py", ".c"))}


def _gcc_version() -> str | None:
    try:
        return subprocess.run(["gcc", "--version"], capture_output=True, text=True,
                              check=True).stdout.splitlines()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return None


def cmd_trial(a) -> int:
    """One frozen trial of trial-plan.json, run by the supervisor in {run_dir}."""
    import platform
    import resource
    import shutil
    import tempfile
    import yaml

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(a.plan) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == a.trial_id)
    assert trial["run_id"] == a.run_id, "run id does not match the plan"
    rd = a.run_dir
    os.makedirs(rd, exist_ok=True)
    up = {k: (v if os.path.isabs(v) else os.path.join(RUNS_DIR, v))
          for k, v in trial.get("inputs_from", {}).items()}
    build = tempfile.mkdtemp(prefix="bb0d26-build-")
    status, reason, summary, code = "completed_valid", None, {}, 0
    try:
        kernel = build_kernel(build)
        stage = trial["stage"]
        if stage == "selftest":
            ok = cmd_selftest(argparse.Namespace(build=build, out=rd))
            with open(os.path.join(rd, "design.json")) as f:
                d = json.load(f)
            summary = {"selftest_pass": ok, "cells": len(d["toy_cells"]), "cells_ok": len(d["toy_cells"])}
            if not ok:
                status, code = "invalid_measurement", 1
                reason = "selftest failed: instrument defect; the experiment is void and no later trial is read"
        elif stage == "census":
            block = trial["block"]
            cmd_census(argparse.Namespace(kernel=kernel, design=up["design"], block=block,
                                          flags=up.get("flags"), out=rd, workers=WORKERS))
            recs = load_jsonl(os.path.join(rd, f"toy-{block}-jobs.jsonl"))
            bad = [r for r in recs if r["status"] != "ok"]
            summary = {"jobs": len(recs), "failed_infrastructure":
                       sum(r["status"].startswith("failed_infrastructure") for r in recs),
                       "degenerate": sum(r["status"] == "degenerate" for r in recs)}
            if bad:
                reason = (f"{len(bad)} jobs failed_infrastructure or degenerate; their cells are invalid in "
                          "this block, never null")
        elif stage == "analyze":
            out = os.path.join(rd, trial["output"])
            an = cmd_analyze(argparse.Namespace(design=up["design"], main=up["main"], rep=up.get("rep"), out=out))
            summary = {"outcome": an["outcome"], "headline": an["headline"],
                       "flagged_cells": an["flagged_cells"], "calibration": an["calibration"],
                       "fraction_valid": an["fraction_valid"]}
        else:
            raise ValueError(f"unknown stage {stage}")
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id,
                       "summary": summary, "invalid_reason": reason}, f, indent=1, sort_keys=True)
    except Exception as e:  # recorded as failed_infrastructure, never a metric
        status, reason, code = "failed", f"failed_infrastructure: {type(e).__name__}: {e}", 1
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id,
                       "summary": {}, "invalid_reason": reason}, f, indent=1)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    commit, dirty = _git_commit()
    ru_c, ru_s = resource.getrusage(resource.RUSAGE_CHILDREN), resource.getrusage(resource.RUSAGE_SELF)
    manifest = {"run": {
        "id": a.run_id, "experiment_id": EXP, "hypothesis_id": HYPOTHESIS_ID,
        "task_id": plan.get("task_id"), "trial_id": a.trial_id, "role": "executor",
        "recorded_at": started[:10], "status": status,
        "validity": {"status": status, "reason": reason or "run.py recorded no invalidation; check.py "
                     "and independent review decide validity", "failure_class": None},
        "code": {"commit": commit, "dirty": dirty, "branch": None,
                 "command": " ".join([sys.executable, *sys.argv]), "code_sha256": code_hashes(),
                 "trial_plan_sha256": _sha256(a.plan), "working_directory": os.getcwd()},
        "environment": {"host": platform.node(), "operating_system": platform.platform(),
                        "python_version": sys.version.split()[0], "gcc_version": _gcc_version(),
                        "processor_count": os.cpu_count(),
                        "source": "manifest.yaml /run/environment"},
        "inputs": {"curve_id": None, "seed": SEED_BLOCK,
                   "parameters": {"trial_id": a.trial_id, "stage": trial["stage"],
                                  "inputs_from": trial.get("inputs_from", {}), "plan": a.plan,
                                  "gcc_flags": GCC_FLAGS, "workers": WORKERS,
                                  "kernel_timeout_s": KERNEL_TIMEOUT_S, "null_reps": NULL_REPS}},
        "timing": {"started_at": started, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "wall_seconds": round(time.time() - t0, 3)},
        "resources": {"peak_rss_bytes": int(max(ru_c.ru_maxrss, ru_s.ru_maxrss) * 1024),
                      "cpu_seconds": round(ru_c.ru_utime + ru_c.ru_stime + ru_s.ru_utime + ru_s.ru_stime, 3)},
        "result": {"metrics": {"raw_result": "raw-result.json"} if code == 0 else {},
                   "valid": status == "completed_valid", "invalid_reason": reason,
                   "raw_result": "raw-result.json",
                   "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                                   "note": "exact coincidence counts on generated toy curves; no discrete "
                                           "logarithm, relation or speedup is claimed"}},
        "artifacts": [n for n in trial["artifacts"] if n != "manifest.yaml"],
    }}
    with open(os.path.join(rd, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    return code


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("trial")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--run-id", required=True)
    s.add_argument("--trial-id", required=True)
    s.add_argument("--plan", required=True)
    s.set_defaults(f=cmd_trial)
    s = sub.add_parser("design")
    s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_design)
    s = sub.add_parser("selftest")
    s.add_argument("--out", required=True)
    s.set_defaults(f=lambda a: 0 if cmd_selftest(argparse.Namespace(build=None, out=a.out)) else 1)
    s = sub.add_parser("census-toy")
    s.add_argument("--kernel", help="compiled labelsum binary; built into a temporary directory if absent")
    s.add_argument("--design", required=True)
    s.add_argument("--block", choices=("main", "rep", "selftest"), required=True)
    s.add_argument("--flags")
    s.add_argument("--out", required=True)
    s.add_argument("--workers", type=int, default=WORKERS)
    s.set_defaults(f=cmd_census)
    s = sub.add_parser("analyze")
    s.add_argument("--design", required=True)
    s.add_argument("--main", required=True)
    s.add_argument("--rep")
    s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_analyze)
    s = sub.add_parser("build")
    s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_build)
    a = ap.parse_args()
    r = a.f(a)
    sys.exit(r if isinstance(r, int) else 0)


if __name__ == "__main__":
    main()
