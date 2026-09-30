#!/usr/bin/env python3
"""TASK-20260924-159c1b -- ZERO-RUN, ZERO-SOLVE callgrind-site PREMISE CHECK of the DRAFT
AMD-EXP-GFPN-05ff43-20260924-launchcover (pre_approval_readings LP-5, LP-1, LP-2 (i)-(vii), LP-3, LP-4).

usage: python3 -B lp_check.py --scratch DIR [--out DIR]

Order (LQ-2, LQ-1):
  1. INTEGRITY (LP-5) first. The only child processes this script starts are read-only git children in this phase
     (listed with argv). Any integrity failure writes premise-check.json / premise-check.md with the failure and
     stops before any reading.
  2. An in-process guard then replaces os.fork / os.posix_spawn / os.exec* / os.spawn* / os.system / os.popen /
     subprocess.Popen by functions that raise and record the attempt. No child can start after this point.
  3. LP-1, LP-2 (i)-(vii), LP-3, LP-4 are computed STATICALLY (ast + text search over source; reads of archived bytes).
     The one frozen import is v2_solver (for parse_msolve_log), after an ast pre-check of its module-level
     statements, with tempfile.tempdir pinned to a scratch directory so that the module-level
     tempfile.gettempdir() call probes nothing.
  4. Closing: every bound file re-hashed; no byte code under any tree; children of this process from /proc.
Observations only. Decides nothing. No solver, valgrind, callgrind_annotate, gp or Sage child.
"""
import ast
import datetime
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tokenize

sys.dont_write_bytecode = True

REPO = "/home/user/crypto-autoresearcher"
EXP = "experiments/EXP-GFPN-05ff43"
TASK = "TASK-20260924-159c1b"
SCRATCH_TMP = sys.argv[sys.argv.index("--scratch") + 1] if "--scratch" in sys.argv else None
SCRATCH_LABEL = "<executor scratchpad>/lp159c1b/tmp (given by --scratch; outside the repository; the path itself is not recorded)"
OUT_DIR = os.path.join(REPO, EXP, "dev-evidence", "launchcover-premise")
if "--out" in sys.argv:
    OUT_DIR = sys.argv[sys.argv.index("--out") + 1]

ARCH = "coordination/goals/GOAL-GFPN-380702/archives"
RC_B2B = ARCH + "/TASK-20260924-b2b59a/snapshot-receipt.json"
RC_C65 = ARCH + "/TASK-20260924-c65bfb/snapshot-receipt.json"
RC_0FA_A = ARCH + "/TASK-20260923-0fa03f/snapshot-receipt.json"
RC_0FA_POST = ARCH + "/TASK-20260923-0fa03f/post-run-receipt.json"
RC_4FF = ARCH + "/TASK-20260923-4ff597/snapshot-receipt.json"
RC_53A = ARCH + "/TASK-20260923-53a47d/preservation-receipt.json"
RC_5CA = ARCH + "/TASK-20260924-5ca2a5/preservation-receipt.json"

LAUNCHCOVER = EXP + "/amendments/v2_addendum_launchcover.yaml"
HEALTH = EXP + "/amendments/v2_addendum_healthresolve.yaml"
SEED = EXP + "/amendments/v2_addendum_seedresolve.yaml"
SOLVEREVENT = EXP + "/amendments/v2_addendum_solverevent.yaml"
CARD_HASHES = {HEALTH: "ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d",
               SEED: "dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81",
               SOLVEREVENT: "011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f"}
CENSUS_DIR = EXP + "/dev-evidence/launch-census"
CENSUS_FILES = [CENSUS_DIR + "/census.md", CENSUS_DIR + "/census.json", CENSUS_DIR + "/census_scan.py"]
CENSUS_CARD_FRAGMENTS = {CENSUS_DIR + "/census.md": ("671a5763", "63db0"), CENSUS_DIR + "/census.json": ("df8b5ac3", "32f6e"),
                         CENSUS_DIR + "/census_scan.py": ("32b9ab59", "fcbce76")}
V2, A1, R1, R2 = (EXP + "/implementation-v2", EXP + "/implementation-v2-a1", EXP + "/implementation-v2-r1", EXP + "/implementation-v2-r2")
TREES = {"v2": V2, "a1": A1, "r1": R1, "r2": R2}
TREE_RECEIPT = {"v2": RC_0FA_A, "a1": RC_4FF, "r1": RC_53A, "r2": RC_5CA}
PLAN_V2 = EXP + "/trial-plan-v2.json"
PLAN_V2_R2, PLAN_A1_R2 = EXP + "/trial-plan-v2-r2.json", EXP + "/trial-plan-v2-a1-r2.json"
EXCL_R2 = R2 + "/reg1-exclusion-list.json"
REF = EXP + "/runs/RUN-GFPN-ac4487"
INFO_FILES = ["ledger/handoffs/TASK-20260924-159c1b.yaml", "ledger/decisions/DEC-20260924-afdc3b.yaml",
              "ledger/corrections/CORR-20260924-432f43.yaml"]

