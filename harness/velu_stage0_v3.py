"""STAGE 0 of EXP-ICINV-fcb497 under PROTOCOL VERSION 2 -- RETRIEVAL LIST ONLY.

This module exists because `harness/velu_stage0.py` is depended on by COMMITTED
runs (RUN-ICINV-kf-stage0, RUN-ICINV-kf-stage0-v2) and must stay byte-identical
so those runs remain reproducible against it.  Amendment
`experiments/EXP-ICINV-fcb497/amendments/v2.yaml` changes exactly two things that
touch code:

    A1  stage0_retrieval_frozen.primary_source.urls_in_order gains two mirrors
        AHEAD of the two eprint URLs (the version-1 list is a strict suffix).
    A2  each quotation must additionally record the URL used, the artifact
        sha256, and the source VERSION STRING as EXTRACTED FROM THE ARTIFACT,
        byte-verified like any other quotation, or `null` plus a reason.

NOTHING ELSE IS CHANGED, AND NOTHING ELSE IS REIMPLEMENTED HERE.  Extraction,
the frozen search-term list, the 400-character window, passage classification,
byte-exact quote re-verification, the attribution check and the four frozen
branch rules are IMPORTED VERBATIM from `harness.velu_stage0`; this module does
not redefine one of them.  `classify_passage`, `find_passages`, `verify_quote`,
`is_full_text` and `decide` are re-exported by name so a reviewer can see that
the objects used here ARE the committed ones (`velu_stage0_v3.decide is
velu_stage0.decide` is True).

THE STANDING PROHIBITION IS UNCHANGED AND UNWEAKENED (contract
`stage0_retrieval_frozen.background_knowledge_prohibition`, amendment A5,
CORR-20260807-a24675, AGENTS.md rule 9): the verdict may cite ONLY the pinned
artifacts.  No remembered sentence from any paper appears in this file.  No
quotation, offset or hash is copied from the archived Red Team report.  If the
source cannot be retrieved the verdict is UNRETRIEVED_INFRA -- never the
remembered answer.

Contains NO domain arithmetic.
"""
from __future__ import annotations

import hashlib
import os
import re

from . import velu_stage0 as s0

# --- re-exported VERBATIM from the committed module; never redefined here -----
sha256_bytes = s0.sha256_bytes
sha256_file = s0.sha256_file
curl_fetch = s0.curl_fetch
copy_local = s0.copy_local
extract_text = s0.extract_text
is_full_text = s0.is_full_text
find_passages = s0.find_passages
verify_quote = s0.verify_quote
classify_passage = s0.classify_passage
attribution_from_contract = s0.attribution_from_contract
attribution_check = s0.attribution_check
decide = s0.decide
write_json = s0.write_json
check_terms_against_contract = s0.check_terms_against_contract
SEARCH_TERMS = s0.SEARCH_TERMS
CONTEXT_CHARS = s0.CONTEXT_CHARS
VERDICTS = s0.VERDICTS
FALLBACK_PATHS = s0.FALLBACK_PATHS          # A1 leaves the fallback UNCHANGED

REPO = s0.REPO
AMENDMENT_PATH = os.path.join(REPO, "experiments", "EXP-ICINV-fcb497",
                              "amendments", "v2.yaml")

# ---------------------------------------------------------------------------
# A1: the amended retrieval list.  PROTOCOL PARAMETERS, not reference values --
# and `check_urls_against_amendment` below nevertheless verifies each one against
# the amendment's own A1 `to:` block at run time, in the same spirit as
# velu_stage0.check_terms_against_contract, so the code cannot drift from it.
# ---------------------------------------------------------------------------
PRIMARY_URLS = (
    "https://msp.org/obs/2020/4-1/obs-v4-n1-p05-s.pdf",
    "https://arxiv.org/pdf/2003.10118",
    "https://eprint.iacr.org/2020/341",
    "https://eprint.iacr.org/2020/341.pdf",
)

