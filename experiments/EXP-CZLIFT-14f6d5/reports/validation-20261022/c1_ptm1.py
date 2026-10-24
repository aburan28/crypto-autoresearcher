#!/usr/bin/env python3
"""Control C1 and proves-too-much object PTM-1 (TASK-20261022-a846f4).

C1  "The rank-7 overlap curve must reproduce its lane-1 counts exactly":
    compares the 382623908456a1 entry (counts, primes, coverage table, h_half)
    of each EXP-CZLIFT-14f6d5 run with the lane-1 (EXP-CZLIFT-a255fc) run of
    the same hmax, and hashes the lane-1 raw results against their receipts.
PTM-1 "11a1 run through the same counter": loads the frozen lane-1 library the
    driver uses (experiments/EXP-CZLIFT-a255fc/implementation/run.py, hash
    checked first) and runs its measure_curve on 11a1 = [0,-1,1,-10,-20]
    (E(Q) = Z/5, torsion count 5 including O) at hmax = 300000 with the
    driver's 16 primes.  Expected failure signature: growth of N_E(H) beyond 5.
Usage: c1_ptm1.py REPO OUT_JSON
"""
import hashlib
import importlib.util
import json
import sys
import time

LIB = "experiments/EXP-CZLIFT-a255fc/implementation/run.py"
LIB_SHA = "d8de24d0e4e1745a963ade212d04daa0370935af1f8b37750ddfd8ddde9656ae"
PAIRS = {"RUN-CZLIFT-ca7450": "RUN-CZLIFT-74f172", "RUN-CZLIFT-b1dce4": "RUN-CZLIFT-490b33"}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    repo, out = sys.argv[1], sys.argv[2]
    res = {"C1": {}, "PTM1": {}}
    for mine, lane1 in PAIRS.items():
        a = json.load(open(f"{repo}/experiments/EXP-CZLIFT-14f6d5/runs/{mine}/raw-result.json"))
        lp = f"{repo}/experiments/EXP-CZLIFT-a255fc/runs/{lane1}/raw-result.json"
        b = json.load(open(lp))
        er = json.load(open(f"{repo}/experiments/EXP-CZLIFT-a255fc/runs/{lane1}/execution-receipt.json"))
        ca = next(c for c in a["raw"]["curves"] if c["label"] == "382623908456a1")
        cb = next(c for c in b["raw"]["curves"] if c["label"] == "382623908456a1")
        res["C1"][mine] = {
            "lane1_run": lane1,
            "lane1_raw_sha256": sha(lp),
            "lane1_raw_sha256_in_its_receipt": er.get("artifact_sha256", {}).get("raw-result.json"),
            "same_hmax": ca["hmax"] == cb["hmax"],
            **{f"equal_{k}": ca[k] == cb[k] for k in ("ainvs", "counts", "primes", "coverage", "h_half", "discriminant", "points_sample")},
        }
    # PTM-1 through the producer's counter
    lib_path = f"{repo}/{LIB}"
    res["PTM1"]["library_sha256"] = sha(lib_path)
    res["PTM1"]["library_sha256_matches_trial_plan"] = res["PTM1"]["library_sha256"] == LIB_SHA
    spec = importlib.util.spec_from_file_location("czlift_lane1_ptm", lib_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    primes = mod.primes_for_coverage(101, 20_000, 16)
    t0 = time.time()
    cv = mod.measure_curve("11a1", [0, -1, 1, -10, -20], 0, 11, hmax=300_000, primes=primes, twists=[], twist_hmax=30_000)
    res["PTM1"]["seconds"] = round(time.time() - t0, 1)
    res["PTM1"]["counts"] = cv["counts"]
    res["PTM1"]["points_sample"] = cv["points_sample"]
    res["PTM1"]["torsion_count_incl_O"] = 5
    cnt = {int(k): v for k, v in cv["counts"].items()}
    hs = sorted(cnt)
    res["PTM1"]["max_count"] = max(cnt.values())
    res["PTM1"]["growth_beyond_torsion"] = any(v > 5 for v in cnt.values())
    res["PTM1"]["nondecreasing"] = all(cnt[hs[i]] <= cnt[hs[i + 1]] for i in range(len(hs) - 1))
    res["PTM1"]["first_H_at_torsion_count"] = next((h for h in hs if cnt[h] == 5), None)
    res["PTM1"]["coverage_cells_n_ge_30"] = sum(1 for c in cv["coverage"] if c["n_points"] >= 30)
    res["PTM1"]["h_half"] = cv["h_half"]
    res["PTM1"]["growth_slope"] = cv["growth_slope"]
    summ = mod.summarize([cv])
    res["PTM1"]["summarize_on_11a1_alone"] = {k: summ[k] for k in ("coverage_cells", "coverage_ratio_median", "growth_slopes", "h_half_scaling")}
    json.dump(res, open(out, "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
