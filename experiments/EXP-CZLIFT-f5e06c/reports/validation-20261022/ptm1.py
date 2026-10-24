#!/usr/bin/env python3
"""PTM-1 proves-too-much control for EXP-CZLIFT-f5e06c (TASK-20261022-65e6c1).

Object: non-anomalous curves at primes in [10^4, 10^5], where Smart's map does not apply.
Known-false conclusion: the canonical-lift rule and the attack behave identically on them.
Expected failure signature: the anomaly check rejects the curve before any measurement;
acceptance invalidates the sampler.

Runs the producer's UNMODIFIED instrument (EXP-CZLIFT-17b7eb measure_curve, imported the way
EXP-CZLIFT-f5e06c/implementation/run.py imports it) and the f5e06c sampler's resolver on:
  O1  the quadratic twist (trace -1, #E = p + 2) of a sampled anomalous curve (same p, same j);
  O2  a sampled CM torsion-arm curve (non-anomalous, CM integral model);
  O3  a sampled random torsion-arm curve;
  O4  resolve_anomalous(D, p) on a CM pair (D, p) whose p is not a trace-1 norm.
Each object is run with assertions on (as in the frozen command) and, as a fragility probe,
in a child interpreter with -O (asserts stripped).
Writes nothing outside stdout.
"""
import json
import os
import subprocess
import sys
import traceback

ROOT = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "parent"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments", "EXP-CZLIFT-f5e06c", "implementation"))
import run as driver  # noqa: E402  (the f5e06c driver; imports nothing at module level that runs trials)
from harness import czlift_medium  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

A_mod = driver.load(driver.SRC_A, "ptm_lane1_a")
EXP = "experiments/EXP-CZLIFT-f5e06c"
raw = json.load(open(os.path.join(ROOT, EXP, "runs", "RUN-CZLIFT-032a92", "raw-result.json")))["raw"]

anom = next(c for c in raw["curves_anomalous"] if c["D"] == -67)
p = anom["p"]
nonres = next(t for t in range(2, p) if pow(t, (p - 1) // 2, p) == p - 1)
twist = (anom["D"], p, anom["A"] * nonres ** 2, anom["B"] * nonres ** 3, anom["j_cm"])
cmt = next(c for c in raw["curves_torsion"] if c["arm"] == "cm_canonical")
rnd = next(c for c in raw["curves_torsion"] if c["arm"] == "random_naive")
D_cm = int(cmt["label"].split("=")[1])
objects = {
    "O1_twist_of_anomalous": twist,
    "O2_cm_torsion_curve": (D_cm, cmt["p"], cmt["A"], cmt["B"], czlift_medium.czlift.CM_J[D_cm]),
    "O3_random_torsion_curve": (-11, rnd["p"], rnd["A"], rnd["B"], czlift_medium.czlift.CM_J[-11]),
}


def probe():
    res = {"asserts_enabled": __debug__}
    for name, (D, pp, A, B, j) in objects.items():
        n_pts = EllipticCurve(pp, A % pp, B % pp).order()
        r = {"D": D, "p": pp, "order": n_pts, "anomalous": n_pts == pp}
        try:
            out = A_mod.measure_curve(D, pp, A, B, j, seed=20261009, samples=8, per_class=1)
            r["outcome"] = "ACCEPTED"
            r["rows"] = len(out["rows"])
            r["row_sample"] = out["rows"][:2]
        except AssertionError as e:
            r["outcome"] = "rejected_by_anomaly_check"
            r["exception"] = f"AssertionError: {e}"
        except Exception as e:  # noqa: BLE001
            r["outcome"] = "failed_loudly_other"
            r["exception"] = f"{type(e).__name__}: {e}"
            r["where"] = traceback.extract_tb(e.__traceback__)[-1].name
        res[name] = r
    # O4: the sampler's resolver on a non-norm prime
    res["O4_resolve_anomalous_nonnorm"] = {
        "D": D_cm, "p": cmt["p"],
        "p_is_trace1_norm": any((1 + abs(D_cm) * v * v) == 4 * cmt["p"] for v in range(1, 2000)),
        "resolve_anomalous": czlift_medium.resolve_anomalous(D_cm, cmt["p"]),
    }
    # the sampler's candidate list: every candidate p is a trace-1 norm for its D
    cands = czlift_medium.anomalous_candidates(10_000, 100_000)
    res["sampler_candidates"] = {
        "n": len(cands),
        "all_trace1_norm": all(any(1 + abs(D) * v * v == 4 * pp for v in range(1, 2000, 2)) for D, pp in cands),
        "discriminants": sorted({D for D, _ in cands}),
    }
    return res


if MODE == "child":
    json.dump(probe(), sys.stdout, default=str)
    sys.exit(0)

parent = probe()
child = subprocess.run([sys.executable, "-O", os.path.abspath(__file__), ROOT, "child"],
                       capture_output=True, text=True)
out = {"asserts_on": parent,
       "asserts_stripped_python_-O": json.loads(child.stdout) if child.returncode == 0 else
       {"returncode": child.returncode, "stderr": child.stderr[-2000:]}}
json.dump(out, sys.stdout, indent=1, default=str)
print()
