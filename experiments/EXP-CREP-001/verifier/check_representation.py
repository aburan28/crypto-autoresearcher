#!/usr/bin/env python3
"""EXP-CREP-001 frozen machine verifier (deterministic, stdlib only).

Mechanical verifier for typed representation packages against the frozen
predicates V1-V6 of experiments/EXP-CREP-001/specification.yaml, applied to
the 12 recorded symbolic instances (B in {2,3} x six strata, with embedded
mutated twins).

  V1 typed_completeness : schema-valid total typed dependency graph from the
                          compact pair-product generators to the z_R sink;
                          no untyped macro, no oracle node, no free lookup.
  V2 target_independence: preprocessing artifacts byte-identical across every
                          instance/twin pair (fresh-target mutation control);
                          preprocessing nodes never read the target.
  V3 compactness        : no forbidden payload; declared preprocessing
                          time/advice/state exponents <= 9/4 in B; declared
                          online-materialized target-dependent coordinates
                          exponent <= 5/4 in B.
  V4 exact_support      : support(z_R_constructed) symdiff support(z_R_reference)
                          empty on every recorded instance.
  V5 exact_replay       : every constructed root replays to the exact labelled
                          source tuple set, negative child queries negative,
                          no_relation_unit returns z_R = 1 with no credited
                          split; zero errors.
  V6 cost_caps          : declared exponent certificate aggregates the typed
                          construction maps exactly (phase-max rule) and stays
                          within 9/4 preprocessing and 5/4 online caps,
                          replay accounting included.

Dedup control (CTRL-DEDUP-PRIOR-NEGATIVES): every package is matched against
the BATCH-002 forbidden payload list (EV-CRYPTO-002, DEC-20260724-003) and
the P1553/P1513 duplicate-owner list recorded in the pinned candidate report
(coordination/goals/GOAL-CRYPTO-001/batches/BATCH-001/tasks/TASK-20260722-101/candidate_report.yaml,
pinned commit b8af1551e45fbe4435745239d29f4d141eea3356, git blob
69615720416250cd713c030df9b7414eefc13494). Matches are recorded as
failed_duplicate with the named owner.

CLI:
  python3 check_representation.py --package PACKAGE.json --instances INSTANCES_DIR
Prints the canonical verdict JSON to stdout (byte-deterministic). Exit code
0 on a completed verification (verdict is data); nonzero only on verifier
infrastructure failure (unreadable package/instances, engine crash).
"""
import json
import os
import sys
from fractions import Fraction

VERIFIER_VERSION = "crep-toy-v1"
ENGINE_ID = "crep-toy-v1"

CAP_PREPROCESSING = Fraction(9, 4)
CAP_ONLINE = Fraction(5, 4)

DECK_COUNT = 5
ADMISSIBLE_MARKERS = ["normal", "tangent", "vertical", "repeated"]
INADMISSIBLE_MARKERS = ["identity", "infinity"]

# Frozen node-kind vocabulary. Phase constrains where a kind may appear.
PREPROCESSING_KINDS = {
    "load_pair_product_generators": "compact_generators",
    "build_static_relation_table": "static_relation_table",
    "build_dyadic_index": "dyadic_index",
    "build_chart_index": "chart_index",
}
ONLINE_KINDS = {
    "materialize_resultant_coefficients": "resultant_coefficient_vector",
    "materialize_translated_endpoints": "translated_endpoints",
    "supplied_input": None,  # produces set from params.payload
    "whole_divisor_translation_macro": "whole_divisor_translation",
    "target_fitted_selector": "target_fitted_selector",
    "componentwise_gcd": "support_intermediate",
    "quotient_ring_gcd": "support_intermediate",
    "norm_from_extension": "support_intermediate",
    "multipoint_evaluate": "support_intermediate",
    "modular_compose": "support_intermediate",
    "power_project": "support_intermediate",
    "subresultant_chain": "support_intermediate",
    "displacement_solve": "support_intermediate",
    "restricted_existence_probe": "existence_bits",
    "dyadic_replay": "replay_witness",
    "tuple_replay": "replay_witness",
    "emit_support_factor": "support_factor",
}
ALLOWED_TYPES = {
    "compact_generators", "static_relation_table", "dyadic_index", "chart_index",
    "existence_bits", "replay_witness", "support_intermediate", "support_factor",
    "resultant_coefficient_vector", "translated_endpoints", "quotient_coordinates",
    "supplied_resultant", "supplied_residue", "supplied_common_factor",
    "supplied_source_tuple", "supplied_scalar_character",
    "target_fitted_selector", "whole_divisor_translation",
}
FORBIDDEN_PAYLOAD_TYPES = {
    "resultant_coefficient_vector": "represented degree-B^2 target coefficient vector",
    "translated_endpoints": "Theta(B^3) translated pair endpoints",
    "quotient_coordinates": "Theta(B^3) translated quotient coordinates",
    "supplied_resultant": "supplied resultant",
    "supplied_residue": "supplied residue",
    "supplied_common_factor": "supplied common factor",
    "supplied_source_tuple": "supplied source tuple",
    "supplied_scalar_character": "supplied scalar character",
    "target_fitted_selector": "target-fitted selector",
    "whole_divisor_translation": "whole-divisor translation macro",
}
ORACLE_KINDS = {"supplied_input"}
MACRO_KINDS = {"whole_divisor_translation_macro", "target_fitted_selector"}

