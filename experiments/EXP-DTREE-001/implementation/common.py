"""Shared run-writing infrastructure for EXP-DTREE-001.

Deliberately confined to experiments/EXP-DTREE-001/implementation/ (per the
frozen specification's test_boundary.implementation note: "New glue confined
to experiments/EXP-DTREE-001/") rather than editing harness/*.py. This module
follows the same conventions as harness/runner.py (git state, per-file content
provenance, independent certificate re-verification) but:

  * writes the exact artifact filenames the frozen specification.yaml
    requires under required_artifacts (manifest.yaml, command.txt,
    environment.json, raw.json, summary.json, stdout.txt, stderr.txt) --
    NOT harness/runner.py's raw-result.json / stdout.log / stderr.log;
  * supports a *list* of certificates per run (a cost-measurement run may
    claim many per-target decomposition/discrete-log relations, not one);
  * captures stdout/stderr internally via a Tee so a run is fully
    self-contained from a single `python3 driver.py <subcommand>` invocation.

Every run this module writes is immutable: it refuses to overwrite an
existing run directory (matching harness/runner.py's discipline).
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import platform
import resource
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import sympy
import yaml


def _find_repo_root(start: str | None = None) -> str:
    d = os.path.abspath(start or __file__)
    d = os.path.dirname(d)
    while True:
        if os.path.exists(os.path.join(d, "AGENTS.md")) and os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("could not locate repo root (AGENTS.md + .git) "
                                f"above {start or __file__}")
        d = parent


REPO = _find_repo_root()
EXP_ID = "EXP-DTREE-001"
EXP_AREA = "DTREE"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)
RUNS_DIR = os.path.join(EXP_DIR, "runs")
IMPL_DIR = os.path.join(EXP_DIR, "implementation")

sys.path.insert(0, REPO)

from harness.toycurve import EllipticCurve, _seed_int  # noqa: E402
from harness.semaev import verify_decomposition_certificate  # noqa: E402


def seed_int(seed: int, tag: str) -> int:
    """Deterministic derived randomness -- identical convention to
    harness.toycurve._seed_int, re-exported so every experiment-local module
    uses exactly one seeding scheme."""
    return _seed_int(seed, tag)


# --------------------------------------------------------------------------
# Git / provenance (mirrors harness/runner.py; see its docstring for the
# GOAL-ENDO-001 N6 rationale for content-hash pinning over commit+dirty alone)
# --------------------------------------------------------------------------

def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                           text=True).stdout.strip()


def git_state() -> tuple[str, bool]:
    commit = _git("rev-parse", "HEAD") or "unknown"
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no"))
    return commit, dirty


def _sha256_file(path: str) -> str | None:
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def _sha256_at_head(rel: str) -> str | None:
    blob = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO,
                           capture_output=True)
    if blob.returncode != 0:
        return None
    return hashlib.sha256(blob.stdout).hexdigest()


def executed_source_files() -> list[str]:
    seen: set[str] = set()
    candidates = [getattr(m, "__file__", None) for m in list(sys.modules.values())]
    candidates.append(sys.argv[0] if sys.argv else None)
    for f in candidates:
        if not f:
            continue
        p = os.path.realpath(f)
        if not p.endswith(".py") or not p.startswith(REPO + os.sep):
            continue
        seen.add(os.path.relpath(p, REPO))
    return sorted(seen)


def source_provenance() -> dict:
    files: dict[str, dict] = {}
    for rel in executed_source_files():
        digest = _sha256_file(os.path.join(REPO, rel))
        if digest is None:
            files[rel] = {"sha256": None, "status": "unreadable"}
            continue
        head = _sha256_at_head(rel)
        if head is None:
            status = "untracked"
        elif head == digest:
            status = "clean"
        else:
            status = "modified"
        files[rel] = {"sha256": digest, "status": status}
    statuses = [v["status"] for v in files.values()]
    return {
        "files": files,
        "file_count": len(files),
        "all_pinned": bool(files) and "unreadable" not in statuses,
        "all_clean": bool(files) and set(statuses) <= {"clean"},
        "modified": sorted(k for k, v in files.items() if v["status"] == "modified"),
        "untracked": sorted(k for k, v in files.items() if v["status"] == "untracked"),
        "unreadable": sorted(k for k, v in files.items() if v["status"] == "unreadable"),
    }


def environment() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "dependencies": {
            "sympy": sympy.__version__,
            "pyyaml": yaml.__version__,
        },
    }


def _inference_block() -> dict:
    """Identical rationale to harness/runner.py's _inference_block: this is
    deterministic Python, never a model call, so there is no resolved model
    to record -- and that is stated explicitly rather than left blank."""
    try:
        from orchestration.adapter.manifest import block_from_env
        return block_from_env()
    except Exception as exc:  # pragma: no cover - import guard
        return {
            "requested_policy": "executor-implementation",
            "resolved_model_id": None,
            "reasoning_effort": None,
            "fallback_used": False,
            "adapter_version": None,
            "note": "deterministic harness execution -- no model in the loop",
            "adapter_error": f"{type(exc).__name__}: {exc}",
        }


def curve_id(p: int, a: int, b: int, field_bits: int) -> str:
    h = hashlib.sha256(f"{p}:{a}:{b}".encode()).hexdigest()[:8]
    return f"TOY-P{field_bits}-{h}"


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


# --------------------------------------------------------------------------
# Certificate verification -- independent of any solver, per
# docs/claims-and-verification.md. Generalizes harness/runner.py's single-
# certificate _verify to a *list* of certificates (a cost-measurement run
# claims many decomposition/discrete-log relations, one per target).
# --------------------------------------------------------------------------

def verify_certificate(cert: dict) -> tuple[bool, str]:
    kind = cert.get("kind", "none")
    if kind == "none":
        return True, "no-claim"
    if kind == "decomposition":
        return verify_decomposition_certificate(cert), "independent-recompute"
    if kind == "discrete_log":
        st = cert["statement"]
        c = st["curve"]
        E = EllipticCurve(c["p"], c["a"], c["b"])
        P, Q, k = tuple(st["P"]), tuple(st["Q"]), int(st["k"])
        return E.mul(k, P) == Q, "independent-recompute"
    return False, f"unknown-kind:{kind}"


def verify_all(certificates: list[dict]) -> dict:
    """Independently re-verify every claimed certificate in this run.

    Returns a summary block plus mutates each certificate dict in place with
    its own verified/verifier fields (so the per-item detail survives into
    raw.json while the manifest gets an honest roll-up).
    """
    commit, _ = git_state()
    claimed = 0
    verified_count = 0
    kinds = set()
    for cert in certificates:
        kind = cert.get("kind", "none")
        kinds.add(kind)
        if kind == "none":
            cert["verified"] = True
            cert["verifier"] = "no-claim"
            cert["verifier_commit"] = commit
            continue
        claimed += 1
        ok, verifier = verify_certificate(cert)
        cert["verified"] = ok
        cert["verifier"] = verifier
        cert["verifier_commit"] = commit
        if ok:
            verified_count += 1
    all_verified = (verified_count == claimed)
    if not kinds or kinds == {"none"}:
        summary_kind = "none"
    else:
        # a run mixes at most one non-"none" kind in this experiment
        summary_kind = sorted(kinds - {"none"})[0] if kinds - {"none"} else "none"
    return {
        "kind": summary_kind,
        "count_claimed": claimed,
        "count_verified": verified_count,
        "all_verified": all_verified,
        "verifier": "independent-recompute" if claimed else "no-claim",
        "verifier_commit": commit,
    }


# --------------------------------------------------------------------------
# Tee: mirror stdout/stderr to the real streams AND an in-memory buffer, so
# a run is fully self-contained and also visible when run in the foreground.
# --------------------------------------------------------------------------

class _Tee(io.TextIOBase):
    def __init__(self, *streams):
        self._streams = streams

    def write(self, s):
        for st in self._streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self._streams:
            st.flush()


@contextlib.contextmanager
def captured_output():
    out_buf, err_buf = io.StringIO(), io.StringIO()
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout = _Tee(real_out, out_buf)
    sys.stderr = _Tee(real_err, err_buf)
    try:
        yield out_buf, err_buf
    finally:
        sys.stdout, sys.stderr = real_out, real_err


# --------------------------------------------------------------------------
# The run record itself
# --------------------------------------------------------------------------

VALID_STATUSES = {
    "completed_valid", "completed_invalid", "failed_infrastructure",
    "failed_implementation", "resource_exhaustion", "cancelled_by_budget",
}


@dataclass
class RunRecord:
    run_id: str                      # RUN-DTREE-NNN
    purpose: str
    command: str                     # exact reproducing command
    seeds: dict                      # every source of randomness used
    inputs: dict                     # curve_id(s), parameters
    started: float
    finished: float
    metrics: dict
    raw: dict                        # full raw per-item data
    summary: dict                    # aggregated/derived statistics
    certificates: list = field(default_factory=list)
    status: str = "completed_valid"
    valid: bool = True
    invalid_reason: str | None = None
    heuristic_validation: dict | None = None
    cost_model: dict | None = None
    protocol_deviations: list = field(default_factory=list)
    anomalies: list = field(default_factory=list)


def write_run(record: RunRecord, stdout_text: str, stderr_text: str,
              out_root: str | None = None) -> str:
    """out_root overrides RUNS_DIR -- used ONLY by pre-execution smoke tests
    (written to the scratchpad, never to experiments/EXP-DTREE-001/runs/) so
    integration bugs are caught without consuming a real, immutable run id."""
    run_dir = os.path.join(out_root or RUNS_DIR, record.run_id)
    if os.path.exists(run_dir):
        raise FileExistsError(
            f"run {record.run_id} already exists at {run_dir}; run records "
            f"are immutable -- supersede with a new RUN id, never overwrite")

    commit, dirty = git_state()
    provenance = source_provenance()
    if not provenance["all_pinned"]:
        raise RuntimeError(
            f"refusing to write {record.run_id}: executed source is not "
            f"pinnable (unreadable: {provenance['unreadable'] or 'none'})")

    cert_summary = verify_all(record.certificates)

    final_status = record.status
    valid = record.valid
    invalid_reason = record.invalid_reason
    if cert_summary["count_claimed"] and not cert_summary["all_verified"]:
        final_status = "completed_invalid"
        valid = False
        invalid_reason = (
            f"{cert_summary['count_claimed'] - cert_summary['count_verified']} "
            f"of {cert_summary['count_claimed']} claimed certificates failed "
            f"independent verification")

    os.makedirs(run_dir)
    ru = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)

    manifest = {
        "run": {
            "id": record.run_id,
            "experiment_id": EXP_ID,
            "purpose": record.purpose,
            "status": final_status,
            "code": {
                "commit": commit,
                "dirty": dirty,
                "command": record.command,
                "source": provenance,
            },
            "inference": _inference_block(),
            "environment": environment(),
            "inputs": record.inputs,
            "seeds": record.seeds,
            "timing": {
                "started_at": _iso(record.started),
                "finished_at": _iso(record.finished),
                "wall_seconds": round(record.finished - record.started, 6),
            },
            "resources": {
                "peak_rss_bytes": peak_rss,
                "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 6),
            },
            "result": {
                "metrics": record.metrics,
                "valid": valid,
                "invalid_reason": invalid_reason,
                "certificate": cert_summary,
            },
            "protocol_deviations": record.protocol_deviations,
            "anomalies": record.anomalies,
            "artifacts": {
                "command": "command.txt",
                "environment": "environment.json",
                "raw": "raw.json",
                "summary": "summary.json",
                "stdout": "stdout.txt",
                "stderr": "stderr.txt",
            },
        }
    }
    if record.heuristic_validation is not None:
        manifest["run"]["heuristic_validation"] = record.heuristic_validation
    if record.cost_model is not None:
        manifest["run"]["cost_model"] = record.cost_model

    def _w(name, content):
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    _w("manifest.yaml", yaml.safe_dump(manifest, sort_keys=False))
    _w("command.txt", record.command + "\n")
    _w("environment.json", json.dumps(environment(), indent=2, sort_keys=True))
    _w("raw.json", json.dumps({
        "run_id": record.run_id, "raw": record.raw,
        "certificates": record.certificates,
    }, indent=2, sort_keys=True, default=str))
    _w("summary.json", json.dumps({
        "run_id": record.run_id, "metrics": record.metrics,
        "summary": record.summary,
    }, indent=2, sort_keys=True, default=str))
    _w("stdout.txt", stdout_text)
    _w("stderr.txt", stderr_text)

    return run_dir
