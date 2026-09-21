#!/usr/bin/env python3
"""check_literals.py -- TASK-20260904-d66403 (RC-1 / RC-2).

Standalone: Python standard library only. No network. No numpy. No SageMath.
No import from experiments/. It NEVER executes
experiments/EXP-WESOVOW-001/cost_model.py -- that file is read as TEXT and the
PAPER_PAIRS literals are recovered by regex. Executing it is prohibited
absolutely by BATCH-dc1424 frozen_artifact_ruling (standing hazard O7/R2:
its default WESOVOW_RAW_PATH names a committed run directory).

Writes only inside this task directory (and only when --emit is passed).

CITATION PROHIBITION, RESTATED VERBATIM:
  The `P=512` crossover value and its `w=2^80` sign are **NOT
  citation-eligible**. This task does not lift that prohibition. Only a
  committed Coordinator decision on independently reviewed evidence can lift it.

PREDICATE EXTENSION, RESTATED VERBATIM:
  In addition to the retained sentence, a row of any EXP-WESOVOW-001
  reconciliation is NOT citation-eligible when either (a) the two anchors
  disagree in the SIGN of the baseline comparison at that row, or (b) the
  smaller |margin| across the two anchors at that row is below that field size's
  anchor gap |Delta log2 T_full + Delta log2 M / 2|.

APPLICATION TO THIS FILE: NEITHER FIRED. This script computes no crossover, no
T_DG or van Oorschot-Wiener baseline comparison, no margin and no speedup. Its
only comparisons are (RC-1) committed literal against paper-stated value and
(RC-2) anchor time against this model's own attained minimum log2 T_full.
Neither prohibition is lifted here and neither could be lifted by this task.
"""

import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))

COST_MODEL = os.path.join(REPO, "experiments", "EXP-WESOVOW-001", "cost_model.py")
PAPER = os.path.join(REPO, "inputs", "P13-WESOLOWSKI-2026", "paper_fulltext.md")
RAW = os.path.join(REPO, "experiments", "EXP-WESOVOW-001", "runs",
                   "RUN-WESOVOW-001", "raw-result.json")
LOCATORS = os.path.join(HERE, "locator_table.json")

FIELD_SIZES = [256, 384, 512, 576, 768]
QUANTITIES = ["log2_time", "log2_memory"]

# ---- pre-registered constants (frozen before Section 4.1 was opened) --------
TOLERANCE_BITS = 0.05
VERDICTS = ("faithful", "mis_transcribed", "undetermined")
COMPOSED = ("literals_mis_transcribed", "literals_faithful", "undetermined")


# ---------------------------------------------------------------- loaders ---
def read_committed_literals(path=COST_MODEL):
    """Recover PAPER_PAIRS from cost_model.py BY READING IT AS TEXT.

    Never imports and never executes it. Returns {log2p: {quantity: value}}.
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    out = {}
    pat = re.compile(r"^\s*(\d+)\s*:\s*\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)\s*,\s*$")
    inside = False
    for i, line in enumerate(lines, start=1):
        if line.startswith("PAPER_PAIRS = {"):
            inside = True
            continue
        if inside:
            if line.startswith("}"):
                break
            m = pat.match(line)
            if m:
                fs = int(m.group(1))
                out[fs] = {"log2_time": float(m.group(2)),
                           "log2_memory": float(m.group(3)),
                           "_line": i}
    return out


def load_locator_table(path=LOCATORS):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def paper_table(loc):
    """{log2p: {quantity: (paper_value_or_None, comparison_form, tolerance)}}"""
    out = {}
    for e in loc["entries"].values():
        out.setdefault(e["log2p"], {})[e["quantity"]] = (
            e["paper_value"], e["comparison_form"], e["tolerance_applied"])
    return out


def load_attained_minima(path=RAW):
    """Model's attained minimum log2 T_full, by EXACT key path
    per_field['log2p=<N>']['optimal']['log2T']."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    out = {}
    for fs in FIELD_SIZES:
        key = "log2p=%d" % fs
        try:
            out[fs] = raw["per_field"][key]["optimal"]["log2T"]
        except KeyError:
            out[fs] = None          # missing data stays missing
    return out


# ------------------------------------------------- pre-registered procedure --
def compare_value(paper_value, literal, comparison_form, tolerance=TOLERANCE_BITS):
    """The pre-registered per-value assignment rule. Returns a verdict."""
    if comparison_form in ("requires_derivation", "absent"):
        return "undetermined"
    if comparison_form != "direct":
        raise ValueError("unknown comparison_form %r" % comparison_form)
    if paper_value is None:
        return "undetermined"
    return "faithful" if abs(paper_value - literal) <= tolerance else "mis_transcribed"


