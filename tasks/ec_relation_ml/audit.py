#!/usr/bin/env python3
"""Retrospective data-readiness audit; no fitting or outcome-driven split."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def connected_components(rows, keys):
    parents = list(range(len(rows)))
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    owners = {}
    for i,row in enumerate(rows):
        for name in keys:
            key = (name,str(row[name]))
            if key in owners:
                parents[find(i)] = find(owners[key])
            else:
                owners[key] = i
    groups = {}
    for i in range(len(rows)):
        groups.setdefault(find(i),[]).append(i)
    return sorted([len(v) for v in groups.values()],reverse=True)


def audit(repo):
    relative = Path("experiments/EXP-ECDLP-4c6a09/reports/random-fields-20261011T0523Z/methods.csv")
    path = repo/relative
    rows = list(csv.DictReader(path.open()))
    clusters = connected_components(rows,("field_id","curve_uid","p"))
    return {"kind":"retrospective_ml_data_readiness","source_run":"RUN-ECDLP-9e6cc1",
            "source_path":relative.as_posix(),"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "rows":len(rows),"distinct_source_number_fields":len({r["field_id"] for r in rows}),
            "distinct_finite_prime_fields":len({r["p"] for r in rows}),
            "distinct_exact_curve_uids":len({r["curve_uid"] for r in rows}),
            "nominal_repeated_target_attempts":sum(int(r["target_count"]) for r in rows),
            "reported_target_recoveries":sum(int(r["target_recoveries"]) for r in rows),
            "connected_components_requiring_common_source_field_curve_and_prime":clusters,
            "three_way_simultaneous_holdout_possible":len(clusters)>=3,
            "provenance":"internal; derived from retained CSV, not an independent recheck of point equations",
            "interpretation":"Rows are repeated cohorts, not independent fields or independent targets. A simultaneous source-number-field and finite-curve holdout connects these rows; changing row IDs does not remove dependence.",
            "status":"exploratory_only; do not claim a fresh untouched confirmation set",
            "excluded_post_outcome_features":["distinct_subgroup_points","subgroup_coverage_fraction",
                "target_recoveries","useful_relations_per_1000_group_calls",
                "recoveries_per_1000_group_calls","group_calls","global_relation_rank"],
            "feature_acquisition_note":"Seed count, certified rank and number-field descriptors may be public inputs only after their discovery/acquisition costs are charged; unfinished rank searches are retained.",
            "next_corpus_note":"Hold out new finite fields/curves for the same fixed lift template, and run a separate source-number-field/template holdout. A shared fixed template cannot simultaneously be a new unseen template."}


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo",type=Path,default=Path.cwd())
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = audit(args.repo)
    with args.output.open("x") as stream:
        json.dump(result,stream,indent=2)
        stream.write("\n")
    print(json.dumps(result,indent=2))
