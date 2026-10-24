"""J3 phase-2 comparison (validator TASK-20261022-67902e).

Regenerates the producer's sampled inputs (curves, points, control draws) by calling only the
frozen SAMPLER (harness.czlift.random_point, harness.toycurve.EllipticCurve) in the RNG order of
run.py build(); every fit, multiple, relation search and height is computed with the SEALED blind
code (blind/relsearch.py, sha256 f9830f7e...). Compares per cell and per control with raw-result.json.
Usage: python3 -B -I j3_replay.py OUT.json
"""
import json
import math
import random
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE / "blind"))
sys.path.insert(0, str(REPO))
import relsearch as rs  # noqa: E402  (sealed blind code)
from harness import czlift  # noqa: E402  (sampler only)
from harness.toycurve import EllipticCurve  # noqa: E402  (sampler only)

PRIMES = [101, 211, 401, 809, 1601, 3203, 6421, 12809]
RUNS = {20261009: "RUN-CZLIFT-c3f8a8", 20261010: "RUN-CZLIFT-218843"}


def draw_curve(rng, p):
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p:
            return a, b


def draw_points(rng, p, a, b, r):
    E = EllipticCurve(p, a, b)
    pts = []
    while len(pts) < r:
        P = czlift.random_point(E, rng)
        if all(P[0] != Q[0] for Q in pts):
            pts.append(P)
    return pts


def replay(seed, trials=100):
    rng = random.Random(seed)
    cells, dep_rows = [], []
    for p in PRIMES:
        for r in (2, 3):
            valid, dependent, rels, hsum, h4sum, excl, y0 = 0, 0, [], 0.0, 0.0, 0, 0
            for t in range(trials):
                a, b = draw_curve(rng, p)
                pts = draw_points(rng, p, a, b, r)
                L = [(rs.sym(x, p), rs.sym(y, p)) for x, y in pts]
                y0 += any(y == 0 for _, y in L)
                E = rs.fit(L)
                coeff_dens_prime_to_p = all(c.denominator % p for c in E.ainvs())
                Dp = rs.frac_mod_p(E.disc(), p)
                if not coeff_dens_prime_to_p or Dp in (None, 0):
                    excl += 1
                    continue
                # reduction of the fit mod p equals the sampled curve (a, b)
                red = [rs.frac_mod_p(c, p) for c in E.ainvs()]
                assert red == [0, 0, 0, a % p, b % p], (p, r, t)
                T = [(Fr(x), Fr(y)) for x, y in L]
                assert all(E.on_curve(P) for P in T)
                found = rs.relation_search(E, T, 6)
                valid += 1
                for x, _ in L:  # same summation order as the producer: trial order, then point order
                    hsum += rs.naive_height((Fr(x), None))
                h4sum += math.log(max(abs(E.a4.numerator), abs(E.a4.denominator), 1))
                if found:
                    dependent += 1
                    rels.append([list(m) for m in found])
                    dep_rows.append({"seed": seed, "p": p, "r": r, "trial": t, "a": a, "b": b,
                                     "mod_p_points": [list(P) for P in pts], "lifts": [list(l) for l in L],
                                     "fitted_ainvs": [str(c) for c in E.ainvs()],
                                     "disc": str(E.disc()), "relations_bound6": [list(m) for m in found],
                                     "P1_torsion_order_upto12": None})
                    Pt = T[0]
                    Q = None
                    for k in range(1, 13):
                        Q = E.add(Q, Pt)
                        if Q is None:
                            dep_rows[-1]["P1_torsion_order_upto12"] = k
                            break
                    # wider bound for context
                    dep_rows[-1]["relations_bound12"] = [list(m) for m in rs.relation_search(E, T, 12)]
                    if r == 2:
                        (x1, y1), (x2, y2) = L
                        dep_rows[-1]["identity_2P1_plus_P2_eq_O"] = (x1 - x2) ** 2 * (2 * x1 + x2) == (y1 - y2) ** 2
                        dep_rows[-1]["identity_2P1_minus_P2_eq_O"] = (x1 - x2) ** 2 * (2 * x1 + x2) == (y1 + y2) ** 2
            cells.append({"p": p, "r": r, "trials": trials, "valid": valid, "excluded": excl, "dependent": dependent,
                          "relations": rels, "mean_log_height_point": hsum / (r * valid) if valid else None,
                          "mean_log_height_A4": h4sum / valid if valid else None, "trials_with_y0": y0})
    controls = []
    for p in PRIMES:
        for _ in range(3):
            a, b = draw_curve(rng, p)
            P = czlift.random_point(EllipticCurve(p, a, b), rng)
            X1, Y1 = rs.sym(P[0], p), rs.sym(P[1], p)
            k = rng.randrange(1, 5)
            A4 = a + p * k
            E = rs.Curve(0, 0, 0, A4, Y1 * Y1 - X1 ** 3 - A4 * X1)
            P1 = (Fr(X1), Fr(Y1))
            P2 = E.add(P1, P1)
            found = rs.relation_search(E, [P1, P2], 6)
            minmax = min((max(abs(v) for v in m) for m in found), default=None)
            shortest = sorted(m for m in found if max(abs(v) for v in m) == minmax) if found else []
            controls.append({"p": p, "planted_in_relations": (2, -1) in set(found),
                             "shortest_is_planted": shortest == [(2, -1)],
                             "relations": [list(m) for m in found], "y1_zero": Y1 == 0, "k": k})
    return cells, controls, dep_rows


