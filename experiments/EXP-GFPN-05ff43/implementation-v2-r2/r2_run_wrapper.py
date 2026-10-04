#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r2 / 2-a1-r2 -- the r2 RUN WRAPPER (paristack PS-5 re-pointed to r2; solverevent SE-6,
SE-7 as incorporated; seedresolve SF-7; DEC-20260924-15a77a SC-1, SC-8, SC-10, SC-11). Started from
implementation-v2-r1/r1_run_wrapper.py.

usage: python3 -B r2_run_wrapper.py RUN-ID [--replaces RUN-ID] [--dry-run]

The command is NOT given on the command line: it is read from the package's entry in the committed r2 plan that
reserves RUN-ID (trial-plan-v2-r2.json or trial-plan-v2-a1-r2.json). Before ANY directory is created the wrapper
evaluates EVERY check below and REFUSES (exit 2, nothing written, every failing reason printed) unless all hold:
  R-1  FIVE hashes (SC-1): v2 amendment e02d4976...d3, v2-a1 addendum 2c5e0524...0c, paristack 856fdc1d...c7,
       seedresolve dc714a44...81, solverevent (incorporated) 011d4b2c...7f;
  R-2  RUN-ID is reserved in the r2 plan it belongs to and is none of: a v1 id, a v2 id, a v2-a1 id, an r1 id, or any
       of the 82 retired ids (the 40 earlier retired ids and the 42 r1 ids);
  R-3  runs/RUN-ID does not exist;
  R-4  implementation-v2/, implementation-v2.md, trial-plan-v2.json match the TASK-20260923-0fa03f phase-A receipt
       file by file, are tracked and clean, with no unbound file;
  R-5  the same for implementation-v2-a1/ (+ .md, plan) against the TASK-20260923-4ff597 phase-A receipt;
  R-6  the same for implementation-v2-r2/, implementation-v2-r2.md and both r2 plans against the
       TASK-20260924-689d2f phase-A receipt;
  R-7  the PS-4 gate_pass_rule for every gate_required repaired v2 package and every repaired addendum package
       (G1..G4 completed_valid with gate_pass true AND REG-1 (d-parsed) passed; addendum packages 2-11 also need the
       image of controls_a1 completed_valid with gate_pass true); REG-1 is evaluated before G2 and before every
       later package of either r2 plan;
  R-8  every package this one `requires` has a manifest;
  R-9  the plan's watchdogs object equals trial-plan-v2.json's exactly;
  R-10 no other solver-like process is running (v2_solver.other_solver_processes);
  R-11 the ceiling: existing run directories under any id of trial-plan-v2.json, trial-plan-v2-a1.json,
       trial-plan-v2-r1.json, trial-plan-v2-a1-r1.json, trial-plan-v2-r2.json and trial-plan-v2-a1-r2.json, plus one,
       <= 48; and the plan's own count + 1 <= its package_count;
  R-12 contingency_rule verbatim (trial-plan-v2.json line 185) within one r2 plan: --replaces names a planned,
       non-contingency, non-blocking package of the same plan whose manifest records failure_class
       infrastructure_error and that was not replaced before; never a gate package; never across plans;
  R-13 the plan records its protocol_version label, the seedresolve and paristack ids and sha256 and its run card;
       none of TASK-20260923-cd932c, TASK-20260923-6c7f55, TASK-20260923-3aa31e, TASK-20260923-292052 appears in it.
LAUNCH RULE: each package is launched directly through this wrapper, with no outer guard (no shell `timeout`, no
wrapper around the wrapper) that the plan does not declare (CORR-20260923-fb1be8 XD-2; SC-8).
SE-6: the driver child's environment carries PYTHONHASHSEED="0", exactly as v2_run_wrapper.py lines 177-178 and
a1_run_wrapper.py line 299 set it; the entry reads it back inside the driver process and the manifest records it.
Then it creates the directory, records command.txt and environment.json, runs the entry point with
PYTHONDONTWRITEBYTECODE=1, captures stdout.log / stderr.log, and writes manifest.yaml (with the `solver_events`
block, SC-11 (b)). It never invents a status. A package whose solver-events.json records an SE-2 (4) consistency
violation, and which wrote no raw-result.json, is recorded failed / implementation_error (SF-2 (b)).
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
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common as R                                    # noqa: E402

sys.path.insert(0, R.V2_DIR)
import yaml                                              # noqa: E402

