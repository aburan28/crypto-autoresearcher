#!/usr/bin/env python3
"""Blind re-derivation (TASK-20261001-4aefce, J3) of the 2-large-prime
summation-graph statistics of EXP-RELN-c5a377 protocol v4 for one fixture.

Written only from specification.yaml + AMD-20260926-a7d25d (C-2..C-5) +
AMD-20260929-988139 + AMD-20260929-cc7226 and the fixture curve parameters.
The protocol does not pin the seed-to-integer map, the attempt index base,
the choice among several decompositions of one R_j, the vertex set, or
multi-edge/loop handling, so every defensible reading is enumerated and
reported separately rather than one being picked silently.
"""
import argparse
import hashlib
import itertools
import json
import math
import random
import sys
from collections import defaultdict

O = None


def inv(x, p):
    return pow(x, p - 2, p)


def add(P, Q, a, p):
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return O
    if P == Q:
        lam = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def neg(P, p):
    return O if P is O else (P[0], (-P[1]) % p)


def mul(k, P, a, p):
    R = O
    while k:
        if k & 1:
            R = add(R, P, a, p)
        P = add(P, P, a, p)
        k >>= 1
    return R


def sqrt_mod(n, p):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def ceil_root(n, k):
    """Exact ceil(n^(1/k)) for integers."""
    r = int(round(n ** (1.0 / k)))
    while r ** k < n:
        r += 1
    while r > 1 and (r - 1) ** k >= n:
        r -= 1
    return r


def ceil_pow_frac(n, num, den):
    """Exact ceil(n^(num/den)) = smallest r with r^den >= n^num."""
    target = n ** num
    r = int(round(n ** (num / den)))
    while r ** den < target:
        r += 1
    while r > 1 and (r - 1) ** den >= target:
        r -= 1
    return r


def H(label):
    return hashlib.sha256(label.encode("utf-8")).digest()


# ---- seed-to-integer readings (spec seed_rule underdetermines these) -----

def draws(label, q, n, scheme):
    """Return n integers in [0, q) derived from `label` under `scheme`."""
    if scheme == "mod_halves":  # one digest, 128-bit halves, each mod q
        d = H(label)
        vals = [int.from_bytes(d[:16], "big") % q, int.from_bytes(d[16:], "big") % q]
        return vals[:n]
    if scheme == "mod_divmod":  # one digest h; h mod q, (h//q) mod q
        h = int.from_bytes(H(label), "big")
        out = []
        for _ in range(n):
            out.append(h % q)
            h //= q
        return out
    if scheme == "mod_ctr":  # sub-labels label|0, label|1 ; each h mod q
        return [int.from_bytes(H(f"{label}|{i}"), "big") % q for i in range(n)]
    if scheme == "maskreject_ctr":  # top bitlen(q) bits of sha256(label|ctr), reject >= q
        bl = q.bit_length()
        out, ctr = [], 0
        while len(out) < n:
            h = int.from_bytes(H(f"{label}|{ctr}"), "big") >> (256 - bl)
            ctr += 1
            if h < q:
                out.append(h)
        return out
    raise ValueError(scheme)


def target_k(prefix, bits, seed, q, scheme):
    label = f"{prefix}|target|{bits}|{seed}"
    k = draws(label, q, 1, scheme)[0]
    ctr = 0
    while k == 0:  # never observed; k must be nonzero
        ctr += 1
        k = draws(f"{label}|nz{ctr}", q, 1, scheme)[0]
    return k


# ---- decomposition --------------------------------------------------------

def enumerate_lp_points(a, b, p, B2):
    pts = []
    for x in range(B2):
        f = (x * x * x + a * x + b) % p
        y = sqrt_mod(f, p)
        if y is None:
            continue
        ys = sorted({y, (-y) % p})
        for yy in ys:
            pts.append((x, yy))
    return pts


