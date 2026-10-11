#!/usr/bin/env python3
"""Post-hoc exact accounting of shared seed logs in frozen root sets."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"tasks/ec_relation_ml"))
from bridge import from_case, lift
from ec import RelationSystem


def derive(cases,exact):
    groups = {}
    for case in cases:
        groups.setdefault(case["curve_uid"],[]).append(case)
    rows = []
    for uid,cohort in sorted(groups.items()):
        curve = from_case(cohort[0])
        targets = {c["id"]:tuple(c["target"]) for c in cohort}
        seeds = {point for c in cohort for x in c["factor_x"] for point in lift(curve,x)}
        system = RelationSystem(curve,sorted(seeds),targets)
        initial = system.recoveries()
        for case in cohort:
            for x,y in exact[case["id"]]["roots"]:
                for left in lift(curve,x):
                    for right in lift(curve,y):
                        if curve.add(left,right)==tuple(case["target"]):
                            system.insert([(1,left),(1,right),(-1,tuple(case["target"]))])
        recovered = system.recoveries()
        if any(scalar != exact[name]["bsgs"]["scalar"] for name,scalar in recovered.items()):
            raise ValueError("batch recovery disagrees with separately verified BSGS")
        rows.append({"curve_uid":uid,"split":cohort[0]["split"],"targets":len(targets),
                     "initially_known_targets":len(initial),"newly_identified_targets":len(recovered)-len(initial),
                     "sum_of_separate_case_ranks":sum(exact[c["id"]]["relations"]["independent_rank"] for c in cohort),
                     "joint_unknown_columns":len(system.columns),"joint_rank":len(system.basis),
                     "verified_target_scalars":recovered,"target_case_ids":list(targets)})
    splits = {}
    for split in ("train","validation","test"):
        selected = [r for r in rows if r["split"]==split]
        splits[split] = {key:sum(r[key] for r in selected) for key in
                        ("targets","initially_known_targets","newly_identified_targets","sum_of_separate_case_ranks","joint_rank")}
    return {"splits":splits,"curve_batches":rows}


def main():
    output = Path(__file__).with_name("batch-relations-derived.json")
    results = {}
    for name in ("pilot-20261011","standard-20261011"):
        path = ROOT/"tasks/ec_relation_ml/examples"/name
        cases = json.loads((path/"cases.json").read_text())
        exact = json.loads((path/"exact_evaluation.json").read_text())
        results[name] = derive(cases,exact)
    record = {"kind":"post_hoc_exact_shared_batch_accounting","provenance":"Derived from frozen public inputs and measured root sets. New fits/solver trials were not run.",
              "scope":"Joint rank deduplicates shared seed logs within each exact curve. Recovery is checked by point multiplication and separately verified BSGS. No full batch-cost claim is supplied.",
              "results":results}
    with output.open("x") as stream:
        json.dump(record,stream,indent=2)
        stream.write("\n")
    print(json.dumps({name:v["splits"] for name,v in results.items()},indent=2))


if __name__=="__main__":
    main()
