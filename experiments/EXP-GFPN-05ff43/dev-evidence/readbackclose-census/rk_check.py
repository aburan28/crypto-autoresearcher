#!/usr/bin/env python3
"""EXP-GFPN-05ff43 -- ZERO-RUN, ZERO-SOLVE CLOSE CENSUS check script (TASK-20260924-e8da78).

Computes the pre-declared readings of the DRAFT AMD-EXP-GFPN-05ff43-20260924-readbackclose
(pre_approval_readings): RKR-5 (integrity, first), RKR-1, RKR-2, RKR-3, RKR-4, RKR-6, RKR-7.
Observations only: no D, no degree, no approval recommendation, nothing about H-GFPN-9a29be or
HEUR-GFPN-DFLAT beyond "not evidence".

usage:
  PYTHONDONTWRITEBYTECODE=1 python3 -B rk_check.py --out OUT.json --scratch-root DIR [--name-words FILE]

  --scratch-root  the transient scratch directory; every occurrence of it in recorded text is replaced by the
                  label <scratchpad> (the path itself is never written).
  --name-words    optional word-list file (outside the repository); the output JSON and this script are scanned
                  for those words case-insensitively and ONLY the file's sha256 and the hit count are recorded.

Phase 1 (RKQ-2): sha256 checks and read-only git children only. If any check fails, the JSON records the failure,
                 nothing is read as a result, and the script exits 3.
Phase 2 (RKQ-1): an in-process audit-hook guard that refuses child launches and imports of any scanned-tree module.
Phase 3: static readings: ast, dis and tokenize on source text compiled in THIS process (never imported), text
         search, and reads of archived JSON / YAML / text. No child process is started after phase 1.
Dispositions of paths, outcomes and predicates are stated by hand in the tables below (as the two earlier censuses
did); the script checks every cited line against the file text and derives what it can mechanically.
"""
import argparse
import ast
import datetime
import dis
import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import time
import tokenize
import types

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXP_REL = "experiments/EXP-GFPN-05ff43"
EXP = os.path.join(REPO, EXP_REL)
ARCH_REL = "coordination/goals/GOAL-GFPN-380702/archives"
V2 = EXP_REL + "/implementation-v2/"
A1 = EXP_REL + "/implementation-v2-a1/"
R3 = EXP_REL + "/implementation-v2-r3/"
DRAFT_REL = EXP_REL + "/amendments/v2_addendum_readbackclose.yaml"
RBFULL_REL = EXP_REL + "/amendments/v2_addendum_readbackfull.yaml"
RBCOVER_REL = EXP_REL + "/amendments/v2_addendum_readbackcover.yaml"
RBFULL_SHA = "0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1"
RBCOVER_SHA = "dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e"
DIFF_BASE = "dd103455380238ec2f20d17414de687acdcc822a"
CARD_REL = "ledger/handoffs/TASK-20260924-e8da78.yaml"
SUCC_JSON_REL = EXP_REL + "/dev-evidence/readbackfull-census/readbackfull-census.json"
SUCC_MD_REL = EXP_REL + "/dev-evidence/readbackfull-census/readbackfull-census.md"
OUT_DIR_REL = EXP_REL + "/dev-evidence/readbackclose-census"

T0 = time.time()
STARTED = datetime.datetime.now(datetime.timezone.utc)
FILES_READ = {}
CITES = {"n": 0, "failures": [], "by_reading": {}}
GIT_CHILDREN = []
SCRATCH = [None]


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def rd_bytes(rel):
    b = open(os.path.join(REPO, rel), "rb").read()
    FILES_READ[rel] = sha_bytes(b)
    return b


def rd_text(rel):
    return rd_bytes(rel).decode("utf-8", errors="replace")


def rd_json(rel):
    return json.loads(rd_text(rel))


def rd_yaml(rel):
    return yaml.safe_load(rd_text(rel))


def hash_only(rel):
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        return None
    return sha_bytes(open(p, "rb").read())


def redact(s):
    if SCRATCH[0] and isinstance(s, str):
        return s.replace(SCRATCH[0], "<scratchpad>")
    return s


LINES_CACHE = {}


def line_of(rel, n):
    if rel not in LINES_CACHE:
        LINES_CACHE[rel] = rd_text(rel).splitlines()
    ls = LINES_CACHE[rel]
    return ls[n - 1] if 1 <= n <= len(ls) else None


def cite(reading, rel, n, snippet):
    """Check that line n of rel contains snippet; tally per reading."""
    CITES["n"] += 1
    CITES["by_reading"][reading] = CITES["by_reading"].get(reading, 0) + 1
    t = line_of(rel, n)
    ok = t is not None and snippet in t
    if not ok:
        CITES["failures"].append({"reading": reading, "file": rel, "line": n, "expected": snippet, "found": t})
    return "%s:%d" % (os.path.basename(rel), n)


def git(*args):
    argv = ["git", "-C", REPO] + list(args)
    p = subprocess.run(argv, capture_output=True, text=True)
    GIT_CHILDREN.append({"argv": argv, "exit": p.returncode, "stdout_sha256": sha_bytes(p.stdout.encode()),
                         "stdout_lines": len(p.stdout.splitlines())})
    return p


# =================================================================================================== PHASE 1
def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


def phase1():
    out = {}
    ok_all = True
    # (a) the readbackclose draft vs TASK-20260924-1ae107 receipt addendum_sha256
    rc = rd_json(ARCH_REL + "/TASK-20260924-1ae107/ledger-receipt.json")["addendum_sha256"]
    got = hash_only(DRAFT_REL)
    d = yaml.safe_load(open(os.path.join(REPO, DRAFT_REL), "rb").read())["amendment"]
    a_ok = (rc["path"] == DRAFT_REL and got == rc["sha256"] and d.get("status") == "draft"
            and d.get("approved_by") is None and d.get("approval_decision") is None)
    FILES_READ[DRAFT_REL] = got
    out["a_readbackclose_draft"] = {"path": DRAFT_REL, "computed_sha256": got, "receipt_sha256": rc["sha256"],
                                    "receipt": ARCH_REL + "/TASK-20260924-1ae107/ledger-receipt.json (addendum_sha256.sha256)",
                                    "receipt_path_field_equal": rc["path"] == DRAFT_REL, "in_file_status": d.get("status"),
                                    "in_file_approved_by": d.get("approved_by"), "in_file_approval_decision": d.get("approval_decision"),
                                    "pass": a_ok}
    ok_all &= a_ok
    # (b)
    for key, rel, want in (("b_readbackfull", RBFULL_REL, RBFULL_SHA), ("b_readbackcover", RBCOVER_REL, RBCOVER_SHA)):
        g = hash_only(rel)
        FILES_READ[rel] = g
        out[key] = {"path": rel, "computed_sha256": g, "card_sha256": want, "pass": g == want}
        ok_all &= g == want
    # (c) nine VA-1 files vs DEC-20260924-e52eec bound_hashes
    bh = find_key(rd_yaml("ledger/decisions/DEC-20260924-e52eec.yaml"), "bound_hashes")
    rows = []
    for rel, want in bh.items():
        if rel == "note":
            continue
        g = hash_only(rel)
        FILES_READ[rel] = g
        rows.append({"path": rel, "computed_sha256": g, "bound_sha256": want, "equal": g == want})
    c_ok = len(rows) == 9 and all(r["equal"] for r in rows)
    out["c_nine_va1_files"] = {"n": len(rows), "rows": rows, "pass": c_ok}
    ok_all &= c_ok

    def receipt_check(key, rrel, expect_n=None):
        ps = rd_json(rrel)["path_sha256"]
        bad, rows2 = [], []
        for rel, want in ps.items():
            g = hash_only(rel)
            if g != want:
                bad.append({"path": rel, "computed": g, "recorded": want})
            rows2.append((rel, g))
        ok = not bad and (expect_n is None or len(ps) == expect_n)
        out[key] = {"receipt": rrel, "n_paths": len(ps), "n_equal": len(ps) - len(bad), "mismatches": bad, "pass": ok,
                    "path_sha256": {r: g for r, g in rows2} if len(ps) <= 30 else
                    {"combined_sha256_of_sorted_path_hash_lines": sha_bytes("\n".join("%s %s" % x for x in sorted(rows2)).encode())}}
        return ok, ps

    ok, _ = receipt_check("d_archived_census_TASK-20260924-a01341", ARCH_REL + "/TASK-20260924-a01341/snapshot-receipt.json", 3)
    ok_all &= ok
    ok, _ = receipt_check("d_successor_census_TASK-20260924-ddfb69", ARCH_REL + "/TASK-20260924-ddfb69/snapshot-receipt.json", 3)
    ok_all &= ok
    ok, _ = receipt_check("e_TASK-20260924-f1fb0e_snapshot", ARCH_REL + "/TASK-20260924-f1fb0e/snapshot-receipt.json", 22)
    ok_all &= ok
    ok, _ = receipt_check("e_TASK-20260924-f1fb0e_post_run", ARCH_REL + "/TASK-20260924-f1fb0e/post-run-receipt.json", 801)
    ok_all &= ok
    ok, ps0 = receipt_check("f_TASK-20260923-0fa03f", ARCH_REL + "/TASK-20260923-0fa03f/snapshot-receipt.json", 14)
    ok_all &= ok
    ok, ps1 = receipt_check("f_TASK-20260923-4ff597", ARCH_REL + "/TASK-20260923-4ff597/snapshot-receipt.json", 12)
    ok_all &= ok
    unbound = []
    for tree, ps in ((V2, ps0), (A1, ps1)):
        for dp, _dn, fn in os.walk(os.path.join(REPO, tree)):
            if "__pycache__" in dp:
                continue
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), REPO)
                if rel not in ps:
                    unbound.append(rel)
    out["f_unbound_files_in_v2_and_a1_trees"] = {"files": unbound, "pass": not unbound}
    ok_all &= not unbound
    # (g)
    pg = git("diff", "--stat", DIFF_BASE, "--", EXP_REL + "/implementation*", EXP_REL + "/trial-plan-*.json")
    g_ok = pg.returncode == 0 and pg.stdout.strip() == ""
    out["g_git_diff_stat"] = {"argv_base": DIFF_BASE, "exit": pg.returncode, "output": pg.stdout, "pass": g_ok}
    ok_all &= g_ok
    pl = git("ls-files", "--", EXP_REL + "/implementation*", EXP_REL + "/trial-plan-*.json")
    out["g_pathspec_sanity_ls_files_count"] = len(pl.stdout.splitlines())
    head = git("rev-parse", "HEAD").stdout.strip()
    st = git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    out["repository_state"] = {"head": head, "status_porcelain": st}
    out["all_ok"] = bool(ok_all)
    return out


def dp5():
    runs = os.path.join(EXP, "runs")
    dirs = sorted(e for e in os.listdir(runs) if os.path.isdir(os.path.join(runs, e)))
    files = sorted(e for e in os.listdir(runs) if not os.path.isdir(os.path.join(runs, e)))
    r4 = [p for p in ("implementation-v2-r4", "implementation-v2-a1-r4", "trial-plan-v2-r4.json", "trial-plan-v2-a1-r4.json")
          if os.path.exists(os.path.join(EXP, p))] + sorted(e for e in os.listdir(EXP) if e.startswith("implementation-v2-r4"))
    od = os.path.join(REPO, OUT_DIR_REL)
    return {"run_directories": len(dirs), "non_directory_entries_in_runs": files, "r4_paths_present": sorted(set(r4)),
            "readbackclose_census_dir_contents_at_script_time": sorted(os.listdir(od)) if os.path.isdir(od) else None}


# =================================================================================================== PHASE 2
GUARD = {"installed": False, "launch_attempts": 0, "import_attempts": 0, "events": [], "self_test": {}, "mode": "live"}
LAUNCH_EVENTS = {"subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty",
                 "pty.spawn", "os.startfile"}
REFUSED = set()


