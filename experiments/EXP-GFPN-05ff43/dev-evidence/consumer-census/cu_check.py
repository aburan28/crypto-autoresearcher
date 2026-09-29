#!/usr/bin/env python3
"""TASK-20260924-5dfbfd -- ZERO-RUN, ZERO-SOLVE CONSUMER CENSUS for the DRAFT
AMD-EXP-GFPN-05ff43-20260924-consumercover (pre_approval_readings: definitions, CU-5, CU-1, CU-2, CU-4).

usage: python3 -B cu_check.py                 # the census, as run (writes consumer-census.json / .md)
       python3 -B cu_check.py --integrity-only # hash checks only; starts no child, writes nothing

Order (KQ-2, KQ-1):
  1. INTEGRITY (CU-5) first: hash checks (a)-(d). Any failure writes consumer-census.json / .md with the failure and
     stops before any reading. The only child processes this script starts are read-only git children in this
     phase, each listed with its argv (rev-parse, ls-files, cat-file).
  2. An in-process guard then replaces os.fork / os.posix_spawn / os.exec* / os.spawn* / os.system / os.popen /
     subprocess.Popen by functions that raise and record the attempt. No child can start after this point.
  3. CU-1, CU-2 (a)-(d) and CU-4 are computed STATICALLY: ast and tokenize over the source of the scanned files, text
     reads of archived files. NO module of any scanned tree is imported (not even the earlier dev-evidence scripts).
  4. Closing: every bound file re-hashed; no byte code written; no scanned-tree module in sys.modules; children of
     this process from /proc.
Observations only. Decides nothing. No msolve, valgrind, callgrind_annotate, gp, Sage or builder child.
"""
import ast
import datetime
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tokenize

sys.dont_write_bytecode = True

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
EXP = "experiments/EXP-GFPN-05ff43"
TASK = "TASK-20260924-5dfbfd"
OUT_DIR_REL = EXP + "/dev-evidence/consumer-census"
INTEGRITY_ONLY = "--integrity-only" in sys.argv

ARCH = "coordination/goals/GOAL-GFPN-380702/archives"
RC_A28 = ARCH + "/TASK-20260924-a28f0e/snapshot-receipt.json"
RC_C65 = ARCH + "/TASK-20260924-c65bfb/snapshot-receipt.json"
RC_095 = ARCH + "/TASK-20260924-0957c2/snapshot-receipt.json"
RC_0FA_A = ARCH + "/TASK-20260923-0fa03f/snapshot-receipt.json"
RC_4FF = ARCH + "/TASK-20260923-4ff597/snapshot-receipt.json"
RC_53A = ARCH + "/TASK-20260923-53a47d/preservation-receipt.json"
RC_5CA = ARCH + "/TASK-20260924-5ca2a5/preservation-receipt.json"
RECEIPTS = (RC_A28, RC_C65, RC_095, RC_0FA_A, RC_4FF, RC_53A, RC_5CA)

CONSUMERCOVER = EXP + "/amendments/v2_addendum_consumercover.yaml"
LAUNCHCOVER = EXP + "/amendments/v2_addendum_launchcover.yaml"
HEALTH = EXP + "/amendments/v2_addendum_healthresolve.yaml"
SEED = EXP + "/amendments/v2_addendum_seedresolve.yaml"
SOLVEREVENT = EXP + "/amendments/v2_addendum_solverevent.yaml"
CARD_DRAFT_HASHES = {LAUNCHCOVER: "c27ffe5c15d13d1c1137bdba11944ac53f0e91c79d8f460a5d2b18066ca5f447",
                     HEALTH: "ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d",
                     SEED: "dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81",
                     SOLVEREVENT: "011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f"}
CENSUS_DIR = EXP + "/dev-evidence/launch-census"
CENSUS_FILES = [CENSUS_DIR + "/census.md", CENSUS_DIR + "/census.json", CENSUS_DIR + "/census_scan.py"]
PREMISE_DIR = EXP + "/dev-evidence/launchcover-premise"
PREMISE_FILES = [PREMISE_DIR + "/premise-check.md", PREMISE_DIR + "/premise-check.json", PREMISE_DIR + "/lp_check.py"]
PREMISE_CARD_FRAGMENTS = {PREMISE_DIR + "/premise-check.md": ("807409ad", "c452"),
                          PREMISE_DIR + "/premise-check.json": ("caf24d66", "f187"),
                          PREMISE_DIR + "/lp_check.py": ("f386c863", "0b5c")}
V1, V2, A1, R1, R2 = (EXP + "/implementation", EXP + "/implementation-v2", EXP + "/implementation-v2-a1",
                      EXP + "/implementation-v2-r1", EXP + "/implementation-v2-r2")
TREES = {"v1": V1, "v2": V2, "a1": A1, "r1": R1, "r2": R2}
TREE_RECEIPT = {"v2": RC_0FA_A, "a1": RC_4FF, "r1": RC_53A, "r2": RC_5CA}
PLAN_V2_R2, PLAN_A1_R2 = EXP + "/trial-plan-v2-r2.json", EXP + "/trial-plan-v2-a1-r2.json"
EXCL_R1, EXCL_R2 = R1 + "/reg1-exclusion-list.json", R2 + "/reg1-exclusion-list.json"
V1_VALUES_SOURCE = (CENSUS_DIR + "/census.md", 152, 183)
REPO_TOOL_DIRS = ("tools", "harness", "orchestration")
RUN_PACKAGE_FILES = ("raw-result.json", "manifest.yaml", "solver-events.json")
INFO_FILES = ["ledger/handoffs/TASK-20260924-5dfbfd.yaml", "ledger/decisions/DEC-20260924-a7453e.yaml",
              "ledger/corrections/CORR-20260924-e78b7a.yaml", "ledger/decisions/DEC-20260924-afdc3b.yaml"]
GUARD_THRESHOLD_NOTE = ("dispatcher's declared memory guard (DP-4): if MemAvailable drops below 2621440 kB (2.5 GiB) it kills the "
                        "largest-RSS msolve, gp or python3 process; not part of this script")

