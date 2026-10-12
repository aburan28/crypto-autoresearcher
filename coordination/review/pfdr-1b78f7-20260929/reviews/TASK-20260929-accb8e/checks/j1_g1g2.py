"""J1(e): G1 and G2 with my own comparator (not compare_regression.py).
Key (bits, curve, method, fb, engine or 'enumerate'); every key present in the committed
row except `seconds` equal after JSON parse; equal row counts; no duplicate key; la_pivot
precedence of run_procedures (a committed row lacking la_pivot has min_index)."""
import gzip, json, os, sys, collections
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
RUNS = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")
RES = os.path.join(WT, "src/crypto_autoresearcher/index_calculus/results")
PAIRS = [("G1", "R02", "RUN-PFDR-1b78f7-reg-off-sweep-20260924", "sweep-20260924.jsonl.gz"),
         ("G1", "R03", "RUN-PFDR-1b78f7-reg-off-sweep-mitm-20260926", "sweep-mitm-20260926.jsonl.gz"),
         ("G1", "R04", "RUN-PFDR-1b78f7-reg-off-sweep-arity-20260926", "sweep-arity-20260926.jsonl.gz"),
         ("G1", "R05", "RUN-PFDR-1b78f7-reg-off-sweep-minfill-20260926", "sweep-minfill-20260926.jsonl.gz"),
         ("G1", "R06", "RUN-PFDR-1b78f7-reg-off-sweep-arity-minfill-20260926", "sweep-arity-minfill-20260926.jsonl.gz"),
         ("G1", "R07", "RUN-PFDR-1b78f7-reg-off-sweep-arity67-20260928", "sweep-arity67-20260928.jsonl.gz"),
         ("G2", "R08", "RUN-PFDR-1b78f7-reg-census-sweep-minfill-20260926", "sweep-minfill-20260926.jsonl.gz"),
         ("G2", "R09", "RUN-PFDR-1b78f7-reg-census-sweep-arity-minfill-20260926", "sweep-arity-minfill-20260926.jsonl.gz")]


def key(r):
    return (r.get("bits"), r.get("curve"), r.get("method"), r.get("fb"), r.get("engine") or "enumerate")


def load(p, note):
    rl.opened(p, note)
    return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]


def main():
    out = {}
    for gate, rid, run, cf in PAIRS:
        com = load(os.path.join(RES, cf), f"J1(e) {gate}: committed {cf}")
        new = load(os.path.join(RUNS, run, "rows.jsonl.gz"), f"J1(e) {gate}: {rid} rows")
        kc = collections.Counter(key(r) for r in com)
        kn = collections.Counter(key(r) for r in new)
        res = {"committed_rows": len(com), "new_rows": len(new),
               "dup_committed": [list(k) for k, n in kc.items() if n > 1],
               "dup_new": [list(k) for k, n in kn.items() if n > 1],
               "missing_in_new": [list(k) for k in kc if k not in kn],
               "extra_in_new": [list(k) for k in kn if k not in kc]}
        nm = {key(r): r for r in new}
        mism, fields = [], collections.Counter()
        pivot_implied = 0
        extra_keys = collections.Counter()
        for r in com:
            n = nm.get(key(r))
            if n is None:
                continue
            for f, v in r.items():
                if f == "seconds":
                    continue
                if n.get(f, "<absent>") != v:
                    fields[f] += 1
                    if len(mism) < 10:
                        mism.append({"key": list(key(r)), "field": f, "committed": v, "new": n.get(f, "<absent>")})
            if "la_pivot" not in r and n.get("method") != "rho":
                pivot_implied += 1
                if n.get("la_pivot") != "min_index":
                    fields["la_pivot(implied min_index)"] += 1
            for f in n:
                if f not in r:
                    extra_keys[f] += 1
        res["field_mismatches"] = dict(fields)
        res["examples"] = mism
        res["committed_rows_lacking_la_pivot"] = pivot_implied
        res["new_only_keys"] = dict(extra_keys)
        res["pass"] = (len(com) == len(new) and not res["dup_new"] and not res["missing_in_new"]
                       and not res["extra_in_new"] and not fields)
        out[rid] = res
    with open(os.path.join(W, "checks", "out", "j1e-g1g2.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for rid, r in out.items():
        print(rid, {k: (v if not isinstance(v, list) else len(v)) for k, v in r.items() if k != "examples"})


if __name__ == "__main__":
    main()
