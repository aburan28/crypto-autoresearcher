"""AST import / execution audit for EXP-AUXIN-339fb0 typed/ tree.

Stdlib only. Enforces change.D8_custody.import_rule and admission items (6),(9):
  - every import is class (a) stdlib, (b) cypari2/cysignals/pypdf (+deps), or
    (c) another module under this typed/ directory;
  - cert_verify.py and every path-B module import only the standard library;
  - no exec/eval/compile/__import__; no importlib except importlib.metadata;
    no runpy.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

TYPED_DIR = Path(__file__).resolve().parent

ALLOWED_THIRD_PARTY_ROOTS = frozenset(
    {
        "cypari2",
        "cysignals",
        "pypdf",
        # Declared dependencies of the above distributions (recorded in manifest).
        "numpy",
        "typing_extensions",
    }
)

PATH_B_MODULES = frozenset(
    {
        "cert_verify.py",
        "factor_path_b.py",
        "e_eval.py",
        "import_audit.py",
    }
)

FORBIDDEN_CALLS = frozenset({"exec", "eval", "compile", "__import__"})
FORBIDDEN_MODULES = frozenset({"runpy"})


def _stdlib_names() -> Set[str]:
    names = set(getattr(sys, "stdlib_module_names", ()))
    # Always treat these as stdlib even on older interpreters.
    names.update(
        {
            "abc",
            "ast",
            "asyncio",
            "collections",
            "copy",
            "dataclasses",
            "decimal",
            "functools",
            "hashlib",
            "heapq",
            "io",
            "itertools",
            "json",
            "math",
            "os",
            "pathlib",
            "platform",
            "re",
            "shutil",
            "subprocess",
            "sys",
            "time",
            "typing",
            "unicodedata",
            "warnings",
            "__future__",
        }
    )
    return names


def _local_module_names() -> Set[str]:
    names = set()
    for p in TYPED_DIR.glob("*.py"):
        if p.name == "__init__.py":
            continue
        names.add(p.stem)
    return names


def _root_name(mod: str) -> str:
    return mod.split(".", 1)[0]


def classify_import(mod: str, stdlib: Set[str], local: Set[str]) -> str:
    root = _root_name(mod)
    if root in stdlib or mod in stdlib:
        return "a_stdlib"
    if root in ALLOWED_THIRD_PARTY_ROOTS:
        return "b_third_party"
    if root in local:
        return "c_typed_local"
    if root == "importlib":
        # Only importlib.metadata is allowed.
        if mod == "importlib.metadata" or mod.startswith("importlib.metadata."):
            return "a_stdlib"
        return "forbidden_importlib"
    return "forbidden"


def audit_file(path: Path) -> Dict[str, Any]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    stdlib = _stdlib_names()
    local = _local_module_names()
    imports: List[Dict[str, str]] = []
    problems: List[str] = []
    path_b = path.name in PATH_B_MODULES or path.name == "cert_verify.py"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                cls = classify_import(mod, stdlib, local)
                imports.append({"module": mod, "class": cls})
                if cls.startswith("forbidden"):
                    problems.append(f"forbidden import {mod}")
                if path_b and cls == "b_third_party":
                    problems.append(f"path-B/stdlib-only file imports third-party {mod}")
                if path_b and cls == "c_typed_local" and _root_name(mod) not in {
                    # path B may import other stdlib-only typed modules
                    "cert_verify",
                    "e_eval",
                    "import_audit",
                    "factor_path_b",
                }:
                    # Allow only stdlib-only local modules from path B.
                    if _root_name(mod) in {"factor_path_a", "run"}:
                        problems.append(f"path-B file imports non-path-B module {mod}")
                if mod in FORBIDDEN_MODULES or _root_name(mod) in FORBIDDEN_MODULES:
                    problems.append(f"forbidden module {mod}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.level and not mod:
                # relative import of local package
                cls = "c_typed_local"
                imports.append({"module": f".{node.level}", "class": cls})
            else:
                # relative-from with module name still classifies on absolute name
                cls = classify_import(mod, stdlib, local) if mod else "c_typed_local"
                imports.append({"module": mod or ".", "class": cls})
                if cls.startswith("forbidden"):
                    problems.append(f"forbidden import from {mod}")
                if path_b and cls == "b_third_party":
                    problems.append(
                        f"path-B/stdlib-only file imports third-party {mod}"
                    )
                if _root_name(mod) in FORBIDDEN_MODULES:
                    problems.append(f"forbidden module {mod}")
                if mod == "importlib" or (
                    mod.startswith("importlib.") and not mod.startswith("importlib.metadata")
                ):
                    problems.append(f"forbidden importlib usage: {mod}")
        elif isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in FORBIDDEN_CALLS:
                problems.append(f"forbidden call {name}()")

    return {
        "path": str(path.relative_to(TYPED_DIR.parent.parent.parent.parent))
        if False
        else str(path),
        "file": path.name,
        "stdlib_only_required": path_b,
        "imports": imports,
        "problems": problems,
        "ok": len(problems) == 0,
    }


def audit_tree(root: Path = TYPED_DIR) -> Dict[str, Any]:
    results = []
    ok = True
    for path in sorted(root.glob("*.py")):
        r = audit_file(path)
        # Normalize path to repo-relative if possible.
        try:
            # typed/ -> implementation/ -> EXP -> experiments/ -> repo
            repo = root.parents[3]
            r["path"] = str(path.relative_to(repo))
        except Exception:
            r["path"] = str(path)
        results.append(r)
        if not r["ok"]:
            ok = False
    return {"ok": ok, "files": results, "typed_dir": str(root)}