# Dedup rules. D1/D2 match the BATCH-002 forbidden payload list
# (EV-CRYPTO-002, DEC-20260724-003). D3 matches the P1553/P1513
# duplicate-owner list in the pinned candidate report (provenance above).
DEDUP_OWNER_EV = "EV-CRYPTO-002"
DEDUP_SIGNATURES = [
    (("endpoint_aggregate", "source_unrank"), "P1551/IDEA-195",
     "endpoint aggregation followed by exact source unranking"),
    (("nonlinear_common_factor_locate",), "P1513/IDEA-121",
     "compact pair products to nonlinear common-factor location and labelled replay"),
    (("pair_state_collision_router",), "P1516",
     "two pair states plus the missing target-local collision router"),
    (("elliptic_net_recurrence",), "P1540",
     "elliptic-net recurrence and supplied-term controls"),
    (("materialize_resultant_coefficients", "subresultant_chain"), "IDEA-063",
     "post-factor subresultant and provenance propagation"),
    (("materialize_resultant_coefficients", "displacement_solve"), "IDEA-071",
     "determinant/displacement reporting from supplied represented data"),
    (("materialize_translated_endpoints", "displacement_solve"), "IDEA-071",
     "determinant/displacement reporting from supplied represented data"),
    (("endpoint_coefficient_access", "source_unrank"), "IDEA-199",
     "endpoint-coefficient access followed by source unranking"),
    (("represented_algebra", "dynamic_split"), "IDEA-266",
     "dynamic splitting after a source algebra is represented"),
    (("query2p1_index",), "P1553/P1513",
     "Query2P1 indexing operation (P1553 gate)"),
    (("pczt_e_reduction",), "P1553/P1513",
     "PCZT-E reduction (Query2P1 renamed per pinned gate r3)"),
]


# --------------------------------------------------------------------------
# Instance reference semantics (independent re-derivation from deck records)
# --------------------------------------------------------------------------

def label_tuples(decks, label):
    per_deck = []
    for k in range(DECK_COUNT):
        occs = [o for o in decks[k] if o["label"] == label]
        if not occs:
            return []
        per_deck.append(occs)
    import itertools
    tuples = []
    for combo in itertools.product(*per_deck):
        if all(o["marker"] in ADMISSIBLE_MARKERS for o in combo):
            tuples.append([dict(o) for o in combo])
    tuples.sort(key=lambda t: json.dumps(t, sort_keys=True))
    return tuples


def extendible_map(decks, M):
    return {l: label_tuples(decks, l) for l in range(M)}


def poly_from_roots(roots):
    coeffs = [1]
    for r in roots:
        new = [0] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new[i] -= c * r
            new[i + 1] += c
        coeffs = new
    return coeffs


def instance_integrity_problems(inst):
    """Independent re-derivation of every reference block from deck records."""
    problems = []
    B = inst["B"]
    M = inst["universe"]["label_count"]
    decks = inst["decks"]
    if len(decks) != DECK_COUNT:
        problems.append("deck_count mismatch")
    for k, deck in enumerate(decks):
        if len(deck) != B:
            problems.append("deck %d slot count %d != B=%d" % (k, len(deck), B))
        for pos, o in enumerate(deck):
            if o["deck"] != k or o["pos"] != pos:
                problems.append("deck %d occurrence position corruption" % k)
    ext = extendible_map(decks, M)
    if sorted(l for l in range(M) if ext[l]) != inst["reference"]["extendible_labels"]:
        problems.append("reference.extendible_labels mismatch")
    T = inst["target"]["label_set"]
    E = sorted(l for l in T if ext[l])
    if E != inst["reference"]["E"]:
        problems.append("reference.E mismatch")
    if inst["reference"]["z_R_roots"] != E:
        problems.append("reference.z_R_roots mismatch")
    if inst["reference"]["z_R_coefficients"] != poly_from_roots(E):
        problems.append("reference.z_R_coefficients mismatch")
    for l in range(M):
        expected = ext[l] if l in E else []
        if inst["reference"]["replay_table"].get(str(l)) != expected:
            problems.append("reference.replay_table mismatch at label %d" % l)
    Tt = inst["mutated_twin"]["target"]["label_set"]
    Et = sorted(l for l in Tt if ext[l])
    if inst["mutated_twin"]["reference_E"] != Et:
        problems.append("mutated_twin.reference_E mismatch")
    if inst["mutated_twin"]["reference_z_R_coefficients"] != poly_from_roots(Et):
        problems.append("mutated_twin.reference_z_R_coefficients mismatch")
    # generator list integrity
    Bn = len(decks[0])
    gens = []
    for i, x in enumerate(decks[0]):
        for j, y in enumerate(decks[1]):
            gid = i * Bn + j
            w = [x["label"]] if (x["label"] == y["label"] and ext[x["label"]]) else []
            gens.append({
                "id": gid,
                "x_ref": {"deck": 0, "pos": i, "label": x["label"]},
                "y_ref": {"deck": 1, "pos": j, "label": y["label"]},
                "endpoint_value": (x["label"] + y["label"]) % M,
                "witnesses": w,
            })
    if gens != inst["pair_product_generators"]:
        problems.append("pair_product_generators mismatch")
    for g in gens:
        if inst["relation_table"].get(str(g["id"])) != g["witnesses"]:
            problems.append("relation_table mismatch at generator %d" % g["id"])
    return problems


