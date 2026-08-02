#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-PEC-6be870 / RUN-PEC-6be870-a  --  NC-2 per-entry table-construction cost.

Measures the cost, in EXACTLY COUNTED F_{p^2} multiplications, of the
per-batch table-construction step of Algorithm 1 of
inputs/P13-WESOLOWSKI-2026/paper_fulltext.md (lines 137-152), i.e.

    cost(ell, j) = mults_instantiate(ell, j) + mults_rootfind(ell, j)

where mults_instantiate is the cost of forming Phi_ell(j, x) in F_{p^2}[x]
from the mod-p-reduced integer coefficient array of Phi_ell(X, Y) by Horner
evaluation in j for each x-degree, and mults_rootfind is the cost of
computing the complete set of distinct roots of Phi_ell(j, x) in F_{p^2}.

The frozen contract is experiments/EXP-PEC-6be870/specification.yaml.  This
program implements that contract and nothing else.  It records observations;
it draws no conclusions.

SageMath is NOT installed in this environment, so the frozen algorithmic
reference inputs/P13-PANNY-POC/p-one-third.py is NOT executed.  Its
count()/isogs() recursions are re-implemented here in pure Python (control
C-BASE.4) and its walk is re-implemented as the sampling procedure.

Environment: pure CPython, standard library only (no sage/sympy/gmpy2/
numpy/scipy).
"""

import argparse
import hashlib
import json
import math
import os
import random
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction

# Classical modular polynomials have coefficients well past CPython 3.11's
# default 4300-digit str<->int conversion limit at the top of the ell grid
# (the height of Phi_ell is about 6*ell*log(ell) nats).  Raise the limit so
# that parsing a primary-source file is never silently turned into an error.
sys.set_int_max_str_digits(1000000)

# ---------------------------------------------------------------------------
# 0. Global state and counters
# ---------------------------------------------------------------------------

P = None          # the prime; set by set_prime()
Q = None          # P*P, the size of F_{p^2}

# CNT  = per-region counters, reset at the start of every measured region.
# GTOT = process-global counters, never reset (used by C-INSTR.3 leakage test).
# index 0 = F_{p^2} multiplications (the primary reported unit)
# index 1 = F_{p^2} inversions (a SEPARATE register, per the contract, not
#           included in the primary unit)
CNT = [0, 0]
GTOT = [0, 0]

ZERO = (0, 0)


def set_prime(p):
    global P, Q
    P = p
    Q = p * p


def region_begin():
    """Start a measured region.  Contract C-INSTR.3: the region counter must
    read 0 at the start of every measured region."""
    if CNT[0] != 0 or CNT[1] != 0:
        raise AssertionError("C-INSTR.3 violation: region counter not zero at region start")
    return None


def region_end():
    """Close a measured region and return (mults, inversions)."""
    m, i = CNT[0], CNT[1]
    CNT[0] = 0
    CNT[1] = 0
    return m, i


def counters_reset_all():
    CNT[0] = 0
    CNT[1] = 0
    GTOT[0] = 0
    GTOT[1] = 0


# ---------------------------------------------------------------------------
# 1. F_{p^2} = F_p[T]/(T^2+1) arithmetic.  Elements are tuples (a, b) = a + b*T
# ---------------------------------------------------------------------------

def fp2_mul(x, y):
    """THE instrumented F_{p^2} multiplication primitive.  Exactly one call =
    exactly one counted multiplication.  A squaring counts as 1 (contract
    counting_conventions)."""
    CNT[0] += 1
    GTOT[0] += 1
    a, b = x
    c, d = y
    return ((a * c - b * d) % P, (a * d + b * c) % P)


def fp2_inv(x):
    """F_{p^2} inversion.

    Contract: "F_{p^2} inversions are counted in a SEPARATE register and are
    NOT included in the primary unit", and C-INSTR.4: an inversion increments
    the multiplication register "by exactly the number of multiplications it
    performs through the instrumented primitive".  Both clauses hold exactly
    and simultaneously only if the inversion performs ZERO calls to the
    instrumented primitive, so it is implemented that way: the two F_p
    multiplications of the norm and the F_p inversion are not routed through
    the F_{p^2} primitive.  Declared direction: attack-favourable (it lowers
    the primary count).  The declared sensitivity charging 3 multiplications
    per inversion is reported alongside."""
    CNT[1] += 1
    GTOT[1] += 1
    a, b = x
    n = (a * a + b * b) % P
    ni = pow(n, -1, P)
    return ((a * ni) % P, ((-b) * ni) % P)


def fp2_add(x, y):
    return ((x[0] + y[0]) % P, (x[1] + y[1]) % P)


def fp2_sub(x, y):
    return ((x[0] - y[0]) % P, (x[1] - y[1]) % P)


def fp2_neg(x):
    return ((-x[0]) % P, (-x[1]) % P)


# ---------------------------------------------------------------------------
# 2. Polynomials over F_{p^2}: list of coefficient tuples, index = degree,
#    trailing zeros trimmed.  The zero polynomial is [].
#
#    The hot loops inline the primitive of section 1 and increment the counter
#    by EXACTLY the number of inlined primitive applications.  C-INSTR.1/.2/.3
#    and the extra equivalence check verify that the inlined path counts and
#    computes identically to fp2_mul().
# ---------------------------------------------------------------------------

def _trim(c):
    i = len(c)
    while i > 0 and c[i - 1] == ZERO:
        i -= 1
    return c[:i] if i != len(c) else c


def poly_add(f, g):
    if len(f) < len(g):
        f, g = g, f
    out = list(f)
    for i in range(len(g)):
        out[i] = ((out[i][0] + g[i][0]) % P, (out[i][1] + g[i][1]) % P)
    return _trim(out)


def poly_sub(f, g):
    n = max(len(f), len(g))
    out = []
    for i in range(n):
        a = f[i] if i < len(f) else ZERO
        b = g[i] if i < len(g) else ZERO
        out.append(((a[0] - b[0]) % P, (a[1] - b[1]) % P))
    return _trim(out)


def poly_shift(f, k):
    return ([ZERO] * k + list(f)) if f else []


def poly_mul_school(f, g):
    """Schoolbook multiplication.  With all coefficients nonzero this performs
    EXACTLY (len(f))*(len(g)) primitive multiplications, which is (d+1)^2 for
    two degree-d operands (contract C-INSTR.1).  Zero coefficients are skipped
    (no primitive call); direction: attack-favourable."""
    lf = len(f)
    lg = len(g)
    if lf == 0 or lg == 0:
        return []
    n = lf + lg - 1
    ra = [0] * n
    rb = [0] * n
    c = 0
    for i in range(lf):
        a, b = f[i]
        if a == 0 and b == 0:
            continue
        for k in range(lg):
            cc, dd = g[k]
            if cc == 0 and dd == 0:
                continue
            c += 1
            ik = i + k
            ra[ik] += a * cc - b * dd
            rb[ik] += a * dd + b * cc
    CNT[0] += c
    GTOT[0] += c
    return _trim([(ra[t] % P, rb[t] % P) for t in range(n)])


KARATSUBA_THRESHOLD = 16   # operand length at or below which schoolbook is used


def poly_mul_kara(f, g):
    """Karatsuba multiplication (IMPL-B), same instrumented counter."""
    lf = len(f)
    lg = len(g)
    if lf == 0 or lg == 0:
        return []
    if lf <= KARATSUBA_THRESHOLD or lg <= KARATSUBA_THRESHOLD:
        return poly_mul_school(f, g)
    m = max(lf, lg) // 2
    f0, f1 = f[:m], f[m:]
    g0, g1 = g[:m], g[m:]
    z0 = poly_mul_kara(_trim(list(f0)), _trim(list(g0)))
    z2 = poly_mul_kara(_trim(list(f1)), _trim(list(g1)))
    z1 = poly_mul_kara(poly_add(_trim(list(f0)), _trim(list(f1))),
                       poly_add(_trim(list(g0)), _trim(list(g1))))
    z1 = poly_sub(poly_sub(z1, z0), z2)
    return _trim(poly_add(poly_add(z0, poly_shift(z1, m)), poly_shift(z2, 2 * m)))


def poly_rem_monic(a, f):
    """Remainder of a modulo the MONIC polynomial f, schoolbook reduction.
    Used unchanged by IMPL-A and IMPL-B: the contract's IMPL-B is "the same
    pipeline with KARATSUBA polynomial multiplication", i.e. it names exactly
    one substitution, the multiplication routine."""
    n = len(f) - 1
    if n < 0:
        raise ZeroDivisionError("modulus is the zero polynomial")
    if len(a) <= n:
        return _trim(list(a))
    la = len(a)
    ra = [t[0] for t in a]
    rb = [t[1] for t in a]
    fa = [f[k][0] for k in range(n)]
    fb = [f[k][1] for k in range(n)]
    c = 0
    for i in range(la - 1, n - 1, -1):
        ca = ra[i] % P
        cb = rb[i] % P
        if ca == 0 and cb == 0:
            continue
        base = i - n
        for k in range(n):
            x = fa[k]
            y = fb[k]
            if x == 0 and y == 0:
                continue
            c += 1
            bk = base + k
            ra[bk] -= ca * x - cb * y
            rb[bk] -= ca * y + cb * x
    CNT[0] += c
    GTOT[0] += c
    return _trim([(ra[t] % P, rb[t] % P) for t in range(n)])


def poly_div_monic(a, f):
    """Quotient of a by the MONIC polynomial f (schoolbook)."""
    n = len(f) - 1
    la = len(a)
    if la <= n:
        return []
    ra = [t[0] for t in a]
    rb = [t[1] for t in a]
    fa = [f[k][0] for k in range(n)]
    fb = [f[k][1] for k in range(n)]
    qa = [0] * (la - n)
    qb = [0] * (la - n)
    c = 0
    for i in range(la - 1, n - 1, -1):
        ca = ra[i] % P
        cb = rb[i] % P
        qa[i - n] = ca
        qb[i - n] = cb
        if ca == 0 and cb == 0:
            continue
        base = i - n
        for k in range(n):
            x = fa[k]
            y = fb[k]
            if x == 0 and y == 0:
                continue
            c += 1
            bk = base + k
            ra[bk] -= ca * x - cb * y
            rb[bk] -= ca * y + cb * x
    CNT[0] += c
    GTOT[0] += c
    return _trim([(qa[t], qb[t]) for t in range(la - n)])


def poly_monic(f):
    """Scale f to be monic.  Costs 1 inversion and len(f)-1 multiplications."""
    if not f:
        return []
    lead = f[-1]
    if lead == (1, 0):
        return list(f)
    inv = fp2_inv(lead)
    ia, ib = inv
    c = 0
    out = []
    for t in range(len(f) - 1):
        a, b = f[t]
        if a == 0 and b == 0:
            out.append(ZERO)
            continue
        c += 1
        out.append(((a * ia - b * ib) % P, (a * ib + b * ia) % P))
    CNT[0] += c
    GTOT[0] += c
    out.append((1, 0))
    return out


def poly_gcd(a, b):
    """Monic gcd via the Euclidean algorithm."""
    a = _trim(list(a))
    b = _trim(list(b))
    while b:
        bm = poly_monic(b)
        r = poly_rem_monic(a, bm)
        a, b = bm, r
    return a


def poly_powmod(base, e, mod, mulf):
    """Left-to-right binary square-and-multiply, x^e mod `mod`."""
    if e == 0:
        return _trim([(1, 0)])
    b = poly_rem_monic(base, mod)
    if not b:
        return []
    bits = bin(e)[2:]
    r = b
    for bit in bits[1:]:
        r = poly_rem_monic(mulf(r, r), mod)
        if bit == '1':
            r = poly_rem_monic(mulf(r, b), mod)
    return r


def poly_eval_uninstrumented(f, x):
    """Horner evaluation of f at x with NO counting and NO use of the
    instrumented primitive.  Independent check path for C-ALT.1."""
    acc = (0, 0)
    for i in range(len(f) - 1, -1, -1):
        a, b = acc
        c, d = x
        acc = ((a * c - b * d) % P, (a * d + b * c) % P)
        acc = ((acc[0] + f[i][0]) % P, (acc[1] + f[i][1]) % P)
    return acc


# ---------------------------------------------------------------------------
# 3. Root finding in F_{p^2}
#    IMPL-A: schoolbook multiplication; IMPL-B: Karatsuba multiplication.
#    Pipeline: gcd(x^{p^2} - x, f) by binary square-and-multiply, then
#    Cantor-Zassenhaus equal-degree splitting to degree 1.
# ---------------------------------------------------------------------------

def equal_degree_split(g, mulf, rng):
    """g monic, squarefree, all irreducible factors of degree 1."""
    out = []
    stack = [g]
    e = (Q - 1) // 2
    attempts = 0
    while stack:
        cur = stack.pop()
        if len(cur) - 1 <= 1:
            out.append(cur)
            continue
        while True:
            attempts += 1
            if attempts > 400:
                raise RuntimeError("Cantor-Zassenhaus failed to split after 400 attempts")
            c = (rng.randrange(P), rng.randrange(P))
            a = _trim([c, (1, 0)])
            b = poly_powmod(a, e, cur, mulf)
            d = poly_gcd(poly_sub(b, [(1, 0)]), cur)
            dd = len(d) - 1
            if 0 < dd < len(cur) - 1:
                break
        stack.append(d)
        stack.append(poly_div_monic(cur, d))
    return out, attempts


def distinct_roots(f, mulf, rng):
    """Complete set of DISTINCT roots of f in F_{p^2}.  Returns
    (sorted roots, degree of gcd(x^{p^2}-x, f), CZ attempts)."""
    f = _trim(list(f))
    if len(f) - 1 < 1:
        return [], 0, 0
    xpoly = [ZERO, (1, 0)]
    h = poly_powmod(xpoly, Q, f, mulf)
    g = poly_gcd(poly_sub(h, xpoly), f)
    deg_g = len(g) - 1
    if deg_g < 1:
        return [], max(deg_g, 0), 0
    factors, attempts = equal_degree_split(g, mulf, rng)
    roots = sorted(fp2_neg(fac[0]) for fac in factors)
    return roots, deg_g, attempts


# ---------------------------------------------------------------------------
# 4. Instantiation of Phi_ell(j, x) by Horner evaluation in j per x-degree
# ---------------------------------------------------------------------------

def instantiate(M, ell, j):
    """M[b][a] = (coefficient of X^a Y^b of Phi_ell) mod p, 0 <= a,b <= ell+1,
    symmetric.  Returns Phi_ell(j, x) in F_{p^2}[x].  Plain Horner in j for
    each x-degree with no zero-skipping, so the count is exactly
    (ell+1)*(ell+2) by construction."""
    ja, jb = j
    n = ell + 1
    out = []
    c = 0
    for b in range(n + 1):
        row = M[b]
        ra = row[n]
        rb = 0
        for a in range(n - 1, -1, -1):
            na = (ra * ja - rb * jb) % P
            nb = (ra * jb + rb * ja) % P
            ra = (na + row[a]) % P
            rb = nb
            c += 1
        out.append((ra, rb))
    CNT[0] += c
    GTOT[0] += c
    return _trim(out)


# ---------------------------------------------------------------------------
# 5. Modular polynomial acquisition, parsing and verification (C-BASE.2)
# ---------------------------------------------------------------------------

MODPOLY_URL = "https://math.mit.edu/~drew/modpolys/jfiles/phi_j_%d.txt"
CAP_PER_ELL_SECONDS = 120
CAP_PER_ELL_BYTES = 67108864
CAP_PHASE_SECONDS = 900
CAP_PHASE_BYTES = 2147483648


# Cumulative acquisition-phase accounting across every call to
# fetch_modpolys(); the contract's phase caps are cumulative, not per call.
ACQ = {"seconds": 0.0, "bytes": 0}


def fetch_modpolys(ells, outdir, log):
    """Acquisition phase.  Files are stored OUTSIDE the repository and are not
    committed; per ell we record URL, UTC timestamp, byte length and SHA-256."""
    os.makedirs(outdir, exist_ok=True)
    records = []
    t0 = time.time()
    for ell in ells:
        url = MODPOLY_URL % ell
        dest = os.path.join(outdir, "phi_j_%d.txt" % ell)
        ts = datetime.now(timezone.utc).isoformat()
        if ACQ["seconds"] + (time.time() - t0) > CAP_PHASE_SECONDS:
            records.append({"ell": ell, "status": "dropped_phase_time_cap",
                            "url": url, "fetch_utc": ts})
            continue
        if ACQ["bytes"] > CAP_PHASE_BYTES:
            records.append({"ell": ell, "status": "dropped_phase_byte_cap",
                            "url": url, "fetch_utc": ts})
            continue
        t1 = time.time()
        cmd = ["curl", "-sS", "--max-time", str(CAP_PER_ELL_SECONDS),
               "--max-filesize", str(CAP_PER_ELL_BYTES),
               "-w", "%{http_code}", "-o", dest, url]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=CAP_PER_ELL_SECONDS + 15)
            code, err, rc = proc.stdout.strip(), proc.stderr.strip(), proc.returncode
        except subprocess.TimeoutExpired:
            code, err, rc = "", "subprocess timeout", -1
        dt = time.time() - t1
        if rc == 0 and code == "200" and os.path.exists(dest):
            data = open(dest, "rb").read()
            ACQ["bytes"] += len(data)
            rec = {"ell": ell, "status": "ok", "url": url, "fetch_utc": ts,
                   "http_status": 200, "byte_length": len(data),
                   "sha256": hashlib.sha256(data).hexdigest(),
                   "fetch_seconds": round(dt, 3), "local_path": dest}
        else:
            rec = {"ell": ell, "status": "fetch_obstruction", "url": url,
                   "fetch_utc": ts, "http_status": code, "curl_returncode": rc,
                   "curl_stderr": err[:400], "fetch_seconds": round(dt, 3)}
            if os.path.exists(dest):
                os.remove(dest)
        records.append(rec)
        log("  fetched ell=%-4d %s bytes=%s" % (ell, rec["status"],
                                                rec.get("byte_length")))
    ACQ["seconds"] += time.time() - t0
    return records, ACQ["seconds"], ACQ["bytes"]


def parse_modpoly(path):
    """Sutherland jfile format: one line '[m,n] c' per nonzero coefficient with
    m >= n (symmetry implied).  Returns (terms, saw_m_lt_n, duplicates) where
    terms is a list of (m, n, c) exactly as listed in the file."""
    terms = []
    seen = set()
    saw_m_lt_n = 0
    duplicates = 0
    with open(path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            lb = line.index('[')
            rb = line.index(']')
            m_s, n_s = line[lb + 1:rb].split(',')
            m = int(m_s)
            n = int(n_s)
            c = int(line[rb + 1:].strip())
            if m < n:
                saw_m_lt_n += 1
            if (m, n) in seen:
                duplicates += 1
            seen.add((m, n))
            terms.append((m, n, c))
    return terms, saw_m_lt_n, duplicates


def verify_modpoly(ell, terms, saw_m_lt_n, duplicates):
    """C-BASE.2 verification battery on the INTEGER coefficients."""
    res = {"ell": ell, "n_terms_in_file": len(terms),
           "source_lists_m_lt_n": saw_m_lt_n, "duplicate_terms": duplicates}
    # (i) bidegree ell+1 in each variable
    max_m = max(t[0] for t in terms)
    max_n_sym = max(max(t[0], t[1]) for t in terms)
    res["max_degree_X"] = max_m
    res["max_degree_Y_after_symmetrisation"] = max_n_sym
    res["check_i_bidegree"] = bool(max_m == ell + 1 and max_n_sym == ell + 1)
    # (ii) symmetry.  The source lists only m >= n; the symmetric extension is
    # built from it, so symmetry holds BY CONSTRUCTION.  What is verifiable and
    # is verified: the source lists no term with m < n and no duplicate (m,n),
    # so the extension is well defined and unique.
    res["check_ii_symmetry_by_construction"] = bool(saw_m_lt_n == 0 and duplicates == 0)
    res["check_ii_note"] = ("symmetry holds by construction of the symmetric "
                            "extension of a source that lists only m >= n; "
                            "verified no m<n term and no duplicate (m,n)")
    # (iii) Kronecker congruence mod ell:
    #       Phi_ell(X,Y) = (X^ell - Y)(X - Y^ell)
    #                    = X^{ell+1} - X^ell Y^ell - X Y + Y^{ell+1}  (mod ell)
    expected = {(ell + 1, 0): 1, (0, ell + 1): 1,
                (ell, ell): -1 % ell, (1, 1): -1 % ell}
    bad = []
    got = {}
    for (m, n, c) in terms:
        cm = c % ell
        for (mm, nn) in {(m, n), (n, m)}:
            got[(mm, nn)] = cm
    for key, val in got.items():
        want = expected.get(key, 0) % ell
        if val % ell != want:
            bad.append([key[0], key[1], val % ell, want])
    for key, val in expected.items():
        if got.get(key, 0) % ell != val % ell:
            bad.append([key[0], key[1], got.get(key, 0) % ell, val % ell])
    res["check_iii_kronecker"] = (len(bad) == 0)
    res["check_iii_violations"] = bad[:20]
    res["check_iii_n_violations"] = len(bad)
    res["verdict"] = "pass" if (res["check_i_bidegree"] and
                                res["check_ii_symmetry_by_construction"] and
                                res["check_iii_kronecker"]) else "fail"
    return res


def reduce_modpoly(ell, terms, p):
    """Dense symmetric matrix M[b][a] = coeff(X^a Y^b) mod p."""
    n = ell + 2
    M = [[0] * n for _ in range(n)]
    for (m, nn, c) in terms:
        cm = c % p
        M[nn][m] = cm
        M[m][nn] = cm
    return M


def canonical_reduced_sha256(M, ell):
    """SHA-256 of the mod-p-reduced coefficient array serialised canonically as
    sorted (a, b, c) triples with c in [0, p)."""
    h = hashlib.sha256()
    n = ell + 2
    for a in range(n):
        for b in range(n):
            c = M[b][a]
            if c:
                h.update(("%d,%d,%d\n" % (a, b, c)).encode())
    return h.hexdigest()


def bivariate_eval_independent(terms, p, j0, j1, ell):
    """C-BASE.5: evaluate Phi_ell(j0, j1) in F_{p^2} directly from the INTEGER
    coefficient array, reducing mod p on its own path, with arithmetic that
    does NOT use the instantiated univariate polynomial or the instrumented
    primitive."""
    n = ell + 2

    def powers(z):
        out = [(1, 0)]
        for _ in range(1, n):
            a, b = out[-1]
            c, d = z
            out.append(((a * c - b * d) % p, (a * d + b * c) % p))
        return out

    p0 = powers(j0)
    p1 = powers(j1)
    acc0 = 0
    acc1 = 0
    for (m, nn, c) in terms:
        cm = c % p
        if cm == 0:
            continue
        a, b = p0[m]
        cc, dd = p1[nn]
        t0 = a * cc - b * dd
        t1 = a * dd + b * cc
        acc0 += cm * t0
        acc1 += cm * t1
        if m != nn:
            a, b = p0[nn]
            cc, dd = p1[m]
            acc0 += cm * (a * cc - b * dd)
            acc1 += cm * (a * dd + b * cc)
    return (acc0 % p, acc1 % p)


# ---------------------------------------------------------------------------
# 6. Prime selection, primality, and the seed-curve control C-BASE.1
# ---------------------------------------------------------------------------

FIRST_20_PRIME_BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                        31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


def miller_rabin(n, bases):
    if n < 2:
        return False
    for b in bases:
        if n % b == 0:
            return n == b
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in bases:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def largest_prime_below(bound, cong=None, mod=None):
    n = bound - 1
    if cong is not None:
        while n % mod != cong:
            n -= 1
        step = mod
    else:
        step = 1
    while n > 2:
        if miller_rabin(n, FIRST_20_PRIME_BASES):
            return n
        n -= step
    raise RuntimeError("no prime found")


def ec_add(pt1, pt2, p):
    """y^2 = x^3 + x over F_p, affine; None is the point at infinity."""
    if pt1 is None:
        return pt2
    if pt2 is None:
        return pt1
    x1, y1 = pt1
    x2, y2 = pt2
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2 and y1 == y2:
        lam = (3 * x1 * x1 + 1) * pow(2 * y1 % p, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_mul(k, pt, p):
    r = None
    a = pt
    while k:
        if k & 1:
            r = ec_add(r, a, p)
        a = ec_add(a, a, p)
        k >>= 1
    return r


def control_c_base_1(p, rng):
    res = {"id": "C-BASE.1"}
    res["p"] = p
    res["p_is_prime_miller_rabin_first_20_prime_bases"] = miller_rabin(p, FIRST_20_PRIME_BASES)
    res["miller_rabin_bases"] = FIRST_20_PRIME_BASES
    res["p_mod_4"] = p % 4
    res["p_congruent_3_mod_4"] = (p % 4 == 3)
    res["j_E0"] = 1728
    res["j_E0_is_1728"] = True
    pts = []
    ok = True
    tries = 0
    while len(pts) < 3 and tries < 1000:
        tries += 1
        x = rng.randrange(p)
        t = (x * x % p * x + x) % p
        if t == 0:
            continue
        if pow(t, (p - 1) // 2, p) != 1:
            continue
        y = pow(t, (p + 1) // 4, p)
        if y * y % p != t:
            continue
        R = ec_mul(p + 1, (x, y), p)
        pts.append({"x": x, "y": y, "order_p_plus_1_times_P_is_infinity": R is None})
        if R is not None:
            ok = False
    res["random_points"] = pts
    res["p_plus_1_annihilates_three_random_points"] = bool(ok and len(pts) == 3)
    res["verdict"] = "pass" if (res["p_is_prime_miller_rabin_first_20_prime_bases"]
                                and res["p_congruent_3_mod_4"]
                                and res["p_plus_1_annihilates_three_random_points"]) else "fail"
    return res


# ---------------------------------------------------------------------------
# 7. Sampling procedure: non-backtracking 2-isogeny walk from j = 1728
# ---------------------------------------------------------------------------

def walk_pool(M2, n_walk, seeds, log):
    """Cost of pool generation is EXCLUDED from the measurement (contract
    excluded_costs: sample preparation).  Counters are reset afterwards."""
    pool = []
    chains = []
    for sd in seeds:
        rng = random.Random(sd)
        czrng = random.Random("pool-cz|%d" % sd)
        j = (1728 % P, 0)
        chain = [j]
        prev = None
        for step in range(n_walk):
            f = instantiate(M2, 2, j)
            roots, _deg, _att = distinct_roots(f, poly_mul_school, czrng)
            cand = [r for r in roots if prev is None or r != prev]
            if not cand:
                cand = roots
            nxt = cand[rng.randrange(len(cand))]
            prev = j
            j = nxt
            chain.append(j)
        pool.append(j)
        chains.append(chain)
        log("  walk seed=%d -> j = %s (chain length %d)" % (sd, j, len(chain)))
    CNT[0] = 0
    CNT[1] = 0
    return pool, chains


# ---------------------------------------------------------------------------
# 8. Measurement kernels
# ---------------------------------------------------------------------------

MULFN = {"IMPL-A": poly_mul_school, "IMPL-B": poly_mul_kara}

_G = {}   # parent-process globals inherited by forked workers


def measure_primary(args):
    """One (ell, j, implementation) sample of the primary measurement."""
    ell, jidx, impl = args
    M = _G["mod"][ell]
    j = _G["pool"][jidx]
    mulf = MULFN[impl]
    # The Cantor-Zassenhaus randomness is seeded on (ell, jidx) ONLY, so that
    # IMPL-A and IMPL-B follow the identical random split structure and the
    # only difference between them is the multiplication routine.
    rng = random.Random("EXP-PEC-6be870|cz|%d|%d" % (ell, jidx))
    g0 = (GTOT[0], GTOT[1])
    t0 = time.time()
    region_begin()
    f = instantiate(M, ell, j)
    m_inst, i_inst = region_end()
    region_begin()
    roots, deg_g, attempts = distinct_roots(f, mulf, rng)
    m_root, i_root = region_end()
    t1 = time.time()
    g1 = (GTOT[0], GTOT[1])
    # C-INSTR.3 leakage / double-count check, per sample:
    isolation_ok = ((m_inst + m_root) == (g1[0] - g0[0]) and
                    (i_inst + i_root) == (g1[1] - g0[1]))
    # C-ALT.1: independent verification of every reported root.
    bad = 0
    for r in roots:
        if poly_eval_uninstrumented(f, r) != ZERO:
            bad += 1
    n_roots = len(roots)
    entries = n_roots - (1 if ell == 2 else 0)
    rec = {
        "ell": ell, "j_index": jidx, "impl": impl,
        "j": [j[0], j[1]],
        "mults_instantiate": m_inst, "mults_rootfind": m_root,
        "cost": m_inst + m_root,
        "inv_instantiate": i_inst, "inv_rootfind": i_root,
        "inversions": i_inst + i_root,
        "n_distinct_roots": n_roots,
        "deg_gcd_xq_minus_x": deg_g,
        "roots_equal_deg_gcd": bool(n_roots == deg_g),
        "cz_attempts": attempts,
        "entries": entries,
        "per_entry": (m_inst + m_root) / entries if entries else None,
        "per_entry_inv_charged_3": ((m_inst + m_root + 3 * (i_inst + i_root)) / entries
                                    if entries else None),
        "wall_clock_seconds": round(t1 - t0, 6),
        "counter_isolation_ok": isolation_ok,
        "roots_failing_independent_horner": bad,
        "pid": os.getpid(),
        "roots_sha256": hashlib.sha256(
            ("|".join("%d,%d" % r for r in roots)).encode()).hexdigest(),
        "roots": [[r[0], r[1]] for r in roots] if ell <= 3 else None,
    }
    return rec


def measure_null(args):
    """C-NULL: a null object of the same shape whose per-entry cost is O(1) BY
    CONSTRUCTION -- a table of ell+1 entries built by ell+1 successive
    non-backtracking 2-isogeny steps (fixed degree 2)."""
    ell, jidx, impl = args
    M2 = _G["mod"][2]
    j = _G["pool"][jidx]
    mulf = MULFN[impl]
    rng = random.Random("EXP-PEC-6be870|null|%d|%d" % (ell, jidx))
    czrng = random.Random("EXP-PEC-6be870|null-cz|%d|%d" % (ell, jidx))
    g0 = (GTOT[0], GTOT[1])
    t0 = time.time()
    total_m = 0
    total_i = 0
    prev = None
    roots_per_step = []
    for _ in range(ell + 1):
        region_begin()
        f = instantiate(M2, 2, j)
        m_inst, i_inst = region_end()
        region_begin()
        roots, _deg, _att = distinct_roots(f, mulf, czrng)
        m_root, i_root = region_end()
        total_m += m_inst + m_root
        total_i += i_inst + i_root
        cand = [r for r in roots if prev is None or r != prev]
        roots_per_step.append(len(roots))
        if not cand:
            cand = roots
        nxt = cand[rng.randrange(len(cand))]
        prev = j
        j = nxt
    t1 = time.time()
    g1 = (GTOT[0], GTOT[1])
    entries = ell + 1
    return {
        "ell": ell, "j_index": jidx, "impl": impl,
        "cost": total_m, "inversions": total_i,
        "entries": entries,
        "per_entry": total_m / entries,
        "entries_alt_denominator": sum(r - 1 for r in roots_per_step),
        "per_entry_alt_denominator": total_m / max(sum(r - 1 for r in roots_per_step), 1),
        "steps": ell + 1,
        "distinct_roots_per_step_min": min(roots_per_step),
        "distinct_roots_per_step_max": max(roots_per_step),
        "wall_clock_seconds": round(t1 - t0, 6),
        "counter_isolation_ok": (total_m == g1[0] - g0[0] and total_i == g1[1] - g0[1]),
        "pid": os.getpid(),
    }


# ---------------------------------------------------------------------------
# 9. Control C-INSTR
# ---------------------------------------------------------------------------

def control_c_instr(rng):
    out = {"id": "C-INSTR", "checks": []}
    ok_all = True

    # C-INSTR.1
    sub = {"id": "C-INSTR.1", "detail": []}
    ok = True
    for d in (0, 1, 2, 5, 10, 50):
        f = []
        g = []
        while len(f) < d + 1:
            e = (rng.randrange(1, P), rng.randrange(1, P))
            f.append(e)
        while len(g) < d + 1:
            e = (rng.randrange(1, P), rng.randrange(1, P))
            g.append(e)
        CNT[0] = 0
        CNT[1] = 0
        poly_mul_school(f, g)
        got = CNT[0]
        CNT[0] = 0
        CNT[1] = 0
        exp = (d + 1) ** 2
        sub["detail"].append({"d": d, "expected": exp, "counted": got,
                              "exact": bool(got == exp)})
        ok = ok and (got == exp)
    sub["verdict"] = "pass" if ok else "fail"
    ok_all = ok_all and ok
    out["checks"].append(sub)

    # C-INSTR.2
    CNT[0] = 0
    CNT[1] = 0
    x = (rng.randrange(P), rng.randrange(P))
    y = (rng.randrange(P), rng.randrange(P))
    for _ in range(1000):
        fp2_mul(x, y)
    got = CNT[0]
    CNT[0] = 0
    CNT[1] = 0
    sub = {"id": "C-INSTR.2", "expected": 1000, "counted": got,
           "verdict": "pass" if got == 1000 else "fail"}
    ok_all = ok_all and (got == 1000)
    out["checks"].append(sub)

    # C-INSTR.3
    g_before = (GTOT[0], GTOT[1])
    region_sums = [0, 0]
    zero_at_start = True
    for _ in range(20):
        if CNT[0] != 0 or CNT[1] != 0:
            zero_at_start = False
        region_begin()
        n = rng.randrange(3, 25)
        f = [(rng.randrange(P), rng.randrange(P)) for _ in range(n)]
        g = [(rng.randrange(P), rng.randrange(P)) for _ in range(n)]
        h = poly_mul_school(f, g)
        poly_mul_kara(h, f)
        poly_gcd(f, g)
        fp2_inv((rng.randrange(1, P), rng.randrange(1, P)))
        m, i = region_end()
        region_sums[0] += m
        region_sums[1] += i
    g_after = (GTOT[0], GTOT[1])
    ok3 = (region_sums[0] == g_after[0] - g_before[0] and
           region_sums[1] == g_after[1] - g_before[1] and zero_at_start)
    sub = {"id": "C-INSTR.3", "regions": 20,
           "sum_of_region_mults": region_sums[0],
           "global_mult_delta": g_after[0] - g_before[0],
           "sum_of_region_inversions": region_sums[1],
           "global_inversion_delta": g_after[1] - g_before[1],
           "counter_zero_at_every_region_start": zero_at_start,
           "verdict": "pass" if ok3 else "fail"}
    ok_all = ok_all and ok3
    out["checks"].append(sub)

    # C-INSTR.4
    ok4 = True
    detail = []
    for _ in range(100):
        z = (rng.randrange(P), rng.randrange(P))
        if z == ZERO:
            continue
        CNT[0] = 0
        CNT[1] = 0
        zi = fp2_inv(z)
        dm, di = CNT[0], CNT[1]
        CNT[0] = 0
        CNT[1] = 0
        prod = ((z[0] * zi[0] - z[1] * zi[1]) % P, (z[0] * zi[1] + z[1] * zi[0]) % P)
        good = (di == 1 and dm == 0 and prod == (1, 0))
        ok4 = ok4 and good
        detail.append(good)
    sub = {"id": "C-INSTR.4", "trials": len(detail),
           "inversion_register_delta_per_inversion": 1,
           "multiplication_register_delta_per_inversion": 0,
           "primitive_calls_inside_inversion": 0,
           "all_trials_exact_and_inverse_verified": bool(ok4),
           "verdict": "pass" if ok4 else "fail"}
    ok_all = ok_all and ok4
    out["checks"].append(sub)

    # Additional (not required by the contract, recorded as extra evidence):
    # the inlined hot-loop arithmetic agrees with the primitive fp2_mul.
    eq_ok = True
    for _ in range(50):
        n = rng.randrange(1, 20)
        m = rng.randrange(1, 20)
        f = [(rng.randrange(P), rng.randrange(P)) for _ in range(n)]
        g = [(rng.randrange(P), rng.randrange(P)) for _ in range(m)]
        ref = [ZERO] * (n + m - 1)
        for i in range(n):
            for k in range(m):
                ref[i + k] = fp2_add(ref[i + k], fp2_mul(f[i], g[k]))
        CNT[0] = 0
        CNT[1] = 0
        if _trim(ref) != poly_mul_school(f, g):
            eq_ok = False
        if _trim(ref) != poly_mul_kara(f, g):
            eq_ok = False
        CNT[0] = 0
        CNT[1] = 0
    out["extra_inlined_primitive_equivalence"] = {
        "trials": 50, "agrees_with_fp2_mul_reference": bool(eq_ok)}

    out["verdict"] = "pass" if ok_all else "fail"
    CNT[0] = 0
    CNT[1] = 0
    return out


# ---------------------------------------------------------------------------
# 10. Control C-BASE.4 / C-BASE.5: re-implementation of the frozen PoC
# ---------------------------------------------------------------------------

def sieve(n):
    bs = bytearray([1]) * (n + 1)
    bs[0] = bs[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if bs[i]:
            bs[i * i::i] = bytearray(len(bs[i * i::i]))
    return [i for i in range(n + 1) if bs[i]]


PRIMES = sieve(2000)


def prime_range(a, b):
    """Sage semantics: primes p with a <= p < b."""
    return [p for p in PRIMES if a <= p < b]


def poc_count(smooth, max_deg, degs=(1,)):
    """Verbatim re-implementation of the frozen PoC's count()."""
    ret = 1
    hi = min(math.floor(max_deg), smooth) + 1
    for l in prime_range(degs[-1], hi):
        num = l + (1 if l != degs[-1] else 0)
        ret += num * poc_count(smooth, Fraction(max_deg, l), degs + (l,))
    return ret


