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
import sys
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


def _sha256_file(path: str) -> str | None:
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def _sha256_at_head(rel: str) -> str | None:
    """sha256 of a path's content AT HEAD, or None if absent there."""
    blob = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO,
                          capture_output=True)
    if blob.returncode != 0:
        return None
    return hashlib.sha256(blob.stdout).hexdigest()


def executed_source_files() -> list[str]:
    """Repo-relative .py files this process actually imported.

    Derived from `sys.modules` rather than from a declared list, so it records
    what RAN instead of what someone remembered to declare. The entry script is
    included even when it is executed as `__main__`.
    """
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
    """Pin every source file this run executed, by content hash.

    GOAL-ENDO-001 next action N6 (open since DEC-20260807-c8aa8b, promoted to
    blocking by CORR-20260807-0f5d56): `code.commit` plus a `dirty` flag does
    NOT identify the code that ran. Seventeen of EXP-ICINV-4d33aa's nineteen
    measurement runs recorded `dirty: true` with no per-file binding, which is
    why one EXP-INSTR-85b102 root cause is permanently unrecoverable -- the
    pre-repair source no longer exists anywhere.

    Content hashes fix this without forcing a commit-before-run workflow: an
    untracked file that is committed later still matches the hash recorded
    here, and a file that is edited later provably does not. `status` says how
    each file stood relative to HEAD at run time:

        clean          -- tracked, and identical to HEAD
        modified       -- tracked, but differs from HEAD
        untracked      -- not in HEAD at all (a new module, the usual case for
                          a harness written in the same session that ran it)
        unreadable     -- could not be hashed; the run is NOT pinned

    `all_pinned` is the field a reviewer should read: it is True when every
    executed source file was hashed, whatever its git status. `all_clean` is
    the stricter claim that the recorded commit alone reproduces the run.
    """
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
        "note": (
            "Every executed source file is pinned by sha256 (N6). `commit` "
            "alone does not identify this run's code when `dirty` is true; "
            "these hashes do, and they stay valid after the files are "
            "committed."),
    }


def untracked_source_vs_output() -> dict:
    """Split untracked paths into SOURCE and OUTPUT.

    The original N6 defect: `git_state()` ignores untracked files wholesale
    because run outputs are untracked while being written -- which also hides
    an untracked .py that the run imported. Outputs live under
    `experiments/*/runs/`; source does not.
    """
    raw = _git("ls-files", "--others", "--exclude-standard")
    untracked = [p for p in raw.splitlines() if p]
    source, output = [], []
    for p in untracked:
        parts = p.split("/")
        is_output = (len(parts) >= 3 and parts[0] == "experiments"
                     and parts[2] == "runs")
        (output if is_output else source).append(p)
    code_source = [p for p in source if p.endswith(".py")]
    return {
        "untracked_source_code": sorted(code_source),
        "untracked_other_count": len(source) - len(code_source),
        "untracked_output_count": len(output),
    }


def environment() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "dependencies": {"sympy": sympy.__version__, "pyyaml": yaml.__version__},
    }


