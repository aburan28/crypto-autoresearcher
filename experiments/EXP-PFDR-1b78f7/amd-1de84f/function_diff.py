"""AMD-20260929-1de84f C-2 build-equivalence certificate for EXP-PFDR-1b78f7.

    python3 experiments/EXP-PFDR-1b78f7/amd-1de84f/function_diff.py

Evaluates conditions E-1..E-4 verbatim and writes, next to this file,
source.diff (unified diff, frozen vs amended, every file below) and
function-diff.json.  E-5 (R01a) is a separate run.

Frozen reference: the bytes of each file at commit 1a037688c (the
TASK-20260928-f15632 archive), read with `git show 1a037688c:<path>`, whose
sha256 must equal experiments/EXP-PFDR-1b78f7/implementation-notes.yaml
frozen_source_sha256 / byte_unchanged_files.  The amended build is the working
tree.  No module of the engine is imported: every file is read as bytes and
parsed with `ast`.
"""
from __future__ import annotations

import ast
import datetime as dt
import difflib
import hashlib
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FROZEN = "1a037688c"
PKG = "src/crypto_autoresearcher/index_calculus"
NOTES = "experiments/EXP-PFDR-1b78f7/implementation-notes.yaml"

E1_FROZEN_SOURCE = [f"{PKG}/{n}" for n in ("factor_base.py", "tails.py", "decompose.py",
                                            "solver.py", "harvest.py")]
E2_FILE = f"{PKG}/curve.py"
E3_FILE = f"{PKG}/__main__.py"
E2_ALLOWED_CHANGED = {"generate_prime_order_curve_j0"}
E2_ALLOWED_ADDED = {"_j0_has_prime_order_twist"}
E3_ALLOWED_CHANGED = {"_instance_j0", "_census_instance", "_census_job", "cmd_census"}
# files whose diff is shown in source.diff but which are not engine files of E-1..E-4
DIFF_ONLY = ["tests/test_index_calculus_harvest.py",
             "experiments/EXP-PFDR-1b78f7/analyze_census.py"]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def frozen_bytes(rel: str) -> bytes:
    r = subprocess.run(["git", "show", f"{FROZEN}:{rel}"], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show {FROZEN}:{rel} failed: {r.stderr.decode()}")
    return r.stdout


def work_bytes(rel: str) -> bytes:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return fh.read()


def notes_pins() -> tuple[dict, dict]:
    notes = yaml.safe_load(open(os.path.join(REPO, NOTES)))["implementation_notes"]
    frozen_src = dict(notes["frozen_source_sha256"])
    unchanged = {}
    for k, v in notes["byte_unchanged_files"]["sha256"].items():
        rel = k if k.startswith(("src/", "tests/")) else f"{PKG}/{k}"
        unchanged[rel] = v
    return frozen_src, unchanged


# -- AST units -----------------------------------------------------------------------------------

def units(src: bytes) -> tuple[dict, list]:
    """{qualified name: ast.dump} per top-level function, class and method, and the
    ordered list of ast.dump of module-level statements that are not definitions."""
    tree = ast.parse(src)
    defs, other = {}, []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, ast.ClassDef):
            defs[node.name] = ast.dump(node, include_attributes=False)
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defs[f"{node.name}.{sub.name}"] = ast.dump(sub, include_attributes=False)
        else:
            other.append(ast.dump(node, include_attributes=False))
    return defs, other


