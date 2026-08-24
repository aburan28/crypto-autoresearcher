"""RED-TEAM ADVERSARIAL INSTRUMENTS -- TASK-20260824-e9d21a, joints J8/J11/J13.

MECHANISM: a RUN-TIME PROJECTION/WRAPPER over the committed classes, exactly the
contract's `ablation_mechanism`, EXCEPT that the projection may be CONDITIONAL ON
THE PRIMITIVE and may be a LOSSY RE-KEYING rather than a deletion -- neither of
which `controlpower.project()` can express, which is why these instruments are
outside the contract's declared lattice.  NO COMMITTED FILE IS MODIFIED; nothing
under harness/ is written.  Everything below imports the committed modules and
reuses the committed census, generators, serialisation and draws.
"""
import os, sys, json, random
sys.path.insert(0, "/home/user/crypto-autoresearcher")
from harness.diffpath import adjudicator as ADJ
from harness.diffpath import equivalence as EQ
from harness.diffpath import primitives as P
from harness.diffpath import controlpower as CP
from harness.diffpath import census as CEN

# FIREWALL: the committed build_census() calls quarantine_attestation(), which
# opens the Tier-A payload 'rb' to hash it. This session refuses that read by any
# route, so the function is STUBBED IN THIS PROCESS ONLY (a run-time monkeypatch;
# NO COMMITTED FILE IS TOUCHED). Nothing this review measures depends on it: only
# `census.shadow` is used, and the shadow entries are built from the two planted
# seeds and do not read the payload.
CEN.quarantine_attestation = lambda: {
    "path": "<NOT OPENED BY THE RED TEAM SESSION>", "bytes_hashed": 0,
    "sha256_recomputed": "0" * 64, "sha256_expected": None, "match": None,
    "read_mode": "STUBBED -- the red-team session never opened the payload",
    "parsed": False, "attestation": "stubbed by TASK-20260824-e9d21a"}

STRICT = CP.STRICT
census = CEN.build_census(CP.SEEDS["planted_path_generation_md5"],
                          CP.SEEDS["planted_path_generation_sha1"],
                          scan={"candidates": []})
SHADOW = list(census.shadow)

# ---- committed variant list, via the committed mirror (self-checking) --------
def vkeys(obj, gens=STRICT):
    return CP.variant_keys(obj, gens)

# ---- the adversarial projections ------------------------------------------
def proj_drop(names):
    names = frozenset(names)
    return lambda key, prim: tuple(p for p in key if p[0] not in names)

def proj_drop_on_primitive(names, only_primitive):
    names = frozenset(names)
    def f(key, prim):
        if prim != only_primitive:
            return key
        return tuple(p for p in key if p[0] not in names)
    return f

def proj_lossy_wordset(key, prim):
    """O-A: replace message_difference VALUE by the SET of differing word indices."""
    out = []
    for (n, v) in key:
        if n == "message_difference":
            out.append((n, tuple(i for i, w in enumerate(v) if w != 0)))
        else:
            out.append((n, v))
    return tuple(out)

def proj_lossy_weight(key, prim):
    """O-A': replace message_difference VALUE by its Hamming weight."""
    out = []
    for (n, v) in key:
        if n == "message_difference":
            out.append((n, sum(bin(w).count("1") for w in v)))
        else:
            out.append((n, v))
    return tuple(out)

def proj_seed16_sha1(key, prim):
    """O-RT2: on sha1 read only the first 16 words of the message difference."""
    if prim != "sha1":
        return key
    return tuple((n, (v[:16] if n == "message_difference" else v)) for (n, v) in key)

def proj_seed16_sha1_noflag(key, prim):
    return tuple(p for p in proj_seed16_sha1(key, prim)
                 if p[0] != "in_linearized_code")

class Instr:
    """An adjudicator defined by a projection of the committed serialisation."""
    def __init__(self, name, proj):
        self.name, self.proj = name, proj
        self.index = {"strict": {}, "permissive": {}}
        for mode, gens in (("strict", STRICT), ("permissive", CP.PERMISSIVE)):
            idx = {}
            for e in SHADOW:
                idx.setdefault(self.canon(e.obj, gens), []).append(e.id)
            self.index[mode] = idx
    def canon(self, obj, gens=STRICT):
        return min(self.proj(k, obj.primitive) for k in vkeys(obj, gens))
    def verdict(self, obj, mode="strict"):
        gens = STRICT if mode == "strict" else CP.PERMISSIVE
        hit = self.index[mode].get(self.canon(obj, gens))
        return ("MEMBER", hit[0]) if hit else ("NON-MEMBER", None)

