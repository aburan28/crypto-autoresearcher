#!/usr/bin/env python3
"""
EXP-SSI-697354 -- crossover locus p*(w) from committed numbers only.

Executor implementation of the FROZEN contract
experiments/EXP-SSI-697354/specification.yaml (status: approved,
approved_by: coordinator, hypothesis H-SSI-7fe2bf, question RQ-SSI-001).

WHAT THIS IS: deterministic closed-form arithmetic on already-committed
numbers (the 8-row table T1, the 5-row paper anchor T2, and the declared
scalars T3).  Nothing is measured here; nothing is executed at any scale;
no isogeny, curve, field element, walk or table is constructed.  Every
number this program emits is MODELED, not measured, except the re-read
committed inputs, which are transcriptions of prior measurements.

Primary path: Python 3 standard library ONLY
(math, json, os, sys, time, hashlib, statistics, platform, importlib,
 argparse, resource, re, datetime -- the last four are stdlib as well).
numpy is used for NOTHING on the primary path; it is probed only for the
OPTIONAL cross-check XCHK-2, whose absence changes no reported number.

Determinism: no randomness anywhere.  Seed 0 is recorded for form only.
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import resource
import statistics
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EXPERIMENT_ID = "EXP-SSI-697354"
RUN_ID = "RUN-SSI-697354-a"
SEED = 0  # form only; no randomness is used anywhere

# ---------------------------------------------------------------------------
# FROZEN INPUT LITERALS (specification.yaml `inputs`).  These are the values
# the run must re-derive from the committed files and compare against.
# ---------------------------------------------------------------------------

T1_PATH = ("coordination/goals/GOAL-SSI-001/batches/BATCH-046/tasks/"
           "TASK-20260804-55952a/implementation/cost_measurements.json")
T2_PATH = "inputs/P13-WESOLOWSKI-2026/paper_fulltext.md"
T2_LINES = (234, 238)
COST_MODEL_PATH = ("coordination/tasks/TASK-20260724-P13-VAL/repro/experiments/"
                   "EXP-P13VOW-001/cost_model.py")
RED_TEAM_PATH = ("coordination/goals/GOAL-SSI-001/batches/BATCH-046/tasks/"
                 "TASK-20260804-55952a/red_team_concrete_cost.yaml")
SPEC_PATH = "experiments/EXP-SSI-697354/specification.yaml"

T1_X = [9, 14, 17, 20, 24, 28, 32, 40]
T1_Y = [143.72875226039784, 192.67237687366168, 244.77013354917037,
        293.178645371192, 343.926267281106, 439.4038324400175,
        515.2952824694235, 651.0768243785084]

T2_P = [256, 384, 512, 576, 768]
T2_LPAPER = [106.5, 157.5, 204.2, 230.9, 302.4]
T2_LMEM = [92.5, 138.6, 181.3, 206.0, 272.2]
T2_LPREV = [128.0, 192.0, 256.0, 288.0, 384.0]
T2_LABELS = ["SQIsign NIST-I", "SQIsign NIST-III", "SQIsign NIST-V", None, None]

# T3 declared scalars
S_STRUCT = [0.0, 3.0]
A_AES = [0.0, -1.736966, 1.584963, 3.906891]
A_LABELS = {0.0: "F_p2_operations_no_conversion",
            -1.736966: "pure_RAM_alpha_0.3",
            1.584963: "cpu_aes_ni_alpha_3",
            3.906891: "asic_alpha_15"}
C_OVERHEAD = [0.0, 0.5, 1.0, 1.8, 2.0]
LOG2_K_DG = 0.0
LOG2_K_DG_SENS = [-4.0, -2.0, 0.0, 2.0, 4.0]
GLOBAL_STORAGE_LOG2_BYTES = 73.08
BYTES_PER_ENTRY = [64, 256]

# w grid: 14 declared values (H-SSI-7fe2bf test_boundary.parameters.log2_w_grid)
W_GRID = [20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 60.0, 70.0, 80.0,
          92.5, 138.6, 181.3, 206.0, 272.2]

P_LO, P_HI = 256.0, 768.0
P_SCAN_STEP = 1.0

MC_LIST = ["MC_P13", "MC_VOW"]
LAWS_MAIN = ["L1", "L2", "L3", "L4"]
NULLS = ["N0", "N1"]

# frozen reference values (specification.yaml preregistered_prediction)
FROZEN_REF = {
    "a1": 15.576908, "a2": 16.2, "a3": 16.925485, "b3": -36.279641,
    "a4": 16.27692061,
    "E_at_256": {"L1": 11.961328, "L2": 12.017922, "L3": 12.069019,
                 "L4": 12.024751, "L5": 12.379},
    "T_A_256_S0_A0": {"L1": 118.461328, "L2": 118.517922, "L3": 118.569019,
                      "L4": 118.524751},
    "L_paper_minus_P_over_3": [21.166667, 29.5, 33.533333, 38.9, 46.4],
    "L_mem_minus_P_over_3": [7.166667, 10.6, 10.633333, 14.0, 16.2],
    "gap_below_target_S0_A0_c0": {"NIST-I": 9.538672, "NIST-III": 21.95,
                                  "NIST-V": 38.84},
    "memory_bytes_log2_at_64B": {"NIST-I": 98.5, "NIST-III": 144.6,
                                 "NIST-V": 187.3},
}

FORBIDDEN_MODULES = ["sage", "sagemath", "g6k", "fpylll", "scipy", "mpmath"]
PROBED_MODULES = ["numpy"] + FORBIDDEN_MODULES


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def rp(rel):
    return os.path.join(REPO_ROOT, rel)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


LOG = []


def say(msg):
    print(msg, flush=True)
    LOG.append(msg)


class GateFailure(Exception):
    pass


class InputDrift(Exception):
    pass


# ---------------------------------------------------------------------------
# STEP 0 -- environment / dependency assertion
# ---------------------------------------------------------------------------

def build_environment():
    modules = {}
    for m in PROBED_MODULES:
        try:
            spec = importlib.util.find_spec(m)
        except (ImportError, ValueError):
            spec = None
        modules[m] = {"present": spec is not None,
                      "origin": getattr(spec, "origin", None) if spec else None,
                      "version": None}
    # version only for permitted-optional numpy; never imported on primary path
    forbidden_imported = sorted(set(FORBIDDEN_MODULES) & set(sys.modules))
    env = {
        "interpreter": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "version_string": sys.version,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "module_presence": modules,
        "forbidden_modules_checked": FORBIDDEN_MODULES,
        "forbidden_modules_imported": forbidden_imported,
        "no_forbidden_import_assertion": (
            "No forbidden module (sage, sagemath, g6k, fpylll, scipy, mpmath) was "
            "imported by this process at the time of writing this record; "
            "sys.modules intersection with the forbidden list is empty."
            if not forbidden_imported else
            "VIOLATION: a forbidden module is present in sys.modules."),
        "stdlib_modules_imported_by_primary_path": sorted([
            "argparse", "datetime", "hashlib", "importlib", "json", "math",
            "os", "platform", "re", "resource", "statistics", "sys", "time"]),
        "numpy_used_for_any_reported_number": False,
        "network_access_performed": False,
        "seed": SEED,
        "randomness_sources": [],
    }
    return env


# ---------------------------------------------------------------------------
# STEP 1 -- re-read and verify the committed inputs (integrity rules)
# ---------------------------------------------------------------------------

def verify_T1():
    path = rp(T1_PATH)
    with open(path) as fh:
        doc = json.load(fh)
    rows = doc["scaling_summary"]
    x = [r["log2_p"] for r in rows]
    y = [r["avg_mults_per_entry"] for r in rows]
    ok = (len(rows) == 8 and x == T1_X and y == T1_Y)
    detail = {
        "path": T1_PATH, "pointer": "$.scaling_summary",
        "rows_found": len(rows),
        "x_reextracted": x, "y_reextracted": y,
        "x_frozen": T1_X, "y_frozen": T1_Y,
        "float_equality_exact": ok,
        "sha256": sha256_file(path),
        "primes_used_per_row": [r["primes_used"] for r in rows],
        "known_limitation_carried": (
            "Every T1 row uses primes_used in {[2,3], [2,3,5]}; RT-20260805-92751c "
            "OBJ-1 states the operating ell at NIST-I is far larger and that "
            "per-entry cost rises with it."),
    }
    if not ok:
        raise InputDrift("T1 re-extraction differs from frozen values: %r" % detail)
    return detail


def verify_T2():
    path = rp(T2_PATH)
    with open(path, encoding="utf-8") as fh:
        all_lines = fh.readlines()
    lines = all_lines[T2_LINES[0] - 1: T2_LINES[1]]
    pat = re.compile(
        r"For log2\(p\)\s*[^\d]*?(\d+)[^:]*:\s*[^\d]*?2\^([0-9.]+) "
        r"F_\{p\^2\}-operations and memory [^\d]*?2\^([0-9.]+); "
        r"\(previous methods:[^\d]*?2\^([0-9.]+)")
    P, Lp, Lm, Lprev = [], [], [], []
    for ln in lines:
        m = pat.search(ln)
        if not m:
            raise InputDrift("T2 line did not parse: %r" % ln)
        P.append(int(m.group(1)))
        Lp.append(float(m.group(2)))
        Lm.append(float(m.group(3)))
        Lprev.append(float(m.group(4)))
    ok_paper = (P == T2_P and Lp == T2_LPAPER and Lm == T2_LMEM and Lprev == T2_LPREV)

    # independent transcription check against PAPER_PAIRS in cost_model.py
    cm_path = rp(COST_MODEL_PATH)
    with open(cm_path, encoding="utf-8") as fh:
        cm_lines = fh.readlines()
    seg = "".join(cm_lines[59:66])  # lines 60..66, 1-indexed
    pairs = {int(a): (float(b), float(c)) for a, b, c in
             re.findall(r"(\d+):\s*\(([0-9.]+),\s*([0-9.]+)\)", seg)}
    ok_pairs = (sorted(pairs) == T2_P and
                all(pairs[p] == (t, m) for p, t, m in zip(T2_P, T2_LPAPER, T2_LMEM)))

    detail = {
        "path": T2_PATH, "lines": list(T2_LINES),
        "P_reextracted": P, "L_paper_reextracted": Lp,
        "L_mem_reextracted": Lm, "L_prev_reextracted": Lprev,
        "matches_frozen_columns": ok_paper,
        "independent_transcription_source": COST_MODEL_PATH + " lines 60-66",
        "PAPER_PAIRS_reextracted": {str(k): list(v) for k, v in sorted(pairs.items())},
        "matches_independent_transcription": ok_pairs,
        "sha256_paper": sha256_file(path),
        "sha256_cost_model": sha256_file(cm_path),
        "convention_note": (
            "L_prev equals P/2 at all five rows to the stated precision (the "
            "paper's own convention log2 k_DG = 0). This is a TRANSCRIPTION, not "
            "an independently verified Delfs-Galbraith constant (HEUR-XO-2)."),
        "L_prev_equals_P_over_2": [abs(lp - p / 2.0) for lp, p in zip(Lprev, P)],
    }
    if not (ok_paper and ok_pairs):
        raise InputDrift("T2 transcription mismatch: %r" % detail)
    return detail


# ---------------------------------------------------------------------------
# STEP 2 -- per-entry laws
# ---------------------------------------------------------------------------

def fit_laws():
    x = [float(v) for v in T1_X]
    y = list(T1_Y)
    n = len(x)
    a1 = sum(xi * yi for xi, yi in zip(x, y)) / sum(xi * xi for xi in x)
    a2 = 2.0 * 8.1
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    a3 = sxy / sxx
    b3 = my - a3 * mx
    a4 = y[-1] / x[-1]
    return {"a1": a1, "a2": a2, "a3": a3, "b3": b3, "a4": a4, "n": n}


COEF = None  # populated in main


def E_law(name, P):
    """Per-entry contribution in bits.  Returns (value, undefined_reason)."""
    if name == "L1":
        return math.log2(COEF["a1"] * P), None
    if name == "L2":
        return math.log2(COEF["a2"] * P), None
    if name == "L3":
        v = COEF["a3"] * P + COEF["b3"]
        if v <= 0:
            return None, "L3_undefined_a3P_plus_b3_nonpositive"
        return math.log2(v), None
    if name == "L4":
        return math.log2(COEF["a4"] * P), None
    if name == "L5":
        return math.log2(T1_Y[-1] * (P / 40.0) ** 1.1321), None
    if name == "N0":
        return 0.0, None
    if name == "N1":
        return 9.8, None
    raise ValueError(name)


# ---------------------------------------------------------------------------
# STEP 3 -- T2 interpolation (piecewise linear, window is a HARD boundary)
# ---------------------------------------------------------------------------

def _interp(P, col):
    if P < P_LO or P > P_HI:
        raise ValueError("EVALUATION OUTSIDE WINDOW [256, 768] IS REFUSED: P=%r" % P)
    for i in range(len(T2_P) - 1):
        lo, hi = T2_P[i], T2_P[i + 1]
        if lo <= P <= hi:
            if P == lo:
                return col[i]
            if P == hi:
                return col[i + 1]
            t = (P - lo) / (hi - lo)
            return col[i] + t * (col[i + 1] - col[i])
    raise ValueError("unreachable P=%r" % P)


def L_paper(P):
    return _interp(P, T2_LPAPER)


def L_mem(P):
    return _interp(P, T2_LMEM)


def bracketing_rows(P):
    if P in [float(v) for v in T2_P]:
        return {"exact_committed_row": P, "bracketing_rows": None}
    for i in range(len(T2_P) - 1):
        if T2_P[i] < P < T2_P[i + 1]:
            return {"exact_committed_row": None,
                    "bracketing_rows": [T2_P[i], T2_P[i + 1]]}
    return {"exact_committed_row": None, "bracketing_rows": None}


def stamps_for(P):
    st = {"fit_window_extrapolation": True,
          "extrapolation_ratio": (P / 40.0) if P is not None else None,
          "fit_window_log2p": [9, 40],
          "responsible_input": "T1 (" + T1_PATH + "), HEUR-XO-1"}
    if P is not None:
        st.update(bracketing_rows(P))
        st["interpolated_between_committed_rows"] = st["bracketing_rows"]
    return st


# ---------------------------------------------------------------------------
# STEP 4 -- cost functions
# ---------------------------------------------------------------------------

def T_A_full(P, law, S, A, c):
    """Assessed-method cost with NO memory term (both conventions share it)."""
    e, undef = E_law(law, P)
    if undef:
        return None, undef
    return L_paper(P) + e + S + c * math.sqrt(P) + A, None


def T_A(P, w, law, S, A, c, mc):
    base, undef = T_A_full(P, law, S, A, c)
    if undef:
        return None, undef
    if mc == "MC_P13":
        return base - 0.5 * min(w, L_mem(P)), None
    if mc == "MC_VOW":
        if w < L_mem(P):
            return None, "INFEASIBLE_AT_MEMORY"
        return base, None
    raise ValueError(mc)


def T_B(P, w, A, mc, k=LOG2_K_DG):
    if mc == "MC_P13":
        return P / 2.0 + k + A
    if mc == "MC_VOW":
        return P / 2.0 + k + A - 0.5 * w
    raise ValueError(mc)


def delta(P, w, law, S, A, c, mc, k=LOG2_K_DG):
    """Delta = T_B - T_A; positive means the assessed method is cheaper.
    Returns (value, reason_if_undefined)."""
    ta, undef = T_A(P, w, law, S, A, c, mc)
    if undef:
        return None, undef
    return T_B(P, w, A, mc, k) - ta, None


# ---------------------------------------------------------------------------
# STEP 5 -- the crossover solver (ONE code path; nulls swap only E)
# ---------------------------------------------------------------------------

SCAN_PS = [P_LO + i * P_SCAN_STEP for i in range(int((P_HI - P_LO) / P_SCAN_STEP) + 1)]
assert len(SCAN_PS) == 513


def solve_cell(law, S, A, c, mc, w, k=LOG2_K_DG, track=None):
    """Steps 1-6 of crossover_procedure, identically for laws and nulls."""
    vals = []
    for P in SCAN_PS:
        g, undef = delta(P, w, law, S, A, c, mc, k)
        vals.append((P, g, undef))
    feas = [(P, g) for (P, g, u) in vals if u is None]
    undef_reasons = sorted({u for (_, _, u) in vals if u is not None})

    out = {"n_feasible_scan_points": len(feas),
           "n_masked_scan_points": len(vals) - len(feas),
           "mask_reasons": undef_reasons}

    if not feas:
        out["outcome"] = ("INFEASIBLE_AT_MEMORY"
                          if "INFEASIBLE_AT_MEMORY" in undef_reasons
                          else "UNDEFINED_" + (undef_reasons[0] if undef_reasons else "UNKNOWN"))
        out["smallest_log2_w_making_P256_feasible"] = 92.5
        out["p_star"] = None
        out["delta_at_P_lo"] = None
        out["delta_at_P_hi"] = None
        return out

    out["delta_at_P_lo"] = feas[0][1]
    out["delta_at_P_hi"] = feas[-1][1]
    out["P_lo_feasible"] = feas[0][0]
    out["P_hi_feasible"] = feas[-1][0]
    out["sign_at_P_lo"] = (0 if feas[0][1] == 0 else (1 if feas[0][1] > 0 else -1))
    out["sign_at_P_hi"] = (0 if feas[-1][1] == 0 else (1 if feas[-1][1] > 0 else -1))

    if track is not None:
        for P, g in feas:
            if abs(g) < track["min_abs"]:
                track["min_abs"] = abs(g)
                track["cell"] = {"law": law, "S": S, "A": A, "c": c, "MC": mc,
                                 "log2_w": w, "log2_p": P, "delta": g}

    roots, brackets = [], []
    for i in range(len(feas) - 1):
        P0, g0 = feas[i]
        P1, g1 = feas[i + 1]
        if g0 == 0.0:
            roots.append(P0)
            brackets.append([P0, P0])
            continue
        if g0 * g1 < 0:
            lo, hi, glo = P0, P1, g0
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                gm, _u = delta(mid, w, law, S, A, c, mc, k)
                if gm == 0.0 or abs(gm) < 1e-9:
                    lo = hi = mid
                    break
                if glo * gm < 0:
                    hi = mid
                else:
                    lo, glo = mid, gm
            roots.append(0.5 * (lo + hi))
            brackets.append([P0, P1])
    if feas[-1][1] == 0.0:
        roots.append(feas[-1][0])
        brackets.append([feas[-1][0], feas[-1][0]])

    if not roots:
        out["outcome"] = "NO_CROSSOVER_IN_WINDOW"
        out["p_star"] = None
        return out

    outside = [r for r in roots if r < P_LO - 1e-12 or r > P_HI + 1e-12]
    if outside:
        out["outcome"] = "ROOT_OUTSIDE_WINDOW"
        out["direction"] = ["below_256" if r < P_LO else "above_768" for r in outside]
        out["p_star"] = None
        return out

    if len(roots) > 1:
        out["outcome"] = "MULTIPLE_ROOTS"
        out["roots"] = roots
        out["knife_edge_brackets"] = brackets
        out["p_star"] = None
        return out

    out["outcome"] = "NUMERIC"
    out["p_star"] = roots[0]
    out["knife_edge_bracket"] = brackets[0]
    out["residual_g_at_root"] = delta(roots[0], w, law, S, A, c, mc, k)[0]
    return out


# ---------------------------------------------------------------------------
# XCHK-1 -- second, independently written expression path for T_A(256)
# ---------------------------------------------------------------------------

def xchk1():
    """Direct summation of the committed literals, written out by hand, with
    log base change done as log(x)/log(2) rather than log2()."""
    ln2 = math.log(2.0)
    sxy = (9.0 * 143.72875226039784 + 14.0 * 192.67237687366168
           + 17.0 * 244.77013354917037 + 20.0 * 293.178645371192
           + 24.0 * 343.926267281106 + 28.0 * 439.4038324400175
           + 32.0 * 515.2952824694235 + 40.0 * 651.0768243785084)
    sxx = (81.0 + 196.0 + 289.0 + 400.0 + 576.0 + 784.0 + 1024.0 + 1600.0)
    a1_alt = sxy / sxx
    n = 8.0
    sx = 9.0 + 14.0 + 17.0 + 20.0 + 24.0 + 28.0 + 32.0 + 40.0
    sy = (143.72875226039784 + 192.67237687366168 + 244.77013354917037
          + 293.178645371192 + 343.926267281106 + 439.4038324400175
          + 515.2952824694235 + 651.0768243785084)
    a3_alt = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    b3_alt = (sy - a3_alt * sx) / n
    a4_alt = 651.0768243785084 / 40.0
    vals = {
        "L1": 106.5 + math.log(a1_alt * 256.0) / ln2,
        "L2": 106.5 + math.log(16.2 * 256.0) / ln2,
        "L3": 106.5 + math.log(a3_alt * 256.0 + b3_alt) / ln2,
        "L4": 106.5 + math.log(a4_alt * 256.0) / ln2,
    }
    return vals, {"a1": a1_alt, "a3": a3_alt, "b3": b3_alt, "a4": a4_alt}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--mem-limit-gb", type=float, default=1.0)
    args = ap.parse_args()
    if args.seed != SEED:
        raise SystemExit("seed is frozen at 0")

    try:
        cap = int(args.mem_limit_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        mem_cap_applied = cap
    except (ValueError, OSError) as exc:  # pragma: no cover
        mem_cap_applied = None
        say("WARNING: could not apply RLIMIT_AS: %s" % exc)

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    t_start = time.time()
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    say("== EXP-SSI-697354 / RUN-SSI-697354-a ==")
    say("Deterministic arithmetic on committed numbers. seed=%d (form only)." % SEED)
    say("Memory cap applied (RLIMIT_AS bytes): %r" % mem_cap_applied)

    # ---------------- step 0: environment ----------------
    env = build_environment()
    env["memory_cap_bytes"] = mem_cap_applied
    env["started_at"] = started_at
    if env["forbidden_modules_imported"]:
        raise SystemExit("FORBIDDEN MODULE IMPORTED -- run invalid")
    with open(os.path.join(outdir, "environment.json"), "w") as fh:
        json.dump(env, fh, indent=2, sort_keys=True)
    say("environment.json written. numpy present: %s; forbidden modules present: %s"
        % (env["module_presence"]["numpy"]["present"],
           {m: env["module_presence"][m]["present"] for m in FORBIDDEN_MODULES}))

    # ---------------- step 1: input integrity ----------------
    t1 = verify_T1()
    t2 = verify_T2()
    say("T1 re-extraction exact: %s ; T2 paper match: %s ; T2 independent "
        "transcription match: %s" % (t1["float_equality_exact"],
                                     t2["matches_frozen_columns"],
                                     t2["matches_independent_transcription"]))

    input_hashes = {
        "recorded_at": started_at,
        "files": {
            T1_PATH: sha256_file(rp(T1_PATH)),
            T2_PATH: sha256_file(rp(T2_PATH)),
            COST_MODEL_PATH: sha256_file(rp(COST_MODEL_PATH)),
            RED_TEAM_PATH: sha256_file(rp(RED_TEAM_PATH)),
            SPEC_PATH: sha256_file(rp(SPEC_PATH)),
            "experiments/EXP-SSI-697354/crossover.py": sha256_file(os.path.abspath(__file__)),
        },
        "freeze_receipt": {
            "specification_path": SPEC_PATH,
            "specification_sha256": sha256_file(rp(SPEC_PATH)),
            "frozen": True,
            "frozen_at": "2026-08-06",
            "frozen_by": "coordinator",
            "freeze_task": "TASK-20260806-976fd5",
            "read_only_during_execution": True,
            "note": ("The Executor did not modify specification.yaml. This hash "
                     "binds the contract text that governed this run."),
        },
        "scalar_sources": {
            "S_struct": RED_TEAM_PATH + " verdict.security_estimate_range.F_p2_operations",
            "A_aes_log2_alpha": RED_TEAM_PATH + " OBJ-6",
            "c_overhead_scenario": "EV-WESO-001 observations + " + COST_MODEL_PATH + " line 68",
            "log2_k_DG": "T2 column L_prev (paper's own previous-methods figures)",
            "global_storage_log2_bytes": RED_TEAM_PATH + " OBJ-5",
            "bytes_per_entry": RED_TEAM_PATH + " OBJ-5",
            "log2_w_grid": "H-SSI-7fe2bf test_boundary.parameters.log2_w_grid (14 values)",
        },
    }
    with open(os.path.join(outdir, "input_hashes.json"), "w") as fh:
        json.dump(input_hashes, fh, indent=2, sort_keys=True)
    with open(os.path.join(outdir, "freeze_receipt.json"), "w") as fh:
        json.dump(input_hashes["freeze_receipt"], fh, indent=2, sort_keys=True)

    # ---------------- step 2: fit the laws ----------------
    global COEF
    COEF = fit_laws()
    say("fitted coefficients: a1=%.9f a2=%.9f a3=%.9f b3=%.9f a4=%.9f"
        % (COEF["a1"], COEF["a2"], COEF["a3"], COEF["b3"], COEF["a4"]))

    # ---------------- RG gate FIRST ----------------
    gate = run_reproduction_gate()
    with open(os.path.join(outdir, "reproduction_gate.json"), "w") as fh:
        json.dump(gate, fh, indent=2, sort_keys=True)
    say("RG verdicts: " + json.dumps(gate["verdicts"]))
    if not gate["all_pass"]:
        say("REPRODUCTION GATE FAILED -- stopping before any curve is computed "
            "(specification stopping_rules; proposal falsifier F1).")
        raw = {"experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
               "status": "invalid", "invalid_reason": "RG gate failure",
               "reproduction_gate": gate}
        with open(os.path.join(outdir, "raw-result.json"), "w") as fh:
            json.dump(raw, fh, indent=2, sort_keys=True)
        return 2

    # ---------------- MONO-5 (data check on T2) ----------------
    mono5 = run_mono5()
    say("MONO-5 verdict: %s" % mono5["verdict"])

    # ---------------- main + null + sensitivity grids ----------------
    say("solving grids ...")
    grids = solve_all_grids()
    say("main cells: %d ; null cells: %d ; L5 cells: %d"
        % (len(grids["main"]), len(grids["null"]), len(grids["l5"])))

    # ---------------- controls / metrics ----------------
    nullrep = null_object_report(grids)
    mono = mono3_and_4(grids, monotonicity_report(mono5))
    say("MONO verdicts: " + json.dumps(mono["blocking_limbs_verdict"])
        + " ; MONO-3: " + mono["MONO-3_verdict"])
    scope = scope_report()
    sens = sensitivity_report(grids)
    undef = undefined_segments(grids)
    tails = tail_checks(grids)
    p_star_table = p_star_table_report(grids)
    bandcmp = band_width_comparison(grids)
    p_star_table["summary"]["band_width_comparison_at_P256_w30"] = bandcmp
    say("band-width comparison at (P=256, log2 w=30): " + json.dumps(
        {k: bandcmp.get(k) for k in ["n_numeric_loci", "p_star_band_width_over_midpoint",
                                     "margin_band_width_over_abs_midpoint", "verdict"]}))

    for name, obj in [("p_star_table.json", p_star_table),
                      ("null_object.json", nullrep),
                      ("monotonicity.json", mono),
                      ("undefined_segments.json", undef),
                      ("scope_statement.json", scope),
                      ("sensitivity.json", sens)]:
        with open(os.path.join(outdir, name), "w") as fh:
            json.dump(obj, fh, indent=2, sort_keys=True)

    # XCHK-2 (optional, numpy)
    xchk2 = {"id": "XCHK-2", "blocking": False}
    try:
        import numpy  # noqa: F401  (optional secondary cross-check only)
        xchk2["status"] = "AVAILABLE_BUT_NOT_RUN"
        xchk2["detail"] = ("numpy import succeeded; XCHK-2 re-derivation was not "
                           "attempted -- see execution report.")
    except ImportError as exc:
        xchk2["status"] = "NOT_RUN"
        xchk2["import_error_text"] = repr(exc)
        xchk2["detail"] = ("numpy is absent, so the optional Dickman-rho "
                           "re-derivation of L_paper/L_mem was not run. Per "
                           "specification.infrastructure_failure_disposition this "
                           "is INFRASTRUCTURE SIGNAL, changes no reported number, "
                           "and is not a finding about the cost model.")
        xchk2["tolerance_that_would_have_applied_bits"] = 3.51
    with open(os.path.join(outdir, "cross_check_secondary.json"), "w") as fh:
        json.dump(xchk2, fh, indent=2, sort_keys=True)
    say("XCHK-2: %s" % xchk2["status"])

    wall = time.time() - t_start
    ru = resource.getrusage(resource.RUSAGE_SELF)
    finished_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    out_of_window = [r for r in grids["main"] + grids["null"] + grids["l5"]
                     if r["p_star"] is not None
                     and not (P_LO - 1e-12 <= r["p_star"] <= P_HI + 1e-12)]
    unstamped = [r for r in grids["main"] + grids["null"] + grids["l5"]
                 if r["stamps"].get("fit_window_extrapolation") is not True]
    validity = {
        "invalidation_rules_checked": {
            "RG-1..RG-5 all pass": gate["all_pass"],
            "XCHK-1 within 1e-12": gate["XCHK-1"]["pass"],
            "input rows match frozen values": (t1["float_equality_exact"]
                                               and t2["matches_frozen_columns"]),
            "T2 independent transcription matches": t2["matches_independent_transcription"],
            "MONO-1 pass": mono["MONO-1"]["pass"],
            "MONO-2 pass": mono["MONO-2"]["pass"],
            "MONO-4 pass": mono["MONO-4"]["pass"],
            "MONO-5 pass": mono["MONO-5"]["pass"],
            "no p* outside [256, 768]": not out_of_window,
            "every cell carries its extrapolation stamp": not unstamped,
            "undefined_segments.json non-empty": undef["summary"]["n_entries"] > 0,
            "no forbidden module imported": not env["forbidden_modules_imported"],
            "no reported number depends on numpy": True,
        },
        "n_p_star_outside_window": len(out_of_window),
        "n_cells_missing_extrapolation_stamp": len(unstamped),
    }
    validity["all_invalidation_rules_satisfied"] = all(
        validity["invalidation_rules_checked"].values())
    say("invalidation rules all satisfied: %s"
        % validity["all_invalidation_rules_satisfied"])

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "status": "completed",
        "validity": validity,
        "seed": SEED,
        "determinism_note": ("No randomness is used anywhere; a re-run is "
                             "byte-identical apart from timing fields."),
        "timing": {"started_at": started_at, "finished_at": finished_at,
                   "wall_seconds": wall,
                   "cpu_user_seconds": ru.ru_utime,
                   "cpu_sys_seconds": ru.ru_stime},
        "resources": {"peak_rss_bytes": ru.ru_maxrss * 1024,
                      "memory_cap_bytes": mem_cap_applied},
        "input_integrity": {"T1": t1, "T2": t2},
        "fitted_coefficients": COEF,
        "coefficient_vs_frozen_reference": {
            k: {"computed": COEF[k], "frozen_reference": FROZEN_REF[k],
                "abs_diff": abs(COEF[k] - FROZEN_REF[k])}
            for k in ["a1", "a2", "a3", "b3", "a4"]},
        "reproduction_gate": gate,
        "cross_check_XCHK1": gate["XCHK-1"],
        "cross_check_XCHK2": xchk2,
        "null_object": nullrep,
        "monotonicity": mono,
        "p_star_summary": p_star_table["summary"],
        "scope": scope,
        "sensitivity": sens,
        "tail_checks": tails,
        "undefined_segments_summary": undef["summary"],
        "grid_counts": {"main_cells": len(grids["main"]),
                        "null_cells": len(grids["null"]),
                        "l5_sensitivity_cells": len(grids["l5"]),
                        "k_dg_sensitivity_cells": grids["k_cells"]},
        "measured_vs_modeled": {
            "measured_inputs": [
                "T1 avg_mults_per_entry at log2 p in [9, 40] (prior measurement, "
                "re-read and hash-bound here; NOT re-measured by this run)"],
            "transcribed_inputs": [
                "T2 L_paper / L_mem / L_prev (paper Section 4.1 transcription)",
                "T3 declared scalars S_struct, A, c, log2_k_DG, storage figures"],
            "modeled_outputs": [
                "every T_A, T_B, Delta, p*, band, gap and displacement in this file"],
            "optimistic_assumptions_carried": [
                "HEUR-XO-1: the affine per-entry law fitted at log2 p in [9, 40] "
                "with ell in {2,3,5} is used at log2 p in [256, 768]; "
                "extrapolation_ratio in [6.4, 19.2].",
                "HEUR-XO-2: log2 k_DG = 0 is a transcription of the paper's own "
                "previous-methods column, not an independently verified constant.",
                "HEUR-XO-3: exactly one memory-charging convention is physically "
                "correct; the corpus commits both and reconciles neither.",
                "Wesolowski Heuristic 1 is assumed and is UNVALIDATED in this corpus.",
                "c = 0.0 and A = -1.736966 (pure RAM) are attacker-favourable "
                "corners, never neutral defaults."],
        },
    }
    with open(os.path.join(outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh, indent=2, sort_keys=True)

    say("wall_seconds=%.3f peak_rss_bytes=%d" % (wall, ru.ru_maxrss * 1024))
    say("done.")
    return 0


# ---------------------------------------------------------------------------
# reproduction gate
# ---------------------------------------------------------------------------

def run_reproduction_gate():
    g = {"id": "RG-REPRODUCTION-GATE", "blocking": True,
         "parameters": {"log2_p": 256, "memory": "unbounded (no memory term)",
                        "baseline": "memoryless", "c": 0.0},
         "units_note": ("T_A here is in log2 F_{p^2}-operations when A = 0, and "
                        "in log2 AES-equivalents when A != 0."),
         "residuals_unit": "bits"}

    rg1 = {}
    for law in LAWS_MAIN:
        v, _ = T_A_full(256.0, law, 0.0, 0.0, 0.0)
        e, _ = E_law(law, 256.0)
        rg1[law] = {
            "E_at_256": e,
            "E_at_256_frozen_reference": FROZEN_REF["E_at_256"][law],
            "E_residual_bits": e - FROZEN_REF["E_at_256"][law],
            "T_A_256": v,
            "T_A_256_frozen_reference": FROZEN_REF["T_A_256_S0_A0"][law],
            "residual_vs_frozen_reference_bits": v - FROZEN_REF["T_A_256_S0_A0"][law],
            "residual_vs_committed_anchor_118_5_bits": v - 118.5,
            "in_window_118_25_118_75": 118.25 <= v <= 118.75,
            "stamps": stamps_for(256.0),
        }
    g["RG-1"] = {"statement": ("For each of L1..L4: T_A(256) with S=0, A=0, c=0 "
                              "lies in [118.25, 118.75]."),
                 "per_law": rg1,
                 "pass": all(r["in_window_118_25_118_75"] for r in rg1.values())}

    rg2 = {}
    for law in LAWS_MAIN:
        v, _ = T_A_full(256.0, law, 3.0, 0.0, 0.0)
        rg2[law] = {"T_A_256_S3": v,
                    "residual_vs_committed_anchor_121_5_bits": v - 121.5,
                    "in_window_121_25_121_75": 121.25 <= v <= 121.75,
                    "stamps": stamps_for(256.0)}
    g["RG-2"] = {"statement": "Same with S = 3.0 lies in [121.25, 121.75].",
                 "per_law": rg2,
                 "pass": all(r["in_window_121_25_121_75"] for r in rg2.values())}

    rg3 = {}
    A3 = 1.584963
    for law in LAWS_MAIN:
        lo, _ = T_A_full(256.0, law, 0.0, A3, 0.0)
        hi, _ = T_A_full(256.0, law, 3.0, A3, 0.0)
        rg3[law] = {"T_A_256_S0_A_alpha3": lo,
                    "T_A_256_S3_A_alpha3": hi,
                    "residual_vs_committed_anchor_120_bits": lo - 120.0,
                    "residual_vs_committed_anchor_123_bits": hi - 123.0,
                    "lo_in_119_9_120_4": 119.9 <= lo <= 120.4,
                    "hi_in_122_9_123_4": 122.9 <= hi <= 123.4,
                    "stamps": stamps_for(256.0)}
    g["RG-3"] = {"statement": ("Applying A = 1.584963 (alpha = 3, hardware) gives "
                              "[119.9, 120.4] and [122.9, 123.4]."),
                 "unit": "log2 AES-equivalents (hardware model)",
                 "per_law": rg3,
                 "pass": all(r["lo_in_119_9_120_4"] and r["hi_in_122_9_123_4"]
                             for r in rg3.values())}

    lows = [rg1[l]["T_A_256"] for l in LAWS_MAIN]
    highs = [rg3[l]["T_A_256_S3_A_alpha3"] for l in LAWS_MAIN]
    lo_repro, hi_repro = min(lows), max(highs)
    g["RG-4"] = {
        "statement": ("EV-SSI-59f7a2's headline bracket [118.5, 123.0] is "
                      "reproduced with both endpoints within 0.25 bits, and the "
                      "UNIT of each endpoint is recorded."),
        "reproduced_low_endpoint": lo_repro,
        "reproduced_high_endpoint": hi_repro,
        "low_residual_bits": lo_repro - 118.5,
        "high_residual_bits": hi_repro - 123.0,
        "low_within_0_25": abs(lo_repro - 118.5) <= 0.25,
        "high_within_0_25": abs(hi_repro - 123.0) <= 0.25,
        "unit_of_low_endpoint": "log2 F_{p^2}-operations (S = 0, A = 0)",
        "unit_of_high_endpoint": ("log2 AES-equivalents, hardware model "
                                  "alpha = 3 (S = 3.0, A = 1.584963)"),
        "units_differ": True,
        "UNIT_MIXING_DISCLOSURE": (
            "The two endpoints of the committed headline bracket [118.5, 123.0] "
            "are in DIFFERENT UNITS. The low endpoint 2^{118.5} is stated by "
            "red_team_concrete_cost.yaml verdict.security_estimate_range."
            "F_p2_operations as an F_{p^2}-operation count; the high endpoint "
            "2^{123} is the upper end of AES_equivalent_hardware. This run "
            "reproduces each endpoint in its own unit and reports the mixing "
            "rather than silently converting. This is a disclosure ABOUT THE "
            "INPUT RECORD, not a defect of this run."),
        "pass": (abs(lo_repro - 118.5) <= 0.25 and abs(hi_repro - 123.0) <= 0.25),
        "stamps": stamps_for(256.0),
    }

    # RG-5
    cells = []
    for law in LAWS_MAIN:
        for S in S_STRUCT:
            for A in A_AES:
                v, _ = T_A_full(256.0, law, S, A, 0.0)
                cells.append({"law": law, "S": S, "A": A,
                              "A_label": A_LABELS[A],
                              "T_A_256": v, "gap_below_128_bits": 128.0 - v})
    gaps = [c["gap_below_128_bits"] for c in cells]
    inside = [c for c in cells if 6.0 <= c["gap_below_128_bits"] <= 11.0]
    g["RG-5"] = {
        "statement": ("Over the scenario grid at P = 256 (4 laws x 2 S x 4 A, "
                      "c = 0), min gap <= 6.5 and max gap >= 10.5, covering the "
                      "committed interval [6, 11] bits."),
        "committed_interval": [6.0, 11.0],
        "grid_min_gap_bits": min(gaps),
        "grid_max_gap_bits": max(gaps),
        "grid_span_bits": [min(gaps), max(gaps)],
        "grid_span_wider_than_committed_interval": (min(gaps) < 6.0 or max(gaps) > 11.0),
        "min_gap_le_6_5": min(gaps) <= 6.5,
        "max_gap_ge_10_5": max(gaps) >= 10.5,
        "named_subgrid_reproducing_6_to_11": {
            "rule": ("the set of (law, S, A) cells at c = 0, P = 256 whose gap "
                     "below 2^128 lies inside [6, 11] bits"),
            "n_cells": len(inside),
            "cells": inside,
            "subgrid_min_gap_bits": (min(c["gap_below_128_bits"] for c in inside)
                                     if inside else None),
            "subgrid_max_gap_bits": (max(c["gap_below_128_bits"] for c in inside)
                                     if inside else None),
            "A_values_present": sorted({c["A"] for c in inside}),
            "S_values_present": sorted({c["S"] for c in inside}),
        },
        "all_cells": cells,
        "frozen_reference_gap_NIST_I_L1_S0_A0": FROZEN_REF["gap_below_target_S0_A0_c0"]["NIST-I"],
        "residual_vs_frozen_reference_bits": (
            [c for c in cells if c["law"] == "L1" and c["S"] == 0.0
             and c["A"] == 0.0][0]["gap_below_128_bits"]
            - FROZEN_REF["gap_below_target_S0_A0_c0"]["NIST-I"]),
        "stamps": stamps_for(256.0),
        "pass": (min(gaps) <= 6.5 and max(gaps) >= 10.5),
    }

    # XCHK-1
    alt, altcoef = xchk1()
    x1 = {"id": "XCHK-1", "blocking": True, "tolerance": 1e-12, "per_law": {}}
    worst = 0.0
    for law in LAWS_MAIN:
        primary = rg1[law]["T_A_256"]
        d = abs(primary - alt[law])
        worst = max(worst, d)
        x1["per_law"][law] = {"primary_path": primary,
                              "independent_expression_path": alt[law],
                              "abs_difference": d,
                              "agrees_to_1e-12": d <= 1e-12}
    x1["alternative_coefficients"] = altcoef
    x1["max_abs_difference"] = worst
    x1["pass"] = worst <= 1e-12
    g["XCHK-1"] = x1

    # A-cancellation check (specification cost_functions.margin.unit_cancellation_note)
    devs = []
    for law in LAWS_MAIN:
        for S in S_STRUCT:
            for c in C_OVERHEAD:
                for mc in MC_LIST:
                    for w in W_GRID:
                        for P in (256.0, 768.0):
                            vs = []
                            for A in A_AES:
                                d, u = delta(P, w, law, S, A, c, mc)
                                if u is None:
                                    vs.append(d)
                            if len(vs) > 1:
                                devs.append(max(vs) - min(vs))
    g["A_cancellation_check"] = {
        "statement": ("A appears on both sides of Delta and cancels; it is "
                      "retained in T_A and T_B (where it matters for the "
                      "absolute-cost gate) and is not silently dropped."),
        "max_spread_of_Delta_over_the_4_A_values": max(devs) if devs else None,
        "n_comparisons": len(devs),
        "tolerance": 1e-12,
        "pass": (max(devs) <= 1e-12) if devs else None,
    }

    g["verdicts"] = {k: g[k]["pass"] for k in
                     ["RG-1", "RG-2", "RG-3", "RG-4", "RG-5", "XCHK-1"]}
    g["all_pass"] = all(g["verdicts"].values())
    g["on_failure_rule"] = ("RUN INVALID; nothing else may be emitted "
                            "(proposal falsifier F1).")
    return g


# ---------------------------------------------------------------------------
# MONO-5 (data check on the committed T2 columns)
# ---------------------------------------------------------------------------

def run_mono5():
    P = [float(p) for p in T2_P]
    lp, lm = T2_LPAPER, T2_LMEM
    lp_inc = all(lp[i] < lp[i + 1] for i in range(4))
    lm_inc = all(lm[i] < lm[i + 1] for i in range(4))
    o1 = [lp[i] - P[i] / 3.0 for i in range(5)]
    o1m = [lm[i] - P[i] / 3.0 for i in range(5)]
    o1_inc = all(o1[i] < o1[i + 1] for i in range(4))
    o1_in_band = all(21.0 <= v <= 47.0 for v in o1)
    o1m_nondec = all(o1m[i] <= o1m[i + 1] + 1e-12 for i in range(4))
    ok = lp_inc and lm_inc and o1_inc and o1_in_band and o1m_nondec
    return {
        "id": "MONO-5", "kind": "DATA CHECK on the 5 committed T2 rows",
        "L_paper_strictly_increasing": lp_inc,
        "L_mem_strictly_increasing": lm_inc,
        "L_paper_minus_P_over_3": o1,
        "L_paper_minus_P_over_3_frozen_reference": FROZEN_REF["L_paper_minus_P_over_3"],
        "L_paper_minus_P_over_3_residuals_bits": [
            a - b for a, b in zip(o1, FROZEN_REF["L_paper_minus_P_over_3"])],
        "L_paper_minus_P_over_3_strictly_increasing": o1_inc,
        "L_paper_minus_P_over_3_in_21_47": o1_in_band,
        "L_mem_minus_P_over_3": o1m,
        "L_mem_minus_P_over_3_frozen_reference": FROZEN_REF["L_mem_minus_P_over_3"],
        "L_mem_minus_P_over_3_residuals_bits": [
            a - b for a, b in zip(o1m, FROZEN_REF["L_mem_minus_P_over_3"])],
        "L_mem_minus_P_over_3_non_decreasing": o1m_nondec,
        "verdict": "PASS" if ok else "FAIL",
        "pass": ok,
        "why_it_matters": ("L_paper(P) - P/3 is the only in-corpus handle on the "
                           "superpolynomial o(1) term."),
    }


# ---------------------------------------------------------------------------
# grids
# ---------------------------------------------------------------------------

def solve_all_grids():
    """Delta does not depend on A (A cancels; verified separately in the gate),
    so cells are solved once per (law,S,c,MC,w,k) and the result is attached to
    each of the 4 declared A values.  Every declared cell is still emitted."""
    track = {"min_abs": float("inf"), "cell": None}
    main, nulls, l5 = [], [], []
    k_cells = 0

    def emit(law, arm, target):
        nonlocal k_cells
        for S in S_STRUCT:
            for c in C_OVERHEAD:
                for mc in MC_LIST:
                    for w in W_GRID:
                        base = solve_cell(law, S, 0.0, c, mc, w,
                                          track=(track if arm == "main" else None))
                        ksens = None
                        if arm == "main":
                            ksens = {}
                            for k in LOG2_K_DG_SENS:
                                if k == 0.0:
                                    ksens[repr(k)] = base["p_star"]
                                else:
                                    ksens[repr(k)] = solve_cell(
                                        law, S, 0.0, c, mc, w, k=k)["p_star"]
                                    k_cells += 1
                        for A in A_AES:
                            row = dict(base)
                            row.update({"law": law, "arm": arm, "S": S, "A": A,
                                        "A_label": A_LABELS[A], "c": c,
                                        "MC": mc, "log2_w": w,
                                        "log2_k_DG": LOG2_K_DG})
                            row["stamps"] = stamps_for(row.get("p_star"))
                            row["stamps"]["window_endpoints_stamped"] = {
                                "P_lo": stamps_for(P_LO)["extrapolation_ratio"],
                                "P_hi": stamps_for(P_HI)["extrapolation_ratio"]}
                            if ksens is not None:
                                row["p_star_vs_log2_k_DG"] = ksens
                            target.append(row)

    for law in LAWS_MAIN:
        emit(law, "main", main)
    for law in NULLS:
        emit(law, "null", nulls)
    emit("L5", "l5_sensitivity", l5)

    return {"main": main, "null": nulls, "l5": l5,
            "min_abs_delta": track, "k_cells": k_cells}


def cellkey(r):
    return (r["S"], r["A"], r["c"], r["MC"], r["log2_w"])


def p_star_table_report(grids):
    rows = grids["main"]
    labels = {}
    per_conv = {mc: {} for mc in MC_LIST}
    for r in rows:
        labels[r["outcome"]] = labels.get(r["outcome"], 0) + 1
        per_conv[r["MC"]][r["outcome"]] = per_conv[r["MC"]].get(r["outcome"], 0) + 1

    band = {}
    for w in W_GRID:
        sel = [r for r in rows if r["log2_w"] == w]
        num = [r["p_star"] for r in sel if r["outcome"] == "NUMERIC"]
        nc_attack = sum(1 for r in sel if r["outcome"] == "NO_CROSSOVER_IN_WINDOW"
                        and r["sign_at_P_lo"] > 0)
        nc_base = sum(1 for r in sel if r["outcome"] == "NO_CROSSOVER_IN_WINDOW"
                      and r["sign_at_P_lo"] <= 0)
        band[repr(w)] = {
            "p_star_band": [min(num), max(num)] if num else None,
            "n_numeric": len(num),
            "n_no_crossover_attack_side": nc_attack,
            "n_no_crossover_baseline_side": nc_base,
            "n_infeasible": sum(1 for r in sel
                                if r["outcome"] == "INFEASIBLE_AT_MEMORY"),
            "n_multiple_roots": sum(1 for r in sel
                                    if r["outcome"] == "MULTIPLE_ROOTS"),
            "n_root_outside_window": sum(1 for r in sel
                                         if r["outcome"] == "ROOT_OUTSIDE_WINDOW"),
            "n_cells": len(sel),
        }

    # sign agreement between conventions
    agree = disagree = comparable = 0
    index = {(r["law"], r["S"], r["A"], r["c"], r["MC"], r["log2_w"]): r for r in rows}
    for r in rows:
        if r["MC"] != "MC_P13":
            continue
        q = index.get((r["law"], r["S"], r["A"], r["c"], "MC_VOW", r["log2_w"]))
        if q is None:
            continue
        if r["delta_at_P_lo"] is None or q["delta_at_P_lo"] is None:
            continue
        comparable += 1
        s1 = 1 if r["delta_at_P_lo"] > 0 else (-1 if r["delta_at_P_lo"] < 0 else 0)
        s2 = 1 if q["delta_at_P_lo"] > 0 else (-1 if q["delta_at_P_lo"] < 0 else 0)
        if s1 == s2:
            agree += 1
        else:
            disagree += 1

    return {
        "rows": rows,
        "summary": {
            "n_main_cells": len(rows),
            "expected_main_cells": 4 * 2 * 4 * 5 * 2 * 14,
            "outcome_counts": labels,
            "outcome_counts_per_convention": per_conv,
            "p_star_band_per_log2_w": band,
            "convention_sign_comparison_at_P_256": {
                "n_comparable_cells": comparable,
                "n_sign_agree": agree,
                "n_sign_disagree": disagree,
                "note": ("comparison is at the window's low endpoint P = 256; "
                         "cells where MC_VOW is memory-infeasible are not "
                         "comparable and are excluded from the counts"),
            },
            "decisiveness_note": ("a convention producing 100% of a single "
                                  "categorical label is reported as decisive, "
                                  "not averaged into a band"),
        },
    }


def band_width_comparison(grids, P_match=256.0, w_match=30.0):
    """metrics.primary item 3 (the proposal's F2 comparison), reported as
    numbers only -- no verdict on the falsifier is issued here."""
    rows = [r for r in grids["main"] if r["log2_w"] == w_match]
    loci = [r["p_star"] for r in rows if r["outcome"] == "NUMERIC"]
    margins, margins_distinct = [], []
    for r in rows:
        d, u = delta(P_match, w_match, r["law"], r["S"], r["A"], r["c"], r["MC"])
        if u is None:
            margins.append(d)
            if r["A"] == 0.0:
                margins_distinct.append(d)
    out = {
        "matched_point": {"log2_p": P_match, "log2_w": w_match},
        "n_cells_at_this_w": len(rows),
        "n_numeric_loci": len(loci),
        "n_margin_cells_defined": len(margins),
        "n_margin_cells_defined_A_free": len(margins_distinct),
        "note": ("Delta is invariant in A (A cancels), so the A-free count is the "
                 "number of distinct margin values; cells where MC_VOW is "
                 "memory-infeasible at this w are excluded and counted separately"),
        "n_margin_cells_infeasible": len(rows) - len(margins),
        "stamps": stamps_for(P_match),
    }
    if margins:
        mlo, mhi = min(margins), max(margins)
        mmid = 0.5 * (mlo + mhi)
        out["margin_band_bits"] = [mlo, mhi]
        out["margin_band_width_bits"] = mhi - mlo
        out["margin_band_midpoint_bits"] = mmid
        out["margin_band_width_over_abs_midpoint"] = (
            (mhi - mlo) / abs(mmid) if mmid != 0 else None)
    if len(loci) >= 2:
        plo, phi = min(loci), max(loci)
        pmid = 0.5 * (plo + phi)
        out["p_star_band_log2p"] = [plo, phi]
        out["p_star_band_width_log2p"] = phi - plo
        out["p_star_band_midpoint_log2p"] = pmid
        out["p_star_band_width_over_midpoint"] = (phi - plo) / pmid
        out["comparison"] = {
            "p_star_fractional_width": (phi - plo) / pmid,
            "margin_fractional_width": out.get("margin_band_width_over_abs_midpoint"),
            "difference": (
                (phi - plo) / pmid - out["margin_band_width_over_abs_midpoint"]
                if out.get("margin_band_width_over_abs_midpoint") is not None
                else None),
            "interpretation_withheld": ("this run reports the two fractions; the "
                                        "F2 judgement is the reviewer's"),
        }
    else:
        out["verdict"] = "NOT_EVALUABLE_FOR_LOCUS(n = %d numeric loci)" % len(loci)
    return out


def null_object_report(grids):
    main = {(r["law"],) + cellkey(r): r for r in grids["main"]}
    nulls = {(r["law"],) + cellkey(r): r for r in grids["null"]}

    # D_null on the margin SURFACE, evaluated on the P scan grid
    prof = {"D_null0": {}, "D_null1": {}}
    extremes = {"D_null0": {"min": None, "max": None},
                "D_null1": {"min": None, "max": None}}
    for law in LAWS_MAIN:
        for P in SCAN_PS:
            e, undef = E_law(law, P)
            if undef:
                continue
            d0 = abs(e - 0.0)
            d1 = abs(e - 9.8)
            for nm, d in (("D_null0", d0), ("D_null1", d1)):
                key = (law, P)
                prof[nm].setdefault(law, {})[repr(P)] = d
                cur = extremes[nm]
                if cur["min"] is None or d < cur["min"]["value"]:
                    cur["min"] = {"value": d, "law": law, "log2_p": P}
                if cur["max"] is None or d > cur["max"]["value"]:
                    cur["max"] = {"value": d, "law": law, "log2_p": P}

    # verify the displacement identity on actual grid cells (Delta difference)
    checks = []
    for law in LAWS_MAIN:
        for S in S_STRUCT:
            for c in C_OVERHEAD:
                for mc in MC_LIST:
                    for w in W_GRID:
                        for P in (256.0, 512.0, 768.0):
                            dc, u1 = delta(P, w, law, S, 0.0, c, mc)
                            d0, u2 = delta(P, w, "N0", S, 0.0, c, mc)
                            d1, u3 = delta(P, w, "N1", S, 0.0, c, mc)
                            if u1 or u2 or u3:
                                continue
                            e, _ = E_law(law, P)
                            checks.append({
                                "law": law, "log2_p": P, "log2_w": w, "MC": mc,
                                "S": S, "c": c,
                                "D_null0_from_Delta": abs(dc - d0),
                                "D_null1_from_Delta": abs(dc - d1),
                                "D_null0_predicted_E": e,
                                "D_null1_predicted_absE_minus_9_8": abs(e - 9.8),
                            })
    max_id0 = max(abs(ch["D_null0_from_Delta"] - ch["D_null0_predicted_E"])
                  for ch in checks)
    max_id1 = max(abs(ch["D_null1_from_Delta"] - ch["D_null1_predicted_absE_minus_9_8"])
                  for ch in checks)

    # monotonicity of D_null0 in P, per law
    mono_in_P = {}
    for law in LAWS_MAIN:
        vals = [prof["D_null0"][law][repr(P)] for P in SCAN_PS]
        mono_in_P[law] = all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))

    # ordering D_null1 < D_null0 at every evaluated P
    ordering_ok = True
    ordering_viol = []
    for law in LAWS_MAIN:
        for P in SCAN_PS:
            if not (prof["D_null1"][law][repr(P)] < prof["D_null0"][law][repr(P)]):
                ordering_ok = False
                ordering_viol.append({"law": law, "log2_p": P})

    d1_at_256 = {law: prof["D_null1"][law][repr(256.0)] for law in LAWS_MAIN}

    # locus displacement
    disp = []
    for key, r in main.items():
        law = key[0]
        for nl in NULLS:
            q = nulls[(nl,) + key[1:]]
            entry = {"law": law, "null_arm": nl, "S": r["S"], "A": r["A"],
                     "c": r["c"], "MC": r["MC"], "log2_w": r["log2_w"],
                     "corrected_outcome": r["outcome"],
                     "null_outcome": q["outcome"],
                     "corrected_p_star": r["p_star"],
                     "null_p_star": q["p_star"]}
            if r["p_star"] is not None and q["p_star"] is not None:
                entry["abs_locus_displacement_log2p"] = abs(r["p_star"] - q["p_star"])
                entry["kind"] = "numeric"
            else:
                entry["abs_locus_displacement_log2p"] = None
                entry["kind"] = "categorical_transition"
                entry["transition"] = "%s -> %s" % (r["outcome"], q["outcome"])
            disp.append(entry)
    numeric_disp = [d["abs_locus_displacement_log2p"] for d in disp
                    if d["abs_locus_displacement_log2p"] is not None]

    return {
        "id": "NULL-OBJECT", "blocking": False,
        "identical_code_path": ("both null arms are solved by solve_cell(), the "
                                "same function used for L1..L4, with only E(.) "
                                "swapped; no separate solver exists"),
        "preregistered_prediction": (
            "min D_null0 >= 11.9 bits and max D_null0 <= 14.2 bits, increasing "
            "monotonically in P; D_null1 at P = 256 in [1.5, 4.0] bits; and "
            "D_null1 < D_null0 at EVERY evaluated P."),
        "D_null0": {"min": extremes["D_null0"]["min"],
                    "max": extremes["D_null0"]["max"],
                    "argmin": extremes["D_null0"]["min"],
                    "argmax": extremes["D_null0"]["max"],
                    "min_ge_11_9": extremes["D_null0"]["min"]["value"] >= 11.9,
                    "max_le_14_2": extremes["D_null0"]["max"]["value"] <= 14.2,
                    "min_ge_1_0_bit": extremes["D_null0"]["min"]["value"] >= 1.0,
                    "strictly_increasing_in_P_per_law": mono_in_P},
        "D_null1": {"min": extremes["D_null1"]["min"],
                    "max": extremes["D_null1"]["max"],
                    "argmin": extremes["D_null1"]["min"],
                    "argmax": extremes["D_null1"]["max"],
                    "at_P_256_per_law": d1_at_256,
                    "at_P_256_in_1_5_to_4_0": all(1.5 <= v <= 4.0
                                                  for v in d1_at_256.values())},
        "ordering_D_null1_lt_D_null0_everywhere": ordering_ok,
        "ordering_violations": ordering_viol[:20],
        "surface_identity_check": {
            "note": ("D_null on the margin surface must equal |E_law(P) - E_null(P)| "
                     "exactly, since the two arms differ only in E; verified on a "
                     "3-P x full-theta subgrid of actual Delta evaluations"),
            "n_cells_checked": len(checks),
            "max_abs_identity_error_D_null0": max_id0,
            "max_abs_identity_error_D_null1": max_id1,
        },
        "per_P_profile_D_null0": prof["D_null0"],
        "per_P_profile_D_null1": prof["D_null1"],
        "locus_displacement": {
            "n_pairs": len(disp),
            "n_numeric_pairs": len(numeric_disp),
            "max_abs_displacement": max(numeric_disp) if numeric_disp else None,
            "min_abs_displacement": min(numeric_disp) if numeric_disp else None,
            "categorical_transition_counts": _counter(
                [d.get("transition") for d in disp if d["kind"] != "numeric"]),
            "rows": disp,
        },
    }


def _counter(seq):
    out = {}
    for s in seq:
        if s is None:
            continue
        out[s] = out.get(s, 0) + 1
    return out


def monotonicity_report(mono5):
    # MONO-1
    seg_records = []
    fails = []
    for P in [float(p) for p in T2_P]:
        lm = L_mem(P)
        for law in LAWS_MAIN:
            for S in S_STRUCT:
                for A in A_AES:
                    for c in C_OVERHEAD:
                        for mc in MC_LIST:
                            for i in range(len(W_GRID) - 1):
                                w0, w1 = W_GRID[i], W_GRID[i + 1]
                                d0, u0 = delta(P, w0, law, S, A, c, mc)
                                d1, u1 = delta(P, w1, law, S, A, c, mc)
                                if u0 or u1:
                                    continue
                                slope = (d1 - d0) / (w1 - w0)
                                if mc == "MC_P13":
                                    expected = (0.5 * (min(w1, lm) - min(w0, lm))
                                                / (w1 - w0))
                                    kind = ("below_clamp" if w1 <= lm else
                                            ("at_or_above_clamp" if w0 >= lm
                                             else "straddles_clamp"))
                                else:
                                    expected = -0.5
                                    kind = "feasible_feasible"
                                ok = abs(slope - expected) <= 1e-6
                                rec = {"log2_p": P, "law": law, "S": S, "A": A,
                                       "c": c, "MC": mc, "w_segment": [w0, w1],
                                       "segment_kind": kind,
                                       "measured_slope": slope,
                                       "expected_slope": expected,
                                       "abs_error": abs(slope - expected),
                                       "ok": ok}
                                if not ok:
                                    fails.append(rec)
                                seg_records.append(rec)
    pure = {}
    for r in seg_records:
        pure.setdefault((r["MC"], r["segment_kind"]), set()).add(round(r["measured_slope"], 12))
    agg = {}
    for r in seg_records:
        k = "%s|%s|log2p=%g|w=[%g,%g]" % (r["MC"], r["segment_kind"], r["log2_p"],
                                          r["w_segment"][0], r["w_segment"][1])
        a = agg.setdefault(k, {"n": 0, "min_measured_slope": None,
                               "max_measured_slope": None,
                               "expected_slope": r["expected_slope"],
                               "max_abs_error": 0.0})
        a["n"] += 1
        a["min_measured_slope"] = (r["measured_slope"] if a["min_measured_slope"] is None
                                   else min(a["min_measured_slope"], r["measured_slope"]))
        a["max_measured_slope"] = (r["measured_slope"] if a["max_measured_slope"] is None
                                   else max(a["max_measured_slope"], r["measured_slope"]))
        a["max_abs_error"] = max(a["max_abs_error"], r["abs_error"])
    mono1 = {
        "id": "MONO-1", "blocking": True, "tolerance": 1e-6,
        "statement": ("d(Delta)/d(log2 w) = +0.5 exactly under MC_P13 while "
                      "log2 w < L_mem(P) and 0 exactly at or above it; -0.5 "
                      "exactly under MC_VOW wherever the assessed method is "
                      "feasible."),
        "method": ("finite difference on the 13 adjacent segments of the declared "
                   "14-value w grid, at every committed P row and every theta; "
                   "segments that straddle the clamp are reported separately and "
                   "compared against the clamp-implied slope"),
        "n_segments_measured": len(seg_records),
        "distinct_measured_slopes_by_segment_kind": {
            "%s|%s" % k: sorted(v) for k, v in pure.items()},
        "measured_slopes_by_P_and_segment": agg,
        "n_failures": len(fails),
        "failures": fails[:20],
        "verdict": "PASS" if not fails else "FAIL",
        "pass": not fails,
    }

    # MONO-2: locate the kink by bisecting the measured slope of Delta
    h = 1e-11
    kinks = []
    for P in [float(p) for p in T2_P]:
        lo, hi = 0.0, 400.0
        law, S, A, c, mc = "L1", 0.0, 0.0, 0.0, "MC_P13"

        def slope_at(w):
            a, _ = delta(P, w, law, S, A, c, mc)
            b, _ = delta(P, w - h, law, S, A, c, mc)
            return (a - b) / h

        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if slope_at(mid) > 0.25:
                lo = mid
            else:
                hi = mid
        kink = 0.5 * (lo + hi)
        kinks.append({"log2_p": P, "measured_kink_log2_w": kink,
                      "committed_L_mem": L_mem(P),
                      "abs_error": abs(kink - L_mem(P)),
                      "within_1e-9": abs(kink - L_mem(P)) <= 1e-9})
    mono2 = {
        "id": "MONO-2", "blocking": True, "tolerance": 1e-9,
        "statement": ("The kink in Delta versus log2 w under MC_P13 sits at "
                      "exactly L_mem(P) for the five committed rows."),
        "method": ("bisection on a backward finite-difference slope of the "
                   "assembled Delta (h = 1e-11), 200 iterations; this measures "
                   "the kink of the assembled function rather than reading the "
                   "min() clamp"),
        "kinks": kinks,
        "verdict": "PASS" if all(k["within_1e-9"] for k in kinks) else "FAIL",
        "pass": all(k["within_1e-9"] for k in kinks),
    }
    return_kinks = [k["measured_kink_log2_w"] for k in kinks]

    return {"MONO-1": mono1, "MONO-2": mono2,
            "measured_kink_locations": return_kinks,
            "MONO-5": mono5,
            "_placeholder": None}


def mono3_and_4(grids, mono):
    rows = grids["main"]
    # MONO-3
    thetas = {}
    for r in rows:
        key = (r["law"], r["S"], r["A"], r["c"], r["MC"])
        thetas.setdefault(key, []).append(r)
    results = []
    fails = []
    n_not_eval = 0
    for key, rs in thetas.items():
        rs = sorted(rs, key=lambda r: r["log2_w"])
        pts = [(r["log2_w"], r["p_star"]) for r in rs if r["outcome"] == "NUMERIC"]
        entry = {"law": key[0], "S": key[1], "A": key[2], "c": key[3],
                 "MC": key[4], "n_numeric_loci": len(pts)}
        if len(pts) < 2:
            entry["verdict"] = "NOT_EVALUABLE(n = %d)" % len(pts)
            n_not_eval += 1
        else:
            diffs = [pts[i + 1][1] - pts[i][1] for i in range(len(pts) - 1)]
            if key[4] == "MC_P13":
                ok = all(d <= 1e-12 for d in diffs)
                entry["required_direction"] = "non-increasing in log2 w"
            else:
                ok = all(d >= -1e-12 for d in diffs)
                entry["required_direction"] = "non-decreasing in log2 w"
            entry["p_star_vs_w"] = pts
            entry["consecutive_differences"] = diffs
            entry["verdict"] = "PASS" if ok else "FAIL"
            if not ok:
                fails.append(entry)
        results.append(entry)
    mono3 = {
        "id": "MONO-3", "blocking": False,
        "statement": ("p*(w) is non-increasing in w under MC_P13 and "
                      "non-decreasing under MC_VOW, wherever at least two "
                      "numeric loci exist within one theta; otherwise "
                      "NOT_EVALUABLE(n = count), NEVER pass."),
        "n_thetas": len(results),
        "n_not_evaluable": n_not_eval,
        "n_evaluable": len(results) - n_not_eval,
        "n_failures": len(fails),
        "failures": fails[:20],
        "verdict": ("NOT_EVALUABLE(n = 0 evaluable thetas)"
                    if len(results) - n_not_eval == 0
                    else ("PASS" if not fails else "FAIL")),
        "per_theta": results,
    }

    # MONO-4
    best = None
    n_ge_half = 0
    n_cmp = 0
    for law in LAWS_MAIN:
        for S in S_STRUCT:
            for c in C_OVERHEAD:
                for w in W_GRID:
                    if w < 10:
                        continue
                    for P in SCAN_PS:
                        a, ua = delta(P, w, law, S, 0.0, c, "MC_P13")
                        b, ub = delta(P, w, law, S, 0.0, c, "MC_VOW")
                        if ua or ub:
                            continue
                        n_cmp += 1
                        d = abs(a - b)
                        if d >= 0.5:
                            n_ge_half += 1
                        if best is None or d > best["abs_difference"]:
                            best = {"abs_difference": d, "law": law, "S": S,
                                    "c": c, "log2_w": w, "log2_p": P,
                                    "Delta_MC_P13": a, "Delta_MC_VOW": b}
    mono4 = {
        "id": "MONO-4", "blocking": True,
        "statement": ("MC_P13 and MC_VOW differ by at least 0.5 bits in Delta at "
                      "some evaluated cell with log2 w >= 10."),
        "n_comparable_cells": n_cmp,
        "n_cells_differing_by_at_least_0_5_bits": n_ge_half,
        "max_difference_cell": best,
        "verdict": "PASS" if (best and best["abs_difference"] >= 0.5) else "FAIL",
        "pass": bool(best and best["abs_difference"] >= 0.5),
    }
    mono.pop("_placeholder", None)
    mono["MONO-3"] = mono3
    mono["MONO-4"] = mono4
    mono["blocking_limbs_verdict"] = {
        "MONO-1": mono["MONO-1"]["verdict"], "MONO-2": mono["MONO-2"]["verdict"],
        "MONO-4": mono4["verdict"], "MONO-5": mono["MONO-5"]["verdict"]}
    mono["MONO-3_verdict"] = mono3["verdict"]
    return mono


def scope_report():
    scope = {"axes_are_reported_separately": True,
             "mandatory_qualifier": (
                 "Every cost number below is conditional on Wesolowski's "
                 "Heuristic 1 (unvalidated in this corpus) and on HEUR-XO-1..3, "
                 "and is stated together with the memory requirement it needs: "
                 "2^{L_mem} table entries at the same P. Nothing here is an "
                 "executed attack and nothing here is a security claim."),
             "forbidden_sentence_note": (
                 "The unqualified sentence about NIST-III/V retaining margin is "
                 "not used anywhere in this package; every use names its axis.")}

    a_rows, b_rows, c_rows = [], [], []
    levels = [("NIST-I", 256.0, 128.0), ("NIST-III", 384.0, 192.0),
              ("NIST-V", 512.0, 256.0)]
    for label, P, target in levels:
        for law in LAWS_MAIN:
            for S in S_STRUCT:
                for c in C_OVERHEAD:
                    taf, _ = T_A_full(P, law, S, 0.0, c)
                    a_rows.append({
                        "level": label, "log2_p": P, "law": law, "S": S, "c": c,
                        "A": 0.0, "unit": "log2 F_{p^2}-operations",
                        "T_A_unbounded_memory_MC_P13":
                            taf - 0.5 * L_mem(P),
                        "T_B_matched_baseline": P / 2.0 + LOG2_K_DG,
                        "advantage_bits_MC_P13_at_w_ge_L_mem":
                            (P / 2.0 + LOG2_K_DG) - (taf - 0.5 * L_mem(P)),
                        "advantage_bits_no_memory_discount":
                            (P / 2.0 + LOG2_K_DG) - taf,
                        "required_memory_log2_entries": L_mem(P),
                        "stamps": stamps_for(P)})
                    if c == 0.0 and S == 0.0:
                        b_rows.append({
                            "level": label, "log2_p": P, "law": law, "S": S,
                            "c": c, "A": 0.0,
                            "target_bits": target,
                            "T_A_full_unit_F_p2_ops": taf,
                            "gap_below_target_bits": target - taf,
                            "required_memory_log2_entries": L_mem(P),
                            "stamps": stamps_for(P)})
        for bpe in BYTES_PER_ENTRY:
            need = L_mem(P) + math.log2(bpe)
            c_rows.append({
                "level": label, "log2_p": P, "bytes_per_entry": bpe,
                "required_memory_log2_bytes": need,
                "global_storage_log2_bytes": GLOBAL_STORAGE_LOG2_BYTES,
                "excess_over_global_storage_log2": need - GLOBAL_STORAGE_LOG2_BYTES,
                "feasible_against_committed_global_storage":
                    need <= GLOBAL_STORAGE_LOG2_BYTES,
                "stamps": stamps_for(P)})

    def ordering(vals):
        return all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))

    a_ref = [r["advantage_bits_no_memory_discount"] for r in a_rows
             if r["law"] == "L1" and r["S"] == 0.0 and r["c"] == 0.0]
    b_ref = [r["gap_below_target_bits"] for r in b_rows if r["law"] == "L1"]
    c_ref = [r["excess_over_global_storage_log2"] for r in c_rows
             if r["bytes_per_entry"] == 64]

    scope["SCOPE-A_advantage_over_matched_baseline"] = {
        "axis": "advantage over the matched Delfs-Galbraith / previous-methods baseline",
        "preregistered_prediction": "advantage INCREASES with NIST level",
        "reference_scenario": "law L1, S = 0, A = 0, c = 0, log2 k_DG = 0",
        "reference_values_bits_no_memory_discount": a_ref,
        "reference_increases_with_level": ordering(a_ref),
        "rows": a_rows,
    }
    scope["SCOPE-B_gap_below_the_levels_own_target"] = {
        "axis": "assessed cost against the level's own classical target",
        "preregistered_prediction": "gap below target INCREASES with level",
        "frozen_reference": FROZEN_REF["gap_below_target_S0_A0_c0"],
        "reference_values_bits": b_ref,
        "reference_residuals_vs_frozen_bits": [
            b_ref[i] - list(FROZEN_REF["gap_below_target_S0_A0_c0"].values())[i]
            for i in range(3)],
        "reference_increases_with_level": ordering(b_ref),
        "note": ("On this axis NIST-III/V are not safer than NIST-I in the "
                 "unbounded-memory model; each figure requires 2^{L_mem} table "
                 "entries and is conditional on Heuristic 1."),
        "rows": b_rows,
    }
    scope["SCOPE-C_memory_feasibility"] = {
        "axis": "required table memory against the committed global-storage figure",
        "preregistered_prediction": ("infeasible at all three levels, with "
                                     "infeasibility INCREASING with level"),
        "frozen_reference_at_64B": FROZEN_REF["memory_bytes_log2_at_64B"],
        "reference_excess_bits_at_64B": c_ref,
        "reference_increases_with_level": ordering(c_ref),
        "all_levels_infeasible": all(not r["feasible_against_committed_global_storage"]
                                     for r in c_rows),
        "rows": c_rows,
    }
    return scope


def sensitivity_report(grids):
    # L5
    l5 = []
    for P in [float(p) for p in T2_P]:
        e5, _ = E_law("L5", P)
        e4, _ = E_law("L4", P)
        l5.append({"log2_p": P, "E_L5": e5, "E_L4": e4,
                   "E_L5_minus_E_L4_bits": e5 - e4,
                   "stamps": stamps_for(P)})
    l5_frozen = {"E_L5_at_256_frozen_reference": FROZEN_REF["E_at_256"]["L5"],
                 "E_L5_at_256_measured": E_law("L5", 256.0)[0]}
    l5_frozen["residual_bits"] = (l5_frozen["E_L5_at_256_measured"]
                                  - l5_frozen["E_L5_at_256_frozen_reference"])

    # induced locus displacement L5 vs L4
    l5rows = {cellkey(r): r for r in grids["l5"]}
    l4rows = {cellkey(r): r for r in grids["main"] if r["law"] == "L4"}
    disp = []
    for k, r4 in l4rows.items():
        r5 = l5rows[k]
        entry = {"S": r4["S"], "A": r4["A"], "c": r4["c"], "MC": r4["MC"],
                 "log2_w": r4["log2_w"], "L4_outcome": r4["outcome"],
                 "L5_outcome": r5["outcome"], "L4_p_star": r4["p_star"],
                 "L5_p_star": r5["p_star"]}
        if r4["p_star"] is not None and r5["p_star"] is not None:
            entry["abs_displacement_log2p"] = abs(r5["p_star"] - r4["p_star"])
        else:
            entry["abs_displacement_log2p"] = None
            entry["transition"] = "%s -> %s" % (r4["outcome"], r5["outcome"])
        disp.append(entry)
    numd = [d["abs_displacement_log2p"] for d in disp
            if d["abs_displacement_log2p"] is not None]

    # log2 k_DG sensitivity: d(p*)/d(log2 k_DG) at every w
    ksens = []
    for w in W_GRID:
        rows = [r for r in grids["main"] if r["log2_w"] == w and r["A"] == 0.0]
        per = []
        for r in rows:
            ks = r.get("p_star_vs_log2_k_DG")
            if not ks:
                continue
            pts = [(k, ks[repr(k)]) for k in LOG2_K_DG_SENS if ks[repr(k)] is not None]
            if len(pts) >= 2:
                slope = ((pts[-1][1] - pts[0][1]) / (pts[-1][0] - pts[0][0]))
            else:
                slope = None
            per.append({"law": r["law"], "S": r["S"], "c": r["c"], "MC": r["MC"],
                        "p_star_vs_log2_k_DG": {str(k): v for k, v in
                                                zip(LOG2_K_DG_SENS,
                                                    [ks[repr(k)] for k in LOG2_K_DG_SENS])},
                        "n_numeric": len(pts),
                        "d_p_star_d_log2_k_DG": slope,
                        "note": (None if len(pts) >= 2 else
                                 "NOT_EVALUABLE(n = %d numeric loci)" % len(pts))})
        slopes = [p["d_p_star_d_log2_k_DG"] for p in per
                  if p["d_p_star_d_log2_k_DG"] is not None]
        ksens.append({"log2_w": w, "n_theta": len(per),
                      "n_with_slope": len(slopes),
                      "min_slope": min(slopes) if slopes else None,
                      "max_slope": max(slopes) if slopes else None,
                      "per_theta": per})

    # adversarial corner
    e_at_256 = {law: E_law(law, 256.0)[0] for law in LAWS_MAIN}
    smallest_law = min(e_at_256, key=lambda k: e_at_256[k])
    corner_rows = []
    for w in W_GRID:
        r = solve_cell(smallest_law, 0.0, -1.736966, 0.0, "MC_P13", w)
        r.update({"log2_w": w, "law": smallest_law, "S": 0.0, "A": -1.736966,
                  "c": 0.0, "MC": "MC_P13", "log2_k_DG": 0.0,
                  "stamps": stamps_for(r.get("p_star"))})
        corner_rows.append(r)
    corner = {
        "id": "ADVERSARIAL-CORNER",
        "definition": ("per-entry law giving the smallest E at P = 256, S = 0, "
                       "A = -1.736966 (pure RAM, the attacker-favourable corner "
                       "that OBJ-6 flags as most attacker-favorable), c = 0.0, "
                       "MC_P13, log2 k_DG = 0"),
        "law_with_smallest_E_at_256": smallest_law,
        "E_at_256_per_law": e_at_256,
        "rows": corner_rows,
        "T_A_full_at_256": T_A_full(256.0, smallest_law, 0.0, -1.736966, 0.0)[0],
        "required_memory_log2_entries_at_256": L_mem(256.0),
    }

    # SANITY-1
    sanity_rows = []
    for P in [float(p) for p in T2_P]:
        lm = L_mem(P)
        below_w = min(20.0, lm / 2.0)
        above_w = lm + 10.0
        h = 1e-6
        d_below = ((T_A(P, below_w + h, "L1", 0.0, 0.0, 0.0, "MC_P13")[0]
                    - T_A(P, below_w, "L1", 0.0, 0.0, 0.0, "MC_P13")[0]) / h)
        d_above = ((T_A(P, above_w + h, "L1", 0.0, 0.0, 0.0, "MC_P13")[0]
                    - T_A(P, above_w, "L1", 0.0, 0.0, 0.0, "MC_P13")[0]) / h)
        t_small = T_A(P, 20.0, "L1", 0.0, 0.0, 0.0, "MC_P13")[0]
        t_full = T_A(P, lm, "L1", 0.0, 0.0, 0.0, "MC_P13")[0]
        sanity_rows.append({
            "log2_p": P, "L_mem": lm,
            "dT_A_dlog2w_below_clamp": d_below,
            "dT_A_dlog2w_above_clamp": d_above,
            "T_A_at_log2w_20": t_small,
            "T_A_at_log2w_L_mem": t_full,
            "cost_increase_when_memory_reduced_from_L_mem_to_2^20_bits":
                t_small - t_full,
            "max_discount_bits_0_5_times_L_mem": 0.5 * lm,
            "reducing_memory_makes_assessed_method_cheaper": (t_small < t_full),
            "stamps": stamps_for(P)})
    pathology = any(r["reducing_memory_makes_assessed_method_cheaper"]
                    for r in sanity_rows)
    sanity = {
        "id": "SANITY-1-MODEL-COHERENCE",
        "audit_question": ("does MC_P13 imply that REDUCING memory below L_mem(P) "
                           "makes the assessed method CHEAPER?"),
        "measured_answer": ("NO under the committed formula: dT_A/d(log2 w) is "
                            "negative below the clamp, so cost FALLS as memory "
                            "RISES and RISES as memory falls."
                            if not pathology else
                            "YES -- see MODEL_PATHOLOGY below"),
        "sign_of_dT_A_dlog2w_below_clamp": "negative",
        "convention_reading": ("the committed MC_P13 formula gives the vOW memory "
                               "discount to the ASSESSED METHOD; the discount "
                               "shrinks with memory and is clamped at L_mem(P)"),
        "MODEL_PATHOLOGY": ("memory_discount_direction" if pathology else None),
        "rows": sanity_rows,
        "recorded_discrepancy": (
            "H-SSI-7fe2bf HEUR-XO-3 supporting_results states that MC-P13 'as "
            "written it makes the assessed method CHEAPER as memory shrinks below "
            "M'. The formula as committed in specification.yaml "
            "(T_A = ... - 0.5*min(log2 w, L_mem)) and in cost_model.py line 236 "
            "(T_w_vOW = T_full / sqrt(min(w, M))) yields the OPPOSITE direction: "
            "cost rises as memory shrinks. This run reports the measured sign and "
            "does not resolve the discrepancy; it is recorded for the Coordinator "
            "and reviewers."),
    }

    # transcription-consistency readout
    trans = {
        "abs_a1_minus_16_2": abs(COEF["a1"] - 16.2),
        "abs_a4_minus_16_2": abs(COEF["a4"] - 16.2),
        "a3P_plus_b3_at_256": COEF["a3"] * 256.0 + COEF["b3"],
        "a2P_at_256": 16.2 * 256.0,
        "abs_difference_at_256": abs(COEF["a3"] * 256.0 + COEF["b3"] - 16.2 * 256.0),
        "abs_difference_at_256_bits": abs(
            math.log2(COEF["a3"] * 256.0 + COEF["b3"]) - math.log2(16.2 * 256.0)),
    }

    return {
        "L5_extrapolation_sensitivity": {
            "status": ("NOT a member of the main scenario band and NOT part of "
                       "the reproduction gate; reported separately"),
            "alpha_primary": 1.1321,
            "per_committed_row": l5,
            "frozen_reference_check": l5_frozen,
            "induced_locus_displacement": {
                "n_pairs": len(disp),
                "n_numeric": len(numd),
                "min_abs_displacement_log2p": min(numd) if numd else None,
                "max_abs_displacement_log2p": max(numd) if numd else None,
                "categorical_transition_counts": _counter(
                    [d.get("transition") for d in disp
                     if d["abs_displacement_log2p"] is None]),
                "rows": disp},
        },
        "log2_k_DG_sensitivity": {
            "ratio_form_note": ("Delta(log2_k_DG) = Delta(0) + log2_k_DG; the "
                                "ratio form is primary and k-free, the absolute "
                                "locus is emitted at log2 k_DG = 0 only, with "
                                "independently_transcribed: false (HEUR-XO-2)"),
            "evaluated_at": LOG2_K_DG_SENS,
            "per_log2_w": ksens},
        "adversarial_corner": corner,
        "SANITY-1": sanity,
        "transcription_consistency_readout": trans,
    }


def undefined_segments(grids):
    entries = []
    for arm in ("main", "null", "l5"):
        for r in grids[arm]:
            guards = ["fit_window_extrapolation"]
            responsible = ["T1 fit window log2 p in [9, 40] carried to [256, 768] "
                           "under HEUR-XO-1"]
            if r["outcome"] == "INFEASIBLE_AT_MEMORY":
                guards.append("INFEASIBLE_AT_MEMORY")
                responsible.append("T2 L_mem column vs the declared log2 w grid")
            if r["mask_reasons"]:
                for m in r["mask_reasons"]:
                    if m not in guards:
                        guards.append(m)
                        responsible.append("T2 L_mem column (MC_VOW feasibility mask)"
                                           if m == "INFEASIBLE_AT_MEMORY"
                                           else "T1 OLS law L3 (a3*P + b3 <= 0)")
            if r["outcome"] == "NUMERIC" and r["stamps"].get("bracketing_rows"):
                guards.append("interpolated_between_committed_rows")
                responsible.append("T2 rows %s" % (r["stamps"]["bracketing_rows"],))
            entries.append({
                "arm": arm, "law": r["law"], "S": r["S"], "A": r["A"],
                "c": r["c"], "MC": r["MC"], "log2_w": r["log2_w"],
                "outcome": r["outcome"],
                "guards": guards,
                "extrapolation_ratio": r["stamps"]["extrapolation_ratio"],
                "extrapolation_ratio_window": [P_LO / 40.0, P_HI / 40.0],
                "responsible_inputs": responsible,
            })
    counts = _counter([g for e in entries for g in e["guards"]])
    l3_undef = [e for e in entries if any("L3_undefined" in g for g in e["guards"])]
    return {
        "summary": {
            "n_entries": len(entries),
            "guard_counts": counts,
            "empty_list_would_be_a_defect": True,
            "is_empty": len(entries) == 0,
            "universal_guard": ("every cell carries fit_window_extrapolation: true "
                                "with extrapolation_ratio = P/40 in [6.4, 19.2]"),
            "n_L3_undefined_cells": len(l3_undef),
            "L3_design_time_check": ("a3*P + b3 > 0 on [256, 768]; the design-time "
                                     "note says this guard does not fire"),
        },
        "entries": entries,
    }


def tail_checks(grids):
    tr = grids["min_abs_delta"]
    rows = grids["main"]
    endpoints = [{"law": r["law"], "S": r["S"], "A": r["A"], "c": r["c"],
                  "MC": r["MC"], "log2_w": r["log2_w"],
                  "delta_at_P_lo": r["delta_at_P_lo"],
                  "delta_at_P_hi": r["delta_at_P_hi"],
                  "outcome": r["outcome"]} for r in rows]
    nc = [e for e in endpoints if e["outcome"] == "NO_CROSSOVER_IN_WINDOW"]
    spreads = [abs(e["delta_at_P_hi"] - e["delta_at_P_lo"]) for e in nc]
    knife = [{"law": r["law"], "S": r["S"], "A": r["A"], "c": r["c"],
              "MC": r["MC"], "log2_w": r["log2_w"], "p_star": r["p_star"],
              "bracket": r.get("knife_edge_bracket")}
             for r in rows if r["outcome"] == "NUMERIC"]
    per_conv = {}
    for mc in MC_LIST:
        per_conv[mc] = _counter([r["outcome"] for r in rows if r["MC"] == mc])
    return {
        "endpoint_deltas_reported_for_every_cell": True,
        "n_cells_with_endpoint_deltas": len(endpoints),
        "no_crossover_endpoint_spread_bits": {
            "n": len(nc),
            "min": min(spreads) if spreads else None,
            "max": max(spreads) if spreads else None,
            "mean": statistics.fmean(spreads) if spreads else None},
        "smallest_abs_delta_in_grid": {
            "value_bits": tr["min_abs"], "cell": tr["cell"],
            "knife_edge_rule": ("a minimum below 1 bit at a memory-feasible cell "
                                "means the comparison is knife-edge there; the "
                                "locus in that neighbourhood is reported as the "
                                "unit-grid bracket containing the root, not as a "
                                "bare point"),
            "below_1_bit": tr["min_abs"] < 1.0},
        "knife_edge_brackets_for_numeric_loci": knife[:200],
        "n_numeric_loci_with_brackets": len(knife),
        "categorical_label_counts_per_convention": per_conv,
        "decisive_conventions": {
            mc: (list(per_conv[mc])[0] if len(per_conv[mc]) == 1 else None)
            for mc in MC_LIST},
    }


if __name__ == "__main__":
    sys.exit(main())
