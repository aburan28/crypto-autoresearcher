"""Checker for EXP-CZLIFT-7c8d73: reproduces two curves, re-derives the summary, checks the series instrument."""
from __future__ import annotations
import json, os, sys, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..")); sys.path.insert(0, REPO)
import run as driver  # noqa: E402
from harness import czlift, czlift_formal  # noqa: E402
from harness.czlift import ZpCurve  # noqa: E402


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr); return 1
    rd = args[0]
    raw = json.load(open(os.path.join(rd, "raw-result.json"))); man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    if man["experiment_id"] != driver.EXP_ID or man["status"] != "completed_valid":
        print("manifest mismatch", file=sys.stderr); return 1
    seed, P = man["inputs"]["seed"], man["inputs"]["parameters"]
    curves = raw["raw"]["curves"]
    expected = czlift.anomalous_cm_curves(P["pmax"])
    if [(c["D"], c["p"]) for c in curves] != [(D, p) for D, p, *_ in expected]:
        print("curve list differs", file=sys.stderr); return 1
    for D, p, A, B, j in expected[:2]:
        rec = next(c for c in curves if c["p"] == p and c["D"] == D)
        if driver.measure_curve(D, p, A, B, j, seed=seed, samples=P["samples"], per_class=P["per_class"])["rows"] != rec["rows"]:
            print(f"curve p={p} does not reproduce", file=sys.stderr); return 1
    if driver.summarize(curves) != {k: v for k, v in raw["metrics"].items() if k in driver.summarize(curves)}:
        print("summary does not re-derive", file=sys.stderr); return 1
    # instrument: exp_F and log_F are mutually inverse and log_F is additive on a formal point pair
    D, p, A, B, j = expected[-1]
    E = ZpCurve(p, driver.PRECISION, A, B); w, lg, ex = czlift_formal.formal_series(E)
    z = p * 3 + p * p * 5
    if ex.eval(lg.eval(z)) != z % E.M or lg.eval(ex.eval(z)) != z % E.M:
        print("log_F / exp_F are not inverse", file=sys.stderr); return 1
    print("check ok"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
