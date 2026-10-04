"""J1(f) C-2: my own ast.dump comparison of curve.py and __main__.py between the frozen
build (git show 1a037688c:<path>) and a32e70808, per top-level function/class/method and
of the ordered module-level non-def statements; my own static call graph from cmd_sweep
(and main's sweep dispatch) over ast Name/Attribute references, transitively; E-1 by
hashes (frozen files vs 1a037688c; byte-unchanged files vs implementation-notes pins).
Compared against amd-1de84f/function-diff.json's E-2..E-4 claims. Imports no engine module
(sources are parsed, never executed)."""
import ast, hashlib, json, os, subprocess, sys
import yaml
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
FROZEN = "1a037688c"
PKG = "src/crypto_autoresearcher/index_calculus"


def git_show(rev, path):
    rl.log(os.path.join(WT, path), f"J1(f) C-2: git show {rev}:{path} (object read, no checkout)")
    return subprocess.run(["git", "-C", WT, "--no-optional-locks", "show", f"{rev}:{path}"], capture_output=True, check=True).stdout


def units(src):
    """{qualified name: ast.dump} for top-level functions/classes and methods; plus the
    ordered list of module-level non-def statements."""
    tree = ast.parse(src)
    out, mod = {}, []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, ast.ClassDef):
            out[node.name] = ast.dump(ast.ClassDef(name=node.name, bases=node.bases, keywords=node.keywords,
                                                  body=[b for b in node.body if not isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))],
                                                  decorator_list=node.decorator_list), include_attributes=False)
            for b in node.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out[f"{node.name}.{b.name}"] = ast.dump(b, include_attributes=False)
        else:
            mod.append(ast.dump(node, include_attributes=False))
    return out, mod, tree


def diff_units(a, b):
    changed = sorted(k for k in a if k in b and a[k] != b[k])
    added = sorted(k for k in b if k not in a)
    removed = sorted(k for k in a if k not in b)
    return changed, added, removed


def refs(node):
    s = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            s.add(n.id)
        elif isinstance(n, ast.Attribute):
            s.add(n.attr)
    return s


def call_graph_reach(tree, roots):
    defs = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs[node.name] = node
        elif isinstance(node, ast.ClassDef):
            defs[node.name] = node
    seen, stack = set(), list(roots)
    while stack:
        f = stack.pop()
        if f in seen or f not in defs:
            continue
        seen.add(f)
        for r in refs(defs[f]):
            if r in defs and r not in seen:
                stack.append(r)
    return seen


def main():
    out = {}
    fd = json.load(open(rl.opened(os.path.join(WT, "experiments/EXP-PFDR-1b78f7/amd-1de84f/function-diff.json"), "J1(f) C-2: producer function-diff.json (after seal)")))
    out["function_diff_json_top_keys"] = sorted(fd.keys())
    for fn in ["curve.py", "__main__.py"]:
        a_src = git_show(FROZEN, f"{PKG}/{fn}")
        b_path = os.path.join(WT, PKG, fn)
        b_src = open(rl.opened(b_path, "J1(f) C-2: amended source parsed (ast)"), "rb").read()
        ua, ma, ta = units(a_src)
        ub, mb, tb = units(b_src)
        ch, ad, rm = diff_units(ua, ub)
        out[fn] = {"changed": ch, "added": ad, "removed": rm, "module_level_statements_equal": ma == mb,
                   "module_level_added": [s[:160] for s in mb if s not in ma],
                   "module_level_removed": [s[:160] for s in ma if s not in mb],
                   "frozen_sha256": hashlib.sha256(a_src).hexdigest(), "amended_sha256": hashlib.sha256(b_src).hexdigest()}
        if fn == "__main__.py":
            # sweep reachability: from cmd_sweep and main (main dispatches sweep); in the amended file
            reach = call_graph_reach(tb, ["cmd_sweep"])
            reach_main = call_graph_reach(tb, ["main"])
            out[fn]["sweep_reachable_from_cmd_sweep"] = sorted(reach)
            out[fn]["reachable_from_main"] = sorted(reach_main)
            out[fn]["intersection_cmd_sweep_with_changed_or_added"] = sorted(reach & set(ch + ad))
    # curve.py changes reachable from __main__'s cmd_sweep? names referenced transitively
    tb_main = ast.parse(open(os.path.join(WT, PKG, "__main__.py"), "rb").read())
    reach = call_graph_reach(tb_main, ["cmd_sweep"])
    names_used = set()
    defs = {n.name: n for n in tb_main.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for f in reach:
        names_used |= refs(defs[f])
    out["curve.py"]["changed_or_added_names_referenced_by_sweep_reachable_main_functions"] = sorted(
        names_used & set(out["curve.py"]["changed"] + out["curve.py"]["added"]))
    # E-1 hashes
    notes = yaml.safe_load(open(rl.opened(os.path.join(WT, "experiments/EXP-PFDR-1b78f7/implementation-notes.yaml"), "J1(f) E-1: implementation-notes pins (after seal)")))
    out["implementation_notes_keys"] = sorted(notes.keys()) if isinstance(notes, dict) else None
    e1 = {}
    for f in ["factor_base.py", "tails.py", "decompose.py", "solver.py", "harvest.py", "linalg.py", "_accel.py",
              "rho.py", "semaev.py", "msolve.py", "polyfp.py", "stats.py", "README.md", "__init__.py"]:
        a = hashlib.sha256(git_show(FROZEN, f"{PKG}/{f}")).hexdigest()
        b = hashlib.sha256(open(os.path.join(WT, PKG, f), "rb").read()).hexdigest()
        e1[f] = {"frozen_1a037688c": a, "a32e70808": b, "equal": a == b}
    for f in ["tests/test_index_calculus_fp.py"]:
        a = hashlib.sha256(git_show(FROZEN, f)).hexdigest()
        b = hashlib.sha256(open(os.path.join(WT, f), "rb").read()).hexdigest()
        e1[f] = {"frozen_1a037688c": a, "a32e70808": b, "equal": a == b}
    res_dir = os.path.join(WT, PKG, "results")
    for f in sorted(os.listdir(res_dir)):
        a = hashlib.sha256(git_show(FROZEN, f"{PKG}/results/{f}")).hexdigest()
        b = hashlib.sha256(open(os.path.join(res_dir, f), "rb").read()).hexdigest()
        e1[f"results/{f}"] = {"frozen_1a037688c": a, "a32e70808": b, "equal": a == b}
    out["E1"] = e1
    # the producer's claims, for side-by-side
    out["function_diff_json_claims"] = {k: (v if len(json.dumps(v)) < 1500 else f"<{len(json.dumps(v))} chars>") for k, v in fd.items()}
    with open(os.path.join(W, "checks", "out", "j1f-c2-ast.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for fn in ["curve.py", "__main__.py"]:
        print(fn, {k: v for k, v in out[fn].items() if k not in ("reachable_from_main", "sweep_reachable_from_cmd_sweep")})
    print("E1 all equal:", all(v["equal"] for v in e1.values()), [k for k, v in e1.items() if not v["equal"]])
    print("function-diff.json keys:", out["function_diff_json_top_keys"])


if __name__ == "__main__":
    main()
