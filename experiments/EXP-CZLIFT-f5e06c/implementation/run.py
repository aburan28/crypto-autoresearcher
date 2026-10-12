"""EXP-CZLIFT-f5e06c driver: medium-scale replication of EXP-CZLIFT-17b7eb and EXP-CZLIFT-ae0a13.

Reuses the two lane-1 drivers' measure_curve and summarize functions
UNMODIFIED (imported from their implementation directories) on curves
sampled between 10^4 and 10^5 by harness/czlift_medium.py: the anomalous CM
arm (Smart against the canonical lift, j-distance rule) and the torsion-section
arms (CM-canonical and random-integer lifts). Both summaries are recorded
under their original metric names, prefixed by arm. Observations only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness import czlift_medium  # noqa: E402
from harness.czlift_run import write_run_record  # noqa: E402

EXP_ID = "EXP-CZLIFT-f5e06c"
SRC_A = os.path.join(REPO, "experiments", "EXP-CZLIFT-17b7eb", "implementation", "run.py")
SRC_B = os.path.join(REPO, "experiments", "EXP-CZLIFT-ae0a13", "implementation", "run.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(seed: int, pmin: int, pmax: int, n_anom: int, n_cm: int, n_rand: int, samples_a: int, samples_b: int):
    A = load(SRC_A, "czlift_lane1_a")
    B = load(SRC_B, "czlift_lane1_b")
    rng = random.Random(seed)
    anom = czlift_medium.sample_anomalous(pmin, pmax, n_anom, rng)
    cm = czlift_medium.sample_cm_prime_subgroup(pmin, pmax, n_cm, 101, rng)
    rand = czlift_medium.sample_random_prime_subgroup(pmin, pmax, n_rand, 101, rng)
    curves_a = [A.measure_curve(D, p, Aa, Bb, j, seed=seed, samples=samples_a, per_class=1) for D, p, Aa, Bb, j in anom]
    curves_b = [B.measure_curve("cm_canonical", p, Aa, Bb, N, n, seed=seed, samples=samples_b, label=f"D={D}") for D, p, Aa, Bb, N, n in cm]
    curves_b += [B.measure_curve("random_naive", p, a, b, N, n, seed=seed, samples=samples_b, label="random") for p, a, b, N, n in rand]
    ma = A.summarize(curves_a)
    mb = B.summarize(curves_b)
    metrics = {"anomalous": {k: v for k, v in ma.items() if k not in ("by_class", "degenerate_by_section")},
               "anomalous_by_class": ma["by_class"], "anomalous_degenerate_by_section": ma["degenerate_by_section"],
               "torsion": {k: v for k, v in mb.items() if k != "sections"}, "torsion_sections": mb["sections"],
               "seed": seed, "pmin": pmin, "pmax": pmax, "curves_anomalous": len(anom), "curves_cm": len(cm), "curves_random": len(rand),
               "anomalous_curve_list": [(D, p) for D, p, *_ in anom]}
    return metrics, {"curves_anomalous": curves_a, "curves_torsion": curves_b}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True); ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--pmin", type=int, default=10_000); ap.add_argument("--pmax", type=int, default=100_000)
    ap.add_argument("--n-anom", type=int, default=24); ap.add_argument("--n-cm", type=int, default=16); ap.add_argument("--n-rand", type=int, default=8)
    ap.add_argument("--samples-a", type=int, default=8); ap.add_argument("--samples-b", type=int, default=12)
    a = ap.parse_args(argv)
    t0 = time.time()
    m, raw = build(a.seed, a.pmin, a.pmax, a.n_anom, a.n_cm, a.n_rand, a.samples_a, a.samples_b)
    t1 = time.time()
    sources = [os.path.abspath(__file__), SRC_A, SRC_B, os.path.join(REPO, "harness", "czlift.py"), os.path.join(REPO, "harness", "czlift_medium.py"),
               os.path.join(REPO, "harness", "czlift_run.py"), os.path.join(REPO, "harness", "toycurve.py")]
    write_run_record(a.run_dir, run_id=a.run_id, exp_id=EXP_ID, status="completed_valid", command=[sys.executable] + sys.argv, sources=sources, seed=a.seed,
                     parameters={"pmin": a.pmin, "pmax": a.pmax, "n_anom": a.n_anom, "n_cm": a.n_cm, "n_rand": a.n_rand, "samples_a": a.samples_a, "samples_b": a.samples_b, "tier": "medium"},
                     metrics=m, raw=raw, started=t0, finished=t1, stdout=json.dumps({"anomalous": m["anomalous"], "torsion": m["torsion"]}, indent=1) + "\n")
    print(json.dumps({"anomalous": m["anomalous"], "torsion": m["torsion"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
