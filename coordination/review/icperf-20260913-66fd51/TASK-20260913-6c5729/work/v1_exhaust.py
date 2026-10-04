"""V1, beyond the attack plan: enumerate the ENTIRE solution set of every
shipped instance by evaluating f3 (find_points.sage line 40) at every triple
(x1,x2,x3) in V^3, and classify each root by whether its x-coordinates lie on
E or on the quadratic twist.

This independently certifies every SAT and every UNSAT answer the run records
on the 60 shipped instances, without running a solver: |V|^3 is 32768 (l=5) or
262144 (l=6), and f3 is symmetric so only sorted triples are enumerated.

Uses a discrete-log table for GF(2^n) (x = a is primitive for the Conway
moduli the generator emits; primitivity is asserted, not assumed).
"""
from __future__ import annotations

import glob
import json
import os
import time

from valgf import GF2n, BinaryCurve, INF, f3_summation, parse_info

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
OUT = os.path.dirname(os.path.abspath(__file__))


class LogField:
    """GF(2^n) with log/antilog tables, built on top of the validator's own
    GF2n so the tables are derived from the same reduction."""

    def __init__(self, F: GF2n):
        self.F = F
        self.n = F.n
        self.q = 1 << F.n
        self.order = self.q - 1
        exp = [0] * (2 * self.order)
        log = [None] * self.q
        v = 1
        for i in range(self.order):
            exp[i] = v
            assert log[v] is None, "a = x is not primitive for this modulus"
            log[v] = i
            v = F.mul(v, 2)
        assert v == 1
        for i in range(self.order, 2 * self.order):
            exp[i] = exp[i - self.order]
        self.exp = exp
        self.log = log

    def mul(self, a, b):
        if a == 0 or b == 0:
            return 0
        return self.exp[self.log[a] + self.log[b]]


def f3_fast(L, xr_pows, X1, X2, X3):
    m = L.mul
    xr, xr2, xr3, xr4 = xr_pows
    p12 = m(X1, X2)
    e1 = X1 ^ X2 ^ X3
    e2 = p12 ^ m(X2, X3) ^ m(X1, X3)
    e3 = m(p12, X3)
    A = m(e1, e1)          # e1^2
    B = m(e2, e2)          # e2^2
    C = e3
    A2 = m(A, A)           # e1^4
    B2 = m(B, B)           # e2^4
    C2 = m(C, C)
    C3 = m(C2, C)
    C4 = m(C2, C2)
    r = xr4
    r ^= A2
    r ^= C4
    r ^= m(B2, xr4)
    r ^= m(C3, xr)
    r ^= m(m(C, B), xr3)
    r ^= m(m(C, A), xr)
    r ^= m(C, xr3)
    r ^= m(m(A, C2), xr2)
    r ^= m(C2, xr4)
    r ^= C2
    r ^= m(B, xr2)
    return r


