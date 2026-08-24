"""THE NOVELTY ADJUDICATOR -- the bound entry point of EXP-DIFFP-fe894e.

The canonicaliser, the strict/permissive membership decision, and the drivers
for CTL-PLANT, CTL-NULL, CTL-OBS and CTL-NEARBY.

WHAT A VERDICT MEANS, AND WHAT IT DOES NOT (contract interpretation_limits,
restated here because this is the file a reader will open first):

  MEMBER      "equivalent to a census entry under the verified generators".
              NEVER "identical to a published path" and never "already known".
  NON-MEMBER  scoped to the census that produced it.  Against a census with
              zero readable entries it means "not in an empty census", which
              is NO INFORMATION AT ALL, and every record citing such a verdict
              must say so in the same sentence.  IT IS NEVER NOVELTY.

NOVELTY IS UNVERIFIED AND NO NOVELTY CLAIM IS MADE OR LICENSED by anything in
this module, for any path, for either primitive.  No search over the difference
space is performed anywhere in this package (IR-8).

STRICT AND PERMISSIVE ARE TWO FIELDS AND ARE NEVER MERGED (IR-5).  Excluding a
real equivalence over-declares novelty; admitting a false one under-declares
it; reporting both bounds the error in a direction a reader can see.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from . import equivalence as EQ
from . import primitives as P
from .census import Census
from .pathobj import PathObject, plant_from_pair, seeded_pair

MASK32 = P.MASK32


# ---------------------------------------------------------------------------
# the canonicaliser
# ---------------------------------------------------------------------------

def normalise_conditions(obj: PathObject, e5_active: bool):
    """Normal form of a real condition set.

    Dedup + sort + contradiction detection: the same (step, operand, bit)
    pinned to two different values is unsatisfiable, and every unsatisfiable
    condition set has the SAME normal form.  This is the analogue of the normal
    form E5's verification check decides on the bounded alphabet.

    SCOPE LIMIT, STATED: E5 was VERIFIED against full solution-set enumeration
    on the bounded alphabet only.  That the same normal form is solution-set
    exact on real per-step 32-bit condition sets is NOT established here and is
    NOT claimed.
    """
    keys = sorted({(c.step, c.operand, c.bit, c.value) for c in obj.conditions})
    if not e5_active:
        return tuple(keys)
    seen: dict = {}
    for (s, op, b, v) in keys:
        if seen.get((s, op, b), v) != v:
            return ("UNSAT",)
        seen[(s, op, b)] = v
    return tuple(keys)


def serialize(obj: PathObject, gens: frozenset) -> tuple:
    """The canonical serialisation under the generator set `gens`."""
    if obj.primitive == "md5":
        diff_part = tuple(obj.delta_m or ())
    else:
        diff_part = tuple(obj.dv or ())
    parts = [("primitive", obj.primitive), ("length", obj.length),
             ("message_difference", diff_part),
             ("step_delta", tuple(obj.step_delta)),
             ("conditions", normalise_conditions(obj, "E5" in gens))]
    if "E4" not in gens:
        # without E4 the signed-digit REPRESENTATION is part of the identity
        parts.append(("signed_representation", tuple(obj.step_delta_signed)))
    if "E6" not in gens:
        parts.append(("block_index", obj.block_index))
    if "E1" not in gens:
        parts.append(("step_start", obj.step_range[0]))
    if obj.primitive == "sha1":
        parts.append(("in_linearized_code", obj.in_linearized_code))
    return tuple(parts)


def canonical(obj: PathObject, gens: frozenset) -> tuple:
    """Canonical form: minimise the serialisation over the generated group.

    QUANTIFIER ORDER (contract equivalence_declaration.quantifier_order):
    for every candidate P there EXISTS a census entry C and there EXISTS a
    group element g with g(P) = C; g may depend on both P and C.  Minimising
    the serialisation over the orbit realises exactly that existential and
    claims nothing stronger.
    """
    base = EQ.align_E1(obj) if ("E1" in gens and obj.primitive == "sha1") else obj
    variants = [base]
    if "E3" in gens:
        variants = variants + [EQ.act_E3_negate(v) for v in variants]
    if "E2" in gens and obj.primitive == "sha1":
        variants = [EQ.act_E2_rotate(v, b) for v in variants for b in range(32)]
    return min(serialize(v, gens) for v in variants)


def orbit_images(obj: PathObject, gens: frozenset) -> list[PathObject]:
    """Every image CTL-PLANT must recall, one per verified generator."""
    out: list[PathObject] = []
    if "E3" in gens:
        out.append(EQ.act_E3_negate(obj))
    if "E6" in gens:
        out.append(EQ.act_E6_reindex(obj, 3))
    if "E1" in gens and obj.primitive == "sha1":
        out += [EQ.act_E1_shift(obj, s) for s in EQ.E1_SHIFTS]
    if "E2" in gens and obj.primitive == "sha1":
        out += [EQ.act_E2_rotate(obj, b) for b in (1, 7, 16, 31)]
    return out


def diff_vector(obj: PathObject) -> list[int]:
    base = list(obj.delta_m or ()) if obj.primitive == "md5" else list(obj.dv or ())
    return base + list(obj.step_delta)


def hamming_distance(a: list[int], b: list[int]) -> int | None:
    """Declared distance on canonical forms: bit distance of the difference
    vectors.  Incomparable (None) when the vectors have different lengths --
    a different step_range extent is a declared_non_generator, so those objects
    are not near each other, they are not comparable at all."""
    if len(a) != len(b):
        return None
    return sum(bin((x ^ y) & MASK32).count("1") for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# membership
# ---------------------------------------------------------------------------

@dataclass
class Adjudication:
    candidate_id: str
    primitive: str
    strict_verdict: str                 # MEMBER | NON-MEMBER
    strict_matched_entry: str | None
    permissive_verdict: str             # MEMBER | NON-MEMBER
    permissive_matched_entry: str | None
    strict_generators: tuple
    permissive_generators: tuple
    closest_entry: str | None = None
    closest_distance: int | None = None
    census_readable_entries: int = 0
    census_plantable_entries: int = 0
    scope_note: str = ""

    def to_record(self) -> dict:
        d = dict(self.__dict__)
        d["strict_generators"] = list(self.strict_generators)
        d["permissive_generators"] = list(self.permissive_generators)
        return d


class Adjudicator:
    def __init__(self, census: Census, verified: frozenset,
                 declared: frozenset = frozenset(EQ.ALL_GENERATORS)):
        self.census = census
        self.strict = frozenset(verified)
        self.permissive = frozenset(declared)
        self._index: dict = {}
        for mode, gens in (("strict", self.strict), ("permissive", self.permissive)):
            idx: dict = {}
            for e in census.plantable_entries():
                idx.setdefault(canonical(e.obj, gens), []).append(e.id)
            self._index[mode] = idx

    def adjudicate(self, obj: PathObject) -> Adjudication:
        s_key = canonical(obj, self.strict)
        p_key = canonical(obj, self.permissive)
        s_hit = self._index["strict"].get(s_key)
        p_hit = self._index["permissive"].get(p_key)

        best_id, best_d = None, None
        v = diff_vector(obj)
        for e in self.census.plantable_entries():
            d = hamming_distance(v, diff_vector(e.obj))
            if d is None:
                continue
            if best_d is None or d < best_d:
                best_id, best_d = e.id, d

        n_readable = len(self.census.readable)
        return Adjudication(
            candidate_id=obj.id, primitive=obj.primitive,
            strict_verdict="MEMBER" if s_hit else "NON-MEMBER",
            strict_matched_entry=s_hit[0] if s_hit else None,
            permissive_verdict="MEMBER" if p_hit else "NON-MEMBER",
            permissive_matched_entry=p_hit[0] if p_hit else None,
            strict_generators=tuple(sorted(self.strict)),
            permissive_generators=tuple(sorted(self.permissive)),
            closest_entry=best_id, closest_distance=best_d,
            census_readable_entries=n_readable,
            census_plantable_entries=len(self.census.plantable_entries()),
            scope_note=(
                "NON-MEMBER is scoped to this census. Readable (literature) "
                f"entries: {n_readable}. With {n_readable} readable entries a "
                "NON-MEMBER verdict against the literature means 'not in an "
                "empty census' and is NOT novelty."),
        )


# ---------------------------------------------------------------------------
# control drivers
# ---------------------------------------------------------------------------

def ctl_plant(adj: Adjudicator, census: Census) -> dict:
    """CTL-PLANT: planted-positive recall, as an INTEGER FRACTION."""
    hits = attempts = 0
    misses: list[dict] = []
    per_class: dict = {}
    orbit_sizes: dict = {}
    canon_counts: dict = {}
    for e in census.shadow:
        cases = [("planted", e.obj)]
        for img in orbit_images(e.obj, adj.strict):
            cls = (img.path_data or {}).get("kind", "image")
            cases.append((cls, img))
        # ORBIT SIZE = how many DISTINCT objects the equivalence identifies,
        # measured against the FINEST identity (serialize with no generator in
        # force).  Reported alongside the number of distinct CANONICAL forms in
        # the same orbit, which is a correctness check and must be 1.  Both are
        # integers, and an orbit of size 1 -- an equivalence doing no work on
        # this object -- is visible as such rather than hidden.
        raw = {serialize(o, frozenset()) for _, o in cases}
        orbit_sizes[e.id] = len(raw)
        canon_counts[e.id] = len({canonical(o, adj.strict) for _, o in cases})
        for cls, o in cases:
            attempts += 1
            a = adj.adjudicate(o)
            rec = per_class.setdefault(f"{e.primitive}:{cls}",
                                       {"hits": 0, "attempts": 0})
            rec["attempts"] += 1
            if a.strict_verdict == "MEMBER":
                hits += 1
                rec["hits"] += 1
            else:
                misses.append({"planted_entry": e.id, "case": cls,
                               "candidate_id": o.id,
                               "closest_entry": a.closest_entry,
                               "closest_distance": a.closest_distance})
    dist: dict = {}
    for v in orbit_sizes.values():
        dist[v] = dist.get(v, 0) + 1
    return {
        "control": "CTL-PLANT",
        "recall_hits": hits, "recall_attempts": attempts,
        "recall_fraction": f"{hits}/{attempts}",
        "passed": hits == attempts and attempts > 0,
        "per_class": per_class,
        "misses": misses,
        "orbit_size_distribution": {str(k): v for k, v in sorted(dist.items())},
        "orbit_size_note": (
            "Orbit size is the number of DISTINCT OBJECTS, under the FINEST "
            "identity (serialisation with no generator in force), among "
            "{planted path} u {its images under every verified generator}. It "
            "measures how much work the equivalence does. An orbit of size 1 "
            "means the equivalence identifies nothing for that object and is "
            "reported as such rather than hidden."),
        "distinct_canonical_forms_per_orbit": canon_counts,
        "distinct_canonical_forms_note": (
            "A CORRECTNESS check, not a measure of work: every orbit must "
            "collapse to exactly 1 canonical form, or CTL-OBS direction (ii) "
            "has found a canonicaliser defect."),
        "orbit_image_count_per_entry": {e.id: len(orbit_images(e.obj, adj.strict))
                                        for e in census.shadow},
    }


def _null_draw_md5(rng: random.Random, weight: int) -> PathObject:
    """Family (a): MD5 delta_m uniform at MATCHED Hamming weight."""
    bits = rng.sample(range(16 * 32), weight)
    delta = [0] * 16
    for b in bits:
        delta[b // 32] |= 1 << (b % 32)
    cv, m, mp = seeded_pair(rng, "md5", delta_m=delta)
    return plant_from_pair(f"NULL-MD5-{rng.getrandbits(32):08x}", "md5",
                           cv, m, mp, (0, 63), source_ref="null_draw",
                           provenance="internal")


def _null_draw_sha1(rng: random.Random, in_code: bool) -> PathObject:
    """Families (b) and (c): SHA-1 DVs uniform IN the linearized code, and
    uniform in the UNCONSTRAINED word space."""
    if in_code:
        seed16 = [rng.getrandbits(32) for _ in range(16)]
        cv, m, mp = seeded_pair(rng, "sha1", delta_m=seed16)
        obj = plant_from_pair(f"NULL-SHA1C-{rng.getrandbits(32):08x}", "sha1",
                              cv, m, mp, (0, 79), source_ref="null_draw",
                              provenance="internal")
        return obj
    seed16 = [rng.getrandbits(32) for _ in range(16)]
    cv, m, mp = seeded_pair(rng, "sha1", delta_m=seed16)
    obj = plant_from_pair(f"NULL-SHA1U-{rng.getrandbits(32):08x}", "sha1",
                          cv, m, mp, (0, 79), source_ref="null_draw",
                          provenance="internal")
    # unconstrained family: overwrite the DV with a uniform word vector, which
    # is in general NOT a codeword -- `in_linearized_code` is RECOMPUTED, never
    # assumed.
    words = [rng.getrandbits(32) for _ in range(80)]
    obj.dv = tuple(words)
    obj.dv_seed_window = tuple(words[:16])
    obj.in_linearized_code = P.sha1_in_linearized_code(words)
    return obj


def ctl_null(adj: Adjudicator, census: Census, seeds: dict, n: int = 1000) -> dict:
    """CTL-NULL, against a census CONTAINING PLANTABLE ENTRIES (IR-4).

    A null control against an empty census returns NON-MEMBER for everything
    trivially and has measured NOTHING.  The plantable-entry attestation below
    is what distinguishes this run from that vacuous one.
    """
    plantable = census.plantable_entries()
    attest = {
        "plantable_entries": len(plantable),
        "plantable_entry_ids": [e.id for e in plantable],
        "vacuous": len(plantable) == 0,
        "statement": (
            f"This null was adjudicated against a census containing "
            f"{len(plantable)} entries a draw could POSSIBLY have matched "
            f"({sum(1 for e in plantable if e.primitive == 'md5')} md5, "
            f"{sum(1 for e in plantable if e.primitive == 'sha1')} sha1), so a "
            f"false positive was possible. A null against an empty census "
            f"would be VACUOUS and is not what was run."),
    }
    if not plantable:
        return {"control": "CTL-NULL", "status": "VACUOUS",
                "plantable_census_attestation": attest,
                "note": "IR-4: recorded VACUOUS; this does not discharge the control."}

    md5_weights = [sum(bin(d).count("1") for d in e.obj.delta_m)
                   for e in census.shadow if e.primitive == "md5"]
    families = {}
    for fam, seed in (("md5_delta_m", seeds["null_draw_md5_delta_m"]),
                      ("sha1_dv_in_code", seeds["null_draw_sha1_dv_in_code"]),
                      ("sha1_dv_unconstrained", seeds["null_draw_sha1_dv_unconstrained"])):
        rng = random.Random(seed)
        strict_fp = perm_fp = 0
        fp_examples: list[dict] = []
        closest = None
        in_code_count = 0
        for _ in range(n):
            if fam == "md5_delta_m":
                obj = _null_draw_md5(rng, rng.choice(md5_weights))
            else:
                obj = _null_draw_sha1(rng, fam == "sha1_dv_in_code")
                in_code_count += 1 if obj.in_linearized_code else 0
            a = adj.adjudicate(obj)
            if a.strict_verdict == "MEMBER":
                strict_fp += 1
                if len(fp_examples) < 5:
                    fp_examples.append({"candidate": obj.id, "mode": "strict",
                                        "matched": a.strict_matched_entry})
            if a.permissive_verdict == "MEMBER":
                perm_fp += 1
                if len(fp_examples) < 10:
                    fp_examples.append({"candidate": obj.id, "mode": "permissive",
                                        "matched": a.permissive_matched_entry})
            if a.closest_distance is not None and (
                    closest is None or a.closest_distance < closest["distance"]):
                closest = {"candidate": obj.id, "entry": a.closest_entry,
                           "distance": a.closest_distance,
                           "distance_units": "bits of the concatenated "
                                             "message-difference and per-step "
                                             "modular-difference vector"}
        families[fam] = {
            "draws": n,
            "strict_false_positives": strict_fp,
            "permissive_false_positives": perm_fp,
            "seed": seed,
            "closest_non_matching_draw": closest,
            "draws_in_linearized_code": in_code_count,
        }
    return {
        "control": "CTL-NULL",
        "status": "RUN",
        "plantable_census_attestation": attest,
        "families": families,
        "strict_false_positive_total": sum(f["strict_false_positives"]
                                           for f in families.values()),
        "permissive_false_positive_total": sum(f["permissive_false_positives"]
                                               for f in families.values()),
        "never_merged_note": ("strict and permissive counts are separate fields "
                              "and are not merged, averaged or summed together "
                              "into one number (IR-5)"),
    }


def ctl_obs(adj: Adjudicator, census: Census, seed: int, slice_n: int = 512) -> dict:
    """CTL-OBS, both directions (KN-TECH-080 audit 2).

    (i) two DISTINCT ground-truth objects with EQUAL canonical form -- the
        equivalence is too coarse.  REPORTED, not required to be zero.
    (ii) an object and a KNOWN-equivalent image with DIFFERENT canonical forms
        -- the canonicaliser is incorrect.  Must be ZERO; any discrepancy is an
        implementation defect and a STOP.
    """
    rng = random.Random(seed)
    seen: dict = {}
    collisions: list[dict] = []
    objs = 0
    for prim, steps in (("md5", 64), ("sha1", 80)):
        for _ in range(slice_n):
            cv, m, mp = seeded_pair(rng, prim)
            o = plant_from_pair(f"OBS-{prim}-{objs:04d}", prim, cv, m, mp,
                                (0, steps - 1), source_ref="ctl_obs_slice",
                                provenance="internal")
            objs += 1
            key = canonical(o, adj.strict)
            gt = EQ.ground_truth_signature(o)
            if key in seen:
                other_id, other_gt = seen[key]
                if other_gt != gt:
                    collisions.append({
                        "object_a": other_id, "ground_truth_signature_a": list(other_gt),
                        "object_b": o.id, "ground_truth_signature_b": list(gt),
                        "shared_canonical_form_digest": str(hash(key)),
                    })
            else:
                seen[key] = (o.id, gt)

    discrepancies: list[dict] = []
    checks = 0
    for e in census.shadow:
        base = canonical(e.obj, adj.strict)
        for img in orbit_images(e.obj, adj.strict):
            checks += 1
            if canonical(img, adj.strict) != base:
                discrepancies.append({
                    "object": e.obj.id, "image": img.id,
                    "generator": (img.path_data or {}).get("kind"),
                })
    return {
        "control": "CTL-OBS",
        "direction_i": {
            "what": "distinct ground-truth objects with equal canonical form",
            "slice": f"{objs} seeded planted objects over both primitives "
                     f"({slice_n} per primitive), full step ranges, seed {seed}",
            "distinct_objects_examined": objs,
            "distinct_canonical_forms": len(seen),
            "collisions_found": len(collisions),
            "collisions": collisions,
            "required_to_be_zero": False,
        },
        "direction_ii": {
            "what": "known-equivalent images with different canonical forms",
            "checks": checks,
            "discrepancies_found": len(discrepancies),
            "discrepancies": discrepancies,
            "required_to_be_zero": True,
            "passed": len(discrepancies) == 0,
        },
    }


def ctl_nearby(seed: int, n: int = 1000) -> dict:
    """CTL-NEARBY: the SHA-0 expansion, the closest object where the hoped-for
    structure differs.  The IDENTICAL in_linearized_code test is applied."""
    rng = random.Random(seed)
    sha0_as_sha1 = 0
    sha1_as_sha1 = 0
    for _ in range(n):
        w16 = [rng.getrandbits(32) for _ in range(16)]
        if P.sha1_in_linearized_code(P.sha0_expand(w16, 80)):
            sha0_as_sha1 += 1
        if P.sha1_in_linearized_code(P.sha1_expand(w16, 80)):
            sha1_as_sha1 += 1
    return {
        "control": "CTL-NEARBY",
        "n": n, "seed": seed,
        "sha0_codewords_testing_as_sha1": sha0_as_sha1,
        "sha0_rate_fraction": f"{sha0_as_sha1}/{n}",
        "sha1_codewords_testing_as_sha1": sha1_as_sha1,
        "sha1_rate_fraction": f"{sha1_as_sha1}/{n}",
        "separated": sha0_as_sha1 == 0 and sha1_as_sha1 == n,
        "limit": ("SHA-0's expansion is implemented from the stated one-rotation "
                  "difference and is NOT gated on a published SHA-0 digest; no "
                  "claim is made about SHA-0 digests or SHA-0 security."),
    }


CODE_PATH_FINGERPRINT_FUNCTIONS = (
    "harness.diffpath.adjudicator.canonical",
    "harness.diffpath.adjudicator.serialize",
    "harness.diffpath.adjudicator.normalise_conditions",
    "harness.diffpath.adjudicator.Adjudicator.adjudicate",
    "harness.diffpath.adjudicator.hamming_distance",
    "harness.diffpath.equivalence.align_E1",
    "harness.diffpath.equivalence.act_E1_shift",
    "harness.diffpath.equivalence.act_E2_rotate",
    "harness.diffpath.equivalence.act_E3_negate",
    "harness.diffpath.equivalence.act_E6_reindex",
    "harness.diffpath.verifier.conforms",
    "harness.diffpath.pathobj.plant_from_pair",
)
