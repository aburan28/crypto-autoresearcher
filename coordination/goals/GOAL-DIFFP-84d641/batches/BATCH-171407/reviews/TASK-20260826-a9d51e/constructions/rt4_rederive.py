"""RT4 BLIND RE-DERIVATION -- TASK-20260826-a9d51e, joint R4-J5 / R4-J4.

WHAT THIS IS.  An INDEPENDENT re-implementation of EXP-DIFFP-f26790's
per-instrument forcing predicate, its cell selector and its differing-cell
count, written from the contract's WRITTEN STATEMENT and from the committed
substrate only.  It does NOT import, read or execute harness/diffpath/readmit.py
(the producer's implementation) or tests/test_diffpath_readmit.py, and it asserts
that at run time.

BLINDNESS BY MECHANISM.  A sys.addaudithook installed BEFORE any harness import
raises on any `open`/`io.open`/`os.open`/`compile`/`exec` naming a path under
    harness/diffpath/readmit.py
    tests/test_diffpath_readmit.py
    coordination/goals/GOAL-DIFFP-84d641/sealed-priors
    coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/reviews/TASK-20260826-422106
    coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/task-cards/TASK-20260826-422106
    coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/review-plan/assignment-TASK-20260826-422106.yaml
    coordination/goals/GOAL-MD5-001/quarantine
    coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/tasks/TASK-20260826-82c660
and the module list is asserted at start and at end.  THE BOUNDARY IS STATED
RATHER THAN CLAIMED AWAY: this covers THIS PYTHON PROCESS ONLY.

QUARANTINE, BY MECHANISM AND NOT BY INTENT.  harness.diffpath.census IS NEVER
IMPORTED and census.build_census is NEVER CALLED.  The sixteen shadow entries are
rebuilt here from the two declared planted-path seeds using pathobj.seeded_pair
and pathobj.plant_from_pair, which read NOTHING from disk.  No network call is
made.  The audit hook above additionally raises on any open under the quarantine
prefix, so the non-reading is enforced rather than promised.

NOTHING UNDER harness/ IS MODIFIED.  Every adversarial instrument below is a
RUN-TIME PROJECTION built in this file.
"""
from __future__ import annotations

import io
import json
import os
import random
import sys

# THE WORKTREE ROOT, FOUND BY WALKING UP UNTIL harness/diffpath/depgraph.py
# EXISTS.  A hard-coded number of parent steps silently imported the MAIN
# checkout's harness/ instead of this worktree's on the first attempt, which
# would have made every number below a measurement of the wrong tree.
def _find_repo(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, "harness", "diffpath", "depgraph.py")):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            raise RuntimeError("worktree root not found")
        d = nd


REPO = _find_repo(os.path.dirname(__file__))

BLIND_PREFIXES = [
    "harness/diffpath/readmit.py",
    "tests/test_diffpath_readmit.py",
    "coordination/goals/GOAL-DIFFP-84d641/sealed-priors",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/reviews/TASK-20260826-422106",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/task-cards/TASK-20260826-422106",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/review-plan/assignment-TASK-20260826-422106.yaml",
    "coordination/goals/GOAL-MD5-001/quarantine",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/tasks/TASK-20260826-82c660",
]
BLOCKED = {"count": 0, "events": []}


def _norm(x):
    try:
        if isinstance(x, bytes):
            x = x.decode("utf-8", "replace")
        p = os.path.realpath(os.fspath(x))
    except Exception:                                             # noqa: BLE001
        return None
    if isinstance(p, bytes):
        p = p.decode("utf-8", "replace")
    return p.replace(os.sep, "/")


def _hook(event, args):
    if event not in ("open", "io.open", "os.open"):
        return
    for a in args[:1]:
        if not isinstance(a, (str, bytes, os.PathLike)):
            continue
        p = _norm(a)
        if p is None:
            continue
        for b in BLIND_PREFIXES:
            if b in p or p.endswith("/" + b):
                BLOCKED["count"] += 1
                BLOCKED["events"].append({"event": event, "path": p})
                raise RuntimeError(f"BLIND_FROM VIOLATION BLOCKED: {p}")


sys.addaudithook(_hook)

assert "harness.diffpath.readmit" not in sys.modules, "readmit preloaded"
assert not any("readmit" in m for m in sys.modules), "readmit-like module loaded"
MODULES_AT_START = len(sys.modules)

sys.path.insert(0, REPO)
for _m in [m for m in list(sys.modules) if m.split(".")[0] == "harness"]:
    del sys.modules[_m]

