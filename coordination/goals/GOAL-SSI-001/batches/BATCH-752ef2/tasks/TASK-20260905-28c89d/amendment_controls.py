#!/usr/bin/env python3
"""Controls AC-1..AC-4 for TASK-20260905-28c89d (CF-1/RC-6, GOAL-SSI-001).

STANDALONE. Python standard library only. No network. No numpy, no SageMath.
It imports NOTHING from experiments/ and it NEVER executes
experiments/EXP-WESOVOW-001/cost_model.py -- that file is read as text only, and
not even that by this script, which reads only artifacts of this task directory.

CITATION PROHIBITION, RESTATED VERBATIM:
    The `P=512` crossover value and its `w=2^80` sign are **NOT
    citation-eligible**. This task does not lift that prohibition. Only a
    committed Coordinator decision on independently reviewed evidence can lift
    it.
PREDICATE EXTENSION, RESTATED VERBATIM:
    In addition to the retained sentence, a row of any EXP-WESOVOW-001
    reconciliation is NOT citation-eligible when either (a) the two anchors
    disagree in the SIGN of the baseline comparison at that row, or (b) the
    smaller |margin| across the two anchors at that row is below that field
    size's anchor gap |Delta log2 T_full + Delta log2 M / 2|.
APPLICABILITY IN THIS ARTIFACT: the retained sentence is APPLICABLE (this file
    manipulates a symbolic description of a crossover) and DID NOT FIRE (no
    crossover value, baseline comparison, margin, sign or speedup is computed,
    tabulated or emitted anywhere; the only numbers here are the abstract
    coefficients alpha, beta, delta of a contract SHAPE). The predicate
    extension is NOT APPLICABLE and did not fire: no reconciliation row is
    read, cited or computed.
BLIND-PHASE HYGIENE: no value of the PAPER_PAIRS mapping at cost_model.py:60-66
    and no EV-SSI-5d954c delta appears in this file. They are named by locator.

Every control takes its input as an argument so a reviewer can import this
module and call it with an input the reviewer constructs.

Writes: NOTHING inside the repository. The AC-3/AC-4 positive controls
materialize their scratch copy in a caller-supplied directory, defaulting to a
fresh tempfile.mkdtemp() OUTSIDE the repository, because this task's declared
artifact path set is exact and a seventh file in the task directory would break
the snapshot archive's verification.
"""

import argparse
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# The unsatisfiability argument, as a general engine over a CONTRACT SHAPE.
# ---------------------------------------------------------------------------
# A contract shape is the pair of blocks abstracted to three coefficients.
#
#   Notation (all quantities are base-2 logarithms):
#     t = log2 T_full, m = log2 M, x = log2 w, d = log2 T_DG,
#     h = overhead_bits, A = t + h - d.
#     g(x) := log2 T(w) - t - h, the charging law's memory-dependent term.
#
#   METRICS BLOCK  states a closed-form crossover:   log2 w* = alpha*m + beta*A
#   CAP CONTROL    states the value of g at w = M:   g(m) = delta
#
#   The crossover is, by its own definition, the budget where the
#   overhead-inflated time meets the baseline: t + g(log2 w*) + h = d, i.e.
#   g(log2 w*) = -A. Substituting the metrics block: g(alpha*m + beta*A) = -A,
#   required to hold across the contract's scenario grid, on which A takes many
#   distinct values at each m.
#
#   Positing the law's memory term affine in (x, m), g(x) = kappa*x + mu*m,
#   and matching coefficients of A and of m:
#       kappa*beta = -1          =>  kappa = -1/beta      (needs beta != 0)
#       kappa*alpha + mu = 0     =>  mu    = alpha/beta
#   The cap control then requires
#       g(m) = (kappa + mu)*m = m*(alpha - 1)/beta = delta.
#
#   This is the whole argument. It is deliberately written so that alpha, beta
#   and delta are INPUTS: the same code decides the real contract and any
#   synthetic one, which is what makes AC-1 informative rather than a mirror.

