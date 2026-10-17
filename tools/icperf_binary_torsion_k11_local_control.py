"""Freeze a target-blind, same-width random control for the weighted k11 base.

Enumerate every liftable torsion pair in the selected 11-bit affine block,
then SHA-256-rank pairs and keep the weighted base's realized column count.
This prepares an input set; it does not search for a relation or time a solver.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_torsion_coordinate import negative, x_from_phi  # noqa: E402
from tools.icperf_ordinary_binary_fixture import add, lift_x, on_curve, scale  # noqa: E402

PARENT = ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json"
FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
DOMAIN = b"icperf-binary-k11-local-control-v1"
SEED = 20261017


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(t: int) -> bytes:
    return hashlib.sha256(DOMAIN + SEED.to_bytes(8, "big") + t.to_bytes(8, "big")).digest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    parent, fixture = json.loads(PARENT.read_bytes()), json.loads(FIXTURE.read_bytes())
    assert parent["fixture_sha256"] == sha(FIXTURE)
    offset, width = parent["selected_offset"], 11
    scan = next(row for row in parent["candidate_scans"] if row["offset"] == offset)
    target_columns = scan["projected_columns"]
    assert offset == 4096 and target_columns == 316
    gamma = parent["coordinate"]["gamma"]
    t2 = tuple(parent["coordinate"]["two_torsion"])
    b, r = fixture["b_polynomial_bits"], fixture["prime_order"]
    assert on_curve(t2, b) and scale(2, t2, b) is None
    full = {}
    counts = {"pairs_attempted": 0, "exceptional_pairs": 0, "nonliftable_pairs": 0}
    for v in range(0, 1 << width, 2):
        counts["pairs_attempted"] += 1
        t = offset ^ v
        x, xp = x_from_phi(t, gamma), x_from_phi(t ^ 1, gamma)
        if x in (0, gamma) or xp in (0, gamma):
            counts["exceptional_pairs"] += 1
            continue
        p, pp = lift_x(x, b), lift_x(xp, b)
        assert (p is None) == (pp is None)
        if p is None:
            counts["nonliftable_pairs"] += 1
            continue
        assert on_curve(p, b) and on_curve(pp, b)
        assert add(p, t2, b) in (pp, negative(pp))
        full[t] = (p, pp)
    assert len(full) == 511 and counts == {"pairs_attempted": 1024,
                                          "exceptional_pairs": 0,
                                          "nonliftable_pairs": 513}
    chosen = sorted(sorted(full, key=lambda t: (rank(t), t))[:target_columns])
    assert len(chosen) == 316 and len(set(chosen)) == 316
    reps, projected, signs = [], [], []
    for t in chosen:
        p, pp = full[t]
        image, pair_image = scale(4, p, b), scale(4, pp, b)
        assert image is not None and pair_image is not None and scale(r, image, b) is None
        sign = 1 if image == pair_image else -1
        assert pair_image == (image if sign == 1 else negative(image))
        reps.append([t, *p])
        projected.append(list(image))
        signs.append(sign)
    assert len({row[0] for row in projected}) == target_columns
    selected_raw = sorted(t for even in chosen for t in (even, even ^ 1))
    assert len(selected_raw) == 632
    output = {
        "schema": "icperf-binary-torsion-k11-local-control-v1",
        "scope": "target-blind matched-width factor-base control; no solver, relation yield or speed claim",
        "source_sha256": sha(Path(__file__)), "parent_base_sha256": sha(PARENT),
        "fixture_sha256": sha(FIXTURE), "curve": parent["curve"],
        "coordinate": parent["coordinate"], "selected_offset": offset,
        "selection": {"domain": DOMAIN.decode(), "seed": SEED, "width": width,
                      "rule": "SHA-256-rank all liftable even-phi torsion pairs in the selected offset; take first 316, then sort by phi",
                      "target_columns": target_columns,
                      "target_origin": "realized columns of the archived weighted k11 base",
                      "selection_uses_target": False},
        "full_block": {**counts, "liftable_pairs": len(full),
                       "liftable_even_phi": sorted(full)},
        "candidate_scans": [{"offset": offset, "accepted_phi": selected_raw,
                             "raw_representatives": len(selected_raw),
                             "projected_columns": target_columns,
                             "selected_representatives": reps,
                             "projected_points": projected, "pair_signs": signs}],
        "preparation": {"wall_seconds": time.perf_counter() - started_wall,
                        "cpu_seconds": time.process_time() - started_cpu,
                        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                                          (1 if sys.platform == "darwin" else 1024),
                        "loadavg_end": list(os.getloadavg()),
                        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                   capture_output=True, text=True, check=True).stdout.strip(),
                        "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                                                 capture_output=True, text=True, check=True).stdout.splitlines(),
                        "python_version": sys.version}}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"full_liftable_pairs": len(full), "selected_columns": len(chosen),
                      "raw_representatives": len(selected_raw)}, sort_keys=True))


if __name__ == "__main__":
    main()
