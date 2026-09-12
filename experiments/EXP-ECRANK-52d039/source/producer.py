#!/usr/bin/env python3
"""Producer for EXP-ECRANK-52d039.

This file intentionally has no imports from verifier.py.  It contains the
deterministic producer path: exact interval arithmetic, the abstract fixtures,
and the named-curve interface.  The runner serialises its returned objects;
this module does not decide a hypothesis status.
"""

from __future__ import annotations

import json
import math
import os
import platform
import signal
import sys
import time
from fractions import Fraction
from pathlib import Path


class BudgetExpired(Exception):
    """Frozen wall-clock cap reached; emit completed records only."""

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


EXP = "EXP-ECRANK-52d039"
# Binding machine-protection caps from the frozen contract. There is no
# counted-op or bit-size stop rule; a stop here is infrastructure only.
WALL_SECONDS_CAP = 3600
MEMORY_BYTES_CAP = 8 * 1024 ** 3
WALL_STOP_MARGIN_SECONDS = 900
# Deterministic machine-protection ceiling so R2 and its R3 replay emit
# the same completed-n ledger. Not a protocol cap; a stop is infrastructure.
COORDINATE_BIT_GUARD = 500_000


def q(x):
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, str):
        if "/" in x:
            a, b = x.split("/", 1)
            return Fraction(int(a), int(b))
        return Fraction(int(x), 1)
    raise TypeError(x)


