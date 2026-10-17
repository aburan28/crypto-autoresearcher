#!/usr/bin/env python3
"""fit.py -- m4-sat-cost-pilot. EXPLORATORY, hypothesis-generating; not program evidence.

Deterministic (stdlib only, seed 20261017). Reads results/*.jsonl, writes fit.json and
aggregate.md: per-cell table and least-squares fits log2(conflicts) = a + alpha * l per
(family, m, config) over completed UNSAT instances, with a non-parametric bootstrap CI
(2000 resamples of the instance rows, percentile 2.5/97.5). Censored (timed-out) rows
are listed, never imputed, never fitted.
"""
import glob
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 20261017
NBOOT = 2000
BUDGET_ALPHA = {3: 0.5, 4: 1.0}   # alpha < m/2 - 1 (ctrial-harvest/README.md)

rows = []
for p in sorted(glob.glob(str(HERE / "results" / "*.jsonl"))):
    for line in open(p):
        r = json.loads(line)
        r.setdefault("family", "chained_S3")
        rows.append(r)


def ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None, None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b


def fit_group(grp):
    xs = [r["l"] for r in grp]; ys = [math.log2(r["conflicts"]) for r in grp]
    a, b = ols(xs, ys)
    if b is None:
        return {"n": len(grp), "l_values": sorted(set(xs)), "alpha": None, "note": "single l value; no slope"}
    rng = random.Random(SEED)
    bs = []
    for _ in range(NBOOT):
        samp = [grp[rng.randrange(len(grp))] for _ in grp]
        _, bb = ols([r["l"] for r in samp], [math.log2(r["conflicts"]) for r in samp])
        if bb is not None:
            bs.append(bb)
    bs.sort()
    lo, hi = bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    return {"n": len(grp), "l_values": sorted(set(xs)), "a": a, "alpha": b, "alpha_ci95": [lo, hi],
            "rmse_bits": math.sqrt(sum(e * e for e in resid) / len(resid)), "n_boot": len(bs)}


# ---- per-cell table
cells = defaultdict(list)
for r in rows:
    cells[(r["family"], r["m"], r["n"], r["l"], r["config"])].append(r)
table = []
for key in sorted(cells):
    fam, m, n, l, cfg = key
    grp = cells[key]
    U = [r for r in grp if r["label"] == "UNSAT"]
    Uok = [r for r in U if r["status"] == "UNSAT"]
    Ucens = [r for r in U if r["status"] == "censored_timeout"]
    Ubad = [r for r in U if r["status"] not in ("UNSAT", "censored_timeout")]
    S = [r for r in grp if r["label"] == "SAT"]
    Sok = [r for r in S if r["status"] == "SAT"]
    law = 2 ** (m * l) / math.factorial(m)
    ent = {"family": fam, "m": m, "n": n, "l": l, "config": cfg, "N": grp[0]["N"], "neq": grp[0]["neq"],
           "unsat_completed": len(Uok), "unsat_censored": len(Ucens), "unsat_other": len(Ubad),
           "sat_completed": len(Sok), "sat_total": len(S),
           "exhaustive_2_ml": 2 ** (m * l), "law_2ml_over_mfact": law}
    if Uok:
        c = [r["conflicts"] for r in Uok]
        ent.update({"conf_median": st.median(c), "conf_mean": st.mean(c), "conf_min": min(c), "conf_max": max(c),
                    "log2_conf_median": math.log2(st.median(c)), "ratio_median_to_law": st.median(c) / law,
                    "ratio_median_to_2ml": st.median(c) / 2 ** (m * l),
                    "wall_median_s": st.median(r["wall_s"] for r in Uok),
                    "nodes_eq_conf": all(r.get("nodes") == r["conflicts"] for r in Uok),
                    "fails_minus_conf": sorted(set(r["fails"] - r["conflicts"] for r in Uok if r.get("fails") is not None)),
                    "label_agree": all(r["label_agrees_with_solver"] for r in Uok)})
    if Ucens:
        ent["censored_wall_s"] = [round(r["wall_s"], 1) for r in Ucens]
    if Sok:
        ent.update({"sat_conf_median": st.median(r["conflicts"] for r in Sok), "sat_conf": sorted(r["conflicts"] for r in Sok),
                    "sat_models_verified": ("n/a (no system to check against)" if all(r.get("sat_model_verified") is None for r in Sok) else all(r.get("sat_model_verified") for r in Sok)),
                    "sat_wall_median_s": st.median(r["wall_s"] for r in Sok)})
    if S and len(Sok) < len(S):
        ent["sat_not_completed"] = [(r["id"], r["status"]) for r in S if r["status"] != "SAT"]
    table.append(ent)

# ---- fits
fits = {}
groups = defaultdict(list)
for r in rows:
    if r["label"] == "UNSAT" and r["status"] == "UNSAT" and r["conflicts"]:
        groups[(r["family"], r["m"], r["config"])].append(r)
