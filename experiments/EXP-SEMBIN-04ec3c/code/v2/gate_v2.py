#!/usr/bin/env python3
"""C-IMPL-GATE (AMD-20261001-e61f2b change C-4), re-implemented by the executor
from the amendment text alone.

The reference quantities here are written independently of model_v2.py:
  * L via math.lgamma (the driver uses the exact integer factorial);
  * S via math.floor(m / 2.0) (the driver uses integer floor division);
  * the log-sum via math.fsum (the driver accumulates in a loop);
  * the yield identity via log2 binom(2^d, m) (the driver never forms it).

Checks:
  (a) YIELD IDENTITY  every evaluated sweep cell with d >= 16:
      |TPR_impl - (N - log2 binom(2^d, m))| <= 0.05 bits
  (b) CLOSED FORMS    every listed degree, m in 2..16, d in {16, 24, 32},
      every permitted s, every oracle model: PROBE, FILL, LA, TOTAL equal the
      header closed forms to within 1e-6 bits
  (c) BUDGET INVARIANT every MITM_CAPPED sweep cell: s*d <= log2 B and
      s = min(S, floor(log2 B / d))
  (d) M-BOUND PROBE   every argmin over m landing at m = 16 is re-evaluated with
      m up to 24 and labelled bound-tracking if it moves
  (e) GATE POWER      run by run_v2.py over the unmutated driver and M1-M4

Operationalisation notes (disclosed in the manifest):
  * (a) "computed independently via lgamma": the three-lgamma form
    lgamma(X+1) - lgamma(X-m+1) - lgamma(m+1) with X = 2^d loses all precision
    in IEEE double once d exceeds about 40 (lgamma(X) ~ X ln X). The falling
    factorial is therefore evaluated as sum_{i<m} log2(X - i) via log1p and m!
    via lgamma; the pure three-lgamma form is evaluated beside it wherever
    d <= 24 and their maximum disagreement is reported.
  * (d) is a labelling rule in the amendment, not a pass/fail test. Its
    executable pass criterion here is completeness and consistency: every
    argmin at m = 16 is probed, and the m <= 24 re-evaluation restricted to
    m <= 16 reproduces the original argmin exactly.
"""
from __future__ import annotations

import math

LN2 = math.log(2.0)
GATE_DEGREES = (97, 109, 131, 163, 191, 233, 239, 283, 409, 571)
GATE_M = tuple(range(2, 17))
GATE_D_B = (16.0, 24.0, 32.0)
GATE_MODELS = ("FREE", "ENUM", "MITM", "MITM_CAPPED")
GATE_V1_BUDGETS = (30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, None)
TOL_A = 0.05
TOL_B = 1e-6
MAX_EXAMPLES = 5

# cell tuple indices (model_v2.CELL_FIELDS)
I_S, I_TPR, I_CALLS, I_PROBE, I_FILL, I_LA, I_TOTAL, I_TABLE = range(8)


def ref_N(n: int, log2_r: float) -> float:
    return log2_r if n == 131 else float(n)


def ref_L(m: int) -> float:
    return math.lgamma(m + 1.0) / LN2


def ref_S(m: int) -> int:
    return int(math.floor(m / 2.0))


def ref_s(model: str, m: int, d: float, log2_budget) -> int:
    if model in ("FREE", "ENUM"):
        return 0
    S = ref_S(m)
    if model == "MITM" or log2_budget is None:
        return S
    return min(S, int(math.floor(log2_budget / d)))


def ref_closed_forms(N: float, model: str, m: int, d: float, s: int):
    TPR = N + ref_L(m) - m * d
    if model == "FREE":
        o = 0.0
    elif model == "ENUM":
        o = (m - 1) * d
    else:
        o = (m - s) * d
    PROBE = d + TPR + o
    FILL = s * d if (model in ("MITM", "MITM_CAPPED") and s >= 1) else 0.0
    LA = 2.0 * d
    top = max(PROBE, FILL, LA)
    TOTAL = top + math.log2(math.fsum(2.0 ** (x - top) for x in (PROBE, FILL, LA)))
    return {"PROBE": PROBE, "FILL": FILL, "LA": LA, "TOTAL": TOTAL}


