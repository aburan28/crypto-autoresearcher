"""Domain arithmetic for EXP-ICINV-fcb497 (GOAL-ENDO-001).

Measures m = ord_d(lambda), the extension degree of the field of definition of a
generator of the kernel of the Z[pi]-minimal non-scalar endomorphism of an
ordinary E/F_p, on the frozen seven-decade prime ladder, against a MATCHED
random-unit null and a BLOCKING planted control.

EVERY constant in the FROZEN block below is copied from the approved contract
`experiments/EXP-ICINV-fcb497/specification.yaml` and may not be changed except
by a versioned protocol_amendment.  Nothing in this module retrieves anything,
quotes anything, or writes a run record: retrieval lives in
`harness/velu_stage0.py` and run packaging in `harness/run_kerfield.py`.

EDIT PROHIBITION HONOURED: this module imports only `harness.toycurve`,
`sympy` and the standard library.  It does not import or touch
harness/exp_icinv.py, harness/exp_icinv_fullgroup.py, harness/run_fullgroup.py,
harness/run_saturation.py or harness/isogeny_class.py, whose committed runs must
stay reproducible byte-for-byte.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field

import sympy

from .toycurve import EllipticCurve

EXP_ID = "EXP-ICINV-fcb497"
HYPOTHESIS_ID = "H-ICINV-82ee6a"
GOAL_ID = "GOAL-ENDO-001"
HANDOFF_ID = "TASK-20260807-f9c69c"
REQUESTED_POLICY = "executor-implementation"      # from the handoff, verbatim

# ---------------------------------------------------------------------------
# FROZEN (specification.yaml, status: approved, DEC-20260807-1538f8)
# ---------------------------------------------------------------------------
# curve_sampling_frozen.prime_ladder_rule: the largest prime STRICTLY BELOW 2^k.
# The contract froze a RULE and refused to write literals; the ladder is
# computed and primality-verified at run time by `prime_ladder()`.
LADDER_EXPONENTS = (12, 14, 16, 18, 20, 22, 24)
CURVES_PER_DECADE_FLOOR = 400
CURVES_PER_DECADE_TARGET = 1000
ATTEMPT_CAP_PER_DECADE = 4000
SEEDS = (20260807, 20260814, 11235813)
DEGREE_WINDOW_K = 5                               # minimisation_rule: k = 5
PLANTED_R = (3, 5, 7, 11, 17, 33, 65, 129, 1025, 65537)
FIXTURE_ELLS = (3, 5, 7, 11, 13)
FIXTURE_CURVES = 3
FIXTURE_ELLS_PER_CURVE = 3
ORDER_CERT_POINTS = 3                             # ">= 3 independently sampled points"
CONDUCTOR_BINS = ("f == 1", "2 <= f <= 10", "f > 10")
CONDUCTOR_SECONDARY_BOUND = 100                   # O-minimal secondary where f <= 100
KS_CRITICAL_COEFF = 1.358                         # level 0.05, two-sample
D_MIN_RESOLVABLE = 0.10                           # effects below this are UNRESOLVABLE
DEGENERATE_INVALIDATION_FRACTION = 0.20           # F-v
DECADE_EXCLUSION_INVALIDATION_FRACTION = 0.01     # invalidation_rules
MEMORY_RECONCILIATION_BAND = (0.25, 4.0)


# ---------------------------------------------------------------------------
# deterministic streams (curve_sampling_frozen.curve_stream, matched_null_frozen)
# ---------------------------------------------------------------------------
def _h(tag: str) -> int:
    return int(hashlib.sha256(tag.encode()).hexdigest(), 16)


def curve_param(seed: int, p: int, which: str, i: int) -> int:
    """a = int(sha256(f"{seed}:{p}:a:{i}"),16) mod p   (contract, verbatim shape)."""
    return _h(f"{seed}:{p}:{which}:{i}") % p


def null_unit_draw(seed: int, p: int, i: int, d: int) -> tuple[int, int]:
    """A uniform unit mod d from the independent null stream.

    Contract: a = int(sha256(f"{seed}:null:{p}:{i}"),16) mod d, REDRAWN while
    gcd(a, d) > 1.  The contract fixes the first tag and not the redraw tag;
    redraws append ":r{j}" (j = 1, 2, ...).  DECLARED in implementation.md.
    Returns (a, redraws).
    """
    a = _h(f"{seed}:null:{p}:{i}") % d
    j = 0
    while math.gcd(a, d) != 1:
        j += 1
        a = _h(f"{seed}:null:{p}:{i}:r{j}") % d
    return a, j


# ---------------------------------------------------------------------------
# prime ladder
# ---------------------------------------------------------------------------
def prime_ladder() -> list[dict]:
    """The seven ladder primes, each certified prime and maximal below 2^k."""
    out = []
    for k in LADDER_EXPONENTS:
        p = int(sympy.prevprime(2 ** k))
        assert sympy.isprime(p) and p < 2 ** k
        # maximality: nothing prime strictly between p and 2^k
        assert int(sympy.nextprime(p)) >= 2 ** k
        out.append({
            "k": k, "p": p, "bits": p.bit_length(),
            "primality_test": "sympy.isprime (BPSW: strong Lucas + Miller-Rabin)",
            "maximality_check": "sympy.nextprime(p) >= 2**k",
            "sympy_version": sympy.__version__,
        })
    return out


# ---------------------------------------------------------------------------
# exact integer factorisation, verified (factorisation_rule)
# ---------------------------------------------------------------------------
def factor_exact(n: int) -> tuple[dict[int, int], bool]:
    """Trial division to floor(sqrt(n)); returns (factorisation, verified).

    `verified` re-multiplies the recorded prime powers and compares to n, which
    is the control that makes a SILENTLY TRUNCATED factorisation detectable
    (the canonical artifact tell this contract is built to catch).
    """
    if n <= 0:
        return {}, False
    fac: dict[int, int] = {}
    m = n
    q = 2
    while q * q <= m:
        while m % q == 0:
            fac[q] = fac.get(q, 0) + 1
            m //= q
        q += 1 if q == 2 else 2
    if m > 1:
        fac[m] = fac.get(m, 0) + 1
    prod = 1
    for pr, e in fac.items():
        prod *= pr ** e
    return fac, prod == n


def carmichael_from_factorisation(fac: dict[int, int]) -> int:
    lam = 1
    for q, e in fac.items():
        if q == 2:
            c = 1 if e == 1 else (2 if e == 2 else 2 ** (e - 2))
        else:
            c = (q - 1) * q ** (e - 1)
        lam = lam * c // math.gcd(lam, c)
    return lam


def multiplicative_order(a: int, d: int) -> dict:
    """m = ord_d(a), with the contract's two verifications recorded.

    THE SINGLE SHARED CODE PATH.  Stage 3, the matched null, the planted
    control and the m = 1 nearby-object fixture all call THIS function; the
    contract requires the fixture's m to come from the same code path as
    stage 3, and this is how that is made true rather than asserted.
    """
    if d <= 1 or math.gcd(a % d, d) != 1:
        return {"m": None, "ok": False, "reason": "a is not a unit mod d",
                "pow_check": None, "minimality_check": None}
    a %= d
    dfac, dver = factor_exact(d)
    if not dver:
        return {"m": None, "ok": False, "reason": "d factorisation unverified",
                "pow_check": None, "minimality_check": None}
    lam = carmichael_from_factorisation(dfac)
    m = lam
    lamfac, lamver = factor_exact(lam)
    if not lamver:
        return {"m": None, "ok": False, "reason": "carmichael factorisation unverified",
                "pow_check": None, "minimality_check": None}
    for q in sorted(lamfac):
        while m % q == 0 and pow(a, m // q, d) == 1:
            m //= q
    pow_check = pow(a, m, d) == 1
    mfac, mver = factor_exact(m) if m > 1 else ({}, True)
    minimality = mver and all(pow(a, m // q, d) != 1 for q in mfac)
    return {"m": m, "ok": bool(pow_check and minimality), "reason": None,
            "pow_check": bool(pow_check), "minimality_check": bool(minimality),
            "order_factorisation": {str(k): v for k, v in mfac.items()},
            "carmichael_lambda": lam}


def unit_order_cdf_fraction(fac: dict[int, int], bound: int) -> float:
    """Exact fraction of units mod d whose multiplicative order is <= bound.

    Computed from the factorisation of d by CRT: the order of a unit is the lcm
    of its orders in each (Z/q^e)^*, each of which is cyclic (or C2 x C2^{e-2}
    for 2^e, e >= 3).  Used by the SMALL-ORDER OUTLIER tail check, which asks
    how rare an observed small m actually is.
    """
    groups: list[list[int]] = []
    for q, e in sorted(fac.items()):
        if q == 2:
            if e == 1:
                groups.append([1])
            elif e == 2:
                groups.append([2])
            else:
                groups.append([2, 2 ** (e - 2)])
        else:
            groups.append([(q - 1) * q ** (e - 1)])
    cyclic = [n for g in groups for n in g]
    # distribution of orders in each cyclic factor: #{x : ord(x) = t} = phi(t)
    dists: list[dict[int, int]] = []
    for n in cyclic:
        dist: dict[int, int] = {}
        for t in sympy.divisors(n):
            dist[int(t)] = int(sympy.totient(t))
        dists.append(dist)
    acc = {1: 1}
    for dist in dists:
        nxt: dict[int, int] = {}
        for o1, c1 in acc.items():
            for o2, c2 in dist.items():
                o = o1 * o2 // math.gcd(o1, o2)
                nxt[o] = nxt.get(o, 0) + c1 * c2
        acc = nxt
    total = sum(acc.values())
    le = sum(c for o, c in acc.items() if o <= bound)
    return le / total if total else float("nan")


# ---------------------------------------------------------------------------
# curve order certificate (order_certificate_required_per_curve)
# ---------------------------------------------------------------------------
def _bsgs_annihilator(E: EllipticCurve, Q, p: int) -> int | None:
    """Some n in the Hasse interval with n*Q = O, by baby-step/giant-step."""
    h = math.isqrt(4 * p)
    L, U = p + 1 - h, p + 1 + h
    W = U - L + 1
    w = math.isqrt(W) + 1
    baby: dict = {}
    R = None
    for j in range(w):
        if R not in baby:
            baby[R] = j
        R = E.add(R, Q)
    G = R                                  # w*Q
    negG = E.negate(G)
    cur = E.mul(L, Q)
    for i in range(W // w + 2):
        neg = E.negate(cur)
        if neg in baby:                    # (L+i*w)Q = -jQ  =>  (L+i*w+j)Q = O
            n = L + i * w + baby[neg]
            if L <= n <= U:
                return n
        if cur in baby:                    # (L+i*w)Q = jQ  =>  (L+i*w-j)Q = O
            n = L + i * w - baby[cur]
            if L <= n <= U:
                return n
        cur = E.add(cur, G)
    return None


def point_order(E: EllipticCurve, Q, p: int) -> int | None:
    n = _bsgs_annihilator(E, Q, p)
    if n is None:
        return None
    fac, ver = factor_exact(n)
    if not ver:
        return None
    for q in sorted(fac):
        while n % q == 0 and E.mul(n // q, Q) is None:
            n //= q
    return n


def order_certificate(E: EllipticCurve, p: int, seed: int, tag: str) -> dict:
    """#E by BSGS with a UNIQUENESS flag, per the frozen certificate rule."""
    h = math.isqrt(4 * p)
    L, U = p + 1 - h, p + 1 + h
    pts, orders = [], []
    x = _h(f"{seed}:{tag}:x") % p
    tries = 0
    while len(pts) < ORDER_CERT_POINTS and tries < 200:
        tries += 1
        Q = E.lift_x(x)
        x = (x + 1) % p
        if Q is None or Q in pts:
            continue
        o = point_order(E, Q, p)
        if o is None:
            return {"order": None, "unique": False, "reason": "point order failed",
                    "points_used": len(pts)}
        pts.append(Q)
        orders.append(o)
    if len(pts) < ORDER_CERT_POINTS:
        return {"order": None, "unique": False, "reason": "too few points",
                "points_used": len(pts)}
    lam = 1
    for o in orders:
        lam = lam * o // math.gcd(lam, o)
    cands = [n for n in range(((L + lam - 1) // lam) * lam, U + 1, lam)]
    unique = len(cands) == 1
    n = cands[0] if unique else None
    annihilates = bool(n) and all(E.mul(n, Q) is None for Q in pts)
    return {"order": n if annihilates else None,
            "unique": bool(unique and annihilates),
            "reason": None if (unique and annihilates) else
                      ("not unique in Hasse interval" if not unique
                       else "annihilation check failed"),
            "candidates_in_hasse": len(cands),
            "point_orders": orders,
            "points_used": len(pts),
            "hasse_interval": [L, U],
            "annihilates_all_sampled_points": annihilates}


# ---------------------------------------------------------------------------
# endomorphism arithmetic (endomorphism_arithmetic_frozen)
# ---------------------------------------------------------------------------
def norm(u: int, v: int, t: int, p: int) -> int:
    """N(u + v pi) = u^2 + u v t + v^2 p."""
    return u * u + u * v * t + v * v * p


def degree_window(t: int, p: int, k: int = DEGREE_WINDOW_K) -> list[dict]:
    """The k smallest values of N(u + v pi) over v != 0, with their (u, v).

    N = (u + v t/2)^2 + v^2 |D|/4, so for fixed v the minimum over u is at
    u ~ -v t / 2 and N grows with v^2.  The v-range is expanded until v^2|D|/4
    already exceeds the k-th best, which makes the window PROVABLY the k
    smallest and not merely the k smallest found.
    """
    absD4 = p - t * t / 4.0                     # |D|/4 > 0 for an ordinary curve
    found: list[tuple[int, int, int]] = []
    v = 1
    while True:
        if found and len(found) >= k and v * v * absD4 > sorted(n for n, _, _ in found)[k - 1]:
            break
        for sv in (v, -v):
            u0 = int(round(-sv * t / 2))
            for du in range(-2, 3):
                u = u0 + du
                found.append((norm(u, sv, t, p), u, sv))
        v += 1
        if v > 64:                              # unreachable at toy scale; guard
            break
    seen = set()
    uniq = []
    for n, u, sv in sorted(found, key=lambda z: (z[0], abs(z[2]), z[2], abs(z[1]), z[1])):
        if (u, sv) in seen:
            continue
        seen.add((u, sv))
        uniq.append({"d": n, "u": u, "v": sv})
    return uniq[:k]


def admissibility(u: int, v: int, d: int) -> dict:
    """primitive (gcd(u,v) = 1) AND gcd(v, d) = 1."""
    g_uv = math.gcd(abs(u), abs(v))
    g_vd = math.gcd(abs(v), d)
    return {"primitive": g_uv == 1, "gcd_u_v": g_uv, "gcd_v_d": g_vd,
            "admissible": bool(g_uv == 1 and g_vd == 1)}


def eigenvalue(u: int, v: int, d: int) -> int:
    """lambda = (-u) * v^{-1} mod d (defined because gcd(v, d) = 1)."""
    return (-u) * pow(v % d, -1, d) % d


def conductor(t: int, p: int) -> dict:
    """f = [O_K : Z[pi]], from D = t^2 - 4p = D_0 f^2 with D_0 fundamental."""
    D = t * t - 4 * p
    fac, ver = factor_exact(abs(D))
    if not ver:
        return {"D": D, "f": None, "fundamental_discriminant": None,
                "verified": False}
    sq = 1
    for q, e in fac.items():
        sq *= q ** (e // 2)
    f = 1
    for cand in sorted(sympy.divisors(sq), reverse=True):
        D0 = D // (cand * cand)
        if D0 % 4 in (0, 1) and _is_fundamental(D0):
            f = int(cand)
            break
    return {"D": D, "f": f, "fundamental_discriminant": D // (f * f),
            "verified": True}


def _is_fundamental(D0: int) -> bool:
    if D0 % 4 == 1:
        return sympy.ntheory.factor_.core(abs(D0), 2) == abs(D0) or _squarefree(abs(D0))
    if D0 % 4 == 0:
        m = D0 // 4
        return (m % 4 in (2, 3)) and _squarefree(abs(m))
    return False


def _squarefree(n: int) -> bool:
    fac, ver = factor_exact(n)
    return ver and all(e == 1 for e in fac.values())


def conductor_bin(f: int | None) -> str:
    if f is None:
        return "unknown"
    if f == 1:
        return CONDUCTOR_BINS[0]
    if 2 <= f <= 10:
        return CONDUCTOR_BINS[1]
    return CONDUCTOR_BINS[2]


# ---------------------------------------------------------------------------
# cost accounting (MODELED, LOWER BOUND -- optimistic_assumptions)
# ---------------------------------------------------------------------------
def corrected_cost_log2(d: int, m: int) -> dict:
    """Otilde(sqrt(d) * m) F_p-operations.  basis: modeled; bound_kind: lower_bound.

    Conditional on the STAGE-0 verdict being KERNEL_FIELD; emitted regardless so
    the accounting is auditable, and LABELLED conditional by the caller.
    """
    return {
        "basis": "modeled",
        "bound_kind": "lower_bound",
        "time_log2_fp_ops": 0.5 * math.log2(d) + math.log2(m),
        "memory_log2_fp_elements": 0.5 * math.log2(d) + math.log2(m),
        "conditional_on": ["STAGE-0 verdict KERNEL_FIELD", "HEUR-ORD-1"],
        "formula": "Otilde(sqrt(d) * m) F_p-operations and F_p-elements",
    }


def degeneration_check(ell: int, m: int) -> dict:
    """H2: at d = ell with m = O(1) the accounting must degenerate to Otilde(sqrt ell).

    DEGENERATION IS AN EXPONENT STATEMENT, and is implemented as one: the
    corrected count Otilde(sqrt(d) * m) at d = ell is Otilde(sqrt ell) exactly
    when m does not grow with ell.  The contract admits m = 1 and, in the
    declared twisted case, m = 2; both leave the exponent of ell at 1/2 and
    differ only by the recorded constant factor log2(m), which is reported
    beside the figure rather than absorbed into it.
    """
    c = corrected_cost_log2(ell, m) if m else None
    expected = 0.5 * math.log2(ell)
    return {"ell": ell, "m": m,
            "corrected_time_log2": c["time_log2_fp_ops"] if c else None,
            "sqrt_ell_log2": expected,
            "constant_factor_log2": math.log2(m) if m else None,
            "exponent_of_ell": 0.5,
            "degenerates": bool(m in (1, 2)),
            "degeneration_criterion": "m is O(1) (m in {1, 2} per the frozen "
                                      "fixture rule), so Otilde(sqrt(ell)*m) = "
                                      "Otilde(sqrt ell); the constant factor "
                                      "log2(m) is reported, not absorbed"}


# ---------------------------------------------------------------------------
# controls
# ---------------------------------------------------------------------------
def planted_control() -> dict:
    """d = r^2 - 1, lambda = r must report m = 2 EXACTLY on every frozen r."""
    rows = []
    for r in PLANTED_R:
        d = r * r - 1
        res = multiplicative_order(r, d)
        rows.append({"r": r, "d": d, "m": res["m"], "expected_m": 2,
                     "pass": res["m"] == 2 and res["ok"],
                     "pow_check": res["pow_check"],
                     "minimality_check": res["minimality_check"],
                     "order_verification_ok": res["ok"]})
    return {"verdict": "PASS" if all(x["pass"] for x in rows) else "FAIL",
            "rows": rows,
            "construction": "r^2 = 1 mod (r^2-1) and r != 1 mod (r^2-1) for r >= 3",
            "code_path": "harness.exp_kerfield.multiplicative_order (same as STAGE 3)"}


def m1_fixture(p: int, seed: int) -> dict:
    """The m = 1 small-ell rational-eigenspace nearby-object control.

    Qualification, per the frozen rule: X^2 - tX + p has a root lambda mod ell
    AND the corresponding eigenspace of pi on E[ell] is F_p-rational -- i.e.
    lambda = 1 (pointwise rational) or lambda = -1 mod ell (the twisted case,
    which the contract admits provided the eigenvalue computation DECLARES it).
    m is then computed by the SAME code path as stage 3.
    """
    curves, skipped, i = [], [], 0
    while len(curves) < FIXTURE_CURVES and i < ATTEMPT_CAP_PER_DECADE:
        a = curve_param(seed, p, "a", i)
        b = curve_param(seed, p, "b", i)
        idx = i
        i += 1
        try:
            E = EllipticCurve(p, a, b)
        except ValueError:
            skipped.append({"index": idx, "reason": "singular"})
            continue
        cert = order_certificate(E, p, seed, f"fixture:{idx}")
        if cert["order"] is None:
            skipped.append({"index": idx, "reason": f"order certificate: {cert['reason']}"})
            continue
        t = p + 1 - cert["order"]
        if t == 0:
            skipped.append({"index": idx, "reason": "supersingular (t = 0)"})
            continue
        qual = []
        for ell in FIXTURE_ELLS:
            roots = sorted({r for r in range(ell) if (r * r - t * r + p) % ell == 0})
            rational = [r for r in roots if r % ell in (1 % ell, (ell - 1) % ell)]
            if not rational:
                continue
            lam = rational[0]
            res = multiplicative_order(lam, ell)
            qual.append({
                "ell": ell, "eigenvalues_mod_ell": roots, "lambda": lam,
                "eigenvalue_case": "lambda = 1 (pointwise F_p-rational kernel)"
                                   if lam % ell == 1 % ell else
                                   "lambda = -1 (TWISTED case, declared by the "
                                   "eigenvalue computation)",
                "m": res["m"], "order_verification_ok": res["ok"],
                "pow_check": res["pow_check"],
                "minimality_check": res["minimality_check"],
                "degeneration": degeneration_check(ell, res["m"] or 0),
                "pass": bool(res["m"] in (1, 2) and res["ok"]
                             and degeneration_check(ell, res["m"])["degenerates"]),
            })
        if len(qual) < FIXTURE_ELLS_PER_CURVE:
            skipped.append({"index": idx, "reason": "shortfall: only "
                            f"{len(qual)} qualifying ell",
                            "qualifying": [q["ell"] for q in qual]})
            continue
        curves.append({"index": idx, "p": p, "a": a, "b": b, "order": cert["order"],
                       "t": t, "ells": qual[:FIXTURE_ELLS_PER_CURVE]})
    rows = [q for c in curves for q in c["ells"]]
    ok = (len(curves) == FIXTURE_CURVES and rows and all(q["pass"] for q in rows))
    return {"verdict": "PASS" if ok else "FAIL",
            "curves": curves,
            "substitutions_declared": skipped,
            "selection_rule": "first curves of the frozen stream at p_12 having "
                              f"{FIXTURE_ELLS_PER_CURVE} qualifying ell in "
                              f"{list(FIXTURE_ELLS)}; shortfalls recorded and the "
                              "next curve used (contract m1_baseline_fixture_frozen)",
            "code_path": "harness.exp_kerfield.multiplicative_order (same as STAGE 3)"}


# ---------------------------------------------------------------------------
# stage 3: one decade, one seed
# ---------------------------------------------------------------------------
@dataclass
class DecadeResult:
    p: int
    k: int
    seed: int
    instances: list = field(default_factory=list)
    exclusions: list = field(default_factory=list)
    attempts: int = 0


def measure_decade(p: int, k: int, seed: int,
                   target: int = CURVES_PER_DECADE_TARGET) -> DecadeResult:
    res = DecadeResult(p=p, k=k, seed=seed)
    i = 0
    while len(res.instances) < target and i < ATTEMPT_CAP_PER_DECADE:
        idx = i
        i += 1
        res.attempts = i
        a = curve_param(seed, p, "a", idx)
        b = curve_param(seed, p, "b", idx)
        try:
            E = EllipticCurve(p, a, b)
        except ValueError:
            res.exclusions.append({"index": idx, "reason": "singular (4a^3+27b^2=0)"})
            continue
        cert = order_certificate(E, p, seed, f"{p}:{idx}")
        if cert["order"] is None:
            res.exclusions.append({"index": idx, "reason":
                                   f"order certificate failed: {cert['reason']}",
                                   "certificate": cert})
            continue
        N = cert["order"]
        t = p + 1 - N
        if t == 0:
            res.exclusions.append({"index": idx, "reason": "supersingular (t = 0)"})
            continue
        window = degree_window(t, p)
        cond = conductor(t, p)
        chosen = None
        window_rows = []
        for rank, w in enumerate(window):
            adm = admissibility(w["u"], w["v"], w["d"])
            dfac, dver = factor_exact(w["d"])
            row = {"rank": rank, **w, **adm, "d_factorisation_verified": dver,
                   "d_factorisation": {str(q): e for q, e in sorted(dfac.items())}}
            if adm["admissible"] and dver:
                lam = eigenvalue(w["u"], w["v"], w["d"])
                om = multiplicative_order(lam, w["d"])
                row["lambda"] = lam
                row["m"] = om["m"]
                row["order_verification_ok"] = om["ok"]
                row["pow_check"] = om["pow_check"]
                row["minimality_check"] = om["minimality_check"]
                if om["ok"] and w["d"] > 1:
                    row["log_m_over_log_d"] = (math.log(om["m"]) / math.log(w["d"])
                                               if om["m"] and om["m"] > 1 else 0.0)
                if chosen is None and om["ok"]:
                    chosen = row
            window_rows.append(row)
        minimiser_admissible = bool(window_rows and window_rows[0].get("admissible")
                                    and window_rows[0].get("d_factorisation_verified"))
        if chosen is None:
            res.exclusions.append({"index": idx, "reason":
                                   "no admissible/verifiable alpha in the k=5 window",
                                   "window": window_rows})
            continue
        d = chosen["d"]
        a_null, redraws = null_unit_draw(seed, p, idx, d)
        null_ord = multiplicative_order(a_null, d)
        inst = {
            "index": idx, "p": p, "k": k, "seed": seed, "a": a, "b": b,
            "order_E": N, "t": t, "D": cond["D"], "f": cond["f"],
            "fundamental_discriminant": cond["fundamental_discriminant"],
            "conductor_bin": conductor_bin(cond["f"]),
            "order_certificate": {kk: cert[kk] for kk in
                                  ("unique", "candidates_in_hasse", "point_orders",
                                   "points_used", "hasse_interval",
                                   "annihilates_all_sampled_points")},
            "degree_window": window_rows,
            "minimiser_admissible": minimiser_admissible,
            "primary_rank": chosen["rank"],
            "u": chosen["u"], "v": chosen["v"], "d": d,
            "d_over_p": d / p,
            "primitive": chosen["primitive"], "gcd_v_d": chosen["gcd_v_d"],
            "d_factorisation": chosen["d_factorisation"],
            "d_factorisation_verified": chosen["d_factorisation_verified"],
            "lambda": chosen["lambda"], "m": chosen["m"],
            "order_pow_check": chosen["pow_check"],
            "order_minimality_check": chosen["minimality_check"],
            "log_m_over_log_d": (math.log(chosen["m"]) / math.log(d)
                                 if chosen["m"] and chosen["m"] > 1 else 0.0),
            "null_a": a_null, "null_redraws": redraws, "null_m": null_ord["m"],
            "null_order_ok": null_ord["ok"],
            "null_log_m_over_log_d": (math.log(null_ord["m"]) / math.log(d)
                                      if null_ord["m"] and null_ord["m"] > 1 else 0.0),
            "window_spread_log_m_over_log_d": _spread(window_rows),
        }
        res.instances.append(inst)
    return res


def _spread(window_rows: list) -> float | None:
    vals = [r["log_m_over_log_d"] for r in window_rows if "log_m_over_log_d" in r]
    return (max(vals) - min(vals)) if len(vals) >= 2 else None


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------
def ks_two_sample(x: list[float], y: list[float]) -> dict:
    n, m = len(x), len(y)
    if n == 0 or m == 0:
        return {"D": None, "n": n, "m": m, "critical_value": None,
                "below_critical": None, "signed_direction": None}
    xs, ys = sorted(x), sorted(y)
    allv = sorted(set(xs) | set(ys))
    D = 0.0
    signed_max, signed_min = 0.0, 0.0
    i = j = 0
    for v in allv:
        while i < n and xs[i] <= v:
            i += 1
        while j < m and ys[j] <= v:
            j += 1
        diff = i / n - j / m
        D = max(D, abs(diff))
        signed_max = max(signed_max, diff)
        signed_min = min(signed_min, diff)
    crit = KS_CRITICAL_COEFF * math.sqrt((n + m) / (n * m))
    return {"D": D, "n": n, "m": m, "critical_value": crit,
            "below_critical": D < crit,
            "signed_sup_curve_below_null": signed_max,
            "signed_sup_curve_above_null": -signed_min,
            "direction": ("curve-derived DEFICIT of log m / log d vs null"
                          if signed_max >= -signed_min else
                          "curve-derived EXCESS of log m / log d vs null"),
            "resolvable_floor": D_MIN_RESOLVABLE,
            "resolvable": D >= D_MIN_RESOLVABLE}


def quantiles(v: list[float]) -> dict:
    if not v:
        return {"n": 0}
    s = sorted(v)

    def q(f):
        if len(s) == 1:
            return s[0]
        pos = f * (len(s) - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, len(s) - 1)
        return s[lo] + (pos - lo) * (s[hi] - s[lo])
    return {"n": len(s), "min": s[0], "q1": q(0.25), "median": q(0.5),
            "q3": q(0.75), "max": s[-1], "mean": sum(s) / len(s)}


def ecdf(v: list[float], points: int = 21) -> list[list[float]]:
    if not v:
        return []
    s = sorted(v)
    out = []
    for i in range(points):
        x = s[0] + (s[-1] - s[0]) * i / (points - 1) if len(s) > 1 else s[0]
        c = sum(1 for z in s if z <= x) / len(s)
        out.append([x, c])
    return out


# ---------------------------------------------------------------------------
# analytic peak memory (M7; computed BEFORE the run, from data structures)
# ---------------------------------------------------------------------------
def analytic_peak_bytes(stage: str, n_instances: int = CURVES_PER_DECADE_TARGET,
                        seeds: int = len(SEEDS), p: int = 2 ** 24) -> dict:
    """MODELED peak memory, sized from the declared data structures.

    interpreter+sympy resident baseline .......... 48 MB   (declared constant)
    per-instance record ......................... ~2 KB    (window of 5 with
                                                  factorisations, JSON-ready)
    BSGS baby table ............................. w = sqrt(4 sqrt p) entries,
                                                  ~120 B per dict entry
    """
    base = 48 * 1024 * 1024
    per_instance = 2048
    w = math.isqrt(math.isqrt(4 * p) * 4) + 1
    baby = w * 120
    if stage == "stage3":
        tot = base + per_instance * n_instances * seeds + baby
    elif stage == "stage2":
        tot = base + per_instance * 64 + baby
    elif stage in ("stage0", "stage1"):
        tot = base + 16 * 1024 * 1024          # retrieved text / corpus scan buffers
    else:
        tot = base + per_instance * n_instances * seeds * 7
    return {"basis": "modeled", "analytic_peak_bytes": int(tot),
            "components": {"interpreter_and_sympy_baseline_bytes": base,
                           "per_instance_record_bytes": per_instance,
                           "instances": n_instances * seeds if stage == "stage3" else None,
                           "bsgs_baby_table_bytes": baby},
            "band": list(MEMORY_RECONCILIATION_BAND)}
