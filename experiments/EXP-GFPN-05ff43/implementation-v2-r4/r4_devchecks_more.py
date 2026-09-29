#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r4 stage (TASK-20260924-d91a96) -- development checks DV-1 (static part and the child-side probe),
DV-5, DV-8, DV-9 (SC-6), DV-10, DV-11 (static launch list with the CC-1 dispositions, the dynamic counts of the DV-7 toy
lineage, the VC-3 consumer inventory of r4_inventory.py) and DV-15 (SC-3), re-pointed to r4 by DEC-20260924-daf670
LKA-3, LKA-11 (a). Called through r4_devchecks.py; development only; outputs under --out (the session scratchpad).
Started from implementation-v2-r3/r3_devchecks_more.py.
"""
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r4_common as R                                    # noqa: E402

TOK = re.compile(r"RUN-GFPN-[0-9a-f]{6}")
READABLE_RUNS = ("RUN-GFPN-ac4487", "RUN-GFPN-3377f1", "RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956")


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def git_env():
    return dict(os.environ, GIT_OPTIONAL_LOCKS="0")


# ============================================================================ DV-1 static inventory + child probe
def dv1_static(out, rest):
    """Static search of implementation-v2/, implementation-v2-a1/ and the r4 layer for PARI uses, the call graph from
    each driver command to them, a NO-COMPUTATION start-up probe of the Sage child's PARI stack (capped child launched
    through the DELIVERED r4 launch recorder), the gp child's configuration (read from the code), and
    callgrind_annotate's resolved path and version (CC-8 (e))."""
    os.makedirs(out, exist_ok=True)
    pat = re.compile(r"cypari2|\bpari\b|ellcard|allocatemem|parisize|/usr/bin/gp|\bgp\b|sage", re.I)
    hits = []
    for d in (R.V2_DIR, R.A1_DIR, HERE):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py"):
                continue
            for i, line in enumerate(open(os.path.join(d, f)), 1):
                if pat.search(line):
                    hits.append({"file": os.path.relpath(os.path.join(d, f), R.REPO), "line": i, "text": line.rstrip()[:200]})
    comparator = os.path.join(R.REPO, "coordination", "goals", "GOAL-GFPN-380702", "reviews", "TASK-20260923-58953e", "scratch", "k4a_anchor_system.py")
    comp_hits = [{"line": i, "text": line.rstrip()[:200]} for i, line in enumerate(open(comparator), 1)
                 if re.search(r"pari|GF\(|allocatemem|parisize|import|alarm", line)]
    graph = {
        "v2 fixture": "v2_driver.main -> cmd_fixture (275) -> fixture_core (284) -> C.curve_order_pari (308) [IN-PROCESS cypari2] at (4111, n = 3) and (16777291, n = 3)",
        "v2 controls": "v2_driver.main -> cmd_controls (752) -> C.fixture_n3(4111) (764) -> C.curve_order_pari (771) [IN-PROCESS cypari2] at (4111, n = 3)",
        "v2 fixture4": "v2_driver.main -> cmd_fixture4 (526) -> C.fixture_n4 -> C.curve_order_pari (542) [IN-PROCESS cypari2] at (4111, n = 4)",
        "v2 anchor-identity": "v2_driver.main -> cmd_anchor_identity (628) -> V.run_child(SAGE_PYTHON, COMPARATOR) (650) [CHILD: Sage, PARI-backed GF(p^5); library-default stack; FLAGGED, DEC-20260924-bea197 R-5]",
        "v2 build": "v2_driver.main -> cmd_build (935): builders in capped v2_child.py children (flint/numpy); ladder orders from ladder.json; no PARI",
        "v2 cells": "v2_driver.main -> cmd_cells (1016): orders from ladder.json; msolve children; no PARI",
        "v2 aggregate": "v2_driver.main -> cmd_aggregate (1248): reads raw-result.json files; no PARI",
        "a1 controls-a1": "a1_driver.main -> cmd_controls_a1 (56) -> P.curve_facts (89) -> V.run_child(/usr/bin/gp) [CHILD: gp, parisize 256000000 / parisizemax 4000000000 set in the script, a1_pari.py line 38; no random seed set (CG-9 (f))]",
        "a1 build": "a1_driver.cmd_build (219) -> v2_driver.cmd_build; no PARI",
        "a1 cells": "a1_driver.cmd_cells (228) -> v2_driver.cmd_cells; no PARI",
        "a1 aggregate-a1": "a1_driver.cmd_aggregate_a1 (276): reads raw-result.json files; no PARI",
        "r4 layer": "r4_common.PariStack: cypari2.Pari() constructions, allocatemem and default read-backs only; no computation. r4_recorder: no PARI",
        "callgrind_annotate (S-3)": "v2_solver.callgrind_instructions (533): subprocess.run(['callgrind_annotate', ...]) (PATH lookup; uncapped; 600 s timeout); no PARI",
    }
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C
    import r4_devchecks as DC
    REC = DC.recorder_in_this_process(os.path.join(out, "recorder_rundir"))
    probe = os.path.join(out, "sage_pari_probe.py")
    with open(probe, "w") as fh:
        fh.write("from sage.all import *\nfrom sage.libs.pari import pari\n"
                 "print('R4PROBE parisize', int(pari.default('parisize')))\nprint('R4PROBE parisizemax', int(pari.default('parisizemax')))\n"
                 "print('R4PROBE stacksize', int(pari.stacksize()))\nprint('R4PROBE stacksizemax', int(pari.stacksizemax()))\n"
                 "import sage.version; print('R4PROBE sage_version', sage.version.version)\n")
    so, se = os.path.join(out, "sage_pari_probe.stdout"), os.path.join(out, "sage_pari_probe.stderr")
    rec = REC.launch_recorder([C.SAGE_PYTHON, probe], so, se, cap_bytes=R.CAP_BYTES, timeout_s=3600, count_instructions=False)
    vals = {}
    for line in open(so, errors="replace"):
        if line.startswith("R4PROBE "):
            k, v = line.split()[1], line.split()[2]
            vals[k] = v
    ffc = glob.glob(os.path.join(os.path.dirname(os.path.dirname(C.SAGE_PYTHON)), "lib", "python3*", "site-packages", "sage", "rings", "finite_rings", "finite_field_constructor.py"))
    impl = []
    if ffc:
        for i, line in enumerate(open(ffc[0]), 1):
            if re.search(r"impl = |order < zech_log_bound|pari_ffelt|givaro", line):
                impl.append({"line": i, "text": line.rstrip()[:160]})
    ca_path = shutil.which("callgrind_annotate")
    ca_run = subprocess.run(["callgrind_annotate", "--version"], capture_output=True, text=True) if ca_path else None
    ca_ver = ((ca_run.stdout or "") + (ca_run.stderr or "")).strip() if ca_run else None     # it prints its version on stderr
    vg_path = shutil.which("valgrind")
    vg_ver = subprocess.run(["valgrind", "--version"], capture_output=True, text=True).stdout.strip() if vg_path else None
    ms_path = shutil.which("msolve")
    gp_path = shutil.which("gp")
    gp_ver = subprocess.run(["gp", "--version-short"], capture_output=True, text=True).stdout.strip() if gp_path else None
    dpkg = subprocess.run(["dpkg-query", "-W", "-f=${Package} ${Version}\n", "msolve", "valgrind", "pari-gp"], capture_output=True, text=True).stdout.splitlines()
    a1p = open(os.path.join(R.A1_DIR, "a1_pari.py")).read().splitlines()
    rep = {"static_hits": hits, "comparator_hits": comp_hits, "call_graph": graph,
           "sage_child_probe": {"script": open(probe).read(), "child": {k: rec.get(k) for k in ("outcome", "returncode", "rlimit_as_child_getrlimit", "rlimit_as_proc_limits_after_exec", "wall_seconds")},
                                "values": vals, "stderr_tail": open(se, errors="replace").read().splitlines()[-10:],
                                "launched_through": "the delivered r4 launch recorder (r4_recorder.launch_recorder) installed over the frozen run_child"},
           "sage_finite_field_constructor": {"file": os.path.relpath(ffc[0], os.path.dirname(os.path.dirname(os.path.dirname(C.SAGE_PYTHON)))) if ffc else None, "lines": impl[:40]},
           "gp_child_configuration_from_code": {"a1_pari.py line 38": a1p[37] if len(a1p) >= 38 else None, "gp_path": gp_path, "gp_version": gp_ver},
           "toolchain": {"callgrind_annotate_path": ca_path, "callgrind_annotate_version": ca_ver, "valgrind_path": vg_path, "valgrind_version": vg_ver,
                         "msolve_path": ms_path, "gp_path": gp_path, "dpkg": dpkg,
                         "subprocess_argv": [["callgrind_annotate", "--version"], ["valgrind", "--version"], ["gp", "--version-short"],
                                             ["dpkg-query", "-W", "-f=${Package} ${Version}\\n", "msolve", "valgrind", "pari-gp"]],
                         "note": "CC-8 (e): RUN-GFPN-ac4487's environment.json records valgrind-3.22.0 and msolve 0.6.5-1build2 and has no callgrind_annotate entry"}}
    dump(os.path.join(out, "dv1_static.json"), rep)
    print("DV-1 static: %d PARI-related lines in v2/v2-a1/layer; Sage probe %s %s getrlimit %s; callgrind_annotate %s %s; valgrind %s %s; msolve %s; gp %s %s"
          % (len(hits), rec.get("outcome"), vals, rec.get("rlimit_as_child_getrlimit"), ca_path, ca_ver, vg_path, vg_ver, ms_path, gp_path, gp_ver))
    return 0


