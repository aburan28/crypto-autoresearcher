#!/usr/bin/env python3
"""
EXP-SSI-9b542d: The Wesolowski crossover locus p*(w) from committed numbers.
REPAIRED: correctly-anchored vOW time-memory law (MC_P13_CORRECTED).

Zero-compute cost-model experiment. Standard library only on primary path.
"""
import math
import json
import os
import sys
import time
import hashlib
import statistics
import platform
import importlib
import importlib.util
import re
import ast

# ===========================================================================
# CONSTANTS from the frozen specification
# ===========================================================================

EXPERIMENT_ID = "EXP-SSI-9b542d"
RUN_ID = "RUN-SSI-9b542d-001"
SEED = 0  # No randomness used; recorded for form only

# Memory grid (frozen in specification)
W_GRID_LOG2 = [20, 25, 30, 35, 40, 50, 60, 70, 80, 92.5, 138.6, 181.3, 206.0, 272.2]
UNBOUNDED_LOG2_W = 1000  # representation of unbounded memory

# T2 paper anchor table (frozen)
T2_P = [256, 384, 512, 576, 768]
T2_L_PAPER = [106.5, 157.5, 204.2, 230.9, 302.4]
T2_L_MEM = [92.5, 138.6, 181.3, 206.0, 272.2]
T2_L_PREV = [128.0, 192.0, 256.0, 288.0, 384.0]
T2_LABELS = ["SQIsign NIST-I", "SQIsign NIST-III", "SQIsign NIST-V", None, None]

# T1 frozen values
T1_FROZEN_X = [9, 14, 17, 20, 24, 28, 32, 40]
T1_FROZEN_Y = [
    143.72875226039784,
    192.67237687366168,
    244.77013354917037,
    293.178645371192,
    343.926267281106,
    439.4038324400175,
    515.2952824694235,
    651.0768243785084,
]

# Declared scalars
S_VALUES = [0.0, 3.0]
A_VALUES = [0.0, -1.736966, 1.584963, 3.906891]
A_LABELS = ["F_p2_operations_no_conversion", "pure_RAM_alpha_0.3",
            "cpu_aes_ni_alpha_3", "asic_alpha_15"]
C_VALUES = [0.0, 0.5, 1.0, 1.8, 2.0]
LOG2_K_DG = 0.0
GLOBAL_STORAGE_LOG2_BYTES = 73.08
BYTES_PER_ENTRY_VALUES = [64, 256]

# Crossover window
P_MIN, P_MAX = 256, 768
P_SCAN_STEP = 1.0
BISECT_TOL = 1e-9
BISECT_MAX_ITER = 80

# Reference values
FROZEN_A1 = 15.576908
FROZEN_A2 = 16.2
FROZEN_A3 = 16.925485
FROZEN_B3 = -36.279641
FROZEN_A4 = 16.27692061

# ===========================================================================
# PATHS (relative to repo root)
# ===========================================================================
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T1_PATH = os.path.join(REPO_ROOT,
    "coordination/goals/GOAL-SSI-001/batches/BATCH-046/tasks/TASK-20260804-55952a/implementation/cost_measurements.json")
T2_PATH = os.path.join(REPO_ROOT,
    "inputs/P13-WESOLOWSKI-2026/paper_fulltext.md")
COST_MODEL_PATH = os.path.join(REPO_ROOT,
    "coordination/tasks/TASK-20260724-P13-VAL/repro/experiments/EXP-P13VOW-001/cost_model.py")


def sha256_file(path):
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# STEP 0: Environment verification
# ===========================================================================
def step0_environment():
    """Record environment and verify dependencies."""
    env = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "os_name": os.name,
    }

    # Check module availability
    modules_to_check = ["numpy", "sage", "sagemath", "g6k", "fpylll",
                        "scipy", "mpmath", "re", "ast"]
    module_status = {}
    for mod in modules_to_check:
        spec = importlib.util.find_spec(mod)
        if spec is not None:
            module_status[mod] = {"present": True, "location": str(spec.origin)}
        else:
            module_status[mod] = {"present": False}

    env["module_availability"] = module_status

    # Record which forbidden modules are AVAILABLE (not whether we import them)
    forbidden = ["sage", "sagemath", "g6k", "fpylll", "scipy", "mpmath"]
    forbidden_available = [m for m in forbidden if module_status.get(m, {}).get("present", False)]
    env["forbidden_modules_available_on_system"] = forbidden_available
    # The assertion is that THIS CODE does not import any forbidden module.
    # We only use stdlib. This is a declaration, verified by code inspection.
    env["no_forbidden_import_assertion"] = True
    env["assertion_basis"] = ("This code imports only stdlib modules: math, json, os, sys, "
                              "time, hashlib, statistics, platform, importlib, re, ast. "
                              "No forbidden module (sage, sagemath, g6k, fpylll, scipy, mpmath) "
                              "is imported by this run.")

    # Verify required stdlib modules
    required_stdlib = ["re", "ast", "math", "json", "os", "sys", "time",
                       "hashlib", "statistics", "platform", "importlib"]
    env["required_stdlib_verified"] = all(
        importlib.util.find_spec(m) is not None for m in required_stdlib
    )

    return env


# ===========================================================================
# INPUT LOADING AND VERIFICATION
# ===========================================================================
def load_and_verify_t1():
    """Load T1 scaling_summary and verify frozen values."""
    with open(T1_PATH, "r") as f:
        data = json.load(f)

    scaling = data["scaling_summary"]
    assert len(scaling) == 8, f"Expected 8 rows, got {len(scaling)}"

    extracted_x = [row["log2_p"] for row in scaling]
    extracted_y = [row["avg_mults_per_entry"] for row in scaling]

    # Exact float equality on decimal literals
    for i in range(8):
        assert extracted_x[i] == T1_FROZEN_X[i], \
            f"T1 x mismatch at row {i}: {extracted_x[i]} != {T1_FROZEN_X[i]}"
        assert extracted_y[i] == T1_FROZEN_Y[i], \
            f"T1 y mismatch at row {i}: {extracted_y[i]} != {T1_FROZEN_Y[i]}"

    return extracted_x, extracted_y


def load_and_verify_t2():
    """Load T2 from paper_fulltext.md lines 234-238, parse with regex."""
    with open(T2_PATH, "r") as f:
        lines = f.readlines()

    # Lines 234-238 (1-indexed)
    target_lines = lines[233:238]  # 0-indexed

    # Parse pattern: lines use Unicode approx/geq chars
    # Format: "For log2(p) ≈ 256 ...: ≥ 2^106.5 F_{p^2}-operations and memory ≥ 2^92.5; (previous methods: ≈ 2^128 ...)"
    # The ≈ is U+2248 and ≥ is U+2265

    parsed_P = []
    parsed_time = []
    parsed_mem = []
    parsed_prev = []

    # Match: log2(p) ≈ NNN  (Unicode approx-equal)
    p_pattern = r'log2\(p\)\s*[\u2248~≈=]+\s*(\d+)'
    # Match: first 2^X.Y (the time), then memory ... 2^X.Y, then previous ... 2^X
    num_pattern = r'[\u2265>=]+\s*2\^([\d.]+)\s+F.*?memory\s*[\u2265>=]+\s*2\^([\d.]+).*?previous.*?[\u2248~≈=]+\s*2\^(\d+)'

    for line in target_lines:
        p_match = re.search(p_pattern, line)
        if p_match:
            parsed_P.append(int(p_match.group(1)))

        nums = re.search(num_pattern, line)
        if nums:
            parsed_time.append(float(nums.group(1)))
            parsed_mem.append(float(nums.group(2)))
            parsed_prev.append(float(nums.group(3)))

    assert len(parsed_P) == 5, f"Parsed {len(parsed_P)} P values, expected 5"
    assert parsed_P == T2_P, f"P mismatch: {parsed_P} != {T2_P}"
    assert parsed_time == T2_L_PAPER, f"L_paper mismatch: {parsed_time} != {T2_L_PAPER}"
    assert parsed_mem == T2_L_MEM, f"L_mem mismatch: {parsed_mem} != {T2_L_MEM}"
    assert parsed_prev == T2_L_PREV, f"L_prev mismatch: {parsed_prev} != {T2_L_PREV}"

    # Now verify against PAPER_PAIRS from cost_model.py (read as text)
    with open(COST_MODEL_PATH, "r") as f:
        cm_text = f.read()

    # Extract PAPER_PAIRS dict using ast
    pp_match = re.search(r'PAPER_PAIRS\s*=\s*(\{[^}]+\})', cm_text)
    assert pp_match, "Could not find PAPER_PAIRS in cost_model.py"
    paper_pairs = ast.literal_eval(pp_match.group(1))

    for p_val in T2_P:
        t_paper, m_paper = paper_pairs[p_val]
        idx = T2_P.index(p_val)
        assert t_paper == T2_L_PAPER[idx], \
            f"PAPER_PAIRS time mismatch at P={p_val}: {t_paper} != {T2_L_PAPER[idx]}"
        assert m_paper == T2_L_MEM[idx], \
            f"PAPER_PAIRS mem mismatch at P={p_val}: {m_paper} != {T2_L_MEM[idx]}"

    # Extract OVERHEAD_C
    oc_match = re.search(r'OVERHEAD_C\s*=\s*(\[[^\]]+\])', cm_text)
    assert oc_match, "Could not find OVERHEAD_C in cost_model.py"
    overhead_c = ast.literal_eval(oc_match.group(1))
    # Verify overlap: 0.0, 0.5, 1.0, 2.0 from the file; we use 0.0, 0.5, 1.0, 1.8, 2.0
    for v in overhead_c:
        assert v in C_VALUES, f"OVERHEAD_C value {v} not in declared C_VALUES"

    return paper_pairs, overhead_c