def scanned_module_names():
    roots = [os.path.join(EXP, d) for d in sorted(os.listdir(EXP)) if d.startswith("implementation")]
    roots += [os.path.join(REPO, "tools"), os.path.join(REPO, "harness"),
              os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7"),
              os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch")]
    names = set()
    for r in roots:
        if not os.path.isdir(r):
            continue
        for dp, _dn, fn in os.walk(r):
            for f in fn:
                if f.endswith(".py"):
                    names.add(f[:-3])
    return names


def _hook(ev, args):
    if ev in LAUNCH_EVENTS:
        if GUARD["mode"] == "live":
            GUARD["launch_attempts"] += 1
            GUARD["events"].append(ev)
        raise RuntimeError("rk_check guard: child launch refused (%s)" % ev)
    if ev == "import" and args and isinstance(args[0], str) and args[0].split(".")[0] in REFUSED:
        if GUARD["mode"] == "live":
            GUARD["import_attempts"] += 1
            GUARD["events"].append("import:" + args[0])
        raise ImportError("rk_check guard: scanned-tree import refused (%s)" % args[0])


def install_guard():
    names = scanned_module_names()
    collide = sorted(n for n in names if n in sys.stdlib_module_names)
    REFUSED.update(n for n in names if n not in sys.stdlib_module_names)
    already = sorted(n for n in REFUSED if n in sys.modules)
    sys.addaudithook(_hook)
    GUARD["installed"] = True
    GUARD["installed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    GUARD["mode"] = "self_test"
    st = {}
    try:
        sys.audit("subprocess.Popen", "x", ["x"], None, None)
        st["launch_refused"] = None
    except RuntimeError:
        st["launch_refused"] = "subprocess.Popen"
    try:
        sys.audit("import", "v2_solver", None, [], [], [])
        st["import_refused"] = None
    except ImportError:
        st["import_refused"] = "v2_solver"
    GUARD["mode"] = "live"
    GUARD["self_test"] = st
    GUARD["n_module_names_refused"] = len(REFUSED)
    GUARD["stdlib_name_collisions_not_refused"] = collide
    GUARD["refused_names_already_imported_before_install"] = already
    GUARD["refused_names_sha256"] = sha_bytes("\n".join(sorted(REFUSED)).encode())


# =================================================================================================== PHASE 3 helpers
def parse(rel):
    return ast.parse(rd_text(rel))


def funcs(tree):
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(n.name, []).append(n)
    return out


def classes(tree):
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}


def bound_names(target):
    """Names a target BINDS (Name, and Names inside Tuple / List / Starred); a Subscript or Attribute store binds no name."""
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        return [n for e in target.elts for n in bound_names(e)]
    if isinstance(target, ast.Starred):
        return bound_names(target.value)
    return []


def compiled_code(rel):
    """Compile the SOURCE TEXT in this process (no import) and return the module code object."""
    return compile(rd_text(rel), os.path.join(REPO, rel), "exec")


def code_objects(co):
    out = {}
    stack = [co]
    while stack:
        c = stack.pop()
        for k in c.co_consts:
            if isinstance(k, types.CodeType):
                out.setdefault(k.co_qualname, []).append(k)
                stack.append(k)
    return out


def instrs_on_lines(code, lines):
    res = {}
    for ins in dis.get_instructions(code):
        ln = ins.positions.lineno if ins.positions else None
        if ln in lines:
            res.setdefault(ln, []).append(ins.opname + ((" " + ins.argrepr) if ins.argrepr else ""))
    return res


# =================================================================================================== RKR-1
SOLVER = V2 + "v2_solver.py"


def rkr1():
    R = "RKR-1"
    t = parse(SOLVER)
    F = funcs(t)
    Cl = classes(t)
    rc, rcl = F["run_child"][0], F["_run_child_locked"][0]
    ret = {}
    for fn in (rc, rcl):
        ret[fn.name] = [{"line": n.lineno, "value": ast.unparse(n.value) if n.value else None}
                        for n in ast.walk(fn) if isinstance(n, ast.Return)]
    called_module_funcs = {}
    top = {n.name for n in t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    reach = ["run_child", "_run_child_locked"]
    seen = set()
    while reach:
        name = reach.pop()
        if name in seen:
            continue
        seen.add(name)
        nodes = F.get(name, [])
        if name in Cl:
            nodes = [m for m in Cl[name].body if isinstance(m, ast.FunctionDef)]
        for fn in nodes:
            for n in ast.walk(fn):
                if isinstance(n, ast.Call):
                    if isinstance(n.func, ast.Name) and n.func.id in top:
                        called_module_funcs.setdefault(name, set()).add(n.func.id)
                        reach.append(n.func.id)
                    if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == "lk":
                        called_module_funcs.setdefault(name, set()).add("SolverLock." + n.func.attr)
    reached = sorted(seen | {"SolverLock.acquire", "SolverLock.release", "SolverLock.__init__"})
    fn_nodes = {"run_child": rc, "_run_child_locked": rcl, "self_rss_bytes": F["self_rss_bytes"][0],
                "other_solver_processes": F["other_solver_processes"][0], "_perf_open_instructions": F["_perf_open_instructions"][0],
                "_perf_read": F["_perf_read"][0], "_decode_status": F["_decode_status"][0]}
    for m in Cl["SolverLock"].body:
        if isinstance(m, ast.FunctionDef):
            fn_nodes["SolverLock." + m.name] = m
    explicit_raises = {k: [n.lineno for n in ast.walk(v) if isinstance(n, ast.Raise)] for k, v in fn_nodes.items()}
    handlers = []
    for k, v in fn_nodes.items():
        for n in ast.walk(v):
            if isinstance(n, ast.Try):
                for h in n.handlers:
                    body = [type(b).__name__ + ((" " + ast.unparse(b.value)) if isinstance(b, ast.Return) and b.value else "") for b in h.body]
                    handlers.append({"function": k, "line": h.lineno, "catches": ast.unparse(h.type) if h.type else "(bare)",
                                     "body": body})
                if n.finalbody:
                    handlers.append({"function": k, "line": n.finalbody[0].lineno, "catches": "finally",
                                     "body": [ast.unparse(b)[:80] for b in n.finalbody]})
    # raise points: every line with a call, per function (explicit OS / C calls listed)
    raise_lines = {}
    for k, v in fn_nodes.items():
        ls = {}
        for n in ast.walk(v):
            if isinstance(n, ast.Call):
                ls.setdefault(n.lineno, set()).add(ast.unparse(n.func))
        raise_lines[k] = {str(a): sorted(b) for a, b in sorted(ls.items())}
    # rec / pid bindings
    def binds(fn, name):
        out = []
        for n in ast.walk(fn):
            tg = []
            if isinstance(n, ast.Assign):
                tg = n.targets
            elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                tg = [n.target]
            elif isinstance(n, (ast.For, ast.comprehension)):
                tg = [n.target]
            elif isinstance(n, ast.Delete):
                tg = n.targets
            elif isinstance(n, ast.ExceptHandler) and n.name == name:
                out.append(n.lineno)
            for x in tg:
                if name in bound_names(x):
                    out.append(n.lineno)
        return sorted(set(out))
    child_body = None
    for n in ast.walk(rcl):
        if isinstance(n, ast.If) and ast.unparse(n.test) == "pid == 0":
            child_body = (n.body[0].lineno, max(getattr(x, "end_lineno", x.lineno) for x in n.body))
    co = compiled_code(SOLVER)
    cos = code_objects(co)
    c_rc, c_rcl = cos["run_child"][0], cos["_run_child_locked"][0]
    bytecode = {"run_child": {str(k): v for k, v in instrs_on_lines(c_rc, {152, 171, 173, 174}).items()},
                "_run_child_locked": {str(k): v for k, v in instrs_on_lines(c_rcl, {181, 220, 227}).items()}}
    frame_identity = {
        "run_child": {"n_code_objects": len(cos["run_child"]), "co_firstlineno": c_rc.co_firstlineno, "co_qualname": c_rc.co_qualname,
                      "rec_is_fast_local": "rec" in c_rc.co_varnames, "cellvars": list(c_rc.co_cellvars)},
        "_run_child_locked": {"n_code_objects": len(cos["_run_child_locked"]), "co_firstlineno": c_rcl.co_firstlineno,
                              "co_qualname": c_rcl.co_qualname, "pid_is_fast_local": "pid" in c_rcl.co_varnames,
                              "rec_is_parameter": "rec" in c_rcl.co_varnames[:c_rcl.co_argcount], "cellvars": list(c_rcl.co_cellvars)}}
    facts = {"returns": ret, "explicit_raise_statements": explicit_raises, "functions_reached_from_run_child": reached,
             "calls_to_v2_solver_functions": {k: sorted(v) for k, v in called_module_funcs.items()},
             "exception_handlers_and_finally": handlers,
             "rec_bindings_run_child": binds(rc, "rec"), "rec_bindings__run_child_locked": binds(rcl, "rec"),
             "pid_bindings__run_child_locked": binds(rcl, "pid"),
             "child_only_block_lines": child_body, "bytecode_from_source_compiled_here": bytecode,
             "frame_identity": frame_identity, "raise_point_lines_with_calls": raise_lines,
             "lock_argument_passed_by_any_call_site": "none (checked by text search of the scanned trees below)"}
    # cited lines (v2_solver)
    S = SOLVER
    for n, s in ((149, "def run_child("), (150, "lock=True"), (151, "never raises for child failures"), (152, 'rec = {"argv"'),
                 (153, "if not isinstance(cap_bytes, int)"), (155, "return rec"), (156, "rss = self_rss_bytes()"), (160, "return rec"),
                 (161, "others = other_solver_processes()"), (165, "return rec"), (166, "lk = SolverLock() if lock else None"),
                 (167, "lk.acquire(wait_s=0)"), (169, "return rec"), (170, "try:"), (171, "return _run_child_locked("), (172, "finally:"),
                 (173, "if lk is not None:"), (174, "lk.release()"), (177, "def _run_child_locked("), (178, "rep_r, rep_w = os.pipe()"),
                 (179, "go_r, go_w = os.pipe()"), (180, "t0 = time.time()"), (181, "pid = os.fork()"), (182, "if pid == 0:"), (183, "try:"),
                 (187, "os.chdir(cwd)"), (188, "fo = os.open(stdout_path"), (190, "os.dup2(fo, 1)"), (193, "resource.setrlimit"),
                 (195, "ERR setrlimit"), (196, "os._exit(97)"), (198, 'os.write(rep_w, ("OK'), (200, "if soft != cap_bytes or hard != cap_bytes:"),
                 (201, "os._exit(98)"), (202, "os.read(go_r, 1)"), (206, "except BaseException:"), (208, "os._exit(99)"),
                 (210, "os.close(rep_w)"), (211, "os.close(go_r)"), (214, "chunk = os.read(rep_r, 256)"), (218, "os.close(rep_r)"),
                 (219, "report = report.decode"), (220, 'rec["child_rlimit_report"] = report'), (221, 'if not report.startswith("OK"):'),
                 (222, "os.close(go_w)"), (223, "os.wait4(pid, 0)"), (224, "child could not set RLIMIT_AS"), (225, "return rec"),
                 (226, "_, soft, hard = report.split()"), (227, 'rec["rlimit_as_child_getrlimit"]'), (228, "if int(soft) != cap_bytes:"),
                 (229, "os.close(go_w)"), (230, "os.wait4(pid, 0)"), (232, "return rec"), (235, "_perf_open_instructions(pid)"),
                 (236, 'os.write(go_w, b"g")'), (237, "os.close(go_w)"), (244, "os.wait4(pid, os.WNOHANG)"),
                 (261, "except (OSError, ValueError, IndexError):"), (263, "time.time() - t0 > timeout_s"), (266, "os.kill(pid, signal.SIGKILL)"),
                 (267, "except ProcessLookupError:"), (269, "os.wait4(pid, 0)"), (271, "time.sleep(0.2)"), (275, "_decode_status(status)"),
                 (281, "_perf_read(perf_fd)"), (287, 'rec["outcome"] = "timeout"'), (288, 'rec["returncode"] == 0'), (299, "open(stderr_path"),
                 (301, "except OSError:"), (304, "memory_exhausted"), (308, "return rec"), (52, 'open("/proc/self/status")'),
                 (73, 'os.listdir("/proc")'), (82, "except OSError:"), (101, 'open(self.path, "a+")'),
                 (105, "fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)"), (107, "except OSError:"), (109, "self.fh.close()"),
                 (111, "return False"), (115, "if self.fh:"), (116, "fcntl.flock(self.fh, fcntl.LOCK_UN)"), (117, "self.fh.close()"),
                 (132, "_libc.syscall"), (141, "os.read(fd, 24)"), (142, "finally:"), (143, "os.close(fd)"), (311, "def _decode_status")):
        cite(R, S, n, s)
    # ---- the path table (dispositions by hand; every cited line checked above)
    P = []

    def row(pid, what, lines, child, l227, fate, obj, frames, pidb, other_obj, rk1, a, b, note=None):
        P.append({"id": pid, "path": what, "lines": lines, "child_created": child, "line_227_executed": l227,
                  "run_child": fate, "record_object": obj, "frames_on_traceback": frames, "pid_bound_in__run_child_locked_frame": pidb,
                  "frozen_handler_returns_other_object": other_obj, "rk1_as_worded_records": rk1,
                  "RKR-1_a": a, "RKR-1_b": b, "note": note})
    OBJ_RET = "returned object IS the object built at 152 (every return in run_child returns `rec`; 171 returns what _run_child_locked returns, which is its parameter `rec` passed at 171, never rebound)"
    OBJ_TB = "`rec` in the outermost frozen run_child frame IS the object built at 152 (single binding at 152; mutated in place by _run_child_locked)"
    NA = "not applicable (no line 227)"
    for pid, what, lines in (("P-1", "refused before fork: invalid cap", "153-155"), ("P-2", "refused before fork: driver RSS > 1 GiB", "156-160"),
                             ("P-3", "refused before fork: another solver-like process", "161-165"), ("P-4", "refused before fork: host lock held", "166-169")):
        row(pid, what, lines, False, False, "returns (refused_to_start)", OBJ_RET, "n/a (return)", "n/a (_run_child_locked not entered)", "no",
            {"readback_from": "returned_record", "child_created": False, "pair": "absent", "pair_read_by_parent": False,
             "basis": "RK-1 (a): no key child_rlimit_report (set only at 220)"}, NA, "holds (no child)")
    row("P-6", "ERR setrlimit: the child writes 'ERR setrlimit ...' and exits 97", "193-196; 220-225", True, False,
        "returns (refused_to_start)", OBJ_RET, "n/a (return)", "n/a (return)", "no",
        {"readback_from": "returned_record", "child_created": True, "pair": "absent", "pair_read_by_parent": False,
         "child_rlimit_report": "'ERR setrlimit ...'", "basis": "RK-1 (a) key presence (220 precedes 225)"}, NA, "holds",
        "NOT A BAR class named by RKR-1 (ERR setrlimit report)")
    row("P-7", "pre-setrlimit child failure (os.chdir / os.open / os.dup2 in the child, 186-191), swallowed at 206, exit 99; empty report",
        "186-191; 206-208; 220-225", True, False, "returns (refused_to_start)", OBJ_RET, "n/a (return)", "n/a (return)", "no",
        {"readback_from": "returned_record", "child_created": True, "pair": "absent", "pair_read_by_parent": False,
         "child_rlimit_report": "''", "basis": "RK-1 (a): key presence, 'true whatever its value, the empty string included'"}, NA, "holds",
        "NOT A BAR class named by RKR-1 (the empty report)")
    row("P-8", "soft read-back != cap", "226-232", True, True, "returns (refused_to_start)", OBJ_RET, "n/a (return)", "n/a (return)", "no",
        {"readback_from": "returned_record", "child_created": True, "pair": "copied", "pair_read_by_parent": True}, "holds", "holds")
    row("P-9", "hard-only mismatch (child exits 98 at 200-201; parent tests soft only at 228): a race", "200-201; 228; 236", True, True,
        "returns via P-12 (308) or raises at 236 (P-14c)", OBJ_RET + "; on the raise: " + OBJ_TB, "on the raise: run_child, _run_child_locked",
        "yes (on the raise)", "no", {"readback_from": "returned_record or raise_frame_record", "child_created": True, "pair": "copied",
                                     "pair_read_by_parent": True}, "holds", "holds")
    for pid, what, lines in (("P-10", "ok without perf counter", "233; 284-285; 288-289; 308"), ("P-11", "ok with perf counter (returns unless _perf_read raises: P-14c)", "235; 280-282; 308"),
                             ("P-12", "memory_exhausted / crashed / non-zero exit (exec failure exit 99 included)", "290-308"),
                             ("P-13", "timeout", "263-270; 286-287; 308")):
        row(pid, what, lines, True, True, "returns", OBJ_RET, "n/a (return)", "n/a (return)", "no",
            {"readback_from": "returned_record", "child_created": True, "pair": "copied", "pair_read_by_parent": True}, "holds", "holds")
    row("P-5a", "raise in run_child before 171: 152 (list(argv); dict build), self_rss_bytes (52-56), other_solver_processes (72-90; OSError at 80-81 is caught at 82), SolverLock() (96-98), acquire (101-112; OSError at 105 caught at 107, then 109 close may raise), the refusal formatting, or an asynchronous exception at any of these lines",
        "152-169; 51-56; 69-90; 96-112", False, False, "RAISES", OBJ_TB + " (UNBOUND if the raise is at 152 itself, before STORE_FAST rec)",
        "run_child (+ callee frame)", "n/a (_run_child_locked not entered)", "no (acquire's handler returns False inside acquire; run_child then returns `rec` at 169)",
        {"readback_from": "raise_frame_record", "child_created": False, "pair": "absent", "pair_read_by_parent": False, "raised": "<type>",
         "basis": "no key; no _run_child_locked frame"}, NA, "holds (no child)",
        "O-1: RK-1 (b) does not state what is recorded when the run_child frame is found but `rec` is not bound (raise at 152). O-2: an asynchronous raise after acquire() returned True at 167 and before the try at 170 leaves the lock file locked until the SolverLock object is collected (no child).")
    row("P-5b", "raise in _run_child_locked before a child exists: os.pipe 178 / 179, time.time 180, os.fork 181 failing (OSError) or its audit event refused",
        "178-181", False, False, "RAISES (after the finally at 172-174 runs; see P-F2)", OBJ_TB, "run_child, _run_child_locked", "no", "no",
        {"readback_from": "raise_frame_record", "child_created": False, "pair": "absent", "pair_read_by_parent": False, "raised": "<type>"},
        NA, "holds (no child)")
    row("P-16", "raise AT 181 AFTER fork() created the child in the parent and BEFORE `pid` is bound: the bytecode of 181 is CALL then STORE_FAST pid; a MemoryError raised while the C function converts the new pid to a Python int, or an asynchronous exception (the default SIGINT handler's KeyboardInterrupt; no other handler is installed in the scanned closure) delivered at the next bytecode boundary after the CALL returns",
        "181", True, False, "RAISES", OBJ_TB, "run_child, _run_child_locked", "NO (pid unbound)", "no",
        {"readback_from": "raise_frame_record", "child_created": False, "pair": "absent", "pair_read_by_parent": False, "raised": "<type>",
         "basis": "rec lacks child_rlimit_report (220 not reached) and the _run_child_locked frame holds no `pid`"},
        NA, "FAILS: a child is created and RK-1 as worded records child_created false",
        "The child reports OK and waits at 202 for the go byte; the parent never closes go_w on this path, so the child is released when the parent process exits (RKL-2). Reachability is a run-time fact (RKL-3); the interpreter behaviour is L-11.")
    row("P-14a", "raise after `pid` is bound and before 220 completes: 182 (asynchronous), os.close 210 / 211, os.read 214, 217, os.close 218, 219, 220",
        "181-220", True, False, "RAISES", OBJ_TB, "run_child, _run_child_locked (+ none)", "yes (pid > 0)", "no",
        {"readback_from": "raise_frame_record", "child_created": True, "pair": "absent", "pair_read_by_parent": False,
         "child_rlimit_report": "key missing (the raise preceded line 220)", "basis": "RK-1 (b): positive pid in the _run_child_locked frame"},
        NA, "holds", "NOT A BAR class named by RKR-1 (a raise before 227)")
    row("P-14b", "raise after 220 and before 227 completes: 221, os.close 222, os.wait4 223, 224 (formatting; _decode_status 311-318), 226 (split / unpack), 227 (int() or the store)",
        "220-227", True, False, "RAISES", OBJ_TB, "run_child, _run_child_locked (+ _decode_status)", "yes", "no",
        {"readback_from": "raise_frame_record", "child_created": True, "pair": "absent", "pair_read_by_parent": False,
         "child_rlimit_report": "as carried: 'ERR setrlimit ...' or '' on 222-224; 'OK <soft> <hard>' on 226-227"},
        NA, "holds",
        "NOT A BAR (a raise before 227). O-3: on 226-227 the report is 'OK <soft> <hard>' and the pair is not read; RK-1 (c)'s examples and RK-2 (ii)'s classes (ERR setrlimit report; empty report; report not read) do not name this report class. From the frozen child, 226-227 can raise only asynchronously or by MemoryError (the child writes exactly 'OK %d %d', 198).")
    row("P-14c", "raise after 227 completed, in _run_child_locked or a callee: os.close 229, os.wait4 230, 231, _perf_open_instructions 235 (129-136), os.write 236 (BrokenPipeError), os.close 237, os.wait4 244, 249-260 (exceptions other than OSError / ValueError / IndexError escape 261), 263, os.kill 266 (other than ProcessLookupError), os.wait4 269, time.sleep 271, 272-279, _perf_read 281 (os.read / struct.unpack 141; os.close 143 in its finally), 284-307 (open at 299 guarded for OSError only)",
        "228-308; 126-145", True, True, "RAISES", OBJ_TB, "run_child, _run_child_locked (+ callee)", "yes", "no",
        {"readback_from": "raise_frame_record", "child_created": True, "pair": "copied", "pair_read_by_parent": True, "raised": "<type>"},
        "holds", "holds", "Contains the successor census's P-14 at 230 / 236 / 244 and P-15 at 281.")
    row("P-F1", "run_child raises AFTER _run_child_locked returned: an asynchronous exception at 171 after the CALL returns, or lk.release() raising in the finally (115-117: fcntl.flock LOCK_UN, self.fh.close(), or asynchronous)",
        "171-174; 114-118", True, "as the return path (yes on 232 / 308; no on 225)", "RAISES (the returned record is discarded)",
        OBJ_TB + " in the state of the return path", "run_child (+ SolverLock.release); _run_child_locked is NOT on the traceback", "n/a (frame gone)",
        "no", {"readback_from": "raise_frame_record", "child_created": True, "pair": "copied where 227 executed; else absent",
               "pair_read_by_parent": "true on 232 / 308; false on 225", "basis": "key child_rlimit_report present (220 precedes 225, 232, 308)"},
        "holds", "holds", "Pre-fork returns (155-169) precede the try at 170, so the finally does not run on them.")
    row("P-F2", "_run_child_locked raises, AND lk.release() raises in run_child's finally (172-174): the exception that leaves run_child is the one from release (the first is its __context__); its traceback holds run_child (174) and SolverLock.release, NOT _run_child_locked",
        "172-174; 114-118 after any of P-5b / P-16 / P-14a / P-14b / P-14c", "as the first raise", "as the first raise", "RAISES",
        OBJ_TB, "run_child, SolverLock.release; _run_child_locked NOT on this traceback (only on __context__.__traceback__)",
        "NO frame of _run_child_locked on the traceback", "no",
        {"after P-5b": {"child_created": False, "correct": True},
         "after P-16": {"child_created": False, "correct": False},
         "after P-14a": {"child_created": False, "pair": "absent", "correct": False,
                         "basis": "rec lacks the key (220 not reached) and no _run_child_locked frame is on the traceback, so the pid test finds nothing"},
         "after P-14b": {"child_created": True, "pair": "absent", "pair_read_by_parent": False, "correct": True},
         "after P-14c": {"child_created": True, "pair": "copied", "pair_read_by_parent": True, "correct": True}},
        "holds (after P-14c the pair is copied from `rec`)", "FAILS after P-14a and after P-16: a created child recorded child_created false",
        "Needs two raises: one in _run_child_locked after fork and before 220, then one from release (an OSError from flock / close, or an asynchronous exception, e.g. a second KeyboardInterrupt, while the finally runs).")
    row("P-C", "CHILD-PROCESS side: in the fork child (os.fork returned 0), an asynchronous exception delivered before the try at 183 (at the bytecode boundary after 181, or at 182) leaves _run_child_locked and run_child IN THE CHILD PROCESS; run_child's finally calls lk.release() in the child (flock LOCK_UN on the open file description the parent shares); the child then continues in the caller's frames without RLIMIT_AS (193 never ran)",
        "181-183; 172-174", "by the definition (a positive pid in the PARENT): the parent side is P-7", False,
        "in the child process: RAISES; in the parent: returns at 225 with report '' once the child exits and closes rep_w", OBJ_RET + " (parent)",
        "parent: n/a (return)", "parent: n/a", "no",
        {"parent": {"readback_from": "returned_record", "child_created": True, "pair": "absent", "child_rlimit_report": "''"},
         "child_process_copy_of_the_recorder": {"child_created": False, "basis": "no key; pid == 0"}},
        NA, "holds on the parent (key presence)",
        "O-4: not traced beyond run_child (L-12): the definitions state CHILD CREATED on the parent; RK-1 does not name records written by a fork child's inherited recorder.")
    fa = [p["id"] for p in P if str(p["RKR-1_a"]).startswith("FAILS")]
    fb = [p["id"] for p in P if str(p["RKR-1_b"]).startswith("FAILS")]
    reading = {
        "draft_condition": "(a) on EVERY path on which line 227 executed, RK-1 (a) or (b) as worded copies the pair; AND (b) on EVERY path on which a child is created, RK-1 as worded records child_created true. A path on which (a) or (b) fails makes the draft NOT approvable as written.",
        "paths_on_which_a_fails": fa, "paths_on_which_b_fails": fb,
        "b_failures_detail": {"P-16": "raise at 181 after the child is created and before `pid` is bound",
                              "P-F2": "after P-14a (or P-16): a raise in _run_child_locked after fork and before 220, followed by a raise from lk.release() in run_child's finally"},
        "stated": "The census names no path on which (a) fails. It names paths on which (b) fails as worded: P-16, and P-F2 after P-14a or P-16."}
    return {"facts": facts, "paths": P, "observations": {
        "O-1": "RK-1 (b) does not state what is recorded when the run_child frame is found but `rec` is unbound (a raise at 152 itself; no child).",
        "O-2": "An asynchronous raise after acquire() returned True (167) and before the try (170) leaves the host lock held until collection (no child).",
        "O-3": "A raise at 226-227 leaves report 'OK <soft> <hard>' without the pair; RK-1 (c) / RK-2 (ii) name no such report class.",
        "O-4": "A fork-child raise before 183 (P-C) runs run_child's finally in the child and continues uncapped in the caller; not traced (L-12)."},
        "reading": reading}


# =================================================================================================== RKR-2
def closure_files(succ):
    mods = set()
    for v in succ["RLR-2"]["entry_import_closure"].values():
        mods |= set(v["modules"])
    files = {}
    for m in sorted(mods):
        for tree in (V2, A1, R3):
            p = tree + m + ".py"
            if os.path.isfile(os.path.join(REPO, p)):
                files[m] = p
    return files


NAMES = ("run_child", "_run_child_locked")
RESOLVED_DYNAMIC = []


def rebind_scan(rel):
    t = parse(rel)
    hits = []
    for n in ast.walk(t):
        tg = []
        kind = None
        if isinstance(n, ast.Assign):
            tg, kind = n.targets, "assign"
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
            tg, kind = [n.target], "assign"
        elif isinstance(n, ast.Delete):
            tg, kind = n.targets, "delete"
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension)):
            tg, kind = [n.target], "loop-target"
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            tg, kind = [i.optional_vars for i in n.items if i.optional_vars is not None], "with-target"
        for x in tg:
            if any(b in NAMES for b in bound_names(x)):
                hits.append({"line": n.lineno, "kind": kind, "target": ast.unparse(x)})
            for y in ast.walk(x):
                if isinstance(y, ast.Attribute) and (y.attr in NAMES or y.attr == "__code__"):
                    hits.append({"line": n.lineno, "kind": kind + " (attribute)", "target": ast.unparse(x)})
                if isinstance(y, ast.Subscript) and ast.unparse(y.value) in ("globals()", "vars()", "sys.modules") or (
                        isinstance(y, ast.Subscript) and ast.unparse(y.value).endswith("__dict__")):
                    hits.append({"line": n.lineno, "kind": kind + " (namespace subscript)", "target": ast.unparse(x)})
        if isinstance(n, (ast.Global, ast.Nonlocal)) and any(x in NAMES for x in n.names):
            hits.append({"line": n.lineno, "kind": type(n).__name__, "target": ",".join(n.names)})
        if isinstance(n, ast.ExceptHandler) and n.name in NAMES:
            hits.append({"line": n.lineno, "kind": "except-as", "target": n.name})
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                if (a.asname or a.name) in NAMES or a.name in NAMES:
                    hits.append({"line": n.lineno, "kind": "import-binding", "target": ast.unparse(n)})
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name in NAMES:
            hits.append({"line": n.lineno, "kind": "def", "target": n.name})
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("setattr", "delattr"):
            a1 = n.args[1] if len(n.args) > 1 else None
            if isinstance(a1, ast.Constant):
                if a1.value in NAMES or a1.value == "__code__":
                    hits.append({"line": n.lineno, "kind": n.func.id, "target": ast.unparse(n)[:120]})
            else:
                vals = None
                if isinstance(a1, ast.Name):
                    for fo in ast.walk(t):
                        if (isinstance(fo, ast.For) and isinstance(fo.target, ast.Name) and fo.target.id == a1.id
                                and fo.lineno <= n.lineno <= fo.end_lineno and isinstance(fo.iter, (ast.Tuple, ast.List))
                                and all(isinstance(e, ast.Constant) for e in fo.iter.elts)):
                            vals = [e.value for e in fo.iter.elts]
                rec = {"line": n.lineno, "kind": n.func.id + " (non-constant name)", "target": ast.unparse(n)[:120],
                       "name_values_resolved_from_enclosing_for_over_a_literal": vals}
                if vals is None or any(v in NAMES or v == "__code__" for v in vals):
                    hits.append(rec)
                else:
                    RESOLVED_DYNAMIC.append(dict(rec, file=os.path.basename(rel)))
        if isinstance(n, ast.NamedExpr) and n.target.id in NAMES:
            hits.append({"line": n.lineno, "kind": "walrus", "target": n.target.id})
    return hits