def compare(seed, cells, controls, run_dir):
    raw = json.loads((run_dir / "raw-result.json").read_text())["raw"]
    out = {"cells": [], "controls": {}}
    for mine, rec in zip(cells, raw["cells"]):
        rec_rels = sorted(rs.canon(tuple(m)) for m in rec["relations"])
        my_short = sorted(min(rl, key=lambda m: max(abs(v) for v in m)) for rl in mine["relations"])
        my_short = sorted(tuple(m) for m in my_short)
        out["cells"].append({
            "p": rec["p"], "r": rec["r"], "same_cell": (mine["p"], mine["r"]) == (rec["p"], rec["r"]),
            "valid": (mine["valid"], rec["valid"]), "dependent": (mine["dependent"], rec["dependent"]),
            "shortest_relations_equal": my_short == rec_rels, "mine_shortest": [list(m) for m in my_short],
            "recorded": rec["relations"],
            "height_point_absdiff": abs(mine["mean_log_height_point"] - rec["mean_log_height_point"]),
            "height_A4_absdiff": abs(mine["mean_log_height_A4"] - rec["mean_log_height_A4"]),
            "trials_with_y0": mine["trials_with_y0"], "excluded_mine": mine["excluded"]})
    out["controls"] = {
        "n": len(controls), "recorded": raw["controls"],
        "blind_planted_in_relations": [c["planted_in_relations"] for c in controls],
        "blind_shortest_is_planted": [c["shortest_is_planted"] for c in controls],
        "agree_elementwise": [c["shortest_is_planted"] for c in controls] == raw["controls"],
        "any_y1_zero": any(c["y1_zero"] for c in controls),
        "max_relations_per_control": max(len(c["relations"]) for c in controls),
    }
    cs = out["cells"]
    out["summary"] = {
        "all_cells_aligned": all(c["same_cell"] for c in cs),
        "valid_equal_all": all(c["valid"][0] == c["valid"][1] for c in cs),
        "dependent_equal_all": all(c["dependent"][0] == c["dependent"][1] for c in cs),
        "relations_equal_all": all(c["shortest_relations_equal"] for c in cs),
        "max_height_point_absdiff": max(c["height_point_absdiff"] for c in cs),
        "max_height_A4_absdiff": max(c["height_A4_absdiff"] for c in cs),
        "trials_with_y0_total": sum(c["trials_with_y0"] for c in cs),
        "excluded_total_mine": sum(c["excluded_mine"] for c in cs),
        "blind_valid_total": sum(c["valid"][0] for c in cs),
        "blind_dependent_total": sum(c["dependent"][0] for c in cs),
        "controls_detected_blind": sum(out["controls"]["blind_planted_in_relations"]),
    }
    return out


def main():
    t0 = time.time()
    res = {"task_id": "TASK-20261022-67902e", "blind_code_sha256": {
        "relsearch.py": __import__("hashlib").sha256((HERE / "blind" / "relsearch.py").read_bytes()).hexdigest()}}
    for seed, run in RUNS.items():
        cells, controls, dep_rows = replay(seed)
        res[run] = compare(seed, cells, controls, REPO / "experiments" / "EXP-CZLIFT-ed8113" / "runs" / run)
        res[run]["seed"] = seed
        res[run]["dependent_rows"] = dep_rows
    res["elapsed_seconds"] = round(time.time() - t0, 1)
    Path(sys.argv[1]).write_text(json.dumps(res, indent=1, default=str) + "\n")
    for run in RUNS.values():
        print(run, json.dumps(res[run]["summary"]), json.dumps({k: v for k, v in res[run]["controls"].items()
                                                                 if k not in ("recorded", "blind_planted_in_relations", "blind_shortest_is_planted")}))
        for d in res[run]["dependent_rows"]:
            print("  dependent:", json.dumps(d))
    print("elapsed", res["elapsed_seconds"])


if __name__ == "__main__":
    main()