def decompositions(R, pts, ptset_x, a, p, B2):
    """All (P1, P2) with P1 in scan order, P2 = R - P1, x(P2) < B2.
    Scan order: x ascending, then y ascending. P2 = O is excluded."""
    out = []
    for P1 in pts:
        P2 = add(R, neg(P1, p), a, p)
        if P2 is O:
            continue
        if P2[0] < B2:
            out.append((P1, P2))
    return out


def klass(x1, x2, B):
    s = (x1 < B) + (x2 < B)
    return {2: "full", 1: "1LP", 0: "2LP"}[s]


PRIO = {"full": 0, "1LP": 1, "2LP": 2}
ROOT = "root"


def relation_edges(decs, B, choice):
    """Turn the decompositions of one attempt into relations per `choice`."""
    if not decs:
        return []
    if choice == "first":
        sel = [decs[0]]
    elif choice == "best":
        sel = [min(decs, key=lambda d: PRIO[klass(d[0][0], d[1][0], B)])]
    elif choice == "all":
        seen, sel = set(), []
        for d in decs:
            key = frozenset(d)
            if key in seen:
                continue
            seen.add(key)
            sel.append(d)
    else:
        raise ValueError(choice)
    rels = []
    for P1, P2 in sel:
        x1, x2 = P1[0], P2[0]
        c = klass(x1, x2, B)
        if c == "full":
            rels.append(("full", None))
        elif c == "1LP":
            lp = x1 if x1 >= B else x2
            rels.append(("1LP", (lp, ROOT)))
        else:
            rels.append(("2LP", (x1, x2)))
    return rels


# ---- graph statistics -----------------------------------------------------

def graph_stats(edges, lp_classes, vertex_mode, edge_mode, L):
    if edge_mode == "simple":
        E = list({frozenset(e) if e[0] != e[1] else None for e in edges} - {None})
        E = [tuple(sorted(e, key=str)) for e in E]
    else:
        E = list(edges)
    V = set()
    for u, v in E:
        V.add(u)
        V.add(v)
    if vertex_mode == "all":
        V |= set(lp_classes)
        V.add(ROOT)
    parent = {v: v for v in V}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in E:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    comp_v = defaultdict(int)
    comp_e = defaultdict(int)
    for v in V:
        comp_v[find(v)] += 1
    for u, v in E:
        comp_e[find(u)] += 1
    c = len(comp_v)
    cwc = sum(1 for r in comp_v if comp_e[r] >= comp_v[r])
    nV, nE = len(V), len(E)
    cr = nE - nV + c
    giant = max(comp_v.values()) if comp_v else 0
    gfrac = giant / nV if nV else None
    dproof = (math.log(cr) / math.log(L) - 1) if (cr > 0 and L > 1) else None
    dratio = (math.log(cr / nE) / math.log(L)) if (cr > 0 and nE > 0 and L > 1) else None
    sub = (gfrac is not None and gfrac < 0.05 and cr <= 2 * cwc)
    return {
        "V": nV, "E": nE, "components": c, "components_with_cycle": cwc,
        "cycle_rank": cr, "giant_component_vertices": giant,
        "giant_fraction": gfrac, "E_over_V": (nE / nV if nV else None),
        "delta_proof": dproof, "delta_ratio": dratio,
        "cell_subcritical_condition": sub,
    }


