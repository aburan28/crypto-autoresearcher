"""Static leak audit (source/leak_audit.py per specification.yaml's
planted_leak_check_of_the_audit control). Forbids the feature or model code
path from importing the label code path (enumerate_counts.py,
lookup_labels.py, certificates.py) or referencing a discrete-logarithm /
enumeration-index / node-order identifier by name.

This is a STATIC, AST-level audit: it never executes the scanned code.
"""
from __future__ import annotations

import ast
import os

FORBIDDEN_MODULES = {"enumerate_counts", "lookup_labels", "certificates"}
FORBIDDEN_NAME_SUBSTRINGS = [
    "discrete_log", "dlog", "log_p", "logp", "scalar_k", "the_scalar",
    "enumeration_index", "node_order", "node_index", "positional_index",
]


def _names_in_source(source: str):
    tree = ast.parse(source)
    imported_modules = set()
    referenced_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split(".")[0])
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.Name):
            referenced_names.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            referenced_names.add(node.attr.lower())
        elif isinstance(node, ast.FunctionDef):
            referenced_names.add(node.name.lower())
    return imported_modules, referenced_names


def audit_source_string(source: str, label: str) -> dict:
    violations = []
    try:
        imported, referenced = _names_in_source(source)
    except SyntaxError as e:
        return {"label": label, "verdict": "reject", "violations": [f"syntax_error: {e}"]}
    forbidden_imports_found = sorted(imported & FORBIDDEN_MODULES)
    if forbidden_imports_found:
        violations.append(f"forbidden_import: {forbidden_imports_found}")
    for name in referenced:
        for bad in FORBIDDEN_NAME_SUBSTRINGS:
            if bad in name:
                violations.append(f"forbidden_identifier: {name} (matches '{bad}')")
    verdict = "reject" if violations else "pass"
    return {"label": label, "verdict": verdict, "violations": violations}


def audit_file(path: str) -> dict:
    with open(path, "r") as f:
        source = f.read()
    return audit_source_string(source, os.path.basename(path))


def audit_all(source_dir: str) -> dict:
    targets = ["features.py", "model_gnn.py", "model_trees.py", "graph_build.py"]
    results = []
    for t in targets:
        p = os.path.join(source_dir, t)
        if os.path.exists(p):
            results.append(audit_file(p))
    overall = "pass" if all(r["verdict"] == "pass" for r in results) else "reject"
    return {"overall_verdict": overall, "per_file": results}


PLANTED_LEAK_SOURCE = '''
"""Deliberately-bad diagnostic feature module: adds log_P(R) mod 2 as a
feature via a call into the label code path. This file is NEVER imported by
the real pipeline; it exists only so leak_audit.py can prove the static
audit rejects it (specification.yaml's planted_leak_check_of_the_audit)."""
import numpy as np
from enumerate_counts import enumerate_count_vector_E  # forbidden: label code path
import lookup_labels  # forbidden: label code path


def discrete_log_lookup(R, P, curve):
    """Computes log_P(R) by brute force -- a discrete-log oracle, forbidden
    as a feature source under any name."""
    cur = None
    k = 0
    while True:
        if cur == R:
            return k
        cur = curve.add(cur, P) if cur is not None else P
        k += 1


def compute_features_E_planted(curve, targets, translate_points, regime, P, base_summary=None):
    rows = []
    for (x, y) in targets:
        leak_bit = discrete_log_lookup((x, y), P, curve) % 2
        rows.append([x / curve.p, y / curve.p, leak_bit])
    return np.array(rows, dtype=np.float64)
'''


def run_planted_leak_diagnostic() -> dict:
    result = audit_source_string(PLANTED_LEAK_SOURCE, "planted_leak_diagnostic_module")
    audit_rejected = result["verdict"] == "reject"
    return {
        "audit_verdict": result["verdict"],
        "violations": result["violations"],
        "audit_correctly_rejected_planted_leak": audit_rejected,
    }


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print(audit_all(here))
    print(run_planted_leak_diagnostic())