def ref_log2_binom_pow2(d: float, m: int) -> float:
    """log2 binom(2^d, m): falling factorial via log1p, m! via lgamma."""
    X = 2.0 ** d
    acc = 0.0
    for i in range(m):
        acc += d + math.log1p(-i / X) / LN2
    return acc - math.lgamma(m + 1.0) / LN2


def ref_log2_binom_pure_lgamma(d: float, m: int) -> float:
    X = 2.0 ** d
    return (math.lgamma(X + 1.0) - math.lgamma(X - m + 1.0)
            - math.lgamma(m + 1.0)) / LN2


class SweepChecks:
    """Streaming checks (a) and (c), plus the per-m argmin table (d) needs."""

    def __init__(self, log2_r: float):
        self.log2_r = log2_r
        self.a = {"cells_checked": 0, "violations": 0, "max_abs_diff_bits": 0.0,
                  "tolerance_bits": TOL_A, "examples": []}
        self.c = {"cells_checked": 0, "violations": 0, "examples": []}
        self.pure_lgamma_cross = {"cells": 0, "max_abs_diff_bits": 0.0}
        self._ycache = {}
        # (n, model, B, m) -> (TOTAL, d) minimum over in-domain cells
        self.min_by_m = {}

    def observe(self, n, model, b, m, d, cell):
        if d >= 16.0:
            key = (n, m, d)
            ref = self._ycache.get(key)
            if ref is None:
                ref = ref_N(n, self.log2_r) - ref_log2_binom_pow2(d, m)
                if d <= 24.0:
                    alt = ref_N(n, self.log2_r) - ref_log2_binom_pure_lgamma(d, m)
                    self.pure_lgamma_cross["cells"] += 1
                    self.pure_lgamma_cross["max_abs_diff_bits"] = max(
                        self.pure_lgamma_cross["max_abs_diff_bits"], abs(alt - ref))
                self._ycache[key] = ref
            diff = abs(cell[I_TPR] - ref)
            self.a["cells_checked"] += 1
            if diff > self.a["max_abs_diff_bits"]:
                self.a["max_abs_diff_bits"] = diff
            if diff > TOL_A:
                self.a["violations"] += 1
                if len(self.a["examples"]) < MAX_EXAMPLES:
                    self.a["examples"].append({"n": n, "model": model, "B": b, "m": m,
                                               "d": d, "TPR_impl": cell[I_TPR],
                                               "TPR_ref": ref, "diff": diff})
        if model == "MITM_CAPPED":
            self.c["cells_checked"] += 1
            s = cell[I_S]
            want = ref_s(model, m, d, b)
            ok = (s == want) and (b is None or s * d <= b)
            if not ok:
                self.c["violations"] += 1
                if len(self.c["examples"]) < MAX_EXAMPLES:
                    self.c["examples"].append({"n": n, "B": b, "m": m, "d": d,
                                               "s_impl": s, "s_ref": want,
                                               "s_times_d": s * d})
        if cell[I_CALLS] >= 0.0:
            k = (n, model, b, m)
            cur = self.min_by_m.get(k)
            if cur is None or cell[I_TOTAL] < cur[0]:
                self.min_by_m[k] = (cell[I_TOTAL], d)

    def result_a(self):
        r = dict(self.a)
        r["pure_three_lgamma_cross_check_d_le_24"] = dict(self.pure_lgamma_cross)
        r["passed"] = (self.a["violations"] == 0 and self.a["cells_checked"] > 0)
        return r

    def result_c(self):
        r = dict(self.c)
        r["passed"] = (self.c["violations"] == 0 and self.c["cells_checked"] > 0)
        return r


