"""
NEW FINDING (not among the five gaps DEC-20260906-da1212 named, not caught by
the amendment-v3-review, not addressed by v4): stage2.py's
static_provenance_check() does a LITERAL SOURCE-TEXT SCAN for the OLD T3
function names, using this exact dict (stage2.py lines 63-72, read directly
by this review):

    "T3 (rudin_shapiro_sign)": "def rudin_shapiro_sign(",
    "T3 (rudin_shapiro_sign_array)": "def rudin_shapiro_sign_array(",

This is DIFFERENT from V3-CHG-2's required_naming_and_wiring, which is about
WIRING A CALL SITE (stage0.py line 54's E.rudin_shapiro_sign_array(xs) call,
correctly identified by the amendment-v3-review's attack_3). stage2.py's
check never CALLS rudin_shapiro_sign_array; it greps estimator.py's own
source text for the literal function SIGNATURE string. Neither v3's
required_naming_and_wiring nor v4's change_5 (which touches ONLY
selftest.py) updates this dict.

Two consequences, verified by this script against (a) the REAL, currently
committed estimator.py and (b) a faithful reconstruction of estimator.py
after V3-CHG-2's rename/add is applied:

  (a) TODAY, BEFORE any amendment: "T3 (rudin_shapiro_sign_array)" already
      shows reads_k=True (hence static_provenance gate FAILS) -- but this is
      a FALSE POSITIVE already diagnosed by round-1's own validator (J1,
      experiments/EXP-ECDLP-56ee42/reviews/round-1/validator/
      check_e_t3_dataflow_and_definition.py lines 76-88): every one of the
      7 "k" token matches is either the docstring's prose "bit-length k" or
      the function's OWN LOCAL LOOP VARIABLE `k` (a bit-shift level index
      over the vectorized fill, bounded by n = the array's own length, NOT
      the discrete-log coordinate). J1 diagnosed this; NOTHING in v2, v3, or
      v4 patches the scanner or the dict to stop it recurring.

  (b) AFTER v3's required rename is applied (as literally specified,
      verified against the reconstruction in full_patched_estimator_v3only.py
      in this same directory): the search strings "def rudin_shapiro_sign("
      and "def rudin_shapiro_sign_array(" are no longer found ANYWHERE in
      estimator.py's source at all (the functions are renamed to
      _rudin_shapiro_signflip_variant(_array), and the new function is named
      rudin_shapiro_sign_true(_array) -- neither string is a substring
      match). Both T3 entries flip from {found:true, reads_k:true, pass:
      false} to {found:false, reads_k:null, pass:false} -- STILL FALSE, for
      a DIFFERENT reason, with NO patch required in v3 or v4 to fix it.

Since v3's own required_rerun_before_stage_3 explicitly requires "its gates
(POS-A, POS-B, CONTROL-C1, CONTROL-C2 ..., static provenance C3) all pass"
before Stage 3 may be dispatched, the REQUIRED Stage 0-2 re-run's Stage 2 will
FAIL its static_provenance gate YET AGAIN under v3+v4 as currently drafted,
UNLESS the Executor also updates stage2.py's `functions` dict to reference
the NEW function names -- a change neither amendment specifies, in the same
"falls through the gap between a call site and something else" pattern
change_5 fixes for selftest.py, but left open here for a BLOCKING gate
rather than a manual regression script.
"""
import re
from pathlib import Path


def static_provenance_check_reimplementation(src: str) -> dict:
    """Exact reimplementation of stage2.py's static_provenance_check()
    body (verified line-for-line against the real stage2.py, read directly
    by this review), applied to an arbitrary estimator.py source string."""
    functions = {
        "T1/T2 (thue_morse_sign)": "def thue_morse_sign(",
        "T1/T2 (thue_morse_sign_array)": "def thue_morse_sign_array(",
        "T3 (rudin_shapiro_sign)": "def rudin_shapiro_sign(",
        "T3 (rudin_shapiro_sign_array)": "def rudin_shapiro_sign_array(",
        "T4 (popcount_mod4)": "def popcount_mod4(",
        "T4 (popcount_mod4_array)": "def popcount_mod4_array(",
        "COMPARATOR (top_bit_fiber)": "def top_bit_fiber(",
        "COMPARATOR (top_bit_fiber_array)": "def top_bit_fiber_array(",
    }
    results = {}
    all_pass = True
    for name, sig in functions.items():
        idx = src.find(sig)
        if idx < 0:
            results[name] = {"found": False, "reads_k": None, "pass": False}
            all_pass = False
            continue
        next_def = src.find("\ndef ", idx + 1)
        body = src[idx:next_def if next_def > 0 else len(src)]
        code_lines = [ln for ln in body.split('\n')
                      if ln.strip() and not ln.strip().startswith('#')
                      and not ln.strip().startswith('"')
                      and not ln.strip().startswith("'")]
        code_k_refs = re.findall(r'\bk\b', '\n'.join(code_lines))
        reads_k = len(code_k_refs) > 0
        results[name] = {"found": True, "reads_k": reads_k,
                          "k_refs_in_code": code_k_refs, "pass": not reads_k}
        if reads_k:
            all_pass = False
    return {"all_pass": all_pass, "functions": results}