OUT = {"schema": "crypto.autoresearch.gfpn05.launchcover_premise_check.v1", "task_id": TASK, "experiment_id": "EXP-GFPN-05ff43",
       "draft_defining_the_readings": "AMD-EXP-GFPN-05ff43-20260924-launchcover (DRAFT, not approved), pre_approval_readings",
       "ordered_by": "DEC-20260924-afdc3b", "archived_by": "TASK-20260924-0957c2",
       "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "children_started": [], "files_read": {}}
HASHES = {}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ab(rel):
    return os.path.join(REPO, rel)


def sha(rel):
    h = hashlib.sha256(open(ab(rel), "rb").read()).hexdigest()
    HASHES[rel] = h
    return h


def git(*args):
    argv = ["git", "-C", REPO] + list(args)
    OUT["children_started"].append({"argv": argv, "phase": "integrity", "at": now()})
    return subprocess.run(argv, capture_output=True, text=True, timeout=60).stdout


def write_outputs(stop=None):
    os.makedirs(OUT_DIR, exist_ok=True)
    OUT["stop"] = stop
    OUT["finished_at"] = now()
    txt = json.dumps(OUT, indent=1, default=str, sort_keys=False)
    open(os.path.join(OUT_DIR, "premise-check.json"), "w").write(txt + "\n")
    open(os.path.join(OUT_DIR, "premise-check.md"), "w").write(render_md())


# ===================================================================================================== 1. INTEGRITY
def load_receipt(rel):
    return json.load(open(ab(rel)))


def integrity():
    checks = []

    def chk(name, rel, expected, source):
        actual = sha(rel) if os.path.exists(ab(rel)) else None
        checks.append({"check": name, "path": rel, "expected_sha256": expected, "actual_sha256": actual,
                       "expected_from": source, "equal": actual is not None and actual == expected})

    OUT["git_at_start"] = {"head": git("rev-parse", "HEAD").strip(),
                           "status_porcelain": git("status", "--porcelain", "--untracked-files=all").splitlines()}
    for rc in (RC_B2B, RC_C65, RC_0FA_A, RC_0FA_POST, RC_4FF, RC_53A, RC_5CA):
        OUT.setdefault("receipts_used", {})[rc] = sha(rc)
    b2b = load_receipt(RC_B2B)
    chk("(a) launchcover draft == TASK-20260924-b2b59a addendum_sha256", LAUNCHCOVER, b2b["addendum_sha256"]["sha256"],
        RC_B2B + " addendum_sha256.sha256")
    if LAUNCHCOVER in b2b.get("path_sha256", {}):
        chk("(a') launchcover draft == TASK-20260924-b2b59a path_sha256", LAUNCHCOVER, b2b["path_sha256"][LAUNCHCOVER], RC_B2B + " path_sha256")
    for rel, h in CARD_HASHES.items():
        chk("(b) %s == card value" % os.path.basename(rel), rel, h, "card LQ-2 (b)")
    c65 = load_receipt(RC_C65)["path_sha256"]
    for rel in CENSUS_FILES:
        chk("(c) %s == TASK-20260924-c65bfb path_sha256" % os.path.basename(rel), rel, c65.get(rel), RC_C65 + " path_sha256")
        a, z = CENSUS_CARD_FRAGMENTS[rel]
        checks.append({"check": "(c') card-quoted fragment %s...%s of %s" % (a, z, os.path.basename(rel)), "path": rel,
                       "expected_sha256": "%s...%s" % (a, z), "actual_sha256": c65.get(rel),
                       "expected_from": "card LQ-2 (c)", "equal": bool(c65.get(rel)) and c65[rel].startswith(a) and c65[rel].endswith(z)})
    # (d) every implementation file read (all *.py of the four trees, the r2 exclusion list, trial-plan-v2.json,
    #     both r2 plans (hashed only))
    for key, tree in TREES.items():
        bound = load_receipt(TREE_RECEIPT[key])["path_sha256"]
        for f in sorted(glob.glob(ab(tree) + "/*.py")):
            rel = os.path.relpath(f, REPO)
            chk("(d) %s file == %s" % (key, os.path.basename(TREE_RECEIPT[key].split("/")[-2])), rel, bound.get(rel), TREE_RECEIPT[key] + " path_sha256")
    chk("(d) r2 reg1-exclusion-list.json == TASK-20260924-5ca2a5", EXCL_R2, load_receipt(RC_5CA)["path_sha256"].get(EXCL_R2), RC_5CA + " path_sha256")
    chk("(d) trial-plan-v2.json == TASK-20260923-0fa03f phase A", PLAN_V2, load_receipt(RC_0FA_A)["path_sha256"].get(PLAN_V2), RC_0FA_A + " path_sha256")
    checks.append({"check": "(d') trial-plan-v2.json == card value", "path": PLAN_V2,
                   "expected_sha256": "16f33e39b58277734f52b4b3c7353a9878ff6703a638a561541adb8f57e44e16", "actual_sha256": HASHES.get(PLAN_V2),
                   "expected_from": "card inputs", "equal": HASHES.get(PLAN_V2) == "16f33e39b58277734f52b4b3c7353a9878ff6703a638a561541adb8f57e44e16"})
    for rel in (PLAN_V2_R2, PLAN_A1_R2):
        chk("(d) %s == TASK-20260924-5ca2a5 (hashed only; not otherwise read)" % os.path.basename(rel), rel,
            load_receipt(RC_5CA)["path_sha256"].get(rel), RC_5CA + " path_sha256")
    # (e) every RUN-GFPN-ac4487 file read
    post = load_receipt(RC_0FA_POST)["path_sha256"]
    ref_files = [REF + "/raw-result.json", REF + "/environment.json", REF + "/manifest.yaml"]
    for ext in (".ms", ".ms.log", ".ms.err", ".callgrind.stdout", ".callgrind.stderr"):
        ref_files += sorted(os.path.relpath(f, REPO) for f in glob.glob(ab(REF) + "/solver/*" + ext))
    ref_files = sorted(set(ref_files))
    for rel in ref_files:
        chk("(e) RUN-GFPN-ac4487 file == TASK-20260923-0fa03f post-run", rel, post.get(rel), RC_0FA_POST + " path_sha256")
    # informational (not an LP-5 item): the card, decision and correction against the TASK-20260924-b2b59a receipt
    info = []
    for rel in INFO_FILES:
        want = b2b.get("path_sha256", {}).get(rel)
        got = sha(rel)
        info.append({"path": rel, "sha256": got, "b2b59a_path_sha256": want, "equal": want == got})
    return {"checks": checks, "n_checks": len(checks), "n_equal": sum(1 for c in checks if c["equal"]),
            "pass": all(c["equal"] for c in checks), "informational_b2b59a_bindings": info}


# ===================================================================================================== 2. GUARD
GUARD = {"installed_at": None, "blocked_attempts": []}


def _blocked(name):
    def f(*a, **k):
        GUARD["blocked_attempts"].append({"call": name, "args": repr(a)[:200], "at": now()})
        raise RuntimeError("premise-check guard: child launch %s refused (LQ-1)" % name)
    return f


def install_guard():
    for n in ("fork", "forkpty", "posix_spawn", "posix_spawnp", "system", "popen", "execv", "execve", "execvp", "execvpe",
              "execl", "execle", "execlp", "execlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe", "spawnl", "spawnle"):
        if hasattr(os, n):
            setattr(os, n, _blocked("os." + n))
    subprocess.Popen = _blocked("subprocess.Popen")
    GUARD["installed_at"] = now()


def children_now():
    kids = []
    for t in glob.glob("/proc/self/task/*/children"):
        try:
            kids += open(t).read().split()
        except OSError:
            pass
    return sorted(set(kids))


# ===================================================================================================== helpers
SRC = {}


def src(rel):
    if rel not in SRC:
        b = open(ab(rel), "rb").read()
        OUT["files_read"][rel] = hashlib.sha256(b).hexdigest()
        t = b.decode()
        SRC[rel] = {"text": t, "lines": t.splitlines(), "tree": ast.parse(t) if rel.endswith(".py") else None}
    return SRC[rel]


def line(rel, n):
    return src(rel)["lines"][n - 1]


def cite(rel, n, token):
    """A citation: file, line, token; present iff the token occurs on that line."""
    return {"file": rel, "line": n, "token": token, "present": token in line(rel, n)}


def funcs(rel):
    out = []

    def visit(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = prefix + ch.name
                out.append((ch.lineno, ch.end_lineno, q, ch))
                visit(ch, q + ".")
            else:
                visit(ch, prefix)
    visit(src(rel)["tree"], "")
    return out


def enclosing(rel, n):
    best = None
    for a, z, q, _node in funcs(rel):
        if a <= n <= z and (best is None or a >= best[0]):
            best = (a, q)
    return best[1] if best else "<module>"


def func_node(rel, qual):
    for _a, _z, q, node in funcs(rel):
        if q == qual:
            return node
    return None


def tree_files():
    out = []
    for key, tree in TREES.items():
        out += [(key, os.path.relpath(f, REPO)) for f in sorted(glob.glob(ab(tree) + "/*.py"))]
    return out


# ===================================================================================================== 3. LP-1
CG1_REACHABLE = [
    {"id": "S-1", "draft_line": 275, "draft_token": "S-1  implementation-v2/v2_driver.py lines 165-166 (solve). CLASSIFIED.",
     "file": V2 + "/v2_driver.py", "lines": [165, 166], "census_site": V2 + "/v2_driver.py:166", "enclosing_function": "solve",
     "classified": True,
     "commands": [["trial-plan-v2-r2.json", "fixture"], ["trial-plan-v2-r2.json", "fixture4"], ["trial-plan-v2-r2.json", "controls"],
                  ["trial-plan-v2-r2.json", "anchor-identity"], ["trial-plan-v2-r2.json", "cells"], ["trial-plan-v2-a1-r2.json", "cells"],
                  ["trial-plan-v2-a1-r2.json", "controls-a1"]],
     "commands_draft_text": "Reached by v2 fixture, fixture4, controls, anchor-identity and cells, and by a1 cells and controls-a1 (draft lines 276-277)",
     "disposition": "WRAPPED BY SE-3"},
    {"id": "S-2", "draft_line": 280, "draft_token": "S-2  implementation-v2-a1/a1_health.py lines 144/147 (run_system).",
     "file": A1 + "/a1_health.py", "lines": [144, 147], "census_site": A1 + "/a1_health.py:147", "enclosing_function": "run_system",
     "classified": True, "commands": [["trial-plan-v2-a1-r2.json", "controls-a1"]],
     "commands_draft_text": "Reached by a1 controls-a1 only (draft line 281)", "disposition": "WRAPPED BY HR-3 (HR-1..HR-8)"},
    {"id": "S-3", "draft_line": 283, "draft_token": "S-3  implementation-v2/v2_driver.py line 209 -> v2_solver.py lines",
     "file": V2 + "/v2_driver.py", "lines": [209], "launch_file": V2 + "/v2_solver.py", "launch_lines": [516, 517],
     "census_site": V2 + "/v2_driver.py:209", "enclosing_function": None, "classified": True, "commands": None,
     "commands_draft_text": ("NOT STATED as a command list. The S-3 text (draft lines 285-289) states the launch condition: 'Launched only "
                             "inside a call the SE-3 wrapper makes, in the attempt it records, when that attempt is ok.'"),
     "disposition": "COVERED BY CG-2..CG-6"}]
CG1_UNREACHABLE = [
    {"id": "U-1", "draft_line": 290, "draft_token": "v1 implementation/run_wrapper.py line 36", "file": EXP + "/implementation/run_wrapper.py", "line": 36},
    {"id": "U-2", "draft_line": 291, "draft_token": "(msolve -h); v1 implementation/symmetrize.py lines 392/399;", "file": EXP + "/implementation/symmetrize.py", "line": 399, "argv_line": 392},
    {"id": "U-3", "draft_line": 292, "draft_token": "k5k7/square_analogue.py line 157;", "file": "k5k7/square_analogue.py", "line": 157},
    {"id": "U-4", "draft_line": 292, "draft_token": "k5k7/square_analogue_m4.py line", "file": "k5k7/square_analogue_m4.py", "line": 26,
     "extra_token": {"draft_line": 293, "token": "26; and the unresolved operator argv at v1 run_wrapper.py line 98."}},
    {"id": "U-5", "draft_line": 293, "draft_token": "the unresolved operator argv at v1 run_wrapper.py line 98", "file": EXP + "/implementation/run_wrapper.py", "line": 98,
     "unresolved": True}]


def lp1():
    census = json.load(open(ab(CENSUS_DIR + "/census.json")))
    OUT["files_read"][CENSUS_DIR + "/census.json"] = HASHES[CENSUS_DIR + "/census.json"]
    cn1 = census["CN1_msolve_launch_census"]
    sites = {s["site"]: s for s in cn1["sites"]}
    rd = cn1["reading"]
    rep = {"method": "CG-1 transcribed from the draft (each transcription token verified on its draft line) and compared field by field "
                     "with census.json CN1_msolve_launch_census.sites / .unresolved_argv_sites_reviewed / .reading",
           "draft_token_checks": [], "reachable": [], "unreachable": [], "differences": [], "not_stated_in_CG1": []}
    for e in CG1_REACHABLE + CG1_UNREACHABLE:
        rep["draft_token_checks"].append(cite(LAUNCHCOVER, e["draft_line"], e["draft_token"]))
        if "extra_token" in e:
            rep["draft_token_checks"].append(cite(LAUNCHCOVER, e["extra_token"]["draft_line"], e["extra_token"]["token"]))
    for e in CG1_REACHABLE:
        s = sites.get(e["census_site"])
        row = {"id": e["id"], "census_site": e["census_site"], "census_present": s is not None, "fields": {}}
        if s is None:
            rep["differences"].append("%s: census has no site %s" % (e["id"], e["census_site"]))
            rep["reachable"].append(row)
            continue
        c = s["classification"]
        # file / line
        cl = {"argv_line": [c["argv_line"]["file"], c["argv_line"]["line"]], "launch_line": [c["launch_line"]["file"], c["launch_line"]["line"]]}
        if "wrapper_argv_line" in c:
            cl["wrapper_argv_line"] = [c["wrapper_argv_line"]["file"], c["wrapper_argv_line"]["line"]]
        if e["id"] == "S-3":
            cg = {"driver": [e["file"], e["lines"]], "launch": [e["launch_file"], e["launch_lines"]]}
            eq = (cl["argv_line"] == [e["file"], 209] and cl["launch_line"] == [e["launch_file"], 517]
                  and cl.get("wrapper_argv_line") == [e["launch_file"], 516])
        else:
            cg = [e["file"], e["lines"]]
            eq = cl["argv_line"] == [e["file"], e["lines"][0]] and cl["launch_line"] == [e["file"], e["lines"][-1]]
        row["fields"]["file_and_line"] = {"CG-1": cg, "census": cl, "equal": eq}
        # enclosing function
        if e["enclosing_function"] is None:
            row["fields"]["enclosing_function"] = {"CG-1": "NOT STATED (S-3 names v2_driver.py line 209 -> v2_solver.py lines 516-517, no function)",
                                                   "census": s["enclosing_function"], "equal": None}
            rep["not_stated_in_CG1"].append("%s enclosing function (census: %s)" % (e["id"], s["enclosing_function"]))
        else:
            row["fields"]["enclosing_function"] = {"CG-1": e["enclosing_function"], "census": s["enclosing_function"],
                                                   "equal": e["enclosing_function"] == s["enclosing_function"]}
        # classified
        cc = c["classified"]
        census_cls = cc is True or (e["census_site"] in rd["reachable_sites_classified_by_the_literal_definition"])
        row["fields"]["classified"] = {"CG-1": "CLASSIFIED", "census_value_verbatim": cc,
                                       "census_reading_classified_by_literal_definition": e["census_site"] in rd["reachable_sites_classified_by_the_literal_definition"],
                                       "census_literal_application": (c.get("classification_detail") or {}).get("literal_application_of_the_CN-1_definition"),
                                       "equal": census_cls}
        # commands
        ccmd = sorted([x["plan"], x["command"]] for x in s["reached_by_commands"])
        if e["commands"] is None:
            row["fields"]["commands"] = {"CG-1": e["commands_draft_text"], "census_static": ccmd, "equal": None}
            rep["not_stated_in_CG1"].append("%s commands (census static list: %s)" % (e["id"], ", ".join("%s %s" % tuple(x) for x in ccmd)))
        else:
            row["fields"]["commands"] = {"CG-1": sorted(e["commands"]), "CG-1_text": e["commands_draft_text"], "census_static": ccmd,
                                         "equal": sorted(e["commands"]) == ccmd}
        row["fields"]["reachable"] = {"CG-1": True, "census": s["reachable"], "equal": s["reachable"] is True}
        row["disposition_informational"] = {"CG-1": e["disposition"], "census_wrapped_by": c.get("wrapped_by")}
        for k, v in row["fields"].items():
            if v["equal"] is False:
                rep["differences"].append("%s %s: CG-1 %r != census %r" % (e["id"], k, v.get("CG-1"), v.get("census", v.get("census_static", v.get("census_value_verbatim")))))
        rep["reachable"].append(row)
    # unreachable
    unres = cn1["unresolved_argv_sites_reviewed"]
    for e in CG1_UNREACHABLE:
        if e.get("unresolved"):
            m = [u for u in unres if u["site"] == "%s:%d" % (e["file"], e["line"])]
            row = {"id": e["id"], "census_entry": m[0]["site"] if m else None, "fields": {
                "file_and_line": {"CG-1": [e["file"], e["line"]], "census": [m[0]["site"]] if m else None, "equal": bool(m)},
                "enclosing_function": {"CG-1": "NOT STATED", "census": m[0]["function"] if m else None, "equal": None},
                "classified": {"CG-1": "NOT STATED", "census": "no classification (msolve not determinable statically)", "equal": None},
                "commands": {"CG-1": "UNREACHABLE", "census_reachable": m[0]["reachable"] if m else None, "equal": bool(m) and m[0]["reachable"] is False}}}
        else:
            m = [s for s in sites.values() if s["site"].endswith("%s:%d" % (e["file"], e["line"])) and not s["reachable"]]
            s = m[0] if m else None
            fl = {"CG-1": [e["file"], [e.get("argv_line"), e["line"]] if e.get("argv_line") else e["line"]],
                  "census": ([s["file"], [s["classification"]["argv_line"]["line"], s["classification"]["launch_line"]["line"]]] if s else None)}
            fl["equal"] = bool(s) and (e.get("argv_line") is None or s["classification"]["argv_line"]["line"] == e["argv_line"])
            row = {"id": e["id"], "census_entry": s["site"] if s else None, "fields": {
                "file_and_line": fl,
                "enclosing_function": {"CG-1": "NOT STATED", "census": s["enclosing_function"] if s else None, "equal": None},
                "classified": {"CG-1": "NOT STATED", "census": s["classification"]["classified"] if s else None, "equal": None},
                "commands": {"CG-1": "UNREACHABLE", "census_reached_by_commands": s["reached_by_commands"] if s else None,
                             "census_reachable": s["reachable"] if s else None, "equal": bool(s) and s["reached_by_commands"] == [] and s["reachable"] is False}}}
        for k, v in row["fields"].items():
            if v["equal"] is False:
                rep["differences"].append("%s %s differs or census entry missing" % (e["id"], k))
            if v["equal"] is None:
                rep["not_stated_in_CG1"].append("%s %s (census: %s)" % (e["id"], k, json.dumps(v.get("census"))[:160]))
        rep["unreachable"].append(row)
    # list-level
    cg_reach = sorted(e["census_site"] for e in CG1_REACHABLE)
    cg_unreach = sorted(r["census_entry"] for r in rep["unreachable"] if r["census_entry"])
    census_unreach = sorted(rd["unreachable_sites"] + [u["site"] for u in unres])
    rep["list_level"] = {"CG1_reachable_as_census_ids": cg_reach, "census_reachable": sorted(rd["reachable_msolve_launch_sites"]),
                         "reachable_lists_equal": cg_reach == sorted(rd["reachable_msolve_launch_sites"]),
                         "census_reachable_classified_by_literal_definition": sorted(rd["reachable_sites_classified_by_the_literal_definition"]),
                         "CG1_unreachable_as_census_ids": cg_unreach, "census_unreachable_plus_unresolved": census_unreach,
                         "unreachable_lists_equal": cg_unreach == census_unreach and len(CG1_UNREACHABLE) == len(census_unreach),
                         "census_counts": census.get("counts")}
    if not rep["list_level"]["reachable_lists_equal"]:
        rep["differences"].append("reachable site lists differ")
    if not rep["list_level"]["unreachable_lists_equal"]:
        rep["differences"].append("unreachable lists differ")
    # census argument-level note (S-3 commands), quoted with line check
    rep["census_argument_level_note"] = [cite(CENSUS_DIR + "/census.md", n, t) for n, t in (
        (281, "**Argument-level note.**"), (286, "It runs only after an ok outcome (line 207)."),
        (287, "So the callgrind child actually runs in `fixture` and in `cells` with m = 4, in both plans."))]
    OUT["files_read"][CENSUS_DIR + "/census.md"] = HASHES[CENSUS_DIR + "/census.md"]
    rep["draft_tokens_all_present"] = all(x["present"] for x in rep["draft_token_checks"])
    rep["reading_words_of_the_draft"] = ("this draft is approvable as written ONLY IF CG-1's three reachable sites and five unreachable "
                                         "entries equal the census's lists exactly. Otherwise it is NOT approvable as written. (draft lines 596-598)")
    rep["n_differences_in_stated_values"] = len(rep["differences"])
    rep["n_fields_not_stated_in_CG1"] = len(rep["not_stated_in_CG1"])
    return rep


# ===================================================================================================== 4. LP-2
DRV, SOL = V2 + "/v2_driver.py", V2 + "/v2_solver.py"
RES = R2 + "/r2_resolve.py"


def lp2_i():
    c = [cite(DRV, 158, "def solve(ctx, names, eqs, tag, timeout_s, retain_input, gb_only=False, callgrind_timeout=None):"),
         cite(DRV, 207, 'if callgrind_timeout and outcome == "ok":'),
         cite(DRV, 197, "outcome, reason = V.classify_solve(rec, st, kind, payload, sinfo, nfail)"),
         cite(DRV, 198, "res.update(outcome=outcome, reason=reason"),
         cite(DRV, 200, 'D = st["dimension_of_quotient"]'),
         cite(DRV, 202, "res.update(D=None, D_defined=False"),
         cite(DRV, 204, "res.update(D=D, D_defined=D is not None, solutions="),
         cite(DRV, 206, "res.update(D=None, D_defined=False, solutions=[])"),
         cite(DRV, 208, 'cg_out = os.path.join(sd, tag + ".cg.ms.out")'),
         cite(DRV, 209, 'res["instructions_callgrind"] = V.callgrind_instructions(V.msolve_argv(inp, cg_out, threads=1, gb_only=gb_only), sd, tag, ctx.cap, callgrind_timeout)'),
         cite(DRV, 210, "try:"), cite(DRV, 211, "os.remove(cg_out)"), cite(DRV, 212, "except OSError:"), cite(DRV, 213, "pass"),
         cite(DRV, 184, 'if rec.get("outcome") == "refused_to_start":'), cite(DRV, 186, "return _retain(res, inp, out, retain_input)"),
         cite(DRV, 187, "if gb_only:"), cite(DRV, 189, "return _retain(res, inp, out, retain_input)")]
    node = func_node(DRV, "solve")
    # every store / use of cg_out and of "instructions_callgrind" inside solve (ast)
    cg_uses, ic_stores, ic_other = [], [], []
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id == "cg_out":
            cg_uses.append({"line": n.lineno, "ctx": type(n.ctx).__name__, "source": line(DRV, n.lineno).strip()})
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and n.slice.value == "instructions_callgrind":
            (ic_stores if isinstance(n.ctx, ast.Store) else ic_other).append({"line": n.lineno, "ctx": type(n.ctx).__name__})
        if isinstance(n, ast.Constant) and n.value == "instructions_callgrind":
            pass
    ic_consts = sorted({n.lineno for n in ast.walk(node) if isinstance(n, ast.Constant) and n.value == "instructions_callgrind"})
    # statement order: assignments of outcome / reason / D / solutions precede line 207
    sets_before = sorted({n.lineno for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                          and n.func.attr == "update" and any(k.arg in ("outcome", "reason", "D", "solutions") for k in n.keywords)})
    # the only callgrind launch inside solve
    cg_calls = [{"line": n.lineno, "call": ast.unparse(n.func)} for n in ast.walk(node)
                if isinstance(n, ast.Call) and "callgrind" in ast.unparse(n.func)]
    # does anything in solve read cg_out's contents? (open / parse calls taking cg_out)
    readers = [{"line": n.lineno, "call": ast.unparse(n)[:160]} for n in ast.walk(node) if isinstance(n, ast.Call)
               and any(isinstance(a, ast.Name) and a.id == "cg_out" for a in n.args)
               and ast.unparse(n.func) not in ("V.msolve_argv", "os.remove")]
    # callgrind_instructions never opens the msolve output: its only open() is of the callgrind out file
    ci = func_node(SOL, "callgrind_instructions")
    ci_opens = [{"line": n.lineno, "call": ast.unparse(n)[:120]} for n in ast.walk(ci) if isinstance(n, ast.Call) and ast.unparse(n.func) == "open"]
    res = {"citations": c, "all_citations_present": all(x["present"] for x in c),
           "ast": {"cg_out_name_uses_in_solve": cg_uses, "instructions_callgrind_subscript_stores_in_solve": ic_stores,
                   "instructions_callgrind_other_subscripts_in_solve": ic_other, "instructions_callgrind_constant_lines_in_solve": ic_consts,
                   "res.update_with_outcome_reason_D_solutions_lines": sets_before,
                   "callgrind_calls_in_solve": cg_calls, "calls_passing_cg_out_other_than_msolve_argv_and_os.remove": readers,
                   "open_calls_in_callgrind_instructions": ci_opens}}
    ok = (res["all_citations_present"] and [x["line"] for x in ic_stores] == [209] and not ic_other and ic_consts == [209]
          and all(ln < 207 for ln in sets_before) and [x["line"] for x in cg_calls] == [209] and not readers
          and sorted({x["line"] for x in cg_uses}) == [208, 209, 211]
          and [x["call"] for x in ci_opens] == ["open(out, errors='replace')"])
    res["confirmed"] = ok
    res["notes"] = ["The child is also not reached when the primary child refused to start (lines 184-186) or when gb_only is true "
                    "(lines 187-189): both return before line 207.",
                    "Line 209 passes gb_only=gb_only to msolve_argv; on that path gb_only is always false, because line 187 returned otherwise.",
                    "The record is later copied into recorded rows by callers of solve(): v2_driver.py line 360 (fixture_core.run_target) "
                    "and line 1180 (_run_cell); see LP-2 (iv)."]
    return res


def lp2_ii():
    c = [cite(RES, 203, "def solve(ctx, names, eqs, tag, timeout_s, retain_input, gb_only=False, callgrind_timeout=None):"),
         cite(RES, 206, "args = (ctx, names, eqs, tag, timeout_s, retain_input)"),
         cite(RES, 207, 'kwargs = {"gb_only": gb_only, "callgrind_timeout": callgrind_timeout}'),
         cite(RES, 210, "res = _call_original(original, args, kwargs)"),
         cite(RES, 224, "res = _call_original(original, args, kwargs)"),
         cite(RES, 114, "return original(*args, **kwargs)"),
         cite(RES, 61, 'if outcome == "degenerate_parametrisation" and isinstance(reason, str):'),
         cite(RES, 70, 'if outcome == "positive_dimensional" and RANDOM_FORM in (log_text or ""):'),
         cite(RES, 72, "return None"),
         cite(RES, 227, 'clause = ssf_clause(res.get("outcome"), res.get("reason"), text)'),
         cite(RES, 256, "if clause is None:"), cite(RES, 257, "break"),
         cite(RES, 244, "viol = _consistency(attempts, ends, starts)"), cite(RES, 255, "raise SolverEventConsistencyError"),
         cite(RES, 280, "return res")]
    node = func_node(RES, "solve")
    kw_assigns = [ast.unparse(n) for n in ast.walk(node) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "kwargs" for t in n.targets)]
    kwargs_mutations = [{"line": n.lineno, "src": ast.unparse(n)[:120]} for n in ast.walk(node)
                        if (isinstance(n, (ast.Assign, ast.AugAssign)) and any(isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "kwargs"
                                                                                for t in (n.targets if isinstance(n, ast.Assign) else [n.target])))
                        or (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                            and n.func.value.id == "kwargs")]
    calls = [{"line": n.lineno, "src": ast.unparse(n)} for n in ast.walk(node) if isinstance(n, ast.Call) and ast.unparse(n.func) == "_call_original"]
    ssf = func_node(RES, "ssf_clause")
    returns = [{"line": n.lineno, "src": ast.unparse(n)} for n in ast.walk(ssf) if isinstance(n, ast.Return)]
    res = {"citations": c, "all_citations_present": all(x["present"] for x in c),
           "ast": {"kwargs_assignments": kw_assigns, "kwargs_mutations": kwargs_mutations, "_call_original_calls": calls,
                   "ssf_clause_returns": returns},
           "derivation": [
               "Every attempt (and the gb_only pass-through) calls the original solve() with the same kwargs object built once at line 207; "
               "kwargs is never mutated (ast: no subscript store and no method call on kwargs).",
               "ssf_clause returns a clause only for outcome degenerate_parametrisation (lines 61-69) or positive_dimensional (line 70); "
               "otherwise None (line 72). So an attempt that is followed by another attempt has a non-ok outcome, and inside it the "
               "frozen solve() skips the callgrind child (v2_driver.py line 207).",
               "The loop ends at the first attempt without the SSF signature (lines 256-257), or keeps a still-SSF (non-ok) last "
               "attempt (lines 258-270). The returned result is the last attempt's (line 280).",
               "EDGE, recorded: a consistency violation (lines 244-255) raises after the attempt that caused it. If that attempt "
               "(k >= 2) was ok, its callgrind child ran inside it; that attempt is the last one, it is written to the event, and the "
               "package ends failed (implementation_error). No attempt after an ok attempt exists in any path."]}
    res["confirmed"] = (res["all_citations_present"] and kw_assigns == ["kwargs = {'gb_only': gb_only, 'callgrind_timeout': callgrind_timeout}"]
                        and not kwargs_mutations and sorted(x["line"] for x in calls) == [210, 224]
                        and all(x["src"] == "_call_original(original, args, kwargs)" for x in calls))
    return res


def lp2_iii(tree_list):
    c = [cite(SOL, 515, 'out = os.path.join(workdir, "%s.callgrind.out" % tag)'),
         cite(SOL, 516, 'vargv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=%s" % out] + list(argv)'),
         cite(SOL, 517, 'rec = run_child(vargv, os.path.join(workdir, "%s.callgrind.stdout" % tag), os.path.join(workdir, "%s.callgrind.stderr" % tag),'),
         cite(DRV, 160, 'sd = os.path.join(ctx.rd, "solver")'),
         cite(DRV, 165, "argv = V.msolve_argv(inp, out, threads=1, gb_only=gb_only)"),
         cite(DRV, 209, "V.msolve_argv(inp, cg_out, threads=1, gb_only=gb_only), sd, tag"),
         cite(SOL, 548, "try:"), cite(SOL, 549, "os.remove(out)"), cite(SOL, 550, "except OSError:"), cite(SOL, 551, "pass"),
         cite(SOL, 521, 'if rec.get("outcome") != "ok" or not os.path.exists(out):'), cite(SOL, 524, "return res"),
         cite(RES, 189, 'for ext in (".ms.out", ".ms.log", ".ms.err"):'), cite(RES, 195, "os.rename(src, dst)")]
    node = func_node(DRV, "solve")
    ma = [n for n in ast.walk(node) if isinstance(n, ast.Call) and ast.unparse(n.func) == "V.msolve_argv"]
    ma_rec = [{"line": n.lineno, "args": [ast.unparse(a) for a in n.args], "keywords": {k.arg: ast.unparse(k.value) for k in n.keywords}} for n in ma]
    argv_equal_but_output = (len(ma_rec) == 2 and ma_rec[0]["args"][0] == ma_rec[1]["args"][0] and ma_rec[0]["keywords"] == ma_rec[1]["keywords"]
                             and ma_rec[0]["args"][1] != ma_rec[1]["args"][1] and len(ma_rec[0]["args"]) == len(ma_rec[1]["args"]) == 2)
    # every remove / rename / move call in the scanned trees
    pat = re.compile(r"^(os\.(remove|unlink|rename|replace|rmdir|removedirs|renames)|shutil\.(rmtree|move)|.*\.unlink|.*\.rename)$")
    calls = []
    for key, rel in tree_list:
        for n in ast.walk(src(rel)["tree"]):
            if isinstance(n, ast.Call) and pat.match(ast.unparse(n.func)):
                calls.append({"tree": key, "file": rel, "line": n.lineno, "function": enclosing(rel, n.lineno), "call": ast.unparse(n)[:200],
                              "names_callgrind_text": "callgrind" in ast.unparse(n)})
    reviewed = {  # manual reading of every call, recorded (file, line) -> target
        (DRV, 144): "out + '.npz' of a builder child (builder scratch)",
        (DRV, 211): "<tag>.cg.ms.out (msolve output of the callgrind child), removed unread",
        (DRV, 221): "inp = <tag>.ms when not retained (_retain)",
        (DRV, 227): "out = <tag>.ms.out when > RETAIN_MAX_BYTES (_retain)",
        (SOL, 549): "<tag>.callgrind.out (callgrind's own out file)",
        (A1 + "/a1_devchecks.py", 342): "development harness scratch directory base = os.path.join(sd, name) under its own output",
        (A1 + "/a1_toy.py", 302): "development harness scratch directory <out>/toy",
        (R1 + "/r1_devchecks_more.py", 250): "development harness copy directory <out>/perturb/<tag> (a copy of the reference)",
        (R1 + "/r1_dv6.py", 83): "manifest.yaml of a DV-6 synthetic scratch run directory",
        (R1 + "/r1_dv6.py", 137): "DV-6 scratch runs directory <out>/runs/<tag>",
        (R1 + "/r1_dv6.py", 275): "DV-6 scratch entry directory <out>/entry/<entry>_<mode>",
        (R1 + "/r1_toy.py", 298): "development harness scratch directory <out>/toy",
        (R2 + "/r2_devchecks_more.py", 278): "development harness copy directory <out>/perturb/<tag> (a copy of the reference)",
        (R2 + "/r2_devchecks_more.py", 608): "development harness extraction directory <out>/extract",
        (R2 + "/r2_dv6.py", 84): "manifest.yaml of a DV-6 synthetic scratch run directory",
        (R2 + "/r2_dv6.py", 138): "DV-6 scratch runs directory <out>/runs/<tag>",
        (R2 + "/r2_dv6.py", 287): "DV-6 scratch entry directory <out>/entry/<entry>_<mode>",
        (R2 + "/r2_reg1.py", 151): "a NamedTemporaryFile copy of a .ms.out (parsed_key)",
        (RES, 148): "solver-events.json.tmp -> solver-events.json (atomic rewrite)",
        (RES, 195): "<tag>.ms.out / .ms.log / .ms.err -> +'.ssf-attempt<k>' (loop at line 189 names only these three extensions)"}
    for x in calls:
        x["target_manual_reading"] = reviewed.get((x["file"], x["line"]), "NOT REVIEWED")
        x["can_target_a_package_callgrind_stdout_or_stderr"] = False if (x["file"], x["line"]) in reviewed else None
    res = {"citations": c, "all_citations_present": all(x["present"] for x in c), "msolve_argv_calls_in_solve": ma_rec,
           "callgrind_msolve_argv_equals_primary_except_output_path": argv_equal_but_output,
           "remove_rename_calls_in_scanned_trees": calls, "n_remove_rename_calls": len(calls),
           "unreviewed_calls": [x for x in calls if x["target_manual_reading"] == "NOT REVIEWED"],
           "notes": ["The workdir passed at v2_driver.py line 209 is sd = <run dir>/solver (line 160), so the two files are "
                     "<run dir>/solver/<tag>.callgrind.stdout and .stderr.",
                     "run_child is called with count_instructions=False for the callgrind child (v2_solver.py line 518) and with its "
                     "default for the primary child (v2_driver.py line 166). That is a run_child keyword, not an msolve argv element.",
                     "On a non-ok callgrind child, or a missing out file, callgrind_instructions returns at line 524 BEFORE the removal at "
                     "lines 548-551, so <tag>.callgrind.out is left in place on that path. Recorded; it is not a removal.",
                     "Every rmtree target in the scanned trees is a development-harness scratch or copy directory under the harness's own "
                     "output path (manual reading, listed per call); none names a package run directory."]}
    res["confirmed"] = (res["all_citations_present"] and argv_equal_but_output and not res["unreviewed_calls"]
                        and not any(x["names_callgrind_text"] and x["line"] != 549 for x in calls))
    return res


CG_KEYS_TOP = None


def lp2_iv(tree_list):
    ci = func_node(SOL, "callgrind_instructions")
    top, child = [], []
    for n in ast.walk(ci):
        if isinstance(n, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == "method" for k in n.keys):
            for k, v in zip(n.keys, n.values):
                top.append({"key": k.value, "line": n.lineno})
                if k.value == "child":
                    tup = [g for g in ast.walk(v) if isinstance(g, ast.Tuple)]
                    child = [e.value for e in tup[0].elts]
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "res" and isinstance(t.slice, ast.Constant):
                    top.append({"key": t.slice.value, "line": n.lineno})
    keys = []
    for x in top:
        if x["key"] not in [k["key"] for k in keys]:
            keys.append({"key": x["key"], "lines": sorted({y["line"] for y in top if y["key"] == x["key"]})})
    ex = json.load(open(ab(EXCL_R2)))
    OUT["files_read"][EXCL_R2] = HASHES[EXCL_R2]
    x1417 = [e for e in ex["entries"] if e["id"] in ("X14", "X15", "X16", "X17")]
    excl_lines = [cite(EXCL_R2, n, t) for n, t in ((35, '"id": "X14"'), (37, '"id": "X15"'), (39, '"id": "X16"'), (41, '"id": "X17"'))]
    removed = [tuple(e["path"][3:]) for e in x1417]
    compared_top = [k["key"] for k in keys if (k["key"],) not in removed]
    compared_child = [c for c in child if ("child", c) not in removed]
    all_cg_excl = [e["id"] for e in ex["entries"] if "instructions_callgrind" in e["path"]]
    global CG_KEYS_TOP
    CG_KEYS_TOP = [k["key"] for k in keys]
    # ---- every textual hit of instructions_callgrind and each key, in every scanned .py file
    search_keys = ["instructions_callgrind"] + [k["key"] for k in keys] + [c for c in child if c not in [k["key"] for k in keys]]
    hits = []
    for key_t, rel in tree_list:
        s = src(rel)
        tokpos = {}
        try:
            for tok in tokenize.generate_tokens(io.StringIO(s["text"]).readline):
                for ln in range(tok.start[0], tok.end[0] + 1):
                    tokpos.setdefault(ln, []).append(tok)
        except tokenize.TokenError:
            pass
        for i, L in enumerate(s["lines"], 1):
            for key in search_keys:
                for m in re.finditer(r"\b%s\b" % re.escape(key), L):
                    kind = "other"
                    for tok in tokpos.get(i, []):
                        a = tok.start if tok.start[0] == i else (i, 0)
                        z = tok.end if tok.end[0] == i else (i, 10 ** 6)
                        if a[1] <= m.start() < z[1]:
                            kind = {tokenize.NAME: "identifier", tokenize.STRING: "string", tokenize.COMMENT: "comment"}.get(tok.type, tokenize.tok_name[tok.type])
                            if kind == "string" and tok.string.strip("\"'") == key:
                                kind = "string-literal key"
                            break
                    hits.append({"tree": key_t, "file": rel, "line": i, "key": key, "token_kind": kind,
                                 "function": enclosing(rel, i), "source": L.strip()[:220]})
    # classification (recorded rules; every hit gets one)
    fn_mentions_ic = {}
    for key_t, rel in tree_list:
        for a, z, q, _n in funcs(rel):
            body = "\n".join(src(rel)["lines"][a - 1:z])
            fn_mentions_ic[(rel, q)] = "instructions_callgrind" in body
    for h in hits:
        rel, ln, key, fn = h["file"], h["line"], h["key"], h["function"]
        if h["token_kind"] in ("comment",) or (h["token_kind"] == "string" and key not in ("instructions_callgrind",)):
            cls, why = "no", "text inside a comment or a docstring / message string; not a key access"
        elif rel == SOL and fn == "callgrind_instructions":
            cls, why = "writer", "constructs the instructions_callgrind record (v2_solver.callgrind_instructions); it reads the callgrind child's own rec to build it"
        elif rel == DRV and fn == "solve" and ln == 209 and key == "instructions_callgrind":
            cls, why = "writer", "stores the record at res['instructions_callgrind'] (line 209); not a reader"
        elif rel == DRV and fn == "solve" and 207 <= ln <= 213:
            cls, why = "no", "reads the primary solve's own outcome (line 207), not the callgrind record's"
        elif rel == DRV and key == "instructions_callgrind" and ln in (360, 1180):
            cls, why = "copy", ("copies r['instructions_callgrind'] whole into the recorded row by a key tuple (dict comprehension); "
                                "no decision reads it")
        elif re.search(r'collect\(\s*raw\s*,\s*"%s"' % re.escape(key), h["source"]):
            cls, why = "READS", ("generic key-name collection over the WHOLE raw-result (recursive collect): it also collects "
                                 "instructions_callgrind.child.%s wherever a record carries one" % key)
        elif h["token_kind"] == "string" and key == "instructions_callgrind":
            cls, why = "no", "text inside a message / docstring string"
        elif fn_mentions_ic.get((rel, fn.split(".")[0])) or fn_mentions_ic.get((rel, fn)):
            cls, why = "REVIEW", "enclosing function also mentions instructions_callgrind"
        else:
            cls, why = "no", ("the accessed object is not an instructions_callgrind record: the enclosing function never names "
                              "instructions_callgrind and the hit is not a key-name collection over raw-result")
        h["reads_instructions_callgrind_value"] = cls
        h["why"] = why
    review_manual = {
        (DRV, 359): ("no", "key tuple of the row copy: row['outcome'], row['reason'] are the target's own fields, not the callgrind record's"),
        (DRV, 1179): ("no", "key tuple of the row copy: row['outcome'], row['reason'] are the target's own fields, not the callgrind record's"),
    }
    for h in hits:
        if h["reads_instructions_callgrind_value"] == "REVIEW":
            m = review_manual.get((h["file"], h["line"]))
            if m is None and h["file"] == DRV and h["function"] in ("fixture_core", "fixture_core.run_target", "_run_cell", "solve"):
                m = ("no", "in a function that also copies instructions_callgrind; this hit accesses the target / child record's own key, not the "
                           "callgrind record's (the callgrind record is never subscripted by key in scanned code)")
            if m:
                h["reads_instructions_callgrind_value"], h["why"] = m[0], m[1] + " [manual reading]"
    # ---- generic (non-textual) consumers: recursive walkers and whole-entry comparisons, found by ast
    walkers = []
    for key_t, rel in tree_list:
        for a, z, q, node in funcs(rel):
            if isinstance(node, ast.ClassDef):
                continue
            calls = {ast.unparse(c.func) for c in ast.walk(node) if isinstance(c, ast.Call)}
            body = ast.unparse(node)
            # a container walker: recursive AND dispatches on dict / list (not arithmetic recursion)
            if node.name in calls and "isinstance" in body and ("dict" in body or "list" in body):
                walkers.append({"file": rel, "line": a, "function": q})
    # the REG-1 comparators' non-recursive entry point strip() wraps the recursive _strip()
    for rel in (R1 + "/r1_reg1.py", R2 + "/r2_reg1.py"):
        for a, z, q, node in funcs(rel):
            if q == "strip":
                walkers.append({"file": rel, "line": a, "function": q, "note": "non-recursive; wraps _strip over whole objects"})
    walker_calls = []
    for w in walkers:
        name = w["function"].split(".")[-1]
        for n in ast.walk(src(w["file"])["tree"]):
            if isinstance(n, ast.Call) and ast.unparse(n.func) == name:
                fn = enclosing(w["file"], n.lineno)
                if fn.split(".")[-1] == name:
                    continue                                        # the recursion itself
                walker_calls.append({"file": w["file"], "line": n.lineno, "function": fn, "call": ast.unparse(n)[:180]})
    generic_manual = {
        (V2 + "/v2_run_wrapper.py", 202): "READS: collect(raw, 'rlimit_as_child_getrlimit') gathers every read-back in raw-result, including instructions_callgrind.child.rlimit_as_child_getrlimit; the set goes to manifest resources.child_rlimit_as_read_back_by_getrlimit (line 222)",
        (V2 + "/v2_run_wrapper.py", 203): "collect(raw, 'threads_executed'): not a callgrind key; traverses the record, reads nothing from it",
        (A1 + "/a1_run_wrapper.py", 324): "READS: as v2_run_wrapper.py 202 (manifest line 349)",
        (A1 + "/a1_run_wrapper.py", 325): "collect(raw, 'threads_executed'): not a callgrind key",
        (R1 + "/r1_run_wrapper.py", 408): "READS: as v2_run_wrapper.py 202 (manifest line 443)",
        (R1 + "/r1_run_wrapper.py", 409): "collect(raw, 'threads_executed'): not a callgrind key",
        (R2 + "/r2_run_wrapper.py", 474): "READS: as v2_run_wrapper.py 202 (manifest line 517)",
        (R2 + "/r2_run_wrapper.py", 475): "collect(raw, 'threads_executed'): not a callgrind key",
        (V2 + "/v2_check_run.py", 99): "walk(raw, scan): scan reacts only to keys F3 / tail_check_2_36 (lines 96-98); traverses the callgrind record, reads no callgrind key",
        (R2 + "/r2_check_run.py", 98): "find_solver_records(raw): yields dicts whose 'solver' has an argv (lines 81-90); the callgrind record has no 'solver' key and is never yielded; reads no callgrind key",
        (R1 + "/r1_reg1.py", 172): "READS (whole-entry): r1 REG-1 (b) compares every target entry whole minus the r1 exclusions (strip); the r1 comparator of the retired r1 lineage",
        (R1 + "/r1_reg1.py", 173): "READS (whole-entry): as line 172, candidate side",
        (R1 + "/r1_reg1.py", 152): "certificate scope; no callgrind record",
        (R1 + "/r1_reg1.py", 178): "raw-result metrics scope; no callgrind record",
        (R2 + "/r2_reg1.py", 260): "READS (whole-entry): r2 REG-1 (b), reference side (the comparison the draft names)",
        (R2 + "/r2_reg1.py", 261): "READS (whole-entry): r2 REG-1 (b), candidate side",
        (R2 + "/r2_reg1.py", 240): "certificate scope; no callgrind record",
        (R2 + "/r2_reg1.py", 266): "raw-result metrics scope; no callgrind record",
        (R1 + "/r1_reg1.py", 73): "inside strip(): applies _strip once per exclusion path of the given scope (for target entries, X14-X17 remove four callgrind fields)",
        (R2 + "/r2_reg1.py", 83): "inside strip(): applies _strip once per exclusion path of the given scope (for target entries, X14-X17 remove four callgrind fields)",
    }
    for w in walker_calls:
        w["manual_reading"] = generic_manual.get((w["file"], w["line"]), "operates on trial plans (DV-5 / RC-4 (c) / plan build), not on raw-result; reads no target entry")
    for w in walker_calls:
        if w["manual_reading"].startswith("operates on trial plans"):
            # verify the argument is not a raw-result object by name
            w["argument_is_named_raw"] = bool(re.search(r"\b(raw|rraw|craw|rl\[|cl\[)\b", w["call"]))
    extra_generic = [
        {"file": V2 + "/v2_check_run.py", "line": 63, "function": "main", "reading": "READS the manifest list built by the wrappers' collect "
         "(which includes the callgrind child's read-back): every entry must equal the requested cap, else an error (lines 63-70); "
         "v2_check_run.main is the frozen checker, run unchanged by a1_check_run.main (line 133), r1_check_run (lines 41, 60) and r2_check_run",
         "citations": [cite(V2 + "/v2_check_run.py", 63, 'caps = res.get("child_rlimit_as_read_back_by_getrlimit") or []'),
                       cite(V2 + "/v2_check_run.py", 69, 'if c.get("soft") != req_cap or c.get("hard") != req_cap:'),
                       cite(V2 + "/v2_check_run.py", 70, 'errs.append("child RLIMIT_AS read-back %s != requested %s" % (c, req_cap))'),
                       cite(V2 + "/v2_run_wrapper.py", 202, 'collect(raw, "rlimit_as_child_getrlimit", [])'),
                       cite(V2 + "/v2_run_wrapper.py", 222, '"child_rlimit_as_read_back_by_getrlimit": [json.loads(c) for c in caps],'),
                       cite(A1 + "/a1_check_run.py", 133, "v2_rc = V2CHK.main(rd)"),
                       cite(R2 + "/r2_check_run.py", 70, "return K.main(rd)")]},
        {"file": V2 + "/v2_check_run.py", "line": 103, "function": "main", "reading": "txt = json.dumps(raw): a whole-text substring test for three v1 key names (lines 103-106); it traverses the callgrind record's text and reacts to none of its keys",
         "citations": [cite(V2 + "/v2_check_run.py", 103, "txt = json.dumps(raw)")]},
    ]
    # the r2 comparator is the named reader: it never names instructions_callgrind; it reads it through strip() of whole entries
    r2reg1_names_ic = "instructions_callgrind" in src(R2 + "/r2_reg1.py")["text"]
    r1reg1_names_ic = "instructions_callgrind" in src(R1 + "/r1_reg1.py")["text"]
    readers = sorted({(h["file"], h["function"]) for h in hits if h["reads_instructions_callgrind_value"] == "READS"})
    discrepancies = []
    for f, fn in readers:
        discrepancies.append("%s %s reads instructions_callgrind.child.rlimit_as_child_getrlimit by generic key-name collection" % (f, fn))
    discrepancies.append(V2 + "/v2_check_run.py main (lines 63-70) checks the manifest read-back list that includes the callgrind child's "
                         "rlimit_as_child_getrlimit (a checker function reading a value derived from an instructions_callgrind key)")
    discrepancies.append(R1 + "/r1_reg1.py compare (lines 168-173) reads instructions_callgrind fields by whole-entry comparison, as "
                         "r2_reg1.compare does (an r1 function other than r2_reg1.compare)")
    res = {"key_set": {"top_level": keys, "child_mapping": child, "source_lines": "v2_solver.py 519-547",
                       "note": ("f4_core_inclusive_Ir and f4_core_function are absent on the non-ok path (return at line 524); "
                                "f4_core_function is absent on the callgrind_annotate exception path (lines 545-547); reason only on the "
                                "non-ok path (523); f4_core_note only when no 'f4' function is found (544) or on the exception (547).")},
           "exclusions_X14_X17": [{"id": e["id"], "path": e["path"], "category": e["category"]} for e in x1417],
           "exclusion_line_citations": excl_lines, "exclusions_naming_instructions_callgrind": all_cg_excl,
           "reg1_compared_subset": {"top_level": compared_top, "child_mapping": compared_child,
                                    "as_dv17_list": ["method", "label", "child.outcome", "child.returncode", "child.rlimit_as_child_getrlimit",
                                                     "reason (presence and value)", "f4_core_function", "f4_core_note (presence and value)"]},
           "textual_search": {"keys_searched": search_keys, "trees": list(TREES.values()), "n_files": len(tree_list), "n_hits": len(hits),
                              "hits_by_class": {c: sum(1 for h in hits if h["reads_instructions_callgrind_value"] == c) for c in
                                                sorted({h["reads_instructions_callgrind_value"] for h in hits})},
                              "hits": hits},
           "generic_consumers": {"recursive_walkers": walkers, "walker_and_strip_call_sites": walker_calls, "other": extra_generic,
                                 "r2_reg1_names_instructions_callgrind_textually": r2reg1_names_ic,
                                 "r1_reg1_names_instructions_callgrind_textually": r1reg1_names_ic},
           "discrepancies": discrepancies}
    res["confirmed"] = False if discrepancies else True
    return res


def lp2_v():
    c = [cite(SOL, 347, "def parse_msolve_log(text):"),
         cite(SOL, 350, 'st = {"dimension_of_quotient": None, "f4_rounds": [], "fglm": {}, "no_solution": False,'),
         cite(SOL, 351, '"positive_dimension_reported": False, "timings": {}, "f4_summary": {}}'),
         cite(SOL, 352, r'mm = re.search(r"Dimension of quotient:\s*(\d+)", text)'),
         cite(SOL, 354, 'st["dimension_of_quotient"] = int(mm.group(1))'),
         cite(SOL, 357, 'if re.search(r"(?i)positive dimension|dimension is positive|not zero-dimensional|positive-dimensional", text):'),
         cite(SOL, 358, 'st["positive_dimension_reported"] = True'),
         cite(SOL, 395, 'st["fglm"] = {"dim": int(mm.group(1)), "nontrivial_cols": int(mm.group(2)), "nontrivial_pct": float(mm.group(3))}'),
         cite(SOL, 396, r'mm = re.search(r"Degree of the square-free part:\s*(\d+)", text)'),
         cite(SOL, 398, 'st["fglm"]["squarefree_degree"] = int(mm.group(1))'),
         cite(SOL, 402, "return st")]
    return {"citations": c, "all_citations_present": all(x["present"] for x in c),
            "names_returned": {"dimension_of_quotient": "st['dimension_of_quotient'] (None if not printed)",
                               "squarefree_degree": "st['fglm']['squarefree_degree'] -- KEY ABSENT (not None) when 'Degree of the square-free part:' is not printed",
                               "positive_dimension_reported": "st['positive_dimension_reported'] (False by default)"},
            "note": "The first 'Dimension of quotient:' match is taken (re.search); a log with several printed dimensions yields the first."}


def ssf_indicator(st, text):
    rf = RANDOM_FORM in text
    sq = st["fglm"].get("squarefree_degree")
    dq = st["dimension_of_quotient"]
    return rf or (sq is not None and dq is not None and sq != dq)


RANDOM_FORM = "[coefficients of linear form are randomly chosen]"


def read_text(rel):
    b = open(ab(rel), "rb").read()
    OUT["files_read"][rel] = hashlib.sha256(b).hexdigest()
    return b.decode(errors="replace")


def lp2_vi_vii(V):
    rawrel = REF + "/raw-result.json"
    rawb = open(ab(rawrel), "rb").read()
    OUT["files_read"][rawrel] = hashlib.sha256(rawb).hexdigest()
    raw = json.loads(rawb)
    rawlines = rawb.decode().splitlines()
    ex = json.load(open(ab(EXCL_R2)))
    xpaths = [e["path"][3:] for e in ex["entries"] if e["id"] in ("X14", "X15", "X16", "X17")]
    # any instructions_callgrind anywhere in raw-result (full recursive search)
    anywhere = []

    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "instructions_callgrind":
                    anywhere.append(p + "/" + k)
                walk(v, p + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + "[%d]" % i)
    walk(raw, "")
    entries = []
    for lst in ("targets", "planted_targets", "replaced_fresh_targets"):
        for i, t in enumerate(raw.get(lst) or []):
            for arm, a in (t.get("arms") or {}).items():
                if "instructions_callgrind" not in a:
                    continue
                ic = a["instructions_callgrind"]
                tag = "fx_%s_%s" % (t["target"], arm)          # v2_driver.py line 344
                comp = json.loads(json.dumps(ic))
                for pth in xpaths:
                    o = comp
                    for k in pth[:-1]:
                        o = o.get(k, {}) if isinstance(o, dict) else {}
                    if isinstance(o, dict):
                        o.pop(pth[-1], None)
                files = {}
                for ext in (".ms", ".callgrind.stdout", ".callgrind.stderr", ".ms.log", ".ms.err"):
                    rel = "%s/solver/%s%s" % (REF, tag, ext)
                    if os.path.exists(ab(rel)):
                        b = open(ab(rel), "rb").read()
                        OUT["files_read"][rel] = hashlib.sha256(b).hexdigest()
                        files[ext] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
                    else:
                        files[ext] = "absent"
                argv = (a.get("solver") or {}).get("argv") or []
                inp_from_argv = os.path.basename(argv[argv.index("-f") + 1]) if "-f" in argv else None
                e = {"target_list": lst, "index": i, "target": t["target"], "arm": arm, "tag": tag,
                     "tag_matches_recorded_argv_input": inp_from_argv == tag + ".ms",
                     "reg1_compared_fields_verbatim": comp, "child_wall_seconds": (ic.get("child") or {}).get("wall_seconds"),
                     "retained": {"solver/<tag>.ms": files[".ms"], "<tag>.callgrind.stdout": files[".callgrind.stdout"],
                                  "<tag>.callgrind.stderr": files[".callgrind.stderr"]},
                     "primary_logs": {"<tag>.ms.log": files[".ms.log"], "<tag>.ms.err": files[".ms.err"]},
                     "recorded": {"outcome": a.get("outcome"), "dimension_of_quotient_printed": a.get("dimension_of_quotient_printed"),
                                  "input_sha256": (a.get("input") or {}).get("sha256")}}
                e["retained_ms_sha256_equals_recorded_input_sha256"] = (isinstance(files[".ms"], dict) and files[".ms"]["sha256"] == e["recorded"]["input_sha256"])
                # anomalies named by the draft
                an = []
                if (ic.get("child") or {}).get("outcome") != "ok":
                    an.append("non-ok child")
                if "reason" in ic:
                    an.append("reason present")
                if "f4_core_note" in ic:
                    an.append("f4_core_note present")
                if ic.get("f4_core_function") is None:
                    an.append("null or absent f4_core_function")
                # (vii) readings
                logs = {}
                for pair, (e1, e2) in (("callgrind", (".callgrind.stdout", ".callgrind.stderr")), ("primary", (".ms.log", ".ms.err"))):
                    if files[e1] == "absent" or files[e2] == "absent":
                        logs[pair] = {"text_built": False, "absent": [x for x in (e1, e2) if files[x] == "absent"]}
                        continue
                    text = read_text("%s/solver/%s%s" % (REF, tag, e1)) + "\n" + read_text("%s/solver/%s%s" % (REF, tag, e2)) + "\n"
                    st = V.parse_msolve_log(text)
                    logs[pair] = {"text_built": True, "text_rule": "%s + '\\n' + %s + '\\n'" % (e1, e2),
                                  "printed_quotient_dimension": st["dimension_of_quotient"],
                                  "squarefree_degree": st["fglm"].get("squarefree_degree", "absent (key not set)"),
                                  "positive_dimension_reported": st["positive_dimension_reported"],
                                  "random_form_string_present": RANDOM_FORM in text,
                                  "log_visible_ssf_indicator": ssf_indicator(st, text),
                                  "n_dimension_of_quotient_lines": len(re.findall(r"Dimension of quotient:\s*(\d+)", text)),
                                  "distinct_printed_dimensions": sorted({int(x) for x in re.findall(r"Dimension of quotient:\s*(\d+)", text)}),
                                  "linear_form_lines": sorted(set(re.findall(r"\[coefficients of linear form are[^\]]*\]", text)))}
                    if pair == "callgrind":
                        cmd = [ln for ln in text.splitlines() if re.match(r"^==\d+== Command: ", ln)]
                        logs[pair]["valgrind_command_line"] = cmd[0].split("Command: ", 1)[1] if cmd else None
                        exp_argv = [x if x != argv[argv.index("-o") + 1] else x[:-len(".ms.out")] + ".cg.ms.out" for x in argv] if "-o" in argv else None
                        logs[pair]["command_equals_recorded_primary_argv_with_cg_output_path"] = (cmd[0].split("Command: ", 1)[1] == " ".join(exp_argv)) if (cmd and exp_argv) else None
                both = all(logs[p].get("text_built") for p in logs)
                e["log_readings"] = logs
                e["printed_quotient_dimensions_agree"] = (logs["callgrind"]["printed_quotient_dimension"] == logs["primary"]["printed_quotient_dimension"]) if both else None
                e["callgrind_printed_dimension_equals_recorded_dimension_of_quotient_printed"] = (
                    logs["callgrind"]["printed_quotient_dimension"] == a.get("dimension_of_quotient_printed")) if logs["callgrind"].get("text_built") else None
                if both and logs["callgrind"]["log_visible_ssf_indicator"]:
                    an.append("log-visible SSF indicator (callgrind pair)")
                if both and logs["primary"]["log_visible_ssf_indicator"]:
                    an.append("log-visible SSF indicator (primary pair)")
                if e["printed_quotient_dimensions_agree"] is False:
                    an.append("quotient-dimension disagreement")
                e["anomalies_named_by_the_draft"] = an
                entries.append(e)
    # supplementary: the draft's own citations of the reference (findings L-3 and not_established; budget_impact)
    lines_f4 = [n for n, L in enumerate(rawlines, 1) if '"f4_core_function"' in L]
    vals_f4 = sorted({L.split(":", 1)[1].strip().rstrip(",") for L in rawlines if '"f4_core_function"' in L})
    stdout = read_text(REF + "/solver/fx_reg0_raw_x.callgrind.stdout").splitlines()
    mslog = read_text(REF + "/solver/fx_reg0_raw_x.ms.log").splitlines()
    supp = {"f4_core_function_lines_in_raw_result": {"n": len(lines_f4), "first": lines_f4[0] if lines_f4 else None, "last": lines_f4[-1] if lines_f4 else None,
                                                    "distinct_values": vals_f4},
            "raw_result_lines_732_748": rawlines[731:748],
            "raw_result_line_736": rawlines[735],
            "fx_reg0_raw_x_stdout_vs_ms_log": {str(n): {"callgrind.stdout": stdout[n - 1], "ms.log": mslog[n - 1], "equal": stdout[n - 1] == mslog[n - 1]}
                                               for n in (239, 240, 317, 318)},
            "fx_reg0_raw_x_stdout_equals_ms_log_whole": stdout == mslog,
            "fx_reg0_raw_x_line_counts": {"callgrind.stdout": len(stdout), "ms.log": len(mslog)},
            "fx_reg0_raw_x_differing_line_numbers": [n for n in range(1, min(len(stdout), len(mslog)) + 1) if stdout[n - 1] != mslog[n - 1]],
            "fx_reg0_raw_x_equal_after_masking_decimal_numbers_and_whitespace_runs": [re.sub(r"\s+", " ", re.sub(r"\d+\.\d+", "#", x)) for x in stdout] == [re.sub(r"\s+", " ", re.sub(r"\d+\.\d+", "#", x)) for x in mslog]}
    ws = [e["child_wall_seconds"] for e in entries]
    return {"n_entries": len(entries), "instructions_callgrind_paths_anywhere_in_raw_result": anywhere,
            "entries": entries, "sum_child_wall_seconds": round(sum(ws), 6) if all(isinstance(w, (int, float)) for w in ws) else None,
            "all_retained_present": all(isinstance(v, dict) for e in entries for v in e["retained"].values()),
            "entries_with_anomalies": [(e["tag"], e["anomalies_named_by_the_draft"]) for e in entries if e["anomalies_named_by_the_draft"]],
            "supplementary_draft_citation_checks": supp}


def lp3(vi, R=10, timeout=None):
    n, s = vi["n_entries"], vi["sum_child_wall_seconds"]
    return {"label": "DERIVED (arithmetic on archived reference values); never measured", "R": R, "N_ref": n,
            "sum_reference_child_wall_seconds": s,
            "bound_1_R_x_sum_plus_spacing_s": round(R * s + 2.0 * R * n, 6), "bound_1_formula": "R x sum + 2.0 s x R x N_ref",
            "bound_1_parts": {"R_x_sum": round(R * s, 6), "spacing": 2.0 * R * n},
            "bound_2_worst_case_s": R * n * timeout, "bound_2_formula": "R x N_ref x callgrind_timeout_s.m3", "callgrind_timeout_s_m3": timeout,
            "bound_2_hours": round(R * n * timeout / 3600.0, 3), "bound_1_hours": round((R * s + 2.0 * R * n) / 3600.0, 6)}


def lp4(V):
    env = json.load(open(ab(REF + "/environment.json")))
    OUT["files_read"][REF + "/environment.json"] = HASHES[REF + "/environment.json"]
    quoted = {}

    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + "[%d]" % i)
        elif any(t in (p + str(o)).lower() for t in ("valgrind", "msolve", "callgrind")):
            quoted[p] = o
    walk(env, "")
    w = {}
    for prog in ("valgrind", "callgrind_annotate", "msolve"):
        p = shutil.which(prog)
        w[prog] = {"shutil.which": p, "realpath": os.path.realpath(p) if p else None}
    consts = {"v2_solver.VALGRIND": V.VALGRIND, "v2_solver.MSOLVE": V.MSOLVE}
    stat = {k: {"exists": os.path.exists(v), "realpath": os.path.realpath(v)} for k, v in consts.items()}
    return {"label": "READ (shutil.which and os.path only; no tool launched)", "which": w, "frozen_constants": consts, "frozen_constants_stat": stat,
            "callgrind_annotate_lookup": "PATH lookup at v2_solver.py line 533 (argv[0] 'callgrind_annotate')",
            "PATH": os.environ.get("PATH"),
            "RUN-GFPN-ac4487_environment_json_verbatim": quoted,
            "environment_json_records_callgrind_annotate": any("callgrind_annotate" in (k + str(v)) for k, v in quoted.items())}


