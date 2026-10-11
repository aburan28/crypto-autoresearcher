"""Dickman-de Bruijn rho, piecewise power series on unit intervals.

Method (spec V-RHO-3 "piecewise power series on unit intervals"):
  R_k(xi) = rho(k - xi), 0 <= xi <= 1, k = 1, 2, ..., KMAX.
  R_1 = 1.  From u rho'(u) = -rho(u-1):  (k - xi) R_k'(xi) = R_{k-1}(xi), hence
  with R_k = sum a_i xi^i and R_{k-1} = sum b_i xi^i:
      a_{i+1} = (b_i + i a_i) / (k (i+1)),   i >= 0,
      a_0     = b_0 - sum_{i>=1} a_i          (continuity R_k(1) = R_{k-1}(0)).
  Coefficients are computed in mpmath at 60 decimal digits and truncated when
  a_i < 1e-45 * a_1; all a_i (i >= 1) are >= 0, so float Horner evaluation has
  no cancellation.  rho(u) = 1 for 0 <= u <= 1; rho(u) = 0 for u < 0 is never used.
"""
import math

import mpmath

KMAX = 120
_COEF = None


def _build():
    global _COEF
    mpmath.mp.dps = 60
    coefs = {1: [mpmath.mpf(1)]}
    for k in range(2, KMAX + 1):
        b = coefs[k - 1]
        a = [mpmath.mpf(0)]
        i = 0
        while True:
            bi = b[i] if i < len(b) else mpmath.mpf(0)
            nxt = (bi + i * a[i]) / (k * (i + 1))
            a.append(nxt)
            i += 1
            if i > 5 and nxt < mpmath.mpf(10) ** -45 * a[1]:
                break
            if i > 4000:
                raise RuntimeError("rho series did not converge at k=%d" % k)
        a[0] = b[0] - mpmath.fsum(a[1:])
        coefs[k] = a
    _COEF = {k: [float(x) for x in v] for k, v in coefs.items()}
    _COEF["mp"] = coefs


def rho(u):
    if _COEF is None:
        _build()
    if u <= 1.0:
        return 1.0
    if u > KMAX:
        raise ValueError("rho: u=%r beyond KMAX" % u)
    k = int(math.ceil(u))
    xi = k - u
    c = _COEF[k]
    s = 0.0
    for a in reversed(c):
        s = s * xi + a
    return s


def rho_mp(u):
    """High-precision evaluation (mpmath) for validation."""
    if _COEF is None:
        _build()
    u = mpmath.mpf(u)
    if u <= 1:
        return mpmath.mpf(1)
    k = int(mpmath.ceil(u))
    xi = k - u
    return mpmath.polyval(list(reversed(_COEF["mp"][k])), xi)


def rho_inv(target, lo=1.0, hi=KMAX - 1e-9):
    """u with rho(u) = target (rho strictly decreasing on (1, KMAX))."""
    if target >= 1.0:
        return 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if rho(mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def validate():
    """V-RHO-1..3.  Returns dict with verdicts and inputs."""
    out = {"method": "piecewise power series on unit intervals (mpmath 60 digits for coefficients, float Horner evaluation)",
           "KMAX": KMAX}
    # V-RHO-1
    pts = [1.0 + t / 200.0 for t in range(201)]
    err = max(abs(rho(u) - (1.0 - math.log(u))) for u in pts)
    out["V-RHO-1"] = {"points": len(pts), "max_abs_error": err, "threshold": 1e-10,
                      "verdict": "PASS" if err <= 1e-10 else "FAIL"}
    # V-RHO-2
    mpmath.mp.dps = 60
    pD = 5 * 2 ** 248 - 1
    u = float(mpmath.log(mpmath.mpf(pD) / 2) / (3 * mpmath.log(12589)))
    r = rho(u)
    ref = 1.0 / 69232
    rel = abs(r - ref) / ref
    out["V-RHO-2"] = {"u": u, "rho_u": r, "one_over_rho": 1.0 / r, "source_value": "1/69232",
                      "relative_difference": rel, "threshold": 0.02, "verdict": "PASS" if rel <= 0.02 else "FAIL"}
    # V-RHO-3: monotone (non-increasing, strictly decreasing on (1, 100]) and positive on grid step 1e-3
    step = 1e-3
    prev = rho(0.0)
    ok_pos, ok_mono, n = True, True, 0
    t = 0
    while True:
        uu = t * step
        if uu > 100.0:
            break
        v = rho(uu)
        n += 1
        if not v > 0:
            ok_pos = False
        if uu > 1.0 + 1e-12 and not v < prev:
            ok_mono = False
        if v > prev:
            ok_mono = False
        prev = v
        t += 1
    # float-vs-mp agreement spot check
    spots = [1.5, 2.5, 3.7, 5.0, 6.1, 10.3, 25.0, 60.0, 99.0]
    relerr = max(abs(rho(s) - float(rho_mp(s))) / float(rho_mp(s)) for s in spots)
    out["V-RHO-3"] = {"grid": "u in [0, 100] step 1e-3", "points": n, "positive": ok_pos, "monotone": ok_mono,
                      "float_vs_mp_max_rel_error": relerr,
                      "verdict": "PASS" if (ok_pos and ok_mono and relerr < 1e-12) else "FAIL"}
    out["reference_values"] = {str(x): rho(x) for x in [2, 3, 4, 5, 6, 7]}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(validate(), indent=1))