def compose(per_value):
    """The pre-registered composition rule, in its declared precedence order."""
    vals = list(per_value.values())
    for v in vals:
        if v not in VERDICTS:
            raise ValueError("verdict outside the pre-registered vocabulary: %r" % v)
    if any(v == "mis_transcribed" for v in vals):
        return "literals_mis_transcribed"
    if vals and all(v == "faithful" for v in vals):
        return "literals_faithful"
    return "undetermined"


def run_procedure(literal_set, ptable):
    """Run the WHOLE pre-registered procedure on an arbitrary literal set."""
    per_value = {}
    for fs in FIELD_SIZES:
        for q in QUANTITIES:
            pv, form, tol = ptable[fs][q]
            per_value["log2p=%d|%s" % (fs, q)] = compare_value(
                pv, literal_set[fs][q], form, tol)
    return {"per_value": per_value, "composed": compose(per_value)}


# ------------------------------------------------------------- decoy sets ---
def decoy_shift(lits, delta=0.30):
    return {fs: {q: lits[fs][q] + delta for q in QUANTITIES} for fs in FIELD_SIZES}


def decoy_permute(lits):
    """256's pair -> 384, 384's -> 512, 512's -> 576, 576's -> 768, 768's -> 256."""
    order = FIELD_SIZES
    out = {}
    for i, fs in enumerate(order):
        src = order[i - 1]
        out[fs] = {q: lits[src][q] for q in QUANTITIES}
    return out


def decoy_null(lits):
    return {fs: {"log2_time": fs / 2.0, "log2_memory": 0.0} for fs in FIELD_SIZES}


def decoy_unit(lits, delta=6.0):
    """Memory expressed per 64-byte entry rather than per entry."""
    return {fs: {"log2_time": lits[fs]["log2_time"],
                 "log2_memory": lits[fs]["log2_memory"] + delta}
            for fs in FIELD_SIZES}