def rkr2(succ_bytes, succ, integ):
    R = "RKR-2"
    blk = succ["RLR-2"]
    carried = {"source": SUCC_JSON_REL, "file_sha256": sha_bytes(succ_bytes),
               "RLR-2_block_canonical_sha256": sha_bytes(json.dumps(blk, sort_keys=True).encode()),
               "md_lines": "readbackfull-census.md 294-387", "md_sha256": FILES_READ.get(SUCC_MD_REL),
               "reachable_call_sites": blk.get("reachable_call_sites"),
               "reachable_call_sites_not_intercepted": blk.get("reachable_call_sites_not_intercepted"),
               "from_v2_solver_import_statements": blk.get("from_v2_solver_import_statements"),
               "capped_launches_reachable_from_module_level_code": blk.get("capped_launches_reachable_from_module_level_code"),
               "non_call_references_to_run_child_anywhere": blk.get("non_call_references_to_run_child_anywhere")}
    change = {"RKQ-2_g_diff_since_dd1034553": integ["g_git_diff_stat"]["output"], "empty": integ["g_git_diff_stat"]["pass"]}
    t = parse(SOLVER)
    defs = {nm: [{"line": n.lineno, "qualname_parent": "module" if n in t.body else "nested"} for n in ast.walk(t)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nm] for nm in NAMES}
    cite(R, SOLVER, 149, "def run_child(")
    cite(R, SOLVER, 177, "def _run_child_locked(")
    files = closure_files(succ)
    scan = {}
    for m, rel in files.items():
        h = rebind_scan(rel)
        if rel == SOLVER:
            h = [x for x in h if not (x["kind"] == "def" and x["line"] in (149, 177))]
        scan[m] = h
    extra = {}
    for rel in (R3 + "r3_run_wrapper.py", R3 + "r3_check_run.py", R3 + "r3_reg1.py", A1 + "a1_check_run.py", V2 + "v2_check_run.py"):
        extra[os.path.basename(rel)] = rebind_scan(rel)
    lock_kw = []
    for tree in (V2, A1, R3):
        for f in sorted(os.listdir(os.path.join(REPO, tree))):
            if f.endswith(".py"):
                for n in ast.walk(parse(tree + f)):
                    if isinstance(n, ast.Call) and any(k.arg == "lock" for k in n.keywords):
                        lock_kw.append("%s:%d" % (f, n.lineno))
    signal_handlers = []
    for m, rel in files.items():
        for i, ln in enumerate(rd_text(rel).splitlines(), 1):
            if re.search(r"signal\.signal\(|signal\.alarm\(|setitimer\(|register_at_fork\(|addaudithook\(", ln):
                signal_handlers.append("%s:%d" % (os.path.basename(rel), i))
    hits = {m: h for m, h in scan.items() if h}
    reading = {
        "draft_condition": "(a) the successor census's RLR-2 finding stands (six reachable call sites, all resolving run_child at call time through module v2_solver; no import-time capture; no `from v2_solver import`) and no call site has been added since (RKR-5's diff); AND (b) EXACTLY ONE definition each of run_child and _run_child_locked in implementation-v2/v2_solver.py, with the first lines RK-1 names, and no rebinding of either name anywhere in either entry's closure.",
        "a": "carried by hash: six reachable call sites, none not intercepted, no `from v2_solver import`, no module-level capped launch; the RKQ-2 (g) diff since dd1034553 is empty, so no call site has been added in the implementation trees or plans",
        "b_definition_counts": {k: len(v) for k, v in defs.items()}, "b_first_lines": {k: [x["line"] for x in v] for k, v in defs.items()},
        "b_rebinding_hits_in_closure": hits, "stated": ""}
    ok_b = all(len(v) == 1 for v in defs.values()) and defs["run_child"][0]["line"] == 149 and defs["_run_child_locked"][0]["line"] == 177 and not hits
    reading["stated"] = ("Exactly one definition each (run_child 149, _run_child_locked 177, both module level); no assignment, deletion, "
                         "attribute rebinding, `global`, import binding, setattr / delattr, namespace-subscript write or __code__ write "
                         "of either name in any module of either r3 entry's closure." if ok_b else
                         "See b_definition_counts and b_rebinding_hits_in_closure.")
    return {"a_carried": carried, "a_change_since_dd1034553": change,
            "b_definitions": defs, "b_closure_modules_scanned": files, "b_rebinding_scan": scan,
            "b_also_scanned_outside_closure": extra, "b_dynamic_setattr_resolved_not_a_hit": RESOLVED_DYNAMIC,
            "lock_keyword_at_any_call": lock_kw,
            "signal_or_fork_or_audit_handlers_in_closure": signal_handlers, "reading": reading}


