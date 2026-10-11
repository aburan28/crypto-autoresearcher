#!/usr/bin/env python3
"""EXP-GFPN-05ff43 -- TASK-20260924-1039eb: ZERO-RUN, ZERO-SOLVE static LAUNCH-PATH CENSUS.

Computes, from source code and archived bytes only, the pre-declared readings of the DRAFT
AMD-EXP-GFPN-05ff43-20260924-healthresolve (pre_approval_readings): CN-5 (integrity, FIRST), CN-1 (msolve launch
sites, classification, reachability), CN-2 (i)-(ix) (health-path code facts, with the no-solver .ms round trip of the
four health systems at p' = 1073741831), CN-3 (PARI inventory) and CN-4 (other child launches).

It launches NO msolve, gp, Sage, valgrind or builder child. The only child processes it starts are read-only `git`
invocations (git rev-parse / git show / git ls-files / git log) during the integrity phase; after that phase an
in-process guard replaces os.fork / os.posix_spawn / os.exec* / os.system / os.popen / subprocess.Popen by functions
that raise, so no later step (including the permitted CN-2 (vi) imports) can start a child. The guard's record is
written into census.json.

Static analysis uses the ast module; frozen modules are NOT imported, except the four names CN-2 (vi) needs
(v2_arms.write_msolve_input, v2_driver._parse_ms_file, a1_health.draw, a1_common.HEALTH_SEED), which LC-1 permits
because importing them starts no computation and no child (module-level statements are listed in census.json).

usage: python3 -B census_scan.py --out-dir <write_scope dir> --scratch <scratchpad dir>
Writes <out-dir>/census.json only. census.md is written by the Executor from census.json.
"""
import argparse
import ast
import datetime
import dis
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile

sys.dont_write_bytecode = True

TASK_ID = "TASK-20260924-1039eb"
EXP_REL = "experiments/EXP-GFPN-05ff43"
HERE = os.path.dirname(os.path.abspath(__file__))


def find_repo(start):
    d = start
    while d != "/":
        if os.path.isdir(os.path.join(d, ".git")) or os.path.isfile(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=None)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--scratch", required=True)
ARGS = ap.parse_args()
REPO = os.path.abspath(ARGS.repo or find_repo(os.getcwd()) or find_repo(HERE))
EXP = os.path.join(REPO, EXP_REL)
OUT_DIR = os.path.abspath(ARGS.out_dir)
SCRATCH = os.path.abspath(ARGS.scratch)
os.makedirs(SCRATCH, exist_ok=True)

TREES = {
    "v1": EXP_REL + "/implementation",
    "v2": EXP_REL + "/implementation-v2",
    "a1": EXP_REL + "/implementation-v2-a1",
    "r1": EXP_REL + "/implementation-v2-r1",
    "r2": EXP_REL + "/implementation-v2-r2",
}
EXTERNAL_INPUTS = {
    "k4a": "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py",
    "k5k7": "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7",
}
ARCH = "coordination/goals/GOAL-GFPN-380702/archives"
RECEIPTS = {
    "bc10a8": ARCH + "/TASK-20260924-bc10a8/snapshot-receipt.json",
    "0fa03f_phaseA": ARCH + "/TASK-20260923-0fa03f/snapshot-receipt.json",
    "4ff597_phaseA": ARCH + "/TASK-20260923-4ff597/snapshot-receipt.json",
    "53a47d": ARCH + "/TASK-20260923-53a47d/preservation-receipt.json",
    "5ca2a5": ARCH + "/TASK-20260924-5ca2a5/preservation-receipt.json",
}
HEALTHRESOLVE = EXP_REL + "/amendments/v2_addendum_healthresolve.yaml"
SEEDRESOLVE = EXP_REL + "/amendments/v2_addendum_seedresolve.yaml"
SOLVEREVENT = EXP_REL + "/amendments/v2_addendum_solverevent.yaml"
SEEDRESOLVE_SHA = "dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81"
SOLVEREVENT_SHA = "011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f"
R2_BUNDLE = EXP_REL + "/dev-evidence/stage-r2-dv/stage-r2-dv-evidence.tar.gz"
PLAN_V2 = EXP_REL + "/trial-plan-v2.json"
PLAN_A1 = EXP_REL + "/trial-plan-v2-a1.json"
PLAN_V2_R2 = EXP_REL + "/trial-plan-v2-r2.json"
PLAN_A1_R2 = EXP_REL + "/trial-plan-v2-a1-r2.json"

OUT = {"schema": "crypto.autoresearch.gfpn05.launch_census.v1", "task_id": TASK_ID, "experiment_id": "EXP-GFPN-05ff43",
       "draft_defining_the_readings": "AMD-EXP-GFPN-05ff43-20260924-healthresolve (DRAFT, not approved)",
       "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "census_children_started": [],
       "files_read": {}}


def rel(p):
    return os.path.relpath(p, REPO)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    with open(path, "rb") as fh:
        return sha_bytes(fh.read())


def git(*args):
    """Read-only git (the ONLY child processes this census starts; recorded)."""
    argv = ["git", "-C", REPO] + list(args)
    OUT["census_children_started"].append({"argv": argv, "phase": "integrity", "at": datetime.datetime.now(datetime.timezone.utc).isoformat()})
    return subprocess.run(argv, capture_output=True).stdout


def write_out(stop=None):
    OUT["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if stop:
        OUT["STOP"] = stop
    txt = json.dumps(OUT, indent=1, sort_keys=False, default=str)
    for bad in ("TASK-20260923-cd932c", "TASK-20260923-6c7f55", "TASK-20260923-3aa31e", "TASK-20260923-292052",
                "TASK-20260924-946010", "TASK-20260924-9490b1"):
        # these ids may appear only as quoted source text, never as this record's task id (LC-7)
        assert OUT["task_id"] != bad
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "census.json"), "w") as fh:
        fh.write(txt + "\n")


# =====================================================================================================================
# CN-5 / LC-2: INTEGRITY FIRST
# =====================================================================================================================
def receipt_map(path):
    d = json.load(open(os.path.join(REPO, path)))
    ps = d.get("path_sha256") or {}
    if isinstance(ps, list):
        ps = {x["path"]: x["sha256"] for x in ps}
    return d, dict(ps)


def tree_files(tree_rel):
    """Every regular file on disk under the tree (including ignored ones), sorted."""
    out = []
    for dp, dn, fn in os.walk(os.path.join(REPO, tree_rel)):
        dn.sort()
        for f in sorted(fn):
            out.append(rel(os.path.join(dp, f)))
    return sorted(out)


def integrity():
    res = {"checks": [], "pass": True}

    def chk(name, path, expected, actual, source):
        ok = expected is not None and expected == actual
        res["checks"].append({"check": name, "path": path, "expected_sha256": expected, "actual_sha256": actual,
                              "expected_from": source, "equal": ok})
        if not ok:
            res["pass"] = False
        return ok

    rec = {k: receipt_map(v) for k, v in RECEIPTS.items()}
    res["receipts"] = {k: {"path": RECEIPTS[k], "sha256": sha_file(os.path.join(REPO, RECEIPTS[k])),
                           "task_id": rec[k][0].get("task_id"), "phase": rec[k][0].get("phase"),
                           "commit_sha": rec[k][0].get("commit_sha"), "binding_mode": rec[k][0].get("binding_mode"),
                           "n_path_sha256": len(rec[k][1])} for k in rec}
    # (a) the healthresolve draft equals addendum_sha256 of TASK-20260924-bc10a8's receipt
    add = rec["bc10a8"][0].get("addendum_sha256") or {}
    chk("(a) healthresolve draft == TASK-20260924-bc10a8 addendum_sha256", HEALTHRESOLVE, add.get("sha256"),
        sha_file(os.path.join(REPO, HEALTHRESOLVE)), RECEIPTS["bc10a8"] + " addendum_sha256.sha256")
    chk("(a') healthresolve draft == TASK-20260924-bc10a8 path_sha256", HEALTHRESOLVE, rec["bc10a8"][1].get(HEALTHRESOLVE),
        sha_file(os.path.join(REPO, HEALTHRESOLVE)), RECEIPTS["bc10a8"] + " path_sha256")
    res["addendum_sha256_block"] = add
    # (b) the seedresolve and solverevent drafts
    chk("(b) seedresolve draft", SEEDRESOLVE, SEEDRESOLVE_SHA, sha_file(os.path.join(REPO, SEEDRESOLVE)), "card LC-2 (b)")
    chk("(b) solverevent draft", SOLVEREVENT, SOLVEREVENT_SHA, sha_file(os.path.join(REPO, SOLVEREVENT)), "card LC-2 (b)")
    # (c) implementation-v2 / -a1 / -r1 files, file by file, and no file on disk outside the receipt
    for tree, rk in (("v2", "0fa03f_phaseA"), ("a1", "4ff597_phaseA"), ("r1", "53a47d"), ("r2", "5ca2a5")):
        disk = tree_files(TREES[tree])
        bound = sorted(p for p in rec[rk][1] if p.startswith(TREES[tree] + "/"))
        extra = sorted(set(disk) - set(bound))
        missing = sorted(set(bound) - set(disk))
        res["checks"].append({"check": "(%s) %s/ file list equals the %s receipt" % ("d" if tree == "r2" else "c", TREES[tree], rk),
                              "path": TREES[tree], "on_disk_not_bound": extra, "bound_not_on_disk": missing,
                              "n_disk": len(disk), "n_bound": len(bound), "equal": not extra and not missing})
        if extra or missing:
            res["pass"] = False
        for p in disk:
            chk("(%s) %s" % ("d" if tree == "r2" else "c", tree), p, rec[rk][1].get(p), sha_file(os.path.join(REPO, p)), RECEIPTS[rk])
    # (d) the r2 note, both r2 plans and the stage-r2 bundle
    for p in (EXP_REL + "/implementation-v2-r2.md", PLAN_V2_R2, PLAN_A1_R2, R2_BUNDLE):
        chk("(d) r2 output", p, rec["5ca2a5"][1].get(p), sha_file(os.path.join(REPO, p)), RECEIPTS["5ca2a5"])
    # frozen plans read for the command comparison: bound by the phase-A receipts
    chk("(c) frozen plan", PLAN_V2, rec["0fa03f_phaseA"][1].get(PLAN_V2), sha_file(os.path.join(REPO, PLAN_V2)), RECEIPTS["0fa03f_phaseA"])
    chk("(c) frozen plan", PLAN_A1, rec["4ff597_phaseA"][1].get(PLAN_A1), sha_file(os.path.join(REPO, PLAN_A1)), RECEIPTS["4ff597_phaseA"])
    # v1 files and the two coordination scratch inputs: sha256 on disk and at HEAD, and every archive that binds them
    head = git("rev-parse", "HEAD").decode().strip()
    res["head"] = head
    res["dirty_tree_porcelain"] = git("status", "--porcelain", "--untracked-files=all").decode().splitlines()
    all_receipts = {}
    for dp, dn, fn in os.walk(os.path.join(REPO, ARCH)):
        for f in fn:
            if f.endswith(".json"):
                try:
                    _d, m = receipt_map(rel(os.path.join(dp, f)))
                    all_receipts[rel(os.path.join(dp, f))] = m
                except Exception:                       # noqa: BLE001
                    pass
    recorded = []
    ext_files = tree_files(TREES["v1"]) + [EXTERNAL_INPUTS["k4a"]] + tree_files(EXTERNAL_INPUTS["k5k7"])
    tracked = set(git("ls-files", "--", TREES["v1"], EXTERNAL_INPUTS["k4a"], EXTERNAL_INPUTS["k5k7"]).decode().splitlines())
    for p in ext_files:
        disk = sha_file(os.path.join(REPO, p))
        at_head = sha_bytes(git("show", "HEAD:" + p)) if p in tracked else None
        binds = sorted("%s = %s" % (r, m[p]) for r, m in all_receipts.items() if p in m)
        recorded.append({"path": p, "sha256_disk": disk, "tracked": p in tracked, "sha256_at_HEAD": at_head,
                         "disk_equals_HEAD": (disk == at_head) if at_head else None, "bound_by_archives": binds,
                         "binding_archive_values_equal_disk": all(b.endswith(disk) for b in binds) if binds else None})
    res["recorded_not_receipt_bound_inputs"] = recorded
    return res


INTEG = integrity()
OUT["CN5_integrity"] = INTEG
if not INTEG["pass"]:
    write_out(stop="LC-2 integrity failed; nothing was read as a result (CN-5: the census is INCOMPLETE)")
    print("STOP: integrity failed", file=sys.stderr)
    sys.exit(3)

# ---------------------------------------------------------------------------------------------------------------------
# From here on NO child process may start: install the guard.
# ---------------------------------------------------------------------------------------------------------------------
GUARD = {"installed_at": None, "blocked_attempts": []}


def _blocked(name):
    def f(*a, **k):
        GUARD["blocked_attempts"].append({"call": name, "args": repr(a)[:200]})
        raise RuntimeError("census guard: child launch %s refused (LC-1)" % name)
    return f


for _n in ("fork", "forkpty", "posix_spawn", "posix_spawnp", "system", "popen", "execv", "execve", "execvp", "execvpe",
           "execl", "execle", "execlp", "execlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe", "spawnl", "spawnle"):
    if hasattr(os, _n):
        setattr(os, _n, _blocked("os." + _n))
