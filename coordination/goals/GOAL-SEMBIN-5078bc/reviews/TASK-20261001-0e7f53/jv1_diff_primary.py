"""JV-1 attack step 1: diff every primary cell of RUN-SEMBIN-be48b7 against an
independent implementation of the AMD-20261001-e61f2b header block.

Inputs: raw-result.json read from commit b8019a6fb via `git show` (never the
working tree), and jv1_header_model.py (this directory).

Checks
  D1  every argmin row (3600): s, TPR, CALLS, PROBE, FILL, LA, TOTAL, VOW,
      margins, subrho flags, store, domain-edge flag, recomputed at the row's
      (n, m, d, model, B).
  D2  independent grid argmin per (n, model, B, m, bound) over the v1 grid
      d = 1.0 .. bound step 0.25, CALLS < 0 excluded; compare TOTAL (and d when
      the argmin is unique).
  D3  every cell_counts row (240): cells, in_domain, out_of_domain,
      subrho_vs_VOW, subrho_vs_PUB.
  D4  the generic-lower-bound flag (C-3) over every primary cell, and its
      per-degree minimum slack.
  D5  per-degree primary minimum and its margin, against E-2.
  D6  continuous-d minimum per (n, model, B, m) in domain (fine grid + golden
      refinement), and the grid discretisation excess per row.
  D7  domain exclusion: every CALLS < 0 cell re-costed with CALLS clamped to
      0 (one oracle call) -- would any excluded cell be sub-rho if kept?
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm  # noqa: E402

REPO = HERE.parents[4]
SNAP = "b8019a6fb"
RAW = "experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-be48b7/raw-result.json"

BUDGETS = ["30", "40", "50", "60", "70", "80", "90", "100", "unlimited"]
COMBOS = [("FREE", "unlimited"), ("ENUM", "unlimited"), ("MITM", "unlimited")] + [
    ("MITM_CAPPED", b) for b in BUDGETS]
PRIMARY = {"ENUM", "MITM", "MITM_CAPPED"}
MS = range(2, 17)


def log2B(b: str):
    return None if b == "unlimited" else float(b)


def grid(bound: float):
    out, k = [], 0
    while True:
        d = 1.0 + 0.25 * k
        if d > bound + 1e-12:
            break
        out.append(d)
        k += 1
    return out


def bound_value(n: int, label: str) -> float:
    return float(n) if label == "n" else n / 2.0


def load_raw():
    txt = subprocess.check_output(["git", "-C", str(REPO), "show", f"{SNAP}:{RAW}"])
    return json.loads(txt)


def main():
    raw = load_raw()
    res = {"snapshot": SNAP, "raw_result": RAW}

    # ---------------- D1: argmin rows ----------------
    fields = ["TPR", "CALLS", "PROBE", "FILL", "LA", "TOTAL", "VOW"]
    maxdiff = defaultdict(float)
    mism = []
    for row in raw["argmin_rows"]:
        c = hm.cell(row["n"], row["m"], row["d"], row["model"], log2B(row["B"]))
        if c["s"] != row["s"]:
            mism.append(("s", row["n"], row["model"], row["B"], row["m"], row["d_bound"], c["s"], row["s"]))
        for f in fields:
            dlt = abs(c[f] - row[f])
            maxdiff[f] = max(maxdiff[f], dlt)
        mv = c["TOTAL"] - c["VOW"]
        maxdiff["margin_vs_VOW_bits"] = max(maxdiff["margin_vs_VOW_bits"], abs(mv - row["margin_vs_VOW_bits"]))
        if row["n"] == 131:
            mp = c["TOTAL"] - hm.PUB_131
            maxdiff["margin_vs_PUB_bits"] = max(maxdiff["margin_vs_PUB_bits"], abs(mp - row["margin_vs_PUB_bits"]))
            if (mp < 0) != row["subrho_vs_PUB"]:
                mism.append(("subrho_vs_PUB", row["n"], row["model"], row["B"], row["m"], row["d_bound"]))
        else:
            if row["PUB"] is not None or row["margin_vs_PUB_bits"] is not None:
                mism.append(("PUB_outside_131", row["n"], row["model"], row["B"], row["m"]))
        if (mv < 0) != row["subrho_vs_VOW"]:
            mism.append(("subrho_vs_VOW", row["n"], row["model"], row["B"], row["m"], row["d_bound"]))
        exp_tab = c["s"] * row["d"] if c["s"] >= 1 and row["model"] in ("MITM", "MITM_CAPPED") else None
        got_tab = row["log2_table_entries"]
        if (exp_tab is None) != (got_tab is None) or (exp_tab is not None and abs(exp_tab - got_tab) > 1e-9):
            mism.append(("log2_table_entries", row["n"], row["model"], row["B"], row["m"], exp_tab, got_tab))
        if c["out_of_domain"]:
            mism.append(("argmin_row_out_of_domain", row["n"], row["model"], row["B"], row["m"], row["d"]))
    res["D1_argmin_rows"] = {
        "rows": len(raw["argmin_rows"]),
        "max_abs_diff_bits": dict(maxdiff),
        "mismatches": mism,
    }

    # ---------------- D2/D3/D4/D7: full grid ----------------
    my_argmin = {}
    counts = {}
    flag_min_slack = defaultdict(lambda: math.inf)
    flag_fired = 0
    primary_cells = 0
    clamped_subrho = []
    clamped_min_margin = defaultdict(lambda: math.inf)
    for n in hm.DEGREES:
        N = hm.N_of(n)
        V = hm.vow(n)
        for bl in ("n", "n/2"):
            ds = grid(bound_value(n, bl))
            for model, b in COMBOS:
                lb = log2B(b)
                cnt = dict(cells=0, in_domain=0, out_of_domain=0, subrho_vs_VOW=0,
                           subrho_vs_PUB=0 if n == 131 else None)
                for m in MS:
                    best = None
                    for d in ds:
                        c = hm.cell(n, m, d, model, lb)
                        cnt["cells"] += 1
                        if c["out_of_domain"]:
                            cnt["out_of_domain"] += 1
                            if bl == "n" and model in PRIMARY:
                                # D7: clamp CALLS to 0 -> PROBE = o
                                tot = hm.log2sumexp2(c["o"], c["FILL"], c["LA"])
                                mg = tot - V
                                key = (n, model, b)
                                clamped_min_margin[key] = min(clamped_min_margin[key], mg)
                                if mg < 0 or (n == 131 and tot < hm.PUB_131):
                                    clamped_subrho.append((n, model, b, m, d, tot))
                            continue
                        cnt["in_domain"] += 1
                        if c["TOTAL"] < V:
                            cnt["subrho_vs_VOW"] += 1
                        if n == 131 and c["TOTAL"] < hm.PUB_131:
                            cnt["subrho_vs_PUB"] += 1
                        if bl == "n" and model in PRIMARY:
                            primary_cells += 1
                            slack = c["TOTAL"] - (N / 2 - 2.0)
                            flag_min_slack[n] = min(flag_min_slack[n], slack)
                            if slack < 0:
                                flag_fired += 1
                        if best is None or c["TOTAL"] < best[0] - 1e-12:
                            best = (c["TOTAL"], d, 1)
                        elif abs(c["TOTAL"] - best[0]) <= 1e-12:
                            best = (best[0], best[1], best[2] + 1)
                    my_argmin[(n, model, b, m, bl)] = best
                counts[(n, model, b, bl)] = cnt

    # D2 compare
    d2_maxdiff = 0.0
    d2_dmismatch = []
    d2_missing = []
    for row in raw["argmin_rows"]:
        key = (row["n"], row["model"], row["B"], row["m"], row["d_bound"])
        best = my_argmin.get(key)
        if best is None:
            d2_missing.append(key)
            continue
        d2_maxdiff = max(d2_maxdiff, abs(best[0] - row["TOTAL"]))
        if best[2] == 1 and abs(best[1] - row["d"]) > 1e-9:
            d2_dmismatch.append((key, best[1], row["d"]))
    res["D2_grid_argmin"] = {
        "rows_compared": len(raw["argmin_rows"]) - len(d2_missing),
        "max_abs_TOTAL_diff_bits": d2_maxdiff,
        "unique_argmin_d_mismatches": d2_dmismatch,
        "rows_without_in_domain_cell": d2_missing,
    }

    # D3 compare
    d3_mism = []
    for row in raw["cell_counts"]:
        key = (row["n"], row["model"], row["B"], row["d_bound"])
        mine = counts[key]
        for f in ("cells", "in_domain", "out_of_domain", "subrho_vs_VOW", "subrho_vs_PUB"):
            if mine[f] != row[f]:
                d3_mism.append((key, f, mine[f], row[f]))
        if row["primary"] != (row["model"] in PRIMARY):
            d3_mism.append((key, "primary", row["model"] in PRIMARY, row["primary"]))
    tot_in = sum(v["in_domain"] for k, v in counts.items() if k[1] in PRIMARY and k[3] == "n")
    tot_out = sum(v["out_of_domain"] for k, v in counts.items() if k[1] in PRIMARY and k[3] == "n")
    tot_sub = sum(v["subrho_vs_VOW"] for k, v in counts.items() if k[1] in PRIMARY)
    tot_sub_pub = sum((v["subrho_vs_PUB"] or 0) for k, v in counts.items() if k[1] in PRIMARY)
    free_sub = {f"{k[0]}|{k[3]}": v["subrho_vs_VOW"] for k, v in counts.items() if k[1] == "FREE"}
    res["D3_cell_counts"] = {
        "rows_compared": len(raw["cell_counts"]),
        "mismatches": d3_mism,
        "primary_in_domain_bound_n": tot_in,
        "primary_out_of_domain_bound_n": tot_out,
        "primary_subrho_vs_VOW_both_bounds": tot_sub,
        "primary_subrho_vs_PUB_131_both_bounds": tot_sub_pub,
        "raw_primary_subrho_totals": raw["primary_subrho_totals"],
        "FREE_control_subrho_vs_VOW": free_sub,
    }
    # OOD by degree/model vs raw (bound n)
    ood_mism = []
    for k, v in raw["out_of_domain_counts_by_degree_model"].items():
        n_s, model = k.split("|")
        n = int(n_s)
        if model == "MITM_CAPPED":
            mine = sum(counts[(n, model, b, "n")]["out_of_domain"] for b in BUDGETS)
        else:
            mine = counts[(n, model, "unlimited", "n")]["out_of_domain"]
        if mine != v:
            ood_mism.append((k, mine, v))
    res["D3_cell_counts"]["out_of_domain_by_degree_model_mismatches"] = ood_mism

    # D4
    raw_slack = raw["generic_lower_bound_flag"]["min_slack_bits_by_degree"]
    res["D4_generic_flag"] = {
        "primary_cells_checked": primary_cells,
        "raw_cells_checked": raw["generic_lower_bound_flag"]["cells_checked"],
        "fired_in_domain": flag_fired,
        "min_slack_by_degree": {str(k): v for k, v in flag_min_slack.items()},
        "max_abs_diff_vs_raw_slack": max(abs(flag_min_slack[n] - raw_slack[str(n)]) for n in hm.DEGREES),
    }

    # D7
    res["D7_domain_exclusion_clamped"] = {
        "rule": "CALLS < 0 cells re-costed with PROBE = o (one oracle call), bound n, primary models",
        "would_be_subrho_count": len(clamped_subrho),
        "examples": clamped_subrho[:10],
        "min_clamped_margin_vs_VOW_by_degree": {
            str(n): min(v for k, v in clamped_min_margin.items() if k[0] == n) for n in hm.DEGREES},
    }

    # ---------------- D5/D6: minima ----------------
    E2 = {97: 16.54, 109: 17.69, 131: 19.12, 163: 21.55, 191: 23.55, 233: 26.22,
          239: 26.55, 283: 29.00, 409: 35.49, 571: 42.70}

    def cont_min(n, m, model, b):
        """Minimum TOTAL over real d in [1, n] with CALLS >= 0 and the model's s law."""
        lb = log2B(b)
        N = hm.N_of(n)
        L = hm.L_of(m)
        dmax = min(float(n), (N + L) / (m - 1))  # CALLS >= 0 <=> d <= (N+L)/(m-1)
        if dmax < 1.0:
            return None

        def f(d):
            return hm.cell(n, m, d, model, lb)["TOTAL"]
        # fine scan then golden refinement inside each s-piece (s law piecewise in d)
        step = 0.001
        best = (math.inf, None)
        k = 0
        while True:
            d = 1.0 + step * k
            if d > dmax:
                break
            v = f(d)
            if v < best[0]:
                best = (v, d)
            k += 1
        v = f(dmax)
        if v < best[0]:
            best = (v, dmax)
        lo, hi = max(1.0, best[1] - step), min(dmax, best[1] + step)
        g = (math.sqrt(5) - 1) / 2
        a, bb = lo, hi
        for _ in range(80):
            c1 = bb - g * (bb - a)
            c2 = a + g * (bb - a)
            if f(c1) < f(c2):
                bb = c2
            else:
                a = c1
        dm = (a + bb) / 2
        if f(dm) < best[0]:
            best = (f(dm), dm)
        return best

    d5 = {}
    d6_rows = []
    worst_excess = (0.0, None)
    for n in hm.DEGREES:
        V = hm.vow(n)
        grid_best = None
        cont_best = None
        for model, b in COMBOS:
            if model not in PRIMARY:
                continue
            for m in MS:
                g_ = my_argmin[(n, model, b, m, "n")]
                cm = cont_min(n, m, model, b)
                if g_ is not None and cm is not None:
                    exc = g_[0] - cm[0]
                    d6_rows.append(dict(n=n, model=model, B=b, m=m, grid_TOTAL=g_[0], grid_d=g_[1],
                                        cont_TOTAL=cm[0], cont_d=cm[1], excess_bits=exc))
                    if exc > worst_excess[0]:
                        worst_excess = (exc, d6_rows[-1])
                if g_ is not None and (grid_best is None or g_[0] < grid_best[0]):
                    grid_best = (g_[0], model, b, m, g_[1])
                if cm is not None and (cont_best is None or cm[0] < cont_best[0]):
                    cont_best = (cm[0], model, b, m, cm[1])
        raw_pm = raw["per_degree_minimum"][str(n)]["n"]["primary_min"]
        d5[str(n)] = dict(
            mine_grid_min_TOTAL=grid_best[0], mine_grid_argmin=dict(model=grid_best[1], B=grid_best[2], m=grid_best[3], d=grid_best[4]),
            mine_grid_margin_vs_VOW=grid_best[0] - V,
            raw_primary_min_TOTAL=raw_pm["TOTAL"], raw_margin_vs_VOW=raw_pm["margin_vs_VOW_bits"],
            diff_grid_vs_raw=grid_best[0] - raw_pm["TOTAL"],
            mine_continuous_min_TOTAL=cont_best[0], mine_continuous_margin_vs_VOW=cont_best[0] - V,
            continuous_argmin=dict(model=cont_best[1], B=cont_best[2], m=cont_best[3], d=cont_best[4]),
            E2=E2[n], continuous_minus_E2=cont_best[0] - V - E2[n], grid_minus_E2=grid_best[0] - V - E2[n],
            margin_vs_PUB_continuous=(cont_best[0] - hm.PUB_131) if n == 131 else None,
        )
    res["D5_per_degree_minimum"] = d5
    exc_primary_min = [r for r in d6_rows]
    res["D6_grid_discretisation"] = {
        "rows": len(d6_rows),
        "max_excess_bits_any_row": worst_excess[0],
        "worst_row": worst_excess[1],
        "rows_with_excess_over_0_1_bit": sum(1 for r in d6_rows if r["excess_bits"] > 0.1),
        "rows_with_excess_over_0_5_bit": sum(1 for r in d6_rows if r["excess_bits"] > 0.5),
        "min_continuous_margin_vs_VOW_any_primary_row": min(r["cont_TOTAL"] - hm.vow(r["n"]) for r in d6_rows),
    }
    out = HERE / "jv1_diff_primary_output.json"
    out.write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k not in ("D5_per_degree_minimum",)}, indent=1, default=str)[:6000])
    for n, v in d5.items():
        print(n, "grid_min %.4f raw %.4f diff %.2e | margin grid %.3f cont %.3f E2 %.2f cont-E2 %+.3f | argmin %s"
              % (v["mine_grid_min_TOTAL"], v["raw_primary_min_TOTAL"], v["diff_grid_vs_raw"],
                 v["mine_grid_margin_vs_VOW"], v["mine_continuous_margin_vs_VOW"], v["E2"],
                 v["continuous_minus_E2"], v["continuous_argmin"]))


if __name__ == "__main__":
    main()
