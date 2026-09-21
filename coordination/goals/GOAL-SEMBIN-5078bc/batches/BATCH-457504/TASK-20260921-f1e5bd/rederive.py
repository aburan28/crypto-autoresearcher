#!/usr/bin/env python3
"""Blind re-derivation of d_F4, closure_D and their separation for J-3 of
review round REVIEW-SEMBIN-20260921-457504 (TASK-20260921-f1e5bd).

This is a RE-DERIVATION, not a replication.  It was written from

  * Semaev's definition of d_F4 and "step degree"
    (inputs/SEMAEV-2015-310/paper_fulltext.md lines 486, 629-636), and
  * the frozen contract experiments/EXP-SEMBIN-c2c312/specification.yaml,

without reading experiments/EXP-SEMBIN-c2c312/code/summarize.py, the run's
summary.json / results-table.json / task-report.md / NOTES-*, or the `result`
and `controls` blocks of its manifest.yaml.

BLINDNESS ENFORCEMENT
---------------------
The per-cell records the task directs us to read (worker*/cells/results.jsonl)
already carry the producer's *derived* scalars -- d_F4_naive, d_F4_semaev,
d_F4_last_productive_round, d_F4_partial_max_deg_seen, closure_D,
D_macaulay_rank_statistic, f4_empty_step_degrees, f4_step_count -- alongside
the primitive profiles.  A re-derivation that read those would be worthless.

So every record is passed through `primitive_view()` before anything else
touches it.  That function DROPS the producer-derived keys listed in
PRODUCER_DERIVED and returns only the whitelisted primitives.  The derivation
code below can therefore not read a producer scalar even by accident: the key
is gone from the dict it is handed.  `--audit-blindness` prints what was
dropped.

For the F4 statistic the script does not even use the record's `rounds` array
(itself a producer parse of the engine output): it parses the raw msolve logs
under worker*/cells/instances/*.msolve.log with its own parser.  The record's
`rounds` array is read only inside `crosscheck_producer_trace_parse()`, which
is reported separately and feeds nothing in the derivation.

Usage
-----
    python3 rederive.py \
        --run-dir experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f \
        --out rederived.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict

WORKERS = ["workerA", "workerB", "workerC", "heavy", "heavy_closure"]

# ---------------------------------------------------------------------------
# Blindness: the producer's derived scalars, dropped before any derivation.
# ---------------------------------------------------------------------------

PRODUCER_DERIVED = {
    "d_F4_naive",
    "d_F4_semaev",
    "d_F4_last_productive_round",
    "d_F4_partial_max_deg_seen",
    "closure_D",
    "D_macaulay_rank_statistic",
    "f4_empty_step_degrees",
    "f4_step_count",
    # per_D-entry level
    "verdict",
    "verdict_basis",
    "deficit_vs_semiregular",
    "sr_pred_rank",
    "sr_HF",
}

# `rounds` is the producer's parse of the engine log.  It is quarantined: the
# derivation uses our own parse of the .msolve.log, and `rounds` is surfaced
# only to the cross-check function.
QUARANTINED = {"rounds"}

IDENTITY_KEYS = [
    "instance_id", "instrument", "family", "group", "structure", "status",
    "unreached_reason", "exit_code", "engine", "engine_version",
    "field_equation_convention", "n", "m", "t", "k", "N", "n_equations",
    "subspace", "B_mode", "seed", "draw", "system_sha256", "input_sha256",
    "msolve_input_sha256", "stdout_sha256", "max_generator_degree",
    "input_max_degree", "ideal_is_unit", "quotient_dimension", "basis_length",
    "wall_s", "peak_rss_bytes", "per_D",
]

CLOSURE_PRIMITIVES = [
    "D", "status", "reason", "contains_one", "standard_monomials",
    "standard_monomials_exceeds_cap", "solutions", "solutions_source",
    "basis_leading_degree_counts", "basis_lm_sha256", "rank", "ncols",
    "max_rows_seen", "iterations", "field_equation_convention", "wall_s", "rc",
]

MACAULAY_PRIMITIVES = [
    "D", "status", "reason", "rank", "rows", "cols", "contains_one", "wall_s",
]

_DROPPED: Counter = Counter()


def primitive_view(rec: dict) -> dict:
    """Return the record with every producer-derived / quarantined key removed."""
    out = {}
    for key, val in rec.items():
        if key in PRODUCER_DERIVED or key in QUARANTINED:
            _DROPPED[key] += 1
            continue
        if key == "per_D" and isinstance(val, list):
            allowed = (CLOSURE_PRIMITIVES if rec.get("instrument") == "closure_certificate"
                       else MACAULAY_PRIMITIVES)
            cleaned = []
            for entry in val:
                e = {}
                for k2, v2 in entry.items():
                    if k2 in PRODUCER_DERIVED:
                        _DROPPED[f"per_D.{k2}"] += 1
                        continue
                    if k2 in allowed or k2 == "instrument":
                        e[k2] = v2
                    else:
                        _DROPPED[f"per_D.unlisted.{k2}"] += 1
                cleaned.append(e)
            out[key] = cleaned
        elif key in IDENTITY_KEYS:
            out[key] = val
        else:
            _DROPPED[f"unlisted.{key}"] += 1
    return out


# ---------------------------------------------------------------------------
# Our own parser for msolve's F4 verbosity.
# ---------------------------------------------------------------------------
#
# msolve prints one line per F4 round:
#
#   deg     sel   pairs        mat          density        new data      time(rd)
#     2      69      69     310 x 242        0.97%      0 new   69 zero   0.00 | 0.00
#
# and a final "reduce final basis" line that is NOT an F4 round (it is the
# inter-reduction of the finished basis), followed by TIMINGS / COMPUTATIONAL
# DATA blocks.  A run killed by the wall or memory cap leaves the last round
# line truncated mid-way; we keep those as `partial` rounds, because the
# degree field is already printed when the round is *entered* -- polynomials of
# that degree demonstrably occurred -- but the round's `new` count is unknown.

_HEADER_RE = re.compile(r"^deg\s+sel\s+pairs\s+mat\s+density")
_ROUND_RE = re.compile(
    r"^\s*(?P<deg>\d+)\s+(?P<sel>\d+)\s+(?P<pairs>\d+)\s+"
    r"(?P<rows>\d+)\s*x\s*(?P<cols>\d+)\s+(?P<density>[\d.]+)%\s+"
    r"(?P<new>\d+)\s+new\s+(?P<zero>\d+)\s+zero\s+"
    r"(?P<real>[\d.]+)\s*\|\s*(?P<cpu>[\d.]+)\s*$"
)
_PARTIAL_RE = re.compile(r"^\s*(?P<deg>\d+)\s+(?P<sel>\d+)\s+(?P<pairs>\d+)(?P<rest>.*)$")
_SEP_RE = re.compile(r"^-{5,}\s*$")


def parse_msolve_log(path: str) -> dict:
    """Parse one msolve log into our own round list. Reads nothing else."""
    with open(path, "r", errors="replace") as fh:
        lines = fh.read().splitlines()

    start = None
    for i, line in enumerate(lines):
        if _HEADER_RE.match(line):
            start = i + 1
            break
    if start is None:
        return {"parsed": False, "reason": "no F4 round-table header in log",
                "rounds": [], "partial_rounds": [], "f4_finished": False,
                "unparsed_lines": []}

    rounds, partials, unparsed = [], [], []
    f4_finished = False
    for line in lines[start:]:
        if not line.strip():
            continue
        if _SEP_RE.match(line):
            continue
        if line.lstrip().startswith("reduce final basis"):
            f4_finished = True
            continue
        if "TIMINGS" in line or "COMPUTATIONAL DATA" in line:
            break
        m = _ROUND_RE.match(line)
        if m:
            rounds.append({
                "deg": int(m.group("deg")),
                "sel": int(m.group("sel")),
                "pairs": int(m.group("pairs")),
                "rows": int(m.group("rows")),
                "cols": int(m.group("cols")),
                "new": int(m.group("new")),
                "zero": int(m.group("zero")),
                "complete": True,
            })
            continue
        p = _PARTIAL_RE.match(line)
        if p and line[:1] in (" ", "\t"):
            partials.append({
                "deg": int(p.group("deg")),
                "sel": int(p.group("sel")),
                "pairs": int(p.group("pairs")),
                "complete": False,
                "raw_tail": p.group("rest").strip(),
            })
            continue
        unparsed.append(line)

    return {"parsed": True, "reason": None, "rounds": rounds,
            "partial_rounds": partials, "f4_finished": f4_finished,
            "unparsed_lines": unparsed}


# ---------------------------------------------------------------------------
# d_F4, four ways.
# ---------------------------------------------------------------------------
#
# Semaev (paper line 631): "step degree" is the maximal total degree of the
# polynomials for which a row echelon form is computed.
# Semaev (paper line 486): d_F4 is the maximal total degree of the polynomials
# occurring before a Groebner basis is computed.
# Semaev (paper lines 634-636): the steps he EXCLUDES are the trailing ones
# "where 'step degree' was 5, 6, 7 with the message 'No pairs to reduce'".
#
# The exclusion is defined on steps that had NO PAIRS.  Under msolve those are
# the rounds with sel == 0.  We therefore compute:
#
#   naive          max deg over all rounds, nothing excluded
#   semaev_literal max deg after removing the TRAILING run of sel == 0 rounds
#                  -- Semaev's own rule, transcribed
#   excl_trailing_unproductive
#                  max deg after removing the TRAILING run of rounds that
#                  produced no new basis element (new == 0).  This is a
#                  DIFFERENT and strictly more aggressive rule: such a round
#                  did select pairs and did compute a row echelon form, so
#                  under Semaev's own wording its degree counts.  It is
#                  included because it is the only rule that has anything to
#                  exclude on an msolve trace.
#   excl_all_unproductive
#                  max deg over rounds with new > 0, wherever they occur.


def _max_deg(rounds) -> int | None:
    degs = [r["deg"] for r in rounds]
    return max(degs) if degs else None


def derive_d_f4(trace: dict) -> dict:
    rounds = trace["rounds"]
    partials = trace["partial_rounds"]

    # --- trailing run of "no pairs to reduce" steps (Semaev's own exclusion)
    zero_pair_idx = [i for i, r in enumerate(rounds) if r["sel"] == 0]
    cut = len(rounds)
    while cut > 0 and rounds[cut - 1]["sel"] == 0:
        cut -= 1
    semaev_literal_kept = rounds[:cut]
    semaev_literal_excluded = [r["deg"] for r in rounds[cut:]]

    # --- trailing run of unproductive rounds (new == 0)
    cutp = len(rounds)
    while cutp > 0 and rounds[cutp - 1]["new"] == 0:
        cutp -= 1
    trailing_unproductive = [r["deg"] for r in rounds[cutp:]]
    kept_to_last_productive = rounds[:cutp]

    productive = [r for r in rounds if r["new"] > 0]
    all_unproductive_degs = sorted({r["deg"] for r in rounds if r["new"] == 0})

    per_deg_sel = defaultdict(int)
    per_deg_new = defaultdict(int)
    per_deg_rounds = defaultdict(int)
    for r in rounds:
        per_deg_sel[r["deg"]] += r["sel"]
        per_deg_new[r["deg"]] += r["new"]
        per_deg_rounds[r["deg"]] += 1

    naive_complete = _max_deg(rounds)
    naive_incl_partial = _max_deg(rounds + partials)

    return {
        "n_rounds_complete": len(rounds),
        "n_rounds_partial": len(partials),
        "f4_finished": trace["f4_finished"],
        "rounds_with_no_pairs_sel0": len(zero_pair_idx),
        "no_pair_step_degrees": [rounds[i]["deg"] for i in zero_pair_idx],

        "d_F4_naive": naive_complete,
        "d_F4_naive_including_partial_rounds": naive_incl_partial,

        "d_F4_semaev_literal": _max_deg(semaev_literal_kept),
        "semaev_literal_excluded_step_degrees": semaev_literal_excluded,
        "semaev_literal_exclusion_is_vacuous": len(semaev_literal_excluded) == 0,

        "d_F4_excl_trailing_unproductive": _max_deg(kept_to_last_productive),
        "trailing_unproductive_step_degrees": trailing_unproductive,
        "d_F4_excl_all_unproductive": _max_deg(productive),
        "all_unproductive_step_degrees": all_unproductive_degs,

        "per_degree_pair_count_profile": {str(d): per_deg_sel[d] for d in sorted(per_deg_sel)},
        "per_degree_new_basis_profile": {str(d): per_deg_new[d] for d in sorted(per_deg_new)},
        "per_degree_round_count": {str(d): per_deg_rounds[d] for d in sorted(per_deg_rounds)},
        "f4_work_degrees": sorted(per_deg_sel),
        "f4_productive_degrees": sorted({r["deg"] for r in productive}),
        "step_degree_sequence": [r["deg"] for r in rounds] + [f"{p['deg']}*" for p in partials],
    }


# ---------------------------------------------------------------------------
# closure_D.
# ---------------------------------------------------------------------------
#
# closure_D is the smallest degree cap D at which the degree-capped Boolean
# closure W_D is ALREADY a Groebner basis of the ideal.
#
# Working in the Boolean quotient ring F2[x]/(x_i^2 - x_i), the ideal
# I + <field equations> is radical, so
#
#       dim_F2  F2[x]/I  =  |V(I)|,
#
# and the number of standard monomials of the leading-term ideal of W_D equals
# dim_F2 F2[x]/I exactly when W_D is a Groebner basis (otherwise the leading
# term ideal is too small and the standard monomials too many).  So, from the
# primitives recorded per cap:
#
#   is_GB(D)   <=>  1 in W_D                      (unit ideal, GB = {1})
#                   or  standard_monomials(D) == |V(I)|
#   not_GB(D)  <=>  standard_monomials(D) >  |V(I)|
#
# |V(I)| is a property of the IDEAL, not of the cap, so a value established at
# one cap is propagated to every cap of the same instance.  That is what lets
# a cap whose own standard-monomial count merely "exceeds the cap" still be
# decided: >100000 > |V(I)| = 36 settles it.


def derive_closure_D(rec: dict) -> dict:
    per_d = rec.get("per_D") or []
    entries = {}
    for e in per_d:
        D = e.get("D")
        if D is None:
            continue
        entries.setdefault(D, e)

    # instance-level |V(I)|, propagated across caps
    sols = {e.get("solutions") for e in per_d if e.get("solutions") is not None}
    solutions = None
    solutions_conflict = sorted(sols) if len(sols) > 1 else None
    if len(sols) == 1:
        solutions = sols.pop()
    if any(e.get("contains_one") for e in per_d):
        if solutions is None:
            solutions = 0
        elif solutions != 0:
            solutions_conflict = [solutions, 0]

    per_cap = OrderedDict()
    for D in sorted(entries):
        e = entries[D]
        if e.get("status") != "completed":
            per_cap[str(D)] = {"decision": "not_probed", "why": e.get("status"),
                               "reason": e.get("reason")}
            continue
        c1 = bool(e.get("contains_one"))
        sm = e.get("standard_monomials")
        over = bool(e.get("standard_monomials_exceeds_cap"))
        if c1:
            dec, why = "is_GB", "1 in W_D, so W_D generates the unit ideal and is a GB"
        elif sm is not None and solutions is not None and sm == solutions:
            dec, why = "is_GB", f"standard monomials {sm} == |V(I)| {solutions}"
        elif sm is not None and solutions is not None and sm > solutions:
            dec, why = "not_GB", f"standard monomials {sm} > |V(I)| {solutions}"
        elif over and solutions is not None:
            dec, why = "not_GB", f"standard monomials exceed the enumeration cap, hence > |V(I)| {solutions}"
        else:
            dec, why = "undetermined", "|V(I)| not established anywhere in this instance's profile"
        per_cap[str(D)] = {
            "decision": dec, "why": why, "contains_one": c1,
            "standard_monomials": sm, "standard_monomials_exceeds_cap": over,
            "rank": e.get("rank"), "ncols": e.get("ncols"),
            "basis_leading_degree_counts": e.get("basis_leading_degree_counts"),
        }

    probed = sorted(entries)
    gb_caps = [int(d) for d, v in per_cap.items() if v["decision"] == "is_GB"]
    closure_D = min(gb_caps) if gb_caps else None

    # Is that minimum exact, or only an upper bound?
    qualifier, gaps = None, []
    min_meaningful = rec.get("max_generator_degree")
    if closure_D is not None:
        for d, v in per_cap.items():
            if int(d) < closure_D and v["decision"] != "not_GB":
                gaps.append({"D": int(d), "decision": v["decision"]})
        if min_meaningful is not None and probed and min(probed) > min_meaningful:
            gaps.append({"D": f"<{min(probed)}", "decision": "never_probed",
                         "note": f"smallest cap probed is {min(probed)} but generators have degree "
                                 f"{min_meaningful}, so caps {min_meaningful}..{min(probed)-1} are untested"})
        qualifier = "exact" if not gaps else "upper_bound"

    # per-degree rank-gain profile of the closure at each cap
    gain = OrderedDict()
    for D in sorted(entries):
        counts = entries[D].get("basis_leading_degree_counts") or {}
        gain[str(D)] = {
            "pivots_by_leading_monomial_degree": counts,
            "degrees_with_gain": sorted(int(k) for k, v in counts.items() if v),
            "sum_equals_rank": (sum(counts.values()) == entries[D].get("rank")) if counts else None,
            "iteration_new_pivots": [it.get("new_pivots") for it in (entries[D].get("iterations") or [])],
        }

    return {
        "caps_probed": probed,
        "max_generator_degree": min_meaningful,
        "solutions_cardinality_V_I": solutions,
        "solutions_conflict": solutions_conflict,
        "per_cap": per_cap,
        "closure_D": closure_D,
        "closure_D_qualifier": qualifier,
        "closure_D_gaps_below": gaps,
        "not_derivable_reason": None if closure_D is not None else
            ("no cap in the probed profile is decidably a Groebner basis; "
             + ("|V(I)| was never established" if solutions is None
                else "every probed cap is decidably not a GB and no larger cap was reached")),
        "per_degree_rank_gain_profile": gain,
    }


# ---------------------------------------------------------------------------
# Macaulay single-level rank profile (for tail check (ii)).
# ---------------------------------------------------------------------------


def derive_macaulay_profile(rec: dict) -> dict:
    per_d = rec.get("per_D") or []
    entries = {}
    for e in per_d:
        if e.get("D") is not None:
            entries.setdefault(e["D"], e)
    rows = OrderedDict()
    for D in sorted(entries):
        e = entries[D]
        rows[str(D)] = {"status": e.get("status"), "rank": e.get("rank"),
                        "rows": e.get("rows"), "cols": e.get("cols"),
                        "contains_one": e.get("contains_one"),
                        "reason": e.get("reason")}
    gained, increments = [], OrderedDict()
    probed = sorted(entries)
    for i, D in enumerate(probed):
        e = entries[D]
        if e.get("status") != "completed" or e.get("rank") is None:
            continue
        if i == 0:
            increments[str(D)] = None  # no D-1 level recorded to difference against
            continue
        prev = entries[probed[i - 1]]
        if prev.get("rank") is None or probed[i - 1] != D - 1:
            increments[str(D)] = None
            continue
        inc = e["rank"] - prev["rank"]
        increments[str(D)] = inc
        if inc > 0:
            gained.append(D)
    return {"caps_probed": probed, "per_cap": rows,
            "rank_increment_vs_previous_cap": increments,
            "degrees_with_positive_rank_increment": gained,
            "increment_undefined_note":
                "an increment is null where the previous cap D-1 was not probed; "
                "the Macaulay instrument probed only the caps listed in caps_probed"}


# ---------------------------------------------------------------------------
# Cross-check of the producer's own trace PARSE (quarantined input).
# ---------------------------------------------------------------------------


def crosscheck_producer_trace_parse(raw_rec: dict, trace: dict) -> dict:
    """Compare our log parse against the record's `rounds` array.

    This validates the producer's PARSER, not its statistics, and feeds
    nothing in the derivation above.
    """
    prod = raw_rec.get("rounds") or []
    ours = trace["rounds"]
    same_len = len(prod) == len(ours)
    mismatches = []
    for i, (p, o) in enumerate(zip(prod, ours)):
        for key in ("deg", "sel", "pairs", "new", "zero", "rows", "cols"):
            if p.get(key) != o.get(key):
                mismatches.append({"round": i, "field": key,
                                   "producer": p.get(key), "rederived": o.get(key)})
    return {"producer_round_count": len(prod), "rederived_round_count": len(ours),
            "counts_agree": same_len, "field_mismatches": mismatches,
            "agrees": same_len and not mismatches}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def load_records(run_dir: str):
    """Yield (worker, primitive_view(record), raw_record)."""
    for worker in WORKERS:
        path = os.path.join(run_dir, worker, "cells", "results.jsonl")
        if not os.path.exists(path):
            continue
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            yield worker, primitive_view(raw), raw


def _f4_candidate_rank(cand: dict) -> tuple:
    """Order F4 candidate records best-first: most complete rounds wins."""
    tr = cand.get("trace")
    n_complete = len(tr["rounds"]) if tr else -1
    return (n_complete,
            1 if (tr and tr["f4_finished"]) else 0,
            1 if cand["rec"].get("status") == "completed" else 0)


def _profile_candidate_rank(cand: dict) -> tuple:
    per_d = cand["rec"].get("per_D") or []
    return (sum(1 for e in per_d if e.get("status") == "completed"), len(per_d))


def compare_against_producer(run_dir: str, rederived_path: str) -> dict:
    """POST-HOC comparison.  Not part of the derivation.

    Runs only under --compare, strictly after rederived.json exists, and reads
    the producer's derived scalars straight out of the per-cell records -- the
    very fields `primitive_view()` drops.  Nothing here can influence
    rederived.json, which is written by main() before this is reachable.
    """
    mine = json.load(open(rederived_path))["instances"]
    prod: dict = {}
    for worker in WORKERS:
        path = os.path.join(run_dir, worker, "cells", "results.jsonl")
        if not os.path.exists(path):
            continue
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            slot = prod.setdefault(r["instance_id"], {})
            if r.get("instrument") == "f4_trace_msolve":
                cand = {"d_F4_naive": r.get("d_F4_naive"),
                        "d_F4_semaev": r.get("d_F4_semaev"),
                        "d_F4_last_productive_round": r.get("d_F4_last_productive_round"),
                        "d_F4_partial_max_deg_seen": r.get("d_F4_partial_max_deg_seen"),
                        "f4_empty_step_degrees": r.get("f4_empty_step_degrees"),
                        "f4_step_count": r.get("f4_step_count"),
                        "status": r.get("status"),
                        "_n": len(r.get("rounds") or [])}
                if slot.get("f4") is None or cand["_n"] > slot["f4"]["_n"]:
                    slot["f4"] = cand
            if r.get("instrument") == "closure_certificate":
                nd = sum(1 for e in (r.get("per_D") or []) if e.get("status") == "completed")
                if slot.get("cl") is None or nd > slot["cl"]["_n"]:
                    slot["cl"] = {"closure_D": r.get("closure_D"), "_n": nd}

    rows, disagreements = [], []
    for iid, v in mine.items():
        f = v.get("f4", {}) or {}
        p = prod.get(iid, {})
        pf, pc = p.get("f4") or {}, p.get("cl") or {}
        row = {
            "instance": iid,
            "rederived_d_F4_naive": f.get("d_F4_naive"),
            "producer_d_F4_naive": pf.get("d_F4_naive"),
            "rederived_d_F4_semaev_literal": f.get("d_F4_semaev_literal"),
            "rederived_d_F4_excl_trailing_unproductive":
                f.get("d_F4_excl_trailing_unproductive"),
            "producer_d_F4_semaev": pf.get("d_F4_semaev"),
            "producer_d_F4_last_productive_round": pf.get("d_F4_last_productive_round"),
            "producer_d_F4_partial_max_deg_seen": pf.get("d_F4_partial_max_deg_seen"),
            "producer_f4_empty_step_degrees": pf.get("f4_empty_step_degrees"),
            "rederived_trailing_unproductive_step_degrees":
                f.get("trailing_unproductive_step_degrees"),
            "rederived_no_pair_step_degrees": f.get("no_pair_step_degrees"),
            "rederived_closure_D": v["closure"].get("closure_D"),
            "producer_closure_D": pc.get("closure_D"),
        }
        flags = []
        if (row["rederived_d_F4_naive"] is not None
                and row["producer_d_F4_naive"] is not None
                and row["rederived_d_F4_naive"] != row["producer_d_F4_naive"]):
            flags.append("d_F4_naive_value_conflict")
        if (row["rederived_d_F4_naive"] is not None
                and row["producer_d_F4_naive"] is None):
            flags.append("producer_withholds_d_F4_naive_on_a_capped_cell")
        if row["rederived_closure_D"] != row["producer_closure_D"]:
            flags.append("closure_D_conflict")
        if (row["rederived_d_F4_semaev_literal"] is not None
                and row["producer_d_F4_semaev"] is not None
                and row["rederived_d_F4_semaev_literal"] != row["producer_d_F4_semaev"]):
            flags.append("semaev_convention_conflict")
        if (row["rederived_d_F4_excl_trailing_unproductive"]
                != row["producer_d_F4_last_productive_round"]):
            flags.append("trailing_unproductive_convention_conflict")
        if flags:
            row["flags"] = flags
            disagreements.append(row)
        rows.append(row)
    return {"rows": rows, "disagreements": disagreements,
            "n_instances": len(rows), "n_disagreeing": len(disagreements)}


def orphan_scan(run_dir: str) -> dict:
    """Instances with retained artifacts on disk but NO row in any results.jsonl.

    Both this derivation and the run's own summary enumerate instances from
    results.jsonl, so an instance that produced artifacts without producing a
    record is invisible to both.  Reconciling the instances/ directories against
    the records is the only way to see it.  Where such an instance left an
    msolve log, d_F4 is derived here with exactly the same parser and the same
    definitions used for every other instance.
    """
    recorded = set()
    for worker in WORKERS:
        path = os.path.join(run_dir, worker, "cells", "results.jsonl")
        if not os.path.exists(path):
            continue
        for line in open(path):
            line = line.strip()
            if line:
                recorded.add(json.loads(line)["instance_id"])

    on_disk: dict = defaultdict(lambda: defaultdict(set))
    for worker in WORKERS:
        d = os.path.join(run_dir, worker, "cells", "instances")
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            for suf in (".msolve.log", ".msolve.err", ".json", ".gb", ".ms"):
                if name.endswith(suf):
                    on_disk[name[:-len(suf)]][worker].add(suf)
                    break

    out = []
    for stem in sorted(set(on_disk) - recorded):
        entry = {"instance_id": stem,
                 "artifacts": {w: sorted(s) for w, s in on_disk[stem].items()},
                 "f4": None}
        for worker in on_disk[stem]:
            log = os.path.join(run_dir, worker, "cells", "instances", f"{stem}.msolve.log")
            if os.path.exists(log):
                trace = parse_msolve_log(log)
                d = derive_d_f4(trace)
                entry["f4"] = {
                    "source_worker": worker,
                    "d_F4_naive": d["d_F4_naive"],
                    "d_F4_naive_including_partial_rounds":
                        d["d_F4_naive_including_partial_rounds"],
                    "d_F4_semaev_literal": d["d_F4_semaev_literal"],
                    "d_F4_excl_trailing_unproductive":
                        d["d_F4_excl_trailing_unproductive"],
                    "n_rounds_complete": d["n_rounds_complete"],
                    "n_rounds_partial": d["n_rounds_partial"],
                    "f4_trace_complete_per_log": d["f4_finished"],
                    "no_pair_step_degrees": d["no_pair_step_degrees"],
                    "per_degree_pair_count_profile": d["per_degree_pair_count_profile"],
                }
                break
        entry["closure_D"] = None
        entry["closure_note"] = ("no closure or Macaulay record exists for this "
                                 "instance, so no closure_D and no separation")
        out.append(entry)
    return {"recorded_instance_ids": len(recorded),
            "instance_stems_on_disk": len(on_disk),
            "on_disk_but_in_no_record": out}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-blindness", action="store_true")
    ap.add_argument("--orphan-scan", action="store_true",
                    help="Report instances with retained artifacts but no row in "
                         "any results.jsonl. Prints only; never changes --out.")
    ap.add_argument("--compare", action="store_true",
                    help="POST-HOC only: after --out is written, print the comparison "
                         "against the producer's derived scalars. Reads fields the "
                         "derivation deliberately drops; never affects --out.")
    args = ap.parse_args()
    run_dir = args.run_dir

    # The experiment's design is that both instruments receive BYTE-IDENTICAL
    # systems, and in this run the two instruments for one instance frequently
    # live in DIFFERENT worker shards (the heavy cells' F4 pass was deferred to
    # `heavy`, their closure pass to `heavy_closure`).  The unit of analysis is
    # therefore the instance, not the (worker, instance) pair.  Records are
    # merged across workers by instance_id and the merge is only accepted when
    # every contributing record carries the same system_sha256.
    insts: dict = OrderedDict()
    parse_problems = []

    for worker, rec, raw in load_records(run_dir):
        iid = rec["instance_id"]
        slot = insts.setdefault(iid, {"instance_id": iid, "candidates": defaultdict(list),
                                      "workers": set(), "sha": set(), "meta": {}})
        slot["workers"].add(worker)
        if rec.get("system_sha256"):
            slot["sha"].add(rec["system_sha256"])
        for field in ("n", "m", "t", "k", "N", "n_equations", "family", "group",
                      "structure", "subspace", "B_mode", "seed", "draw",
                      "field_equation_convention", "max_generator_degree"):
            if rec.get(field) is not None:
                slot["meta"].setdefault(field, rec[field])
        cand = {"worker": worker, "rec": rec, "raw": raw, "trace": None,
                "log": None}
        if rec.get("instrument") == "f4_trace_msolve":
            log = os.path.join(run_dir, worker, "cells", "instances", f"{iid}.msolve.log")
            if os.path.exists(log):
                cand["log"] = log
                cand["trace"] = parse_msolve_log(log)
                if cand["trace"]["unparsed_lines"]:
                    parse_problems.append({"instance": iid, "worker": worker,
                                           "unparsed": cand["trace"]["unparsed_lines"][:5]})
        slot["candidates"][rec.get("instrument")].append(cand)

    out_instances = OrderedDict()

    for iid, slot in insts.items():
        entry = {"instance_id": iid}
        entry.update(slot["meta"])
        entry["workers_contributing"] = sorted(slot["workers"])
        entry["system_sha256"] = sorted(slot["sha"])[0] if len(slot["sha"]) == 1 else None
        entry["system_sha256_conflict"] = sorted(slot["sha"]) if len(slot["sha"]) > 1 else None
        entry["instruments_present"] = sorted(k for k in slot["candidates"] if k)
        entry["records_per_instrument"] = {k: len(v) for k, v in slot["candidates"].items() if k}

        # ---- F4 -----------------------------------------------------------
        f4cands = slot["candidates"].get("f4_trace_msolve") or []
        if not f4cands:
            entry["f4"] = {"available": False,
                           "why": "no f4_trace_msolve record for this instance in any worker"}
        else:
            best = max(f4cands, key=_f4_candidate_rank)
            if best["trace"] is None:
                entry["f4"] = {
                    "available": False,
                    "recorded_status": best["rec"].get("status"),
                    "recorded_unreached_reason": best["rec"].get("unreached_reason"),
                    "attempted_in_workers": sorted({c["worker"] for c in f4cands}),
                    "why": "no msolve log on disk in any worker: the engine was never "
                           "launched for this cell",
                }
            else:
                trace = best["trace"]
                d = derive_d_f4(trace)
                d["available"] = d["n_rounds_complete"] > 0
                d["source_worker"] = best["worker"]
                d["log_path"] = os.path.relpath(best["log"], run_dir)
                d["recorded_status"] = best["rec"].get("status")
                d["recorded_exit_code"] = best["rec"].get("exit_code")
                d["recorded_unreached_reason"] = best["rec"].get("unreached_reason")
                d["other_f4_records"] = [
                    {"worker": c["worker"], "status": c["rec"].get("status"),
                     "has_log": c["log"] is not None}
                    for c in f4cands if c is not best]
                d["f4_trace_complete_per_log"] = trace["f4_finished"]
                d["trace_truncated"] = (not trace["f4_finished"]) or bool(trace["partial_rounds"])
                d["producer_trace_parse_crosscheck"] = crosscheck_producer_trace_parse(
                    best["raw"], trace)
                # Every F4 record that names a log gets cross-checked, not only
                # the one we derived from.  A cell that was retried keeps only
                # the LAST attempt's log on disk, so an earlier record's trace
                # can no longer be reproduced from any retained raw artifact;
                # this is where that shows up.
                allx = []
                for c in f4cands:
                    if c["trace"] is None:
                        continue
                    x = crosscheck_producer_trace_parse(c["raw"], c["trace"])
                    x["worker"] = c["worker"]
                    x["recorded_status"] = c["rec"].get("status")
                    x["is_the_record_derived_from"] = c is best
                    if not x["agrees"]:
                        prod = c["raw"].get("rounds") or []
                        ours = c["trace"]["rounds"]
                        x["producer_rounds_are_prefix_of_log"] = (
                            len(prod) <= len(ours)
                            and all(all(p.get(k) == o.get(k)
                                        for k in ("deg", "sel", "pairs", "new", "zero"))
                                    for p, o in zip(prod, ours)))
                    allx.append(x)
                d["all_f4_record_log_crosschecks"] = allx
                entry["f4"] = d

        # ---- closure ------------------------------------------------------
        ccands = slot["candidates"].get("closure_certificate") or []
        if not ccands:
            entry["closure"] = {"available": False,
                                "why": "the closure instrument was not run on this instance "
                                       "in any worker"}
        else:
            best = max(ccands, key=_profile_candidate_rank)
            c = derive_closure_D(best["rec"])
            c["available"] = c["closure_D"] is not None
            c["source_worker"] = best["worker"]
            c["n_closure_records_for_instance"] = len(ccands)
            entry["closure"] = c

        # ---- Macaulay -----------------------------------------------------
        mcands = slot["candidates"].get("macaulay_single_level_DREG") or []
        if not mcands:
            entry["macaulay"] = {"available": False,
                                 "why": "the Macaulay instrument was not run on this instance "
                                        "in any worker"}
        else:
            best = max(mcands, key=_profile_candidate_rank)
            entry["macaulay"] = derive_macaulay_profile(best["rec"])
            entry["macaulay"]["source_worker"] = best["worker"]

        # ---- separation ---------------------------------------------------
        cD = entry["closure"].get("closure_D")
        f4 = entry.get("f4", {})
        sep = {"closure_D": cD, "closure_D_qualifier": entry["closure"].get("closure_D_qualifier")}
        for label, field in (("naive", "d_F4_naive"),
                             ("semaev_literal", "d_F4_semaev_literal"),
                             ("excl_trailing_unproductive", "d_F4_excl_trailing_unproductive"),
                             ("excl_all_unproductive", "d_F4_excl_all_unproductive")):
            v = f4.get(field)
            sep[f"d_F4_{label}"] = v
            sep[f"separation_vs_{label}"] = (cD - v) if (cD is not None and v is not None) else None
        sep["both_reached"] = cD is not None and f4.get("d_F4_naive") is not None
        if not sep["both_reached"]:
            missing = []
            if cD is None:
                missing.append("closure_D: " + str(entry["closure"].get("not_derivable_reason")
                                                   or entry["closure"].get("why")))
            if f4.get("d_F4_naive") is None:
                missing.append("d_F4: " + str(f4.get("why") or "no complete F4 round in the log"))
            sep["not_computable_because"] = missing
        entry["separation"] = sep

        # ---- tail check (i) -------------------------------------------------
        # Statistics agree but the per-degree profiles differ.
        ti = {"applicable": sep["both_reached"]}
        if sep["both_reached"]:
            f4_degs = f4.get("f4_work_degrees") or []
            cl_prof = entry["closure"]["per_degree_rank_gain_profile"].get(str(cD), {})
            cl_degs = cl_prof.get("degrees_with_gain") or []
            for label in ("naive", "semaev_literal", "excl_trailing_unproductive",
                          "excl_all_unproductive"):
                agree = sep[f"separation_vs_{label}"] == 0
                ti[f"statistics_agree_{label}"] = agree
            ti["f4_work_degrees"] = f4_degs
            ti["f4_per_degree_pair_counts"] = f4.get("per_degree_pair_count_profile")
            ti["closure_rank_gain_degrees_at_closure_D"] = cl_degs
            ti["closure_pivots_by_degree_at_closure_D"] = cl_prof.get("pivots_by_leading_monomial_degree")
            ti["profiles_differ"] = sorted(f4_degs) != sorted(cl_degs)
            ti["degrees_only_in_f4"] = sorted(set(f4_degs) - set(cl_degs))
            ti["degrees_only_in_closure"] = sorted(set(cl_degs) - set(f4_degs))
            ti["HIT_agree_but_profiles_differ"] = bool(
                ti.get("statistics_agree_naive") and ti["profiles_differ"])
            # The two profiles are indexed on DIFFERENT things -- the F4 side on
            # step degree (the degree of the polynomials whose row echelon form
            # is computed), the closure side on the degree of a pivot's leading
            # monomial.  An F4 run has no step at degree 0 or 1 because there
            # are no critical pairs there, while the closure basis certainly has
            # pivots with linear and constant leading monomials.  So the raw
            # comparison above will differ on every instance for a reason that
            # is about the indexing, not about the instruments.  The restricted
            # comparison drops degrees below 2, where a like-for-like reading is
            # available, and is the one to read.
            lo = 2
            f4r = sorted(x for x in f4_degs if x >= lo)
            clr = sorted(x for x in cl_degs if x >= lo)
            ti["comparison_floor_degree"] = lo
            ti["f4_work_degrees_ge2"] = f4r
            ti["closure_gain_degrees_ge2"] = clr
            ti["profiles_differ_restricted_to_degrees_ge_2"] = f4r != clr
            ti["degrees_only_in_f4_ge2"] = sorted(set(f4r) - set(clr))
            ti["degrees_only_in_closure_ge2"] = sorted(set(clr) - set(f4r))
            ti["HIT_agree_but_profiles_differ_restricted"] = bool(
                ti.get("statistics_agree_naive")
                and ti["profiles_differ_restricted_to_degrees_ge_2"])
            ti["indexing_caveat"] = (
                "f4_work_degrees is indexed by F4 STEP degree; "
                "closure_rank_gain_degrees is indexed by the degree of a pivot's "
                "LEADING MONOMIAL. The retained artifacts do not carry a common "
                "indexing, so only the supports are compared, never the counts.")
        else:
            ti["why_not"] = sep.get("not_computable_because")
        entry["tail_check_i"] = ti

        # ---- tail check (ii) ------------------------------------------------
        tii = {
            "f4_degrees_reporting_no_pairs": f4.get("no_pair_step_degrees"),
            "f4_no_pair_steps_exist": bool(f4.get("no_pair_step_degrees")),
            "f4_trailing_unproductive_degrees_msolve_proxy":
                f4.get("trailing_unproductive_step_degrees"),
            "f4_all_unproductive_degrees_msolve_proxy":
                f4.get("all_unproductive_step_degrees"),
            "macaulay_degrees_with_positive_rank_increment":
                entry["macaulay"].get("degrees_with_positive_rank_increment"),
            "macaulay_rank_increments": entry["macaulay"].get("rank_increment_vs_previous_cap"),
            "macaulay_per_cap": entry["macaulay"].get("per_cap"),
            "closure_rank_gain_degrees_per_cap": {
                d: v.get("degrees_with_gain")
                for d, v in (entry["closure"].get("per_degree_rank_gain_profile") or {}).items()
            } or None,
        }
        if f4.get("no_pair_step_degrees") is not None and not f4["no_pair_step_degrees"]:
            tii["predicted_mechanism_testable"] = False
            tii["why_not_testable"] = (
                "msolve emits no round with sel == 0, so the F4 side of the predicted "
                "coincidence -- the degrees at which F4 reports 'No pairs to reduce' -- "
                "is the empty set on this engine. The contract's predicted mechanism "
                "cannot be tested as literally stated on this run.")
        elif f4.get("no_pair_step_degrees") is None:
            tii["predicted_mechanism_testable"] = None
            tii["why_not_testable"] = "no F4 trace for this instance"
        else:
            tii["predicted_mechanism_testable"] = True
        mg = entry["macaulay"].get("degrees_with_positive_rank_increment")
        tp = f4.get("trailing_unproductive_step_degrees")
        if mg is not None and tp is not None:
            tii["proxy_coincidence"] = sorted(set(tp)) == sorted(set(mg))
            tii["proxy_degrees_only_in_f4_tail"] = sorted(set(tp) - set(mg))
            tii["proxy_degrees_only_in_macaulay_gain"] = sorted(set(mg) - set(tp))
        entry["tail_check_ii"] = tii

        out_instances[iid] = entry

    # ---- run-level roll-ups ------------------------------------------------
    both = [k for k, v in out_instances.items() if v["separation"]["both_reached"]]
    seps_naive = {k: out_instances[k]["separation"]["separation_vs_naive"] for k in both}
    hits_i = [k for k, v in out_instances.items()
              if v["tail_check_i"].get("HIT_agree_but_profiles_differ")]
    truncated = [k for k, v in out_instances.items()
                 if v.get("f4", {}).get("available") and v["f4"].get("trace_truncated")]
    status_vs_log = [
        {"instance": k,
         "recorded_status": v["f4"].get("recorded_status"),
         "f4_trace_complete_per_log": v["f4"].get("f4_trace_complete_per_log"),
         "d_F4_naive": v["f4"].get("d_F4_naive")}
        for k, v in out_instances.items()
        if v.get("f4", {}).get("available")
        and v["f4"].get("recorded_status") != "completed"
    ]
    xchk_bad = [{"instance": k, **v["f4"]["producer_trace_parse_crosscheck"]}
                for k, v in out_instances.items()
                if v.get("f4", {}).get("available")
                and not v["f4"]["producer_trace_parse_crosscheck"]["agrees"]]
    xchk_all_bad = []
    for k, v in out_instances.items():
        for x in (v.get("f4", {}).get("all_f4_record_log_crosschecks") or []):
            if not x["agrees"]:
                xchk_all_bad.append({"instance": k, **{kk: vv for kk, vv in x.items()
                                                       if kk != "field_mismatches"},
                                     "n_field_mismatches": len(x["field_mismatches"])})

    doc = {
        "meta": {
            "task_id": "TASK-20260921-f1e5bd",
            "joint": "J-3",
            "review_round": "REVIEW-SEMBIN-20260921-457504",
            "run_dir": run_dir,
            "what_this_is": "blind re-derivation from raw records and the definitions; "
                            "the producer's summarizer, summary.json, results-table.json, "
                            "task-report.md, NOTES-*, and the manifest's result/controls "
                            "blocks were not read before this file was written",
            "producer_derived_fields_dropped_before_derivation": dict(_DROPPED),
            "instance_merge_rule": "records are merged across worker shards by instance_id; "
                                   "a merge is reported as conflicted if the contributing "
                                   "records disagree on system_sha256",
            "instances_with_sha256_conflict": [
                k for k, v in out_instances.items() if v.get("system_sha256_conflict")],
            "instances_merged_across_workers": {
                k: v["workers_contributing"] for k, v in out_instances.items()
                if len(v["workers_contributing"]) > 1},
            "log_lines_not_parsed": parse_problems,
        },
        "definitions_used": {
            "d_F4_naive": "max step degree over all complete F4 rounds in the msolve log",
            "d_F4_naive_including_partial_rounds":
                "as above, also counting a round whose header line was printed but whose "
                "result line was truncated by a kill; those polynomials demonstrably occurred",
            "d_F4_semaev_literal":
                "Semaev's rule transcribed: max step degree after deleting the TRAILING run of "
                "steps that reported no pairs (sel == 0). Paper lines 631-636.",
            "d_F4_excl_trailing_unproductive":
                "max step degree after deleting the TRAILING run of rounds that added no new "
                "basis element (new == 0). NOT Semaev's rule: such a round selected pairs and "
                "computed a row echelon form, so its degree counts under the paper's own wording.",
            "d_F4_excl_all_unproductive":
                "max step degree over rounds with new > 0 wherever they occur",
            "closure_D":
                "smallest degree cap D at which the degree-capped Boolean closure W_D is already "
                "a Groebner basis; decided per cap by (1 in W_D) or (standard monomials == |V(I)|), "
                "with |V(I)| propagated across the caps of one instance",
            "separation": "closure_D - d_F4, per named d_F4 variant",
        },
        "coverage": {
            "instances_seen": len(out_instances),
            "with_f4_trace": sum(1 for v in out_instances.values() if v.get("f4", {}).get("available")),
            "with_closure_D": sum(1 for v in out_instances.values() if v["closure"].get("available")),
            "with_both": len(both),
            "f4_traces_truncated": truncated,
        },
        "rollups": {
            "separation_vs_naive_counts": dict(Counter(seps_naive.values())),
            "separation_vs_naive_by_instance": seps_naive,
            "largest_separation": (max(seps_naive.values()) if seps_naive else None),
            "instances_at_largest_separation":
                [k for k, v in seps_naive.items() if seps_naive and v == max(seps_naive.values())],
            "tail_check_i_hits": hits_i,
            "tail_check_i_hits_restricted_to_degrees_ge_2": [
                k for k, v in out_instances.items()
                if v["tail_check_i"].get("HIT_agree_but_profiles_differ_restricted")],
            "instances_where_d_F4_conventions_disagree": [
                {"instance": k,
                 "d_F4_naive": v["f4"]["d_F4_naive"],
                 "d_F4_semaev_literal": v["f4"]["d_F4_semaev_literal"],
                 "d_F4_excl_trailing_unproductive": v["f4"]["d_F4_excl_trailing_unproductive"],
                 "d_F4_excl_all_unproductive": v["f4"]["d_F4_excl_all_unproductive"],
                 "d_F4_naive_including_partial_rounds":
                     v["f4"]["d_F4_naive_including_partial_rounds"],
                 "trailing_unproductive_step_degrees":
                     v["f4"]["trailing_unproductive_step_degrees"],
                 "closure_D_available": v["closure"].get("available", False)}
                for k, v in out_instances.items()
                if v.get("f4", {}).get("available")
                and len({v["f4"]["d_F4_naive"], v["f4"]["d_F4_semaev_literal"],
                         v["f4"]["d_F4_excl_trailing_unproductive"],
                         v["f4"]["d_F4_excl_all_unproductive"],
                         v["f4"]["d_F4_naive_including_partial_rounds"]}) > 1],
            "d_F4_naive_distribution": dict(Counter(
                v["f4"]["d_F4_naive"] for v in out_instances.values()
                if v.get("f4", {}).get("available"))),
            "semaev_literal_exclusion_vacuous_everywhere": all(
                v["f4"]["semaev_literal_exclusion_is_vacuous"]
                for v in out_instances.values() if v.get("f4", {}).get("available")),
            "f4_rounds_with_sel_zero_run_wide": sum(
                v["f4"].get("rounds_with_no_pairs_sel0", 0)
                for v in out_instances.values() if v.get("f4", {}).get("available")),
            "recorded_nonterminal_status_but_complete_f4_trace": [
                r for r in status_vs_log if r["f4_trace_complete_per_log"]],
            "recorded_nonterminal_status_with_partial_trace": [
                r for r in status_vs_log if not r["f4_trace_complete_per_log"]],
            "producer_trace_parse_disagreements": xchk_bad,
            "any_f4_record_disagreeing_with_the_log_on_disk": xchk_all_bad,
        },
        "instances": out_instances,
    }

    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=False)
        fh.write("\n")

    if args.audit_blindness:
        print("dropped before derivation:", file=sys.stderr)
        for k, v in sorted(_DROPPED.items()):
            print(f"  {k}: {v}", file=sys.stderr)

    print(f"wrote {args.out}: {len(out_instances)} instances, "
          f"{doc['coverage']['with_f4_trace']} with an F4 trace, "
          f"{doc['coverage']['with_closure_D']} with a derivable closure_D, "
          f"{len(both)} with both")

    if args.orphan_scan:
        scan = orphan_scan(run_dir)
        print(f"\n--- orphan scan: {scan['recorded_instance_ids']} instance ids in "
              f"results.jsonl, {scan['instance_stems_on_disk']} stems on disk, "
              f"{len(scan['on_disk_but_in_no_record'])} with artifacts but no record ---")
        print(json.dumps(scan["on_disk_but_in_no_record"], indent=1))

    if args.compare:
        cmp = compare_against_producer(run_dir, args.out)
        print(f"\n--- POST-HOC comparison against the producer's scalars "
              f"({cmp['n_disagreeing']} of {cmp['n_instances']} instances flagged) ---")
        for row in cmp["disagreements"]:
            print(json.dumps(row, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
