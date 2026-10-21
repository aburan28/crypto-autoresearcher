"""Prepare same-size random and small-x prime factor-base controls.

This retains every candidate x draw, accepted point, miss, exact membership
polynomial and setup receipt. It does not run an algebraic solver or ECDLP.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import random
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from crypto_autoresearcher.index_calculus.curve import Curve  # noqa: E402
from crypto_autoresearcher.index_calculus.factor_base import FactorBase  # noqa: E402
from tools.icperf_explicit_base import point_digest  # noqa: E402

FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"
SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"
SIZE = 475
SEED = 20261017


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace(curve: Curve, base: FactorBase, kind: str) -> list[dict]:
    """Reconstruct the exact deterministic draw stream, retaining misses."""
    events = []
    accepted = []
    if kind == "random":
        rng = random.Random(f"fb-random|{curve.p}|{curve.a}|{curve.b}|{SIZE}|{SEED}")
        seen = set()
        while len(accepted) < SIZE:
            x = rng.randrange(curve.p)
            if x in seen:
                events.append({"x": x, "status": "repeat"})
                continue
            seen.add(x)
            point = curve.lift_x(x)
            if point is None or point[1] == 0:
                events.append({"x": x, "status": "nonliftable"})
            else:
                events.append({"x": x, "status": "accepted"})
                accepted.append(point)
    elif kind == "small_x":
        for x in range(base.params["bound"]):
            point = curve.lift_x(x)
            if point is None or point[1] == 0:
                events.append({"x": x, "status": "nonliftable"})
            else:
                events.append({"x": x, "status": "accepted"})
                accepted.append(point)
    else:
        raise ValueError(kind)
    assert accepted == base.points and len(accepted) == SIZE
    return events


def prepare_one(curve: Curve, kind: str) -> dict:
    wall, cpu = time.perf_counter(), time.process_time()
    base = (FactorBase.random(curve, SIZE, SEED) if kind == "random"
            else FactorBase.small_x(curve, SIZE))
    constructor = {"wall_seconds": time.perf_counter() - wall,
                   "cpu_seconds": time.process_time() - cpu,
                   "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                                     (1 if sys.platform == "darwin" else 1024)}
    events = trace(curve, base, kind)
    poly = base.membership_poly()
    assert len(base) == SIZE and max(poly) == SIZE and len(poly) <= SIZE + 1
    assert all(sum(c * pow(point[0], e, curve.p) for e, c in poly.items()) % curve.p == 0
               for point in base.points)
    return {"kind": kind, "size": len(base), "parameters": base.params,
            "points": [list(point) for point in base.points],
            "point_sha256": point_digest(base.points),
            "draw_stream": events, "draw_count": len(events),
            "accepted_count": sum(event["status"] == "accepted" for event in events),
            "nonliftable_count": sum(event["status"] == "nonliftable" for event in events),
            "repeat_count": sum(event["status"] == "repeat" for event in events),
            "membership_coefficients": {str(e): c for e, c in poly.items()},
            "membership_degree": max(poly),
            "membership_nonzero_terms": len(poly),
            "constructor": constructor}


def build_record() -> dict:
    fixture, scan = json.loads(FIXTURE.read_bytes()), json.loads(SCAN.read_bytes())
    c = fixture["curve"]
    assert scan["curve"] == c and scan["selected_realized_size"] == SIZE
    selected = next(a for a in scan["attempts"]
                    if a["base_parameters"]["seed"] == scan["selected_seed"])
    curve = Curve(c["p"], c["a"], c["b"], c["order"])
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    wall, cpu = time.perf_counter(), time.process_time()
    controls = [prepare_one(curve, kind) for kind in ("random", "small_x")]
    coset_x = {point[0] for point in selected["points"]}
    for control in controls:
        control["x_overlap_with_coset"] = len(coset_x & {p[0] for p in control["points"]})
    return {"schema": "icperf-prime-475-controls-v1",
            "scope": "target-blind equal-realized-size control bases and exact membership inputs; no solver or ECDLP cost claim",
            "source_sha256": sha(Path(__file__)),
            "factor_base_source_sha256": sha(ROOT / "src/crypto_autoresearcher/index_calculus/factor_base.py"),
            "fixture_sha256": sha(FIXTURE), "scan_sha256": sha(SCAN),
            "curve": c, "size": SIZE, "random_seed": SEED,
            "coset_reference": {"selected_seed": scan["selected_seed"],
                                "point_sha256": scan["selected_point_sha256"],
                                "size": SIZE, "membership_degree": 896,
                                "membership_nonzero_terms": 2},
            "controls": controls,
            "preparation": {"started_at_utc": started,
                            "finished_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                            "wall_seconds": time.perf_counter() - wall,
                            "cpu_seconds": time.process_time() - cpu,
                            "platform": platform.platform(), "python_version": platform.python_version(),
                            "loadavg_end": list(os.getloadavg()),
                            "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                       capture_output=True, text=True, check=True).stdout.strip(),
                            "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                                                 capture_output=True, text=True, check=True).stdout.splitlines()}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = build_record()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"controls": [{"kind": row["kind"], "size": row["size"],
                                     "draws": row["draw_count"],
                                     "membership_terms": row["membership_nonzero_terms"]}
                                    for row in record["controls"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
