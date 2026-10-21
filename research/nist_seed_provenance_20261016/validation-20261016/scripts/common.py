"""Shared primitives for VAL-20261016-cd9156, written from public texts only.

drand48 family: POSIX / Open Group drand48 page (../specs/posix_drand48_excerpt.txt):
  X_{n+1} = (a X_n + c) mod 2^48, a = 0x5DEECE66D, c = 0xB;
  srand48(v): high-order 32 bits of X <- low-order 32 bits of v, low 16 bits <- 0x330E;
  every drand48()/lrand48() call first advances X, then takes high-order bits of the NEW X.
  lrand48() returns a value in [0, 2^31): the 31 high-order bits, X >> 17.
  drand48() returns a double in [0,1) built from high-order bits; the usual (and the
  only exact) transformation of all 48 bits is X / 2^48. For any reading that uses at
  least the 8 high-order bits, (int)(drand48()*256) == X >> 40 (checked numerically in
  j1_q1_seeds.py, also against the platform libc).

X9.62 seed-to-c map: FIPS 186-2 App. 6.4/6.5 and SP 800-186 C.3.1/C.3.2
(../specs/*excerpt.txt): l = bitlen(p), v = floor((l-1)/160), w = l - 160 v - 1,
h0 = w rightmost bits of SHA-1(s), h_i = SHA-1((z+i) mod 2^160) for i = 1..v,
c = int(h0 || h1 || ... || hv); verify b^2 c == -27 (mod p).
(X9.62's wording "rightmost w+1 bits with the leftmost bit cleared" gives the same c.)
"""
import hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # validation-20261016/
BUNDLE = os.path.dirname(ROOT)                     # research/nist_seed_provenance_20261016/

A = 0x5DEECE66D
C = 0xB
M = 1 << 48
MASK = M - 1
AINV = pow(A, -1, M)
SRAND_LOW = 0x330E


def srand48(v):
    return ((v & 0xFFFFFFFF) << 16) | SRAND_LOW


def step(x):
    return (A * x + C) & MASK


def back(x):
    return (AINV * (x - C)) & MASK


def affine_pow(n):
    """(a_n, c_n) with LCG^n(x) = a_n x + c_n mod 2^48."""
    an, cn = 1, 0
    ba, bc = A, C
    while n:
        if n & 1:
            an, cn = (ba * an) & MASK, (ba * cn + bc) & MASK
        ba, bc = (ba * ba) & MASK, (ba * bc + bc) & MASK
        n >>= 1
    return an, cn


def jump(x, n):
    an, cn = affine_pow(n)
    return (an * x + cn) & MASK


def drand48_byte_stream(t, nbytes):
    """bytes of (int)(drand48()*256) for nbytes consecutive calls after srand48(t)."""
    x = srand48(t)
    out = bytearray(nbytes)
    for k in range(nbytes):
        x = (A * x + C) & MASK
        out[k] = x >> 40
    return bytes(out)


def x962_c(seed, l, variant="std"):
    """seed: 20 bytes. Returns integer c. Variants for the J2 known-false controls:
    std   : as specified
    a_noclear : take w+1 rightmost bits (leftmost bit of the X9.62 chunk not cleared)
    b_left    : take the w LEFTMOST bits of SHA-1(s) instead of the rightmost
    c_nowrap  : (z+i) without the mod 2^160 wrap (161-bit string if it overflows)
    d_le      : s_i = little-endian encoding of (z_le + i), z_le = little-endian reading of s
    e_i0      : i runs 0..v-1 (h_1 = SHA-1(s), ...)
    """
    g = 160
    v = (l - 1) // g
    w = l - g * v - 1
    H = int.from_bytes(hashlib.sha1(seed).digest(), "big")
    if variant == "a_noclear":
        h0 = H & ((1 << (w + 1)) - 1)
        wbits = w + 1
    elif variant == "b_left":
        h0 = H >> (g - w)
        wbits = w
    else:
        h0 = H & ((1 << w) - 1)
        wbits = w
    c = h0
    z = int.from_bytes(seed, "big")
    zle = int.from_bytes(seed, "little")
    for i in range(1, v + 1):
        if variant == "c_nowrap":
            zi = z + i
            si = zi.to_bytes((zi.bit_length() + 7) // 8 if zi >= 1 << g else 20, "big")
        elif variant == "d_le":
            si = ((zle + i) % (1 << g)).to_bytes(20, "little")
        elif variant == "e_i0":
            si = ((z + i - 1) % (1 << g)).to_bytes(20, "big")
        else:
            si = ((z + i) % (1 << g)).to_bytes(20, "big")
        hi = int.from_bytes(hashlib.sha1(si).digest(), "big")
        c = (c << g) | hi
    return c


def load_params():
    with open(os.path.join(ROOT, "out", "params.json")) as f:
        js = json.load(f)
    out = {}
    for k, v in js.items():
        rec = dict(v)
        for kk in ("p", "a", "b", "n", "seed", "poly"):
            if kk in rec:
                rec[kk] = int(rec[kk], 16)
        rec["seed_bytes"] = rec["seed"].to_bytes(20, "big")
        out[k] = rec
    return out


# The six runs as stated in the README census table (t, field label, block count).
RUNS = [
    (863711343, "p239", 3048),
    (863966734, "p192", 6013),
    (871002724, "p521", 1136),
    (871696354, "p256", 1842),
    (872952608, "p384", 2688),
    (891607927, "p224", 7026),
]
# Which published prime curves share each run's field (by p, verified in j1).
FIELD_CURVE = {"p239": "prime239v1", "p192": "P-192", "p521": "P-521",
               "p256": "P-256", "p384": "P-384", "p224": "P-224"}
PRIME_CURVES = ["P-192", "prime192v2", "prime192v3", "P-224", "prime239v1",
                "prime239v2", "prime239v3", "P-256", "P-384", "P-521"]
BINARY_CURVES = ["B-233", "B-283", "B-409", "B-571"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def order_log(label, path):
    """Append 'UTC sha256 label path' to logs/order.log (constraint 4)."""
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    rel = os.path.relpath(path, ROOT)
    with open(os.path.join(ROOT, "logs", "order.log"), "a") as f:
        f.write(f"{ts}\t{sha256_file(path)}\t{label}\t{rel}\n")
