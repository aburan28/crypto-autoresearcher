#!/usr/bin/env python3
"""Section 3.8: the ML ladder retrained on the expanded datasets.

Reads the per-dataset results files written by
ml-cryptanalysis/scripts/run_isogeny_stratified.py and writes
expanded_retrain_table.{json,md} next to this script: for every dataset-target
pair, the best out-of-fold MAE (bits) with controls only and with the static
block, the setup |F| columns where they exist, the GNN with and without edges,
the shuffled-static null (gain, p, draws) and the same-stratum paired SD.

Usage: python3 expanded_retrain_table.py [ML_RESULTS_DIR]
  (default /home/user/ml-cryptanalysis/experiments/isogeny-stratified)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else "/home/user/ml-cryptanalysis/experiments/isogeny-stratified"
DATASETS = ["prime_rho", "prime_rho_expanded", "prime_enum_graph", "prime_enum_graph_expanded",
            "binary_ic_per_curve", "binary_ic_per_curve_expanded", "binary_n51_class", "binary_classes"]
LARGE_N = 15000  # above this the pipeline draws at most 50 null permutations


def best(stages, target, features):
    v = [s["metrics"]["mae_log2"] for s in stages
         if s["stage"] == "tabular" and s["target"] == target and s["features"] == features]
    return min(v) if v else None


def main():
    rows = []
    for name in DATASETS:
        path = os.path.join(SRC, f"results_{name}.json")
        if not os.path.exists(path):
            continue
        d = json.load(open(path))["datasets"][name]
        st, summ = d["stages"], d["summary"]
        for t in sorted({s["target"] for s in st if s["stage"] == "tabular"}):
            r = {"dataset": name, "rows": summ["rows"], "edges": summ["edges"], "target": t,
                 "controls": best(st, t, "controls"), "static": best(st, t, "controls+static"),
                 "setup": best(st, t, "controls+setup"), "static_setup": best(st, t, "controls+static+setup")}
            for s in st:
                if s["target"] != t:
                    continue
                m = s["metrics"]
                if s["stage"] == "null_shuffled_static":
                    draws = m["perms"] if summ["rows"] <= LARGE_N else min(m["perms"], 50)
                    r.update(null_gain=m["observed_mae_gain_log2"], null_p=m["p_perm"], null_draws=draws)
                elif s["stage"] == "graph" and s["kind"] in ("gnn_edges", "gnn_no_edges"):
                    r[s["kind"]] = m["mae_log2"]
                elif s["stage"] == "negative_control_same_stratum_pairs":
                    r["stratum_sd"] = m["sd_paired_diff_log2"]
            r["static_minus_controls"] = r["static"] - r["controls"]
            rows.append(r)
    json.dump({"source": SRC, "rows": rows}, open(os.path.join(HERE, "expanded_retrain_table.json"), "w"), indent=1)

    f = lambda x, nd=4: "—" if x is None or x != x else f"{x:.{nd}f}"  # None or NaN (no same-stratum pairs)
    L = ["| dataset (rows) | target | controls | + static | static − controls | + setup \\|F\\| | GNN edges / no edges | null gain (p, draws) | same-stratum SD |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        gnn = f"{f(r.get('gnn_edges'))} / {f(r.get('gnn_no_edges'))}" if "gnn_edges" in r else "—"
        nul = f"{r['null_gain']:+.5f} ({r['null_p']:.3f}, {r['null_draws']})" if "null_gain" in r else "—"
        L.append(f"| {r['dataset']} ({r['rows']:,}) | `{r['target']}` | {f(r['controls'])} | {f(r['static'])} | "
                 f"{r['static_minus_controls']:+.5f} | {f(r['setup'])} | {gnn} | {nul} | {f(r.get('stratum_sd'))} |")
    open(os.path.join(HERE, "expanded_retrain_table.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
