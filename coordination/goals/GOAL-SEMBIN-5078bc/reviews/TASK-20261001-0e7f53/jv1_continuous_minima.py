"""JV-1: exact real-d minima of the v2 header-block TOTAL, per (degree, model,
budget, m), in domain (CALLS >= 0, 1 <= d <= n), and the v2 grid excess.

On each interval where s is constant, TOTAL(d) = log2(2^(a1 + b1 d) + 2^(b2 d)
+ 2^(2d)) is a log-sum-exp of affine functions, hence convex, so a golden-section
search per piece is exact. MITM_CAPPED pieces: s = k on (log2B/(k+1), log2B/k],
s = S for d <= log2B/S, s = 0 for d > log2B. The left end of a piece is open;
its infimum there is reported as the limit (attainable to any precision).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm  # noqa: E402
from jv1_diff_primary import COMBOS, MS, PRIMARY, grid, load_raw, log2B  # noqa: E402


def total_fixed_s(n, m, d, model, s):
    return hm.cell(n, m, d, model, None, s=s)["TOTAL"]


def golden(f, a, b, it=200):
    g = (math.sqrt(5) - 1) / 2
    c, e = b - g * (b - a), a + g * (b - a)
    fc, fe = f(c), f(e)
    for _ in range(it):
        if fc < fe:
            b, e, fe = e, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, e, fe
            e = a + g * (b - a)
            fe = f(e)
    cands = [(f(a), a), (f(b), b), (fc, c), (fe, e)]
    return min(cands)


def pieces(model, m, lb, lo, hi):
    S = m // 2
    if model in ("FREE", "ENUM"):
        return [(0, lo, hi)]
    if model == "MITM" or lb is None:
        return [(S, lo, hi)]
    out = []
    # s = S on d <= lb/S
    edges = [(S, -math.inf, lb / S)]
    for k in range(S - 1, 0, -1):
        edges.append((k, lb / (k + 1), lb / k))
    edges.append((0, lb, math.inf))
    for s, a, b in edges:
        a2, b2 = max(a, lo), min(b, hi)
        if a2 <= b2:
            out.append((s, a2, b2))
    return out


def cont_min(n, m, model, b):
    lb = log2B(b)
    N, L = hm.N_of(n), hm.L_of(m)
    hi = min(float(n), (N + L) / (m - 1))
    lo = 1.0
    if hi < lo:
        return None
    best = None
    for s, a, bb in pieces(model, m, lb, lo, hi):
        v, d = golden(lambda x: total_fixed_s(n, m, x, model, s), a, bb)
        if best is None or v < best[0]:
            best = (v, d, s)
    return best


def main():
    raw = load_raw()
    rows = []
    for n in hm.DEGREES:
        for model, b in COMBOS:
            if model not in PRIMARY:
                continue
            for m in MS:
                c = cont_min(n, m, model, b)
                g = None
                for d in grid(float(n)):
                    x = hm.cell(n, m, d, model, log2B(b))
                    if x["out_of_domain"]:
                        continue
                    if g is None or x["TOTAL"] < g[0]:
                        g = (x["TOTAL"], d, x["s"])
                if c and g:
                    rows.append(dict(n=n, model=model, B=b, m=m, cont=c[0], cont_d=c[1], cont_s=c[2],
                                     grid=g[0], grid_d=g[1], grid_s=g[2], excess=g[0] - c[0]))
    per_nb = {}
    for r in rows:
        if r["model"] != "MITM_CAPPED":
            continue
        k = (r["n"], r["B"])
        cur = per_nb.get(k)
        if cur is None:
            per_nb[k] = dict(cont=r["cont"], grid=r["grid"], cont_arg=(r["m"], r["cont_s"], r["cont_d"]))
        else:
            if r["cont"] < cur["cont"]:
                cur["cont"], cur["cont_arg"] = r["cont"], (r["m"], r["cont_s"], r["cont_d"])
            cur["grid"] = min(cur["grid"], r["grid"])
    raw_pb = {}
    for n in hm.DEGREES:
        for b, v in raw["per_degree_minimum"][str(n)]["n"]["per_budget_min"].items():
            raw_pb[(n, b)] = v["TOTAL"]
    pb_out = {}
    for (n, b), v in per_nb.items():
        pb_out[f"{n}|{b}"] = dict(grid_min=v["grid"], raw_per_budget_min=raw_pb[(n, b)],
                                  grid_vs_raw=v["grid"] - raw_pb[(n, b)], continuous_min=v["cont"],
                                  continuous_argmin_m_s_d=v["cont_arg"], excess_grid_over_continuous=v["grid"] - v["cont"],
                                  continuous_margin_vs_VOW=v["cont"] - hm.vow(n))
    worst_pb = max(pb_out.items(), key=lambda kv: kv[1]["excess_grid_over_continuous"])
    by_model = {}
    for r in rows:
        bm = by_model.setdefault(r["model"], dict(rows=0, max_excess=0.0, over_0_1=0))
        bm["rows"] += 1
        bm["max_excess"] = max(bm["max_excess"], r["excess"])
        bm["over_0_1"] += r["excess"] > 0.1
    out = dict(rows=len(rows), by_model=by_model,
               max_row_excess=max(rows, key=lambda r: r["excess"]),
               per_budget=pb_out, worst_per_budget_excess=worst_pb,
               min_continuous_margin_vs_VOW_all_primary_rows=min(r["cont"] - hm.vow(r["n"]) for r in rows),
               min_continuous_margin_vs_PUB_131=min(r["cont"] - hm.PUB_131 for r in rows if r["n"] == 131))
    (HERE / "jv1_continuous_minima_output.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != "per_budget"}, indent=1, default=str))
    for k in ("97|60", "97|80", "131|40", "131|80", "131|unlimited", "239|unlimited", "571|unlimited"):
        print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in pb_out[k].items()})


if __name__ == "__main__":
    main()
