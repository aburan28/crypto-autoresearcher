#!/usr/bin/env python3
"""finalize.py -- TASK-20260804-8965ec

Builds RESULTS.json and anchor_results.json from raw.jsonl and pin_receipt.json.
Performs NO arithmetic beyond copying/comparing fields already present in the
engines' own JSON output -- per this campaign's convention that summaries must
agree with raw data because the builder does no independent computation.

INFERENCE BLOCK: policy executor-implementation, requested_policy
executor-implementation, resolved_model claude-sonnet-5, fallback_used false,
model_verified false, standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
"""
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

def load_raw():
    arms = {}
    path = os.path.join(HERE, "raw.jsonl")
    if not os.path.exists(path):
        return arms
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            arms[d.get("label", "UNKNOWN")] = d
    return arms

def main():
    arms = load_raw()
    pin = {}
    pin_path = os.path.join(HERE, "pin_receipt.json")
    if os.path.exists(pin_path):
        pin = json.load(open(pin_path))

    cases = {}
    for case, count5_lbl, cnt_lbl, r in [
        ("CASE_Z", "CASE_Z_count5", "CASE_Z_cnt_soft", 4),
        ("CASE_NZ", "CASE_NZ_count5", "CASE_NZ_cnt_soft", 5),
    ]:
        c5 = arms.get(count5_lbl)
        cn = arms.get(cnt_lbl)
        entry = {
            "r": r,
            "count5_arm": c5,
            "cnt_soft_arm": cn,
        }
        if c5 and cn and "n" in c5 and "n" in cn:
            entry["n_agree"] = (c5["n"] == cn["n"])
            entry["N_agree"] = (c5.get("N") == cn.get("N"))
        else:
            entry["n_agree"] = None
            entry["N_agree"] = None
            entry["not_run_or_incomplete"] = True
        cases[case] = entry

    out = {
        "task_id": "TASK-20260804-8965ec",
        "objective": "cross-instrument anchor between BATCH-001's count5.c and BATCH-002's cnt.c",
        "pin_receipt": pin,
        "cases": cases,
        "raw_arms_present": sorted(arms.keys()),
    }
    with open(os.path.join(HERE, "anchor_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