# --------------------------------------------------------------------------
# Native schema validation (mirrors package_schema.json; jsonschema absent)
# --------------------------------------------------------------------------

def is_nonneg_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x >= 0


def schema_problems(pkg):
    p = []
    if not isinstance(pkg, dict):
        return ["package is not a JSON object"]
    for key in ["package_id", "kind", "target", "dependency_graph", "exponent_certificate", "semantics", "provenance"]:
        if key not in pkg:
            p.append("missing required key: %s" % key)
    if p:
        return p
    if pkg["kind"] not in ("route", "calibration"):
        p.append("kind must be route or calibration")
    if pkg["target"] != "z_R":
        p.append("target must be z_R")
    g = pkg["dependency_graph"]
    for key in ["nodes", "edges", "roots", "sinks"]:
        if key not in g:
            p.append("dependency_graph missing key: %s" % key)
    if p:
        return p
    ids = set()
    for n in g["nodes"]:
        for key in ["id", "kind", "phase", "produces", "retained", "declared"]:
            if key not in n:
                p.append("node missing key: %s" % key)
                continue
        if n["id"] in ids:
            p.append("duplicate node id: %s" % n["id"])
        ids.add(n.get("id"))
        if n.get("phase") not in ("preprocessing", "online"):
            p.append("node %s bad phase" % n.get("id"))
        if not isinstance(n.get("retained"), bool):
            p.append("node %s retained must be boolean" % n.get("id"))
        d = n.get("declared", {})
        if not is_nonneg_number(d.get("size_exponent_in_B")):
            p.append("node %s declared.size_exponent_in_B must be a nonnegative number" % n.get("id"))
    for e in g["edges"]:
        for key in ["from", "to", "map"]:
            if key not in e:
                p.append("edge missing key: %s" % key)
        if e.get("from") not in ids or e.get("to") not in ids:
            p.append("edge references unknown node: %s->%s" % (e.get("from"), e.get("to")))
        m = e.get("map", {})
        for key in ["input_size_exponent_in_B", "output_size_exponent_in_B", "cost_exponent_in_B"]:
            if not is_nonneg_number(m.get(key)):
                p.append("edge %s->%s map.%s must be a nonnegative number" % (e.get("from"), e.get("to"), key))
    for r in g.get("roots", []):
        if r not in ids:
            p.append("unknown root: %s" % r)
    for s in g.get("sinks", []):
        if s not in ids:
            p.append("unknown sink: %s" % s)
    cert = pkg["exponent_certificate"]
    for key in ["preprocessing", "online", "replay_accounting", "aggregation_rule"]:
        if key not in cert:
            p.append("exponent_certificate missing key: %s" % key)
    if "preprocessing" in cert:
        for key in ["time_exponent_in_B", "retained_advice_exponent_in_B", "retained_state_exponent_in_B"]:
            if not is_nonneg_number(cert["preprocessing"].get(key)):
                p.append("certificate preprocessing.%s must be a nonnegative number" % key)
    if "online" in cert:
        for key in ["time_exponent_in_B", "workspace_exponent_in_B", "materialized_target_dependent_coordinates_exponent_in_B"]:
            if not is_nonneg_number(cert["online"].get(key)):
                p.append("certificate online.%s must be a nonnegative number" % key)
    ra = cert.get("replay_accounting", {})
    for key in ["dyadic_queries_per_tuple", "positive_and_negative_queries_included", "final_exact_source_verification_included"]:
        if key not in ra:
            p.append("replay_accounting missing key: %s" % key)
    sem = pkg["semantics"]
    if sem.get("engine") != ENGINE_ID:
        p.append("semantics.engine must be %s" % ENGINE_ID)
    prov = pkg["provenance"]
    for key in ["built_by", "built_at_run"]:
        if key not in prov:
            p.append("provenance missing key: %s" % key)
    return p


