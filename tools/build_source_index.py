#!/usr/bin/env python3
"""Regenerate knowledge/SOURCES.md and knowledge/sources.json.

The source index answers one question the knowledge index does not: *what
external material has this program actually consumed, and can a later session
get back to it?* `knowledge/INDEX.md` lists what we believe; this lists what we
read, where it came from, and whether the bytes are still reachable.

Four producers feed it, and they are deliberately kept apart because they carry
different amounts of proof:

  1. `inputs/**/source_record.yaml` — SRC-* packages. A source record is an
     assertion by the session that froze it. `artifact_frozen_in_repo` is the
     field that separates a checkable receipt (SRC-P13-WESOLOWSKI-2026, whose
     text is committed) from an assertion about a read that happened
     (SRC-OAI-TEN-PROOFS-2026, whose PDF is not).
  2. `inputs/**/provenance.json` — per-URL retrieval attempts, including the
     ones that FAILED. A blocked fetch is provenance too: it records that the
     source was sought and why it is missing, which is not the same as never
     having looked.
  3. `inputs/**/*.sha256` sidecars — files vendored into the repository. These
     are the only entries whose hash this tool can recompute, so they are the
     only ones it reports a verdict on.
  4. `knowledge/literature/*.md` — KN-LIT-* citations, keyed by whatever
     external identifier the entry carries.

Rule 5 of AGENTS.md is why the gap sections exist rather than being quietly
dropped: an entry with no recorded identifier is reported as having none. It is
not backfilled, guessed, or resolved by title search here.

Usage:
    python3 tools/build_source_index.py [--check]

--check exits non-zero if either output is stale (for CI), without rewriting.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_OUT = os.path.join(REPO, "knowledge", "SOURCES.md")
JSON_OUT = os.path.join(REPO, "knowledge", "sources.json")
SCHEMA = "crypto.autoresearch.source_index.v1"

# Hashing every vendored byte on each run is cheap for inputs/ (~10 MB) and
# would not be for experiments/ run artifacts, which have their own immutability
# checker (tools/check_run_immutability.py). Kept scoped rather than clever.
HASH_SIZE_LIMIT = 64 * 1024 * 1024


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _rel(path: str) -> str:
    return os.path.relpath(path, REPO)


def _text(value) -> str:
    """Collapse a YAML scalar to one table-safe line."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return "; ".join(_text(v) for v in value)
    return " ".join(str(value).split()).replace("|", "\\|")


def _sha256(path: str) -> str | None:
    if os.path.getsize(path) > HASH_SIZE_LIMIT:
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_identifier(kind: str, value) -> str | None:
    """Normalise one identifier to a comparable `kind:value` key.

    Only strips prefixes and casing the corpus actually uses ('iacr:2004/031',
    'arXiv:2607.14624', a doi.org URL). It does not resolve one identifier kind
    into another -- an entry carrying only a URL stays a URL entry.
    """
    if value in (None, "", "null", "None"):
        return None
    text = str(value).strip()
    low = text.lower()
    if kind == "eprint":
        low = low.removeprefix("iacr:").removeprefix("eprint:")
        return f"eprint:{low}"
    if kind == "arxiv":
        low = low.removeprefix("arxiv:").removeprefix("abs/")
        return f"arxiv:{low}"
    if kind == "doi":
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            low = low.removeprefix(prefix)
        return f"doi:{low}"
    if kind == "isbn":
        return f"isbn:{low.removeprefix('isbn:').replace('-', '')}"
    if kind == "url":
        low = low.removeprefix("https://").removeprefix("http://").rstrip("/")
        return f"url:{low}"
    return f"{kind}:{low}"


# --------------------------------------------------------------------------
# 1. SRC-* source packages
# --------------------------------------------------------------------------

