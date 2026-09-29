"""Corpus inventory, route resolution, and view extraction — EXP-CRYPTO-3759c6.

Source-only preparation artifact for TASK-20260907-da9b67. This module defines
the *interfaces and pure functions* the frozen protocol
(``experiments/EXP-CRYPTO-3759c6/specification.yaml``) requires for the corpus
stage. It is written for later admission and does not perform a census: no
function in this file is invoked against the real repository or the pinned
commit by this preparation task. Producing ``census.json``,
``corpus-manifest.jsonl``, ``route-audit.jsonl``, or ``candidate-pairs.jsonl``
is future admitted scientific work (see ``preparation-report.yaml``).

Frozen parameters this module must honor when it is later run (spec refs):
  - source_commit: 5401431c1576bf0e75fac70df1cc54f409ed7c85  (corpus.inputs)
  - corpus_rule: all committed knowledge/literature/KN-LIT-*.md and
    ledger/proposals/IDEA-*.yaml blobs at that exact commit (spec.corpus_rule)
  - ordering: UTF-8 bytewise lexical repository path, then canonical record ID
    (spec.corpus.ordering)
  - manifest_fields: [path, git_blob_id, byte_length, sha256, filename_ID,
    declared_ID, route_chain, parse_status, payload_status, view_hashes,
    eligibility_reason] (spec.corpus.manifest_fields)

No shell execution occurs anywhere in this module: git object access is via
``git cat-file``/``git ls-tree`` subprocess calls with fixed argv lists (no
shell=True, no string interpolation into a shell), which is a controlled
subprocess invocation, not a replay of an untrusted recorded command. Nothing
in this file calls those subprocess helpers at import time or from module
scope; they are functions to be invoked by the future admission runner.
"""

from __future__ import annotations

import dataclasses
import hashlib
import re
import subprocess
from enum import Enum
from typing import Iterable, Optional

# ---------------------------------------------------------------------------
# Frozen constants (spec.controlled_variables, spec.inputs)
# ---------------------------------------------------------------------------

SOURCE_COMMIT = "5401431c1576bf0e75fac70df1cc54f409ed7c85"

#: Corpus membership predicate. Two path *shapes* only; no other directory or
#: extension is in-corpus regardless of content. (spec.inputs.corpus_rule)
CORPUS_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^knowledge/literature/KN-LIT-[^/]+\.md$"),
    re.compile(r"^ledger/proposals/IDEA-[^/]+\.yaml$"),
)


class ParseStatus(str, Enum):
    OK = "ok"
    MALFORMED = "malformed"          # duplicate YAML keys, bad frontmatter, ambiguous title/abstract
    UNRESOLVED_ROUTE = "unresolved_route"
    MISSING_BLOB = "missing_blob"


class PayloadStatus(str, Enum):
    PRESENT = "present"              # hash-verified local payload, not an LFS pointer
    LFS_POINTER = "lfs_pointer"      # a pointer is not a payload (spec.corpus.payloads)
    ABSENT = "absent"
    DECODE_ERROR = "decode_error"    # not strict-UTF-8


@dataclasses.dataclass(frozen=True)
class CorpusRow:
    """One row of ``corpus-manifest.jsonl`` (spec.corpus.manifest_fields).

    All fields are outputs of a real inventory pass; this dataclass only
    fixes their names, types and invariants. No instance is constructed by
    this preparation task.
    """

    path: str
    git_blob_id: str
    byte_length: int
    sha256: str
    filename_id: Optional[str]
    declared_id: Optional[str]
    route_chain: tuple[str, ...]           # empty if no supersession route applies
    parse_status: ParseStatus
    payload_status: PayloadStatus
    view_hashes: dict[str, str]            # {"full_body": sha256, "title_abstract": sha256}
    eligibility_reason: Optional[str]      # non-null iff excluded from scoring


@dataclasses.dataclass(frozen=True)
class RouteAuditRow:
    """One row of ``route-audit.jsonl`` (spec.corpus.routes)."""

    source_path: str
    source_hash: str
    target_path: str
    target_hash: str
    route_kind: str           # e.g. "schema_supersession", "proposal_successor"
    cycle_detected: bool
    resolved_effective_id: Optional[str]


