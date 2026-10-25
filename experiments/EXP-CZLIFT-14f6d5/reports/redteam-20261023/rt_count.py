"""Positive control for the red-team counter: re-enumerate the three run curves to H = 3e5
and compare every grid count with raw-result.json of RUN-CZLIFT-b1dce4 (read by key).
Writes rt_count_output.json (counts + the affine (a, d, c) lists, c >= 0)."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rt_lib as L

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RAW = os.path.join(REPO, "experiments/EXP-CZLIFT-14f6d5/runs/RUN-CZLIFT-b1dce4/raw-result.json")
GRID = [10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000]

raw = json.load(open(RAW))["raw"]["curves"]
out = {"hmax": 300000, "curves": {}}
for cv in raw:
    t0 = time.time()
    pts = L.enumerate_points(cv["ainvs"], 300000)
    cnt = L.counts_from_points(pts, GRID)
    rec = {int(k): v for k, v in cv["counts"].items()}
    out["curves"][cv["label"]] = {
        "ainvs": cv["ainvs"], "discriminant_mine": L.discriminant(cv["ainvs"]), "discriminant_recorded": cv["discriminant"],
        "counts_mine": cnt, "counts_recorded": rec, "match": all(cnt[h] == rec[h] for h in GRID),
        "points_adc": pts, "seconds": round(time.time() - t0, 1)}
    print(cv["label"], "match", out["curves"][cv["label"]]["match"], cnt, round(time.time() - t0, 1), "s", flush=True)
json.dump(out, open(os.path.join(HERE, "rt_count_output.json"), "w"))
