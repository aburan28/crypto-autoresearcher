"""RT4 ARM (b) ATTACK -- TASK-20260826-a9d51e, joint R4-J6 (and O-Q6).

INDEPENDENT construction of the consistent-pair flag-and-dv family EXACTLY as
EXP-DIFFP-f26790 declares it ("replacing the dv by a non-codeword AND setting
the flag False"), offered to the COMMITTED well-formedness gate on BOTH
primitives, with the MEASURED moved-component set read off the COMMITTED
serialiser, and with its sha1 draw-key set compared against the COMMITTED
d_message_difference family's.

IT ANSWERS THREE QUESTIONS THE DECLARATION CANNOT ANSWER ABOUT ITSELF.
 (1) Which CLAUSE of the gate rejects on md5, and is that clause the same
     predicate as the sha1 clause of the same name?
 (2) Is the measured moved set the declared one?
 (3) Is the family a NEW object on sha1, or the committed d_message_difference
     family under a new name?  O-Q6 asks this of the md5 side; this asks it of
     the side where the family IS constructible, which the plan does not.

Nothing under harness/ is modified.  readmit.py is never imported.
"""
from __future__ import annotations

import io
import json
import os
import random
import sys


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
sys.path.insert(0, REPO)

assert "harness.diffpath.readmit" not in sys.modules

from harness.diffpath import census as _CEN                     # noqa: E402
_CEN.quarantine_attestation = lambda: {"sha256_recomputed": "STUBBED",
                                       "bytes_read": 0}
_CEN.scan_corpus = lambda: (_ for _ in ()).throw(
    RuntimeError("RT4: scan_corpus must never be called"))

from harness.diffpath import adjudicator as ADJ                 # noqa: E402
from harness.diffpath import controlpower as CP                 # noqa: E402
from harness.diffpath import depgraph as DG                     # noqa: E402
from harness.diffpath import pathobj as PO                      # noqa: E402
from harness.diffpath import primitives as P                    # noqa: E402

assert "harness.diffpath.readmit" not in sys.modules

STRICT = CP.STRICT
SEEDS = CP.SEEDS
K_VALUES = CP.K_VALUES


class _E:
    def __init__(self, oid, prim, obj):
        self.id, self.primitive, self.obj = oid, prim, obj


class _C:
    def __init__(self, s):
        self.shadow = s


def shadow():
    out = []
    for prim, seed, steps in (("md5", SEEDS["planted_path_generation_md5"], 64),
                              ("sha1", SEEDS["planted_path_generation_sha1"], 80)):
        rng = random.Random(seed)
        for k in range(8):
            cv, m, mp = PO.seeded_pair(rng, prim)
            o = PO.plant_from_pair(f"PLANT-{prim.upper()}-{k:02d}", prim, cv, m,
                                   mp, (0, steps - 1))
            out.append(_E(o.id, prim, o))
    return _C(out)


