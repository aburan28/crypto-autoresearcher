#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- run-package wrapper (STAGE 2 ONLY; stage 1 never calls it).

usage: python3 -B v2_run_wrapper.py RUN-ID

The command is NOT given on the command line: it is read from the package's entry in the committed
trial-plan-v2.json, so a package can only run what the plan declared. Before ANY directory is created
the wrapper REFUSES (exit 2, nothing written) unless:
  W-1  the amendment hashes to the bound sha256 (TASK-20260923-cd932c bound_protocol);
  W-2  RUN-ID is reserved in trial-plan-v2.json and is not a v1 id (EC-6);
  W-3  experiments/EXP-GFPN-05ff43/runs/RUN-ID does not exist (run records are immutable);
  W-4  implementation-v2/, implementation-v2.md and trial-plan-v2.json are tracked by git and clean
       (DP-5, AC-3, DC-6 R-11): the phase-A commit is what runs;
  W-5  every package earlier in plan order that this one `requires` has a manifest (terminal);
  W-6  for a package with gate_required: every blocking gate package has run_status completed_valid
       and gate_pass true (EC-3: no n = 5 cell before F-1..F-3, the anchor identity and the frozen
       controls pass);
  W-7  fewer than 48 v2 packages exist (DC-7 A-7);
  W-8  no other solver-like process is running (EC-10);
  W-9  a contingency package names the package it replaces and that package ended infrastructure_error.
