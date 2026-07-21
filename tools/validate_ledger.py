#!/usr/bin/env python3
"""Validate the research ledger, experiments, and run records.

Mechanically enforces the invariants that AGENTS.md and docs/ state in prose:

  * every record's ID matches its type's format and its filename;
  * IDs are globally unique (never reused);
  * cross-references resolve (hypothesis->question, evidence->run, ...);
  * required fields are present per record type;
  * run manifests are complete and reproducible;
  * a run claiming a solve carries a verified certificate;
  * an evidence record never asserts above the claim tier its runs allow;
  * knowledge/INDEX.md is not stale.

Exit code 0 if clean, 1 if any error. Empty ledger validates clean.

Usage: python3 tools/validate_ledger.py
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ID_PATTERNS = {
    "research_question": re.compile(r"^RQ-[A-Z]+-\d{3}$"),
    "idea": re.compile(r"^IDEA-\d{8}-\d{3}$"),
    "hypothesis": re.compile(r"^H-[A-Z]+-\d{3}$"),
    "experiment": re.compile(r"^EXP-[A-Z]+-\d{3}$"),
    "evidence": re.compile(r"^EV-[A-Z]+-\d{3}$"),
    "coordinator_decision": re.compile(r"^DEC-\d{8}-\d{3}$"),
    "handoff": re.compile(r"^TASK-\d{8}-\d{3}$"),
}
RUN_ID = re.compile(r"^RUN-[A-Za-z0-9._-]+$")

# Ledger record types are detected by their single top-level key, so records
# validate whether they live flat in ledger/ (e.g. ledger/H-DREG-001.yaml) or in
# a typed subdirectory (e.g. ledger/hypotheses/H-SEMAEV-001.yaml). Both layouts
# are in use in this repo.
LEDGER_TYPES = {
    "research_question", "idea", "hypothesis", "evidence",
    "coordinator_decision", "handoff",
}

REQUIRED = {
    "research_question": ["id", "title", "scope", "status", "owner"],
    "idea": ["id", "title", "class", "claim", "mechanism", "novelty_status"],
    "hypothesis": ["id", "question_id", "statement", "mechanism", "status"],
    "experiment": ["id", "hypothesis_id", "version", "status", "metrics",
                   "budget", "success_criterion"],
    "evidence": ["id", "hypothesis_id", "run_ids", "direction", "strength",
                 "claim_tier"],
    "coordinator_decision": ["id", "decision", "target_ids", "decided_by"],
    "handoff": ["id", "from", "to", "objective", "budget"],
}

RUN_REQUIRED_TOP = ["id", "experiment_id", "status", "code", "environment",
                    "inputs", "timing", "result"]

TIER_ORDER = {"toy": 0, "medium": 1, "crypto": 2}


class Ctx:
    def __init__(self):
        self.errors: list[str] = []
        self.ids: dict[str, str] = {}          # id -> source path
        self.records: dict[str, dict] = {}      # id -> record body
        self.run_params: dict[str, dict] = {}   # run id -> inputs.parameters

    def err(self, path: str, msg: str):
        self.errors.append(f"{os.path.relpath(path, REPO)}: {msg}")

    def register(self, rec_id: str, path: str, body: dict):
        if rec_id in self.ids:
            self.err(path, f"duplicate ID {rec_id} (also in "
                           f"{os.path.relpath(self.ids[rec_id], REPO)})")
        else:
            self.ids[rec_id] = path
            self.records[rec_id] = body


def load_yaml(path: str, ctx: Ctx):
    try:
        return yaml.safe_load(open(path, encoding="utf-8"))
    except yaml.YAMLError as e:
        ctx.err(path, f"invalid YAML: {e}")
        return None


def check_ledger_record(path: str, rec_type: str, ctx: Ctx):
    doc = load_yaml(path, ctx)
    if doc is None:
        return
    if not isinstance(doc, dict) or rec_type not in doc:
        ctx.err(path, f"expected top-level key '{rec_type}'")
        return
    body = doc[rec_type]
    if not isinstance(body, dict):
        ctx.err(path, f"'{rec_type}' must be a mapping")
        return
    rec_id = body.get("id")
    if not rec_id:
        ctx.err(path, "missing 'id'")
        return
    if not ID_PATTERNS[rec_type].match(str(rec_id)):
        ctx.err(path, f"ID {rec_id} does not match {rec_type} format")
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem != str(rec_id):
        ctx.err(path, f"filename stem '{stem}' != id '{rec_id}'")
    for field in REQUIRED[rec_type]:
        if body.get(field) in (None, ""):
            ctx.err(path, f"missing required field '{field}'")
    ctx.register(str(rec_id), path, body)


def check_experiment(path: str, ctx: Ctx):
    doc = load_yaml(path, ctx)
    if doc is None:
        return
    if not isinstance(doc, dict) or "experiment" not in doc:
        ctx.err(path, "expected top-level key 'experiment'")
        return
    body = doc["experiment"]
    rec_id = body.get("id")
    if not rec_id or not ID_PATTERNS["experiment"].match(str(rec_id)):
        ctx.err(path, f"bad experiment id {rec_id!r}")
        return
    for field in REQUIRED["experiment"]:
        if body.get(field) in (None, ""):
            ctx.err(path, f"missing required field '{field}'")
    # An approved contract must have no null approval fields.
    if body.get("status") == "approved":
        for field in ("success_criterion", "falsification_criterion",
                      "approved_by"):
            if body.get(field) in (None, ""):
                ctx.err(path, f"approved experiment has null '{field}'")
    ctx.register(str(rec_id), path, body)


def check_run(path: str, ctx: Ctx):
    doc = load_yaml(path, ctx)
    if doc is None:
        return
    body = doc.get("run") if isinstance(doc, dict) else None
    if not isinstance(body, dict):
        ctx.err(path, "expected top-level key 'run'")
        return
    rec_id = body.get("id")
    if not rec_id or not RUN_ID.match(str(rec_id)):
        ctx.err(path, f"bad run id {rec_id!r}")
    for field in RUN_REQUIRED_TOP:
        if body.get(field) in (None, ""):
            ctx.err(path, f"run missing required field '{field}'")
    # Reproducibility: commit + command must be present.
    code = body.get("code") or {}
    if not code.get("commit"):
        ctx.err(path, "run.code.commit missing (not reproducible)")
    if not code.get("command"):
        ctx.err(path, "run.code.command missing (not reproducible)")
    # Companion artifacts must exist next to the manifest.
    run_dir = os.path.dirname(path)
    for artifact in ("command.txt", "environment.json", "stdout.log",
                     "stderr.log", "raw-result.json"):
        if not os.path.exists(os.path.join(run_dir, artifact)):
            ctx.err(path, f"run directory missing artifact '{artifact}'")
    # Certificate discipline (docs/claims-and-verification.md).
    result = body.get("result") or {}
    cert = result.get("certificate") or {}
    kind = cert.get("kind")
    if kind in ("discrete_log", "decomposition"):
        if cert.get("verified") is not True:
            ctx.err(path, f"run claims a {kind} but certificate.verified "
                          f"is not true")
    elif kind != "none":
        ctx.err(path, "run.result.certificate.kind must be one of "
                      "discrete_log|decomposition|none")
    if rec_id:
        ctx.run_params[str(rec_id)] = (body.get("inputs") or {}).get("parameters") or {}
        ctx.register(str(rec_id), path, body)


def tier_of_run(params: dict) -> int | None:
    bits = params.get("field_bits") or params.get("field_bit_size")
    if bits is None:
        return None
    bits = int(bits)
    if bits <= 32:
        return TIER_ORDER["toy"]
    if bits <= 96:
        return TIER_ORDER["medium"]
    return TIER_ORDER["crypto"]


def check_cross_refs(ctx: Ctx):
    for rec_id, body in list(ctx.records.items()):
        if rec_id.startswith("H-"):
            q = body.get("question_id")
            if q and q not in ctx.ids:
                ctx.err(ctx.ids[rec_id], f"hypothesis references unknown "
                                         f"question '{q}'")
        elif rec_id.startswith("EXP-"):
            h = body.get("hypothesis_id")
            if h and h not in ctx.ids:
                ctx.err(ctx.ids[rec_id], f"experiment references unknown "
                                         f"hypothesis '{h}'")
        elif rec_id.startswith("EV-"):
            h = body.get("hypothesis_id")
            if h and h not in ctx.ids:
                ctx.err(ctx.ids[rec_id], f"evidence references unknown "
                                         f"hypothesis '{h}'")
            for run_id in body.get("run_ids") or []:
                if run_id not in ctx.ids:
                    ctx.err(ctx.ids[rec_id], f"evidence references unknown "
                                             f"run '{run_id}'")
            for exp_id in body.get("experiment_ids") or []:
                if exp_id not in ctx.ids:
                    ctx.err(ctx.ids[rec_id], f"evidence references unknown "
                                             f"experiment '{exp_id}'")
            # Claim-tier ceiling.
            declared = TIER_ORDER.get(body.get("claim_tier"))
            run_tiers = [tier_of_run(ctx.run_params.get(r, {}))
                         for r in body.get("run_ids") or []]
            run_tiers = [t for t in run_tiers if t is not None]
            if declared is not None and run_tiers and declared > max(run_tiers):
                ctx.err(ctx.ids[rec_id], f"claim_tier '{body.get('claim_tier')}'"
                                         f" exceeds what its runs' parameters "
                                         f"allow")


def check_knowledge_index(ctx: Ctx):
    rc = subprocess.run(
        [sys.executable, os.path.join(REPO, "tools", "build_knowledge_index.py"),
         "--check"],
        capture_output=True, text=True)
    if rc.returncode != 0:
        ctx.errors.append((rc.stderr or rc.stdout).strip() or
                          "knowledge/INDEX.md is stale")


def detect_ledger_type(path: str, ctx: Ctx) -> str | None:
    """Identify a ledger record by its single known top-level key.

    Returns None for YAML that is not one of the validated ledger record types
    (e.g. research_goal, archive receipts, helper data), so those files are
    skipped rather than misreported.
    """
    doc = load_yaml(path, ctx)
    if not isinstance(doc, dict):
        return None
    present = [k for k in doc.keys() if k in LEDGER_TYPES]
    if len(present) == 1:
        return present[0]
    return None


def main() -> int:
    ctx = Ctx()
    ledger_root = os.path.join(REPO, "ledger")
    for path in sorted(glob.glob(os.path.join(ledger_root, "**", "*.yaml"),
                                 recursive=True)):
        rec_type = detect_ledger_type(path, ctx)
        if rec_type is not None:
            check_ledger_record(path, rec_type, ctx)
    for path in sorted(glob.glob(os.path.join(REPO, "experiments", "*",
                                              "specification.yaml"))):
        check_experiment(path, ctx)
    for path in sorted(glob.glob(os.path.join(REPO, "experiments", "*", "runs",
                                              "*", "manifest.yaml"))):
        check_run(path, ctx)
    check_cross_refs(ctx)
    check_knowledge_index(ctx)

    if ctx.errors:
        print(f"FAIL: {len(ctx.errors)} validation error(s):\n", file=sys.stderr)
        for e in ctx.errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(ctx.ids)} records, ledger is consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