# =================================================================================================== RKR-3
CHK = {"v2": V2 + "v2_check_run.py", "a1": A1 + "a1_check_run.py", "r3": R3 + "r3_check_run.py", "reg1": R3 + "r3_reg1.py"}


def checker_items():
    items = []
    for key, rel in CHK.items():
        t = parse(rel)
        fnof = {}
        for n in ast.walk(t):
            if isinstance(n, ast.FunctionDef):
                for m in ast.walk(n):
                    if hasattr(m, "lineno"):
                        fnof.setdefault(m.lineno, n.name)
        src = rd_text(rel).splitlines()
        for n in ast.walk(t):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "append"
                    and isinstance(n.func.value, ast.Name) and n.func.value.id in ("errs", "fails", "ref")):
                items.append({"checker": key, "file": os.path.basename(rel), "line": n.lineno, "function": fnof.get(n.lineno),
                              "text": ast.unparse(n.args[0]) if n.args else None, "source": src[n.lineno - 1].strip()})
            if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id == "errs":
                items.append({"checker": key, "file": os.path.basename(rel), "line": n.lineno, "function": fnof.get(n.lineno),
                              "text": ast.unparse(n.value), "source": src[n.lineno - 1].strip()})
    items.sort(key=lambda x: (x["checker"], x["line"]))
    # non-append exit points, by hand, checked
    other = [("r3", 369, 'FAIL; run id not reserved in either r3 plan', "main: no r3 plan reserves the run id -> return 1"),
             ("r3", 56, "REFUSING: v2_common.PLAN_PATH read-back differs", "frozen_v2: redirection read-back -> return 2"),
             ("r3", 75, "REFUSING: redirection read-back differs", "frozen_a1: redirection read-back -> return 2"),
             ("r3", 400, "return 1 if (errs or pr.returncode) else 0", "main: exit 1 on any r3 item or a non-zero frozen checker"),
             ("a1", 141, "return 1 if (errs or v2_rc) else 0", "main: exit 1 on any addendum item or a non-zero v2_check_run.main"),
             ("v2", 110, "return 1 if errs else 0", "main: exit 1 on any item")]
    for k, n, s, what in other:
        cite("RKR-3", CHK[k], n, s)
    return items, [{"checker": k, "line": n, "what": what} for k, n, s, what in other]


def item_key(it):
    return "%s:%d" % (it["file"], it["line"])


# dispositions per zero-call outcome class: default for every item, then exceptions
ZL = "v2_check_run.py:67"
LAUNCH_INDEPENDENT = ("does not fail by design: its inputs (plan, manifest blocks the wrapper writes from preflight and host state, "
                      "pari-stack.json from the entry, the solver-events.json written by the entry's begin() before dispatch) do not "
                      "depend on a run_child call; on correctly recorded r3 packages it passes (archived f1fb0e post-run checker outputs, "
                      "G1..G4: every r3 item PASS)")
EXC_COMMON = {
    "v2_check_run.py:45": "does not fail: the run id is reserved in the plan the checker reads",
    "v2_check_run.py:48": "does not fail: finish() writes raw-result.json, ladder-table.yaml, heur-dflat.yaml, cost-band-p64.yaml (v2_driver 84-87); the wrapper creates certificates/ (435) and writes command.txt, environment.json, stdout.log, stderr.log, manifest.yaml",
    "v2_check_run.py:54": "does not fail: the wrapper copies raw run_status into the manifest (506); its only change (508-509: non-zero driver exit with completed_valid -> failed) is the exception 53 allows",
    "v2_check_run.py:56": "does not fail: manifest result.metrics is raw.get('metrics', {}) (wrapper 558)",
    ZL: "FAILS: resources.child_rlimit_as_read_back_by_getrlimit is empty (no run_child record exists, so the key collection at wrapper 510 finds no rlimit_as_child_getrlimit) and raw kind is not 'aggregate' (65)",
    "v2_check_run.py:70": "not reached: no entry to compare",
    "v2_check_run.py:73": "does not fail: msolve_threads_executed is [] (no solve), and the test at 72 is `if thr and ...`",
    "v2_check_run.py:84": "not reached: no certificate file (no solve, no lift)",
    "v2_check_run.py:91": "not reached: no certificate file",
    "v2_check_run.py:94": "does not fail: certificate kind is 'none' (cells 1103-1105; or the wrapper default at 559 when raw carries none)",
    "v2_check_run.py:98": "does not fail: F3 / tail_check_2_36 values are v2_scoring.UNDECIDABLE_F3 ('undecidable ...', v2_scoring 23, 257)",
    "v2_check_run.py:102": "does not fail: a cells raw sets group_order = A.group_order(kind, m), which is 2^5 * 5! = 3840 for norm at m = 5 (v2_arms 71-72); other kinds carry no cells",
    "v2_check_run.py:106": "does not fail: none of the three v1 key names is written by the drivers (launch-independent)",
    "a1_check_run.py:86": "not reached: raw has no aggregate_variant (cells / fixture kinds)",
}
OUTCOMES = [
    {"id": "Z-C5", "kinds": ["cells m = 5 (both r3 plans; also as a contingency replacing one)"],
     "what": "no runnable cell reaches _run_cell: each cell ends before it as not_attempted by disposition (1037-1041), refused (rescaling 1044-1050; norm without 2-torsion 1052-1058), condition not met (1059-1067), polynomial unavailable (1068-1075), cached polynomial missing / sha256 mismatch (1076-1081) or invalid (1083-1086)",
     "recorded_as": "completed_valid when every terminal is refused / not_attempted (1101); failed with failure_class resource_exhaustion when any cell is 'invalid' (1101-1102)",
     "sufficient_conditions": ["random_no2torsion: torsion_S5_rq, S5_rescaled and torsion_S5_norm are refused (no rational 2-torsion; the plan records these as expected refusals), raw is not_attempted by disposition, so ONE non-ok S5 m = 5 build row suffices",
                               "ecgfp5_shaped at 16777291: the ladder data record b_is_square_in_Fq true (the only ladder rung and shape with true); the rescaling tests F.is_square(b) itself (v2_arms 165) and, where that agrees with the record, refuses ('b-square class mismatch', 173-174) for torsion_S5_rq and S5_rescaled; one non-ok S5 row then suffices (torsion_S5_norm's condition measured_in_this_package:S5 is not met)",
                               "other (shape, p): S5, torsion_S5_rq and S5_rescaled each without an ok build row (or with a cache mismatch / invalid)"],
     "frozen_lines": [(V2 + "v2_driver.py", 1037, 'spec.get("disposition") == "not_attempted"'), (V2 + "v2_driver.py", 1044, 'A.base_of(kind) == "x_over_lam_in_Fp"'),
                      (V2 + "v2_driver.py", 1052, 'elif kind == "norm":'), (V2 + "v2_driver.py", 1064, "condition not met"),
                      (V2 + "v2_driver.py", 1071, 'brec.get("outcome") != "ok"'), (V2 + "v2_driver.py", 1073, "polynomial unavailable"),
                      (V2 + "v2_driver.py", 1078, "cached polynomial missing"), (V2 + "v2_driver.py", 1084, '"status": "invalid"'),
                      (V2 + "v2_driver.py", 1090, "_run_cell("), (V2 + "v2_driver.py", 1101, 'raw["run_status"]'),
                      (V2 + "v2_driver.py", 1105, '"kind": "none"'), (V2 + "v2_driver.py", 1107, "finish(ctx, raw"),
                      (V2 + "v2_arms.py", 173, "if b_sq:"), (V2 + "v2_arms.py", 174, "b-square class mismatch")],
     "exceptions": {}},
    {"id": "Z-F4", "kinds": ["fixture4 (F-4; v2-r3 plan only)"],
     "what": "cmd_fixture4: the data file's curve refuses the rescaling (536-541) before any build_poly",
     "recorded_as": "failed / specification_error (539)",
     "frozen_lines": [(V2 + "v2_driver.py", 538, 'if rs["refused"]:'), (V2 + "v2_driver.py", 539, 'failure_class="specification_error"'),
                      (V2 + "v2_driver.py", 540, 'finish(ctx, raw, note="F-4 refused")')], "exceptions": {}},
    {"id": "Z-G12", "kinds": ["fixture (G1, G2: gate packages)"],
     "what": "fixture_core: the fixture curve refuses the DC-3 rescaling (298-307) before any build_poly",
     "recorded_as": "failed / specification_error, gate_pass false (305)",
     "frozen_lines": [(V2 + "v2_driver.py", 304, 'if rs["refused"]:'), (V2 + "v2_driver.py", 305, 'failure_class="specification_error"'),
                      (V2 + "v2_driver.py", 280, "finish(ctx, raw")], "exceptions": {}},
    {"id": "W-1", "kinds": ["every kind (recorded by the WRAPPER, not by the frozen driver's own result logic)"],
     "what": "the driver exits or raises before any run_child call without writing raw-result.json (e.g. a1_driver._check_package_p 50-52, a1_driver 223-224 / 232-233 SystemExit refusals; an exception in Ctx() or before the first launch); the entry still wrote solver-events.json (begin() before dispatch) and pari-stack.json (finally)",
     "recorded_as": "failed / infrastructure_error, raw written by the wrapper (491-505) with the three yaml files",
     "frozen_lines": [(R3 + "r3_run_wrapper.py", 491, "if raw is None:"), (R3 + "r3_run_wrapper.py", 493, 'fclass = "infrastructure_error"'),
                      (R3 + "r3_run_wrapper.py", 503, 'for f in ("ladder-table.yaml", "heur-dflat.yaml", "cost-band-p64.yaml"):'),
                      (A1 + "a1_driver.py", 52, "raise SystemExit"), (R3 + "r3_entry_v2.py", 65, "RS.begin()"),
                      (R3 + "r3_entry_v2.py", 77, "R.write_pari_stack_json")],
     "exceptions": {"v2_check_run.py:94": "does not fail: raw carries no certificate; the manifest default is kind 'none' (wrapper 559)",
                    "v2_check_run.py:98": "does not fail: the wrapper's raw carries no F3 key"}},
    {"id": "W-2", "kinds": ["every kind (recorded by the WRAPPER)"],
     "what": "the r3 entry refuses before any command (a failed RC-3 / SE-3 / HR-3 / SE-6 / RC-2 (a) read-back: r3_entry_v2 60-64; r3_entry_a1 92): no begin(), so no solver-events.json; pari-stack.json status refused_before_any_command with no exit read-back",
     "recorded_as": "failed / infrastructure_error (wrapper 494-495)",
     "frozen_lines": [(R3 + "r3_entry_v2.py", 60, "if reasons:"), (R3 + "r3_entry_v2.py", 61, "refused_before_any_command"),
                      (R3 + "r3_entry_a1.py", 92, "refused_before_any_command"), (R3 + "r3_run_wrapper.py", 494, "refused_before_any_command")],
     "exceptions": {"r3_check_run.py:279": "FAILS: pari_stack status refused_before_any_command (278)",
                    "r3_check_run.py:305": "FAILS: no exit read-back in the refusal record (r3_common.write_pari_stack_json 405-417; exit_readback not run)",
                    "r3_check_run.py:308": "FAILS: no exit read-back (parisize None)",
                    "r3_check_run.py:167": "FAILS: solver-events.json missing (begin() not reached)",
                    "r3_check_run.py:185": "not reached (events_file_epsilon returns at 168)",
                    "r3_check_run.py:283": "FAILS if the refusal was a redirection read-back",
                    "r3_check_run.py:288": "FAILS if the refusal was the SE-3 read-back",
                    "r3_check_run.py:293": "FAILS if the refusal was the a1 HR-3 read-back",
                    "r3_check_run.py:297": "FAILS if the refusal was the v2 HR-3 read-back",
                    "r3_check_run.py:302": "FAILS if the refusal was the RC-2 (a) start read-back",
                    "r3_check_run.py:317": "FAILS if the refusal was the SE-6 hash-seed read-back",
                    "v2_check_run.py:94": "does not fail: the manifest default certificate kind 'none'",
                    "v2_check_run.py:98": "does not fail: the wrapper's raw carries no F3 key"}},
]
NO_ZERO_CALL_KINDS = [
    {"kind": "anchor (G3, anchor-identity)", "why": "its first launch is unconditional: the comparator run_child at 650", "lines": [(V2 + "v2_driver.py", 650, "V.run_child(")]},
    {"kind": "controls (G4)", "why": "its first launch is unconditional: build_poly at 768 -> child_job -> run_child 101", "lines": [(V2 + "v2_driver.py", 768, "build_poly("), (V2 + "v2_driver.py", 101, "V.run_child(")]},
    {"kind": "build (both plans)", "why": "every plan build list holds S5 and S4 rows for every shape; kind S takes no refusal branch (947) and reaches build_poly at 961", "lines": [(V2 + "v2_driver.py", 947, 'if kind in ("rq", "norm", "S_rescaled"):'), (V2 + "v2_driver.py", 961, "build_poly(")]},
    {"kind": "cells m = 4 (both plans)", "why": "the raw arm is disposition 'run' with no condition and needs no build (kind raw_x); _run_cell's first target runs raw_grid (1161) -> run_child, since early_stop is None and the per-cell watchdog (86400 s for raw|m4) cannot have fired before the first target", "lines": [(V2 + "v2_driver.py", 1149, "per_cell_no_measurement_watchdog_s"), (V2 + "v2_driver.py", 1161, "raw_grid(")]},
    {"kind": "controls_a1 (a1 plan package 1)", "why": "the gp child is unconditional: P.curve_facts at a1_driver 89 -> a1_pari 96 run_child", "lines": [(A1 + "a1_driver.py", 89, "P.curve_facts("), (A1 + "a1_pari.py", 96, "V.run_child(")]},
    {"kind": "aggregate / aggregate_a1", "why": "they never call run_child (no launch path; successor census path count 0), and their raw kind is 'aggregate' (v2_driver 1314; a1_driver 374), which v2_check_run exempts at 65: the ZL item is not reached; no item fails by design", "lines": [(V2 + "v2_driver.py", 1314, '"kind": "aggregate"'), (A1 + "a1_driver.py", 374, '"kind": "aggregate"'), (V2 + "v2_check_run.py", 65, 'if raw.get("kind") != "aggregate":')]},
    {"kind": "contingency", "why": "runs the replaced package's command and plan entry (wrapper 427-430; v2_driver 59-62): as the replaced kind", "lines": [(R3 + "r3_run_wrapper.py", 427, 'if pk["kind"] == "contingency":'), (V2 + "v2_driver.py", 59, 'if self.pkg["kind"] == "contingency":')]},
]


