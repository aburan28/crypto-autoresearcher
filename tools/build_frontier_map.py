#!/usr/bin/env python3
"""Render, check and search the known-results map (knowledge/frontiers/ecdlp/).

The map is the claim-level answer to "has this been done before?". A KN-LIT
entry says what ONE paper contains; a known-result row (KR-<AREA>-<tok>) says
what the literature has ESTABLISHED about one mechanism, bound or record, which
papers establish it, and -- in `forecloses` -- the phrases an idea generator
would use when it is about to re-derive it. The program's measured failure
mode was never a missing paper: it was ideas generated before anyone compared
them with a known result that sat in the corpus as an unreadable stub
(docs/novelty-screen-20260729.md; DEC-20260916-3c0cf5 on IDEA-20260915-8fe0ef;
the isogeny-transfer lane closed by Tate's theorem, EV-IT-511f3d). The map is
short enough to paste into an ideation handoff, so the comparison happens
BEFORE generation and does not depend on the retrieval index being up.

    python3 tools/build_frontier_map.py                      # render every area
    python3 tools/build_frontier_map.py --area index-calculus
    python3 tools/build_frontier_map.py --out knowledge/frontiers/ecdlp/MAP.md
    python3 tools/build_frontier_map.py --match "frobenius invariant factor base"
    python3 tools/build_frontier_map.py --check             # CI: schema + refs

Rows are one file each and write-once (a correction is a new row plus
`superseded_by` on the old one), for the same reason goal checkpoints are
sharded: a shared YAML list conflicts on every concurrent append. MAP.md is
derived and gitignored, like knowledge/INDEX.md. See the directory README for
the schema.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - the repo pins PyYAML
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTIER_ROOT = os.path.join(REPO, "knowledge", "frontiers", "ecdlp")

# area directory -> KR area code. A row's id must carry its directory's code.
AREAS = {
    "generic-rho": "RHO",
    "index-calculus": "IC",
}
KR_ID = re.compile(r"^KR-([A-Z]+)-([0-9a-f]{6})$")
KN_REF = re.compile(r"^KN-(LIT|TECH|FIND|OPEN)-(?:\d{3,4}|[0-9a-f]{6})$")
KN_DIRS = {"LIT": "literature", "TECH": "techniques", "FIND": "findings",
           "OPEN": "open-problems"}

REQUIRED = ["id", "area", "kind", "title", "claim", "status", "sources",
            "forecloses", "added", "superseded_by"]
KINDS = {
    "known_mechanism",   # a technique and what it buys (e.g. negation map: sqrt 2)
    "known_bound",       # a proven or heuristic complexity statement
    "known_negative",    # an established obstruction / "does not help" result
    "record",            # a computational record or published cost figure
    "dispute",           # a claim the literature contests (e.g. FFD assumption)
    "textbook_fact",     # classical fact ideation keeps rediscovering
}
STATUSES = {"proven", "heuristic", "conjectured", "disputed", "refuted",
            "measured", "reported"}
VERIFICATION_STATES = {
    "full_text_read",       # the cited locator was read in the primary source
    "abstract_read",        # only the abstract / summary page was read
    "secondary_source",     # stated by a survey or a later paper that was read
    "recalled_unverified",  # a pointer only; never sufficient on its own
}
INTERNAL_RELATIONS = {"rederived", "measured", "extends", "contradicts",
                      "applies", "cites"}


def row_paths() -> list[str]:
    out: list[str] = []
    for area in AREAS:
        out += glob.glob(os.path.join(FRONTIER_ROOT, area, "KR-*.yaml"))
    return sorted(p for p in out if not os.path.basename(p).startswith("._"))


def load_rows() -> list[dict[str, Any]]:
    rows = []
    for path in row_paths():
        with open(path, encoding="utf-8") as fh:
            body = yaml.safe_load(fh) or {}
        body["_path"] = os.path.relpath(path, REPO)
        body["_area_dir"] = os.path.basename(os.path.dirname(path))
        rows.append(body)
    return rows


def row_ids() -> set[str]:
    """Ids of every row on disk (used by validate_ledger for prior_art)."""
    return {os.path.splitext(os.path.basename(p))[0] for p in row_paths()}


def knowledge_ref_exists(ref: str) -> bool:
    m = KN_REF.match(ref or "")
    if not m:
        return False
    return os.path.exists(os.path.join(REPO, "knowledge", KN_DIRS[m.group(1)],
                                       ref + ".md"))


def _internal_ids() -> set[str]:
    """Stems of every identifier-bearing path (ledger records, tasks, ...)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import allocate_id  # noqa: E402  (shares the identifier-space scan)
    stems: set[str] = set()
    for path in allocate_id._identifier_paths():
        stems.add(allocate_id._record_identifier(path))
        stems.add(os.path.splitext(os.path.basename(path))[0])
    return stems


