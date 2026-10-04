"""Read pinned groebner_compare schema-1 summaries. No solver execution."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re

SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
SCOPE = "bounded-Boolean-solver-stage"
NUMBERS = ("total_wall_seconds", "parent_and_reaped_children_cpu_seconds",
           "peak_worker_process_rss_bytes", "verified_relation_rank", "fallback_attempts",
           "attempted_instances", "verified_instances", "verified_witness_instances")


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def _number(value):
    return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None


def _text(value, limit=500):
    return value[:limit] if isinstance(value, str) else ""


def _read(repo, spec, limit=4 * 1024 * 1024):
    if not isinstance(spec, dict) or not SHA.fullmatch(str(spec.get("sha256", ""))):
        raise ValueError("Source SHA-256 is missing or invalid.")
    name = spec.get("path")
    if not isinstance(name, str) or "\\" in name:
        raise ValueError("Source path must be repository-relative.")
    relative = PurePosixPath(name)
    if relative.is_absolute() or not relative.parts or any(p in ("..", ".git") for p in relative.parts):
        raise ValueError("Source path must be repository-relative.")
    path = (repo / name).resolve()
    if not path.is_relative_to(repo.resolve()):
        raise ValueError("Source path leaves the repository.")
    if path.stat().st_size > limit:
        raise ValueError("Source exceeds the size limit.")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError("Source hash does not match its catalog pin.")
    return raw, {"path": relative.as_posix(), "sha256": spec["sha256"]}


def receipt(repo, entry):
    sources = {}
    manifest_raw, sources["manifest"] = _read(repo, entry.get("manifest"))
    summary_raw, sources["summary"] = _read(repo, entry.get("summary"))
    manifest, summary = json.loads(manifest_raw), json.loads(summary_raw)
    if not isinstance(manifest, dict) or not isinstance(summary, dict):
        raise ValueError("Manifest and summary must be objects.")
    if manifest.get("schema") != 1 or summary.get("schema") != 1 or summary.get("scope") != SCOPE:
        raise ValueError("Unsupported receipt schema or scope.")
    manifest_hash = _digest(manifest)
    if summary.get("manifest_sha256") != manifest_hash:
        raise ValueError("Summary is not bound to the supplied manifest.")
    instances, results = manifest.get("instances"), summary.get("results")
    if not isinstance(instances, list) or not instances or not isinstance(results, list):
        raise ValueError("Receipt has no frozen workload or result list.")
    backend = summary.get("backend")
    if not isinstance(backend, dict) or backend not in manifest.get("backends", []):
        raise ValueError("Backend is not in the frozen manifest.")
    complete = len(results) == len(instances)
    counts = Counter()
    for i, row in enumerate(results):
        if (not isinstance(row, dict) or i >= len(instances)
                or row.get("input_sha256") != _digest(instances[i])
                or row.get("instance_id") != instances[i].get("id")):
            raise ValueError("Result identity does not match the frozen workload.")
        status = row.get("status")
        counts[status if status in ("verified", "verified_witness", "unknown") else "unknown"] += 1
    environment = None
    if entry.get("host") is not None:
        host_raw, sources["host"] = _read(repo, entry["host"])
        host = json.loads(host_raw)
        hashes = host.get("source_sha256") if isinstance(host, dict) else None
        if (not isinstance(hashes, dict) or not hashes
                or not all(isinstance(k, str) and isinstance(v, str) and SHA.fullmatch(v)
                           for k, v in hashes.items())
                or host.get("manifest_sha256") != manifest_hash):
            raise ValueError("Host receipt is not bound to the manifest and harness sources.")
        environment = {"python": _text(host.get("python"), 300),
                       "platform": _text(host.get("platform"), 300),
                       "harness_sha256": _digest(hashes)}
    attempt_status = None
    if entry.get("events") is not None:
        event_raw, sources["events"] = _read(repo, entry["events"], 16 * 1024 * 1024)
        attempt_status = dict.fromkeys(("ok", "timeout", "unavailable", "error", "incompatible", "unknown"), 0)
        for line in event_raw.splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("Attempt journal contains a non-object row.")
            if event.get("status") in attempt_status:
                attempt_status[event["status"]] += 1
    metrics = {key: _number(summary.get(key)) for key in NUMBERS}
    # Counts are checked against the receipt's frozen input/result list.
    if (metrics["attempted_instances"] != len(results)
            or metrics["verified_instances"] != counts["verified"]
            or metrics["verified_witness_instances"] != counts["verified_witness"]):
        raise ValueError("Summary counts disagree with its result rows.")
    boundary = _text(summary.get("timing_boundary"), 1000)
    excluded = summary.get("excluded_costs")
    if not isinstance(excluded, list) or not all(isinstance(x, str) for x in excluded):
        excluded = None
    return {"id": entry["id"], "label": _text(entry.get("label"), 120) or entry["id"],
            "scope": SCOPE, "manifest_sha256": manifest_hash,
            "backend": {key: _text(backend.get(key), 100) for key in ("id", "mode")},
            "timing_boundary": boundary, "excluded_costs": excluded,
            "metrics": metrics, "complete": complete,
            "verification": "recorded_verified" if complete and not counts["unknown"] else "incomplete_or_unknown",
            "relation_verification_complete": summary.get("relation_verification_complete") is True,
            "outcomes": dict(counts), "attempt_status": attempt_status,
            "sources": sources, "environment": environment, "fixture": entry.get("fixture") is True}


def payload(repo: Path):
    catalog = repo / "ui" / "receipts.json"
    if not catalog.exists():
        return {"schema": 1, "receipts": [], "errors": []}
    try:
        if catalog.stat().st_size > 131072:
            raise ValueError("Receipt catalog exceeds the size limit.")
        data = json.loads(catalog.read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or data.get("schema") != 1
                or not isinstance(data.get("receipts"), list) or len(data["receipts"]) > 100):
            raise ValueError("Unsupported receipt catalog.")
    except (OSError, ValueError, UnicodeError, RecursionError):
        return {"schema": 1, "receipts": [], "errors": [{"id": "catalog", "reason": "Receipt catalog is unavailable or invalid."}]}
    receipts, errors, seen = [], [], set()
    for entry in data["receipts"]:
        key = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(key, str) or not SAFE_ID.fullmatch(key) or key in seen:
            errors.append({"id": "catalog", "reason": "Invalid or duplicate receipt identifier."})
            continue
        seen.add(key)
        try:
            receipts.append(receipt(repo, entry))
        except ValueError as exc:
            # Parser errors can contain source snippets: expose only our fixed messages.
            reason = str(exc) if type(exc) is ValueError else "Receipt JSON is invalid."
            errors.append({"id": key, "reason": reason})
        except (OSError, UnicodeError, TypeError, KeyError, AttributeError, OverflowError, RecursionError):
            errors.append({"id": key, "reason": "Pinned receipt is missing, unreadable, or malformed."})
    return {"schema": 1, "receipts": receipts, "errors": errors}
