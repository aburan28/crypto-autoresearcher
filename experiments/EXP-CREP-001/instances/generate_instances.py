#!/usr/bin/env python3
"""EXP-CREP-001 frozen instance generator (deterministic, stdlib only).

Generates the 12 recorded symbolic labelled-deck instances
(B in {2, 3} crossed with six strata) with embedded mutated twins, per
experiments/EXP-CREP-001/specification.yaml inputs.recorded_instances.

Seed policy (frozen): deterministic construction and audit; no randomness
anywhere. Instances are fully public combinatorial labelled-deck objects:
five signed, coloured decks of B occurrence records each, a target label
set, the pair-product generator list (size exactly B^2, deck0 x deck1), the
reference support set E (extendible target labels, by construction), the
reference z_R = product over labels in E, and the reference replay table.
Each instance carries a mutated twin (same decks and preprocessing universe,
different target label set) for the fresh-target mutation control.

Public semantics rules (recorded inside every instance file):
  - A label is COMPLETE when it has at least one occurrence in every deck.
  - A source tuple for a label is a choice of one occurrence per deck
    (cartesian product over decks).
  - A tuple is ADMISSIBLE when every occurrence marker is admissible
    (markers 'identity' and 'infinity' make a tuple inadmissible; 'normal',
    'tangent', 'vertical', 'repeated' are admissible).
  - A label is EXTENDIBLE when it has at least one admissible tuple.
  - E = extendible labels intersected with the target label set.
  - Pair-product generator g=(x,y), x from deck 0, y from deck 1, witnesses
    label l iff x.label == y.label == l and l is extendible.
"""
import itertools
import json
import os
import sys

DECK_COUNT = 5
B_VALUES = [2, 3]
STRATA = [
    "no_relation_unit",
    "single_hit",
    "multi_hit",
    "collision_duplicate_endpoints",
    "exceptional_markers",
    "repeated_source",
]
DECK_COLOURS = ["red", "blue", "green", "gold", "white"]
ADMISSIBLE_MARKERS = ["normal", "tangent", "vertical", "repeated"]
INADMISSIBLE_MARKERS = ["identity", "infinity"]

GENERATOR_VERSION = "crep-instances-v1"


def universe_size(B):
    return 4 * B + 2


def target_labels(B):
    return list(range(1, B + 1))


def twin_target_labels(B):
    return list(range(B + 1, 2 * B + 1))


def filler_pool(B):
    M = universe_size(B)
    return [0] + list(range(2 * B + 1, M))


def sign_of(label, deck, pos):
    return 1 if (label + deck + pos) % 2 == 0 else -1


def make_occ(label, deck, pos, marker):
    return {
        "deck": deck,
        "pos": pos,
        "label": label,
        "sign": sign_of(label, deck, pos),
        "colour": DECK_COLOURS[deck],
        "marker": marker,
    }


def mandated_decks(B, stratum):
    """Per-deck list of (label, marker) pairs mandated by the stratum design.

    Deck capacities (B slots per deck) are filled afterwards by the
    deterministic filler rule.
    """
    T = target_labels(B)
    M = universe_size(B)
    decks = [[] for _ in range(DECK_COUNT)]
    if stratum == "no_relation_unit":
        # Every target label misses deck 4: z_R = 1, no split may be credited.
        for k in range(4):
            decks[k] = [(t, "normal") for t in T]
    elif stratum == "single_hit":
        # Label 1 complete; other targets miss decks 1 and 4. Fillers are
        # chosen (below) so that all generator endpoints are distinct.
        for k in range(DECK_COUNT):
            decks[k].append((1, "normal"))
        for k in (0, 2, 3):
            for t in T[1:]:
                decks[k].append((t, "normal"))
    elif stratum == "multi_hit":
        hits = T if B == 2 else T[:2]
        for k in range(DECK_COUNT):
            for t in hits:
                decks[k].append((t, "normal"))
        for k in range(4):
            for t in T:
                if t not in hits:
                    decks[k].append((t, "normal"))
    elif stratum == "collision_duplicate_endpoints":
        # Label 1 complete. Deck 0 carries c0 and deck 1 carries c1 with
        # c0 + c1 == 2 (mod M), so the false pair (c0, c1) collides with the
        # true witnessing pair (1, 1) at endpoint value 2.
        c0 = B + 1  # a twin-target label; placed once, never extendible
        c1 = (M + 2 - c0) % M
        decks[0] = [(1, "normal"), (c0, "normal")]
        decks[1] = [(1, "normal"), (c1, "normal")]
        for k in (2, 3):
            decks[k] = [(1, "normal")] + [(t, "normal") for t in T[1:]]
        decks[4] = [(1, "normal")]
    elif stratum == "exceptional_markers":
        # Label 1: complete with tangent (deck 1) and vertical (deck 3)
        # markers -> admissible, extendible.
        # Label 2: complete but identity-marked at deck 2 -> inadmissible.
        # Label 3 (B=3): complete but infinity-marked at deck 4 -> inadmissible.
        decks[0] = [(t, "normal") for t in T]
        decks[1] = [(1, "tangent")] + [(t, "normal") for t in T[1:]]
        decks[2] = [(1, "normal"), (2, "identity")] + [(t, "normal") for t in T[2:]]
        decks[3] = [(1, "vertical")] + [(t, "normal") for t in T[1:]]
        if B == 2:
            decks[4] = [(t, "normal") for t in T]
        else:
            decks[4] = [(1, "normal"), (2, "normal"), (3, "infinity")]
    elif stratum == "repeated_source":
        # Label 1 has two occurrences in deck 2 -> exactly two distinct
        # admissible tuples. Other targets are incomplete.
        decks[0] = [(t, "normal") for t in T]
        decks[1] = [(t, "normal") for t in T]
        if B == 2:
            decks[2] = [(1, "normal"), (1, "normal")]
        else:
            decks[2] = [(1, "normal"), (1, "normal"), (2, "normal")]
        decks[3] = [(t, "normal") for t in T]
        decks[4] = [(1, "normal")]
    else:
        raise ValueError("unknown stratum: %s" % stratum)
    return decks


