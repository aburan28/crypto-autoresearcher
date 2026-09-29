"""RED TEAM ROUND 3 -- TASK-20260824-7d9f92 -- INDEPENDENT RE-DERIVATION.

MECHANISM: a run-time WRAPPER/PROJECTION over the committed modules. NO COMMITTED
FILE IS MODIFIED and harness/diffpath/depgraph.py and tests/test_diffpath_depgraph.py
are NEVER IMPORTED OR READ (blind_from of the round's blind_rederivation).

QUARANTINE FIREWALL BY MECHANISM: census.build_census() is NEVER CALLED, so
census.quarantine_attestation() -- which opens the Tier-A payload 'rb' -- is never
reached. harness.diffpath.census is not even imported. The 16 shadow entries are
rebuilt here from the two declared planted-path seeds with the committed
seeded_pair/plant_from_pair, which read nothing from disk.
"""
import os, sys, json, itertools, random

REPO = os.environ.get("DIFFP_REPO") or os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir]*8))
sys.path.insert(0, REPO)

from harness.diffpath import adjudicator as ADJ
from harness.diffpath import equivalence as EQ
from harness.diffpath import primitives as P
from harness.diffpath import controlpower as CP
from harness.diffpath.pathobj import PathObject, seeded_pair, plant_from_pair, bsdr_encode

assert "harness.diffpath.depgraph" not in sys.modules, "blind_from violation"

STRICT = CP.STRICT
SEEDS = CP.SEEDS
DECLARED_ROWS = ("primitive", "length", "message_difference",
                 "step_delta", "block_index", "in_linearized_code")
FAMILIES = DECLARED_ROWS          # one family d_X per component
BLOCK_INDEX_RANGE = (0, 3)        # my declared range; E6 reindexes to 3
K_VALUES = (1, 2, 4, 8, 16)       # k >= 1 only, per the cell verdict rule

# ---------------------------------------------------------------- census (16)
def build_shadow():
    out = []
    for prim, seed, steps in (("md5", SEEDS["planted_path_generation_md5"], 64),
                              ("sha1", SEEDS["planted_path_generation_sha1"], 80)):
        rng = random.Random(seed)
        for k in range(8):
            cv, m, mp = seeded_pair(rng, prim)
            out.append(plant_from_pair(f"PLANT-{prim.upper()}-{k:02d}", prim,
                                       cv, m, mp, (0, steps - 1)))
    return out

SHADOW = build_shadow()

# --------------------------------------------------- derived component list
def derived_components(obj):
    return [n for (n, v) in ADJ.serialize(obj, STRICT)]

DERIVED = {p: derived_components([o for o in SHADOW if o.primitive == p][0])
           for p in ("md5", "sha1")}

# ------------------------------------------------------- CTL-WF (my version)
def wf_reject_reasons(obj):
    r = []
    try:
        a, b = obj.step_range
    except Exception:
        return ["step_range malformed"]
    steps = 64 if obj.primitive == "md5" else 80
    if not (isinstance(a, int) and isinstance(b, int) and 0 <= a <= b < steps):
        r.append("step_range not well formed for primitive")
    if len(obj.step_delta) != (b - a + 1):
        r.append("step_delta arity != length")
    if obj.primitive == "md5":
        if obj.delta_m is None or len(obj.delta_m) != 16:
            r.append("md5 message-difference word count != 16")
        if obj.dv is not None:
            r.append("md5 object carries a sha1 dv")
    else:
        if obj.dv is None:
            r.append("sha1 object carries no dv")
        else:
            if len(obj.dv) != (b - a + 1):
                r.append("sha1 dv word count != length")
            if obj.in_linearized_code != P.sha1_in_linearized_code(list(obj.dv)):
                r.append("in_linearized_code != sha1_in_linearized_code(dv)")
        if obj.delta_m is not None:
            r.append("sha1 object carries an md5 delta_m")
    if not (BLOCK_INDEX_RANGE[0] <= obj.block_index <= BLOCK_INDEX_RANGE[1]):
        r.append("block_index outside declared range")
    return r

# ----------------------------------------------- variant keys (self-checking)
def vkeys(obj, gens=STRICT):
    return CP.variant_keys(obj, gens)

# ------------------------------------------------------------- instruments
def proj_identity(key, prim):
    return key

def proj_drop_on_primitive(names, only_primitive):
    """VERBATIM re-expression of the committed O-E projection from
    BATCH-efcae7/reviews/TASK-20260824-e9d21a/constructions/rt_instruments.py."""
    names = frozenset(names)
    def f(key, prim):
        if prim != only_primitive:
            return key
        return tuple(p for p in key if p[0] not in names)
    return f

OE = proj_drop_on_primitive(["message_difference"], "sha1")

def make_key(obj, instr_proj, drop_set):
    drop = frozenset(drop_set)
    ks = []
    for k in vkeys(obj, STRICT):
        k = instr_proj(k, obj.primitive)
        ks.append(tuple(p for p in k if p[0] not in drop))
    return min(ks)

def build_index(entries, instr_proj, drop_set):
    idx = {}
    for o in entries:
        idx.setdefault(make_key(o, instr_proj, drop_set), []).append(o.id)
    return idx

# ---------------------------------------------------------------- families
def fam_message_difference(src):
    """The COMMITTED family (d) primary arm, reused: perturb_message_difference."""
    nbits = CP.md_bits(src)
    out = []
    for k in K_VALUES:
        if k > nbits:
            continue
        out.append(CP.perturb_message_difference(src, tuple(range(k)), f"det{k}"))
    return out