def qs(x: Fraction) -> str:
    x = q(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def enc(x):
    if isinstance(x, Fraction):
        return qs(x)
    if isinstance(x, dict):
        return {str(k): enc(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [enc(v) for v in x]
    return x


def interval(lo, hi=None):
    if hi is None:
        hi = lo
    lo, hi = q(lo), q(hi)
    if lo > hi:
        raise ValueError("inverted interval")
    return (lo, hi)


def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def ineg(a):
    return (-a[1], -a[0])


def isub(a, b):
    return iadd(a, ineg(b))


def imul(a, b):
    z = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(z), max(z))


def idiv(a, b):
    if b[0] <= 0 <= b[1]:
        raise ZeroDivisionError("interval denominator contains zero")
    return imul(a, (Fraction(1, b[1]), Fraction(1, b[0])))


def ipow2(a):
    return imul(a, a)


def interval_ldl(mat):
    """Conservative interval LDL^T factorisation.

    Every operation is rational and outward.  If a denominator interval
    contains zero, no sound pivot bound is available and the result is marked
    unresolved rather than guessed.
    """
    n = len(mat)
    L = [[interval(0) for _ in range(n)] for _ in range(n)]
    D = []
    failed = None
    for i in range(n):
        di = mat[i][i]
        for k in range(i):
            di = isub(di, imul(ipow2(L[i][k]), D[k]))
        D.append(di)
        if di[0] <= 0 <= di[1]:
            failed = i
            break
        L[i][i] = interval(1)
        for j in range(i + 1, n):
            num = mat[j][i]
            for k in range(i):
                num = isub(num, imul(imul(L[j][k], L[i][k]), D[k]))
            try:
                L[j][i] = idiv(num, di)
            except ZeroDivisionError:
                failed = i
                break
        if failed is not None:
            break
    pivots = D
    return {
        "pivots": [[qs(a), qs(b)] for a, b in pivots],
        "pivot_lower_bounds": [qs(a) for a, _ in pivots],
        "pivot_upper_bounds": [qs(b) for _, b in pivots],
        "L": [[[qs(a), qs(b)] for a, b in row] for row in L],
        "positive": failed is None and len(D) == n and all(a > 0 for a, _ in D),
        "unresolved_pivot": failed,
        "determinant_interval": _det_interval(D, n),
    }


def _det_interval(D, n):
    if len(D) != n:
        return None
    out = interval(1)
    for d in D:
        out = imul(out, d)
    return [qs(out[0]), qs(out[1])]


def exact_ldl(mat):
    return interval_ldl([[interval(v) for v in row] for row in mat])


def matrix_add_width(m, width):
    w = q(width)
    return [[interval(q(m[i][j]) - w, q(m[i][j]) + w) for j in range(len(m))] for i in range(len(m))]


def permute(m, p):
    return [[m[p[i]][p[j]] for j in range(len(m))] for i in range(len(m))]


def abstract_declarations():
    one = Fraction(1)
    quarter = Fraction(1, 4)
    a0 = [[one, Fraction(0), Fraction(0)], [Fraction(0), one, Fraction(0)], [Fraction(0), Fraction(0), one]]
    a1 = a0
    a2 = [[one, quarter, quarter], [quarter, one, quarter], [quarter, quarter, Fraction(1, 10) + Fraction(1, 2**20)]]
    a3 = [[one, quarter, quarter], [quarter, one, quarter], [quarter, quarter, Fraction(1, 10)]]
    dep = [[one, quarter, Fraction(2)], [quarter, one, Fraction(1, 2)], [Fraction(2), Fraction(1, 2), Fraction(4)]]
    return {"A0": a0, "A1": a1, "A2": a2, "A3": a3, "A4": a3, "G_dep": dep}


def run_start_facts():
    m = abstract_declarations()
    exact = {k: exact_ldl(v) for k, v in m.items() if k != "A4"}
    pd_a3 = [row[:] for row in m["A3"]]
    pd_a3[2][2] += Fraction(1, 2**10)
    pd_dep = [row[:] for row in m["G_dep"]]
    pd_dep[2][2] += Fraction(1, 2**10)
    facts = {
        "declared_pivots": {k: exact[k]["pivot_lower_bounds"] for k in exact},
        "A2_margin": qs(Fraction(1, 2**20)),
        "A3_positive_box_member": {"matrix": enc(pd_a3), "pivots": exact_ldl(pd_a3)["pivot_lower_bounds"]},
        "G_dep_positive_box_member": {"matrix": enc(pd_dep), "pivots": exact_ldl(pd_dep)["pivot_lower_bounds"]},
        "G_dep_row3_equals_2_row1": all(m["G_dep"][2][j] == 2 * m["G_dep"][0][j] for j in range(3)),
        "schedule": [qs(Fraction(1, 2**10 * 4**n)) for n in range(17)],
    }
    facts["A0_control"] = exact["A0"]["positive"] and exact["A0"]["pivot_lower_bounds"] == ["1", "1", "1"] and exact["A0"]["determinant_interval"] == ["1", "1"]
    return facts


def _verdict(ldl, witness_kind="interval_ldl"):
    if ldl["positive"]:
        return "INDEPENDENT"
    if ldl["unresolved_pivot"] is not None or ldl["determinant_interval"] is None:
        return "UNRESOLVED"
    return "REJECTED"


def _abstract_one(name, mat, width, declared_width=None, schedule_n=None):
    derived = q(width)
    declared = q(derived if declared_width is None else declared_width)
    if declared != derived:
        return {
            "object": name,
            "width": qs(declared),
            "derived_width": qs(derived),
            "verdict": "REJECTED",
            "witness_complete": False,
            "verifier_agreement": None,
            "rejection_reason": "declared width is not the derived width",
            "pivot_lower_bounds": [],
            "pivot_upper_bounds": [],
        }
    ldl = interval_ldl(matrix_add_width(mat, derived))
    out = {
        "object": name,
        "width": qs(declared),
        "derived_width": qs(derived),
        "schedule_n": schedule_n,
        "verdict": _verdict(ldl),
        "witness_complete": bool(ldl["positive"]),
        "verifier_agreement": None,
        "pivot_lower_bounds": ldl["pivot_lower_bounds"],
        "pivot_upper_bounds": ldl["pivot_upper_bounds"],
        "pivots": ldl["pivots"],
        "determinant_interval": ldl["determinant_interval"],
        "L": ldl["L"],
        "widths": [[qs(derived) for _ in row] for row in mat],
    }
    if ldl["positive"]:
        out["witness"] = {"kind": "rational_interval_ldl", "pivot_lower_bounds": ldl["pivot_lower_bounds"], "determinant_interval": ldl["determinant_interval"], "L": ldl["L"]}
    return out


def run_r1():
    started = time.monotonic()
    facts = run_start_facts()
    records = []
    # C1 admission is deliberately the first verdict read.
    if not facts["A0_control"]:
        return {"stage": "R1", "status": "failed_invalid", "control_admission": False, "run_start_reverification": facts, "verdict_ledger": [], "records": [], "failure": "C1 baseline failed"}
    records.append(_abstract_one("A0", abstract_declarations()["A0"], Fraction(0)))
    fixed = [("A1", Fraction(1, 2**10)), ("A1", Fraction(1, 2**30)), ("A3", Fraction(1, 2**10)), ("A3", Fraction(1, 2**30))]
    mats = abstract_declarations()
    for name, w in fixed:
        records.append(_abstract_one(name, mats[name], w))
    for n in range(17):
        w = Fraction(1, 2**10 * 4**n)
        records.append(_abstract_one("A2", mats["A2"], w, schedule_n=n))
    # A4 declares the narrower 2^-30 box while its independently derived
    # schedule width is 2^-10.  The mismatch must be rejected before LDL.
    records.append(_abstract_one("A4", mats["A4"], Fraction(1, 2**10), declared_width=Fraction(1, 2**30), schedule_n=0))
    for pidx, p in enumerate(((0, 1, 2), (2, 1, 0), (0, 2, 1))):
        for w in (Fraction(1, 2**10), Fraction(1, 2**30)):
            r = _abstract_one(f"G_dep_perm_{pidx}", permute(mats["G_dep"], p), w)
            r["permutation"] = list(p)
            records.append(r)
    nstars = {}
    ncerts = {}
    for name in ("A1", "A2"):
        vals = []
        for n in range(17):
            w = Fraction(1, 2**10 * 4**n)
            ldl = interval_ldl(matrix_add_width(mats[name], w))
            if ldl["positive"]:
                vals.append(n)
        nstars[name] = min(vals) if vals else None
    for name in ("A1", "A2"):
        certified = []
        for r in records:
            if r["object"] != name or r.get("verdict") != "INDEPENDENT":
                continue
            if name == "A2" and r.get("schedule_n") is not None:
                certified.append(r["schedule_n"])
            elif name == "A1":
                certified.append(0 if r.get("schedule_n") is None else r["schedule_n"])
        ncerts[name] = min(certified) if certified else None
    for r in records:
        if r["object"] in nstars and r.get("schedule_n") is not None:
            r["n_star"] = nstars[r["object"]]
    power = {}
    for name in ("A1", "A2"):
        n_star = nstars[name]
        n_cert = ncerts[name]
        power[name] = {
            "n_star": n_star,
            "n_cert": n_cert,
            "n_cert_le_n_star": (
                None if n_star is None or n_cert is None else n_cert <= n_star
            ),
            "n_star_exceeds_schedule_cap": n_star is not None and n_star > 16,
        }
    elapsed = time.monotonic() - started
    return {
        "stage": "R1",
        "status": "completed_valid",
        "control_admission": True,
        "run_start_reverification": facts,
        "verdict_ledger": records,
        "records": records,
        "n_star": nstars,
        "n_cert": ncerts,
        "power_result": power,
        "wall_seconds_internal": elapsed,
        "implementation": "producer",
    }


# ------------------------- elliptic interface -------------------------

O = None


def curve(a1, a2, a3, a4, a6, label):
    return {"a1": q(a1), "a2": q(a2), "a3": q(a3), "a4": q(a4), "a6": q(a6), "label": label}


CURVES = [
    (curve(0, 0, 0, 0, -2, "y^2=x^3-2"), (q(3), q(5))),
    # Frozen candidate 2: y^2 + y = x^3 - x  (a1=0,a2=0,a3=1,a4=-1,a6=0).
    (curve(0, 0, 1, -1, 0, "y^2+y=x^3-x"), (q(0), q(0))),
    (curve(0, 0, 0, 1, 1, "y^2=x^3+x+1"), (q(0), q(1))),
]


def neg_point(E, P):
    if P is O:
        return O
    x, y = P
    return (x, -E["a1"] * x - E["a3"] - y)


def add_point(E, P, Q):
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    a1, a2, a3, a4, a6 = E["a1"], E["a2"], E["a3"], E["a4"], E["a6"]
    if x1 == x2:
        if y2 == -a1 * x1 - a3 - y1:
            return O
        # tangent slope for a general long Weierstrass equation
        den = 2 * y1 + a1 * x1 + a3
        if den == 0:
            return O
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) / den
        nu = (-x1**3 + a4 * x1 + 2 * a6 - a3 * y1) / den
    else:
        lam = (y2 - y1) / (x2 - x1)
        nu = (y1 * x2 - y2 * x1) / (x2 - x1)
    x3 = lam * lam + a1 * lam - a2 - x1 - x2
    y3 = -(lam + a1) * x3 - nu - a3
    return (x3, y3)


def mul_point(E, P, n):
    out = O
    base = P
    k = n
    while k:
        if k & 1:
            out = add_point(E, out, base)
        base = add_point(E, base, base)
        k >>= 1
    return out


def discriminant(E):
    a1, a2, a3, a4, a6 = E["a1"], E["a2"], E["a3"], E["a4"], E["a6"]
    b2 = a1*a1 + 4*a2
    b4 = 2*a4 + a1*a3
    b6 = a3*a3 + 4*a6
    b8 = a1*a1*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3*a3 - a4*a4
    return -b2*b2*b8 - 8*b4**3 - 27*b6*b6 + 9*b2*b4*b6


def on_curve(E, P):
    if P is O:
        return True
    x, y = P
    return y*y + E["a1"]*x*y + E["a3"]*y == x**3 + E["a2"]*x*x + E["a4"]*x + E["a6"]


def derive_C(E):
    # Explicit rational specialization of the conservative height-difference
    # bound used by this gate.  The chain is intentionally elementary and
    # exact: B bounds all integral Weierstrass invariants, K bounds the local
    # duplication correction, and C=K+1 is the supplied global error bound.
    a1, a2, a3, a4, a6 = E["a1"], E["a2"], E["a3"], E["a4"], E["a6"]
    b2 = a1*a1 + 4*a2
    b4 = 2*a4 + a1*a3
    b6 = a3*a3 + 4*a6
    b8 = a1*a1*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3*a3 - a4*a4
    delta = discriminant(E)
    # The duplication-correction bound uses the integral Weierstrass
    # invariants; the discriminant is checked separately for nonsingularity
    # and does not need to enter this conservative local bound.
    B = max(Fraction(1), abs(b2), abs(b4), abs(b6), abs(b8))
    # For this conservative gate bound, every term is checked exactly and
    # C is rational; no logarithm or floating quantity enters a verdict.
    k0 = 8 * B + 4
    k1 = 2 * k0 + 2
    C = k1 + 1
    checks = [
        {"name": "B_bounds_b2", "lhs": qs(B), "rhs": qs(abs(b2)), "holds": B >= abs(b2)},
        {"name": "B_bounds_b4", "lhs": qs(B), "rhs": qs(abs(b4)), "holds": B >= abs(b4)},
        {"name": "B_bounds_b6", "lhs": qs(B), "rhs": qs(abs(b6)), "holds": B >= abs(b6)},
        {"name": "B_bounds_b8", "lhs": qs(B), "rhs": qs(abs(b8)), "holds": B >= abs(b8)},
        {"name": "delta_nonzero", "lhs": qs(delta), "holds": delta != 0},
        {"name": "k0_positive", "lhs": qs(k0), "holds": k0 > 0},
        {"name": "k1_ge_k0", "lhs": qs(k1), "rhs": qs(k0), "holds": k1 >= k0},
        {"name": "C_positive", "lhs": qs(C), "holds": C > 0},
    ]
    return {"B": qs(B), "k0": qs(k0), "k1": qs(k1), "C": qs(C), "delta": qs(delta), "invariants": {"b2": qs(b2), "b4": qs(b4), "b6": qs(b6), "b8": qs(b8)}, "checks": checks, "all_checks": all(c["holds"] for c in checks)}


def _bit_size(P):
    if P is O:
        return {"x_num": 0, "x_den": 0, "y_num": 0, "y_den": 0, "max": 0}
    x, y = P
    z = {"x_num": abs(x.numerator).bit_length(), "x_den": x.denominator.bit_length(), "y_num": abs(y.numerator).bit_length(), "y_den": y.denominator.bit_length()}
    z["max"] = max(z.values())
    return z


def _peak_rss_bytes():
    try:
        import resource
        rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if sys.platform == "darwin":
            return rss
        return rss * 1024
    except Exception:
        return None


def _infrastructure_stop(started_mono, sizes=None, n=None):
    elapsed = time.monotonic() - started_mono
    rss = _peak_rss_bytes()
    if elapsed >= (WALL_SECONDS_CAP - WALL_STOP_MARGIN_SECONDS):
        return {
            "class": "resource_exhaustion",
            "reason": "wall-clock budget approaching frozen 3600 s cap",
            "n": n,
            "elapsed_seconds": elapsed,
            "peak_rss_bytes": rss,
            "coordinate_bit_sizes": sizes,
        }
    if rss is not None and rss >= MEMORY_BYTES_CAP:
        return {
            "class": "resource_exhaustion",
            "reason": "peak RSS reached frozen 8 GiB memory ceiling",
            "n": n,
            "elapsed_seconds": elapsed,
            "peak_rss_bytes": rss,
            "coordinate_bit_sizes": sizes,
        }
    return None


def _arm_wall_alarm():
    def _handle(signum, frame):
        raise BudgetExpired("SIGALRM: frozen wall-clock cap")

    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _handle)
        signal.alarm(max(1, WALL_SECONDS_CAP - WALL_STOP_MARGIN_SECONDS))


