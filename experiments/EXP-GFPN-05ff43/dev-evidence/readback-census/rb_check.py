#!/usr/bin/env python3
"""rb_check.py -- the zero-run, zero-solve READ-BACK CENSUS check script of TASK-20260924-bf5724.

EXP-GFPN-05ff43; DRAFT AMD-EXP-GFPN-05ff43-20260924-readbackcover (not approved), pre_approval_readings RBR-5, RBR-1,
RBR-2, RBR-3, RBR-4, computed exactly as the draft and the card (RBQ-1..RBQ-8) word them; ordered by
DEC-20260924-1ce186 R-7. OBSERVATIONS ONLY: nothing here is evidence about D, the quotient, H-GFPN-9a29be or
HEUR-GFPN-DFLAT, and nothing here is an approval recommendation.

usage:  PYTHONDONTWRITEBYTECODE=1 python3 -B rb_check.py --out <readback-census.json>

Phase 1 (RBR-5 / RBQ-2), INTEGRITY FIRST. Only read-only git children are launched, each with its argv recorded.
  Any failure of (a)-(e) writes the JSON with the failure and exits 3 before any reading.
Phase 2 (RBQ-1). An in-process guard (sys.addaudithook) is installed that REFUSES every child-process launch
  (subprocess.Popen, os.system, os.exec*, os.posix_spawn, os.spawn*, os.fork, os.forkpty, pty.spawn) and every import
  of a module whose name is the name of a .py file of a scanned tree. Its attempt counts are reported. It is
  self-tested with sys.audit() (which launches nothing and imports nothing).
Phase 3. The readings. Every source file is read as bytes and parsed with ast / tokenize, never imported. Every run
  package file is read from its phase-B-bound bytes: the sha256 of the bytes read is compared with the
  TASK-20260924-f1fb0e post-run receipt at read time. Every line cited by a disposition is re-checked against the
  file's text (citation checks). The capped-child instance table is tied to a static call graph built here: every
  path from a command to a capped launch must be covered by an instance, and every instance by a path.
Nothing is written except the --out file.
"""
import argparse
import ast
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import tokenize

import yaml

sys.dont_write_bytecode = True

REPO = "/home/user/crypto-autoresearcher"
EXP_REL = "experiments/EXP-GFPN-05ff43"
EXP = os.path.join(REPO, EXP_REL)
ARCH = os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/archives")
BASE_COMMIT = "dd103455380238ec2f20d17414de687acdcc822a"
ADDENDUM_REL = EXP_REL + "/amendments/v2_addendum_readbackcover.yaml"
ADDENDUM_SHA_CARD = "dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e"
GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
CAP = 10737418240
TASK_ID = "TASK-20260924-bf5724"

