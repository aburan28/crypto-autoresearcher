"""Timed isogenous-model scalar multiplication (driver for bench.c).

Arms, on the same K random (P, k) pairs, interleaved and rotated per repetition:

* ``A0 E``          -- k P on E with its own arithmetic (generic a: dbl-2007-bl);
* ``A1 persistent`` -- k' P' on the a = -3 model of the neighbour, P' already there;
* ``A2 one-shot``   -- forward route, k' = k c mod n, k' P' on the neighbour, dual route;
* ``A3 A/A``        -- A0 again, timed as a separate arm: the instrument-noise control.

E's own doubling is the generic-a formula; a curve that is itself a = -3 is
outside this instrument's scope (it would understate A0).

Every arm's affine output is checked against a Python reference (k P on E for
A0 and A2, k' P' on the neighbour for A1) before any timing is reported.
Timings are measured wall-clock nanoseconds per scalar multiplication on this
host; ratios carry a paired percentile-bootstrap interval over repetitions.

    python -m harness.endosweep.isobench.isobench --rows RUN/raw-result.json --curve NAME --out-dir DIR
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .. import explicit as EX
from .. import isomodel as IM
from ..toyverify import Curve, Isomorphism, prime_nth_roots
from . import maps as MP

HERE = Path(__file__).resolve().parent


def build_route(row: dict, ells: list[int], depth: int, max_nodes: int, seed: int) -> dict:
    p, a, b, n, h = (int(row["p"], 16), int(row["a"], 16), int(row["b"], 16), int(row["n"], 16), row["cofactor"])
    E = Curve(p, a, b)
    trace = p + 1 - n * h
    best = row["best"]
    nodes = IM.bfs(E, trace, n, ells, depth, max_nodes)
    node = next(x for x in nodes if x.j == best["j"])
    P = EX.point_of_order(E, n, h, seed=seed)
    maps, cur, duals, Q = [], E, [], P
    for e in node.path:
        phi = EX.KernelIsogeny(cur, e.kernel, e.ell)
        d = IM._dual(phi, e.ell, trace, Q)
        if d is None:
            raise RuntimeError(f"no dual for degree-{e.ell} step")
        maps.append(phi)
        duals.append(d)
        Q = phi(Q)
        cur = phi.codomain
    # isomorphism to the a = -3 model: u^4 = -3 / a'
    r = (-3) * pow(cur.a, -1, p) % p
    u = None
    for c in prime_nth_roots(r, 2, p):
        rr = prime_nth_roots(int(c), 2, p)
        if rr:
            u = int(rr[0])
            break
    if u is None:
        raise RuntimeError("neighbour is not a = -3-equivalent")
    iso = Isomorphism(cur, u)
    Cm3 = iso.codomain
    assert Cm3.a == p - 3
    sign, deg = 1, 1
    for (_psi, _iso, sg), e in zip(duals, node.path):
        sign *= sg
        deg *= e.ell
    c = pow(deg, -1, n) * sign % n
    idstep = {"N": [0, 1], "M": [1], "psi": [1], "ell": 1}
    fwd = [dict(MP.step_polys(phi), uinv=1) for phi in maps] + [dict(idstep, uinv=pow(u, -1, p))]
    back = [dict(idstep, uinv=u)]
    for psi, iso_back, _sg in reversed(duals):
        back.append(dict(MP.step_polys(psi), uinv=pow(iso_back.u, -1, p)))
    return {"p": p, "n": n, "h": h, "a": a, "b": b, "E": E, "Cm3": Cm3, "c": c, "deg": deg, "sign": sign,
            "path": [e.ell for e in node.path], "maps": maps, "iso": iso, "fwd": fwd, "back": back}


def _route_forward(R: dict, P):
    for phi in R["maps"]:
        P = phi(P)
    return R["iso"](P)


def write_input(R: dict, pts: list, out: Path, reps: int) -> None:
    p, n = R["p"], R["n"]
    hx = lambda v: format(v % (1 << 256), "x")
    L = [hx(p), hx(n), hx(R["a"]), hx(p - 3), hx(R["c"] * (1 << 256) % n)]

    def step(s):
        k = len(s["psi"]) - 1
        N = list(s["N"]) + [0] * (2 * k + 2 - len(s["N"]))
        M = list(s["M"]) + [0] * (3 * k + 1 - len(s["M"]))
        return [str(k)] + [hx(x) for x in N] + [hx(x) for x in M] + [hx(x) for x in s["psi"]] + [hx(s["uinv"])]
    L.append(str(len(R["fwd"])))
    for s in R["fwd"]:
        L += step(s)
    L.append(str(len(R["back"])))
    for s in R["back"]:
        L += step(s)
    L += [str(len(pts)), str(reps)]
    for P, k, Pn, kn in pts:
        L += [hx(P[0]), hx(P[1]), hx(k), hx(Pn[0]), hx(Pn[1]), hx(kn)]
    out.write_text("\n".join(L) + "\n")


def boot(xs: list[float], ys: list[float], B: int, rng: random.Random) -> tuple[float, float, float]:
    ratios = [y / x for x, y in zip(xs, ys)]
    est = statistics.median(ratios)
    bs = []
    for _ in range(B):
        s = [ratios[rng.randrange(len(ratios))] for _ in ratios]
        bs.append(statistics.median(s))
    bs.sort()
    return est, bs[int(0.025 * B)], bs[int(0.975 * B) - 1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rows", required=True)
    ap.add_argument("--curve", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ells", default="2,3,5,7,11,13")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--max-nodes", type=int, default=64)
    ap.add_argument("--points", type=int, default=64)
    ap.add_argument("--reps", type=int, default=41)
    ap.add_argument("--bootstrap", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=20261016)
    ap.add_argument("--cc", default=os.environ.get("CC", "cc"))
    ap.add_argument("--cflags", default="-O2 -march=native")
    args = ap.parse_args(argv)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    row = next(r for r in json.load(open(args.rows))["rows"] if r["name"] == args.curve)
    t0 = time.time()
    R = build_route(row, [int(x) for x in args.ells.split(",")], args.depth, args.max_nodes, args.seed)
    rng = random.Random(args.seed)
    E, Cm3, n, h = R["E"], R["Cm3"], R["n"], R["h"]
    pts = []
    for i in range(args.points):
        P = EX.point_of_order(E, n, h, seed=rng.randrange(2, 1 << 30))
        k = rng.randrange(1, n)
        Pn = _route_forward(R, P)
        pts.append((P, k, Pn, k * R["c"] % n))
    tmp = Path(tempfile.mkdtemp(prefix="isobench-"))
    exe = tmp / "bench"
    cc = [args.cc, *args.cflags.split(), "-o", str(exe), str(HERE / "bench.c")]
    subprocess.check_call(cc)
    cc_version = subprocess.run([args.cc, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    write_input(R, pts, tmp / "input.txt", args.reps)
    proc = subprocess.run([str(exe)], stdin=open(tmp / "input.txt"), capture_output=True, text=True, check=True)
    shutil.copyfile(tmp / "input.txt", out / "bench-input.txt")
    (out / "bench-output.txt").write_text(proc.stdout)
    timings: dict[int, dict[int, float]] = {}
    results: dict[tuple[int, int], tuple[int, int]] = {}
    for line in proc.stdout.splitlines():
        f = line.split()
        if f[0] == "T":
            timings.setdefault(int(f[2]), {})[int(f[1])] = float(f[3])
        elif f[0] == "R":
            results[(int(f[1]), int(f[2]))] = (int(f[3], 16), int(f[4], 16))
    # correctness against the Python reference
    bad = []
    for i, (P, k, Pn, kn) in enumerate(pts):
        want = E.mul(k, P)
        if results[(0, i)] != want:
            bad.append(("A0", i))
        if results[(2, i)] != want:
            bad.append(("A2", i))
        if results[(3, i)] != want:
            bad.append(("A3", i))
        if results[(1, i)] != Cm3.mul(kn, Pn):
            bad.append(("A1", i))
    reps = sorted(timings[0])
    A0 = [timings[0][r] for r in reps]
    A1 = [timings[1][r] for r in reps]
    A2 = [timings[2][r] for r in reps]
    A3 = [timings[3][r] for r in reps]
    brng = random.Random(args.seed + 1)
    r1, r2, r3 = (boot(A0, A1, args.bootstrap, brng), boot(A0, A2, args.bootstrap, brng),
                  boot(A0, A3, args.bootstrap, brng))
    summary = {
        "curve": args.curve, "path": R["path"], "degree": R["deg"], "dual_sign": R["sign"],
        "points": args.points, "reps": args.reps, "correct": not bad, "mismatches": bad[:20],
        "ns_per_op_median": {"A0_E": statistics.median(A0), "A1_persistent": statistics.median(A1),
                             "A2_oneshot": statistics.median(A2), "A3_AA": statistics.median(A3)},
        "ratio_A1_over_A0": {"median": r1[0], "ci95": [r1[1], r1[2]]},
        "ratio_A2_over_A0": {"median": r2[0], "ci95": [r2[1], r2[2]]},
        "ratio_A3_over_A0_AA": {"median": r3[0], "ci95": [r3[1], r3[2]]},
        "derived_saving": {"persistent": 1 - r1[0], "oneshot": 1 - r2[0]},
        "provenance": {"command": " ".join(sys.argv), "cc": " ".join(cc[:-4] + cc[-1:]), "cc_version": cc_version,
                       "host": platform.platform(), "machine": platform.machine(), "processor": platform.processor(),
                       "cpu_count": os.cpu_count(), "python": sys.version,
                       "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                       "seconds": round(time.time() - t0, 1)},
    }
    (out / "timings.json").write_text(json.dumps({"reps": reps, "A0": A0, "A1": A1, "A2": A2, "A3": A3}, indent=1))
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: summary[k] for k in ("correct", "ns_per_op_median", "ratio_A1_over_A0", "ratio_A2_over_A0", "ratio_A3_over_A0_AA")}))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
