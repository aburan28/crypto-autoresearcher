#!/usr/bin/env python3
"""PROBE R (red team, TASK-20260809-444fe7) -- WHAT IS THE DIGIT-FOR-DIGIT
CROSS-PLATFORM AGREEMENT ACTUALLY EVIDENCE OF?

NOT PRE-REGISTERED. Rescores NO frozen verdict. CLAIM TIER TOY.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out probe_replication_output.json

WHAT IT ATTACKS
---------------
report_relvar.md section 5(i) reports "AGREEMENT to every reported digit,
reproduced on a different operating system, a different CPU architecture, a
different Python and a different numpy from the reviewer's (section 8). This
is the strongest replication in this section and it is a measurement of ours,
not an inheritance of theirs."

Two separate questions, which the phrase "agreement to every reported digit"
merges:

  (R1) HOW STRONG IS THE AGREEMENT? The producer's table compares 3 to 5
       significant figures because that is the precision the predecessor's
       report PRINTED. The predecessor's committed probe output
       (probe_A2_rel2_replication.out.txt) carries the per-basis hkz values to
       6 decimals, 48 numbers rather than 7. This block compares all of them.
       If they agree the claim is stronger than the report states; if they do
       not, the report's agreement is an artifact of the quoted precision.

  (R2) IS IT AN INDEPENDENT REPRODUCTION, OR A PORTABILITY CHECK? A
       reproduction that re-executes the SAME algorithm on the SAME seeds
       tests the platform, not the method: a systematic error in the shared
       code path reproduces exactly. This block compares the two files'
       hkz_profile / basis-construction source, normalized for whitespace and
       comments, and reports how much of the pipeline is textually shared.

MY OWN CHECK'S COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE RUNNING, BOTH WAYS
---------------------------------------------------------------------------
* could-not-FIRE: if the predecessor's committed output did not carry more
  digits than its report quoted, R1 could not add anything. It does carry 6
  decimals -- so the arrangement is live and the comparison is real.
* could-not-PASS: I could manufacture "shared code" by comparing whole files,
  which share a task template. Guarded by comparing NAMED FUNCTIONS only
  (make_A, build_basis, hkz_profile) after stripping comments, docstrings and
  whitespace, and by reporting the per-function verdict separately rather than
  a single similarity score.

AM-10 / AM-11 ON THIS PROBE'S OWN STATISTICS
--------------------------------------------
The agreement statistic is reported per basis index i = 0..7 and per beta
(AM-10 replication across all 8 frozen bases, not at i = 0) and with the
max / median absolute deviation across them (AM-11 dispersion), never as a
single pass/fail.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
from collections import OrderedDict

import numpy as np

PRED_OUT = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/"
            "TASK-20260808-6de788/probes/probe_A2_rel2_replication.out.txt")
PRED_PY = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/"
           "TASK-20260808-6de788/probes/probe_A2_rel2_replication.py")
PROD_JSON = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
             "TASK-20260809-cda2f6/results_relvar.json")
PROD_PY = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
           "TASK-20260809-cda2f6/measure_relvar.py")
ANCESTOR_PY = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
               "TASK-20260808-2a9085/measure_am4.py")


def read(path, rev="HEAD"):
    if os.path.exists(path):
        return open(path, "rb").read()
    return subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                          capture_output=True, check=True).stdout


def norm_func(src_bytes, name):
    """Return a whitespace/comment/docstring-normalized token stream for the
    named top-level function, or None."""
    tree = ast.parse(src_bytes.decode())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            body = list(node.body)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                body = body[1:]              # strip the docstring
            stripped = ast.Module(body=body, type_ignores=[])
            return ast.dump(stripped, annotate_fields=False)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="probe_replication_output.json")
    args = ap.parse_args()

    OUT = OrderedDict()
    OUT["probe"] = "PROBE-R"
    OUT["task_id"] = "TASK-20260809-444fe7"
    OUT["claim_tier"] = "toy"
    OUT["status_of_this_measurement"] = (
        "RED-TEAM PROBE. NOT PRE-REGISTERED. Compares two committed artifacts; "
        "re-measures nothing and rescores nothing.")

    print("=" * 78)
    print("PROBE R -- what is the cross-platform agreement evidence of?")
    print("RED-TEAM PROBE, NOT PRE-REGISTERED, RESCORES NOTHING. TOY.")
    print("=" * 78)

    # ------------------------------------------------------------ R1
    pred_txt = read(PRED_OUT).decode()
    pred = {}
    beta = None
    for line in pred_txt.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+"
                     r"(\d+\.\d+)\s+(\d+\.\d+)", line)
        if m:
            b, i, h6, h14 = int(m.group(1)), int(m.group(2)), float(
                m.group(3)), float(m.group(4))
            pred[(b, i)] = {"k6": h6, "k14": h14}
    prod = json.loads(read(PROD_JSON).decode())
    rows = []
    for (b, i), pv in sorted(pred.items()):
        ent = prod["G_REL2"]["hkz"]["L7/L8"].get(str(b))
        if not ent or "per_basis" not in ent:
            continue
        e = ent["per_basis"][i]
        # X_a is the k = 6 side (L7), X_b the k = 14 side (L8)
        rows.append({
            "beta": b, "basis_i": i,
            "predecessor_k6": pv["k6"], "producer_k6": e["X_a"],
            "predecessor_k14": pv["k14"], "producer_k14": e["X_b"],
            "abs_dev_k6": abs(pv["k6"] - e["X_a"]),
            "abs_dev_k14": abs(pv["k14"] - e["X_b"]),
            "agree_at_6dp": bool(round(e["X_a"], 6) == pv["k6"]
                                 and round(e["X_b"], 6) == pv["k14"]),
        })
    devs = [r["abs_dev_k6"] for r in rows] + [r["abs_dev_k14"] for r in rows]
    OUT["R1_digit_for_digit"] = {
        "n_values_compared": len(devs),
        "n_pairs_agreeing_at_6_decimals": sum(1 for r in rows if r["agree_at_6dp"]),
        "n_pairs": len(rows),
        "max_abs_deviation": float(np.max(devs)) if devs else None,
        "median_abs_deviation": float(np.median(devs)) if devs else None,
        "precision_of_the_predecessor_record": "6 decimals (its committed .out.txt)",
        "precision_quoted_in_report_relvar_section_5(i)": "3 to 5 significant figures",
        "reading": (
            "The producer's own table compares at the precision its source "
            "PRINTED. This block compares at the precision its source "
            "COMMITTED. Whichever way it comes out, the claim's strength is "
            "bounded by the digits actually compared, and this block states "
            "how many that is."),
        "per_entry": rows,
    }
    print("\n[R1] compared %d committed values across 3 betas x 8 bases x 2 sides"
          % len(devs))
    print("     agree at 6 decimals: %d of %d pairs; max abs deviation %.3e"
          % (OUT["R1_digit_for_digit"]["n_pairs_agreeing_at_6_decimals"],
             len(rows), OUT["R1_digit_for_digit"]["max_abs_deviation"]))

    # ------------------------------------------------------------ R2
    pred_py, prod_py = read(PRED_PY), read(PROD_PY)
    # The two files name the same steps differently; the map is stated
    # explicitly so the comparison is not silently defeated by a rename.
    NAME_MAP = [("basis", "build_basis"), ("hkz_profile", "hkz_profile"),
                ("hkz_at", "x_rawtail_of"), ("make_A", "make_A")]
    fns = OrderedDict()
    for pname, qname in NAME_MAP:
        a, b = norm_func(pred_py, pname), norm_func(prod_py, qname)
        # a coarse structural measure that survives renaming of locals
        sim = None
        if a is not None and b is not None:
            ta = re.findall(r"[A-Za-z_]+", a)
            tb = re.findall(r"[A-Za-z_]+", b)
            sa, sb = set(ta), set(tb)
            sim = len(sa & sb) / len(sa | sb) if (sa | sb) else None
        fns["%s~%s" % (pname, qname)] = {
            "in_predecessor_probe": a is not None,
            "in_producer_script": b is not None,
            "AST_IDENTICAL_after_stripping_comments_and_docstrings":
                bool(a is not None and b is not None and a == b),
            "jaccard_of_identifier_sets": sim,
            "predecessor_ast_sha256": hashlib.sha256(a.encode()).hexdigest()[:16] if a else None,
            "producer_ast_sha256": hashlib.sha256(b.encode()).hexdigest()[:16] if b else None,
        }
    # Both files describe their pipeline as "CARRIED VERBATIM from
    # BATCH-cbe023 measure_am4.py". The sharper question is therefore not
    # whether they copy each other but whether either copies the ANCESTOR.
    anc_py = read(ANCESTOR_PY)
    anc = OrderedDict()
    for name in ["hkz_profile", "make_A", "build_basis", "gram_int"]:
        a = norm_func(anc_py, name)
        p = norm_func(pred_py, name) or norm_func(pred_py, "basis" if
                                                  name == "build_basis" else name)
        q = norm_func(prod_py, name)
        anc[name] = {
            "in_ancestor": a is not None,
            "ancestor_IDENTICAL_to_predecessor_probe":
                bool(a is not None and p is not None and a == p),
            "ancestor_IDENTICAL_to_producer_script":
                bool(a is not None and q is not None and a == q),
        }
    OUT["R2b_comparison_against_the_declared_common_ancestor"] = {
        "ancestor": ANCESTOR_PY,
        "per_function": anc,
        "reading": (
            "Both scripts label the pipeline CARRIED VERBATIM. If no function "
            "is AST-identical to the ancestor, 'carried verbatim' is a "
            "SEMANTIC carry re-implemented independently, which makes the "
            "cross-platform agreement a stronger result than a shared-text "
            "reproduction would be. What it still cannot rule out is an error "
            "in the shared SPECIFICATION or in the exactly-matched fpylll "
            "0.6.4, which both runs depend on identically."),
    }

    shared = [k for k, v in fns.items()
              if v["AST_IDENTICAL_after_stripping_comments_and_docstrings"]]
    OUT["R2_shared_code_path"] = {
        "functions_checked": fns,
        "functions_AST_identical_in_both": shared,
        "n_identical": len(shared),
        "seeds_shared": (
            "make_A uses numpy.random.default_rng([1, d, k, i]), a "
            "platform-independent PCG64 seed sequence, and the basis is built "
            "in exact int64 arithmetic. So the INPUT to the reduction is "
            "bit-identical across platforms by construction, not by "
            "agreement."),
        "reading": (
            "Functions that are AST-identical in both files are a SHARED CODE "
            "PATH. Agreement across them measures portability of that path -- "
            "which is a real result and rules out a platform-dependent float "
            "artifact in the HKZ profile at these cells -- but it cannot "
            "detect an error that is IN the shared path, and it is not method "
            "independence."),
    }
    print("\n[R2] AST-identical functions in both files: %s" % (shared or "none"))

    OUT["HEADLINE"] = {
        "agreement_at_6_decimals": "%d of %d pairs" % (
            OUT["R1_digit_for_digit"]["n_pairs_agreeing_at_6_decimals"], len(rows)),
        "max_abs_deviation": OUT["R1_digit_for_digit"]["max_abs_deviation"],
        "n_shared_functions": len(shared),
        "n_functions_identical_to_the_declared_common_ancestor": sum(
            1 for v in anc.values()
            if v["ancestor_IDENTICAL_to_predecessor_probe"]
            or v["ancestor_IDENTICAL_to_producer_script"]),
        "what_the_agreement_is_evidence_of": (
            "cross-platform PORTABILITY of a shared code path on shared seeds; "
            "NOT method independence, and NOT a check that could have caught "
            "an error inside the shared path"),
    }
    with open(args.out, "w") as fh:
        json.dump(OUT, fh, indent=1)
    print("\nwrote %s" % args.out)


if __name__ == "__main__":
    main()