OUT = {"schema": "crypto.autoresearch.gfpn05.readback_census.v1", "task_id": TASK_ID, "experiment_id": "EXP-GFPN-05ff43",
       "draft": "AMD-EXP-GFPN-05ff43-20260924-readbackcover (DRAFT, not approved)", "ordered_by": "DEC-20260924-1ce186 R-7",
       "statement": ("observations only; nothing here is evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT; "
                     "no approval recommendation"),
       "started_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "python": sys.version.split()[0], "files_read_sha256": {}}
GIT_CHILDREN = []


# ============================================================================ helpers
def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def read_bytes(rel, record=True):
    with open(os.path.join(REPO, rel), "rb") as fh:
        b = fh.read()
    if record:
        OUT["files_read_sha256"][rel] = sha_bytes(b)
    return b


def load_json_rel(rel, record=True):
    return json.loads(read_bytes(rel, record))


def git(args):
    argv = ["git", "-C", REPO] + list(args)
    t0 = time.time()
    p = subprocess.run(argv, capture_output=True, text=True)
    GIT_CHILDREN.append({"argv": argv, "returncode": p.returncode, "seconds": round(time.time() - t0, 3),
                         "stdout_lines": len(p.stdout.splitlines()), "stderr": p.stderr.strip()})
    return p


def write_out(path):
    OUT["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT["git_children_integrity_phase_only"] = GIT_CHILDREN
    with open(path, "w") as fh:
        json.dump(OUT, fh, indent=1, sort_keys=False, default=str)
        fh.write("\n")


# ============================================================================ phase 1: integrity (RBR-5 / RBQ-2)
def integrity():
    res = {}
    # (a) the draft against the card value and the TASK-20260924-9c617a receipt's addendum_sha256
    lr = load_json_rel("coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-9c617a/ledger-receipt.json")
    got = sha_bytes(read_bytes(ADDENDUM_REL))
    rv = lr["addendum_sha256"]["sha256"]
    res["a_draft_addendum_sha256"] = {"path": ADDENDUM_REL, "card_value": ADDENDUM_SHA_CARD, "receipt_value": rv,
                                      "receipt_path_field": lr["addendum_sha256"]["path"], "computed": got,
                                      "ok": got == ADDENDUM_SHA_CARD == rv and lr["addendum_sha256"]["path"] == ADDENDUM_REL}
    # (b) the nine VA-1 files against DEC-20260924-e52eec bound_hashes (parsed with yaml; data only)
    dec = yaml.safe_load(read_bytes("ledger/decisions/DEC-20260924-e52eec.yaml"))
    dd = dec.get("coordinator_decision", dec)            # the record's top-level key (DEC-20260924-e52eec line 31)
    bh = {k: v for k, v in (dd.get("bound_hashes") or {}).items() if k != "note"}
    rows = {k: {"bound": v, "computed": sha_bytes(read_bytes(k)), "ok": sha_bytes(read_bytes(k, False)) == v} for k, v in bh.items()}
    res["b_nine_va1_amendment_files"] = {"n": len(bh), "rows": rows, "ok": len(bh) == 9 and all(r["ok"] for r in rows.values())}
    # (c) 22 phase-A paths and 801 phase-B paths of TASK-20260924-f1fb0e
    for name, n_exp in (("snapshot-receipt.json", 22), ("post-run-receipt.json", 801)):
        rel = "coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-f1fb0e/" + name
        rc = load_json_rel(rel)["path_sha256"]
        bad = []
        for p, h in rc.items():
            ap = os.path.join(REPO, p)
            if not os.path.exists(ap):
                bad.append({"path": p, "reason": "absent"})
                continue
            with open(ap, "rb") as fh:
                if sha_bytes(fh.read()) != h:
                    bad.append({"path": p, "reason": "sha256 differs"})
        res["c_TASK-20260924-f1fb0e_" + name] = {"receipt": rel, "n_paths": len(rc), "n_expected": n_exp, "mismatches": bad,
                                                  "ok": len(rc) == n_exp and not bad}
    # (d) implementation-v2/ and implementation-v2-a1/ against their phase-A receipts (every bound path, a superset of
    #     every file this census reads from those trees)
    for tid, tree in (("TASK-20260923-0fa03f", "implementation-v2/"), ("TASK-20260923-4ff597", "implementation-v2-a1/")):
        rel = "coordination/goals/GOAL-GFPN-380702/archives/%s/snapshot-receipt.json" % tid
        rcj = load_json_rel(rel)
        rc = rcj["path_sha256"]
        bad = [p for p, h in rc.items() if not os.path.exists(os.path.join(REPO, p)) or sha_bytes(read_bytes(p, False)) != h]
        on_disk = sorted(os.path.join(EXP_REL, tree, f) for f in os.listdir(os.path.join(EXP, tree)) if f.endswith(".py"))
        unbound = [p for p in on_disk if p not in rc]
        res["d_" + tid] = {"receipt": rel, "receipt_phase": rcj.get("phase"), "n_paths": len(rc), "mismatches": bad,
                           "tree_py_files_not_bound": unbound, "ok": not bad and not unbound}
    # (e) no change since the phase-B archive commit
    pathspecs = [EXP_REL + "/implementation*", EXP_REL + "/trial-plan-*.json"]
    p = git(["diff", "--stat", BASE_COMMIT, "--"] + pathspecs)
    ls = git(["ls-files", "--"] + pathspecs)
    res["e_git_diff_stat"] = {"argv": GIT_CHILDREN[-2]["argv"], "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                              "pathspec_sanity_ls_files_count": len(ls.stdout.splitlines()),
                              "ok": p.returncode == 0 and p.stdout == "" and len(ls.stdout.splitlines()) > 0}
    head = git(["rev-parse", "HEAD"]).stdout.strip()
    st = git(["status", "--porcelain", "--untracked-files=all"]).stdout.splitlines()
    res["repository_state"] = {"head": head, "status_porcelain": st}
    res["all_ok"] = all(v["ok"] for k, v in res.items() if isinstance(v, dict) and "ok" in v)
    return res


# ============================================================================ phase 2: the guard (RBQ-1)
GUARD = {"installed": False, "installed_utc": None, "launch_attempts": 0, "import_attempts": 0, "events": [],
         "self_test": {"mode": False, "launch_refused": None, "import_refused": None}}
LAUNCH_EVENTS = {"subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty", "pty.spawn",
                 "os.startfile"}
SCANNED_MODULE_NAMES = set()


def _hook(event, args):
    if not GUARD["installed"]:
        return
    if event in LAUNCH_EVENTS:
        if GUARD["self_test"]["mode"]:
            GUARD["self_test"]["launch_refused"] = event
        else:
            GUARD["launch_attempts"] += 1
            GUARD["events"].append({"event": event, "args": repr(args)[:200]})
        raise RuntimeError("rb_check guard (RBQ-1): child launch refused: %s" % event)
    if event == "import":
        name = str(args[0]).split(".")[0] if args else ""
        if name in SCANNED_MODULE_NAMES:
            if GUARD["self_test"]["mode"]:
                GUARD["self_test"]["import_refused"] = name
            else:
                GUARD["import_attempts"] += 1
                GUARD["events"].append({"event": "import", "module": name})
            raise ImportError("rb_check guard (RBQ-1): import of scanned-tree module %s refused" % name)


SCANNED_TREES = ["implementation", "implementation-v2", "implementation-v2-a1", "implementation-v2-r1", "implementation-v2-r2",
                 "implementation-v2-r3"]
COMPARATOR_REL = "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
K5K7_REL = "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7"


def scanned_py_files():
    out = []
    for t in SCANNED_TREES:
        d = os.path.join(EXP, t)
        for f in sorted(os.listdir(d)):
            if f.endswith(".py"):
                out.append(os.path.join(EXP_REL, t, f))
    out.append(COMPARATOR_REL)
    for f in sorted(os.listdir(os.path.join(REPO, K5K7_REL))):
        if f.endswith(".py"):
            out.append(os.path.join(K5K7_REL, f))
    return out


def install_guard():
    for rel in scanned_py_files():
        SCANNED_MODULE_NAMES.add(os.path.basename(rel)[:-3])
    sys.addaudithook(_hook)
    GUARD["installed"] = True
    GUARD["installed_utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    GUARD["self_test"]["mode"] = True
    try:
        sys.audit("subprocess.Popen", "/bin/true", ["/bin/true"], None, None)
    except RuntimeError:
        pass
    try:
        sys.audit("import", "v2_driver", None, None, None, None)
    except ImportError:
        pass
    GUARD["self_test"]["mode"] = False
    GUARD["scanned_module_names_refused"] = sorted(SCANNED_MODULE_NAMES)


# ============================================================================ phase 3: static index of the sources
FILES = {"v2d": EXP_REL + "/implementation-v2/v2_driver.py", "v2s": EXP_REL + "/implementation-v2/v2_solver.py",
         "v2c": EXP_REL + "/implementation-v2/v2_child.py", "v2k": EXP_REL + "/implementation-v2/v2_check_run.py",
         "v2cm": EXP_REL + "/implementation-v2/v2_common.py",
         "a1d": EXP_REL + "/implementation-v2-a1/a1_driver.py", "a1h": EXP_REL + "/implementation-v2-a1/a1_health.py",
         "a1p": EXP_REL + "/implementation-v2-a1/a1_pari.py", "a1k": EXP_REL + "/implementation-v2-a1/a1_check_run.py",
         "r3r": EXP_REL + "/implementation-v2-r3/r3_resolve.py", "r3w": EXP_REL + "/implementation-v2-r3/r3_run_wrapper.py",
         "r3c": EXP_REL + "/implementation-v2-r3/r3_check_run.py", "r3g": EXP_REL + "/implementation-v2-r3/r3_reg1.py",
         "r3x": EXP_REL + "/implementation-v2-r3/reg1-exclusion-list.json", "r3e2": EXP_REL + "/implementation-v2-r3/r3_entry_v2.py",
         "r3e1": EXP_REL + "/implementation-v2-r3/r3_entry_a1.py", "r3cm": EXP_REL + "/implementation-v2-r3/r3_common.py"}
TEXT = {}


def text_lines(rel):
    if rel not in TEXT:
        TEXT[rel] = read_bytes(rel).decode("utf-8", errors="replace").splitlines()
    return TEXT[rel]


class Mod:
    def __init__(self, rel):
        self.rel = rel
        self.name = os.path.basename(rel)[:-3]
        src = read_bytes(rel)
        TEXT[rel] = src.decode("utf-8", errors="replace").splitlines()
        self.tree = ast.parse(src, filename=rel)
        self.defs, self.parent = {}, {}
        self._collect(self.tree, "", None)
        self.aliases, self.from_imports = {}, {}
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.aliases[a.asname or a.name.split(".")[0]] = a.name
            elif isinstance(n, ast.ImportFrom) and n.module:
                for a in n.names:
                    self.from_imports[a.asname or a.name] = (n.module, a.name)

    def _collect(self, node, prefix, parent):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = prefix + ch.name
                self.defs[q] = ch
                self.parent[q] = parent
                self._collect(ch, q + ".", q)
            elif isinstance(ch, ast.ClassDef):
                self._collect(ch, prefix + ch.name + ".", parent)
            else:
                self._collect(ch, prefix, parent)

    def own_calls(self, qual):
        node = self.tree if qual == "<module>" else self.defs[qual]
        body = list(node.body)
        out = []
        stack = body[:]
        while stack:
            n = stack.pop()
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(n, ast.Call):
                out.append(n)
            stack.extend(ast.iter_child_nodes(n))
        return sorted(out, key=lambda c: (c.lineno, c.col_offset))

    def enclosing(self, line):
        best = None
        for q, d in self.defs.items():
            if d.lineno <= line <= d.end_lineno and (best is None or d.lineno >= self.defs[best].lineno):
                best = q
        return best or "<module>"


RUNTIME_DIRS = ["implementation-v2", "implementation-v2-a1"]
RUNTIME_R3 = ["r3_entry_v2.py", "r3_entry_a1.py", "r3_resolve.py", "r3_common.py"]
ALIAS_OVERRIDES = {"a1_driver": {"C": "v2_common"},        # a1_driver.py line 30: C = AC.redirect_v2() returns v2_common
                   "r3_resolve": {"V": "v2_solver"}}       # r3_resolve.py line 329: V = _STATE["v2_solver"] (install, line 435)
EXT_LAUNCH = {("subprocess", a) for a in ("run", "Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput")} | \
             {("os", a) for a in ("system", "popen", "execv", "execve", "execvp", "execvpe", "execl", "execlp", "fork", "forkpty",
                                  "posix_spawn", "posix_spawnp", "spawnv", "spawnve", "spawnl")}


def load_runtime():
    mods = {}
    for d in RUNTIME_DIRS:
        for f in sorted(os.listdir(os.path.join(EXP, d))):
            if f.endswith(".py"):
                m = Mod(os.path.join(EXP_REL, d, f))
                mods[m.name] = m
    for f in RUNTIME_R3:
        m = Mod(os.path.join(EXP_REL, "implementation-v2-r3", f))
        mods[m.name] = m
    for mn, ov in ALIAS_OVERRIDES.items():
        mods[mn].aliases.update(ov)
    return mods


def resolve(mods, mod, qual, call):
    f = call.func
    m = mods[mod]
    if isinstance(f, ast.Name):
        n = f.id
        q = qual
        while q not in (None, "<module>"):
            if (q + "." + n) in m.defs:
                return (mod, q + "." + n)
            q = m.parent.get(q)
        if n in m.defs:
            return (mod, n)
        if (n + ".__init__") in m.defs:                  # class instantiation
            return (mod, n + ".__init__")
        if n in m.from_imports:
            src, orig = m.from_imports[n]
            if src in mods and orig in mods[src].defs:
                return (src, orig)
        return None
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        base = m.aliases.get(f.value.id)
        if base is None:
            return None
        if base in mods:
            if f.attr in mods[base].defs:
                return (base, f.attr)
            if (f.attr + ".__init__") in mods[base].defs:  # class instantiation (e.g. D.Ctx())
                return (base, f.attr + ".__init__")
            return None
        return ("ext:" + base, f.attr)
    return None


def edges(mods, node, ctx):
    """Outgoing call edges of node = (module, qual, variant). ctx 'v2' (SE-3) or 'a1' (SE-3 + HR-3)."""
    mod, qual, variant = node
    out = []
    m = mods[mod]
    for c in m.own_calls(qual):
        t = resolve(mods, mod, qual, c)
        if t is None:
            continue
        if t[0].startswith("ext:"):
            if (t[0][4:], t[1]) in EXT_LAUNCH:
                out.append((c.lineno, ("ext", t[0][4:] + "." + t[1], ""), c))
            continue
        if t == ("v2_driver", "solve") and mod != "r3_resolve":
            t = ("r3_resolve", "solve")                      # SE-3: the module attribute is the r3 wrapper at run time
        if t == ("a1_health", "run_system") and mod != "r3_resolve" and ctx == "a1":
            t = ("r3_resolve", "run_system")                 # HR-3 (a1 entry only)
        out.append((c.lineno, (t[0], t[1], ""), c))
    # the wrappers call the ORIGINAL frozen function objects through _call_original (runtime binding captured at install)
    if (mod, qual) == ("r3_resolve", "solve"):
        for c in m.own_calls(qual):
            if isinstance(c.func, ast.Name) and c.func.id in ("_call_original", "_bounded"):
                out.append((c.lineno, ("v2_driver", "solve", "orig"), c))
    if (mod, qual) == ("r3_resolve", "run_system"):
        for c in m.own_calls(qual):
            if isinstance(c.func, ast.Name) and c.func.id == "_bounded":
                out.append((c.lineno, ("a1_health", "run_system", "orig"), c))
    return out


def node_key(node):
    return "%s:%s%s" % (node[0], node[1], "#original" if node[2] == "orig" else "")


def command_entries(mods):
    out = {}
    for plan, drv in (("v2-r3", "v2_driver"), ("v2-a1-r3", "a1_driver")):
        main = mods[drv].defs["main"]
        for n in ast.walk(main):
            if isinstance(n, ast.Dict) and n.keys and all(isinstance(k, ast.Constant) for k in n.keys):
                for k, v in zip(n.keys, n.values):
                    if isinstance(v, ast.Name):
                        out["%s %s" % (plan, k.value)] = ((drv, v.id, ""), "v2" if plan == "v2-r3" else "a1")
    return out


def reach_paths(mods, entry, ctx):
    capped, uncapped = [], []
    memo = {}

    def can_reach(node, seen):
        if node in memo:
            return memo[node]
        if node[0] == "ext":
            return True
        if node[0] not in mods or (node[1] not in mods[node[0]].defs):
            return False
        r = False
        for _ln, t, _c in edges(mods, node, ctx):
            if t == ("v2_solver", "run_child", "") or t[0] == "ext":
                r = True
            elif t not in seen and can_reach(t, seen | {t}):
                r = True
        memo[node] = r
        return r

    def dfs(node, path, seen):
        for ln, t, c in edges(mods, node, ctx):
            e = {"caller": node_key(node), "file": mods[node[0]].rel, "line": ln, "callee": node_key(t) if t[0] != "ext" else t[1]}
            if t == ("v2_solver", "run_child", ""):
                capped.append(path + [e])
            elif t[0] == "ext":
                if not (node[0] == "v2_solver" and node[1] == "_run_child_locked"):
                    uncapped.append(path + [e])
            elif t not in seen and can_reach(t, seen | {t}):
                dfs(t, path + [e], seen | {t})
    dfs(entry, [], {entry})
    return capped, uncapped


# ============================================================================ the capped-child instance table (RBR-1)
# Branches: 'ok' = child exited ok and <out>.meta.json carries the pair; 'refused_meta' = child exited ok but wrote a
# refusal meta WITHOUT the pair (v2_child.py 68, 80); 'no_meta' = timeout / memory_exhausted / crashed / nonzero exit /
# pre-exec read-back mismatch (no meta.json; the run_child record still carries the pair when the child reported one);
# 'recorded' = the attempt whose result the frozen function returned to its caller; 'ssf_earlier' = an attempt with the
# SSF signature that the r3 bounded rule renamed and re-solved (never returned to the frozen caller).
# For each branch: raw = the pair reaches raw-result.json under the key rlimit_as_child_getrlimit (RB-2 (a), the
# unchanged r3 key-name collection); meta = child/<tag>.meta.json carries rlimit_as_child_getrlimit (RB-2 (b));
# rb1 = RB-1 as worded records the pair in a solver-events.json attempt record (RB-2 (c)); "reading" = only if RB-1 is
# read to cover a gb_only pass-through call.
V2 = ["v2-r3"]
A1 = ["v2-a1-r3"]
B_BUILD_OK = {"branch": "ok", "raw": None, "meta": True, "rb1": False}


def inst(iid, commands, caller, launch, kind, tags, branches, raw_path, meta_path, returned, other_files, threads, cites,
         checks=(), launched=True, note=None):
    return {"id": iid, "commands": commands, "caller": {"file": FILES[caller[0]], "line": caller[1]},
            "launch_site": {"file": FILES[launch[0]], "line": launch[1]}, "kind": kind, "tags": tags, "launched_at_run_time": launched,
            "branches": branches, "readback": {"raw_result_write_path": raw_path, "child_meta_json": meta_path,
                                               "returned_to_S1_or_S2_wrapper": returned, "other_package_files": other_files},
            "threads_executed": threads, "cites": [{"file": FILES[f], "line": ln, "expect": s} for f, ln, s in cites],
            "static_checks": list(checks), "note": note}


TH_NA = {"applies": False, "reason": "not an msolve child; no threads-executed value is produced"}
TH_CG = {"applies": True, "raw_result": False, "package_file": False, "returned": False, "rb1": False,
         "reason": "the frozen callgrind record (v2_solver.py 519-520) carries no threads value; valgrind runs the msolve argv with -t 1"}
BUILD_CITES = [("v2d", 101, "V.run_child(argv"), ("v2d", 105, 'if rec.get("outcome") == "ok" and os.path.exists(mp)'),
               ("v2d", 124, '"child": _slim(rec)'), ("v2d", 126, '"child": _slim(rec)'), ("v2d", 128, '"child": _slim(rec)'),
               ("v2d", 151, '"rlimit_as_child_getrlimit"'), ("v2c", 90, '"rlimit_as_child_getrlimit": {"soft": soft, "hard": hard}'),
               ("v2c", 68, '"refused": True'), ("v2c", 80, '"refused": True'), ("v2c", 61, "child RLIMIT_AS read back: soft=%d hard=%d"),
               ("v2s", 227, 'rec["rlimit_as_child_getrlimit"] = {"soft": int(soft), "hard": int(hard)}')]
GRID_CITES = [("v2d", 136, "rec, meta, out = child_job(ctx, spec, tag, timeout_s)"), ("v2d", 138, '"child": _slim(rec)'),
              ("v2d", 147, 'return eqs, Cg, {"outcome": "ok", "child": _slim(rec), "meta": meta}'),
              ("v2c", 103, '"rlimit_as_child_getrlimit": {"soft": soft, "hard": hard}')]
S1_CITES = [("v2d", 166, "rec = V.run_child(argv"), ("v2d", 167, 'res["solver"] = _slim(rec)'),
            ("v2d", 169, 'res["threads_executed"] = V.threads_from_argv(argv)'),
            ("r3r", 185, '"child_rlimit_as_getrlimit": sol.get("rlimit_as_child_getrlimit")'),
            ("r3r", 277, "event = dict(event_head"), ("r3r", 263, "res = _call_original(original, args, kwargs)"),
            ("r3r", 319, "return res")]
S1_BRANCHES = lambda raw: [{"branch": "recorded", "raw": raw, "meta": False, "rb1": True},  # noqa: E731
                           {"branch": "ssf_earlier", "raw": False, "meta": False, "rb1": True,
                            "today": "r3 SSF event attempt record child_rlimit_as_getrlimit (r3_resolve.py 185, 277-279), read by no r3 collector"}]
S1_RET = "result['solver']['rlimit_as_child_getrlimit'] (v2_driver.py 167, _slim 151)"


def s1_threads(raw, raw_path):
    return {"applies": True, "raw_result": raw, "raw_result_write_path": raw_path, "package_file": False,
            "returned": "result['threads_executed'] (v2_driver.py 169)", "rb1": True}


INSTANCES = [
    # ---------------------------------------------------------------- v2-r3 fixture (G1, G2)
    inst("I-01", ["v2-r3 fixture"], ("v2d", 317), ("v2d", 101), "builder (build_poly)", "fixture_<arm> (4)",
         [{"branch": "ok", "raw": True, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "builds.<arm>.child.rlimit_as_child_getrlimit (also builds.<arm>.meta.rlimit_as_child_getrlimit on ok)",
         "child/fixture_<arm>.meta.json (ok branch only)", "not a wrapped call", ["child/fixture_<arm>.stdout (text line, v2_child.py 61)"],
         TH_NA, BUILD_CITES + [("v2d", 317, 'build_poly(ctx, F, E, arm, m, seed, "fixture_%s" % arm'), ("v2d", 321, 'raw["builds"] = builds')]),
    inst("I-02", ["v2-r3 fixture"], ("v2d", 348), ("v2d", 101), "builder (raw_grid)", "fx_<target>_<raw_x|raw_u> (2 per target)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "on failure only: targets[].arms.<arm>.reason.child.rlimit_as_child_getrlimit (v2_driver.py 350); on ok only construction_ops is kept (353)",
         "child/fx_<target>_<arm>.meta.json (ok branch)", "not a wrapped call", ["child/<tag>.stdout (text line)"], TH_NA,
         GRID_CITES + [("v2d", 348, 'raw_grid(ctx, F, E, kind, m, t["x_R"], nodes, tag'), ("v2d", 350, '"reason": ginfo'),
                       ("v2d", 353, 'cons = ginfo["meta"]["construction_ops"]')]),
    inst("I-03", ["v2-r3 fixture"], ("v2d", 358), ("v2d", 166), "S-1 solve (msolve)", "fx_<target>_<arm> (6 per target)",
         S1_BRANCHES(True), "targets[] | replaced_fresh_targets[] | planted_targets[] .arms.<arm>.solver.rlimit_as_child_getrlimit",
         None, S1_RET, [], s1_threads(True, "targets[]....arms.<arm>.threads_executed"),
         S1_CITES + [("v2d", 358, "r = solve(ctx, names, eqs, tag"), ("v2d", 359, '"threads_executed", "input", "solver"'),
                     ("v2d", 508, '"targets": rows, "replaced_fresh_targets": replaced, "planted_targets": planted_rows')]),
    inst("I-04", ["v2-r3 fixture"], ("v2d", 358), ("v2s", 517), "S-3 callgrind (valgrind -> msolve)", "<tag> of each ok S-1 attempt",
         [{"branch": "ok_solve_with_callgrind_timeout", "raw": True, "meta": False, "rb1": False}],
         "targets[]....arms.<arm>.instructions_callgrind.child.rlimit_as_child_getrlimit", None,
         "inside the S-1 result: result['instructions_callgrind']['child']['rlimit_as_child_getrlimit'] (RB-1 (b) as worded copies result['solver'][...] only)",
         ["solver-events.json S-3 record reg1_compared_fields_verbatim.child_values (r3_resolve.py 348-361; not an attempt record)"], TH_CG,
         [("v2d", 207, 'if callgrind_timeout and outcome == "ok"'), ("v2d", 209, 'res["instructions_callgrind"] = V.callgrind_instructions('),
          ("v2s", 517, "rec = run_child(vargv"), ("v2s", 519, '"rlimit_as_child_getrlimit"'), ("v2d", 360, '"instructions_callgrind"'),
          ("r3r", 349, 'rb = child.get("rlimit_as_child_getrlimit")')],
         checks=[{"kind": "call_has_keyword", "file": FILES["v2d"], "line": 358, "keyword": "callgrind_timeout", "expect": True}]),
    # ---------------------------------------------------------------- v2-r3 fixture4
    inst("I-05", ["v2-r3 fixture4"], ("v2d", 548), ("v2d", 101), "builder (build_poly)", "f4_<arm> (4)",
         [{"branch": "ok", "raw": True, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "builds.<arm>.child.rlimit_as_child_getrlimit", "child/f4_<arm>.meta.json (ok)", "not a wrapped call", ["child/<tag>.stdout (text line)"],
         TH_NA, BUILD_CITES + [("v2d", 548, "build_poly(ctx, F, E, arm, 4"), ("v2d", 551, 'raw["builds"] = builds')]),
    inst("I-06", ["v2-r3 fixture4"], ("v2d", 565), ("v2d", 166), "S-1 solve (msolve)", "f4_t<i>_<arm>", S1_BRANCHES(True),
         "targets[].arms.<arm>.solver.rlimit_as_child_getrlimit", None, S1_RET, [], s1_threads(True, "targets[].arms.<arm>.threads_executed"),
         S1_CITES + [("v2d", 565, 'r = solve(ctx, names, eqs, "f4_t%d_%s"'), ("v2d", 566, '"threads_executed", "input", "solver"'),
                     ("v2d", 575, "targets=rows")]),
    # ---------------------------------------------------------------- v2-r3 anchor-identity (G3)
    inst("I-07", ["v2-r3 anchor-identity"], ("v2d", 650), ("v2d", 650), "Sage comparator", "comparator (1)",
         [{"branch": "any_outcome", "raw": True, "meta": False, "rb1": False}], "comparator.child.rlimit_as_child_getrlimit", None,
         "not a wrapped call", [], TH_NA,
         [("v2d", 650, "V.run_child([C.SAGE_PYTHON, C.COMPARATOR, cdir]"), ("v2d", 652, 'comp["child"] = _slim(rec)'),
          ("v2d", 655, 'raw["comparator"] = comp')]),
    inst("I-08", ["v2-r3 anchor-identity"], ("v2d", 671), ("v2d", 101), "builder (build_poly)", "anchor_S4 (1)",
         [{"branch": "ok", "raw": True, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "build.child.rlimit_as_child_getrlimit", "child/anchor_S4.meta.json (ok)", "not a wrapped call", ["child/<tag>.stdout (text line)"],
         TH_NA, BUILD_CITES + [("v2d", 671, 'build_poly(ctx, F, E, "S4", 4'), ("v2d", 673, 'raw["build"] = binfo')]),
    inst("I-09", ["v2-r3 anchor-identity"], ("v2d", 693), ("v2d", 166), "S-1 solve (msolve -g 1; gb_only pass-through)",
         "anchor_<comparator_random|v2_t0..t2> (4)", [{"branch": "passthrough", "raw": True, "meta": False, "rb1": "reading"}],
         "targets[].solver.rlimit_as_child_getrlimit", None, S1_RET + " (returned through the r3 pass-through branch, r3_resolve.py 382-387)", [],
         s1_threads(True, "targets[].threads_executed"),
         S1_CITES + [("v2d", 693, "gb_only=True"), ("v2d", 697, '"threads_executed": r["threads_executed"]'), ("v2d", 699, '"solver": r["solver"]'),
                     ("v2d", 740, "targets=rows"), ("r3r", 382, "if gb_only:")]),
    inst("I-10", ["v2-r3 anchor-identity"], ("v2d", 711), ("v2d", 166), "S-1 solve (msolve -g 1; gb_only pass-through)",
         "anchor_comparator_system (1)", [{"branch": "passthrough", "raw": False, "meta": False, "rb1": "reading"}],
         "NONE: row['comparator_system'] keeps outcome, input and the trace only (v2_driver.py 713-716)", None,
         S1_RET + " (returned through the r3 pass-through branch, r3_resolve.py 382-387)", [],
         {"applies": True, "raw_result": False, "raw_result_write_path": None, "package_file": False,
          "returned": "result['threads_executed'] (v2_driver.py 169)", "rb1": "reading"},
         S1_CITES + [("v2d", 711, 'rc = solve(ctx, cn, ceqs, "anchor_comparator_system"'), ("v2d", 714, 'row["comparator_system"]["outcome"] = rc["outcome"]'),
                     ("v2d", 716, 'row["comparator_system"]["input"] = rc["input"]'), ("r3r", 382, "if gb_only:"),
                     ("r3r", 383, '"passthrough_calls_gb_only_true"'), ("r3r", 253, 'cnt["wrapped_calls"] += 1')],
         checks=[{"kind": "names_loaded", "file": FILES["v2d"], "func": "cmd_anchor_identity", "name": "rc",
                  "expect_attrs_or_subscripts": ["f4_rounds", "outcome", "input"]}],
         note=("RB-1 records 'EVERY attempt of EVERY wrapped call at S-1'. In the r3 layer's vocabulary a gb_only call is NOT a wrapped "
               "call: wrapped_calls is incremented only inside _bounded (r3_resolve.py 253), and gb_only calls are passed through and "
               "counted separately (382-387; RUN-GFPN-f5412a records wrapped_calls 0, passthrough_calls_gb_only_true 5). The draft does not "
               "say whether RB-1 covers pass-through calls. If it does not, this child has NO source.")),
    # ---------------------------------------------------------------- v2-r3 controls (G4)
    inst("I-11", ["v2-r3 controls"], ("v2d", 768), ("v2d", 101), "builder (build_poly)", "ctl_identity_n3 (1)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: info is never read after line 768; raw (924-930) holds checks whose details carry no child record", "child/ctl_identity_n3.meta.json (ok)",
         "not a wrapped call", ["child/ctl_identity_n3.stdout (text line, v2_child.py 61)"], TH_NA,
         BUILD_CITES + [("v2d", 768, 'pol, info = build_poly(ctx, F, E, "identity", 3'), ("v2d", 924, 'raw = {"kind": "frozen_controls"')],
         checks=[{"kind": "name_never_loaded", "file": FILES["v2d"], "func": "cmd_controls", "name": "info"}],
         note="refused_meta is unreachable for kind identity (x_in_Fp base; v2_child.py 65, 79)"),
    inst("I-12", ["v2-r3 controls"], ("v2d", 782), ("v2d", 101), "builder (raw_grid)", "ctl_raw_random, ctl_raw_planted (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: ginfo is never read after line 782", "child/ctl_raw_<label>.meta.json (ok)", "not a wrapped call",
         ["child/<tag>.stdout (text line)"], TH_NA,
         GRID_CITES + [("v2d", 782, 'eqs_raw, Cg, ginfo = raw_grid(ctx, F, E, "raw_x", 3')],
         checks=[{"kind": "name_never_loaded", "file": FILES["v2d"], "func": "cmd_controls", "name": "ginfo"}],
         note="refused_meta is unreachable for kind raw_x"),
    inst("I-13", ["v2-r3 controls"], ("v2d", 801), ("v2d", 101), "builder (build_poly)", "ctl_identity_n5_m3, ctl_identity_n5_m4 (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: the record is bound to _ (line 801)", "child/ctl_identity_n5_m<m>.meta.json (ok)", "not a wrapped call",
         ["child/<tag>.stdout (text line)"], TH_NA, BUILD_CITES + [("v2d", 801, 'pol5, _ = build_poly(ctx, F5, E5, "identity", m')],
         note="refused_meta is unreachable for kind identity"),
    inst("I-14", ["v2-r3 controls"], ("v2d", 805), ("v2d", 101), "builder (raw_grid)", "ctl_raw_n5_m3, ctl_raw_n5_m4 (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: the record is bound to _i (line 805)", "child/ctl_raw_n5_m<m>.meta.json (ok)", "not a wrapped call",
         ["child/<tag>.stdout (text line)"], TH_NA, GRID_CITES + [("v2d", 805, '_e, Cg5, _i = raw_grid(ctx, F5, E5, "raw_x", m')],
         checks=[{"kind": "name_never_loaded", "file": FILES["v2d"], "func": "cmd_controls", "name": "_i"}],
         note="refused_meta is unreachable for kind raw_x"),
    inst("I-15", ["v2-r3 controls"], ("v2d", 816), ("v2d", 101), "builder (build_poly)",
         "ctl_S3, ctl_S3_rescaled, ctl_torsion_S3_rq, ctl_torsion_S3_norm (4)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": False, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: the record is bound to _ (line 816)", "child/ctl_<arm>.meta.json (ok)", "not a wrapped call", ["child/<tag>.stdout (text line)"],
         TH_NA, BUILD_CITES + [("v2d", 816, 'polc, _ = build_poly(ctx, F5, E5, arm, 3')],
         note="refused_meta reachable for S3_rescaled / torsion_S3_rq (rescaling refusal) and torsion_S3_norm (no rational 2-torsion)"),
    inst("I-16", ["v2-r3 controls"], ("v2d", 786), ("v2d", 166), "S-1 solve (msolve)", "ctl_identity_random, ctl_identity_planted (2)",
         S1_BRANCHES(False), "NONE: the check detail keeps D and outcome only (v2_driver.py 792-795)", None, S1_RET, [],
         s1_threads(False, None), S1_CITES + [("v2d", 786, 's_id = solve(ctx, A.varnames("identity", 3), eqs_id, "ctl_identity_%s"'),
                                                ("v2d", 793, '"D_identity": s_id and s_id["D"]')]),
    inst("I-17", ["v2-r3 controls"], ("v2d", 787), ("v2d", 166), "S-1 solve (msolve)", "ctl_rawx_random, ctl_rawx_planted (2)",
         S1_BRANCHES(False), "NONE (v2_driver.py 792-795)", None, S1_RET, [], s1_threads(False, None),
         S1_CITES + [("v2d", 787, 's_raw = solve(ctx, A.varnames("raw_x", 3), eqs_raw, "ctl_rawx_%s"')]),
    inst("I-18", ["v2-r3 controls"], ("v2d", 841), ("v2d", 166), "S-1 solve (msolve)", "ctl_planted_<arm> (4)",
         S1_BRANCHES(False), "NONE: the check detail keeps outcome and counts only (v2_driver.py 845-846)", None, S1_RET, [], s1_threads(False, None),
         S1_CITES + [("v2d", 841, 's = solve(ctx, names, eqs, "ctl_planted_%s"'), ("v2d", 846, '{"outcome": s["outcome"], "n_rational_solutions"')]),
    # ---------------------------------------------------------------- build (v2-r3 and v2-a1-r3)
    inst("I-19", ["v2-r3 build", "v2-a1-r3 build"], ("v2d", 961), ("v2d", 101), "builder (build_poly, to_cache)",
         "build_<p>_<shape>_<arm>_m<m> (one per plan build item not refused before launch)",
         [{"branch": "ok", "raw": True, "meta": False, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "polynomials[].info.child.rlimit_as_child_getrlimit (also polynomials[].info.meta.rlimit_as_child_getrlimit on ok)",
         "NONE under child/: to_cache=True writes <tag>.meta.json to C.CACHE_DIR outside the package (v2_driver.py 96); a copy goes to polynomials/<tag>.meta.json when retained (969-970)",
         "not a wrapped call", ["polynomials/<tag>.meta.json (retained copies)", "child/<tag>.stdout (text line)"], TH_NA,
         BUILD_CITES + [("v2d", 962, "to_cache=True"), ("v2d", 963, 'row.update(outcome=info["outcome"], seed=seed, info=info)'),
                        ("v2d", 979, '"polynomials": rows'), ("v2d", 96, 'C.CACHE_DIR if spec.get("to_cache") else cd'),
                        ("a1d", 225, "D.cmd_build(args)")]),
    # ---------------------------------------------------------------- cells (v2-r3 and v2-a1-r3)
    inst("I-20", ["v2-r3 cells", "v2-a1-r3 cells"], ("v2d", 1161), ("v2d", 101), "builder (raw_grid)", "grid_<arm>_t<i> (raw arms, m <= 4)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": False, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: on ok only construction_ops is kept (1168); on failure the row keeps outcome and a reason STRING (1163), not the child record",
         "child/grid_<arm>_t<i>.meta.json (ok)", "not a wrapped call", ["child/<tag>.stdout (text line)"], TH_NA,
         GRID_CITES + [("v2d", 1161, 'raw_grid(ctx, F, E, kind, m, R[0], nodes, "grid_" + tag'),
                       ("v2d", 1163, 'reason="raw grid child: %s" % ginfo.get("reason")'),
                       ("v2d", 1168, 'row["construction_ops"] = ginfo["meta"]["construction_ops"]'), ("a1d", 234, "D.cmd_cells(args)")],
         note=("refused_meta: raw_u only; the same deterministic rescaling is computed at cell level first (v2_driver.py 1044-1050), so a "
               "child-side refusal is not expected; it is a static branch")),
    inst("I-21", ["v2-r3 cells", "v2-a1-r3 cells"], ("v2d", 1174), ("v2d", 166), "S-1 solve (msolve)", "<arm>_t<i>", S1_BRANCHES(True),
         "cells[].targets[].solver.rlimit_as_child_getrlimit", None, S1_RET, [], s1_threads(True, "cells[].targets[].threads_executed"),
         S1_CITES + [("v2d", 1174, "r = solve(ctx, names, eqs, tag"), ("v2d", 1179, '"threads_executed", "input", "solver"'),
                     ("v2d", 1093, '"cells": cells')]),
    inst("I-22", ["v2-r3 cells", "v2-a1-r3 cells"], ("v2d", 1174), ("v2s", 517), "S-3 callgrind (valgrind -> msolve)",
         "<arm>_t0 of each m <= 4 cell with an ok recorded attempt",
         [{"branch": "ok_solve_with_callgrind_timeout", "raw": True, "meta": False, "rb1": False}],
         "cells[].targets[].instructions_callgrind.child.rlimit_as_child_getrlimit", None,
         "inside the S-1 result: result['instructions_callgrind']['child']['rlimit_as_child_getrlimit']",
         ["solver-events.json S-3 record (not an attempt record)"], TH_CG,
         [("v2d", 1175, "callgrind_timeout=(cg_timeout if (cg_timeout and i == 0) else None)"), ("v2d", 1180, '"instructions_callgrind"'),
          ("v2d", 1089, "if m <= 4 else None"), ("v2s", 519, '"rlimit_as_child_getrlimit"')],
         checks=[{"kind": "call_has_keyword", "file": FILES["v2d"], "line": 1174, "keyword": "callgrind_timeout", "expect": True}]),
    # ---------------------------------------------------------------- v2-a1-r3 controls-a1
    inst("I-23", ["v2-a1-r3 controls-a1"], ("a1d", 89), ("a1p", 96), "gp (PARI)", "controls_a1_pari (1)",
         [{"branch": "any_outcome", "raw": True, "meta": False, "rb1": False}], "checks[b].detail.pari.child.rlimit_as_child_getrlimit", None,
         "not a wrapped call", [], TH_NA,
         [("a1d", 89, "pr = P.curve_facts("), ("a1p", 96, "rec = V.run_child(argv, so, se"), ("a1p", 98, '"rlimit_as_child_getrlimit"'),
          ("a1d", 91, 'detail_b = {"pari": pr'), ("a1d", 112, 'rec("b_pari_ellcard_recheck_and_double_odd_facts", ok_b, detail_b)'),
          ("a1d", 209, '"checks": checks')]),
]
for _ln, _nm, _launched, _note in ((234, "first", True, None), (241, "retry_seed2", True, "runs only when the first system fails (a1_health.py 238-242)"),
                                   (237, "reinvocation", False, "runs only if reinvoke_on_fail; controls-a1 calls H.run without it (default False, a1_health.py 223)"),
                                   (244, "retry_seed2_reinvocation", False, "runs only if reinvoke_on_fail (default False)")):
    INSTANCES.append(inst("I-24-" + _nm, ["v2-a1-r3 controls-a1"], ("a1h", _ln), ("a1h", 147), "S-2 health (msolve)",
                          "health_p<p>_d<pattern>%s (one per pattern)" % {"first": "", "retry_seed2": "_seed2", "reinvocation": "_reinvoke",
                                                                          "retry_seed2_reinvocation": "_seed2_reinvoke"}[_nm],
                          [{"branch": "recorded", "raw": False, "meta": False, "rb1": True},
                           {"branch": "ssf_earlier", "raw": False, "meta": False, "rb1": True,
                            "today": "r3 SSF event attempt record child_rlimit_as_getrlimit (r3_resolve.py 199), read by no r3 collector"}],
                          "NONE under the collected key: checks[d].detail.per_pattern[].getrlimit carries the FIRST system's pair under the key "
                          "'getrlimit' (a1_driver.py 133), which the r3 key-name collection does not read; retries are not in raw-result.json",
                          None, "result['child']['rlimit_as_child_getrlimit'] (a1_health.py 150)",
                          ["health/health-<p>.json systems[].<first|retry_seed2|...>.child.rlimit_as_child_getrlimit and getrlimit_read_backs (a1_health.py 248-252)"],
                          {"applies": True, "raw_result": False, "raw_result_write_path": None,
                           "package_file": "health/health-<p>.json systems[].<...>.threads_executed",
                           "returned": "result['threads_executed'] (a1_health.py 149)", "rb1": True},
                          [("a1d", 129, 'hr = H.run(p, os.path.join(ctx.rd, "health"), cap=ctx.cap)'),
                           ("a1d", 133, '"getrlimit": e["first"]["child"].get("rlimit_as_child_getrlimit")'),
                           ("a1h", 147, "rec = V.run_child(argv, logp, errp"), ("a1h", 149, '"threads_executed": V.threads_from_argv(argv)'),
                           ("a1h", 150, '"rlimit_as_child_getrlimit"'), ("a1h", 251, "health-%d.json"), ("a1h", 223, "reinvoke_on_fail=False"),
                           ("a1h", _ln, "run_system("), ("r3r", 199, '"child_rlimit_as_getrlimit": child.get("rlimit_as_child_getrlimit")'),
                           ("r3r", 408, "return _bounded(R.SITE_S2")],
                          checks=[{"kind": "call_lacks_keyword", "file": FILES["a1d"], "line": 129, "keyword": "reinvoke_on_fail"}],
                          launched=_launched, note=_note))
INSTANCES += [
    inst("I-25", ["v2-a1-r3 controls-a1"], ("a1d", 146), ("v2d", 101), "builder (build_poly)", "ctl_a1_torsion_S3_rq, ctl_a1_S3_rescaled (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": False, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         ("NONE under the collected key: checks[f].detail.<arm>.build_getrlimit carries the pair under the key 'build_getrlimit' "
          "(a1_driver.py 184); the failure detail of check (e) keeps outcome and reason only (163)"),
         "child/ctl_a1_<arm>.meta.json (ok)", "not a wrapped call", ["child/<tag>.stdout (text line)"], TH_NA,
         BUILD_CITES + [("a1d", 146, 'polc, info = D.build_poly(ctx, F, E5, arm, 3, seed, "ctl_a1_%s"'),
                        ("a1d", 163, '"build": {k: info.get(k) for k in ("outcome", "reason")}'), ("a1d", 184, '"build_getrlimit"')],
         note=("refused_meta: the rescaling refusal is pre-checked at a1_driver.py 139 with the same deterministic A.rescaling, so a "
               "child-side refusal is not expected; it is a static branch")),
    inst("I-26", ["v2-a1-r3 controls-a1"], ("a1d", 166), ("v2d", 166), "S-1 solve (msolve)", "ctl_a1_planted_<arm> (2)",
         S1_BRANCHES(False), ("NONE under the collected key: checks[e].detail.solver_getrlimit carries the pair under the key "
                              "'solver_getrlimit' (a1_driver.py 174)"), None, S1_RET, [],
         s1_threads(True, "checks[e].detail.threads_executed (a1_driver.py 173; the key the r3 threads collection reads)"),
         S1_CITES + [("a1d", 166, 's = D.solve(ctx, names, eqs, "ctl_a1_planted_%s"'), ("a1d", 173, '"threads_executed": s.get("threads_executed")'),
                     ("a1d", 174, '"solver_getrlimit"')]),
]
# callgrind children statically reachable through solve() but NEVER launched: the caller passes no callgrind_timeout
for _cmd, _f, _ln in (("v2-r3 fixture4", "v2d", 565), ("v2-r3 anchor-identity", "v2d", 693), ("v2-r3 anchor-identity", "v2d", 711),
                      ("v2-r3 controls", "v2d", 786), ("v2-r3 controls", "v2d", 787), ("v2-r3 controls", "v2d", 841),
                      ("v2-a1-r3 controls-a1", "a1d", 166)):
    INSTANCES.append(inst("I-NL-%s-%d" % (_f, _ln), [_cmd], (_f, _ln), ("v2s", 517), "S-3 callgrind (static path only)", "none",
                          [], None, None, None, [], TH_NA, [("v2d", 207, 'if callgrind_timeout and outcome == "ok"')],
                          checks=[{"kind": "call_lacks_keyword", "file": FILES[_f], "line": _ln, "keyword": "callgrind_timeout"}],
                          launched=False, note="never launched: callgrind_timeout defaults to None (v2_driver.py 158) and line 207 requires it"))


def sources_of(branch):
    s = []
    if branch.get("raw"):
        s.append("RB-2 (a) raw-result.json")
    if branch.get("meta"):
        s.append("RB-2 (b) child/*.meta.json")
    if branch.get("rb1") is True:
        s.append("RB-1 / RB-2 (c) solver-events.json attempt record")
    return s


# ============================================================================ static checks
def func_node(rel, name):
    tree = ast.parse(read_bytes(rel, False), filename=rel)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    return None


def call_at(rel, line):
    tree = ast.parse(read_bytes(rel, False), filename=rel)
    cands = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and n.lineno == line]
    return cands


def run_static_check(chk):
    k = chk["kind"]
    if k in ("call_has_keyword", "call_lacks_keyword"):
        cs = call_at(chk["file"], chk["line"])
        target = [c for c in cs if isinstance(c.func, (ast.Name, ast.Attribute)) and
                  (getattr(c.func, "id", None) or getattr(c.func, "attr", None)) in ("solve", "run", "H.run")]
        if not target:
            target = cs
        has = any(any(kw.arg == chk["keyword"] for kw in c.keywords) for c in target)
        ok = has if k == "call_has_keyword" else not has
        return dict(chk, observed_has_keyword=has, ok=ok)
    if k == "name_never_loaded":
        fn = func_node(chk["file"], chk["func"])
        loads = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id == chk["name"] and isinstance(n.ctx, ast.Load)]
        return dict(chk, loads_at_lines=loads, ok=not loads)
    if k == "names_loaded":
        fn = func_node(chk["file"], chk["func"])
        used = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == chk["name"]:
                if isinstance(n.slice, ast.Constant):
                    used.add(n.slice.value)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == chk["name"]:
                used.add("." + n.attr)
        return dict(chk, subscripts_read=sorted(used), ok=sorted(used) == sorted(chk["expect_attrs_or_subscripts"]))
    return dict(chk, ok=False, error="unknown check")


def citation_check(c):
    lines = text_lines(c["file"])
    ok = 1 <= c["line"] <= len(lines) and c["expect"] in lines[c["line"] - 1]
    return ok


# ============================================================================ RBR-1
def rbr1(mods):
    entries = command_entries(mods)
    per_cmd, uncovered_paths, all_uncapped = {}, [], {}
    inst_hits = {i["id"]: set() for i in INSTANCES}
    for cmd, (entry, ctx) in sorted(entries.items()):
        capped, uncapped = reach_paths(mods, entry, ctx)
        rows = []
        for path in capped:
            term = path[-1]
            path_lines = {(e["file"], e["line"]) for e in path}
            hit = [i["id"] for i in INSTANCES if cmd in i["commands"] and (i["caller"]["file"], i["caller"]["line"]) in path_lines
                   and (i["launch_site"]["file"], i["launch_site"]["line"]) == (term["file"], term["line"])]
            for h in hit:
                inst_hits[h].add(cmd)
            if not hit:
                uncovered_paths.append({"command": cmd, "path": path})
            rows.append({"launch_site": "%s:%d" % (term["file"], term["line"]), "enclosing": term["caller"],
                         "path": " > ".join("%s@%d" % (e["caller"], e["line"]) for e in path), "instances": hit})
        un = sorted({"%s:%d (%s) -> %s" % (p[-1]["file"], p[-1]["line"], p[-1]["caller"], p[-1]["callee"]) for p in uncapped})
        all_uncapped[cmd] = un
        per_cmd[cmd] = {"entry": node_key(entry), "runtime_binding": "SE-3" + (" + HR-3" if ctx == "a1" else ""),
                        "n_paths_to_capped_launch": len(capped), "paths": rows, "uncapped_launches_reachable": un}
    unmatched = [{"id": i, "commands_declared": [c for c in next(x for x in INSTANCES if x["id"] == i)["commands"]],
                  "commands_with_path": sorted(s)} for i, s in inst_hits.items()
                 if set(next(x for x in INSTANCES if x["id"] == i)["commands"]) != s]
    # citations and static checks
    cit = []
    for i in INSTANCES:
        for c in i["cites"]:
            cit.append({"instance": i["id"], "file": c["file"], "line": c["line"], "expect": c["expect"], "ok": citation_check(c)})
        i["static_check_results"] = [run_static_check(ch) for ch in i["static_checks"]]
    # readings
    table, no_source, reading_dependent, static_only = [], [], [], []
    for i in INSTANCES:
        if not i["launched_at_run_time"] and not i["branches"]:
            static_only.append({"id": i["id"], "commands": i["commands"], "kind": i["kind"],
                                "caller": "%s:%d" % (i["caller"]["file"], i["caller"]["line"]),
                                "launch_site": "%s:%d" % (i["launch_site"]["file"], i["launch_site"]["line"]), "note": i["note"],
                                "static_check_results": i["static_check_results"]})
            continue
        brs = []
        for b in i["branches"]:
            src = sources_of(b)
            row = {"branch": b["branch"], "sources_under_RB1_RB2_as_worded": src}
            if b.get("today"):
                row["today_in_package"] = b["today"]
            if b.get("rb1") == "reading":
                row["conditional_source"] = "RB-1 only if RB-1 is read to cover gb_only pass-through calls"
            brs.append(row)
            if not src:
                rec = {"instance": i["id"], "commands": i["commands"], "kind": i["kind"], "tags": i["tags"], "branch": b["branch"],
                       "caller": "%s:%d" % (i["caller"]["file"], i["caller"]["line"]),
                       "launched_at_run_time": i["launched_at_run_time"]}
                (reading_dependent if b.get("rb1") == "reading" else no_source).append(rec)
        table.append({"id": i["id"], "commands": i["commands"], "kind": i["kind"], "tags": i["tags"],
                      "caller": "%s:%d" % (i["caller"]["file"], i["caller"]["line"]),
                      "caller_function": mods_enclosing(mods, i["caller"]["file"], i["caller"]["line"]),
                      "launch_site": "%s:%d" % (i["launch_site"]["file"], i["launch_site"]["line"]),
                      "launched_at_run_time": i["launched_at_run_time"], "readback": i["readback"], "threads_executed": i["threads_executed"],
                      "branches": brs, "note": i["note"], "static_check_results": i["static_check_results"]})
    ok_only = [r for r in no_source if r["branch"] in ("ok", "recorded", "any_outcome", "passthrough")]
    return {"method": ("static call graph over the runtime modules (implementation-v2/, implementation-v2-a1/, r3_entry_v2, r3_entry_a1, "
                       "r3_resolve, r3_common), parsed with ast; command entries from the dispatch dicts of v2_driver.main and "
                       "a1_driver.main; SE-3 (both entries) and HR-3 (a1 entry) runtime rebinding applied; every path from a command "
                       "to a v2_solver.run_child call enumerated; the instance table (dispositions, read by hand from the cited lines) "
                       "must cover every path and every instance must lie on a path; every cited line re-checked"),
            "definition_capped_child": "a process launched through v2_solver.run_child (the only frozen function that sets RLIMIT_AS in a child; see launch_scan)",
            "commands": per_cmd, "coverage": {"paths_not_covered_by_an_instance": uncovered_paths, "instances_without_a_matching_path": unmatched},
            "citation_checks": {"n": len(cit), "failures": [c for c in cit if not c["ok"]]}, "instances": table,
            "static_paths_never_launched": static_only,
            "children_with_no_source": no_source, "children_with_no_source_on_ok_branch": ok_only,
            "children_whose_source_depends_on_reading_RB1": reading_dependent}


def mods_enclosing(mods, rel, line):
    for m in mods.values():
        if m.rel == rel:
            return m.enclosing(line)
    return None


# ============================================================================ launch scan (every scanned tree)
def launch_scan():
    capped, setr, other = [], [], []
    for rel in scanned_py_files():
        try:
            m = Mod(rel)
        except SyntaxError as e:                        # noqa: PERF203
            other.append({"file": rel, "error": repr(e)})
            continue
        for q in list(m.defs) + ["<module>"]:
            for c in m.own_calls(q):
                f = c.func
                name = getattr(f, "id", None) or getattr(f, "attr", None)
                base = f.value.id if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else None
                if name == "run_child":
                    capped.append({"file": rel, "line": c.lineno, "enclosing": q})
                elif name == "setrlimit":
                    setr.append({"file": rel, "line": c.lineno, "enclosing": q, "text": text_lines(rel)[c.lineno - 1].strip()})
                elif (base, name) in EXT_LAUNCH or (base is None and name in ("Popen", "execv", "execve", "system")):
                    other.append({"file": rel, "line": c.lineno, "enclosing": q, "call": "%s.%s" % (base, name) if base else name})
    return {"run_child_call_sites": capped, "setrlimit_call_sites": setr, "other_launch_call_sites": other}


# ============================================================================ RBR-2
def rbr2(mods):
    entries = command_entries(mods)
    wrapped = []
    for cmd, (entry, ctx) in sorted(entries.items()):
        seen = set()
        stack = [entry]
        reach = set()
        while stack:
            n = stack.pop()
            if n in reach or n[0] not in mods or n[1] not in mods[n[0]].defs:
                continue
            reach.add(n)
            for ln, t, c in edges(mods, n, ctx):
                if t[0] == "ext":
                    continue
                if n[0] != "r3_resolve" and t[:2] in (("r3_resolve", "solve"), ("r3_resolve", "run_system")):
                    gb = any(kw.arg == "gb_only" and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in c.keywords)
                    key = (cmd, mods[n[0]].rel, ln)
                    if key not in seen:
                        seen.add(key)
                        wrapped.append({"command": cmd, "file": mods[n[0]].rel, "line": ln, "enclosing": n[1],
                                        "site": "S-1 v2_driver.solve (SE-3)" if t[1] == "solve" else "S-2 a1_health.run_system (HR-3)",
                                        "gb_only_literal_true": gb})
                if t not in reach:
                    stack.append(t)
    TODAY = {  # (file, line) -> today's SC-4 enumeration source (r3_check_run.py 89-99, 111-125, 134-145)
        (FILES["v2d"], 358): ("raw-result.json solve record (row carries 'solver' with argv and 'outcome')", True, [("v2d", 359, '"solver"')]),
        (FILES["v2d"], 565): ("raw-result.json solve record", True, [("v2d", 566, '"solver"')]),
        (FILES["v2d"], 1174): ("raw-result.json solve record", True, [("v2d", 1179, '"solver"')]),
        (FILES["v2d"], 786): ("NONE: the controls check detail carries no 'solver' record", False, [("v2d", 793, '"D_identity"')]),
        (FILES["v2d"], 787): ("NONE", False, [("v2d", 794, '"same_solution_set"')]),
        (FILES["v2d"], 841): ("NONE", False, [("v2d", 846, '"outcome": s["outcome"]')]),
        (FILES["a1d"], 166): ("NONE: check (e) detail carries 'solver_getrlimit' and 'threads_executed' but no 'solver' record", False,
                              [("a1d", 174, '"solver_getrlimit"')]),
        (FILES["a1h"], 234): ("health/health-<p>.json systems[].first", True, [("r3c", 122, '"first", "reinvocation", "retry_seed2", "retry_seed2_reinvocation"')]),
        (FILES["a1h"], 237): ("health/health-<p>.json systems[].reinvocation", True, [("r3c", 122, '"reinvocation"')]),
        (FILES["a1h"], 241): ("health/health-<p>.json systems[].retry_seed2", True, [("r3c", 122, '"retry_seed2"')]),
        (FILES["a1h"], 244): ("health/health-<p>.json systems[].retry_seed2_reinvocation", True, [("r3c", 122, '"retry_seed2_reinvocation"')]),
        (FILES["v2d"], 693): ("not a wrapped call (gb_only pass-through); its raw solve records carry '-g' in argv and are skipped by SC-4 (r3_check_run.py 136)",
                              None, [("r3c", 136, 'if "-g" in argv or o.get("outcome") != "ok"')]),
        (FILES["v2d"], 711): ("not a wrapped call (gb_only pass-through); not in raw-result.json", None, [("v2d", 714, '"outcome"')]),
    }
    rows, cit = [], []
    for w in wrapped:
        t = TODAY.get((w["file"], w["line"]))
        if t is None:
            rows.append(dict(w, today="UNCLASSIFIED (census table gap)", today_enumerated=None))
            continue
        for f, ln, s in t[2]:
            cit.append({"file": FILES[f], "line": ln, "expect": s, "ok": citation_check({"file": FILES[f], "line": ln, "expect": s})})
        is_wrapped = not w["gb_only_literal_true"]
        rows.append(dict(w, is_wrapped_call=is_wrapped, today=t[0], today_enumerated=t[1],
                         under_RB1_RB3_as_worded=("enumerated: RB-1 writes every attempt of the call to a solver-events.json attempt record "
                                                  "(tag, retained flag, outcome class); RB-3 enumerates from those records")
                         if is_wrapped else "not a wrapped call; excluded from SC-4 ('-g' argv)"))
    gaps_today = [r for r in rows if r.get("is_wrapped_call") and r.get("today_enumerated") is False]
    unclassified = [r for r in rows if r.get("today") == "UNCLASSIFIED (census table gap)"]
    return {"method": "wrapped call sites found on the same static call graph as RBR-1 (edges into r3_resolve.solve / r3_resolve.run_system from outside r3_resolve); today's source read by hand at the cited lines against r3_check_run.sc4_accounting",
            "call_sites": rows, "wrapped_call_sites_not_enumerated_today": gaps_today, "unclassified": unclassified,
            "citation_checks": {"n": len(cit), "failures": [c for c in cit if not c["ok"]]},
            "wrapped_call_sites_not_enumerable_under_RB1_RB3_as_worded": []}


# ============================================================================ RBR-3
RBR3_TABLE = {
    "R-1": ("amendment files' bytes vs R.BOUND_HASHES (nine hashes)", False, None),
    "R-2": ("the eight plans' run-id lists and R.RETIRED_ALL (ids only)", False, None),
    "R-3": ("existence of runs/<RUN-ID> (this package's own directory)", False, None),
    "R-4": ("implementation-v2/ tree: git ls-files, git status, sha256 vs the TASK-20260923-0fa03f receipt", False, None),
    "R-5": ("implementation-v2-a1/ tree vs the TASK-20260923-4ff597 receipt", False, None),
    "R-6": ("implementation-v2-r3/ tree and both r3 plans vs the TASK-20260924-f1fb0e phase-A receipt", False, None),
    "R-7": ("(i) r7_gate_packages: raw-result.json run_status and gate_pass of each of G1..G4; (ii) r7_reg1_verdict on reg1(): REG-1 "
            "comparison of G1's solver/*.ms, solver/*.ms.out (+ .ms.log, .ms.err, .ms), certificates/*.json, raw-result.json and "
            "solver-events.json against RUN-GFPN-ac4487; (iii) r7_controls_a1_image: raw-result.json run_status and gate_pass of "
            "RUN-GFPN-2c4862", True,
            "YES: (i) and (iii) read run_status / gate_pass, which a completion-gate checker verdict can contradict (RUN-GFPN-bfe956: "
            "completed_valid, gate_pass true, r3 checker exit 1); (ii) REG-1 of G1 is a separate comparison from G1's checker verdict. "
            "All three are the predicates RB-4 replaces (gate packages; the controls_a1 image; REG-1 kept unchanged)"),
    "R-8": ("existence of runs/<req>/manifest.yaml for every package in `requires` (existence only; no field read)", True,
            "NO field is read, so no checker verdict can contradict what R-8 reads (every checker opens manifest.yaml; none disputes its "
            "existence). R-8 admits on the existence of another package's record regardless of that package's status"),
    "R-9": ("the plan's watchdogs object vs trial-plan-v2.json's", False, None),
    "R-10": ("the host process table (v2_solver.other_solver_processes)", False, None),
    "R-11": ("existence of run directories under the ids of the eight plans (a count)", False, None),
    "R-12": ("the replaced package's manifest.yaml failure_class (must be infrastructure_error), its plan entry (not blocking), and "
             "every other contingency package's manifest.yaml package.replaces", True,
             "reads another package's recorded failure_class. No completion-gate checker item reads failure_class (token counts below), so no "
             "checker item tests the value R-12 reads; the checker's exit status on the replaced package is a verdict about that package, "
             "not about its failure_class. R-12 admits a replacement run of the replaced package, not a package that relies on its result"),
    "R-13": ("the plan's protocol_version, repair amendments, task_id and forbidden ids; r3 constants", False, None),
}


def token_count(rel, word):
    n = 0
    for tok in tokenize.tokenize(io.BytesIO(read_bytes(rel, False)).readline):
        if tok.type in (tokenize.NAME, tokenize.STRING) and word in tok.string:
            n += 1
    return n


def rbr3():
    m = Mod(FILES["r3w"])
    lines = {}
    for q in list(m.defs) + ["<module>"]:
        for c in m.own_calls(q):
            if isinstance(c.func, ast.Attribute) and c.func.attr == "append" and isinstance(c.func.value, ast.Name) and c.func.value.id == "ref" and c.args:
                a = c.args[0]
                s = a.left.value if isinstance(a, ast.BinOp) and isinstance(a.left, ast.Constant) else (a.value if isinstance(a, ast.Constant) else None)
                if isinstance(s, str) and s.startswith("R-"):
                    rid = s.split()[0]
                    lines.setdefault(rid, []).append({"line": c.lineno, "function": q})
    # the call sites of the predicate functions inside preflight
    pre = m.defs["preflight"]
    pre_calls = [{"line": c.lineno, "callee": getattr(c.func, "id", None) or getattr(c.func, "attr", None)}
                 for c in m.own_calls("preflight") if (getattr(c.func, "id", "") or "").startswith(("r7_", "r8_", "r12_", "reg1", "tree_check"))]
    # R-4 / R-5 / R-6: tree_check formats its tag at run time ("%s ..." % (tag, ...)), called with "R-4", "R-5", "R-6"
    tc_lines = [c.lineno for c in m.own_calls("tree_check") if isinstance(c.func, ast.Attribute) and c.func.attr == "append"]
    tc_calls = {}
    for c in m.own_calls("preflight"):
        if getattr(c.func, "id", None) == "tree_check" and c.args and isinstance(c.args[0], ast.Constant):
            tc_calls[c.args[0].value] = c.lineno
    for rid in ("R-4", "R-5", "R-6"):
        lines[rid] = [{"line": ln, "function": "tree_check"} for ln in tc_lines] + [{"line": tc_calls.get(rid), "function": "preflight"}]
    rows = []
    for rid in ["R-%d" % i for i in range(1, 14)]:
        reads, another, contra = RBR3_TABLE[rid]
        locs = lines.get(rid, [])
        fns = sorted({x["function"] for x in locs})
        rows.append({"id": rid, "refusal_lines": [x["line"] for x in locs], "functions": fns,
                     "function_def_lines": {f: [m.defs[f].lineno, m.defs[f].end_lineno] for f in fns if f in m.defs},
                     "reads": reads, "admits_on_another_packages_record": another, "checker_can_contradict": contra})
    counts = {rel: {w: token_count(rel, w) for w in ("failure_class", "run_status", "gate_pass")} for rel in (FILES["v2k"], FILES["a1k"], FILES["r3c"])}
    cit = [(FILES["r3w"], 180, 'r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True'),
           (FILES["r3w"], 195, 'r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True'),
           (FILES["r3w"], 186, 'if rg["verdict"] != "PASS"'),
           (FILES["r3w"], 202, 'os.path.exists(os.path.join(RUNS, req, "manifest.yaml"))'),
           (FILES["r3w"], 221, 'man.get("failure_class") != "infrastructure_error"'),
           (FILES["r3w"], 227, '(m2.get("package") or {}).get("replaces") == replaces'),
           (FILES["r3w"], 282, 'need_gate = (which == "v2r3" and pk.get("gate_required")) or which == "a1r3"'),
           (FILES["r3w"], 285, "if rid != gate_ids[0]:"),
           (FILES["r3w"], 288, 'if which == "a1r3" and pk.get("controls_a1_gate_required"):'),
           (FILES["a1k"], 83, 'if r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:'),
           (FILES["v2k"], 53, 'if man["status"] != raw.get("run_status")')]
    cres = [{"file": f, "line": ln, "expect": s, "ok": citation_check({"file": f, "line": ln, "expect": s})} for f, ln, s in cit]
    return {"method": "ast: every ref.append('R-n ...') in r3_run_wrapper.py mapped to its function; what each reads read by hand at the cited lines",
            "predicates": rows, "preflight_predicate_calls": pre_calls, "preflight_def_lines": [pre.lineno, pre.end_lineno],
            "checker_token_counts": counts, "citation_checks": {"n": len(cres), "failures": [c for c in cres if not c["ok"]]},
            "gate_role_note": ("G2..G4 have gate_required false (trial-plan-v2-r3.json), so R-7 (i) does not apply to them; each is admitted "
                               "on R-8 (the previous gate package's manifest exists) and, from G2 on, REG-1 (r3_run_wrapper.py 282-287)"),
            "checker_item_reading_another_package": ("a1_check_run.py 79-84 (an item of the frozen a1 CHECKER, not an admission predicate) reads "
                                                     "the controls_a1 image's raw-result run_status and gate_pass for every package with "
                                                     "controls_a1_gate_required"),
            "driver_level_cross_package_reads_outside_RBR3": [
                "v2_driver._load_build (989-1003): cells read the build package's raw-result polynomials[].outcome and the cached npz sha256",
                "v2_driver._prior_cells / _condition_met (1006-1013, 1110-1127): m = 4 cells read the prior m = 5 package's cell terminal status and metrics",
                "v2_driver.cmd_aggregate (1248-1326) and a1_driver.cmd_aggregate_a1 (276-393): read cells packages' raw-result.json",
                "v2_common.resolve_replacement and a1_driver._resolve (243-254): read contingency packages' manifest package.replaces",
                "v2_driver.cmd_anchor_identity (642): reads the archived RUN-GFPN-61bba9 raw-result parameters"]}


# ============================================================================ RBR-4 (a): the four gate packages, phase-B bytes
def rbr4a():
    rc = load_json_rel("coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-f1fb0e/post-run-receipt.json", record=False)["path_sha256"]
    out = {}

    def pread(rel):
        b = read_bytes(rel)
        want = rc.get(rel)
        if want is None or want != sha_bytes(b):
            raise SystemExit("RBR-4 (a): %s is not bound by, or differs from, the phase-B receipt" % rel)
        return b

    for rid in GATE:
        pd_rel = os.path.join(EXP_REL, "runs", rid)
        on_disk = sorted(os.path.relpath(os.path.join(dp, f), REPO) for dp, _d, fs in os.walk(os.path.join(REPO, pd_rel)) for f in fs)
        bound = sorted(p for p in rc if p.startswith(pd_rel + "/"))
        rel_names = [p[len(pd_rel) + 1:] for p in on_disk]
        raw = json.loads(pread(pd_rel + "/raw-result.json"))
        man = yaml.safe_load(pread(pd_rel + "/manifest.yaml"))["run"]
        sev = json.loads(pread(pd_rel + "/solver-events.json"))
        specs = [n for n in rel_names if n.startswith("child/") and n.endswith(".spec.json")]
        metas = [n for n in rel_names if n.startswith("child/") and n.endswith(".meta.json")]
        spec_jobs = {}
        for s in specs:
            spec_jobs[s[len("child/"):-len(".spec.json")]] = json.loads(pread(pd_rel + "/" + s)).get("job")
        meta_pairs = {}
        for s in metas:
            mj = json.loads(pread(pd_rel + "/" + s))
            meta_pairs[s[len("child/"):-len(".meta.json")]] = mj.get("rlimit_as_child_getrlimit")
        ms_logs = [n for n in rel_names if n.startswith("solver/") and (n.endswith(".ms.log") or ".ms.log.ssf-attempt" in n)]
        cg = [n for n in rel_names if n.startswith("solver/") and n.endswith(".callgrind.stdout")]
        sage = [n for n in rel_names if n == "comparator/stdout.log"]
        gp = [n for n in rel_names if n.startswith("pari/") and n.endswith(".gp.stdout")]
        hl = [n for n in rel_names if n.startswith("health/") and n.endswith(".ms.log")]
        evidenced = {"builder_build_poly": sorted(t for t, j in spec_jobs.items() if j == "build_poly"),
                     "builder_raw_grid": sorted(t for t, j in spec_jobs.items() if j == "raw_grid"),
                     "S-1 msolve": sorted(os.path.basename(n).split(".ms.log")[0] for n in ms_logs),
                     "S-3 callgrind": sorted(os.path.basename(n)[:-len(".callgrind.stdout")] for n in cg),
                     "Sage comparator": ["comparator"] if sage else [], "gp": sorted(gp), "S-2 health msolve": sorted(hl)}
        # raw-result.json: every run_child record (a dict with 'outcome' and a non-null 'rlimit_as_child_getrlimit')
        recs = []

        def walk(o, path):
            if isinstance(o, dict):
                if o.get("rlimit_as_child_getrlimit") is not None and "outcome" in o:
                    recs.append((path, o))
                for k, v in o.items():
                    walk(v, path + "/" + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, path + "[%d]" % i)
        walk(raw, "")
        key_occ = []

        def walk2(o, path):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "rlimit_as_child_getrlimit":
                        key_occ.append(path + "/" + k)
                    walk2(v, path + "/" + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk2(v, path + "[%d]" % i)
        walk2(raw, "")
        via_raw = {"S-1 msolve": set(), "builder": set(), "S-3 callgrind": 0, "Sage comparator": 0, "gp": 0, "S-2 health msolve": 0}
        for path, o in recs:
            argv = o.get("argv") or []
            if path.endswith("/solver"):
                if "-f" in argv:
                    via_raw["S-1 msolve"].add(os.path.basename(argv[argv.index("-f") + 1])[:-len(".ms")])
            elif path.endswith("/instructions_callgrind/child"):
                via_raw["S-3 callgrind"] += 1
            elif path.endswith("/comparator/child"):
                via_raw["Sage comparator"] += 1
            elif argv and argv[-1].endswith(".spec.json"):
                via_raw["builder"].add(os.path.basename(argv[-1])[:-len(".spec.json")])
            elif path.endswith("/pari/child"):
                via_raw["gp"] += 1
        via_raw_counts = {k: (len(v) if isinstance(v, set) else v) for k, v in via_raw.items()}
        n_evid = sum(len(v) for v in evidenced.values())
        n_raw = sum(via_raw_counts.values())
        # SC-4 enumeration exactly as r3_check_run.sc4_accounting selects rows (re-implemented; nothing imported)
        sc4 = []

        def fsr(o):
            if isinstance(o, dict):
                s = o.get("solver")
                if isinstance(s, dict) and s.get("argv"):
                    yield o
                for v in o.values():
                    yield from fsr(v)
            elif isinstance(o, list):
                for v in o:
                    yield from fsr(v)
        for o in fsr(raw):
            argv = o["solver"]["argv"]
            if "-g" in argv or o.get("outcome") != "ok":
                continue
            tag = os.path.basename(argv[argv.index("-f") + 1])[:-len(".ms")]
            sc4.append({"tag": tag, "retained_ms_out": ("solver/%s.ms.out" % tag) in rel_names})
        s1 = (sev.get("sites") or {}).get("v2_driver.solve") or {}
        s2 = (sev.get("sites") or {}).get("a1_health.run_system") or {}
        s3 = (sev.get("sites") or {}).get("v2_driver.solve/callgrind") or {}
        s1_ok_retained = [t for t in evidenced["S-1 msolve"] if ("solver/%s.ms.out" % t) in rel_names]
        no_source_today = sorted(set(evidenced["S-1 msolve"]) - via_raw["S-1 msolve"])
        builders = evidenced["builder_build_poly"] + evidenced["builder_raw_grid"]
        builder_no_raw = sorted(set(builders) - via_raw["builder"])
        builder_meta_pair = sorted(t for t in builders if isinstance(meta_pairs.get(t), dict))
        out[rid] = {
            "files_on_disk_equal_receipt_bound_set": on_disk == bound, "n_files": len(on_disk),
            "command": (man.get("code") or {}).get("command", "").split("r3_entry_v2.py")[-1].strip(),
            "run_status": raw.get("run_status"), "gate_pass": raw.get("gate_pass"),
            "capped_children_evidenced_by_kind": {k: len(v) for k, v in evidenced.items()}, "capped_children_evidenced_total": n_evid,
            "evidence_rule": ("builder: child/<tag>.spec.json by spec job; S-1: solver/<tag>.ms.log (+ .ssf-attempt<k>); S-3: "
                              "solver/<tag>.callgrind.stdout; Sage: comparator/stdout.log; gp: pari/*.gp.stdout; S-2: health/*.ms.log"),
            "readback_reaches_manifest_through_raw_result_by_kind": via_raw_counts, "readback_reaches_manifest_through_raw_result_total": n_raw,
            "raw_result_key_occurrences_rlimit_as_child_getrlimit": len(key_occ),
            "raw_result_key_occurrences_threads_executed": json.dumps(raw).count('"threads_executed"'),
            "manifest_child_rlimit_as_read_back_by_getrlimit": man["resources"].get("child_rlimit_as_read_back_by_getrlimit"),
            "manifest_msolve_threads_executed": man["resources"].get("msolve_threads_executed"),
            "manifest_child_rlimit_as_requested_bytes": man["resources"].get("child_rlimit_as_requested_bytes"),
            "child_meta_json_with_pair": len(builder_meta_pair), "child_meta_pairs_equal_cap": all(
                meta_pairs[t] == {"soft": CAP, "hard": CAP} for t in builder_meta_pair),
            "builders_without_raw_readback": builder_no_raw,
            "builders_without_raw_or_meta_readback": sorted(set(builder_no_raw) - set(builder_meta_pair)),
            "S1_children_without_raw_readback": no_source_today,
            "sc4_rows_as_r3_selects_them": len(sc4), "sc4_rows_with_retained_output": sum(1 for r in sc4 if r["retained_ms_out"]),
            "S1_ok_or_other_attempts_with_retained_ms_out_on_disk": len(s1_ok_retained),
            "wrapped_attempts": {"S-1 wrapped_calls": (s1.get("counters") or {}).get("wrapped_calls"),
                                 "S-1 attempts_total": (s1.get("counters") or {}).get("attempts_total"),
                                 "S-1 passthrough_calls_gb_only_true": (s1.get("counters") or {}).get("passthrough_calls_gb_only_true"),
                                 "S-1 re_solves": (s1.get("counters") or {}).get("re_solves"),
                                 "S-2 wrapped_calls": (s2.get("counters") or {}).get("wrapped_calls"),
                                 "S-2 attempts_total": (s2.get("counters") or {}).get("attempts_total"),
                                 "S-3 callgrind_children_observed": (s3.get("counters") or {}).get("callgrind_children_observed"),
                                 "S-1 events": len(s1.get("events") or []), "S-2 events": len(s2.get("events") or [])},
        }
    # the specific CORR-20260924-ec044e statements for RUN-GFPN-bfe956, re-read
    g4 = os.path.join(EXP_REL, "runs", "RUN-GFPN-bfe956")
    ml = pread(g4 + "/manifest.yaml").decode().splitlines()
    rl = pread(g4 + "/raw-result.json").decode().splitlines()
    cl = pread(g4 + "/child/ctl_S3.meta.json").decode().splitlines()
    el = pread(g4 + "/solver/ctl_planted_S3.ms.err").decode().splitlines()
    sl = pread(g4 + "/solver-events.json").decode().splitlines()
    solver_files = sorted(p for p in rc if p.startswith(g4 + "/solver/"))
    corr = {"manifest_lines_176_183": ml[175:183], "raw_result_line_516": rl[515] if len(rl) >= 516 else None,
            "raw_result_threads_key_count": sum(1 for x in rl if '"threads"' in x),
            "raw_result_rlimit_key_count": sum(1 for x in rl if "rlimit_as_child_getrlimit" in x),
            "ctl_S3_meta_lines_83_86": cl[82:86], "ctl_planted_S3_ms_err_line_15": el[14] if len(el) >= 15 else None,
            "solver_events_lines_11_31_contain_wrapped_calls_8": any('"wrapped_calls": 8' in x for x in sl[10:31]),
            "solver_file_count": len(solver_files), "solver_tags": len({os.path.basename(p).split(".")[0] for p in solver_files})}
    out["_CORR-20260924-ec044e_statements_rechecked"] = corr
    return out


# ============================================================================ RBR-4 (b): REG-1 field scope
def rbr4b():
    ex = json.loads(read_bytes(FILES["r3x"]))
    m = Mod(FILES["r3g"])
    strs = sorted({n.value for n in ast.walk(m.tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                   and any(w in n.value for w in ("manifest", "solver-events", "health", "sc4", "SC-4"))})
    reads = []
    for q in list(m.defs):
        for c in m.own_calls(q):
            if isinstance(c.func, ast.Attribute) and c.func.attr == "read" and c.args:
                reads.append({"function": q, "line": c.lineno, "arg": ast.unparse(c.args[0])})
            if isinstance(c.func, ast.Name) and c.func.id == "open" and c.args:
                reads.append({"function": q, "line": c.lineno, "arg": "open(" + ast.unparse(c.args[0]) + ")"})
    cit = [(FILES["r3g"], 193, 'not (e.get("consistency") or {}).get("ok", True)'),
           (FILES["r3g"], 194, 'viol = bool(doc.get("consistency_violation")) or bool(ev_bad)'),
           (FILES["r3g"], 198, 'rep["counters"] = {R.SITE_S1: s1.get("counters"), R.SITE_S2: s2.get("counters")}'),
           (FILES["r3g"], 282, 'rep["solver_events_json_verbatim"] = se_txt'),
           (FILES["r3g"], 175, 'p = os.path.join(candidate, "solver-events.json")'),
           (FILES["r3g"], 47, 'TARGET_LISTS = ["targets", "planted_targets", "replaced_fresh_targets"]')]
    cres = [{"file": f, "line": ln, "expect": s, "ok": citation_check({"file": f, "line": ln, "expect": s})} for f, ln, s in cit]
    exs = [{"id": e["id"], "scope": e["scope"], "path": e["path"]} for e in ex["entries"]]
    touches = [e["id"] for e in ex["entries"] if any(w in json.dumps(e["path"]) for w in ("solver-events", "resources", "manifest", "attempt", "sc4"))]
    return {"reg1_reads": reads, "reg1_string_constants_naming_manifest_solver_events_health_sc4": strs,
            "exclusions": exs, "exclusions_touching_solver_events_manifest_or_sc4": touches,
            "citation_checks": {"n": len(cres), "failures": [c for c in cres if not c["ok"]]},
            "per_change": {
                "RB-1 (solver-events.json attempt records; a recording failure is an SE-2 (4) consistency violation)": {
                    "reg1_reads_it": True,
                    "what": ("REG-1's SE-4 (e) test reads the CANDIDATE's solver-events.json: it must exist and parse; the top-level "
                             "consistency_violation flag and the S-1 / S-2 events' consistency.ok decide a FAIL (r3_reg1.py 175-197); the "
                             "counters are copied and the whole file is quoted verbatim (198, 282). RB-1 adds attempt records to that file "
                             "and adds a new cause (a recording failure) for the consistency flag. The reference RUN-GFPN-ac4487's "
                             "solver-events.json is not read.")},
                "RB-2 (manifest resources)": {"reg1_reads_it": False, "what": "REG-1 reads no manifest.yaml (reads listed above)"},
                "RB-3 (SC-4 output)": {"reg1_reads_it": False,
                                       "what": ("REG-1 reads no SC-4 output; r3_reg1 imports r3_accounting only for the frozen parse "
                                                "functions (ACC._v2) and ACC.EXTRA_VAR_LINE (r3_reg1.py 140, 162)")},
                "X1..X17": {"reads_a_changed_field": bool(touches),
                            "what": ("scopes certificate (run_id), raw-result (metrics.wall_seconds) and target-entry (arms.*.solver.*, "
                                     "timings, last_f4_round, instructions_callgrind.*); none names solver-events.json, the manifest or SC-4. "
                                     "RB-1 copies (reads) arms.*.solver.rlimit_as_child_getrlimit and threads_executed from the returned "
                                     "result; it changes no raw-result.json field, and REG-1 (b) compares those two fields unexcluded")}}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    OUT["phase_1_integrity"] = integrity()
    if not OUT["phase_1_integrity"]["all_ok"]:
        OUT["stopped"] = "RBQ-2 integrity failure: no reading was made"
        write_out(a.out)
        print("STOP: integrity failure")
        return 3
    install_guard()
    OUT["guard"] = GUARD
    mods = load_runtime()
    OUT["runtime_modules"] = {n: m.rel for n, m in sorted(mods.items())}
    OUT["runtime_imports_outside_runtime_set"] = sorted({"%s imports %s" % (n, v) for n, m in mods.items() for v in list(m.aliases.values()) +
                                                         [x[0] for x in m.from_imports.values()]
                                                         if v.split(".")[0] in SCANNED_MODULE_NAMES and v.split(".")[0] not in mods})
    OUT["launch_scan"] = launch_scan()
    OUT["RBR-1"] = rbr1(mods)
    OUT["RBR-2"] = rbr2(mods)
    OUT["RBR-3"] = rbr3()
    OUT["RBR-4"] = {"a": rbr4a(), "b": rbr4b()}
    OUT["guard"] = GUARD
    OUT["wall_seconds"] = round(time.time() - t0, 3)
    write_out(a.out)
    print("done: guard launch attempts %d, import attempts %d" % (GUARD["launch_attempts"], GUARD["import_attempts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
