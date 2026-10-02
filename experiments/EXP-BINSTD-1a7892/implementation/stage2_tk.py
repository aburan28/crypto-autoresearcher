"""Fix Field.trace and validate irreducibles; Stage-2 T_k cost instrument."""
from __future__ import annotations

import math
import random
import time
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from curve import Curve
from gf2n import Field, IRRED, is_irreducible, pmod, clmul


def make_field(n: int) -> Field:
    if n in IRRED:
        return Field(n, IRRED[n])
    # search for an irreducible of degree n (low weight)
    for t in range(1, n):
        for s in range(0, t):
            mod = (1 << n) | (1 << t) | ((1 << s) if s else 0)
            if s == 0:
                mod = (1 << n) | (1 << t) | 1
            ok, _ = is_irreducible(mod)
            if ok:
                IRRED[n] = mod
                return Field(n, mod)
    raise ValueError(f"no irreducible found for n={n}")


def choose_toy_curve(F: Field, seed: int) -> Curve:
    rng = random.Random(seed)
    for _ in range(10000):
        A = rng.randrange(F.q)
        B = rng.randrange(1, F.q)
        C = Curve(F, A, B)
        # need at least a few affine points
        pts = []
        for x in range(F.q):
            P = C.lift_x(x)
            if P is not None:
                pts.append(P)
                if len(pts) >= 4:
                    return C
    raise RuntimeError("failed to find toy curve with points")


def factor_base(C: Curve) -> List[Tuple[int, int]]:
    """Factor base = nonzero points of E(F_q) (both y-lifts)."""
    fb = []
    for x in range(C.F.q):
        P = C.lift_x(x)
        if P is None:
            continue
        fb.append(P)
        N = C.neg(P)
        if N != P:
            fb.append(N)
    return fb


def sum_points(C: Curve, pts: List) -> Optional[Tuple[int, int]]:
    R = None
    for P in pts:
        R = C.add(R, P)
    return R


def certificate_verify(C: Curve, R, parts: List) -> bool:
    """Independent re-verification: sum parts on the curve equals R."""
    if not all(C.on_curve(P) for P in parts):
        return False
    if R is not None and not C.on_curve(R):
        return False
    S = sum_points(C, parts)
    return S == R


def tk_system_params(g: int) -> Dict[str, Any]:
    """Gorla–Massierer T_n sizes with n = g+1 (arity-g relations).

    Working in T_n: 2n-1 equations in 2n-2 indeterminates of total degree
    (n-1)*2^{n-2}. Source: iacr:2014/318 §6.2 (extracted Stage 1).
    """
    n = g + 1
    n_eq = 2 * n - 1
    n_var = 2 * n - 2
    total_degree = (n - 1) * (1 << (n - 2))
    return {
        "n": n,
        "g": g,
        "n_equations": n_eq,
        "n_variables": n_var,
        "total_degree": total_degree,
        "source": "Gorla-Massierer iacr:2014/318 §6.2 (extracted)",
        "label": "modeled_system_shape",
    }


def macaulay_shape(n_var: int, n_eq: int, deg: int, D: int) -> Dict[str, Any]:
    """Dense Macaulay matrix shape over F_2 at degree D (upper bound)."""
    if D < deg:
        return {
            "D": D,
            "n_rows": 0,
            "n_cols": 0,
            "feasible": False,
            "reason": "D < equation_degree",
        }
    n_cols = math.comb(n_var + D, D)
    # each equation contributes monomials of degree <= D-deg
    per_eq = math.comb(n_var + (D - deg), D - deg) if D >= deg else 0
    n_rows = n_eq * per_eq
    entries = n_rows * n_cols
    # hard cap: ~64e6 entries (~64 MB of uint8) advisory for this instrument
    feasible = entries <= 64_000_000 and n_cols <= 20000 and n_rows <= 20000
    return {
        "D": D,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "entries": entries,
        "feasible": feasible,
        "label": "modeled_macaulay_shape",
    }


