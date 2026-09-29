"""EXP-RELN-c5a377 protocol-v4 driver.

Protocol v4 = specification.yaml + AMD-20260926-a7d25d + AMD-20260929-988139
+ AMD-20260929-cc7226. A charged run is refused unless ALL hold:
  * the memory watchdog is available (psutil importable; FX-7 fails closed);
  * C-7 readings pass (15-min load <= 14, system volume >= 5 GiB free,
    repository volume >= 20 GiB free); unreadable readings fail closed;
  * --run-id RUN-... is given and the run directory does not exist;
  * --admission-decision names ledger/decisions/<DEC>.yaml, a
    coordinator_decision whose id matches, whose target_ids include
    EXP-RELN-c5a377, whose execution_admission.currently_admitted is
    exactly true, which is not superseded or withdrawn (status, a non-null
    superseded_by, or a later decision listing it under supersedes);
  * the trial plan's protocol hashes match the specification, amendment,
    fixture JSON and generator, and the fixture JSON matches the frozen hash;
  * the v3/v4 amendments and their approving decisions exist and the
    amendments carry the hashes pinned here and in the decisions (FX-2);
  * --snapshot-receipt PATH lists every implementation file with the sha256
    found in the working tree, and the implementation tree is clean (FX-5).

Each fixture runs in a fresh process (celltask.py) under nice; its own peak
RSS comes from os.wait4 and a psutil watchdog kills it above 8 GiB
(resource_exhaustion, an infrastructure outcome). The run stops at the first
procedure defect (failed identity or control).

Run record (FX-1): manifest.yaml carries the canonical top-level run: block
(docs/evidence-and-reproducibility.md) plus a driver: companion block; it is
written with status running before the first cell and rewritten after every
cell. The driver console is teed to stdout.log / stderr.log in the run
directory. An exception or SIGTERM/SIGHUP/SIGINT is recorded as
failed_infrastructure.

  python3 driver.py --check-admission-only
  python3 driver.py --run-id RUN-... --admission-decision DEC-... --snapshot-receipt PATH
  python3 driver.py --smoke-dry-run --run-id DRYRUN-... --runs-dir implementation/smoke/<dir>
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import json
import os
import platform
import re
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fixtures  # noqa: E402
import hostinfo  # noqa: E402
import labels  # noqa: E402

EXP_DIR = HERE.parent
REPO_ROOT_DEFAULT = EXP_DIR.parent.parent
ADMISSION_TARGET = "EXP-RELN-c5a377"
HYPOTHESIS_ID = "H-RELN-4d092c"
PROTOCOL_VERSION = 4
PLAN_PROTOCOL_VERSION = 2
MEMORY_LIMIT_BYTES = 8 * 2 ** 30
IMPL_REL = "experiments/EXP-RELN-c5a377/implementation"

# FX-2: governing records of protocol v4, with the amendment hashes approved by
# their decisions (amendment_sha256_at_decision).
GOVERNING = {
    "specification": ("experiments/EXP-RELN-c5a377/specification.yaml", None, None),
    "amendment_v2": ("experiments/EXP-RELN-c5a377/amendments/AMD-20260926-a7d25d.yaml",
                     "b9bdc6f4293331d9af8694e2e0c5af0345b22664e579d3eec46fdbc6fa8c7281", None),
    "amendment_v3": ("experiments/EXP-RELN-c5a377/amendments/AMD-20260929-988139.yaml",
                     "dc39dd92802eceac30f42e17e31c2d28ad8d8b6d8b781cd138f78f8c2b27f765",
                     "decision_v3"),
    "amendment_v4": ("experiments/EXP-RELN-c5a377/amendments/AMD-20260929-cc7226.yaml",
                     "7a92fbb6b0a70cbf314b401bcf15699087a68e902021ea7024dcf2f8a1d7e9dd",
                     "decision_v4"),
    "decision_v3": ("ledger/decisions/DEC-20260929-3d166b.yaml", None, None),
    "decision_v4": ("ledger/decisions/DEC-20260929-7a62cc.yaml", None, None),
    "fixtures": ("experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json",
                 fixtures.FROZEN_JSON_SHA256, None),
    "fixture_generator": ("experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.py", None, None),
}

EXIT_REFUSED_ADMISSION = 3
EXIT_REFUSED_DECISION = 4
EXIT_REFUSED_PLAN = 5
EXIT_REFUSED_EXISTS = 6
EXIT_PROCEDURE_DEFECT = 7
EXIT_INFRASTRUCTURE = 8
EXIT_REFUSED_WATCHDOG = 9
EXIT_REFUSED_SNAPSHOT = 10

ADMISSION_ENV = "RELN_C5A377_ADMISSION_DECISION"
REPO_ENV = "RELN_C5A377_REPO_ROOT"
RUN_DIR_ENV = "RELN_C5A377_RUN_DIR"


class RunInterrupted(Exception):
    pass


def import_psutil():
    try:
        return importlib.import_module("psutil")
    except ImportError:
        return None


def _load_decision(repo_root: Path, dec_id: str):
    import yaml
    path = Path(repo_root) / "ledger" / "decisions" / f"{dec_id}.yaml"
    if not path.exists():
        return None, None, f"{path} does not exist"
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return None, None, f"{path} does not parse: {e}"
    dec = doc.get("coordinator_decision") if isinstance(doc, dict) else None
    if not isinstance(dec, dict):
        return None, None, f"{path} has no coordinator_decision mapping"
    return path, (doc, dec), None


def _superseding_decisions(repo_root: Path, dec_id: str, own: Path) -> list:
    import yaml
    hits = []
    for p in sorted((Path(repo_root) / "ledger" / "decisions").glob("DEC-*.yaml")):
        if p == own:
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
        d = doc.get("coordinator_decision") if isinstance(doc, dict) else None
        sup = (d or {}).get("supersedes") if isinstance(d, dict) else None
        sup = [sup] if isinstance(sup, str) else (sup or [])
        if dec_id in sup:
            hits.append(p.name)
    return hits


def check_decision(repo_root: Path, dec_id: str | None) -> tuple[bool, str]:
    if not dec_id or not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", dec_id):
        return False, f"invalid decision id {dec_id!r}"
    path, pair, err = _load_decision(repo_root, dec_id)
    if err:
        return False, err
    doc, dec = pair
    if dec.get("id") != dec_id:
        return False, f"{path} id {dec.get('id')!r} != {dec_id}"
    for where, m in (("coordinator_decision", dec), ("document", doc)):
        st = m.get("status")
        if isinstance(st, str) and st.strip().lower() in ("superseded", "withdrawn"):
            return False, f"{path} {where} status is {st!r}"
        if m.get("superseded_by") not in (None, "", []):
            return False, f"{path} {where} has superseded_by {m.get('superseded_by')!r}"
    if ADMISSION_TARGET not in (dec.get("target_ids") or []):
        return False, f"{path} target_ids do not include {ADMISSION_TARGET}"
    adm = dec.get("execution_admission")
    if not isinstance(adm, dict) or adm.get("currently_admitted") is not True:
        got = adm.get("currently_admitted") if isinstance(adm, dict) else adm
        return False, f"{path} execution_admission.currently_admitted is {got!r}, not true"
    for k in ("status", "superseded_by"):
        v = adm.get(k)
        if (k == "status" and isinstance(v, str) and v.strip().lower() in ("superseded", "withdrawn")) or \
                (k == "superseded_by" and v not in (None, "", [])):
            return False, f"{path} execution_admission.{k} is {v!r}"
    later = _superseding_decisions(repo_root, dec_id, path)
    if later:
        return False, f"{path} is superseded by {later}"
    return True, str(path)


def check_plan(plan: dict) -> tuple[bool, list]:
    import make_trial_plan
    want = make_trial_plan.protocol_hashes()
    bad = [k for k, v in want.items() if (plan.get("protocol") or {}).get(k) != v]
    if plan.get("protocol_version") != PLAN_PROTOCOL_VERSION:
        bad.append(f"protocol_version {plan.get('protocol_version')} != {PLAN_PROTOCOL_VERSION}")
    if plan.get("namespace") != labels.FROZEN_NS:
        bad.append(f"namespace {plan.get('namespace')!r} != {labels.FROZEN_NS}")
    if fixtures.sha256_file(fixtures.FIXTURE_JSON) != fixtures.FROZEN_JSON_SHA256:
        bad.append("fixture JSON hash differs from AMD-20260926-a7d25d C-1")
    return not bad, bad


def protocol_binding(repo_root: Path) -> dict:
    """FX-2: path and sha256 of every governing record (None if absent)."""
    out = {"protocol_version": PROTOCOL_VERSION,
           "composition": "specification.yaml + AMD-20260926-a7d25d + AMD-20260929-988139 + "
                          "AMD-20260929-cc7226", "records": {}}
    for name, (rel, _, _) in GOVERNING.items():
        p = Path(repo_root) / rel
        out["records"][name] = {"path": rel, "sha256": fixtures.sha256_file(p) if p.exists() else None}
    return out


def check_protocol_binding(repo_root: Path, binding: dict) -> tuple[bool, list]:
    import yaml
    bad = []
    recs = binding["records"]
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
            except (OSError, yaml.YAMLError) as e:
                bad.append(f"{dp}: {e}")
                continue
            if d.get("amendment_sha256_at_decision") != got:
                bad.append(f"{rel} sha256 != {dp.name} amendment_sha256_at_decision")
    return not bad, bad


def _git(repo_root: Path, *a):
    r = subprocess.run(["git", "-C", str(repo_root), *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_state(repo_root: Path) -> dict:
    st = _git(repo_root, "status", "--porcelain")
    impl = _git(repo_root, "status", "--porcelain", "--untracked-files=all", "--", IMPL_REL)
    return {"commit": _git(repo_root, "rev-parse", "HEAD"),
            "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": None if st is None else bool(st), "status_porcelain": (st or "").splitlines()[:200],
            "implementation_dirty": None if impl is None else bool(impl),
            "implementation_status_porcelain": (impl or "").splitlines()[:200]}


def implementation_files() -> list:
    """Code and plan files the snapshot receipt must pin (tests included)."""
    files = sorted(HERE.glob("*.py")) + sorted((HERE / "tests").glob("*.py"))
    return files + [HERE / "trial-plan-v2.json"]


def verify_snapshot(repo_root: Path, receipt_path) -> tuple[bool, dict]:
    """FX-5: every receipt entry under the implementation directory matches the
    working tree, every implementation file is pinned, and the implementation
    tree is clean. The receipt file itself is excluded from the comparison."""
    repo_root = Path(repo_root).resolve()
    info = {"receipt": str(receipt_path) if receipt_path else None, "mismatches": [], "missing": [],
            "unpinned": [], "dirty": None, "checked": 0}
    if not receipt_path:
        info["error"] = "no --snapshot-receipt given"
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
    info["receipt_sha256"] = fixtures.sha256_file(rp)
    info["receipt_task_id"] = rec.get("task_id")
    try:
        own = str(rp.relative_to(repo_root))
    except ValueError:
        own = None
    prefix = IMPL_REL + "/"
    for rel, want in sorted(pins.items()):
        if rel == own or not rel.startswith(prefix):
            continue
        p = repo_root / rel
        info["checked"] += 1
        if not p.is_file():
            info["missing"].append(rel)
        elif fixtures.sha256_file(p) != want:
            info["mismatches"].append(rel)
    for p in implementation_files():
        rel = str(p.resolve().relative_to(repo_root))
        if rel not in pins:
            info["unpinned"].append(rel)
    impl = _git(repo_root, "status", "--porcelain", "--untracked-files=all", "--", IMPL_REL)
    if impl is None:
        info["error"] = "git status unavailable (fails closed)"
        return False, info
    info["dirty"] = bool(impl)
    info["dirty_paths"] = impl.splitlines()[:200]
    ok = not (info["mismatches"] or info["missing"] or info["unpinned"] or info["dirty"])
    return ok, info


def _env_bool(name):
    v = os.environ.get(name)
    if v is None or not v.strip():
        return None
    return v.strip().lower() in ("1", "true", "yes", "on")


def inference_block() -> dict:
    """From AUTORESEARCH_* at launch only; unset stays null."""
    e = os.environ.get
    return {"requested_policy": e("AUTORESEARCH_REQUESTED_POLICY") or e("AUTORESEARCH_POLICY") or None,
            "backend": e("AUTORESEARCH_BACKEND") or None,
            "runtime": e("AUTORESEARCH_RUNTIME") or None,
            "resolved_model_id": e("AUTORESEARCH_RESOLVED_MODEL_ID") or e("AUTORESEARCH_MODEL_ID") or "unverified",
            "model_verified": _env_bool("AUTORESEARCH_MODEL_VERIFIED") is True,
            "reasoning_effort": e("AUTORESEARCH_REASONING_EFFORT") or None,
            "fallback_allowed": _env_bool("AUTORESEARCH_FALLBACK_ALLOWED"),
            "fallback_used": _env_bool("AUTORESEARCH_FALLBACK_USED"),
            "fallback_reason": e("AUTORESEARCH_FALLBACK_REASON") or None,
            "degraded_allowed": _env_bool("AUTORESEARCH_DEGRADED_ALLOWED"),
            "degraded_requirements": e("AUTORESEARCH_DEGRADED_REQUIREMENTS") or None,
            "source": "AUTORESEARCH_* environment variables at launch; unset -> null / 'unverified'"}


def implementation_hashes() -> dict:
    return {str(p.relative_to(HERE)): fixtures.sha256_file(p) for p in implementation_files()}


def _pkg_version(name):
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return None


def sage_version() -> dict:
    for exe in ("sage", str(Path.home() / ".local" / "bin" / "sage"), "/usr/local/bin/sage"):
        try:
            r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as e:
            last = str(e)
            continue
        if r.returncode == 0 and r.stdout.strip():
            return {"version": r.stdout.strip().splitlines()[0], "executable": exe}
        last = (r.stderr or r.stdout).strip()[:200]
    return {"version": None, "error": last}


def environment_info() -> dict:
    sv = sage_version()
    return {"host": hostinfo.host_identity(), "operating_system": platform.platform(),
            "architecture": platform.machine(), "python_version": sys.version.split()[0],
            "python_executable": sys.executable, "sage_version": sv.get("version"), "sage": sv,
            "dependencies": {n: _pkg_version(n) for n in ("pyyaml", "scipy", "networkx", "psutil", "numpy",
                                                            "pytest")},
            "sage_use": "verifiers and fixture regeneration only; charged paths use ecarith.py",
            "implementation_sha256": implementation_hashes(), "inference": inference_block(),
            "env_TMPDIR": os.environ.get("TMPDIR")}


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def run_cell(cmd: list, log_dir: Path, name: str, psutil, env=None) -> dict:
    """Fresh process; per-child peak RSS via os.wait4; RSS watchdog at 8 GiB."""
    if psutil is None:
        raise RuntimeError("memory watchdog unavailable (psutil missing); refusing to launch a cell")
    out = open(log_dir / f"{name}.stdout.log", "x")
    err = open(log_dir / f"{name}.stderr.log", "x")
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=out, stderr=err, cwd=str(HERE), env=env)
    killed, peak_polled, status, ru = False, 0, None, None
    try:
        while True:
            pid, status, ru = os.wait4(proc.pid, os.WNOHANG)
            if pid:
                break
            try:
                rss = psutil.Process(proc.pid).memory_info().rss
                peak_polled = max(peak_polled, rss)
                if rss > MEMORY_LIMIT_BYTES:
                    proc.kill()
                    killed = True
            except psutil.Error:
                pass
            time.sleep(0.5)
    finally:
        if status is None:
            proc.kill()
            proc.wait()
        out.close()
        err.close()
    maxrss = ru.ru_maxrss if sys.platform == "darwin" else ru.ru_maxrss * 1024
    return {"returncode": os.waitstatus_to_exitcode(status), "peak_rss_bytes": maxrss,
            "peak_rss_polled_bytes": peak_polled, "killed_by_memory_watchdog": killed,
            "wall_seconds": time.time() - t0, "cpu_user_seconds": ru.ru_utime,
            "cpu_system_seconds": ru.ru_stime}


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


RUN_STATUS = {0: "completed_valid", EXIT_PROCEDURE_DEFECT: "invalid",
              EXIT_INFRASTRUCTURE: "failed_infrastructure"}


class RunRecord:
    """Canonical run manifest (FX-1), rewritten after every state change."""

    def __init__(self, run_dir: Path, args, command: str, env_info: dict, plan_sha: str, ns: str,
                 dry, order: list, readings: dict, decision_path, binding: dict, snapshot: dict | None,
                 git: dict):
        self.run_dir = run_dir
        self.t0 = time.time()
        self.cells, self.results = [], []
        self.failure_class = None
        self.failure_reason = None
        self.status = "running"
        self.status_note = None
        self.started = _now()
        self.finished = None
        self.run = {
            "id": args.run_id, "experiment_id": ADMISSION_TARGET, "hypothesis_id": HYPOTHESIS_ID,
            "protocol_version": PROTOCOL_VERSION,
            "purpose": ("implementation smoke dry run (smoke namespace; not evidence)" if dry
                        else "EXP-RELN-c5a377 protocol v4 confirmatory run"),
            "code": {"commit": git.get("commit"), "branch": git.get("branch"), "dirty": git.get("dirty"),
                     "implementation_dirty": git.get("implementation_dirty"), "command": command,
                     "implementation_sha256": env_info["implementation_sha256"]},
            "inference": env_info["inference"],
            "environment": {"operating_system": env_info["operating_system"],
                            "architecture": env_info["architecture"],
                            "sage_version": env_info["sage_version"],
                            "python_version": env_info["python_version"],
                            "dependencies": env_info["dependencies"],
                            "host": env_info["host"].get("hostname"), "workers": 1,
                            "details": "environment.json"},
            "inputs": {"admission_decision": args.admission_decision,
                       "admission_decision_path": decision_path,
                       "snapshot_receipt": (snapshot or {}).get("receipt"),
                       "snapshot_verification": snapshot,
                       "trial_plan": str(Path(args.plan)), "trial_plan_sha256": plan_sha,
                       "namespace": ns, "dry_run": dry, "fixtures_in_order": order,
                       "protocol": binding, "admission_readings_C7": readings,
                       "seed_rule": "SHA256 labels (labels.py); namespace above"},
        }
        self.git = git

    def manifest(self) -> dict:
        peak = max([c.get("peak_rss_bytes") or 0 for c in self.cells] or [0])
        cpu = sum((c.get("cpu_user_seconds") or 0) + (c.get("cpu_system_seconds") or 0) for c in self.cells)
        valid = self.status == "completed_valid"
        run = dict(self.run)
        run.update({
            "status": self.status, "status_note": self.status_note,
            "failure_class": self.failure_class, "failure_reason": self.failure_reason,
            "timing": {"started_at": self.started, "updated_at": _now(), "finished_at": self.finished,
                       "wall_seconds": time.time() - self.t0},
            "resources": {"peak_rss_bytes": peak or None, "cpu_seconds": cpu,
                          "peak_rss_source": "os.wait4 per fixture process"},
            "result": {"metrics": {"cells_planned": len(run["inputs"]["fixtures_in_order"]),
                                   "cells_completed": sum(1 for c in self.cells if c["status"] == "completed"),
                                   "verdict": None,
                                   "verdict_note": "C-5 verdict is computed by analysis.py from raw-result.json; "
                                                   "smoke-namespace cells never receive one"},
                       "valid": valid if self.status != "running" else None,
                       "invalid_reason": None if valid or self.status == "running"
                       else (self.failure_reason or self.status),
                       "raw": "raw-result.json",
                       "certificate": {"kind": "decomposition",
                                       "covers": "every 2-LP relation (audit.py) and every determined LP log "
                                                 "(recovery.py), re-verified with vcurve.py arithmetic",
                                       "verified": (not any(c.get("procedure_defects") for c in self.cells))
                                       if self.status != "running" and self.cells else None,
                                       "verifier": "audit.py / recovery.py via vcurve.py (independent arithmetic)"}},
            "artifacts": {"command": "command.txt", "environment": "environment.json",
                          "stdout": "stdout.log", "stderr": "stderr.log", "raw": "raw-result.json",
                          "cells": "cells/<fixture>.json, .attempts.jsonl, .stdout.log, .stderr.log"},
            "depends_on_runs": []})
        driver = {"cells": self.cells, "git": self.git, "memory_limit_bytes": MEMORY_LIMIT_BYTES,
                  "stop_on_first_procedure_defect": True}
        return {"run": run, "driver": driver}

    def write(self):
        import yaml
        tmp = self.run_dir / "manifest.yaml.tmp"
        tmp.write_text(yaml.safe_dump(self.manifest(), sort_keys=False))
        os.replace(tmp, self.run_dir / "manifest.yaml")
        tmp = self.run_dir / "raw-result.json.tmp"
        tmp.write_text(json.dumps({"run_id": self.run["id"], "status": self.status, "cells": self.results},
                                  indent=1, sort_keys=True))
        os.replace(tmp, self.run_dir / "raw-result.json")


def _raise_signal(signum, frame):
    raise RunInterrupted(f"signal {signal.Signals(signum).name}")


def execute(args, plan, readings, decision_path, dry, command: str, binding: dict,
            snapshot: dict | None, psutil) -> int:
    run_dir = Path(args.runs_dir) / args.run_id
    if run_dir.exists():
        print(f"REFUSED: {run_dir} exists (run records are immutable)", file=sys.stderr)
        return EXIT_REFUSED_EXISTS
    cells_dir = run_dir / "cells"
    cells_dir.mkdir(parents=True)
    ns = labels.SMOKE_NS if dry else labels.FROZEN_NS
    if dry and not labels.is_smoke_ns(ns):
        raise AssertionError("dry run must use a smoke namespace")
    fx_rows = {r["fixture_id"]: r for r in plan["fixtures"]}
    order = dry["fixtures"] if dry else plan["execution_order"]
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
        rec = RunRecord(run_dir, args, command, env_info, fixtures.sha256_file(args.plan), ns, dry, order,
                        readings, decision_path, binding, snapshot, git_state(Path(args.repo_root)))
        rec.write()
        child_env = dict(os.environ)
        for k in (ADMISSION_ENV, REPO_ENV, RUN_DIR_ENV):
            child_env.pop(k, None)
        if not dry:
            child_env.update({ADMISSION_ENV: args.admission_decision,
                              REPO_ENV: str(Path(args.repo_root).resolve()),
                              RUN_DIR_ENV: str(run_dir.resolve())})
        for fid in order:
            r = fx_rows[fid]
            a1 = dry["a1"] if dry else r["A1"]
            a2 = dry["a2"] if dry else r["A2"]
            reps = dry["replicates"] if dry else plan["replicates"]["rewire"]
            rhot = dry["rho_targets"] if dry else plan["rho_targets_per_fixture"]
            out = cells_dir / f"{fid}.json"
            cmd = ["nice", "-n", "10", sys.executable, str(HERE / "celltask.py"), "--bits", str(r["bits"]),
                   "--seed", str(r["seed"]), "--ns", ns, "--a1", str(a1), "--a2", str(a2),
                   "--replicates", str(reps), "--rho-targets", str(rhot), "--out", str(out)]
            print(f"[{_now()}] cell {fid}: {' '.join(cmd)}", flush=True)
            info = run_cell(cmd, cells_dir, fid, psutil, env=child_env)
            info.update(fixture_id=fid, command=cmd)
            if info["killed_by_memory_watchdog"]:
                info["status"] = "resource_exhaustion"
                code = EXIT_INFRASTRUCTURE
                rec.failure_class = "resource_exhaustion"
                rec.failure_reason = f"cell {fid} exceeded {MEMORY_LIMIT_BYTES} bytes RSS"
            elif info["returncode"] == EXIT_PROCEDURE_DEFECT:
                info["status"] = "procedure_defect"
                code = EXIT_PROCEDURE_DEFECT
                rec.failure_class = "procedure_defect"
            elif info["returncode"] != 0 or not out.exists():
                info["status"] = "infrastructure_error"
                code = EXIT_INFRASTRUCTURE
                rec.failure_class = "infrastructure_error"
                rec.failure_reason = f"cell {fid} exit {info['returncode']}, output present {out.exists()}"
            else:
                info["status"] = "completed"
            if out.exists():
                res = json.loads(out.read_text())
                info["procedure_defects"] = res["procedure_defects"]
                info["result_sha256"] = fixtures.sha256_file(out)
                rec.results.append(res)
                if code == EXIT_PROCEDURE_DEFECT:
                    rec.failure_reason = f"cell {fid}: {res['procedure_defects']}"
            rec.cells.append(info)
            rec.write()
            print(f"[{_now()}] cell {fid}: {info['status']} rss={info['peak_rss_bytes']}", flush=True)
            if code:
                break
        rec.status = RUN_STATUS[code]
    except BaseException as e:  # exceptions and signals -> failed_infrastructure
        code = EXIT_INFRASTRUCTURE
        traceback.print_exc()
        if rec is not None:
            rec.status = "failed_infrastructure"
            rec.failure_class = "signal" if isinstance(e, (RunInterrupted, KeyboardInterrupt)) else "exception"
            rec.failure_reason = f"{type(e).__name__}: {e}"
    finally:
        if rec is not None:
            rec.finished = _now()
            rec.write()
        for s, h in old_handlers.items():
            signal.signal(s, h)
        sys.stdout, sys.stderr = old_out, old_err
        tee_out.close()
        tee_err.close()
    return code


def frozen_budgets(plan: dict) -> set:
    return {int(f[k]) for f in plan["fixtures"] for k in ("A1", "A2")}


def main(argv=None) -> int:
    argv_used = list(sys.argv[1:] if argv is None else argv)
    command = " ".join([sys.executable, str(HERE / "driver.py")] + argv_used)
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--admission-decision")
    ap.add_argument("--snapshot-receipt")
    ap.add_argument("--plan", default=str(HERE / "trial-plan-v2.json"))
    ap.add_argument("--repo-root", default=str(REPO_ROOT_DEFAULT))
    ap.add_argument("--runs-dir", default=str(EXP_DIR / "runs"))
    ap.add_argument("--check-admission-only", action="store_true")
    ap.add_argument("--smoke-dry-run", action="store_true",
                    help="implementation check: smoke namespace, one fixture, budgets that differ from every "
                         "frozen A1/A2, output under implementation/smoke/; C-7 recorded, not enforced")
    ap.add_argument("--dry-fixture", default="b16-s13")
    ap.add_argument("--dry-a1", type=int, default=64)
    ap.add_argument("--dry-a2", type=int, default=256)
    ap.add_argument("--dry-replicates", type=int, default=4)
    ap.add_argument("--dry-rho-targets", type=int, default=2)
    args = ap.parse_args(argv_used)
    repo_root = Path(args.repo_root)
    psutil = import_psutil()
    if psutil is None:
        print("REFUSED: psutil is not importable, so the 8 GiB memory watchdog cannot run (FX-7)",
              file=sys.stderr)
        return EXIT_REFUSED_WATCHDOG
    readings = hostinfo.readings(repo_root)
    ok, reasons = hostinfo.check(readings)
    readings["admitted_by_precondition"] = ok
    readings["reasons"] = reasons
    plan = json.loads(Path(args.plan).read_text())
    binding = protocol_binding(repo_root)
    if args.smoke_dry_run:
        smoke_root = (HERE / "smoke").resolve()
        if smoke_root not in Path(args.runs_dir).resolve().parents:
            print("REFUSED: --smoke-dry-run output must be under implementation/smoke/", file=sys.stderr)
            return EXIT_REFUSED_PLAN
        if not args.run_id or not args.run_id.startswith("DRYRUN-"):
            print("REFUSED: --smoke-dry-run needs --run-id DRYRUN-...", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
        if args.dry_fixture not in {r["fixture_id"] for r in plan["fixtures"]}:
            print(f"REFUSED: unknown --dry-fixture {args.dry_fixture}", file=sys.stderr)
            return EXIT_REFUSED_PLAN
        frozen = frozen_budgets(plan)
        clash = sorted({args.dry_a1, args.dry_a2} & frozen)
        if clash:
            print(f"REFUSED: smoke budgets {clash} equal a frozen A1/A2 budget (AMD-20260929-cc7226 FX-6)",
                  file=sys.stderr)
            return EXIT_REFUSED_PLAN
        snapshot = None
        if args.snapshot_receipt:
            _, snapshot = verify_snapshot(repo_root, args.snapshot_receipt)
        dry = {"fixtures": [args.dry_fixture], "a1": args.dry_a1, "a2": args.dry_a2,
               "replicates": args.dry_replicates, "rho_targets": args.dry_rho_targets,
               "frozen_budgets_checked": sorted(frozen), "C7_not_enforced": {"ok": ok, "reasons": reasons}}
        return execute(args, plan, readings, "smoke-dry-run (no admission decision)", dry, command,
                       binding, snapshot, psutil)
    print(json.dumps({"admission_readings_C7": readings}, indent=1))
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
    return execute(args, plan, readings, decision_path, None, command, binding, snapshot, psutil)


if __name__ == "__main__":
    sys.exit(main())
