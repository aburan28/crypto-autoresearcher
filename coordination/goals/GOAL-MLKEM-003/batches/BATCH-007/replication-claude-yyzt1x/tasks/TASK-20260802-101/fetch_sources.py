#!/usr/bin/env python3
"""TASK-20260802-101 -- primary-source retrieval for the GOAL-MLKEM-003 falsification gate.

This is the exact retrieval script run for TASK-20260802-101. It performs every
network attempt that backs the adjudication, records the outcome of each attempt
(retrieved or unretrieved, with the exact error), and writes:

  inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json
  inputs/MLKEM-DUAL-SOURCES-20260802/extracts/*        (small text regions actually used)

Design rules imposed by the handoff (ledger/handoffs/TASK-20260802-101.yaml):

  * Every attempted source gets a record with url, http_status, retrieved_at
    (UTC), sha256, bytes, revision_id and retrieved|unretrieved. A source that
    cannot be fetched is recorded as unretrieved with its exact error; it is
    NEVER paraphrased from memory and is NEVER evidence for or against a
    finding (AGENTS.md rule 5).
  * Large binaries are hashed but not vendored. Only the small text regions the
    adjudication actually quotes are written under extracts/.
  * No adjudication logic lives here. This script retrieves and extracts; the
    verdicts are in source_adjudication.md / adjudication_results.json.
  * Outbound HTTPS goes through the session agent proxy. TLS verification is
    never disabled. Hosts denied by egress policy are reported, not routed
    around: in particular github.com / api.github.com returned a
    repository-scoped 403 from the proxy for kevin-carrier/CodedDualAttack, and
    this script does not substitute a sibling host to read that repository.

Full-object bytes are cached under CACHE_DIR (a scratch directory outside the
repository) so that a re-run is cheap; the sha256 recorded is always the sha256
of the complete retrieved object, whatever subset is vendored.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import html
import json
import os
import re
import subprocess
import sys

REPO = "/home/user/crypto-autoresearcher"
OUT_DIR = os.path.join(REPO, "inputs", "MLKEM-DUAL-SOURCES-20260802")
EXTRACT_DIR = os.path.join(OUT_DIR, "extracts")
CACHE_DIR = os.environ.get(
    "TASK101_CACHE",
    "/tmp/claude-0/-home-user-crypto-autoresearcher/"
    "6f974a8d-a1d9-5a78-a9b4-6eaac09bcaf4/scratchpad/task101cache",
)

# A plain, honest UA. No attempt is made to defeat a bot challenge.
UA = "crypto-autoresearcher/TASK-20260802-101 (+curl)"

RECORDS: list[dict] = []


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(source_id: str, url: str, *, revision_id: str, note: str = "",
          follow: bool = True, expect_pdf: bool = False) -> dict:
    """One HTTPS attempt. Returns the provenance record; caches the body.

    ``expect_pdf`` guards against the common failure where a publisher answers a
    PDF URL with HTTP 200 and a cookie-wall HTML page. Such a response is
    recorded as *unretrieved*: a 200 that does not carry the requested object is
    a failed retrieval, not a retrieval.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    body_path = os.path.join(CACHE_DIR, source_id + ".body")
    hdr_path = os.path.join(CACHE_DIR, source_id + ".hdr")
    cmd = ["curl", "-sS", "-A", UA, "-D", hdr_path, "-o", body_path,
           "-w", "%{http_code}|%{size_download}|%{content_type}|%{url_effective}"]
    if follow:
        cmd.append("-L")
    cmd.append(url)
    rec = {
        "source_id": source_id,
        "url": url,
        "revision_id": revision_id,
        "retrieved_at": utcnow(),
        "command": " ".join(cmd),
        "note": note,
    }
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        rec.update(status="unretrieved", http_status=None, sha256=None, bytes=None,
                   error=f"timeout after 180s: {exc}")
        RECORDS.append(rec)
        return rec
    if proc.returncode != 0:
        rec.update(status="unretrieved", http_status=None, sha256=None, bytes=None,
                   error=f"curl exit {proc.returncode}: {proc.stderr.strip()[:400]}")
        RECORDS.append(rec)
        return rec
    parts = proc.stdout.split("|")
    http_status = int(parts[0])
    content_type = parts[2].strip() if len(parts) > 2 else None
    url_effective = parts[3].strip() if len(parts) > 3 else url
    raw = open(body_path, "rb").read()
    rec.update(
        http_status=http_status,
        bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        content_type=content_type,
        url_effective=url_effective,
        cache_path=body_path,
    )
    if expect_pdf:
        rec["is_pdf"] = raw[:5] == b"%PDF-"
    if http_status == 200 and len(raw) > 0 and (not expect_pdf or rec.get("is_pdf")):
        rec["status"] = "retrieved"
    elif http_status == 200 and expect_pdf and not rec.get("is_pdf"):
        rec["status"] = "unretrieved"
        rec["error"] = (
            "HTTP 200 but the body is not a PDF (content_type=%s, first 5 bytes=%r); "
            "the server answered the PDF URL with an interstitial/cookie-wall page."
            % (content_type, raw[:5])
        )
    else:
        rec["status"] = "unretrieved"
        # Preserve the exact server-side explanation, truncated.
        snippet = raw[:400].decode("utf-8", "replace")
        mitigated = ""
        try:
            hdrs = open(hdr_path, encoding="utf-8", errors="replace").read()
            m = re.search(r"^cf-mitigated:\s*(\S+)", hdrs, re.M | re.I)
            if m:
                mitigated = f" [cf-mitigated: {m.group(1)}]"
        except OSError:
            pass
        rec["error"] = f"HTTP {http_status}{mitigated}; body[0:400]={snippet!r}"
    RECORDS.append(rec)
    print(f"[{rec['status']:11s}] {http_status} {len(raw):>9d}B  {source_id}", file=sys.stderr)
    return rec