def rkr3():
    R = "RKR-3"
    items, other = checker_items()
    kinds = {}
    for pr in (EXP_REL + "/trial-plan-v2-r3.json", EXP_REL + "/trial-plan-v2-a1-r3.json"):
        for p in rd_json(pr)["packages"]:
            k = p["kind"] + (" m=%s" % p["m"] if p["kind"] == "cells" else "")
            kinds.setdefault(os.path.basename(pr), {}).setdefault(k, []).append(p["run_id"])
    for o in OUTCOMES:
        for rel, n, s in o["frozen_lines"]:
            cite(R, rel, n, s)
    for k in NO_ZERO_CALL_KINDS:
        for rel, n, s in k["lines"]:
            cite(R, rel, n, s)
    for n, s in ((65, 'if raw.get("kind") != "aggregate":'), (66, "if not caps:"), (67, 'errs.append("no child RLIMIT_AS read-back recorded")'),
                 (72, "if thr and thr != [1]:"), (107, 'print("%s: %s; %s"'), (109, 'print("  -", e)')):
        cite(R, CHK["v2"], n, s)
    for rel, n, s in ((R3 + "r3_run_wrapper.py", 510, 'collect(raw, "rlimit_as_child_getrlimit"'), (R3 + "r3_run_wrapper.py", 435, 'os.makedirs(os.path.join(rd, "certificates"))'),
                      (R3 + "r3_run_wrapper.py", 559, '"certificate": raw.get("certificate") or {"kind": "none"'), (V2 + "v2_driver.py", 85, "ladder-table.yaml"),
                      (V2 + "v2_driver.py", 87, "cost-band-p64.yaml"), (V2 + "v2_arms.py", 72, "return 2 ** m * math.factorial(m)"),
                      (V2 + "v2_scoring.py", 257, '"F3": UNDECIDABLE_F3'), (R3 + "r3_resolve.py", 453, "def begin():"), (R3 + "r3_entry_a1.py", 96, "RS.begin()"),
                      (R3 + "r3_common.py", 405, "def write_pari_stack_json"), (R3 + "r3_check_run.py", 278, "refused_before_any_command"),
                      (R3 + "r3_check_run.py", 372, "subprocess.run(FROZEN_LAUNCHER"), (A1 + "a1_check_run.py", 133, "v2_rc = V2CHK.main(rd)"),
                      (A1 + "a1_check_run.py", 136, "v2_check_run (unchanged, plan redirected)")):
        cite(R, rel, n, s)
    ladder = {}
    for r in rd_json(EXP_REL + "/implementation/ladder.json"):
        ladder[str(r["p"])] = {sh: (r["curves"][sh] or {}).get("b_is_square_in_Fq") for sh in ("ecgfp5_shaped", "random_2torsion", "random_no2torsion")}
    cite(R, V2 + "v2_arms.py", 165, "b_sq = F.is_square(b)")
    per_outcome = {}
    for o in OUTCOMES:
        disp = []
        for it in items:
            k = item_key(it)
            if it["checker"] == "reg1":
                d = "not applied to this package: r3_reg1 compares G1 with RUN-GFPN-ac4487 at the ADMISSION of later packages (r3_run_wrapper 285-287); its recorded verdict is read by r3_check_run 327-334"
            elif k in o["exceptions"]:
                d = o["exceptions"][k]
            elif k in EXC_COMMON:
                d = EXC_COMMON[k]
            elif it["checker"] == "a1" and o["id"] in ("Z-F4", "Z-G12"):
                d = "not applied: a v2-r3 package is checked by v2_check_run (r3_check_run 371)"
            else:
                d = LAUNCH_INDEPENDENT
            disp.append({"item": k, "function": it["function"], "text": it["text"], "disposition": d})
        failing = [x for x in disp if x["disposition"].startswith("FAILS")]
        per_outcome[o["id"]] = {"kinds": o["kinds"], "what": o["what"], "recorded_as": o["recorded_as"],
                                "sufficient_conditions": o.get("sufficient_conditions"),
                                "frozen_lines": ["%s:%d" % (os.path.basename(a), b) for a, b, _c in o["frozen_lines"]],
                                "items_failing": [x["item"] for x in failing], "items_failing_conditionally":
                                    [x["item"] for x in failing if " if " in x["disposition"]],
                                "every_item": disp}
    zl_output = {"v2r3_package": ["<rd>: FAIL; [<notes>]", "  - no child RLIMIT_AS read-back recorded"],
                 "a1r3_package": ["v2_check_run (unchanged, plan redirected): FAIL", "<rd>: FAIL; [<notes>]",
                                  "  - no child RLIMIT_AS read-back recorded", "<rd>: addendum checks PASS"],
                 "archived_instance": "RUN-GFPN-bfe956 (f1fb0e post-run receipt r3_checker_outputs_verbatim): frozen checker FAIL rc=1 with the single item line '  - no child RLIMIT_AS read-back recorded' and header '<rd>: FAIL; ['7/7 certificates re-verify independently']'; r3 checks PASS"}
    only_zl = [o for o, v in per_outcome.items() if v["items_failing"] == [ZL]]
    other_fail = {o: [i for i in v["items_failing"] if i != ZL] for o, v in per_outcome.items() if [i for i in v["items_failing"] if i != ZL]}
    reading = {"draft_condition": "for every zero-launch outcome, the list of failing items is EXACTLY the one item RK-3 (b) (iv) names (v2_check_run.py 66-67). Another item failing by design on a zero-launch outcome makes the draft NOT approvable as written.",
               "outcomes_with_exactly_the_ZL_item": only_zl, "outcomes_with_other_failing_items": other_fail,
               "stated": ("On the zero-call outcomes the frozen driver logic produces (Z-C5, Z-F4, Z-G12) and on W-1, the failing items are exactly "
                          "v2_check_run.py 66-67. On W-2 (an entry refusal before any command, recorded by the wrapper) other items fail: "
                          "r3_check_run.py 167, 279, 305, 308 and at least one read-back item. Whether W-1 and W-2 are 'correctly recorded "
                          "outcomes' in the draft's sense is not decided here (L-13).")}
    return {"ladder_b_is_square_in_Fq_as_recorded": ladder, "package_kinds": kinds, "checker_items": items, "checker_exit_points": other, "zero_call_outcomes": per_outcome,
            "kinds_without_a_zero_call_outcome_from_driver_logic": [{"kind": k["kind"], "why": k["why"]} for k in NO_ZERO_CALL_KINDS],
            "zl_output_shape": zl_output, "reading": reading}


# =================================================================================================== RKR-4
X_COVERAGE = {"X-01": "RB-4 (by name: G1..G4)", "X-02": "RB-4 (by name: the controls_a1 image)",
              "X-03": "RK-3 (a) BY NAME: 'G1 read by REG-1 at the admission of every package after G1, G3 and G4 included'; the X-03 reference (RUN-GFPN-ac4487) is named NOT covered by design",
              "X-04": "RK-3 (a) BY NAME: 'every `requires` entry, subject to (d)'", "X-05": "named NOT covered by design (R-12's failure_class read)",
              "X-06": "named NOT covered by design (existence and count only)", "X-07": "RK-3 (a) BY NAME (_load_build)",
              "X-08": "RK-3 (a) BY NAME (_prior_cells, _condition_met)", "X-09": "RK-3 (a) BY NAME (cmd_aggregate)",
              "X-10": "RK-3 (a) BY NAME (cmd_aggregate_a1)", "X-11": "RK-3 (a) BY NAME (v2_common.resolve_replacement, a1_driver._resolve: the contingency manifests)",
              "X-12": "named NOT covered by design (archived RUN-GFPN-61bba9, outside the r4 lineage, bound by hash)"}
READ_LINES = {  # every run-directory read line in the command modules and the r3 wrapper -> X id
    V2 + "v2_driver.py": {642: "X-12", 683: "X-12", 700: "X-12", 993: "X-11", 995: "X-07", 1009: "X-11", 1010: "X-08", 1253: "X-11", 1256: "X-09", 1269: "X-11",
                          1314: "not a read (writes the list of run ids into its own raw)"},
    V2 + "v2_common.py": {81: "X-11"},
    A1 + "a1_driver.py": {239: "X-10", 248: "X-11", 283: "X-11", 286: "X-10", 291: "X-11", 294: "X-10", 295: "X-10", 321: "X-11",
                          375: "not a read (writes the list of run ids into its own raw)"},
    R3 + "r3_run_wrapper.py": {98: "X-01/X-02 (_raw)", 108: "X-05 (_manifest)", 156: "X-03", 157: "X-03", 159: "X-03 reference", 177: "X-01", 192: "X-02",
                               202: "X-04", 218: "X-05", 226: "X-05", 273: "X-06", 274: "X-06 (the R-3 message)", 300: "X-06", 305: "X-06",
                               433: "not a read of another package (its own run directory)"},
}
READ_PAT = re.compile(r'"runs"|\bRUNS\b|RUNS_DIR|ARCHIVED_ANCHOR_RUN|_raw\(|_manifest\(|resolve_replacement\(|\b_resolve\(|_load_raw\(')


