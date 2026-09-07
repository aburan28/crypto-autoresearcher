"""
Independent, code-execution verification of V5-CHG-1 (amendment v5,
experiments/EXP-ECDLP-56ee42/amendments/
v5_stage2_provenance_and_power_check_budget_repair.yaml), closing exactly the
gap the amendment's own drafting session disclosed it could not close ("no
code-execution tool in this session ... the correctness of (a)-(c) rests on
this Coordinator's own direct, line-by-line comparison ... not on re-running
the code a third time").

This script does NOT reuse the amendment-v4-review's own reconstruction file
(full_patched_estimator_v3only.py) or its reimplementation
(stage2_static_provenance_break.py). It independently:

  1. Builds a v3-renamed estimator.py from the REAL, currently-committed
     estimator.py by applying V3-CHG-2's required rename/add verbatim (via
     exact-substring replacement, asserting the old text is found first, so
     a silent mismatch cannot pass unnoticed).
  2. Imports and RUNS the REAL, currently-committed stage2.py's own
     static_provenance_check() function (not a reimplementation) against
     that v3-renamed estimator.py, BEFORE V5-CHG-1's dict fix is applied
     (real stage2.py, unmodified) -- this is the "before" state the
     amendment claims gives {found:false, reads_k:null, pass:false}.
  3. Applies V5-CHG-1's exact new_text to a copy of the real stage2.py (a
     two-line dict-entry substitution, asserting the old text is found
     first) and re-runs the REAL static_provenance_check() again -- the
     "after" state the amendment claims gives
     {found:true, reads_k:false, pass:true} for both T3 entries and
     all_pass:true overall.
  4. Additionally tests BOTH "partial application" orders the review task
     asks about: (a) V5-CHG-1's dict fix applied WITHOUT V3-CHG-2's
     estimator.py rename (i.e. against the REAL, current, un-renamed
     estimator.py); (b) V3-CHG-2's rename applied WITHOUT V5-CHG-1's dict
     fix (same as step 2's "before" state, re-stated here for clarity) --
     to check whether a partial/out-of-order application of the
     sequencing_dependency the amendment names fails SAFE (gate correctly
     reports failure) or fails DANGEROUS (gate silently reports a false
     pass).

No file outside this review's own write_scope
(experiments/EXP-ECDLP-56ee42/reviews/amendment-v5-review/) is read for
mutation and none outside it is written. The REAL committed estimator.py and
stage2.py are read-only inputs; all patched copies live under ./scratch/.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_IMPL = Path(
    "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-56ee42/implementation"
)
HERE = Path(__file__).parent
SCRATCH = HERE / "scratch_v5chg1"


def build_v3_renamed_estimator(real_src: str) -> str:
    """Apply V3-CHG-2's required rename/add to the real estimator.py source,
    independently derived from the amendment's own required_vectorized_fix /
    required_naming_and_wiring text (not copied from any prior review's
    reconstruction file)."""
    old_scalar_def = '''def rudin_shapiro_sign(x: int) -> int:
    """The Rudin-Shapiro sign, defined by the recursion r(0)=r(1)=1,
    r(2n)=r(n), r(2n+1)=-r(n) for n>=1 (the standard Rudin-Shapiro sequence,
    OEIS A016158, which carries the root-N property the hypothesis relies on).

    INTERPRETATION NOTE: the contract describes u as 'the count of block 11
    in the binary expansion'.  That heuristic characterization does NOT
    exactly match the recursion (they diverge at x=5, 9, 10, ...; 135 of the
    first 256 values differ).  The recursion is used as the canonical
    definition because (a) it is the standard Rudin-Shapiro sequence and
    (b) the hypothesis's root-N property is a property of the recursion, not
    of the block-count sequence.  This interpretation is recorded in the run
    record; a reviewer who reads the contract's 'block 11' literally may
    request a protocol_amendment.  See _rudin_shapiro_u for the literal
    block-count (kept for reference / audit)."""
    if x < 2:
        return 1
    sign = 1
    while x >= 2:
        if x & 1:
            sign = -sign
        x >>= 1
    return sign'''
    assert old_scalar_def in real_src, "scalar def not found verbatim in real estimator.py"
    new_scalar_def = '''def _rudin_shapiro_signflip_variant(x: int) -> int:
    """RETIRED (renamed by amendment v3, V3-CHG-2): the recursion
    r(0)=r(1)=1, r(2n)=r(n), r(2n+1)=-r(n) for n>=1.  NEVER called by any
    stage going forward; kept for the audit trail only."""
    if x < 2:
        return 1
    sign = 1
    while x >= 2:
        if x & 1:
            sign = -sign
        x >>= 1
    return sign


def rudin_shapiro_sign_true(x: int) -> int:
    """The TRUE Rudin-Shapiro sign per amendment v3 (V3-CHG-2): the literal
    block-count definition, v(R) = (-1)^u(x), via the identity
    u(x) = popcount(x & (x >> 1))."""
    return 1 if (x & (x >> 1)).bit_count() % 2 == 0 else -1'''
    src2 = real_src.replace(old_scalar_def, new_scalar_def)
    assert src2 != real_src

    old_array_def = '''def rudin_shapiro_sign_array(xs: np.ndarray) -> np.ndarray:
    """Vectorised Rudin-Shapiro sign via the recursion r(0)=r(1)=1,
    r(2n)=r(n), r(2n+1)=-r(n), which equals (-1)^{u(x)} with u the count of
    (overlapping) '11' blocks in the binary expansion.  Fills level by level
    (all of bit-length k from bit-length k-1) so it is O(n) vectorised work."""
    n = int(xs.max(initial=0)) + 1
    r = np.ones(n, dtype=np.int8)
    k = 1
    while (1 << k) < n:
        lo = 1 << k
        hi = min(1 << (k + 1), n)
        m = np.arange(lo, hi, dtype=np.int64)
        parent = r[m >> 1]
        r[lo:hi] = np.where((m & 1) == 0, parent, -parent)
        k += 1
    return r[xs.astype(np.int64)]'''
    assert old_array_def in src2, "array def not found verbatim"
    new_array_def = '''def _rudin_shapiro_signflip_variant_array(xs: np.ndarray) -> np.ndarray:
    """RETIRED (renamed by amendment v3, V3-CHG-2). See
    _rudin_shapiro_signflip_variant."""
    n = int(xs.max(initial=0)) + 1
    r = np.ones(n, dtype=np.int8)
    k = 1
    while (1 << k) < n:
        lo = 1 << k
        hi = min(1 << (k + 1), n)
        m = np.arange(lo, hi, dtype=np.int64)
        parent = r[m >> 1]
        r[lo:hi] = np.where((m & 1) == 0, parent, -parent)
        k += 1
    return r[xs.astype(np.int64)]


def rudin_shapiro_sign_true_array(xs: np.ndarray) -> np.ndarray:
    """Vectorised TRUE Rudin-Shapiro sign per amendment v3 (V3-CHG-2), using
    the SAME SWAR popcount reduction popcount_mod4_array uses, mod 2 instead
    of mod 4."""
    x = xs.astype(np.uint64)
    y = x & (x >> 1)
    c = y - ((y >> 1) & 0x5555555555555555)
    c = (c & 0x3333333333333333) + ((c >> 2) & 0x3333333333333333)
    c = (c + (c >> 4)) & 0x0F0F0F0F0F0F0F0F
    pc = ((c * 0x0101010101010101) >> 56).astype(np.uint8)
    return (1 - 2 * (pc % 2)).astype(np.int8)'''
    src3 = src2.replace(old_array_def, new_array_def)
    assert src3 != src2
    return src3


def apply_v5chg1_dict_fix(real_stage2_src: str) -> str:
    old = '''        "T3 (rudin_shapiro_sign)": "def rudin_shapiro_sign(",
        "T3 (rudin_shapiro_sign_array)": "def rudin_shapiro_sign_array(",'''
    new = '''        "T3 (rudin_shapiro_sign_true)": "def rudin_shapiro_sign_true(",
        "T3 (rudin_shapiro_sign_true_array)": "def rudin_shapiro_sign_true_array(",'''
    assert old in real_stage2_src, "V5-CHG-1's claimed old_text not found verbatim in real stage2.py"
    out = real_stage2_src.replace(old, new)
    assert out != real_stage2_src
    return out


def run_static_provenance_check(dirpath: Path) -> dict:
    """Runs, in a fresh subprocess with cwd=dirpath, the REAL
    static_provenance_check() function from whatever stage2.py/estimator.py
    pair lives in dirpath -- executes the real code, not a reimplementation."""
    code = (
        "import sys, json; sys.path.insert(0, '.'); "
        "import importlib; "
        "import stage2 as S2; "
        "print(json.dumps(S2.static_provenance_check()))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], cwd=dirpath,
        capture_output=True, text=True, check=True,
    )
    return json.loads(proc.stdout)


def main() -> None:
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)

    real_estimator_src = (REPO_IMPL / "estimator.py").read_text()
    real_stage2_src = (REPO_IMPL / "stage2.py").read_text()

    v3_renamed_estimator_src = build_v3_renamed_estimator(real_estimator_src)
    v5chg1_stage2_src = apply_v5chg1_dict_fix(real_stage2_src)

    scenarios = {
        "0_today_real_unmodified": {
            "estimator.py": real_estimator_src,
            "stage2.py": real_stage2_src,
            "desc": "REAL committed estimator.py + REAL committed stage2.py "
                    "(reproduces the archived RUN-ECDLP-56ee42-S2 record's "
                    "false-positive reads_k=true finding).",
        },
        "1_before_v5chg1_v3_renamed_only": {
            "estimator.py": v3_renamed_estimator_src,
            "stage2.py": real_stage2_src,
            "desc": "V3-CHG-2 rename APPLIED to estimator.py, stage2.py dict "
                    "UNMODIFIED (real). This is the 'before V5-CHG-1' state "
                    "the amendment claims gives "
                    "{found:false, reads_k:null, pass:false}.",
        },
        "2_after_v5chg1_both_applied": {
            "estimator.py": v3_renamed_estimator_src,
            "stage2.py": v5chg1_stage2_src,
            "desc": "V3-CHG-2 rename AND V5-CHG-1 dict fix BOTH applied. "
                    "This is the state V5-RA-1 requires to show "
                    "{found:true, reads_k:false, pass:true} for both T3 "
                    "entries and all_pass:true overall.",
        },
        "3_partial_application_dict_fix_without_rename": {
            "estimator.py": real_estimator_src,
            "stage2.py": v5chg1_stage2_src,
            "desc": "PARTIAL APPLICATION (order A): V5-CHG-1's dict fix "
                    "applied to stage2.py, but estimator.py is the REAL, "
                    "CURRENT, UN-RENAMED file (V3-CHG-2 not yet applied). "
                    "Tests whether an out-of-order partial application "
                    "fails SAFE (gate correctly reports failure) or "
                    "DANGEROUSLY (a false all_pass:true).",
        },
    }

    all_results = {}
    for name, spec in scenarios.items():
        d = SCRATCH / name
        d.mkdir()
        (d / "estimator.py").write_text(spec["estimator.py"])
        (d / "stage2.py").write_text(spec["stage2.py"])
        result = run_static_provenance_check(d)
        all_results[name] = {"desc": spec["desc"], "result": result}
        print(f"=== scenario: {name} ===")
        print(spec["desc"])
        print(json.dumps(result, indent=2))
        print()

    # ------------------------------------------------------------------
    # Assertions checking the amendment's own claimed before/after values,
    # and the safety of partial application.
    # ------------------------------------------------------------------
    before = all_results["1_before_v5chg1_v3_renamed_only"]["result"]
    after = all_results["2_after_v5chg1_both_applied"]["result"]
    partial = all_results["3_partial_application_dict_fix_without_rename"]["result"]

    assert before["functions"]["T3 (rudin_shapiro_sign)"] == {
        "found": False, "reads_k": None, "pass": False}
    assert before["functions"]["T3 (rudin_shapiro_sign_array)"] == {
        "found": False, "reads_k": None, "pass": False}
    assert before["all_pass"] is False
    print("CONFIRMED: 'before V5-CHG-1' state exactly matches the amendment's "
          "claimed {found:false, reads_k:null, pass:false}.")

    assert after["functions"]["T3 (rudin_shapiro_sign_true)"] == {
        "found": True, "reads_k": False, "k_refs_in_code": [], "pass": True}
    assert after["functions"]["T3 (rudin_shapiro_sign_true_array)"] == {
        "found": True, "reads_k": False, "k_refs_in_code": [], "pass": True}
    assert after["all_pass"] is True
    print("CONFIRMED: 'after V5-CHG-1' state exactly matches V5-RA-1's "
          "required {found:true, reads_k:false, pass:true} for both T3 "
          "entries, and all_pass:true across all eight entries.")

    assert partial["all_pass"] is False
    assert partial["functions"]["T3 (rudin_shapiro_sign_true)"]["found"] is False
    print("CONFIRMED: partial application (V5-CHG-1's dict fix WITHOUT "
          "V3-CHG-2's estimator.py rename) fails SAFE: all_pass is False, "
          "never a false positive pass.")

    print()
    print("ALL ASSERTIONS PASSED. V5-CHG-1's claimed before/after behaviour "
          "is independently confirmed by actually executing the REAL "
          "stage2.py's static_provenance_check() function (not a "
          "reimplementation) against constructed estimator.py/stage2.py "
          "pairs, and the sequencing_dependency's partial-application risk "
          "is confirmed to fail safe in this direction.")


if __name__ == "__main__":
    main()