def collect_source_packages() -> list[dict]:
    rows = []
    for path in sorted(glob.glob(os.path.join(REPO, "inputs", "**", "source_record.yaml"),
                                 recursive=True)):
        record = yaml.safe_load(_read(path)) or {}
        provenance = record.get("provenance") or {}
        artifact = record.get("source_artifact") or {}
        repro = record.get("reproducibility") or {}

        frozen_path = record.get("frozen_path")
        frozen_exists = bool(frozen_path) and os.path.exists(os.path.join(REPO, frozen_path))
        package_dir = os.path.dirname(path)
        # Shipped alongside the record. SRC-P13-WESOLOWSKI-2026 declares no
        # `frozen_path` yet its full text sits in the package, so keying only on
        # that field would report the corpus's one fully-frozen paper as absent.
        contents = sorted(
            _rel(p)
            for p in glob.glob(os.path.join(package_dir, "**", "*"), recursive=True)
            if os.path.isfile(p) and os.path.basename(p) not in ("source_record.yaml", "README.md")
        )
        # An explicit declaration wins over both: SRC-OAI states its own artifact
        # is absent and that statement is the point of the record. Inference only
        # fills the field in when nobody declared it, and says which rung it used.
        declared = repro.get("artifact_frozen_in_repo")
        if declared is not None:
            frozen, basis = bool(declared), "declared"
        elif frozen_exists:
            frozen, basis = True, "frozen_path"
        elif contents:
            frozen, basis = True, "package_contents"
        else:
            frozen, basis = False, "no_artifact_found"

        rows.append({
            "record_id": record.get("record_id") or "",
            "kind": record.get("kind") or "",
            "title": record.get("title") or "",
            "author": record.get("author"),
            "year": record.get("year"),
            "package": _rel(os.path.dirname(path)),
            "record_path": _rel(path),
            "url": record.get("source_url") or provenance.get("url"),
            "sha256": artifact.get("sha256") or provenance.get("sha256"),
            "frozen_path": frozen_path,
            "frozen_path_present": frozen_exists,
            "artifact_frozen_in_repo": frozen,
            "artifact_frozen_basis": basis,
            "package_contents": contents,
            "recorded_at": record.get("recorded_at") or record.get("frozen_at"),
            "goal_id": record.get("goal_id"),
            "task_id": record.get("task_id"),
            "used_by": record.get("used_by") or [],
            "limitation": (repro.get("limitation") or "").strip() or None,
        })
    rows.sort(key=lambda r: r["record_id"])
    return rows


# --------------------------------------------------------------------------
# 2. Per-URL retrieval attempts (provenance.json packages)
# --------------------------------------------------------------------------

def collect_retrievals() -> list[dict]:
    rows = []
    seen_fail_markers: set[str] = set()
    for path in sorted(glob.glob(os.path.join(REPO, "inputs", "**", "provenance.json"),
                                 recursive=True)):
        doc = json.loads(_read(path))
        package = _rel(os.path.dirname(path))
        attempts = list(doc.get("attempts") or []) + list(doc.get("addendum_attempts") or [])
        for attempt in attempts:
            rows.append({
                "package": package,
                "provenance_path": _rel(path),
                "source_id": attempt.get("source_id") or "",
                "url": attempt.get("url") or "",
                "purpose": attempt.get("purpose"),
                "retrieved_at": attempt.get("retrieved_at"),
                "http_status": attempt.get("http_status"),
                "status": attempt.get("status") or "",
                "bytes": attempt.get("bytes"),
                "sha256": attempt.get("sha256"),
                "vendored_path": attempt.get("vendored_path"),
                "reason": attempt.get("reason") or attempt.get("curl_stderr"),
                "revision_id": attempt.get("revision_id"),
                "task_id": doc.get("task_id"),
                "goal_id": doc.get("goal_id"),
            })
        for artifact in doc.get("local_artifacts") or []:
            rows.append({
                "package": package,
                "provenance_path": _rel(path),
                "source_id": "local-artifact",
                "url": None,
                "purpose": artifact.get("role"),
                "retrieved_at": doc.get("generated_at"),
                "http_status": None,
                "status": "local_artifact",
                "bytes": artifact.get("bytes"),
                "sha256": artifact.get("sha256"),
                "vendored_path": artifact.get("path"),
                "reason": None,
                "revision_id": None,
                "task_id": doc.get("task_id"),
                "goal_id": doc.get("goal_id"),
            })
    for fail_marker in sorted(
        glob.glob(os.path.join(REPO, "inputs", "**", "sources", "*.FAIL"), recursive=True)
    ):
        rel = _rel(fail_marker)
        if rel in seen_fail_markers:
            continue
        seen_fail_markers.add(rel)
        target = fail_marker[: -len(".FAIL")]
        if os.path.exists(target):
            continue
        package = _rel(os.path.dirname(os.path.dirname(fail_marker)))
        rows.append({
            "package": package,
            "provenance_path": None,
            "source_id": os.path.basename(target),
            "url": None,
            "purpose": "artifact_fetch",
            "retrieved_at": None,
            "http_status": None,
            "status": "failed",
            "bytes": None,
            "sha256": None,
            "vendored_path": _rel(target),
            "reason": _read(fail_marker).strip() or "fetch blocked",
            "revision_id": None,
            "task_id": None,
            "goal_id": None,
        })
    rows.sort(key=lambda r: (r["package"], r["source_id"], r["url"] or ""))
    return rows