def rkr4(succ):
    R = "RKR-4"
    a = succ["RLR-4"]["a"]
    carried = {"source": SUCC_JSON_REL, "X_table_canonical_sha256": sha_bytes(json.dumps(a["a_reads"], sort_keys=True).encode()),
               "outside_scope_canonical_sha256": sha_bytes(json.dumps(a.get("a_reads_outside_the_card_scope"), sort_keys=True).encode()),
               "bindings_canonical_sha256": sha_bytes(json.dumps(a.get("a_archived_package_bindings"), sort_keys=True).encode()),
               "md_lines": "readbackfull-census.md 436-468", "ids": [x["id"] for x in a["a_reads"]]}
    # scan for run-directory reads and map to X ids
    found, unmapped = [], []
    for rel in (V2 + "v2_driver.py", V2 + "v2_common.py", V2 + "v2_lift.py", V2 + "v2_solver.py", V2 + "v2_child.py", V2 + "v2_scoring.py",
                A1 + "a1_driver.py", A1 + "a1_health.py", A1 + "a1_pari.py", A1 + "a1_reading.py", A1 + "a1_common.py",
                R3 + "r3_entry_v2.py", R3 + "r3_entry_a1.py", R3 + "r3_resolve.py", R3 + "r3_common.py", R3 + "r3_run_wrapper.py"):
        for i, ln in enumerate(rd_text(rel).splitlines(), 1):
            s = ln.strip()
            if s.startswith("#") or not READ_PAT.search(ln):
                continue
            if re.match(r"^(def |[A-Z_0-9]+ *=)", s) or s.startswith(('"""', "usage")):
                continue
            x = READ_LINES.get(rel, {}).get(i)
            rec = {"file": os.path.basename(rel), "line": i, "text": s[:140], "maps_to": x}
            (found if x else unmapped).append(rec)
    further = [{"id": "X-13", "reader": "a1_check_run.py 79-84 (addendum_checks), a CHECKER item", "package_kind_read": "the controls_a1 image (plan gate addendum_blocking_package)",
                "field": "raw-result.json run_status, gate_pass", "covered_by_name": "neither RB-4 nor RK-3 (a) names this checker read; RB-4 names the package it reads (the controls_a1 image, X-02)",
                "note": "listed by the successor census as outside the card scope; RKR-4 (a) covers reads 'by any command of either plan or by the r3 wrapper', and this reader is neither"}]
    cite(R, A1 + "a1_check_run.py", 79, 'if pk.get("controls_a1_gate_required"):')
    cite(R, A1 + "a1_check_run.py", 83, 'r.get("run_status") != "completed_valid"')
    # (b) per kind read and outcome (dispositions by hand)
    B = [
        {"kind": "G1..G4 (X-01, X-03, X-04)", "outcome": "completed_valid, gate_pass true, frozen checker exit 0, r4 checks pass", "verdict": "PASS", "infrastructure_launch": None},
        {"kind": "G1..G4", "outcome": "any other (including a zero-call Z-G12 fixture refusal)", "verdict": "FAIL (RK-3 (b) (i): PASS_ZL never applies to G1..G4); a gate failure stops the lineage by design (RB-4)", "infrastructure_launch": "not the basis of the stop"},
        {"kind": "controls_a1 image (X-02)", "outcome": "as G1..G4", "verdict": "PASS, or FAIL (never PASS_ZL); a failure ends the addendum at its gate by design", "infrastructure_launch": "not the basis"},
        {"kind": "fixture4 F-4 (X-04 only: build 4111 requires it)", "outcome": "launched, >= 1 pair collected", "verdict": "PASS if the other items pass", "infrastructure_launch": None,
         "note": "RK-3 (d): admitted by R-8's existence test only; its verdict gates nothing"},
        {"kind": "fixture4 F-4", "outcome": "Z-F4 (rescaling refused; failed / specification_error; zero call)", "verdict": "PASS_ZL (only the ZL item fails)", "infrastructure_launch": False},
        {"kind": "build (X-07, X-04)", "outcome": "rows ok / refused / failed with >= 1 created child whose pair is collected (completed_valid or failed)", "verdict": "PASS (the frozen checker's 53 accepts failed; 66-70 pass)", "infrastructure_launch": "may be present; not read by PASS"},
        {"kind": "build", "outcome": "every launch refused before fork, or every created child without a pair", "verdict": "FAIL (ZL item; launch_records non-empty, so not PASS_ZL)", "infrastructure_launch": True,
         "note": "RK-3 (c) designed stop"},
        {"kind": "cells m = 5 (X-08, X-09, X-10, X-04)", "outcome": "measured / not_measured with >= 1 pair collected", "verdict": "PASS", "infrastructure_launch": "may be present; not read by PASS"},
        {"kind": "cells m = 5", "outcome": "Z-C5 (zero call; completed_valid, or failed / resource_exhaustion when a cell is 'invalid')", "verdict": "PASS_ZL", "infrastructure_launch": False},
        {"kind": "cells m = 5 and m = 4", "outcome": "every target refused before fork, or no created child with a pair", "verdict": "FAIL", "infrastructure_launch": True, "note": "RK-3 (c) designed stop"},
        {"kind": "cells m = 4 (X-09, X-10, X-04)", "outcome": "measured / not_measured / not_attempted / refused with >= 1 pair (the raw cell always launches)", "verdict": "PASS", "infrastructure_launch": "may be present"},
        {"kind": "aggregate v2 (X-10)", "outcome": "its figures (zero call; kind aggregate exempt at 65)", "verdict": "PASS (exit 0)", "infrastructure_launch": False},
        {"kind": "contingency (X-11)", "outcome": "as the kind replaced", "verdict": "as the kind replaced", "infrastructure_launch": "as the kind replaced"},
        {"kind": "every kind read", "outcome": "W-1 (driver ended before any launch without raw-result.json; wrapper records failed / infrastructure_error; for an aggregate the wrapper's raw has no kind, so 65 does not exempt it)", "verdict": "PASS_ZL (only the ZL item fails)", "infrastructure_launch": False,
         "note": "RK-3 (b) reads no run_status or failure_class"},
        {"kind": "every kind read", "outcome": "W-2 (entry refused before any command; wrapper records failed / infrastructure_error)", "verdict": "FAIL (several items)", "infrastructure_launch": False,
         "note": "a FAIL WITHOUT an infrastructure launch; RK-3 (c) does not apply; RL-4 refuses the dependant (a stop that RK-3 (c) does not name as designed)"},
    ]
    cite(R, V2 + "v2_driver.py", 1009, "run = C.resolve_replacement(C.load_plan(), run)")
    cite(R, V2 + "v2_driver.py", 1013, 'json.load(open(rp)).get("cells", [])')
    cite(R, V2 + "v2_driver.py", 1122, 'return False, "no m = 5 cell for %s in the prior package"')
    cite(R, V2 + "v2_driver.py", 998, 'data = json.load(open(rp))')
    cite(R, V2 + "v2_driver.py", 999, 'for r in data["polynomials"]:')
    # (c) non-blocking declarations
    plans = {}
    for pr in ("trial-plan-v2.json", "trial-plan-v2-a1.json", "trial-plan-v2-r3.json", "trial-plan-v2-a1-r3.json"):
        rel = EXP_REL + "/" + pr
        doc = rd_json(rel)
        lines = rd_text(rel).splitlines()
        texts = []

        def walk(o, path):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, path + "/" + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, path + "[%d]" % i)
            elif isinstance(o, str) and re.search(r"(?i)\bnot\s+blocking\b|non-?blocking", o):
                ln = next((i for i, t in enumerate(lines, 1) if json.dumps(o)[1:-1][:60] in t), None)
                texts.append({"json_path": path, "line": ln, "text": o})
        walk(doc, "")
        bf = [{"order": p.get("order"), "run_id": p["run_id"], "kind": p["kind"], "blocking": p.get("blocking")} for p in doc["packages"]]
        plans[pr] = {"texts_declaring_not_blocking": texts, "n_packages": len(bf),
                     "blocking_field_false": [x["run_id"] for x in bf if x["blocking"] is False],
                     "blocking_field_true": [x["run_id"] for x in bf if x["blocking"] is True]}
    f4 = {"trial-plan-v2.json": "RUN-GFPN-a07776", "trial-plan-v2-r3.json": "RUN-GFPN-596fb2"}
    requires_f4 = {}
    for pr, fid in f4.items():
        doc = rd_json(EXP_REL + "/" + pr)
        requires_f4[pr] = [{"run_id": p["run_id"], "kind": p["kind"], "driver_args": p.get("driver_args")} for p in doc["packages"] if fid in (p.get("requires") or [])]
    # does build's command read any of F-4's recorded content? static scan of cmd_build and its static callees
    t = parse(V2 + "v2_driver.py")
    Fd = funcs(t)
    Cd = classes(t)
    names = ["cmd_build", "build_poly", "child_job", "field_spec", "curve_spec", "finish", "_slim"]
    toks = []
    for nm in names:
        for n in ast.walk(Fd[nm][0]):
            s = None
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and ("runs" == n.value or n.value.startswith("RUN-GFPN")):
                s = repr(n.value)
            if isinstance(n, ast.Attribute) and n.attr in ("EXP_DIR", "ARCHIVED_ANCHOR_RUN", "resolve_replacement", "RUNS_DIR"):
                s = ast.unparse(n)
            if s:
                toks.append("%s:%d %s" % (nm, n.lineno, s))
    for n in ast.walk(Cd["Ctx"]):
        if isinstance(n, ast.Attribute) and n.attr in ("EXP_DIR", "ARCHIVED_ANCHOR_RUN", "resolve_replacement"):
            toks.append("Ctx:%d %s" % (n.lineno, ast.unparse(n)))
    cite(R, EXP_REL + "/trial-plan-v2.json", 78, '"F-4": "package 5 runs after the gate and is NOT blocking"')
    cite(R, EXP_REL + "/trial-plan-v2-r3.json", 506, '"F-4": "package 5 runs after the gate and is NOT blocking"')
    cite(R, EXP_REL + "/trial-plan-v2.json", 263, "(NOT blocking)")
    cite(R, EXP_REL + "/trial-plan-v2-r3.json", 712, "(NOT blocking)")
    cite(R, R3 + "r3_run_wrapper.py", 216, 'if tgt.get("blocking"):')
    cite(R, R3 + "r3_run_wrapper.py", 529, '"blocking"')
    cite(R, V2 + "v2_driver.py", 532, '"blocking": False')
    cite(R, V2 + "v2_driver.py", 96, 'C.CACHE_DIR if spec.get("to_cache") else cd')
    cite(R, V2 + "v2_driver.py", 548, "build_poly(ctx, F, E, arm, 4")
    reading = {
        "draft_condition": "(a) every read ... is covered BY NAME by RB-4 or RK-3 (a), or is one RK-3 (a) names as not covered by design; (b) for every package kind so read and every correctly recorded outcome a dependant's frozen logic acts on, the verdict is PASS or PASS_ZL, OR the outcome contains an infrastructure launch; (c) F-4 is the ONLY package ... that a gate rule or label declares non-blocking, and the package that names F-4 in `requires` reads none of F-4's recorded content.",
        "a": "X-01..X-12 each covered by name or named not covered by design (table); the RKQ-2 (g) diff is empty; the scan maps every run-directory read line of the command modules and the r3 wrapper to X-01..X-12 (unmapped lines listed). Further read found: X-13, a CHECKER item (a1_check_run 79-84), named by neither RB-4 nor RK-3 (a).",
        "b": "Every listed outcome has verdict PASS or PASS_ZL, or is FAIL with an infrastructure launch, EXCEPT: W-2 (an entry refusal before any command): FAIL without an infrastructure launch; and G1..G4 / the controls_a1 image outside PASS / the RB-4 gate stop. Whether W-2 is a 'correctly recorded outcome a dependant's frozen logic acts on' is not decided here (L-13); if admitted, the m = 4 package's _prior_cells would read it as having no m = 5 cell (1013, 1122).",
        "c": "By gate rule and by label text, F-4 is the only package declared not blocking (trial-plan-v2.json 78, 263; trial-plan-v2-r3.json 506, 712); the a1 plans declare none. One further text matches: the `content` field of package 3 (G3, anchor-identity; blocking true) in trial-plan-v2.json (239) and trial-plan-v2-r3.json (688) ends 'wall-clock ratio vs 17.01 s reported NON-BLOCKING': it declares a reported figure non-blocking, not a package. The boolean field `blocking` is false on every non-gate package of the v2-lineage plans and on every a1 package except controls_a1; the r3 wrapper reads that field only as 'is a gate package' (R-12, 216). The package naming F-4 in `requires` is build 4111 (RUN-GFPN-1ad09b; RUN-GFPN-596fb2's successor RUN-GFPN-c8f179); cmd_build and its static callees reference no run directory, EXP_DIR or run id: it reads none of F-4's recorded content."}
    return {"a_carried": carried, "a_coverage_by_name": X_COVERAGE, "a_scan_mapped": found, "a_scan_unmapped": unmapped, "a_further_reads": further,
            "b_outcomes": B, "c_plans": plans, "c_packages_requiring_F4": requires_f4, "c_cmd_build_run_directory_references": toks,
            "reading": reading}