def note_only(source_id: str, url: str, *, revision_id: str, status: str,
              error: str, note: str) -> dict:
    """A source that was deliberately NOT fetched, recorded with the reason."""
    rec = {
        "source_id": source_id,
        "url": url,
        "revision_id": revision_id,
        "retrieved_at": utcnow(),
        "command": None,
        "http_status": None,
        "bytes": None,
        "sha256": None,
        "status": status,
        "error": error,
        "note": note,
    }
    RECORDS.append(rec)
    return rec


def strip_html(raw: bytes) -> str:
    s = raw.decode("utf-8", "replace")
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "\n", s)
    s = html.unescape(s)
    return "\n".join(l.strip() for l in s.split("\n") if l.strip())


def write_extract(name: str, text: str) -> str:
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    path = os.path.join(EXTRACT_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"  -> extract {name} ({len(text.encode())}B)", file=sys.stderr)
    return path


def pdf_pages(path: str) -> list[str]:
    from pypdf import PdfReader
    reader = PdfReader(path)
    return [p.extract_text() or "" for p in reader.pages]


def pdf_meta(path: str) -> dict:
    from pypdf import PdfReader
    return {k: str(v) for k, v in (PdfReader(path).metadata or {}).items()}


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    # ---------------------------------------------------------------- Q1 side A
    # ePrint 2022/1750: abstract/metadata page (HTML) -- carries the revision
    # history line that pins the current revision.
    r = fetch("eprint-2022-1750-abstract", "https://eprint.iacr.org/2022/1750",
              revision_id="eprint:2022/1750 landing page as served on retrieval date",
              note="Authoritative ePrint metadata page: title, revision count/date, note field.")
    if r["status"] == "retrieved":
        txt = strip_html(open(r["cache_path"], "rb").read())
        # Keep the paper block only (from the title heading to the BibTeX block).
        i = txt.find("Paper 2022/1750")
        j = txt.find("Note: In order to protect the privacy")
        write_extract("eprint-2022-1750-abstract-page.txt",
                      txt[i if i >= 0 else 0: j if j > 0 else len(txt)])

    # ePrint revision-history listing (all versions with timestamps).
    fetch("eprint-2022-1750-versions", "https://eprint.iacr.org/archive/versions/2022/1750",
          revision_id="eprint:2022/1750 all-versions listing",
          note="Needed to enumerate exact per-revision timestamps and archive PDF URLs.")

    # ePrint current PDF (the object Q1 nominally wants).
    fetch("eprint-2022-1750-pdf", "https://eprint.iacr.org/2022/1750.pdf",
          revision_id="eprint:2022/1750 current revision PDF", expect_pdf=True)

    # Control: is the PDF block specific to this paper, or to all ePrint PDFs?
    fetch("eprint-2023-302-pdf-control", "https://eprint.iacr.org/2023/302.pdf",
          revision_id="eprint:2023/302 current revision PDF", expect_pdf=True,
          note="Control probe: establishes that the 403 is path-class-wide on ePrint, "
               "not specific to 2022/1750.")

    # ePrint search index entry -- independent confirmation of the last-updated date.
    r = fetch("eprint-search-coded-dual-attack",
              "https://eprint.iacr.org/search?q=coded+dual+attack",
              revision_id="eprint search index as served on retrieval date",
              note="Q3 literature sweep + independent 'Last updated' date for 2022/1750.")
    if r["status"] == "retrieved":
        raw = open(r["cache_path"], "rb").read().decode("utf-8", "replace")
        rows = []
        for m in re.finditer(
                r'class="paperlink" href="/(\d{4}/\d+)">.*?Last updated: ([\d-]+).*?<strong>(.*?)</strong>',
                raw, re.S):
            rows.append(f"{m.group(1)}  last_updated={m.group(2)}  "
                        f"{html.unescape(re.sub('<[^>]+>', '', m.group(3)))}")
        write_extract("eprint-search-coded-dual-attack-hits.txt", "\n".join(rows) + "\n")

    # ---------------------------------------------------------------- Q1 side B
    # HAL metadata for hal-05406481 -- pins the vendored artifact's deposit side.
    r = fetch("hal-05406481-api",
              "https://api.archives-ouvertes.fr/search/?q=halId_s:hal-05406481"
              "&fl=halId_s,version_i,title_s,submittedDate_s,modifiedDate_s,"
              "fileMain_s,files_s,label_s,producedDate_s&wt=json",
              revision_id="hal-05406481 (HAL API record)",
              note="Deposit version, dates and file URL for the vendored artifact.")
    if r["status"] == "retrieved":
        write_extract("hal-05406481-api.json",
                      open(r["cache_path"], encoding="utf-8", errors="replace").read())

    # HAL document PDF -- the live copy of the object the findings were derived from.
    r = fetch("hal-05406481-document", "https://hal.science/hal-05406481/document",
              revision_id="hal-05406481 v1 (deposited 2025-12-09)", expect_pdf=True,
              note="Full PDF; hashed but NOT vendored (already an immutable run artifact "
                   "at experiments/EXP-MLKEM-010/vendor-lock/). Only Table C.2 page and "
                   "the Fig 4.1 section are extracted.")
    if r["status"] == "retrieved":
        pdf_path = r["cache_path"] + ".pdf"
        os.replace(r["cache_path"], pdf_path)
        r["cache_path"] = pdf_path
        pages = pdf_pages(pdf_path)
        meta = pdf_meta(pdf_path)
        r["pdf_metadata"] = meta
        r["pdf_pages"] = len(pages)
        write_extract("carrier-hal-05406481-pdf-metadata.json",
                      json.dumps({"pages": len(pages), "metadata": meta}, indent=2) + "\n")
        # Title page (page 2; page 1 is the HAL cover sheet).
        write_extract("carrier-hal-05406481-p02-titlepage.txt", pages[1][:1200])
        # Table C.2 page.
        for idx, page in enumerate(pages):
            if "Table C.2" in page and "143.30" in page:
                write_extract("carrier-hal-05406481-p%02d-tableC1-C2.txt" % (idx + 1), page)
        # Fig 4.1 validation section.
        joined = "\n".join(pages)
        k = joined.find("Validating our Analysis Through Simulations")
        if k >= 0:
            end = joined.find("5 Application", k)
            write_extract("carrier-hal-05406481-fig4.1-validation-section.txt",
                          joined[k:end if end > k else k + 6000])

        # Independent cross-check of the vendored artifact under the SAME hash.
        vendored = os.path.join(REPO, "experiments", "EXP-MLKEM-010", "vendor-lock",
                                "Carrier-2022-1750-hal-05406481.pdf")
        if os.path.exists(vendored):
            vh = hashlib.sha256(open(vendored, "rb").read()).hexdigest()
            r["vendored_artifact_sha256"] = vh
            r["byte_identical_to_vendored_artifact"] = (vh == r["sha256"])

    # Published version of record (CRYPTO 2025) -- a third, independent revision.
    fetch("springer-chapter-landing",
          "https://link.springer.com/chapter/10.1007/978-3-032-01855-7_15",
          revision_id="Springer CRYPTO 2025 chapter, DOI 10.1007/978-3-032-01855-7_15")
    fetch("springer-chapter-pdf",
          "https://link.springer.com/content/pdf/10.1007/978-3-032-01855-7_15.pdf",
          revision_id="Springer CRYPTO 2025 chapter PDF (open access, CC BY)",
          expect_pdf=True)
    fetch("unpaywall-978-3-032-01855-7_15",
          "https://api.unpaywall.org/v2/10.1007/978-3-032-01855-7_15?email=info@adamburan.com",
          revision_id="Unpaywall OA-location index",
          note="Enumerates every OA host for the published version.")
    fetch("semanticscholar-978-3-032-01855-7_15",
          "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/978-3-032-01855-7_15"
          "?fields=title,externalIds,openAccessPdf,year,venue",
          revision_id="Semantic Scholar record")

    # ------------------------------------------------------------------- Q2
    # kevin-carrier/CodedDualAttack. Both GitHub hosts are denied for this
    # session by egress policy; recorded and NOT routed around.
    fetch("github-api-CodedDualAttack",
          "https://api.github.com/repos/kevin-carrier/CodedDualAttack",
          revision_id="repository HEAD (unknown -- not obtained)")
    fetch("github-api-CodedDualAttack-commits",
          "https://api.github.com/repos/kevin-carrier/CodedDualAttack/commits?per_page=3",
          revision_id="repository HEAD commit list (unknown -- not obtained)")
    fetch("github-web-CodedDualAttack",
          "https://github.com/kevin-carrier/CodedDualAttack",
          revision_id="repository HEAD (unknown -- not obtained)")
    fetch("github-api-numpy-control", "https://api.github.com/repos/numpy/numpy",
          revision_id="n/a (control probe)",
          note="Control probe: establishes the GitHub denial is session-wide, not a "
               "property of the CodedDualAttack repository or a transient error.")
    note_only(
        "raw-githubusercontent-CodedDualAttack",
        "https://raw.githubusercontent.com/kevin-carrier/CodedDualAttack/main/verifyModel/FFT_sample.py",
        revision_id="repository HEAD (unknown -- not obtained)",
        status="not_attempted",
        error=("Deliberately not fetched. The session carries an explicit "
               "repository-scoped GitHub access denial (see github-* records). "
               "/root/.ccr/README.md instructs that a proxy 403 must be reported, "
               "not routed around, so a sibling host was not used to read the same "
               "repository. Independently, the handoff requires the observed HEAD "
               "commit SHA, which raw.githubusercontent.com cannot supply."),
        note=("Remedy for a follow-up task: obtain GitHub access for "
              "kevin-carrier/CodedDualAttack (add_repo) and re-run Q2."))

    # ------------------------------------------------------------------- Q3
    # Ducas-Pulles CRYPTO 2023 (the heuristics objection).
    fetch("eprint-2023-302-abstract", "https://eprint.iacr.org/2023/302",
          revision_id="eprint:2023/302 landing page as served on retrieval date")
    r = fetch("cwi-33407-ducas-pulles-2023", "https://ir.cwi.nl/pub/33407/33407.pdf",
              revision_id="CWI repository copy of Ducas-Pulles, CRYPTO 2023", expect_pdf=True,
              note="Full PDF hashed, not vendored; only the Section 5 experiments "
                   "region is extracted.")
    if r["status"] == "retrieved":
        p = r["cache_path"] + ".pdf"
        os.replace(r["cache_path"], p)
        r["cache_path"] = p
        joined = "\n".join(pdf_pages(p))
        k = joined.find("5.2 Distribution of Scores of Uniform Targets")
        if k >= 0:
            end = joined.find("Conclusion. All in all", k)
            write_extract("ducas-pulles-2023-sec5.2-5.3-excerpt.txt",
                          joined[k:end + 600 if end > k else k + 7000])
        # Record whether the Carrier-specific quantity appears at all.
        r["mentions_Pwrong_token"] = "Pwrong" in joined
        r["mentions_Carrier"] = "Carrier" in joined

    # Pouly-Shen EUROCRYPT 2024, provable dual attack (post-objection line).
    r = fetch("hal-04827068-pouly-shen-2024", "https://inria.hal.science/hal-04827068/document",
              revision_id="hal-04827068 v1 (submitted 2024-12-09)", expect_pdf=True)
    if r["status"] == "retrieved":
        p = r["cache_path"] + ".pdf"
        os.replace(r["cache_path"], p)
        r["cache_path"] = p
        joined = "\n".join(pdf_pages(p))
        r["mentions_Pwrong_token"] = "Pwrong" in joined
        r["mentions_Carrier"] = "Carrier" in joined

    # MATZOV 2022 technical report.
    r = fetch("zenodo-6493704-matzov",
              "https://zenodo.org/api/records/6493704/files/"
              "Report%20on%20the%20Security%20of%20LWE%20updated.pdf/content",
              revision_id="Zenodo record 6493704 (DOI 10.5281/zenodo.6493704), 'updated' file",
              expect_pdf=True)
    if r["status"] == "retrieved":
        p = r["cache_path"] + ".pdf"
        os.replace(r["cache_path"], p)
        r["cache_path"] = p
        joined = "\n".join(pdf_pages(p))
        r["mentions_Pwrong_token"] = "Pwrong" in joined

    # Guo-Johansson ASIACRYPT 2021 (the other dual-attack claim).
    fetch("eprint-2021-948-abstract", "https://eprint.iacr.org/2021/948",
          revision_id="eprint:2021/948 landing page as served on retrieval date")
    fetch("eprint-2021-948-pdf", "https://eprint.iacr.org/2021/948.pdf",
          revision_id="eprint:2021/948 current revision PDF", expect_pdf=True)
    fetch("lup-guo-johansson-record",
          "https://lup.lub.lu.se/record/292b3d98-754c-414d-95db-ee38806157f9",
          revision_id="Lund University Publications record",
          note="Checked for an OA full text; none linked.")

    # Newer work citing the Carrier variant (Q3 sweep).
    for pid in ("2026/599", "2026/1400", "2026/1326"):
        sid = "eprint-%s-abstract" % pid.replace("/", "-")
        r = fetch(sid, "https://eprint.iacr.org/%s" % pid,
                  revision_id="eprint:%s landing page as served on retrieval date" % pid,
                  note="Q3 sweep: recent paper surfaced by the ePrint search for "
                       "coded/dual attacks on LWE.")
        if r["status"] == "retrieved":
            txt = strip_html(open(r["cache_path"], "rb").read())
            i = txt.find("Paper %s" % pid)
            j = txt.find("Note: In order to protect the privacy")
            write_extract("eprint-%s-abstract.txt" % pid.replace("/", "-"),
                          txt[i if i >= 0 else 0: j if j > 0 else len(txt)])
        fetch(sid.replace("-abstract", "-pdf"), "https://eprint.iacr.org/%s.pdf" % pid,
              revision_id="eprint:%s current revision PDF" % pid, expect_pdf=True)

    r = fetch("semanticscholar-citations-carrier",
              "https://api.semanticscholar.org/graph/v1/paper/"
              "DOI:10.1007/978-3-032-01855-7_15/citations"
              "?fields=title,year,venue,externalIds,openAccessPdf&limit=100",
              revision_id="Semantic Scholar citation edges as served on retrieval date")
    if r["status"] == "retrieved":
        write_extract("semanticscholar-citations-carrier.json",
                      open(r["cache_path"], encoding="utf-8", errors="replace").read())

    # Wayback: an archived copy of the ePrint PDF would settle Q1 on ePrint bytes.
    fetch("wayback-availability-eprint-pdf",
          "https://archive.org/wayback/available?url=eprint.iacr.org/2022/1750.pdf",
          revision_id="Wayback availability index")
    fetch("wayback-cdx-eprint-pdf",
          "http://web.archive.org/cdx/search/cdx?url=eprint.iacr.org/2022/1750.pdf"
          "&output=json&limit=30",
          revision_id="Wayback CDX index for the ePrint PDF")
    fetch("wayback-snapshot-eprint-pdf",
          "http://web.archive.org/web/20260114001146/https://eprint.iacr.org/2022/1750.pdf",
          revision_id="Wayback snapshot 20260114001146 of eprint.iacr.org/2022/1750.pdf",
          expect_pdf=True,
          note="The snapshot named by the archive.org availability API; would give "
               "ePrint-hosted bytes for the current revision if reachable.")

    # ----------------------------------------------------- handoff priority (2)
    fetch("nist-fips-203", "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf",
          revision_id="FIPS 203 (final, published 2024-08-13)", expect_pdf=True,
          note="Handoff priority (2). Retrieved for provenance completeness; the "
               "adjudication of Q1/Q2/Q3 does not depend on it.")
    fetch("nist-fips-203-landing", "https://csrc.nist.gov/pubs/fips/203/final",
          revision_id="CSRC landing page for FIPS 203 (final)")

    # ------------------------------------------------------------------ output
    env = {
        "retrieved_at_utc": utcnow(),
        "curl_version": subprocess.run(["curl", "--version"], capture_output=True,
                                       text=True).stdout.splitlines()[0],
        "python": sys.version.split()[0],
        "git_commit": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                                     capture_output=True, text=True).stdout.strip(),
        "https_proxy_configured": bool(os.environ.get("HTTPS_PROXY")),
        "tls_verification": "enabled (agent-proxy CA bundle /root/.ccr/ca-bundle.crt)",
    }
    try:
        from pypdf import __version__ as _pv
        env["pypdf"] = _pv
    except Exception:
        env["pypdf"] = None

    doc = {
        "task_id": "TASK-20260802-101",
        "goal_id": "GOAL-MLKEM-003",
        "batch_id": "BATCH-007",
        "generated_by": os.path.basename(__file__),
        "environment": env,
        "counts": {
            "attempted": len(RECORDS),
            "retrieved": sum(1 for r in RECORDS if r["status"] == "retrieved"),
            "unretrieved": sum(1 for r in RECORDS if r["status"] == "unretrieved"),
            "not_attempted": sum(1 for r in RECORDS if r["status"] == "not_attempted"),
        },
        "sources": RECORDS,
    }
    with open(os.path.join(OUT_DIR, "provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print(json.dumps(doc["counts"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