OUT = {"schema": "crypto.autoresearch.gfpn05.consumer_census.v1", "task_id": TASK, "experiment_id": "EXP-GFPN-05ff43",
       "draft_defining_the_readings": "AMD-EXP-GFPN-05ff43-20260924-consumercover (DRAFT, not approved), pre_approval_readings",
       "authority": "DEC-20260924-a7453e (the draft authorizes nothing)", "archived_by": "TASK-20260924-ad3f9a",
       "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "children_started": [], "files_read": {}}
HASHES = {}
DEVIATIONS = []


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ab(rel):
    return os.path.join(REPO, rel)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(rel):
    h = sha_bytes(open(ab(rel), "rb").read())
    HASHES[rel] = h
    return h


def git(args, stdin=None):
    argv = ["git", "-C", "<repository root>"] + list(args)
    OUT["children_started"].append({"argv": argv, "phase": "integrity", "at": now(),
                                    "stdin": None if stdin is None else "%d lines (object names HEAD:<path>)" % stdin.count("\n")})
    real = ["git", "-C", REPO] + list(args)
    r = subprocess.run(real, input=stdin.encode() if stdin is not None else None, capture_output=True, timeout=120)
    return r.stdout


def load_json(rel):
    return json.load(open(ab(rel)))


# ===================================================================================================== 1. INTEGRITY
def tree_py_files(tree_rel):
    return sorted(os.path.relpath(f, REPO) for f in glob.glob(ab(tree_rel) + "/*.py"))


def v1_recorded_values():
    """census.md lines 152-183: the table rows '| `path` | `sha` | tracked | ... |'."""
    rel, a, z = V1_VALUES_SOURCE
    lines = open(ab(rel)).read().splitlines()[a - 1:z]
    vals = {}
    for n, L in enumerate(lines, start=a):
        m = re.match(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|", L)
        if m:
            vals[m.group(1)] = {"sha256": m.group(2), "census_md_line": n}
    return vals


def integrity(run_git=True):
    checks = []
    abbrev = []

    def chk(name, rel, expected, source):
        actual = sha(rel) if os.path.exists(ab(rel)) else None
        checks.append({"check": name, "path": rel, "expected_sha256": expected, "actual_sha256": actual,
                       "expected_from": source, "equal": actual is not None and expected is not None and actual == expected})

    receipts = {}
    for rc in RECEIPTS:
        receipts[rc] = sha(rc)
    a28 = load_json(RC_A28)
    # (a)
    chk("(a) consumercover draft == TASK-20260924-a28f0e addendum_sha256.sha256", CONSUMERCOVER, a28["addendum_sha256"]["sha256"],
        RC_A28 + " addendum_sha256.sha256")
    chk("(a') consumercover draft == TASK-20260924-a28f0e path_sha256", CONSUMERCOVER, a28["path_sha256"].get(CONSUMERCOVER), RC_A28 + " path_sha256")
    # (b)
    for rel, h in CARD_DRAFT_HASHES.items():
        chk("(b) %s == card KQ-2 (b) value" % os.path.basename(rel), rel, h, "card KQ-2 (b)")
    # (c)
    c65 = load_json(RC_C65)["path_sha256"]
    for rel in CENSUS_FILES:
        chk("(c) %s == TASK-20260924-c65bfb path_sha256" % os.path.basename(rel), rel, c65.get(rel), RC_C65 + " path_sha256")
    p95 = load_json(RC_095)["path_sha256"]
    for rel in PREMISE_FILES:
        chk("(c) %s == TASK-20260924-0957c2 path_sha256" % os.path.basename(rel), rel, p95.get(rel), RC_095 + " path_sha256")
        a, z = PREMISE_CARD_FRAGMENTS[rel]
        v = p95.get(rel) or ""
        abbrev.append({"check": "card KQ-2 (c) parenthetical abbreviation %s...%s of %s (prefix/suffix of the receipt value)" % (a, z, os.path.basename(rel)),
                       "path": rel, "card_abbreviation": "%s...%s" % (a, z), "receipt_value": v,
                       "prefix_matches": v.startswith(a), "suffix_matches": v.endswith(z),
                       "note": ("informational, not a KQ-2 (c) item: KQ-2 (c) binds the file to the receipt path_sha256; the card "
                                "quotes that value abbreviated in parentheses")})
    # (d) every implementation file read: every *.py of the five trees, both reg1 exclusion lists, both r2 plans
    for key in ("v2", "a1", "r1", "r2"):
        bound = load_json(TREE_RECEIPT[key])["path_sha256"]
        tid = TREE_RECEIPT[key].split("/")[-2]
        for rel in tree_py_files(TREES[key]):
            chk("(d) %s file == %s receipt" % (key, tid), rel, bound.get(rel), TREE_RECEIPT[key] + " path_sha256")
    b53 = load_json(RC_53A)["path_sha256"]
    b5c = load_json(RC_5CA)["path_sha256"]
    chk("(d) r1 reg1-exclusion-list.json == TASK-20260923-53a47d receipt", EXCL_R1, b53.get(EXCL_R1), RC_53A + " path_sha256")
    chk("(d) r2 reg1-exclusion-list.json == TASK-20260924-5ca2a5 receipt", EXCL_R2, b5c.get(EXCL_R2), RC_5CA + " path_sha256")
    for rel in (PLAN_V2_R2, PLAN_A1_R2):
        chk("(d) %s == TASK-20260924-5ca2a5 receipt" % os.path.basename(rel), rel, b5c.get(rel), RC_5CA + " path_sha256")
    v1vals = v1_recorded_values()
    for rel in tree_py_files(V1):
        rv = v1vals.get(rel)
        chk("(d) v1 file == census.md line %s" % (rv["census_md_line"] if rv else "NONE"), rel, rv["sha256"] if rv else None,
            "%s lines %d-%d" % V1_VALUES_SOURCE)
    info = []
    for rel in INFO_FILES:
        got = sha(rel)
        want = a28["path_sha256"].get(rel)
        info.append({"path": rel, "sha256": got, "a28f0e_path_sha256": want, "equal_if_bound": (want == got) if want else None})
    res = {"checks": checks, "n_checks": len(checks), "n_equal": sum(1 for c in checks if c["equal"]),
           "pass": all(c["equal"] for c in checks), "receipts_used_sha256": receipts, "card_abbreviation_checks": abbrev, "informational_bindings": info,
           "addendum_block_in_receipt": a28["addendum_sha256"]}
    if run_git and res["pass"]:
        res["git"] = git_state()
    return res


def git_blob_sha1(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def git_state():
    """Read-only git children (integrity phase only): HEAD, the repo's modified/deleted/untracked list, and the HEAD
    bytes of every tracked .py under tools/, harness/, orchestration/ and the five scanned trees (one cat-file --batch)."""
    head = git(["rev-parse", "HEAD"]).decode().strip()
    dirty = git(["ls-files", "--modified", "--deleted", "--others", "--exclude-standard"]).decode().splitlines()
    tracked = git(["ls-files", "--"] + list(REPO_TOOL_DIRS) + [TREES[k] for k in TREES]).decode().splitlines()
    tracked_py = sorted(p for p in tracked if p.endswith(".py"))
    req = "".join("HEAD:%s\n" % p for p in tracked_py)
    blob = git(["cat-file", "--batch"], stdin=req)
    head_sha = {}
    i = 0
    for p in tracked_py:
        nl = blob.index(b"\n", i)
        hdr = blob[i:nl].decode().split()
        if len(hdr) < 3 or hdr[1] != "blob":
            head_sha[p] = None
            i = nl + 1
            continue
        size = int(hdr[2])
        body = blob[nl + 1: nl + 1 + size]
        head_sha[p] = {"sha256": sha_bytes(body), "git_blob": hdr[0]}
        i = nl + 1 + size + 1
    scope_dirty = sorted(p for p in dirty if p.startswith(tuple(list(REPO_TOOL_DIRS) + [EXP])))
    return {"head": head, "repo_dirty_paths_count": len(dirty),
            "repo_dirty_paths_under_scanned_or_experiment_dirs": scope_dirty,
            "repo_dirty_paths_note": ("git ls-files --modified --deleted --others --exclude-standard: working tree vs index; the "
                                      "HEAD bytes of every scanned .py are compared below"),
            "head_py": head_sha, "n_tracked_py_in_scope": len(tracked_py)}


# ===================================================================================================== 2. GUARD
GUARD = {"installed_at": None, "blocked_attempts": []}


def _blocked(name):
    def f(*a, **k):
        GUARD["blocked_attempts"].append({"call": name, "args": repr(a)[:200], "at": now()})
        raise RuntimeError("consumer-census guard: child launch %s refused (KQ-1)" % name)
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
    return kids




# ===================================================================================================== 3. STATIC ENGINE
# Access-path taint over the ast. A TAG is (origin, path, via, full, ser):
#   origin  what the value is: "S1" (a solve() result), "S1/solver", "S1/f:<field>", "S3" (the callgrind record),
#           "S3/child", "S3/f:<field>", "S2" (a run_system record), "S2/child", "S2/f:<field>", "<site>/childrec" (the
#           raw run_child record inside a frozen producer), "<site>/file:<suffix>" (a file the site leaves), and
#           "C4:<file>:<line>" (a non-msolve child record, CU-4);
#   path    where, inside the value held, the tainted datum sits ((), the value itself; "[]" a list element; "*" any key);
#   via     "" for the site value itself (returned, passed, held), else the DERIVED VALUE it was stored into
#           ("mem:<function>:<variable>", "file:<name>", or a named marker);
#   full    the path of the datum inside that derived value, recorded when it was stored;
#   ser     True when the value is a serialization (json.dumps / str / repr) of the tainted structure.
SITE_OF = {"S1": "S-1", "S2": "S-2", "S3": "S-3"}
WILD = "~wildcard"          # marks a tag that passed through a computed-key / wildcard-path match (over-approximation)
SITE_FILE_SUFFIXES = [(".ssf-attempt", "S1", "renamed attempt file <tag>.ms.*.ssf-attempt<k>"),
                      (".callgrind.stdout", "S3", "V-6 <tag>.callgrind.stdout"), (".callgrind.stderr", "S3", "V-6 <tag>.callgrind.stderr"),
                      (".callgrind.out", "S3", "V-6 <tag>.callgrind.out (removed)"), (".cg.ms.out", "S3", "V-6 <tag>.cg.ms.out (removed)"),
                      (".ms.out", "S1", "<tag>.ms.out"), (".ms.log", "S1", "<tag>.ms.log"), (".ms.err", "S1", "<tag>.ms.err"),
                      (".ms", "S1", "<tag>.ms (input)")]
FILE_EXT_RE = re.compile(r"\.(json|yaml|yml|txt|md|log|tsv|csv)$")
MAXPATH = 7
PRODUCERS = {"S1": "v2/v2_driver:solve", "S2": "a1/a1_health:run_system", "S3": "v2/v2_solver:callgrind_instructions"}
SOURCE_CALLS = {"v2/v2_driver:solve": "S1", "r2/r2_resolve:solve": "S1", "r2/r2_resolve:_call_original": "S1",
                "a1/a1_health:run_system": "S2", "v2/v2_solver:callgrind_instructions": "S3"}
RUNTIME_BINDINGS = [("v2/v2_driver:solve", "r2/r2_resolve:solve",
                     "SE-3: under both r2 entries v2_driver.solve is the r2 wrapper (r2_resolve.install, r2_resolve.py line 298)"),
                    ("r2/r2_resolve:_call_original", "v2/v2_driver:solve",
                     "SE-3: _STATE['original'] is the frozen v2_driver.solve (r2_resolve.install, lines 292-297)")]
CALL_PASSTHRU = {"sorted", "list", "tuple", "set", "frozenset", "dict", "reversed", "enumerate", "zip", "filter", "map", "iter", "next",
                 "copy", "deepcopy", "min", "max", "sum", "any", "all", "abs", "round", "int", "float", "bool", "len", "str", "repr",
                 "format", "json.loads", "json.load", "yaml.safe_load", "yaml.load", "json.dumps", "yaml.safe_dump", "yaml.dump",
                 "OrderedDict", "defaultdict", "Counter", "statistics.median", "statistics.mean", "statistics.pstdev", "median", "mean",
                 "math.log", "math.log2", "math.sqrt", "fractions.Fraction", "Fraction", "hashlib.sha256", "canonical_json", "dumps"}
SER_CALLS = {"json.dumps", "str", "repr", "yaml.safe_dump", "yaml.dump", "pprint.pformat", "canonical_json", "dumps"}
HASH_CALLS = {"hashlib.sha256", "hashlib.sha1", "hashlib.md5", "hash", "sha256_bytes"}
STORE_METHODS = {"append", "add", "insert", "extend", "update", "setdefault", "appendleft", "__setitem__"}
STR_METHODS = {"read", "read_text", "readlines", "splitlines", "strip", "lower", "upper", "decode", "encode", "format", "join", "split",
               "replace", "rstrip", "lstrip", "title", "rsplit", "partition", "hexdigest", "digest"}
SEARCH_METHODS = {"startswith", "endswith", "find", "count", "index", "rfind", "__contains__"}
RE_SEARCH = {"re.search", "re.match", "re.fullmatch", "re.findall", "re.finditer", "re.sub"}


def T(origin, path=(), via="", full=(), ser=False):
    return (origin, tuple(path)[:MAXPATH], via, tuple(full)[:MAXPATH], ser)


def site_of(origin):
    if origin.startswith("C4:"):
        return "CU-4"
    return SITE_OF.get(origin.split("/")[0], "?")


def is_field_origin(o):
    return "/f:" in o or "/file:" in o or ("|f:" in o)


def child_origin(o, k):
    o2 = _child_origin(o, k)
    # bound the dotted depth: a repeated dynamic key is idempotent, and at most 4 components are kept
    if "/f:" in o2 or "|f:" in o2:
        sep = "/f:" if "/f:" in o2 else "|f:"
        head, tail = o2.split(sep, 1)
        parts = tail.split(".")
        red = []
        for x in parts:
            if x == "*" and red and red[-1] == "*":
                continue
            red.append(x)
        if len(red) > 2:
            red = red[:2] + ["*"] if red[1] != "*" else red[:2]
        o2 = head + sep + ".".join(red)
    return o2


def _child_origin(o, k):
    if o.startswith("C4:"):
        return o + ("|f:" if "|f:" not in o else ".") + k
    head = o.split("/")[0]
    if o == "S1":
        if k == "instructions_callgrind" and "S3" in SOURCES_ENABLED:
            return "S3"
        if k == "solver":
            return "S1/solver"
        return "S1/f:" + k
    if o in ("S3", "S2"):
        return o + ("/child" if k == "child" else "/f:" + k)
    if o in ("S1/solver", "S3/child", "S2/child", "S1/childrec", "S2/childrec", "S3/childrec"):
        return head + "/f:" + o.split("/")[1] + "." + k
    return o + "." + k


def field_name(o):
    if "|f:" in o:
        return o.split("|f:", 1)[1]
    if "/f:" in o:
        return o.split("/f:", 1)[1]
    if "/file:" in o:
        return "file " + o.split("/file:", 1)[1]
    return "<whole record>"


SCHEMA = {}          # record origin -> the keys its frozen producer sets (definitions); filled by set_schema()
SCALAR_FIELDS = {"S1/f:outcome", "S1/f:reason", "S1/f:D", "S1/f:D_defined", "S1/f:D_reason", "S1/f:tag", "S1/f:parse_kind",
                 "S1/f:n_f4_computations", "S1/f:threads_executed", "S1/f:dimension_of_quotient_printed", "S1/f:no_solution_reported",
                 "S1/f:substitution_failures", "S1/f:output_sha256", "S1/f:output_retained",
                 "S1/f:solver.outcome", "S1/f:solver.wall_seconds", "S1/f:solver.returncode", "S1/f:solver.timed_out",
                 "S1/f:solver.peak_rss_bytes", "S1/f:solver.peak_vm_bytes", "S1/f:solver.refusal_reason",
                 "S1/f:solver.driver_rss_bytes_before_launch", "S1/f:solver.timeout_s",
                 "S3/f:method", "S3/f:label", "S3/f:instructions_user", "S3/f:reason", "S3/f:f4_core_inclusive_Ir", "S3/f:f4_core_function",
                 "S3/f:f4_core_note", "S3/f:child.outcome", "S3/f:child.wall_seconds", "S3/f:child.returncode", "S3/f:child.peak_vm_bytes",
                 "S2/f:tag", "S2/f:p", "S2/f:expected_D", "S2/f:command", "S2/f:threads_executed", "S2/f:exit_status", "S2/f:signal",
                 "S2/f:dimension_of_quotient_printed", "S2/f:parse_kind", "S2/f:n_rational_solutions", "S2/f:rational_substitution_failures",
                 "S2/f:v2_outcome_class", "S2/f:v2_outcome_reason", "S2/f:pass", "S2/f:solver_side_signal", "S2/f:wall_seconds",
                 "S2/f:child.outcome", "S2/f:child.returncode", "S2/f:child.timed_out", "S2/f:child.wall_seconds", "S2/f:child.peak_rss_bytes",
                 "S2/f:child.peak_vm_bytes", "S2/f:child.refusal_reason", "S2/f:child.child_rlimit_report",
                 "S1/f:<comparison result>", "S2/f:<comparison result>", "S3/f:<comparison result>",
                 "S1/f:<string>", "S2/f:<string>", "S3/f:<string>",
                 "S1/f:<aggregate>", "S2/f:<aggregate>", "S3/f:<aggregate>"}


def set_schema(fields):
    SCHEMA.clear()
    SCHEMA["S1"] = set(fields["S-1"])
    SCHEMA["S1/solver"] = set(fields["S-1 solver"])
    SCHEMA["S3"] = set(fields["S-3"])
    SCHEMA["S3/child"] = set(fields["S-3 child"])
    SCHEMA["S2"] = {x for x in fields["S-2"] if not x.startswith("run().")}
    SCHEMA["S2/child"] = set(fields["S-2 child"])


def key_possible(o, k):
    """Can key k of a value with origin o hold site data? Records: only the keys the frozen producer sets.
    Scalar fields: no key. Everything else (childrec, container-valued fields, files, CU-4): any key."""
    if k in ("*",):
        return True
    if o in SCHEMA:
        return k in SCHEMA[o]
    if o in SCALAR_FIELDS:
        return False
    return True


class Mod:
    def __init__(self, key, name, tree, rel, src, pseudo=False):
        self.key, self.name, self.tree, self.rel, self.src, self.pseudo = key, name, tree, rel, src, pseudo
        self.lines = src.splitlines()
        self.ast = ast.parse(src)
        self.parents = {}
        for p in ast.walk(self.ast):
            for c in ast.iter_child_nodes(p):
                self.parents[c] = p
        self.consts, self.imports, self.from_imports, self.star, self.classes, self.defs = {}, {}, {}, [], {}, {}
        self.assign_nodes = {}      # C5: module-level name -> assigned expression (path constants built by os.path.join)
        for st in self.ast.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                v = const_value(st.value)
                if v is not None:
                    self.consts[st.targets[0].id] = v
                self.assign_nodes.setdefault(st.targets[0].id, []).append(st.value)
        for n in ast.walk(self.ast):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.imports[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
                    if a.asname is None and "." in a.name:
                        self.imports[a.name.split(".")[0]] = a.name.split(".")[0]
            elif isinstance(n, ast.ImportFrom):
                modname = ("." * n.level) + (n.module or "")
                for a in n.names:
                    if a.name == "*":
                        self.star.append(modname)
                    else:
                        self.from_imports[a.asname or a.name] = (modname, a.name)

    def line(self, n):
        return self.lines[n - 1] if 0 < n <= len(self.lines) else ""


def const_value(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return n.value
    if isinstance(n, (ast.Tuple, ast.List, ast.Set)) and n.elts and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in n.elts):
        return tuple(e.value for e in n.elts)
    return None


class Func:
    def __init__(self, fid, mod, node, qual, parent, body):
        self.fid, self.mod, self.node, self.qual, self.parent, self.body = fid, mod, node, qual, parent, body
        self.params = []
        if node is not None and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = node.args
            self.params = [x.arg for x in a.posonlyargs + a.args] + ([a.vararg.arg] if a.vararg else []) + [x.arg for x in a.kwonlyargs] + ([a.kwarg.arg] if a.kwarg else [])
        self.env = {}
        self.consts = {}          # local name -> set of string constants (constant loops / assignments)
        self.assigns = {}         # local name -> [value nodes]
        self.fh = {}              # file handle name -> (names, mode)
        self.lineno = node.lineno if node is not None else 1
        self.end = getattr(node, "end_lineno", None) if node is not None else None


MODS, FUNCS, MODNAME = {}, {}, {}
MODS_BY_REL = {}
PARAM, RET, FILE_TAGS, GLOBAL_ENV, ATTR, CALLABLE_PARAM = {}, {}, {}, {}, {}, {}
CLOSURE_MUT = {}
PMUT = {}                 # C12: (function id, parameter) -> tags the function stores into that parameter's object
LOADER, WRITER, HASHER = {}, {}, {}
EDGES = {}
C4_SITES = {}                                     # (rel, line) -> {"callee_last": str, "program": str}
S_LAUNCH_LINES = set()                            # (rel, line) of the classified launches (sources inside producers)
HITS = {}
CHANGED = [False]
RECORDING = [False]


def fid_rel(fid):
    return FUNCS[fid].mod.rel if fid in FUNCS else None


DEPS = {}
PROGRESS = [None]
DIRTY = []
DIRTY_SET = set()


def dep(key, fid):
    DEPS.setdefault(key, set()).add(fid)


def mark_dirty(fid):
    if fid not in DIRTY_SET and fid in FUNCS:
        DIRTY_SET.add(fid)
        DIRTY.append(fid)


def passes_callgrind_timeout(call):
    for k in call.keywords:
        if k.arg == "callgrind_timeout":
            return not (isinstance(k.value, ast.Constant) and k.value.value is None)
    return len(call.args) >= 8 and not (isinstance(call.args[7], ast.Constant) and call.args[7].value is None)


def derived_scalar(tags, label):
    """A boolean / number computed from site data: a scalar derived value (no key can be read from it)."""
    out = set()
    for (o, p, via, full, ser) in tags:
        r = root_origin(o)
        o2 = (r + "|f:" + label) if r.startswith("C4:") else (r + "/f:" + label)
        out.add((o2, (), via, full, False))
    return out


def root_origin(o):
    if o.startswith("C4:"):
        return o.split("|")[0]
    return o.split("/")[0]


def trunc(p, n):
    return p if len(p) <= n else tuple(p[:n - 1]) + ("*",)


def norm(tags, k=128, total=1024):
    """Bound a tag set (documented abstraction, over-approximating only): per origin at most k distinct paths, beyond
    which paths are truncated to their first two keys plus a wildcard; above `total` tags, to their first key plus a
    wildcard; above `total` again, field origins collapse to <site>/f:*. A wildcard key matches every key."""
    if len(tags) <= k:
        return tags
    by = {}
    for tg in tags:
        by.setdefault((tg[0], tg[4]), []).append(tg)
    out = set()
    for (o, ser), v in by.items():
        if len(v) <= k:
            out |= set(v)
        else:
            out |= {(o, trunc(p, 3), via, trunc(full, 3), ser) for (o, p, via, full, ser) in v}
    if len(out) > total:
        out = dedupe({(o, trunc(p, 2), via, trunc(full, 2), ser) for (o, p, via, full, ser) in out})
    if len(out) > total:
        out = dedupe({((root_origin(o) + ("|f:*" if o.startswith("C4:") else "/f:*")) if is_field_origin(o) else o, p, via, full, ser)
                      for (o, p, via, full, ser) in out})
    return out


def merge_states(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = (out[k] | v) if k in out else v
    return out


def states_equal(a, b):
    return a.keys() == b.keys() and all(a[k] == b[k] for k in a)


def dedupe(tags):
    out, seen = set(), set()
    for tg in sorted(tags, key=lambda t: (t[0], t[1], t[2])):
        k = (tg[0], tg[1], tg[4])
        if k not in seen:
            seen.add(k)
            out.add(tg)
    return out


COLLAPSED = set()


def collapse(tags):
    """Monotone collapse of a stored set: every path truncated to its first two keys plus a wildcard; one tag per
    (origin, path, ser)."""
    return dedupe({(o, trunc(p, 3), via, trunc(full, 3), ser) for (o, p, via, full, ser) in tags})


def add_to(store, key, tags):
    ck = (id(store), key)
    cur = store.setdefault(key, set())
    if ck in COLLAPSED:
        tags = collapse(tags)
        have = {(o, p, ser) for (o, p, via, full, ser) in cur}
        new = {t for t in tags if (t[0], t[1], t[4]) not in have}
    else:
        tags = norm(tags)
        new = tags - cur
    if not new:
        return False
    cur |= new
    if ck not in COLLAPSED and len(cur) > 2000:
        COLLAPSED.add(ck)
        store[key] = collapse(cur)
    CHANGED[0] = True
    if store is PARAM:
        mark_dirty(key[0])
    else:
        dk = (("R", key) if store is RET else ("F", key) if store is FILE_TAGS else ("G",) + tuple(key) if store is GLOBAL_ENV
              else ("M",) + tuple(key) if store is CLOSURE_MUT else ("PM",) + tuple(key) if store is PMUT else ("A", key))
        for f in sorted(DEPS.get(dk, ())):
            mark_dirty(f)
    return True


def body_stmts(stmts):
    """Statements of a body, descending into compound statements but not into nested defs / classes."""
    out = []
    for st in stmts:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        out.append(st)
        for fld in ("body", "orelse", "finalbody"):
            sub = getattr(st, fld, None)
            if isinstance(sub, list) and not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out += body_stmts(sub)
        if isinstance(st, ast.Try) or (hasattr(ast, "TryStar") and isinstance(st, getattr(ast, "TryStar"))):
            for h in st.handlers:
                out += body_stmts(h.body)
        if hasattr(ast, "Match") and isinstance(st, ast.Match):
            for c in st.cases:
                out += body_stmts(c.body)
    return out


def is_main_guard(st):
    return (isinstance(st, ast.If) and isinstance(st.test, ast.Compare) and isinstance(st.test.left, ast.Name)
            and st.test.left.id == "__name__")


def load_module(key, name, tree, rel, src, pseudo=False):
    m = Mod(key, name, tree, rel, src, pseudo)
    MODS[key] = m
    MODS_BY_REL[rel] = m
    MODNAME.setdefault(name, []).append(key)
    top = [st for st in m.ast.body if not is_main_guard(st)]
    FUNCS[key + ":<module>"] = Func(key + ":<module>", m, None, "<module>", None, body_stmts(top))
    FUNCS[key + ":<module>"].raw = top
    mains = [st for st in m.ast.body if is_main_guard(st)]
    if mains:
        FUNCS[key + ":<main>"] = Func(key + ":<main>", m, None, "<main>", None, body_stmts(mains[0].body))
        FUNCS[key + ":<main>"].lineno = mains[0].lineno
        FUNCS[key + ":<main>"].raw = mains[0].body

    def visit(node, prefix, parent_fid, cls):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = prefix + ch.name
                fid = key + ":" + q
                FUNCS[fid] = Func(fid, m, ch, q, parent_fid, body_stmts(ch.body))
                FUNCS[fid].raw = ch.body
                if cls:
                    m.classes.setdefault(cls, {})[ch.name] = fid
                elif parent_fid is None or parent_fid.endswith(":<module>"):
                    m.defs[ch.name] = fid
                visit(ch, q + ".", fid, None)
            elif isinstance(ch, ast.ClassDef):
                m.classes.setdefault(ch.name, {})
                visit(ch, prefix + ch.name + ".", parent_fid, ch.name)
                if "__init__" in m.classes[ch.name]:
                    m.defs[ch.name] = m.classes[ch.name]["__init__"]
            else:
                visit(ch, prefix, parent_fid, cls)
    visit(m.ast, "", key + ":<module>", None)
    return m


def resolve_module(mod, name):
    """A module name as imported by `mod` -> module key(s) among the loaded modules."""
    base = name.lstrip(".").split(".")[-1] if name else ""
    keys = MODNAME.get(base, [])
    if not keys:
        return []
    if mod.tree in ("v1", "v2", "a1", "r1", "r2"):
        exp = [k for k in keys if MODS[k].tree in ("v1", "v2", "a1", "r1", "r2")]
        same = [k for k in exp if MODS[k].tree == mod.tree]
        return same or exp
    same_dir = [k for k in keys if os.path.dirname(MODS[k].rel) == os.path.dirname(mod.rel)]
    tool = [k for k in keys if MODS[k].tree == "tool"]
    return same_dir or tool


def module_aliases(mod):
    out = {}
    for alias, name in mod.imports.items():
        ks = resolve_module(mod, name)
        if ks:
            out[alias] = ks
    return out


ALIAS_CACHE = {}


def aliases(mod):
    if mod.key not in ALIAS_CACHE:
        ALIAS_CACHE[mod.key] = module_aliases(mod)
    return ALIAS_CACHE[mod.key]


def resolve_name(fn, name):
    """A bare name called / referenced in fn -> function ids."""
    mod = fn.mod
    # nested defs of the enclosing chain
    p = fn
    while p is not None:
        cand = p.fid + "." + name if not p.fid.endswith((":<module>", ":<main>")) else None
        if cand and cand in FUNCS:
            return [cand]
        p = FUNCS.get(p.parent) if p.parent else None
    if name in fn.params and fn.fid in CALLABLE_PARAM and name in CALLABLE_PARAM[fn.fid]:
        return sorted(CALLABLE_PARAM[fn.fid][name])
    if name in mod.defs:
        return [mod.defs[name]]
    if name in mod.from_imports:
        mname, orig = mod.from_imports[name]
        out = []
        for k in resolve_module(mod, mname):
            if orig in MODS[k].defs:
                out.append(MODS[k].defs[orig])
        return out
    for mname in mod.star:
        for k in resolve_module(mod, mname):
            if name in MODS[k].defs:
                return [MODS[k].defs[name]]
    return []


RESOLVE_CACHE = {}


def resolve_call(fn, f):
    if isinstance(f, ast.Name) and f.id in fn.params:
        return [x for x in _resolve_call(fn, f) if x in FUNCS]
    k = (fn.fid, id(f))
    if k not in RESOLVE_CACHE:
        RESOLVE_CACHE[k] = [x for x in _resolve_call(fn, f) if x in FUNCS]
    return RESOLVE_CACHE[k]


def _resolve_call(fn, f):
    if isinstance(f, ast.Name):
        return resolve_name(fn, f.id)
    if isinstance(f, ast.Attribute):
        al = aliases(fn.mod)
        if isinstance(f.value, ast.Name) and f.value.id in al:
            out = []
            for k in al[f.value.id]:
                if f.attr in MODS[k].defs:
                    out.append(MODS[k].defs[f.attr])
            return out
        # obj.method: methods of that name in this module's classes and in the modules it imports (approximate)
        out = []
        mods = [fn.mod.key] + [k for ks in al.values() for k in ks]
        for k in mods:
            for cls, meths in MODS[k].classes.items():
                if f.attr in meths:
                    out.append(meths[f.attr])
        return sorted(set(out))
    return []


def dotted(f):
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        d = dotted(f.value)
        return (d + "." + f.attr) if d else f.attr
    return ""


def str_consts(fn, n, depth=0, seen=None):
    """Every string constant an expression can carry: literals, local assignments, constant loops, module constants."""
    out = set()
    if n is None or depth > 4:
        return out
    seen = seen if seen is not None else set()
    for x in ast.walk(n):
        if isinstance(x, ast.Constant) and isinstance(x.value, str):
            out.add(x.value)
        elif isinstance(x, ast.Name) and x.id not in seen:
            seen.add(x.id)
            if x.id in fn.consts:
                out |= fn.consts[x.id]
            for v in fn.assigns.get(x.id, []):
                out |= str_consts(fn, v, depth + 1, seen)
            c = fn.mod.consts.get(x.id)
            if c is not None:
                out |= set(c) if isinstance(c, tuple) else {c}
            elif x.id in fn.mod.assign_nodes and x.id not in fn.assigns and (fn.mod.key + ":<module>") in FUNCS:
                for v in fn.mod.assign_nodes[x.id]:     # C5: a module-level path expression of this module
                    out |= str_consts(FUNCS[fn.mod.key + ":<module>"], v, depth + 1, seen)
            p = FUNCS.get(fn.parent) if fn.parent else None
            while p is not None and not p.fid.endswith(":<module>"):
                for v in p.assigns.get(x.id, []):
                    out |= str_consts(p, v, depth + 1, seen)
                p = FUNCS.get(p.parent) if p.parent else None
        elif isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name):
            for k in aliases(fn.mod).get(x.value.id, []):
                c = MODS[k].consts.get(x.attr)
                if c is not None:
                    out |= set(c) if isinstance(c, tuple) else {c}
                elif x.attr in MODS[k].assign_nodes and (k + ":<module>") in FUNCS and ("attr", k, x.attr) not in seen:
                    seen.add(("attr", k, x.attr))      # C5: a module-level path expression of an imported scanned module
                    for v in MODS[k].assign_nodes[x.attr]:
                        out |= str_consts(FUNCS[k + ":<module>"], v, depth + 1, seen)
    return out


def names_in(fn, n):
    return {x.id for x in ast.walk(n) if isinstance(x, ast.Name)} if n is not None else set()


FILE_IDS_CACHE = {}


def file_ids(fn, n):
    k = (fn.fid, id(n), sum(len(v) for v in fn.assigns.values()), sum(len(v) for v in fn.consts.values()))
    if k not in FILE_IDS_CACHE:
        FILE_IDS_CACHE[k] = _file_ids(fn, n)
    return FILE_IDS_CACHE[k]


def _file_ids(fn, n):
    """(derived-file names, site-file suffix hits, param indices) for a path expression."""
    cs = str_consts(fn, n)
    files, sitef = set(), set()
    for c in cs:
        base = c.rsplit("/", 1)[-1]
        for suf, site, label in SITE_FILE_SUFFIXES:
            if base.endswith(suf) or base == suf or (suf == ".ssf-attempt" and suf in base):
                sitef.add((site, suf, label))
                break
        else:
            if FILE_EXT_RE.search(base) and len(base) < 80 and " " not in base:
                files.add(base)
    if any(c in ("solver",) for c in cs) and not sitef:
        sitef.add(("S1", "solver/", "the solver/ directory"))
    params = set()
    pn = names_in(fn, n)
    for i, p in enumerate(fn.params):
        if p in pn:
            params.add(i)
        else:
            for v in fn.assigns.get(p, []):
                pass
    for nm in pn:
        for v in fn.assigns.get(nm, []):
            for i, p in enumerate(fn.params):
                if p in names_in(fn, v):
                    params.add(i)
    return files, sitef, params


def site_of_file(fn, site):
    if site == "S1" and fn.mod.name in ("a1_health",):
        return "S2"
    return site


# ----------------------------------------------------------------------------------------------- the evaluator
def prefix(tags, key, fn, root, fresh_via=True):
    out = set()
    for (o, p, via, full, ser) in tags:
        np = ((key,) + p)[:MAXPATH]
        if via == "" and fresh_via:
            out.add((o, np, "mem:%s:%s" % (fn.fid, root), np, ser))
        else:
            out.add((o, np, via, full if via else np, ser))
    return out


def strip_elem(tags):
    out = set()
    for (o, p, via, full, ser) in tags:
        if p and p[0] in ("[]", "*"):
            out.add((o, p[1:], via, full, ser))
        elif not p and ser:
            out.add((o, p, via, full, ser))
    return out


class Ev:
    def __init__(self, fn):
        self.fn = fn
        self.mod = fn.mod
        self.cond = []                  # tags of enclosing if / while tests (implicit flow)
        self.state = {}                 # flow-sensitive local state
        self._comp_saved = {}

    # ----- environment
    def lookup(self, name):
        fn = self.fn
        if name in self.state:
            out = self.state[name]
            cm = CLOSURE_MUT.get((fn.fid, name))
            if cm:
                out = out | cm
            dep(("M", fn.fid, name), fn.fid)
            return out
        if name in fn.locals_ and not fn.fid.endswith((":<module>", ":<main>")):
            dep(("M", fn.fid, name), fn.fid)
            return set(CLOSURE_MUT.get((fn.fid, name), set()))
        p = FUNCS.get(fn.parent) if fn.parent else None
        while p is not None:
            if name in p.env and not p.fid.endswith(":<module>"):
                return p.env[name] | CLOSURE_MUT.get((p.fid, name), set())
            p = FUNCS.get(p.parent) if p.parent else None
        dep(("G", self.mod.key, name), self.fn.fid)
        return GLOBAL_ENV.get((self.mod.key, name), set())

    def _summary(self, name, tags):
        fn = self.fn
        cur = fn.env.setdefault(name, set())
        if not tags <= cur:
            fn.env[name] = norm(cur | tags)
            self.local_changed = True

    def bind(self, name, tags):
        """Strong update of a local name (flow-sensitive state); the summary env keeps the union for closures."""
        fn = self.fn
        tags = norm(set(tags))
        if fn.fid.endswith((":<module>", ":<main>")) or name in getattr(fn, "globals_", set()):
            add_to(GLOBAL_ENV, (self.mod.key, name), tags)
        self.state[name] = tags
        self._summary(name, tags)

    def bind_weak(self, name, tags):
        """A mutation (store into a container held by `name`): union, and propagate to the owner of a non-local name."""
        fn = self.fn
        tags = norm(set(tags))
        if name in fn.locals_ or fn.fid.endswith((":<module>", ":<main>")):
            if fn.fid.endswith((":<module>", ":<main>")) or name in getattr(fn, "globals_", set()):
                add_to(GLOBAL_ENV, (self.mod.key, name), tags)
            self.state[name] = norm(self.lookup(name) | tags)
            self._summary(name, tags)
            return
        p = FUNCS.get(fn.parent) if fn.parent else None
        while p is not None and not p.fid.endswith((":<module>", ":<main>")):
            if name in p.locals_:
                add_to(CLOSURE_MUT, (p.fid, name), tags)
                return
            p = FUNCS.get(p.parent) if p.parent else None
        add_to(GLOBAL_ENV, (self.mod.key, name), tags)

    def implicit(self):
        """Control dependence is recorded one step (CONTROL_WRITES), never propagated (method note M-7)."""
        return set()

    def note_control(self, target_desc, node):
        if not RECORDING[0] or not self.cond:
            return
        origins = set()
        for t in self.cond:
            origins |= {tg[0] for tg in t}
        if origins:
            CONTROL_WRITES.append({"fid": self.fn.fid, "file": self.mod.rel, "line": getattr(node, "lineno", 0), "target": target_desc,
                                   "controlled_by_origins": sorted(origins)})

    # ----- hits
    def hit(self, node, tag, field, mode, note=None):
        if not RECORDING[0]:
            return
        o, p, via, full, ser = tag
        key = (self.fn.fid, getattr(node, "lineno", 0), getattr(node, "col_offset", 0), o, via, mode, field)
        if key in HITS:
            if p:
                HITS[key].setdefault("paths", set()).add("/".join(p))
            return
        HITS[key] = {"fid": self.fn.fid, "file": self.mod.rel, "line": getattr(node, "lineno", 0), "col": getattr(node, "col_offset", 0),
                     "function": self.fn.qual, "tree": self.mod.tree, "origin": o, "site": site_of(o), "field": field, "mode": mode,
                     "via": via, "full": "/".join(full), "node": node, "note": note, "paths": {"/".join(p)} if p else set()}

    def whole_hits(self, node, tags, mode, note=None):
        for tg in tags:
            o = tg[0]
            fld = field_name(o) if tg[1] == () else "<structure holding site data>"
            self.hit(node, tg, fld, mode, note)

    # ----- subscripts
    def sub(self, tags, keys, node, mode="m1"):
        out = set()
        for tg in tags:
            o, p, via, full, ser = tg
            if ser:
                continue
            for k in keys:
                if p == ():
                    if k == "[]":
                        if is_field_origin(o) and o not in SCALAR_FIELDS:
                            out.add((o + "[]" if not o.endswith("[]") else o, (), via, full, ser))
                        continue
                    if not key_possible(o, k):
                        continue
                    no = child_origin(o, k)
                    out.add((no, (), via, full, ser))
                    self.hit(node, tg, field_name(no) if is_field_origin(no) else (k if k != "*" else "<computed key>"),
                             "m7+" + mode if via else mode)
                else:
                    h = p[0]
                    if h == k or h == "*" or k == "*":
                        wild = (h != k) and not via.endswith(WILD)
                        nt = (o, p[1:], via + WILD if wild else via, full, ser)
                        out.add(nt)
                        if p[1:] == () and k != "[]":
                            # the read reaches the site datum itself: a field, or the record / sub-record under its key
                            self.hit(node, nt, field_name(o) if is_field_origin(o) else (k if k != "*" else "<computed key>"),
                                     "m7+" + mode if via else mode)
        return out

    def keys_of(self, n):
        if isinstance(n, ast.Constant):
            if isinstance(n.value, str):
                return {n.value}
            return {"[]"}
        if isinstance(n, ast.Slice) or isinstance(n, ast.UnaryOp):
            return {"[]"}
        if isinstance(n, ast.Name) and n.id in self.fn.consts and self.fn.consts[n.id]:
            return set(self.fn.consts[n.id])
        if isinstance(n, ast.Name) and n.id in ("i", "j", "idx", "k_idx", "n", "pos"):
            return {"[]"}
        return {"*"}

    # ----- expressions
    def ev(self, n):
        r = self._ev(n)
        return norm(r) if len(r) > 128 else r

    def _ev(self, n):
        if n is None:
            return set()
        t = type(n)
        if t is ast.Name:
            return set(self.lookup(n.id))
        if t is ast.Constant:
            return set()
        if t is ast.Attribute:
            if isinstance(n.value, ast.Name) and n.value.id in aliases(self.mod):
                out = set()
                for k in aliases(self.mod)[n.value.id]:
                    dep(("G", k, n.attr), self.fn.fid)
                    out |= GLOBAL_ENV.get((k, n.attr), set())
                return out
            self.ev(n.value)
            ak = (self.mod.tree, n.attr)
            dep(("A", ak), self.fn.fid)
            return set(ATTR.get(ak, set()))
        if t is ast.Subscript:
            b = self.ev(n.value)
            self.ev(n.slice)
            return self.sub(b, self.keys_of(n.slice), n)
        if t is ast.Call:
            return self.call(n)
        if t is ast.Dict:
            out = set()
            for k, v in zip(n.keys, n.values):
                vt = self.ev(v)
                if k is None:
                    if vt:
                        self.whole_hits(n, vt, "m6", "** unpacking copies every key")
                    out |= {(o, p, via or "mem:%s:<dict>" % self.fn.fid, full or p, ser) for (o, p, via, full, ser) in vt}
                    continue
                self.ev(k)
                for kk in self.keys_of(k):
                    out |= {(o, ((kk,) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in vt}
            return out
        if t in (ast.List, ast.Tuple, ast.Set):
            out = set()
            for e in n.elts:
                out |= {(o, (("[]",) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in self.ev(e)}
            return out
        if t is ast.Starred:
            return self.ev(n.value)
        if t in (ast.ListComp, ast.SetComp, ast.GeneratorExp):
            saved, self._comp_saved = self._comp_saved, {}
            self.comp_gens(n.generators)
            out = {(o, (("[]",) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in self.ev(n.elt)}
            self._restore_comp(saved)
            return out
        if t is ast.DictComp:
            saved, self._comp_saved = self._comp_saved, {}
            self.comp_gens(n.generators)
            out = self._dictcomp(n)
            self._restore_comp(saved)
            return out
        if t is ast.BinOp:
            a, b = self.ev(n.left), self.ev(n.right)
            if isinstance(n.op, ast.Mod) and isinstance(n.left, ast.Constant) and isinstance(n.left.value, str):
                return {(o, p, via, full, True) if p else (o, p, via, full, ser) for (o, p, via, full, ser) in b} | a
            return a | b
        if t is ast.BoolOp:
            out = set()
            for v in n.values:
                out |= self.ev(v)
            return out
        if t is ast.UnaryOp:
            return self.ev(n.operand)
        if t is ast.Compare:
            return self.compare(n)
        if t is ast.IfExp:
            tt = self.ev(n.test)
            return tt | self.ev(n.body) | self.ev(n.orelse)
        if t is ast.JoinedStr:
            out = set()
            for v in n.values:
                out |= self.ev(v)
            return out
        if t is ast.FormattedValue:
            vt = self.ev(n.value)
            if vt and any(tg[1] for tg in vt):
                self.whole_hits(n, {tg for tg in vt if tg[1]}, "m6", "f-string formatting of a structure")
            return vt
        if t is ast.NamedExpr:
            vt = self.ev(n.value)
            self.assign(n.target, vt, n.value)
            return vt
        if t in (ast.Await, ast.Yield, ast.YieldFrom):
            return self.ev(n.value)
        if t is ast.Lambda:
            return set()
        if t is ast.Slice:
            self.ev(n.lower)
            self.ev(n.upper)
            self.ev(n.step)
            return set()
        return set()

    def _restore_comp(self, saved):
        for nm, old in self._comp_saved.items():
            if old is None:
                self.state.pop(nm, None)
            else:
                self.state[nm] = old
        self._comp_saved = saved

    def _dictcomp(self, n):
        out = set()
        if isinstance(n.key, ast.Name) and self.fn.consts.get(n.key.id) and len(self.fn.consts[n.key.id]) <= 64:
            allk = set(self.fn.consts[n.key.id])
            for kk in sorted(allk):
                self.fn.consts[n.key.id] = {kk}
                vt = self.ev(n.value)
                out |= {(o, ((kk,) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in vt}
            self.fn.consts[n.key.id] = allk
            return out
        ks = self.keys_of(n.key) if not isinstance(n.key, ast.Name) else {"*"}
        self.ev(n.key)
        vt = self.ev(n.value)
        for kk in ks:
            out |= {(o, ((kk,) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in vt}
        return out

    def compare(self, n):
        left = self.ev(n.left)
        res = set()
        prev = left
        prev_node = n.left
        for op, c in zip(n.ops, n.comparators):
            ct = self.ev(c)
            if isinstance(op, (ast.In, ast.NotIn)):
                ser_r = {tg for tg in ct if tg[4]}
                if ser_r:
                    self.whole_hits(n, ser_r, "m5", "substring test on a serialization")
                keyset = {tg for tg in ct if not tg[4] and tg[1] == () and not is_field_origin(tg[0])}
                const_left = isinstance(prev_node, ast.Constant) and isinstance(prev_node.value, str)
                if keyset and const_left:
                    for tg in keyset:
                        if key_possible(tg[0], prev_node.value):
                            self.hit(n, tg, prev_node.value, "m7+m1" if tg[2] else "m1", "membership test of a key")
                if const_left:
                    # a constant string tested against a mapping: a key test, which reads site data only at that key
                    for tg in ct:
                        if not tg[4] and len(tg[1]) == 1 and tg[1][0] in (prev_node.value, "*"):
                            self.hit(n, (tg[0], (), tg[2], tg[3], False), prev_node.value, "m7+m1" if tg[2] else "m1", "membership test of a key")
                    cont = {tg for tg in ct if not tg[4] and tg[1] and tg[1][0] == "[]"}
                else:
                    cont = {tg for tg in ct if not tg[4] and tg[1] != ()}
                if cont:
                    self.whole_hits(n, cont, "m4", "membership test against entries of a structure")
                res |= derived_scalar({tg for tg in (ct | prev) if tg[1] == () or tg[4] or tg in cont}, "<comparison result>")
            elif isinstance(op, (ast.Eq, ast.NotEq)):
                for side in (prev, ct):
                    whole = {tg for tg in side if not tg[4] and (tg[1] != () or not is_field_origin(tg[0]))}
                    if whole:
                        self.whole_hits(n, whole, "m4", "whole-entry / whole-record comparison")
                res |= derived_scalar(prev | ct, "<comparison result>")
            elif isinstance(op, (ast.Is, ast.IsNot)):
                res |= derived_scalar({tg for tg in (prev | ct) if tg[1] == ()}, "<comparison result>")
            else:
                res |= derived_scalar({tg for tg in (prev | ct) if tg[1] == ()}, "<comparison result>")
            prev, prev_node = ct, c
        return res

    def comp_gens(self, gens):
        for g in gens:
            for x in ast.walk(g.target):
                if isinstance(x, ast.Name) and x.id not in self._comp_saved:
                    self._comp_saved[x.id] = self.state.get(x.id, None)
            it = self.ev(g.iter)
            self.loop_target(g.target, g.iter, it)
            for cond in g.ifs:
                self.ev(cond)

    def iter_tags(self, it_node, it):
        """Element tags of iterating `it`; m6 hits for iteration over a mapping holding site data."""
        out = strip_elem(it)
        maps = {tg for tg in it if tg[1] == () and not tg[4] and not is_field_origin(tg[0])}
        if maps:
            self.whole_hits(it_node, maps, "m6", "iteration over a record's keys")
        mapc = {tg for tg in it if len(tg[1]) == 1 and tg[1][0] not in ("[]",) and not tg[4]}
        if mapc:
            self.whole_hits(it_node, mapc, "m6", "iteration over the keys of a mapping whose values are site records / fields")
        return out

    def loop_target(self, target, it_node, it):
        # constant loops: for ext in (".ms.log", ".ms.err")
        if isinstance(target, ast.Name):
            cv = const_value(it_node) if it_node is not None else None
            if cv is not None:
                self.fn.consts[target.id] = set(cv) if isinstance(cv, tuple) else {cv}
            elif isinstance(it_node, ast.Name) and it_node.id in self.fn.mod.consts and isinstance(self.fn.mod.consts[it_node.id], tuple):
                self.fn.consts[target.id] = set(self.fn.mod.consts[it_node.id])
        if isinstance(it_node, ast.Call) and isinstance(it_node.func, ast.Attribute) and it_node.func.attr == "items" \
                and isinstance(target, ast.Tuple) and len(target.elts) == 2:
            base = self.ev(it_node.func.value)
            self.assign(target.elts[1], self.values_tags(base), None)
            self.assign(target.elts[0], set(), None)
            return
        if isinstance(it_node, ast.Call) and isinstance(it_node.func, ast.Name) and it_node.func.id == "enumerate" \
                and isinstance(target, ast.Tuple) and len(target.elts) == 2 and it_node.args:
            inner = self.ev(it_node.args[0])
            self.assign(target.elts[1], self.iter_tags(it_node.args[0], inner), None)
            return
        if isinstance(it_node, ast.Call) and isinstance(it_node.func, ast.Name) and it_node.func.id == "zip" \
                and isinstance(target, ast.Tuple) and len(target.elts) == len(it_node.args):
            for tnode, anode in zip(target.elts, it_node.args):
                self.assign(tnode, self.iter_tags(anode, self.ev(anode)), None)
            return
        el = self.iter_tags(it_node, it)
        self.assign(target, el, None)

    def values_tags(self, base):
        out = set()
        for (o, p, via, full, ser) in base:
            if ser:
                continue
            if p == ():
                if not is_field_origin(o):
                    out.add((child_origin(o, "*"), (), via, full, ser))
            else:
                out.add((o, p[1:], via, full, ser))
        return out

    # ----- calls
    def call(self, n):
        f = n.func
        fname = dotted(f)
        last = fname.split(".")[-1] if fname else ""
        argt = [self.ev(a) for a in n.args]
        kwt = {}
        for k in n.keywords:
            kwt[k.arg] = self.ev(k.value)
        allargs = set()
        for a in argt:
            allargs |= a
        for v in kwt.values():
            allargs |= v
        is_mod_attr = isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in aliases(self.mod)
        # C1 (this task's repair of the partial script): a call on an imported LIBRARY module name (copy.deepcopy,
        # shutil.copy, ...) is a library call, not a method of a value; its arguments carry the data (M-17)
        is_lib_mod = (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and not is_mod_attr
                      and f.value.id in self.mod.imports and f.value.id not in getattr(self.fn, "locals_", set()))
        if is_lib_mod and f.attr in ("copy", "deepcopy"):
            return allargs
        # ---- method calls on values
        if isinstance(f, ast.Attribute) and not is_mod_attr and not is_lib_mod:
            m = f.attr
            recv = self.ev(f.value)
            if m == "get" and n.args:
                return self.sub(recv, self.keys_of(n.args[0]), n) | (argt[1] if len(argt) > 1 else set())
            if m in ("pop", "setdefault") and n.args and recv and m == "pop":
                return self.sub(recv, self.keys_of(n.args[0]), n)
            if m in ("items", "values"):
                vals = self.values_tags(recv)
                maps = {tg for tg in recv if not tg[4] and (len(tg[1]) == 1 or (tg[1] == () and not is_field_origin(tg[0])))}
                if maps:
                    self.whole_hits(n, maps, "m6", ".%s() over a mapping holding site data" % m)
                return {(o, (("[]",) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in vals}
            if m == "keys":
                maps = {tg for tg in recv if not tg[4] and (len(tg[1]) == 1 or (tg[1] == () and not is_field_origin(tg[0])))}
                if maps:
                    self.whole_hits(n, maps, "m6", ".keys() of a mapping holding site data")
                return set()
            if m in ("copy", "deepcopy"):
                return recv
            if m in STORE_METHODS:
                if m == "update":
                    vt = set(argt[0]) if argt else set()
                    for kk, v in kwt.items():
                        if kk:
                            vt |= {(o, ((kk,) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in v}
                    self.store_into(f.value, vt, None, n, m)
                elif m == "setdefault":
                    if len(argt) > 1:
                        for kk in self.keys_of(n.args[0]):
                            self.store_into(f.value, argt[1], kk, n, m)
                    return self.sub(recv, self.keys_of(n.args[0]), n) if n.args else set()
                elif m == "insert":
                    self.store_into(f.value, argt[1] if len(argt) > 1 else set(), "[]", n, m)
                elif m == "extend":
                    self.store_into(f.value, allargs, None, n, m)
                else:
                    self.store_into(f.value, allargs, "[]", n, m)
                return set()
            if m == "write" and isinstance(f.value, ast.Name) and f.value.id in self.fn.fh:
                names, sitef, mode = self.fn.fh[f.value.id]
                self.write_file(names, allargs, n)
                return set()
            if m in SEARCH_METHODS:
                ser = {tg for tg in recv if tg[4]}
                if ser:
                    self.whole_hits(n, ser, "m5", "substring test (.%s) on a serialization" % m)
                return recv | allargs
            if m in STR_METHODS:
                if m in ("read", "read_text"):
                    fids = resolve_call(self.fn, f)
                    lo = [fi for fi in fids if fi in LOADER]
                    if lo:
                        # C13: a .read() that resolves BY NAME to a loader method may be a file object's read(); keep both
                        return self.loader_result(n, lo, fids) | recv | allargs
                return recv | allargs
        # ---- builtins and library calls
        if fname in ("open", "io.open", "codecs.open"):
            return self.open_call(n)
        if fname in ("json.dump", "yaml.safe_dump", "yaml.dump") and len(n.args) >= 2:
            dest = n.args[1]
            names = set()
            if isinstance(dest, ast.Name) and dest.id in self.fn.fh:
                names = self.fn.fh[dest.id][0]
            elif isinstance(dest, ast.Call) and dotted(dest.func) == "open":
                names = file_ids(self.fn, dest.args[0])[0] if dest.args else set()
            self.write_file(names, argt[0], n)
            return set()
        if fname in SER_CALLS:
            whole = {tg for tg in allargs if not tg[4] and (tg[1] != () or not is_field_origin(tg[0]))}
            return {(o, p, via, full, True) for (o, p, via, full, ser) in allargs} if whole else allargs
        if fname in HASH_CALLS:
            whole = {tg for tg in allargs if tg[1] != () or not is_field_origin(tg[0]) or tg[4]}
            if whole:
                self.whole_hits(n, whole, "m4", "hashing of a structure / serialization")
            return {(o, p, via, full, False) for (o, p, via, full, ser) in allargs}
        if fname in RE_SEARCH:
            if allargs:
                self.whole_hits(n, {tg for tg in allargs if tg[4] or tg[1] != ()}, "m5", "regular-expression test on a serialization")
            return allargs
        if fname in ("os.path.exists", "os.path.isfile", "os.path.getsize", "os.remove", "os.unlink", "os.rename", "os.replace",
                     "glob.glob", "glob.iglob", "os.listdir", "os.scandir", "shutil.copy", "shutil.copyfile", "shutil.copy2", "shutil.move",
                     "os.stat", "os.path.getmtime", "os.path.isdir"):
            for a in n.args:
                self.site_file_op(n, a, fname)
        # ---- resolved scanned functions
        fids = resolve_call(self.fn, f)
        ret = set()
        if fname in CALL_PASSTHRU or last in ("sorted", "list", "tuple", "dict", "set", "min", "max", "sum", "any", "all", "len", "str",
                                                "int", "float", "round", "abs", "bool"):
            if not fids:
                ret |= {(o, p, via, full, ser) for (o, p, via, full, ser) in allargs}
                if last in ("dict",) and allargs:
                    maps = {tg for tg in allargs if tg[1] == () and not is_field_origin(tg[0])}
                    if maps:
                        self.whole_hits(n, maps, "m6", "dict(record) copies every key")
                if last in ("sorted", "list", "tuple", "set") and argt:
                    ret = set()
                    for a in argt:
                        ret |= a
                elif last == "len":
                    ret = set()
                elif last in ("min", "max", "sum", "any", "all") and argt:
                    ret = set()
                    for a in argt:
                        ret |= {tg for tg in strip_elem(a) if tg[1] == ()} | {tg for tg in a if tg[1] == ()}
                    ret = derived_scalar(ret, "<aggregate>") if last in ("sum", "any", "all") else ret
        # special sources and producer-internal child records
        for fi in fids:
            if fi in SOURCE_CALLS:
                src = SOURCE_CALLS[fi]
                if src in SOURCES_ENABLED:
                    ret.add(T(src))
                elif src == "S1" and "S3" in SOURCES_ENABLED and fi == "v2/v2_driver:solve" and passes_callgrind_timeout(n):
                    # a solve() result holds the S-3 record under instructions_callgrind only when the call passes a
                    # callgrind_timeout (v2_driver.py line 207; argument level, census.md lines 281-287) (M-13)
                    ret.add(T("S3", ("instructions_callgrind",)))
        key = (self.mod.rel, n.lineno)
        if key in S_LAUNCH_LINES_BY and last in S_LAUNCH_LINES_BY[key]["callees"] and S_LAUNCH_LINES_BY[key]["origin"].split("/")[0] in SOURCES_ENABLED:
            ret.add(T(S_LAUNCH_LINES_BY[key]["origin"]))
        if "C4" in SOURCES_ENABLED and key in C4_SITES and last == C4_SITES[key]["callee_last"]:
            ret.add(T("C4:%s:%d" % (self.mod.rel, n.lineno)))
        # walkers / collectors
        for fi in fids:
            if fi in WALKERS and allargs:
                self.whole_hits(n, {tg for tg in allargs if not tg[4]}, WALKERS[fi][0], "call of %s (%s)" % (FUNCS[fi].qual, WALKERS[fi][1]))
            if fi in WALKERS and WALKERS[fi][0] == "m2" and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
                COLLECTOR_RESULTS[id(n)] = collected(argt[0], n.args[1].value)
        # loaders / writers / hashers
        lo = [fi for fi in fids if fi in LOADER]
        if lo:
            ret |= self.loader_result(n, lo, fids)
        for fi in fids:
            if fi in WRITER:
                pi, oi = WRITER[fi]
                off = self.offset(fi, f)
                pa = self.arg_node(n, fi, pi - off)
                oa = self.arg_node(n, fi, oi - off)
                if pa is not None and oa is not None:
                    self.write_file(file_ids(self.fn, pa)[0], self.ev(oa), n)
                    self.site_file_op(n, pa, "write via " + FUNCS[fi].qual)
            if fi in HASHER:
                off = self.offset(fi, f)
                pa = self.arg_node(n, fi, HASHER[fi] - off)
                if pa is not None:
                    names, sitef, _ = file_ids(self.fn, pa)
                    for nm in names:
                        ft = self.file_tags(nm)
                        if ft:
                            self.whole_hits(n, ft, "m4", "sha256 of the file %s" % nm)
                    self.site_file_op(n, pa, "hash via " + FUNCS[fi].qual)
        # propagation into scanned callees
        for fi in fids:
            fo = FUNCS[fi]
            off = self.offset(fi, f)
            for i, a in enumerate(n.args):
                if isinstance(a, ast.Starred):
                    continue
                j = i + off
                if j < len(fo.params):
                    if argt[i]:
                        add_to(PARAM, (fi, fo.params[j]), argt[i])
                    self.callable_arg(fi, fo.params[j], a)
                    dep(("PM", fi, fo.params[j]), self.fn.fid)
                    self.apply_pmut(a, PMUT.get((fi, fo.params[j])), n)
            for k in n.keywords:
                if k.arg and k.arg in fo.params:
                    if kwt.get(k.arg):
                        add_to(PARAM, (fi, k.arg), kwt[k.arg])
                    self.callable_arg(fi, k.arg, k.value)
                    dep(("PM", fi, k.arg), self.fn.fid)
                    self.apply_pmut(k.value, PMUT.get((fi, k.arg)), n)
            if fi not in SOURCE_CALLS and id(n) not in COLLECTOR_RESULTS:
                dep(("R", fi), self.fn.fid)
                ret |= RET.get(fi, set())
            elif id(n) in COLLECTOR_RESULTS:
                ret |= {(o, (("[]",) + p)[:MAXPATH], via or "mem:%s:<collected>" % self.fn.fid, full, ser) for (o, p, via, full, ser) in COLLECTOR_RESULTS[id(n)]}
        # path / string builders: a string derived from their arguments (a scalar derived value, M-12)
        if fname.startswith("os.path.") or fname in ("str.join", "Path", "pathlib.Path") or last in ("basename", "dirname", "join", "relpath", "abspath",
                                                                                                      "normpath", "splitext", "format"):
            if not fids:
                return derived_scalar({tg for tg in allargs}, "<string>")
        # an unresolved call that is not a known library call: its value is derived from its arguments
        if not fids and fname not in CALL_PASSTHRU and not ret and fname not in ("print", "isinstance", "hasattr", "getattr", "type"):
            ret |= {(o, p, via, full, ser) for (o, p, via, full, ser) in allargs}
        if fname == "print" and allargs:
            whole = {tg for tg in allargs if tg[1] != () or not is_field_origin(tg[0])}
            if whole:
                self.whole_hits(n, whole, "m6", "printed whole")
        return ret

    def offset(self, fi, f):
        fo = FUNCS[fi]
        if "." in fo.qual and fo.params and fo.params[0] in ("self", "cls") and isinstance(f, ast.Attribute):
            return 1
        return 0

    def arg_node(self, n, fi, idx):
        fo = FUNCS[fi]
        if 0 <= idx < len(n.args):
            return n.args[idx]
        pname = fo.params[idx + self.offset(fi, n.func)] if 0 <= idx + self.offset(fi, n.func) < len(fo.params) else None
        for k in n.keywords:
            if k.arg == pname:
                return k.value
        return None

    def callable_arg(self, fi, pname, a):
        if isinstance(a, (ast.Name, ast.Attribute)):
            r = resolve_call(self.fn, a)
            if r:
                cur = CALLABLE_PARAM.setdefault(fi, {}).setdefault(pname, set())
                if not set(r) <= cur:
                    cur |= set(r)
                    CHANGED[0] = True
                    mark_dirty(fi)

    def loader_result(self, n, lo, fids):
        out = set()
        for fi in lo:
            off = self.offset(fi, n.func)
            pa = self.arg_node(n, fi, LOADER[fi] - off)
            if pa is None:
                continue
            names, sitef, _ = file_ids(self.fn, pa)
            for nm in names:
                out |= self.file_tags(nm, pa)
            for (site, suf, label) in sitef:
                s = site_of_file(self.fn, site)
                if s not in SOURCES_ENABLED:
                    continue
                tg = T(s + "/file:" + suf)
                self.hit(n, tg, label, "m8", "read via " + FUNCS[fi].qual)
                out.add(tg)
        return out

    def file_tags(self, name, path_node=None):
        if self.mod.tree == "tool" and MODULE_PIN.get(self.mod.key):
            PINNED_READS.add((self.mod.rel, getattr(path_node, "lineno", 0), name, MODULE_PIN[self.mod.key]))
            return set()
        if path_node is not None and self.mod.tree == "tool":
            pins = {c for c in str_consts(self.fn, path_node) if re.search(r"EXP-[A-Z0-9]+-[0-9a-f]{3,6}|EXP-[A-Z0-9]+-\d{3}", c)}
            if pins and not any("EXP-GFPN-05ff43" in c for c in pins):
                PINNED_READS.add((self.mod.rel, getattr(path_node, "lineno", 0), name, tuple(sorted(pins))[:3]))
                return set()
        dep(("F", name), self.fn.fid)
        return set(FILE_TAGS.get(name, set()))

    def open_call(self, n):
        if not n.args:
            return set()
        names, sitef, params = file_ids(self.fn, n.args[0])
        mode = "r"
        if len(n.args) > 1 and isinstance(n.args[1], ast.Constant):
            mode = str(n.args[1].value)
        for k in n.keywords:
            if k.arg == "mode" and isinstance(k.value, ast.Constant):
                mode = str(k.value.value)
        out = set()
        if "w" in mode or "a" in mode or "x" in mode:
            for (site, suf, label) in sitef:
                if site_of_file(self.fn, site) in SOURCES_ENABLED:
                    self.hit(n, T(site_of_file(self.fn, site) + "/file:" + suf), label, "m8", "open for write (%s)" % mode)
            return set()
        for nm in names:
            out |= self.file_tags(nm, n.args[0])
        for (site, suf, label) in sitef:
            if site_of_file(self.fn, site) not in SOURCES_ENABLED:
                continue
            tg = T(site_of_file(self.fn, site) + "/file:" + suf)
            self.hit(n, tg, label, "m8", "open for read (%s)" % mode)
            out.add(tg)
        return out

    def site_file_op(self, n, a, op):
        names, sitef, _ = file_ids(self.fn, a)
        for (site, suf, label) in sitef:
            if site_of_file(self.fn, site) in SOURCES_ENABLED:
                self.hit(n, T(site_of_file(self.fn, site) + "/file:" + suf), label, "m8", op)

    def write_file(self, names, tags, n):
        tags = {(o, p, via, full, False) for (o, p, via, full, ser) in tags}
        if not tags:
            return
        if RECORDING[0]:
            DERIVED_WRITES.append({"fid": self.fn.fid, "file": self.mod.rel, "line": n.lineno, "into": ["file:" + x for x in sorted(names)] or ["file:<unresolved path>"],
                                   "origins": sorted({o for (o, p, via, full, ser) in tags}), "from_via": sorted({via for (o, p, via, full, ser) in tags if via}),
                                   "paths": sorted({"/".join(p) for (o, p, via, full, ser) in tags})[:400]})
        whole = {tg for tg in tags if tg[1] != () or not is_field_origin(tg[0])}
        if whole:
            self.whole_hits(n, whole, "m6", "serializer writes every key to %s" % (",".join(sorted(names)) or "<unresolved path>"))
        for nm in names:
            add_to(FILE_TAGS, nm, {(o, p, "file:" + nm, p, False) for (o, p, via, full, ser) in tags})

    def store_into(self, cnode, tags, key, n, how):
        if self.cond and how in STORE_METHODS:
            try:
                self.note_control("%s.%s(...)" % (ast.unparse(cnode)[:60], how), n)
            except Exception:                            # noqa: BLE001
                pass
        if not tags:
            return
        keys = []
        c = cnode
        while isinstance(c, ast.Subscript):
            ks = self.keys_of(c.slice)
            keys.insert(0, sorted(ks)[0] if len(ks) == 1 else "*")
            c = c.value
        if key is not None:
            keys.append(key)
        root = c.id if isinstance(c, ast.Name) else (dotted(c) or "<expr>")
        new = set(tags)
        for kk in reversed(keys):
            new = {(o, ((kk,) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in new}
        new = {(o, p, via if via else "mem:%s:%s" % (self.fn.fid, root), full if via else p, ser) for (o, p, via, full, ser) in new}
        if RECORDING[0]:
            DERIVED_WRITES.append({"fid": self.fn.fid, "file": self.mod.rel, "line": n.lineno, "into": ["mem:%s:%s" % (self.fn.fid, root)],
                                   "key_path": keys, "how": how, "origins": sorted({tg[0] for tg in tags}),
                                   "from_via": sorted({tg[2] for tg in tags if tg[2]})})
        if isinstance(c, ast.Name):
            self.bind_weak(c.id, new)
            self.alias_mut(c.id, tags, keys)
        elif isinstance(c, ast.Attribute):
            if isinstance(c.value, ast.Name) and c.value.id in aliases(self.mod):
                for k in aliases(self.mod)[c.value.id]:
                    add_to(GLOBAL_ENV, (k, c.attr), new)
            else:
                add_to(ATTR, (self.mod.tree, c.attr), new)

    # C12 (M-20): mutation through an alias. A store into a local that aliases a container (doc = _STATE["doc"]; a = b)
    # also stores into that container; a store into a PARAMETER is recorded (PMUT) and applied to the caller's argument.
    def alias_mut(self, name, tags, keys, depth=0):
        fn = self.fn
        if depth > 3 or not tags or fn.fid.endswith((":<module>", ":<main>")):
            return
        if name in fn.params:
            rel = set(tags)
            for kk in reversed(list(keys)):
                rel = {(o, ((kk,) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in rel}
            rel = {(o, p, via if via else "mem:%s:%s" % (fn.fid, name), full if via else p, ser) for (o, p, via, full, ser) in rel}
            add_to(PMUT, (fn.fid, name), rel)
            return
        for v in list(fn.assigns.get(name, [])):
            vkeys, c = [], v
            while isinstance(c, ast.Subscript):
                ks = self.keys_of(c.slice)
                vkeys.insert(0, sorted(ks)[0] if len(ks) == 1 else "*")
                c = c.value
            if not isinstance(c, ast.Name) or c.id == name or (not vkeys and not isinstance(v, ast.Name)):
                continue
            root, allk = c.id, vkeys + list(keys)
            if root in fn.params:
                self.alias_mut(root, tags, allk, depth + 1)
                continue
            new = set(tags)
            for kk in reversed(allk):
                new = {(o, ((kk,) + p)[:MAXPATH], via, full, ser) for (o, p, via, full, ser) in new}
            new = {(o, p, via if via else "mem:%s:%s" % (fn.fid, root), full if via else p, ser) for (o, p, via, full, ser) in new}
            if root in fn.locals_:
                self.bind_weak(root, new)
                self.alias_mut(root, tags, allk, depth + 1)
            else:
                add_to(GLOBAL_ENV, (self.mod.key, root), new)

    def apply_pmut(self, a, pm, n):
        """The caller's side of C12: the argument expression receives what the callee stored into its parameter."""
        if not pm:
            return
        if isinstance(a, ast.Name):
            self.bind_weak(a.id, pm)
            self.alias_mut(a.id, pm, [])
        elif isinstance(a, ast.Subscript):
            self.store_into(a, pm, None, n, "mutated by the callee")

    # ----- statements
    def assign(self, tgt, tags, vnode):
        if self.cond and not isinstance(tgt, (ast.Tuple, ast.List)):
            try:
                self.note_control(ast.unparse(tgt)[:80], tgt)
            except Exception:                            # noqa: BLE001
                pass
        if isinstance(tgt, ast.Name):
            if vnode is not None:
                self.fn.assigns.setdefault(tgt.id, [])
                if vnode not in self.fn.assigns[tgt.id]:
                    self.fn.assigns[tgt.id].append(vnode)
                cv = const_value(vnode)
                if cv is not None:
                    self.fn.consts.setdefault(tgt.id, set()).update(set(cv) if isinstance(cv, tuple) else {cv})
                if isinstance(vnode, ast.Call) and dotted(vnode.func) == "open" and vnode.args:
                    mode = vnode.args[1].value if len(vnode.args) > 1 and isinstance(vnode.args[1], ast.Constant) else "r"
                    if any(x in str(mode) for x in "wax"):
                        nm, sf, _ = file_ids(self.fn, vnode.args[0])
                        self.fn.fh[tgt.id] = (nm, sf, mode)
            self.bind(tgt.id, tags)
        elif isinstance(tgt, (ast.Tuple, ast.List)):
            if isinstance(vnode, (ast.Tuple, ast.List)) and len(vnode.elts) == len(tgt.elts):
                for te, ve in zip(tgt.elts, vnode.elts):
                    self.assign(te, self.ev(ve), ve)
            else:
                el = strip_elem(tags) | {tg for tg in tags if tg[1] == ()}
                for te in tgt.elts:
                    self.assign(te, el, None)
        elif isinstance(tgt, ast.Subscript):
            self.ev(tgt.slice)
            self.store_into(tgt.value, tags | self.implicit(), sorted(self.keys_of(tgt.slice))[0] if len(self.keys_of(tgt.slice)) == 1 else "*", tgt, "subscript assignment")
        elif isinstance(tgt, ast.Attribute):
            if isinstance(tgt.value, ast.Name) and tgt.value.id in aliases(self.mod):
                for k in aliases(self.mod)[tgt.value.id]:
                    add_to(GLOBAL_ENV, (k, tgt.attr), tags | self.implicit())
            else:
                self.ev(tgt.value)
                if tags:
                    add_to(ATTR, (self.mod.tree, tgt.attr), tags | self.implicit())
        elif isinstance(tgt, ast.Starred):
            self.assign(tgt.value, tags, None)

    def block(self, stmts):
        for st in stmts:
            self.stmt(st)

    def _for_once(self, st):
        it = self.ev(st.iter)
        self.loop_target(st.target, st.iter, it)
        if isinstance(st.target, ast.Name) and self.fn.consts.get(st.target.id) and 1 < len(self.fn.consts[st.target.id]) <= 40 \
                and (const_value(st.iter) is not None or (isinstance(st.iter, ast.Name) and isinstance(self.fn.mod.consts.get(st.iter.id), tuple))):
            allk = set(self.fn.consts[st.target.id])
            acc = None
            s0 = dict(self.state)
            for kk in sorted(allk):
                self.state = dict(s0)
                self.fn.consts[st.target.id] = {kk}
                self.block(st.body)
                acc = self.state if acc is None else merge_states(acc, self.state)
            self.state = acc if acc is not None else self.state
            self.fn.consts[st.target.id] = allk
        else:
            self.block(st.body)

    def stmt(self, st):
        t = type(st)
        if t in (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef):
            return
        if t is ast.Assign:
            vt = self.ev(st.value)
            for tgt in st.targets:
                self.assign(tgt, vt, st.value)
        elif t is ast.AnnAssign:
            if st.value is not None:
                self.assign(st.target, self.ev(st.value), st.value)
        elif t is ast.AugAssign:
            vt = self.ev(st.value)
            if isinstance(st.target, ast.Name):
                vt |= self.lookup(st.target.id)
                self.bind(st.target.id, vt)
            else:
                self.assign(st.target, vt, None)
        elif t is ast.Expr:
            self.ev(st.value)
        elif t is ast.Return:
            rt = self.ev(st.value) | self.implicit()
            if self.fn.fid not in SOURCE_CALLS and rt:
                add_to(RET, self.fn.fid, rt)
        elif t is ast.If:
            tt = self.ev(st.test)
            self.cond.append({tg for tg in tt if not tg[4] and tg[1] == ()})
            s0 = dict(self.state)
            self.block(st.body)
            s1 = self.state
            self.state = dict(s0)
            self.block(st.orelse)
            self.state = merge_states(s1, self.state)
            self.cond.pop()
        elif t is ast.While:
            tt = self.ev(st.test)
            self.cond.append({tg for tg in tt if not tg[4] and tg[1] == ()})
            for _ in range(3):
                s0 = dict(self.state)
                self.block(st.body)
                self.state = merge_states(s0, self.state)
                if states_equal(s0, self.state):
                    break
            self.block(st.orelse)
            self.cond.pop()
        elif t in (ast.For, ast.AsyncFor):
            for _ in range(3):
                s0 = dict(self.state)
                self._for_once(st)
                self.state = merge_states(s0, self.state)
                if states_equal(s0, self.state):
                    break
            self.block(st.orelse)
        elif t in (ast.With, ast.AsyncWith):
            for item in st.items:
                ce = item.context_expr
                vt = self.ev(ce)
                if item.optional_vars is not None:
                    if isinstance(ce, ast.Call) and dotted(ce.func) in ("open", "io.open") and ce.args:
                        mode = "r"
                        if len(ce.args) > 1 and isinstance(ce.args[1], ast.Constant):
                            mode = str(ce.args[1].value)
                        for k in ce.keywords:
                            if k.arg == "mode" and isinstance(k.value, ast.Constant):
                                mode = str(k.value.value)
                        if isinstance(item.optional_vars, ast.Name) and any(x in mode for x in "wax"):
                            nm, sf, _ = file_ids(self.fn, ce.args[0])
                            self.fn.fh[item.optional_vars.id] = (nm, sf, mode)
                    self.assign(item.optional_vars, vt, ce)
            self.block(st.body)
        elif t is ast.Try or (hasattr(ast, "TryStar") and t is getattr(ast, "TryStar")):
            s0 = dict(self.state)
            self.block(st.body)
            self.block(st.orelse)
            acc = self.state
            for h in st.handlers:
                self.state = merge_states(s0, acc)
                self.block(h.body)
                acc = merge_states(acc, self.state)
            self.state = acc
            self.block(st.finalbody)
        elif t is ast.Global:
            self.fn.globals_ = getattr(self.fn, "globals_", set()) | set(st.names)
        elif t in (ast.Assert,):
            self.ev(st.test)
            self.ev(st.msg)
        elif t is ast.Raise:
            self.ev(st.exc)
        elif t is ast.Delete:
            for x in st.targets:
                self.ev(x)
        elif hasattr(ast, "Match") and t is ast.Match:
            self.ev(st.subject)
            for c in st.cases:
                self.block(c.body)


DERIVED_WRITES = []
COLLECTOR_RESULTS = {}


def collected(tags, key):
    """Summary of a generic key-name collector called with a constant key: the values found under that key (M-11)."""
    out = set()
    for (o, p, via, full, ser) in tags:
        if ser:
            continue
        hit_at = [i for i, x in enumerate(p) if x == key or x == "*"]
        for i in hit_at:
            # C2: a match at a computed-key position ("*") is an over-approximation; it is marked like sub()'s (M-14)
            wild = p[i] == "*" and not via.endswith(WILD)
            out.add((o, p[i + 1:], via + WILD if wild else via, full, ser))
        if not is_field_origin(o):
            # the record sits at the end of the path: its own key, or its sub-record's key
            if key in SCHEMA.get(o, set()):
                out.add((child_origin(o, key), (), via, full, ser))
            for sub in ("child", "solver"):
                if key in SCHEMA.get(o + "/" + sub, set()):
                    out.add((child_origin(child_origin(o, sub), key), (), via, full, ser))
    return out


CONTROL_WRITES = []
PINNED_READS = set()
MODULE_PIN = {}


MANUAL_PINS = {
    "harness/run_kerfield.py": "EXP-ICINV-fcb497 harness", "harness/exp_icinv_fullgroup.py": "EXP-ICINV harness",
    "harness/finite_yaml_locked_v1.py": "EXP-ECDLP-2cb7f8 / abf981 harness", "harness/finite_yaml_locked_v2.py": "EXP-ECDLP-2cb7f8 / abf981 harness",
    "harness/finite_yaml_locked_v3.py": "EXP-ECDLP-2cb7f8 / abf981 harness", "harness/exp_instr_36c8cf/refvalues_v2.py": "EXP-INSTR-36c8cf harness",
    "harness/exp_instr_36c8cf/refvalues.py": "EXP-INSTR-36c8cf harness", "harness/exp_instr_36c8cf/phase_a_v2.py": "EXP-INSTR-36c8cf harness",
    "harness/exp_icinv_e0cd8f/run_gate.py": "EXP-ICINV-e0cd8f harness", "harness/diffpath/main.py": "EXP-DIFFP-fe894e harness",
    "harness/diffpath/readmit.py": "EXP-DIFFP harness", "harness/diffpath/runs.py": "EXP-DIFFP-fe894e harness",
    "harness/diffpath/controlpower.py": "EXP-DIFFP harness", "harness/diffpath/depgraph.py": "EXP-DIFFP harness",
    "harness/run_fullgroup.py": "EXP-ICINV / EXP-INSTR harness", "harness/exp_icinv_geometry.py": "EXP-ICINV harness",
    "harness/run_md5_calib.py": "EXP-MDFIVE-001 harness", "harness/run_md4_ceiling_v2.py": "EXP-MDFIVE-a8e71e harness",
    "harness/run_md4_ceiling.py": "EXP-MDFIVE-88f7d1 harness", "harness/run_kerfield_stage0_v3.py": "EXP-ICINV-fcb497 harness",
    "harness/run_md4_seed_sweep.py": "GOAL-MD5-001 harness (docstring)", "harness/run_blocknull.py": "EXP-ICINV / EXP-INSTR harness",
    "tools/build_run_repair_20260808.py": "a fixed list of other experiments' run paths", "tools/sage_free_estimator/known_answer_control.py": "EXP-MLKEM-015 control",
    "tools/migrate_autolab_archive.py": "EXP-ALMIG-001 migration", "tools/port_autolab_experiments.py": "AutoLab archive port (source packages, not run packages of this experiment)",
    "tools/test_port_autolab_experiments.py": "unit-test fixtures", "tools/test_run_supersession.py": "unit-test fixtures",
    "tools/test_run_provenance_quarantine.py": "unit-test fixtures", "tools/test_review_independence_addenda.py": "unit-test fixtures",
}


def compute_module_pins():
    """A tool module is PINNED to another experiment when its module-level string constants name an experiment id and
    none of them is EXP-GFPN-05ff43: its run-package reads are of that experiment's packages, never of an r3 package."""
    for k, m in MODS.items():
        if m.tree != "tool":
            continue
        ids = set()
        for st in m.ast.body:
            if isinstance(st, (ast.Assign, ast.AnnAssign)):
                for x in ast.walk(st):
                    if isinstance(x, ast.Constant) and isinstance(x.value, str):
                        ids |= set(re.findall(r"EXP-[A-Z0-9]+-(?:[0-9a-f]{6}|\d{3})", x.value))
        if ids and "EXP-GFPN-05ff43" not in ids and "EXP-GFPN-05ff43" not in m.src:
            MODULE_PIN[k] = "module-level constant(s) " + ",".join(sorted(ids)[:3])
        if m.rel in MANUAL_PINS and "EXP-GFPN-05ff43" not in m.src:
            MODULE_PIN[k] = "MR-PIN: " + MANUAL_PINS[m.rel]
        elif os.path.basename(m.rel).startswith("test_") and "EXP-GFPN-05ff43" not in m.src:
            # C5: generalizes the four unit-test entries of MANUAL_PINS to every unit test the M-16b selection adds
            MODULE_PIN[k] = "MR-PIN-TEST: a unit test; it reads fixture packages it creates, never a run package of EXP-GFPN-05ff43"
WALKERS = {}
SOURCES_ENABLED = {"S1"}


def reset_engine(sources):
    for d in (PARAM, RET, FILE_TAGS, GLOBAL_ENV, ATTR, CALLABLE_PARAM, HITS, DEPS, CLOSURE_MUT, COLLECTOR_RESULTS, PMUT):
        d.clear()
    COLLAPSED.clear()
    DERIVED_WRITES.clear()
    CONTROL_WRITES.clear()
    DIRTY.clear()
    DIRTY_SET.clear()
    for fo in FUNCS.values():
        fo.env = {}
    SOURCES_ENABLED.clear()
    SOURCES_ENABLED.update(sources)
S_LAUNCH_LINES_BY = {}


# ----------------------------------------------------------------------------------------------- summaries
def pre_assigns(fo):
    out = {}
    for st in fo.body:
        if isinstance(st, ast.Assign):
            for tg in st.targets:
                if isinstance(tg, ast.Name):
                    out.setdefault(tg.id, []).append(st.value)
        elif isinstance(st, (ast.With, ast.AsyncWith)):
            for it in st.items:
                if isinstance(it.optional_vars, ast.Name):
                    out.setdefault(it.optional_vars.id, []).append(it.context_expr)
    return out


def depends_on_params(fo, n, pa, depth=0):
    idx = set()
    if n is None or depth > 3:
        return idx
    for nm in names_in(fo, n):
        if nm in fo.params:
            idx.add(fo.params.index(nm))
        for v in pa.get(nm, []):
            idx |= depends_on_params(fo, v, pa, depth + 1)
    return idx


def fn_nodes(fo):
    for st in fo.body:
        for x in ast.walk(st):
            if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)) and x is not fo.node:
                continue
            yield x


def compute_summaries():
    for fid, fo in FUNCS.items():
        if fo.node is None:
            continue
        pa = pre_assigns(fo)
        nodes = list(fn_nodes(fo))
        calls = [x for x in nodes if isinstance(x, ast.Call)]
        # walkers / collectors: recursive over mappings
        selfcall = any(fid in resolve_call(fo, c.func) for c in calls)
        iters_map = any((isinstance(c.func, ast.Attribute) and c.func.attr in ("items", "values")) for c in calls) or \
            any(isinstance(c.func, ast.Name) and c.func.id == "isinstance" and len(c.args) > 1 and "dict" in ast.unparse(c.args[1]) for c in calls)
        if selfcall and iters_map:
            coll = False
            for x in nodes:
                if isinstance(x, ast.Compare) and any(isinstance(op, ast.Eq) for op in x.ops):
                    sides = [x.left] + list(x.comparators)
                    if any(isinstance(sd, ast.Name) and sd.id in fo.params for sd in sides):
                        coll = True
            WALKERS[fid] = ("m2", "generic key-name collector") if coll else ("m3", "recursive walker")
        has_return = any(isinstance(x, ast.Return) and x.value is not None for x in nodes)
        has_hash = any("hashlib" in dotted(c.func) for c in calls)
        for c in calls:
            if dotted(c.func) in ("open", "io.open") and c.args:
                mode = "r"
                if len(c.args) > 1 and isinstance(c.args[1], ast.Constant):
                    mode = str(c.args[1].value)
                for k in c.keywords:
                    if k.arg == "mode" and isinstance(k.value, ast.Constant):
                        mode = str(k.value.value)
                dp = {i for i in depends_on_params(fo, c.args[0], pa) if fo.params[i] not in ("self", "cls")}
                if not dp:
                    continue
                pi = sorted(dp)[0]
                if any(x in mode for x in "wax"):
                    for c2 in calls:
                        d2 = dotted(c2.func)
                        if d2 in ("json.dump", "yaml.safe_dump", "yaml.dump") and c2.args:
                            oi = depends_on_params(fo, c2.args[0], pa)
                            if oi:
                                WRITER[fid] = (pi, sorted(oi)[0])
                        elif isinstance(c2.func, ast.Attribute) and c2.func.attr == "write" and c2.args:
                            oi = depends_on_params(fo, c2.args[0], pa) - {pi}
                            if oi:
                                WRITER[fid] = (pi, sorted(oi)[0])
                elif "b" in mode and has_hash:
                    HASHER[fid] = pi
                elif has_return:
                    LOADER[fid] = pi


# ----------------------------------------------------------------------------------------------- the fixpoint
def compute_locals(fo):
    loc = set(fo.params)
    for st in fo.raw:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            loc.add(st.name)
            continue
        for x in ast.walk(st):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store):
                loc.add(x.id)
            elif isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                loc.add(x.name)
            elif isinstance(x, ast.Global):
                loc -= set(x.names)
    return loc


def run_function(fo, recording=False):
    if not hasattr(fo, "locals_"):
        fo.locals_ = compute_locals(fo)
    fo.env = {}
    fo.consts = dict(fo.consts)
    ev = Ev(fo)

    def init():
        ev.state = {}
        for p in fo.params:
            t = PARAM.get((fo.fid, p))
            ev.state[p] = set(t) if t else set()
            if t:
                fo.env[p] = set(t)
    for _ in range(4):
        ev.local_changed = False
        init()
        ev.block(fo.raw)
        if not ev.local_changed:
            break
    if recording:
        RECORDING[0] = True
        init()
        ev.block(fo.raw)
        RECORDING[0] = False


def analyze_all(max_runs=400000):
    for fid in sorted(FUNCS):
        if not hasattr(FUNCS[fid], "locals_"):
            FUNCS[fid].locals_ = compute_locals(FUNCS[fid])
        mark_dirty(fid)
    runs = 0
    while DIRTY and runs < max_runs:
        fid = DIRTY.pop()
        DIRTY_SET.discard(fid)
        run_function(FUNCS[fid])
        runs += 1
        if PROGRESS[0] and runs % 2000 == 0:
            import time as _tt
            big = max((len(v) for v in FUNCS[fid].env.values()), default=0)
            print("runs", runs, "dirty", len(DIRTY), "fid", fid, "maxenv", big, round(_tt.time() - PROGRESS[0], 1), file=sys.stderr, flush=True)
    converged = not DIRTY
    for fid in sorted(FUNCS):
        run_function(FUNCS[fid], recording=True)
    return {"function_runs": runs, "converged": converged}


# ----------------------------------------------------------------------------------------------- loading the scanned files
def load_scanned(census, git_info):
    rep = {"experiment_trees": {}, "repo_tools": {"selected": [], "not_selected_literal_only_in_docstrings_or_comments": []},
           "embedded_code_strings": [], "parse_failures": []}
    for key in ("v1", "v2", "a1", "r1", "r2"):
        files = tree_py_files(TREES[key])
        rep["experiment_trees"][key] = files
        for rel in files:
            src = open(ab(rel)).read()
            OUT["files_read"][rel] = HASHES.get(rel) or sha(rel)
            name = os.path.basename(rel)[:-3]
            load_module(key + "/" + name, name, key, rel, src)
    # repository tools: every .py under tools/, harness/, orchestration/ carrying a run-package file name in a code string
    head_py = (git_info or {}).get("head_py", {})
    for d in REPO_TOOL_DIRS:
        for f in sorted(glob.glob(ab(d) + "/**/*.py", recursive=True)):
            rel = os.path.relpath(f, REPO)
            if "/__pycache__/" in rel:
                continue
            txt = open(f, errors="replace").read()
            names = [n for n in RUN_PACKAGE_FILES if n in txt]
            if not names and ("path_sha256" in txt or "artifact_sha256" in txt):
                # C5 / M-16b: a GENERIC archive or receipt verifier opens whatever an archive binds (run-package files
                # included) without naming them; it is a scanned file by the definition's "opens raw-result.json ..."
                try:
                    tree = ast.parse(txt)
                except SyntaxError as e:
                    rep["parse_failures"].append({"file": rel, "error": repr(e)})
                    continue
                disk = hashlib.sha256(open(f, "rb").read()).hexdigest()
                hp = head_py.get(rel)
                entry = {"file": rel, "names_in_code_strings": [], "selected_as": "generic archive / receipt verifier (path_sha256 or "
                         "artifact_sha256 in its source; M-16b)", "sha256_disk": disk, "sha256_HEAD": hp["sha256"] if hp else None,
                         "tracked": hp is not None, "disk_equals_HEAD": (hp["sha256"] == disk) if hp else None}
                rep["repo_tools"]["selected"].append(entry)
                OUT["files_read"][rel] = disk
                load_module("tool/" + rel[:-3], os.path.basename(rel)[:-3], "tool", rel, txt)
                continue
            if not names:
                continue
            try:
                tree = ast.parse(txt)
            except SyntaxError as e:
                rep["parse_failures"].append({"file": rel, "error": repr(e)})
                continue
            docs = set()
            for n in ast.walk(tree):
                if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body and \
                        isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant):
                    docs.add(id(n.body[0].value))
            code_names = sorted({nm for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs
                                 for nm in RUN_PACKAGE_FILES if nm in n.value})
            disk = sha_bytes(txt.encode()) if False else hashlib.sha256(open(f, "rb").read()).hexdigest()
            hp = head_py.get(rel)
            entry = {"file": rel, "names_in_code_strings": code_names, "names_anywhere": names, "sha256_disk": disk,
                     "sha256_HEAD": hp["sha256"] if hp else None, "tracked": hp is not None, "disk_equals_HEAD": (hp["sha256"] == disk) if hp else None}
            if code_names:
                rep["repo_tools"]["selected"].append(entry)
                OUT["files_read"][rel] = disk
                name = os.path.basename(rel)[:-3]
                load_module("tool/" + rel[:-3], name, "tool", rel, txt)
            else:
                rep["repo_tools"]["not_selected_literal_only_in_docstrings_or_comments"].append(entry)
    # embedded code strings the census parsed (census.json CN1_msolve_launch_census.embedded_code_strings)
    for e in census["CN1_msolve_launch_census"]["embedded_code_strings"]:
        rel = e["file"]
        m = None
        for k, mm in MODS.items():
            if mm.rel == rel:
                m = mm
        found = None
        if m is not None:
            for n in ast.walk(m.ast):
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and hashlib.sha256(n.value.encode()).hexdigest() == e["string_sha256"]:
                    found = n
                    break
        ent = {"file": rel, "line": e["line"], "string_sha256": e["string_sha256"], "located": found is not None,
               "parses_as_python": None, "text_hits": []}
        if found is not None:
            try:
                ast.parse(found.value)
                ent["parses_as_python"] = True
            except SyntaxError:
                ent["parses_as_python"] = False
            ent["is_docstring"] = any(isinstance(p, (ast.Module, ast.FunctionDef, ast.ClassDef)) and p.body and isinstance(p.body[0], ast.Expr)
                                      and p.body[0].value is found for p in ast.walk(m.ast))
            ent["text_hits"] = embedded_text_hits(found.value)
            if ent["parses_as_python"] and not ent["is_docstring"]:
                load_module("embedded/%s:%d" % (rel, e["line"]), "embedded_%d" % e["line"], "embedded", rel + "#L%d" % e["line"], found.value, pseudo=True)
        rep["embedded_code_strings"].append(ent)
    return rep


ALL_FIELD_NAMES = set()


def embedded_text_hits(txt):
    out = []
    for k in sorted(ALL_FIELD_NAMES):
        if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(k), txt):
            out.append({"token": k, "kind": "site-record field name"})
    for suf, site, label in SITE_FILE_SUFFIXES:
        if suf in txt:
            out.append({"token": suf, "kind": "site file name (%s)" % label})
    return out


def site_record_fields():
    """Field names of the three site records, read statically from the frozen producers (definitions)."""
    f = {"S-1": set(), "S-1 solver": set(), "S-3": set(), "S-3 child": set(), "S-2": set(), "S-2 child": set()}
    # S-1: keys solve() sets on res, _slim's key tuple, res["solver"]["instructions"], _retain's keys
    for fid in ("v2/v2_driver:solve", "v2/v2_driver:_retain"):
        fo = FUNCS[fid]
        for x in ast.walk(fo.node):
            if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id == "res" and isinstance(x.slice, ast.Constant):
                f["S-1"].add(x.slice.value)
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == "update" and isinstance(x.func.value, ast.Name) and x.func.value.id == "res":
                f["S-1"] |= {k.arg for k in x.keywords if k.arg}
            if isinstance(x, ast.Dict) and fid.endswith(":solve"):
                pass
    fo = FUNCS["v2/v2_driver:solve"]
    for x in ast.walk(fo.node):
        if isinstance(x, ast.Assign) and isinstance(x.targets[0], ast.Name) and x.targets[0].id == "res" and isinstance(x.value, ast.Dict):
            f["S-1"] |= {k.value for k in x.value.keys if isinstance(k, ast.Constant)}
    for x in ast.walk(FUNCS["v2/v2_driver:_slim"].node):
        cv = const_value(x) if isinstance(x, ast.Tuple) else None
        if cv:
            f["S-1 solver"] |= set(cv)
    f["S-1 solver"].add("instructions")
    # S-3
    for x in ast.walk(FUNCS["v2/v2_solver:callgrind_instructions"].node):
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id == "res" and isinstance(x.slice, ast.Constant):
            f["S-3"].add(x.slice.value)
        if isinstance(x, ast.Assign) and isinstance(x.targets[0], ast.Name) and x.targets[0].id == "res" and isinstance(x.value, ast.Dict):
            f["S-3"] |= {k.value for k in x.value.keys if isinstance(k, ast.Constant)}
            for k, v in zip(x.value.keys, x.value.values):
                if isinstance(k, ast.Constant) and k.value == "child":
                    for y in ast.walk(v):
                        cv = const_value(y) if isinstance(y, ast.Tuple) else None
                        if cv:
                            f["S-3 child"] |= set(cv)
    # S-2
    for x in ast.walk(FUNCS["a1/a1_health:run_system"].node):
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id == "res" and isinstance(x.slice, ast.Constant):
            f["S-2"].add(x.slice.value)
        if isinstance(x, ast.Assign) and isinstance(x.targets[0], ast.Name) and x.targets[0].id == "res" and isinstance(x.value, ast.Dict):
            f["S-2"] |= {k.value for k in x.value.keys if isinstance(k, ast.Constant)}
            for k, v in zip(x.value.keys, x.value.values):
                if isinstance(k, ast.Constant) and k.value == "child":
                    for y in ast.walk(v):
                        cv = const_value(y) if isinstance(y, ast.Tuple) else None
                        if cv:
                            f["S-2 child"] |= set(cv)
    # keys a1_health derives from the run_system record (census.md lines 300-308): the entry and report keys of run()
    for x in ast.walk(FUNCS["a1/a1_health:run"].node):
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id in ("entry", "report") and isinstance(x.slice, ast.Constant):
            f["S-2"].add("run()." + x.slice.value)
    return {k: sorted(v) for k, v in f.items()}


def setup_launch_sources(census):
    """Classified launches (sources inside the frozen producers) and the CU-4 non-msolve child launches, from the
    archived census.json all_launch_calls (read, not recomputed)."""
    S_LAUNCH_LINES_BY.clear()
    S_LAUNCH_LINES_BY[(V2 + "/v2_driver.py", 166)] = {"origin": "S1/childrec", "callees": {"run_child"}}
    S_LAUNCH_LINES_BY[(A1 + "/a1_health.py", 147)] = {"origin": "S2/childrec", "callees": {"run_child"}}
    S_LAUNCH_LINES_BY[(V2 + "/v2_solver.py", 517)] = {"origin": "S3/childrec", "callees": {"run_child"}}
    S_LAUNCH_LINES_BY[(V2 + "/v2_solver.py", 533)] = {"origin": "S3/childrec", "callees": {"run"}}
    listed = []
    for x in census["all_launch_calls"]:
        key = (x["file"], x["line"])
        if x.get("msolve_in_argv") or key in S_LAUNCH_LINES_BY:
            continue
        prog = x.get("program") or ""
        if prog.startswith("(forwards parameter") or x["callee"] in ("os.fork", "os.execv", "os.execve"):
            listed.append({"file": x["file"], "line": x["line"], "function": x["function"], "callee": x["callee"], "program": prog,
                           "tainted": False, "why": "primitive inside a launcher (forwards its parameter); its caller's launch is listed"})
            continue
        C4_SITES[key] = {"callee_last": x["callee"].split(":")[-1].split(".")[-1], "program": prog, "function": x["function"]}
        listed.append({"file": x["file"], "line": x["line"], "function": x["function"], "callee": x["callee"], "program": prog, "tainted": True})
    return listed


def aggregate_hits():
    agg = {}
    for h in HITS.values():
        k = (h["file"], h["line"], h["site"], h["field"], h["mode"])
        a = agg.get(k)
        if a is None:
            a = agg[k] = {"file": h["file"], "line": h["line"], "fid": h["fid"], "function": h["function"], "tree": h["tree"],
                          "site": h["site"], "field": h["field"], "mode": h["mode"], "origins": set(), "vias": set(), "fulls": set(),
                          "nodes": [], "notes": set()}
        a["origins"].add(h["origin"])
        if h["via"]:
            a["vias"].add(h["via"])
        if h["full"]:
            a["fulls"].add(h["full"])
        a.setdefault("paths", set()).update(h.get("paths") or ())
        a["nodes"].append(h["node"])
        a["nodes"].sort(key=lambda nd: (getattr(nd, "lineno", 0), getattr(nd, "col_offset", 0), type(nd).__name__))
        if h["note"]:
            a["notes"].add(h["note"])
    return agg


def dev_summary():
    import collections
    ag = aggregate_hits()
    print("AGG", len(ag), collections.Counter(a["site"] for a in ag.values()))
    cf = collections.Counter(a["file"] for a in ag.values())
    print("BYFILE", cf.most_common(60))
    if "--show" in sys.argv:
        for k in sorted(ag):
            a = ag[k]
            if a["site"] == "S-3":
                print("H3", a["file"].split("/")[-1], a["line"], a["function"], a["field"][:50], a["mode"], sorted(a["vias"])[:2], "|", MODS_BY_REL.get(a["file"], None) and MODS_BY_REL[a["file"]].line(a["line"]).strip()[:120])
    cf = collections.Counter(h["fid"] for h in HITS.values())
    for k, v in cf.most_common(25):
        print("FN", k, v)
    co = collections.Counter(h["origin"] for h in HITS.values())
    print("ORIGINS", co.most_common(30))
    fl = [k for k in FILE_TAGS]
    for k in ("raw-result.json", "manifest.yaml", "environment.json", "command.txt"):
        print("FILE", k, len(FILE_TAGS.get(k, ())), sorted(FILE_TAGS.get(k, ()))[:12])
    for fid in sorted(FUNCS):
        if fid.startswith(("v2/v2_driver", "v2/v2_scoring", "v2/v2_common")):
            for var, tg in sorted(FUNCS[fid].env.items()):
                roots = [t for t in tg if t[0] == "S3" and t[1] == ()]
                if roots:
                    print("ROOT", fid, var, [(t[2], t[3]) for t in roots][:3])
    for w in DERIVED_WRITES[:0]:
        if any("raw-result.json" in x for x in w["into"]):
            print("WRITE", w["fid"], w["line"], w["origins"][:6], w["from_via"][:4], [x for x in w.get("paths", []) if x.startswith(("metrics", "comparisons", "ac5"))][:10])
    c = collections.Counter((h["site"], h["mode"]) for h in HITS.values())
    for k, v in sorted(c.items()):
        print(k, v)
    print("hits", len(HITS), "derived writes", len(DERIVED_WRITES), "files", sorted(FILE_TAGS))


# ===================================================================================================== 4. EFFECT CLASSES
OUTCOME_RE = re.compile(r"^(outcome|reason|v2_outcome_class|v2_outcome_reason|clause|ssf_clause|run_status|failure_class|fclass|status|"
                        r"solver_side_signal|sig|class|final_outcome|final_reason|final_ssf_clause|outcome_class|accepted_attempt)$")
CHECK_TARGET_RE = re.compile(r"(pass|^ok$|_ok$|^ok_|gate|verdict|equal|valid|consisten|^checks?$|match|violat|^errs?$|^fails?$|^reasons$|^bad$|"
                             r"mismatch|refus|^viol$|same|identical|holds|agree|^eq$|^diff$)", re.I)
CHECK_FUNC_RE = re.compile(r"(check|verify|compare|gate|consisten|valid|readback|preflight|_ok$|refus|assert|^b$|equal)", re.I)
FAIL_APPEND_RE = re.compile(r"(err|fail|reason|viol|problem|bad|issue|mismatch|refus|diff)", re.I)
D_TARGET_RE = re.compile(r"^(D|D_defined|degree|elim_degree|dimension|dim|D_values|ideal_degree_D|sols|solutions|Dcell|Dq|Du|Dsr|Dn|Dd|"
                         r"n_rational_solutions|rels|pts|lifted|D_[A-Za-z_]*|final_D|recorded_D|dims|kind|payload|sinfo|nfail)$")
AGG_TARGET_RE = re.compile(r"(ratio|median|mean|metric|count|rate|^n_|total|variation|log2|score|heur_dflat|^F\d|^T-\d|band|stat|summary|"
                           r"^agg|table|counters|spent)", re.I)
AGG_CALL_RE = re.compile(r"^(sum|min|max|statistics\..*|mean|median|math\.log2?|.*score.*|.*cell_D|.*ratio_block|.*aggregate.*|Counter|"
                         r".*dflat.*|.*d_table)$")
D_CALL_RE = re.compile(r"(rational_solutions|substitute|lift|parse_msolve_param|sign_search|g2_orbit|param_substitution|degree|descend)")
E1_CALL_RE = re.compile(r"(classify|ssf_clause|clause$|outcome_of)")
REPORT_CALL_RE = re.compile(r"^(print|.*\.write|log|.*\.info|.*\.warning|.*\.debug|.*stderr.*)$")
REPORT_TARGET_RE = re.compile(r"^(L|lines|out_lines|md|notes|note|txt|text|report_lines|msg|lines_md|summary_lines|out_md)$")
E_ORDER = ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]


def parent(mod, n):
    return mod.parents.get(n)


def target_names(t):
    out = []
    for x in ast.walk(t):
        if isinstance(x, ast.Name):
            out.append(x.id)
        elif isinstance(x, ast.Subscript) and isinstance(x.slice, ast.Constant) and isinstance(x.slice.value, str):
            out.append(x.slice.value)
        elif isinstance(x, ast.Attribute):
            out.append(x.attr)
    return out


def best(effs):
    effs = [e for e in effs if e is not None]
    if not effs:
        return None
    return min(effs, key=lambda e: E_ORDER.index(e[0]))


def classify_block(stmts, mod):
    """Effect of code governed by a decision: the strongest effect its statements produce."""
    found = []
    for st in stmts:
        for x in ast.walk(st):
            if isinstance(x, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tg = x.targets if isinstance(x, ast.Assign) else [x.target]
                names = [nm for t in tg for nm in target_names(t)]
                if any(OUTCOME_RE.match(nm) for nm in names):
                    found.append(("E1", "R-DEC-E1: the governed branch assigns an outcome / reason / status / class"))
                elif any(CHECK_TARGET_RE.search(nm) for nm in names):
                    found.append(("E2", "R-DEC-E2: the governed branch assigns a pass / ok / gate / verdict value"))
                elif any(D_TARGET_RE.match(nm) for nm in names):
                    found.append(("E3", "R-DEC-E3: the governed branch assigns D / solutions / degree"))
                elif any(AGG_TARGET_RE.search(nm) for nm in names):
                    found.append(("E4", "R-DEC-E4: the governed branch assigns an aggregate / statistic"))
                else:
                    found.append(("E5", "R-DEC-E5: the governed branch stores values"))
            elif isinstance(x, ast.Raise) or (isinstance(x, ast.Call) and dotted(x.func) in ("sys.exit", "exit", "os._exit", "refuse")):
                found.append(("E2", "R-DEC-E2: the governed branch raises / exits / refuses"))
            elif isinstance(x, ast.Return):
                if isinstance(x.value, ast.Constant) and x.value.value in (False, 1, 2, 3, "FAIL"):
                    found.append(("E2", "R-DEC-E2: the governed branch returns a failure value"))
                else:
                    found.append(("E5", "R-DEC-E5: the governed branch returns a value"))
            elif isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr in ("append", "extend", "add", "update"):
                recv = dotted(x.func.value)
                last = recv.split(".")[-1] if recv else ""
                if FAIL_APPEND_RE.search(last):
                    found.append(("E2", "R-DEC-E2: the governed branch records a failure (%s.%s)" % (last, x.func.attr)))
                elif REPORT_TARGET_RE.match(last):
                    found.append(("E6", "R-DEC-E6: the governed branch appends report text"))
                elif OUTCOME_RE.match(last):
                    found.append(("E1", "R-DEC-E1: the governed branch updates an outcome record"))
                else:
                    found.append(("E5", "R-DEC-E5: the governed branch stores values (%s.%s)" % (last, x.func.attr)))
            elif isinstance(x, ast.Call) and REPORT_CALL_RE.match(dotted(x.func) or ""):
                found.append(("E6", "R-DEC-E6: the governed branch prints / writes text"))
            elif isinstance(x, (ast.Continue, ast.Break)):
                found.append(("E5", "R-DEC-E5: the governed branch skips / stops a loop that builds values"))
    return best(found)


def classify_node(mod, fo, node, depth=0, seen=None):
    """(effect, rule) of one accessed value, from its ast context. None when no rule applies."""
    seen = seen if seen is not None else set()
    if depth > 4 or id(node) in seen:
        return None
    seen.add(id(node))
    cur = node
    callees = []
    passed_compare = False
    while True:
        par = parent(mod, cur)
        if par is None:
            return None
        # decisions
        if isinstance(par, (ast.If, ast.While)) and cur is par.test:
            r = classify_block(par.body + par.orelse, mod)
            return r or ("E7", "R-DEC-NONE: the decision governs no store, check, outcome or report")
        if isinstance(par, ast.Assert):
            return ("E2", "R-ASSERT: assert statement")
        if isinstance(par, ast.IfExp) and cur is par.test:
            r = classify_node(mod, fo, par, depth + 1, seen)
            return r and (r[0], "R-IFEXP (selects a value): " + r[1])
        if isinstance(par, ast.comprehension) and cur in par.ifs:
            comp = parent(mod, par)
            r = classify_node(mod, fo, comp, depth + 1, seen)
            return r and (r[0], "R-FILTER (filters a comprehension): " + r[1])
        if isinstance(par, ast.comprehension) and cur is par.iter:
            comp = parent(mod, par)
            r = classify_node(mod, fo, comp, depth + 1, seen)
            return r and (r[0], "R-ITER (iterated by a comprehension): " + r[1])
        if isinstance(par, ast.Call):
            d = dotted(par.func)
            if cur is not par.func:
                callees.append(d)
                if E1_CALL_RE.search(d or ""):
                    return ("E1", "R-CALL-E1: argument of %s" % d)
                if D_CALL_RE.search(d or ""):
                    return ("E3", "R-CALL-E3: argument of %s" % d)
                if AGG_CALL_RE.match(d or ""):
                    return ("E4", "R-CALL-E4: argument of %s" % d)
                if REPORT_CALL_RE.match(d or ""):
                    return ("E6", "R-CALL-E6: argument of %s" % d)
                if isinstance(par.func, ast.Attribute) and par.func.attr in ("append", "extend", "add", "update", "insert", "setdefault"):
                    last = (dotted(par.func.value) or "").split(".")[-1]
                    if FAIL_APPEND_RE.search(last):
                        return ("E2", "R-APPEND-E2: recorded as a failure (%s.%s)" % (last, par.func.attr))
                    if REPORT_TARGET_RE.match(last):
                        return ("E6", "R-APPEND-E6: appended to report text (%s)" % last)
                    if OUTCOME_RE.match(last):
                        return ("E1", "R-APPEND-E1: updates an outcome record (%s)" % last)
                    return ("E5", "R-APPEND-E5: stored into %s" % (last or "a structure"))
                if d in ("json.dump", "yaml.safe_dump", "yaml.dump") or (isinstance(par.func, ast.Attribute) and par.func.attr == "write"):
                    return ("E5", "R-WRITE-E5: written to a file")
                if fo is not None:
                    r = classify_arg(mod, fo, par, cur, depth, seen)
                    if r is not None:
                        return r
        if isinstance(par, ast.Compare):
            passed_compare = True
        if isinstance(par, ast.stmt):
            break
        cur = par
    st = par
    if isinstance(st, ast.Return):
        name = fo.qual.split(".")[-1] if fo is not None else ""
        if E1_CALL_RE.search(name):
            return ("E1", "R-RET-E1: returned by the classifier %s" % name)
        if CHECK_FUNC_RE.search(name) and (passed_compare or "pass" in name):
            return ("E2", "R-RET-E2: returned by the check %s" % name)
        return ("E5", "R-RET-E5: returned to the callers (their reads are hits of their own)")
    if isinstance(st, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        tg = st.targets if isinstance(st, ast.Assign) else [st.target]
        names = [nm for t in tg for nm in target_names(t)]
        simple_locals = [t.id for t in tg if isinstance(t, ast.Name)]
        if any(OUTCOME_RE.match(nm) for nm in names):
            return ("E1", "R-ASSIGN-E1: assigned to %s" % ",".join(names[:3]))
        if any(CHECK_TARGET_RE.search(nm) for nm in names):
            return ("E2", "R-ASSIGN-E2: assigned to %s" % ",".join(names[:3]))
        if any(D_TARGET_RE.match(nm) for nm in names):
            return ("E3", "R-ASSIGN-E3: assigned to %s" % ",".join(names[:3]))
        if any(AGG_TARGET_RE.search(nm) for nm in names) and passed_compare is False:
            return ("E4", "R-ASSIGN-E4: assigned to %s" % ",".join(names[:3]))
        if any(REPORT_TARGET_RE.match(nm) for nm in names):
            return ("E6", "R-ASSIGN-E6: assigned to report text %s" % ",".join(names[:3]))
        if simple_locals and fo is not None:
            uses = []
            for nm in simple_locals:
                for x in fn_all_nodes(fo):
                    if isinstance(x, ast.Name) and x.id == nm and isinstance(x.ctx, ast.Load):
                        uses.append(x)
            effs = [classify_node(mod, fo, u, depth + 1, seen) for u in uses[:40]]
            r = best(effs)
            if r is not None:
                return (r[0], "R-DEFUSE (via local %s): %s" % (",".join(simple_locals), r[1]))
            if not uses:
                return ("E7", "R-DEAD: assigned to a local that is never read")
            return None
        return ("E5", "R-STORE-E5: stored into %s" % ",".join(names[:3]))
    if isinstance(st, ast.Expr):
        # C4: a statement-level call whose value is discarded
        v = st.value
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr in (
                "pop", "setdefault", "update", "append", "extend", "insert", "add", "remove", "discard", "clear"):
            return ("E5", "R-EXPR-MUT: statement-level %s on a stored structure; the value is stored or discarded, no decision "
                          "depends on it" % v.func.attr)
        return None
    if isinstance(st, (ast.For, ast.AsyncFor)) and cur is st.iter:
        uses = []
        tnames = [x.id for x in ast.walk(st.target) if isinstance(x, ast.Name)]
        for x in ast.walk(ast.Module(body=st.body, type_ignores=[])):
            if isinstance(x, ast.Name) and x.id in tnames and isinstance(x.ctx, ast.Load):
                uses.append(x)
        effs = [classify_node(mod, fo, u, depth + 1, seen) for u in uses[:40]]
        r = best(effs)
        if r is not None:
            return (r[0], "R-LOOP (via loop variable %s): %s" % (",".join(tnames), r[1]))
        blk = classify_block(st.body, mod)
        return blk and (blk[0], "R-LOOP-BODY: " + blk[1])
    if isinstance(st, (ast.With, ast.AsyncWith)):
        return ("E7", "R-WITH: context manager")
    return None


def classify_arg(mod, fo, call, argnode, depth, seen):
    """R-ARG: an argument passed to a scanned function takes the effect of that function's uses of the parameter."""
    fids = [f for f in resolve_call(fo, call.func) if f in FUNCS and FUNCS[f].node is not None]
    if not fids:
        return None
    effs = []
    for fi in fids[:4]:
        callee = FUNCS[fi]
        off = 1 if ("." in callee.qual and callee.params and callee.params[0] in ("self", "cls") and isinstance(call.func, ast.Attribute)) else 0
        pname = None
        if isinstance(argnode, ast.keyword):          # C3: a keyword argument names its parameter
            pname = argnode.arg
        elif argnode in call.args:
            j = call.args.index(argnode) + off
            pname = callee.params[j] if j < len(callee.params) else None
        else:
            for k in call.keywords:
                if k.value is argnode:
                    pname = k.arg
        if not pname:
            continue
        uses = [x for x in fn_all_nodes(callee) if isinstance(x, ast.Name) and x.id == pname and isinstance(x.ctx, ast.Load)]
        cm = MODS[callee.mod.key]
        r = best([classify_node(cm, callee, u, depth + 1, seen) for u in uses[:30]])
        if r is not None:
            effs.append((r[0], "R-ARG (parameter %s of %s): %s" % (pname, callee.qual, r[1])))
        elif not uses:
            effs.append(("E7", "R-ARG-UNUSED: parameter %s of %s is never read" % (pname, callee.qual)))
    return best(effs)


FN_NODES_CACHE = {}


def fn_all_nodes(fo):
    if fo.fid not in FN_NODES_CACHE:
        out = []
        for st in fo.raw:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            out += list(ast.walk(st))
        FN_NODES_CACHE[fo.fid] = out
    return FN_NODES_CACHE[fo.fid]


DEV_MODULES = {"r2/r2_dv12", "r2/r2_dv6", "r2/r2_devchecks", "r2/r2_devchecks_more", "r1/r1_dv6", "r1/r1_devchecks", "r1/r1_devchecks_more",
               "r1/r1_toy", "a1/a1_toy", "a1/a1_devchecks"}
REACH_ANY = set()


def classify_hit(a):
    """Effect class of an aggregated hit, with the rule that classified it."""
    mod = MODS_BY_REL.get(a["file"])
    fo = FUNCS.get(a["fid"])
    notes = " ".join(sorted(a["notes"]))
    mode = a["mode"]
    modkey = a["fid"].split(":")[0]
    if modkey in DEV_MODULES and a["fid"] not in REACH_ANY:
        return ("E6", "R-DEV: a development-check harness (%s), reached by no r2 command, wrapper, checker or tool; its outputs are "
                      "development bundles and reports (the draft classes r2_dv12.py, r1_toy.py and a1_toy.py readers as E6)" % modkey.split("/")[1])
    if a["site"] == "S-3" and a["fid"] == PRODUCERS["S3"]:
        return ("E5", "R-PROD: inside the frozen S-3 producer v2_solver.callgrind_instructions: builds the S-3 record from its child record "
                      "and the callgrind outputs")
    if mode == "m8":
        if "open for write" in notes or notes.startswith("write via"):
            return ("E7", "R-F-WRITE: the file is created / written here, nothing is read from it")
        if any(w in notes for w in ("os.remove", "os.unlink")):
            return ("E7", "R-F-REMOVE: removal; no output depends on the content")
        if any(w in notes for w in ("os.rename", "os.replace", "shutil.move")):
            return ("E7", "R-F-RENAME: rename; no output depends on the content")
    if fo is not None and fo.fid in WALKERS and mode in ("m6", "m7+m1", "m1", "m4", "m2", "m3"):
        return ("E7", "R-WALK-INT: traversal inside the %s %s; the call-site hit carries its effect" % (WALKERS[fo.fid][1], fo.qual))
    if mode == "m3":
        keys = walker_keys(a)
        if keys is not None and not any(site_has_key(a["site"], k) for k in keys):
            return ("E7", "R-WALK-KEY: the walker (and its callbacks) test only the keys %s, none a key of the %s record" % (sorted(keys)[:6], a["site"]))
    if mode in ("m2",):
        key = collector_key(a)
        if key is not None and not site_has_key(a["site"], key):
            return ("E7", "R-COLL-KEY: collects key %r, which the %s record does not carry" % (key, a["site"]))
    if mode == "m5":
        lits = m5_literals(a)
        if lits is not None and not any(site_has_key(a["site"], x) or any(suf in x for suf, _, _ in SITE_FILE_SUFFIXES) for x in lits):
            return ("E7", "R-M5-LIT: tests only for literal(s) %s, none a field name of the %s record" % (sorted(lits)[:4], a["site"]))
    if "serializer writes every key" in notes:
        return ("E5", "R-SER-WRITE: serialized into a file")
    if "printed whole" in notes:
        return ("E6", "R-PRINT: printed")
    effs = []
    for nd in a["nodes"][:12]:
        r = classify_node(mod, fo, nd) if mod is not None else None
        effs.append(r)
    r = best(effs)
    return r


def walker_keys(a):
    """String constants a walker call's walker and callback functions test (in comparisons / .get / membership)."""
    fo = FUNCS.get(a["fid"])
    fids = set()
    for nd in a["nodes"]:
        if isinstance(nd, ast.Call) and fo is not None:
            for fi in resolve_call(fo, nd.func):
                if fi in WALKERS:
                    fids.add(fi)
            for arg in nd.args:
                if isinstance(arg, (ast.Name, ast.Attribute)):
                    fids |= set(resolve_call(fo, arg))
    if not fids:
        return None
    keys = set()
    for fi in fids:
        for x in fn_all_nodes(FUNCS[fi]):
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == "get" and x.args and isinstance(x.args[0], ast.Constant):
                keys.add(str(x.args[0].value))
            elif isinstance(x, ast.Compare):
                for c in [x.left] + list(x.comparators):
                    cv = const_value(c)
                    if cv is not None:
                        keys |= set(cv) if isinstance(cv, tuple) else {cv}
            elif isinstance(x, ast.Subscript) and isinstance(x.slice, ast.Constant) and isinstance(x.slice.value, str):
                keys.add(x.slice.value)
    return keys


def site_has_key(site, key):
    if site == "S-3":
        return key in SCHEMA.get("S3", set()) or key in SCHEMA.get("S3/child", set()) or key == "instructions_callgrind"
    if site == "S-1":
        return key in SCHEMA.get("S1", set()) or key in SCHEMA.get("S1/solver", set())
    if site == "S-2":
        return key in SCHEMA.get("S2", set()) or key in SCHEMA.get("S2/child", set())
    return True


def collector_key(a):
    mod = MODS_BY_REL.get(a["file"])
    for nd in a["nodes"]:
        if isinstance(nd, ast.Call) and len(nd.args) >= 2 and isinstance(nd.args[1], ast.Constant) and isinstance(nd.args[1].value, str):
            return nd.args[1].value
    return None


def m5_literals(a):
    fo = FUNCS.get(a["fid"])
    out = set()
    for nd in a["nodes"]:
        if isinstance(nd, ast.Compare):
            left = nd.left
            if isinstance(left, ast.Constant) and isinstance(left.value, str):
                out.add(left.value)
            elif fo is not None:
                cs = str_consts(fo, left)
                if not cs:
                    return None
                out |= cs
        elif isinstance(nd, ast.Call):
            if nd.args and fo is not None:
                cs = str_consts(fo, nd.args[0])
                if not cs:
                    return None
                out |= cs
            else:
                return None
    return out or None


# ----------------------------------------------------------------------------------------------- M-16 file-hash census
# C5 (this task's addition to the partial script). Mode m4 names HASHING. The taint engine sees hashing of a tainted
# VALUE (HASH_CALLS) and of a file whose path is a constant (HASHER helpers); a hash of a FILE whose path arrives as a
# parameter, a loop variable or a receipt key (receipt / archive integrity checks) is invisible to it. This supplement
# enumerates every hashing call in every scanned, unpinned module that hashes a file's bytes and resolves which file.
HASH_CALL_RE = re.compile(r"(^hashlib\.(sha256|sha1|md5|blake2b|new)$|(^|\.)_?(sha256_file|file_sha256|sha256_bytes|sha256_of|sha)$|^sha256$|\.sha256$)")
RUN_PACKAGE_DERIVED = ("raw-result.json", "manifest.yaml", "solver-events.json")
HASH_MANUAL = {}          # (rel, line) -> {"files": [...], "reading": str}; filled below the census section (MR-H-*)


def _path_of_bytes_expr(fo, a, pa, depth=0):
    """The path expression whose file bytes a hashed expression `a` holds, or None when `a` is not file bytes."""
    if a is None or depth > 3:
        return None
    if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute) and a.func.attr in ("read", "read_bytes", "read_text"):
        v = a.func.value
        if isinstance(v, ast.Call) and dotted(v.func) in ("open", "io.open", "Path", "pathlib.Path") and v.args:
            return v.args[0]
        if isinstance(v, ast.Name):
            for st in fo.raw if hasattr(fo, "raw") else []:
                for x in ast.walk(st):
                    if isinstance(x, (ast.With, ast.AsyncWith)):
                        for it in x.items:
                            if isinstance(it.optional_vars, ast.Name) and it.optional_vars.id == v.id and isinstance(it.context_expr, ast.Call) \
                                    and dotted(it.context_expr.func) in ("open", "io.open") and it.context_expr.args:
                                return it.context_expr.args[0]
            return v                                  # a Path-like name: resolve its own assignments
        if isinstance(v, ast.Call):
            fids = resolve_call(fo, v.func)
            if any(fi in LOADER for fi in fids) and v.args:
                return v.args[0]
            return v
        return None
    if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute) and a.func.attr == "read" and a.args:
        fids = resolve_call(fo, a.func)
        if any(fi in LOADER for fi in fids):          # Reader.read("raw-result.json") and the like
            return a.args[0]
    if isinstance(a, ast.Name):
        for v in pa.get(a.id, []):
            p = _path_of_bytes_expr(fo, v, pa, depth + 1)
            if p is not None:
                return p
    return None


def _loop_iters(fo, names):
    """Iterable expressions of the for-loops / comprehensions of fo whose targets bind one of `names`."""
    out = []
    for x in fn_all_nodes(fo):
        if isinstance(x, (ast.For, ast.AsyncFor, ast.comprehension)):
            tn = {y.id for y in ast.walk(x.target) if isinstance(y, ast.Name)}
            if tn & names:
                out.append(x.iter)
    return out


def resolve_path_names(fo, p, depth=0, seen=None):
    """File names a path expression can name: constants (file_ids), loop iterables, and the callers' arguments when
    the path depends on a parameter (depth <= 3). Returns (names, site_files, unresolved_reasons)."""
    seen = seen if seen is not None else set()
    key = (fo.fid, id(p))
    if p is None or depth > 3 or key in seen:
        return set(), set(), ["depth bound or cycle"] if depth > 3 else []
    seen.add(key)
    names, sitef, params = file_ids(fo, p)
    names, sitef, why = set(names), set(sitef), []
    pn = names_in(fo, p)
    pa = pre_assigns(fo)
    for nm in list(pn):
        for v in pa.get(nm, []):
            pn |= names_in(fo, v)
    for it in _loop_iters(fo, pn):
        n2, s2, w2 = resolve_path_names(fo, it, depth + 1, seen)
        names |= n2
        sitef |= s2
        if not (n2 or s2):
            why.append("loop over %s" % ast.unparse(it)[:80])
    for i in sorted(params):
        if fo.params[i] in ("self", "cls"):
            continue
        found_caller = False
        for cfid, cfo in FUNCS.items():
            for c in fn_all_nodes(cfo):
                if isinstance(c, ast.Call) and fo.fid in resolve_call(cfo, c.func):
                    off = 1 if ("." in fo.qual and fo.params and fo.params[0] in ("self", "cls") and isinstance(c.func, ast.Attribute)) else 0
                    j = i - off
                    arg = c.args[j] if 0 <= j < len(c.args) and not isinstance(c.args[j], ast.Starred) else None
                    if arg is None:
                        for k in c.keywords:
                            if k.arg == fo.params[i]:
                                arg = k.value
                    if arg is None:
                        continue
                    found_caller = True
                    n2, s2, w2 = resolve_path_names(cfo, arg, depth + 1, seen)
                    names |= n2
                    sitef |= s2
                    if not (n2 or s2):
                        why.append("caller %s line %d passes %s" % (cfo.qual, c.lineno, ast.unparse(arg)[:60]))
        if not found_caller:
            why.append("parameter %s: no statically resolved caller" % fo.params[i])
    if not (names or sitef) and not why:
        why.append("path %s not resolved to a file-name constant" % ast.unparse(p)[:80])
    return names, sitef, why


def hash_sites():
    """Every hashing call that hashes a file's bytes, in every loaded module (static; computed once)."""
    if HASH_SITES_CACHE:
        return HASH_SITES_CACHE
    for fid, fo in sorted(FUNCS.items()):
        if fid in HASHER:
            continue                                  # the file-hashing helpers themselves; their call sites are enumerated
        last = fo.qual.split(".")[-1]
        if re.match(r"^_?(sha|sha256\w*|file_sha256\w*|sha256_of\w*)$", last):
            continue                                  # value-hashing helpers (sha256_bytes etc.); their call sites are enumerated
        pa = pre_assigns(fo)
        for x in fn_all_nodes(fo):
            if not (isinstance(x, ast.Call) and HASH_CALL_RE.search(dotted(x.func) or "")):
                continue
            d = dotted(x.func)
            if not x.args:
                continue                              # incremental hasher object; its .update() arguments are values
            a = x.args[0]
            helper_is_file = (re.search(r"(sha256_file|file_sha256|_sha256_file)$", d) is not None or
                              any(fi in HASHER for fi in resolve_call(fo, x.func)) or
                              (d.split(".")[-1] == "sha" and any(fi in HASHER for fi in resolve_call(fo, x.func))))
            p = a if helper_is_file else _path_of_bytes_expr(fo, a, pa)
            if p is None:
                continue                              # a hash of a VALUE: the taint engine's m4 (HASH_CALLS) covers it
            names, sitef, why = resolve_path_names(fo, p)
            HASH_SITES_CACHE.append({"fid": fid, "file": fo.mod.rel, "line": x.lineno, "function": fo.qual, "tree": fo.mod.tree,
                                     "call": d, "path_expr": ast.unparse(p)[:120], "names": sorted(names),
                                     "site_files": sorted({"%s %s" % (s, suf) for (s, suf, lab) in sitef}),
                                     "unresolved": not (names or sitef), "unresolved_why": why[:6], "node": x,
                                     "pinned": MODULE_PIN.get(fo.mod.key)})
    return HASH_SITES_CACHE


HASH_SITES_CACHE = []
# C9: recorded manual readings (this task), each read in the frozen / archived source at the cited lines
HASH_MANUAL.update({
    (A1 + "/a1_driver.py", 268): {
        "id": "MR-H-1", "files": ["raw-result.json"],
        "reading": ("phase_b_check hashes every path in paths_read (a1_driver.py lines 263-269). Its one caller, cmd_aggregate_a1 "
                    "(lines 283-298), builds v2_paths from _load_raw(rid), whose path is os.path.join(C.EXP_DIR, 'runs', rid, "
                    "'raw-result.json') (lines 238-240), for every v2 run read and for the v2 aggregate. So it hashes whole v2 "
                    "raw-result.json files, which carry the S-3 record in fixture and m = 4 cell packages (the K-4 copies) and the "
                    "S-1 derived target rows; the result gates run_status / failure_class (lines 371-373). The static resolver does "
                    "not follow list.append (M-16 limit), hence a manual reading.")},
    ("harness/runner.py", 120): {
        "id": "MR-H-2", "files": [],
        "reading": ("source_provenance hashes os.path.join(REPO, rel) for rel in executed_source_files() (harness/runner.py lines "
                    "73-100, 118-121): the repo-relative .py files the process imported. Source files, never a run-package file.")},
})
HIT_MANUAL = {
    (R2 + "/r2_reg1.py", 240, "S-3"): {
        "id": "MR-CI-1", "not_a_consumer": True,
        "reading": ("r2_reg1.compare line 240 compares certificates/*.json (REG-1 (c)). The S-3 tag reaches it only through the "
                    "context-insensitive summary of strip() (M-6), whose (b) call sites (line 259) pass target entries holding the "
                    "S-3 record. A certificate holds no S-3 field: lift_and_certify builds it from the relation and curve data "
                    "(v2_driver.py lines 235-257; extra carries notes only, lines 432-433, 842-844, a1_driver.py 167-169).")},
    (R1 + "/r1_reg1.py", 152, "S-3"): {
        "id": "MR-CI-1", "not_a_consumer": True,
        "reading": ("r1_reg1.compare line 152 compares certificates/*.json; the same context-insensitive route through strip() as "
                    "r2_reg1.py line 240 (MR-CI-1); a certificate holds no S-3 field.")},
    (V2 + "/v2_check_run.py", 72, "S-3"): {
        "id": "MR-WILD-1", "not_a_consumer": True,
        "reading": ("thr is manifest resources.msolve_threads_executed, built by collect(raw, 'threads_executed') (v2_run_wrapper.py "
                    "lines 71-80, 203, 224). The S-3 record carries no key threads_executed (its keys: v2_solver.py lines 519-547; "
                    "child keys outcome, wall_seconds, returncode, rlimit_as_child_getrlimit, peak_vm_bytes). The engine's route is "
                    "the computed-key position arms[arm] (v2_driver.py lines 341-365, 'for arm in arms'), which the collector could "
                    "match only if an arm name were 'threads_executed'; the collected values are the S-1 arm rows' threads_executed.")},
}
_MR_WILD_2 = ("The route matches a wildcard in a stored path: a computed key or a suffix truncated by the M-5 bounding (the stored "
              "S-3 paths here are cells/[]/* and ladder_rows/[]/*, standing for cells/[]/targets/[]/.../instructions_callgrind), and "
              "the non-wildcard 'arm' variants inherit such a match through a store (row['arm'] = cl['arm']). By reading: the S-3 "
              "record is stored by name only under instructions_callgrind of target arm rows (v2_driver.py lines 209, 360, 1180; no "
              "other literal read or write of an S-3 field exists in the five trees); its containers are arms[arm] (line 365), the "
              "target lists and cells[].targets (lines 1147-1218), whole raw results in runs[rid] (line 1257; a1_driver.py 287, 294) "
              "and REG-1 / development reports. The keys read on this line (kind, metrics, arm, run, reading_label, "
              "read_as_primary_shape, group_order, curve_shape) are none of these: a cell's metrics block holds counts, D values, "
              "rates, the primary child's peak RSS and a constant 'instructions' note (v2_driver.py lines 1219-1234); a ladder row "
              "holds cell scalars and metrics sub-fields (v2_driver.py lines 1239-1244) plus run, source, reading_label and "
              "read_as_primary_shape (a1_driver.py lines 305-307). Not an S-3 consumer.")
for _f, _lns in ((A1 + "/a1_check_run.py", (95, 96, 97, 98, 99, 101)), (A1 + "/a1_driver.py", (309, 310, 348, 349)),
                 (V2 + "/v2_check_run.py", (101, 102)), (V2 + "/v2_driver.py", (1266, 1267, 1307, 1308))):
    for _ln in _lns:
        HIT_MANUAL[(_f, _ln, "S-3")] = {"id": "MR-WILD-2", "not_a_consumer": True, "reading": _MR_WILD_2}
for _ln in (371, 372, 373):
    HIT_MANUAL[(A1 + "/a1_driver.py", _ln, "S-3")] = {
        "id": "MR-TUPLE-1", "not_a_consumer": False,
        "reading": ("The engine's route to pb is an over-approximation: 'raw, rp = _load_raw(rid)' gives the path rp the tags of raw "
                    "(tuple unpacking is not positional, M-18). The consumer itself is real: pb = phase_b_check(v2_paths) hashes whole "
                    "v2 raw-result.json files (MR-H-1), which carry the S-3 record (V-1 via K-4), and pb['status'] sets run_status / "
                    "failure_class here. Coverage is therefore stated for V-1.")}
M16_VALUE = {"raw-result.json": "V-1", "manifest.yaml": "V-3", "solver-events.json": "V-5"}


def hash_hit_to_agg(ps, hh):
    """An M-16 file-hash hit as an aggregated hit of pass ps (mode m4 for a derived file, m8 for a site file)."""
    fo = FUNCS[hh["fid"]]
    files = list(hh.get("derived_files") or [])
    sfs = list(hh.get("site_files") or [])
    root = ps if ps != "C4" else "C4:<any non-msolve child record>"
    return {"file": hh["file"], "line": hh["line"], "fid": hh["fid"], "function": hh["function"], "tree": fo.mod.tree,
            "site": SITE_OF.get(ps, "CU-4"), "field": "file " + ", ".join(files + sfs), "mode": "m8" if (sfs and not files) else "m4",
            "origins": {root}, "vias": {"file:" + f for f in files}, "fulls": set(), "paths": set(), "nodes": [hh["node"]],
            "notes": {"M-16 file hash (%s of %s; %s)" % (hh["call"], hh["path_expr"], hh["resolution"])},
            "m16_files": files + sfs, "m16_resolution": hh["resolution"], "m16_manual_reading": hh.get("manual_reading")}


def hash_census(ps):
    """Hits of pass ps among the file-hash sites: a hashed file that carries this pass's site data (FILE_TAGS of the
    pass) or is a site file of this site; unresolved sites are listed with their effect and manual reading."""
    site = SITE_OF.get(ps, "CU-4")
    with_data = {k for k, v in FILE_TAGS.items() if v}
    hits, unresolved, other = [], [], []
    for h in hash_sites():
        fo = FUNCS[h["fid"]]
        eff = classify_node(fo.mod, fo, h["node"])
        mr = HASH_MANUAL.get((h["file"], h["line"]))
        files = set(h["names"])
        sfs = {s.split(" ", 1)[1] for s in h["site_files"] if s.split(" ", 1)[0] == ps}
        how = "static"
        if h["unresolved"] and mr is not None:
            files = set(mr["files"])
            how = "manual reading %s" % mr["id"]
        row = {"file": h["file"], "line": h["line"], "function": h["function"], "fid": h["fid"], "call": h["call"],
               "path_expr": h["path_expr"], "resolved_files": sorted(files), "site_files": sorted(sfs), "resolution": how,
               "unresolved_why": h["unresolved_why"], "effect": eff, "pinned": h["pinned"],
               "manual_reading": mr["reading"] if mr else None, "node": h["node"]}
        if h["pinned"]:
            other.append(dict(row, disposition="pinned module (M-8): not a reader of an EXP-GFPN-05ff43 package"))
            continue
        dat = sorted(files & with_data)
        if dat or sfs:
            hits.append(dict(row, derived_files=dat))
        elif h["unresolved"] and mr is None:
            unresolved.append(row)
        else:
            other.append(dict(row, disposition="hashes no file carrying %s data" % site))
    return {"hits": hits, "unresolved": unresolved, "not_hits": other}


# ===================================================================================================== 5. REACHABILITY
def build_graph():
    g = {fid: set() for fid in FUNCS}
    for fid, fo in FUNCS.items():
        for x in fn_all_nodes(fo):
            if isinstance(x, ast.Call):
                g[fid] |= set(resolve_call(fo, x.func))
            elif isinstance(x, (ast.Name, ast.Attribute)) and isinstance(getattr(x, "ctx", None), ast.Load):
                par = fo.mod.parents.get(x)
                if isinstance(par, ast.Call) and par.func is x:
                    continue
                if isinstance(par, ast.Attribute) and par.value is x:
                    continue
                if isinstance(par, ast.Compare):
                    continue
                if isinstance(par, ast.Call) and dotted(par.func) in ("getattr", "hasattr", "setattr", "id", "callable", "isinstance"):
                    continue
                if isinstance(x, ast.Name) and x.id in fo.params:
                    continue
                g[fid] |= set(resolve_call(fo, x))
            elif isinstance(x, ast.Import):
                for a in x.names:
                    for k in resolve_module(fo.mod, a.name):
                        g[fid].add(k + ":<module>")
            elif isinstance(x, ast.ImportFrom):
                for k in resolve_module(fo.mod, ("." * x.level) + (x.module or "")):
                    g[fid].add(k + ":<module>")
        # calls through callable parameters (bound at call sites)
        for p, fids in CALLABLE_PARAM.get(fid, {}).items():
            g[fid] |= set(fids)
    for a, b, why in RUNTIME_BINDINGS:
        for src in list(g):
            if a in g[src] and src != b:
                g[src].add(b)
        if a in g:
            g[a].add(b) if a == "r2/r2_resolve:_call_original" else None
    g.setdefault("r2/r2_resolve:_call_original", set()).add("v2/v2_driver:solve")
    return g


def reach(g, roots):
    seen, stack = set(), [r for r in roots if r in g]
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        stack += [x for x in g.get(f, ()) if x not in seen]
    return seen


def reachability(g, plans):
    groups = {}
    cmds = []
    for plan_rel, entry in ((PLAN_V2_R2, "r2/r2_entry_v2"), (PLAN_A1_R2, "r2/r2_entry_a1")):
        for c in sorted({(pk.get("driver_args") or [None])[0] for pk in plans[plan_rel]["packages"]} - {None}):
            cmds.append((os.path.basename(plan_rel), c, entry))
    ent = {}
    for plan, c, entry in cmds:
        ent.setdefault(entry, []).append((plan, c))
    for entry, lst in ent.items():
        roots = [entry + ":<module>", entry + ":<main>", entry + ":main"]
        groups["commands of %s via %s" % (sorted({p for p, _ in lst})[0], entry.split("/")[1])] = {
            "roots": roots, "commands": ["%s %s" % x for x in lst], "reached": reach(g, roots)}
    wr = ["r2/r2_run_wrapper:<module>", "r2/r2_run_wrapper:<main>", "r2/r2_run_wrapper:main",
          "r2/r2_check_run:<module>", "r2/r2_check_run:<main>", "r2/r2_check_run:main"]
    groups["r2 wrapper and checker processes"] = {"roots": wr, "reached": reach(g, wr)}
    troots = []
    for k, m in MODS.items():
        if m.tree == "tool" and not MODULE_PIN.get(k):
            troots += [k + ":<module>", k + ":<main>"] + [f for f in FUNCS if f.startswith(k + ":") and f.endswith(":main")]
    groups["repository tools that would read an r3 run package (unpinned tools)"] = {"roots": sorted(troots), "reached": reach(g, troots)}
    return groups, cmds


# ===================================================================================================== 6. CU-1
CC1 = [  # transcribed from the draft's CC-1 text; every token is re-found in that text by verify_cc1()
    {"id": "S-1", "census_site": V2 + "/v2_driver.py:166", "file": "implementation-v2/v2_driver.py", "argv_line": 165, "launch_line": 166,
     "enclosing_function": "solve", "classified": True, "reached_by_commands": "both r2 plans' 7", "reachable": True,
     "tokens": ["S-1  file implementation-v2/v2_driver.py; argv line 165; launch line 166; enclosing function solve; classified true",
                "reached by commands: both r2 plans' 7; reachable true"]},
    {"id": "S-2", "census_site": A1 + "/a1_health.py:147", "file": "implementation-v2-a1/a1_health.py", "argv_line": 144, "launch_line": 147,
     "enclosing_function": "run_system", "classified": True, "reached_by_commands": [["trial-plan-v2-a1-r2.json", "controls-a1"]], "reachable": True,
     "tokens": ["S-2  file implementation-v2-a1/a1_health.py; argv line 144; launch line 147; enclosing function run_system; classified true",
                "reached by commands: [trial-plan-v2-a1-r2.json, controls-a1]; reachable true"]},
    {"id": "S-3", "census_site": V2 + "/v2_driver.py:209", "file": "implementation-v2/v2_driver.py (named by the argv line)",
     "argv_line": ("implementation-v2/v2_driver.py", 209), "wrapper_argv_line": ("implementation-v2/v2_solver.py", 516),
     "launch_line": ("implementation-v2/v2_solver.py", 517), "enclosing_function": "solve",
     "classified": "census.json \"SEE classification_detail (the literal CN-1 definition and the draft's stated expectation differ)\", ruled CLASSIFIED by DEC-20260924-afdc3b R-CG",
     "reached_by_commands": "both r2 plans' 7", "reachable": True,
     "tokens": ["S-3  argv line implementation-v2/v2_driver.py 209; wrapper argv line implementation-v2/v2_solver.py 516; launch line implementation-v2/v2_solver.py 517; enclosing function (of the argv line) solve",
                "ruled CLASSIFIED by DEC-20260924-afdc3b R-CG; reached by commands (static): both r2 plans' 7",
                "reachable true"]},
    {"id": "U-1", "census_site": V1 + "/run_wrapper.py:36", "file": "implementation/run_wrapper.py", "argv_line": 36, "launch_line": 23,
     "enclosing_function": "environment",
     "classified": "literal definition: its stdout enters a recorded field (environment.json software.msolve), which is not a cost measurement; it enters no classifier, check, gate or outcome class",
     "reached_by_commands": [], "reachable": False,
     "tokens": ["U-1  file implementation/run_wrapper.py; argv line 36; launch line 23; enclosing function environment",
                "reached by commands: none; reachable false."]},
    {"id": "U-2", "census_site": V1 + "/symmetrize.py:399", "file": "implementation/symmetrize.py", "argv_line": 392, "launch_line": 399,
     "enclosing_function": "run_msolve", "classified": True, "reached_by_commands": [], "reachable": False,
     "tokens": ["U-2  file implementation/symmetrize.py; argv line 392; launch line 399; enclosing function run_msolve; classified true; reached by commands: none; reachable false."]},
    {"id": "U-3", "census_site": "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue.py:157",
     "file": "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue.py", "argv_line": 157, "launch_line": 157,
     "enclosing_function": "ideal_degree", "classified": True, "reached_by_commands": [], "reachable": False,
     "tokens": ["U-3  file coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue.py;",
                "argv line 157; launch line 157; enclosing function ideal_degree; classified true; reached by commands: none; reachable false."]},
    {"id": "U-4", "census_site": "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_m4.py:26",
     "file": "coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_m4.py", "argv_line": 26, "launch_line": 26,
     "enclosing_function": "ideal_degree", "classified": True, "reached_by_commands": [], "reachable": False,
     "tokens": ["U-4  file coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_m4.py;",
                "argv line 26; launch line 26; enclosing function ideal_degree; classified true; reached by commands: none; reachable false."]},
    {"id": "U-5", "unresolved": True, "census_site": V1 + "/run_wrapper.py:98", "file": "implementation/run_wrapper.py", "line": 98,
     "enclosing_function": "main",
     "classified": "not determinable statically (the v1 wrapper runs whatever command follows '--'); v1 tree, not reachable",
     "reached_by_commands": [], "reachable": False,
     "tokens": ["U-5  file implementation/run_wrapper.py; line 98 (unresolved argv \"cmd\", subprocess.run); function main",
                "reached by commands: none; reachable false."]},
]
BOTH_R2_PLANS_7 = sorted([["trial-plan-v2-a1-r2.json", "cells"], ["trial-plan-v2-a1-r2.json", "controls-a1"],
                          ["trial-plan-v2-r2.json", "anchor-identity"], ["trial-plan-v2-r2.json", "cells"], ["trial-plan-v2-r2.json", "controls"],
                          ["trial-plan-v2-r2.json", "fixture"], ["trial-plan-v2-r2.json", "fixture4"]])


def norm_ws(t):
    return re.sub(r"\s+", " ", t).strip()


def cu1(draft_text, census):
    cc1_text = norm_ws(draft_text.split("CC-1_site_table_every_field_stated:", 1)[1].split("CC-2_consumer_dispositions_by_derived_value:", 1)[0])
    raw_cc1 = draft_text.split("CC-1_site_table_every_field_stated:", 1)[1].split("CC-2_consumer_dispositions_by_derived_value:", 1)[0]
    token_checks = []
    for e in CC1:
        for tok in e["tokens"]:
            token_checks.append({"entry": e["id"], "token": tok, "found_in_CC1_text": norm_ws(tok) in cc1_text})
    both7_defined = all(norm_ws("[%s, %s]" % (a, b)) in cc1_text for a, b in BOTH_R2_PLANS_7)
    sites = {s["site"]: s for s in census["CN1_msolve_launch_census"]["sites"]}
    unres = {u["site"]: u for u in census["CN1_msolve_launch_census"]["unresolved_argv_sites_reviewed"]}
    rows, ndiff, nunstated = [], 0, 0
    def rel_exp(p):
        return p if p.startswith("coordination/") else EXP + "/" + p
    for e in CC1:
        row = {"entry": e["id"], "census_site": e["census_site"], "fields": {}}
        if e.get("unresolved"):
            s = unres.get(e["census_site"])
            f = row["fields"]
            f["file"] = {"CC-1": e["file"], "census.json": s["site"].rsplit(":", 1)[0], "equal": rel_exp(e["file"]) == s["site"].rsplit(":", 1)[0],
                         "rule": "path equal after resolving the experiment-relative CC-1 path (MR-CU1-1)"}
            f["argv_line / launch_line (the one site line)"] = {"CC-1": "line %d" % e["line"], "census.json": int(s["site"].rsplit(":", 1)[1]),
                                                               "equal": e["line"] == int(s["site"].rsplit(":", 1)[1]),
                                                               "rule": "census.json carries one site line for an unresolved-argv entry; CC-1 states that line (MR-CU1-2)"}
            f["enclosing_function"] = {"CC-1": e["enclosing_function"], "census.json": s["function"], "equal": e["enclosing_function"] == s["function"]}
            mv = s["manual_reading"]["msolve"]
            f["classified"] = {"CC-1": e["classified"], "census.json (manual_reading.msolve)": mv, "equal": e["classified"] == mv,
                               "rule": "equal when the census.json value verbatim"}
            f["reached_by_commands"] = {"CC-1": "none", "census.json": "no such field in unresolved_argv_sites_reviewed entries",
                                        "equal": None, "note": "not comparable: census.json carries no reached_by_commands for this entry; not an unstated CC-1 field"}
            f["reachable"] = {"CC-1": e["reachable"], "census.json": s["reachable"], "equal": e["reachable"] == s["reachable"]}
        else:
            s = sites.get(e["census_site"])
            cl = s["classification"]
            f = row["fields"]
            if e["id"] == "S-3":
                f["file"] = {"CC-1": "implementation-v2/v2_driver.py (stated in the argv-line value; no separate 'file' label)",
                             "census.json": s["file"], "equal": s["file"] == V2 + "/v2_driver.py",
                             "rule": "MR-CU1-3: S-3's CC-1 entry names the file inside its argv line; census.json's 'file' is the argv line's file",
                             "alternative_reading": ("ALTERNATIVE (not applied, recorded for the approval act): if a field counts as stated only "
                                                     "under its own label, S-3's CC-1 entry has no 'file' label, this field is UNSTATED and so "
                                                     "UNEQUAL, and the CU-1 reading becomes 'NOT approvable as written'")}
                al, wl, ll = e["argv_line"], e["wrapper_argv_line"], e["launch_line"]
                f["argv_line"] = {"CC-1": "%s %d" % al, "census.json": "%s %d" % (cl["argv_line"]["file"], cl["argv_line"]["line"]),
                                  "equal": rel_exp(al[0]) == cl["argv_line"]["file"] and al[1] == cl["argv_line"]["line"]}
                f["wrapper_argv_line"] = {"CC-1": "%s %d" % wl, "census.json": "%s %d" % (cl["wrapper_argv_line"]["file"], cl["wrapper_argv_line"]["line"]),
                                          "equal": rel_exp(wl[0]) == cl["wrapper_argv_line"]["file"] and wl[1] == cl["wrapper_argv_line"]["line"]}
                f["launch_line"] = {"CC-1": "%s %d" % ll, "census.json": "%s %d" % (cl["launch_line"]["file"], cl["launch_line"]["line"]),
                                    "equal": rel_exp(ll[0]) == cl["launch_line"]["file"] and ll[1] == cl["launch_line"]["line"]}
                f["classified"] = {"CC-1": e["classified"], "census.json": cl["classified"],
                                   "equal": cl["classified"] == "SEE classification_detail (the literal CN-1 definition and the draft's stated expectation differ)",
                                   "rule": "S-3 only: the census.json value verbatim, with DEC-20260924-afdc3b R-CG's ruling on it (CLASSIFIED); CC-1 quotes the census value verbatim and states the ruling"}
            else:
                f["file"] = {"CC-1": e["file"], "census.json": s["file"], "equal": rel_exp(e["file"]) == s["file"],
                             "rule": "path equal after resolving the experiment-relative CC-1 path (MR-CU1-1)"}
                f["argv_line"] = {"CC-1": e["argv_line"], "census.json": cl["argv_line"]["line"], "equal": e["argv_line"] == cl["argv_line"]["line"]}
                f["launch_line"] = {"CC-1": e["launch_line"], "census.json": cl["launch_line"]["line"], "equal": e["launch_line"] == cl["launch_line"]["line"]}
                if e["classified"] is True:
                    f["classified"] = {"CC-1": True, "census.json": cl["classified"], "equal": cl["classified"] is True}
                else:
                    f["classified"] = {"CC-1": e["classified"], "census.json": cl["classified"], "equal": e["classified"] == cl["classified"],
                                       "rule": "equal when the census.json value verbatim"}
            f["enclosing_function"] = {"CC-1": e["enclosing_function"], "census.json": s["enclosing_function"],
                                       "equal": e["enclosing_function"] == s["enclosing_function"]}
            cc_cmds = BOTH_R2_PLANS_7 if e["reached_by_commands"] == "both r2 plans' 7" else sorted(e["reached_by_commands"])
            ce_cmds = sorted([[x["plan"], x["command"]] for x in s["reached_by_commands"]])
            f["reached_by_commands"] = {"CC-1": e["reached_by_commands"] if e["reached_by_commands"] else "none", "CC-1_expanded": cc_cmds,
                                        "census.json": ce_cmds, "equal": cc_cmds == ce_cmds}
            f["reachable"] = {"CC-1": e["reachable"], "census.json": s["reachable"], "equal": e["reachable"] == s["reachable"]}
            if e["id"] == "S-3":
                f["reached_by_commands"]["CC-1_additional_statement"] = ("ACTUALLY launched (argument level, census.md lines 281-287): only in fixture and in "
                                                                         "cells with m = 4 (target 0), in both plans, and only after an ok outcome")
        diffs = [k for k, v in row["fields"].items() if v.get("equal") is False]
        unstated = [k for k, v in row["fields"].items() if v.get("CC-1") in (None, "NOT STATED")]
        row["differences"] = diffs
        row["unstated_fields"] = unstated
        row["census_fields_outside_CU1_list"] = sorted(set((sites.get(e["census_site"]) or unres.get(e["census_site"]) or {}).keys())
                                                       - {"site", "file", "line", "enclosing_function", "function", "classification", "reached_by_commands",
                                                          "reachable", "manual_reading"})
        ndiff += len(diffs)
        nunstated += len(unstated)
        rows.append(row)
    reading = ("CU-1 condition holds (every entry: 0 differences, 0 unstated fields); CU-1 does not make the draft 'NOT approvable as written'"
               if (ndiff == 0 and nunstated == 0) else "NOT approvable as written (CU-1)")
    return {"entries": rows, "n_differences": ndiff, "n_unstated_fields": nunstated, "transcription_token_checks": token_checks,
            "both_r2_plans_7_defined_in_CC1_text": both7_defined,
            "equality_rule": ("line numbers, function names, booleans and command sets are equal when identical; a classified value is equal when it is "
                              "the census.json value verbatim, or the boolean true where census.json carries true, or, for S-3 only, the "
                              "DEC-20260924-afdc3b R-CG ruling on the census.json value; an UNSTATED field is UNEQUAL"),
            "reading_rule": "this draft is approvable as written ONLY IF every entry has 0 differences and 0 unstated fields. Otherwise it is NOT approvable as written.",
            "reading": reading, "raw_cc1_text_sha256": sha_bytes(raw_cc1.encode())}


# ===================================================================================================== 7. CU-2 / CU-4 assembly
K_ROWS = {
    "K-1": {"what": "r2_reg1.compare (b) (r2_reg1.py lines 256-262; whole-entry comparison minus X1..X17)", "file": R2 + "/r2_reg1.py",
            "fids": {"r2/r2_reg1:compare", "r2/r2_reg1:compare.b"}, "lines": set(range(245, 267)), "V": "V-1"},
    "K-2": {"what": "the run wrappers' collect(raw, 'rlimit_as_child_getrlimit') (v2 202, a1 324, r1 408, r2 474)",
            "sites": {(V2 + "/v2_run_wrapper.py", 202), (A1 + "/a1_run_wrapper.py", 324), (R1 + "/r1_run_wrapper.py", 408), (R2 + "/r2_run_wrapper.py", 474)},
            "fids": {"v2/v2_run_wrapper:collect", "a1/a1_run_wrapper:collect", "r1/r1_run_wrapper:collect", "r2/r2_run_wrapper:collect"}, "V": "V-1"},
    "K-3": {"what": "r1_reg1.compare (r1_reg1.py lines 168-174; whole-entry comparison)", "file": R1 + "/r1_reg1.py",
            "fids": {"r1/r1_reg1:compare", "r1/r1_reg1:compare.b"}, "lines": set(range(155, 180)), "V": "V-1"},
    "K-4": {"what": "the copies into fixture and cell target rows (v2_driver.py lines 360, 1180)", "sites": {(V2 + "/v2_driver.py", 359), (V2 + "/v2_driver.py", 360),
            (V2 + "/v2_driver.py", 1179), (V2 + "/v2_driver.py", 1180)}, "V": "V-1"},
    "K-5": {"what": "the frozen checker's walk (v2_check_run.py line 99) and serialization test (line 103), and r2_check_run's find_solver_records (lines 81-90)",
            "sites": {(V2 + "/v2_check_run.py", 99), (V2 + "/v2_check_run.py", 103), (V2 + "/v2_check_run.py", 105)},
            "fids": {"r2/r2_check_run:find_solver_records", "v2/v2_check_run:walk", "v2/v2_check_run:main.scan"}, "V": "V-1"},
}
V3_MARKERS = ("child_rlimit_as_read_back_by_getrlimit",)
SE3_WRAPPER_FIDS_PREFIX = "r2/r2_resolve:"


def k_row_of(a):
    for kid, k in K_ROWS.items():
        if (a["file"], a["line"]) in k.get("sites", set()):
            return kid
        if a["fid"] in k.get("fids", set()) and (not k.get("lines") or a["line"] in k["lines"] or a["fid"].endswith(".b")):
            return kid
    return None


def v_value_of(a):
    """The CC-2 value an S-3 hit falls under, by the derived value it reads."""
    vias = " ".join(sorted(a["vias"]))
    paths = " ".join(sorted(set(a.get("paths") or set()) | set(a["fulls"])))
    if a.get("m16_files"):
        # C5: a whole-file hash reads every value the file carries; the strongest-listed value it holds is reported
        vs = sorted({M16_VALUE.get(f, "V-6" if f.startswith((".callgrind", ".cg.")) else "V-1") for f in a["m16_files"]})
        return "V-1" if "V-1" in vs else vs[0]
    if a["mode"] == "m8":
        return "V-6"
    if any(m in vias or m in paths or m in a["field"] for m in V3_MARKERS) or re.search(r"_run_wrapper:(main|launch):caps", vias):
        return "V-3"
    if "r2_reg1" in vias or a["fid"].startswith("r2/r2_reg1:") and a["fid"] not in K_ROWS["K-1"]["fids"]:
        return "V-2"
    if "solver-events.json" in vias:
        return "V-5"
    if re.search(r"_check_run:main", vias):
        return "V-4"
    return "V-1"


def s3_coverage(a):
    eff = a["effect"][0] if a.get("effect") else None
    if eff not in ("E1", "E2", "E3", "E4"):
        return None
    kid = k_row_of(a)
    v = v_value_of(a)
    if kid:
        return {"value": K_ROWS[kid]["V"], "row": kid, "coverage": "%s / %s" % (K_ROWS[kid]["V"], kid)}
    if v == "V-2":
        return {"value": "V-2", "row": None, "coverage": "V-2 (ANY consumer: disposition CG-4)"}
    if v == "V-4":
        return {"value": "V-4", "row": None, "coverage": "V-4 (ANY consumer: as frozen)"}
    if v == "V-3":
        if eff == "E2":
            return {"value": "V-3", "row": None, "coverage": "V-3 (effect E2: disposition CC-3)"}
        return {"value": "V-3", "row": None, "coverage": "NOT COVERED (V-3 disposes only of effects E2, E5, E6)"}
    if v == "V-5":
        return {"value": "V-5", "row": None, "coverage": "V-5 (record and report only; an r3 consumer with E1-E4 is a DV-11 STOP)"}
    if v == "V-6":
        return {"value": "V-6", "row": None, "coverage": "NOT COVERED (V-6: any other consumer with effect E1-E4 is outside this table)"}
    return {"value": "V-1", "row": None, "coverage": "NOT COVERED (a V-1 consumer that is none of K-1..K-5)"}


def class_of(a, frozen_body):
    """S-1 / S-2 class rule (alpha, beta, frozen-body exception, or OUTSIDE THE CLASS RULE)."""
    eff = a["effect"][0] if a.get("effect") else None
    if eff not in ("E1", "E2", "E3", "E4"):
        return None
    site = "S1" if a["site"] == "S-1" else "S2"
    if a["fid"] in frozen_body[site]:
        return {"class": "frozen-body exception", "rule": "R-CL-X: inside the frozen %s body or a frozen function it calls inside the wrapped call" %
                ("solve()" if site == "S1" else "run_system()")}
    if a["mode"] == "m8":
        if "renamed attempt file" in a["field"] or ".ssf-attempt" in a["field"]:
            return {"class": "OUTSIDE THE CLASS RULE", "rule": "R-CL-OUT-REN: reads a renamed attempt file <tag>...ssf-attempt<k>"}
        return {"class": "beta", "rule": "R-CL-B: reads a file the recorded attempt left under its original name (%s)" % a["field"]}
    if site == "S1" and a["fid"].startswith(SE3_WRAPPER_FIDS_PREFIX):
        return {"class": "OUTSIDE THE CLASS RULE",
                "rule": ("R-CL-OUT-SE3 (MR-SE3): the SE-3 wrapper's own reads of each attempt's result, recorded or not; the draft's class rule "
                         "names alpha, beta and the frozen solve()/run_system() bodies, and states that a consumer that 'reads a non-recorded "
                         "attempt's result' is OUTSIDE; the wrapper body is not named as an exception")}
    if a["fid"] in DEV_DIRECT_ORIGINAL:
        return {"class": "OUTSIDE THE CLASS RULE", "rule": DEV_DIRECT_ORIGINAL[a["fid"]]}
    # C9: the SE-3 wrapper's event record (solver-events.json) records EVERY attempt's outcome, reason, clause and D,
    # recorded or not, plus counters derived from all attempts; its final_* fields copy the returned result
    ev_files = {"file:solver-events.json"}
    if site == "S1" and (any(v.split("~")[0] in ev_files for v in a["vias"]) or "solver-events.json" in (a.get("m16_files") or [])):
        where = " ".join(sorted(set(a.get("paths") or set()) | set(a["fulls"]))) + " " + a["field"]
        if a["mode"] not in ("m4", "m5", "m6") and re.search(r"(^|[/ ])final_(outcome|reason|D|ssf_clause)", where) and "attempts" not in where:
            return {"class": "alpha", "rule": "R-CL-A-SE4F: reads a final_* field of the SE-3 event record, a copy of the result the wrapper returns"}
        return {"class": "OUTSIDE THE CLASS RULE",
                "rule": ("R-CL-OUT-SE4 (literal reading, as MR-SE3): reads the SE-3 wrapper's event record solver-events.json (whole, "
                         "or a field other than a final_* copy), which carries every attempt's result, recorded or not, and counters "
                         "derived from them; it is not the returned result or a copy of it (alpha), not a file the recorded attempt "
                         "left (beta), and not the frozen-body exception; the draft names 'reads a non-recorded attempt's result' "
                         "OUTSIDE. Whether SE-4 as approved covers it is for the approval act")}
    return {"class": "alpha", "rule": ("R-CL-A: reads the result of a solve() call made through the rebound module attribute (the SE-3 wrapper's return "
                                       "under both r2 entries), or a value copied / derived from it" if site == "S1" else
                                       "R-CL-A: reads the result of a run_system() call (the value the HR-3 wrapper would return), or a value copied / "
                                       "derived from it")}


DEV_DIRECT_ORIGINAL = {}


def frozen_bodies(g):
    out = {}
    for site, root, trees in (("S1", "v2/v2_driver:solve", ("v2",)), ("S2", "a1/a1_health:run_system", ("v2", "a1"))):
        seen = reach({k: {x for x in v if x.split("/")[0] in trees} for k, v in g.items()}, [root])
        out[site] = {f for f in seen if not f.endswith((":<module>", ":<main>"))}
    return out


# ===================================================================================================== 8. THE RUN
MODE_METHODS = {
    "m1": ("tokenize-free ast reading of every constant-key access on a value carrying a site-record tag: x['k'], x.get('k'), 'k' in x, "
           "x.pop('k'); the key must be one the site record carries (definitions: the keys its frozen producer sets) to read site data"),
    "m2": ("ast detection of generic key-name collectors: recursive functions (they call themselves) that iterate mappings and compare a loop "
           "key with a parameter (k == key); every call with an argument carrying a site-record tag is a hit; the collected key decides "
           "whether the site record is read (R-COLL-KEY)"),
    "m3": ("ast detection of recursive walkers: recursive functions over mappings / lists that are not collectors; every call with an argument "
           "carrying a site-record tag is a hit; their internal traversal is recorded as hits of its own (R-WALK-INT)"),
    "m4": ("== / != / membership on a value that is a whole record or a structure holding one (not a scalar field), and hashing "
           "(hashlib.* of a serialization; sha256 of a file through a hashing helper) of such a value or of a derived file"),
    "m5": ("json.dumps / str / repr / '%'-formatting of a structure holding site data, followed by `in`, .find/.count/.startswith/.endswith or "
           "re.search / re.match / re.findall; the needle literals are resolved (R-M5-LIT)"),
    "m6": (".items() / .keys() / .values() / iteration / dict(record) / ** unpacking / f-string formatting of a mapping that holds site data, and "
           "serializers that write every key (json.dump / yaml.safe_dump / .write of a serialization) and print of a whole structure"),
    "m7": ("the derived-value set: every write of a site-record field or of a structure holding one into another variable-held structure "
           "(subscript assignment, append / update / insert / setdefault / extend, dict / list displays, comprehensions) or into a file "
           "(json.dump, yaml.safe_dump, .write, and writer helpers detected by ast), followed interprocedurally (parameters, returns, module "
           "globals, attributes per tree) to a fixpoint; every read of a derived value by modes m1-m6 is recorded as 'm7+<mode>'. Files are "
           "identified by the file-name constant of the path expression; a read through a loader helper takes the name from the caller's "
           "argument"),
    "m8": ("open() / os.path.exists / getsize / glob / os.listdir / os.remove / os.rename / os.replace / shutil.* / hashing helpers whose path "
           "expression (constants, local assignments, constant loops, module constants resolved) names the solver/ directory or a "
           "<tag>.ms, .ms.out, .ms.log, .ms.err, .callgrind.stdout / .stderr / .out, .cg.ms.out or .ssf-attempt<k> file"),
}
METHOD_NOTES = [
    "M-1 Sources. S-1: the value of every call resolving to v2_driver.solve, r2_resolve.solve or r2_resolve._call_original (runtime binding SE-3), "
    "and inside solve() the run_child record of line 166. S-2: every call resolving to a1_health.run_system, and inside it the run_child record of "
    "line 147. S-3: every call resolving to v2_solver.callgrind_instructions, the run_child record (line 517) and the callgrind_annotate output "
    "(line 533) inside it, and every solve() result, which holds the S-3 record under the key instructions_callgrind. Site files: m8.",
    "M-2 One pass per site (S-1, S-2, S-3) and one for CU-4; each pass starts from an empty state.",
    "M-3 Tags carry an access path; a constant-key read follows only the matching key; a computed key matches every key (over-approximation); a "
    "key the site record does not carry cannot read site data (record schema from the frozen producers).",
    "M-4 Constant-keyed comprehensions and loops (for k in <constant tuple>) are evaluated once per key, keeping the key/value correlation.",
    "M-5 Tag sets are bounded (norm / collapse): beyond 128 paths per origin or 1024 tags, paths are truncated to a wildcard suffix; "
    "stored sets above 2000 tags collapse monotonically. Bounding only adds matches (over-approximation); the stores that collapsed are "
    "listed per pass.",
    "M-6 Context-insensitive interprocedural propagation (parameters and returns merged over call sites); attributes are keyed by (tree, name); "
    "module globals by (module, name); a call through a function-valued parameter reaches every function bound to it at a call site.",
    "M-7 Control dependence: an assignment governed by a test that reads a site value is recorded one step as a control-dependent derived "
    "write (control_writes), and is NOT propagated further. Its downstream consumers are therefore not enumerated. For S-3 this concerns the "
    "checker's errors (V-4) and REG-1's failures (V-2), whose dispositions cover ANY consumer.",
    "M-8 Tools: a tool module pinned to another experiment (module-level experiment constants, or MR-PIN) contributes no run-package read taint; "
    "its file reads are listed as pinned_reads.",
    "M-9 Hits are aggregated per (file, line, site, field, mode); the derived values, vias and paths are listed with each.",
    "M-10 Static only (transfer assumption (6)): a consumer reached only through dynamic dispatch the method cannot resolve (getattr, exec, "
    "importlib) is not found here.",
    "M-11 A generic key-name collector called with a constant key returns the values found under that key (collector summary).",
    "M-12 os.path.* and string builders return a scalar string derived value (no key can be read from it).",
    "M-13 Argument level for S-3: a solve() call carries the S-3 record under instructions_callgrind only if it passes a callgrind_timeout "
    "that is not the constant None (v2_driver.py line 207); the calls that do are fixture_core.run_target (line 358) and _run_cell "
    "(line 1174), as census.md lines 281-287 record. Inside the frozen producer the S-3 record is built from callgrind_instructions.",
    "M-14 A tag that passed through a computed-key / wildcard-path match carries the marker '~wildcard' in its derived-value name; each hit "
    "reports only_through_wildcard_match (an over-approximation marker).",
    "M-15 Flow-sensitive local states (strong update of names; joins at if / loop / try), comprehension variables scoped to their "
    "comprehension; worklist order and hit aggregation are deterministic (sorted).",
    "M-16 File-hash supplement (added by this task): every hashing call over a FILE's bytes in every scanned, unpinned module is "
    "enumerated by ast and its file resolved (constants, module-level path expressions, loop iterables, callers' arguments to depth "
    "3); a hashed file that carries a pass's site data is a hit (m4; m8 for a site file); unresolved sites are listed with their "
    "effect, and an unresolved E1-E4 site without a recorded manual reading makes CU-2 (a) incomplete. M-16b: repository tools "
    "that verify archived hashes generically (path_sha256 / artifact_sha256 in their source) are scanned files too.",
    "M-17 A call on an imported library module name (copy.deepcopy, shutil.copy, ...) is a library call whose arguments carry the "
    "data; the partial script had treated it as a method of a value (repair C1).",
    "M-18 Tuple unpacking of a call's value is not positional: every target receives the union of the elements' tags "
    "(over-approximation; example and manual reading MR-TUPLE-1).",
    "M-20 Mutation through aliases (added by this task, C12): a store through a local name that aliases a subscript of a global "
    "or of another local (doc = _STATE['doc']) also stores into that container, and a store into a parameter's object is "
    "applied to the caller's argument (context-insensitive, like M-6). Without it the SE-3 event record (solver-events.json) "
    "carried no S-1 data in the engine.",
    "M-19 Reachability groups are the call-graph closure of each entry module (r2_entry_v2, r2_entry_a1), of the r2 wrapper and "
    "checker modules, and of the unpinned tools; an entry module's closure includes every command it dispatches, so the group "
    "over-approximates the plan's commands. Reachability is not a bar (draft CU-2).",
]
PARTIAL_SCRIPT = {"path": OUT_DIR_REL + "/cu_check.py (as left by the interrupted session)", "size_bytes": 173152,
                  "mtime_utc": "2026-09-24T07:54:41Z",
                  "sha256": "a4b9c7df64c0e7cd218d004ffeb08ef262d3c8557a2b1d4baf450742edf5ef75",
                  "lines": 3247,
                  "decision": "REUSED after a full read, as unreviewed draft code; repaired and completed (C1-C11)"}
CHANGES_TO_PARTIAL = [
    "C1 (M-17) library-module receiver: copy.deepcopy(x) / copy.copy(x) return their argument's tags, and a call on an imported "
    "library module no longer enters the value-method branch (it had returned the empty tags of the module name, which hid "
    "r2_reg1.strip / r1_reg1.strip and so K-1 and K-3, and skipped shutil.copy as an m8 file operation).",
    "C2 collected(): a match at a computed-key position is marked as a wildcard match (M-14), like sub()'s.",
    "C3 classify_arg(): a keyword argument maps to its parameter (a dict display passed as keyword argument had been unclassified).",
    "C4 classify_node(): a statement-level pop / setdefault / update / append / extend / insert / add / remove / discard / clear is "
    "E5 (rule R-EXPR-MUT); such statements had been unclassified.",
    "C5 M-16 file-hash supplement (hash_sites, resolve_path_names, hash_census, hash_hit_to_agg), M-16b generic verifier selection, "
    "module-level path expressions resolved by str_consts, and MR-PIN-TEST for unit tests.",
    "C6 the output layer (write_outputs, write_outputs_stop, render_md) that the partial script called but did not define.",
    "C7 name redaction of the written text (a list held reversed in this file) and its counts.",
    "C8 the development-only DEBUG_* environment hooks in run_passes removed (they printed only when set).",
    "C9 recorded manual readings (HASH_MANUAL MR-H-1, MR-H-2; HIT_MANUAL MR-CI-1, MR-WILD-1, MR-TUPLE-1) and the S-1 class rule for "
    "readers of the SE-3 event record (R-CL-OUT-SE4 / R-CL-A-SE4F).",
    "C10 (tried and REVERTED before the recorded run) keeping the wildcard marker on tags written into files: it doubled the stored "
    "tag sets, the M-5 bounding then truncated paths to wildcards, and S-1 hits rose from 7218 to 27731 by over-approximation; "
    "reverted, so a reader of a file does not carry the marker (a known limit of M-14; MR-WILD-1 is a per-hit manual reading).",
    "C11 method notes M-16..M-20 and this record.",
    "C13 a .read() call that resolves by method name to a loader helper (Reader.read in r1_reg1 / r2_reg1) kept only the loader's "
    "file tags and dropped the receiver's, so open(p).read() in those modules returned nothing (a false negative: r2_reg1."
    "solver_events_check); both are kept now.",
    "C12 (M-20) mutation through aliases and through parameters (alias_mut, apply_pmut, PMUT): the partial script had no alias "
    "model, so the S-1 attempt records the SE-3 wrapper appends through its local 'doc' never reached solver-events.json (a "
    "false negative found by this session's in-memory check).",
]
DEV_ITERATIONS = [
    "one --integrity-only invocation (08:02Z; hash checks only, pass 71/71; no child, nothing written)",
    "one shell invocation that failed before Python started (a missing timing utility); its shell redirect created one scratch "
    "file outside the repository holding the 60-byte shell error, which was deleted at once (deviation D-3)",
    "one --preview invocation of the partial script as found (08:02-08:08Z; computed in memory, nothing written, no child)",
    "one COMPLETE run of an earlier state of this script (09:02:23-09:10:24Z, same command) that wrote consumer-census.json "
    "(sha256 bcbf2d25f29572f9ddbc166fa3c2f7a48ca3edd57f30cfe9d9f1d967879c47be, 26413590 bytes) and consumer-census.md (sha256 "
    "9c8c72398ac1ca595767516a50ed050872fcb403e821c81319771ebd217eb684, 9678560 bytes), from cu_check.py sha256 "
    "b1f2d718189ba4ad550a15c7329654be7d25252de3f3fe877df32816fcbe4e77. Its readings were those of the recorded run. Reading it "
    "showed (i) its closing check listed '__main__' (this script, which lives under dev-evidence/) among scanned-tree modules, "
    "which a reader could mistake for an import of a scanned module (CU-5), and (ii) the card-abbreviation observation was not "
    "stated in words. Both are presentation fixes (D-8); the files were rewritten by the recorded run",
    "ten in-memory development invocations (08:09-09:01Z) that imported this script (never a scanned module): the S-3 pass state; "
    "two listings of the hashing sites; four previews of main() (one stopped on a KeyError in the new M-16 code, fixed); two checks "
    "of the S-1 pass for the SE-3 event file (before and after C12); one listing of the S-3 routes and computed-key stores. Each "
    "ran the integrity checks without git, installed the guard, started no child and wrote nothing; one ran as a background "
    "command (D-7)",
]
REDACT_REVERSED = ("edualc", "ciporhtna", "supo", "tennos", "ukiah", "xedoc", "edocnepo", "tpg", "inimeg", "amall", "lartsim",
                   "newq", "keespeed", "mlg", "iaz")


def redact(text):
    counts = {}
    for rv in REDACT_REVERSED:
        tok = rv[::-1]
        n = len(re.findall(re.escape(tok), text, flags=re.I))
        if n:
            counts["token#%d" % REDACT_REVERSED.index(rv)] = n
            text = re.sub(re.escape(tok), "[redacted-name]", text, flags=re.I)
    return text, counts


def name_counts(text):
    return sum(len(re.findall(re.escape(rv[::-1]), text, flags=re.I)) for rv in REDACT_REVERSED)


def _jsonable(x):
    if isinstance(x, (set, frozenset)):
        return sorted(x, key=str)
    if isinstance(x, tuple):
        return list(x)
    if isinstance(x, ast.AST):
        return "<ast %s line %s>" % (type(x).__name__, getattr(x, "lineno", "?"))
    return str(x)


def _write(rel, text):
    p = ab(rel)
    with open(p, "w") as fh:
        fh.write(text)
    return sha_bytes(text.encode())


def write_outputs_stop():
    OUT["partial_script_record"] = PARTIAL_SCRIPT
    OUT["deviations"] = DEVIATIONS
    jtxt, jc = redact(json.dumps(OUT, indent=1, sort_keys=True, default=_jsonable))
    L = ["# Consumer census -- TASK-20260924-5dfbfd -- STOPPED AT INTEGRITY (KQ-2 / CU-5)", "",
         "The census is INCOMPLETE and was not read. Failing checks:", ""]
    for c in OUT["CU5_integrity"]["checks"]:
        if not c["equal"]:
            L.append("- %s: `%s` expected `%s` actual `%s`" % (c["check"], c["path"], c["expected_sha256"], c["actual_sha256"]))
    mtxt, mc = redact("\n".join(L) + "\n")
    _write(OUT_DIR_REL + "/consumer-census.json", jtxt)
    _write(OUT_DIR_REL + "/consumer-census.md", mtxt)


def write_outputs():
    OUT["partial_script_record"] = PARTIAL_SCRIPT
    OUT["changes_to_partial_script"] = CHANGES_TO_PARTIAL
    OUT["development_iterations_before_this_run"] = DEV_ITERATIONS
    OUT["deviations"] = DEVIATIONS
    OUT["inference"] = INFERENCE
    OUT["command"] = COMMAND
    mtxt, mc = redact(render_md())
    # every hit, columnar, one row per line (the file stays reviewable); the rest of the record indented
    rows = OUT.pop("all_hits")
    cols = ["site", "file", "line", "function", "record_or_derived_value", "field", "mode", "effect", "rule", "reachable", "reached_by",
            "only_through_wildcard_match", "cc2_value", "cc2_coverage", "k_row", "class", "class_rule", "manual_reading", "paths",
            "notes", "source"]
    base = json.dumps(OUT, indent=1, sort_keys=True, default=_jsonable).rstrip()
    body = ",\n".join(json.dumps([r.get(c) for c in cols], default=_jsonable) for r in rows)
    jraw = base[:-1].rstrip() + ',\n "all_hits": {"columns": %s, "rows": [\n%s\n]}\n}\n' % (json.dumps(cols), body)
    OUT["all_hits"] = rows
    chk = json.loads(jraw)
    assert len(chk["all_hits"]["rows"]) == len(rows)
    jtxt, jc = redact(jraw)
    OUT_NAMES = {"json_redactions": jc, "md_redactions": mc}
    # the name counts of the final texts (after redaction) are recorded in the .md footer; they are 0 by construction
    tail = ("\n## 9. Name check\n\nModel-family and runtime names (a list held reversed in cu_check.py): occurrences replaced by "
            "`[redacted-name]` before writing: consumer-census.json %d, consumer-census.md %d (per-token counts in the json-free "
            "form: %s / %s). Occurrences remaining after redaction: consumer-census.json %d, consumer-census.md %d.\n"
            % (sum(jc.values()), sum(mc.values()), json.dumps(jc, sort_keys=True), json.dumps(mc, sort_keys=True),
               name_counts(jtxt), name_counts(mtxt)))
    mtxt = mtxt + tail
    hj = _write(OUT_DIR_REL + "/consumer-census.json", jtxt)
    hm = _write(OUT_DIR_REL + "/consumer-census.md", mtxt)
    print("wrote consumer-census.json sha256 %s (%d bytes)" % (hj, len(jtxt.encode())))
    print("wrote consumer-census.md sha256 %s (%d bytes)" % (hm, len(mtxt.encode())))
    return OUT_NAMES


COMMAND = ("cd <repository root> && (ulimit -v 3000000; PYTHONDONTWRITEBYTECODE=1 timeout 1500 python3 -B "
           "experiments/EXP-GFPN-05ff43/dev-evidence/consumer-census/cu_check.py)   # ulimit -v (kB) and timeout (s): "
           "machine protection only, never a result")
INFERENCE = {"requested_policy": "executor-implementation", "resolved_model_id": None,
             "resolved_model_id_note": "the dispatching session supplies no resolved model identifier; none is invented",
             "fallback_used": False, "bedrock_used": False, "network": "not used"}


def _t(x, n=None):
    s = md_escape(x if x is not None else "")
    return s if n is None or len(s) <= n else s[:n - 3] + "..."


def render_md():
    I, C1, C2, C4 = OUT["CU5_integrity"], OUT["CU1_site_table"], OUT["CU2_consumer_census"], OUT["CU4_other_child_records"]
    g = I.get("git", {})
    cl = OUT.get("closing_checks", {})
    L = []
    A = L.append
    A("# Consumer census -- TASK-20260924-5dfbfd -- EXP-GFPN-05ff43")
    A("")
    A("Zero-run, zero-solve consumer census computing the pre-declared readings (definitions, CU-5, CU-1, CU-2, CU-4) of the DRAFT "
      "AMD-EXP-GFPN-05ff43-20260924-consumercover. The draft is NOT approved and authorizes nothing; authority: DEC-20260924-a7453e. "
      "Archived by TASK-20260924-ad3f9a. OBSERVATIONS ONLY: nothing here is evidence about D, the quotient, H-GFPN-9a29be or "
      "HEUR-GFPN-DFLAT; no D and no degree is reported; nothing is decided and no approval is recommended. Each reading is stated as "
      "the draft words it.")
    A("")
    A("## 0. Run record")
    A("")
    A("- Command (as run): `%s`" % COMMAND)
    A("- Repository HEAD read: `%s`" % g.get("head"))
    A("- Dirty paths under tools/, harness/, orchestration/ or the experiment directory at start (git ls-files --modified --deleted "
      "--others --exclude-standard): %s" % (", ".join("`%s`" % p for p in g.get("repo_dirty_paths_under_scanned_or_experiment_dirs", [])) or "none"))
    A("- Started %s; finished %s. Peak RSS of this process (VmHWM): %s kB." % (OUT.get("started_at"), OUT.get("finished_at"), cl.get("max_rss_kB")))
    A("- Memory: %s. Declared threshold recorded here as the dispatcher's guard: MemAvailable < 2621440 kB (2.5 GiB)." % GUARD_THRESHOLD_NOTE)
    A("- Budget: card wall_clock_seconds 21600 (advisory checkpoint); maximum_runs 0 (binding): no run package was created.")
    A("- Randomness: none. The census is deterministic (sorted worklists and aggregation); no seed is used.")
    A("")
    A("Inference (KQ-7):")
    A("")
    A("```yaml")
    A("requested_policy: executor-implementation")
    A("resolved_model_id: null   # the dispatching session supplies no resolved model identifier; none is invented")
    A("fallback_used: false")
    A("bedrock_used: false")
    A("network: not used")
    A("```")
    A("")
    A("Dispatch preconditions cited from the dispatching session (not redone here): DP-1 (archive TASK-20260924-a28f0e, commit "
      "35870b058b45de0822a81da169cddfbfc597b7c8, receipt backfill 0d7b3e812, 0 mismatches; PR #1406 merged, cfc0a34ff); DP-2 (BATCH-e409ca "
      "revision b7c8193ed); DP-3 (executor lane claim f1107cddb, epoch 1, expires 2026-09-24T15:06:28Z, held by the dispatching session); "
      "DP-4 (memory guard, above); DP-5 (50 run directories; no r3 path).")
    A("")
    A("## 1. Integrity (CU-5 / KQ-2), applied first")
    A("")
    A("Result: **%s** -- %d of %d checks equal. Every check compares the full sha256 of the file on disk with the bound value." % (
        "PASS" if I["pass"] else "FAIL", I["n_equal"], I["n_checks"]))
    A("")
    A("| # | check | path | expected sha256 | actual sha256 | equal | bound by |")
    A("|---|---|---|---|---|---|---|")
    for i, c in enumerate(I["checks"], 1):
        A("| %d | %s | `%s` | `%s` | `%s` | %s | %s |" % (i, _t(c["check"]), c["path"], c["expected_sha256"], c["actual_sha256"], c["equal"], _t(c["expected_from"])))
    A("")
    A("Receipts read (sha256 of the receipt file):")
    A("")
    for k, v in sorted(I["receipts_used_sha256"].items()):
        A("- `%s` `%s`" % (k, v))
    A("")
    A("addendum_sha256 block of the TASK-20260924-a28f0e receipt, as read: `%s`" % _t(json.dumps(I["addendum_block_in_receipt"], sort_keys=True)))
    A("")
    A("Card KQ-2 (c) parenthetical abbreviations (informational; the check itself is against the receipt value):")
    A("")
    for c in I["card_abbreviation_checks"]:
        A("- `%s`: card `%s`, receipt `%s`, prefix %s, suffix %s" % (c["path"], c["card_abbreviation"], c["receipt_value"], c["prefix_matches"], c["suffix_matches"]))
    A("")
    for c in I["card_abbreviation_checks"]:
        if not (c["prefix_matches"] and c["suffix_matches"]):
            A("OBSERVATION (not a KQ-2 failure): the card's parenthetical abbreviation `%s` for `%s` does not match the receipt "
              "value `%s` at its %s. KQ-2 (c) binds the file to the receipt path_sha256, which it equals (check above); the "
              "parenthetical is a quotation of that value in the card." % (
                  c["card_abbreviation"], c["path"], c["receipt_value"], "prefix" if not c["prefix_matches"] else "suffix"))
            A("")
    A("Informational bindings (read for context; equality against the a28f0e receipt where it binds them):")
    A("")
    for c in I["informational_bindings"]:
        A("- `%s` sha256 `%s`; a28f0e path_sha256 `%s`; equal %s" % (c["path"], c["sha256"], c["a28f0e_path_sha256"], c["equal_if_bound"]))
    A("")
    A("Repository tools read (bound by no receipt; HEAD sha256 recorded, not a bar):")
    A("")
    A("| tool | selected as | sha256 on disk | sha256 at HEAD | disk == HEAD |")
    A("|---|---|---|---|---|")
    for e in OUT["scanned_files"]["repo_tools"]["selected"]:
        A("| `%s` | %s | `%s` | `%s` | %s |" % (e["file"], _t(e.get("selected_as") or "names " + ",".join(e["names_in_code_strings"])),
                                                e["sha256_disk"], e["sha256_HEAD"], e["disk_equals_HEAD"]))
    A("")
    A("Tools that name a run-package file only in docstrings or comments (not scanned): %s" % (
        ", ".join("`%s`" % e["file"] for e in OUT["scanned_files"]["repo_tools"]["not_selected_literal_only_in_docstrings_or_comments"]) or "none"))
    A("")
    A("Closing checks (after the census): bound files re-hashed %d, changed %s; scanned-tree modules in sys.modules: %s; byte code "
      "files under the scanned trees and the output directory at start %d and at end %d (pre-existing, listed in the json); children "
      "of this process at end: %s; guard refusals: %d." % (
          cl.get("bound_files_rehashed", 0), cl.get("bound_files_changed"), cl.get("scanned_tree_modules_in_sys_modules"),
          len(cl.get("pyc_files_under_scanned_trees_and_output_dir_at_start", [])), len(cl.get("pyc_files_at_end", [])),
          cl.get("children_of_this_process_at_end"), cl.get("guard_blocked_attempts", 0)))
    A("")
    A("## 2. CU-1 -- the CC-1 site table against census.json")
    A("")
    A("Equality rule (draft): %s." % C1["equality_rule"])
    A("")
    A("Transcription check: every CC-1 token this script compares was re-found verbatim in the draft's CC-1 text: %s "
      "(%d tokens); \"both r2 plans' 7\" defined in the CC-1 text: %s; CC-1 text sha256 `%s`." % (
          all(t["found_in_CC1_text"] for t in C1["transcription_token_checks"]), len(C1["transcription_token_checks"]),
          C1["both_r2_plans_7_defined_in_CC1_text"], C1["raw_cc1_text_sha256"]))
    A("")
    for e in C1["entries"]:
        A("### %s (census.json `%s`)" % (e["entry"], e["census_site"]))
        A("")
        A("| field | CC-1 | census.json | equal | rule / note |")
        A("|---|---|---|---|---|")
        for k, v in e["fields"].items():
            cj = [vv for kk, vv in v.items() if kk.startswith("census.json")]
            A("| %s | %s | %s | %s | %s |" % (k, _t(v.get("CC-1_expanded") or v.get("CC-1")), _t(cj[0] if cj else None), v.get("equal"),
                                              _t(v.get("rule") or v.get("note") or v.get("CC-1_additional_statement") or "")))
        A("")
        A("Differences: %s. Unstated fields: %s. census.json fields outside the CU-1 list (not compared): %s." % (
            e["differences"] or "none", e["unstated_fields"] or "none", e["census_fields_outside_CU1_list"] or "none"))
        A("")
    A("Totals: %d differences, %d unstated fields." % (C1["n_differences"], C1["n_unstated_fields"]))
    A("")
    A("Manual readings applied in CU-1 (carried from the partial script, reviewed here): MR-CU1-1 a CC-1 path is experiment-relative "
      "and is compared after prefixing experiments/EXP-GFPN-05ff43/ (coordination/ paths as written); MR-CU1-2 census.json carries one "
      "site line for the unresolved-argv entry U-5, which CC-1 states as 'line 98'; MR-CU1-3 S-3's file is stated inside its argv-line "
      "value. Alternative readings recorded, not applied:")
    A("")
    for e in C1["entries"]:
        for k, v in e["fields"].items():
            if v.get("alternative_reading"):
                A("- %s %s: %s" % (e["entry"], k, v["alternative_reading"]))
    A("")
    A("Reading rule (draft): %s" % C1["reading_rule"])
    A("")
    A("**CU-1 reading: %s**" % C1["reading"])
    A("")
    A("## 3. CU-2 -- consumer census")
    A("")
    A("Definitions applied: %s. SITE RECORD fields as read statically from the frozen producers:" % C2["definitions_applied"])
    A("")
    for k, v in OUT["site_record_fields"].items():
        A("- %s: %s" % (k, ", ".join("`%s`" % x for x in v)))
    A("")
    A("### 3.1 Method per access mode (CU-2 (a))")
    A("")
    for k, v in C2["mode_methods"].items():
        A("- **%s**: %s" % (k, v))
    A("")
    A("Method notes:")
    A("")
    for n in C2["method_notes"]:
        A("- %s" % n)
    A("")
    A("Scanned files: %d .py files of the five trees (%s), %d repository tools, %d embedded code strings located (%d parsed as "
      "Python and scanned); parse failures: %s. Every mode ran over every loaded module." % (
          sum(len(v) for v in OUT["scanned_files"]["experiment_trees"].values()),
          ", ".join("%s %d" % (k, len(v)) for k, v in OUT["scanned_files"]["experiment_trees"].items()),
          len(OUT["scanned_files"]["repo_tools"]["selected"]),
          sum(1 for e in OUT["scanned_files"]["embedded_code_strings"] if e["located"]),
          sum(1 for e in OUT["scanned_files"]["embedded_code_strings"] if e.get("parses_as_python") and not e.get("is_docstring")),
          OUT["scanned_files"]["parse_failures"] or "none"))
    A("")
    eng = OUT.get("engine", {})
    A("Engine: %s modules, %s functions; walkers / collectors detected: %s; module pins: %d (listed in the json)." % (
        eng.get("n_modules"), eng.get("n_functions"), ", ".join("`%s` (%s)" % (k, v[0]) for k, v in eng.get("walkers_and_collectors", {}).items()),
        len(eng.get("module_pins", {}))))
    A("")
    A("Reachability groups (M-19):")
    A("")
    for k, v in eng.get("reachability_groups", {}).items():
        A("- **%s** = %s: %d functions reached%s" % (REACH_CODE.get(k, k), k, v["n_functions_reached"],
                                                     ("; commands " + ", ".join(v["commands"])) if v.get("commands") else ""))
    A("")
    A("### 3.2 Hit counts")
    A("")
    A("| site | hits | by mode | by effect | unclassified | reachable | files with hits | fixpoint converged / function runs |")
    A("|---|---|---|---|---|---|---|---|")
    for site, per in C2["per_site"].items():
        A("| %s | %d | %s | %s | %d | %d | %d | %s / %s |" % (site, per["n_hits"], _t(json.dumps(per["hits_by_mode"])), _t(json.dumps(per["hits_by_effect"])),
                                                           per["n_unclassified"], per["n_reachable"], per["files_with_hits"],
                                                           per["engine"]["converged"], per["engine"]["function_runs"]))
    A("")
    A("S-1 / S-2 class counts over their E1-E4 consumers: S-1 %s; S-2 %s." % (
        json.dumps(C2["per_site"]["S-1"]["c_class_counts"], sort_keys=True), json.dumps(C2["per_site"]["S-2"]["c_class_counts"], sort_keys=True)))
    A("")
    A("### 3.3 (b) S-3: every consumer with effect E1-E4, with its CC-2 value and row")
    A("")
    A("| file:line | function | record / derived value | field | mode | effect | reachable (groups) | CC-2 value / row / coverage | rule | manual reading |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for r in C2["per_site"]["S-3"]["b_consumers_E1_E4"]:
        A("| `%s:%d` | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (r["file"], r["line"], _t(r["function"]), _t(r["record_or_derived_value"], 160),
                                                                     _t(r["field"], 80), r["mode"], r["effect"], _t("; ".join(r["reached_by"]) or "false"),
                                                                     _t(r["cc2_coverage"]), _t(r["rule"], 220), _t(r.get("manual_reading") or "", 400)))
    A("")
    A("Consumers NOT COVERED: %d." % len(C2["per_site"]["S-3"]["b_not_covered"]))
    A("")
    A("### 3.4 (c) S-1 and S-2: consumers with effect E1-E4 OUTSIDE THE CLASS RULE")
    A("")
    A("Every S-1 / S-2 E1-E4 consumer, with its class, is in the full hit table (3.9). Those OUTSIDE THE CLASS RULE:")
    A("")
    A("| site | file:line | function | field | mode | effect | reachable | class rule |")
    A("|---|---|---|---|---|---|---|---|")
    for s in ("S-1", "S-2"):
        for r in C2["per_site"][s]["c_outside_class_rule"]:
            A("| %s | `%s:%d` | %s | %s | %s | %s | %s | %s |" % (s, r["file"], r["line"], _t(r["function"]), _t(r["field"], 80), r["mode"], r["effect"],
                                                              _t("; ".join(r["reached_by"]) or "false"), _t(r["class_rule"], 500)))
    A("")
    A("### 3.5 (d) CC-2 rows K-1..K-5")
    A("")
    A("| row | what | found | hits | effects | reachable | groups | lines |")
    A("|---|---|---|---|---|---|---|---|")
    for kid, k in C2["per_site"]["S-3"]["d_K_rows"].items():
        A("| %s | %s | %s | %d | %s | %s | %s | %s |" % (kid, _t(k["what"]), k["found"], k["n_hits"], ",".join(k["effects"]), k["reachable"],
                                                      _t("; ".join(k["reached_by"])), _t(", ".join(k["lines"]))))
    A("")
    A("### 3.6 Derived-value fixpoint")
    A("")
    for site, d in C2["derived_value_fixpoint"].items():
        A("- %s: %d derived values (in-memory structures and files), converged %s after %d function runs; derived files carrying %s data: %s." % (
            site, d["n_derived_values"], d["converged"], d["function_runs"], site, ", ".join("`%s`" % f for f in sorted(d["files"])) or "none"))
    A("")
    A("Every derived value with its writers, origins and number of reader hits is listed in the json (CU2_consumer_census.derived_value_fixpoint).")
    A("")
    A("### 3.7 M-16 file-hash supplement")
    A("")
    m = C2["m16_file_hash_census"]
    A("Method: %s. Sites: %d (%d in pinned modules); hits per pass: %s; unresolved sites: %d, of which E1-E4 without a manual reading: %d." % (
        m["method"], m["n_sites"], m["n_pinned"], json.dumps(m["hits_per_pass"], sort_keys=True), m["n_unresolved"],
        m["n_unresolved_E1_E4_without_manual_reading"]))
    A("")
    A("Resolved by manual reading:")
    A("")
    for r in m["resolved_by_manual_reading"]:
        A("- `%s:%d` %s: files %s; effect %s. %s" % (r["file"], r["line"], r["function"], r["resolved_files"], r["effect"], _t(r["manual_reading"])))
    A("")
    A("Unresolved sites (file identity not resolved statically; listed with their effect):")
    A("")
    A("| file:line | function | call | path expression | effect | why unresolved |")
    A("|---|---|---|---|---|---|")
    for r in m["unresolved_sites"]:
        A("| `%s:%d` | %s | %s | `%s` | %s | %s |" % (r["file"], r["line"], _t(r["function"]), _t(r["call"]), _t(r["path_expr"]), r["effect"], _t("; ".join(r["unresolved_why"]))))
    A("")
    A("### 3.8 Recorded manual readings")
    A("")
    for (f, ln), v in sorted(HASH_MANUAL.items()):
        A("- **%s** `%s:%d` (file-hash site): %s" % (v["id"], f, ln, v["reading"]))
    for (f, ln, s), v in sorted(HIT_MANUAL.items()):
        A("- **%s** `%s:%d` (%s hit; not a consumer: %s): %s" % (v["id"], f, ln, s, v["not_a_consumer"], v["reading"]))
    A("- **MR-SE3** (rule R-CL-OUT-SE3, carried from the partial script): the SE-3 wrapper's own reads of each attempt's result are "
      "OUTSIDE THE CLASS RULE on the draft's literal words; the draft's rule names alpha, beta and the frozen solve() / run_system() "
      "bodies, and names 'reads a non-recorded attempt's result' OUTSIDE. The wrapper body is not named as an exception. This is the "
      "literal reading; whether 'covered by SE-2..SE-4' reaches the wrapper body is for the approval act.")
    A("- **MR-PIN / MR-PIN-TEST / module-level pins**: tool modules pinned to other experiments or unit tests contribute no run-package "
      "read taint (M-8); the pins and their pinned reads are listed in the json (engine.module_pins, engine.pinned_reads).")
    A("")
    A("### 3.9 CU-2 reading")
    A("")
    A("Reading inputs: `%s`" % json.dumps(C2["reading_inputs"], sort_keys=True))
    A("")
    A("Reading rule (draft): %s" % C2["reading_rule"])
    A("")
    A("**CU-2 reading: %s**" % C2["reading"])
    A("")
    A("Not a bar, by the draft (ruled by the approval act): %s." % C2["not_a_bar_by_the_draft"])
    A("")
    A("### 3.10 Every hit")
    A("")
    A("Every aggregated hit (per file, line, site, field, mode), S-3 first. `wild` marks a hit reached only through a computed-key "
      "match (M-14). Full rule texts, paths and notes are in the json (all_hits).")
    A("")
    A("| # | site | file:line | function | record / derived value | field | mode | effect | reach | class / CC-2 | wild | rule |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    order = {"S-3": 0, "S-2": 1, "S-1": 2}
    for i, r in enumerate(sorted(OUT["all_hits"], key=lambda r: (order.get(r["site"], 3), r["file"], r["line"], r["field"], r["mode"])), 1):
        A("| %d | %s | `%s:%d` | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, r["site"], r["file"].replace(EXP + "/", ""), r["line"], _t(r["function"], 60), _t(r["record_or_derived_value"], 90), _t(r["field"], 60),
            r["mode"], r["effect"], "yes" if r["reachable"] else "no", _t(r.get("cc2_coverage") or r.get("class") or "", 60),
            "yes" if r["only_through_wildcard_match"] else "", _t(r["rule"], 110)))
    A("")
    A("## 4. CU-4 -- other child records (informational)")
    A("")
    A("Non-msolve child launches listed from census.json all_launch_calls: %d (%d traced as sources). E1-E4 consumers of their records "
      "or derived values: %d; reached only through a computed-key match (over-approximation, counted per function in the json): %d; "
      "hits of all effects: %d. %s" % (len(C4["child_launches_listed"]), C4["n_tainted_launches"], C4["n_consumers_E1_E4"],
                                        C4["n_consumers_E1_E4_reached_only_through_a_wildcard_match"], C4["n_hits_all_effects"], C4["note"]))
    A("")
    A("| child launch | program | file:line | function | field | mode | effect | clock or unseeded random | rule |")
    A("|---|---|---|---|---|---|---|---|---|")
    for r in C4["consumers_E1_E4"]:
        A("| `%s` | %s | `%s:%d` | %s | %s | %s | %s | %s | %s |" % (r["child_launch"], _t(r["program"], 60), r["file"].replace(EXP + "/", ""), r["line"],
                                                                 _t(r["function"], 50), _t(r["field"], 50), r["mode"], r["effect"],
                                                                 _t(r["clock_or_unseeded_random"], 90), _t(r["rule"], 100)))
    A("")
    A("## 5. Children, guard, imports")
    A("")
    A("Child processes started by this script (integrity phase only, read-only git; the repository path is shown as a label):")
    A("")
    for c in OUT["children_started"]:
        A("- `%s` (%s)%s" % (" ".join(c["argv"]), c["phase"], (", stdin " + c["stdin"]) if c.get("stdin") else ""))
    A("")
    gd = OUT.get("child_launch_guard", {})
    A("In-process child-launch guard installed at %s (after integrity); refused attempts: %d. No msolve, valgrind, callgrind_annotate, gp, "
      "Sage or builder child was started; no module of a scanned tree was imported (closing check above); no run package was created." % (
          gd.get("installed_at"), len(gd.get("blocked_attempts", []))))
    A("")
    A("## 6. The interrupted previous session, and changes to its script")
    A("")
    A("A previous Executor session on this task was interrupted at about 07:55-07:59Z by a worker / container restart (an "
      "infrastructure interruption; never evidence, never a result). It left only a partial cu_check.py: size %d bytes, %d lines, mtime "
      "%s, sha256 `%s`. Decision: %s. The partial file lacked the output layer (write_outputs / write_outputs_stop were called but not "
      "defined), so it could not have produced deliverables. Changes made:" % (
          PARTIAL_SCRIPT["size_bytes"], PARTIAL_SCRIPT["lines"], PARTIAL_SCRIPT["mtime_utc"], PARTIAL_SCRIPT["sha256"], PARTIAL_SCRIPT["decision"]))
    A("")
    for c in CHANGES_TO_PARTIAL:
        A("- %s" % c)
    A("")
    A("Development iterations before this run (all recorded; none wrote a deliverable):")
    A("")
    for d in DEV_ITERATIONS:
        A("- %s" % d)
    A("")
    A("The three deliverables come from ONE complete run of the final cu_check.py (section 0).")
    A("")
    A("## 7. Deviations")
    A("")
    for d in DEVIATIONS:
        A("- %s" % d)
    A("")
    A("## 8. What this census is not")
    A("")
    A("- Not evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT; no D and no degree is reported.")
    A("- Not an approval recommendation. The approval act (reserved TASK-20260924-7a8167 / DEC-20260924-e6638d) applies CU-5, CU-1, "
      "CU-2 and CU-4 to the archived census.")
    A("- Static only (draft transfer assumption (6); M-10): a consumer reached only through dynamic dispatch is not found here.")
    A("- No security statement about EcGFp5 or EcMasFp5.")
    return "\n".join(L) + "\n"


DEVIATIONS.extend([
    "D-1 INTERRUPTION: the previous Executor session on this task was interrupted (worker / container restart, about 07:55-07:59Z) "
    "before it returned. Infrastructure, never evidence. It left only the partial cu_check.py (173152 bytes, mtime "
    "2026-09-24T07:54:41Z, sha256 a4b9c7df64c0e7cd218d004ffeb08ef262d3c8557a2b1d4baf450742edf5ef75); no consumer-census.md or .json. "
    "This session READ IT IN FULL, REUSED it as unreviewed draft code, and repaired and completed it (C1-C11, section 6). The file "
    "at this path is therefore the final script, not the partial one; the dispatching session keeps the partial copy.",
    "D-2 METHOD REPAIRS DURING DEVELOPMENT: C1 (a false negative that hid K-1 and K-3), C2 / C10 (wildcard markers), C3 / C4 "
    "(unclassified hits), C5 (the M-16 file-hash supplement and the M-16b generic-verifier selection, which widen the scanned tool "
    "set beyond the literal-name selection). Each is a method change made before the one recorded run; none edits a reading, a "
    "definition or a disposition of the draft.",
    "D-3 SCRATCH FILE: one shell command (08:02Z) redirected output to a file in the session's temporary directory (outside the "
    "repository; path withheld: it carries a runtime name) before the command failed for a missing timing utility; the file held only "
    "the 60-byte shell error and was deleted at once. The card forbids scratch files; recorded here.",
    "D-4 BYTE CODE: implementation/__pycache__ exists in the v1 tree before this task (listed by the closing check); this task wrote "
    "no byte code (python3 -B and PYTHONDONTWRITEBYTECODE=1; sys.dont_write_bytecode).",
    "D-5 NAME REDACTION: source lines quoted in hit rows and one scanned tool path contain model-family or runtime names; they are "
    "replaced by [redacted-name] in the written text (section 9 counts).",
    "D-7 TOOL OUTPUT CAPTURE: some development invocations ran as background commands; the tool runtime captured their stdout "
    "in its own task-output location outside the repository (path withheld: it carries a runtime name). This session created "
    "no such file itself; the recorded run's stdout was captured the same way.",
    "D-8 SECOND COMPLETE RUN: the deliverables were first written by a complete run at 09:02-09:10Z (hashes in section 6) and then "
    "rewritten by the recorded run after two presentation fixes to the closing check and the integrity section (no change to the "
    "engine, a rule, a manual reading or a reading). The three deliverables come from the recorded run alone.",
    "D-6 MANUAL READINGS: MR-H-1, MR-H-2, MR-CI-1, MR-WILD-1 and MR-TUPLE-1 were recorded by this task after reading the cited lines; "
    "MR-SE3, MR-PIN and the module pins are carried from the partial script; R-CL-OUT-SE4 / R-CL-A-SE4F is a class rule added by this "
    "task (a literal reading, as MR-SE3). All are listed in section 3.8 so the approval act can rule on each.",
])


def md_escape(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


def run_passes(census):
    results = {}
    for ps in ("S1", "S2", "S3", "C4"):
        reset_engine({ps})
        st = analyze_all()
        ag = aggregate_hits()
        hits = [ag[k] for k in sorted(ag)]
        results[ps] = {"stats": st, "hits": hits, "derived_writes": list(DERIVED_WRITES), "control_writes": list(CONTROL_WRITES),
                       "files": {k: sorted({"%s @ %s" % (o, "/".join(p) or ".") for (o, p, via, full, ser) in v})[:200] for k, v in FILE_TAGS.items()},
                       "n_file_tags": {k: len(v) for k, v in FILE_TAGS.items()}}
        results[ps]["file_names_with_site_data"] = sorted(k for k, v in FILE_TAGS.items() if v)
        results[ps]["hash_sites"] = hash_census(ps)
        print("pass %s: %s, %d aggregated hits, %d file-hash hits" % (ps, st, len(hits), len(results[ps]["hash_sites"]["hits"])),
              file=sys.stderr, flush=True)
    return results


def main():
    t0 = datetime.datetime.now(datetime.timezone.utc)
    DEV = "--preview" in sys.argv
    I = integrity(run_git=not DEV)
    OUT["CU5_integrity"] = I
    if not I["pass"]:
        OUT["child_launch_guard"] = {"installed_at": None, "blocked_attempts": [], "note": "not installed: stopped at integrity"}
        OUT["stop"] = "KQ-2 / CU-5 integrity failed; the census stopped before any reading (INCOMPLETE)"
        write_outputs_stop()
        return 3
    PYC_BEFORE[:] = pyc_list()
    install_guard()
    OUT["child_launch_guard"] = GUARD
    census = json.load(open(ab(CENSUS_DIR + "/census.json")))
    draft_text = open(ab(CONSUMERCOVER)).read()
    OUT["files_read"][CONSUMERCOVER] = HASHES[CONSUMERCOVER]
    OUT["files_read"][CENSUS_DIR + "/census.json"] = HASHES[CENSUS_DIR + "/census.json"]
    plans = {PLAN_V2_R2: load_json(PLAN_V2_R2), PLAN_A1_R2: load_json(PLAN_A1_R2)}
    for rel in (PLAN_V2_R2, PLAN_A1_R2):
        OUT["files_read"][rel] = HASHES[rel]
    # CU-1
    OUT["CU1_site_table"] = cu1(draft_text, census)
    # CU-2 / CU-4
    scan = load_scanned(census, I.get("git"))
    OUT["scanned_files"] = scan
    fields = site_record_fields()
    set_schema(fields)
    for v in fields.values():
        ALL_FIELD_NAMES.update(x.replace("run().", "") for x in v)
    OUT["site_record_fields"] = fields
    c4 = setup_launch_sources(census)
    compute_module_pins()
    compute_summaries()
    res = run_passes(census)
    g = build_graph()
    groups, cmds = reachability(g, plans)
    fb = frozen_bodies(g)
    reach_any = set()
    for gg in groups.values():
        reach_any |= gg["reached"]
    REACH_ANY.update(reach_any)
    for ps in res:
        have = {(a["file"], a["line"], a["site"]) for a in res[ps]["hits"] if a["mode"] in ("m4", "m8")
                and any(("sha256" in n or "hash" in n) for n in a["notes"])}
        for hh in res[ps]["hash_sites"]["hits"]:
            ag = hash_hit_to_agg(ps, hh)
            if (ag["file"], ag["line"], ag["site"]) not in have:
                res[ps]["hits"].append(ag)
        for a in res[ps]["hits"]:
            a["effect"] = classify_hit(a)
    assemble(res, groups, cmds, fb, c4, reach_any)
    OUT["engine"] = {"walkers_and_collectors": {k: v for k, v in sorted(WALKERS.items())}, "loader_helpers": sorted(LOADER),
                     "writer_helpers": sorted(WRITER), "hashing_helpers": sorted(HASHER), "module_pins": dict(sorted(MODULE_PIN.items())),
                     "pinned_reads": sorted([list(x) for x in PINNED_READS]), "n_modules": len(MODS), "n_functions": len(FUNCS),
                     "reachability_groups": {k: {"roots": v["roots"], "commands": v.get("commands"), "n_functions_reached": len(v["reached"])}
                                             for k, v in groups.items()},
                     "frozen_bodies": {k: sorted(v) for k, v in fb.items()}, "runtime_bindings": [list(x) for x in RUNTIME_BINDINGS]}
    closing()
    OUT["finished_at"] = now()
    if DEV:
        preview()
        return 0
    write_outputs()
    return 0


SITE_RECORD_LABEL = {"S-1": "the S-1 record (a solve() result, its solver mapping, every key solve() sets)",
                     "S-2": "the S-2 record (a run_system record and the keys a1_health derives from it)",
                     "S-3": "the S-3 record (res['instructions_callgrind'] and its child mapping)"}


def clock_or_random(a):
    f = a["field"].lower()
    if any(w in f for w in ("wall", "time", "seconds", "timed_out", "timeout", "started", "finished", "utc", "mtime")):
        return "clock: yes (field %s)" % a["field"]
    fo = FUNCS.get(a["fid"])
    if fo is not None:
        for x in fn_all_nodes(fo):
            if isinstance(x, ast.Call) and dotted(x.func) in ("random.random", "random.choice", "random.randint", "random.shuffle", "random.sample",
                                                                "time.time", "time.monotonic", "datetime.datetime.now"):
                return "clock or unseeded random call in the enclosing function (%s), not necessarily on the gating input" % dotted(x.func)
    return "no"


REACH_CODE = {}          # reachability group name -> short code (legend in the json: reachability_group_codes)


def hit_row(a, reach_groups, extra):
    mod = MODS_BY_REL.get(a["file"])
    vias = sorted(a["vias"])
    row = {"file": a["file"], "line": a["line"], "function": a["function"], "site": a["site"],
           "record_or_derived_value": ("site record: " + SITE_RECORD_LABEL.get(a["site"], a["site"])) if not vias else
           ("derived value: " + "; ".join(v[:90] for v in vias[:2]) + (" (+%d more)" % (len(vias) - 2) if len(vias) > 2 else "")),
           "field": a["field"][:120], "mode": a["mode"], "effect": a["effect"][0] if a.get("effect") else "UNCLASSIFIED",
           "rule": a["effect"][1] if a.get("effect") else None,
           "reachable": bool(reach_groups), "reached_by": [REACH_CODE.get(g, g) for g in reach_groups],
           "paths": [x[:80] for x in sorted(a.get("paths") or set())[:2]],
           "only_through_wildcard_match": bool(vias) and all(v.endswith(WILD) for v in vias),
           "notes": [x[:140] for x in sorted(a["notes"])[:1]], "source": (mod.line(a["line"]).strip()[:120] if mod else "")}
    row.update(extra)
    return row


def assemble(res, groups, cmds, fb, c4, reach_any):
    for i, k in enumerate(groups):
        REACH_CODE[k] = "G%d" % (i + 1)
    OUT["reachability_group_codes"] = {v: k for k, v in REACH_CODE.items()}

    def groups_of(fid):
        return [k for k, v in groups.items() if fid in v["reached"]]
    cu2 = {"definitions_applied": "draft pre_approval_readings.definitions (SITE RECORD, DERIVED VALUE, ACCESS MODES, EFFECT CLASSES, CONSUMER, SCANNED FILES, REACHABLE)",
           "mode_methods": MODE_METHODS, "method_notes": METHOD_NOTES, "per_site": {}, "hits": [], "derived_value_fixpoint": {},
           "control_dependent_writes": {}}
    all_rows = []
    for ps, site in (("S1", "S-1"), ("S2", "S-2"), ("S3", "S-3")):
        R_ = res[ps]
        rows = []
        for a in R_["hits"]:
            extra = {}
            if site == "S-3":
                cov = s3_coverage(a)
                extra["cc2_coverage"] = cov["coverage"] if cov else None
                extra["cc2_value"] = cov["value"] if cov else v_value_of(a)
                extra["k_row"] = k_row_of(a)
            else:
                cl = class_of(a, fb)
                extra["class"] = cl["class"] if cl else None
                extra["class_rule"] = cl["rule"] if cl else None
            mr = HIT_MANUAL.get((a["file"], a["line"], site))
            if mr:
                extra["manual_reading"] = "%s: %s" % (mr["id"], mr["reading"])
                if mr["not_a_consumer"] and site == "S-3" and extra.get("cc2_coverage"):
                    extra["cc2_coverage"] = "n/a: not an S-3 consumer (%s)" % mr["id"]
            if a.get("m16_manual_reading"):
                extra["manual_reading"] = (extra.get("manual_reading", "") + " " + a["m16_manual_reading"]).strip()
            rows.append(hit_row(a, groups_of(a["fid"]), extra))
        import collections
        by_mode = collections.Counter(r["mode"].replace("m7+", "m7 (via ") + (")" if r["mode"].startswith("m7+") else "") for r in rows)
        by_eff = collections.Counter(r["effect"] for r in rows)
        unc = [r for r in rows if r["effect"] == "UNCLASSIFIED"]
        per = {"n_hits": len(rows), "hits_by_mode": dict(sorted(by_mode.items())), "hits_by_effect": dict(sorted(by_eff.items())),
               "n_unclassified": len(unc), "n_reachable": sum(1 for r in rows if r["reachable"]), "engine": R_["stats"],
               "files_with_hits": len({r["file"] for r in rows})}
        if site == "S-3":
            e14 = [r for r in rows if r["effect"] in ("E1", "E2", "E3", "E4")]
            per["b_consumers_E1_E4"] = e14
            per["b_not_covered"] = [r for r in e14 if r["cc2_coverage"] and r["cc2_coverage"].startswith("NOT COVERED")]
            kt = {}
            for kid, k in K_ROWS.items():
                hs = [r for r in rows if r.get("k_row") == kid]
                kt[kid] = {"what": k["what"], "found": bool(hs), "n_hits": len(hs), "reachable": any(r["reachable"] for r in hs),
                           "reached_by": sorted({g for r in hs for g in r["reached_by"]}), "effects": sorted({r["effect"] for r in hs}),
                           "lines": sorted({"%s:%d" % (os.path.basename(r["file"]), r["line"]) for r in hs})[:40]}
            per["d_K_rows"] = kt
        else:
            e14 = [r for r in rows if r["effect"] in ("E1", "E2", "E3", "E4")]
            per["c_consumers_E1_E4"] = [[r["file"], r["line"], r["field"], r["mode"], r["effect"], r["class"]] for r in e14]
            per["c_consumers_E1_E4_columns"] = ["file", "line", "field", "mode", "effect", "class (full rows: all_hits)"]
            per["c_outside_class_rule"] = [r for r in e14 if r["class"] == "OUTSIDE THE CLASS RULE"]
            per["c_class_counts"] = dict(collections.Counter(r["class"] for r in e14))
        cu2["per_site"][site] = per
        all_rows += rows
        # derived-value fixpoint
        dv = {}
        for w in R_["derived_writes"]:
            for into in w["into"]:
                d = dv.setdefault(into, {"origins": set(), "writers": set(), "from": set()})
                d["origins"].update(w["origins"])
                d["writers"].add("%s:%d" % (w["file"], w["line"]))
                d["from"].update(w.get("from_via") or [])
        readers = collections.Counter()
        for r in rows:
            for v in (r["record_or_derived_value"].split("derived value: ", 1)[1].split("; ") if r["record_or_derived_value"].startswith("derived") else []):
                readers[v.split(" (+")[0]] += 1
        cu2["derived_value_fixpoint"][site] = {
            "n_derived_values": len(dv), "converged": R_["stats"]["converged"], "function_runs": R_["stats"]["function_runs"],
            "files": {k: {"n_tags": R_["n_file_tags"][k], "datum_paths_sample": R_["files"][k][:40]} for k in sorted(R_["files"])},
            "values": {k: {"origins": sorted(v["origins"])[:12], "writers": sorted(v["writers"])[:12], "derived_from": sorted(v["from"])[:8],
                           "n_reader_hits": readers.get(k, 0)} for k, v in sorted(dv.items())}}
        cu2["control_dependent_writes"][site] = [dict(x, controlled_by_origins=x["controlled_by_origins"][:6]) for x in R_["control_writes"]][:4000]
    # C5: the M-16 file-hash census (pass-independent resolution; the hits are in the per-site lists above)
    def m16_row(r):
        e = r.get("effect")
        return {k: v for k, v in dict(r, effect=e[0] if e else "UNCLASSIFIED", effect_rule=e[1] if e else None).items()
                if k not in ("node", "fid")}
    un = [m16_row(r) for r in res["S1"]["hash_sites"]["unresolved"]]
    un_e14 = [r for r in un if r["effect"] in ("E1", "E2", "E3", "E4", "UNCLASSIFIED")]
    cu2["m16_file_hash_census"] = {
        "method": ("every hashing call (hashlib.*, *sha256_file, *sha256_bytes, sha helpers detected by ast) in every scanned, unpinned "
                   "module whose argument is a FILE's bytes or path; the file is resolved from constants, module-level path "
                   "expressions, loop iterables and the callers' arguments (depth 3); a resolved file that carries a pass's site data "
                   "(that pass's derived-file set) or is a site file is a hit of that pass (mode m4, or m8 for a site file)"),
        "n_sites": len(hash_sites()), "n_pinned": sum(1 for h in hash_sites() if h["pinned"]),
        "hits_per_pass": {SITE_OF.get(ps, "CU-4"): len(res[ps]["hash_sites"]["hits"]) for ps in res},
        "resolved_by_manual_reading": [m16_row(r) for r in res["S1"]["hash_sites"]["hits"] + res["S1"]["hash_sites"]["not_hits"]
                                       if r["resolution"].startswith("manual")],
        "unresolved_sites": un, "n_unresolved": len(un), "n_unresolved_E1_E4_without_manual_reading": len(un_e14),
        "not_hits_per_pass": {SITE_OF.get(ps, "CU-4"): [m16_row(r) for r in res[ps]["hash_sites"]["not_hits"]][:400] for ps in res},
        "derived_files_with_site_data_per_pass": {SITE_OF.get(ps, "CU-4"): res[ps]["file_names_with_site_data"] for ps in res}}
    n_unc = sum(p["n_unclassified"] for p in cu2["per_site"].values())
    n_nc = len(cu2["per_site"]["S-3"]["b_not_covered"])
    n_out = len(cu2["per_site"]["S-1"]["c_outside_class_rule"]) + len(cu2["per_site"]["S-2"]["c_outside_class_rule"])
    parse_fail = OUT["scanned_files"]["parse_failures"]
    a_complete = (n_unc == 0 and not parse_fail and not un_e14)
    cu2["reading_inputs"] = {"a_every_mode_searched_in_every_scanned_file": not parse_fail, "a_parse_failures": parse_fail,
                             "a_unclassified_hits": n_unc, "a_m16_unresolved_E1_E4_sites_without_manual_reading": len(un_e14),
                             "a_complete": a_complete, "b_not_covered": n_nc, "c_outside_class_rule": n_out}
    cu2["reading_rule"] = ("this draft is approvable as written ONLY IF (a) is complete: every mode was searched in every scanned file and 0 hits are "
                           "unclassified; AND (b) finds NO consumer \"NOT COVERED\"; AND (c) finds NO consumer \"OUTSIDE THE CLASS RULE\". "
                           "Otherwise it is NOT approvable as written, and the approval act orders a successor draft.")
    failed = [x for x, bad in (("(a) incomplete (%d unclassified hits; %d unresolved E1-E4 file-hash sites without a manual reading%s)" % (
                                   n_unc, len(un_e14), ", parse failures" if parse_fail else ""), not a_complete),
                               ("(b) %d consumer(s) NOT COVERED" % n_nc, n_nc > 0), ("(c) %d consumer(s) OUTSIDE THE CLASS RULE" % n_out, n_out > 0)) if bad]
    cu2["reading"] = ("NOT approvable as written (CU-2): " + "; ".join(failed)) if failed else \
        "CU-2 conditions (a), (b), (c) hold; CU-2 does not make the draft 'NOT approvable as written'"
    cu2["not_a_bar_by_the_draft"] = "a CC-2 row the census does not find; a reachability different from any expectation; consumers with effect E5, E6 or E7"
    OUT["CU2_consumer_census"] = cu2
    # CU-4
    rows4 = []
    for a in res["C4"]["hits"]:
        if a["effect"] and a["effect"][0] in ("E1", "E2", "E3", "E4") and not (a["vias"] and all(v.endswith(WILD) for v in a["vias"])):
            origin = sorted(a["origins"])[0]
            site = origin.split("|")[0][3:]
            prog = C4_SITES.get((site.rsplit(":", 1)[0], int(site.rsplit(":", 1)[1])), {}).get("program") if ":" in site else None
            rows4.append(hit_row(a, groups_of(a["fid"]), {"child_launch": site, "program": prog, "clock_or_unseeded_random": clock_or_random(a)}))
    wild4 = [a for a in res["C4"]["hits"] if a["effect"] and a["effect"][0] in ("E1", "E2", "E3", "E4") and a["vias"] and all(v.endswith(WILD) for v in a["vias"])]
    OUT["CU4_other_child_records"] = {"child_launches_listed": c4, "n_tainted_launches": sum(1 for x in c4 if x["tainted"]),
                                      "consumers_E1_E4": rows4, "n_consumers_E1_E4": len(rows4),
                                      "n_consumers_E1_E4_reached_only_through_a_wildcard_match": len(wild4),
                                      "consumers_E1_E4_only_through_wildcard_by_function": dict(sorted(__import__("collections").Counter(
                                          "%s:%s" % (a["file"], a["function"]) for a in wild4).items())),
                                      "n_hits_all_effects": len(res["C4"]["hits"]),
                                      "note": "INFORMATIONAL (draft CU-4). The approval act rules on each, as DEC-20260924-afdc3b ruled CN-4."}
    OUT["hit_counts"] = {"S-1": len(res["S1"]["hits"]), "S-2": len(res["S2"]["hits"]), "S-3": len(res["S3"]["hits"]), "CU-4": len(res["C4"]["hits"])}
    OUT["all_hits"] = all_rows


PYC_BEFORE = []


def pyc_list():
    out = []
    for key in TREES:
        out += sorted(os.path.relpath(f, REPO) for f in glob.glob(ab(TREES[key]) + "/**/*.pyc", recursive=True))
    out += sorted(os.path.relpath(f, REPO) for f in glob.glob(ab(OUT_DIR_REL) + "/**/*.pyc", recursive=True))
    return out


def closing():
    changed = [r for r, h in HASHES.items() if os.path.exists(ab(r)) and sha_bytes(open(ab(r), "rb").read()) != h]
    me = os.path.abspath(__file__)          # this census script itself (it lives under dev-evidence/ and is excluded)
    scanned_mods = sorted(m for m, v in sys.modules.items() if getattr(v, "__file__", None) and os.path.abspath(v.__file__) != me and
                          any(os.path.abspath(v.__file__).startswith(ab(t)) for t in list(TREES.values()) + list(REPO_TOOL_DIRS) + [EXP + "/dev-evidence"]))
    OUT["closing_checks"] = {"bound_files_rehashed": len(HASHES), "bound_files_changed": changed,
                             "scanned_tree_modules_in_sys_modules": scanned_mods,
                             "scanned_tree_modules_note": ("modules loaded from the five trees, tools/, harness/, orchestration/ or any "
                                                           "dev-evidence/ directory, excluding this census script itself (__main__)"),
                             "pyc_files_under_scanned_trees_and_output_dir_at_start": PYC_BEFORE, "pyc_files_at_end": pyc_list(),
                             "children_of_this_process_at_end": children_now(), "guard_blocked_attempts": len(GUARD["blocked_attempts"]),
                             "max_rss_kB": int(open("/proc/self/status").read().split("VmHWM:")[1].split()[0]),
                             "memory_guard": GUARD_THRESHOLD_NOTE}


def preview():
    import collections
    cu2 = OUT["CU2_consumer_census"]
    print("CU-1:", OUT["CU1_site_table"]["n_differences"], OUT["CU1_site_table"]["n_unstated_fields"], OUT["CU1_site_table"]["reading"])
    for e in OUT["CU1_site_table"]["entries"]:
        print("  ", e["entry"], "diff", e["differences"], "unstated", e["unstated_fields"])
    print("tokens not found:", [t for t in OUT["CU1_site_table"]["transcription_token_checks"] if not t["found_in_CC1_text"]],
          OUT["CU1_site_table"]["both_r2_plans_7_defined_in_CC1_text"])
    for site, per in cu2["per_site"].items():
        print(site, {k: v for k, v in per.items() if k in ("n_hits", "hits_by_mode", "hits_by_effect", "n_unclassified", "n_reachable", "c_class_counts")})
    print("READING", cu2["reading"])
    for kid, k in cu2["per_site"]["S-3"]["d_K_rows"].items():
        print(kid, k["found"], k["n_hits"], k["reachable"], k["effects"], k["lines"][:8])
    show = [a for a in sys.argv if a.startswith("--show=")]
    for sh in show:
        what = sh.split("=", 1)[1]
        rows = OUT["all_hits"]
        if what == "unc":
            sel = [r for r in rows if r["effect"] == "UNCLASSIFIED"]
        elif what == "s3e14":
            sel = cu2["per_site"]["S-3"]["b_consumers_E1_E4"]
        elif what == "out":
            sel = cu2["per_site"]["S-1"]["c_outside_class_rule"] + cu2["per_site"]["S-2"]["c_outside_class_rule"]
        elif what == "c4":
            sel = OUT["CU4_other_child_records"]["consumers_E1_E4"]
        else:
            sel = [r for r in rows if r["site"] == what]
        cf = collections.Counter("%s %s" % (r["site"], r["file"].split("/")[-1]) for r in sel)
        print("SHOW", what, len(sel), cf.most_common(40))
        for r in sel[:int(os.environ.get("SHOWN", "60"))]:
            print("  %s %s:%d %s | %s | %s | %s | %s | %s" % (r["site"], r["file"].split("/")[-1], r["line"], r["function"], r["field"][:40], r["mode"],
                                                           r["effect"], (r.get("cc2_coverage") or r.get("class") or "")[:40], r["source"][:110]))


if __name__ == "__main__" and INTEGRITY_ONLY:
    I = integrity(run_git=False)
    for c in I["checks"]:
        if not c["equal"]:
            print("UNEQUAL", c)
    print("integrity pass=%s %d/%d" % (I["pass"], I["n_equal"], I["n_checks"]))
    sys.exit(0 if I["pass"] else 3)
elif __name__ == "__main__":
    sys.exit(main())
