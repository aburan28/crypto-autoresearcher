#!/usr/bin/env python3
"""V3 part 2: fixture instance recomputed independently, plus a per-draw
rank table for the named draws the report cites.  Reuses only this task's own
v3_independent.py primitives (no harness/ code).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3_independent import (build_stilde, profile_from_stilde, poly_eval,
                            on_curve, point_add, s3_eval_scalar, load)

MONNAMES = ["a0", "a1", "a2", "a3", "a4", "a5"]


def mask_name(m):
    if m == 0:
        return "1"
    return "*".join(MONNAMES[i] for i in range(6) if m >> i & 1)


def main():
    out = {}
    # ---- fixture instance ------------------------------------------------
    d = load("RUN-PFDR-fd901a-fixture-p4099")
    raw = d["raw"]
    p = raw["curve"]["p"]
    A, B = raw["curve"]["a"], raw["curve"]["b"]
    xR = raw["target"]["x_R"]
    P1 = tuple(raw["target"]["P1"])
    P2 = tuple(raw["target"]["P2"])
    R = tuple(raw["target"]["R"])
    st = build_stilde(A, B, xR, p)
    prof = profile_from_stilde(st, p)
    prod_st = {mask_name(m): c for m, c in st.items()}
    theirs_st = raw["independent_stilde"]
    st_match = prod_st == {k: v for k, v in theirs_st.items()}
    fx = raw["fixture_draw"]
    out["fixture"] = {
        "p": p, "A": A, "B": B, "x_R": xR, "P1": P1, "P2": P2, "R": R,
        "P1_on_curve": on_curve(P1[0], P1[1], A, B, p),
        "P2_on_curve": on_curve(P2[0], P2[1], A, B, p),
        "R_on_curve": on_curve(R[0], R[1], A, B, p),
        "my_P1_plus_P2": point_add(P1, P2, A, p),
        "certificate_reverifies": point_add(P1, P2, A, p) == R,
        "S3_vanishes_at_(x1,x2,xR)": s3_eval_scalar(A, B, raw["target"]["x1"],
                                                    raw["target"]["x2"], xR, p) == 0,
        "my_stilde_term_count": len(st),
        "recorded_generator_term_count": fx["generator_term_counts"][0],
        "my_stilde_equals_producer_independent_stilde": st_match,
        "stilde_coefficient_diff_count": sum(
            1 for k in set(prod_st) | set(theirs_st)
            if prod_st.get(k) != theirs_st.get(k)),
        "my_profile": prof,
        "recorded_meter_full_rank": fx["profile_full_rank"],
        "recorded_meter_top_rank": fx["profile_top_rank"],
        "recorded_meter_fall_dim": fx["profile_fall_dim"],
        "producer_independent_ranks": raw["independent_ranks"],
        "agrees_with_meter": (prof["full_rank"] == fx["profile_full_rank"]
                              and prof["top_rank"] == fx["profile_top_rank"]
                              and prof["fall_dim"] == fx["profile_fall_dim"]),
        "planted_digits": fx["planted_digits"],
        "planted_point_is_root_of_my_stilde":
            poly_eval(st, fx["planted_digits"], p) == 0,
    }

    # ---- named per-draw table (the draws cited in the report) ------------
    table = []
    for label, run in [("p64", "RUN-PFDR-fd901a-sweep-p64"),
                       ("p256", "RUN-PFDR-fd901a-sweep-p256")]:
        dd = load(run)
        pp = dd["metrics"]["prime"]
        wanted = [("semaev", 1101, 1), ("semaev", 1104, 3), ("semaev", 1108, 5),
                  ("semaev_named_p256", "NIST-P-256", 1),
                  ("semaev_named_p256", "NIST-P-256", 4),
                  ("noncurve_cubic", 1101, 1)]
        for arm, cs, ts in wanted:
            hits = [x for x in dd["raw"]["draws"]
                    if x["arm"] == arm and x["curve_seed"] == cs
                    and x["target_seed"] == ts]
            if not hits:
                continue
            x = hits[0]
            cert = x["certificate"]["statement"]
            aa, bb = ((cert["curve"]["a"], cert["curve"]["b"])
                      if x["certificate"]["kind"] == "decomposition"
                      else (cert["cubic"]["a"], cert["cubic"]["b"]))
            s = build_stilde(aa, bb, x["x_R"], pp)
            pr = profile_from_stilde(s, pp)
            table.append({
                "prime_label": label, "prime_bits": dd["metrics"]["prime_bits"],
                "arm": arm, "curve_seed": cs, "target_seed": ts,
                "A": aa, "B": bb, "x_R": x["x_R"],
                "my_full_rank_D3_D6": pr["full_rank"],
                "my_top_rank_D3_D6": pr["top_rank"],
                "my_fall_dim_D3_D6": pr["fall_dim"],
                "my_row_count_D3_D6": pr["row_count"],
                "recorded_full_rank": x["profile_full_rank"],
                "recorded_top_rank": x["profile_top_rank"],
                "recorded_fall_dim": x["profile_fall_dim"],
                "agrees": (pr["full_rank"] == x["profile_full_rank"]
                           and pr["top_rank"] == x["profile_top_rank"]
                           and pr["fall_dim"] == x["profile_fall_dim"]),
            })
    out["named_draw_table"] = table
    json.dump(out, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()
