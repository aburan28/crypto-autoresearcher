#!/usr/bin/env python3
"""Joint V4 of REVIEW-ICPERF-20260913-66fd51 (TASK-20260913-6c5729): null-object
shape and P6 censoring.  Validator's own ANF parser (same one used for V1 step 2);
convert.anf_shape is NOT used.  Pure parsing + medians over results.jsonl.

(1) For each of the 18 files in null_objects/, and for the template Xn..anf the
    row names, compute: header variable/equation counts, distinct variables used,
    monomial counts per degree, the per-equation (degree -> count) profile as an
    ordered list and as a multiset, the number of equations carrying the constant
    T, and two degeneracy checks (repeated variable inside a monomial; repeated
    monomial inside an equation).  Report equality template vs null.
(2) Recompute the P6 ratios from conflicts (pooled median over the six nulls of
    a cell, and summary.py's mean-of-two-label-medians, side by side).
(3) n19l6 censored bound: 180 s / median structured-U default wall.
"""
import json
import os
import statistics as st
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspace"
RUN = f"{ROOT}/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
BENCH = f"{ROOT}/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"


def parse_anf(path):
    lines = open(path).read().split("\n")
    hdr = lines[0].split()
    assert hdr[0] == "p" and hdr[1] == "cnf", hdr
    nvars, neqs = int(hdr[2]), int(hdr[3])
    eqs = []
    for ln in lines[1:]:
        ln = ln.strip()
        if not ln:
            continue
        toks = ln.split()
        assert toks[0] == "x" and toks[-1] == "0", ln
        toks = toks[1:-1]
        terms, const, i = [], 0, 0
        while i < len(toks):
            t = toks[i]
            if t == "T":
                const ^= 1
                i += 1
            elif t.startswith("."):
                d = int(t[1:])
                terms.append(tuple(int(v) for v in toks[i + 1:i + 1 + d]))
                i += 1 + d
            else:
                terms.append((int(t),))
                i += 1
        eqs.append((terms, const))
    assert len(eqs) == neqs, (path, len(eqs), neqs)
    return nvars, eqs


def shape(path):
    nvars, eqs = parse_anf(path)
    used = set()
    by_deg = Counter()
    per_eq = []
    t_count = 0
    repeated_var_in_monomial = 0
    repeated_monomial_in_eq = 0
    max_var = 0
    distinct = set()
    for terms, const in eqs:
        prof = Counter()
        seen = Counter()
        for mono in terms:
            prof[len(mono)] += 1
            by_deg[len(mono)] += 1
            used.update(mono)
            max_var = max(max_var, *mono)
            if len(set(mono)) != len(mono):
                repeated_var_in_monomial += 1
            seen[tuple(sorted(mono))] += 1
            distinct.add(tuple(sorted(mono)))
        repeated_monomial_in_eq += sum(1 for v in seen.values() if v > 1)
        per_eq.append(tuple(sorted(prof.items())))
        t_count += const
    distinct_by_deg = Counter(len(m) for m in distinct)
    d_nonunary = sum(v for d, v in distinct_by_deg.items() if d > 1)
    return {
        "header_nvars": nvars, "header_neqs": len(eqs), "distinct_vars_used": len(used), "max_var_id": max_var,
        "monomials_by_degree": dict(sorted(by_deg.items())), "total_monomials": sum(by_deg.values()),
        "distinct_monomials_by_degree": dict(sorted(distinct_by_deg.items())),
        "distinct_unary": distinct_by_deg.get(1, 0), "distinct_nonunary": d_nonunary,
        "wdsat_MAX_ID_derived (nvars + distinct nonunary)": nvars + d_nonunary,
        "wdsat_MAX_EQ_derived (sum over distinct nonunary of degree+1)": sum((d + 1) * v for d, v in distinct_by_deg.items() if d > 1),
        "max_degree": max(distinct_by_deg),
        "per_eq_profile_ordered": per_eq, "per_eq_profile_multiset": sorted(per_eq),
        "equations_with_constant_T": t_count,
        "monomials_with_repeated_variable": repeated_var_in_monomial,
        "equations_with_repeated_monomial": repeated_monomial_in_eq,
    }


rows = [json.loads(l) for l in open(f"{RUN}/results.jsonl") if l.strip()]
nulls = [r for r in rows if r.get("config") == "default_on_null_object"]
assert len(nulls) == 18, len(nulls)

