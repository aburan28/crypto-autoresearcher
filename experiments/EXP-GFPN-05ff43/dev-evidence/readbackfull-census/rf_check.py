#!/usr/bin/env python3
"""rf_check.py -- the zero-run, zero-solve SUCCESSOR CENSUS check script of TASK-20260924-cab04e.

EXP-GFPN-05ff43; DRAFT AMD-EXP-GFPN-05ff43-20260924-readbackfull (not approved), pre_approval_readings RLR-5, RLR-1,
RLR-2, RLR-3, RLR-4, RLR-7, RLR-6, computed as the draft and the card (RFQ-1..RFQ-9) word them; ordered by
DEC-20260924-650068. OBSERVATIONS ONLY: nothing here is evidence about D, the quotient, H-GFPN-9a29be or
HEUR-GFPN-DFLAT, and nothing here is an approval recommendation.

usage:  PYTHONDONTWRITEBYTECODE=1 python3 -B rf_check.py --out <readbackfull-census.json>

Phase 1 (RLR-5 / RFQ-2), INTEGRITY FIRST: (a)-(g). Only read-only git children are launched, each recorded with argv.
  Any failure writes the JSON with the failure and exits 3 before any reading.
Phase 2 (RFQ-1): an in-process guard (sys.addaudithook) REFUSES every child-process launch and every import of a module
  whose name is the name of a .py file of a scanned tree; attempt counts are reported; self-tested with sys.audit().
Phase 3: the readings. Every source file is read as bytes and parsed with ast / tokenize, never imported. Every line
  a table cites is re-checked against the file text. The predecessor's method (rb_check.py, TASK-20260924-bf5724) is
  reused: the static call graph, the capped-child instance table I-01..I-26 and its citations are carried; the branch
  model is extended by the run_child-level branches the draft's definitions add (refused_before_fork, raised) and by
  the sources RL-1, RL-2, RL-3 (d), (e).
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
ARCH_REL = "coordination/goals/GOAL-GFPN-380702/archives"
BASE_COMMIT = "dd103455380238ec2f20d17414de687acdcc822a"
DRAFT_REL = EXP_REL + "/amendments/v2_addendum_readbackfull.yaml"
COVER_REL = EXP_REL + "/amendments/v2_addendum_readbackcover.yaml"
COVER_SHA = "dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e"
CAP = 10737418240
TASK_ID = "TASK-20260924-cab04e"
LADDER_PRIMES_ORDER = None      # read from ladder.json

OUT = {"schema": "crypto.autoresearch.gfpn05.readbackfull_census.v1", "task_id": TASK_ID, "experiment_id": "EXP-GFPN-05ff43",
       "draft": "AMD-EXP-GFPN-05ff43-20260924-readbackfull (DRAFT, not approved)", "ordered_by": "DEC-20260924-650068",
       "archived_by": "TASK-20260924-ddfb69",
       "statement": ("observations only; nothing here is evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT; "
                     "no approval recommendation; no D or degree is reported as a result"),
       "started_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "python": sys.version.split()[0], "files_read_sha256": {}}
GIT_CHILDREN = []
CITES = []          # every citation checked: (reading, file, line, expect)


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


FORBIDDEN_IN_OUTPUT = ["TASK-20260923-" + x for x in ("cd932c", "6c7f55", "3aa31e", "292052")] + \
                      ["TASK-20260924-" + x for x in ("946010", "9490b1", "4351ac", "b3e690")]
NAME_WORDS = ("claude", "anthropic", "opus", "sonnet", "haiku", "gpt-", "openai", "codex", "opencode", "gemini", "glm")


def write_out(path):
    OUT["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT["git_children_integrity_phase_only"] = GIT_CHILDREN
    txt = json.dumps(OUT, indent=1, sort_keys=False, default=str)
    low = txt.lower()
    OUT["output_self_check"] = {"forbidden_task_ids_present": [t for t in FORBIDDEN_IN_OUTPUT if t in txt],
                                "model_runtime_vendor_words_present": [w for w in NAME_WORDS if w in low],
                                "bedrock_mentions": low.count("bedrock"),
                                "note": "'bedrock' occurs only as the key bedrock_used and the sentence 'Amazon Bedrock is prohibited.'"}
    with open(path, "w") as fh:
        json.dump(OUT, fh, indent=1, sort_keys=False, default=str)
        fh.write("\n")


# ============================================================================ phase 1: integrity (RLR-5 / RFQ-2)
def integrity():
    res = {}
    # (a) the draft against TASK-20260924-833cde's receipt addendum_sha256; status draft; approved_by null
    lr_rel = ARCH_REL + "/TASK-20260924-833cde/ledger-receipt.json"
    lr = load_json_rel(lr_rel)["addendum_sha256"]
    got = sha_bytes(read_bytes(DRAFT_REL))
    d = yaml.safe_load(read_bytes(DRAFT_REL, False))["amendment"]
    res["a_readbackfull_draft"] = {"path": DRAFT_REL, "receipt": lr_rel, "receipt_key": "addendum_sha256.sha256",
                                   "receipt_value": lr.get("sha256"), "receipt_path_field": lr.get("path"),
                                   "receipt_status_field": lr.get("status"), "computed": got,
                                   "in_file_status": d.get("status"), "in_file_approved_by": d.get("approved_by"),
                                   "in_file_approval_decision": d.get("approval_decision"),
                                   "ok": (got == lr.get("sha256") and lr.get("path") == DRAFT_REL and d.get("status") == "draft"
                                          and d.get("approved_by") is None)}
    # (b) readbackcover
    gc = sha_bytes(read_bytes(COVER_REL))
    res["b_readbackcover"] = {"path": COVER_REL, "expected": COVER_SHA, "computed": gc, "ok": gc == COVER_SHA}
    # (c) the nine VA-1 files against DEC-20260924-e52eec bound_hashes (yaml data only)
    dec = yaml.safe_load(read_bytes("ledger/decisions/DEC-20260924-e52eec.yaml"))
    dd = dec.get("coordinator_decision", dec)
    bh = {k: v for k, v in (dd.get("bound_hashes") or {}).items() if k != "note"}
    rows = {}
    for k, v in bh.items():
        c = sha_bytes(read_bytes(k))
        rows[k] = {"bound": v, "computed": c, "ok": c == v}
    res["c_nine_va1_files"] = {"source": "ledger/decisions/DEC-20260924-e52eec.yaml coordinator_decision.bound_hashes", "n": len(bh),
                               "rows": rows, "ok": len(bh) == 9 and all(r["ok"] for r in rows.values())}
    # (d) the archived census files against the TASK-20260924-a01341 receipt
    rc_rel = ARCH_REL + "/TASK-20260924-a01341/snapshot-receipt.json"
    pc = load_json_rel(rc_rel)["path_sha256"]
    rows = {}
    for k, v in pc.items():
        c = sha_bytes(read_bytes(k))
        rows[k] = {"bound": v, "computed": c, "ok": c == v}
    res["d_archived_census"] = {"receipt": rc_rel, "n": len(pc), "rows": rows, "ok": len(pc) == 3 and all(r["ok"] for r in rows.values())}
    # (e) 22 phase-A and 801 phase-B paths of TASK-20260924-f1fb0e
    for name, n_exp in (("snapshot-receipt.json", 22), ("post-run-receipt.json", 801)):
        rel = ARCH_REL + "/TASK-20260924-f1fb0e/" + name
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
        res["e_TASK-20260924-f1fb0e_" + name] = {"receipt": rel, "n_paths": len(rc), "n_expected": n_exp, "mismatches": bad,
                                                  "ok": len(rc) == n_exp and not bad}
    # (f) implementation-v2/ and implementation-v2-a1/ against their phase-A receipts (every bound path: a superset of
    #     every file this census reads from those trees), and no unbound .py file in either tree
    for tid, tree in (("TASK-20260923-0fa03f", "implementation-v2"), ("TASK-20260923-4ff597", "implementation-v2-a1")):
        rel = ARCH_REL + "/%s/snapshot-receipt.json" % tid
        rcj = load_json_rel(rel)
        rc = rcj["path_sha256"]
        bad = [p for p, h in rc.items() if not os.path.exists(os.path.join(REPO, p)) or sha_bytes(read_bytes(p, False)) != h]
        on_disk = sorted(os.path.join(EXP_REL, tree, f) for f in os.listdir(os.path.join(EXP, tree)) if f.endswith(".py"))
        unbound = [p for p in on_disk if p not in rc]
        res["f_" + tid] = {"receipt": rel, "receipt_phase": rcj.get("phase"), "n_paths": len(rc), "mismatches": bad,
                           "tree_py_files_not_bound": unbound, "ok": not bad and not unbound}
    # (g) no change since the phase-B archive commit
    pathspecs = [EXP_REL + "/implementation*", EXP_REL + "/trial-plan-*.json"]
    p = git(["diff", "--stat", BASE_COMMIT, "--"] + pathspecs)
    argv_g = GIT_CHILDREN[-1]["argv"]
    ls = git(["ls-files", "--"] + pathspecs)
    res["g_git_diff_stat"] = {"argv": argv_g, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                              "pathspec_sanity_ls_files_count": len(ls.stdout.splitlines()),
                              "ok": p.returncode == 0 and p.stdout == "" and len(ls.stdout.splitlines()) > 0}
    head = git(["rev-parse", "HEAD"]).stdout.strip()
    st = git(["status", "--porcelain", "--untracked-files=all"]).stdout.splitlines()
    res["repository_state"] = {"head": head, "status_porcelain": st}
    res["all_ok"] = all(v["ok"] for k, v in res.items() if isinstance(v, dict) and "ok" in v)
    return res


def dp5_recheck():
    """DP-5 at script time (listing only; no git child): run directories, r4 paths."""
    rd = os.path.join(EXP, "runs")
    runs = sorted(f for f in os.listdir(rd) if os.path.isdir(os.path.join(rd, f)))
    non_dirs = sorted(f for f in os.listdir(rd) if not os.path.isdir(os.path.join(rd, f)))
    r4 = sorted(f for f in os.listdir(EXP) if f.startswith("implementation-v2-r4") or f in ("trial-plan-v2-r4.json", "trial-plan-v2-a1-r4.json"))
    own = sorted(os.listdir(os.path.join(EXP, "dev-evidence", "readbackfull-census")))
    return {"run_directories": len(runs), "run_directory_ids": runs, "non_directory_entries_in_runs": non_dirs, "r4_paths_present": r4,
            "readbackfull_census_dir_contents_at_script_time": own,
            "note": ("the readbackfull-census/ directory did not exist before this task (checked in the shell before any write); "
                     "at script time it holds only this task's files")}


# ============================================================================ phase 2: the guard (RFQ-1)
GUARD = {"installed": False, "installed_utc": None, "launch_attempts": 0, "import_attempts": 0, "events": [],
         "self_test": {"mode": False, "launch_refused": None, "import_refused": None}}
LAUNCH_EVENTS = {"subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty", "pty.spawn",
                 "os.startfile"}
SCANNED_MODULE_NAMES = set()
SCANNED_TREES = ["implementation", "implementation-v2", "implementation-v2-a1", "implementation-v2-r1", "implementation-v2-r2",
                 "implementation-v2-r3"]
COMPARATOR_REL = "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
K5K7_REL = "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7"


def _hook(event, args):
    if not GUARD["installed"]:
        return
    if event in LAUNCH_EVENTS:
        if GUARD["self_test"]["mode"]:
            GUARD["self_test"]["launch_refused"] = event
        else:
            GUARD["launch_attempts"] += 1
            GUARD["events"].append({"event": event, "args": repr(args)[:200]})
        raise RuntimeError("rf_check guard (RFQ-1): child launch refused: %s" % event)
    if event == "import":
        name = str(args[0]).split(".")[0] if args else ""
        if name in SCANNED_MODULE_NAMES:
            if GUARD["self_test"]["mode"]:
                GUARD["self_test"]["import_refused"] = name
            else:
                GUARD["import_attempts"] += 1
                GUARD["events"].append({"event": "import", "module": name})
            raise ImportError("rf_check guard (RFQ-1): import of scanned-tree module %s refused" % name)


def scanned_py_files(include_tools=False):
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
    if include_tools:
        for top in ("tools", "harness"):
            for dp, _dn, fn in os.walk(os.path.join(REPO, top)):
                if "__pycache__" in dp:
                    continue
                for f in sorted(fn):
                    if f.endswith(".py"):
                        out.append(os.path.relpath(os.path.join(dp, f), REPO))
    return out


def install_guard():
    for rel in scanned_py_files(include_tools=True):
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
        sys.audit("import", "v2_solver", None, None, None, None)
    except ImportError:
        pass
    GUARD["self_test"]["mode"] = False
    GUARD["n_module_names_refused"] = len(SCANNED_MODULE_NAMES)
    GUARD["scanned_tree_module_names_refused"] = sorted(n for n in SCANNED_MODULE_NAMES
                                                        if n.startswith(("v2_", "a1_", "r1_", "r2_", "r3_", "k4a", "symmetrize")))
    GUARD["note"] = "the refused set also holds every .py module name under tools/ and harness/ (read for RLR-2 / RLR-6 as text only)"


# ============================================================================ phase 3: static index of the sources
FILES = {"v2d": EXP_REL + "/implementation-v2/v2_driver.py", "v2s": EXP_REL + "/implementation-v2/v2_solver.py",
         "v2c": EXP_REL + "/implementation-v2/v2_child.py", "v2k": EXP_REL + "/implementation-v2/v2_check_run.py",
         "v2cm": EXP_REL + "/implementation-v2/v2_common.py", "v2a": EXP_REL + "/implementation-v2/v2_arms.py",
         "a1d": EXP_REL + "/implementation-v2-a1/a1_driver.py", "a1h": EXP_REL + "/implementation-v2-a1/a1_health.py",
         "a1p": EXP_REL + "/implementation-v2-a1/a1_pari.py", "a1k": EXP_REL + "/implementation-v2-a1/a1_check_run.py",
         "a1c": EXP_REL + "/implementation-v2-a1/a1_common.py",
         "r3r": EXP_REL + "/implementation-v2-r3/r3_resolve.py", "r3w": EXP_REL + "/implementation-v2-r3/r3_run_wrapper.py",
         "r3c": EXP_REL + "/implementation-v2-r3/r3_check_run.py", "r3g": EXP_REL + "/implementation-v2-r3/r3_reg1.py",
         "r3x": EXP_REL + "/implementation-v2-r3/reg1-exclusion-list.json", "r3e2": EXP_REL + "/implementation-v2-r3/r3_entry_v2.py",
         "r3e1": EXP_REL + "/implementation-v2-r3/r3_entry_a1.py", "r3cm": EXP_REL + "/implementation-v2-r3/r3_common.py",
         "r3d7": EXP_REL + "/implementation-v2-r3/r3_dv7.py", "a1t": EXP_REL + "/implementation-v2-a1/a1_toy.py",
         "draft": DRAFT_REL, "cover": COVER_REL}
TEXT = {}


def text_lines(rel):
    if rel not in TEXT:
        TEXT[rel] = read_bytes(rel).decode("utf-8", errors="replace").splitlines()
    return TEXT[rel]


def cite(reading, fkey, line, expect):
    rel = FILES.get(fkey, fkey)
    CITES.append({"reading": reading, "file": rel, "line": line, "expect": expect})
    return "%s:%d" % (os.path.basename(rel), line)


def citation_check(c):
    lines = text_lines(c["file"])
    return 1 <= c["line"] <= len(lines) and c["expect"] in lines[c["line"] - 1]


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
        out = []
        stack = list(node.body)
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
        if (n + ".__init__") in m.defs:
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
            if (f.attr + ".__init__") in mods[base].defs:
                return (base, f.attr + ".__init__")
            return None
        return ("ext:" + base, f.attr)
    return None


def edges(mods, node, ctx):
    """Outgoing call edges. ctx 'v2' (SE-3) or 'a1' (SE-3 + HR-3). With RL-1 installed, v2_solver.run_child is the
    recorder, which calls the original run_child; the edge into run_child is kept as the capped-launch terminal."""
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
            t = ("r3_resolve", "solve")
        if t == ("a1_health", "run_system") and mod != "r3_resolve" and ctx == "a1":
            t = ("r3_resolve", "run_system")
        out.append((c.lineno, (t[0], t[1], ""), c))
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


# ============================================================================ the capped-child instance table (carried)
# Carried from the archived census (rb_check.py, TASK-20260924-bf5724) with its cited lines; every line is re-checked.
# rb branch fields: raw = RB-2 (a); meta = RB-2 (b); rb1 = RB-1 / RB-2 (c) as worded ("reading" = only if RB-1 covers a
# gb_only pass-through call). Each rb branch is one on which a child is created and run_child RETURNS a record that
# carries the pair (v2_solver.py 227): ok, refused_meta, no_meta, recorded, ssf_earlier, passthrough, any_outcome.
def inst(iid, commands, caller, launch, kind, tags, branches, raw_path, meta_path, returned, other_files, threads, cites,
         checks=(), launched=True, note=None):
    return {"id": iid, "commands": commands, "caller": {"file": FILES[caller[0]], "line": caller[1]},
            "launch_site": {"file": FILES[launch[0]], "line": launch[1]}, "kind": kind, "tags": tags, "launched_at_run_time": launched,
            "branches": branches, "readback": {"raw_result_write_path": raw_path, "child_meta_json": meta_path,
                                               "returned_to_S1_or_S2_wrapper": returned, "other_package_files": other_files},
            "threads_executed": threads, "cites": [{"file": FILES[f], "line": ln, "expect": s} for f, ln, s in cites],
            "static_checks": list(checks), "note": note}


TH_NA = {"applies": False}
TH_CG = {"applies": True, "note": "the frozen callgrind record (v2_solver.py 519-520) carries no threads value"}
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
                           {"branch": "ssf_earlier", "raw": False, "meta": False, "rb1": True}]
S1_RET = "result['solver']['rlimit_as_child_getrlimit'] (v2_driver.py 167, _slim 151)"


def s1_threads(raw, raw_path):
    return {"applies": True, "raw_result": raw, "raw_result_write_path": raw_path, "returned": "result['threads_executed'] (v2_driver.py 169)"}


INSTANCES = [
    inst("I-01", ["v2-r3 fixture"], ("v2d", 317), ("v2d", 101), "builder (build_poly)", "fixture_<arm> (4)",
         [{"branch": "ok", "raw": True, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "builds.<arm>.child.rlimit_as_child_getrlimit", "child/fixture_<arm>.meta.json (ok)", "not a wrapped call", [],
         TH_NA, BUILD_CITES + [("v2d", 317, 'build_poly(ctx, F, E, arm, m, seed, "fixture_%s" % arm'), ("v2d", 321, 'raw["builds"] = builds')]),
    inst("I-02", ["v2-r3 fixture"], ("v2d", 348), ("v2d", 101), "builder (raw_grid)", "fx_<target>_<raw_x|raw_u>",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "on failure only: targets[].arms.<arm>.reason.child (350)", "child/<tag>.meta.json (ok)", "not a wrapped call", [], TH_NA,
         GRID_CITES + [("v2d", 348, 'raw_grid(ctx, F, E, kind, m, t["x_R"], nodes, tag'), ("v2d", 350, '"reason": ginfo'),
                       ("v2d", 353, 'cons = ginfo["meta"]["construction_ops"]')]),
    inst("I-03", ["v2-r3 fixture"], ("v2d", 358), ("v2d", 166), "S-1 solve (msolve)", "fx_<target>_<arm>",
         S1_BRANCHES(True), "targets[] | replaced_fresh_targets[] | planted_targets[] .arms.<arm>.solver", None, S1_RET, [],
         s1_threads(True, "targets[]....arms.<arm>.threads_executed"),
         S1_CITES + [("v2d", 358, "r = solve(ctx, names, eqs, tag"), ("v2d", 359, '"threads_executed", "input", "solver"')]),
    inst("I-04", ["v2-r3 fixture"], ("v2d", 358), ("v2s", 517), "S-3 callgrind (valgrind -> msolve)", "<tag> of each ok S-1 attempt",
         [{"branch": "ok_solve_with_callgrind_timeout", "raw": True, "meta": False, "rb1": False}],
         "targets[]....arms.<arm>.instructions_callgrind.child", None, "inside the S-1 result (instructions_callgrind.child)", [], TH_CG,
         [("v2d", 207, 'if callgrind_timeout and outcome == "ok"'), ("v2d", 209, 'res["instructions_callgrind"] = V.callgrind_instructions('),
          ("v2s", 517, "rec = run_child(vargv"), ("v2s", 519, '"rlimit_as_child_getrlimit"'), ("v2d", 360, '"instructions_callgrind"')]),
    inst("I-05", ["v2-r3 fixture4"], ("v2d", 548), ("v2d", 101), "builder (build_poly)", "f4_<arm> (4)",
         [{"branch": "ok", "raw": True, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "builds.<arm>.child", "child/f4_<arm>.meta.json (ok)", "not a wrapped call", [], TH_NA,
         BUILD_CITES + [("v2d", 548, "build_poly(ctx, F, E, arm, 4"), ("v2d", 551, 'raw["builds"] = builds')]),
    inst("I-06", ["v2-r3 fixture4"], ("v2d", 565), ("v2d", 166), "S-1 solve (msolve)", "f4_t<i>_<arm>", S1_BRANCHES(True),
         "targets[].arms.<arm>.solver", None, S1_RET, [], s1_threads(True, "targets[].arms.<arm>.threads_executed"),
         S1_CITES + [("v2d", 565, 'r = solve(ctx, names, eqs, "f4_t%d_%s"'), ("v2d", 566, '"threads_executed", "input", "solver"')]),
    inst("I-07", ["v2-r3 anchor-identity"], ("v2d", 650), ("v2d", 650), "Sage comparator", "comparator (1)",
         [{"branch": "any_outcome", "raw": True, "meta": False, "rb1": False}], "comparator.child", None, "not a wrapped call", [], TH_NA,
         [("v2d", 650, "V.run_child([C.SAGE_PYTHON, C.COMPARATOR, cdir]"), ("v2d", 652, 'comp["child"] = _slim(rec)'),
          ("v2d", 655, 'raw["comparator"] = comp')]),
    inst("I-08", ["v2-r3 anchor-identity"], ("v2d", 671), ("v2d", 101), "builder (build_poly)", "anchor_S4 (1)",
         [{"branch": "ok", "raw": True, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "build.child", "child/anchor_S4.meta.json (ok)", "not a wrapped call", [], TH_NA,
         BUILD_CITES + [("v2d", 671, 'build_poly(ctx, F, E, "S4", 4'), ("v2d", 673, 'raw["build"] = binfo')]),
    inst("I-09", ["v2-r3 anchor-identity"], ("v2d", 693), ("v2d", 166), "S-1 solve (msolve -g 1; gb_only pass-through)",
         "anchor_<comparator_random|v2_t0..t2> (4)", [{"branch": "passthrough", "raw": True, "meta": False, "rb1": "reading", "rl2": True}],
         "targets[].solver", None, S1_RET + " through the r3 pass-through (r3_resolve.py 382-387)", [],
         s1_threads(True, "targets[].threads_executed"),
         S1_CITES + [("v2d", 693, "gb_only=True"), ("v2d", 697, '"threads_executed": r["threads_executed"]'), ("v2d", 699, '"solver": r["solver"]'),
                     ("r3r", 382, "if gb_only:")]),
    inst("I-10", ["v2-r3 anchor-identity"], ("v2d", 711), ("v2d", 166), "S-1 solve (msolve -g 1; gb_only pass-through)",
         "anchor_comparator_system (1)", [{"branch": "passthrough", "raw": False, "meta": False, "rb1": "reading", "rl2": True}],
         "NONE: row['comparator_system'] keeps outcome, input and the trace only (v2_driver.py 713-716)", None,
         S1_RET + " through the r3 pass-through (r3_resolve.py 382-387)", [],
         {"applies": True, "raw_result": False, "returned": "result['threads_executed'] (v2_driver.py 169)"},
         S1_CITES + [("v2d", 711, 'rc = solve(ctx, cn, ceqs, "anchor_comparator_system"'), ("v2d", 714, 'row["comparator_system"]["outcome"] = rc["outcome"]'),
                     ("v2d", 716, 'row["comparator_system"]["input"] = rc["input"]'), ("r3r", 382, "if gb_only:"),
                     ("r3r", 383, '"passthrough_calls_gb_only_true"'), ("r3r", 253, 'cnt["wrapped_calls"] += 1')],
         checks=[{"kind": "names_loaded", "file": FILES["v2d"], "func": "cmd_anchor_identity", "name": "rc",
                  "expect_attrs_or_subscripts": ["f4_rounds", "outcome", "input"]}]),
    inst("I-11", ["v2-r3 controls"], ("v2d", 768), ("v2d", 101), "builder (build_poly)", "ctl_identity_n3 (1)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: info is never read after line 768", "child/ctl_identity_n3.meta.json (ok)", "not a wrapped call", [], TH_NA,
         BUILD_CITES + [("v2d", 768, 'pol, info = build_poly(ctx, F, E, "identity", 3'), ("v2d", 924, 'raw = {"kind": "frozen_controls"')],
         checks=[{"kind": "name_never_loaded", "file": FILES["v2d"], "func": "cmd_controls", "name": "info"}],
         note="refused_meta is unreachable for kind identity (x_in_Fp base; v2_child.py 65, 79)"),
    inst("I-12", ["v2-r3 controls"], ("v2d", 782), ("v2d", 101), "builder (raw_grid)", "ctl_raw_random, ctl_raw_planted (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: ginfo is never read after line 782", "child/ctl_raw_<label>.meta.json (ok)", "not a wrapped call", [], TH_NA,
         GRID_CITES + [("v2d", 782, 'eqs_raw, Cg, ginfo = raw_grid(ctx, F, E, "raw_x", 3')],
         checks=[{"kind": "name_never_loaded", "file": FILES["v2d"], "func": "cmd_controls", "name": "ginfo"}],
         note="refused_meta is unreachable for kind raw_x"),
    inst("I-13", ["v2-r3 controls"], ("v2d", 801), ("v2d", 101), "builder (build_poly)", "ctl_identity_n5_m3, ctl_identity_n5_m4 (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: the record is bound to _ (line 801)", "child/ctl_identity_n5_m<m>.meta.json (ok)", "not a wrapped call", [], TH_NA,
         BUILD_CITES + [("v2d", 801, 'pol5, _ = build_poly(ctx, F5, E5, "identity", m')], note="refused_meta is unreachable for kind identity"),
    inst("I-14", ["v2-r3 controls"], ("v2d", 805), ("v2d", 101), "builder (raw_grid)", "ctl_raw_n5_m3, ctl_raw_n5_m4 (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: the record is bound to _i (line 805)", "child/ctl_raw_n5_m<m>.meta.json (ok)", "not a wrapped call", [], TH_NA,
         GRID_CITES + [("v2d", 805, '_e, Cg5, _i = raw_grid(ctx, F5, E5, "raw_x", m')],
         checks=[{"kind": "name_never_loaded", "file": FILES["v2d"], "func": "cmd_controls", "name": "_i"}],
         note="refused_meta is unreachable for kind raw_x"),
    inst("I-15", ["v2-r3 controls"], ("v2d", 816), ("v2d", 101), "builder (build_poly)",
         "ctl_S3, ctl_S3_rescaled, ctl_torsion_S3_rq, ctl_torsion_S3_norm (4)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": False, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: the record is bound to _ (line 816)", "child/ctl_<arm>.meta.json (ok)", "not a wrapped call", [], TH_NA,
         BUILD_CITES + [("v2d", 816, 'polc, _ = build_poly(ctx, F5, E5, arm, 3')]),
    inst("I-16", ["v2-r3 controls"], ("v2d", 786), ("v2d", 166), "S-1 solve (msolve)", "ctl_identity_random, ctl_identity_planted (2)",
         S1_BRANCHES(False), "NONE (v2_driver.py 792-795)", None, S1_RET, [], s1_threads(False, None),
         S1_CITES + [("v2d", 786, 's_id = solve(ctx, A.varnames("identity", 3), eqs_id, "ctl_identity_%s"'), ("v2d", 793, '"D_identity": s_id and s_id["D"]')]),
    inst("I-17", ["v2-r3 controls"], ("v2d", 787), ("v2d", 166), "S-1 solve (msolve)", "ctl_rawx_random, ctl_rawx_planted (2)",
         S1_BRANCHES(False), "NONE (v2_driver.py 792-795)", None, S1_RET, [], s1_threads(False, None),
         S1_CITES + [("v2d", 787, 's_raw = solve(ctx, A.varnames("raw_x", 3), eqs_raw, "ctl_rawx_%s"')]),
    inst("I-18", ["v2-r3 controls"], ("v2d", 841), ("v2d", 166), "S-1 solve (msolve)", "ctl_planted_<arm> (4)",
         S1_BRANCHES(False), "NONE (v2_driver.py 845-846)", None, S1_RET, [], s1_threads(False, None),
         S1_CITES + [("v2d", 841, 's = solve(ctx, names, eqs, "ctl_planted_%s"'), ("v2d", 846, '{"outcome": s["outcome"], "n_rational_solutions"')]),
    inst("I-19", ["v2-r3 build", "v2-a1-r3 build"], ("v2d", 961), ("v2d", 101), "builder (build_poly, to_cache)",
         "build_<p>_<shape>_<arm>_m<m>",
         [{"branch": "ok", "raw": True, "meta": False, "rb1": False}, {"branch": "refused_meta", "raw": True, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": True, "meta": False, "rb1": False}],
         "polynomials[].info.child", "NONE under child/: to_cache=True writes the meta to C.CACHE_DIR (v2_driver.py 96)",
         "not a wrapped call", [], TH_NA,
         BUILD_CITES + [("v2d", 962, "to_cache=True"), ("v2d", 963, 'row.update(outcome=info["outcome"], seed=seed, info=info)'),
                        ("v2d", 979, '"polynomials": rows'), ("v2d", 96, 'C.CACHE_DIR if spec.get("to_cache") else cd'),
                        ("a1d", 225, "D.cmd_build(args)")]),
    inst("I-20", ["v2-r3 cells", "v2-a1-r3 cells"], ("v2d", 1161), ("v2d", 101), "builder (raw_grid)", "grid_<arm>_t<i> (raw arms, m <= 4)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": False, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE: ok keeps construction_ops (1168); failure keeps a reason string (1163)", "child/grid_<arm>_t<i>.meta.json (ok)",
         "not a wrapped call", [], TH_NA,
         GRID_CITES + [("v2d", 1161, 'raw_grid(ctx, F, E, kind, m, R[0], nodes, "grid_" + tag'),
                       ("v2d", 1163, 'reason="raw grid child: %s" % ginfo.get("reason")'),
                       ("v2d", 1168, 'row["construction_ops"] = ginfo["meta"]["construction_ops"]'), ("a1d", 234, "D.cmd_cells(args)")]),
    inst("I-21", ["v2-r3 cells", "v2-a1-r3 cells"], ("v2d", 1174), ("v2d", 166), "S-1 solve (msolve)", "<arm>_t<i>", S1_BRANCHES(True),
         "cells[].targets[].solver", None, S1_RET, [], s1_threads(True, "cells[].targets[].threads_executed"),
         S1_CITES + [("v2d", 1174, "r = solve(ctx, names, eqs, tag"), ("v2d", 1179, '"threads_executed", "input", "solver"')]),
    inst("I-22", ["v2-r3 cells", "v2-a1-r3 cells"], ("v2d", 1174), ("v2s", 517), "S-3 callgrind (valgrind -> msolve)",
         "<arm>_t0 of each m <= 4 cell with an ok recorded attempt",
         [{"branch": "ok_solve_with_callgrind_timeout", "raw": True, "meta": False, "rb1": False}],
         "cells[].targets[].instructions_callgrind.child", None, "inside the S-1 result (instructions_callgrind.child)", [], TH_CG,
         [("v2d", 1175, "callgrind_timeout=(cg_timeout if (cg_timeout and i == 0) else None)"), ("v2d", 1180, '"instructions_callgrind"'),
          ("v2d", 1089, "if m <= 4 else None"), ("v2s", 519, '"rlimit_as_child_getrlimit"')]),
    inst("I-23", ["v2-a1-r3 controls-a1"], ("a1d", 89), ("a1p", 96), "gp (PARI)", "controls_a1_pari (1)",
         [{"branch": "any_outcome", "raw": True, "meta": False, "rb1": False}], "checks[b].detail.pari.child", None, "not a wrapped call", [], TH_NA,
         [("a1d", 89, "pr = P.curve_facts("), ("a1p", 96, "rec = V.run_child(argv, so, se"), ("a1p", 98, '"rlimit_as_child_getrlimit"'),
          ("a1d", 91, 'detail_b = {"pari": pr'), ("a1d", 112, 'rec("b_pari_ellcard_recheck_and_double_odd_facts", ok_b, detail_b)')]),
]
for _ln, _nm, _launched in ((234, "first", True), (241, "retry_seed2", True), (237, "reinvocation", False), (244, "retry_seed2_reinvocation", False)):
    INSTANCES.append(inst("I-24-" + _nm, ["v2-a1-r3 controls-a1"], ("a1h", _ln), ("a1h", 147), "S-2 health (msolve)",
                          "health_p<p>_d<pattern>%s" % {"first": "", "retry_seed2": "_seed2", "reinvocation": "_reinvoke",
                                                         "retry_seed2_reinvocation": "_seed2_reinvoke"}[_nm],
                          [{"branch": "recorded", "raw": False, "meta": False, "rb1": True},
                           {"branch": "ssf_earlier", "raw": False, "meta": False, "rb1": True}],
                          "NONE under the collected key (first system at checks[d].detail.per_pattern[].getrlimit, a1_driver.py 133)",
                          None, "result['child']['rlimit_as_child_getrlimit'] (a1_health.py 150)",
                          ["health/health-<p>.json (a1_health.py 248-252)"],
                          {"applies": True, "raw_result": False, "returned": "result['threads_executed'] (a1_health.py 149)"},
                          [("a1d", 129, 'hr = H.run(p, os.path.join(ctx.rd, "health"), cap=ctx.cap)'),
                           ("a1h", 147, "rec = V.run_child(argv, logp, errp"), ("a1h", 149, '"threads_executed": V.threads_from_argv(argv)'),
                           ("a1h", 150, '"rlimit_as_child_getrlimit"'), ("a1h", 223, "reinvoke_on_fail=False"), ("a1h", _ln, "run_system("),
                           ("r3r", 199, '"child_rlimit_as_getrlimit": child.get("rlimit_as_child_getrlimit")'), ("r3r", 408, "return _bounded(R.SITE_S2")],
                          checks=[{"kind": "call_lacks_keyword", "file": FILES["a1d"], "line": 129, "keyword": "reinvoke_on_fail"}],
                          launched=_launched,
                          note=None if _launched else "not executed: H.run is called without reinvoke_on_fail (default False, a1_health.py 223)"))
INSTANCES += [
    inst("I-25", ["v2-a1-r3 controls-a1"], ("a1d", 146), ("v2d", 101), "builder (build_poly)", "ctl_a1_torsion_S3_rq, ctl_a1_S3_rescaled (2)",
         [{"branch": "ok", "raw": False, "meta": True, "rb1": False}, {"branch": "refused_meta", "raw": False, "meta": False, "rb1": False},
          {"branch": "no_meta", "raw": False, "meta": False, "rb1": False}],
         "NONE under the collected key (checks[f].detail.<arm>.build_getrlimit, a1_driver.py 184)", "child/ctl_a1_<arm>.meta.json (ok)",
         "not a wrapped call", [], TH_NA,
         BUILD_CITES + [("a1d", 146, 'polc, info = D.build_poly(ctx, F, E5, arm, 3, seed, "ctl_a1_%s"'),
                        ("a1d", 163, '"build": {k: info.get(k) for k in ("outcome", "reason")}'), ("a1d", 184, '"build_getrlimit"')]),
    inst("I-26", ["v2-a1-r3 controls-a1"], ("a1d", 166), ("v2d", 166), "S-1 solve (msolve)", "ctl_a1_planted_<arm> (2)",
         S1_BRANCHES(False), "NONE under the collected key (checks[e].detail.solver_getrlimit, a1_driver.py 174)", None, S1_RET, [],
         s1_threads(True, "checks[e].detail.threads_executed (a1_driver.py 173)"),
         S1_CITES + [("a1d", 166, 's = D.solve(ctx, names, eqs, "ctl_a1_planted_%s"'), ("a1d", 173, '"threads_executed": s.get("threads_executed")'),
                     ("a1d", 174, '"solver_getrlimit"')]),
]
for _cmd, _f, _ln in (("v2-r3 fixture4", "v2d", 565), ("v2-r3 anchor-identity", "v2d", 693), ("v2-r3 anchor-identity", "v2d", 711),
                      ("v2-r3 controls", "v2d", 786), ("v2-r3 controls", "v2d", 787), ("v2-r3 controls", "v2d", 841),
                      ("v2-a1-r3 controls-a1", "a1d", 166)):
    INSTANCES.append(inst("I-NL-%s-%d" % (_f, _ln), [_cmd], (_f, _ln), ("v2s", 517), "S-3 callgrind (static path only)", "none",
                          [], None, None, None, [], TH_NA, [("v2d", 207, 'if callgrind_timeout and outcome == "ok"')],
                          checks=[{"kind": "call_lacks_keyword", "file": FILES[_f], "line": _ln, "keyword": "callgrind_timeout"}],
                          launched=False, note="never launched: callgrind_timeout defaults to None (v2_driver.py 158) and line 207 requires it"))

# count_instructions per launch site: only v2_driver.py 166 passes none (default True, v2_solver.py 150); the others pass False
COUNT_INSTR_TRUE_SITES = {(FILES["v2d"], 166)}


# ============================================================================ static checks (carried)
def func_node(rel, name):
    tree = ast.parse(read_bytes(rel, False), filename=rel)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    return None


def call_at(rel, line):
    tree = ast.parse(read_bytes(rel, False), filename=rel)
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and n.lineno == line]


def run_static_check(chk):
    k = chk["kind"]
    if k in ("call_has_keyword", "call_lacks_keyword"):
        cs = call_at(chk["file"], chk["line"])
        target = [c for c in cs if isinstance(c.func, (ast.Name, ast.Attribute)) and
                  (getattr(c.func, "id", None) or getattr(c.func, "attr", None)) in ("solve", "run", "H.run")]
        if not target:
            target = cs
        has = any(any(kw.arg == chk["keyword"] for kw in c.keywords) for c in target)
        return dict(chk, observed_has_keyword=has, ok=(has if k == "call_has_keyword" else not has))
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


def mods_enclosing(mods, rel, line):
    for m in mods.values():
        if m.rel == rel:
            return m.enclosing(line)
    return None


# ============================================================================ launch scan (every scanned tree)
def launch_scan():
    capped, setr, other, private = [], [], [], []
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
                elif name == "_run_child_locked":
                    private.append({"file": rel, "line": c.lineno, "enclosing": q})
                elif name in ("setrlimit", "prlimit"):
                    setr.append({"file": rel, "line": c.lineno, "enclosing": q, "text": text_lines(rel)[c.lineno - 1].strip()})
                elif (base, name) in EXT_LAUNCH or (base is None and name in ("Popen", "execv", "execve", "system")):
                    other.append({"file": rel, "line": c.lineno, "enclosing": q, "call": "%s.%s" % (base, name) if base else name})
    return {"run_child_call_sites": capped, "_run_child_locked_call_sites": private, "setrlimit_or_prlimit_call_sites": setr,
            "other_launch_call_sites": other}


def tools_harness_text_scan(words):
    """Text scan (bytes read, never imported) of every file under tools/ and harness/ for the given words."""
    hits, n, h = [], 0, hashlib.sha256()
    for top in ("tools", "harness"):
        for dp, dn, fn in os.walk(os.path.join(REPO, top)):
            dn[:] = sorted(d for d in dn if d != "__pycache__")
            for f in sorted(fn):
                ap = os.path.join(dp, f)
                rel = os.path.relpath(ap, REPO)
                try:
                    with open(ap, "rb") as fh:
                        b = fh.read()
                except OSError:
                    continue
                n += 1
                h.update(rel.encode() + b"\0" + hashlib.sha256(b).digest())
                t = b.decode("utf-8", errors="replace")
                for i, line in enumerate(t.splitlines(), 1):
                    for w in words:
                        if w in line:
                            hits.append({"file": rel, "line": i, "word": w, "text": line.strip()[:160]})
    return {"files_scanned": n, "combined_digest_sha256": h.hexdigest(), "hits": hits}


# ============================================================================ RLR-1 (a): run_child paths
RC_RETURNS = {"run_child": [155, 160, 165, 169, 171], "_run_child_locked": [225, 232, 308]}
RUN_CHILD_PATHS = [
    # id, branch (draft vocabulary), where, child_created, returns_or_raises, pair_in_returned_record, cites
    ("P-1", "refused_before_fork", "invalid cap (not an int, or <= 0)", False, "returns rec (outcome refused_to_start)", False,
     [("v2s", 153, "if not isinstance(cap_bytes, int) or cap_bytes <= 0:"), ("v2s", 155, "return rec")]),
    ("P-2", "refused_before_fork", "driver RSS above 1 GiB", False, "returns rec (refused_to_start)", False,
     [("v2s", 158, "if rss is not None and rss > DRIVER_RSS_LIMIT:"), ("v2s", 160, "return rec")]),
    ("P-3", "refused_before_fork", "another solver-like process is running (EC-10)", False, "returns rec (refused_to_start)", False,
     [("v2s", 162, "if others:"), ("v2s", 165, "return rec")]),
    ("P-4", "refused_before_fork", "host solver lock held", False, "returns rec (refused_to_start)", False,
     [("v2s", 167, "if lk is not None and not lk.acquire(wait_s=0):"), ("v2s", 169, "return rec")]),
    ("P-5", "raised (before fork)", "self_rss_bytes open(/proc/self/status), other_solver_processes os.listdir(/proc), SolverLock.acquire "
     "open(LOCK_PATH, 'a+'), os.pipe (x2) or os.fork raises OSError", False, "RAISES (no record)", False,
     [("v2s", 156, "rss = self_rss_bytes()"), ("v2s", 161, "others = other_solver_processes()"), ("v2s", 101, 'self.fh = open(self.path, "a+")'),
      ("v2s", 178, "rep_r, rep_w = os.pipe()"), ("v2s", 181, "pid = os.fork()")]),
    ("P-6", "ERR setrlimit (child created; NOT A BAR in RLR-1)", "the child cannot set RLIMIT_AS: it writes 'ERR setrlimit ...' and exits 97",
     True, "returns rec (refused_to_start; child_rlimit_report 'ERR setrlimit ...'; returncode)", False,
     [("v2s", 193, "resource.setrlimit(resource.RLIMIT_AS, (cap_bytes, cap_bytes))"), ("v2s", 195, 'os.write(rep_w, ("ERR setrlimit %r" % (e,)).encode())'),
      ("v2s", 220, 'rec["child_rlimit_report"] = report'), ("v2s", 221, 'if not report.startswith("OK"):'), ("v2s", 225, "return rec")]),
    ("P-7", "pre-setrlimit child failure (child created; empty report)", "in the child, os.chdir(cwd), os.open(stdout_path|stderr_path) or "
     "os.dup2 raises before setrlimit; the except at 206 swallows it and the child exits 99 without writing to the report pipe; the parent "
     "reads an EMPTY report", True, "returns rec (refused_to_start 'child could not set RLIMIT_AS: '; child_rlimit_report '')", False,
     [("v2s", 188, "fo = os.open(stdout_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)"), ("v2s", 206, "except BaseException:"),
      ("v2s", 208, "os._exit(99)"), ("v2s", 224, 'refusal_reason="child could not set RLIMIT_AS: %s" % report')]),
    ("P-8", "no_meta: pre-exec read-back mismatch", "the child reads back soft != cap: exits 98; the parent, having set the pair, refuses",
     True, "returns rec (refused_to_start; returncode)", True,
     [("v2s", 227, 'rec["rlimit_as_child_getrlimit"] = {"soft": int(soft), "hard": int(hard)}'), ("v2s", 228, "if int(soft) != cap_bytes:"),
      ("v2s", 232, "return rec")]),
    ("P-9", "no_meta: pre-exec mismatch on hard only", "soft == cap, hard != cap: the child exits 98 (line 200 tests both) while the parent "
     "tests soft only (228) and continues: if the child is still alive the write at 236 succeeds and the child's exit 98 is recorded "
     "as a nonzero exit (P-12); if it has already exited, the write raises (P-14)", True, "returns rec (P-12) or RAISES (P-14): a race",
     True, [("v2s", 200, "if soft != cap_bytes or hard != cap_bytes:"), ("v2s", 228, "if int(soft) != cap_bytes:"), ("v2s", 236, 'os.write(go_w, b"g")')]),
    ("P-10", "ok (without perf)", "exit 0; count_instructions False or perf_event_open failed", True, "returns rec (outcome ok)", True,
     [("v2s", 288, 'elif rec["returncode"] == 0:'), ("v2s", 284, 'rec["instructions"] = {"method": None'), ("v2s", 308, "return rec")]),
    ("P-11", "ok (with perf)", "exit 0; perf counter opened and read", True, "returns rec (ok) unless _perf_read raises (P-15)", True,
     [("v2s", 280, "if perf_fd is not None:"), ("v2s", 281, 'rec["instructions"] = {"method": "perf_event_open instructions:u'),
      ("v2s", 308, "return rec")]),
    ("P-12", "no_meta: memory_exhausted / crash / nonzero exit (incl. exec failure, exit 99)", "nonzero status; memory_exhausted iff near-cap "
     "evidence or an allocation-failure message, else crashed", True, "returns rec", True,
     [("v2s", 304, 'rec["outcome"] = "memory_exhausted" if (near_cap or alloc_msg) else "crashed"'), ("v2s", 308, "return rec")]),
    ("P-13", "no_meta: timeout", "watchdog: SIGKILL after timeout_s", True, "returns rec (outcome timeout)", True,
     [("v2s", 263, "if timeout_s is not None and time.time() - t0 > timeout_s:"), ("v2s", 287, 'rec["outcome"] = "timeout"'),
      ("v2s", 308, "return rec")]),
    ("P-14", "raised (after fork)", "os.write(go_w) raises BrokenPipeError when the child exited after reporting OK and before the go byte "
     "(P-9, or the child killed by a signal in that window); os.read (214), os.close, os.wait4 (223, 230, 244) raising OSError are also "
     "raise points", True, "RAISES (the record, with the pair already set at 227, is not returned)", "not returned",
     [("v2s", 236, 'os.write(go_w, b"g")'), ("v2s", 214, "chunk = os.read(rep_r, 256)"), ("v2s", 244, "wpid, st, r = os.wait4(pid, os.WNOHANG)")]),
    ("P-15", "raised (after the child is reaped)", "_perf_read: os.read or struct.unpack raises (reachable only with count_instructions "
     "True and an opened counter)", True, "RAISES (record not returned)", "not returned",
     [("v2s", 141, 'v, enabled, running = struct.unpack("QQQ", os.read(fd, 24))'), ("v2s", 281, "**_perf_read(perf_fd)")]),
]


def rlr1_run_child_paths():
    m = Mod(FILES["v2s"])
    rets = {}
    for fn in ("run_child", "_run_child_locked"):
        node = m.defs[fn]
        rets[fn] = sorted(n.lineno for n in ast.walk(node) if isinstance(n, ast.Return))
    raises = sorted(n.lineno for fn in ("run_child", "_run_child_locked") for n in ast.walk(m.defs[fn]) if isinstance(n, ast.Raise))
    rows = []
    for pid, br, where, created, ret, pair, cites in RUN_CHILD_PATHS:
        rows.append({"id": pid, "branch": br, "where": where, "child_created": created, "returns_or_raises": ret,
                     "returned_record_carries_rlimit_as_child_getrlimit": pair,
                     "lines": [cite("RLR-1 run_child paths", f, ln, s) for f, ln, s in cites]})
    return {"function": "v2_solver.run_child (first line 149) and _run_child_locked (first line 177)",
            "docstring_claim": cite("RLR-1 run_child paths", "v2s", 151, "never raises for child failures"),
            "pair_set_at": cite("RLR-1 run_child paths", "v2s", 227, 'rec["rlimit_as_child_getrlimit"]'),
            "return_statements_found_by_ast": rets, "return_statements_expected": RC_RETURNS,
            "return_statements_equal_expected": rets == RC_RETURNS,
            "explicit_raise_statements": raises,
            "child_process_never_returns_to_python": cite("RLR-1 run_child paths", "v2s", 208, "os._exit(99)"),
            "paths": rows}


# ============================================================================ RLR-1 (b): per instance, per branch
def call_site_intercepted(launch):
    """RLR-2 result per launch site (filled by rlr2 before rlr1_instances)."""
    return INTERCEPT.get((launch["file"], launch["line"]))


INTERCEPT = {}


def rlr1_instances(mods):
    entries = command_entries(mods)
    per_cmd, uncovered_paths = {}, []
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
        per_cmd[cmd] = {"entry": node_key(entry), "runtime_binding": "SE-3" + (" + HR-3" if ctx == "a1" else "") + " + RL-1 (recorder over run_child)",
                        "n_paths_to_capped_launch": len(capped), "paths": rows,
                        "uncapped_launches_reachable": sorted({"%s:%d (%s) -> %s" % (p[-1]["file"], p[-1]["line"], p[-1]["caller"], p[-1]["callee"])
                                                               for p in uncapped})}
    unmatched = [{"id": i, "commands_declared": next(x for x in INSTANCES if x["id"] == i)["commands"], "commands_with_path": sorted(s)}
                 for i, s in inst_hits.items() if set(next(x for x in INSTANCES if x["id"] == i)["commands"]) != s]
    for i in INSTANCES:
        for c in i["cites"]:
            CITES.append({"reading": "RLR-1 instance %s" % i["id"], "file": c["file"], "line": c["line"], "expect": c["expect"]})
        i["static_check_results"] = [run_static_check(ch) for ch in i["static_checks"]]
    table, no_source, not_a_bar, static_only = [], [], [], []
    for i in INSTANCES:
        if not i["launched_at_run_time"] and not i["branches"]:
            static_only.append({"id": i["id"], "commands": i["commands"], "caller": "%s:%d" % (i["caller"]["file"], i["caller"]["line"]),
                                "note": i["note"], "static_check_results": i["static_check_results"]})
            continue
        icpt = call_site_intercepted(i["launch_site"])
        rl1_ok = bool(icpt and icpt["intercepted_by_RL1_replacement"])
        brs = []
        # (1) the carried branches: child created; run_child returned a record carrying the pair
        for b in i["branches"]:
            src = []
            if b.get("raw"):
                src.append("RB-2 (a) raw-result.json")
            if b.get("meta"):
                src.append("RB-2 (b) child/*.meta.json")
            if b.get("rb1") is True:
                src.append("RB-1 / RB-2 (c) attempt record")
            if rl1_ok:
                src.append("RL-1 launch record / RL-3 (d)")
            if b.get("rl2"):
                src.append("RL-2 pass-through record / RL-3 (e)")
            brs.append({"branch": b["branch"], "child_created": True, "run_child_returns": True,
                        "returned_record_carries_pair": True, "sources": src or ["NONE"],
                        "archived_census_sources_under_RB1_RB2": [s for s in src if s.startswith("RB-")] or ["NONE"]})
        # (2) run_child-level branches the draft's definitions add (P-rows of RLR-1 (a)); they apply to every launch site
        s1 = (i["launch_site"]["file"], i["launch_site"]["line"]) in COUNT_INSTR_TRUE_SITES
        brs.append({"branch": "refused_before_fork (P-1..P-4)", "child_created": False, "run_child_returns": True,
                    "returned_record_carries_pair": False, "sources": ["no child is created (NOT A BAR)"],
                    "RL-1_records": "child_created false; pair 'absent' with refusal_reason"})
        brs.append({"branch": "raised before fork (P-5)", "child_created": False, "run_child_returns": False,
                    "returned_record_carries_pair": False, "sources": ["no child is created"],
                    "RL-1_records": "raised: <type>; child_created false (no returned record)"})
        brs.append({"branch": "ERR setrlimit (P-6)", "child_created": True, "run_child_returns": True, "returned_record_carries_pair": False,
                    "sources": ["NONE (no pair is ever taken; NOT A BAR as the draft words it)"],
                    "RL-1_records": "pair 'absent' with child_rlimit_report 'ERR setrlimit ...' and refusal_reason; child_created true",
                    "no_source_named": True, "draft_not_a_bar": True})
        brs.append({"branch": "pre-setrlimit child failure (P-7)", "child_created": True, "run_child_returns": True,
                    "returned_record_carries_pair": False, "sources": ["NONE (no pair is ever taken)"],
                    "RL-1_records": ("pair 'absent' with child_rlimit_report '' (the key is present, its value is empty) and refusal_reason "
                                     "'child could not set RLIMIT_AS: '; child_created true if RL-1 (c)'s test is the key's presence"),
                    "no_source_named": True, "draft_not_a_bar": "not named by the draft: the draft names 'the ERR setrlimit branch'"})
        brs.append({"branch": "raised after fork (P-14%s)" % (", P-15" if s1 else ""), "child_created": True, "run_child_returns": False,
                    "returned_record_carries_pair": "not returned (the pair was set at 227 in a record run_child does not return)",
                    "sources": ["NONE"],
                    "RL-1_records": ("raised: <type>; pair 'absent'; child_created FALSE, because RL-1 (c) tests the RETURNED record for "
                                     "child_rlimit_report and there is none"),
                    "no_source_named": True, "draft_not_a_bar": "not named by the draft (NOT A BAR lists ERR setrlimit, grandchildren, "
                                                                "refused_before_fork, a child found in two sources)"})
        if True:
            brs.append({"branch": "raised in the frozen caller after run_child returned (archived census L-1)", "child_created": True,
                        "run_child_returns": True, "returned_record_carries_pair": True,
                        "sources": ["RL-1 launch record / RL-3 (d)"] if rl1_ok else ["NONE"],
                        "note": "RL-1 (c) appends the launch record before run_child's return reaches the caller"})
        for b in brs:
            if b.get("no_source_named") or (b["child_created"] and b["sources"] == ["NONE"]):
                rec = {"instance": i["id"], "commands": i["commands"], "kind": i["kind"], "tags": i["tags"], "branch": b["branch"],
                       "launch_site": "%s:%d" % (i["launch_site"]["file"], i["launch_site"]["line"]),
                       "launched_at_run_time": i["launched_at_run_time"], "draft_not_a_bar": b.get("draft_not_a_bar", False)}
                (not_a_bar if b.get("draft_not_a_bar") is True else no_source).append(rec)
        table.append({"id": i["id"], "commands": i["commands"], "kind": i["kind"], "tags": i["tags"],
                      "caller": "%s:%d" % (i["caller"]["file"], i["caller"]["line"]),
                      "caller_function": mods_enclosing(mods, i["caller"]["file"], i["caller"]["line"]),
                      "launch_site": "%s:%d" % (i["launch_site"]["file"], i["launch_site"]["line"]),
                      "launch_site_intercepted_by_RL1": rl1_ok, "launched_at_run_time": i["launched_at_run_time"],
                      "count_instructions_true": s1, "readback_archived": i["readback"], "threads_executed": i["threads_executed"],
                      "branches": brs, "note": i["note"], "static_check_results": i["static_check_results"]})
    carried_no_source = [r for r in table for b in r["branches"] if b.get("archived_census_sources_under_RB1_RB2") == ["NONE"]]
    return {"method": ("the archived census's static call graph (runtime modules parsed with ast; SE-3 both entries, HR-3 a1 entry) re-run "
                       "on the same bytes; its instance table carried with every cited line re-checked; per instance the branches the "
                       "archived census defines (a child is created and run_child returns a record carrying the pair) plus the "
                       "run_child-level branches of RLR-1 (a); sources under RB-1, RB-2 (a)-(c), RL-1 / RL-3 (d) and RL-2 / RL-3 (e) "
                       "as worded; RL-1 counts only where RLR-2 finds the call site intercepted"),
            "commands": per_cmd, "coverage": {"paths_not_covered_by_an_instance": uncovered_paths, "instances_without_a_matching_path": unmatched},
            "instances": table, "static_paths_never_launched": static_only,
            "created_child_branches_with_no_source_not_named_not_a_bar": no_source,
            "created_child_branches_with_no_source_named_not_a_bar_by_the_draft": not_a_bar,
            "carried_branches_with_no_RB_source_now_with_RL1": sorted({"%s %s" % (r["id"], b["branch"]) for r in table for b in r["branches"]
                                                                        if b.get("archived_census_sources_under_RB1_RB2") == ["NONE"]}),
            "n_carried_no_rb_source_rows": len(carried_no_source)}


# ============================================================================ RLR-2
def is_module_binding_of(m, name, modname):
    """True iff `name` is bound in module m only by a module-level `import <modname> as <name>` (never re-bound anywhere)."""
    binds = []
    for n in ast.walk(m.tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if (a.asname or a.name) == name:
                    binds.append(("import", n.lineno, a.name))
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                if (a.asname or a.name) == name:
                    binds.append(("from-import", n.lineno, n.module))
        elif isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.For, ast.With, ast.NamedExpr)):
            for t in ast.walk(n):
                if isinstance(t, ast.Name) and t.id == name and isinstance(t.ctx, ast.Store):
                    binds.append(("assign", t.lineno, None))
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            for a in n.args.args + n.args.kwonlyargs + n.args.posonlyargs:
                if a.arg == name:
                    binds.append(("argument", n.lineno, getattr(n, "name", "lambda")))
        elif isinstance(n, (ast.Global, ast.Nonlocal)) and name in n.names:
            binds.append(("global", n.lineno, None))
    top = [b for b in binds if b[0] == "import" and b[2] == modname]
    return binds, (len(binds) >= 1 and len(top) == len(binds))


def rlr2(mods, scan):
    sites = []
    reachable = {(FILES["v2d"], 101), (FILES["v2d"], 166), (FILES["v2d"], 650), (FILES["v2s"], 517), (FILES["a1h"], 147), (FILES["a1p"], 96)}
    for s in scan["run_child_call_sites"]:
        rel, ln = s["file"], s["line"]
        m = Mod(rel)
        call = [c for c in call_at(rel, ln) if (getattr(c.func, "id", None) or getattr(c.func, "attr", None)) == "run_child"][0]
        expr = ast.unparse(call.func)
        row = {"file": rel, "line": ln, "enclosing_function": s["enclosing"], "expression": expr,
               "reachable_from_a_command": (rel, ln) in reachable}
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            nm = call.func.value.id
            binds, only_mod = is_module_binding_of(m, nm, "v2_solver")
            row.update(form="module-attribute lookup at call time (%s.run_child)" % nm,
                       name_bindings_in_module=[{"kind": b[0], "line": b[1], "what": b[2]} for b in binds],
                       name_is_only_the_v2_solver_module=only_mod,
                       intercepted_by_RL1_replacement=only_mod)
        elif isinstance(call.func, ast.Name) and m.name == "v2_solver":
            fn = m.defs[s["enclosing"]]
            local = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id == "run_child" and isinstance(n.ctx, ast.Store)]
            argn = [a.arg for a in fn.args.args + fn.args.kwonlyargs if a.arg == "run_child"]
            gl = [n.lineno for n in ast.walk(m.tree) if isinstance(n, ast.Name) and n.id == "run_child" and isinstance(n.ctx, ast.Store)]
            row.update(form="module-global lookup inside v2_solver (name run_child in %s)" % s["enclosing"],
                       local_bindings_of_run_child_in_function=local + argn, module_level_rebindings_of_run_child=gl,
                       intercepted_by_RL1_replacement=(not local and not argn and not gl))
        else:
            row.update(form="a name bound earlier", intercepted_by_RL1_replacement=False)
        sites.append(row)
        if row["reachable_from_a_command"]:
            INTERCEPT[(rel, ln)] = row
    for f, ln, s in (("v2d", 38, "import v2_solver as V"), ("a1h", 48, "import v2_solver as V"), ("a1p", 24, "import v2_solver as V"),
                     ("v2s", 517, "rec = run_child(vargv"), ("v2s", 171, "return _run_child_locked(")):
        cite("RLR-2 call forms", f, ln, s)
    # every non-call reference to run_child / _run_child_locked in every scanned tree (capture search), and every from-import
    captures, from_imports, imports_v2_solver, dyn = [], [], [], []
    for rel in scanned_py_files():
        m = Mod(rel)
        call_funcs = {id(c.func) for c in ast.walk(m.tree) if isinstance(c, ast.Call)}
        for n in ast.walk(m.tree):
            if isinstance(n, ast.Attribute) and n.attr in ("run_child", "_run_child_locked") and id(n) not in call_funcs:
                captures.append({"file": rel, "line": n.lineno, "enclosing": m.enclosing(n.lineno), "expr": ast.unparse(n),
                                 "context": text_lines(rel)[n.lineno - 1].strip()[:160]})
            elif isinstance(n, ast.Name) and n.id in ("run_child", "_run_child_locked") and id(n) not in call_funcs:
                captures.append({"file": rel, "line": n.lineno, "enclosing": m.enclosing(n.lineno), "expr": n.id,
                                 "context": text_lines(rel)[n.lineno - 1].strip()[:160]})
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in ("run_child", "_run_child_locked"):
                captures.append({"file": rel, "line": n.lineno, "enclosing": m.enclosing(n.lineno), "expr": repr(n.value),
                                 "context": text_lines(rel)[n.lineno - 1].strip()[:160]})
            elif isinstance(n, ast.ImportFrom) and n.module == "v2_solver":
                from_imports.append({"file": rel, "line": n.lineno, "names": [a.name for a in n.names]})
            elif isinstance(n, ast.Import):
                for a in n.names:
                    if a.name == "v2_solver":
                        imports_v2_solver.append({"file": rel, "line": n.lineno, "as": a.asname,
                                                  "level": "module" if m.enclosing(n.lineno) == "<module>" else "function %s" % m.enclosing(n.lineno)})
        txt = "\n".join(text_lines(rel))
        for w in ("importlib", "spec_from_file_location", "exec_module", "sys.modules[", "__import__(\"v2_solver", "runpy"):
            if w in txt:
                dyn.append({"file": rel, "word": w, "lines": [i for i, l in enumerate(text_lines(rel), 1) if w in l]})
    # the import closure of the two r3 entries (module-level and function-level imports distinguished)
    closure = {}
    for ent in ("r3_entry_v2", "r3_entry_a1"):
        seen, stack, rows = set(), [ent], []
        while stack:
            mn = stack.pop()
            if mn in seen or mn not in mods:
                continue
            seen.add(mn)
            m = mods[mn]
            for n in ast.walk(m.tree):
                names = []
                if isinstance(n, ast.Import):
                    names = [a.name.split(".")[0] for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module:
                    names = [n.module.split(".")[0]]
                for nm in names:
                    rows.append({"importer": mn, "line": n.lineno, "imports": nm, "at": "module level" if m.enclosing(n.lineno) == "<module>"
                                 else "inside %s" % m.enclosing(n.lineno), "scanned_runtime_module": nm in mods})
                    if nm in mods:
                        stack.append(nm)
        closure[ent] = {"modules": sorted(seen), "external_imports": sorted({r["imports"] for r in rows if not r["scanned_runtime_module"]}),
                        "n_import_statements": len(rows)}
    # sys.path directories the entries use, and whether any holds a second v2_solver.py
    path_dirs = {"implementation-v2-r3 (entries' HERE)": EXP_REL + "/implementation-v2-r3", "R.V2_DIR": EXP_REL + "/implementation-v2",
                 "R.A1_DIR": EXP_REL + "/implementation-v2-a1"}
    shadow = {k: sorted(f for f in os.listdir(os.path.join(REPO, v)) if f in ("v2_solver.py", "v2_solver") or f.startswith("v2_solver."))
              for k, v in path_dirs.items()}
    for f, ln, s in (("r3e2", 27, "sys.path.insert(0, HERE)"), ("r3e2", 43, "sys.path.insert(0, R.V2_DIR)"),
                     ("r3e1", 55, "sys.path.insert(0, R.V2_DIR)"), ("r3e1", 56, "sys.path.insert(0, R.A1_DIR)"),
                     ("a1c", 25, "sys.path.insert(0, V2_DIR)"), ("a1c", 27, "sys.path.insert(0, HERE)"),
                     ("r3e1", 76, "if DR.C is not C:"), ("r3e1", 78, "if DR.D is not D:"),
                     ("r3r", 435, '_STATE.update(installed=True, original=orig, v2_solver=getattr(v2_driver_module, "V", None))'),
                     ("r3r", 340, "st = V.parse_msolve_log(text) if not missing else None"),
                     ("r3e2", 48, "RS.install(D, run_dir)"), ("r3e1", 69, "RS.install(D, run_dir)"), ("r3e1", 70, "RS.install_health(H, run_dir)")):
        cite("RLR-2 module identity and install order", f, ln, s)
    # capped launches before dispatch: module-level calls of the runtime modules that reach run_child
    pre, main_guarded = [], []
    for mn, m in mods.items():
        guard_ranges = [(n.lineno, n.end_lineno) for n in m.tree.body if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                        and isinstance(n.test.left, ast.Name) and n.test.left.id == "__name__"]
        for c in m.own_calls("<module>"):
            t = resolve(mods, mn, "<module>", c)
            if t and not t[0].startswith("ext:"):
                capped, _u = reach_paths(mods, (t[0], t[1], ""), "a1")
                if capped or t == ("v2_solver", "run_child"):
                    row = {"module": mn, "line": c.lineno, "callee": "%s.%s" % t}
                    (main_guarded if any(a <= c.lineno <= b for a, b in guard_ranges) else pre).append(row)
    # every other launch of a process that sets RLIMIT_AS
    th = tools_harness_text_scan(["setrlimit", "RLIMIT_AS", "prlimit"])
    ext_names = set()
    for ent in closure.values():
        ext_names |= set(ent["external_imports"])
    tools_harness_modules = {os.path.basename(h["file"])[:-3] for h in th["hits"] if h["file"].endswith(".py")}
    rows_nc = [c for c in captures]
    reach_rows = [s for s in sites if s["reachable_from_a_command"]]
    not_icpt = [s for s in reach_rows if not s["intercepted_by_RL1_replacement"]]
    return {"method": ("ast over every scanned tree: every run_child call with its func expression; the binding of the base name in its "
                       "module (import / assignment / argument / global); every non-call reference to run_child or _run_child_locked "
                       "(Attribute, Name or string constant); every ImportFrom of v2_solver; dynamic-import words; the entries' import "
                       "closure and sys.path; module-level calls reaching run_child"),
            "call_sites": sites, "reachable_call_sites": len(reach_rows), "reachable_call_sites_not_intercepted": not_icpt,
            "_run_child_locked_callers": scan["_run_child_locked_call_sites"],
            "non_call_references_to_run_child_anywhere": rows_nc,
            "from_v2_solver_import_statements": from_imports, "import_v2_solver_statements": imports_v2_solver,
            "dynamic_import_words": dyn, "entry_import_closure": closure,
            "entry_sys_path_directories_holding_a_v2_solver_file": shadow,
            "capped_launches_reachable_from_module_level_code": pre,
            "capped_launches_reachable_only_under_if___name___main": main_guarded,
            "note_main_guarded": "executed only when the file is run as a script; the entries import these modules, so these calls do not run",
            "other_RLIMIT_AS_setting_launches": {
                "scanned_trees": scan["setrlimit_or_prlimit_call_sites"],
                "tools_and_harness_text_hits": th,
                "tools_or_harness_module_imported_by_either_entry_closure": sorted(ext_names & tools_harness_modules)}}


# ============================================================================ RLR-3
def rlr3(mods):
    entries = command_entries(mods)
    gb = []
    for cmd, (entry, ctx) in sorted(entries.items()):
        seen, stack = set(), [entry]
        while stack:
            n = stack.pop()
            if n in seen or n[0] not in mods or n[1] not in mods[n[0]].defs:
                continue
            seen.add(n)
            for ln, t, c in edges(mods, n, ctx):
                if t[0] == "ext":
                    continue
                if n[0] != "r3_resolve" and t[:2] == ("r3_resolve", "solve"):
                    kw = {k.arg: k.value for k in c.keywords}
                    g = kw.get("gb_only")
                    if g is not None and not (isinstance(g, ast.Constant) and g.value is False):
                        gb.append({"command": cmd, "file": mods[n[0]].rel, "line": ln, "enclosing": n[1],
                                   "gb_only_expr": ast.unparse(g), "tag_expr": ast.unparse(c.args[3]) if len(c.args) > 3 else None})
                if t not in seen:
                    stack.append(t)
    # every solve() call anywhere in the runtime modules with a gb_only keyword (completeness)
    allgb = []
    for mn, m in mods.items():
        for c in ast.walk(m.tree):
            if isinstance(c, ast.Call) and any(k.arg == "gb_only" for k in c.keywords):
                allgb.append({"module": mn, "line": c.lineno, "call": ast.unparse(c.func),
                              "gb_only": ast.unparse(next(k.value for k in c.keywords if k.arg == "gb_only"))})
    # order in solve(): the two fields are assigned before every return
    fn = mods["v2_driver"].defs["solve"]
    assigns = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "res" and isinstance(t.slice, ast.Constant):
                    assigns.setdefault(t.slice.value, []).append(n.lineno)
    returns = sorted(n.lineno for n in ast.walk(fn) if isinstance(n, ast.Return))
    order_ok = max(assigns.get("solver", [10 ** 9]) + assigns.get("threads_executed", [10 ** 9])) < min(returns)
    lines = {
        "argv_-g_when_gb_only": cite("RLR-3", "v2s", 333, 'argv += ["-g", "1"] if gb_only else ["-P", "1"]'),
        "argv_built_in_solve": cite("RLR-3", "v2d", 165, "argv = V.msolve_argv(inp, out, threads=1, gb_only=gb_only)"),
        "launch": cite("RLR-3", "v2d", 166, "rec = V.run_child(argv"),
        "result_solver": cite("RLR-3", "v2d", 167, 'res["solver"] = _slim(rec)'),
        "_slim_keeps_the_pair": cite("RLR-3", "v2d", 151, '"rlimit_as_child_getrlimit"'),
        "result_threads_executed": cite("RLR-3", "v2d", 169, 'res["threads_executed"] = V.threads_from_argv(argv)'),
        "return_refused_to_start": cite("RLR-3", "v2d", 186, "return _retain(res, inp, out, retain_input)"),
        "return_gb_only": cite("RLR-3", "v2d", 189, "return _retain(res, inp, out, retain_input)"),
        "gb_only_branch": cite("RLR-3", "v2d", 187, "if gb_only:"),
        "r3_passthrough_branch": cite("RLR-3", "r3r", 382, "if gb_only:"),
        "r3_passthrough_counter": cite("RLR-3", "r3r", 383, '["passthrough_calls_gb_only_true"] += 1'),
        "r3_passthrough_calls_original": cite("RLR-3", "r3r", 384, "res = _call_original(original, args, kwargs)"),
        "r3_passthrough_returns_the_object": cite("RLR-3", "r3r", 387, "return res"),
        "sc4_minus_g_exclusion": cite("RLR-3", "r3c", 136, 'if "-g" in argv or o.get("outcome") != "ok":'),
        "sc4_s1_source_raw_solve_records": cite("RLR-3", "r3c", 134, "for o in find_solver_records(raw):"),
        "sc4_s2_source_health_reports": cite("RLR-3", "r3c", 141, "for h in health_records(rd):"),
        "s2_argv_never_gb_only": cite("RLR-3", "a1h", 144, "argv = V.msolve_argv(inp, out, threads=1)"),
        "RL-2_text_cites_the_exclusion": cite("RLR-3", "draft", 268, "every `-g` argv (r3_check_run.py 136)"),
    }
    return {"gb_only_S1_calls_reached_by_a_command": gb, "every_call_with_a_gb_only_keyword": allgb,
            "solve_assignments": assigns, "solve_returns": returns, "fields_assigned_before_every_return": order_ok,
            "lines": lines,
            "fields_returned_at_each_passthrough_call": {
                "result['solver']['rlimit_as_child_getrlimit']": ("present iff run_child's record carries it (_slim copies the key only "
                                                                  "when present, v2_driver.py 154): P-8..P-13 yes; P-1..P-4, P-6, P-7 no"),
                "result['threads_executed']": "always set (V.threads_from_argv(argv) = 1 for -t 1), before either return",
                "path": "v2_driver.solve (frozen original, captured by SE-3) -> r3_resolve.solve 382-387 returns the same object unchanged"}}


# ============================================================================ RLR-4
def rlr4():
    C = lambda f, ln, s: cite("RLR-4", f, ln, s)  # noqa: E731
    reads = [
        {"id": "X-01", "reader": "r3 wrapper R-7 (i)", "file": FILES["r3w"], "lines": [C("r3w", 176, "for g in gate_ids:"), C("r3w", 177, "r = _raw(g)"),
         C("r3w", 180, 'r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True')], "function": "r7_gate_packages (via _raw 97-104)",
         "package_kind_read": "gate packages G1..G4 (fixture, fixture, anchor-identity, controls)", "file_and_field": "raw-result.json run_status, gate_pass",
         "covered_by": "RB-4 as worded (every post-gate v2-r4 package and every v2-a1-r4 package: G1..G4 (a) status and (b) the r4 checker exits 0)"},
        {"id": "X-02", "reader": "r3 wrapper R-7 (iii)", "file": FILES["r3w"], "lines": [C("r3w", 192, "r = _raw(cid)"),
         C("r3w", 195, 'r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True'), C("r3w", 288, 'if which == "a1r3" and pk.get("controls_a1_gate_required"):')],
         "function": "r7_controls_a1_image", "package_kind_read": "the controls_a1 image", "file_and_field": "raw-result.json run_status, gate_pass",
         "covered_by": "RB-4 as worded (addendum packages 2-11 additionally require the controls_a1 image to satisfy (a) and (b))"},
        {"id": "X-03", "reader": "r3 wrapper REG-1 (R-7 (ii))", "file": FILES["r3w"], "lines": [C("r3w", 156, "cand = os.path.join(RUNS, g1)"),
         C("r3w", 160, "rep = REG.compare(ref, cand)"), C("r3w", 285, "if rid != gate_ids[0]:"), C("r3g", 175, 'p = os.path.join(candidate, "solver-events.json")')],
         "function": "reg1 -> r3_reg1.compare", "package_kind_read": "G1 (candidate) for every package after G1; RUN-GFPN-ac4487 (reference)",
         "file_and_field": ("G1: solver/*.ms, *.ms.out (+ .ms.log, .ms.err), certificates/*.json, raw-result.json (REG-1 (a)-(d)), "
                            "solver-events.json (SE-4 (e)); reference: the same sets"),
         "covered_by": ("G1: for post-gate packages RB-4 (G1's checker verdict); for G2 RL-4 through `requires` (G2 requires G1); for G3 and "
                        "G4 (whose `requires` name G2 and G3, not G1) only RL-4's clause 'every further cross-package read of an "
                        "r4-lineage package that the successor census lists'. Reference RUN-GFPN-ac4487: outside the r4 lineage, "
                        "bound by hash (NOT A BAR as the draft words it)")},
        {"id": "X-04", "reader": "r3 wrapper R-8", "file": FILES["r3w"], "lines": [C("r3w", 201, 'for req in pk.get("requires", []):'),
         C("r3w", 202, 'if not os.path.exists(os.path.join(RUNS, req, "manifest.yaml")):')], "function": "r8_requires",
         "package_kind_read": "every `requires` entry (the previous package in plan order)", "file_and_field": "existence of manifest.yaml (no field)",
         "covered_by": "RL-4 as worded ('every `requires` entry of either r4 plan (R-8, whose existence test stays)')"},
        {"id": "X-05", "reader": "r3 wrapper R-12", "file": FILES["r3w"], "lines": [C("r3w", 218, "man = _manifest(replaces)"),
         C("r3w", 221, 'elif man.get("failure_class") != "infrastructure_error":'), C("r3w", 227, '(m2.get("package") or {}).get("replaces") == replaces')],
         "function": "r12_contingency", "package_kind_read": "the replaced package; every other contingency package of the plan",
         "file_and_field": "manifest.yaml failure_class; manifest.yaml package.replaces",
         "covered_by": "NOT A BAR as the draft words it (R-12's failure_class read; DEC-20260924-650068 R-RB3-R-12 stands); R-12 unchanged (RL-4)"},
        {"id": "X-06", "reader": "r3 wrapper R-3 / R-11", "file": FILES["r3w"], "lines": [C("r3w", 273, "if os.path.exists(os.path.join(RUNS, rid)):"),
         C("r3w", 300, "existing = sorted(i for i in all_ids if os.path.exists(os.path.join(RUNS, i)))")], "function": "preflight",
         "package_kind_read": "run directories (own id; every id of the plans)", "file_and_field": "directory existence only (a count)",
         "covered_by": "not a read of a recorded result (existence and count only)"},
        {"id": "X-07", "reader": "command cells (both plans)", "file": FILES["v2d"], "lines": [C("v2d", 1070, "brec, bsrc = _load_build(ctx.plan, p, shape, arm, m)"),
         C("v2d", 995, 'rp = os.path.join(C.EXP_DIR, "runs", brid, "raw-result.json")'), C("v2d", 999, 'for r in data["polynomials"]:'),
         C("v2d", 1071, 'if brec is None or brec.get("outcome") != "ok":'), C("v2d", 1077, 'if not os.path.exists(npz) or C.sha256_file(npz) != brec["info"]["npz_sha256"]:'),
         C("v2d", 1083, 'if rs is not None and brec.get("rescaling")')], "function": "cmd_cells -> _load_build (989-1003)",
         "package_kind_read": "build (of the same plan and p; or its contingency replacement)",
         "file_and_field": ("raw-result.json polynomials[] shape, arm, m, outcome, reason, info.npz, info.npz_sha256, info.meta."
                            "support_nonzero_monomials, rescaling.beta / lam; and the cached .npz under C.CACHE_DIR (outside the package), sha256-compared"),
         "covered_by": "RL-4 as worded ('the build package a cells package loads (v2_driver._load_build)')"},
        {"id": "X-08", "reader": "command cells (both plans), m = 4", "file": FILES["v2d"], "lines": [C("v2d", 1028, "prior = _prior_cells(args.prior_run)"),
         C("v2d", 1010, 'rp = os.path.join(C.EXP_DIR, "runs", run, "raw-result.json")'), C("v2d", 1013, 'return {c["arm"]: c for c in json.load(open(rp)).get("cells", [])}'),
         C("v2d", 1123, 'st = (c.get("terminal") or {}).get("status")'), C("v2d", 1124, 'n = (c.get("metrics") or {}).get("targets_measured", 0)'),
         C("v2d", 1126, 'return ran and n == 0')], "function": "cmd_cells -> _prior_cells (1006-1013), _condition_met (1110-1127)",
         "package_kind_read": "the prior m = 5 cells package (--prior-run; or its contingency replacement)",
         "file_and_field": "raw-result.json cells[].arm, cells[].terminal.status, cells[].metrics.targets_measured",
         "covered_by": "RL-4 as worded ('the prior m = 5 package an m = 4 cells package reads (_prior_cells, _condition_met)')"},
        {"id": "X-09", "reader": "command aggregate (v2 plan)", "file": FILES["v2d"], "lines": [C("v2d", 1253, "rid = C.resolve_replacement(ctx.plan, rid0)"),
         C("v2d", 1256, 'rp = os.path.join(C.EXP_DIR, "runs", rid, "raw-result.json")'), C("v2d", 1262, 'for cl in r["cells"]:'),
         C("v2d", 1307, 'succ += cl["metrics"]["targets_with_verified_relation"]')], "function": "cmd_aggregate (1248-1326)",
         "package_kind_read": "every cells package named by --runs (18 in the r3 plan)",
         "file_and_field": ("raw-result.json kind, curve_shape, m, cells[] (arm, group, group_order, curve_shape, p, m, target_kind, terminal, "
                            "kind, metrics.ideal_degree_D, D_per_target, targets_measured, outcome_counts, decomposition_success_rate, "
                            "targets_with_verified_relation)"),
         "covered_by": "RL-4 as worded ('every package the aggregate and aggregate_a1 read')"},
        {"id": "X-10", "reader": "command aggregate-a1", "file": FILES["a1d"], "lines": [C("a1d", 286, "raw, rp = _load_raw(rid)"),
         C("a1d", 294, 'runs[rid], sources[rid] = _load_raw(rid)[0], "addendum"'), C("a1d", 295, "v2agg, v2agg_path = _load_raw(args.v2_aggregate)"),
         C("a1d", 298, "pb = phase_b_check(v2_paths)"), C("a1d", 239, 'rp = os.path.join(C.EXP_DIR, "runs", rid, "raw-result.json")')],
         "function": "cmd_aggregate_a1 (276-393) -> _load_raw (238-240), phase_b_check (257-273)",
         "package_kind_read": "every a1 cells package (--a1-runs, 6), every v2 cells package (--v2-runs, 18), the v2 aggregate (--v2-aggregate)",
         "file_and_field": ("cells: raw-result.json as X-09; v2 aggregate: raw-result.json heur_dflat, like_for_like_scoring, "
                            "matched_control_check_F4, cost_band, ladder_rows, planned_cells_without_row, metrics (reconcile_v2_aggregate "
                            "396-442); the v2 paths read are sha256-compared with AC.RECEIPT_V2_PHASE_B"),
         "covered_by": "RL-4 as worded ('every package the aggregate and aggregate_a1 read')"},
        {"id": "X-11", "reader": "v2_common.resolve_replacement / a1_driver._resolve", "file": FILES["v2cm"], "lines": [
         C("v2cm", 81, 'mp = os.path.join(EXP_DIR, "runs", pk["run_id"], "manifest.yaml")'), C("v2cm", 84, 'if (man.get("package") or {}).get("replaces") == rid:'),
         C("a1d", 248, 'mp = os.path.join(C.EXP_DIR, "runs", pk["run_id"], "manifest.yaml")'), C("a1d", 252, 'if (man.get("package") or {}).get("replaces") == rid:')],
         "function": "resolve_replacement (76-86; called at v2_driver 993, 1009, 1253, 1269); a1_driver._resolve (243-254; called at 283, 291, 321)",
         "package_kind_read": "every contingency package of the plan whose manifest exists",
         "file_and_field": "manifest.yaml run.package.replaces",
         "covered_by": ("RL-4 only through its clause 'every further cross-package read of an r4-lineage package that the successor census "
                        "lists'; the packages read are the plan's contingency ids, known from the plan at admission time")},
        {"id": "X-12", "reader": "command anchor-identity", "file": FILES["v2d"], "lines": [
         C("v2d", 642, 'a61 = json.load(open(os.path.join(C.ARCHIVED_ANCHOR_RUN, "raw-result.json")))["parameters"]'),
         C("v2d", 683, 'lp = os.path.join(C.ARCHIVED_ANCHOR_RUN, "anchor_t%d.ms.log" % i)'), C("v2d", 684, '"sha256": C.sha256_file(lp)'),
         C("v2d", 700, 'os.path.join(C.ARCHIVED_ANCHOR_RUN, "anchor_t0.ms.log")')], "function": "cmd_anchor_identity",
         "package_kind_read": "archived RUN-GFPN-61bba9 (v1; outside the r4 lineage)",
         "file_and_field": "raw-result.json parameters.a4, a6, p; anchor_t0..t4.ms.log (traces, f4_summary; sha256 recorded, 684)",
         "covered_by": "NOT A BAR as the draft words it (archived package outside the r4 lineage; binding below)"},
    ]
    outside = [
        {"reader": "frozen checker item a1_check_run.py 79-84 (a checker, not a command or the wrapper)",
         "lines": [C("a1k", 80, 'cid = plan["gate"]["addendum_blocking_package"]'), C("a1k", 83, 'if r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:')],
         "reads": "the controls_a1 image's raw-result.json run_status, gate_pass, for every package with controls_a1_gate_required"},
        {"reader": "r3_check_run.reg1_recorded_check (reads the package's OWN manifest gate.regression_REG-1)",
         "lines": [C("r3c", 327, "if rid != gate_ids[0]:"), C("r3c", 329, 'if rg.get("verdict") != "PASS":')], "reads": "own manifest only"},
    ]
    # archived-package bindings
    bind = {}
    for rid, rel_list, receipt in (("RUN-GFPN-61bba9", ["raw-result.json"] + ["anchor_t%d.ms.log" % i for i in range(5)], ARCH_REL + "/TASK-20260921-98561a/snapshot-receipt.json"),
                                   ("RUN-GFPN-ac4487", ["raw-result.json"], ARCH_REL + "/TASK-20260923-0fa03f/post-run-receipt.json")):
        rc = load_json_rel(receipt)
        ps = rc.get("path_sha256") or {}
        if isinstance(ps, list):
            ps = {x["path"]: x["sha256"] for x in ps}
        rows = []
        for f in rel_list:
            p = "%s/runs/%s/%s" % (EXP_REL, rid, f)
            got = sha_bytes(read_bytes(p))
            rows.append({"path": p, "bound": ps.get(p), "computed": got, "equal": ps.get(p) == got})
        bind[rid] = {"receipt": receipt, "receipt_commit_sha": rc.get("commit_sha"), "rows": rows}
    bind["RUN-GFPN-61bba9"]["how_the_command_uses_the_binding"] = ("cmd_anchor_identity records sha256 of each anchor log (v2_driver.py 684) "
                                                                    "and checks no receipt itself")
    return {"a_reads": reads, "a_reads_outside_the_card_scope": outside, "a_archived_package_bindings": bind}


def rlr4b():
    C = lambda f, ln, s: cite("RLR-4 (b)", f, ln, s)  # noqa: E731
    items = {
        "v2_check_run": [
            {"item": "run id reserved in the plan", "lines": [C("v2k", 43, "C.plan_package(plan, rid)")]},
            {"item": "status agreement", "lines": [C("v2k", 53, 'if man["status"] != raw.get("run_status")')]},
            {"item": "read-back list NON-EMPTY for every kind except 'aggregate', and every entry equal to the requested cap",
             "lines": [C("v2k", 65, 'if raw.get("kind") != "aggregate":'), C("v2k", 66, "if not caps:"),
                       C("v2k", 67, 'errs.append("no child RLIMIT_AS read-back recorded")'), C("v2k", 69, 'if c.get("soft") != req_cap or c.get("hard") != req_cap:')]},
            {"item": "certificates re-verify on a completed_valid run", "lines": [C("v2k", 90, 'if bad and man["status"] == "completed_valid":')]},
        ],
        "a1_check_run": [
            {"item": "controls_a1 checks (a)-(f) present, gate_pass boolean", "lines": [C("a1k", 72, 'if raw.get("kind") == "controls_a1":')]},
            {"item": "controls_a1 image completed_valid with gate_pass true for every package with controls_a1_gate_required",
             "lines": [C("a1k", 79, 'if pk.get("controls_a1_gate_required"):')]},
            {"item": "applies v2_check_run unchanged", "lines": [C("a1k", 133, "v2_rc = V2CHK.main(rd)")]},
        ],
        "r3_check_run": [
            {"item": "frozen checker exit status", "lines": [C("r3c", 400, "return 1 if (errs or pr.returncode) else 0")]},
            {"item": "consistency flag of solver-events.json", "lines": [C("r3c", 174, 'if doc.get("consistency_violation"):')]},
            {"item": "REG-1 recorded PASS from G2 on", "lines": [C("r3c", 329, 'if rg.get("verdict") != "PASS":')]},
            {"item": "status agreement", "lines": [C("r3c", 341, 'if man.get("status") != raw.get("run_status")')]},
            {"item": "SC-4 accounting does not change the exit status", "lines": [C("r3c", 396, "not a check failure")]},
        ]}
    kinds = [
        {"kind": "cells, m = 5 (read by the m = 4 package of the same shape: X-08; by the aggregates: X-09, X-10; by the next package: X-04)",
         "outcomes_acted_on": [
             {"outcome": "a cell recorded not_measured with its targets' children created (timeout, memory_exhausted, crash, "
                         "non-generic outcomes): the draft's example",
              "dependent_logic": [C("v2d", 1125, 'ran = st in ("not_measured", "measured")'), C("v2d", 1235, 'cell["terminal"] = {"status": "measured" if measured else "not_measured"')],
              "package_record": [C("v2d", 1101, 'raw["run_status"] = "invalid" if (certs and not all_ok)'), C("v2d", 1102, 'else "resource_exhaustion"')],
              "checker_item_exits_nonzero_by_design": False,
              "why": ("run_status 'failed' / resource_exhaustion when no cell measured (1101-1102) agrees with the manifest (v2_check_run 53); "
                      "the created children carry pairs (P-8..P-13) collected from raw-result.json (cells[].targets[].solver) and, under RL-3, "
                      "from launch records, so the list is non-empty and equal to the cap; no other item reads a cell outcome")},
             {"outcome": ("a package in which NO capped child is created because every runnable cell is not_attempted with 'polynomial "
                          "unavailable' (the build row for (shape, arm, 5) not ok: v2_driver 1071-1075) and every other cell is refused "
                          "or not_attempted by design (raw not_attempted; torsion_S5_norm conditional on S5 measured). For "
                          "random_no2torsion only S5 is runnable (rq and S_rescaled refused by rescaling 'no rational 2-torsion', "
                          "norm refused at 1052-1058), so one failed build row suffices"),
              "dependent_logic": [C("v2d", 1073, 'cell["terminal"] = {"status": "not_attempted", "reason": "polynomial unavailable: %s" % why}'),
                                  C("v2d", 1122, 'return False, "no m = 5 cell for %s in the prior package" % arm'),
                                  C("v2d", 1126, "return ran and n == 0")],
              "package_record": [C("v2d", 1101, 'all(cl["terminal"]["status"] in ("refused", "not_attempted") for cl in cells) else "failed")')],
              "checker_item_exits_nonzero_by_design": True,
              "item": "v2_check_run.py 65-67 'no child RLIMIT_AS read-back recorded' (kind 'cells' is not exempt; zero launches give an empty list under RB-2 and RL-3 alike)",
              "why": ("run_status completed_valid (all cells refused / not_attempted, 1101); the m = 4 package's _condition_met acts on the S5 "
                      "cell's terminal not_attempted (condition not met, 1125-1126); the aggregates act on the rows; under RL-4 the frozen "
                      "checker's exit 1 on this package refuses the dependent package")},
             {"outcome": ("every target of every runnable cell refused_to_start before fork (P-1..P-4): recorded not_measured with class "
                          "infrastructure_error per target (1184-1188, 1235)"),
              "dependent_logic": [C("v2d", 1125, 'ran = st in ("not_measured", "measured")')],
              "package_record": [C("v2d", 1187, '"refused_to_start": "infrastructure_error"')],
              "checker_item_exits_nonzero_by_design": True,
              "item": "v2_check_run.py 65-67 (no child created, so no pair in any source)",
              "why": "the m = 4 package acts on not_measured (condition met); the checker fails the m = 5 package; under RL-4 the m = 4 package is refused"}]},
        {"kind": "cells, m = 4 (read by the aggregates X-09 / X-10 and by the next package X-04)",
         "outcomes_acted_on": [
             {"outcome": "cells measured / not_measured / not_attempted (condition not met) / refused, with the unconditional raw cell creating children",
              "checker_item_exits_nonzero_by_design": False,
              "why": "the raw cell is unconditional ('run', no condition) and creates raw_grid children (I-20) and solves (I-21), whose pairs RL-1 records on every created-child branch"},
             {"outcome": "every capped launch of the package refused before fork (P-1..P-4)", "checker_item_exits_nonzero_by_design": True,
              "item": "v2_check_run.py 65-67", "why": "no pair exists in any source"}]},
        {"kind": "build (read by cells X-07; by the first m = 5 package X-04)",
         "outcomes_acted_on": [
             {"outcome": "rows ok / refused / failed (timeout, memory_exhausted ...): run_status failed, class resource_exhaustion or infrastructure_error",
              "dependent_logic": [C("v2d", 1071, 'if brec is None or brec.get("outcome") != "ok":')],
              "package_record": [C("v2d", 976, 'raw = {"kind": "build", "p": p, "run_status": "completed_valid" if ok else "failed"')],
              "checker_item_exits_nonzero_by_design": False,
              "why": "every created builder child's pair is kept in polynomials[].info.child on every branch (I-19) and recorded by RL-1"},
             {"outcome": "every builder launch refused before fork", "checker_item_exits_nonzero_by_design": True, "item": "v2_check_run.py 65-67",
              "why": "no pair exists in any source"}]},
        {"kind": "fixture4 F-4 (read by build 4111 through `requires`, X-04)",
         "outcomes_acted_on": [
             {"outcome": "any F-4 outcome: the frozen plan's gate rule says 'package 5 runs after the gate and is NOT blocking'; build does not read F-4's content",
              "checker_item_exits_nonzero_by_design": "only on the items above (e.g. no pair recorded)",
              "why": ("RL-4 makes build's admission depend on F-4's r4 checker exit status through `requires` (build 4111 requires F-4), so "
                      "an F-4 whose checker exits non-zero stops the chain although the frozen plan calls F-4 not blocking")}]},
        {"kind": "gate packages G1..G4 (X-01, X-03, X-04)",
         "outcomes_acted_on": [{"outcome": "completed_valid with gate_pass true (admit) / anything else (refuse)", "checker_item_exits_nonzero_by_design": False,
                                "why": "a failed gate stops the lineage by design (RB-4); no dependent package proceeds on a failed gate"}]},
        {"kind": "controls_a1 image (X-02; a1_check_run 79-84)",
         "outcomes_acted_on": [{"outcome": "completed_valid with gate_pass true (admit) / anything else (refuse)", "checker_item_exits_nonzero_by_design": False,
                                "why": "a failed controls_a1 ends the addendum at its gate by design"}]},
        {"kind": "aggregate (v2) read by aggregate-a1 (X-10)",
         "outcomes_acted_on": [{"outcome": "the v2 aggregate's figures", "checker_item_exits_nonzero_by_design": False,
                                "why": "kind 'aggregate' is exempt from the read-back test (v2_check_run 65); run_status is always completed_valid (v2_driver 1314)",
                                "lines": [C("v2d", 1314, 'raw = {"kind": "aggregate", "run_status": "completed_valid"'),
                                          C("a1d", 374, 'raw = {"kind": "aggregate", "aggregate_variant": "aggregate_a1"')]}]},
        {"kind": "contingency packages (X-11)",
         "outcomes_acted_on": [{"outcome": "manifest package.replaces names the replaced id (resolve_replacement redirects the read)",
                                "checker_item_exits_nonzero_by_design": "as the kind it replaces"}]},
    ]
    chains = {}
    for key, rel in (("v2-r3", EXP_REL + "/trial-plan-v2-r3.json"), ("v2-a1-r3", EXP_REL + "/trial-plan-v2-a1-r3.json")):
        P = load_json_rel(rel)
        chains[key] = {"packages": [{"order": pk.get("order"), "run_id": pk["run_id"], "kind": pk["kind"], "p": pk.get("p"), "shape": pk.get("shape"),
                                     "m": pk.get("m"), "requires": pk.get("requires"), "gate_required": pk.get("gate_required"),
                                     "controls_a1_gate_required": pk.get("controls_a1_gate_required")} for pk in P["packages"]],
                       "gate_F-4_rule": (P.get("gate") or {}).get("F-4")}
    return {"plan_requires_chains": chains, "checker_items_read": items, "per_package_kind": kinds,
            "r4_checks_as_specified": ("RB-3 SC-4 accounting does not change the exit status (readbackcover RB-3); RL-3 accounting 'gating nothing "
                                       "by itself'; RL-5 consistency tests fail only on a recording failure; none reads a cell or build outcome")}


# ============================================================================ RLR-7
def rlr7():
    C = lambda f, ln, s: cite("RLR-7", f, ln, s)  # noqa: E731
    ladder = load_json_rel(EXP_REL + "/implementation/ladder.json")
    a1r3 = load_json_rel(EXP_REL + "/trial-plan-v2-a1-r3.json")
    a1f = load_json_rel(EXP_REL + "/trial-plan-v2-a1.json")
    v2f = load_json_rel(EXP_REL + "/trial-plan-v2.json")
    ca = next(p for p in a1r3["packages"] if p["kind"] == "controls_a1")
    caf = next(p for p in a1f["packages"] if p["kind"] == "controls_a1")
    wd = a1r3["watchdogs"]
    reads = [
        {"input": "the plan package of the run id (Ctx) and its p == --p", "lines": [C("v2d", 58, "self.pkg = C.plan_package(self.plan, self.rid)"),
         C("a1d", 51, 'if int(ctx.pkg.get("p") or -1) != int(p):'), C("a1d", 449, 'a.add_argument("--p", type=int, required=True)')],
         "supplied_by": "the plan (the package whose run_id is the basename of GFPN_RUN_DIR)"},
        {"input": "the ladder entry", "lines": [C("a1d", 68, "rung = C.ladder_entry(p)"), C("v2cm", 35, 'LADDER_PATH = os.path.join(EXP_DIR, "implementation", "ladder.json")'),
         C("a1d", 30, "C = AC.redirect_v2()"), C("a1c", 95, "if ladder_path:")],
         "supplied_by": "v1 implementation/ladder.json (v2_common.LADDER_PATH; redirect_v2() called without ladder_path leaves it), not the plan"},
        {"input": "rescaling_parameters.per_shape (check (c))", "lines": [C("a1d", 114, 'planned = (ctx.plan.get("rescaling_parameters") or {}).get("per_shape", {})'),
         C("a1d", 120, 'same = (not rs["refused"]) and planned.get(s, {}).get("beta") == rs["beta"]')], "supplied_by": "the plan"},
        {"input": "watchdogs: builder_timeout_s.m3 (check (e) builds); per_arm_m '<arm>|m3' per_target_timeout_s (check (e) solves)",
         "lines": [C("a1d", 146, 'ctx.plan["watchdogs"]["builder_timeout_s"]["m3"]'), C("a1d", 166, 'C.watchdog(ctx.plan, arm, 3)["per_target_timeout_s"]')],
         "supplied_by": "the plan (R-9: the plan's watchdogs must equal trial-plan-v2.json's)", "r9": C("r3w", 292, 'if plan is not None and plan.get("watchdogs") != P["v2"].get("watchdogs"):')},
        {"input": "gp (/usr/bin/gp), capped, PARI_TIMEOUT_S 7200; plus an uncapped `gp --version-short` (timeout 30)",
         "lines": [C("a1p", 27, 'GP = "/usr/bin/gp"'), C("a1p", 28, "PARI_TIMEOUT_S = 7200"), C("a1p", 121, "return subprocess.run([GP, \"--version-short\"]")],
         "supplied_by": "the host binary and module constants (not the plan)"},
        {"input": "the health check: PATTERNS (2,2,2), (4,4,4), EXPECTED, DEV_TIMEOUT_S 1800, seed AC.HEALTH_SEED, retry ':2' when the first fails, no reinvocation",
         "lines": [C("a1h", 51, "PATTERNS = [(2, 2, 2), (4, 4, 4)]"), C("a1h", 53, "DEV_TIMEOUT_S = 1800"), C("a1h", 223, "def run(p, out_dir, seed=AC.HEALTH_SEED, cap=AC.CAP_BYTES, reinvoke_on_fail=False):"),
                   C("a1d", 129, 'hr = H.run(p, os.path.join(ctx.rd, "health"), cap=ctx.cap)')],
         "supplied_by": "module constants (not the plan)"},
        {"input": "the cap", "lines": [C("v2d", 43, 'CAP = int(os.environ.get("GFPN_V2_CAP_BYTES", str(V.CAP_BYTES_DEFAULT)))'), C("v2d", 65, "self.cap = CAP")],
         "supplied_by": "v2_driver.CAP (environment GFPN_V2_CAP_BYTES, default 10737418240), not the plan"},
    ]
    frozen_derivation = {
        "rb6_a_text": C("cover", 315, "Plans are derived from the FROZEN plans, as r3's were."),
        "rb5_development_world": C("cover", 287, "directory outside experiments/EXP-GFPN-05ff43/runs/, no reserved"),
        "r3_plan_vs_frozen_a1_plan_controls_a1": {"frozen_p": caf.get("p"), "r3_p": ca.get("p"),
                                                  "frozen_driver_args": caf.get("driver_args"), "r3_driver_args": ca.get("driver_args"),
                                                  "rescaling_parameters_equal": a1f.get("rescaling_parameters") == a1r3.get("rescaling_parameters"),
                                                  "watchdogs_equal": a1f.get("watchdogs") == a1r3.get("watchdogs"),
                                                  "watchdogs_equal_trial_plan_v2": a1r3.get("watchdogs") == v2f.get("watchdogs")},
        "rescaling_parameters_p": (a1r3.get("rescaling_parameters") or {}).get("p"),
        "r3_dv7_precedent": {"lines": [C("r3d7", 47, "TOY_A1_P, TOY_FX3, TOY_FX4_P = 1021, (1033, 1039), 1033"),
                                       C("r3d7", 160, 'ba[1].update(driver_args=["controls-a1", "--p", str(TOY_A1_P)], p=TOY_A1_P)'),
                                       C("r3d7", 174, "C.LADDER_PATH = ladder_path"), C("r3d7", 11, "NO ladder or fixture prime is solved")],
                             "what": ("the r3 layer's development check DV-7 ran controls-a1 through the r3 a1 entry at the toy prime 1021 on "
                                      "toy copies of both r3 plans (package p and driver_args changed, toy-only watchdog keys added to the "
                                      "plans AND to the toy copy of trial-plan-v2.json so that R-9 held), with v2_common.LADDER_PATH and "
                                      "EXP_DIR redirected in process to a toy ladder; it solved at no ladder or fixture prime (R3S-9)")}}
    rows = []
    for r in ladder:
        p = r["p"]
        cv = r["curves"]
        facts = {s: {"order_mod_4": int(c["order"]) % 4, "cofactor": int(c["cofactor"]), "b_is_square_in_Fq": c.get("b_is_square_in_Fq"),
                     "has_rational_2torsion": c.get("has_rational_2torsion")} for s, c in cv.items()}
        e, t2, no = facts["ecgfp5_shaped"], facts["random_2torsion"], facts["random_no2torsion"]
        b_facts = (e["order_mod_4"] == 2 and e["cofactor"] == 2 and e["b_is_square_in_Fq"] is False and t2["order_mod_4"] == 2
                   and t2["cofactor"] == 2 and t2["b_is_square_in_Fq"] is False and no["has_rational_2torsion"] is False)
        same = p == ca.get("p") == (a1r3.get("rescaling_parameters") or {}).get("p")
        rows.append({"p": p, "role": r.get("role"), "ladder_facts": facts,
                     "ladder_records_the_check_b_facts": b_facts,
                     "ecgfp5_shaped_rescaling_refused_by_ladder_fact_b_square": e["b_is_square_in_Fq"] is True,
                     "plan_values_supplied_by_a_derivation_of_the_frozen_plan_without_a_value_change": same,
                     "needs_changed_plan_values": [] if same else ["controls_a1 package p and driver_args set to %d" % p,
                                                                   "rescaling_parameters recomputed at %d (else check (c) records equals_plan false)" % p],
                     "ladder_entry_present": True, "gp_and_health_and_cap": "module constants / host binary; the same at every prime"})
    watch = {"package_watchdogs_field": ca.get("watchdogs"), "builder_timeout_s_m3": wd["builder_timeout_s"]["m3"],
             "per_target_timeout_s": {k: wd["per_arm_m"][k]["per_target_timeout_s"] for k in ("torsion_S3_rq|m3", "S3_rescaled|m3")},
             "module_constants_not_plan": {"a1_health.DEV_TIMEOUT_S": 1800, "a1_pari.PARI_TIMEOUT_S": 7200},
             "capped_children": {"builders": 2, "S-1 solves": 2, "S-2 health systems": "2 first + up to 2 retry_seed2 (reinvocations not executed)", "gp": 1},
             "MODELED_sum_of_declared_single_attempt_timeouts_seconds": 2 * wd["builder_timeout_s"]["m3"] + 2 * 1800 + 4 * 1800 + 7200,
             "modeled_label": ("MODELED arithmetic of declared timeouts, not a measurement: 2 x 1800 (builders) + 2 x 1800 (S-1) + 4 x 1800 "
                               "(S-2) + 7200 (gp); the r3 bounded re-solve rule may add attempts 2..k at S-1 / S-2 until their summed wall "
                               "seconds reach the call's timeout (r3_resolve.py 241-244, 301-309); in-process work (checks (a), (c), (e) "
                               "point sampling, lifting) and the uncapped host scans are bounded by no watchdog"),
             "cg": C("r3r", 244, "return (timeout is not None and spent >= timeout), spent")}
    fr = [x["p"] for x in rows if x["plan_values_supplied_by_a_derivation_of_the_frozen_plan_without_a_value_change"]]
    return {"reads": reads, "frozen_derivation": frozen_derivation, "per_ladder_prime": rows, "frozen_plan_watchdogs": watch,
            "ladder_primes": [x["p"] for x in rows],
            "smallest_prime_supplied_without_changing_a_frozen_plan_value": min(fr) if fr else None,
            "smallest_ladder_prime_if_the_derived_plan_sets_p_and_rescaling_parameters": min(x["p"] for x in rows)}


# ============================================================================ RLR-6
def rlr6():
    words = ["solver-events", "solver_events", "EVENTS_FILE"]
    occ = []
    for rel in scanned_py_files():
        for i, line in enumerate(text_lines(rel), 1):
            if any(w in line for w in words):
                occ.append({"file": rel, "line": i})
    th = tools_harness_text_scan(words)
    C = lambda f, ln, s: cite("RLR-6", f, ln, s)  # noqa: E731
    readers = [
        {"reader": "r3_resolve (the layer's writer)", "lines": [C("r3r", 154, "atomic rewrite of the run-root solver-events.json"), C("r3r", 167, "os.replace(tmp, path)")],
         "reads": "never reads the file: it rewrites its in-memory document _STATE['doc']", "new_top_level_key_changes_what_it_computes": "n/a (writer)"},
        {"reader": "r3_run_wrapper.solver_events_block", "lines": [C("r3w", 391, 'sites = doc.get("sites") or {}'), C("r3w", 395, '"sha256": R.sha256_file(p)')],
         "reads": "top-level sites, K, spacing_s, cap_rule, consistency_violation by constant key; S-1 / S-2 counters and events; S-3 counters; whole-file sha256",
         "new_top_level_key_changes_what_it_computes": "no, except the recorded whole-file sha256 (the bytes change)"},
        {"reader": "r3_run_wrapper.consistency_flag", "lines": [C("r3w", 577, 'return bool(json.load(open(os.path.join(rd, RS.EVENTS_FILE))).get("consistency_violation"))')],
         "reads": "top-level consistency_violation", "new_top_level_key_changes_what_it_computes": "no"},
        {"reader": "r3_check_run.events_file_integrity (VA-6 (a))", "lines": [C("r3c", 157, 'if os.path.exists(sp) and sev.get("sha256") != R.sha256_file(sp):')],
         "reads": "whole-file sha256 against the manifest's recorded sha256", "new_top_level_key_changes_what_it_computes": "no (both sides are the same bytes)"},
        {"reader": "r3_check_run.events_file_epsilon (VA-6 (b))", "lines": [C("r3c", 174, 'if doc.get("consistency_violation"):'), C("r3c", 179, 'c = ((doc.get("sites") or {}).get(site) or {}).get("counters") or {}')],
         "reads": "exists / parses; consistency_violation; K, spacing_s; S-1 / S-2 counters by constant key", "new_top_level_key_changes_what_it_computes": "no"},
        {"reader": "r3_check_run.forbidden_id_keys (VA-7 (b))", "lines": [C("r3c", 195, 'for f in ("manifest.yaml", "raw-result.json", "pari-stack.json", "solver-events.json"):'),
                                                                       C("r3c", 209, "v = d.get(k)")],
         "reads": "top-level keys task_id, run_card, written_by_task, archived_by only", "new_top_level_key_changes_what_it_computes": "no (launch_records / passthrough_records are not among the tested keys)"},
        {"reader": "r3_reg1.solver_events_check and compare (REG-1 SE-4 (e))", "lines": [C("r3g", 175, 'p = os.path.join(candidate, "solver-events.json")'),
                                                                                       C("r3g", 194, 'viol = bool(doc.get("consistency_violation")) or bool(ev_bad)'),
                                                                                       C("r3g", 282, 'rep["solver_events_json_verbatim"] = se_txt')],
         "reads": "candidate only: exists / parses; consistency_violation; S-1 / S-2 events' consistency.ok; counters copied; the file quoted verbatim",
         "new_top_level_key_changes_what_it_computes": "no for the verdict; the verbatim quote grows (report only); a recording failure is one more cause of the flag (RL-7)"},
        {"reader": "a1_check_run addendum_checks forbidden-id byte sweep", "lines": [C("a1k", 51, "for root, _dirs, files in os.walk(rd):"),
                                                                                   C("a1k", 53, 'if f.endswith((".json", ".yaml", ".txt", ".log")):')],
         "reads": "the bytes of every .json file of the package, solver-events.json included, for a1_common.FORBIDDEN_TASK_ID",
         "new_top_level_key_changes_what_it_computes": ("no unless a launch or pass-through record's copied strings (argv, tag, calling frame "
                                                        "file) contain that id; the added bytes are scanned")},
        {"reader": "frozen commands, v2_check_run, the aggregates, a1 phase_b_check", "lines": [C("a1d", 298, "pb = phase_b_check(v2_paths)")],
         "reads": ("none: no file of implementation-v2/ or implementation-v2-a1/ names solver-events.json (text scan); phase_b_check hashes "
                   "only the raw-result.json paths the aggregate read"), "new_top_level_key_changes_what_it_computes": "n/a"},
        {"reader": "repository tools under tools/ and harness/", "lines": [],
         "reads": "none (text scan of every file: no occurrence)", "new_top_level_key_changes_what_it_computes": "n/a"},
    ]
    return {"occurrences_in_scanned_trees": occ, "occurrence_files": sorted({o["file"] for o in occ}),
            "tools_and_harness_scan": th, "readers": readers,
            "development_only_readers_note": ("r3_devchecks_more, r3_dv6, r3_dv7, r3_dv12, r3_dv16, r3_inventory (development checks, never invoked by an "
                                              "entry, the wrapper or the checker) and the retired r2 layer (implementation-v2-r2/) also name the file")}


# ============================================================================ method limits
def method_limits():
    return {
        "carried": {
            "L-1": ("a frozen function that raises after its child ran returns no result: under RL-1 the launch record is appended before "
                    "run_child's return reaches the caller, so for a raise in the CALLER (e.g. v2_driver.solve after 166) RL-1 still has the "
                    "pair; a raise INSIDE run_child after fork (P-14, P-15) returns no record: see L-6"),
            "L-2": "the ERR setrlimit branch (P-6) takes no pair; RL-1 records 'absent'; still applies",
            "L-3": "which branch occurs is a run-time fact; the branches here are static; still applies",
            "L-4": "grandchildren (inside msolve, valgrind, Sage or gp) were not examined; still applies",
            "L-5": ("controls-a1, fixture4, build, cells and aggregate(-a1) have never run under r3; their dispositions are static only; "
                    "still applies, and no r4 code exists: RL-1..RL-3 are read as worded, not as implemented")},
        "new": {
            "L-6": ("RL-1 (c) derives every recorded field from the RETURNED record; on a raise inside run_child after fork (P-14 "
                    "BrokenPipeError at 236 when the child exited before the go byte; P-15 _perf_read) there is no returned record, so "
                    "RL-1 as worded records child_created false and pair 'absent' for a created child"),
            "L-7": ("P-7 (child fails before setrlimit, empty report) is a created-child branch with no pair that is not literally 'the ERR "
                    "setrlimit branch' the draft names NOT A BAR; whether RL-1 (c)'s 'carries child_rlimit_report' is a key-presence test "
                    "(the value is the empty string) is not stated"),
            "L-8": ("RLR-2 is read on the r3 entries and the modules they import; the r4 entries do not exist. A module added by the r4 layer, "
                    "or a file named v2_solver.py placed on the r4 entries' sys.path, is outside this reading"),
            "L-9": ("RLR-7 states what the command reads and where a plan supplies it; whether a derived plan may change the controls_a1 "
                    "package's p and rescaling_parameters, and the wrapper-level admission of a development controls-a1 package (R-7 gate "
                    "packages, REG-1, R-9), are not decided here"),
            "L-10": "RLR-4 (b) is a static reading of the checkers and drivers; no package was run to confirm any checker exit status"}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    OUT["inference"] = {"requested_policy": "executor-implementation", "resolved_model_id": None,
                        "resolved_model_note": "none supplied by the dispatching session; none invented", "fallback_used": False,
                        "bedrock_used": False, "note": "Amazon Bedrock is prohibited. Network access was not used."}
    OUT["phase_1_integrity"] = integrity()
    if not OUT["phase_1_integrity"]["all_ok"]:
        OUT["stopped"] = "RFQ-2 integrity failure: no reading was made"
        write_out(a.out)
        print("STOP: integrity failure")
        return 3
    OUT["dp5_recheck"] = dp5_recheck()
    install_guard()
    OUT["guard"] = GUARD
    mods = load_runtime()
    OUT["runtime_modules"] = {n: m.rel for n, m in sorted(mods.items())}
    # bound-by check of every implementation / plan file read
    union = {}
    for rel in (ARCH_REL + "/TASK-20260923-0fa03f/snapshot-receipt.json", ARCH_REL + "/TASK-20260923-4ff597/snapshot-receipt.json",
                ARCH_REL + "/TASK-20260924-f1fb0e/snapshot-receipt.json"):
        for p, h in load_json_rel(rel, record=False)["path_sha256"].items():
            union[p] = (h, rel)
    scan = launch_scan()
    OUT["launch_scan"] = scan
    OUT["RLR-2"] = rlr2(mods, scan)
    OUT["RLR-1"] = {"a_run_child_paths": rlr1_run_child_paths(), "b_instances": rlr1_instances(mods)}
    OUT["RLR-3"] = rlr3(mods)
    OUT["RLR-4"] = {"a": rlr4(), "b": rlr4b()}
    OUT["RLR-7"] = rlr7()
    OUT["RLR-6"] = rlr6()
    OUT["method_limits"] = method_limits()
    res = [dict(c, ok=citation_check(c)) for c in CITES]
    OUT["citation_checks"] = {"n": len(res), "failures": [c for c in res if not c["ok"]],
                              "by_reading": {k: sum(1 for c in res if c["reading"].split(" ")[0] == k)
                                             for k in sorted({c["reading"].split(" ")[0] for c in res})}}
    impl_reads = {p: h for p, h in OUT["files_read_sha256"].items() if p.startswith(EXP_REL + "/implementation-v2") or
                  (p.startswith(EXP_REL + "/trial-plan-") and p.endswith(".json"))}
    OUT["implementation_and_plan_files_read_vs_receipts"] = {
        "n_read": len(impl_reads),
        "bound_and_equal": sorted(p for p, h in impl_reads.items() if p in union and union[p][0] == h),
        "bound_and_differing": sorted(p for p, h in impl_reads.items() if p in union and union[p][0] != h),
        "not_bound_by_0fa03f_4ff597_or_f1fb0e_phase_A": sorted(p for p in impl_reads if p not in union),
        "note": ("files not bound by those three receipts are covered by RFQ-2 (g) (no change since dd1034553) and, for the r3 development "
                 "files, by the TASK-20260924-f1fb0e phase-B (post-run) receipt where bound")}
    OUT["guard"] = GUARD
    OUT["wall_seconds"] = round(time.time() - t0, 3)
    write_out(a.out)
    print("done: guard launch attempts %d, import attempts %d; citations %d, failures %d" %
          (GUARD["launch_attempts"], GUARD["import_attempts"], OUT["citation_checks"]["n"], len(OUT["citation_checks"]["failures"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