# ===================================================================================================== md
DEVIATIONS = [
    "DV-a (order of reading): before this script's LP-5 integrity phase ran, the Executor read the card, the decision, the correction, "
    "the draft, census.json / census.md / census_scan.py, the cited frozen and preserved source lines, the receipts, and a sample of "
    "RUN-GFPN-ac4487 raw-result.json and solver logs, with shell read tools, to design this script. No solver or other tool child was "
    "started in that preparation. Every reading reported here comes from the final run of this script, after its integrity phase passed.",
    "DV-b (development runs): lp_check.py was developed in the Executor scratchpad and run 5 times there with --out pointing to the "
    "scratchpad (run 1 stopped with a Python exception in LP-1, before writing any output, because it parsed the YAML draft as Python; "
    "runs 2-5 completed). Each development run started the same two read-only git children and no other child; guard blocks 0 in "
    "runs 2-5. The scratch outputs are not deliverables. The deliverables come from one final run of this file in the write_scope.",
    "DV-c (import environment): tempfile.tempdir is pinned to a scratchpad directory before `import v2_solver`, so the module-level "
    "tempfile.gettempdir() (v2_solver.py line 46) probes no directory. The module-level ctypes.CDLL(None) (line 122) loads the "
    "already-mapped C library handle; it starts no process. Both are recorded in LP-2 (v) import.",
    "DV-d (scope of the LP-2 (iv) search): the textual search covers every .py file of implementation-v2, -a1, -r1 and -r2 (the draft's "
    "'frozen, r1 or r2'). The v1 tree and the census tooling are not searched. The two r2 plans are hashed under LP-5 and not otherwise read.",
    "DV-e (method of the 'reads' column): each textual hit is classified by recorded rules (token kind by tokenize; enclosing function "
    "by ast; writer / copy / key-name collection patterns), and a few by recorded manual reading, marked '[manual reading]'. Generic "
    "consumers that never name a key (recursive walkers, strip-based whole-entry comparison) are found by ast and read manually; each "
    "reading is recorded with its call site.",
    "DV-g (second run in the write_scope): the first run of this file in the write_scope completed (integrity 245/245; the same readings), "
    "but its lp_check.py and premise-check.json carried the literal scratchpad path, whose directory name contains a runtime name (LQ-7). "
    "The path was replaced by the --scratch argument and a redacted label, and the file was run again in the write_scope; its outputs "
    "replaced the first run's (nothing had been archived). The first run's three files were kept in the scratchpad and compared with "
    "this run's outputs by the Executor; the comparison is reported in the execution report, not here.",
    "DV-f (supplementary checks): the check also verifies some of the draft's own citations of the reference (raw-result.json lines 736, "
    "747-7062; fx_reg0_raw_x log lines 239-240 and 317-318) and compares each callgrind.stderr 'Command:' line with the recorded primary "
    "argv. These are labelled supplementary and are not LP items.",
]


