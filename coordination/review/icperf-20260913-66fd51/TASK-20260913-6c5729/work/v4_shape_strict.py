#!/usr/bin/env python3
"""V4 step (1), tightened: where exactly do the 18 null objects match their
templates and where do they not?

The run records `shape_matches_template: true` on all 18 rows. The plan's
breaking artifact is "a null object whose monomial-degree profile or variable
count differs from its template", so the question is what "profile" covers.
This splits the comparison into pieces that can differ independently, using
v1_anf.parse_anf -- my own parser, the one whose correctness is pinned by
having evaluated every WDSat assignment in the run to 0 unsatisfied equations.
"""
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from v1_anf import parse_anf

RUN = pathlib.Path("/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3")
BENCH = pathlib.Path("/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks")
HERE = pathlib.Path(__file__).resolve().parent


def profile(path):
    a = parse_anf(str(path))
    per_eq_nonconst, consts, used = [], 0, set()
    for eq in a["equations"]:
        degs = []
        for t in eq:
            if t == ("T",):
                consts += 1
            else:
                degs.append(len(t))
                used.update(t)
        per_eq_nonconst.append(tuple(sorted(degs)))
    return {
        "nvars": a["nvars"],
        "n_eq": len(a["equations"]),
        "per_eq_nonconst": per_eq_nonconst,
        "deg_hist": collections.Counter(d for e in per_eq_nonconst for d in e),
        "n_const": consts,
        "used": used,
    }


rows = []
for r in (json.loads(l) for l in open(RUN / "results.jsonl")):
    if r.get("config") != "default_on_null_object":
        continue
    n = profile(RUN / r["null_object"])
    t = profile(BENCH / f"X{r['instance']}.anf")
    rows.append(
        {
            "null_file": os.path.basename(r["null_object"]),
            "template": f"X{r['instance']}.anf",
            "cell": r["cell"],
            "label": r["label"],
            "row_shape_matches_template": r.get("shape_matches_template"),
            "nvars_equal": n["nvars"] == t["nvars"],
            "n_equations_equal": n["n_eq"] == t["n_eq"],
            "total_degree_histogram_equal_excluding_constant": n["deg_hist"] == t["deg_hist"],
            "per_equation_degree_multiset_equal_excluding_constant": n["per_eq_nonconst"] == t["per_eq_nonconst"],
            "variable_support_equal": n["used"] == t["used"],
            "n_constant_terms_null": n["n_const"],
            "n_constant_terms_template": t["n_const"],
            "constant_terms_equal": n["n_const"] == t["n_const"],
            "n_equations": n["n_eq"],
            "const_fraction_null": round(n["n_const"] / n["n_eq"], 3),
            "const_fraction_template": round(t["n_const"] / t["n_eq"], 3),
            "conflicts": r.get("conflicts"),
            "status": r.get("status"),
            "wall_s": r.get("wall_s"),
        }
    )

agg = {
    "n_null_objects": len(rows),
    "rows_with_producer_flag_true": sum(bool(r["row_shape_matches_template"]) for r in rows),
    "nvars_equal": sum(r["nvars_equal"] for r in rows),
    "n_equations_equal": sum(r["n_equations_equal"] for r in rows),
    "total_degree_histogram_equal_excluding_constant": sum(
        r["total_degree_histogram_equal_excluding_constant"] for r in rows),
    "per_equation_degree_multiset_equal_excluding_constant": sum(
        r["per_equation_degree_multiset_equal_excluding_constant"] for r in rows),
    "variable_support_equal": sum(r["variable_support_equal"] for r in rows),
    "constant_terms_equal": sum(r["constant_terms_equal"] for r in rows),
    "constant_count_null_strictly_below_template": sum(
        r["n_constant_terms_null"] < r["n_constant_terms_template"] for r in rows),
    "mean_const_fraction_null": round(
        sum(r["const_fraction_null"] for r in rows) / len(rows), 4),
    "mean_const_fraction_template": round(
        sum(r["const_fraction_template"] for r in rows) / len(rows), 4),
}
json.dump({"aggregate": agg, "rows": rows},
          open(HERE / "v4_shape_strict.json", "w"), indent=1, sort_keys=True)
print(json.dumps(agg, indent=1))