TOL = 1e-12


def solve_joint(alpha, beta, delta):
    """Return the satisfying set of (t, m) for a contract shape.

    Verdicts:
      'ill_posed'                  - beta == 0; the metrics block does not
                                     determine the law at all.
      'satisfiable_unconstrained'  - every (t, m) works; the blocks agree.
      'unsatisfiable_everywhere'   - no (t, m) works, not even a degenerate one.
      'satisfiable_only_on_slice'  - exactly the m named by m_solution works.
    """
    if abs(beta) < TOL:
        return {
            "verdict": "ill_posed",
            "reason": "beta == 0: the stated crossover does not depend on the "
                      "gap to baseline, so no charging law is determined.",
            "t_constrained": False,
            "m_solution": None,
            "degenerate": None,
        }
    kappa = -1.0 / beta
    mu = alpha / beta
    coeff_m = kappa + mu           # == (alpha - 1) / beta
    if abs(coeff_m) < TOL:
        if abs(delta) < TOL:
            return {"verdict": "satisfiable_unconstrained", "kappa": kappa,
                    "mu": mu, "t_constrained": False, "m_solution": "any",
                    "degenerate": False,
                    "reason": "the cap condition is an identity in m"}
        return {"verdict": "unsatisfiable_everywhere", "kappa": kappa, "mu": mu,
                "t_constrained": False, "m_solution": None, "degenerate": None,
                "reason": "the cap condition demands a nonzero constant from a "
                          "term identically zero in m"}
    m_sol = delta / coeff_m
    return {"verdict": "satisfiable_only_on_slice", "kappa": kappa, "mu": mu,
            "t_constrained": False, "m_solution": m_sol,
            "degenerate": abs(m_sol) < TOL,
            "reason": "the cap condition pins m to a single value; t is free"}


# The real contract, transcribed from the frozen file BY SHAPE ONLY.
#   specification.yaml:39-40  ->  log2 w* = 2*(t + h - d): no m term
#                                 => alpha = 0.0, beta = 2.0
#   specification.yaml:148-149 (C4) -> T(M) = T_full exactly => delta = 0.0
REAL_CONTRACT = {
    "name": "EXP-WESOVOW-001 specification.yaml:39-40 vs control C4:148-149",
    "alpha": 0.0, "beta": 2.0, "delta": 0.0,
    "metrics_locator": "experiments/EXP-WESOVOW-001/specification.yaml:39-40",
    "cap_locator": "experiments/EXP-WESOVOW-001/specification.yaml:148-149",
}

# AC-1's synthetic object: same SHAPE, chosen so a single law satisfies both on
# an open set. It is the real contract with the log2 M term present in the
# crossover (alpha = 1). Nothing about the real file is asserted by it.
AC1_SYNTHETIC_SATISFIABLE = {
    "name": "synthetic-satisfiable (alpha=1: crossover carries the m term)",
    "alpha": 1.0, "beta": 2.0, "delta": 0.0,
}
# A second synthetic, satisfiable only on a NON-degenerate slice, to show the
# engine distinguishes three outcomes and not two.
AC1_SYNTHETIC_NONDEGENERATE_SLICE = {
    "name": "synthetic-nondegenerate-slice (alpha=0, cap offset delta=1)",
    "alpha": 0.0, "beta": 2.0, "delta": 1.0,
}
# AC-2's failure-branch object: genuinely unsatisfiable everywhere, so the
# degenerate witness m = 0 is NOT in its satisfying set.
AC2_EMPTY_SET_CONTRACT = {
    "name": "synthetic-empty-set (alpha=1 with a nonzero cap offset)",
    "alpha": 1.0, "beta": 2.0, "delta": 1.0,
}