def generator_endpoints(decks, M):
    """Endpoint values of the deck0 x deck1 pair-product generators."""
    endpoints = []
    for x in decks[0]:
        for y in decks[1]:
            endpoints.append((x["label"] + y["label"]) % M)
    return endpoints


def fill_decks(label_marker_decks, B, stratum):
    """Fill every deck to exactly B slots with filler labels.

    Deterministic: candidates are taken in pool order; each filler label is
    used in at most two decks (so no filler can become complete/extendible)
    and never twice in the same deck. For single_hit, a filler is accepted
    only if all generator endpoints stay distinct (clean no-collision
    baseline).
    """
    M = universe_size(B)
    decks = [[make_occ(lbl, k, pos, mk) for pos, (lbl, mk) in enumerate(slots)]
             for k, slots in enumerate(label_marker_decks)]
    usage = {}
    for deck in decks:
        for o in deck:
            usage[o["label"]] = usage.get(o["label"], 0) + 1
    for k in range(DECK_COUNT):
        while len(decks[k]) < B:
            placed = False
            for cand in filler_pool(B):
                if usage.get(cand, 0) >= 2:
                    continue
                if any(o["label"] == cand for o in decks[k]):
                    continue
                if stratum == "single_hit" and k in (0, 1):
                    trial = [dict(o) for o in decks[k]] + [make_occ(cand, k, len(decks[k]), "normal")]
                    trial_decks = [trial if kk == k else decks[kk] for kk in range(DECK_COUNT)]
                    eps = generator_endpoints(trial_decks, M)
                    if len(set(eps)) != len(eps):
                        continue
                decks[k].append(make_occ(cand, k, len(decks[k]), "normal"))
                usage[cand] = usage.get(cand, 0) + 1
                placed = True
                break
            if not placed:
                raise RuntimeError("filler pool exhausted for deck %d (%s, B=%d)" % (k, stratum, B))
    return decks


def label_tuples(decks, label):
    """All admissible source tuples for a label (canonical order)."""
    per_deck = []
    for k in range(DECK_COUNT):
        occs = [o for o in decks[k] if o["label"] == label]
        if not occs:
            return []
        per_deck.append(occs)
    tuples = []
    for combo in itertools.product(*per_deck):
        if all(o["marker"] in ADMISSIBLE_MARKERS for o in combo):
            tuples.append([dict(o) for o in combo])
    tuples.sort(key=lambda t: json.dumps(t, sort_keys=True))
    return tuples


def extendible_map(decks, M):
    """label -> admissible tuple list; empty list means not extendible."""
    return {l: label_tuples(decks, l) for l in range(M)}


def poly_from_roots(roots):
    """Integer coefficient list of prod_{r in roots}(x - r), ascending order."""
    coeffs = [1]
    for r in roots:
        new = [0] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new[i] -= c * r
            new[i + 1] += c
        coeffs = new
    return coeffs


def build_generators(decks, M, ext):
    """Pair-product generators: all deck0 x deck1 pairs, exactly B^2."""
    B = len(decks[0])
    generators = []
    for i, x in enumerate(decks[0]):
        for j, y in enumerate(decks[1]):
            gid = i * B + j
            witnesses = []
            if x["label"] == y["label"] and ext[x["label"]]:
                witnesses = [x["label"]]
            generators.append({
                "id": gid,
                "x_ref": {"deck": 0, "pos": i, "label": x["label"]},
                "y_ref": {"deck": 1, "pos": j, "label": y["label"]},
                "endpoint_value": (x["label"] + y["label"]) % M,
                "witnesses": witnesses,
            })
    return generators


