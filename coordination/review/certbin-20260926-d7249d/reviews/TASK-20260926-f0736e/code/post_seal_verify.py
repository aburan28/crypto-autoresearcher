"""Post-seal verification (TASK-20260926-f0736e).  ADDED AFTER seal.txt was
written; reads the sealed files and never writes them.

  python3 code/post_seal_verify.py --dir <task dir> --inputs <blind-inputs.json> --json-out <path>

1. seal.txt hashes == current sha256 of rederivation.json, wdag.jsonl.gz,
   ann.jsonl.gz.
2. Every wdag.jsonl.gz / ann.jsonl.gz line re-checked in THIS process by
   checkers.py against a system rebuilt by checkers.py from the blind inputs
   alone (curve kind: its own closed-form descent; explicit: the monomial
   lists); line sha256 equals rederivation.json's certificate_line_sha256.
3. Labels: wdag labels == {systems with 1 in W_4}; ann labels == {systems with
   1 not in W_4}; each label at most once.
4. Required-field scan (Q1..Q6 per system; Q1 both routes on curve kind).
5. Consistency scan (reported, never repaired): c_k = Tr(t^k/x_R^2) on curve
   kind; Q7 relations; ann functional count == 6196 - final_dim.
"""
import argparse
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import checkers as K  # noqa: E402


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--json-out", required=True)
    a = ap.parse_args()
    out = {}
    seal = {}
    for line in open(os.path.join(a.dir, "seal.txt")):
        parts = line.split()
        if len(parts) == 2 and len(parts[0]) == 64:
            seal[parts[1]] = parts[0]
    out["seal_matches"] = {f: seal.get(f) == sha(os.path.join(a.dir, f))
                           for f in ("rederivation.json", "wdag.jsonl.gz", "ann.jsonl.gz")}
    red = json.load(open(os.path.join(a.dir, "rederivation.json")))
    data = json.load(open(a.inputs))
    B = int(data["curve"]["B"])
    insts = {i["label"]: i for i in data["instances"]}
    systems = red["systems"]

    def eqs_for(label):
        i = insts[label]
        return K.curve_system(int(i["x_R"]), B) if i["kind"] == "curve" else K.explicit_system(i["equations"])

    checks = {"wdag": {}, "ann": {}}
    seen = {"wdag": [], "ann": []}
    for kind, fn in (("wdag", "wdag.jsonl.gz"), ("ann", "ann.jsonl.gz")):
        with gzip.open(os.path.join(a.dir, fn), "rb") as g:
            for raw in g:
                raw = raw.rstrip(b"\n")
                cert = json.loads(raw)
                label = cert["label"]
                seen[kind].append(label)
                eqs = eqs_for(label)
                if kind == "wdag":
                    ok, why = K.check_wdag(cert, eqs, label)
                    extra = {}
                else:
                    ok, why, det = K.check_ann(cert, eqs, label)
                    fd = systems[label]["Q3"]["final_dim"]
                    extra = {"functionals": len(cert["L_hex"]), "equals_codim": len(cert["L_hex"]) == 6196 - fd}
                checks[kind][label] = {"valid": ok, "reason": why,
                                       "line_sha256_matches": hashlib.sha256(raw).hexdigest() == systems[label].get("certificate_line_sha256"),
                                       **extra}
    refuted = sorted(l for l, r in systems.items() if r["Q3"]["one_in_W4"])
    notref = sorted(l for l, r in systems.items() if not r["Q3"]["one_in_W4"])
    out["labels"] = {
        "wdag_labels_equal_refuted_set": sorted(seen["wdag"]) == refuted,
        "ann_labels_equal_not_refuted_set": sorted(seen["ann"]) == notref,
        "no_duplicate_labels": len(seen["wdag"]) == len(set(seen["wdag"])) and len(seen["ann"]) == len(set(seen["ann"])),
        "n_wdag": len(seen["wdag"]), "n_ann": len(seen["ann"]),
    }
    out["certificate_rechecks"] = {
        "wdag_all_valid": all(v["valid"] and v["line_sha256_matches"] for v in checks["wdag"].values()),
        "ann_all_valid": all(v["valid"] and v["line_sha256_matches"] and v["equals_codim"] for v in checks["ann"].values()),
        "per_certificate": checks,
    }
    # required fields
    missing = {}
    req = {"Q1": ["s_exhaustive_2^20"], "Q2": ["rank_3", "rank_4", "one_in_R3", "one_in_R4", "dims_by_deg_M4"],
           "Q3": ["dims_W_i", "fixpoint_index", "one_first_iteration", "final_dim", "dims_by_deg_W4"],
           "Q4": ["kernel_dim", "status", "ell_route"]}
    for label in insts:
        r = systems.get(label)
        if r is None:
            missing[label] = ["whole system"]
            continue
        miss = [q + "." + f for q, fs in req.items() for f in fs if f not in (r.get(q) or {})]
        if insts[label]["kind"] == "curve":
            for f in ("s_quadratic_route", "degenerate", "routes_agree"):
                if f not in r["Q1"]:
                    miss.append("Q1." + f)
        if r["Q3"]["one_in_W4"] and not r.get("Q5"):
            miss.append("Q5")
        if (not r["Q3"]["one_in_W4"]) and not r.get("Q6"):
            miss.append("Q6")
        if r["Q4"].get("applicable"):
            for f in ("jstar", "rank_R3", "rank_R4", "one_R4", "dims_by_deg_R4", "sigma", "T5_applicable"):
                if f not in r["Q4"]:
                    miss.append("Q4." + f)
        if miss:
            missing[label] = miss
    out["required_field_gaps"] = missing
    # consistency scan
    scan = {"curve_c_k_trace_formula_false": [], "curve_rcb_not_applicable": [],
            "Q7_relation_false": [], "Q7_one_disagree": [], "kernel_dims": {}}
    for label, r in systems.items():
        q4 = r["Q4"]
        scan["kernel_dims"][str(q4["kernel_dim"])] = scan["kernel_dims"].get(str(q4["kernel_dim"]), 0) + 1
        if r["kind"] == "curve":
            if q4.get("c_equals_Tr(t^k/x_R^2)") is False:
                scan["curve_c_k_trace_formula_false"].append(label)
            if not q4.get("applicable"):
                scan["curve_rcb_not_applicable"].append(label)
        if r.get("Q7"):
            if not r["Q7"]["final_dim_W4_eq_final_dim_W'4_plus_1160"]:
                scan["Q7_relation_false"].append(label)
            if not r["Q7"]["one_agrees"]:
                scan["Q7_one_disagree"].append(label)
    out["consistency_scan"] = scan
    with open(a.json_out, "w") as f:
        json.dump(out, f, indent=1)
    summary = {k: v for k, v in out.items() if k not in ("certificate_rechecks",)}
    summary["certificate_rechecks"] = {k: v for k, v in out["certificate_rechecks"].items() if k != "per_certificate"}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
