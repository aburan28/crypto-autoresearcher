"""Prospective exact chain-height/lattice instrument; importing runs no study.

The frozen F97 panel is executed only by run_experiment/main. Development uses
explicit p5/p7/p11 parameters. auxiliary_catalog is rebuilt and charged on each
run. Oracle density/height/tree tables never enter candidate root extraction.
All integer root boxes are signed range(-W+1,W), including when W>p/2;
different integer representatives are retained until verified point relations
are deduplicated. Cost components are sequential or explicitly inclusive.
"""
from __future__ import annotations

import argparse
from collections import Counter as Bag
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path
import random
import sys
import time

try:
    from tools import lattice_ic_factorbase as fb
    from tools import lattice_ic_polynomial as poly
    from tools.lattice_ic_core import Counter, Curve, Field, encode_point, rank_mod, write_artifacts
except ModuleNotFoundError:
    import lattice_ic_factorbase as fb
    import lattice_ic_polynomial as poly
    from lattice_ic_core import Counter, Curve, Field, encode_point, rank_mod, write_artifacts


SCHEMA = "lattice_ic.combined.v1"
FIXTURE = {"target": [97, 0, 2], "auxiliary": [97, 1, 0], "depths": [0, 1, 2, 3],
           "coordinate_bounds": [2, 4, 8, 16, 32, 97], "tuple_lengths": [2, 3, 5],
           "reduction_m": 2, "reduction_t": 1, "reduction_L": 0,
           "selected_fibers": "canonical first complete-kernel finite fiber with nonempty actual target base, fixed before height filtering",
           "root_boxes": "signed integers -W+1..W-1 for every original/intermediate x; weight W",
           "target_schedule": "every finite G point per selected fiber/W; O retained as density and homogeneous-rank cell, finite S3 unavailable",
           "caps": {"n": 64, "D": 256, "coefficient_bits": 4096}}
