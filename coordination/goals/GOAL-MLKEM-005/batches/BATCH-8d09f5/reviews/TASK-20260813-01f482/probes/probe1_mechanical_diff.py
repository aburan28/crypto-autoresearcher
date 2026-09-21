#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 1 -- TASK-20260813-01f482 / BATCH-8d09f5 / GOAL-MLKEM-005

Independent mechanical diff. Written from scratch by the Validator, NOT by
importing or reusing measure_hkz_mutation6.py's own build_mechanical_diff()
function -- this probe re-implements the extraction and diff logic
independently so the check does not depend on the producer's own diff code
being correct.

Extracts the 4 named functions from:
  (a) the FROZEN reference measure_hkz_indep.py, committed at
      3d3f5fde552f1a4783616a624f602917719701e8 (read via `git show`, not the
      working-tree copy, to bind to the exact committed bytes)
  (b) the mutant measure_hkz_mutation6.py (source-level function bodies via
      the `ast` module, exactly as the producer did, but independently coded)

Normalizes only the _mut suffix on function names / call sites (a purely
cosmetic rename), then does a line-level diff on the normalized bodies to
find every remaining functional difference.

Writes probe1_mechanical_diff_output.json in this same directory.
"""
import ast
import difflib
import hashlib
import json
import os
import re
import subprocess
from collections import OrderedDict

REPO_ROOT = "/home/user/crypto-autoresearcher"
FROZEN_COMMIT = "3d3f5fde552f1a4783616a624f602917719701e8"
FROZEN_PATH = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/"
               "tasks/TASK-20260813-c0ec71/measure_hkz_indep.py")
MUT_PATH = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/"
            "tasks/TASK-20260813-630414/measure_hkz_mutation6.py")

FROZEN_FUNC_NAMES = ["route_ii_make_A", "route_ii_build_basis",
                      "hkz_route_ii", "route_ii_hkz_value"]
MUT_FUNC_NAMES = ["route_ii_make_A_mut", "route_ii_build_basis_mut",
                  "hkz_route_ii_mut", "route_ii_hkz_value_mut"]


def git_show_bytes(commit, path):
    return subprocess.run(
        ["git", "show", "%s:%s" % (commit, path)],
        cwd=REPO_ROOT, capture_output=True, check=True).stdout


def extract_functions_from_text(src_text, names):
    tree = ast.parse(src_text)
    lines = src_text.splitlines(keepends=True)
    out = OrderedDict()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            start = node.lineno - 1
            end = node.end_lineno
            out[node.name] = "".join(lines[start:end])
    missing = [n for n in names if n not in out]
    if missing:
        raise SystemExit("ABORT: missing functions %r" % missing)
    return out


def normalize_mut_name(text):
    """Strip the cosmetic _mut suffix from function names / self-referential
    call sites so that a line-level diff isolates genuinely functional
    changes. This is the ONLY normalization performed."""
    out = text
    for fn in MUT_FUNC_NAMES:
        base = fn[:-len("_mut")]
        # word-boundary replace fn -> base
        out = re.sub(r"\b%s\b" % re.escape(fn), base, out)
    return out


def main():
    frozen_bytes = git_show_bytes(FROZEN_COMMIT, FROZEN_PATH)
    frozen_sha256 = hashlib.sha256(frozen_bytes).hexdigest()
    frozen_src = frozen_bytes.decode("utf-8")

    with open(os.path.join(REPO_ROOT, MUT_PATH), "r") as fh:
        mut_src = fh.read()
    mut_sha256 = hashlib.sha256(mut_src.encode("utf-8")).hexdigest()

    frozen_funcs = extract_functions_from_text(frozen_src, FROZEN_FUNC_NAMES)
    mut_funcs_raw = extract_functions_from_text(mut_src, MUT_FUNC_NAMES)

    # Normalize mut function bodies: strip _mut suffix from names/self-calls
    mut_funcs_normalized = OrderedDict(
        (name[:-len("_mut")], normalize_mut_name(body))
        for name, body in mut_funcs_raw.items()
    )

    per_function = OrderedDict()
    all_functional_diff_lines = []
    for fname in FROZEN_FUNC_NAMES:
        frozen_body = frozen_funcs[fname]
        # also normalize the def-line's own default-arg additions etc: we
        # do NOT strip anything else, so a genuinely different default
        # argument (e.g. n_bases=N_BASES) WILL show as a diff line, and is
        # reported explicitly below rather than silently normalized away.
        mut_body_norm = mut_funcs_normalized[fname]
        diff = list(difflib.unified_diff(
            frozen_body.splitlines(keepends=True),
            mut_body_norm.splitlines(keepends=True),
            fromfile="frozen/%s" % fname,
            tofile="mut-normalized/%s" % fname,
        ))
        added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
        removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
        per_function[fname] = {
            "diff": "".join(diff),
            "n_added": len(added),
            "n_removed": len(removed),
        }
        all_functional_diff_lines.extend(diff)

    # Count net functional change lines across all 4 functions (post
    # _mut-suffix normalization -- this normalization is name-only and does
    # NOT touch the def-line's added default argument `n_bases=N_BASES`,
    # which legitimately shows up as a diff and is reported here, named
    # explicitly, not silently discounted).
    total_added = sum(v["n_added"] for v in per_function.values())
    total_removed = sum(v["n_removed"] for v in per_function.values())

    out = {
        "frozen_reference_path": FROZEN_PATH,
        "frozen_reference_commit": FROZEN_COMMIT,
        "frozen_reference_sha256_via_git_show": frozen_sha256,
        "frozen_reference_sha256_matches_run_manifest_claim": (
            frozen_sha256 ==
            "74875b4197cee69dc78c2999f9f60f27b678da3159c6cdd0bbc7039a4fb09096"
        ),
        "mutant_path": MUT_PATH,
        "mutant_sha256_working_tree": mut_sha256,
        "per_function_diff": per_function,
        "total_added_lines_post_name_normalization": total_added,
        "total_removed_lines_post_name_normalization": total_removed,
    }
    out_path = os.path.join(
        REPO_ROOT,
        "coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/"
        "TASK-20260813-01f482/probes/probe1_mechanical_diff_output.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
    print("Wrote", out_path)
    print("total_added=%d total_removed=%d" % (total_added, total_removed))
    for fname, v in per_function.items():
        print("--- %s: +%d -%d ---" % (fname, v["n_added"], v["n_removed"]))
        print(v["diff"])


if __name__ == "__main__":
    main()
