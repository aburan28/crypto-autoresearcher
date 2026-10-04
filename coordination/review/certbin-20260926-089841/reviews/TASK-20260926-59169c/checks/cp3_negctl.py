#!/usr/bin/env python3
"""TASK-20260926-59169c CP-3 negative controls ON THE OWN CHECKER.

From real J7 certificates (5 one-node replay certificates and every
multi-node pool certificate, capped at 5 per kind) build corrupted versions and
require checks/wdag_check.py to reject each with the expected rule:
  R  one row removed                           -> (e)
  K  one k changed (k -> (k+1) mod 17)         -> (e)
  T  transplant onto another system of the same kind (other slot) -> rejected ((c) or (e))
  B  a pair of identical rows with |mu| = 3 added (sum unchanged)  -> (b)
  C  a new child of degree 4 used twice with the same j (sum unchanged) -> (c)
  A  (multi-node only) a prod pointing to a later id -> (a)
Rule (d) is implied by (b) and (c) at D = 4 (a row has degree <= 4 and a
product v_j * poly(c) has degree <= 1 + 3), so it is not separately
constructible without first violating (b) or (c); declared vacuous here.
"""
import argparse, copy, gzip, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wdag_check as W  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rev = os.path.join(a.snap, "coordination/review/certbin-20260926-089841")
    j7 = os.path.join(rev, "reviews/TASK-20260926-83cebf")
    blind = json.load(open(os.path.join(rev, "blind/blind-inputs.json")))
    pool = {s["label"]: W.system_from_monomial_lists(s["equations"]) for s in blind["systems"]}
    rows = {}
    for line in gzip.open(os.path.join(j7, "stream-replay.jsonl.gz"), "rt"):
        r = json.loads(line)
        if r["arm"] == "N-CONV" and r["outcome"] == "kept_unsat":
            rows[r["slot"]] = W.system_from_hex(r["row_hex"])
    certs = [json.loads(l) for l in gzip.open(os.path.join(j7, "wcerts.jsonl.gz"), "rt")]
    one = [c for c in certs if c["label_or_replay_key"].startswith("NCONV")][:5]
    multi = [c for c in certs if len(c["nodes"]) > 1][:5]

    def sysof(c):
        lab = c["label_or_replay_key"]
        if lab.startswith("NCONV"):
            return rows[int(lab.split(":")[1])]
        return pool[lab]

    def other(c):
        lab = c["label_or_replay_key"]
        if lab.startswith("NCONV"):
            s = int(lab.split(":")[1])
            return rows[(s + 1) % 144]
        labs = sorted(pool)
        return pool[labs[(labs.index(lab) + 1) % len(labs)]]

    res = []
    for kind, lst in (("one-node", one), ("multi-node", multi)):
        for c in lst:
            F = sysof(c)
            base = W.check_wdag(c, F)[0]
            assert base == "valid"
            out = c["output"]
            # R
            c1 = copy.deepcopy(c)
            nd = next(n for n in c1["nodes"] if n["id"] == out)
            nd["rows"] = nd["rows"][1:]
            res.append((kind, c["label_or_replay_key"], "R", W.check_wdag(c1, F), "(e)"))
            # K
            c2 = copy.deepcopy(c)
            nd = next(n for n in c2["nodes"] if n["id"] == out)
            mu, k = nd["rows"][0]
            nd["rows"][0] = [mu, (k + 1) % 17]
            res.append((kind, c["label_or_replay_key"], "K", W.check_wdag(c2, F), "(e)"))
            # T
            res.append((kind, c["label_or_replay_key"], "T", W.check_wdag(c, other(c)), "(e)"))
            # B
            c3 = copy.deepcopy(c)
            nd = next(n for n in c3["nodes"] if n["id"] == out)
            nd["rows"] = nd["rows"] + [[[1, 2, 3], 0], [[1, 2, 3], 0]]
            res.append((kind, c["label_or_replay_key"], "B", W.check_wdag(c3, F), "(b)"))
            # C: new child id = max+1 would break (a) for the output; renumber: put child first.
            c4 = copy.deepcopy(c)
            for n in c4["nodes"]:
                n["id"] += 1
                n["prods"] = [[j, cc + 1] for j, cc in n["prods"]]
            c4["output"] = out + 1
            k4 = next(k for k in range(17) if W.deg(F[k]) == 2)
            c4["nodes"].insert(0, {"id": 0, "rows": [[[16, 17], k4]], "prods": []})
            nd = next(n for n in c4["nodes"] if n["id"] == out + 1)
            nd["prods"] = nd["prods"] + [[5, 0], [5, 0]]
            r4 = W.check_wdag(c4, F)
            # child degree must really be 4 for this to be a (c) test
            childdeg = W.deg({m | 0 for m in set().union(*[{x | (1 << 16) | (1 << 17)} for x in F[k4]])})
            res.append((kind, c["label_or_replay_key"], "C(child_deg=%d)" % childdeg, r4, "(c)" if childdeg == 4 else "valid"))
            # A
            if len(c["nodes"]) > 1:
                c5 = copy.deepcopy(c)
                n0 = next(n for n in c5["nodes"] if n["id"] == 0)
                n0["prods"] = [[3, out]]
                res.append((kind, c["label_or_replay_key"], "A", W.check_wdag(c5, F), "(a)"))
    rows_out = []
    ok = True
    for kind, lab, typ, (st, det), want in res:
        got = det.get("rule") if st == "invalid" else "valid"
        good = (st == "invalid") if (typ == "T") else (got == want)  # a transplant must be rejected; the first rule hit may be (c) or (e)
        ok &= good
        rows_out.append({"kind": kind, "label": lab, "corruption": typ, "status": st, "rule": got, "expected": want, "as_expected": good})
    json.dump({"all_as_expected": ok, "n": len(rows_out), "rule_d_note": "(d) implied by (b)+(c) at D = 4; not separately constructible", "controls": rows_out}, open(a.out, "w"), indent=1)
    print("negative controls:", len(rows_out), "all as expected:", ok)


if __name__ == "__main__":
    main()
