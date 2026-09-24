#!/usr/bin/env python3
"""J9 O1 -- TASK-20260924-d95e70. FROM ARCHIVED RECORDS ONLY (RT-4): for every
S62 instance, archived s (instance-sets.json archived.s) against
  codim(W_4 in B_{<=4})            = 4048 - final_dim(W_4)
  codim(M_5 cap B_{<=4} in B_{<=4}) = 4048 - dims_by_deg(M_5)[4]
  codim(M_5 in B_{<=5})             = 12616 - rank(M_5)
  and, for the 10 W_5 instances, codim(W_5 in B_{<=5}) and of W_5 cap B_{<=4}.
Signature: every codim >= s; equality reported instance by instance.

Plus a machine check of the Reed-Muller surjectivity lemma the signature uses
(proof in the report): for m in {5, 6, 7} and d in {0, 1, 2, 3}, every set S of
2^{d+1} - 1 points drawn at random (200 draws per (m, d)) has
rank(ev_S on B_{<=d}) = |S|, and a (d+1)-dimensional affine subspace
(2^{d+1} points) does NOT (the bound is tight)."""
import gzip
import json
import os
import random
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "j7-mechanism"))
import rtlib as R  # noqa: E402

RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"


def rm_check():
    res = []
    for m in (5, 6, 7):
        for d in (0, 1, 2, 3):
            if 2 ** (d + 1) > 2 ** m:
                continue
            mons = [sum(1 << i for i in c) for k in range(d + 1) for c in combinations(range(m), k)]

            def rank_on(S):
                e = R.Echelon()
                for mon in mons:
                    v = 0
                    for t, x in enumerate(S):
                        if (mon & x) == mon:
                            v |= 1 << t
                    e.add(v)
                return e.rank()
            rng = random.Random(1000 * m + d)
            ok = 0
            for _ in range(200):
                S = rng.sample(range(2 ** m), 2 ** (d + 1) - 1)
                ok += rank_on(S) == len(S)
            sub = list(range(2 ** (d + 1)))  # the subspace spanned by the first d+1 coordinates
            tight = rank_on(sub) < len(sub)
            res.append({"m": m, "d": d, "random_sets_of_size_2^(d+1)-1_surjective": f"{ok}/200",
                        "affine_subspace_of_size_2^(d+1)_not_surjective": tight})
    return res


def main():
    recs = [json.loads(l) for l in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt")]
    by = {}
    for r in recs:
        by[(r["set"], r["idx"], r["closure"])] = r
    iset = json.load(open(os.path.join(RUN, "instance-sets.json")))["sets"]
    rows = []
    for inst in iset["S62"]:
        idx, s = inst["idx"], inst["archived"]["s"]
        w4 = by[("S62", idx, "W_4")]
        m5 = by[("S62", idx, "M_5")]
        row = {"idx": idx, "s": s, "W4_final_dim": w4["final_dim"], "W4_codim": 4048 - w4["final_dim"],
               "W4_one": w4["one"], "M5_rank": m5["rank"], "M5_one": m5["one"],
               "M5_cap_B4_codim": 4048 - m5["dims_by_deg"][4], "M5_codim_in_B5": 12616 - m5["rank"]}
        row["W4_codim_ge_s"] = row["W4_codim"] >= s
        row["W4_codim_eq_s"] = row["W4_codim"] == s
        row["M5_cap_B4_codim_ge_s"] = row["M5_cap_B4_codim"] >= s
        row["M5_cap_B4_codim_eq_s"] = row["M5_cap_B4_codim"] == s
        row["M5_codim_ge_s"] = row["M5_codim_in_B5"] >= s
        w5 = by.get(("S62", idx, "W_5"))
        if w5:
            row.update({"W5_final_dim": w5["final_dim"], "W5_codim_in_B5": 12616 - w5["final_dim"],
                        "W5_cap_B4_codim": 4048 - w5["dims_by_deg"][4], "W5_one": w5["one"]})
            row["W5_codim_ge_s"] = row["W5_codim_in_B5"] >= s
            row["W5_codim_eq_s"] = row["W5_codim_in_B5"] == s
        row["s_le_31"] = s <= 31
        rows.append(row)
    summ = {
        "n": len(rows),
        "s_distribution": {str(k): sum(1 for r in rows if r["s"] == k) for k in sorted({r["s"] for r in rows})},
        "all_s_le_31": all(r["s_le_31"] for r in rows),
        "W4_codim_ge_s_all": all(r["W4_codim_ge_s"] for r in rows),
        "W4_codim_eq_s_count": sum(r["W4_codim_eq_s"] for r in rows),
        "W4_refuted_any": any(r["W4_one"] for r in rows),
        "M5_cap_B4_codim_ge_s_all": all(r["M5_cap_B4_codim_ge_s"] for r in rows),
        "M5_cap_B4_codim_eq_s_count": sum(r["M5_cap_B4_codim_eq_s"] for r in rows),
        "M5_codim_in_B5_ge_s_all": all(r["M5_codim_ge_s"] for r in rows),
        "M5_refuted_any": any(r["M5_one"] for r in rows),
        "W5_rows": sum(1 for r in rows if "W5_final_dim" in r),
        "W5_codim_ge_s_all": all(r.get("W5_codim_ge_s", True) for r in rows),
        "W5_codim_eq_s_count": sum(1 for r in rows if r.get("W5_codim_eq_s")),
        "W5_refuted_any": any(r.get("W5_one") for r in rows),
    }
    out = {"task": "TASK-20260924-d95e70", "object": "O1", "source": "closures.jsonl.gz + instance-sets.json (archived only)",
           "summary": summ, "rm_lemma_machine_check": rm_check(), "rows": rows}
    json.dump(out, open(os.path.join(HERE, "o1-table.json"), "w"), indent=1)
    print(json.dumps({"summary": summ, "rm": out["rm_lemma_machine_check"]}, indent=1))


if __name__ == "__main__":
    main()
