#!/usr/bin/env python3
"""EXP-QSP-33b442 RUN 5 -- Stage 4: the rational-lambda conjecture check,
item (D)(ii) of H-QSP-5540d7.

Cells (n, n') = (11, 6) [q = 1, r = 5] and (23, 12) [q = 1, r = 11].
200 random coprime pairs (a, b) in F_2[X] with deg a <= 3, deg b <= 3, b != 0
and d = max(deg a, deg b) >= 1 per cell; base seed 20260917 with a named
sub-stream per cell.  Measured: the exact count of x in K with
x^{2^{n'}} b(x) = a(x), against the CONJECTURED bound
d^{q+1} + 2^{n'-r} + q d^q.

Usage:  python3 stage4.py RUN-QSP-33b442-S4
"""
from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qspcore import (KField, FIELD_POLY, field_poly_str, deg, gcd, poly_str,
                     frob_power_mod, f2_roots_in_K, polymod, square, clmul)
import runlib

CELLS = [(11, 6), (23, 12)]
DRAWS = 200
DEG_MAX = 3


def stream_label(n: int, npr: int) -> str:
    return "%d:stage4:n%d-np%d" % (runlib.BASE_SEED, n, npr)


def count_rational_roots(n: int, npr: int, a: int, b: int) -> dict:
    """#{x in K : x^{2^{n'}} b(x) = a(x)}, as deg gcd(P, X^{2^n} - X) with
    P(X) = X^{2^{n'}} b(X) + a(X).  Roots of P with b(x) = 0 would force
    a(x) = 0 too and are excluded by coprimality; that exclusion is CHECKED,
    not assumed."""
    P = (b << (1 << npr)) ^ a
    h = frob_power_mod(n, P) ^ 0b10
    g = P if h == 0 else gcd(P, h)
    common_with_b = deg(gcd(g, b)) if g and b else -1
    return {"N": deg(g) if g else 0, "deg_P": deg(P),
            "deg_gcd_with_b": common_with_b,
            "pole_roots_present": common_with_b > 0}


def brute_rational(K: KField, npr: int, a: int, b: int) -> int:
    cnt = 0
    for x in range(1 << K.n):
        bx = K.eval_f2poly(b, x)
        if bx == 0:
            continue
        if K.mul(K.pow2k(x, npr), bx) == K.eval_f2poly(a, x):
            cnt += 1
    return cnt


