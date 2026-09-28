#!/usr/bin/env python3
"""CP-3 of TASK-20260926-f50294: check EVERY blind certificate
(wdag.jsonl.gz and ann.jsonl.gz of TASK-20260926-f0736e) with the
comparator's own minimal checkers (mini.py), written before the re-deriver's
code was read.

f_k: explicit kind from blind-inputs.json; curve kind by the comparator's own
S_3 descent from x_R. Both are ALSO compared with the run's E_hex (decoded by
the comparator's own E_layout codec) through blind-inputs-key.json, which
cross-checks the 5d1557 extraction.

Negative controls (must all reject): per wdag-v1 certificate kind, 5 mutations
(row removed, k changed, mu changed to another monomial of the same degree,
degree-discipline violation, transplant to another system of the same arm);
per ann-v1 kind, (A1) a functional made nonzero on an M_4 row, (A3) every
constant coordinate cleared, (A2) L = annihilator of rowspace(M_4) on a system
whose M_4 is not W_4-closed, and a transplant.

Usage: python3 check_blind_certs.py <worktree_root> <out_json>
"""
import gzip
import json
import os
import resource
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mini  # noqa: E402

ROUND = "coordination/review/certbin-20260926-d7249d"
F0 = f"{ROUND}/reviews/TASK-20260926-f0736e"
RUN = "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60"


def load_jsonl(p):
    with gzip.open(p, "rt") as fh:
        return [json.loads(x) for x in fh]