def main():
    t0 = time.time()
    infos = sorted(glob.glob(os.path.join(BENCH, "INFO*.dimacs")))
    fields = {}
    results = []

    # recorded solver statuses per instance
    status = {}
    for ln in open(os.path.join(RUN, "results.jsonl")):
        r = json.loads(ln)
        if r.get("engine") == "wdsat" and r.get("config") == "default" \
                and r.get("phase") == "A" and "null_object" not in str(r.get("config")):
            if r.get("instance") and not r.get("null_object"):
                status.setdefault(r["instance"], {})["wdsat_default"] = r["status"]
        if r.get("engine") == "cryptominisat5" and r.get("config") == "cnf_xor":
            status.setdefault(r["instance"], {})["cms_cnf_xor"] = r["status"]

    for path in infos:
        info = parse_info(path)
        n, l = info["n"], info["l"]
        name = os.path.basename(path)[4:-7]
        key = (n, info["modulus_bits"])
        if key not in fields:
            F = GF2n(n, info["modulus_bits"])
            fields[key] = (F, BinaryCurve(F, 1, 1), BinaryCurve(F, 0, 1), LogField(F))
        F, E, TW, L = fields[key]

        xr = F.from_bits_lsb_first(info["xr_bits"])
        xr2 = L.mul(xr, xr)
        xr3 = L.mul(xr2, xr)
        xr4 = L.mul(xr2, xr2)
        xr_pows = (xr, xr2, xr3, xr4)

        onE = [bool(E.is_x_coord(v)) for v in range(1 << l)]
        onTW = [bool(TW.is_x_coord(v)) for v in range(1 << l)]

        roots = []
        V = 1 << l
        for a in range(V):
            for b in range(a, V):
                for c in range(b, V):
                    if f3_fast(L, xr_pows, a, b, c) == 0:
                        roots.append((a, b, c))

        classified = []
        for (a, b, c) in roots:
            cls = {
                "x": [hex(a), hex(b), hex(c)],
                "all_on_E": bool(onE[a] and onE[b] and onE[c]),
                "all_on_twist": bool(onTW[a] and onTW[b] and onTW[c]),
                "on_E_flags": [onE[a], onE[b], onE[c]],
            }
            if cls["all_on_E"]:
                cls["decomposes_on_E"] = decomposes(E, [a, b, c], xr)
            if cls["all_on_twist"]:
                cls["decomposes_on_twist"] = decomposes(TW, [a, b, c], xr)
            classified.append(cls)

        # sanity: f3 must really be the shipped system -- the certificate of an
        # S instance must appear among the roots
        cert_ok = None
        if info["label"] == "S":
            xs = [F.from_bits_lsb_first(p) for p in info["cert_raw"].split("-")]
            cert_ok = tuple(sorted(xs)) in set(tuple(sorted(r)) for r in roots)

        results.append({
            "instance": name, "n": n, "l": l, "label": info["label"],
            "xr_hex": hex(xr),
            "xr_on_E": bool(E.is_x_coord(xr)),
            "xr_on_twist": bool(TW.is_x_coord(xr)),
            "n_sorted_triples_scanned": V * (V + 1) * (V + 2) // 6,
            "n_roots_sorted": len(roots),
            "roots": classified,
            "shipped_certificate_is_a_root": cert_ok,
            "recorded_status": status.get(name, {}),
        })
        print(f"{name:14s} l={l} roots={len(roots):3d} "
              f"xr_onE={results[-1]['xr_on_E']} xr_onTw={results[-1]['xr_on_twist']} "
              f"cert_root={cert_ok} status={status.get(name, {})} "
              f"[{time.time()-t0:.1f}s]", flush=True)

    with open(os.path.join(OUT, "v1_exhaust.json"), "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)

    # cross-check against recorded statuses
    print("\n== cross-check: exhaustive root count vs recorded solver status ==")
    bad = 0
    for r in results:
        pred = "SAT" if r["n_roots_sorted"] > 0 else "UNSAT"
        for eng, st in r["recorded_status"].items():
            if st in ("SAT", "UNSAT") and st != pred:
                print("  MISMATCH", r["instance"], eng, st, "exhaustive says", pred)
                bad += 1
    print(f"  mismatches: {bad}")
    nS = sum(1 for r in results if r["label"] == "S")
    print(f"  S instances with the shipped certificate among the roots: "
          f"{sum(1 for r in results if r['shipped_certificate_is_a_root'])}/{nS}")
    sat_u = [r for r in results if r["label"] == "U" and r["n_roots_sorted"] > 0]
    print(f"  U instances with at least one root: {len(sat_u)}/30 -> "
          f"{[r['instance'] for r in sat_u]}")
    print(f"  total elapsed {time.time()-t0:.1f}s")


def decomposes(curve, xs, xr):
    pts = [curve.points_with_x(v) for v in xs]
    if any(len(p) == 0 for p in pts):
        return {"matches": 0}
    hits = []
    for i, P1 in enumerate(pts[0]):
        for j, P2 in enumerate(pts[1]):
            for k, P3 in enumerate(pts[2]):
                S = curve.add(curve.add(P1, P2), P3)
                if S is not INF and S[0] == xr:
                    hits.append((i, j, k))
    return {"matches": len(hits), "combinations_tried": 8}


if __name__ == "__main__":
    main()