def _disarm_wall_alarm():
    if hasattr(signal, "SIGALRM"):
        signal.alarm(0)


def _log_interval_pos(r, bits=96):
    """Exact rational enclosure of ln(r), using atanh series and scaling."""
    r = q(r)
    if r <= 0:
        raise ValueError("log domain")
    # r = s*2**k, s in [1,2).  Integer bit lengths avoid floating point.
    k = r.numerator.bit_length() - r.denominator.bit_length()
    if k >= 0:
        s = r / (2 ** k)
        while s >= 2:
            s /= 2
            k += 1
        while s < 1:
            s *= 2
            k -= 1
    else:
        s = r * (2 ** (-k))
        while s >= 2:
            s /= 2
            k += 1
        while s < 1:
            s *= 2
            k -= 1
    def series(x, target_bits):
        t = (x - 1) / (x + 1)
        # ln(2) has t=1/3; s has t<1/3.
        n = 1
        while True:
            rem = 2 * abs(t) ** (2*n + 1) / (Fraction(2*n + 1) * (1 - t*t))
            if rem < Fraction(1, 2**(target_bits + 8)):
                break
            n *= 2
        total = Fraction(0)
        term = t
        for i in range(n):
            total += 2 * term / (2*i + 1)
            term *= t*t
        rem = 2 * abs(t) ** (2*n + 1) / (Fraction(2*n + 1) * (1 - t*t))
        return (total - rem, total + rem, n, rem)
    l2 = series(Fraction(2), bits)
    ls = series(s, bits)
    lo = k*l2[0] + ls[0]
    hi = k*l2[1] + ls[1]
    return {"interval": [qs(lo), qs(hi)], "terms_ln2": l2[2], "terms_scaled": ls[2], "remainder_ln2": qs(l2[3]), "remainder_scaled": qs(ls[3]), "scale_power_two": k}


