#!/usr/bin/env python3
"""EXP-GFPN-05ff43 successor stage -- development checks DV-1 (static part and the child-side probe), DV-5, DV-8,
DV-9 (SC-6), DV-10, DV-11 and DV-15 (SC-3). Called through r2_devchecks.py; development only; outputs under --out
(session scratchpad). Started from implementation-v2-r1/r1_devchecks_more.py (DV-11 and DV-15 are new).
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
import r2_common as R                                    # noqa: E402

TOK = re.compile(r"RUN-GFPN-[0-9a-f]{6}")


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ============================================================================ DV-1 static inventory + child probe
def dv1_static(out, rest):
    """Static search of implementation-v2/, implementation-v2-a1/ and the r2 layer for PARI uses, the call graph from
    each driver command to them, and a NO-COMPUTATION start-up probe of the Sage child's PARI stack (capped child)."""
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
                 if re.search(r"pari|GF\(|allocatemem|parisize|import", line)]
    graph = {
        "v2 fixture": "v2_driver.main -> cmd_fixture (275) -> fixture_core (284) -> C.curve_order_pari (308) [IN-PROCESS cypari2]",
        "v2 controls": "v2_driver.main -> cmd_controls (752) -> C.fixture_n3(4111) (764) -> C.curve_order_pari (771) [IN-PROCESS cypari2]",
        "v2 fixture4": "v2_driver.main -> cmd_fixture4 (526) -> C.fixture_n4 -> C.curve_order_pari (542) [IN-PROCESS cypari2]",
        "v2 anchor-identity": "v2_driver.main -> cmd_anchor_identity (628) -> V.run_child(SAGE_PYTHON, COMPARATOR) (650) [CHILD: Sage, PARI-backed GF(p^5)]",
        "v2 build": "v2_driver.main -> cmd_build (935): builders in capped v2_child.py children (flint/numpy); ladder orders from ladder.json; no PARI",
        "v2 cells": "v2_driver.main -> cmd_cells (1016): orders from ladder.json; msolve children; no PARI",
        "v2 aggregate": "v2_driver.main -> cmd_aggregate (1248): reads raw-result.json files; no PARI",
        "a1 controls-a1": "a1_driver.main -> cmd_controls_a1 (56) -> P.curve_facts (89) -> V.run_child(/usr/bin/gp) [CHILD: gp, parisize 256000000 / parisizemax 4000000000 set in the script, a1_pari.py line 38]",
        "a1 build": "a1_driver.cmd_build (219) -> v2_driver.cmd_build; no PARI",
        "a1 cells": "a1_driver.cmd_cells (228) -> v2_driver.cmd_cells; no PARI",
        "a1 aggregate-a1": "a1_driver.cmd_aggregate_a1 (276): reads raw-result.json files; no PARI",
        "r2 layer": "r2_common.PariStack: cypari2.Pari() constructions, allocatemem and default read-backs only; no computation",
    }
    sys.path.insert(0, R.V2_DIR)
    import v2_solver as V
    probe = os.path.join(out, "sage_pari_probe.py")
    with open(probe, "w") as fh:
        fh.write("from sage.all import *\nfrom sage.libs.pari import pari\n"
                 "print('R2PROBE parisize', int(pari.default('parisize')))\nprint('R2PROBE parisizemax', int(pari.default('parisizemax')))\n"
                 "print('R2PROBE stacksize', int(pari.stacksize()))\nprint('R2PROBE stacksizemax', int(pari.stacksizemax()))\n"
                 "import sage.version; print('R2PROBE sage_version', sage.version.version)\n")
    so, se = os.path.join(out, "sage_pari_probe.stdout"), os.path.join(out, "sage_pari_probe.stderr")
    rec = V.run_child(["/opt/conda-sage/envs/sage/bin/python", probe], so, se, cap_bytes=R.CAP_BYTES, timeout_s=3600, count_instructions=False)
    vals = {}
    for line in open(so, errors="replace"):
        if line.startswith("R2PROBE "):
            k, v = line.split()[1], line.split()[2]
            vals[k] = v
    ffc = glob.glob("/opt/conda-sage/envs/sage/lib/python3*/site-packages/sage/rings/finite_rings/finite_field_constructor.py")
    impl = []
    if ffc:
        for i, line in enumerate(open(ffc[0]), 1):
            if re.search(r"impl = |order < zech_log_bound|pari_ffelt|givaro", line):
                impl.append({"line": i, "text": line.rstrip()[:160]})
    rep = {"static_hits": hits, "comparator_hits": comp_hits, "call_graph": graph,
           "sage_child_probe": {"script": open(probe).read(), "child": {k: rec.get(k) for k in ("outcome", "returncode", "rlimit_as_child_getrlimit", "rlimit_as_proc_limits_after_exec", "wall_seconds")},
                                "values": vals, "stderr_tail": open(se, errors="replace").read().splitlines()[-10:]},
           "sage_finite_field_constructor": {"file": ffc[0] if ffc else None, "lines": impl[:40]}}
    dump(os.path.join(out, "dv1_static.json"), rep)
    print("DV-1 static: %d PARI-related lines in v2/v2-a1/layer; Sage probe %s %s getrlimit %s" % (len(hits), rec.get("outcome"), vals, rec.get("rlimit_as_child_getrlimit")))
    return 0


