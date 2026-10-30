"""J3b item (3) follow-up: the short group relation behind each degenerate main-census job.

Reviewer-written affine group law and square root; the producer's seeding convention is reproduced from
specification.yaml log_gap_builder and the vendored random_point (read, not imported): the stream is
random.Random(int(sha256('EXP-PFDR-bb0d26|gap|main|<cell>|<c>'), big-endian)); each base point draws
x = randrange(p) until f(x) is a square, takes the smaller root, and negates it when random() >= 0.5.
Curve parameters (p, a, b, N) are read from the recorded main-block job; no curve is generated, no seed block is
touched, no discrete logarithm and no coincidence count is computed. For every degenerate job (and the first
four ok jobs of the same cell as controls) the script (1) rebuilds the half-box enumeration and compares T,
enumerated, duplicate_skips, infinity_skips, first and last with the record, and (2) lists every relation
v in [-20, 20]^3 (first nonzero entry positive) with v . P = O.
Writes outputs/degenerate-relations.json.
"""
import hashlib
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

EXP = "EXP-PFDR-bb0d26"


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


class E:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a, b

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % p == 0:
                return None
            lam = (3 * P[0] * P[0] + self.a) * pow(2 * P[1], -1, p) % p
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
        x3 = (lam * lam - P[0] - Q[0]) % p
        return (x3, (lam * (P[0] - x3) - P[1]) % p)

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def random_point(self, rng):
        while True:
            x = rng.randrange(self.p)
            f = (x * x * x + self.a * x + self.b) % self.p
            y = sqrt_mod(f, self.p)
            if y is not None:
                P = (x, min(y, self.p - y))
                return P if rng.random() < 0.5 else self.neg(P)


def rng_for(*labels):
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


def half_box(r, T):
    for v in itertools.product(range(-T, T + 1), repeat=r):
        for e in v:
            if e != 0:
                if e > 0:
                    yield v
                break


def rebuild_meta(Ec, pts, r, n, T):
    mult = []
    for P in pts:
        tab = {0: None}
        Q = None
        for k in range(1, T + 1):
            Q = Ec.add(Q, P)
            tab[k], tab[-k] = Q, Ec.neg(Q)
        mult.append(tab)
    seen, labels = set(), 0
    enum = dup = inf = 0
    first = last = None
    for v in half_box(r, T):
        enum += 1
        Q = None
        for tab, ci in zip(mult, v):
            Q = Ec.add(Q, tab[ci])
        if Q is None:
            inf += 1
            continue
        if Q[0] in seen:
            dup += 1
            continue
        seen.add(Q[0])
        labels += 1
        first = first or list(v)
        last = list(v)
        if labels == n:
            break
    return {"T": T, "enumerated": enum, "duplicate_skips": dup, "infinity_skips": inf, "first": first, "last": last}


def relations(Ec, pts, B=20):
    mults = []
    for P in pts:
        tab = {0: None}
        Q = None
        for k in range(1, B + 1):
            Q = Ec.add(Q, P)
            tab[k], tab[-k] = Q, Ec.neg(Q)
        mults.append(tab)
    last = {}
    for k, Q in mults[-1].items():
        last.setdefault(Q, []).append(k)
    out = []
    for head in itertools.product(range(-B, B + 1), repeat=len(pts) - 1):
        Q = None
        for tab, ci in zip(mults[:-1], head):
            Q = Ec.add(Q, tab[ci])
        for k in last.get(Ec.neg(Q), []):
            v = list(head) + [k]
            nz = next((e for e in v if e != 0), 0)
            if nz > 0:
                out.append(v)
    return out


def main():
    recs = C.load_jobs()
    target = [r for r in recs if r["status"] == "degenerate"]
    cells = {r["cell"] for r in target}
    controls = []
    for cid in sorted(cells):
        oks = sorted([r for r in recs if r["cell"] == cid and r["status"] == "ok"], key=lambda r: r["c"])[:4]
        controls += oks
    rows = []
    for rec in target + controls:
        Ec = E(rec["p"], rec["a"], rec["b_coef"])
        rng = rng_for("gap", rec["block"], rec["cell"], rec["c"])
        pts = [Ec.random_point(rng) for _ in range(rec["r"])]
        meta = rebuild_meta(Ec, pts, rec["r"], rec["n"], rec["gap_meta"]["T"])
        rel = relations(Ec, pts, 20)
        rel_sorted = sorted(rel, key=lambda v: (max(map(abs, v)), sum(map(abs, v))))
        rows.append({"cell": rec["cell"], "c": rec["c"], "status": rec["status"], "N": rec["N"],
                     "recorded_gap_meta": rec["gap_meta"], "rebuilt_gap_meta": meta,
                     "gap_meta_match": all(meta[k] == rec["gap_meta"][k] for k in meta),
                     "relations_supnorm_le_20": rel_sorted[:12], "relation_count": len(rel),
                     "shortest_relation_supnorm": max(map(abs, rel_sorted[0])) if rel_sorted else None})
        print(rows[-1]["cell"], rows[-1]["c"], rows[-1]["status"], rows[-1]["gap_meta_match"], rows[-1]["relation_count"], rel_sorted[:4])
    C.write_json("degenerate-relations.json", {
        "task": "TASK-20261029-11526b", "joint": "J3b item (3)",
        "inputs": [C.rel(C.JOBS)], "method": __doc__.strip(), "jobs": rows}, sig=8)


if __name__ == "__main__":
    main()
