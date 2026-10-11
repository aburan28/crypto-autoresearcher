#!/usr/bin/env python3
"""summarize.py -- PILOT (m3closure): results/*.jsonl -> data.csv + tables.md
(tables are pasted into summary.md by hand together with the narrative)."""
import csv
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
INST = HERE / "instances"

FIELDS = ["cell", "id", "family", "n", "k", "N", "vtype", "z", "nsol", "sat", "kind", "D", "status",
          "contains_one", "rank", "ncols", "codim", "rows", "basis_nnz", "standard_monomials",
          "n_iterations", "wall_s", "outer_wall_s", "peak_rss_mb", "mem_cap_gb", "elimination", "m4ri_library",
          "elimination_faults", "dropped_terms_above_D", "ech_calls", "ech_evalcheck_mismatch",
          "evalcheck_flagged_lines", "eval_rows_not_vanishing_total", "n_witnesses_checked", "dims_by_lmdeg"]


import re


def cellkey(c):
    m = re.match(r'n(\d+)-', c)
    return int(m.group(1)) if m else 0


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def cp95(x, n):
    if n == 0:
        return (float("nan"), float("nan"))
    def bis(f, lo=0.0, hi=1.0):
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    lo = 0.0 if x == 0 else bis(lambda p: 1 - binom_cdf(x - 1, n, p) >= 0.025)
    hi = 1.0 if x == n else bis(lambda p: binom_cdf(x, n, p) <= 0.025)
    return lo, hi


def load():
    rows = []
    for f in sorted(RES.glob("*.jsonl")):
        cell = f.stem
        for line in open(f):
            r = json.loads(line)
            r["cell"] = cell
            rows.append(r)
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            o = {k: r.get(k) for k in FIELDS}
            o["sat"] = int(r["nsol"] > 0)
            if r.get("rank") is not None and r.get("ncols") and r.get("status") == "completed":
                o["codim"] = r["ncols"] - r["rank"]
            o["n_iterations"] = len(r["iterations"]) if r.get("iterations") else None
            ev = r.get("eval_rows_not_vanishing")
            o["eval_rows_not_vanishing_total"] = sum(ev) if ev is not None else None
            o["n_witnesses_checked"] = len(ev) if ev is not None else None
            o["dims_by_lmdeg"] = json.dumps(r.get("dims_by_lmdeg")) if r.get("dims_by_lmdeg") is not None else None
            w.writerow(o)


def fmt_frac(x, n):
    if n == 0:
        return "-"
    lo, hi = cp95(x, n)
    return f"{x}/{n} [{lo:.2f},{hi:.2f}]"