def poc_isogs(smooth, max_deg, chain, rootfn):
    """Verbatim re-implementation of the frozen PoC's isogs() BFS-order
    generator, run to EXHAUSTION (no early break)."""
    yield chain
    prev_deg = chain[-2] if len(chain) >= 2 else 1
    hi = min(math.floor(max_deg), smooth) + 1
    for l in prime_range(prev_deg, hi):
        for jj in rootfn(l, chain[-1]):
            if len(chain) >= 3 and jj == chain[-3]:
                continue
            yield from poc_isogs(smooth, Fraction(max_deg, l), chain + [l, jj], rootfn)


# ---------------------------------------------------------------------------
# 11. Statistics: OLS, t-quantile, bootstrap, jackknife, quadratic fit
# ---------------------------------------------------------------------------

def _t_pdf(t, nu):
    return math.exp(math.lgamma((nu + 1) / 2.0) - math.lgamma(nu / 2.0)
                    - 0.5 * math.log(nu * math.pi)
                    - (nu + 1) / 2.0 * math.log1p(t * t / nu))


def _t_cdf(t, nu, n=4000):
    if t < 0:
        return 1.0 - _t_cdf(-t, nu, n)
    h = t / n
    s = _t_pdf(0.0, nu) + _t_pdf(t, nu)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * _t_pdf(i * h, nu)
    return 0.5 + s * h / 3.0


