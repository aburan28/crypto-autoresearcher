"""Independent finite-field replay of the archived ECTD group census."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def primes():
    return [p for p in range(3, 65, 2) if all(p % d for d in range(2, math.isqrt(p) + 1))]


def rhs(p, a2, a4, a6, x):
    return (x * x * x + a2 * x * x + a4 * x + a6) % p


def points(p, a2, a4, a6):
    return {(x, y) for x in range(p) for y in range(p) if y * y % p == rhs(p, a2, a4, a6, x)}


def count(p, a2, a4, a6):
    return 1 + sum(1 if v == 0 else 2 if pow(v, (p - 1) // 2, p) == 1 else 0
                   for x in range(p) for v in [rhs(p, a2, a4, a6, x)])


def invariants(p, a2, a4, a6):
    pts = points(p, a2, a4, a6)
    n = len(pts) + 1
    def plus(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x, y = P
        z, w = Q
        if x == z and (y + w) % p == 0:
            return None
        slope = ((3*x*x + 2*a2*x + a4) * pow(2*y, -1, p) if P == Q else
                 (w-y) * pow((z-x) % p, -1, p)) % p
        u = (slope*slope - a2 - x - z) % p
        return u, (slope*(x-u) - y) % p
    orders = {}
    exponent = 1
    for P in sorted(pts):
        Q = P
        k = 1
        while Q is not None and k <= n:
            Q = plus(Q, P)
            k += 1
        assert Q is None and n % k == 0
        orders[P] = k
        exponent = math.lcm(exponent, k)
    assert n % exponent == 0
    second = n // exponent
    assert exponent % second == 0 and (p - 1) % second == 0
    return pts, n, [exponent, second], orders


def j_delta(p, a2, a4, a6):
    b2, b4, b6 = 4*a2, 2*a4, 4*a6
    b8 = 4*a2*a6 - a4*a4
    c4 = (b2*b2 - 24*b4) % p
    delta = (-b2*b2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6) % p
    return (c4**3 * pow(delta, -1, p)) % p if delta else None, delta


def quotient(p, a, r):
    A = 3*r % p
    B = (3*r*r + a) % p
    c2, c4 = -2*A % p, (A*A - 4*B) % p
    if p == 3:
        assert c2 == 0
        return A, B, c2, c4, 0, c4, 0
    shift = c2 * pow(3, -1, p) % p
    qa = (c4 - c2*c2*pow(3, -1, p)) % p
    qb = (-c2*c4*pow(3, -1, p) + 2*c2**3*pow(27, -1, p)) % p
    return A, B, c2, c4, shift, qa, qb


def square_witness(n):
    return next((q for q in range(2, math.isqrt(n)+1)
                 if n % (q*q) == 0 and all(q % d for d in range(2, math.isqrt(q)+1))), None)


def replay_selection(recorded):
    i = 0
    for p in primes():
        for a in range(p):
            for b in range(p):
                sj, sd = j_delta(p, 0, a, b)
                row = {"p": p, "a": a, "b": b, "source_delta": sd,
                       "source_j": sj, "roots": [], "root_trials": []}
                if sd == 0:
                    row["rejection"] = "singular_source"
                else:
                    n = count(p, 0, a, b)
                    t = p + 1 - n
                    row.update({"source_order": n, "source_trace": t,
                                "source_ordinary": t % p != 0})
                    if t % p == 0:
                        row["rejection"] = "supersingular_source"
                    else:
                        roots = [r for r in range(p) if rhs(p, 0, a, b, r) == 0]
                        row["roots"] = roots
                        if not roots:
                            row["rejection"] = "no_rational_two_torsion"
                        else:
                            for r in roots:
                                A, B, c2, c4, shift, qa, qb = quotient(p, a, r)
                                cj, cd = j_delta(p, 0, qa, qb)
                                attempt = {"r": r, "codomain_delta": cd, "codomain_j": cj}
                                if cd == 0:
                                    attempt["rejection"] = "singular_codomain"
                                else:
                                    m = count(p, 0, qa, qb)
                                    v = p + 1 - m
                                    attempt.update({"codomain_order": m, "codomain_trace": v,
                                                    "codomain_ordinary": v % p != 0})
                                    if m != n or v != t:
                                        attempt["rejection"] = "trace_or_order_mismatch"
                                    elif v % p == 0:
                                        attempt["rejection"] = "supersingular_codomain"
                                    elif cj == sj:
                                        attempt["rejection"] = "same_j"
                                    elif square_witness(n) is None:
                                        attempt["rejection"] = "squarefree_order"
                                    else:
                                        attempt["accepted"] = True
                                row["root_trials"].append(attempt)
                                if attempt.get("accepted"):
                                    assert i < len(recorded) and row == recorded[i]
                                    assert i + 1 == len(recorded)
                                    return {"p": p, "a": a, "b": b, "r": r,
                                            "quotient": {"source_shift": r, "A": A, "B": B,
                                                         "generalized_codomain": [c2, c4, 0],
                                                         "short_codomain": [qa, qb],
                                                         "codomain_shift": shift,
                                                         "degree": 2, "kernel": [["O"], [r, 0]],
                                                         "map": "X=x-r; u=X+A+B/X; v=y*(1-B/X^2); w=u+c2/3 (p>3); O,T->O"}}
                            row["rejection"] = "all_roots_rejected"
                assert i < len(recorded) and row == recorded[i]
                i += 1
    assert i == len(recorded)
    return None


def check(run_dir: Path):
    raw = json.loads((run_dir / "raw-result.json").read_text())
    assert raw["schema"] == "crypto.autoresearch.ectd_group_invariants.v1"
    assert raw["experiment_id"] == "EXP-ECTD-07b200"
    assert raw["run_id"] == "RUN-ECTD-e5714e"
    selected = replay_selection(raw["selection_trace"])
    assert raw["selected"] == selected
    if selected is None:
        assert raw["valid"] is True and raw["reading_row"] == "negative_no_eligible_edge"
        return
    p, a, b, r = (selected[k] for k in ("p", "a", "b", "r"))
    q = selected["quotient"]
    A, B, c2, c4, shift, qa, qb = quotient(p, a, r)
    assert B != 0
    assert q["short_codomain"] == [qa, qb]
    assert j_delta(p, c2, c4, 0)[0] == j_delta(p, 0, qa, qb)[0]
    src_pts, n, src_pair, src_orders = invariants(p, 0, a, b)
    dst_pts, m, dst_pair, dst_orders = invariants(p, 0, qa, qb)
    scaled_a, scaled_b = 16*a % p, 64*b % p
    scaled_pts, scaled_n, scaled_pair, scaled_orders = invariants(p, 0, scaled_a, scaled_b)
    assert n == m == scaled_n == count(p, 0, a, b) == count(p, 0, qa, qb)
    assert abs(p+1-n) <= 2*math.isqrt(p)+1
    assert (p+1-n) % p != 0 and square_witness(n) == raw["prime_square_witness"]
    assert j_delta(p, 0, a, b)[0] != j_delta(p, 0, qa, qb)[0]
    assert src_pair == raw["source"]["factors"]
    assert dst_pair == raw["codomain"]["factors"]
    assert scaled_pair == raw["scaled_source"]["factors"] == src_pair
    for label, actual in [("source", src_orders), ("codomain", dst_orders), ("scaled_source", scaled_orders)]:
        recorded = {tuple(z["point"]): z["order"] for z in raw[label]["point_orders"]}
        assert actual == recorded
    assert {(4*x % p, 8*y % p) for x, y in src_pts} == scaled_pts
    image = {None}
    kernel = set()
    for x, y in src_pts:
        X = (x-r) % p
        if X == 0:
            kernel.add((x,y))
        else:
            inv = pow(X, -1, p)
            mapped = ((X+A+B*inv+shift) % p, y*(1-B*inv*inv) % p)
            assert mapped in dst_pts
            image.add(mapped)
    assert kernel == {(r,0)} and len(image)*2 == n
    assert raw["map_control"]["pass"] is True
    assert raw["map_control"]["image_size"] == len(image)
    assert all(raw["controls"].values()) and raw["valid"] is True
    differences = sum(x != y for x,y in zip(src_pair, dst_pair))
    assert raw["difference_coordinates"] == differences
    assert raw["reading_row"] == ("positive" if differences else "negative_same_factors")


if __name__ == "__main__":
    check(Path(sys.argv[1]))
