"""Run driver for EXP-ICEX-aaccfc protocol version 4 (specification.yaml +
AMD-20260926-ced670 + AMD-20260929-143d11 + AMD-20260929-5a84eb; one run, all
6 fixtures, 30 cells, one worker). NOT EXECUTED by the implementation tasks.

A charged run refuses to start unless, in this order:
  * the host is macOS (C-7 is stated for the repository Mac; OQ-9);
  * the C-7 machine-protection readings pass, fail-closed (15-min load <= 14,
    system volume >= 5 GiB free, repository volume >= 20 GiB free); the
    readings are recorded in the manifest;
  * --run-id is RUN-...;
  * --admission-decision names ledger/decisions/<DEC>.yaml (v4 FX-1): a
    coordinator_decision whose id matches, whose `decision` is an admission
    (ADMIT_DECISIONS), whose target_ids include EXP-ICEX-aaccfc, whose
    execution_admission.currently_admitted is exactly true, which is not
    superseded or withdrawn (a status of superseded/withdrawn, a non-null
    superseded_by -- null is accepted --, or any other decision listing it
    under `supersedes`), and whose file is tracked by git and clean at HEAD;
  * the trial plan's protocol hashes match the files on disk;
  * the protocol v4 records (three amendments, the v3 and v4 approving
    decisions, fixtures) match their pinned sha256, and the v3 and v4
    amendment hashes equal their decisions' amendment_sha256_at_decision;
  * --snapshot-receipt PATH (v4 FX-6) pins every implementation .py, test and
    trial-plan file, every pinned implementation file matches, and the
    implementation tree is clean (the receipt file itself is excluded);
  * runs/<RUN-ID>/ does not exist (run records are immutable).
Then C-1 fixture reproduction (Sage, byte-compare; mismatch = procedure
defect), each cell in a fresh `nice -n 10` process, the independent audit,
the C-5 analysis (metrics.json) and only then the non-verdict FX-A figure
(fxa_nonverdict.json).

Run record (v4 FX-2/FX-3): manifest.yaml has a top-level `run:` block
(id, experiment_id, status, code, environment, inputs, timing, resources,
result, inference, ...) mirroring RUN-SDEG-3de103/manifest_v2.yaml, written
with status running before the first cell and after every cell; a
ProcedureDefect records `invalid`, any other exception or SIGTERM/SIGHUP/SIGINT
records `failed_infrastructure`; raw-result.json (index of cells attempted so
far) is always written.

Usage:
  python3 driver.py --check-admission-only
  python3 driver.py --run-id RUN-... --admission-decision DEC-... --snapshot-receipt PATH
  python3 driver.py --smoke-dry-run --run-id DRYRUN-...smoke... --runs-dir implementation/smoke/<dir>
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import signal  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402
import hostinfo  # noqa: E402

ADMISSION_TARGET = common.EXPERIMENT_ID
ADMIT_DECISIONS = ("admit_execution", "approve_execution", "admit", "approve")
DEAD_STATUSES = ("superseded", "withdrawn")
ADMISSION_ENV, REPO_ENV, RUN_DIR_ENV = ("ICEX_AACCFC_ADMISSION_DECISION", "ICEX_AACCFC_REPO_ROOT",
                                        "ICEX_AACCFC_RUN_DIR")  # read by cellrun.admission_guard
ADMISSION_PINNING = ("any DEC id is accepted: the admission decision did not exist when protocol v4 was frozen, "
                     "so it cannot be pinned by id; it must instead pass every check_decision rule")

EXIT_REFUSED_ADMISSION = 3
EXIT_REFUSED_DECISION = 4
EXIT_REFUSED_PLAN = 5
EXIT_REFUSED_EXISTS = 6
EXIT_PROCEDURE_DEFECT = 7
EXIT_INFRASTRUCTURE = 8
EXIT_REFUSED_HOST = 9
EXIT_REFUSED_SNAPSHOT = 10

# v4 FX-2: governing records -> (repo-relative path, pinned sha256 or None, approving-decision key or None)
_R = common.REPO_ROOT
GOVERNING = {
    "specification": (str(common.SPECIFICATION.relative_to(_R)), None, None),
    "amendment_v2": (str(common.AMENDMENT.relative_to(_R)), common.AMENDMENT_SHA256, None),
    "amendment_v3": (str(common.AMENDMENT_V3.relative_to(_R)), common.AMENDMENT_V3_SHA256, "decision_v3"),
    "amendment_v4": (str(common.AMENDMENT_V4.relative_to(_R)), common.AMENDMENT_V4_SHA256, "decision_v4"),
    "decision_v3": (str(common.DECISION_V3.relative_to(_R)), None, None),
    "decision_v4": (str(common.DECISION_V4.relative_to(_R)), None, None),
    "b0_definition": (str(common.B0_AMENDMENT.relative_to(_R)), None, None),
    "fixtures": (str(common.FIXTURE_JSON.relative_to(_R)), common.FROZEN_JSON_SHA256, None),
    "fixture_generator": (str(common.FIXTURE_GEN.relative_to(_R)), common.FROZEN_GEN_SHA256, None),
}


class RunInterrupted(Exception):
    pass


class RunProcedureDefect(Exception):
    pass


# ------------------------------------------------------------------ admission
def admission_readings(repo_root: Path) -> dict:
    """C-7 readings; any failure to read is recorded and fails closed."""
    try:
        return hostinfo.admission_readings(repo_root)
    except Exception as e:  # noqa: BLE001
        return {"host_kind": hostinfo.host_kind(), "error": repr(e),
                "read_at": dt.datetime.now(dt.timezone.utc).isoformat()}


def check_c7(r: dict) -> tuple[bool, list]:
    if r.get("error"):
        return False, [f"readings unavailable (fail closed): {r['error']}"]
    if r.get("host_kind") != "macos":
        return False, [f"host {r.get('host_kind')} is not the repository Mac (C-7 scope)"]
    for k in ("load_15min", "system_volume_free_gib", "repo_volume_free_gib"):
        if not isinstance(r.get(k), (int, float)):
            return False, [f"reading {k} missing (fail closed)"]
    return hostinfo.check_admission(r)


def _git_rc(repo_root: Path, *a) -> int | None:
    try:
        return subprocess.run(["git", "-C", str(repo_root), *a], capture_output=True, text=True).returncode
    except OSError:
        return None


def _git(repo_root: Path, *a):
    try:
        r = subprocess.run(["git", "-C", str(repo_root), *a], capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _dead(m: dict) -> str | None:
    st = m.get("status")
    if isinstance(st, str) and st.strip().lower() in DEAD_STATUSES:
        return f"status is {st!r}"
    if m.get("superseded_by") not in (None, "", []):
        return f"superseded_by is {m.get('superseded_by')!r}"
    return None


def _superseding_decisions(repo_root: Path, dec_id: str, own: Path) -> list:
    """Every other decision file (committed or not; fail-closed) whose
    `supersedes` (top level or coordinator_decision) names dec_id."""
    import yaml
    hits = []
    for p in sorted((Path(repo_root) / "ledger" / "decisions").glob("DEC-*.yaml")):
        if p.resolve() == own.resolve():
            continue
        try:
            txt = p.read_text()
        except OSError:
            continue
        if dec_id not in txt:
            continue
        try:
            doc = yaml.safe_load(txt)
        except yaml.YAMLError:
            continue
        if not isinstance(doc, dict):
            continue
        for m in (doc, doc.get("coordinator_decision")):
            sup = m.get("supersedes") if isinstance(m, dict) else None
            sup = [sup] if isinstance(sup, str) else (sup if isinstance(sup, list) else [])
            if dec_id in sup:
                hits.append(p.name)
                break
    return hits


def check_decision(repo_root: Path, dec_id: str | None) -> tuple[bool, str]:
    """v4 FX-1 (see module docstring). Returns (ok, path or reason)."""
    import yaml
    if not dec_id or not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", dec_id):
        return False, f"invalid decision id {dec_id!r}"
    repo_root = Path(repo_root)
    rel = f"ledger/decisions/{dec_id}.yaml"
    path = repo_root / rel
    if not path.exists():
        return False, f"{path} does not exist"
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return False, f"{path} does not parse: {e}"
    dec = doc.get("coordinator_decision") if isinstance(doc, dict) else None
    if not isinstance(dec, dict):
        return False, f"{path} has no coordinator_decision mapping"
    if dec.get("id") != dec_id:
        return False, f"{path} id {dec.get('id')!r} != {dec_id}"
    for where, m in (("document", doc), ("coordinator_decision", dec)):
        why = _dead(m)
        if why:
            return False, f"{path} {where} {why}"
    d = dec.get("decision")
    if not isinstance(d, str) or d.strip() not in ADMIT_DECISIONS:
        return False, f"{path} decision {d!r} is not an admission decision {ADMIT_DECISIONS}"
    if ADMISSION_TARGET not in (dec.get("target_ids") or []):
        return False, f"{path} target_ids do not include {ADMISSION_TARGET}"
    adm = dec.get("execution_admission")
    if not isinstance(adm, dict) or adm.get("currently_admitted") is not True:
        got = adm.get("currently_admitted") if isinstance(adm, dict) else adm
        return False, f"{path} execution_admission.currently_admitted is {got!r}, not true"
    why = _dead(adm)
    if why:
        return False, f"{path} execution_admission {why}"
    later = _superseding_decisions(repo_root, dec_id, path)
    if later:
        return False, f"{path} is superseded by {later}"
    if _git_rc(repo_root, "ls-files", "--error-unmatch", "--", rel) != 0:
        return False, f"{path} is not tracked by git (uncommitted decision)"
    if _git_rc(repo_root, "diff", "--quiet", "HEAD", "--", rel) != 0:
        return False, f"{path} differs from HEAD (dirty or staged decision)"
    return True, str(path)


def check_plan(plan: dict) -> tuple[bool, list]:
    import make_trial_plan
    want = make_trial_plan.build_plan()["protocol"]
    got = plan.get("protocol") or {}
    bad = [k for k, v in want.items() if k.endswith("_sha256") and got.get(k) != v]
    if plan.get("protocol_version") != common.PROTOCOL_VERSION:
        bad.append(f"plan protocol_version {plan.get('protocol_version')} != {common.PROTOCOL_VERSION}")
    if plan.get("namespace") != common.FROZEN_NS:
        bad.append(f"plan namespace {plan.get('namespace')!r} != {common.FROZEN_NS}")
    if plan.get("n_cells") != 30 or len(plan.get("cells", [])) != 30:
        bad.append("plan does not cover 6 fixtures x 5 cells")
    return not bad, bad


def protocol_binding(repo_root: Path) -> dict:
    """v4 FX-2: path and sha256 of every governing record (None if absent)."""
    out = {"protocol_version": common.PROTOCOL_VERSION,
           "composition": "specification.yaml + AMD-20260926-ced670 + AMD-20260929-143d11 + AMD-20260929-5a84eb",
           "records": {}}
    for name, (rel, _, _) in GOVERNING.items():
        p = Path(repo_root) / rel
        out["records"][name] = {"path": rel, "sha256": common.sha256_file(p) if p.exists() else None}
    return out


def check_protocol_binding(repo_root: Path, binding: dict) -> tuple[bool, list]:
    import yaml
    bad = []
    recs = binding["records"]
    if binding.get("protocol_version") != 4:
        bad.append(f"protocol_version {binding.get('protocol_version')} != 4")
    for name, (rel, pinned, dec_key) in GOVERNING.items():
        got = recs[name]["sha256"]
        if got is None:
            bad.append(f"{rel} missing")
            continue
        if pinned and got != pinned:
            bad.append(f"{rel} sha256 {got} != pinned {pinned}")
        if dec_key:
            dp = Path(repo_root) / GOVERNING[dec_key][0]
            try:
                d = (yaml.safe_load(dp.read_text()) or {}).get("coordinator_decision") or {}
            except (OSError, yaml.YAMLError, AttributeError) as e:
                bad.append(f"{dp}: {e}")
                continue
            if d.get("amendment_sha256_at_decision") != got:
                bad.append(f"{rel} sha256 != {dp.name} amendment_sha256_at_decision")
    return not bad, bad


# ------------------------------------------------------------------ snapshot (v4 FX-6)
def implementation_files(impl_dir: Path = HERE) -> list:
    """Files a snapshot receipt must pin: every .py (tests included) and the trial plan."""
    impl_dir = Path(impl_dir)
    return (sorted(impl_dir.glob("*.py")) + sorted((impl_dir / "tests").glob("*.py"))
            + sorted(impl_dir.glob("trial-plan*.json")))


def verify_snapshot(repo_root: Path, receipt_path, impl_rel: str = common.IMPL_REL) -> tuple[bool, dict]:
    """Every receipt entry under the implementation directory matches the
    working tree, every implementation file is pinned, and the implementation
    tree is clean. The receipt file itself is excluded from every comparison."""
    repo_root = Path(repo_root).resolve()
    info = {"receipt": str(receipt_path) if receipt_path else None, "mismatches": [], "missing": [],
            "unpinned": [], "dirty": None, "checked": 0}
    if not receipt_path:
        info["error"] = "no --snapshot-receipt given (required for a scientific run)"
        return False, info
    rp = Path(receipt_path).resolve()
    try:
        rec = json.loads(rp.read_text())
        pins = rec["path_sha256"]
        if not isinstance(pins, dict) or not pins:
            raise ValueError("path_sha256 empty or not a mapping")
    except (OSError, ValueError, KeyError, TypeError) as e:
        info["error"] = f"receipt unreadable: {e}"
        return False, info
    info["receipt_sha256"] = common.sha256_file(rp)
    info["receipt_task_id"] = rec.get("task_id")
    try:
        own = str(rp.relative_to(repo_root))
    except ValueError:
        own = None
    info["receipt_excluded"] = own
    prefix = impl_rel.rstrip("/") + "/"
    for rel, want in sorted(pins.items()):
        if rel == own or not rel.startswith(prefix):
            continue
        p = repo_root / rel
        info["checked"] += 1
        if not p.is_file():
            info["missing"].append(rel)
        elif common.sha256_file(p) != want:
            info["mismatches"].append(rel)
    for p in implementation_files(repo_root / impl_rel):
        rel = str(p.resolve().relative_to(repo_root))
        if rel != own and rel not in pins:
            info["unpinned"].append(rel)
    st = _git(repo_root, "status", "--porcelain", "--untracked-files=all", "--", impl_rel)
    if st is None:
        info["error"] = "git status unavailable (fails closed)"
        return False, info
    dirty = [ln for ln in st.splitlines() if own is None or not ln.endswith(own)]
    info["dirty"] = bool(dirty)
    info["dirty_paths"] = dirty[:200]
    ok = not (info["mismatches"] or info["missing"] or info["unpinned"] or info["dirty"])
    info["verified"] = ok
    return ok, info


# ------------------------------------------------------------------ provenance
def git_state(repo_root: Path) -> dict:
    st = _git(repo_root, "status", "--porcelain")
    impl = _git(repo_root, "status", "--porcelain", "--untracked-files=all", "--", common.IMPL_REL)
    return {"commit": _git(repo_root, "rev-parse", "HEAD"),
            "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": None if st is None else bool(st), "status_porcelain": (st or "").splitlines()[:200],
            "implementation_dirty": None if impl is None else bool(impl),
            "implementation_status_porcelain": (impl or "").splitlines()[:200]}


def implementation_hashes() -> dict:
    return {str(p.relative_to(HERE)): common.sha256_file(p) for p in implementation_files()}


def _env_bool(name):
    v = os.environ.get(name)
    if v is None or not v.strip():
        return None
    return v.strip().lower() in ("1", "true", "yes", "on")


def inference_block() -> dict:
    """v4 FX-7: the variables orchestration/adapter exports (AUTORESEARCH_POLICY,
    _BACKEND, _FALLBACK_ALLOWED, _DEGRADED_ALLOWED, _INDEPENDENT_SESSION). The
    adapter exports no resolved model id, so none is invented: resolved_model_id
    is 'unverified' and model_verified is false."""
    e = os.environ.get
    return {"requested_policy": e("AUTORESEARCH_POLICY") or None,
            "backend": e("AUTORESEARCH_BACKEND") or None,
            "resolved_model_id": "unverified",
            "model_verified": False,
            "reasoning_effort": None,
            "fallback_allowed": _env_bool("AUTORESEARCH_FALLBACK_ALLOWED"),
            "fallback_used": None,
            "degraded_allowed": _env_bool("AUTORESEARCH_DEGRADED_ALLOWED"),
            "degraded_requirements": None,
            "independent_session": _env_bool("AUTORESEARCH_INDEPENDENT_SESSION"),
            "source": ("AUTORESEARCH_POLICY/_BACKEND/_FALLBACK_ALLOWED/_DEGRADED_ALLOWED/_INDEPENDENT_SESSION "
                       "at launch; unset -> null; no verified model id is exported, so model_verified false")}


def _pkg_version(name):
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:  # noqa: BLE001
        return None


def environment_info() -> dict:
    return {"host": hostinfo.host_identity(None), "operating_system": platform.platform(),
            "architecture": platform.machine(), "python_version": sys.version.split()[0],
            "python_executable": sys.executable, "sage_executable": common.find_sage(),
            "sage_use": "C-1 fixture reproduction only; charged paths use arith.py",
            "dependencies": {n: _pkg_version(n) for n in ("numpy", "pyyaml", "pytest", "psutil")},
            "implementation_sha256": implementation_hashes(), "inference": inference_block(),
            "env_TMPDIR": os.environ.get("TMPDIR")}


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _rss(who) -> int:
    r = resource.getrusage(who).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


class Tee:
    def __init__(self, stream, path):
        self.stream, self.fh = stream, open(path, "a", buffering=1)

    def write(self, s):
        self.stream.write(s)
        self.fh.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()
        self.fh.flush()

    def close(self):
        self.fh.close()


# ------------------------------------------------------------------ cells
def run_cell_process(task: dict, cell_dir: Path, env=None) -> dict:
    cell_dir.mkdir(parents=True)
    tpath, opath = cell_dir / "task.json", cell_dir / "result.json"
    tpath.write_text(json.dumps(task, sort_keys=True))
    cmd = ["nice", "-n", "10", sys.executable, str(HERE / "cellrun.py"), "--task", str(tpath), "--out", str(opath)]
    (cell_dir / "command.txt").write_text(" ".join(cmd) + "\n")
    with open(cell_dir / "stdout.log", "w") as so, open(cell_dir / "stderr.log", "w") as se:
        rc = subprocess.run(cmd, stdout=so, stderr=se, env=env).returncode
    if not opath.exists():
        return {"task": task, "status": "infrastructure_incomplete", "reason": f"no result (exit {rc})",
                "exit_code": rc}
    out = json.loads(opath.read_text())
    out["exit_code"] = rc
    return out


def selection(plan: dict, dry: dict | None) -> tuple[str, list]:
    if dry:
        fx = dry["fixture"]
        tasks = [{"cell_id": f"{common.fixture_id(fx)}:{k}", "bits": fx["bits"], "seed": fx["seed"], "kind": k,
                  "fixture": fx, "params": dry["params"].get(k, {})} for k in dry["kinds"]]
        return common.SMOKE_NS, tasks
    return plan["namespace"], [dict(c) for c in plan["cells"]]


def _cell_dir(run_dir: Path, cell_id: str) -> Path:
    return run_dir / "cells" / cell_id.replace(":", "__")


class RunRecord:
    """Canonical run manifest (v4 FX-2), rewritten after every state change,
    with raw-result.json (index of cells attempted so far) beside it."""

    def __init__(self, run_dir: Path, args, command: str, env_info: dict, plan_sha: str, ns: str, dry,
                 tasks: list, readings: dict, decision_path, binding: dict, snapshot: dict | None, git: dict):
        self.run_dir = run_dir
        self.t0 = time.time()
        self.cells, self.index = [], []
        self.status, self.status_note = "running", None
        self.failure_class = self.failure_reason = None
        self.started, self.finished = _now(), None
        self.result_extra = {}
        self.driver = {"git": git, "fixture_reproduction": None, "audit_accepted": None,
                       "stop_on_first_failure": True, "memory_limit_bytes": common.MEMORY_LIMIT_BYTES}
        fixtures = sorted({t["cell_id"].split(":")[0] for t in tasks})
        self.run = {
            "id": args.run_id, "experiment_id": common.EXPERIMENT_ID, "hypothesis_id": common.HYPOTHESIS_ID,
            "protocol_version": common.PROTOCOL_VERSION,
            "purpose": ("implementation smoke dry run (smoke namespace, synthetic non-frozen fixture; not evidence)"
                        if dry else "EXP-ICEX-aaccfc protocol v4 confirmatory run"),
            "code": {"commit": git.get("commit"), "branch": git.get("branch"), "dirty": git.get("dirty"),
                     "implementation_dirty": git.get("implementation_dirty"), "command": command,
                     "implementation_sha256": env_info["implementation_sha256"]},
            "environment": {"host": env_info["host"].get("hostname"),
                            "operating_system": env_info["operating_system"],
                            "architecture": env_info["architecture"],
                            "python_version": env_info["python_version"],
                            "dependencies": env_info["dependencies"],
                            "sage_executable": env_info["sage_executable"], "workers": 1,
                            "details": "environment.json"},
            "inputs": {"admission_decision": args.admission_decision if not dry else None,
                       "admission_decision_path": decision_path,
                       "admission_decision_pinning": None if dry else ADMISSION_PINNING,
                       "snapshot_receipt": (snapshot or {}).get("receipt"),
                       "snapshot_verification": snapshot,
                       "trial_plan": str(args.plan), "trial_plan_sha256": plan_sha,
                       "namespace": ns, "fixtures": fixtures, "cells_planned": [t["cell_id"] for t in tasks],
                       "seed_rule": "SHA256 of '<ns>|<kind>|...' labels (common.py); namespace above",
                       "dry_run": dry, "protocol": binding, "admission_readings_C7": readings},
            "inference": env_info["inference"],
        }

    def manifest(self) -> dict:
        peak = max([c.get("peak_rss_bytes") or 0 for c in self.cells] or [0])
        valid = self.status in ("completed_valid", "smoke_completed")
        terminal = self.status != "running"
        ok_cells = bool(self.cells) and all(c.get("status") == "ok" for c in self.cells)
        run = dict(self.run)
        run.update({
            "status": self.status, "status_note": self.status_note,
            "failure_class": self.failure_class, "failure_reason": self.failure_reason,
            "timing": {"started_at": self.started, "updated_at": _now(), "finished_at": self.finished,
                       "wall_seconds": round(time.time() - self.t0, 3)},
            "resources": {"peak_rss_bytes": peak or None, "peak_rss_source": "each cell process's own ru_maxrss",
                          "driver_peak_rss_bytes": _rss(resource.RUSAGE_SELF),
                          "children_peak_rss_bytes": _rss(resource.RUSAGE_CHILDREN)},
            "result": {"valid": valid if terminal else None,
                       "invalid_reason": None if valid or not terminal else (self.failure_reason or self.status),
                       "raw": "raw-result.json",
                       "metrics": self.result_extra.get("metrics"),
                       "metrics_sha256": self.result_extra.get("metrics_sha256"),
                       "fxa_nonverdict": self.result_extra.get("fxa_nonverdict"),
                       "audit": self.result_extra.get("audit"),
                       "cells_planned": len(self.run["inputs"]["cells_planned"]),
                       "cells_attempted": len(self.cells),
                       "certificate": {"kind": "discrete_log",
                                       "covers": ("every factor-base log, k, every descent k_t and every rho "
                                                  "solution, re-verified with verify.py arithmetic in the cell"),
                                       "verified": (ok_cells and len(self.cells) == len(
                                           self.run["inputs"]["cells_planned"])) if terminal else None,
                                       "verifier": "verify.py (independent of arith.py)"}},
            "artifacts": {"command": "command.txt", "environment": "environment.json", "stdout": "stdout.log",
                          "stderr": "stderr.log", "raw": "raw-result.json", "cells": "cells/<cell>/"},
            "depends_on_runs": []})
        return {"run": run, "driver": {**self.driver, "cells": self.cells}}

    def write(self):
        import yaml
        tmp = self.run_dir / "manifest.yaml.tmp"
        tmp.write_text(yaml.safe_dump(self.manifest(), sort_keys=False))
        os.replace(tmp, self.run_dir / "manifest.yaml")
        tmp = self.run_dir / "raw-result.json.tmp"
        tmp.write_text(json.dumps({"run_id": self.run["id"], "status": self.status, "cells": self.index,
                                   "note": "per-cell raw results live at result_path (one fresh process each)"},
                                  indent=1, sort_keys=True))
        os.replace(tmp, self.run_dir / "raw-result.json")


def _raise_signal(signum, frame):
    raise RunInterrupted(f"signal {signal.Signals(signum).name}")


def execute(args, plan, readings, decision_path, dry, command: str, binding: dict, snapshot) -> int:
    import analysis
    import audit
    import pipeline
    run_dir = Path(args.runs_dir) / args.run_id
    run_dir.mkdir(parents=True)
    ns, tasks = selection(plan, dry)
    old_out, old_err = sys.stdout, sys.stderr
    tee_out, tee_err = Tee(old_out, run_dir / "stdout.log"), Tee(old_err, run_dir / "stderr.log")
    sys.stdout, sys.stderr = tee_out, tee_err
    old_handlers = {}
    for s in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        try:
            old_handlers[s] = signal.signal(s, _raise_signal)
        except ValueError:  # not the main thread
            pass
    rec = None
    code = 0
    try:
        (run_dir / "command.txt").write_text(command + "\n")
        env_info = environment_info()
        (run_dir / "environment.json").write_text(json.dumps(env_info, indent=1))
        rec = RunRecord(run_dir, args, command, env_info, common.sha256_file(args.plan), ns, dry, tasks, readings,
                        decision_path, binding, snapshot, git_state(Path(args.repo_root)))
        rec.write()
        child_env = {k: v for k, v in os.environ.items() if k not in (ADMISSION_ENV, REPO_ENV, RUN_DIR_ENV)}
        if not dry:
            child_env.update({ADMISSION_ENV: args.admission_decision, REPO_ENV: str(Path(args.repo_root).resolve()),
                              RUN_DIR_ENV: str(run_dir.resolve())})
        rep = common.reproduce_fixtures(run_dir / "fixture_reproduction.json.out")
        (run_dir / "fixture_reproduction.json").write_text(json.dumps(rep, indent=1))
        rec.driver["fixture_reproduction"] = {k: rep.get(k) for k in (
            "byte_identical", "reproduced_sha256", "generator_sha256_matches_amendment")}
        rec.write()
        if not rep.get("byte_identical"):
            raise RunProcedureDefect("C-1 fixture reproduction mismatch")
        receipts = []
        for task in tasks:
            task = {**task, "namespace": ns}
            print(f"[{_now()}] cell {task['cell_id']} ...", flush=True)
            cdir = _cell_dir(run_dir, task["cell_id"])
            r = run_cell_process(task, cdir, env=child_env)
            receipts.append(r)
            rp = cdir / "result.json"
            entry = {"cell_id": task["cell_id"], "status": r.get("status"), "reason": r.get("reason"),
                     "peak_rss_bytes": r.get("peak_rss_bytes"), "seconds": r.get("seconds"),
                     "exit_code": r.get("exit_code")}
            rec.cells.append(entry)
            rec.index.append({**entry, "result_path": str(rp.relative_to(run_dir)) if rp.exists() else None,
                              "result_sha256": common.sha256_file(rp) if rp.exists() else None})
            rec.write()
            if r.get("status") == "procedure_defect":
                raise RunProcedureDefect(f"procedure defect in {task['cell_id']}: {r.get('reason')}")
            if r.get("status") != "ok":
                rec.failure_class = "cell_" + str(r.get("status"))
                raise RuntimeError(f"{task['cell_id']}: {r.get('status')}: {r.get('reason')}")
        aud = audit.audit_run(receipts)
        (run_dir / "audit.json").write_text(json.dumps(aud, indent=1, sort_keys=True))
        rec.driver["audit_accepted"] = aud["accepted"]
        rec.result_extra["audit"] = "audit.json"
        res = {r["task"]["cell_id"]: r["result"] for r in receipts}
        prim = [v for v in res.values() if v["kind"] == "primary"]
        if dry:
            rec.status = "smoke_completed" if aud["accepted"] else "smoke_audit_rejected"
            rec.status_note = "smoke dry run: no C-5 analysis (no ratio, exponent or verdict)"
            if not aud["accepted"]:
                code = EXIT_PROCEDURE_DEFECT
        else:
            metrics = analysis.analyse(prim, rho=[v for v in res.values() if v["kind"] == "rho"],
                                       null=[v for v in res.values() if v["kind"] == "null_randfb"],
                                       stage_cost=[v for v in res.values() if v["kind"].startswith("stage_cost")],
                                       namespace=ns, fxa=None)
            if not aud["accepted"]:
                metrics["verdict"] = None
                metrics["verdict_withheld"] = "accounting audit rejected the receipt"
            (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, sort_keys=True))
            rec.result_extra.update(metrics="metrics.json",
                                    metrics_sha256=common.sha256_file(run_dir / "metrics.json"))
            rec.status = "completed_valid" if aud["accepted"] else "invalid"
            if not aud["accepted"]:
                rec.failure_class, rec.failure_reason = "audit_rejected", "accounting audit rejected the receipt"
                code = EXIT_PROCEDURE_DEFECT
        rec.write()
        # FX-A (non-verdict) strictly after metrics.json; it cannot alter it.
        try:
            fxa = analysis.fxa_report(prim)
            (run_dir / "fxa_nonverdict.json").write_text(json.dumps(
                {"label": "FX-A descriptive, NOT a verdict input (AMD-20260929-143d11)", "per_fixture": fxa},
                indent=1, sort_keys=True))
            rec.result_extra["fxa_nonverdict"] = "fxa_nonverdict.json"
        except pipeline.ProcedureDefect as e:
            (run_dir / "fxa_nonverdict.json").write_text(json.dumps({"error": f"ProcedureDefect: {e}"}, indent=1))
            rec.result_extra["fxa_nonverdict"] = "fxa_nonverdict.json (procedure defect)"
            rec.failure_class = "procedure_defect_fxa"
            raise RunProcedureDefect(f"FX-A cross-check: {e}") from e
    except RunProcedureDefect as e:
        code = EXIT_PROCEDURE_DEFECT
        traceback.print_exc()
        if rec is not None:
            rec.status = "invalid"
            rec.failure_class = rec.failure_class or "procedure_defect"
            rec.failure_reason = str(e)
    except BaseException as e:  # noqa: BLE001 - exceptions and signals -> failed_infrastructure
        traceback.print_exc()
        if isinstance(e, pipeline.ProcedureDefect):
            code = EXIT_PROCEDURE_DEFECT
            status, cls = "invalid", "procedure_defect"
        else:
            code = EXIT_INFRASTRUCTURE
            status = "failed_infrastructure"
            cls = "signal" if isinstance(e, (RunInterrupted, KeyboardInterrupt)) else "exception"
        if rec is not None:
            rec.status = status
            rec.failure_class = rec.failure_class if (rec.failure_class or "").startswith("cell_") else cls
            rec.failure_reason = f"{type(e).__name__}: {e}"
            rec.driver["traceback"] = traceback.format_exc()[-4000:]
    finally:
        if rec is not None:
            rec.finished = _now()
            try:
                rec.write()
            except Exception:  # noqa: BLE001
                traceback.print_exc()
        for s, h in old_handlers.items():
            signal.signal(s, h)
        sys.stdout, sys.stderr = old_out, old_err
        tee_out.close()
        tee_err.close()
    if code:
        print(f"STOP [{rec.status if rec else 'failed_infrastructure'}]: "
              f"{rec.failure_reason if rec else 'run record not created'}", file=sys.stderr)
    return code


# ------------------------------------------------------------------ main
DRY_DEFAULT_KINDS = ("primary", "null_randfb", "stage_cost_m6", "stage_cost_m8", "rho")


def smoke_fixture(index: int) -> dict:
    """v4 FX-5: smoke never evaluates a frozen fixture; it uses a synthetic one."""
    import synthetic
    fx = synthetic.synthetic_fixture(index)
    if common.is_frozen_fixture(fx):
        raise ValueError("smoke fixture is frozen")
    return fx


def main(argv=None) -> int:
    argv_used = list(sys.argv[1:] if argv is None else argv)
    command = " ".join([sys.executable, str(HERE / "driver.py")] + argv_used)
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--admission-decision")
    ap.add_argument("--snapshot-receipt")
    ap.add_argument("--plan", default=str(HERE / "trial-plan-v2.json"))
    ap.add_argument("--repo-root", default=str(common.REPO_ROOT))
    ap.add_argument("--runs-dir", default=str(common.EXP_DIR / "runs"))
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--check-admission-only", action="store_true")
    ap.add_argument("--smoke-dry-run", action="store_true",
                    help="implementation check: smoke namespace, synthetic NON-frozen fixture, small counts, output "
                         "under implementation/smoke/; C-7 recorded but not enforced; no C-5 analysis")
    ap.add_argument("--dry-fixture-index", type=int, default=0)
    ap.add_argument("--dry-descents", type=int, default=2)
    ap.add_argument("--dry-heldout", type=int, default=16)
    ap.add_argument("--dry-rho-targets", type=int, default=4)
    args = ap.parse_args(argv_used)
    repo_root = Path(args.repo_root)
    if args.workers != 1:
        print("REFUSED: maximum_workers is 1 (C-7)", file=sys.stderr)
        return EXIT_REFUSED_HOST
    readings = admission_readings(repo_root)
    ok, reasons = check_c7(readings)
    print(json.dumps({"admission_readings_C7": readings, "admitted_by_precondition": ok, "reasons": reasons},
                     indent=1))
    plan = json.loads(Path(args.plan).read_text())
    binding = protocol_binding(repo_root)
    if args.smoke_dry_run:
        smoke_root = (HERE / "smoke").resolve()
        if smoke_root not in Path(args.runs_dir).resolve().parents:
            print("REFUSED: --smoke-dry-run output must be under implementation/smoke/<subdir>", file=sys.stderr)
            return EXIT_REFUSED_PLAN
        if not args.run_id or not args.run_id.startswith("DRYRUN-") or "smoke" not in args.run_id:
            print("REFUSED: --smoke-dry-run needs --run-id DRYRUN-...smoke...", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
        if (Path(args.runs_dir) / args.run_id).exists():
            print("REFUSED: smoke run directory exists (immutable)", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
        fx = smoke_fixture(args.dry_fixture_index)
        snapshot = verify_snapshot(repo_root, args.snapshot_receipt)[1] if args.snapshot_receipt else None
        dry = {"fixture": fx, "fixture_frozen": False, "kinds": list(DRY_DEFAULT_KINDS),
               "params": {"primary": {"n_descents": args.dry_descents, "n_heldout": args.dry_heldout},
                          "stage_cost_m6": {"n_heldout": args.dry_heldout},
                          "stage_cost_m8": {"n_heldout": args.dry_heldout},
                          "rho": {"n_targets": args.dry_rho_targets}},
               "admission_readings_not_enforced": {"ok": ok, "reasons": reasons},
               "protocol_binding_check": dict(zip(("ok", "problems"), check_protocol_binding(repo_root, binding)))}
        return execute(args, plan, readings, "smoke-dry-run (no admission decision)", dry, command, binding, snapshot)
    if not ok:
        print(f"REFUSED: C-7 machine-protection precondition not met: {reasons}", file=sys.stderr)
        return EXIT_REFUSED_ADMISSION
    if args.check_admission_only:
        return 0
    if not args.run_id or not re.fullmatch(r"RUN-[A-Za-z0-9._-]+", args.run_id):
        print("REFUSED: --run-id RUN-... required", file=sys.stderr)
        return EXIT_REFUSED_DECISION
    dok, decision_path = check_decision(repo_root, args.admission_decision)
    if not dok:
        print(f"REFUSED: admission decision: {decision_path}", file=sys.stderr)
        return EXIT_REFUSED_DECISION
    pok, bad = check_plan(plan)
    if not pok:
        print(f"REFUSED: trial plan does not match protocol files: {bad}", file=sys.stderr)
        return EXIT_REFUSED_PLAN
    bok, bbad = check_protocol_binding(repo_root, binding)
    if not bok:
        print(f"REFUSED: protocol v4 records do not match: {bbad}", file=sys.stderr)
        return EXIT_REFUSED_PLAN
    sok, snapshot = verify_snapshot(repo_root, args.snapshot_receipt)
    if not sok:
        print(f"REFUSED: snapshot receipt check failed: {json.dumps(snapshot)}", file=sys.stderr)
        return EXIT_REFUSED_SNAPSHOT
    if (Path(args.runs_dir) / args.run_id).exists():
        print(f"REFUSED: {Path(args.runs_dir) / args.run_id} exists (run records are immutable)", file=sys.stderr)
        return EXIT_REFUSED_EXISTS
    return execute(args, plan, readings, decision_path, None, command, binding, snapshot)


if __name__ == "__main__":
    sys.exit(main())