# --------------------------------------------------------------------------
# 3. Vendored artifacts under inputs/
# --------------------------------------------------------------------------

SIDECAR_SUFFIXES = (".sha256", ".FAIL")


def collect_frozen_artifacts() -> list[dict]:
    """Every source artifact under `inputs/`, hashed where a sidecar allows it.

    Keyed on the union of three populations, because each alone loses rows the
    others hold. `inputs/ECTD-TESKE-20260731/sources/` is the worked example:
    `fght-2016-961.pdf` is present with no `.sha256`, and
    `dent-galbraith-hidden.pdf` has only a `.FAIL` — a source that was sought
    and never obtained, which is exactly the row an index of "what we used"
    must not silently drop.
    """
    targets: set[str] = set()
    for sidecar_glob in ("*.sha256", "*.FAIL"):
        for sidecar in glob.glob(os.path.join(REPO, "inputs", "**", sidecar_glob), recursive=True):
            targets.add(sidecar[: sidecar.rindex(".")])
    for path in glob.glob(os.path.join(REPO, "inputs", "**", "sources", "*"), recursive=True):
        if os.path.isfile(path) and not path.endswith(SIDECAR_SUFFIXES):
            targets.add(path)

    rows = []
    for target in sorted(targets):
        sidecar = target + ".sha256"
        fail_marker = target + ".FAIL"
        has_sidecar = os.path.exists(sidecar)
        declared_hash = ""
        if has_sidecar:
            fields = _read(sidecar).strip().split()
            declared_hash = fields[0] if fields else ""
        present = os.path.exists(target)
        actual = _sha256(target) if present else None

        if not present:
            # A missing file with only a failure marker was never retrieved;
            # a missing file that something claimed to hash is a real defect.
            verdict = "never_retrieved" if os.path.exists(fail_marker) else "missing"
        elif not has_sidecar:
            verdict = "present_unhashed"
        elif actual is None:
            verdict = "not_hashed_size_limit"
        elif actual == declared_hash:
            verdict = "match"
        else:
            verdict = "MISMATCH"

        rows.append({
            "path": _rel(target),
            "sidecar": _rel(sidecar) if has_sidecar else None,
            "declared_sha256": declared_hash or None,
            "recomputed_sha256": actual,
            "verdict": verdict,
            "present": present,
            "bytes": os.path.getsize(target) if present else None,
            # A .FAIL marker beside a present file records that some fetch of
            # this source failed; it is not a claim about the file that is here.
            "fetch_failure_marker": os.path.exists(fail_marker),
        })
    rows.sort(key=lambda r: r["path"])
    return rows


# --------------------------------------------------------------------------
# 4. Seed bibliography
# --------------------------------------------------------------------------

def collect_bibliography() -> list[dict]:
    path = os.path.join(REPO, "inputs", "bibliography.json")
    if not os.path.exists(path):
        return []
    rows = []
    for entry in json.loads(_read(path)):
        url = entry.get("url")
        rows.append({
            "id": entry.get("id") or "",
            "title": entry.get("title") or "",
            "authors": entry.get("authors") or [],
            "year": entry.get("year"),
            "source": entry.get("source"),
            "url": url,
            "identifier": canonical_identifier("url", url),
            "tags": entry.get("tags") or [],
        })
    rows.sort(key=lambda r: r["id"])
    return rows


# --------------------------------------------------------------------------
# 5. KN-LIT-* citations
# --------------------------------------------------------------------------

IDENTIFIER_ORDER = ("eprint", "arxiv", "doi", "isbn", "url")


