#!/usr/bin/env python3
"""TASK-20260926-59169c CP-5 floor/ceiling statement.

For every compared item, the number of DISTINCT agreed values across the
compared systems, per (arm, role) group of the pool and for the N-CONV stream.
An item that takes one value on every system of a group (a floor, a ceiling,
or a structurally fixed value such as P = 1695 by L-TOP or final_dim = 4048 =
dim B_{<=4}) is weak evidence about the implementation in that group: a wrong
but saturating implementation would agree too. Values are read from the run's
records (they equal J7's on every compared system; comparison-core.json).
"""
import argparse, gzip, json, os
from collections import defaultdict

REV = "coordination/review/certbin-20260926-089841"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run = os.path.join(a.snap, "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e")
    km = json.load(open(os.path.join(a.snap, REV, "blind-inputs-key.json")))
    cl = defaultdict(dict)
    for l in gzip.open(os.path.join(run, "closures.jsonl.gz"), "rt"):
        r = json.loads(l)
        cl[r["key"]][r["closure"]] = r
    inst = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(os.path.join(run, "instances.jsonl.gz"), "rt")}
    draws = [json.loads(l) for l in gzip.open(os.path.join(run, "draws-N-CONV.jsonl.gz"), "rt")]

    def fields(k):
        R = cl[k]
        f = {
            "s": inst[k]["s"],
            "M_4.rank": R["M_4"]["rank"], "M_4.one": R["M_4"]["one"], "M_4.dims_by_deg[0:4]": tuple(R["M_4"]["dims_by_deg"][:4]), "M_4.P": R["M_4"]["P"],
            "W_4.dims": tuple(R["W_4"]["dims"]), "W_4.fixpoint": R["W_4"]["iterations_to_fixpoint"], "W_4.one_first_iteration": R["W_4"]["one_first_iteration"],
            "W_4.one": R["W_4"]["one"], "W_4.final_dim": R["W_4"]["final_dim"], "W_4.dims_by_deg": tuple(R["W_4"]["dims_by_deg"]),
            "rc_b.kernel_dim": R["rc_b"]["kernel_dim"], "rc_b.label": R["rc_b"]["label"],
        }
        if "M_3" in R:
            f["M_3.rank"] = R["M_3"]["rank"]
            f["M_3.one"] = R["M_3"]["one"]
        if R["rc_b"]["kernel_dim"] == 1:
            f["rc_b.c"] = R["rc_b"]["c"]
            f["rc_b.ell_support"] = tuple(R["rc_b"]["ell_linear_support"])
            f["rc_b.ell_const"] = R["rc_b"]["ell_const"]
            if R["rc_b"].get("substituted"):
                f["rc_b.j_star"] = R["rc_b"]["j_star"]
                f["R'_3.rank"] = R["R'_3"]["rank"]
                f["R'_4.rank"] = R["R'_4"]["rank"]
                f["R'_4.one"] = R["R'_4"]["one"]
                f["R'_4.dims_by_deg"] = tuple(R["R'_4"]["dims_by_deg"])
        return f

    groups = defaultdict(list)
    for lab, v in km.items():
        groups["%s:%s (%s)" % (v["arm"], v["role"], v["group"])].append(v["key"])
    out = {"pool_groups": {}, "nconv_stream": {}, "q1_nconv": {}}
    for g, keys in sorted(groups.items()):
        vals = defaultdict(set)
        for k in keys:
            for f, x in fields(k).items():
                vals[f].add(json.dumps(x))
        out["pool_groups"][g] = {"n": len(keys), "items": {f: ({"constant": json.loads(next(iter(v)))} if len(v) == 1 else {"distinct_values": len(v)})
                                                          for f, v in sorted(vals.items())}}
    for role in ("unsat", "sat"):
        keys = ["N-CONV:%d:%s" % (s, role) for s in range(144)]
        vals = defaultdict(set)
        for k in keys:
            f = fields(k)
            for n in ("s", "M_4.rank", "M_4.one", "M_4.dims_by_deg[0:4]", "M_4.P"):
                vals[n].add(json.dumps(f[n]))
        out["q1_nconv"][role] = {n: ({"constant": json.loads(next(iter(v)))} if len(v) == 1 else {"distinct_values": len(v)}) for n, v in vals.items()}
    ua = [inst["N-CONV:%d:unsat" % s]["attempt"] for s in range(144)]
    sa = [inst["N-CONV:%d:sat" % s]["attempt"] for s in range(144)]
    out["nconv_stream"] = {
        "attempts_total": len(draws),
        "unsat_attempt_index_distinct": len(set(ua)), "unsat_attempt_index_range": [min(ua), max(ua)],
        "sat_attempt_index_distinct": len(set(sa)), "sat_attempt_index_range": [min(sa), max(sa)],
        "s_values_over_attempts_distinct": len({d["s"] for d in draws}),
        "E_sha256_distinct_over_attempts": len({d["E_sha256"] for d in draws}),
        "reading": "stream items vary per attempt; agreement on 1181/1181 attempt hashes and s is strong evidence about the construction and stream (not a floor/ceiling item)",
    }
    json.dump(out, open(a.out, "w"), indent=1)
    for g, v in out["pool_groups"].items():
        const = [f for f, x in v["items"].items() if "constant" in x]
        var = [f for f, x in v["items"].items() if "distinct_values" in x]
        print(g, "n=%d" % v["n"], "CONSTANT:", const, "| VARYING:", var)
    print("Q1", json.dumps(out["q1_nconv"]))
    print("stream", json.dumps(out["nconv_stream"]))


if __name__ == "__main__":
    main()
