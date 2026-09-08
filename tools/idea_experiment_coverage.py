#!/usr/bin/env python3
"""Audit explicit idea -> experiment lineage without treating citations as designs.

This is an administrative inventory, not semantic approval or scientific evidence.
All idea statuses and both canonical/legacy ledger layouts remain in the denominator.
Unknown layouts, parse failures and duplicate identities stay visible for review.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
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
        })
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
                           if (a := ecc_priority.area_of(entry["body"].get("question_id", "")))})
        evidence = links.get(iid, [])
        status = ("explicit_experiment_link" if evidence else
                  "hypothesis_only" if hypotheses.get(iid) else
                  "mention_only" if mentions.get(iid) else "no_experiment_link")
        rows.append({"id": iid, "paths": [e["path"] for e in entries],
                     "source_sha256": [e["sha256"] for e in entries],
                     "title": entries[0]["body"].get("title", ""),
                     "source_statuses": sorted({str(e["body"].get("status", "unspecified")) for e in entries}),
                     "recommended_priority": entries[0]["body"].get("recommended_priority"),
                     "areas": area_set, "ecc": bool(set(area_set) & areas),
                     "classification_unresolved": not area_set,
                     "link_status": status, "experiments": evidence,
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
    return {"schema": "crypto.autoresearch.idea_experiment_coverage.v1", "source_commit": commit,
            "scope": "All discovered idea records, every status, canonical and legacy layouts; ECC first.",
            "completion_proven": False,
            "limitations": ["Explicit lineage is necessary bookkeeping, not proof that an experiment tests every source claim.",
                           "Source status/approval markers are not effective approval; additive contracts and archive authority need review.",
                           "Hypotheses alone, citations and arbitrary mentions do not satisfy experiment coverage.",
                           "Duplicates, unknown links, malformed records and unrecognized lineage layouts require reconciliation.",
                           "This inventories the current tree; publication and concurrent-ref authority need separate checks."],
            "counts": {"ideas": len(rows), "ecc_ideas": sum(r["ecc"] for r in rows),
                       "hypotheses": len(records["hypothesis"]), "experiments": len(records["experiment"]),
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