import v2_solver as V                                    # noqa: E402  (other_solver_processes only)
import r2_reg1 as REG                                    # noqa: E402
import r2_resolve as RS                                  # noqa: E402  (constants and the SSF clause names only)

ENTRY_V2 = os.path.join(HERE, "r2_entry_v2.py")
ENTRY_A1 = os.path.join(HERE, "r2_entry_a1.py")
RUNS = R.RUNS_DIR                                        # module-level: redirected only in development checks
DRIVER_PYTHONHASHSEED = R.DRIVER_PYTHONHASHSEED          # SE-6 "0"; changed only in-process by a development check


def git(*args):
    return subprocess.run(["git", "-C", R.REPO] + list(args), capture_output=True, text=True).stdout.strip()


def git_tree_state(paths_rel):
    """(tracked files, dirty porcelain lines including untracked) for repo-relative paths."""
    return git("ls-files", "--", *paths_rel).splitlines(), git("status", "--porcelain", "--untracked-files=all", "--", *paths_rel).splitlines()


def disk_files(dir_rel):
    d = os.path.join(R.REPO, dir_rel)
    return sorted(os.path.relpath(os.path.join(dp, f), R.REPO) for dp, _dn, fn in os.walk(d) for f in fn)


def phase_a_commit(receipt_path):
    """receipt commit_sha if backfilled, else git log -1 of the receipt (CORR-20260923-fb1be8 XD-1)."""
    if not os.path.exists(receipt_path):
        return None, "receipt absent"
    rc = R.load_json(receipt_path)
    if rc.get("commit_sha"):
        return rc["commit_sha"], "receipt commit_sha (backfilled)"
    sha = git("log", "-1", "--format=%H", "--", os.path.relpath(receipt_path, R.REPO))
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


def tree_check(tag, paths_rel, receipt_path, receipt_label, ref):
    """R-4 / R-5 / R-6: receipt file-by-file, tracked and clean, no unbound file (git and disk)."""
    tr, dirty = git_tree_state(paths_rel)
    d0 = paths_rel[0]
    if not any(t.startswith(d0 + "/") for t in tr) or any(p not in tr for p in paths_rel[1:]):
        ref.append("%s %s are not all tracked by git" % (tag, ", ".join(paths_rel)))
    if dirty:
        ref.append("%s paths are dirty: %s" % (tag, dirty))
    if not os.path.exists(receipt_path):
        ref.append("%s %s receipt absent: %s" % (tag, receipt_label, os.path.relpath(receipt_path, R.REPO)))
        return tr, dirty
    bound = R.receipt_paths(R.load_json(receipt_path))
    bad = [p for p, h in bound.items() if (p == d0 or p.startswith(d0 + "/") or p in paths_rel)
           and (not os.path.exists(os.path.join(R.REPO, p)) or R.sha256_file(os.path.join(R.REPO, p)) != h)]
    if bad:
        ref.append("%s paths differ from the %s receipt: %s" % (tag, receipt_label, bad))
    rb = sorted(p for p in bound if p.startswith(d0 + "/"))
    if sorted(t for t in tr if t.startswith(d0 + "/")) != rb:
        ref.append("%s %s/ file list differs between git and the %s receipt" % (tag, d0, receipt_label))
    unbound_disk = sorted(set(disk_files(d0)) - set(rb))
    if unbound_disk:
        ref.append("%s files under %s/ not bound by the %s receipt: %s" % (tag, d0, receipt_label, unbound_disk))
    for p in paths_rel[1:]:
        if p not in bound:
            ref.append("%s %s not bound by the %s receipt" % (tag, p, receipt_label))
    return tr, dirty


def plans():
    return {"v2r2": R.load_json(R.PLAN_V2_R2), "a1r2": R.load_json(R.PLAN_A1_R2),
            "v2": R.load_json(R.PLAN_V2), "a1": R.load_json(R.PLAN_A1),
            "v2r1": R.load_json(R.PLAN_V2_R1), "a1r1": R.load_json(R.PLAN_A1_R1)}


def g1_id(P):
    return P["v2r2"]["gate"]["blocking_packages"][0]