subprocess.Popen = _blocked("subprocess.Popen")
GUARD["installed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
OUT["child_launch_guard"] = GUARD


def children_now():
    """Child pids of this process from /proc (all threads)."""
    kids = []
    tdir = "/proc/self/task"
    for t in os.listdir(tdir):
        try:
            kids += open(os.path.join(tdir, t, "children")).read().split()
        except OSError:
            pass
    return kids


# =====================================================================================================================
# Source model (ast)
# =====================================================================================================================
SRC = {}        # module -> dict(path, tree, text, lines)


def add_module(mod, path):
    txt = open(os.path.join(REPO, path)).read()
    OUT["files_read"][path] = sha_bytes(txt.encode())
    SRC[mod] = {"path": path, "text": txt, "lines": txt.splitlines(), "tree": ast.parse(txt, filename=path)}


MOD_TREE = {}
dups = []
for tree, trel in TREES.items():
    for p in tree_files(trel):
        if p.endswith(".py"):
            mod = os.path.basename(p)[:-3]
            key = mod if mod not in SRC else "%s@%s" % (mod, tree)
            if mod in SRC:
                dups.append((mod, SRC[mod]["path"], p))
            add_module(key, p)
            MOD_TREE[key] = tree
add_module("k4a_anchor_system", EXTERNAL_INPUTS["k4a"])
MOD_TREE["k4a_anchor_system"] = "external:k4a"
for p in tree_files(EXTERNAL_INPUTS["k5k7"]):
    if p.endswith(".py"):
        m = os.path.basename(p)[:-3]
        add_module(m, p)
        MOD_TREE[m] = "external:k5k7"
OUT["module_name_collisions"] = dups

LAUNCH_PRIMS = {
    "os.fork", "os.forkpty", "os.execv", "os.execve", "os.execvp", "os.execvpe", "os.execl", "os.execle", "os.execlp",
    "os.execlpe", "os.system", "os.popen", "os.spawnv", "os.spawnve", "os.spawnvp", "os.spawnvpe", "os.spawnl",
    "os.spawnle", "os.posix_spawn", "os.posix_spawnp", "subprocess.run", "subprocess.Popen", "subprocess.call",
    "subprocess.check_call", "subprocess.check_output", "subprocess.getoutput", "subprocess.getstatusoutput",
    "pty.spawn", "multiprocessing.Process", "asyncio.create_subprocess_exec", "asyncio.create_subprocess_shell"}
DYNAMIC_NAMES = {"getattr", "setattr", "exec", "eval", "__import__", "compile", "globals", "locals", "vars",
                 "importlib.import_module", "runpy.run_path", "runpy.run_module", "importlib.util.spec_from_file_location"}


def is_main_guard(st):
    """`if __name__ == "__main__":` at module level: runs only when the file is executed as a script, never on import."""
    return (isinstance(st, ast.If) and isinstance(st.test, ast.Compare) and isinstance(st.test.left, ast.Name)
            and st.test.left.id == "__name__" and len(st.test.comparators) == 1
            and isinstance(st.test.comparators[0], ast.Constant) and st.test.comparators[0].value == "__main__")


class Fn:
    def __init__(self, mod, qual, node, cls=None, parent=None):
        self.mod, self.qual, self.node, self.cls, self.parent = mod, qual, node, cls, parent
        self.id = "%s:%s" % (mod, qual)
        self.params = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = node.args
            self.params = [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs] + ([a.vararg.arg] if a.vararg else []) + ([a.kwarg.arg] if a.kwarg else [])
        self.local_defs = {}
        self.calls = []       # dict(line, target(s), raw, node)
        self.refs = []        # (line, target) function references not in call position
        self.assigns = {}     # name -> [value nodes]
        self.imports = set()  # internal modules imported here (function-level) / at module level for <module>
        self.dynamic = []
        self.rebindings = []


FNS = {}
MODINFO = {}


def collect_module(mod):
    info = {"aliases": {}, "defs": {}, "classes": {}, "consts": {}, "func_alias": {}, "listconsts": {}}
    tree = SRC[mod]["tree"]
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                info["aliases"][a.asname or a.name.split(".")[0]] = ("module", a.name if a.asname else a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            for a in n.names:
                if a.name == "*":
                    info.setdefault("star", []).append(n.module)
                    continue
                info["aliases"][a.asname or a.name] = ("attr", n.module, a.name)
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
            info["defs"][st.name] = st
        elif isinstance(st, ast.ClassDef):
            info["classes"][st.name] = st
        elif isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
            v = st.value
            if isinstance(v, ast.Constant):
                info["consts"][st.targets[0].id] = v.value
            elif isinstance(v, (ast.List, ast.Tuple)):
                info["listconsts"][st.targets[0].id] = v
            elif isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name):
                info["func_alias"][st.targets[0].id] = (v.value.id, v.attr)
            elif isinstance(v, ast.Name):
                info["func_alias"][st.targets[0].id] = (None, v.id)
    MODINFO[mod] = info


for m in SRC:
    collect_module(m)
INTERNAL = set(k for k in SRC if "@" not in k)


def const_of(mod, name):
    return MODINFO.get(mod, {}).get("consts", {}).get(name)


def resolve_attr_module(mod, name):
    a = MODINFO[mod]["aliases"].get(name)
    if a and a[0] == "module":
        return a[1]
    return None


def resolve_name(fn, name):
    """-> ('int', fnid) | ('ext', dotted) | ('class', mod.cls) | None"""
    f = fn
    while f is not None:
        if name in f.local_defs:
            return ("int", f.local_defs[name])
        f = f.parent
    mod = fn.mod
    info = MODINFO[mod]
    if name in info["defs"]:
        return ("int", "%s:%s" % (mod, name))
    if name in info["classes"]:
        init = "%s:%s.__init__" % (mod, name)
        return ("int", init) if init in FNS else ("class", "%s:%s" % (mod, name))
    if name in info["func_alias"]:
        am, attr = info["func_alias"][name]
        if am is None:
            return resolve_name(fn, attr) if attr != name else None
        t = resolve_attr_module(mod, am)
        if t:
            return resolve_mod_attr(t, attr)
    a = info["aliases"].get(name)
    if a and a[0] == "attr":
        if a[1] in INTERNAL:
            return resolve_mod_attr(a[1], a[2])
        return ("ext", "%s.%s" % (a[1], a[2]))
    for sm in info.get("star", []):
        if sm in INTERNAL:
            r = resolve_mod_attr(sm, name)
            if r and r[0] in ("int", "class"):
                return r
    return None


def resolve_mod_attr(m, attr):
    if m in INTERNAL:
        info = MODINFO[m]
        if attr in info["defs"]:
            return ("int", "%s:%s" % (m, attr))
        if attr in info["classes"]:
            init = "%s:%s.__init__" % (m, attr)
            return ("int", init) if init in FNS else ("class", "%s:%s" % (m, attr))
        if attr in info["func_alias"]:
            am, a2 = info["func_alias"][attr]
            t = resolve_attr_module(m, am) if am else None
            if t:
                return resolve_mod_attr(t, a2)
        a = info["aliases"].get(attr)
        if a and a[0] == "attr" and a[1] in INTERNAL:
            return resolve_mod_attr(a[1], a[2])
        return ("intattr", "%s.%s" % (m, attr))
    return ("ext", "%s.%s" % (m, attr))


def dotted(expr):
    parts = []
    while isinstance(expr, ast.Attribute):
        parts.append(expr.attr)
        expr = expr.value
    if isinstance(expr, ast.Name):
        parts.append(expr.id)
        return ".".join(reversed(parts))
    return None


def resolve_expr(fn, expr):
    if isinstance(expr, ast.Name):
        return resolve_name(fn, expr.id)
    if isinstance(expr, ast.Attribute):
        d = dotted(expr)
        if d is None:
            return ("method", expr.attr)
        head, rest = d.split(".", 1)
        if head in ("self", "cls") and fn.cls:
            fid = "%s:%s.%s" % (fn.mod, fn.cls, rest)
            return ("int", fid) if fid in FNS else ("method", expr.attr)
        m = resolve_attr_module(fn.mod, head)
        if m is not None:
            if "." in rest:
                return ("ext", "%s.%s" % (m, rest)) if m not in INTERNAL else ("method", expr.attr)
            return resolve_mod_attr(m, rest)
        a = MODINFO[fn.mod]["aliases"].get(head)
        if a and a[0] == "attr" and a[1] not in INTERNAL:
            return ("ext", "%s.%s.%s" % (a[1], a[2], rest))
        return ("method", expr.attr)
    return None


def build_fns(mod):
    tree = SRC[mod]["tree"]
    top = Fn(mod, "<module>", tree)
    FNS[top.id] = top
    for st in tree.body:
        if is_main_guard(st):
            scr = Fn(mod, "<script>", st)
            FNS[scr.id] = scr

    def visit_body(body, owner, cls):
        for st in body:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = st.name if owner.qual == "<module>" else "%s.%s" % (owner.qual, st.name)
                if cls and owner.qual == "<module>":
                    q = "%s.%s" % (cls, st.name)
                f = Fn(mod, q, st, cls=cls if owner.qual == "<module>" or owner.cls else None, parent=owner if owner.qual != "<module>" else None)
                if owner.qual != "<module>":
                    owner.local_defs[st.name] = f.id
                    f.cls = owner.cls
                FNS[f.id] = f
                visit_body(st.body, f, None)
            elif isinstance(st, ast.ClassDef):
                visit_body(st.body, owner, st.name)
            else:
                for field in ("body", "orelse", "finalbody", "handlers"):
                    sub = getattr(st, field, None)
                    if isinstance(sub, list):
                        visit_body([x for x in sub if isinstance(x, ast.stmt)] +
                                   [y for h in sub if isinstance(h, ast.ExceptHandler) for y in h.body], owner, cls)
    visit_body(tree.body, top, None)


for m in SRC:
    build_fns(m)


MAIN_GUARDS = {}


def own_nodes(fn):
    """AST nodes belonging to fn itself (not to nested functions / classes defined inside it)."""
    root = fn.node
    out = []
    if isinstance(root, ast.Module):
        stack = [st for st in root.body if not is_main_guard(st)]
    elif isinstance(root, ast.If):
        stack = list(root.body)
    else:
        stack = list(ast.iter_child_nodes(root))
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and n is not root:
            if isinstance(n, ast.Lambda):
                stack.extend(ast.iter_child_nodes(n))
            else:
                out.extend(n.decorator_list)
                out.extend(n.args.defaults + [d for d in n.args.kw_defaults if d is not None])
            continue
        if isinstance(n, ast.ClassDef):
            if isinstance(root, ast.Module):
                # class bodies: statements outside methods run at import time
                for st in n.body:
                    if not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        stack.append(st)
            continue
        out.append(n)
        stack.extend(ast.iter_child_nodes(n))
    return out


for fid, fn in list(FNS.items()):
    call_funcs = set()
    for n in own_nodes(fn):
        if isinstance(n, ast.Call):
            call_funcs.add(id(n.func))
            tgt = resolve_expr(fn, n.func)
            raw = ast.unparse(n.func)
            fn.calls.append({"line": n.lineno, "target": tgt, "raw": raw, "node": n})
            d = dotted(n.func) or raw
            base = tgt[1] if tgt and tgt[0] == "ext" else d
            if base in DYNAMIC_NAMES or (tgt and tgt[0] == "ext" and tgt[1] in DYNAMIC_NAMES):
                fn.dynamic.append({"line": n.lineno, "call": ast.unparse(n)[:160]})
        elif isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            tg = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tg:
                for nm in ast.walk(t):
                    if isinstance(nm, ast.Name):
                        fn.assigns.setdefault(nm.id, []).append(n.value)
        elif isinstance(n, (ast.For, ast.comprehension)):
            for nm in ast.walk(n.target):
                if isinstance(nm, ast.Name):
                    fn.assigns.setdefault(nm.id, []).append(n.iter)
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            for nm in ast.walk(n.optional_vars):
                if isinstance(nm, ast.Name):
                    fn.assigns.setdefault(nm.id, []).append(n.context_expr)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module]
            for nm in names:
                if nm in INTERNAL:
                    fn.imports.add(nm)
            if isinstance(n, ast.ImportFrom) and n.module in INTERNAL:
                pass
        elif isinstance(n, ast.Subscript) and dotted(n.value) == "sys.modules":
            fn.dynamic.append({"line": n.lineno, "call": ast.unparse(n)[:160]})
    store_bases = set()
    for n in own_nodes(fn):
        if isinstance(n, ast.Attribute):
            store_bases.add(id(n.value))      # `f.attr` (read or write) inspects / sets an attribute of f; it does not call f
        elif isinstance(n, ast.Compare) and all(isinstance(o, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)) for o in n.ops):
            store_bases.update(id(x) for x in [n.left] + n.comparators)   # identity / equality tests do not call
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr", "setattr", "id", "callable") and n.args:
            store_bases.add(id(n.args[0]))
        elif isinstance(n, ast.Assign) and all(isinstance(t, ast.Attribute) for t in n.targets):
            # `mod.attr = f`: a REBINDING of a module / object attribute (recorded; its runtime effect is modelled explicitly)
            store_bases.add(id(n.value))
            fn.rebindings.append({"line": n.lineno, "stmt": ast.unparse(n)[:160]})
    for n in own_nodes(fn):
        if id(n) in store_bases:
            continue
        if isinstance(n, (ast.Name, ast.Attribute)) and isinstance(getattr(n, "ctx", None), ast.Load) and id(n) not in call_funcs:
            t = resolve_expr(fn, n) if isinstance(n, ast.Name) or dotted(n) else None
            if t and t[0] == "int" and t[1] != fid:
                fn.refs.append((n.lineno, t[1]))

METHODS_BY_NAME = {}
for fid, fn in FNS.items():
    if fn.cls and fn.parent is None:
        METHODS_BY_NAME.setdefault(fid.split(".")[-1], []).append(fid)


def module_imports(mod):
    """internal modules imported anywhere in mod (module level and function level)."""
    s = set(m for m in MODINFO[mod].get("star", []) if m in INTERNAL)
    for a in MODINFO[mod]["aliases"].values():
        m = a[1]
        if m in INTERNAL:
            s.add(m)
    return s


# explicit runtime bindings the static graph cannot see (documented, never inferred)
RUNTIME_EDGES = {
    "r2_resolve:_call_original": ["v2_driver:solve"],   # r2_resolve.install records v2_driver.solve as `original` (r2_resolve.py 292-298)
    "r1_resolve:_call_original": [],
}


def edges(fid):
    fn = FNS[fid]
    out = []
    for c in fn.calls:
        t = c["target"]
        if t is None:
            continue
        if t[0] == "int":
            out.append((c["line"], t[1], "call"))
        elif t[0] == "method":
            imp = module_imports(fn.mod) | {fn.mod}
            for cand in METHODS_BY_NAME.get(t[1], []):
                if FNS[cand].mod in imp:
                    out.append((c["line"], cand, "method-name (approximate)"))
    for line, t in fn.refs:
        out.append((line, t, "reference"))
    for t in RUNTIME_EDGES.get(fid, []):
        out.append((None, t, "runtime binding"))
    for m in fn.imports:
        out.append((None, "%s:<module>" % m, "import"))
    if fn.qual == "<module>":
        for m in module_imports(fn.mod):
            # module-level imports only
            pass
        for st in SRC[fn.mod]["tree"].body:
            if isinstance(st, (ast.Import, ast.ImportFrom)):
                for nm in ([a.name for a in st.names] if isinstance(st, ast.Import) else [st.module]):
                    if nm in INTERNAL:
                        out.append((st.lineno, "%s:<module>" % nm, "import"))
    return out


def reach(roots, cut=()):
    parent = {r: None for r in roots}
    order = list(roots)
    i = 0
    while i < len(order):
        f = order[i]
        i += 1
        if f in cut:
            continue
        for line, t, kind in edges(f):
            if t in FNS and t not in parent:
                parent[t] = (f, line, kind)
                order.append(t)
    return parent


def chain(parent, fid):
    out = []
    while fid is not None:
        p = parent.get(fid)
        out.append(fid if p is None else "%s [%s @%s]" % (fid, p[2], p[1]))
        fid = p[0] if p else None
    return list(reversed(out))


