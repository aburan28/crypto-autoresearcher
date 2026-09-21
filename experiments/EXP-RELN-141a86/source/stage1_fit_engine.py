"""
Stage-1 fitting/scoring engine for EXP-RELN-141a86 (TASK-20260907-8fd098).

Extends grammar_engine.py (canonicalize / node_count / numeric_fingerprint,
UNCHANGED) with the numeric machinery Stage 1 needs that Stage 0 did not:
fitting <=2 free CONST leaves of an ENUMERATED expression against REAL
measured (Delta, E_3, ...) data by weighted least squares (weight =
1/null_sd^2, per specification.yaml frozen_pipeline.secondary_engine
"loss = squared error weighted by 1/null_sd^2 per cell", applied here to
BOTH engines' fit objective since the primary engine's own constant_fitting
clause specifies least squares without fixing a weighting -- using the same
weighting as the secondary engine keeps the two comparable, a choice
recorded here as a protocol detail, not a frozen contract term), and
computing the held-out error metric (RMS in null SE over the 2^20 rung)
exactly as specification.yaml metrics.primary defines it.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import grammar_engine as ge

Expr = ge.Expr


def const_placeholders(expr: Expr) -> int:
    tag = expr[0]
    if tag == "CONST":
        return 1
    if tag in ("leaf", "const"):
        return 0
    if tag in ge.UNARY_OPS:
        return const_placeholders(expr[1])
    if tag in ge.BINARY_OPS:
        return const_placeholders(expr[1]) + const_placeholders(expr[2])
    raise ValueError(tag)


def eval_expr(expr: Expr, env: Dict[str, float], const_values: Sequence[float]) -> Optional[float]:
    """Pure-float evaluation (no Fraction machinery -- Stage 1 fits real-
    valued measured statistics, never the exact-rational recovery path of
    recovery_check.py). Returns None on any domain failure (log of <=0,
    division by 0, non-integer binomial args, overflow) -- a None-valued
    row is EXCLUDED from the fit and reported, never coerced to 0."""
    idx = [0]

    def _ev(e):
        tag = e[0]
        if tag == "leaf":
            return float(env[e[1]])
        if tag == "const":
            return float(e[1])
        if tag == "CONST":
            v = const_values[idx[0]]
            idx[0] += 1
            return float(v)
        if tag in ge.UNARY_OPS:
            v = _ev(e[1])
            if v is None:
                return None
            try:
                if tag == "log":
                    return math.log(v) if v > 0 else None
                if tag == "exp":
                    return math.exp(v)
                if tag == "floor":
                    return math.floor(v)
                if tag == "ceil":
                    return math.ceil(v)
            except (ValueError, OverflowError):
                return None
        if tag in ge.BINARY_OPS:
            a = _ev(e[1])
            b = _ev(e[2])
            if a is None or b is None:
                return None
            try:
                if tag == "add":
                    return a + b
                if tag == "sub":
                    return a - b
                if tag == "mul":
                    return a * b
                if tag == "div":
                    return a / b if b != 0 else None
                if tag == "pow":
                    if a == 0 and b < 0:
                        return None
                    if a < 0 and b != int(b):
                        return None
                    r = a ** b
                    return None if isinstance(r, complex) else r
                if tag == "binomial":
                    if int(a) != a or int(b) != b or a < 0 or b < 0 or b > a or a > 1e7:
                        return None
                    return float(math.comb(int(a), int(b)))
            except (ValueError, OverflowError, ZeroDivisionError):
                return None
        raise ValueError(tag)

    try:
        return _ev(expr)
    except RecursionError:
        return None


def _weighted_sse(expr: Expr, rows: List[Dict], stat_key: str, const_values: Sequence[float]) -> Optional[float]:
    """Same overflow hazard as held_out_error (see that function's docstring,
    this dispatch's follow-up): a candidate expression can predict a
    genuinely huge but finite value against a row with a tiny null_sd, and
    `x ** 2` raises OverflowError on the float-range crossing where `x * x`
    silently (and correctly, per IEEE) returns inf. Squaring via `*` here
    for the same reason -- this is the grid-search fit objective, called
    ~thousands of times per level, so it must never raise on a legitimately
    bad candidate; a bad candidate is exactly what a large/inf SSE already
    correctly represents."""
    total = 0.0
    n_used = 0
    for row in rows:
        pred = eval_expr(expr, row["leaves"], const_values)
        if pred is None:
            return None
        obs = row["statistics"].get(stat_key)
        sd = row["null_sd"].get(stat_key)
        if obs is None or sd is None or sd <= 0:
            continue
        term = (pred - obs) / sd  # `/` overflows to inf silently, never raises
        total += term * term  # `*` overflows to inf silently (unlike `**`), never raises
        n_used += 1
    if n_used == 0:
        return None
    return total


def _coarse_to_fine_1d(f, lo: float, hi: float, grid_iterations: int, grid_points: int,
                        start: Optional[float] = None) -> Tuple[float, float]:
    """1-D deterministic coarse-to-fine grid search minimizing f(c) -> sse
    (or None to mean 'not evaluable'). Returns (best_c, best_sse); best_sse
    is +inf if f was never evaluable anywhere tried."""
    best_c = start if start is not None else 0.0
    best_sse = f(best_c)
    if best_sse is None:
        best_sse = float("inf")
    for _ in range(grid_iterations):
        step = (hi - lo) / (grid_points - 1)
        for i in range(grid_points):
            c = lo + i * step
            sse = f(c)
            if sse is not None and sse < best_sse:
                best_sse, best_c = sse, c
        span = max(step * 2, 1e-12)
        lo, hi = best_c - span, best_c + span
    return best_c, best_sse


def fit_constants(expr: Expr, rows: List[Dict], stat_key: str,
                   grid_iterations: int = 16, grid_points: int = 15,
                   restarts_2d: Sequence[float] = (-8.0, -1.0, 0.0, 1.0, 2.0, 3.0, 8.0),
                   rounds_2d: int = 6, grid_iterations_2d: int = 6
                   ) -> Tuple[Optional[List[float]], Optional[float]]:
    """
    Deterministic coarse-to-fine grid search (no scipy/numpy dependency) for
    the <=2 free CONST leaves of `expr`, minimizing the null-SE-weighted SSE
    on `rows` (training rows only -- caller is responsible for passing only
    non-held-out rows). Returns (const_values, weighted_sse) or (None, None)
    if the expression is never evaluable on this table.

    For 2 free constants, a naive joint coarse-to-fine grid was found (self-
    test, this dispatch) to get stuck in a local basin and MISS the true
    global optimum (e.g. failed to recover INV-A1's own two tied constants
    from noiseless synthetic data). Replaced by deterministic alternating
    coordinate descent (fix c1, 1-D-optimize c0, then fix c0, 1-D-optimize
    c1, repeated) from several fixed starting points (restarts_2d), keeping
    the best result across all starts -- this is the standard remedy for a
    non-convex joint objective and is still fully deterministic (no random
    seed involved, same result on every re-run).
    """
    n_const = const_placeholders(expr)
    if n_const == 0:
        sse = _weighted_sse(expr, rows, stat_key, [])
        return ([], sse) if sse is not None else (None, None)
    if n_const > 2:
        return None, None

    if n_const == 1:
        c0, sse = _coarse_to_fine_1d(
            lambda c: _weighted_sse(expr, rows, stat_key, [c]),
            -64.0, 64.0, grid_iterations, grid_points)
        return ([c0], sse) if sse != float("inf") else (None, None)

    # n_const == 2: alternating coordinate descent from multiple starts.
    best_c: Optional[List[float]] = None
    best_sse = float("inf")
    for start0 in restarts_2d:
        c = [start0, 0.0]
        for _round in range(rounds_2d):
            c0, s0 = _coarse_to_fine_1d(
                lambda x: _weighted_sse(expr, rows, stat_key, [x, c[1]]),
                -64.0, 64.0, grid_iterations_2d, grid_points, start=c[0])
            c[0] = c0
            c1, s1 = _coarse_to_fine_1d(
                lambda x: _weighted_sse(expr, rows, stat_key, [c[0], x]),
                -64.0, 64.0, grid_iterations_2d, grid_points, start=c[1])
            c[1] = c1
        sse = _weighted_sse(expr, rows, stat_key, c)
        if sse is not None and sse < best_sse:
            best_sse, best_c = sse, list(c)

    if best_c is None:
        return None, None
    return best_c, best_sse


def held_out_error(expr: Expr, const_values: Sequence[float], held_out_rows: List[Dict],
                    stat_key: str) -> Optional[Dict]:
    """RMS over held-out cells of |e(cell)-observed(cell)|/null_sd(cell), per
    specification.yaml metrics.primary; returns None if no held-out row
    carries this statistic with a usable null_sd (reported, never estimated).

    DIAGNOSED (this dispatch, follow-up to TASK-20260907-8fd098): an early
    complexity-level expression can fit a genuinely-departing positive
    control (e.g. ZN_interval, whose Delta is legitimately O(1e2-1e4) --
    that IS the control working as designed, see stage1_own_enumeration.py)
    so badly that e_se = |pred-obs|/sd is itself astronomically large. Python
    float `**` raises OverflowError when the mathematical result exceeds
    float range (CPython, confirmed: `1e160 ** 2` raises but `1e160 * 1e160`
    silently returns `inf`); `e_se ** 2` was therefore crashing the whole
    multi-hour driver on a held-out error that is REAL and simply enormous,
    not a data bug. Fixed by squaring via `*` (never raises for this reason;
    IEEE-consistent inf on overflow, which is the mathematically correct
    value, not a clamp) and flagging any such row distinctly so a consumer
    never mistakes silent inf propagation for a well-behaved small metric."""
    sq = []
    per_curve = []
    any_overflow = False
    for row in held_out_rows:
        obs = row["statistics"].get(stat_key)
        sd = row["null_sd"].get(stat_key)
        if obs is None or sd is None or sd <= 0:
            continue
        pred = eval_expr(expr, row["leaves"], const_values)
        if pred is None:
            return None
        e_se = abs(pred - obs) / sd  # `/` overflows to inf silently, never raises
        sq_val = e_se * e_se  # `*` overflows to inf silently (unlike `**`), never raises
        overflow = math.isinf(sq_val) or math.isinf(e_se) or math.isnan(sq_val)
        any_overflow = any_overflow or overflow
        sq.append(sq_val)
        per_curve.append({
            "curve_index": row.get("curve_index"),
            "error_null_se": e_se,
            "overflow": overflow,
        })
    if not sq:
        return None
    rms = math.sqrt(sum(sq) / len(sq))
    return {
        "rms_null_se": rms,
        "n_held_out_rows": len(sq),
        "per_row": per_curve,
        "held_out_error_overflow": any_overflow,
    }


def leaf_env_for_row(row: Dict) -> Dict[str, float]:
    return {"N": row["N"], "B": row["B"], "m": row["m"], "M": row["M"], "mu": row["mu"]}


# ---------------------------------------------------------------------------
# Known closed forms for candidate-list scoring (a disclosed simplification:
# generic symbolic-equivalence-of-arbitrary-enumerated-forms is not
# implemented in this dispatch; the handful of candidates with a concrete,
# frozen closed form and free constants already stated in candidate-list.yaml
# are checked numerically instead, on the SAME leaf grid used for the fit).
# ---------------------------------------------------------------------------

KNOWN_CANDIDATES = {
    "INV-A1": lambda env: 1.0 - 3.0 * (env["B"] - 1.0) / env["N"],
    "INV-1": lambda env: env["M"] / env["N"],
    "INV-2prime": lambda env: 1.0 - 1.0 / env["N"],
}


def score_against_known_candidates(expr: Expr, const_values: Sequence[float], rows: List[Dict],
                                    tol: float = 1e-6) -> List[str]:
    """Numeric-equivalence check (not full symbolic equivalence) against
    KNOWN_CANDIDATES: an expression 'matches' a candidate if its fitted
    prediction agrees with the candidate's exact closed form to within `tol`
    relative on every row supplied. Returns the list of matched candidate
    ids (usually 0 or 1)."""
    matches = []
    for cand_id, fn in KNOWN_CANDIDATES.items():
        ok = True
        for row in rows:
            env = leaf_env_for_row(row)
            pred = eval_expr(expr, env, const_values)
            ref = fn(env)
            if pred is None:
                ok = False
                break
            denom = abs(ref) if abs(ref) > 1e-12 else 1.0
            if abs(pred - ref) / denom > tol:
                ok = False
                break
        if ok:
            matches.append(cand_id)
    return matches


if __name__ == "__main__":
    # self-test: fit INV-A1's own expression shape against synthetic rows
    # built FROM INV-A1 itself (sanity: the fitter must recover CONST=1,3
    # exactly, and held-out error must come out ~0).
    import sys
    expr = ge.canonicalize(("sub", ("CONST",), ("div", ("mul", ("leaf", "m"), ("sub", ("leaf", "B"), ("CONST",))), ("leaf", "N"))))
    rows = []
    for N in (16411, 65537, 262147):
        for B in (50, 80, 160):
            M = math.comb(B + 2, 3)
            mu = M / N
            delta = 1.0 - 3.0 * (B - 1) / N
            rows.append({
                "leaves": {"N": N, "B": B, "m": 3, "M": M, "mu": mu},
                "statistics": {"Delta": delta}, "null_sd": {"Delta": 1e-3},
                "curve_index": 0, "N": N, "B": B, "m": 3, "M": M, "mu": mu,
            })
    train = rows[:-3]
    held = rows[-3:]
    c, sse = fit_constants(expr, train, "Delta")
    print(f"fitted consts={c} sse={sse}", file=sys.stderr)
    ho = held_out_error(expr, c, held, "Delta")
    print(f"held_out={ho}", file=sys.stderr)
    assert ho["rms_null_se"] < 1e-3, ho
    matches = score_against_known_candidates(expr, c, rows)
    print(f"matches={matches}", file=sys.stderr)
    assert "INV-A1" in matches

    # Regression self-test (this dispatch's follow-up): a wildly-mismatched
    # expression against a held-out row with a tiny null_sd -- the exact
    # ZN_interval-positive-control shape that crashed the driver with
    # OverflowError on `e_se ** 2` -- must return a large-but-finite/inf
    # rms_null_se, flagged, and MUST NOT raise.
    bad_expr = ge.canonicalize(("leaf", "N"))  # N ~ 1e6, obs ~ 1.0, sd tiny
    bad_held = [{
        "leaves": {"N": 1048583, "B": 185, "m": 3, "M": 1072445, "mu": 1.02},
        "statistics": {"Delta": 1.0}, "null_sd": {"Delta": 1e-300},
        "curve_index": 99,
    }]
    ho_bad = held_out_error(bad_expr, [], bad_held, "Delta")
    print(f"overflow-case held_out={ho_bad}", file=sys.stderr)
    assert ho_bad is not None
    assert ho_bad["held_out_error_overflow"] is True
    assert math.isinf(ho_bad["rms_null_se"])
    print("stage1_fit_engine.py overflow-guard self-test: OK", file=sys.stderr)

    print("stage1_fit_engine.py self-test: OK", file=sys.stderr)
