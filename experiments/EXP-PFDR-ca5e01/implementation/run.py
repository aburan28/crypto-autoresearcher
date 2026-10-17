"""EXP-PFDR-ca5e01: pair-sum coincidence census of window and rank-d GAP bases.

Frozen-contract driver (specification.yaml is the authority; this file is bound
by sha256 in trial-plan.json). Standard library only, plus the vendored copy of
src/crypto_autoresearcher/index_calculus/curve.py and the C kernel paircount.c.

Subcommands (each writes only under --out):
  build      compile paircount.c -> <out>/paircount
  selftest   kernel == brute-force Python count on small curves; base builders
  pilot      sizing pass: null bases only on the pilot curve block -> design.json
  census     main or replication block for the cells in design.json -> jobs.jsonl
  analyze    frozen statistics and outcome rules -> analysis.json

Counting convention (CC): for a symmetric base F (F = -F) of exactly b points,
C(F) = sum over s != O of binom(m_s, 2), with m_s the number of unordered pairs
{P, Q}, P != Q, Q != -P, with P + Q = s. The null is 20 uniformly random
symmetric bases of the same b on the same curve.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import curve as ec  # noqa: E402  (vendored, sha256-pinned)

EXP = "EXP-PFDR-ca5e01"
BITS = (16, 18, 20, 22)
THETAS = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65)
DIMS = (1, 2, 3)
B_MIN, B_MAX = 16, 8192
NULL_REPS = 20
TARGET_COINC = 2500
N_MIN, N_MAX = 10, 4000
PILOT_CURVES = 8
PLANT_FRAC = 0.30
SEED_BLOCK = {"pilot": 7_000_000, "main": 7_100_000, "rep": 7_200_000}
KERNEL_TIMEOUT_S = 3600
WORKERS = 4

# frozen decision thresholds (specification.yaml analysis / outcomes)
FLAG_DEV, FLAG_Z = 0.10, 4.0
NULL_DEV = 0.05
REP_Z, REP_DEV = 3.0, 0.05
PLANT_KAPPA, PLANT_Z = 1.15, 4.0
CAL_SD_LO, CAL_SD_HI, CAL_MEAN_ABS = 0.85, 1.15, 0.25
BOOT_B = 2000


def _rng(*labels: object) -> random.Random:
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


def cells() -> list[dict]:
    out = []
    for bits in BITS:
        for th in THETAS:
            b = 2 * round((2.0 ** (bits * th)) / 2)
            if not (B_MIN <= b <= B_MAX):
                continue
            for d in DIMS:
                out.append({"cell": f"b{bits}-t{th:.2f}-d{d}", "bits": bits,
                            "theta": th, "d": d, "b": b})
    return out


def get_curve(bits: int, block: str, c: int):
    E, G = ec.generate_prime_order_curve(bits, seed=SEED_BLOCK[block] + c)
    return E, G


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


def plant_size(target: float, b: int) -> int:
    """Smallest L with plant_internal(L) >= target and 2L <= b/2 (else the cap)."""
    lo, hi = 1, max(1, b // 4)
    while lo < hi:
        mid = (lo + hi) // 2
        if plant_internal(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def planted_base(E, G, b: int, L: int, rng: random.Random) -> list:
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


def job(kernel: str, cell: dict, block: str, c: int, nulls_only: bool = False) -> dict:
    t0 = time.time()
    E, G = get_curve(cell["bits"], block, c)
    b = cell["b"]
    rec = {"cell": cell["cell"], "block": block, "c": c, "p": E.p, "a": E.a,
           "b_coef": E.b, "N": E.order, "b": b, "status": "ok"}
    try:
        nb = [null_base(E, b, _rng("null", block, cell["cell"], c, r)) for r in range(NULL_REPS)]
        res = run_kernel(kernel, E, nb)
        rec["null"] = [r[2] for r in res]
        rec["pairs"] = res[0][1]
        if nulls_only:
            rec["seconds"] = round(time.time() - t0, 3)
            return rec
        if cell["d"] == 1:
            sb, meta = window_base(E, b, _rng("struct", block, cell["cell"], c))
        else:
            sb, meta = gap_base(E, b, cell["d"], _rng("struct", block, cell["cell"], c))
        m_c = statistics.fmean(rec["null"])
        L = plant_size(PLANT_FRAC * m_c, b)
        plant_ok = plant_internal(L) >= PLANT_FRAC * m_c
        pb = planted_base(E, G, b, L, _rng("plant", block, cell["cell"], c))
        res2 = run_kernel(kernel, E, [sb, pb])
        rec.update({"struct": res2[0][2], "struct_meta": meta, "struct_pairs": res2[0][1],
                    "plant": res2[1][2], "plant_L": L, "plant_internal": plant_internal(L),
                    "plant_feasible": plant_ok})
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
        futs = [pool.submit(job, kernel, cell, block, c, nulls_only) for cell, block, c in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            f.write(json.dumps(fut.result(), sort_keys=True) + "\n")
            f.flush()
            if i % 200 == 0 or i == len(futs):
                print(f"  {i}/{len(futs)}", flush=True)


def _load(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(ln) for ln in f]


# ---------------------------------------------------------------- subcommands

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


def cmd_selftest(a) -> None:
    kernel = os.path.join(getattr(a, "build", None) or a.out, "paircount")
    checks = []
    for bits in (10, 12, 14):
        for c in range(3):
            E, G = ec.generate_prime_order_curve(bits, seed=9_900_000 + c)
            for name, B in (("null", null_base(E, 40, _rng("st", bits, c))),
                            ("window", window_base(E, 40, _rng("stw", bits, c))[0]),
                            ("gap2", gap_base(E, 40, 2, _rng("stg", bits, c))[0]),
                            ("gap3", gap_base(E, 40, 3, _rng("stg3", bits, c))[0]),
                            ("plant", planted_base(E, G, 40, 6, _rng("stp", bits, c)))):
                assert len(B) == 40 and len(set(B)) == 40, name
                assert all(E.is_on_curve(P) for P in B), name
                assert set(B) == {(x, (-y) % E.p) for x, y in B}, f"{name} not symmetric"
                k = run_kernel(kernel, E, [B])[0][2]
                br = _brute(E, B)
                checks.append({"bits": bits, "c": c, "base": name, "kernel": k, "brute": br})
                assert k == br, (bits, c, name, k, br)
    # plant_internal against a brute count on integers via the group
    E, G = ec.generate_prime_order_curve(16, seed=9_900_100)
    for L in (1, 2, 3, 5, 9, 14):
        pts = []
        Q = None
        for _ in range(L):
            Q = G if Q is None else E.add(Q, G)
            pts += [Q, E.neg(Q)]
        assert _brute(E, pts) == plant_internal(L), L
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "selftest.json"), "w") as f:
        json.dump({"pass": True, "checks": checks}, f, indent=1)
    print(f"selftest PASS ({len(checks)} kernel-vs-brute checks + plant_internal)")


def cmd_pilot(a) -> None:
    kernel = os.path.join(a.build, "paircount")
    os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, "pilot-jobs.jsonl")
    todo = [(cell, "pilot", c) for cell in cells() for c in range(PILOT_CURVES)]
    _run_jobs(kernel, todo, jp, nulls_only=True)
    recs = [r for r in _load(jp) if r["status"] == "ok"]
    design = {"experiment": EXP, "rule": f"n = clamp(ceil(1.1*{TARGET_COINC}/mean_null), "
              f"{N_MIN}, {N_MAX}); mean_null over {PILOT_CURVES} pilot curves x {NULL_REPS} nulls",
              "cells": []}
    for cell in cells():
        rs = [r for r in recs if r["cell"] == cell["cell"]]
        if len(rs) < PILOT_CURVES:
            design["cells"].append({**cell, "status": "pilot_incomplete"})
            continue
        mn = statistics.fmean(x for r in rs for x in r["null"])
        n = N_MAX if mn <= 0 else min(N_MAX, max(N_MIN, math.ceil(1.1 * TARGET_COINC / mn)))
        design["cells"].append({**cell, "status": "ok", "pilot_mean_null": mn,
                                "n_curves": n, "expected_null_total": n * mn,
                                "powered_by_design": n * mn >= TARGET_COINC})
    with open(os.path.join(a.out, "design.json"), "w") as f:
        json.dump(design, f, indent=1, sort_keys=True)
    print("design.json written:", len(design["cells"]), "cells")


def cmd_census(a) -> None:
    kernel = os.path.join(a.build, "paircount")
    os.makedirs(a.out, exist_ok=True)
    with open(a.design) as f:
        design = json.load(f)
    only = None
    if a.block == "rep":
        with open(a.flags) as f:
            only = set(json.load(f)["flagged_cells"])
    todo = []
    for cell in design["cells"]:
        if cell["status"] != "ok" or (only is not None and cell["cell"] not in only):
            continue
        todo += [(cell, a.block, c) for c in range(cell["n_curves"])]
    _run_jobs(kernel, todo, os.path.join(a.out, f"{a.block}-jobs.jsonl"), nulls_only=False)


def _cell_stats(rs: list[dict], seed: str) -> dict:
    rs = sorted(rs, key=lambda r: r["c"])  # completion order of a 4-worker run must not move the bootstrap
    S = sum(r["struct"] for r in rs)
    Pl = sum(r["plant"] for r in rs)
    means = [statistics.fmean(r["null"]) for r in rs]
    var = [statistics.variance(r["null"]) for r in rs]
    M, V = sum(means), sum(var)
    sd = math.sqrt(V * (1 + 1 / NULL_REPS)) if V > 0 else float("nan")
    kappa = S / M if M > 0 else float("nan")
    rng = _rng("boot", seed)
    n = len(rs)
    boots = []
    for _ in range(BOOT_B):
        idx = [rng.randrange(n) for _ in range(n)]
        m = sum(means[i] for i in idx)
        boots.append(sum(rs[i]["struct"] for i in idx) / m if m > 0 else float("nan"))
    boots.sort()
    # null-vs-null calibration: replicate 0 as pseudo-structured vs the other 19
    pS = sum(r["null"][0] for r in rs)
    pM = sum(statistics.fmean(r["null"][1:]) for r in rs)
    pV = sum(statistics.variance(r["null"][1:]) for r in rs)
    return {"curves": n, "S": S, "M": M, "V": V, "kappa": kappa,
            "ci95": [boots[int(0.025 * BOOT_B)], boots[int(0.975 * BOOT_B) - 1]],
            "z": (S - M) / sd if sd == sd and sd > 0 else float("nan"),
            "plant_kappa": Pl / M if M > 0 else float("nan"),
            "plant_z": (Pl - M) / sd if sd == sd and sd > 0 else float("nan"),
            "plant_feasible_all": all(r["plant_feasible"] for r in rs),
            "z_cal": (pS - pM) / math.sqrt(pV * (1 + 1 / (NULL_REPS - 1))) if pV > 0 else float("nan"),
            "b_matched": all(r["struct_pairs"] > 0 for r in rs)}


def cmd_analyze(a) -> None:
    with open(a.design) as f:
        design = json.load(f)
    main = [r for r in _load(a.main) if r["status"] == "ok"]
    rep = [r for r in _load(a.rep) if r["status"] == "ok"] if a.rep and os.path.exists(a.rep) else []
    cellrows, zcal = [], []
    for cell in design["cells"]:
        row = {k: cell[k] for k in ("cell", "bits", "theta", "d", "b")}
        rs = [r for r in main if r["cell"] == cell["cell"]]
        if cell["status"] != "ok" or len(rs) < cell.get("n_curves", 1):
            row.update(cls="invalid", reason="incomplete (failed_infrastructure or pilot)",
                       curves=len(rs))
            cellrows.append(row)
            continue
        st = _cell_stats(rs, cell["cell"] + "|main")
        row.update(st)
        powered = st["M"] >= TARGET_COINC
        planted = st["plant_feasible_all"] and st["plant_kappa"] >= PLANT_KAPPA and st["plant_z"] > PLANT_Z
        row["powered"], row["planted_recovered"] = powered, planted
        if powered:
            zcal.append(st["z_cal"])
        if not powered:
            row["cls"] = "inconclusive_underpowered"
        elif not planted:
            row["cls"] = "inconclusive_plant_not_recovered"
        elif abs(st["kappa"] - 1) >= FLAG_DEV and abs(st["z"]) > FLAG_Z:
            row["cls"] = "flagged"
        elif abs(st["kappa"] - 1) < NULL_DEV and 1 - 2 * NULL_DEV <= st["ci95"][0] and st["ci95"][1] <= 1 + 2 * NULL_DEV:
            row["cls"] = "null"
        else:
            row["cls"] = "intermediate"
        cellrows.append(row)
    cal = {"n": len(zcal), "mean": statistics.fmean(zcal) if zcal else None,
           "sd": statistics.pstdev(zcal) if len(zcal) > 1 else None}
    cal["pass"] = bool(zcal) and cal["sd"] is not None and CAL_SD_LO <= cal["sd"] <= CAL_SD_HI \
        and abs(cal["mean"]) <= CAL_MEAN_ABS
    flagged = [r["cell"] for r in cellrows if r["cls"] == "flagged"]
    for r in cellrows:
        if r["cls"] != "flagged":
            continue
        rr = [x for x in rep if x["cell"] == r["cell"]]
        if not rr:
            r["replication"] = "not_run"
            continue
        planned = next(c["n_curves"] for c in design["cells"] if c["cell"] == r["cell"])
        if len({x["c"] for x in rr}) != planned:
            r["replication"] = "incomplete"  # failed_infrastructure curves: never evidence, never a survival
            continue
        st = _cell_stats(rr, r["cell"] + "|rep")
        same = (st["kappa"] - 1) * (r["kappa"] - 1) > 0
        r["replication"] = {**st, "survives": bool(same and abs(st["z"]) > REP_Z
                                                   and abs(st["kappa"] - 1) >= REP_DEV)}
    valid = [r for r in cellrows if r["cls"] in ("null", "flagged", "intermediate")]
    frac_valid = len(valid) / len(cellrows) if cellrows else 0.0
    if not cal["pass"] or frac_valid < 0.5:
        outcome = "O-INVALID"
    elif any(isinstance(r.get("replication"), dict) and r["replication"]["survives"] for r in cellrows):
        outcome = "O-STRUCT"
    elif flagged and any(r.get("replication") in ("not_run", "incomplete")
                         for r in cellrows if r["cls"] == "flagged"):
        outcome = "O-PENDING-REPLICATION"
    elif valid and all(r["cls"] == "null" for r in valid) and frac_valid >= 0.8:
        outcome = "O-NULL"
    else:
        outcome = "O-MIXED"
    # secondary: per (bits, d) least-squares slope of log kappa on theta over valid cells
    slopes = {}
    for bits in BITS:
        for d in DIMS:
            pts = [(r["theta"], math.log(r["kappa"])) for r in valid
                   if r["bits"] == bits and r["d"] == d and r["kappa"] > 0]
            if len(pts) >= 3:
                mx = statistics.fmean(t for t, _ in pts)
                my = statistics.fmean(v for _, v in pts)
                sxx = sum((t - mx) ** 2 for t, _ in pts)
                slopes[f"b{bits}-d{d}"] = sum((t - mx) * (v - my) for t, v in pts) / sxx
    out = {"experiment": EXP, "outcome": outcome, "calibration": cal,
           "fraction_valid": frac_valid, "flagged_cells": flagged,
           "secondary_slope_logkappa_per_theta": slopes, "cells": cellrows}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    with open(os.path.join(os.path.dirname(a.out) or ".", "flags.json"), "w") as f:
        json.dump({"flagged_cells": flagged}, f)
    print("outcome", outcome, "| cells", len(cellrows), "| valid", len(valid),
          "| flagged", len(flagged), "| calibration", cal)


# ---------------------------------------------------------------- supervisor trial entry

HYPOTHESIS_ID = "H-PFDR-011a4b"
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
    up = {k: os.path.join(RUNS_DIR, v) for k, v in trial.get("inputs_from", {}).items()}
    build = tempfile.mkdtemp(prefix="ca5e01-build-")
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
            summary = {"cells": len(d["cells"]), "cells_ok": sum(c["status"] == "ok" for c in d["cells"]),
                       "curves_planned": sum(c.get("n_curves", 0) for c in d["cells"])}
        elif stage == "census":
            block = trial["block"]
            flags = up.get("flags")
            cmd_census(argparse.Namespace(build=build, design=up["design"], block=block, flags=flags, out=rd))
            recs = _load(os.path.join(rd, f"{block}-jobs.jsonl"))
            bad = [r for r in recs if r["status"] != "ok"]
            summary = {"jobs": len(recs), "failed_infrastructure": len(bad)}
            if bad:
                reason = f"{len(bad)} jobs failed_infrastructure; their cells are invalid, never null"
        elif stage == "analyze":
            out = os.path.join(rd, trial["output"])
            cmd_analyze(argparse.Namespace(design=up["design"], main=up["main"], rep=up.get("rep"), out=out))
            with open(out) as f:
                an = json.load(f)
            summary = {"outcome": an["outcome"], "flagged_cells": an["flagged_cells"],
                       "calibration": an["calibration"], "fraction_valid": an["fraction_valid"]}
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
        "validity": {"status": status, "reason": reason or "run.py recorded no invalidation; check.py "
                     "and independent review decide validity", "failure_class": None},
        "code": {"commit": commit, "dirty": dirty, "branch": None,
                 "command": " ".join([sys.executable, *sys.argv]), "code_sha256": code_sha,
                 "trial_plan_sha256": _sha256(a.plan), "working_directory": os.getcwd()},
        "environment": {"host": platform.node(), "operating_system": platform.platform(),
                        "python_version": sys.version.split()[0], "processor_count": os.cpu_count(),
                        "source": "manifest.yaml /run/environment"},
        "inputs": {"curve_id": None, "seed": None,
                   "parameters": {"trial_id": a.trial_id, "stage": trial["stage"],
                                  "inputs_from": trial.get("inputs_from", {}), "plan": a.plan}},
        "timing": {"started_at": started, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "wall_seconds": round(time.time() - t0, 3)},
        "resources": {"peak_rss_bytes": int(max(ru_c.ru_maxrss, ru_s.ru_maxrss) * 1024),
                      "cpu_seconds": round(ru_c.ru_utime + ru_c.ru_stime + ru_s.ru_utime + ru_s.ru_stime, 3)},
        "result": {"metrics": {"raw_result": "raw-result.json"} if code == 0 else {},
                   "valid": status == "completed_valid", "invalid_reason": reason,
                   "raw_result": "raw-result.json",
                   "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                                   "note": "exact coincidence counts on public toy curves; no discrete "
                                           "logarithm, relation or speedup is claimed"}},
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
    s = sub.add_parser("selftest"); s.add_argument("--out", required=True); s.set_defaults(f=cmd_selftest)
    s = sub.add_parser("pilot"); s.add_argument("--build", required=True); s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_pilot)
    s = sub.add_parser("census"); s.add_argument("--build", required=True); s.add_argument("--design", required=True)
    s.add_argument("--block", choices=("main", "rep"), required=True); s.add_argument("--flags")
    s.add_argument("--out", required=True); s.set_defaults(f=cmd_census)
    s = sub.add_parser("analyze"); s.add_argument("--design", required=True); s.add_argument("--main", required=True)
    s.add_argument("--rep"); s.add_argument("--out", required=True); s.set_defaults(f=cmd_analyze)
    a = ap.parse_args()
    sys.exit(a.f(a) or 0)


if __name__ == "__main__":
    main()