# =====================================================================================================================
# Launch analysis
# =====================================================================================================================
def names_in(expr):
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


def closure_names(fn, expr, depth=0, seen=None):
    seen = seen if seen is not None else set()
    out = set()
    for nm in names_in(expr):
        out.add(nm)
        if nm in fn.assigns and nm not in seen and depth < 6:
            seen.add(nm)
            for v in fn.assigns[nm]:
                out |= closure_names(fn, v, depth + 1, seen)
    return out


def argv_expr(call, prim):
    n = call["node"]
    kw = {k.arg: k.value for k in n.keywords if k.arg}
    shell = isinstance(kw.get("shell"), ast.Constant) and kw["shell"].value is True
    if prim in ("os.system", "os.popen", "subprocess.getoutput", "subprocess.getstatusoutput", "asyncio.create_subprocess_shell"):
        return (n.args[0] if n.args else None), True
    if prim.startswith("os.exec") or prim.startswith("os.spawn") or prim.startswith("os.posix_spawn"):
        idx = 2 if prim.startswith("os.spawn") else 1
        return (n.args[idx] if len(n.args) > idx else (n.args[0] if n.args else None)), False
    if prim == "os.fork" or prim == "os.forkpty":
        return None, False
    if n.args:
        return n.args[0], shell
    return kw.get("args") or kw.get("argv") or kw.get("cmd"), shell


LAUNCHERS = {}     # fid -> {"param", "index", "vararg", "shell", "prefix", "via": (line, callee)}


def target_of(call):
    t = call["target"]
    if t is None:
        return None
    if t[0] == "ext" and t[1] in LAUNCH_PRIMS:
        return ("prim", t[1])
    if t[0] == "int" and t[1] in LAUNCHERS:
        return ("launcher", t[1])
    return None


def launcher_arg(call, lid):
    L = LAUNCHERS[lid]
    n = call["node"]
    if L.get("vararg"):
        return ast.Tuple(elts=list(n.args), ctx=ast.Load()) if n.args else None
    kw = {k.arg: k.value for k in n.keywords if k.arg}
    if L["param"] in kw:
        return kw[L["param"]]
    fnl = FNS[lid]
    idx = L["index"] - (1 if fnl.cls and fnl.params and fnl.params[0] in ("self", "cls") else 0)
    return n.args[idx] if len(n.args) > idx else None


def forwarded(fn, ex, depth=0):
    """(param, prefix) if ex passes a parameter of fn WHOLE as the argv sequence (or the whole shell string):
    Name P, list(P), tuple(P), *P inside a list, or a '+' concatenation containing one of these. A parameter used only
    inside an element (a file name, a flag value) is NOT forwarding. prefix: the literal program element placed before it."""
    if ex is None or depth > 5:
        return None
    if isinstance(ex, ast.Name):
        if ex.id in fn.params:
            return (ex.id, None)
        if ex.id in fn.assigns:
            for v in fn.assigns[ex.id]:
                r = forwarded(fn, v, depth + 1)
                if r:
                    return r
        return None
    if isinstance(ex, ast.Call) and isinstance(ex.func, ast.Name) and ex.func.id in ("list", "tuple") and ex.args:
        return forwarded(fn, ex.args[0], depth + 1)
    if isinstance(ex, (ast.List, ast.Tuple)):
        for i, e in enumerate(ex.elts):
            if isinstance(e, ast.Starred):
                r = forwarded(fn, e.value, depth + 1)
                if r:
                    return (r[0], ast.unparse(ex.elts[0]) if i > 0 else r[1])
        return None
    if isinstance(ex, ast.BinOp) and isinstance(ex.op, ast.Add):
        r = forwarded(fn, ex.right, depth + 1) or forwarded(fn, ex.left, depth + 1)
        if r:
            left = ex.left
            while isinstance(left, ast.BinOp):
                left = left.left
            if isinstance(left, ast.Name) and left.id in fn.assigns:
                left = fn.assigns[left.id][-1]
            pref = ast.unparse(left.elts[0]) if isinstance(left, (ast.List, ast.Tuple)) and left.elts else None
            if isinstance(left, ast.Name) and left.id not in fn.params:
                pref = left.id
            return (r[0], pref or r[1])
    return None


changed = True
while changed:
    changed = False
    for fid, fn in FNS.items():
        if fid in LAUNCHERS or fn.qual == "<module>":
            continue
        for c in fn.calls:
            tk = target_of(c)
            if tk is None:
                continue
            if tk[0] == "prim":
                ex, shell = argv_expr(c, tk[1])
            else:
                ex, shell = launcher_arg(c, tk[1]), LAUNCHERS[tk[1]]["shell"]
            r = forwarded(fn, ex)
            if not r:
                continue
            p, pref = r
            va = fn.node.args.vararg.arg if fn.node.args.vararg else None
            if tk[0] == "launcher" and LAUNCHERS[tk[1]].get("prefix"):
                pref = LAUNCHERS[tk[1]]["prefix"] + ((" + " + pref) if pref else "")
            LAUNCHERS[fid] = {"param": p, "index": fn.params.index(p), "vararg": p == va, "shell": shell,
                              "prefix": pref, "via": (c["line"], tk[1])}
            changed = True
            break

PROGRAM_CONSTS = {}


def const_value(fn, expr):
    """Resolve a constant string for an argv element (module constants, cross-module constants)."""
    if isinstance(expr, ast.Constant):
        return expr.value
    if isinstance(expr, ast.Name):
        v = const_of(fn.mod, expr.id)
        if v is not None:
            return v
        a = MODINFO[fn.mod]["aliases"].get(expr.id)
        if a and a[0] == "attr" and a[1] in INTERNAL:
            return const_of(a[1], a[2])
    if isinstance(expr, ast.Attribute):
        d = dotted(expr)
        if d == "sys.executable":
            return "<sys.executable: python3>"
        if d:
            head, rest = d.split(".", 1)
            m = resolve_attr_module(fn.mod, head)
            if m in INTERNAL and "." not in rest:
                return const_of(m, rest) or ("<%s.%s>" % (m, rest))
    return None


MSOLVE_MARKERS = ("/usr/bin/msolve",)


def classify_program(fn, ex, shell, depth=0):
    """-> dict(program, msolve: True/False/None(unknown), detail)"""
    if ex is None:
        return {"program": None, "msolve": None, "detail": "no argv expression"}
    if isinstance(ex, ast.Name) and ex.id in fn.assigns and depth < 5:
        rs = [classify_program(fn, v, shell, depth + 1) for v in fn.assigns[ex.id]]
        progs = sorted({str(r["program"]) for r in rs})
        ms = [r["msolve"] for r in rs]
        return {"program": " | ".join(progs), "msolve": True if any(m is True for m in ms) else (None if any(m is None for m in ms) else False),
                "detail": "via local name %s (%d assignment(s))" % (ex.id, len(rs))}
    if isinstance(ex, ast.Call):
        t = resolve_expr(fn, ex.func)
        if t and t[1].endswith("msolve_argv"):
            return {"program": "/usr/bin/msolve (v2_solver.msolve_argv)", "msolve": True, "detail": ast.unparse(ex)[:200]}
        if isinstance(ex.func, ast.Name) and ex.func.id == "list" and ex.args:
            return classify_program(fn, ex.args[0], shell, depth + 1)
    if isinstance(ex, ast.BinOp):
        return classify_program(fn, ex.left, shell, depth + 1)
    if isinstance(ex, ast.Name) and ex.id in MODINFO[fn.mod]["listconsts"] and depth < 5:
        r = classify_program(fn, MODINFO[fn.mod]["listconsts"][ex.id], shell, depth + 1)
        r["detail"] = "module constant %s = %s" % (ex.id, ast.unparse(MODINFO[fn.mod]["listconsts"][ex.id])[:160])
        return r
    if isinstance(ex, (ast.List, ast.Tuple)) and ex.elts:
        v = const_value(fn, ex.elts[0])
        if v is None:
            return {"program": ast.unparse(ex.elts[0]), "msolve": None, "detail": "argv[0] not a resolvable constant"}
        ms = ("msolve" in os.path.basename(str(v))) or str(v) in MSOLVE_MARKERS or (
            isinstance(ex.elts[0], (ast.Name, ast.Attribute)) and ast.unparse(ex.elts[0]).split(".")[-1] == "MSOLVE")
        return {"program": str(v), "msolve": bool(ms), "detail": ast.unparse(ex)[:200]}
    if isinstance(ex, (ast.Constant, ast.JoinedStr)) and shell:
        s = ex.value if isinstance(ex, ast.Constant) else "".join(x.value if isinstance(x, ast.Constant) else "{}" for x in ex.values)
        progs = [seg.strip().split()[0] for seg in re.split(r"\||;|&&|\|\|", str(s)) if seg.strip()]
        return {"program": "shell: " + " | ".join(progs), "msolve": any(os.path.basename(p) == "msolve" for p in progs),
                "detail": str(s)[:200]}
    v = const_value(fn, ex)
    if v is not None and shell:
        return classify_program(fn, ast.Constant(value=v), shell, depth + 1)
    return {"program": ast.unparse(ex)[:120], "msolve": None, "detail": "dynamic argv expression"}


SITES = []
for fid, fn in FNS.items():
    for c in fn.calls:
        tk = target_of(c)
        if tk is None:
            continue
        if tk[0] == "prim":
            ex, shell = argv_expr(c, tk[1])
        else:
            ex, shell = launcher_arg(c, tk[1]), LAUNCHERS[tk[1]]["shell"]
        forwarding = fid in LAUNCHERS and LAUNCHERS[fid]["via"][0] == c["line"]
        if not forwarding and fid in LAUNCHERS and forwarded(fn, ex):
            forwarding = True
        if tk[1] == "os.fork":
            forwarding = True       # the fork in v2_solver._run_child_locked precedes the exec of the forwarded argv
        prog = classify_program(fn, ex, shell) if not forwarding else {"program": "(forwards parameter %s)" % LAUNCHERS.get(fid, {}).get("param"), "msolve": None, "detail": "launcher-internal"}
        fixed_prefix = None
        if forwarding and fid in LAUNCHERS and LAUNCHERS[fid].get("prefix") and LAUNCHERS[fid]["via"][0] == c["line"]:
            fixed_prefix = LAUNCHERS[fid]["prefix"]
            pv = const_value(fn, ast.parse(fixed_prefix.split(" + ")[0], mode="eval").body)
            prog = {"program": "%s (fixed here; arguments forwarded from parameter %s)" % (pv or fixed_prefix, LAUNCHERS[fid]["param"]),
                    "msolve": bool(pv and os.path.basename(str(pv)) == "msolve"), "detail": "program fixed in this launcher"}
        wrapper_prefix = LAUNCHERS[tk[1]]["prefix"] if tk[0] == "launcher" else None
        caller_entry = False
        if wrapper_prefix and not forwarding:
            pv = const_value(FNS[tk[1]], ast.parse(wrapper_prefix.split(" + ")[0], mode="eval").body)
            if prog["msolve"] is not True:
                # a call into a launcher whose program is fixed inside it (git, v1 run_msolve): a CALLER ENTRY of that
                # launcher's site, not a separate site
                caller_entry = True
                prog = {"program": "%s (fixed in %s)" % (pv or wrapper_prefix, tk[1]),
                        "msolve": bool(pv and os.path.basename(str(pv)) == "msolve"), "detail": "caller of a fixed-program launcher"}
        # launch chain down to the primitive
        chain_lines = ["%s:%d" % (SRC[fn.mod]["path"], c["line"])]
        lid = tk[1] if tk[0] == "launcher" else None
        while lid:
            L = LAUNCHERS[lid]
            chain_lines.append("%s:%d" % (SRC[FNS[lid].mod]["path"], L["via"][0]))
            lid = L["via"][1] if L["via"][1] in LAUNCHERS else None
            if lid is None:
                pass
        SITES.append({"module": fn.mod, "tree": MOD_TREE.get(fn.mod), "file": SRC[fn.mod]["path"], "line": c["line"],
                      "function": fn.qual, "fid": fid, "callee": tk[1], "callee_kind": tk[0], "argv_expr": ast.unparse(ex)[:240] if ex is not None else None,
                      "shell": shell, "forwarding": forwarding, "wrapper_prefix": wrapper_prefix, "fixed_prefix_here": fixed_prefix,
                      "caller_entry_of_fixed_program_launcher": caller_entry,
                      "program": prog["program"], "msolve_in_argv": prog["msolve"], "program_detail": prog["detail"],
                      "launch_chain": chain_lines, "source_line": SRC[fn.mod]["lines"][c["line"] - 1].strip()[:240]})

# ---------------------------------------------------------------------------------------------------------------------
# MANUAL RESOLUTIONS of argv expressions the static resolver leaves dynamic. Each is a recorded reading by the Executor
# with its basis (file:line). The script re-checks that every cited line contains the cited token.
# ---------------------------------------------------------------------------------------------------------------------

def line_has(path_rel, line, token):
    lines = open(os.path.join(REPO, path_rel)).read().splitlines()
    return 0 < line <= len(lines) and token in lines[line - 1]


CITE_FAILS = []
N_CITES = [0]


def cite(path_rel, line, token):
    ok = line_has(path_rel, line, token)
    N_CITES[0] += 1
    if not ok:
        CITE_FAILS.append({"path": path_rel, "line": line, "token": token})
    return {"file": path_rel, "line": line, "token": token, "present": ok}


V2 = TREES["v2"]
A1 = TREES["a1"]
R2 = TREES["r2"]
V1 = TREES["v1"]
K5 = EXTERNAL_INPUTS["k5k7"]

MANUAL_ARGV = {
    V1 + "/run_wrapper.py:98": {
        "program": "operator-supplied command: run_wrapper.py RUN-ID CELL-LABEL -- <command ...> (cmd = argv[3:], line 82)",
        "msolve": "not determinable statically (the v1 wrapper runs whatever command follows '--'); v1 tree, not reachable",
        "basis": [cite(V1 + "/run_wrapper.py", 82, "cmd = argv[3:]"), cite(V1 + "/run_wrapper.py", 98, "subprocess.run(cmd")]},
}

# ---------------------------------------------------------------------------------------------------------------------
# Embedded code in string literals (generated shim scripts of the development harnesses)
# ---------------------------------------------------------------------------------------------------------------------
EMBED_TOKENS = ("subprocess", "Popen", "os.system", "run_child", "msolve_argv", "/usr/bin/msolve", "execv", "runpy", "os.fork",
                "callgrind_instructions", "SAGE_PYTHON", "/usr/bin/gp", "cypari2")