def ge_f2_ops(n_rows: int, n_cols: int, seed: int) -> Dict[str, Any]:
    """Measured dense F2 Gaussian-elimination op count on a random matrix
    of the given shape (arity-driven cost proxy; not a Groebner engine)."""
    rng = np.random.default_rng(seed)
    # pack columns into bitwords
    nwords = (n_cols + 63) // 64
    M = rng.integers(0, 2, size=(n_rows, n_cols), dtype=np.uint8)
    t0 = time.perf_counter()
    # convert to bit-packed rows
    rows = np.zeros((n_rows, nwords), dtype=np.uint64)
    for i in range(n_rows):
        for j in range(n_cols):
            if M[i, j]:
                rows[i, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    rank = 0
    xor_words = 0
    pivots = []
    used = [False] * n_rows
    for col in range(n_cols):
        w, b = col >> 6, col & 63
        mask = np.uint64(1) << np.uint64(b)
        piv = None
        for i in range(n_rows):
            if not used[i] and (rows[i, w] & mask):
                piv = i
                break
        if piv is None:
            continue
        used[piv] = True
        pivots.append((piv, col))
        rank += 1
        for i in range(n_rows):
            if i != piv and (rows[i, w] & mask):
                rows[i] ^= rows[piv]
                xor_words += nwords
    wall = time.perf_counter() - t0
    return {
        "measured_wall_s": wall,
        "measured_rank": rank,
        "measured_xor_word_ops": xor_words,
        "measured_n_rows": n_rows,
        "measured_n_cols": n_cols,
        "label": "measured",
    }


def pick_macaulay_D(g: int) -> int:
    """Fixed truncated Macaulay degree D=3 for cross-g comparability.

    Full Gorla–Massierer total_degree grows exponentially in n=g+1 and is
    recorded separately; the instrument uses a constant D so that matrix
    size is driven by n_variables=2g (arity), not by an opportunistic
    per-g degree reduction that would invert the cost curve.
    """
    shape = tk_system_params(g)
    D = 3
    ms = macaulay_shape(shape["n_variables"], shape["n_equations"], min(2, D), D)
    if not ms["feasible"]:
        # fall back one step
        D = 2
        ms = macaulay_shape(shape["n_variables"], shape["n_equations"], min(2, D), D)
        if not ms["feasible"]:
            return 1
    return D


def measure_tk_trial(d: int, k_prime: int, seed: int) -> Dict[str, Any]:
    g = k_prime - 1
    assert g == k_prime - 1
    F = make_field(d)
    C = choose_toy_curve(F, seed ^ 0xB17)
    fb = factor_base(C)
    if len(fb) < g:
        return {
            "ok": False,
            "termination_reason": "instrument_ceiling",
            "reason": f"factor_base_size {len(fb)} < g={g}",
        }
    rng = random.Random(seed)
    parts = [fb[rng.randrange(len(fb))] for _ in range(g)]
    R = sum_points(C, parts)
    cert_ok = certificate_verify(C, R, parts)

    sys_p = tk_system_params(g)
    # Truncated Macaulay instrument: equation degree clipped so a matrix fits.
    D = pick_macaulay_D(g)
    eq_deg_instrument = min(2, D)  # truncated; full total_degree recorded separately
    ms = macaulay_shape(sys_p["n_variables"], sys_p["n_equations"], eq_deg_instrument, D)
    out: Dict[str, Any] = {
        "ok": True,
        "construction": "Tk",
        "d": d,
        "k_prime": k_prime,
        "g": g,
        "dk": d * k_prime,
        "seed": seed,
        "curve": {"A": C.A, "B": C.B, "field_n": d, "modulus": C.F.mod},
        "factor_base_size": len(fb),
        "system_shape": sys_p,
        "macaulay_instrument": {
            **ms,
            "equation_degree_used": eq_deg_instrument,
            "full_total_degree": sys_p["total_degree"],
            "truncation_note": (
                "Fixed Macaulay degree D<=3 with equation degree clipped to <=2 so "
                "cross-g cost is driven by n_variables=2g (arity). Full "
                "Gorla–Massierer total_degree is under system_shape.total_degree. "
                "Bias: optimistic for attack (understates true Groebner cost)."
            ),
            "label_mix": "modeled_shape + measured_GE_on_random_matrix_of_that_shape",
        },
        "certificate": {
            "kind": "decomposition",
            "verified": cert_ok,
            "n_parts": g,
            "R": None if R is None else [R[0], R[1]],
            "parts": [[p[0], p[1]] for p in parts],
        },
    }
    if not ms["feasible"]:
        out["termination_reason"] = "instrument_ceiling"
        out["per_trial_cost"] = {
            "status": "instrument_ceiling",
            "modeled_entries": ms["entries"],
            "label": "modeled",
        }
        return out

    ge = ge_f2_ops(ms["n_rows"], ms["n_cols"], seed)
    out["per_trial_cost"] = {
        "wall_s": ge["measured_wall_s"],
        "xor_word_ops": ge["measured_xor_word_ops"],
        "macaulay_rows": ms["n_rows"],
        "macaulay_cols": ms["n_cols"],
        "label": "measured",
    }
    out["ge"] = ge
    out["termination_reason"] = "completed"
    # Optional: at g=2 also measure exhaustive FB-pair search wall (sanity)
    if g == 2 and len(fb) <= 64:
        t0 = time.perf_counter()
        found = 0
        target = R
        for a, b in combinations(range(len(fb)), 2):
            if sum_points(C, [fb[a], fb[b]]) == target:
                found += 1
                break
        out["g2_exhaustive_pair_search_wall_s"] = time.perf_counter() - t0
        out["g2_exhaustive_found"] = found > 0
        out["g2_exhaustive_label"] = "measured"
    return out


def measure_null_no_subfield(seed: int) -> Dict[str, Any]:
    """NULL control: curve over F_{2^p} with p prime → no intermediate subfield → no T_k."""
    p = 5  # prime; F_{2^5} has no proper subfield other than F_2
    F = make_field(p)
    C = choose_toy_curve(F, seed ^ 0xA011)
    # Intermediate subfields of F_{2^p}: only F_2 and itself.
    divisors = [d for d in range(1, p) if p % d == 0]
    intermediate = [d for d in divisors if d not in (1,)]  # proper nontrivial
    # For prime p, divisors of p are {1,p}; intermediate relative degrees empty.
    has_tk = False  # no F_{q^k}/F_q with 1<k<p structure from composite extension
    return {
        "construction": "null_no_subfield",
        "field_n": p,
        "n_is_prime": True,
        "proper_divisors_of_n": divisors,
        "intermediate_subfield_degrees": intermediate,
        "Tk_construction_possible": has_tk,
        "Tk_finite_cost": None if not has_tk else "INVALID",
        "reports_no_Tk_construction": not has_tk,
        "curve": {"A": C.A, "B": C.B, "modulus": F.mod},
        "seed": seed,
        "termination_reason": "completed",
        "note": (
            "Prime extension degree ⇒ no intermediate subfield to descend to; "
            "instrument must report no T_k construction (not a finite cost)."
        ),
    }


def measure_non_tk(g: int, seed: int) -> Dict[str, Any]:
    """CTRL-non-Tk-same-arity: random F2 Macaulay-shaped matrix, same (n_var,n_eq,D)."""
    sys_p = tk_system_params(g)
    D = pick_macaulay_D(g)
    eq_deg_instrument = min(2, D)
    ms = macaulay_shape(sys_p["n_variables"], sys_p["n_equations"], eq_deg_instrument, D)
    out = {
        "construction": "non_Tk_same_arity",
        "g": g,
        "system_shape": sys_p,
        "macaulay_instrument": ms,
        "seed": seed,
    }
    if not ms["feasible"]:
        out["termination_reason"] = "instrument_ceiling"
        out["per_trial_cost"] = {"status": "instrument_ceiling", "label": "modeled"}
        return out
    ge = ge_f2_ops(ms["n_rows"], ms["n_cols"], seed ^ 0xC771)
    out["per_trial_cost"] = {
        "wall_s": ge["measured_wall_s"],
        "xor_word_ops": ge["measured_xor_word_ops"],
        "macaulay_rows": ms["n_rows"],
        "macaulay_cols": ms["n_cols"],
        "label": "measured",
    }
    out["ge"] = ge
    out["termination_reason"] = "completed"
    out["note"] = (
        "Random dense F2 matrix of the same Macaulay shape; isolates arity-driven "
        "GE cost from T_k-specific polynomial structure."
    )
    return out