# --------------------------------------------------------------------------
# Toy execution engine (frozen semantics; engine id crep-toy-v1)
# --------------------------------------------------------------------------

def dyadic_levels(M):
    pad = 1
    while pad < M:
        pad *= 2
    levels = 0
    step = 1
    while step <= pad:
        levels += 1
        step *= 2
    return pad, levels


def build_dyadic_index_value(M, ext):
    pad, _ = dyadic_levels(M)
    intervals = []
    step = 1
    while step <= pad:
        a = 0
        while a < pad:
            hi = min(a + step, pad)
            bit = any(ext.get(l) for l in range(a, min(hi, M)))
            intervals.append({"lo": a, "hi": hi, "or_bit": bit})
            a += step
        step *= 2
    return {"universe_pad": pad, "interval_count": len(intervals), "intervals": intervals}


def execute_package(pkg, inst, target_labels):
    """Execute the package graph. Returns (values, trace).

    Preprocessing nodes receive no target argument (structural target
    independence). Online nodes may read the target. All values are
    canonical JSON-able objects; execution is deterministic.
    """
    decks = inst["decks"]
    M = inst["universe"]["label_count"]
    ext = extendible_map(decks, M)
    extendible = {l: t for l, t in ext.items() if t}
    g = pkg["dependency_graph"]
    nodes = {n["id"]: n for n in g["nodes"]}
    preds = {n["id"]: [] for n in g["nodes"]}
    for e in g["edges"]:
        preds[e["to"]].append(e["from"])
    # topological order (deterministic: Kahn with sorted queue)
    indeg = {nid: len(preds[nid]) for nid in nodes}
    queue = sorted(nid for nid in nodes if indeg[nid] == 0)
    order = []
    while queue:
        nid = queue.pop(0)
        order.append(nid)
        for e in g["edges"]:
            if e["from"] == nid:
                indeg[e["to"]] -= 1
                if indeg[e["to"]] == 0:
                    queue.append(e["to"])
        queue.sort()
    if len(order) != len(nodes):
        raise ValueError("dependency graph has a cycle")

    def support_of_target():
        return sorted(l for l in target_labels if extendible.get(l))

    _, probe_levels = dyadic_levels(M)
    values = {}
    trace = {"probe_counts": {}, "credited_splits": [], "target_read_by_preprocessing": False}
    for nid in order:
        node = nodes[nid]
        kind = node["kind"]
        phase = node["phase"]
        inputs = [values[p] for p in sorted(preds[nid])]
        if phase == "preprocessing":
            if kind == "load_pair_product_generators":
                value = {"generators": inst["pair_product_generators"]}
            elif kind == "build_static_relation_table":
                value = {"relation_table": inst["relation_table"]}
            elif kind == "build_dyadic_index":
                value = build_dyadic_index_value(M, ext)
            elif kind == "build_chart_index":
                value = {"deck_occurrences": [
                    [{"pos": o["pos"], "label": o["label"], "marker": o["marker"]} for o in decks[k]]
                    for k in range(DECK_COUNT)]}
            else:
                raise ValueError("unknown preprocessing kind: %s" % kind)
        else:
            if kind == "materialize_resultant_coefficients":
                value = {"coefficient_vector": [1 if extendible.get(l) else 0 for l in range(M)],
                         "target_dependent": True}
            elif kind == "materialize_translated_endpoints":
                value = {"translated_endpoints": [
                    {"generator": gg["id"], "endpoint_value": gg["endpoint_value"]}
                    for gg in inst["pair_product_generators"]],
                    "target_dependent": True}
            elif kind == "supplied_input":
                value = {"supplied": node.get("params", {}).get("payload", "supplied_resultant"),
                         "oracle": True,
                         "simulated_support": support_of_target()}
            elif kind in ("componentwise_gcd", "quotient_ring_gcd", "norm_from_extension",
                          "multipoint_evaluate", "modular_compose", "power_project",
                          "subresultant_chain", "displacement_solve"):
                value = {"support": support_of_target()}
            elif kind in ("whole_divisor_translation_macro", "target_fitted_selector"):
                value = {"support": support_of_target(), "macro": kind}
            elif kind == "restricted_existence_probe":
                bits = {str(l): bool(extendible.get(l)) for l in target_labels}
                trace["probe_counts"][nid] = {
                    "labels_queried": len(target_labels),
                    "dyadic_probes_per_label": probe_levels,
                    "total_probes": len(target_labels) * probe_levels,
                }
                value = {"bits": bits}
            elif kind in ("dyadic_replay", "tuple_replay"):
                if kind == "dyadic_replay":
                    # support comes from the probe/gcd predecessors
                    sup = set()
                    for iv in inputs:
                        if "bits" in iv:
                            sup |= {int(l) for l, b in iv["bits"].items() if b}
                        if "support" in iv:
                            sup |= set(iv["support"])
                        if "simulated_support" in iv:
                            sup |= set(iv["simulated_support"])
                else:
                    sup = set(target_labels)
                replay = {}
                for l in inst["universe"]["labels"]:
                    if l in sup and extendible.get(l):
                        replay[str(l)] = [list(t) for t in extendible[l]]
                    else:
                        replay[str(l)] = []
                trace["probe_counts"].setdefault(nid, {})
                if kind == "dyadic_replay":
                    trace["probe_counts"][nid] = {
                        "labels_replayed": len(sup),
                        "dyadic_descent_queries_per_label": probe_levels,
                        "total_queries": len(sup) * probe_levels,
                    }
                value = {"replay": replay}
            elif kind == "emit_support_factor":
                sup = set()
                for iv in inputs:
                    if "support" in iv:
                        sup |= set(iv["support"])
                    if "bits" in iv:
                        sup |= {int(l) for l, b in iv["bits"].items() if b}
                    if "simulated_support" in iv:
                        sup |= set(iv["simulated_support"])
                    if "replay" in iv:
                        sup |= {int(l) for l, t in iv["replay"].items() if t}
                roots = sorted(sup)
                value = {"z_R_roots": roots, "z_R_coefficients": poly_from_roots(roots)}
            else:
                raise ValueError("unknown online kind: %s" % kind)
        values[nid] = value
    return values, trace