EMBEDDED = []
for mod, s in SRC.items():
    for n in ast.walk(s["tree"]):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) > 80:
            hits = [t for t in EMBED_TOKENS if t in n.value]
            if not hits:
                continue
            try:
                sub = ast.parse(n.value)
                parses = True
            except SyntaxError:
                sub, parses = None, False
            calls = []
            if sub is not None:
                for m in ast.walk(sub):
                    if isinstance(m, ast.Call):
                        d = dotted(m.func) or ast.unparse(m.func)
                        if any(t in d for t in ("subprocess", "Popen", "system", "run_child", "exec", "runpy", "fork", "msolve", "callgrind", "rc")):
                            calls.append({"line_in_string": m.lineno, "call": ast.unparse(m)[:200]})
            EMBEDDED.append({"module": mod, "tree": MOD_TREE.get(mod), "file": s["path"], "line": n.lineno, "tokens": hits,
                             "parses_as_python": parses, "launch_like_calls": calls,
                             "string_sha256": sha_bytes(n.value.encode())})

# ---------------------------------------------------------------------------------------------------------------------
# Reachability (static call graph through module attributes, references and import-time code), per plan command
# ---------------------------------------------------------------------------------------------------------------------
plans = {k: json.load(open(os.path.join(REPO, v))) for k, v in (("v2", PLAN_V2), ("a1", PLAN_A1), ("v2r2", PLAN_V2_R2), ("a1r2", PLAN_A1_R2))}
for k, v in (("v2", PLAN_V2), ("a1", PLAN_A1), ("v2r2", PLAN_V2_R2), ("a1r2", PLAN_A1_R2)):
    OUT["files_read"][v] = sha_file(os.path.join(REPO, v))


def commands_of(plan):
    out = []
    for p in sorted(plan["packages"], key=lambda x: x["order"]):
        out.append({"order": p["order"], "run_id": p["run_id"], "kind": p["kind"], "driver_args": p.get("driver_args"),
                    "command": (p.get("driver_args") or [None])[0]})
    return out


cmp_cmds = {}
for fr, r2 in (("v2", "v2r2"), ("a1", "a1r2")):
    a, b = commands_of(plans[fr]), commands_of(plans[r2])
    rows = []
    for x, y in zip(a, b):
        rows.append({"order": x["order"], "kind": x["kind"], "frozen_run_id": x["run_id"], "r2_run_id": y["run_id"],
                     "frozen_command": x["command"], "r2_command": y["command"], "command_equal": x["command"] == y["command"],
                     "driver_args_equal": x["driver_args"] == y["driver_args"],
                     "difference": None if x["driver_args"] == y["driver_args"] else "run ids inside --prior-run/--runs/--a1-runs/--v2-runs/--v2-aggregate arguments (id map)"})
    cmp_cmds[r2] = {"n_packages": [len(a), len(b)], "rows": rows,
                    "commands_invoked": sorted({r["r2_command"] for r in rows if r["r2_command"]}),
                    "contingency_packages": [r["r2_run_id"] for r in rows if r["kind"] == "contingency"],
                    "all_commands_equal": all(r["command_equal"] for r in rows)}
cmp_cmds["contingency_note"] = ("contingency packages carry no driver_args; r2_run_wrapper.launch uses the replaced package's driver_args "
                                "(r2_run_wrapper.py lines 387-391), so they invoke the same commands")
cite(R2 + "/r2_run_wrapper.py", 390, "driver_args = tgt[\"driver_args\"]")

DISPATCH = {"v2r2": {"entry": "r2_entry_v2", "driver_main": "v2_driver:main",
                     "dispatch_line": cite(V2 + "/v2_driver.py", 1347, '"fixture": cmd_fixture'),
                     "commands": {"fixture": "v2_driver:cmd_fixture", "fixture4": "v2_driver:cmd_fixture4",
                                  "anchor-identity": "v2_driver:cmd_anchor_identity", "controls": "v2_driver:cmd_controls",
                                  "build": "v2_driver:cmd_build", "cells": "v2_driver:cmd_cells", "aggregate": "v2_driver:cmd_aggregate"}},
            "a1r2": {"entry": "r2_entry_a1", "driver_main": "a1_driver:main",
                     "dispatch_line": cite(A1 + "/a1_driver.py", 462, '"controls-a1": cmd_controls_a1'),
                     "commands": {"controls-a1": "a1_driver:cmd_controls_a1", "build": "a1_driver:cmd_build",
                                  "cells": "a1_driver:cmd_cells", "aggregate-a1": "a1_driver:cmd_aggregate_a1"}}}

# SE-3 runtime binding: under both r2 entries every lookup of v2_driver.solve reaches r2_resolve.solve, which calls the
# original through _call_original (r2_resolve.py 203-224, 287-298; r2_entry_v2.py 46; r2_entry_a1.py 64).
SE3_BASIS = [cite(R2 + "/r2_resolve.py", 298, "v2_driver_module.solve = solve"), cite(R2 + "/r2_resolve.py", 224, "_call_original(original, args, kwargs)"),
             cite(R2 + "/r2_entry_v2.py", 46, "RS.install(D, run_dir)"), cite(R2 + "/r2_entry_a1.py", 64, "RS.install(D, run_dir)")]
_orig_edges = edges


def edges_r2(fid):
    out = _orig_edges(fid)
    extra = []
    for line, t, kind in out:
        if t == "v2_driver:solve" and fid != "r2_resolve:_call_original":
            extra.append((line, "r2_resolve:solve", "runtime binding (SE-3: v2_driver.solve is the r2 wrapper)"))
    return [e for e in out if not (e[1] == "v2_driver:solve" and fid != "r2_resolve:_call_original")] + extra


edges = edges_r2

REACH = {}
for plan_key, d in DISPATCH.items():
    entry = d["entry"]
    prelude = ["%s:<module>" % entry, "%s:main" % entry]
    for cmd in cmp_cmds[plan_key]["commands_invoked"]:
        root = d["commands"][cmd]
        par = reach(prelude + [root], cut={d["driver_main"]})
        REACH[(plan_key, cmd)] = par
HARNESS = {"r2_run_wrapper (package wrapper process, every package of both r2 plans)": reach(["r2_run_wrapper:<module>", "r2_run_wrapper:main"]),
           "r2_check_run (post-run checker named by both r2 plans; not a driver command)": reach(["r2_check_run:<module>", "r2_check_run:main"])}

reach_any = set()
for par in REACH.values():
    reach_any |= set(par)
OUT["reachability_method"] = {
    "graph": ("static call graph over every scanned module (ast): calls resolved through local defs, module globals, `import X as Y` "
              "aliases (Y.f), `from X import f`, `from X import *`, module-level aliases (e.g. a1_driver `log = D.log`), self.method; "
              "every function REFERENCE (dict dispatch, callbacks, assignment to a module attribute) is an edge, except a name used only as "
              "the base of an attribute access (f.x), as an operand of is / is not / == / !=, or as the first argument of getattr / hasattr / "
              "setattr / id / callable (these inspect the object and never call it); import-time code of every imported module is an edge, "
              "`if __name__ == '__main__':` blocks are NOT import-time code (they run only when the file is executed as a script); "
              "an unresolved obj.method() call is linked to every class method of that name in the calling module or the modules it "
              "imports (approximate, over-inclusive)."),
    "runtime_bindings_added": {"SE-3": "under both r2 entries every call of v2_driver.solve is routed to r2_resolve.solve, which reaches "
                                        "the original v2_driver.solve through r2_resolve._call_original", "basis": SE3_BASIS},
    "roots_per_command": "entry <module> + entry main (the edge into the driver's main() is cut) + the command's dispatch function",
    "commands_from": "driver_args[0] of every package of trial-plan-v2-r2.json and trial-plan-v2-a1-r2.json (contingency packages replay these)",
    "attribute_rebindings_in_reachable_functions": sorted([{"fid": f, **d} for f in reach_any for d in FNS[f].rebindings], key=lambda x: (x["fid"], x["line"])),
    "rebinding_rule": "a value assigned to an attribute (mod.attr = f) is recorded here and is not a call edge; the one rebinding of a callable in the r2 entries (r2_resolve.install, v2_driver.solve) is modelled by the SE-3 runtime binding",
    "dynamic_features_in_reachable_functions": sorted([{"fid": f, **d} for f in reach_any for d in FNS[f].dynamic], key=lambda x: (x["fid"], x["line"])),
    "approximate_method_edges_used": sorted({"%s -> %s (line %s)" % (v[0], t, v[1]) for par in REACH.values() for t, v in par.items()
                                             if v and v[2].startswith("method-name")}),
}


def reach_info(fid):
    cmds = []
    for (pk, cmd), par in REACH.items():
        if fid in par:
            cmds.append({"plan": {"v2r2": "trial-plan-v2-r2.json", "a1r2": "trial-plan-v2-a1-r2.json"}[pk], "command": cmd,
                         "call_chain": chain(par, fid)})
    return cmds


def harness_info(fid):
    return [{"process": h, "call_chain": chain(par, fid)} for h, par in HARNESS.items() if fid in par]


# ---------------------------------------------------------------------------------------------------------------------
# CN-1: msolve launch sites
# ---------------------------------------------------------------------------------------------------------------------
MS_SITES = [s for s in SITES if (s["msolve_in_argv"] is True and not s["caller_entry_of_fixed_program_launcher"]
                                   and (not s["forwarding"] or s.get("fixed_prefix_here")))]
for s in SITES:
    key = "%s:%d" % (s["file"], s["line"])
    if key in MANUAL_ARGV:
        s["manual_argv_reading"] = MANUAL_ARGV[key]
UNRESOLVED = [s for s in SITES if s["msolve_in_argv"] is None and not s["forwarding"] and not s["caller_entry_of_fixed_program_launcher"]]