def collect_literature() -> list[dict]:
    rows = []
    for path in sorted(glob.glob(os.path.join(REPO, "knowledge", "literature", "*.md"))):
        text = _read(path)
        if not text.startswith("---"):
            continue
        try:
            fm = yaml.safe_load(text.split("---", 2)[1]) or {}
        except yaml.YAMLError:
            # Reported, not skipped: an unparseable entry is a corpus defect and
            # silently dropping it would shrink the gap counts below.
            rows.append({
                "id": os.path.basename(path)[: -len(".md")],
                "path": _rel(path),
                "title": "",
                "authors": [],
                "year": None,
                "venue": None,
                "identifiers": [],
                "primary_identifier": None,
                "citation_verified": None,
                "superseded_by": None,
                "parse_error": True,
            })
            continue
        raw = fm.get("identifiers") or {}
        identifiers = []
        if isinstance(raw, dict):
            for kind in IDENTIFIER_ORDER:
                key = canonical_identifier(kind, raw.get(kind))
                if key:
                    identifiers.append(key)
            for kind in sorted(set(raw) - set(IDENTIFIER_ORDER)):
                key = canonical_identifier(kind, raw.get(kind))
                if key:
                    identifiers.append(key)
        authors = fm.get("authors") or []
        rows.append({
            "id": str(fm.get("id") or os.path.basename(path)[: -len(".md")]),
            "path": _rel(path),
            "title": str(fm.get("title") or ""),
            "authors": [str(a) for a in authors] if isinstance(authors, list) else [str(authors)],
            "year": fm.get("year"),
            "venue": fm.get("venue"),
            "identifiers": identifiers,
            "primary_identifier": identifiers[0] if identifiers else None,
            "citation_verified": fm.get("citation_verified"),
            "superseded_by": fm.get("superseded_by"),
            "parse_error": False,
        })
    rows.sort(key=lambda r: r["id"])
    return rows


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def build() -> dict:
    packages = collect_source_packages()
    retrievals = collect_retrievals()
    artifacts = collect_frozen_artifacts()
    bibliography = collect_bibliography()
    literature = collect_literature()

    with_id = [r for r in literature if r["primary_identifier"]]
    without_id = [r for r in literature if not r["primary_identifier"]]

    # Two KN-LIT entries pointing at one identifier are a curation signal, not
    # an error: one may supersede the other, or the corpus may hold a genuine
    # duplicate. Reported so a curator can tell which.
    by_identifier: dict[str, list[str]] = defaultdict(list)
    for row in with_id:
        by_identifier[row["primary_identifier"]].append(row["id"])
    duplicates = sorted(
        ({"identifier": k, "entries": sorted(v)} for k, v in by_identifier.items() if len(v) > 1),
        key=lambda d: d["identifier"],
    )

    verified = Counter(str(r["citation_verified"]) for r in literature)
    kinds = Counter(r["primary_identifier"].split(":", 1)[0] for r in with_id)
    retrieved = sum(1 for r in retrievals if r["status"] == "retrieved")

    return {
        "schema": SCHEMA,
        "generated_by": "tools/build_source_index.py",
        "counts": {
            "source_packages": len(packages),
            "source_packages_with_frozen_artifact": sum(
                1 for p in packages if p["artifact_frozen_in_repo"]),
            "retrieval_attempts": len(retrievals),
            "retrieval_attempts_succeeded": retrieved,
            "retrieval_attempts_failed": len(retrievals) - retrieved,
            "vendored_artifacts": len(artifacts),
            "vendored_artifacts_hash_match": sum(1 for a in artifacts if a["verdict"] == "match"),
            "vendored_artifacts_present_unhashed": sum(
                1 for a in artifacts if a["verdict"] == "present_unhashed"),
            "vendored_artifacts_never_retrieved": sum(
                1 for a in artifacts if a["verdict"] == "never_retrieved"),
            "vendored_artifacts_hash_mismatch": sum(
                1 for a in artifacts if a["verdict"] == "MISMATCH"),
            "seed_bibliography": len(bibliography),
            "literature_entries": len(literature),
            "literature_with_identifier": len(with_id),
            "literature_without_identifier": len(without_id),
            "literature_parse_errors": sum(1 for r in literature if r["parse_error"]),
            "identifier_kinds": dict(sorted(kinds.items())),
            "citation_verified": dict(sorted(verified.items())),
            "duplicate_identifiers": len(duplicates),
        },
        "source_packages": packages,
        "retrieval_attempts": retrievals,
        "vendored_artifacts": artifacts,
        "seed_bibliography": bibliography,
        "literature": literature,
        "duplicate_identifiers": duplicates,
    }


