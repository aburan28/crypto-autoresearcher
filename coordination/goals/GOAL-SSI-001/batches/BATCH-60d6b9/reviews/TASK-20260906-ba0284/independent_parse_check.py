#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""independent_parse_check.py -- TASK-20260906-ba0284, GOAL-SSI-001, BATCH-60d6b9.

THE VALIDATOR'S OWN SPLICE-AND-PARSE. Written and run BEFORE
tasks/TASK-20260906-ee372e/amendment_parse_control.py or its report were opened
(attested; see validation_report.yaml review_attestation.reading_order).

WHAT IT IS FOR
--------------
Joint J1 of coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/review_plan.yaml.
It answers, from committed bytes and with no dependence on any producer
implementation:

  * does experiments/EXP-WESOVOW-001/specification.yaml with the REDRAFTED
    clause_1 spliced over lines 39-40 PARSE, and is experiment.metrics then a
    7-element list whose item 5 is a single-key mapping carrying the
    replacement's own key;
  * does the same file with the SUPERSEDED clause_1 (BATCH-752ef2
    TASK-20260905-28c89d) fail to parse -- tried at three candidate splice
    columns, because the superseded draft declared no splice procedure;
  * do the redrafted clause_2, clause_3 and clause_4 splice and parse, alone and
    all-four-together, and what key lists result;
  * is the redrafted clause_1 text content-identical to the superseded one after
    normalising leading whitespace, and do the two parse to the same VALUE.

It also constructs, for joint J2, the negative shape objects the review plan
names (a metrics list of length 6, one of length 8, and one whose item 5 is a
plain string), so the same objects can be fed to the producer's control.

STANDING CONSTRAINTS THIS FILE HONOURS
--------------------------------------
* experiments/ and inputs/ are READ-ONLY. Every amended file exists only as a
  Python string in memory. Nothing is written anywhere by this script.
* cost_model.py is never imported and never executed.
* sys.dont_write_bytecode is set before any import that could touch a
  snapshot-bound directory, so no __pycache__ is created there.
* No PAPER_PAIRS value, delta, crossover, margin, sign or speedup is computed,
  restated or printed. The prior text of metrics[5] is handled as opaque bytes
  and is only ever compared, never evaluated or reported as a quantity.

USAGE
-----
    PYTHONDONTWRITEBYTECODE=1 python3 independent_parse_check.py [--json]

