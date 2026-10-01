#!/usr/bin/env python3
"""TASK-20260926-59169c CP-4 (b): third, specification-literal check for the
one CP-2 disagreement class (per-line counting flags: run certificate-
verification.json counts_for_M4 / counts_for_W4 against J1 counts_toward_M4 /
counts_toward_w on 824 flat-v1 lines).

DECLARED SCOPE: 6 systems (CP-6 cap: at most 20 systems or stream steps):
  N-CONV:0:unsat      (M_4 flat |mu|<=2, W_4 flat |mu|<=2, W_4 wdag one-node)
  N-CONVL:0:unsat     (the only M_4 flat with max |mu| = 1)
  N-CONVL:2:unsat     (W_4 flat with max |mu| = 3; two-node wdag)
  N-CONV17:83:unsat   (the only N-CONV17 W_4 flat with max |mu| = 3)
  C20:F-S3:5          (S3-C20)
  U62:F-S3:27         (S3-U62; W_4 flat max |mu| = 3, two-node wdag)
For every certificate line of these systems in the run's certificates.jsonl.gz,
own verification (checks/wdag_check.py) on f_k decoded from the run's
instances.jsonl.gz E_hex, then two readings of the frozen text:
  R-CF (object.certificate_format sentences read as eligibility): a verified
       flat-v1 is eligible for M_4 and for W_4 iff max |mu| <= 2; a valid
       wdag-v1 is eligible for W_4.
  R-MN (metrics MN1 / secondary M_4 metric): M_4 counted iff a verified flat-v1
       labelled M_4 with max |mu| <= 2; w counted iff a VERIFIED wdag-v1
       labelled W_4.
Per system: is it counted for M_4 and for W_4 under each reading, and do the
readings give the same per-system outcome?
"""
import argparse, gzip, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wdag_check as W  # noqa: E402

KEYS = ["N-CONV:0:unsat", "N-CONVL:0:unsat", "N-CONVL:2:unsat", "N-CONV17:83:unsat", "C20:F-S3:5", "U62:F-S3:27"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run = os.path.join(a.snap, "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e")
    inst = {}
    for l in gzip.open(os.path.join(run, "instances.jsonl.gz"), "rt"):
        r = json.loads(l)
        if r["key"] in KEYS:
            inst[r["key"]] = r
    lines = [json.loads(l) for l in gzip.open(os.path.join(run, "certificates.jsonl.gz"), "rt")]
    lines = [c for c in lines if c["key"] in KEYS]
    cv = {c["cid"]: c for c in json.load(open(os.path.join(run, "certificate-verification.json")))["certificates"]}
    res = {"declared_systems": KEYS, "lines": [], "per_system": {}}
    for k in KEYS:
        F = W.system_from_hex(inst[k]["E_hex"])
        sysrec = {"cf_M4": False, "cf_W4": False, "mn_M4": False, "mn_W4": False}
        for c in [c for c in lines if c["key"] == k]:
            if c["format"] == "flat-v1":
                ok, mx = W.check_flat(c["body"], F)
                cf_m4 = cf_w4 = ok and mx <= 2
                mn_m4 = ok and mx <= 2 and c["closure"] == "M_4"
                mn_w4 = False
            else:
                st, det = W.check_wdag(c["body"], F)
                ok = st == "valid"
                mx = det.get("max_mu")
                cf_m4 = False
                cf_w4 = ok
                mn_m4 = False
                mn_w4 = ok and c["closure"] == "W_4"
            rv = cv[c["cid"]]
            res["lines"].append({"cid": c["cid"], "key": k, "closure": c["closure"], "format": c["format"], "own_verified": ok,
                                 "max_mu": mx, "R-CF_M4": cf_m4, "R-CF_W4": cf_w4, "R-MN_M4": mn_m4, "R-MN_W4": mn_w4,
                                 "run_counts_for_M4": rv.get("counts_for_M4"), "run_counts_for_W4": rv.get("counts_for_W4"),
                                 "run_flags_equal_R-CF": (rv.get("counts_for_M4", False) == cf_m4 or c["format"] == "wdag-v1") and rv.get("counts_for_W4") == cf_w4})
            sysrec["cf_M4"] |= cf_m4
            sysrec["cf_W4"] |= cf_w4
            sysrec["mn_M4"] |= mn_m4
            sysrec["mn_W4"] |= mn_w4
        sysrec["M4_same_under_both_readings"] = sysrec["cf_M4"] == sysrec["mn_M4"]
        sysrec["W4_same_under_both_readings"] = sysrec["cf_W4"] == sysrec["mn_W4"]
        res["per_system"][k] = sysrec
    res["all_lines_own_verified"] = all(x["own_verified"] for x in res["lines"])
    res["run_flags_are_R-CF_eligibility_on_all_lines"] = all(x["run_flags_equal_R-CF"] for x in res["lines"])
    res["per_system_outcome_reading_invariant"] = all(v["M4_same_under_both_readings"] and v["W4_same_under_both_readings"] for v in res["per_system"].values())
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "lines"}, indent=1))


if __name__ == "__main__":
    main()
