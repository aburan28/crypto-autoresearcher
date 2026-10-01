#!/usr/bin/env python3
"""J9 O2 -- run the ARCHIVED closure engine, unchanged, on the 20 N-ELL
instances (after o2-predictions.json was declared and hashed), then my own
literal W_4 (rtlib.literal_W) on every instance as a cross-check, and compare
both with the declaration. Engine: experiments/EXP-CERTBIN-e94b27/impl/
closure.py (Closure(18, 4, 17).w_closure, want_cert=True), instance decoding
by the engine's own instances.E_from_hex / eqs_of. Nothing is modified."""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/impl"
sys.path.insert(0, ENGINE)
from closure import Closure, eval_cert  # noqa: E402
from instances import E_from_hex, eqs_of  # noqa: E402

sys.path.insert(1, os.path.join(HERE, "..", "j7-mechanism"))
import rtlib as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    inst = json.load(open(os.path.join(HERE, "n-ell-instances.json")))["instances"]
    pred = {p["label"]: p for p in json.load(open(os.path.join(HERE, "o2-predictions.json")))["instances"]}
    cl = Closure(18, 4, 17)
    sp = R.Space(range(18), 4)
    rows = []
    for it in inst:
        E = E_from_hex(it["E_hex"])
        eqs = eqs_of(E)
        t = time.time()
        rec, cert = cl.w_closure(eqs, want_cert=True)
        te = time.time() - t
        eng = {k: rec[k] for k in ("iterations_to_fixpoint", "dims", "final_dim", "one", "one_first_iteration",
                                   "dims_by_deg", "new_fallen_per_iteration")}
        eng["certificate_emitted"] = cert is not None
        if cert is not None:
            eng["engine_self_check_sum_is_1"] = eval_cert(cert, eqs) == [0]
        t = time.time()
        fs = [set(f) for f in eqs]
        own, _ = R.literal_W(sp, fs, 4)
        to = time.time() - t
        d = pred[it["label"]]["DECLARED"]
        cmp = {"engine_matches_declared": (isinstance(d, dict) and eng["one"] == d["one"] and eng["final_dim"] == d["final_dim"]
                                           and eng["dims_by_deg"] == d["dims_by_deg"] and eng["dims"] == d["dims"]
                                           and eng["iterations_to_fixpoint"] == d["iterations_to_fixpoint"]),
               "own_matches_engine": (own["one"] == eng["one"] and own["final_dim"] == eng["final_dim"]
                                      and own["dims"] == eng["dims"] and own["dims_by_deg"] == eng["dims_by_deg"]
                                      and own["iterations_to_fixpoint"] == eng["iterations_to_fixpoint"])}
        row = {"label": it["label"], "draw": it["draw"], "engine": eng, "own_literal_W4": own,
               "declared": d, "compare": cmp, "engine_seconds": round(te, 2), "own_seconds": round(to, 2)}
        rows.append(row)
        print(json.dumps({"label": it["label"], "engine": {k: eng[k] for k in ("one", "final_dim", "dims", "dims_by_deg")},
                          **cmp}), flush=True)
    summ = {"n": len(rows),
            "engine_refutations": sum(1 for r in rows if r["engine"]["one"]),
            "own_refutations": sum(1 for r in rows if r["own_literal_W4"]["one"]),
            "engine_matches_declared": sum(r["compare"]["engine_matches_declared"] for r in rows),
            "own_matches_engine": sum(r["compare"]["own_matches_engine"] for r in rows),
            "signature_PASS": all(not r["engine"]["one"] and r["compare"]["engine_matches_declared"] for r in rows)}
    out = {"task": "TASK-20260924-d95e70", "object": "O2 engine run + own W_4",
           "engine_closure_py_sha256": sha(os.path.join(ENGINE, "closure.py")),
           "engine_instances_py_sha256": sha(os.path.join(ENGINE, "instances.py")),
           "engine_macaulay_py_sha256": sha(os.path.join(ENGINE, "macaulay.py")),
           "summary": summ, "rows": rows}
    json.dump(out, open(os.path.join(HERE, "o2-engine-and-own.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