def run(fx, prefix, scheme, j0, choices):
    p, a, b, q = fx["p"], fx["a"], fx["b"], fx["N"]
    G = tuple(fx["G"])
    B = ceil_pow_frac(p, 1, 5)
    B2 = ceil_pow_frac(p, 2, 5)
    A1 = ceil_pow_frac(q, 1, 2)
    A2 = ceil_pow_frac(q, 3, 5)
    pts = enumerate_lp_points(a, b, p, B2)
    fb_classes = sorted({P[0] for P in pts if P[0] < B})
    lp_classes = sorted({P[0] for P in pts if P[0] >= B})
    L = len(fb_classes)
    k = target_k(prefix, fx["bits"], fx["seed"], q, scheme)
    Q = mul(k, G, a, p)
    per_choice = {ch: {"A1": None, "A2": None} for ch in choices}
    acc = {ch: {"full": 0, "1LP": 0, "2LP": 0, "edges": [], "attempts_with_relation": 0,
                "R_is_O": 0} for ch in choices}
    for j in range(A2):
        jj = j + j0
        aj, bj = draws(f"{prefix}|attempt|{fx['bits']}|{fx['seed']}|{jj}", q, 2, scheme)
        R = add(mul(aj, G, a, p), mul(bj, Q, a, p), a, p)
        decs = [] if R is O else decompositions(R, pts, None, a, p, B2)
        for ch in choices:
            if R is O:
                acc[ch]["R_is_O"] += 1
            rels = relation_edges(decs, B, ch)
            if rels:
                acc[ch]["attempts_with_relation"] += 1
            for kind, e in rels:
                acc[ch][kind] += 1
                if e is not None:
                    acc[ch]["edges"].append(e)
        if j + 1 in (A1, A2):
            tag = "A1" if j + 1 == A1 else "A2"
            for ch in choices:
                st = {kk: acc[ch][kk] for kk in ("full", "1LP", "2LP", "attempts_with_relation", "R_is_O")}
                st["attempts"] = j + 1
                st["graphs"] = {}
                for vm, em in itertools.product(("touched", "all"), ("multi", "simple")):
                    st["graphs"][f"{vm}/{em}"] = graph_stats(acc[ch]["edges"], lp_classes, vm, em, L)
                per_choice[ch][tag] = st
    return {
        "params": {"p": p, "a": a, "b": b, "q": q, "G": list(G), "B": B, "B2": B2,
                   "L_liftable_classes_below_B": L, "ceil_q_1_5": ceil_pow_frac(q, 1, 5),
                   "A1": A1, "A2": A2, "n_points_x_lt_B2": len(pts),
                   "n_fb_classes": len(fb_classes), "n_lp_classes": len(lp_classes),
                   "target_k": k},
        "reading": {"prefix": prefix, "scheme": scheme, "attempt_index_base": j0},
        "results": per_choice,
    }


def sanity(fx):
    p, a, b, q = fx["p"], fx["a"], fx["b"], fx["N"]
    G = tuple(fx["G"])
    on = (G[1] ** 2 - (G[0] ** 3 + a * G[0] + b)) % p == 0
    hasse = abs(p + 1 - q) <= 2 * math.isqrt(p) + 2
    disc = (4 * a ** 3 + 27 * b ** 2) % p != 0
    return {"G_on_curve": on, "qG_is_O": mul(q, G, a, p) is O, "q_in_hasse_interval": hasse,
            "nonsingular": disc, "q_prime": all(q % d for d in range(2, math.isqrt(q) + 1)),
            "p_prime": all(p % d for d in range(2, math.isqrt(p) + 1)),
            "j_is_0_or_1728": a % p == 0 or b % p == 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--bits", type=int, default=16)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    fxs = json.load(open(args.fixtures))["fixtures"]
    fx = [f for f in fxs if f["bits"] == args.bits and f["seed"] == args.seed][0]
    out = {"fixture": fx, "sanity": sanity(fx), "readings": []}
    choices = ("first", "best", "all")
    for prefix in ("EXP-RELN-c5a377/v2", "EXP-RELN-c5a377/v1"):
        for scheme in ("mod_halves", "mod_divmod", "mod_ctr", "maskreject_ctr"):
            for j0 in (0, 1):
                out["readings"].append(run(fx, prefix, scheme, j0, choices))
    json.dump(out, open(args.out, "w"), indent=1)
    print(json.dumps(out["sanity"]), file=sys.stderr)


if __name__ == "__main__":
    main()