# Recorded readings (Executor, from the cited lines) of what happens to each msolve site's output. The cited tokens are
# re-checked by cite(); a missing token is reported in census.json under citation_failures.
CLASSIFICATION = {
    V2 + "/v2_driver.py:166": {
        "site_label": "v2_driver.solve (the frozen cell / fixture / control / anchor solve)",
        "argv_line": cite(V2 + "/v2_driver.py", 165, "argv = V.msolve_argv(inp, out, threads=1, gb_only=gb_only)"),
        "launch_line": cite(V2 + "/v2_driver.py", 166, "rec = V.run_child(argv"),
        "classified": True,
        "enters": [cite(V2 + "/v2_driver.py", 176, "st = V.parse_msolve_log(text)"),
                   cite(V2 + "/v2_driver.py", 193, "V.parse_msolve_param(out)"),
                   cite(V2 + "/v2_driver.py", 197, "V.classify_solve(rec, st, kind, payload, sinfo, nfail)"),
                   cite(V2 + "/v2_driver.py", 198, "res.update(outcome=outcome, reason=reason"),
                   cite(V2 + "/v2_driver.py", 204, "D=D, D_defined=D is not None"),
                   cite(V2 + "/v2_driver.py", 188, "res.update(outcome=rec[\"outcome\"]")],
        "note": ("gb_only=True calls (anchor-identity, v2_driver.py lines 693 and 711) return before classify_solve (line 188) but their "
                 "F4 trace (line 177) is compared by the anchor trace-identity gate; gb_only=False calls are classified at line 197. "
                 "Under both r2 entries every call reaches this site through r2_resolve.solve (SE-3; gb_only passed straight through, "
                 "r2_resolve.py lines 208-212)."),
        "wrapped_by": "SE-3 (r2_resolve.solve replaces v2_driver.solve in both r2 entries)"},
    V2 + "/v2_driver.py:209": {
        "site_label": "callgrind child: valgrind --tool=callgrind running the same msolve argv (v2_driver.solve line 209 -> v2_solver.callgrind_instructions line 517)",
        "argv_line": cite(V2 + "/v2_driver.py", 209, "V.callgrind_instructions(V.msolve_argv(inp, cg_out, threads=1, gb_only=gb_only)"),
        "launch_line": cite(V2 + "/v2_solver.py", 517, "rec = run_child(vargv"),
        "wrapper_argv_line": cite(V2 + "/v2_solver.py", 516, "vargv = [VALGRIND, \"--tool=callgrind\""),
        "classified": "SEE classification_detail (the literal CN-1 definition and the draft's stated expectation differ)",
        "classification_detail": {
            "does_not_enter": ["v2_solver.classify_solve", "the target's outcome / reason / D / solutions (all set before line 207)",
                               "any frozen v2 or v2-a1 check or gate (no frozen module reads instructions_callgrind)"],
            "does_not_enter_basis": [cite(V2 + "/v2_driver.py", 207, "if callgrind_timeout and outcome == \"ok\":"),
                                     cite(V2 + "/v2_driver.py", 211, "os.remove(cg_out)")],
            "enters_recorded_fields": {
                "fields": "res['instructions_callgrind'] = {method, label, child: {outcome, wall_seconds, returncode, rlimit_as_child_getrlimit, peak_vm_bytes}, instructions_user, f4_core_inclusive_Ir, f4_core_function, f4_core_note, reason (when the child is not ok)}",
                "basis": [cite(V2 + "/v2_solver.py", 519, "\"child\": {k: rec.get(k) for k in (\"outcome\", \"wall_seconds\", \"returncode\", \"rlimit_as_child_getrlimit\", \"peak_vm_bytes\")}"),
                          cite(V2 + "/v2_solver.py", 523, "res[\"reason\"] = \"callgrind child outcome %s\""),
                          cite(V2 + "/v2_solver.py", 542, "res[\"f4_core_function\"]"),
                          cite(V2 + "/v2_driver.py", 360, "\"instructions_callgrind\""),
                          cite(V2 + "/v2_driver.py", 1180, "\"instructions_callgrind\"")],
                "cost_measurement_fields_among_them": "instructions_user, f4_core_inclusive_Ir (instruction counts), child.wall_seconds (wall)",
                "non_cost_fields_among_them": "child.outcome, child.returncode, child.rlimit_as_child_getrlimit, child.peak_vm_bytes (host reading), method, label, f4_core_function, f4_core_note, reason"},
            "enters_a_pass_fail_check_and_gate": {
                "check": "REG-1 (r2 layer, r2_reg1.compare (b)): every fixture target entry is compared whole minus the exclusion list X1..X17; X14-X17 exclude only instructions_callgrind.child.wall_seconds, .child.peak_vm_bytes, .instructions_user and .f4_core_inclusive_Ir, so instructions_callgrind.method, .label, .child.outcome, .child.returncode, .child.rlimit_as_child_getrlimit, .f4_core_function, .f4_core_note (and .reason when present) are compared; a difference FAILS REG-1",
                "gate": "r2_run_wrapper.preflight R-7 refuses every package after G1 unless REG-1 passes (r2_run_wrapper.py lines 22-23, 222-225)",
                "packages_whose_callgrind_output_REG-1_compares": "G1 only (fixture --p 4111; image of RUN-GFPN-ac4487); fixture_core passes callgrind_timeout = callgrind_timeout_s.m3 on every fixture solve (v2_driver.py 313, 358)",
                "basis": [cite(R2 + "/r2_reg1.py", 260, "rv = strip(rl[i], ex, \"target-entry\")"),
                          cite(R2 + "/reg1-exclusion-list.json", 1, "{"),
                          cite(R2 + "/r2_run_wrapper.py", 225, "R-7 REG-1 did not pass"),
                          cite(V2 + "/v2_driver.py", 358, "callgrind_timeout=cgtime")]},
            "literal_application_of_the_CN-1_definition": ("CLASSIFIED: its log/output enters recorded result fields other than wall, cpu or "
                                                           "instruction counts (child.outcome, child.returncode, f4_core_function, reason) and "
                                                           "enters a pass/fail check that gates packages (REG-1 (b))."),
            "draft_expectation": "the draft's CN-1 reading states the callgrind child (v2_driver.py line 209, v2_solver.py line 517) is 'expected' among the unclassified reachable launches",
            "census_position": "REPORTED AS A DISCREPANCY BETWEEN THE DEFINITION AND THE STATED EXPECTATION; the approval act rules on it (CN-1). The census decides nothing."},
        "wrapped_by": "runs inside the frozen solve(), i.e. inside the SE-3 wrapper's attempts, only after an ok outcome; never re-solved (SE-2 (6))"},
    A1 + "/a1_health.py:147": {
        "site_label": "a1_health.run_system (controls_a1 check (d), the msolve characteristic check)",
        "argv_line": cite(A1 + "/a1_health.py", 144, "argv = V.msolve_argv(inp, out, threads=1)"),
        "launch_line": cite(A1 + "/a1_health.py", 147, "rec = V.run_child(argv, logp, errp, cap_bytes=cap, timeout_s=DEV_TIMEOUT_S"),
        "classified": True,
        "enters": [cite(A1 + "/a1_health.py", 163, "st = V.parse_msolve_log(text)"),
                   cite(A1 + "/a1_health.py", 168, "V.parse_msolve_param(out)"),
                   cite(A1 + "/a1_health.py", 182, "V.classify_solve(rec, st, kind, payload, sinfo, nfail or 0)"),
                   cite(A1 + "/a1_health.py", 185, "res[\"v2_outcome_class\"] = outcome"),
                   cite(A1 + "/a1_health.py", 199, "res[\"pass\"] = all(checks.values())"),
                   cite(A1 + "/a1_health.py", 245, "entry[\"pattern_pass\"]"),
                   cite(A1 + "/a1_driver.py", 130, "rec(\"d_msolve_characteristic_check_synthetic\", hr[\"pass\"]")],
        "wrapped_by": "NONE in the r2 layer (the r2 a1 entry replaces only v2_driver.solve; r2_entry_a1.py lines 24, 64); the draft's HR-3 would wrap it"},
    V1 + "/symmetrize.py:399": {
        "site_label": "v1 symmetrize.run_msolve (v1 cells, fixtures and controls)",
        "argv_line": cite(V1 + "/symmetrize.py", 392, "cmd = [MSOLVE, \"-v\", \"2\""),
        "launch_line": cite(V1 + "/symmetrize.py", 399, "proc = subprocess.Popen(cmd"),
        "classified": True,
        "enters": [cite(V1 + "/symmetrize.py", 435, "stats = parse_msolve_log(out + \"\\n\" + err)"),
                   cite(V1 + "/symmetrize.py", 448, "stats.update({\"returncode\": rc, \"timed_out\": timed_out, \"outcome\": outcome")],
        "wrapped_by": "not applicable (v1; no v2+ module imports a v1 module)"},
    V1 + "/run_wrapper.py:36": {
        "site_label": "v1 run_wrapper.environment: shell 'msolve -h 2>&1 | head -1' (version string)",
        "argv_line": cite(V1 + "/run_wrapper.py", 36, "sh(\"msolve -h 2>&1 | head -1\")"),
        "launch_line": cite(V1 + "/run_wrapper.py", 23, "subprocess.run(cmd, shell=True"),
        "classified": "literal definition: its stdout enters a recorded field (environment.json software.msolve), which is not a cost measurement; it enters no classifier, check, gate or outcome class",
        "enters": [cite(V1 + "/run_wrapper.py", 36, "\"msolve\": sh(")],
        "wrapped_by": "not applicable (v1)"},
    K5 + "/square_analogue.py:157": {
        "site_label": "red-team scratch k5k7/square_analogue.py ideal_degree: msolve cross-check of Singular vdim",
        "argv_line": cite(K5 + "/square_analogue.py", 157, "[\"/usr/bin/msolve\", \"-v\", \"2\", \"-t\", \"1\""),
        "launch_line": cite(K5 + "/square_analogue.py", 157, "subprocess.run("),
        "classified": True,
        "enters": [cite(K5 + "/square_analogue.py", 165, "\"D_msolve\": msD")],
        "wrapped_by": "not applicable (not executed or imported by any scanned tree; v2_common reads only the JSON data of this directory)"},
    K5 + "/square_analogue_m4.py:26": {
        "site_label": "red-team scratch k5k7/square_analogue_m4.py ideal_degree (-t 4)",
        "argv_line": cite(K5 + "/square_analogue_m4.py", 26, "[\"/usr/bin/msolve\", \"-v\", \"2\", \"-t\", \"4\""),
        "launch_line": cite(K5 + "/square_analogue_m4.py", 26, "subprocess.run("),
        "classified": True,
        "enters": [],
        "wrapped_by": "not applicable (not executed or imported by any scanned tree)"},
}


def callers_of(fid):
    out = []
    for f, fn in FNS.items():
        for c in fn.calls:
            t = c["target"]
            if t and t[0] == "int" and t[1] == fid:
                out.append({"caller": f, "file": SRC[fn.mod]["path"], "line": c["line"], "source_line": SRC[fn.mod]["lines"][c["line"] - 1].strip()[:200]})
    return out


cn1_sites = []
for s in MS_SITES:
    key = "%s:%d" % (s["file"], s["line"])
    ann = CLASSIFICATION.get(key)
    r = reach_info(s["fid"])
    h = harness_info(s["fid"])
    cn1_sites.append({"site": key, "file": s["file"], "line": s["line"], "enclosing_function": s["function"], "tree": s["tree"],
                      "argv_construction": s["argv_expr"], "program_launched": ("valgrind (callgrind) -> " if s.get("wrapper_prefix") else "") + str(s["program"]),
                      "launch_chain_to_primitive": s["launch_chain"], "source_line": s["source_line"],
                      "classification": ann if ann else "UNANNOTATED (no recorded reading; see census.md)",
                      "reachable": bool(r), "reached_by_commands": [{"plan": x["plan"], "command": x["command"]} for x in r],
                      "call_chains": {"%s %s" % (x["plan"], x["command"]): x["call_chain"] for x in r},
                      "reached_by_harness_processes": h,
                      "callers": callers_of(s["fid"])})
# the v1 launcher's own callers (the launch function is called from these v1 sites)
cn1_unresolved = [{"site": "%s:%d" % (s["file"], s["line"]), "function": s["function"], "callee": s["callee"], "argv_expr": s["argv_expr"],
                   "tree": s["tree"], "manual_reading": s.get("manual_argv_reading"), "reachable": bool(reach_info(s["fid"]))} for s in UNRESOLVED]

reachable_classified = [x for x in cn1_sites if x["reachable"] and x["classification"] != "UNANNOTATED" and
                        (x["classification"].get("classified") is True)]
reachable_other = [x for x in cn1_sites if x["reachable"] and x not in reachable_classified]
OUT["CN1_msolve_launch_census"] = {
    "definition_applied": "healthresolve pre_approval_readings.definitions (MSOLVE LAUNCH SITE, CLASSIFIED, REACHABLE), verbatim",
    "trees_scanned": {k: v for k, v in TREES.items()},
    "outside_files_executed_or_imported": {
        "executed": [{"path": EXTERNAL_INPUTS["k4a"], "by": "v2_driver.cmd_anchor_identity line 650 (Sage python child)",
                      "msolve_launches_in_it": [x["site"] for x in cn1_sites if x["file"] == EXTERNAL_INPUTS["k4a"]],
                      "child_launches_in_it": [s["line"] for s in SITES if s["file"] == EXTERNAL_INPUTS["k4a"]]}],
        "read_as_data_only": [{"path": EXTERNAL_INPUTS["k5k7"] + "/square_analogue_n3.json", "by": "v2_common.fixture_n3 (line 199)"},
                              {"path": EXTERNAL_INPUTS["k5k7"] + "/square_analogue_n4.json", "by": "v2_common.fixture_n4 (line 218)"},
                              {"path": TREES["v1"] + "/ladder.json", "by": "v2_common.load_ladder (line 142); a1_common.LADDER_PATH"}],
        "scanned_although_not_executed": [x for x in tree_files(EXTERNAL_INPUTS["k5k7"]) if x.endswith(".py")],
        "imports_resolving_outside_the_trees": sorted({a[1] for m in SRC for a in MODINFO[m]["aliases"].values() if a[1] not in INTERNAL}),
        "v1_modules_imported_by_v2_or_later": sorted({"%s imports %s" % (m, a[1]) for m in SRC if MOD_TREE.get(m) in ("v2", "a1", "r1", "r2")
                                                      for a in MODINFO[m]["aliases"].values() if a[1] in INTERNAL and MOD_TREE.get(a[1]) == "v1"}),
    },
    "commands": cmp_cmds,
    "sites": cn1_sites,
    "unresolved_argv_sites_reviewed": cn1_unresolved,
    "embedded_code_strings": EMBEDDED,
    "reading": {
        "reachable_msolve_launch_sites": [x["site"] for x in cn1_sites if x["reachable"]],
        "reachable_sites_classified_by_the_literal_definition": [x["site"] for x in cn1_sites if x["reachable"] and (
            x["classification"].get("classified") is True or x["site"].endswith("v2_driver.py:209"))],
        "unreachable_sites": [x["site"] for x in cn1_sites if not x["reachable"]],
    },
}

# ---------------------------------------------------------------------------------------------------------------------
# CN-2 (i)-(ix)
# ---------------------------------------------------------------------------------------------------------------------
CN2 = {}
CN2["i"] = {
    "log_text_a1_health": [cite(A1 + "/a1_health.py", 145, "logp, errp = os.path.join(out_dir, tag + \".ms.log\"), os.path.join(out_dir, tag + \".ms.err\")"),
                           cite(A1 + "/a1_health.py", 157, "text = \"\""), cite(A1 + "/a1_health.py", 158, "for f in (logp, errp):"),
                           cite(A1 + "/a1_health.py", 160, "text += open(f, errors=\"replace\").read() + \"\\n\""),
                           cite(A1 + "/a1_health.py", 161, "except OSError:")],
    "log_text_v2_driver": [cite(V2 + "/v2_driver.py", 170, "text = \"\""), cite(V2 + "/v2_driver.py", 171, "for ext in (\".ms.log\", \".ms.err\"):"),
                           cite(V2 + "/v2_driver.py", 173, "text += open(os.path.join(sd, tag + ext), errors=\"replace\").read() + \"\\n\""),
                           cite(V2 + "/v2_driver.py", 174, "except OSError:")],
    "classify_only_when_child_ok": [cite(A1 + "/a1_health.py", 167, "if rec.get(\"outcome\") == \"ok\":"),
                                    cite(A1 + "/a1_health.py", 182, "outcome, reason = V.classify_solve(rec, st, kind, payload, sinfo, nfail or 0)"),
                                    cite(A1 + "/a1_health.py", 183, "else:"),
                                    cite(A1 + "/a1_health.py", 184, "outcome, reason = rec.get(\"outcome\"), rec.get(\"refusal_reason\")")],
    "no_file_removed_by_a1_health": "os.remove" not in SRC["a1_health"]["text"],
    "differences_noted": [
        "a1_health passes nfail or 0 (line 182) where v2_driver passes nfail initialised to 0 (lines 191, 197): same value.",
        "on a non-ok child a1_health records reason = rec.refusal_reason (line 184); v2_driver records classify_solve's (outcome, None) (v2_solver.py 490-491) except refused_to_start (v2_driver.py 184-185). Neither is an SSF class.",
        "a1_health keeps .ms.log/.ms.err in out_dir after return (no os.remove in a1_health.py), so the text can be rebuilt after the frozen run_system returns."],
}
# (ii) reason strings
cs = FNS["v2_solver:classify_solve"].node
rets = []
for n in ast.walk(cs):
    if isinstance(n, ast.Return) and isinstance(n.value, ast.Tuple):
        rets.append({"line": n.lineno, "return": ast.unparse(n.value)[:220]})
CN2["ii"] = {
    "classify_solve_returns": sorted(rets, key=lambda x: x["line"]),
    "SF-1_clauses_vs_code": [
        {"clause": "(i) exact 'eliminating polynomial is not square-free'", "code": cite(V2 + "/v2_solver.py", 498, "return \"degenerate_parametrisation\", \"eliminating polynomial is not square-free\"")},
        {"clause": "(ii) begins 'eliminating polynomial degree '", "code": cite(V2 + "/v2_solver.py", 501, "return \"degenerate_parametrisation\", (\"eliminating polynomial degree %s != quotient dimension %s \"")},
        {"clause": "(iii) begins 'msolve reports square-free part degree '", "code": cite(V2 + "/v2_solver.py", 505, "return \"degenerate_parametrisation\", \"msolve reports square-free part degree %s != quotient dimension %s\"")},
        {"clause": "(iv) ends 'parsed solution(s) fail substitution into the descended system'", "code": cite(V2 + "/v2_solver.py", 507, "return \"degenerate_parametrisation\", \"%d parsed solution(s) fail substitution into the descended system\" % n_sub_fail")},
        {"clause": "(v) positive_dimensional (+ random-form string in the log text)", "code": [cite(V2 + "/v2_solver.py", 493, "return \"positive_dimensional\""), cite(V2 + "/v2_solver.py", 495, "return \"positive_dimensional\"")]}],
    "run_system_carries_them_unmodified": [cite(A1 + "/a1_health.py", 182, "outcome, reason = V.classify_solve("),
                                           cite(A1 + "/a1_health.py", 185, "res[\"v2_outcome_class\"] = outcome"),
                                           cite(A1 + "/a1_health.py", 186, "res[\"v2_outcome_reason\"] = reason")],
    "other_writes_of_v2_outcome_class_or_reason_in_any_scanned_file": sorted(
        "%s:%d" % (SRC[m]["path"], i + 1) for m in SRC for i, l in enumerate(SRC[m]["lines"])
        if re.search(r"\[\s*[\"']v2_outcome_(class|reason)[\"']\s*\]\s*=", l)),
    "r2_ssf_clause_function_matches_SF-1": [cite(R2 + "/r2_resolve.py", 62, "if reason == \"eliminating polynomial is not square-free\":"),
                                            cite(R2 + "/r2_resolve.py", 64, "if reason.startswith(\"eliminating polynomial degree \"):"),
                                            cite(R2 + "/r2_resolve.py", 66, "if reason.startswith(\"msolve reports square-free part degree \"):"),
                                            cite(R2 + "/r2_resolve.py", 68, "if reason.endswith(\"parsed solution(s) fail substitution into the descended system\"):")],
}
# (iii) call-time global lookup of run_system (bytecode of the in-memory compile; nothing written)