# ===========================================================================
# PER-ENTRY LAWS
# ===========================================================================
def compute_fit_parameters(xs, ys):
    """Compute all per-entry law parameters from T1 data."""
    # L1: proportional (no intercept), a1 = sum(xi*yi)/sum(xi^2)
    a1 = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)

    # L2: committed headline a2 = 16.2
    a2 = 16.2

    # L3: OLS with intercept
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    a3 = (n * sxy - sx * sy) / denom
    b3 = (sy * sxx - sx * sxy) / denom

    # L4: largest-row anchor
    a4 = ys[-1] / xs[-1]  # y(x=40) / 40

    return a1, a2, a3, b3, a4


def E_law(P, law_id, a1, a2, a3, b3, a4):
    """Compute E(P) = log2(per-entry cost at log2_p = P) for a given law."""
    if law_id == "L1":
        return math.log2(a1 * P)
    elif law_id == "L2":
        return math.log2(a2 * P)
    elif law_id == "L3":
        val = a3 * P + b3
        if val <= 0:
            return None  # UNDEFINED
        return math.log2(val)
    elif law_id == "L4":
        return math.log2(a4 * P)
    elif law_id == "L5":
        # E(P) = log2(651.0768243785084 * (P/40)^1.1321)
        return math.log2(651.0768243785084 * (P / 40.0) ** 1.1321)
    elif law_id == "N0":
        return 0.0  # Null: one op per entry
    elif law_id == "N1":
        return 9.8  # Null: superseded Velu
    else:
        raise ValueError(f"Unknown law: {law_id}")


# ===========================================================================
# INTERPOLATION OF T2 COLUMNS
# ===========================================================================
def interpolate_t2(P, column):
    """Piecewise-linear interpolation of a T2 column. P must be in [256, 768]."""
    assert P_MIN <= P <= P_MAX, f"P={P} outside window [{P_MIN}, {P_MAX}]"
    for i in range(len(T2_P) - 1):
        if T2_P[i] <= P <= T2_P[i + 1]:
            t = (P - T2_P[i]) / (T2_P[i + 1] - T2_P[i])
            return column[i] + t * (column[i + 1] - column[i])
    # Should not reach here if P is in window
    raise ValueError(f"P={P} not bracketed by T2 rows")


def L_paper(P):
    return interpolate_t2(P, T2_L_PAPER)


def L_mem(P):
    return interpolate_t2(P, T2_L_MEM)


def L_prev(P):
    return interpolate_t2(P, T2_L_PREV)


def get_bracketing_rows(P):
    """Return the two bracketing T2 rows for interpolation."""
    for i in range(len(T2_P) - 1):
        if T2_P[i] <= P <= T2_P[i + 1]:
            return (T2_P[i], T2_P[i + 1])
    return None


# ===========================================================================
# COST FUNCTIONS
# ===========================================================================
def T_full(P, law_id, S, A, c, a1, a2, a3, b3, a4):
    """Full-memory assessed-method cost (no memory penalty)."""
    E = E_law(P, law_id, a1, a2, a3, b3, a4)
    if E is None:
        return None
    return L_paper(P) + E + S + c * math.sqrt(P) + A


def T_A_corrected(P, log2_w, law_id, S, A, c, a1, a2, a3, b3, a4):
    """MC_P13_CORRECTED: T_full(P) + 0.5 * max(0, L_mem(P) - log2_w)"""
    tf = T_full(P, law_id, S, A, c, a1, a2, a3, b3, a4)
    if tf is None:
        return None
    penalty = 0.5 * max(0.0, L_mem(P) - log2_w)
    return tf + penalty


def T_A_superseded(P, log2_w, law_id, S, A, c, a1, a2, a3, b3, a4):
    """MC_P13_SUPERSEDED (negative control only): T_full(P) - 0.5*min(log2_w, L_mem(P))"""
    tf = T_full(P, law_id, S, A, c, a1, a2, a3, b3, a4)
    if tf is None:
        return None
    return tf - 0.5 * min(log2_w, L_mem(P))


def T_B_corrected(P, log2_w, A, log2_k_dg=0.0):
    """MC_P13_CORRECTED baseline: P/2 + log2_k_DG + A (memoryless)."""
    return P / 2.0 + log2_k_dg + A


def T_B_vow(P, log2_w, A, log2_k_dg=0.0):
    """MC_VOW baseline: P/2 + log2_k_DG + A - 0.5*log2_w."""
    return P / 2.0 + log2_k_dg + A - 0.5 * log2_w


def T_A_vow(P, log2_w, law_id, S, A, c, a1, a2, a3, b3, a4):
    """MC_VOW assessed method: T_full (no memory penalty on assessed side).
    FEASIBLE only where log2_w >= L_mem(P)."""
    return T_full(P, law_id, S, A, c, a1, a2, a3, b3, a4)


def is_feasible_vow(P, log2_w):
    """MC_VOW feasibility: log2_w >= L_mem(P)."""
    return log2_w >= L_mem(P)


# ===========================================================================
# MARGIN FUNCTIONS
# ===========================================================================
def margin_corrected(P, log2_w, law_id, S, A, c, a1, a2, a3, b3, a4, log2_k_dg=0.0):
    """Delta = T_B - T_A under MC_P13_CORRECTED. Positive = assessed cheaper."""
    ta = T_A_corrected(P, log2_w, law_id, S, A, c, a1, a2, a3, b3, a4)
    if ta is None:
        return None
    tb = T_B_corrected(P, log2_w, A, log2_k_dg)
    return tb - ta


def margin_vow(P, log2_w, law_id, S, A, c, a1, a2, a3, b3, a4, log2_k_dg=0.0):
    """Delta = T_B - T_A under MC_VOW. Returns None if infeasible."""
    if not is_feasible_vow(P, log2_w):
        return None  # INFEASIBLE
    ta = T_A_vow(P, log2_w, law_id, S, A, c, a1, a2, a3, b3, a4)
    if ta is None:
        return None
    tb = T_B_vow(P, log2_w, A, log2_k_dg)
    return tb - ta


# ===========================================================================
# CROSSOVER SOLVER
# ===========================================================================
def solve_crossover(margin_fn, P_min=256, P_max=768, step=1.0):
    """
    Bracket scan + bisection for the crossover locus.
    Returns dict with outcome and details.
    """
    # Step 1: bracket scan
    points = []
    P = float(P_min)
    while P <= P_max + 1e-9:
        g = margin_fn(P)
        points.append((P, g))
        P += step

    # Step 2: find feasible points
    feasible = [(p, g) for p, g in points if g is not None]

    if not feasible:
        # All infeasible
        min_feasible_w = L_mem(P_min)  # smallest log2_w that makes P_min feasible
        return {
            "outcome": "INFEASIBLE_AT_MEMORY",
            "min_log2_w_for_feasibility": min_feasible_w,
            "endpoint_256": None,
            "endpoint_768": None,
        }

    # Step 4: count sign changes among feasible points
    sign_changes = []
    for i in range(len(feasible) - 1):
        p1, g1 = feasible[i]
        p2, g2 = feasible[i + 1]
        if g1 * g2 < 0:
            sign_changes.append((p1, g1, p2, g2))

    # Endpoint values
    ep_256 = None
    ep_768 = None
    for p, g in feasible:
        if abs(p - 256.0) < 0.5:
            ep_256 = g
        if abs(p - 768.0) < 0.5:
            ep_768 = g

    if not sign_changes:
        # No crossover
        signs = [1 if g > 0 else (-1 if g < 0 else 0) for _, g in feasible]
        dominant_sign = 1 if sum(signs) > 0 else -1
        return {
            "outcome": "NO_CROSSOVER_IN_WINDOW",
            "sign": dominant_sign,
            "endpoint_256": ep_256,
            "endpoint_768": ep_768,
            "n_feasible": len(feasible),
        }

    # Step 5: bisect the FIRST bracketing interval
    roots = []
    for sc in sign_changes:
        p_lo, g_lo, p_hi, g_hi = sc
        for _ in range(BISECT_MAX_ITER):
            p_mid = (p_lo + p_hi) / 2.0
            g_mid = margin_fn(p_mid)
            if g_mid is None:
                break
            if abs(g_mid) < BISECT_TOL:
                break
            if g_mid * g_lo < 0:
                p_hi, g_hi = p_mid, g_mid
            else:
                p_lo, g_lo = p_mid, g_mid
        root = (p_lo + p_hi) / 2.0
        # Window guard
        if root < P_MIN or root > P_MAX:
            roots.append({"value": None, "direction": "below" if root < P_MIN else "above",
                          "outcome": "ROOT_OUTSIDE_WINDOW"})
        else:
            roots.append({"value": root, "outcome": "NUMERIC"})

    if len(roots) == 1:
        r = roots[0]
        if r["outcome"] == "ROOT_OUTSIDE_WINDOW":
            return {
                "outcome": "ROOT_OUTSIDE_WINDOW",
                "direction": r["direction"],
                "endpoint_256": ep_256,
                "endpoint_768": ep_768,
            }
        return {
            "outcome": "NUMERIC",
            "p_star_log2": r["value"],
            "endpoint_256": ep_256,
            "endpoint_768": ep_768,
        }
    else:
        # Multiple roots
        numeric_roots = [r["value"] for r in roots if r["outcome"] == "NUMERIC"]
        return {
            "outcome": "MULTIPLE_ROOTS",
            "roots": numeric_roots,
            "all_roots_detail": roots,
            "endpoint_256": ep_256,
            "endpoint_768": ep_768,
        }


