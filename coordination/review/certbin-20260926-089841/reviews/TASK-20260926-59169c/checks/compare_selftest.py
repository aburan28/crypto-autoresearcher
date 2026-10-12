#!/usr/bin/env python3
"""TASK-20260926-59169c: mutation self-test of checks/compare.py (non-vacuity).

Copies the J7/J1 outputs and the key file of the archived snapshot into a
scratch tree (the run directory and the other inputs are symlinked, read
only), plants one discrepancy per item class, runs compare.py on the mutated
tree, and requires every planted discrepancy to be reported as a
disagreement (and nothing else to change). The archived files are never
modified.
"""
import argparse, gzip, json, os, shutil, subprocess, sys

REV = "coordination/review/certbin-20260926-089841"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    W = a.work
    if os.path.exists(W):
        shutil.rmtree(W)
    # symlink tree, then materialize the files we mutate
    for top in ("experiments", "coordination"):
        pass
    os.makedirs(os.path.join(W, REV, "reviews"), exist_ok=True)
    os.makedirs(os.path.join(W, "experiments/EXP-CERTBIN-ddfe75/runs"), exist_ok=True)
    os.symlink(os.path.join(a.snap, "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"),
               os.path.join(W, "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"))
    os.symlink(os.path.join(a.snap, REV, "blind"), os.path.join(W, REV, "blind"))
    for t in ("TASK-20260926-83cebf", "TASK-20260926-f0e5a4"):
        shutil.copytree(os.path.join(a.snap, REV, "reviews", t), os.path.join(W, REV, "reviews", t))
    shutil.copy(os.path.join(a.snap, REV, "blind-inputs-key.json"), os.path.join(W, REV, "blind-inputs-key.json"))
    j7 = os.path.join(W, REV, "reviews/TASK-20260926-83cebf")
    j1 = os.path.join(W, REV, "reviews/TASK-20260926-f0e5a4")

    d7 = json.load(open(os.path.join(j7, "rederivation.json")))
    # M1 row bit flip in the kept unsat system of slot 7
    h = d7["Q0"]["slots"]["7"]["unsat"]["row_hex"][3]
    d7["Q0"]["slots"]["7"]["unsat"]["row_hex"][3] = format(int(h, 16) ^ 1, "x")
    # M3 Q1 rank
    d7["Q1"]["unsat"]["NCONV-REPLAY:33:unsat"]["rank_4"] += 1
    # M4 Q3 dims
    d7["Q3"]["BS-010"]["dims"][0] += 1
    # M5 Q5 c bit
    d7["Q5"]["BS-005"]["c"][0] ^= 1
    # M7 Q2 P
    d7["Q2"]["BS-004"]["P"] += 1
    # M9 Q3 one_first_iteration
    d7["Q3"]["BS-001"]["one_first_iteration"] = 0 if d7["Q3"]["BS-001"]["one_first_iteration"] != 0 else 1
    json.dump(d7, open(os.path.join(j7, "rederivation.json"), "w"))
    # M2 stream: s of slot 20 attempt 1
    recs = [json.loads(l) for l in gzip.open(os.path.join(j7, "stream-replay.jsonl.gz"), "rt")]
    for r in recs:
        if r["arm"] == "N-CONV" and r["slot"] == 20 and r["attempt"] == 1:
            r["s"] += 1
        if r["arm"] == "N-CONV" and r["slot"] == 40 and r["attempt"] == 0:  # M10 discarded/kept row flip -> hash
            r["row_hex"][0] = format(int(r["row_hex"][0], 16) ^ 2, "x")
    with gzip.open(os.path.join(j7, "stream-replay.jsonl.gz"), "wt") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    # M6 J1 verdict
    v1 = json.load(open(os.path.join(j1, "verification.json")))
    v1["certificates_VC3"]["per_line"][5]["verified"] = False
    json.dump(v1, open(os.path.join(j1, "verification.json"), "w"))
    # M8 key mapping swap of two N-CONV unsat pool systems (BS-018 slot 0, BS-020 slot 1)
    km = json.load(open(os.path.join(W, REV, "blind-inputs-key.json")))
    km["BS-018"], km["BS-020"] = km["BS-020"], km["BS-018"]
    json.dump(km, open(os.path.join(W, REV, "blind-inputs-key.json"), "w"))

    here = os.path.dirname(os.path.abspath(__file__))
    tmpout = os.path.join(W, "comparison-mutated.json")
    subprocess.run([sys.executable, os.path.join(here, "compare.py"), "--snap", W, "--out", tmpout], check=True,
                   stdout=subprocess.DEVNULL, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    c = json.load(open(tmpout))
    ps = {r["slot"]: r for r in c["Q0"]["N-CONV"]["per_slot"]}
    q1 = {r["slot"]: r for r in c["Q1"]["per_system"]["unsat"]}
    pool = {r["label"]: r for r in c["Q2_Q5_pool"]["per_system"]}
    det = {
        "M1_row_bit_slot7": not ps[7]["unsat_rows_decoded"]["agree"],
        "M2_attempt_s_slot20": not ps[20]["every_attempt"]["agree"] and any(d["field"] == "s" and d["attempt"] == 1 for d in ps[20]["every_attempt"]["disagreements"]),
        "M10_attempt_row_hash_slot40": not ps[40]["every_attempt"]["agree"] and any(d["field"].startswith("E_sha256") for d in ps[40]["every_attempt"]["disagreements"]),
        "M3_Q1_rank_slot33": not q1[33]["rank"]["agree"],
        "M4_Q3_dims_BS010": not pool["BS-010"]["Q3.dims_per_iteration"]["agree"],
        "M5_Q5_c_BS005": not pool["BS-005"]["Q5.c"]["agree"],
        "M7_Q2_P_BS004": not pool["BS-004"]["Q2.P"]["agree"],
        "M9_Q3_one_first_iteration_BS001": not pool["BS-001"]["Q3.one_first_iteration"]["agree"],
        "M6_J1_verdict_cid5": any(x["cid"] == 5 and "verified" in x.get("disagree", {}) for x in c["J1_vs_run_certificate_verification"]["lines_with_any_disagreement"]),
        "M8_key_swap_BS018_BS020_rows": (not pool["BS-018"]["map.pool_equations_equal_run_E_hex"]["agree"]) and (not pool["BS-020"]["map.pool_equations_equal_run_E_hex"]["agree"]),
    }
    # what else the key swap moved (floor/ceiling illustration)
    swap_other = {lab: {k: v["agree"] for k, v in pool[lab].items() if isinstance(v, dict) and "agree" in v and v["agree"] is False}
                  for lab in ("BS-018", "BS-020")}
    res = {"detected": det, "all_detected": all(det.values()),
           "key_swap_items_that_still_agreed_note": "items of BS-018/BS-020 NOT flagged by the swap are those at a common value for both systems (floor/ceiling or shared value)",
           "key_swap_flagged_items": swap_other}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res, indent=1))
    shutil.rmtree(W)


if __name__ == "__main__":
    main()
