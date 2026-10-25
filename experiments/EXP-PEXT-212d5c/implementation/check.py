#!/usr/bin/env python3
"""Producer-written output checker of EXP-PEXT-212d5c (not independent review).

  python3 check.py RUN_DIR experiments/EXP-PEXT-212d5c/trial-plan.json TRIAL_ID

Checks that every declared artifact of the trial exists and parses, that raw-result.json names this run and trial,
and the stage's internal consistency: regression (every check identical), construct (configs = 14 x orbit reps, every
configuration (m, r) = (3, 7)), char2 (element totals 2^N - 1), census (structures per model = (Q^3 - Q)/(q^3 - q),
stratum counts, zero subcover-sum mismatches, every curve record carries j_idx and stratum), lean (status recorded),
analyze (every prediction carries an outcome). Exit 0 when well-formed; findings such as derived-check violations
are reported, not repaired. Standard library plus PyYAML.
"""
from __future__ import annotations

import json
import os
import sys

import yaml


def jl(path: str) -> list:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> int:
    rd, plan_path, tid = sys.argv[1:4]
    with open(plan_path) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == tid)
    errors: list = []
    for name in trial["artifacts"]:
        if not os.path.isfile(os.path.join(rd, name)):
            errors.append(f"missing artifact {name}")
    if errors:
        print("\n".join(errors))
        return 1
    with open(os.path.join(rd, "raw-result.json")) as f:
        raw = json.load(f)
    if raw.get("run_id") != trial["run_id"] or raw.get("trial_id") != tid or raw.get("experiment") != plan["experiment_id"]:
        errors.append("raw-result.json does not name this run, trial and experiment")
    with open(os.path.join(rd, "manifest.yaml")) as f:
        man = yaml.safe_load(f)
    if man["run"]["id"] != trial["run_id"]:
        errors.append("manifest run id mismatch")
    stage = trial["stage"]
    notes: list = []
    if raw.get("invalid_reason"):
        notes.append(f"recorded invalid_reason: {raw['invalid_reason']}")
    if stage == "regression":
        with open(os.path.join(rd, "regression.json")) as f:
            reg = json.load(f)
        bad = [c["name"] for c in reg["checks"] if not c["identical"]]
        if reg["pass"] != (not bad):
            errors.append("regression.json pass flag disagrees with its checks")
        notes.append(f"regression checks {len(reg['checks'])}, failed {bad}")
    elif stage == "construct":
        for q in (3, 5, 7):
            recs = jl(os.path.join(rd, f"construct-q{q}.jsonl"))
            s = next(r for r in recs if r["rec"] == "construct")
            cur = [r for r in recs if r["rec"] == "construct_curve"]
            if s["configs"] != 14 * s["x_orbit_reps"] or s["x_orbit_reps"] != (q ** 7 - q) // (q ** 3 - q):
                errors.append(f"q={q}: configuration count is not 14 (q^7 - q)/(q^3 - q)")
            if len(cur) != s["j_genus7"] or sum(r["configs"] for r in cur) != s["configs"]:
                errors.append(f"q={q}: per-j records do not add up")
            if any(r["order"] + r["order_twist"] != 2 * q ** 7 + 2 for r in cur):
                errors.append(f"q={q}: twist orders do not sum to 2Q + 2")
            notes.append(f"q={q}: j_genus7 {s['j_genus7']} of {s['j_split']}, configs other {s['configs_other']}")
    elif stage == "char2":
        for r in jl(os.path.join(rd, "char2.jsonl")):
            if sum(r["m_hist"].values()) != 2 ** r["N"] - 1:
                errors.append(f"l={r['l']}: histogram does not cover K*")
            notes.append(f"l={r['l']}: m_hist {r['m_hist']}, prediction match {r['matches_prediction']}")
    elif stage == "census":
        recs = jl(os.path.join(rd, "census-n7-q3.jsonl"))
        field = next(r for r in recs if r["rec"] == "field")
        tot = next(r for r in recs if r["rec"] == "totals")
        curves = [r for r in recs if r["rec"] == "curve"]
        q = 3
        expect = (q ** 21 - q ** 7) // (q ** 3 - q)
        if field["structures"] != expect or field["structures_expected"] != expect:
            errors.append("structure count per model is not (Q^3 - Q)/(q^3 - q)")
        for c in curves:
            if sum(c["structures_by_genus"].values()) + c["m1_structures"] != expect:
                errors.append(f"curve A{c['A_idx']} B{c['B_idx']}: structures do not add up")
            if "j_idx" not in c or "stratum" not in c:
                errors.append("curve record without j_idx or stratum")
        if len(curves) != tot["models_total"]:
            errors.append("curve records do not match models_total")
        if tot["mismatches"]:
            errors.append(f"subcover-sum mismatches {tot['mismatches']}")
        dc = next(r for r in recs if r["rec"] == "derived_checks")
        notes.append(f"models {len(curves)}; derived-check violations {dc['violations']}")
    elif stage == "lean":
        with open(os.path.join(rd, "lean.json")) as f:
            le = json.load(f)
        notes.append(f"lean status {le['status']}")
    elif stage == "analyze":
        with open(os.path.join(rd, "analysis.json")) as f:
            an = json.load(f)
        if any("outcome" not in v for v in an["predictions"].values()):
            errors.append("a prediction without an outcome")
        notes.append(f"headline: {an['headline']}")
    for n in notes:
        print(n)
    for e in errors:
        print("ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