# ---- the strengthened suite, run against an arbitrary instrument -----------
NULL = CP.null_draws(census, n=1000)

def run_suite(I):
    r = {"instrument": I.name}
    # CTL-PLANT
    hits = att = 0
    for e in SHADOW:
        cases = [e.obj] + list(ADJ.orbit_images(e.obj, STRICT))
        for o in cases:
            att += 1
            if I.verdict(o, "strict")[0] == "MEMBER":
                hits += 1
    r["CTL_PLANT"] = f"{hits}/{att}"
    r["CTL_PLANT_full"] = (hits == att)
    # CTL-NULL a,b,c
    fp = {}
    for fam, d in NULL.items():
        s = sum(1 for o in d["draws"] if I.verdict(o, "strict")[0] == "MEMBER")
        p = sum(1 for o in d["draws"] if I.verdict(o, "permissive")[0] == "MEMBER")
        fp[fam] = {"strict_fp": s, "permissive_fp": p, "draws": len(d["draws"])}
    r["CTL_NULL"] = fp
    r["CTL_NULL_strict_fp_total"] = sum(v["strict_fp"] for v in fp.values())
    # CTL-NULL-D primary arm, exactly the committed construction
    rng = random.Random(CP.SEEDS["null_draw_message_difference_perturbed"])
    cells = {}
    for e in SHADOW:
        src = e.obj
        nbits = CP.md_bits(src)
        for k in CP.K_VALUES:
            plan = [("deterministic", tuple(range(k)))]
            if k >= 1:
                plan += [("seeded", tuple(sorted(rng.sample(range(nbits), k))))
                         for _ in range(CP.R_SEEDED)]
            for dt, pos in plan:
                obj = CP.perturb_message_difference(src, pos, f"k{k}-{dt}")
                key = f"{e.primitive}|k={k}"
                c = cells.setdefault(key, {"draws": 0, "member": 0})
                c["draws"] += 1
                if I.verdict(obj, "strict")[0] == "MEMBER":
                    c["member"] += 1
    r["CTL_NULL_D_per_primitive_k"] = cells
    r["CTL_NULL_D_member_k_ge_1_md5"] = sum(
        c["member"] for kk, c in cells.items() if kk.startswith("md5") and "k=0" not in kk)
    r["CTL_NULL_D_member_k_ge_1_sha1"] = sum(
        c["member"] for kk, c in cells.items() if kk.startswith("sha1") and "k=0" not in kk)
    k0m = sum(c["member"] for kk, c in cells.items() if "k=0" in kk)
    k0d = sum(c["draws"] for kk, c in cells.items() if "k=0" in kk)
    r["CTL_NULL_D_k0"] = f"{k0m}/{k0d}"
    old = (not r["CTL_PLANT_full"]) or r["CTL_NULL_strict_fp_total"] > 0
    dm = r["CTL_NULL_D_member_k_ge_1_md5"] + r["CTL_NULL_D_member_k_ge_1_sha1"]
    r["DETECTED_by_OLD_suite"] = "DETECTED" if old else "NOT DETECTED"
    r["DETECTED_by_STRENGTHENED_suite"] = (
        "DETECTED" if (old or dm > 0 or k0m != k0d) else "NOT DETECTED")
    r["PASSES_STRENGTHENED_SUITE_AS_AN_INSTRUMENT"] = (
        r["CTL_PLANT_full"] and r["CTL_NULL_strict_fp_total"] == 0
        and dm == 0 and k0m == k0d)
    # the sub-arm the battery's DETECTION_RULE never reads
    rng2 = random.Random(CP.SEEDS["null_draw_message_difference_perturbed"])
    sub = {"draws": 0, "member": 0}
    for e in SHADOW:
        if e.primitive != "sha1":
            continue
        plan = [tuple([1] + [0] * 15)] + [tuple(rng2.getrandbits(32) for _ in range(16))
                                          for _ in range(CP.R_SEEDED)]
        for w16 in plan:
            if not any(w16):
                continue
            obj = CP.perturb_by_codeword(e.obj, w16, "rt")
            sub["draws"] += 1
            if I.verdict(obj, "strict")[0] == "MEMBER":
                sub["member"] += 1
    r["SUBARM_D_SHA1_INCODE_member"] = sub
    return r
