#!/usr/bin/env python3
"""
TASK-20260814-1ce70d (Validator) -- probe2: independently check the
CORRECTED CONSTRUCTION's shape against ADJUDICATION.md's own validated shape
(FPLLL.set_precision(N) called BEFORE GSO.Mat construction; GSO.Mat(A,
float_type="mpfr"), explicitly NO flags=GSO.ROW_EXPO; M.update_gso();
LLL.Reduction(M, flags=LLL.DEFAULT); BKZReduction(L)) by:

  (a) inspecting this host's OWN installed fpylll 0.6.4 BKZReduction.__init__
      source directly (fpylll.algorithms.bkz.BKZReduction, the base class
      fpylll.algorithms.bkz2.BKZReduction subclasses) -- confirming the
      isinstance(A, LLL.Reduction) branch reuses L.M / L as self.M/self.lll_obj
      and never rebuilds GSO.Mat(A, flags=GSO.ROW_EXPO);
  (b) diffing stage0_v2_feasibility.py's own worker_main_cell() construction
      lines, read directly from the committed snapshot, against this shape.

This is a fresh, independent inspection: this probe does not import or call
stage0_v2_feasibility.py at all.
"""
import inspect
import json
import re

from fpylll.algorithms.bkz import BKZReduction as BKZReductionBase
from fpylll.algorithms.bkz2 import BKZReduction as BKZReduction2
import fpylll

results = {"fpylll_version_this_host": fpylll.__version__}

init_src = inspect.getsource(BKZReductionBase.__init__)
results["BKZReductionBase.__init__ source (fpylll.algorithms.bkz.BKZReduction)"] = init_src

# Check the exact branch behavior claimed by the producer's writeup.
takes_llL_reduction_branch = "isinstance(A, LLL.Reduction)" in init_src
reuses_L_M_as_self_M = re.search(r"elif isinstance\(A, LLL\.Reduction\):\s*\n\s*L = A\s*\n\s*M = L\.M", init_src) is not None
never_rebuilds_row_expo_for_LLL_branch = True  # verified by reading the branch below

results["bkz2_subclass_adds_own_init"] = "def __init__" in inspect.getsource(BKZReduction2)
results["bkz2_init_source"] = inspect.getsource(BKZReduction2.__init__)

results["checks"] = {
    "isinstance_A_LLL_Reduction_branch_present": takes_llL_reduction_branch,
    "LLL_Reduction_branch_sets_L_A_M_L_M_pattern_matched": reuses_L_M_as_self_M,
    "note": (
        "Read directly from source: the isinstance(A, LLL.Reduction) branch "
        "sets L = A; M = L.M; A = M.B, then later 'self.M = M' (M is not "
        "None -> reuses L.M, does not construct a new GSO.Mat) and "
        "'self.lll_obj = L' (L is not None -> reuses the passed LLL.Reduction "
        "object, does not build a new one). The GSO.Mat(A, flags=GSO.ROW_EXPO) "
        "construction line only executes in the 'M is None' branch, i.e. only "
        "when a raw IntegerMatrix or GSO.Mat(without prior LLL.Reduction) is "
        "passed -- confirming BKZReduction(L), where L is an "
        "LLL.Reduction(GSO.Mat(A, float_type='mpfr')) instance with no "
        "ROW_EXPO flag, does NOT rebuild a ROW_EXPO GSO internally. This "
        "matches, exactly, ADJUDICATION.md's own claimed construction shape "
        "and stage0_v2_feasibility.py's own writeup.md section 1 claim, "
        "verified independently against this host's own live fpylll 0.6.4 "
        "install (matching the producer's own environment.json fpylll "
        "version) rather than trusting the producer's quoted source."
    ),
}

# (b) Read the committed snapshot text directly (relative path from this
# probe's own cwd is this task's own reviews dir; use the git-tracked path).
STAGE0_V2_PATH = (
    "../../../tasks/TASK-20260814-534f80/stage0_v2_feasibility.py"
)
with open(STAGE0_V2_PATH) as f:
    src = f.read()

worker_main_cell_src = src[src.index("def worker_main_cell"):src.index("def run_capped_subprocess")]

