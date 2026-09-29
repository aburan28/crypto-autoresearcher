"""EXP-RELN-c5a377 protocol-v2 driver.

A charged run is refused unless ALL hold:
  * C-7 readings pass (15-min load <= 14, system volume >= 5 GiB free,
    repository volume >= 20 GiB free); unreadable readings fail closed;
  * --run-id RUN-... is given and the run directory does not exist;
  * --admission-decision names ledger/decisions/<DEC>.yaml, a
    coordinator_decision whose id matches, whose target_ids include
    EXP-RELN-c5a377 and whose execution_admission.currently_admitted is
    exactly true;
  * the trial plan's protocol hashes match the specification, amendment,
    fixture JSON and generator, and the fixture JSON matches the frozen hash.

Each fixture runs in a fresh process (celltask.py) under nice; its own peak
RSS comes from os.wait4 and a psutil watchdog kills it above 8 GiB
(resource_exhaustion, an infrastructure outcome). The run stops at the first
procedure defect (failed identity or control).

  python3 driver.py --check-admission-only
  python3 driver.py --run-id RUN-... --admission-decision DEC-...
  python3 driver.py --smoke-dry-run --run-id DRYRUN-... --runs-dir implementation/smoke/dry
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fixtures  # noqa: E402
import hostinfo  # noqa: E402
import labels  # noqa: E402

EXP_DIR = HERE.parent
REPO_ROOT_DEFAULT = EXP_DIR.parent.parent
ADMISSION_TARGET = "EXP-RELN-c5a377"
PROTOCOL_VERSION = 2
MEMORY_LIMIT_BYTES = 8 * 2 ** 30

EXIT_REFUSED_ADMISSION = 3
EXIT_REFUSED_DECISION = 4
EXIT_REFUSED_PLAN = 5
EXIT_REFUSED_EXISTS = 6
EXIT_PROCEDURE_DEFECT = 7
EXIT_INFRASTRUCTURE = 8


def check_decision(repo_root: Path, dec_id: str | None) -> tuple[bool, str]:
    import yaml
    if not dec_id or not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", dec_id):
        return False, f"invalid decision id {dec_id!r}"
    path = Path(repo_root) / "ledger" / "decisions" / f"{dec_id}.yaml"
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
    if ADMISSION_TARGET not in (dec.get("target_ids") or []):
        return False, f"{path} target_ids do not include {ADMISSION_TARGET}"
    adm = dec.get("execution_admission")
    if not isinstance(adm, dict) or adm.get("currently_admitted") is not True:
        got = adm.get("currently_admitted") if isinstance(adm, dict) else adm
        return False, f"{path} execution_admission.currently_admitted is {got!r}, not true"
    return True, str(path)


def check_plan(plan: dict) -> tuple[bool, list]:
    import make_trial_plan
    want = make_trial_plan.protocol_hashes()
    bad = [k for k, v in want.items() if (plan.get("protocol") or {}).get(k) != v]
    if plan.get("protocol_version") != PROTOCOL_VERSION:
        bad.append(f"protocol_version {plan.get('protocol_version')} != {PROTOCOL_VERSION}")
    if plan.get("namespace") != labels.FROZEN_NS:
        bad.append(f"namespace {plan.get('namespace')!r} != {labels.FROZEN_NS}")
    if fixtures.sha256_file(fixtures.FIXTURE_JSON) != fixtures.FROZEN_JSON_SHA256:
        bad.append("fixture JSON hash differs from AMD-20260926-a7d25d C-1")
    return not bad, bad


def git_state(repo_root: Path) -> dict:
    def g(*a):
        r = subprocess.run(["git", "-C", str(repo_root), *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    st = g("status", "--porcelain")
    return {"commit": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": None if st is None else bool(st), "status_porcelain": (st or "").splitlines()[:200]}


def _env_bool(name):
    v = os.environ.get(name)
    if v is None or not v.strip():
        return None
    return v.strip().lower() in ("1", "true", "yes", "on")


def inference_block() -> dict:
    """FX-5 pattern: from AUTORESEARCH_* at launch only; unset stays null."""
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
    return {p.name: fixtures.sha256_file(p) for p in sorted(HERE.glob("*.py"))}


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def run_cell(cmd: list, log_dir: Path, name: str) -> dict:
    """Fresh process; per-child peak RSS via os.wait4; RSS watchdog at 8 GiB."""
    try:
        import psutil
    except ImportError:
        psutil = None
    out = open(log_dir / f"{name}.stdout.log", "x")
    err = open(log_dir / f"{name}.stderr.log", "x")
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=out, stderr=err, cwd=str(HERE))
    killed, peak_polled = False, 0
    while True:
        pid, status, ru = os.wait4(proc.pid, os.WNOHANG)
        if pid:
            break
        if psutil is not None:
            try:
                rss = psutil.Process(proc.pid).memory_info().rss
                peak_polled = max(peak_polled, rss)
                if rss > MEMORY_LIMIT_BYTES:
                    proc.kill()
                    killed = True
            except psutil.Error:
                pass
        time.sleep(0.5)
    out.close()
    err.close()
    maxrss = ru.ru_maxrss if sys.platform == "darwin" else ru.ru_maxrss * 1024
    return {"returncode": os.waitstatus_to_exitcode(status), "peak_rss_bytes": maxrss,
            "peak_rss_polled_bytes": peak_polled, "killed_by_memory_watchdog": killed,
            "wall_seconds": time.time() - t0, "cpu_user_seconds": ru.ru_utime,
            "cpu_system_seconds": ru.ru_stime}


def execute(args, plan, readings, decision_path, dry) -> int:
    import yaml
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
    manifest = {"run_id": args.run_id, "experiment_id": ADMISSION_TARGET,
                "protocol_version": PROTOCOL_VERSION, "status": "running", "started_at": _now(),
                "dry_run": dry, "namespace": ns, "admission_decision": args.admission_decision,
                "admission_decision_path": decision_path, "admission_readings_C7": readings,
                "git": git_state(Path(args.repo_root)), "plan_sha256": fixtures.sha256_file(args.plan),
                "protocol": plan["protocol"], "inference": inference_block(),
                "certificate": {"kind": "relation_and_log_certificates",
                                "verifier": "audit.py / recovery.py via vcurve.py (independent arithmetic)"},
                "cells": []}
    (run_dir / "command.txt").write_text(" ".join([sys.executable] + sys.argv) + "\n")
    (run_dir / "environment.json").write_text(json.dumps(
        {"host": hostinfo.host_identity(), "implementation_sha256": implementation_hashes(),
         "inference": inference_block(), "env_TMPDIR": os.environ.get("TMPDIR")}, indent=1))
    results, code = [], 0
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
        info = run_cell(cmd, cells_dir, fid)
        info.update(fixture_id=fid, command=cmd)
        if info["killed_by_memory_watchdog"]:
            info["status"] = "resource_exhaustion"
            code = EXIT_INFRASTRUCTURE
        elif info["returncode"] == EXIT_PROCEDURE_DEFECT:
            info["status"] = "procedure_defect"
            code = EXIT_PROCEDURE_DEFECT
        elif info["returncode"] != 0 or not out.exists():
            info["status"] = "infrastructure_error"
            code = EXIT_INFRASTRUCTURE
        else:
            info["status"] = "completed"
        if out.exists():
            res = json.loads(out.read_text())
            info["procedure_defects"] = res["procedure_defects"]
            info["result_sha256"] = fixtures.sha256_file(out)
            results.append(res)
        manifest["cells"].append(info)
        print(f"[{_now()}] cell {fid}: {info['status']} rss={info['peak_rss_bytes']}", flush=True)
        if code:
            break
    manifest["finished_at"] = _now()
    manifest["status"] = {0: "completed", EXIT_PROCEDURE_DEFECT: "procedure_defect"}.get(code, "failed_infrastructure")
    (run_dir / "raw-result.json").write_text(json.dumps({"run_id": args.run_id, "cells": results},
                                                        indent=1, sort_keys=True))
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    return code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--admission-decision")
    ap.add_argument("--plan", default=str(HERE / "trial-plan-v2.json"))
    ap.add_argument("--repo-root", default=str(REPO_ROOT_DEFAULT))
    ap.add_argument("--runs-dir", default=str(EXP_DIR / "runs"))
    ap.add_argument("--check-admission-only", action="store_true")
    ap.add_argument("--smoke-dry-run", action="store_true",
                    help="implementation check: smoke namespace, b16-s11 only, tiny counts, output under "
                         "implementation/smoke/; C-7 readings recorded, not enforced")
    ap.add_argument("--dry-a1", type=int, default=64)
    ap.add_argument("--dry-a2", type=int, default=256)
    ap.add_argument("--dry-replicates", type=int, default=4)
    ap.add_argument("--dry-rho-targets", type=int, default=2)
    args = ap.parse_args(argv)
    repo_root = Path(args.repo_root)
    readings = hostinfo.readings(repo_root)
    ok, reasons = hostinfo.check(readings)
    readings["admitted_by_precondition"] = ok
    readings["reasons"] = reasons
    plan = json.loads(Path(args.plan).read_text())
    if args.smoke_dry_run:
        smoke_root = (HERE / "smoke").resolve()
        if smoke_root not in Path(args.runs_dir).resolve().parents:
            print("REFUSED: --smoke-dry-run output must be under implementation/smoke/", file=sys.stderr)
            return EXIT_REFUSED_PLAN
        if not args.run_id or not args.run_id.startswith("DRYRUN-"):
            print("REFUSED: --smoke-dry-run needs --run-id DRYRUN-...", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
        dry = {"fixtures": ["b16-s11"], "a1": args.dry_a1, "a2": args.dry_a2,
               "replicates": args.dry_replicates, "rho_targets": args.dry_rho_targets,
               "C7_not_enforced": {"ok": ok, "reasons": reasons}}
        return execute(args, plan, readings, "smoke-dry-run (no admission decision)", dry)
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
    return execute(args, plan, readings, decision_path, None)


if __name__ == "__main__":
    sys.exit(main())
