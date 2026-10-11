"""Build resolve/k-table.jsonl from the F1 job captures with the DISJOINT checker
(ec_check.py). Imports nothing from crypto_autoresearcher (AST scan in checks/).
Each capture is matched, in order, to the solver rows the same job wrote
(rho rows excluded) and identified by (panel, bits, curve, m, arm, mode).
The archived p, a, b, N come from the canonical row files (read as JSON).

usage: python3 build_ktable.py <out k-table.jsonl> <out summary.json>
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ec_check as C  # noqa: E402  (own module)

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
CANON = {("main", 3): RUNS + "/RUN-PFDR-1b78f7-census-m3/rows.jsonl.gz",
         ("main", 4): RUNS + "/RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz",
         ("main", 5): RUNS + "/RUN-PFDR-1b78f7-census-m5/rows.jsonl.gz",
         ("j0", 3): RUNS + "/RUN-PFDR-1b78f7-j0/rows.jsonl.gz"}


def load_canon():
    out = {}
    for (panel, m), p in CANON.items():
        for l in gzip.open(p, "rt"):
            r = json.loads(l)
            if not str(r.get("method", "")).startswith("ic_m"):
                continue
            out[(r["panel"], r["bits"], r["curve"], int(r["method"][4:]), r["arm"], r["mode"])] = r
    return out


def main():
    canon = load_canon()
    log = [json.loads(l) for l in open(os.path.join(HERE, "run-log.jsonl"))]
    latest = {}
    for r in log:
        latest.setdefault(r["label"], []).append(r)
    recs, problems = [], []
    bs_cache = {}
    for label, atts in sorted(latest.items()):
        a = atts[0]  # attempt 1 is the reference execution; attempt 2 (if any) only separates nondeterminism
        d = a["dir"]
        caps = [json.loads(l) for l in open(os.path.join(d, "captures.jsonl"))]
        rows = [json.loads(l) for l in open(os.path.join(d, "rows.jsonl"))]
        srows = [r for r in rows if str(r.get("method", "")).startswith("ic_m")]
        if len(caps) != len(srows):
            problems.append([label, f"captures {len(caps)} != solver rows {len(srows)}"])
        for cap, row in zip(caps, srows):
            key = (row["panel"], row["bits"], row["curve"], int(row["method"][4:]), row["arm"], row["mode"])
            if cap.get("capture_error"):
                problems.append([label, list(key), cap["capture_error"]])
                continue
            if cap["fb_kind"] != row["fb"] or cap["harvest"] != row["mode"] or cap["m"] != key[3]:
                problems.append([label, list(key), "capture/row mismatch", cap["fb_kind"], row["fb"], cap["harvest"]])
            arch = canon.get(key)
            capd = dict(cap, bits=key[1], curve=key[2])
            res = C.check(capd, {"p": arch["p"], "a": arch["a"], "b": arch["b"], "N": arch["N"]} if arch else None)
            ck = (cap["p"], cap["a"], cap["b"], tuple(cap["P"]), tuple(cap["Q"]), cap["N"])
            if ck not in bs_cache:
                bs_cache[ck] = C.bsgs(C.Curve(cap["p"], cap["a"], cap["b"]), tuple(cap["P"]), tuple(cap["Q"]), cap["N"])
            k_bsgs = bs_cache[ck]
            rec = {"job": label, "attempt": a["attempt"], "panel": key[0], "bits": key[1], "curve": key[2], "m": key[3],
                   "arm": key[4], "mode": key[5], "p": cap["p"], "a": cap["a"], "b": cap["b"], "N": cap["N"],
                   "P": cap["P"], "Q": cap["Q"], "terminated_by": cap["terminated_by"],
                   "solver_verified_flag": cap["verified_flag"], "k_solver": res.pop("k_solver"),
                   "k_rule": res.pop("k_rule"), "k_bsgs": k_bsgs, "checks": res}
            rec["checks"]["k_bsgs_eq_k_rule"] = k_bsgs == rec["k_rule"]
            rec["checks"]["archived_row_present"] = arch is not None
            if arch is not None:
                rec["checks"]["archived_k_found_eq_reexecution"] = arch["k_found"] == (cap["k_solver"] is not None)
                rec["checks"]["archived_terminated_by_eq_reexecution"] = arch["harvest"]["terminated_by"] == cap["terminated_by"]
            recs.append(rec)
    with open(sys.argv[1], "w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    # summary
    summ = {"instances": len(recs), "problems": problems, "solved": sum(1 for r in recs if r["k_solver"] is not None),
            "capped": sum(1 for r in recs if r["terminated_by"] == "attempt_cap"), "check_failures": {}}
    for r in recs:
        for c, v in r["checks"].items():
            if v is False:
                summ["check_failures"].setdefault(c, []).append([r["panel"], r["bits"], r["curve"], r["m"], r["arm"], r["mode"]])
    summ["all_checks_pass"] = not summ["check_failures"] and not problems
    json.dump(summ, open(sys.argv[2], "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items()}, indent=1)[:3000])


if __name__ == "__main__":
    main()
