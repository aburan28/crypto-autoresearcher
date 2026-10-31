"""EXP-PFDR-2d36f9: growth ladder of pair-sum coincidences, window and rank-d GAP bases.

Frozen-contract driver (experiments/EXP-PFDR-2d36f9/specification.yaml is the
authority; this file is bound by sha256 in trial-plan.json). Standard library
only, plus the vendored copy of src/crypto_autoresearcher/index_calculus/curve.py
and the C kernel paircount.c.

Subcommands (each writes only under --out):
  build      compile paircount.c -> <out>/paircount
  selftest   kernel == brute-force count; builder and order-certification checks
  pilot      sizing and plant design on the pilot curve block -> design.json
  census     main or replication block for the cells in design.json -> jobs.jsonl
  analyze    frozen line statistics, controls and reading -> analysis file
  reanalysis descriptive stage-1 re-analysis of EXP-PFDR-ca5e01 -> reanalysis.json
  trial      one frozen trial of trial-plan.json (supervisor entry point)

Counting convention (CC), unchanged from EXP-PFDR-ca5e01: for a symmetric base
F (F = -F) of exactly b points, C(F) = sum over s != O of binom(m_s, 2), with
m_s the number of unordered pairs {P, Q}, P != Q, Q != -P, with P + Q = s. The
null is 20 uniformly random symmetric bases of the same b on the same curve.
"""
from __future__ import annotations

import argparse
import hashlib
import gzip
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import curve as ec  # noqa: E402  (vendored, sha256-pinned)

EXP = "EXP-PFDR-2d36f9"
BITS = (16, 20, 24, 28, 32)
THETAS = (0.30, 0.35)
DIMS = (1, 2, 3)
GAMMAS = ("0", "1/6", "1/3", "1/2")
B_MIN, B_MAX = 16, 4096
NULL_REPS = 20
TARGET_COINC = 2500
N_MIN, N_MAX = 10, 4000
PILOT_CURVES = 8
SEED_BLOCK = {"pilot": 6_000_000, "main": 6_100_000, "rep": 6_200_000, "selftest": 6_900_000}
KERNEL_TIMEOUT_S = 3600
WORKERS = 4

PLANT_PREFIX = 1.3
PLANT_SLOPE_TOL = 0.03
PLANT_GAMMA_TOL = 0.05
ZN_TOL = 0.05
DELTA_STAR = 1.0 / 3.0
RATIO_STAR = 6.35
CAL_SD_LO, CAL_SD_HI, CAL_MEAN_ABS = 0.70, 1.30, 0.40
BOOT_B = 2000


def _rng(*labels: object) -> random.Random:
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


def _gamma_value(gamma: str) -> float:
    return float(Fraction(gamma))


def cell_name(bits: int, theta: float, d: int) -> str:
    return f"b{bits}-t{theta:.2f}-d{d}"


def cells() -> list[dict]:
    out = []
    for bits in BITS:
        for th in THETAS:
            b = 2 * round((2.0 ** (bits * th)) / 2)
            assert B_MIN <= b <= B_MAX, (bits, th, b)
            for d in DIMS:
                out.append({"cell": cell_name(bits, th, d), "bits": bits,
                            "theta": th, "d": d, "b": b})
    return out


def certify_curve(E, G, bits: int, seed: int) -> dict:
    p = E.p
    N = E.order
    hasse = abs(N - (p + 1)) <= 2 * math.isqrt(p)
    prime = ec.is_probable_prime(N)
    pts_ok = 0
    for i in range(4):
        Q = E.random_point(_rng("ordcert", bits, seed, i))
        if E.mul(N, Q) is None:
            pts_ok += 1
    return {"bits": bits, "seed": seed, "p": p, "N": N, "N_prime": bool(prime),
            "hasse": bool(hasse), "hasse_margin": abs(N - (p + 1)),
            "hasse_radius": 2 * math.isqrt(p), "points_ok": pts_ok,
            "pass": bool(prime and hasse and pts_ok == 4)}


def get_curve(bits: int, block: str, c: int):
    if c >= 4000:
        raise ValueError("curve index c must be < 4000")
    seed = SEED_BLOCK[block] + c
    E, G = ec.generate_prime_order_curve(bits, seed=seed)
    cert = certify_curve(E, G, bits, seed)
    return E, G, cert


def _lift(E, x: int):
    r = E.rhs(x)
    if r == 0:
        return None
    y = ec.sqrt_mod(r, E.p)
    return None if y is None else y


def _add_pair(E, pts: list, seen: set, x: int) -> bool:
    if x in seen:
        return False
    seen.add(x)
    y = _lift(E, x)
    if y is None:
        return False
    pts.append((x, y))
    pts.append((x, (-y) % E.p))
    return True


def null_base(E, b: int, rng: random.Random, avoid: set | None = None) -> list:
    pts: list = []
    seen = set(avoid or ())
    while len(pts) < b:
        _add_pair(E, pts, seen, rng.randrange(E.p))
    return pts


def window_base(E, b: int, rng: random.Random) -> tuple[list, dict]:
    x0 = rng.randrange(E.p)
    pts: list = []
    seen: set = set()
    k = 0
    while len(pts) < b:
        _add_pair(E, pts, seen, (x0 + k) % E.p)
        k += 1
    return pts, {"x0": x0, "span": k}


def gap_base(E, b: int, d: int, rng: random.Random) -> tuple[list, dict]:
    """Rank-d GAP x0 + a + c*w1 (+ e*w2), box sides ~ b^(1/d), filled in
    lexicographic order (outermost index last) until exactly b points."""
    x0 = rng.randrange(E.p)
    ws = [rng.randrange(1, E.p) for _ in range(d - 1)]
    side = max(2, math.ceil(b ** (1.0 / d)))
    pts: list = []
    seen: set = set()
    n = 0
    while len(pts) < b:
        digits, q = [], n
        for _ in range(d - 1):
            digits.append(q % side)
            q //= side
        digits.append(q)  # outermost index is unbounded: fills the last layer partially
        x = (x0 + digits[0] + sum(di * w for di, w in zip(digits[1:], ws))) % E.p
        _add_pair(E, pts, seen, x)
        n += 1
        if n > 50 * b + 1000:
            raise RuntimeError("GAP enumeration did not reach b points")
    return pts, {"x0": x0, "w": ws, "side": side, "enumerated": n}


def gamma_plant_base(E, G, b: int, L: int, rng: random.Random) -> list:
    """{+-kG : 1 <= k <= L} plus uniform symmetric fill avoiding the planted x."""
    pts: list = []
    seen: set = set()
    Q = None
    for _ in range(L):
        Q = G if Q is None else E.add(Q, G)
        x, y = Q
        seen.add(x)
        pts.append((x, y))
        pts.append((x, (-y) % E.p))
    while len(pts) < b:
        _add_pair(E, pts, seen, rng.randrange(E.p))
    return pts


