"""RED TEAM ROUND 3 -- TASK-20260824-7d9f92 -- ADVERSARIAL OBJECTS O-P1..O-P7.

MECHANISM: run-time construction and run-time PROJECTION wrappers only. No
committed file is modified. harness/diffpath/depgraph.py and
tests/test_diffpath_depgraph.py are never imported or read.
QUARANTINE FIREWALL: census.build_census() is never called and
harness.diffpath.census is never imported, so the Tier-A payload is never opened.
"""
import os, sys, json, random
REPO = os.environ.get("DIFFP_REPO")
sys.path.insert(0, REPO)
from harness.diffpath import adjudicator as ADJ
from harness.diffpath import equivalence as EQ
from harness.diffpath import primitives as P
from harness.diffpath import controlpower as CP
from harness.diffpath.pathobj import PathObject, seeded_pair, plant_from_pair

STRICT = CP.STRICT
SEEDS = CP.SEEDS
R = {}

# ------------------------------------------------------------------ census
def planted(prim, steps, k, step_range=None):
    rng = random.Random(SEEDS[f"planted_path_generation_{prim}"])
    for i in range(k + 1):
        cv, m, mp = seeded_pair(rng, prim)
    return plant_from_pair(f"PLANT-{prim.upper()}-{k:02d}", prim, cv, m, mp,
                           step_range or (0, steps - 1))

SHADOW = []
for prim, steps in (("md5", 64), ("sha1", 80)):
    rng = random.Random(SEEDS[f"planted_path_generation_{prim}"])
    for k in range(8):
        cv, m, mp = seeded_pair(rng, prim)
        SHADOW.append(plant_from_pair(f"PLANT-{prim.upper()}-{k:02d}", prim, cv, m, mp,
                                      (0, steps - 1)))
SHA = [o for o in SHADOW if o.primitive == "sha1"]

# ================================================================= O-P1
# A well-formed SHA-1 object at a step range OTHER than the full one, built by
# the COMMITTED plant_from_pair from the SAME seeded pair as census entry 0.
rng = random.Random(SEEDS["planted_path_generation_sha1"])
cv, m, mp = seeded_pair(rng, "sha1")
op1 = {}
for rngspec in [(0, 79), (0, 15), (0, 10), (8, 40), (16, 79)]:
    o = plant_from_pair("OP1", "sha1", cv, m, mp, rngspec)
    op1[str(rngspec)] = {
        "stored_flag_from_full_expansion": o.in_linearized_code,
        "recomputed_flag_from_serialised_message_difference":
            P.sha1_in_linearized_code(list(o.dv)),
        "dv_words": len(o.dv),
        "agree": o.in_linearized_code == P.sha1_in_linearized_code(list(o.dv)),
    }
R["O-P1"] = {
    "construction": ("the committed plant_from_pair applied to the SAME seeded "
                     "message pair that produces census entry PLANT-SHA1-00, at "
                     "five step ranges. plant_from_pair computes the stored flag "
                     "from the FULL 80-word expansion difference and stores "
                     "dv = full_dv[a:b+1] as the serialised message_difference."),
    "per_step_range": op1}

# ================================================================= O-P1b
# sha1_in_linearized_code is a CONSTANT function of its argument at |dv| <= 16.
R["O-P1b"] = {
  "statement": ("sha1_in_linearized_code(words) returns False for every words "
                "with len < 16 and True for every words with len == 16, so on a "
                "step range of extent <= 16 the predicate carries ZERO bits "
                "about the message difference."),
  "len_15_random_100": sum(P.sha1_in_linearized_code([random.getrandbits(32) for _ in range(15)]) for _ in range(100)),
  "len_16_random_100": sum(P.sha1_in_linearized_code([random.getrandbits(32) for _ in range(16)]) for _ in range(100)),
  "len_17_random_100": sum(P.sha1_in_linearized_code([random.getrandbits(32) for _ in range(17)]) for _ in range(100)),
}

# ================================================================= O-P2
# Equivalence generators CARRY the flag. Applied to a flag-FALSE object,
# act_E1_shift REPLACES dv by the expansion of the seed window -- a codeword --
# while carrying the FALSE flag over.
base = SHA[0]
bad = PathObject(**{**base.__dict__})
bad.id = "OP2-FLAGFALSE"
d = list(base.dv); d[40] ^= 1          # break the codeword
bad.dv = tuple(d)
bad.in_linearized_code = P.sha1_in_linearized_code(list(d))   # honestly False
carriers = {}
for name, img in (("act_E1_shift(+1)", EQ.act_E1_shift(bad, 1)),
                  ("act_E2_rotate(7)", EQ.act_E2_rotate(bad, 7)),
                  ("act_E3_negate", EQ.act_E3_negate(bad)),
                  ("act_E6_reindex(3)", EQ.act_E6_reindex(bad, 3))):
    carriers[name] = {
        "carried_flag": img.in_linearized_code,
        "recomputed_flag_from_image_dv": P.sha1_in_linearized_code(list(img.dv)),
        "agree": img.in_linearized_code == P.sha1_in_linearized_code(list(img.dv))}
