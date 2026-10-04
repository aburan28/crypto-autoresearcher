"""MODELED quantities for EXP-ECDLP-869870, written verbatim from the frozen
contract's preregistered_prediction ((B1)-(B4), C_max(a), the fixture values).

Everything in this module is a MODEL number. Nothing here reads a measurement.
"""
from __future__ import annotations

import math

import numpy as np

# Published Bernstein-Lange fixture values (Section 4 case study and Table 4.1),
# copied from the frozen contract's fixture_procedure. Keyed by (a, r).
FIXTURE_CELLS = [(0.25, 2), (0.5, 1), (0.5, 2), (0.5, 8), (1.0, 1), (1.0, 2), (1.0, 8)]
PUBLISHED_SCALED_COST = {
    (0.25, 2): 1.79, (0.5, 1): 2.14, (0.5, 2): 1.62, (0.5, 8): 1.38,
    (1.0, 1): 2.01, (1.0, 2): 1.62, (1.0, 8): 1.50,
}
PUBLISHED_SCALED_PRECOMP = {
    (0.25, 2): 1.24, (0.5, 1): 0.85, (0.5, 2): 1.90, (0.5, 8): 15.7,
    (1.0, 1): 1.34, (1.0, 2): 3.66, (1.0, 8): 36.9,
}
# (B4) model values at the seven cells, as written in the contract.
B4_CONTRACT_VALUES = {
    (0.25, 2): 1.25, (0.5, 1): 0.88, (0.5, 2): 2.12, (0.5, 8): 17.0,
    (1.0, 1): 1.50, (1.0, 2): 4.00, (1.0, 8): 40.0,
}
# Model oracle constants at the N/T = 8 cells (contract: "within 0.05 of 1.35 / 1.51").
MODEL_NT8 = {(0.5, 8): 1.35, (1.0, 8): 1.51}
GATE_COST_TOL = 0.10          # absolute
GATE_PRECOMP_TOL = 0.12       # relative

# Contract's rounded C_max and x* values (B2) and (B3).
CMAX_CONTRACT = {1.0: (0.19, 0.66), 0.5: (0.40, 0.52), 0.25: (0.74, 0.39), 0.125: (1.2, 0.27)}
B3_CONTRACT = {1.0: 1.51, 0.5: 1.35, 0.25: 1.28, 0.125: 1.30}


def c_rand(a_m: float) -> float:
    """(B1) unselected law: 1 - (1 + 2 a_m)^{-1/2}."""
    return 1.0 - (1.0 + 2.0 * a_m) ** -0.5


def _g(x: float) -> float:
    return 2.0 * x ** -0.5 * math.exp(-x / 2.0) - math.sqrt(2 * math.pi) * math.erfc(math.sqrt(x / 2.0))


def solve_xstar(a: float) -> float:
    """(B2): x* solving 2 x^{-1/2} e^{-x/2} - sqrt(2 pi) erfc(sqrt(x/2)) = a sqrt(2 pi).
    g is decreasing in x; bisection."""
    target = a * math.sqrt(2 * math.pi)
    lo, hi = 1e-9, 50.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _g(mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def c_max(a: float) -> float:
    """(B2) oracle ceiling C_max(a) = erfc(sqrt(x*/2))."""
    return math.erfc(math.sqrt(solve_xstar(a) / 2.0))


def b3_oracle_constant(a: float) -> float:
    """(B3): L sqrt(T/N) = sqrt(a) / C_max(a)."""
    return math.sqrt(a) / c_max(a)


def b4_walks(r: float, a: float, T: int) -> float:
    """(B4): walks needed to reach r T distinct DPs, m = (r + r^2 a / 2) T."""
    return (r + r * r * a / 2.0) * T


def b4_scaled_precomp(r: float, a: float) -> float:
    """(B4): P / sqrt(N T) = sqrt(a) r (1 + r a / 2)."""
    return math.sqrt(a) * r * (1.0 + r * a / 2.0)


def borel_log_pmf(mu: float, nmax: int) -> np.ndarray:
    """log P(n) for n = 1..nmax of Borel(mu): e^{-mu n} (mu n)^{n-1} / n!.
    Returns array of length nmax+1 with index 0 = -inf."""
    n = np.arange(1, nmax + 1, dtype=np.float64)
    log_fact = np.cumsum(np.log(n))  # log n!
    lp = -mu * n + (n - 1.0) * np.log(mu * n) - log_fact
    out = np.full(nmax + 1, -np.inf)
    out[1:] = lp
    return out


def borel_max_band(theta: float, K: float, W: float, q_lo=0.005, q_hi=0.995) -> dict:
    """99% band for the maximum of K i.i.d. Borel(1 - theta) samples
    (the contract's 'Borel(1 - theta) N/W-sample order-statistic 99% band').
    P(max <= n) = F(n)^K.  MODEL number."""
    mu = 1.0 - theta
    nmax = int(max(1000, 80 * W * W))
    lp = borel_log_pmf(mu, nmax)
    pmf = np.exp(lp[1:])
    cdf = np.cumsum(pmf)
    total = float(cdf[-1])
    cdf = np.minimum(cdf, 1.0)
    logF = np.log(np.clip(cdf, 1e-300, 1.0))
    logP = K * logF
    P = np.exp(logP)
    n = np.arange(1, nmax + 1)
    lo = int(n[np.searchsorted(P, q_lo)]) if P[-1] >= q_lo else None
    hi = int(n[np.searchsorted(P, q_hi)]) if P[-1] >= q_hi else None
    return {"n_lo": lo, "n_hi": hi, "K": K, "mu": mu, "pmf_mass_to_nmax": total, "nmax": nmax}


def model_table(a: float) -> dict:
    """All MODEL numbers at a given a (labelled modeled)."""
    return {
        "a": a,
        "c_max_numeric": c_max(a),
        "x_star_numeric": solve_xstar(a),
        "c_max_contract_rounded": CMAX_CONTRACT[a][1],
        "x_star_contract_rounded": CMAX_CONTRACT[a][0],
        "b3_oracle_constant_numeric": b3_oracle_constant(a),
        "b3_contract_rounded": B3_CONTRACT[a],
        "c_rand_at_a": c_rand(a),
        "source": "EXP-ECDLP-869870 preregistered_prediction (IDEA-20260906-aed829 (B1)-(B3), design (B4)); MODELED",
    }