SHAPE_KEYS = ["header_nvars", "header_neqs", "distinct_vars_used", "max_var_id", "monomials_by_degree",
              "total_monomials", "per_eq_profile_ordered", "per_eq_profile_multiset"]
table = []
for r in sorted(nulls, key=lambda r: (r["cell"], r["label"], r["instance"])):
    null_path = f"{RUN}/{r['null_object']}"
    tmpl_path = f"{BENCH}/X{r['instance']}.anf"
    sn, stpl = shape(null_path), shape(tmpl_path)
    eq = {k: sn[k] == stpl[k] for k in SHAPE_KEYS}
    ns = r.get("null_sizing") or {}
    table.append({
        "instance": r["instance"], "cell": r["cell"], "label": r["label"], "null_object": r["null_object"],
        "template": os.path.relpath(tmpl_path, ROOT), "row_shape_matches_template": r.get("shape_matches_template"),
        "template_nvars/neqs": (stpl["header_nvars"], stpl["header_neqs"]),
        "null_nvars/neqs": (sn["header_nvars"], sn["header_neqs"]),
        "template_monomials_by_degree": stpl["monomials_by_degree"], "null_monomials_by_degree": sn["monomials_by_degree"],
        "template_distinct_vars": stpl["distinct_vars_used"], "null_distinct_vars": sn["distinct_vars_used"],
        "per_eq_profile_equal_in_order": eq["per_eq_profile_ordered"],
        "per_eq_profile_equal_as_multiset": eq["per_eq_profile_multiset"],
        "template_T_count": stpl["equations_with_constant_T"], "null_T_count": sn["equations_with_constant_T"],
        "null_monomials_with_repeated_variable": sn["monomials_with_repeated_variable"],
        "null_equations_with_repeated_monomial": sn["equations_with_repeated_monomial"],
        "template_monomials_with_repeated_variable": stpl["monomials_with_repeated_variable"],
        "template_equations_with_repeated_monomial": stpl["equations_with_repeated_monomial"],
        "validator_shape_equal_all_keys": all(eq.values()), "shape_key_equality": eq,
        "template_distinct_monomials_by_degree": stpl["distinct_monomials_by_degree"],
        "null_distinct_monomials_by_degree": sn["distinct_monomials_by_degree"],
        "distinct_nonunary_tmpl/null": (stpl["distinct_nonunary"], sn["distinct_nonunary"]),
        "null_sizing_row_vs_validator": {
            "n_eqs": (ns.get("n_eqs"), sn["header_neqs"]),
            "n_unary": (ns.get("n_unary"), sn["distinct_unary"]),
            "n_nonunary_monomials": (ns.get("n_nonunary_monomials"), sn["distinct_nonunary"]),
            "MAX_ANF_ID": (ns.get("MAX_ANF_ID"), sn["header_nvars"] + 1),
            "MAX_ID": (ns.get("MAX_ID"), sn["wdsat_MAX_ID_derived (nvars + distinct nonunary)"]),
            "MAX_EQ": (ns.get("MAX_EQ"), sn["wdsat_MAX_EQ_derived (sum over distinct nonunary of degree+1)"]),
            "MAX_XEQ": (ns.get("MAX_XEQ"), sn["header_neqs"] + 1),
            "MAX_DEGREE": (ns.get("MAX_DEGREE"), sn["max_degree"]),
        },
        "status": r["status"], "conflicts": r.get("conflicts"), "wall_s": r["wall_s"], "timeout_s": r["timeout_s"],
        "timed_out": r.get("timed_out"), "wdsat_MAX_ID_vs_null_sizing": (r["wdsat_constants"]["MAX_ID"], ns.get("MAX_ID")),
    })

# ---- (2) P6 ratios


def med(v):
    v = [x for x in v if x is not None]
    return st.median(v) if v else None


def finished(r):
    s = r.get("status", "")
    return not (s.startswith("budget_stop") or s.startswith("infrastructure") or s == "unknown")