def build_instance(B, stratum):
    M = universe_size(B)
    T = target_labels(B)
    Ttwin = twin_target_labels(B)
    decks = fill_decks(mandated_decks(B, stratum), B, stratum)
    ext = extendible_map(decks, M)
    extendible_labels = sorted(l for l in range(M) if ext[l])
    E = sorted(l for l in T if ext[l])
    E_twin = sorted(l for l in Ttwin if ext[l])
    generators = build_generators(decks, M, ext)
    relation_table = {str(g["id"]): list(g["witnesses"]) for g in generators}
    endpoint_seen = {}
    endpoint_collisions = []
    for g in generators:
        e = g["endpoint_value"]
        if e in endpoint_seen:
            endpoint_collisions.append(sorted([endpoint_seen[e], g["id"]]))
        else:
            endpoint_seen[e] = g["id"]
    endpoint_collisions.sort()
    replay_table = {str(l): (ext[l] if l in E else []) for l in range(M)}
    replay_table_twin = {str(l): (ext[l] if l in E_twin else []) for l in range(M)}
    instance = {
        "instance_id": "INST-%d-%s" % (B, stratum),
        "generator": "experiments/EXP-CREP-001/instances/generate_instances.py",
        "generator_version": GENERATOR_VERSION,
        "B": B,
        "stratum": stratum,
        "deck_count": DECK_COUNT,
        "semantics_rules": {
            "completeness_rule": "a label is complete when it has at least one occurrence in every deck",
            "tuple_rule": "a source tuple chooses one occurrence of the label per deck",
            "admissible_markers": ADMISSIBLE_MARKERS,
            "inadmissible_markers": INADMISSIBLE_MARKERS,
            "extendible_rule": "a label is extendible when it has at least one admissible tuple",
            "support_rule": "E = extendible labels intersected with the target label set",
            "witness_rule": "generator (x,y) witnesses label l iff x.label == y.label == l and l is extendible",
            "endpoint_rule": "endpoint_value = (x.label + y.label) mod universe_size",
        },
        "universe": {"label_count": M, "labels": list(range(M))},
        "deck_colours": DECK_COLOURS,
        "decks": decks,
        "target": {"label_set": T},
        "mutated_twin": {
            "target": {"label_set": Ttwin},
            "reference_E": E_twin,
            "reference_z_R_roots": E_twin,
            "reference_z_R_coefficients": poly_from_roots(E_twin),
            "reference_replay_table": replay_table_twin,
        },
        "pair_product_generators": generators,
        "relation_table": relation_table,
        "endpoint_collisions": endpoint_collisions,
        "reference": {
            "extendible_labels": extendible_labels,
            "E": E,
            "z_R_roots": E,
            "z_R_coefficients": poly_from_roots(E),
            "replay_table": replay_table,
        },
    }
    return instance


def instance_integrity_problems(inst):
    """Self-check; the verifier independently re-runs these derivations."""
    problems = []
    B = inst["B"]
    M = inst["universe"]["label_count"]
    decks = inst["decks"]
    if len(decks) != DECK_COUNT:
        problems.append("deck_count mismatch")
    for k, deck in enumerate(decks):
        if len(deck) != B:
            problems.append("deck %d has %d slots, expected %d" % (k, len(deck), B))
    ext = extendible_map(decks, M)
    if sorted(l for l in range(M) if ext[l]) != inst["reference"]["extendible_labels"]:
        problems.append("extendible_labels mismatch")
    T = inst["target"]["label_set"]
    if sorted(l for l in T if ext[l]) != inst["reference"]["E"]:
        problems.append("reference E mismatch")
    Tt = inst["mutated_twin"]["target"]["label_set"]
    if sorted(l for l in Tt if ext[l]) != inst["mutated_twin"]["reference_E"]:
        problems.append("twin reference E mismatch")
    gens = build_generators(decks, M, ext)
    if gens != inst["pair_product_generators"]:
        problems.append("pair_product_generators mismatch")
    if inst["reference"]["z_R_coefficients"] != poly_from_roots(inst["reference"]["E"]):
        problems.append("z_R coefficients mismatch")
    return problems


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for B in B_VALUES:
        for stratum in STRATA:
            inst = build_instance(B, stratum)
            problems = instance_integrity_problems(inst)
            if problems:
                raise RuntimeError("instance %s failed self-check: %s" % (inst["instance_id"], problems))
            path = os.path.join(out_dir, inst["instance_id"] + ".json")
            with open(path, "w") as f:
                json.dump(inst, f, indent=2, sort_keys=True)
                f.write("\n")
            written.append((inst["instance_id"], len(inst["reference"]["E"])))
    for iid, esize in written:
        print("generated %s (|E|=%d)" % (iid, esize))
    print("total instances: %d" % len(written))


if __name__ == "__main__":
    main()