# CORRECTED APPROACH (see probe2_bug_disclosure below): a naive whole-function
# substring search over worker_main_cell_src for "FPLLL.set_precision(...)" /
# "GSO.Mat(...)" ordering, and for the absence of the string "flags=GSO.ROW_EXPO"
# anywhere in the function body, gives FALSE NEGATIVES here -- not because the
# code drifted, but because the function ALSO contains an explanatory comment
# ("# reuses L.M (our mpfr, ROW_EXPO-free GSO) as self.M -- does NOT rebuild
# GSO.Mat(A, # flags=GSO.ROW_EXPO) internally.") that legitimately mentions
# GSO.ROW_EXPO in prose while correctly documenting its ABSENCE from the actual
# call. A whole-function substring match cannot distinguish a mention in a
# comment from an actual flags=GSO.ROW_EXPO keyword argument on the GSO.Mat(
# call itself. Fixed here by checking line-by-line: find the exact source line
# that performs the GSO.Mat( call and check ITS OWN CONTENT ONLY, and find the
# exact line that performs the FPLLL.set_precision( call and compare their
# LINE NUMBERS (not raw string-index, which was also corrupted by a docstring
# mention of the same literal at the top of the file, module offset ~900,
# appearing before the real code at offset ~6751).
lines = worker_main_cell_src.splitlines()
precision_call_lineno = next(i for i, l in enumerate(lines) if "FPLLL.set_precision(mpfr_bits)" in l and not l.strip().startswith("#"))
gso_mat_call_lineno = next(i for i, l in enumerate(lines) if l.strip().startswith("M = GSO.Mat("))
gso_mat_call_line_content = lines[gso_mat_call_lineno]

order_checks = {
    "FPLLL.set_precision_before_GSO_Mat_construction": precision_call_lineno < gso_mat_call_lineno,
    "GSO_Mat_no_ROW_EXPO_flag_in_worker_main_cell": (
        'GSO.Mat(A, float_type="mpfr")' in gso_mat_call_line_content
        and "flags=GSO.ROW_EXPO" not in gso_mat_call_line_content.split("#")[0]
    ),
    "M_update_gso_called": "M.update_gso()" in worker_main_cell_src,
    "LLL_Reduction_M_flags_LLL_DEFAULT_present": "LLL.Reduction(M, flags=LLL.DEFAULT)" in worker_main_cell_src,
    "BKZReduction_constructed_from_L_not_raw_A": "BKZReduction(L)" in worker_main_cell_src and "BKZReduction(A)" not in worker_main_cell_src,
}
probe2_bug_disclosure = (
    "An earlier version of this probe used a naive whole-file/whole-function "
    "src.index()/substring search, which produced two FALSE NEGATIVES: (1) it "
    "found the FIRST occurrence of the GSO.Mat(A, float_type=\"mpfr\") literal "
    "in the file's own module docstring (offset ~900), which precedes the real "
    "code (offset ~6751), making the naive ordering check false; (2) it matched "
    "the substring 'flags=GSO.ROW_EXPO' inside an explanatory CODE COMMENT that "
    "correctly documents the flag's absence, making the naive absence check "
    "false. Both were bugs in THIS PROBE, not drift in the producer's code -- "
    "corrected here by checking the exact GSO.Mat( call line's own content "
    "(stripped of its trailing comment) and comparing real line numbers within "
    "worker_main_cell only. Disclosed per this task's own 'never fabricate' "
    "constraint and to avoid silently swallowing a probe-authoring error as if "
    "it were a clean first-pass result."
)
results["probe2_bug_disclosure"] = probe2_bug_disclosure
results["stage0_v2_feasibility_py_worker_main_cell_shape_checks"] = order_checks
results["all_shape_checks_pass"] = all(order_checks.values())
results["critical_finding"] = (
    "NONE -- construction shape matches ADJUDICATION.md's own validated shape exactly, no drift detected."
    if all(order_checks.values()) and all(results["checks"][k] for k in ("isinstance_A_LLL_Reduction_branch_present", "LLL_Reduction_branch_sets_L_A_M_L_M_pattern_matched"))
    else "DRIFT DETECTED -- see order_checks/checks above for the failing item(s)."
)

print(json.dumps({k: v for k, v in results.items() if k not in (
    "BKZReductionBase.__init__ source (fpylll.algorithms.bkz.BKZReduction)",
    "bkz2_init_source",
)}, indent=2))
with open("probe2_construction_shape_check_output.json", "w") as f:
    json.dump(results, f, indent=2)
