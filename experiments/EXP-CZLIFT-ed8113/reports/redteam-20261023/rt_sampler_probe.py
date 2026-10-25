"""Red-team behavioural probe of the frozen sampler (TASK-20261023-62eb31).
Executes harness.czlift.random_point through the driver's import (source not
read) on p = 101 curves with three 2-torsion points, and counts Y = 0 among the
3200 replayed producer inputs. Checks finding F1 of VAL-20261022-b08129."""
from __future__ import annotations

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "implementation")))
import run as driver  # noqa: E402


def main():
    d = json.load(open(os.path.join(HERE, "rt_replay_inputs.json")))
    y0 = sum(1 for s in d.values() for row in s["rows"] for _, y in row["pts"] if int(y) == 0)
    npts = sum(len(row["pts"]) for s in d.values() for row in s["rows"])
    p = 101
    out = {"replayed_points": npts, "replayed_points_with_Y_0": y0, "probe": []}
    rng = random.Random(62)
    curves = []
    for a in range(p):
        for b in range(p):
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            roots = [x for x in range(p) if (x ** 3 + a * x + b) % p == 0]
            if len(roots) == 3:
                curves.append((a, b, roots))
            if len(curves) >= 3:
                break
        if len(curves) >= 3:
            break
    for a, b, roots in curves:
        E = driver.EllipticCurve(p, a, b)
        n = 20000
        draws = [driver.czlift.random_point(E, rng) for _ in range(n)]
        naff = sum(1 for x in range(p) for y in range(p) if (y * y - x ** 3 - a * x - b) % p == 0)
        out["probe"].append({"a": a, "b": b, "two_torsion_x": roots, "affine_points": naff, "draws": n,
                             "draws_with_y_0": sum(1 for P in draws if P is not None and P[1] % p == 0),
                             "expected_y0_draws_if_uniform_over_affine": round(n * 3 / naff, 1),
                             "draws_none": sum(1 for P in draws if P is None)})
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(HERE, "rt_sampler_probe.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