def code_obj(path_rel, qual):
    co = compile(open(os.path.join(REPO, path_rel)).read(), os.path.join(REPO, path_rel), "exec", dont_inherit=True)
    stack = [co]
    while stack:
        c = stack.pop()
        if c.co_qualname == qual:
            return c
        stack += [k for k in c.co_consts if hasattr(k, "co_code")]
    return None


run_co = code_obj(A1 + "/a1_health.py", "run")
loads = [{"line": ins.positions.lineno, "opname": ins.opname, "argval": ins.argval} for ins in dis.get_instructions(run_co)
         if ins.argval == "run_system"]
refs_rs = sorted("%s:%d %s" % (SRC[m]["path"], i + 1, l.strip()[:140]) for m in SRC for i, l in enumerate(SRC[m]["lines"]) if "run_system" in l)
from_imports = sorted("%s:%d %s" % (SRC[m]["path"], n.lineno, ast.unparse(n)) for m in SRC for n in ast.walk(SRC[m]["tree"])
                      if isinstance(n, ast.ImportFrom) and n.module == "a1_health")
run_def = FNS["a1_health:run"].node
CN2["iii"] = {
    "run_system_loads_in_a1_health_run_bytecode": loads,
    "all_are_LOAD_GLOBAL": all(x["opname"] == "LOAD_GLOBAL" for x in loads) and len(loads) == 4,
    "call_lines": sorted({x["line"] for x in loads}),
    "run_defaults_capture_run_system": any("run_system" in ast.unparse(d) for d in run_def.args.defaults + run_def.args.kw_defaults if d is not None),
    "every_textual_occurrence_of_run_system_in_scanned_files": refs_rs,
    "from_a1_health_import_anywhere": from_imports,
    "modules_calling_run_system": sorted({c["caller"].split(":")[0] for c in callers_of("a1_health:run_system")}),
    "a1_driver_H_is_a1_health": cite(A1 + "/a1_driver.py", 38, "import a1_health as H"),
    "compile_note": "compiled in memory with compile(); no byte code written (python3 -B, sys.dont_write_bytecode)",
}
# (iv) callers of a1_health.run and run_system
CN2["iv"] = {
    "callers_of_a1_health.run": [dict(c, reached_by=[{"plan": x["plan"], "command": x["command"]} for x in reach_info(c["caller"])])
                                 for c in callers_of("a1_health:run")],
    "callers_of_a1_health.run_system": [dict(c, reached_by=[{"plan": x["plan"], "command": x["command"]} for x in reach_info(c["caller"])])
                                        for c in callers_of("a1_health:run_system")],
    "a1_driver_129_passes_reinvoke_on_fail": "reinvoke_on_fail" in SRC["a1_driver"]["lines"][128],
    "run_default_reinvoke_on_fail": cite(A1 + "/a1_health.py", 223, "reinvoke_on_fail=False"),
    "commands_reaching_run_system": [{"plan": x["plan"], "command": x["command"], "call_chain": x["call_chain"]} for x in reach_info("a1_health:run_system")],
}
# (v) DEV_TIMEOUT_S
rs_co = code_obj(A1 + "/a1_health.py", "run_system")
CN2["v"] = {
    "definition": cite(A1 + "/a1_health.py", 53, "DEV_TIMEOUT_S = 1800"),
    "use": cite(A1 + "/a1_health.py", 147, "timeout_s=DEV_TIMEOUT_S"),
    "bytecode_loads_in_run_system": [{"line": i.positions.lineno, "opname": i.opname} for i in dis.get_instructions(rs_co) if i.argval == "DEV_TIMEOUT_S"],
    "every_occurrence_in_scanned_files": sorted("%s:%d %s" % (SRC[m]["path"], i + 1, l.strip()[:140]) for m in SRC for i, l in enumerate(SRC[m]["lines"]) if "DEV_TIMEOUT_S" in l),
    "run_system_signature_has_timeout_parameter": "timeout" in " ".join(FNS["a1_health:run_system"].params),
}
# (vi) substitution premise + round trip
CN2["vi"] = {
    "write": cite(A1 + "/a1_health.py", 143, "wi = A.write_msolve_input(inp, NAMES, p, eqs)"),
    "substitute_same_eqs": [cite(A1 + "/a1_health.py", 172, "V.substitute(eqs, s, p)"), cite(A1 + "/a1_health.py", 178, "param_substitution(payload, eqs, p, len(NAMES))")],
    "dense_system_coefficients": cite(A1 + "/a1_health.py", 59, "rng.randrange(1, p)"),
    "draw": [cite(A1 + "/a1_health.py", 64, "rng = random.Random(seed)"), cite(A1 + "/a1_health.py", 65, "return {degs: dense_system(rng, p, degs) for degs in PATTERNS}")],
    "retry_draw": cite(A1 + "/a1_health.py", 240, "retry = draw(seed + \":2\", p)"),
    "parse_ms_file_range": [cite(V2 + "/v2_driver.py", 582, "def _parse_ms_file(path):"), cite(V2 + "/v2_driver.py", 606, "eq[tuple(e)] = (eq.get(tuple(e), 0) + c) % p"),
                            cite(V2 + "/v2_driver.py", 608, "return names, p, eqs")],
    "write_msolve_input_range": [cite(V2 + "/v2_arms.py", 691, "def write_msolve_input(path, names, p, eqs):"),
                                 cite(V2 + "/v2_arms.py", 698, "if c == 0:"), cite(V2 + "/v2_arms.py", 701, "terms.append(f\"{c}*{mono}\" if mono else f\"{c}\")")],
}
# module-level statements of every module the permitted imports load (LC-1 pre-check)
premods = ["v2_arms", "v2_driver", "v2_common", "v2_lift", "v2_scoring", "v2_solver", "v2_verify_independent", "v2_child", "v2_field", "a1_health", "a1_common"]
modlevel = {}
for m in premods:
    stmts = []
    for st in SRC[m]["tree"].body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)):
            continue
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant):
            continue
        calls = sorted({ast.unparse(n.func) for n in ast.walk(st) if isinstance(n, ast.Call)})
        if calls or isinstance(st, ast.If):
            stmts.append({"line": st.lineno, "stmt": ast.unparse(st)[:160], "calls": calls})
    modlevel[m] = stmts
CN2["vi"]["lc1_import_precheck_module_level_statements_with_calls"] = modlevel
kids_before = children_now()
sys.path.insert(0, os.path.join(REPO, V2))
sys.path.insert(0, os.path.join(REPO, A1))
import a1_common as _AC       # noqa: E402
import v2_arms as _A          # noqa: E402
import a1_health as _H        # noqa: E402
import v2_driver as _D        # noqa: E402
kids_after = children_now()
imported_from = {m: os.path.relpath(sys.modules[m].__file__, REPO) for m in sorted(sys.modules) if m.startswith(("v2_", "a1_"))}
bytecode_dirs = [os.path.join(REPO, t, "__pycache__") for t in (V2, A1)]
PRIME = 1073741831
rt = []
sysdir = os.path.join(SCRATCH, "health-systems")
os.makedirs(sysdir, exist_ok=True)
for seed in (_AC.HEALTH_SEED, _AC.HEALTH_SEED + ":2"):
    systems = _H.draw(seed, PRIME)
    for degs in _H.PATTERNS:
        tag = "health_p%d_d%s%s" % (PRIME, "".join(map(str, degs)), "" if seed == _AC.HEALTH_SEED else "_seed2")
        f = os.path.join(sysdir, tag + ".ms")
        wi = _A.write_msolve_input(f, _H.NAMES, PRIME, systems[degs])
        g = os.path.join(sysdir, tag + ".roundtrip.ms")
        names, p2, eqs2 = _D._parse_ms_file(f)
        wi2 = _A.write_msolve_input(g, names, p2, eqs2)
        bf, bg = open(f, "rb").read(), open(g, "rb").read()
        first_diff = None
        if bf != bg:
            first_diff = next((i for i in range(min(len(bf), len(bg))) if bf[i] != bg[i]), min(len(bf), len(bg)))
        coeffs = [c for eq in systems[degs] for c in eq.values()]
        rt.append({"seed": seed, "pattern": list(degs), "tag": tag, "file": rel(f) if f.startswith(REPO) else f,
                   "sha256": sha_bytes(bf), "bytes": len(bf), "write_info": wi,
                   "roundtrip_sha256": sha_bytes(bg), "roundtrip_bytes": len(bg), "roundtrip_write_info": wi2,
                   "byte_identical": bf == bg, "first_differing_byte_offset": first_diff,
                   "parsed_names": names, "parsed_p": p2, "parsed_equals_drawn_system": eqs2 == [dict(e) for e in systems[degs]],
                   "n_equations": len(systems[degs]), "n_terms": sum(len(e) for e in systems[degs]),
                   "coefficient_min": min(coeffs), "coefficient_max": max(coeffs), "all_coefficients_in_1_to_p_minus_1": all(1 <= c <= PRIME - 1 for c in coeffs)})
CN2["vi"]["import_check"] = {"child_pids_before_import": kids_before, "child_pids_after_import": kids_after,
                             "guard_blocked_attempts": list(GUARD["blocked_attempts"]), "modules_imported_from": imported_from,
                             "health_seed": _AC.HEALTH_SEED, "names": _H.NAMES, "patterns": [list(x) for x in _H.PATTERNS],
                             "expected": {str(list(k)): v for k, v in _H.EXPECTED.items()}}
CN2["vi"]["round_trip_p_1073741831"] = rt
CN2["vi"]["round_trip_all_byte_identical"] = all(x["byte_identical"] for x in rt) and len(rt) == 4
CN2["vi"]["solver_run_on_them"] = "none"
# (vii) failure recording
CN2["vii"] = {
    "pass_predicate": [cite(A1 + "/a1_health.py", 188, "checks = {"), cite(A1 + "/a1_health.py", 198, "res[\"checks\"] = checks"), cite(A1 + "/a1_health.py", 199, "res[\"pass\"] = all(checks.values())")],
    "signal_classification_only_on_failure": [cite(A1 + "/a1_health.py", 202, "if not res[\"pass\"]:"), cite(A1 + "/a1_health.py", 218, "res[\"solver_side_signal\"] = sig")],
    "re_draw": [cite(A1 + "/a1_health.py", 238, "if not r[\"pass\"]:"), cite(A1 + "/a1_health.py", 239, "if retry is None:"),
                cite(A1 + "/a1_health.py", 240, "retry = draw(seed + \":2\", p)"), cite(A1 + "/a1_health.py", 241, "r2 = run_system(p, retry[degs], degs, tag + \"_seed2\", out_dir, cap)")],
    "pattern_pass": cite(A1 + "/a1_health.py", 245, "entry[\"pattern_pass\"] = r[\"pass\"] or bool(entry.get(\"retry_seed2\", {}).get(\"pass\"))"),
    "report_pass": cite(A1 + "/a1_health.py", 247, "report[\"pass\"] = all(e[\"pattern_pass\"] for e in report[\"systems\"])"),
    "written": cite(A1 + "/a1_health.py", 251, "health-%d.json"),
    "controls_a1_records": [cite(A1 + "/a1_driver.py", 130, "hr[\"pass\"]"), cite(A1 + "/a1_driver.py", 132, "\"D\": e[\"first\"][\"dimension_of_quotient_printed\"]"),
                            cite(A1 + "/a1_driver.py", 187, "allok = all(c[\"pass\"] for c in checks)"), cite(A1 + "/a1_driver.py", 208, "\"gate_pass\": allok")],
    "notes": ["A failed first draw is kept in the report (entry['first']) with its checks, v2_outcome_class/reason and solver_side_signal; the re-draw result is entry['retry_seed2'].",
              "The ':2' systems are drawn once (lazily, on the first failing pattern) as draw(seed + ':2', p), i.e. BOTH patterns from one Random stream in PATTERNS order; the (4,4,4) re-draw system is the second draw of that stream whichever pattern failed first.",
              "a1_driver's check (d) detail records per pattern only pattern_pass and the FIRST draw's D and getrlimit (lines 131-133); the full record is health/health-<p>.json.",
              "check (d) failing makes controls_a1 gate_pass false (lines 187, 208) and run_status failed with failure_class infrastructure_error only if a failed check's detail carries an infrastructure outcome class at the keys a1_driver inspects (lines 188-205); the health detail dict carries no 'outcome' key, so a failed check (d) is classed implementation_error by those lines unless another failed check is infrastructure-classed."]}