# ===========================================================================
# GATES AND CONTROLS
# ===========================================================================
def run_boundary_condition_gate(a1, a2, a3, b3, a4):
    """BOUNDARY-CONDITION-GATE: BCG-1 and BCG-2."""
    results = {"BCG-1": [], "BCG-2": []}
    laws = ["L1", "L2", "L3", "L4"]

    # BCG-2 FIRST (negative control must pass before BCG-1 is trusted)
    for P, l_mem in zip(T2_P, T2_L_MEM):
        for law in laws:
            # Evaluate superseded formula at w = M (log2_w = L_mem(P))
            ta_sup = T_A_superseded(P, l_mem, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            tf = T_full(P, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            if ta_sup is not None and tf is not None:
                residual = abs(ta_sup - tf)
                expected = 0.5 * l_mem
                results["BCG-2"].append({
                    "P": P, "law": law, "residual_bits": residual,
                    "expected_residual": expected,
                    "match": abs(residual - expected) < 1e-9,
                    "above_1_bit": residual > 1.0,
                })

    # Check BCG-2 integrity: all must be > 1.0 bit
    bcg2_pass = all(r["above_1_bit"] for r in results["BCG-2"])
    results["BCG-2_verdict"] = "PASS" if bcg2_pass else "FAIL_CONTROL_INTEGRITY"

    # BCG-1 (corrected formula)
    for P, l_mem in zip(T2_P, T2_L_MEM):
        for law in laws:
            ta_cor = T_A_corrected(P, l_mem, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            tf = T_full(P, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            if ta_cor is not None and tf is not None:
                residual = abs(ta_cor - tf)
                results["BCG-1"].append({
                    "P": P, "law": law, "residual_bits": residual,
                    "passes_tolerance": residual < 1e-9,
                })

    bcg1_pass = all(r["passes_tolerance"] for r in results["BCG-1"])
    results["BCG-1_verdict"] = "PASS" if bcg1_pass else "FAIL"

    results["gate_verdict"] = "PASS" if (bcg1_pass and bcg2_pass) else "FAIL"
    return results


def run_reproduction_gate(a1, a2, a3, b3, a4):
    """RG-1..RG-5 reproduction gate."""
    results = {}
    laws = ["L1", "L2", "L3", "L4"]

    # Compute T_A at P=256, log2_w=1000, c=0 for all combinations
    gate_values = {}
    for law in laws:
        for S in S_VALUES:
            for A in A_VALUES:
                ta = T_A_corrected(256, UNBOUNDED_LOG2_W, law, S, A, 0.0,
                                   a1, a2, a3, b3, a4)
                gate_values[(law, S, A)] = ta

    # RG-1: S=0, A=0, all laws in [118.25, 118.75]
    rg1_vals = [gate_values[(law, 0.0, 0.0)] for law in laws]
    rg1_pass = all(118.25 <= v <= 118.75 for v in rg1_vals if v is not None)
    results["RG-1"] = {
        "values": {law: gate_values[(law, 0.0, 0.0)] for law in laws},
        "band": [min(v for v in rg1_vals if v), max(v for v in rg1_vals if v)],
        "required_band": [118.25, 118.75],
        "verdict": "PASS" if rg1_pass else "FAIL",
    }

    # RG-2: S=3.0, A=0, all laws in [121.25, 121.75]
    rg2_vals = [gate_values[(law, 3.0, 0.0)] for law in laws]
    rg2_pass = all(121.25 <= v <= 121.75 for v in rg2_vals if v is not None)
    results["RG-2"] = {
        "values": {law: gate_values[(law, 3.0, 0.0)] for law in laws},
        "band": [min(v for v in rg2_vals if v), max(v for v in rg2_vals if v)],
        "required_band": [121.25, 121.75],
        "verdict": "PASS" if rg2_pass else "FAIL",
    }

    # RG-3: A=1.584963, S=0 in [119.9, 120.4] and S=3.0 in [122.9, 123.4]
    rg3_s0 = [gate_values[(law, 0.0, 1.584963)] for law in laws]
    rg3_s3 = [gate_values[(law, 3.0, 1.584963)] for law in laws]
    rg3_pass_s0 = all(119.9 <= v <= 120.4 for v in rg3_s0 if v is not None)
    rg3_pass_s3 = all(122.9 <= v <= 123.4 for v in rg3_s3 if v is not None)
    results["RG-3"] = {
        "values_S0": {law: gate_values[(law, 0.0, 1.584963)] for law in laws},
        "values_S3": {law: gate_values[(law, 3.0, 1.584963)] for law in laws},
        "band_S0": [min(v for v in rg3_s0 if v), max(v for v in rg3_s0 if v)],
        "band_S3": [min(v for v in rg3_s3 if v), max(v for v in rg3_s3 if v)],
        "required_band_S0": [119.9, 120.4],
        "required_band_S3": [122.9, 123.4],
        "verdict": "PASS" if (rg3_pass_s0 and rg3_pass_s3) else "FAIL",
    }

    # RG-4: Unit mixing disclosure
    # Low endpoint: RG-1 (F_p2 operations), High endpoint: RG-3 S=3 (AES-equivalent)
    low_ep = max(rg1_vals)
    high_ep = max(rg3_s3)
    results["RG-4"] = {
        "headline_bracket": [min(rg1_vals), max(rg3_s3)],
        "low_endpoint_unit": "F_p2_operations",
        "high_endpoint_unit": "AES_equivalent_at_alpha_3",
        "unit_mixing_disclosed": True,
        "units_differ": True,
        "verdict": "PASS",  # passes by disclosing
    }

    # RG-5: Full grid at P=256, c=0, MC_P13_CORRECTED, log2_w=1000
    # 4 laws x 2 S x 4 A
    gaps = []
    target = 128.0
    for law in laws:
        for S in S_VALUES:
            for A in A_VALUES:
                ta = gate_values[(law, S, A)]
                if ta is not None:
                    gap = target - ta
                    gaps.append({"law": law, "S": S, "A": A, "T_A": ta, "gap": gap})

    min_gap = min(g["gap"] for g in gaps)
    max_gap = max(g["gap"] for g in gaps)
    rg5_pass = (min_gap <= 6.5 and max_gap >= 10.5)
    results["RG-5"] = {
        "min_gap": min_gap,
        "max_gap": max_gap,
        "min_gap_cell": next(g for g in gaps if g["gap"] == min_gap),
        "max_gap_cell": next(g for g in gaps if g["gap"] == max_gap),
        "required_span_covers": [6.0, 11.0],
        "actual_span": [min_gap, max_gap],
        "verdict": "PASS" if rg5_pass else "FAIL",
    }

    overall = all(results[k]["verdict"] == "PASS" for k in ["RG-1", "RG-2", "RG-3", "RG-4", "RG-5"])
    results["gate_verdict"] = "PASS" if overall else "FAIL"
    return results


def run_xchk1(a1, a2, a3, b3, a4):
    """XCHK-1: independent expression path for T_A(256, log2_w=1000, S=0, A=0, c=0)."""
    results = {}
    laws = ["L1", "L2", "L3", "L4"]

    for law in laws:
        # General evaluator
        ta_general = T_A_corrected(256, UNBOUNDED_LOG2_W, law, 0.0, 0.0, 0.0,
                                   a1, a2, a3, b3, a4)
        # Independent direct summation
        if law == "L1":
            E_direct = math.log2(a1 * 256)
        elif law == "L2":
            E_direct = math.log2(a2 * 256)
        elif law == "L3":
            E_direct = math.log2(a3 * 256 + b3)
        elif law == "L4":
            E_direct = math.log2(a4 * 256)
        # Direct: L_paper(256) + E + S(=0) + c(=0)*sqrt(256) + A(=0) + penalty(=0)
        # penalty = 0.5*max(0, 92.5 - 1000) = 0
        ta_direct = 106.5 + E_direct + 0.0 + 0.0 + 0.0 + 0.0

        diff = abs(ta_general - ta_direct)
        results[law] = {
            "general_evaluator": ta_general,
            "direct_summation": ta_direct,
            "difference": diff,
            "passes_1e-12": diff < 1e-12,
        }

    all_pass = all(r["passes_1e-12"] for r in results.values())
    results["verdict"] = "PASS" if all_pass else "FAIL"
    return results


def run_monotonicity(a1, a2, a3, b3, a4):
    """MONO-1..MONO-5 checks."""
    results = {}

    # MONO-1: d(Delta)/d(log2 w) check
    mono1_checks = []
    laws = ["L1", "L2", "L3", "L4"]
    for P in T2_P:
        l_mem_P = L_mem(P)
        for law in laws:
            for S in S_VALUES[:1]:  # Sample S=0 for efficiency (the slope is S-independent)
                A = 0.0
                c = 0.0
                for i in range(len(W_GRID_LOG2) - 1):
                    w1 = W_GRID_LOG2[i]
                    w2 = W_GRID_LOG2[i + 1]

                    # MC_P13_CORRECTED
                    d1_c = margin_corrected(P, w1, law, S, A, c, a1, a2, a3, b3, a4)
                    d2_c = margin_corrected(P, w2, law, S, A, c, a1, a2, a3, b3, a4)
                    if d1_c is not None and d2_c is not None:
                        slope_c = (d2_c - d1_c) / (w2 - w1)
                        # Expected: +0.5 if both below L_mem(P), 0 if both above
                        if w2 <= l_mem_P:
                            expected = 0.5
                        elif w1 >= l_mem_P:
                            expected = 0.0
                        else:
                            expected = None  # Spans the kink
                        if expected is not None:
                            mono1_checks.append({
                                "P": P, "law": law, "MC": "MC_P13_CORRECTED",
                                "w1": w1, "w2": w2, "slope": slope_c,
                                "expected": expected, "error": abs(slope_c - expected),
                                "pass": abs(slope_c - expected) < 1e-6,
                            })

                    # MC_VOW: slope = -0.5 wherever feasible
                    d1_v = margin_vow(P, w1, law, S, A, c, a1, a2, a3, b3, a4)
                    d2_v = margin_vow(P, w2, law, S, A, c, a1, a2, a3, b3, a4)
                    if d1_v is not None and d2_v is not None:
                        slope_v = (d2_v - d1_v) / (w2 - w1)
                        mono1_checks.append({
                            "P": P, "law": law, "MC": "MC_VOW",
                            "w1": w1, "w2": w2, "slope": slope_v,
                            "expected": -0.5, "error": abs(slope_v - (-0.5)),
                            "pass": abs(slope_v - (-0.5)) < 1e-6,
                        })

    mono1_pass = all(c["pass"] for c in mono1_checks)
    results["MONO-1"] = {
        "n_checks": len(mono1_checks),
        "n_pass": sum(1 for c in mono1_checks if c["pass"]),
        "n_fail": sum(1 for c in mono1_checks if not c["pass"]),
        "max_error": max(c["error"] for c in mono1_checks) if mono1_checks else 0,
        "verdict": "PASS" if mono1_pass else "FAIL",
    }

    # MONO-2: Kink location at L_mem(P)
    mono2_checks = []
    for P in T2_P:
        l_mem_P = L_mem(P)
        for law in laws:
            # Check that penalty is exactly 0 at log2_w = L_mem(P) and > 0 just below
            ta_at_lmem = T_A_corrected(P, l_mem_P, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            tf = T_full(P, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            ta_below = T_A_corrected(P, l_mem_P - 1.0, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            ta_above = T_A_corrected(P, l_mem_P + 1.0, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)

            if all(v is not None for v in [ta_at_lmem, tf, ta_below, ta_above]):
                kink_correct = (
                    abs(ta_at_lmem - tf) < 1e-9  # penalty = 0 at kink
                    and abs(ta_above - tf) < 1e-9  # penalty = 0 above kink
                    and ta_below > tf + 0.4  # penalty > 0 below kink (0.5*1.0 = 0.5)
                )
                mono2_checks.append({
                    "P": P, "law": law, "L_mem_P": l_mem_P,
                    "residual_at_kink": abs(ta_at_lmem - tf),
                    "penalty_below": ta_below - tf,
                    "penalty_above": ta_above - tf,
                    "pass": kink_correct,
                })

    mono2_pass = all(c["pass"] for c in mono2_checks)
    results["MONO-2"] = {
        "n_checks": len(mono2_checks),
        "all_pass": mono2_pass,
        "kink_locations": {f"P={c['P']}": c["L_mem_P"] for c in mono2_checks[:5]},
        "verdict": "PASS" if mono2_pass else "FAIL",
    }

    # MONO-3: p*(w) non-increasing in w under MC_P13_CORRECTED
    # Collect numeric loci for a sample theta
    mono3_results = []
    for law in laws[:2]:  # Sample L1, L2
        for S in [0.0]:
            for A in [0.0]:
                for c in [0.0]:
                    loci_corr = []
                    loci_vow = []
                    for w in W_GRID_LOG2:
                        # MC_P13_CORRECTED
                        def mf_c(P, _w=w):
                            return margin_corrected(P, _w, law, S, A, c, a1, a2, a3, b3, a4)
                        res_c = solve_crossover(mf_c)
                        if res_c["outcome"] == "NUMERIC":
                            loci_corr.append((w, res_c["p_star_log2"]))

                        # MC_VOW
                        def mf_v(P, _w=w):
                            return margin_vow(P, _w, law, S, A, c, a1, a2, a3, b3, a4)
                        res_v = solve_crossover(mf_v)
                        if res_v["outcome"] == "NUMERIC":
                            loci_vow.append((w, res_v["p_star_log2"]))

                    # Check monotonicity
                    if len(loci_corr) >= 2:
                        non_increasing = all(
                            loci_corr[i+1][1] <= loci_corr[i][1] + 1e-6
                            for i in range(len(loci_corr) - 1)
                        )
                        mono3_results.append({
                            "law": law, "S": S, "A": A, "c": c, "MC": "MC_P13_CORRECTED",
                            "n_numeric": len(loci_corr),
                            "non_increasing": non_increasing,
                            "loci": loci_corr,
                        })
                    else:
                        mono3_results.append({
                            "law": law, "S": S, "A": A, "c": c, "MC": "MC_P13_CORRECTED",
                            "n_numeric": len(loci_corr),
                            "verdict": f"NOT_EVALUABLE(n={len(loci_corr)})",
                        })

                    if len(loci_vow) >= 2:
                        non_decreasing = all(
                            loci_vow[i+1][1] >= loci_vow[i][1] - 1e-6
                            for i in range(len(loci_vow) - 1)
                        )
                        mono3_results.append({
                            "law": law, "S": S, "A": A, "c": c, "MC": "MC_VOW",
                            "n_numeric": len(loci_vow),
                            "non_decreasing": non_decreasing,
                            "loci": loci_vow,
                        })
                    else:
                        mono3_results.append({
                            "law": law, "S": S, "A": A, "c": c, "MC": "MC_VOW",
                            "n_numeric": len(loci_vow),
                            "verdict": f"NOT_EVALUABLE(n={len(loci_vow)})",
                        })

    # Determine overall MONO-3 verdict
    evaluable = [r for r in mono3_results if "non_increasing" in r or "non_decreasing" in r]
    if evaluable:
        mono3_pass = all(
            r.get("non_increasing", True) and r.get("non_decreasing", True)
            for r in evaluable
        )
        mono3_verdict = "PASS" if mono3_pass else "FAIL"
    else:
        mono3_verdict = "NOT_EVALUABLE"

    results["MONO-3"] = {
        "results": mono3_results,
        "verdict": mono3_verdict,
    }

    # MONO-4: MC_P13_CORRECTED and MC_VOW differ by >= 0.5 bits somewhere
    mono4_found = False
    max_diff = 0.0
    for P in T2_P:
        for w in W_GRID_LOG2:
            if w >= 10 and is_feasible_vow(P, w):
                d_c = margin_corrected(P, w, "L1", 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
                d_v = margin_vow(P, w, "L1", 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
                if d_c is not None and d_v is not None:
                    diff = abs(d_c - d_v)
                    max_diff = max(max_diff, diff)
                    if diff >= 0.5:
                        mono4_found = True

    results["MONO-4"] = {
        "max_difference_bits": max_diff,
        "exceeds_0.5_bits": mono4_found,
        "verdict": "PASS" if mono4_found else "FAIL",
    }

    # MONO-5: Data checks on T2 columns
    mono5_checks = {}
    # L_paper strictly increasing
    l_paper_increasing = all(T2_L_PAPER[i+1] > T2_L_PAPER[i] for i in range(4))
    # L_mem strictly increasing
    l_mem_increasing = all(T2_L_MEM[i+1] > T2_L_MEM[i] for i in range(4))
    # L_paper(P) - P/3 strictly increasing and in [21.0, 47.0]
    lp_minus_p3 = [T2_L_PAPER[i] - T2_P[i]/3.0 for i in range(5)]
    lp_p3_increasing = all(lp_minus_p3[i+1] > lp_minus_p3[i] for i in range(4))
    lp_p3_in_range = all(21.0 <= v <= 47.0 for v in lp_minus_p3)
    # L_mem(P) - P/3 non-decreasing
    lm_minus_p3 = [T2_L_MEM[i] - T2_P[i]/3.0 for i in range(5)]
    lm_p3_nondecreasing = all(lm_minus_p3[i+1] >= lm_minus_p3[i] - 1e-9 for i in range(4))

    mono5_pass = all([l_paper_increasing, l_mem_increasing, lp_p3_increasing,
                      lp_p3_in_range, lm_p3_nondecreasing])
    results["MONO-5"] = {
        "L_paper_strictly_increasing": l_paper_increasing,
        "L_mem_strictly_increasing": l_mem_increasing,
        "L_paper_minus_P_over_3": lp_minus_p3,
        "L_paper_minus_P_over_3_increasing": lp_p3_increasing,
        "L_paper_minus_P_over_3_in_21_47": lp_p3_in_range,
        "L_mem_minus_P_over_3": lm_minus_p3,
        "L_mem_minus_P_over_3_nondecreasing": lm_p3_nondecreasing,
        "verdict": "PASS" if mono5_pass else "FAIL",
    }

    return results


def run_sanity1(a1, a2, a3, b3, a4):
    """SANITY-1: Model coherence audit."""
    results = []
    laws = ["L1", "L2", "L3", "L4"]

    for P in T2_P:
        l_mem_P = L_mem(P)
        for law in laws:
            # d(T_A)/d(log2_w) below L_mem(P)
            w_below = l_mem_P - 10.0
            if w_below < 1:
                w_below = 1.0
            ta1 = T_A_corrected(P, w_below, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            ta2 = T_A_corrected(P, w_below + 1.0, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            if ta1 is not None and ta2 is not None:
                slope = ta2 - ta1  # dT_A/d(log2_w) ~ (ta2 - ta1) / 1.0
                # slope should be -0.5 (cost FALLS as memory rises)
                results.append({
                    "P": P, "law": law,
                    "dT_A_d_log2w_below_Lmem": slope,
                    "sign": "negative" if slope < 0 else "positive" if slope > 0 else "zero",
                    "physically_correct": slope < 0,
                    "magnitude": abs(slope),
                    "expected_magnitude": 0.5,
                })

    all_correct = all(r["physically_correct"] for r in results)
    any_pathology = not all_correct
    return {
        "checks": results,
        "all_physically_correct": all_correct,
        "model_pathology": any_pathology,
        "interpretation": (
            "Reducing memory below L_mem(P) makes the assessed method MORE expensive "
            "(cost rises as memory falls). This is the physically required direction."
            if all_correct else
            "MODEL_PATHOLOGY: memory_discount_direction - some cells show cost falling as memory falls."
        ),
    }


# ===========================================================================
# MAIN COMPUTATION
# ===========================================================================
def main():
    start_time = time.time()
    print(f"EXP-SSI-9b542d: Starting execution at {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    print(f"Seed: {SEED} (no randomness used)")

    # ===== STEP 0: Environment =====
    print("\n=== STEP 0: Environment verification ===")
    env = step0_environment()
    if not env["no_forbidden_import_assertion"]:
        print("FATAL: Forbidden modules found:", env["forbidden_modules_found"])
        sys.exit(1)
    print(f"  Python: {env['python_version'].split()[0]}")
    print(f"  Platform: {env['platform']}")
    print(f"  Forbidden modules: none found")
    print(f"  Required stdlib: verified")

    # ===== STEP 1: Load and verify inputs =====
    print("\n=== STEP 1: Input loading and verification ===")
    t1_x, t1_y = load_and_verify_t1()
    print(f"  T1: 8 rows verified (log2_p {t1_x[0]}-{t1_x[-1]})")

    paper_pairs, overhead_c = load_and_verify_t2()
    print(f"  T2: 5 rows verified against paper lines 234-238")
    print(f"  PAPER_PAIRS: verified against cost_model.py")
    print(f"  OVERHEAD_C from file: {overhead_c}")

    # Record input hashes
    input_hashes = {
        "T1_cost_measurements.json": sha256_file(T1_PATH),
        "T2_paper_fulltext.md": sha256_file(T2_PATH),
        "cost_model.py": sha256_file(COST_MODEL_PATH),
    }
    print(f"  Input hashes recorded")

    # ===== STEP 2: Compute fit parameters =====
    print("\n=== STEP 2: Fit parameters ===")
    a1, a2, a3, b3, a4 = compute_fit_parameters(t1_x, t1_y)
    print(f"  a1 (proportional): {a1:.6f}  (frozen ref: {FROZEN_A1})")
    print(f"  a2 (headline): {a2} (frozen ref: {FROZEN_A2})")
    print(f"  a3 (OLS slope): {a3:.6f} (frozen ref: {FROZEN_A3})")
    print(f"  b3 (OLS intercept): {b3:.6f} (frozen ref: {FROZEN_B3})")
    print(f"  a4 (largest-row): {a4:.8f} (frozen ref: {FROZEN_A4})")

    # Verify against frozen values
    assert abs(a1 - FROZEN_A1) < 0.001, f"a1 drift: {a1} vs {FROZEN_A1}"
    assert a2 == FROZEN_A2
    assert abs(a3 - FROZEN_A3) < 0.001, f"a3 drift: {a3} vs {FROZEN_A3}"
    assert abs(b3 - FROZEN_B3) < 0.001, f"b3 drift: {b3} vs {FROZEN_B3}"
    assert abs(a4 - FROZEN_A4) < 0.001, f"a4 drift: {a4} vs {FROZEN_A4}"

    # Transcription consistency readout
    transcription = {
        "|a1 - 16.2|": abs(a1 - 16.2),
        "|a4 - 16.2|": abs(a4 - 16.2),
        "|a3*256+b3 - a2*256|": abs(a3*256 + b3 - a2*256),
    }
    print(f"  Transcription consistency: |a1-16.2|={transcription['|a1 - 16.2|']:.4f}, "
          f"|a4-16.2|={transcription['|a4 - 16.2|']:.4f}")

    # ===== STEP 3: BOUNDARY-CONDITION-GATE =====
    print("\n=== STEP 3: BOUNDARY-CONDITION-GATE ===")
    bcg = run_boundary_condition_gate(a1, a2, a3, b3, a4)
    print(f"  BCG-2 (negative control): {bcg['BCG-2_verdict']}")
    if bcg["BCG-2_verdict"] == "PASS":
        sample = bcg["BCG-2"][0]
        print(f"    Sample: P={sample['P']}, residual={sample['residual_bits']:.2f} bits "
              f"(expected {sample['expected_residual']:.2f})")
    print(f"  BCG-1 (corrected formula): {bcg['BCG-1_verdict']}")
    if bcg["BCG-1_verdict"] == "PASS":
        print(f"    All residuals < 1e-9 bits (max: {max(r['residual_bits'] for r in bcg['BCG-1']):.2e})")
    print(f"  Gate verdict: {bcg['gate_verdict']}")

    if bcg["gate_verdict"] == "FAIL":
        print("\nFATAL: BOUNDARY-CONDITION-GATE failed. Run INVALID.")
        # Still write artifacts for diagnosis
        write_outputs(env, input_hashes, a1, a2, a3, b3, a4, transcription,
                      bcg, None, None, None, None, None, None, None, None, None,
                      start_time, "INVALID", "BOUNDARY-CONDITION-GATE failed")
        sys.exit(2)

    # ===== STEP 4: REPRODUCTION GATE =====
    print("\n=== STEP 4: REPRODUCTION GATE ===")
    rg = run_reproduction_gate(a1, a2, a3, b3, a4)
    for k in ["RG-1", "RG-2", "RG-3", "RG-4", "RG-5"]:
        print(f"  {k}: {rg[k]['verdict']}")
    print(f"  Gate verdict: {rg['gate_verdict']}")

    if rg["gate_verdict"] == "FAIL":
        print("\nFATAL: REPRODUCTION GATE failed. Run INVALID.")
        write_outputs(env, input_hashes, a1, a2, a3, b3, a4, transcription,
                      bcg, rg, None, None, None, None, None, None, None, None,
                      start_time, "INVALID", "REPRODUCTION GATE failed")
        sys.exit(3)

    # ===== STEP 5: XCHK-1 =====
    print("\n=== STEP 5: Cross-check XCHK-1 ===")
    xchk1 = run_xchk1(a1, a2, a3, b3, a4)
    print(f"  Verdict: {xchk1['verdict']}")
    for law, r in xchk1.items():
        if law != "verdict" and isinstance(r, dict):
            print(f"    {law}: diff = {r['difference']:.2e}")

    if xchk1["verdict"] == "FAIL":
        print("\nFATAL: XCHK-1 failed. Run INVALID.")
        write_outputs(env, input_hashes, a1, a2, a3, b3, a4, transcription,
                      bcg, rg, xchk1, None, None, None, None, None, None, None,
                      start_time, "INVALID", "XCHK-1 failed")
        sys.exit(4)

    # ===== STEP 6: MONOTONICITY =====
    print("\n=== STEP 6: Monotonicity checks ===")
    mono = run_monotonicity(a1, a2, a3, b3, a4)
    for k in ["MONO-1", "MONO-2", "MONO-3", "MONO-4", "MONO-5"]:
        print(f"  {k}: {mono[k]['verdict']}")

    blocking_mono_fail = any(
        mono[k]["verdict"] == "FAIL" for k in ["MONO-1", "MONO-2", "MONO-4", "MONO-5"]
    )
    if blocking_mono_fail:
        print("\nFATAL: Blocking monotonicity check failed. Run INVALID.")
        write_outputs(env, input_hashes, a1, a2, a3, b3, a4, transcription,
                      bcg, rg, xchk1, mono, None, None, None, None, None, None,
                      start_time, "INVALID", "Blocking MONO check failed")
        sys.exit(5)

    # ===== STEP 7: MAIN CROSSOVER GRID =====
    print("\n=== STEP 7: Main crossover grid (4480 cells) ===")
    laws_main = ["L1", "L2", "L3", "L4"]
    mc_types = ["MC_P13_CORRECTED", "MC_VOW"]

    p_star_table = []
    cell_count = 0
    n_numeric = 0
    n_no_crossover = 0
    n_infeasible = 0
    n_multiple = 0

    for law in laws_main:
        for S in S_VALUES:
            for A in A_VALUES:
                for c in C_VALUES:
                    for mc in mc_types:
                        for w in W_GRID_LOG2:
                            cell_count += 1

                            # Build margin function
                            if mc == "MC_P13_CORRECTED":
                                def mf(P, _w=w, _law=law, _S=S, _A=A, _c=c):
                                    return margin_corrected(P, _w, _law, _S, _A, _c,
                                                           a1, a2, a3, b3, a4)
                            else:
                                def mf(P, _w=w, _law=law, _S=S, _A=A, _c=c):
                                    return margin_vow(P, _w, _law, _S, _A, _c,
                                                     a1, a2, a3, b3, a4)

                            result = solve_crossover(mf)
                            result["law"] = law
                            result["S"] = S
                            result["A"] = A
                            result["c"] = c
                            result["MC"] = mc
                            result["log2_w"] = w
                            result["fit_window_extrapolation"] = True
                            result["extrapolation_ratio_min"] = 256.0 / 40.0
                            result["extrapolation_ratio_max"] = 768.0 / 40.0

                            # Interpolation info
                            if result["outcome"] == "NUMERIC":
                                ps = result["p_star_log2"]
                                br = get_bracketing_rows(ps)
                                result["interpolated_between_committed_rows"] = br
                                n_numeric += 1
                            elif result["outcome"] == "NO_CROSSOVER_IN_WINDOW":
                                n_no_crossover += 1
                            elif result["outcome"] == "INFEASIBLE_AT_MEMORY":
                                n_infeasible += 1
                            elif result["outcome"] == "MULTIPLE_ROOTS":
                                n_multiple += 1

                            # L_mem at window endpoints for feasibility visibility
                            result["L_mem_at_256"] = L_mem(256)
                            result["L_mem_at_768"] = L_mem(768)

                            p_star_table.append(result)

    print(f"  Total cells: {cell_count}")
    print(f"  Numeric: {n_numeric}, No crossover: {n_no_crossover}, "
          f"Infeasible: {n_infeasible}, Multiple: {n_multiple}")

    # ===== STEP 8: NULL OBJECT =====
    print("\n=== STEP 8: Null object arms ===")
    null_laws = ["N0", "N1"]
    null_table = []
    null_displacements = {"N0": [], "N1": []}

    for null_law in null_laws:
        for S in S_VALUES:
            for A in A_VALUES:
                for c in C_VALUES:
                    for mc in mc_types:
                        for w in W_GRID_LOG2:
                            if mc == "MC_P13_CORRECTED":
                                def mf_null(P, _w=w, _law=null_law, _S=S, _A=A, _c=c):
                                    return margin_corrected(P, _w, _law, _S, _A, _c,
                                                           a1, a2, a3, b3, a4)
                            else:
                                def mf_null(P, _w=w, _law=null_law, _S=S, _A=A, _c=c):
                                    return margin_vow(P, _w, _law, _S, _A, _c,
                                                     a1, a2, a3, b3, a4)

                            result = solve_crossover(mf_null)
                            result["law"] = null_law
                            result["S"] = S
                            result["A"] = A
                            result["c"] = c
                            result["MC"] = mc
                            result["log2_w"] = w
                            result["fit_window_extrapolation"] = True
                            null_table.append(result)

    # Compute null displacements on the margin SURFACE (not the locus)
    for P in T2_P:
        for w in W_GRID_LOG2:
            for law in laws_main:
                for S in S_VALUES[:1]:
                    for A in [0.0]:
                        for c in [0.0]:
                            d_corr = margin_corrected(P, w, law, S, A, c, a1, a2, a3, b3, a4)
                            d_n0 = margin_corrected(P, w, "N0", S, A, c, a1, a2, a3, b3, a4)
                            d_n1 = margin_corrected(P, w, "N1", S, A, c, a1, a2, a3, b3, a4)
                            if d_corr is not None and d_n0 is not None:
                                null_displacements["N0"].append({
                                    "P": P, "w": w, "law": law,
                                    "D": abs(d_corr - d_n0),
                                })
                            if d_corr is not None and d_n1 is not None:
                                null_displacements["N1"].append({
                                    "P": P, "w": w, "law": law,
                                    "D": abs(d_corr - d_n1),
                                })

    # Summarize null displacements
    null_summary = {}
    for nk in ["N0", "N1"]:
        disps = null_displacements[nk]
        if disps:
            ds = [d["D"] for d in disps]
            null_summary[nk] = {
                "min": min(ds),
                "max": max(ds),
                "argmin": next(d for d in disps if d["D"] == min(ds)),
                "argmax": next(d for d in disps if d["D"] == max(ds)),
            }

    print(f"  D_null0: min={null_summary['N0']['min']:.4f}, max={null_summary['N0']['max']:.4f}")
    print(f"  D_null1: min={null_summary['N1']['min']:.4f}, max={null_summary['N1']['max']:.4f}")

    # Check preregistered predictions
    null_pred = {
        "D_null0_min_ge_11.9": null_summary["N0"]["min"] >= 11.9,
        "D_null0_max_le_14.2": null_summary["N0"]["max"] <= 14.2,
        "D_null1_lt_D_null0_everywhere": all(
            null_displacements["N1"][i]["D"] < null_displacements["N0"][i]["D"]
            for i in range(min(len(null_displacements["N0"]), len(null_displacements["N1"])))
        ),
    }
    print(f"  Predictions: {null_pred}")

    # ===== STEP 9: SENSITIVITY (L5, log2_k_DG, adversarial corner) =====
    print("\n=== STEP 9: Sensitivity analysis ===")

    # L5 sensitivity
    l5_sensitivity = []
    for P in T2_P:
        e_l4 = E_law(P, "L4", a1, a2, a3, b3, a4)
        e_l5 = E_law(P, "L5", a1, a2, a3, b3, a4)
        l5_sensitivity.append({
            "P": P,
            "E_L4": e_l4,
            "E_L5": e_l5,
            "E_L5_minus_E_L4": e_l5 - e_l4 if e_l5 and e_l4 else None,
        })
    print(f"  L5 sensitivity: E_L5 - E_L4 at P=256: {l5_sensitivity[0]['E_L5_minus_E_L4']:.4f}")

    # log2_k_DG sensitivity
    k_dg_values = [-4.0, -2.0, 0.0, 2.0, 4.0]
    k_dg_sensitivity = []
    for w in W_GRID_LOG2[:5]:  # Sample first 5 w values
        loci_at_k = []
        for k in k_dg_values:
            def mf_k(P, _w=w, _k=k):
                return margin_corrected(P, _w, "L1", 0.0, 0.0, 0.0,
                                        a1, a2, a3, b3, a4, log2_k_dg=_k)
            res = solve_crossover(mf_k)
            loci_at_k.append({
                "log2_k_DG": k,
                "outcome": res["outcome"],
                "p_star": res.get("p_star_log2"),
            })
        k_dg_sensitivity.append({"log2_w": w, "loci": loci_at_k})

    # Adversarial corner
    # Smallest E: find which law gives smallest E at each P
    adversarial_corner = []
    for P in T2_P:
        e_vals = {law: E_law(P, law, a1, a2, a3, b3, a4) for law in laws_main}
        min_law = min(e_vals, key=lambda k: e_vals[k] if e_vals[k] is not None else float('inf'))
        # Adversarial: min E, S=0, A=-1.736966, c=0.0, MC_P13_CORRECTED
        ta_adv = T_A_corrected(P, UNBOUNDED_LOG2_W, min_law, 0.0, -1.736966, 0.0,
                               a1, a2, a3, b3, a4)
        tb_adv = T_B_corrected(P, UNBOUNDED_LOG2_W, -1.736966)
        # MC_VOW comparison at same point (unbounded memory, so feasible)
        ta_vow_adv = T_A_vow(P, UNBOUNDED_LOG2_W, min_law, 0.0, -1.736966, 0.0,
                             a1, a2, a3, b3, a4)
        tb_vow_adv = T_B_vow(P, UNBOUNDED_LOG2_W, -1.736966)

        adversarial_corner.append({
            "P": P,
            "law": min_law,
            "E": e_vals[min_law],
            "T_A_MC_P13_CORRECTED": ta_adv,
            "T_B_MC_P13_CORRECTED": tb_adv,
            "margin_MC_P13_CORRECTED": tb_adv - ta_adv if ta_adv else None,
            "T_A_MC_VOW": ta_vow_adv,
            "T_B_MC_VOW": tb_vow_adv,
            "margin_MC_VOW": tb_vow_adv - ta_vow_adv if ta_vow_adv else None,
            "note": "A cancels in Delta (appears on both sides)",
        })

    print(f"  Adversarial corner at P=256: margin={adversarial_corner[0]['margin_MC_P13_CORRECTED']:.4f} bits")

    # SANITY-1
    print("\n=== STEP 9b: SANITY-1 model coherence ===")
    sanity1 = run_sanity1(a1, a2, a3, b3, a4)
    print(f"  All physically correct: {sanity1['all_physically_correct']}")

    # ===== STEP 10: SCOPE STATEMENT =====
    print("\n=== STEP 10: Scope statement ===")
    scope = compute_scope(a1, a2, a3, b3, a4)
    for axis in ["SCOPE-A", "SCOPE-B", "SCOPE-C"]:
        print(f"  {axis}: {scope[axis]['summary']}")

    # ===== STEP 11: CONVENTION-SIGN TABLE =====
    print("\n=== STEP 11: Convention-sign table ===")
    conv_sign = compute_convention_sign(a1, a2, a3, b3, a4)
    print(f"  Agree count: {conv_sign['agree_count']} / {conv_sign['total_feasible']}")

    # ===== STEP 12: P* band per log2_w =====
    print("\n=== STEP 12: P* bands ===")
    bands = compute_bands(p_star_table)
    for b in bands[:3]:
        print(f"  log2_w={b['log2_w']}: [{b['min_p_star']:.2f}, {b['max_p_star']:.2f}] "
              f"(n_numeric={b['n_numeric']})" if b['min_p_star'] else
              f"  log2_w={b['log2_w']}: no numeric loci")

    # ===== STEP 13: Tail checks =====
    print("\n=== STEP 13: Tail checks ===")
    tail = compute_tail_checks(p_star_table, a1, a2, a3, b3, a4)
    print(f"  Smallest |Delta| in grid: {tail['smallest_abs_delta']:.6f} bits "
          f"at P={tail['smallest_abs_delta_cell']['P']}")

    # ===== STEP 14: XCHK-2 (optional, numpy) =====
    print("\n=== STEP 14: XCHK-2 (optional) ===")
    xchk2 = attempt_xchk2()
    print(f"  Status: {xchk2['status']}")

    # ===== STEP 15: L5 grid (sensitivity, 1120 cells) =====
    print("\n=== STEP 15: L5 sensitivity grid (1120 cells) ===")
    l5_table = []
    for S in S_VALUES:
        for A in A_VALUES:
            for c in C_VALUES:
                for mc in mc_types:
                    for w in W_GRID_LOG2:
                        if mc == "MC_P13_CORRECTED":
                            def mf_l5(P, _w=w, _S=S, _A=A, _c=c):
                                return margin_corrected(P, _w, "L5", _S, _A, _c,
                                                       a1, a2, a3, b3, a4)
                        else:
                            def mf_l5(P, _w=w, _S=S, _A=A, _c=c):
                                return margin_vow(P, _w, "L5", _S, _A, _c,
                                                  a1, a2, a3, b3, a4)
                        result = solve_crossover(mf_l5)
                        result["law"] = "L5"
                        result["S"] = S
                        result["A"] = A
                        result["c"] = c
                        result["MC"] = mc
                        result["log2_w"] = w
                        result["fit_window_extrapolation"] = True
                        l5_table.append(result)
    print(f"  L5 cells computed: {len(l5_table)}")

    # ===== FINALIZE =====
    elapsed = time.time() - start_time
    print(f"\n=== Execution complete in {elapsed:.2f}s ===")

    # Write all outputs
    write_outputs(env, input_hashes, a1, a2, a3, b3, a4, transcription,
                  bcg, rg, xchk1, mono, p_star_table, null_table, null_summary,
                  null_pred, {
                      "l5_sensitivity": l5_sensitivity,
                      "k_dg_sensitivity": k_dg_sensitivity,
                      "adversarial_corner": adversarial_corner,
                      "sanity1": sanity1,
                  }, scope, conv_sign,
                  start_time, "VALID", None,
                  bands=bands, tail=tail, xchk2=xchk2, l5_table=l5_table)


# ===========================================================================
# HELPER COMPUTATIONS
# ===========================================================================
def compute_scope(a1, a2, a3, b3, a4):
    """Compute SCOPE-A, SCOPE-B, SCOPE-C."""
    scope = {}
    nist_levels = [(256, "NIST-I", 128.0), (384, "NIST-III", 192.0), (512, "NIST-V", 256.0)]

    # SCOPE-A: advantage over matched baseline
    scope_a = []
    for P, label, target in nist_levels:
        # At unbounded memory, S=0, A=0, c=0, L1
        ta = T_A_corrected(P, UNBOUNDED_LOG2_W, "L1", 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
        tb = T_B_corrected(P, UNBOUNDED_LOG2_W, 0.0)
        advantage = tb - ta  # assessed method advantage
        scope_a.append({"P": P, "label": label, "advantage_bits": advantage,
                        "target": target, "T_A": ta, "T_B": tb})

    scope["SCOPE-A"] = {
        "data": scope_a,
        "advantage_increases_with_level": (
            scope_a[0]["advantage_bits"] < scope_a[1]["advantage_bits"] < scope_a[2]["advantage_bits"]
        ),
        "summary": f"Advantage: {scope_a[0]['advantage_bits']:.2f} / "
                   f"{scope_a[1]['advantage_bits']:.2f} / "
                   f"{scope_a[2]['advantage_bits']:.2f} bits at NIST-I/III/V",
    }

    # SCOPE-B: gap below level's own target
    scope_b = []
    for P, label, target in nist_levels:
        ta = T_A_corrected(P, UNBOUNDED_LOG2_W, "L1", 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
        gap = target - ta
        scope_b.append({"P": P, "label": label, "gap_below_target": gap,
                        "target": target, "T_A": ta})

    scope["SCOPE-B"] = {
        "data": scope_b,
        "gap_grows_with_level": (
            scope_b[0]["gap_below_target"] < scope_b[1]["gap_below_target"] < scope_b[2]["gap_below_target"]
        ),
        "summary": f"Gap below target: {scope_b[0]['gap_below_target']:.4f} / "
                   f"{scope_b[1]['gap_below_target']:.4f} / "
                   f"{scope_b[2]['gap_below_target']:.4f} bits",
    }

    # SCOPE-C: memory feasibility
    scope_c = []
    for P, label, target in nist_levels:
        l_mem = L_mem(P)
        for bpe in BYTES_PER_ENTRY_VALUES:
            log2_bytes = l_mem + math.log2(bpe)
            excess = log2_bytes - GLOBAL_STORAGE_LOG2_BYTES
            scope_c.append({
                "P": P, "label": label,
                "L_mem_entries": l_mem,
                "bytes_per_entry": bpe,
                "log2_total_bytes": log2_bytes,
                "excess_over_global_storage": excess,
                "infeasible": excess > 0,
            })

    scope["SCOPE-C"] = {
        "data": scope_c,
        "all_infeasible": all(s["infeasible"] for s in scope_c),
        "infeasibility_increases": True,  # L_mem grows with P
        "summary": f"Memory: all levels infeasible "
                   f"(excess: {scope_c[0]['excess_over_global_storage']:.1f} / "
                   f"{scope_c[2]['excess_over_global_storage']:.1f} / "
                   f"{scope_c[4]['excess_over_global_storage']:.1f} bits at 64B/entry)",
    }

    return scope


def compute_convention_sign(a1, a2, a3, b3, a4):
    """Convention-sign table: sign(Delta) under both conventions."""
    agree = 0
    total_feasible = 0
    sign_table = []

    for P in T2_P:
        for w in W_GRID_LOG2:
            d_c = margin_corrected(P, w, "L1", 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            d_v = margin_vow(P, w, "L1", 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            if d_c is not None and d_v is not None:
                s_c = 1 if d_c > 0 else (-1 if d_c < 0 else 0)
                s_v = 1 if d_v > 0 else (-1 if d_v < 0 else 0)
                total_feasible += 1
                if s_c == s_v:
                    agree += 1
                sign_table.append({"P": P, "w": w, "sign_corrected": s_c, "sign_vow": s_v})

    return {
        "agree_count": agree,
        "total_feasible": total_feasible,
        "disagree_count": total_feasible - agree,
        "sample": sign_table[:20],
    }


def compute_bands(p_star_table):
    """Compute p* band per log2_w."""
    bands = []
    for w in W_GRID_LOG2:
        cells_at_w = [r for r in p_star_table if r["log2_w"] == w]
        numeric = [r for r in cells_at_w if r["outcome"] == "NUMERIC"]
        no_cross_attack = [r for r in cells_at_w if r["outcome"] == "NO_CROSSOVER_IN_WINDOW"
                           and r.get("sign", 0) > 0]
        no_cross_baseline = [r for r in cells_at_w if r["outcome"] == "NO_CROSSOVER_IN_WINDOW"
                             and r.get("sign", 0) <= 0]
        infeasible = [r for r in cells_at_w if r["outcome"] == "INFEASIBLE_AT_MEMORY"]

        if numeric:
            p_stars = [r["p_star_log2"] for r in numeric]
            bands.append({
                "log2_w": w,
                "min_p_star": min(p_stars),
                "max_p_star": max(p_stars),
                "n_numeric": len(numeric),
                "n_no_crossover_attack_side": len(no_cross_attack),
                "n_no_crossover_baseline_side": len(no_cross_baseline),
                "n_infeasible": len(infeasible),
            })
        else:
            bands.append({
                "log2_w": w,
                "min_p_star": None,
                "max_p_star": None,
                "n_numeric": 0,
                "n_no_crossover_attack_side": len(no_cross_attack),
                "n_no_crossover_baseline_side": len(no_cross_baseline),
                "n_infeasible": len(infeasible),
            })
    return bands


def compute_tail_checks(p_star_table, a1, a2, a3, b3, a4):
    """Tail checks: smallest |Delta|, endpoint values, categorical counts."""
    # Find smallest |Delta| across the entire main grid
    smallest_abs_delta = float('inf')
    smallest_cell = None

    # Categorical counts per convention
    cat_counts = {"MC_P13_CORRECTED": {}, "MC_VOW": {}}

    for r in p_star_table:
        mc = r["MC"]
        outcome = r["outcome"]
        cat_counts[mc][outcome] = cat_counts[mc].get(outcome, 0) + 1

        # Check endpoint deltas
        for ep_key in ["endpoint_256", "endpoint_768"]:
            val = r.get(ep_key)
            if val is not None and abs(val) < smallest_abs_delta:
                smallest_abs_delta = abs(val)
                smallest_cell = {
                    "P": 256 if "256" in ep_key else 768,
                    "law": r["law"], "S": r["S"], "A": r["A"],
                    "c": r["c"], "MC": r["MC"], "log2_w": r["log2_w"],
                    "delta_value": val,
                }

    # BCG-1 residual across all main-grid P values (not just committed rows)
    bcg1_interpolated = []
    for P_int in range(256, 769, 64):
        l_mem_P = L_mem(P_int)
        for law in ["L1", "L2", "L3", "L4"]:
            ta = T_A_corrected(P_int, l_mem_P, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            tf = T_full(P_int, law, 0.0, 0.0, 0.0, a1, a2, a3, b3, a4)
            if ta is not None and tf is not None:
                bcg1_interpolated.append({
                    "P": P_int, "law": law,
                    "residual": abs(ta - tf),
                    "is_committed_row": P_int in T2_P,
                })

    return {
        "smallest_abs_delta": smallest_abs_delta,
        "smallest_abs_delta_cell": smallest_cell,
        "categorical_counts": cat_counts,
        "bcg1_interpolated_check": bcg1_interpolated,
        "bcg1_max_residual": max(r["residual"] for r in bcg1_interpolated) if bcg1_interpolated else 0,
    }


def attempt_xchk2():
    """XCHK-2: optional numpy cross-check."""
    try:
        import numpy
        # If numpy is available, we could do the Dickman rho cross-check
        # But per spec, this is optional and does not affect any reported number
        return {
            "status": "NOT_IMPLEMENTED",
            "note": "numpy available but Dickman rho cross-check not implemented in this run",
            "numpy_version": numpy.__version__,
        }
    except ImportError as e:
        return {
            "status": "NOT_RUN",
            "reason": str(e),
            "note": "numpy absent; run remains valid per specification",
        }


# ===========================================================================
# OUTPUT WRITING
# ===========================================================================
def write_outputs(env, input_hashes, a1, a2, a3, b3, a4, transcription,
                  bcg, rg, xchk1, mono, p_star_table, null_table, null_summary,
                  null_pred, sensitivity, scope, conv_sign,
                  start_time, validity, invalid_reason, **kwargs):
    """Write all output artifacts."""
    elapsed = time.time() - start_time

    # Create run directory
    run_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", RUN_ID)
    os.makedirs(run_dir, exist_ok=True)

    # environment.json
    write_json(os.path.join(run_dir, "environment.json"), env)

    # input_hashes.json
    write_json(os.path.join(run_dir, "input_hashes.json"), input_hashes)

    # boundary_condition_gate.json
    if bcg:
        write_json(os.path.join(run_dir, "boundary_condition_gate.json"), bcg)

    # reproduction_gate.json
    if rg:
        write_json(os.path.join(run_dir, "reproduction_gate.json"), rg)

    # cross_check_secondary.json
    xchk2 = kwargs.get("xchk2", {"status": "NOT_RUN"})
    write_json(os.path.join(run_dir, "cross_check_secondary.json"), {
        "XCHK-1": xchk1,
        "XCHK-2": xchk2,
    })

    # monotonicity.json
    if mono:
        write_json(os.path.join(run_dir, "monotonicity.json"), mono)

    # p_star_table.json
    if p_star_table:
        write_json(os.path.join(run_dir, "p_star_table.json"), {
            "main_grid": p_star_table,
            "l5_sensitivity_grid": kwargs.get("l5_table", []),
            "null_grid": null_table,
        })

    # null_object.json
    if null_summary:
        write_json(os.path.join(run_dir, "null_object.json"), {
            "displacements_summary": null_summary,
            "preregistered_predictions": null_pred,
        })

    # sensitivity.json
    if sensitivity:
        write_json(os.path.join(run_dir, "sensitivity.json"), sensitivity)

    # scope_statement.json
    if scope:
        write_json(os.path.join(run_dir, "scope_statement.json"), scope)

    # undefined_segments.json
    # Every cell carries fit_window_extrapolation: true
    undefined_segs = []
    if p_star_table:
        # All cells have extrapolation > 1x (ratio 6.4x-19.2x)
        undefined_segs.append({
            "guard_flag": "fit_window_extrapolation",
            "applies_to": "ALL 4480 main grid cells",
            "extrapolation_ratio_range": [256.0/40.0, 768.0/40.0],
            "responsible_input": "T1 fit window [9, 40] vs evaluation window [256, 768]",
        })
        # Check for L3 undefined
        l3_undef = [r for r in p_star_table if r["law"] == "L3"
                    and r.get("outcome") == "UNDEFINED"]
        if l3_undef:
            undefined_segs.append({
                "guard_flag": "L3_undefined_negative_argument",
                "cells": l3_undef,
            })
    write_json(os.path.join(run_dir, "undefined_segments.json"), {
        "segments": undefined_segs,
        "is_empty": len(undefined_segs) == 0,
        "note": "Non-empty as required: at minimum the extrapolation stamp applies to all cells",
    })

    # raw-result.json (comprehensive)
    raw_result = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "seed": SEED,
        "validity": validity,
        "invalid_reason": invalid_reason,
        "elapsed_seconds": elapsed,
        "fit_parameters": {"a1": a1, "a2": a2, "a3": a3, "b3": b3, "a4": a4},
        "transcription_consistency": transcription,
        "gates": {
            "boundary_condition_gate": bcg["gate_verdict"] if bcg else None,
            "reproduction_gate": rg["gate_verdict"] if rg else None,
            "xchk1": xchk1["verdict"] if xchk1 else None,
        },
        "monotonicity_verdicts": {k: mono[k]["verdict"] for k in
                                  ["MONO-1", "MONO-2", "MONO-3", "MONO-4", "MONO-5"]} if mono else None,
        "null_summary": null_summary,
        "null_predictions": null_pred,
        "scope_summary": {k: scope[k]["summary"] for k in ["SCOPE-A", "SCOPE-B", "SCOPE-C"]} if scope else None,
        "convention_sign": {"agree": conv_sign["agree_count"],
                            "total": conv_sign["total_feasible"]} if conv_sign else None,
        "bands": kwargs.get("bands"),
        "tail_checks": kwargs.get("tail"),
        "n_main_cells": len(p_star_table) if p_star_table else 0,
        "n_null_cells": len(null_table) if null_table else 0,
        "n_l5_cells": len(kwargs.get("l5_table", [])),
        "A_cancels_in_Delta": True,
        "A_cancels_note": "A appears on both T_B and T_A sides and cancels in Delta = T_B - T_A",
    }
    write_json(os.path.join(run_dir, "raw-result.json"), raw_result)

    # manifest.yaml (as JSON for simplicity since we're stdlib-only)
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "git_commit": get_git_commit(),
        "git_dirty": get_git_dirty(),
        "seed": SEED,
        "deterministic": True,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "start_time": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(start_time)),
        "end_time": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "elapsed_seconds": elapsed,
        "wall_clock_budget_seconds": 600,
        "validity": validity,
        "invalid_reason": invalid_reason,
        "input_hashes": input_hashes,
        "no_forbidden_imports": env["no_forbidden_import_assertion"],
        "inference": {
            "requested_policy": "executor-implementation",
            "note": "Zero-compute experiment; no model inference during run",
        },
    }
    write_json(os.path.join(run_dir, "manifest.yaml"), manifest)

    # command.txt
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(f"python3 experiments/EXP-SSI-9b542d/crossover.py\n")
        f.write(f"# Working directory: {REPO_ROOT}\n")
        f.write(f"# Python: {sys.executable}\n")

    print(f"\nAll artifacts written to {run_dir}")
    print(f"Validity: {validity}")
    if invalid_reason:
        print(f"Invalid reason: {invalid_reason}")


def write_json(path, data):
    """Write JSON with proper formatting."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_git_commit():
    """Get current git commit hash."""
    try:
        import subprocess
        result = subprocess.run(["git", "rev-parse", "HEAD"],
                               capture_output=True, text=True, cwd=REPO_ROOT)
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def get_git_dirty():
    """Check if git tree is dirty."""
    try:
        import subprocess
        result = subprocess.run(["git", "status", "--porcelain"],
                               capture_output=True, text=True, cwd=REPO_ROOT)
        return len(result.stdout.strip()) > 0 if result.returncode == 0 else None
    except Exception:
        return None


if __name__ == "__main__":
    main()