def render_md():
    o = OUT
    L = ["# Launchcover premise check (TASK-20260924-159c1b)", "",
         "Zero-run, zero-solve premise check for the DRAFT `AMD-EXP-GFPN-05ff43-20260924-launchcover`. It computes the draft's "
         "pre-declared readings (`pre_approval_readings`) LP-5, LP-1, LP-2 (i)-(vii), LP-3 and LP-4 from source code and archived bytes.",
         "",
         "- Ordered by `DEC-20260924-afdc3b`. Archived by `TASK-20260924-0957c2`.",
         "- The draft does not authorize this check (its `authorization` field). The draft is NOT approved.",
         "- **Observations only.** Nothing here is evidence about D, the quotient, `H-GFPN-9a29be` or `HEUR-GFPN-DFLAT`. No D or degree is "
         "reported as a result. No approval recommendation is made.",
         "- No msolve, valgrind, callgrind_annotate, gp, Sage or builder child was started. No run package was created.",
         "- Generated by `lp_check.py` from `premise-check.json`. Both are in this directory.", ""]
    L += ["## Inference", "", "- requested_policy: executor-implementation", "- resolved_model_id: null",
          "- fallback_used: false", "- bedrock_used: false", "- network: not used", ""]
    L += ["## Children and guard (LQ-1)", ""]
    for c in o.get("children_started", []):
        L.append("- child started, phase `%s`, at %s: `%s`" % (c["phase"], c["at"], " ".join(c["argv"])))
    g = o.get("child_launch_guard") or {}
    L.append("- In-process guard installed at %s. Blocked launch attempts: **%d**." % (g.get("installed_at"), len(g.get("blocked_attempts") or [])))
    cl = o.get("closing_checks") or {}
    if cl:
        L.append("- Children of this process from /proc: before the frozen import %s; after it %s; at the end %s." % (
            cl.get("children_before_import"), cl.get("children_after_import"), cl.get("children_at_end")))
    L.append("")
    # integrity
    I = o.get("LP5_integrity") or {}
    L += ["## LP-5: integrity (applied first)", "",
          "Result: **%s** (%s of %s checks equal)." % ("PASS" if I.get("pass") else "FAIL", I.get("n_equal"), I.get("n_checks")), "",
          "| # | check | path | expected sha256 | actual sha256 | equal |", "|---|---|---|---|---|---|"]
    for i, c in enumerate(I.get("checks") or [], 1):
        L.append("| %d | %s | `%s` | `%s` | `%s` | %s |" % (i, c["check"], c["path"], c["expected_sha256"], c["actual_sha256"], c["equal"]))
    L.append("")
    if I.get("informational_b2b59a_bindings"):
        L.append("Informational (not an LP-5 item): the card, decision and correction against the TASK-20260924-b2b59a receipt:")
        for x in I["informational_b2b59a_bindings"]:
            L.append("- `%s` sha256 `%s`; b2b59a path_sha256 `%s`; equal %s" % (x["path"], x["sha256"], x["b2b59a_path_sha256"], x["equal"]))
        L.append("")
    L.append("Git at start (read-only children): HEAD `%s`; `git status --porcelain --untracked-files=all` lines: %d%s" % (
        (o.get("git_at_start") or {}).get("head"), len((o.get("git_at_start") or {}).get("status_porcelain") or []),
        "".join("\n  - `%s`" % s for s in (o.get("git_at_start") or {}).get("status_porcelain") or [])))
    L.append("")
    if o.get("stop"):
        L += ["## STOP", "", "**%s**" % o["stop"], "", "Nothing was read as a result. Under LP-5 the check is INCOMPLETE and is never read.", ""]
        return "\n".join(L) + "\n"
    # LP-1
    P = o["LP1_site_coverage"]
    L += ["## LP-1: site coverage (CG-1 against census.json)", "",
          "Method: %s. Every CG-1 transcription token was checked on its draft line: all present = %s." % (P["method"], P["draft_tokens_all_present"]), "",
          "### Reachable sites", "", "| CG-1 | census site | field | CG-1 | census | equal |", "|---|---|---|---|---|---|"]
    for r in P["reachable"]:
        for k, v in r["fields"].items():
            cv = v.get("census", v.get("census_static", v.get("census_value_verbatim")))
            L.append("| %s | `%s` | %s | %s | %s | %s |" % (r["id"], r["census_site"], k, json.dumps(v.get("CG-1")).replace("|", "/"),
                                                           json.dumps(cv).replace("|", "/"), "not stated in CG-1" if v["equal"] is None else v["equal"]))
    L += ["", "Classification detail (census) for S-3: `%s`" % P["reachable"][2]["fields"]["classified"].get("census_literal_application"), "",
          "Dispositions (informational, not an LP-1 field):"]
    for r in P["reachable"]:
        L.append("- %s: CG-1 `%s`; census wrapped_by `%s`" % (r["id"], r["disposition_informational"]["CG-1"], r["disposition_informational"]["census_wrapped_by"]))
    L += ["", "### Unreachable entries", "", "| CG-1 | census entry | field | CG-1 | census | equal |", "|---|---|---|---|---|---|"]
    for r in P["unreachable"]:
        for k, v in r["fields"].items():
            cv = v.get("census", v.get("census_reached_by_commands", v.get("census_reachable")))
            L.append("| %s | `%s` | %s | %s | %s | %s |" % (r["id"], r["census_entry"], k, json.dumps(v.get("CG-1")).replace("|", "/"),
                                                           json.dumps(cv).replace("|", "/"), "not stated in CG-1" if v["equal"] is None else v["equal"]))
    ll = P["list_level"]
    L += ["", "### List level", "",
          "- Reachable: CG-1 %s; census %s; equal **%s**." % (ll["CG1_reachable_as_census_ids"], ll["census_reachable"], ll["reachable_lists_equal"]),
          "- Census reachable sites classified by the literal definition: %s." % ll["census_reachable_classified_by_literal_definition"],
          "- Unreachable (4 sites + 1 unresolved argv): CG-1 %s; census %s; equal **%s**." % (ll["CG1_unreachable_as_census_ids"], ll["census_unreachable_plus_unresolved"], ll["unreachable_lists_equal"]),
          "- Census counts: %s." % ll["census_counts"], "",
          "### Differences in values CG-1 states: %d" % P["n_differences_in_stated_values"], ""]
    L += ["- %s" % d for d in P["differences"]] or ["- none"]
    L += ["", "### Fields CG-1 does not state: %d" % P["n_fields_not_stated_in_CG1"], ""]
    L += ["- %s" % d for d in P["not_stated_in_CG1"]]
    L += ["", "The census argument-level note on S-3 (census.md lines 281-287; each line checked):"]
    for c in P["census_argument_level_note"]:
        L.append("- line %d present=%s: `%s`" % (c["line"], c["present"], c["token"]))
    L += ["", "### LP-1 reading, as the draft words it", "", "> %s" % P["reading_words_of_the_draft"], "",
          "Values computed for that reading:",
          "- Every value CG-1 states equals census.json: **%s** (%d differences)." % (P["n_differences_in_stated_values"] == 0, P["n_differences_in_stated_values"]),
          "- The site lists are equal: reachable **%s**, unreachable **%s**." % (ll["reachable_lists_equal"], ll["unreachable_lists_equal"]),
          "- CG-1 leaves %d compared fields unstated (listed above). One of these is the S-3 command list: census.json lists 7 static "
          "commands, while the census argument-level note says the child actually runs only in `fixture` and in m <= 4 `cells`. The draft does "
          "not say whether an unstated field counts as \"not equal\". This check does not decide that. The approval act rules on it." % P["n_fields_not_stated_in_CG1"], ""]
    # LP-2
    Q = o["LP2_callgrind_site_facts"]
    L += ["## LP-2: callgrind-site facts", ""]
    for key, title in (("i", "(i) v2_driver.solve launch condition, record and output removal"), ("ii", "(ii) the r2 SE-3 wrapper passes callgrind_timeout unchanged"),
                       ("iii", "(iii) callgrind log files, argv, removals"), ("v", "(v) parse_msolve_log names")):
        q = Q[key]
        L += ["### %s" % title, "", "Confirmed (every citation present and the ast checks as stated): **%s**" % q.get("confirmed", q.get("all_citations_present")), ""]
        for c in q["citations"]:
            L.append("- `%s` line %d present=%s: `%s`" % (os.path.basename(c["file"]), c["line"], c["present"], c["token"]))
        if key == "i":
            a = q["ast"]
            L += ["- ast: the only `res[\"instructions_callgrind\"]` store in solve is at line(s) %s. Other subscripts: %s. Constant lines: %s." % (
                [x["line"] for x in a["instructions_callgrind_subscript_stores_in_solve"]], a["instructions_callgrind_other_subscripts_in_solve"], a["instructions_callgrind_constant_lines_in_solve"]),
                  "- ast: `res.update` with outcome/reason/D/solutions at lines %s, all before 207." % a["res.update_with_outcome_reason_D_solutions_lines"],
                  "- ast: callgrind calls in solve: %s. `cg_out` uses: %s." % (a["callgrind_calls_in_solve"], [(x["line"], x["ctx"]) for x in a["cg_out_name_uses_in_solve"]]),
                  "- ast: calls passing `cg_out` other than msolve_argv / os.remove: %s. `open()` calls in callgrind_instructions: %s." % (
                      a["calls_passing_cg_out_other_than_msolve_argv_and_os.remove"], a["open_calls_in_callgrind_instructions"])]
            L += ["- note: %s" % n for n in q["notes"]]
        if key == "ii":
            a = q["ast"]
            L += ["- ast: kwargs assignments %s; kwargs mutations %s; `_call_original` calls %s." % (a["kwargs_assignments"], a["kwargs_mutations"], [(x["line"], x["src"]) for x in a["_call_original_calls"]]),
                  "- ssf_clause returns: %s." % [(x["line"], x["src"]) for x in a["ssf_clause_returns"]]]
            L += ["- %s" % d for d in q["derivation"]]
        if key == "iii":
            L += ["- msolve_argv calls in solve: %s." % q["msolve_argv_calls_in_solve"],
                  "- Callgrind msolve argv equals the primary argv except for the output path: **%s**." % q["callgrind_msolve_argv_equals_primary_except_output_path"],
                  "- Remove / rename / move calls in the scanned trees: %d (unreviewed: %d)." % (q["n_remove_rename_calls"], len(q["unreviewed_calls"])), "",
                  "| file | line | function | call | target (manual reading) |", "|---|---|---|---|---|"]
            for x in q["remove_rename_calls_in_scanned_trees"]:
                L.append("| `%s` | %d | %s | `%s` | %s |" % (x["file"].split("/", 2)[-1], x["line"], x["function"], x["call"].replace("|", "/")[:90], x["target_manual_reading"]))
            L += [""] + ["- note: %s" % n for n in q["notes"]]
        if key == "v":
            L += ["- %s: %s" % (k, v) for k, v in q["names_returned"].items()]
            L += ["- note: %s" % q["note"], "- synthetic call (pure regex, no solver): %s" % json.dumps(q.get("synthetic_call"))]
        L.append("")
    iv = Q["iv"]
    L += ["### (iv) instructions_callgrind key set, REG-1-compared subset, readers", "",
          "Confirmed as the draft states it: **%s**" % iv["confirmed"], "",
          "- Top-level keys (v2_solver.py 519-547): %s" % ", ".join("%s (line %s)" % (k["key"], k["lines"]) for k in iv["key_set"]["top_level"]),
          "- child mapping keys (line 519): %s" % ", ".join(iv["key_set"]["child_mapping"]),
          "- note: %s" % iv["key_set"]["note"],
          "- X14-X17 (reg1-exclusion-list.json lines 35-42): %s. Exclusions naming instructions_callgrind: %s." % (
              "; ".join("%s %s" % (e["id"], "/".join(e["path"])) for e in iv["exclusions_X14_X17"]), iv["exclusions_naming_instructions_callgrind"]),
          "- Exclusion line citations: %s" % ", ".join("line %d present=%s" % (c["line"], c["present"]) for c in iv["exclusion_line_citations"]),
          "- REG-1-compared subset: top level %s; child %s." % (iv["reg1_compared_subset"]["top_level"], iv["reg1_compared_subset"]["child_mapping"]),
          "", "**Discrepancies with the draft's statement \"no frozen, r1 or r2 function other than r2_reg1.compare reads instructions_callgrind or any of its keys\":**", ""]
    L += ["- %s" % d for d in iv["discrepancies"]] or ["- none"]
    ts = iv["textual_search"]
    L += ["", "Textual search: keys %s; %d files in %s; **%d hits**, by class %s. Every hit is listed below, with its enclosing function and whether it "
          "reads an instructions_callgrind value." % (ts["keys_searched"], ts["n_files"], ts["trees"], ts["n_hits"], ts["hits_by_class"]), ""]
    L += ["Classes: READS = reads a value of an instructions_callgrind record; copy = copies the whole record into a recorded row; "
          "writer = builds or stores the record; no = the accessed object is not an instructions_callgrind record (the reason is given per hit in "
          "premise-check.json).", ""]
    L += ["| file | line | key | token | function | reads |", "|---|---|---|---|---|---|"]
    for h in ts["hits"]:
        L.append("| `%s` | %d | %s | %s | %s | %s |" % (h["file"].split("/", 2)[-1], h["line"], h["key"], h["token_kind"], h["function"], h["reads_instructions_callgrind_value"]))
    gc = iv["generic_consumers"]
    L += ["", "Generic (non-textual) consumers, found by ast (recursive walkers and their call sites, and whole-entry `strip` comparisons):", "",
          "- r2_reg1.py names instructions_callgrind textually: %s. r1_reg1.py: %s. (REG-1 reads it through whole-entry comparison.)" % (
              gc["r2_reg1_names_instructions_callgrind_textually"], gc["r1_reg1_names_instructions_callgrind_textually"]),
          "- recursive walkers: %s" % ", ".join("%s:%d %s" % (w["file"].split("/")[-1], w["line"], w["function"]) for w in gc["recursive_walkers"]), "",
          "| file | line | function | call | reading |", "|---|---|---|---|---|"]
    for w in gc["walker_and_strip_call_sites"]:
        L.append("| `%s` | %d | %s | `%s` | %s |" % (w["file"].split("/", 2)[-1], w["line"], w["function"], w["call"].replace("|", "/")[:80], w["manual_reading"]))
    for x in gc["other"]:
        L.append("| `%s` | %d | %s | - | %s (citations present: %s) |" % (x["file"].split("/", 2)[-1], x["line"], x["function"], x["reading"],
                                                                       all(c["present"] for c in x["citations"])))
    L.append("")
    # vi / vii
    R = Q["vi_vii"]
    L += ["### (vi) THE REFERENCE: RUN-GFPN-ac4487 entries carrying instructions_callgrind", "",
          "- Count: **%d**. Paths of instructions_callgrind anywhere in raw-result.json: %d (all under targets / planted_targets arms)." % (R["n_entries"], len(R["instructions_callgrind_paths_anywhere_in_raw_result"])),
          "- Sum of child.wall_seconds: %s s. All retained files present: %s." % (R["sum_child_wall_seconds"], R["all_retained_present"]),
          "- Entries with any anomaly the draft names (non-ok child, reason, f4_core_note, null f4_core_function, log-visible SSF indicator, "
          "quotient-dimension disagreement): %s" % (R["entries_with_anomalies"] or "none"), "",
          "| # | list | idx | tag | method | label | child.outcome | child.returncode | child.rlimit_as_child_getrlimit | reason | f4_core_function | f4_core_note | child.wall_seconds | .ms sha256 | .callgrind.stdout sha256 | .callgrind.stderr sha256 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, e in enumerate(R["entries"], 1):
        c = e["reg1_compared_fields_verbatim"]
        ch = c.get("child", {})
        r_ = e["retained"]
        L.append("| %d | %s | %d | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, e["target_list"], e["index"], e["tag"], c.get("method"), c.get("label"), ch.get("outcome"), ch.get("returncode"),
            json.dumps(ch.get("rlimit_as_child_getrlimit")), c.get("reason", "(absent)"), c.get("f4_core_function", "(absent)"),
            c.get("f4_core_note", "(absent)"), e["child_wall_seconds"],
            *(("`%s`" % r_[k]["sha256"]) if isinstance(r_[k], dict) else "absent" for k in ("solver/<tag>.ms", "<tag>.callgrind.stdout", "<tag>.callgrind.stderr"))))
    L += ["", "The REG-1-compared fields of every entry are also given verbatim as JSON in premise-check.json (`LP2_callgrind_site_facts.vi_vii.entries[*].reg1_compared_fields_verbatim`).",
          "Per entry: tag = `fx_<target>_<arm>` (v2_driver.py line 344); it equals the recorded argv input for %d of %d entries. The retained .ms sha256 equals the recorded input sha256 for %d of %d." % (
              sum(e["tag_matches_recorded_argv_input"] for e in R["entries"]), R["n_entries"],
              sum(e["retained_ms_sha256_equals_recorded_input_sha256"] for e in R["entries"]), R["n_entries"]), "",
          "### (vii) THE ARCHIVED LOGS (zero-solve readings, frozen parse_msolve_log)", "",
          "| tag | cg dim | cg sqfree | cg posdim | cg random-form | cg SSF ind. | pr dim | pr sqfree | pr posdim | pr random-form | pr SSF ind. | dims agree | cg dim = recorded | cg Command = primary argv (cg out) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in R["entries"]:
        cg, pr = e["log_readings"]["callgrind"], e["log_readings"]["primary"]
        L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            e["tag"], cg.get("printed_quotient_dimension"), cg.get("squarefree_degree"), cg.get("positive_dimension_reported"), cg.get("random_form_string_present"),
            cg.get("log_visible_ssf_indicator"), pr.get("printed_quotient_dimension"), pr.get("squarefree_degree"), pr.get("positive_dimension_reported"),
            pr.get("random_form_string_present"), pr.get("log_visible_ssf_indicator"), e["printed_quotient_dimensions_agree"],
            e["callgrind_printed_dimension_equals_recorded_dimension_of_quotient_printed"], cg.get("command_equals_recorded_primary_argv_with_cg_output_path")))
    L += ["", "Printed quotient dimensions are log readings of archived harness bytes, reported only as the LP-2 (vii) comparison "
          "fields. They are not reported as a result about D.", "",
          "Distinct linear-form lines seen in the logs: %s" % sorted({x for e in R["entries"] for p in ("callgrind", "primary") for x in e["log_readings"][p].get("linear_form_lines", [])}), ""]
    S = R["supplementary_draft_citation_checks"]
    L += ["Supplementary checks of the draft's own citations of the reference (not LP items):",
          "- `\"f4_core_function\"` lines in raw-result.json: %d, first line %s, last line %s; distinct values %s." % (
              S["f4_core_function_lines_in_raw_result"]["n"], S["f4_core_function_lines_in_raw_result"]["first"], S["f4_core_function_lines_in_raw_result"]["last"],
              S["f4_core_function_lines_in_raw_result"]["distinct_values"]),
          "- raw-result.json line 736: `%s`" % S["raw_result_line_736"].strip(),
          "- fx_reg0_raw_x.callgrind.stdout vs .ms.log at lines 239, 240, 317, 318: equal %s; whole files equal line by line: %s." % (
              {k: v["equal"] for k, v in S["fx_reg0_raw_x_stdout_vs_ms_log"].items()}, S["fx_reg0_raw_x_stdout_equals_ms_log_whole"]),
          "- fx_reg0_raw_x line counts %s; %d line numbers differ: %s. Equal after masking every decimal number (d.d) and collapsing whitespace runs: %s. Not an LP item." % (
              S["fx_reg0_raw_x_line_counts"], len(S["fx_reg0_raw_x_differing_line_numbers"]), S["fx_reg0_raw_x_differing_line_numbers"],
              S["fx_reg0_raw_x_equal_after_masking_decimal_numbers_and_whitespace_runs"]), ""]
    L += ["### LP-2 reading, as the draft words it", "",
          "> a discrepancy in (i), (ii), (iii) or (iv) makes this draft NOT approvable as written, because CG-2..CG-6 rest on them. [...] "
          "(v), (vi) and (vii) are ruled on by the approval act. (draft lines 642-650)", "",
          "Values computed for that reading:",
          "- (i) confirmed: **%s**" % Q["i"]["confirmed"], "- (ii) confirmed: **%s**" % Q["ii"]["confirmed"],
          "- (iii) confirmed: **%s**" % Q["iii"]["confirmed"], "- (iv) confirmed as stated: **%s** (%d discrepancies named above)" % (iv["confirmed"], len(iv["discrepancies"])),
          "- (v), (vi), (vii): reported above for the approval act.", ""]
    # LP-3, LP-4
    T = o["LP3_DV17_feasibility"]
    L += ["## LP-3: DV-17 feasibility (%s)" % T["label"], "",
          "- R = %d (fixed by CG-5 (d)); N_ref = %d; sum of reference child.wall_seconds = %s s." % (T["R"], T["N_ref"], T["sum_reference_child_wall_seconds"]),
          "- Bound 1, %s = %s s (%s h): R x sum = %s s, spacing = %s s." % (T["bound_1_formula"], T["bound_1_R_x_sum_plus_spacing_s"], T["bound_1_hours"],
                                                                            T["bound_1_parts"]["R_x_sum"], T["bound_1_parts"]["spacing"]),
          "- Bound 2, worst case %s = %s s (%s h), with callgrind_timeout_s.m3 = %s s from trial-plan-v2.json." % (T["bound_2_formula"], T["bound_2_worst_case_s"], T["bound_2_hours"], T["callgrind_timeout_s_m3"]),
          "- These are derived, never measured. The reference wall seconds were recorded on the reference host at RUN-GFPN-ac4487.", ""]
    U = o["LP4_environment"]
    L += ["## LP-4: environment (%s)" % U["label"], ""]
    for k, v in U["which"].items():
        L.append("- `shutil.which(%r)` = `%s` (realpath `%s`)" % (k, v["shutil.which"], v["realpath"]))
    for k, v in U["frozen_constants"].items():
        L.append("- %s = `%s`; exists %s; realpath `%s`" % (k, v, U["frozen_constants_stat"][k]["exists"], U["frozen_constants_stat"][k]["realpath"]))
    L.append("- callgrind_annotate: %s. PATH at check time: `%s`" % (U["callgrind_annotate_lookup"], U["PATH"]))
    L.append("- RUN-GFPN-ac4487 environment.json, verbatim:")
    for k, v in U["RUN-GFPN-ac4487_environment_json_verbatim"].items():
        L.append("  - `%s` = `%s`" % (k, v))
    L.append("- environment.json records callgrind_annotate: %s" % U["environment_json_records_callgrind_annotate"])
    L.append("")
    # closing + deviations
    L += ["## Closing checks", ""]
    for k, v in (o.get("closing_checks") or {}).items():
        L.append("- %s: %s" % (k, json.dumps(v)[:600]))
    L += ["", "## Deviations", ""]
    L += ["- %s" % d for d in (o.get("deviations") or [])] or ["- none"]
    L += ["", "## Files read", "", "%d files read, each with its sha256 in premise-check.json (`files_read`). Every one is bound by a receipt checked under LP-5, except the "
          "receipts themselves (hashed in `receipts_used`) and the informational ledger records." % len(o.get("files_read") or {}), ""]
    return "\n".join(L) + "\n"