# =================================================================================================== RKR-6
def rkr6():
    R = "RKR-6"
    W = R3 + "r3_run_wrapper.py"
    t = parse(W)
    F = funcs(t)
    pf, la, mn = F["preflight"][0], F["launch"][0], F["main"][0]
    sets = []
    for n in ast.walk(pf):
        if isinstance(n, ast.Assign):
            for x in n.targets:
                for y in ast.walk(x):
                    if isinstance(y, ast.Subscript) and isinstance(y.value, ast.Name) and y.value.id == "info":
                        sets.append({"line": n.lineno, "key": ast.unparse(y.slice)})
                if isinstance(x, ast.Tuple):
                    for e in x.elts:
                        if isinstance(e, ast.Name) and e.id == "info":
                            sets.append({"line": n.lineno, "key": "(tuple) " + ast.unparse(n.value)[:60]})
    init = [n for n in ast.walk(pf) if isinstance(n, ast.Assign) and any(isinstance(x, ast.Tuple) and "info" in ast.unparse(x) for x in n.targets)]
    early_returns = [{"line": n.lineno, "value": ast.unparse(n.value)[:80]} for n in ast.walk(pf) if isinstance(n, ast.Return)]
    reads = []
    for n in ast.walk(la):
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == "info":
            reads.append({"line": n.lineno, "key": ast.unparse(n.slice)})
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == "info":
            reads.append({"line": n.lineno, "key": ast.unparse(n.args[0]) if n.args else None, "via": n.func.attr})
    for n, s in ((68, "RUNS = R.RUNS_DIR"), (231, "def preflight(rid, replaces=None):"), (233, 'ref, info = [], {"rid": rid, "replaces": replaces}'),
                 (241, "try:"), (244, "return ref + ["), (245, 'info["plans"] = P'), (253, 'info["plan_key"] = which'), (270, "if pk is None:"),
                 (273, "if os.path.exists(os.path.join(RUNS, rid)):"), (276, "tree_check(\"R-4\""), (278, "tree_check(\"R-6\""), (279, 'info["reg1"] = None'),
                 (282, "need_gate = "), (284, "r7_gate_packages(gate_ids, ref)"), (285, "if rid != gate_ids[0]:"), (286, 'info["reg1"] = reg1(P)'),
                 (287, "r7_reg1_verdict"), (288, 'pk.get("controls_a1_gate_required")'), (290, "r8_requires(pk, by_id, ref)"),
                 (292, 'plan.get("watchdogs") != P["v2"].get("watchdogs")'), (295, "others = V.other_solver_processes()"),
                 (299, "all_ids ="), (309, 'pk["kind"] == "contingency"'), (319, 'plan.get("protocol_version") != want_label'), (322, "refuse_forbidden_ids(plan, ref)"),
                 (323, 'info["pk"], info["plan"] = pk, plan'), (324, "return ref, info"), (403, "def main(argv=None):"), (412, "refusals, info = preflight(rid, replaces)"),
                 (413, "if refusals:"), (416, "return 2"), (420, "return launch(rid, replaces, info)"), (423, "def launch(rid, replaces, info):"),
                 (424, 'P, plan, pk, which = info["plans"], info["plan"], info["pk"], info["plan_key"]'), (431, "entry = ENTRY_V2 if which == \"v2r3\" else ENTRY_A1"),
                 (433, "rd = os.path.join(RUNS, rid)"), (434, "cmd = [sys.executable, \"-B\", entry] + list(driver_args)"), (462, 'info["amendment_sha256"]'),
                 (472, "child_env = dict(os.environ, GFPN_RUN_DIR=rd, GFPN_V2_PACKAGE=rid"), (477, "proc = subprocess.run(cmd, cwd=R.REPO, env=child_env"),
                 (565, 'if info.get("reg1") is not None:'), (566, 'run["gate"] = {"regression_REG-1": info["reg1"]}'),
                 (156, "cand = os.path.join(RUNS, g1)"), (158, 'return {"verdict": "NOT_EVALUABLE"'), (159, "ref = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN)"),
                 (179, 'ref.append("R-7 repaired gate package %s has not run" % g)'), (187, 'ref.append("R-7 REG-1 did not pass'), (203, 'ref.append("R-8 required earlier package')):
        cite(R, W, n, s)
    # (b) development world per command (dispositions by hand)
    plan_v2r3 = rd_json(EXP_REL + "/trial-plan-v2-r3.json")
    plan_a1r3 = rd_json(EXP_REL + "/trial-plan-v2-a1-r3.json")
    byid = {p["run_id"]: p for p in plan_v2r3["packages"]}
    byid_a1 = {p["run_id"]: p for p in plan_a1r3["packages"]}
    G = plan_v2r3["gate"]["blocking_packages"]
    ctl, anc, ca1 = byid[G[3]], byid[G[2]], byid_a1[plan_a1r3["gate"]["addendum_blocking_package"]]
    pk_facts = {"controls": {"run_id": ctl["run_id"], "gate_required": ctl.get("gate_required"), "requires": ctl.get("requires")},
                "anchor-identity": {"run_id": anc["run_id"], "gate_required": anc.get("gate_required"), "requires": anc.get("requires")},
                "controls-a1": {"run_id": ca1["run_id"], "plan": "a1r3", "controls_a1_gate_required": ca1.get("controls_a1_gate_required"),
                                "requires": ca1.get("requires"), "p": ca1.get("p")}}
    EXPECTED = "expected (RK-4 (a) lists it)"
    pred = []
    for cmd in ("controls", "anchor-identity", "controls-a1"):
        f = pk_facts[cmd]
        rows = [{"predicate": "R-1 (234-240)", "refusal": None, "why": "the amendment files are unchanged"},
                {"predicate": "R-2 (257-271)", "refusal": None, "why": "the development label is reserved in the development copy the redirected plan path names, and is none of the v1 / v2 / a1 / r1 / r2 / retired ids"},
                {"predicate": "R-3 (273-274)", "refusal": None, "why": "no directory of the label under the redirected RUNS"},
                {"predicate": "R-4, R-5 (276-277)", "refusal": None, "why": "implementation-v2/ and -v2-a1/ equal their receipts and are clean (RKQ-2 (f), (g))"},
                {"predicate": "R-6 (278)", "refusal": None, "why": "for the r3 wrapper as written, implementation-v2-r3/ equals the f1fb0e phase-A receipt; see note N-2 for the r4 analogue at stage time"}]
        if cmd == "controls-a1":
            rows.append({"predicate": "R-7 gate packages (282-284)", "refusal": "4 x 'R-7 repaired gate package <G> has not run' (need_gate: every a1r3 package)", "status": EXPECTED})
        else:
            rows.append({"predicate": "R-7 gate packages (282-284)", "refusal": None, "why": "need_gate is false: v2r3 and gate_required %s" % f["gate_required"]})
        rows.append({"predicate": "R-7 REG-1 (285-287; reg1 153-162)", "refusal": "'R-7 REG-1 did not pass (NOT_EVALUABLE): G1 <G1> has not run' (G1 absent under the redirected RUNS)", "status": EXPECTED})
        if cmd == "controls-a1":
            rows.append({"predicate": "R-7 controls_a1 image (288-289)", "refusal": None, "why": "the controls_a1 package's own controls_a1_gate_required is %s" % f["controls_a1_gate_required"]})
        rows.append({"predicate": "R-8 (290; 199-203)", "refusal": ("'R-8 required earlier package %s ... has no manifest'" % f["requires"][0]) if f["requires"] else None,
                     "status": EXPECTED if f["requires"] else None, "why": None if f["requires"] else "requires is empty"})
        rows += [{"predicate": "R-9 (292-293)", "refusal": None, "why": "the development copy's watchdogs equal trial-plan-v2.json's"},
                 {"predicate": "R-10 (295-297)", "refusal": "only if another solver-like process runs on the host at that moment", "status": "NOT in RK-4 (a)'s list: a host-state refusal would be a STOP as RK-4 (a) words it"},
                 {"predicate": "R-11 (299-307)", "refusal": None, "why": "no directory of the eight plans' ids under the redirected RUNS"},
                 {"predicate": "R-12 (309-312)", "refusal": None, "why": "not a contingency; no --replaces"},
                 {"predicate": "R-13 (314-322)", "refusal": None, "why": "the development copy keeps protocol_version, the repair block and task_id; the label carries no forbidden id"},
                 {"predicate": "RB-4 / RL-4 / RK-3 (r4 only)", "refusal": "for controls-a1: RB-4 (b) on G1..G4; for controls / anchor-identity: RL-4 on the `requires` entry", "status": EXPECTED}]
        pred.append({"command": cmd, "package": f, "predicates": rows})
    # (c) reads of the run id by the three frozen commands
    rid_reads = [
        {"where": "v2_driver.py 55-58 (Ctx.__init__)", "use": "run_dir() = GFPN_RUN_DIR (v2_common 97-101); run_id() = its basename (104-105); plan_package(plan, rid) looks up the package in v2_common.PLAN_PATH's plan", "commands": ["controls", "anchor-identity", "controls-a1 (a1_driver 57 D.Ctx())"], "class": "look up its package; name its directory"},
        {"where": "v2_driver.py 59-62", "use": "contingency only: the package becomes the replaced one with run_id = rid", "commands": ["contingency runs"], "class": "look up"},
        {"where": "v2_driver.py 78 (finish)", "use": "raw['package'] = ctx.pkg: the plan package, whose run_id field is the label", "commands": ["controls", "anchor-identity", "controls-a1 (D.finish, a1_driver 215)"], "class": "copied into raw-result.json (a written copy of the looked-up package)"},
        {"where": "v2_driver.py 252 -> v2_lift.py 220", "use": "make_certificate(..., ctx.rid, ...) writes \"run_id\": <label> into every certificate", "commands": ["controls (lift_and_certify 842)", "controls-a1 (a1_driver 167)"], "class": "WRITTEN INTO CERTIFICATE CONTENT (not a lookup and not the directory name); v2_verify_independent does not read it"},
        {"where": "r3_run_wrapper.py 433, 472, 469-471, 515, 528", "use": "the wrapper: run directory, GFPN_RUN_DIR / GFPN_V2_PACKAGE, command.txt, manifest id, derived_from = id_map inverse of the label (None)", "commands": ["wrapper, not a frozen command"], "class": "wrapper"},
    ]
    for rel, n, s in ((V2 + "v2_driver.py", 55, "self.rd = C.run_dir()"), (V2 + "v2_driver.py", 56, "self.rid = C.run_id()"), (V2 + "v2_driver.py", 58, "C.plan_package(self.plan, self.rid)"),
                      (V2 + "v2_driver.py", 62, "run_id=self.rid"), (V2 + "v2_driver.py", 78, 'raw.setdefault("package", ctx.pkg)'), (V2 + "v2_driver.py", 252, "ctx.rid"),
                      (V2 + "v2_lift.py", 220, '"run_id": run_id'), (V2 + "v2_driver.py", 842, "lift_and_certify("), (A1 + "a1_driver.py", 57, "ctx = D.Ctx()"),
                      (A1 + "a1_driver.py", 167, "D.lift_and_certify("), (V2 + "v2_common.py", 105, "return os.path.basename(run_dir().rstrip(\"/\"))"),
                      (V2 + "v2_common.py", 32, 'PLAN_PATH = os.path.join(EXP_DIR, "trial-plan-v2.json")'), (R3 + "r3_entry_v2.py", 45, "C.PLAN_PATH = R.PLAN_V2_R3"),
                      (R3 + "r3_entry_a1.py", 58, "AC.PLAN_A1_PATH = R.PLAN_A1_R3"), (R3 + "r3_check_run.py", 53, "C.PLAN_PATH = R.PLAN_V2_R3"),
                      (R3 + "r3_check_run.py", 37, "FROZEN_LAUNCHER = [sys.executable")):
        cite(R, rel, n, s)
    vi_reads_run_id = "run_id" in rd_text(V2 + "v2_verify_independent.py")
    # (d) redirections the r3 development checks made, by ast (every attribute assignment / setattr in the r3 dev-check files)
    red = []
    for f in ("r3_dv7.py", "r3_dv12.py", "r3_dv16.py", "r3_dv6.py", "r3_devchecks.py", "r3_devchecks_more.py"):
        tt = parse(R3 + f)
        for n in ast.walk(tt):
            tg = n.targets if isinstance(n, ast.Assign) else ([n.target] if isinstance(n, ast.AugAssign) else [])
            for x in tg:
                for y in ast.walk(x):
                    if isinstance(y, ast.Attribute) and isinstance(y.value, ast.Name) and y.value.id in ("W", "R", "C", "AC", "K", "a1_toy", "RS", "REG"):
                        red.append({"file": f, "line": n.lineno, "target": ast.unparse(y), "value": ast.unparse(n.value)[:90]})
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "setattr":
                red.append({"file": f, "line": n.lineno, "target": "setattr(%s)" % ", ".join(ast.unparse(a) for a in n.args[:2]), "value": ast.unparse(n.args[2])[:60] if len(n.args) > 2 else None})
    for rel, n, s in ((R3 + "r3_dv7.py", 468, "W.git_tree_state = lambda paths"), (R3 + "r3_dv7.py", 469, 'W.ENTRY_V2 = W.ENTRY_A1 = shims["entry_toy.py"]'),
                      (R3 + "r3_dv7.py", 470, '"PLAN_V2_R3": env["plan_v2r3"]'), (R3 + "r3_dv7.py", 473, "setattr(R, k, v)"),
                      (R3 + "r3_dv7.py", 480, "R.RUNS_DIR, R.RECEIPT_V2_PHASE_B = reg_runs, reg_receipt"), (R3 + "r3_dv7.py", 481, 'W.RUNS = os.path.join(worlds[w], "runs")'),
                      (R3 + "r3_dv7.py", 486, "rc = W.main([rid])"), (R3 + "r3_dv7.py", 570, "K.FROZEN_LAUNCHER = [sys.executable"),
                      (R3 + "r3_dv7.py", 174, "C.LADDER_PATH = ladder_path"), (R3 + "r3_dv7.py", 230, "for k, v in CFG[\"R\"].items():"), (R3 + "r3_dv7.py", 231, "setattr(R, k, v)"),
                      (R3 + "r3_dv7.py", 299, 'for k, v in CFG["mods"].get(_n, {}).items():'), (R3 + "r3_dv7.py", 300, "setattr(module, k, v)"),
                      (R3 + "r3_dv7.py", 314, "module.run_child = run_child"), (R3 + "r3_dv7.py", 342, 'runpy.run_path(entry, run_name="__main__")'),
                      (R3 + "r3_dv7.py", 401, '"mods": {"v2_common": {"EXP_DIR": world_exp, "LADDER_PATH": env["ladder"]'),
                      (R3 + "r3_dv7.py", 402, '"a1_common": {"EXP_DIR": world_exp, "RUNS_DIR"'),
                      (R3 + "r3_dv12.py", 111, "W.git_tree_state = lambda paths"), (R3 + "r3_dv12.py", 113, 'W.ENTRY_V2 = W.ENTRY_A1 = shims["entry_toy.py"]'),
                      (R3 + "r3_dv12.py", 122, "setattr(R, k, v)"), (R3 + "r3_dv12.py", 146, '"mods": {"v2_common": {"EXP_DIR": exp'),
                      (R3 + "r3_dv12.py", 149, 'os.environ["R3_TOY_CFG"] = cfgp'), (R3 + "r3_dv12.py", 153, "R.RUNS_DIR = reporter.get"), (R3 + "r3_dv12.py", 156, "W.RUNS = runs"),
                      (R3 + "r3_dv12.py", 161, "rc = W.main([rid])"), (R3 + "r3_common.py", 31, "RUNS_DIR = os.path.join(EXP_DIR, \"runs\")"),
                      (R3 + "r3_common.py", 112, "PLAN_V2_R3 = os.path.join"), (R3 + "r3_common.py", 113, "PLAN_A1_R3 = os.path.join"), (R3 + "r3_common.py", 114, "LADDER_PATH = os.path.join"),
                      (V2 + "v2_common.py", 35, "LADDER_PATH = os.path.join"), (V2 + "v2_common.py", 30, "EXP_DIR = os.path.abspath")):
        cite(R, rel, n, s)
    reading = {
        "draft_condition": "(a) preflight and launch are separate functions such that launch can be invoked in a development process after a recorded preflight, and every value launch reads from `info` and where each comes from when preflight recorded refusals; (b) ... every refusal preflight records is one of the admission predicates RK-4 (a) lists as expected; (c) the development label is the ONLY plan value the development copy changes, and no frozen command reads the run id other than to look up its package and name its directory; (d) every in-process redirection RK-4 (a) needs (RUNS, the plan paths, the ladder path) exists as a module attribute the r3 development checks already redirected, with lines.",
        "a": "preflight (231-324) and launch (423-570) are separate module functions; main (403-420) calls launch only when preflight returns no refusal. launch reads info['plans'], info['plan'], info['pk'], info['plan_key'] (424), info['amendment_sha256'] (462) and info.get('reg1') / info['reg1'] (565-566). preflight sets all of them before it returns (235-240, 245, 253, 279 / 286, 323) whether or not it recorded refusals; the one exception is the early return at 244 (a plan unreadable), after which plans, plan_key, pk and plan are unset. In the development world info['reg1'] is the NOT_EVALUABLE block (158), which launch writes into the manifest (565-566); r3_check_run 327-330 then fails on a non-G1 package ('gate.regression_REG-1 not recorded PASS').",
        "b": "controls: REG-1 and R-8; anchor-identity: REG-1 and R-8; controls-a1: R-7 gate packages (x4) and REG-1. Each is one RK-4 (a) lists as expected. Two predicates can refuse outside that list: R-10 (host state, 295-297) and, for the r4 wrapper at stage time, the R-6 analogue (N-2).",
        "c": "The frozen commands read the run id to look up the package and to name the directory (Ctx 55-58), AND controls and controls-a1 write it into every certificate (v2_driver 252 -> v2_lift 220); finish() also copies the looked-up package (with the label as run_id) into raw-result.json (78). The run id reaches the frozen command only as the basename of GFPN_RUN_DIR (v2_common 104-105), and the plan it is looked up in is the ENTRY process's v2_common.PLAN_PATH (r3_entry_v2 45; r3_entry_a1 58), not the wrapper process's.",
        "d": "RUNS (r3_run_wrapper 68), the plan paths (r3_common 112-113) and the ladder path (v2_common 35; r3_common 114) are module attributes, and the r3 development checks redirected them (r3_dv7 470-473, 480-481, 174; r3_dv12 121-122, 153-156). BUT the frozen command runs in the ENTRY CHILD process (r3_run_wrapper 434, 477) and the frozen checker in its own child (r3_check_run 37, 372); the r3 checks reached those processes only by replacing W.ENTRY_V2 / W.ENTRY_A1 with a shim entry (r3_dv7 469; r3_dv12 113) and K.FROZEN_LAUNCHER (r3_dv7 570) that re-apply the redirections from R3_TOY_CFG (r3_dv7 230-231, 299-300; cfg 393-404; r3_dv12 139-149), and by replacing W.git_tree_state (r3_dv7 468; r3_dv12 111). RK-4 (a) names in-process redirection only; it names neither the child-process redirection nor these replacements."}
    notes = {"N-1": "In-process redirection in the wrapper process does not reach the entry child (a new interpreter, r3_run_wrapper 477): without a child-side redirection, the entry loads the real plan (r3_entry_v2 45) and Ctx's plan_package raises KeyError on the label (v2_common 69-73), an outcome of class W-1.",
             "N-2": "DV-18 runs during the r4 stage 'before the stage writes its bundle' (readbackcover RB-5), i.e. before the r4 phase-A archive. The r3 wrapper's R-6 compares its own tree with its phase-A receipt (276-278; tree_check 114-139); an r4 analogue would find no receipt and untracked files at that time. The r3 checks handled their R-6 by a synthetic receipt and a replaced git_tree_state (r3_dv12 111, 118-122). This is an inference about unwritten r4 code from the r3 base (L-14).",
             "N-3": "reg1() reads the REG-1 reference through R.RUNS_DIR (159), not RUNS: with only RUNS redirected the reference is still the archived RUN-GFPN-ac4487; the candidate G1 is looked up under RUNS (156).",
             "N-4": "The development package's own frozen checker (v2_check_run 41-45 in r3_check_run's child, 53) looks the label up in the real r3 plan unless that child is redirected too ('run id not reserved in trial-plan-v2.json').",
             "v2_verify_independent_reads_run_id": vi_reads_run_id}
    return {"a_info_keys_set_by_preflight": sets, "a_preflight_returns": early_returns, "a_launch_reads_info": reads,
            "b_package_facts": pk_facts, "b_predicates_per_command": pred, "c_run_id_reads": rid_reads,
            "d_redirections_in_r3_dev_checks_by_ast": red, "notes": notes, "reading": reading}