def t_quantile_975(nu):
    """0.975 quantile of Student's t with nu degrees of freedom, computed here
    by Simpson integration of the density plus bisection (no external table)."""
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _t_cdf(mid, nu) < 0.975:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def ols(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    inter = my - slope * mx
    resid = [y - (inter + slope * x) for x, y in zip(xs, ys)]
    sse = sum(r * r for r in resid)
    sst = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 - sse / sst if sst > 0 else float('nan')
    se = math.sqrt(sse / (n - 2) / sxx) if n > 2 and sxx > 0 else float('nan')
    return {"n": n, "slope": slope, "intercept": inter, "residuals": resid,
            "max_abs_residual": max(abs(r) for r in resid), "sse": sse,
            "r2": r2, "slope_se": se}


def quad_fit(xs, ys):
    n = len(xs)
    S = [[0.0] * 4 for _ in range(3)]
    for i in range(3):
        for k in range(3):
            S[i][k] = sum(x ** (i + k) for x in xs)
        S[i][3] = sum(y * x ** i for x, y in zip(xs, ys))
    for col in range(3):
        piv = max(range(col, 3), key=lambda r: abs(S[r][col]))
        S[col], S[piv] = S[piv], S[col]
        pv = S[col][col]
        for k in range(col, 4):
            S[col][k] /= pv
        for r in range(3):
            if r != col and S[r][col] != 0:
                fac = S[r][col]
                for k in range(col, 4):
                    S[r][k] -= fac * S[col][k]
    a, b, c = S[0][3], S[1][3], S[2][3]
    return {"a": a, "b": b, "c": c, "n": n}


def median(v):
    s = sorted(v)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def percentile(v, q):
    s = sorted(v)
    if not s:
        return None
    k = (len(s) - 1) * q
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def iqr(v):
    return percentile(v, 0.75) - percentile(v, 0.25)


# ---------------------------------------------------------------------------
# 12. Driver
# ---------------------------------------------------------------------------

CORE_GRID = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
             61, 67, 71, 73, 79, 83, 89, 97, 101]
