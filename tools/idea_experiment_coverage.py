#!/usr/bin/env python3
"""Audit explicit idea -> experiment lineage without treating citations as designs.

This is an administrative inventory, not semantic approval or scientific evidence.
All idea statuses, canonical/legacy ledgers, legacy Markdown and archived proposal
lists remain in the denominator. Legacy preflight contracts are separate candidates.
Unknown layouts, parse failures and duplicate identities stay visible for review.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

import yaml

try:
    from . import ecc_priority, validate_ledger
except ImportError:
    import ecc_priority
    import validate_ledger

IDEA_ID = re.compile(r"(?:IDEA-\d{8}-[A-Za-z0-9]{3,8}|[A-Z]+-IDEA-\d+)")
SOURCE_FIELDS = frozenset({
    "idea_id", "idea_ids", "proposal_id", "proposal_ids", "proposal_ref",
    "source_idea", "source_ideas", "source_idea_id", "source_idea_ids",
    "source_proposal", "source_proposal_id", "source_proposal_ids",
    "source_proposal_path", "derived_from_idea", "converts_idea", "parent_idea_id",
})
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
LEGACY_ID_FILE = re.compile(r"([A-Z]+-IDEA-\d+)_.*\.md")


def additional_sources(repo: Path, records: dict, errors: list) -> dict:
    """Inventory archived proposals and legacy contracts without approving them."""
    legacy_contracts = defaultdict(list)
    registry = {}
    index_path = repo / "ideas/idea_registry.tsv"
    if index_path.exists():
        with index_path.open() as stream:
            registry = {r["idea_id"]: r for r in csv.DictReader(stream, delimiter="\t")}
    readme = repo / "ideas/README.md"
    # Classification comes from the declared corpus scope, never the ID prefix.
    corpus_area = "ECDLP" if readme.exists() and (
        "research hypotheses for generic\nprime-field ECDLP" in readme.read_text()) else None
    for folder in ("ideas", "ideas/deferred", "ideas/rejected"):
        for path in sorted((repo / folder).glob("*.md")):
            match = LEGACY_ID_FILE.fullmatch(path.name)
            if not match:
                continue
            iid = match.group(1)
            raw = path.read_bytes()
            text = raw.decode()
            rel = path.relative_to(repo).as_posix()
            heading = re.search(r"^#\s+([^\n]+)", text, re.M)
            if not heading or not re.match(re.escape(iid) + r"(?:\s|$)", heading.group(1)):
                errors.append({"path": rel, "error": "legacy filename/header identity mismatch"})
            state = re.search(r"^- (?:State|Status):\s*`([^`]+)`", text, re.M)
            body = {"id": iid, "title": heading.group(1) if heading else path.stem,
                    "status": state.group(1) if state else registry.get(iid, {}).get("status", "unspecified")}
            records["idea"][iid].append({"path": rel, "sha256": hashlib.sha256(raw).hexdigest(),
                "body": body, "sources": {}, "mentions": [], "effective_path": rel,
                "source_type": "legacy_markdown", "area": corpus_area,
                "classification_source": "ideas/README.md" if corpus_area else None,
                "location": "document", "directory_disposition": folder})
    for path in sorted(set((repo / "coordination").rglob("*.yaml")) |
                       set((repo / "coordination").rglob("*.yml"))):
        if "reviews" in path.relative_to(repo).parts:
            continue  # Review quotations are not originating proposal lists.
        raw = path.read_bytes()
        if not re.search(rb'(?:^|\{)\s*["\']?(?:proposals|ideas)["\']?\s*:', raw, re.M):
            continue
        rel = path.relative_to(repo).as_posix()
        try:
            doc = yaml.load(raw, Loader=LOADER)
            if not isinstance(doc, dict):
                raise ValueError("archived proposal document is not a mapping")
            for field in ("proposals", "ideas"):
                if field not in doc:
                    continue
                if not isinstance(doc[field], list):
                    raise ValueError(f"archived {field} is not a list")
                for index, body in enumerate(doc[field]):
                    if not isinstance(body, dict) or not IDEA_ID.fullmatch(str(body.get("id", ""))):
                        errors.append({"path": rel, "error": f"{field}[{index}] has no recognized idea id"})
                        continue
                    records["idea"][body["id"]].append({"path": rel,
                        "sha256": hashlib.sha256(raw).hexdigest(), "body": body,
                        "sources": explicit_sources(body), "mentions": [], "effective_path": rel,
                        "source_type": "archived_proposal_list", "location": f"{field}[{index}]"})
        except (OSError, ValueError, yaml.YAMLError, UnicodeError) as exc:
            errors.append({"path": rel, "error": str(exc).splitlines()[0]})
    for folder in ("ideas/contracts", "ideas/deferred/contracts", "ideas/rejected/contracts"):
        for path in sorted(set((repo / folder).glob("*.yaml")) | set((repo / folder).glob("*.yml"))):
            rel = path.relative_to(repo).as_posix()
            try:
                raw = path.read_bytes()
                doc = yaml.load(raw, Loader=LOADER)
                body = doc.get("experiment") if isinstance(doc, dict) else None
                if not isinstance(body, dict) or not isinstance(body.get("id"), str):
                    raise ValueError("legacy contract has no experiment mapping/id")
                sources = explicit_sources(body)
                hid = body.get("hypothesis_id")
                if isinstance(hid, str) and IDEA_ID.fullmatch(hid):
                    sources.setdefault(hid, []).append("hypothesis_id (legacy idea reference)")
                if not sources:
                    errors.append({"path": rel, "error": "legacy contract has no explicit idea lineage"})
                for iid, fields in sources.items():
                    legacy_contracts[iid].append({"id": body["id"], "path": rel,
                        "sha256": hashlib.sha256(raw).hexdigest(), "fields": fields,
                        "source_status": body.get("status"), "source_approved_by": body.get("approved_by"),
                        "semantic_coverage": "legacy_candidate_requires_readiness_and_scope_review"})
            except (OSError, ValueError, yaml.YAMLError, UnicodeError) as exc:
                errors.append({"path": rel, "error": str(exc).splitlines()[0]})
    return legacy_contracts


def explicit_sources(body: dict) -> dict[str, list[str]]:
    """Only exact identifiers or exact repository paths in lineage fields count."""
    found = defaultdict(list)
    for field in sorted(SOURCE_FIELDS):
        value = body.get(field)
        for item in value if isinstance(value, list) else [value]:
            if not isinstance(item, str):
                continue
            candidate = item.strip()
            if candidate.startswith(("ledger/proposals/", "ledger/ideas/", "ledger/")):
                candidate = Path(candidate).stem
            elif candidate.startswith("ideas/") and LEGACY_ID_FILE.fullmatch(Path(candidate).name):
                candidate = LEGACY_ID_FILE.fullmatch(Path(candidate).name).group(1)
            if IDEA_ID.fullmatch(candidate):
                found[candidate].append(field)
    return dict(found)


def scan(repo: Path) -> dict:
    repo = repo.resolve()
    records = {kind: defaultdict(list) for kind in ("idea", "hypothesis", "experiment")}
    errors = []
    routed = []
    try:
        registered = validate_ledger.load_schema_supersessions(
            str(repo / "tools/schema_supersession_registry.yaml"))
        registry = {Path(key).relative_to(validate_ledger.REPO).as_posix(): entry
                    for key, entry in registered.items()}
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append({"path": "tools/schema_supersession_registry.yaml", "error": str(exc)})
        registry = {}
    patterns = ("ledger/*.yaml", "ledger/proposals/*.yaml", "ledger/ideas/*.yaml",
                "ledger/hypotheses/*.yaml", "experiments/*/specification.yaml")
    paths = sorted({p for pattern in patterns for p in repo.glob(pattern)})
    for path in paths:
        rel = path.relative_to(repo).as_posix()
        if path.parent == repo / "ledger" and not (
                path.stem.startswith(("IDEA-", "H-")) or "-IDEA-" in path.stem):
            continue
        effective = path
        try:
            raw = path.read_bytes()
            entry = registry.get(rel)
            if entry:
                replacement_rel = Path(entry["superseding_path"]).relative_to(validate_ledger.REPO)
                effective = repo / replacement_rel
                replacement = effective.read_bytes()
                if (hashlib.sha256(raw).hexdigest() != entry["superseded_sha256"] or
                        hashlib.sha256(replacement).hexdigest() != entry["superseding_sha256"]):
                    errors.append({"path": rel, "error": "registered source/replacement hash mismatch"})
                    continue
                routed.append({"path": rel, "effective_path": replacement_rel.as_posix(),
                               "hashes_verified": True, "redirect_id": entry["redirect_id"]})
                if entry["redirect_id"]:
                    continue  # The canonical redirect target is discovered independently.
                raw = replacement
            doc = yaml.load(raw, Loader=LOADER)
        except (OSError, yaml.YAMLError, UnicodeError) as exc:
            errors.append({"path": rel, "error": str(exc).splitlines()[0]})
            continue
        if not isinstance(doc, dict):
            errors.append({"path": rel, "error": "record document is not a mapping"})
            continue
        kind = next((k for k in records if k in doc), None)
        body = doc.get(kind) if kind else None
        if kind is None and rel.startswith(("ledger/proposals/", "ledger/ideas/")):
            kind, body = "idea", doc
        if kind is None and rel.startswith("experiments/"):
            if isinstance(doc.get("id"), str) and doc["id"].startswith("EXP-"):
                kind, body = "experiment", doc
            else:
                errors.append({"path": rel, "error": "unrecognized experiment layout"})
                continue
        if kind is None:
            continue  # Other root-ledger record kinds are outside this census.
        if not isinstance(body, dict) or not isinstance(body.get("id"), str):
            errors.append({"path": rel, "error": f"{kind} has no textual id/mapping"})
            continue
        records[kind][body["id"]].append({
            "path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "body": body,
            "effective_path": effective.relative_to(repo).as_posix(),
            "sources": explicit_sources(body), "mentions": sorted(set(IDEA_ID.findall(raw.decode()))),
            "source_type": "canonical_or_legacy_ledger", "location": "document",
        })
    legacy_contracts = additional_sources(repo, records, errors)
    links = defaultdict(list)
    hypotheses = defaultdict(list)
    mentions = defaultdict(list)
    for hid, entries in records["hypothesis"].items():
        for rec in entries:
            for iid, fields in rec["sources"].items():
                hypotheses[iid].append({"id": hid, "path": rec["path"], "fields": fields})
            for iid in rec["mentions"]:
                mentions[iid].append(rec["path"])
    for eid, entries in records["experiment"].items():
        for rec in entries:
            body = rec["body"]
            origins = defaultdict(list)
            for iid, fields in rec["sources"].items():
                origins[iid].append({"kind": "direct", "path": rec["path"], "fields": fields})
            hid = body.get("hypothesis_id")
            if isinstance(hid, str):
                for hyp in records["hypothesis"].get(hid, []):
                    for iid, fields in hyp["sources"].items():
                        origins[iid].append({"kind": "via_hypothesis", "id": hid,
                                             "path": hyp["path"], "fields": fields})
            for iid, lineage in origins.items():
                links[iid].append({"id": eid, "path": rec["path"], "sha256": rec["sha256"],
                                   "effective_path": rec["effective_path"],
                                   "source_status": body.get("status"),
                                   "source_approved_by": body.get("approved_by"),
                                   "hypothesis_id": hid, "lineage": lineage,
                                   "semantic_coverage": "not_adjudicated_by_this_tool"})
            for iid in rec["mentions"]:
                mentions[iid].append(rec["path"])
    areas = ecc_priority.ecc_areas(ecc_priority.load_policy(repo / "orchestration/research-priority.yaml"))
    rows = []
    for iid, entries in sorted(records["idea"].items()):
        area_set = sorted({a for entry in entries
                           if (a := entry.get("area") or ecc_priority.area_of(
                               entry["body"].get("question_id") or entry["body"].get("goal_id", "")))})
        evidence = links.get(iid, [])
        status = ("explicit_experiment_link" if evidence else
                  "hypothesis_only" if hypotheses.get(iid) else
                  "mention_only" if mentions.get(iid) else "no_experiment_link")
        rows.append({"id": iid, "paths": [e["path"] for e in entries],
                     "source_locations": [{k: e.get(k) for k in
                        ("path", "location", "source_type", "classification_source", "directory_disposition")}
                        for e in entries],
                     "source_sha256": [e["sha256"] for e in entries],
                     "title": entries[0]["body"].get("title", ""),
                     "source_statuses": sorted({str(e["body"].get("status", "unspecified")) for e in entries}),
                     "recommended_priority": entries[0]["body"].get("recommended_priority"),
                     "areas": area_set, "ecc": bool(set(area_set) & areas),
                     "classification_unresolved": not area_set,
                     "link_status": status, "experiments": evidence,
                     "legacy_contract_candidates": legacy_contracts.get(iid, []),
                     "hypotheses": hypotheses.get(iid, []),
                     "mention_paths": sorted(set(mentions.get(iid, [])))})
    rows.sort(key=lambda row: (not row["ecc"], row["link_status"] == "explicit_experiment_link",
                              {"high": 0, "medium": 1, "low": 2}.get(row["recommended_priority"], 3), row["id"]))
    duplicates = [{"kind": kind, "id": rid, "paths": [e["path"] for e in entries]}
                  for kind, index in records.items() for rid, entries in index.items() if len(entries) > 1]
    unknown = [{"id": iid, "experiment_ids": sorted({e["id"] for e in entries})}
               for iid, entries in sorted(links.items()) if iid not in records["idea"]]
    try:
        commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                         text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    counts = Counter(r["link_status"] for r in rows)
    return {"schema": "crypto.autoresearch.idea_experiment_coverage.v2", "source_commit": commit,
            "scope": "All discovered idea records, every status, canonical and legacy layouts; ECC first.",
            "completion_proven": False,
            "limitations": ["Explicit lineage is necessary bookkeeping, not proof that an experiment tests every source claim.",
                           "Source status/approval markers are not effective approval; additive contracts and archive authority need review.",
                           "Hypotheses alone, citations and arbitrary mentions do not satisfy experiment coverage.",
                           "Duplicates, unknown links, malformed records and unrecognized lineage layouts require reconciliation.",
                           "Legacy preflight contracts are inventoried separately and do not establish canonical experiment readiness.",
                           "Discovery covers ledger YAML, identified Markdown under ideas/{,deferred/,rejected/}, and top-level ideas/proposals lists in coordination YAML; unminted prose candidates need separate intake.",
                           "This inventories the current tree; publication and concurrent-ref authority need separate checks."],
            "counts": {"ideas": len(rows), "ecc_ideas": sum(r["ecc"] for r in rows),
                       "hypotheses": len(records["hypothesis"]), "experiments": len(records["experiment"]),
                       "idea_source_types": dict(Counter(e["source_type"] for entries in records["idea"].values() for e in entries)),
                       "ideas_with_legacy_contract_candidates": sum(bool(legacy_contracts.get(r["id"])) for r in rows),
                       "classification_unresolved": sum(r["classification_unresolved"] for r in rows),
                       "link_status": dict(sorted(counts.items())),
                       "ecc_without_explicit_experiment": sum(r["ecc"] and not r["experiments"] for r in rows),
                       "all_without_explicit_experiment": sum(not r["experiments"] for r in rows)},
            "errors": errors, "schema_routing": routed, "duplicate_records": duplicates,
            "unknown_source_ids": unknown, "ideas": rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)
    report = scan(args.repo)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"counts": report["counts"], "parse_errors": len(report["errors"]),
                      "duplicate_records": len(report["duplicate_records"]),
                      "unknown_source_ids": len(report["unknown_source_ids"]), "completion_proven": False}, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