def ac1_satisfiability_control(contract):
    """AC-1. Run the unsatisfiability argument on a contract shape that a
    single charging law satisfies on an OPEN SET.

    FAILS IF the argument returns any form of unsatisfiability. An argument
    that finds a contradiction in a contract that has none is finding it in its
    own method.
    """
    res = solve_joint(contract["alpha"], contract["beta"], contract["delta"])
    passed = res["verdict"] == "satisfiable_unconstrained"
    return {
        "control": "AC-1",
        "input": dict(contract),
        "observed": res,
        "verdict": "pass" if passed else "FAIL",
        "failing_input_would_be": "any contract shape whose blocks agree on an "
                                  "open set but on which solve_joint returns "
                                  "unsatisfiable_everywhere or "
                                  "satisfiable_only_on_slice",
    }


def ac2_degenerate_witness_control(contract, witness_m):
    """AC-2. Evaluate the argument at the point the reproduction concedes the
    real blocks ARE jointly satisfiable.

    FAILS IF the argument reports a contradiction there, i.e. if it claims
    unsatisfiability unconditionally rather than on the excluded set.
    """
    res = solve_joint(contract["alpha"], contract["beta"], contract["delta"])
    if res["verdict"] == "satisfiable_unconstrained":
        member = True
    elif res["verdict"] == "satisfiable_only_on_slice":
        member = abs(res["m_solution"] - witness_m) < TOL
    else:
        member = False
    return {
        "control": "AC-2",
        "input": dict(contract),
        "witness_log2M": witness_m,
        "observed": res,
        "witness_is_in_satisfying_set": member,
        "verdict": "pass" if member else "FAIL",
        "failing_input_would_be": "a contract shape whose satisfying set is "
                                  "empty, e.g. AC2_EMPTY_SET_CONTRACT, for "
                                  "which the witness is not a member",
    }


# ---------------------------------------------------------------------------
# Text scans. AC-3 and AC-4.
# ---------------------------------------------------------------------------
# A scan normalizes the text (YAML folds sentences across lines, so a
# line-by-line regex cannot see a sentence) while keeping a map from normalized
# offset back to the original line number, so every hit is reported with a real
# locator.

TRANSCRIPTION_PREMISE_VOCABULARY = [
    r"correct(?:ing|ed|ion|ions)?\s+(?:the\s+|a\s+|any\s+|one\s+|those\s+)?"
    r"(?:literal|digit|transcribed\s+value)s?",
    r"repair(?:ing)?\s+the\s+anchor\s+by\s+correct",
    r"mis-?transcri\w*",
    r"transcription\s+(?:defect|error|errors|mistake|fault|failure|problem|issue)",
    r"\btypo\w*",
    r"wrong\s+(?:digit|literal|transcribed\s+value)s?",
    r"(?:incorrect|erroneous|mistaken|faulty)\s+(?:literal|digit|transcription)s?",
    r"(?:if|assuming|provided|unless|should)\s+the\s+(?:literal|digit|ten\s+value)s?\s+"
    r"(?:are|is|were|was|be)\s+(?:correct|right|accurate|faithful|wrong)",
    r"the\s+(?:literal|digit)s?\s+(?:are|is|were|was)\s+wrong",
    r"(?:change|changing|changed|replace|replacing|adjust|adjusting|amend|amending)\s+"
    r"(?:the\s+|a\s+|any\s+|one\s+)?(?:literal|digit)s?\b",
    r"premised\s+on\s+a\s+transcription",
]