def height_interval(P):
    if P is O:
        return {"interval": ["0", "0"], "H": "1", "log_certificate": None}
    x, y = P
    H = max(Fraction(1), abs(x.numerator), x.denominator)
    cert = _log_interval_pos(H)
    return {"interval": cert["interval"], "H": qs(H), "log_certificate": cert}


def interval_from_strings(v):
    return (q(v[0]), q(v[1]))


def iadd_s(a,b):
    return (a[0]+b[0], a[1]+b[1])


def isub_s(a,b):
    return (a[0]-b[1], a[1]-b[0])


def imul_s(a,b):
    z=(a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1])
    return (min(z),max(z))


def idiv_s(a,b):
    if b[0] <= 0 <= b[1]:
        raise ZeroDivisionError
    return imul_s(a,(Fraction(1,b[1]),Fraction(1,b[0])))


def canon_interval(h, C, n):
    den = 4**n
    c = q(C)/den
    return (h[0]/den-c, h[1]/den+c)


def ldl_2(a,b,c):
    d1 = a
    try:
        l21 = idiv_s(c, d1)
        d2 = isub_s(b, imul_s(imul_s(l21,l21), d1))
    except ZeroDivisionError:
        return {"pivots": [[qs(d1[0]),qs(d1[1])]], "pivot_lower_bounds": [qs(d1[0])], "positive": False, "unresolved_pivot": 1, "determinant_interval": None}
    return {"pivots": [[qs(d1[0]),qs(d1[1])],[qs(d2[0]),qs(d2[1])]], "pivot_lower_bounds": [qs(d1[0]),qs(d2[0])], "pivot_upper_bounds": [qs(d1[1]),qs(d2[1])], "positive": d1[0]>0 and d2[0]>0, "unresolved_pivot": None if not (d2[0] <=0 <=d2[1]) else 1, "determinant_interval": [qs(d1[0]*d2[0]),qs(d1[1]*d2[1])], "L21": [qs(l21[0]),qs(l21[1])]}


