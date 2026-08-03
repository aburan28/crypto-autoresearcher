#!/usr/bin/env python3
"""TASK-20260802-101 post-pass: add `revision_id` to every provenance record.

The handoff asks that each provenance entry carry a revision identifier.  This
script derives one for every attempt *from artifacts already retrieved* -- the
ePrint landing pages and OAI record, the HAL API record, the OpenAlex/Semantic
Scholar/Zenodo records, the PDF metadata captured in source_reads.json, and the
`git ls-remote` output -- and records, per attempt, the basis it used.  It
invents nothing: where no identifier is derivable (typically a request refused
before any content was served) it writes `revision_id: null` with an explicit
basis string.

It adds fields only; it does not alter any existing field.

Usage: python3 annotate_revisions.py
"""

from __future__ import annotations

import datetime as _dt
import html as _html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[6]
OUT = REPO_ROOT / "inputs" / "MLKEM-DUAL-SOURCES-20260802"


def text_of(path: pathlib.Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    flat = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", _html.unescape(flat))


def eprint_history(rel: str) -> str | None:
    p = OUT / rel
    if not p.exists():
        return None
    flat = text_of(p)
    m = re.search(r"History (.{0,180}?) (?:See all versions|Short URL)", flat)
    return m.group(1).strip() if m else None


def main() -> int:
    prov_path = OUT / "provenance.json"
    prov = json.loads(prov_path.read_text())
    reads = json.loads((OUT / "source_reads.json").read_text())

    # --- identifiers derived from retrieved artifacts -----------------------
    oai = None
    p = OUT / "eprint-2022-1750" / "oai_getrecord.xml"
    if p.exists():
        m = re.search(r"<datestamp>([^<]+)</datestamp>", p.read_text())
        oai = m.group(1) if m else None
    hist_1750 = eprint_history("eprint-2022-1750/landing.html")
    hist_302 = eprint_history("eprint-2023-302/landing.html")
    hist_948 = eprint_history("eprint-2021-948/landing.html")

    hal = (reads.get("q1_current_revision_metadata") or {}).get("hal_record") or {}
    hal_id = ("HAL %s v%s, submitted %s, file %s"
              % (hal.get("halId_s"), hal.get("version_i"),
                 hal.get("submittedDate_s"),
                 (hal.get("files_s") or [None])[0])) if hal else None

    def json_field(rel, *keys):
        q = OUT / rel
        if not q.exists():
            return None
        try:
            doc = json.loads(q.read_text())
        except Exception:
            return None
        for k in keys:
            doc = doc.get(k) if isinstance(doc, dict) else None
            if doc is None:
                return None
        return doc

    openalex_id = json_field("eprint-2022-1750/openalex_work.json", "id")
    openalex_upd = json_field("eprint-2022-1750/openalex_work.json", "updated_date")
    s2_id = json_field("eprint-2022-1750/semanticscholar.json", "paperId")
    zen_upd = json_field("matzov-2022/zenodo_record.json", "updated")
    zen_created = json_field("matzov-2022/zenodo_record.json", "created")
    gj_openalex = json_field("guo-johansson-2021/openalex_work.json", "id")
    gj_upd = json_field("guo-johansson-2021/openalex_work.json", "updated_date")

    corpus = reads.get("q3_other_sources") or {}
    fips_meta = (corpus.get("fips203-pdf") or {}).get("pdf_metadata") or {}
    matz_meta = (corpus.get("matzov-pdf") or {}).get("pdf_metadata") or {}
    head = (prov.get("code_repository") or {}).get("head_commit")

    eprint_1750 = ("ePrint 2022/1750, current revision as of retrieval: %s"
                   % hist_1750 + (
                       "; OAI-PMH datestamp %s" % oai if oai else ""))
    refused = ("not derivable: the request was refused before any content was "
               "served, so no revision identifier exists for this attempt")

    MAP = {
        "eprint-2022-1750-landing": (eprint_1750, "landing page History block"),
        "eprint-2022-1750-pdf": (eprint_1750 + " [TARGET, not retrieved]",
                                 "target revision from the landing page/OAI record"),
        "eprint-2022-1750-versions": (eprint_1750 + " [TARGET, not retrieved]",
                                      "target revision from the landing page/OAI record"),
        "eprint-2022-1750-oai": (eprint_1750, "OAI-PMH <datestamp>"),
        "hal-05406481-api": (hal_id, "HAL API record fields"),
        "hal-05406481-document": (hal_id + " [TARGET, not retrieved]" if hal_id else None,
                                  "target deposit version from the HAL API record"),
        "hal-05406481-file": (hal_id + " [TARGET, not retrieved]" if hal_id else None,
                              "target deposit version from the HAL API record"),
        "openalex-work": ("OpenAlex %s, updated_date %s" % (openalex_id, openalex_upd),
                          "OpenAlex record id + updated_date"),
        "semanticscholar-work": ("Semantic Scholar paperId %s" % s2_id,
                                 "Semantic Scholar paperId (no version field exposed)"),
        "springer-chapter": ("Springer chapter DOI 10.1007/978-3-032-01855-7_15 "
                             "(CRYPTO 2025 published version; landing page only, "
                             "no full text)",
                             "DOI of the published version"),
        "wayback-cdx-eprint-pdf": (None, refused),
        "fips203-landing": ("NIST FIPS 203 (final) publication landing page, "
                            "retrieved 2026-08-02",
                            "csrc.nist.gov landing page for the final publication"),
        "fips203-pdf": ("NIST FIPS 203 PDF, /CreationDate %s, /ModDate %s"
                        % (fips_meta.get("/CreationDate"), fips_meta.get("/ModDate")),
                        "embedded PDF metadata of the retrieved file"),
        "eprint-2023-302-landing": ("ePrint 2023/302, history: %s" % hist_302,
                                    "landing page History block"),
        "eprint-2023-302-pdf": ("ePrint 2023/302, history: %s [TARGET, not retrieved]"
                                % hist_302, "target revision from the landing page"),
        "matzov-zenodo-record": ("Zenodo record 6412487, created %s, updated %s"
                                 % (zen_created, zen_upd),
                                 "Zenodo record timestamps"),
        "matzov-pdf": ("MATZOV report PDF, /CreationDate %s"
                       % matz_meta.get("/CreationDate"),
                       "embedded PDF metadata of the retrieved file"),
        "eprint-2021-948-landing": ("ePrint 2021/948, history: %s -- NOTE: this "
                                    "identifier is NOT Guo-Johansson" % hist_948,
                                    "landing page History block"),
        "eprint-2021-948-pdf": ("ePrint 2021/948 [TARGET, not retrieved; and NOT "
                                "Guo-Johansson]", "see the landing-page identity check"),
        "github-api-repo": (None, refused),
        "github-web-repo": (None, refused),
        "codeload-tarball": (None, refused),
        "raw-readme-main": ("kevin-carrier/CodedDualAttack ref main (= %s); the "
                            "repository has no README.md at any ref" % head,
                            "git ls-remote + the tracked-file manifest of the clone"),
        "raw-readme-master": ("kevin-carrier/CodedDualAttack ref master; ls-remote "
                              "advertises only refs/heads/main (= %s)" % head,
                              "git ls-remote"),
        "raw-fft-sample-main": ("kevin-carrier/CodedDualAttack ref main = commit %s"
                                % head, "git ls-remote + clone head"),
        "guo-johansson-openalex": ("OpenAlex %s, updated_date %s" % (gj_openalex, gj_upd),
                                   "OpenAlex record id + updated_date"),
        "guo-johansson-eprint-search": ("ePrint search endpoint result set as of "
                                        "2026-08-02 (query snapshot, no revision)",
                                        "query snapshot; a search page has no revision"),
        "eprint-2021-948-identity-check": ("ePrint 2021/948, history: %s" % hist_948,
                                           "landing page History block"),
    }

    annotated = 0
    for rec in prov.get("attempts", []) + prov.get("addendum_attempts", []):
        rid, basis = MAP.get(rec["source_id"], (None, "no mapping declared"))
        rec["revision_id"] = rid
        rec["revision_id_basis"] = basis
        annotated += 1

    if prov.get("code_repository"):
        prov["code_repository"]["revision_id"] = (
            "kevin-carrier/CodedDualAttack HEAD = refs/heads/main = %s "
            "(commit date %s)" % (head, prov["code_repository"].get("head_commit_date")))
        prov["code_repository"]["revision_id_basis"] = "git ls-remote + shallow clone"
    for art in prov.get("local_artifacts", []):
        meta = art.get("pdf_metadata") or {}
        art["revision_id"] = (
            "HAL hal-05406481 v1 deposit copy; embedded PDF /ModDate %s "
            "(HAL cover-page /CreationDate %s is the download stamp)"
            % (meta.get("/ModDate"), meta.get("/CreationDate")))
        art["revision_id_basis"] = "embedded PDF metadata + HAL API record"

    prov["revision_annotation_generated_at"] = _dt.datetime.now(
        _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prov["revision_annotation_generator"] = (
        "coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/"
        "TASK-20260802-101/annotate_revisions.py")
    prov_path.write_text(json.dumps(prov, indent=2) + "\n")
    print("annotated %d attempt records" % annotated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