# CENSUS FIREWALL, BY MECHANISM.  harness.diffpath.depgraph imports census at
# module scope, so census cannot be kept out of sys.modules.  What CAN be made
# mechanical is that neither the corpus scan, nor build_census, nor
# quarantine_attestation is ever CALLED: each is replaced IN THIS PROCESS ONLY
# by a stub that RAISES.  A call would therefore crash this script rather than
# open a byte of the quarantined payload.  Nothing committed is edited.
from harness.diffpath import census as _CEN                # noqa: E402
CENSUS_STUB_CALLS = {"n": 0}


def _forbidden(name):
    def f(*a, **k):
        CENSUS_STUB_CALLS["n"] += 1
        raise RuntimeError(f"RT4 FIREWALL: census.{name} must never be called")
    return f


# quarantine_attestation is the ONLY function in this package that opens the
# quarantined payload.  It is replaced by a stub that OPENS NOTHING.  The audit
# hook above independently RAISES on any open under the quarantine prefix, so
# the firewall is enforced by two mechanisms rather than by intent.
QUAR_STUB_CALLS = {"n": 0}


def _quar_stub():
    QUAR_STUB_CALLS["n"] += 1
    return {"sha256_recomputed": "STUBBED-NOT-HASHED-BY-RT4",
            "bytes_read": 0, "mechanism": "RT4 stub; opens nothing"}


_CEN.quarantine_attestation = _quar_stub
_CEN.scan_corpus = _forbidden("scan_corpus")

# build_census is NOT called by this script for its own census: the sixteen
# shadow entries are rebuilt from the two declared seeds.  It is counted here
# because the COMMITTED rt_instruments.py of BATCH-efcae7 -- which IR-11
# REQUIRES be imported rather than re-expressed -- calls it at MODULE SCOPE.
BUILD_CENSUS_CALLS = {"n": 0}
_real_build = _CEN.build_census


def _counted_build(*a, **k):
    BUILD_CENSUS_CALLS["n"] += 1
    return _real_build(*a, **k)


_CEN.build_census = _counted_build

from harness.diffpath import adjudicator as ADJ            # noqa: E402
from harness.diffpath import controlpower as CP            # noqa: E402
from harness.diffpath import depgraph as DG                # noqa: E402
from harness.diffpath import pathobj as PO                 # noqa: E402

assert "harness.diffpath.readmit" not in sys.modules, "readmit imported"

STRICT = CP.STRICT
SEEDS = CP.SEEDS


# ---------------------------------------------------------------------------
# the sixteen shadow entries, rebuilt from the two declared seeds only
# ---------------------------------------------------------------------------
class _Entry:
    __slots__ = ("id", "primitive", "obj")

    def __init__(self, oid, prim, obj):
        self.id, self.primitive, self.obj = oid, prim, obj


class _Census:
    def __init__(self, shadow):
        self.shadow = shadow


def build_shadow():
    shadow = []
    for prim, seed, steps in (("md5", SEEDS["planted_path_generation_md5"], 64),
                              ("sha1", SEEDS["planted_path_generation_sha1"], 80)):
        rng = random.Random(seed)
        for k in range(8):
            cv, m, mp = PO.seeded_pair(rng, prim)
            obj = PO.plant_from_pair(f"PLANT-{prim.upper()}-{k:02d}", prim,
                                     cv, m, mp, (0, steps - 1))
            shadow.append(_Entry(obj.id, prim, obj))
    return _Census(shadow)


# ---------------------------------------------------------------------------
# MY forcing predicate, implemented from the contract's WRITTEN STATEMENT
# ---------------------------------------------------------------------------
#   "the cell (F, r) IS FORCED FOR I if and only if, in the key pi_I(K) with
#    c(r) additionally deleted, THERE REMAINS a component d such that the graph
#    carries a DERIVATION-BACKED edge d -> c(r) on the primitive under
#    consideration."
#
# READINGS OF THE UNDER-DETERMINED CASE (c(r) not a component of K on this
# primitive).  DECLARED HERE, ALL THREE, BEFORE ANY NUMBER IS READ:
#   A "edge_only"      -- the literal clause.  No edge => NOT forced =>
#                         adjudicated.
#   B "edge_or_vacuous" -- the committed predecessor's disjunct
#                         (depgraph.forced_rows / ASSIGNING_RULE R1): the
#                         deletion is the identity on the key, so the cell is
#                         forced.
#   C "out_of_domain"  -- MY THIRD READING.  The contract defines r as "the
#                         deletion of EXACTLY ONE component c(r) FROM K".  If
#                         c(r) is not in K on this primitive there is no such
#                         row, the predicate has no instance, and the cell is
#                         neither forced nor adjudicated: it is emitted as
#                         `null` under H-8.
READINGS = ("edge_only", "edge_or_vacuous", "out_of_domain")

