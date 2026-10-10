"""EXP-CZLIFT-14f6d5 driver: the rank ladder extended with RETRIEVED high-rank curves.

Reuses the EXP-CZLIFT-a255fc driver UNMODIFIED (imported from its
implementation directory) with the curve list replaced by equations retrieved
on 2026-10-09 from Dujella's rank-history pages (provenance retrieved, URLs
below). LMFDB's elliptic-curve database (conductor <= 500000) holds no curve
of rank 8 (the API query returned an empty data array on 2026-10-09), so the
retrieved records are the classical rank-record curves, whose stated ranks
are LOWER BOUNDS (the pages list 8 and 9 independent points):

  rank >= 8  Grunewald-Zimmert 1977   https://web.math.pmf.unizg.hr/~duje/tors/rk8.html
             y^2 + xy + y = x^3 - x^2 - 6494556985832 x + 6351402068900282539
  rank >= 9  Brumer-Kramer 1977       https://web.math.pmf.unizg.hr/~duje/tors/rk9.html
             y^2 + xy + y = x^3 - x^2 - 1608154463 x + 25555312501831

The rank-7 minimal-conductor curve of the lane-1 ladder is kept as the
overlap control. Observations only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from harness.czlift_run import write_run_record  # noqa: E402

EXP_ID = "EXP-CZLIFT-14f6d5"
SRC_C = os.path.join(REPO, "experiments", "EXP-CZLIFT-a255fc", "implementation", "run.py")
CURVES = [
    ("382623908456a1", [0, 0, 0, -10012, 346900], 7, 382623908456),
    ("grunewald-zimmert-1977-rank-ge-8", [1, -1, 1, -6494556985832, 6351402068900282539], 8, None),
    ("brumer-kramer-1977-rank-ge-9", [1, -1, 1, -1608154463, 25555312501831], 9, None),
]


def load_c():
    spec = importlib.util.spec_from_file_location("czlift_lane1_c", SRC_C)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.CURVES = list(CURVES)
    return mod


def build(hmax: int, n_primes: int):
    Cm = load_c()
    metrics, raw = Cm.build(hmax, 30_000, 0, n_primes)
    metrics["retrieved_sources"] = {"grunewald-zimmert-1977-rank-ge-8": "https://web.math.pmf.unizg.hr/~duje/tors/rk8.html",
                                    "brumer-kramer-1977-rank-ge-9": "https://web.math.pmf.unizg.hr/~duje/tors/rk9.html",
                                    "lmfdb_rank8_query": "https://www.lmfdb.org/api/ec_curvedata/?rank=8 returned an empty data array on 2026-10-09"}
    metrics["rank_label_note"] = "ranks 8 and 9 are lower bounds as stated by the source pages; rank 7 is the lane-1 minimal-conductor label (recalled)"
    return metrics, raw


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True); ap.add_argument("--run-id", required=True)
    ap.add_argument("--hmax", type=int, default=100_000); ap.add_argument("--n-primes", type=int, default=16)
    a = ap.parse_args(argv)
    t0 = time.time(); m, raw = build(a.hmax, a.n_primes); t1 = time.time()
    write_run_record(a.run_dir, run_id=a.run_id, exp_id=EXP_ID, status="completed_valid", command=[sys.executable] + sys.argv,
                     sources=[os.path.abspath(__file__), SRC_C, os.path.join(REPO, "harness", "czlift_run.py")], seed=None,
                     parameters={"hmax": a.hmax, "n_primes": a.n_primes, "tier": "toy", "deterministic": True},
                     metrics=m, raw=raw, started=t0, finished=t1, curve_id="retrieved-rank-record-ladder", stdout=json.dumps(m, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in m.items() if k not in ("growth_slopes", "h_half_scaling")})); print(json.dumps(m["growth_slopes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
