#!/usr/bin/env python3
"""Charged-cost grid for EXP-XOR-7267e4.

Arm A (exhaustive) vs Arm B (x-oracle MITM) vs Arm D (random-from-F_p MITM
true null), under the frozen charge model of
experiments/EXP-XOR-7267e4/specification.yaml: one field operation = one
E.add evaluation as performed by the frozen harness.toycurve add.

REUSE, NOT REIMPLEMENTATION.  This file does not redefine the curve search,
factor-base construction, or Arm A/B mechanics.  It loads them directly,
byte-verified, from the frozen predecessor:
  experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py
(find_curve, build_factor_base, arm_a_no_oracle, arm_b_x_oracle).

Arm D ("true null": right-half table + Q=|F| queries drawn uniformly at
random from F_p, one per left element, collision-free within the run) is
*mechanically identical* to the frozen full_grid.arm_c_random_predictor --
same table, same query-count-per-left-element structure, same PRNG
collision-avoidance discipline.  That is exactly the control the frozen
XOR spec calls "Arm D" (H-XOR-a227dc's mechanism section; the name traces to
EV-ECDLP-65b004's red-team "Arm D: Random-from-F_p MITM, true null model"
suggestion).  Arm D is therefore implemented as a thin, transparent wrapper
that calls the frozen arm_c_random_predictor UNCHANGED and relabels its
result -- not a reimplementation, and not a fourth "Arm C" data point in the
120-arm-run battery (which is strictly [A, B, D] per the frozen spec's
design_note).

Grid: m=3, primes=[101,103,107,211], b=[0.4,0.5], seeds=[1..5],
arms=[A,B,D] => 4*2*5*3 = 120 arm-runs, 8 (p,b) groups of 5 seeds each.

Produces (into the run directory passed on argv[1]):
  - raw-result.json  (every arm-run record, group aggregates, overall stats)
  - analysis.yaml    (per-cell table, naive-n40 / corrected-n8 statistics,
                       tail check, falsification checks, memory reconciliation)

This script performs measurement only.  It draws no conclusion about
H-XOR-a227dc; it reports the predefined metrics exactly as specified.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import math
import platform
import resource
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# CTRL-BLOB: byte-verify the frozen predecessor before importing anything
# from it.  This is the no-reimplementation gate -- computation proceeds
# only if the file on disk is byte-identical to the hash independently
# recorded in three separate ledger records (EV-ECDLP-65b004's
# artifact_hash_independently_computed_20260807, and the baseline_sha256
# fields of EXP-XOR-62b256 and EXP-XOR-019343's specifications).
# ---------------------------------------------------------------------------

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parent.parent.parent.parent
FROZEN_FULL_GRID_PATH = (
    REPO_ROOT / "experiments" / "EXP-SEMAEV-f48dd1" / "implementation" / "full_grid.py"
)
EXPECTED_FROZEN_SHA256 = (
    "64d682e56e28472987ebd319f6250a09620c566ab7a881701d53acce3300a540"
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_frozen_full_grid() -> Tuple[object, str, bool]:
    actual_sha256 = _sha256_file(FROZEN_FULL_GRID_PATH)
    ctrl_blob_pass = actual_sha256 == EXPECTED_FROZEN_SHA256
    spec = importlib.util.spec_from_file_location(
        "xor_7267e4_frozen_full_grid", FROZEN_FULL_GRID_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # module-level `if __name__ == "__main__"` does not fire
    return module, actual_sha256, ctrl_blob_pass


# ---------------------------------------------------------------------------
# Arm D: thin, transparent wrapper around the frozen arm_c_random_predictor.
# ---------------------------------------------------------------------------

def arm_d_random_null(full_grid_module, E, F: List, m: int, seed: int) -> Dict:
    """Arm D (true null): calls the frozen arm_c_random_predictor UNCHANGED.

    Mechanism match to H-XOR-a227dc's Arm D definition, verified line by
    line against experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py:
      - same right-half table construction (|F|^2 adds);
      - Q = |F| queries, exactly one per left element (matches Arm B's Q);
      - each query value drawn uniformly at random from F_p (unfiltered --
        NOT restricted to on-curve x-coordinates), via a SHA-256-keyed PRNG
        seeded on (seed, P1 coords, counter);
      - collision-avoidance retry loop enforcing all PRNG outputs distinct
        within the run (CTRL-PRNG-NO-COLLISION);
      - candidate verification (2 adds each) only on a query value that
        happens to land in an occupied table bucket (chance collision).
    field_operations returned already equals |F|^2 + 2*candidates_verified,
    i.e. C_D exactly as the frozen spec's charge_model.arm_d_accounting
    defines it -- no additional charge is added here.
    """
    result = full_grid_module.arm_c_random_predictor(E, F, m, seed)
    result["arm"] = "D"
    result["oracle_type"] = "random_from_Fp_true_null"
    return result


# ---------------------------------------------------------------------------
# Memory instrumentation
# ---------------------------------------------------------------------------

def _ru_maxrss_bytes() -> int:
    """Process-wide peak RSS watermark (monotonic, cumulative over process
    lifetime -- NOT isolated per arm-run).  Darwin's getrusage reports
    ru_maxrss in bytes already; Linux reports kilobytes."""
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == "Darwin":
        return int(ru)
    return int(ru) * 1024


def _measure(fn, *args) -> Dict:
    """Run fn(*args), returning wall-clock time and an ISOLATED peak-memory
    measurement.

    tracemalloc.reset_peak() does NOT reset the peak to zero: per the
    Python docs it "set[s] the peak size of memory blocks traced ... to the
    CURRENT size" (bytes already resident -- sympy's imported internals,
    prior cells' not-yet-reclaimed allocations, interpreter bookkeeping --
    are includED, not cleared). A first implementation of this measurement
    read tracemalloc.get_traced_memory()'s post-call peak directly and found
    it dominated by that baseline (~33 MB, roughly IDENTICAL across arms A/
    B/D on the same cell, an obvious tell that it was not measuring each
    arm's own allocation): implied bytes-per-table-entry came out around
    45,000, which is not a plausible cost for a Python tuple-of-int-tuples
    entry. The FIX, applied here and verified against the empirical tell
    (isolated bytes/entry ~77-81 for arms B/D, ~0.6 KB for arm A which
    builds no table -- self-consistent, small, and explicable), is to
    capture the baseline explicitly right after reset_peak() and subtract:
    isolated_peak = post_call_peak - baseline_current_at_reset.  Both the
    raw components and the corrected isolated figure are returned and
    recorded so this correction is fully auditable rather than silently
    applied.
    """
    gc.collect()
    tracemalloc.reset_peak()
    baseline_current, _baseline_peak = tracemalloc.get_traced_memory()
    t0 = time.perf_counter()
    result = fn(*args)
    wall = time.perf_counter() - t0
    _post_current, post_peak_absolute = tracemalloc.get_traced_memory()
    isolated_peak = max(0, post_peak_absolute - baseline_current)
    return {
        "result": result,
        "wall_seconds": wall,
        "tracemalloc_baseline_bytes": baseline_current,
        "tracemalloc_absolute_peak_bytes": post_peak_absolute,
        "tracemalloc_isolated_peak_bytes": isolated_peak,
    }


# ---------------------------------------------------------------------------
# Analytic (modeled) formulas -- see charge_model in specification.yaml.
# ---------------------------------------------------------------------------

def analytic_non_identity_pairs(F_size: int) -> int:
    """T = number of (P2,P3) right-half pairs with P2+P3 != O.

    build_factor_base (frozen, unchanged) always inserts a point's negation
    alongside it (or the point is its own negation at y=0, a 2-torsion
    point, where P+P=O).  Consequently every P2 in F has EXACTLY ONE P3 in F
    with P2+P3=O (the unique group inverse, which is guaranteed present in F
    by construction). So exactly |F| of the |F|^2 right-half pairs sum to O,
    and T = |F|^2 - |F| = |F|*(|F|-1) always, independent of the specific
    curve or prime. This is a structural fact about build_factor_base's
    output, not a per-run measurement, and is used only in the MODELED
    (never the measured) column.
    """
    return F_size * (F_size - 1)


def modeled_C_B(F_size: int, R_B: int) -> float:
    """C_B ~ |F|^2 + 2*R  (specification.yaml preregistered_prediction),
    using the approximation candidates_verified ~ R_B (measured
    candidates_verified may exceed R_B by same-sign false positives; this
    is the MODELED column, not the measured one)."""
    return F_size ** 2 + 2 * R_B


def modeled_C_D(F_size: int, Q: int, p: int) -> float:
    """C_D ~ |F|^2 + 2*(#chance collisions), with
    E[#chance collisions] = Q * (|distinct table keys| / p) * avg_bucket_size
                           = Q * T / p     (the |distinct keys| term cancels
                                            algebraically against avg bucket
                                            size = T / |distinct keys|)
    where T = analytic_non_identity_pairs(F_size)."""
    T = analytic_non_identity_pairs(F_size)
    expected_chance_collisions = Q * T / p
    return F_size ** 2 + 2 * expected_chance_collisions


# ---------------------------------------------------------------------------
# Grid parameters (frozen; do not alter).
# ---------------------------------------------------------------------------

M = 3
PRIMES = [101, 103, 107, 211]
B_VALUES = [0.4, 0.5]
SEEDS = [1, 2, 3, 4, 5]
BUDGET_WALL_PER_RUN_S = 30
BUDGET_TOTAL_WALL_S = 3600

# Small hardcoded Student-t critical-value table (two-sided alpha=0.05),
# matching the table already used by the frozen predecessor's own analysis
# (experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py); a public
# statistical constant, not part of the charged-cost machinery under test.
T_TABLE = {
    3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 15: 2.131, 20: 2.086,
    25: 2.060, 30: 2.042, 39: 2.023, 40: 2.021, 60: 2.000,
    120: 1.980, 1000: 1.962,
}


def t_critical(df: int) -> float:
    if df in T_TABLE:
        return T_TABLE[df]
    nearest = min(T_TABLE.keys(), key=lambda k: abs(k - df))
    return T_TABLE[nearest]


def mean_std_ci(values: List[float]) -> Dict:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": None, "std": None, "se": None, "ci_95": [None, None], "df": None, "t_critical": None}
    mean = statistics.mean(values)
    std = statistics.stdev(values) if n > 1 else 0.0
    se = std / math.sqrt(n) if n > 0 else 0.0
    df = n - 1
    tcrit = t_critical(df) if df > 0 else None
    if tcrit is not None:
        ci = [mean - tcrit * se, mean + tcrit * se]
    else:
        ci = [mean, mean]
    return {"n": n, "mean": mean, "std": std, "se": se, "df": df, "t_critical": tcrit, "ci_95": ci}


# ---------------------------------------------------------------------------
# Per-instance (p, b, seed) execution
# ---------------------------------------------------------------------------

def run_instance(full_grid_module, E, F: List, B_size: int, N: int, p: int, b: float, seed: int) -> Dict:
    F_size = len(F)

    m_A = _measure(full_grid_module.arm_a_no_oracle, E, F, M)
    result_A = m_A["result"]
    result_A["arm"] = "A"
    result_A["oracle_type"] = "none"

    m_B = _measure(full_grid_module.arm_b_x_oracle, E, F, M)
    result_B = m_B["result"]
    result_B["arm"] = "B"
    result_B["oracle_type"] = "x_coordinate"

    m_D = _measure(arm_d_random_null, full_grid_module, E, F, M, seed)
    result_D = m_D["result"]

    wall_A, wall_B, wall_D = m_A["wall_seconds"], m_B["wall_seconds"], m_D["wall_seconds"]
    ru_maxrss_after = _ru_maxrss_bytes()

    C_A = result_A["field_operations"]
    C_B = result_B["field_operations"]
    C_D = result_D["field_operations"]
    R_A = result_A["relations_found"]
    R_B = result_B["relations_found"]
    R_D = result_D["relations_found"]
    Q_B = result_B["oracle_queries"]
    Q_D = result_D["oracle_queries"]

    # Cross-checks of the measured field_operations against the charge
    # model's own closed-form construction (self-consistency, not a new
    # measurement source): these must hold by construction of the frozen
    # functions, and a mismatch would indicate the frozen file's mechanics
    # no longer match the charge_model's stated formulas.
    expected_C_A_exact = 2 * (F_size ** 3)
    expected_C_B_exact = F_size ** 2 + 2 * result_B["candidates_verified"]
    expected_C_D_exact = F_size ** 2 + 2 * result_D["candidates_verified"]

    control_checks = {
        "CTRL-QUERY-COUNT": Q_B == Q_D,
        "CTRL-PRNG-NO-COLLISION": bool(result_D.get("prng_collision_free", False)),
        "CTRL-YIELD-REF": R_B == R_A,
    }

    budget_checks = {
        "arm_A_within_30s": wall_A <= BUDGET_WALL_PER_RUN_S,
        "arm_B_within_30s": wall_B <= BUDGET_WALL_PER_RUN_S,
        "arm_D_within_30s": wall_D <= BUDGET_WALL_PER_RUN_S,
    }

    hash_table_probes = {
        # "Probing" = table lookups during the query phase (one dict "in"
        # check per query, hit or miss); construction-phase inserts are
        # reported separately as right_half_pairs (an exact count, since
        # every (P2,P3) iteration is a loop pass, though only T=|F|^2-|F|
        # of them reach the dict-insert statement -- see
        # analytic_non_identity_pairs).
        "B_lookup_probes": Q_B,
        "D_lookup_probes": Q_D,
        "B_construction_pairs_iterated": result_B["right_half_pairs"],
        "D_construction_pairs_iterated": result_D["right_half_pairs"],
    }

    R_D_over_R_B_instance = (R_D / R_B) if R_B else None

    return {
        "p": p,
        "b": b,
        "seed": seed,
        "B_size": B_size,
        "N": N,
        "curve": {"a": E.a, "b": E.b},
        "factor_base_size": F_size,
        "arms": {"A": result_A, "B": result_B, "D": result_D},
        "wall_clock_seconds_wrapper": {"A": wall_A, "B": wall_B, "D": wall_D},
        "tracemalloc_peak_bytes": {
            "A": m_A["tracemalloc_isolated_peak_bytes"],
            "B": m_B["tracemalloc_isolated_peak_bytes"],
            "D": m_D["tracemalloc_isolated_peak_bytes"],
        },
        "tracemalloc_raw": {
            "A": {"baseline_bytes": m_A["tracemalloc_baseline_bytes"], "absolute_peak_bytes": m_A["tracemalloc_absolute_peak_bytes"]},
            "B": {"baseline_bytes": m_B["tracemalloc_baseline_bytes"], "absolute_peak_bytes": m_B["tracemalloc_absolute_peak_bytes"]},
            "D": {"baseline_bytes": m_D["tracemalloc_baseline_bytes"], "absolute_peak_bytes": m_D["tracemalloc_absolute_peak_bytes"]},
        },
        "process_ru_maxrss_bytes_after_instance": ru_maxrss_after,
        "derived": {
            "C_A": C_A, "C_B": C_B, "C_D": C_D,
            "R_A": R_A, "R_B": R_B, "R_D": R_D,
            "R_D_over_R_B": R_D_over_R_B_instance,
            "C_B_modeled": modeled_C_B(F_size, R_B),
            "C_D_modeled": modeled_C_D(F_size, Q_D, p),
            "C_A_self_consistent": C_A == expected_C_A_exact,
            "C_B_self_consistent": C_B == expected_C_B_exact,
            "C_D_self_consistent": C_D == expected_C_D_exact,
            "analytic_F2": F_size ** 2,
            "analytic_T_non_identity_pairs": analytic_non_identity_pairs(F_size),
        },
        "hash_table_probes": hash_table_probes,
        "control_checks": control_checks,
        "budget_checks": budget_checks,
        "all_controls_pass": all(control_checks.values()),
        "status": "completed" if all(control_checks.values()) else "control_check_failed",
    }


# ---------------------------------------------------------------------------
# Grid driver
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: charged_grid.py <output_run_dir>", file=sys.stderr)
        return 2
    output_dir = Path(sys.argv[1]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    tracemalloc.start()
    grid_t0 = time.perf_counter()

    print("=" * 78)
    print("EXP-XOR-7267e4 charged-cost grid")
    print(f"m={M}, primes={PRIMES}, b={B_VALUES}, seeds={SEEDS}, arms=[A,B,D]")
    print(f"Total: {len(PRIMES)}x{len(B_VALUES)}x{len(SEEDS)} = "
          f"{len(PRIMES)*len(B_VALUES)*len(SEEDS)} instances x 3 arms = "
          f"{len(PRIMES)*len(B_VALUES)*len(SEEDS)*3} arm-runs")
    print("=" * 78)

    full_grid_module, actual_sha256, ctrl_blob_pass = load_frozen_full_grid()
    print(f"\nCTRL-BLOB: frozen predecessor {FROZEN_FULL_GRID_PATH}")
    print(f"  expected sha256: {EXPECTED_FROZEN_SHA256}")
    print(f"  actual   sha256: {actual_sha256}")
    print(f"  CTRL-BLOB pass:  {ctrl_blob_pass}")

    result_payload = {
        "experiment_id": "EXP-XOR-7267e4",
        "run_id": "RUN-XOR-7267e4-grid",
        "hypothesis_id": "H-XOR-a227dc",
        "parameters": {"m": M, "primes": PRIMES, "b_values": B_VALUES, "seeds": SEEDS, "arms": ["A", "B", "D"]},
        "ctrl_blob": {
            "frozen_path": str(FROZEN_FULL_GRID_PATH.relative_to(REPO_ROOT)),
            "expected_sha256": EXPECTED_FROZEN_SHA256,
            "actual_sha256": actual_sha256,
            "pass": ctrl_blob_pass,
        },
    }

    if not ctrl_blob_pass:
        print("\n*** CTRL-BLOB FAILED: frozen predecessor hash mismatch. Aborting"
              " computation -- no scientific measurement is meaningful against a"
              " modified machinery file. ***")
        result_payload["aborted"] = True
        result_payload["abort_reason"] = "CTRL-BLOB mismatch"
        result_payload["total_wall_clock_seconds"] = round(time.perf_counter() - grid_t0, 4)
        with open(output_dir / "raw-result.json", "w") as f:
            json.dump(result_payload, f, indent=2)
        return 1

    instances: List[Dict] = []
    groups: List[Dict] = []
    early_exit = {"triggered": False, "detail": None}
    group_index = 0

    for p in PRIMES:
        print(f"\nFinding curve for p={p} ...")
        E = full_grid_module.find_curve(p)
        N = E.order()
        print(f"  curve y^2 = x^3 + {E.a}x + {E.b} over F_{p}, order N={N}")

        for b in B_VALUES:
            group_index += 1
            B_size = int(math.floor(p ** b))
            print(f"\n--- group {group_index}/8: p={p} b={b} (B_size={B_size}) ---")

            F, x_coords = full_grid_module.build_factor_base(E, B_size)
            F_size = len(F)

            group_instances = []
            for seed in SEEDS:
                t0 = time.perf_counter()
                try:
                    rec = run_instance(full_grid_module, E, F, B_size, N, p, b, seed)
                    rec["factor_base_x_coords"] = x_coords
                    rec["wall_clock_total"] = round(time.perf_counter() - t0, 6)
                except Exception as exc:  # pragma: no cover - defensive
                    rec = {
                        "p": p, "b": b, "seed": seed, "B_size": B_size,
                        "status": "error", "error": str(exc), "error_type": type(exc).__name__,
                        "wall_clock_total": round(time.perf_counter() - t0, 6),
                        "arms": {}, "control_checks": {}, "all_controls_pass": False,
                    }
                    print(f"  seed={seed}: *** ERROR: {exc} ***")
                group_instances.append(rec)
                instances.append(rec)
                if rec.get("status") == "completed":
                    d = rec["derived"]
                    print(f"  seed={seed}: C_A={d['C_A']} C_B={d['C_B']} C_D={d['C_D']}  "
                          f"R_A={d['R_A']} R_B={d['R_B']} R_D={d['R_D']}  "
                          f"controls={rec['control_checks']}")
                else:
                    print(f"  seed={seed}: status={rec.get('status')}")

            valid_group_instances = [r for r in group_instances if r.get("status") == "completed"]
            if valid_group_instances:
                C_A_vals = [r["derived"]["C_A"] for r in valid_group_instances]
                C_B_vals = [r["derived"]["C_B"] for r in valid_group_instances]
                C_D_vals = [r["derived"]["C_D"] for r in valid_group_instances]
                R_A_vals = [r["derived"]["R_A"] for r in valid_group_instances]
                R_B_vals = [r["derived"]["R_B"] for r in valid_group_instances]
                R_D_vals = [r["derived"]["R_D"] for r in valid_group_instances]
                group_C_A = statistics.mean(C_A_vals)
                group_C_B = statistics.mean(C_B_vals)
                group_C_D = statistics.mean(C_D_vals)
                group_R_A = statistics.mean(R_A_vals)
                group_R_B = statistics.mean(R_B_vals)
                group_R_D = statistics.mean(R_D_vals)
                group_R_D_over_R_B = (group_R_D / group_R_B) if group_R_B else None

                group_record = {
                    "group_index": group_index,
                    "p": p, "b": b, "F_size": F_size, "B_size": B_size, "N": N,
                    "n_valid_seeds": len(valid_group_instances),
                    "C_A_mean": group_C_A, "C_B_mean": group_C_B, "C_D_mean": group_C_D,
                    "C_A_std": statistics.stdev(C_A_vals) if len(C_A_vals) > 1 else 0.0,
                    "C_B_std": statistics.stdev(C_B_vals) if len(C_B_vals) > 1 else 0.0,
                    "C_D_std": statistics.stdev(C_D_vals) if len(C_D_vals) > 1 else 0.0,
                    "R_A_mean": group_R_A, "R_B_mean": group_R_B, "R_D_mean": group_R_D,
                    "R_D_over_R_B": group_R_D_over_R_B,
                    "ranking_C_A_gt_C_D_gt_C_B": (group_C_A > group_C_D > group_C_B),
                    "F1_tripped_C_B_ge_C_A": group_C_B >= group_C_A,
                    "F2_tripped_C_B_ge_C_D": group_C_B >= group_C_D,
                    "F3_tripped_R_D_over_R_B_ge_0_95": (group_R_D_over_R_B is not None and group_R_D_over_R_B >= 0.95),
                    "tracemalloc_peak_bytes_mean": {
                        arm: statistics.mean([r["tracemalloc_peak_bytes"][arm] for r in valid_group_instances])
                        for arm in ("A", "B", "D")
                    },
                    "analytic_F2": F_size ** 2,
                }
            else:
                group_record = {
                    "group_index": group_index, "p": p, "b": b, "F_size": F_size,
                    "B_size": B_size, "N": N, "n_valid_seeds": 0,
                    "status": "no_valid_seeds",
                }
            groups.append(group_record)

            # Early-exit stopping rule: over the first 4 (p,b) groups, if
            # C_D <= C_B in >= 2 of them, stop and escalate (F1 of the
            # falsification criteria on prediction 1 -- oracle not
            # load-bearing). Evaluated on cell (group) means, matching the
            # primary metric's own "mean over seeds" definition.
            if group_index <= 4 and "C_D_mean" in group_record:
                tripped_so_far = sum(
                    1 for g in groups[:4]
                    if "C_D_mean" in g and g["C_D_mean"] <= g["C_B_mean"]
                )
                if group_index == 4 and tripped_so_far >= 2 and not early_exit["triggered"]:
                    early_exit["triggered"] = True
                    early_exit["detail"] = (
                        f"{tripped_so_far} of the first 4 groups show C_D_mean <= C_B_mean"
                    )
                    print(f"\n*** EARLY-EXIT STOPPING RULE TRIGGERED: {early_exit['detail']} ***")

        if early_exit["triggered"]:
            break

    total_elapsed = time.perf_counter() - grid_t0
    process_peak_rss_bytes = _ru_maxrss_bytes()

    # -----------------------------------------------------------------------
    # Overall statistics: naive n (all valid per-seed instances) vs
    # corrected n=8 (group means).  Arms A and B are deterministic given the
    # curve (seed-independent) -- exactly as in the frozen predecessor's own
    # non-independence note -- so the naive n is pseudo-replicated for A/B
    # (and nested/nonindependent-across-groups for D). n=8 group means are
    # the corrected statistic per DEC-20260808-6a7ac4 / EV-ECDLP-65b004's
    # discipline.
    # -----------------------------------------------------------------------
    valid_instances = [r for r in instances if r.get("status") == "completed"]
    naive_n = len(valid_instances)

    def naive_stats(key: str) -> Dict:
        vals = [r["derived"][key] for r in valid_instances]
        return mean_std_ci(vals)

    def group_stats(key_mean: str) -> Dict:
        vals = [g[key_mean] for g in groups if key_mean in g]
        return mean_std_ci(vals)

    design_groups_planned = 8
    design_shortfall_note = (
        f"Design called for {design_groups_planned} independent (p,b) groups; "
        f"only {len(groups)} were REACHED before the frozen early-exit "
        f"stopping rule triggered (see early_exit). The label "
        f"'corrected_n8_groups' names the STATISTICAL METHODOLOGY from "
        f"specification.yaml's replication discipline (group-mean correction "
        f"for A/B pseudo-replication), not a claim that 8 groups were "
        f"observed -- the actual n is in the 'n' field alongside every "
        f"statistic below."
        if len(groups) < design_groups_planned else
        f"All {design_groups_planned} planned independent (p,b) groups were reached."
    )

    overall = {
        "naive_n": {
            "n": naive_n,
            "pseudo_replication_note": (
                "Arms A and B are deterministic given the curve; the 5 seed "
                "replicates within each (p,b) group repeat the identical A/B "
                "values 5x. This naive pooled statistic is INVALID for C_A, "
                "C_B, R_A, R_B due to pseudo-replication and is reported for "
                "transparency only, exactly as EV-ECDLP-65b004 / "
                "DEC-20260808-6a7ac4 require. Arm D varies by seed but is "
                "still nested within (p,b) groups, not independent draws. "
                + design_shortfall_note
            ),
            "C_A": naive_stats("C_A"), "C_B": naive_stats("C_B"), "C_D": naive_stats("C_D"),
            "R_A": naive_stats("R_A"), "R_B": naive_stats("R_B"), "R_D": naive_stats("R_D"),
        },
        "corrected_n8_groups": {
            "n": len(groups),
            "design_note": design_shortfall_note,
            "C_A": group_stats("C_A_mean"), "C_B": group_stats("C_B_mean"), "C_D": group_stats("C_D_mean"),
            "R_A": group_stats("R_A_mean"), "R_B": group_stats("R_B_mean"), "R_D": group_stats("R_D_mean"),
            "R_D_over_R_B": group_stats("R_D_over_R_B"),
        },
    }

    # Falsification checks, per group and overall (measured, not interpreted).
    f1_cells = [g for g in groups if g.get("F1_tripped_C_B_ge_C_A")]
    f2_cells = [g for g in groups if g.get("F2_tripped_C_B_ge_C_D")]
    f3_cells = [g for g in groups if g.get("F3_tripped_R_D_over_R_B_ge_0_95")]
    ranking_holds_cells = [g for g in groups if g.get("ranking_C_A_gt_C_D_gt_C_B")]

    # Tail check: ranking stability at smallest (p=101,b=0.4) and largest
    # (p=211,b=0.5) cells.
    smallest_cell = next((g for g in groups if g["p"] == 101 and g["b"] == 0.4), None)
    largest_cell = next((g for g in groups if g["p"] == 211 and g["b"] == 0.5), None)
    tail_check = {
        "smallest_cell_p101_b0.4_ranking_holds": smallest_cell.get("ranking_C_A_gt_C_D_gt_C_B") if smallest_cell else None,
        "smallest_cell_reached": smallest_cell is not None,
        "largest_cell_p211_b0.5_ranking_holds": largest_cell.get("ranking_C_A_gt_C_D_gt_C_B") if largest_cell else None,
        "largest_cell_reached": largest_cell is not None,
        "note": (
            "largest_cell_p211_b0.5 was NOT reached before the early-exit "
            "stopping rule triggered; its ranking_holds value is null, not "
            "measured as False -- absence of data, not a negative result, "
            "for that specific cell." if largest_cell is None else
            "both tail cells were reached."
        ),
    }

    # Memory reconciliation: implied bytes-per-analytic-F^2-entry, per group,
    # for arms B and D (the arms that build the |F|^2 table); flag >2x
    # cross-group deviation.
    memory_reconciliation = []
    for g in groups:
        if "tracemalloc_peak_bytes_mean" not in g:
            continue
        F2 = g["analytic_F2"]
        row = {"p": g["p"], "b": g["b"], "F_size": g["F_size"], "analytic_F2": F2}
        for arm in ("B", "D"):
            peak = g["tracemalloc_peak_bytes_mean"][arm]
            row[f"tracemalloc_peak_bytes_mean_{arm}"] = peak
            row[f"implied_bytes_per_F2_entry_{arm}"] = (peak / F2) if F2 else None
        memory_reconciliation.append(row)

    def _discrepancy_flag(field: str) -> Dict:
        ratios = [r[field] for r in memory_reconciliation if r.get(field) is not None and r[field] > 0]
        if len(ratios) < 2:
            return {"flag": False, "note": "insufficient groups to compare"}
        lo, hi = min(ratios), max(ratios)
        ratio_of_ratios = (hi / lo) if lo > 0 else None
        return {
            "min_bytes_per_entry": lo, "max_bytes_per_entry": hi,
            "max_over_min_ratio": ratio_of_ratios,
            "flag_gt_2x": (ratio_of_ratios is not None and ratio_of_ratios > 2.0),
        }

    memory_reconciliation_summary = {
        "arm_B": _discrepancy_flag("implied_bytes_per_F2_entry_B"),
        "arm_D": _discrepancy_flag("implied_bytes_per_F2_entry_D"),
        "process_peak_rss_bytes_whole_run": process_peak_rss_bytes,
        "process_peak_rss_bytes_note": (
            "Whole-process, cumulative, monotonic-nondecreasing watermark "
            "(resource.getrusage RUSAGE_SELF ru_maxrss) captured once at the "
            "end of the full grid run -- NOT isolated per arm/cell. The "
            "per-cell reconciliation above instead uses tracemalloc peak "
            "(isolated per arm-run via reset_peak()), which is the more "
            "precise instrument for per-cell |F|^2-table reconciliation."
        ),
    }

    result_payload.update({
        "instances": instances,
        "groups": groups,
        "overall_statistics": overall,
        "early_exit": early_exit,
        "falsification_checks": {
            "F1_cells_tripped": [{"p": g["p"], "b": g["b"]} for g in f1_cells],
            "F2_cells_tripped": [{"p": g["p"], "b": g["b"]} for g in f2_cells],
            "F3_cells_tripped": [{"p": g["p"], "b": g["b"]} for g in f3_cells],
            "cells_reached": len(groups),
            "cells_planned": 8,
            "ranking_C_A_gt_C_D_gt_C_B_holds_count": len(ranking_holds_cells),
            "ranking_holds_note": (
                f"Ranking held in {len(ranking_holds_cells)} of {len(groups)} "
                f"REACHED (p,b) cells (plan called for 8; "
                f"{8 - len(groups)} cell(s) not reached -- see early_exit)."
                if len(groups) < 8 else
                f"Ranking held in {len(ranking_holds_cells)} of {len(groups)} cells (full grid reached)."
            ),
        },
        "tail_check": tail_check,
        "memory_reconciliation": memory_reconciliation,
        "memory_reconciliation_summary": memory_reconciliation_summary,
        "total_wall_clock_seconds": round(total_elapsed, 4),
        "total_arm_runs": len(instances) * 3,
        "total_instances": len(instances),
        "invalid_instances": len(instances) - naive_n,
        "budget": {
            "wall_clock_seconds_per_run": BUDGET_WALL_PER_RUN_S,
            "total_wall_clock_seconds_budget": BUDGET_TOTAL_WALL_S,
            "total_wall_clock_seconds_used": round(total_elapsed, 4),
            "within_total_budget": total_elapsed <= BUDGET_TOTAL_WALL_S,
        },
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })

    raw_result_path = output_dir / "raw-result.json"
    with open(raw_result_path, "w") as f:
        json.dump(result_payload, f, indent=2)
    print(f"\nRaw result written to: {raw_result_path}")

    # -----------------------------------------------------------------------
    # analysis.yaml
    # -----------------------------------------------------------------------
    lines = [
        "analysis:",
        "  experiment_id: EXP-XOR-7267e4",
        "  run_id: RUN-XOR-7267e4-grid",
        "  hypothesis_id: H-XOR-a227dc",
        f"  timestamp: {result_payload['timestamp']}",
        f"  total_instances: {len(instances)}",
        f"  total_arm_runs: {len(instances) * 3}",
        f"  valid_instances: {naive_n}",
        f"  invalid_instances: {len(instances) - naive_n}",
        f"  total_wall_clock_seconds: {round(total_elapsed, 4)}",
        f"  early_exit_triggered: {early_exit['triggered']}",
    ]
    if early_exit["triggered"]:
        lines.append(f"  early_exit_detail: \"{early_exit['detail']}\"")
    lines += [
        "",
        "  ctrl_blob:",
        f"    pass: {ctrl_blob_pass}",
        f"    expected_sha256: {EXPECTED_FROZEN_SHA256}",
        f"    actual_sha256: {actual_sha256}",
        "",
        "  per_cell_results:",
    ]
    for g in groups:
        if "C_A_mean" not in g:
            lines.append(f"    - p: {g['p']}")
            lines.append(f"      b: {g['b']}")
            lines.append(f"      status: {g.get('status', 'unknown')}")
            continue
        lines += [
            f"    - p: {g['p']}",
            f"      b: {g['b']}",
            f"      F_size: {g['F_size']}",
            f"      B_size: {g['B_size']}",
            f"      N: {g['N']}",
            f"      n_valid_seeds: {g['n_valid_seeds']}",
            "      measured:",
            f"        C_A_mean: {round(g['C_A_mean'], 6)}",
            f"        C_B_mean: {round(g['C_B_mean'], 6)}",
            f"        C_D_mean: {round(g['C_D_mean'], 6)}",
            f"        C_D_std: {round(g['C_D_std'], 6)}",
            f"        R_A_mean: {round(g['R_A_mean'], 6)}",
            f"        R_B_mean: {round(g['R_B_mean'], 6)}",
            f"        R_D_mean: {round(g['R_D_mean'], 6)}",
            f"        R_D_over_R_B: {round(g['R_D_over_R_B'], 8) if g['R_D_over_R_B'] is not None else 'null'}",
            f"      ranking_C_A_gt_C_D_gt_C_B: {g['ranking_C_A_gt_C_D_gt_C_B']}",
            f"      F1_tripped_C_B_ge_C_A: {g['F1_tripped_C_B_ge_C_A']}",
            f"      F2_tripped_C_B_ge_C_D: {g['F2_tripped_C_B_ge_C_D']}",
            f"      F3_tripped_R_D_over_R_B_ge_0.95: {g['F3_tripped_R_D_over_R_B_ge_0_95']}",
            "      memory_tracemalloc_peak_bytes_mean:",
            f"        A: {round(g['tracemalloc_peak_bytes_mean']['A'], 2)}",
            f"        B: {round(g['tracemalloc_peak_bytes_mean']['B'], 2)}",
            f"        D: {round(g['tracemalloc_peak_bytes_mean']['D'], 2)}",
            f"      analytic_F2: {g['analytic_F2']}",
        ]

    def _fmt_stats_block(indent: str, stats: Dict) -> List[str]:
        out = [f"{indent}n: {stats['n']}"]
        if stats["n"]:
            out += [
                f"{indent}mean: {round(stats['mean'], 6)}",
                f"{indent}std: {round(stats['std'], 6)}",
                f"{indent}se: {round(stats['se'], 6)}",
                f"{indent}df: {stats['df']}",
                f"{indent}t_critical: {stats['t_critical']}",
                f"{indent}ci_95: [{round(stats['ci_95'][0], 6)}, {round(stats['ci_95'][1], 6)}]",
            ]
        return out

    lines += [
        "", "  overall_statistics:",
        f"    design_note: \"{design_shortfall_note}\"",
        "    naive_n:", f"      n: {overall['naive_n']['n']}",
    ]
    for key in ("C_A", "C_B", "C_D", "R_A", "R_B", "R_D"):
        lines.append(f"      {key}:")
        lines += _fmt_stats_block("        ", overall["naive_n"][key])
    lines += ["    corrected_n8_groups:", f"      n: {overall['corrected_n8_groups']['n']}"]
    for key in ("C_A", "C_B", "C_D", "R_A", "R_B", "R_D", "R_D_over_R_B"):
        lines.append(f"      {key}:")
        lines += _fmt_stats_block("        ", overall["corrected_n8_groups"][key])

    lines += [
        "",
        "  falsification_checks:",
        f"    cells_reached: {len(groups)}",
        f"    cells_planned: 8",
        f"    F1_cells_tripped_count: {len(f1_cells)}",
        f"    F2_cells_tripped_count: {len(f2_cells)}",
        f"    F3_cells_tripped_count: {len(f3_cells)}",
        f"    ranking_C_A_gt_C_D_gt_C_B_holds_count: {len(ranking_holds_cells)}",
        f"    ranking_holds_note: \"held in {len(ranking_holds_cells)} of {len(groups)} REACHED cells (plan: 8)\"",
        "",
        "  tail_check:",
        f"    smallest_cell_p101_b0.4_ranking_holds: {tail_check['smallest_cell_p101_b0.4_ranking_holds']}",
        f"    smallest_cell_reached: {tail_check['smallest_cell_reached']}",
        f"    largest_cell_p211_b0.5_ranking_holds: {tail_check['largest_cell_p211_b0.5_ranking_holds']}",
        f"    largest_cell_reached: {tail_check['largest_cell_reached']}",
        f"    note: \"{tail_check['note']}\"",
        "",
        "  memory_reconciliation_summary:",
        f"    process_peak_rss_bytes_whole_run: {memory_reconciliation_summary['process_peak_rss_bytes_whole_run']}",
        "    arm_B:",
    ]
    for k, v in memory_reconciliation_summary["arm_B"].items():
        lines.append(f"      {k}: {v}")
    lines.append("    arm_D:")
    for k, v in memory_reconciliation_summary["arm_D"].items():
        lines.append(f"      {k}: {v}")

    lines += ["", "  controls_summary:"]
    for ctrl in ("CTRL-QUERY-COUNT", "CTRL-PRNG-NO-COLLISION", "CTRL-YIELD-REF"):
        all_pass = all(r["control_checks"].get(ctrl, False) for r in valid_instances)
        lines.append(f"    {ctrl}: {all_pass}")
    lines.append(f"    CTRL-BLOB: {ctrl_blob_pass}")

    analysis_path = output_dir / "analysis.yaml"
    with open(analysis_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Analysis written to: {analysis_path}")

    print("\n" + "=" * 78)
    print(f"Grid complete. Instances: {len(instances)}  Valid: {naive_n}  "
          f"Wall: {total_elapsed:.4f}s  Early-exit: {early_exit['triggered']}")
    print("=" * 78)

    return 0 if naive_n == len(instances) else 1


if __name__ == "__main__":
    sys.exit(main())