def reg1(P):
    """Evaluate REG-1 (reference RUN-GFPN-ac4487 vs the r2 image G1; d-parsed). Returns the manifest block."""
    g1 = g1_id(P)
    cand = os.path.join(RUNS, g1)
    if not os.path.exists(os.path.join(cand, "raw-result.json")):
        return {"verdict": "NOT_EVALUABLE", "reason": "G1 %s has not run" % g1}
    ref = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN)
    rep = REG.compare(ref, cand)
    return {"verdict": rep["verdict"], "d_branch": R.REG1_D_BRANCH, "candidate": g1, "reference": R.REG1_REFERENCE_RUN,
            "exclusion_list_sha256": rep["exclusion_list_sha256"], "failures": rep["failures"], "output": REG.render(rep)}


def preflight(rid, replaces=None):
    """Evaluate every refusal. Returns (refusals, info). Writes nothing."""
    ref, info = [], {"rid": rid, "replaces": replaces}
    # R-1 (five hashes)
    info["amendment_sha256"] = {}
    for path, want in R.BOUND_HASHES:
        got = R.sha256_file(path) if os.path.exists(path) else None
        info["amendment_sha256"][os.path.basename(path)] = got
        if got != want:
            ref.append("R-1 %s sha256 %s != bound %s" % (os.path.basename(path), got, want))
    try:
        P = plans()
    except Exception as e:                               # noqa: BLE001
        return ref + ["R-2 a plan is unreadable: %r" % (e,)], info
    info["plans"] = P
    v2_frozen = {p["run_id"] for p in P["v2"]["packages"]}
    a1_frozen = {p["run_id"] for p in P["a1"]["packages"]}
    r1_ids = {p["run_id"] for p in P["v2r1"]["packages"]} | {p["run_id"] for p in P["a1r1"]["packages"]}
    v1 = set(P["v2"].get("v1_ids_never_reused", [])) | set(P["a1"].get("v1_ids_never_reused", []))
    which = "v2r2" if rid in {p["run_id"] for p in P["v2r2"]["packages"]} else (
        "a1r2" if rid in {p["run_id"] for p in P["a1r2"]["packages"]} else None)
    info["plan_key"] = which
    plan = P[which] if which else None
    by_id = {p["run_id"]: p for p in plan["packages"]} if plan else {}
    pk = by_id.get(rid)
    # R-2
    if rid in v1:
        ref.append("R-2 %s is a v1 run id" % rid)
    if rid in v2_frozen:
        ref.append("R-2 %s is a v2 run id (trial-plan-v2.json); retired or kept as a record, never run under the r2 wrapper" % rid)
    if rid in a1_frozen:
        ref.append("R-2 %s is a v2-a1 run id (trial-plan-v2-a1.json); retired, never run under the r2 wrapper" % rid)
    if rid in r1_ids:
        ref.append("R-2 %s is an r1 run id (trial-plan-v2-r1.json / trial-plan-v2-a1-r1.json); retired, never run" % rid)
    if rid in set(R.RETIRED_ALL):
        ref.append("R-2 %s is a retired run id (the 82 retired ids)" % rid)
    if pk is None:
        ref.append("R-2 %s is not reserved in trial-plan-v2-r2.json or trial-plan-v2-a1-r2.json" % rid)
    # R-3
    if os.path.exists(os.path.join(RUNS, rid)):
        ref.append("R-3 run directory exists (immutable): %s" % os.path.join(RUNS, rid))
    # R-4, R-5, R-6
    info["v2_tree"] = tree_check("R-4", R.V2_PATHS_REL, R.RECEIPT_V2_PHASE_A, "TASK-20260923-0fa03f phase-A", ref)
    info["a1_tree"] = tree_check("R-5", R.A1_PATHS_REL, R.RECEIPT_A1_PHASE_A, "TASK-20260923-4ff597 phase-A", ref)
    info["r2_tree"] = tree_check("R-6", R.R2_PATHS_REL, R.RECEIPT_R2_PHASE_A, "%s phase-A" % R.ARCHIVE_TASK, ref)
    info["reg1"] = None
    if pk is not None:
        # R-7
        gate_ids = P["v2r2"]["gate"]["blocking_packages"]
        need_gate = (which == "v2r2" and pk.get("gate_required")) or which == "a1r2"
        if need_gate:
            for g in gate_ids:
                r = _raw(g)
                if r is None:
                    ref.append("R-7 repaired gate package %s has not run" % g)
                elif r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
                    ref.append("R-7 repaired gate package %s did not pass: status %s gate_pass %s (PS-4)" % (g, r.get("run_status"), r.get("gate_pass")))
        if rid != gate_ids[0]:
            rg = reg1(P)
            info["reg1"] = rg
            if rg["verdict"] != "PASS":
                ref.append("R-7 REG-1 did not pass (%s): %s" % (rg["verdict"], rg.get("reason") or rg.get("failures")))
        if which == "a1r2" and pk.get("controls_a1_gate_required"):
            cid = plan["gate"]["addendum_blocking_package"]
            r = _raw(cid)
            if r is None:
                ref.append("R-7 controls_a1 image %s has not run" % cid)
            elif r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
                ref.append("R-7 controls_a1 image %s did not pass: status %s gate_pass %s" % (cid, r.get("run_status"), r.get("gate_pass")))
        # R-8
        for req in pk.get("requires", []):
            if _manifest(req) is None:
                ref.append("R-8 required earlier package %s (%s) has no manifest" % (req, by_id.get(req, {}).get("label")))
    # R-9
    if plan is not None and plan.get("watchdogs") != P["v2"].get("watchdogs"):
        ref.append("R-9 the plan's watchdogs differ from trial-plan-v2.json lines 95-177")
    # R-10
    others = V.other_solver_processes()
    if others:
        ref.append("R-10 another solver-like process is running (EC-10): %s" % others)
    # R-11 (six plans)
    all_ids = v2_frozen | a1_frozen | r1_ids | {p["run_id"] for p in P["v2r2"]["packages"]} | {p["run_id"] for p in P["a1r2"]["packages"]}
    existing = sorted(i for i in all_ids if os.path.exists(os.path.join(RUNS, i)))
    info["existing_dirs"] = existing
    if len(existing) + 1 > R.MAX_PACKAGES_SHARED:
        ref.append("R-11 ceiling: %d run directories exist under ids of the six plans; one more exceeds 48 -- an impediment for a new Coordinator decision" % len(existing))
    if plan is not None:
        own = [p["run_id"] for p in plan["packages"] if os.path.exists(os.path.join(RUNS, p["run_id"]))]
        if len(own) + 1 > int(plan.get("package_count", 0)):
            ref.append("R-11 the plan's own package_count %s would be exceeded" % plan.get("package_count"))
    # R-12
    if pk is not None and pk["kind"] == "contingency":
        if not replaces:
            ref.append("R-12 a contingency package must name the package it replaces (--replaces)")
        elif replaces not in by_id:
            ref.append("R-12 --replaces must name a package of the SAME r2 plan (never across plans): %s" % replaces)
        elif by_id[replaces]["kind"] == "contingency":
            ref.append("R-12 --replaces must name a planned, non-contingency package")
        else:
            tgt = by_id[replaces]
            if tgt.get("blocking"):
                ref.append("R-12 %s is a gate package and is never replaced (contingency_rule; PS-4)" % replaces)
            man = _manifest(replaces)
            if man is None:
                ref.append("R-12 replaced package has no manifest")
            elif man.get("failure_class") != "infrastructure_error":
                ref.append("R-12 only an infrastructure_error package may be replaced (never implementation_error, resource_exhaustion, "
                           "invalid_measurement or a result): %s is %s" % (replaces, man.get("failure_class")))
            for p2 in plan["packages"]:
                if p2["kind"] == "contingency" and p2["run_id"] != rid:
                    m2 = _manifest(p2["run_id"])
                    if m2 and (m2.get("package") or {}).get("replaces") == replaces:
                        ref.append("R-12 %s was already replaced once by %s" % (replaces, p2["run_id"]))
    elif replaces:
        ref.append("R-12 --replaces is only valid for a contingency id")
    # R-13
    if plan is not None:
        want_label, want_task = (R.PROTOCOL_V2_R2, R.TASK_RUNS_V2) if which == "v2r2" else (R.PROTOCOL_A1_R2, R.TASK_RUNS_A1)
        rp = plan.get("repair") or {}
        sr, ps = rp.get("seedresolve") or {}, rp.get("paristack") or {}
        if (plan.get("protocol_version") != want_label or sr.get("id") != R.SEEDRESOLVE_ID or sr.get("sha256") != R.SEEDRESOLVE_SHA256
                or ps.get("id") != R.PARISTACK_ID or ps.get("sha256") != R.PARISTACK_SHA256 or plan.get("task_id") != want_task):
            ref.append("R-13 the plan does not record protocol_version %s, the seedresolve and paristack ids/sha256 and run card %s" % (want_label, want_task))
        txt = json.dumps(plan)
        for f in R.FORBIDDEN_TASK_IDS:
            if f in txt:
                ref.append("R-13 the plan carries a forbidden task id")
    info["pk"], info["plan"] = pk, plan
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


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:                               # noqa: BLE001
        return "ERROR: %r" % (e,)