# =================================================================================================== RKR-7
def rkr7():
    R = "RKR-7"
    fields = ("launch_records", "child_readback_accounting", "pair_read_by_parent", "readback_from", "frame_inspection", "raise_site", "child_created")
    hits = {}
    ntext = 0
    digest = hashlib.sha256()
    for root in ("tools", "harness", EXP_REL + "/implementation-v2", EXP_REL + "/implementation-v2-a1", EXP_REL + "/implementation-v2-r3"):
        for dp, _dn, fn in os.walk(os.path.join(REPO, root)):
            if "__pycache__" in dp or ".venv" in dp:
                continue
            for f in sorted(fn):
                if not f.endswith((".py", ".sh", ".yaml", ".yml", ".json", ".md", ".txt")):
                    continue
                p = os.path.join(dp, f)
                try:
                    b = open(p, "rb").read()
                except OSError:
                    continue
                ntext += 1
                digest.update(os.path.relpath(p, REPO).encode() + b"\0" + sha_bytes(b).encode() + b"\n")
                s = b.decode("utf-8", errors="replace")
                for fl in fields:
                    if fl in s:
                        hits.setdefault(fl, []).append(os.path.relpath(p, REPO))
    readers = [
        {"reader": "RL-3 collector (r4 wrapper; not written)", "reads": "launch_records: child_created, the pair; RK-2 adds readback_from and the named lists",
         "changes_what_it_computes": "YES, by design: RK-1 (a) makes child_created true on P-7 (key presence) and RK-1 (b) adds raise-path records whose pair is copied (P-14c, P-F1) to source (d); 'capped children evidenced' counts child_created true"},
        {"reader": "frozen v2_check_run 62-70 (via resources.child_rlimit_as_read_back_by_getrlimit, the RB-2 union with RL-3 (d))", "reads": "the de-duplicated pairs",
         "changes_what_it_computes": "YES where a raise-path pair is the only source of a pair: 66-67 then passes and 68-70 compares it (RK-2: 'applies to every source, the raise-frame records included')"},
        {"reader": "r4 checks: RK-3 (b) (ii), (iii) and RK-3 (c)", "reads": "launch_records emptiness; child_created, raised, pair_read_by_parent; RL-3 recorder gaps",
         "changes_what_it_computes": "new readers, by design (the verdict)"},
        {"reader": "REG-1 SE-4 (e): r3_reg1.solver_events_check 171-199 and render 321-333", "reads": "exists / parses; top-level consistency_violation; S-1 / S-2 events' consistency.ok and counters, by constant key; the whole file quoted (report only)",
         "changes_what_it_computes": "no for the verdict (launch_records are not read by key); the verbatim quote grows; RK-1 (b)'s frame_inspection 'not_found' is an SE-2 (4) violation and would set the flag (a recording failure; RK-6)"},
        {"reader": "a1_check_run addendum_checks byte sweep 51-58", "reads": "every .json / .yaml / .txt / .log of the package (solver-events.json and manifest.yaml included) for AC.FORBIDDEN_TASK_ID",
         "changes_what_it_computes": "no, unless a copied string (refusal_reason with the lock path, child_rlimit_report) contains that id; the added bytes are scanned; a hit fails the package"},
        {"reader": "r3_check_run.events_file_integrity 153-158", "reads": "whole-file sha256 of solver-events.json vs the manifest's recorded sha256", "changes_what_it_computes": "no (both sides are the same bytes)"},
        {"reader": "r3_check_run.events_file_epsilon 161-185", "reads": "constant keys (flag, K, spacing, S-1 / S-2 counters, watchdog_after_resolve)", "changes_what_it_computes": "no"},
        {"reader": "r3_check_run.forbidden_id_keys 189-211", "reads": "top-level task_id, run_card, written_by_task, archived_by of manifest / raw / pari-stack / solver-events", "changes_what_it_computes": "no (the added fields are nested)"},
        {"reader": "r3_check_run.forbidden_id_sweep 214-224", "reads": "command.txt, stdout.log, stderr.log, environment.json, pari-stack.json only", "changes_what_it_computes": "no (neither solver-events.json nor manifest.yaml is swept)"},
        {"reader": "r3_check_run.sc4_accounting 128-150", "reads": "raw-result.json solve records and health reports", "changes_what_it_computes": "no"},
        {"reader": "r3_run_wrapper.solver_events_block 381-400 and consistency_flag 573-579", "reads": "constant keys and the whole-file sha256", "changes_what_it_computes": "no (the recorded sha256 changes with the bytes)"},
        {"reader": "frozen commands, aggregates, a1 phase_b_check", "reads": "none of solver-events.json or manifest resources (successor census RLR-6)", "changes_what_it_computes": "n/a"},
    ]
    for rel, n, s in ((R3 + "r3_reg1.py", 171, "def solver_events_check(candidate):"), (R3 + "r3_reg1.py", 194, 'viol = bool(doc.get("consistency_violation")) or bool(ev_bad)'),
                      (A1 + "a1_check_run.py", 53, 'if f.endswith((".json", ".yaml", ".txt", ".log")):'), (A1 + "a1_check_run.py", 55, "AC.FORBIDDEN_TASK_ID in open("),
                      (R3 + "r3_check_run.py", 157, 'if os.path.exists(sp) and sev.get("sha256") != R.sha256_file(sp):'), (R3 + "r3_check_run.py", 45, "SWEPT_FILES = ("),
                      (R3 + "r3_check_run.py", 134, "for o in find_solver_records(raw):"), (R3 + "r3_run_wrapper.py", 510, 'collect(raw, "rlimit_as_child_getrlimit"'),
                      (V2 + "v2_check_run.py", 63, 'caps = res.get("child_rlimit_as_read_back_by_getrlimit") or []'),
                      (V2 + "v2_solver.py", 168, "host solver lock %s is held")):
        cite(R, rel, n, s)
    return {"field_names_searched": fields, "text_files_scanned": ntext, "text_scan_combined_sha256": digest.hexdigest(),
            "files_naming_a_field": hits, "readers": readers,
            "stated": "Informational. Readers that change what they compute: the RL-3 collector and the r4 checks (by design), and the frozen v2_check_run 62-70 through the collected pairs where a raise-path pair is the only source. No other listed reader changes its verdict; REG-1's verbatim quote grows and a recording failure is one more cause of its flag."}


# =================================================================================================== main
def name_self_check(paths, wordfile):
    if not wordfile:
        return {"used": False}
    raw = open(wordfile, "rb").read()
    words = [w.strip().lower() for w in raw.decode().splitlines() if w.strip() and not w.startswith("#")]
    hits = 0
    for p in paths:
        t = open(p, "rb").read().decode("utf-8", errors="replace").lower()
        for w in words:
            hits += len(re.findall(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", t))
    return {"used": True, "word_file": "<scratchpad>/rkcensus/<word list> (outside the repository)", "word_file_sha256": sha_bytes(raw),
            "files_scanned": [os.path.basename(p) for p in paths], "hits": hits}


def forbidden_ids_from_card():
    txt = rd_text(CARD_REL)
    m = re.search(r"Nothing written carries(.*?)as its own task id", txt, re.S)
    return sorted(set(re.findall(r"TASK-\d{8}-[0-9a-f]{6}", m.group(1)))) if m else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scratch-root", required=True)
    ap.add_argument("--name-words", default=None)
    a = ap.parse_args()
    SCRATCH[0] = os.path.abspath(a.scratch_root)
    doc = {"schema": "crypto.autoresearch.gfpn05.close_census.v1", "task_id": "TASK-20260924-e8da78", "experiment_id": "EXP-GFPN-05ff43",
           "draft": "AMD-EXP-GFPN-05ff43-20260924-readbackclose (DRAFT, not approved)", "ordered_by": "DEC-20260924-a789e1",
           "archived_by": "TASK-20260924-71d070",
           "statement": "Observations only. Not evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT. No D or degree is reported. No approval recommendation.",
           "started_utc": STARTED.isoformat(), "python": platform.python_version(),
           "command": redact("PYTHONDONTWRITEBYTECODE=%s %s -B %s %s" % (os.environ.get("PYTHONDONTWRITEBYTECODE"), os.path.basename(sys.executable),
                                                                        os.path.relpath(os.path.abspath(__file__), REPO), " ".join(sys.argv[1:]))),
           "cwd": redact(os.getcwd()), "dont_write_bytecode": sys.dont_write_bytecode,
           "inference": {"requested_policy": "executor-implementation", "resolved_model_id": None,
                         "resolved_model_note": "none supplied by the dispatching session; none invented", "fallback_used": False, "bedrock_used": False}}
    integ = phase1()
    doc["phase_1_integrity_RKR-5"] = integ
    doc["dp5_recheck"] = dp5()
    doc["git_children_integrity_phase_only"] = GIT_CHILDREN
    if not integ["all_ok"]:
        doc["stopped"] = "RKQ-2 integrity failed: nothing was read as a result"
        doc["files_read_sha256"] = FILES_READ
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=1, default=str)
        return 3
    install_guard()
    doc["guard"] = GUARD
    rd_text(CARD_REL)
    succ_b = rd_bytes(SUCC_JSON_REL)
    succ = json.loads(succ_b)
    rd_bytes(SUCC_MD_REL)
    for key, fn in (("RKR-1", rkr1), ("RKR-2", lambda: rkr2(succ_b, succ, integ)), ("RKR-3", rkr3), ("RKR-4", lambda: rkr4(succ)),
                    ("RKR-6", rkr6), ("RKR-7", rkr7)):
        try:
            doc[key] = fn()
        except Exception as e:                           # noqa: BLE001
            doc[key] = {"INCOMPLETE": "%s: %r" % (type(e).__name__, e)}
    doc["method_limits"] = {
        "carried": {"L-1": "RL-1 closes a raise in the CALLER after run_child returned; a raise INSIDE run_child is now read under RK-1 (b) (RKR-1 table)",
                    "L-2": "the ERR setrlimit branch takes no pair (now a NOT A BAR class of RKR-1)", "L-3": "which path occurs is a run-time fact (RKL-3)",
                    "L-4": "grandchildren not examined (RKL-1)", "L-5": "controls-a1, fixture4, build, cells and aggregate(-a1) never ran under r3; no r4 code exists: RK-1..RK-4 are read as worded",
                    "L-6": "superseded as a reading of RL-1 by RK-1; RK-1 as worded still records child_created false on P-16 and P-F2 after P-14a / P-16",
                    "L-7": "closed as worded: RK-1 (a) defines key presence", "L-8": "RKR-2 is read on the r3 entries' closure; the r4 closure is checked by DV-18 (h) at stage time",
                    "L-9": "RK-4 (b) names 1073741831; the development admission is read under RKR-6 on the r3 base", "L-10": "RKR-3 / RKR-4 (b) are static readings of the checkers; no package was run"},
        "new": {"L-11": "Interpreter behaviour (a C-level call raising after its side effect, e.g. MemoryError converting a new pid; asynchronous exceptions delivered at bytecode boundaries) is taken from the language's documented behaviour and from bytecode compiled here from source text, not from interpreter source.",
                "L-12": "The fork-child path P-C is not traced beyond run_child.",
                "L-13": "Whether the wrapper-recorded outcomes W-1 and W-2 are 'correctly recorded outcomes' in the draft's sense is not decided; they are listed with their items and verdicts.",
                "L-14": "RKR-6 reads the r3 wrapper as the base of the r4 wrapper; predicates the r4 wrapper adds or re-points (e.g. its R-6 at stage time) are inferred, not read."}}
    doc["citation_checks"] = CITES
    doc["forbidden_task_ids_source"] = "read at run time from the card's RKQ-9 text (%d ids); not embedded" % len(forbidden_ids_from_card())
    doc["files_read_sha256"] = FILES_READ
    doc["wall_seconds"] = round(time.time() - T0, 3)
    doc["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    txt = json.dumps(doc, indent=1, default=str)
    fids = forbidden_ids_from_card()
    doc["output_self_check"] = {"forbidden_task_ids_present": [f for f in fids if f in txt],
                                "scratch_path_present": SCRATCH[0] in txt}
    with open(a.out, "w") as fh:
        json.dump(doc, fh, indent=1, default=str)
    nsc = name_self_check([os.path.abspath(a.out), os.path.abspath(__file__)], a.name_words)
    doc["output_self_check"]["name_words"] = nsc
    doc["guard_final"] = {"launch_attempts": GUARD["launch_attempts"], "import_attempts": GUARD["import_attempts"]}
    with open(a.out, "w") as fh:
        json.dump(doc, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