# ---------------------------------------------------------------------------
# A2: version-string extraction.
#
# SCOPE NOTE, RECORDED: these patterns are NOT additions to the frozen
# `extraction_target_frozen` search-term list and are never used to locate an
# operation-count passage.  SR5's frozen grid ("no additional search term") binds
# that list, which is imported unchanged above.  These patterns implement the
# SEPARATE recording obligation amendment A2 adds, and they are generic
# publication markers -- no paper-specific string, no remembered version, and no
# value copied from any record.  Every match is byte-verified at recorded offsets
# exactly like a quotation; when nothing matches, the run records
# `version_string: null` with a reason and SUPPLIES NOTHING.
# ---------------------------------------------------------------------------
VERSION_PATTERNS = (
    ("arxiv_version_marker", r"arXiv:\d{4}\.\d{4,5}v\d+"),
    ("arxiv_identifier", r"arXiv:\d{4}\.\d{4,5}"),
    ("open_book_series_line", r"The Open Book Series[^\n]{0,80}"),
    ("msp_locator", r"msp\.org/[^\s]{3,80}"),
    ("doi_line", r"(?i)\bdoi[:\s]{1,3}10\.\d{4,9}/[^\s]{1,60}"),
    ("volume_year_line", r"(?i)\bvol(?:ume)?\.?\s*\d{1,3}\b[^\n]{0,60}(?:19|20)\d{2}"),
    ("revision_line", r"(?i)\b(?:last (?:updated|revised)|revised|version)\b[:\s][^\n]{0,60}"),
    ("ants_line", r"(?i)\bANTS\b[^\n]{0,60}"),
)
MAX_VERSION_MATCHES_PER_PATTERN = 8


def check_urls_against_amendment(urls=PRIMARY_URLS) -> dict:
    """Guard: every coded URL must appear in amendment v2's A1 `to:` block.

    Reads the amendment AT RUN TIME and pins it by sha256, so the retrieval list
    in this file cannot silently diverge from the approved one
    (CORR-20260807-a24675 reference_value_rule_binding, applied to a protocol
    parameter rather than to a measured value).
    """
    with open(AMENDMENT_PATH, "rb") as fh:
        blob = fh.read()
    text = blob.decode("utf-8")
    start = text.find("field: stage0_retrieval_frozen.primary_source.urls_in_order")
    to_idx = text.find("      to:", start)
    end = text.find("ordering_rationale:", to_idx)
    block = text[to_idx:end] if (start >= 0 and to_idx > start and end > to_idx) else ""
    in_block = [u for u in urls if u in block]
    order_ok = [block.find(u) for u in urls] == sorted(block.find(u) for u in urls)
    return {
        "amendment_path": os.path.relpath(AMENDMENT_PATH, REPO),
        "amendment_sha256": hashlib.sha256(blob).hexdigest(),
        "a1_to_block_byte_start": len(text[:to_idx].encode("utf-8")),
        "a1_to_block_byte_end": len(text[:end].encode("utf-8")),
        "a1_to_block_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
        "all_urls_in_amendment": len(in_block) == len(urls),
        "per_url_present": {u: (u in block) for u in urls},
        "coded_order_matches_amendment_order": bool(order_ok),
        "version_1_list_is_a_strict_suffix": (
            tuple(urls[-len(s0.PRIMARY_URLS):]) == tuple(s0.PRIMARY_URLS)),
        "note": ("the retrieval list is read back against the APPROVED amendment "
                 "at run time; nothing here is transcribed from a report"),
    }


