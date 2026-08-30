"""Stage 1 + Stage 3: exhaustive dual-check of the seven exact stratum-count
closed forms, on a panel curve, plus the internal sum checks.

Deliberately simpler than the sibling EXP-MONO-4c7479's dual arm(a)/arm(b)
machinery (see spec `stage1_classification.independence_from_sibling_arms`):
no F_{p^2}/F_{p^4} arithmetic anywhere. The inert-case class is decided by a
single F_p Legendre symbol of c0, computed DIRECTLY from (e1,e2) -- never
via t1,t2.
"""
from __future__ import annotations

from fp_common import legendre, inverse, tonelli_shanks

INV2_CACHE: dict = {}


def _inv2(p: int) -> int:
    v = INV2_CACHE.get(p)
    if v is None:
        v = inverse(2, p)
        INV2_CACHE[p] = v
    return v


def classify_panel_curve(p: int, A: int, B: int, log_rows: bool = True):
    """Exhaustively classify every (e1,e2) in F_p x F_p for curve (A,B).

    Returns (tallies, log) where tallies is a dict with keys
    double_root, A1_identity, A2_sigma_i, A3_sigma1sigma2, A4_ramified_A,
    B1_block_swap, B2_ramified_B, B3_four_cycle (all counts), and log is a
    list of per-point rows (e1, e2, D, chi_D, stratum, [chi1,chi2 or chi_c0])
    when log_rows is True (always True for panel curves per
    `required_artifacts`; kept as a parameter for clarity/testability).
    """
    inv2 = _inv2(p)
    tallies = {
        "double_root": 0,
        "A1_identity": 0, "A2_sigma_i": 0, "A3_sigma1sigma2": 0,
        "A4_ramified_A": 0,
        "B1_block_swap": 0, "B2_ramified_B": 0, "B3_four_cycle": 0,
    }
    log = [] if log_rows else None

    for e1 in range(p):
        e1sq = e1 * e1 % p
        for e2 in range(p):
            D = (e1sq - 4 * e2) % p
            if D == 0:
                tallies["double_root"] += 1
                if log_rows:
                    log.append((e1, e2, D, 0, "double_root", None, None))
                continue
            chi_D = legendre(D, p)
            if chi_D == 1:
                sqrtD = tonelli_shanks(D, p)
                t1 = (e1 + sqrtD) * inv2 % p
                t2 = (e1 - sqrtD) * inv2 % p
                f1 = (t1 * t1 * t1 + A * t1 + B) % p
                f2 = (t2 * t2 * t2 + A * t2 + B) % p
                if f1 == 0 or f2 == 0:
                    tallies["A4_ramified_A"] += 1
                    if log_rows:
                        log.append((e1, e2, D, chi_D, "A4_ramified_A", None, None))
                    continue
                c1 = legendre(f1, p)
                c2 = legendre(f2, p)
                if c1 == 1 and c2 == 1:
                    stratum = "A1_identity"
                elif c1 == -1 and c2 == -1:
                    stratum = "A3_sigma1sigma2"
                else:
                    stratum = "A2_sigma_i"
                tallies[stratum] += 1
                if log_rows:
                    log.append((e1, e2, D, chi_D, stratum, c1, c2))
            else:
                # Inert case: c0 computed DIRECTLY from (e1,e2), never via
                # t1,t2 -- no F_{p^2} lift is performed anywhere.
                e1e1 = e1 * e1 % p
                e2sq = e2 * e2 % p
                e2cu = e2sq * e2 % p
                c0 = (
                    e2cu
                    + A * e2 % p * ((e1e1 - 2 * e2) % p)
                    + B * ((e1 * e1e1 - 3 * e1 * e2) % p)
                    + A * A % p * e2
                    + A * B % p * e1
                    + B * B % p
                ) % p
                if c0 == 0:
                    tallies["B2_ramified_B"] += 1
                    if log_rows:
                        log.append((e1, e2, D, chi_D, "B2_ramified_B", None, None))
                    continue
                chi_c0 = legendre(c0, p)
                stratum = "B1_block_swap" if chi_c0 == 1 else "B3_four_cycle"
                tallies[stratum] += 1
                if log_rows:
                    log.append((e1, e2, D, chi_D, stratum, chi_c0, None))
    return tallies, log
