#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PC-1: does the AMENDED contract still load, and still have the declared shape?

This is the control RT-1 (BATCH-79a0cb red-team report) showed the
EXP-WESOVOW-001 protocol amendment lacked.  An amendment that replaces text in
a machine-readable contract must carry a check that the RESULT still loads and
still has the declared shape.  It is committed and re-runnable so that its
result is re-checkable from an artifact rather than from a transcript.

WHAT IT ASSERTS, in order.  The first failure wins and is named on stdout; the
process then exits nonzero.

  P1  the amended text parses with yaml.safe_load
  P2  experiment.metrics is a list of exactly 7 items
  P3  metrics[5] is a mapping with exactly one key
  P4  metrics[5] equals - key AND value - the standalone parse of clause_1's
      own replacement_text_in_full

WHY P4 IS NOT OPTIONAL.  The UNAMENDED frozen specification.yaml already has a
7-element metrics list whose item 5 is a single-key mapping.  A control
asserting only P1-P3 therefore PASSES ON THE FILE IT EXISTS TO DETECT THE
AMENDMENT OF, and its pass on the redraft would be entailed by the file's
pre-existing shape rather than by anything the amendment did.  P4 is what makes
the control able to fail on that object, and `--selftest` runs that object
first.

WHAT IT DOES NOT CHECK.  Whether the replacement's CONTENT is correct; whether
the incorporated law is the right model of anything; whether any other consumer
of the contract accepts the amended file.  Clauses 2, 3 and 4 are spliced and
parsed by --splice-all-clauses and their resulting key lists are REPORTED, not
asserted on.  A green result means the amendment is APPLICABLE, never that it
is RIGHT.