def inference_block():
    return {"requested_policy": "executor-implementation", "resolved_model_id": None,
            "resolved_by": "not recorded by the executor; the dispatching session records the resolved binding",
            "backend": os.environ.get("AUTORESEARCH_BACKEND"), "policy_env": os.environ.get("AUTORESEARCH_POLICY"),
            "fallback_used": False, "fallback_reason": None, "bedrock_used": False,
            "note": "every number in this package comes from deterministic code (msolve, python-flint, PARI, pure Python); no model is in the arithmetic loop"}


def watchdog_after_resolve(raw, events):
    """SF-2 (d): cells whose per-cell watchdog fired after a target with at least one re-solve."""
    resolved_tags = {e["tag"] for e in events if len(e.get("attempts") or []) >= 2}
    out = []
    for cell in (raw or {}).get("cells") or []:
        rows = cell.get("targets") or []
        fired = next((i for i, r in enumerate(rows) if r.get("status") == "not_attempted"
                      and str(r.get("reason", "")).startswith("per-cell watchdog")), None)
        if fired is None:
            continue
        before = ["%s_t%d" % (cell.get("arm"), r.get("target")) for r in rows[:fired] if r.get("target") is not None]
        hit = sorted(t for t in before if t in resolved_tags)
        if hit:
            out.append({"arm": cell.get("arm"), "m": cell.get("m"), "first_not_attempted_row": fired, "resolved_targets_before": hit})
    return out


