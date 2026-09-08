#!/usr/bin/env python3
"""C3 amended static provenance check, RE-RECORDED before Stage 3 (amendment
v2 C3; required by the handoff: "the C3 amended provenance check is RE-
RECORDED passing, disclosed in the Stage 3 manifest").

The C3 amendment changes the SCANNER MECHANISM from a token-based scan (flag
any standalone 'k' in the function body -- unsound for local loop counters)
to an INPUT-based AST scan: flag a k-dependence only when the discrete-log
coordinate k enters the statistic code path as INPUT (a function parameter,
a global/module-level name, a closure capture, or an array element indexed by
a point's discrete-log coordinate).  A local loop counter named k is NOT a
flag.

The DICT is the V5-CHG-1 corrected one (the V3-CHG-2-renamed true functions
rudin_shapiro_sign_true / _array, not the retired signflip-variant names).

TWO SCANS ARE RECORDED:
  (A) TOKEN SCAN -- the prior mechanism, re-run for comparison/transparency.
  (B) AST SCAN -- the C3-amended operative check.
The AST scan is the operative check (all_pass is the AST scan's verdict).

The AST-scan logic is reused from the pre-existing (untracked, read-only
reference) implementation/provenance_check.py, with the dict corrected for
the V3-CHG-2 rename.  This reuse is disclosed.

Run (from the experiment root):
    PYTHONPATH=implementation python3 implementation/c3_provenance_rerecord.py
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")

# The V5-CHG-1 corrected dict (V3-CHG-2-renamed true functions).
STATISTIC_FUNCTIONS = {
    "T1/T2 (thue_morse_sign)": "thue_morse_sign",
    "T1/T2 (thue_morse_sign_array)": "thue_morse_sign_array",
    "T3 (rudin_shapiro_sign_true)": "rudin_shapiro_sign_true",
    "T3 (rudin_shapiro_sign_true_array)": "rudin_shapiro_sign_true_array",
    "T4 (popcount_mod4)": "popcount_mod4",
    "T4 (popcount_mod4_array)": "popcount_mod4_array",
    "COMPARATOR (top_bit_fiber)": "top_bit_fiber",
    "COMPARATOR (top_bit_fiber_array)": "top_bit_fiber_array",
}


def _token_scan(src: str, func_name: str) -> dict:
    """The prior token-based scan (unsound for local names); re-run for
    comparison/transparency only."""
    sig = f"def {func_name}("
    idx = src.find(sig)
    if idx < 0:
        return {"found": False, "reads_k": None, "pass": False}
    next_def = src.find("\ndef ", idx + 1)
    body = src[idx:next_def if next_def > 0 else len(src)]
    code_lines = [ln for ln in body.split('\n')
                  if ln.strip() and not ln.strip().startswith('#')
                  and not ln.strip().startswith('"')
                  and not ln.strip().startswith("'")]
    k_refs = re.findall(r'\bk\b', '\n'.join(code_lines))
    reads_k = len(k_refs) > 0
    return {"found": True, "reads_k": reads_k,
            "k_refs_in_code": k_refs, "pass": not reads_k}


def _ast_scan(tree: ast.Module, func_name: str) -> dict:
    """The C3-amended AST scan: flag a k-dependence only when the discrete-log
    coordinate k enters the statistic code path as INPUT (parameter, global,
    closure, or DL-coordinate array index).  A local loop counter named k is
    NOT a flag.  (Logic reused from implementation/provenance_check.py.)"""
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func = node
            break
    if func is None:
        return {"found": False, "reads_k": None, "pass": False,
                "reason": "function not found"}
    params = set()
    a = func.args
    for arg in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs):
        params.add(arg.arg)
    if a.vararg:
        params.add(a.vararg.arg)
    if a.kwarg:
        params.add(a.kwarg.arg)
    local_assigned = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            local_assigned.add(node.id)
    referenced = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            referenced.add(node.id)
    k_is_param = "k" in params
    k_is_referenced = "k" in referenced
    k_is_local = "k" in local_assigned
    k_as_input = k_is_param or (k_is_referenced and not k_is_local)
    k_indexed = False
    for node in ast.walk(func):
        if isinstance(node, ast.Subscript):
            sl = node.slice
            if isinstance(sl, ast.Name) and sl.id == "k" and not k_is_local:
                k_indexed = True
    reads_k = k_as_input or k_indexed
    return {
        "found": True,
        "params": sorted(params),
        "k_is_parameter": k_is_param,
        "k_is_referenced": k_is_referenced,
        "k_is_local_variable": k_is_local,
        "k_as_input": k_as_input,
        "k_indexed_by_dl_coordinate": k_indexed,
        "reads_k": reads_k,
        "pass": not reads_k,
        "reason": (
            "k is a local loop counter (bit-length), not the discrete-log "
            "coordinate; the function is a pure function of its parameters"
            if (k_is_referenced and k_is_local and not k_is_param)
            else ("k enters the code path as input" if reads_k
                  else "k is not referenced")),
    }


def main() -> None:
    src_path = Path(__file__).resolve().parent / "estimator.py"
    src = src_path.read_text()
    tree = ast.parse(src)
    out = {
        "check": ("C3 amended static provenance check (no T1-T4 or COMPARATOR "
                  "statistic code path reads the discrete-log coordinate k), "
                  "RE-RECORDED before Stage 3"),
        "scanner_change_disclosed": ("C3 (amendment v2) changes the scanner "
                                     "from a token-based scan (flag any "
                                     "standalone 'k') to an INPUT-based AST "
                                     "scan (flag k only as an input: "
                                     "parameter, global, closure, or DL-"
                                     "coordinate array index).  The AST scan "
                                     "is the operative check.  The dict is "
                                     "the V5-CHG-1 corrected one (V3-CHG-2-"
                                     "renamed true functions)."),
        "scope": ("T1-T4 and COMPARATOR statistic functions only; POS-A, "
                  "POS-B and NULL-1 read k / harness data BY DESIGN and are "
                  "exempt"),
        "source_file": str(src_path),
        "token_scan": {},
        "ast_scan": {},
    }
    token_all_pass = True
    ast_all_pass = True
    for label, func_name in STATISTIC_FUNCTIONS.items():
        t = _token_scan(src, func_name)
        a = _ast_scan(tree, func_name)
        out["token_scan"][label] = t
        out["ast_scan"][label] = a
        if not t["pass"]:
            token_all_pass = False
        if not a["pass"]:
            ast_all_pass = False
    out["token_scan_all_pass"] = token_all_pass
    out["ast_scan_all_pass"] = ast_all_pass
    out["all_pass"] = ast_all_pass  # the operative check is the AST scan
    out_path = (Path(__file__).resolve().parent.parent / "runs" /
                "C3-provenance-rerecord-20260908.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"token_scan_all_pass": token_all_pass,
                      "ast_scan_all_pass": ast_all_pass,
                      "all_pass": ast_all_pass,
                      "written_to": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()