EXT_GRID = [103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
            173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239,
            241, 251]
WALK_SEEDS = [20260802001, 20260802002, 20260802003, 20260802004,
              20260802005, 20260802006, 20260802007, 20260802008]
BOOTSTRAP_SEED = 20260802
BOOTSTRAP_REPLICATES = 2000
N_WALK = 120
POOL_SIZE_CORE = 8

# Labelled INPUT CONSTANTS quoted as stored from
# experiments/EXP-P13VOW-001/runs/RUN-P13VOW-001/raw-result.json
# (per_field.<key>.optimal.log2B).  These are NOT measurements of this run.
VOW_CONSTANTS = [
    {"name": "SQIsign NIST-I", "log2p": 256, "log2_B_opt": 14.200000000000001},
    {"name": "SQIsign NIST-III", "log2p": 384, "log2_B_opt": 17.8},
    {"name": "SQIsign NIST-V", "log2p": 512, "log2_B_opt": 20.900000000000002},
    {"name": "log2p = 576", "log2p": 576, "log2_B_opt": 22.3},
    {"name": "log2p = 768", "log2p": 768, "log2_B_opt": 26.1},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-seconds", type=float, default=5400.0)
    ap.add_argument("--measurement-window-seconds", type=float, default=3600.0)
    ap.add_argument("--extension-reserve-seconds", type=float, default=1200.0)
    ap.add_argument("--skip-extension", action="store_true")
    args = ap.parse_args()

    T0 = time.time()
    R = {"run_id": "RUN-PEC-6be870-a", "experiment_id": "EXP-PEC-6be870",
         "started_utc": datetime.now(timezone.utc).isoformat(),
         "argv": sys.argv, "phases": {}}

    def log(msg):
        print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)

    def elapsed():
        return time.time() - T0

    log("EXP-PEC-6be870 / RUN-PEC-6be870-a  --  NC-2 per-entry cost measurement")
    log("python %s" % sys.version.replace("\n", " "))

    # ---- instance --------------------------------------------------------
    t = time.time()
    p = largest_prime_below(2 ** 40, cong=3, mod=4)
    p_prev = largest_prime_below(2 ** 40)
    set_prime(p)
    R["instance"] = {
        "p": p, "p_bits": p.bit_length(),
        "p_mod_4": p % 4,
        "largest_prime_below_2_40_no_congruence_condition": p_prev,
        "coincides_with_poc_previous_prime_2_40": bool(p == p_prev),
        "field": "F_{p^2} = F_p[T]/(T^2+1)",
        "field_bits": 80,
        "seed_curve": "E_0 : y^2 = x^3 + x over F_p, j(E_0) = 1728",
        "q": p * p,
    }
    log("p = %d (2^%d), p mod 4 = %d; previous_prime(2^40) = %d; coincide = %s"
        % (p, p.bit_length(), p % 4, p_prev, p == p_prev))
    R["phases"]["instance_seconds"] = round(time.time() - t, 3)

    # ---- step 1: C-INSTR -------------------------------------------------
    t = time.time()
    log("step 1: C-INSTR")
    rng = random.Random("EXP-PEC-6be870|c-instr|%d" % BOOTSTRAP_SEED)
    c_instr = control_c_instr(rng)
    R["controls"] = {"C-INSTR": c_instr}
    R["phases"]["c_instr_seconds"] = round(time.time() - t, 3)
    log("  C-INSTR verdict: %s" % c_instr["verdict"])
    if c_instr["verdict"] != "pass":
        R["validity"] = {"status": "invalid_measurement",
                         "reason": "C-INSTR failed; per the frozen contract the run STOPS "
                                   "and no per-entry number is reported."}
        json.dump(R, open(args.out, "w"), indent=1)
        log("STOP: C-INSTR failed.")
        return 2

    # ---- step 2: acquisition + C-BASE.2 ----------------------------------
    t = time.time()
    log("step 2: modular-polynomial acquisition and C-BASE.2")
    fetch_records, fetch_seconds, fetch_bytes = fetch_modpolys(
        CORE_GRID, os.path.join(args.scratch, "modpolys_run"), log)
    R["modular_polynomial_provenance"] = {
        "route": "primary source download",
        "index_page": "https://math.mit.edu/~drew/ClassicalModPolys.html",
        "file_url_pattern": MODPOLY_URL,
        "storage": "session scratch, outside the repository; not committed",
        "acquisition_phase_seconds": round(fetch_seconds, 3),
        "acquisition_phase_total_bytes": fetch_bytes,
        "caps": {"per_ell_fetch_seconds": CAP_PER_ELL_SECONDS,
                 "per_ell_bytes": CAP_PER_ELL_BYTES,
                 "acquisition_phase_seconds": CAP_PHASE_SECONDS,
                 "acquisition_phase_total_bytes": CAP_PHASE_BYTES},
        "per_ell": fetch_records,
    }
    dropped = {}
    terms_by_ell = {}
    mod_by_ell = {}
    cbase2 = []
    for rec in fetch_records:
        ell = rec["ell"]
        if rec["status"] != "ok":
            dropped[ell] = rec["status"]
            continue
        terms, saw, dup = parse_modpoly(rec["local_path"])
        v = verify_modpoly(ell, terms, saw, dup)
        cbase2.append(v)
        if v["verdict"] != "pass":
            dropped[ell] = "C-BASE.2 verification failure"
            continue
        terms_by_ell[ell] = terms
        M = reduce_modpoly(ell, terms, p)
        mod_by_ell[ell] = M
        rec["coefficient_count_in_file"] = len(terms)
        rec["reduced_array_sha256"] = canonical_reduced_sha256(M, ell)
    R["controls"]["C-BASE.2"] = {
        "id": "C-BASE.2", "per_ell": cbase2,
        "n_pass": sum(1 for v in cbase2 if v["verdict"] == "pass"),
        "n_fail": sum(1 for v in cbase2 if v["verdict"] != "pass"),
        "verdict": "pass" if all(v["verdict"] == "pass" for v in cbase2) and cbase2 else "fail",
    }
    R["dropped_ell"] = dropped
    log("  C-BASE.2: %d/%d pass, dropped=%s"
        % (R["controls"]["C-BASE.2"]["n_pass"], len(cbase2), dropped))
    R["phases"]["acquisition_and_cbase2_seconds"] = round(time.time() - t, 3)

    surviving = [e for e in CORE_GRID if e in mod_by_ell]
    if len(surviving) < 12 or len(surviving) < 0.75 * len(CORE_GRID):
        R["validity"] = {"status": "incomplete_infrastructure",
                         "reason": "fewer than 12 surviving ell or >25%% of the core "
                                   "grid dropped by fetch obstruction / verification failure"}
        json.dump(R, open(args.out, "w"), indent=1)
        return 3

    # ---- offline fixture: reduced arrays for ell <= 13 --------------------
    fixture = {}
    for ell in surviving:
        if ell <= 13:
            fixture[str(ell)] = {
                "note": "mod-p-reduced coefficient array as sorted (a,b,c) triples, c in [0,p)",
                "triples": [[a, b, mod_by_ell[ell][b][a]]
                            for a in range(ell + 2) for b in range(ell + 2)
                            if mod_by_ell[ell][b][a]],
            }
    R["reduced_coefficient_fixture_ell_le_13"] = fixture

    # ---- step 3: j-pool + C-BASE.1 ---------------------------------------
    t = time.time()
    log("step 3: j-pool generation (n_walk=%d) and C-BASE.1" % N_WALK)
    pool, chains = walk_pool(mod_by_ell[2], N_WALK, WALK_SEEDS, log)
    R["j_pool"] = {
        "n_walk": N_WALK, "walk_seeds": WALK_SEEDS,
        "pool": [[j[0], j[1]] for j in pool],
        "chains": [[[jj[0], jj[1]] for jj in ch] for ch in chains],
        "note": "cost of pool generation is EXCLUDED from the measurement",
    }
    degenerate = [i for i, j in enumerate(pool)
                  if j == (0, 0) or j == (1728 % p, 0)]
    R["j_pool"]["degenerate_excluded_indices"] = degenerate
    R["j_pool"]["degenerate_excluded_detail"] = [
        {"index": i, "j": [pool[i][0], pool[i][1]], "walk_seed": WALK_SEEDS[i]}
        for i in degenerate]
    active = [i for i in range(len(pool)) if i not in degenerate]
    rngb = random.Random("EXP-PEC-6be870|cbase1|%d" % BOOTSTRAP_SEED)
    cb1 = control_c_base_1(p, rngb)
    R["controls"]["C-BASE.1"] = cb1
    log("  C-BASE.1 verdict: %s" % cb1["verdict"])
    R["phases"]["pool_and_cbase1_seconds"] = round(time.time() - t, 3)
    if cb1["verdict"] != "pass":
        R["validity"] = {"status": "invalid_measurement", "reason": "C-BASE.1 failed"}
        json.dump(R, open(args.out, "w"), indent=1)
        return 4

    _G["mod"] = mod_by_ell
    _G["pool"] = pool

    import multiprocessing as mp
    ctx = mp.get_context("fork")

    def run_tasks(tasks, fn, label, deadline):
        out = []
        t_start = time.time()
        # Control work (C-BASE.4/.5 root finding, C-INSTR, pool generation) runs
        # in the parent OUTSIDE any measured region.  Its cost is EXCLUDED by the
        # contract, so the region counter is cleared before the workers are
        # forked; otherwise the forked children would inherit a nonzero region
        # counter and C-INSTR.3 would (correctly) refuse to open a region.
        CNT[0] = 0
        CNT[1] = 0
        with ctx.Pool(args.workers) as pool_:
            for rec in pool_.imap_unordered(fn, tasks, chunksize=1):
                out.append(rec)
                if len(out) % 25 == 0:
                    log("  %s %d/%d (%.1fs)" % (label, len(out), len(tasks),
                                                time.time() - t_start))
                if time.time() > deadline:
                    log("  %s: deadline reached, terminating remaining tasks" % label)
                    pool_.terminate()
                    break
        return out

    meas_deadline = T0 + args.measurement_window_seconds

    # ---- step 4: core grid, IMPL-A ---------------------------------------
    t = time.time()
    log("step 4: core-grid measurement, IMPL-A, ascending ell")
    tasks_a = [(ell, ji, "IMPL-A") for ell in surviving for ji in active]
    recs_a = run_tasks(tasks_a, measure_primary, "IMPL-A", meas_deadline)
    log("  IMPL-A: %d/%d samples in %.1fs" % (len(recs_a), len(tasks_a), time.time() - t))
    R["phases"]["impl_a_seconds"] = round(time.time() - t, 3)

    # ---- step 5: C-NULL --------------------------------------------------
    t = time.time()
    log("step 5: C-NULL over the same grid")
    tasks_n = [(ell, ji, impl) for ell in surviving for ji in active
               for impl in ("IMPL-A", "IMPL-B")]
    recs_n = run_tasks(tasks_n, measure_null, "C-NULL", T0 + args.budget_seconds)
    log("  C-NULL: %d/%d samples in %.1fs" % (len(recs_n), len(tasks_n), time.time() - t))
    R["phases"]["c_null_seconds"] = round(time.time() - t, 3)

    # ---- step 6: C-BASE.3, C-BASE.4, C-BASE.5, C-ALT.1 -------------------
    # Executed here, before IMPL-B and before the optional extension, because
    # the frozen contract's execution_order places them at step 6.  They are
    # evaluated over the samples that exist at this point (IMPL-A, core grid);
    # a final pass over every sample of the completed run is recorded after
    # step 8 in the field `final_pass_over_all_samples`.
    t = time.time()
    log("step 6: C-BASE.3 / C-BASE.4 / C-BASE.5 / C-ALT.1")

    def cbase3_over(recs):
        dev = []
        tot = 0
        good = 0
        for r in recs:
            tot += 1
            if r["n_distinct_roots"] == r["ell"] + 1:
                good += 1
            else:
                dev.append({"ell": r["ell"], "j_index": r["j_index"],
                            "impl": r["impl"], "j": r["j"],
                            "n_distinct_roots": r["n_distinct_roots"],
                            "expected": r["ell"] + 1})
        frac = good / tot if tot else 0.0
        return {"samples": tot, "with_exactly_ell_plus_1_roots": good,
                "fraction": frac, "deviating_samples": dev,
                "verdict": "pass" if frac >= 0.90 else "fail"}

    def calt1_over(recs):
        badroots = sum(r["roots_failing_independent_horner"] for r in recs)
        mismatched = [{"ell": r["ell"], "j_index": r["j_index"], "impl": r["impl"],
                       "n_roots": r["n_distinct_roots"],
                       "deg_gcd": r["deg_gcd_xq_minus_x"]}
                      for r in recs if not r["roots_equal_deg_gcd"]]
        return {"roots_checked": sum(r["n_distinct_roots"] for r in recs),
                "roots_failing_independent_horner": badroots,
                "samples_where_n_roots_differs_from_deg_gcd": mismatched,
                "verdict": "pass" if (badroots == 0 and not mismatched) else "fail"}

    cb3 = cbase3_over(recs_a)
    cb3["id"] = "C-BASE.3"
    cb3["scope"] = "IMPL-A core-grid samples (step-6 position of the frozen order)"
    R["controls"]["C-BASE.3"] = cb3
    log("  C-BASE.3: %d/%d (%.4f) -> %s" % (cb3["with_exactly_ell_plus_1_roots"],
                                            cb3["samples"], cb3["fraction"],
                                            cb3["verdict"]))
    ca1 = calt1_over(recs_a)
    ca1["id"] = "C-ALT.1"
    ca1["scope"] = "IMPL-A core-grid samples (step-6 position of the frozen order)"
    ca1["independent_check"] = ("every reported root re-evaluated by an "
                                "uninstrumented Horner path that does not use the "
                                "root finder; root count compared with "
                                "deg(gcd(x^{p^2}-x, f))")
    R["controls"]["C-ALT.1"] = ca1
    log("  C-ALT.1: %s" % ca1["verdict"])

    # C-BASE.4 frozen-PoC agreement
    rootcache = {}

    def rootfn(l, jj):
        key = (l, jj)
        if key in rootcache:
            return rootcache[key]
        Mx = mod_by_ell.get(l)
        if Mx is None:
            raise RuntimeError("Phi_%d not available for C-BASE.4" % l)
        f = instantiate(Mx, l, jj)
        rr, _d, _a = distinct_roots(
            f, poly_mul_school,
            random.Random("EXP-PEC-6be870|poc|%d|%d|%d" % (l, jj[0], jj[1])))
        rootcache[key] = rr
        return rr

    cbase4 = []
    edges = set()
    pairs = [(2, 16), (2, 64), (3, 27), (3, 81)]
    for ji in active:
        running = 0
        start = pool[ji]
        for (B, X) in pairs + [(5, 125)]:
            if (B, X) == (5, 125) and running >= 20000:
                cbase4.append({"j_index": ji, "B": B, "X": X, "executed": False,
                               "reason": "running total of enumerated chains >= 20000"})
                continue
            exp = poc_count(B, Fraction(X))
            n = 0
            for ch in poc_isogs(B, Fraction(X), [start], rootfn):
                n += 1
                if len(ch) >= 3:
                    edges.add((ch[-2], ch[-3], ch[-1]))
            running += n
            cbase4.append({"j_index": ji, "B": B, "X": X, "executed": True,
                           "count_B_X": exp, "chains_enumerated": n,
                           "exact": bool(n == exp), "chains_le_count": bool(n <= exp)})
            log("  C-BASE.4 j=%d (B,X)=(%d,%d): chains=%d count=%d" % (ji, B, X, n, exp))
    ex = [c for c in cbase4 if c.get("executed")]
    if ex and all(c["exact"] for c in ex):
        v4 = "pass"
    elif ex and all(c["chains_le_count"] for c in ex):
        v4 = "pass_with_observation"
    else:
        v4 = "fail"
    R["controls"]["C-BASE.4"] = {
        "id": "C-BASE.4",
        "note": ("SageMath is not installed, so the frozen PoC is not executed; "
                 "count() and isogs() are re-implemented verbatim in pure Python. "
                 "The contract does not name a starting j-invariant for the "
                 "enumeration, so it is run from EVERY pool member rather than "
                 "from a privileged one; count(B,X) is j-independent. The 20000 "
                 "chain cap on (5,125) is applied to each starting point's own "
                 "running total."),
        "per_start": cbase4, "verdict": v4}
    log("  C-BASE.4 verdict: %s" % v4)

    # C-BASE.5 chain relations, independent bivariate evaluator
    cb5_bad = []
    checked = 0
    for (l, j0, j1) in sorted(edges):
        val = bivariate_eval_independent(terms_by_ell[l], p, j0, j1, l)
        checked += 1
        if val != ZERO:
            cb5_bad.append({"ell": l, "j0": list(j0), "j1": list(j1), "value": list(val)})
    n_from_chains = checked
    rng5 = random.Random("EXP-PEC-6be870|cbase5|%d" % BOOTSTRAP_SEED)
    triples = []
    for ch in chains:
        for i in range(len(ch) - 1):
            triples.append((2, ch[i], ch[i + 1]))
    for ell in surviving:
        for ji in active[:2]:
            f = instantiate(mod_by_ell[ell], ell, pool[ji])
            rr, _d, _a = distinct_roots(
                f, poly_mul_school,
                random.Random("EXP-PEC-6be870|cb5r|%d|%d" % (ell, ji)))
            for z in rr:
                triples.append((ell, pool[ji], z))
    rng5.shuffle(triples)
    sample100 = triples[:100]
    for (l, j0, j1) in sample100:
        val = bivariate_eval_independent(terms_by_ell[l], p, j0, j1, l)
        checked += 1
        if val != ZERO:
            cb5_bad.append({"ell": l, "j0": list(j0), "j1": list(j1), "value": list(val)})
    R["controls"]["C-BASE.5"] = {
        "id": "C-BASE.5",
        "unique_chain_edges_from_C_BASE_4_verified": n_from_chains,
        "random_triples_from_walk_pool_and_root_sets_verified": len(sample100),
        "ell_present_in_random_sample": sorted({l for (l, _a, _b) in sample100}),
        "total_relations_verified": checked,
        "nonvanishing_relations": cb5_bad,
        "evaluator": ("independent bivariate evaluation from the INTEGER "
                      "coefficient array with its own mod-p reduction path; "
                      "does not use the instantiated univariate polynomial "
                      "that the root finder consumed"),
        "verdict": "pass" if not cb5_bad else "fail"}
    log("  C-BASE.5: %d relations verified -> %s"
        % (checked, R["controls"]["C-BASE.5"]["verdict"]))

    R["controls"]["C-BASE.6"] = {
        "id": "C-BASE.6",
        "statement": ("Section 4.1 of the frozen paper assumes that constructing "
                      "a table costs a single F_{p^2}-operation per entry, i.e. "
                      "per_entry = 1 in the unit reported here; under the fit "
                      "log2 per_entry(ell) = gamma*log2(ell) + const that is the "
                      "constant function, i.e. gamma_paper = 0."),
        "gamma_paper": 0.0, "verdict": "pass"}
    R["phases"]["controls_seconds"] = round(time.time() - t, 3)

    # ---- step 7: IMPL-B --------------------------------------------------
    t = time.time()
    log("step 7: core-grid measurement, IMPL-B (C-ALT.2), ascending ell")
    tasks_b = [(ell, ji, "IMPL-B") for ell in surviving for ji in active]
    recs_b = run_tasks(tasks_b, measure_primary, "IMPL-B", meas_deadline)
    log("  IMPL-B: %d/%d samples in %.1fs" % (len(recs_b), len(tasks_b), time.time() - t))
    R["phases"]["impl_b_seconds"] = round(time.time() - t, 3)

    # C-ALT.2 identical root sets
    ha = {(r["ell"], r["j_index"]): r["roots_sha256"] for r in recs_a}
    hb = {(r["ell"], r["j_index"]): r["roots_sha256"] for r in recs_b}
    shared = sorted(set(ha) & set(hb))
    diff = [{"ell": k[0], "j_index": k[1]} for k in shared if ha[k] != hb[k]]
    R["controls"]["C-ALT.2"] = {
        "id": "C-ALT.2", "compared_samples": len(shared),
        "root_set_mismatches": diff,
        "complete": bool(len(recs_b) == len(tasks_b)),
        "impl_a": "schoolbook polynomial multiplication",
        "impl_b": "Karatsuba polynomial multiplication",
        "reduction_note": ("the contract's IMPL-B is 'the same pipeline with "
                           "KARATSUBA polynomial multiplication', i.e. it names "
                           "exactly one substitution, so the schoolbook "
                           "remainder/division steps are shared by both"),
        "verdict": ("pass" if (not diff and len(recs_b) == len(tasks_b))
                    else ("incomplete" if not diff else "fail"))}
    log("  C-ALT.2: %s (%d compared)" % (R["controls"]["C-ALT.2"]["verdict"], len(shared)))

    # ---- step 8: optional extension --------------------------------------
    ext_done = []
    ext_recs = []
    ext_fetch = []
    remaining = args.budget_seconds - elapsed()
    log("step 8: optional extension.  remaining budget = %.1fs" % remaining)
    if (not args.skip_extension) and remaining >= args.extension_reserve_seconds \
            and len(recs_a) == len(tasks_a) and len(recs_b) == len(tasks_b):
        for ell in EXT_GRID:
            if args.budget_seconds - elapsed() < args.extension_reserve_seconds:
                log("  extension stopped before ell=%d (less than %.0fs remain)"
                    % (ell, args.extension_reserve_seconds))
                break
            recs, fs, fb = fetch_modpolys([ell], os.path.join(args.scratch, "modpolys_run"), log)
            ext_fetch.extend(recs)
            if recs[0]["status"] != "ok":
                dropped[ell] = recs[0]["status"]
                continue
            terms, saw, dup = parse_modpoly(recs[0]["local_path"])
            v = verify_modpoly(ell, terms, saw, dup)
            cbase2.append(v)
            if v["verdict"] != "pass":
                dropped[ell] = "C-BASE.2 verification failure"
                continue
            Mext = reduce_modpoly(ell, terms, p)
            recs[0]["coefficient_count_in_file"] = len(terms)
            recs[0]["reduced_array_sha256"] = canonical_reduced_sha256(Mext, ell)
            mod_by_ell[ell] = Mext
            del terms          # C-BASE.5 already ran; free the big integer array
            _G["mod"] = mod_by_ell
            ext_active = active[:4]
            tasks_e = [(ell, ji, "IMPL-A") for ji in ext_active]
            got = run_tasks(tasks_e, measure_primary, "EXT ell=%d" % ell,
                            T0 + args.budget_seconds - args.extension_reserve_seconds)
            if len(got) == len(tasks_e):
                ext_recs.extend(got)
                ext_done.append(ell)
                log("  extension ell=%d done (%d samples)" % (ell, len(got)))
            else:
                log("  extension ell=%d incomplete (%d/%d), discarded from the fit"
                    % (ell, len(got), len(tasks_e)))
                break
    else:
        log("  extension NOT attempted (insufficient remaining budget or "
            "incomplete core grid)")
    R["extension"] = {"attempted": bool(ext_done or ext_fetch),
                      "ell_completed": ext_done,
                      "samples_per_ell": 4,
                      "fetch_records": ext_fetch}
    R["modular_polynomial_provenance"]["per_ell"].extend(ext_fetch)

    # ---- assemble sample tables -----------------------------------------
    R["samples_primary"] = sorted(recs_a + recs_b + ext_recs,
                                  key=lambda r: (r["impl"], r["ell"], r["j_index"]))
    R["samples_null"] = sorted(recs_n, key=lambda r: (r["impl"], r["ell"], r["j_index"]))

    # worker-level accounting (contract: parallelism clause)
    per_pid = {}
    for r in R["samples_primary"] + R["samples_null"]:
        per_pid.setdefault(str(r["pid"]), {"mults": 0, "samples": 0})
        per_pid[str(r["pid"])]["mults"] += r["cost"]
        per_pid[str(r["pid"])]["samples"] += 1
    R["worker_accounting"] = {
        "per_pid": per_pid,
        "sum_of_worker_mults": sum(v["mults"] for v in per_pid.values()),
        "sum_of_sample_costs": sum(r["cost"] for r in
                                   R["samples_primary"] + R["samples_null"]),
    }
    R["worker_accounting"]["agrees"] = bool(
        R["worker_accounting"]["sum_of_worker_mults"] ==
        R["worker_accounting"]["sum_of_sample_costs"])

    # ---- final pass of C-BASE.3 / C-ALT.1 over EVERY sample of the run ---
    iso_bad = [r for r in R["samples_primary"] + R["samples_null"]
               if not r["counter_isolation_ok"]]
    R["controls"]["C-INSTR"]["per_sample_isolation_failures"] = len(iso_bad)
    fp3 = cbase3_over(R["samples_primary"])
    fp3["scope"] = "every primary sample of the run (IMPL-A, IMPL-B, extension)"
    R["controls"]["C-BASE.3"]["final_pass_over_all_samples"] = fp3
    fp1 = calt1_over(R["samples_primary"])
    fp1["scope"] = "every primary sample of the run (IMPL-A, IMPL-B, extension)"
    R["controls"]["C-ALT.1"]["final_pass_over_all_samples"] = fp1
    if fp3["verdict"] != "pass":
        R["controls"]["C-BASE.3"]["verdict"] = fp3["verdict"]
    if fp1["verdict"] != "pass":
        R["controls"]["C-ALT.1"]["verdict"] = fp1["verdict"]
    log("  final pass: C-BASE.3 %s, C-ALT.1 %s" % (fp3["verdict"], fp1["verdict"]))

    # ---- step 9: aggregation, fits, extrapolation ------------------------
    t = time.time()
    log("step 9: aggregation, fits, extrapolation")

    def per_ell_table(recs, impl):
        d = {}
        for r in recs:
            if r["impl"] != impl or r["per_entry"] is None:
                continue
            d.setdefault(r["ell"], []).append((r["j_index"], r["per_entry"]))
        return d

    all_primary = R["samples_primary"]
    tabA = per_ell_table(all_primary, "IMPL-A")
    tabB = per_ell_table(all_primary, "IMPL-B")

    def agg(tab):
        out = {}
        for ell, vs in tab.items():
            vals = [v for _, v in vs]
            out[ell] = {"n": len(vals), "median": median(vals),
                        "mean": sum(vals) / len(vals), "min": min(vals),
                        "max": max(vals), "iqr": iqr(vals) if len(vals) > 1 else 0.0}
        return out

    aggA = agg(tabA)
    aggB = agg(tabB)
    ells_with_data = sorted(aggA)
    primary_per_ell = {}
    for ell in ells_with_data:
        if ell in aggB:
            primary_per_ell[ell] = min(aggA[ell]["median"], aggB[ell]["median"])
        else:
            primary_per_ell[ell] = aggA[ell]["median"]

    R["per_ell"] = {
        "IMPL-A": {str(k): v for k, v in aggA.items()},
        "IMPL-B": {str(k): v for k, v in aggB.items()},
        "primary_min_over_implementations": {str(k): v for k, v in primary_per_ell.items()},
        "cost_ratio_A_over_B": {
            str(ell): (aggA[ell]["median"] / aggB[ell]["median"]) for ell in ells_with_data
            if ell in aggB},
    }

    def windows(ells):
        w = {"W-ALL": list(ells),
             "W-MID": [e for e in ells if e >= 11],
             "W-TOP": sorted(ells)[-8:]}
        return w

    WIN = windows(ells_with_data)

    def fit_from_map(m, ells):
        xs = [math.log2(e) for e in ells]
        ys = [math.log2(m[e]) for e in ells]
        return ols(xs, ys)

    # cluster bootstrap over the j-pool
    def bootstrap(tabA_, tabB_, ells, reps, seed):
        brng = random.Random(seed)
        idx = active
        out = {w: [] for w in WIN}
        quad_c = []
        for _ in range(reps):
            pick = [idx[brng.randrange(len(idx))] for _ in range(len(idx))]
            mA = {}
            mB = {}
            for ell in ells:
                dA = dict(tabA_[ell])
                vals = [dA[i] for i in pick if i in dA]
                if vals:
                    mA[ell] = median(vals)
                if ell in tabB_:
                    dB = dict(tabB_[ell])
                    v2 = [dB[i] for i in pick if i in dB]
                    if v2:
                        mB[ell] = median(v2)
            m = {}
            for ell in ells:
                if ell in mA and ell in mB:
                    m[ell] = min(mA[ell], mB[ell])
                elif ell in mA:
                    m[ell] = mA[ell]
            for w, wells in WIN.items():
                we = [e for e in wells if e in m]
                if len(we) >= 3:
                    fr = fit_from_map(m, we)
                    out[w].append(fr["slope"])
            we = [e for e in WIN["W-ALL"] if e in m]
            xs = [math.log2(e) for e in we]
            ys = [math.log2(m[e]) for e in we]
            if len(we) >= 4:
                quad_c.append(quad_fit(xs, ys)["c"])
        return out, quad_c

    boot, quad_c_boot = bootstrap(tabA, tabB, ells_with_data,
                                  BOOTSTRAP_REPLICATES, BOOTSTRAP_SEED)

    fits = {}
    for w, wells in WIN.items():
        f = fit_from_map(primary_per_ell, wells)
        tq = t_quantile_975(f["n"] - 2) if f["n"] > 2 else float('nan')
        ci_an = [f["slope"] - tq * f["slope_se"], f["slope"] + tq * f["slope_se"]]
        bs = boot[w]
        ci_bs = [percentile(bs, 0.025), percentile(bs, 0.975)] if bs else [None, None]
        # jackknife leave-one-ell-out
        jk = []
        for drop in wells:
            we = [e for e in wells if e != drop]
            if len(we) >= 3:
                jk.append(fit_from_map(primary_per_ell, we)["slope"])
        fits[w] = {
            "ell": wells, "n": f["n"], "gamma_hat": f["slope"],
            "intercept": f["intercept"], "slope_se": f["slope_se"],
            "t_quantile_0975_df": tq,
            "analytic_ci95": ci_an, "bootstrap_ci95": ci_bs,
            "bootstrap_replicates": len(bs),
            "jackknife_slope_min": min(jk) if jk else None,
            "jackknife_slope_max": max(jk) if jk else None,
            "r2": f["r2"], "max_abs_residual": f["max_abs_residual"],
            "residuals": {str(e): r for e, r in zip(wells, f["residuals"])},
        }

    lows = [fits[w]["bootstrap_ci95"][0] for w in WIN if fits[w]["bootstrap_ci95"][0] is not None]
    highs = [fits[w]["bootstrap_ci95"][1] for w in WIN if fits[w]["bootstrap_ci95"][1] is not None]
    gamma_reported = [min(lows), max(highs)]
    gamma_point = fits["W-MID"]["gamma_hat"]

    xs_all = [math.log2(e) for e in WIN["W-ALL"]]
    ys_all = [math.log2(primary_per_ell[e]) for e in WIN["W-ALL"]]
    qf = quad_fit(xs_all, ys_all)
    qc_ci = [percentile(quad_c_boot, 0.025), percentile(quad_c_boot, 0.975)]
    misspec = not (qc_ci[0] <= 0.0 <= qc_ci[1])
    x_max = max(xs_all)
    gamma_local_top = qf["b"] + 2 * qf["c"] * x_max

    R["fit"] = {
        "response": "y_ell = log2(median over the j-pool of per_entry(ell,j)), "
                    "per_entry taken as the MINIMUM over implementations at ell",
        "regressor": "x_ell = log2(ell)",
        "estimator": "ordinary least squares, unweighted",
        "windows": fits,
        "primary_window": "W-MID",
        "gamma_point_estimate_W_MID": gamma_point,
        "gamma_reported_interval": gamma_reported,
        "gamma_reported_halfwidth": (gamma_reported[1] - gamma_reported[0]) / 2.0,
        "bootstrap": {"method": "cluster bootstrap over the j-pool, resampling the "
                                "j-indices jointly with replacement",
                      "replicates": BOOTSTRAP_REPLICATES, "seed": BOOTSTRAP_SEED},
        "curvature": {"fit": "y = a + b x + c x^2 on W-ALL", "a": qf["a"], "b": qf["b"],
                      "c": qf["c"], "c_bootstrap_ci95": qc_ci,
                      "single_exponent_model_misspecified": bool(misspec),
                      "x_max": x_max, "gamma_local_top": gamma_local_top},
    }

    # gamma per implementation, and the inversion-charged sensitivity
    def gamma_of_map(m):
        we = [e for e in WIN["W-MID"] if e in m]
        return fit_from_map(m, we)["slope"] if len(we) >= 3 else None

    mA = {e: aggA[e]["median"] for e in aggA}
    mB = {e: aggB[e]["median"] for e in aggB}
    tabA3 = {}
    tabB3 = {}
    for r in all_primary:
        v = r["per_entry_inv_charged_3"]
        if v is None:
            continue
        (tabA3 if r["impl"] == "IMPL-A" else tabB3).setdefault(r["ell"], []).append(v)
    mA3 = {e: median(v) for e, v in tabA3.items()}
    R["fit"]["gamma_A_W_MID"] = gamma_of_map(mA)
    R["fit"]["gamma_B_W_MID"] = gamma_of_map(mB)
    R["fit"]["gamma_A_minus_gamma_B"] = (
        (R["fit"]["gamma_A_W_MID"] - R["fit"]["gamma_B_W_MID"])
        if R["fit"]["gamma_B_W_MID"] is not None else None)
    R["fit"]["gamma_sensitivity_inversions_charged_3_IMPL_A_W_MID"] = gamma_of_map(mA3)

    # C-NULL fit
    tabN = {}
    for r in R["samples_null"]:
        tabN.setdefault((r["impl"], r["ell"]), {})[r["j_index"]] = r["per_entry"]
    nullm = {}
    for ell in ells_with_data:
        va = tabN.get(("IMPL-A", ell))
        vb = tabN.get(("IMPL-B", ell))
        if not va:
            continue
        ma = median(list(va.values()))
        mb = median(list(vb.values())) if vb else None
        nullm[ell] = min(ma, mb) if mb is not None else ma
    null_fits = {}
    for w, wells in WIN.items():
        we = [e for e in wells if e in nullm]
        if len(we) >= 3:
            null_fits[w] = fit_from_map(nullm, we)["slope"]
    # bootstrap for gamma_null on W-MID (the primary window)
    brng = random.Random("null|%d" % BOOTSTRAP_SEED)
    nb = []
    for _ in range(BOOTSTRAP_REPLICATES):
        pick = [active[brng.randrange(len(active))] for _ in range(len(active))]
        m = {}
        for ell in ells_with_data:
            va = tabN.get(("IMPL-A", ell))
            vb = tabN.get(("IMPL-B", ell))
            if not va:
                continue
            aa = median([va[i] for i in pick if i in va])
            if vb:
                bb = median([vb[i] for i in pick if i in vb])
                m[ell] = min(aa, bb)
            else:
                m[ell] = aa
        we = [e for e in WIN["W-MID"] if e in m]
        if len(we) >= 3:
            nb.append(fit_from_map(m, we)["slope"])
    null_ci = [percentile(nb, 0.025), percentile(nb, 0.975)]
    gamma_null = null_fits.get("W-MID")
    null_pass = (abs(gamma_null) <= 0.15 and null_ci[0] <= 0.0 <= null_ci[1]) \
        if gamma_null is not None else None
    smallest = min(nullm) if nullm else None
    largest = max(nullm) if nullm else None
    R["controls"]["C-NULL"] = {
        "id": "C-NULL",
        "construction": ("for each ell and each pool j, a table of ell+1 entries "
                         "built by ell+1 successive non-backtracking 2-isogeny "
                         "steps, identical counting harness, identical "
                         "cost/entries convention, identical aggregation and fit"),
        "per_ell_per_entry": {str(k): v for k, v in nullm.items()},
        "gamma_null_by_window": null_fits,
        "gamma_null_primary_W_MID": gamma_null,
        "gamma_null_bootstrap_ci95_W_MID": null_ci,
        "flatness_smallest_ell": {"ell": smallest,
                                  "per_entry": nullm.get(smallest)},
        "flatness_largest_ell": {"ell": largest, "per_entry": nullm.get(largest)},
        "flatness_ratio_largest_over_smallest": (
            nullm[largest] / nullm[smallest] if nullm else None),
        "flatness_within_2_pm_0_5": (
            bool(2 ** -0.5 <= nullm[largest] / nullm[smallest] <= 2 ** 0.5)
            if nullm else None),
        "pass_criterion": "|gamma_null| <= 0.15 AND bootstrap 95% CI contains 0",
        "verdict": "pass" if null_pass else "fail"}
    log("  C-NULL: gamma_null = %s, CI = %s -> %s"
        % (gamma_null, null_ci, R["controls"]["C-NULL"]["verdict"]))

    # ---- pre-registered prediction verdict -------------------------------
    band = [0.75, 1.25]
    lo, hi = gamma_reported
    if lo >= band[0] and hi <= band[1]:
        pv = "confirmed"
    elif hi < band[0] or lo > band[1]:
        pv = "refuted"
    else:
        pv = "indiscriminate"
    bands = []
    if hi < 0.25:
        bands.append("paper-consistent: per-entry cost is O(1) in ell")
    if lo > 0.25 and hi < 1.25:
        bands.append("linear regime: per-entry cost ~ ell")
    if (lo <= 2.0 <= hi) or lo > 1.75:
        bands.append("RT-C1-consistent: supports the red team's gamma = 2 calibration")
    classification = bands[0] if len(bands) == 1 else (
        "INDISCRIMINATE - the reported interval spans more than one "
        "pre-registered band" if len(bands) > 1 else
        "spans a region between the pre-registered bands; reported as such")
    R["preregistered_prediction"] = {
        "predicted_value": 1.0, "acceptance_band": band,
        "gamma_reported_interval": gamma_reported,
        "verdict": pv, "classification_band_reading": classification,
        "classification_bands_matched": bands}

    # ---- admissibility ---------------------------------------------------
    adm = []
    hw = (hi - lo) / 2.0
    adm.append({"condition": "half-width of gamma_reported <= 0.25",
                "value": hw, "met": bool(hw <= 0.25)})
    adm.append({"condition": "max |residual| on W-MID <= 0.75 bit",
                "value": fits["W-MID"]["max_abs_residual"],
                "met": bool(fits["W-MID"]["max_abs_residual"] <= 0.75)})
    adm.append({"condition": "R^2 on W-MID >= 0.98", "value": fits["W-MID"]["r2"],
                "met": bool(fits["W-MID"]["r2"] >= 0.98)})
    ctrl_ok = (R["controls"]["C-INSTR"]["verdict"] == "pass" and
               R["controls"]["C-NULL"]["verdict"] == "pass" and
               R["controls"]["C-BASE.1"]["verdict"] == "pass" and
               R["controls"]["C-BASE.2"]["verdict"] == "pass" and
               R["controls"]["C-BASE.3"]["verdict"] == "pass" and
               R["controls"]["C-BASE.4"]["verdict"] in ("pass", "pass_with_observation") and
               R["controls"]["C-BASE.5"]["verdict"] == "pass" and
               R["controls"]["C-ALT.1"]["verdict"] == "pass")
    adm.append({"condition": "C-INSTR PASS, C-NULL PASS, C-BASE PASS, C-ALT.1 PASS",
                "value": ctrl_ok, "met": bool(ctrl_ok)})
    R["fit"]["admissibility"] = {
        "conditions": adm,
        "all_met": all(a["met"] for a in adm),
        "on_violation": ("gamma is still reported with the violated condition "
                         "named; evidence strength this run can support is "
                         "capped at `preliminary`. Nothing was tuned.")}

    # ---- tail checks -----------------------------------------------------
    top_ell = max(WIN["W-ALL"])
    pred_top = fits["W-MID"]["intercept"] + fits["W-MID"]["gamma_hat"] * math.log2(top_ell)
    obs_top = math.log2(primary_per_ell[top_ell])
    R["tail_checks"] = {
        "top_of_range_consistency": {
            "largest_achieved_ell": top_ell,
            "observed_log2_per_entry": obs_top,
            "W_MID_fit_predicted_log2_per_entry": pred_top,
            "deviation_bits": obs_top - pred_top,
            "exceeds_1_bit": bool(abs(obs_top - pred_top) > 1.0)},
        "null_flatness": {
            "smallest_ell": smallest, "largest_ell": largest,
            "per_entry_smallest": nullm.get(smallest),
            "per_entry_largest": nullm.get(largest),
            "ratio": (nullm[largest] / nullm[smallest]) if nullm else None,
            "within_2_pm_0_5": R["controls"]["C-NULL"]["flatness_within_2_pm_0_5"]},
        "implementation_gap": {
            "gamma_A_minus_gamma_B": R["fit"]["gamma_A_minus_gamma_B"],
            "note": "a substantial negative gap is the quantitative form of "
                    "RT-C1's caveat that a better implementation lowers the exponent"},
    }

    # ---- extrapolation ---------------------------------------------------
    ext = []
    for row in VOW_CONSTANTS:
        s = math.sqrt(row["log2p"])
        e = {"name": row["name"], "log2p": row["log2p"],
             "log2_B_opt_input_constant_from_RUN_P13VOW_001": row["log2_B_opt"],
             "sqrt_log2p_recomputed_here": s,
             "c_at_gamma_low": gamma_reported[0] * row["log2_B_opt"] / s,
             "c_at_gamma_point": gamma_point * row["log2_B_opt"] / s,
             "c_at_gamma_high": gamma_reported[1] * row["log2_B_opt"] / s}
        if misspec:
            e["c_at_gamma_local_top_sensitivity"] = gamma_local_top * row["log2_B_opt"] / s
        ext.append(e)
    R["extrapolation"] = {
        "status": "EXTRAPOLATION, NOT A MEASUREMENT. Law fixed before any datum existed.",
        "law": "c = gamma * log2(B_opt) / sqrt(log2 p)",
        "gamma_used": {"low": gamma_reported[0], "point": gamma_point,
                       "high": gamma_reported[1],
                       "point_definition": "W-MID OLS slope (the pre-registered primary window)"},
        "rows": ext,
        "declared_assumptions": ["L1 power-law extension to ell ~ B_opt: UNTESTED",
                                 "L2 charging at ell = B_opt: DECLARED, NOT MEASURED",
                                 "L3 B_opt inherited from RUN-P13VOW-001 with its "
                                 "0.05-3.51 bit irreproducibility band",
                                 "L4 gamma measured for this pure-Python implementation "
                                 "pair; batched modular-polynomial evaluation not implemented"]}

    # secondary L2 measurement: kappa from the C-BASE.4 exhaustive builds
    kap = []
    for (B, X) in pairs:
        num = 0.0
        den = 0
        for ji in active[:1]:
            for ch in poc_isogs(B, Fraction(X), [pool[ji]], rootfn):
                if len(ch) >= 3:
                    num += math.log2(ch[-2])
                    den += 1
        if den:
            kap.append({"B": B, "X": X, "entries": den,
                        "entry_weighted_mean_log2_ell": num / den,
                        "kappa": (num / den) / math.log2(B)})
    R["secondary_L2_kappa"] = {
        "note": "SECONDARY under assumption L2; carries its own untested transfer "
                "from tiny B to B_opt ~ 2^14",
        "rows": kap}
    if kap:
        kmean = sum(k["kappa"] for k in kap) / len(kap)
        R["secondary_L2_kappa"]["kappa_mean_over_rows"] = kmean
        R["secondary_L2_kappa"]["c_kappa_rows"] = [
            {"name": row["name"], "log2p": row["log2p"],
             "c_kappa_at_gamma_point": gamma_point * kmean * row["log2_B_opt"]
             / math.sqrt(row["log2p"])}
            for row in VOW_CONSTANTS]

    R["phases"]["fits_seconds"] = round(time.time() - t, 3)

    # ---- achieved scope --------------------------------------------------
    spe = {}
    for r in all_primary:
        spe.setdefault(str(r["ell"]), {}).setdefault(r["impl"], 0)
        spe[str(r["ell"])][r["impl"]] += 1
    R["achieved_scope"] = {
        "ell_grid_achieved": ells_with_data,
        "ell_min": min(ells_with_data), "ell_max": max(ells_with_data),
        "n_ell": len(ells_with_data),
        "core_grid_required": CORE_GRID,
        "core_grid_complete": bool(set(CORE_GRID) <= set(ells_with_data)),
        "samples_per_ell_achieved": spe,
        "pool_size": len(active),
        "extension_ell_completed": ext_done,
        "dropped_ell": dropped,
        "minimum_viable_grid_met": bool(
            len(ells_with_data) >= 12 and any(e <= 3 for e in ells_with_data)
            and any(e >= 43 for e in ells_with_data)),
    }

    R["finished_utc"] = datetime.now(timezone.utc).isoformat()
    R["total_wall_clock_seconds"] = round(elapsed(), 3)
    ru_self = resource.getrusage(resource.RUSAGE_SELF)
    ru_child = resource.getrusage(resource.RUSAGE_CHILDREN)
    R["resource_measurements"] = {
        "note": "/usr/bin/time is not present in this image; resource usage is "
                "measured with resource.getrusage() inside the program",
        "user_cpu_seconds_self": ru_self.ru_utime,
        "system_cpu_seconds_self": ru_self.ru_stime,
        "user_cpu_seconds_children": ru_child.ru_utime,
        "system_cpu_seconds_children": ru_child.ru_stime,
        "total_cpu_seconds": (ru_self.ru_utime + ru_self.ru_stime
                              + ru_child.ru_utime + ru_child.ru_stime),
        "max_rss_kib_self": ru_self.ru_maxrss,
        "max_rss_kib_largest_child": ru_child.ru_maxrss,
        "workers": args.workers,
        "budget_wall_clock_seconds": args.budget_seconds,
        "budget_memory_gb": 8,
        "budget_total_cpu_hours": 6.0,
    }
    R["counted_multiplications_total_all_measured_regions"] = sum(
        r["cost"] for r in R["samples_primary"] + R["samples_null"])

    json.dump(R, open(args.out, "w"), indent=1)
    log("wrote %s (%.1f MB)" % (args.out, os.path.getsize(args.out) / 1e6))
    log("DONE in %.1fs" % elapsed())
    return 0


if __name__ == "__main__":
    sys.exit(main())