def solver_events_block(rd, raw):
    """SC-11 (b) manifest block, recomputed from run-root solver-events.json."""
    p = os.path.join(rd, RS.EVENTS_FILE)
    if not os.path.exists(p):
        return {"status": "absent: the entry point wrote no solver-events.json", "K": R.K, "spacing_s": R.SPACING_S}
    try:
        doc = json.load(open(p))
    except Exception as e:                               # noqa: BLE001
        return {"status": "unparseable: %r" % (e,), "K": R.K, "spacing_s": R.SPACING_S, "sha256": R.sha256_file(p)}
    c = doc.get("counters") or {}
    ev = doc.get("events") or []
    return {"status": "present", "file": RS.EVENTS_FILE, "sha256": R.sha256_file(p), "K": doc.get("K"), "spacing_s": doc.get("spacing_s"),
            "cap_rule": doc.get("cap_rule"),
            "ssf_attempts_by_clause": c.get("ssf_attempts_by_clause"), "re_solves": c.get("re_solves"),
            "solves_with_ssf_attempt": c.get("solves_with_ssf_attempt"),
            "solves_still_ssf_after_last_attempt": c.get("solves_still_ssf_after_last_attempt"),
            "resolve_cap_reached": c.get("resolve_cap_reached"),
            "resolve_cap_reached_tags": [e["tag"] for e in ev if e.get("resolve_cap_reached")],
            "watchdog_after_resolve": watchdog_after_resolve(raw, ev),
            "wrapped_calls_gb_only_false": c.get("wrapped_calls_gb_only_false"), "attempts_total": c.get("attempts_total"),
            "passthrough_calls_gb_only_true": c.get("passthrough_calls_gb_only_true"),
            "consistency_violation": doc.get("consistency_violation"),
            "event_tags": [e.get("tag") for e in ev]}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if len(argv) not in (1, 3) or (len(argv) == 3 and argv[1] != "--replaces"):
        print("REFUSING (nothing written): usage: r2_run_wrapper.py RUN-ID [--replaces RUN-ID] [--dry-run]", file=sys.stderr)
        return 2
    rid = argv[0]
    replaces = argv[2] if len(argv) == 3 else None
    refusals, info = preflight(rid, replaces)
    if refusals:
        for r in refusals:
            print("REFUSING (nothing written): " + r, file=sys.stderr)
        return 2
    if dry:
        print("DRY RUN: every R-1..R-13 check passes for %s; nothing written" % rid)
        return 0
    return launch(rid, replaces, info)


