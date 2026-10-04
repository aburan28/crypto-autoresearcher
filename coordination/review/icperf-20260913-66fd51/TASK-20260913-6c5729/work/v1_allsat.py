"""V1: independently re-verify EVERY SAT answer in the run (not just the five),
and evaluate every recorded WDSat assignment against the shipped ANF."""
from __future__ import annotations

import json
import os
from collections import Counter

from valgf import GF2n, BinaryCurve, INF, f3_summation, parse_info
from v1_anf import evaluate as anf_evaluate

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
OUT = os.path.dirname(os.path.abspath(__file__))

_cache = {}


def field_for(inst):
    if inst not in _cache:
        info = parse_info(os.path.join(BENCH, f"INFO{inst}.dimacs"))
        F = GF2n(info["n"], info["modulus_bits"])
        _cache[inst] = (info, F, BinaryCurve(F, 1, 1), BinaryCurve(F, 0, 1))
    return _cache[inst]


def decompose_matches(curve, xs, xr):
    pts = [curve.points_with_x(v) for v in xs]
    if any(len(p) == 0 for p in pts):
        return None
    k = 0
    for P1 in pts[0]:
        for P2 in pts[1]:
            for P3 in pts[2]:
                S = curve.add(curve.add(P1, P2), P3)
                if S is not INF and S[0] == xr:
                    k += 1
    return k


def main():
    rows = [json.loads(l) for l in open(os.path.join(RUN, "results.jsonl"))]
    tally = Counter()
    disagreements = []
    anf_checks = []
    detail = []

    for r in rows:
        tally[(r.get("phase"), r.get("engine"), r.get("config"), r.get("status"))] += 1

    sat_rows = [r for r in rows if r.get("status") == "SAT" and "verification" in r]
    cert_rows = [r for r in rows if r.get("config") == "shipped" or r.get("engine") == "certificate"]

    for r in sat_rows:
        inst = r["instance"]
        info, F, E, TW = field_for(inst)
        l = info["l"]
        xr = F.from_bits_lsb_first(info["xr_bits"])
        xs = [F.from_bits_lsb_first(b) for b in r["verification"]["x_bits"]]
        mine_E = decompose_matches(E, xs, xr)
        mine_TW = decompose_matches(TW, xs, xr)
        f3 = f3_summation(F, xs[0], xs[1], xs[2], xr)
        my_verified = bool(mine_E)
        rec = bool(r["verification"]["verified"])
        if my_verified != rec:
            disagreements.append({"instance": inst, "engine": r["engine"],
                                  "config": r["config"], "recorded": rec,
                                  "mine": my_verified})
        detail.append({
            "instance": inst, "engine": r["engine"], "config": r["config"],
            "x_hex": [hex(v) for v in xs], "xr_hex": hex(xr),
            "f3_is_zero": f3 == 0,
            "E_decomposition_sign_choices": mine_E,
            "twist_decomposition_sign_choices": mine_TW,
            "recorded_verified": rec, "my_verified": my_verified,
            "matches_shipped_certificate_as_set":
                r["verification"].get("matches_shipped_certificate_as_set"),
        })

        if r.get("engine") == "wdsat" and r.get("assignment"):
            ev = anf_evaluate(os.path.join(BENCH, f"X{inst}.anf"), r["assignment"])
            anf_checks.append({
                "instance": inst, "config": r["config"],
                "n_equations": ev["n_equations"],
                "unsatisfied_under_xor_eq_1": ev["n_eq_xor_equals_0"],
                "core_decodes_to_recorded_x_bits":
                    [r["assignment"][i * l:(i + 1) * l] for i in range(3)]
                    == r["verification"]["x_bits"],
            })

    # shipped certificate rows
    certs = [r for r in rows if r.get("phase") == "A" and "certificate" in json.dumps(r)[:200].lower()
             and r.get("engine") in (None, "certificate")]

    summary = {
        "n_rows": len(rows),
        "n_sat_rows_with_verification_block": len(sat_rows),
        "n_recorded_verified_true": sum(1 for r in sat_rows if r["verification"]["verified"]),
        "n_recorded_verified_false": sum(1 for r in sat_rows if not r["verification"]["verified"]),
        "n_my_verified_true": sum(1 for d in detail if d["my_verified"]),
        "n_my_verified_false": sum(1 for d in detail if not d["my_verified"]),
        "n_f3_zero": sum(1 for d in detail if d["f3_is_zero"]),
        "disagreements_with_producer_decoder": disagreements,
        "n_wdsat_assignments_checked_against_anf": len(anf_checks),
        "n_wdsat_assignments_with_any_unsatisfied_equation":
            sum(1 for a in anf_checks if a["unsatisfied_under_xor_eq_1"] != 0),
        "n_wdsat_core_bits_matching_recorded_x_bits":
            sum(1 for a in anf_checks if a["core_decodes_to_recorded_x_bits"]),
        "unverified_rows": [d for d in detail if not d["my_verified"]],
    }
    with open(os.path.join(OUT, "v1_allsat.json"), "w") as fh:
        json.dump({"summary": summary, "detail": detail, "anf_checks": anf_checks},
                  fh, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True)[:4000])


if __name__ == "__main__":
    main()
