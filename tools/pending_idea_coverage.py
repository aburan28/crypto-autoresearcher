#!/usr/bin/env python3
"""Source-pinned, read-only discovery of idea/design/task coverage candidates.

This is NOT an approval, readiness, lifecycle, or scientific-evidence checker.
It never labels an absent reference as proof that an idea needs a new design.
All record and policy inputs come from one resolved Git commit, including the
canonical ecc_priority classifier. The only write is an explicitly named, new
JSON report. Example:

    python3 tools/pending_idea_coverage.py --commit HEAD --output /tmp/coverage.json

Missing status, unreadable records, version selection, and queue authority stay
unresolved. Exit 0 means a diagnostic was written, not that coverage passed;
--fail-on-gaps makes disclosed discovery errors return 1. Fatal errors return 2.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import types

import yaml


# Capture generator identity at import, before a potentially long scan. Reading
# __file__ again at report time could bind later edits to earlier executed code.
GENERATOR_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SCHEMA = "crypto.autoresearch.pending_idea_coverage.v1"
QUEUE_SCHEMA = "crypto.autoresearch.dispatch_queue.v1"
POLICY_PATH = "orchestration/research-priority.yaml"
CLASSIFIER_PATH = "tools/ecc_priority.py"
REGISTRY_PATH = "tools/schema_supersession_registry.yaml"
STRUCTURED_SUFFIXES = {".yaml", ".yml", ".json"}
SOURCE_FIELDS = frozenset({
    "derived_from_idea", "derived_from_ideas", "source_idea", "source_ideas",
    "source_idea_id", "source_idea_ids", "source_proposal", "source_proposals",
    "source_proposal_id", "source_proposal_ids", "proposal_id", "proposal_ids",
    "idea_id", "idea_ids", "origin_idea_id", "origin_idea_ids",
})
IDEA_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_-])(?:IDEA-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+|"
    r"[A-Z0-9]+-IDEA-[A-Za-z0-9]+)(?![A-Za-z0-9_-])")
EXP_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_-])EXP-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+(?![A-Za-z0-9_-])")
DOCUMENT_PATH = re.compile(
    r"(?:experiments|ledger|coordination)/[A-Za-z0-9_./+@-]+\.(?:yaml|yml|json)")
SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_path(value: object) -> str | None:
    """Accept a literal repository path; never expand globs or follow symlinks."""
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or any(c in value for c in "*?[]\n\r"):
        return None
    return str(p)


def scalars(value: object, field: str = "", ancestors: frozenset = frozenset()):
    """Walk parsed scalars, tolerating YAML aliases without recursive cycles."""
    if isinstance(value, (dict, list)):
        if id(value) in ancestors:
            return
        ancestors = ancestors | {id(value)}
        items = value.items() if isinstance(value, dict) else enumerate(value)
        for key, child in items:
            yield from scalars(child, f"{field}.{key}" if field else str(key), ancestors)
    elif isinstance(value, str):
        yield field, value


class GitSnapshot:
    """Read immutable blobs by object id; never inspect working-tree records."""

    def __init__(self, repo: Path, commit: str, max_document_bytes: int):
        self.repo = repo.resolve()
        self.repo = Path(self.git("rev-parse", "--show-toplevel").decode().strip())
        self.commit = self.git("rev-parse", "--verify", "--end-of-options", f"{commit}^{{commit}}").decode().strip()
        self.max_document_bytes = max_document_bytes
        self.entries = {}
        for entry in self.git("ls-tree", "-r", "-l", "-z", self.commit).split(b"\0"):
            if not entry:
                continue
            meta, path = entry.split(b"\t", 1)
            mode, kind, oid, size = meta.decode().split()
            self.entries[path.decode("utf-8", "surrogateescape")] = {
                "git_blob_id": oid, "mode": mode, "kind": kind,
                "size_bytes": int(size) if size != "-" else None,
            }
        self.manifest = {}
        self.diagnostics = []
        self._reported = set()
        self._raw = {}
        self._docs = {}
        self.proc = subprocess.Popen(
            ["git", "-C", str(self.repo), "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], stderr=subprocess.PIPE)

    def problem(self, code: str, path: str, detail: str):
        key = (code, path, detail)
        if key not in self._reported:
            self._reported.add(key)
            self.diagnostics.append({"code": code, "path": path, "detail": detail})

    def read(self, path: str, *, cache: bool = True) -> bytes | None:
        if path in self._raw:
            return self._raw[path]
        ent = self.entries.get(path)
        if ent is None:
            self.problem("missing_committed_path", path, "Path is absent from the pinned commit.")
            return None
        item = self.manifest.setdefault(path, {"path": path, **ent, "sha256": None})
        if ent["kind"] != "blob" or ent["mode"] == "120000":
            self.problem("unsupported_git_entry", path, "Not an ordinary blob; no symlink is followed.")
            return None
        if ent["size_bytes"] > self.max_document_bytes:
            self.problem("document_size_limit", path,
                         f"{ent['size_bytes']} bytes exceeds --max-document-bytes={self.max_document_bytes}.")
            return None
        self.proc.stdin.write((ent["git_blob_id"] + "\n").encode())
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().decode().split()
        if len(header) != 3 or header[1] != "blob":
            raise RuntimeError(f"Unexpected git cat-file response for {path}: {header!r}")
        data = self.proc.stdout.read(int(header[2]))
        if len(data) != int(header[2]) or self.proc.stdout.read(1) != b"\n":
            raise RuntimeError(f"Truncated git blob for {path}")
        item["sha256"] = sha256(data)
        if cache:
            self._raw[path] = data
        return data

    def document(self, path: str, *, cache: bool = True):
        if path in self._docs:
            return self._docs[path]
        raw = self.read(path, cache=cache)
        if raw is None:
            return None
        try:
            doc = json.loads(raw) if path.endswith(".json") else yaml.load(raw, Loader=SAFE_LOADER)
        except (ValueError, yaml.YAMLError, UnicodeError, RecursionError) as exc:
            self.manifest[path]["parse_state"] = "error"
            self.problem("parse_error", path, str(exc))
            doc = None
        else:
            self.manifest[path]["parse_state"] = "parsed"
        if cache:
            self._docs[path] = doc
        return doc

    def close(self):
        self.proc.stdin.close()
        self.proc.stdout.close()
        self.proc.wait()
        self.proc.stderr.close()


class Resolver:
    """Hash-checked schema substitutions with explicit original/effective bindings."""

    def __init__(self, snapshot: GitSnapshot):
        self.s = snapshot
        self.entries = {}
        doc = self.s.document(REGISTRY_PATH)
        if not isinstance(doc, dict) or doc.get("schema") != "schema-supersession-registry-v1":
            self.s.problem("invalid_supersession_registry", REGISTRY_PATH, "Expected schema-supersession-registry-v1.")
            return
        records = doc.get("records")
        if not isinstance(records, list):
            self.s.problem("invalid_supersession_registry", REGISTRY_PATH, "records must be a list.")
            return
        for index, entry in enumerate(records):
            if not isinstance(entry, dict):
                self.s.problem("invalid_supersession_entry", REGISTRY_PATH, f"Entry {index} is not a mapping.")
                continue
            src = relative_path(entry.get("superseded_path"))
            dst = relative_path(entry.get("superseding_path"))
            if not src or not dst or src in self.entries:
                self.s.problem("invalid_supersession_entry", REGISTRY_PATH, f"Entry {index}: invalid or duplicate path.")
                continue
            self.entries[src] = {**entry, "superseded_path": src, "superseding_path": dst}

    def resolve(self, original: str, kind: str) -> dict:
        current = original
        chain, seen, aliases = [], set(), set()
        valid = True
        while current in self.entries:
            if current in seen:
                self.s.problem("supersession_cycle", original, current)
                valid = False
                break
            seen.add(current)
            entry = self.entries[current]
            target = entry["superseding_path"]
            before, after = self.s.read(current), self.s.read(target)
            if (before is None or after is None
                    or sha256(before) != entry.get("superseded_sha256")
                    or sha256(after) != entry.get("superseding_sha256")):
                self.s.problem("supersession_hash_mismatch", original, f"Cannot verify {current} -> {target}.")
                valid = False
                break
            expected = entry.get("redirect_id") or entry.get("replacement_id")
            target_doc = self.s.document(target)
            body = target_doc.get(kind) if isinstance(target_doc, dict) else None
            source_doc = self.s.document(current)
            source_body = source_doc.get(kind) if isinstance(source_doc, dict) else None
            previous_id = source_body.get("id") if isinstance(source_body, dict) else None
            if not isinstance(previous_id, str):
                if kind == "experiment" and current.startswith("experiments/"):
                    previous_id = PurePosixPath(current).parts[1]
                elif current.startswith(("ledger/proposals/", "ledger/ideas/", "ledger/hypotheses/")):
                    previous_id = PurePosixPath(current).stem
            if not expected and (not previous_id or not isinstance(body, dict) or body.get("id") != previous_id):
                self.s.problem("unregistered_identity_change", original,
                               "Schema correction without redirect_id/replacement_id must preserve the source identity.")
                valid = False
                break
            if expected and (not isinstance(body, dict) or body.get("id") != expected):
                self.s.problem("supersession_identity_mismatch", original, f"Target does not declare {expected!r}.")
                valid = False
                break
            if entry.get("redirect_id") and entry.get("replacement_id"):
                self.s.problem("invalid_supersession_entry", current, "redirect_id and replacement_id are mutually exclusive.")
                valid = False
                break
            if isinstance(source_body, dict) and isinstance(source_body.get("id"), str):
                aliases.add(source_body["id"])
            # A registered replacement of an unparseable source still binds its
            # legacy path identity. This is an alias, never an invented record.
            if kind == "experiment" and current.startswith("experiments/"):
                aliases.add(PurePosixPath(current).parts[1])
            elif kind != "experiment" and current.startswith(("ledger/proposals/", "ledger/ideas/", "ledger/hypotheses/")):
                aliases.add(PurePosixPath(current).stem)
            chain.append({"original_path": current, "original_sha256": sha256(before),
                          "effective_path": target, "effective_sha256": sha256(after),
                          "redirect_id": entry.get("redirect_id"),
                          "replacement_id": entry.get("replacement_id")})
            current = target
        doc = self.s.document(current)
        body = doc.get(kind) if isinstance(doc, dict) else None
        # Alternate historical protocol documents sometimes omit the wrapper.
        shape = "wrapped"
        if kind == "experiment" and isinstance(doc, dict) and body is None:
            if isinstance(doc.get("id"), str) and doc["id"].startswith("EXP-") and "hypothesis_id" in doc:
                body, shape = doc, "unwrapped_candidate"
        if not isinstance(body, dict):
            self.s.problem("unresolved_record_shape", original, f"Expected a {kind} mapping.")
            valid = False
            body = {}
        identifier = body.get("id")
        if not isinstance(identifier, str) or not identifier:
            self.s.problem("missing_record_identity", original, f"Missing {kind}.id.")
            identifier = None
            valid = False
        if identifier:
            aliases.add(identifier)
        return {"kind": kind, "id": identifier,
                "original_path": original,
                "original_sha256": self.s.manifest.get(original, {}).get("sha256"),
                "effective_path": current,
                "effective_sha256": self.s.manifest.get(current, {}).get("sha256"),
                "aliases": sorted(aliases), "supersession_chain": chain,
                "identity_state": "resolved_candidate" if valid else "unresolved",
                "document_shape": shape, "body": body}


def record_summary(record: dict) -> dict:
    return {k: v for k, v in record.items() if k != "body"}


def identity_index(records: list[dict], s: GitSnapshot) -> dict[str, str]:
    """Only unique, verified aliases enter joins; collisions remain diagnostics."""
    identities = defaultdict(set)
    paths_by_id = defaultdict(set)
    for rec in records:
        if rec["identity_state"] != "resolved_candidate":
            continue
        paths_by_id[rec["id"]].add(rec["effective_path"])
        for alias in rec["aliases"]:
            identities[alias].add(rec["id"])
    for iid, paths in paths_by_id.items():
        # Protocol versions intentionally share one identifier; other records
        # need one effective path, including redirected aliases.
        if len(paths) > 1 and records and records[0]["kind"] != "experiment":
            s.problem("duplicate_effective_identity", iid, "; ".join(sorted(paths)))
            for alias, targets in identities.items():
                if iid in targets:
                    targets.add("<ambiguous>")
    result = {}
    for alias, targets in sorted(identities.items()):
        if len(targets) == 1:
            result[alias] = next(iter(targets))
        else:
            s.problem("ambiguous_identity_alias", alias, "; ".join(sorted(targets)))
    return result


def pinned_classifier(s: GitSnapshot):
    """Use the repository's trusted canonical classifier at the pinned commit.

    Policy data are parsed safely. Executed code is only tools/ecc_priority.py
    from that same explicitly selected repository commit, never record text.
    No default load_policy() call (which would read the live tree) is made.
    """
    policy = s.document(POLICY_PATH)
    code = s.read(CLASSIFIER_PATH)
    if not isinstance(policy, dict) or code is None:
        s.problem("classification_unavailable", POLICY_PATH, "Pinned policy or canonical classifier is unavailable.")
        return lambda _: {"classification": "unclassified", "area": None, "reason": "policy_unavailable"}
    try:
        module = types.ModuleType("_pending_coverage_pinned_ecc_priority")
        module.__file__ = str(s.repo / CLASSIFIER_PATH)
        exec(compile(code, f"{s.commit}:{CLASSIFIER_PATH}", "exec"), module.__dict__)
        included = module.ecc_areas(policy)
        excluded = policy.get("excluded_areas")
        if not isinstance(excluded, dict):
            raise ValueError("excluded_areas must be a mapping")
        if included & set(excluded):
            raise ValueError("ECC inclusions overlap explicit exclusions")
    except Exception as exc:
        s.problem("classification_unavailable", CLASSIFIER_PATH, str(exc))
        return lambda _: {"classification": "unclassified", "area": None, "reason": "classifier_error"}

    def classify(question_id):
        if not isinstance(question_id, str):
            return {"classification": "unclassified", "area": None, "reason": "missing_or_nontext_question_id"}
        area = module.area_of(question_id)
        if area in included:
            label, reason = "ecc", "explicit_ecc_area"
        elif area in excluded:
            label, reason = "non_ecc", "explicit_excluded_area"
        else:
            label, reason = "unclassified", "area_not_classified_by_policy" if area else "identifier_has_no_canonical_area"
        return {"classification": label, "area": area, "reason": reason}
    return classify


def source_links(record: dict, aliases: dict[str, str], proposal_paths: dict[str, str]):
    declared, mentions = [], []
    for field, value in scalars(record["body"]):
        root = field.split(".")[0]
        # Structured source objects support id/ref/path only. A source object's
        # explanatory prose does not acquire a typed edge merely by nesting.
        parts = field.split(".")[1:]
        source_leaf = root in SOURCE_FIELDS and all(p.isdigit() or p in {"id", "ref", "path"} for p in parts)
        target = aliases.get(value) or proposal_paths.get(relative_path(value))
        base = {"record_path": record["effective_path"], "record_id": record["id"],
                "record_kind": record["kind"], "field": field}
        if source_leaf and target:
            declared.append({**base, "idea_id": target, "reference": value,
                             "relation": "declared_source_candidate"})
            continue
        for token in sorted(set(IDEA_TOKEN.findall(value))):
            iid = aliases.get(token)
            if iid is None:
                if source_leaf:
                    mentions.append({**base, "idea_id": None, "reference": token,
                                     "relation": "unresolved_source_reference"})
                continue
            low = (field + " " + value).lower()
            if "out of scope" in low or "forbidden" in low or "separate experiment" in low:
                relation = "lexical_scope_limit_mention"
            elif any(k in field.lower() for k in ("control", "null")):
                relation = "lexical_control_mention"
            elif any(k in field.lower() for k in ("citation", "reference", "source_refs", "history", "baseline")):
                relation = "lexical_reference_mention"
            else:
                relation = "lexical_mention"
            mentions.append({**base, "idea_id": iid, "reference": token, "relation": relation})
    return declared, mentions


def task_summary(queue_path: str, index: int, task: dict) -> dict:
    owned, protocol_paths, ownership_gaps = [], set(), []
    fields = {"write_scope": task.get("write_scope"), "artifact_paths": task.get("artifact_paths")}
    handoff = task.get("handoff")
    if isinstance(handoff, dict):
        fields["handoff.artifact_paths"] = handoff.get("artifact_paths")
    for field, value in fields.items():
        if value is None:
            continue
        if not isinstance(value, list):
            ownership_gaps.append({"field": field, "reason": "Expected a list of literal paths."})
            continue
        for index_in_field, text in enumerate(value):
            leaf = f"{field}.{index_in_field}"
            path = relative_path(text)
            if path is None:
                ownership_gaps.append({"field": leaf, "reason": "Not a literal repository path."})
            if path and len(PurePosixPath(path).parts) >= 2 and path.startswith("experiments/"):
                eid = PurePosixPath(path).parts[1]
                if eid.startswith("EXP-"):
                    owned.append({"experiment_alias": eid, "field": leaf, "path": path})
    mentions = set()
    for _, value in scalars(task):
        mentions.update(EXP_TOKEN.findall(value))
        protocol_paths.update(p for p in DOCUMENT_PATH.findall(value) if p.startswith("experiments/"))
    return {"task_key": f"{queue_path}#{index}", "queue_path": queue_path,
            "task_id": task.get("id"), "role": task.get("role"), "recorded_state": task.get("state"),
            "owned_paths": owned, "mentioned_experiment_aliases": sorted(mentions),
            "ownership_discovery_gaps": ownership_gaps,
            "protocol_document_path_candidates": sorted(protocol_paths),
            "authority_audit": "not_performed", "readiness_audit": "not_performed",
            "completion_verified": False}


def build_inventory(repo: Path, commit: str = "HEAD", max_document_bytes: int = 16 * 1024 * 1024) -> dict:
    if max_document_bytes <= 0:
        raise ValueError("max_document_bytes must be positive")
    s = GitSnapshot(repo, commit, max_document_bytes)
    try:
        resolver = Resolver(s)
        classify = pinned_classifier(s)
        proposal_paths, hypothesis_paths, protocol_paths = [], [], set()
        coordination_paths, authority_paths = [], []
        for path in s.entries:
            p = PurePosixPath(path)
            if p.suffix not in STRUCTURED_SUFFIXES:
                continue
            if path.startswith(("ledger/proposals/", "ledger/ideas/")):
                proposal_paths.append(path)
            elif path.startswith("ledger/hypotheses/"):
                hypothesis_paths.append(path)
            elif path.startswith("experiments/"):
                if len(p.parts) == 3 or "specification" in p.name or p.name == "experiment.yaml":
                    protocol_paths.add(path)
            elif path.startswith("coordination/"):
                coordination_paths.append(path)
            elif path.startswith(("ledger/handoffs/", "ledger/goals/", "ledger/decisions/")):
                authority_paths.append(path)
        ideas = [resolver.resolve(path, "idea") for path in sorted(proposal_paths)]
        hypotheses = [resolver.resolve(path, "hypothesis") for path in sorted(hypothesis_paths)]
        idea_aliases = identity_index(ideas, s)
        hypothesis_aliases = identity_index(hypotheses, s)
        proposal_path_ids = {p: idea_aliases[r["id"]] for r in ideas if r["id"] in idea_aliases
                             for p in (r["original_path"], r["effective_path"])}

        queues, tasks, other_schemas, pointers = [], [], Counter(), []
        for path in sorted(coordination_paths + authority_paths):
            doc = s.document(path, cache=False)
            if not isinstance(doc, dict):
                continue
            for field, value in scalars(doc):
                for target in sorted(set(DOCUMENT_PATH.findall(value))):
                    if target.startswith("experiments/") and target in s.entries:
                        protocol_paths.add(target)
                    if "queue" in field.lower() or "dispatch" in field.lower():
                        pointers.append({"source_path": path, "field": field, "target_path": target,
                                         "authority_audit": "not_performed"})
            schema = doc.get("schema")
            if schema != QUEUE_SCHEMA:
                if isinstance(schema, str):
                    other_schemas[schema] += 1
                continue
            entries = doc.get("tasks")
            queue = {"path": path, "sha256": s.manifest[path]["sha256"], "schema": schema,
                     "authority_audit": "not_performed", "dispatch_validation": "not_performed",
                     "recorded_task_count": len(entries) if isinstance(entries, list) else None}
            queues.append(queue)
            if not isinstance(entries, list):
                s.problem("invalid_queue_shape", path, "Dispatch queue tasks must be a list.")
                continue
            for index, task in enumerate(entries):
                if not isinstance(task, dict):
                    s.problem("invalid_task_shape", path, f"tasks[{index}] is not a mapping.")
                    continue
                summary = task_summary(path, index, task)
                tasks.append(summary)
                for gap in summary["ownership_discovery_gaps"]:
                    s.problem("invalid_task_ownership", path,
                              f"tasks[{index}].{gap['field']}: {gap['reason']}")

        protocols, inspected = [], set()
        # Follow committed protocol/amendment pointers to a fixed point. Merely
        # being a referenced document does not make it a protocol or authority.
        while protocol_paths - inspected:
            path = min(protocol_paths - inspected)
            inspected.add(path)
            doc = s.document(path)
            filename = PurePosixPath(path).name
            expected_protocol = (filename.startswith("specification")
                                 or filename in {"experiment.yaml", "experiment.yml", "experiment.json"}
                                 or path in resolver.entries)
            is_protocol = isinstance(doc, dict) and (isinstance(doc.get("experiment"), dict) or (
                isinstance(doc.get("id"), str) and doc["id"].startswith("EXP-") and "hypothesis_id" in doc))
            if expected_protocol or is_protocol:
                record = resolver.resolve(path, "experiment")
                protocols.append(record)
                doc = s.document(record["effective_path"])
            if not isinstance(doc, dict):
                continue
            for _, value in scalars(doc):
                protocol_paths.update(p for p in DOCUMENT_PATH.findall(value)
                                      if p.startswith("experiments/") and p in s.entries)
        experiment_aliases = identity_index(protocols, s)
        owners = defaultdict(list)
        for task in tasks:
            matches = defaultdict(list)
            for owned in task["owned_paths"]:
                eid = experiment_aliases.get(owned["experiment_alias"])
                if eid:
                    matches[eid].append(owned)
            task["owned_experiment_candidates"] = sorted(matches)
            task["lexical_only_experiment_candidates"] = sorted({experiment_aliases[a]
                for a in task["mentioned_experiment_aliases"] if a in experiment_aliases} - set(matches))
            for eid, paths in sorted(matches.items()):
                owners[eid].append({"task_key": task["task_key"], "queue_path": task["queue_path"],
                                    "task_id": task["task_id"], "role": task["role"],
                                    "ownership_basis": paths, "protocol_version_audit": "not_performed"})

        typed, lexical = [], []
        for record in hypotheses + protocols:
            if record["identity_state"] != "resolved_candidate":
                continue
            declared, mentioned = source_links(record, idea_aliases, proposal_path_ids)
            typed.extend(declared)
            lexical.extend(mentioned)
            for mention in mentioned:
                if mention["relation"] == "unresolved_source_reference":
                    s.problem("unresolved_source_reference", record["effective_path"],
                              f"{mention['field']}: {mention['reference']}")
        typed_by_idea, lexical_by_idea = defaultdict(list), defaultdict(list)
        for edge in typed:
            typed_by_idea[edge["idea_id"]].append(edge)
        for edge in lexical:
            if edge["idea_id"]:
                lexical_by_idea[edge["idea_id"]].append(edge)
        experiments_by_hypothesis = defaultdict(list)
        protocol_summaries = []
        for rec in protocols:
            body = rec["body"]
            hs = body.get("hypothesis_id")
            hs = [hs] if isinstance(hs, str) else hs if isinstance(hs, list) else []
            bindings = [{"reference": h, "canonical_id": hypothesis_aliases.get(h),
                         "state": "resolved_candidate" if h in hypothesis_aliases else "unresolved"}
                        for h in hs if isinstance(h, str)]
            for binding in bindings:
                if binding["state"] == "unresolved":
                    s.problem("unresolved_hypothesis_reference", rec["effective_path"], binding["reference"])
            summary = {**record_summary(rec), "version": body.get("version"),
                       "recorded_status": body.get("status"), "recorded_approved_by": body.get("approved_by"),
                       "hypothesis_bindings": bindings, "version_authority_audit": "not_performed",
                       "approval_audit": "not_performed", "protocol_completeness_audit": "not_performed",
                       "owned_task_candidates": owners.get(rec["id"], []), "completion_verified": False}
            protocol_summaries.append(summary)
            if rec["identity_state"] == "resolved_candidate":
                for binding in bindings:
                    if binding["canonical_id"]:
                        experiments_by_hypothesis[binding["canonical_id"]].append(rec["effective_path"])

        rows = []
        for rec in ideas:
            body, iid = rec["body"], rec["id"]
            sources = typed_by_idea[iid]
            linked_hypotheses = sorted({e["record_id"] for e in sources if e["record_kind"] == "hypothesis"})
            direct = {e["record_path"] for e in sources if e["record_kind"] == "experiment"}
            via_hypothesis = {p for h in linked_hypotheses for p in experiments_by_hypothesis[h]}
            linked_protocols = sorted(direct | via_hypothesis)
            has_status = "status" in body
            lifecycle = ("explicit_proposed_requires_lifecycle_audit" if body.get("status") == "proposed"
                         else "explicit_status_requires_lifecycle_audit" if has_status
                         else "missing_status_requires_lifecycle_audit")
            if rec["identity_state"] == "unresolved":
                coverage = "unresolved_record"
            elif sources:
                coverage = "declared_source_candidates_require_design_audit"
            elif lexical_by_idea[iid]:
                coverage = "lexical_mentions_only_require_source_audit"
            else:
                coverage = "no_source_candidate_found_discovery_and_lifecycle_audit_required"
            rows.append({**record_summary(rec), "title": body.get("title") or body.get("name"),
                         "question_id": body.get("question_id"), "goal_id": body.get("goal_id"),
                         **classify(body.get("question_id")), "status_present": has_status,
                         "recorded_status": body.get("status"), "recorded_disposition": body.get("disposition"),
                         "lifecycle_audit": lifecycle, "coverage": coverage,
                         "declared_source_candidates": sources,
                         "lexical_mentions": lexical_by_idea[iid],
                         "hypothesis_candidates": linked_hypotheses,
                         "protocol_path_candidates": linked_protocols,
                         "protocol_paths_via_hypothesis_candidates": sorted(via_hypothesis - direct),
                         "approval_audit": "not_performed", "archive_audit": "not_performed",
                         "completion_verified": False, "readiness_verified": False})
        rows.sort(key=lambda r: ({"ecc": 0, "non_ecc": 1, "unclassified": 2}[r["classification"]],
                                 r["id"] or "", r["original_path"]))
        return {"schema": SCHEMA, "source_commit": s.commit,
                "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "generator": {"path": "tools/pending_idea_coverage.py", "sha256": GENERATOR_SHA256,
                              "python": sys.version.split()[0], "pyyaml": yaml.__version__},
                "scope": {"proposal_directories": ["ledger/proposals", "ledger/ideas"],
                          "proposal_selection": "All committed structured documents; no status filter.",
                          "queue_discovery": "All committed structured documents under coordination and scanned ledger authority directories; exact schema required.",
                          "protocol_discovery": "Experiment root documents, specification-named documents, and committed experiment document pointers followed to a fixed point.",
                          "classification": "Canonical pinned ecc_priority module plus pinned policy; only explicit exclusions are non_ecc.",
                          "authority": "Unresolved: historical/active queues and protocol versions are not selected.",
                          "max_document_bytes": max_document_bytes},
                "summary": {"proposal_documents": len(rows), "unique_resolved_idea_ids": len({r['id'] for r in rows if r['identity_state'] == 'resolved_candidate'}),
                            "classification_counts": dict(Counter(r["classification"] for r in rows)),
                            "coverage_counts": dict(Counter(r["coverage"] for r in rows)),
                            "explicit_proposed": sum(r["recorded_status"] == "proposed" for r in rows),
                            "status_absent": sum(not r["status_present"] for r in rows),
                            "dispatch_queue_documents": len(queues), "task_documents": len(tasks),
                            "protocol_documents": len(protocols), "diagnostic_count": len(s.diagnostics),
                            "discovery_has_gaps": bool(s.diagnostics), "completion_verified": False, "readiness_verified": False},
                "ideas": rows, "hypotheses": [record_summary(r) for r in hypotheses],
                "protocols": protocol_summaries, "dispatch_queues": queues, "tasks": tasks,
                "non_dispatch_schemas": dict(sorted(other_schemas.items())),
                "queue_pointer_candidates": pointers,
                "unresolved_source_references": [e for e in lexical if e["idea_id"] is None],
                "diagnostics": s.diagnostics, "input_manifest": [s.manifest[p] for p in sorted(s.manifest)],
                "required_next_audits": ["Reconcile lifecycle dispositions and committed decisions.",
                    "Resolve unreadable records and ambiguous identities.", "Audit declared-source and lexical scope associations.",
                    "Select authoritative protocol versions, batches, queues and handoffs.",
                    "Audit protocol completeness, Coordinator approval, dispatch validation, dependencies and claims.",
                    "Verify snapshot/ledger archive receipts and any execution evidence separately."]}
    finally:
        s.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--commit", default="HEAD", help="Git commit/ref resolved once (default: HEAD)")
    parser.add_argument("--output", type=Path, required=True, help="New report path; existing files are never overwritten")
    parser.add_argument("--max-document-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--fail-on-gaps", action="store_true", help="Exit 1 after writing a report with discovery diagnostics")
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise FileExistsError(f"Output already exists: {args.output}")
        report = build_inventory(args.repo, args.commit, args.max_document_bytes)
        serialized = json.dumps(report, indent=2, default=str, ensure_ascii=True) + "\n"
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(serialized)
        print(json.dumps({"output": str(args.output.resolve()), "source_commit": report["source_commit"], **report["summary"]}, indent=2))
        return int(args.fail_on_gaps and report["summary"]["discovery_has_gaps"])
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"pending idea coverage: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
