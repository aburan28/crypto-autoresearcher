"""Stage this repository's records into the corpus layout.

The corpus layout in the plan assumes documents arrive in S3 with hand-written
sidecars. This program's records already exist, in the repository, with their
provenance written into YAML frontmatter and record fields -- so the sidecars
are *derived* from them rather than authored again. Every field below comes
from a recorded value or the directory a file lives in; nothing is inferred by
a model, and ``provenance_class`` is ``deterministic`` to say so.

This is what makes the local vertical slice run against real content: the
ingestion path, the chunker, and the evaluation set all see the same documents
an agent will actually ask about.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Collection, Iterator

from crypto_kb.config import SOURCE_PREFIX
from crypto_kb.ingest.schema_supersession import (
    SchemaSupersession,
    SchemaSupersessionError,
    load_schema_supersessions,
    route_repository_source,
)
from crypto_kb.metadata import metadata_key
from crypto_kb.models import Authority, ClaimStatus, EvidenceLevel, ProvenanceClass, SourceType

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

#: Venues that are not peer reviewed, so an entry citing them is a preprint.
_PREPRINT_VENUES = ("eprint", "arxiv", "preprint")

#: Evidence-record strength -> the program's evidence levels.
_STRENGTH: dict[str, EvidenceLevel] = {
    "machine-checked": EvidenceLevel.MACHINE_CHECKED,
    "independently-reproduced": EvidenceLevel.INDEPENDENTLY_REPRODUCED,
    "replicated": EvidenceLevel.REPLICATED,
    "multi-run": EvidenceLevel.REPLICATED,
    "single-run": EvidenceLevel.SINGLE_RUN,
    "analytical": EvidenceLevel.ANALYTICAL,
    "theoretical": EvidenceLevel.ANALYTICAL,
}

#: Evidence-record direction -> claim status.
_DIRECTION: dict[str, ClaimStatus] = {
    "supports": ClaimStatus.SUPPORTED,
    "strengthens": ClaimStatus.SUPPORTED,
    "weakens": ClaimStatus.WEAKENED,
    "refutes": ClaimStatus.REJECTED_SCOPED,
    "rejects": ClaimStatus.REJECTED_SCOPED,
    "inconclusive": ClaimStatus.INCONCLUSIVE,
    "neutral": ClaimStatus.INCONCLUSIVE,
}


@dataclass(frozen=True)
class StagingRule:
    """Where a family of repository files goes, and how its sidecar is built."""

    name: str
    glob: str
    destination: str
    source_type: SourceType
    id_prefix: str
    build: Callable[[Path, dict[str, Any], str], dict[str, Any]]


@dataclass
class StagedDocument:
    source_key: str
    metadata: dict[str, Any]
    data: bytes


# --------------------------------------------------------------------------
# Sidecar builders
# --------------------------------------------------------------------------


def _literature(path: Path, front: dict[str, Any], git_commit: str) -> dict[str, Any]:
    venue = str(front.get("venue", "") or "").lower()
    identifiers = front.get("identifiers") or {}
    url = identifiers.get("url") if isinstance(identifiers, dict) else None
    is_preprint = any(marker in venue for marker in _PREPRINT_VENUES) or not venue
    return {
        "source_type": SourceType.PAPER.value,
        "title": front.get("title") or path.stem,
        "authors": [str(a) for a in front.get("authors", []) or []],
        "publication_year": _int_or_none(front.get("year")),
        "publication_status": "preprint" if is_preprint else "published",
        "topics": [str(t) for t in front.get("tags", []) or []],
        # An external paper carries an external status regardless of how much
        # this program believes it.
        "claim_status": ClaimStatus.EXTERNAL_SOURCE.value,
        "authority": (Authority.PREPRINT if is_preprint else Authority.PEER_REVIEWED).value,
        "source_url": url,
        "superseded": bool(front.get("superseded_by")),
        "superseded_by": front.get("superseded_by"),
    }


def _technique(path: Path, front: dict[str, Any], git_commit: str) -> dict[str, Any]:
    return {
        "source_type": SourceType.INTERNAL_NOTE.value,
        "title": front.get("title") or path.stem,
        "topics": [str(t) for t in front.get("tags", []) or []],
        "claim_status": ClaimStatus.PUBLISHED.value,
        "authority": Authority.INTERNAL_ANALYSIS.value,
        "git_commit": git_commit,
        "superseded": bool(front.get("superseded_by")),
        "superseded_by": front.get("superseded_by"),
    }


def _finding(path: Path, front: dict[str, Any], git_commit: str) -> dict[str, Any]:
    confidence = str(front.get("confidence", "") or "").lower()
    evidence = _STRENGTH.get(confidence)
    return {
        "source_type": SourceType.INTERNAL_NOTE.value,
        "title": front.get("title") or path.stem,
        "topics": [str(t) for t in front.get("tags", []) or []],
        "claim_status": ClaimStatus.SUPPORTED.value,
        "evidence_level": evidence.value if evidence else None,
        "related_experiments": [str(e) for e in front.get("experiment_refs", []) or []],
        "git_commit": git_commit,
        "superseded": bool(front.get("superseded_by")),
        "superseded_by": front.get("superseded_by"),
    }


def _open_problem(path: Path, front: dict[str, Any], git_commit: str) -> dict[str, Any]:
    return {
        "source_type": SourceType.INTERNAL_NOTE.value,
        "title": front.get("title") or path.stem,
        "topics": [str(t) for t in front.get("tags", []) or []],
        "claim_status": ClaimStatus.HYPOTHESIS.value,
        "authority": Authority.INTERNAL_ANALYSIS.value,
        "git_commit": git_commit,
    }


def _evidence_record(path: Path, record: dict[str, Any], git_commit: str) -> dict[str, Any]:
    body = record.get("evidence", record) if isinstance(record, dict) else {}
    strength = str(body.get("strength", "") or "").lower()
    direction = str(body.get("direction", "") or "").lower()
    evidence = _STRENGTH.get(strength)
    return {
        "source_type": SourceType.LEDGER.value,
        "title": f"Evidence {body.get('id', path.stem)} for {body.get('hypothesis_id', 'unknown hypothesis')}",
        "claim_status": _DIRECTION.get(direction, ClaimStatus.INCONCLUSIVE).value,
        "evidence_level": evidence.value if evidence else None,
        "experiment_id": _first(body.get("experiment_ids")),
        "related_experiments": [str(e) for e in body.get("experiment_ids", []) or []],
        "run_ids": [str(r) for r in body.get("run_ids", []) or []],
        "git_commit": git_commit,
    }


def _ledger_record(path: Path, record: dict[str, Any], git_commit: str) -> dict[str, Any]:
    body = _unwrap(record)
    return {
        "source_type": SourceType.LEDGER.value,
        "title": str(body.get("title") or body.get("statement") or body.get("question") or path.stem)[:300],
        "claim_status": ClaimStatus.HYPOTHESIS.value
        if path.name.startswith("H-")
        else ClaimStatus.PUBLISHED.value,
        "authority": Authority.INTERNAL_ANALYSIS.value,
        "experiment_id": _first(body.get("experiment_ids")),
        "related_experiments": [str(e) for e in body.get("experiment_ids", []) or []],
        "git_commit": git_commit,
    }


def _experiment(path: Path, record: dict[str, Any], git_commit: str) -> dict[str, Any]:
    body = _unwrap(record)
    experiment_id = str(body.get("id") or path.parent.name)
    return {
        "source_type": SourceType.EXPERIMENT.value,
        "title": str(body.get("title") or body.get("objective") or experiment_id)[:300],
        "claim_status": ClaimStatus.PUBLISHED.value,
        # A specification is a plan, not a result: it is single-run evidence at
        # best, and only once its runs exist.
        "evidence_level": EvidenceLevel.NONE.value,
        "authority": Authority.SINGLE_RUN_EXPERIMENT.value,
        "experiment_id": experiment_id,
        "related_experiments": [experiment_id],
        "git_commit": git_commit,
    }


def _repository_doc(path: Path, front: dict[str, Any], git_commit: str) -> dict[str, Any]:
    return {
        "source_type": SourceType.REPOSITORY_DOC.value,
        "title": front.get("title") or _first_heading(path) or path.stem,
        "claim_status": ClaimStatus.PUBLISHED.value,
        "authority": Authority.INTERNAL_ANALYSIS.value,
        "git_commit": git_commit,
    }


def _vendored_paper(path: Path, front: dict[str, Any], git_commit: str) -> dict[str, Any]:
    return {
        "source_type": SourceType.PAPER.value,
        "title": _first_heading(path) or path.parent.name,
        "claim_status": ClaimStatus.EXTERNAL_SOURCE.value,
        "authority": Authority.PREPRINT.value,
        "publication_status": "preprint",
    }


RULES: tuple[StagingRule, ...] = (
    StagingRule("literature", "knowledge/literature/KN-LIT-*.md", "papers/literature-notes",
                SourceType.PAPER, "paper", _literature),
    StagingRule("techniques", "knowledge/techniques/KN-TECH-*.md", "internal-notes/techniques",
                SourceType.INTERNAL_NOTE, "technique", _technique),
    StagingRule("findings", "knowledge/findings/KN-FIND-*.md", "internal-notes/findings",
                SourceType.INTERNAL_NOTE, "finding", _finding),
    StagingRule("open-problems", "knowledge/open-problems/KN-OPEN-*.md", "internal-notes/open-problems",
                SourceType.INTERNAL_NOTE, "open-problem", _open_problem),
    StagingRule("evidence", "ledger/evidence/EV-*.yaml", "ledgers/evidence",
                SourceType.LEDGER, "evidence", _evidence_record),
    StagingRule("evidence-root", "ledger/EV-*.yaml", "ledgers/evidence",
                SourceType.LEDGER, "evidence", _evidence_record),
    StagingRule("hypotheses", "ledger/H-*.yaml", "ledgers/hypotheses",
                SourceType.LEDGER, "hypothesis", _ledger_record),
    StagingRule("questions", "ledger/RQ-*.yaml", "ledgers/questions",
                SourceType.LEDGER, "question", _ledger_record),
    StagingRule("decisions", "ledger/decisions/DEC-*.yaml", "ledgers/decisions",
                SourceType.LEDGER, "decision", _ledger_record),
    StagingRule("decisions-root", "ledger/DEC-*.yaml", "ledgers/decisions",
                SourceType.LEDGER, "decision", _ledger_record),
    StagingRule("experiments", "experiments/*/specification.yaml", "experiments/specifications",
                SourceType.EXPERIMENT, "experiment", _experiment),
    StagingRule("experiment-analysis", "experiments/*/analysis.md", "experiments/analyses",
                SourceType.EXPERIMENT, "experiment-analysis", _experiment),
    StagingRule("docs", "docs/*.md", "repository-docs",
                SourceType.REPOSITORY_DOC, "doc", _repository_doc),
    StagingRule("vendored-papers", "inputs/*/paper_fulltext.md", "papers/vendored",
                SourceType.PAPER, "paper", _vendored_paper),
)


# --------------------------------------------------------------------------
# Staging
# --------------------------------------------------------------------------


def stage_repository(
    repo_root: Path,
    store,
    rules: tuple[StagingRule, ...] = RULES,
    limit_per_rule: int | None = None,
    include: Collection[str] | None = None,
) -> list[StagedDocument]:
    """Copy repository records into the corpus layout with derived sidecars.

    ``include`` restricts staging to an explicit set of repository-relative
    POSIX paths. The rules still decide *how* each file is staged; the set
    decides *which* files exist at all, which is what pins a corpus whose
    content must not move under an evaluation.
    """
    git_commit = _git_commit(repo_root)
    staged: list[StagedDocument] = []
    for document in iter_staged(repo_root, rules, git_commit, limit_per_rule, include):
        store.put(document.source_key, document.data)
        store.put(
            metadata_key(document.source_key),
            json.dumps(document.metadata, indent=2, sort_keys=True).encode("utf-8"),
            content_type="application/json",
        )
        staged.append(document)
    return staged


def iter_staged(
    repo_root: Path,
    rules: tuple[StagingRule, ...],
    git_commit: str,
    limit_per_rule: int | None = None,
    include: Collection[str] | None = None,
) -> Iterator[StagedDocument]:
    allowed = None if include is None else frozenset(include)
    supersessions = load_schema_supersessions(repo_root)
    seen_ids: set[str] = set()
    for rule in rules:
        count = 0
        for path in sorted(repo_root.glob(rule.glob)):
            if limit_per_rule is not None and count >= limit_per_rule:
                break
            if not path.is_file():
                continue
            if allowed is not None and path.relative_to(repo_root).as_posix() not in allowed:
                continue
            document = _stage_one(repo_root, path, rule, git_commit, supersessions)
            if document is None:
                continue
            source_id = document.metadata["source_id"]
            if source_id in seen_ids:
                # Two rules can match one file (ledger/EV-*.yaml also lives
                # under ledger/evidence/). First rule wins; a duplicate would
                # index the same content under two ids and break diversity.
                continue
            seen_ids.add(source_id)
            count += 1
            yield document


def _stage_one(
    repo_root: Path,
    path: Path,
    rule: StagingRule,
    git_commit: str,
    supersessions: dict[str, SchemaSupersession] | None = None,
) -> StagedDocument | None:
    registry = supersessions if supersessions is not None else load_schema_supersessions(repo_root)
    routed = route_repository_source(repo_root, path, registry)
    raw = routed.data
    text = raw.decode("utf-8", errors="replace")
    front = _front_or_record(path, text)
    if front is None:
        if routed.supersession is not None:
            raise SchemaSupersessionError(
                f"registered replacement for "
                f"{routed.supersession.superseded_path} is not parseable"
            )
        return None

    identifier = _identifier(path, rule, front)
    fields = rule.build(path, front, git_commit)
    metadata = {
        "schema_version": 1,
        "source_id": f"{rule.id_prefix}:{identifier}",
        "provenance_class": ProvenanceClass.DETERMINISTIC.value,
        **fields,
    }
    if routed.supersession is not None:
        entry = routed.supersession
        legacy_id = _legacy_identifier(path, rule)
        expected_id = entry.redirect_id or entry.replacement_id or legacy_id
        if identifier != expected_id:
            raise SchemaSupersessionError(
                f"registered replacement for {entry.superseded_path} declares "
                f"identifier {identifier!r}, expected {expected_id!r}"
            )
        if entry.redirect_id:
            # The pinned target parsed to the declared canonical identifier.
            # Its ordinary discovery path will stage it once; suppress only
            # this immutable alias after that identity check succeeds.
            return None
        if legacy_id != identifier:
            metadata["supersedes"] = sorted(
                {*metadata.get("supersedes", []), legacy_id}
            )
        metadata["verification_artifacts"] = sorted(
            {
                *metadata.get("verification_artifacts", []),
                f"{entry.superseded_path}@sha256:{entry.superseded_sha256}",
                f"{entry.superseding_path}@sha256:{entry.superseding_sha256}",
            }
        )
    metadata = {k: v for k, v in metadata.items() if v is not None or k in {"superseded_by"}}
    relative = path.relative_to(repo_root).as_posix()
    # Keyed by identifier, not filename: every experiment's spec is called
    # `specification.yaml`, so filename keys would collide and each staged
    # experiment would overwrite the last.
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", identifier)
    source_key = f"{SOURCE_PREFIX}{rule.destination}/{safe}{path.suffix}"
    metadata.setdefault("topics", [])
    metadata["topics"] = sorted({*metadata.get("topics", []), *_path_topics(relative)})
    return StagedDocument(source_key=source_key, metadata=metadata, data=raw)


def _front_or_record(path: Path, text: str) -> dict[str, Any] | None:
    if path.suffix in {".yaml", ".yml"}:
        try:
            import yaml

            loaded = yaml.safe_load(text)
        except Exception:
            return None
        return loaded if isinstance(loaded, dict) else {}
    match = _FRONTMATTER.match(text)
    if not match:
        return {}
    try:
        import yaml

        loaded = yaml.safe_load(match.group(1))
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _identifier(path: Path, rule: StagingRule, front: dict[str, Any]) -> str:
    body = _unwrap(front)
    recorded = body.get("id") if isinstance(body, dict) else None
    if isinstance(recorded, str) and recorded.strip():
        base = recorded.strip()
    elif path.name in {"specification.yaml", "analysis.md", "paper_fulltext.md"}:
        base = path.parent.name
    else:
        base = path.stem
    if rule.name == "experiment-analysis":
        return f"{base}-analysis"
    return base


def _legacy_identifier(path: Path, rule: StagingRule) -> str:
    if path.name in {"specification.yaml", "analysis.md", "paper_fulltext.md"}:
        base = path.parent.name
    else:
        base = path.stem
    return f"{base}-analysis" if rule.name == "experiment-analysis" else base


def _path_topics(relative: str) -> list[str]:
    """Directory-derived topics. Deterministic, and useful for coarse filters."""
    parts = [p for p in Path(relative).parts[:-1] if p not in {".", ""}]
    return [p.lower() for p in parts]


def _unwrap(record: Any) -> dict[str, Any]:
    """Ledger records wrap their body in a single top-level key."""
    if not isinstance(record, dict):
        return {}
    if len(record) == 1:
        only = next(iter(record.values()))
        if isinstance(only, dict):
            return only
    return record


def _first(values: Any) -> str | None:
    if isinstance(values, list) and values:
        return str(values[0])
    return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _first_heading(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for _ in range(60):
                line = handle.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        return None
    return None


def _git_commit(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return result.stdout.strip() or "unknown"
