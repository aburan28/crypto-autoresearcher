#!/usr/bin/env python3
"""J2 validity checks for EXP-PFDR-bb0d26 (TASK-20261029-958053, REVIEW-PFDR-bb0d26-20261029).

usage: j2_validity.py <repo_root> <scratch_root_with_tree> <out.json>

Reads the committed snapshot (repo_root at 1eddb474, clean tree) and a scratch tree (tree-auth.tar +
runs-head.tar extracted) in which check.py was run. Checks:
  run count and order, receipt hashes, manifest code/plan hashes against the plan and the authority-commit
  implementation, seed rule on every job record (curves regenerated with the vendored generator), census
  completeness against design.json, flags.json and the empty replication file, degenerate jobs and the
  invalid cell, and that no other cell has a non-ok job.
Curve regeneration imports the vendored curve.py (curve generator only; no counting code is used).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

EXP_REL = "experiments/EXP-PFDR-bb0d26"
AUTH = "48bd193abff869348779b06e4bd9a93b7bbe1d95"
SPEC_ORDER = [("selftest", "RUN-PFDR-e44a19"), ("census-toy-main", "RUN-PFDR-4d8c71"),
              ("analyze-main", "RUN-PFDR-243425"), ("census-toy-rep", "RUN-PFDR-cd03e2"),
              ("analyze-final", "RUN-PFDR-089edc")]
SEED_BLOCK = {"main": 8_100_000, "rep": 8_200_000, "selftest": 8_900_000}


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_git(root, rev, rel):
    b = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=root, capture_output=True, check=True).stdout
    return hashlib.sha256(b).hexdigest()


def main(argv):
    root, scratch, out_path = argv
    E = os.path.join(root, EXP_REL)
    R = os.path.join(E, "runs")
    rep = {"checks": [], "failures": []}

    def check(name, ok, detail=None):
        rep["checks"].append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            rep["failures"].append(name)

    # ---- run count and identities
    dirs = sorted(d for d in os.listdir(R) if os.path.isdir(os.path.join(R, d)))
    check("exactly five run directories", len(dirs) == 5, dirs)
    check("run directory names equal the specification's run ids", sorted(r for _, r in SPEC_ORDER) == dirs)
    receipts = {}
    for tid, rid in SPEC_ORDER:
        raw = json.load(open(os.path.join(R, rid, "raw-result.json")))
        rc = json.load(open(os.path.join(R, rid, "execution-receipt.json")))
        receipts[rid] = rc
        check(f"{rid} raw-result identity", raw["trial_id"] == tid and raw["run_id"] == rid and raw["experiment"] == "EXP-PFDR-bb0d26",
              {"trial_id": raw["trial_id"], "run_id": raw["run_id"]})
        check(f"{rid} receipt identity, status output_validated, returncode 0, check_returncode 0",
              rc["trial_id"] == tid and rc["run_id"] == rid and rc["status"] == "output_validated"
              and rc["returncode"] == 0 and rc["check_returncode"] == 0,
              {k: rc[k] for k in ("status", "returncode", "check_returncode", "started_at", "finished_at")})
    order = [receipts[r]["started_at"] for _, r in SPEC_ORDER]
    fins = [receipts[r]["finished_at"] for _, r in SPEC_ORDER]
    check("trials ran in specification order, each starting after the previous finished",
          all(order[i] < order[i + 1] and fins[i] <= order[i + 1] for i in range(4)),
          list(zip([t for t, _ in SPEC_ORDER], order, fins)))

    # ---- receipt hashes recomputed
    plan_path = os.path.join(E, "trial-plan.json")
    plan = json.load(open(plan_path))
    plan_sha = sha_file(plan_path)
    hash_rows = []
    for tid, rid in SPEC_ORDER:
        rc = receipts[rid]
        named = rc["artifact_sha256"]
        files = set(os.listdir(os.path.join(R, rid)))
        mism = []
        for name, want in sorted(named.items()):
            got = sha_file(os.path.join(R, rid, name))
            hash_rows.append({"run": rid, "file": name, "recorded": want, "recomputed": got, "equal": got == want})
            if got != want:
                mism.append(name)
        check(f"{rid} every file named in execution-receipt.json recomputes to its sha256", not mism,
              {"files_named": len(named), "mismatches": mism})
        check(f"{rid} run directory holds exactly the receipt-named files plus the receipt itself",
              files == set(named) | {"execution-receipt.json"},
              {"unnamed_files": sorted(files - set(named) - {"execution-receipt.json"}),
               "named_missing": sorted(set(named) - files)})
        check(f"{rid} receipt plan_sha256 equals sha256(trial-plan.json)", rc["plan_sha256"] == plan_sha)
        check(f"{rid} receipt authority commit is the authority commit", rc["authority"]["commit"] == AUTH)
    rep["receipt_hash_rows"] = hash_rows

    # ---- frozen code and plan hashes
    spec_sha = sha_file(os.path.join(E, "specification.yaml"))
    check("trial-plan specification_sha256 equals sha256(specification.yaml)", plan["specification_sha256"] == spec_sha,
          {"plan": plan["specification_sha256"], "file": spec_sha})
    src = plan["source_sha256"]
    for rel, want in sorted(src.items()):
        a = sha_git(root, AUTH, rel)
        h = sha_file(os.path.join(root, rel))
        check(f"plan source_sha256 {rel} equals the file at authority commit and at the snapshot", a == want == h,
              {"plan": want, "authority": a, "snapshot": h})
    import yaml
    for tid, rid in SPEC_ORDER:
        man = yaml.safe_load(open(os.path.join(R, rid, "manifest.yaml")))["run"]
        cs = man["code"]["code_sha256"]
        bad = []
        for k, v in cs.items():
            rel = f"{EXP_REL}/implementation/{k}"
            a = sha_git(root, AUTH, rel)
            if v != a or (rel in src and src[rel] != v):
                bad.append(k)
        check(f"{rid} manifest code_sha256 (all {len(cs)} files) equal the authority-commit files and the plan", not bad,
              {"files": sorted(cs), "mismatches": bad})
        check(f"{rid} manifest trial_plan_sha256 equals the plan", man["code"]["trial_plan_sha256"] == plan_sha)
        check(f"{rid} manifest commit is the authority commit and dirty is false",
              man["code"]["commit"] == AUTH and man["code"]["dirty"] is False,
              {"commit": man["code"]["commit"], "dirty": man["code"]["dirty"]})
        check(f"{rid} manifest python_version 3.11.15", man["environment"]["python_version"] == "3.11.15")
        check(f"{rid} manifest seed blocks equal the frozen rule", man["inputs"]["seed"] == SEED_BLOCK, man["inputs"]["seed"])
        env = json.load(open(os.path.join(R, rid, "environment.json")))
        check(f"{rid} environment.json source_sha256 equals the plan source_sha256", env["source_sha256"] == src
              and env["specification_sha256"] == spec_sha and env["commit"] == AUTH, env["python"])
    d = subprocess.run(["git", "diff", "--stat", AUTH, "origin/main", "--", f"{EXP_REL}/implementation",
                        f"{EXP_REL}/trial-plan.json", f"{EXP_REL}/specification.yaml", f"{EXP_REL}/runbook.yaml"],
                       cwd=root, capture_output=True, text=True, check=True).stdout
    t1 = subprocess.run(["git", "rev-parse", f"{AUTH}:{EXP_REL}/implementation"], cwd=root, capture_output=True, text=True).stdout.strip()
    t2 = subprocess.run(["git", "rev-parse", f"origin/main:{EXP_REL}/implementation"], cwd=root, capture_output=True, text=True).stdout.strip()
    t3 = subprocess.run(["git", "rev-parse", f"HEAD:{EXP_REL}/implementation"], cwd=root, capture_output=True, text=True).stdout.strip()
    check("implementation/ byte-unchanged authority -> origin/main -> HEAD (git tree ids equal, empty diff)",
          d.strip() == "" and t1 == t2 == t3, {"tree_authority": t1, "tree_origin_main": t2, "tree_head": t3,
                                               "origin_main": subprocess.run(["git", "rev-parse", "origin/main"], cwd=root,
                                                                             capture_output=True, text=True).stdout.strip()})

    # ---- design, completeness, seeds
    design = json.load(open(os.path.join(R, "RUN-PFDR-e44a19", "design.json")))
    cells = {c["cell"]: c for c in design["toy_cells"]}
    check("design.json has 45 cells", len(cells) == 45)
    recs = [json.loads(l) for l in open(os.path.join(R, "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")) if l.strip()]
    keys = [(r["cell"], r["c"]) for r in recs]
    planned = {(cid, c) for cid, cell in cells.items() for c in range(cell["n_curves"])}
    check("census-toy-main: one record per planned (cell, curve) key, no duplicates, no extras",
          len(keys) == len(set(keys)) and set(keys) == planned,
          {"records": len(recs), "planned": len(planned), "missing": len(planned - set(keys)), "extra": len(set(keys) - planned)})
    check("census-toy-main: every record block main", all(r["block"] == "main" for r in recs))
    check("census-toy-main: record bits/r/n equal the design cell", all(
        (r["bits"], r["r"], r["n"]) == (cells[r["cell"]]["bits"], cells[r["cell"]]["r"], cells[r["cell"]]["n"]) for r in recs))
    sys.path.insert(0, os.path.join(scratch, EXP_REL, "implementation", "vendor"))
    import curve as ec  # vendored generator, curve generation only
    curves = {}
    for r in recs:
        curves.setdefault((r["bits"], r["c"]), set()).add((r["p"], r["a"], r["b_coef"], r["N"]))
    incons = [k for k, v in curves.items() if len(v) != 1]
    check("records sharing (bits, c) share one curve (cells at the same bits share the curve set)", not incons, incons[:5])
    off = []
    for (bits, c), v in sorted(curves.items()):
        Ec, _ = ec.generate_prime_order_curve(bits, seed=SEED_BLOCK["main"] + c)
        if (Ec.p, Ec.a, Ec.b, Ec.order) not in v:
            off.append({"bits": bits, "c": c, "recorded": sorted(v), "regenerated": (Ec.p, Ec.a, Ec.b, Ec.order)})
    check("every job curve equals generate_prime_order_curve(bits, 8100000 + c)", not off,
          {"distinct_curves_checked": len(curves), "off_rule": off[:5]})
    check("every job p has the cell's bit length", all(r["p"].bit_length() == r["bits"] for r in recs))

    # ---- statuses
    nonok = [r for r in recs if r["status"] != "ok"]
    check("non-ok jobs: exactly 4, all degenerate, all in b20-r3-n4096",
          len(nonok) == 4 and all(r["status"] == "degenerate" and r["cell"] == "b20-r3-n4096" for r in nonok),
          [{"cell": r["cell"], "c": r["c"], "status": r["status"], "gap_meta": r["gap_meta"]} for r in nonok])
    check("degenerate jobs carry no counts", all(r["null_C"] is None and r["gap_C"] is None and r["plant_C"] is None for r in nonok))
    check("degenerate jobs exhausted the half-box (enumerated = ((2T+1)^r - 1)/2)",
          all(r["gap_meta"]["enumerated"] == ((2 * r["gap_meta"]["T"] + 1) ** r["r"] - 1) // 2 for r in nonok))
    check("degenerate jobs collected fewer than n labels (enumerated - duplicate_skips - infinity_skips < n)",
          all(r["gap_meta"]["enumerated"] - r["gap_meta"]["duplicate_skips"] - r["gap_meta"]["infinity_skips"] < r["n"] for r in nonok),
          [r["gap_meta"]["enumerated"] - r["gap_meta"]["duplicate_skips"] - r["gap_meta"]["infinity_skips"] for r in nonok])
    rm = json.load(open(os.path.join(R, "RUN-PFDR-4d8c71", "raw-result.json")))["summary"]
    check("census-toy-main raw-result summary equals the recount of the jobs file",
          rm == {"jobs": len(recs), "failed_infrastructure": sum(r["status"].startswith("failed_infrastructure") for r in recs),
                 "degenerate": sum(r["status"] == "degenerate" for r in recs)}, rm)
    for rid, fname in (("RUN-PFDR-243425", "analysis-main.json"), ("RUN-PFDR-089edc", "analysis.json")):
        an = json.load(open(os.path.join(R, rid, fname)))
        cls = {c["cell"]: c for c in an["cells"]}
        inv = cls["b20-r3-n4096"]
        check(f"{rid} b20-r3-n4096 class invalid (not null) with curves 46", inv["cls"] == "invalid",
              {k: inv.get(k) for k in ("cls", "curves", "S", "M", "kappa", "z", "powered")})
        check(f"{rid} every other cell has all n_curves ok records", all(
            sum(1 for r in recs if r["cell"] == cid and r["status"] == "ok") == cells[cid]["n_curves"]
            for cid in cells if cid != "b20-r3-n4096"))
        classes = {}
        for c in an["cells"]:
            classes[c["cls"]] = classes.get(c["cls"], 0) + 1
        check(f"{rid} classes: 44 null, 1 invalid; flagged_cells empty; outcome O-NULL; headline SUPPORT_SCOPED",
              classes == {"null": 44, "invalid": 1} and an["flagged_cells"] == [] and an["outcome"] == "O-NULL"
              and an.get("headline") == "SUPPORT_SCOPED", {"classes": classes, "outcome": an["outcome"],
                                                           "headline": an.get("headline"), "fraction_valid": an["fraction_valid"],
                                                           "calibration": an["calibration"]})
        check(f"{rid} fraction_valid = 44/45", an["fraction_valid"] == 44 / 45, an["fraction_valid"])
    # ---- replication rule
    for rid in ("RUN-PFDR-243425", "RUN-PFDR-089edc"):
        fl = json.load(open(os.path.join(R, rid, "flags.json")))
        check(f"{rid} flags.json lists no cell", fl == {"flagged_cells": []}, fl)
    tr = os.path.join(R, "RUN-PFDR-cd03e2", "toy-rep-jobs.jsonl")
    check("toy-rep-jobs.jsonl is zero bytes", os.path.getsize(tr) == 0, os.path.getsize(tr))
    rr = json.load(open(os.path.join(R, "RUN-PFDR-cd03e2", "raw-result.json")))["summary"]
    check("census-toy-rep summary 0 jobs, 0 failed, 0 degenerate (frozen stopping rule with no flagged cell)",
          rr == {"jobs": 0, "failed_infrastructure": 0, "degenerate": 0}, rr)
    ct = next(t for t in plan["trials"] if t["id"] == "census-toy-rep")
    check("census-toy-rep reads flags from RUN-PFDR-243425 and allows an empty toy-rep-jobs.jsonl",
          ct["inputs_from"].get("flags") == "RUN-PFDR-243425/flags.json" and ct.get("allow_empty_artifacts") == ["toy-rep-jobs.jsonl"])

    rep["ok"] = not rep["failures"]
    rep["python"] = sys.version
    rep["executable"] = sys.executable
    with open(out_path, "w") as f:
        json.dump(rep, f, indent=1, default=str)
    for c in rep["checks"]:
        print(("OK   " if c["ok"] else "FAIL ") + c["check"])
    print("FAILURES:", rep["failures"])
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