def preprocessing_artifacts_bytes(pkg, inst, target_labels):
    """Canonical bytes of the preprocessing artifacts under a given target."""
    values, _ = execute_package(pkg, inst, target_labels)
    g = pkg["dependency_graph"]
    artifacts = {}
    for n in g["nodes"]:
        if n["phase"] == "preprocessing" and n.get("retained", True):
            artifacts[n["id"]] = values[n["id"]]
    return json.dumps(artifacts, sort_keys=True, separators=(",", ":")).encode("utf-8")


# --------------------------------------------------------------------------
# Dedup control
# --------------------------------------------------------------------------

def dedup_matches(pkg):
    matches = []
    g = pkg["dependency_graph"]
    kinds_in_order = []
    nodes = {n["id"]: n for n in g["nodes"]}
    for n in g["nodes"]:
        if n["kind"] in ORACLE_KINDS:
            payload = n.get("params", {}).get("payload", "supplied_resultant")
            matches.append({
                "rule": "D1",
                "payload_or_pattern": FORBIDDEN_PAYLOAD_TYPES.get(payload, payload),
                "owner": DEDUP_OWNER_EV,
                "evidence_refs": ["EV-CRYPTO-002", "DEC-20260724-003"],
                "node": n["id"],
            })
        if n["kind"] in MACRO_KINDS:
            matches.append({
                "rule": "D2",
                "payload_or_pattern": FORBIDDEN_PAYLOAD_TYPES[nodes[n["id"]]["produces"]],
                "owner": DEDUP_OWNER_EV,
                "evidence_refs": ["EV-CRYPTO-002", "DEC-20260724-003"],
                "node": n["id"],
            })
    # kind sequence in topological-ish (node declaration) order
    for n in g["nodes"]:
        kinds_in_order.append(n["kind"])
    for signature, owner, description in DEDUP_SIGNATURES:
        it = iter(kinds_in_order)
        if all(any(k == sk for k in it) for sk in signature):
            matches.append({
                "rule": "D3",
                "payload_or_pattern": description,
                "owner": owner,
                "evidence_refs": [
                    "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-001/tasks/TASK-20260722-101/candidate_report.yaml@b8af1551e45fbe4435745239d29f4d141eea3356"
                ],
                "signature": list(signature),
            })
    return matches


# --------------------------------------------------------------------------
# Predicates V1-V6
# --------------------------------------------------------------------------