def check_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = {r.get("id") for r in rows}
    internal_ids: set[str] | None = None
    for r in rows:
        where = r["_path"]
        for field in REQUIRED:
            if field not in r:
                errors.append(f"{where}: missing required field '{field}'")
        rid = str(r.get("id") or "")
        stem = os.path.splitext(os.path.basename(where))[0]
        m = KR_ID.match(rid)
        if not m:
            errors.append(f"{where}: id '{rid}' is not KR-<AREA>-<6hex>")
        elif m.group(1) != AREAS.get(r["_area_dir"]):
            errors.append(f"{where}: id area {m.group(1)} does not match "
                          f"directory {r['_area_dir']} "
                          f"({AREAS.get(r['_area_dir'])})")
        if rid and rid != stem:
            errors.append(f"{where}: id '{rid}' != filename stem '{stem}'")
        if r.get("area") != r["_area_dir"]:
            errors.append(f"{where}: area '{r.get('area')}' != directory "
                          f"'{r['_area_dir']}'")
        if r.get("kind") not in KINDS:
            errors.append(f"{where}: kind '{r.get('kind')}' not in "
                          f"{sorted(KINDS)}")
        if r.get("status") not in STATUSES:
            errors.append(f"{where}: status '{r.get('status')}' not in "
                          f"{sorted(STATUSES)}")
        for field in ("title", "claim"):
            if not str(r.get(field) or "").strip():
                errors.append(f"{where}: '{field}' is empty")
        sources = r.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{where}: 'sources' must be a non-empty list")
            sources = []
        grounded = False
        for i, s in enumerate(sources):
            if not isinstance(s, dict):
                errors.append(f"{where}: sources[{i}] must be a mapping")
                continue
            ref = str(s.get("ref") or "")
            if not knowledge_ref_exists(ref):
                errors.append(f"{where}: sources[{i}].ref '{ref}' does not "
                              "resolve to a knowledge/ entry")
            state = s.get("verification_state")
            if state not in VERIFICATION_STATES:
                errors.append(f"{where}: sources[{i}].verification_state "
                              f"'{state}' not in {sorted(VERIFICATION_STATES)}")
            elif state != "recalled_unverified":
                grounded = True
            if not str(s.get("locator") or "").strip():
                errors.append(f"{where}: sources[{i}].locator is empty "
                              "(name the theorem/section/page, or 'abstract')")
        if sources and not grounded:
            errors.append(f"{where}: every source is recalled_unverified; a "
                          "row needs at least one source someone has read")
        fc = r.get("forecloses")
        if (not isinstance(fc, list) or not fc
                or not all(isinstance(x, str) and x.strip() for x in fc)):
            errors.append(f"{where}: 'forecloses' must be a non-empty list of "
                          "phrases an idea would use when re-deriving this")
        for field in ("dominated_by", "superseded_by"):
            val = r.get(field)
            if val not in (None, "") and val not in ids:
                errors.append(f"{where}: {field} '{val}' is not a row id")
        for i, o in enumerate(r.get("open") or []):
            if not knowledge_ref_exists(str(o)):
                errors.append(f"{where}: open[{i}] '{o}' does not resolve")
        internal = r.get("internal") or []
        if not isinstance(internal, list):
            errors.append(f"{where}: 'internal' must be a list")
            internal = []
        for i, item in enumerate(internal):
            if not isinstance(item, dict):
                errors.append(f"{where}: internal[{i}] must be a mapping")
                continue
            if item.get("relation") not in INTERNAL_RELATIONS:
                errors.append(f"{where}: internal[{i}].relation "
                              f"'{item.get('relation')}' not in "
                              f"{sorted(INTERNAL_RELATIONS)}")
            ref = str(item.get("ref") or "")
            if KN_REF.match(ref):
                if not knowledge_ref_exists(ref):
                    errors.append(f"{where}: internal[{i}].ref '{ref}' does "
                                  "not resolve")
                continue
            if internal_ids is None:
                internal_ids = _internal_ids()
            if ref not in internal_ids:
                errors.append(f"{where}: internal[{i}].ref '{ref}' is not an "
                              "identifier present in this checkout")
    seen: dict[str, str] = {}
    for r in rows:
        rid = r.get("id")
        if rid in seen:
            errors.append(f"{r['_path']}: duplicate id {rid} (also "
                          f"{seen[rid]})")
        seen[rid] = r["_path"]
    return errors


