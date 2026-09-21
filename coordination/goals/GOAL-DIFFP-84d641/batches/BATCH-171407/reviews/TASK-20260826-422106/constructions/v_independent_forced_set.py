"""INDEPENDENT RE-IMPLEMENTATION of EXP-DIFFP-f26790's forcing predicate.

WRITTEN BY TASK-20260826-422106 (Validator) BEFORE OPENING ANY FILE UNDER THE
PRODUCER'S TASK DIRECTORY.  MECHANISM: re-implemented from the contract's own
statement at `the_forcing_predicate_stated_formally...`, over the COMMITTED
graph artifact of the CLOSED batch BATCH-145531
(dependency-graph-result.json), which carries the run-time-derived key
component list and the labelled edge records.  IT DOES NOT IMPORT
harness/diffpath/readmit.py AND DOES NOT CALL census.build_census.

Instruments' projections are taken from the committed declarations:
  honest            : identity
  O-E               : drop 'message_difference' on sha1 only (per-primitive)
  always_member     : NOT a projection -- identity projection by declaration
  always_non_member : NOT a projection -- identity projection by declaration
"""
import json, os, sys, itertools

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir]*8))
GRAPH = os.path.join(
    REPO, "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-145531/tasks/"
          "TASK-20260824-68ba87/dependency-graph-result.json")

g = json.load(open(GRAPH))
KEY = g["derived_key_components_IR13"]["derived_per_primitive"]      # per prim
ROWS = g["derived_key_components_IR13"]["derived_union_in_first_appearance_order"]
PRIMS = ("md5", "sha1")

# --- the derivation-backed edge set, per primitive, from the committed graph
EDGES = {p: [tuple(e) for e in g["edges_with_a_derivation_and_a_witness"][p]]
         for p in PRIMS}       # list of (X, Y)

FAMILIES = {                    # the three CTL-WF-constructible families
    "d_message_difference": ["message_difference"],
    "d_step_delta":         ["step_delta"],
    "d_block_index":        ["block_index"],
}

def retained(prim, proj, deleted, order):
    """names surviving pi_I composed with the row's deletion, per order."""
    k = list(KEY[prim])
    if order == "project_then_delete":
        k = proj(k, prim)
        k = [c for c in k if c != deleted]
    elif order == "delete_then_project":
        k = [c for c in k if c != deleted]
        k = proj(k, prim)
    else:
        raise KeyError(order)
    return k

def forced(prim, proj, deleted, order, reading):
    """THE PREDICATE, from the contract statement."""
    rem = retained(prim, proj, deleted, order)
    edges = [(x, y) for (x, y) in EDGES[prim] if y == deleted and x in rem]
    vacuous = deleted not in KEY[prim]      # vacuity vs the HONEST key
    if reading == "edge_only":
        return bool(edges), edges, vacuous
    if reading == "edge_or_vacuous":
        return (bool(edges) or vacuous), edges, vacuous
    raise KeyError(reading)

P_ID = lambda k, p: list(k)
P_OE = lambda k, p: [c for c in k if not (p == "sha1" and c == "message_difference")]
INSTR = {"honest": P_ID, "O-E": P_OE,
         "always_member": P_ID, "always_non_member": P_ID}

ORDERS = ("project_then_delete", "delete_then_project")
READINGS = ("edge_only", "edge_or_vacuous")

out = {"mechanism": __doc__, "key_components_per_primitive": KEY,
       "rows_union": ROWS, "derivation_backed_edges": {p: EDGES[p] for p in PRIMS},
       "cell_universe": {
           "families_constructible": sorted(FAMILIES),
           "rows": len(ROWS), "primitives": len(PRIMS),
           "cells_per_primitive": len(FAMILIES) * len(ROWS),
           "cells_total_both_primitives": len(FAMILIES) * len(ROWS) * len(PRIMS),
           "arithmetic": "3 families x 6 union rows = 18 cells PER PRIMITIVE; "
                         "36 cells in TOTAL across the two primitives"},
       "per_instrument": {}}