Exit status is 0 when every check ran, 1 when a check could not be run at all
(a missing input). It is deliberately NOT an assertion harness: this script
REPORTS what happened; the verdicts live in validation_report.yaml.
"""

import sys

sys.dont_write_bytecode = True  # before any further import

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

import yaml  # noqa: E402

# ---------------------------------------------------------------------------
# Locators. Repository-relative, resolved from this file's own location so the
# script is re-runnable from any working directory.
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([os.pardir] * 7)))

SPEC = os.path.join(REPO, "experiments", "EXP-WESOVOW-001", "specification.yaml")
REDRAFT = os.path.join(
    REPO,
    "coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/tasks/"
    "TASK-20260906-ee372e/protocol_amendment_redraft.yaml",
)
SUPERSEDED = os.path.join(
    REPO,
    "coordination/goals/GOAL-SSI-001/batches/BATCH-752ef2/tasks/"
    "TASK-20260905-28c89d/protocol_amendment_draft.yaml",
)

# The anchor the amendment's own splice_procedure asserts before splicing
# clause_1. Checked here independently rather than trusted.
CLAUSE1_FIRST_LINE_PREFIX = "  - crossover memory log2(w*) per (p, overhead c)"
# Search anchors for the two append sites, recomputed rather than hard-coded as
# line numbers, because each applied clause moves every line below it.
ANCHOR_END_OF_MODEL_DEFINITION = "  scenario_definitions:"
ANCHOR_END_OF_CONTROLS_0 = "  - id: C2-baseline-consistency"

CLAUSE1_LINES_1BASED = (39, 40)


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def indent_block(text, columns):
    """Prepend `columns` spaces to every non-empty line. Empty lines stay empty
    so no trailing whitespace is introduced."""
    out = []
    for line in text.split("\n"):
        out.append((" " * columns + line) if line.strip() else line)
    return "\n".join(out)


def strip_trailing_blank(lines):
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def replace_lines(spec_lines, first_1based, last_1based, block_lines):
    """Return a new line list with [first..last] (1-based, inclusive) replaced."""
    i, j = first_1based - 1, last_1based
    return spec_lines[:i] + list(block_lines) + spec_lines[j:]


def insert_before_anchor(spec_lines, anchor, block_lines):
    """Insert block immediately before the first line equal to `anchor`."""
    for idx, line in enumerate(spec_lines):
        if line == anchor:
            return spec_lines[:idx] + list(block_lines) + spec_lines[idx:], idx
    raise LookupError("anchor not found: %r" % anchor)


class _DuplicateKeyRecordingLoader(yaml.SafeLoader):
    """yaml.safe_load silently keeps the LAST of two identical mapping keys, so a
    clause that re-adds an existing key would parse cleanly and shadow it. A
    shape-only check cannot see that. This loader records every collision."""

    duplicates = None  # set per parse


def _construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            loader.duplicates.append(
                {"key": str(key), "line": key_node.start_mark.line + 1}
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_DuplicateKeyRecordingLoader.construct_mapping = _construct_mapping


def duplicate_keys(text):
    """Return the list of duplicate mapping keys, or None if the text does not
    parse at all."""
    loader = _DuplicateKeyRecordingLoader(text)
    loader.duplicates = []
    try:
        loader.get_single_data()
    except Exception:  # noqa: BLE001
        return None
    finally:
        loader.dispose()
    return loader.duplicates


def structural_diff(a, b, path=""):
    """Every difference between two parsed documents, as (path, kind) pairs.
    Used to check that the amendment changes EXACTLY what it says and nothing
    else -- a check no shape assertion can make."""
    out = []
    if type(a) is not type(b):
        return [(path, "TYPE %s -> %s" % (type(a).__name__, type(b).__name__))]
    if isinstance(a, dict):
        for k in a:
            if k not in b:
                out.append((path + "." + str(k), "REMOVED"))
            else:
                out.extend(structural_diff(a[k], b[k], path + "." + str(k)))
        for k in b:
            if k not in a:
                out.append((path + "." + str(k), "ADDED"))
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path, "LENGTH %d -> %d" % (len(a), len(b))))
        for i, (u, v) in enumerate(zip(a, b)):
            out.extend(structural_diff(u, v, path + "[%d]" % i))
    elif a != b:
        out.append((path, "VALUE CHANGED"))
    return out


def parse_report(text):
    """Parse and describe. Never raises on a YAML error; records it."""
    rec = {
        "parses": None,
        "error_class": None,
        "error_message": None,
        "duplicate_keys": None,
        "metrics_len": None,
        "metrics_types": None,
        "metrics_5_type": None,
        "metrics_5_keys": None,
        "metrics_5_value_sha256": None,
        "model_definition_keys": None,
        "controls_0_keys": None,
    }
    try:
        doc = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 - reporting, not handling
        rec["parses"] = False
        rec["error_class"] = type(exc).__name__
        rec["error_message"] = " ".join(str(exc).split())
        return rec
    rec["parses"] = True
    rec["duplicate_keys"] = duplicate_keys(text)
    try:
        exp = doc["experiment"]
    except Exception:  # noqa: BLE001
        rec["error_message"] = "parsed but has no top-level `experiment` key"
        return rec
    m = exp.get("metrics")
    if isinstance(m, list):
        rec["metrics_len"] = len(m)
        rec["metrics_types"] = [type(x).__name__ for x in m]
        if len(m) > 5:
            item = m[5]
            rec["metrics_5_type"] = type(item).__name__
            if isinstance(item, dict):
                rec["metrics_5_keys"] = list(item.keys())
                if len(item) == 1:
                    val = list(item.values())[0]
                    rec["metrics_5_value_sha256"] = hashlib.sha256(
                        ("" if val is None else str(val)).encode("utf-8")
                    ).hexdigest()
            elif isinstance(item, str):
                rec["metrics_5_value_sha256"] = hashlib.sha256(
                    item.encode("utf-8")
                ).hexdigest()
    md = exp.get("model_definition")
    if isinstance(md, dict):
        rec["model_definition_keys"] = list(md.keys())
    ctrls = exp.get("controls")
    if isinstance(ctrls, list) and ctrls and isinstance(ctrls[0], dict):
        rec["controls_0_keys"] = list(ctrls[0].keys())
    return rec


# ---------------------------------------------------------------------------
# Splices
# ---------------------------------------------------------------------------
def splice_clause_1(spec_lines, text, columns):
    block = strip_trailing_blank(indent_block(text, columns).split("\n"))
    return replace_lines(spec_lines, *CLAUSE1_LINES_1BASED, block_lines=block)


def splice_clause_2(spec_lines, text, columns=4):
    block = strip_trailing_blank(indent_block(text, columns).split("\n"))
    new, _ = insert_before_anchor(spec_lines, ANCHOR_END_OF_MODEL_DEFINITION, block)
    return new


def splice_clauses_3_4(spec_lines, text3, text4, columns=4):
    block = strip_trailing_blank(indent_block(text3, columns).split("\n"))
    block += strip_trailing_blank(indent_block(text4, columns).split("\n"))
    new, _ = insert_before_anchor(spec_lines, ANCHOR_END_OF_CONTROLS_0, block)
    return new


def splice_one(spec_lines, which, texts):
    if which == "clause_1":
        return splice_clause_1(spec_lines, texts["clause_1"], 2)
    if which == "clause_2":
        return splice_clause_2(spec_lines, texts["clause_2"], 4)
    if which == "clause_3":
        return splice_clauses_3_4(spec_lines, texts["clause_3"], "", 4)
    if which == "clause_4":
        return splice_clauses_3_4(spec_lines, "", texts["clause_4"], 4)
    raise ValueError(which)


def splice_all_bottom_up(spec_lines, texts):
    """clause_4/clause_3 first, then clause_2, then clause_1 -- so no anchor of a
    not-yet-applied clause has moved. Anchors are searched, not counted."""
    lines = splice_clauses_3_4(spec_lines, texts["clause_3"], texts["clause_4"], 4)
    lines = splice_clause_2(lines, texts["clause_2"], 4)
    lines = splice_clause_1(lines, texts["clause_1"], 2)
    return lines


# ---------------------------------------------------------------------------
# J2 negative shape objects, built here so the producer's control can be run on
# exactly the objects this script reports on.
# ---------------------------------------------------------------------------
def negative_metrics_len(spec_lines, texts, delta):
    """Splice the redrafted clause_1 and then add (delta>0) or drop (delta<0)
    whole metrics items, so the file PARSES but metrics has length 7+delta."""
    lines = splice_clause_1(spec_lines, texts["clause_1"], 2)
    if delta > 0:
        # insert an extra plain-scalar item directly after the metrics header
        idx = lines.index("  metrics:")
        extra = ["  - an extra metrics item that nobody ordered"] * delta
        return lines[:idx + 1] + extra + lines[idx + 1:]
    # delta < 0: drop the first metrics item (a single plain scalar line)
    idx = lines.index("  metrics:")
    return lines[: idx + 1] + lines[idx + 1 - delta:]


def negative_metrics_5_plain_string(spec_lines):
    """Replace lines 39-40 with a single folded-scalar item, so the file parses
    and metrics still has 7 items but item 5 is a plain STRING. This is the
    `>-` variant the redraft's rt_1_repair_note explicitly REJECTS."""
    block = [
        "  - >-",
        "    crossover memory log2(w*) per (p, overhead c) - the memory budget, in",
        "    table entries, at which the overhead-inflated vOW time of a given",
        "    (p, c) scenario meets the baseline fixed by control C2.",
    ]
    return replace_lines(spec_lines, 39, 40, block)