FRAMING_DRIFT_VOCABULARY = [
    # NOTE ON THE CHARACTER CLASS: these patterns use `.` rather than `[^.]`
    # for the gap between anchors. The superseded sentence itself contains a
    # decimal point (`abs(dev) <= 0.75`), so a period-excluding gap could not
    # match it -- a scanner that cannot match the very sentence it exists to
    # catch. The cost is a wider gap and therefore a higher false-positive
    # rate, which errs toward failing the real draft rather than passing it.
    r"two-?sided.{0,240}?\bis\s+itself\s+the\s+defect\b",
    r"applying\s+a\s+two-?sided.{0,240}?one-?sided",
    r"one-?sided.{0,200}?two-?sided.{0,160}?\bdefect\b",
    r"two-?sided.{0,200}?one-?sided.{0,160}?\b(?:is|as)\s+(?:itself\s+)?the\s+defect\b",
    r"the\s+(?:real\s+|actual\s+|underlying\s+)?defect\s+is\s+(?:that\s+)?(?:the\s+)?two-?sided",
    r"two-?sided\s+(?:test|tolerance|check|gate).{0,160}?\b(?:is|as|was)\b.{0,80}?"
    r"(?:the\s+)?(?:defect|error|mistake|flaw|problem)\b",
    r"(?:test|tolerance)\s+(?:should|must|ought\s+to)\s+be\s+one-?sided",
    r"C1.{0,120}?(?:should|must)\s+be\s+one-?sided",
]



def _normalize_with_linemap(text):
    """Collapse whitespace, returning (normalized, offset->line_number map)."""
    norm_chars = []
    line_of = []
    line = 1
    prev_space = True
    for ch in text:
        if ch == "\n":
            line += 1
            ch = " "
        if ch.isspace():
            if prev_space:
                continue
            norm_chars.append(" ")
            line_of.append(line)
            prev_space = True
        else:
            norm_chars.append(ch)
            line_of.append(line)
            prev_space = False
    return "".join(norm_chars), line_of


def exempt_line_ranges(text, exempt_key_names):
    """Line ranges (1-based, inclusive) of declared scan-exempt YAML regions.

    A region begins at a line whose content is `<key>:` for a declared key and
    runs while following lines are blank or indented strictly deeper. The
    mechanism is deliberately narrow: only keys named in the caller's list, and
    a reviewer can re-run any scan with exempt_key_names=() to see everything.
    """
    ranges = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        indent = len(lines[i]) - len(stripped)
        key = stripped.split(":", 1)[0] if ":" in stripped else None
        if key in exempt_key_names:
            start = i + 1
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if not nxt.strip():
                    j += 1
                    continue
                if len(nxt) - len(nxt.lstrip()) > indent:
                    j += 1
                    continue
                break
            ranges.append((start, j))       # 1-based start, j == last line
            i = j
            continue
        i += 1
    return ranges


def _blank_ranges(text, ranges):
    lines = text.split("\n")
    for (a, b) in ranges:
        for k in range(a - 1, min(b, len(lines))):
            lines[k] = ""
    return "\n".join(lines)


def scan_text(text, vocabulary, exempt_key_names=()):
    """Return every vocabulary hit with its pattern, matched span and line."""
    exempt = exempt_line_ranges(text, exempt_key_names)
    scanned = _blank_ranges(text, exempt) if exempt else text
    norm, line_of = _normalize_with_linemap(scanned)
    low = norm.lower()
    hits = []
    for pat in vocabulary:
        for m in re.finditer(pat, low):
            hits.append({
                "pattern": pat,
                "matched_text": norm[m.start():m.end()],
                "line": line_of[m.start()] if m.start() < len(line_of) else None,
            })
    return {"hits": hits,
            "exempt_line_ranges": [list(r) for r in exempt],
            "exempt_key_names": list(exempt_key_names)}


def ac3_transcription_premise_control(text, exempt_key_names=()):
    """AC-3. FAILS IF the scan reports a hit in the real draft.

    LIMITATION, DISCLOSED IN THE CONTROL ITSELF: this is a LEXICAL scan. It
    cannot distinguish an assertion from a disclaimer, and a semantically
    equivalent premise expressed in unlisted words would pass. It is therefore
    a necessary and not a sufficient check, and the drafting avoided the
    vocabulary outright rather than relying on the scanner to exculpate it.
    """
    res = scan_text(text, TRANSCRIPTION_PREMISE_VOCABULARY, exempt_key_names)
    return {"control": "AC-3", "observed": res,
            "verdict": "pass" if not res["hits"] else "FAIL",
            "failing_input_would_be": "a draft containing any listed premise "
                                      "phrase outside a declared exempt region"}