# align_E1 is called INSIDE the committed canonical()/variant_keys()
al = EQ.align_E1(EQ.act_E1_shift(bad, 1))
carriers["align_E1(act_E1_shift(+1))"] = {
    "carried_flag": al.in_linearized_code,
    "recomputed_flag_from_image_dv": P.sha1_in_linearized_code(list(al.dv)),
    "agree": al.in_linearized_code == P.sha1_in_linearized_code(list(al.dv)),
    "dv_changed_by_canonicalisation": tuple(al.dv) != tuple(bad.dv)}
R["O-P2"] = {"source_object_flag": bad.in_linearized_code,
             "generators_that_carry_rather_than_recompute": carriers,
             "count_of_committed_generators_that_carry_the_flag": 5}

# ================================================================= O-P3
# A well-formed SHA-1 object OUTSIDE the linearized code, and the census's own
# constancy on the flag.
R["O-P3"] = {
  "census_sha1_flag_values": sorted({o.in_linearized_code for o in SHA}),
  "distinct_flag_values_in_census": len({o.in_linearized_code for o in SHA}),
  "why": ("sha1_expand is GF(2)-linear, so for a planted pair "
          "dv = expand(m) ^ expand(mp) = expand(m ^ mp) is ALWAYS a codeword. "
          "No planted SHA-1 object can ever have flag False."),
  "out_of_code_object_is_constructible_directly": {
      "id": bad.id, "flag": bad.in_linearized_code,
      "differs_from_census_entry_in": "message_difference only (one bit)"},
}

# ============================================ counting rule / degenerate arms
def vkeys(o): return CP.variant_keys(o, STRICT)
def proj_id(key, prim): return key
def proj_drop_on_primitive(names, only_primitive):
    names = frozenset(names)
    def f(key, prim):
        if prim != only_primitive: return key
        return tuple(p for p in key if p[0] not in names)
    return f
OE = proj_drop_on_primitive(["message_difference"], "sha1")

def mk(o, proj, drop):
    drop = frozenset(drop)
    return min(tuple(p for p in proj(k, o.primitive) if p[0] not in drop) for k in vkeys(o))

ROWS = ("primitive","length","message_difference","step_delta","block_index","in_linearized_code")
def fam_md(src):
    n = CP.md_bits(src)
    return [CP.perturb_message_difference(src, tuple(range(k)), f"det{k}") for k in (1,2,4,8,16) if k<=n]
def fam_sd(src):
    out=[]
    for k in (1,2,4,8,16):
        new=PathObject(**{**src.__dict__}); dd=list(src.step_delta)
        for p in range(k): dd[p//32] ^= 1<<(p%32)
        new.step_delta=tuple(dd); new.id=f"{src.id}~SD{k}"; out.append(new)
    return out
def fam_bi(src):
    out=[]
    for v in range(4):
        if v==src.block_index: continue
        new=PathObject(**{**src.__dict__}); new.block_index=v; new.id=f"{src.id}~BI{v}"; out.append(new)
    return out
FAM={"message_difference":fam_md,"step_delta":fam_sd,"block_index":fam_bi}

INSTR = {"honest": ("proj", proj_id), "O_E": ("proj", OE),
         "always_member": ("const", True), "always_non_member": ("const", False)}

def verdict(fam, prim, row, kind):
    ents=[o for o in SHADOW if o.primitive==prim]
    ds=[d for s in ents for d in FAM[fam](s)]
    if kind[0]=="const":
        return "DETECTED" if kind[1] else "NOT DETECTED"
    idx={mk(o,kind[1],(row,)) for o in ents}
    return "DETECTED" if any(mk(d,kind[1],(row,)) in idx for d in ds) else "NOT DETECTED"

cells_adj=[]; cells_all=[]
for fam in FAM:
    for row in ROWS:
        for prim in ("md5","sha1"):
            v={n:verdict(fam,prim,row,k) for n,k in INSTR.items()}
            rec={"family":f"d_{fam}","row":f"delete_{row}","primitive":prim,**v}
            cells_all.append(rec)
            if fam==row: rec["class"]="diagonal"
            elif row=="in_linearized_code": rec["class"]="forced_by_the_graph"
            else:
                rec["class"]="adjudicated"; cells_adj.append(rec)
def count(cells, other):
    return sum(1 for c in cells if c["honest"]!=c[other])
noforced=[c for c in cells_all if c["class"]!="diagonal"]
R["counting_rule"]={
 "adjudicated_cells_per_primitive": len(cells_adj),
 "differing_vs_O_E": count(cells_adj,"O_E"),
 "differing_vs_always_member": count(cells_adj,"always_member"),
 "differing_vs_always_non_member": count(cells_adj,"always_non_member"),
 "differing_vs_honest": 0,
 "honest_verdict_distribution_over_adjudicated":
    {v: sum(1 for c in cells_adj if c["honest"]==v) for v in ("DETECTED","NOT DETECTED")},
 "if_the_forced_by_the_graph_exclusion_is_NOT_applied": {
    "cells": len(noforced),
    "differing_vs_O_E": count(noforced,"O_E"),
    "the_differing_cells": [c for c in noforced if c["honest"]!=c["O_E"]]},
 "diagonal_cells": [c for c in cells_all if c["class"]=="diagonal"],
}
print(json.dumps(R, indent=1, default=str))