CN2["vii"]["notes_basis"] = [cite(A1 + "/a1_driver.py", 196, "outs.append(d.get(\"outcome\"))"), cite(A1 + "/a1_driver.py", 205, "fclass = None if allok else (\"infrastructure_error\" if infra else \"implementation_error\")")]
# (viii) maximum classified msolve launches per controls-a1 command (from the code)
cm = FNS["a1_driver:cmd_controls_a1"]
solve_calls = [c["line"] for c in cm.calls if c["target"] and c["target"][1] == "v2_driver:solve"]
h_calls = [c["line"] for c in cm.calls if c["target"] and c["target"][1] == "a1_health:run"]
rs_calls = [c["line"] for c in FNS["a1_health:run"].calls if c["target"] and c["target"][1] == "a1_health:run_system"]
solve_kw = [ast.unparse(c["node"]) for c in cm.calls if c["target"] and c["target"][1] == "v2_driver:solve"]
CN2["viii"] = {
    "planted_arm_solves": {"call_lines": solve_calls, "loop": cite(A1 + "/a1_driver.py", 143, "for arm in (\"torsion_S3_rq\", \"S3_rescaled\"):"),
                           "per_arm_max": 1, "arms": 2, "max": 2, "callgrind_timeout_passed": any("callgrind_timeout" in s for s in solve_kw),
                           "gb_only_passed": any("gb_only" in s for s in solve_kw), "calls": solve_kw},
    "health_launches": {"H.run_call_lines": h_calls, "run_system_call_lines": rs_calls, "patterns": 2,
                        "per_pattern_max_with_reinvoke_false": "first draw (234) + at most one seed-':2' re-draw (241); the reinvocations at 237 and 244 need reinvoke_on_fail true",
                        "max": 4},
    "other_msolve_launch_sites_reachable_from_controls-a1": sorted({x["site"] for x in cn1_sites if any(r["command"] == "controls-a1" for r in x["reached_by_commands"])}),
    "maximum_classified_msolve_launches_frozen_code": 6,
    "CORR-20260924-5b83a1_item_2_value": 6,
    "confirms_CORR_item_2": True,
    "derived_not_measured_note": ("With the r2 layer as delivered (SE-3 wraps solve() only) the 2 planted solves can each make up to K + 1 = 6 "
                                  "attempts: at most 2 x 6 + 4 = 16 classified launches. With HR-3 as drafted, each of the 4 wrapped "
                                  "run_system calls can also make up to 6 attempts: at most 2 x 6 + 4 x 6 = 36. Derived from code and draft "
                                  "text; not a measurement; both further bounded by the SF-2 (c) / HR-6 caps."),
}
# (ix) watchdogs / timeouts spanning more than one run_system call in the controls_a1 package
CN2["ix"] = {
    "per_child_timeouts_only": [cite(A1 + "/a1_health.py", 147, "timeout_s=DEV_TIMEOUT_S"),
                                cite(A1 + "/a1_driver.py", 166, "C.watchdog(ctx.plan, arm, 3)[\"per_target_timeout_s\"]"),
                                cite(A1 + "/a1_driver.py", 146, "ctx.plan[\"watchdogs\"][\"builder_timeout_s\"][\"m3\"]"),
                                cite(A1 + "/a1_pari.py", 28, "PARI_TIMEOUT_S = 7200")],
    "a1_health.run_deadline": "none: no clock is read in a1_health.run (lines 223-253) and no aggregate timeout is passed",
    "a1_health_run_reads_time": "time." in "\n".join(SRC["a1_health"]["lines"][222:253]),
    "cmd_controls_a1_deadline": "none: t0 (line 59) feeds only metrics.wall_seconds (line 210)",
    "cmd_controls_a1_time_uses": sorted("a1_driver.py:%d %s" % (i + 56, l.strip()[:120]) for i, l in enumerate(SRC["a1_driver"]["lines"][55:215]) if "time." in l),
    "entry_process_timeout": "none in r2_entry_a1 (no alarm, no timer)",
    "wrapper_timeout_on_the_driver_child": [cite(R2 + "/r2_run_wrapper.py", 437, "proc = subprocess.run(cmd, cwd=R.REPO, env=child_env, stdout=so, stderr=se)"),
                                            cite(R2 + "/r2_run_wrapper.py", 36, "LAUNCH RULE")],
    "plan_watchdogs_for_the_package": {"package_watchdogs_field": [p for p in plans["a1r2"]["packages"] if p["order"] == 1][0]["watchdogs"],
                                       "per_cell_no_measurement_watchdog": "evaluated only in v2_driver._run_cell (cells); not in controls-a1",
                                       "plan_watchdog_keys": sorted(plans["a1r2"]["watchdogs"].keys())},
    "other_spanning_limits_in_code": "none found. Not in code: dispatcher-level lane claim TTLs and task wall-clock budgets of the run card (not scanned; the R2b''-successor card does not exist yet).",
    "sum_bound_note": ("Derived from code, not measured: the 4 health launches are each capped at DEV_TIMEOUT_S = 1800 s (4 x 1800 s = 7200 s of "
                       "child wall time at most, plus the frozen launch overhead); HR-6 as drafted adds per wrapped call less than 1800 s of "
                       "re-solve wall time beyond attempt 2 (sum of attempts 2..k < 1800 s before a further attempt starts, and the last "
                       "attempt itself up to 1800 s)."),
}
OUT["CN2_health_path_facts"] = CN2


def find_line(path_rel, token, start=1):
    for i, l in enumerate(open(os.path.join(REPO, path_rel)).read().splitlines(), 1):
        if i >= start and token in l:
            return cite(path_rel, i, token)
    CITE_FAILS.append({"path": path_rel, "line": None, "token": token})
    return {"file": path_rel, "line": None, "token": token, "present": False}


# ---------------------------------------------------------------------------------------------------------------------
# stage-r2 bundle: extract ONLY into the scratchpad (after LC-2 (d) passed), verify members, read dv1
# ---------------------------------------------------------------------------------------------------------------------
bdir = os.path.join(SCRATCH, "stage-r2-bundle")
os.makedirs(bdir, exist_ok=True)
bundle = {"path": R2_BUNDLE, "sha256": sha_file(os.path.join(REPO, R2_BUNDLE)), "extracted_to": bdir}
with tarfile.open(os.path.join(REPO, R2_BUNDLE)) as tf:
    names = tf.getnames()
    bundle["n_members"] = len(names)
    want = [n for n in names if n.startswith("stage-r2-dv/dv1/") or n == "stage-r2-dv/MEMBERS.sha256"]
    for n in want:
        m = tf.getmember(n)
        if not m.isfile():
            continue
        data = tf.extractfile(m).read()
        dst = os.path.join(bdir, n)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as fh:
            fh.write(data)
man = {}
mp = os.path.join(bdir, "stage-r2-dv/MEMBERS.sha256")
for line in open(mp).read().splitlines():
    parts = line.split()
    if len(parts) >= 2:
        man[parts[-1].lstrip("*").lstrip("./")] = parts[0]
dv1 = {}
for n in sorted(os.listdir(os.path.join(bdir, "stage-r2-dv/dv1"))):
    p = os.path.join(bdir, "stage-r2-dv/dv1", n)
    h = sha_file(p)
    keyc = [k for k in man if k.endswith("dv1/" + n)]
    dv1[n] = {"sha256": h, "bytes": os.path.getsize(p), "MEMBERS.sha256_entry": man.get(keyc[0]) if keyc else None,
              "matches_MEMBERS": (man.get(keyc[0]) == h) if keyc else None}
bundle["dv1_members"] = dv1
bundle["MEMBERS.sha256_sha256"] = sha_file(mp)
probe_src = open(os.path.join(bdir, "stage-r2-dv/dv1/sage_pari_probe.py")).read()
probe_out = open(os.path.join(bdir, "stage-r2-dv/dv1/sage_pari_probe.stdout")).read()
probe_err = open(os.path.join(bdir, "stage-r2-dv/dv1/sage_pari_probe.stderr")).read()
bundle["sage_pari_probe"] = {"script_text": probe_src, "stdout_text": probe_out, "stderr_text": probe_err}
try:
    st = json.load(open(os.path.join(bdir, "stage-r2-dv/dv1/dv1_static.json")))
    bundle["dv1_static_top_level_keys"] = sorted(st.keys()) if isinstance(st, dict) else type(st).__name__
except Exception as e:                                   # noqa: BLE001
    bundle["dv1_static_top_level_keys"] = "unparseable: %r" % (e,)
OUT["stage_r2_bundle"] = bundle

# ---------------------------------------------------------------------------------------------------------------------
# CN-3: PARI inventory
# ---------------------------------------------------------------------------------------------------------------------
pari_fns = []
for fid, fn in FNS.items():
    hits = []
    for n in own_nodes(fn):
        if isinstance(n, ast.Import) and any(a.name == "cypari2" for a in n.names):
            hits.append(n.lineno)
        elif isinstance(n, ast.ImportFrom) and n.module == "cypari2":
            hits.append(n.lineno)
    if hits:
        pari_fns.append((fid, sorted(set(hits))))
n3 = json.load(open(os.path.join(REPO, EXTERNAL_INPUTS["k5k7"], "square_analogue_n3.json")))
n4 = json.load(open(os.path.join(REPO, EXTERNAL_INPUTS["k5k7"], "square_analogue_n4.json")))
OUT["files_read"][EXTERNAL_INPUTS["k5k7"] + "/square_analogue_n3.json"] = sha_file(os.path.join(REPO, EXTERNAL_INPUTS["k5k7"], "square_analogue_n3.json"))
OUT["files_read"][EXTERNAL_INPUTS["k5k7"] + "/square_analogue_n4.json"] = sha_file(os.path.join(REPO, EXTERNAL_INPUTS["k5k7"], "square_analogue_n4.json"))


def n3_degree(p):
    ent = next(e for e in n3["primes"] if e["p"] == p)
    m = re.fullmatch(r"F_(\d+)\[z\]/\(z\^(\d+) - (\d+)\)", ent["field"])
    return int(m.group(2)), ent["field"]


mm4 = re.fullmatch(r"GF\((\d+)\^4\) modulus (.*)", n4["result"]["field"])
N4 = (int(n4["result"]["p"]), 4, n4["result"]["field"])
DV2_POINTS = [(4111, 3), (16777291, 3), (4111, 4)]
PS = EXP_REL + "/amendments/v2_addendum_paristack.yaml"
dv2_basis = [find_line(PS, "(4111, n = 3, the fixture_n3(4111) curve)"), find_line(PS, "(16777291, n = 3, the fixture_n3(16777291) curve)"),
             find_line(PS, "(4111, n = 4, the fixture_n4 curve)")]
fix_ps = sorted({int(r["driver_args"][2]) for r in plans["v2r2"]["packages"] if (r.get("driver_args") or [None])[0] == "fixture"})
reach_points = {
    "fixture": [{"p": p, "degree": n3_degree(p)[0], "field": n3_degree(p)[1], "curve": "fixture_n3(%d)" % p,
                 "basis": [cite(V2 + "/v2_driver.py", 278, "fx = C.fixture_n3(args.p)"), cite(V2 + "/v2_driver.py", 308, "N = C.curve_order_pari(F, E)")]} for p in fix_ps],
    "fixture4": [{"p": N4[0], "degree": N4[1], "field": N4[2], "curve": "fixture_n4()",
                  "basis": [cite(V2 + "/v2_driver.py", 529, "fx = C.fixture_n4()"), cite(V2 + "/v2_driver.py", 542, "N = C.curve_order_pari(F, E)")]}],
    "controls": [{"p": 4111, "degree": n3_degree(4111)[0], "field": n3_degree(4111)[1], "curve": "fixture_n3(4111)",
                  "basis": [cite(V2 + "/v2_driver.py", 764, "fx = C.fixture_n3(4111)"), cite(V2 + "/v2_driver.py", 771, "N = C.curve_order_pari(F, E)")]}],
}
inproc = []
for fid, lines in pari_fns:
    r = reach_info(fid)
    h = harness_info(fid)
    ent = {"function": fid, "file": SRC[FNS[fid].mod]["path"], "import_cypari2_lines": lines, "tree": MOD_TREE.get(FNS[fid].mod),
           "reached_by_commands": sorted({(x["plan"], x["command"]) for x in r}), "reached_by_harness": [x["process"] for x in h]}
    if fid == "v2_common:curve_order_pari":
        pts = []
        for cmd, lst in reach_points.items():
            for x in lst:
                pts.append(dict(x, command=cmd, covered_by_DV2=(x["p"], x["degree"]) in DV2_POINTS))
        ent["points_reached"] = pts
        ent["stack_configuration"] = {"branch": "PS-1 P-A (r2 plans' repair.ps1_branch)", "parisize": 67108864, "parisizemax": 536870912,
                                      "basis": [cite(R2 + "/r2_common.py", 149, "PARISIZE = 67108864"), cite(R2 + "/r2_common.py", 150, "PARISIZEMAX = 536870912"),
                                                cite(R2 + "/r2_common.py", 239, "h.allocatemem(PARISIZE, PARISIZEMAX, silent=True)"),
                                                cite(R2 + "/r2_entry_v2.py", 36, "stack.configure()")]}
        ent["handle"] = cite(V2 + "/v2_common.py", 253, "pari = cypari2.Pari()")
        ent["a1_plan_reaches_it"] = any(x[0] == "trial-plan-v2-a1-r2.json" for x in ent["reached_by_commands"])
        ent["ladder_prime_n5_reached"] = any(x["p"] in (262151, 16777291, 1073741831) and x["degree"] == 5 for x in pts)
    inproc.append(ent)
curve_order_callers = callers_of("v2_common:curve_order_pari")
gp_facts = {
    "site": cite(A1 + "/a1_pari.py", 96, "rec = V.run_child(argv, so, se, cap_bytes=cap, timeout_s=timeout_s, count_instructions=False)"),
    "argv": cite(A1 + "/a1_pari.py", 94, "argv = [GP, \"-q\", \"-f\", \"--default\", \"nbthreads=1\", gpf]"),
    "stack_set_by_script": [cite(A1 + "/a1_pari.py", 38, "default(parisize, 256000000);"), cite(A1 + "/a1_pari.py", 38, "default(parisizemax, 4000000000);")],
    "parisize": 256000000, "parisizemax": 4000000000,
    "note": "gp starts with -q -f (no gprc) and nbthreads=1; the script's first two lines set the stack before any computation",
    "process": "capped child (v2_solver.run_child, RLIMIT_AS = cap)",
    "reached_by_commands": sorted({(x["plan"], x["command"]) for x in reach_info("a1_pari:curve_facts")}),
    "points_reached": [{"command": "controls-a1", "p": 1073741831, "degree": 5, "curves": "the three ladder curves of rung 1073741831 (AC.SHAPES)",
                        "basis": [cite(A1 + "/a1_driver.py", 69, "F = C.ladder_field(rung)"), cite(V2 + "/v2_common.py", 154, "Fq.binomial(rung[\"p\"], 5, rung[\"cmod\"])"),
                                  cite(A1 + "/a1_driver.py", 89, "pr = P.curve_facts(p, list(F.modulus), curves, pari_dir, \"controls_a1_pari\")")]}],
    "fb1_curve_search_reachable": bool(reach_info("a1_pari:fb1_curve_search")),
}
gp_version_children = [
    {"site": cite(A1 + "/a1_pari.py", 121, "subprocess.run([GP, \"--version-short\"]"), "process": "UNCAPPED child (subprocess.run, not run_child), timeout 30 s",
     "computation": "none (version string)", "stack": "gp defaults (no default() set; no computation)",
     "reached_by_commands": sorted({(x["plan"], x["command"]) for x in reach_info("a1_pari:gp_version")})},
    {"site": cite(R2 + "/r2_run_wrapper.py", 412, "\"pari_gp\": sh(\"gp --version-short 2>&1 | head -1\")"), "process": "UNCAPPED shell child of the wrapper process, timeout 60 s",
     "computation": "none (version string)", "stack": "gp defaults", "reached_by": "r2_run_wrapper.launch, every package"}]
