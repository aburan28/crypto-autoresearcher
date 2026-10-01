#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 -- ADDENDUM run-package wrapper (stage 2b only; stage 1b never runs a package).

usage: python3 -B a1_run_wrapper.py RUN-ID [--replaces RUN-ID]
       python3 -B a1_run_wrapper.py RUN-ID [--replaces RUN-ID] --dry-run     (evaluate the refusals only)

The command is NOT given on the command line: it is read from the package's entry in the committed
trial-plan-v2-a1.json. Before ANY directory is created the wrapper evaluates EVERY check below and REFUSES
(exit 2, nothing written, every failing reason printed) unless all hold (card S1B-3; addendum A1-7 (2);
DEC-20260923-8b2dbf AA-5 (b), (e)):
  A-1  both amendment hashes match (v2 amendment e02d4976...d3; addendum 2c5e0524...0c);
  A-2  RUN-ID is reserved in trial-plan-v2-a1.json, and is neither a v1 id (v1_ids_never_reused of either
       plan) nor a v2 id (any run id reserved in trial-plan-v2.json);
  A-3  experiments/EXP-GFPN-05ff43/runs/RUN-ID does not exist (run records are immutable);
  A-4  implementation-v2/, implementation-v2.md and trial-plan-v2.json match the TASK-20260923-0fa03f
       phase-A receipt file by file, are tracked by git and clean;
  A-5  implementation-v2-a1/, implementation-v2-a1.md and trial-plan-v2-a1.json are tracked by git, clean,
       and match the TASK-20260923-4ff597 phase-A receipt file by file (the receipt must exist and its
       implementation-v2-a1/ file list must equal git's);
  A-6  the A1-2 gates: the four v2 gate packages RUN-GFPN-ac4487, RUN-GFPN-3377f1, RUN-GFPN-76420e and
       RUN-GFPN-b231c1 have run_status completed_valid and gate_pass true; for packages 2-9 and any
       contingency, controls_a1 has run_status completed_valid and gate_pass true;
  A-7  every package this one `requires` has a manifest;
  A-8  the plan's watchdogs object equals trial-plan-v2.json's (its lines 95-177) exactly (AC-6);
  A-9  no other solver-like process is running (EC-10; AC-6);
  A-10 the SHARED DC-7 A-7 ceiling: existing v2 run directories + existing addendum run directories + this
       one <= 48 (AA-5 (e)); and the addendum's own count never exceeds its plan's package_count;
  A-11 a contingency id obeys trial-plan-v2.json's contingency_rule verbatim, for ADDENDUM packages only:
       --replaces names a planned, non-contingency, non-blocking addendum package whose manifest records
       failure_class infrastructure_error and that has not been replaced before; --replaces is refused
       for any other id;
  A-12 the plan records protocol_version "2-a1", this addendum's id and sha256 and task TASK-20260923-6c7f55,
       and carries no forbidden task id.
Then it creates the directory, records command.txt and environment.json, runs a1_driver.py with
PYTHONDONTWRITEBYTECODE=1, captures stdout.log / stderr.log and writes manifest.yaml (A1-7 (3)). The wrapper
never invents a status: a crashed driver is failed / infrastructure_error.
"""
import datetime
import json
import os
import platform
import resource
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

import yaml                                              # noqa: E402

import v2_solver as V                                    # noqa: E402

HERE = AC.HERE
DRIVER = os.path.join(HERE, "a1_driver.py")
RUNS = AC.RUNS_DIR
REPO = AC.REPO


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True).stdout.strip()


def git_tree_state(paths_rel):
    """(tracked files, dirty porcelain lines) for repo-relative paths."""
    return git("ls-files", "--", *paths_rel).splitlines(), git("status", "--porcelain", "--untracked-files=all", "--", *paths_rel).splitlines()


def phase_a_commit(receipt, receipt_path):
    """The phase-A commit of an archive: the receipt's backfilled commit_sha if present, else the commit that added the
    receipt file (`git log -1 -- <receipt>`), since a receipt never carries its own commit's sha when first written."""
    if receipt.get("commit_sha"):
        return receipt["commit_sha"], "receipt commit_sha (backfilled)"
    sha = git("log", "-1", "--format=%H", "--", os.path.relpath(receipt_path, REPO))
    return (sha or None), ("git log -1 of the receipt file" if sha else "not determinable: receipt not committed")


def _raw(rid):
    rp = os.path.join(RUNS, rid, "raw-result.json")
    if not os.path.exists(rp):
        return None
    try:
        return json.load(open(rp))
    except Exception:                                    # noqa: BLE001
        return {"run_status": "unparseable"}


def _manifest(rid):
    mp = os.path.join(RUNS, rid, "manifest.yaml")
    if not os.path.exists(mp):
        return None
    return yaml.safe_load(open(mp))["run"]


def preflight(rid, replaces=None):
    """Evaluate every refusal. Returns (refusals, info). Writes nothing."""
    ref, info = [], {"rid": rid, "replaces": replaces}
    # A-1
    h_v2 = AC.sha256_file(AC.V2_AMENDMENT_PATH)
    h_a1 = AC.sha256_file(AC.ADDENDUM_PATH)
    info["amendment_sha256"] = {"v2": h_v2, "addendum": h_a1}
    if h_v2 != AC.V2_AMENDMENT_SHA256:
        ref.append("A-1 v2 amendment sha256 mismatch")
    if h_a1 != AC.ADDENDUM_SHA256:
        ref.append("A-1 addendum sha256 mismatch")
    try:
        plan = AC.load_json(AC.PLAN_A1_PATH)
        v2plan = AC.load_json(AC.V2_PLAN_PATH)
    except Exception as e:                               # noqa: BLE001
        return ref + ["A-2 plan unreadable: %r" % (e,)], info
    by_id = {p["run_id"]: p for p in plan["packages"]}
    v2_ids = {p["run_id"] for p in v2plan["packages"]}
    v1_ids = set(plan.get("v1_ids_never_reused", [])) | set(v2plan.get("v1_ids_never_reused", []))
    pk = by_id.get(rid)
    # A-2
    if rid in v1_ids:
        ref.append("A-2 %s is a v1 run id" % rid)
    if rid in v2_ids:
        ref.append("A-2 %s is a v2 run id (reserved in trial-plan-v2.json); v2 packages run only through v2_run_wrapper.py" % rid)
    if pk is None:
        ref.append("A-2 %s is not reserved in trial-plan-v2-a1.json" % rid)
    # A-3
    if os.path.exists(os.path.join(RUNS, rid)):
        ref.append("A-3 run directory exists (immutable): %s" % os.path.join(RUNS, rid))
    # A-4
    tr, dirty = git_tree_state(AC.V2_PATHS_REL)
    info["v2_tracked"], info["v2_dirty"] = len(tr), dirty
    if not any(t.startswith(AC.V2_PATHS_REL[0] + "/") for t in tr) or AC.V2_PATHS_REL[1] not in tr or AC.V2_PATHS_REL[2] not in tr:
        ref.append("A-4 implementation-v2/, implementation-v2.md and trial-plan-v2.json are not all tracked")
    if dirty:
        ref.append("A-4 v2 paths are dirty: %s" % dirty)
    if not os.path.exists(AC.RECEIPT_V2_PHASE_A):
        ref.append("A-4 TASK-20260923-0fa03f phase-A receipt absent")
    else:
        rc = AC.load_json(AC.RECEIPT_V2_PHASE_A)
        info["v2_phase_a_commit"], info["v2_phase_a_commit_source"] = phase_a_commit(rc, AC.RECEIPT_V2_PHASE_A)
        bad = [p for p, h in AC.receipt_paths(rc).items() if not os.path.exists(os.path.join(REPO, p)) or AC.sha256_file(os.path.join(REPO, p)) != h]
        if bad:
            ref.append("A-4 v2 paths differ from the TASK-20260923-0fa03f phase-A receipt: %s" % bad)
        extra = sorted(set(t for t in tr if t.startswith(AC.V2_PATHS_REL[0] + "/")) - set(AC.receipt_paths(rc)))
        if extra:
            ref.append("A-4 files under implementation-v2/ not bound by the phase-A receipt: %s" % extra)
    # A-5
    tr1, dirty1 = git_tree_state(AC.A1_PATHS_REL)
    info["a1_tracked"], info["a1_dirty"] = len(tr1), dirty1
    if not any(t.startswith(AC.A1_PATHS_REL[0] + "/") for t in tr1) or AC.A1_PATHS_REL[1] not in tr1 or AC.A1_PATHS_REL[2] not in tr1:
        ref.append("A-5 implementation-v2-a1/, implementation-v2-a1.md and trial-plan-v2-a1.json are not all committed (phase A of TASK-20260923-4ff597)")
    if dirty1:
        ref.append("A-5 addendum paths are dirty: %s" % dirty1)
    if not os.path.exists(AC.RECEIPT_A1_PHASE_A):
        ref.append("A-5 TASK-20260923-4ff597 phase-A receipt absent: %s" % os.path.relpath(AC.RECEIPT_A1_PHASE_A, REPO))
    else:
        r1 = AC.load_json(AC.RECEIPT_A1_PHASE_A)
        info["a1_phase_a_commit"], info["a1_phase_a_commit_source"] = phase_a_commit(r1, AC.RECEIPT_A1_PHASE_A)
        bound = AC.receipt_paths(r1)
        bad = [p for p, h in bound.items() if not os.path.exists(os.path.join(REPO, p)) or AC.sha256_file(os.path.join(REPO, p)) != h]
        if bad:
            ref.append("A-5 addendum paths differ from the TASK-20260923-4ff597 phase-A receipt: %s" % bad)
        g_files = sorted(t for t in tr1 if t.startswith(AC.A1_PATHS_REL[0] + "/"))
        r_files = sorted(p for p in bound if p.startswith(AC.A1_PATHS_REL[0] + "/"))
        if g_files != r_files:
            ref.append("A-5 implementation-v2-a1/ file list differs between git and the phase-A receipt")
        for p_ in AC.A1_PATHS_REL[1:]:
            if p_ not in bound:
                ref.append("A-5 %s not bound by the TASK-20260923-4ff597 phase-A receipt" % p_)
    if pk is not None:
        # A-6
        if pk.get("gate_required"):
            for g in AC.V2_GATE_PACKAGES:
                r = _raw(g)
                if r is None:
                    ref.append("A-6 v2 gate package %s has not run" % g)
                elif r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
                    ref.append("A-6 v2 gate package %s did not pass: status %s gate_pass %s (AC-5)" % (g, r.get("run_status"), r.get("gate_pass")))
        if pk.get("controls_a1_gate_required"):
            cid = plan["gate"]["addendum_blocking_package"]
            r = _raw(cid)
            if r is None:
                ref.append("A-6 controls_a1 %s has not run" % cid)
            elif r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
                ref.append("A-6 controls_a1 %s did not pass: status %s gate_pass %s (A1-2 gates)" % (cid, r.get("run_status"), r.get("gate_pass")))
        # A-7
        for req in pk.get("requires", []):
            if _manifest(req) is None:
                ref.append("A-7 required earlier package %s (%s) has no manifest" % (req, by_id[req]["label"]))
    # A-8
    if plan.get("watchdogs") != v2plan.get("watchdogs"):
        ref.append("A-8 watchdog values differ from trial-plan-v2.json lines 95-177 (AC-6 uniformity)")
    # A-9
    others = V.other_solver_processes()
    if others:
        ref.append("A-9 another solver-like process is running (EC-10): %s" % others)
    # A-10
    exist_v2 = [i for i in v2_ids if os.path.exists(os.path.join(RUNS, i))]
    exist_a1 = [p["run_id"] for p in plan["packages"] if os.path.exists(os.path.join(RUNS, p["run_id"]))]
    info["existing_v2_dirs"], info["existing_a1_dirs"] = len(exist_v2), len(exist_a1)
    if len(exist_v2) + len(exist_a1) + 1 > AC.MAX_PACKAGES_SHARED:
        ref.append("A-10 shared ceiling: %d v2 + %d addendum run directories exist; one more exceeds 48 (DC-7 A-7; AA-5 (e)) -- an impediment for a new Coordinator decision"
                   % (len(exist_v2), len(exist_a1)))
    if len(exist_a1) + 1 > int(plan.get("package_count", 0)):
        ref.append("A-10 the addendum's own package count %s would be exceeded" % plan.get("package_count"))
    # A-11
    if pk is not None and pk["kind"] == "contingency":
        if not replaces:
            ref.append("A-11 a contingency package must name the package it replaces (--replaces)")
        elif replaces not in by_id or by_id[replaces]["kind"] == "contingency":
            ref.append("A-11 --replaces must name a planned, non-contingency ADDENDUM package (v2 packages use v2's own contingency ids)")
        else:
            tgt = by_id[replaces]
            if tgt.get("blocking"):
                ref.append("A-11 controls_a1 is the addendum's blocking gate and is never replaced (contingency_rule: never for a failed gate)")
            man = _manifest(replaces)
            if man is None:
                ref.append("A-11 replaced package has no manifest")
            elif man.get("failure_class") != "infrastructure_error":
                ref.append("A-11 only an infrastructure_error package may be replaced (never implementation_error, resource_exhaustion, "
                           "invalid_measurement or a result): %s is %s" % (replaces, man.get("failure_class")))
            for p2 in plan["packages"]:
                if p2["kind"] == "contingency" and p2["run_id"] != rid:
                    m2 = _manifest(p2["run_id"])
                    if m2 and (m2.get("package") or {}).get("replaces") == replaces:
                        ref.append("A-11 %s was already replaced once by %s" % (replaces, p2["run_id"]))
    elif replaces:
        ref.append("A-11 --replaces is only valid for an addendum contingency id")
    # A-12
    if plan.get("protocol_version") != AC.PROTOCOL_VERSION or (plan.get("addendum") or {}).get("id") != AC.ADDENDUM_ID \
            or (plan.get("addendum") or {}).get("sha256") != AC.ADDENDUM_SHA256 or plan.get("task_id") != AC.TASK_ID_RUNS:
        ref.append("A-12 the plan does not record protocol_version 2-a1, the addendum id/sha256 and TASK-20260923-6c7f55")
    if AC.FORBIDDEN_TASK_ID in json.dumps(plan):
        ref.append("A-12 the plan carries the forbidden task id (AA-5 (a))")
    info["plan"], info["v2plan"], info["pk"] = plan, v2plan, pk
    return ref, info


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


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if len(argv) not in (1, 3) or (len(argv) == 3 and argv[1] != "--replaces"):
        print("REFUSING (nothing written): usage: a1_run_wrapper.py RUN-ID [--replaces RUN-ID] [--dry-run]", file=sys.stderr)
        return 2
    rid = argv[0]
    replaces = argv[2] if len(argv) == 3 else None
    refusals, info = preflight(rid, replaces)
    if refusals:
        for r in refusals:
            print("REFUSING (nothing written): " + r, file=sys.stderr)
        return 2
    if dry:
        print("DRY RUN: every A-1..A-12 check passes for %s; nothing written" % rid)
        return 0
    plan, pk = info["plan"], info["pk"]
    by_id = {p["run_id"]: p for p in plan["packages"]}
    driver_args = pk.get("driver_args")
    if pk["kind"] == "contingency":
        tgt = by_id[replaces]
        driver_args = tgt["driver_args"]
        pk = dict(pk, replaces=replaces, replaced_label=tgt["label"], watchdogs=tgt.get("watchdogs"))
    rd = os.path.join(RUNS, rid)
    cmd = [sys.executable, "-B", DRIVER] + list(driver_args)
    os.makedirs(os.path.join(rd, "certificates"))
    tr, dirty = git_tree_state(AC.V2_PATHS_REL)
    tr1, dirty1 = git_tree_state(AC.A1_PATHS_REL)
    env_rec = {
        "operating_system": platform.platform(), "python_version": platform.python_version(),
        "host": __import__("v2_common").host_record(),
        "dependencies": {"msolve": V_sh("dpkg-query -W -f='${Version}' msolve"), "python_flint": V_sh("python3 -c 'import flint;print(flint.__version__)'"),
                         "numpy": V_sh("python3 -c 'import numpy;print(numpy.__version__)'"), "pyyaml": V_sh("python3 -c 'import yaml;print(yaml.__version__)'"),
                         "pari_gp": V_sh("gp --version-short 2>&1 | head -1"), "cypari2": V_sh("python3 -c 'import importlib.metadata as m;print(m.version(\"cypari2\"))'"),
                         "valgrind": V_sh("valgrind --version")},
        "git": {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
                "implementation_v2_last_commit": git("log", "-1", "--format=%H", "--", *AC.V2_PATHS_REL),
                "implementation_v2_a1_last_commit": git("log", "-1", "--format=%H", "--", *AC.A1_PATHS_REL),
                "implementation_v2_dirty_paths": dirty, "implementation_v2_a1_dirty_paths": dirty1,
                "repo_dirty_paths": git("status", "--porcelain").splitlines()},
        "phase_a_commits": {"TASK-20260923-0fa03f": info.get("v2_phase_a_commit"), "TASK-20260923-4ff597": info.get("a1_phase_a_commit"),
                            "sources": {"TASK-20260923-0fa03f": info.get("v2_phase_a_commit_source"),
                                        "TASK-20260923-4ff597": info.get("a1_phase_a_commit_source")}},
        "amendment_sha256": info["amendment_sha256"],
        "trial_plan_v2_a1_sha256": AC.sha256_file(AC.PLAN_A1_PATH), "trial_plan_v2_sha256": AC.sha256_file(AC.V2_PLAN_PATH),
        "ladder_json_sha256": AC.sha256_file(AC.LADDER_PATH),
    }
    json.dump(env_rec, open(os.path.join(rd, "environment.json"), "w"), indent=2)
    with open(os.path.join(rd, "command.txt"), "w") as fh:
        fh.write("# cwd: %s\n# GFPN_RUN_DIR=%s\n# PYTHONDONTWRITEBYTECODE=1\n%s\n" % (REPO, rd, " ".join(cmd)))
    child_env = dict(os.environ, GFPN_RUN_DIR=rd, GFPN_V2_PACKAGE=rid, GFPN_V2_REPLACES=replaces or "",
                     PYTHONHASHSEED="0", PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
    started = datetime.datetime.now(datetime.timezone.utc)
    t0 = time.time()
    with open(os.path.join(rd, "stdout.log"), "w") as so, open(os.path.join(rd, "stderr.log"), "w") as se:
        proc = subprocess.run(cmd, cwd=REPO, env=child_env, stdout=so, stderr=se)
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
            with open(os.path.join(rd, f), "w") as fh:
                yaml.safe_dump({"note": "driver produced no result; see stderr.log"}, fh)
    status = raw.get("run_status", "failed")
    fclass = raw.get("failure_class")
    if proc.returncode != 0 and status == "completed_valid":
        status, fclass = "failed", fclass or "infrastructure_error"
    caps = sorted({json.dumps(v, sort_keys=True) for v in collect(raw, "rlimit_as_child_getrlimit", []) if v})
    threads = sorted({v for v in collect(raw, "threads_executed", []) if v is not None})
    manifest = {"run": {
        "id": rid, "experiment_id": AC.EXPERIMENT_ID, "protocol_version": AC.PROTOCOL_VERSION,
        "addendum": {"id": AC.ADDENDUM_ID, "sha256": AC.ADDENDUM_SHA256, "approval_decision": AC.ADDENDUM_APPROVAL,
                     "conditions": ["AA-1", "AA-2", "AA-3", "AA-4", "AA-5", "AA-6", "AA-7", "AA-8"]},
        "amendment": {"id": AC.V2_AMENDMENT_ID, "sha256": AC.V2_AMENDMENT_SHA256, "approval_decision": AC.V2_APPROVAL,
                      "conditions": ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6"]},
        "task_id": AC.TASK_ID_RUNS, "hypothesis_id": "H-GFPN-9a29be", "heuristic_under_test": "HEUR-GFPN-DFLAT",
        "status": status, "failure_class": fclass, "claim_tier": "toy",
        "package": {k: pk.get(k) for k in ("order", "label", "kind", "blocking", "gate_required", "controls_a1_gate_required", "requires", "replaces", "replaced_label")},
        "code": {"commit": env_rec["git"]["head"],
                 "implementation_v2_last_commit": env_rec["git"]["implementation_v2_last_commit"],
                 "implementation_v2_a1_last_commit": env_rec["git"]["implementation_v2_a1_last_commit"],
                 "phase_a_commits": env_rec["phase_a_commits"],
                 "implementation_v2_clean": not dirty, "implementation_v2_a1_clean": not dirty1,
                 "command": " ".join(cmd), "wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py"},
        "inference": AC.inference_block(),
        "environment": {k: env_rec[k] for k in ("operating_system", "python_version", "dependencies")},
        "host": env_rec["host"],
        "inputs": {"seeds": raw.get("seeds"), "parameters": {k: raw.get(k) for k in ("p", "n", "m", "curve_shape", "field", "curve") if k in raw},
                   "trial_plan_v2_a1_sha256": env_rec["trial_plan_v2_a1_sha256"], "trial_plan_v2_sha256": env_rec["trial_plan_v2_sha256"],
                   "ladder_json_sha256": env_rec["ladder_json_sha256"]},
        "timing": {"started_at": started.isoformat(), "finished_at": finished.isoformat(), "wall_seconds": round(wall, 3)},
        "resources": {
            "child_rlimit_as_read_back_by_getrlimit": [json.loads(c) for c in caps],
            "child_rlimit_as_requested_bytes": (raw.get("envelope") or {}).get("cap_bytes"),
            "msolve_threads_executed": threads,
            "host_mem_total_kB": env_rec["host"]["mem_total_kB"], "host_swap_total_kB": env_rec["host"]["swap_total_kB"],
            "driver_and_children_maxrss_bytes_rusage": ru.ru_maxrss * 1024, "cpu_seconds_children": round(ru.ru_utime + ru.ru_stime, 3),
            "watchdogs_declared": {"package_scope": pk.get("watchdogs"), "values": plan["watchdogs"],
                                   "equal_to_trial_plan_v2": plan["watchdogs"] == info["v2plan"]["watchdogs"]},
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


def V_sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:                               # noqa: BLE001
        return "ERROR: %r" % (e,)


if __name__ == "__main__":
    sys.exit(main())
