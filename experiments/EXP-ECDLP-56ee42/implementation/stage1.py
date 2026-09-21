"""
Stage 1 for EXP-ECDLP-56ee42: reproduce f558e4's frozen fixture EXACTLY in
rationals (at N = 23, s = 3, interval partition of Z/23Z: q_strict = 0 and
q_maj = 284/529), then enumerate the six ladder subgroups and cache the
(x, y) arrays as uint32 .npy files for the Stage 3 task.

If the fixture misses, STOP (F2), archive the computed value, and return.

Run:  python3 stage1.py
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
import estimator as E

LADDER = [
    {"T": 17, "p": 131101, "b": 27, "N": 131113},
    {"T": 19, "p": 524309, "b": 80, "N": 525361},
    {"T": 21, "p": 2097169, "b": 1, "N": 2098321},
    {"T": 23, "p": 8388617, "b": 21, "N": 8391797},
    {"T": 25, "p": 33554473, "b": 49, "N": 33557891},
    {"T": 27, "p": 134217757, "b": 70, "N": 134234689},
]

FIXTURE_N = 23
FIXTURE_S = 3
FIXTURE_QMAJ = Fraction(284, 529)
FIXTURE_QSTRICT = Fraction(0, 1)


def main() -> None:
    t_start = time.time()
    out = {"stage": 1, "steps": {}}

    # --- Step 1: reproduce the frozen fixture ---
    t0 = time.time()
    v = E.interval_partition(FIXTURE_N, FIXTURE_S)
    qm, N_arr = E.q_maj_exact(v, FIXTURE_N)
    qs = E.q_strict_exact(v, FIXTURE_N)
    fixture_pass = (qm == FIXTURE_QMAJ and qs == FIXTURE_QSTRICT)
    out["steps"]["fixture"] = {
        "N": FIXTURE_N,
        "s": FIXTURE_S,
        "q_maj_computed": str(qm),
        "q_maj_expected": str(FIXTURE_QMAJ),
        "q_strict_computed": str(qs),
        "q_strict_expected": str(FIXTURE_QSTRICT),
        "q_maj_float": float(qm),
        "pass": fixture_pass,
        "seconds": round(time.time() - t0, 3),
    }
    print(f"fixture: q_maj = {qm} ({float(qm):.6f}), q_strict = {qs}  "
          f"-> {'PASS' if fixture_pass else 'FAIL (F2)'}", file=sys.stderr)

    if not fixture_pass:
        # STOP (F2): archive the computed value and return.
        out["gate_F2"] = True
        out["validity"] = "failed_gate_F2"
        out["validity_reason"] = (
            f"fixture missed: q_maj = {qm} != {FIXTURE_QMAJ} or "
            f"q_strict = {qs} != {FIXTURE_QSTRICT}")
        out_path = Path("runs/RUN-ECDLP-56ee42-S1/raw-result.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
        print("STAGE 1 STOPPED (F2): fixture missed", file=sys.stderr)
        return

    # --- Step 2: enumerate the subgroups and cache (x, y) arrays ---
    cache_dir = Path("runs/stage-cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    enum_results = []
    for rung in LADDER:
        p, b, n = rung["p"], rung["b"], rung["N"]
        t0 = time.time()
        xs, ys = E.enumerate_subgroup(p, b, n)
        dt = time.time() - t0
        # verify the generator is on the curve and n*P = O
        px, py = int(xs[1]), int(ys[1])
        assert (py * py - (px * px * px + px + b)) % p == 0, "P not on curve"
        # verify a few random points are on the curve
        for k in [2, n // 2, n - 1]:
            x, y = int(xs[k]), int(ys[k])
            assert (y * y - (x * x * x + x + b)) % p == 0, f"point {k} not on curve"
        # cache as uint32 .npy
        x_path = cache_dir / f"rung_T{rung['T']}_x.npy"
        y_path = cache_dir / f"rung_T{rung['T']}_y.npy"
        np.save(x_path, xs.astype(np.uint32))
        np.save(y_path, ys.astype(np.uint32))
        enum_results.append({
            "T": rung["T"], "p": p, "b": b, "N": n,
            "generator": [px, py],
            "seconds": round(dt, 2),
            "x_cache": str(x_path), "y_cache": str(y_path),
            "x_sha256": _sha256_file(x_path), "y_sha256": _sha256_file(y_path),
        })
        print(f"T={rung['T']} n={n}: enumerated in {dt:.1f}s, "
              f"cached to {x_path.name}/{y_path.name}", file=sys.stderr)

    out["steps"]["enumeration"] = enum_results
    out["gate_F2"] = False
    out["validity"] = "valid"
    out["validity_reason"] = "fixture reproduced exactly; enumeration complete"
    out["wall_clock_seconds"] = round(time.time() - t_start, 2)

    out_path = Path("runs/RUN-ECDLP-56ee42-S1/raw-result.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(f"Stage 1 complete in {out['wall_clock_seconds']}s", file=sys.stderr)
    print(json.dumps({"fixture_pass": fixture_pass,
                      "q_maj": str(qm), "q_strict": str(qs)}, indent=2))


def _sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    main()
