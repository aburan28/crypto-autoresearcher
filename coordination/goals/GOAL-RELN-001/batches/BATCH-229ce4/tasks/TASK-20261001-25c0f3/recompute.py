"""Independent recomputation of RUN-RELN-a695fe (validator TASK-20261001-25c0f3, joint J1).

Written from specification.yaml + AMD-20260926-a7d25d (C-2..C-5) +
AMD-20260929-988139 (OQ-4 ruling, accepted literal readings) +
AMD-20260929-cc7226 (F-3, F-4). Imports nothing from the implementation.

For every fixture:
  * re-derive B, B2, A1, A2 with exact integer ceilings and check the fixture
    curve (non-singular, q prime, q*G = O);
  * re-derive the target k and every (a_j, b_j) from the SHA256 label rule;
  * recompute R_j = a_j G + b_j Q and re-scan ALL points with x < B2 (both
    signs) to decide every attempt's outcome, decomposition count, and the
    first relation in (x, y) scan order; diff against attempts.jsonl;
  * rebuild the LP multigraph (root + LP x-classes on an edge) per budget,
    components by BFS, cycle rank, components with a cycle, giant fraction,
    delta_proof / delta_ratio; diff against the stored graph block;
  * consistency-check each stored ER / rewire replicate and the known positive;
then apply the C-5 rules (with the accepted literal readings) to my own
numbers, and write recompute_out.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from collections import deque
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
RUN = REPO / "experiments/EXP-RELN-c5a377/runs/RUN-RELN-a695fe"
OUT = Path(sys.argv[2])
NS = "EXP-RELN-c5a377/v2"
FULL_SCAN = "--no-scan" not in sys.argv


# ---------------------------------------------------------------- labels
def H(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode()).digest(), "big")


def unif(label: str, n: int) -> int:
    lim = ((1 << 256) // n) * n
    v, r = H(label), 0
    while v >= lim:
        r += 1
        v = H(f"{label}|rej{r}")
    return v % n


# ---------------------------------------------------------------- integers
def iceil_root(x: int, k: int) -> int:
    """smallest integer r with r**k >= x"""
    r = max(1, int(round(x ** (1.0 / k))))
    while r ** k < x:
        r += 1
    while r > 1 and (r - 1) ** k >= x:
        r -= 1
    return r


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % sp == 0:
            return n == sp
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def sqrt_mod(r: int, p: int):
    if r == 0:
        return 0
    if pow(r, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(r, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, x = s, pow(z, q, p), pow(r, q, p), pow(r, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, x = i, b * b % p, t * b * b % p, x * b % p
    return x


# ---------------------------------------------------------------- curve
class Curve:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a, b

    def on(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - (x ** 3 + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def mul(self, k, P):
        R, A = None, P
        while k:
            if k & 1:
                R = self.add(R, A)
            A = self.add(A, A)
            k >>= 1
        return R


def sgn(y, p):
    return 1 if y <= (p - 1) // 2 else -1


# ---------------------------------------------------------------- graph
def graph_metrics(n, edges, L):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    comp = [-1] * n
    sizes = []
    for s in range(n):
        if comp[s] >= 0:
            continue
        cid = len(sizes)
        comp[s] = cid
        dq, cnt = deque([s]), 0
        while dq:
            u = dq.popleft()
            cnt += 1
            for w in adj[u]:
                if comp[w] < 0:
                    comp[w] = cid
                    dq.append(w)
        sizes.append(cnt)
    c = len(sizes)
    ecount = [0] * c
    for u, _ in edges:
        ecount[comp[u]] += 1
    cyc = sum(1 for i in range(c) if ecount[i] > sizes[i] - 1)
    m = len(edges)
    cr = m - n + c
    if L < 2 or cr <= 0:
        dp = dr = None
    else:
        dp = math.log(cr) / math.log(L) - 1
        dr = math.log(cr / m) / math.log(L)
    return {"V": n, "E": m, "components": c, "cycle_rank": cr, "components_with_cycle": cyc,
            "giant_component_fraction": (max(sizes) / n) if n else None,
            "delta_proof": dp, "delta_ratio": dr}


def build_graph(rels, B):
    lp = sorted({x for (k, x1, x2) in rels if k in ("lp1", "lp2") for x in (x1, x2) if x >= B})
    vid = {x: i + 1 for i, x in enumerate(lp)}
    edges = []
    for k, x1, x2 in rels:
        if k == "lp1":
            edges.append((vid[x1 if x1 >= B else x2], 0))
        elif k == "lp2":
            edges.append((vid[x1], vid[x2]))
    return len(lp) + 1, edges, lp


def close(a, b, tol=1e-12):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol


# ---------------------------------------------------------------- per cell
def do_cell(fid, frozen_fx, trial_budgets):
    cell = json.loads((RUN / "cells" / f"{fid}.json").read_text())
    att = [json.loads(l) for l in (RUN / "cells" / f"{fid}.attempts.jsonl").read_text().splitlines()]
    fx = cell["fixture"]
    rep = {"fixture_id": fid, "issues": []}
    iss = rep["issues"]
    if fx != frozen_fx:
        iss.append("cell fixture differs from frozen fixture JSON entry")
    p, q, a, b, G = fx["p"], fx["N"], fx["a"], fx["b"], tuple(fx["G"])
    bits, seed = fx["bits"], fx["seed"]
    E = Curve(p, a, b)
    curve_ok = {"nonsingular": (4 * a ** 3 + 27 * b * b) % p != 0, "p_prime": is_prime(p),
                "q_prime": is_prime(q), "G_on_curve": E.on(G), "qG_is_O": E.mul(q, G) is None,
                "q_gt_sqrt_p": q * q > p, "j_not_0_1728": a % p != 0 and b % p != 0}
    rep["curve_checks"] = curve_ok
    if not all(curve_ok.values()):
        iss.append(f"curve check failed: {curve_ok}")
    B, B2 = iceil_root(p, 5), iceil_root(p * p, 5)
    A1, A2 = iceil_root(q, 2), iceil_root(q ** 3, 5)
    rep["derived"] = {"B": B, "B2": B2, "A1": A1, "A2": A2}
    hdr = cell["header"]
    for k, v in (("B", B), ("B2", B2)):
        if hdr[k] != v:
            iss.append(f"header {k}={hdr[k]} != derived {v}")
    if cell["params"]["A1"] != A1 or cell["params"]["A2"] != A2:
        iss.append(f"cell budgets {cell['params']} != derived A1={A1} A2={A2}")
    if trial_budgets is not None and tuple(trial_budgets) != (A1, A2):
        iss.append(f"trial-plan budgets {trial_budgets} != derived {(A1, A2)}")
    if len(att) != A2:
        iss.append(f"attempts.jsonl has {len(att)} lines, expected A2={A2}")
    if [r["j"] for r in att] != list(range(len(att))):
        iss.append("attempt indices are not 0..A2-1 in order")
    # factor base / LP classes and scan set
    S, fb, lpc = [], [], []
    for x in range(B2):
        r = (x ** 3 + a * x + b) % p
        y = sqrt_mod(r, p)
        if y is None:
            continue
        if y == 0:
            S.append((x, 0))
        else:
            S.extend(sorted([(x, y), (x, p - y)]))
        (fb if x < B else lpc).append(x)
    L = len(fb)
    rep["derived"].update({"L": L, "n_lp_classes_liftable": len(lpc), "scan_size": len(S)})
    for k, v in (("L", L), ("n_lp_classes_liftable", len(lpc)), ("scan_size", len(S))):
        if hdr[k] != v:
            iss.append(f"header {k}={hdr[k]} != derived {v}")
    k_t = unif(f"{NS}|target|{bits}|{seed}", q)
    Q = E.mul(k_t, G)
    if hdr["target_k"] != k_t or tuple(hdr["Q"]) != Q:
        iss.append("target k / Q mismatch")
    # attempts
    nmis = {"coeff": 0, "outcome": 0, "rel": 0, "n_decomp": 0, "single": 0}
    Sneg = [E.neg(P) for P in S]
    for r in att:
        j = r["j"]
        lbl = f"{NS}|attempt|{bits}|{seed}|{j}"
        aj, bj = unif(lbl + "|a", q), unif(lbl + "|b", q)
        if (aj, bj) != (r["a"], r["b"]):
            nmis["coeff"] += 1
        if not FULL_SCAN:
            continue
        R = E.add(E.mul(aj, G), E.mul(bj, Q))
        if R is None:
            out, rel, nd, single = "R_is_O", None, 0, False
        else:
            seen, first, single = set(), None, False
            for P1, nP1 in zip(S, Sneg):
                T = E.add(R, nP1)
                if T is None:
                    single = True
                elif T[0] < B2:
                    key = (P1, T) if P1 <= T else (T, P1)
                    if key not in seen:
                        seen.add(key)
                        if first is None:
                            first = key
            nd = len(seen)
            if first:
                (x1, y1), (x2, y2) = first
                # verify the decomposition independently
                if E.add(first[0], first[1]) != R:
                    iss.append(f"attempt {j}: decomposition does not sum to R")
                rel = [x1, sgn(y1, p), x2, sgn(y2, p)]
                out = ("full", "lp1", "lp2")[(x1 >= B) + (x2 >= B)]
            else:
                rel = None
                out = ("single_point_fb" if R[0] < B else "single_point_lp") if single else "miss"
        if out != r["outcome"]:
            nmis["outcome"] += 1
        if rel != r["rel"]:
            nmis["rel"] += 1
        if nd != r["n_decomp"]:
            nmis["n_decomp"] += 1
        if single != r["single_point"]:
            nmis["single"] += 1
    rep["attempt_mismatches"] = nmis
    rep["attempts_rescanned"] = len(att) if FULL_SCAN else 0
    if any(nmis.values()):
        iss.append(f"attempt mismatches {nmis}")
    # per budget
    rep["budgets"] = {}
    for blk in cell["budgets"]:
        name, A = blk["budget"], blk["attempts"]
        if A != {"A1": A1, "A2": A2}[name]:
            iss.append(f"{name}: attempts {A} != derived")
        pre = att[:A]
        rels = [(r["outcome"], r["rel"][0], r["rel"][2]) for r in pre if r["outcome"] in ("full", "lp1", "lp2")]
        n, edges, lp = build_graph(rels, B)
        m = graph_metrics(n, edges, L)
        g = blk["graph"]
        diffs = {}
        for k in ("V", "E", "components", "cycle_rank", "components_with_cycle"):
            if g[k] != m[k]:
                diffs[k] = (g[k], m[k])
        for k in ("giant_component_fraction", "delta_proof", "delta_ratio"):
            if not close(g[k], m[k]):
                diffs[k] = (g[k], m[k])
        if g["L"] != L:
            diffs["L"] = (g["L"], L)
        if blk["lp_x"] != lp:
            diffs["lp_x"] = "differs"
        counts = {}
        for r in pre:
            counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
        for k, v in blk["outcome_counts"].items():
            if counts.get(k, 0) != v:
                diffs[f"outcome_counts.{k}"] = (v, counts.get(k, 0))
        if diffs:
            iss.append(f"{name}: graph diffs {diffs}")
        # null replicates: shape + internal consistency
        er = blk["null_er"]["replicates"]
        rw = blk["null_rewire"]["replicates"]
        nerr = []
        feasible_expected = n >= 2 and m["E"] <= n * (n - 1) // 2
        for kind, reps in (("er", er), ("rewire", rw)):
            if len(reps) != 32:
                nerr.append(f"{kind}: {len(reps)} replicates")
            for i, x in enumerate(reps):
                if x is None:
                    if kind == "rewire" or feasible_expected:
                        nerr.append(f"{kind}[{i}] null but feasible")
                    continue
                if x["V"] != m["V"] or x["E"] != m["E"]:
                    nerr.append(f"{kind}[{i}] V/E {x['V']},{x['E']} != {m['V']},{m['E']}")
                if x["cycle_rank"] != x["E"] - x["V"] + x["components"]:
                    nerr.append(f"{kind}[{i}] cycle rank identity")
                exp = None if (L < 2 or x["cycle_rank"] <= 0) else math.log(x["cycle_rank"]) / math.log(L) - 1
                if not close(exp, x["delta_proof"]):
                    nerr.append(f"{kind}[{i}] delta_proof {x['delta_proof']} != {exp}")
                if not (x["components_with_cycle"] <= x["cycle_rank"]):
                    nerr.append(f"{kind}[{i}] components_with_cycle > cycle_rank")
        if nerr:
            iss.append(f"{name}: null replicate issues {nerr[:5]} (+{max(0, len(nerr) - 5)})")
        # known positive
        kp = blk["known_positive"]
        vmin = None
        if L >= 2:
            vv = 2
            while True:
                cr = math.ceil(vv ** 1.5)
                if math.log(cr) / math.log(L) - 1 > 0.25:
                    vmin = vv
                    break
                vv += 1
        exp_status = None
        kperr = []
        if L < 2 or n < 2:
            exp_status = "not_exercised"
        elif n < vmin:
            exp_status = "not_exercised"
        else:
            pcr = math.ceil(n ** 1.5)
            exp_dp = math.log(pcr) / math.log(L) - 1
            exp_status = "pass" if exp_dp > 0.25 else "FAIL"
            km = kp.get("metrics") or {}
            if kp.get("planted_cycle_rank") != pcr or km.get("cycle_rank") != pcr:
                kperr.append("planted cycle rank")
            if not close(km.get("delta_proof"), exp_dp):
                kperr.append("planted delta_proof")
        if kp.get("status") != exp_status or kp.get("gate_min_V") != vmin:
            kperr.append(f"status {kp.get('status')} vs expected {exp_status}; gate_min_V {kp.get('gate_min_V')} vs {vmin}")
        if kperr:
            iss.append(f"{name}: known positive {kperr}")
        er_ok = [x["delta_proof"] for x in er if x is not None and x["delta_proof"] is not None]
        rep["budgets"][name] = {
            **m, "L": L, "attempts": A,
            "relations": {k: counts.get(k, 0) for k in ("full", "lp1", "lp2")},
            "er_feasible_replicates": sum(1 for x in er if x is not None),
            "er_delta_proof_defined": er_ok,
            "er_mean_delta_proof_defined": statistics.fmean(er_ok) if er_ok else None,
            "rewire_delta_proof_defined": [x["delta_proof"] for x in rw if x["delta_proof"] is not None],
            "known_positive_status": kp.get("status"), "known_positive_expected": exp_status,
            "gate_min_V": vmin, "known_false_status": (blk.get("known_false") or {}).get("status"),
            "fixture_subcritical": (m["giant_component_fraction"] < 0.05
                                    and m["cycle_rank"] <= 2 * m["components_with_cycle"]),
            "giant_lt_005": m["giant_component_fraction"] < 0.05,
            "cr_le_2cwc": m["cycle_rank"] <= 2 * m["components_with_cycle"],
        }
    rep["procedure_defects"] = cell["procedure_defects"]
    return rep


# ---------------------------------------------------------------- verdict
T2, T7 = 4.302652729911275, 2.364624251592785


def my_verdict(cells):
    sizes, budgets = (16, 20, 24), ("A1", "A2")
    tab = {}
    for r in cells:
        bits = int(r["fixture_id"][1:3])
        for bu, row in r["budgets"].items():
            tab.setdefault((bits, bu), []).append((int(r["fixture_id"].split("-s")[1]), row))
    per = {}
    ci_all, er_exc_any, er_undet = True, False, []
    for bits in sizes:
        for bu in budgets:
            rows = [row for _, row in sorted(tab[(bits, bu)], key=lambda t: t[0])]
            dp = [row["delta_proof"] for row in rows]
            if len(dp) == 3 and all(v is not None for v in dp):
                lci = statistics.fmean(dp) - T2 * statistics.stdev(dp) / math.sqrt(3)
            else:
                lci = None
            ci_ok = lci is not None and lci > 0.25
            ci_all &= ci_ok
            nfeas = sum(row["er_feasible_replicates"] for row in rows)
            # ER mean over feasible replicates; a feasible replicate whose delta is undefined
            # (cycle rank 0) has no delta value, so it is excluded from the mean.
            erv = [v for row in rows for v in row["er_delta_proof_defined"]]
            ermean = statistics.fmean(erv) if erv else None
            if nfeas == 0:
                exc = "undetermined"
                er_undet.append(f"{bits}-{bu}")
            else:
                exc = ermean is not None and ermean > 0.25
                er_exc_any |= exc
            kp_ok = all(row["known_positive_status"] == "pass" for row in rows)
            per[f"{bits}-{bu}"] = {
                "delta_proof": dp, "lower_95_ci": lci, "ci_gt_quarter": ci_ok,
                "er_mean_delta_proof": ermean, "er_n_defined": len(erv), "er_feasible": nfeas,
                "er_exceeds_quarter": exc, "kp_power_confirmed": kp_ok,
                "fixtures_subcritical": [row["fixture_subcritical"] for row in rows],
                "giant_fraction": [row["giant_component_fraction"] for row in rows],
                "cycle_rank": [row["cycle_rank"] for row in rows],
                "components_with_cycle": [row["components_with_cycle"] for row in rows],
                "V": [row["V"] for row in rows], "E": [row["E"] for row in rows]}
    trend, trend_all = {}, True
    for bu in budgets:
        xs, ys = [], []
        for bits in sizes:
            for _, row in tab[(bits, bu)]:
                xs.append(bits)
                ys.append(row["delta_proof"])
        if any(y is None for y in ys):
            trend[bu] = {"slope": None, "upper": None, "ok": False}
            trend_all = False
            continue
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs)
        sl = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        it = my - sl * mx
        se = math.sqrt(sum((y - it - sl * x) ** 2 for x, y in zip(xs, ys)) / (n - 2) / sxx)
        up = sl + T7 * se
        trend[bu] = {"slope": sl, "upper": up, "ok": up >= 0}
        trend_all &= up >= 0
    sup = ci_all and trend_all and not er_exc_any
    if sup and er_undet:
        sup = "undetermined"
    sub = all(row["fixture_subcritical"] for r in cells for row in r["budgets"].values())
    if sup == "undetermined":
        v = "inconclusive"
    elif sup is True and sub:
        v = "inconclusive"
    elif sup is True:
        v = "supercritical-enriched"
    elif sub:
        v = "certified-subcritical"
    else:
        v = "inconclusive"
    failing_sub = [f"{r['fixture_id']}-{bu}" for r in cells for bu, row in r["budgets"].items()
                   if not row["fixture_subcritical"]]
    return {"verdict": v, "supercritical_rule": sup, "subcritical_rule": sub,
            "ci_gt_quarter_all": ci_all, "trend_ok_both": trend_all, "er_exceeds_any": er_exc_any,
            "er_undetermined_cells": er_undet, "subcritical_failing_fixture_budgets": failing_sub,
            "per_cell": per, "trend": trend}


def main():
    frozen = json.loads((REPO / "experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json").read_text())
    frozen = {f"b{f['bits']}-s{f['seed']}": f for f in frozen["EXP-RELN-c5a377"]}
    tp = json.loads((REPO / "experiments/EXP-RELN-c5a377/implementation/trial-plan-v2.json").read_text())
    raw = json.loads((RUN / "raw-result.json").read_text())
    # raw-result cells must equal the per-cell JSON files
    raw_vs_cells = {}
    for c in raw["cells"]:
        f = json.loads((RUN / "cells" / f"{c['fixture_id']}.json").read_text())
        raw_vs_cells[c["fixture_id"]] = (f == c)
    results = []
    for fid in sorted(frozen):
        tb = None
        for t in tp["fixtures"]:
            if t.get("fixture_id") == fid:
                tb = (t["A1"], t["A2"])
                if (t["B"], t["B2"], t["L"]) != (None, None, None):
                    tp_bl = (t["B"], t["B2"], t["L"])
        ab = {c["budget"]: c["attempts"] for c in tp["cells"] if c["cell_id"].startswith(fid + "-")}
        if tb is None or ab != {"A1": tb[0], "A2": tb[1]}:
            print("WARNING trial-plan cells/fixtures budgets disagree", fid, tb, ab)
        print("cell", fid, flush=True)
        results.append(do_cell(fid, frozen[fid], tb))
    out = {"raw_result_cells_equal_cell_files": raw_vs_cells,
           "raw_cell_ids": sorted(c["fixture_id"] for c in raw["cells"]),
           "cells": results, "verdict": my_verdict(results)}
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"verdict": out["verdict"]["verdict"],
                      "sup": out["verdict"]["supercritical_rule"], "sub": out["verdict"]["subcritical_rule"],
                      "issues": {r["fixture_id"]: r["issues"] for r in results}}, indent=1))


if __name__ == "__main__":
    main()