def main():
    root, outp = sys.argv[1], sys.argv[2]
    os.chdir(root)
    t0 = time.time()
    bi = json.load(open(f"{ROUND}/blind/blind-inputs.json"))
    key = json.load(open(f"{ROUND}/blind-inputs-key.json"))
    B = bi["curve"]["B"]
    inst = {r["key"]: r for r in load_jsonl(f"{RUN}/instances.jsonl.gz")}
    systems = {}
    cross = {}
    for x in bi["instances"]:
        lab = x["label"]
        if x["kind"] == "curve":
            fs = mini.descend_s3(x["x_R"], B)
        else:
            fs = mini.explicit_to_polys(x["equations"])
        systems[lab] = fs
        rk = key[lab]["key"]
        dec = mini.decode_ehex(inst[rk]["E_hex"])
        cross[lab] = {"key": rk, "kind": x["kind"], "equal_to_run_E_hex": dec == fs,
                      "x_R_equal": (x.get("x_R") == inst[rk].get("x_R")) if x["kind"] == "curve" else None}
    wd = {r["label"]: r for r in load_jsonl(f"{F0}/wdag.jsonl.gz")}
    an = {r["label"]: r for r in load_jsonl(f"{F0}/ann.jsonl.gz")}
    res = {}
    for lab in sorted(systems):
        fs = systems[lab]
        ent = {"key": key[lab]["key"], "arm": key[lab]["arm"], "role": key[lab]["role"]}
        if lab in wd:
            ok, why, st = mini.check_wdag(wd[lab], fs)
            ent["wdag"] = {"status": "valid" if ok else "invalid", "first_violation": why,
                           "stats": {k: v for k, v in st.items() if k != "deg_by_node"},
                           "deg_by_node": st.get("deg_by_node")}
        else:
            ent["wdag"] = {"status": "absent"}
        if lab in an:
            ts = time.time()
            ok, why, st = mini.check_ann(an[lab], fs)
            ent["ann"] = {"status": "valid" if ok else "invalid", "first_violation": why,
                          "stats": st, "seconds": round(time.time() - ts, 1)}
        else:
            ent["ann"] = {"status": "absent"}
        res[lab] = ent
        print(lab, ent["key"], "wdag", ent["wdag"]["status"], ent["wdag"].get("first_violation"),
              "ann", ent["ann"]["status"], ent["ann"].get("first_violation"), flush=True)

    # ---------------------------------------------------------- negative controls
    neg = []
    rng = np.random.default_rng(20260926)  # comparator's own negative-control stream

    def rec(kind, lab, desc, cert, fs, checker):
        ok, why, _ = checker(cert, fs)
        neg.append({"kind": kind, "label": lab, "mutation": desc, "rejected": not ok, "reason": why})

    by_arm = {}
    for lab in sorted(wd):
        by_arm.setdefault(key[lab]["arm"], []).append(lab)
    for arm, labs in sorted(by_arm.items()):
        for lab in labs[:5]:
            fs = systems[lab]
            c0 = wd[lab]
            # 1. one row removed (from the output node)
            c = json.loads(json.dumps(c0))
            onode = [n for n in c["nodes"] if n["id"] == c["output"]][0]
            onode["rows"].pop(int(rng.integers(0, len(onode["rows"]))))
            rec("wdag-v1/" + arm, lab, "row removed from output node", c, fs, mini.check_wdag)
            # 2. one k changed
            c = json.loads(json.dumps(c0))
            onode = [n for n in c["nodes"] if n["id"] == c["output"]][0]
            i = int(rng.integers(0, len(onode["rows"])))
            onode["rows"][i][1] = (onode["rows"][i][1] + 1 + int(rng.integers(0, 18))) % 19
            rec("wdag-v1/" + arm, lab, "k changed in output node", c, fs, mini.check_wdag)
            # 3. mu changed to another monomial of the same degree
            c = json.loads(json.dumps(c0))
            onode = [n for n in c["nodes"] if n["id"] == c["output"]][0]
            cand = [t for t, (mu, k) in enumerate(onode["rows"]) if len(mu) >= 1]
            t = cand[int(rng.integers(0, len(cand)))]
            mu = onode["rows"][t][0]
            new = sorted(set(mu[:-1]) | {next(v for v in range(20) if v not in mu)})
            onode["rows"][t][0] = new
            rec("wdag-v1/" + arm, lab, "mu %r -> %r (same degree)" % (mu, new), c, fs, mini.check_wdag)
            # 4. degree-discipline violation: a one-node wdag with a |mu| = 3 row
            c = {"D": 4, "nv": 20, "neq": 19, "nodes": [{"id": 0, "rows": [[[0, 1, 2], 0]], "prods": []}], "output": 0}
            rec("wdag-v1/" + arm, lab, "one-node wdag with |mu| = 3", c, fs, mini.check_wdag)
            # 4b. a prods child of degree 4: node 0 = a degree-4 M_4 row, node 1 = v_19 * node 0
            c = json.loads(json.dumps(c0))
            nid = max(n["id"] for n in c["nodes"]) + 1
            c["nodes"].append({"id": nid, "rows": [[[0, 1], 0]], "prods": []})
            c["nodes"].append({"id": nid + 1, "rows": [], "prods": [[19, nid]]})
            onode = [n for n in c["nodes"] if n["id"] == c["output"]][0]
            # attach: output node unchanged, but add a node using a degree-4 child and make it the output
            c["output"] = nid + 1
            rec("wdag-v1/" + arm, lab, "prods child of degree 4 (and output moved)", c, fs, mini.check_wdag)
            # 5. transplant to another system of the same arm
            other = [x for x in labs if x != lab][0]
            rec("wdag-v1/" + arm, lab, "transplanted to " + other, c0, systems[other], mini.check_wdag)
    by_arm_a = {}
    for lab in sorted(an):
        by_arm_a.setdefault(key[lab]["arm"], []).append(lab)
    for arm, labs in sorted(by_arm_a.items()):
        lab = labs[0]
        fs = systems[lab]
        c0 = an[lab]
        M4 = mini.m4_rows(fs)
        # (A1): lambda 0 xor a functional that is 1 exactly on one M_4 row's leading coordinate
        L = [mini.hex_to_bits(h) for h in c0["L_hex"]]
        row = M4[int(rng.integers(0, M4.shape[0]))]
        nzs = np.flatnonzero(row)
        if nzs.size:
            L2 = [x.copy() for x in L]
            L2[0][nzs[0]] ^= 1
            c = dict(c0, L_hex=[format(int(np.packbits(x, bitorder="little")[::-1].tobytes().hex(), 16), "x") for x in L2])
            ok, why, _ = mini.check_ann(c, fs, M4=M4)
            neg.append({"kind": "ann-v1/" + arm, "label": lab, "mutation": "lambda 0 flipped on a coordinate of an M_4 row",
                        "rejected": not ok, "reason": why})
        # (A3): every constant coordinate cleared
        L2 = [x.copy() for x in L]
        for x in L2:
            x[6195] = 0
        c = dict(c0, L_hex=[format(int(np.packbits(x, bitorder="little")[::-1].tobytes().hex(), 16), "x") for x in L2])
        ok, why, _ = mini.check_ann(c, fs, M4=M4)
        neg.append({"kind": "ann-v1/" + arm, "label": lab, "mutation": "every constant coordinate cleared",
                    "rejected": not ok, "reason": why})
        # transplant
        other = [x for x in labs if x != lab]
        if other:
            ok, why, _ = mini.check_ann(c0, systems[other[0]])
            neg.append({"kind": "ann-v1/" + arm, "label": lab, "mutation": "transplanted to " + other[0],
                        "rejected": not ok, "reason": why})
    # (A2) control: L = basis of the annihilator of rowspace(M_4), on the first
    # blind S3-SAT100 system (W_4 != M_4 there if the closure grows)
    sat = sorted(l for l in systems if key[l]["arm"] == "S3-SAT100")[0]
    fs = systems[sat]
    M4 = mini.m4_rows(fs)
    rk, Kann = mini.gf2_rref_nullspace(M4)   # nullspace of M4 = functionals vanishing on every row
    Lh = [format(int(np.packbits(x, bitorder="little")[::-1].tobytes().hex(), 16), "x") for x in Kann]
    c = {"D": 4, "nv": 20, "neq": 19, "L_hex": Lh}
    ok, why, st = mini.check_ann(c, fs, M4=M4)
    neg.append({"kind": "ann-v1/(A2)", "label": sat, "mutation": "L = annihilator of rowspace(M_4) only (rank M_4 = %d, |L| = %d)" % (rk, len(Lh)),
                "rejected": not ok, "reason": why, "stats": st})
    out = {
        "task": "TASK-20260926-f50294", "cp": "CP-3",
        "checker": "checks/mini.py (own; stdlib + numpy; no crypto_autoresearcher import)",
        "f_k_sources": {"curve": "own S_3 descent from blind-inputs.json x_R", "explicit": "blind-inputs.json equations"},
        "cross_check_vs_run_E_hex": cross,
        "cross_check_all_equal": all(v["equal_to_run_E_hex"] for v in cross.values()),
        "per_label": res,
        "counts": {
            "wdag": {s: sum(1 for v in res.values() if v["wdag"]["status"] == s) for s in ("valid", "invalid", "absent")},
            "ann": {s: sum(1 for v in res.values() if v["ann"]["status"] == s) for s in ("valid", "invalid", "absent")},
        },
        "negative_controls": neg,
        "negative_controls_all_rejected": all(x["rejected"] for x in neg),
        "seconds": round(time.time() - t0, 1),
        "max_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }
    json.dump(out, open(outp, "w"), indent=1)
    print("DONE", out["counts"], "negctl all rejected:", out["negative_controls_all_rejected"],
          "cross:", out["cross_check_all_equal"], out["seconds"], "s", out["max_rss_mb"], "MB")


if __name__ == "__main__":
    main()