def _one_line(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().replace("|", "\\|")


KIND_ORDER = ["record", "known_bound", "known_mechanism", "known_negative",
              "dispute", "textbook_fact"]


def render(rows: list[dict[str, Any]], area: str | None = None) -> str:
    live = [r for r in rows if not r.get("superseded_by")]
    areas = [area] if area else list(AREAS)
    out = ["# ECDLP known-results map (generated -- do not edit)", "",
           "Rows live in `knowledge/frontiers/ecdlp/<area>/KR-*.yaml`; this "
           "file is rebuilt by `tools/build_frontier_map.py`. Superseded rows "
           "are omitted. **An idea whose claim or mechanism matches a row's "
           "claim or `forecloses` phrases is `novelty_status: known` (or "
           "`adaptation` if it changes the setting) and must cite the row.** "
           "Absence of a row is not evidence of novelty: the map is curated, "
           "not exhaustive.", ""]
    for a in areas:
        sel = [r for r in live if r.get("area") == a]
        sel.sort(key=lambda r: (KIND_ORDER.index(r.get("kind"))
                                if r.get("kind") in KIND_ORDER else 99,
                                str(r.get("id"))))
        out += [f"## {a} ({len(sel)} rows)", "",
                "| id | kind / status | claim | sources | forecloses |",
                "|---|---|---|---|---|"]
        for r in sel:
            srcs = ", ".join(
                f"{s.get('ref')} ({s.get('locator')}; "
                f"{s.get('verification_state')})"
                for s in (r.get("sources") or []) if isinstance(s, dict))
            fc = "; ".join(r.get("forecloses") or [])
            out.append(f"| {r.get('id')} | {r.get('kind')} / {r.get('status')}"
                       f" | **{_one_line(r.get('title'))}.** "
                       f"{_one_line(r.get('claim'))} | {_one_line(srcs)} | "
                       f"{_one_line(fc)} |")
        out.append("")
    return "\n".join(out)


STOP = set("a an and are as at be by for from in into is it its of on or "
           "over the to under via with without using use than that this "
           "these those we our".split())


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9^/+\-]+", text.lower())
            if t not in STOP and len(t) > 1}


def match(rows: list[dict[str, Any]], query: str, limit: int = 8
          ) -> list[tuple[float, dict[str, Any], list[str]]]:
    """Rank rows against a free-text idea description.

    Scoring is deliberately simple and explainable: query-token overlap with
    the row's forecloses phrases (weight 3), title (2) and claim (1), plus a
    bonus for every forecloses phrase contained verbatim in the query. A low
    score is NOT evidence of novelty; it means read the map by hand.
    """
    q = _tokens(query)
    ql = " ".join(query.lower().split())
    scored = []
    for r in rows:
        if r.get("superseded_by"):
            continue
        fc = [str(x) for x in (r.get("forecloses") or [])]
        hits = [p for p in fc if " ".join(p.lower().split()) in ql]
        score = (3 * len(q & _tokens(" ".join(fc)))
                 + 2 * len(q & _tokens(str(r.get("title") or "")))
                 + len(q & _tokens(str(r.get("claim") or "")))
                 + 5 * len(hits))
        if score:
            scored.append((float(score), r, hits))
    scored.sort(key=lambda t: (-t[0], str(t[1].get("id"))))
    return scored[:limit]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 tools/build_frontier_map.py",
        description="Render, check or search the ECDLP known-results map.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true",
                   help="validate every row (schema, ids, references); CI")
    g.add_argument("--match", metavar="TEXT",
                   help="rank rows against an idea's claim/mechanism text")
    ap.add_argument("--area", choices=sorted(AREAS),
                    help="render one area only")
    ap.add_argument("--out", metavar="PATH",
                    help="write the rendered map here instead of stdout")
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args(argv)
    rows = load_rows()
    if args.check:
        errors = check_rows(rows)
        for e in errors:
            print(e, file=sys.stderr)
        if errors:
            print(f"{len(errors)} error(s) in {len(rows)} known-result rows",
                  file=sys.stderr)
            return 1
        by_area = {a: sum(r.get("area") == a for r in rows) for a in AREAS}
        print(f"known-results map OK: {len(rows)} rows {by_area}")
        return 0
    if args.match:
        res = match(rows, args.match, args.limit)
        if not res:
            print("no row shares a term with the query -- this is NOT "
                  "evidence of novelty; read the rendered map")
            return 0
        for score, r, hits in res:
            print(f"{r['id']}  score={score:g}  [{r.get('kind')}/"
                  f"{r.get('status')}]  {_one_line(r.get('title'))}")
            if hits:
                print(f"    matched phrase(s): {'; '.join(hits)}")
            print(f"    sources: " + ", ".join(
                str(s.get('ref')) for s in r.get('sources') or []
                if isinstance(s, dict)))
        return 0
    text = render(rows, args.area)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {args.out} ({len(rows)} rows)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
