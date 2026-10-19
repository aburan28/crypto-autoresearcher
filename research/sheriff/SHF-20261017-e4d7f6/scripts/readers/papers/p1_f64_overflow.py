"""P1 blind re-derivation: which standard group orders have n^4 > f64::MAX.

Exact integer arithmetic only. Orders are written from the published standards
(SEC 2 v2 for secp*k1, FIPS 186-4 for P-*, RFC 5639 for brainpool); the
256-bit ones are additionally checked against #E(F_p) by Sage in
p1_curve_orders.sage. No producer code is read or imported.

Also: a textbook float64 Gram-Schmidt on the initial Boneh-Venkatesan basis
(m = 8, k_bits = 3/4 n_bits, random a, t), unscaled and with the 2^-(max_bits-500)
scaling the note describes, to see (a) where squared GS norms overflow and
(b) the size of the cancellation residual relative to the true component.
"""
import math
import random
import sys

import numpy as np

F64_MAX = (2**53 - 1) * 2**971
assert float(F64_MAX) == sys.float_info.max

ORDERS = {
    "secp192k1": 0xFFFFFFFFFFFFFFFFFFFFFFFE26F2FC170F69466A74DEFD8D,
    "secp224k1": 0x010000000000000000000000000001DCE8D2EC6184CAF0A971769FB1F7,
    "secp256k1": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    "P-256": 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
    "brainpoolP256r1": 0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7,
    "P-384": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973,
    "brainpoolP384r1": 0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565,
    "P-521": 6864797660130609714981900799081393217269435300143305409394463459185543183397655394245057746333217197532963996371363321113864768612440380340372808892707005449,
}

FIELDS = {
    "secp192k1": 2**192 - 2**32 - 4553,
    "secp224k1": 2**224 - 2**32 - 6803,
    "secp256k1": 2**256 - 2**32 - 977,
    "P-256": 2**256 - 2**224 + 2**192 + 2**96 - 1,
    "brainpoolP256r1": 0xA9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377,
    "P-384": 2**384 - 2**128 - 2**96 + 2**32 - 1,
    "brainpoolP384r1": 0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B412B1DA197FB71123ACD3A729901D1A71874700133107EC53,
    "P-521": 2**521 - 1,
}


def is_probable_prime(x, rounds=40):
    if x < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if x % q == 0:
            return x == q
    d, r = x - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    rr = random.Random(1)
    for _ in range(rounds):
        a = rr.randrange(2, x - 1)
        y = pow(a, d, x)
        if y in (1, x - 1):
            continue
        for _ in range(r - 1):
            y = y * y % x
            if y == x - 1:
                break
        else:
            return False
    return True


print("== order sanity: n prime (MR-40), p prime, Hasse |p+1-n| <= 2 sqrt(p) (cofactor 1) ==")
for name, n in ORDERS.items():
    p = FIELDS[name]
    t = p + 1 - n
    print(f"{name:16s} n_bits={n.bit_length()} n_prime={is_probable_prime(n)} p_prime={is_probable_prime(p)} hasse={t*t <= 4*p}")

print("\n== exact n^4 vs f64::MAX = (2^53-1)*2^971 ==")
print(f"{'curve':16s} {'n_bits':>6s}  n^4>MAX  log2(n^4/MAX)        n^4 - MAX sign / margin")
for name, n in ORDERS.items():
    n4 = n**4
    over = n4 > F64_MAX
    # log2 ratio with enough precision via integer shifting
    ratio = math.log2(n4) - math.log2(F64_MAX)  # math.log2 accepts big ints exactly-enough
    print(f"{name:16s} {n.bit_length():6d}  {str(over):7s}  {ratio:+.6e}")

# threshold: smallest n with n^4 > F64_MAX
lo, hi = 1, 2**257
while lo < hi:
    mid = (lo + hi) // 2
    if mid**4 > F64_MAX:
        hi = mid
    else:
        lo = mid + 1
T = lo
print(f"\nthreshold N* = min n with n^4 > f64::MAX: 2^256 - N* = {2**256 - T} (~2^{math.log2(2**256 - T):.2f})")
for name in ("secp256k1", "P-256", "brainpoolP256r1"):
    n = ORDERS[name]
    d = 2**256 - n
    print(f"  {name:16s} 2^256 - n = ~2^{math.log2(d):.2f}  -> {'above' if n >= T else 'below'} threshold")
# What the f64 conversion does to n itself
for name in ("secp256k1", "P-256", "brainpoolP256r1"):
    n = ORDERS[name]
    fn = float(n)
    sq = fn * fn
    try:
        q = sq * sq
    except OverflowError:
        q = "OverflowError"
    print(f"  float({name}) == 2^256: {fn == 2.0**256};  (float(n)^2)^2 = {q}")

print("\n== textbook float64 Gram-Schmidt on initial BV basis (m=8, k_bits=3n/4) ==")


def bv_basis(n, m, kb, rng):
    a = [rng.randrange(n) for _ in range(m)]
    t = [rng.randrange(n) for _ in range(m)]
    B = []
    for i in range(m):
        row = [0] * (m + 2)
        row[i] = n * n
        B.append(row)
    B.append([n * x for x in a] + [2**kb, 0])
    B.append([n * x for x in t] + [0, n * 2**kb])
    return B


def gs_f64(B, shift):
    rows = [np.array([float_scaled(x, shift) for x in r], dtype=np.float64) for r in B]
    bstar = []
    norms = []
    with np.errstate(over="ignore", invalid="ignore"):
        for i, b in enumerate(rows):
            v = b.copy()
            for j, bs in enumerate(bstar):
                nj = norms[j]
                mu = (b @ bs) / nj if nj > 0 else 0.0
                v = v - mu * bs
            bstar.append(v)
            norms.append(float(v @ v))
    return bstar, norms


def float_scaled(x, shift):
    """x / 2^shift as float64, exact-to-rounding (x may exceed f64 range)."""
    if x == 0:
        return 0.0
    s = -1.0 if x < 0 else 1.0
    x = abs(x)
    nb = x.bit_length()
    if nb > 60:
        top = x >> (nb - 60)
        try:
            return s * math.ldexp(float(top), nb - 60 - shift)
        except OverflowError:
            return s * math.inf
    return s * math.ldexp(float(x), -shift)


rng = random.Random(20261017)
m = 8
for name, n in ORDERS.items():
    nb = n.bit_length()
    kb = 3 * nb // 4
    B = bv_basis(n, m, kb, rng)
    maxbits = max(x.bit_length() for r in B for x in r if x)
    for label, shift in (("unscaled", 0), ("scaled", max(0, maxbits - 500))):
        bstar, norms = gs_f64(B, shift)
        first_norm = norms[0]
        nonfinite = sum(1 for x in norms if not math.isfinite(x))
        # true component of b*_m (row index m) is 2^kb at coordinate m; residual = max |b*_m[l]| for l<m
        bm = bstar[m]
        resid = max(abs(float(x)) for x in bm[:m])
        true = abs(float(bm[m]))
        ratio = (math.log2(resid) - math.log2(true)) if (resid > 0 and true > 0 and math.isfinite(resid)) else float("nan")
        print(f"{name:16s} {label:8s} shift={shift:4d} ||b*_0||^2={first_norm:.3e} nonfinite_norms={nonfinite:2d} "
              f"row m: max|resid[l<m]|={resid:.3e} true b*_m[m]={true:.3e} log2(resid/true)={ratio:+.1f}")