# ============================================================================ DV-5 plan derivation (own code path)
def md_declared_keys():
    """Read the declared key paths back from implementation-v2-r4.md (the RC-4 (b) record), independently."""
    txt = open(os.path.join(R.EXP_DIR, "implementation-v2-r4.md")).read()
    sec = txt.split("## RC-4 (a)")[0].split("## RC-4 (b)")[1]
    v2part, a1part = sec.split("`trial-plan-v2-a1-r4.json` (13 paths):")
    grab = lambda s: re.findall(r"^\| `(/[^`]+)` \|", s, re.M)   # noqa: E731
    return grab(v2part), grab(a1part)


def dv5_equal(r4plan, frozen, declared, inverse):
    """RC-4 (c) with DV-5's OWN implementation: pointer deletion by path walking, inverse mapping by a character
    scanner (no regex substitution, no writer function)."""
    def walk_delete(o, parts):
        if len(parts) == 1:
            if isinstance(o, dict):
                o.pop(parts[0], None)
            return
        if isinstance(o, dict) and parts[0] in o:
            walk_delete(o[parts[0]], parts[1:])

    def unmap(s):
        out, i, L = [], 0, len("RUN-GFPN-") + 6
        while i < len(s):
            j = s.find("RUN-GFPN-", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            tok = s[j:j + L]
            ok_tok = len(tok) == L and all(c in "0123456789abcdef" for c in tok[9:])
            out.append(inverse.get(tok, tok) if ok_tok else tok)
            i = j + L
        return "".join(out)

    def rec(o):
        if isinstance(o, dict):
            return {k: rec(v) for k, v in o.items()}
        if isinstance(o, list):
            return [rec(v) for v in o]
        return unmap(o) if isinstance(o, str) else o
    r, f = json.loads(json.dumps(r4plan)), json.loads(json.dumps(frozen))
    for ptr in declared:
        parts = ptr.strip("/").split("/")
        walk_delete(r, parts)
        walk_delete(f, parts)
    a = json.dumps(rec(r), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    b = json.dumps(f, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return a == b, hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest()


def strings_with_paths(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from strings_with_paths(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings_with_paths(v, path + "/%d" % i)
    elif isinstance(o, str):
        yield path, o


def lka1_repair_ok(rp):
    """LKA-1: the repair block names the seventeen with sha256 and standing (reanchor e788a1, rung31 8b2dbf, paristack
    80e280, seedresolve 15a77a, valueclose e52eec, launchkind daf670; the other nine "incorporated by reference, never
    approved"); RB-1..RB-8, RL-1..RL-8, RK-1..RK-7, RF-0..RF-8, RG-1..RG-9, RH-1..RH-8, RI-1..RI-6, RJ-1..RJ-8; LKA-1..LKA-15;
    and the VA-1 content (K = 5; spacing 2 s; the SF-2 (c) / HR-6 cap; REG-1 (d) d-parsed; the three sites with their
    CC-1 dispositions; the PS-1 branch; R = 10; V-1..V-7, K-1..K-6 and the classes)."""
    a = rp.get("amendments") or {}
    nv = "incorporated by reference, never approved"
    approved = {"paristack": "DEC-20260923-80e280", "seedresolve": "DEC-20260924-15a77a", "valueclose": "DEC-20260924-e52eec",
                "launchkind": "DEC-20260924-daf670"}
    want_sha = dict((os.path.basename(p), h) for p, h in R.BOUND_HASHES)
    files = {"paristack": "v2_addendum_paristack.yaml", "seedresolve": "v2_addendum_seedresolve.yaml", "solverevent": "v2_addendum_solverevent.yaml",
             "healthresolve": "v2_addendum_healthresolve.yaml", "launchcover": "v2_addendum_launchcover.yaml", "consumercover": "v2_addendum_consumercover.yaml",
             "valueclose": "v2_addendum_valueclose.yaml", "readbackcover": "v2_addendum_readbackcover.yaml", "readbackfull": "v2_addendum_readbackfull.yaml",
             "readbackclose": "v2_addendum_readbackclose.yaml", "failclosed": "v2_addendum_failclosed.yaml", "childend": "v2_addendum_childend.yaml",
             "gapattr": "v2_addendum_gapattr.yaml", "attcount": "v2_addendum_attcount.yaml", "launchkind": "v2_addendum_launchkind.yaml"}
    c = {}
    for k, f in files.items():
        b = a.get(k) or {}
        c["amendment_%s" % k] = b.get("sha256") == want_sha[f] and ((b.get("approval_decision") == approved[k]) if k in approved else (b.get("standing") == nv))
    c["seventeen_hashes"] = rp.get("bound_hashes_seventeen") == {os.path.relpath(p, R.REPO): h for p, h in R.BOUND_HASHES} and len(rp.get("bound_hashes_seventeen") or {}) == 17
    c["reanchor_and_rung31_in_the_seventeen"] = ("experiments/EXP-GFPN-05ff43/amendments/v1_to_v2_reanchor_and_arm_iii.yaml" in (rp.get("bound_hashes_seventeen") or {})
                                                 and "experiments/EXP-GFPN-05ff43/amendments/v2_addendum_rung31.yaml" in (rp.get("bound_hashes_seventeen") or {}))
    rules = rp.get("rules") or {}
    c["rules_RB_RL_RK_RF_RG_RH_RI_RJ"] = (rules.get("RB") == ["RB-%d" % i for i in range(1, 9)] and rules.get("RL") == ["RL-%d" % i for i in range(1, 9)]
                                          and rules.get("RK") == ["RK-%d" % i for i in range(1, 8)] and rules.get("RF") == ["RF-%d" % i for i in range(0, 9)]
                                          and rules.get("RG") == ["RG-%d" % i for i in range(1, 10)] and rules.get("RH") == ["RH-%d" % i for i in range(1, 9)]
                                          and rules.get("RI") == ["RI-%d" % i for i in range(1, 7)] and rules.get("RJ") == ["RJ-%d" % i for i in range(1, 9)])
    c["LKA_1_to_15"] = (rp.get("approval") or {}).get("conditions") == ["LKA-%d" % i for i in range(1, 16)] and (rp.get("approval") or {}).get("decision") == "DEC-20260924-daf670"
    c["K_5"] = rp.get("K") == 5
    c["spacing_2s"] = rp.get("spacing_s") == 2.0
    c["cap_SF2c_with_HR6"] = "SF-2 (c)" in str(rp.get("resolve_cap")) and "HR-6" in str(rp.get("resolve_cap")) and "DEV_TIMEOUT_S" in str(rp.get("resolve_cap"))
    c["d_parsed"] = rp.get("reg1_d_branch") == "d-parsed"
    c["ps1_branch"] = rp.get("ps1_branch") == "P-A"
    c["R_10"] = rp.get("dv17_R") == 10
    c["three_sites_with_dispositions"] = (sorted((rp.get("sites") or {}).keys()) == sorted([R.SITE_S1, R.SITE_S2, R.SITE_S3])
                                          and all((rp["sites"][k] or {}).get("disposition") for k in rp["sites"]))
    c["value_table_V1_V7"] = sorted(((rp.get("value_table") or {}).get("values") or {}).keys()) == ["V-%d" % i for i in range(1, 8)]
    c["value_table_K1_K6"] = sorted(((rp.get("value_table") or {}).get("rows") or {}).keys()) == ["K-%d" % i for i in range(1, 7)]
    c["classes"] = sorted(((rp.get("value_table") or {}).get("classes") or {}).keys()) == sorted(["alpha", "beta", "frozen-body", "gamma", "epsilon"])
    c["corrections_17"] = rp.get("corrections") == R.CORRECTIONS and len(R.CORRECTIONS) == 17
    c["launch_kinds_six"] = sorted((rp.get("launch_kinds_RJ-4") or {}).keys()) == ["LK-%d" % i for i in range(1, 7)]
    return c


def dv5(out, rest):
    """rest: --dv2 PATH --dv3 PATH (passed to the writer's --check)."""
    os.makedirs(out, exist_ok=True)
    rep, ok = {"plans": {}}, True
    v2, a1 = R.load_json(R.PLAN_V2), R.load_json(R.PLAN_A1)
    v2r4, a1r4 = R.load_json(R.PLAN_V2_R4), R.load_json(R.PLAN_A1_R4)
    old_plans = [R.load_json(p) for p in (R.PLAN_V2_R1, R.PLAN_A1_R1, R.PLAN_V2_R2, R.PLAN_A1_R2, R.PLAN_V2_R3, R.PLAN_A1_R3)]
    rep["frozen_sha256"] = {"trial-plan-v2.json": sha(R.PLAN_V2), "trial-plan-v2-a1.json": sha(R.PLAN_A1)}
    ok &= rep["frozen_sha256"] == {"trial-plan-v2.json": R.PLAN_V2_SHA256, "trial-plan-v2-a1.json": R.PLAN_A1_SHA256}
    M = dict(v2r4["id_map"], **a1r4["id_map"])
    inverse = {v: k for k, v in M.items()}
    v1 = set(v2["v1_ids_never_reused"]) | set(a1["v1_ids_never_reused"])
    fv2, fa1 = [p["run_id"] for p in v2["packages"]], [p["run_id"] for p in a1["packages"]]
    old_ids = [p["run_id"] for pl in old_plans for p in pl["packages"]]
    rep["M"] = {"entries": len(M), "bijection": len(set(M.values())) == 42 and len(M) == 42,
                "preimages_are_the_42_frozen_ids": set(M) == set(fv2) | set(fa1),
                "images_disjoint_from_v1_v2_a1_r1_r2_r3_retired162": not (set(M.values()) & (v1 | set(fv2) | set(fa1) | set(old_ids) | set(R.RETIRED_ALL))),
                "images_equal_minted_ids": sorted(M.values()) == sorted(x.strip() for x in open(os.path.join(HERE, "minted-run-ids.txt")) if x.strip()),
                "a1r4_id_map_v2_equals_v2r4_id_map": a1r4.get("id_map_v2") == v2r4["id_map"]}
    ok &= rep["M"]["entries"] == 42 and all(v for k, v in rep["M"].items() if k != "entries")
    mdv2, mda1 = md_declared_keys()
    all_lines = open(R.PLAN_V2).read().splitlines()
    rep["watchdogs_line_range"] = {"line_95": all_lines[94], "line_177": all_lines[176], "line_178": all_lines[177]}
    wd_txt = "\n".join(all_lines[94:178]).strip()
    assert wd_txt.startswith('"watchdogs":') and all_lines[177] == " },"
    wd_obj = json.loads(wd_txt[len('"watchdogs":'):].rstrip().rstrip(","))
    for name, plan, frozen, md_keys, n_expected, fz_ids in (("trial-plan-v2-r4.json", v2r4, v2, mdv2, 31, fv2),
                                                              ("trial-plan-v2-a1-r4.json", a1r4, a1, mda1, 11, fa1)):
        declared = plan["repair"]["declared_key_paths"]
        eq, h_r, h_f = dv5_equal(plan, frozen, declared, inverse)
        allowed_old_prefixes = ["/id_map", "/v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/frozen_v2_ids_never_reused", "/id_map_v2"]
        old = set(fv2) | set(fa1) | set(old_ids)
        stray = []
        for pth, s in strings_with_paths(plan):
            for t in TOK.findall(s):
                if t in old and not any(pth == a or pth.startswith(a + "/") for a in allowed_old_prefixes):
                    stray.append({"path": pth, "id": t})
        disclosed = [x for x in stray if x["path"] == "/gate/regression/reference_run"]
        undisclosed = [x for x in stray if x["path"] != "/gate/regression/reference_run"]
        pk_ids = [p["run_id"] for p in sorted(plan["packages"], key=lambda p: p["order"])]
        ri = plan["retired_ids"]
        c = {"rc4c_equality_dv5_own_code": eq, "canonical_sha256_r4_side": h_r, "canonical_sha256_frozen_side": h_f,
             "declared_keys_equal_md_record": declared == md_keys,
             "watchdogs_identical_to_trial_plan_v2_lines_95_177": plan["watchdogs"] == wd_obj == v2["watchdogs"],
             "package_count": len(pk_ids) == n_expected == plan["package_count"],
             "every_package_id_is_the_image_of_the_frozen_id_in_order": pk_ids == [M[i] for i in [p["run_id"] for p in sorted(frozen["packages"], key=lambda p: p["order"])]],
             "no_old_id_outside_maps_lists_retired_ids_except_disclosed": not undisclosed,
             "retired_ids_carry_162": (ri["n_retired"] == 162 and ri["r1_ids_retired_unused"] == R.RETIRED_R1 and ri["r2_ids_retired_unused"] == R.RETIRED_R2
                                       and ri["r3_ids_retired_unused"] == R.RETIRED_R3 and ri["used_r3_gate_ids_kept_as_records_never_rerun_never_reused"] == R.USED_R3),
             "no_forbidden_task_id_eight": all(f not in json.dumps(plan) for f in R.FORBIDDEN_TASK_IDS) and len(R.FORBIDDEN_TASK_IDS) == 8,
             "protocol_label": plan["protocol_version"] == (R.PROTOCOL_V2_R4 if n_expected == 31 else R.PROTOCOL_A1_R4),
             "task_id": plan["task_id"] == (R.TASK_RUNS_V2 if n_expected == 31 else R.TASK_RUNS_A1),
             "written_by_task": plan["written_by_task"] == R.TASK_STAGE,
             "archived_by": plan["archived_by"] == "TASK-20260924-4a47e5 phase A (Coordinator)",
             "gate_regression_d_parsed": plan["gate"]["regression"]["d_branch"] == "d-parsed" and plan["gate"]["regression"]["exclusion_list_sha256"] == sha(R.REG1_EXCLUSION_LIST),
             "gate_admission_RB4_recorded": "rule_RB-4" in (plan["gate"].get("admission") or {})}
        lka1 = lka1_repair_ok(plan["repair"])
        c["repair_block_lka1_content"] = all(lka1.values())
        c["ceiling_note_48_of_48_ten_plans"] = "6 + 31 + 11 = 48 of 48" in plan["ceiling_note"] and "TEN plans" in plan["ceiling_note"]
        rep["plans"][name] = {"checks": c, "lka1_repair_detail": lka1, "old_id_occurrences_disclosed": disclosed,
                              "old_id_occurrences_undisclosed": undisclosed, "md_declared_keys": md_keys}
        ok &= all(c[k] for k in c if not k.startswith("canonical"))
    a1chk = {"v2_blocking_packages_are_the_four_r4_gate_ids": a1r4["gate"]["v2_blocking_packages"] == v2r4["gate"]["blocking_packages"] == [M[g] for g in v2["gate"]["blocking_packages"]],
             "addendum_blocking_package_is_image_of_controls_a1": a1r4["gate"]["addendum_blocking_package"] == M[a1["gate"]["addendum_blocking_package"]],
             "plan_branch_31_bit": a1r4["plan_branch"] == "31-bit",
             "phase_b_receipt_repointed_to_4a47e5": a1r4["repair"]["v2_gate_repointed_to"]["phase_b_receipt"] == os.path.relpath(R.RECEIPT_R4_PHASE_B, R.REPO),
             "gate_regression_in_a1_plan": a1r4["gate"].get("regression", {}).get("d_branch") == "d-parsed",
             "v2_ids_never_reused_mapped": a1r4["v2_ids_never_reused"] == [M[i] for i in a1["v2_ids_never_reused"]]}
    agg = [p for p in a1r4["packages"] if p["kind"] == "aggregate_a1"][0]["driver_args"]
    fagg = [p for p in a1["packages"] if p["kind"] == "aggregate_a1"][0]["driver_args"]
    a1chk["aggregate_a1_args_mapped"] = agg == [",".join(M.get(t, t) for t in x.split(",")) if "RUN-GFPN-" in x else x for x in fagg]
    rep["a1_plan_specific"] = a1chk
    ok &= all(a1chk.values())
    cmd = [sys.executable, "-B", os.path.join(HERE, "r4_make_plans.py"), "--check"] + list(rest)
    pr = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    rep["writer_regenerates_byte_identically"] = {"command": cmd, "returncode": pr.returncode, "stdout": pr.stdout.splitlines(), "stderr": pr.stderr.splitlines()}
    ok &= pr.returncode == 0
    rep["pass"] = bool(ok)
    dump(os.path.join(out, "dv5.json"), rep)
    print(json.dumps({k: v["checks"] for k, v in rep["plans"].items()}, indent=1))
    print(json.dumps(a1chk))
    print("writer --check:", pr.stdout.strip())
    print("DV-5:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ============================================================================ DV-8 exclusion list + comparator (d-parsed)
def _ok_events_doc():
    return {"schema": "crypto.autoresearch.gfpn05.r4.solver_events.v1", "synthetic": "DV-8 only: a structurally valid no-event file",
            "K": 5, "spacing_s": 2.0, "consistency_violation": False, "launch_records": [], "recording_failures": [],
            "sites": {R.SITE_S1: {"counters": {}, "events": [], "attempt_records": [], "passthrough_records": []},
                      R.SITE_S2: {"counters": {}, "events": [], "attempt_records": []},
                      R.SITE_S3: {"counters": {}, "records": []}}}


def dv8(out, rest):
    import ast
    import r4_reg1 as REG
    os.makedirs(out, exist_ok=True)
    rep, ok = {}, True
    ex, ex_sha = REG.load_exclusions()
    never = set(ex["never_excludable"])
    rep["exclusion_list_sha256"] = ex_sha
    rep["byte_identical_to_r3_list"] = sha(R.REG1_EXCLUSION_LIST) == sha(os.path.join(R.EXP_DIR, "implementation-v2-r3", "reg1-exclusion-list.json"))
    rep["byte_identical_to_r2_list"] = sha(R.REG1_EXCLUSION_LIST) == sha(os.path.join(R.EXP_DIR, "implementation-v2-r2", "reg1-exclusion-list.json"))
    rep["byte_identical_to_r1_list"] = sha(R.REG1_EXCLUSION_LIST) == sha(os.path.join(R.EXP_DIR, "implementation-v2-r1", "reg1-exclusion-list.json"))
    rep["sha256_equals_declared_4122bcb0"] = ex_sha == R.REG1_EXCLUSION_SHA256
    md = open(os.path.join(R.EXP_DIR, "implementation-v2-r1.md")).read().splitlines()
    rep["equal_to_implementation_v2_r1_md_lines_329_372"] = "\n".join(md[328:372]) + "\n" == open(R.REG1_EXCLUSION_LIST).read()
    rep["entries"] = [e["id"] for e in ex["entries"]]
    rep["entries_confined_to_permitted_categories"] = all(e["category"] in ex["permitted_categories"] for e in ex["entries"])
    rep["no_entry_names_a_never_excludable_field"] = all(not (set(e["path"]) & never) for e in ex["entries"])
    ok &= (rep["entries_confined_to_permitted_categories"] and rep["no_entry_names_a_never_excludable_field"] and rep["byte_identical_to_r1_list"]
           and rep["equal_to_implementation_v2_r1_md_lines_329_372"] and rep["entries"] == ["X%d" % i for i in range(1, 18)]
           and rep["byte_identical_to_r2_list"] and rep["byte_identical_to_r3_list"] and rep["sha256_equals_declared_4122bcb0"])
    ref = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN)

    def copy_ref(tag, events=True):
        d = os.path.join(out, "perturb", tag, R.REG1_REFERENCE_RUN)
        if os.path.exists(os.path.dirname(d)):
            shutil.rmtree(os.path.dirname(d))
        shutil.copytree(ref, d)
        if events:
            dump(os.path.join(d, "solver-events.json"), _ok_events_doc())
        return d
    selfc = copy_ref("self_with_empty_events")
    self_rep = REG.compare(ref, selfc)
    rep["self"] = {"candidate": "byte copy of RUN-GFPN-ac4487 + a structurally valid no-event solver-events.json", "verdict": self_rep["verdict"],
                   "output": REG.render(self_rep)}
    ok &= self_rep["verdict"] == "PASS"
    cases = {}
    d = copy_ref("a_ms_byte")
    p = os.path.join(d, "solver", "fx_reg0_S3.ms")
    b = bytearray(open(p, "rb").read()); i = b.rfind(b"1"); b[i:i + 1] = b"2"; open(p, "wb").write(bytes(b))
    cases["a: one byte of solver/fx_reg0_S3.ms"] = (d, "FAIL")
    d = copy_ref("b_raw_D")
    p = os.path.join(d, "raw-result.json")
    r = json.load(open(p)); r["targets"][2]["arms"]["S3"]["D"] += 1; json.dump(r, open(p, "w"), indent=1)
    cases["b: raw-result targets[2].arms.S3.D + 1"] = (d, "FAIL")
    d = copy_ref("c_cert_u")
    p = os.path.join(d, "certificates", "decomposition_S3_rescaled_tfresh1_r0.json")
    c = json.load(open(p)); c["factor_base"]["u_values"][0] = (c["factor_base"]["u_values"][0] + 1) % 4111; json.dump(c, open(p, "w"), indent=1)
    cases["c: certificates/decomposition_S3_rescaled_tfresh1_r0.json factor_base.u_values[0] + 1"] = (d, "FAIL")
    sys.path.insert(0, R.V2_DIR)
    import v2_solver as V
    pick = None
    for f in sorted(glob.glob(os.path.join(ref, "solver", "*.ms.out"))):
        k, pl = V.parse_msolve_param(f)
        if k == "param":
            names = open(f[:-4]).readline().strip().split(",")
            s, _ = V.rational_solutions(pl, 4111, len(names))
            if s:
                pick = os.path.basename(f)
                break
    d = copy_ref("d_parsed_field")
    p = os.path.join(d, "solver", pick)
    txt = open(p).read().strip()
    body = txt[:-1] if txt.endswith(":") else txt
    data = ast.literal_eval(body.replace("\n", ""))
    coeffs = data[1][5][1][2][0][0][1]
    coeffs[0] = (coeffs[0] + 1) % 4111
    open(p, "w").write(repr(data) + ":\n")
    cases["d: solver/%s first parametrisation polynomial constant coefficient + 1 (solution set changes)" % pick] = (d, "FAIL")
    d = copy_ref("d_bytes_only_control")
    p = os.path.join(d, "solver", pick)
    body = open(p).read()                                # read BEFORE opening for write
    open(p, "w").write(body.rstrip("\n") + "\n\n")
    cases["control d-parsed: solver/%s gains one trailing newline (bytes differ, parsed fields equal)" % pick] = (d, "PASS")
    d = copy_ref("excluded_only")
    p = os.path.join(d, "raw-result.json")
    r = json.load(open(p)); r["metrics"]["wall_seconds"] = 1.0; r["targets"][0]["arms"]["S3"]["solver"]["wall_seconds"] = 99.0; json.dump(r, open(p, "w"), indent=1)
    p = os.path.join(d, "certificates", "decomposition_S3_tfresh1_r0.json")
    c = json.load(open(p)); c["run_id"] = "RUN-GFPN-3e27a0"; json.dump(c, open(p, "w"), indent=1)
    cases["control: excluded fields only (metrics.wall_seconds, one solver.wall_seconds, one certificate run_id)"] = (d, "PASS")
    d = copy_ref("se_missing", events=False)
    cases["SE-4: candidate solver-events.json missing"] = (d, "FAIL")
    d = copy_ref("se_unparseable")
    open(os.path.join(d, "solver-events.json"), "w").write("{not json")
    cases["SE-4: candidate solver-events.json does not parse"] = (d, "FAIL")
    d = copy_ref("se_violation")
    ev = _ok_events_doc(); ev["consistency_violation"] = True
    ev["sites"][R.SITE_S1]["events"] = [{"site": R.SITE_S1, "tag": "fx_reg0_S3", "consistency": {"ok": False, "violations": ["synthetic DV-8 violation"]}}]
    dump(os.path.join(d, "solver-events.json"), ev)
    cases["SE-4: candidate solver-events.json records a consistency violation (top-level flag and an S-1 event)"] = (d, "FAIL")
    d = copy_ref("se_violation_s2_event_only")
    ev = _ok_events_doc()
    ev["sites"][R.SITE_S2]["events"] = [{"site": R.SITE_S2, "tag": "health_synthetic", "consistency": {"ok": False, "violations": ["synthetic DV-8 violation"]}}]
    dump(os.path.join(d, "solver-events.json"), ev)
    cases["SE-4 / HR-5: an S-2 event records a consistency violation (flag unset)"] = (d, "FAIL")
    d = copy_ref("se_recording_failure_flag")
    ev = _ok_events_doc(); ev["consistency_violation"] = True
    ev["recording_failures"] = [{"where": "launch record", "exception_type": "OSError", "synthetic": "DV-8"}]
    dump(os.path.join(d, "solver-events.json"), ev)
    cases["SE-4 (r4): a recording failure sets the top-level flag (RB-1 / RL-1 / RL-2; RL-7)"] = (d, "FAIL")
    d = copy_ref("se_callgrind_record_only")
    ev = _ok_events_doc()
    ev["sites"][R.SITE_S3]["records"] = [{"site": R.SITE_S3, "tag": "fx_reg0_S3", "log_visible_ssf_indicator": True,
                                          "printed_quotient_dimension_equals_recorded_attempt": False,
                                          "child_readback_equals_requested_cap": False, "consistency": {"ok": False}}]
    ev["sites"][R.SITE_S3]["counters"] = {"callgrind_children_observed": 1, "with_log_visible_ssf_indicator": 1,
                                          "with_quotient_dimension_mismatch": 1, "with_readback_differing_from_requested_cap": 1}
    dump(os.path.join(d, "solver-events.json"), ev)
    cases["control VA-6 (c): a synthetic callgrind-site record (indicator, mismatch, cap flag, even a consistency-like key) is recorded only; REG-1 does not read it"] = (d, "PASS")
    d = copy_ref("se_launch_records_outside_sets")
    ev = _ok_events_doc()
    ev["launch_records"] = [{"ordinal": 1, "synthetic": "DV-8 only", "child_created": "undetermined", "raised": "OSError"}]
    dump(os.path.join(d, "solver-events.json"), ev)
    cases["control RL-7: launch records are outside REG-1's compared sets (even an undetermined one; the r4 checker, not REG-1, reads them)"] = (d, "PASS")
    d = copy_ref("se_renamed_file_outside_sets")
    shutil.copy(os.path.join(d, "solver", "fx_reg0_S3.ms.out"), os.path.join(d, "solver", "fx_reg0_S3.ms.out.ssf-attempt1"))
    cases["control: a renamed *.ssf-attempt1 file is outside the compared sets (listed with sha256)"] = (d, "PASS")
    rep["perturbations"] = {}
    for name, (cd, must) in cases.items():
        rr = REG.compare(ref, cd)
        rep["perturbations"][name] = {"verdict": rr["verdict"], "expected": must, "failures": rr["failures"],
                                      "renamed_attempt_files": rr["renamed_attempt_files"]}
        ok &= rr["verdict"] == must
        print("  %-110s %s (expected %s)" % (name, rr["verdict"], must))
    alt_receipt = os.path.join(out, "perturb", "receipt_altered.json")
    rc = R.load_json(R.RECEIPT_V2_PHASE_B)
    key = "experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/raw-result.json"
    rc["path_sha256"][key] = "0" * 64
    dump(alt_receipt, rc)
    rr = REG.compare(ref, selfc, receipt=alt_receipt)
    rep["reference_integrity_negative"] = {"verdict": rr["verdict"], "failures": rr["failures"][:3]}
    ok &= rr["verdict"] == "FAIL"
    rep["pass"] = bool(ok)
    dump(os.path.join(out, "dv8.json"), rep)
    with open(os.path.join(out, "dv8_self_output.txt"), "w") as fh:
        fh.write(rep["self"]["output"] + "\n")
    print("DV-8 self:", self_rep["verdict"], "; integrity negative:", rr["verdict"], "; files verified", self_rep["reference_integrity"]["files_verified"])
    print("DV-8:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ============================================================================ DV-9 no edit (SC-6)
def _bound_paths_readable(bound, E):
    """Receipt paths the r4 stage may read: under the experiment, outside the r4 write scope, and under runs/ only
    inside the six packages the card permits (R4S-12)."""
    out = {}
    for p, h in bound.items():
        if not p.startswith(E):
            continue
        rest = p[len(E):]
        if rest.startswith(("implementation-v2-r4/", "dev-evidence/stage-r4-dv/")) or rest in ("implementation-v2-r4.md", "trial-plan-v2-r4.json", "trial-plan-v2-a1-r4.json"):
            continue
        if rest.startswith("runs/") and rest.split("/")[1] not in READABLE_RUNS:
            continue
        out[p] = h
    return out


def dv9(out, rest):
    """rest[0]: baseline.json taken at the stage start before any write (sha256, size and mtime of every file under the
    frozen roots; lstat metadata of every other run package; the byte-code listing; the runs/ listing; git status);
    rest[1]: the stage start (UTC ISO). SC-6: pre-existing byte code is listed; any byte code under any frozen tree whose
    mtime is later than the stage start is a failure."""
    os.makedirs(out, exist_ok=True)
    base = R.load_json(rest[0])
    start_epoch = datetime.datetime.fromisoformat(rest[1]).timestamp() if len(rest) > 1 else None
    files = base["files"]
    now = {}
    for p in files:
        fp = os.path.join(R.EXP_DIR, p)
        now[p] = sha(fp) if os.path.isfile(fp) else None
    disk = set()
    for top in base["frozen_roots"]:
        fp = os.path.join(R.EXP_DIR, top)
        if os.path.isfile(fp):
            disk.add(top)
        else:
            for dp, dn, fn in os.walk(fp):
                for f in fn:
                    disk.add(os.path.relpath(os.path.join(dp, f), R.EXP_DIR))
    meta_now, meta_changed = {}, []
    for r in sorted(os.listdir(R.RUNS_DIR)):
        if r in READABLE_RUNS:
            continue
        rp = os.path.join(R.RUNS_DIR, r)
        if os.path.isdir(rp):
            for dp, dn, fn in os.walk(rp):
                for x in fn:
                    q = os.path.join(dp, x)
                    st = os.lstat(q)
                    meta_now[os.path.relpath(q, R.EXP_DIR)] = {"bytes": st.st_size, "mtime": st.st_mtime}
        else:
            st = os.lstat(rp)
            meta_now["runs/" + r] = {"bytes": st.st_size, "mtime": st.st_mtime}
    for k in set(meta_now) | set(base["runs_metadata_only"]):
        if meta_now.get(k) != base["runs_metadata_only"].get(k):
            meta_changed.append(k)
    rep = {"baseline_file": "<scratchpad>/r4/dv9/baseline.json", "baseline_taken_at": base["taken_at_utc"], "n_baseline": len(files),
           "frozen_roots": base["frozen_roots"],
           "changed": sorted(p for p in files if files[p].get("sha256") and now.get(p) != files[p]["sha256"]),
           "added": sorted(disk - set(files)), "removed": sorted(p for p in files if files[p].get("sha256") and now.get(p) is None),
           "other_run_packages_metadata_only": {"n_files": len(meta_now), "changed_or_added_or_removed": sorted(meta_changed),
                                                "method": "lstat size and mtime only; never read (R4S-12)"}}
    checks = {}
    E = os.path.join("experiments", "EXP-GFPN-05ff43") + "/"
    for label, rp in (("0fa03f_phase_A", R.RECEIPT_V2_PHASE_A), ("4ff597_phase_A", R.RECEIPT_A1_PHASE_A), ("0fa03f_phase_B", R.RECEIPT_V2_PHASE_B),
                      ("f1fb0e_phase_A (r3 layer)", os.path.join(R.ARCHIVES, "TASK-20260924-f1fb0e", "snapshot-receipt.json")),
                      ("f1fb0e_phase_B (r3 gate packages)", os.path.join(R.ARCHIVES, "TASK-20260924-f1fb0e", "post-run-receipt.json")),
                      ("53a47d_preservation (stage R1)", os.path.join(R.ARCHIVES, "TASK-20260923-53a47d", "preservation-receipt.json")),
                      ("5ca2a5_preservation (stage r2)", os.path.join(R.ARCHIVES, "TASK-20260924-5ca2a5", "preservation-receipt.json")),
                      ("3ee9a8_seedresolve_premise", os.path.join(R.ARCHIVES, "TASK-20260924-3ee9a8", "snapshot-receipt.json")),
                      ("0957c2_launchcover_premise", os.path.join(R.ARCHIVES, "TASK-20260924-0957c2", "snapshot-receipt.json")),
                      ("ad3f9a_consumer_census", os.path.join(R.ARCHIVES, "TASK-20260924-ad3f9a", "snapshot-receipt.json")),
                      ("c65bfb_launch_census", os.path.join(R.ARCHIVES, "TASK-20260924-c65bfb", "snapshot-receipt.json")),
                      ("68cf6b_launchkind_review", os.path.join(R.ARCHIVES, "TASK-20260924-68cf6b", "snapshot-receipt.json"))):
        if not os.path.exists(rp):
            checks[label] = "receipt absent"
            continue
        bound = _bound_paths_readable(R.receipt_paths(R.load_json(rp)), E)
        bad = [p for p, h in bound.items() if not (os.path.exists(os.path.join(R.REPO, p)) and sha(os.path.join(R.REPO, p)) == h)]
        checks[label] = {"experiment_paths_bound_and_readable": len(bound), "mismatched_or_missing": bad, "equal": not bad}
    rep["receipt_equalities"] = checks
    rep["amendments_seventeen"] = {os.path.basename(p): (sha(p), w, sha(p) == w) for p, w in R.BOUND_HASHES}
    rep["ladder_json"] = {"sha256": sha(R.LADDER_PATH), "unchanged": files.get("implementation/ladder.json", {}).get("sha256") == sha(R.LADDER_PATH)}
    pyc, late = [], []
    for dp, dn, fn in os.walk(R.EXP_DIR):
        for n in fn:
            if n.endswith((".pyc", ".pyo")) or "__pycache__" in dp.split(os.sep):
                fp = os.path.join(dp, n)
                st = os.stat(fp)
                rec = {"path": os.path.relpath(fp, R.REPO), "size": st.st_size,
                       "mtime_utc": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat()}
                pyc.append(rec)
                if start_epoch is not None and st.st_mtime > start_epoch:
                    late.append(rec)
    rep["bytecode_now"] = pyc
    rep["bytecode_at_baseline"] = base["byte_code_files"]
    rep["bytecode_later_than_stage_start"] = late
    rep["bytecode_unchanged_since_baseline"] = sorted(x["path"] for x in pyc) == sorted("experiments/EXP-GFPN-05ff43/" + x["path"] for x in base["byte_code_files"])
    gs_cmd = ["git", "-C", R.REPO, "status", "--porcelain", "--untracked-files=all"]
    gs = subprocess.run(gs_cmd, capture_output=True, text=True, env=git_env()).stdout.splitlines()
    scope = ("experiments/EXP-GFPN-05ff43/implementation-v2-r4/", "experiments/EXP-GFPN-05ff43/implementation-v2-r4.md",
             "experiments/EXP-GFPN-05ff43/trial-plan-v2-r4.json", "experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r4.json",
             "experiments/EXP-GFPN-05ff43/dev-evidence/stage-r4-dv/")
    rep["git_argv"] = [gs_cmd, ["git", "-C", R.REPO, "rev-parse", "HEAD"]]
    rep["git_status"] = gs
    rep["git_status_outside_write_scope"] = [l for l in gs if not l[3:].startswith(scope)]
    rep["git_status_tracked_modifications"] = [l for l in gs if not l.startswith("??")]
    runs = sorted(os.listdir(R.RUNS_DIR))
    rep["runs_dir_entries"] = len(runs)
    rep["no_new_run_directory"] = runs == base["runs_listing"]
    rep["git_head"] = subprocess.run(["git", "-C", R.REPO, "rev-parse", "HEAD"], capture_output=True, text=True, env=git_env()).stdout.strip()
    rep["git_head_unchanged"] = rep["git_head"] == base["head"]
    ok = (not rep["changed"] and not rep["added"] and not rep["removed"] and not meta_changed
          and all(isinstance(v, dict) and v["equal"] for v in checks.values())
          and all(v[2] for v in rep["amendments_seventeen"].values()) and not late and rep["bytecode_unchanged_since_baseline"]
          and rep["ladder_json"]["unchanged"]
          and not rep["git_status_outside_write_scope"] and not rep["git_status_tracked_modifications"] and rep["no_new_run_directory"])
    rep["pass"] = ok
    dump(os.path.join(out, "dv9.json"), rep)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("bytecode_now", "bytecode_at_baseline", "git_status", "frozen_roots")}, indent=1)[:6000])
    print("DV-9:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ============================================================================ DV-10 ids
def dv10(out, rest):
    """rest[0]: the mint-time --check log (every bare id checked BEFORE any stage file named it); rest[1]: the
    allocator log. The current re-check is recorded as information only."""
    os.makedirs(out, exist_ok=True)
    ids = [x.strip() for x in open(os.path.join(HERE, "minted-run-ids.txt")) if x.strip()]
    mint_log = open(rest[0]).read()
    alloc_log = open(rest[1]).read()
    blocks, mint_rc = {}, {}
    for chunk in mint_log.split("### python3 -B tools/allocate_id.py --check ")[1:]:
        cid, body = chunk.split("\n", 1)
        blocks[cid.strip()] = body
        mrc = re.search(r"^rc=(\d+)$", body, re.M)
        mint_rc[cid.strip()] = int(mrc.group(1)) if mrc else None
    alloc_ids = re.findall(r"free run id for 'GFPN': (RUN-GFPN-[0-9a-f]{6})", alloc_log)
    v2, a1 = R.load_json(R.PLAN_V2), R.load_json(R.PLAN_A1)
    v1 = set(v2["v1_ids_never_reused"]) | set(a1["v1_ids_never_reused"])
    fv2, fa1 = {p["run_id"] for p in v2["packages"]}, {p["run_id"] for p in a1["packages"]}
    old = {}
    for key, paths in (("r1", (R.PLAN_V2_R1, R.PLAN_A1_R1)), ("r2", (R.PLAN_V2_R2, R.PLAN_A1_R2)), ("r3", (R.PLAN_V2_R3, R.PLAN_A1_R3))):
        old[key] = set()
        for p in paths:
            old[key] |= {x["run_id"] for x in R.load_json(p)["packages"]}
    checks = []
    for i in ids:
        cmd = [sys.executable, "-B", os.path.join(R.REPO, "tools", "allocate_id.py"), "--check", i]
        pr = subprocess.run(cmd, capture_output=True, text=True, cwd=R.REPO, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        occ = re.search(r"occurrences across the union \((\d+) identifier-bearing paths scanned\): (\d+)", pr.stdout)
        mocc = re.search(r"occurrences across the union \((\d+) identifier-bearing paths scanned\): (\d+)", blocks.get(i, ""))
        checks.append({"id": i, "mint_time_check_rc": mint_rc.get(i), "mint_time_occurrences": int(mocc.group(2)) if mocc else None,
                       "mint_time_ok": "OK: well-formed and free across the union." in blocks.get(i, ""),
                       "recheck_now_command": cmd, "recheck_now_rc": pr.returncode, "recheck_now_occurrences": int(occ.group(2)) if occ else None,
                       "in_v1": i in v1, "in_v2": i in fv2, "in_a1": i in fa1, "in_r1": i in old["r1"], "in_r2": i in old["r2"], "in_r3": i in old["r3"],
                       "in_retired": i in set(R.RETIRED_ALL), "run_dir_exists": os.path.exists(os.path.join(R.RUNS_DIR, i))})
    rep = {"n": len(ids), "distinct": len(set(ids)), "ids_equal_allocator_outputs_in_order": ids == alloc_ids, "checks": checks,
           "none_in_v1_v2_a1_r1_r2_r3_retired162": not any(c["in_v1"] or c["in_v2"] or c["in_a1"] or c["in_r1"] or c["in_r2"] or c["in_r3"] or c["in_retired"] for c in checks),
           "no_run_dir": not any(c["run_dir_exists"] for c in checks),
           "retired_run_dirs": sorted(i for i in R.RETIRED_ALL if os.path.exists(os.path.join(R.RUNS_DIR, i)))}
    rep["all_mint_time_checks_ok_zero_occurrences"] = all(c["mint_time_check_rc"] == 0 and c["mint_time_occurrences"] == 0 and c["mint_time_ok"] for c in checks)
    rep["pass"] = (rep["n"] == 42 and rep["distinct"] == 42 and rep["ids_equal_allocator_outputs_in_order"] and rep["none_in_v1_v2_a1_r1_r2_r3_retired162"]
                   and rep["no_run_dir"] and not rep["retired_run_dirs"] and rep["all_mint_time_checks_ok_zero_occurrences"])
    dump(os.path.join(out, "dv10.json"), rep)
    print("DV-10: 42 ids; mint-time --check rc %s occurrences %s; re-check now rc %s occurrences %s" % (
        sorted({c["mint_time_check_rc"] for c in checks}), sorted({c["mint_time_occurrences"] for c in checks}),
        sorted({c["recheck_now_rc"] for c in checks}), sorted({c["recheck_now_occurrences"] for c in checks})))
    print("DV-10:", "PASS" if rep["pass"] else "FAIL")
    return 0 if rep["pass"] else 1


# ============================================================================ DV-11 (CG-6 with CC-5, VC-3; VA-6..VA-8)
MSOLVE_MARKERS = ("msolve_argv", "MSOLVE", "VALGRIND", "/usr/bin/msolve")
LAUNCH_CALLEES = ("run_child", "callgrind_instructions", "Popen", "execv", "execve", "system", "launch_recorder")
EXPECTED_SITES = {
    "S-1": {"file": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py", "argv_line": 165, "launch_line": 166, "function": "solve",
            "disposition": "WRAPPED BY SE-3 (re-solved on the SSF signature when gb_only is false; passed through when gb_only is true, SE-2 (6)); RB-1 / RL-2 records"},
    "S-2": {"file": "experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py", "argv_line": 144, "launch_line": 147, "function": "run_system",
            "disposition": "WRAPPED BY HR-3 (HR-1..HR-8); RB-1 records"},
    "S-3": {"file": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py", "argv_line": 209, "function": "solve",
            "wrapper_file": "experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py", "wrapper_argv_line": 516, "launch_line": 517,
            "wrapper_function": "callgrind_instructions",
            "disposition": ("COVERED BY CG-2..CG-6 and CC-2..CC-5 (with VC-1, VC-3): never re-solved, recorded (CG-3, CC-4), pre-measured "
                            "(DV-17), compared by REG-1 unchanged, its consumers disposed of by CC-2 with VC-1, counted by DV-11; bound to "
                            "RB-1 (e) by RJ-1. CLASSIFIED (CORR-20260924-432f43 item 1): its output file <tag>.cg.ms.out is removed unread, "
                            "but the record's non-cost fields enter REG-1 (b) and the frozen checker's cap check reads its read-back (CC-3)")}}


def static_launch_sites():
    """AST scan of implementation-v2/, implementation-v2-a1/ and the r4 layer: every call of a process launcher
    (run_child, callgrind_instructions, launch_recorder, Popen, exec*, os.system, subprocess.*) whose argv carries msolve
    (MSOLVE, the literal /usr/bin/msolve, an argv built by msolve_argv, or a VALGRIND-prefixed argv), directly or through
    a local name assigned from such an expression. Returns (msolve launch sites, every launch-like call)."""
    import ast
    found, calls = [], []
    for d in (R.V2_DIR, R.A1_DIR, HERE):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py"):
                continue
            path = os.path.join(d, f)
            src = open(path).read()
            tree = ast.parse(src)
            lines = src.splitlines()
            for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                tainted, assign_line = set(), {}
                for n in ast.walk(fn):
                    if isinstance(n, ast.Assign):
                        seg = ast.get_source_segment(src, n.value) or ""
                        if any(m in seg for m in MSOLVE_MARKERS) or any(isinstance(x, ast.Name) and x.id in tainted for x in ast.walk(n.value)):
                            for t in n.targets:
                                if isinstance(t, ast.Name):
                                    tainted.add(t.id)
                                    assign_line[t.id] = n.lineno
                for n in ast.walk(fn):
                    if not isinstance(n, ast.Call):
                        continue
                    callee = n.func.attr if isinstance(n.func, ast.Attribute) else (n.func.id if isinstance(n.func, ast.Name) else None)
                    base = ast.get_source_segment(src, n.func) or ""
                    is_launch = callee in LAUNCH_CALLEES or base.startswith("subprocess.")
                    if not is_launch or not n.args:
                        continue
                    a0 = n.args[0]
                    seg = ast.get_source_segment(src, a0) or ""
                    names = {x.id for x in ast.walk(a0) if isinstance(x, ast.Name)}
                    msolve = any(m in seg for m in MSOLVE_MARKERS) or bool(names & tainted)
                    rec = {"file": os.path.relpath(path, R.REPO), "line": n.lineno, "function": fn.name, "callee": base,
                           "argv_source": seg[:160], "carries_msolve": msolve,
                           "argv_line": min([assign_line[x] for x in names & tainted] or [n.lineno]),
                           "text": lines[n.lineno - 1].strip()[:180]}
                    calls.append(rec)
                    if msolve:
                        found.append(rec)
    uniq = {}
    for r in found:
        uniq[(r["file"], r["line"])] = r
    return sorted(uniq.values(), key=lambda r: (r["file"], r["line"])), calls


def match_sites(found):
    """Map each found msolve launch call to S-1 / S-2 / S-3; anything else is unexpected (a STOP)."""
    out, unexpected = {"S-1": [], "S-2": [], "S-3": []}, []
    for r in found:
        key = (r["file"], r["line"])
        if key == (EXPECTED_SITES["S-1"]["file"], EXPECTED_SITES["S-1"]["launch_line"]):
            out["S-1"].append(r)
        elif key == (EXPECTED_SITES["S-2"]["file"], EXPECTED_SITES["S-2"]["launch_line"]):
            out["S-2"].append(r)
        elif key in ((EXPECTED_SITES["S-3"]["file"], EXPECTED_SITES["S-3"]["argv_line"]),
                     (EXPECTED_SITES["S-3"]["wrapper_file"], EXPECTED_SITES["S-3"]["launch_line"])):
            out["S-3"].append(r)
        else:
            unexpected.append(r)
    return out, unexpected


def census_sites():
    """The archived launch census CN-1 sites restricted to implementation-v2/ and implementation-v2-a1/."""
    c = R.load_json(os.path.join(R.EXP_DIR, "dev-evidence", "launch-census", "census.json"))
    sites = c["CN1_msolve_launch_census"]["sites"]
    keep = [s for s in sites if "/implementation-v2/" in s["file"] or "/implementation-v2-a1/" in s["file"]]
    return [{k: s.get(k) for k in ("site", "file", "line", "enclosing_function", "reachable", "classification")} for s in keep], \
        [{k: s.get(k) for k in ("site", "file", "line", "enclosing_function", "reachable")} for s in sites]


def dynamic_counts(dv7_dir):
    """DV-11 dynamic part on the DV-7 toy lineage: per package, children (the development fork trace, beneath the
    recorder) against the wrapper counters, the RL-1 launch records and the CG-3 records (CG-6)."""
    trace_p = os.path.join(dv7_dir, "toy", "trace.jsonl")
    tr = [json.loads(l) for l in open(trace_p)] if os.path.exists(trace_p) else []
    rep = json.load(open(os.path.join(dv7_dir, "dv7.json"))) if os.path.exists(os.path.join(dv7_dir, "dv7.json")) else {}
    per_pkg = []
    ok = True
    by_pkg = {}
    for t in tr:
        by_pkg.setdefault(t.get("package"), []).append(t)
    for p in rep.get("packages", []):
        if not p.get("status"):
            continue
        key = "%s/%s" % (p["world"], p["run_id"])
        ev = by_pkg.get(key, [])
        forks = [t for t in ev if t.get("event") == "fork"]
        calls = [t for t in ev if t.get("event") == "original_call_end"]
        s1 = [t for t in forks if t.get("launcher") == "v2_driver.solve" and t.get("child_argv0") == "msolve"]
        s2 = [t for t in forks if t.get("launcher") == "a1_health.run_system" and t.get("child_argv0") == "msolve"]
        s3 = [t for t in forks if t.get("child_argv0") == "valgrind"]
        other_msolve = [t for t in forks if t.get("child_argv0") in ("msolve", "valgrind") and t not in s1 + s2 + s3]
        outside = [t for t in s1 + s2 + s3 if not t.get("inside_wrapper_original_call")]
        doc = {}
        sp = os.path.join(p["run_dir"], "solver-events.json")
        if os.path.exists(sp):
            doc = json.load(open(sp))
        sites = doc.get("sites") or {}
        c1 = (sites.get(R.SITE_S1) or {}).get("counters") or {}
        c2 = (sites.get(R.SITE_S2) or {}).get("counters") or {}
        n3_records = len((sites.get(R.SITE_S3) or {}).get("records") or [])
        lrs = doc.get("launch_records") or []
        cg_calls = [t for t in calls if t.get("site") == R.SITE_S1 and t.get("recorded_attempt_ok_with_callgrind_timeout")]
        s3_in_interval = all(any(c["t_start"] <= x["t"] <= c["t_end"] for c in calls if c.get("site") == R.SITE_S1) for x in s3)
        s3_tags_recorded = sorted(r.get("tag") for r in (sites.get(R.SITE_S3) or {}).get("records") or [])
        row = {"package": key, "forks_traced": len(forks), "launch_records_child_created_true": sum(1 for r in lrs if r.get("child_created") is True),
               "launch_records": len(lrs),
               "s1_msolve_children": len(s1), "s1_wrapper_attempts_plus_passthrough": (c1.get("attempts_total") or 0) + (c1.get("passthrough_calls_gb_only_true") or 0),
               "s2_msolve_children": len(s2), "s2_wrapper_attempts": c2.get("attempts_total") or 0,
               "s3_valgrind_children": len(s3), "s3_wrapped_calls_ok_with_callgrind_timeout": len(cg_calls),
               "s3_cg3_records": n3_records, "s3_children_inside_a_wrapped_call_interval": s3_in_interval,
               "s3_every_child_has_a_cg3_record": sorted(t.get("tag") for t in s3) == s3_tags_recorded,
               "classified_launches_outside_both_wrappers": len(outside), "other_msolve_children": len(other_msolve),
               "builder_python_children": sum(1 for t in forks if (t.get("child_argv0") or "").startswith("python")),
               "gp_children": sum(1 for t in forks if t.get("child_argv0") == "gp")}
        row["equal"] = (row["s1_msolve_children"] == row["s1_wrapper_attempts_plus_passthrough"] and row["s2_msolve_children"] == row["s2_wrapper_attempts"]
                        and row["s3_valgrind_children"] == row["s3_wrapped_calls_ok_with_callgrind_timeout"] == row["s3_cg3_records"]
                        and row["forks_traced"] == row["launch_records_child_created_true"]
                        and s3_in_interval and row["s3_every_child_has_a_cg3_record"] and not outside and not other_msolve)
        ok &= row["equal"]
        per_pkg.append(row)
    return {"trace_file": "dv7/toy/trace.jsonl", "n_trace_events": len(tr), "per_package": per_pkg, "all_equal": ok and bool(per_pkg)}


def dv11(out, rest):
    """rest[0]: the DV-7 output directory (toy lineage and its trace)."""
    os.makedirs(out, exist_ok=True)
    found, calls = static_launch_sites()
    matched, unexpected = match_sites(found)
    cen_v2a1, cen_all = census_sites()
    r4_sites = [r for r in found if "/implementation-v2-r4/" in r["file"]]
    static_ok = (len(matched["S-1"]) == 1 and len(matched["S-2"]) == 1 and len(matched["S-3"]) == 2 and not unexpected and not r4_sites)
    concord = []
    for s in cen_all:
        f = s["file"]
        if "/implementation-v2/v2_driver.py" in f:
            disp = "S-3 (argv line 209)" if s.get("line") == 209 else "S-1"
        elif "/implementation-v2-a1/a1_health.py" in f:
            disp = "S-2"
        else:
            disp = "unreachable (U-1..U-5 of CC-1)"
        concord.append(dict(s, disposition=disp))
    dyn = dynamic_counts(rest[0]) if rest else {"all_equal": None, "note": "no DV-7 directory given"}
    import r4_inventory as INV
    inv = INV.inventory(os.path.join(out, "inventory"))
    rep = {"static": {"launch_like_calls": calls, "msolve_launch_calls_found": found, "matched": matched, "unexpected": unexpected,
                      "r4_layer_msolve_launch_sites": r4_sites, "expected_sites_CC1": EXPECTED_SITES, "pass": static_ok},
           "census_concordance_HR11_CC1": concord, "census_sites_in_v2_and_a1_trees": cen_v2a1,
           "dynamic": dyn, "inventory_summary": inv["summary"], "inventory_file": "dv11/inventory/inventory.json"}
    stops = []
    if not static_ok:
        stops.append("static launch list differs from S-1..S-3 (or an r4 launch site exists)")
    if dyn.get("all_equal") is not True:
        stops.append("a dynamic count differs, a classified launch lies outside both wrappers, a fork has no launch record, or an S-3 child lacks a CG-3 record")
    stops += inv["summary"]["stops"]
    rep["STOP"] = stops or None
    rep["pass"] = not stops
    dump(os.path.join(out, "dv11.json"), rep)
    print("DV-11 static: S-1 %d, S-2 %d, S-3 %d call(s); unexpected %d; r4 launch sites %d" % (len(matched["S-1"]), len(matched["S-2"]), len(matched["S-3"]), len(unexpected), len(r4_sites)))
    print("DV-11 dynamic:", json.dumps({k: v for k, v in dyn.items() if k != "per_package"}))
    for r in dyn.get("per_package", []):
        print("   ", json.dumps(r))
    print("DV-11 inventory:", json.dumps(inv["summary"])[:4000])
    print("DV-11:", "PASS" if rep["pass"] else "STOP: %s" % stops)
    return 0 if rep["pass"] else 3


# ============================================================================ DV-15 (SC-3) parametrisation accounting
def dv15(out, rest):
    """(a) the 75 outputs of the premise check's set O, re-extracted from the hash-verified characterization archive,
    DV-7 bundle and RUN-GFPN-ac4487/solver/, each verified against its receipt first; (b) (optional, rest: run dirs)
    every recorded attempt the frozen classifier called ok in the given toy run directories, enumerated with RB-3.
    NO solver child."""
    import r4_accounting as ACC
    os.makedirs(out, exist_ok=True)
    rep = {"integrity": [], "rows_a": [], "rows_b": []}
    ok = True
    ch = R.receipt_paths(R.load_json(os.path.join(R.ARCHIVES, "TASK-20260923-683f34", "snapshot-receipt.json")))
    pres = R.receipt_paths(R.load_json(os.path.join(R.ARCHIVES, "TASK-20260923-53a47d", "preservation-receipt.json")))
    pc = R.receipt_paths(R.load_json(os.path.join(R.ARCHIVES, "TASK-20260924-3ee9a8", "snapshot-receipt.json")))
    post = R.receipt_paths(R.load_json(R.RECEIPT_V2_PHASE_B))
    E = "experiments/EXP-GFPN-05ff43/"
    files = {"distinct-outputs.tar.gz": (E + "dev-evidence/solver-characterization/distinct-outputs.tar.gz", ch),
             "stageR1-dv7-evidence.tar.gz": (E + "dev-evidence/stageR1-dv7/stageR1-dv7-evidence.tar.gz", pres),
             "premise-check.json": (E + "dev-evidence/seedresolve-premise/premise-check.json", pc)}
    for name, (rel, bound) in files.items():
        got = sha(os.path.join(R.REPO, rel))
        rec = {"file": rel, "sha256": got, "receipt_value": bound.get(rel), "matches": got == bound.get(rel)}
        rep["integrity"].append(rec)
        ok &= rec["matches"]
    if not ok:
        rep["pass"] = False
        rep["STOP_integrity"] = "an input does not match its receipt; DV-15 not evaluated"
        dump(os.path.join(out, "dv15.json"), rep)
        print("DV-15: integrity FAIL")
        return 1
    ex = os.path.join(out, "extract")
    if os.path.exists(ex):
        shutil.rmtree(ex)
    for name in ("distinct-outputs.tar.gz", "stageR1-dv7-evidence.tar.gz"):
        with tarfile.open(os.path.join(R.REPO, files[name][0]), "r:gz") as tf:
            tf.extractall(os.path.join(ex, name.split(".")[0]), filter="data")
    pool = {}
    for dp, _dn, fn in os.walk(ex):
        for f in fn:
            fp = os.path.join(dp, f)
            pool.setdefault(sha(fp), fp)
    acdir = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN, "solver")
    n_ac_verified = 0
    for f in sorted(os.listdir(acdir)):
        fp = os.path.join(acdir, f)
        h = sha(fp)
        key = os.path.relpath(fp, R.REPO)
        if post.get(key) != h:
            rep["integrity"].append({"file": key, "matches": False})
            ok = False
            continue
        n_ac_verified += 1
        pool.setdefault(h, fp)
    rep["ac4487_solver_files_verified_against_post_run_receipt"] = n_ac_verified
    O = R.load_json(os.path.join(R.REPO, files["premise-check.json"][0]))["PR2_output_set_O"]["entries"]
    sys.path.insert(0, R.V2_DIR)
    import v2_solver as V
    import v2_driver as Dv                               # read-only import: _parse_ms_file only; nothing is launched
    for e in O:
        row = {"input_key": e["input_key"], "output_sha256": e["output_sha256"]}
        outp = pool.get(e["output_sha256"])
        msp = pool.get(e["input_ms_sha256"])
        prim = e["primary"]
        logp, errp = pool.get(prim.get("log_sha256")), pool.get(prim.get("err_sha256"))
        row["located"] = {"output": bool(outp), "input_ms": bool(msp), "log": bool(logp), "err": bool(errp) or prim.get("err_sha256") is None}
        if not (outp and msp and logp):
            row["status"] = "NOT LOCATED"
            ok = False
            rep["rows_a"].append(row)
            continue
        names, p, eqs = Dv._parse_ms_file(msp)
        text = ""
        for f in (logp, errp):
            if f:
                text += open(f, errors="replace").read() + "\n"
            else:
                text += "\n"
        st = V.parse_msolve_log(text)
        rec = {"outcome": prim.get("child_outcome_as_recorded")}
        kind = payload = None
        sols, sinfo, nfail = [], None, 0
        if rec["outcome"] == "ok":
            kind, payload = V.parse_msolve_param(outp)
            if kind == "param":
                sols, sinfo = V.rational_solutions(payload, p, len(names))
                nfail = sum(1 for s in sols if not V.substitute(eqs, s, p))
        outcome, reason = V.classify_solve(rec, st, kind, payload, sinfo, nfail)
        row.update(classifier_outcome=outcome, classifier_reason=reason, premise_check_primary_outcome=prim.get("outcome"),
                   classification_agrees_with_premise_check=(outcome == prim.get("outcome")))
        ok &= row["classification_agrees_with_premise_check"]
        a = ACC.accounting(outp, nvars=len(names), p=p)
        row.update({k: a.get(k) for k in ("parse_kind", "applicable", "n_roots", "n_den_zero", "n_arity", "n_points", "n_distinct",
                                           "invariant_holds", "mirror_equals_frozen_rational_solutions", "elim_degree", "header_degree")})
        row["p"], row["nvars"] = p, len(names)
        row["ok_classified"] = outcome == "ok"
        if row["ok_classified"] and row.get("applicable") and not row.get("invariant_holds"):
            row["VIOLATION"] = True
        rep["rows_a"].append(row)
    import r4_check_run as K
    for rd in rest:
        if not os.path.isdir(rd) or not os.path.exists(os.path.join(rd, "raw-result.json")):
            rep["rows_b"].append({"run_dir": rd, "status": "no raw-result.json"})
            continue
        acc = K.sc4_accounting(rd)
        for r in acc["rows"]:
            r["run_dir"] = rd
            r["ok_classified"] = True
            if r.get("applicable") and not r.get("invariant_holds"):
                r["VIOLATION"] = True
            rep["rows_b"].append(r)
        rep.setdefault("rb3_coverage_gaps_named_report_only", []).extend(dict(g, run_dir=rd) for g in acc.get("coverage_gaps_named") or [])
    viol = [r for r in rep["rows_a"] + rep["rows_b"] if r.get("VIOLATION")]
    rep["n_rows_a"] = len(rep["rows_a"])
    rep["n_ok_classified_a"] = sum(1 for r in rep["rows_a"] if r.get("ok_classified"))
    rep["n_rows_b"] = len(rep["rows_b"])
    rep["violations"] = viol
    rep["STOP"] = ("SC-3: DV-15 finds %d violation(s) of the invariant on ok-classified outputs" % len(viol)) if viol else None
    rep["pass"] = bool(ok) and not viol and rep["n_rows_a"] == 75
    dump(os.path.join(out, "dv15.json"), rep)
    print("DV-15: set O %d outputs (%d ok-classified), toy rows %d, violations %d, integrity/location/classification ok %s"
          % (rep["n_rows_a"], rep["n_ok_classified_a"], rep["n_rows_b"], len(viol), ok))
    print("DV-15:", "PASS" if rep["pass"] else "FAIL/STOP")
    return 0 if rep["pass"] else 3


def dispatch(check, out, rest):
    if check == "dv6":
        import r4_dv6
        return r4_dv6.dv6(out, rest)
    if check == "dv7":
        import r4_dv7
        return r4_dv7.dv7(out, rest)
    if check == "dv12":
        import r4_dv12
        return r4_dv12.dv12(out, rest)
    if check == "dv16":
        import r4_dv16
        return r4_dv16.dv16(out, rest)
    fn = {"dv1": dv1_static, "dv5": dv5, "dv8": dv8, "dv9": dv9, "dv10": dv10, "dv11": dv11, "dv15": dv15}[check]
    return fn(out, rest)