def main(run_id: str) -> int:
    inputs = {
        "stage": "stage_4 (rational-lambda conjecture check, (D)(ii))",
        "cells": [{"n": n, "n_prime": npr, "q": n // npr, "r": n % npr,
                   "draws": DRAWS, "field_polynomial": field_poly_str(n),
                   "field_polynomial_bits": hex(FIELD_POLY[n]),
                   "seed_stream_label": stream_label(n, npr)} for n, npr in CELLS],
        "sampling": "a, b drawn uniformly from F_2[X] with deg <= %d (a in [0, 15], "
                    "b in [1, 15]); a pair is kept iff gcd(a, b) = 1 and "
                    "d = max(deg a, deg b) >= 1, otherwise redrawn from the same "
                    "stream" % DEG_MAX,
        "measurement": "#{x in K : x^{2^{n'}} b(x) = a(x)} as deg gcd(X^{2^n} - X, "
                       "X^{2^{n'}} b(X) + a(X)), with the b(x) = 0 exclusion CHECKED "
                       "per draw; cross-checked by brute enumeration of all 2^n "
                       "elements at n = 11",
        "conjectured_bound": "d^{q+1} + 2^{n'-r} + q d^q",
        "seeds": {"base_seed": runlib.BASE_SEED,
                  "sub_streams": {"n%d_np%d" % (n, npr): stream_label(n, npr)
                                  for n, npr in CELLS},
                  "derivation": "random.Random('<base_seed>:stage4:n<n>-np<n'>')"},
        "obligation": "specification stage_4.obligation: EITHER the pole bookkeeping "
                      "of (D)(ii) is written out in the Stage 5 report OR the "
                      "extension is recorded as WITHDRAWN. This run produces the "
                      "fixture; the report records the choice.",
    }
    run = runlib.Run(run_id, "stage_4",
                     "python3 experiments/EXP-QSP-33b442/implementation/stage4.py " + run_id,
                     inputs, certificate_kind="none")
    raw: dict = {"stage": "stage_4", "specification_version": 1}
    cells_out = {}
    exceed = []
    brute_disagree = []
    run.log("== Stage 4: rational lambda = a/b, %d draws per cell" % DRAWS)
    for n, npr in CELLS:
        K = KField(n)
        q, r = divmod(n, npr)
        rng = random.Random(stream_label(n, npr))
        rows = []
        hist: dict[int, int] = {}
        mx = (-1, None)
        pole_hits = 0
        for i in range(DRAWS):
            while True:
                a = rng.getrandbits(4)
                b = rng.getrandbits(4)
                if b == 0:
                    continue
                if deg(gcd(a, b) if a else b) != 0:
                    continue
                d = max(deg(a), deg(b))
                if d >= 1:
                    break
            res = count_rational_roots(n, npr, a, b)
            bound = d ** (q + 1) + (1 << (npr - r)) + q * d ** q
            i1 = brute_rational(K, npr, a, b) if n <= 11 else None
            row = {"draw_index": i, "seed_stream": stream_label(n, npr),
                   "a_bits": a, "a_printed": poly_str(a) if a else "0",
                   "b_bits": b, "b_printed": poly_str(b),
                   "deg_a": deg(a), "deg_b": deg(b), "d": d,
                   "n": n, "n_prime": npr, "q": q, "r": r,
                   "field_polynomial": field_poly_str(n),
                   "N": res["N"], "conjectured_bound": bound,
                   "ratio": res["N"] / bound, "deg_P": res["deg_P"],
                   "pole_roots_present": res["pole_roots_present"],
                   "deg_gcd_with_b": res["deg_gcd_with_b"],
                   "instruments_run": ["gcd"] + (["I1_brute"] if i1 is not None else []),
                   "I1_brute": i1,
                   "above_conjectured_bound": res["N"] > bound}
            if i1 is not None and i1 != res["N"]:
                brute_disagree.append(row)
            if res["pole_roots_present"]:
                pole_hits += 1
            if res["N"] > bound:
                exceed.append(row)
            hist[res["N"]] = hist.get(res["N"], 0) + 1
            if res["N"] > mx[0]:
                mx = (res["N"], row)
            rows.append(row)
        label = "n%d_np%d" % (n, npr)
        cells_out[label] = {
            "n": n, "n_prime": npr, "q": q, "r": r, "draws": DRAWS,
            "field_polynomial": field_poly_str(n), "seed_stream": stream_label(n, npr),
            "max_N": mx[0], "max_N_draw": mx[1],
            "N_histogram": dict(sorted(hist.items())),
            "conjectured_bound_at_d_le_3": DEG_MAX ** (q + 1) + (1 << (npr - r)) + q * DEG_MAX ** q,
            "draws_above_conjectured_bound": sum(1 for r_ in rows if r_["above_conjectured_bound"]),
            "draws_with_a_shared_root_of_P_and_b": pole_hits,
            "I1_brute_run": rows[0]["I1_brute"] is not None,
            "rows": rows,
        }
        with open(run.path("cells", label + ".json"), "w") as fh:
            json.dump(cells_out[label], fh, indent=1, sort_keys=False)
        run.log("   (%d, %d) q=%d r=%d: max N = %d (bound at d=3 is %d), hist %s, "
                "draws above the conjectured bound = %d, brute cross-check = %s"
                % (n, npr, q, r, mx[0], cells_out[label]["conjectured_bound_at_d_le_3"],
                   cells_out[label]["N_histogram"],
                   cells_out[label]["draws_above_conjectured_bound"],
                   "run on every draw" if cells_out[label]["I1_brute_run"] else
                   "not affordable (2^%d elements)" % n))
    raw["stage_4_cells"] = cells_out
    raw["per_cell_json_files"] = ["cells/%s.json" % k for k in cells_out]
    raw["M5"] = {k: {"max_N": v["max_N"], "conjectured_bound_at_d_le_3":
                     v["conjectured_bound_at_d_le_3"], "N_histogram": v["N_histogram"],
                     "draws_above_conjectured_bound": v["draws_above_conjectured_bound"]}
                 for k, v in cells_out.items()}
    raw["draws_above_conjectured_bound"] = exceed
    raw["brute_cross_check_disagreements"] = brute_disagree
    raw["obligation_note"] = (
        "This run produces the fixture only. Per specification stage_4.obligation the "
        "Stage 5 report must either write out the pole bookkeeping of (D)(ii) or record "
        "the extension as WITHDRAWN; a fixture that passes without the bookkeeping "
        "written out leaves the extension conjectural and it is recorded as "
        "withdrawn-as-stated. (A) and (B) are untouched by this stage either way.")
    if brute_disagree:
        run.warn("STOP: the gcd count and the brute enumeration disagree on %d draws"
                 % len(brute_disagree))
        run.finish(raw, "invalid_measurement",
                   "gcd count vs brute enumeration disagreement on %d draws" % len(brute_disagree),
                   certificate={"kind": "none", "verified": None, "verifier": "n/a"},
                   anomalies=[{"branch": "F5", "detail": "instrument disagreement in Stage 4"}])
        return 1
    run.log("\n== Summary: %d draws, %d above the conjectured bound"
            % (DRAWS * len(CELLS), len(exceed)))
    run.finish(raw, "completed_valid",
               "%d rational-lambda draws counted exactly; %d above the conjectured "
               "bound d^{q+1} + 2^{n'-r} + q d^q" % (DRAWS * len(CELLS), len(exceed)),
               certificate={"kind": "none", "verified": True,
                            "verifier": "pure measurement run: no discrete-log solve and "
                                        "no factor-base relation is claimed. The counts at "
                                        "n = 11 are cross-checked against brute enumeration "
                                        "of all 2^11 field elements."},
               anomalies=([{"branch": "F4", "detail": "draw(s) above the conjectured "
                            "rational bound", "rows": exceed}] if exceed else []))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
