#!/usr/bin/env python3
"""Write the content-first snapshot receipt for TASK-20260905-73ac7e.

Usage: python3 make_receipt.py <repo-root> <filed-idea-id> ... [--unused ID ...]
Hashes every declared path at the working tree; commit_sha/parent_sha stay null
(the receipt cannot embed its own hash or the commit that will contain it).
"""
import hashlib, json, os, sys, datetime

root = sys.argv[1]
args = sys.argv[2:]
unused = args[args.index("--unused") + 1:] if "--unused" in args else []
filed = [a for a in args if a.startswith("IDEA-") and a not in unused]
NS = "equation-schemes-20260905-802f7c"
TASK = "TASK-20260905-73ac7e"
PROD = "TASK-20260905-802f7c"
here = f"coordination/ideation/{NS}/archives/{TASK}"
paths = [f"ledger/proposals/{i}.yaml" for i in filed] + [
    f"ledger/handoffs/{PROD}.yaml", f"ledger/handoffs/{TASK}.yaml",
    f"coordination/ideation/{NS}/tasks/{PROD}/context.md",
    f"coordination/ideation/{NS}/tasks/{PROD}/report.md",
    f"coordination/ideation/{NS}/tasks/{PROD}/sources.json",
    "research/equation_schemes_safecurves_20260905.md",
    "research/equation-schemes-20260905/equation_schemes_check.py",
    "research/equation-schemes-20260905/parse_safecurves.py",
    "research/equation-schemes-20260905/parsed_safecurves.json",
    "research/equation-schemes-20260905/results.json",
    "research/equation-schemes-20260905/table.md",
]
rp = os.path.join(root, "research/equation-schemes-20260905/retrieved-pages")
paths += sorted(f"research/equation-schemes-20260905/retrieved-pages/{f}" for f in os.listdir(rp) if not f.endswith(".pdf"))
paths.append(f"{here}/snapshot-receipt.json")
sha = {}
for p in paths:
    fp = os.path.join(root, p)
    if p.endswith("snapshot-receipt.json"):
        sha[p] = None; continue
    if not os.path.exists(fp):
        sys.exit(f"missing declared path: {p}")
    sha[p] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
receipt = {
    "schema": "crypto.autoresearch.archive_receipt.v1",
    "task_id": TASK, "goal_id": None, "batch_id": None,
    "ideation_namespace": NS,
    "goal_ids_bound_by_proposals": sorted({g for i in filed for g in
        __import__("re").findall(r"GOAL-[A-Z]+-[0-9a-f]{3,6}", open(os.path.join(root, f"ledger/proposals/{i}.yaml")).read())}),
    "archive_kind": "snapshot", "kind": "snapshot", "binding_mode": "content_first",
    "status": "prepared_for_post_commit_verification",
    "prepared_at": datetime.date.today().isoformat(),
    "commit_sha": None, "parent_sha": None, "receipt_self_sha256": None,
    "source_task_ids": [PROD],
    "record_ids": filed + [PROD, TASK],
    "paths": paths, "path_sha256": sha,
    "unused_preallocated_ids": unused,
    "seed_provenance": "User-supplied instruction and pasted SafeCurves Equations page (2026-09-05), recorded verbatim in tasks/" + PROD + "/context.md; a pointer, not a citation, not evidence.",
    "questions_unchanged": ["ledger/questions/RQ-ECDLP-623a32.yaml", "ledger/questions/RQ-MODEL-e61cb2.yaml"],
    "scientific_boundary": "Proposals and an arithmetic verification note only: no hypothesis, experiment, evidence or decision record is created and no status changes; approval is /design-experiment under Coordinator authority; no SCURVE criterion cell is adjudicated.",
    "self_neutrality": "The receipt cannot embed its own hash, commit SHA or parent SHA; those remain null.",
}
out = os.path.join(root, here, "snapshot-receipt.json")
json.dump(receipt, open(out, "w"), indent=2)
print("wrote", out, "with", len(paths), "paths;", len(filed), "proposals;", len(unused), "unused ids")
