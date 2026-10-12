"""J-VAL (4) supplementary: TB recount under the PDI-3 reading (TB pairs = star pairs
(1, j) only; a tail-tail pair (i, j) is a TT pair, CC-4), TASK-20261009-33b5cf.
Imports recount.py of this directory (this task's own code) for the CC-1 primitives.
(a) TB distinct monic count per instance from star pairs only, compared with the census
    harvest.TB.at_stop.relations_distinct of every instance, and its total per arm with
    analysis.json secondary.TB_counts;
(b) for every instance where the plain-CC-1 TB count differs, whether each extra
    (tail-tail) relation is in the same instance's TT relation set.
No seeds. Usage: python tb_pdi3.py <repo> <out.json>
"""
import gzip
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recount as rc  # noqa: E402

RUN = "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-table"


def main():
    repo, outp = sys.argv[1:3]
    design = json.load(open(os.path.join(repo, rc.DESIGN)))
    Nof = {(c["bits"], c["curve"]): int(c["N"]) for c in design["curves"]}
    an = json.load(open(os.path.join(repo, "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-analysis/analysis.json")))
    jobs = os.path.join(repo, RUN, "attempt-1", "jobs")
    tot = defaultdict(int)
    mism = []
    extra = []
    for job in sorted(os.listdir(jobs)):
        inst = defaultdict(list)
        with gzip.open(os.path.join(jobs, job, "harvest-rows.jsonl.gz"), "rt") as fh:
            for line in fh:
                r = json.loads(line)
                inst[(r["bits"], r["curve"], r["arm"], r["class"])].append(r)
        census = {}
        with gzip.open(os.path.join(jobs, job, "rows.jsonl.gz"), "rt") as fh:
            for line in fh:
                r = json.loads(line)
                census[(r["bits"], r["curve"], r["arm"])] = r["harvest"]["TB"]["at_stop"]["relations_distinct"]
        for (b, c, arm), want in census.items():
            rows = inst.get((b, c, arm, "TB"), [])
            N = Nof[(b, c)]
            star = set()
            for r in rows:
                rv = rc.reduce_vec(rc.vec_of(r), N)
                if rc.first_nonzero(rv):
                    star.add(rc.monic(rv, N))
            tot[arm] += len(star)
            if len(star) != want:
                mism.append([b, c, arm, len(star), want])
            if rows:
                full = rc.recount_instance(rows, N)["set"]
                if full != star:
                    tt = rc.recount_instance(inst.get((b, c, arm, "TT"), []), N)["set"]
                    for v in full - star:
                        extra.append({"instance": [b, c, arm], "extra_relation_in_TT_set": v in tt})
    out = {"tb_star_only_vs_census_mismatches": mism,
           "tb_star_only_totals": dict(tot),
           "analysis_TB_counts": an["secondary"]["TB_counts"],
           "totals_equal": {a: tot[a] == an["secondary"]["TB_counts"][a] for a in tot},
           "plain_cc1_extra_relations": extra}
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
