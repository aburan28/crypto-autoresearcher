"""Executor driver for the STAGE-0 RE-EXECUTION of EXP-ICINV-fcb497.

TASK-20260808-7865e0, protocol version 2
(experiments/EXP-ICINV-fcb497/amendments/v2.yaml), approved by
DEC-20260808-e75211.  Writes exactly ONE new run package,
experiments/EXP-ICINV-fcb497/runs/RUN-ICINV-kf-stage0-v3/.

WHY A NEW DRIVER RATHER THAN AN EDIT.  `harness/run_kerfield.py` and
`harness/velu_stage0.py` are the code that COMMITTED runs
(RUN-ICINV-kf-stage0, RUN-ICINV-kf-stage0-v2 and the eleven stage-1..4 runs)
are pinned to by sha256.  Editing either would leave those receipts pointing at
code that no longer exists.  This module therefore reuses them by IMPORT --
`runner.git_state`, `runner.environment`, `runner.source_provenance`,
`runner.untracked_source_vs_output`, `exp_kerfield.analytic_peak_bytes`, and the
whole of `velu_stage0`'s extraction / classification / verification / branch
logic through `velu_stage0_v3` -- and changes ONLY what amendment v2 changes:
the retrieval list (A1) and the per-quotation version recording (A2).

STAGES 1-4 ARE NOT RUN BY THIS MODULE.  They are committed, independently
validated, and untouched by this amendment.

Usage:
    python3 -m harness.run_kerfield_stage0_v3
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import re
import resource
import signal
import sys
import time
from datetime import datetime, timezone

import yaml

from . import exp_kerfield as ex
from . import runner
from . import velu_stage0 as s0_committed
from . import velu_stage0_v3 as s0

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_ID = ex.EXP_ID
RUNS_ROOT = os.path.join(REPO, "experiments", EXP_ID, "runs")

RUN_ID = "RUN-ICINV-kf-stage0-v3"
HANDOFF_ID = "TASK-20260808-7865e0"          # the ACTIVE handoff, not v1's
DECISION_ID = "DEC-20260808-e75211"
AMENDMENT = "experiments/EXP-ICINV-fcb497/amendments/v2.yaml"
PROTOCOL_VERSION = 2
SUPERSEDES = ("RUN-ICINV-kf-stage0", "RUN-ICINV-kf-stage0-v2")
BATCH_ID = None                              # assigned by the Coordinator snapshot

# handoff budget (TASK-20260808-7865e0), which is TIGHTER than the contract's
# per-run cap of 7200 s and therefore the one enforced here.
WALL_CLOCK_CAP_SECONDS = 3600
MEMORY_CAP_BYTES = 4 * 1024 ** 3
MAXIMUM_RUNS = 1                             # ONE run directory (handoff budget)


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


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


def inference_block() -> dict:
    try:
        from orchestration.adapter.config import ADAPTER_VERSION
    except Exception:                                          # pragma: no cover
        ADAPTER_VERSION = None
    return {
        "requested_policy": "executor-implementation",   # from TASK-20260808-7865e0
        "canonical_policy": "executor-implementation",
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
            "TASK-20260808-7865e0 requires a session that did not write "
            "CORR-20260808-ba8792 or amendments/v2.yaml. This Executor session "
            "wrote neither; under this harness independence means independent "
            "context and a fresh reading, not a different model."),
        "adapter_version": ADAPTER_VERSION,
        "config_digest": None,
        "policy_env_present": bool(os.environ.get("AUTORESEARCH_POLICY")),
        "note": ("the retrieval, hashing, extraction and byte verification are "
                 "performed by deterministic harness code; no model is in the "
                 "verification loop"),
        "handoff_id": HANDOFF_ID,
    }


def prepare_run_dir(run_id: str) -> str:
    run_dir = os.path.join(RUNS_ROOT, run_id)
    if os.path.exists(run_dir):
        raise FileExistsError(
            f"run {run_id} already exists at {run_dir}; run records are immutable "
            f"-- supersede with a NEW run id, never overwrite (amendment v2 A4)")
    os.makedirs(run_dir, exist_ok=False)
    return run_dir


def write_artifact(run_dir: str, name: str, obj) -> dict:
    path = os.path.join(run_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return {"artifact": name, "sha256": _sha256_file(path),
            "written_at": _iso(time.time()), "bytes": os.path.getsize(path)}


# ---------------------------------------------------------------------------
# STAGE 0, protocol version 2
# ---------------------------------------------------------------------------
def stage0_v3(run_dir: str) -> tuple[dict, list, list]:
    receipts, deviations = [], []
    src_dir = os.path.join(run_dir, "sources")
    os.makedirs(src_dir, exist_ok=True)

    attribution = s0.attribution_from_contract()
    term_guard = s0.check_terms_against_contract()      # frozen list, unchanged
    url_guard = s0.check_urls_against_amendment()       # A1, read back at run time

    plan = [("primary", u) for u in s0.PRIMARY_URLS]
    for path in s0.FALLBACK_PATHS:                      # UNCHANGED by A1
        role = "fallback_corpus_note" if not path.startswith("http") else "fallback_paper"
        plan.append((role, path))

    artifacts = []
    for role, loc in plan:
        label = re.sub(r"[^A-Za-z0-9]+", "-", loc).strip("-")[-60:]
        raw_dest = os.path.join(src_dir, f"{label}.raw")
        if loc.startswith("http"):
            fetch = s0.curl_fetch(loc, raw_dest)
        else:
            fetch = s0.copy_local(loc, raw_dest)
        entry = {"role": role, "label": label, "location": loc, "fetch": fetch,
                 "text": None, "full_text": None, "passages": [],
                 "attribution_check": None, "version": None}
        if fetch["ok"]:
            text = s0.extract_text(raw_dest, os.path.join(src_dir, f"{label}.txt"))
            entry["text"] = text
            entry["full_text"] = s0.is_full_text(fetch, text)
            if text["ok"]:
                tp = os.path.join(REPO, text["text_path"])
                entry["version"] = s0.extract_version_strings(tp)      # A2
                found = s0.find_passages(tp)                           # FROZEN
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
            entry["full_text"] = {"is_full_text": False, "reason": "not retrieved"}
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

    # THE FROZEN BRANCH RULES, applied by the COMMITTED implementation.
    verdict = s0.decide(artifacts)

    # Full quotation tail: EVERY passage found, not only the deciding one
    # (tail_checks "STAGE-0 QUOTATION TAIL"), now carrying A2's per-quotation
    # url_used / artifact_sha256 / version_string.
    tail = []
    for a in artifacts:
        ver = a.get("version") or {}
        for p in a["passages"]:
            tail.append({
                "source": a["label"], "role": a["role"],
                "url_used": a["location"],
                "final_url": (a["fetch"] or {}).get("final_url"),
                "artifact_sha256": (a["fetch"] or {}).get("sha256"),
                "text_sha256": (a["text"] or {}).get("sha256"),
                "version_string": ver.get("version_string"),
                "version_string_reason": ver.get("version_string_reason"),
                "version_string_byte_start": ver.get("version_string_byte_start"),
                "version_string_byte_end": ver.get("version_string_byte_end"),
                "version_string_verified_exact_substring":
                    ver.get("version_string_verified_exact_substring"),
                "term_matches": p["terms"],
                "label": p["classification"]["label"],
                "label_with_document_context":
                    p["classification"].get("label_with_document_context"),
                "kernel_rationality_in_document":
                    p["classification"].get("kernel_rationality_in_document"),
                "field_tokens": p["classification"]["field_tokens"],
                "kernel_rationality_markers":
                    p["classification"]["kernel_rationality_markers"],
                "byte_start": p["context_byte_start"],
                "byte_end": p["context_byte_end"],
                "context_chars": p["context_chars"],
                "verified_exact_substring": p["verification"]["verified"],
                "context": p["context"],
            })
    unverified = [t for t in tail if not t["verified_exact_substring"]]

    arxiv = next((a for a in artifacts
                  if a["location"] == "https://arxiv.org/pdf/2003.10118"), None)
    pred = s0.prediction_check(
        (arxiv or {}).get("fetch", {}).get("sha256"),
        (arxiv or {}).get("fetch", {}).get("byte_length_on_disk"))

    out = {
        "experiment_id": EXP_ID, "stage": "0",
        "run_id": RUN_ID,
        "protocol_version": PROTOCOL_VERSION,
        "amendment": AMENDMENT,
        "handoff_id": HANDOFF_ID,
        "approved_by_decision": DECISION_ID,
        "supersedes_runs": list(SUPERSEDES),
        "supersession_note": (
            "DECLARED FROM THIS RUN'S OWN SIDE (amendment v2 change A4). This run "
            "supersedes RUN-ICINV-kf-stage0 and RUN-ICINV-kf-stage0-v2, BOTH OF "
            "WHICH ARE RETAINED BYTE-UNCHANGED, are not re-scored, and remain "
            "readable as what they are: version-1 STAGE-0 executions that returned "
            "AMBIGUOUS on a retrieval list pinned entirely to eprint.iacr.org, "
            "whose PDFs answered HTTP 403. Their verdicts stand exactly as "
            "recorded. What changes here is the RETRIEVAL LIST (A1) and the "
            "per-quotation version recording (A2); the byte-verification path, "
            "the frozen search terms, the 400-character window, the classifier and "
            "all four branch rules are the committed velu_stage0 objects, imported "
            "unmodified."),
        "verdict": verdict["verdict"], "verdict_detail": verdict,
        "frozen_branch_rules_applied": {
            "evaluation_order": list(s0.VERDICTS),
            "determinate_verdict_requires_full_text": True,
            "corpus_note_can_only_return_AMBIGUOUS": True,
            "authoritative_version_rule": (
                "amendment v2 A1: where the versions differ, the ANTS XIV / MSP "
                "version is authoritative. A determinate verdict resting SOLELY on "
                "the arXiv preprint says so on its face and records the preprint's "
                "version string. Disagreement between byte-verified passages of the "
                "pinned sources fires the EXISTING S0_AMBIGUOUS clause; no new "
                "clause was added and none is applied."),
            "background_knowledge_prohibition": (
                "the verdict cites ONLY pinned artifacts. No remembered sentence "
                "from any paper, and no quotation, offset or hash from the archived "
                "Red Team report, appears in this record or in the code that made "
                "it (amendment v2 A5, CORR-20260807-a24675, AGENTS.md rule 9)."),
            "decide_is_the_committed_implementation":
                s0.decide is s0_committed.decide,
            "classify_is_the_committed_implementation":
                s0.classify_passage is s0_committed.classify_passage,
            "find_passages_is_the_committed_implementation":
                s0.find_passages is s0_committed.find_passages,
            "verify_quote_is_the_committed_implementation":
                s0.verify_quote is s0_committed.verify_quote,
            "search_terms_identical_to_committed":
                tuple(s0.SEARCH_TERMS) == tuple(s0_committed.SEARCH_TERMS),
            "context_chars_identical_to_committed":
                s0.CONTEXT_CHARS == s0_committed.CONTEXT_CHARS,
        },
        "sources": [{k: v for k, v in a.items() if k != "passages"} for a in artifacts],
        "attribution": attribution,
        "search_term_guard": term_guard,
        "retrieval_list_guard": url_guard,
        "arxiv_prediction_check": pred,
        "quotation_tail": tail,
        "quotation_tail_count": len(tail),
        "quotations_failing_byte_verification": unverified,
        "operation_count_passages": [t for t in tail
                                     if t["label"] in ("kernel_field", "base_field",
                                                       "field_unspecified")],
    }
    receipts.append(write_artifact(run_dir, "stage0-verdict.json", out))
    receipts.append(write_artifact(run_dir, "quotation-tail.json", {
        "run_id": RUN_ID, "experiment_id": EXP_ID,
        "protocol_version": PROTOCOL_VERSION, "amendment": AMENDMENT,
        "quotation_tail_count": len(tail),
        "quotations_failing_byte_verification": unverified,
        "per_quotation_fields_required_by_A2":
            ["url_used", "artifact_sha256", "version_string", "byte_start",
             "byte_end", "verified_exact_substring"],
        "quotations": tail,
    }))
    receipts.append(write_artifact(run_dir, "sources-manifest.json", {
        "run_id": RUN_ID,
        "files": sorted(
            ({"path": os.path.relpath(os.path.join(src_dir, fn), REPO),
              "sha256": _sha256_file(os.path.join(src_dir, fn)),
              "bytes": os.path.getsize(os.path.join(src_dir, fn))}
             for fn in os.listdir(src_dir)),
            key=lambda z: z["path"]),
        "retrieval_receipts": [
            {"url": a["location"], "role": a["role"],
             "http_status": a["fetch"].get("http_status"),
             "final_url": a["fetch"].get("final_url"),
             "content_type": a["fetch"].get("content_type"),
             "byte_length": a["fetch"].get("byte_length_on_disk"),
             "sha256": a["fetch"].get("sha256"),
             "retrieved_at": a["fetch"].get("retrieved_at"),
             "raw_path": a["fetch"].get("stored_path"),
             "text_path": (a["text"] or {}).get("text_path"),
             "text_sha256": (a["text"] or {}).get("sha256"),
             "extraction_method": (a["text"] or {}).get("method"),
             "is_full_text": (a["full_text"] or {}).get("is_full_text"),
             "version_string": (a.get("version") or {}).get("version_string"),
             "version_string_reason": (a.get("version") or {}).get("version_string_reason")}
            for a in artifacts],
    }))
    return out, receipts, deviations


# ---------------------------------------------------------------------------
# run packaging
# ---------------------------------------------------------------------------
def finalise_run(run_dir: str, *, status: str, command: str, started: float,
                 finished: float, parameters: dict, metrics: dict, raw: dict,
                 stdout: str, stderr: str, valid: bool, invalid_reason,
                 deviations: list, artifact_receipts: list,
                 analytic_memory: dict) -> str:
    commit, dirty = runner.git_state()
    provenance = runner.source_provenance()
    if not provenance["all_pinned"]:
        raise RuntimeError(
            f"refusing to finalise {RUN_ID}: code.source.all_pinned is false "
            f"(unreadable: {provenance['unreadable']}). An unpinned run is "
            f"INVALID under this contract (CORR-20260807-911ef7).")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)

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
            f"[{lo}, {hi}].")

    manifest = {"run": {
        "id": RUN_ID,
        "experiment_id": EXP_ID,
        "hypothesis_id": ex.HYPOTHESIS_ID,
        "goal_id": ex.GOAL_ID,
        "handoff_id": HANDOFF_ID,
        "approved_by_decision": DECISION_ID,
        "protocol_version": PROTOCOL_VERSION,
        "amendment": AMENDMENT,
        "supersedes_runs": list(SUPERSEDES),
        "batch_id": BATCH_ID,
        "stage": "0",
        "status": status,
        "code": {"commit": commit, "dirty": dirty, "command": command,
                 "source": provenance,
                 "untracked": runner.untracked_source_vs_output()},
        "inference": inference_block(),
        "environment": runner.environment(),
        "inputs": {"curve_id": "n/a", "seed": None, "parameters": parameters},
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
                   "certificate": {
                       "kind": "none",
                       "verified": True,
                       "verifier": "no-claim",
                       "note": ("PURE MEASUREMENT / LITERATURE RETRIEVAL RUN: this "
                                "run claims no discrete-log solve and no "
                                "factor-base relation, so certificate.kind is "
                                "explicitly none "
                                "(docs/claims-and-verification.md)"),
                       "verifier_commit": commit}},
        "protocol_deviations": deviations,
        "artifacts": {"command": "command.txt", "environment": "environment.json",
                      "stdout": "stdout.log", "stderr": "stderr.log",
                      "raw_result": "raw-result.json",
                      "sources_dir": "sources/",
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
        json.dump({"metrics": metrics,
                   "certificate": {"kind": "none", "verified": True,
                                   "verifier": "no-claim"},
                   "raw": raw}, fh, indent=1, sort_keys=True, default=str)
    return run_dir


def _budget_alarm(signum, frame):                              # pragma: no cover
    raise TimeoutError(
        f"handoff wall-clock budget of {WALL_CLOCK_CAP_SECONDS}s exceeded; "
        f"this is SR6 failed_infrastructure, never a verdict")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()

    command = "python3 -m harness.run_kerfield_stage0_v3 " + " ".join(sys.argv[1:])
    command = command.strip()
    run_dir = prepare_run_dir(RUN_ID)

    tee_out, tee_err = Tee(sys.stdout), Tee(sys.stderr)
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = tee_out, tee_err
    signal.signal(signal.SIGALRM, _budget_alarm)
    signal.alarm(WALL_CLOCK_CAP_SECONDS)
    started = time.time()
    status, valid, invalid_reason = "completed_valid", True, None
    metrics: dict = {}
    raw: dict = {}
    receipts: list = []
    devs: list = []
    analytic = ex.analytic_peak_bytes("stage0")
    parameters = {
        "stage": "0",
        "protocol_version": PROTOCOL_VERSION,
        "amendment": AMENDMENT,
        "primary_urls": list(s0.PRIMARY_URLS),
        "fallback_paths": list(s0.FALLBACK_PATHS),
        "supersedes_runs": list(SUPERSEDES),
        "curl_max_time_seconds": s0_committed.CURL_MAX_TIME,
    }
    try:
        print(f"[{RUN_ID}] STAGE 0 re-execution under protocol version "
              f"{PROTOCOL_VERSION} ({AMENDMENT})")
        print(f"[{RUN_ID}] retrieval order: {', '.join(s0.PRIMARY_URLS)}")
        out, r, d = stage0_v3(run_dir)
        receipts += r
        devs += d
        metrics = {
            "M0_stage0_field_verdict": out["verdict"],
            "claim_tier": out["verdict_detail"]["claim_tier"],
            "quotation_tail_count": out["quotation_tail_count"],
            "operation_count_passages": len(out["operation_count_passages"]),
            "quotations_failing_byte_verification":
                len(out["quotations_failing_byte_verification"]),
            "sources_retrieved_ok": sum(1 for a in out["sources"]
                                        if a["fetch"]["ok"]),
            "full_texts_retrieved": sum(1 for a in out["sources"]
                                        if (a["full_text"] or {}).get("is_full_text")),
        }
        raw = {"sources": out["sources"],
               "retrieval_list_guard": out["retrieval_list_guard"],
               "search_term_guard": out["search_term_guard"],
               "arxiv_prediction_check": out["arxiv_prediction_check"],
               "frozen_branch_rules_applied": out["frozen_branch_rules_applied"]}
        print(f"[{RUN_ID}] VERDICT: {out['verdict']} -- "
              f"{out['verdict_detail']['reason']}")
        for a in out["sources"]:
            print(f"[{RUN_ID}]   {a['role']:22s} {a['location']}  "
                  f"HTTP={a['fetch'].get('http_status')}  "
                  f"bytes={a['fetch'].get('byte_length_on_disk')}  "
                  f"sha256={a['fetch'].get('sha256')}  "
                  f"full_text={(a['full_text'] or {}).get('is_full_text')}  "
                  f"version={(a.get('version') or {}).get('version_string')!r}")
        if out["verdict"] == "UNRETRIEVED_INFRA":
            status = "failed_infrastructure"
        if out["quotations_failing_byte_verification"]:
            status, valid = "invalid", False
            invalid_reason = ("a STAGE-0 quotation failed exact byte-substring "
                              "re-verification at its recorded offsets "
                              "(invalidation_rules)")
    except TimeoutError as exc:                                # pragma: no cover
        status, valid = "failed_infrastructure", False
        invalid_reason = str(exc)
        devs.append({"kind": "resource_exhaustion", "where": "run",
                     "observed": str(exc), "classification": "resource_exhaustion",
                     "consequence": "SR6: never negative mathematical evidence"})
    except Exception as exc:                                   # pragma: no cover
        status, valid = "failed_infrastructure", False
        invalid_reason = f"{type(exc).__name__}: {exc}"
        devs.append({"kind": "exception", "where": "run", "observed": str(exc),
                     "classification": "infrastructure_error",
                     "consequence": "partial artifacts retained (SR6)"})
        raise
    finally:
        signal.alarm(0)
        finished = time.time()
        sys.stdout, sys.stderr = old_out, old_err
        finalise_run(run_dir, status=status, command=command, started=started,
                     finished=finished, parameters=parameters, metrics=metrics,
                     raw=raw, stdout=tee_out.buf.getvalue(),
                     stderr=tee_err.buf.getvalue(), valid=valid,
                     invalid_reason=invalid_reason, deviations=devs,
                     artifact_receipts=receipts, analytic_memory=analytic)
        print(f"[{RUN_ID}] wrote {os.path.relpath(run_dir, REPO)} status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