def compare_units(fr: bytes, am: bytes) -> dict:
    dF, oF = units(fr)
    dA, oA = units(am)
    changed = sorted(k for k in dF.keys() & dA.keys() if dF[k] != dA[k])
    added = sorted(dA.keys() - dF.keys())
    removed = sorted(dF.keys() - dA.keys())
    sm = difflib.SequenceMatcher(a=oF, b=oA, autojunk=False)
    mod_ops = [(tag, i1, i2, j1, j2) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    added_module_stmts = []
    other_module_changes = []
    for tag, i1, i2, j1, j2 in mod_ops:
        if tag == "insert":
            added_module_stmts += oA[j1:j2]
        else:
            other_module_changes.append({"op": tag, "frozen": oF[i1:i2], "amended": oA[j1:j2]})
    return {"changed": changed, "added": added, "removed": removed,
            "module_statements_equal": oF == oA,
            "module_statements_added": added_module_stmts,
            "module_statements_other_changes": other_module_changes,
            "units_compared": len(dF.keys() & dA.keys())}


# -- references and the static call graph -----------------------------------------------------------

def module_name(rel: str) -> str:
    return os.path.splitext(os.path.basename(rel))[0]


class RefCollector(ast.NodeVisitor):
    """Name and Attribute references, plus the names bound by any `from .x import y`."""

    def __init__(self):
        self.names: set[str] = set()
        self.attrs: set[str] = set()
        self.imports: dict[str, tuple[str, str]] = {}

    def visit_Name(self, node):
        self.names.add(node.id)

    def visit_Attribute(self, node):
        self.attrs.add(node.attr)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level >= 1 and node.module:
            for a in node.names:
                self.imports[a.asname or a.name] = (node.module, a.name)


def graph(files: dict[str, bytes]):
    """Nodes 'module:qualname' for every top-level function, class and method of every
    engine module; edges by Name (resolved in-module or through relative imports, the
    module's and the function's own) and by Attribute (over-approximated: any function
    or method of any engine module with that name).  Referencing a class reaches its
    methods (over-approximation)."""
    nodes: dict[str, ast.AST] = {}
    by_short: dict[str, set[str]] = {}
    mod_imports: dict[str, dict] = {}
    top: dict[str, set[str]] = {}
    for rel, src in files.items():
        mod = module_name(rel)
        tree = ast.parse(src)
        rc = RefCollector()
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                rc.visit(node)
        mod_imports[mod] = rc.imports
        top[mod] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = f"{mod}:{node.name}"
                nodes[q] = node
                top[mod].add(node.name)
                by_short.setdefault(node.name, set()).add(q)
                if isinstance(node, ast.ClassDef):
                    for sub in node.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            qq = f"{mod}:{node.name}.{sub.name}"
                            nodes[qq] = sub
                            by_short.setdefault(sub.name, set()).add(qq)
    edges: dict[str, set[str]] = {}
    for q, node in nodes.items():
        mod = q.split(":")[0]
        rc = RefCollector()
        rc.visit(node)
        imps = dict(mod_imports[mod])
        imps.update(rc.imports)
        out = set()
        for n in rc.names:
            if n in imps:
                m2, n2 = imps[n]
                m2 = m2.split(".")[-1]
                if f"{m2}:{n2}" in nodes:
                    out.add(f"{m2}:{n2}")
            elif n in top[mod]:
                out.add(f"{mod}:{n}")
        for a in rc.attrs:
            out |= by_short.get(a, set())
        # a class reaches its methods
        if isinstance(node, ast.ClassDef):
            out |= {k for k in nodes if k.startswith(f"{q}.")}
        edges[q] = out
    # referencing a class reaches its methods
    for q in list(edges):
        extra = set()
        for t in edges[q]:
            if isinstance(nodes.get(t), ast.ClassDef):
                extra |= {k for k in nodes if k.startswith(f"{t}.")}
        edges[q] |= extra
    return nodes, edges, mod_imports


def references_to(files: dict[str, bytes], target_mod: str, target: str) -> list[str]:
    nodes, edges, _ = graph(files)
    return sorted(q for q, out in edges.items() if f"{target_mod}:{target}" in out)


def main_sweep_dispatch(src: bytes) -> tuple[list[int], set[str], set[str]]:
    """Statements of main() that belong to the sweep dispatch: every statement that
    references neither another subparser variable (s, g, c, z) nor another cmd_*."""
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    other_vars = {"s", "g", "c", "z"}
    other_cmds = {"cmd_solve", "cmd_engines", "cmd_census", "cmd_analyze"}
    lines, names, attrs = [], set(), set()
    for st in fn.body:
        rc = RefCollector()
        rc.visit(st)
        bound = {t.id for t in getattr(st, "targets", []) if isinstance(t, ast.Name)}
        if (rc.names | bound) & (other_vars | other_cmds):
            continue
        lines.append(st.lineno)
        names |= rc.names
        attrs |= rc.attrs
    return lines, names, attrs


def reachable(roots: set[str], edges: dict[str, set[str]]) -> set[str]:
    seen, stack = set(), list(roots)
    while stack:
        q = stack.pop()
        if q in seen:
            continue
        seen.add(q)
        stack.extend(edges.get(q, ()))
    return seen


def run() -> int:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    frozen_src_pins, unchanged_pins = notes_pins()
    report: dict = {"certificate": "AMD-20260929-1de84f C-2 build-equivalence (E-1..E-4)",
                    "frozen_commit": FROZEN,
                    "frozen_commit_full": subprocess.run(["git", "rev-parse", FROZEN], cwd=REPO,
                                                         capture_output=True, text=True).stdout.strip(),
                    "working_tree_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                                        capture_output=True, text=True).stdout.strip(),
                    "command": " ".join([sys.executable] + sys.argv),
                    "started_at": started,
                    "script_sha256": sha(open(os.path.abspath(__file__), "rb").read())}

    # frozen reference integrity: git show bytes == implementation-notes pins
    ref = {}
    for rel, pin in sorted(list(frozen_src_pins.items()) + list(unchanged_pins.items())):
        fb = frozen_bytes(rel)
        ref[rel] = {"pin": pin, "git_show_sha256": sha(fb), "equal": sha(fb) == pin}
    report["frozen_reference_integrity"] = {"pass": all(v["equal"] for v in ref.values()),
                                            "files": ref}

    # E-1
    e1 = {}
    for rel in E1_FROZEN_SOURCE:
        w = sha(work_bytes(rel))
        e1[rel] = {"pin": frozen_src_pins[rel], "amended_sha256": w, "identical": w == frozen_src_pins[rel]}
    for rel, pin in sorted(unchanged_pins.items()):
        w = sha(work_bytes(rel))
        e1[rel] = {"pin": pin, "amended_sha256": w, "identical": w == pin}
    # every results/ file present now must be pinned (no new or missing results file)
    res_now = sorted(f"{PKG}/results/{n}" for n in os.listdir(os.path.join(REPO, PKG, "results")))
    res_pinned = sorted(k for k in unchanged_pins if k.startswith(f"{PKG}/results/"))
    report["E-1"] = {"pass": all(v["identical"] for v in e1.values()) and res_now == res_pinned,
                     "files": e1, "results_files_present": res_now,
                     "results_files_pinned": res_pinned,
                     "results_file_set_equal": res_now == res_pinned}

    # E-2
    cF, cA = frozen_bytes(E2_FILE), work_bytes(E2_FILE)
    assert sha(cF) == frozen_src_pins[E2_FILE]
    c2 = compare_units(cF, cA)
    eng_files = {f"{PKG}/{n}": work_bytes(f"{PKG}/{n}") for n in sorted(os.listdir(os.path.join(REPO, PKG)))
                 if n.endswith(".py")}
    helper_refs = {h: references_to(eng_files, "curve", h) for h in c2["added"]}
    helpers_ok = all(set(v) <= {f"curve:{x}" for x in E2_ALLOWED_CHANGED | E2_ALLOWED_ADDED}
                     for v in helper_refs.values())
    e2_pass = (set(c2["changed"]) <= E2_ALLOWED_CHANGED and not c2["removed"]
               and set(c2["added"]) <= E2_ALLOWED_ADDED | set(helper_refs) and helpers_ok
               and c2["module_statements_equal"])
    report["E-2"] = {"pass": e2_pass, "file": E2_FILE, **c2,
                     "allowed_changed": sorted(E2_ALLOWED_CHANGED),
                     "allowed_added": sorted(E2_ALLOWED_ADDED),
                     "added_helpers_referenced_by": helper_refs,
                     "note": "module_statements_equal covers imports and module constants"}

    # E-3
    mF, mA = frozen_bytes(E3_FILE), work_bytes(E3_FILE)
    assert sha(mF) == frozen_src_pins[E3_FILE]
    c3 = compare_units(mF, mA)
    helper_refs3 = {h: references_to(eng_files, "__main__", h) for h in c3["added"]}
    allowed3 = {f"__main__:{x}" for x in E3_ALLOWED_CHANGED | set(c3["added"])}
    helpers3_ok = all(v and set(v) <= allowed3 for v in helper_refs3.values())
    # added module constants may only be referenced by the allowed functions
    const_ok = not c3["module_statements_other_changes"]
    added_const_names = []
    for d in c3["module_statements_added"]:
        added_const_names.append(d)
    const_ok = const_ok and not added_const_names  # none expected; any would need a reference check
    e3_pass = (set(c3["changed"]) <= E3_ALLOWED_CHANGED and not c3["removed"] and helpers3_ok
               and const_ok)
    report["E-3"] = {"pass": e3_pass, "file": E3_FILE, **c3,
                     "allowed_changed": sorted(E3_ALLOWED_CHANGED),
                     "added_helpers_referenced_by": helper_refs3}

    # E-4
    nodes, edges, _ = graph(eng_files)
    lines, names, attrs = main_sweep_dispatch(mA)
    roots = {"__main__:cmd_sweep"}
    top_main = {q.split(":")[1] for q in nodes if q.startswith("__main__:") and "." not in q.split(":")[1]}
    imps_main = graph(eng_files)[2]["__main__"]
    for n in names:
        if n in top_main and n != "main":
            roots.add(f"__main__:{n}")
        elif n in imps_main:
            m2, n2 = imps_main[n]
            if f"{m2.split('.')[-1]}:{n2}" in nodes:
                roots.add(f"{m2.split('.')[-1]}:{n2}")
    for a in attrs:
        for q in nodes:
            if q.split(":")[1].split(".")[-1] == a:
                roots.add(q)
    reach = reachable(roots, edges)
    changed_set = ({f"curve:{x}" for x in c2["changed"] + c2["added"]}
                   | {f"__main__:{x}" for x in c3["changed"] + c3["added"]})
    inter = sorted(reach & changed_set)
    # instrument control: from cmd_census the same graph must reach the changed functions
    ctrl = sorted(reachable({"__main__:cmd_census"}, edges) & changed_set)
    report["E-4_instrument_control"] = {
        "root": "__main__:cmd_census", "reached_changed_or_added": ctrl,
        "pass": set(ctrl) == changed_set,
        "note": "the graph is not vacuous: the census path reaches every changed or added unit"}
    report["E-4"] = {"pass": not inter and set(ctrl) == changed_set,
                     "graph": "ast Name and Attribute references over every engine module "
                              "(src/crypto_autoresearcher/index_calculus/*.py, amended build); Names "
                              "resolved in-module and through relative imports (module-level and "
                              "function-local); Attributes over-approximated to every function or "
                              "method of that name in any engine module; a class reaches its methods",
                     "roots": sorted(roots),
                     "main_sweep_dispatch_statement_lines": lines,
                     "sweep_reachable_set": sorted(reach),
                     "changed_or_added_set": sorted(changed_set),
                     "intersection": inter}

    # source.diff over every file named above
    diff_files = sorted(set(frozen_src_pins) | set(unchanged_pins)) + DIFF_ONLY
    chunks = []
    per_file = {}
    for rel in diff_files:
        fb, wb = frozen_bytes(rel), work_bytes(rel)
        per_file[rel] = {"frozen_sha256": sha(fb), "amended_sha256": sha(wb), "identical": fb == wb}
        if fb == wb:
            continue
        try:
            a, b = fb.decode().splitlines(keepends=True), wb.decode().splitlines(keepends=True)
        except UnicodeDecodeError:
            chunks.append(f"Binary files a/{rel} and b/{rel} differ\n")
            continue
        chunks.extend(difflib.unified_diff(a, b, fromfile=f"a/{rel} ({FROZEN})", tofile=f"b/{rel} (amended)"))
    with open(os.path.join(HERE, "source.diff"), "w") as fh:
        fh.write("".join(chunks))
    report["source_diff"] = {"path": "experiments/EXP-PFDR-1b78f7/amd-1de84f/source.diff",
                             "files": per_file,
                             "sha256": sha("".join(chunks).encode())}
    report["all_pass"] = all(report[k]["pass"] for k in ("E-1", "E-2", "E-3", "E-4")) \
        and report["frozen_reference_integrity"]["pass"]
    report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(os.path.join(HERE, "function-diff.json"), "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=False)
    print(json.dumps({k: (report[k]["pass"] if isinstance(report[k], dict) and "pass" in report[k] else None)
                      for k in ("frozen_reference_integrity", "E-1", "E-2", "E-3", "E-4")}
                     | {"all_pass": report["all_pass"],
                        "E-2_changed": c2["changed"], "E-2_added": c2["added"],
                        "E-3_changed": c3["changed"], "E-3_added": c3["added"],
                        "E-4_intersection": inter}, indent=2))
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
