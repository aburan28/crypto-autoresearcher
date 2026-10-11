"""Frozen F_89 coordinate-pair census. Invoke through trial-plan.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

P, A, B = 89, 1, 1
EXPERIMENT_ID = "EXP-ECTD-97777a"
RUN_ID = "RUN-ECTD-63f478"


def add(u, v):
    if u is None:
        return v
    if v is None:
        return u
    x1, y1 = u
    x2, y2 = v
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if u == v:
        slope = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % P, -1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    return x3, (slope * (x1 - x3) - y1) % P


def points():
    return [(x, y) for x in range(P) for y in range(P)
            if (y * y - x**3 - A * x - B) % P == 0]


def permuted_labels():
    values = list(range(P))
    state = 5140517
    for i in range(P - 1, 0, -1):
        state = (1103515245 * state + 12345) % (2**31)
        j = state % (i + 1)
        values[i], values[j] = values[j], values[i]
    return values


def census():
    prime = all(P % q for q in range(2, int(P**0.5) + 1))
    discriminant = (-16 * (4 * A**3 + 27 * B**2)) % P
    rows = points()
    order = len(rows) + 1
    labels = permuted_labels()
    hits, null_hits = [], []
    eligible = 0
    roundtrips = 0
    nonscored_roundtrips = 0
    excluded = {"zero_y": 0, "opposite": 0, "infinite_sum": 0}
    excluded_roundtrip = None
    for i, u in enumerate(rows):
        for v in rows[i + 1:]:
            if u[1] == 0 or v[1] == 0:
                excluded["zero_y"] += 1
                reason = "zero_y"
            elif u[0] == v[0] and (u[1] + v[1]) % P == 0:
                excluded["opposite"] += 1
                reason = "opposite"
            else:
                reason = None
            if reason is not None:
                if excluded_roundtrip is None:
                    sum_excluded = add(u, v)
                    if sum_excluded is not None:
                        excluded_roundtrip = {"pair": [list(u), list(v)], "reason": reason,
                                              "pass": add(sum_excluded, (v[0], -v[1] % P)) == u}
                continue
            w = add(u, v)
            if w is None:
                excluded["infinite_sum"] += 1
                continue
            eligible += 1
            back = add(w, (v[0], -v[1] % P))
            if back != u:
                raise ValueError(f"round trip failed for {u}, {v}")
            roundtrips += 1
            row = [list(u), list(v), list(w)]
            if w[0] == (u[0] + v[0]) % P:
                hits.append(row)
            else:
                nonscored_roundtrips += 1
            if labels[w[0]] == (labels[u[0]] + labels[v[0]]) % P:
                null_hits.append(row)
    controls = {"prime": prime, "nonsingular": discriminant != 0,
                "ordinary": order != P + 1,
                "hasse_interval": 72 <= order <= 108,
                "roundtrip_all_eligible": roundtrips == eligible,
                "roundtrip_nonscored": nonscored_roundtrips > 0 or eligible == len(hits),
                "roundtrip_first_excluded": excluded_roundtrip is None or excluded_roundtrip["pass"],
                "pair_partition": eligible + sum(excluded.values()) == len(rows) * (len(rows) - 1) // 2,
                "permutation_bijective": sorted(labels) == list(range(P))}
    return {"parameters": {"p": P, "a": A, "b": B, "seed": 5140517},
            "point_count": order, "discriminant_mod_p": discriminant,
            "affine_points": len(rows), "candidate_pairs": len(rows) * (len(rows) - 1) // 2,
            "eligible_pairs": eligible, "exclusion_counts": excluded,
            "first_excluded_roundtrip": excluded_roundtrip,
            "W": len(hits), "permuted_label_count": len(null_hits),
            "hits": hits, "permuted_label_hits": null_hits,
            "permutation": labels, "controls": controls,
            "valid": all(controls.values())}


def write_run(run_dir: Path):
    if (run_dir / "raw-result.json").exists() or (run_dir / "manifest.yaml").exists():
        raise FileExistsError(f"immutable run artifacts already exist in {run_dir}")
    started = datetime.now(timezone.utc).isoformat()
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    result = census()
    wall, cpu = time.perf_counter() - wall_start, time.process_time() - cpu_start
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_max
    if sys.platform != "darwin":
        peak *= 1024
    result["resources"] = {"wall_clock_seconds": wall, "cpu_seconds": cpu,
                           "peak_rss_bytes": peak}
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip())
    source = "experiments/EXP-ECTD-97777a/implementation/run.py"
    manifest = {"run": {"id": RUN_ID, "experiment_id": EXPERIMENT_ID,
                        "hypothesis_id": "H-ECTD-cda162", "goal_id": "GOAL-ECTD-001",
                        "task_id": "TASK-20261010-cd7e81", "status": "completed_unreviewed",
                        "recorded_at": started,
                        "code": {"commit": commit, "dirty": dirty,
                                 "command": f"python3 {source} --run-dir <run_dir>",
                                 "source_path": source,
                                 "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                        "environment": {"python": platform.python_version(), "platform": platform.platform()},
                        "inputs": {"parameters": result["parameters"], "seeds": {"permutation": 5140517}},
                        "timing": {"wall_clock_seconds": wall, "cpu_seconds": cpu},
                        "resources": {"peak_rss_bytes": peak},
                        "result": {"validity_status": "pending_checker", "certificate": {"kind": "none", "verified": False},
                                   "metrics": {"W": result["W"], "point_count": result["point_count"],
                                               "permuted_label_count": result["permuted_label_count"]}},
                        "artifacts": {"raw_result": "raw-result.json", "stdout": "stdout.log",
                                      "stderr": "stderr.log", "environment": "environment.json",
                                      "command": "command.txt"}}}
    (run_dir / "manifest.yaml").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    write_run(Path(parser.parse_args().run_dir))