# ===================================================================================================== main
def main():
    I = integrity()
    OUT["LP5_integrity"] = I
    if not I["pass"]:
        OUT["child_launch_guard"] = {"installed_at": None, "blocked_attempts": [], "note": "not installed: stopped at integrity"}
        OUT["deviations"] = DEVIATIONS
        write_outputs(stop="LQ-2 / LP-5 integrity failed; the check stopped before any reading (INCOMPLETE)")
        print("STOP: integrity failed", file=sys.stderr)
        return 3
    install_guard()
    OUT["child_launch_guard"] = GUARD
    tl = tree_files()
    OUT["LP1_site_coverage"] = lp1()
    Q = {"i": lp2_i(), "ii": lp2_ii(), "iii": lp2_iii(tl), "iv": lp2_iv(tl), "v": lp2_v()}
    # the one frozen import: v2_solver (parse_msolve_log). ast pre-check of its module-level statements first.
    modlevel = []
    for st in src(SOL)["tree"].body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) or (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant)):
            continue
        calls = sorted({ast.unparse(n.func) for n in ast.walk(st) if isinstance(n, ast.Call)})
        modlevel.append({"line": st.lineno, "stmt": ast.unparse(st)[:160], "calls": calls})
    import tempfile
    if not SCRATCH_TMP or os.path.abspath(SCRATCH_TMP).startswith(REPO):
        raise SystemExit("--scratch DIR outside the repository is required")
    os.makedirs(SCRATCH_TMP, exist_ok=True)
    tempfile.tempdir = SCRATCH_TMP                       # gettempdir() then returns this without probing any directory
    pyc_before = sorted(glob.glob(ab(EXP) + "/implementation-v2*/**/__pycache__", recursive=True))
    kids_before = children_now()
    sys.path.insert(0, ab(V2))
    import v2_solver as V                                  # noqa: E402
    kids_after = children_now()
    imported = {m: getattr(sys.modules[m], "__file__", None) for m in sorted(sys.modules) if m.startswith(("v2_", "a1_", "r1_", "r2_"))}
    Q["v"]["import"] = {"module_level_statements_with_calls": [m for m in modlevel if m["calls"]], "all_module_level_statements": modlevel,
                        "tempfile.tempdir_pinned_to": SCRATCH_LABEL, "imported_repo_modules": imported,
                        "v2_solver_file_sha256": hashlib.sha256(open(V.__file__, "rb").read()).hexdigest(),
                        "v2_solver_file_equals_LP5_hash": hashlib.sha256(open(V.__file__, "rb").read()).hexdigest() == HASHES.get(SOL),
                        "parse_msolve_log_code_file": V.parse_msolve_log.__code__.co_filename,
                        "parse_msolve_log_firstlineno": V.parse_msolve_log.__code__.co_firstlineno,
                        "children_before": kids_before, "children_after": kids_after,
                        "guard_blocked_attempts_after_import": len(GUARD["blocked_attempts"])}
    syn = "Dimension of quotient: 7\nDegree of the square-free part: 6\npositive dimension\n"
    st = V.parse_msolve_log(syn)
    Q["v"]["synthetic_call"] = {"text": syn, "dimension_of_quotient": st["dimension_of_quotient"], "fglm.squarefree_degree": st["fglm"].get("squarefree_degree"),
                                "positive_dimension_reported": st["positive_dimension_reported"], "ssf_indicator_on_it": ssf_indicator(st, syn),
                                "empty_text": {"dimension_of_quotient": V.parse_msolve_log("")["dimension_of_quotient"],
                                               "fglm_keys": sorted(V.parse_msolve_log("")["fglm"]), "positive_dimension_reported": V.parse_msolve_log("")["positive_dimension_reported"]}}
    Q["v"]["confirmed"] = (Q["v"]["all_citations_present"] and st["dimension_of_quotient"] == 7 and st["fglm"].get("squarefree_degree") == 6
                           and st["positive_dimension_reported"] is True)
    Q["vi_vii"] = lp2_vi_vii(V)
    OUT["LP2_callgrind_site_facts"] = Q
    plan = json.load(open(ab(PLAN_V2)))
    OUT["files_read"][PLAN_V2] = HASHES[PLAN_V2]
    OUT["LP3_DV17_feasibility"] = lp3(Q["vi_vii"], R=10, timeout=plan["watchdogs"]["callgrind_timeout_s"]["m3"])
    OUT["LP4_environment"] = lp4(V)
    # closing
    changed = [r for r, h in HASHES.items() if hashlib.sha256(open(ab(r), "rb").read()).hexdigest() != h]
    pyc_after = sorted(glob.glob(ab(EXP) + "/implementation-v2*/**/__pycache__", recursive=True))
    pyc_files = sorted(glob.glob(ab(EXP) + "/implementation-v2*/**/*.pyc", recursive=True))
    OUT["closing_checks"] = {"bound_files_rehashed": len(HASHES), "bound_files_changed": changed,
                             "pycache_dirs_under_implementation_v2_trees_before_import": [os.path.relpath(p, REPO) for p in pyc_before],
                             "pycache_dirs_under_implementation_v2_trees_at_end": [os.path.relpath(p, REPO) for p in pyc_after],
                             "pyc_files_under_implementation_v2_trees_at_end": [os.path.relpath(p, REPO) for p in pyc_files],
                             "children_before_import": kids_before, "children_after_import": kids_after, "children_at_end": children_now(),
                             "guard_blocked_attempts": len(GUARD["blocked_attempts"]),
                             "scratch_tmp_contents_at_end": sorted(os.listdir(SCRATCH_TMP)),
                             "files_read_not_checked_under_LP5": sorted(r for r in OUT["files_read"] if r not in {c["path"] for c in I["checks"]})}
    OUT["deviations"] = DEVIATIONS
    OUT["inference"] = {"requested_policy": "executor-implementation", "resolved_model_id": None, "fallback_used": False, "bedrock_used": False}
    write_outputs()
    print("integrity %s (%d/%d); LP-1 differences %d, unstated %d; LP-2 i %s ii %s iii %s iv %s (%d discrepancies) v %s; N_ref %d; guard blocks %d" % (
        I["pass"], I["n_equal"], I["n_checks"], OUT["LP1_site_coverage"]["n_differences_in_stated_values"], OUT["LP1_site_coverage"]["n_fields_not_stated_in_CG1"],
        Q["i"]["confirmed"], Q["ii"]["confirmed"], Q["iii"]["confirmed"], Q["iv"]["confirmed"], len(Q["iv"]["discrepancies"]), Q["v"]["confirmed"],
        Q["vi_vii"]["n_entries"], len(GUARD["blocked_attempts"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
