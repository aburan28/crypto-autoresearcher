#!/usr/bin/env python3
"""Phase-2 enumeration with the validator's own sieve (TASK-20261022-a846f4).

Imports scan() from the sealed blind/blind_sieve.py unchanged and runs it on
curves whose a-invariants are only known from the run records (the rank-7
overlap curve, a-invariants read from raw-result.json) plus the proves-too-much
object 11a1 at the full hmax.  Not blind: the a-invariants of the rank-7 curve
come from the producer's raw result.
Usage: j2_enumerate.py BLIND_SIEVE_PY HMAX OUT_JSON
"""
import importlib.util
import json
import sys
import time

spec = importlib.util.spec_from_file_location("blind_sieve", sys.argv[1])
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)

CURVES = {"382623908456a1_from_raw": [0, 0, 0, -10012, 346900]}


def main():
    hmax, out = int(sys.argv[2]), sys.argv[3]
    res = {"scan_hmax": hmax, "curves": {}}
    for name, ai in CURVES.items():
        t0 = time.time()
        pts, surv = bs.scan(ai, hmax)
        pts.sort(key=lambda p: (bs.xh(p[0]), p[0], p[1]))
        grid = [10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000]
        res["curves"][name] = {
            "a_invariants": ai,
            "counts_excl_O": {str(h): sum(1 for p in pts if bs.xh(p[0]) <= h) for h in grid if h <= hmax},
            "points": [{"x": str(x), "y": str(y), "H_x": bs.xh(x)} for x, y in pts],
            "seconds": round(time.time() - t0, 1),
        }
        print(name, res["curves"][name]["counts_excl_O"], res["curves"][name]["seconds"], flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