def check_V1(pkg):
    reasons = []
    problems = schema_problems(pkg)
    reasons.extend(problems)
    g = pkg["dependency_graph"]
    nodes = {n["id"]: n for n in g["nodes"]}
    # vocabulary and typing
    for n in g["nodes"]:
        kind = n["kind"]
        if n["phase"] == "preprocessing":
            if kind not in PREPROCESSING_KINDS:
                reasons.append("node %s: kind %s not in frozen preprocessing vocabulary" % (n["id"], kind))
        else:
            if kind not in ONLINE_KINDS:
                reasons.append("node %s: kind %s not in frozen online vocabulary" % (n["id"], kind))
        if n["produces"] not in ALLOWED_TYPES:
            reasons.append("node %s: produces type %s not in frozen type vocabulary" % (n["id"], n["produces"]))
        if kind in PREPROCESSING_KINDS and n["produces"] != PREPROCESSING_KINDS[kind]:
            reasons.append("node %s: produces %s, kind %s produces %s" % (n["id"], n["produces"], kind, PREPROCESSING_KINDS[kind]))
        if kind in ONLINE_KINDS and ONLINE_KINDS[kind] is not None and n["produces"] != ONLINE_KINDS[kind]:
            reasons.append("node %s: produces %s, kind %s produces %s" % (n["id"], n["produces"], kind, ONLINE_KINDS[kind]))
        if kind in ORACLE_KINDS:
            reasons.append("node %s: oracle node (%s) imports an externally supplied object; no free lookup" % (n["id"], kind))
        if kind in MACRO_KINDS:
            reasons.append("node %s: untyped macro kind %s" % (n["id"], kind))
    # graph totality
    roots = set(g["roots"])
    sinks = set(g["sinks"])
    if not roots:
        reasons.append("no roots declared")
    for r in roots:
        if nodes.get(r, {}).get("kind") != "load_pair_product_generators":
            reasons.append("root %s is not a compact pair-product generator source" % r)
    if len(sinks) != 1:
        reasons.append("exactly one z_R sink required, found %d" % len(sinks))
    for s in sinks:
        if nodes.get(s, {}).get("produces") != "support_factor":
            reasons.append("sink %s does not produce support_factor" % s)
    # acyclicity + reachability
    preds = {n["id"]: [] for n in g["nodes"]}
    succs = {n["id"]: [] for n in g["nodes"]}
    for e in g["edges"]:
        preds[e["to"]].append(e["from"])
        succs[e["from"]].append(e["to"])
    indeg = {nid: len(preds[nid]) for nid in nodes}
    queue = sorted(nid for nid in nodes if indeg[nid] == 0)
    seen = 0
    while queue:
        nid = queue.pop(0)
        seen += 1
        for s in succs[nid]:
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
    if seen != len(nodes):
        reasons.append("dependency graph has a cycle")
    reachable_from_roots = set()
    stack = list(roots)
    while stack:
        nid = stack.pop()
        if nid in reachable_from_roots:
            continue
        reachable_from_roots.add(nid)
        stack.extend(succs[nid])
    reaches_sink = set()
    stack = list(sinks)
    while stack:
        nid = stack.pop()
        if nid in reaches_sink:
            continue
        reaches_sink.add(nid)
        stack.extend(preds[nid])
    for nid in nodes:
        if nid not in reachable_from_roots:
            reasons.append("node %s not reachable from roots (free lookup)" % nid)
        if nid not in reaches_sink:
            reasons.append("node %s does not reach the z_R sink (dangling)" % nid)
    # every edge has a complete typed construction map
    for e in g["edges"]:
        m = e.get("map", {})
        for key in ["input_size_exponent_in_B", "output_size_exponent_in_B", "cost_exponent_in_B"]:
            if key not in m:
                reasons.append("edge %s->%s missing typed map key %s" % (e["from"], e["to"], key))
    return {"pass": not reasons, "reasons": sorted(reasons)}


def check_V2(pkg, instances):
    reasons = []
    identical = 0
    pairs = 0
    for inst in instances:
        t_primary = inst["target"]["label_set"]
        t_twin = inst["mutated_twin"]["target"]["label_set"]
        b1 = preprocessing_artifacts_bytes(pkg, inst, t_primary)
        b2 = preprocessing_artifacts_bytes(pkg, inst, t_twin)
        pairs += 1
        if b1 == b2:
            identical += 1
        else:
            reasons.append("preprocessing artifacts diverge under target mutation on %s" % inst["instance_id"])
    return {"pass": not reasons, "reasons": sorted(reasons),
            "pairs_checked": pairs, "pairs_byte_identical": identical}


def check_V3(pkg):
    reasons = []
    g = pkg["dependency_graph"]
    for n in g["nodes"]:
        if n["produces"] in FORBIDDEN_PAYLOAD_TYPES:
            reasons.append("node %s carries forbidden payload: %s" % (n["id"], FORBIDDEN_PAYLOAD_TYPES[n["produces"]]))
    cert = pkg["exponent_certificate"]
    pre = cert["preprocessing"]
    for key in ["time_exponent_in_B", "retained_advice_exponent_in_B", "retained_state_exponent_in_B"]:
        if Fraction(str(pre[key])) > CAP_PREPROCESSING:
            reasons.append("declared preprocessing %s = %s exceeds cap 9/4" % (key, pre[key]))
    td = Fraction(str(cert["online"]["materialized_target_dependent_coordinates_exponent_in_B"]))
    if td > CAP_ONLINE:
        reasons.append("declared online-materialized target-dependent coordinates exponent = %s exceeds cap 5/4"
                       % cert["online"]["materialized_target_dependent_coordinates_exponent_in_B"])
    return {"pass": not reasons, "reasons": sorted(reasons)}