for key in sorted(groups):
    fam, m, cfg = key
    f = fit_group(groups[key])
    f["budget_alpha_max"] = BUDGET_ALPHA.get(m)
    f["cells"] = sorted(set((r["n"], r["l"]) for r in groups[key]))
    fits[f"{fam}|m{m}|{cfg}"] = f
    # fixed-n subsets (l varied at one n), where >= 2 l values exist
    byn = defaultdict(list)
    for r in groups[key]:
        byn[r["n"]].append(r)
    for n, g in sorted(byn.items()):
        if len(set(r["l"] for r in g)) >= 2:
            fits[f"{fam}|m{m}|{cfg}|n{n}"] = {**fit_group(g), "fixed_n": n}

out = {"seed": SEED, "n_boot": NBOOT, "rows": len(rows), "cells": table, "fits": fits}
json.dump(out, open(HERE / "fit.json", "w"), indent=1, sort_keys=True)

# ---- aggregate.md
L = ["# m4-sat-cost-pilot: per-cell table and fits", "",
     "Exploratory, hypothesis-generating. Not program evidence. Generated by `fit.py` (seed "
     f"{SEED}, {NBOOT} bootstrap resamples) from `results/*.jsonl`; every number below is a function of those files.", "",
     "`conf` is WDSat's own printed counter (the paper's 'conflicts': one count per branch point "
     "opened, i.e. per decision; the patched build's `nodes` counter equals it on every row where "
     "`nodes_eq_conf` is true, and `fails` = failed branch inferences = conf + 1 on UNSAT runs). "
     "`law` = 2^(m l)/m!. Chained cells: `family` chained_S3 (this pilot's exporter); `trimoska_S4`: "
     "the vendored published S_4 instances (`inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks`), solver-build control.", "",
     "## UNSAT per cell", "",
     "| family | m | n | k=l | config | N | #eq | UNSAT done | cens. | conf median | conf mean | 2^(ml) | law 2^(ml)/m! | median/law | median/2^(ml) | median wall s |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for e in table:
    if e["unsat_completed"]:
        L.append(f"| {e['family']} | {e['m']} | {e['n']} | {e['l']} | {e['config']} | {e['N']} | {e['neq']} | {e['unsat_completed']} | {e['unsat_censored']} | "
                 f"{e['conf_median']:.0f} | {e['conf_mean']:.1f} | {e['exhaustive_2_ml']} | {e['law_2ml_over_mfact']:.1f} | {e['ratio_median_to_law']:.3f} | "
                 f"{e['ratio_median_to_2ml']:.4f} | {e['wall_median_s']:.2f} |")
    else:
        L.append(f"| {e['family']} | {e['m']} | {e['n']} | {e['l']} | {e['config']} | {e['N']} | {e['neq']} | 0 | {e['unsat_censored']} | "
                 f"censored ({', '.join(str(w) for w in e.get('censored_wall_s', []))} s) | | {e['exhaustive_2_ml']} | {e['law_2ml_over_mfact']:.1f} | | | |")
L += ["", "## SAT instances (cost reported separately; never fitted)", "",
      "| family | m | n | l | config | SAT done / labelled | conf values | median wall s | models verified |", "|---|---|---|---|---|---|---|---|---|"]
for e in table:
    if e["sat_total"]:
        L.append(f"| {e['family']} | {e['m']} | {e['n']} | {e['l']} | {e['config']} | {e['sat_completed']}/{e['sat_total']} | "
                 f"{e.get('sat_conf', [])} | {e.get('sat_wall_median_s', float('nan')):.2f} | {e.get('sat_models_verified')} |")
L += ["", "## Fits: log2(conf) = a + alpha * l over completed UNSAT instances", "",
      "| group | cells (n,l) | n rows | a | alpha | 95% bootstrap CI | rmse bits | budget needs alpha < |", "|---|---|---|---|---|---|---|---|"]
for key, f in fits.items():
    if f.get("alpha") is None:
        L.append(f"| {key} | {f.get('cells', f.get('fixed_n'))} | {f['n']} | | (one l value) | | | {f.get('budget_alpha_max', '')} |")
    else:
        L.append(f"| {key} | {f.get('cells', 'n=' + str(f.get('fixed_n')))} | {f['n']} | {f['a']:.2f} | {f['alpha']:.3f} | "
                 f"[{f['alpha_ci95'][0]:.3f}, {f['alpha_ci95'][1]:.3f}] | {f['rmse_bits']:.3f} | {f.get('budget_alpha_max', '')} |")
L += ["", "Integrity flags: " + ("all UNSAT labels agree with the solver" if all(e.get("label_agree", True) for e in table) else "LABEL DISAGREEMENT, see fit.json")
      + "; " + ("all checkable SAT models verified" if all(e.get("sat_models_verified", True) in (True,) or isinstance(e.get("sat_models_verified"), str) for e in table) else "UNVERIFIED SAT MODEL, see fit.json") + "."]
(HERE / "aggregate.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