def zn_interval_base(E, G, b: int) -> list:
    """{+-kG : 1 <= k <= b/2}, exactly b points (b is even by construction)."""
    if b % 2:
        raise ValueError("Z/N interval base needs even b")
    pts: list = []
    Q = None
    for _ in range(b // 2):
        Q = G if Q is None else E.add(Q, G)
        x, y = Q
        pts.append((x, y))
        pts.append((x, (-y) % E.p))
    return pts


def plant_internal(L: int) -> int:
    """Exact nontrivial coincidences inside {kG : 1 <= |k| <= L} (L < N/4).

    K = [-L, L] minus 0. For s != 0, |s| <= 2L, the ordered pairs (i, j) in K^2
    with i + j = s number (2L + 1 - |s|) minus 2 when 1 <= |s| <= L (i = 0 or
    j = 0); removing the diagonal i = j = s/2 and halving gives m_s. Checked
    against a group brute force in selftest."""
    tot = 0
    for s in range(1, 2 * L + 1):  # m_s = m_{-s}
        ordered = (2 * L + 1 - s) - (2 if s <= L else 0)
        diag = 1 if s % 2 == 0 and s // 2 <= L else 0
        m = (ordered - diag) // 2
        tot += 2 * (m * (m - 1) // 2)
    return tot


def plant_bracket(target: float, b: int) -> dict:
    """Smallest L whose plant_internal reaches target, with the seeded-rounding bracket."""
    cap = max(1, b // 4)
    if target <= plant_internal(1):
        return {"L_lo": 1, "L_hi": 1, "p_hi": 0.0, "feasible": True, "L_cap": cap,
                "target": target}
    for L in range(2, cap + 1):
        hi = plant_internal(L)
        if hi >= target:
            lo = plant_internal(L - 1)
            p_hi = (target - lo) / (hi - lo) if hi > lo else 0.0
            return {"L_lo": L - 1, "L_hi": L, "p_hi": p_hi, "feasible": True,
                    "L_cap": cap, "target": target}
    return {"L_lo": cap, "L_hi": cap, "p_hi": 0.0, "feasible": False,
            "L_cap": cap, "target": target}


def plant_L_for_curve(cfg: dict, block: str, bits: int, theta: float, gamma: str,
                      c: int) -> int:
    if not cfg["feasible"] or cfg["L_hi"] <= cfg["L_lo"] or cfg["p_hi"] <= 0.0:
        return cfg["L_lo"]
    rng = _rng("plantL", block, bits, theta, gamma, c)
    return cfg["L_hi"] if rng.random() < cfg["p_hi"] else cfg["L_lo"]


def run_kernel(kernel: str, E, bases: list[list]) -> list[tuple[int, int, int]]:
    lines = [f"{E.p} {E.a}"]
    for B in bases:
        lines.append(str(len(B)))
        lines.extend(f"{x} {y}" for x, y in B)
    proc = subprocess.run([kernel], input="\n".join(lines) + "\n", capture_output=True,
                          text=True, timeout=KERNEL_TIMEOUT_S, check=True)
    out = [tuple(map(int, ln.split())) for ln in proc.stdout.strip().splitlines()]
    if len(out) != len(bases):
        raise RuntimeError(f"kernel returned {len(out)} lines for {len(bases)} bases")
    return out


def job(kernel: str, cell: dict, block: str, c: int, plant_cfgs: list | None = None,
        nulls_only: bool = False) -> dict:
    t0 = time.time()
    bits, theta, d, b = cell["bits"], cell["theta"], cell["d"], cell["b"]
    E, G, cert = get_curve(bits, block, c)
    rec = {"cell": cell["cell"], "bits": bits, "theta": theta, "d": d, "block": block,
           "c": c, "p": E.p, "a": E.a, "b_coef": E.b, "N": E.order, "b": b,
           "order": cert, "status": "ok"}
    try:
        nb = [null_base(E, b, _rng("null", block, bits, theta, c, r)) for r in range(NULL_REPS)]
        res = run_kernel(kernel, E, nb)
        rec["null"] = [r[2] for r in res]
        rec["pairs"] = res[0][1]
        if nulls_only:
            rec["seconds"] = round(time.time() - t0, 3)
            return rec
        if d == 1:
            sb, meta = window_base(E, b, _rng("struct", block, bits, theta, d, c))
        else:
            sb, meta = gap_base(E, b, d, _rng("struct", block, bits, theta, d, c))
        zb = zn_interval_base(E, G, b)
        bases = [sb] + [gamma_plant_base(E, G, b, pcfg["L"],
                                         _rng("plant", block, bits, theta, pcfg["gamma"], c))
                        for pcfg in plant_cfgs]
        res2 = run_kernel(kernel, E, bases + [zb])
        rec.update({"struct": res2[0][2], "struct_meta": meta, "struct_pairs": res2[0][1],
                    "zn": res2[-1][2], "zn_pairs": res2[-1][1],
                    "plant": {}, "plant_L": {}, "plant_internal": {}, "plant_feasible": {}})
        for i, pcfg in enumerate(plant_cfgs):
            g = pcfg["gamma"]
            rec["plant"][g] = res2[1 + i][2]
            rec["plant_L"][g] = pcfg["L"]
            rec["plant_internal"][g] = plant_internal(pcfg["L"])
            rec["plant_feasible"][g] = bool(pcfg["feasible"])
    except subprocess.TimeoutExpired:
        rec["status"] = "failed_infrastructure:timeout"
    except subprocess.CalledProcessError as e:
        rec["status"] = f"failed_infrastructure:kernel_exit_{e.returncode}"
    rec["seconds"] = round(time.time() - t0, 3)
    return rec


def _done_keys(path: str) -> set:
    keys = set()
    if os.path.exists(path):
        with open(path) as f:
            for ln in f:
                r = json.loads(ln)
                if r.get("status") == "ok":
                    keys.add((r["cell"], r["block"], r["c"]))
    return keys


def _run_jobs(kernel: str, todo: list, out_path: str, nulls_only: bool) -> None:
    done = _done_keys(out_path)
    todo = [t for t in todo if (t[0]["cell"], t[1], t[2]) not in done]
    todo.sort(key=lambda t: -t[0]["b"])  # largest bases first for load balance
    print(f"jobs to run: {len(todo)} (already done: {len(done)})", flush=True)
    with ProcessPoolExecutor(max_workers=WORKERS) as pool, open(out_path, "a") as f:
        futs = [pool.submit(job, kernel, cell, block, c, cfgs, nulls_only)
                for cell, block, c, cfgs in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            f.write(json.dumps(fut.result(), sort_keys=True) + "\n")
            f.flush()
            if i % 200 == 0 or i == len(futs):
                print(f"  {i}/{len(futs)}", flush=True)


def _load(path: str) -> list[dict]:
    # Large run artifacts are stored gzipped (AGENTS.md artifact policy); read
    # the stored form transparently when the plain path is absent.
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path = path + ".gz"
    if path.endswith(".gz"):
        with gzip.open(path, "rt") as f:
            return [json.loads(ln) for ln in f]
    with open(path) as f:
        return [json.loads(ln) for ln in f]


def _ols(xs: list, ys: list) -> tuple[float, float, list]:
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0 or n < 2:
        return float("nan"), float("nan"), [float("nan")] * n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    intercept = my - slope * mx
    return slope, intercept, [y - (intercept + slope * x) for x, y in zip(xs, ys)]


def _pct(sorted_vals: list, q_lo: float, q_hi: float) -> tuple[float, float]:
    if not sorted_vals:
        return float("nan"), float("nan")
    n = len(sorted_vals)
    return sorted_vals[min(n - 1, int(q_lo * n))], sorted_vals[min(n - 1, max(0, int(q_hi * n) - 1))]


def cell_stats(rs: list[dict], kind: str = "struct") -> dict:
    rs = sorted(rs, key=lambda r: r["c"])
    if kind == "struct":
        Ss = [r["struct"] for r in rs]
        Ms = [statistics.fmean(r["null"]) for r in rs]
        Vs = [statistics.variance(r["null"]) for r in rs]
    elif kind == "zn":
        Ss = [r["zn"] for r in rs]
        Ms = [statistics.fmean(r["null"]) for r in rs]
        Vs = [statistics.variance(r["null"]) for r in rs]
    elif kind.startswith("plant:"):
        g = kind.split(":", 1)[1]
        Ss = [r["plant"][g] for r in rs]
        Ms = [statistics.fmean(r["null"]) for r in rs]
        Vs = [statistics.variance(r["null"]) for r in rs]
    elif kind == "aa":
        Ss = [r["null"][0] for r in rs]
        Ms = [statistics.fmean(r["null"][1:]) for r in rs]
        Vs = [statistics.variance(r["null"][1:]) for r in rs]
    else:
        raise ValueError(kind)
    S, M, V = sum(Ss), sum(Ms), sum(Vs)
    denom_sd = math.sqrt(V * (1 + 1 / NULL_REPS)) if V > 0 else float("nan")
    kappa = S / M if M > 0 else float("nan")
    pS = sum(r["null"][0] for r in rs)
    pM = sum(statistics.fmean(r["null"][1:]) for r in rs)
    pV = sum(statistics.variance(r["null"][1:]) for r in rs)
    z_cal = (pS - pM) / math.sqrt(pV * (1 + 1 / (NULL_REPS - 1))) if pV > 0 else float("nan")
    return {"curves": len(rs), "S": S, "M": M, "V": V, "kappa": kappa,
            "z": (S - M) / denom_sd if denom_sd == denom_sd and denom_sd > 0 else float("nan"),
            "z_cal": z_cal, "S_by_curve": Ss, "M_by_curve": Ms}


def _rung_entry(cell: dict, recs: list[dict], kind: str, n_curves: int) -> dict | None:
    rs = [r for r in recs if r["cell"] == cell["cell"]]
    if not rs:
        return None
    st = cell_stats(rs, kind)
    return {"cell": cell["cell"], "bits": cell["bits"], "d": cell["d"],
            "n_curves": n_curves, "curves": len(rs), "stats": st,
            "Nbar": statistics.fmean(math.log2(r["N"]) for r in rs),
            "ok": len(rs) >= n_curves and st["M"] >= TARGET_COINC}


def build_line(label: str, kind: str, theta: float, variant,
               design: dict, recs: list[dict]) -> dict:
    cellmap = {c["cell"]: c for c in design["cells"]}
    entries = []
    for bits in BITS:
        d = variant if kind in ("struct", "aa") else 1
        cell = cellmap[cell_name(bits, theta, d)]
        n_curves = cell.get("n_curves", 0)
        entries.append(_rung_entry(cell, recs, kind, n_curves))
    row = {"label": label, "kind": "plant" if kind.startswith("plant") else kind,
           "theta": theta,
           "d": variant if kind in ("struct", "aa") else None,
           "gamma": variant if kind.startswith("plant") else None,
           "kappa_by_rung": []}
    if any(e is None for e in entries):
        row.update({"valid": False, "invalid_reason": "missing rung records",
                    "class": "invalid", "delta_hat": float("nan"),
                    "ci95": [float("nan"), float("nan")], "residuals": []})
        return row
    valid = all(e["ok"] for e in entries)
    reasons = []
    for e in entries:
        if e["curves"] < e["n_curves"]:
            reasons.append(f"{e['cell']} has {e['curves']} ok records for {e['n_curves']} curves")
        if e["stats"]["M"] < TARGET_COINC:
            reasons.append(f"{e['cell']} M {e['stats']['M']:.1f} < {TARGET_COINC}")
    for e in entries:
        row["kappa_by_rung"].append({
            "cell": e["cell"], "bits": e["bits"], "Nbar": e["Nbar"],
            "S": e["stats"]["S"], "M": e["stats"]["M"], "kappa": e["stats"]["kappa"],
            "z": e["stats"]["z"], "curves": e["curves"], "n_curves": e["n_curves"]})
    xs = [e["Nbar"] for e in entries]
    ys = [math.log2(e["stats"]["kappa"]) if e["stats"]["kappa"] > 0 else float("nan")
          for e in entries]
    delta, _, resid = _ols(xs, ys)
    row.update({"valid": bool(valid), "invalid_reason": "; ".join(reasons) or None,
                "delta_hat": delta, "residuals": resid})
    if valid:
        rng = _rng("boot", label)
        rep_kappa = [[] for _ in entries]
        for _ in range(BOOT_B):
            kk = []
            for e in entries:
                sv, mv = e["stats"]["S_by_curve"], e["stats"]["M_by_curve"]
                n = len(sv)
                S = M = 0.0
                for _ in range(n):
                    i = rng.randrange(n)
                    S += sv[i]
                    M += mv[i]
                kk.append(S / M if M > 0 else float("nan"))
            for j, k in enumerate(kk):
                rep_kappa[j].append(k)
        boot_deltas = []
        for b in range(BOOT_B):
            ky = [math.log2(rep_kappa[j][b]) if rep_kappa[j][b] > 0 else float("nan")
                  for j in range(len(entries))]
            if all(v == v for v in ky):
                boot_deltas.append(_ols(xs, ky)[0])
        boot_deltas.sort()
        lo, hi = _pct(boot_deltas, 0.025, 0.975)
        row["ci95"] = [lo, hi]
        row["bootstrap_replicates"] = len(boot_deltas)
        for j in range(len(entries)):
            vals = sorted(v for v in rep_kappa[j] if v == v and v > 0)
            row["kappa_by_rung"][j]["ci95"] = list(_pct(vals, 0.025, 0.975))
        idx = {bits: i for i, bits in enumerate(BITS)}
        for name, (a, b) in (("ratio_16_24", (16, 24)), ("ratio_24_32", (24, 32))):
            vals = sorted(rep_kappa[idx[b]][i] / rep_kappa[idx[a]][i]
                          for i in range(BOOT_B)
                          if rep_kappa[idx[a]][i] > 0 and rep_kappa[idx[b]][i] > 0)
            row[name] = {"value": (row["kappa_by_rung"][idx[b]]["kappa"]
                                   / row["kappa_by_rung"][idx[a]]["kappa"]
                                   if row["kappa_by_rung"][idx[a]]["kappa"] > 0 else float("nan")),
                         "ci95": list(_pct(vals, 0.025, 0.975)), "R_star": RATIO_STAR}
        row["class"] = classify(valid, row["ci95"][0], row["ci95"][1])
    else:
        row.update({"ci95": [float("nan"), float("nan")], "class": "invalid",
                    "ratio_16_24": None, "ratio_24_32": None})
    return row


def classify(valid: bool, lower: float, upper: float) -> str:
    if not valid:
        return "invalid"
    if lower > 0 and upper >= DELTA_STAR:
        return "ALIVE"
    if lower > 0 and upper < DELTA_STAR:
        return "SUB-BE-GROWING"
    if lower <= 0 and upper < DELTA_STAR:
        return "SUB-BE"
    return "UNRESOLVED"


def build_design(recs: list[dict]) -> dict:
    ok = [r for r in recs if r.get("status") == "ok"]
    per_rung_N: dict = {}
    for r in ok:
        per_rung_N.setdefault(r["bits"], {})[r["c"]] = r["N"]
    Lbar = {bits: statistics.fmean(math.log2(n) for n in vals.values())
            for bits, vals in per_rung_N.items() if vals}
    design = {"experiment": EXP,
              "rule": f"n = clamp(ceil(1.1*{TARGET_COINC}/mean_null), {N_MIN}, {N_MAX}); "
                      f"mean_null over {PILOT_CURVES} pilot curves x {NULL_REPS} nulls",
              "null_reps": NULL_REPS, "pilot_curves": PILOT_CURVES,
              "seed_blocks": dict(SEED_BLOCK), "Lbar": {str(k): v for k, v in Lbar.items()},
              "cells": [], "plants": []}
    mean_null: dict = {}
    n_by_cell: dict = {}
    for cell in cells():
        rs = [r for r in ok if r["cell"] == cell["cell"]]
        if len({r["c"] for r in rs}) < PILOT_CURVES:
            design["cells"].append({**cell, "status": "pilot_incomplete"})
            continue
        mn = statistics.fmean(x for r in rs for x in r["null"])
        n = N_MAX if mn <= 0 else min(N_MAX, max(N_MIN, math.ceil(1.1 * TARGET_COINC / mn)))
        design["cells"].append({**cell, "status": "ok", "pilot_mean_null": mn,
                                "n_curves": n, "expected_null_total": n * mn})
        mean_null[(cell["bits"], cell["theta"])] = mn
        n_by_cell[cell["cell"]] = n
    if len(Lbar) != len(BITS):
        return design
    for theta in THETAS:
        for gamma in GAMMAS:
            pts_internal, pts_design = [], []
            for bits in BITS:
                cell = next(c for c in design["cells"]
                            if c["cell"] == cell_name(bits, theta, 1))
                if cell.get("status") != "ok":
                    continue
                mn = mean_null[(bits, theta)]
                K = PLANT_PREFIX * 2.0 ** (_gamma_value(gamma) * (Lbar[bits] - Lbar[16]))
                cfg = plant_bracket((K - 1.0) * mn, cell["b"])
                n = cell["n_curves"]
                Ls = [plant_L_for_curve(cfg, "main", bits, theta, gamma, c) for c in range(n)]
                pooled = statistics.fmean(plant_internal(L) for L in Ls) if Ls else float("nan")
                design["plants"].append({
                    "bits": bits, "theta": theta, "gamma": gamma,
                    "target": cfg["target"], "pilot_mean_null": mn,
                    "L_lo": cfg["L_lo"], "L_hi": cfg["L_hi"], "p_hi": cfg["p_hi"],
                    "L_cap": cfg["L_cap"], "feasible": cfg["feasible"],
                    "L_per_curve": Ls, "pooled_internal": pooled,
                    "gamma_design": None})
                pts_internal.append(math.log2(1.0 + pooled / mn) if mn > 0 else float("nan"))
                pts_design.append(Lbar[bits])
            if len(pts_internal) == len(BITS):
                gd = _ols(pts_design, pts_internal)[0]
                for p in design["plants"]:
                    if p["theta"] == theta and p["gamma"] == gamma:
                        p["gamma_design"] = gd
    return design


def plant_cfgs_for(design: dict, cell: dict, block: str, c: int) -> list[dict]:
    out = []
    for g in GAMMAS:
        p = next(p for p in design["plants"]
                 if p["bits"] == cell["bits"] and p["theta"] == cell["theta"]
                 and p["gamma"] == g)
        if block == "main" and c < len(p["L_per_curve"]):
            L = p["L_per_curve"][c]
        else:
            L = plant_L_for_curve(p, block, cell["bits"], cell["theta"], g, c)
        out.append({"gamma": g, "L": L, "feasible": p["feasible"]})
    return out


def _plant_gamma_design(design: dict, theta: float, gamma: str) -> float:
    p = next((p for p in design["plants"] if p["theta"] == theta and p["gamma"] == gamma), None)
    if p is None or p.get("gamma_design") is None:
        return float("nan")
    return float(p["gamma_design"])


def _ci_contains_zero(ci) -> bool:
    return ci[0] <= 0 <= ci[1]


def evaluate(design: dict, main_all: list[dict], rep_all: list[dict], selftest_pass: bool,
             block: str) -> dict:
    cellmap = {c["cell"]: c for c in design["cells"]}
    main = [r for r in main_all if r.get("status") == "ok"]
    rep = [r for r in rep_all if r.get("status") == "ok"]
    struct_lines = []
    for theta in THETAS:
        for d in DIMS:
            label = f"structured|theta={theta:.2f}|d={d}"
            struct_lines.append(build_line(label, "struct", theta, d, design, main))
    plant_lines = []
    zn_lines = []
    if design.get("plants"):
        for theta in THETAS:
            for gamma in GAMMAS:
                label = f"plant|theta={theta:.2f}|gamma={gamma}"
                row = build_line(label, f"plant:{gamma}", theta, gamma, design, main)
                row["gamma_design"] = _plant_gamma_design(design, theta, gamma)
                row["gamma_target"] = _gamma_value(gamma)
                plant_lines.append(row)
        for theta in THETAS:
            label = f"zn|theta={theta:.2f}"
            row = build_line(label, "zn", theta, None, design, main)
            row["expected_slope"] = 1.0 - theta
            zn_lines.append(row)
    aa_lines = []
    for theta in THETAS:
        for d in DIMS:
            label = f"aa|theta={theta:.2f}|d={d}"
            aa_lines.append(build_line(label, "aa", theta, d, design, main))

    cells = []
    for cell in design["cells"]:
        rs = [r for r in main if r["cell"] == cell["cell"]]
        row = {k: cell[k] for k in ("cell", "bits", "theta", "d", "b")}
        if cell.get("status") != "ok" or len(rs) < cell.get("n_curves", 1):
            row.update({"class_label": "invalid", "curves": len(rs)})
            cells.append(row)
            continue
        st = cell_stats(rs, "struct")
        row.update({"curves": len(rs), "n_curves": cell["n_curves"],
                    "S": st["S"], "M": st["M"], "V": st["V"], "kappa": st["kappa"],
                    "z": st["z"], "z_cal": st["z_cal"],
                    "Nbar": statistics.fmean(math.log2(r["N"]) for r in rs)})
        cells.append(row)

    zcal = [r["z_cal"] for r in cells if "z_cal" in r]
    cal = {"n": len(zcal),
           "mean": statistics.fmean(zcal) if zcal else None,
           "sd": statistics.pstdev(zcal) if len(zcal) > 1 else None}
    cal["pass"] = bool(zcal) and cal["sd"] is not None \
        and CAL_SD_LO <= cal["sd"] <= CAL_SD_HI and abs(cal["mean"]) <= CAL_MEAN_ABS

    c3 = {"name": "gamma-slope plants", "detail": [], "pass": bool(plant_lines)}
    for theta in THETAS:
        if not plant_lines:
            break
        for gamma in GAMMAS:
            row = next(r for r in plant_lines if r["theta"] == theta and r["gamma"] == gamma)
            d_slope_ok = row["valid"] and abs(row["delta_hat"] - row["gamma_design"]) <= PLANT_SLOPE_TOL
            d_gamma_ok = row["valid"] and abs(row["gamma_design"] - _gamma_value(gamma)) <= PLANT_GAMMA_TOL
            item = {"theta": theta, "gamma": gamma, "class": row["class"],
                    "delta_hat": row["delta_hat"], "gamma_design": row["gamma_design"],
                    "slope_ok": bool(d_slope_ok), "design_ok": bool(d_gamma_ok)}
            blocking = True
            if gamma == "0":
                blocking = d_slope_ok and d_gamma_ok and row["class"] == "SUB-BE"
            elif gamma == "1/6":
                blocking = d_slope_ok and d_gamma_ok and row["class"] == "SUB-BE-GROWING"
            elif gamma == "1/2":
                blocking = d_slope_ok and d_gamma_ok and row["class"] == "ALIVE"
            else:
                item["reported_only"] = "class"
                blocking = d_slope_ok and d_gamma_ok
            item["blocking"] = bool(blocking)
            c3["pass"] = c3["pass"] and blocking
            c3["detail"].append(item)

    c4 = {"name": "Z/N interval", "detail": [], "pass": bool(zn_lines)}
    for theta in THETAS:
        if not zn_lines:
            break
        row = next(r for r in zn_lines if r["theta"] == theta)
        ok = row["valid"] and abs(row["delta_hat"] - (1.0 - theta)) <= ZN_TOL \
            and row["class"] == "ALIVE"
        c4["detail"].append({"theta": theta, "delta_hat": row["delta_hat"],
                             "expected": 1.0 - theta, "class": row["class"],
                             "pass": bool(ok)})
        c4["pass"] = c4["pass"] and ok

    aa_cover = sum(1 for r in aa_lines if r["valid"] and _ci_contains_zero(r["ci95"]))
    aa_alive = [r["label"] for r in aa_lines if r["class"] == "ALIVE"]
    c5 = {"name": "A/A null line", "cover_zero": aa_cover, "alive_lines": aa_alive,
          "pass": bool(aa_cover >= 5 and not aa_alive),
          "detail": [{"label": r["label"], "delta_hat": r["delta_hat"],
                      "ci95": r["ci95"], "class": r["class"]} for r in aa_lines]}
    c6 = {"name": "z_cal calibration", "sd": cal["sd"], "mean": cal["mean"],
          "sd_band": [CAL_SD_LO, CAL_SD_HI], "mean_band_abs": CAL_MEAN_ABS,
          "pass": bool(cal["pass"])}

    valid_struct = [r for r in struct_lines if r["valid"]]
    alive = [r for r in valid_struct if r["class"] == "ALIVE"]
    controls = {"C3": c3, "C4": c4, "C5": c5, "C6": c6}
    blocking_pass = all(controls[k]["pass"] for k in ("C3", "C4", "C5", "C6"))

    if block != "main":
        for row in alive:
            label = row["label"]
            theta, d = row["theta"], row["d"]
            rungs = []
            for bits in BITS:
                cell = cellmap[cell_name(bits, theta, d)]
                rs = [r for r in rep if r["cell"] == cell["cell"]]
                rungs.append({"bits": bits, "rs": rs, "cell": cell})
            lr = _replication_line(label, theta, d, rungs, design, rep)
            row["replication"] = lr
    else:
        for row in alive:
            row["replication"] = {"complete": False, "survives": None,
                                  "reason": "replication not run"}

    if not selftest_pass or not blocking_pass or len(valid_struct) < 5:
        reading = "O-INVALID"
    elif any(r.get("replication", {}).get("survives") for r in alive):
        reading = "O-ALIVE"
    elif block == "main" and any(r.get("replication", {}).get("complete") is False
                                 for r in alive):
        reading = "O-PENDING-REPLICATION"
    elif valid_struct and all(r["class"] in ("SUB-BE", "SUB-BE-GROWING")
                              for r in valid_struct):
        reading = "O-SUB-BE"
    else:
        reading = "O-MIXED"

    be_met = any(r.get("replication", {}).get("survives")
                 and r["replication"].get("delta_hat", float("nan")) >= DELTA_STAR
                 for r in alive)
    infeasible = [{"bits": p["bits"], "theta": p["theta"], "gamma": p["gamma"],
                   "L_cap": p["L_cap"]} for p in design.get("plants", []) if not p["feasible"]]
    failed = [{"cell": r["cell"], "c": r["c"], "status": r["status"], "block": r["block"]}
              for r in main_all + rep_all if r.get("status") != "ok"]
    return {"experiment": EXP, "block": block, "reading": reading, "outcome": reading,
            "valid_lines": [r["label"] for r in valid_struct],
            "alive_lines": [r["label"] for r in alive],
            "break_even_met": bool(be_met),
            "calibration": cal, "controls": controls,
            "selftest_pass": bool(selftest_pass),
            "lines": struct_lines + plant_lines + zn_lines + aa_lines,
            "cells": cells, "infeasible_plants": infeasible,
            "failed_infrastructure": failed}


def _replication_line(label: str, theta: float, d: int, rungs: list[dict],
                      design: dict, rep: list[dict]) -> dict:
    entries = []
    for rung in rungs:
        cell = rung["cell"]
        rs = [r for r in rep if r["cell"] == cell["cell"]]
        if len(rs) < cell.get("n_curves", 1):
            return {"complete": False, "survives": None,
                    "reason": f"{cell['cell']} has {len(rs)} replication records for "
                              f"{cell.get('n_curves')} curves",
                    "delta_hat": None, "ci95": None, "class": None}
        st = cell_stats(rs, "struct")
        if st["M"] < TARGET_COINC:
            return {"complete": False, "survives": None,
                    "reason": f"{cell['cell']} replication M below target",
                    "delta_hat": None, "ci95": None, "class": None}
        entries.append({"bits": rung["bits"], "stats": st,
                        "Nbar": statistics.fmean(math.log2(r["N"]) for r in rs)})
    xs = [e["Nbar"] for e in entries]
    ys = [math.log2(e["stats"]["kappa"]) if e["stats"]["kappa"] > 0 else float("nan")
          for e in entries]
    delta, _, resid = _ols(xs, ys)
    rng = _rng("boot", label + "|rep")
    rep_kappa = [[] for _ in entries]
    for _ in range(BOOT_B):
        kk = []
        for e in entries:
            sv, mv = e["stats"]["S_by_curve"], e["stats"]["M_by_curve"]
            n = len(sv)
            S = M = 0.0
            for _ in range(n):
                i = rng.randrange(n)
                S += sv[i]
                M += mv[i]
            kk.append(S / M if M > 0 else float("nan"))
        for j, k in enumerate(kk):
            rep_kappa[j].append(k)
    boot = []
    for b in range(BOOT_B):
        ky = [math.log2(rep_kappa[j][b]) if rep_kappa[j][b] > 0 else float("nan")
              for j in range(len(entries))]
        if all(v == v for v in ky):
            boot.append(_ols(xs, ky)[0])
    boot.sort()
    lo, hi = _pct(boot, 0.025, 0.975)
    survives = bool(lo > 0 and hi >= DELTA_STAR)
    return {"complete": True, "delta_hat": delta, "ci95": [lo, hi], "residuals": resid,
            "class": classify(True, lo, hi), "survives": survives}


def cmd_build(a) -> None:
    os.makedirs(a.out, exist_ok=True)
    subprocess.run(["gcc", "-O2", "-std=c11", "-o", os.path.join(a.out, "paircount"),
                    os.path.join(HERE, "paircount.c")], check=True)
    print("built", os.path.join(a.out, "paircount"))


def _brute(E, pts: list) -> int:
    mult: dict = {}
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            P, Q = pts[i], pts[j]
            if P[0] == Q[0]:
                continue  # Q = -P (distinct points sharing x)
            s = E.add(P, Q)
            mult[s] = mult.get(s, 0) + 1
    return sum(m * (m - 1) // 2 for m in mult.values())


def _kernel_check(kernel: str, E, name: str, B: list, checks: list, **extra) -> None:
    assert len(B) == len(set(B)), name
    assert all(E.is_on_curve(P) for P in B), name
    assert set(B) == {(x, (-y) % E.p) for x, y in B}, f"{name} not symmetric"
    k = run_kernel(kernel, E, [B])[0][2]
    br = _brute(E, B)
    checks.append({"base": name, "kernel": k, "brute": br, **extra})
    if k != br:
        raise AssertionError((name, k, br, extra))


def cmd_selftest(a) -> None:
    kernel = os.path.join(getattr(a, "build", None) or a.out, "paircount")
    checks: list = []
    for bits in (10, 12, 14):
        for c in range(3):
            E, G, _ = get_curve(bits, "selftest", c)
            bases = [("null", null_base(E, 40, _rng("st", bits, c))),
                     ("window", window_base(E, 40, _rng("stw", bits, c))[0]),
                     ("gap2", gap_base(E, 40, 2, _rng("stg", bits, c))[0]),
                     ("gap3", gap_base(E, 40, 3, _rng("stg3", bits, c))[0]),
                     ("zn", zn_interval_base(E, G, 40))]
            for gi, gamma in enumerate(GAMMAS, 1):
                bases.append((f"plant{gamma}", gamma_plant_base(
                    E, G, 40, 2 + 2 * gi, _rng("stp", bits, c, gamma))))
            for name, B in bases:
                _kernel_check(kernel, E, name, B, checks, bits=bits, c=c)
    for bits in BITS:
        c = 20 + bits
        E, G, _ = get_curve(bits, "selftest", c)
        bases = [("null", null_base(E, 40, _rng("strung", bits, c))),
                 ("window", window_base(E, 40, _rng("strungw", bits, c))[0]),
                 ("gap2", gap_base(E, 40, 2, _rng("strungg", bits, c))[0]),
                 ("gap3", gap_base(E, 40, 3, _rng("strungg3", bits, c))[0]),
                 ("zn", zn_interval_base(E, G, 40))]
        for gi, gamma in enumerate(GAMMAS, 1):
            bases.append((f"plant{gamma}", gamma_plant_base(
                E, G, 40, 2 + 2 * gi, _rng("strungp", bits, c, gamma))))
        for name, B in bases:
            _kernel_check(kernel, E, name, B, checks, bits=bits, c=c)
    E, G, _ = get_curve(16, "selftest", 10)
    internal = []
    for L in (1, 2, 3, 5, 9, 14):
        pts = []
        Q = None
        for _ in range(L):
            Q = G if Q is None else E.add(Q, G)
            pts += [Q, E.neg(Q)]
        got = _brute(E, pts)
        internal.append({"L": L, "plant_internal": plant_internal(L), "brute": got,
                         "pass": got == plant_internal(L)})
        if got != plant_internal(L):
            raise AssertionError(("plant_internal", L, got, plant_internal(L)))
    order = []
    for i in range(8):
        seed = SEED_BLOCK["selftest"] + i
        E32, G32 = ec.generate_prime_order_curve(32, seed=seed)
        cert = certify_curve(E32, G32, 32, seed)
        order.append(cert)
        if not cert["pass"]:
            raise AssertionError(("order certification", cert))
    for i in range(4):
        seed = SEED_BLOCK["selftest"] + 100 + i
        E28, G28 = ec.generate_prime_order_curve(28, seed=seed)
        cert = certify_curve(E28, G28, 28, seed)
        order.append(cert)
        if not cert["pass"]:
            raise AssertionError(("order certification", cert))
    E32, G32 = ec.generate_prime_order_curve(32, seed=SEED_BLOCK["selftest"] + 100)
    key_checks = []
    near = [("null", null_base(E32, 64, _rng("st32n", 0))),
            ("window", window_base(E32, 64, _rng("st32w", 0))[0]),
            ("gap2", gap_base(E32, 64, 2, _rng("st32g", 0))[0]),
            ("gap3", gap_base(E32, 64, 3, _rng("st32g3", 0))[0]),
            ("zn", zn_interval_base(E32, G32, 64))]
    for gi, gamma in enumerate(GAMMAS, 1):
        near.append((f"plant{gamma}", gamma_plant_base(
            E32, G32, 64, 2 + 2 * gi, _rng("st32p", gamma))))
    for name, B in near:
        _kernel_check(kernel, E32, name, B, key_checks, bits=32, near_2_32=True)
    key_bound = (E32.p - 1) * E32.p + (E32.p - 1)
    kb = {"p": E32.p, "p_bits": E32.p.bit_length(), "bound": key_bound,
          "lt_2_64": key_bound < (1 << 64), "p_lt_2_32": E32.p < (1 << 32),
          "pass": bool(key_bound < (1 << 64) and E32.p < (1 << 32))}
    if not kb["pass"]:
        raise AssertionError(("key bound", kb))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "selftest.json"), "w") as f:
        json.dump({"pass": True, "experiment": EXP, "checks": checks,
                   "key_checks": key_checks, "plant_internal_checks": internal,
                   "order_certification": order, "key_bound": kb}, f, indent=1)
    print(f"selftest PASS ({len(checks)} kernel-vs-brute + {len(key_checks)} near-2^32 "
          f"key checks + {len(internal)} plant_internal + {len(order)} order "
          f"certifications (8 at 32 bits, 4 at 28 bits))")


def cmd_pilot(a) -> None:
    kernel = os.path.join(a.build, "paircount")
    os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, "pilot-jobs.jsonl")
    todo = [(cell, "pilot", c, None) for cell in cells() for c in range(PILOT_CURVES)]
    _run_jobs(kernel, todo, jp, nulls_only=True)
    recs = [r for r in _load(jp) if r["status"] == "ok"]
    design = build_design(recs)
    with open(os.path.join(a.out, "design.json"), "w") as f:
        json.dump(design, f, indent=1, sort_keys=True)
    print("design.json written:", len(design["cells"]), "cells,",
          len(design["plants"]), "plant entries")


def cmd_census(a) -> None:
    kernel = os.path.join(a.build, "paircount")
    os.makedirs(a.out, exist_ok=True)
    with open(a.design) as f:
        design = json.load(f)
    only = None
    if a.block == "rep":
        with open(a.flags) as f:
            only = set(json.load(f)["alive_cells"])
    todo = []
    for cell in design["cells"]:
        if cell.get("status") != "ok" or (only is not None and cell["cell"] not in only):
            continue
        for c in range(cell["n_curves"]):
            todo.append((cell, a.block, c, plant_cfgs_for(design, cell, a.block, c)))
    _run_jobs(kernel, todo, os.path.join(a.out, f"{a.block}-jobs.jsonl"), nulls_only=False)


def cmd_analyze(a) -> None:
    with open(a.design) as f:
        design = json.load(f)
    main = _load(a.main)
    rep = _load(a.rep) if a.rep and os.path.exists(a.rep) else []
    block = "main" if (not a.rep or a.rep == a.main) else "final"
    if a.rep and a.rep != a.main:
        block = "final"
    selftest_pass = False
    if getattr(a, "selftest", None) and os.path.exists(a.selftest):
        with open(a.selftest) as f:
            selftest_pass = bool(json.load(f).get("pass"))
    an = evaluate(design, main, rep, selftest_pass, block)
    out = a.out
    with open(out, "w") as f:
        json.dump(an, f, indent=1, sort_keys=True)
    alive_cells = sorted({cell_name(bits, line["theta"], line["d"])
                          for line in an["lines"]
                          if line["kind"] == "struct" and line["class"] == "ALIVE"
                          for bits in BITS})
    with open(os.path.join(os.path.dirname(out) or ".", "flags.json"), "w") as f:
        json.dump({"alive_lines": an["alive_lines"], "alive_cells": alive_cells,
                   "reading": an["reading"]}, f)
    print("reading", an["reading"], "| valid lines", len(an["valid_lines"]),
          "| alive", len(an["alive_lines"]), "| calibration", an["calibration"])


def cmd_reanalysis(a) -> None:
    import json as _json
    with open(a.ca5e01_analysis) as f:
        analysis = _json.load(f)
    main = _load(a.ca5e01_main)
    ok = [r for r in main if r.get("status") == "ok"]
    Nbar: dict = {}
    for r in ok:
        Nbar.setdefault(r["cell"], {}).setdefault(r["c"], r["N"])
    lines = []
    for cell in analysis.get("cells", []):
        if "kappa" not in cell or cell["kappa"] <= 0:
            continue
        ns = Nbar.get(cell["cell"], {})
        lines.append({"theta": cell["theta"], "d": cell["d"], "bits": cell["bits"],
                      "kappa": cell["kappa"], "N": cell["N"] if "N" in cell else None,
                      "Nbar": statistics.fmean(math.log2(n) for n in ns.values())
                      if ns else float("nan"),
                      "cell_class": cell.get("cls"), "cell": cell["cell"]})
    slopes = {}
    for theta in sorted({x["theta"] for x in lines}):
        for d in sorted({x["d"] for x in lines}):
            pts = [x for x in lines if x["theta"] == theta and x["d"] == d
                   and x["Nbar"] == x["Nbar"]]
            if len(pts) < 3:
                continue
            xs = [x["Nbar"] for x in pts]
            ys = [math.log2(x["kappa"]) for x in pts]
            delta, intercept, resid = _ols(xs, ys)
            slopes[f"theta{theta:.2f}-d{d}"] = {
                "theta": theta, "d": d, "n_points": len(pts), "slope": delta,
                "intercept": intercept, "residuals": resid,
                "bits": [x["bits"] for x in pts],
                "kappa": [x["kappa"] for x in pts], "Lbar": xs}
    out = {"experiment": EXP, "kind": "reanalysis-ca5e01",
           "source_runs": {"analysis": os.path.basename(os.path.dirname(a.ca5e01_analysis)),
                           "main_jobs": os.path.basename(os.path.dirname(a.ca5e01_main))},
           "note": "Descriptive only (coordinator resolution R5): stage-1 slope of "
                   "log2 kappa on rung mean log2 N over EXP-PFDR-ca5e01 bits 16..22. "
                   "It reads data whose cell outcome is already known and never enters "
                   "the EXP-PFDR-2d36f9 reading.",
           "slopes": slopes, "points": lines}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("reanalysis.json written:", len(slopes), "lines")


HYPOTHESIS_ID = "H-PFDR-ed7ccf"
RUNS_DIR = os.path.normpath(os.path.join(HERE, "..", "runs"))


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit() -> tuple[str | None, bool | None]:
    try:
        c = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True,
                           text=True, check=True)
        d = subprocess.run(["git", "status", "--porcelain", "--", HERE], cwd=HERE,
                           capture_output=True, text=True, check=True)
        return c.stdout.strip(), bool(d.stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return None, None


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
    up = {}
    for k, v in trial.get("inputs_from", {}).items():
        p = v if os.path.isabs(v) else os.path.normpath(os.path.join(RUNS_DIR, v))
        up[k] = p
    build = tempfile.mkdtemp(prefix="pfdr2d36f9-build-")
    status, reason, summary = "completed_valid", None, {}
    try:
        cmd_build(argparse.Namespace(out=build))
        stage = trial["stage"]
        if stage == "selftest":
            cmd_selftest(argparse.Namespace(build=build, out=rd))
            summary = {"selftest_pass": True}
        elif stage == "pilot":
            cmd_pilot(argparse.Namespace(build=build, out=rd))
            with open(os.path.join(rd, "design.json")) as f:
                d = json.load(f)
            summary = {"cells": len(d["cells"]),
                       "cells_ok": sum(c["status"] == "ok" for c in d["cells"]),
                       "curves_planned": sum(c.get("n_curves", 0) for c in d["cells"]),
                       "plants": len(d.get("plants", []))}
        elif stage == "census":
            block = trial["block"]
            cmd_census(argparse.Namespace(build=build, design=up["design"], block=block,
                                          flags=up.get("flags"), out=rd))
            recs = _load(os.path.join(rd, f"{block}-jobs.jsonl"))
            bad = [r for r in recs if r["status"] != "ok"]
            summary = {"jobs": len(recs), "failed_infrastructure": len(bad)}
            if bad:
                reason = f"{len(bad)} jobs failed_infrastructure; their cells are invalid, never null"
        elif stage == "analyze" and trial.get("mode") == "reanalysis":
            cmd_reanalysis(argparse.Namespace(ca5e01_analysis=up["ca5e01_analysis"],
                                              ca5e01_main=up["ca5e01_main"],
                                              out=os.path.join(rd, trial["output"])))
            with open(os.path.join(rd, trial["output"])) as f:
                ra = json.load(f)
            summary = {"descriptive_only": True, "lines": len(ra["slopes"])}
        elif stage == "analyze":
            out = os.path.join(rd, trial["output"])
            cmd_analyze(argparse.Namespace(design=up["design"], main=up["main"],
                                           rep=up.get("rep"), selftest=up.get("selftest"),
                                           out=out))
            with open(out) as f:
                an = json.load(f)
            summary = {"reading": an["reading"], "alive_lines": an["alive_lines"],
                       "calibration": an["calibration"],
                       "valid_lines": len(an["valid_lines"]),
                       "controls": {k: v["pass"] for k, v in an["controls"].items()}}
        else:
            raise ValueError(f"unknown stage {stage}")
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id,
                       "summary": summary, "invalid_reason": reason}, f, indent=1, sort_keys=True)
        code = 0
    except Exception as e:  # recorded as failed_infrastructure, never a metric
        status, reason, code = "failed", f"failed_infrastructure: {type(e).__name__}: {e}", 1
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id,
                       "summary": {}, "invalid_reason": reason}, f, indent=1)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    commit, dirty = _git_commit()
    ru_c, ru_s = resource.getrusage(resource.RUSAGE_CHILDREN), resource.getrusage(resource.RUSAGE_SELF)
    code_sha = {os.path.relpath(os.path.join(dp, fn), HERE): _sha256(os.path.join(dp, fn))
                for dp, _, fns in os.walk(HERE) if "__pycache__" not in dp
                for fn in sorted(fns) if fn.endswith((".py", ".c"))}
    manifest = {"run": {
        "id": a.run_id, "experiment_id": EXP, "hypothesis_id": HYPOTHESIS_ID,
        "task_id": plan.get("task_id"), "trial_id": a.trial_id, "role": "executor",
        "recorded_at": started[:10], "status": status,
        "validity": {"status": status, "reason": reason or "run.py recorded no invalidation; "
                     "check.py and independent review decide validity", "failure_class": None},
        "code": {"commit": commit, "dirty": dirty, "branch": None,
                 "command": " ".join([sys.executable, *sys.argv]), "code_sha256": code_sha,
                 "trial_plan_sha256": _sha256(a.plan), "working_directory": os.getcwd()},
        "environment": {"host": platform.node(), "operating_system": platform.platform(),
                        "python_version": sys.version.split()[0], "processor_count": os.cpu_count(),
                        "source": "manifest.yaml /run/environment"},
        "inputs": {"curve_id": None, "seed": None,
                   "parameters": {"trial_id": a.trial_id, "stage": trial["stage"],
                                  "inputs_from": trial.get("inputs_from", {}), "plan": a.plan}},
        "timing": {"started_at": started,
                   "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "wall_seconds": round(time.time() - t0, 3)},
        "resources": {"peak_rss_bytes": int(max(ru_c.ru_maxrss, ru_s.ru_maxrss) * 1024),
                      "cpu_seconds": round(ru_c.ru_utime + ru_c.ru_stime + ru_s.ru_utime
                                           + ru_s.ru_stime, 3)},
        "result": {"metrics": {"raw_result": "raw-result.json"} if code == 0 else {},
                   "valid": status == "completed_valid", "invalid_reason": reason,
                   "raw_result": "raw-result.json",
                   "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                                   "note": "exact coincidence counts on public toy curves; no "
                                           "discrete logarithm, relation or speedup is claimed"}},
        "artifacts": [n for n in trial["artifacts"] if n != "manifest.yaml"],
    }}
    with open(os.path.join(rd, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    return code


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("trial"); s.add_argument("--run-dir", required=True); s.add_argument("--run-id", required=True)
    s.add_argument("--trial-id", required=True); s.add_argument("--plan", required=True)
    s.set_defaults(f=cmd_trial)
    s = sub.add_parser("build"); s.add_argument("--out", required=True); s.set_defaults(f=cmd_build)
    s = sub.add_parser("selftest"); s.add_argument("--out", required=True); s.add_argument("--build")
    s.set_defaults(f=cmd_selftest)
    s = sub.add_parser("pilot"); s.add_argument("--build", required=True); s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_pilot)
    s = sub.add_parser("census"); s.add_argument("--build", required=True); s.add_argument("--design", required=True)
    s.add_argument("--block", choices=("main", "rep"), required=True); s.add_argument("--flags")
    s.add_argument("--out", required=True); s.set_defaults(f=cmd_census)
    s = sub.add_parser("analyze"); s.add_argument("--design", required=True); s.add_argument("--main", required=True)
    s.add_argument("--rep"); s.add_argument("--selftest"); s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_analyze)
    s = sub.add_parser("reanalysis"); s.add_argument("--ca5e01-analysis", required=True)
    s.add_argument("--ca5e01-main", required=True); s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_reanalysis)
    a = ap.parse_args()
    sys.exit(a.f(a) or 0)


if __name__ == "__main__":
    main()