# ---------------------------------------------------------------------------
def build_objects():
    """Return (objects, meta). Each object is (name, text, known_conclusion)."""
    spec_text = read_text(SPEC)
    spec_lines = spec_text.split("\n")

    redraft = yaml.safe_load(read_text(REDRAFT))["amendment"]
    superseded = yaml.safe_load(read_text(SUPERSEDED))["amendment"]

    rtexts = {
        k: redraft["proposed_replacement"][k]["replacement_text_in_full"]
        for k in ("clause_1", "clause_2", "clause_3", "clause_4")
    }
    stexts = {
        k: superseded["proposed_replacement"][k]["replacement_text_in_full"]
        for k in ("clause_1", "clause_2", "clause_3", "clause_4")
    }

    meta = {
        "spec_sha256": sha256_file(SPEC),
        "redraft_sha256": sha256_file(REDRAFT),
        "superseded_sha256": sha256_file(SUPERSEDED),
        "spec_line_count": len(spec_lines),
        "spec_line_39": spec_lines[38],
        "spec_line_40": spec_lines[39],
        "clause1_anchor_asserted_by_amendment": CLAUSE1_FIRST_LINE_PREFIX,
        "clause1_anchor_holds": spec_lines[38].startswith(CLAUSE1_FIRST_LINE_PREFIX),
        "redraft_declared_splice_indents": {
            k: redraft["proposed_replacement"][k].get("splice_indent")
            for k in ("clause_1", "clause_2", "clause_3", "clause_4")
        },
        "superseded_declared_splice_indents": {
            k: superseded["proposed_replacement"][k].get("splice_indent")
            for k in ("clause_1", "clause_2", "clause_3", "clause_4")
        },
    }

    # --- content identity of the two clause_1 texts, whitespace-normalised ---
    def norm(t):
        return "\n".join(" ".join(line.split()) for line in t.split("\n")).strip()

    meta["clause_1_content_identical_after_whitespace_normalisation"] = (
        norm(rtexts["clause_1"]) == norm(stexts["clause_1"])
    )
    meta["clause_1_byte_identical"] = rtexts["clause_1"] == stexts["clause_1"]
    meta["clause_1_redraft_sha256"] = hashlib.sha256(
        rtexts["clause_1"].encode("utf-8")
    ).hexdigest()
    meta["clause_1_superseded_sha256"] = hashlib.sha256(
        stexts["clause_1"].encode("utf-8")
    ).hexdigest()
    meta["clause_1_per_line_leading_spaces_redraft"] = [
        len(l) - len(l.lstrip(" ")) for l in rtexts["clause_1"].split("\n")
    ]
    meta["clause_1_per_line_leading_spaces_superseded"] = [
        len(l) - len(l.lstrip(" ")) for l in stexts["clause_1"].split("\n")
    ]
    for k in ("clause_2", "clause_3", "clause_4"):
        meta["%s_byte_identical_to_superseded" % k] = rtexts[k] == stexts[k]

    objects = []

    objects.append(
        ("O0_unamended_frozen_file", spec_text,
         "no clause applied; 'the amendment has been applied' is KNOWN FALSE")
    )
    objects.append(
        ("O1_redraft_clause_1_only",
         "\n".join(splice_one(spec_lines, "clause_1", rtexts)),
         "must parse; metrics len 7; metrics[5] single-key mapping")
    )
    for col in (0, 2, 4):
        objects.append(
            ("O2_superseded_clause_1_at_col_%d" % col,
             "\n".join(splice_clause_1(spec_lines, stexts["clause_1"], col)),
             "'this amended file parses' is KNOWN FALSE (two prior sessions)")
        )
    objects.append(
        ("O3_redraft_clause_2_only",
         "\n".join(splice_one(spec_lines, "clause_2", rtexts)),
         "must parse; model_definition gains vow_charging_law")
    )
    objects.append(
        ("O4_redraft_clause_3_only",
         "\n".join(splice_one(spec_lines, "clause_3", rtexts)),
         "must parse; controls[0] gains anchor_semantics")
    )
    objects.append(
        ("O5_redraft_clause_4_only",
         "\n".join(splice_one(spec_lines, "clause_4", rtexts)),
         "must parse; controls[0] gains anchor_reachability")
    )
    objects.append(
        ("O6_redraft_all_four_bottom_up",
         "\n".join(splice_all_bottom_up(spec_lines, rtexts)),
         "POSITIVE CONTROL: must parse with all declared shape and keys")
    )
    objects.append(
        ("O7_metrics_len_6", "\n".join(negative_metrics_len(spec_lines, rtexts, -1)),
         "parses but metrics length is 6; 'shape preserved' KNOWN FALSE")
    )
    objects.append(
        ("O8_metrics_len_8", "\n".join(negative_metrics_len(spec_lines, rtexts, +1)),
         "parses but metrics length is 8; 'shape preserved' KNOWN FALSE")
    )
    objects.append(
        ("O9_metrics_5_plain_string",
         "\n".join(negative_metrics_5_plain_string(spec_lines)),
         "parses, metrics length 7, but metrics[5] is a STRING; KNOWN FALSE")
    )
    return objects, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--dump", metavar="NAME",
                    help="print the spliced text of one object to stdout and exit")
    args = ap.parse_args()

    for p in (SPEC, REDRAFT, SUPERSEDED):
        if not os.path.exists(p):
            sys.stderr.write("missing input: %s\n" % p)
            return 1

    objects, meta = build_objects()

    if args.dump:
        for name, text, _ in objects:
            if name == args.dump:
                sys.stdout.write(text)
                return 0
        sys.stderr.write("no such object: %s\n" % args.dump)
        return 1

    results = []
    for name, text, known in objects:
        rec = parse_report(text)
        rec["object"] = name
        rec["known_conclusion"] = known
        rec["object_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        results.append(rec)

    # The check no shape assertion can make: what, exactly, does applying all
    # four clauses change in the PARSED document relative to the frozen file?
    texts = {name: text for name, text, _ in objects}
    diff = structural_diff(
        yaml.safe_load(texts["O0_unamended_frozen_file"]),
        yaml.safe_load(texts["O6_redraft_all_four_bottom_up"]),
    )
    meta["structural_diff_unamended_vs_all_four"] = [
        {"path": p, "kind": k} for p, k in diff
    ]

    if args.json:
        print(json.dumps({"meta": meta, "results": results}, indent=2, sort_keys=True))
        return 0

    print("independent_parse_check.py -- TASK-20260906-ba0284")
    print("spec sha256      : %s" % meta["spec_sha256"])
    print("redraft sha256   : %s" % meta["redraft_sha256"])
    print("superseded sha256: %s" % meta["superseded_sha256"])
    print("clause_1 anchor at line 39 holds: %s" % meta["clause1_anchor_holds"])
    print("clause_1 redraft vs superseded, byte identical      : %s"
          % meta["clause_1_byte_identical"])
    print("clause_1 redraft vs superseded, identical modulo ws : %s"
          % meta["clause_1_content_identical_after_whitespace_normalisation"])
    print("clause_1 leading spaces, redraft   : %s"
          % meta["clause_1_per_line_leading_spaces_redraft"])
    print("clause_1 leading spaces, superseded: %s"
          % meta["clause_1_per_line_leading_spaces_superseded"])
    for k in ("clause_2", "clause_3", "clause_4"):
        print("%s byte-identical to superseded: %s"
              % (k, meta["%s_byte_identical_to_superseded" % k]))
    print("")
    for rec in results:
        print("=" * 74)
        print("OBJECT   : %s" % rec["object"])
        print("known    : %s" % rec["known_conclusion"])
        print("parses   : %s" % rec["parses"])
        if not rec["parses"]:
            print("error    : %s: %s" % (rec["error_class"], rec["error_message"]))
            continue
        print("metrics  : len=%s types=%s" % (rec["metrics_len"], rec["metrics_types"]))
        print("metrics5 : type=%s keys=%s" % (rec["metrics_5_type"], rec["metrics_5_keys"]))
        print("md keys  : %s" % (rec["model_definition_keys"],))
        print("C1 keys  : %s" % (rec["controls_0_keys"],))
        print("dup keys : %s" % (rec["duplicate_keys"],))
    print("=" * 74)
    print("STRUCTURAL DIFF, unamended frozen file -> all four clauses applied:")
    for entry in meta["structural_diff_unamended_vs_all_four"]:
        print("  %-8s %s" % (entry["kind"], entry["path"]))
    print("  total differences: %d"
          % len(meta["structural_diff_unamended_vs_all_four"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