p6 = {}
for cell in ("n15l5", "n17l6", "n19l6"):
    U_default = [r["conflicts"] for r in rows if r["cell"] == cell and r["label"] == "U" and r["engine"] == "wdsat"
                 and r["config"] == "default" and finished(r)]
    S_default = [r["conflicts"] for r in rows if r["cell"] == cell and r["label"] == "S" and r["engine"] == "wdsat"
                 and r["config"] == "default" and finished(r)]
    cell_nulls = [r for r in nulls if r["cell"] == cell]
    fin = [r for r in cell_nulls if finished(r)]
    pooled = med([r["conflicts"] for r in fin])
    medS = med([r["conflicts"] for r in fin if r["label"] == "S"])
    medU = med([r["conflicts"] for r in fin if r["label"] == "U"])
    mean_of_label_medians = med([medS, medU])  # summary.py: med([U_null_med, S_null_med]) = their mean
    U_med = med(U_default)
    min_fin_null = min([r["conflicts"] for r in fin], default=None)
    U_default_wall = med([r["wall_s"] for r in rows if r["cell"] == cell and r["label"] == "U" and r["engine"] == "wdsat"
                          and r["config"] == "default" and finished(r)])
    S_default_wall = med([r["wall_s"] for r in rows if r["cell"] == cell and r["label"] == "S" and r["engine"] == "wdsat"
                          and r["config"] == "default" and finished(r)])
    p6[cell] = {
        "n_nulls": len(cell_nulls), "n_finished": len(fin), "statuses": Counter(r["status"] for r in cell_nulls),
        "null_conflicts_each": [(r["instance"], r["status"], r.get("conflicts"), r["wall_s"]) for r in cell_nulls],
        "structured_U_default_median_conflicts": U_med, "structured_S_default_median_conflicts": med(S_default),
        "null_pooled_median_conflicts": pooled, "null_S_median": medS, "null_U_median": medU,
        "null_mean_of_label_medians (summary.py rule)": mean_of_label_medians,
        "ratio_pooled": (pooled / U_med) if pooled and U_med else None,
        "ratio_summary_rule": (mean_of_label_medians / U_med) if mean_of_label_medians and U_med else None,
        "min_finishing_null_conflicts": min_fin_null,
        "min_finishing_null_over_U_median": (min_fin_null / U_med) if min_fin_null and U_med else None,
        "any_finishing_null_below_structured_U_median": (min_fin_null is not None and min_fin_null < U_med),
        "structured_U_default_median_wall_s": U_default_wall, "structured_S_default_median_wall_s": S_default_wall,
        "censored_wall_lower_bound_180_over_U_median_wall": 180.0 / U_default_wall if U_default_wall else None,
        "censored_wall_lower_bound_180_over_S_median_wall": 180.0 / S_default_wall if S_default_wall else None,
    }

# ---- MAX_ID sizing invariant over every WDSat row (structured and null): the contract's
# invalidation rule names a build whose MAX_ID differs from the ANF-derived value.
shape_cache = {}


def cached_shape(path):
    if path not in shape_cache:
        shape_cache[path] = shape(path)
    return shape_cache[path]


maxid_check = []
for r in rows:
    if r.get("engine") != "wdsat" or "wdsat_constants" not in r:
        continue
    anf = f"{RUN}/{r['null_object']}" if r.get("config") == "default_on_null_object" else f"{BENCH}/X{r['instance']}.anf"
    s = cached_shape(anf)
    derived = s["wdsat_MAX_ID_derived (nvars + distinct nonunary)"]
    maxid_check.append((r["instance"], r["config"], r["wdsat_constants"]["MAX_ID"], derived,
                        r["wdsat_constants"]["MAX_ID"] == derived,
                        r["wdsat_constants"].get("MAX_ANF_ID") == s["header_nvars"] + 1,
                        r["wdsat_constants"].get("MAX_XEQ") == s["header_neqs"] + 1,
                        r["wdsat_constants"].get("MAX_EQ") == s["wdsat_MAX_EQ_derived (sum over distinct nonunary of degree+1)"]))
maxid_summary = {"wdsat_rows_checked": len(maxid_check),
                 "MAX_ID_matches": sum(1 for m in maxid_check if m[4]),
                 "MAX_ANF_ID_matches": sum(1 for m in maxid_check if m[5]),
                 "MAX_XEQ_matches": sum(1 for m in maxid_check if m[6]),
                 "MAX_EQ_matches_(d+1)_rule": sum(1 for m in maxid_check if m[7]),
                 "MAX_ID_mismatches": [m for m in maxid_check if not m[4]]}