WHAT IT NEVER DOES.  It opens no file for writing anywhere, writes nothing to
disk, creates no directory, imports and executes nothing from experiments/, and
in particular never imports or executes experiments/EXP-WESOVOW-001/cost_model.py
(CF-10: that file's default raw-output path names a committed run directory).
The amended contract exists only as a string in memory.  Bytecode writing is
disabled on the first line of execution so that no __pycache__ appears inside a
snapshot-bound directory.

THE STANDING CITATION PROHIBITION, RESTATED VERBATIM AND NOT LIFTED BY THIS
FILE:

  The `P=512` crossover value and its `w=2^80` sign are **NOT
  citation-eligible**. This task does not lift that prohibition. Only a
  committed Coordinator decision on independently reviewed evidence can lift
  it.

AND ITS PREDICATE EXTENSION, RESTATED VERBATIM:

  In addition to the retained sentence, a row of any EXP-WESOVOW-001
  reconciliation is NOT citation-eligible when either (a) the two anchors
  disagree in the SIGN of the baseline comparison at that row, or (b) the
  smaller |margin| across the two anchors at that row is below that field
  size's anchor gap |Delta log2 T_full + Delta log2 M / 2|.

NEITHER FIRED HERE.  This script computes YAML parse outcomes, list lengths and
mapping key counts.  It derives, recomputes, tabulates and cites no crossover
value, no baseline-comparison sign, no margin and no speedup.

Dependencies: the Python standard library plus PyYAML.  Nothing else.
"""

import sys

sys.dont_write_bytecode = True  # no __pycache__ inside a snapshot-bound directory

import argparse
import io
import json

import yaml

# ---------------------------------------------------------------------------
# The declared splice procedure.  See protocol_amendment_redraft.yaml,
# key amendment.splice_procedure.  These are the amendment's declarations, not
# this script's choices; changing one here would make the control check a
# different amendment than the one recorded.
TARGET_FIRST_LINE = 39          # 1-based, inclusive: experiment.metrics[5]
TARGET_LAST_LINE = 40           # 1-based, inclusive
CLAUSE_1_SPLICE_INDENT = 2      # the column of the metrics list items
CLAUSE_2_SPLICE_INDENT = 4      # the column of model_definition's keys
CLAUSE_34_SPLICE_INDENT = 4     # the column of controls[0]'s keys
MODEL_DEFINITION_APPEND_AFTER = 107   # 1-based last line of experiment.model_definition
CONTROLS_0_APPEND_AFTER = 141         # 1-based last line of experiment.controls[0]

EXPECTED_METRICS_LEN = 7
METRICS_INDEX = 5

AMENDMENT_CLAUSE_PATH = ("amendment", "proposed_replacement")


class ControlResult(object):
    """The outcome of one exercise of the control on one object."""

    def __init__(self, object_name):
        self.object_name = object_name
        self.passed = None            # True / False
        self.failed_assertion = None  # "P1" | "P2" | "P3" | "P4" | None
        self.message = ""
        self.observations = {}        # everything observed, pass or fail
        self.clause_key_lists = {}    # filled by --splice-all-clauses

    def as_dict(self):
        return {
            "object": self.object_name,
            "passed": self.passed,
            "failed_assertion": self.failed_assertion,
            "message": self.message,
            "observations": self.observations,
            "clause_key_lists": self.clause_key_lists,
        }


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def indent_block(text, columns):
    """Place a stored clause text at the given column, blank lines left blank."""
    out = []
    for line in text.rstrip("\n").split("\n"):
        out.append((" " * columns + line) if line.strip() else "")
    return out


def splice_replace(spec_text, clause_text, indent,
                   first_line=TARGET_FIRST_LINE, last_line=TARGET_LAST_LINE):
    """Replace spec lines [first_line, last_line] (1-based) with the clause."""
    lines = spec_text.split("\n")
    return "\n".join(
        lines[: first_line - 1] + indent_block(clause_text, indent) + lines[last_line:]
    )


def splice_append(spec_text, clause_text, indent, after_line):
    """Append the clause immediately after spec line `after_line` (1-based)."""
    lines = spec_text.split("\n")
    return "\n".join(
        lines[:after_line] + indent_block(clause_text, indent) + lines[after_line:]
    )


def find_anchor(text, prefix):
    """1-based number of the line BEFORE which `prefix` first occurs.

    Returned as an `after_line` for splice_append: the clause is inserted
    immediately before the first line starting with `prefix`.  Used instead of a
    fixed line number whenever a previous clause has already shifted the file.
    """
    for index, line in enumerate(text.split("\n")):
        if line.startswith(prefix):
            return index          # 0-based index == 1-based "insert after" line
    raise ValueError("could not locate anchor line starting %r" % (prefix,))


def expected_metrics_item(clause_text):
    """Parse clause_1's own replacement text, standalone, into its metrics item.

    This is deliberately NOT read out of the amended file: P4 must compare the
    amended file against the CLAUSE, so the expected value has to be obtained
    from the clause independently of the splice.
    """
    parsed = yaml.safe_load(clause_text)
    if not isinstance(parsed, list) or len(parsed) != 1:
        raise ValueError(
            "clause_1 replacement text does not parse standalone as a "
            "one-item sequence; got %r" % (type(parsed).__name__,)
        )
    return parsed[0]


def load_clause_texts(amendment_path):
    doc = yaml.safe_load(read_text(amendment_path))
    node = doc
    for key in AMENDMENT_CLAUSE_PATH:
        node = node[key]
    return {name: node[name]["replacement_text_in_full"]
            for name in ("clause_1", "clause_2", "clause_3", "clause_4")
            if name in node}


def run_control(spec_text, clause_1_text, apply_clause_1=True, object_name="(unnamed)"):
    """Run P1..P4.  Returns a ControlResult; raises nothing for a normal failure.

    `apply_clause_1=False` runs the control against the spec text AS GIVEN -
    that is the unamended-frozen-file object, and it is the object on which a
    P1-P3-only control would wrongly pass.
    """
    result = ControlResult(object_name)
    result.observations["clause_1_applied"] = bool(apply_clause_1)

    # The expected content, from the clause itself.
    try:
        expected = expected_metrics_item(clause_1_text)
        result.observations["expected_metrics_item_parsed"] = True
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        expected = None
        result.observations["expected_metrics_item_parsed"] = False
        result.observations["expected_metrics_item_error"] = "%s: %s" % (
            type(exc).__name__, exc)

    amended = splice_replace(spec_text, clause_1_text, CLAUSE_1_SPLICE_INDENT) \
        if apply_clause_1 else spec_text

    # -- P1 -----------------------------------------------------------------
    try:
        doc = yaml.safe_load(amended)
    except Exception as exc:  # noqa: BLE001
        result.passed = False
        result.failed_assertion = "P1"
        result.message = (
            "P1 FAILED - the amended text does not parse with yaml.safe_load. "
            "%s: %s" % (type(exc).__name__, str(exc).replace("\n", " | "))
        )
        result.observations["parse_error_type"] = type(exc).__name__
        result.observations["parse_error"] = str(exc)
        return result
    result.observations["P1"] = "pass - the amended text parses"

    # -- P2 -----------------------------------------------------------------
    try:
        metrics = doc["experiment"]["metrics"]
    except Exception as exc:  # noqa: BLE001
        result.passed = False
        result.failed_assertion = "P2"
        result.message = ("P2 FAILED - experiment.metrics is not reachable in the "
                          "parsed document (%s: %s)" % (type(exc).__name__, exc))
        return result
    result.observations["metrics_type"] = type(metrics).__name__
    result.observations["metrics_len"] = (
        len(metrics) if isinstance(metrics, list) else None)
    if not isinstance(metrics, list) or len(metrics) != EXPECTED_METRICS_LEN:
        result.passed = False
        result.failed_assertion = "P2"
        result.message = (
            "P2 FAILED - experiment.metrics is not a list of exactly %d items; "
            "it is a %s of length %s" % (
                EXPECTED_METRICS_LEN, type(metrics).__name__,
                len(metrics) if hasattr(metrics, "__len__") else "n/a")
        )
        return result
    result.observations["P2"] = "pass - experiment.metrics is a list of 7 items"

    # -- P3 -----------------------------------------------------------------
    item = metrics[METRICS_INDEX]
    result.observations["metrics_5_type"] = type(item).__name__
    result.observations["metrics_5_keys"] = (
        list(item.keys()) if isinstance(item, dict) else None)
    if not isinstance(item, dict) or len(item) != 1:
        result.passed = False
        result.failed_assertion = "P3"
        result.message = (
            "P3 FAILED - metrics[5] is not a mapping with exactly one key; "
            "it is a %s%s" % (
                type(item).__name__,
                " with %d keys" % len(item) if isinstance(item, dict) else "")
        )
        return result
    result.observations["P3"] = "pass - metrics[5] is a single-key mapping"

    # -- P4 -----------------------------------------------------------------
    if expected is None:
        result.passed = False
        result.failed_assertion = "P4"
        result.message = (
            "P4 FAILED - clause_1's own replacement text could not be parsed "
            "standalone, so there is no expected content to compare against: %s"
            % result.observations.get("expected_metrics_item_error"))
        return result
    if not isinstance(expected, dict) or len(expected) != 1:
        result.passed = False
        result.failed_assertion = "P4"
        result.message = (
            "P4 FAILED - clause_1's own replacement text does not itself parse "
            "as a single-key mapping; it parses as %s"
            % type(expected).__name__)
        return result
    result.observations["expected_metrics_5_keys"] = list(expected.keys())
    if item != expected:
        got_key = list(item.keys())[0]
        want_key = list(expected.keys())[0]
        if got_key != want_key:
            detail = ("the key differs: amended file has %r, clause_1 declares %r"
                      % (got_key, want_key))
        else:
            detail = "the key matches but the value differs"
        result.passed = False
        result.failed_assertion = "P4"
        result.message = (
            "P4 FAILED - metrics[5] does not equal the parse of clause_1's own "
            "replacement text; %s. THIS IS THE ASSERTION THAT DISTINGUISHES THE "
            "AMENDED FILE FROM THE UNAMENDED ONE." % detail)
        return result
    result.observations["P4"] = ("pass - metrics[5] equals the standalone parse of "
                                 "clause_1's replacement text")

    result.passed = True
    result.failed_assertion = None
    result.message = "PASS - P1, P2, P3 and P4 all hold."
    return result


def splice_all_clauses(spec_text, clauses):
    """Splice clauses 2, 3 and 4 under the declared procedure and report shapes.

    Reported, never asserted on.  Returns a dict of observations.
    """
    out = {}

    if "clause_2" in clauses:
        try:
            text = splice_append(spec_text, clauses["clause_2"],
                                 CLAUSE_2_SPLICE_INDENT,
                                 MODEL_DEFINITION_APPEND_AFTER)
            doc = yaml.safe_load(text)
            out["clause_2"] = {
                "parses": True,
                "model_definition_keys":
                    list(doc["experiment"]["model_definition"].keys()),
            }
        except Exception as exc:  # noqa: BLE001
            out["clause_2"] = {"parses": False,
                               "error": "%s: %s" % (type(exc).__name__, exc)}

    for name in ("clause_3", "clause_4"):
        if name not in clauses:
            continue
        try:
            text = splice_append(spec_text, clauses[name], CLAUSE_34_SPLICE_INDENT,
                                 CONTROLS_0_APPEND_AFTER)
            doc = yaml.safe_load(text)
            out[name] = {
                "parses": True,
                "controls_0_keys": list(doc["experiment"]["controls"][0].keys()),
            }
        except Exception as exc:  # noqa: BLE001
            out[name] = {"parses": False,
                         "error": "%s: %s" % (type(exc).__name__, exc)}

    if "clause_3" in clauses and "clause_4" in clauses:
        try:
            joint = (clauses["clause_3"].rstrip("\n") + "\n"
                     + clauses["clause_4"].rstrip("\n") + "\n")
            text = splice_append(spec_text, joint, CLAUSE_34_SPLICE_INDENT,
                                 CONTROLS_0_APPEND_AFTER)
            doc = yaml.safe_load(text)
            out["clause_3_and_clause_4_together"] = {
                "parses": True,
                "controls_0_keys": list(doc["experiment"]["controls"][0].keys()),
            }
        except Exception as exc:  # noqa: BLE001
            out["clause_3_and_clause_4_together"] = {
                "parses": False, "error": "%s: %s" % (type(exc).__name__, exc)}

    if clauses:
        try:
            # THE FIXED LINE NUMBERS ABOVE ARE ANCHORS INTO THE UNMODIFIED
            # version-1 file, and each clause applied shifts the ones after it -
            # clause_1's replacement is 9 lines where the original was 2, so
            # everything below line 40 moves down by 7, and clause_2 then moves
            # controls[0] again.  Applying all four therefore requires anchors
            # recomputed by SEARCH after each step, never the constants.  An
            # earlier version of this function used the constants here; it
            # produced a file that still parsed but in which
            # model_definition.vow_charging_law was absent, which is exactly the
            # silent-wrong-answer failure this control exists to catch, and it
            # was caught by reading the reported key list.  Recorded in
            # amendment_parse_control_report.yaml.
            text = splice_replace(spec_text, clauses["clause_1"],
                                  CLAUSE_1_SPLICE_INDENT)
            text = splice_append(text, clauses["clause_2"], CLAUSE_2_SPLICE_INDENT,
                                 find_anchor(text, "  scenario_definitions:"))
            joint = (clauses["clause_3"].rstrip("\n") + "\n"
                     + clauses["clause_4"].rstrip("\n") + "\n")
            text = splice_append(
                text, joint, CLAUSE_34_SPLICE_INDENT,
                find_anchor(text, "  - id: C2-baseline-consistency"))
            doc = yaml.safe_load(text)
            out["all_four_clauses_together"] = {
                "parses": True,
                "metrics_len": len(doc["experiment"]["metrics"]),
                "metrics_5_keys": list(doc["experiment"]["metrics"][5].keys()),
                "model_definition_keys":
                    list(doc["experiment"]["model_definition"].keys()),
                "controls_0_keys": list(doc["experiment"]["controls"][0].keys()),
            }
        except Exception as exc:  # noqa: BLE001
            out["all_four_clauses_together"] = {
                "parses": False, "error": "%s: %s" % (type(exc).__name__, exc)}

    return out


# ---------------------------------------------------------------------------
# The two synthetic negative objects, built here so that every object the
# control was exercised on is reconstructible from this committed file alone.
def synthetic_length_breaking(clause_1_text):
    """Parses, but yields a metrics list of length 8 instead of 7."""
    return clause_1_text.rstrip("\n") + "\n- an eighth metrics entry that nobody declared\n"


def synthetic_type_breaking():
    """Parses, but makes metrics[5] a plain string instead of a mapping."""
    return ("- crossover memory log2(w*) per (p, overhead c) - a plain string\n"
            "  with a continuation line and no colon, so it parses as a scalar\n")


def selftest(spec_path, amendment_path, superseded_path, stream):
    """Exercise the control on the five declared objects.  Exit 0 iff all five
    behaved as the amendment declares they must."""
    spec_text = read_text(spec_path)
    clauses = load_clause_texts(amendment_path)
    superseded_clause_1 = load_clause_texts(superseded_path)["clause_1"]

    objects = [
        ("(a) UNAMENDED frozen specification.yaml, no clause applied",
         dict(clause_1_text=clauses["clause_1"], apply_clause_1=False), "P4"),
        ("(b) SUPERSEDED BATCH-752ef2 clause_1, spliced over lines 39-40",
         dict(clause_1_text=superseded_clause_1, apply_clause_1=True), "P1"),
        ("(c) LENGTH-BREAKING replacement (parses; metrics length 8)",
         dict(clause_1_text=synthetic_length_breaking(clauses["clause_1"]),
              apply_clause_1=True), "P2"),
        ("(d) TYPE-BREAKING replacement (parses; metrics[5] a plain string)",
         dict(clause_1_text=synthetic_type_breaking(), apply_clause_1=True), "P3"),
        ("(e) THE REDRAFT's clause_1 - the positive control",
         dict(clause_1_text=clauses["clause_1"], apply_clause_1=True), None),
    ]

    all_as_declared = True
    results = []
    for name, kwargs, must_fail_on in objects:
        result = run_control(spec_text=spec_text, object_name=name, **kwargs)
        expected_desc = ("FAIL on %s" % must_fail_on) if must_fail_on else "PASS"
        actual_desc = ("FAIL on %s" % result.failed_assertion) if not result.passed \
            else "PASS"
        as_declared = (actual_desc == expected_desc)
        all_as_declared = all_as_declared and as_declared
        stream.write("%s\n" % name)
        stream.write("    declared: %s\n" % expected_desc)
        stream.write("    observed: %s\n" % actual_desc)
        stream.write("    message : %s\n" % result.message)
        stream.write("    verdict : %s\n\n" % ("AS DECLARED" if as_declared
                                               else "NOT AS DECLARED"))
        payload = result.as_dict()
        payload["declared"] = expected_desc
        payload["observed"] = actual_desc
        payload["as_declared"] = as_declared
        results.append(payload)

    stream.write("--- clause splices under the declared procedure (REPORTED, not asserted) ---\n")
    shapes = splice_all_clauses(spec_text, clauses)
    stream.write(json.dumps(shapes, indent=2, sort_keys=True) + "\n\n")

    stream.write("SELFTEST %s - %d/%d objects behaved as declared.\n"
                 % ("PASS" if all_as_declared else "FAIL",
                    sum(1 for r in results if r["as_declared"]), len(results)))
    return 0 if all_as_declared else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="PC-1: parse the amended EXP-WESOVOW-001 contract and assert "
                    "P1-P4.  Writes nothing anywhere.")
    parser.add_argument("--spec", required=True,
                        help="path to the FROZEN specification.yaml (read-only)")
    parser.add_argument("--amendment", required=True,
                        help="path to the amendment record carrying clause_1")
    parser.add_argument("--clause-1-file", default=None,
                        help="override clause_1's replacement text with this file's "
                             "contents, for exercising the control on a negative "
                             "object; it supplies BOTH the spliced text and the "
                             "expected content")
    parser.add_argument("--no-splice", action="store_true",
                        help="run against the spec AS GIVEN, applying no clause - "
                             "this is the unamended-frozen-file object")
    parser.add_argument("--splice-all-clauses", action="store_true",
                        help="additionally splice clauses 2, 3 and 4 and REPORT the "
                             "resulting key lists")
    parser.add_argument("--selftest", action="store_true",
                        help="exercise the control on the five declared objects")
    parser.add_argument("--superseded", default=None,
                        help="path to the superseded BATCH-752ef2 draft; required "
                             "by --selftest for negative object (b)")
    args = parser.parse_args(argv)

    if args.selftest:
        if not args.superseded:
            parser.error("--selftest requires --superseded")
        return selftest(args.spec, args.amendment, args.superseded, sys.stdout)

    spec_text = read_text(args.spec)
    clauses = load_clause_texts(args.amendment)
    clause_1_text = read_text(args.clause_1_file) if args.clause_1_file \
        else clauses["clause_1"]

    result = run_control(
        spec_text=spec_text,
        clause_1_text=clause_1_text,
        apply_clause_1=not args.no_splice,
        object_name=(args.clause_1_file or args.amendment)
        + (" [no-splice]" if args.no_splice else ""),
    )
    sys.stdout.write("object  : %s\n" % result.object_name)
    sys.stdout.write("result  : %s\n" % ("PASS" if result.passed else "FAIL"))
    if result.failed_assertion:
        sys.stdout.write("assertion that fired: %s\n" % result.failed_assertion)
    sys.stdout.write("message : %s\n" % result.message)
    sys.stdout.write("observations:\n%s\n"
                     % json.dumps(result.observations, indent=2, sort_keys=True))

    if args.splice_all_clauses:
        shapes = splice_all_clauses(spec_text, clauses)
        sys.stdout.write("clause splices (REPORTED, not asserted):\n%s\n"
                         % json.dumps(shapes, indent=2, sort_keys=True))

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