def consistent_pair_draw(obj, positions, tag):
    """THE FAMILY AS THE CONTRACT DECLARES IT: perturb the message difference
    AND SET the flag False, so the pair stays mutually consistent."""
    new = PO.PathObject(**{**obj.__dict__})
    new.id = f"{obj.id}~CP{tag}"
    if obj.primitive == "md5":
        d = list(obj.delta_m)
        for p in positions:
            d[p // 32] ^= 1 << (p % 32)
        new.delta_m = tuple(d)
        new.delta_m_signed = tuple(PO.bsdr_encode(x) for x in d)
    else:
        d = list(obj.dv)
        for p in positions:
            d[p // 32] ^= 1 << (p % 32)
        new.dv = tuple(d)
    new.in_linearized_code = False          # DECLARED, not recomputed
    return new


def inconsistent_pair_draw(obj, positions, tag):
    """The other side of CTL-PAIR-WF: same dv perturbation, flag left True."""
    new = consistent_pair_draw(obj, positions, tag + "INC")
    new.in_linearized_code = True
    return new


def moved_components(src, drw):
    a = dict(ADJ.serialize(src, STRICT))
    b = dict(ADJ.serialize(drw, STRICT))
    names = list(dict.fromkeys(list(a) + list(b)))
    return sorted(n for n in names if a.get(n, "<absent>") != b.get(n, "<absent>"))


def main():
    out = {}
    cen = shadow()
    out["source_entry_flags"] = {e.id: e.obj.in_linearized_code
                                 for e in cen.shadow}

    rng = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    per = {p: {"constructed": 0, "accepted": 0, "rejected": 0,
               "rejection_reasons": {}} for p in ("md5", "sha1")}
    inc = {p: {"checked": 0, "rejected": 0, "wrongly_accepted": 0}
           for p in ("md5", "sha1")}
    moved_measured = {p: {} for p in ("md5", "sha1")}
    draws = []
    still_codeword = {"sha1": 0}

    for e in cen.shadow:
        src, prim = e.obj, e.primitive
        nbits = CP.md_bits(src)
        for k in K_VALUES:
            plan = [("deterministic", tuple(range(k)))]
            if k >= 1:
                plan += [("seeded", tuple(sorted(rng.sample(range(nbits), k))))
                         for _ in range(DG.R_NEW_FAMILIES)]
            for dt, pos in plan:
                o = consistent_pair_draw(src, pos, f"k{k}-{dt}")
                per[prim]["constructed"] += 1
                bad = DG.wf_violations(o)
                if bad:
                    per[prim]["rejected"] += 1
                    for b in bad:
                        per[prim]["rejection_reasons"][b] = \
                            per[prim]["rejection_reasons"].get(b, 0) + 1
                else:
                    per[prim]["accepted"] += 1
                    draws.append({"primitive": prim, "k": k, "src": src,
                                  "obj": o})
                    mv = tuple(moved_components(src, o))
                    moved_measured[prim][str(mv)] = \
                        moved_measured[prim].get(str(mv), 0) + 1
                if prim == "sha1" and k >= 1:
                    if P.sha1_in_linearized_code(list(o.dv)):
                        still_codeword["sha1"] += 1
                # the two-sided gate: the INCONSISTENT pair must be REJECTED
                oi = inconsistent_pair_draw(src, pos, f"k{k}-{dt}")
                inc[prim]["checked"] += 1
                if DG.wf_violations(oi):
                    inc[prim]["rejected"] += 1
                else:
                    inc[prim]["wrongly_accepted"] += 1

    out["gate_consistent_side_per_primitive"] = per
    out["gate_inconsistent_side_per_primitive"] = inc
    out["measured_moved_component_sets_on_accepted_draws"] = moved_measured
    out["declared_moved_component_set"] = ["message_difference",
                                           "in_linearized_code"]
    out["sha1_perturbed_dv_still_a_codeword_count"] = still_codeword["sha1"]

    # ---- WHICH CLAUSE REJECTS ON MD5, AND IS IT THE SAME PREDICATE? --------
    e_md5 = [e for e in cen.shadow if e.primitive == "md5"][0]
    probe = PO.PathObject(**{**e_md5.obj.__dict__})
    probe.in_linearized_code = False
    probe_flagless = PO.PathObject(**{**e_md5.obj.__dict__})
    out["md5_gate_probe"] = {
        "unmodified_md5_entry_violations": DG.wf_violations(e_md5.obj),
        "md5_entry_with_flag_set_False_violations": DG.wf_violations(probe),
        "md5_entry_with_flag_left_None_violations":
            DG.wf_violations(probe_flagless),
        "note": ("the md5 branch of W3 tests `obj.in_linearized_code is not "
                 "None` and the sha1 branch tests `flag == "
                 "sha1_in_linearized_code(dv)`. TWO DIFFERENT PREDICATES "
                 "SHARING ONE CHECK ID."),
    }

    # ---- IS IT A NEW OBJECT ON SHA-1, OR d_message_difference RENAMED? -----
    cp_keys = {ADJ.canonical(d["obj"], STRICT)
               for d in draws if d["primitive"] == "sha1" and d["k"] >= 1}
    dmd_keys = set()
    dmd_n = 0
    for e, k, dt, o in DG.family_d_draws(cen):
        if e.primitive == "sha1" and k >= 1 and not DG.wf_violations(o):
            dmd_keys.add(ADJ.canonical(o, STRICT))
            dmd_n += 1
    out["sha1_extensional_comparison_against_committed_d_message_difference"] = {
        "consistent_pair_distinct_canonical_keys": len(cp_keys),
        "d_message_difference_distinct_canonical_keys": len(dmd_keys),
        "d_message_difference_accepted_draws": dmd_n,
        "consistent_pair_keys_that_are_ALSO_d_message_difference_keys":
            len(cp_keys & dmd_keys),
        "consistent_pair_keys_OUTSIDE_d_message_difference":
            len(cp_keys - dmd_keys),
        "what_this_can_and_cannot_show": (
            "The two families draw from the SAME shared random.Random at the "
            "SAME seed but consume it in DIFFERENT amounts (64 versus 8 draws "
            "per k), so a key present in one and absent from the other is a "
            "fact about the DRAW PLAN and not about the family's REACH. What "
            "IS a fact about reach is the CONSTRUCTOR: on every accepted "
            "sha1 draw the declared flag False EQUALS "
            "sha1_in_linearized_code(perturbed dv), because CTL-WF check W3 "
            "rejects every draw where it does not -- so the gate-accepted "
            "image of the consistent-pair constructor is CONTAINED IN the "
            "image of the committed perturb_message_difference constructor on "
            "the same positions."),
    }

    # the containment claim, tested constructor-wise on identical positions
    same = diff = 0
    rng2 = random.Random(SEEDS["null_draw_message_difference_perturbed"])
    for e in cen.shadow:
        if e.primitive != "sha1":
            continue
        nbits = CP.md_bits(e.obj)
        for k in (1, 2, 4, 8, 16):
            for _ in range(8):
                pos = tuple(sorted(rng2.sample(range(nbits), k)))
                a = consistent_pair_draw(e.obj, pos, "X")
                b = CP.perturb_message_difference(e.obj, pos, "X")
                if DG.wf_violations(a):
                    continue
                if ADJ.serialize(a, STRICT) == ADJ.serialize(b, STRICT):
                    same += 1
                else:
                    diff += 1
    out["constructor_wise_identity_on_identical_positions_sha1"] = {
        "gate_accepted_consistent_pair_draws_compared": same + diff,
        "serialised_key_IDENTICAL_to_perturb_message_difference": same,
        "serialised_key_DIFFERENT": diff,
    }

    out["readmit_absent_from_sys_modules_at_end"] = (
        "harness.diffpath.readmit" not in sys.modules)
    return out


if __name__ == "__main__":
    r = main()
    with io.open(os.path.join(os.path.dirname(__file__), "rt4_armb.json"),
                 "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps(r, indent=1, sort_keys=True, default=str))
