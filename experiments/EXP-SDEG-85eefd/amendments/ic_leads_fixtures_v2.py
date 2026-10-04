# Deterministic fixture derivation for the protocol-version-2 amendments of the
# seven IC-lead experiments (BATCH-739b32). Run with: sage -python <this file>
# Output is JSON on stdout; the amendments freeze the values it printed and
# the executor must reproduce them byte-for-byte before any scientific run.
import hashlib
import json
import sys

from sage.all import GF, EllipticCurve, Integer, is_prime, next_prime

EMBEDDING_DEGREE_FLOOR = 20


def h(label):
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def admissible(p, a, b):
    """Return (N, reason) where reason is None when the curve is admitted."""
    F = GF(p)
    if a % p == 0 or b % p == 0:
        return None, "j in {0,1728}"
    if (4 * a**3 + 27 * b**2) % p == 0:
        return None, "singular"
    E = EllipticCurve(F, [a, b])
    N = Integer(E.order())
    if not is_prime(N):
        return N, "order not prime"
    if N == p:
        return N, "anomalous"
    if N == p + 1:
        return N, "supersingular"
    for k in range(1, EMBEDDING_DEGREE_FLOOR + 1):
        if pow(p, k, N) == 1:
            return N, f"embedding degree {k}"
    return N, None


def base_point(p, a, b):
    """Smallest x on the curve, with y = min(y, p - y)."""
    F = GF(p)
    for xx in range(p):
        rhs = F(xx) ** 3 + a * F(xx) + b
        if rhs.is_square():
            y = int(rhs.sqrt())
            return [xx, min(y, p - y)]
    raise RuntimeError("no point")


def generic_fixture(exp, bits, seed):
    for c in range(1_000_000):
        x = h(f"{exp}/v2|curve|{bits}|{seed}|{c}")
        p = next_prime(2 ** (bits - 1) + (x % 2 ** (bits - 1)))
        if p.nbits() != bits:
            continue
        a = (x >> 64) % p
        b = (x >> 128) % p
        N, why = admissible(p, a, b)
        if why is None:
            return dict(exp=exp, bits=bits, seed=seed, counter=c, p=int(p), a=int(a),
                        b=int(b), N=int(N), G=base_point(p, a, b))
    raise RuntimeError("no fixture")


P1480 = {8: (32801, 1, 5), 16: (1048609, 5, 7), 32: (33554593, 3, 9)}


def sdeg_fixture(L, seed):
    p, a0, b0 = P1480[L]
    if seed == 1:
        N, why = admissible(p, a0, b0)
        assert why is None or why.startswith("embedding"), why
        return dict(exp="EXP-SDEG-85eefd", L=L, seed=1, counter=None, p=p, a=a0, b=b0,
                    N=int(N), G=base_point(p, a0, b0), admission_note=why,
                    source="P1480 fixture verbatim")
    for c in range(1_000_000):
        x = h(f"EXP-SDEG-85eefd/v2|curve|L{L}|{seed}|{c}")
        a = x % p
        b = (x >> 64) % p
        N, why = admissible(p, a, b)
        if why is None:
            return dict(exp="EXP-SDEG-85eefd", L=L, seed=seed, counter=c, p=p, a=int(a),
                        b=int(b), N=int(N), G=base_point(p, a, b), admission_note=None,
                        source="v2 hash rule")
    raise RuntimeError("no fixture")


CELLS = {
    "EXP-RELN-c5a377": ([16, 20, 24], [11, 12, 13]),
    "EXP-ICEX-aaccfc": ([16, 20], [21, 22, 23]),
    "EXP-ICEX-11c498": ([16, 18, 20], [31, 32, 33]),
    "EXP-ICEX-ba5ca2": ([16, 20], [41, 42, 43]),
    "EXP-ECDLP-c74a83": ([16, 18, 20], [51, 52, 53]),
}

out = {"EXP-SDEG-85eefd": [sdeg_fixture(L, s) for L in (8, 16, 32) for s in (1, 2, 3)]}
for exp, (bits_list, seeds) in CELLS.items():
    out[exp] = [generic_fixture(exp, bits, s) for bits in bits_list for s in seeds]
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