def _inference_block() -> dict:
    """Record which inference backend, if any, was in this run's loop.

    Harness runs are deterministic code, so the usual answer is "no model" --
    which is exactly what makes their numbers backend-independent. When a run
    IS driven by an agent, `AUTORESEARCH_POLICY` (and optionally
    `AUTORESEARCH_BACKEND`) are set at launch and the adapter resolves the
    exact model that answered. A missing or broken adapter is recorded, never
    silently replaced with a plausible-looking block.
    """
    try:
        from orchestration.adapter.manifest import block_from_env
        return block_from_env()
    except Exception as exc:                      # pragma: no cover - import guard
        return {
            "requested_policy": "executor-implementation",
            "resolved_model_id": None,
            "reasoning_effort": None,
            "fallback_used": False,
            "adapter_version": None,
            "note": "deterministic harness execution — no model in the loop",
            "adapter_error": f"{type(exc).__name__}: {exc}",
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


def _cairn_cross_check(cert: dict, verified: bool) -> dict | None:
    """Stage 0 (docs/cairn-integration-plan.md): re-score a certificate through
    cairn's sandboxed verifier, a second independent implementation in a
    different repository, language, process, and OS jail.

    Opt-in and never a new hard dependency -- returns a `not_attempted` block
    rather than running at all when `tools/cairn_bridge.CAIRN_MCP_BIN` is
    unset, so a machine with no cairn build behaves exactly as before this
    existed. Returns None only when the certificate kind is not one Stage 0
    covers (`cairn_bridge.SUPPORTED_KINDS`) -- nothing to cross-check, so
    nothing is recorded, same as `_verify` returning "no-claim" for
    `kind: none`.

    Raises RuntimeError on a genuine disagreement: cairn's checker and this
    module's own independent recomputation reaching opposite conclusions
    about the same witness means one of the two implementations has a bug,
    and that is worth refusing the run over rather than silently recording
    -- the plan's invariant (a), and the same severity class as the
    unpinnable-source refusal just above this function's caller. cairn
    answering `unavailable` is never treated as a disagreement (invariant
    b): it is cairn saying it could not check, not that it checked and
    disagreed, and is recorded as data exactly like any other verdict.
    """
    # `tools/` is deliberately NOT among pyproject.toml's installed packages
    # (it is repo-root-relative tooling, not redistributable library code --
    # see that file's own comment on why `harness` and `tools` differ here),
    # so `import tools` is not guaranteed to resolve from ambient sys.path:
    # this module is routinely invoked as `python3 harness/<script>.py`,
    # which puts `harness/` on sys.path[0], not REPO. Insert REPO explicitly
    # rather than assume, the same defensive step cairn_bridge.py takes for
    # its own sibling imports.
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from tools import cairn_bridge

    if cert.get("kind") not in cairn_bridge.SUPPORTED_KINDS:
        return None
    if not cairn_bridge.available():
        return {"status": "not_attempted", "reason": f"{cairn_bridge.ENV_BIN} not set"}
    try:
        verdict = cairn_bridge.score_certificate(cert)
    except cairn_bridge.CairnUnavailableError as exc:
        # A bridge-level failure (binary present but unreachable, timeout,
        # unparseable response) is the same "says nothing about the
        # artifact" case as cairn's own `unavailable` verdict -- recorded,
        # never treated as agreement OR disagreement.
        return {"status": "not_attempted", "reason": str(exc)}

    block = {
        "status": verdict.status,
        "detail": verdict.detail,
        "objective_id": verdict.objective_id,
        "checker_sha256": verdict.checker_sha256,
    }
    if verdict.status == "accept" and not verified:
        raise RuntimeError(
            f"cairn disagreement: this module's independent recomputation rejected the "
            f"certificate but cairn's sandboxed checker accepted it "
            f"({verdict.objective_id}, checker {verdict.checker_sha256}): {verdict.detail}. "
            f"Two independent implementations disagreeing about a witness means one of "
            f"them has a bug; refusing to write a run that cannot say which.")
    if verdict.status == "reject" and verified:
        raise RuntimeError(
            f"cairn disagreement: this module's independent recomputation accepted the "
            f"certificate but cairn's sandboxed checker rejected it "
            f"({verdict.objective_id}, checker {verdict.checker_sha256}): {verdict.detail}. "
            f"Two independent implementations disagreeing about a witness means one of "
            f"them has a bug; refusing to write a run that cannot say which.")
    return block


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
    commit, dirty = git_state()
    provenance = source_provenance()
    # N6, promoted to BLOCKING by CORR-20260807-0f5d56. A run whose executed
    # source cannot be pinned by content hash is unreproducible in a way no
    # later commit can repair -- exactly the failure that made one
    # EXP-INSTR-85b102 root cause permanently unrecoverable. Refuse it. Note
    # this fires on UNREADABLE source only: an untracked or modified file is
    # pinned by its hash and is fine, which is what keeps the ordinary
    # write-a-module-then-run-it workflow working.
    #
    # CHECKED BEFORE makedirs, DELIBERATELY. Refusing after creating the
    # directory would leave an empty RUN id behind in a tree whose whole
    # discipline is that run ids are immutable and never reused -- and the
    # wrapper's own FileExistsError would then block the retry. A test pins
    # this ordering.
    if not provenance["all_pinned"]:
        raise RuntimeError(
            f"refusing to write {run_id}: executed source is not pinnable "
            f"(unreadable: {provenance['unreadable'] or 'none imported'}). "
            f"A manifest that cannot bind its own code to a hash is not a "
            f"reproduction package (GOAL-ENDO-001 N6).")

    # Also BEFORE makedirs, same reasoning: a cairn disagreement is a wrapper-
    # level integrity alarm, not a research outcome, and refusing after
    # creating the run directory would leave the same empty-RUN-id hazard the
    # comment above this one exists to avoid. An ordinary failed certificate
    # (both checkers agree it does not verify) is NOT refused here -- that is
    # `completed_invalid` below, a legitimate recorded result.
    cert = dict(result.certificate)
    verified, verifier = _verify(cert)
    cert["verified"] = verified
    cert["verifier"] = verifier
    cert["verifier_commit"] = commit
    cairn_cross_check = _cairn_cross_check(cert, verified)
    if cairn_cross_check is not None:
        cert["cairn_cross_check"] = cairn_cross_check

    os.makedirs(run_dir)
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is KB on Linux, bytes on macOS.
    peak_rss = ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)

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
            "code": {"commit": commit, "dirty": dirty, "command": command,
                     "source": provenance,
                     "untracked": untracked_source_vs_output()},
            "inference": _inference_block(),
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
                                "verifier": cert.get("verifier"),
                                **({"cairn_cross_check": cairn_cross_check}
                                   if cairn_cross_check is not None else {})},
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


def _inference_block() -> dict:
    """The `inference` block every harness-written run manifest carries.

    A run produced by this module is deterministic Python, not a model call,
    so there is no resolved model to record. Saying that explicitly is the
    point: AGENTS.md requires the block on every run manifest, and an absent
    block reads as "nobody recorded it" rather than "no inference happened".
    """
    return {
        "requested_policy": "executor-terra",
        "resolved_model_id": "none (deterministic harness execution)",
        "reasoning_effort": None,
        "fallback_used": False,
        "adapter_version": None,
    }


def _write(run_dir: str, name: str, content: str) -> None:
    with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
        f.write(content)
