"""Red-team replay of the producer's sampled inputs (TASK-20261023-62eb31).

Executes the frozen driver experiments/EXP-CZLIFT-ed8113/implementation/run.py
build() in its own RNG order, with run.dependent() replaced by a recorder that
returns None (dependent() consumes no randomness, so the RNG stream and every
sampled curve/point are unchanged). The planted controls are recorded but not
used. Output: one JSON per seed with every valid trial's (p, r, a, b, lifted
points, fitted A2, A4, A6). The replay is checked against the run record by the
per-cell mean naive point height (computed by trial() before dependent()), and
by the one recorded relation (seed 20261009, p = 101, r = 2) re-found with the
producer's own dependent() on the replayed input.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "EXP-CZLIFT-ed8113", "implementation"))
import run as driver  # noqa: E402

ORIG_DEPENDENT = driver.dependent
ORIG_TRIAL = driver.trial
ORIG_CONTROL = driver.planted_control

state = {"ctx": None, "rows": []}


def rec_dependent(lifted, A2, A4, bound):
    ctx = state["ctx"]
    if ctx is not None and ctx.get("kind") == "trial":
        X, Y = lifted[0]
        A6 = Y * Y - X ** 3 - A2 * X * X - A4 * X
        state["rows"].append({**{k: v for k, v in ctx.items() if k != "kind"},
                              "pts": [[str(x), str(y)] for x, y in lifted],
                              "A2": str(A2), "A4": str(A4), "A6": str(A6)})
    return None


def rec_trial(p, a, b, r, rng):
    state["ctx"] = {"kind": "trial", "p": p, "a": a, "b": b, "r": r}
    out = ORIG_TRIAL(p, a, b, r, rng)
    state["ctx"] = None
    return out


def rec_control(p, rng):
    state["ctx"] = {"kind": "control"}
    out = ORIG_CONTROL(p, rng)
    state["ctx"] = None
    return out


def main():
    driver.dependent = rec_dependent
    driver.trial = rec_trial
    driver.planted_control = rec_control
    out = {}
    for seed, run_id in ((20261009, "RUN-CZLIFT-c3f8a8"), (20261010, "RUN-CZLIFT-218843")):
        state["rows"] = []
        _, raw = driver.build(seed, 100, list(driver.PRIMES))
        rec = json.load(open(os.path.join(REPO, "experiments", "EXP-CZLIFT-ed8113", "runs", run_id, "raw-result.json")))
        maxdiff = 0.0
        for c_new, c_old in zip(raw["cells"], rec["raw"]["cells"]):
            assert (c_new["p"], c_new["r"], c_new["valid"]) == (c_old["p"], c_old["r"], c_old["valid"])
            maxdiff = max(maxdiff, abs(c_new["mean_log_height_point"] - c_old["mean_log_height_point"]),
                          abs(c_new["mean_log_height_A4"] - c_old["mean_log_height_A4"]))
        # index within cell
        idx = {}
        for row in state["rows"]:
            k = (row["p"], row["r"])
            row["i"] = idx.get(k, 0)
            idx[k] = row["i"] + 1
        assert len(state["rows"]) == 1600
        # re-find recorded relations with the producer's own search
        refound = []
        for row in state["rows"]:
            if row["p"] == 101:
                lifted = [(Fraction(x), Fraction(y)) for x, y in row["pts"]]
                rel = ORIG_DEPENDENT(lifted, Fraction(row["A2"]), Fraction(row["A4"]), driver.RELATION_BOUND)
                if rel is not None:
                    refound.append({"p": row["p"], "r": row["r"], "i": row["i"], "pts": row["pts"], "rel": rel})
        rec_rel = [(c["p"], c["r"], r) for c in rec["raw"]["cells"] for r in c["relations"] if c["p"] == 101]
        out[str(seed)] = {"run_id": run_id, "replay_max_abs_height_diff": maxdiff,
                          "recorded_relations_p101": rec_rel, "refound_relations_p101": refound,
                          "rows": state["rows"]}
        print(seed, "maxdiff", maxdiff, "recorded", rec_rel, "refound", [(x["p"], x["r"], x["i"], x["rel"], x["pts"]) for x in refound])
    json.dump(out, open(os.path.join(HERE, "rt_replay_inputs.json"), "w"))


if __name__ == "__main__":
    main()
