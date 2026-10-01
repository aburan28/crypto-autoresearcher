#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- child jobs (builders and grid interpolation).

Always launched by v2_solver.run_child from the driver, so RLIMIT_AS is set IN THIS PROCESS before
exec and read back (AC-1, DC-6 R-1). The job re-reads its own limit at start and refuses to run if it
is not the requested cap. Jobs:
  build_poly  interpolate one arm polynomial (X / t_R symbolic), held-out check, single-flip test;
              writes <out>.npz (C, monos) and <out>.meta.json.
  raw_grid    per-target raw_x / raw_u grid system for one x_R; writes <out>.npz (C) and <out>.meta.json
              with the counted construction operations (DC-4 C-3).
usage: v2_child.py <spec.json>
"""
import json
import os
import random
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                                     # noqa: E402

import flint                                           # noqa: E402
flint.ctx.threads = 1

from v2_field import Fq, Curve, OpCount               # noqa: E402
import v2_arms as A                                    # noqa: E402


def field_curve(spec):
    F = Fq(spec["field"]["p"], spec["field"]["modulus"])
    c = spec["curve"]
    E = Curve(F, F.from_coeffs(c["a2"]), F.from_coeffs(c["a4"]), F.from_coeffs(c["a6"]), c.get("label", ""))
    return F, E


def save_poly(pol, out, extra_meta):
    np.savez_compressed(out + ".npz", C=pol.C, monos=np.array(pol.monos, dtype=np.int64))
    meta = dict(pol.meta)
    meta.update(extra_meta)
    with open(out + ".meta.json", "w") as fh:
        json.dump(meta, fh, indent=1, default=str)


def load_poly(path_npz, F):
    d = np.load(path_npz, allow_pickle=False)
    with open(path_npz[:-4] + ".meta.json") as fh:
        meta = json.load(fh)
    monos = [tuple(int(x) for x in row) for row in d["monos"]]
    pol = A.ArmPolynomial(meta["kind"], meta["m"], monos, F, d["C"], meta)
    pol.support = [monos[i] for i in range(len(monos)) if d["C"][:, i, :].any()]
    return pol


def main():
    spec = json.load(open(sys.argv[1]))
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    if spec.get("cap_bytes") is not None and soft != spec["cap_bytes"]:
        print("REFUSING: RLIMIT_AS read back %s != requested %s" % (soft, spec["cap_bytes"]), file=sys.stderr)
        sys.exit(96)
    print("child RLIMIT_AS read back: soft=%d hard=%d" % (soft, hard), flush=True)
    F, E = field_curve(spec)
    kind, m = spec["kind"], spec["m"]
    rs = None
    if A.base_of(kind) == "x_over_lam_in_Fp":
        rs = A.rescaling(E, beta_override=spec.get("beta_override"))
        if rs["refused"]:
            json.dump({"refused": True, "reason": rs["reason"]}, open(spec["out"] + ".meta.json", "w"))
            sys.exit(0)
    t0 = time.time()
    if spec["job"] == "build_poly":
        rng = random.Random(spec["sample_seed"])
        lim = spec.get("pool_limit", A.POOL_LIMIT_DEFAULT)
        if kind in ("S", "identity", "raw_x"):
            pool = A.pool_x(E, lim)
        elif kind in ("S_rescaled", "rq", "raw_u"):
            pool = A.pool_u(E, rs["lam_obj"], lim)
        elif kind == "norm":
            if not E.has_rational_2torsion() or E.a6 != 0:
                json.dump({"refused": True, "reason": "no rational 2-torsion"}, open(spec["out"] + ".meta.json", "w"))
                sys.exit(0)
            pool = A.pool_t(E, lim)
        else:
            raise ValueError(kind)
        pol = A.build_arm_polynomial(kind, m, E, rs, pool, rng, log=lambda *a: print(*a, flush=True))
        if pol.meta["held_out_mismatches"] != 0:
            print("held-out verification failed", file=sys.stderr)
        flip = A.single_flip_test(pol, E, rs, pool, random.Random(spec["sample_seed"] + ":flip"), n_points=spec.get("flip_points", 12))
        extra = {"single_flip_test": flip, "rescaling": A.public_rescaling(rs) if rs else None,
                 "sample_seed": spec["sample_seed"], "rlimit_as_child_getrlimit": {"soft": soft, "hard": hard},
                 "support_exponents": [list(a) for a in pol.support] if len(pol.support) <= 5000 else None,
                 "seconds_total": round(time.time() - t0, 2)}
        if kind == "rq":
            extra["rq_relation_equation_numeric_check"] = A.check_rq_relation_equation(m, rs["beta"], F.p, random.Random(spec["sample_seed"] + ":releq"))
        save_poly(pol, spec["out"], extra)
    elif spec["job"] == "raw_grid":
        ctr = OpCount(F.n)
        xR = F.from_coeffs(spec["x_R"])
        names, eqs, info, C = A.raw_system_at_target(kind, m, E, rs, xR, spec["nodes"], counter=ctr, log=lambda *a: None)
        np.savez_compressed(spec["out"] + ".npz", C=C)
        meta = {"kind": kind, "m": m, "info": info, "construction_ops": ctr.as_dict(),
                "rescaling": A.public_rescaling(rs) if rs else None,
                "rlimit_as_child_getrlimit": {"soft": soft, "hard": hard}, "seconds_total": round(time.time() - t0, 2)}
        json.dump(meta, open(spec["out"] + ".meta.json", "w"), indent=1, default=str)
    else:
        raise ValueError(spec["job"])
    print("child job done in %.1fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