Then it creates the directory, records command.txt, environment.json, runs the driver with
PYTHONDONTWRITEBYTECODE=1 (nothing is written into implementation-v2/), captures stdout.log / stderr.log,
and writes manifest.yaml. The wrapper never invents a status: a crashed driver is failed /
infrastructure_error.
"""
import datetime
import json
import os
import platform
import resource
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yaml                                              # noqa: E402

import v2_common as C                                    # noqa: E402
import v2_solver as V                                    # noqa: E402

RUNS = os.path.join(C.EXP_DIR, "runs")
V2_PATHS = ["experiments/EXP-GFPN-05ff43/implementation-v2", "experiments/EXP-GFPN-05ff43/implementation-v2.md",
            "experiments/EXP-GFPN-05ff43/trial-plan-v2.json"]
MAX_PACKAGES = 48


def git(*args):
    return subprocess.run(["git", "-C", C.REPO] + list(args), capture_output=True, text=True).stdout.strip()


def refuse(msg):
    print("REFUSING (nothing written): " + msg, file=sys.stderr)
    sys.exit(2)


def inference_block():
    return {
        "requested_policy": "executor-implementation",
        "resolved_model_id": None,
        "resolved_by": "not recorded by the executor; the dispatching session records the resolved binding",
        "backend": os.environ.get("AUTORESEARCH_BACKEND"),
        "policy_env": os.environ.get("AUTORESEARCH_POLICY"),
        "fallback_used": False,
        "fallback_reason": None,
        "bedrock_used": False,
        "note": "every number in this package comes from deterministic code (msolve, python-flint, PARI, pure Python); no model is in the arithmetic loop",
    }


def collect(obj, key, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                out.append(v)
            collect(v, key, out)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, key, out)
    return out


def main():
    if len(sys.argv) not in (2, 4) or (len(sys.argv) == 4 and sys.argv[2] != "--replaces"):
        refuse("usage: v2_run_wrapper.py RUN-ID [--replaces RUN-ID-OF-AN-infrastructure_error-PACKAGE]")
    rid = sys.argv[1]
    replaces = sys.argv[3] if len(sys.argv) == 4 else None
    # W-1
    if C.sha256_file(C.AMENDMENT_PATH) != C.AMENDMENT_SHA256:
        refuse("amendment sha256 mismatch (W-1)")
    plan = C.load_plan()
    # W-2
    try:
        pk = C.plan_package(plan, rid)
    except KeyError as e:
        refuse(str(e))
    if rid in plan.get("v1_ids_never_reused", []):
        refuse("v1 run id (W-2)")
    rd = os.path.join(RUNS, rid)
    # W-3
    if os.path.exists(rd):
        refuse("run directory exists (immutable): %s" % rd)
    # W-4
    tracked = git("ls-files", "--", *V2_PATHS).splitlines()
    dirty = git("status", "--porcelain", "--", *V2_PATHS).splitlines()
    if not tracked or not any(t.startswith(V2_PATHS[0]) for t in tracked) or V2_PATHS[1] not in tracked or V2_PATHS[2] not in tracked:
        refuse("implementation-v2/, implementation-v2.md and trial-plan-v2.json are not all committed (W-4, DP-5)")
    if dirty:
        refuse("v2 implementation paths are dirty (W-4, DP-5): %s" % dirty)
    # W-5
    by_id = {p["run_id"]: p for p in plan["packages"]}
    for req in pk.get("requires", []):
        if not os.path.exists(os.path.join(RUNS, req, "manifest.yaml")):
            refuse("required earlier package %s (%s) has no manifest (W-5)" % (req, by_id[req]["label"]))
    # W-6
    if pk.get("gate_required"):
        for g in plan["gate"]["blocking_packages"]:
            rp = os.path.join(RUNS, g, "raw-result.json")
            if not os.path.exists(rp):
                refuse("blocking gate package %s has not run (W-6)" % g)
            r = json.load(open(rp))
            if r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
                refuse("blocking gate package %s did not pass: status %s gate_pass %s (W-6; EC-3)" % (g, r.get("run_status"), r.get("gate_pass")))
    # W-7
    existing = [p["run_id"] for p in plan["packages"] if os.path.exists(os.path.join(RUNS, p["run_id"]))]
    if len(existing) >= MAX_PACKAGES:
        refuse("48 v2 packages already exist (W-7; DC-7 A-7): an impediment for a new Coordinator decision")
    # W-8
    others = V.other_solver_processes()
    if others:
        refuse("another solver-like process is running (W-8, EC-10): %s" % others)
    # W-9: contingency ids (trial-plan-v2.json contingency_rule)
    driver_args = pk.get("driver_args")
    if pk["kind"] == "contingency":
        if not replaces:
            refuse("a contingency package must name the package it replaces (--replaces)")
        if replaces not in by_id or by_id[replaces]["kind"] == "contingency":
            refuse("--replaces must name a planned, non-contingency package")
        tgt = by_id[replaces]
        if tgt.get("blocking"):
            refuse("gate packages are never re-run under this card: any gate failure ends the task (EC-3, AC-5)")
        mp = os.path.join(RUNS, replaces, "manifest.yaml")
        if not os.path.exists(mp):
            refuse("replaced package has no manifest")
        man = yaml.safe_load(open(mp))["run"]
        if man.get("failure_class") != "infrastructure_error":
            refuse("only an infrastructure_error package may be replaced (never implementation_error, resource_exhaustion, "
                   "invalid_measurement or a result): %s is %s" % (replaces, man.get("failure_class")))
        for p2 in plan["packages"]:
            if p2["kind"] == "contingency" and p2["run_id"] != rid and os.path.exists(os.path.join(RUNS, p2["run_id"], "manifest.yaml")):
                m2 = yaml.safe_load(open(os.path.join(RUNS, p2["run_id"], "manifest.yaml")))["run"]
                if (m2.get("package") or {}).get("replaces") == replaces:
                    refuse("%s was already replaced once by %s" % (replaces, p2["run_id"]))
        driver_args = tgt["driver_args"]
        pk = dict(pk, replaces=replaces, replaced_label=tgt["label"], watchdogs=tgt.get("watchdogs"))
    elif replaces:
        refuse("--replaces is only valid for a contingency id")
    cmd = [sys.executable, "-B", os.path.join(HERE, "v2_driver.py")] + driver_args
    os.makedirs(os.path.join(rd, "certificates"))
    env_rec = {
        "operating_system": platform.platform(), "python_version": platform.python_version(),
        "host": C.host_record(),
        "dependencies": {"msolve": C.sh("dpkg-query -W -f='${Version}' msolve"), "python_flint": C.sh("python3 -c 'import flint;print(flint.__version__)'"),
                         "numpy": C.sh("python3 -c 'import numpy;print(numpy.__version__)'"), "pyyaml": C.sh("python3 -c 'import yaml;print(yaml.__version__)'"),
                         "pari_gp": C.sh("gp --version-short 2>&1 | head -1"), "cypari2": C.sh("python3 -c 'import cypari2;print(cypari2.__version__)'"),
                         "valgrind": C.sh("valgrind --version"), "sage_python": C.SAGE_PYTHON},
        "git": {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
                "implementation_v2_last_commit": git("log", "-1", "--format=%H", "--", *V2_PATHS),
                "implementation_v2_dirty_paths": dirty, "repo_dirty_paths": git("status", "--porcelain").splitlines()},
        "amendment_sha256": C.AMENDMENT_SHA256,
        "trial_plan_sha256": C.sha256_file(C.PLAN_PATH),
        "ladder_json_sha256": C.sha256_file(C.LADDER_PATH),
    }
    json.dump(env_rec, open(os.path.join(rd, "environment.json"), "w"), indent=2)
    with open(os.path.join(rd, "command.txt"), "w") as fh:
        fh.write("# cwd: %s\n# GFPN_RUN_DIR=%s\n# PYTHONDONTWRITEBYTECODE=1\n%s\n" % (C.REPO, rd, " ".join(cmd)))
    child_env = dict(os.environ, GFPN_RUN_DIR=rd, GFPN_V2_PACKAGE=rid, GFPN_V2_REPLACES=replaces or "",
                     PYTHONHASHSEED="0", PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
    started = datetime.datetime.now(datetime.timezone.utc)
    t0 = time.time()
    with open(os.path.join(rd, "stdout.log"), "w") as so, open(os.path.join(rd, "stderr.log"), "w") as se:
        proc = subprocess.run(cmd, cwd=C.REPO, env=child_env, stdout=so, stderr=se)
    wall = time.time() - t0
    finished = datetime.datetime.now(datetime.timezone.utc)
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    raw_path = os.path.join(rd, "raw-result.json")
    raw = None
    if os.path.exists(raw_path):
        try:
            raw = json.load(open(raw_path))
        except Exception as e:                           # noqa: BLE001
            raw = {"run_status": "failed", "failure_class": "implementation_error", "note": "raw-result.json unparseable: %r" % (e,)}
    if raw is None:
        raw = {"run_status": "failed", "failure_class": "infrastructure_error", "note": "driver exited %s without writing raw-result.json" % proc.returncode}
        json.dump(raw, open(raw_path, "w"), indent=2)
        for f in ("ladder-table.yaml", "heur-dflat.yaml", "cost-band-p64.yaml"):
            C.write_yaml(os.path.join(rd, f), {"note": "driver produced no result; see stderr.log"})
    status = raw.get("run_status", "failed")
    fclass = raw.get("failure_class")
    if proc.returncode != 0 and status == "completed_valid":
        status, fclass = "failed", fclass or "infrastructure_error"
    caps = sorted({json.dumps(v, sort_keys=True) for v in collect(raw, "rlimit_as_child_getrlimit", []) if v})
    threads = sorted({v for v in collect(raw, "threads_executed", []) if v is not None})
    manifest = {"run": {
        "id": rid, "experiment_id": C.EXPERIMENT_ID, "protocol_version": 2,
        "amendment": {"id": "AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii", "sha256": C.AMENDMENT_SHA256,
                      "approval_decision": "DEC-20260923-e788a1", "conditions": ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6"]},
        "task_id": C.TASK_ID, "hypothesis_id": "H-GFPN-9a29be", "heuristic_under_test": "HEUR-GFPN-DFLAT",
        "status": status, "failure_class": fclass, "claim_tier": "toy",
        "package": {k: pk.get(k) for k in ("order", "label", "kind", "blocking", "gate_required", "requires", "replaces", "replaced_label")},
        "code": {"commit": env_rec["git"]["head"], "implementation_v2_last_commit": env_rec["git"]["implementation_v2_last_commit"],
                 "implementation_v2_clean": not dirty, "command": " ".join(cmd),
                 "wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py"},
        "inference": inference_block(),
        "environment": {k: env_rec[k] for k in ("operating_system", "python_version", "dependencies")},
        "host": env_rec["host"],
        "inputs": {"seeds": raw.get("seeds"), "parameters": {k: raw.get(k) for k in ("p", "n", "m", "curve_shape", "field", "curve") if k in raw},
                   "trial_plan_sha256": env_rec["trial_plan_sha256"], "ladder_json_sha256": env_rec["ladder_json_sha256"],
                   "data_source": raw.get("data_source")},
        "timing": {"started_at": started.isoformat(), "finished_at": finished.isoformat(), "wall_seconds": round(wall, 3)},
        "resources": {
            "child_rlimit_as_read_back_by_getrlimit": [json.loads(c) for c in caps],
            "child_rlimit_as_requested_bytes": (raw.get("envelope") or {}).get("cap_bytes"),
            "msolve_threads_executed": threads,
            "host_mem_total_kB": env_rec["host"]["mem_total_kB"], "host_swap_total_kB": env_rec["host"]["swap_total_kB"],
            "driver_and_children_maxrss_bytes_rusage": ru.ru_maxrss * 1024, "cpu_seconds_children": round(ru.ru_utime + ru.ru_stime, 3),
            "watchdogs_declared": {"package_scope": pk.get("watchdogs"), "values": plan["watchdogs"]},
            "note": "the cap recorded is the value each child read back with getrlimit after setting it (DC-6 R-1), never a wrapper default"},
        "result": {"metrics": raw.get("metrics", {}), "valid": status == "completed_valid", "gate_pass": raw.get("gate_pass"),
                   "exit_code": proc.returncode, "certificate": raw.get("certificate") or {"kind": "none", "verified": None, "verifier": None},
                   "F3": "undecidable (AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii DC-4)"},
        "artifacts": {"raw_result": "raw-result.json", "ladder_table": "ladder-table.yaml", "heur_dflat": "heur-dflat.yaml",
                      "cost_band_p64": "cost-band-p64.yaml", "certificates_dir": "certificates/", "stdout": "stdout.log", "stderr": "stderr.log",
                      "solver_inputs": "solver/ (R-10)"},
    }}
    with open(os.path.join(rd, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=110)
    print("%s: status=%s wall=%.1fs exit=%s dir=%s" % (rid, status, wall, proc.returncode, rd))
    return 0


if __name__ == "__main__":
    sys.exit(main())