def launch(rid, replaces, info):
    P, plan, pk, which = info["plans"], info["plan"], info["pk"], info["plan_key"]
    by_id = {p["run_id"]: p for p in plan["packages"]}
    driver_args = pk.get("driver_args")
    if pk["kind"] == "contingency":
        tgt = by_id[replaces]
        driver_args = tgt["driver_args"]
        pk = dict(pk, replaces=replaces, replaced_label=tgt["label"], watchdogs=tgt.get("watchdogs"))
    entry = ENTRY_V2 if which == "v2r2" else ENTRY_A1
    inv = {v: k for k, v in plan["id_map"].items()}
    rd = os.path.join(RUNS, rid)
    cmd = [sys.executable, "-B", entry] + list(driver_args)
    os.makedirs(os.path.join(rd, "certificates"))
    import v2_common as C                                # host_record only (unchanged v2 code)
    trees = {k: git_tree_state(p) for k, p in (("v2", R.V2_PATHS_REL), ("a1", R.A1_PATHS_REL), ("r2", R.R2_PATHS_REL))}
    rec_0fa03f, src_0fa03f = phase_a_commit(R.RECEIPT_V2_PHASE_A)
    rec_4ff597, src_4ff597 = phase_a_commit(R.RECEIPT_A1_PHASE_A)
    c689, src_689 = phase_a_commit(R.RECEIPT_R2_PHASE_A)
    pac = {"TASK-20260923-0fa03f": R.PHASE_A_COMMIT_0FA03F, R.ARCHIVE_TASK: c689,
           "sources": {"TASK-20260923-0fa03f": "literal (PS-5; CORR-20260923-fb1be8 XD-1); receipt reading %s via %s" % (rec_0fa03f, src_0fa03f),
                       R.ARCHIVE_TASK: "read from its phase-A receipt at run time: %s" % src_689}}
    if which == "a1r2":
        pac["TASK-20260923-4ff597"] = R.PHASE_A_COMMIT_4FF597
        pac["sources"]["TASK-20260923-4ff597"] = "literal (PS-5); receipt reading %s via %s" % (rec_4ff597, src_4ff597)
    env_rec = {
        "operating_system": platform.platform(), "python_version": platform.python_version(), "host": C.host_record(),
        "dependencies": {"msolve": sh("dpkg-query -W -f='${Version}' msolve"), "python_flint": sh("python3 -c 'import flint;print(flint.__version__)'"),
                         "numpy": sh("python3 -c 'import numpy;print(numpy.__version__)'"), "pyyaml": sh("python3 -c 'import yaml;print(yaml.__version__)'"),
                         "pari_gp": sh("gp --version-short 2>&1 | head -1"),
                         "cypari2": sh("python3 -c 'import importlib.metadata as m;print(m.version(\"cypari2\"))'"),
                         "valgrind": sh("valgrind --version"), "sage_python": C.SAGE_PYTHON},
        "PYTHONHASHSEED_set_for_driver": DRIVER_PYTHONHASHSEED,
        "git": {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
                "implementation_v2_last_commit": git("log", "-1", "--format=%H", "--", *R.V2_PATHS_REL),
                "implementation_v2_a1_last_commit": git("log", "-1", "--format=%H", "--", *R.A1_PATHS_REL),
                "implementation_v2_r2_last_commit": git("log", "-1", "--format=%H", "--", *R.R2_PATHS_REL),
                "dirty_paths": {k: v[1] for k, v in trees.items()}, "repo_dirty_paths": git("status", "--porcelain").splitlines()},
        "phase_a_commits": pac,
        "amendment_sha256": info["amendment_sha256"],
        "plan_sha256": {os.path.basename(p): R.sha256_file(p) for p in (R.PLAN_V2_R2, R.PLAN_A1_R2, R.PLAN_V2, R.PLAN_A1)},
        "ladder_json_sha256": R.sha256_file(R.LADDER_PATH),
    }
    with open(os.path.join(rd, "environment.json"), "w") as fh:
        json.dump(env_rec, fh, indent=2)
    with open(os.path.join(rd, "command.txt"), "w") as fh:
        fh.write("# cwd: %s\n# GFPN_RUN_DIR=%s\n# PYTHONDONTWRITEBYTECODE=1\n# PYTHONHASHSEED=%s (SE-6)\n# launched by: python3 -B %s %s%s (no outer guard)\n%s\n"
                 % (R.REPO, rd, DRIVER_PYTHONHASHSEED, os.path.relpath(os.path.abspath(__file__), R.REPO), rid,
                    (" --replaces " + replaces) if replaces else "", " ".join(cmd)))
    child_env = dict(os.environ, GFPN_RUN_DIR=rd, GFPN_V2_PACKAGE=rid, GFPN_V2_REPLACES=replaces or "",
                     PYTHONHASHSEED=DRIVER_PYTHONHASHSEED, PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
    started = datetime.datetime.now(datetime.timezone.utc)
    t0 = time.time()
    with open(os.path.join(rd, "stdout.log"), "w") as so, open(os.path.join(rd, "stderr.log"), "w") as se:
        proc = subprocess.run(cmd, cwd=R.REPO, env=child_env, stdout=so, stderr=se)
    wall = time.time() - t0
    finished = datetime.datetime.now(datetime.timezone.utc)
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    ps_path = os.path.join(rd, "pari-stack.json")
    pstack = json.load(open(ps_path)) if os.path.exists(ps_path) else None
    raw_path = os.path.join(rd, "raw-result.json")
    raw = None
    if os.path.exists(raw_path):
        try:
            raw = json.load(open(raw_path))
        except Exception as e:                           # noqa: BLE001
            raw = {"run_status": "failed", "failure_class": "implementation_error", "note": "raw-result.json unparseable: %r" % (e,)}
    sev_pre = None
    try:
        sev_pre = json.load(open(os.path.join(rd, RS.EVENTS_FILE)))
    except Exception:                                    # noqa: BLE001
        pass
    if raw is None:
        note = "driver exited %s without writing raw-result.json" % proc.returncode
        fclass = "infrastructure_error"
        if pstack and pstack.get("status") == "refused_before_any_command":
            note = "the entry point refused before any command (PARI stack, redirection or SE-3 read-back): %s" % pstack.get("refusal_reasons")
        elif sev_pre and sev_pre.get("consistency_violation"):
            fclass = "implementation_error"
            note = ("the r2 re-solve layer raised on an SE-2 (4) / SF-2 (b) consistency violation (solver-events.json); the package "
                    "ends failed as implementation_error and is never a result")
        raw = {"run_status": "failed", "failure_class": fclass, "note": note}
        with open(raw_path, "w") as fh:
            json.dump(raw, fh, indent=2)
        for f in ("ladder-table.yaml", "heur-dflat.yaml", "cost-band-p64.yaml"):
            with open(os.path.join(rd, f), "w") as fh:
                yaml.safe_dump({"note": "driver produced no result; see stderr.log"}, fh)
    status = raw.get("run_status", "failed")
    fclass = raw.get("failure_class")
    if proc.returncode != 0 and status == "completed_valid":
        status, fclass = "failed", fclass or "infrastructure_error"
    caps = sorted({json.dumps(v, sort_keys=True) for v in collect(raw, "rlimit_as_child_getrlimit", []) if v})
    threads = sorted({v for v in collect(raw, "threads_executed", []) if v is not None})
    wd_equal = plan["watchdogs"] == P["v2"]["watchdogs"]
    sev = solver_events_block(rd, raw)
    hs = (pstack or {}).get("python_hash_seed_driver_readback")
    man = {"run": {
        "id": rid, "experiment_id": R.EXPERIMENT_ID, "protocol_version": R.PROTOCOL_V2_R2 if which == "v2r2" else R.PROTOCOL_A1_R2,
        "amendment": {"id": R.V2_AMENDMENT_ID, "sha256": R.V2_AMENDMENT_SHA256, "approval_decision": R.V2_APPROVAL,
                      "conditions": ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6"]},
    }}
    run = man["run"]
    if which == "a1r2":
        run["addendum"] = {"id": R.A1_ADDENDUM_ID, "sha256": R.A1_ADDENDUM_SHA256, "approval_decision": R.A1_APPROVAL,
                           "conditions": ["AA-1", "AA-2", "AA-3", "AA-4", "AA-5", "AA-6", "AA-7", "AA-8"]}
    run["repair"] = {"paristack": {"id": R.PARISTACK_ID, "sha256": R.PARISTACK_SHA256, "approval_decision": R.PARISTACK_APPROVAL,
                                   "conditions": R.PARISTACK_CONDITIONS},
                     "seedresolve": {"id": R.SEEDRESOLVE_ID, "sha256": R.SEEDRESOLVE_SHA256, "approval_decision": R.SEEDRESOLVE_APPROVAL,
                                     "conditions": R.SEEDRESOLVE_CONDITIONS, "correction": R.SEEDRESOLVE_CORRECTION},
                     "solverevent": {"id": R.SOLVEREVENT_ID, "sha256": R.SOLVEREVENT_SHA256, "standing": R.SOLVEREVENT_STANDING}}
    run.update({
        "task_id": plan["task_id"], "hypothesis_id": R.HYPOTHESIS_ID, "heuristic_under_test": R.HEURISTIC_ID,
        "status": status, "failure_class": fclass, "claim_tier": "toy",
        "derived_from": inv.get(rid),
        "package": {k: pk.get(k) for k in ("order", "label", "kind", "blocking", "gate_required", "controls_a1_gate_required",
                                            "requires", "replaces", "replaced_label")},
        "code": {"commit": env_rec["git"]["head"],
                 "implementation_v2_last_commit": env_rec["git"]["implementation_v2_last_commit"],
                 "implementation_v2_a1_last_commit": env_rec["git"]["implementation_v2_a1_last_commit"],
                 "implementation_v2_r2_last_commit": env_rec["git"]["implementation_v2_r2_last_commit"],
                 "phase_a_commits": pac,
                 "implementation_v2_clean": not trees["v2"][1], "implementation_v2_a1_clean": not trees["a1"][1],
                 "implementation_v2_r2_clean": not trees["r2"][1],
                 "command": " ".join(cmd), "entry_point": os.path.relpath(entry, R.REPO),
                 "wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_run_wrapper.py"},
        "inference": inference_block(),
        "environment": {"operating_system": env_rec["operating_system"], "python_version": env_rec["python_version"],
                        "dependencies": env_rec["dependencies"], "PYTHONHASHSEED_set_for_driver": DRIVER_PYTHONHASHSEED,
                        "PYTHONHASHSEED_driver_readback": hs},
        "host": env_rec["host"],
        "inputs": {"seeds": raw.get("seeds"), "parameters": {k: raw.get(k) for k in ("p", "n", "m", "curve_shape", "field", "curve") if k in raw},
                   "plan_sha256": env_rec["plan_sha256"], "ladder_json_sha256": env_rec["ladder_json_sha256"], "data_source": raw.get("data_source")},
        "timing": {"started_at": started.isoformat(), "finished_at": finished.isoformat(), "wall_seconds": round(wall, 3)},
        "resources": {
            "child_rlimit_as_read_back_by_getrlimit": [json.loads(c) for c in caps],
            "child_rlimit_as_requested_bytes": (raw.get("envelope") or {}).get("cap_bytes"),
            "msolve_threads_executed": threads,
            "host_mem_total_kB": env_rec["host"]["mem_total_kB"], "host_swap_total_kB": env_rec["host"]["swap_total_kB"],
            "driver_and_children_maxrss_bytes_rusage": ru.ru_maxrss * 1024, "cpu_seconds_children": round(ru.ru_utime + ru.ru_stime, 3),
            "watchdogs_declared": {"package_scope": pk.get("watchdogs"), "values": plan["watchdogs"], "equal_to_trial_plan_v2": wd_equal},
            "pari_stack": pstack if pstack is not None else {"status": "absent: the entry point wrote no pari-stack.json"},
            "note": "the cap recorded is the value each child read back with getrlimit after setting it (DC-6 R-1), never a wrapper default"},
        "solver_events": sev,
        "result": {"metrics": raw.get("metrics", {}), "valid": status == "completed_valid", "gate_pass": raw.get("gate_pass"),
                   "exit_code": proc.returncode, "certificate": raw.get("certificate") or {"kind": "none", "verified": None, "verifier": None},
                   "F3": "undecidable (AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii DC-4)"},
        "artifacts": {"raw_result": "raw-result.json", "ladder_table": "ladder-table.yaml", "heur_dflat": "heur-dflat.yaml",
                      "cost_band_p64": "cost-band-p64.yaml", "certificates_dir": "certificates/", "stdout": "stdout.log", "stderr": "stderr.log",
                      "solver_inputs": "solver/ (R-10)", "pari_stack": "pari-stack.json", "solver_events": RS.EVENTS_FILE},
    })
    if info.get("reg1") is not None:
        run["gate"] = {"regression_REG-1": info["reg1"]}
    with open(os.path.join(rd, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(man, fh, sort_keys=False, width=110)   # never altered: a forbidden id is caught by r2_check_run
    print("%s: status=%s wall=%.1fs exit=%s dir=%s" % (rid, status, wall, proc.returncode, rd))
    return 0


if __name__ == "__main__":
    sys.exit(main())