def main():
    rows = load()
    write_csv(rows, HERE / "data.csv")
    out = []
    P = out.append
    by = defaultdict(list)
    for r in rows:
        by[(r["cell"], r["family"])].append(r)
    # ---- labelling census
    P("### Target census (enumeration labels, all labelled targets incl. not run)\n")
    P("| cell | q | targets | unique | UNSAT | SAT | enum agree (curve vs Boolean) | eval at zeros ok |")
    P("|---|---|---|---|---|---|---|---|")
    for f in sorted(INST.glob("*.json")):
        if f.stem.endswith("-nulls"):
            continue
        c = json.load(open(f))
        I = c["instances"]
        uq = [x for x in I if not x.get("dup_target")]
        P(f"| {f.stem} | {c.get('q', '-')} | {len(I)} | {len(uq)} | {sum(x['nsol']==0 for x in uq)} | "
          f"{sum(x['nsol']>0 for x in uq)} | {sum(x.get('enum_agree', True) for x in I)}/{len(I)} | "
          f"{sum(x.get('eval_ok', True) for x in I)}/{len(I)} |")
    # ---- refutation table
    P("\n### Refutation of UNSAT instances, false refutation of SAT instances (libclosure / M4RI unless 'my')\n")
    P("| cell | family | task | UNSAT refuted [CP95] | SAT refuted (must be 0) | censored/errors |")
    P("|---|---|---|---|---|---|")
    for (cell, fam), rs in sorted(by.items(), key=lambda t: (cellkey(t[0][0]), t[0])):
        tasks = sorted({(r["kind"], r["D"]) for r in rs}, key=lambda t: (t[0].startswith("my"), t[0], t[1]))
        for kind, D in tasks:
            sub = [r for r in rs if r["kind"] == kind and r["D"] == D]
            ok = [r for r in sub if r.get("status") == "completed"]
            U = [r for r in ok if r["nsol"] == 0]
            S = [r for r in ok if r["nsol"] > 0]
            cens = len(sub) - len(ok)
            P(f"| {cell} | {fam} | {kind}_{D} | {fmt_frac(sum(r['contains_one'] for r in U), len(U))} | "
              f"{sum(r['contains_one'] for r in S)}/{len(S)} | {cens} |")
    # ---- minimal refuting degree
    P("\n### Minimal refuting degree per UNSAT instance (among degrees computed)\n")
    P("| cell | family | closure | distribution of min D (instances) |")
    P("|---|---|---|---|")
    for (cell, fam), rs in sorted(by.items(), key=lambda t: (cellkey(t[0][0]), t[0])):
        for pref in ("M", "W"):
            per = defaultdict(dict)
            for r in rs:
                if r["kind"] == pref and r["nsol"] == 0 and r.get("status") == "completed":
                    per[r["id"]][r["D"]] = r["contains_one"]
            if not per:
                continue
            dist = defaultdict(int)
            for iid, dd in per.items():
                ref = [D for D, v in dd.items() if v]
                if ref:
                    m = min(ref)
                    # monotone: a refutation at D implies refutation at all larger D;
                    # min is only certain if every smaller computed degree failed
                    dist[f"{m}"] += 1
                else:
                    dist[f">{max(dd)} (computed {sorted(dd)})"] += 1
            P(f"| {cell} | {fam} | {pref}_D | " + ", ".join(f"D={k}: {v}" for k, v in sorted(dist.items())) + " |")
    # ---- SAT: closure determines the solutions
    P("\n### SAT instances: does W_D determine the solution set? (codim(W_D in B_<=D) == #solutions)\n")
    P("| cell | family | task | codim == nsol | standard monomials == nsol | eval rows not vanishing at known zeros (total) | evalcheck mismatches |")
    P("|---|---|---|---|---|---|---|")
    for (cell, fam), rs in sorted(by.items(), key=lambda t: (cellkey(t[0][0]), t[0])):
        for kind, D in sorted({(r["kind"], r["D"]) for r in rs}):
            S = [r for r in rs if r["kind"] == kind and r["D"] == D and r["nsol"] > 0 and r.get("status") == "completed"]
            if not S:
                continue
            cod = sum((r["ncols"] - r["rank"]) == r["nsol"] for r in S)
            sm = sum(r.get("standard_monomials") == r["nsol"] for r in S if "standard_monomials" in r)
            nsm = sum(1 for r in S if "standard_monomials" in r)
            ev = sum(sum(r.get("eval_rows_not_vanishing") or []) for r in S)
            mm = sum((r.get("ech_evalcheck_mismatch") or 0) for r in S)
            P(f"| {cell} | {fam} | {kind}_{D} | {cod}/{len(S)} | {sm}/{nsm} | {ev} | {mm} |")
    # ---- cross-check
    P("\n### Cross-check libclosure (M4RI 0.0.20200125) vs independent eliminator (myclosure.c)\n")
    P("| cell | pair | instances | contains_one agree | rank+dims agree (non-refuted, or M_D) |")
    P("|---|---|---|---|---|")
    for (cell, fam), rs in sorted(by.items(), key=lambda t: (cellkey(t[0][0]), t[0])):
        idx = {(r["id"], r["kind"], r["D"]): r for r in rs if r.get("status") == "completed"}
        for kind in ("M", "W"):
            for D in sorted({r["D"] for r in rs if r["kind"] == "my" + kind}):
                pairs = [(idx[(i, kind, D)], idx[(i, "my" + kind, D)]) for (i, kk, dd) in idx
                         if kk == kind and dd == D and (i, "my" + kind, D) in idx]
                if not pairs:
                    continue
                a1 = sum(a["contains_one"] == b["contains_one"] for a, b in pairs)
                cmp = [(a, b) for a, b in pairs if kind == "M" or (not a["contains_one"] and not b["contains_one"])]
                a2 = sum(a["rank"] == b["rank"] and a.get("dims_by_lmdeg") == b.get("dims_by_lmdeg") for a, b in cmp)
                P(f"| {cell} {fam} | {kind}_{D} vs my{kind}_{D} | {len(pairs)} | {a1}/{len(pairs)} | {a2}/{len(cmp)} |")
    # ---- sizes and cost
    P("\n### Matrix sizes, wall time and peak RSS (libclosure, completed runs; medians [min-max])\n")
    P("| cell | family | task | sat | count | ncols | max rows | final rank | basis nnz | iterations | wall s | peak RSS MB |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")

    def mm(v, f="{:.0f}"):
        v = [x for x in v if x is not None]
        if not v:
            return "-"
        return f"{f.format(st.median(v))} [{f.format(min(v))}-{f.format(max(v))}]"
    for (cell, fam), rs in sorted(by.items(), key=lambda t: (cellkey(t[0][0]), t[0])):
        for kind, D in sorted({(r["kind"], r["D"]) for r in rs if not r["kind"].startswith("my")}):
            for sat in (0, 1):
                S = [r for r in rs if r["kind"] == kind and r["D"] == D and (r["nsol"] > 0) == sat and r.get("status") == "completed"]
                if not S:
                    continue
                P(f"| {cell} | {fam} | {kind}_{D} | {sat} | {len(S)} | {S[0]['ncols']} | {mm([r['rows'] for r in S])} | "
                  f"{mm([r['rank'] for r in S])} | {mm([r.get('basis_nnz') for r in S])} | "
                  f"{mm([len(r['iterations']) - 1 for r in S if r.get('iterations')])} | {mm([r['wall_s'] for r in S], '{:.1f}')} | "
                  f"{mm([r['peak_rss_mb'] for r in S])} |")
    # ---- growth fit: W4 UNSAT, poly V, S3 family
    P("\n### Growth of per-attempt W_4 refutation cost vs l = k (S3, poly V, UNSAT, refuted runs)\n")
    pts = defaultdict(list)
    pts_rc = defaultdict(list)
    for r in rows:
        if (r["family"] == "S3" and r["vtype"] == "poly" and r["kind"] == "W" and r["D"] == 4 and r["nsol"] == 0
                and r.get("status") == "completed" and r["contains_one"]):
            pts[r["k"]].append(math.log2(max(r["wall_s"], 1e-3)))
            pts_rc[r["k"]].append(math.log2(r["rows"] * r["ncols"]))
    for name, data in (("log2(wall s)", pts), ("log2(max rows x ncols)", pts_rc)):
        ks = sorted(data)
        if len(ks) < 2:
            continue
        P(f"\n{name}: per-k medians " + ", ".join(f"k={k}: {st.median(data[k]):.2f} (n_inst={len(data[k])})" for k in ks))

        def fit(d):
            xs, ys = [], []
            for k in d:
                for y in d[k]:
                    xs.append(k); ys.append(y)
            mx, my = st.mean(xs), st.mean(ys)
            return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        slope = fit(data)
        rng = random.Random(1)
        bs = []
        for _ in range(2000):
            d2 = {k: [rng.choice(v) for _ in v] for k, v in data.items()}
            bs.append(fit(d2))
        bs.sort()
        P(f"OLS slope over instances (k in {ks}): {slope:.2f} bits per unit l, bootstrap 95% CI "
          f"[{bs[50]:.2f}, {bs[1949]:.2f}] (resampling instances within each k; {len(ks)} sizes)")
        # local slopes between consecutive k
        loc = []
        for a, b in zip(ks, ks[1:]):
            loc.append(f"k {a}->{b}: {(st.median(data[b]) - st.median(data[a])) / (b - a):.2f}")
        P("local slopes (medians): " + "; ".join(loc))
    (HERE / "tables.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