out = {"shape_table": table, "P6": p6, "wdsat_sizing_invariant": maxid_summary,
       "distinct_nonunary_tmpl_vs_null": [(t["instance"],) + t["distinct_nonunary_tmpl/null"] for t in table],
       "n_rows_shape_equal_validator": sum(1 for t in table if t["validator_shape_equal_all_keys"]),
       "n_rows_shape_true_on_row": sum(1 for t in table if t["row_shape_matches_template"]),
       "rows_where_validator_disagrees_with_row_flag": [t["instance"] for t in table if t["validator_shape_equal_all_keys"] != bool(t["row_shape_matches_template"])],
       "rows_with_T_count_difference": [(t["instance"], t["template_T_count"], t["null_T_count"]) for t in table if t["template_T_count"] != t["null_T_count"]],
       "null_degeneracies": [(t["instance"], t["null_monomials_with_repeated_variable"], t["null_equations_with_repeated_monomial"]) for t in table
                             if t["null_monomials_with_repeated_variable"] or t["null_equations_with_repeated_monomial"]],
       "template_degeneracies": [(t["instance"], t["template_monomials_with_repeated_variable"], t["template_equations_with_repeated_monomial"]) for t in table
                                 if t["template_monomials_with_repeated_variable"] or t["template_equations_with_repeated_monomial"]],
       "null_sizing_mismatches": [(t["instance"], t["null_sizing_row_vs_validator"]) for t in table
                                  if any(a != b for a, b in t["null_sizing_row_vs_validator"].values())],
       }
json.dump(out, open(f"{HERE}/v4_null_shapes.json", "w"), indent=1, default=str)

# markdown table
md = ["| instance | template (vars,eqs) | null (vars,eqs) | template monomials by degree | null monomials by degree | per-eq profile equal (ordered / multiset) | T count tmpl/null | distinct vars tmpl/null | row flag | validator | status | conflicts | wall_s |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for t in table:
    md.append(f"| {t['instance']} | {t['template_nvars/neqs']} | {t['null_nvars/neqs']} | {t['template_monomials_by_degree']} | {t['null_monomials_by_degree']} | "
              f"{t['per_eq_profile_equal_in_order']} / {t['per_eq_profile_equal_as_multiset']} | {t['template_T_count']}/{t['null_T_count']} | "
              f"{t['template_distinct_vars']}/{t['null_distinct_vars']} | {t['row_shape_matches_template']} | {t['validator_shape_equal_all_keys']} | {t['status']} | {t['conflicts']} | {t['wall_s']} |")
md.append("")
md.append("## P6 per cell")
md.append("")
md.append("| cell | nulls finished/6 | null pooled median conflicts | null S-median / U-median | summary.py rule (mean of label medians) | structured U default median conflicts | ratio (pooled) | ratio (summary rule) | min finishing null / U median | 180 s / U median wall | 180 s / S median wall |")
md.append("|---|---|---|---|---|---|---|---|---|---|---|")
for c, v in p6.items():
    f = lambda x: "null" if x is None else (f"{x:.2f}" if isinstance(x, float) else str(x))
    md.append(f"| {c} | {v['n_finished']}/{v['n_nulls']} | {f(v['null_pooled_median_conflicts'])} | {f(v['null_S_median'])} / {f(v['null_U_median'])} | "
              f"{f(v['null_mean_of_label_medians (summary.py rule)'])} | {f(v['structured_U_default_median_conflicts'])} | {f(v['ratio_pooled'])} | "
              f"{f(v['ratio_summary_rule'])} | {f(v['min_finishing_null_over_U_median'])} | {f(v['censored_wall_lower_bound_180_over_U_median_wall'])} | "
              f"{f(v['censored_wall_lower_bound_180_over_S_median_wall'])} |")
open(f"{HERE}/v4_null_shapes.md", "w").write("\n".join(md) + "\n")

print("shape equal (validator):", out["n_rows_shape_equal_validator"], "/ 18; row flag true:", out["n_rows_shape_true_on_row"],
      "; disagreements:", out["rows_where_validator_disagrees_with_row_flag"])
print("T-count differences:", out["rows_with_T_count_difference"])
print("null degeneracies:", out["null_degeneracies"])
print("template degeneracies:", out["template_degeneracies"])
print("null_sizing mismatches:", out["null_sizing_mismatches"])
print("distinct nonunary monomials template vs null:", out["distinct_nonunary_tmpl_vs_null"])
print("wdsat sizing invariant:", maxid_summary)
for c, v in p6.items():
    print(c, {k: v[k] for k in ("n_finished", "statuses", "null_pooled_median_conflicts", "null_mean_of_label_medians (summary.py rule)",
                                 "structured_U_default_median_conflicts", "ratio_pooled", "ratio_summary_rule", "min_finishing_null_over_U_median",
                                 "any_finishing_null_below_structured_U_median", "censored_wall_lower_bound_180_over_U_median_wall",
                                 "censored_wall_lower_bound_180_over_S_median_wall")})
    print("   ", v["null_conflicts_each"])