# ============================================================================ DV-5 plan derivation (own code path)
def md_declared_keys():
    """Read the declared key paths back from implementation-v2-r2.md (the RC-4 (b) record), independently."""
    txt = open(os.path.join(R.EXP_DIR, "implementation-v2-r2.md")).read()
    sec = txt.split("## RC-4 (a)")[0]
    v2part, a1part = sec.split("`trial-plan-v2-a1-r2.json` (12 paths):")
    grab = lambda s: re.findall(r"^\| `(/[^`]+)` \|", s, re.M)   # noqa: E731
    return grab(v2part), grab(a1part)


def dv5_equal(r2plan, frozen, declared, inverse):
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
    r, f = json.loads(json.dumps(r2plan)), json.loads(json.dumps(frozen))
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


def sc1_repair_ok(rp):
    """SC-1: the repair block names paristack (DEC-20260923-80e280), seedresolve (DEC-20260924-15a77a) and solverevent
    ('incorporated by reference, never approved') with each sha256, and records K = 5, the 2 s spacing, the SF-2 (c)
    cap and the REG-1 (d) branch d-parsed."""
    c = {"paristack": (rp.get("paristack") or {}).get("sha256") == R.PARISTACK_SHA256 and rp["paristack"].get("approval_decision") == "DEC-20260923-80e280",
         "seedresolve": (rp.get("seedresolve") or {}).get("sha256") == R.SEEDRESOLVE_SHA256 and rp["seedresolve"].get("approval_decision") == "DEC-20260924-15a77a",
         "solverevent": (rp.get("solverevent") or {}).get("sha256") == R.SOLVEREVENT_SHA256 and rp["solverevent"].get("standing") == "incorporated by reference, never approved",
         "K_5": rp.get("K") == 5, "spacing_2s": rp.get("spacing_s") == 2.0, "cap": "SF-2 (c)" in str(rp.get("resolve_cap")),
         "d_parsed": rp.get("reg1_d_branch") == "d-parsed", "ps1_branch": rp.get("ps1_branch") == "P-A"}
    return c


