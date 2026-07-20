#!/usr/bin/env python3
"""Independent development verifier for EXP-SGCP-EMBED-002.

This verifier does not import or execute the producer. It reconstructs the EC
objects, predicate selection, collision graph, retained embedding, and primary
coverage optimum from the emitted coordinates.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


EXPECTED_SCHEMA = "sgcp-embed-002-development-v1"
VERIFICATION_SCHEMA = "sgcp-embed-002-development-verification-v1"
SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parents[1]
DEVELOPMENT_ROOT = EXPERIMENT_ROOT / "development"
Point = tuple[int, int] | None
Formal = tuple[int, ...]


def stable_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(stable_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            state.update(block)
    return state.hexdigest()


def strict_load(path: Path) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate key {key!r} in {path}")
            result[key] = value
        return result

    def constant(value: str) -> Any:
        raise ValueError(f"non-finite constant {value!r} in {path}")

    return json.loads(
        path.read_text(encoding="ascii"),
        object_pairs_hook=pairs,
        parse_constant=constant,
    )


def is_prime(value: int) -> bool:
    if type(value) is not int or value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def point_order(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def decode_point(value: Any) -> Point:
    if value == "O":
        return None
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(type(coordinate) is not int for coordinate in value)
    ):
        raise ValueError(f"invalid point encoding {value!r}")
    return value[0], value[1]


def label(point: Point) -> str:
    return "O" if point is None else f"{point[0]}:{point[1]}"


def bits(mask: int) -> Iterator[int]:
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


class Curve:
    def __init__(self, p: int, a: int, b: int) -> None:
        if not is_prime(p) or p <= 3:
            raise ValueError("invalid prime field")
        self.p = p
        self.a = a % p
        self.b = b % p
        if self.discriminant() == 0:
            raise ValueError("singular curve")

    def discriminant(self) -> int:
        return (4 * pow(self.a, 3, self.p) + 27 * pow(self.b, 2, self.p)) % self.p

    def j(self) -> int:
        return (
            1728
            * 4
            * pow(self.a, 3, self.p)
            * pow(self.discriminant(), -1, self.p)
            % self.p
        )

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def negate(self, point: Point) -> Point:
        return None if point is None else (point[0], -point[1] % self.p)

    def plus(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = 2 * y1 % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        result = (x3, (slope * (x1 - x3) - y1) % self.p)
        if not self.contains(result):
            raise AssertionError("independent addition left curve")
        return result

    def points(self) -> list[Point]:
        roots: dict[int, list[int]] = defaultdict(list)
        for y in range(self.p):
            roots[y * y % self.p].append(y)
        result: list[Point] = [None]
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            result.extend((x, y) for y in roots.get(rhs, []))
        return sorted(result, key=point_order)


def polynomial(roots: Sequence[int], p: int) -> list[int]:
    result = [1]
    for root in roots:
        next_result = [0] * (len(result) + 1)
        for degree, coefficient in enumerate(result):
            next_result[degree] = (next_result[degree] - coefficient * root) % p
            next_result[degree + 1] = (next_result[degree + 1] + coefficient) % p
        result = next_result
    return result


def admissible(curve: Curve, group: Sequence[Point]) -> dict[int, tuple[Point, Point]]:
    fibers: dict[int, list[Point]] = defaultdict(list)
    for point in group:
        if point is not None:
            fibers[point[0]].append(point)
    result: dict[int, tuple[Point, Point]] = {}
    for x, values in fibers.items():
        ordered = tuple(sorted(values, key=point_order))
        if len(ordered) == 2 and curve.negate(ordered[0]) == ordered[1]:
            result[x] = (ordered[0], ordered[1])
    return result


def map_ranking(roots: Sequence[int], p: int, params: dict[str, Any]) -> tuple[list[int], list[int]]:
    u = params["u"]
    v = params["v"]
    w = params["w"]
    if any(type(value) is not int for value in (u, v, w, params["determinant"], params["nonce"])):
        raise ValueError("noninteger Mobius parameter")
    if (u * w - v) % p == 0 or params["determinant"] != (u * w - v) % p:
        raise ValueError("degenerate or inconsistent Mobius map")
    scored: list[tuple[int, int]] = []
    poles: list[int] = []
    for x in roots:
        denominator = (x + w) % p
        if denominator == 0:
            poles.append(x)
        else:
            scored.append(((u * x + v) * pow(denominator, -1, p) % p, x))
    return [x for _, x in sorted(scored)], sorted(poles)


def verify_factor_base(curve: Curve, group: Sequence[Point], row: dict[str, Any]) -> list[Point]:
    record = row["public_model"]["factor_base"]
    digest_payload = dict(record)
    supplied_selection_digest = digest_payload.pop("selection_sha256", None)
    if supplied_selection_digest != digest(digest_payload):
        raise AssertionError("factor-base selection digest mismatch")
    B = row["B"]
    family = row["family"]
    fibers = admissible(curve, group)
    roots = sorted(fibers)
    required = B // 2
    if family == "least_x_interval":
        expected = roots[:required]
        poles: list[int] = []
    elif family == "mobius_interval":
        ranking, poles = map_ranking(roots, curve.p, record["parameters"]["map"])
        expected = ranking[:required]
    elif family == "two_mobius_union":
        rankings: list[list[int]] = []
        pole_set: set[int] = set()
        for params in record["parameters"]["maps"]:
            ranking, map_poles = map_ranking(roots, curve.p, params)
            rankings.append(ranking)
            pole_set.update(map_poles)
        expected = []
        positions = [0, 0]
        while len(expected) < required:
            changed = False
            for index in range(2):
                while positions[index] < len(rankings[index]):
                    candidate = rankings[index][positions[index]]
                    positions[index] += 1
                    if candidate not in expected:
                        expected.append(candidate)
                        changed = True
                        break
                if len(expected) == required:
                    break
            if not changed:
                raise AssertionError("independent two-map selection stalled")
        if positions != record["parameters"]["alternating_positions"]:
            raise AssertionError("two-map positions mismatch")
        poles = sorted(pole_set)
    elif family == "hash_x_null":
        replicate = row["null_replicate"]
        curve_info = row["curve"]
        token = [curve_info[key] for key in ("p", "a", "b", "q", "seed")]
        ranked = []
        for x in roots:
            value = hashlib.sha256(
                stable_bytes(
                    {
                        "domain": "sgcp-002-hash-x-null",
                        "curve": token,
                        "B": B,
                        "replicate": replicate,
                        "x": x,
                    }
                )
            ).hexdigest()
            ranked.append((value, x))
        expected = [x for _, x in sorted(ranked)[:required]]
        poles = []
    else:
        raise ValueError(f"unknown family {family!r}")
    if sorted(expected) != record["selected_roots"]:
        raise AssertionError("predicate selected-root mismatch")
    if poles != record["excluded_poles"]:
        raise AssertionError("predicate pole audit mismatch")
    if polynomial(sorted(expected), curve.p) != record["root_polynomial_coefficients_ascending_mod_p"]:
        raise AssertionError("root polynomial mismatch")
    factors = sorted(
        (point for root in expected for point in fibers[root]), key=point_order
    )
    if ["O" if point is None else [point[0], point[1]] for point in factors] != record["points"]:
        raise AssertionError("factor point list mismatch")
    if len(factors) != B or any(curve.negate(point) not in factors for point in factors):
        raise AssertionError("factor-base cardinality or sign mismatch")
    return factors


def subsets(formal: Formal) -> set[Formal]:
    result: set[Formal] = {()}
    for degree in range(1, len(formal) + 1):
        result.update(itertools.combinations(formal, degree))
    return result


def ideal(B: int, maxima: Iterable[Formal]) -> set[Formal]:
    result: set[Formal] = {(), *((index,) for index in range(B))}
    for maximum in maxima:
        result.update(subsets(tuple(sorted(maximum))))
    return result


def evaluate(curve: Curve, factors: Sequence[Point], formal: Formal) -> Point:
    result: Point = None
    for index in formal:
        result = curve.plus(result, factors[index])
    return result


def injective_map(
    curve: Curve, factors: Sequence[Point], family: Iterable[Formal]
) -> tuple[dict[Point, Formal], bool]:
    by_point: dict[Point, Formal] = {}
    for formal in sorted(set(family), key=lambda value: (len(value), value)):
        point = evaluate(curve, factors, formal)
        if point in by_point and by_point[point] != formal:
            return by_point, False
        by_point[point] = formal
    return by_point, True


def reconstruct_graph(
    curve: Curve, factors: Sequence[Point]
) -> tuple[list[dict[str, Any]], list[int], int, int, list[Point]]:
    degree2: dict[Point, list[Formal]] = defaultdict(list)
    for formal in itertools.combinations_with_replacement(range(len(factors)), 2):
        degree2[evaluate(curve, factors, formal)].append(formal)
    canonical2 = [
        (point, min(degree2[point]))
        for point in sorted(degree2, key=point_order)
        if point is not None
    ]
    by_formal: dict[Formal, list[tuple[Point, tuple[Formal, Formal]]]] = defaultdict(list)
    raw_a4: set[Point] = set()
    for left_index, right_index in itertools.combinations_with_replacement(
        range(len(canonical2)), 2
    ):
        left_point, left_formal = canonical2[left_index]
        right_point, right_formal = canonical2[right_index]
        formal = tuple(sorted(left_formal + right_formal))
        point = curve.plus(left_point, right_point)
        by_formal[formal].append((point, tuple(sorted((left_formal, right_formal)))))
        raw_a4.add(point)
    candidates: list[dict[str, Any]] = []
    for formal in sorted(by_formal):
        points = {entry[0] for entry in by_formal[formal]}
        if len(points) != 1:
            raise AssertionError("inconsistent formal evaluation")
        candidates.append({"formal": formal, "point": next(iter(points))})
    eligible: list[dict[str, Any]] = []
    maps: list[dict[Point, Formal]] = []
    for candidate in candidates:
        mapping, valid = injective_map(curve, factors, ideal(len(factors), [candidate["formal"]]))
        if valid:
            eligible.append(candidate)
            maps.append(mapping)
    conflicts = [0] * len(eligible)
    edge_count = 0
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            collision = any(
                maps[left][point] != maps[right][point]
                for point in set(maps[left]).intersection(maps[right])
            )
            if collision:
                conflicts[left] |= 1 << right
                conflicts[right] |= 1 << left
                edge_count += 1
    return eligible, conflicts, len(candidates), edge_count, sorted(raw_a4, key=point_order)


def support_counter(curve: Curve, values: Sequence[Point]) -> Counter[Point]:
    ordered = sorted(set(values), key=point_order)
    result: Counter[Point] = Counter()
    for left_index, left in enumerate(ordered):
        for right in ordered[left_index:]:
            result[curve.plus(left, right)] += 1
    return result


def expansion_metrics(curve: Curve, factors: Sequence[Point]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for degree in (1, 2, 4, 8):
        multiplicities: Counter[Point] = Counter()
        for formal in itertools.combinations_with_replacement(range(len(factors)), degree):
            multiplicities[evaluate(curve, factors, formal)] += 1
        histogram = Counter(multiplicities.values())
        result[str(degree)] = {
            "formal_witness_count": sum(multiplicities.values()),
            "support": len(multiplicities),
            "ordered_additive_energy": sum(value * value for value in multiplicities.values()),
            "maximum_multiplicity": max(multiplicities.values(), default=0),
            "multiplicity_histogram": {str(key): histogram[key] for key in sorted(histogram)},
        }
    return result


def clique_cover(mask: int, conflicts: Sequence[int]) -> int:
    groups: list[int] = []
    order = sorted(bits(mask), key=lambda vertex: (-(conflicts[vertex] & mask).bit_count(), vertex))
    for vertex in order:
        for index, group in enumerate(groups):
            if conflicts[vertex] & group == group:
                groups[index] |= 1 << vertex
                break
        else:
            groups.append(1 << vertex)
    return len(groups)


def independent_primary_optimum(
    curve: Curve,
    candidates: Sequence[dict[str, Any]],
    conflicts: Sequence[int],
    incumbent_mask: int,
    maximum_nodes: int = 5000000,
) -> tuple[int, int, bool]:
    points = [candidate["point"] for candidate in candidates]
    group = curve.points()
    point_index = {point: index for index, point in enumerate(group)}
    outputs = [
        [point_index[curve.plus(left, right)] for right in points]
        for left in points
    ]

    def selected_support(mask: int) -> int:
        selected = list(bits(mask))
        result = 0
        for position, left in enumerate(selected):
            for right in selected[position:]:
                result |= 1 << outputs[left][right]
        return result

    best = selected_support(incumbent_mask).bit_count()
    all_mask = (1 << len(candidates)) - 1
    stack: list[tuple[int, int]] = [(0, all_mask)]
    explored = 0
    while stack and explored < maximum_nodes:
        chosen, available = stack.pop()
        explored += 1
        active = chosen | available
        possible_outputs = 0
        active_vertices = list(bits(active))
        for position, left in enumerate(active_vertices):
            for right in active_vertices[position:]:
                possible_outputs |= 1 << outputs[left][right]
        chosen_support = selected_support(chosen)
        alpha = clique_cover(available, conflicts)
        selected_count = chosen.bit_count()
        pair_capacity = selected_count * alpha + alpha * (alpha + 1) // 2
        upper = min(
            possible_outputs.bit_count(),
            chosen_support.bit_count() + pair_capacity,
            len(group),
        )
        if upper <= best:
            continue
        if available == 0:
            best = max(best, chosen_support.bit_count())
            continue
        vertex = max(
            bits(available),
            key=lambda item: ((conflicts[item] & available).bit_count(), -item),
        )
        without = available & ~(1 << vertex)
        stack.append((chosen, without))
        stack.append(
            (
                chosen | (1 << vertex),
                without & ~conflicts[vertex],
            )
        )
    return best, explored, not stack


def retained_model(
    curve: Curve, factors: Sequence[Point], maxima: Sequence[Formal]
) -> tuple[int, int, int, dict[str, bool], list[dict[str, str]]]:
    family = ideal(len(factors), maxima)
    mapping, injective = injective_map(curve, factors, family)
    inverse = {formal: point for point, formal in mapping.items()}
    nonempty = sorted((formal for formal in family if formal), key=lambda value: (len(value), value))
    edges: list[tuple[Formal, Formal, Formal]] = []
    compatible = True
    for left_index, left in enumerate(nonempty):
        for right in nonempty[left_index:]:
            union = tuple(sorted(left + right))
            if union not in family:
                continue
            edges.append((left, right, union))
            if curve.plus(inverse[left], inverse[right]) != inverse[union]:
                compatible = False
    constrained: set[Point] = {None}
    for left, right, output in edges:
        constrained.update((inverse[left], inverse[right], inverse[output]))
    axioms = {
        "identity": True,
        "commutativity": True,
        "associativity": all(subsets(formal).issubset(family) for formal in family),
        "compatibility_coordinates": compatible,
        "injective_evaluation": injective,
        "unique_prime_multiset_factorization": injective,
        "acyclic_by_formal_degree": all(
            len(output) > max(len(left), len(right)) for left, right, output in edges
        ),
        "source_recovery": all(tuple(sorted(formal)) == formal for formal in family),
        "direct_final_edge_excluded": not any(
            len(left) == 4 and len(right) == 4 for left, right, _ in edges
        ),
    }
    public_edges = [
        {
            "left": label(inverse[left]),
            "right": label(inverse[right]),
            "output": label(inverse[output]),
        }
        for left, right, output in edges
    ]
    return len(constrained), len(edges), len(family), axioms, public_edges


def verify_row(row: dict[str, Any], maximum_nodes: int) -> dict[str, Any]:
    errors: list[str] = []
    supplied_digest = row.get("row_sha256")
    payload = dict(row)
    payload.pop("row_sha256", None)
    if supplied_digest != digest(payload):
        errors.append("row digest mismatch")
    info = row["curve"]
    curve = Curve(info["p"], info["a"], info["b"])
    group = curve.points()
    q = len(group)
    expected_curve = {
        "q": q,
        "trace": curve.p + 1 - q,
        "j": curve.j(),
        "generator": "O" if group[1] is None else [group[1][0], group[1][1]],
    }
    for key, value in expected_curve.items():
        if info.get(key) != value:
            errors.append(f"curve {key} mismatch")
    if not is_prime(q) or q.bit_length() != info["bits"]:
        errors.append("curve group-order acceptance mismatch")
    if info["trace"] in (0, 1) or info["j"] in (0, 1728 % curve.p):
        errors.append("curve special-case rejection mismatch")
    try:
        factors = verify_factor_base(curve, group, row)
    except Exception as error:
        errors.append(f"factor base: {error}")
        factors = []
    if not factors:
        return {"valid": False, "errors": errors, "primary_nodes": 0}

    eligible, conflicts, candidate_count, conflict_count, raw_a4 = reconstruct_graph(curve, factors)
    graph = row["private_audit"]["graph"]
    observed_graph = (
        graph["candidate_count"],
        graph["eligible_candidate_count"],
        graph["conflict_count"],
    )
    expected_graph = (candidate_count, len(eligible), conflict_count)
    if observed_graph != expected_graph:
        errors.append(f"graph count mismatch: {observed_graph!r} != {expected_graph!r}")

    by_formal = {candidate["formal"]: index for index, candidate in enumerate(eligible)}
    selected_formals = [tuple(value) for value in row["public_model"]["selected_maxima"]]
    try:
        selected_indices = [by_formal[formal] for formal in selected_formals]
    except KeyError as error:
        errors.append(f"selected maximum is not independently eligible: {error}")
        selected_indices = []
    selected_mask = sum(1 << index for index in selected_indices)
    if any(conflicts[index] & selected_mask for index in selected_indices):
        errors.append("selected maxima are not graph independent")
    selected_points = [eligible[index]["point"] for index in selected_indices]
    retained = support_counter(curve, selected_points)
    raw = support_counter(curve, raw_a4)
    retention = row["private_audit"]["retention"]
    if (len(raw), len(retained)) != (
        retention["raw_final_support"],
        retention["retained_final_support"],
    ):
        errors.append("retention support mismatch")
    if (
        max(raw.values(), default=0),
        max(retained.values(), default=0),
    ) != (
        retention["raw_maximum_multiplicity"],
        retention["retained_maximum_multiplicity"],
    ):
        errors.append("retention multiplicity mismatch")
    if expansion_metrics(curve, factors) != row["private_audit"]["expansion"]:
        errors.append("additive expansion mismatch")

    constrained, edge_count, family_count, axioms, public_edges = retained_model(
        curve, factors, selected_formals
    )
    public = row["public_model"]
    if (constrained, edge_count, family_count) != (
        public["constrained_count"],
        public["public_edge_count"],
        public["formal_family_count"],
    ):
        errors.append("retained model count mismatch")
    for key, value in axioms.items():
        if public["axioms"].get(key) != value:
            errors.append(f"axiom mismatch: {key}")
    if public_edges != public["public_edges"]:
        errors.append("public edge table mismatch")
    if digest(public_edges) != public["public_edges_sha256"]:
        errors.append("public edge digest mismatch")
    expected_delta_divisor = math.gcd(constrained, q)
    expected_delta = {
        "numerator": constrained // expected_delta_divisor,
        "denominator": q // expected_delta_divisor,
    }
    if public["delta"] != expected_delta:
        errors.append("constrained-density ratio mismatch")

    if selected_indices != row["private_audit"]["optimizer"]["selected_indices"]:
        errors.append("optimizer selected-index mismatch")
    if hex(selected_mask) != row["private_audit"]["optimizer"]["selected_mask_hex"]:
        errors.append("optimizer selected-mask mismatch")

    optimum, primary_nodes, complete = independent_primary_optimum(
        curve, eligible, conflicts, selected_mask, maximum_nodes
    )
    optimizer = row["private_audit"]["optimizer"]
    lower = optimizer["retained_support_lower_bound"]
    upper = optimizer["retained_support_upper_bound"]
    if complete:
        if not lower <= optimum <= upper:
            errors.append("producer optimizer interval excludes independent optimum")
        if optimizer["primary_exact"] and not (lower == upper == optimum):
            errors.append("producer exact primary optimum mismatch")
    return {
        "valid": not errors and complete,
        "errors": errors,
        "curve": {"p": curve.p, "a": curve.a, "b": curve.b, "q": q},
        "B": row["B"],
        "family": row["family"],
        "null_replicate": row["null_replicate"],
        "candidate_count": candidate_count,
        "eligible_candidate_count": len(eligible),
        "conflict_count": conflict_count,
        "independent_primary_optimum": optimum,
        "producer_primary_interval": [lower, upper],
        "primary_nodes": primary_nodes,
        "primary_proof_complete": complete,
    }


def verify_document(path: Path, maximum_nodes: int) -> dict[str, Any]:
    document = strict_load(path)
    errors: list[str] = []
    if document.get("schema") != EXPECTED_SCHEMA:
        errors.append("unexpected document schema")
    if document.get("canonical") is not False:
        errors.append("development document claims canonical status")
    supplied = document.get("document_sha256")
    payload = dict(document)
    payload.pop("document_sha256", None)
    if supplied != digest(payload):
        errors.append("document digest mismatch")
    row_reports = [verify_row(row, maximum_nodes) for row in document.get("rows", [])]
    if any(not report["valid"] for report in row_reports):
        errors.append("one or more row verifications failed")
    report = {
        "schema": VERIFICATION_SCHEMA,
        "verifier_source_path": str(SCRIPT_PATH),
        "verifier_source_sha256": file_digest(SCRIPT_PATH),
        "input_path": str(path.resolve()),
        "input_file_sha256": file_digest(path),
        "input_document_sha256": supplied,
        "valid": not errors,
        "errors": errors,
        "row_count": len(row_reports),
        "valid_row_count": sum(bool(row["valid"]) for row in row_reports),
        "total_primary_nodes": sum(row["primary_nodes"] for row in row_reports),
        "rows": row_reports,
        "independent_checks": [
            "strict JSON and document/row digests",
            "curve equation, point count, prime order, trace, j-invariant, and generator",
            "predicate roots, Mobius maps and poles, hash-null ranking, signs, and root polynomial",
            "balanced candidate universe, individual eligibility, and pair-conflict graph",
            "selected graph independence, formal closure, public edges, axioms, density, and retention",
            "degree-1/2/4/8 support and emitted formal-multiset multiplicity/energy fields",
            "independent depth-first proof of the primary coverage optimum",
        ],
        "claim_boundary": "development verification only; not canonical hypothesis evidence",
    }
    report["verification_sha256"] = digest(report)
    return report


def output_path(path: Path) -> Path:
    resolved = path.resolve()
    if DEVELOPMENT_ROOT.resolve() not in resolved.parents:
        raise ValueError("verification output must be below the development directory")
    if resolved.exists():
        raise FileExistsError(resolved)
    return resolved


def write_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("xb") as handle:
        handle.write(stable_bytes(value) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-primary-nodes", type=int, default=5000000)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = verify_document(args.input.resolve(strict=True), args.maximum_primary_nodes)
    write_atomic(output_path(args.output), report)
    print(
        json.dumps(
            {
                "valid": report["valid"],
                "row_count": report["row_count"],
                "valid_row_count": report["valid_row_count"],
                "total_primary_nodes": report["total_primary_nodes"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
