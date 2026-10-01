#!/usr/bin/env python3
"""TASK-20260926-59169c CP-3 (second half): per run key in the pool (55) and per
N-CONV unsatisfiable slot (144), is each RUN-COUNTED refutation witnessed by J7
(a J7 wdag-v1 that the own checker accepts -- checks/cp3_wdag_check.out.json),
by J1 (J1 verified the run's counted certificate), by both, or contradicted?

Run-counted (the run's own rule, analysis.py and MN1): M_4 = a verified flat-v1
labelled M_4 with max|mu| <= 2; W_4 = a verified wdag-v1 labelled W_4
(verification status taken from the run's certificate-verification.json).
A J7 certificate witnesses M_4 only if it is a single node with no prods (the
specification's form of an M_4 refutation); any valid J7 wdag-v1 witnesses W_4.
Contradicted = J7 computes s >= 1, or J7's own closure says 1 is NOT in the
closure, or J1 rejects the run's counted certificate.
Also recorded: systems the run does NOT count as refuted, and whether J7 agrees.
"""
import argparse, gzip, json, os
from collections import Counter, defaultdict

REV = "coordination/review/certbin-20260926-089841"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--cp3", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rev = os.path.join(a.snap, REV)
    run = os.path.join(a.snap, "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e")
    d7 = json.load(open(os.path.join(rev, "reviews/TASK-20260926-83cebf/rederivation.json")))
    v1 = json.load(open(os.path.join(rev, "reviews/TASK-20260926-f0e5a4/verification.json")))
    km = json.load(open(os.path.join(rev, "blind-inputs-key.json")))
    cp3 = json.load(open(a.cp3))["per_certificate"]
    certs = {json.loads(l)["label_or_replay_key"]: json.loads(l) for l in gzip.open(os.path.join(rev, "reviews/TASK-20260926-83cebf/wcerts.jsonl.gz"), "rt")}
    j7valid = {c["j7_label"]: (c["status"] == "valid") for c in cp3}
    j7onenode = {lab: (len(c["nodes"]) == 1 and not c["nodes"][0].get("prods")) for lab, c in certs.items()}
    cv = {c["cid"]: c for c in json.load(open(os.path.join(run, "certificate-verification.json")))["certificates"]}
    j1 = {p["cid"]: p for p in v1["certificates_VC3"]["per_line"]}
    lines = [json.loads(l) for l in gzip.open(os.path.join(run, "certificates.jsonl.gz"), "rt")]
    inst = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(os.path.join(run, "instances.jsonl.gz"), "rt")}
    cl = defaultdict(dict)
    for l in gzip.open(os.path.join(run, "closures.jsonl.gz"), "rt"):
        r = json.loads(l)
        cl[r["key"]][r["closure"]] = r
    counted = defaultdict(dict)  # key -> closure -> cid
    for c in lines:
        v = cv[c["cid"]]
        if not v["verified"]:
            continue
        if c["closure"] == "M_4" and c["format"] == "flat-v1" and v["max_mu"] <= 2:
            counted[c["key"]]["M_4"] = c["cid"]
        if c["closure"] == "W_4" and c["format"] == "wdag-v1":
            counted[c["key"]]["W_4"] = c["cid"]

    def status(rk, j7lab, j7_s, j7_one):
        out = {"run_key": rk, "j7_label": j7lab, "run_counted": sorted(counted.get(rk, {})),
               "engine_one": {X: cl[rk][X]["one"] for X in ("M_4", "W_4")}}
        per = {}
        for X in ("M_4", "W_4"):
            if X not in counted.get(rk, {}):
                # not a run-counted refutation: does J7 agree it is not refuted at X?
                jX = j7_one.get(X)
                per[X] = {"run_counted": False,
                          "j7_agrees_not_refuted": (jX is False) if jX is not None else None,
                          "note": None if jX is not None else "J7 did not compute %s on this system" % X}
                continue
            cid = counted[rk][X]
            by_j1 = bool(j1[cid]["verified"])
            has = j7lab in j7valid and j7valid[j7lab]
            by_j7 = has and (j7onenode[j7lab] if X == "M_4" else True)
            contra = []
            if j7_s is not None and j7_s != 0:
                contra.append("J7 s = %d" % j7_s)
            if j7_one.get(X) is False:
                contra.append("J7 closure: 1 not in %s" % X)
            if not by_j1:
                contra.append("J1 rejects run certificate cid %d" % cid)
            st = "contradicted" if contra else ("both" if by_j7 and by_j1 else "J7 only" if by_j7 else "J1 only" if by_j1 else "unwitnessed")
            per[X] = {"run_counted": True, "run_cid": cid, "witness": st, "by_J7": by_j7, "by_J1": by_j1, "contradictions": contra}
        out["per_closure"] = per
        return out

    pool = []
    for lab in sorted(km):
        rk = km[lab]["key"]
        j7_one = {"M_4": d7["Q2"][lab]["one_in_R_4"], "W_4": d7["Q3"][lab]["one"]}
        pool.append(dict(status(rk, lab, d7["Q2"][lab]["s"], j7_one), label=lab, arm=km[lab]["arm"], role=km[lab]["role"]))
    slots = []
    for s in range(144):
        rk = "N-CONV:%d:unsat" % s
        lab = "NCONV-REPLAY:%d:unsat" % s
        q1 = d7["Q1"]["unsat"][lab]
        # J7 computed only M_4 on replay systems (AMB-17); a valid one-node wdag certifies 1 in M_4 subset W_4,
        # so J7's statement about W_4 is implied when 1 in M_4, and absent otherwise.
        j7_one = {"M_4": q1["one_in_R_4"], "W_4": True if q1["one_in_R_4"] else None}
        slots.append(dict(status(rk, lab, q1["s"], j7_one), slot=s))

    def tally(recs):
        t = Counter()
        for r in recs:
            for X, p in r["per_closure"].items():
                if p["run_counted"]:
                    t["%s run-counted: %s" % (X, p["witness"])] += 1
                else:
                    t["%s not run-counted: J7 agrees not refuted=%s" % (X, p["j7_agrees_not_refuted"])] += 1
        return dict(sorted(t.items()))

    by_arm = defaultdict(list)
    for r in pool:
        by_arm["%s:%s" % (r["arm"], r["role"])].append(r)
    res = {
        "pool_tally": tally(pool),
        "pool_tally_by_arm_role": {k: tally(v) for k, v in sorted(by_arm.items())},
        "nconv_unsat_slots_tally": tally(slots),
        "any_contradicted": any(p.get("witness") == "contradicted" for r in pool + slots for p in r["per_closure"].values()),
        "any_unwitnessed": any(p.get("witness") == "unwitnessed" for r in pool + slots for p in r["per_closure"].values()),
        "pool": pool, "nconv_unsat_slots": slots,
    }
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("pool", "nconv_unsat_slots")}, indent=1))


if __name__ == "__main__":
    main()
