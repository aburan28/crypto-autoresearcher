"""J2 recomputation (validator TASK-20261022-67902e, phase 2), written before reading check.py.

Recomputes every frozen metric of EXP-CZLIFT-ed8113 from raw-result.json["raw"] alone and
compares with raw-result.json["metrics"], manifest.yaml result.metrics and stdout.log.
Usage: python3 j2_recompute.py RUN_DIR [RUN_DIR ...] > j2_recompute.json
"""
import json
import math
import re
import sys
from pathlib import Path

PRIMES = [101, 211, 401, 809, 1601, 3203, 6421, 12809]
BOUND = 6


def manifest_metrics(path):
    """result.metrics block of manifest.yaml, loaded with PyYAML safe_load."""
    import yaml
    return yaml.safe_load(Path(path).read_text())["run"]["result"]["metrics"]


def cp_upper(k, n, conf=0.95):
    """One-sided exact (Clopper-Pearson) upper bound by bisection on the binomial CDF."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(k + 1))
        if cdf > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi


def recompute(run_dir):
    d = json.loads((Path(run_dir) / "raw-result.json").read_text())
    raw, rec = d["raw"], d["metrics"]
    cells = raw["cells"]
    out = {"run_dir": str(run_dir), "checks": {}, "recomputed": {}, "recorded_raw_metrics": rec}
    ck = out["checks"]
    # coverage of the frozen grid
    grid = sorted((c["p"], c["r"]) for c in cells)
    ck["grid_is_8_primes_x_r23_no_dups"] = grid == sorted((p, r) for p in PRIMES for r in (2, 3))
    ck["trials_per_cell_all_100"] = all(c["trials"] == 100 for c in cells)
    ck["valid_le_trials"] = all(0 <= c["valid"] <= c["trials"] for c in cells)
    ck["excluded_singular_per_cell"] = {f"{c['p']},{c['r']}": c["trials"] - c["valid"] for c in cells}
    ck["dependent_le_valid"] = all(0 <= c["dependent"] <= c["valid"] for c in cells)
    ck["cell_rate_eq_dependent_over_valid"] = all(
        abs(c["dependence_rate"] - (c["dependent"] / c["valid"] if c["valid"] else 0.0)) < 1e-15 for c in cells)
    ck["relations_count_eq_dependent"] = all(len(c["relations"]) == c["dependent"] for c in cells)
    ck["relations_have_length_r"] = all(all(len(m) == c["r"] for m in c["relations"]) for c in cells)
    ck["relations_within_bound"] = all(all(max(abs(v) for v in m) <= BOUND and any(m) for m in c["relations"])
                                       for c in cells)
    ck["log_p_matches"] = all(abs(c["log_p"] - math.log(c["p"])) < 1e-12 for c in cells)
    # frozen metrics
    R = out["recomputed"]
    R["cells"] = len(cells)
    R["valid_trials_total"] = sum(c["valid"] for c in cells)
    R["dependent_total"] = sum(c["dependent"] for c in cells)
    R["dependence_rate_overall"] = R["dependent_total"] / R["valid_trials_total"]
    R["dependence_rate_by_r"] = {
        str(r): sum(c["dependent"] for c in cells if c["r"] == r) / sum(c["valid"] for c in cells if c["r"] == r)
        for r in (2, 3)}
    R["controls"] = len(raw["controls"])
    R["control_detection_rate"] = sum(bool(x) for x in raw["controls"]) / len(raw["controls"])
    # height ratio per prime: three candidate definitions (the specification does not fix one)
    hr_pooled, hr_r2, hr_r3 = {}, {}, {}
    for p in PRIMES:
        cs = {c["r"]: c for c in cells if c["p"] == p}
        lp = math.log(p)
        hr_r2[str(p)] = cs[2]["mean_log_height_point"] / lp
        hr_r3[str(p)] = cs[3]["mean_log_height_point"] / lp
        # pooled over points: r=2 cell contributes 2*valid points, r=3 cell 3*valid points
        n2, n3 = 2 * cs[2]["valid"], 3 * cs[3]["valid"]
        hr_pooled[str(p)] = (cs[2]["mean_log_height_point"] * n2 + cs[3]["mean_log_height_point"] * n3) / (n2 + n3) / lp
    R["height_ratio_candidates"] = {"r2_cell_only": hr_r2, "r3_cell_only": hr_r3, "pooled_over_points": hr_pooled,
                                    "mean_of_cells": {k: (hr_r2[k] + hr_r3[k]) / 2 for k in hr_r2}}
    # comparisons with the recorded metrics
    cmp = out["comparison_raw_metrics"] = {}
    for k in ("cells", "valid_trials_total", "dependent_total", "controls"):
        cmp[k] = (R[k], rec[k], R[k] == rec[k])
    cmp["dependence_rate_overall"] = (R["dependence_rate_overall"], rec["dependence_rate_overall"],
                                      R["dependence_rate_overall"] == rec["dependence_rate_overall"])
    cmp["dependence_rate_by_r"] = {r: (R["dependence_rate_by_r"][r], rec["dependence_rate_by_r"][r],
                                       R["dependence_rate_by_r"][r] == rec["dependence_rate_by_r"][r]) for r in ("2", "3")}
    cmp["control_detection_rate"] = (R["control_detection_rate"], rec["control_detection_rate"],
                                     R["control_detection_rate"] == rec["control_detection_rate"])
    cmp["relation_bound"] = (BOUND, rec["relation_bound"], BOUND == rec["relation_bound"])
    cmp["primes"] = rec["primes"] == PRIMES
    hrm = {}
    for name, cand in R["height_ratio_candidates"].items():
        hrm[name] = all(round(cand[p], 4) == rec["height_ratio_point_over_log_p"][p] for p in cand)
    cmp["height_ratio_definition_matching_recorded_4dp"] = hrm
    cmp["height_ratio_recorded"] = rec["height_ratio_point_over_log_p"]
    # manifest and stdout agree with raw metrics
    mm = manifest_metrics(Path(run_dir) / "manifest.yaml")
    so = json.loads((Path(run_dir) / "stdout.log").read_text())
    def norm(x):
        return json.loads(json.dumps(x, sort_keys=True))
    rec_n = norm(rec)
    out["manifest_metrics_equal_raw_metrics"] = norm(mm) == rec_n
    out["stdout_metrics_equal_raw_metrics"] = norm(so) == rec_n
    if norm(mm) != rec_n:
        out["manifest_vs_raw_diff"] = {k: (mm.get(k), rec.get(k)) for k in set(mm) | set(rec) if norm(mm.get(k)) != norm(rec.get(k))}
    # frozen criteria
    k, n = R["dependent_total"], R["valid_trials_total"]
    out["criteria_this_seed"] = {
        "success_part": R["dependence_rate_overall"] <= 0.002 and R["control_detection_rate"] == 1.0,
        "falsification_part": R["dependence_rate_overall"] > 0.01 and R["control_detection_rate"] == 1.0,
        "invalidation_control_rate_lt_1": R["control_detection_rate"] < 1.0,
        "invalidation_relation_outside_bound": not ck["relations_within_bound"],
        "preregistered_point_prediction_0_of_1600": k == 0 and n == 1600,
        "one_sided_95_upper_bound": cp_upper(k, n),
    }
    out["dependent_cells"] = [{"p": c["p"], "r": c["r"], "relations": c["relations"]} for c in cells if c["dependent"]]
    return out


if __name__ == "__main__":
    res = [recompute(a) for a in sys.argv[1:]]
    print(json.dumps(res, indent=1))
