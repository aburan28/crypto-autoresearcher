#!/usr/bin/env python3
"""TASK-20260802-101 -- primary-source retrieval and source reads for GOAL-MLKEM-003.

Retrieves (or records the failure to retrieve) the primary sources behind the
program's standing Carrier findings, and performs the *reads* the three
adjudication questions need.  It performs no experiment, fits no model and
draws no conclusion: every number it emits is either a byte-level fact about a
retrieved artifact, or a direct read of a retrieved artifact's contents.

Outputs (all inside the task's declared write scope):

  inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json   one record per attempt
  inputs/MLKEM-DUAL-SOURCES-20260802/source_reads.json machine-readable reads
  inputs/MLKEM-DUAL-SOURCES-20260802/extracts/...      the text regions used

Large binaries (FIPS 203 PDF, MATZOV PDF) are downloaded to a work directory
outside the repository; only their provenance and the extracted regions
actually used are vendored.  The Carrier full text is NOT re-vendored: the
run-immutable copy at experiments/EXP-MLKEM-010/vendor-lock/ is opened
read-only and only text regions are extracted from it.

Usage:  python3 fetch_sources.py [--work DIR] [--skip-network]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[6]
OUT_ROOT = REPO_ROOT / "inputs" / "MLKEM-DUAL-SOURCES-20260802"
EXTRACTS = OUT_ROOT / "extracts"

CARRIER_VENDOR_PDF = (
    REPO_ROOT
    / "experiments"
    / "EXP-MLKEM-010"
    / "vendor-lock"
    / "Carrier-2022-1750-hal-05406481.pdf"
)

# A plain desktop-browser UA.  No attempt is made to defeat any bot challenge:
# a challenge response is recorded as `unretrieved`, never worked around.
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# attempt table: every URL this task tried, in the handoff's preference order
# ---------------------------------------------------------------------------
ATTEMPTS = [
    # (1) ePrint 2022/1750 -- Carrier-Meyer-Hilfiger-Shen-Tillich
    dict(id="eprint-2022-1750-landing", url="https://eprint.iacr.org/2022/1750",
         save="eprint-2022-1750/landing.html", kind="html",
         purpose="current revision history + authors' version note (Q1)"),
    dict(id="eprint-2022-1750-pdf", url="https://eprint.iacr.org/2022/1750.pdf",
         save="eprint-2022-1750/pdf_attempt.body", kind="pdf",
         purpose="current-revision full text (Q1) -- byte-level check"),
    dict(id="eprint-2022-1750-versions",
         url="https://eprint.iacr.org/archive/versions/2022/1750",
         save="eprint-2022-1750/versions_attempt.body", kind="html",
         purpose="per-revision list (Q1)"),
    dict(id="eprint-2022-1750-oai",
         url=("https://eprint.iacr.org/oai?verb=GetRecord&identifier="
              "oai:eprint.iacr.org:2022/1750&metadataPrefix=oai_dc"),
         save="eprint-2022-1750/oai_getrecord.xml", kind="xml",
         purpose="machine-readable datestamp of the current revision (Q1)"),
    dict(id="hal-05406481-api",
         url=("https://api.archives-ouvertes.fr/search/?q=halId_s:hal-05406481"
              "&fl=halId_s,version_i,title_s,submittedDate_s,modifiedDate_s,"
              "fileMain_s,files_s,label_s,doiId_s&wt=json"),
         save="eprint-2022-1750/hal_api_record.json", kind="json",
         purpose="identity/version of the vendored HAL deposit (Q1 baseline)"),
    dict(id="hal-05406481-document", url="https://hal.science/hal-05406481/document",
         save="eprint-2022-1750/hal_document_attempt.body", kind="pdf",
         purpose="fresh copy of the vendored full text (Q1)"),
    dict(id="hal-05406481-file",
         url="https://hal.science/hal-05406481/file/2022-1750.pdf",
         save="eprint-2022-1750/hal_file_attempt.body", kind="pdf",
         purpose="fresh copy of the vendored full text, direct file URL (Q1)"),
    dict(id="openalex-work",
         url="https://api.openalex.org/works/doi:10.1007/978-3-032-01855-7_15",
         save="eprint-2022-1750/openalex_work.json", kind="json",
         purpose="enumerate every open-access full-text location (Q1)"),
    dict(id="semanticscholar-work",
         url=("https://api.semanticscholar.org/graph/v1/paper/"
              "DOI:10.1007/978-3-032-01855-7_15?fields=title,openAccessPdf,"
              "externalIds,isOpenAccess"),
         save="eprint-2022-1750/semanticscholar.json", kind="json",
         purpose="independent open-access location check (Q1)"),
    dict(id="springer-chapter",
         url="https://link.springer.com/chapter/10.1007/978-3-032-01855-7_15",
         save="eprint-2022-1750/springer_landing.html", kind="html",
         purpose="published CRYPTO 2025 version landing page (Q1)"),
    dict(id="wayback-cdx-eprint-pdf",
         url=("http://web.archive.org/cdx/search/cdx?url=eprint.iacr.org/2022/"
              "1750.pdf&output=json&limit=20"),
         save="eprint-2022-1750/wayback_cdx_attempt.body", kind="json",
         purpose="archived copy of the ePrint PDF (Q1 fallback)"),
    # (2) NIST FIPS 203
    dict(id="fips203-landing", url="https://csrc.nist.gov/pubs/fips/203/final",
         save="fips203/landing.html", kind="html",
         purpose="ML-KEM standard, publication record"),
    dict(id="fips203-pdf",
         url="https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf",
         save=None, kind="pdf", work_only=True,
         purpose="ML-KEM standard full text (Q3 corpus check)"),
    # (3) Ducas-Pulles ePrint 2023/302
    dict(id="eprint-2023-302-landing", url="https://eprint.iacr.org/2023/302",
         save="eprint-2023-302/landing.html", kind="html",
         purpose="dual-sieve heuristic objections, metadata + abstract (Q3)"),
    dict(id="eprint-2023-302-pdf", url="https://eprint.iacr.org/2023/302.pdf",
         save="eprint-2023-302/pdf_attempt.body", kind="pdf",
         purpose="Ducas-Pulles full text (Q3)"),
    # (4) MATZOV 2022
    dict(id="matzov-zenodo-record", url="https://zenodo.org/api/records/6412487",
         save="matzov-2022/zenodo_record.json", kind="json",
         purpose="MATZOV report provenance"),
    dict(id="matzov-pdf",
         url=("https://zenodo.org/api/records/6412487/files/"
              "Report%20on%20the%20Security%20of%20LWE.pdf/content"),
         save=None, kind="pdf", work_only=True,
         purpose="MATZOV full text (Q3)"),
    # (5) Guo-Johansson
    dict(id="eprint-2021-948-landing", url="https://eprint.iacr.org/2021/948",
         save="eprint-2021-948/landing.html", kind="html",
         purpose="Guo-Johansson dual attack, metadata + abstract (Q3)"),
    dict(id="eprint-2021-948-pdf", url="https://eprint.iacr.org/2021/948.pdf",
         save="eprint-2021-948/pdf_attempt.body", kind="pdf",
         purpose="Guo-Johansson full text (Q3)"),
    # code: kevin-carrier/CodedDualAttack (Q2)
    dict(id="github-api-repo",
         url="https://api.github.com/repos/kevin-carrier/CodedDualAttack",
         save="codeddualattack/github_api_attempt.json", kind="json",
         purpose="repository head metadata (Q2)"),
    dict(id="github-web-repo",
         url="https://github.com/kevin-carrier/CodedDualAttack",
         save="codeddualattack/github_web_attempt.body", kind="html",
         purpose="repository web page (Q2)"),
    dict(id="codeload-tarball",
         url=("https://codeload.github.com/kevin-carrier/CodedDualAttack/"
              "tar.gz/refs/heads/main"),
         save=None, kind="bin", work_only=True,
         purpose="repository tarball at head (Q2)"),
    dict(id="raw-readme-main",
         url=("https://raw.githubusercontent.com/kevin-carrier/CodedDualAttack/"
              "main/README.md"),
         save=None, kind="text", work_only=True,
         purpose="branch-name probe recorded in the handoff (Q2)"),
    dict(id="raw-readme-master",
         url=("https://raw.githubusercontent.com/kevin-carrier/CodedDualAttack/"
              "master/README.md"),
         save=None, kind="text", work_only=True,
         purpose="branch-name probe recorded in the handoff (Q2)"),
    dict(id="raw-fft-sample-main",
         url=("https://raw.githubusercontent.com/kevin-carrier/CodedDualAttack/"
              "main/verifyModel/ScoreExperimentalDistribution/FFT_sample.py"),
         save="codeddualattack/FFT_sample.raw-main.py", kind="text",
         purpose="Pwrong/Pgood score paths at the current default branch (Q2)"),
]

BOT_CHALLENGE_MARKERS = (
    b"Just a moment...",
    b"Making sure you&#39;re not a bot",
    b"Making sure you're not a bot",
    b"Protected by Anubis",
    b"cf-browser-verification",
)


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def fetch(attempt: dict, work: pathlib.Path) -> dict:
    """One retrieval attempt, recorded whether it succeeds or fails."""
    body = work / ("body_" + attempt["id"] + ".bin")
    started = utcnow()
    cmd = [
        "curl", "-sSL", "-A", UA, "--max-time", "300",
        "-o", str(body),
        "-w", "%{http_code}\t%{size_download}\t%{content_type}\t%{url_effective}\t%{time_total}",
        attempt["url"],
    ]
    proc = run(cmd)
    rec = dict(
        source_id=attempt["id"],
        url=attempt["url"],
        purpose=attempt["purpose"],
        retrieved_at=started,
        curl_exit=proc.returncode,
        curl_stderr=proc.stderr.strip() or None,
    )
    if proc.returncode != 0 or "\t" not in proc.stdout:
        rec.update(status="unretrieved", http_status=None, bytes=None, sha256=None,
                   content_type=None,
                   unretrieved_reason=(proc.stderr.strip() or
                                       "curl failed with no diagnostic"))
        return rec
    code, size, ctype, eff, ttot = proc.stdout.split("\t")
    raw = body.read_bytes() if body.exists() else b""
    rec.update(http_status=int(code), bytes=len(raw), content_type=ctype,
               effective_url=eff, seconds=float(ttot),
               sha256=sha256_bytes(raw) if raw else None)

    challenge = next((m.decode("utf-8", "replace") for m in BOT_CHALLENGE_MARKERS
                      if m in raw[:20000]), None)
    wanted_pdf = attempt["kind"] == "pdf"
    is_pdf = raw[:5] == b"%PDF-"
    if rec["http_status"] != 200:
        rec["status"] = "unretrieved"
        rec["unretrieved_reason"] = "HTTP %s" % code + (
            "; bot-challenge interstitial (%s)" % challenge if challenge else "")
        if b"Blocked by egress policy" in raw:
            rec["unretrieved_reason"] += "; proxy egress policy denial"
        if raw and b"not enabled for this session" in raw:
            rec["unretrieved_reason"] += "; session GitHub access gate"
    elif challenge and not is_pdf:
        rec["status"] = "unretrieved"
        rec["unretrieved_reason"] = (
            "HTTP 200 but body is a bot-challenge interstitial (%s); "
            "not circumvented" % challenge)
    elif wanted_pdf and not is_pdf:
        rec["status"] = "unretrieved"
        rec["unretrieved_reason"] = "HTTP 200 but body is not a PDF (%s)" % ctype
    else:
        rec["status"] = "retrieved"

    # keep the body: vendored inside the repo when small and useful, otherwise
    # only in the work directory (provenance still carries its sha256)
    if attempt.get("save") and raw:
        dest = OUT_ROOT / attempt["save"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(body, dest)
        rec["vendored_path"] = str(dest.relative_to(REPO_ROOT))
    elif raw:
        rec["work_path_not_vendored"] = str(body)
    return rec


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------
def pdf_pages(path: pathlib.Path):
    """Extract per-page text.

    pypdf probes `cryptography` at import time; this image's cryptography rust
    binding raises pyo3 PanicException, which pypdf's ImportError guard cannot
    catch.  The stubs below force pypdf onto its pure-python crypt provider.
    All PDFs read here are unencrypted, so no decryption path is exercised.
    """
    for name in ("cryptography", "cryptography.hazmat",
                 "cryptography.hazmat.primitives",
                 "cryptography.hazmat.primitives.ciphers",
                 "cryptography.hazmat.primitives.asymmetric",
                 "cryptography.exceptions"):
        if name not in sys.modules:
            mod = types.ModuleType(name)
            mod.__path__ = []          # type: ignore[attr-defined]
            sys.modules[name] = mod
    import pypdf  # noqa: E402
    reader = pypdf.PdfReader(str(path))
    meta = {k: str(v) for k, v in (reader.metadata or {}).items()}
    return meta, [p.extract_text() for p in reader.pages], pypdf.__version__


def write_extract(relpath: str, text: str) -> str:
    dest = EXTRACTS / relpath
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return str(dest.relative_to(REPO_ROOT))


def load_out_file(path: pathlib.Path):
    """Parse a CodedDualAttack .out file: '#'-comment header + one float/line."""
    header, values = [], []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            header.append(s)
        else:
            values.append(float(s))
    return header, values


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get(
        "TASK101_WORK", "/tmp/task-20260802-101-work"))
    ap.add_argument("--skip-network", action="store_true")
    args = ap.parse_args()

    work = pathlib.Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    EXTRACTS.mkdir(parents=True, exist_ok=True)

    provenance = dict(
        schema="crypto.autoresearch.source_provenance.v1",
        task_id="TASK-20260802-101",
        goal_id="GOAL-MLKEM-003",
        generated_at=utcnow(),
        generator="coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/"
                  "TASK-20260802-101/fetch_sources.py",
        policy_note=(
            "Bot-challenge interstitials (Cloudflare on eprint.iacr.org PDF "
            "endpoints, Anubis proof-of-work on hal.science) were NOT solved or "
            "circumvented; they are recorded as unretrieved. Proxy egress "
            "denials were not retried or routed around."),
        attempts=[],
        local_artifacts=[],
        code_repository=None,
    )
    reads = dict(
        schema="crypto.autoresearch.source_reads.v1",
        task_id="TASK-20260802-101",
        generated_at=utcnow(),
        note=("Direct reads of retrieved artifacts. No model is fitted and no "
              "conclusion is drawn here."),
    )

    # ---------------- network attempts ----------------
    if not args.skip_network:
        for attempt in ATTEMPTS:
            rec = fetch(attempt, work)
            provenance["attempts"].append(rec)
            print("[%-9s] %s %s" % (rec["status"], rec.get("http_status"),
                                    rec["url"]), flush=True)

    # ---------------- code head (git smart-HTTP) ----------------
    repo_url = "https://github.com/kevin-carrier/CodedDualAttack"
    clone = work / "CodedDualAttack_head"
    ls = run(["git", "ls-remote", repo_url])
    code = dict(url=repo_url, retrieved_at=utcnow(),
                ls_remote_cmd="git ls-remote " + repo_url,
                ls_remote_exit=ls.returncode,
                ls_remote_stdout=ls.stdout.strip(),
                ls_remote_stderr=ls.stderr.strip() or None)
    if ls.returncode == 0 and ls.stdout.strip():
        refs = dict((ln.split("\t")[1], ln.split("\t")[0])
                    for ln in ls.stdout.strip().splitlines())
        code["refs"] = refs
        code["head_commit"] = refs.get("HEAD")
        code["status"] = "retrieved"
    else:
        code["status"] = "unretrieved"
        code["unretrieved_reason"] = ls.stderr.strip() or "git ls-remote failed"

    if code["status"] == "retrieved" and not args.skip_network:
        if clone.exists():
            shutil.rmtree(clone)
        cl = run(["git", "clone", "--depth", "1", repo_url, str(clone)])
        code["clone_cmd"] = "git clone --depth 1 %s %s" % (repo_url, clone)
        code["clone_exit"] = cl.returncode
        code["clone_stderr"] = cl.stderr.strip() or None
    if clone.exists():
        head = run(["git", "-C", str(clone), "log", "-1",
                    "--format=%H\t%cI\t%an\t%s"]).stdout.strip()
        if head:
            h, cdate, author, subject = head.split("\t", 3)
            code.update(cloned_head_commit=h, head_commit_date=cdate,
                        head_author=author, head_subject=subject)
        files = run(["git", "-C", str(clone), "ls-files"]).stdout.split()
        manifest = {f: sha256_file(clone / f) for f in files
                    if (clone / f).is_file()}
        code["file_count"] = len(manifest)
        write_extract("codeddualattack/file_sha256_manifest.txt",
                      "".join("%s  %s\n" % (v, k)
                              for k, v in sorted(manifest.items())))
        code["file_sha256_manifest"] = (
            "inputs/MLKEM-DUAL-SOURCES-20260802/extracts/codeddualattack/"
            "file_sha256_manifest.txt")
    provenance["code_repository"] = code

    # ---------------- Q2 read: score-path asymmetry at head ----------------
    if clone.exists():
        vm = clone / "verifyModel" / "ScoreExperimentalDistribution"
        fft_src = (vm / "FFT_sample.py").read_text()
        alg_src = (vm / "Algorithm.py").read_text()
        vendored_fft = (REPO_ROOT / "experiments" / "EXP-MLKEM-013" /
                        "vendor-lock" / "FFT_sample.py")
        pwrong_line = next(l.strip() for l in fft_src.splitlines()
                           if "fftn" in l)
        pgood_lines = [l.rstrip() for l in fft_src.splitlines()
                       if "self.F" in l]
        reads["q2_code_head"] = dict(
            head_commit=code.get("cloned_head_commit"),
            pinned_commit_in_findings="9c1367f85d26038244bc83c025d84c0b7006f2ee",
            head_equals_pinned=(code.get("cloned_head_commit") ==
                                "9c1367f85d26038244bc83c025d84c0b7006f2ee"),
            fft_sample_sha256_head=sha256_file(vm / "FFT_sample.py"),
            fft_sample_sha256_vendored=sha256_file(vendored_fft),
            algorithm_py_sha256_head=sha256_file(vm / "Algorithm.py"),
            pwrong_scale_line=pwrong_line,
            pgood_scale_lines=pgood_lines,
            pwrong_pipeline_lines=[l.strip() for l in alg_src.splitlines()
                                   if "T_FFT" in l or "score_function_complete" in l
                                   or "compute_survival" in l][:8],
            pgood_pipeline_lines=[l.strip() for l in alg_src.splitlines()
                                  if "compute_score" in l or
                                  "score_function_target" in l][:8],
        )
        write_extract("codeddualattack/FFT_sample.head.py", fft_src)

        # ---------------- Q3 read: measured T ranges at head ----------------
        data = vm / "data"
        q3 = dict(k_fft_alignment_note=(
            "EV-MLKEM-013 froze the alignment: Pwrong is fftn(T).real/k_fft, "
            "Pgood is the raw cosine sum, so Pgood/k_fft puts both on one "
            "scale. k_fft=3 for every archived parameter set below."),
            pwrong_files=[], pgood_files=[])
        for p in sorted(data.glob("Pwrong_*.out")):
            header, vals = load_out_file(p)
            positive = [i for i, v in enumerate(vals) if v > 0]
            q3["pwrong_files"].append(dict(
                file=p.name, sha256=sha256_file(p), bytes=p.stat().st_size,
                n_data_lines=len(vals), max_T_index=len(vals) - 1,
                last_T_with_positive_mass=positive[-1] if positive else None,
                value_at_last_positive=vals[positive[-1]] if positive else None,
                header=[h for h in header if len(h) < 200]))
            write_extract("codeddualattack/%s.header.txt" % p.name,
                          "\n".join(header) + "\n")
        for p in sorted(data.glob("Pgood_*.out")):
            header, vals = load_out_file(p)
            q3["pgood_files"].append(dict(
                file=p.name, sha256=sha256_file(p), bytes=p.stat().st_size,
                n_values=len(vals),
                raw_min=min(vals), raw_median=statistics.median(vals),
                raw_max=max(vals),
                aligned_min=min(vals) / 3.0,
                aligned_median=statistics.median(vals) / 3.0,
                aligned_max=max(vals) / 3.0,
                header=[h for h in header if len(h) < 200]))
            write_extract("codeddualattack/%s.header.txt" % p.name,
                          "\n".join(header) + "\n")
        reads["q3_code_head_data"] = q3

    # ---------------- Q1 read: Table C.2 in the vendored full text ---------
    if CARRIER_VENDOR_PDF.exists():
        meta, pages, pypdf_version = pdf_pages(CARRIER_VENDOR_PDF)
        prov_local = dict(
            path=str(CARRIER_VENDOR_PDF.relative_to(REPO_ROOT)),
            sha256=sha256_file(CARRIER_VENDOR_PDF),
            bytes=CARRIER_VENDOR_PDF.stat().st_size,
            role="baseline artifact the standing findings were derived from "
                 "(read-only; not modified, not re-vendored)",
            pdf_metadata=meta, pages=len(pages), pypdf_version=pypdf_version)
        provenance["local_artifacts"].append(prov_local)

        wanted = {37: "carrier-hal-05406481/page37_tables_C1_C2.txt",
                  26: "carrier-hal-05406481/page26_fig41.txt",
                  25: "carrier-hal-05406481/page25_pwrong_validation.txt",
                  23: "carrier-hal-05406481/page23_approx_4_8_4_9.txt",
                  27: "carrier-hal-05406481/page27_threshold_choice.txt"}
        extract_paths = {}
        for pageno, rel in wanted.items():
            if pageno <= len(pages):
                extract_paths[pageno] = write_extract(rel, pages[pageno - 1])
        write_extract("carrier-hal-05406481/pdf_metadata.json",
                      json.dumps(meta, indent=2) + "\n")

        page37 = pages[36] if len(pages) >= 37 else ""
        cn_block = page37.split("CN:")[-1] if "CN:" in page37 else ""
        cn_row = next((l for l in cn_block.splitlines()
                       if l.startswith("Kyber-512")), None)
        reads["q1_table_c2"] = dict(
            artifact=prov_local["path"],
            artifact_sha256=prov_local["sha256"],
            pdf_moddate=meta.get("/ModDate"),
            pdf_creationdate=meta.get("/CreationDate"),
            pdf_creator=meta.get("/Creator"),
            pdf_producer=meta.get("/Producer"),
            pdf_page_of_table_c2=37,
            printed_page_number="36",
            cn_kyber512_row_verbatim=cn_row,
            cn_kyber512_log2_Tsample=(cn_row.split()[3] if cn_row else None),
            cc_kyber512_row_verbatim=next(
                (l for l in page37.split("CC:")[-1].split("CN:")[0].splitlines()
                 if l.startswith("Kyber-512")), None),
            table_c2_caption=next((l for l in page37.splitlines()
                                   if l.startswith("Table C.2")), None),
            occurrences_of_143_30=page37.count("143.30"),
            occurrences_of_134_30=page37.count("134.30"),
            extract_paths=extract_paths)

        # Q3 read on the paper side: where does Fig 4.1 measure Pwrong?
        p26 = pages[25] if len(pages) >= 26 else ""
        ticks = re.findall(r"\b\d{3,4}\b", p26.split("T\n")[0]) if p26 else []
        reads["q3_paper_side"] = dict(
            fig41_axis_ticks_first_panel=ticks[:10],
            fig41_caption_snippet=(p26[p26.find("Fig.4.1"):p26.find("Fig.4.1") + 420]
                                   if "Fig.4.1" in p26 else None),
            threshold_choice_quote=next(
                (s.strip() for s in (pages[26] if len(pages) >= 27 else "")
                 .split(".") if "Approximation 4.8" in s and "Pgood" in s), None),
            table_c2_caption_pgood=reads["q1_table_c2"]["table_c2_caption"])

    # ---------------- corpus checks on the other retrieved PDFs ------------
    corpus = {}
    for sid, fname in (("matzov-pdf", "body_matzov-pdf.bin"),
                       ("fips203-pdf", "body_fips203-pdf.bin")):
        p = work / fname
        if not p.exists() or p.read_bytes()[:5] != b"%PDF-":
            corpus[sid] = dict(available=False)
            continue
        meta, pages, _ = pdf_pages(p)
        text = "\n".join(pages)
        counts = {pat: len(re.findall(re.escape(pat), text, flags=re.I))
                  for pat in ("Pwrong", "P_wrong", "false positive",
                              "false-positive", "Pgood", "threshold",
                              "simulation", "experimental")}
        corpus[sid] = dict(available=True, sha256=sha256_file(p),
                           bytes=p.stat().st_size, pages=len(pages),
                           pdf_metadata=meta, term_counts=counts)
        if sid == "matzov-pdf":
            idx = text.lower().find("false positive")
            if idx >= 0:
                region = re.sub(r"\s+", " ", text[max(0, idx - 900): idx + 600])
                corpus[sid]["false_positive_locus"] = region
                write_extract("matzov-2022/false_positive_locus.txt",
                              region + "\n")
        if sid == "fips203-pdf":
            write_extract("fips203/front_matter.txt",
                          "\n".join(pages[:2]))
    reads["q3_other_sources"] = corpus

    # ---------------- ePrint revision history (Q1, current side) ----------
    landing = OUT_ROOT / "eprint-2022-1750" / "landing.html"
    oai = OUT_ROOT / "eprint-2022-1750" / "oai_getrecord.xml"
    hist = {}
    if landing.exists():
        html = landing.read_text(encoding="utf-8", errors="replace")
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
        m = re.search(r"History (.{0,160}?) See all versions", flat)
        hist["landing_history_text"] = m.group(1).strip() if m else None
        n = re.search(r"Note: ([^<]{0,200}?) Metadata", flat)
        hist["landing_version_note"] = n.group(1).strip() if n else None
        hist["landing_sha256"] = sha256_file(landing)
    if oai.exists():
        xml = oai.read_text(encoding="utf-8", errors="replace")
        d = re.search(r"<datestamp>([^<]+)</datestamp>", xml)
        hist["oai_datestamp"] = d.group(1) if d else None
        hist["oai_sha256"] = sha256_file(oai)
    hal = OUT_ROOT / "eprint-2022-1750" / "hal_api_record.json"
    if hal.exists():
        try:
            doc = json.loads(hal.read_text())["response"]["docs"][0]
            hist["hal_record"] = doc
        except Exception as exc:                        # pragma: no cover
            hist["hal_record_parse_error"] = repr(exc)
    reads["q1_current_revision_metadata"] = hist

    # ---------------- write outputs ----------------
    (OUT_ROOT / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=False) + "\n")
    (OUT_ROOT / "source_reads.json").write_text(
        json.dumps(reads, indent=2, sort_keys=False) + "\n")
    print("\nwrote %s" % (OUT_ROOT / "provenance.json"))
    print("wrote %s" % (OUT_ROOT / "source_reads.json"))
    retrieved = sum(1 for a in provenance["attempts"] if a["status"] == "retrieved")
    print("attempts: %d retrieved, %d unretrieved"
          % (retrieved, len(provenance["attempts"]) - retrieved))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
