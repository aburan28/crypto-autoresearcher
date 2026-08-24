"""Executor driver for EXP-ICINV-fcb497 (GOAL-ENDO-001, TASK-20260807-f9c69c).

Runs the frozen contract's stages IN ITS DECLARED ORDER and writes one immutable
run package per stage.

    stage 0   THE BLOCKING GATE, RUN FIRST AND ALONE. Retrieve the square-root
              Velu source by curl over the frozen URL order, pin every byte
              stream by sha256, extract text, locate EVERY operation-count
              passage with the frozen search terms, re-verify each quotation as
              an exact byte-substring, and emit a verdict in
              {KERNEL_FIELD, BASE_FIELD, AMBIGUOUS, UNRETRIEVED_INFRA}.
              NONE OF THE FOUR IS AN ABORT: stages 1-4 run under every one.
    stage 1   the read-only barrier table over ledger/, knowledge/, analysis/
              and docs/, every quoted cell byte-verified against its artifact.
              THE TABLE ESCALATES; IT NEVER CORRECTS (AGENTS.md rule 4).
    stage 2   CONTROLS, BEFORE ANY MEASUREMENT IS READ: the planted control
              (d = r^2-1, lambda = r, must report m = 2) and the m = 1
              nearby-object fixture, both through the stage-3 code path.
    stage 3   one prime decade, three seeds. The matched null is WRITTEN TO THE
              RUN RECORD BEFORE the KS statistic is computed, and the KS input is
              read back from that written file (SR2, null-first).
    decide    the frozen decision rule, the concrete-cost table, the six tail
              checks, and the terminal states -- emitted BY THE RUN.

Usage:
    python3 -m harness.run_kerfield --stage 0
    python3 -m harness.run_kerfield --stage 1
    python3 -m harness.run_kerfield --stage 2
    python3 -m harness.run_kerfield --stage 3 --k 12
    python3 -m harness.run_kerfield --stage decide

NOTE, RECORDED RATHER THAN QUIETLY WORKED AROUND: `runner.write_run` emits only
six artifacts and hardcodes `requested_policy: executor-terra` in its inference
block, and this contract lists `harness/runner.py` under `reused_unmodified`
(editing it would also make this run INVALID under the contract's own
invalidation rules). This module therefore writes the manifest itself, reusing
`runner.git_state()`, `runner.environment()`, `runner.source_provenance()` and
`runner.untracked_source_vs_output()` verbatim so the revision, environment and
-- above all -- the BLOCKING `code.source` pinning block are produced by exactly
the committed code the campaign audits with
`tools/check_run_source_provenance.py`.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import re
import resource
import sys
import time
from datetime import datetime, timezone

import yaml

from . import exp_kerfield as ex
from . import runner
from . import velu_stage0 as s0

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_ID = ex.EXP_ID
RUNS_ROOT = os.path.join(REPO, "experiments", EXP_ID, "runs")
HANDOFF_ID = ex.HANDOFF_ID
BATCH_ID = None            # assigned by the Coordinator's snapshot task
WALL_CLOCK_CAP_SECONDS = 7200
MEMORY_CAP_BYTES = 4 * 1024 ** 3
MAXIMUM_RUNS = 12


# ---------------------------------------------------------------------------
# run packaging
# ---------------------------------------------------------------------------
def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def inference_block() -> dict:
    try:
        from orchestration.adapter.config import ADAPTER_VERSION
    except Exception:                                          # pragma: no cover
        ADAPTER_VERSION = None
    return {
        "requested_policy": ex.REQUESTED_POLICY,
        "canonical_policy": ex.REQUESTED_POLICY,
        "backend": os.environ.get("AUTORESEARCH_BACKEND"),
        "provider": None,
        "resolved_model_id": "claude-opus-5",
        "model_provenance": "operator-supplied",
        "model_verified": False,
        "model_verified_reason": (
            "no adapter probe receipt exists for this session; "
            "`python3 -m orchestration.adapter doctor --probe` was not run"),
        "requested_reasoning_effort": None,
        "reasoning_effort": None,
        "fallback_used": True,
        "fallback_reason": (
            "this Claude Code harness cannot resolve the policy aliases in "
            "orchestration/model-policies.yaml; every alias falls back to the one "
            "model the session runs on. Recorded, never silently substituted "
            "(AGENTS.md rule 11)."),
        "degraded_requirements": [],
        "independent_session": True,
        "independent_session_note": (
            "the Executor session is separate from the Coordinator session that "
            "drafted and approved the contract; under this harness that means "
            "independent context and a fresh reading, not a different model"),
        "adapter_version": ADAPTER_VERSION,
        "config_digest": None,
        "policy_env_present": bool(os.environ.get("AUTORESEARCH_POLICY")),
        "note": ("the measured numbers are produced by deterministic harness "
                 "code; no model is in the measurement loop"),
        "handoff_id": HANDOFF_ID,
    }


def prepare_run_dir(run_id: str) -> str:
    """Create the immutable run directory, refusing to clobber an existing id."""
    run_dir = os.path.join(RUNS_ROOT, run_id)
    if os.path.exists(run_dir):
        raise FileExistsError(
            f"run {run_id} already exists at {run_dir}; run records are immutable "
            f"-- supersede with a NEW run id, never overwrite")
    os.makedirs(run_dir, exist_ok=False)
    return run_dir


def write_artifact(run_dir: str, name: str, obj) -> dict:
    path = os.path.join(run_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return {"artifact": name, "sha256": _sha256_file(path),
            "written_at": _iso(time.time()), "bytes": os.path.getsize(path)}


def finalise_run(run_dir: str, run_id: str, *, stage: str, status: str,
                 command: str, started: float, finished: float, parameters: dict,
                 metrics: dict, raw: dict, stdout: str, stderr: str, valid: bool,
                 invalid_reason, curve_id: str, seed, deviations: list,
                 artifact_receipts: list, analytic_memory: dict,
                 certificate: dict | None = None) -> str:
    commit, dirty = runner.git_state()
    provenance = runner.source_provenance()
    if not provenance["all_pinned"]:
        raise RuntimeError(
            f"refusing to finalise {run_id}: code.source.all_pinned is false "
            f"(unreadable: {provenance['unreadable']}). An unpinned run is "
            f"INVALID under this contract (CORR-20260807-911ef7).")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)
    cert = dict(certificate or {"kind": "none"})
    cert.setdefault("verified", True)
    cert.setdefault("verifier", "no-claim")
    cert.setdefault("note", "PURE MEASUREMENT / LITERATURE RUN: this experiment "
                            "claims no discrete-log solve and no factor-base "
                            "relation, so certificate.kind is explicitly none "
                            "(docs/claims-and-verification.md)")
    cert["verifier_commit"] = commit

    memory = dict(analytic_memory)
    memory["measured_peak_rss_bytes"] = peak_rss
    memory["basis_measured_peak_rss"] = "measured"
    ratio = peak_rss / memory["analytic_peak_bytes"] if memory["analytic_peak_bytes"] else None
    memory["ratio_measured_over_analytic"] = ratio
    lo, hi = ex.MEMORY_RECONCILIATION_BAND
    memory["within_band"] = bool(ratio is not None and lo <= ratio <= hi)
    memory["band"] = [lo, hi]
    if not memory["within_band"]:
        memory["diagnosis"] = (
            "REPORTED, NOT ABSORBED: the measured/analytic ratio is outside "
            f"[{lo}, {hi}]. The analytic model sizes only the declared data "
            "structures plus a fixed interpreter baseline; a ratio below the band "
            "means the baseline constant is too large for this stage's actual "
            "resident set, a ratio above it means a structure was under-sized.")

    manifest = {"run": {
        "id": run_id,
        "experiment_id": EXP_ID,
        "hypothesis_id": ex.HYPOTHESIS_ID,
        "goal_id": ex.GOAL_ID,
        "handoff_id": HANDOFF_ID,
        "batch_id": BATCH_ID,
        "stage": stage,
        "status": status,
        "code": {"commit": commit, "dirty": dirty, "command": command,
                 "source": provenance,
                 "untracked": runner.untracked_source_vs_output()},
        "inference": inference_block(),
        "environment": runner.environment(),
        "inputs": {"curve_id": curve_id, "seed": seed, "parameters": parameters},
        "timing": {"started_at": _iso(started), "finished_at": _iso(finished),
                   "wall_seconds": round(finished - started, 6),
                   "wall_clock_cap_seconds": WALL_CLOCK_CAP_SECONDS,
                   "within_cap": (finished - started) <= WALL_CLOCK_CAP_SECONDS},
        "resources": {"peak_rss_bytes": peak_rss,
                      "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 6),
                      "memory_cap_bytes": MEMORY_CAP_BYTES,
                      "memory_reconciliation": memory},
        "result": {"metrics": metrics, "valid": valid,
                   "invalid_reason": invalid_reason,
                   "certificate": {"kind": cert.get("kind"),
                                   "verified": cert.get("verified"),
                                   "verifier": cert.get("verifier"),
                                   "note": cert.get("note")}},
        "protocol_deviations": deviations,
        "artifacts": {"command": "command.txt", "environment": "environment.json",
                      "stdout": "stdout.log", "stderr": "stderr.log",
                      "raw_result": "raw-result.json",
                      "extra": artifact_receipts},
    }}

    def _w(name, content):
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as fh:
            fh.write(content)

    _w("manifest.yaml", yaml.safe_dump(manifest, sort_keys=False, width=100,
                                       allow_unicode=True))
    _w("command.txt", command + "\n")
    _w("environment.json", json.dumps(runner.environment(), indent=2, sort_keys=True))
    _w("stdout.log", stdout)
    _w("stderr.log", stderr)
    with open(os.path.join(run_dir, "raw-result.json"), "w", encoding="utf-8") as fh:
        json.dump({"metrics": metrics, "certificate": cert, "raw": raw},
                  fh, indent=1, sort_keys=True, default=str)
    return run_dir


class Tee(io.TextIOBase):
    def __init__(self, stream):
        self.stream = stream
        self.buf = io.StringIO()

    def write(self, s):
        self.stream.write(s)
        self.buf.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()


# ---------------------------------------------------------------------------
# STAGE 0
# ---------------------------------------------------------------------------
def stage0(run_dir: str, supersedes: str | None = None) -> tuple[dict, list, list]:
    receipts, deviations = [], []
    src_dir = os.path.join(run_dir, "sources")
    os.makedirs(src_dir, exist_ok=True)
    attribution = s0.attribution_from_contract()
    term_guard = s0.check_terms_against_contract()
    artifacts = []

    plan = [("primary", u) for u in s0.PRIMARY_URLS]
    for path in s0.FALLBACK_PATHS:
        role = "fallback_corpus_note" if not path.startswith("http") else "fallback_paper"
        plan.append((role, path))

    for role, loc in plan:
        label = re.sub(r"[^A-Za-z0-9]+", "-", loc).strip("-")[-60:]
        raw_dest = os.path.join(src_dir, f"{label}.raw")
        if loc.startswith("http"):
            fetch = s0.curl_fetch(loc, raw_dest)
        else:
            fetch = s0.copy_local(loc, raw_dest)
        entry = {"role": role, "label": label, "location": loc, "fetch": fetch,
                 "text": None, "full_text": None, "passages": [],
                 "attribution_check": None}
        if fetch["ok"]:
            text = s0.extract_text(raw_dest, os.path.join(src_dir, f"{label}.txt"))
            entry["text"] = text
            entry["full_text"] = s0.is_full_text(fetch, text)
            if text["ok"]:
                tp = os.path.join(REPO, text["text_path"])
                found = s0.find_passages(tp)
                entry["passage_search"] = {k: v for k, v in found.items()
                                           if k != "passages"}
                with open(tp, encoding="utf-8", errors="replace") as fh:
                    document = fh.read()
                for p in found["passages"]:
                    p["classification"] = s0.classify_passage(p["context"], document)
                    p["verification"] = s0.verify_quote(
                        tp, p["context"], p["context_byte_start"],
                        p["context_byte_end"])
                entry["passages"] = found["passages"]
                entry["attribution_check"] = s0.attribution_check(tp, attribution)
        else:
            entry["full_text"] = {"is_full_text": False,
                                  "reason": "not retrieved"}
            if loc.startswith("http") and fetch.get("http_status") not in (200, None):
                deviations.append({
                    "kind": "infrastructure_outcome",
                    "where": f"STAGE 0 retrieval of {loc}",
                    "observed": f"HTTP {fetch.get('http_status')} "
                                f"({fetch.get('content_type')})",
                    "classification": "infrastructure_error",
                    "consequence": "recorded as a retrieval failure for this URL; "
                                   "NEVER read as a BASE_FIELD verdict "
                                   "(AGENTS.md rule 5)",
                })
        artifacts.append(entry)

    verdict = s0.decide(artifacts)
    # The full quotation tail: EVERY operation-count passage found, not only the
    # one the verdict rests on (tail_checks, STAGE-0 QUOTATION TAIL).
    tail = [{"source": a["label"], "role": a["role"],
             "text_sha256": (a["text"] or {}).get("sha256"),
             "term_matches": p["terms"], "label": p["classification"]["label"],
             "label_with_document_context":
                 p["classification"].get("label_with_document_context"),
             "kernel_rationality_in_document":
                 p["classification"].get("kernel_rationality_in_document"),
             "field_tokens": p["classification"]["field_tokens"],
             "kernel_rationality_markers": p["classification"]["kernel_rationality_markers"],
             "byte_start": p["context_byte_start"], "byte_end": p["context_byte_end"],
             "context_chars": p["context_chars"],
             "verified_exact_substring": p["verification"]["verified"],
             "context": p["context"]}
            for a in artifacts for p in a["passages"]]
    unverified = [t for t in tail if not t["verified_exact_substring"]]

    out = {
        "experiment_id": EXP_ID, "stage": "0",
        "supersedes_run": supersedes,
        "supersession_note": (
            "RECORDED, NOT HIDDEN: this run supersedes " + supersedes +
            ", which is RETAINED UNEDITED. The superseded run's retrieval, "
            "pinning, offsets and byte verification are unchanged and its verdict "
            "is identical; what it got wrong is a CLASSIFIER DEFECT in the "
            "quotation tail -- a kernel-rationality qualification lying in the "
            "same sentence but outside the frozen 400-character window made "
            "kernel-qualified passages of 2020/341 read `base_field`. The repair "
            "adds a document-level flag beside the window label and cannot move "
            "the verdict, which is gated on retrieving a full text in either "
            "version." if supersedes else None),
        "verdict": verdict["verdict"], "verdict_detail": verdict,
        "frozen_branch_rules_applied": {
            "evaluation_order": list(s0.VERDICTS),
            "determinate_verdict_requires_full_text": True,
            "corpus_note_can_only_return_AMBIGUOUS": True,
            "background_knowledge_prohibition": (
                "the verdict cites ONLY pinned artifacts; no remembered sentence "
                "from any paper appears in this record or in the code that made "
                "it (CORR-20260807-a24675, AGENTS.md rule 9)"),
        },
        "sources": [{k: v for k, v in a.items() if k != "passages"} for a in artifacts],
        "attribution": attribution,
        "search_term_guard": term_guard,
        "quotation_tail": tail,
        "quotation_tail_count": len(tail),
        "quotations_failing_byte_verification": unverified,
        "operation_count_passages": [t for t in tail
                                     if t["label"] in ("kernel_field", "base_field",
                                                       "field_unspecified")],
    }
    receipts.append(write_artifact(run_dir, "stage0-verdict.json", out))
    return out, receipts, deviations


# ---------------------------------------------------------------------------
# STAGE 1 -- the read-only barrier table
# ---------------------------------------------------------------------------
BARRIER_TERMS = ("Velu", "velu", "isogeny evaluation", "evaluate the isogeny",
                 "degree-d isogeny", "degree d isogeny", "kernel polynomial",
                 "Otilde(d)", "O(d)", "action step", "class group action",
                 "CSIDH", "isogeny walk step")
BARRIER_ROOTS = ("ledger", "knowledge", "analysis", "docs")
_COST_RE = re.compile(
    r"(Otilde|\\tilde\{O\}|\\widetilde\{O\}|O~|Õ|\bO\s*\(|p\^\{?[0-9/]+"
    r"|\bsqrt\s*\(|sqrt\s+[a-zA-Z]|\bexponent\b)", re.I)
_PER_EVAL_RE = re.compile(
    r"(field operation|group operation|multiplication|per evaluation|inside one "
    r"evaluation|kernel polynomial|isogeny evaluation|evaluate the isogeny)", re.I)
_COUNTS_EVALUATIONS_RE = re.compile(
    r"(evaluations?\b|action step|walk step|steps?\b|queries|class member)", re.I)
_SMALL_ELL_RE = re.compile(r"(small (prime|degree)|polylog|ell in|\bCSIDH\b|"
                           r"degree-?\s*\\?ell|prime norm)", re.I)
_THETA_P_RE = re.compile(r"(Theta\(p\)|~\s*p\b|degree\s*d\s*~\s*p|\|D\|/4)", re.I)
_KERNEL_FIELD_STATED_RE = re.compile(
    r"(F_\{p\^m\}|F_\{q\^|rational kernel|kernel.{0,40}rational|"
    r"field of definition of.{0,40}kernel|m\s*=\s*ord)", re.I)


def _iter_corpus_files():
    for root in BARRIER_ROOTS:
        for dp, dns, fns in os.walk(os.path.join(REPO, root)):
            dns[:] = [d for d in dns if d != ".git"]
            for fn in fns:
                if fn.endswith((".md", ".yaml", ".yml", ".json", ".txt")):
                    yield os.path.join(dp, fn)


def _quote_at(path: str, char_start: int, char_end: int) -> dict:
    with open(path, "rb") as fh:
        blob = fh.read()
    text = blob.decode("utf-8", errors="replace")
    quote = text[char_start:char_end]
    bs = len(text[:char_start].encode("utf-8"))
    be = bs + len(quote.encode("utf-8"))
    ok = blob[bs:be] == quote.encode("utf-8")
    return {"quote": quote, "byte_start": bs, "byte_end": be,
            "artifact_sha256": hashlib.sha256(blob).hexdigest(),
            "byte_verified_exact_substring": bool(ok and quote.encode() in blob),
            "artifact_path": os.path.relpath(path, REPO)}


def _classify_barrier_row(ctx: str, stage0_verdict: str) -> dict:
    counts_evals = bool(_COUNTS_EVALUATIONS_RE.search(ctx))
    per_eval = bool(_PER_EVAL_RE.search(ctx))
    if _SMALL_ELL_RE.search(ctx):
        regime = "small_prime_ell (polylog degree)"
    elif _THETA_P_RE.search(ctx):
        regime = "degree Theta(p)"
    else:
        regime = "undetermined"
    kernel_field = ("stated in the artifact" if _KERNEL_FIELD_STATED_RE.search(ctx)
                    else "unknown")
    if counts_evals and not per_eval:
        applies = "no"
        corrected = "unchanged: the figure counts EVALUATIONS/steps, not field " \
                    "operations inside one isogeny evaluation"
        changed = "no"
        reason = ("the quoted figure is a count of action/isogeny EVALUATIONS or "
                  "walk steps; the square-root Velu correction multiplies the cost "
                  "INSIDE one evaluation and therefore cannot move this exponent")
        rule = "R1-counts-evaluations"
    elif stage0_verdict != "KERNEL_FIELD":
        applies = "undetermined"
        corrected = "undetermined"
        changed = "undetermined"
        reason = (f"STAGE-0 verdict is {stage0_verdict}: NO COST STATEMENT MAY BE "
                  "MADE IN EITHER DIRECTION for a figure that counts field "
                  "operations inside one isogeny evaluation")
        rule = "R2-stage0-not-determinate"
    elif regime.startswith("small_prime_ell") and kernel_field != "unknown":
        applies = "yes"
        corrected = "unchanged: m = O(1) on a rational kernel, so Otilde(sqrt(ell)*m) " \
                    "= Otilde(sqrt ell)"
        changed = "no"
        reason = "small-ell rational-kernel regime; the correction factor m is O(1)"
        rule = "R3-small-ell-rational-kernel"
    else:
        applies = "undetermined"
        corrected = "undetermined"
        changed = "undetermined"
        reason = "kernel field of definition not stated in the artifact; never guessed"
        rule = "R4-kernel-field-unknown"
    return {"degree_regime": regime, "kernel_field_of_definition": kernel_field,
            "sqrt_velu_applies": applies, "corrected_cost": corrected,
            "exponent_changed": changed, "reason": reason,
            "classification_rule": rule,
            "counts_evaluations": counts_evals,
            "counts_field_ops_inside_one_evaluation": per_eval}


REQUIRED_ROW_ANCHORS = (
    {"row_id": "REQ-1-c36472-transport",
     "artifact": "ledger/proposals/IDEA-20260807-c36472.yaml",
     "anchor": r"\[open\] The Otilde\(p\^\{1/4\}\)[^\n]*(\n[^\n]*){0,3}",
     "note": "IDEA-20260807-c36472's Otilde(p^{1/4}) TRANSPORT figure. Its own "
             "[open] mark is carried forward UNDISCHARGED by this table."},
    {"row_id": "REQ-2-c36472-identification",
     "artifact": "ledger/proposals/IDEA-20260807-c36472.yaml",
     "anchor": r"h ~ p\^\{1/2\} class members[^\n]*(\n[^\n]*){0,3}",
     "note": "the h ~ p^{1/2} IDENTIFICATION cost that IDEA-20260807-c36472 names "
             "as the real T5 barrier."},
)


def stage1(run_dir: str, stage0_verdict: str) -> tuple[dict, list, list]:
    rows, deviations = [], []
    for path in sorted(_iter_corpus_files()):
        rel = os.path.relpath(path, REPO)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            deviations.append({"kind": "unreadable_corpus_file", "path": rel,
                               "error": str(exc),
                               "classification": "infrastructure_error"})
            continue
        seen = set()
        for term in BARRIER_TERMS:
            for m in re.finditer(re.escape(term), text):
                lo = max(0, m.start() - 200)
                hi = min(len(text), m.end() + 200)
                ctx = text[lo:hi]
                if not _COST_RE.search(ctx):
                    continue
                key = (lo // 200, hi // 200)
                if key in seen:
                    continue
                seen.add(key)
                q = _quote_at(path, lo, hi)
                cls = _classify_barrier_row(ctx, stage0_verdict)
                rows.append({
                    "record_id": _record_id(rel, text),
                    "artifact_path": rel,
                    "matched_term": term,
                    "quoted_charged_cost": q["quote"],
                    "quotation_basis": "quoted_from_record",
                    "quotation_byte_start": q["byte_start"],
                    "quotation_byte_end": q["byte_end"],
                    "artifact_sha256": q["artifact_sha256"],
                    "byte_verified": q["byte_verified_exact_substring"],
                    **cls,
                    "corrected_cost_basis": "modeled",
                })
    required = []
    for spec in REQUIRED_ROW_ANCHORS:
        path = os.path.join(REPO, spec["artifact"])
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        m = re.search(spec["anchor"], text)
        if m is None:
            deviations.append({"kind": "required_row_anchor_not_found",
                               "row_id": spec["row_id"], "artifact": spec["artifact"],
                               "classification": "implementation_error"})
            continue
        lo = max(0, m.start() - 200)
        hi = min(len(text), m.end() + 200)
        q = _quote_at(path, lo, hi)
        cls = _classify_barrier_row(q["quote"], stage0_verdict)
        if spec["row_id"] == "REQ-1-c36472-transport":
            cls.update({
                "sqrt_velu_applies": "no",
                "corrected_cost": "unchanged at Otilde(p^{1/4})",
                "exponent_changed": "no",
                "reason": ("the figure counts ACTION EVALUATIONS and not field "
                           "operations inside one evaluation, so a correction to "
                           "the cost of one evaluation cannot move this exponent "
                           "(contract barrier_table_frozen.required_rows)"),
                "classification_rule": "R0-required-row-contract-prescribed",
            })
        required.append({
            "row_id": spec["row_id"], "record_id": "IDEA-20260807-c36472",
            "artifact_path": spec["artifact"], "note": spec["note"],
            "quoted_charged_cost": q["quote"], "quotation_basis": "quoted_from_record",
            "quotation_byte_start": q["byte_start"], "quotation_byte_end": q["byte_end"],
            "artifact_sha256": q["artifact_sha256"],
            "byte_verified": q["byte_verified_exact_substring"],
            "open_mark_carried_forward": "[open]" in q["quote"],
            **cls, "corrected_cost_basis": "modeled",
        })
    allrows = required + rows
    changed = [r for r in allrows if r["exponent_changed"] == "yes"]
    undet = [r for r in allrows if r["exponent_changed"] == "undetermined"]
    unverified = [r for r in allrows if not r["byte_verified"]]
    audit_outcome = ("OUTCOME_STALE_BARRIER" if changed else
                     "OUTCOME_AUDIT_PARTIAL" if undet else "OUTCOME_AUDIT_CLEAN")
    table = {
        "experiment_id": EXP_ID, "stage": "1",
        "stage0_verdict_used": stage0_verdict,
        "scope": {"roots": list(BARRIER_ROOTS), "terms": list(BARRIER_TERMS),
                  "read_only": True},
        "no_edit_authority": ("THE TABLE MAY NOT EDIT, CORRECT OR SUPERSEDE ANY "
                              "OTHER RECORD. A row with exponent_changed = yes is "
                              "ESCALATED to the Coordinator (AGENTS.md rule 4)."),
        "columns": ["record_id", "artifact_path", "quoted_charged_cost",
                    "degree_regime", "kernel_field_of_definition",
                    "sqrt_velu_applies", "corrected_cost", "exponent_changed",
                    "reason"],
        "required_rows": required,
        "rows": rows,
        "row_count": len(allrows),
        "M4_exponent_changed_count": len(changed),
        "M4_undetermined_count": len(undet),
        "rows_failing_byte_verification": len(unverified),
        "audit_outcome": audit_outcome,
        "undetermined_rows_what_is_missing": sorted({
            r["reason"] for r in undet}),
    }
    receipts = [write_artifact(run_dir, "barrier-table.json", table)]
    md = _barrier_markdown(table)
    path = os.path.join(run_dir, "barrier-table.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(md)
    receipts.append({"artifact": "barrier-table.md", "sha256": _sha256_file(path),
                     "written_at": _iso(time.time()),
                     "bytes": os.path.getsize(path)})
    return table, receipts, deviations


def _record_id(rel: str, text: str) -> str:
    m = re.search(r"^\s*id:\s*([A-Z][A-Z0-9-]+-[A-Za-z0-9]+)", text, re.M)
    if m:
        return m.group(1)
    base = os.path.basename(rel)
    return os.path.splitext(base)[0]


def _barrier_markdown(table: dict) -> str:
    def esc(s):
        return str(s).replace("|", "\\|").replace("\n", " ")[:400]
    lines = [
        "# Barrier table -- EXP-ICINV-fcb497 STAGE 1",
        "",
        "READ-ONLY AUDIT. This table ESCALATES; it never corrects "
        "(AGENTS.md rule 4).",
        "",
        f"- STAGE-0 verdict used: `{table['stage0_verdict_used']}`",
        f"- rows: {table['row_count']}",
        f"- M4 exponent_changed = yes: {table['M4_exponent_changed_count']}",
        f"- M4 undetermined: {table['M4_undetermined_count']}",
        f"- audit outcome: **{table['audit_outcome']}**",
        "",
        "`quoted_charged_cost` cells are read from the cited artifact AT RUN TIME "
        "and byte-verified against it (basis: quoted_from_record). "
        "`corrected_cost` cells are basis: modeled.",
        "",
        "| record_id | artifact_path | quoted_charged_cost | degree_regime | "
        "kernel_field_of_definition | sqrt_velu_applies | corrected_cost | "
        "exponent_changed | reason |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in table["required_rows"] + table["rows"]:
        lines.append("| " + " | ".join(esc(r[c]) for c in
                     ["record_id", "artifact_path", "quoted_charged_cost",
                      "degree_regime", "kernel_field_of_definition",
                      "sqrt_velu_applies", "corrected_cost", "exponent_changed",
                      "reason"]) + " |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# STAGE 2 -- controls
# ---------------------------------------------------------------------------
def stage2(run_dir: str) -> tuple[dict, list, list]:
    ladder = ex.prime_ladder()
    p12 = ladder[0]["p"]
    planted = ex.planted_control()
    fixture = ex.m1_fixture(p12, ex.SEEDS[0])
    controls = {
        "experiment_id": EXP_ID, "stage": "2",
        "order": ["planted control", "m = 1 nearby-object fixture"],
        "sr2_note": ("controls are run and WRITTEN TO THE RUN RECORD before any "
                     "STAGE-3 distribution or KS statistic is read "
                     "(docs/inventor-protocol.md, controls before belief)"),
        "prime_ladder": ladder,
        "M3_planted_control": planted,
        "M6_m1_fixture": fixture,
        "verification_summary": {
            "planted_rows": len(planted["rows"]),
            "planted_all_m_equals_2": all(r["m"] == 2 for r in planted["rows"]),
            "fixture_curves": len(fixture["curves"]),
            "fixture_pairs": sum(len(c["ells"]) for c in fixture["curves"]),
            "fixture_all_pass": fixture["verdict"] == "PASS",
        },
        "blocking": ("a failed planted control INVALIDATES the run set and no null "
                     "it reports may be cited; a failed m = 1 fixture invalidates "
                     "the cost accounting"),
    }
    receipts = [write_artifact(run_dir, "controls.json", controls)]
    devs = []
    if planted["verdict"] != "PASS":
        devs.append({"kind": "blocking_control_failure", "control": "planted",
                     "classification": "invalid_measurement"})
    if fixture["verdict"] != "PASS":
        devs.append({"kind": "blocking_control_failure", "control": "m1_fixture",
                     "classification": "invalid_measurement"})
    if fixture["substitutions_declared"]:
        devs.append({
            "kind": "declared_substitution",
            "where": "m = 1 fixture curve selection",
            "detail": f"{len(fixture['substitutions_declared'])} curves of the "
                      "frozen stream were skipped with a recorded shortfall reason "
                      "before three curves with three qualifying ell were found; "
                      "the contract's fixture rule prescribes exactly this "
                      "substitution and requires it to be declared",
            "classification": "protocol_declared_substitution"})
    return controls, receipts, devs


# ---------------------------------------------------------------------------
# STAGE 3 -- one decade, three seeds, NULL WRITTEN BEFORE KS IS READ
# ---------------------------------------------------------------------------
def stage3(run_dir: str, k: int, controls_ref: dict) -> tuple[dict, list, list]:
    ladder = {r["k"]: r for r in ex.prime_ladder()}
    p = ladder[k]["p"]
    devs = []
    per_seed = {}
    t0 = time.time()
    for seed in ex.SEEDS:
        dr = ex.measure_decade(p, k, seed)
        per_seed[str(seed)] = dr
        print(f"  seed {seed}: n={len(dr.instances)} excluded={len(dr.exclusions)} "
              f"attempts={dr.attempts} ({time.time() - t0:.1f}s)")

    # ---- PHASE 1: write the per-instance table and the MATCHED NULL first ----
    per_instance = {
        "experiment_id": EXP_ID, "stage": "3", "k": k, "p": p,
        "ladder_entry": ladder[k],
        "seeds": list(ex.SEEDS),
        "per_seed": {s: {"instances": dr.instances, "exclusions": dr.exclusions,
                         "attempts": dr.attempts,
                         "achieved_n": len(dr.instances)}
                     for s, dr in per_seed.items()},
        "controls_reference": controls_ref,
    }
    receipts = [write_artifact(run_dir, "per-instance-measurements.json", per_instance)]

    null_payload = {
        "experiment_id": EXP_ID, "stage": "3", "k": k, "p": p,
        "written_before_any_ks_statistic_was_computed": True,
        "matched_on": "the SAME d as the curve-derived instance (frozen)",
        "stream": 'a = int(sha256(f"{seed}:null:{p}:{i}"),16) mod d, redrawn while '
                  'gcd(a, d) > 1 (redraw tag ":r{j}", declared)',
        "per_seed": {s: [{"index": i["index"], "d": i["d"], "null_a": i["null_a"],
                          "null_redraws": i["null_redraws"], "null_m": i["null_m"],
                          "null_order_ok": i["null_order_ok"],
                          "null_log_m_over_log_d": i["null_log_m_over_log_d"]}
                         for i in dr.instances]
                     for s, dr in per_seed.items()},
    }
    null_receipt = write_artifact(run_dir, "matched-null.json", null_payload)
    receipts.append(null_receipt)
    null_written_at = time.time()

    # ---- PHASE 2: read the null BACK FROM DISK and only now compute the KS ----
    with open(os.path.join(run_dir, "matched-null.json"), encoding="utf-8") as fh:
        null_from_disk = json.load(fh)
    ks_started = time.time()

    dists = {"experiment_id": EXP_ID, "stage": "3", "k": k, "p": p,
             "null_first_ordering": {
                 "matched_null_sha256": null_receipt["sha256"],
                 "matched_null_written_at": _iso(null_written_at),
                 "ks_computed_at": _iso(ks_started),
                 "ks_input_source": "matched-null.json read back from disk",
                 "sr2_satisfied": True},
             "per_seed": {}}
    for seed_s, dr in per_seed.items():
        curve_v = [i["log_m_over_log_d"] for i in dr.instances
                   if i["order_pow_check"] and i["order_minimality_check"]]
        nulls = null_from_disk["per_seed"][seed_s]
        null_v = [z["null_log_m_over_log_d"] for z in nulls if z["null_order_ok"]]
        n = len(dr.instances)
        excl = len(dr.exclusions)
        degenerate = sum(1 for i in dr.instances if not i["minimiser_admissible"])
        strata = {}
        for b in ex.CONDUCTOR_BINS:
            cv = [i["log_m_over_log_d"] for i in dr.instances
                  if i["conductor_bin"] == b]
            nv = [i["null_log_m_over_log_d"] for i in dr.instances
                  if i["conductor_bin"] == b]
            strata[b] = {"n": len(cv), "curve": ex.quantiles(cv),
                         "null": ex.quantiles(nv),
                         "ks": ex.ks_two_sample(cv, nv) if cv else None}
        dists["per_seed"][seed_s] = {
            "achieved_n": n,
            "verdict_yielding": n >= ex.CURVES_PER_DECADE_FLOOR,
            "floor": ex.CURVES_PER_DECADE_FLOOR,
            "M1_curve": ex.quantiles(curve_v),
            "null": ex.quantiles(null_v),
            "M2_ks": ex.ks_two_sample(curve_v, null_v),
            "M5_degenerate_fraction": degenerate / n if n else None,
            "M5_excluded_curve_fraction": excl / (n + excl) if (n + excl) else 0.0,
            "excluded_count": excl,
            "exclusion_reasons": sorted({e["reason"][:60] for e in dr.exclusions}),
            "d_over_p": ex.quantiles([i["d_over_p"] for i in dr.instances]),
            "window_spread": ex.quantiles([i["window_spread_log_m_over_log_d"]
                                           for i in dr.instances
                                           if i["window_spread_log_m_over_log_d"]
                                           is not None]),
            "ecdf_curve": ex.ecdf(curve_v),
            "ecdf_null": ex.ecdf(null_v),
            "conductor_strata": strata,
            "factorisation_verification": {
                "instances_with_verified_d_factorisation":
                    sum(1 for i in dr.instances if i["d_factorisation_verified"]),
                "instances_with_verified_order":
                    sum(1 for i in dr.instances
                        if i["order_pow_check"] and i["order_minimality_check"]),
                "all_verified": all(i["d_factorisation_verified"]
                                    and i["order_pow_check"]
                                    and i["order_minimality_check"]
                                    for i in dr.instances),
            },
            "collisions_d_m": _collisions(dr.instances),
            "smallest_5_log_m_over_log_d": _small_tail(dr.instances),
            "O_minimal_secondary": _o_minimal_secondary(dr.instances),
        }
    receipts.append(write_artifact(run_dir, "distributions.json", dists))
    if any(v["achieved_n"] < ex.CURVES_PER_DECADE_FLOOR
           for v in dists["per_seed"].values()):
        devs.append({"kind": "sample_size_floor_not_met", "k": k,
                     "classification": "negative_observation",
                     "detail": "a seed at this decade yielded fewer than "
                               f"{ex.CURVES_PER_DECADE_FLOOR} admissible "
                               "instances; SR4 gives it NO distributional verdict"})
    return {"per_instance": per_instance, "distributions": dists}, receipts, devs


def _collisions(instances: list) -> dict:
    seen: dict[tuple[int, int], int] = {}
    for i in instances:
        key = (i["d"], i["m"])
        seen[key] = seen.get(key, 0) + 1
    coll = {f"{d}:{m}": c for (d, m), c in seen.items() if c > 1}
    return {"distinct_d_m_pairs": len(seen), "colliding_pairs": len(coll),
            "collisions": dict(sorted(coll.items(), key=lambda z: -z[1])[:25]),
            "note": ("the observation-collision artifact required by "
                     "H-ICINV-82ee6a's proof_search_map: collisions FORBID any use "
                     "of (d, m) as an identifying invariant")}


def _small_tail(instances: list) -> list:
    rows = sorted(instances, key=lambda i: i["log_m_over_log_d"])[:5]
    out = []
    for i in rows:
        fac = {int(k): v for k, v in i["d_factorisation"].items()}
        try:
            frac = ex.unit_order_cdf_fraction(fac, i["m"])
        except Exception as exc:                             # pragma: no cover
            frac = f"uncomputed: {type(exc).__name__}"
        out.append({k: i[k] for k in ("index", "p", "a", "b", "t", "D", "f", "u",
                                      "v", "d", "lambda", "m",
                                      "log_m_over_log_d")}
                   | {"exact_fraction_of_units_with_order_at_most_m": frac})
    return out


def _o_minimal_secondary(instances: list) -> dict:
    """O-minimal non-scalar degree where f <= 100 (DECLARED SECONDARY).

    For Z[pi] of conductor f in the maximal order O, the minimal non-scalar
    degree over O is smaller by a factor f^2 in the leading term: the Z[pi]
    minimum is ~ |D|/4 = f^2 |D_0|/4 while the O minimum is ~ |D_0|/4. The ratio
    MEASURES the size of the contract's declared scope narrowing.
    """
    rows = []
    for i in instances:
        f = i["f"]
        if not f or f > ex.CONDUCTOR_SECONDARY_BOUND:
            continue
        D0 = i["fundamental_discriminant"]
        o_min = abs(D0) / 4.0
        rows.append({"index": i["index"], "f": f, "z_pi_minimal_d": i["d"],
                     "O_minimal_degree_leading_term": o_min,
                     "ratio_Zpi_over_O": i["d"] / o_min if o_min else None})
    ratios = [r["ratio_Zpi_over_O"] for r in rows if r["ratio_Zpi_over_O"]]
    return {"n": len(rows), "bound": ex.CONDUCTOR_SECONDARY_BOUND,
            "ratio_quantiles": ex.quantiles(ratios),
            "basis": "modeled (leading term |D_0|/4; no O-arithmetic performed)",
            "sample": rows[:10]}


# ---------------------------------------------------------------------------
# decide
# ---------------------------------------------------------------------------
def _load(run_id: str, artifact: str) -> tuple[dict, str]:
    path = os.path.join(RUNS_ROOT, run_id, artifact)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), _sha256_file(path)


def decide(run_dir: str, stage_runs: dict) -> tuple[dict, list, list]:
    devs = []
    s0v, s0h = _load(stage_runs["stage0"], "stage0-verdict.json")
    bt, bth = _load(stage_runs["stage1"], "barrier-table.json")
    ct, cth = _load(stage_runs["stage2"], "controls.json")
    decades = {}
    for k, rid in stage_runs["stage3"].items():
        d, h = _load(rid, "distributions.json")
        decades[int(k)] = {"run_id": rid, "sha256": h, "distributions": d}

    ks_sorted = sorted(decades)
    # per-seed decade medians and verdict-yielding flags
    seedwise = {}
    for seed in ex.SEEDS:
        s = str(seed)
        rows = []
        for k in ks_sorted:
            ps = decades[k]["distributions"]["per_seed"][s]
            rows.append({
                "k": k, "p": decades[k]["distributions"]["p"],
                "achieved_n": ps["achieved_n"],
                "verdict_yielding": ps["verdict_yielding"],
                "median_log_m_over_log_d": ps["M1_curve"].get("median"),
                "null_median": ps["null"].get("median"),
                "ks_D": ps["M2_ks"]["D"], "ks_critical": ps["M2_ks"]["critical_value"],
                "ks_below_critical": ps["M2_ks"]["below_critical"],
                "ks_direction": ps["M2_ks"]["direction"],
                "ks_resolvable": ps["M2_ks"]["resolvable"],
                "degenerate_fraction": ps["M5_degenerate_fraction"],
                "excluded_fraction": ps["M5_excluded_curve_fraction"],
                "factorisation_all_verified":
                    ps["factorisation_verification"]["all_verified"],
            })
        vy = [r for r in rows if r["verdict_yielding"]]
        largest = vy[-1] if vy else None
        med_seq = [r["median_log_m_over_log_d"] for r in vy]
        top3 = vy[-3:]
        criteria = {
            "verdict_yielding_decades": len(vy),
            "median_at_largest": largest["median_log_m_over_log_d"] if largest else None,
            "median_at_largest_ge_0.75": bool(largest and
                                              largest["median_log_m_over_log_d"] >= 0.75),
            "max_median": max(med_seq) if med_seq else None,
            "fall_from_max_to_largest": (max(med_seq) - med_seq[-1]) if med_seq else None,
            "fall_le_0.05": bool(med_seq and (max(med_seq) - med_seq[-1]) <= 0.05),
            "ks_below_critical_in_top3": sum(1 for r in top3 if r["ks_below_critical"]),
            "ks_below_critical_at_least_2_of_3": sum(
                1 for r in top3 if r["ks_below_critical"]) >= 2,
            "degenerate_fraction_max": max((r["degenerate_fraction"] or 0)
                                           for r in vy) if vy else None,
            "degenerate_le_0.20": all((r["degenerate_fraction"] or 0) <=
                                      ex.DEGENERATE_INVALIDATION_FRACTION for r in vy),
            "ks_significant_deficit_in_top3": sum(
                1 for r in top3
                if (not r["ks_below_critical"]) and "DEFICIT" in (r["ks_direction"] or "")),
            "median_at_largest_lt_0.5": bool(largest and
                                             largest["median_log_m_over_log_d"] < 0.5),
            "median_rising": bool(len(med_seq) >= 2 and med_seq[-1] > med_seq[0]),
            "median_flat_or_decreasing": bool(
                len(med_seq) >= 2 and (med_seq[-1] - med_seq[0]) <= 0.01),
            "factorisation_control_passes": all(r["factorisation_all_verified"]
                                                for r in rows),
        }
        criteria["OUTCOME_NULL_fires"] = bool(
            criteria["median_at_largest_ge_0.75"] and criteria["fall_le_0.05"]
            and criteria["ks_below_critical_at_least_2_of_3"]
            and criteria["degenerate_le_0.20"])
        criteria["OUTCOME_FAMILY_fires"] = bool(
            ((criteria["median_at_largest_lt_0.5"] and not criteria["median_rising"])
             or criteria["ks_significant_deficit_in_top3"] >= 2)
            and criteria["factorisation_control_passes"]
            and not criteria["median_flat_or_decreasing"])
        criteria["OUTCOME_INSTRUMENT_fires"] = bool(
            criteria["median_flat_or_decreasing"]
            and criteria["factorisation_control_passes"])
        seedwise[s] = {"rows": rows, "criteria": criteria}

    def votes(key):
        return sum(1 for s in seedwise.values() if s["criteria"][key])

    # frozen order: NULL, FAMILY, INSTRUMENT; agreement at >= 2 of 3 seeds
    measurement_outcome = None
    for name, key in (("OUTCOME_NULL_generic_order", "OUTCOME_NULL_fires"),
                      ("OUTCOME_FAMILY_small_m", "OUTCOME_FAMILY_fires"),
                      ("OUTCOME_INSTRUMENT_defect", "OUTCOME_INSTRUMENT_fires")):
        if votes(key) >= 2:
            measurement_outcome = name
            break
    if measurement_outcome is None:
        measurement_outcome = "NO_OUTCOME_FIRED"
        devs.append({"kind": "decision_rule_no_state_fired",
                     "classification": "invalid_measurement",
                     "detail": "no measurement outcome reached >= 2 of 3 seed "
                               "agreement; recorded rather than chosen"})

    multi = [n for n, k in (("OUTCOME_NULL_generic_order", "OUTCOME_NULL_fires"),
                            ("OUTCOME_FAMILY_small_m", "OUTCOME_FAMILY_fires"),
                            ("OUTCOME_INSTRUMENT_defect", "OUTCOME_INSTRUMENT_fires"))
             if votes(k) >= 2]
    if len(multi) > 1:
        devs.append({"kind": "multiple_measurement_outcomes_matched",
                     "matched": multi, "resolved_by": "frozen evaluation order",
                     "classification": "protocol_note"})

    verdict_decades = min(sum(1 for r in s["rows"] if r["verdict_yielding"])
                          for s in seedwise.values())
    seeds_agreeing = votes({"OUTCOME_NULL_generic_order": "OUTCOME_NULL_fires",
                            "OUTCOME_FAMILY_small_m": "OUTCOME_FAMILY_fires",
                            "OUTCOME_INSTRUMENT_defect": "OUTCOME_INSTRUMENT_fires"}
                           .get(measurement_outcome, "OUTCOME_NULL_fires")) \
        if measurement_outcome != "NO_OUTCOME_FIRED" else 0

    invalidations = []
    if ct["M3_planted_control"]["verdict"] != "PASS":
        invalidations.append("planted control did not report m = 2 on every frozen r")
    if ct["M6_m1_fixture"]["verdict"] != "PASS":
        invalidations.append("m = 1 nearby-object fixture failed")
    if verdict_decades < 5:
        invalidations.append(f"only {verdict_decades} of 7 decades yielded a "
                             "distributional verdict (< 5)")
    if s0v["quotations_failing_byte_verification"]:
        invalidations.append("a STAGE-0 quotation failed byte-substring verification")
    if bt["rows_failing_byte_verification"]:
        invalidations.append("a barrier-table quoted cell failed byte verification")

    terminal = "INVALID" if invalidations else {
        "KERNEL_FIELD": "S0-KERNEL-FIELD", "BASE_FIELD": "S0-INVERTED",
        "AMBIGUOUS": "S0-UNDETERMINED", "UNRETRIEVED_INFRA": "S0-INFRA",
    }[s0v["verdict"]]

    evidence_strength = ("replicated" if (seeds_agreeing == 3 and verdict_decades >= 6)
                         else "preliminary")

    out = {
        "experiment_id": EXP_ID, "stage": "decide",
        "inputs": {
            "stage0_run": stage_runs["stage0"], "stage0_verdict_sha256": s0h,
            "stage1_run": stage_runs["stage1"], "barrier_table_sha256": bth,
            "stage2_run": stage_runs["stage2"], "controls_sha256": cth,
            "stage3_runs": {str(k): {"run_id": v["run_id"], "sha256": v["sha256"]}
                            for k, v in decades.items()},
        },
        "stage0_verdict": s0v["verdict"],
        "stage0_branch_state": {
            "KERNEL_FIELD": "S0_KERNEL_FIELD", "BASE_FIELD": "S0_BASE_FIELD",
            "AMBIGUOUS": "S0_AMBIGUOUS", "UNRETRIEVED_INFRA": "S0_UNRETRIEVED_INFRA",
        }[s0v["verdict"]],
        "stage0_consequence": s0v["verdict_detail"]["consequence"],
        "per_seed_criteria": seedwise,
        "seed_votes": {k: votes(k) for k in ("OUTCOME_NULL_fires",
                                             "OUTCOME_FAMILY_fires",
                                             "OUTCOME_INSTRUMENT_fires")},
        "measurement_outcome": measurement_outcome,
        "audit_outcome": bt["audit_outcome"],
        "M4_exponent_changed_count": bt["M4_exponent_changed_count"],
        "M4_undetermined_count": bt["M4_undetermined_count"],
        "M3_planted_control_verdict": ct["M3_planted_control"]["verdict"],
        "M6_m1_fixture_verdict": ct["M6_m1_fixture"]["verdict"],
        "verdict_yielding_decades_min_over_seeds": verdict_decades,
        "invalidations_fired": invalidations,
        "M8_terminal_state": terminal,
        "evidence_strength_calibration": {
            "seeds_agreeing": seeds_agreeing,
            "verdict_yielding_decades": verdict_decades,
            "permitted_strength": evidence_strength,
            "claim_tier_cap": "toy",
            "note": "FIXED BEFORE EXECUTION; strength is computed here, not chosen",
        },
        "no_outcome_shopping": ("terminal states are computed by the frozen rule "
                               "INSIDE the run and written to the run record (SR7)"),
    }
    receipts = [write_artifact(run_dir, "decision-rule-evaluation.json", out)]
    return out, receipts, devs


# ---------------------------------------------------------------------------
# concrete cost table + tail checks (decide run)
# ---------------------------------------------------------------------------
BASELINE_ANCHORS = (
    {"record_id": "KN-TECH-006", "path": "knowledge/techniques/KN-TECH-006.md",
     "anchor": r"complexity:.*"},
    {"record_id": "KN-TECH-001", "path": "knowledge/techniques/KN-TECH-001.md",
     "anchor": r"complexity:.*"},
    {"record_id": "KN-TECH-018", "path": "knowledge/techniques/KN-TECH-018.md",
     "anchor": r"complexity:.*"},
    {"record_id": "KN-TECH-031", "path": "knowledge/techniques/KN-TECH-031.md",
     "anchor": r"complexity:.*"},
)


def _baseline_quotes() -> list:
    out = []
    for spec in BASELINE_ANCHORS:
        path = os.path.join(REPO, spec["path"])
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        m = re.search(spec["anchor"], text)
        if m is None:
            out.append({**spec, "error": "anchor not found", "byte_verified": False})
            continue
        q = _quote_at(path, m.start(), min(len(text), m.end()))
        out.append({"record_id": spec["record_id"], "artifact_path": spec["path"],
                    "basis": "quoted_from_record", "quote": q["quote"],
                    "byte_start": q["byte_start"], "byte_end": q["byte_end"],
                    "artifact_sha256": q["artifact_sha256"],
                    "byte_verified": q["byte_verified_exact_substring"]})
    return out


def cost_table(run_dir: str, decision: dict, stage_runs: dict) -> tuple[dict, list]:
    d24, _ = _load(stage_runs["stage3"]["24"], "distributions.json")
    ps0 = d24["per_seed"][str(ex.SEEDS[0])]
    measured_rows = [{
        "parameter_set": "PS-TOY-24", "basis": "measured",
        "log2_p": math.log2(d24["p"]),
        "median_log_m_over_log_d": ps0["M1_curve"].get("median"),
        "median_d_over_p": ps0["d_over_p"].get("median"),
        "achieved_n": ps0["achieved_n"], "seed": ex.SEEDS[0],
        "source_run": stage_runs["stage3"]["24"],
    }]
    m_est = None
    if ps0["M1_curve"].get("median") is not None and ps0["d_over_p"].get("median"):
        m_est = ps0["M1_curve"]["median"]

    def modeled_row(name, log2p, exponent_m, note, ell=None):
        if ell is not None:
            time_log2 = 0.5 * math.log2(ell)
            mem_log2 = 0.5 * math.log2(ell)
            dlog = math.log2(ell)
        else:
            dlog = log2p                     # d ~ p (optimistic assumption 3)
            time_log2 = 0.5 * dlog + exponent_m * dlog
            mem_log2 = 0.5 * dlog + exponent_m * dlog
        return {
            "parameter_set": name, "basis": "modeled", "bound_kind": "lower_bound",
            "log2_d_assumed": dlog,
            "m_exponent_used": exponent_m,
            "time_log2_fp_operations": time_log2,
            "memory_log2_fp_elements": mem_log2,
            "conditional_on": ["STAGE-0 verdict KERNEL_FIELD (NOT ESTABLISHED: "
                               f"actual verdict {decision['stage0_verdict']})",
                               "HEUR-ORD-1"],
            "note": note,
        }

    modeled_rows = [
        modeled_row("PS-TOY-24", math.log2(d24["p"]), m_est or 0.0,
                    "m exponent taken from the MEASURED median of log m / log d at "
                    "this set; the row itself is modeled and its measured input is "
                    "carried in the separate measured table, never mixed into this row"),
        modeled_row("PS-P256", 256.0, 1.0,
                    "MODELED ONLY under H1 (m ~ d ~ p). No measurement is possible: "
                    "computing m requires factoring d ~ 2^256"),
        modeled_row("PS-P384", 384.0, 1.0,
                    "MODELED ONLY under H1, as PS-P256"),
        modeled_row("PS-ELL-SMALL", None, 0.0,
                    "one class-group action step at ell = 13, m = O(1): the "
                    "accounting degenerates to Otilde(sqrt ell)", ell=13),
    ]
    table = {
        "experiment_id": EXP_ID,
        "title": "CORRECTED-COST BOUND TABLE (modeled)",
        "titling_rule": ("this table rests on a model and is therefore titled a "
                         "BOUND, never a prediction and never a measurement"),
        "measured_inputs": measured_rows,
        "modeled_cost_rows": modeled_rows,
        "no_row_mixes_bases": True,
        "optimistic_assumptions": [
            {"assumption": "the Otilde in Otilde(sqrt d) is treated as a polylog "
                           "cofactor when comparing to Otilde(d)",
             "direction_of_bias": "UNDERSTATES the square-root method's true cost; "
                                  "the bias favours the WORRY being tested, i.e. the "
                                  "conservative direction",
             "affects": ["all modeled_cost_rows"]},
            {"assumption": "one F_{p^m} operation costs Otilde(m) F_p operations",
             "direction_of_bias": "UNDERSTATES the corrected cost (schoolbook is "
                                  "m^2); every corrected figure is a LOWER BOUND",
             "affects": ["all modeled_cost_rows"]},
            {"assumption": "d ~ p for the minimal non-scalar endomorphism",
             "direction_of_bias": "NEUTRAL-TO-OPTIMISTIC; CHECKED, not assumed -- "
                                  "the measured d/p distribution is reported",
             "affects": ["PS-TOY-24", "PS-P256", "PS-P384"]},
            {"assumption": "the toy ladder's distribution of log m / log d is "
                           "informative about larger p",
             "direction_of_bias": "UNKNOWN AND UNCONTROLLED -- THIS EXPERIMENT "
                                  "REFUSES TO MAKE IT. PS-P256 and PS-P384 rows are "
                                  "MODELED under H1 and labelled conditional",
             "affects": ["PS-P256", "PS-P384"]},
        ],
        "hidden_overhead": [
            "the polylogarithmic resultant/remainder-tree cost inside Otilde(sqrt d), "
            "NOT measured here because this experiment evaluates no square-root Velu "
            "implementation",
            "computing m at all requires FACTORING d ~ p, which is subexponential; "
            "that cost is paid by this audit and never by an attacker, and it is "
            "what caps the ladder at 2^24",
            "the Otilde(sqrt d) MEMORY of the baby-step/giant-step table, in "
            "kernel-generator-field elements = Otilde(sqrt(d)*m) F_p-elements",
        ],
        "standing_baselines_quoted_from_record": _baseline_quotes(),
        "sota_delta": 0.0,
        "sota_delta_note": "ZERO: 0.886 sqrt(N) before and after. This experiment "
                           "mounts no attack and evaluates no isogeny.",
        "dominated_by": ["Pollard rho with distinguished points (KN-TECH-006) and "
                         "BSGS (KN-TECH-031) for the ECDLP; nothing here competes "
                         "with either"],
        "affected_vs_safe_scope": {
            "affected_constructions": [],
            "safe_and_why": [
                "NIST P-256/P-384 and all prime-field ECDLP parameters: the "
                "corrected model is an UPWARD cost correction on an endomorphism "
                "evaluation, and mechanism STEP 4 (H-ENDO-001) makes the "
                "endomorphism act on the prime-order subgroup as a scalar, so no "
                "attack is enabled or impeded",
                "CSIDH-style class-group actions: their action steps are "
                "small-prime, rational-kernel isogenies where m is O(1) and the "
                "correction factor is 1",
            ],
            "conditional_on": f"STAGE-0 verdict {decision['stage0_verdict']}; under "
                              "AMBIGUOUS or UNRETRIEVED_INFRA no cost statement is "
                              "made in either direction",
        },
    }
    return table, [write_artifact(run_dir, "concrete-cost-table.json", table)]


def tail_checks(run_dir: str, decision: dict, stage_runs: dict,
                s0v: dict, analytic_memory: dict) -> tuple[dict, list]:
    decades = {}
    for k, rid in stage_runs["stage3"].items():
        d, _ = _load(rid, "distributions.json")
        decades[int(k)] = d
    seed0 = str(ex.SEEDS[0])
    out = {
        "experiment_id": EXP_ID,
        "T1_small_order_outlier": {
            str(k): decades[k]["per_seed"][seed0]["smallest_5_log_m_over_log_d"]
            for k in sorted(decades)},
        "T2_decay_tail": {
            str(k): {"p": decades[k]["p"],
                     "log2_p": math.log2(decades[k]["p"]),
                     **{s: {kk: decades[k]["per_seed"][s]["M1_curve"].get(kk)
                            for kk in ("min", "q1", "median", "q3", "max", "n")}
                        for s in decades[k]["per_seed"]}}
            for k in sorted(decades)},
        "T3_degenerate_and_excluded": {
            str(k): {s: {"degenerate_fraction": v["M5_degenerate_fraction"],
                         "excluded_fraction": v["M5_excluded_curve_fraction"],
                         "excluded_count": v["excluded_count"],
                         "exclusion_reasons": v["exclusion_reasons"]}
                     for s, v in decades[k]["per_seed"].items()}
            for k in sorted(decades)},
        "T4_degree_window": {
            str(k): {s: decades[k]["per_seed"][s]["window_spread"]
                     for s in decades[k]["per_seed"]}
            for k in sorted(decades)},
        "T5_memory_reconciliation": analytic_memory,
        "T6_stage0_quotation_tail": {
            "total_passages": s0v["quotation_tail_count"],
            "operation_count_passages": len(s0v["operation_count_passages"]),
            "failing_byte_verification": len(s0v["quotations_failing_byte_verification"]),
            "labels": sorted({t["label"] for t in s0v["quotation_tail"]}),
            "note": "EVERY operation-count passage found in the pinned text is "
                    "reported in stage0-verdict.json, not only the deciding one",
        },
        "resolvability_floor": {
            "D_min": ex.D_MIN_RESOLVABLE,
            "rule": "effects below D = 0.10 are DECLARED UNRESOLVABLE BY THIS "
                    "DESIGN and are NOT reported as null results",
        },
    }
    return out, [write_artifact(run_dir, "tail-checks.json", out)]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True,
                    choices=["0", "1", "2", "3", "decide"])
    ap.add_argument("--k", type=int, help="ladder exponent for stage 3")
    ap.add_argument("--run-suffix", help="override the descriptive run suffix")
    ap.add_argument("--supersedes", help="RUN id this run supersedes (retained)")
    ap.add_argument("--stage0-run", default="RUN-ICINV-kf-stage0",
                    help="which STAGE-0 run's verdict later stages consume")
    args = ap.parse_args()

    command = "python3 -m harness.run_kerfield " + " ".join(sys.argv[1:])
    stage = args.stage
    suffix = args.run_suffix or {
        "0": "kf-stage0", "1": "kf-stage1-barrier", "2": "kf-stage2-controls",
        "decide": "kf-decide",
    }.get(stage, f"kf-stage3-k{args.k}")
    run_id = f"RUN-ICINV-{suffix}"
    run_dir = prepare_run_dir(run_id)

    tee_out, tee_err = Tee(sys.stdout), Tee(sys.stderr)
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = tee_out, tee_err
    started = time.time()
    status, valid, invalid_reason = "completed_valid", True, None
    metrics: dict = {}
    raw: dict = {}
    receipts: list = []
    devs: list = []
    parameters: dict = {"stage": stage}
    curve_id, seed = "n/a", None
    analytic = ex.analytic_peak_bytes(
        {"0": "stage0", "1": "stage1", "2": "stage2", "3": "stage3"}.get(stage,
                                                                         "decide"))
    try:
        if stage == "0":
            print(f"[{run_id}] STAGE 0 -- the blocking literature gate, run first "
                  f"and alone")
            out, r, d = stage0(run_dir, supersedes=args.supersedes)
            receipts += r
            devs += d
            metrics = {"M0_stage0_field_verdict": out["verdict"],
                       "claim_tier": out["verdict_detail"]["claim_tier"],
                       "quotation_tail_count": out["quotation_tail_count"],
                       "operation_count_passages":
                           len(out["operation_count_passages"]),
                       "quotations_failing_byte_verification":
                           len(out["quotations_failing_byte_verification"])}
            raw = {"sources": out["sources"]}
            parameters |= {"primary_urls": list(s0.PRIMARY_URLS),
                           "fallback_paths": list(s0.FALLBACK_PATHS),
                           "supersedes_run": args.supersedes}
            print(f"[{run_id}] VERDICT: {out['verdict']} -- {out['verdict_detail']['reason']}")
            if out["verdict"] == "UNRETRIEVED_INFRA":
                status = "failed_infrastructure"
        elif stage == "1":
            s0v, _ = _load(args.stage0_run, "stage0-verdict.json")
            print(f"[{run_id}] STAGE 1 barrier table, under STAGE-0 verdict "
                  f"{s0v['verdict']} from {args.stage0_run}")
            parameters |= {"stage0_run": args.stage0_run}
            out, r, d = stage1(run_dir, s0v["verdict"])
            receipts += r
            devs += d
            metrics = {"row_count": out["row_count"],
                       "M4_exponent_changed_count": out["M4_exponent_changed_count"],
                       "M4_undetermined_count": out["M4_undetermined_count"],
                       "audit_outcome": out["audit_outcome"],
                       "rows_failing_byte_verification":
                           out["rows_failing_byte_verification"]}
            raw = {"scope": out["scope"], "required_rows": out["required_rows"]}
            print(f"[{run_id}] rows={out['row_count']} changed="
                  f"{out['M4_exponent_changed_count']} undetermined="
                  f"{out['M4_undetermined_count']} -> {out['audit_outcome']}")
        elif stage == "2":
            print(f"[{run_id}] STAGE 2 controls -- BEFORE any measurement is read")
            out, r, d = stage2(run_dir)
            receipts += r
            devs += d
            metrics = {"M3_planted_control": out["M3_planted_control"]["verdict"],
                       "M6_m1_fixture": out["M6_m1_fixture"]["verdict"],
                       **out["verification_summary"]}
            raw = {"prime_ladder": out["prime_ladder"]}
            parameters |= {"planted_r": list(ex.PLANTED_R),
                           "fixture_ells": list(ex.FIXTURE_ELLS)}
            seed = ex.SEEDS[0]
            valid = (out["M3_planted_control"]["verdict"] == "PASS"
                     and out["M6_m1_fixture"]["verdict"] == "PASS")
            if not valid:
                status, invalid_reason = "completed_invalid", "blocking control failed"
            print(f"[{run_id}] planted={metrics['M3_planted_control']} "
                  f"fixture={metrics['M6_m1_fixture']}")
        elif stage == "3":
            if args.k not in ex.LADDER_EXPONENTS:
                raise SystemExit(f"--k must be one of {ex.LADDER_EXPONENTS}")
            controls, ch = _load("RUN-ICINV-kf-stage2-controls", "controls.json")
            if controls["M3_planted_control"]["verdict"] != "PASS":
                raise SystemExit("SR3: planted control did not pass; stage 3 "
                                 "refuses to start")
            ref = {"run_id": "RUN-ICINV-kf-stage2-controls",
                   "controls_sha256": ch,
                   "planted": controls["M3_planted_control"]["verdict"],
                   "fixture": controls["M6_m1_fixture"]["verdict"]}
            print(f"[{run_id}] STAGE 3 decade k={args.k}; controls on disk "
                  f"({ch[:12]}...) planted={ref['planted']} fixture={ref['fixture']}")
            out, r, d = stage3(run_dir, args.k, ref)
            receipts += r
            devs += d
            dist = out["distributions"]
            metrics = {"k": args.k, "p": dist["p"],
                       "per_seed": {s: {"achieved_n": v["achieved_n"],
                                        "median_log_m_over_log_d":
                                            v["M1_curve"].get("median"),
                                        "null_median": v["null"].get("median"),
                                        "ks_D": v["M2_ks"]["D"],
                                        "ks_critical": v["M2_ks"]["critical_value"],
                                        "ks_below_critical": v["M2_ks"]["below_critical"],
                                        "M5_degenerate_fraction":
                                            v["M5_degenerate_fraction"],
                                        "M5_excluded_curve_fraction":
                                            v["M5_excluded_curve_fraction"]}
                                    for s, v in dist["per_seed"].items()}}
            raw = {"null_first_ordering": dist["null_first_ordering"]}
            parameters |= {"k": args.k, "p": dist["p"], "seeds": list(ex.SEEDS),
                           "target_n": ex.CURVES_PER_DECADE_TARGET,
                           "floor_n": ex.CURVES_PER_DECADE_FLOOR}
            curve_id = f"LADDER-K{args.k}-P{dist['p']}"
            analytic = ex.analytic_peak_bytes("stage3", p=dist["p"])
        else:
            stage_runs = {"stage0": args.stage0_run,
                          "stage1": "RUN-ICINV-kf-stage1-barrier",
                          "stage2": "RUN-ICINV-kf-stage2-controls",
                          "stage3": {str(k): f"RUN-ICINV-kf-stage3-k{k}"
                                     for k in ex.LADDER_EXPONENTS}}
            print(f"[{run_id}] frozen decision rule over "
                  f"{len(stage_runs['stage3'])} decade runs")
            out, r, d = decide(run_dir, stage_runs)
            receipts += r
            devs += d
            s0v, _ = _load(stage_runs["stage0"], "stage0-verdict.json")
            ct, cr = cost_table(run_dir, out, stage_runs)
            receipts += cr
            tc, tr = tail_checks(run_dir, out, stage_runs, s0v, analytic)
            receipts += tr
            metrics = {"M0_stage0_field_verdict": out["stage0_verdict"],
                       "measurement_outcome": out["measurement_outcome"],
                       "audit_outcome": out["audit_outcome"],
                       "M8_terminal_state": out["M8_terminal_state"],
                       "M3_planted_control": out["M3_planted_control_verdict"],
                       "M6_m1_fixture": out["M6_m1_fixture_verdict"],
                       "verdict_yielding_decades":
                           out["verdict_yielding_decades_min_over_seeds"],
                       "seed_votes": out["seed_votes"],
                       "permitted_evidence_strength":
                           out["evidence_strength_calibration"]["permitted_strength"]}
            raw = {"invalidations_fired": out["invalidations_fired"]}
            if out["invalidations_fired"]:
                status, valid = "completed_invalid", False
                invalid_reason = "; ".join(out["invalidations_fired"])
            print(f"[{run_id}] terminal={out['M8_terminal_state']} "
                  f"measurement={out['measurement_outcome']} "
                  f"audit={out['audit_outcome']}")
    except Exception as exc:                                   # noqa: BLE001
        status, valid = "failed_infrastructure", False
        invalid_reason = f"{type(exc).__name__}: {exc}"
        import traceback
        traceback.print_exc()
        devs.append({"kind": "run_exception", "error": invalid_reason,
                     "classification": "infrastructure_error"})
    finally:
        finished = time.time()
        sys.stdout, sys.stderr = old_out, old_err
        finalise_run(run_dir, run_id, stage=stage, status=status, command=command,
                     started=started, finished=finished, parameters=parameters,
                     metrics=metrics, raw=raw, stdout=tee_out.buf.getvalue(),
                     stderr=tee_err.buf.getvalue(), valid=valid,
                     invalid_reason=invalid_reason, curve_id=curve_id, seed=seed,
                     deviations=devs, artifact_receipts=receipts,
                     analytic_memory=analytic)
    print(f"wrote {os.path.relpath(run_dir, REPO)} status={status}")
    return 0 if status.startswith("completed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