def render(index: dict) -> str:
    c = index["counts"]
    out: list[str] = [
        "# Source Index",
        "",
        "Every external source this program has consumed, and how reachable it",
        "still is. Generated from the repository by `tools/build_source_index.py` —",
        "do not hand-edit facts here; correct the underlying record and regenerate.",
        "Machine-readable twin: `knowledge/sources.json`.",
        "",
        "`knowledge/INDEX.md` lists what the corpus *believes*. This lists what it",
        "*read*. The distinction that matters in every table below is whether the",
        "bytes are in the repository: a hash this tool can recompute is a receipt,",
        "a hash it cannot is an assertion by the session that recorded it.",
        "",
        "## Summary",
        "",
        "| Class | Count |",
        "|---|---|",
        f"| Frozen source packages (`SRC-*`) | {c['source_packages']} |",
        f"| — of those with the artifact committed | {c['source_packages_with_frozen_artifact']} |",
        f"| Per-URL retrieval attempts | {c['retrieval_attempts']} |",
        f"| — succeeded | {c['retrieval_attempts_succeeded']} |",
        f"| — failed or blocked | {c['retrieval_attempts_failed']} |",
        f"| Source artifacts under `inputs/` | {c['vendored_artifacts']} |",
        f"| — hash recomputed and matching | {c['vendored_artifacts_hash_match']} |",
        f"| — hash MISMATCH | {c['vendored_artifacts_hash_mismatch']} |",
        f"| — present but carrying no `.sha256` | {c['vendored_artifacts_present_unhashed']} |",
        f"| — sought and never retrieved | {c['vendored_artifacts_never_retrieved']} |",
        f"| Seed bibliography entries | {c['seed_bibliography']} |",
        f"| Literature entries (`KN-LIT-*`) | {c['literature_entries']} |",
        f"| — with a resolvable external identifier | {c['literature_with_identifier']} |",
        f"| — with no identifier recorded | {c['literature_without_identifier']} |",
        "",
        "Primary identifier kinds — one per entry, chosen in eprint > arXiv > DOI >"
        " ISBN > URL order, so an entry carrying both an ePrint number and a URL"
        " counts once, under ePrint: "
        + (", ".join(f"{k} {v}" for k, v in c["identifier_kinds"].items()) or "none")
        + ". Every identifier an entry carries is kept in `sources.json`.",
        "",
        "`citation_verified` distribution: "
        + ", ".join(f"`{k}` {v}" for k, v in c["citation_verified"].items())
        + ".",
        "",
        "## 1. Frozen source packages",
        "",
        "`SRC-*` records under `inputs/`. `Artifact in repo` is the field that",
        "decides whether a later session can re-read what was read here.",
        "",
        "| Record | Title | Author | Year | Package | Artifact in repo | Basis | URL | sha256 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for p in index["source_packages"]:
        out.append("| {} | {} | {} | {} | `{}` | {} | {} | {} | {} |".format(
            _text(p["record_id"]), _text(p["title"]), _text(p["author"]), _text(p["year"]),
            _text(p["package"]), "yes" if p["artifact_frozen_in_repo"] else "**no**",
            _text(p["artifact_frozen_basis"]), _text(p["url"]), (p["sha256"] or "")[:16]))

    limited = [p for p in index["source_packages"] if p["limitation"]]
    if limited:
        out += ["", "Declared reproducibility limitations:", ""]
        for p in limited:
            out.append(f"- **{p['record_id']}** — {_text(p['limitation'])}")

    out += [
        "",
        "## 2. Per-URL retrieval attempts",
        "",
        "From `provenance.json` packages. Failed attempts are kept: a blocked",
        "fetch records that the source was sought and why it is missing, which is",
        "not the same as never having looked.",
        "",
        "| Source id | URL | Status | HTTP | Retrieved at | Vendored path |",
        "|---|---|---|---|---|---|",
    ]
    for r in index["retrieval_attempts"]:
        out.append("| {} | {} | {} | {} | {} | {} |".format(
            _text(r["source_id"]), _text(r["url"]), _text(r["status"]),
            _text(r["http_status"]), _text(r["retrieved_at"]),
            f"`{r['vendored_path']}`" if r["vendored_path"] else ""))

    out += [
        "",
        "## 3. Source artifacts under `inputs/`",
        "",
        "The only rows in this document whose integrity this tool checks itself,",
        "and only where a `.sha256` sidecar states an expected value:",
        "",
        "- `match` / `MISMATCH` — sidecar present, hash recomputed here.",
        "- `present_unhashed` — the file is in the repository but nothing declares",
        "  what it should hash to, so this index vouches for its presence only.",
        "- `never_retrieved` — a `.FAIL` marker with no file. The source was sought",
        "  and not obtained; the row stays so the attempt is not mistaken for an",
        "  absence of interest.",
        "",
        "`fetch marker` flags a sibling `.FAIL` file. Beside a *present* file it",
        "records that some fetch failed, and says nothing about the file that is here.",
        "",
        "| Path | Bytes | Verdict | Declared sha256 | Fetch marker |",
        "|---|---|---|---|---|",
    ]
    for a in index["vendored_artifacts"]:
        out.append("| `{}` | {} | {} | {} | {} |".format(
            _text(a["path"]), _text(a["bytes"]),
            a["verdict"] if a["verdict"] == "match" else f"**{a['verdict']}**",
            (a["declared_sha256"] or "")[:16], "yes" if a["fetch_failure_marker"] else ""))

    out += [
        "",
        "## 4. Seed bibliography",
        "",
        "`inputs/bibliography.json` — the hand-curated list the corpus started from.",
        "",
        "| id | Title | Authors | Year | Venue | URL |",
        "|---|---|---|---|---|---|",
    ]
    for b in index["seed_bibliography"]:
        out.append("| `{}` | {} | {} | {} | {} | {} |".format(
            _text(b["id"]), _text(b["title"]), _text(b["authors"]),
            _text(b["year"]), _text(b["source"]), _text(b["url"])))

    with_id = [r for r in index["literature"] if r["primary_identifier"]]
    without_id = [r for r in index["literature"] if not r["primary_identifier"]]

    out += [
        "",
        "## 5. Literature citations with a resolvable identifier",
        "",
        f"{len(with_id)} of {len(index['literature'])} `KN-LIT-*` entries carry an",
        "eprint, arXiv, DOI, ISBN or URL identifier.",
        "",
        "| ID | Title | Year | Identifier | Verified |",
        "|---|---|---|---|---|",
    ]
    for r in with_id:
        out.append("| {} | {} | {} | `{}` | {} |".format(
            _text(r["id"]), _text(r["title"]), _text(r["year"]),
            _text(r["primary_identifier"]), _text(r["citation_verified"])))

    out += [
        "",
        "## 6. Literature citations with no recorded identifier",
        "",
        f"{len(without_id)} entries name a source this index cannot resolve to a",
        "retrievable location. They are listed, not dropped and not backfilled by",
        "guesswork (AGENTS.md rule 5): closing a row means finding the identifier",
        "and editing the entry, after which this table shrinks on its own.",
        "",
        "| ID | Title | Year | Venue | Verified |",
        "|---|---|---|---|---|",
    ]
    for r in without_id:
        out.append("| {} | {} | {} | {} | {} |".format(
            _text(r["id"]), _text(r["title"]), _text(r["year"]),
            _text(r["venue"]), _text(r["citation_verified"])))

    out += [
        "",
        "## 7. Identifiers claimed by more than one entry",
        "",
        "A curation signal, not an error: one entry may supersede the other, or the",
        "corpus may hold a true duplicate. Resolving it is a `/curate-knowledge` job.",
        "",
    ]
    if index["duplicate_identifiers"]:
        out += ["| Identifier | Entries |", "|---|---|"]
        for d in index["duplicate_identifiers"]:
            out.append(f"| `{_text(d['identifier'])}` | {', '.join(d['entries'])} |")
    else:
        out.append("None.")

    return "\n".join(out) + "\n"


def main() -> int:
    index = build()
    markdown = render(index)
    payload = json.dumps(index, indent=2, sort_keys=False, ensure_ascii=False) + "\n"

    if "--check" in sys.argv[1:]:
        stale = []
        for path, want in ((MD_OUT, markdown), (JSON_OUT, payload)):
            have = _read(path) if os.path.exists(path) else ""
            if have != want:
                stale.append(_rel(path))
        if stale:
            print(f"stale: {', '.join(stale)}; run tools/build_source_index.py", file=sys.stderr)
            return 1
        print("knowledge/SOURCES.md and knowledge/sources.json are up to date")
        return 0

    _write(MD_OUT, markdown)
    _write(JSON_OUT, payload)
    c = index["counts"]
    print(f"wrote {_rel(MD_OUT)} and {_rel(JSON_OUT)}: "
          f"{c['source_packages']} source packages, "
          f"{c['retrieval_attempts']} retrieval attempts, "
          f"{c['vendored_artifacts']} source artifacts, "
          f"{c['seed_bibliography']} bibliography entries, "
          f"{c['literature_entries']} literature entries "
          f"({c['literature_without_identifier']} without an identifier)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
