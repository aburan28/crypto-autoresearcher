"""Checker for EXP-CZLIFT-8c50ea: verifies every sample point exactly in Z[theta], re-counts one curve at small height, re-derives the summary."""
from __future__ import annotations
import json, os, sys, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..")); sys.path.insert(0, REPO)
import run as driver  # noqa: E402
from harness import czlift_cubic as C  # noqa: E402


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr); return 1
    rd = args[0]
    raw = json.load(open(os.path.join(rd, "raw-result.json"))); man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    if man["experiment_id"] != driver.EXP_ID or man["status"] != "completed_valid":
        print("manifest mismatch", file=sys.stderr); return 1
    curves = raw["raw"]["curves"]
    if [c["label"] for c in curves] != [c[0] for c in driver.CURVES]:
        print("curve list differs", file=sys.stderr); return 1
    for cv in curves:
        a1, a2, a3, a4, a6 = cv["ainvs"]
        b2 = a1 * a1 + 4 * a2; b4 = 2 * a4 + a1 * a3; b6 = a3 * a3 + 4 * a6
        for alpha, d, gamma in cv["points_sample"]:
            if C.mul(tuple(gamma), tuple(gamma)) != C.g_value(tuple(alpha), d, b2, b4, b6):
                print(f"sample point on {cv['label']} is not on the curve over K", file=sys.stderr); return 1
        for cell in cv["coverage"]:
            if cell["distinct"] > cell["N_p"] or cell["distinct"] < 1:
                print("coverage cell out of range", file=sys.stderr); return 1
    cv = curves[1]
    fresh = driver.measure_curve(cv["label"], cv["ainvs"], cv["rank_recalled_over_Q"], hmax=4, dmax=min(2, cv["dmax"]), primes=[])
    # the recount at height 4 with dmax 2 must not exceed the recorded count at height 4 (recorded uses dmax >= 2)
    if fresh["counts_K"]["4"] > cv["counts_K"]["4"]:
        print("height-4 recount exceeds the recorded count", file=sys.stderr); return 1
    if driver.summarize(curves) != {k: raw["metrics"][k] for k in driver.summarize(curves)}:
        print("summary does not re-derive", file=sys.stderr); return 1
    print("check ok"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
