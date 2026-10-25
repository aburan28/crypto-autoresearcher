"""Collects the numbers the red-team report cites (TASK-20261023-7b5dc6) from the rt_*_output.json files.

Adds: Spearman rank correlations of N_E(1e5) with log|disc| and with the rank lower bound across the seven
rank >= 7 curves (run curves + Elkies-Watkins rows); local growth exponents 2 dlog N / dlog log H between
grid points; the cap analysis of the success clause S4 (H_half at p >= 1000 needs n >= N_p / 2).
Output rt_summary_output.json.
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, f)))

cnt = J("rt_count_output.json")["curves"]
ew = J("rt_ew_output.json")["rows"]
ew6 = {r["label"]: r["counts"] for r in J("rt_ew_1e6_output.json")["rows"]}
rows = []
for lab, r in (("GZ-1977", 8), ("BK-1977", 9)):
    key = [k for k in cnt if k.startswith("grunewald" if lab.startswith("GZ") else "brumer")][0]
    c = {int(k): v for k, v in cnt[key]["counts_mine"].items()}
    rows.append({"label": lab, "rank_lb": r, "abs_disc": abs(cnt[key]["discriminant_mine"]), "N1e5": c[100000], "N3e5": c[300000]})
for e in ew:
    c = {int(k): v for k, v in e["counts"].items()}
    row = {"label": e["label"], "rank_lb": e["rank_lower_bound_source"], "abs_disc": e["abs_disc"], "N1e5": c[100000], "N3e5": c[300000]}
    if e["label"] in ew6:
        row["N1e6"] = ew6[e["label"]]["1000000"]
    rows.append(row)


def ranks(v):
    s = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
            j += 1
        for k in range(i, j + 1):
            r[s[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den


N = [r["N1e5"] for r in rows]
out = {"seven_curves": rows,
       "spearman_N1e5_vs_log_abs_disc": spearman(N, [math.log(r["abs_disc"]) for r in rows]),
       "spearman_N1e5_vs_rank_lb": spearman(N, [r["rank_lb"] for r in rows]),
       "spearman_N3e5_vs_log_abs_disc": spearman([r["N3e5"] for r in rows], [math.log(r["abs_disc"]) for r in rows]),
       "spearman_N3e5_vs_rank_lb": spearman([r["N3e5"] for r in rows], [r["rank_lb"] for r in rows])}
loc = {}
for r in rows:
    e = {"1e5->3e5": 2 * math.log(r["N3e5"] / r["N1e5"]) / math.log(math.log(3e5) / math.log(1e5))}
    if "N1e6" in r:
        e["3e5->1e6"] = 2 * math.log(r["N1e6"] / r["N3e5"]) / math.log(math.log(1e6) / math.log(3e5))
    loc[r["label"]] = e
out["local_growth_exponent_2dlogN_dloglogH"] = loc
# S4 cap: H_half(p) needs distinct >= N_p/2, and distinct <= n
raw = json.load(open(os.path.join(HERE, "..", "..", "runs", "RUN-CZLIFT-b1dce4", "raw-result.json")))["raw"]["curves"]
s4 = {}
for cv in raw:
    if cv["label"].startswith("3826"):
        continue
    n = cv["counts"]["300000"]
    nps = sorted({(c["p"], c["N_p"]) for c in cv["coverage"]})
    s4[cv["label"]] = {"n_at_3e5": n, "primes_ge_1000_where_H_half_is_possible": [p for p, Np in nps if p >= 1000 and n >= Np / 2]}
out["S4_cap"] = s4
tr = J("rt_null_translate_output.json")["rows"]
out["translation_mutation_N1e5"] = [{"curve": t["family"], "t": t["t"], "N1e5": t["counts"]["100000"], "N3e5": t["counts"]["300000"]} for t in tr]
nl = J("rt_null_null_output.json")["rows"]
fam = {}
for r in nl:
    fam.setdefault(r["family"], []).append(r["counts"]["300000"])
out["coefficient_matched_null_N3e5"] = {k: {"n_curves": len(v), "values": v, "max": max(v)} for k, v in fam.items()}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "rt_summary_output.json"), "w"), indent=1)
