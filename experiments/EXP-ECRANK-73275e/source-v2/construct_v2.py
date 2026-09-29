"""Construction arm for EXP-ECRANK-73275e v2 (R12/R13/R14).

Copy-with-record of v1 source/construct.py construct_arm. The v1 file is
NOT edited. The ONLY changes from v1 construct_arm are:
  - ops_cap is a parameter (v1 used the module global OPS_CAP = 1.0e8).
  - A wall-clock cap check (7200 s) is added inside the b-tuple loop, per
    the amendment's per-run stopping rule ("counted-ops cap OR 7200 s wall,
    whichever first"). v1 had no wall-clock check in the loop.
  - The exhaustion record carries which cap fired.

All helper functions (sample_b, sample_dpat, solve_n6, solve_n8,
rat_height, B_INTS) are imported from v1 construct (read-only). The
counted-ops convention is the v1 IC-1 (Fraction arithmetic + isqrt +
modular pow); ops_cap_respected is the EXACT boolean (counted_ops < cap)
[SR-9].
"""

import random
import time
from fractions import Fraction as Fr

import ecrank_engine as E
import construct
import null_family as NF


def construct_arm_v2(engine, n, seed, n_b, H_levels, certifier=None,
                     coset=None, ec=None, null_family=False, stop_at=None,
                     ops_cap=1.0e8, wall_clock_cap=7200.0, t_start=None):
    """Seeded construction arm (v2). Returns raw observation dict.

    Identical to v1 construct_arm except for the parameterized ops_cap and
    the wall-clock cap. See module docstring.
    """
    if t_start is None:
        t_start = time.monotonic()
    rng = random.Random(seed)
    cosets = engine.eligible_cosets()
    rng_c = random.Random(seed)
    coset = coset or cosets[rng_c.randrange(len(cosets))]
    values = [engine.class_value(m) for m in coset["members"]]
    found = []
    near_miss = []
    feasible = 0
    H_top = max(H_levels)
    counts = {int(H): 0 for H in H_levels}
    exhaustion = None
    bi = -1
    for bi in range(n_b):
        if engine.ops_count() >= ops_cap:
            exhaustion = {"kind": "counted_ops_cap", "ops": engine.ops_count(),
                          "b_index": bi, "cap": ops_cap}
            break
        if (time.monotonic() - t_start) >= wall_clock_cap:
            exhaustion = {"kind": "wall_clock_cap",
                          "ops": engine.ops_count(), "b_index": bi,
                          "wall_seconds": time.monotonic() - t_start,
                          "cap": wall_clock_cap}
            break
        if stop_at and bi >= stop_at:
            break
        b = construct.sample_b(rng, n)
        dpat = [1] * n if null_family else construct.sample_dpat(rng, n, values)
        if n == 6:
            if null_family:
                A, B, C = NF.d1_quadratic_coeffs(engine, b)
                C_null = NF.null_constant(A, B, C)
                kept, near, meta = construct.solve_n6(engine, b, dpat, H_top,
                                                      null_override=(A, B, C_null))
            else:
                kept, near, meta = construct.solve_n6(engine, b, dpat, H_top)
        else:
            kept, near, meta = construct.solve_n8(engine, b, dpat, H_top)
        if kept:
            feasible += 1
        else:
            if near:
                near_miss.append({"b_index": bi, "b": [str(x) for x in b],
                                  "d_pattern": list(dpat),
                                  "failing": near[:3], "meta": meta})
        for inst in kept:
            h = inst["r_height"]
            rec = {"b_index": bi, "instance": inst, "r_height": h}
            if certifier is not None and coset is not None and ec is not None:
                cert = certifier.certify_instance(inst, coset, ec)
                rec["certificate"] = {
                    "verdict": cert.get("verdict"),
                    "aggregate_total": cert.get("aggregate_total"),
                    "n_classes": len(cert.get("classes", {})),
                    "class_keys": sorted(str(k) for k in cert.get("classes", {})),
                }
            found.append(rec)
            for H in H_levels:
                if h <= H:
                    counts[int(H)] += 1
    return {
        "n": n,
        "seed": seed,
        "n_b_declared": n_b,
        "n_b_done": bi + 1 if n_b else 0,
        "H_levels": list(H_levels),
        "feasible_tuples": feasible,
        "feasibility_fraction": (feasible / n_b) if n_b else 0,
        "found": found,
        "counts_per_H": counts,
        "near_miss_ledger": near_miss[:200],
        "near_miss_total": len(near_miss),
        "exhaustion": exhaustion,
        "coset_V": list(coset["V"]) if coset else None,
        "ops": engine.ops_count(),
    }
