"""
Polynomial arithmetic over F_p (coefficients as tuples, index = degree,
little-endian: poly[i] is the coefficient of x**i), plus the small "division
polynomial ring" R = F_p[x][y]/(y^2 - c(x)) represented as (A, B) pairs
meaning A(x) + B(x)*y.

All arithmetic here is pure F_p polynomial algebra: no extension fields are
ever constructed. This is deliberate (see run manifest note
"isogeny_kernel_method"): kernel polynomials are recovered via gcd against
x^p mod psi_ell(x), entirely inside F_p[x].

None of this module's arithmetic touches the Q1 (group-operation) or Q2
(per-member field-cost) counters: those are solve-time metrics with their
own dedicated instrumented engines (ec_group_ops.py, ec_jacobian.py). This
module carries the WALK cost (Q3's isogeny-evaluation component) instead: a
module-level field-multiplication tally, incremented once per F_p
multiplication actually performed inside pmul/pdivmod, so that the
Velu/Kohel construction cost entering Q3 is MEASURED by counting real
multiplications this code executes, not modelled by a formula (see
run_census.py, "walk_cost measured basis").
"""
from __future__ import annotations

Poly = tuple  # tuple[int, ...], little-endian, may have trailing zero coeffs

_field_mul_tally = [0]


def reset_field_mul_tally():
    _field_mul_tally[0] = 0


def get_field_mul_tally():
    return _field_mul_tally[0]


def _trim(c):
    c = list(c)
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return tuple(c)


def padd(a, b, p):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(len(a)):
        out[i] = a[i]
    for i in range(len(b)):
        out[i] = (out[i] + b[i]) % p
    return _trim(out)


def psub(a, b, p):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(len(a)):
        out[i] = a[i]
    for i in range(len(b)):
        out[i] = (out[i] - b[i]) % p
    return _trim(out)


def pscale(a, k, p):
    k %= p
    return _trim([(c * k) % p for c in a])


def pmul(a, b, p):
    if a == (0,) or b == (0,):
        return (0,)
    out = [0] * (len(a) + len(b) - 1)
    count = 0
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj == 0:
                continue
            out[i + j] = (out[i + j] + ai * bj) % p
            count += 1
    _field_mul_tally[0] += count
    return _trim(out)


def pdeg(a):
    a = _trim(a)
    if a == (0,):
        return -1
    return len(a) - 1


def pdivmod(a, b, p):
    """Polynomial division a = q*b + r over F_p[x] (p prime, field)."""
    a = list(_trim(a))
    b = _trim(b)
    if b == (0,):
        raise ZeroDivisionError("poly division by zero")
    db = pdeg(b)
    inv_lead = pow(b[db], p - 2, p)
    da = pdeg(a) if a != [0] else -1
    q = [0] * max(1, da - db + 1) if da >= db else [0]
    while True:
        da = len(a) - 1
        while da >= 0 and a[da] == 0:
            da -= 1
        if da < db:
            break
        coef = (a[da] * inv_lead) % p
        _field_mul_tally[0] += 1
        shift = da - db
        if shift >= len(q):
            q.extend([0] * (shift - len(q) + 1))
        q[shift] = coef
        for i, bc in enumerate(b):
            a[shift + i] = (a[shift + i] - coef * bc) % p
            _field_mul_tally[0] += 1
    r = _trim(a) if a else (0,)
    return _trim(q), r


def pmod(a, m, p):
    _, r = pdivmod(a, m, p)
    return r


def pgcd(a, b, p):
    a = _trim(a)
    b = _trim(b)
    while b != (0,):
        _, r = pdivmod(a, b, p)
        a, b = b, r
    if a == (0,):
        return a
    inv_lead = pow(a[-1], p - 2, p)
    return _trim([(c * inv_lead) % p for c in a])


def pmulmod(a, b, m, p):
    return pmod(pmul(a, b, p), m, p)


def ppowmod(base, e, m, p):
    """base^e mod m, in F_p[x]/(m)."""
    result = (1,)
    b = pmod(base, m, p)
    while e > 0:
        if e & 1:
            result = pmulmod(result, b, m, p)
        b = pmulmod(b, b, m, p)
        e >>= 1
    return result


def peval(a, x, p):
    r = 0
    for c in reversed(a):
        r = (r * x + c) % p
    return r


# ---- (A, B) ring elements for A(x) + B(x)*y, y^2 = c(x) ----

def ring_mul(e1, e2, c, p):
    a1, b1 = e1
    a2, b2 = e2
    A = padd(pmul(a1, a2, p), pmul(pmul(b1, b2, p), c, p), p)
    B = padd(pmul(a1, b2, p), pmul(a2, b1, p), p)
    return (A, B)


def ring_add(e1, e2, p):
    return (padd(e1[0], e2[0], p), padd(e1[1], e2[1], p))


def ring_sub(e1, e2, p):
    return (psub(e1[0], e2[0], p), psub(e1[1], e2[1], p))


def ring_sqr(e, c, p):
    return ring_mul(e, e, c, p)


def ring_pow(e, n, c, p):
    result = ((1,), (0,))
    base = e
    while n > 0:
        if n & 1:
            result = ring_mul(result, base, c, p)
        base = ring_sqr(base, c, p)
        n >>= 1
    return result


# ---- Newton's identities: power sums from elementary symmetric (monic poly coeffs) ----

def power_sums_from_monic(coeffs_desc, k, p):
    """
    Given a monic polynomial of degree d with coefficients in descending
    order coeffs_desc = [1, c_{d-1}, ..., c_1, c_0] (i.e. x^d + c_{d-1}x^{d-1}
    + ... + c_0), return [s_1, ..., s_k], the power sums of its roots
    (with multiplicity), via Newton's identities. Requires k <= d in the
    generic case used here (k = 1, 2, 3; d = (ell-1)/2 >= 1 for ell in
    {3,5,7,11,13}).
    """
    d = len(coeffs_desc) - 1
    # e_i = (-1)^i * coeffs_desc[i], elementary symmetric functions, e_0 = 1
    e = [1] + [((-1) ** i) * coeffs_desc[i] % p for i in range(1, d + 1)]
    while len(e) <= k:
        e.append(0)
    s = [0] * (k + 1)  # s[0] unused
    for n in range(1, k + 1):
        total = 0
        for i in range(1, n):
            total += ((-1) ** (i - 1)) * e[i] * s[n - i]
        total += ((-1) ** (n - 1)) * n * e[n]
        s[n] = total % p
    return s[1:]
