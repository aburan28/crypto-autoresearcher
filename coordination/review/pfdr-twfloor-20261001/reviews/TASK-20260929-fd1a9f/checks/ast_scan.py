"""AST import scan of the disjoint checker modules (VF-3)."""
import ast, json, sys, hashlib
out = {}
for path in sys.argv[2:]:
    src = open(path).read()
    tree = ast.parse(src)
    imps = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imps += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imps.append(("." * node.level) + (node.module or ""))
    calls = sorted({n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("__import__", "exec", "eval", "compile")})
    bad = [i for i in imps if i.split(".")[0] not in ("json", "math", "random", "sys", "os", "__future__", "ec_check", "gzip", "collections", "hashlib")]
    out[path] = {"sha256": hashlib.sha256(src.encode()).hexdigest(), "imports": sorted(set(imps)),
                 "dynamic_import_or_exec_calls": calls,
                 "imports_outside_stdlib_allowlist": bad,
                 "mentions_crypto_autoresearcher": "crypto_autoresearcher" in src.replace("Imports NOTHING from crypto_autoresearcher", ""),
                 "verdict": "disjoint" if not bad and not calls else "NOT disjoint"}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