def extract_version_strings(text_path: str) -> dict:
    """A2: extract the source VERSION STRING from the artifact itself.

    Every candidate is located programmatically, recorded with its BYTE offsets
    into the UTF-8 text file, and re-checked with the committed
    `velu_stage0.verify_quote` as an exact byte substring.  The chosen
    `version_string` is the first match of the first pattern that matches, in the
    declared pattern order.  NO VERSION STRING IS EVER SUPPLIED: if nothing
    matches, the result is `version_string: null` with `version_string_reason`.
    """
    with open(text_path, "rb") as fh:
        blob = fh.read()
    text = blob.decode("utf-8", errors="replace")
    candidates: list[dict] = []
    for name, pattern in VERSION_PATTERNS:
        rx = re.compile(pattern)
        for i, mt in enumerate(rx.finditer(text)):
            if i >= MAX_VERSION_MATCHES_PER_PATTERN:
                break
            matched = mt.group(0)
            byte_start = len(text[:mt.start()].encode("utf-8"))
            byte_end = byte_start + len(matched.encode("utf-8"))
            candidates.append({
                "pattern_name": name,
                "pattern": pattern,
                "matched_text": matched,
                "char_start": mt.start(),
                "byte_start": byte_start,
                "byte_end": byte_end,
                "verification": s0.verify_quote(text_path, matched,
                                                byte_start, byte_end),
            })
    verified = [c for c in candidates if c["verification"]["verified"]]
    chosen = verified[0] if verified else None
    return {
        "text_path": os.path.relpath(text_path, REPO),
        "text_sha256": hashlib.sha256(blob).hexdigest(),
        "pattern_order": [n for n, _ in VERSION_PATTERNS],
        "candidates": candidates,
        "candidate_count": len(candidates),
        "candidates_failing_byte_verification":
            [c for c in candidates if not c["verification"]["verified"]],
        "version_string": chosen["matched_text"] if chosen else None,
        "version_string_pattern": chosen["pattern_name"] if chosen else None,
        "version_string_byte_start": chosen["byte_start"] if chosen else None,
        "version_string_byte_end": chosen["byte_end"] if chosen else None,
        "version_string_verified_exact_substring": bool(chosen),
        "version_string_reason": (
            None if chosen else
            "no generic publication-version marker matched this artifact's "
            "extracted text; NONE IS SUPPLIED (amendment v2 change A2)"),
        "selection_rule": ("first byte-verified match of the first pattern that "
                           "matches, in the declared pattern order"),
    }


def prediction_check(obtained_sha256: str | None,
                     obtained_byte_length: int | None) -> dict:
    """Check the run's OWN retrieval against the amendment's recorded prediction.

    Amendment v2 records a sha256 and a byte length for
    https://arxiv.org/pdf/2003.10118 as a FALSIFIABLE PREDICTION, never as a
    value to copy.  This function therefore reads the amendment at run time,
    locates the predicted values programmatically, and reports ONLY the boolean
    comparison together with the BYTE OFFSETS at which a reviewer can read the
    prediction for themselves.  THE PREDICTED VALUES ARE DELIBERATELY NOT COPIED
    INTO THE RESULT: the run reports what it actually obtained, and a mismatch is
    reported as a finding rather than reconciled (TASK-20260808-7865e0).
    """
    with open(AMENDMENT_PATH, "rb") as fh:
        blob = fh.read()
    text = blob.decode("utf-8")
    hashes = [(mt.group(0), mt.start()) for mt in re.finditer(r"\b[0-9a-f]{64}\b", text)]
    lens = [(mt.group(1), mt.start(1))
            for mt in re.finditer(r"returns HTTP 200,\s*(\d+)\s*bytes", text)]
    out = {
        "amendment_path": os.path.relpath(AMENDMENT_PATH, REPO),
        "amendment_sha256": hashlib.sha256(blob).hexdigest(),
        "predicted_sha256_occurrences": len(hashes),
        "predicted_byte_length_occurrences": len(lens),
        "obtained_sha256": obtained_sha256,
        "obtained_byte_length": obtained_byte_length,
        "predicted_value_copied_into_this_record": False,
        "note": ("the predicted values are NOT reproduced here; they are located "
                 "by byte offset in the pinned amendment so a reviewer can read "
                 "them at the source. The run reports what it OBTAINED."),
    }
    if hashes:
        val, pos = hashes[0]
        out["predicted_sha256_byte_start"] = len(text[:pos].encode("utf-8"))
        out["predicted_sha256_byte_end"] = out["predicted_sha256_byte_start"] + 64
        out["obtained_sha256_matches_prediction"] = (obtained_sha256 == val)
    else:
        out["obtained_sha256_matches_prediction"] = None
    if lens:
        val, pos = lens[0]
        out["predicted_byte_length_byte_start"] = len(text[:pos].encode("utf-8"))
        out["predicted_byte_length_byte_end"] = (
            out["predicted_byte_length_byte_start"] + len(val))
        out["obtained_byte_length_matches_prediction"] = (
            obtained_byte_length is not None and int(val) == int(obtained_byte_length))
    else:
        out["obtained_byte_length_matches_prediction"] = None
    return out
