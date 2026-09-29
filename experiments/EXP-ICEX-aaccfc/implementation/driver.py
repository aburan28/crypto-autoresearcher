"""Run driver for EXP-ICEX-aaccfc protocol version 3 (AMD-20260929-143d11; one run, all 6 fixtures,
30 cells, one worker). NOT EXECUTED by the implementation task.

A charged run refuses to start unless, in this order:
  * the host is macOS (C-7 is stated for the repository Mac; OQ-9);
  * the C-7 machine-protection readings pass, fail-closed (15-min load <= 14,
    system volume >= 5 GiB free, repository volume >= 20 GiB free); the
    readings are recorded in the manifest;
  * --run-id is RUN-...;
  * --admission-decision names ledger/decisions/<DEC>.yaml, a
    coordinator_decision whose id matches, whose target_ids include
    EXP-ICEX-aaccfc and whose execution_admission.currently_admitted is
    exactly true (FX-1 pattern);
  * the trial plan's protocol hashes match the files on disk;
  * runs/<RUN-ID>/ does not exist (run records are immutable).
Then C-1 fixture reproduction (Sage, byte-compare; mismatch = procedure defect,
stop), then each cell in a fresh `nice -n 10` process (FX-4), then the
independent audit, then the C-5 analysis.

Usage:
  python3 driver.py --check-admission-only
  python3 driver.py --run-id RUN-... --admission-decision DEC-...
  python3 driver.py --smoke-dry-run --run-id DRYRUN-... --runs-dir implementation/smoke/driver_dryrun
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402
import hostinfo  # noqa: E402

ADMISSION_TARGET = common.EXPERIMENT_ID
EXIT_REFUSED_ADMISSION = 3
EXIT_REFUSED_DECISION = 4
EXIT_REFUSED_PLAN = 5
EXIT_REFUSED_EXISTS = 6
EXIT_PROCEDURE_DEFECT = 7
EXIT_INFRASTRUCTURE = 8
EXIT_REFUSED_HOST = 9

INFERENCE_KEYS = ("requested_policy", "resolved_model_id", "reasoning_effort", "fallback_used",
                  "degraded_requirements")


# ------------------------------------------------------------------ admission
def admission_readings(repo_root: Path) -> dict:
    """C-7 readings; any failure to read is recorded and fails closed (FX-2)."""
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


def check_decision(repo_root: Path, dec_id: str | None) -> tuple[bool, str]:
    """FX-1: admit only the explicitly named decision, and only if it is a
    coordinator_decision whose id matches, whose target_ids include
    EXP-ICEX-aaccfc and whose execution_admission.currently_admitted is true."""
    import yaml
    if not dec_id or not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", dec_id):
        return False, f"invalid decision id {dec_id!r}"
    path = repo_root / "ledger" / "decisions" / f"{dec_id}.yaml"
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
    want = {"specification_sha256": common.sha256_file(common.SPECIFICATION),
            "amendment_sha256": common.sha256_file(common.AMENDMENT),
            "amendment_v3_sha256": common.sha256_file(common.AMENDMENT_V3),
            "b0_definition_sha256": common.sha256_file(common.B0_AMENDMENT),
            "fixtures_sha256": common.sha256_file(common.FIXTURE_JSON),
            "fixture_generator_sha256": common.sha256_file(common.FIXTURE_GEN)}
    bad = [k for k, v in want.items() if plan.get("protocol", {}).get(k) != v]
    if plan.get("protocol_version") != common.PROTOCOL_VERSION:
        bad.append(f"plan protocol_version {plan.get('protocol_version')} != {common.PROTOCOL_VERSION}")
    if want["amendment_v3_sha256"] != common.AMENDMENT_V3_SHA256:
        bad.append("AMD-20260929-143d11 hash differs from DEC-20260929-a8d594 amendment_sha256_at_decision")
    if want["fixtures_sha256"] != common.FROZEN_JSON_SHA256:
        bad.append("frozen fixture JSON hash differs from AMD-20260926-ced670 C-1")
    if want["fixture_generator_sha256"] != common.FROZEN_GEN_SHA256:
        bad.append("fixture generator hash differs from AMD-20260926-ced670 C-1")
    if plan.get("n_cells") != 30 or len(plan.get("cells", [])) != 30:
        bad.append("plan does not cover 6 fixtures x 5 cells")
    return not bad, bad


# ------------------------------------------------------------------ provenance
def git_state(repo_root: Path) -> dict:
    def g(*a):
        r = subprocess.run(["git", "-C", str(repo_root), *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    status = g("status", "--porcelain")
    return {"commit": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": None if status is None else bool(status),
            "status_porcelain": (status or "").splitlines()[:200]}


def implementation_hashes() -> dict:
    return {p.name: common.sha256_file(p) for p in sorted(HERE.glob("*.py"))}


def _env_bool(name):
    v = os.environ.get(name)
    if v is None or not v.strip():
        return None
    return v.strip().lower() in ("1", "true", "yes", "on")


def _env_list(name):
    v = os.environ.get(name)
    if v is None:
        return None
    v = v.strip()
    if not v:
        return []
    try:
        out = json.loads(v)
        if isinstance(out, list):
            return [str(x) for x in out]
    except ValueError:
        pass
    return [x.strip() for x in v.split(",") if x.strip()]


def inference_block() -> dict:
    """FX-5: inference provenance from the launch environment only; unset stays null/'unverified'."""
    env = os.environ.get
    model = env("AUTORESEARCH_RESOLVED_MODEL_ID") or env("AUTORESEARCH_MODEL_ID")
    return {"requested_policy": env("AUTORESEARCH_REQUESTED_POLICY") or env("AUTORESEARCH_POLICY") or None,
            "backend": env("AUTORESEARCH_BACKEND") or None, "runtime": env("AUTORESEARCH_RUNTIME") or None,
            "resolved_model_id": model or "unverified",
            "model_verified": _env_bool("AUTORESEARCH_MODEL_VERIFIED") is True,
            "reasoning_effort": env("AUTORESEARCH_REASONING_EFFORT") or None,
            "fallback_allowed": _env_bool("AUTORESEARCH_FALLBACK_ALLOWED"),
            "fallback_used": _env_bool("AUTORESEARCH_FALLBACK_USED"),
            "fallback_reason": env("AUTORESEARCH_FALLBACK_REASON") or None,
            "degraded_allowed": _env_bool("AUTORESEARCH_DEGRADED_ALLOWED"),
            "degraded_requirements": _env_list("AUTORESEARCH_DEGRADED_REQUIREMENTS"),
            "independent_session": _env_bool("AUTORESEARCH_INDEPENDENT_SESSION"),
            "source": "AUTORESEARCH_* environment variables at launch; unset -> null / 'unverified'"}


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class Tee:
    def __init__(self, stream, path):
        self.stream, self.fh = stream, open(path, "a", buffering=1)

    def write(self, s):
        self.stream.write(s)
        self.fh.write(s)

    def flush(self):
        self.stream.flush()
        self.fh.flush()


# ------------------------------------------------------------------ cells
def run_cell_process(task: dict, cell_dir: Path) -> dict:
    cell_dir.mkdir(parents=True)
    tpath, opath = cell_dir / "task.json", cell_dir / "result.json"
    tpath.write_text(json.dumps(task, sort_keys=True))
    cmd = ["nice", "-n", "10", sys.executable, str(HERE / "cellrun.py"), "--task", str(tpath), "--out", str(opath)]
    (cell_dir / "command.txt").write_text(" ".join(cmd) + "\n")
    with open(cell_dir / "stdout.log", "w") as so, open(cell_dir / "stderr.log", "w") as se:
        rc = subprocess.run(cmd, stdout=so, stderr=se).returncode
    if not opath.exists():
        return {"task": task, "status": "infrastructure_incomplete", "reason": f"no result (exit {rc})",
                "exit_code": rc}
    out = json.loads(opath.read_text())
    out["exit_code"] = rc
    return out


def selection(plan: dict, dry: dict | None) -> tuple[str, list]:
    if dry:
        fx = common.fixture(16, 21)
        tasks = [{"cell_id": f"{common.fixture_id(fx)}:{k}", "bits": 16, "seed": 21, "kind": k,
                  "params": dry["params"].get(k, {})} for k in dry["kinds"]]
        return common.SMOKE_NS, tasks
    return plan["namespace"], [dict(c) for c in plan["cells"]]


def run(args, readings, decision_path, plan, dry) -> int:
    import yaml
    import analysis
    import audit
    repo_root = Path(args.repo_root)
    run_dir = Path(args.runs_dir) / args.run_id
    run_dir.mkdir(parents=True)
    t0 = time.time()
    out0, err0 = sys.stdout, sys.stderr
    sys.stdout = Tee(sys.__stdout__, run_dir / "stdout.log")
    sys.stderr = Tee(sys.__stderr__, run_dir / "stderr.log")
    (run_dir / "command.txt").write_text(" ".join([sys.executable] + sys.argv) + "\n")
    env = {"host": hostinfo.host_identity(None), "implementation_sha256": implementation_hashes(),
           "inference": inference_block()}
    (run_dir / "environment.json").write_text(json.dumps(env, indent=1))
    ns, tasks = selection(plan, dry)
    manifest = {
        "run_id": args.run_id, "experiment_id": common.EXPERIMENT_ID, "protocol_version": common.PROTOCOL_VERSION,
        "admission_decision": args.admission_decision, "admission_decision_path": decision_path,
        "protocol": plan["protocol"], "trial_plan_sha256": common.sha256_file(args.plan),
        "git": git_state(repo_root), "host": env["host"], "admission_readings_C7": readings,
        "implementation_sha256": env["implementation_sha256"], "namespace": ns,
        "started_at": _now(), "status": "running", "validity": None,
        "inference": env["inference"], **{k: env["inference"][k] for k in INFERENCE_KEYS},
        "smoke_dry_run": dry, "cells": [],
    }

    def write_manifest():
        manifest["wall_seconds"] = round(time.time() - t0, 3)
        manifest["driver_peak_rss_bytes"] = _rss(resource.RUSAGE_SELF)
        manifest["children_peak_rss_bytes"] = _rss(resource.RUSAGE_CHILDREN)
        (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))

    def finish(status, reason, code):
        manifest["status"] = status
        manifest["validity"] = {"status": status, "reason": reason}
        manifest["ended_at"] = _now()
        write_manifest()
        if code:
            print(f"STOP [{status}]: {reason}", file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout, sys.stderr = out0, err0
        return code

    write_manifest()
    rep = common.reproduce_fixtures(run_dir / "fixture_reproduction.json.out")
    (run_dir / "fixture_reproduction.json").write_text(json.dumps(rep, indent=1))
    manifest["fixture_reproduction"] = {k: rep.get(k) for k in ("byte_identical", "reproduced_sha256",
                                                                 "generator_sha256_matches_amendment")}
    if not rep.get("byte_identical"):
        return finish("invalid", "C-1 fixture reproduction mismatch (procedure defect)", EXIT_PROCEDURE_DEFECT)
    receipts = []
    for task in tasks:
        task = {**task, "namespace": ns}
        print(f"cell {task['cell_id']} ...", flush=True)
        r = run_cell_process(task, run_dir / "cells" / task["cell_id"].replace(":", "__"))
        receipts.append(r)
        manifest["cells"].append({"cell_id": task["cell_id"], "status": r.get("status"),
                                  "peak_rss_bytes": r.get("peak_rss_bytes"), "seconds": r.get("seconds"),
                                  "reason": r.get("reason")})
        write_manifest()
        if r.get("status") == "procedure_defect":
            return finish("invalid", f"procedure defect in {task['cell_id']}: {r.get('reason')}", EXIT_PROCEDURE_DEFECT)
        if r.get("status") != "ok":
            return finish("failed_infrastructure", f"{task['cell_id']}: {r.get('reason')}", EXIT_INFRASTRUCTURE)
    aud = audit.audit_run(receipts)
    (run_dir / "audit.json").write_text(json.dumps(aud, indent=1, sort_keys=True))
    manifest["audit_accepted"] = aud["accepted"]
    index = []
    for r in receipts:
        rp = run_dir / "cells" / r["task"]["cell_id"].replace(":", "__") / "result.json"
        index.append({"cell_id": r["task"]["cell_id"], "status": r.get("status"),
                      "result_path": str(rp.relative_to(run_dir)), "result_sha256": common.sha256_file(rp),
                      "peak_rss_bytes": r.get("peak_rss_bytes"), "seconds": r.get("seconds")})
    (run_dir / "raw-result.json").write_text(json.dumps(
        {"cells": index, "note": "per-cell raw results live at result_path (one fresh process each)"},
        indent=1, sort_keys=True))
    if dry:
        manifest["analysis"] = "not computed in smoke dry-run (verdict metric withheld by handoff)"
        return finish("smoke_completed" if aud["accepted"] else "smoke_audit_rejected",
                      "smoke dry-run; no scientific output", 0 if aud["accepted"] else EXIT_PROCEDURE_DEFECT)
    res = {r["task"]["cell_id"]: r["result"] for r in receipts}
    prim = [v for v in res.values() if v["kind"] == "primary"]
    metrics = analysis.analyse(prim, rho=[v for v in res.values() if v["kind"] == "rho"],
                               null=[v for v in res.values() if v["kind"] == "null_randfb"],
                               stage_cost=[v for v in res.values() if v["kind"].startswith("stage_cost")],
                               namespace=ns)
    if not aud["accepted"]:
        metrics["verdict"] = None
        metrics["verdict_withheld"] = "accounting audit rejected the receipt"
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, sort_keys=True))
    return finish("completed_valid" if aud["accepted"] else "invalid",
                  "all cells completed; audit " + ("accepted" if aud["accepted"] else "rejected"),
                  0 if aud["accepted"] else EXIT_PROCEDURE_DEFECT)


def _rss(who) -> int:
    r = resource.getrusage(who).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


# ------------------------------------------------------------------ main
DRY_DEFAULT_KINDS = ("primary", "null_randfb", "stage_cost_m6", "stage_cost_m8", "rho")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--admission-decision")
    ap.add_argument("--plan", default=str(HERE / "trial-plan-v2.json"))
    ap.add_argument("--repo-root", default=str(common.REPO_ROOT))
    ap.add_argument("--runs-dir", default=str(common.EXP_DIR / "runs"))
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--check-admission-only", action="store_true")
    ap.add_argument("--smoke-dry-run", action="store_true",
                    help="implementation check: smoke namespace, b16-s21 only, small counts, output under "
                         "implementation/smoke/; C-7 readings recorded but not enforced; no analysis")
    ap.add_argument("--dry-descents", type=int, default=2)
    ap.add_argument("--dry-heldout", type=int, default=16)
    ap.add_argument("--dry-rho-targets", type=int, default=4)
    args = ap.parse_args(argv)
    repo_root = Path(args.repo_root)
    if args.workers != 1:
        print("REFUSED: maximum_workers is 1 (C-7)", file=sys.stderr)
        return EXIT_REFUSED_HOST
    readings = admission_readings(repo_root)
    ok, reasons = check_c7(readings)
    print(json.dumps({"admission_readings_C7": readings, "admitted_by_precondition": ok, "reasons": reasons},
                     indent=1))
    dry = None
    if args.smoke_dry_run:
        smoke_root = (HERE / "smoke").resolve()
        runs = Path(args.runs_dir).resolve()
        if smoke_root not in runs.parents and runs != smoke_root:
            print("REFUSED: --smoke-dry-run output must be under implementation/smoke/", file=sys.stderr)
            return EXIT_REFUSED_PLAN
        if not args.run_id or not args.run_id.startswith("DRYRUN-") or "smoke" not in args.run_id:
            print("REFUSED: --smoke-dry-run needs --run-id DRYRUN-...smoke...", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
        dry = {"fixture": "b16-s21", "kinds": list(DRY_DEFAULT_KINDS),
               "params": {"primary": {"n_descents": args.dry_descents, "n_heldout": args.dry_heldout},
                          "stage_cost_m6": {"n_heldout": args.dry_heldout},
                          "stage_cost_m8": {"n_heldout": args.dry_heldout},
                          "rho": {"n_targets": args.dry_rho_targets}},
               "admission_readings_not_enforced": {"ok": ok, "reasons": reasons}}
        decision_path = "smoke-dry-run (no admission decision)"
    else:
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
    plan = json.loads(Path(args.plan).read_text())
    pok, bad = check_plan(plan)
    if not pok:
        print(f"REFUSED: trial plan does not match protocol files: {bad}", file=sys.stderr)
        return EXIT_REFUSED_PLAN
    if (Path(args.runs_dir) / args.run_id).exists():
        print(f"REFUSED: {Path(args.runs_dir) / args.run_id} exists (run records are immutable)", file=sys.stderr)
        return EXIT_REFUSED_EXISTS
    return run(args, readings, decision_path, plan, dry)


if __name__ == "__main__":
    sys.exit(main())
