#!/usr/bin/env python3
"""J3 (DEC-20260924-5b1c8e R-2): was the C-SELF coverage rule of deviation 2
the one that produced the archived selftest.json, and did that self-test
finish before phase 1? Read-only; no phase is re-run.

Checks, from archived bytes only:
  S1 every recorded case's (D, neq, planted?) follows the committed schedule
     of selftest.py (schedule[(draw - 1) % 6]);
  S2 applying the committed stop rule (>= 5 draws AND all four coverage
     counters > 0) to the recorded cases stops exactly at the recorded last
     draw, and the recorded coverage counters equal a recount;
  S3 selftest.json finished_at precedes the first driver invocation and the
     phase-1 checkpoint; its seed equals S_selftest of the specification;
  S4 how many recorded systems reach iterations_to_fixpoint >= 2 (where the
     semi-naive and literal rules could differ).
"""
import gzip
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0")
SCHEDULE = [(3, 5, False), (3, 6, False), (4, 6, True), (3, 4, False), (4, 5, False), (3, 6, True)]  # selftest.py line 239


def main():
    st = json.load(open(os.path.join(RUN, "selftest.json")))
    w = st["C-SELF"]["items"]["W_D_vs_brute_force_random_systems"]
    cases = w["cases"]
    s1 = [c["draw"] for c in cases if (c["D"], c["neq"], c["planted"] is not None) != SCHEDULE[(c["draw"] - 1) % 6]]
    cover = {"refuted_it0": 0, "refuted_it_ge1": 0, "planted": 0, "unrefuted_multi_iteration": 0}
    stop_at = None
    for c in cases:
        e = c["engine"]
        if e["one"]:
            cover["refuted_it0" if e["one_first_iteration"] == 0 else "refuted_it_ge1"] += 1
        elif e["iterations_to_fixpoint"] >= 1:
            cover["unrefuted_multi_iteration"] += 1
        if c["planted"] is not None:
            cover["planted"] += 1
        if c["draw"] >= 5 and all(v > 0 for v in cover.values()):
            stop_at = c["draw"]
            break
    invs = [json.loads(line) for line in open(os.path.join(RUN, "checkpoint", "invocations.jsonl"))]
    p1 = json.load(gzip.open(os.path.join(RUN, "checkpoint", "p1-sets-oracles-base.json.gz"), "rt"))
    res = {"task_id": "TASK-20260924-c83b05", "joint": "J3", "check": "C-SELF coverage rule (R-2)",
           "S1_cases_off_schedule": s1,
           "S2_stop_rule_stops_at": stop_at, "S2_recorded_last_draw": cases[-1]["draw"],
           "S2_recount_coverage": cover, "S2_recorded_coverage": w["coverage"],
           "S2_consistent": stop_at == cases[-1]["draw"] and cover == w["coverage"],
           "S3_selftest_finished_at": st["finished_at"], "S3_first_driver_invocation": invs[0]["at"],
           "S3_phase1_finished_at": p1["finished_at"],
           "S3_selftest_before_phase1": st["finished_at"] < invs[0]["at"] < p1["finished_at"],
           "S3_seed": st["S_selftest"], "S3_seed_equals_spec": st["S_selftest"] == 2026092430099,
           "S4_iterations_histogram": {str(k): sum(1 for c in cases if c["engine"]["iterations_to_fixpoint"] == k) for k in range(4)},
           "S4_cases_with_ge2_iterations": sum(1 for c in cases if c["engine"]["iterations_to_fixpoint"] >= 2),
           "all_cases_match_recorded": all(c["match"] for c in cases)}
    json.dump(res, open(os.path.join(HERE, "selftest_rule_results.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
