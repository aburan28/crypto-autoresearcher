"""Command line: ``python -m crypto_autoresearcher.index_calculus``.

    solve  --bits 20 --m 2 --fb small_x [--rho]      one instance, JSON out
    sweep  --bits 12 14 16 18 --m 2 3 --curves 3     cost table and fitted
                                                     exponents vs Pollard rho

The fitted exponent is the least-squares slope of log2(cost) against log2(N).
Index-calculus cost is reported in two columns that are never summed: S_3
root solves (one modular square root each) and group operations; rho cost is
group operations.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys

from .curve import generate_prime_order_curve
from .rho import pollard_rho
from .solver import FACTOR_BASES, solve_index_calculus


def _instance(bits: int, curve_seed: int, target_seed: int):
    E, P = generate_prime_order_curve(bits, curve_seed)
    k = random.Random(f"target|{bits}|{curve_seed}|{target_seed}").randrange(1, E.order)
    return E, P, E.mul(k, P), k


def _slope(xs: list[float], ys: list[float]) -> float | None:
    if len(set(xs)) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def cmd_solve(args: argparse.Namespace) -> int:
    E, P, Q, k = _instance(args.bits, args.curve_seed, args.target_seed)
    E.ops.group_ops = 0
    out = {"curve": {"p": E.p, "a": E.a, "b": E.b, "order": E.order},
           "P": P, "Q": Q}
    ic = solve_index_calculus(E, P, Q, m=args.m, fb_kind=args.fb,
                              fb_size=args.fb_size, seed=args.seed)
    out["index_calculus"] = ic.to_dict() | {"correct": ic.k == k}
    if args.rho:
        rr = pollard_rho(E, P, Q, seed=args.seed)
        out["rho"] = {"k": rr.k, "verified": rr.verified, "group_ops": rr.group_ops,
                      "restarts": rr.restarts, "seconds": rr.seconds}
    json.dump(out, sys.stdout, indent=2, default=list)
    print()
    return 0 if ic.verified else 1


def cmd_sweep(args: argparse.Namespace) -> int:
    rows = []
    for bits in args.bits:
        for c in range(args.curves):
            E, P, Q, k = _instance(bits, c, 0)
            logN = math.log2(E.order)
            rr = pollard_rho(E, P, Q, seed=c)
            rows.append({"bits": bits, "curve": c, "method": "rho", "fb": "-",
                         "log2N": logN, "ok": rr.verified, "cost": rr.group_ops,
                         "group_ops": rr.group_ops, "s3_solves": 0,
                         "seconds": rr.seconds})
            for m in args.m:
                for fb in args.fb:
                    E.ops.group_ops = 0
                    ic = solve_index_calculus(E, P, Q, m=m, fb_kind=fb, seed=c)
                    rows.append({"bits": bits, "curve": c, "method": f"ic_m{m}",
                                 "fb": fb, "fb_size": ic.factor_base["size"],
                                 "log2N": logN, "ok": ic.verified and ic.k == k,
                                 "cost": ic.s3_solves, "group_ops": ic.group_ops,
                                 "s3_solves": ic.s3_solves,
                                 "relations": ic.relations,
                                 "seconds": ic.seconds_total})
            if not args.json:
                for r in rows[-(1 + len(args.m) * len(args.fb)):]:
                    print(f"{r['bits']:>4} c{r['curve']} {r['method']:<7} {r['fb']:<8} "
                          f"|F|={r.get('fb_size', '-')!s:<5} ok={r['ok']!s:<5} "
                          f"s3={r['s3_solves']:<9} gops={r['group_ops']:<9} "
                          f"t={r['seconds']:.2f}s", file=sys.stderr)
    fits = {}
    for key in sorted({(r["method"], r["fb"]) for r in rows}):
        sel = [r for r in rows if (r["method"], r["fb"]) == key and r["ok"]]
        xs = [r["log2N"] for r in sel]
        fits[f"{key[0]}:{key[1]}"] = {
            "exponent_group_ops": _slope(xs, [math.log2(max(1, r["group_ops"])) for r in sel]),
            "exponent_s3_solves": (_slope(xs, [math.log2(max(1, r["s3_solves"])) for r in sel])
                                   if key[0] != "rho" else None),
            "instances": len(sel),
        }
    if args.json:
        json.dump({"rows": rows, "fits": fits}, sys.stdout, indent=2)
        print()
    else:
        print("fitted exponents (slope of log2 cost vs log2 N):")
        for name, f in fits.items():
            g = f["exponent_group_ops"]
            s = f["exponent_s3_solves"]
            print(f"  {name:<18} group_ops {g if g is None else round(g, 3)!s:<7}"
                  f" s3_solves {s if s is None else round(s, 3)!s:<7} n={f['instances']}")
    return 0 if all(r["ok"] for r in rows) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m crypto_autoresearcher.index_calculus",
                                 description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("solve", help="solve one instance")
    s.add_argument("--bits", type=int, default=16)
    s.add_argument("--m", type=int, default=2)
    s.add_argument("--fb", choices=FACTOR_BASES, default="small_x")
    s.add_argument("--fb-size", type=int, default=None)
    s.add_argument("--curve-seed", type=int, default=0)
    s.add_argument("--target-seed", type=int, default=0)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--rho", action="store_true", help="also run Pollard rho")
    s.set_defaults(func=cmd_solve)

    w = sub.add_parser("sweep", help="cost table and fitted exponents vs rho")
    w.add_argument("--bits", type=int, nargs="+", default=[12, 14, 16, 18])
    w.add_argument("--m", type=int, nargs="+", default=[2])
    w.add_argument("--fb", choices=FACTOR_BASES, nargs="+", default=["small_x"])
    w.add_argument("--curves", type=int, default=3)
    w.add_argument("--json", action="store_true")
    w.set_defaults(func=cmd_sweep)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