@dataclasses.dataclass(frozen=True)
class Candidate:
    """One row of ``candidate-pairs.jsonl`` (spec.candidates.definition).

    Unique (proposal_id, effective_kn_lit_id) pairs from direct source_refs
    fields only, at the effective proposal root.
    """

    proposal_id: str
    effective_kn_lit_id: Optional[str]     # None iff the reference is unresolved
    source_field: str
    source_path: str
    source_line: Optional[int]
    original_token: str
    unresolved_reason: Optional[str]       # non-null iff effective_kn_lit_id is None


# ---------------------------------------------------------------------------
# Git object access (read-only; not invoked by this task)
# ---------------------------------------------------------------------------

def git_ls_tree(commit: str, repo_root: str) -> list[tuple[str, str]]:
    """Return (path, blob_id) for every blob at ``commit`` under ``repo_root``.

    Fixed argv, no shell metacharacters, no interpolation of untrusted text.
    Not called by this preparation task; a future admission pass invokes this
    to build the raw path universe before filtering by CORPUS_PATH_PATTERNS.
    """
    proc = subprocess.run(
        ["git", "ls-tree", "-r", "--full-tree", commit],
        cwd=repo_root,
        capture_output=True,
        check=True,
        text=False,
    )
    rows: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        # "<mode> <type> <blob>\t<path>"
        meta, path = line.split(b"\t", 1)
        blob_id = meta.split()[2]
        rows.append((path.decode("utf-8"), blob_id.decode("ascii")))
    return rows


def git_cat_blob(blob_id: str, repo_root: str) -> bytes:
    """Return raw bytes of a git blob object. Not called by this task."""
    proc = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def in_corpus(path: str) -> bool:
    """True iff ``path`` matches the frozen corpus_rule path shapes."""
    return any(pattern.match(path) for pattern in CORPUS_PATH_PATTERNS)


def is_lfs_pointer(raw: bytes) -> bool:
    """Git LFS pointer text is not a payload (spec.corpus.payloads)."""
    return raw.startswith(b"version https://git-lfs.github.com/spec/")


def decode_strict_utf8(raw: bytes) -> tuple[Optional[str], PayloadStatus]:
    """Deterministic Unicode decoding as UTF-8 with strict errors (spec.corpus.ordering)."""
    if is_lfs_pointer(raw):
        return None, PayloadStatus.LFS_POINTER
    try:
        return raw.decode("utf-8", errors="strict"), PayloadStatus.PRESENT
    except UnicodeDecodeError:
        return None, PayloadStatus.DECODE_ERROR


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def corpus_sort_key(path: str, record_id: Optional[str]) -> tuple[bytes, str]:
    """UTF-8 bytewise lexical repository path, then canonical record ID (spec.corpus.ordering)."""
    return (path.encode("utf-8"), record_id or "")


# ---------------------------------------------------------------------------
# Identity and route resolution (spec.corpus.identity, spec.corpus.routes)
# ---------------------------------------------------------------------------

def filename_stem_id(path: str) -> str:
    """Filename stem is the candidate ID (spec.corpus.identity)."""
    leaf = path.rsplit("/", 1)[-1]
    for suffix in (".md", ".yaml", ".yml"):
        if leaf.endswith(suffix):
            return leaf[: -len(suffix)]
    return leaf


def resolve_route(
    source_id: str,
    declared_route_targets: Iterable[tuple[str, str]],
    known_hashes: dict[str, str],
) -> RouteAuditRow:
    """Resolve one explicit, committed, hash-verified route.

    Never infer a route from a similar title, date, or numerical suffix
    (spec.corpus.routes). ``declared_route_targets`` must come from an
    explicit committed supersession/schema-registry binding present in the
    pinned source packet/commit; this function performs no fuzzy matching.
    This is a pure function over already-extracted route declarations; it
    does not read the corpus itself and is not invoked by this task.
    """
    raise NotImplementedError(
        "resolve_route is a frozen interface for the future admission pass; "
        "no route resolution is performed by TASK-20260907-da9b67."
    )


# ---------------------------------------------------------------------------
# View extraction (spec.corpus_views)
# ---------------------------------------------------------------------------

#: Case-insensitive literal "Abstract" heading detector, any Markdown level.
_ABSTRACT_HEADING = re.compile(r"^(#{1,6})\s*Abstract\s*$", re.IGNORECASE | re.MULTILINE)
_ANY_HEADING = re.compile(r"^(#{1,6})\s+.*$", re.MULTILINE)
_H1_HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