def fam_step_delta(src):
    out = []
    n = len(src.step_delta) * 32
    for k in K_VALUES:
        if k > n:
            continue
        new = PathObject(**{**src.__dict__})
        d = list(src.step_delta)
        for p in range(k):
            d[p // 32] ^= 1 << (p % 32)
        new.step_delta = tuple(d)
        new.id = f"{src.id}~SD{k}"
        out.append(new)
    return out

def fam_block_index(src):
    out = []
    for v in range(BLOCK_INDEX_RANGE[0], BLOCK_INDEX_RANGE[1] + 1):
        if v == src.block_index:
            continue
        new = PathObject(**{**src.__dict__})
        new.block_index = v
        new.id = f"{src.id}~BI{v}"
        out.append(new)
    return out

def fam_primitive(src):
    new = PathObject(**{**src.__dict__})
    new.primitive = "sha1" if src.primitive == "md5" else "md5"
    new.id = f"{src.id}~PRIM"
    return [new]

def fam_length(src):
    """Perturb `length` (the step_range extent) holding every other key
    component -- including step_delta and message_difference -- FIXED."""
    a, b = src.step_range
    out = []
    for nb in (b - 1, b - 2):
        if nb <= a:
            continue
        new = PathObject(**{**src.__dict__})
        new.step_range = (a, nb)
        new.id = f"{src.id}~LEN{nb}"
        out.append(new)
    return out

def fam_in_linearized_code(src):
    """NULL FAMILY (e): flip the flag holding the message difference fixed."""
    if src.primitive != "sha1":
        return []
    new = PathObject(**{**src.__dict__})
    new.in_linearized_code = not src.in_linearized_code
    new.id = f"{src.id}~FLAG"
    return [new]

FAM_FN = {"message_difference": fam_message_difference,
          "step_delta": fam_step_delta,
          "block_index": fam_block_index,
          "primitive": fam_primitive,
          "length": fam_length,
          "in_linearized_code": fam_in_linearized_code}

# ------------------------------------------------------------- gate the draws
draws = {}          # (family, primitive) -> list of gate-ACCEPTED draws
gate = {}           # (family, primitive) -> {"constructed":n,"rejected":n,"reasons":{}}
for fam in FAMILIES:
    for prim in ("md5", "sha1"):
        acc, rej, reasons = [], 0, {}
        for src in [o for o in SHADOW if o.primitive == prim]:
            for d in FAM_FN[fam](src):
                rs = wf_reject_reasons(d)
                if rs:
                    rej += 1
                    for x in rs:
                        reasons[x] = reasons.get(x, 0) + 1
                else:
                    acc.append((src, d))
        draws[(fam, prim)] = acc
        gate[(fam, prim)] = {"constructed": len(acc) + rej, "accepted": len(acc),
                             "rejected": rej, "reasons": reasons}

# ------------------------------------------------------------ cell verdicts
def cell_verdict(fam, prim, row, instr_proj):
    ds = draws[(fam, prim)]
    if not ds:
        return None                      # NOT CONSTRUCTIBLE on this primitive
    entries = [o for o in SHADOW if o.primitive == prim]
    idx = build_index(entries, instr_proj, (row,))
    for src, d in ds:
        if make_key(d, instr_proj, (row,)) in idx:
            return "DETECTED"
    return "NOT DETECTED"

results = {}
for fam in FAMILIES:
    for row in DECLARED_ROWS:
        for prim in ("md5", "sha1"):
            h = cell_verdict(fam, prim, row, proj_identity)
            e = cell_verdict(fam, prim, row, OE)
            results[(fam, row, prim)] = (h, e)

# --------------------------------------------------------------- exclusions
FORCED_ROW = "in_linearized_code"     # forced by the derivation-backed edge
def classify(fam, row, prim):
    if not draws[(fam, prim)]:
        return "not_constructible"
    if fam == row:
        return "diagonal"
    if row == FORCED_ROW:
        return "forced_by_the_graph"
    return "adjudicated"

out = {"derived_components": DERIVED,
       "gate": {f"{k[0]}|{k[1]}": v for k, v in gate.items()},
       "cells": [], "summary": {}}

adj_pp = diff_pp = 0
adj_pairs = set(); diff_pairs = set()
forced_diff = []
for fam in FAMILIES:
    for row in DECLARED_ROWS:
        for prim in ("md5", "sha1"):
            cls = classify(fam, row, prim)
            h, e = results[(fam, row, prim)]
            rec = {"family": f"d_{fam}", "row": f"delete_{row}", "primitive": prim,
                   "class": cls, "honest": h, "O_E": e,
                   "differs": (cls == "adjudicated" and h != e)}
            out["cells"].append(rec)
            if cls == "adjudicated":
                adj_pp += 1
                adj_pairs.add((fam, row))
                if h != e:
                    diff_pp += 1
                    diff_pairs.add((fam, row))
            if cls == "forced_by_the_graph" and h != e:
                forced_diff.append(rec)

out["summary"] = {
    "per_primitive_cells_total": 6 * 6 * 2,
    "per_primitive_cells_adjudicated": adj_pp,
    "per_primitive_differing_cells_honest_vs_O_E": diff_pp,
    "family_by_row_cells_total": 36,
    "family_by_row_cells_with_at_least_one_adjudicated_primitive": len(adj_pairs),
    "family_by_row_differing_cells_honest_vs_O_E": len(diff_pairs),
    "differing_pairs": sorted(f"d_{a}|delete_{b}" for a, b in diff_pairs),
    "cells_excluded_as_forced_by_the_graph_that_WOULD_have_differed": forced_diff,
}
print(json.dumps(out, indent=1, default=str))
