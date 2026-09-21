"""STAGE 0 of EXP-ICINV-fcb497: retrieval, pinning, and BYTE-VERIFIED quotation.

Answers exactly one question and answers it ONLY from pinned bytes: over WHICH
FIELD is the square-root Velu Otilde(sqrt d) operation count stated?

THE HARD RULE THIS MODULE EXISTS TO ENFORCE (contract
`stage0_retrieval_frozen.background_knowledge_prohibition`, CORR-20260807-a24675,
AGENTS.md rule 9): the verdict may cite ONLY the pinned artifacts.  Nothing here
contains a remembered sentence from any paper.  Every emitted quotation is
extracted programmatically from a retrieved byte stream and re-checked as an
exact byte-substring of the pinned text file at recorded offsets.  If the source
cannot be retrieved the verdict is UNRETRIEVED_INFRA -- never the remembered
answer.

Contains NO domain arithmetic (contract inputs.implementation.new_modules).
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_PATH = os.path.join(REPO, "experiments", "EXP-ICINV-fcb497", "specification.yaml")

# ---------------------------------------------------------------------------
# FROZEN (stage0_retrieval_frozen)
# ---------------------------------------------------------------------------
PRIMARY_URLS = (
    "https://eprint.iacr.org/2020/341",
    "https://eprint.iacr.org/2020/341.pdf",
)
FALLBACK_PATHS = (
    "knowledge/literature/KN-LIT-780.md",
    "https://eprint.iacr.org/2020/1109",
    "https://eprint.iacr.org/2020/1109.pdf",
)
CURL_MAX_TIME = 120

# extraction_target_frozen search terms.  These are PROTOCOL PARAMETERS, not
# reference values; `check_terms_against_contract` nevertheless verifies each one
# is present in the contract's own frozen list so the code cannot drift from it.
SEARCH_TERMS = (
    "operations", "field operations", "multiplications", "\\tilde{O}", "Otilde",
    "O~", "sqrt", "\\sqrt", "baby-step", "giant-step", "kernel",
    "field of definition", "F_q", "F_{q}", "\\mathbf{F}", "\\mathbb{F}",
)
CONTEXT_CHARS = 400            # ">= 400 characters of surrounding context"
MAX_PASSAGES = 4000            # truncation is RECORDED, never silent
FULL_TEXT_MIN_CHARS = 5000     # what counts as a retrieved FULL TEXT (see below)

VERDICTS = ("KERNEL_FIELD", "BASE_FIELD", "AMBIGUOUS", "UNRETRIEVED_INFRA")


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


# ---------------------------------------------------------------------------
# retrieval
# ---------------------------------------------------------------------------
def curl_fetch(url: str, dest: str) -> dict:
    """The frozen retrieval command shape, with its full receipt.

    `curl -sS -L --max-time 120 -o <artifact> <url>`, recording the HTTP status,
    the final URL after redirects, the Content-Type, the byte length and the
    retrieval timestamp.  A non-200 status is an INFRASTRUCTURE outcome and is
    reported as one; it is NEVER read as a verdict.
    """
    fmt = ("%{http_code}\t%{content_type}\t%{size_download}\t%{url_effective}"
           "\t%{time_total}")
    cmd = ["curl", "-sS", "-L", "--max-time", str(CURL_MAX_TIME), "-o", dest,
           "-w", fmt, url]
    started = _now()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    rec = {
        "url": url, "command": " ".join(cmd), "retrieved_at": started,
        "curl_exit": proc.returncode, "curl_stderr": proc.stderr.strip()[:2000],
        "http_status": None, "content_type": None, "byte_length": None,
        "final_url": None, "seconds": None, "stored_path": None, "sha256": None,
        "ok": False,
    }
    if proc.stdout.count("\t") >= 4:
        code, ctype, size, final, secs = proc.stdout.split("\t")[:5]
        rec.update({"http_status": int(code), "content_type": ctype,
                    "byte_length": int(size), "final_url": final,
                    "seconds": float(secs)})
    if os.path.exists(dest):
        rec["stored_path"] = os.path.relpath(dest, REPO)
        rec["sha256"] = sha256_file(dest)
        rec["byte_length_on_disk"] = os.path.getsize(dest)
    rec["ok"] = (rec["curl_exit"] == 0 and rec["http_status"] == 200
                 and bool(rec.get("byte_length_on_disk")))
    return rec


def copy_local(rel_path: str, dest: str) -> dict:
    src = os.path.join(REPO, rel_path)
    rec = {"url": f"file://{rel_path}", "command": f"read {rel_path}",
           "retrieved_at": _now(), "curl_exit": None, "curl_stderr": "",
           "http_status": None, "content_type": "text/markdown",
           "final_url": rel_path, "seconds": 0.0, "stored_path": None,
           "sha256": None, "ok": False, "local": True}
    if not os.path.exists(src):
        rec["error"] = "absent from this worktree"
        return rec
    with open(src, "rb") as fh:
        data = fh.read()
    with open(dest, "wb") as fh:
        fh.write(data)
    rec.update({"stored_path": os.path.relpath(dest, REPO),
                "sha256": sha256_bytes(data), "byte_length": len(data),
                "byte_length_on_disk": len(data), "ok": True})
    return rec


# ---------------------------------------------------------------------------
# text extraction
# ---------------------------------------------------------------------------
def _looks_like_pdf(path: str) -> bool:
    with open(path, "rb") as fh:
        return fh.read(5) == b"%PDF-"


def extract_text(src: str, dest: str) -> dict:
    """Extract plain text beside the pinned byte stream, with its own sha256."""
    rec = {"source": os.path.relpath(src, REPO), "method": None, "ok": False,
           "text_path": None, "sha256": None, "chars": 0, "error": None,
           "is_pdf": False}
    try:
        if _looks_like_pdf(src):
            rec["is_pdf"] = True
            proc = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8",
                                   src, dest], capture_output=True, text=True)
            rec["method"] = "pdftotext -layout -enc UTF-8 (poppler)"
            if proc.returncode != 0:
                rec["error"] = proc.stderr.strip()[:500]
                return rec
        else:
            with open(src, "rb") as fh:
                raw = fh.read().decode("utf-8", errors="replace")
            if "<html" in raw[:4000].lower() or "<!doctype html" in raw[:200].lower():
                txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw,
                             flags=re.S | re.I)
                txt = re.sub(r"<[^>]+>", " ", txt)
                txt = html.unescape(txt)
                txt = re.sub(r"[ \t\r\f\v]+", " ", txt)
                txt = re.sub(r"\n\s*\n+", "\n\n", txt)
                rec["method"] = ("html tag strip + entity unescape + whitespace "
                                 "collapse (harness.velu_stage0.extract_text)")
            else:
                txt = raw
                rec["method"] = "verbatim (plain text / markdown)"
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(txt)
    except OSError as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
        return rec
    if not os.path.exists(dest):
        rec["error"] = "extractor produced no output"
        return rec
    rec.update({"text_path": os.path.relpath(dest, REPO),
                "sha256": sha256_file(dest),
                "chars": os.path.getsize(dest), "ok": True})
    return rec


def is_full_text(fetch_rec: dict, text_rec: dict) -> dict:
    """Does this artifact constitute a RETRIEVED FULL TEXT?

    The contract freezes: "A determinate verdict requires a retrieved full text
    of 2020/341 or 2020/1109 with a byte-verified passage."  A landing/abstract
    page is metadata plus an abstract and is NOT the full text, so the test is
    made explicit and mechanical rather than left to the executor's judgement:
    the artifact must be a PDF document whose extracted text exceeds
    FULL_TEXT_MIN_CHARS characters.
    """
    pdf = bool(text_rec.get("is_pdf"))
    chars = int(text_rec.get("chars") or 0)
    return {"is_full_text": bool(pdf and chars >= FULL_TEXT_MIN_CHARS),
            "is_pdf_document": pdf, "extracted_chars": chars,
            "min_chars_required": FULL_TEXT_MIN_CHARS,
            "criterion": "PDF document with >= "
                         f"{FULL_TEXT_MIN_CHARS} extracted characters"}


# ---------------------------------------------------------------------------
# passage location, quotation, and byte-exact re-verification
# ---------------------------------------------------------------------------
def find_passages(text_path: str, terms=SEARCH_TERMS) -> dict:
    with open(text_path, "rb") as fh:
        blob = fh.read()
    text = blob.decode("utf-8", errors="replace")
    hits = []
    for term in terms:
        start = 0
        while True:
            idx = text.find(term, start)
            if idx < 0:
                break
            start = idx + 1
            lo = max(0, idx - CONTEXT_CHARS // 2)
            hi = min(len(text), idx + len(term) + CONTEXT_CHARS // 2)
            if hi - lo < CONTEXT_CHARS:
                hi = min(len(text), lo + CONTEXT_CHARS)
                lo = max(0, hi - CONTEXT_CHARS)
            ctx = text[lo:hi]
            byte_start = len(text[:lo].encode("utf-8"))
            byte_end = byte_start + len(ctx.encode("utf-8"))
            hits.append({
                "term": term, "char_offset": idx,
                "context": ctx, "context_char_start": lo, "context_char_end": hi,
                "context_byte_start": byte_start, "context_byte_end": byte_end,
                "context_chars": len(ctx),
            })
            if len(hits) >= MAX_PASSAGES:
                return {"passages": hits, "truncated": True,
                        "truncation_note": f"capped at {MAX_PASSAGES}; RECORDED"}
    # dedupe identical contexts, keeping every matching term
    merged: dict[tuple[int, int], dict] = {}
    for h in hits:
        key = (h["context_byte_start"], h["context_byte_end"])
        if key in merged:
            merged[key]["terms"].append(h["term"])
        else:
            m = dict(h)
            m["terms"] = [m.pop("term")]
            merged[key] = m
    out = sorted(merged.values(), key=lambda z: z["context_byte_start"])
    return {"passages": out, "truncated": False, "raw_hit_count": len(hits)}


def verify_quote(text_path: str, quote: str, byte_start: int, byte_end: int) -> dict:
    """Re-check a quotation as an EXACT byte-substring at the recorded offsets."""
    with open(text_path, "rb") as fh:
        blob = fh.read()
    qb = quote.encode("utf-8")
    slice_ok = blob[byte_start:byte_end] == qb
    present = blob.find(qb)
    return {"exact_substring": present >= 0,
            "offsets_match": bool(slice_ok),
            "verified": bool(slice_ok and present >= 0),
            "byte_start": byte_start, "byte_end": byte_end,
            "first_occurrence_byte_offset": present,
            "file_sha256": sha256_bytes(blob),
            "text_path": os.path.relpath(text_path, REPO)}


# ---------------------------------------------------------------------------
# passage classification (mechanical; the verdict is READ from this, not typed)
# ---------------------------------------------------------------------------
_COUNT_RE = re.compile(
    r"(\\widetilde\{O\}|\\tilde\{O\}|Otilde|O~|\bO\s*\(|\\Theta|\bcost\b)",
    re.I)
_OPS_RE = re.compile(r"(operations?|multiplications?|field operations?)", re.I)
_FIELD_TOKEN_RE = re.compile(
    r"(\\mathbb\{F\}_\{?[^\s\$\},]+\}?|\\mathbf\{F\}_\{?[^\s\$\},]+\}?"
    r"|\bF_\{[^\}]+\}|\bF_[a-zA-Z0-9]+|\bGF\([^\)]+\))")
_KERNEL_RATIONALITY_RE = re.compile(
    r"(kernel|\\langle\s*\{?\s*P\s*\}?\s*\\rangle|<P>|point .{0,40}\bin\b .{0,60}\("
    r"|field of definition|generator of the kernel|P\s*\\in|of prime order"
    r"|quotient curve)",
    re.I)


def classify_passage(ctx: str, document: str | None = None) -> dict:
    """Deterministic features of one passage, and the branch label they imply.

    kernel_field  -- the passage states a count over a field AND, in the same
                     context, places the kernel / kernel generator in that field
                     (equivalently: the field in which the kernel points are
                     represented).
    base_field    -- the passage states a count over a field with NO
                     kernel-rationality qualification anywhere in its context.
    field_unspecified -- an operation count with no field designator at all.
    not_a_count   -- the passage matched a frozen search term but states no
                     operation count.
    """
    has_count = bool(_COUNT_RE.search(ctx))
    has_ops = bool(_OPS_RE.search(ctx))
    fields = sorted(set(_FIELD_TOKEN_RE.findall(ctx)))
    kern = _KERNEL_RATIONALITY_RE.findall(ctx)
    doc_kern = (_KERNEL_RATIONALITY_RE.findall(document) if document else [])
    if not (has_count and has_ops):
        label = "not_a_count"
    elif not fields:
        label = "field_unspecified"
    elif kern:
        label = "kernel_field"
    else:
        label = "base_field"
    # DEFECT REPAIR, RECORDED: a kernel-rationality qualification can sit in the
    # SAME SENTENCE but outside a 400-character window, which mislabels an
    # otherwise kernel-qualified count as base_field. The window label is kept
    # verbatim (it is what the frozen 400-character rule sees) and a
    # DOCUMENT-level flag is reported beside it, so a reviewer can see both.
    return {"has_count_expression": has_count, "has_operation_word": has_ops,
            "field_tokens": fields,
            "kernel_rationality_markers": sorted({k.lower() for k in kern}),
            "kernel_rationality_in_document": sorted({k.lower() for k in doc_kern}),
            "label": label,
            "label_with_document_context": (
                "kernel_field" if (label == "base_field" and doc_kern) else label),
            "label_note": ("`label` applies the frozen >=400-character context rule "
                           "literally; `label_with_document_context` additionally "
                           "counts kernel-rationality qualifications elsewhere in "
                           "the same artifact. NEITHER can move the verdict when no "
                           "full text was retrieved -- the determinate branches are "
                           "gated on one.")}


# ---------------------------------------------------------------------------
# attribution check (read from the contract at run time -- never transcribed)
# ---------------------------------------------------------------------------
def attribution_from_contract() -> dict:
    with open(SPEC_PATH, "rb") as fh:
        blob = fh.read()
    text = blob.decode("utf-8")
    start = text.find("primary_source:")
    end = text.find("fallback_source:", start)
    ident = text[start:end] if start >= 0 and end > start else ""
    names = sorted(set(re.findall(r"[A-Z][a-z]+(?:-[A-Z][a-z]+)*", ident)))
    return {"spec_path": os.path.relpath(SPEC_PATH, REPO),
            "spec_sha256": sha256_bytes(blob),
            "identity_block": ident.strip(),
            "identity_byte_start": len(text[:start].encode()),
            "identity_byte_end": len(text[:end].encode()),
            "capitalised_tokens": names,
            "note": "the attribution is READ FROM THE CONTRACT at run time and "
                    "byte-pinned; it is never typed from memory "
                    "(CORR-20260807-a24675)"}


def attribution_check(text_path: str, attribution: dict) -> dict:
    with open(text_path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    tokens = [t for t in attribution["capitalised_tokens"] if len(t) > 3]
    found = {t: (t in text) for t in tokens}
    return {"tokens_checked": tokens,
            "tokens_found_in_artifact": sorted(t for t, v in found.items() if v),
            "tokens_absent_from_artifact": sorted(t for t, v in found.items() if not v),
            "note": "an author/title token absent from the retrieved artifact is "
                    "reported as an ATTRIBUTION DEFECT, not silently accepted"}


# ---------------------------------------------------------------------------
# the frozen verdict rule
# ---------------------------------------------------------------------------
def decide(artifacts: list[dict]) -> dict:
    """Evaluate stage0_branches_frozen STRICTLY IN ORDER; first to fire wins.

    Two frozen gates constrain the determinate branches and both are applied
    mechanically here:
      * "A determinate verdict requires a retrieved FULL TEXT of 2020/341 or
        2020/1109 with a byte-verified passage" -- so a landing/abstract page,
        however cleanly it quotes, can never return KERNEL_FIELD or BASE_FIELD.
      * "the corpus note alone can NEVER return a KERNEL_FIELD or BASE_FIELD
        verdict.  It may return only AMBIGUOUS."
    """
    retrieved = [a for a in artifacts if a["fetch"]["ok"]]
    determinate_sources = [
        a for a in retrieved
        if a["role"] in ("primary", "fallback_paper") and a["full_text"]["is_full_text"]
    ]
    primary_full = [a for a in determinate_sources if a["role"] == "primary"]

    labels_by_source = {
        a["label"]: sorted({p["classification"]["label"] for p in a["passages"]
                            if p["classification"]["label"] in
                            ("kernel_field", "base_field", "field_unspecified")})
        for a in retrieved
    }
    verified_quotes = [
        p for a in retrieved for p in a["passages"]
        if p["verification"]["verified"]
    ]

    if not retrieved:
        return _verdict("UNRETRIEVED_INFRA", labels_by_source, verified_quotes,
                        "No source could be retrieved (non-200 status, timeout, "
                        "or no network) and no local copy exists. INFRASTRUCTURE "
                        "OUTCOME, never a mathematical result and never a "
                        "BASE_FIELD verdict (AGENTS.md rule 5).",
                        determinate_sources)

    def _labelled(srcs, want):
        # KERNEL_FIELD is read from the STRICT window label: the passage itself
        # must state the count over the field the kernel points live in.
        # BASE_FIELD is read from the DOCUMENT-AWARE label, because its frozen
        # condition is "with NO kernel-rationality qualification" -- a
        # qualification anywhere in the same artifact defeats it. The asymmetry
        # is deliberate and makes the record-inverting branch the harder one to
        # fire, never the easier one.
        key = "label" if want == "kernel_field" else "label_with_document_context"
        return [p for a in srcs for p in a["passages"]
                if p["classification"].get(key) == want and p["verification"]["verified"]]

    kern = _labelled(primary_full, "kernel_field")
    base = _labelled(primary_full, "base_field")

    if primary_full and kern and not base:
        return _verdict("KERNEL_FIELD", labels_by_source, verified_quotes,
                        "A byte-verified passage of the pinned PRIMARY FULL TEXT "
                        "states the count over the field in which the kernel "
                        "points are represented, and no byte-verified passage of "
                        "the same source contradicts it.", determinate_sources,
                        deciding=kern[:3])
    if primary_full and base and not kern:
        return _verdict("BASE_FIELD", labels_by_source, verified_quotes,
                        "A byte-verified passage of the pinned PRIMARY FULL TEXT "
                        "states the count over the base field with no "
                        "kernel-rationality qualification, and no byte-verified "
                        "passage contradicts it.", determinate_sources,
                        deciding=base[:3])

    if not determinate_sources:
        why = ("Sources WERE retrieved, but no FULL TEXT of 2020/341 or 2020/1109 "
               "was among them, and the contract freezes that a determinate "
               "verdict requires one. Only landing/abstract pages and/or the "
               "corpus note were retrievable, and the corpus note alone may "
               "return only AMBIGUOUS.")
    elif kern and base:
        why = ("Different byte-verified passages of the pinned sources disagree "
               "about the field the count is stated over.")
    else:
        why = ("The pinned full text states the count without disambiguating the "
               "field.")
    return _verdict("AMBIGUOUS", labels_by_source, verified_quotes, why,
                    determinate_sources,
                    deciding=(kern + base)[:3])


def _verdict(v, labels, quotes, why, determinate_sources, deciding=None) -> dict:
    assert v in VERDICTS
    return {
        "verdict": v,
        "reason": why,
        "labels_by_source": labels,
        "determinate_sources_available": [a["label"] for a in determinate_sources],
        "byte_verified_quotation_count": len(quotes),
        "deciding_passages": deciding or [],
        "claim_tier": {
            "KERNEL_FIELD": "literature_primary_read",
            "BASE_FIELD": "literature_primary_read",
            "AMBIGUOUS": "literature_secondary_or_ambiguous",
            "UNRETRIEVED_INFRA": "none (infrastructure outcome)",
        }[v],
        "consequence": {
            "KERNEL_FIELD": "Cost corollary CC of H-ICINV-82ee6a STANDS as a "
                            "conditional claim; the Otilde(sqrt(d)*m) accounting "
                            "may be stated, LABELLED MODELED and conditional on "
                            "HEUR-ORD-1.",
            "BASE_FIELD": "THE INVERTING BRANCH: cost corollary CC is REFUTED, "
                          "the knife edge is REAL, and IDEA-20260807-9fb27c must "
                          "be SUPERSEDED by a new record under a new id. "
                          "Mechanism STEP 4 (H-ENDO-001) still makes the tie "
                          "useless for the ECDLP.",
            "AMBIGUOUS": "NO COST STATEMENT MAY BE MADE IN EITHER DIRECTION. CC "
                         "remains UNDETERMINED. Successor action: obtain the "
                         "ANTS XIV proceedings version or a locally archived PDF.",
            "UNRETRIEVED_INFRA": "INFRASTRUCTURE OUTCOME. CC remains UNDETERMINED; "
                                 "successor action is a retrieval retry.",
        }[v],
        "stages_1_to_4_still_run": True,
    }


def write_json(path: str, obj) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return sha256_file(path)


def check_terms_against_contract(terms=SEARCH_TERMS) -> dict:
    """Guard: every coded search term must appear in the contract's frozen list."""
    with open(SPEC_PATH, encoding="utf-8") as fh:
        spec = fh.read()
    start = spec.find("extraction_target_frozen:")
    end = spec.find("quote_verification_rule_blocking:", start)
    block = spec[start:end] if start >= 0 else ""
    out = {}
    for t in terms:
        variants = {t, t.replace("\\", "\\\\"), t.replace("\\", "")}
        out[t] = any(v in block for v in variants)
    return {"all_terms_in_contract": all(out.values()), "per_term": out,
            "contract_block_sha256": hashlib.sha256(block.encode()).hexdigest()}
