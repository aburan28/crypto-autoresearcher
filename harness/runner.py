"""Run wrapper: execute a bounded experiment and emit an immutable run record.

Produces exactly the reproduction package required by
docs/evidence-and-reproducibility.md:

    experiments/<EXP>/runs/<RUN>/
        manifest.yaml   command.txt   environment.json
        stdout.log      stderr.log    raw-result.json

Every solve/relation claim is re-verified here with code independent of the
solver (the certificate discipline, docs/claims-and-verification.md); a failed
certificate makes the run invalid_measurement rather than a result. Run
directories are never overwritten -- the wrapper refuses to clobber an existing
RUN id.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

import sympy
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()


def git_state() -> tuple[str, bool]:
    commit = _git("rev-parse", "HEAD") or "unknown"
    # "dirty" means tracked source differs from HEAD (what affects
    # reproducibility). Untracked files -- notably the run outputs being
    # written -- are intentionally ignored.
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no"))
    return commit, dirty


def environment() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "dependencies": {"sympy": sympy.__version__, "pyyaml": yaml.__version__},
    }


def curve_id(p: int, a: int, b: int, field_bits: int) -> str:
    h = hashlib.sha256(f"{p}:{a}:{b}".encode()).hexdigest()[:8]
    return f"TOY-P{field_bits}-{h}"


@dataclass
class RunResult:
    """What an experiment returns for a single planned run."""
    run_suffix: str                       # -> RUN-<EXP-area>-<suffix>
    curve_id: str
    seed: int
    parameters: dict
    metrics: dict
    certificate: dict                     # {"kind": ..., "statement": {...}} or {"kind":"none"}
    valid: bool = True
    invalid_reason: str | None = None
    stdout: str = ""
    stderr: str = ""
    raw: dict = field(default_factory=dict)
    # Optional exemplar-aligned metadata (see harness/README.md). Recorded
    # verbatim in the manifest when provided; the keys are omitted entirely
    # otherwise, so existing runs and manifests are unaffected.
    heuristic_validation: dict | None = None
    cost_model: dict | None = None


# Certificate verifiers, keyed by kind. Each is INDEPENDENT of any solver.
def _verify(cert: dict) -> tuple[bool, str]:
    from .semaev import verify_decomposition_certificate
    from .toycurve import EllipticCurve

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


def write_run(exp_id: str, exp_area: str, result: RunResult, *,
              status: str, command: str, started: float, finished: float,
              out_root: str | None = None) -> str:
    run_id = f"RUN-{exp_area}-{result.run_suffix}"
    root = out_root or os.path.join(REPO, "experiments", exp_id)
    run_dir = os.path.join(root, "runs", run_id)
    if os.path.exists(run_dir):
        raise FileExistsError(
            f"run {run_id} already exists at {run_dir}; run records are "
            f"immutable -- supersede with a new RUN id, do not overwrite")
    os.makedirs(run_dir)

    commit, dirty = git_state()
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is KB on Linux, bytes on macOS.
    peak_rss = ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)

    cert = dict(result.certificate)
    verified, verifier = _verify(cert)
    cert["verified"] = verified
    cert["verifier"] = verifier
    cert["verifier_commit"] = commit

    final_status = status
    valid = result.valid
    invalid_reason = result.invalid_reason
    if cert.get("kind") in ("discrete_log", "decomposition") and not verified:
        final_status = "completed_invalid"
        valid = False
        invalid_reason = "certificate failed independent verification"

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": exp_id,
            "status": final_status,
            "code": {"commit": commit, "dirty": dirty, "command": command},
            "inference": {
                "requested_policy": "executor-terra",
                "resolved_model_id": "none (deterministic harness execution)",
                "reasoning_effort": None,
                "fallback_used": False,
                "adapter_version": None,
            },
            "environment": environment(),
            "inputs": {
                "curve_id": result.curve_id,
                "seed": result.seed,
                "parameters": result.parameters,
            },
            "timing": {
                "started_at": _iso(started),
                "finished_at": _iso(finished),
                "wall_seconds": round(finished - started, 6),
            },
            "resources": {"peak_rss_bytes": peak_rss,
                          "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 6)},
            "result": {
                "metrics": result.metrics,
                "valid": valid,
                "invalid_reason": invalid_reason,
                "certificate": {"kind": cert.get("kind"),
                                "verified": cert.get("verified"),
                                "verifier": cert.get("verifier")},
            },
            "artifacts": {
                "command": "command.txt",
                "environment": "environment.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "raw_result": "raw-result.json",
            },
        }
    }

    # Optional exemplar-aligned blocks: recorded verbatim, present only when
    # the experiment supplied them (keys absent means "not this run class").
    if result.heuristic_validation is not None:
        manifest["run"]["heuristic_validation"] = dict(result.heuristic_validation)
    if result.cost_model is not None:
        manifest["run"]["cost_model"] = dict(result.cost_model)

    _write(run_dir, "manifest.yaml",
           yaml.safe_dump(manifest, sort_keys=False))
    _write(run_dir, "command.txt", command + "\n")
    _write(run_dir, "environment.json",
           json.dumps(environment(), indent=2, sort_keys=True))
    _write(run_dir, "stdout.log", result.stdout)
    _write(run_dir, "stderr.log", result.stderr)
    _write(run_dir, "raw-result.json",
           json.dumps({"metrics": result.metrics, "certificate": cert,
                       "raw": result.raw}, indent=2, sort_keys=True, default=str))
    return run_id


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _write(run_dir: str, name: str, content: str) -> None:
    with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
        f.write(content)
