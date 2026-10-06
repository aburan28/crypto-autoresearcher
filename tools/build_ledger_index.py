#!/usr/bin/env python3
"""Build compact, gitignored indexes of the proposal and hypothesis ledgers.

`ledger/proposals/` is ~2,300 files and 78 MB; `ledger/hypotheses/` another
~1,900. The `propose-ideas` dedup step and the `tune-skill` chain walk used to
be told to read them, which is where a large part of every ideation session's
context went. This tool writes one line of JSON per record to

    ledger/.index/proposals.jsonl
    ledger/.index/hypotheses.jsonl
    ledger/.index/experiments.jsonl

carrying only what dedup and orientation need: id, area, status, question and
goal ids, title, class, the claim/statement and mechanism cut to
EXCERPT_CHARS characters, the ids the record references, its date, and its
byte size. A session greps these (~0.5 MB) instead of the corpus, and opens a
record only when the excerpt says it matters.

The index is DERIVED STATE, like `knowledge/INDEX.md`: gitignored, rebuilt on
demand, and rebuilt in CI (`--check-builds`) so a record the builder cannot
read is caught on the branch that broke it. Nothing reads the index as
evidence; a record is cited by id and read from the ledger.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parents[1]
INDEX_DIR = Path("ledger") / ".index"
EXCERPT_CHARS = 200
ID_RE = re.compile(r"\b(?:GOAL|RQ|IDEA|H|EXP|RUN|EV|DEC|TASK|KN-(?:LIT|TECH|FIND|OPEN)|CORR)-[A-Za-z0-9-]+\b")

# kind -> (directory glob, top-level key the record body sits under)
SOURCES: dict[str, tuple[str, str]] = {
    "proposals": ("ledger/proposals/*.yaml", "idea"),
    "hypotheses": ("ledger/hypotheses/*.yaml", "hypothesis"),
    "experiments": ("experiments/*/specification.yaml", "experiment"),
}


def excerpt(value: Any, limit: int = EXCERPT_CHARS) -> str | None:
    if value is None:
        return None
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def area_of(record_id: str | None, body: dict[str, Any]) -> str | None:
    if isinstance(body.get("area"), str):
        return body["area"]
    if not record_id:
        return None
    parts = record_id.split("-")
    # IDEA-YYYYMMDD-tok carries no area; H-/EXP-/RQ-/GOAL- do.
    if len(parts) >= 3 and parts[0] in {"H", "EXP", "RQ", "GOAL", "EV"}:
        return parts[1]
    return None


def date_of(record_id: str | None, body: dict[str, Any]) -> str | None:
    for key in ("added", "designed_at", "specified_at", "created", "recorded_at"):
        value = body.get(key)
        if value:
            return str(value)[:10]
    if record_id:
        m = re.search(r"-(\d{8})-", record_id)
        if m:
            d = m.group(1)
            return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return None


def referenced_ids(body: dict[str, Any], own_id: str | None) -> list[str]:
    blob = json.dumps(body, ensure_ascii=False, default=str)
    found = {m.group(0) for m in ID_RE.finditer(blob)}
    found.discard(own_id or "")
    return sorted(found)


def index_record(kind: str, path: Path, body: dict[str, Any], size: int) -> dict[str, Any]:
    rid = body.get("id") if isinstance(body.get("id"), str) else path.parent.name if kind == "experiments" else path.stem
    row: dict[str, Any] = {
        "id": rid,
        "kind": kind[:-1] if kind.endswith("s") else kind,
        "path": str(path),  # build() overwrites with the repo-relative form
        "area": area_of(rid, body),
        "status": body.get("status"),
        "date": date_of(rid, body),
        "bytes": size,
        "question_id": body.get("question_id"),
        "goal_id": body.get("goal_id"),
        "title": excerpt(body.get("title"), 160),
        "refs": referenced_ids(body, rid),
    }
    if kind == "proposals":
        row.update({
            "class": body.get("class"),
            "novelty_status": body.get("novelty_status"),
            "claim": excerpt(body.get("claim")),
            "mechanism": excerpt(body.get("mechanism")),
            "dominated_by": excerpt(body.get("dominated_by"), 120),
        })
    elif kind == "hypotheses":
        row.update({
            "statement": excerpt(body.get("statement")),
            "mechanism": excerpt(body.get("mechanism")),
            "proposal_id": body.get("proposal_id") or body.get("source_proposal"),
        })
    else:
        row.update({
            "hypothesis_id": body.get("hypothesis_id"),
            "approved_by": body.get("approved_by"),
            "designed_at": str(body.get("designed_at")) if body.get("designed_at") else None,
            "success_criterion": excerpt(body.get("success_criterion")),
        })
    return row


def iter_records(repo_root: Path, kind: str) -> Iterable[tuple[Path, dict[str, Any] | None, int, str | None]]:
    pattern, top = SOURCES[kind]
    for path in sorted(repo_root.glob(pattern)):
        raw = path.read_bytes()
        try:
            doc = yaml.safe_load(raw)
        except yaml.YAMLError as error:
            yield path, None, len(raw), f"unparseable: {str(error).splitlines()[0]}"
            continue
        if not isinstance(doc, dict):
            yield path, None, len(raw), "not a mapping"
            continue
        body = doc.get(top) if isinstance(doc.get(top), dict) else doc
        yield path, body, len(raw), None


def build(repo_root: Path = REPO, out_dir: Path | None = None) -> dict[str, Any]:
    out_dir = out_dir or repo_root / INDEX_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"out_dir": str(out_dir), "kinds": {}, "unreadable": []}
    for kind in SOURCES:
        rows = 0
        out = out_dir / f"{kind}.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for path, body, size, problem in iter_records(repo_root, kind):
                rel = str(path.relative_to(repo_root))
                if body is None:
                    summary["unreadable"].append({"path": rel, "problem": problem})
                    continue
                row = index_record(kind, path, body, size)
                row["path"] = rel
                fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True, default=str) + "\n")
                rows += 1
        summary["kinds"][kind] = {"rows": rows, "bytes": out.stat().st_size, "file": str(out)}
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--out-dir", type=Path, help="defaults to <repo>/ledger/.index")
    parser.add_argument("--check-builds", action="store_true",
                        help="exit 1 when any record could not be indexed (CI)")
    args = parser.parse_args(argv)
    summary = build(args.repo_root, args.out_dir)
    for kind, info in summary["kinds"].items():
        print(f"{kind}: {info['rows']} rows, {info['bytes'] / 1024:.0f} KiB -> {info['file']}")
    # The same allowances check_merge_hygiene.py grants: the prune-only
    # baseline, and records retired by the hash-verified supersession registry.
    import check_merge_hygiene as hygiene
    tolerated = hygiene._baseline() | set(hygiene._retired_by_supersession())
    new_failures = []
    for item in summary["unreadable"]:
        tag = "grandfathered" if item["path"] in tolerated else "unreadable"
        print(f"{tag}: {item['path']}: {item['problem']}", file=sys.stderr)
        if tag == "unreadable":
            new_failures.append(item)
    if args.check_builds and new_failures:
        print(f"FAIL: {len(new_failures)} record(s) could not be indexed and are neither "
              f"baselined nor superseded", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