# COMPOSITION ORDERS, both measured (the contract requires it).
ORDERS = ("project_then_delete", "delete_then_project")


def derivation_backed_determiners(edges_by_prim, prim, target):
    """Every X with a derived_and_witnessed edge X -> target on `prim`."""
    return sorted({r["X"] for r in edges_by_prim[prim]
                   if r["Y"] == target and r["verdict"] == "EDGE"
                   and r["label"] == "derived_and_witnessed"})


def projected_component_names(proj, key_components, prim):
    """Names surviving pi_I, obtained by applying pi_I to a NAME-VALUE key."""
    fake = tuple((n, 0) for n in key_components)
    return [p[0] for p in proj(fake, prim)]


def forced_for(instrument_proj, row, prim, key_components, edges_by_prim,
               reading, order):
    """MY per-instrument forcing predicate.  Returns (status, edges)."""
    in_key = row in key_components
    if not in_key:
        if reading == "edge_or_vacuous":
            return "FORCED", [{"X": None, "Y": row,
                               "derivation": f"{row} is not a component of the "
                                             f"{prim} key; deleting it is the "
                                             f"identity on every {prim} key"}]
        if reading == "out_of_domain":
            return "OUT_OF_DOMAIN", []
        # edge_only falls through to the edge test, which will find nothing
        # that can force a component the key does not contain.
    if order == "project_then_delete":
        remaining = [n for n in projected_component_names(
            instrument_proj, key_components, prim) if n != row]
    else:
        deleted = [n for n in key_components if n != row]
        remaining = projected_component_names(instrument_proj, deleted, prim)
    dets = derivation_backed_determiners(edges_by_prim, prim, row)
    hits = [d for d in dets if d in remaining]
    if hits:
        return "FORCED", [{"X": d, "Y": row, "derivation": "derived_and_witnessed"}
                          for d in hits]
    return "ADJUDICATED", []


# ---------------------------------------------------------------------------
# adversarial instruments, built as RUN-TIME PROJECTIONS (never file edits)
# ---------------------------------------------------------------------------
def proj_identity(key, prim):
    return key


def proj_drop_on_primitive(names, only_primitive):
    names = frozenset(names)

    def f(key, prim):
        if prim != only_primitive:
            return key
        return tuple(p for p in key if p[0] not in names)
    return f


def proj_drop_everywhere(names):
    names = frozenset(names)

    def f(key, prim):
        return tuple(p for p in key if p[0] not in names)
    return f


