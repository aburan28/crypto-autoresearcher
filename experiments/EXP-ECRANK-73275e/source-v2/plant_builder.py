"""Frozen plant builders for EXP-ECRANK-73275e v2 (IV-3R / R10, R11).

FROZEN before any R10/R11 step (the v1 null_family freeze discipline
applied to plants, per the amendment's IV-3R plant_builder_freeze).

Two builders:
  - build_plants_n6: the R3-FAMILY SHAPE (amendment IV-3R). The same
    prescribed-square-pattern mechanism with carrier r_n and the n=6
    univariate quadratic solve in t (g = x + t) that produced R3's 28
    certified instances -- NOT the non-elliptic R7 d=(1..1) family. Each
    plant is elliptic (deg s = 4, disc != 0) at build time, a distinct
    (b-tuple, pattern) pair, no shared h0, built inside the frozen box
    (r-height <= 10^4). Plants are derived CONSTRUCTIVELY (prescribe the
    pattern, solve the quadratic, keep deg s = 4 roots) and NEVER import
    R3's found-instance list.
  - build_plants_n8_r7: the R7 family (d=(1..1)) at n=8, elliptic
    (deg s = 3). Each plant is determined by its b-tuple (d=(1..1) fixed,
    r = g(b) with g = polysqrt_trunc(p, 4)).

Both builders derive every object from the named run seed via
random.Random(seed) (the amendment's derivation_discipline). No
derived-seed practice.
"""

import random
from fractions import Fraction as Fr

import ecrank_engine as E
import construct


H_BOX_N6 = 10 ** 4  # frozen box: r-height <= 10^4


def build_plants_n6(engine, seed, n_plants=9, H_box=H_BOX_N6,
                    max_resamples=20000):
    """Build n_plants elliptic n=6 plants from the R3-family shape.

    Returns (plants, coset, build_ledger). Each plant records its
    b-stream position (the index of the (b, dpat) sample that produced it,
    1-indexed over ALL samples, including rejected ones).
    """
    rng = random.Random(seed)
    cosets = engine.eligible_cosets()
    rng_c = random.Random(seed)
    coset = cosets[rng_c.randrange(len(cosets))]
    values = [engine.class_value(m) for m in coset["members"]]
    plants = []
    used_bp = set()    # distinct (b-tuple, pattern) pairs (IV-9)
    used_h0 = set()    # no shared h0 (IV-9)
    ledger = []
    sample_idx = 0
    resamples = 0
    while len(plants) < n_plants and resamples < max_resamples:
        b = construct.sample_b(rng, 6)
        dpat = construct.sample_dpat(rng, 6, values)
        sample_idx += 1
        resamples += 1
        bp_key = (tuple(str(x) for x in b), tuple(dpat))
        entry = {"sample_idx": sample_idx,
                 "b": [str(x) for x in b], "d_pattern": list(dpat)}
        if bp_key in used_bp:
            entry["outcome"] = "skip_duplicate_bp"
            ledger.append(entry)
            continue
        xs = [Fr(x) for x in b]
        A, B, C = construct._n6_quad(engine, xs, dpat)
        roots = construct._quad_rational_roots(A, B, C)
        entry["n_rational_roots"] = len(roots)
        plant = None
        for t in roots:
            g = [Fr(t), Fr(1)]
            r = [engine.peval(g, x) for x in xs]
            if any(ri == 0 for ri in r):
                continue
            hA = max(construct.rat_height(ri) for ri in r)
            if hA > H_box:
                continue
            inst, why = engine.build_instance(xs, dpat, r, 6)
            if inst is None:
                continue
            if inst["deg_s"] != 4:
                continue  # MUST be elliptic deg s = 4 (IV-3R)
            hB = construct.rat_height(t)
            if hA in used_h0:
                continue  # prefer distinct h0 (IV-9)
            plant = {
                "b": [str(x) for x in b],
                "d_pattern": list(dpat),
                "t": str(t),
                "r": [str(x) for x in r],
                "h_A": hA,
                "h_B": hB,
                "deg_s": inst["deg_s"],
                "disc_s": inst["disc_s"],
                "b_stream_position": sample_idx,
                "instance": inst,
            }
            break
        if plant is None:
            entry["outcome"] = "no_valid_elliptic_inbox_root"
            ledger.append(entry)
            continue
        used_bp.add(bp_key)
        used_h0.add(plant["h_A"])
        plant["index"] = len(plants)
        entry["outcome"] = "planted"
        entry["h_A"] = plant["h_A"]
        ledger.append(entry)
        plants.append(plant)
    return plants, coset, ledger


def build_plants_n8_r7(engine, seed, n_plants=9, max_resamples=20000):
    """Build n_plants elliptic n=8 plants from the R7 family (d=(1..1)).

    The R7 family at n=8 is elliptic (deg s = 3). Each plant is determined
    by its b-tuple. Returns (plants, build_ledger).
    """
    rng = random.Random(seed)
    B_INTS = construct.B_INTS
    plants = []
    used_b = set()
    ledger = []
    sample_idx = 0
    resamples = 0
    while len(plants) < n_plants and resamples < max_resamples:
        rest = rng.sample(B_INTS, 6)
        b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
        sample_idx += 1
        resamples += 1
        b_key = tuple(str(x) for x in b)
        entry = {"sample_idx": sample_idx, "b": [str(x) for x in b]}
        if b_key in used_b:
            entry["outcome"] = "skip_duplicate_b"
            ledger.append(entry)
            continue
        p, g, s = engine.mestre_polys(list(b))
        r = [engine.peval(g, x) for x in b]
        inst, why = engine.build_instance(list(b), [1] * 8, r, 8)
        if inst is None:
            entry["outcome"] = "build_rejected"
            entry["reason"] = why
            ledger.append(entry)
            continue
        if inst["deg_s"] != 3:
            entry["outcome"] = "not_deg_s_3"
            entry["deg_s"] = inst["deg_s"]
            ledger.append(entry)
            continue
        hA = inst["r_height"]
        plant = {
            "b": [str(x) for x in b],
            "d_pattern": [1] * 8,
            "r": [str(x) for x in r],
            "h_A": hA,
            "deg_s": inst["deg_s"],
            "disc_s": inst["disc_s"],
            "b_stream_position": sample_idx,
            "instance": inst,
        }
        used_b.add(b_key)
        plant["index"] = len(plants)
        entry["outcome"] = "planted"
        entry["h_A"] = hA
        ledger.append(entry)
        plants.append(plant)
    return plants, ledger