ARMS = ("chain", "no_chain_list")
CONTROLS = ("identity_window", "positive_dimension_chain", "kernel_poles", "random_same_size", "coordinate_relabel")
UNPRICED = ["Python allocation, serialization, hashing and arithmetic instructions below named calls",
            "no heterogeneous primitive-operation total or cryptographic-scale discovery cost",
            "Groebner/HNF/LLL calls counted with measured times; their internal bit-operation costs not separately priced"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _point(curve, encoded):
    return poly._decode_point(curve, encoded)


def _center(x, p):
    return x if x <= p//2 else x-p


def _fraction(a, b):
    return {"numerator": a, "denominator": b, "defined": b != 0}


def _cost(counter, wall, cpu, scope):
    result = poly._cost(counter, wall, cpu, scope)
    result["unpriced_work"] = list(UNPRICED)
    return result


def _check_height(height, p, fiber, W):
    require(height["W"] == W, "changed height bound")
    expected_sets = []
    for rows, key in ((fiber["paths"], "source_chains"), (fiber["membership_paths"], "target_chains")):
        expected = []
        for source in rows:
            # Point-chain equations themselves are checked independently by
            # fb.check_catalog before these heights can be used.
            centered = [None if point is None else (point[0][0]+p//2) % p-p//2 for point in source["points"]]
            maximum = max((abs(value) for value in centered if value is not None), default=None)
            finite = None not in centered
            expected.append({"source": source.get("source", source.get("source_lift")), "target": source.get("target"),
                "points": source["points"], "centered_x": centered, "finite": finite, "max_abs_x": maximum,
                "pole_indices": [i for i, value in enumerate(centered) if value is None],
                "retained": finite and maximum < W})
        require(height[key] == expected, "incorrect centered chain or strict-height retention")
        expected_sets.append(expected)
    source, target = expected_sets
    allowed = {fb._label(row["target"]) for row in target if row["retained"]}
    original = fiber["bases"]["list"]
    retained = [point for point in original if fb._label(point) in allowed]
    require(height["base_before"] == original and height["base_after"] == retained and
            height["M_before"] == len(original) and height["M_after"] == len(retained) and
            height["rejected_points"] == [point for point in original if point not in retained], "wrong retained target base")
    require(height["point_retention"] == _fraction(len(retained), len(original)) and
            height["source_chain_retention"] == _fraction(sum(row["retained"] for row in source), len(source)) and
            height["target_chain_retention"] == _fraction(sum(row["retained"] for row in target), len(target)), "wrong retention denominator")
    for records, key in ((source, "source_max_height_histogram"), (target, "target_max_height_histogram")):
        values = Bag(row["max_abs_x"] for row in records if row["finite"])
        require(height[key] == [[value, values[value]] for value in sorted(values)], "height distribution incomplete")
    require(height["fullfield_baseline"] == (W >= p), "fullfield mislabeled as a small-height case")
    poly._check_cost(height["cost"])
    require(height["cost"]["counter"]["operations"].get("height.coordinate_inspected", 0) ==
            sum(len(row["centered_x"]) for row in source+target), "unpaid chain-height census")
    return retained


def _check_density(record, p, coefficients, group_encoded, base_encoded, m):
    curve = Curve(Field(p), *coefficients)
    group = [_point(curve, point) for point in group_encoded]
    base = [_point(curve, point) for point in base_encoded]
    index = {point: i for i, point in enumerate(group)}
    counts = [int(point is None) for point in group]
    layers = []
    transitions = 0
    for _ in range(m):
        following = [0]*len(group)
        for i, total in enumerate(group):
            if counts[i]:
                for point in base:
                    following[index[curve.add(total, point)]] += counts[i]
                    transitions += 1
        counts = following
        layers.append(counts)
    require(record["m"] == m and record["M"] == len(base) and record["r"] == len(group)
            and record["base"] == base_encoded and record["targets"] == group_encoded, "wrong density parameters")
    require(record["histogram"] == counts and record["layers"] == layers and sum(counts) == len(base)**m and
            record["first_moment"] == {"numerator": len(base)**m, "denominator": len(group)} and
            record["coverage"] == sum(value > 0 for value in counts), "wrong all-target density/first moment")
    require(len(record["witnesses"]) == len(group), "missing density witness cells")
    for target, count, witness in zip(group, counts, record["witnesses"]):
        require((witness is not None) == (count > 0), "false zero/nonzero density witness")
        if witness is not None:
            points = [_point(curve, point) for point in witness]
            require(len(points) == m and all(point in base for point in points) and poly._sum(curve, points) == target, "false oracle point identity")
    poly._check_cost(record["cost"])
    require(record["cost"]["counter"]["operations"].get("oracle.dp_transition", 0) == transitions, "unpaid density DP transitions")
    return counts


def _check_tree(record, p, coefficients, group_encoded, base_encoded, m, density_counts):
    curve = Curve(Field(p), *coefficients)
    base = [_point(curve, point) for point in base_encoded]
    group = [_point(curve, point) for point in group_encoded]
    shape = _tree_shape(m)
    require(record["m"] == m and record["M"] == len(base) and record["base"] == base_encoded and
            record["shape"] == [list(pair) for pair in shape] and record["ordered_tuple_total"] == len(base)**m, "wrong tree parameters")
    # Recursive verifier folds the fixed tree; no producer tree_census call.
    cache, marginals = {}, {}
    transitions = 0
    def evaluate(node):
        nonlocal transitions
        if node < m:
            return {(point, -1, False): 1 for point in base}, 1
        left, right = shape[node-m]
        ld, nl = evaluate(left)
        rd, nr = evaluate(right)
        values, heights = Bag(), Bag()
        for (a, x, oa), n in ld.items():
            for (b, y, ob), k in rd.items():
                transitions += 1
                point = curve.add(a, b)
                centered = None if point is None else (point[0][0]+p//2) % p-p//2
                values[(point, max(x, y, -1 if centered is None else abs(centered)), oa or ob or point is None)] += n*k
                heights[centered] += n*k
        marginals[node] = {"left": left, "right": right, "subtree_leaves": nl+nr,
            "full_tuple_height_counts": [[height, n*len(base)**(m-nl-nr)] for height, n in sorted(heights.items(), key=lambda pair: (-p if pair[0] is None else pair[0]))]}
        return values, nl+nr
    distribution, _ = evaluate(m+len(shape)-1)
    require(record["nodes"] == [marginals[node] for node in range(m, m+len(shape))], "false intermediate node heights")
    expected_targets = []
    for point in group:
        rows = sorted([height, branch, count] for (target, height, branch), count in distribution.items() if target == point)
        expected_targets.append({"R": encode_point(curve, point), "count": sum(row[2] for row in rows), "max_abs_intermediate_and_O": rows})
    require(record["uniform_targets"] == expected_targets and [row["count"] for row in expected_targets] == density_counts, "tree heights do not preserve all-target counts")
    planted = record["planted"]
    require(planted["size"] == int(bool(base)), "wrong planted cohort denominator")
    if base:
        witness = planted["tree"]
        require(witness["leaves"] == [base_encoded[0]]*m, "adaptive planted tuple")
        values = [base[0]]*m
        require(len(witness["nodes"]) == len(shape), "missing planted tree node")
        for row, (left, right) in zip(witness["nodes"], shape):
            point = curve.add(values[left], values[right])
            values.append(point)
            require(row == {"left": left, "right": right, "point": encode_point(curve, point),
                    "branch": "O" if point is None else "affine", "centered_x": None if point is None else _center(point[0][0], p)}, "false planted tree identity/height")
        require(witness["sum"] == encode_point(curve, values[-1]), "planted sum wrong")
    else:
        require(planted["tree"] is None, "invented planted tuple from empty base")
    poly._check_cost(record["cost"])
    require(record["cost"]["counter"]["operations"].get("oracle.tree_dp_transition", 0) == transitions, "unpaid tree transitions")


def _check_suite(suite, p, coefficients, group_encoded, base_encoded, lengths=(2, 3, 5)):
    require(suite["is_candidate_input"] is False and [row["m"] for row in suite["density"]] == list(lengths) and
            [row["m"] for row in suite["trees"]] == [m for m in lengths if m in (3, 5)], "missing density/tree panel")
    counts = {m: _check_density(row, p, coefficients, group_encoded, base_encoded, m) for m, row in zip(lengths, suite["density"])}
    for row in suite["trees"]:
        _check_tree(row, p, coefficients, group_encoded, base_encoded, row["m"], counts[row["m"]])
    poly._check_cost(suite["setup_cost"])
    return sum(len(rows) for rows in counts.values())


def _check_public_rank(record, p, coefficients, group_encoded, base_encoded, target_encoded, decompositions, P_encoded, r, multiplier):
    """Reconstruct allowed public knowledge and rows independently of producer."""
    curve = Curve(Field(p), *coefficients)
    group = [_point(curve, point) for point in group_encoded]
    base = [_point(curve, point) for point in base_encoded]
    target, P = _point(curve, target_encoded), _point(curve, P_encoded)
    require(record["target"] == target_encoded and record["P"] == P_encoded and record["base"] == base_encoded and record["action_multiplier"] == multiplier, "wrong rank context/action")
    action = record["action"]
    images = [None if point is None else (curve.field.mul(multiplier, point[0]), point[1]) for point in group]
    require(all(curve.is_on_curve(point) and point in group for point in images), "nonstable action used for rank")
    lambdas = [k for k in range(1, r) if curve.mul(k, P) == images[group.index(P)]]
    require(len(lambdas) == 1, "uncertified action eigenvalue")
    lam = lambdas[0]
    require(all(curve.mul(lam, point) == image for point, image in zip(group, images)) and
            action == {"preserved": True, "admitted": True, "lambda": lam,
                "multiplier": curve.field.encode(multiplier), "all_G": [{"point": encode_point(curve, point), "image": encode_point(curve, image)} for point, image in zip(group, images)],
                "scalar_candidates": lambdas, "reason": None}, "false all-G scalar-action certificate")
    known, public_rows = {None: 0}, [{"point": None, "scalar": 0, "sign": 0, "exponent": 0}]
    current = P
    for exponent in range(r):
        value = pow(lam, exponent, r)
        require(current == curve.mul(value, P), "false public orbit scalar")
        for sign, point in ((1, current), (-1, curve.neg(current))):
            scalar = sign*value % r
            if point in known:
                require(known[point] == scalar, "inconsistent known log")
            else:
                known[point] = scalar
                public_rows.append({"point": encode_point(curve, point), "scalar": scalar, "sign": sign, "exponent": exponent})
        current = images[group.index(current)]
        if current == P:
            break
    require(record["public_known"]["generator"] == P_encoded and record["public_known"]["points"] == public_rows, "injected verifier known-log table")
    original_variables = base+([] if target is None or target in base else [target])
    reps, lookup = [], {}
    for point in original_variables:
        if point in lookup:
            continue
        members = {}
        current, scalar = point, 1
        for exponent in range(r):
            members[current] = scalar
            members[curve.neg(current)] = -scalar % r
            current = images[group.index(current)]
            scalar = scalar*lam % r
            if current == point:
                break
        rep = min(members, key=fb._key)
        norm = pow(members[rep], -1, r)
        for member, value in members.items():
            lookup[member] = (len(reps), value*norm % r)
        reps.append(rep)
    raw_rows, rows = [], []
    for encoded in decompositions:
        points = [_point(curve, point) for point in encoded]
        require(len(points) == 2 and all(point in base for point in points) and poly._sum(curve, points) == target, "false rank decomposition")
        raw, row = [0]*len(original_variables), [0]*len(reps)
        for sign, point in [(1, point) for point in points]+([] if target is None else [(-1, target)]):
            raw[original_variables.index(point)] += sign
            column, weight = lookup[point]
            row[column] += sign*weight
        raw_rows.append([value % r for value in raw])
        rows.append([value % r for value in row])
    K = []
    for i, point in enumerate(reps):
        if point in known:
            row = [0]*(len(reps)+1)
            row[i], row[-1] = 1, -known[point] % r
            K.append(row)
    unknown = [i for i, point in enumerate(reps) if point not in known]
    normalized = [[row[i] for i in unknown]+[sum(coefficient*known[point] for point, coefficient in zip(reps, row) if point in known) % r] for row in rows]
    rank = fb._independent_rank
    stacked = K+[row+[0] for row in rows]
    known_rank, total_rank = rank(K, r), rank(stacked, r)
    require(total_rank == rank([row[:-1] for row in stacked], r) and total_rank-known_rank == rank(normalized, r), "inconsistent normalized affine equations")
    require(record["variables"] == [encode_point(curve, point) for point in reps] and record["raw_variables"] == [encode_point(curve, point) for point in original_variables] and
            record["raw_rows"] == raw_rows and record["rows"] == rows and record["known_constraints"] == K and
            record["known_rank"] == known_rank and record["rank_with_known"] == total_rank and
            record["marginal_new_rank"] == total_rank-known_rank and record["formal_raw_rank"] == rank(raw_rows, r) and
            record["formal_quotient_rank"] == rank(rows, r) and record["normalized_rows"] == normalized and record["unknown_columns"] == unknown,
            "false candidate marginal/formal rank certificate")
    require(record["target_base_alias"] == (target is not None and target in base) and
            record["target_orbit_alias"] == (target is not None and any(lookup[point][0] == lookup[target][0] for point in base)), "false target alias")
    poly._check_cost(record["cost"])


def check_cell(cell, p, coefficients, group_encoded, P_encoded, r, base_encoded, depth, image_encoded, target_encoded, W, arm, multiplier=35):
    """Verify source equations, exact HNF/LLL/norms and all root/lift witnesses."""
    sp, _ = poly.dependencies()
    require(cell["parameters"] == {"p": p, "coefficients": list(coefficients), "d": depth, "image": image_encoded,
            "target": target_encoded, "W": W, "arm": arm, "t": 1, "L": 0}, "changed reduction parameters")
    variables, equations, first, descriptors = build_system(p, coefficients, depth, image_encoded, target_encoded, base_encoded, W, arm)
    require(cell["variables"] == [str(x) for x in variables] and cell["source_equations"] == [poly._pack(expr, variables) for expr in equations], "changed original system")
    curve = Curve(Field(p), *coefficients)
    context = {"curve": curve, "G": [_point(curve, point) for point in group_encoded], "target": _point(curve, target_encoded),
               "allowed_base": [_point(curve, point) for point in base_encoded], "source_equations": equations,
               "coordinate_sources": first, "auxiliary_chains": descriptors}
    boxes = [list(range(-W+1, W)) for _ in variables]
    require(cell["boxes"] == boxes and cell["context"] == poly._context_certificate(context, variables), "changed signed boxes or actual point/chain context")
    require(cell["system_statistics"] == {"variables": len(variables), "original_equations": len(equations),
        "total_degrees": [int(sp.Poly(expr, *variables).total_degree()) for expr in equations],
        "original_support_sizes": [len(poly._pack(expr, variables)) for expr in equations],
        "integer_box_sizes": [len(box) for box in boxes]}, "false source variable/degree/monomial/box statistics")
    lattice = cell["lattice"]
    require(lattice["polynomials"] == cell["source_equations"] and lattice["variables"] == cell["variables"] and lattice["p"] == p and
            lattice["weight_bounds"] == [W]*len(variables) and lattice["t"] == 1 and lattice["L"] == 0 and lattice["arm"] == "dense", "lattice not bound to all source equations/boxes")
    poly.check_lattice(lattice)
    poly.check_reduction(lattice, cell["reduction"])
    certified = [poly._unpack(expr, variables) for expr in cell["reduction"]["certified_equations"]]
    poly.check_extraction(cell["extraction"], certified, variables, boxes, context)
    decompositions = sorted({tuple(tuple(tuple(coord) for coord in point) for point in witness["points"])
                            for record in cell["extraction"]["verification"] for witness in record["witnesses"]})
    encoded = [[[[int(x) for x in coord] for coord in point] for point in row] for row in decompositions]
    require(cell["decompositions"] == encoded, "rank inputs not exactly genuinely extracted decompositions")
    _check_public_rank(cell["candidate_rank"], p, coefficients, group_encoded, base_encoded, target_encoded, encoded, P_encoded, r, multiplier)
    _check_public_rank(cell["homogeneous_rank"], p, coefficients, group_encoded, base_encoded, None, [], P_encoded, r, multiplier)
    expected_status = "bounded_instrument_stop" if cell["reduction"]["status"] == "bounded_instrument_stop" else "measured" if cell["extraction"]["valid_root_count"] else "zero_yield"
    require(cell["status"] == expected_status, "false reduction/extraction status")
    poly._check_cost(cell["setup_cost"])
    require(cell["setup_cost"]["counter"]["operations"].get("system.original_equation") == len(equations), "unpaid original system construction")
    require(cell["work_components"] == ["setup_cost", "lattice.cost", "reduction.cost", "extraction.cost", "candidate_rank.cost", "homogeneous_rank.cost"], "deleted arm cost stage")
    poly._check_rss(cell["inclusive_cost"]["resource"])
    require(cell["inclusive_cost"]["wall_seconds"] >= cell["setup_cost"]["wall_seconds"] and cell["inclusive_cost"]["cpu_seconds"] >= cell["setup_cost"]["cpu_seconds"], "false inclusive arm timing")
    return 1+len(encoded)


def _phase(counter, name, function):
    """Sequential timing/OS lifetime-highwater RSS receipt for one named stage."""
    wall, cpu = time.monotonic(), time.process_time()
    with counter.phase(name):
        value = function()
    return value, _cost(counter, wall, cpu, name)


def _chain_record(p, row):
    coordinates = [None if x is None else _center(x[0], p) for x in row["x"]]
    finite = all(x is not None for x in coordinates)
    return {"source": row.get("source", row.get("source_lift")), "target": row.get("target"),
            "points": row["points"], "centered_x": coordinates, "finite": finite,
            "max_abs_x": max((abs(x) for x in coordinates if x is not None), default=None),
            "pole_indices": [i for i, x in enumerate(coordinates) if x is None]}


def height_cell(p, fiber, W):
    """Complete source/actual-target chain retention, including rejected records.

    This is a paid catalog-derived census. Candidate extraction receives only
    the explicit filtered base, never census roots or relation witnesses.
    A point survives iff at least one complete rational source path fits W.
    """
    require(type(W) is int and W > 0, "positive integer bound required")
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with counter.phase("height_census"):
        source = [_chain_record(p, row) for row in fiber["paths"]]
        membership = [_chain_record(p, row) for row in fiber["membership_paths"]]
        for record in source+membership:
            counter.inc("height.coordinate_inspected", len(record["centered_x"]))
            record["retained"] = record["finite"] and record["max_abs_x"] < W
        retained_labels = {fb._label(row["target"]) for row in membership if row["retained"]}
        original = fiber["bases"]["list"]
        base = [point for point in original if fb._label(point) in retained_labels]
        rejected = [point for point in original if point not in base]
        histogram = lambda rows: [[height, count] for height, count in sorted(Bag(row["max_abs_x"] for row in rows if row["finite"]).items())]
    return {"W": W, "source_chains": source, "target_chains": membership,
            "source_max_height_histogram": histogram(source), "target_max_height_histogram": histogram(membership),
            "M_before": len(original), "M_after": len(base), "base_before": original, "base_after": base,
            "rejected_points": rejected, "point_retention": _fraction(len(base), len(original)),
            "source_chain_retention": _fraction(sum(row["retained"] for row in source), len(source)),
            "target_chain_retention": _fraction(sum(row["retained"] for row in membership), len(membership)),
            "fullfield_baseline": W >= p, "height_label": "whole-field baseline" if W >= p else "actual centered-coordinate window; density measured, no low-height inference",
            "cost": _cost(counter, wall, cpu, "all source/target rational-chain heights and strict retention")}


def _tree_shape(m):
    require(m in (3, 5), "tree only for m3/m5")
    return [(0, 1), (3, 2)] if m == 3 else [(0, 1), (2, 3), (5, 6), (7, 4)]


def _tree_witness(curve, points):
    nodes, values = [], list(points)
    for left, right in _tree_shape(len(points)):
        point = curve.add(values[left], values[right])
        values.append(point)
        nodes.append({"left": left, "right": right, "point": encode_point(curve, point),
                      "branch": "O" if point is None else "affine",
                      "centered_x": None if point is None else _center(point[0][0], curve.field.p)})
    return {"leaves": [encode_point(curve, point) for point in points], "nodes": nodes,
            "sum": encode_point(curve, values[-1])}


def tree_census(p, coefficients, group_encoded, base_encoded, m):
    """Exact all-ordered-tuple tree-node heights via paid subtree convolutions.

    State (sum,max intermediate |x|,has O) avoids an exponential tuple dump.
    Per-node marginal distributions count full ordered tuples, and per-fixed-R
    joint maximum/O distributions retain uniform target conditioning. Separate
    planted cohort is the canonical repeated first-base-point tuple, not an
    unknown target or a sample from the uniform-target denominator.
    """
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    curve = Curve(Field(p, counter=counter), *coefficients)
    group = [_point(curve, point) for point in group_encoded]
    base = [_point(curve, point) for point in base_encoded]
    shape = _tree_shape(m)
    with counter.phase("tree_density_dp_oracle"):
        states = [{(point, -1, False): 1 for point in base} for _ in range(m)]
        leaf_counts = [1]*m
        marginal = []
        for left, right in shape:
            combined, heights = Bag(), Bag()
            leaves = leaf_counts[left]+leaf_counts[right]
            for (a, ha, oa), na in states[left].items():
                for (b, hb, ob), nb in states[right].items():
                    counter.inc("oracle.tree_dp_transition")
                    point = curve.add(a, b)
                    height = -1 if point is None else abs(_center(point[0][0], p))
                    combined[(point, max(ha, hb, height), oa or ob or point is None)] += na*nb
                    heights[None if point is None else _center(point[0][0], p)] += na*nb
            states.append(combined)
            leaf_counts.append(leaves)
            marginal.append({"left": left, "right": right, "subtree_leaves": leaves,
                "full_tuple_height_counts": [[height, count*len(base)**(m-leaves)] for height, count in sorted(heights.items(), key=lambda x: (-p if x[0] is None else x[0]))]})
        targets = []
        for target in group:
            histogram = sorted((height, has_o, count) for (point, height, has_o), count in states[-1].items() if point == target)
            targets.append({"R": encode_point(curve, target), "count": sum(row[2] for row in histogram),
                            "max_abs_intermediate_and_O": [list(row) for row in histogram]})
        planted = _tree_witness(curve, [base[0]]*m) if base else None
    return {"m": m, "M": len(base), "base": base_encoded, "shape": [list(pair) for pair in shape],
            "ordered_tuple_total": len(base)**m, "nodes": marginal, "uniform_targets": targets,
            "planted": {"cohort": "canonical repeated first actual base point; deterministic construction, not uniform", "size": int(bool(base)), "tree": planted},
            "role": "paid oracle; no tree point, target or height distribution passed to candidate extraction",
            "cost": _cost(counter, wall, cpu, "all-tuple tree heights via exact group convolution; planted cohort separately labeled")}


def density_suite(p, coefficients, group_encoded, base_encoded, lengths=(2, 3, 5)):
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with counter.phase("density_input_setup"):
        curve = Curve(Field(p, counter=counter), *coefficients)
        group = [_point(curve, point) for point in group_encoded]
        base = [_point(curve, point) for point in base_encoded]
    setup = _cost(counter, wall, cpu, "fresh density input decoding; DP/tree stages separately paid")
    return {"density": [poly.group_density(curve, group, base, m) for m in lengths],
            "trees": [tree_census(p, coefficients, group_encoded, base_encoded, m) for m in lengths if m in (3, 5)],
            "is_candidate_input": False, "setup_cost": setup}


def build_system(p, coefficients, depth, image_encoded, target_encoded, base_encoded, W, arm, *, counter=None):
    """Actual m2 S3 plus two literal finite chain systems or explicit base lists.

    In chain arm x[leg,0] is the target x (separate target/auxiliary y lifts),
    x_j*x_(j+1)-x_j²-a_j=0 and x_d-Bx=0. Pole branches are separately retained
    in the catalog, and excluded from this finite terminal fiber only after its
    complete certificate. No denominator saturation or oracle root injection.
    No-chain arm uses S3 and product(x_i-u) over exactly the same final base x's.
    """
    sp, _ = poly.dependencies()
    require(arm in ARMS and 0 <= depth <= 3 and W > 0, "wrong system arm/depth/bound")
    curve = Curve(Field(p, counter=counter), *coefficients)
    target = _point(curve, target_encoded)
    require(target is not None, "finite S3 target required; O is separately retained")
    if arm == "chain":
        variables = tuple(sp.Symbol(f"x{leg}_{j}") for leg in range(2) for j in range(depth+1))
        first = [0, depth+1]
    else:
        variables = tuple(sp.Symbol(f"x{leg}_0") for leg in range(2))
        first = [0, 1]
    equations = [poly.s3(variables[first[0]], variables[first[1]], target[0][0], *coefficients)]
    descriptors = []
    if arm == "chain":
        require(image_encoded is not None, "finite auxiliary image required")
        image_x = image_encoded[0][0]
        for leg in range(2):
            indices = list(range(leg*(depth+1), (leg+1)*(depth+1)))
            for j in range(depth):
                x, y = (variables[indices[k]] for k in (j, j+1))
                equations.append(x*y-x*x-pow(-4, j, p))
            equations.append(variables[indices[-1]]-_center(image_x, p))
            descriptors.append({"A": 1, "x_indices": indices, "image_point": image_encoded})
    else:
        xs = sorted({_center(point[0][0], p) for point in base_encoded})
        for i in first:
            equations.append(sp.prod(variables[i]-x for x in xs))
    equations = [poly.centered_polynomial(expr, variables, p) for expr in equations]
    return variables, equations, first, descriptors


def _public_rank(p, coefficients, group_encoded, base_encoded, target_encoded, decompositions, P_encoded, r, multiplier=35):
    """Candidate rows only; certified signed alpha-orbit public knowledge.

    Alpha is used only after a full actual-G action certificate. Software
    fixtures supply multiplier1 explicitly; no action replacement is performed.
    No arbitrary verifier point log enters.
    """
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    curve = Curve(Field(p, counter=counter), *coefficients)
    group = [_point(curve, point) for point in group_encoded]
    base = [_point(curve, point) for point in base_encoded]
    target, P = _point(curve, target_encoded), _point(curve, P_encoded)
    with counter.phase("public_action_and_rank"):
        # Field/Curve class identities can differ between namespace and direct
        # script imports in the two immutable route modules. Keep each module's
        # field objects local; pass JSON-native certificates across interfaces.
        images = [fb._alpha(curve, point, multiplier) for point in group]
        counter.inc("action.membership_attempt", len(group))
        require(all(curve.is_on_curve(point) and point in group for point in images), "no certified scalar action")
        scalars = [k for k in range(1, r) if curve.mul(k, P) == fb._alpha(curve, P, multiplier)]
        require(len(scalars) == 1, "ambiguous scalar action")
        lam = scalars[0]
        require(all(image == curve.mul(lam, point) for point, image in zip(group, images)), "no certified scalar action")
        action = {"preserved": True, "admitted": True, "lambda": lam, "multiplier": curve.field.encode(multiplier),
                  "all_G": [{"point": encode_point(curve, point), "image": encode_point(curve, image)} for point, image in zip(group, images)],
                  "scalar_candidates": scalars, "reason": None}
        known, witnesses = {None: 0}, [{"point": None, "scalar": 0, "sign": 0, "exponent": 0}]
        current, scalar = P, 1
        for exponent in range(r):
            for sign, point in ((1, current), (-1, curve.neg(current))):
                value = sign*scalar % r
                if point in known:
                    require(known[point] == value, "inconsistent public action scalar")
                else:
                    known[point] = value
                    witnesses.append({"point": encode_point(curve, point), "scalar": value, "sign": sign, "exponent": exponent})
            counter.inc("public_action.orbit_step")
            current, scalar = fb._alpha(curve, current, multiplier), scalar*lam % r
            if current == P:
                break
        public = {"generator": P_encoded, "points": witnesses,
                  "policy": "O and signed certified alpha^j(P) only; no verifier log table"}
        # Canonical full signed-action orbits; include target in the same orbit
        # space so aliases are merged even when target is not in actual base.
        variables_points = base+([] if target is None or target in base else [target])
        reps, lookup = [], {}
        for point in variables_points:
            if point in lookup:
                continue
            orbit, current, scalar = {}, point, 1
            for _ in range(2*r):
                for signed, value in ((current, scalar), (curve.neg(current), -scalar % r)):
                    if signed in orbit:
                        require(orbit[signed] == value, "inconsistent signed orbit")
                    orbit[signed] = value
                current, scalar = fb._alpha(curve, current, multiplier), scalar*lam % r
                if current == point:
                    break
            rep = min(orbit, key=fb._key)
            inverse = pow(orbit[rep], -1, r)
            idx = len(reps)
            reps.append(rep)
            for member, value in orbit.items():
                lookup[member] = (idx, value*inverse % r)
        rows, raw_rows, raw_variables = [], [], list(variables_points)
        for encoded in decompositions:
            points = [_point(curve, point) for point in encoded]
            require(len(points) == 2 and all(point in base for point in points) and poly._sum(curve, points) == target, "rank without actual candidate identity")
            row, raw = [0]*len(reps), [0]*len(raw_variables)
            for sign, point in [(1, point) for point in points]+([] if target is None else [(-1, target)]):
                i, value = lookup[point]
                row[i] = (row[i]+sign*value) % r
                raw[raw_variables.index(point)] = (raw[raw_variables.index(point)]+sign) % r
            rows.append(row)
            raw_rows.append(raw)
        K = fb._known_affine_constraints(reps, known, r)
        normalized, unknown = fb._normalized_rows(rows, reps, known, r)
        known_rank = fb._rank(K, r, counter)
        stacked = K+[row+[0] for row in rows]
        total_rank = fb._rank(stacked, r, counter)
        require(total_rank == fb._rank([row[:-1] for row in stacked], r, counter), "inconsistent affine candidate rows")
        marginal = total_rank-known_rank
        require(fb._rank(normalized, r, counter) == marginal, "rank normalization mismatch")
        formal_raw, formal_quotient = fb._rank(raw_rows, r, counter), fb._rank(rows, r, counter)
    return {"target": target_encoded, "base": base_encoded, "P": P_encoded, "action_multiplier": multiplier,
            "action": action, "public_known": public, "variables": [encode_point(curve, point) for point in reps],
            "raw_variables": [encode_point(curve, point) for point in raw_variables], "raw_rows": raw_rows, "rows": rows,
            "known_constraints": K, "known_rank": known_rank, "rank_with_known": total_rank,
            "normalized_rows": normalized, "unknown_columns": unknown, "marginal_new_rank": marginal,
            "formal_raw_rank": formal_raw, "formal_quotient_rank": formal_quotient,
            "target_base_alias": target is not None and target in base,
            "target_orbit_alias": target is not None and any(lookup[point][0] == lookup[target][0] for point in base),
            "scope": "one fixed target; formal ranks diagnostic; signed certified alpha-orbit public constraints only; no target pooling",
            "cost": _cost(counter, wall, cpu, "certified public action, actual candidate rows, affine rank normalization")}


def reduction_cell(p, coefficients, group_encoded, P_encoded, r, base_encoded, depth, image_encoded,
                   target_encoded, W, arm, multiplier=35):
    """Fresh actual HNF/LLL/extraction arm with signed boxes; never a box oracle."""
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with counter.phase("system_and_context_setup"):
        poly._reset_symbolic_cache(counter)
        curve = Curve(Field(p, counter=counter), *coefficients)
        group = [_point(curve, point) for point in group_encoded]
        base = [_point(curve, point) for point in base_encoded]
        target = _point(curve, target_encoded)
        variables, source, first, chains = build_system(p, coefficients, depth, image_encoded, target_encoded, base_encoded, W, arm, counter=counter)
        counter.inc("system.original_equation", len(source))
        context = {"curve": curve, "G": group, "target": target, "allowed_base": base,
                   "source_equations": source, "coordinate_sources": first, "auxiliary_chains": chains}
        boxes = [list(range(-W+1, W)) for _ in variables]
        sp, _ = poly.dependencies()
        statistics = {"variables": len(variables), "original_equations": len(source),
            "total_degrees": [int(sp.Poly(expr, *variables).total_degree()) for expr in source],
            "original_support_sizes": [len(poly._pack(expr, variables)) for expr in source],
            "integer_box_sizes": [len(box) for box in boxes]}
        counter.inc("system.statistics_equation", len(source))
    setup = _cost(counter, wall, cpu, "fresh field/curve/counter/cache; actual source systems and signed boxes")
    lattice = poly.build_shift_lattice(source, variables, p, [W]*len(variables), 1, 0, "dense")
    reduced = poly.reduce_and_certify(lattice)
    sp, _ = poly.dependencies()
    equations = [poly._unpack(expr, variables) for expr in reduced["certified_equations"]]
    extracted = poly.extract_and_verify(equations, variables, boxes, context)
    decompositions = sorted({tuple(tuple(tuple(c) for c in point) for point in witness["points"])
                             for record in extracted["verification"] for witness in record["witnesses"]})
    decompositions = [[[[int(x) for x in coord] for coord in point] for point in points] for points in decompositions]
    candidate_rank = _public_rank(p, coefficients, group_encoded, base_encoded, target_encoded, decompositions, P_encoded, r, multiplier)
    homogeneous_rank = _public_rank(p, coefficients, group_encoded, base_encoded, None, [], P_encoded, r, multiplier)
    status = "bounded_instrument_stop" if reduced["status"] == "bounded_instrument_stop" else ("measured" if extracted["valid_root_count"] else "zero_yield")
    return {"parameters": {"p": p, "coefficients": list(coefficients), "d": depth, "image": image_encoded,
                "target": target_encoded, "W": W, "arm": arm, "t": 1, "L": 0},
            "variables": [str(x) for x in variables], "source_equations": [poly._pack(expr, variables) for expr in source],
            "context": poly._context_certificate(context, variables), "boxes": boxes, "system_statistics": statistics,
            "lattice": lattice, "reduction": reduced, "extraction": extracted,
            "decompositions": decompositions, "candidate_rank": candidate_rank, "homogeneous_rank": homogeneous_rank,
            "status": status, "setup_cost": setup,
            "inclusive_cost": {"wall_seconds": time.monotonic()-wall, "cpu_seconds": time.process_time()-cpu,
                               "resource": poly.rss("inclusive cold arm; components already included")},
            "work_components": ["setup_cost", "lattice.cost", "reduction.cost", "extraction.cost", "candidate_rank.cost", "homogeneous_rank.cost"],
            "oracle_policy": "no density, DP, catalog intermediate root or planted point passed to candidate extraction; explicit allowed base is paid membership setup"}


def positive_dimension_control(p, coefficients, group_encoded, P_encoded):
    sp, _ = poly.dependencies()
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with counter.phase("positive_dimension_source_setup"):
        poly._reset_symbolic_cache(counter)
        u, v = sp.symbols("u v")
        source = [u*v-u*u-1]
        curve = Curve(Field(p, counter=counter), *coefficients)
        context = {"curve": curve, "G": [_point(curve, point) for point in group_encoded],
                   "target": _point(curve, P_encoded), "source_equations": source, "coordinate_sources": [0, 1]}
        original_ideal = poly.ideal_certificate(source, (u, v), counter)
    setup = _cost(counter, wall, cpu, "unanchored chain source, original ideal dimension and fresh point context")
    lattice = poly.build_shift_lattice(source, (u, v), p, (2, 2), 1, 0, "dense")
    reduced = poly.reduce_and_certify(lattice)
    certified = [poly._unpack(expr, (u, v)) for expr in reduced["certified_equations"]]
    extraction = poly.extract_and_verify(certified, (u, v), [list(range(-1, 2))]*2, context)
    return {"source_equations": [poly._pack(expr, (u, v)) for expr in source],
            "original_ideal": original_ideal, "lattice": lattice, "reduction": reduced, "setup_cost": setup,
            "extraction": extraction, "scope": "unanchored finite chain equation has positive dimension; no terminal fiber/S3; no independent equation guarantee"}


def _case(identifier, panel, inputs, observables, certificates, work, status="measured", limits=None):
    require(status in poly.STATUSES, "unknown shared status")
    return {"id": identifier, "panel": panel, "status": status, "inputs": inputs,
            "observables": observables, "certificates": certificates, "work": work, "limits": limits or []}


def _controls(seed, p, coefficients, group_encoded, base_encoded, key, lengths):
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with counter.phase("control_construction"):
        curve = Curve(Field(p, counter=counter), *coefficients)
        nonzero = [point for point in group_encoded if point is not None]
        random_base = random.Random(f"{seed}:{key}:random").sample(nonzero, len(base_encoded))
        permutation = list(range(p))
        random.Random(f"{seed}:{key}:labels").shuffle(permutation)
        xs = {point[0][0] for point in base_encoded}
        relabeled = [point for point in nonzero if permutation[point[0][0]] in xs]
        counter.inc("control.explicit_base_entry", len(nonzero)+len(random_base)+len(relabeled))
        counter.inc("control.coordinate_permutation", p)
    setup = _cost(counter, wall, cpu, "seeded size-matched random base and coordinate permutation construction")
    return {"random_same_size": {"base": random_base, "density": density_suite(p, coefficients, group_encoded, random_base, lengths)},
            "coordinate_relabel": {"base": relabeled, "permutation": permutation,
                                   "density": density_suite(p, coefficients, group_encoded, relabeled, lengths)}, "setup_cost": setup}


def run_experiment(seed=1729):
    """Execute every frozen cell only after external scientific-run admission."""
    wall, cpu = time.monotonic(), time.process_time()
    sp, fpylll = poly.dependencies()
    dependency = {"wall_seconds": time.monotonic()-wall, "cpu_seconds": time.process_time()-cpu,
                  "versions": {"sympy": sp.__version__, "fpylll": fpylll.__version__, "python": sys.version},
                  "integer_serialization": "full precision JSON; decimal conversion guard disabled by dependency gate; arithmetic caps unchanged",
                  "resource": poly.rss("shared actual dependency setup; allocator/modules remain shared")}
    catalog_wall, catalog_cpu = time.monotonic(), time.process_time()
    catalog = fb.auxiliary_catalog()  # rebuild; never consume a prior run artifact
    catalog_receipt = {"wall_seconds": time.monotonic()-catalog_wall, "cpu_seconds": time.process_time()-catalog_cpu,
                       "resource": poly.rss("inclusive actual rebuilt catalog and all its component work")}
    p, coefficients = 97, (0, 2)
    admission = catalog["target"]["admission"]
    group, P, r = admission["G"] or [], admission["P"], admission["r"]
    cases = [_case("catalog", "rebuild", {"p": p, "depths": FIXTURE["depths"]},
                   {"admitted": admission["admitted"]}, {"catalog": catalog}, {"inclusive_cost": catalog_receipt},
                   "measured" if admission["admitted"] else "inadmissible")]
    selections, shared_filters = [], {}
    for entry in catalog["entries"]:
        depth = entry["d"]
        chosen = next((fiber for fiber in entry["finite_fibers"] if entry["complete_kernel"] and fiber["bases"]["list"]), None) if admission["admitted"] else None
        selections.append({"d": depth, "fiber_index": chosen["index"] if chosen else None,
                           "reason": "canonical first admitted nonempty before height filtering" if chosen else "no complete-kernel nonempty actual target base; not replaced"})
        cases.append(_case(f"d{depth}/poles", "kernel_poles", {"d": depth},
                           {"complete_kernel": entry["complete_kernel"], "kernel_size": len(entry["kernel"])},
                           {"paths": [_chain_record(p, row) for row in entry["pole_paths"]]}, entry["work"],
                           "measured" if entry["complete_kernel"] else "inadmissible"))
        for fiber in entry["finite_fibers"]:
            key = f"d{depth}/fiber{fiber['index']}"
            before = density_suite(p, coefficients, group, fiber["bases"]["list"]) if admission["admitted"] else None
            cases.append(_case(key+"/before", "full_fiber_density", {"d": depth, "fiber_index": fiber["index"]},
                {"M": len(fiber["bases"]["list"]), "selected": fiber is chosen}, {"density": before},
                {"membership_setup": fiber["work"], "oracle_costs_in_certificates": True},
                "measured" if before and fiber["bases"]["list"] else "zero_yield" if admission["admitted"] else "inadmissible"))
            for W in FIXTURE["coordinate_bounds"]:
                height = height_cell(p, fiber, W)
                density = density_suite(p, coefficients, group, height["base_after"]) if admission["admitted"] else None
                controls = _controls(seed, p, coefficients, group, height["base_after"], key+f"/W{W}", (2, 3, 5)) if admission["admitted"] else None
                cases.append(_case(key+f"/W{W}", "height_retention", {"d": depth, "fiber_index": fiber["index"], "W": W},
                    {"M_before": height["M_before"], "M_after": height["M_after"], "fullfield_baseline": W == p},
                    {"height": height, "density": density, "controls": controls},
                    {"height_cost": height["cost"], "density_and_control_costs_in_certificates": True},
                    "measured" if height["M_after"] else "zero_yield"))
        if chosen is None:
            cases.append(_case(f"d{depth}/reduction-unavailable", "selection", {"d": depth},
                               {"selected": None}, {}, {}, "inadmissible", [selections[-1]["reason"]]))
            continue
        for W in FIXTURE["coordinate_bounds"]:
            # Pure explicit membership filtering; none of the DP relation tables
            # or centered chain root assignments enters reduction_cell.
            filtered = height_cell(p, chosen, W)
            base = filtered["base_after"]
            filter_id = f"d{depth}/W{W}"
            shared_filters[filter_id] = filtered["cost"]
            for target in group:
                target_index = group.index(target)
                for arm in ARMS:
                    identifier = f"d{depth}/reduction/W{W}/R{target_index}/{arm}"
                    inputs = {"d": depth, "fiber_index": chosen["index"], "W": W, "target": target, "arm": arm}
                    if target is None:
                        rank = _public_rank(p, coefficients, group, base, None, [], P, r)
                        cases.append(_case(identifier, "finite_m2_reduction", inputs, {"finite_target": False},
                                           {"homogeneous_rank": rank}, {"rank_cost": rank["cost"], "filter_receipt_id": filter_id}, "inadmissible",
                                           ["O has no affine x for S3; all O decompositions remain in density, no surrogate finite target"]))
                    else:
                        cell = reduction_cell(p, coefficients, group, P, r, base, depth, chosen["B"], target, W, arm)
                        cases.append(_case(identifier, "finite_m2_reduction", inputs,
                            {"finite_target": True, "valid_roots": cell["extraction"]["valid_root_count"],
                             "marginal_new_rank": cell["candidate_rank"]["marginal_new_rank"]}, {"cell": cell},
                            {"components": cell["work_components"], "inclusive_cost": cell["inclusive_cost"],
                             "filter_receipt_id": filter_id,
                             "filter_reuse": "same rebuilt selection filter reused symmetrically for both arms/all R; charge once actual, add identically in alternative cold totals"}, cell["status"]))
    if admission["admitted"]:
        curve = Curve(Field(p), *coefficients)
        window = [point for point in group if point is not None and abs(_center(point[0][0], p)) < 2]
        control = reduction_cell(p, coefficients, group, P, r, window, 0, None, P, 2, "no_chain_list")
        cases.append(_case("identity_window", "identity_no_chain", {"W": 2, "target": P},
                           {"actual_lll_calls": control["reduction"]["cost"]["counter"]["operations"].get("lll.fpylll_call", 0)},
                           {"cell": control}, {"components": control["work_components"], "inclusive_cost": control["inclusive_cost"]}, control["status"]))
        positive = positive_dimension_control(p, coefficients, group, P)
        cases.append(_case("positive_dimension_chain", "positive_dimension_chain", {"p": p, "W": 2},
                           {"original_dimension": positive["original_ideal"]["dimension"]}, positive,
                           {"components": ["setup_cost", "lattice.cost", "reduction.cost", "extraction.cost"]}, "zero_yield"))
    else:
        for control in ("identity_window", "positive_dimension_chain"):
            cases.append(_case(control, control, {}, {}, {}, {}, "inadmissible", ["target subgroup not admitted; minimum real-LLL stage unavailable"]))
    result = {"schema_version": SCHEMA, "direction": "combined", "seed": seed, "parameters": dict(FIXTURE),
              "selections": selections, "cases": cases, "checks": {"producer_check": "pending"},
              "limitations": ["Exact toy instrumentation only; no scientific conclusion or speedup claim.",
                  "Low map degree supplies no small-coordinate guarantee; actual fullfield/window density is measured.",
                  "Certified strict norm equations still require zero-dimensional extraction and original rational chain/sign/subgroup checks.",
                  "Public-known affine rank is per fixed target; density/planted tables are diagnostic oracles, not candidate inputs."],
              "work_accounting": {"dependency_setup": dependency, "rebuilt_catalog": catalog_receipt,
                  "shared_selected_filter_receipts": shared_filters,
                  "cold_policy": "actual shared catalog/setup charged once, identically added to every hypothetical cold arm; reused density oracle never a free candidate solve",
                  "online_policy": "fresh candidate Field/Curve/counter and cleared Sympy caches per arm; modules/allocator shared and dependency cost explicit",
                  "descent": "not implemented; no recovered discrete logarithm or end-to-end attack cost claimed",
                  "unpriced_work": list(UNPRICED)}, "instrument_scope": "prospective exact finite fixture, bounded n64/D256/4096bit; no scientific promotion"}
    verify_wall, verify_cpu = time.monotonic(), time.process_time()
    checked = check_result(result)
    result["checks"] = {"producer_check": "passed", "certificate_items": checked["certificate_items"], "independent_scientific_review": False}
    result["work_accounting"]["verification"] = {"wall_seconds": time.monotonic()-verify_wall, "cpu_seconds": time.process_time()-verify_cpu,
                                                "resource": poly.rss("actual checker; excluded from candidate primitive counts")}
    return result


def _check_controls(controls, seed, p, coefficients, group_encoded, base_encoded, key):
    require(set(controls) == {"random_same_size", "coordinate_relabel", "setup_cost"}, "deleted random/relabel control")
    nonzero = [point for point in group_encoded if point is not None]
    random_base = random.Random(f"{seed}:{key}:random").sample(nonzero, len(base_encoded))
    permutation = list(range(p))
    random.Random(f"{seed}:{key}:labels").shuffle(permutation)
    xs = {point[0][0] for point in base_encoded}
    relabeled = [point for point in nonzero if permutation[point[0][0]] in xs]
    require(controls["random_same_size"]["base"] == random_base and len(random_base) == len(base_encoded), "random base changed size/seed")
    require(controls["coordinate_relabel"]["base"] == relabeled and controls["coordinate_relabel"]["permutation"] == permutation, "changed coordinate relabel control")
    checked = _check_suite(controls["random_same_size"]["density"], p, coefficients, group_encoded, random_base)
    checked += _check_suite(controls["coordinate_relabel"]["density"], p, coefficients, group_encoded, relabeled)
    poly._check_cost(controls["setup_cost"])
    require(controls["setup_cost"]["counter"]["operations"].get("control.coordinate_permutation") == p and
            controls["setup_cost"]["counter"]["operations"].get("control.explicit_base_entry") == len(nonzero)+len(random_base)+len(relabeled), "unpaid control construction")
    return checked


def _check_positive(control, p, coefficients, group_encoded, P_encoded):
    sp, _ = poly.dependencies()
    u, v = sp.symbols("u v")
    source = [u*v-u*u-1]
    require(control["source_equations"] == [poly._pack(expr, (u, v)) for expr in source] and
            control["original_ideal"] == poly.ideal_certificate(source, (u, v)) and
            control["original_ideal"]["dimension"] == 1, "false positive-dimensional chain control")
    lattice = control["lattice"]
    require(lattice["polynomials"] == control["source_equations"] and lattice["variables"] == ["u", "v"] and
            lattice["p"] == p and lattice["weight_bounds"] == [2, 2] and lattice["t"] == 1 and lattice["L"] == 0 and lattice["arm"] == "dense", "wrong positive-dimension lattice source")
    poly.check_lattice(lattice)
    poly.check_reduction(lattice, control["reduction"])
    curve = Curve(Field(p), *coefficients)
    context = {"curve": curve, "G": [_point(curve, point) for point in group_encoded], "target": _point(curve, P_encoded),
               "source_equations": source, "coordinate_sources": [0, 1]}
    certified = [poly._unpack(expr, (u, v)) for expr in control["reduction"]["certified_equations"]]
    poly.check_extraction(control["extraction"], certified, (u, v), [list(range(-1, 2))]*2, context)
    require(control["extraction"]["valid_root_count"] == 0, "positive-dimensional chain falsely scored as finite extraction success")
    poly._check_cost(control["setup_cost"])
    require(control["setup_cost"]["counter"]["operations"].get("groebner.call") == 1, "unpaid original chain dimension check")


def check_result(result):
    """Exact frozen coverage and independent field/point/lattice certificates.

    Refuses changed source parameters before touching study arithmetic. This
    checker is a producer integrity check, not independent scientific review.
    It does not invoke a lattice reducer or pass oracle roots to extraction.
    """
    required = {"schema_version", "direction", "seed", "parameters", "cases", "checks", "limitations", "work_accounting", "instrument_scope", "selections"}
    require(isinstance(result, dict) and required <= set(result), "missing combined result fields")
    require(result["schema_version"] == SCHEMA and result["direction"] == "combined", "wrong schema/direction")
    require(result["parameters"] == FIXTURE, "changed frozen combined parameters")
    cases = result["cases"]
    require(isinstance(cases, list) and cases and cases[0]["id"] == "catalog", "missing rebuilt catalog")
    for case in cases:
        require({"id", "panel", "status", "inputs", "observables", "certificates", "work", "limits"} <= set(case) and
                case["status"] in poly.STATUSES, "incomplete case/shared status")
    require(len({case["id"] for case in cases}) == len(cases), "duplicate case id")
    by_id = {case["id"]: case for case in cases}
    catalog = cases[0]["certificates"]["catalog"]
    require(catalog["p"] == 97 and catalog["depths"] == [0, 1, 2, 3] and
            catalog["target"]["p"] == 97 and catalog["target"]["A"] == 0 and catalog["target"]["B"] == 2, "changed rebuilt catalog fixture")
    checked = fb.check_catalog(catalog)
    admission = catalog["target"]["admission"]
    group, P, r = admission["G"] or [], admission["P"], admission["r"]
    require(cases[0]["inputs"] == {"p": 97, "depths": [0, 1, 2, 3]} and cases[0]["observables"] == {"admitted": admission["admitted"]} and
            cases[0]["status"] == ("measured" if admission["admitted"] else "inadmissible"), "false catalog admission")
    expected_ids, selections, expected_filter_ids = ["catalog"], [], []
    for entry in catalog["entries"]:
        depth = entry["d"]
        chosen = next((fiber for fiber in entry["finite_fibers"] if entry["complete_kernel"] and fiber["bases"]["list"]), None) if admission["admitted"] else None
        selections.append({"d": depth, "fiber_index": chosen["index"] if chosen else None,
                           "reason": "canonical first admitted nonempty before height filtering" if chosen else "no complete-kernel nonempty actual target base; not replaced"})
        identifier = f"d{depth}/poles"
        expected_ids.append(identifier)
        require(identifier in by_id, "deleted pole control")
        pole = by_id[identifier]
        expected_poles = []
        for row in entry["pole_paths"]:
            values = [None if point is None else _center(point[0][0], 97) for point in row["points"]]
            expected_poles.append({"source": row["source"], "target": None, "points": row["points"], "centered_x": values,
                "finite": None not in values, "max_abs_x": max((abs(value) for value in values if value is not None), default=None),
                "pole_indices": [i for i, value in enumerate(values) if value is None]})
        require(pole["panel"] == "kernel_poles" and pole["inputs"] == {"d": depth} and
                pole["certificates"] == {"paths": expected_poles} and
                pole["observables"] == {"complete_kernel": entry["complete_kernel"], "kernel_size": len(entry["kernel"])} and
                pole["status"] == ("measured" if entry["complete_kernel"] else "inadmissible"), "lost/incorrect projective pole branch")
        for fiber in entry["finite_fibers"]:
            key = f"d{depth}/fiber{fiber['index']}"
            identifier = key+"/before"
            expected_ids.append(identifier)
            require(identifier in by_id, "deleted full fiber")
            case = by_id[identifier]
            require(case["panel"] == "full_fiber_density" and case["inputs"] == {"d": depth, "fiber_index": fiber["index"]} and
                    case["observables"] == {"M": len(fiber["bases"]["list"]), "selected": fiber is chosen}, "wrong full-fiber density label")
            status = "measured" if admission["admitted"] and fiber["bases"]["list"] else "zero_yield" if admission["admitted"] else "inadmissible"
            require(case["status"] == status, "false full-fiber density status")
            if admission["admitted"]:
                checked += _check_suite(case["certificates"]["density"], 97, (0, 2), group, fiber["bases"]["list"])
            else:
                require(case["certificates"]["density"] is None, "oracle on unadmitted subgroup")
            for W in FIXTURE["coordinate_bounds"]:
                identifier = key+f"/W{W}"
                expected_ids.append(identifier)
                require(identifier in by_id, "deleted window/fiber adverse cell")
                case = by_id[identifier]
                height = case["certificates"]["height"]
                base = _check_height(height, 97, fiber, W)
                require(case["panel"] == "height_retention" and case["inputs"] == {"d": depth, "fiber_index": fiber["index"], "W": W} and
                        case["observables"] == {"M_before": len(fiber["bases"]["list"]), "M_after": len(base), "fullfield_baseline": W == 97} and
                        case["status"] == ("measured" if base else "zero_yield"), "false height case parameters/status")
                if admission["admitted"]:
                    checked += _check_suite(case["certificates"]["density"], 97, (0, 2), group, base)
                    checked += _check_controls(case["certificates"]["controls"], result["seed"], 97, (0, 2), group, base, key+f"/W{W}")
                else:
                    require(case["certificates"]["density"] is None and case["certificates"]["controls"] is None, "unadmitted density/control")
        if chosen is None:
            identifier = f"d{depth}/reduction-unavailable"
            expected_ids.append(identifier)
            require(identifier in by_id and by_id[identifier]["status"] == "inadmissible" and by_id[identifier]["certificates"] == {}, "missing unselected-depth admission failure")
            continue
        for W in FIXTURE["coordinate_bounds"]:
            source_case = by_id[f"d{depth}/fiber{chosen['index']}/W{W}"]
            base = source_case["certificates"]["height"]["base_after"]
            filter_id = f"d{depth}/W{W}"
            expected_filter_ids.append(filter_id)
            require(filter_id in result["work_accounting"]["shared_selected_filter_receipts"], "missing paid selected-filter setup")
            filter_cost = result["work_accounting"]["shared_selected_filter_receipts"][filter_id]
            poly._check_cost(filter_cost)
            require(filter_cost["counter"]["operations"] == source_case["certificates"]["height"]["cost"]["counter"]["operations"], "unpaid repeated selected-base filtering")
            for j, target in enumerate(group):
                for arm in ARMS:
                    identifier = f"d{depth}/reduction/W{W}/R{j}/{arm}"
                    expected_ids.append(identifier)
                    require(identifier in by_id, "deleted selected-fiber matched reduction")
                    case = by_id[identifier]
                    require(case["panel"] == "finite_m2_reduction" and case["inputs"] ==
                            {"d": depth, "fiber_index": chosen["index"], "W": W, "target": target, "arm": arm}, "changed selected-fiber/target schedule")
                    require(case["work"]["filter_receipt_id"] == filter_id, "wrong shared filter cost reference")
                    if target is None:
                        require(case["status"] == "inadmissible" and case["observables"] == {"finite_target": False}, "O silently given finite S3 coordinates")
                        _check_public_rank(case["certificates"]["homogeneous_rank"], 97, (0, 2), group, base, None, [], P, r, 35)
                    else:
                        cell = case["certificates"]["cell"]
                        checked += check_cell(cell, 97, (0, 2), group, P, r, base, depth, chosen["B"], target, W, arm)
                        require(case["status"] == cell["status"] and case["observables"] ==
                                {"finite_target": True, "valid_roots": cell["extraction"]["valid_root_count"], "marginal_new_rank": cell["candidate_rank"]["marginal_new_rank"]}, "false valid-root/rank status")
                        require(case["work"]["components"] == cell["work_components"] and case["work"]["inclusive_cost"] == cell["inclusive_cost"] and case["work"]["filter_reuse"], "missing matched arm work")
    require(result["selections"] == selections, "adaptive selected fiber")
    expected_ids += ["identity_window", "positive_dimension_chain"]
    require([case["id"] for case in cases] == expected_ids, "deleted/reordered/extra panel/control")
    if admission["admitted"]:
        identity = by_id["identity_window"]
        window = [point for point in group if point is not None and abs(_center(point[0][0], 97)) < 2]
        checked += check_cell(identity["certificates"]["cell"], 97, (0, 2), group, P, r, window, 0, None, P, 2, "no_chain_list")
        calls = identity["certificates"]["cell"]["reduction"]["cost"]["counter"]["operations"].get("lll.fpylll_call", 0)
        require(calls == 1 and identity["observables"] == {"actual_lll_calls": 1} and identity["status"] == identity["certificates"]["cell"]["status"], "mandatory actual identity/no-chain LLL missing")
        positive = by_id["positive_dimension_chain"]
        _check_positive(positive["certificates"], 97, (0, 2), group, P)
        require(positive["status"] == "zero_yield" and positive["observables"] == {"original_dimension": 1}, "positive-dimension control falsely promoted")
    else:
        require(all(by_id[key]["status"] == "inadmissible" for key in ("identity_window", "positive_dimension_chain")), "minimum stage false admission")
    work = result["work_accounting"]
    require(set(work["shared_selected_filter_receipts"]) == set(expected_filter_ids), "deleted/extra shared selected-filter costs")
    require(work["unpriced_work"] and work["cold_policy"] and work["online_policy"] and work["descent"], "missing full cost scope/limitations")
    require(work["dependency_setup"]["versions"]["sympy"] == "1.14.0" and work["dependency_setup"]["versions"]["fpylll"] == "0.6.4", "dependency receipt mismatch")
    for key in ("dependency_setup", "rebuilt_catalog"):
        require(work[key]["wall_seconds"] >= 0 and work[key]["cpu_seconds"] >= 0, "invented setup timings")
        poly._check_rss(work[key]["resource"])
    return {"certificate_items": checked, "scientific_validation": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    if args.check is not None:
        if args.output_dir is not None:
            parser.error("--check and --output-dir are exclusive")
        poly.dependencies()  # full-precision JSON parse, exact required versions
        print(json.dumps(check_result(json.loads(args.check.read_text())), sort_keys=True))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir required for execution")
    started = datetime.now(timezone.utc).isoformat()
    wall, cpu = time.monotonic(), time.process_time()
    result = run_experiment(args.seed)
    write_artifacts(result, args.output_dir, args.seed, started, wall, cpu)
    print(json.dumps({"direction": "combined", "cases": len(result["cases"]), "checks": result["checks"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