def ac4_framing_drift_control(text, exempt_key_names=()):
    """AC-4. FAILS IF a hit is found in the real draft. Same lexical
    limitation as AC-3, disclosed identically."""
    res = scan_text(text, FRAMING_DRIFT_VOCABULARY, exempt_key_names)
    return {"control": "AC-4", "observed": res,
            "verdict": "pass" if not res["hits"] else "FAIL",
            "failing_input_would_be": "a draft asserting, outside a declared "
                                      "exempt region, that a two-sided "
                                      "tolerance applied to one-sided figures "
                                      "is itself the defect"}


AFFIRMATION_PATTERNS = [
    r"two-?sided\s+test\s+is\s+(?:therefore\s+)?correct\s+for",
    r"correct\s+for\s+(?:control\s+)?c1'?s?\s+own\s+declared",
    r"correct\s+for\s+c1'?s?\s+own\s+declared\s+purpose",
    r"remains?\s+correct\s+for\s+control\s+c1'?s?\s+own\s+declared",
]


def ac4_affirmation_check(text):
    """The converse limb of AC-4: the draft must AFFIRM the two-sided test as
    correct for C1's own declared instrument-sanity purpose, not merely avoid
    denying it. Mechanical presence check; the hand check is recorded in
    amendment_controls_report.yaml."""
    norm, line_of = _normalize_with_linemap(text)
    low = norm.lower()
    found = []
    for pat in AFFIRMATION_PATTERNS:
        for m in re.finditer(pat, low):
            found.append({"pattern": pat, "matched_text": norm[m.start():m.end()],
                          "line": line_of[m.start()]})
    return {"check": "AC-4-affirmation", "found": found,
            "verdict": "pass" if found else "FAIL"}


def positive_control(scan_fn, text, offending_sentence, insert_after_line,
                     scratch_dir=None, exempt_key_names=()):
    """Materialize a scratch copy with one offending sentence inserted OUTSIDE
    any exempt region, run the same scan on it, and report whether it fired.

    The scratch copy is written to scratch_dir, defaulting to a fresh temporary
    directory OUTSIDE the repository (see module docstring).
    """
    scratch_dir = scratch_dir or tempfile.mkdtemp(prefix="ac_poscontrol_")
    lines = text.split("\n")
    idx = min(max(insert_after_line, 0), len(lines))
    lines.insert(idx, offending_sentence)
    mutated = "\n".join(lines)
    path = os.path.join(scratch_dir, "positive_control_copy.yaml")
    with open(path, "w") as fh:
        fh.write(mutated)
    with open(path) as fh:
        result = scan_fn(fh.read(), exempt_key_names)
    return {"scratch_copy_path": path,
            "inserted_sentence": offending_sentence,
            "inserted_after_line": idx,
            "scan_result": result,
            "fired": result["verdict"] == "FAIL"}


# ---------------------------------------------------------------------------
SCANNED_ARTIFACTS = ["protocol_amendment_draft.yaml",
                     "category_and_licensing_analysis.yaml",
                     "defect_reproduction.yaml"]
DECLARED_EXEMPT_KEYS = ("superseded_broad_framing_quoted_for_disclaimer_only",)

AC3_OFFENDING_SENTENCE = (
    "  positive_control_injected_sentence: >-\n"
    "    The anchor should be repaired by correcting the literals, since the "
    "divergence is a transcription error and the ten digits contain a typo.")
AC4_OFFENDING_SENTENCE = (
    "  positive_control_injected_sentence: >-\n"
    "    Applying a two-sided abs(dev) <= 0.75 test to the paper's one-sided "
    ">= figures is itself the defect.")