# ---------------------------------------------------------------- controls ---
def vc0_locator_completeness(loc, paper_path=PAPER):
    """VC-0. Every one of the ten numbers has a locator; for every `direct`
    value the quoted_text at the recorded line range is ACTUALLY the text at
    those lines in the paper AND contains the recorded paper_value.

    FAILURE BRANCH (reachable; exercised in main() on a mutated table): any
    entry whose quoted_text is not at its recorded lines, or does not contain
    the number attributed to it, or which has neither a paper locator nor a
    recorded failed search.
    """
    with open(paper_path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    problems = []
    entries = loc["entries"]
    expected = {"log2p=%d|%s" % (fs, q) for fs in FIELD_SIZES for q in QUANTITIES}
    missing = expected - set(entries)
    if missing:
        problems.append("entries missing for: %s" % sorted(missing))
    for key, e in sorted(entries.items()):
        pl = e.get("paper_locator")
        has_loc = bool(pl and pl.get("quoted_text"))
        has_search = bool(e.get("failed_search"))
        if not has_loc and not has_search:
            problems.append("%s: neither a paper locator nor a recorded failed search" % key)
            continue
        if not has_loc:
            continue
        seg = "\n".join(lines[pl["line_start"] - 1: pl["line_end"]])
        if pl["quoted_text"] not in seg:
            problems.append("%s: quoted_text is not the text at %s:%d-%d"
                            % (key, pl["path"], pl["line_start"], pl["line_end"]))
            continue
        if e["comparison_form"] == "direct":
            token = "2^%s" % _fmt(e["paper_value"])
            if token not in pl["quoted_text"]:
                problems.append("%s: quoted_text does not contain the attributed number %s"
                                % (key, token))
    return {"control": "VC-0", "passed": not problems, "problems": problems,
            "entries_checked": len(entries)}


def _fmt(x):
    s = ("%.10g" % x)
    return s if "." in s else s + ".0"


def vc1_decoy_rejection(lits, ptable):
    """VC-1. Run the SAME procedure on four decoy sets.
    FAILURE BRANCH (reachable): any decoy returning `literals_faithful`."""
    decoys = {
        "i_shift_plus_0.30": decoy_shift(lits, 0.30),
        "ii_cyclic_permutation": decoy_permute(lits),
        "iii_null_object": decoy_null(lits),
        "iv_unit_object_memory_plus_6.0": decoy_unit(lits, 6.0),
    }
    results = {}
    for name, ds in decoys.items():
        r = run_procedure(ds, ptable)
        results[name] = {
            "composed": r["composed"],
            "n_mis_transcribed": sum(1 for v in r["per_value"].values()
                                     if v == "mis_transcribed"),
            "n_faithful": sum(1 for v in r["per_value"].values() if v == "faithful"),
            "n_undetermined": sum(1 for v in r["per_value"].values()
                                  if v == "undetermined"),
        }
    committed = run_procedure(lits, ptable)
    accepted_faithful = [n for n, r in results.items()
                         if r["composed"] == "literals_faithful"]
    contradiction = (committed["composed"] == "literals_faithful"
                     and any(n.startswith(("i_", "ii_")) for n in accepted_faithful))
    return {"control": "VC-1",
            "passed": not accepted_faithful,
            "committed_set_composed": committed["composed"],
            "decoys": results,
            "decoys_returning_faithful": accepted_faithful,
            "self_contradiction": contradiction}


def vc1_non_constancy_probe(lits, ptable, delta=0.02):
    """NOT one of the four decoys. A procedure that rejects EVERYTHING would
    pass VC-1 while carrying no information, so probe that the procedure
    ACCEPTS a set differing by less than the tolerance."""
    near = {fs: {q: lits[fs][q] + delta for q in QUANTITIES} for fs in FIELD_SIZES}
    r = run_procedure(near, ptable)
    return {"probe": "non_constancy", "delta_bits": delta,
            "composed": r["composed"],
            "procedure_is_constant_rejector": r["composed"] != "literals_faithful"}


def vc2_resolution(lits, ptable, ladder=(0.5, 0.2, 0.1, 0.05, 0.02)):
    """VC-2. Per value, the SMALLEST delta in the ladder at which the procedure
    still returns `mis_transcribed` for that value.
    FAILURE BRANCH (reachable): any `direct` value where delta = 0.2 does not
    yield `mis_transcribed`."""
    per_value = {}
    for fs in FIELD_SIZES:
        for q in QUANTITIES:
            key = "log2p=%d|%s" % (fs, q)
            pv, form, tol = ptable[fs][q]
            row = {}
            for d in ladder:
                row[str(d)] = compare_value(pv, lits[fs][q] + d, form, tol)
            flagged = [d for d in ladder if row[str(d)] == "mis_transcribed"]
            per_value[key] = {
                "comparison_form": form,
                "ladder": row,
                "smallest_delta_still_mis_transcribed": (min(flagged) if flagged else None),
                "distinguishes_0.2": row["0.2"] == "mis_transcribed",
            }
    blind = [k for k, v in per_value.items()
             if v["comparison_form"] == "direct" and not v["distinguishes_0.2"]]
    return {"control": "VC-2", "passed": not blind,
            "values_blind_at_0.2_bits": blind, "per_value": per_value}


def rc2_reachability(anchor_times, attained):
    """RC-2. anchor_time >= attained minimum -> `reachable`, else `off_curve`.
    Both branches are reachable and both are exercised in main()."""
    rows = {}
    for fs in FIELD_SIZES:
        a, m = anchor_times.get(fs), attained.get(fs)
        if a is None or m is None:
            rows[fs] = {"verdict": "not_attempted",
                        "reason": "a needed committed value is absent"}
            continue
        d = a - m
        rows[fs] = {"anchor_log2T": a, "attained_min_log2T": m,
                    "signed_difference_anchor_minus_min": d,
                    "verdict": "reachable" if d >= 0.0 else "off_curve"}
    return {"control": "RC-2", "rows": rows}


# -------------------------------------------------------------------- main ---
def main():
    lits_raw = read_committed_literals()
    lits = {fs: {"log2_time": lits_raw[fs]["log2_time"],
                 "log2_memory": lits_raw[fs]["log2_memory"]} for fs in FIELD_SIZES}
    loc = load_locator_table()
    ptable = paper_table(loc)
    attained = load_attained_minima()

    out = {}
    out["committed_literal_lines"] = {fs: lits_raw[fs]["_line"] for fs in FIELD_SIZES}
    out["rc1"] = run_procedure(lits, ptable)

    out["vc0_real"] = vc0_locator_completeness(loc)
    # VC-0 failure branch, exercised on a CONCRETE mutated input: file the
    # log2p=384 row's quoted text under the log2p=256 time entry.
    import copy
    mutated = copy.deepcopy(loc)
    mutated["entries"]["log2p=256|log2_time"]["paper_locator"]["quoted_text"] = \
        loc["entries"]["log2p=384|log2_time"]["paper_locator"]["quoted_text"]
    out["vc0_mutated_input"] = vc0_locator_completeness(mutated)

    out["vc1"] = vc1_decoy_rejection(lits, ptable)
    out["vc1_non_constancy_probe"] = vc1_non_constancy_probe(lits, ptable)
    out["vc2"] = vc2_resolution(lits, ptable)

    anchors = {fs: lits[fs]["log2_time"] for fs in FIELD_SIZES}
    out["rc2_real"] = rc2_reachability(anchors, attained)
    # RC-2 direction (a): the model's OWN optima must all come back reachable.
    out["rc2_control_a_model_own_optima"] = rc2_reachability(dict(attained), attained)
    # RC-2 direction (b): synthetic anchors 5.0 bits BELOW the attained minimum.
    below = {fs: (attained[fs] - 5.0 if attained[fs] is not None else None)
             for fs in FIELD_SIZES}
    out["rc2_control_b_five_bits_below"] = rc2_reachability(below, attained)

    json.dump(out, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