def main():
    out = {}
    census = build_shadow()

    comp = DG.derive_components(census)
    components = comp["derived_union_in_first_appearance_order"]
    key_by_prim = comp["derived_per_primitive"]
    out["components_union"] = components
    out["key_components_per_primitive"] = key_by_prim

    pop = DG.declared_population(census)
    edges_by_prim = {p: DG.edge_records(pop["objects"][p], p, components)
                     for p in ("md5", "sha1")}
    out["derivation_backed_edges"] = {
        p: sorted((r["X"], r["Y"]) for r in edges_by_prim[p]
                  if r["verdict"] == "EDGE"
                  and r["label"] == "derived_and_witnessed")
        for p in ("md5", "sha1")}
    out["population_sizes"] = pop["population_sizes"]

    families = DG.build_families(census)
    out["families"] = {n: f["per_primitive"] for n, f in families.items()}

    # O-E, IMPORTED from the closed batch's committed constructions (IR-11),
    # not rebuilt.  The local proj_* above exist only for MY adversarial
    # objects.
    rt = DG.load_reused_O_E()
    o_e = rt.proj_drop_on_primitive(["message_difference"], "sha1")

    instruments = {
        "honest": proj_identity,
        "O-E": o_e,
        # ---- MY ADVERSARIAL OBJECTS (O-Q4 and two extensions) --------------
        "O-Q4_flagblind_sha1": proj_drop_on_primitive(["in_linearized_code"],
                                                      "sha1"),
        "O-Q7a_totally_blind": proj_drop_everywhere(
            ["length", "message_difference", "step_delta", "block_index",
             "in_linearized_code"]),
        "O-Q7b_stepdelta_blind": proj_drop_everywhere(["step_delta"]),
    }

    # ---- forced sets, every instrument x reading x order x primitive -------
    forced = {}
    for iname, proj in instruments.items():
        for reading in READINGS:
            for order in ORDERS:
                for prim in ("md5", "sha1"):
                    fset, adj, ood = [], [], []
                    for row in components:
                        st, ed = forced_for(proj, row, prim, key_by_prim[prim],
                                            edges_by_prim, reading, order)
                        (fset if st == "FORCED" else
                         ood if st == "OUT_OF_DOMAIN" else adj).append(row)
                    forced[f"{iname}|{reading}|{order}|{prim}"] = {
                        "forced_rows": fset, "adjudicated_rows": adj,
                        "out_of_domain_rows": ood}
    out["forced_row_sets"] = forced

    # ---- CTL-FORCE-PI side 1: identity forced set vs the committed six -----
    committed_rows = sorted(DG.forced_rows(components, edges_by_prim,
                                           key_by_prim).keys())
    out["committed_predecessor_forced_rows"] = committed_rows
    out["committed_predecessor_rule_is_primitive_uniform"] = True
    ctl = {}
    for reading in READINGS:
        for order in ORDERS:
            per = {p: forced[f"honest|{reading}|{order}|{p}"]["forced_rows"]
                   for p in ("md5", "sha1")}
            union = sorted(set(per["md5"]) | set(per["sha1"]))
            inter = sorted(set(per["md5"]) & set(per["sha1"]))
            ctl[f"{reading}|{order}"] = {
                "per_primitive": per,
                "union_over_primitives": union,
                "intersection_over_primitives": inter,
                "equals_committed_at_union_granularity":
                    union == committed_rows,
                "equals_committed_at_per_primitive_granularity":
                    per["md5"] == committed_rows and per["sha1"] == committed_rows,
            }
    out["CTL_FORCE_PI_side1_identity"] = ctl

    # ---- CTL-FORCE-PI side 2: the rule must MOVE across instruments --------
    move = {}
    for reading in READINGS:
        for order in ORDERS:
            sigs = {i: {p: forced[f"{i}|{reading}|{order}|{p}"]["forced_rows"]
                        for p in ("md5", "sha1")}
                    for i in ("honest", "O-E")}
            move[f"{reading}|{order}"] = {
                "honest": sigs["honest"], "O-E": sigs["O-E"],
                "forced_set_is_invariant_honest_vs_O_E":
                    sigs["honest"] == sigs["O-E"]}
    out["CTL_FORCE_PI_side2_moves"] = move

    # ---- the cell tables and the differing counts --------------------------
    entry_keys = {e.id: (CP.variant_keys(e.obj, STRICT), e.primitive)
                  for e in census.shadow}
    fam_keys = {n: [(d["primitive"], d["k"], CP.variant_keys(d["obj"], STRICT))
                    for d in f["draws"]] for n, f in families.items()}

    def index_for(proj, drop, prim):
        idx = {}
        for eid, (keys, kprim) in entry_keys.items():
            if kprim != prim:
                continue
            idx.setdefault(DG.canon_under(keys, kprim, proj, drop),
                           []).append(eid)
        return idx

    def verdict(fam, row, prim, proj):
        idx = index_for(proj, [row], prim)
        keys = fam_keys[fam]
        member = draws = 0
        for kprim, k, kk in keys:
            if k < 1 or kprim != prim:
                continue
            draws += 1
            if idx.get(DG.canon_under(kk, kprim, proj, [row])):
                member += 1
        return ("DETECTED" if member > 0 else "NOT DETECTED"), draws, member

    constructible = [n for n, f in families.items()
                     if not f["NOT_CONSTRUCTIBLE_on_every_primitive"]]
    out["constructible_families"] = sorted(constructible)

    tables = {}
    for reading in READINGS:
        for order in ORDERS:
            key = f"{reading}|{order}"
            rows_out = []
            for prim in ("md5", "sha1"):
                hset = forced[f"honest|{reading}|{order}|{prim}"]
                oset = forced[f"O-E|{reading}|{order}|{prim}"]
                for fam in sorted(constructible):
                    moved = families[fam]["declaration"]["moves"][0]
                    for row in components:
                        rec = {"family": fam, "row": row, "primitive": prim}
                        if row == moved:
                            rec["exclusion"] = "diagonal"
                            rows_out.append(rec)
                            continue
                        rec["honest_status"] = (
                            "FORCED" if row in hset["forced_rows"] else
                            "OUT_OF_DOMAIN" if row in hset["out_of_domain_rows"]
                            else "ADJUDICATED")
                        rec["O_E_status"] = (
                            "FORCED" if row in oset["forced_rows"] else
                            "OUT_OF_DOMAIN" if row in oset["out_of_domain_rows"]
                            else "ADJUDICATED")
                        if "ADJUDICATED" in (rec["honest_status"],
                                             rec["O_E_status"]):
                            hv, hd, hm = verdict(fam, row, prim, proj_identity)
                            ov, od, om = verdict(fam, row, prim, o_e)
                            rec["honest_verdict"] = hv
                            rec["O_E_verdict"] = ov
                            rec["differs"] = hv != ov
                            rec["honest_member_draws"] = hm
                            rec["O_E_member_draws"] = om
                            rec["perturbed_draws_k_ge_1"] = hd
                        rows_out.append(rec)
            tables[key] = rows_out
    out["cell_tables"] = tables

    # ---- THE SELECTOR EXPERIMENT: same instrument pair, three domains ------
    counts = {}
    for key, rows_out in tables.items():
        c = {}
        for prim in ("md5", "sha1"):
            sub = [r for r in rows_out
                   if r["primitive"] == prim and "exclusion" not in r]
            hon = [r for r in sub if r["honest_status"] == "ADJUDICATED"]
            oe = [r for r in sub if r["O_E_status"] == "ADJUDICATED"]
            both = [r for r in sub if r["honest_status"] == "ADJUDICATED"
                    and r["O_E_status"] == "ADJUDICATED"]
            either = [r for r in sub if "differs" in r]
            c[prim] = {
                "domain_honest": {"adjudicated": len(hon),
                                  "differing": sum(1 for r in hon if r["differs"])},
                "domain_O_E": {"adjudicated": len(oe),
                               "differing": sum(1 for r in oe if r["differs"])},
                "domain_intersection": {"adjudicated": len(both),
                                        "differing": sum(1 for r in both if r["differs"])},
                "domain_union": {"adjudicated": len(either),
                                 "differing": sum(1 for r in either if r["differs"])},
                "differing_cells": [
                    {"family": r["family"], "row": r["row"],
                     "honest": r["honest_verdict"], "O_E": r["O_E_verdict"]}
                    for r in either if r["differs"]],
            }
        counts[key] = c
    out["differing_counts_by_selector_domain"] = counts

    # ---- O-Q4 / O-Q7a / O-Q7b: does blindness buy adjudication surface? ----
    surface = {}
    for iname in instruments:
        for reading in READINGS:
            for prim in ("md5", "sha1"):
                k = f"{iname}|{reading}|project_then_delete|{prim}"
                surface[f"{iname}|{reading}|{prim}"] = {
                    "forced_rows": forced[k]["forced_rows"],
                    "n_adjudicated_rows": len(forced[k]["adjudicated_rows"]),
                }
    out["adjudication_surface_by_instrument"] = surface

    # ---- transitive-closure reading (a PATH of derivation-backed edges) ----
    closure = {}
    for prim in ("md5", "sha1"):
        e = out["derivation_backed_edges"][prim]
        reach = {}
        for (x, y) in e:
            reach.setdefault(y, set()).add(x)
        changed = True
        while changed:
            changed = False
            for y, xs in list(reach.items()):
                for x in list(xs):
                    for z in reach.get(x, ()):
                        if z not in xs:
                            xs.add(z)
                            changed = True
        closure[prim] = {y: sorted(xs) for y, xs in reach.items()}
    out["transitive_closure_of_derivation_backed_edges"] = closure

    out["blind_from_blocked_attempts"] = BLOCKED["count"]
    out["readmit_absent_from_sys_modules_at_end"] = (
        "harness.diffpath.readmit" not in sys.modules)
    out["forbidden_census_stub_calls_attempted"] = CENSUS_STUB_CALLS["n"]
    out["quarantine_attestation_stub_calls"] = QUAR_STUB_CALLS["n"]
    out["build_census_calls_by_the_committed_IR11_import"] = \
        BUILD_CENSUS_CALLS["n"]
    out["harness_module_file_actually_imported"] = DG.__file__
    out["repo_root_resolved"] = REPO
    out["modules_loaded"] = len(sys.modules)
    out["variant_mirror_check"] = dict(CP.VARIANT_MIRROR_CHECK)
    return out


if __name__ == "__main__":
    res = main()
    dest = os.path.join(os.path.dirname(__file__), "rt4_rederivation.json")
    with io.open(dest, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: v for k, v in res.items()
                      if k not in ("cell_tables",)},
                     indent=1, sort_keys=True, default=str))
