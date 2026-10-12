"""AST import / execution audit for EXP-BINSTD-178742 typed/ tree.

Stdlib only. Every .py under typed/ must import only:
  (a) the Python standard library, or
  (c) another module under this typed/ directory.

No third-party distributions are admitted for packaging. Forbidden:
  exec/eval/compile/__import__; importlib except importlib.metadata; runpy.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

TYPED_DIR = Path(__file__).resolve().parent

FORBIDDEN_CALLS = frozenset({"exec", "eval", "compile", "__import__"})
FORBIDDEN_MODULES = frozenset({"runpy"})


def _stdlib_names() -> Set[str]:
    names = set(getattr(sys, "stdlib_module_names", ()))
    names.update(
        {
            "abc",
            "argparse",
            "ast",
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
    if root in local:
        return "c_typed_local"
    if root == "importlib":
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

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                cls = classify_import(mod, stdlib, local)
                imports.append({"module": mod, "class": cls})
                if cls.startswith("forbidden"):
                    problems.append(f"forbidden import {mod}")
                if mod in FORBIDDEN_MODULES or _root_name(mod) in FORBIDDEN_MODULES:
                    problems.append(f"forbidden module {mod}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.level and not mod:
                cls = "c_typed_local"
                imports.append({"module": f".{node.level}", "class": cls})
            else:
                cls = classify_import(mod, stdlib, local) if mod else "c_typed_local"
                imports.append({"module": mod or ".", "class": cls})
                if cls.startswith("forbidden"):
                    problems.append(f"forbidden import from {mod}")
                if _root_name(mod) in FORBIDDEN_MODULES:
                    problems.append(f"forbidden module {mod}")
                if mod == "importlib" or (
                    mod.startswith("importlib.")
                    and not mod.startswith("importlib.metadata")
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
        "path": str(path),
        "file": path.name,
        "stdlib_only_required": True,
        "imports": imports,
        "problems": problems,
        "ok": len(problems) == 0,
    }


def audit_tree(root: Path = TYPED_DIR) -> Dict[str, Any]:
    results = []
    ok = True
    for path in sorted(root.glob("*.py")):
        r = audit_file(path)
        try:
            repo = root.parents[3]
            r["path"] = str(path.relative_to(repo))
        except Exception:
            r["path"] = str(path)
        results.append(r)
        if not r["ok"]:
            ok = False
    return {"ok": ok, "files": results, "typed_dir": str(root)}