def check_V4(pkg, instances):
    per_instance = {}
    reasons = []
    for inst in instances:
        values, _ = execute_package(pkg, inst, inst["target"]["label_set"])
        g = pkg["dependency_graph"]
        sink = g["sinks"][0]
        roots_constructed = values[sink]["z_R_roots"]
        E = inst["reference"]["E"]
        symdiff = sorted(set(roots_constructed) ^ set(E))
        per_instance[inst["instance_id"]] = {
            "constructed_support": roots_constructed,
            "reference_support": E,
            "support_symmetric_difference": symdiff,
        }
        if symdiff:
            reasons.append("%s: support symmetric difference %s" % (inst["instance_id"], symdiff))
    return {"pass": not reasons, "reasons": sorted(reasons), "per_instance": per_instance}


def check_V5(pkg, instances):
    per_instance = {}
    reasons = []
    for inst in instances:
        values, trace = execute_package(pkg, inst, inst["target"]["label_set"])
        g = pkg["dependency_graph"]
        replay = {}
        for n in g["nodes"]:
            if n["kind"] in ("dyadic_replay", "tuple_replay"):
                replay = values[n["id"]]["replay"]
        sink = g["sinks"][0]
        roots_constructed = values[sink]["z_R_roots"]
        ref_table = inst["reference"]["replay_table"]
        errors = []
        for l in inst["universe"]["labels"]:
            got = replay.get(str(l), [])
            want = ref_table.get(str(l), [])
            if got != want:
                errors.append({"label": l, "expected_tuples": len(want), "got_tuples": len(got)})
        unit_ok = True
        if inst["stratum"] == "no_relation_unit":
            unit_ok = (roots_constructed == [] and trace["credited_splits"] == [])
            if not unit_ok:
                errors.append({"no_relation_unit": "constructed z_R must be 1 with no credited split",
                               "roots": roots_constructed, "credited_splits": trace["credited_splits"]})
        per_instance[inst["instance_id"]] = {
            "replay_errors": errors,
            "replay_error_count": len(errors),
            "constructed_roots": roots_constructed,
            "no_relation_unit_ok": unit_ok,
        }
        if errors:
            reasons.append("%s: %d replay errors" % (inst["instance_id"], len(errors)))
    return {"pass": not reasons, "reasons": sorted(reasons), "per_instance": per_instance}


def check_V6(pkg):
    reasons = []
    g = pkg["dependency_graph"]
    nodes = {n["id"]: n for n in g["nodes"]}
    cert = pkg["exponent_certificate"]
    # Edge phase = phase of the edge's target node; retained preprocessing
    # state = max size exponent over retained preprocessing nodes; online
    # workspace = max over online-edge outputs and online-node sizes.
    pre_edges = [e for e in g["edges"] if nodes[e["to"]]["phase"] == "preprocessing"]
    on_edges = [e for e in g["edges"] if nodes[e["to"]]["phase"] == "online"]

    def frac(x):
        return Fraction(str(x))

    agg_pre_time = max([frac(e["map"]["cost_exponent_in_B"]) for e in pre_edges], default=Fraction(0))
    agg_on_time = max([frac(e["map"]["cost_exponent_in_B"]) for e in on_edges], default=Fraction(0))
    agg_pre_state = max([frac(n["declared"]["size_exponent_in_B"])
                         for n in g["nodes"] if n["phase"] == "preprocessing" and n["retained"]],
                        default=Fraction(0))
    on_outputs = [frac(e["map"]["output_size_exponent_in_B"]) for e in on_edges]
    on_node_sizes = [frac(n["declared"]["size_exponent_in_B"]) for n in g["nodes"] if n["phase"] == "online"]
    agg_on_ws = max(on_outputs + on_node_sizes, default=Fraction(0))

    pre = cert["preprocessing"]
    on = cert["online"]
    if frac(pre["time_exponent_in_B"]) != agg_pre_time:
        reasons.append("certificate preprocessing.time_exponent_in_B=%s does not aggregate construction maps (expected %s)"
                       % (pre["time_exponent_in_B"], agg_pre_time))
    if frac(pre["retained_state_exponent_in_B"]) != agg_pre_state:
        reasons.append("certificate preprocessing.retained_state_exponent_in_B=%s does not aggregate retained construction outputs (expected %s)"
                       % (pre["retained_state_exponent_in_B"], agg_pre_state))
    if frac(on["time_exponent_in_B"]) != agg_on_time:
        reasons.append("certificate online.time_exponent_in_B=%s does not aggregate construction maps (expected %s)"
                       % (on["time_exponent_in_B"], agg_on_time))
    if frac(on["workspace_exponent_in_B"]) != agg_on_ws:
        reasons.append("certificate online.workspace_exponent_in_B=%s does not aggregate online materialization (expected %s)"
                       % (on["workspace_exponent_in_B"], agg_on_ws))
    ra = cert.get("replay_accounting", {})
    if ra.get("positive_and_negative_queries_included") is not True:
        reasons.append("replay accounting does not include positive and negative dyadic queries")
    if ra.get("final_exact_source_verification_included") is not True:
        reasons.append("replay accounting does not include the final exact source verification")
    for key in ["time_exponent_in_B", "retained_advice_exponent_in_B", "retained_state_exponent_in_B"]:
        if frac(pre[key]) > CAP_PREPROCESSING:
            reasons.append("preprocessing %s = %s exceeds cap 9/4" % (key, pre[key]))
    for key in ["time_exponent_in_B", "workspace_exponent_in_B"]:
        if frac(on[key]) > CAP_ONLINE:
            reasons.append("online %s = %s exceeds cap 5/4" % (key, on[key]))
    return {"pass": not reasons, "reasons": sorted(reasons),
            "aggregates": {
                "preprocessing_time": str(agg_pre_time),
                "preprocessing_retained_state": str(agg_pre_state),
                "online_time": str(agg_on_time),
                "online_workspace": str(agg_on_ws),
            }}


