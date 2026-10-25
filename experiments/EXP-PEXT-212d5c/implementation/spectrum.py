#!/usr/bin/env python3
"""Abstract (m, r, genus) spectrum of the (2,...,2) GHS compositum by 2-torsion type, odd characteristic.

EXP-PEXT-212d5c, derivation aid (Lemma M7 / E7 / O7 / T7 of H-PEXT-d536a1). Pure combinatorics, no field:
B' has four points of K-degree type split (1,1,1,1), (1,1,2) or (1,3) (the point at infinity counted as a
K-rational point). A K-class of degree d lies either in a short sigma-orbit (size d, contained in B', a
constant summand of the module, annihilator x + 1; possible only when gcd(d, n) = 1) or in a free orbit (size n d) at a position of
Z/n = (Z/nd)/<n>; classes of the same degree may share a free orbit at distinct positions. With s_O the
position polynomial of a free orbit O, h_O = (x^n - 1)/gcd(s_O, x^n - 1), m = deg lcm of all h (x + 1 for
short orbits), r = sum of orbit sizes, genus = 2^(m-2)(r-4)+1 for m >= 2. Every realised structure has one of
these (type, m, r); the converse (which abstract configuration is realised by some curve) is not claimed.

  python3 spectrum.py [n ...]      -> one JSON line per n: allowed (m, r, genus) per type, spectra, floors
Standard library only.
"""
from __future__ import annotations

import itertools
import math
import json
import sys


def pmod(a: int, b: int) -> int:
    """Remainder of F_2[x] polynomials as bit masks."""
    db = b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        a ^= b << (a.bit_length() - 1 - db)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def pmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pdiv(a: int, b: int) -> int:
    q = 0
    db = b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        s = a.bit_length() - 1 - db
        q |= 1 << s
        a ^= b << s
    assert a == 0
    return q


def plcm(a: int, b: int) -> int:
    return pdiv(pmul(a, b), pgcd(a, b))


def deg(a: int) -> int:
    return a.bit_length() - 1


def configurations(n: int, degrees: tuple[int, ...]):
    """Yield (m, r) for every abstract placement of K-classes of the given degrees."""
    xn1 = (1 << n) | 1
    k = len(degrees)
    # placement of class i: ('s',) short orbit, or ('f', orbit_label, position); orbit labels canonical
    for labels in itertools.product(range(-1, k), repeat=k):  # -1 = short orbit
        # canonical: free orbit labels appear in increasing first-use order, classes in one orbit share degree
        seen: list[int] = []
        ok = True
        for i, lab in enumerate(labels):
            if lab < 0:
                continue
            if lab not in seen:
                if lab != len(seen):
                    ok = False
                    break
                seen.append(lab)
        if not ok:
            continue
        # a short orbit (size d) exists only for gcd(d, n) = 1: a K-point of degree d in F_{q^d}
        if any(lab < 0 and math.gcd(degrees[i], n) != 1 for i, lab in enumerate(labels)):
            continue
        orbit_deg: dict[int, int] = {}
        for i, lab in enumerate(labels):
            if lab >= 0:
                if orbit_deg.setdefault(lab, degrees[i]) != degrees[i]:
                    ok = False
        if not ok:
            continue
        members = {lab: [i for i in range(k) if labels[i] == lab] for lab in orbit_deg}
        for poss in itertools.product(range(n), repeat=sum(len(v) for v in members.values())):
            it = iter(poss)
            pos = {lab: [next(it) for _ in v] for lab, v in members.items()}
            if any(len(set(p)) != len(p) for p in pos.values()):
                continue
            h = 1
            r = 0
            for i, lab in enumerate(labels):
                if lab < 0:
                    h = plcm(h, 0b11)
                    r += degrees[i]
            for lab, p in pos.items():
                s = 0
                for e in p:
                    s ^= 1 << e
                h = plcm(h, pdiv(xn1, pgcd(s, xn1)))
                r += n * orbit_deg[lab]
            yield deg(h), r


TYPES = {"split": (1, 1, 1, 1), "Z2": (1, 1, 2), "odd": (1, 3)}


def genus(m: int, r: int) -> int:
    return (1 << (m - 2)) * (r - 4) + 1


def spectrum(n: int) -> dict:
    out: dict = {"n": n, "types": {}}
    for name, degs in TYPES.items():
        mr = sorted(set(configurations(n, degs)))
        gs = sorted({genus(m, r) for m, r in mr if m >= 2})
        out["types"][name] = {
            "m_r": [[m, r] for m, r in mr],
            "genera": gs,
            "floor": gs[0],
            "floor_m_r": sorted([m, r] for m, r in mr if m >= 2 and genus(m, r) == gs[0]),
            "m_values": sorted({m for m, _ in mr}),
        }
    out["m_values_all"] = sorted({m for t in out["types"].values() for m in t["m_values"]})
    return out


if __name__ == "__main__":
    for n in [int(a) for a in sys.argv[1:]] or [3, 5, 7]:
        print(json.dumps(spectrum(n), sort_keys=True))