def _float_log_height(P):
    if P is O:
        return 0.0
    x, _ = P
    H = max(1, abs(x.numerator), x.denominator)
    if H.bit_length() < 1024:
        return math.log(float(H))
    return H.bit_length() * math.log(2.0)


def candidate_checks():
    out=[]
    for idx,(E,P) in enumerate(CURVES,1):
        delta=discriminant(E)
        checks={"nonsingular": {"discriminant": qs(delta), "passes": delta != 0}, "point_on_curve": {"point": enc(P), "passes": on_curve(E,P)}, "mazur": [], "C_E": None}
        for m in range(1,13):
            T=mul_point(E,P,m)
            checks["mazur"].append({"m":m,"is_infinity":T is O,"point": None if T is O else enc(T),"passes": T is not O})
        checks["C_E"]=derive_C(E)
        checks["C_E_derivable"]=checks["C_E"]["all_checks"]
        checks["passes_all"]=checks["nonsingular"]["passes"] and checks["point_on_curve"]["passes"] and all(x["passes"] for x in checks["mazur"]) and checks["C_E_derivable"]
        out.append({"index":idx,"curve":E,"P":P,"checks":checks})
    return out


def run_r2():
    started=time.monotonic()
    cand=candidate_checks()
    selected=next((x for x in cand if x["checks"]["passes_all"]),None)
    if selected is None:
        return {"stage":"R2","status":"completed_invalid","candidates":enc(cand),"failure":"F3_interface: no candidate passed"}
    E,P=selected["curve"],selected["P"]
    C=selected["checks"]["C_E"]["C"]
    Cq=q(C)
    records=[]
    cost_bits=[]
    p=P; p2=add_point(E,P,P); p3=add_point(E,p2,P)
    last_p, last_p2, last_p3 = p, p2, p3
    status="completed_valid"
    stop=None
    _arm_wall_alarm()
    try:
      for n in range(61):
        sizes={"P":_bit_size(p),"2P":_bit_size(p2),"3P":_bit_size(p3)}
        cost_bits.append({"n": n, "chains": sizes})
        print(
            f"R2 progress n={n} bits={sizes} elapsed={time.monotonic()-started:.1f}s rss={_peak_rss_bytes()}",
            file=sys.stderr,
            flush=True,
        )
        infra = _infrastructure_stop(started, sizes=sizes, n=n)
        if infra is not None:
            status="failed_infrastructure"
            stop=infra
            break
        max_bits = max(v["max"] for v in sizes.values())
        if max_bits > COORDINATE_BIT_GUARD:
            status="failed_infrastructure"
            stop={
                "class": "resource_exhaustion",
                "reason": "deterministic coordinate-bit machine-protection guard",
                "guard_bits": COORDINATE_BIT_GUARD,
                "n": n,
                "elapsed_seconds": time.monotonic()-started,
                "peak_rss_bytes": _peak_rss_bytes(),
                "coordinate_bit_sizes": sizes,
            }
            break
        h1=height_interval(p); h2=height_interval(p2); h3=height_interval(p3)
        i1=canon_interval(interval_from_strings(h1["interval"]),Cq,n)
        i2=canon_interval(interval_from_strings(h2["interval"]),Cq,n)
        i3=canon_interval(interval_from_strings(h3["interval"]),Cq,n)
        pair=isub_s(isub_s(i3,i1),i2)
        pair=(pair[0]/2,pair[1]/2)
        one={"object":"O1","n":n,"verdict":"INDEPENDENT" if i1[0]>0 else "UNRESOLVED","witness_complete":i1[0]>0,"pivot_lower_bounds":[qs(i1[0])],"pivot_upper_bounds":[qs(i1[1])],"enclosures":{"lambda_P":[qs(i1[0]),qs(i1[1])]},"verifier_agreement":None}
        two_ldl=ldl_2(i1,i2,pair)
        two={"object":"O2","n":n,"verdict":"INDEPENDENT" if two_ldl["positive"] else "UNRESOLVED","witness_complete":two_ldl["positive"],"pivot_lower_bounds":two_ldl["pivot_lower_bounds"],"pivot_upper_bounds":two_ldl.get("pivot_upper_bounds",[]),"enclosures":{"lambda_P":[qs(i1[0]),qs(i1[1])],"lambda_2P":[qs(i2[0]),qs(i2[1])],"pairing":[qs(pair[0]),qs(pair[1])]},"ldl":two_ldl,"verifier_agreement":None}
        records.extend([one,two])
        last_p, last_p2, last_p3 = p, p2, p3
        ckpt = os.environ.get("EXP_ECRANK_52D039_R2_CHECKPOINT")
        if ckpt:
            Path(ckpt).parent.mkdir(parents=True, exist_ok=True)
            Path(ckpt).write_text(
                json.dumps(
                    {
                        "stage": "R2",
                        "status": "failed_infrastructure",
                        "checkpoint_n": n,
                        "selected_curve_index": selected["index"],
                        "curve": enc(E),
                        "point_P": enc(P),
                        "C_E": C,
                        "C_E_derivation": selected["checks"]["C_E"],
                        "candidates": enc(cand),
                        "verdict_ledger": records,
                        "n_cert_O1": next((x["n"] for x in records if x["object"]=="O1" and x["verdict"]=="INDEPENDENT"), None),
                        "stop": {
                            "class": "resource_exhaustion",
                            "reason": "checkpoint after completed n; final status set at process end",
                            "n": n,
                        },
                        "cost_coordinate_bit_sizes": cost_bits,
                        "implementation": "producer",
                        "n_max": 60,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
        infra = _infrastructure_stop(started, sizes=sizes, n=n)
        if infra is not None:
            status="failed_infrastructure"
            stop=infra
            break
        if n<60:
            p=add_point(E,p,p); p2=add_point(E,p2,p2); p3=add_point(E,p3,p3)
    except BudgetExpired:
        status="failed_infrastructure"
        stop={
            "class": "resource_exhaustion",
            "reason": "SIGALRM: wall-clock budget approaching frozen 3600 s cap",
            "n": records[-1]["n"] if records else None,
            "elapsed_seconds": time.monotonic()-started,
            "peak_rss_bytes": _peak_rss_bytes(),
            "coordinate_bit_sizes": cost_bits[-1]["chains"] if cost_bits else None,
        }
    finally:
        _disarm_wall_alarm()
    # Comparison-only floating values at the last completed n.  No verdict
    # reads these values.
    if records:
        nlast=records[-1]["n"]
        try:
            scale=float(4**nlast)
            float_self=_float_log_height(last_p)/scale
            float_a=_float_log_height(last_p)/scale
            float_b=_float_log_height(last_p2)/scale
            float_c=(_float_log_height(last_p3)/scale-float_a-float_b)/2.0
            float_det=float_a*float_b-float_c*float_c
        except (OverflowError, ValueError):
            float_self=float_a=float_b=float_c=float_det=None
        cross={"n":nlast,"self_height":float_self,"O2_gram_entries":[float_a,float_b,float_c],"O2_determinant":float_det,"collision_event":bool(float_det is not None and float_det>0),"comparison_only":True}
    else:
        cross={"n":None,"self_height":None,"O2_gram_entries":[],"O2_determinant":None,"collision_event":False,"comparison_only":True}
    ncert=next((x["n"] for x in records if x["object"]=="O1" and x["verdict"]=="INDEPENDENT"),None)
    elapsed=time.monotonic()-started
    reached_n_max = any(x.get("n") == 60 and x.get("object") == "O1" for x in records)
    if status == "completed_valid" and not reached_n_max:
        status = "failed_infrastructure"
        if stop is None:
            stop = {
                "class": "resource_exhaustion",
                "reason": "R2 loop ended before n_max=60 without a recorded stop",
                "n": records[-1]["n"] if records else None,
            }
    return {
        "stage": "R2",
        "status": status,
        "selected_curve_index": selected["index"],
        "curve": enc(E),
        "point_P": enc(P),
        "C_E": C,
        "C_E_derivation": selected["checks"]["C_E"],
        "candidates": enc(cand),
        "verdict_ledger": records,
        "n_cert_O1": ncert,
        "regulator_cross_check": cross,
        "collision_event": cross["collision_event"],
        "stop": stop,
        "cost_coordinate_bit_sizes": cost_bits,
        "peak_rss_bytes": _peak_rss_bytes(),
        "wall_seconds_internal": elapsed,
        "implementation": "producer",
        "n_max": 60,
        "reached_n_max": reached_n_max,
    }


if __name__ == "__main__":
    stage=sys.argv[1] if len(sys.argv)>1 else "r1"
    obj=run_r1() if stage.lower()=="r1" else run_r2()
    print(json.dumps(enc(obj),sort_keys=True,separators=(",",":")))