# --------------------------------------------------------------------------
# Verdict driver
# --------------------------------------------------------------------------

def load_instances(instances_dir):
    instances = []
    for name in sorted(os.listdir(instances_dir)):
        if name.startswith("INST-") and name.endswith(".json") and not name.startswith("._"):
            with open(os.path.join(instances_dir, name)) as f:
                instances.append(json.load(f))
    return instances


def verify_package(pkg, instances):
    verdict = {
        "package_id": pkg["package_id"],
        "kind": pkg["kind"],
        "route_id": pkg.get("route_id"),
        "verifier_version": VERIFIER_VERSION,
        "engine": ENGINE_ID,
        "instance_ids": [i["instance_id"] for i in instances],
    }
    # instance integrity (instrument check)
    integrity = {}
    for inst in instances:
        probs = instance_integrity_problems(inst)
        if probs:
            integrity[inst["instance_id"]] = probs
    verdict["instance_integrity"] = {"pass": not integrity, "problems": integrity}
    # dedup control (recorded for every package; routes only are scored as
    # failed_duplicate - calibration fixtures are instruments, not routes)
    matches = dedup_matches(pkg)
    verdict["dedup"] = {
        "matched": bool(matches),
        "matches": matches,
        "failed_duplicate": bool(matches) and pkg["kind"] == "route",
        "owners": sorted({m["owner"] for m in matches}),
    }
    v1 = check_V1(pkg)
    # V2/V4/V5 execute even when V1 fails (the engine can execute oracle and
    # macro nodes); a graph the engine cannot execute at all (e.g. cyclic)
    # fails the predicate with the engine error recorded as the reason.
    def guarded(fn):
        try:
            return fn()
        except ValueError as exc:
            return {"pass": False, "reasons": ["engine cannot execute package: %s" % exc]}
    v2 = guarded(lambda: check_V2(pkg, instances))
    v2.setdefault("pairs_checked", 0)
    v2.setdefault("pairs_byte_identical", 0)
    v3 = check_V3(pkg)
    v4 = guarded(lambda: check_V4(pkg, instances))
    v4.setdefault("per_instance", {})
    v5 = guarded(lambda: check_V5(pkg, instances))
    v5.setdefault("per_instance", {})
    v6 = check_V6(pkg)
    verdict["predicates"] = {"V1": v1, "V2": v2, "V3": v3, "V4": v4, "V5": v5, "V6": v6}
    first_failed = None
    for name in ["V1", "V2", "V3", "V4", "V5", "V6"]:
        if not verdict["predicates"][name]["pass"]:
            first_failed = name
            break
    verdict["first_failed_predicate"] = first_failed
    verdict["route_verdict"] = "PASS" if first_failed is None else "FAIL"
    verdict["declared_exponents"] = pkg["exponent_certificate"]
    return verdict


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main():
    args = sys.argv[1:]
    package_path = None
    instances_dir = None
    i = 0
    while i < len(args):
        if args[i] == "--package":
            package_path = args[i + 1]
            i += 2
        elif args[i] == "--instances":
            instances_dir = args[i + 1]
            i += 2
        else:
            print("unknown argument: %s" % args[i], file=sys.stderr)
            sys.exit(2)
    if not package_path or not instances_dir:
        print("usage: check_representation.py --package P --instances DIR", file=sys.stderr)
        sys.exit(2)
    with open(package_path) as f:
        pkg = json.load(f)
    instances = load_instances(instances_dir)
    if len(instances) != 12:
        print("expected 12 recorded instances, found %d" % len(instances), file=sys.stderr)
        sys.exit(3)
    verdict = verify_package(pkg, instances)
    print(canonical_json(verdict))


if __name__ == "__main__":
    main()
