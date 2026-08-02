#!/usr/bin/env python3
"""TASK-20260802-101 addendum: correct the Guo-Johansson source identification.

The first pass of fetch_sources.py attempted https://eprint.iacr.org/2021/948
for source (5), Guo-Johansson.  The retrieved landing page shows that this
identifier belongs to an unrelated paper ("How to Make a Secure Index for
Searchable Symmetric Encryption, Revisited", Watanabe et al.), i.e. the ePrint
number was a guess and not a verified identifier.  The program's own literature
record KN-LIT-109 carries `eprint: null` and DOI 10.1007/978-3-030-92068-5_2.

This addendum therefore (a) records the misidentification as a fact of the run,
and (b) makes correctly-targeted attempts for Guo-Johansson via the DOI.  It
appends its attempts to provenance.json under `addendum_attempts`; it does not
rewrite any record produced by the first pass.

Usage: python3 fetch_addendum.py [--work DIR]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[6]
OUT_ROOT = REPO_ROOT / "inputs" / "MLKEM-DUAL-SOURCES-20260802"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36")

ATTEMPTS = [
    dict(id="guo-johansson-openalex",
         url="https://api.openalex.org/works/doi:10.1007/978-3-030-92068-5_2",
         save="guo-johansson-2021/openalex_work.json", kind="json",
         purpose="enumerate open-access full-text locations for KN-LIT-109"),
    dict(id="guo-johansson-eprint-search",
         url="https://eprint.iacr.org/search?q=Faster+Dual+Lattice+Attacks+for+"
             "Solving+LWE+with+Applications+to+CRYSTALS",
         save="guo-johansson-2021/eprint_search.html", kind="html",
         purpose="check whether an ePrint version of KN-LIT-109 exists"),
    dict(id="eprint-2021-948-identity-check",
         url="https://eprint.iacr.org/2021/948",
         save=None, kind="html",
         purpose="record that this identifier is NOT Guo-Johansson"),
]

CHALLENGE = (b"Just a moment...", b"not a bot", b"Protected by Anubis")


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(attempt, work: pathlib.Path):
    body = work / ("addendum_" + attempt["id"] + ".bin")
    cmd = ["curl", "-sSL", "-A", UA, "--max-time", "180", "-o", str(body),
           "-w", "%{http_code}\t%{size_download}\t%{content_type}\t%{url_effective}",
           attempt["url"]]
    started = utcnow()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    rec = dict(source_id=attempt["id"], url=attempt["url"],
               purpose=attempt["purpose"], retrieved_at=started,
               command=" ".join(cmd), curl_exit=proc.returncode,
               curl_stderr=proc.stderr.strip() or None)
    if proc.returncode != 0 or "\t" not in proc.stdout:
        rec.update(status="unretrieved", http_status=None, bytes=None,
                   sha256=None,
                   unretrieved_reason=proc.stderr.strip() or "curl failed")
        return rec, b""
    code, size, ctype, eff = proc.stdout.split("\t")
    raw = body.read_bytes() if body.exists() else b""
    rec.update(http_status=int(code), bytes=len(raw), content_type=ctype,
               effective_url=eff,
               sha256=hashlib.sha256(raw).hexdigest() if raw else None)
    ch = next((m.decode() for m in CHALLENGE if m in raw[:20000]), None)
    if rec["http_status"] != 200:
        rec.update(status="unretrieved", unretrieved_reason="HTTP %s" % code)
    elif ch:
        rec.update(status="unretrieved",
                   unretrieved_reason="HTTP 200 bot-challenge interstitial (%s);"
                                      " not circumvented" % ch)
    else:
        rec["status"] = "retrieved"
    if attempt.get("save") and raw:
        dest = OUT_ROOT / attempt["save"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        rec["vendored_path"] = str(dest.relative_to(REPO_ROOT))
    return rec, raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="/tmp/task-20260802-101-work")
    args = ap.parse_args()
    work = pathlib.Path(args.work)
    work.mkdir(parents=True, exist_ok=True)

    records, oa_locations = [], None
    for attempt in ATTEMPTS:
        rec, raw = fetch(attempt, work)
        if attempt["id"] == "guo-johansson-openalex" and rec["status"] == "retrieved":
            doc = json.loads(raw)
            oa_locations = [dict(is_oa=l.get("is_oa"),
                                 landing_page_url=l.get("landing_page_url"),
                                 pdf_url=l.get("pdf_url"),
                                 version=l.get("version"),
                                 source=(l.get("source") or {}).get("display_name"))
                            for l in doc.get("locations", [])]
            rec["openalex_title"] = doc.get("title")
            rec["openalex_locations"] = oa_locations
            rec["openalex_is_oa"] = (doc.get("open_access") or {}).get("is_oa")
        if attempt["id"] == "eprint-2021-948-identity-check" and raw:
            import re
            import html as _html
            flat = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ",
                          raw.decode("utf-8", "replace"))))
            m = re.search(r"Paper 2021/948 (.{0,120}?) [A-Z][a-z]+ [A-Z]", flat)
            rec["paper_title_at_this_identifier"] = m.group(1).strip() if m else None
            rec["is_guo_johansson"] = False
        records.append(rec)
        print("[%-11s] %s %s" % (rec["status"], rec.get("http_status"), rec["url"]))

    # any OA pdf url OpenAlex reports gets one honest attempt
    for loc in (oa_locations or []):
        if loc.get("is_oa") and loc.get("pdf_url"):
            rec, _ = fetch(dict(id="guo-johansson-oa-pdf", url=loc["pdf_url"],
                                save="guo-johansson-2021/oa_pdf_attempt.body",
                                kind="pdf",
                                purpose="Guo-Johansson full text via OpenAlex OA "
                                        "location"), work)
            records.append(rec)
            print("[%-11s] %s %s" % (rec["status"], rec.get("http_status"),
                                     rec["url"]))

    prov_path = OUT_ROOT / "provenance.json"
    prov = json.loads(prov_path.read_text())
    prov.setdefault("addendum_attempts", []).extend(records)
    prov["addendum_note"] = (
        "Source (5) Guo-Johansson: the first pass attempted "
        "https://eprint.iacr.org/2021/948, an ePrint number that was NOT verified "
        "against any retrieved source. The retrieved landing page shows that "
        "identifier belongs to an unrelated paper, so that attempt must not be "
        "read as a Guo-Johansson retrieval. KN-LIT-109 records eprint: null and "
        "DOI 10.1007/978-3-030-92068-5_2; the attempts below target that DOI.")
    prov["addendum_generated_at"] = utcnow()
    prov["addendum_generator"] = (
        "coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/"
        "TASK-20260802-101/fetch_addendum.py")
    prov_path.write_text(json.dumps(prov, indent=2) + "\n")
    print("updated %s" % prov_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