if __name__ == "__main__":
    import json

    real_src = Path(
        "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-56ee42/"
        "implementation/estimator.py"
    ).read_text()
    patched_src = Path("full_patched_estimator_v3only.py").read_text()

    print("=== (a) TODAY, against the REAL committed estimator.py ===")
    real_result = static_provenance_check_reimplementation(real_src)
    print(json.dumps(real_result["functions"]["T3 (rudin_shapiro_sign)"], indent=2))
    print(json.dumps(real_result["functions"]["T3 (rudin_shapiro_sign_array)"], indent=2))
    print("all_pass:", real_result["all_pass"])
    # This must match the actual archived RUN-ECDLP-56ee42-S2/raw-result.json
    # exactly (independently read by this review):
    archived_S2_T3_array_entry = {
        "found": True, "reads_k": True,
        "k_refs_in_code": ["k", "k", "k", "k", "k", "k", "k"], "pass": False,
    }
    assert real_result["functions"]["T3 (rudin_shapiro_sign_array)"] == archived_S2_T3_array_entry, \
        "reimplementation does not match the archived S2 record -- reimplementation bug"
    print("CONFIRMED: reimplementation reproduces the archived S2 static-provenance-check.json exactly.")

    print()
    print("=== (b) AFTER v3's V3-CHG-2 rename is applied (reconstruction) ===")
    patched_result = static_provenance_check_reimplementation(patched_src)
    print(json.dumps(patched_result["functions"]["T3 (rudin_shapiro_sign)"], indent=2))
    print(json.dumps(patched_result["functions"]["T3 (rudin_shapiro_sign_array)"], indent=2))
    print("all_pass:", patched_result["all_pass"])
    assert patched_result["functions"]["T3 (rudin_shapiro_sign)"]["found"] is False
    assert patched_result["functions"]["T3 (rudin_shapiro_sign_array)"]["found"] is False
    assert patched_result["all_pass"] is False
    print()
    print("CONFIRMED: static_provenance_check.all_pass is STILL False after the v3")
    print("rename -- now via 'not found' rather than a false-positive 'reads_k'.")
    print("Neither v3 nor v4 patches stage2.py's function-name dict, so the")
    print("required Stage 0-2 re-run's Stage 2 'static_provenance' gate --")
    print("explicitly named as required-to-pass by v3's own")
    print("required_rerun_before_stage_3 clause -- will FAIL AGAIN, blocking")
    print("Stage 3 dispatch, for a reason neither amendment discloses or fixes.")

    print()
    print("=== For completeness: what WOULD happen if the dict were correctly")
    print("    updated to point at the new true implementation? ===")
    functions_fixed = {
        "T3 (rudin_shapiro_sign_true)": "def rudin_shapiro_sign_true(",
        "T3 (rudin_shapiro_sign_true_array)": "def rudin_shapiro_sign_true_array(",
    }
    for name, sig in functions_fixed.items():
        idx = patched_src.find(sig)
        next_def = patched_src.find("\ndef ", idx + 1)
        body = patched_src[idx:next_def if next_def > 0 else len(patched_src)]
        code_lines = [ln for ln in body.split('\n')
                      if ln.strip() and not ln.strip().startswith('#')
                      and not ln.strip().startswith('"')
                      and not ln.strip().startswith("'")]
        code_k_refs = re.findall(r'\bk\b', '\n'.join(code_lines))
        print(f"  {name}: found={idx>=0}, k_refs_in_code={code_k_refs}, "
              f"would_pass={idx>=0 and len(code_k_refs)==0}")
    print("  (i.e. updating the dict is a straightforward, one-line-per-entry")
    print("   fix, and the NEW true implementation contains no local variable")
    print("   literally named k, so it would PASS cleanly -- this is a real,")
    print("   simple, currently-unspecified required control, not a deep")
    print("   design problem.)")
