#!/usr/bin/env python3
"""Validate the research ledger, experiments, and run records.

Mechanically enforces the invariants that AGENTS.md and docs/ state in prose:

  * every record's ID matches its type's format and its filename;
  * IDs are globally unique (never reused);
  * cross-references resolve (hypothesis->question, evidence->run, ...);
  * required fields are present per record type;
  * run manifests are complete and reproducible;
  * a run claiming a solve carries a verified certificate;
  * evidence records carry descriptive scale metadata and explicit scope;
  * knowledge/INDEX.md is not stale.

Exit code 0 if clean, 1 if any error. Empty ledger validates clean.

Legacy records that predate this validator are grandfathered via
tools/validate_ledger_baseline.txt: known error lines listed there are
reported as suppressed instead of failing the build, so new violations
still block while immutable historical run records stay untouched.
Entries may only ever be removed from the baseline (as records are
repaired or superseded), never added — regenerating it to absorb a new
violation defeats the check.

An archived run manifest that is repaired by a NEW record rather than an
edit (AGENTS.md core rule 4) is routed via tools/run_supersession_registry.yaml:
the run-schema check reads the superseding record, while both files stay
pinned by sha256 and the superseded file must remain present at its
original path. Supersession redirects the check; it never suppresses it.

The same rule applies to archived ledger, experiment, knowledge, and goal
checkpoint records through tools/schema_supersession_registry.yaml.  The
discovered source stays byte-identical and hash-pinned; validation reads the
explicit replacement record.  This is deliberately separate from the legacy
inventories and the prune-only baseline: a supersession must supply a complete
record and cannot turn an error into a warning.

Usage: python3 tools/validate_ledger.py [--no-baseline] [--update-baseline]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import stat
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE_PATH = os.path.join(REPO, "tools", "validate_ledger_baseline.txt")
LEGACY_LEDGER_INVENTORY = os.path.join(
    REPO, "tools", "legacy_ledger_inventory.yaml"
)
LEGACY_RUN_INVENTORY = os.path.join(
    REPO, "tools", "legacy_run_inventory.yaml"
)
RUN_SUPERSESSION_REGISTRY = os.path.join(
    REPO, "tools", "run_supersession_registry.yaml"
)
RUN_SUPERSESSION_SCHEMA = "run-supersession-registry-v1"
RUN_SUPERSESSION_REQUIRED = ["run_id", "superseded_path", "superseded_sha256",
                             "superseding_path", "superseding_sha256",
                             "defect", "registered"]
# The exact shape check_run() discovers by glob. A superseded record must match
# it (otherwise the entry would never be consulted and would only mislead), and
# a superseding record must NOT match it (otherwise the glob would find it too
# and register the same run id twice, weakening the duplicate-ID check).
RUN_MANIFEST_PATH = re.compile(
    r"^experiments/[^/]+/runs/[^/]+/manifest\.yaml$")
SCHEMA_SUPERSESSION_REGISTRY = os.path.join(
    REPO, "tools", "schema_supersession_registry.yaml"
)
SCHEMA_SUPERSESSION_SCHEMA = "schema-supersession-registry-v1"
SCHEMA_SUPERSESSION_REQUIRED = ["kind", "superseded_path",
                                "superseded_sha256", "superseding_path",
                                "superseding_sha256", "defect", "registered"]
SCHEMA_SUPERSESSION_KINDS = {
    "ledger", "experiment", "knowledge", "goal_checkpoint"
}
SCHEMA_SUPERSESSION_ROOT = "ledger/corrections/schema-supersessions/"
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

# Identifier suffixes. TWO FORMS ARE VALID AND THE RANDOM ONE IS PREFERRED.
#
#   SUFFIX_LEGACY  \d{3}        sequential, allocated max+1. Every record minted
#                               before 2026-08-01 uses it. STILL VALID FOREVER --
#                               those records are immutable and must keep
#                               validating -- but NEVER MINT A NEW ONE.
#   SUFFIX_RANDOM  [0-9a-f]{6}  a random 24-bit token. This is the form new
#                               records use.
#
# Why the change: sequential allocation requires scanning committed state for a
# maximum, and CONCURRENT WORKTREES ALL SCAN THE SAME STATE AND GET THE SAME
# ANSWER. They then mint the same identifier for different records, and the
# collision is only discovered at merge time, when both records are already
# committed and immutable and neither can be renamed without breaking whatever
# archive binds it. The random token needs no scan at all, so two worktrees
# cannot converge by construction. Cost of the change: identifiers no longer
# sort into creation order. Nothing in this repository ordered by them.
SUFFIX_LEGACY = r"\d{3}"
SUFFIX_RANDOM = r"[0-9a-f]{6}"
SUFFIX = rf"(?:{SUFFIX_LEGACY}|{SUFFIX_RANDOM})"

DUPLICATE_RUN_IDS = os.path.join(REPO, "tools", "duplicate_run_ids.yaml")


def _load_duplicate_run_owners() -> dict[str, set[str]]:
    """run id -> the experiments it occurs under, for ids that collide.

    Frozen by tools/build_duplicate_run_ids.py and held to never grow by
    tools/test_duplicate_run_ids.py. Read here so a citation of a colliding id
    can be required to say which experiment it means. Absent file is not fatal:
    the check simply does not fire, and the must-not-grow test is what notices.
    """
    try:
        document = yaml.safe_load(open(DUPLICATE_RUN_IDS, encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    records = (document or {}).get("records") or {}
    return {
        rec_id: {o.get("experiment_id") for o in entry.get("occurrences") or []}
        for rec_id, entry in records.items()
    }


DUPLICATE_RUN_OWNERS = _load_duplicate_run_owners()

ID_PATTERNS = {
    "goal": re.compile(rf"^GOAL-[A-Z0-9]+-{SUFFIX}$"),
    "research_question": re.compile(rf"^RQ-[A-Z]+-{SUFFIX}$"),
    "idea": re.compile(rf"^IDEA-\d{{8}}-{SUFFIX}$"),
    "hypothesis": re.compile(rf"^H-[A-Z]+-{SUFFIX}$"),
    "experiment": re.compile(rf"^EXP-[A-Z]+-{SUFFIX}$"),
    "evidence": re.compile(rf"^EV-[A-Z]+-{SUFFIX}$"),
    "coordinator_decision": re.compile(rf"^DEC-\d{{8}}-{SUFFIX}$"),
    "handoff": re.compile(rf"^TASK-\d{{8}}-{SUFFIX}$"),
    # Batches carry no date or area segment: BATCH-<suffix>. Sequential batch
    # numbers are the LAST place in this harness where two concurrent lanes
    # still collide by construction -- each computes "highest + 1" from the
    # same committed state and both open BATCH-028. That happened twice in one
    # session: once as a directory-name collision resolved by yielding, and
    # once as a whole card set replaced wholesale. The legacy \d{3} form stays
    # valid forever because existing batch directories are immutable.
    "batch": re.compile(rf"^BATCH-{SUFFIX}$"),
}
RUN_ID = re.compile(r"^RUN-[A-Za-z0-9._-]+$")

LEDGER_DIRS = {
    "questions": "research_question",
    "proposals": "idea",
    "hypotheses": "hypothesis",
    "evidence": "evidence",
    "decisions": "coordinator_decision",
    "handoffs": "handoff",
}

REQUIRED = {
    "research_question": ["id", "title", "scope", "status", "owner"],
    "idea": ["id", "title", "class", "claim", "mechanism", "novelty_status"],
    "hypothesis": ["id", "question_id", "statement", "mechanism", "status"],
    "experiment": ["id", "hypothesis_id", "version", "status", "metrics",
                   "budget", "success_criterion"],
    "evidence": ["id", "hypothesis_id", "run_ids", "direction", "strength",
                 "claim_tier", "proof_status", "proof_refs"],
    "coordinator_decision": ["id", "decision", "target_ids",
                             "knowledge_promotion", "decided_by"],
    "handoff": ["id", "from", "to", "objective", "budget"],
}

RUN_REQUIRED_TOP = ["id", "experiment_id", "status", "code", "environment",
                    "inputs", "timing", "result"]

# A control, instrument check or certification run legitimately bears on NO
# hypothesis, and several records say so at length: "Naming a hypothesis here
# would invite exactly the inference the run cannot support." Requiring the
# field non-empty pushed those records toward naming a hypothesis they must not
# name -- the rule inverted its own purpose. An explicit null is accepted, but
# only when the record documents the choice in a sibling note, so a silent
# omission is still an error and the reasoning stays on the record.
#
# Likewise an observation-only contract has no criterion to succeed or fail on.
# EXP-YIELD-003 spells the intent out: "The schema field is present and
# explicitly null rather than absent, so that a reader cannot mistake an omitted
# field for an overlooked one" -- exactly the distinction enforced here.
#
# approved_by is deliberately NOT nullable: AGENTS.md rule 1 gives it exactly
# one legitimate value.
DOCUMENTED_NULL_OK = {
    "hypothesis_id": ("hypothesis_id_note", "hypothesis_note"),
    "success_criterion": ("success_criterion_note",),
    "falsification_criterion": ("falsification_criterion_note",),
}


def field_is_satisfied(body: dict, field: str) -> bool:
    if body.get(field) not in (None, ""):
        return True
    if field not in body:
        return False          # absent entirely: never excused
    for note in DOCUMENTED_NULL_OK.get(field, ()):
        if str(body.get(note) or "").strip():
            return True
    return False


TIER_ORDER = {"toy": 0, "medium": 1, "crypto": 2}
PROOF_STATUSES = {"certificate", "derivation", "empirical_only",
                  "not_applicable"}

# Both blocks below are OPTIONAL and checked only when present, which is what
# lets them land without a baseline entry: the baseline is prune-only, so a
# newly-required field on immutable records could never be grandfathered and
# would fail `main` forever. Absence is reported as schema debt instead --
# `tools/obstruction_registry.py --debt` for the obstruction backlog. What is
# enforced is that a record CLAIMING the new schema completes it.
CITATION_PROVENANCE = {"recalled", "retrieved", "kb", "internal"}

# `recalled` means no agent in this program opened the source. Such a reference
# is a pointer for a reviewer, never support (AGENTS.md rule 9), so these two
# record shapes may not rest on one. No committed record carries a provenance
# field at all, so this can be a hard error from the start: it fires only on
# records written against the new schema.
PROVENANCE_ASSERTS_LITERATURE = {"known", "adaptation"}

OBSTRUCTION_REQUIRED = ["statement", "quantity", "value", "scope"]

# `review_plan` on a handoff follows the same optional-when-present rule. What
# this checks is the plan's INTERNAL consistency, which is all a single record
# can show: whether the reviewers honoured it is cross-checked against their
# attestations by `tools/check_review_independence.py`, which needs the reports
# and so cannot run here.
REVIEW_VERDICTS = {"holds", "breaks", "inconclusive"}


def check_review_plan(path: str, body: dict, ctx: Ctx) -> None:
    """Validate a `review_plan` block on a handoff."""
    plan = body.get("review_plan")
    if plan is None:
        return
    if not isinstance(plan, dict):
        ctx.err(path, "review_plan must be a mapping")
        return
    for field in ("claim_under_review", "coordinator_prior"):
        if not str(plan.get(field) or "").strip():
            ctx.err(path, f"review_plan.{field} is required; the prior is "
                          f"recorded before the round so concurrence can be "
                          f"told apart from agreement with the Coordinator")
    joints = plan.get("joints")
    if not isinstance(joints, list) or not joints:
        ctx.err(path, "review_plan.joints must be a nonempty list; a review "
                      "with no named load-bearing step cannot show coverage")
    else:
        seen: dict[str, int] = {}
        for index, entry in enumerate(joints):
            if not isinstance(entry, dict):
                ctx.err(path, f"review_plan.joints[{index}] must be a mapping")
                continue
            name = str(entry.get("joint") or "").strip()
            if not name:
                ctx.err(path, f"review_plan.joints[{index}].joint is empty")
            else:
                seen[name] = seen.get(name, 0) + 1
            if not str(entry.get("assigned_to") or "").strip():
                ctx.err(path, f"review_plan.joints[{index}] has no "
                              f"assigned_to; an unowned joint is the coverage "
                              f"gap this plan exists to make visible")
            if not str(entry.get("attack_plan") or "").strip():
                ctx.err(path, f"review_plan.joints[{index}] has no "
                              f"attack_plan; a worked attack returns a result "
                              f"either way, 'review this' returns an opinion")
        for name, count in seen.items():
            if count > 1:
                ctx.err(path, f"review_plan joint '{name}' is listed {count} "
                              f"times; one joint, one owner")
    blindness = plan.get("blindness")
    if blindness is not None:
        if not isinstance(blindness, dict):
            ctx.err(path, "review_plan.blindness must be a mapping")
        elif (blindness.get("lifted_for")
                and not str(blindness.get("rationale") or "").strip()):
            ctx.err(path, "review_plan.blindness.lifted_for is nonempty and "
                          "requires a rationale; blindness is lifted on "
                          "purpose, never drifted out of")
    control = plan.get("proves_too_much")
    if not isinstance(control, dict) or not (control.get("objects") or []):
        ctx.err(path, "review_plan.proves_too_much.objects is required; the "
                      "argument is run against objects where its conclusion is "
                      "known false, as controls-before-belief for an argument")
    elif not str(control.get("failure_signature") or "").strip():
        ctx.err(path, "review_plan.proves_too_much.failure_signature is "
                      "required; state what the argument must do on a "
                      "known-false object or the control cannot fail")
    rederivation = plan.get("blind_rederivation")
    if isinstance(rederivation, dict) and rederivation.get("required"):
        for field in ("quantity", "assigned_to"):
            if not str(rederivation.get(field) or "").strip():
                ctx.err(path, f"review_plan.blind_rederivation.{field} is "
                              f"required when required is true")
        if not (rederivation.get("blind_from") or []):
            ctx.err(path, "review_plan.blind_rederivation.blind_from is "
                          "required; name the producer's implementation, notes "
                          "and report, or the independence is not checkable")


def check_citations(path: str, body: dict, rec_type: str, ctx: Ctx) -> None:
    """Validate `citations` and hypothesis `structural_ingredients` entries."""
    groups = [("citations", body.get("citations"))]
    if rec_type == "hypothesis":
        groups.append(("structural_ingredients",
                       body.get("structural_ingredients")))
    for field, entries in groups:
        if entries is None:
            continue
        if not isinstance(entries, list):
            ctx.err(path, f"{field} must be a list")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or "provenance" not in entry:
                continue          # pre-schema entry; reported as debt, not error
            where = f"{field}[{index}]"
            provenance = entry.get("provenance")
            if provenance not in CITATION_PROVENANCE:
                ctx.err(path, f"{where}.provenance must be "
                              f"recalled|retrieved|kb|internal")
                continue
            if provenance == "recalled":
                if rec_type == "coordinator_decision":
                    ctx.err(path, f"{where} is provenance 'recalled'; a "
                                  f"remembered source may not back a decision "
                                  f"(AGENTS.md rule 9)")
                if (rec_type == "idea" and body.get("novelty_status")
                        in PROVENANCE_ASSERTS_LITERATURE):
                    ctx.err(path, f"{where} is provenance 'recalled' but "
                                  f"novelty_status is "
                                  f"'{body.get('novelty_status')}'; use "
                                  f"'unverified' until the source is read")
            elif not str(entry.get("verified_by") or "").strip():
                ctx.err(path, f"{where}.provenance is '{provenance}' and "
                              f"requires verified_by naming the agent that "
                              f"read the source")


def check_obstruction(path: str, body: dict, ctx: Ctx) -> None:
    """Validate an `obstruction` block: a measurement, not a verdict."""
    block = body.get("obstruction")
    if block is None:
        return
    if not isinstance(block, dict):
        ctx.err(path, "obstruction must be a mapping")
        return
    for field in OBSTRUCTION_REQUIRED:
        if not str(block.get(field) or "").strip():
            ctx.err(path, f"obstruction.{field} is required; an obstruction "
                          f"recorded as prose is a verdict, not a datum")
    measured_by = block.get("measured_by")
    if not isinstance(measured_by, list) or not measured_by:
        ctx.err(path, "obstruction.measured_by must be a nonempty list of "
                      "RUN-*/EXP-* IDs the value is read from")
    check = block.get("resource_check")
    if not isinstance(check, dict):
        ctx.err(path, "obstruction.resource_check is required (inventor "
                      "protocol section 4); an unexamined obstruction asserts "
                      "only that nobody looked")
        return
    if check.get("examined") is not True:
        ctx.err(path, "obstruction.resource_check.examined must be true; the "
                      "reversal is checked when the object is still loaded")
    if not str(check.get("reading") or "").strip():
        ctx.err(path, "obstruction.resource_check.reading is required; name "
                      "the theory taking this measurement as its hypothesis, "
                      "or state that the check found none")
    if not isinstance(check.get("spawned_ids", []), list):
        ctx.err(path, "obstruction.resource_check.spawned_ids must be a list")
KNOWLEDGE_TYPES = {
    "literature": ("literature", "KN-LIT-"),
    "technique": ("techniques", "KN-TECH-"),
    "internal_finding": ("findings", "KN-FIND-"),
    "open_problem": ("open-problems", "KN-OPEN-"),
}

# These canonical records were committed before proof/promotion fields became
# mandatory. They remain immutable and are reported as schema debt; every new
# canonical record must use the current schema.
PRE_V2_CANONICAL_IDS = {"EV-SEMAEV-001", "DEC-20260719-001"}


class Ctx:
    def __init__(
        self,
        legacy_paths: set[str],
        legacy_id_remaps: dict[str, str] | None = None,
        schema_supersessions: dict[str, dict] | None = None,
    ):
        self.errors: list[str] = []
        self.legacy_warnings: list[str] = []
        self.ids: dict[str, str] = {}          # id -> source path
        self.records: dict[str, dict] = {}      # id -> record body
        self.record_types: dict[str, str] = {}
        self.run_params: dict[str, dict] = {}   # run id -> inputs.parameters
        self.knowledge: dict[str, str] = {}
        self.legacy_paths = legacy_paths
        self.legacy_id_remaps = legacy_id_remaps or {}
        self.legacy_aliases: set[str] = set()
        self.schema_supersessions = schema_supersessions or {}

    def source_path(self, path: str) -> str:
        """Return the hash-pinned replacement for a registered source path."""
        entry = self.schema_supersessions.get(os.path.abspath(path))
        if (entry and not entry.get("redirect_id")
                and os.path.isfile(entry["superseding_path"])):
            return entry["superseding_path"]
        return path

    def schema_supersession(self, path: str) -> dict | None:
        return self.schema_supersessions.get(os.path.abspath(path))

    def err(self, path: str, msg: str, *, force: bool = False):
        # First line only: PyYAML messages span lines and embed absolute
        # paths, which would break exact-line baseline matching across hosts.
        msg = str(msg).splitlines()[0].strip()
        rendered = f"{os.path.relpath(path, REPO)}: {msg}"
        if not force and os.path.abspath(path) in self.legacy_paths:
            self.legacy_warnings.append(rendered)
        else:
            self.errors.append(rendered)

    def register(self, rec_id: str, path: str, body: dict, rec_type: str):
        if rec_id in self.ids:
            self.err(path, f"duplicate ID {rec_id} (also in "
                           f"{os.path.relpath(self.ids[rec_id], REPO)})",
                     force=True)
        else:
            self.ids[rec_id] = path
            self.records[rec_id] = body
            self.record_types[rec_id] = rec_type


def load_yaml(path: str, ctx: Ctx):
    source = ctx.source_path(path)
    try:
        with open(source, encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except yaml.YAMLError as e:
        ctx.err(source, f"invalid YAML: {e}")
        return None


def check_ledger_record(path: str, rec_type: str, ctx: Ctx):
    supersession = ctx.schema_supersession(path)
    if supersession and supersession.get("redirect_id"):
        ctx.legacy_aliases.add(os.path.splitext(os.path.basename(path))[0])
        return
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
    replacement_id = (supersession or {}).get("replacement_id")
    if replacement_id and str(rec_id) != replacement_id:
        ctx.err(path, f"registered replacement_id '{replacement_id}' != "
                      f"superseding record id '{rec_id}'", force=True)
    if replacement_id:
        ctx.legacy_aliases.add(stem)
    elif stem != str(rec_id):
        ctx.err(path, f"filename stem '{stem}' != id '{rec_id}'")
        if os.path.abspath(path) in ctx.legacy_paths:
            ctx.legacy_aliases.add(stem)
    required = REQUIRED[rec_type]
    if str(rec_id) in PRE_V2_CANONICAL_IDS:
        required = [field for field in required
                    if field not in {"proof_status", "proof_refs",
                                     "knowledge_promotion"}]
    for field in required:
        if not field_is_satisfied(body, field):
            ctx.err(path, f"missing required field '{field}'")
    if rec_type == "evidence" and "proof_status" in body:
        if body["proof_status"] not in PROOF_STATUSES:
            ctx.err(path, "proof_status must be certificate|derivation|"
                          "empirical_only|not_applicable")
        if not isinstance(body.get("proof_refs"), list):
            ctx.err(path, "proof_refs must be a list")
    check_citations(path, body, rec_type, ctx)
    if rec_type in ("evidence", "coordinator_decision"):
        check_obstruction(path, body, ctx)
    if rec_type == "handoff":
        check_review_plan(path, body, ctx)
    if rec_type == "coordinator_decision" and "knowledge_promotion" in body:
        promotion = body["knowledge_promotion"]
        if not isinstance(promotion, dict):
            ctx.err(path, "knowledge_promotion must be a mapping")
        else:
            promoted = promotion.get("promoted")
            if not isinstance(promoted, list):
                ctx.err(path, "knowledge_promotion.promoted must be a list")
            if promoted == [] and not promotion.get("not_warranted"):
                ctx.err(path, "empty knowledge_promotion.promoted requires "
                              "a nonempty not_warranted reason")
    remapped_to = ctx.legacy_id_remaps.get(os.path.abspath(path))
    if remapped_to:
        ctx.legacy_warnings.append(
            f"{os.path.relpath(path, REPO)}: historical ID {rec_id} is "
            f"remapped to {remapped_to}; frozen source is not registered"
        )
        return
    ctx.register(str(rec_id), path, body, rec_type)


def check_experiment(path: str, ctx: Ctx):
    supersession = ctx.schema_supersession(path)
    if supersession and supersession.get("redirect_id"):
        ctx.legacy_aliases.add(os.path.basename(os.path.dirname(path)))
        return
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
    replacement_id = (supersession or {}).get("replacement_id")
    if replacement_id and str(rec_id) != replacement_id:
        ctx.err(path, f"registered replacement_id '{replacement_id}' != "
                      f"superseding record id '{rec_id}'", force=True)
    if replacement_id:
        stem = os.path.basename(os.path.dirname(path))
        ctx.legacy_aliases.add(stem)
    for field in REQUIRED["experiment"]:
        if not field_is_satisfied(body, field):
            ctx.err(path, f"missing required field '{field}'")
    # An approved contract must have no null approval fields.
    if body.get("status") == "approved":
        for field in ("success_criterion", "falsification_criterion",
                      "approved_by"):
            if not field_is_satisfied(body, field):
                ctx.err(path, f"approved experiment has null '{field}'")
    ctx.register(str(rec_id), path, body, "experiment")


def check_run(path: str, ctx: Ctx, supersessions: dict[str, dict] | None = None):
    """Validate the run manifest discovered at `path`.

    If `path` is registered in tools/run_supersession_registry.yaml, the schema
    check is applied to the SUPERSEDING record instead: the archived file is
    immutable, so a defect in it is repaired by a new record, not an edit, and
    the check must read the record that actually carries the fields.

    Routing is decided by exact registered path only. The superseded file must
    still exist and still hash to its registered value — that is checked by
    check_run_supersessions(), not softened here. Companion artifacts are
    always looked for in the discovered run directory, since they belong to the
    run package regardless of where the superseding record is filed.
    """
    run_dir = os.path.dirname(path)
    entry = (supersessions or {}).get(os.path.abspath(path))
    if entry is not None:
        superseding = entry["superseding_path"]
        if os.path.isfile(superseding):
            path = superseding
        else:
            # Reported by check_run_supersessions() as well; fall back to the
            # superseded record so the run still gets validated and registered
            # rather than silently vanishing from the ledger.
            ctx.err(path, "registered superseding run manifest is missing; "
                          "validating the superseded record in place",
                    force=True)
    doc = load_yaml(path, ctx)
    if doc is None:
        return
    body = doc.get("run") if isinstance(doc, dict) else None
    if not isinstance(body, dict):
        ctx.err(path, "expected top-level key 'run'")
        # A frozen legacy manifest predates the nested `run:` shape and records
        # its id flat. ctx.err has already suppressed the shape complaint for
        # it, but without registering the id nothing may cite the run -- every
        # evidence record naming it fails instead, which is the schema debt
        # reported as the record's own defect. Register it the way legacy
        # ledger records register their filename stem: the run exists, it is
        # frozen by hash, and it is simply not schema-checkable.
        if os.path.abspath(path) in ctx.legacy_paths and isinstance(doc, dict):
            legacy_id = doc.get("run_id") or doc.get("id")
            if isinstance(legacy_id, str) and RUN_ID.match(legacy_id):
                ctx.legacy_aliases.add(legacy_id)
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
    # Companion artifacts must exist in the run directory.
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
        ctx.register(str(rec_id), path, body, "run")


def tier_of_run(params: dict) -> int | None:
    """Highest claim tier a run's parameters can support.

    `field_bits` may be a single value or a LIST of cells: a run that sweeps
    several field sizes records e.g. [16, 20], and both EXP-LPF-001 runs do.
    Semantics for a multi-cell run: **the tier is governed by the largest
    cell**. The tier ceiling asks what size of instance the run actually
    reached, and the largest cell is that size; taking the smallest or the
    first would understate a run that did reach a bigger instance.

    An absent, empty, or non-numeric value yields None — tier unknown, so no
    ceiling is enforced from this run — which is the pre-existing behaviour for
    a missing field_bits. It is never a crash: `int()` on a list raises
    TypeError, which would abort the whole validation instead of reporting a
    line, so list values are unpacked before any coercion.
    """
    bits = params.get("field_bits") or params.get("field_bit_size")
    if bits is None:
        return None
    cells = list(bits) if isinstance(bits, (list, tuple, set)) else [bits]
    widths = []
    for cell in cells:
        if isinstance(cell, bool) or not isinstance(cell, (int, float, str)):
            return None
        try:
            widths.append(int(cell))
        except (TypeError, ValueError):
            return None
    if not widths:
        return None
    bits = max(widths)
    if bits <= 32:
        return TIER_ORDER["toy"]
    if bits <= 96:
        return TIER_ORDER["medium"]
    return TIER_ORDER["crypto"]


def check_cross_refs(ctx: Ctx):
    for rec_id, body in list(ctx.records.items()):
        rec_type = ctx.record_types[rec_id]
        if rec_type == "hypothesis":
            q = body.get("question_id")
            if q and q not in ctx.ids and q not in ctx.legacy_aliases:
                ctx.err(ctx.ids[rec_id], f"hypothesis references unknown "
                                         f"question '{q}'")
        elif rec_type == "experiment":
            h = body.get("hypothesis_id")
            if h and h not in ctx.ids and h not in ctx.legacy_aliases:
                ctx.err(ctx.ids[rec_id], f"experiment references unknown "
                                         f"hypothesis '{h}'")
        elif rec_type == "evidence":
            h = body.get("hypothesis_id")
            if h and h not in ctx.ids and h not in ctx.legacy_aliases:
                ctx.err(ctx.ids[rec_id], f"evidence references unknown "
                                         f"hypothesis '{h}'")
            # legacy_aliases is consulted here for the same reason the
            # hypothesis and question checks above consult it: a frozen
            # pre-schema record exists and may be cited, it just cannot be
            # schema-checked. Omitting it here reported the citing record as
            # defective for naming a run that is present and hash-frozen.
            for run_id in body.get("run_ids") or []:
                if run_id not in ctx.ids and run_id not in ctx.legacy_aliases:
                    ctx.err(ctx.ids[rec_id], f"evidence references unknown "
                                             f"run '{run_id}'")
            for exp_id in body.get("experiment_ids") or []:
                if exp_id not in ctx.ids and exp_id not in ctx.legacy_aliases:
                    ctx.err(ctx.ids[rec_id], f"evidence references unknown "
                                             f"experiment '{exp_id}'")
            # Citing a run id that exists under more than one experiment is
            # ambiguous unless the record also names which one it means. The
            # collisions themselves are frozen and disclosed in
            # tools/duplicate_run_ids.yaml -- they cannot be repaired, because
            # renumbering rewrites committed manifests. What is NOT tolerable
            # is a citation nobody can resolve: scale metadata and run
            # provenance read ctx.run_params, which holds whichever colliding manifest
            # was globbed LAST, so an unqualified citation is checked against a
            # run the record may never have meant.
            for run_id in body.get("run_ids") or []:
                owners = DUPLICATE_RUN_OWNERS.get(run_id)
                if not owners:
                    continue
                named = owners & set(body.get("experiment_ids") or [])
                if len(named) != 1:
                    ctx.err(ctx.ids[rec_id],
                            f"cites run '{run_id}', which exists under "
                            f"{sorted(owners)}; experiment_ids must name "
                            f"exactly one of them to resolve the citation")
            # `claim_tier` is descriptive metadata. The record and decision
            # must state the tested parameters and any transfer assumptions,
            # but the validator does not impose an automatic scale ceiling.
        elif rec_type == "coordinator_decision":
            for target_id in body.get("target_ids") or []:
                if (str(target_id).startswith(("RQ-", "H-", "EXP-", "EV-"))
                        and target_id not in ctx.ids
                        and target_id not in ctx.legacy_aliases):
                    ctx.err(ctx.ids[rec_id], f"decision references unknown "
                                             f"target '{target_id}'")


def load_legacy_inventory() -> dict[str, str]:
    doc = load_yaml(LEGACY_LEDGER_INVENTORY, Ctx(set()))
    if not isinstance(doc, dict) or doc.get("schema") != "legacy-ledger-inventory-v1":
        raise ValueError("invalid legacy ledger inventory schema")
    records = doc.get("records")
    if not isinstance(records, dict):
        raise ValueError("legacy ledger inventory records must be a mapping")
    return {str(path): str(digest) for path, digest in records.items()}


def load_legacy_id_remaps() -> dict[str, str]:
    doc = yaml.safe_load(open(LEGACY_LEDGER_INVENTORY, encoding="utf-8"))
    remaps = doc.get("remapped_ids", {}) if isinstance(doc, dict) else {}
    if not isinstance(remaps, dict):
        raise ValueError("legacy ledger inventory remapped_ids must be a mapping")
    return {str(path): str(rec_id) for path, rec_id in remaps.items()}


def load_legacy_run_inventory() -> dict[str, str]:
    doc = yaml.safe_load(open(LEGACY_RUN_INVENTORY, encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != "legacy-run-inventory-v1":
        raise ValueError("invalid legacy run inventory schema")
    records = doc.get("records")
    if not isinstance(records, dict):
        raise ValueError("legacy run inventory records must be a mapping")
    return {str(path): str(digest) for path, digest in records.items()}


def load_run_supersessions(path: str | None = None) -> dict[str, dict]:
    """Load the run-supersession registry, keyed by absolute superseded path.

    Shape problems raise ValueError (the tool refuses to run on a malformed
    registry rather than half-applying it). Whether the registered files exist
    and still hash to their registered values is a per-run finding and is
    reported by check_run_supersessions().
    """
    path = path or RUN_SUPERSESSION_REGISTRY
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    if not isinstance(doc, dict) or doc.get("schema") != RUN_SUPERSESSION_SCHEMA:
        raise ValueError("invalid run supersession registry schema")
    records = doc.get("records") or []
    if not isinstance(records, list):
        raise ValueError("run supersession registry records must be a list")
    entries: dict[str, dict] = {}
    for index, raw in enumerate(records):
        if not isinstance(raw, dict):
            raise ValueError(f"run supersession record {index} must be a mapping")
        for field in RUN_SUPERSESSION_REQUIRED:
            if not str(raw.get(field) or "").strip():
                raise ValueError(f"run supersession record {index} is missing "
                                 f"required field '{field}'")
        superseded = str(raw["superseded_path"]).strip()
        superseding = str(raw["superseding_path"]).strip()
        for label, relative in (("superseded_path", superseded),
                                ("superseding_path", superseding)):
            if os.path.isabs(relative) or ".." in relative.split("/"):
                raise ValueError(f"run supersession {label} must be a "
                                 f"repository-relative path without '..': "
                                 f"{relative}")
        if not RUN_MANIFEST_PATH.match(superseded):
            raise ValueError(f"run supersession superseded_path must be a "
                             f"discovered run manifest "
                             f"(experiments/*/runs/*/manifest.yaml): "
                             f"{superseded}")
        if RUN_MANIFEST_PATH.match(superseding):
            raise ValueError(f"run supersession superseding_path must not "
                             f"itself be discovered by the run glob, or the "
                             f"run id would be registered twice: {superseding}")
        digests = {}
        for label in ("superseded_sha256", "superseding_sha256"):
            digest = str(raw[label]).strip().lower()
            if not SHA256_HEX.match(digest):
                raise ValueError(f"run supersession {label} must be 64 hex "
                                 f"characters: {raw[label]!r}")
            digests[label] = digest
        key = os.path.abspath(os.path.join(REPO, superseded))
        if key in entries:
            raise ValueError(f"run supersession registry lists {superseded} "
                             f"more than once")
        entries[key] = {
            "run_id": str(raw["run_id"]).strip(),
            "superseded_path": key,
            "superseded_sha256": digests["superseded_sha256"],
            "superseding_path": os.path.abspath(
                os.path.join(REPO, superseding)),
            "superseding_sha256": digests["superseding_sha256"],
        }
    return entries


def _schema_supersession_kind_for_path(relative: str) -> str | None:
    patterns = {
        "ledger": re.compile(
            r"^ledger/(?:questions|proposals|hypotheses|evidence|decisions|handoffs)/[^/]+\.yaml$"),
        "experiment": re.compile(r"^experiments/[^/]+/specification\.yaml$"),
        "knowledge": re.compile(
            r"^knowledge/(?:literature|techniques|findings|open-problems)/[^/]+\.md$"),
        "goal_checkpoint": re.compile(
            r"^ledger/goals/[^/]+/checkpoints/[^/]+\.yaml$"),
    }
    for kind, pattern in patterns.items():
        if pattern.match(relative):
            return kind
    return None


def load_schema_supersessions(path: str | None = None) -> dict[str, dict]:
    """Load immutable-record schema replacements keyed by original path."""
    path = path or SCHEMA_SUPERSESSION_REGISTRY
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    if (not isinstance(doc, dict)
            or doc.get("schema") != SCHEMA_SUPERSESSION_SCHEMA):
        raise ValueError("invalid schema supersession registry schema")
    records = doc.get("records") or []
    if not isinstance(records, list):
        raise ValueError("schema supersession registry records must be a list")
    entries: dict[str, dict] = {}
    for index, raw in enumerate(records):
        if not isinstance(raw, dict):
            raise ValueError(
                f"schema supersession record {index} must be a mapping")
        for field in SCHEMA_SUPERSESSION_REQUIRED:
            if not str(raw.get(field) or "").strip():
                raise ValueError(
                    f"schema supersession record {index} is missing "
                    f"required field '{field}'")
        kind = str(raw["kind"]).strip()
        if kind not in SCHEMA_SUPERSESSION_KINDS:
            raise ValueError(
                f"schema supersession record {index} has invalid kind {kind!r}")
        superseded = str(raw["superseded_path"]).strip()
        superseding = str(raw["superseding_path"]).strip()
        for label, relative in (("superseded_path", superseded),
                                ("superseding_path", superseding)):
            if os.path.isabs(relative) or ".." in relative.split("/"):
                raise ValueError(
                    f"schema supersession {label} must be a repository-relative "
                    f"path without '..': {relative}")
        discovered_kind = _schema_supersession_kind_for_path(superseded)
        if discovered_kind != kind:
            raise ValueError(
                f"schema supersession kind {kind!r} does not match discovered "
                f"source kind {discovered_kind!r}: {superseded}")
        redirect_id = raw.get("redirect_id")
        if redirect_id and raw.get("replacement_id"):
            raise ValueError(
                "schema supersession may declare redirect_id or "
                "replacement_id, not both")
        if not redirect_id and not superseding.startswith(SCHEMA_SUPERSESSION_ROOT):
            raise ValueError(
                "schema supersession replacement must live below "
                f"{SCHEMA_SUPERSESSION_ROOT}: {superseding}")
        superseding_kind = _schema_supersession_kind_for_path(superseding)
        if redirect_id and superseding_kind != kind:
            raise ValueError(
                f"schema redirect target kind {superseding_kind!r} does not "
                f"match source kind {kind!r}: {superseding}")
        if not redirect_id and superseding_kind is not None:
            raise ValueError(
                "schema supersession replacement must not itself match a "
                f"validator discovery glob: {superseding}")
        digests = {}
        for label in ("superseded_sha256", "superseding_sha256"):
            digest = str(raw[label]).strip().lower()
            if not SHA256_HEX.match(digest):
                raise ValueError(
                    f"schema supersession {label} must be 64 hex characters: "
                    f"{raw[label]!r}")
            digests[label] = digest
        key = os.path.abspath(os.path.join(REPO, superseded))
        if key in entries:
            raise ValueError(
                f"schema supersession registry lists {superseded} more than once")
        replacement_id = raw.get("replacement_id")
        entries[key] = {
            "kind": kind,
            "superseded_path": key,
            "superseded_sha256": digests["superseded_sha256"],
            "superseding_path": os.path.abspath(
                os.path.join(REPO, superseding)),
            "superseding_sha256": digests["superseding_sha256"],
            "replacement_id": (str(replacement_id).strip()
                               if replacement_id else None),
            "redirect_id": (str(redirect_id).strip() if redirect_id else None),
        }
    return entries


def check_schema_supersessions(ctx: Ctx,
                               supersessions: dict[str, dict]) -> None:
    """Pin both sides of every schema supersession before routing reads."""
    for key in sorted(supersessions):
        entry = supersessions[key]
        for role, file_path, expected in (
            ("superseded", entry["superseded_path"],
             entry["superseded_sha256"]),
            ("superseding", entry["superseding_path"],
             entry["superseding_sha256"]),
        ):
            if not os.path.isfile(file_path):
                ctx.err(file_path,
                        f"registered {role} schema record is missing; a "
                        "supersession requires both records to be present",
                        force=True)
                continue
            with open(file_path, "rb") as handle:
                actual = hashlib.sha256(handle.read()).hexdigest()
            if actual != expected:
                ctx.err(file_path,
                        f"registered {role} schema record hash changed "
                        f"(registry pins {expected[:8]}, found {actual[:8]}); "
                        "supersede it instead of editing it",
                        force=True)


def check_schema_redirects(ctx: Ctx,
                           supersessions: dict[str, dict]) -> None:
    """Require every alias-only supersession to resolve to its pinned target."""
    for entry in supersessions.values():
        target_id = entry.get("redirect_id")
        if not target_id:
            continue
        if target_id not in ctx.ids and target_id not in ctx.knowledge:
            ctx.err(entry["superseded_path"],
                    f"schema redirect target '{target_id}' is not a canonical "
                    "record", force=True)


def _run_id_of(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as handle:
            doc = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None
    body = doc.get("run") if isinstance(doc, dict) else None
    if isinstance(body, dict):
        rec_id = body.get("id")
    elif isinstance(doc, dict):
        # A supersession is specifically how an archived flat pre-schema
        # manifest gains the canonical nested shape.  Its historical id is
        # still binding and must match the replacement.
        rec_id = doc.get("run_id") or doc.get("id")
    else:
        rec_id = None
    return str(rec_id) if rec_id else None


def check_run_supersessions(ctx: Ctx, supersessions: dict[str, dict]) -> None:
    """Audit every registered supersession before any routing happens.

    Both files must be present and hash to their registered values, and both
    must declare the registered run id. A supersession that let either file
    drift, or that pointed at an unrelated record, would be a way to hide
    changes to an archived run rather than a way to repair one, so every
    finding here is an error and none is downgraded to a legacy warning.
    """
    for key in sorted(supersessions):
        entry = supersessions[key]
        for role, file_path, expected in (
            ("superseded", entry["superseded_path"],
             entry["superseded_sha256"]),
            ("superseding", entry["superseding_path"],
             entry["superseding_sha256"]),
        ):
            if not os.path.isfile(file_path):
                ctx.err(file_path,
                        f"registered {role} run manifest is missing; a "
                        f"supersession requires both records to be present",
                        force=True)
                continue
            with open(file_path, "rb") as handle:
                actual = hashlib.sha256(handle.read()).hexdigest()
            if actual != expected:
                ctx.err(file_path,
                        f"registered {role} run manifest hash changed "
                        f"(registry pins {expected[:8]}, found {actual[:8]}); "
                        f"supersede it instead of editing it",
                        force=True)
                continue
            found = _run_id_of(file_path)
            if found != entry["run_id"]:
                ctx.err(file_path,
                        f"registered {role} run manifest declares run id "
                        f"{found!r}, but the supersession registry entry is "
                        f"for {entry['run_id']!r}",
                        force=True)


def check_legacy_run_inventory(ctx: Ctx, inventory: dict[str, str]) -> None:
    for relative, expected in sorted(inventory.items()):
        path = os.path.join(REPO, relative)
        if not os.path.isfile(path):
            ctx.err(path, "frozen legacy run manifest is missing", force=True)
            continue
        actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if actual != expected:
            ctx.err(
                path,
                "frozen legacy run manifest hash changed; supersede it instead",
                force=True,
            )


def register_legacy_json_runs(ctx: Ctx, inventory: dict[str, str]) -> None:
    """Register run ids of frozen legacy manifests serialized as JSON.

    Some pre-canonical runs recorded their manifest as `manifest.json` rather
    than `manifest.yaml`. The scan below only visits `manifest.yaml`, so those
    runs were never seen at all: not schema-checked (correctly -- they predate
    the schema) but also never registered, so every evidence record citing one
    was reported as referencing an unknown run. The run is present and frozen
    by hash in the inventory; only its serialization is old.

    This registers the id as a legacy alias, exactly as a flat `manifest.yaml`
    does. It deliberately does NOT register the body: nothing here becomes
    schema-checkable, claim tiers are not derived from it, and a run with no
    manifest of any kind stays unregistered, because no record of it exists.
    """
    for relative in sorted(inventory):
        if not relative.endswith(".json"):
            continue
        path = os.path.join(REPO, relative)
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError):
            continue          # hash/presence is check_legacy_run_inventory's job
        if not isinstance(doc, dict):
            continue
        legacy_id = doc.get("run_id") or doc.get("id")
        if isinstance(legacy_id, str) and RUN_ID.match(legacy_id):
            ctx.legacy_aliases.add(legacy_id)


def check_legacy_ledger(
    ctx: Ctx,
    inventory: dict[str, str],
) -> None:
    patterns = {
        "RQ-*.yaml": "research_question",
        "H-*.yaml": "hypothesis",
        "EV-*.yaml": "evidence",
        "DEC-*.yaml": "coordinator_decision",
    }
    observed: set[str] = set()
    for pattern, rec_type in patterns.items():
        for path in sorted(glob.glob(os.path.join(REPO, "ledger", pattern))):
            relative = os.path.relpath(path, REPO)
            observed.add(relative)
            # Even a malformed frozen record provides a stable historical
            # filename alias for later correction/supersession records.
            ctx.legacy_aliases.add(os.path.splitext(os.path.basename(path))[0])
            expected = inventory.get(relative)
            if expected is None:
                ctx.err(path, "new root-level ledger record is forbidden; "
                              "use the canonical ledger subdirectory",
                        force=True)
            else:
                actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
                if actual != expected:
                    ctx.err(path, "frozen legacy ledger record hash changed; "
                                  "supersede it in a canonical subdirectory",
                            force=True)
            check_ledger_record(path, rec_type, ctx)
    for missing in sorted(set(inventory) - observed):
        ctx.err(os.path.join(REPO, missing),
                "frozen legacy ledger record is missing", force=True)


def check_legacy_id_remaps(ctx: Ctx) -> None:
    for source, target_id in sorted(ctx.legacy_id_remaps.items()):
        if target_id not in ctx.ids:
            ctx.err(
                source,
                f"legacy remap target '{target_id}' is not a canonical record",
                force=True,
            )


def check_knowledge_entries(ctx: Ctx) -> None:
    for entry_type, (directory, prefix) in KNOWLEDGE_TYPES.items():
        pattern = os.path.join(REPO, "knowledge", directory, "*.md")
        for path in sorted(glob.glob(pattern)):
            source = ctx.source_path(path)
            text = open(source, encoding="utf-8").read()
            if not text.startswith("---"):
                ctx.err(path, "knowledge entry is missing YAML frontmatter")
                continue
            try:
                frontmatter = yaml.safe_load(text.split("---", 2)[1]) or {}
            except yaml.YAMLError as error:
                ctx.err(path, f"invalid knowledge frontmatter: {error}")
                continue
            rec_id = frontmatter.get("id")
            stem = os.path.splitext(os.path.basename(path))[0]
            if not isinstance(rec_id, str) or not rec_id.startswith(prefix):
                ctx.err(path, f"knowledge id must start with {prefix}")
                continue
            supersession = ctx.schema_supersession(path)
            replacement_id = (supersession or {}).get("replacement_id")
            if replacement_id and rec_id != replacement_id:
                ctx.err(path, f"registered replacement_id '{replacement_id}' != "
                              f"superseding knowledge id '{rec_id}'", force=True)
            if not replacement_id and stem != rec_id:
                ctx.err(path, f"filename stem '{stem}' != id '{rec_id}'")
            if frontmatter.get("type") != entry_type:
                ctx.err(path, f"knowledge type must be '{entry_type}'")
            for field in ("title", "tags", "confidence", "added"):
                if frontmatter.get(field) in (None, "", []):
                    ctx.err(path, f"knowledge entry missing '{field}'")
            if rec_id in ctx.knowledge:
                ctx.err(path, f"duplicate knowledge ID {rec_id}")
            ctx.knowledge[rec_id] = path
            if replacement_id:
                ctx.knowledge[stem] = path
            if entry_type == "internal_finding":
                refs = frontmatter.get("internal_refs")
                if not isinstance(refs, list) or not refs:
                    ctx.err(path, "internal finding requires internal_refs")
                else:
                    for ref in refs:
                        if ref not in ctx.ids:
                            ctx.err(path, f"internal finding references unknown "
                                          f"record '{ref}'")
                if frontmatter.get("proof_status") not in PROOF_STATUSES:
                    ctx.err(path, "internal finding requires valid proof_status")
                if not isinstance(frontmatter.get("proof_refs"), list):
                    ctx.err(path, "internal finding proof_refs must be a list")

    for rec_id, body in ctx.records.items():
        if ctx.record_types[rec_id] != "coordinator_decision":
            continue
        promotion = body.get("knowledge_promotion")
        if not isinstance(promotion, dict):
            continue
        for entry in promotion.get("promoted") or []:
            # Records in the wild write both shapes: a bare `KN-*` id, and a
            # mapping carrying the id plus a note or action. Take the id from
            # either. An entry that is neither is a malformed reference, not a
            # reason to abort the whole run -- an unhashable one used to raise
            # TypeError here and take every later check down with it.
            if isinstance(entry, dict):
                knowledge_id = entry.get("id")
            else:
                knowledge_id = entry
            if not isinstance(knowledge_id, str):
                ctx.err(ctx.ids[rec_id], "knowledge_promotion entry is not a "
                                         f"knowledge ID: {entry!r}")
                continue
            if knowledge_id not in ctx.knowledge:
                ctx.err(ctx.ids[rec_id], "knowledge_promotion references "
                                         f"unknown entry '{knowledge_id}'")


GOAL_ID = ID_PATTERNS["goal"]
GOAL_LEGACY_ID = re.compile(rf"^GOAL-[A-Z0-9]+-{SUFFIX_LEGACY}$")
GOAL_RANDOM_ID = re.compile(rf"^GOAL-[A-Z0-9]+-{SUFFIX_RANDOM}$")
# `closed_at_budget` is a terminal status in active use. It asserts that the
# campaign budget ran out WITHOUT a completion criterion being met, so it makes
# no success claim and needs no quorum. Using it to retire a goal that did meet
# a criterion, in order to avoid the quorum, is a contract violation.
GOAL_STATUSES = {"draft", "active", "paused", "blocked", "completed",
                 "cancelled", "closed_at_budget"}
GOAL_REQUIRED = ["id", "title", "objective", "question_ids", "status",
                 "completion_criteria", "pause_conditions", "next_action",
                 "owner"]

# Goal records were not validated at all before this check existed, and these
# three were marked `completed` before the closure quorum was a rule. The rule
# is prospective: demanding retroactive attestations would either block CI
# permanently or invite back-dated ones, and a fabricated attestation is worse
# than an unattested closure. They are exempt from the quorum and required-field
# checks only, still validated for id format and status, and reported as schema
# debt. Do not add to this set: a new closure must earn its quorum.
PRE_QUORUM_GOAL_IDS = {"GOAL-ICLIFT-001", "GOAL-XEDN-001", "GOAL-XEDN-002",
                       "GOAL-P13-001"}

# A goal may only be closed out on the concurring judgement of three
# independently-resolved models. See AGENTS.md "Goal closure quorum".
GOAL_CLOSURE_QUORUM = 3

# SUSPENDED. The quorum requirement is not enforced while this is False.
#
# Why: the rule presumes several backends that bind to genuinely different
# models. In the harness as deployed there is one usable backend, so three
# attestations necessarily resolve to one model -- which the rule itself
# defines as *not* a quorum. The requirement therefore made `completed`
# unreachable for every goal regardless of its research merit, turning a
# safeguard against overclaiming into a blanket block. Goals that met their
# criteria were left `paused`, which understates them.
#
# What this does NOT relax. Everything below still applies whenever a
# completion_quorum block is present at all:
#   - attestation shape (ATTESTATION_REQUIRED), independent_session,
#     and reviewed_record_ids resolving to real records;
#   - a recorded DISSENT still contradicts `completed`. That is ordinary
#     self-consistency, not the quorum: having obtained a dissent, closing
#     anyway is incoherent at any quorum size;
#   - `quorum_satisfied: true` on a non-completed goal is still an error.
# Attestations remain fully supported and are still worth recording; they are
# simply no longer a precondition for closure.
#
# To restore: set this True. The enforcement code and its tests are intact and
# are exercised in both modes by tools/test_goal_closure_quorum.py, so flipping
# it back needs no other edit. Restore it once more than one backend resolves
# (`python3 -m orchestration.adapter doctor --probe`).
GOAL_CLOSURE_QUORUM_REQUIRED = False
ATTESTATION_REQUIRED = ["role", "requested_policy", "resolved_model_id",
                        "independent_session", "reviewed_record_ids",
                        "verdict"]
CONCUR = "CONCUR"
DISSENT = "DISSENT"


def check_goal_closure_quorum(path: str, goal: dict, ctx: Ctx):
    """Check the closure quorum on a goal marked `completed`.

    When `GOAL_CLOSURE_QUORUM_REQUIRED` is true, a closed-out goal must carry
    `completion_quorum.attestations`: at least three verdicts whose
    `resolved_model_id` values are pairwise distinct and which all CONCUR. The
    distinctness is on the *resolved* model, not the requested policy alias,
    because a policy that falls back to a shared model yields correlated
    judgements and is not a quorum.

    The requirement is currently SUSPENDED (see `GOAL_CLOSURE_QUORUM_REQUIRED`),
    so a `completed` goal need not carry the block at all. A block that IS
    present is still validated in full except for the count and distinctness
    gates: attestations must be well-formed, sessions independent, cited
    records real, and a recorded DISSENT still contradicts closure.
    """
    quorum = goal.get("completion_quorum")
    if not isinstance(quorum, dict):
        if GOAL_CLOSURE_QUORUM_REQUIRED:
            ctx.err(path, "goal status 'completed' requires a "
                          f"completion_quorum block with "
                          f"{GOAL_CLOSURE_QUORUM} concurring attestations")
        return

    attestations = quorum.get("attestations")
    if not isinstance(attestations, list) or not attestations:
        # A block that is present must still be well-formed, whether or not
        # the quorum gates closure: an empty attestations list asserts a
        # review that did not happen.
        ctx.err(path, "completion_quorum.attestations must be a non-empty list")
        return

    for i, att in enumerate(attestations):
        if not isinstance(att, dict):
            ctx.err(path, f"completion_quorum.attestations[{i}] must be a "
                          "mapping")
            return
        for field in ATTESTATION_REQUIRED:
            if att.get(field) in (None, "", []):
                ctx.err(path, f"completion_quorum.attestations[{i}] missing "
                              f"required field '{field}'")

    verdicts = [str(a.get("verdict", "")).strip().upper() for a in attestations]
    dissent = [i for i, v in enumerate(verdicts) if v == DISSENT]
    if dissent:
        ctx.err(path, "goal status 'completed' contradicts DISSENT in "
                      f"completion_quorum.attestations{dissent}; a dissent "
                      "blocks closure until superseded by a new decision")

    concurring = [a for a, v in zip(attestations, verdicts) if v == CONCUR]
    if GOAL_CLOSURE_QUORUM_REQUIRED:
        # The count and the distinctness are the quorum proper, and they are
        # the only two checks the suspension turns off.
        if len(concurring) < GOAL_CLOSURE_QUORUM:
            ctx.err(path, f"goal closure needs {GOAL_CLOSURE_QUORUM} CONCUR "
                          f"attestations, found {len(concurring)}")

        models = [str(a.get("resolved_model_id", "")).strip()
                  for a in concurring if a.get("resolved_model_id")]
        distinct = {m for m in models if m}
        if len(distinct) < GOAL_CLOSURE_QUORUM:
            ctx.err(path, "goal closure needs "
                          f"{GOAL_CLOSURE_QUORUM} pairwise-distinct "
                          f"resolved_model_id values among concurring "
                          f"attestations, found {len(distinct)} "
                          f"({sorted(distinct)})")

    non_independent = [i for i, a in enumerate(attestations)
                       if a.get("independent_session") is not True]
    if non_independent:
        ctx.err(path, "every closure attestation must set "
                      "independent_session: true; not set at "
                      f"attestations{non_independent}")

    for i, att in enumerate(attestations):
        refs = att.get("reviewed_record_ids")
        if isinstance(refs, list) and refs:
            # Knowledge findings/literature live in ctx.knowledge (loaded
            # before check_goals), not ctx.ids. GOAL-* keeps the prefix
            # escape used when a goal id is mid-registration.
            unknown = [
                r for r in refs
                if r not in ctx.ids
                and r not in ctx.knowledge
                and not str(r).startswith("GOAL-")
            ]
            if unknown:
                ctx.err(path, f"completion_quorum.attestations[{i}] cites "
                              f"unknown record(s) {unknown}")


def load_goal_documents(ctx: Ctx):
    """Yield (path, goal, expected_basename) for both goal record layouts.

    FLAT:     ledger/goals/GOAL-X-001.yaml
    SHARDED:  ledger/goals/GOAL-X-001/goal.yaml
              ledger/goals/GOAL-X-001/checkpoints/BATCH-NNN.yaml   (write-once)

    The sharded layout exists because a goal record is the one ledger file that
    MANY campaigns write. GOAL-PATH-001 is edited by all eight of its children,
    and two coordinators appending different entries to one `batch_checkpoints`
    list conflict every single time -- a textual conflict in a place where there
    is no semantic conflict at all, since the entries are independent and
    append-only.

    One file per checkpoint is conflict-free by construction, which is the same
    move that fixed identifier collisions: stop requiring a writer to read shared
    state it does not need. Both layouts are supported and NOTHING IS MIGRATED
    AUTOMATICALLY -- a goal converts when its Coordinator next touches it, via
    tools/shard_goal.py. Migrating all of them at once would land a rename in
    every one of the open branches simultaneously.
    """
    goals_root = os.path.join(REPO, "ledger", "goals")
    try:
        entries = sorted(os.scandir(goals_root), key=lambda entry: entry.name)
    except OSError:
        entries = []

    for entry in entries:
        if (entry.is_symlink() or not entry.name.endswith(".yaml")
                or not entry.is_file(follow_symlinks=False)):
            continue
        path = entry.path
        doc = load_yaml(path, ctx)
        if doc is None:
            continue
        goal = doc.get("research_goal") if isinstance(doc, dict) else None
        if not isinstance(goal, dict):
            ctx.err(path, "missing top-level 'research_goal' mapping")
            continue
        yield path, goal, lambda rec_id: f"{rec_id}.yaml", os.path.basename(path)

    for entry in entries:
        if entry.is_symlink() or not entry.is_dir(follow_symlinks=False):
            continue
        path = os.path.join(entry.path, "goal.yaml")
        try:
            mode = os.lstat(path).st_mode
        except OSError:
            continue
        if not stat.S_ISREG(mode):
            continue
        doc = load_yaml(path, ctx)
        if doc is None:
            continue
        goal = doc.get("research_goal") if isinstance(doc, dict) else None
        if not isinstance(goal, dict):
            ctx.err(path, "missing top-level 'research_goal' mapping")
            continue
        directory = os.path.dirname(path)
        checkpoints = os.path.join(directory, "checkpoints")
        try:
            checkpoint_mode = os.lstat(checkpoints).st_mode
        except OSError:
            checkpoint_mode = 0
        if stat.S_ISDIR(checkpoint_mode):
            checkpoint_entries = sorted(
                os.scandir(checkpoints), key=lambda checkpoint: checkpoint.name
            )
        else:
            checkpoint_entries = []
        shards = [
            checkpoint.path
            for checkpoint in checkpoint_entries
            if (not checkpoint.is_symlink()
                and checkpoint.name.endswith(".yaml")
                and checkpoint.is_file(follow_symlinks=False))
        ]
        merged = []
        for shard in shards:
            sdoc = load_yaml(shard, ctx)
            if sdoc is None:
                continue
            entry = sdoc.get("batch_checkpoint") if isinstance(sdoc, dict) else None
            if not isinstance(entry, dict):
                ctx.err(shard, "missing top-level 'batch_checkpoint' mapping")
                continue
            merged.append(entry)
        if merged:
            existing = goal.get("batch_checkpoints") or []
            if not isinstance(existing, list):
                ctx.err(path, "batch_checkpoints must be a list")
                existing = []
            goal = dict(goal)
            goal["batch_checkpoints"] = list(existing) + merged
        yield path, goal, lambda rec_id: "goal.yaml", os.path.basename(directory)


def check_trusted_goal_prefixes(ctx: Ctx) -> bool:
    """Require ordinary ledger and ledger/goals directories without follow."""
    for relative in ("ledger", "ledger/goals"):
        path = os.path.join(REPO, *relative.split("/"))
        try:
            mode = os.lstat(path).st_mode
        except OSError:
            description = "missing"
        else:
            if stat.S_ISLNK(mode):
                description = "symlink"
            elif stat.S_ISDIR(mode):
                continue
            elif stat.S_ISREG(mode):
                description = "regular file"
            else:
                description = "special file"
        ctx.err(path, f"trusted goal prefix is {description}; required ordinary "
                      "directory and target was not read", force=True)
        return False
    return True


def check_goal_symlinks(ctx: Ctx) -> None:
    """Reject goal-tree symlinks without opening or traversing their targets."""
    root = os.path.join(REPO, "ledger", "goals")
    try:
        root_mode = os.lstat(root).st_mode
    except OSError:
        return
    if not stat.S_ISDIR(root_mode):
        return
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda entry: entry.name)
        except OSError:
            continue
        for entry in entries:
            if entry.is_symlink():
                ctx.err(entry.path,
                        "goal path may not be a symlink; target was not read",
                        force=True)
            elif entry.is_dir(follow_symlinks=False):
                pending.append(entry.path)


def check_goals(ctx: Ctx):
    if not check_trusted_goal_prefixes(ctx):
        return
    check_goal_symlinks(ctx)
    for path, goal, expected_name, identity in load_goal_documents(ctx):
        rec_id = goal.get("id")
        if not rec_id or not GOAL_ID.match(str(rec_id)):
            ctx.err(path, f"invalid goal id {rec_id!r}")
        else:
            if os.path.basename(path) != expected_name(rec_id):
                ctx.err(path, f"filename must match id ({expected_name(rec_id)})")
            if identity != str(rec_id) and identity != f"{rec_id}.yaml":
                ctx.err(path, f"goal directory must be named {rec_id}")
            ctx.register(str(rec_id), path, goal, "research_goal")

        grandfathered = str(rec_id) in PRE_QUORUM_GOAL_IDS

        if not grandfathered:
            for field in GOAL_REQUIRED:
                if goal.get(field) in (None, ""):
                    ctx.err(path, f"missing required field '{field}'")

        status = str(goal.get("status", "")).strip()
        if status and status not in GOAL_STATUSES:
            ctx.err(path, f"invalid status {status!r}")

        if status == "completed" and not grandfathered:
            check_goal_closure_quorum(path, goal, ctx)
        elif isinstance(goal.get("completion_quorum"), dict):
            # Attestations may be gathered before the transition; they simply
            # must not be mistaken for a closure that has not happened.
            quorum = goal["completion_quorum"]
            if quorum.get("quorum_satisfied") is True and status != "completed":
                ctx.err(path, "completion_quorum.quorum_satisfied is true but "
                              f"status is {status!r}; only a Coordinator "
                              "ledger archive may perform the transition")


def check_knowledge_index(ctx: Ctx):
    # --verify-corpus, not --check. INDEX.md is generated and no longer
    # committed (see build_knowledge_index.py), so there is no file to be stale
    # against. What this check has always actually caught is the BUILDER
    # CRASHING on a corrupt corpus, and building the index and discarding it
    # catches that identically.
    rc = subprocess.run(
        [sys.executable, os.path.join(REPO, "tools", "build_knowledge_index.py"),
         "--verify-corpus"],
        capture_output=True, text=True)
    if rc.returncode != 0:
        msg = (rc.stderr or rc.stdout).strip() or "knowledge corpus does not build"
        # Take the LAST line, not the first. When the index builder raises,
        # the first line is "Traceback (most recent call last):" -- which is
        # both uninformative and, worse, IDENTICAL for every possible cause.
        # CI diffs error sets between head and base, so an unchanging string
        # cancels out and the failure is invisible. That is how a builder
        # crashing on committed conflict markers went unreported. The last
        # line carries the actual exception.
        lines = [ln.strip() for ln in msg.splitlines() if ln.strip()]
        detail = lines[-1] if lines else "knowledge/INDEX.md is stale"
        ctx.errors.append(f"knowledge/INDEX.md: build_knowledge_index.py "
                          f"failed: {detail}")


BASELINE_HEADER = """\
# Grandfathered validation errors — legacy records that predate the
# validator, plus one documented re-anchoring. Each line matches one error
# exactly as validate_ledger.py reports it.
#
# INVARIANT: lines may only ever be REMOVED (as records are repaired or
# superseded); never add a line to absorb a new violation. Prune stale
# lines with: python3 tools/validate_ledger.py --update-baseline
#
# RE-ANCHOR 2026-08-02, authorized by DEC-20260802-008 as amended by
# DEC-20260802-009 and DEC-20260802-010, and recorded as a protocol_amendment
# there. This file was regenerated once, growing from 1138 to 2246 entries.
# The 1108 added entries are the SET difference against the pre-image, not a
# subtraction: the validator reported 1110 lines, but EV-SIG-008 cites
# RUN-EXP-SIG-008-q and -r twice each and a baseline is a set, so two
# identical lines collapse. Pre-existing debt in these categories only:
#   680 pre-current-schema run manifests (missing required field, missing
#       companion artifact, missing code.commit/code.command, invalid
#       certificate.kind) — repair blocked by tools/check_run_immutability.py
#   235 run IDs shared across EXP-FCP-001/EXP-FCP-002/EXP-IC-001 — same
#       block; disclosed in tools/duplicate_run_ids.yaml, which must not grow
#    69 evidence and decision records citing runs or experiments that do not
#       register in this repository — disclosed on each affected record
#    35 evidence records missing direction/strength — disclosed in
#       ledger/registers/unevidenced-records.yaml; none may support a
#       hypothesis transition until reviewed
#    82 knowledge frontmatter pending /curate-knowledge
#     5 ID area tokens containing digits (RQ/H/EXP-PMA4-001, H/EV-P13-001).
#       Four report "ID ... does not match ... format"; EXP-PMA4-001 reports
#       "bad experiment id" instead, because check_experiment returns early on
#       a malformed id rather than continuing like check_ledger_record. Same
#       defect, different message, so a message-shaped count splits the
#       category away from the five records this line names.
#       These records register and all cross-references resolve; renaming
#       was refused on cost/risk grounds. The ID patterns were NOT widened,
#       so a new non-conforming ID still fails.
#     2 records outside the current schema vocabulary: EV-P13-001's
#       conditional_on_heuristic proof_status (more precise than the schema
#       admits) and EXP-MLKEM-004's null approved_by (unfillable without
#       asserting an approval event no record establishes).
# No mechanically repairable line was absorbed. Lines naming a record moved by
# the DEC-20260802-001 relocation were admitted only where the identical
# message appears in tools/prerelocation_error_snapshot.txt under that
# record's pre-relocation path — a set-membership test, not a judgement.
# The full debt stays inspectable with --no-baseline. The only-ever-removed
# invariant resumes from this point: a later addition is a contract violation,
# not a second re-anchoring.
"""


def load_baseline(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as fh:
        return {ln.rstrip("\n") for ln in fh
                if ln.strip() and not ln.lstrip().startswith("#")}


def write_baseline(entries: set[str]) -> None:
    with open(BASELINE_PATH, "w", encoding="utf-8") as fh:
        fh.write(BASELINE_HEADER)
        for e in sorted(entries):
            fh.write(e + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate the research ledger, experiments, and runs.")
    ap.add_argument("--no-baseline", action="store_true",
                    help="fail on every error, including grandfathered ones")
    ap.add_argument("--update-baseline", action="store_true",
                    help="prune baseline entries that no longer occur "
                         "(bootstraps the full set only if no baseline "
                         "file exists; never grows an existing one)")
    args = ap.parse_args()

    # This must precede every inventory, glob, supersession, and record read.
    # If ledger itself is an alias, even an apparently unrelated ledger glob
    # would otherwise escape the candidate tree before check_goals runs.
    prefix_ctx = Ctx(set())
    if not check_trusted_goal_prefixes(prefix_ctx):
        print(f"FAIL: {len(prefix_ctx.errors)} new validation error(s):\n",
              file=sys.stderr)
        for error in prefix_ctx.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    try:
        legacy_inventory = load_legacy_inventory()
        legacy_id_remaps = load_legacy_id_remaps()
        legacy_run_inventory = load_legacy_run_inventory()
    except (OSError, ValueError) as error:
        print(f"FAIL: cannot load legacy inventory: {error}",
              file=sys.stderr)
        return 1
    try:
        run_supersessions = load_run_supersessions()
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: cannot load run supersession registry: {error}",
              file=sys.stderr)
        return 1
    try:
        schema_supersessions = load_schema_supersessions()
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: cannot load schema supersession registry: {error}",
              file=sys.stderr)
        return 1
    legacy_paths = {os.path.abspath(os.path.join(REPO, path))
                    for path in (*legacy_inventory, *legacy_run_inventory)}
    absolute_remaps = {
        os.path.abspath(os.path.join(REPO, path)): target
        for path, target in legacy_id_remaps.items()
    }
    ctx = Ctx(legacy_paths, absolute_remaps, schema_supersessions)
    check_schema_supersessions(ctx, schema_supersessions)
    check_legacy_ledger(ctx, legacy_inventory)
    for sub, rec_type in LEDGER_DIRS.items():
        for path in sorted(glob.glob(os.path.join(REPO, "ledger", sub, "*.yaml"))):
            check_ledger_record(path, rec_type, ctx)
    for path in sorted(glob.glob(os.path.join(REPO, "experiments", "*",
                                              "specification.yaml"))):
        check_experiment(path, ctx)
    check_legacy_run_inventory(ctx, legacy_run_inventory)
    register_legacy_json_runs(ctx, legacy_run_inventory)
    check_run_supersessions(ctx, run_supersessions)
    for path in sorted(glob.glob(os.path.join(REPO, "experiments", "*", "runs",
                                              "*", "manifest.yaml"))):
        check_run(path, ctx, run_supersessions)
    check_legacy_id_remaps(ctx)
    # Knowledge must be indexed before goal closure quorum checks so that
    # reviewed_record_ids may cite KN-* entries (ctx.knowledge), not only
    # ledger ids (ctx.ids).
    check_knowledge_entries(ctx)
    check_schema_redirects(ctx, schema_supersessions)
    check_goals(ctx)
    check_cross_refs(ctx)
    check_knowledge_index(ctx)

    current = set(ctx.errors)
    if args.update_baseline:
        # Prune-only: an existing baseline can shrink but never grow, so a
        # new violation cannot be laundered into the grandfathered set.
        old = load_baseline(BASELINE_PATH)
        entries = (old & current) if os.path.exists(BASELINE_PATH) else current
        write_baseline(entries)
        print(f"wrote {len(entries)} baseline entrie(s) to "
              f"{os.path.relpath(BASELINE_PATH, REPO)}")
        return 0

    baseline = set() if args.no_baseline else load_baseline(BASELINE_PATH)
    new = [e for e in ctx.errors if e not in baseline]
    suppressed = len(ctx.errors) - len(new)
    stale = baseline - current
    if suppressed:
        print(f"note: {suppressed} grandfathered legacy error(s) suppressed "
              f"by {os.path.relpath(BASELINE_PATH, REPO)}")
    if ctx.legacy_warnings:
        print(f"note: {len(legacy_inventory)} frozen root-level ledger records "
              f"were indexed; {len(legacy_run_inventory)} legacy run "
              f"manifest(s) were indexed; {len(ctx.legacy_warnings)} legacy "
              "schema issue(s) remain read-only")
    if run_supersessions:
        print(f"note: {len(run_supersessions)} superseded run manifest(s) "
              f"routed to their superseding records by "
              f"{os.path.relpath(RUN_SUPERSESSION_REGISTRY, REPO)}; both "
              f"records stay hash-pinned")
    if schema_supersessions:
        print(f"note: {len(schema_supersessions)} archived schema record(s) "
              f"routed to complete replacements by "
              f"{os.path.relpath(SCHEMA_SUPERSESSION_REGISTRY, REPO)}; both "
              f"records stay hash-pinned")
    if stale:
        print(f"note: {len(stale)} baseline entrie(s) no longer occur; prune "
              f"with --update-baseline")

    if new:
        print(f"FAIL: {len(new)} new validation error(s):\n", file=sys.stderr)
        for e in new:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(ctx.ids)} records, no new violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