sage = {
    "site": cite(V2 + "/v2_driver.py", 650, "rec = V.run_child([C.SAGE_PYTHON, C.COMPARATOR, cdir]"),
    "script": EXTERNAL_INPUTS["k4a"], "script_sha256": sha_file(os.path.join(REPO, EXTERNAL_INPUTS["k4a"])),
    "python": const_of("v2_common", "SAGE_PYTHON"),
    "process": "capped child (v2_solver.run_child), timeout comparator_timeout_s",
    "comparator_timeout_s": plans["v2r2"]["watchdogs"]["comparator_timeout_s"],
    "reached_by_commands": sorted({(x["plan"], x["command"]) for x in reach_info("v2_driver:cmd_anchor_identity")}),
    "pari_uses_in_script": [cite(EXTERNAL_INPUTS["k4a"], 158, "N = int(E.order())"), cite(EXTERNAL_INPUTS["k4a"], 36, "#E(F_q) by PARI SEA (via Sage)")],
    "other_library_field_arithmetic_in_script": "GF(p), GF(p**5, modulus=...), PolynomialRing, EllipticCurve, is_irreducible, resultant, matrix rank / solve_right (Sage library; which backend each uses is not determined statically and no Sage process was started)",
    "points_reached": [{"p": 16777291, "degree": 5, "label": "RUN-GFPN-61bba9 (anchor25)", "basis": cite(EXTERNAL_INPUTS["k4a"], 72, "p=16777291, cmod=2")},
                       {"p": 65551, "degree": 5, "label": "RUN-GFPN-bbed6f (anchor17)", "basis": cite(EXTERNAL_INPUTS["k4a"], 77, "p=65551, cmod=2")}],
    "degree_basis": cite(EXTERNAL_INPUTS["k4a"], 135, "modulus = Zv ** 5 - cmod"),
    "loop_over_both_curves": cite(EXTERNAL_INPUTS["k4a"], 309, "for label, cv in CURVES.items():"),
    "stack_configuration": {"set_by_code": "none (the comparator sets no PARI stack; the driver passes no env or flag for it)",
                            "start_up_probe_from_bundle": {"member_stdout": "stage-r2-dv/dv1/sage_pari_probe.stdout", "stdout_text": probe_out,
                                                           "member_script": "stage-r2-dv/dv1/sage_pari_probe.py"}},
}
OUT["CN3_PARI_inventory"] = {
    "in_process_cypari2_entries_all_trees": inproc,
    "curve_order_pari_call_sites": curve_order_callers,
    "DV2_points_paristack_PS6": {"points": DV2_POINTS, "basis": dv2_basis},
    "gp_children": {"curve_facts": gp_facts, "version_probes": gp_version_children},
    "sage_comparator_child": sage,
    "r2_dv1_note": "DEC-20260924-bea197 R-5 quotes parisize 8000000 / parisizemax 1073741824 for the Sage child (DV-1 probe); the census reads the probe's own stdout above.",
}

# ---------------------------------------------------------------------------------------------------------------------
# CN-4: every other child launch reachable from the successor plans' commands (and the per-package harness processes)
# ---------------------------------------------------------------------------------------------------------------------
CN4_ANN = {
    V2 + "/v2_common.py:129": {"child": "shell: grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 (host scan)", "via": "v2_common.host_record <- v2_driver.Ctx.__init__ (line 63)",
                               "classified": "no: recorded in raw-result host block (v2_driver.finish line 79); not compared by REG-1 (not in its compared items)",
                               "clock": "no (60 s subprocess timeout only)", "seed": "no", "environment": "yes: host CPU"},
    V2 + "/v2_common.py:131": {"child": "shell: dpkg-query -W -f='${Version}' msolve (package query; msolve is NOT executed)", "via": "v2_common.host_record",
                               "classified": "no: host block only", "clock": "no", "seed": "no", "environment": "yes: installed package database"},
    V2 + "/v2_common.py:132": {"child": "shell: dpkg-query libmsolve-* (package query)", "via": "v2_common.host_record", "classified": "no: host block only",
                               "clock": "no", "seed": "no", "environment": "yes: installed package database"},
    V2 + "/v2_common.py:136": {"child": "shell: dpkg-query -W -f='${Version}' msolve (package query)", "via": "v2_common.msolve_version <- v2_driver.Ctx.__init__ (line 64)",
                               "classified": "no classifier; recorded as envelope.msolve_version and, in anchor-identity, raw['msolve_version'] (line 639) and in envelope tuples",
                               "clock": "no", "seed": "no", "environment": "yes: installed package database"},
    V2 + "/v2_driver.py:101": {"child": "python3 -B implementation-v2/v2_child.py <spec.json> (builder: build_poly / raw_grid); sys.executable", "via": "v2_driver.child_job <- build_poly (122) / raw_grid (136)",
                               "classified": "yes: the built polynomial / grid defines the systems solved; build outcome and meta (single-flip, held-out) enter checks (e.g. a1_driver check (f) lines 179-186; fixture F-checks)",
                               "clock": "timeout_s (builder_timeout_s) -> outcome timeout; meta seconds_total recorded", "seed": "yes, declared: random.Random(spec['sample_seed']) and ':flip' / ':releq' streams (v2_child.py 72, 88, 94); seeds are deterministic strings from the driver",
                               "environment": "inherits the driver env; output path under C.CACHE_DIR when to_cache (GFPN_V2_CACHE_DIR / TMPDIR; v2_common.py 42)",
                               "launches_in_script": "none (v2_child.py has no launch call)"},
    V2 + "/v2_driver.py:650": {"child": "Sage python /opt/conda-sage/envs/sage/bin/python k4a_anchor_system.py <cdir> (comparator)", "via": "cmd_anchor_identity",
                               "classified": "yes: its random target x_R and anchor25_random.ms feed the anchor trace-identity gate (v2_driver.py 659-669, 704-720); failure -> infrastructure_error, gate_pass false (655-658)",
                               "clock": "comparator_timeout_s (run_child); inside the script alarm(240) around E.order() (k4a 156) -> order not computed if it fires", "seed": "yes, declared in the script: random.Random('TASK-20260923-58953e:K4a:%d' % p), set_random_seed(20260923 + p) (k4a 198-199)",
                               "environment": "inherits the driver env; the Sage installation at a fixed path", "launches_in_script": "none (k4a_anchor_system.py has no launch call)"},
    V2 + "/v2_solver.py:533": {"child": "callgrind_annotate --inclusive=yes <out> (UNCAPPED subprocess.run, not run_child; PATH lookup)", "via": "v2_solver.callgrind_instructions, after an ok valgrind child",
                               "classified": "its output sets f4_core_function / f4_core_note (compared by REG-1 (b); not excluded) and f4_core_inclusive_Ir (excluded, X17)",
                               "clock": "timeout 600 s -> exception -> f4_core_note 'callgrind_annotate failed: ...' (a compared field)", "seed": "no", "environment": "yes: PATH resolution of callgrind_annotate"},
    V2 + "/v2_solver.py:517": {"child": "valgrind --tool=callgrind <msolve argv> (see CN-1)", "via": "v2_solver.callgrind_instructions <- v2_driver.solve 209",
                               "classified": "see CN-1 site v2_driver.py:209", "clock": "callgrind_timeout_s", "seed": "the msolve child it runs is the same argv as the solve (FGLM clock seed)", "environment": "valgrind at /usr/bin/valgrind"},
    A1 + "/a1_pari.py:96": {"child": "/usr/bin/gp -q -f --default nbthreads=1 <script.gp> (capped)", "via": "a1_pari.curve_facts <- a1_driver.cmd_controls_a1 line 89",
                            "classified": "yes: controls_a1 check (b) (a1_driver.py 92-112)", "clock": "PARI_TIMEOUT_S 7200 (a1_pari.py 28)", "seed": "none set by the script (no setrand)",
                            "environment": "gp binary at /usr/bin/gp; -f skips gprc"},
    A1 + "/a1_pari.py:121": {"child": "/usr/bin/gp --version-short (UNCAPPED subprocess.run, timeout 30)", "via": "a1_pari.gp_version <- a1_driver.cmd_controls_a1 line 90",
                             "classified": "no: recorded as detail_b.pari.gp_version inside check (b)'s detail", "clock": "timeout 30 s -> 'ERROR ...' string recorded", "seed": "no",
                             "environment": "yes: installed gp"},
}
HARNESS_ANN = {
    "git": {"children": "git -C <repo> rev-parse HEAD / branch --show-current / log -1 --format=%H -- <paths> (x3 + receipts) / status --porcelain / ls-files / status --porcelain --untracked-files=all",
            "classified": "yes for tree_check (R-4..R-6 refusals: tracked, clean, receipt file lists) and phase_a_commit; environment.json git block otherwise",
            "clock": "no", "seed": "no", "environment": "yes: repository state"},
    "sh": {"children": "dpkg-query msolve; python3 -c (flint / numpy / yaml / cypari2 version); gp --version-short | head -1; valgrind --version (all UNCAPPED shell children, timeout 60 s)",
           "classified": "no: environment.json dependencies block", "clock": "no", "seed": "no", "environment": "yes: PATH-resolved python3, gp, valgrind"},
    "driver": {"children": "python3 -B r2_entry_{v2,a1}.py <driver_args> (the command itself), env PYTHONHASHSEED=0, PYTHONDONTWRITEBYTECODE=1, GFPN_RUN_DIR ...; no timeout (no outer guard)",
               "classified": "the command", "clock": "no timeout", "seed": "PYTHONHASHSEED=0 set", "environment": "inherits os.environ plus the listed variables"},
    "check_run": {"children": "python3 -B r2_check_run.py frozen-v2|frozen-a1 <run dir> (runs the frozen v2_check_run / a1_check_run)",
                  "classified": "yes: checker verdict", "clock": "no", "seed": "no", "environment": "inherits env"},
}
cn4_rows = []
covered = set()
for s in SITES:
    if s["msolve_in_argv"] is True and not s["caller_entry_of_fixed_program_launcher"]:
        continue
    if s["forwarding"] and not s.get("fixed_prefix_here"):
        continue
    r = reach_info(s["fid"])
    if not r:
        continue
    key = "%s:%d" % (s["file"], s["line"])
    covered.add(key)
    cn4_rows.append({"site": key, "function": s["function"], "program": s["program"], "argv_expr": s["argv_expr"],
                     "reached_by_commands": sorted({(x["plan"], x["command"]) for x in r}),
                     "example_call_chain": r[0]["call_chain"], "reading": CN4_ANN.get(key, "UNANNOTATED")})
harness_rows = []
for s in SITES:
    if s["forwarding"] and not s.get("fixed_prefix_here"):
        continue
    h = harness_info(s["fid"])
    if not h:
        continue
    key = "%s:%d" % (s["file"], s["line"])
    grp = ("git" if "git" in str(s["program"]).split(" (")[0].split("/")[-1] or s["callee"].endswith(":git") or "git_tree_state" in s["callee"]
           or "tree_check" in s["callee"] or "phase_a_commit" in s["callee"] else
           "sh" if s["callee"].endswith(":sh") else "driver" if s["line"] == 437 and s["file"].endswith("r2_run_wrapper.py") else
           "check_run" if s["file"].endswith("r2_check_run.py") else "other")
    harness_rows.append({"site": key, "function": s["function"], "program": s["program"], "argv_expr": s["argv_expr"], "processes": [x["process"] for x in h],
                         "group": grp, "reading": HARNESS_ANN.get(grp) if grp in HARNESS_ANN else (CN4_ANN.get(key) or "UNANNOTATED")})
cg_args = [{"line": c["line"], "call": ast.unparse(c["node"])[:200], "fid": f} for f, fn in FNS.items() for c in fn.calls
           if c["target"] and c["target"][1] in ("v2_driver:solve",) and "callgrind_timeout" in ast.unparse(c["node"])]
OUT["CN4_other_child_launches"] = {
    "driver_process_sites_reachable_from_commands": cn4_rows,
    "unannotated_driver_sites": [r["site"] for r in cn4_rows if r["reading"] == "UNANNOTATED"],
    "harness_process_sites": harness_rows,
    "unannotated_harness_sites": [r["site"] for r in harness_rows if r["reading"] == "UNANNOTATED"],
    "callgrind_argument_level_note": {"solve_calls_passing_callgrind_timeout": cg_args,
                                      "reading": "static reachability counts the callgrind child wherever solve() is reachable; only fixture_core (line 358, callgrind_timeout_s.m3) and _run_cell (line 1175, target 0 of an m <= 4 cell) pass a callgrind_timeout, and it runs only after an ok outcome (line 207)"},
    "python_children_scripts": {"v2_child.py": [x for x in SITES if x["file"].endswith("v2_child.py")],
                                "k4a_anchor_system.py": [x for x in SITES if x["file"] == EXTERNAL_INPUTS["k4a"]]},
}

# ---------------------------------------------------------------------------------------------------------------------
# closing: frozen/preserved bytes unchanged, no child started after the guard, no byte code written
# ---------------------------------------------------------------------------------------------------------------------
after = {}
changed = []
for c in INTEG["checks"]:
    if c.get("path") and c.get("actual_sha256"):
        now = sha_file(os.path.join(REPO, c["path"]))
        if now != c["actual_sha256"]:
            changed.append(c["path"])
pyc = []
for t in (V2, A1, TREES["r1"], R2):
    for dp, dn, fnames in os.walk(os.path.join(REPO, t)):
        pyc += [rel(os.path.join(dp, f)) for f in fnames if f.endswith(".pyc")]
v1pyc = {rel(os.path.join(REPO, V1, "__pycache__", f)): os.stat(os.path.join(REPO, V1, "__pycache__", f)).st_mtime
         for f in sorted(os.listdir(os.path.join(REPO, V1, "__pycache__")))} if os.path.isdir(os.path.join(REPO, V1, "__pycache__")) else {}
OUT["closing_checks"] = {
    "bound_files_unchanged_at_end": not changed, "changed": changed,
    "pyc_under_v2_a1_r1_r2_trees": pyc,
    "pre_existing_v1_pycache_files_mtime": v1pyc,
    "child_pids_at_end": children_now(),
    "guard_blocked_attempts": GUARD["blocked_attempts"],
    "census_children_started": OUT["census_children_started"],
    "citation_failures": CITE_FAILS,
    "n_citations_checked": N_CITES[0],
}
OUT["counts"] = {"modules_scanned": len(SRC), "functions": len(FNS), "launch_calls_found": len(SITES),
                 "msolve_launch_sites": len(cn1_sites), "launchers_inferred": len(LAUNCHERS)}
OUT["launchers_inferred"] = {k: dict(v, via=list(v["via"])) for k, v in LAUNCHERS.items()}
OUT["all_launch_calls"] = [{k: v for k, v in s.items() if k != "fid"} for s in SITES]
OUT["inference"] = {"requested_policy": "executor-implementation", "resolved_model_id": None, "fallback_used": False, "bedrock_used": False}
write_out()
print("census.json written: %s" % os.path.join(OUT_DIR, "census.json"))
print("integrity pass: %s; msolve sites: %d; citation failures: %d; guard blocks: %d; children at end: %s" % (
    INTEG["pass"], len(cn1_sites), len(CITE_FAILS), len(GUARD["blocked_attempts"]), children_now()))
