"""V4: null-object shape against template, P6 ratios, n19l6 censoring.

Shape is computed with the validator's own ANF parser (v1_anf.parse_anf),
independently of code/convert.py's anf_shape.
"""
from __future__ import annotations

import json
import os
import statistics
from collections import Counter

from v1_anf import parse_anf

RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
OUT = os.path.dirname(os.path.abspath(__file__))


def shape(path):
    a = parse_anf(path)
    per_eq = []
    agg = Counter()
    for eq in a["equations"]:
        degs = Counter(("T" if t == ("T",) else len(t)) for t in eq)
        per_eq.append(tuple(sorted(degs.items(), key=lambda kv: str(kv[0]))))
        agg.update(degs)
    used = set()
    for eq in a["equations"]:
        for t in eq:
            if t != ("T",):
                used.update(t)
    return {
        "nvars_header": a["nvars"],
        "neqs_header": a["neqs_declared"],
        "n_equations": len(a["equations"]),
        "n_distinct_variables_used": len(used),
        "max_variable_index": max(used) if used else 0,
        "degree_histogram": {str(k): v for k, v in sorted(agg.items(), key=lambda kv: str(kv[0]))},
        "n_terms_total": sum(agg.values()),
        "per_equation_degree_multisets": per_eq,
    }


def main():
    rows = [json.loads(l) for l in open(os.path.join(RUN, "results.jsonl"))]
    nulls = [r for r in rows if r.get("config") == "default_on_null_object"]
    assert len(nulls) == 18, len(nulls)

    table = []
    for r in nulls:
        npath = os.path.join(RUN, r["null_object"])
        tpath = os.path.join(BENCH, f"X{r['instance']}.anf")
        ns, ts = shape(npath), shape(tpath)
        per_eq_equal = ns["per_equation_degree_multisets"] == ts["per_equation_degree_multisets"]
        table.append({
            "null_file": os.path.basename(npath),
            "template": os.path.basename(tpath),
            "cell": r["cell"], "label": r["label"],
            "seed": r.get("null_seed"),
            "row_shape_matches_template": r.get("shape_matches_template"),
            "nvars_null": ns["nvars_header"], "nvars_template": ts["nvars_header"],
            "neqs_null": ns["n_equations"], "neqs_template": ts["n_equations"],
            "nvars_equal": ns["nvars_header"] == ts["nvars_header"],
            "neqs_equal": ns["n_equations"] == ts["n_equations"],
            "degree_histogram_equal": ns["degree_histogram"] == ts["degree_histogram"],
            "per_equation_degree_multiset_equal": per_eq_equal,
            "distinct_vars_used_null": ns["n_distinct_variables_used"],
            "distinct_vars_used_template": ts["n_distinct_variables_used"],
            "max_var_index_null": ns["max_variable_index"],
            "max_var_index_template": ts["max_variable_index"],
            "degree_histogram_null": ns["degree_histogram"],
            "degree_histogram_template": ts["degree_histogram"],
            "status": r["status"], "conflicts": r.get("conflicts"),
            "wall_s": r.get("wall_s"), "timeout_s": r.get("timeout_s"),
            "null_sizing_n_eqs": (r.get("null_sizing") or {}).get("n_eqs"),
            "null_sizing_n_unary": (r.get("null_sizing") or {}).get("n_unary"),
            "null_sizing_n_nonunary_monomials": (r.get("null_sizing") or {}).get("n_nonunary_monomials"),
        })

    # ---- P6 recomputation, two aggregations ------------------------------
    p6 = {}
    for cell in ("n15l5", "n17l6", "n19l6"):
        nl = [r for r in nulls if r["cell"] == cell]
        fin = [r for r in nl if r["status"] in ("SAT", "UNSAT")]
        struct_u = [r["conflicts"] for r in rows
                    if r.get("engine") == "wdsat" and r.get("config") == "default"
                    and r["cell"] == cell and r["label"] == "U"
                    and r["status"] in ("SAT", "UNSAT")]
        su_med = statistics.median(struct_u)
        su_wall = statistics.median([r["wall_s"] for r in rows
                                     if r.get("engine") == "wdsat" and r.get("config") == "default"
                                     and r["cell"] == cell and r["label"] == "U"
                                     and r["status"] in ("SAT", "UNSAT")])
        per_label = {}
        for lab in ("S", "U"):
            v = [r["conflicts"] for r in fin if r["label"] == lab]
            per_label[lab] = statistics.median(v) if v else None
        allv = [r["conflicts"] for r in fin]
        pooled = statistics.median(allv) if allv else None
        lm = [v for v in per_label.values() if v is not None]
        label_med = statistics.median(lm) if lm else None
        p6[cell] = {
            "n_null_rows": len(nl), "n_null_finished": len(fin),
            "n_null_timeout": len(nl) - len(fin),
            "per_label_median_conflicts": per_label,
            "null_median_conflicts_pooled_over_all_rows": pooled,
            "null_median_conflicts_median_of_label_medians": label_med,
            "structured_U_median_conflicts": su_med,
            "ratio_pooled": (pooled / su_med) if pooled else None,
            "ratio_median_of_label_medians": (label_med / su_med) if label_med else None,
            "structured_U_median_wall_s": su_wall,
            "null_timeout_s": sorted({r["timeout_s"] for r in nl}),
            "censored_wall_ratio_lower_bound":
                (sorted({r["timeout_s"] for r in nl})[0] / su_wall),
            "any_timed_out_null_reports_conflicts":
                any(r.get("conflicts") is not None for r in nl
                    if r["status"] not in ("SAT", "UNSAT")),
        }

    out = {"shape_table": table, "P6": p6}
    with open(os.path.join(OUT, "v4_null.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    print(f"{'null file':28s} {'nv=':>4s} {'neq=':>5s} {'deghist=':>9s} {'per-eq=':>8s} "
          f"{'row flag':>9s} {'status':>18s} {'conflicts':>10s}")
    for t in table:
        print(f"{t['null_file']:28s} {str(t['nvars_equal']):>4s} {str(t['neqs_equal']):>5s} "
              f"{str(t['degree_histogram_equal']):>9s} {str(t['per_equation_degree_multiset_equal']):>8s} "
              f"{str(t['row_shape_matches_template']):>9s} {t['status']:>18s} "
              f"{str(t['conflicts']):>10s}")
    print()
    agree = sum(1 for t in table if t["nvars_equal"] and t["neqs_equal"]
                and t["degree_histogram_equal"] and t["per_equation_degree_multiset_equal"])
    print(f"null objects matching template on all four shape statistics: {agree}/18")
    print()
    for cell, v in p6.items():
        print(cell, json.dumps({k: vv for k, vv in v.items()
                                if k != "per_label_median_conflicts"}, sort_keys=True))
        print("   per-label medians:", v["per_label_median_conflicts"])


if __name__ == "__main__":
    main()