def check_b(driver, log2_r: float):
    """(b) closed forms, driver vs reference, every permitted s."""
    out = {"cells_checked": 0, "violations": 0, "max_abs_diff_bits": 0.0,
           "tolerance_bits": TOL_B, "examples": []}
    for n in GATE_DEGREES:
        N = ref_N(n, log2_r)
        for m in GATE_M:
            for d in GATE_D_B:
                for model in GATE_MODELS:
                    if model == "MITM_CAPPED":
                        budgets = list(GATE_V1_BUDGETS) + [float(s * d) for s in range(0, ref_S(m) + 1)]
                    else:
                        budgets = [None]
                    for b in budgets:
                        s_ref = ref_s(model, m, d, b)
                        ref = ref_closed_forms(N, model, m, d, s_ref)
                        cell = driver.evaluate(n, model, m, d, b)
                        got = {"PROBE": cell[I_PROBE], "FILL": cell[I_FILL],
                               "LA": cell[I_LA], "TOTAL": cell[I_TOTAL]}
                        out["cells_checked"] += 1
                        worst = max(abs(got[k] - ref[k]) for k in ref)
                        out["max_abs_diff_bits"] = max(out["max_abs_diff_bits"], worst)
                        if worst > TOL_B:
                            out["violations"] += 1
                            if len(out["examples"]) < MAX_EXAMPLES:
                                out["examples"].append({"n": n, "m": m, "d": d,
                                                        "model": model, "B": b,
                                                        "s_ref": s_ref,
                                                        "s_impl": cell[I_S],
                                                        "impl": got, "ref": ref})
    out["passed"] = (out["violations"] == 0 and out["cells_checked"] > 0)
    return out


def _argmin_over_m(min_by_m, n, model, b, m_values):
    best = None
    for m in m_values:
        v = min_by_m.get((n, model, b, m))
        if v is None:
            continue
        if best is None or v[0] < best[1]:
            best = (m, v[0], v[1])
    return best


def check_d(driver, checks: SweepChecks, degrees, m_max_probe: int = 24):
    """(d) m-bound probe on every (degree, model, B) argmin over m in 2..16."""
    probes = []
    consistent = True
    keys = sorted({(k[0], k[1], k[2]) for k in checks.min_by_m},
                  key=lambda t: (t[0], t[1], -1 if t[2] is None else t[2]))
    for (n, model, b) in keys:
        base = _argmin_over_m(checks.min_by_m, n, model, b, range(2, 17))
        if base is None or base[0] != 16:
            continue
        ext = {}
        for m in range(2, m_max_probe + 1):
            best = None
            for d in driver.d_grid(float(n)):
                cell = driver.evaluate(n, model, m, d, b)
                if cell[I_CALLS] < 0.0:
                    continue
                if best is None or cell[I_TOTAL] < best[0]:
                    best = (cell[I_TOTAL], d)
            if best is not None:
                ext[(n, model, b, m)] = best
        re16 = _argmin_over_m(ext, n, model, b, range(2, 17))
        re24 = _argmin_over_m(ext, n, model, b, range(2, m_max_probe + 1))
        same = (re16 is not None and re16[0] == base[0]
                and abs(re16[1] - base[1]) < 1e-12)
        consistent = consistent and same
        moves = re24 is not None and re24[0] != 16
        probes.append({"n": n, "model": model, "B": b,
                       "argmin_m_le_16": base[0], "total_m_le_16": base[1],
                       "argmin_m_le_24": None if re24 is None else re24[0],
                       "total_m_le_24": None if re24 is None else re24[1],
                       "moves": moves,
                       "label": "bound-tracking" if moves else "interior-or-stable",
                       "reevaluation_consistent": same})
    return {"argmins_at_m16_probed": len(probes), "probes": probes,
            "all_reevaluations_consistent": consistent,
            "bound_tracking_count": sum(1 for p in probes if p["moves"]),
            "passed": bool(consistent)}
