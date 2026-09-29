"""N2R dual-convention height reconciliation for EXP-ECRANK-73275e v2 (R12/R14).

Pre-registered by the amendment (n2r_reconciliation). The executor records
BOTH exact predicates VERBATIM from the frozen source into the raw result
BEFORE any count is reported, then reports N_6 (or N_8) per H under:
  - Convention A (A_recorded_r_height): h_A = max_i rat_height(r_i) over the
    full r vector of the found instance -- the convention under which v1
    reported counts.
  - Convention B (B_solved_free_coordinate_height): h_B = rat_height(t*) of
    the solved free coordinate (the kept root of the n=6 univariate
    quadratic, in canonical minimal form) -- the search-box reading of
    HEUR-1's H.

The decade ratios under BOTH conventions are frozen DESCRIPTIVE tail_checks:
reported, never interpreted. No branch is selected here.

For n=6 the free coordinate is t with g = x + t, so r_i = t + b_i and, since
b_0 = 0 (affine normal form), t = r_0 exactly. h_B = rat_height(r_0).
"""

import os
from fractions import Fraction as Fr

import ecrank_engine as E
import construct


def rat_height(r):
    # VERBATIM predicate (Convention A and B both use this height function),
    # copied from source/construct.py lines 23-24.
    return max(abs(r.numerator), r.denominator)


def _read_lines(path):
    with open(path) as f:
        return f.read().splitlines()


def verbatim_predicates(repo_root):
    """Extract the exact predicate lines verbatim from the frozen source.

    Returns a dict with the rat_height definition and the instance
    classification lines for each convention, quoted verbatim.
    """
    src = os.path.join(repo_root, "experiments", "EXP-ECRANK-73275e", "source")
    construct_lines = _read_lines(os.path.join(src, "construct.py"))

    # rat_height definition (construct.py)
    rat_height_lines = []
    for i, ln in enumerate(construct_lines):
        if ln.startswith("def rat_height("):
            rat_height_lines = [construct_lines[i], construct_lines[i + 1]]
            break

    # Convention A classification: the r-height filter in solve_n6 and the
    # cumulative count in construct_arm.
    conv_a_filter = []
    for i, ln in enumerate(construct_lines):
        if "h = max(rat_height(ri) for ri in r)" in ln:
            conv_a_filter = [construct_lines[i], construct_lines[i + 1],
                             construct_lines[i + 2], construct_lines[i + 3]]
            break
    conv_a_count = []
    for i, ln in enumerate(construct_lines):
        if "counts[int(H)] += 1" in ln:
            conv_a_count = [construct_lines[i - 2], construct_lines[i - 1],
                            construct_lines[i]]
            break

    # Convention B classification: this module's h_B definition (verbatim
    # from the frozen v2 source). Match the actual function definition line
    # (starts with 'def h_B_from_instance(' after stripping), not the
    # extraction code that quotes the name.
    n2r_lines = _read_lines(os.path.join(
        repo_root, "experiments", "EXP-ECRANK-73275e", "source-v2", "n2r.py"))
    conv_b_lines = []
    for i, ln in enumerate(n2r_lines):
        if ln.lstrip().startswith("def h_B_from_instance("):
            conv_b_lines = n2r_lines[i:i + 10]
            break

    return {
        "rat_height_definition": {
            "source": "source/construct.py",
            "lines": rat_height_lines,
        },
        "convention_A_recorded_r_height": {
            "definition": "h_A = max_i rat_height(r_i) over the full r vector",
            "filter_lines_source": "source/construct.py (solve_n6)",
            "filter_lines": conv_a_filter,
            "count_lines_source": "source/construct.py (construct_arm)",
            "count_lines": conv_a_count,
        },
        "convention_B_solved_free_coordinate_height": {
            "definition": ("h_B = rat_height(t*) of the solved free "
                           "coordinate; for n=6, t = r_0 (b_0 = 0)"),
            "lines_source": "source-v2/n2r.py (h_B_from_instance)",
            "lines": conv_b_lines,
        },
    }


def h_B_from_instance(inst):
    """Convention B height: rat_height of the solved free coordinate.

    For n=6, g = x + t, r_i = t + b_i, b_0 = 0, so t = r_0 exactly.
    h_B = rat_height(r_0), r_0 in canonical minimal form (a Fraction).
    """
    r = [Fr(x) for x in inst["r"]]
    b = [Fr(x) for x in inst["b"]]
    t = r[0] - b[0]  # = r[0] since b[0] = 0
    return rat_height(t)


def h_A_from_instance(inst):
    """Convention A height: the recorded r_height (max over the full r vector)."""
    return inst["r_height"]


def membership_level(h, H_levels):
    """The largest H in H_levels with h <= H, or None if h exceeds the top box."""
    level = None
    for H in sorted(H_levels):
        if h <= H:
            level = int(H)
    return level


def reconcile(found, H_levels):
    """Build the N2R tables from a list of found-instance records.

    found: list of construct_arm 'found' records (each with 'instance' and
    'r_height'). Returns a dict with the per-instance cross-tabulation, the
    cumulative counts under both conventions, and the decade ratios.
    DESCRIPTIVE only; no interpretation.
    """
    H_sorted = sorted(int(H) for H in H_levels)
    cross_tab = []
    nA = {H: 0 for H in H_sorted}
    nB = {H: 0 for H in H_sorted}
    out_of_box_B = 0
    for rec in found:
        inst = rec["instance"]
        hA = h_A_from_instance(inst)
        hB = h_B_from_instance(inst)
        lvlA = membership_level(hA, H_sorted)
        lvlB = membership_level(hB, H_sorted)
        if lvlB is None:
            out_of_box_B += 1
        cross_tab.append({
            "b_index": rec.get("b_index"),
            "h_A": hA,
            "h_B": hB,
            "membership_level_A": lvlA,
            "membership_level_B": lvlB,
        })
        for H in H_sorted:
            if hA <= H:
                nA[H] += 1
            if hB <= H:
                nB[H] += 1
    return {
        "H_levels": H_sorted,
        "n_instances": len(found),
        "cross_tabulation": cross_tab,
        "N_per_H_convention_A": {str(H): nA[H] for H in H_sorted},
        "N_per_H_convention_B": {str(H): nB[H] for H in H_sorted},
        "out_of_box_B_observations": out_of_box_B,
        "decade_ratios": _decade_ratios(H_sorted, nA, nB),
    }


def _decade_ratios(H_sorted, nA, nB):
    """Smallest and largest H-decade ratios under each convention, plus the
    two-decade totals. DESCRIPTIVE (frozen tail_check); no pass/fail band."""
    out = {}
    for name, n in (("convention_A", nA), ("convention_B", nB)):
        ratios = []
        for lo, hi in zip(H_sorted[:-1], H_sorted[1:]):
            if n[lo] > 0:
                ratios.append({"from_H": lo, "to_H": hi,
                               "N_from": n[lo], "N_to": n[hi],
                               "ratio": n[hi] / n[lo]})
        entry = {"decade_ratios": ratios}
        if ratios:
            entry["smallest_ratio"] = min(r["ratio"] for r in ratios)
            entry["largest_ratio"] = max(r["ratio"] for r in ratios)
        if len(H_sorted) >= 3 and n[H_sorted[0]] > 0:
            entry["two_decade_total_ratio"] = (n[H_sorted[-1]] /
                                               n[H_sorted[0]])
        entry["exponent_plus2_prediction_per_decade"] = 100
        out[name] = entry
    return out