def _read(name):
    with open(os.path.join(HERE, name)) as fh:
        return fh.read()


def self_check(scratch_dir=None):
    out = {"ac1": [], "ac2": [], "ac3": {}, "ac4": {}}

    out["ac1"].append(ac1_satisfiability_control(AC1_SYNTHETIC_SATISFIABLE))
    out["ac1_reachability_demo"] = {
        "note": "the SAME engine on other shapes, to show AC-1's verdict is "
                "not entailed by its own construction",
        "real_contract": solve_joint(REAL_CONTRACT["alpha"],
                                     REAL_CONTRACT["beta"],
                                     REAL_CONTRACT["delta"]),
        "nondegenerate_slice": solve_joint(
            AC1_SYNTHETIC_NONDEGENERATE_SLICE["alpha"],
            AC1_SYNTHETIC_NONDEGENERATE_SLICE["beta"],
            AC1_SYNTHETIC_NONDEGENERATE_SLICE["delta"]),
        "empty_set": solve_joint(AC2_EMPTY_SET_CONTRACT["alpha"],
                                 AC2_EMPTY_SET_CONTRACT["beta"],
                                 AC2_EMPTY_SET_CONTRACT["delta"]),
        "ill_posed": solve_joint(0.0, 0.0, 0.0),
    }
    out["ac2"].append(ac2_degenerate_witness_control(REAL_CONTRACT, 0.0))
    out["ac2_failure_branch_fired"] = ac2_degenerate_witness_control(
        AC2_EMPTY_SET_CONTRACT, 0.0)

    for name in SCANNED_ARTIFACTS:
        text = _read(name)
        out["ac3"][name] = ac3_transcription_premise_control(text)
        out["ac4"][name] = ac4_framing_drift_control(
            text, DECLARED_EXEMPT_KEYS)
        out["ac4"].setdefault("_unexempted", {})[name] = ac4_framing_drift_control(
            text, ())

    draft = _read("protocol_amendment_draft.yaml")
    analysis = _read("category_and_licensing_analysis.yaml")
    out["ac3_positive_control"] = positive_control(
        ac3_transcription_premise_control, draft, AC3_OFFENDING_SENTENCE, 5,
        scratch_dir)
    out["ac4_positive_control"] = positive_control(
        ac4_framing_drift_control, draft, AC4_OFFENDING_SENTENCE, 5,
        scratch_dir, DECLARED_EXEMPT_KEYS)
    out["ac4_affirmation"] = {
        "protocol_amendment_draft.yaml": ac4_affirmation_check(draft),
        "category_and_licensing_analysis.yaml": ac4_affirmation_check(analysis),
    }

    def all_pass():
        ok = all(r["verdict"] == "pass" for r in out["ac1"])
        ok = ok and all(r["verdict"] == "pass" for r in out["ac2"])
        ok = ok and out["ac2_failure_branch_fired"]["verdict"] == "FAIL"
        ok = ok and all(v["verdict"] == "pass" for v in out["ac3"].values())
        ok = ok and all(v["verdict"] == "pass"
                        for k, v in out["ac4"].items() if k != "_unexempted")
        ok = ok and out["ac3_positive_control"]["fired"]
        ok = ok and out["ac4_positive_control"]["fired"]
        ok = ok and any(v["verdict"] == "pass"
                        for v in out["ac4_affirmation"].values())
        return ok

    out["all_controls_behaved_as_contracted"] = all_pass()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-check", action="store_true",
                    help="run AC-1..AC-4 on this task's artifacts and print JSON")
    ap.add_argument("--scratch-dir", default=None,
                    help="where the positive controls materialize their scratch "
                         "copies; defaults to a temp dir OUTSIDE the repository")
    args = ap.parse_args(argv)
    if not args.self_check:
        ap.print_help()
        return 2
    print(json.dumps(self_check(args.scratch_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