for iname, proj in INSTR.items():
    ent = {}
    for order in ORDERS:
        for reading in READINGS:
            tag = f"{reading}/{order}"
            per_prim = {}
            for prim in PRIMS:
                f_rows, adj_cells, forced_cells, diag_cells = [], [], [], []
                for fam, moves in sorted(FAMILIES.items()):
                    for row in ROWS:
                        cell = f"{fam}|{row}|{prim}"
                        if len(moves) == 1 and row == moves[0]:
                            diag_cells.append(cell); continue
                        fo, edges, vac = forced(prim, proj, row, order, reading)
                        (forced_cells if fo else adj_cells).append(cell)
                for row in ROWS:
                    fo, edges, vac = forced(prim, proj, row, order, reading)
                    if fo:
                        f_rows.append({"row": row, "edges": edges, "vacuous": vac})
                per_prim[prim] = {
                    "forced_rows": f_rows,
                    "forced_row_names": [r["row"] for r in f_rows],
                    "cells_total": len(FAMILIES) * len(ROWS),
                    "diagonal_excluded": len(diag_cells),
                    "forced_excluded": len(forced_cells),
                    "adjudicated": len(adj_cells),
                    "adjudicated_cells": sorted(adj_cells),
                    "forced_cells": sorted(forced_cells),
                }
            # aggregate: a cell is forced in aggregate iff forced on BOTH prims
            agg_forced = sorted(
                set(c.rsplit("|", 1)[0] for c in per_prim["md5"]["forced_cells"]) &
                set(c.rsplit("|", 1)[0] for c in per_prim["sha1"]["forced_cells"]))
            per_prim["aggregate_named_as_aggregate"] = {
                "forced_on_both_primitives": agg_forced,
                "count": len(agg_forced)}
            ent[tag] = per_prim
    out["per_instrument"][iname] = ent

# CTL-FORCE-PI side A: identity forced set vs the committed six
COMMITTED = json.load(open(os.path.join(
    REPO, "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-145531/tasks/"
          "TASK-20260824-68ba87/offdiagonal-matrix-result.json")))
six = sorted(f"{e['family']}|{e['row_deletes']}"
             for e in COMMITTED["excluded_cells_with_every_reason"]
             if e["exclusion"] == "forced_by_the_graph")
out["committed_six_forced_cells"] = six
out["CTL_FORCE_PI_side_A"] = {
    tag: {"identity_aggregate_forced":
              out["per_instrument"]["honest"][tag]["aggregate_named_as_aggregate"]["forced_on_both_primitives"],
          "equals_committed_six":
              out["per_instrument"]["honest"][tag]["aggregate_named_as_aggregate"]["forced_on_both_primitives"] == six}
    for tag in ent}
out["CTL_FORCE_PI_side_B_forced_set_moves_honest_vs_OE"] = {
    tag: {prim: (out["per_instrument"]["honest"][tag][prim]["forced_row_names"]
                 != out["per_instrument"]["O-E"][tag][prim]["forced_row_names"])
          for prim in PRIMS} for tag in ent}
out["re_admitted_forced_for_identity_not_forced_for_O_E"] = {
    tag: {prim: sorted(set(out["per_instrument"]["honest"][tag][prim]["forced_cells"]) -
                       set(out["per_instrument"]["O-E"][tag][prim]["forced_cells"]))
          for prim in PRIMS} for tag in ent}

json.dump(out, open(os.path.join(os.path.dirname(__file__),
                                 "v_independent_forced_set.json"), "w"),
          indent=1, sort_keys=True)
print(json.dumps({
    "cells_per_primitive": out["cell_universe"]["cells_per_primitive"],
    "cells_total": out["cell_universe"]["cells_total_both_primitives"],
    "committed_six": six,
    "side_A": out["CTL_FORCE_PI_side_A"],
    "side_B": out["CTL_FORCE_PI_side_B_forced_set_moves_honest_vs_OE"],
    "readmitted": out["re_admitted_forced_for_identity_not_forced_for_O_E"],
}, indent=1))
for iname in INSTR:
    for tag in ent:
        for prim in PRIMS:
            e = out["per_instrument"][iname][tag][prim]
            print(f"{iname:18s} {tag:38s} {prim:5s} forced_rows={e['forced_row_names']!s:45s}"
                  f" diag={e['diagonal_excluded']} forced={e['forced_excluded']} adjudicated={e['adjudicated']}")