@dataclasses.dataclass(frozen=True)
class TitleAbstractExtraction:
    title: str
    abstract: str
    title_source: Optional[str]     # "frontmatter" | "h1" | None
    abstract_source: Optional[str]  # "frontmatter" | "heading" | None
    ambiguous: bool                 # True iff multiple conflicting Abstract headings found


def extract_full_body_view(text: str) -> str:
    """Complete effective UTF-8 record, frontmatter and body, line endings preserved.

    (spec.corpus_views.full_body) This is an identity transform by design: the
    admitted grep engine operates on the record bytes exactly as stored.
    """
    return text


def extract_title_abstract_view(
    text: str,
    frontmatter_title: Optional[str],
    frontmatter_abstract: Optional[str],
) -> TitleAbstractExtraction:
    """Title/abstract precedence per spec.corpus_views.title_abstract.

    Title: nonempty frontmatter title scalar, else first literal H1, else
    empty. Abstract: scalar frontmatter abstract, else a unique literal
    "Abstract" heading (case-insensitive) whose body ends at the next
    heading of the same-or-higher level; multiple conflicting candidates are
    unresolved (ambiguous=True), never selected after results. Missing
    abstract is empty; never substitute Contribution/summary/an inferred
    abstract. Concatenation (title, newline, abstract) is the caller's job
    once this extraction is accepted, not performed inside this function so
    that ambiguous/ missing states remain independently inspectable.
    """
    title_source = None
    title = ""
    if frontmatter_title and frontmatter_title.strip():
        title = frontmatter_title
        title_source = "frontmatter"
    else:
        match = _H1_HEADING.search(text)
        if match:
            title = match.group(1)
            title_source = "h1"

    abstract_source = None
    abstract = ""
    ambiguous = False
    if frontmatter_abstract and frontmatter_abstract.strip():
        abstract = frontmatter_abstract
        abstract_source = "frontmatter"
    else:
        headings = list(_ABSTRACT_HEADING.finditer(text))
        if len(headings) > 1:
            ambiguous = True
        elif len(headings) == 1:
            heading = headings[0]
            level = len(heading.group(1))
            body_start = heading.end()
            body_end = len(text)
            for later in _ANY_HEADING.finditer(text, body_start):
                if len(later.group(1)) <= level:
                    body_end = later.start()
                    break
            abstract = text[body_start:body_end].strip("\n")
            abstract_source = "heading"

    return TitleAbstractExtraction(
        title=title,
        abstract=abstract,
        title_source=title_source,
        abstract_source=abstract_source,
        ambiguous=ambiguous,
    )


def concatenate_title_abstract(extraction: TitleAbstractExtraction) -> str:
    """title, one newline, abstract (spec.corpus_views.title_abstract)."""
    return f"{extraction.title}\n{extraction.abstract}"


def metadata_stratum(extraction: TitleAbstractExtraction) -> str:
    """title-only / abstract-only / both / neither (spec.corpus_views.metadata)."""
    has_title = bool(extraction.title)
    has_abstract = bool(extraction.abstract)
    if has_title and has_abstract:
        return "both"
    if has_title:
        return "title_only"
    if has_abstract:
        return "abstract_only"
    return "neither"


# ---------------------------------------------------------------------------
# Candidate extraction (spec.candidates)
# ---------------------------------------------------------------------------

def extract_candidates(
    proposal_id: str,
    source_refs: Iterable[object],
    source_path: str,
) -> list[Candidate]:
    """Unique (proposal_ID, effective_KN-LIT_ID) pairs from direct source_refs only.

    Accept a literal KN-LIT ID, a repository path naming that record, or a
    structured entry with an explicit id/record_id/path field. Conflicting
    explicit fields are unresolved. A prose mention, bibliography occurrence,
    or transitive reference is not a direct pair (spec.candidates). This
    function performs no corpus lookup and does not resolve routes; it only
    normalizes the raw source_refs shape into Candidate rows with
    effective_kn_lit_id left None (unresolved) until route resolution runs.
    It is not invoked by this preparation task against real proposal records.
    """
    raise NotImplementedError(
        "extract_candidates is a frozen interface for the future admission "
        "pass; no candidate enumeration is performed by TASK-20260907-da9b67."
    )


def dedupe_aliases(candidates: list[Candidate]) -> list[Candidate]:
    """Source-reference aliases resolving to the same effective KN-LIT ID are
    deduplicated within a proposal, retaining all original locators
    (spec.corpus.routes). Interface only; not invoked here.
    """
    raise NotImplementedError(
        "dedupe_aliases is a frozen interface for the future admission pass."
    )
