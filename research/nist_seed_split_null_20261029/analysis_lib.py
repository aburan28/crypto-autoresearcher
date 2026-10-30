"""Helpers shared with analysis.py (identical definitions)."""
import json

def primes(lo, hi):
    s = bytearray([1]) * (hi + 1); s[0:2] = b"\0\0"
    for i in range(2, int(hi ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(lo, hi + 1) if s[i]]


def chi(x, l):
    x %= l
    if x == 0: return 0
    return 1 if pow(x, (l - 1) // 2, l) == 1 else -1


_cache = {}
def probs(p, l, prime_order=True):
    """P(split), P(ramified) for Frob uniform in GL2(F_l) with det p,
    excluding eigenvalue 1 when prime_order. #{A: tr=u, det=d} = l^2 + l*chi(u^2-4d)."""
    key = (p % l, l, prime_order)
    if key in _cache: return _cache[key]
    d = p % l; w = {1: 0, -1: 0, 0: 0}
    for u in range(l):
        if prime_order and (1 - u + d) % l == 0: continue
        c = chi(u * u - 4 * d, l); w[c] += l * l + l * c
    s = sum(w.values()); _cache[key] = (w[1] / s, w[0] / s); return _cache[key]


def pmf(qs):
    f = [1.0]
    for q in qs:
        g = [0.0] * (len(f) + 1)
        for k, v in enumerate(f): g[k] += v * (1 - q); g[k + 1] += v * q
        f = g
    return f



def load_rows(path):
    raw = json.load(open(path)); rows = []
    for r in raw["rows"]:
        p = int(r["p_hex"], 16); n = int(r["n_hex"], 16); t = p + 1 - n
        rows.append(dict(name=r["name"], label=r["label"], bits=r["field_bits"], uid=r["curve_uid"],
                         p=p, n=n, t=t, D=t * t - 4 * p, twist=p + 1 + t))
    return rows