def dv5(out, rest):
    os.makedirs(out, exist_ok=True)
    rep, ok = {"plans": {}}, True
    v2, a1 = R.load_json(R.PLAN_V2), R.load_json(R.PLAN_A1)
    v2r2, a1r2 = R.load_json(R.PLAN_V2_R2), R.load_json(R.PLAN_A1_R2)
    r1a, r1b = R.load_json(R.PLAN_V2_R1), R.load_json(R.PLAN_A1_R1)
    rep["frozen_sha256"] = {"trial-plan-v2.json": sha(R.PLAN_V2), "trial-plan-v2-a1.json": sha(R.PLAN_A1)}
    ok &= rep["frozen_sha256"] == {"trial-plan-v2.json": R.PLAN_V2_SHA256, "trial-plan-v2-a1.json": R.PLAN_A1_SHA256}
    M = dict(v2r2["id_map"], **a1r2["id_map"])
    inverse = {v: k for k, v in M.items()}
    v1 = set(v2["v1_ids_never_reused"]) | set(a1["v1_ids_never_reused"])
    fv2, fa1 = [p["run_id"] for p in v2["packages"]], [p["run_id"] for p in a1["packages"]]
    r1ids = [p["run_id"] for p in r1a["packages"]] + [p["run_id"] for p in r1b["packages"]]
    rep["M"] = {"entries": len(M), "bijection": len(set(M.values())) == 42 and len(M) == 42,
                "preimages_are_the_42_frozen_ids": set(M) == set(fv2) | set(fa1),
                "images_disjoint_from_v1_v2_a1_r1_retired": not (set(M.values()) & (v1 | set(fv2) | set(fa1) | set(r1ids) | set(R.RETIRED_ALL))),
                "images_equal_minted_ids": sorted(M.values()) == sorted(x.strip() for x in open(os.path.join(HERE, "minted-run-ids.txt")) if x.strip()),
                "a1r2_id_map_v2_equals_v2r2_id_map": a1r2.get("id_map_v2") == v2r2["id_map"]}
    ok &= rep["M"]["entries"] == 42 and all(v for k, v in rep["M"].items() if k != "entries")
    mdv2, mda1 = md_declared_keys()
    all_lines = open(R.PLAN_V2).read().splitlines()
    rep["watchdogs_line_range"] = {"line_95": all_lines[94], "line_177": all_lines[176], "line_178": all_lines[177]}
    wd_txt = "\n".join(all_lines[94:178]).strip()
    assert wd_txt.startswith('"watchdogs":') and all_lines[177] == " },"
    wd_obj = json.loads(wd_txt[len('"watchdogs":'):].rstrip().rstrip(","))
    for name, plan, frozen, md_keys, n_expected, fz_ids in (("trial-plan-v2-r2.json", v2r2, v2, mdv2, 31, fv2),
                                                              ("trial-plan-v2-a1-r2.json", a1r2, a1, mda1, 11, fa1)):
        declared = plan["repair"]["declared_key_paths"]
        eq, h_r, h_f = dv5_equal(plan, frozen, declared, inverse)
        allowed_old_prefixes = ["/id_map", "/v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/frozen_v2_ids_never_reused",
                                "/id_map_v2"] if name == "trial-plan-v2-r2.json" else ["/id_map", "/id_map_v2", "/frozen_v2_ids_never_reused",
                                                                                      "/a1_ids_never_reused", "/retired_ids"]
        old = set(fv2) | set(fa1) | set(r1ids)
        stray = []
        for pth, s in strings_with_paths(plan):
            for t in TOK.findall(s):
                if t in old and not any(pth == a or pth.startswith(a + "/") for a in allowed_old_prefixes):
                    stray.append({"path": pth, "id": t})
        disclosed = [x for x in stray if x["path"] == "/gate/regression/reference_run"]
        undisclosed = [x for x in stray if x["path"] != "/gate/regression/reference_run"]
        pk_ids = [p["run_id"] for p in sorted(plan["packages"], key=lambda p: p["order"])]
        c = {"rc4c_equality_dv5_own_code": eq, "canonical_sha256_r2_side": h_r, "canonical_sha256_frozen_side": h_f,
             "declared_keys_equal_md_record": declared == md_keys,
             "watchdogs_identical_to_trial_plan_v2_lines_95_177": plan["watchdogs"] == wd_obj == v2["watchdogs"],
             "package_count": len(pk_ids) == n_expected == plan["package_count"],
             "every_package_id_is_the_image_of_the_frozen_id_in_order": pk_ids == [M[i] for i in [p["run_id"] for p in sorted(frozen["packages"], key=lambda p: p["order"])]],
             "no_old_or_r1_id_outside_maps_lists_retired_ids_except_disclosed": not undisclosed,
             "retired_ids_carry_82": plan["retired_ids"]["n_retired"] == 82 and plan["retired_ids"]["r1_ids_retired_unused"] == r1ids,
             "no_forbidden_task_id": all(f not in json.dumps(plan) for f in R.FORBIDDEN_TASK_IDS),
             "protocol_label": plan["protocol_version"] == (R.PROTOCOL_V2_R2 if n_expected == 31 else R.PROTOCOL_A1_R2),
             "task_id": plan["task_id"] == (R.TASK_RUNS_V2 if n_expected == 31 else R.TASK_RUNS_A1),
             "written_by_task": plan["written_by_task"] == R.TASK_STAGE,
             "archived_by": plan["archived_by"] == "TASK-20260924-689d2f phase A (Coordinator)",
             "gate_regression_d_parsed": plan["gate"]["regression"]["d_branch"] == "d-parsed" and plan["gate"]["regression"]["exclusion_list_sha256"] == sha(R.REG1_EXCLUSION_LIST)}
        sc1 = sc1_repair_ok(plan["repair"])
        c["repair_block_sc1_content"] = all(sc1.values())
        rep["plans"][name] = {"checks": c, "sc1_repair_detail": sc1, "old_id_occurrences_disclosed": disclosed,
                              "old_id_occurrences_undisclosed": undisclosed, "md_declared_keys": md_keys}
        ok &= all(c[k] for k in c if not k.startswith("canonical"))
    a1chk = {"v2_blocking_packages_are_the_four_r2_gate_ids": a1r2["gate"]["v2_blocking_packages"] == v2r2["gate"]["blocking_packages"] == [M[g] for g in v2["gate"]["blocking_packages"]],
             "addendum_blocking_package_is_image_of_controls_a1": a1r2["gate"]["addendum_blocking_package"] == M[a1["gate"]["addendum_blocking_package"]],
             "plan_branch_31_bit": a1r2["plan_branch"] == "31-bit",
             "v2_ids_never_reused_mapped": a1r2["v2_ids_never_reused"] == [M[i] for i in a1["v2_ids_never_reused"]]}
    agg = [p for p in a1r2["packages"] if p["kind"] == "aggregate_a1"][0]["driver_args"]
    fagg = [p for p in a1["packages"] if p["kind"] == "aggregate_a1"][0]["driver_args"]
    a1chk["aggregate_a1_args_mapped"] = agg == [",".join(M.get(t, t) for t in x.split(",")) if "RUN-GFPN-" in x else x for x in fagg]
    rep["a1_plan_specific"] = a1chk
    ok &= all(a1chk.values())
    pr = subprocess.run([sys.executable, "-B", os.path.join(HERE, "r2_make_plans.py"), "--check"], capture_output=True, text=True,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    rep["writer_regenerates_byte_identically"] = {"returncode": pr.returncode, "stdout": pr.stdout.splitlines(), "stderr": pr.stderr.splitlines()}
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
    return {"schema": "crypto.autoresearch.gfpn05.r2.solver_events.v1", "synthetic": "DV-8 only: a structurally valid no-event file",
            "K": 5, "spacing_s": 2.0, "counters": {}, "consistency_violation": False, "events": []}


def dv8(out, rest):
    import ast
    import r2_reg1 as REG
    os.makedirs(out, exist_ok=True)
    rep, ok = {}, True
    ex, ex_sha = REG.load_exclusions()
    never = set(ex["never_excludable"])
    rep["exclusion_list_sha256"] = ex_sha
    rep["byte_identical_to_r1_list"] = sha(R.REG1_EXCLUSION_LIST) == sha(os.path.join(R.EXP_DIR, "implementation-v2-r1", "reg1-exclusion-list.json"))
    md = open(os.path.join(R.EXP_DIR, "implementation-v2-r1.md")).read().splitlines()
    rep["equal_to_implementation_v2_r1_md_lines_329_372"] = "\n".join(md[328:372]) + "\n" == open(R.REG1_EXCLUSION_LIST).read()
    rep["entries"] = [e["id"] for e in ex["entries"]]
    rep["entries_confined_to_permitted_categories"] = all(e["category"] in ex["permitted_categories"] for e in ex["entries"])
    rep["no_entry_names_a_never_excludable_field"] = all(not (set(e["path"]) & never) for e in ex["entries"])
    ok &= (rep["entries_confined_to_permitted_categories"] and rep["no_entry_names_a_never_excludable_field"] and rep["byte_identical_to_r1_list"]
           and rep["equal_to_implementation_v2_r1_md_lines_329_372"] and rep["entries"] == ["X%d" % i for i in range(1, 18)])
    ref = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN)

    def copy_ref(tag, events=True):
        d = os.path.join(out, "perturb", tag, R.REG1_REFERENCE_RUN)
        if os.path.exists(os.path.dirname(d)):
            shutil.rmtree(os.path.dirname(d))
        shutil.copytree(ref, d)
        if events:
            dump(os.path.join(d, "solver-events.json"), _ok_events_doc())
        return d
    # self: RUN-GFPN-ac4487 vs a byte copy of itself carrying a no-event solver-events.json (the candidate must have one, SE-4)
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
    # (d) d-parsed: a parsed field perturbed (the first parametrisation polynomial's constant coefficient, in an output
    # with at least one F_p-rational solution, so the solution set changes)
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
    body = open(p).read()                                # read BEFORE opening for write (DV-8 attempt 1 harness fault)
    open(p, "w").write(body.rstrip("\n") + "\n\n")
    cases["control d-parsed: solver/%s gains one trailing newline (bytes differ, parsed fields equal)" % pick] = (d, "PASS")
    d = copy_ref("excluded_only")
    p = os.path.join(d, "raw-result.json")
    r = json.load(open(p)); r["metrics"]["wall_seconds"] = 1.0; r["targets"][0]["arms"]["S3"]["solver"]["wall_seconds"] = 99.0; json.dump(r, open(p, "w"), indent=1)
    p = os.path.join(d, "certificates", "decomposition_S3_tfresh1_r0.json")
    c = json.load(open(p)); c["run_id"] = "RUN-GFPN-a09162"; json.dump(c, open(p, "w"), indent=1)
    cases["control: excluded fields only (metrics.wall_seconds, one solver.wall_seconds, one certificate run_id)"] = (d, "PASS")
    d = copy_ref("se_missing", events=False)
    cases["SE-4: candidate solver-events.json missing"] = (d, "FAIL")
    d = copy_ref("se_unparseable")
    open(os.path.join(d, "solver-events.json"), "w").write("{not json")
    cases["SE-4: candidate solver-events.json does not parse"] = (d, "FAIL")
    d = copy_ref("se_violation")
    ev = _ok_events_doc(); ev["consistency_violation"] = True
    ev["events"] = [{"tag": "fx_reg0_S3", "consistency": {"ok": False, "violations": ["synthetic DV-8 violation"]}}]
    dump(os.path.join(d, "solver-events.json"), ev)
    cases["SE-4: candidate solver-events.json records a consistency violation"] = (d, "FAIL")
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
def dv9(out, rest):
    """rest: baseline.sha256 (repo-relative paths, taken before any write), stage_start_epoch.txt, v1_pycache_pre.txt."""
    os.makedirs(out, exist_ok=True)
    base = {}
    for line in open(rest[0]):
        h, p = line.split(None, 1)
        base[p.strip()] = h
    start_epoch = float(open(rest[1]).read().strip())
    now = {}
    for p in base:
        fp = os.path.join(R.REPO, p)
        now[p] = sha(fp) if os.path.exists(fp) else None
    roots = sorted({"/".join(p.split("/")[:3]) if p.count("/") >= 3 else p for p in base})
    disk = set()
    for top in ["specification.yaml", "amendments", "implementation", "implementation.md", "trial-plan.json", "implementation-v2", "implementation-v2.md",
                "trial-plan-v2.json", "implementation-v2-a1", "implementation-v2-a1.md", "trial-plan-v2-a1.json", "implementation-v2-r1",
                "implementation-v2-r1.md", "trial-plan-v2-r1.json", "trial-plan-v2-a1-r1.json", "dev-evidence/seedresolve-premise",
                "dev-evidence/solver-characterization", "dev-evidence/stageR1-dv7", "runs/RUN-GFPN-ac4487", "runs/RUN-GFPN-3377f1", "execution-report-v2.yaml"]:
        fp = os.path.join(R.EXP_DIR, top)
        if os.path.isfile(fp):
            disk.add(os.path.relpath(fp, R.REPO))
        else:
            for dp, dn, fn in os.walk(fp):
                if "__pycache__" in dp.split(os.sep):
                    continue
                for f in fn:
                    disk.add(os.path.relpath(os.path.join(dp, f), R.REPO))
    rep = {"baseline_file": rest[0], "n_baseline": len(base), "roots": roots,
           "changed": sorted(p for p in base if now.get(p) != base[p]), "added": sorted(disk - set(base)),
           "removed": sorted(p for p in base if now.get(p) is None)}
    checks = {}
    for label, rp in (("0fa03f_phase_A", R.RECEIPT_V2_PHASE_A), ("4ff597_phase_A", R.RECEIPT_A1_PHASE_A), ("0fa03f_phase_B", R.RECEIPT_V2_PHASE_B)):
        bound = R.receipt_paths(R.load_json(rp))
        checks[label] = all(os.path.exists(os.path.join(R.REPO, p)) and sha(os.path.join(R.REPO, p)) == h for p, h in bound.items())
    pres = os.path.join(R.ARCHIVES, "TASK-20260923-53a47d", "preservation-receipt.json")
    if os.path.exists(pres):
        bound = R.receipt_paths(R.load_json(pres))
        checks["53a47d_preservation_receipt (stage-R1 paths, DV-7 bundle)"] = all(
            os.path.exists(os.path.join(R.REPO, p)) and sha(os.path.join(R.REPO, p)) == h for p, h in bound.items())
    rep["receipt_equalities"] = checks
    rep["amendments"] = {os.path.basename(p): (sha(p), w, sha(p) == w) for p, w in R.BOUND_HASHES}
    pyc, late = [], []
    for dp, dn, fn in os.walk(R.EXP_DIR):
        for n in dn + fn:
            if n == "__pycache__" or n.endswith(".pyc"):
                fp = os.path.join(dp, n)
                st = os.stat(fp)
                rec = {"path": os.path.relpath(fp, R.REPO), "size": st.st_size,
                       "mtime_utc": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat()}
                pyc.append(rec)
                if n != "__pycache__" and st.st_mtime > start_epoch:
                    late.append(rec)
    rep["bytecode_now"] = pyc
    rep["bytecode_later_than_stage_start"] = late
    rep["v1_pycache_pre_existing_listing"] = open(rest[2]).read().splitlines()
    rep["pre_existing_v1_pycache_only"] = all(x["path"].startswith("experiments/EXP-GFPN-05ff43/implementation/__pycache__") for x in pyc)
    gs = subprocess.run(["git", "-C", R.REPO, "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True).stdout.splitlines()
    scope = ("experiments/EXP-GFPN-05ff43/implementation-v2-r2/", "experiments/EXP-GFPN-05ff43/implementation-v2-r2.md",
             "experiments/EXP-GFPN-05ff43/trial-plan-v2-r2.json", "experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r2.json",
             "experiments/EXP-GFPN-05ff43/dev-evidence/stage-r2-dv/")
    rep["git_status"] = gs
    rep["git_status_outside_write_scope"] = [l for l in gs if not l[3:].startswith(scope)]
    rep["git_status_tracked_modifications"] = [l for l in gs if not l.startswith("??")]
    # the baseline listing runs_pre.txt was taken with `ls` (hidden entries omitted); compare with the same semantics
    # and list hidden entries separately (DV-9 attempt 1 harness fault: .gitkeep compared against an `ls` listing)
    runs = sorted(x for x in os.listdir(R.RUNS_DIR) if not x.startswith("."))
    rep["runs_dir_entries_non_hidden"] = len(runs)
    rep["runs_dir_hidden_entries"] = sorted(x for x in os.listdir(R.RUNS_DIR) if x.startswith("."))
    rep["no_new_run_directory"] = runs == [x.strip() for x in open(os.path.join(os.path.dirname(rest[0]), "runs_pre.txt")) if x.strip()]
    ok = (not rep["changed"] and not rep["added"] and not rep["removed"] and all(checks.values())
          and all(v[2] for v in rep["amendments"].values()) and not late and rep["pre_existing_v1_pycache_only"]
          and not rep["git_status_outside_write_scope"] and not rep["git_status_tracked_modifications"] and rep["no_new_run_directory"])
    rep["pass"] = ok
    dump(os.path.join(out, "dv9.json"), rep)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("bytecode_now", "v1_pycache_pre_existing_listing", "git_status", "roots")}, indent=1)[:4000])
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
    r1 = {p["run_id"] for p in R.load_json(R.PLAN_V2_R1)["packages"]} | {p["run_id"] for p in R.load_json(R.PLAN_A1_R1)["packages"]}
    checks = []
    for i in ids:
        pr = subprocess.run([sys.executable, "-B", os.path.join(R.REPO, "tools", "allocate_id.py"), "--check", i], capture_output=True, text=True,
                            cwd=R.REPO, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        occ = re.search(r"occurrences across the union \((\d+) identifier-bearing paths scanned\): (\d+)", pr.stdout)
        mocc = re.search(r"occurrences across the union \((\d+) identifier-bearing paths scanned\): (\d+)", blocks.get(i, ""))
        checks.append({"id": i, "mint_time_check_rc": mint_rc.get(i), "mint_time_occurrences": int(mocc.group(2)) if mocc else None,
                       "mint_time_ok": "OK: well-formed and free across the union." in blocks.get(i, ""),
                       "recheck_now_rc": pr.returncode, "recheck_now_occurrences": int(occ.group(2)) if occ else None,
                       "in_v1": i in v1, "in_v2": i in fv2, "in_a1": i in fa1, "in_r1": i in r1, "in_retired": i in set(R.RETIRED_ALL),
                       "run_dir_exists": os.path.exists(os.path.join(R.RUNS_DIR, i))})
    rep = {"n": len(ids), "distinct": len(set(ids)), "ids_equal_allocator_outputs_in_order": ids == alloc_ids, "checks": checks,
           "none_in_v1_v2_a1_r1_retired": not any(c["in_v1"] or c["in_v2"] or c["in_a1"] or c["in_r1"] or c["in_retired"] for c in checks),
           "no_run_dir": not any(c["run_dir_exists"] for c in checks),
           "retired_run_dirs": sorted(i for i in R.RETIRED_ALL if os.path.exists(os.path.join(R.RUNS_DIR, i)))}
    rep["all_mint_time_checks_ok_zero_occurrences"] = all(c["mint_time_check_rc"] == 0 and c["mint_time_occurrences"] == 0 and c["mint_time_ok"] for c in checks)
    rep["pass"] = (rep["n"] == 42 and rep["distinct"] == 42 and rep["ids_equal_allocator_outputs_in_order"] and rep["none_in_v1_v2_a1_r1_retired"]
                   and rep["no_run_dir"] and not rep["retired_run_dirs"] and rep["all_mint_time_checks_ok_zero_occurrences"])
    dump(os.path.join(out, "dv10.json"), rep)
    print("DV-10: 42 ids; mint-time --check rc %s occurrences %s; re-check now rc %s occurrences %s" % (
        sorted({c["mint_time_check_rc"] for c in checks}), sorted({c["mint_time_occurrences"] for c in checks}),
        sorted({c["recheck_now_rc"] for c in checks}), sorted({c["recheck_now_occurrences"] for c in checks})))
    print("DV-10:", "PASS" if rep["pass"] else "FAIL")
    return 0 if rep["pass"] else 1


# ============================================================================ DV-11 msolve call paths
def dv11(out, rest):
    """Static search of implementation-v2/, implementation-v2-a1/ and the r2 layer for every msolve launch (MSOLVE,
    msolve_argv, run_child with an msolve argv) and every call site of solve(); classification of each launch site as
    (i) inside the frozen solve() (reached only through the SE-3 wrapper), (ii) callgrind, (iii) gb_only, or
    (iv) a CLASSIFIED msolve launch outside solve() (its output passed to v2_solver.classify_solve); reachability
    from the commands the r2 plans invoke; and the dynamic count available without the DV-7 lineage (rest[0], if
    given: DV-12's traced unforced toy G1 run)."""
    os.makedirs(out, exist_ok=True)
    pats = {"MSOLVE": re.compile(r"\bMSOLVE\b"), "msolve_argv": re.compile(r"msolve_argv\("), "run_child": re.compile(r"\brun_child\("),
            "classify_solve": re.compile(r"classify_solve\("), "solve_call": re.compile(r"(?<![\w.])(?:D\.)?solve\("),
            "callgrind": re.compile(r"callgrind_instructions\("), "literal_msolve": re.compile(r"/usr/bin/msolve")}
    hits = []
    for d in (R.V2_DIR, R.A1_DIR, HERE):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py"):
                continue
            lines = open(os.path.join(d, f)).read().splitlines()
            fn = None
            for i, line in enumerate(lines, 1):
                m = re.match(r"\s*def (\w+)\(", line)
                if m and not line.startswith(" " * 8):
                    fn = m.group(1)
                s = line.strip()
                if s.startswith("#"):
                    continue
                for k, rx in pats.items():
                    if rx.search(line):
                        hits.append({"file": os.path.relpath(os.path.join(d, f), R.REPO), "line": i, "function": fn, "pattern": k, "text": line.rstrip()[:180]})
    # The frozen launch sites, read from the code (file:line of the frozen files; confirmed by the hits above)
    sites = [
        {"site": "v2_driver.solve (lines 158-215): msolve_argv (165) + run_child (166); classify_solve (197)", "kind": "classified msolve launch INSIDE solve()",
         "through_se3_wrapper": True, "gb_only": "per call site", "reached_by": "every solve() call site below"},
        {"site": "v2_driver.solve (lines 207-209): V.callgrind_instructions(V.msolve_argv(...)) -> run_child(valgrind msolve)", "kind": "callgrind (output never classified)",
         "through_se3_wrapper": True, "reached_by": "solve() with callgrind_timeout and an ok outcome"},
        {"site": "v2_solver.callgrind_instructions (512-548): run_child(valgrind ...)", "kind": "callgrind", "through_se3_wrapper": True,
         "reached_by": "v2_driver.solve only"},
        {"site": "a1_health.run_system (lines 139-230): V.msolve_argv (144) + V.run_child (147); V.parse_msolve_param / rational_solutions / substitute; V.classify_solve (182)",
         "kind": "CLASSIFIED msolve launch OUTSIDE solve()", "through_se3_wrapper": False,
         "reached_by": "a1_health.run (lines 232-) <- a1_driver.cmd_controls_a1 check (d) (a1_driver.py line 129: H.run(p, ctx.rd/health, cap=ctx.cap)) <- "
                       "`controls-a1 --p 1073741831`, package order 1 of trial-plan-v2-a1-r2.json (the addendum's blocking package, image of controls_a1)",
         "classification_consumed": "res['v2_outcome_class'] / checks feed res['pass'] and the health report that a1_driver records for controls_a1 check (d)"},
    ]
    solve_sites = [h for h in hits if h["pattern"] == "solve_call" and "def solve" not in h["text"]]
    rep = {"static_hits": hits, "launch_sites": sites, "solve_call_sites": solve_sites}
    outside = [s for s in sites if s["kind"].startswith("CLASSIFIED") and not s["through_se3_wrapper"]]
    # reachability of a1_health from the r2 plan command
    a1plan = R.load_json(R.PLAN_A1_R2)
    ctl = [p for p in a1plan["packages"] if (p.get("driver_args") or [None])[0] == "controls-a1"]
    rep["r2_plan_packages_reaching_a1_health"] = [{"run_id": p["run_id"], "order": p["order"], "label": p["label"], "driver_args": p["driver_args"]} for p in ctl]
    src = open(os.path.join(R.A1_DIR, "a1_driver.py")).read().splitlines()
    rep["a1_driver_quotes"] = {str(n): src[n - 1] for n in (38, 129, 130, 131)}
    hsrc = open(os.path.join(R.A1_DIR, "a1_health.py")).read().splitlines()
    rep["a1_health_quotes"] = {str(n): hsrc[n - 1] for n in (144, 145, 146, 147, 182)}
    # dynamic part available without DV-7 (DV-12's traced unforced toy G1 run), if given
    if rest:
        tr = [json.loads(l) for l in open(rest[0])] if os.path.exists(rest[0]) else []
        ev = json.load(open(rest[1])) if len(rest) > 1 and os.path.exists(rest[1]) else {}
        ch = [t for t in tr if t.get("event") == "child"]
        cls = [t for t in ch if t.get("child_argv0") == "msolve" and "-P" in (t.get("child_flags") or [])]
        gb = [t for t in ch if t.get("child_argv0") == "msolve" and "-g" in (t.get("child_flags") or [])]
        cg = [t for t in ch if t.get("child_argv0") == "valgrind"]
        c = (ev.get("counters") or {})
        rep["dynamic_partial"] = {"source": "DV-12 traced unforced toy G1 run (fixture command only; the DV-7 lineage was not run)",
                                  "classified_msolve_children_-P": len(cls), "wrapper_attempts_total": c.get("attempts_total"),
                                  "equal": len(cls) == c.get("attempts_total"), "gb_only_msolve_children": len(gb),
                                  "callgrind_children": len(cg), "other_children": sorted({t.get("child_argv0") for t in ch} - {"msolve", "valgrind"}),
                                  "classified_children_outside_wrapper_in_trace": sum(1 for t in cls if not t.get("inside_wrapper"))}
    rep["classified_msolve_launch_outside_wrapper_found"] = bool(outside)
    rep["STOP"] = ("DV-11 finds a classified msolve launch outside the SE-3 wrapper: %s. Reached by %s. SE-3 / SE-9 (incorporated), "
                   "card ST-8: STOP for a new Coordinator decision. The layer cannot remove it without replacing a function other than "
                   "v2_driver.solve (ST-1)." % (outside[0]["site"], [x["run_id"] for x in rep["r2_plan_packages_reaching_a1_health"]])) if outside else None
    rep["pass"] = not outside and (not rest or rep.get("dynamic_partial", {}).get("equal", True))
    dump(os.path.join(out, "dv11.json"), rep)
    print("DV-11: %d static hits; solve() call sites %d; launch sites: %s" % (len(hits), len(solve_sites), [(s["kind"], s["through_se3_wrapper"]) for s in sites]))
    if "dynamic_partial" in rep:
        print("DV-11 dynamic (partial):", json.dumps(rep["dynamic_partial"]))
    print("DV-11:", "PASS" if rep["pass"] else ("STOP: " + (rep["STOP"] or "dynamic count mismatch")))
    return 0 if rep["pass"] else 3


# ============================================================================ DV-15 (SC-3) parametrisation accounting
def dv15(out, rest):
    """(a) the 75 outputs of the premise check's set O, re-extracted from the hash-verified characterization archive,
    DV-7 bundle and RUN-GFPN-ac4487/solver/, each verified against its receipt first; (b) (optional, rest: run dirs)
    every recorded attempt the frozen classifier called ok in the given toy run directories. NO solver child."""
    import r2_accounting as ACC
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
    # (b) toy run directories (recorded attempts classified ok)
    import r2_check_run as K
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


def dv15b(out, rest):
    """DV-15 part (b) only (SC-3 (b)): every recorded attempt the frozen classifier called ok in the given toy run
    directories (rest), with the frozen v2_solver imported read-only and NO solver child. Part (a) is dv15."""
    import r2_check_run as K
    os.makedirs(out, exist_ok=True)
    rows = []
    for rd in rest:
        if not os.path.exists(os.path.join(rd, "raw-result.json")):
            rows.append({"run_dir": rd, "status": "no raw-result.json"})
            continue
        acc = K.sc4_accounting(rd)
        for r in acc["rows"]:
            r["run_dir"] = rd
            r["ok_classified"] = True
            if r.get("applicable") and not r.get("invariant_holds"):
                r["VIOLATION"] = True
            rows.append(r)
    viol = [r for r in rows if r.get("VIOLATION")]
    rep = {"rows_b": rows, "n_rows_b": len(rows), "n_applicable": sum(1 for r in rows if r.get("applicable")), "violations": viol,
           "STOP": ("SC-3: DV-15 (b) finds %d violation(s) on ok-classified outputs" % len(viol)) if viol else None, "pass": not viol}
    dump(os.path.join(out, "dv15b.json"), rep)
    print("DV-15 (b): %d rows, %d applicable (param), violations %d" % (rep["n_rows_b"], rep["n_applicable"], len(viol)))
    print("DV-15 (b):", "PASS" if rep["pass"] else "STOP")
    return 0 if rep["pass"] else 3


def dispatch(check, out, rest):
    if check == "dv6":
        import r2_dv6
        return r2_dv6.dv6(out, rest)
    if check == "dv12":
        import r2_dv12
        return r2_dv12.dv12(out, rest)
    fn = {"dv1": dv1_static, "dv5": dv5, "dv8": dv8, "dv9": dv9, "dv10": dv10, "dv11": dv11, "dv15": dv15, "dv15b": dv15b}[check]
    return fn(out, rest)
