from __future__ import annotations

import copy
import contextvars
import hashlib
import io
import itertools
import json
import math
import os
import re
import runpy
import shutil
import stat
import subprocess
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
SOURCE = (
    REPO_ROOT
    / "experiments"
    / "EXP-SGCP-EMBED-002"
    / "src"
    / "sgcp_embed_family.py"
)
MODULE = runpy.run_path(str(SOURCE))
VERIFIER_SOURCE = SOURCE.with_name("verify_sgcp_embed_family.py")
VERIFIER = runpy.run_path(str(VERIFIER_SOURCE))
_RAW_VERIFY_DENSITY_ROW_FOR_TESTS = VERIFIER["_verify_density_row_for_tests"]
_RAW_VERIFY_V18_DOCUMENT_FOR_TESTS = VERIFIER[
    "_verify_v18_document_value_for_tests"
]


@contextmanager
def verifier_path_test_context():
    verifier_globals = _RAW_VERIFY_DENSITY_ROW_FOR_TESTS.__globals__
    state = verifier_globals["_VerificationState"](
        path_permit=verifier_globals["_PATH_VERIFICATION_PERMIT"],
        owner_thread_id=threading.get_ident(),
    )
    active_state = verifier_globals["_ACTIVE_VERIFICATION_STATE"]
    token = active_state.set(state)
    try:
        yield state
    finally:
        state.closed = True
        active_state.reset(token)


def verify_density_row_for_test(
    row: object,
    maximum_nodes: object,
    scope: str | None = None,
) -> dict[str, object]:
    with verifier_path_test_context():
        return _RAW_VERIFY_DENSITY_ROW_FOR_TESTS(row, maximum_nodes, scope)


def verify_v18_document_for_test(
    document: object,
    maximum_nodes: object,
) -> tuple[list[str], list[dict[str, object]]]:
    with verifier_path_test_context():
        return _RAW_VERIFY_V18_DOCUMENT_FOR_TESTS(document, maximum_nodes)


def independent_publication_status(path: Path) -> dict[str, object]:
    development_root = (
        REPO_ROOT / "experiments" / "EXP-SGCP-EMBED-002" / "development"
    ).resolve(strict=True)
    try:
        raw = os.fspath(path)
    except TypeError:
        return {"accepted": False, "status": "unaccepted_path"}
    if type(raw) is not str:
        return {"accepted": False, "status": "unaccepted_path"}
    if (
        raw == ""
        or "\x00" in raw
        or not raw.startswith("/")
        or raw.endswith("/")
    ):
        return {"accepted": False, "status": "unaccepted_path"}
    components = raw.split("/")
    leading_separators = len(raw) - len(raw.lstrip("/"))
    if (
        components[-1] == "."
        or leading_separators == 2
        or ".." in components
    ):
        return {"accepted": False, "status": "unaccepted_path"}
    admitted = Path(os.path.abspath(raw))
    try:
        relative_path = admitted.relative_to(development_root)
    except ValueError:
        return {"accepted": False, "status": "unaccepted_path"}
    if not relative_path.parts:
        return {"accepted": False, "status": "unaccepted_path"}
    relative = relative_path.as_posix()
    receipt_name = (
        f".{hashlib.sha256(os.fsencode(admitted.name)).hexdigest()}"
        ".publication-receipt.json"
    )
    receipt_path = admitted.with_name(receipt_name)
    try:
        receipt_stat = receipt_path.lstat()
    except FileNotFoundError:
        return {
            "accepted": False,
            "status": "unaccepted_orphan" if admitted.exists() else "absent",
        }
    if not stat.S_ISREG(receipt_stat.st_mode):
        return {"accepted": False, "status": "unaccepted_invalid_receipt"}
    receipt_raw = receipt_path.read_bytes()
    if not receipt_raw.endswith(b"\n"):
        return {"accepted": False, "status": "unaccepted_invalid_receipt"}

    def unique_pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError("duplicate receipt key")
            result[key] = value
        return result

    try:
        receipt = json.loads(
            receipt_raw[:-1].decode("ascii"),
            object_pairs_hook=unique_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite receipt constant {value}")
            ),
        )
    except Exception:
        return {"accepted": False, "status": "unaccepted_invalid_receipt"}
    required_keys = {
        "schema",
        "experiment_id",
        "protocol_version",
        "publication_id",
        "destination_name",
        "destination_relative_path",
        "payload_bytes",
        "payload_sha256",
        "receipt_sha256",
    }
    lower_hex_64 = lambda value: (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
    if (
        type(receipt) is not dict
        or set(receipt) != required_keys
        or receipt["schema"] != "sgcp-embed-002-publication-receipt-v18"
        or receipt["experiment_id"] != "EXP-SGCP-EMBED-002"
        or type(receipt["protocol_version"]) is not int
        or receipt["protocol_version"] != 18
        or not lower_hex_64(receipt["publication_id"])
        or receipt["destination_name"] != admitted.name
        or receipt["destination_relative_path"] != relative
        or type(receipt["payload_bytes"]) is not int
        or receipt["payload_bytes"] < 0
        or not lower_hex_64(receipt["payload_sha256"])
        or not lower_hex_64(receipt["receipt_sha256"])
    ):
        return {"accepted": False, "status": "unaccepted_invalid_receipt"}
    receipt_payload = dict(receipt)
    supplied_digest = receipt_payload.pop("receipt_sha256")
    canonical_payload = json.dumps(
        receipt_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    canonical_receipt = json.dumps(
        receipt,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii") + b"\n"
    if (
        hashlib.sha256(canonical_payload).hexdigest() != supplied_digest
        or canonical_receipt != receipt_raw
    ):
        return {"accepted": False, "status": "unaccepted_invalid_receipt"}
    try:
        payload_stat = admitted.lstat()
        payload = admitted.read_bytes()
    except (FileNotFoundError, OSError):
        return {"accepted": False, "status": "unaccepted_receipt_mismatch"}
    if (
        not stat.S_ISREG(payload_stat.st_mode)
        or len(payload) != receipt["payload_bytes"]
        or hashlib.sha256(payload).hexdigest() != receipt["payload_sha256"]
    ):
        return {"accepted": False, "status": "unaccepted_receipt_mismatch"}
    return {
        "accepted": True,
        "status": "accepted",
        "publication_id": receipt["publication_id"],
        "payload_bytes": receipt["payload_bytes"],
        "payload_sha256": receipt["payload_sha256"],
        "receipt_sha256": supplied_digest,
    }


def exhaustive_graph(
    pair_outputs: list[list[int]], conflicts: list[int]
) -> tuple[int, int]:
    best = (0, 0)
    for mask in range(1 << len(conflicts)):
        if any(conflicts[index] & mask for index in MODULE["iter_mask"](mask)):
            continue
        support = MODULE["support_mask_for_selection"](mask, pair_outputs).bit_count()
        best = max(best, (support, mask.bit_count()))
    return best


def resign_density_row(row: dict[str, object]) -> None:
    payload = dict(row)
    payload.pop("row_sha256", None)
    row["row_sha256"] = VERIFIER["digest"](payload)


def refresh_density_accounting(row: dict[str, object]) -> None:
    public_model = row["public_model"]
    private_audit = row["private_audit"]
    public_caps = public_model["density_frontier"]
    private_caps = private_audit["density_frontier"]
    row_payload = dict(row)
    row_payload.pop("row_sha256", None)
    row_payload.pop("accounting", None)
    row["accounting"] = {
        "scope": "nested canonical-JSON byte measures; fields are nonadditive",
        "public_model_json_bytes": len(VERIFIER["stable_bytes"](public_model)),
        "private_audit_json_bytes": len(VERIFIER["stable_bytes"](private_audit)),
        "row_payload_without_accounting_or_digest_json_bytes": len(
            VERIFIER["stable_bytes"](row_payload)
        ),
        "nested_per_cap_json_bytes": [
            {
                "constrained_cap": public["constrained_cap"],
                "public_embedding_json_bytes": len(VERIFIER["stable_bytes"](public)),
                "private_cap_json_bytes": len(VERIFIER["stable_bytes"](private)),
            }
            for public, private in zip(public_caps, private_caps)
        ],
    }
    resign_density_row(row)


def resign_factor_base(row: dict[str, object]) -> None:
    record = row["public_model"]["factor_base"]
    payload = dict(record)
    payload.pop("selection_sha256", None)
    record["selection_sha256"] = VERIFIER["digest"](payload)


def resign_document(document: dict[str, object]) -> None:
    payload = dict(document)
    payload.pop("document_sha256", None)
    document["document_sha256"] = VERIFIER["digest"](payload)


def synthetic_gate_rows() -> list[dict[str, object]]:
    group_sizes = {5: 23, 6: 47, 7: 97, 8: 193}
    rows = []
    for bits, seed, B, family, replicate in MODULE["canonical_row_keys"]():
        q = group_sizes[bits]
        caps = sorted({max(1, q // 4), max(1, q // 2), max(1, 3 * q // 4), q})
        if family == MODULE["NULL_FAMILY"]:
            support = (1, 2, 2, 3)[replicate]
        else:
            support = q // 2
        public_caps = [{"constrained_cap": cap} for cap in caps]
        private_caps = [
            {
                "constrained_cap": cap,
                "optimizer": {
                    "retained_support_lower_bound": support,
                    "retained_support_upper_bound": support,
                    "primary_exact": True,
                    "full_objective_exact": True,
                    "absolute_gap": 0,
                    "remaining_frontier_nodes": 0,
                    "frontier_states": [],
                    "frontier_sha256": VERIFIER["digest"]([]),
                    "termination_reason": "full_objective_proved",
                    "node_cap": MODULE["CANONICAL_NODE_CAP"],
                },
                "retention": {
                    "retained_to_balanced_raw": {
                        "numerator": 1,
                        "denominator": 2,
                    }
                },
            }
            for cap in caps
        ]
        rows.append(
            {
                "curve": {
                    "bits": bits,
                    "seed": seed,
                    "p": 10_000 * bits + seed,
                    "a": bits,
                    "b": seed,
                    "q": q,
                },
                "B": B,
                "family": family,
                "null_replicate": replicate,
                "public_model": {
                    "constrained_budget_caps": caps,
                    "density_frontier": public_caps,
                },
                "private_audit": {"density_frontier": private_caps},
            }
        )
    return rows


def canonical_factor_base_transcript_rows() -> list[dict[str, object]]:
    """Build public curve/factor-base controls without constructing density rows."""
    curves = {}
    rows = []
    for bits, seed, B, family, replicate in MODULE["canonical_row_keys"]():
        key = (bits, seed)
        if key not in curves:
            ops = MODULE["OperationCounts"]()
            curves[key] = (*MODULE["_generated_curve_for_controls"](bits, seed, ops), ops)
        curve, points, record, ops = curves[key]
        _, factor_record = MODULE["factor_base"](
            curve,
            points,
            record,
            B,
            family,
            replicate,
            ops,
        )
        rows.append(
            {
                "curve": record,
                "B": B,
                "family": family,
                "null_replicate": replicate,
                "public_model": {"factor_base": factor_record},
            }
        )
    return rows


def standalone_point_order(point):
    return (0, 0, 0) if point is None else (1, point[0], point[1])


def standalone_stable_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def standalone_digest(value):
    return hashlib.sha256(standalone_stable_bytes(value)).hexdigest()


def standalone_point_record(point):
    return "O" if point is None else [point[0], point[1]]


def standalone_label(point):
    return "O" if point is None else f"{point[0]}:{point[1]}"


def standalone_add(p, a, left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def standalone_eval(p, a, factors, formal):
    point = None
    for index in formal:
        point = standalone_add(p, a, point, factors[index])
    return point


def standalone_submultisets(formal):
    values = {()}
    for degree in range(1, len(formal) + 1):
        values.update(itertools.combinations(formal, degree))
    return values


def standalone_ideal(B, maxima):
    values = {(), *((index,) for index in range(B))}
    for maximum in maxima:
        values.update(standalone_submultisets(tuple(sorted(maximum))))
    return values


def standalone_polynomial(roots, p):
    coefficients = [1]
    for root in roots:
        updated = [0] * (len(coefficients) + 1)
        for index, coefficient in enumerate(coefficients):
            updated[index] = (updated[index] - root * coefficient) % p
            updated[index + 1] = (updated[index + 1] + coefficient) % p
        coefficients = updated
    return coefficients


def standalone_graph_metrics(conflicts):
    count = len(conflicts)
    degrees = [mask.bit_count() for mask in conflicts]
    unseen = set(range(count))
    components = []
    while unseen:
        stack = [min(unseen)]
        unseen.remove(stack[0])
        component = []
        while stack:
            vertex = stack.pop()
            component.append(vertex)
            neighbors = {
                index for index in unseen if conflicts[vertex] & (1 << index)
            }
            unseen.difference_update(neighbors)
            stack.extend(sorted(neighbors, reverse=True))
        components.append(sorted(component))
    remaining = set(range(count))
    degeneracy = 0
    while remaining:
        vertex = min(
            remaining,
            key=lambda index: (
                sum(bool(conflicts[index] & (1 << other)) for other in remaining),
                index,
            ),
        )
        degree = sum(
            bool(conflicts[vertex] & (1 << other)) for other in remaining
        )
        degeneracy = max(degeneracy, degree)
        remaining.remove(vertex)
    histogram = {str(degree): degrees.count(degree) for degree in sorted(set(degrees))}
    return {
        "vertices": count,
        "edges": sum(degrees) // 2,
        "components": sorted(len(component) for component in components),
        "component_count": len(components),
        "degree_min": min(degrees, default=0),
        "degree_max": max(degrees, default=0),
        "degree_histogram": histogram,
        "degeneracy": degeneracy,
    }


def standalone_frozen_b4_oracle():
    """Rebuild the B4 object without producer or verifier semantic helpers."""
    p = 19
    a = 2
    b = 9
    B = 4
    affine = [
        (x, y)
        for x in range(p)
        for y in range(p)
        if (y * y - (x * x * x + a * x + b)) % p == 0
    ]
    q = len(affine) + 1
    fibers = {}
    for point in affine:
        fibers.setdefault(point[0], []).append(point)
    admissible = [
        x
        for x in sorted(fibers)
        if len(fibers[x]) == 2
        and (fibers[x][0][1] + fibers[x][1][1]) % p == 0
    ]
    roots = admissible[: B // 2]
    factors = sorted(
        [point for x in roots for point in fibers[x]], key=standalone_point_order
    )
    factor_base = {
        "family": "least_x_interval",
        "null_replicate": None,
        "B": B,
        "admissible_root_count": len(admissible),
        "selected_roots": roots,
        "selected_root_count": len(roots),
        "excluded_poles": [],
        "parameters": {},
        "root_polynomial_coefficients_ascending_mod_p": standalone_polynomial(
            roots, p
        ),
        "points": [standalone_point_record(point) for point in factors],
        "negation_symmetric": True,
    }
    factor_base["selection_sha256"] = standalone_digest(factor_base)

    degree2_by_point = {}
    for formal in itertools.combinations_with_replacement(range(B), 2):
        point = standalone_eval(p, a, factors, formal)
        degree2_by_point.setdefault(point, []).append(formal)
    representatives = [
        (point, min(degree2_by_point[point]))
        for point in sorted(degree2_by_point, key=standalone_point_order)
        if point is not None
    ]
    representative_records = [
        {"point": standalone_point_record(point), "formal": list(formal)}
        for point, formal in representatives
    ]
    representative_compiler = {
        "id": "lexicographically_least_formal_per_nonidentity_2F_output_v2",
        "identity_output_excluded": True,
        "representative_count": len(representative_records),
        "representatives": representative_records,
        "representatives_sha256": standalone_digest(representative_records),
    }

    candidate_points = {}
    candidate_parent_pairs = {}
    for left, right in itertools.combinations_with_replacement(
        range(len(representatives)), 2
    ):
        left_point, left_formal = representatives[left]
        right_point, right_formal = representatives[right]
        formal = tuple(sorted(left_formal + right_formal))
        point = standalone_add(p, a, left_point, right_point)
        parent_pair = tuple(sorted((left_formal, right_formal)))
        if formal in candidate_points:
            assert candidate_points[formal] == point
        candidate_points[formal] = point
        candidate_parent_pairs.setdefault(formal, []).append(parent_pair)
    candidates = [
        {
            "formal": formal,
            "point": candidate_points[formal],
            "parent_pairs": sorted(candidate_parent_pairs[formal]),
        }
        for formal in sorted(candidate_points)
    ]

    eligible = []
    eligible_universe_indices = []
    rejected = []
    closure_maps = []
    for universe_index, candidate in enumerate(candidates):
        family = standalone_ideal(B, [candidate["formal"]])
        point_to_formal = {}
        first_collision = None
        for formal in sorted(family, key=lambda item: (len(item), item)):
            point = standalone_eval(p, a, factors, formal)
            if point in point_to_formal:
                first_collision = (point_to_formal[point], formal, point)
                break
            point_to_formal[point] = formal
        if first_collision is None:
            eligible.append(candidate)
            eligible_universe_indices.append(universe_index)
            closure_maps.append(point_to_formal)
        else:
            left, right, point = first_collision
            rejected.append(
                {
                    "universe_index": universe_index,
                    "formal": list(candidate["formal"]),
                    "point": standalone_point_record(candidate["point"]),
                    "first_collision": {
                        "left": list(left),
                        "right": list(right),
                        "point": standalone_point_record(point),
                    },
                }
            )

    conflicts = [0] * len(eligible)
    conflict_records = []
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            first_collision = next(
                (
                    (
                        closure_maps[left][point],
                        closure_maps[right][point],
                        point,
                    )
                    for point in sorted(
                        set(closure_maps[left]).intersection(closure_maps[right]),
                        key=standalone_point_order,
                    )
                    if closure_maps[left][point] != closure_maps[right][point]
                ),
                None,
            )
            if first_collision is not None:
                conflicts[left] |= 1 << right
                conflicts[right] |= 1 << left
                left_formal, right_formal, point = first_collision
                conflict_records.append(
                    {
                        "left": left,
                        "right": right,
                        "left_universe_index": eligible_universe_indices[left],
                        "right_universe_index": eligible_universe_indices[right],
                        "first_collision": {
                            "left": list(left_formal),
                            "right": list(right_formal),
                            "point": standalone_point_record(point),
                        },
                    }
                )

    candidates_by_cap = {}
    for mask in range(1 << len(eligible)):
        selected_indices = [
            index for index in range(len(eligible)) if mask & (1 << index)
        ]
        if any(conflicts[index] & mask for index in selected_indices):
            continue
        maxima = [eligible[index]["formal"] for index in selected_indices]
        family = standalone_ideal(B, maxima)
        evaluations = {
            formal: standalone_eval(p, a, factors, formal) for formal in family
        }
        assert len(set(evaluations.values())) == len(evaluations)
        nonempty = sorted(
            (formal for formal in family if formal), key=lambda item: (len(item), item)
        )
        constrained = {None}
        edges = []
        for position, left in enumerate(nonempty):
            for right in nonempty[position:]:
                union = tuple(sorted(left + right))
                if union not in family:
                    continue
                edges.append((left, right, union))
                constrained.update(
                    (evaluations[left], evaluations[right], evaluations[union])
                )
        selected_points = [eligible[index]["point"] for index in selected_indices]
        support = {
            standalone_add(p, a, left, right)
            for position, left in enumerate(selected_points)
            for right in selected_points[position:]
        }
        objective = (len(support), -len(constrained), -len(edges), len(maxima))
        witness = tuple(sorted(maxima))
        public_edges = [
            {
                "left": standalone_label(evaluations[left]),
                "right": standalone_label(evaluations[right]),
                "output": standalone_label(evaluations[output]),
            }
            for left, right, output in edges
        ]
        source_table = [
            {"label": standalone_label(point), "formal": list(formal)}
            for point, formal in sorted(
                (
                    (point, formal)
                    for formal, point in evaluations.items()
                    if point in constrained
                ),
                key=lambda item: standalone_point_order(item[0]),
            )
        ]
        degree_histogram = {
            str(degree): sum(len(formal) == degree for formal in family)
            for degree in sorted({len(formal) for formal in family})
        }
        forbidden_final_edges = sum(
            len(left) == 4 and len(right) == 4 for left, right, _ in edges
        )
        axioms = {
            "identity": True,
            "commutativity": True,
            "associativity": all(
                standalone_submultisets(formal).issubset(family)
                for formal in family
            ),
            "associativity_method": "downward-closed formal multiset union",
            "compatibility_coordinates": all(
                standalone_add(
                    p, a, evaluations[left], evaluations[right]
                )
                == evaluations[output]
                for left, right, output in edges
            ),
            "injective_evaluation": len(set(evaluations.values())) == len(evaluations),
            "unique_prime_multiset_factorization": len(set(evaluations.values()))
            == len(evaluations),
            "acyclic_by_formal_degree": all(
                len(output) > max(len(left), len(right))
                for left, right, output in edges
            ),
            "source_recovery": all(tuple(sorted(formal)) == formal for formal in family),
            "source_recovery_via_public_table": len(source_table) == len(constrained),
            "direct_final_edge_excluded": forbidden_final_edges == 0,
            "direct_final_edge_absent_by_construction": forbidden_final_edges == 0,
            "forbidden_final_edge_count": forbidden_final_edges,
        }
        divisor = math.gcd(len(constrained), q)
        candidate = {
            "objective": objective,
            "witness": witness,
            "selected_indices": selected_indices,
            "selected_mask_hex": hex(sum(1 << index for index in selected_indices)),
            "formal_family_count": len(family),
            "formal_degree_histogram": degree_histogram,
            "constrained_count": len(constrained),
            "delta": {
                "numerator": len(constrained) // divisor,
                "denominator": q // divisor,
            },
            "constrained_labels": [
                standalone_label(point)
                for point in sorted(constrained, key=standalone_point_order)
            ],
            "public_edge_count": len(edges),
            "public_edges": public_edges,
            "public_edges_sha256": standalone_digest(public_edges),
            "source_table": source_table,
            "source_table_sha256": standalone_digest(source_table),
            "axioms": axioms,
        }
        caps = sorted({max(1, q // 4), max(1, q // 2), max(1, 3 * q // 4), q})
        for cap in caps:
            if len(constrained) <= cap:
                candidates_by_cap.setdefault(cap, []).append(candidate)

    winners = {}
    for cap, values in candidates_by_cap.items():
        best_objective = max(value["objective"] for value in values)
        best_witness = min(
            value["witness"]
            for value in values
            if value["objective"] == best_objective
        )
        winners[cap] = next(
            value
            for value in values
            if value["objective"] == best_objective
            and value["witness"] == best_witness
        )
    return {
        "factors": factors,
        "factor_base": factor_base,
        "representatives": representative_records,
        "representative_compiler": representative_compiler,
        "candidates": candidates,
        "eligible": eligible,
        "candidate_count": len(candidates),
        "eligible_count": len(eligible),
        "eligible_universe_indices": eligible_universe_indices,
        "individually_rejected": rejected,
        "conflicts": conflict_records,
        "conflict_count": len(conflict_records),
        "graph_metrics": standalone_graph_metrics(conflicts),
        "caps": caps,
        "winners": winners,
    }


def configure_gate_rows(null_supports=(8, 8, 10, 12)):
    rows = synthetic_gate_rows()
    for row in rows:
        support = null_supports[row["null_replicate"]] if row["family"] == MODULE["NULL_FAMILY"] else 10
        for private in row["private_audit"]["density_frontier"]:
            private["optimizer"]["retained_support_lower_bound"] = support
            private["optimizer"]["retained_support_upper_bound"] = support
    return rows


def set_gate_differences(rows, family, cap_fraction, differences_by_bits):
    for bits in MODULE["CANONICAL_BITS"]:
        coordinate_rows = [
            row
            for row in rows
            if row["curve"]["bits"] == bits
            and row["family"] == family
            and row["null_replicate"] is None
        ]
        coordinate_rows.sort(key=lambda row: (row["curve"]["seed"], row["B"]))
        for row, difference in zip(coordinate_rows, differences_by_bits[bits]):
            q = row["curve"]["q"]
            cap = q // 2 if cap_fraction == "1/2" else 3 * q // 4
            cell = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == cap
            )
            cell["optimizer"]["retained_support_lower_bound"] = 9 + difference
            cell["optimizer"]["retained_support_upper_bound"] = 9 + difference


def gate_cap_report(gate, family, cap_fraction):
    family_report = next(value for value in gate["families"] if value["family"] == family)
    return next(
        value
        for value in family_report["matched_null_cap_tests"]
        if value["cap_fraction"] == cap_fraction
    )


class SgcpEmbedFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        cls.frozen_density_row = MODULE["build_density_row"](
            curve,
            points,
            record,
            4,
            "least_x_interval",
            None,
            100000,
            ops,
        )
        cls.transient_legacy_control_rows = {
            B: MODULE["_build_frozen_legacy_control_row"](B)
            for B in (4, 6, 8)
        }
        cls.transient_legacy_control_receipt = {
            "B_values": [4, 6, 8],
            "row_count": 3,
            "curve_family_density_rows": 0,
            "row_sha256": [
                cls.transient_legacy_control_rows[B]["row_sha256"]
                for B in (4, 6, 8)
            ],
        }

    def test_curve_sampler_enforces_registered_filters(self) -> None:
        with verifier_path_test_context():
            for bits, seed in itertools.product((5, 6, 7, 8), (101, 211)):
                with self.subTest(bits=bits, seed=seed):
                    ops = MODULE["OperationCounts"]()
                    curve, points, record = MODULE["_generated_curve_for_controls"](
                        bits, seed, ops
                    )
                    self.assertEqual(len(points), record["q"])
                    self.assertEqual(record["q"].bit_length(), bits)
                    self.assertTrue(MODULE["is_prime"](record["q"]))
                    self.assertNotIn(record["trace"], (0, 1))
                    self.assertNotIn(record["j"], (0, 1728 % curve.p))
                    self.assertTrue(all(curve.on_curve(point) for point in points))
                    self.assertEqual(
                        MODULE["stable_digest"](record["rejected_draws"]),
                        record["rejection_digest"],
                    )
                    verified_curve = VERIFIER["verify_curve_provenance"](record)
                    self.assertEqual(
                        (verified_curve.p, verified_curve.a, verified_curve.b),
                        (curve.p, curve.a, curve.b),
                    )

    def test_v18_public_generated_construction_is_gated_before_row_math(self) -> None:
        producer_globals = MODULE["build_density_row"].__globals__
        original_generated_control = producer_globals["_generated_curve_for_controls"]
        original_factor_base = producer_globals["factor_base"]
        calls = []

        def forbidden_generated_control(*_args, **_kwargs):
            calls.append("generated_curve")
            raise AssertionError("public gate must precede generated-curve control")

        def forbidden_factor_base(*_args, **_kwargs):
            calls.append("factor_base")
            raise AssertionError("public gate must precede factor-base work")

        producer_globals["_generated_curve_for_controls"] = forbidden_generated_control
        try:
            with self.assertRaisesRegex(PermissionError, "public generated-curve"):
                MODULE["generated_curve"](5, 101)

            ops = MODULE["OperationCounts"]()
            curve, points, record = MODULE["frozen_curve"](ops)
            non_frozen_association = copy.deepcopy(record)
            non_frozen_association["draw"] = 0
            producer_globals["factor_base"] = forbidden_factor_base
            before_ops = vars(ops).copy()
            cases = (
                (points, non_frozen_association, 100000),
                (points[:-1] + [points[-2]], record, 100000),
                ([points[0], (False, 3), *points[2:]], record, 100000),
                (points, record, 100000.0),
            )
            for candidate_points, candidate_record, node_cap in cases:
                with self.subTest(node_cap=node_cap, record=candidate_record):
                    with self.assertRaisesRegex(
                        PermissionError, "density-row construction"
                    ):
                        MODULE["build_density_row"](
                            curve,
                            candidate_points,
                            candidate_record,
                            4,
                            "least_x_interval",
                            None,
                            node_cap,
                            ops,
                        )
            for candidate_record in (record, non_frozen_association):
                with self.subTest(legacy_record=candidate_record):
                    with self.assertRaisesRegex(
                        PermissionError, "legacy-row construction"
                    ):
                        MODULE["build_legacy_row"](
                            curve,
                            points,
                            candidate_record,
                            4,
                            "least_x_interval",
                            None,
                            100000,
                            ops,
                        )
            original_all = producer_globals.get("all")

            def forbidden_point_scan(*_args, **_kwargs):
                calls.append("point_scan")
                raise AssertionError("length rejection must precede point scanning")

            producer_globals["all"] = forbidden_point_scan
            try:
                with self.assertRaisesRegex(PermissionError, "density-row construction"):
                    MODULE["build_density_row"](
                        curve,
                        [*points, None],
                        record,
                        4,
                        "least_x_interval",
                        None,
                        100000,
                        ops,
                    )
            finally:
                if original_all is None:
                    producer_globals.pop("all", None)
                else:
                    producer_globals["all"] = original_all
            self.assertEqual(vars(ops), before_ops)
        finally:
            producer_globals["_generated_curve_for_controls"] = original_generated_control
            producer_globals["factor_base"] = original_factor_base
        self.assertEqual(calls, [])

    def test_frozen_legacy_control_rejects_noncanonical_B_before_curve_work(self) -> None:
        helper_globals = MODULE["_build_frozen_legacy_control_row"].__globals__
        original_frozen_curve = helper_globals["frozen_curve"]
        calls = []

        def forbidden_frozen_curve(*_args, **_kwargs):
            calls.append("frozen_curve")
            raise AssertionError("B validation must precede frozen-curve work")

        helper_globals["frozen_curve"] = forbidden_frozen_curve
        try:
            for B in (False, 3, 10):
                with self.subTest(B=B):
                    with self.assertRaisesRegex(ValueError, "B must be one of"):
                        MODULE["_build_frozen_legacy_control_row"](B)
        finally:
            helper_globals["frozen_curve"] = original_frozen_curve
        self.assertEqual(calls, [])

    def test_curve_rejection_transcript_records_duplicates_and_complete_reasons(
        self,
    ) -> None:
        fixtures = [
            ((17, 0, 0), "singular"),
            ((17, 0, 1), "trace_zero"),
            ((17, 1, 3), "anomalous_trace_one"),
            ((19, 0, 2), "j_zero"),
            ((17, 1, 0), "j_1728"),
        ]
        for (p, a, b), expected_reason in fixtures:
            with self.subTest(reason=expected_reason):
                reasons, _ = MODULE["curve_rejection_reasons"](p, a, b, 5)
                self.assertIn(expected_reason, reasons)
                for duplicate in (False, True):
                    produced = MODULE["ordered_curve_rejection_reasons"](
                        p, a, b, 5, duplicate
                    )
                    independently_reconstructed = VERIFIER[
                        "ordered_independent_rejection_reasons"
                    ](p, a, b, 5, duplicate)
                    self.assertEqual(produced, independently_reconstructed)
                    if duplicate:
                        self.assertEqual(produced[0][0], "duplicate_candidate")

        multi_reason = MODULE["ordered_curve_rejection_reasons"](
            5, 0, 1, 4, True
        )
        self.assertEqual(
            multi_reason,
            VERIFIER["ordered_independent_rejection_reasons"](
                5, 0, 1, 4, True
            ),
        )
        self.assertEqual(
            multi_reason[0],
            [
                "duplicate_candidate",
                "wrong_q_bit_length",
                "nonprime_group_order",
                "trace_zero",
                "j_zero",
            ],
        )

        generated_globals = MODULE["_generated_curve_for_controls"].__globals__
        original_hash = generated_globals["hash_int"]

        def scripted_hash(domain, fields, modulus, ops=None):
            draw = fields[2]
            if domain == "sgcp-002-curve-p":
                return 1
            if domain == "sgcp-002-curve-a":
                return (0, 0, 2)[draw] % modulus
            if domain == "sgcp-002-curve-b":
                return (0, 0, 9)[draw] % modulus
            raise AssertionError(domain)

        generated_globals["hash_int"] = scripted_hash
        try:
            _, _, record = MODULE["_generated_curve_for_controls"](5, 999)
        finally:
            generated_globals["hash_int"] = original_hash
        self.assertEqual(record["draw"], 2)
        self.assertEqual(record["rejected_draws"][0]["reasons"], ["singular"])
        self.assertEqual(
            record["rejected_draws"][1]["reasons"],
            ["duplicate_candidate", "singular"],
        )

    def test_generated_curve_provenance_mutation_is_rejected(self) -> None:
        ops = MODULE["OperationCounts"]()
        _, _, record = MODULE["_generated_curve_for_controls"](5, 101, ops)
        with verifier_path_test_context():
            VERIFIER["verify_curve_provenance"](record)
            mutated = copy.deepcopy(record)
            mutated["rejection_digest"] = "0" * 64
            with self.assertRaises(AssertionError):
                VERIFIER["verify_curve_provenance"](mutated)

    def test_predicates_are_matched_and_deterministic(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["_generated_curve_for_controls"](6, 101, ops)
        jobs = [
            ("least_x_interval", None),
            ("mobius_interval", None),
            ("two_mobius_union", None),
            ("hash_x_null", 0),
            ("hash_x_null", 1),
        ]
        for family, replicate in jobs:
            with self.subTest(family=family, replicate=replicate):
                factors, first = MODULE["factor_base"](
                    curve, points, record, 8, family, replicate, ops
                )
                repeated_factors, second = MODULE["factor_base"](
                    curve, points, record, 8, family, replicate, ops
                )
                self.assertEqual(factors, repeated_factors)
                self.assertEqual(first, second)
                self.assertEqual(len(factors), 8)
                self.assertEqual(first["selected_root_count"], 4)
                self.assertTrue(first["negation_symmetric"])
                for point in factors:
                    self.assertIn(curve.neg(point), factors)

    def test_predicate_replicate_rules_and_mobius_transcript_are_enforced(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        with self.assertRaises(ValueError):
            MODULE["factor_base"](
                curve, points, record, 4, "least_x_interval", 999, ops
            )
        with self.assertRaises(ValueError):
            MODULE["factor_base"](curve, points, record, 4, "hash_x_null", 4, ops)

        curve, points, record = MODULE["_generated_curve_for_controls"](6, 101, ops)
        _, factor_record = MODULE["factor_base"](
            curve, points, record, 4, "mobius_interval", None, ops
        )
        row = {
            "curve": record,
            "B": 4,
            "family": "mobius_interval",
            "null_replicate": None,
            "public_model": {"factor_base": factor_record},
        }
        verifier_curve = VERIFIER["Curve"](
            record["p"], record["a"], record["b"]
        )
        verifier_group = verifier_curve.points()
        VERIFIER["verify_factor_base"](verifier_curve, verifier_group, row)
        mutated = copy.deepcopy(row)
        mutated["public_model"]["factor_base"]["parameters"]["map"]["nonce"] += 1
        resign_factor_base(mutated)
        with self.assertRaisesRegex(
            AssertionError, "Mobius derivation transcript mismatch"
        ):
            VERIFIER["verify_factor_base"](
                verifier_curve, verifier_group, mutated
            )

        illegal = copy.deepcopy(self.frozen_density_row)
        illegal["null_replicate"] = 999
        illegal["public_model"]["factor_base"]["null_replicate"] = 999
        resign_factor_base(illegal)
        refresh_density_accounting(illegal)
        report = verify_density_row_for_test(
            illegal, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "frozen row grid association mismatch" in error
                for error in report["errors"]
            )
        )

    def test_branch_and_bound_matches_exhaustive_graph_fixtures(self) -> None:
        fixtures = [
            [0, 0, 0, 0, 0],
            [0b11110, 0b11101, 0b11011, 0b10111, 0b01111],
            [0b00010, 0b00101, 0b01010, 0b10100, 0b01000],
            [0b10010, 0b00101, 0b01010, 0b10100, 0b01001],
        ]
        point_count = 11
        pair_outputs = [
            [((left + 1) * (right + 2) + left + right) % point_count for right in range(5)]
            for left in range(5)
        ]
        for conflicts in fixtures:
            for left in range(5):
                for right in range(5):
                    pair_outputs[right][left] = pair_outputs[left][right]
            with self.subTest(conflicts=conflicts):
                expected = exhaustive_graph(pair_outputs, conflicts)
                observed = MODULE["optimize_coverage_graph"](
                    pair_outputs, point_count, conflicts, 100000
                )
                self.assertTrue(observed["primary_exact"])
                self.assertTrue(observed["full_objective_exact"])
                self.assertEqual(
                    (
                        observed["retained_support_lower_bound"],
                        observed["selected_count"],
                    ),
                    expected,
                )

    def test_forced_cap_returns_interval_containing_exact_optimum(self) -> None:
        candidate_count = 9
        point_count = 17
        pair_outputs = [
            [((left + 3) * (right + 5) + left) % point_count for right in range(candidate_count)]
            for left in range(candidate_count)
        ]
        for left in range(candidate_count):
            for right in range(candidate_count):
                pair_outputs[right][left] = pair_outputs[left][right]
        conflicts = [0] * candidate_count
        for left, right in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)):
            conflicts[left] |= 1 << right
            conflicts[right] |= 1 << left
        optimum, _ = exhaustive_graph(pair_outputs, conflicts)
        capped = MODULE["optimize_coverage_graph"](
            pair_outputs, point_count, conflicts, 0
        )
        self.assertLessEqual(capped["retained_support_lower_bound"], optimum)
        self.assertGreaterEqual(capped["retained_support_upper_bound"], optimum)
        self.assertEqual(capped["termination_reason"], "node_cap")
        self.assertTrue(capped["frontier_states"])
        self.assertGreater(capped["absolute_gap"], 0)
        self.assertFalse(capped["primary_exact"])
        self.assertFalse(capped["full_objective_exact"])
        self.assertEqual(
            VERIFIER["verify_frontier_certificate"](
                pair_outputs, point_count, conflicts, capped
            ),
            [],
        )

    def test_frozen_fixture_reproduces_predecessor_optima(self) -> None:
        expected = {
            4: (31, 12, 20, 13, 5, 20, 26),
            6: (68, 8, 4, 7, 4, 17, 20),
            8: (124, 14, 53, 7, 4, 14, 21),
        }
        for B, values in expected.items():
            with self.subTest(B=B):
                row = copy.deepcopy(self.transient_legacy_control_rows[B])
                graph = row["private_audit"]["graph"]
                optimizer = row["private_audit"]["optimizer"]
                self.assertEqual(
                    (
                        graph["candidate_count"],
                        graph["eligible_candidate_count"],
                        graph["conflict_count"],
                        optimizer["retained_support_lower_bound"],
                        optimizer["selected_count"],
                        optimizer["constrained_count"],
                        optimizer["public_edge_count"],
                    ),
                    values,
                )
                self.assertTrue(optimizer["primary_exact"])
                self.assertTrue(optimizer["full_objective_exact"])
                self.assertTrue(
                    all(
                        value
                        for key, value in row["public_model"]["axioms"].items()
                        if key not in {"associativity_method", "forbidden_final_edge_count"}
                    )
                )

    def _reviewed_v18_tree(self) -> str:
        """The one exact tree DEC-SGCP-EMBED-002-018 says was reviewed.

        Read from the decision record rather than hardcoded, so the test can
        never certify a surface the decision did not name, and cross-checked
        against all three pre-run reviews so a single edited document cannot
        move it.
        """
        experiment_root = SOURCE.parents[1]
        decision = json.loads(
            (experiment_root / "decision-v18.json").read_text(encoding="ascii")
        )["coordinator_decision"]
        trees = {
            match
            for rationale in decision["rationale"]
            for match in re.findall(r"tree ([0-9a-f]{40})", rationale)
        }
        self.assertEqual(len(trees), 1, trees)
        tree = trees.pop()
        for name in ("pre-run-theory-review-v18.md",
                     "pre-run-accounting-review-v18.md",
                     "pre-run-red-team-review-v18.md"):
            self.assertIn(
                tree,
                (experiment_root / name).read_text(encoding="utf-8"),
                name,
            )
        return tree

    def test_v18_discloses_exact_transient_legacy_control_scope(self) -> None:
        experiment_root = SOURCE.parents[1]
        amendment_path = experiment_root / "protocol-amendment-v18.json"
        amendment = json.loads(amendment_path.read_text(encoding="ascii"))[
            "protocol_amendment"
        ]
        specification = json.loads(
            (experiment_root / "specification.json").read_text(encoding="ascii")
        )["experiment"]
        ledger = json.loads(
            (REPO_ROOT / "ledger.json").read_text(encoding="ascii")
        )
        ledger_entry = next(
            entry
            for entry in ledger["ledger"]["experiments"]
            if entry["id"] == "EXP-SGCP-EMBED-002"
        )
        contract_title = (
            (experiment_root / "contract.md")
            .read_text(encoding="ascii")
            .splitlines()[0]
        )
        handoff = (experiment_root / "handoff.md").read_text(encoding="ascii")
        research_ledger = (REPO_ROOT / "research_ledger.md").read_text(
            encoding="ascii"
        )
        revision_response = (
            experiment_root / "revision-response-v18.md"
        ).read_text(encoding="ascii")
        test_log = (experiment_root / "development-test-log-v18.md").read_text(
            encoding="ascii"
        )
        manifest = json.loads(
            (experiment_root / "review-surface-manifest-v18.json").read_text(
                encoding="ascii"
            )
        )["review_surface_manifest"]
        self.assertEqual(amendment["version_from"], 17)
        self.assertEqual(amendment["version_to"], 18)
        self.assertEqual(specification["version"], 18)
        self.assertEqual(ledger_entry["version"], 18)
        self.assertEqual(MODULE["PROTOCOL_VERSION"], 18)
        self.assertEqual(VERIFIER["PROTOCOL_VERSION"], 18)
        self.assertEqual(
            contract_title,
            "# Experiment Contract: EXP-SGCP-EMBED-002, version 18",
        )
        # V18 has since passed its three exact-commit reviews, so both
        # documents disclose the closed-out state rather than the pending one.
        # The assertion still pins WHICH state is disclosed -- it must not
        # silently drift back to "awaiting review".
        self.assertIn("## Handoff: SGCP V18 exact-commit review closeout", handoff)
        self.assertIn(
            "The V18 CLI-ingress, historical-evidence, callback-scope, and "
            "Git-entry review repair is ready for separate non-executing "
            "launch-plan design.",
            research_ledger,
        )
        for document in (revision_response, test_log):
            next_action = document.split("## Next action", 1)[1]
            self.assertIn("exact Git commit and tree", next_action)
            self.assertNotIn("validate and commit", next_action.lower())
        self.assertEqual(manifest["protocol_version"], 18)
        self.assertFalse(manifest["binding"]["self_hashing"])
        self.assertFalse(manifest["binding"]["predicted_commit_or_tree"])
        self.assertTrue(manifest["binding"]["entry_metadata_digest_only"])
        self.assertEqual(
            manifest["authority"],
            {
                "generated_v18_curve_family_density_rows": 0,
                "canonical_runs": 0,
                "historical_v1_development_rows": 17,
                "historical_development_run_manifests": 1,
                "maximum_runs": 0,
                "launch_plan_authorized": False,
                "execution_authorized": False,
            },
        )

        # The receipt certifies the surface the three V18 reviewers actually
        # inspected. `binding.required_reviewer_checks` says that surface is
        # enumerated with `git ls-tree -rz --full-tree` over one exact tree,
        # and DEC-SGCP-EMBED-002-018 records that each reviewer reproduced the
        # 200-entry receipt "from git ls-tree". Re-deriving it from the working
        # tree instead re-certifies whatever the repository happens to hold
        # today, which drifts every time an unrelated file lands in tests/,
        # schemas/ or src/crypto_autoresearcher/ -- and had already drifted to
        # 206 entries.
        reviewed_tree = self._reviewed_v18_tree()
        if subprocess.run(
            ["git", "cat-file", "-t", reviewed_tree],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        ).stdout.strip() != "tree":
            self.skipTest(
                f"reviewed V18 tree {reviewed_tree} is not present in this "
                f"clone, so the inventory receipt cannot be reproduced from "
                f"the surface the reviewers inspected")

        rules = manifest["inventory_rules"]
        tree_paths = subprocess.run(
            ["git", "ls-tree", "-r", "--full-tree", "--name-only",
             reviewed_tree],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.splitlines()

        inventoried_paths = set(rules["repository_exact_paths"])
        for rule in rules["flat_directory_rules"]:
            prefix = rule["directory"].rstrip("/") + "/"
            for relative in tree_paths:
                if not relative.startswith(prefix):
                    continue
                name = relative[len(prefix):]
                if "/" in name:                       # flat rule, not recursive
                    continue
                if (
                    name.startswith(rules["exclude_appledouble_prefix"])
                    or not name.endswith(rule["suffix"])
                ):
                    continue
                inventoried_paths.add(relative)
        static_prefix = rules["experiment_static_root"].rstrip("/") + "/"
        for relative in tree_paths:
            if not relative.startswith(static_prefix):
                continue
            relative_static = relative[len(static_prefix):]
            name = relative_static.rsplit("/", 1)[-1]
            if (
                name.startswith(rules["exclude_appledouble_prefix"])
                or name in rules["experiment_excluded_basenames"]
                or not any(name.endswith(suffix)
                           for suffix in rules["experiment_static_suffixes"])
            ):
                continue
            if any(
                component in rules["experiment_excluded_components"]
                for component in relative_static.split("/")
                ):
                continue
            inventoried_paths.add(relative)
        inventoried_paths.update(
            rules["experiment_historical_evidence_exact_paths"]
        )

        entry_records = bytearray()
        for relative in sorted(
            inventoried_paths, key=lambda value: value.encode("ascii")
        ):
            encoded_path = relative.encode("ascii")
            self.assertFalse(
                any(byte <= 0x1F or byte == 0x7F for byte in encoded_path)
            )
            entry_records.extend(b"100644\0blob\0")
            entry_records.extend(encoded_path)
            entry_records.extend(b"\0")
        self.assertEqual(
            manifest["inventory_receipt"],
            {
                "entry_count": len(inventoried_paths),
                "entry_records_sha256": hashlib.sha256(
                    entry_records
                ).hexdigest(),
            },
        )
        self.assertEqual(
            amendment["budget"],
            {
                "additional_development_curve_rows": 0,
                "generated_v18_curve_family_density_rows": 0,
                "canonical_maximum_runs": 0,
                "historical_v1_development_rows": 17,
                "historical_development_run_manifests": 1,
                "transient_legacy_semantic_control_rows": {
                    "B_values": [4, 6, 8],
                    "classification": (
                        "noncanonical test-only predecessor reproductions"
                    ),
                    "curve_family_density_rows": 0,
                },
                "launch_plan_authorized": False,
                "execution_authorized": False,
            },
        )
        declared = amendment["budget"]["transient_legacy_semantic_control_rows"]
        self.assertEqual(
            declared,
            {
                "B_values": [4, 6, 8],
                "classification": "noncanonical test-only predecessor reproductions",
                "curve_family_density_rows": 0,
            },
        )
        self.assertEqual(
            self.transient_legacy_control_receipt,
            {
                "B_values": [4, 6, 8],
                "row_count": 3,
                "curve_family_density_rows": 0,
                "row_sha256": [
                    self.transient_legacy_control_rows[B]["row_sha256"]
                    for B in (4, 6, 8)
                ],
            },
        )

    def test_pairwise_conflict_graph_matches_full_closure_on_frozen_B4(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        factors, _ = MODULE["factor_base"](
            curve, points, record, 4, "least_x_interval", None, ops
        )
        universe = MODULE["balanced_universe"](curve, factors)
        graph = MODULE["candidate_graph"](curve, factors, universe["candidates"])
        eligible = graph["eligible"]
        conflicts = graph["conflict_masks"]
        for mask in range(1 << len(eligible)):
            graph_feasible = not any(
                conflicts[index] & mask for index in MODULE["iter_mask"](mask)
            )
            maxima = [eligible[index]["formal"] for index in MODULE["iter_mask"](mask)]
            family = MODULE["order_ideal"](4, maxima)
            _, collisions = MODULE["evaluate_family"](curve, factors, family)
            self.assertEqual(graph_feasible, not collisions)

    def test_v18_legacy_direct_row_api_is_disabled_before_math(self) -> None:
        row = copy.deepcopy(self.transient_legacy_control_rows[4])
        bad_digest = copy.deepcopy(row)
        bad_digest["row_sha256"] = "0" * 64
        huge_prime = copy.deepcopy(row)
        huge_prime["curve"]["p"] = 10**1000 + 7

        verifier_globals = VERIFIER["verify_row"].__globals__
        guarded = ("Curve", "reconstruct_graph", "independent_primary_optimum")
        originals = {name: verifier_globals[name] for name in guarded}
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"legacy rejection must precede {name}")

            return reject

        for name in guarded:
            verifier_globals[name] = forbidden(name)
        try:
            for candidate in (row, bad_digest, huge_prime):
                report = VERIFIER["verify_row"](candidate, 100000)
                self.assertFalse(report["valid"])
                self.assertIn("legacy direct-row API is disabled", report["errors"][-1])
                self.assertEqual(report["primary_nodes"], 0)
            density_report = VERIFIER["verify_density_row"](
                self.frozen_density_row, 100000, "frozen_fixture"
            )
            self.assertFalse(density_report["valid"])
            self.assertIn(
                "direct density-row API is non-evidence and disabled",
                density_report["errors"][-1],
            )
            self.assertIsNone(density_report["resource_reservation"])
            self.assertEqual(density_report["primary_nodes"], 0)
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_density_objective_matches_exhaustive_caps(self) -> None:
        point_count = 13
        pair_outputs = [
            [((left + 2) * (right + 3) + left + right) % point_count for right in range(6)]
            for left in range(6)
        ]
        for left in range(6):
            for right in range(6):
                pair_outputs[right][left] = pair_outputs[left][right]
        conflicts = [0] * 6
        for left, right in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5)):
            conflicts[left] |= 1 << right
            conflicts[right] |= 1 << left
        weights = [2, 2, 3, 3, 4, 4]

        def metrics(mask: int) -> dict[str, object]:
            selected = list(MODULE["iter_mask"](mask))
            return {
                "constrained_count": 1 + sum(weights[index] for index in selected),
                "public_edge_count": sum(index + 1 for index in selected),
                "witness_list": selected,
            }

        for cap in (1, 5, 9, 17):
            with self.subTest(cap=cap):
                best_key = None
                best_witness = None
                for mask in range(1 << len(conflicts)):
                    if any(conflicts[index] & mask for index in MODULE["iter_mask"](mask)):
                        continue
                    row_metrics = metrics(mask)
                    if row_metrics["constrained_count"] > cap:
                        continue
                    support = MODULE["support_mask_for_selection"](
                        mask, pair_outputs
                    ).bit_count()
                    key = (
                        support,
                        -row_metrics["constrained_count"],
                        -row_metrics["public_edge_count"],
                        mask.bit_count(),
                    )
                    witness = tuple(row_metrics["witness_list"])
                    if best_key is None or key > best_key or (
                        key == best_key and witness < best_witness
                    ):
                        best_key = key
                        best_witness = witness
                observed = MODULE["optimize_coverage_graph"](
                    pair_outputs,
                    point_count,
                    conflicts,
                    100000,
                    metrics,
                    max_constrained=cap,
                    objective_mode="density",
                )
                self.assertTrue(observed["full_objective_exact"])
                self.assertEqual(
                    (
                        observed["retained_support_lower_bound"],
                        -observed["constrained_count"],
                        -observed["public_edge_count"],
                        observed["selected_count"],
                    ),
                    best_key,
                )
                self.assertEqual(tuple(observed["witness_list"]), best_witness)
                self.assertLessEqual(observed["constrained_count"], cap)

    def test_frozen_full_objective_matches_third_exhaustive_oracle(self) -> None:
        row = self.frozen_density_row
        curve = VERIFIER["verify_curve_provenance"](row["curve"])
        group = curve.points()
        factors = VERIFIER["verify_factor_base"](curve, group, row)
        eligible, conflicts, *_ = VERIFIER["reconstruct_graph"](curve, factors)

        candidates = []
        for mask in range(1 << len(conflicts)):
            selected_indices = list(VERIFIER["bits"](mask))
            if any(conflicts[index] & mask for index in selected_indices):
                continue
            maxima = [eligible[index]["formal"] for index in selected_indices]
            constrained, edge_count, _, _, _, _ = VERIFIER["retained_model"](
                curve, factors, maxima
            )
            selected_points = [eligible[index]["point"] for index in selected_indices]
            support = len(VERIFIER["support_counter"](curve, selected_points))
            witness = tuple(tuple(formal) for formal in sorted(maxima))
            objective = (
                support,
                -constrained,
                -edge_count,
                len(selected_indices),
            )
            candidates.append(
                (
                    constrained,
                    objective,
                    witness,
                    selected_indices,
                    edge_count,
                )
            )

        for public, private in zip(
            row["public_model"]["density_frontier"],
            row["private_audit"]["density_frontier"],
        ):
            cap = public["constrained_cap"]
            feasible = [candidate for candidate in candidates if candidate[0] <= cap]
            best_objective = max(candidate[1] for candidate in feasible)
            best_witness = min(
                candidate[2]
                for candidate in feasible
                if candidate[1] == best_objective
            )
            winner = next(
                candidate
                for candidate in feasible
                if candidate[1] == best_objective and candidate[2] == best_witness
            )
            optimizer = private["optimizer"]
            self.assertEqual(
                (
                    optimizer["retained_support_lower_bound"],
                    -optimizer["constrained_count"],
                    -optimizer["public_edge_count"],
                    optimizer["selected_count"],
                ),
                best_objective,
            )
            self.assertEqual(
                tuple(tuple(formal) for formal in optimizer["witness_list"]),
                best_witness,
            )
            self.assertEqual(optimizer["selected_indices"], winner[3])
            self.assertEqual(public["constrained_count"], winner[0])
            self.assertEqual(public["public_edge_count"], winner[4])

    def test_frozen_b4_matches_full_standalone_transcript(self) -> None:
        row = self.frozen_density_row
        oracle = standalone_frozen_b4_oracle()
        expected_factors = [
            tuple(point) for point in row["public_model"]["factor_base"]["points"]
        ]
        self.assertEqual(oracle["factors"], expected_factors)
        verifier_curve = VERIFIER["Curve"](19, 2, 9)
        reconstructed = VERIFIER["reconstruct_graph"](
            verifier_curve, expected_factors
        )
        self.assertEqual(oracle["candidates"], reconstructed[-1])
        self.assertEqual(oracle["eligible"], reconstructed[0])
        self.assertEqual(oracle["factor_base"], row["public_model"]["factor_base"])
        compiler = row["public_model"]["representative_compiler"]
        self.assertEqual(oracle["representative_compiler"], compiler)
        self.assertEqual(
            oracle["caps"], row["public_model"]["constrained_budget_caps"]
        )
        graph = row["private_audit"]["graph"]
        self.assertEqual(oracle["candidate_count"], graph["candidate_count"])
        self.assertEqual(oracle["eligible_count"], graph["eligible_candidate_count"])
        self.assertEqual(oracle["conflict_count"], graph["conflict_count"])
        self.assertEqual(
            {
                "candidate_count": oracle["candidate_count"],
                "eligible_candidate_count": oracle["eligible_count"],
                "individually_rejected_count": len(oracle["individually_rejected"]),
                "conflict_count": oracle["conflict_count"],
                **oracle["graph_metrics"],
            },
            graph,
        )
        self.assertEqual(
            oracle["eligible_universe_indices"],
            row["private_audit"]["eligible_universe_indices"],
        )
        self.assertEqual(
            oracle["individually_rejected"],
            row["private_audit"]["individually_rejected"],
        )
        self.assertEqual(oracle["conflicts"], row["private_audit"]["conflicts"])
        for public, private in zip(
            row["public_model"]["density_frontier"],
            row["private_audit"]["density_frontier"],
        ):
            winner = oracle["winners"][public["constrained_cap"]]
            optimizer = private["optimizer"]
            self.assertEqual(
                winner["objective"],
                (
                    optimizer["retained_support_lower_bound"],
                    -optimizer["constrained_count"],
                    -optimizer["public_edge_count"],
                    optimizer["selected_count"],
                ),
            )
            self.assertEqual(
                winner["witness"],
                tuple(tuple(formal) for formal in optimizer["witness_list"]),
            )
            self.assertEqual(winner["selected_indices"], optimizer["selected_indices"])
            self.assertEqual(winner["selected_mask_hex"], optimizer["selected_mask_hex"])
            self.assertEqual(winner["constrained_count"], public["constrained_count"])
            self.assertEqual(
                winner["formal_family_count"], public["formal_family_count"]
            )
            self.assertEqual(
                winner["formal_degree_histogram"], public["formal_degree_histogram"]
            )
            self.assertEqual(winner["delta"], public["delta"])
            self.assertEqual(winner["axioms"], public["axioms"])
            self.assertEqual(winner["public_edge_count"], public["public_edge_count"])
            self.assertEqual(winner["public_edges"], public["public_edges"])
            self.assertEqual(
                winner["public_edges_sha256"], public["public_edges_sha256"]
            )
            self.assertEqual(winner["source_table"], public["source_table"])
            self.assertEqual(
                winner["source_table_sha256"], public["source_table_sha256"]
            )
            self.assertEqual(
                winner["constrained_labels"],
                [entry["label"] for entry in public["source_table"]],
            )

    def test_corrected_energy_matches_ordered_and_multiset_recounts(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        factors, _ = MODULE["factor_base"](
            curve, points, record, 4, "least_x_interval", None, ops
        )
        observed = MODULE["degree_expansion"](curve, factors, (2,))["2"]
        formal_counts = {}
        for formal in itertools.combinations_with_replacement(range(4), 2):
            point = MODULE["evaluate_formal"](curve, factors, formal)
            formal_counts[point] = formal_counts.get(point, 0) + 1
        ordered_counts = {}
        for ordered in itertools.product(range(4), repeat=2):
            point = MODULE["evaluate_formal"](curve, factors, ordered)
            ordered_counts[point] = ordered_counts.get(point, 0) + 1
        self.assertEqual(observed["formal_multiset_witness_count"], 10)
        self.assertEqual(observed["ordered_tuple_witness_count"], 16)
        self.assertEqual(
            observed["formal_multiset_collision_energy"],
            sum(value * value for value in formal_counts.values()),
        )
        self.assertEqual(
            observed["ordered_tuple_additive_energy"],
            sum(value * value for value in ordered_counts.values()),
        )
        all_degrees = MODULE["degree_expansion"](curve, factors)
        self.assertEqual(
            all_degrees,
            VERIFIER["expansion_metrics"](
                VERIFIER["Curve"](curve.p, curve.a, curve.b),
                factors,
            ),
        )
        for degree in (1, 2, 4, 8):
            with self.subTest(degree=degree):
                metrics = all_degrees[str(degree)]
                self.assertEqual(
                    metrics["formal_multiset_witness_count"],
                    math.comb(len(factors) + degree - 1, degree),
                )
                self.assertEqual(
                    metrics["ordered_tuple_witness_count"], len(factors) ** degree
                )

    def test_density_gap_frontier_replays_from_root(self) -> None:
        point_count = 19
        candidate_count = 8
        pair_outputs = [
            [((left + 5) * (right + 7) + right) % point_count for right in range(candidate_count)]
            for left in range(candidate_count)
        ]
        for left in range(candidate_count):
            for right in range(candidate_count):
                pair_outputs[right][left] = pair_outputs[left][right]
        conflicts = [0] * candidate_count
        for left, right in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)):
            conflicts[left] |= 1 << right
            conflicts[right] |= 1 << left

        def metrics(mask: int) -> dict[str, object]:
            selected = list(MODULE["iter_mask"](mask))
            return {
                "constrained_count": 1 + 2 * len(selected),
                "public_edge_count": sum(selected),
                "witness_list": selected,
            }

        producer = MODULE["optimize_coverage_graph"](
            pair_outputs,
            point_count,
            conflicts,
            0,
            metrics,
            max_constrained=9,
            objective_mode="density",
        )
        replay = VERIFIER["replay_density_search"](
            pair_outputs, point_count, conflicts, 0, 9, metrics
        )
        self.assertTrue(producer["frontier_states"])
        for key in replay:
            if key == "metric_cache_entries":
                continue
            self.assertEqual(replay[key], producer[key], key)
        self.assertEqual(
            VERIFIER["verify_frontier_certificate"](
                pair_outputs, point_count, conflicts, producer
            ),
            [],
        )

    def test_frozen_density_frontier_is_exact_and_within_every_cap(self) -> None:
        row = self.frozen_density_row
        self.assertEqual(row["public_model"]["constrained_budget_caps"], [5, 11, 17, 23])
        for public, private in zip(
            row["public_model"]["density_frontier"],
            row["private_audit"]["density_frontier"],
        ):
            self.assertEqual(public["constrained_cap"], private["constrained_cap"])
            self.assertLessEqual(public["constrained_count"], public["constrained_cap"])
            self.assertTrue(private["optimizer"]["primary_exact"])
            self.assertTrue(private["optimizer"]["full_objective_exact"])
            self.assertEqual(private["optimizer"]["frontier_states"], [])
            cache_limit = (
                private["optimizer"]["node_cap"]
                + row["private_audit"]["graph"]["eligible_candidate_count"] ** 2
                + 64
            )
            self.assertLessEqual(
                private["optimizer"]["metric_cache_entries"], cache_limit
            )
            self.assertEqual(
                private["structural_work"]["optimizer_metric_cache_entries"],
                private["optimizer"]["metric_cache_entries"],
            )
            self.assertEqual(
                private["structural_work"]["full_model_cache_entries"],
                private["optimizer"]["metric_cache_entries"],
            )
            self.assertEqual(
                private["retention"]["eight_fold_support"],
                row["private_audit"]["expansion"]["8"]["support"],
            )
        verification = verify_density_row_for_test(
            row, 100000, "frozen_fixture"
        )
        self.assertTrue(verification["valid"], verification["errors"])
        self.assertEqual(len(verification["cap_reports"]), 4)
        self.assertEqual(
            verification["actual_work"]["replay_nodes"],
            verification["replay_nodes"],
        )
        self.assertEqual(
            verification["actual_work"]["independent_primary_nodes"],
            verification["primary_nodes"],
        )
        self.assertGreater(
            verification["actual_work"]["primary_support_cache_entries"], 0
        )
        self.assertNotIn("operation_counts", row)
        self.assertEqual(
            row["structural_work"]["degree_multiset_evaluations"],
            sum(
                row["private_audit"]["expansion"][str(degree)][
                    "formal_multiset_witness_count"
                ]
                for degree in (1, 2, 4, 8)
            ),
        )

        mutated = copy.deepcopy(row)
        mutated["accounting"]["public_model_json_bytes"] += 1
        resign_density_row(mutated)
        mutation_report = verify_density_row_for_test(
            mutated, 100000, "frozen_fixture"
        )
        self.assertFalse(mutation_report["valid"])
        self.assertTrue(
            any(
                "cost-accounting byte receipt mismatch" in error
                for error in mutation_report["errors"]
            )
        )

        mutated = copy.deepcopy(row)
        mutated["structural_work"]["pair_output_cells"] += 1
        refresh_density_accounting(mutated)
        mutation_report = verify_density_row_for_test(
            mutated, 100000, "frozen_fixture"
        )
        self.assertFalse(mutation_report["valid"])
        self.assertIn("row structural-work receipt mismatch", mutation_report["errors"])

    def test_closed_schema_rejects_scalar_material_and_nested_graph_extras(self) -> None:
        scalar = copy.deepcopy(self.frozen_density_row)
        scalar["scalar_table"] = []
        refresh_density_accounting(scalar)
        report = verify_density_row_for_test(
            scalar, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("more keys than the V18 source schema" in error for error in report["errors"])
        )

        nested = copy.deepcopy(self.frozen_density_row)
        nested["private_audit"]["individually_rejected"][0]["note"] = "extra"
        refresh_density_accounting(nested)
        report = verify_density_row_for_test(
            nested, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "individual rejection[0] has more keys than the V18 source schema"
                in error
                for error in report["errors"]
            )
        )

    def test_semantic_mutations_are_rejected_after_receipts_are_refreshed(self) -> None:
        representative = copy.deepcopy(self.frozen_density_row)
        compiler = representative["public_model"]["representative_compiler"]
        compiler["representatives"][0]["formal"] = [3, 3]
        compiler["representatives_sha256"] = VERIFIER["digest"](
            compiler["representatives"]
        )
        refresh_density_accounting(representative)
        report = verify_density_row_for_test(
            representative, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertIn("representative compiler mismatch", report["errors"])

        objective = copy.deepcopy(self.frozen_density_row)
        objective["private_audit"]["density_frontier"][0]["optimizer"][
            "objective_order"
        ][0:2] = ["constrained_count:min", "retained_support:max"]
        refresh_density_accounting(objective)
        report = verify_density_row_for_test(
            objective, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("optimizer objective-order mismatch" in error for error in report["errors"])
        )

        source = copy.deepcopy(self.frozen_density_row)
        source_cap = source["public_model"]["density_frontier"][0]
        source_cap["source_table"][0]["formal"] = [0]
        source_cap["source_table_sha256"] = VERIFIER["digest"](
            source_cap["source_table"]
        )
        refresh_density_accounting(source)
        report = verify_density_row_for_test(
            source, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("public source table/digest mismatch" in error for error in report["errors"])
        )

        unresolved = copy.deepcopy(self.frozen_density_row)
        optimizer = unresolved["private_audit"]["density_frontier"][0]["optimizer"]
        optimizer["primary_exact"] = False
        optimizer["retained_support_upper_bound"] += 1
        optimizer["absolute_gap"] = 1
        refresh_density_accounting(unresolved)
        report = verify_density_row_for_test(
            unresolved, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "optimizer exactness" in error
                for error in report["errors"]
            )
        )

    def test_v18_exact_types_reject_json_equality_aliases(self) -> None:
        mutations = (
            (
                "zero_to_false",
                ("private_audit", "density_frontier", 0, "optimizer", "absolute_gap"),
                False,
            ),
            (
                "zero_to_negative_float_zero",
                (
                    "private_audit",
                    "density_frontier",
                    0,
                    "optimizer",
                    "remaining_frontier_nodes",
                ),
                -0.0,
            ),
            (
                "integer_count_to_float",
                ("private_audit", "graph", "candidate_count"),
                float(self.frozen_density_row["private_audit"]["graph"]["candidate_count"]),
            ),
            (
                "boolean_to_integer",
                ("public_model", "density_frontier", 0, "axioms", "identity"),
                1,
            ),
            (
                "ratio_integer_to_float",
                ("public_model", "density_frontier", 0, "delta", "numerator"),
                float(
                    self.frozen_density_row["public_model"]["density_frontier"][0][
                        "delta"
                    ]["numerator"]
                ),
            ),
            (
                "node_cap_to_float",
                ("private_audit", "density_frontier", 0, "optimizer", "node_cap"),
                100000.0,
            ),
            ("wall_time_to_integer", ("wall_time_seconds",), 0),
            (
                "mask_to_integer",
                (
                    "private_audit",
                    "density_frontier",
                    0,
                    "optimizer",
                    "selected_mask_hex",
                ),
                0,
            ),
        )
        for label, path, replacement in mutations:
            with self.subTest(label=label):
                mutated = copy.deepcopy(self.frozen_density_row)
                target = mutated
                for component in path[:-1]:
                    target = target[component]
                target[path[-1]] = replacement
                refresh_density_accounting(mutated)
                report = verify_density_row_for_test(
                    mutated, 100000, "frozen_fixture"
                )
                self.assertFalse(report["valid"])
                self.assertTrue(
                    any("exact type mismatch" in error for error in report["errors"]),
                    report["errors"],
                )

        receipt = copy.deepcopy(self.frozen_density_row)
        byte_receipt = receipt["accounting"]["nested_per_cap_json_bytes"][0]
        byte_receipt["public_embedding_json_bytes"] = float(
            byte_receipt["public_embedding_json_bytes"]
        )
        resign_density_row(receipt)
        report = verify_density_row_for_test(
            receipt, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("exact type mismatch" in error for error in report["errors"]),
            report["errors"],
        )

    def test_v18_type_checker_rejects_every_frozen_scalar_type_substitution(self) -> None:
        scalar_paths = []

        def visit(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    visit(child, path + (key,))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, path + (index,))
            else:
                scalar_paths.append(path)

        visit(self.frozen_density_row)
        checked = 0
        for path in scalar_paths:
            mutated = copy.deepcopy(self.frozen_density_row)
            target = mutated
            for component in path[:-1]:
                target = target[component]
            original = target[path[-1]]
            if type(original) is bool:
                replacement = int(original)
            elif type(original) is int:
                replacement = float(original)
            elif type(original) is float:
                replacement = int(original)
            elif type(original) is str:
                replacement = 0
            elif original is None:
                replacement = False
            else:
                continue
            target[path[-1]] = replacement
            errors = VERIFIER["v18_row_type_errors"](mutated)
            self.assertTrue(errors, path)
            checked += 1
        self.assertGreater(checked, 1000)

    def test_v18_preflight_returns_invalid_receipts_for_red_team_crash_cases(self) -> None:
        mutations = []

        truncated_caps = copy.deepcopy(self.frozen_density_row)
        truncated_caps["public_model"]["constrained_budget_caps"].pop()
        refresh_density_accounting(truncated_caps)
        mutations.append(("truncated_caps", truncated_caps, "must contain exactly 4"))

        invalid_formal = copy.deepcopy(self.frozen_density_row)
        invalid_formal["public_model"]["density_frontier"][0]["selected_maxima"] = [
            [999]
        ]
        refresh_density_accounting(invalid_formal)
        mutations.append(("invalid_formal", invalid_formal, "must contain exactly 4"))

        duplicate_formal = copy.deepcopy(self.frozen_density_row)
        duplicate_cell = next(
            cell
            for cell in duplicate_formal["public_model"]["density_frontier"]
            if cell["selected_maxima"]
        )
        duplicate_cell["selected_maxima"].append(
            copy.deepcopy(duplicate_cell["selected_maxima"][0])
        )
        refresh_density_accounting(duplicate_formal)
        mutations.append(("duplicate_formal", duplicate_formal, "not unique"))

        negative_cap = copy.deepcopy(self.frozen_density_row)
        negative_cap["public_model"]["constrained_budget_caps"][0] = -1
        negative_cap["public_model"]["density_frontier"][0]["constrained_cap"] = -1
        negative_cap["private_audit"]["density_frontier"][0]["constrained_cap"] = -1
        negative_cap["private_audit"]["density_frontier"][0]["optimizer"][
            "max_constrained"
        ] = -1
        refresh_density_accounting(negative_cap)
        mutations.append(("negative_cap", negative_cap, "outside 1..q"))

        for label, mutated, expected in mutations:
            with self.subTest(label=label):
                first = verify_density_row_for_test(
                    mutated, 100000, "frozen_fixture"
                )
                second = verify_density_row_for_test(
                    mutated, 100000, "frozen_fixture"
                )
                self.assertFalse(first["valid"])
                self.assertEqual(first, second)
                self.assertEqual(first["primary_nodes"], 0)
                self.assertTrue(
                    any(expected in error for error in first["errors"]), first["errors"]
                )
                self.assertFalse(
                    any("verifier failure" in error for error in first["errors"]),
                    first["errors"],
                )
                document = MODULE["build_document"](
                    [self.frozen_density_row],
                    "frozen_fixture",
                    MODULE["frozen_parameters"](100000),
                )
                document["rows"] = [mutated]
                resign_document(document)
                document_errors, document_reports = verify_v18_document_for_test(
                    document, 100000
                )
                self.assertTrue(document_errors)
                self.assertEqual(document_reports, [])
                self.assertTrue(
                    any(expected in error for error in document_errors),
                    document_errors,
                )

    def test_v18_verifier_entrypoints_are_total_with_explicit_ceilings(self) -> None:
        missing_scope = verify_density_row_for_test(
            self.frozen_density_row, 100000
        )
        self.assertFalse(missing_scope["valid"])
        self.assertIn(
            "density row scope must be explicitly registered",
            missing_scope["errors"],
        )

        bad_digest = copy.deepcopy(self.frozen_density_row)
        bad_digest["row_sha256"] = "0" * 64
        verifier_globals = _RAW_VERIFY_DENSITY_ROW_FOR_TESTS.__globals__
        original_curve_verifier = verifier_globals["verify_curve_provenance"]
        original_frozen_curve = verifier_globals["frozen_curve_record"]
        original_registered_curve = verifier_globals["registered_curve_bundle"]
        curve_calls = []

        def forbidden_curve_verifier(_):
            curve_calls.append("provenance")
            raise AssertionError("digest failure must precede curve work")

        def forbidden_frozen_curve():
            curve_calls.append("frozen")
            raise AssertionError("digest failure must precede frozen curve work")

        def forbidden_registered_curve(*_args):
            curve_calls.append("registered")
            raise AssertionError("digest failure must precede registered curve work")

        verifier_globals["verify_curve_provenance"] = forbidden_curve_verifier
        verifier_globals["frozen_curve_record"] = forbidden_frozen_curve
        verifier_globals["registered_curve_bundle"] = forbidden_registered_curve
        try:
            digest_report = verify_density_row_for_test(
                bad_digest, 100000, "frozen_fixture"
            )
        finally:
            verifier_globals["verify_curve_provenance"] = original_curve_verifier
            verifier_globals["frozen_curve_record"] = original_frozen_curve
            verifier_globals["registered_curve_bundle"] = original_registered_curve
        self.assertFalse(digest_report["valid"])
        self.assertTrue(
            any("row digest mismatch" in error for error in digest_report["errors"])
        )
        self.assertEqual(curve_calls, [])

        for maximum_nodes in (False, -1, VERIFIER["MAXIMUM_PRIMARY_NODES"] + 1):
            with self.subTest(maximum_nodes=maximum_nodes):
                row_report = verify_density_row_for_test(
                    self.frozen_density_row, maximum_nodes, "frozen_fixture"
                )
                self.assertFalse(row_report["valid"])
                document = MODULE["build_document"](
                    [self.frozen_density_row],
                    "frozen_fixture",
                    MODULE["frozen_parameters"](100000),
                )
                errors, reports = verify_v18_document_for_test(
                    document, maximum_nodes
                )
                self.assertTrue(errors)
                self.assertEqual(reports, [])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / "malformed.json"
            malformed.write_text('{"schema":', encoding="ascii")
            report = VERIFIER["verify_document"](malformed, 100000)
            self.assertFalse(report["valid"])
            self.assertTrue(
                any("strict JSON parse failure" in error for error in report["errors"])
            )

            non_object = root / "non-object.json"
            non_object.write_text("[]", encoding="ascii")
            report = VERIFIER["verify_document"](non_object, 100000)
            self.assertFalse(report["valid"])
            self.assertIn("input document is not an object", report["errors"])

            duplicate = root / "duplicate.json"
            duplicate.write_text('{"schema":"x","schema":"y"}', encoding="ascii")
            report = VERIFIER["verify_document"](duplicate, 100000)
            self.assertFalse(report["valid"])
            self.assertTrue(any("duplicate key" in error for error in report["errors"]))

    def test_v18_overlong_reflected_path_returns_bounded_invalid_report(self) -> None:
        path = Path("x" * (VERIFIER["MAXIMUM_VERIFICATION_REPORT_BYTES"] + 1))
        report = VERIFIER["verify_document"](path, False)
        self.assertFalse(report["valid"])
        self.assertTrue(report["input_path"].startswith("<input path omitted:"))
        self.assertLessEqual(
            len(VERIFIER["stable_bytes"](report)),
            VERIFIER["MAXIMUM_VERIFICATION_REPORT_BYTES"],
        )

    def test_v18_snapshot_hash_and_parse_are_bound_to_the_same_bytes(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        original_bytes = VERIFIER["stable_bytes"](document)
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_snapshot = verifier_globals["read_input_snapshot"]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changing.json"
            path.write_bytes(original_bytes)

            def snapshot_then_change(snapshot_path):
                raw, receipt = original_snapshot(snapshot_path)
                snapshot_path.write_bytes(b'{"schema":"changed-after-snapshot"}')
                return raw, receipt

            verifier_globals["read_input_snapshot"] = snapshot_then_change
            try:
                report = VERIFIER["verify_document"](path, 100000)
            finally:
                verifier_globals["read_input_snapshot"] = original_snapshot

            self.assertTrue(report["valid"], report["errors"])
            self.assertEqual(
                report["input_file_sha256"], hashlib.sha256(original_bytes).hexdigest()
            )
            self.assertNotEqual(
                report["input_file_sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
            )
            self.assertEqual(report["input_document_sha256"], document["document_sha256"])

    def test_v18_source_hash_is_diagnostic_and_not_reopened_for_reporting(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_file_digest = verifier_globals["file_digest"]

        def forbidden_file_digest(_path):
            raise AssertionError("reporting must not reopen the verifier source")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            verifier_globals["file_digest"] = forbidden_file_digest
            try:
                report = VERIFIER["verify_document"](path, 100000)
            finally:
                verifier_globals["file_digest"] = original_file_digest
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(
            report["verifier_source_sha256"],
            VERIFIER["VERIFIER_SOURCE_DIAGNOSTIC_SHA256"],
        )
        self.assertFalse(report["verifier_source_attested"])
        self.assertIn("not executed-code attestation", report["verifier_source_hash_scope"])
        self.assertIn("parent path components", report["input_symlink_policy"])

    def test_v18_diagnostics_are_count_and_byte_bounded(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        for index in range(1000):
            document[f"secret_{index:04d}"] = "x" * 4096
        resign_document(document)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "amplified.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            report = VERIFIER["verify_document"](path, 100000)
        observed = report["diagnostic_observed"]
        limits = report["diagnostic_limits"]
        self.assertFalse(report["valid"])
        self.assertLessEqual(observed["count"], limits["maximum_count"])
        self.assertLessEqual(observed["bytes"], limits["maximum_bytes"])
        self.assertFalse(observed["truncated"])
        self.assertTrue(
            all(
                len(error.encode("ascii")) <= limits["maximum_item_bytes"]
                for error in report["errors"]
            )
        )
        report_bytes = VERIFIER["stable_bytes"](report)
        self.assertLessEqual(
            len(report_bytes), VERIFIER["MAXIMUM_VERIFICATION_REPORT_BYTES"]
        )
        self.assertNotIn(b"secret_", report_bytes)

    def test_v18_reflected_document_digest_is_sanitized_before_reporting(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        document["document_sha256"] = {"secret": "not-a-digest"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid-digest.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            report = VERIFIER["verify_document"](path, 100000)
        self.assertFalse(report["valid"])
        self.assertIsNone(report["input_document_sha256"])
        self.assertEqual(
            report["phases"][-1],
            {"name": "source_collection_bounds", "status": "failed"},
        )
        self.assertNotIn(b"secret", VERIFIER["stable_bytes"](report))

    def test_v18_serialized_report_ceiling_covers_integrity_fields(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_limit = verifier_globals["MAXIMUM_VERIFICATION_REPORT_BYTES"]
        verifier_globals["MAXIMUM_VERIFICATION_REPORT_BYTES"] = 5050
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bounded-report.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["MAXIMUM_VERIFICATION_REPORT_BYTES"] = original_limit

        self.assertFalse(report["valid"])
        self.assertEqual(report["rows"], [])
        self.assertLessEqual(len(VERIFIER["stable_bytes"](report)), 5050)
        signed_payload = dict(report)
        supplied_hash = signed_payload.pop("verification_sha256")
        self.assertEqual(supplied_hash, VERIFIER["digest"](signed_payload))
        pre_integrity_payload = dict(signed_payload)
        supplied_size = pre_integrity_payload.pop(
            "serialized_report_bytes_before_size_field_and_hash"
        )
        self.assertEqual(supplied_size, len(VERIFIER["stable_bytes"](pre_integrity_payload)))

    def test_v18_source_collection_bounds_precede_generic_traversal(self) -> None:
        baseline = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        mutations = []

        polynomial = copy.deepcopy(baseline)
        polynomial["rows"][0]["public_model"]["factor_base"][
            "root_polynomial_coefficients_ascending_mod_p"
        ].append(0)
        mutations.append((polynomial, "factor root polynomial must contain exactly 3"))

        maps = copy.deepcopy(baseline)
        maps["rows"][0]["family"] = "two_mobius_union"
        maps["rows"][0]["public_model"]["factor_base"]["parameters"] = {
            "maps": [{}, {}, {}],
            "alternating_positions": [0, 1],
        }
        mutations.append((maps, "two-Mobius maps must contain exactly 2"))

        alternating = copy.deepcopy(baseline)
        alternating["rows"][0]["family"] = "two_mobius_union"
        alternating["rows"][0]["public_model"]["factor_base"]["parameters"] = {
            "maps": [{}, {}],
            "alternating_positions": [0, 1, 2],
        }
        mutations.append(
            (
                alternating,
                "two-Mobius alternating positions must contain exactly 2",
            )
        )

        reasons = copy.deepcopy(baseline)
        reasons["rows"][0]["curve"]["rejected_draws"] = [
            {
                "draw": 0,
                "p": 5,
                "a": 0,
                "b": 1,
                "reasons": list(VERIFIER["REJECTION_REASON_ORDER"]) + ["extra"],
            }
        ]
        mutations.append(
            (reasons, "curve rejection[0] reasons exceeds its source-derived length bound")
        )

        accounting = copy.deepcopy(baseline)
        accounting["rows"][0]["accounting"]["nested_per_cap_json_bytes"].append(
            copy.deepcopy(
                accounting["rows"][0]["accounting"]["nested_per_cap_json_bytes"][0]
            )
        )
        mutations.append(
            (accounting, "nested per-cap byte receipts must contain exactly 4")
        )

        nested_dictionary = copy.deepcopy(baseline)
        nested_dictionary["rows"][0]["public_model"]["factor_base"].update(
            {f"extra_{index}": index for index in range(1000)}
        )
        mutations.append(
            (
                nested_dictionary,
                "factor-base record has more keys than the V18 source schema",
            )
        )

        invalid_B = copy.deepcopy(baseline)
        invalid_B["rows"][0]["B"] = 3
        invalid_B["rows"][0]["private_audit"]["expansion"] = {
            "nested": [[0] * 1000]
        }
        mutations.append((invalid_B, "row.B is outside the V18 source range"))

        canonical_gate = copy.deepcopy(baseline)
        canonical_gate["scope"] = "canonical"
        canonical_gate["canonical"] = True
        canonical_gate["parameters"] = VERIFIER["expected_canonical_parameters"]()
        canonical_gate["family_gate"] = VERIFIER["independent_family_gate"](
            synthetic_gate_rows()
        )
        canonical_gate["family_gate"]["families"][0]["matched_null_cap_tests"][0][
            "strata"
        ].append(
            copy.deepcopy(
                canonical_gate["family_gate"]["families"][0][
                    "matched_null_cap_tests"
                ][0]["strata"][0]
            )
        )
        mutations.append(
            (
                canonical_gate,
                "family gate[0].matched_null_cap_tests[0].strata must contain exactly 4",
            )
        )

        verifier_globals = VERIFIER["verify_document"].__globals__
        originals = {
            name: verifier_globals[name]
            for name in ("bounded_json_errors", "_verify_v18_document_value_unchecked")
        }
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"collection rejection must precede {name}")

            return reject

        for name in originals:
            verifier_globals[name] = forbidden(name)
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bounded.json"
                for document, expected in mutations:
                    with self.subTest(expected=expected):
                        path.write_bytes(VERIFIER["stable_bytes"](document))
                        report = VERIFIER["verify_document"](path, 100000)
                        self.assertFalse(report["valid"])
                        self.assertTrue(
                            any(expected in error for error in report["errors"]),
                            report["errors"],
                        )
                        self.assertEqual(
                            report["phases"][-1],
                            {"name": "source_collection_bounds", "status": "failed"},
                        )
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_v18_rejects_nonregular_and_symlink_inputs_before_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regular = root / "regular.json"
            regular.write_text("{}", encoding="ascii")
            symlink = root / "link.json"
            symlink.symlink_to(regular)
            fifo = root / "input.fifo"
            os.mkfifo(fifo)
            for path in (root, symlink, fifo):
                with self.subTest(path=path.name):
                    report = VERIFIER["verify_document"](path, 100000)
                    self.assertFalse(report["valid"])
                    self.assertEqual(
                        report["phases"],
                        [
                            {"name": "verifier_budget_preflight", "status": "passed"},
                            {"name": "single_regular_file_snapshot", "status": "failed"},
                        ],
                    )
                    self.assertEqual(
                        report["independent_checks"], ["verifier_budget_preflight"]
                    )

            oversized = root / "oversized.json"
            oversized.touch()
            os.truncate(oversized, VERIFIER["MAXIMUM_INPUT_BYTES"] + 1)
            snapshot_globals = VERIFIER["read_input_snapshot"].__globals__
            original_readv = snapshot_globals["os"].readv
            read_calls = 0

            def forbidden_readv(*_args, **_kwargs):
                nonlocal read_calls
                read_calls += 1
                raise AssertionError("oversized input must be rejected before reading")

            snapshot_globals["os"].readv = forbidden_readv
            try:
                with self.assertRaisesRegex(ValueError, "input byte ceiling exceeded"):
                    VERIFIER["read_input_snapshot"](oversized)
            finally:
                snapshot_globals["os"].readv = original_readv
            self.assertEqual(read_calls, 0)

            real_parent = root / "real-parent"
            real_parent.mkdir()
            parent_target = real_parent / "input.json"
            parent_target.write_text("{}", encoding="ascii")
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            raw, _ = VERIFIER["read_input_snapshot"](
                linked_parent / "input.json"
            )
            self.assertEqual(raw, b"{}")

    def test_v18_snapshot_uses_one_exact_buffer_at_the_size_boundary(self) -> None:
        snapshot_globals = VERIFIER["read_input_snapshot"].__globals__
        original_limit = snapshot_globals["MAXIMUM_INPUT_BYTES"]
        original_readv = snapshot_globals["os"].readv
        backing_ids = []
        read_calls = 0

        def observing_readv(descriptor, buffers):
            nonlocal read_calls
            read_calls += 1
            self.assertEqual(len(buffers), 1)
            backing_ids.append(id(buffers[0].obj))
            return original_readv(descriptor, buffers)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exact = root / "exact.bin"
            oversized = root / "oversized.bin"
            exact.write_bytes(b"x" * 4096)
            oversized.write_bytes(b"x" * 4097)
            snapshot_globals["MAXIMUM_INPUT_BYTES"] = 4096
            snapshot_globals["os"].readv = observing_readv
            try:
                raw, receipt = VERIFIER["read_input_snapshot"](exact)
                calls_after_exact = read_calls
                with self.assertRaisesRegex(ValueError, "input byte ceiling exceeded"):
                    VERIFIER["read_input_snapshot"](oversized)
            finally:
                snapshot_globals["os"].readv = original_readv
                snapshot_globals["MAXIMUM_INPUT_BYTES"] = original_limit

        self.assertIs(type(raw), bytearray)
        self.assertEqual(raw, b"x" * 4096)
        self.assertEqual(receipt, hashlib.sha256(raw).hexdigest())
        self.assertGreater(calls_after_exact, 0)
        self.assertEqual(read_calls, calls_after_exact)
        self.assertEqual(set(backing_ids), {id(raw)})

    def test_v18_snapshot_buffer_is_cleared_before_json_object_construction(self) -> None:
        raw = bytearray(b'{"value":1}')
        strict_globals = VERIFIER["strict_json_load"].__globals__
        original_loads = strict_globals["json"].loads
        observed = []

        def observing_loads(value, *args, **kwargs):
            observed.append((type(value), len(raw)))
            return original_loads(value, *args, **kwargs)

        strict_globals["json"].loads = observing_loads
        try:
            document = VERIFIER["strict_json_load"](raw, Path("memory.json"))
        finally:
            strict_globals["json"].loads = original_loads

        self.assertEqual(document, {"value": 1})
        self.assertEqual(observed, [(str, 0)])
        self.assertEqual(raw, bytearray())

    def test_v18_lexical_preflight_rejects_amplification_before_json_load(self) -> None:
        strict_globals = VERIFIER["strict_json_load"].__globals__
        original_loads = strict_globals["json"].loads
        original_limits = {
            name: strict_globals[name]
            for name in (
                "MAXIMUM_JSON_NODES",
                "MAXIMUM_JSON_DEPTH",
                "MAXIMUM_JSON_STRING_BYTES",
                "MAXIMUM_JSON_SCALAR_TOKEN_BYTES",
            )
        }
        load_calls = 0

        def forbidden_loads(*_args, **_kwargs):
            nonlocal load_calls
            load_calls += 1
            raise AssertionError("lexical rejection must precede JSON object construction")

        strict_globals["json"].loads = forbidden_loads
        try:
            cases = (
                ("MAXIMUM_JSON_NODES", 3, b"[0,0,0]", "token ceiling"),
                ("MAXIMUM_JSON_DEPTH", 1, b"[[[0]]]", "depth ceiling"),
                ("MAXIMUM_JSON_STRING_BYTES", 3, b'["abcd"]', "string-token ceiling"),
                ("MAXIMUM_JSON_SCALAR_TOKEN_BYTES", 3, b"[1234]", "scalar-token ceiling"),
            )
            for name, limit, payload, diagnostic in cases:
                with self.subTest(name=name):
                    strict_globals.update(original_limits)
                    strict_globals[name] = limit
                    with self.assertRaisesRegex(ValueError, diagnostic):
                        VERIFIER["strict_json_load"](
                            bytearray(payload), Path("amplified.json")
                        )
            strict_globals.update(original_limits)
            with self.assertRaisesRegex(ValueError, "whitespace is not admitted"):
                VERIFIER["strict_json_load"](
                    bytearray(b'{"value": 1}'), Path("spaced.json")
                )
            with self.assertRaisesRegex(ValueError, "non-ASCII byte"):
                VERIFIER["strict_json_load"](
                    bytearray(b'{"value":"\xff"}'), Path("non-ascii.json")
                )
        finally:
            strict_globals.update(original_limits)
            strict_globals["json"].loads = original_loads
        self.assertEqual(load_calls, 0)

    def test_v18_registered_preflight_blocks_huge_bits_and_row_amplification(self) -> None:
        mutated = copy.deepcopy(self.frozen_density_row)
        mutated["curve"]["bits"] = 40
        refresh_density_accounting(mutated)

        verifier_globals = _RAW_VERIFY_DENSITY_ROW_FOR_TESTS.__globals__
        original_curve_verifier = verifier_globals["verify_curve_provenance"]
        curve_calls = 0

        def forbidden_curve_verifier(_):
            nonlocal curve_calls
            curve_calls += 1
            raise AssertionError("semantic curve verification must not run")

        verifier_globals["verify_curve_provenance"] = forbidden_curve_verifier
        try:
            row_report = verify_density_row_for_test(
                mutated, 100000, "frozen_fixture"
            )
        finally:
            verifier_globals["verify_curve_provenance"] = original_curve_verifier
        self.assertFalse(row_report["valid"])
        self.assertEqual(curve_calls, 0)
        self.assertEqual(row_report["primary_nodes"], 0)
        self.assertTrue(
            any("registered fixture" in error for error in row_report["errors"])
        )

        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        document["rows"] = [mutated]
        resign_document(document)
        document_globals = _RAW_VERIFY_V18_DOCUMENT_FOR_TESTS.__globals__
        original_row_verifier = document_globals["_verify_density_row_unchecked"]
        row_calls = 0

        def forbidden_row_verifier(*_args, **_kwargs):
            nonlocal row_calls
            row_calls += 1
            raise AssertionError("row semantics must not run")

        document_globals["_verify_density_row_unchecked"] = forbidden_row_verifier
        try:
            errors, reports = verify_v18_document_for_test(document, 100000)
            amplified = copy.deepcopy(document)
            amplified["rows"] = [copy.deepcopy(mutated) for _ in range(12)]
            resign_document(amplified)
            amplified_errors, amplified_reports = verify_v18_document_for_test(
                amplified, 100000
            )
        finally:
            document_globals["_verify_density_row_unchecked"] = original_row_verifier
        self.assertTrue(errors)
        self.assertEqual(reports, [])
        self.assertTrue(amplified_errors)
        self.assertEqual(amplified_reports, [])
        self.assertEqual(row_calls, 0)

    def test_v18_static_optimizer_admission_precedes_curve_and_solver_work(self) -> None:
        mutations = []

        wrong_objective = copy.deepcopy(self.frozen_density_row)
        wrong_objective["private_audit"]["density_frontier"][0]["optimizer"][
            "objective_mode"
        ] = "legacy"
        refresh_density_accounting(wrong_objective)
        mutations.append((wrong_objective, "objective mode mismatch"))

        nonempty_frontier = copy.deepcopy(self.frozen_density_row)
        optimizer = nonempty_frontier["private_audit"]["density_frontier"][0][
            "optimizer"
        ]
        optimizer["full_objective_exact"] = False
        optimizer["remaining_frontier_nodes"] = 1
        optimizer["termination_reason"] = "node_cap"
        optimizer["frontier_states"] = [
            {
                "selected_mask_hex": "0x0",
                "available_mask_hex": "0x0",
                "selected_support_mask_hex": "0x0",
                "support_upper_bound": 0,
                "selected_count_upper_bound": 0,
            }
        ]
        optimizer["frontier_sha256"] = VERIFIER["digest"](
            optimizer["frontier_states"]
        )
        refresh_density_accounting(nonempty_frontier)
        mutations.append((nonempty_frontier, "exact frontier must contain exactly 0"))

        oversized_mask = copy.deepcopy(self.frozen_density_row)
        oversized_mask["private_audit"]["density_frontier"][0]["optimizer"][
            "selected_mask_hex"
        ] = "0x" + "f" * 128
        refresh_density_accounting(oversized_mask)
        mutations.append((oversized_mask, "optimizer mask"))

        oversized_edges = copy.deepcopy(self.frozen_density_row)
        public = oversized_edges["public_model"]["density_frontier"][0]
        formal_bound = sum(math.comb(4 + degree - 1, degree) for degree in range(5))
        public["public_edges"] = [
            {"left": "O", "right": "O", "output": "O"}
            for _ in range(formal_bound * (formal_bound + 1) // 2 + 1)
        ]
        public["public_edges_sha256"] = VERIFIER["digest"](public["public_edges"])
        refresh_density_accounting(oversized_edges)
        mutations.append((oversized_edges, "edge table exceeds its source-derived length bound"))

        verifier_globals = _RAW_VERIFY_DENSITY_ROW_FOR_TESTS.__globals__
        guarded = (
            "verify_curve_provenance",
            "frozen_curve_record",
            "registered_curve_bundle",
            "replay_density_search",
            "independent_density_primary_optimum",
        )
        originals = {name: verifier_globals[name] for name in guarded}
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"static admission must precede {name}")

            return reject

        for name in guarded:
            verifier_globals[name] = forbidden(name)
        try:
            for mutated, expected in mutations:
                with self.subTest(expected=expected):
                    report = verify_density_row_for_test(
                        mutated, 100000, "frozen_fixture"
                    )
                    self.assertFalse(report["valid"])
                    self.assertIsNone(report["resource_reservation"])
                    self.assertTrue(
                        any(expected in error for error in report["errors"]),
                        report["errors"],
                    )
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_v18_claims_and_nested_integrity_precede_reservation_and_math(self) -> None:
        baseline = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        mutations = []

        summary = copy.deepcopy(baseline)
        summary["summary"]["row_count"] += 1
        resign_document(summary)
        mutations.append((summary, "document summary mismatch"))

        gate = copy.deepcopy(baseline)
        gate["family_gate"]["status"] = "PASS"
        resign_document(gate)
        mutations.append((gate, "frozen family gate is not the exact registered object"))

        nested_digest = copy.deepcopy(baseline)
        nested_digest["rows"][0]["public_model"]["factor_base"][
            "selection_sha256"
        ] = "0" * 64
        refresh_density_accounting(nested_digest["rows"][0])
        resign_document(nested_digest)
        mutations.append((nested_digest, "factor-base selection digest mismatch"))

        nested_accounting = copy.deepcopy(baseline)
        nested_accounting["rows"][0]["accounting"]["public_model_json_bytes"] += 1
        resign_density_row(nested_accounting["rows"][0])
        resign_document(nested_accounting)
        mutations.append((nested_accounting, "cost-accounting byte receipt mismatch"))

        verifier_globals = VERIFIER["verify_document"].__globals__
        originals = {
            name: verifier_globals[name]
            for name in ("resource_envelope", "_verify_density_row_unchecked")
        }
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"static admission must precede {name}")

            return reject

        for name in originals:
            verifier_globals[name] = forbidden(name)
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "static-preflight.json"
                for document, expected in mutations:
                    with self.subTest(expected=expected):
                        path.write_bytes(VERIFIER["stable_bytes"](document))
                        report = VERIFIER["verify_document"](path, 100000)
                        self.assertFalse(report["valid"])
                        self.assertIsNone(report["resource_reservation"])
                        self.assertTrue(
                            any(expected in error for error in report["errors"]),
                            report["errors"],
                        )
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_v18_replay_budget_and_actual_phase_receipts_fail_closed(self) -> None:
        over_budget = copy.deepcopy(self.frozen_density_row)
        for cell in over_budget["private_audit"]["density_frontier"]:
            cell["optimizer"]["node_cap"] = 100001
        refresh_density_accounting(over_budget)
        verifier_globals = _RAW_VERIFY_DENSITY_ROW_FOR_TESTS.__globals__
        original_replay = verifier_globals["replay_density_search"]
        replay_calls = 0

        def forbidden_replay(*_args, **_kwargs):
            nonlocal replay_calls
            replay_calls += 1
            raise AssertionError("replay must not run")

        verifier_globals["replay_density_search"] = forbidden_replay
        try:
            report = verify_density_row_for_test(
                over_budget, 100000, "frozen_fixture"
            )
        finally:
            verifier_globals["replay_density_search"] = original_replay
        self.assertFalse(report["valid"])
        self.assertEqual(replay_calls, 0)
        self.assertEqual(report["primary_nodes"], 0)
        self.assertTrue(
            any("trusted verifier limit" in error for error in report["errors"])
        )

        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        document_globals = _RAW_VERIFY_V18_DOCUMENT_FOR_TESTS.__globals__
        original_total_replay = document_globals["MAXIMUM_TOTAL_REPLAY_NODES"]
        original_row_verifier = document_globals["_verify_density_row_unchecked"]
        aggregate_row_calls = 0

        def forbidden_aggregate_row(*_args, **_kwargs):
            nonlocal aggregate_row_calls
            aggregate_row_calls += 1
            raise AssertionError("aggregate-budget rejection must precede row semantics")

        document_globals["MAXIMUM_TOTAL_REPLAY_NODES"] = 399999
        document_globals["_verify_density_row_unchecked"] = forbidden_aggregate_row
        try:
            aggregate_errors, aggregate_reports = verify_v18_document_for_test(
                document, 100000
            )
        finally:
            document_globals["MAXIMUM_TOTAL_REPLAY_NODES"] = original_total_replay
            document_globals["_verify_density_row_unchecked"] = original_row_verifier
        self.assertIn(
            "replay-node bound exceeds the trusted verifier limit", aggregate_errors
        )
        self.assertEqual(aggregate_reports, [])
        self.assertEqual(aggregate_row_calls, 0)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            valid = VERIFIER["verify_document"](path, 100000)
            self.assertTrue(valid["valid"], valid["errors"])
            standalone = standalone_frozen_b4_oracle()
            standalone_candidate_count = standalone["candidate_count"]
            standalone_eligible_count = standalone["eligible_count"]
            self.assertEqual(
                valid["actual_work"],
                {
                    "actual_work_complete": True,
                    "registered_curve_cache_hits": 0,
                    "registered_curve_cache_misses": 0,
                    "registered_curve_draws": 0,
                    "registered_curve_hash_calls": 0,
                    "registered_prime_candidates": 0,
                    "predicate_hash_calls": 0,
                    "registered_curve_point_enumerations": 0,
                    "frozen_curve_point_enumerations": 1,
                    "semantic_curve_point_enumerations": 1,
                    "primary_curve_point_enumerations": 4,
                    "expansion_cells": 214,
                    "graph_candidate_evaluations": standalone_candidate_count,
                    "graph_eligible_conflict_checks": math.comb(
                        standalone_eligible_count, 2
                    ),
                    "graph_eligible_pair_output_cells": (
                        standalone_eligible_count**2
                    ),
                    "replay_nodes": 218,
                    "replay_metric_cache_entries": 268,
                    "retained_model_replay_cache_entries": 268,
                    "independent_primary_nodes": 250,
                    "primary_support_cache_entries": 56,
                    "primary_constrained_cache_entries": 129,
                    "retained_model_calls": 401,
                    "retained_model_cells": 41404,
                    "registered_curve_cache_entries": 0,
                },
            )
            self.assertEqual(
                valid["resource_reservation"],
                {
                    "row_count": 1,
                    "cap_cell_count": 4,
                    "registered_curve_cache_entries": 0,
                    "registered_curve_cache_lookups_upper_bound": 0,
                    "registered_curve_cache_misses_upper_bound": 0,
                    "registered_prime_candidates_upper_bound": 0,
                    "registered_curve_draws_upper_bound": 0,
                    "registered_curve_hash_calls_upper_bound": 0,
                    "registered_curve_point_enumerations_upper_bound": 0,
                    "frozen_curve_point_enumerations_upper_bound": 1,
                    "predicate_hash_calls_upper_bound": 0,
                    "semantic_curve_point_enumerations_upper_bound": 1,
                    "primary_curve_point_enumerations_upper_bound": 4,
                    "expansion_cells_upper_bound": 214,
                    "graph_candidate_evaluations_upper_bound": 35,
                    "graph_eligible_conflict_checks_upper_bound": 595,
                    "graph_eligible_pair_output_cells_upper_bound": 1225,
                    "replay_nodes_upper_bound": 400000,
                    "independent_primary_nodes_upper_bound": 400000,
                    "metric_cache_entries_upper_bound": 1610320,
                    "retained_model_calls_upper_bound": 805164,
                    "retained_model_cells_upper_bound": 2000832540,
                },
            )
            self.assertEqual(valid["resource_reservation"]["row_count"], 1)
            self.assertEqual(valid["resource_reservation"]["cap_cell_count"], 4)
            self.assertEqual(
                valid["resource_reservation"]["replay_nodes_upper_bound"], 400000
            )
            self.assertEqual(
                valid["resource_reservation"]["independent_primary_nodes_upper_bound"],
                400000,
            )
            self.assertLessEqual(
                valid["actual_work"]["replay_nodes"],
                valid["resource_reservation"]["replay_nodes_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["independent_primary_nodes"],
                valid["resource_reservation"]["independent_primary_nodes_upper_bound"],
            )
            observed_cache_entries = sum(
                valid["actual_work"][name]
                for name in (
                    "replay_metric_cache_entries",
                    "retained_model_replay_cache_entries",
                    "primary_support_cache_entries",
                    "primary_constrained_cache_entries",
                )
            )
            self.assertLessEqual(
                observed_cache_entries,
                valid["resource_reservation"]["metric_cache_entries_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["retained_model_calls"],
                valid["resource_reservation"]["retained_model_calls_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["retained_model_cells"],
                valid["resource_reservation"]["retained_model_cells_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["semantic_curve_point_enumerations"],
                valid["resource_reservation"][
                    "semantic_curve_point_enumerations_upper_bound"
                ],
            )
            self.assertLessEqual(
                valid["actual_work"]["primary_curve_point_enumerations"],
                valid["resource_reservation"][
                    "primary_curve_point_enumerations_upper_bound"
                ],
            )
            self.assertLessEqual(
                valid["actual_work"]["registered_prime_candidates"],
                valid["resource_reservation"][
                    "registered_prime_candidates_upper_bound"
                ],
            )
            self.assertLessEqual(
                valid["actual_work"]["predicate_hash_calls"],
                valid["resource_reservation"][
                    "predicate_hash_calls_upper_bound"
                ],
            )
            self.assertTrue(valid["actual_work"]["actual_work_complete"])

            extra = copy.deepcopy(document)
            extra["unexpected"] = True
            resign_document(extra)
            path.write_bytes(VERIFIER["stable_bytes"](extra))
            invalid = VERIFIER["verify_document"](path, 100000)
            self.assertFalse(invalid["valid"])
            self.assertEqual(
                invalid["phases"][-1],
                {"name": "source_collection_bounds", "status": "failed"},
            )
            self.assertFalse(
                any(
                    phase["name"] == "bounded_json_shape"
                    for phase in invalid["phases"]
                )
            )

            budget_invalid = VERIFIER["verify_document"](path, False)
            self.assertEqual(
                budget_invalid["phases"],
                [{"name": "verifier_budget_preflight", "status": "failed"}],
            )

    def test_v18_phase_receipts_match_executed_control_flow(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"

            path.write_bytes(VERIFIER["stable_bytes"](document))
            valid = VERIFIER["verify_document"](path, 100000)
            self.assertTrue(valid["valid"], valid["errors"])
            self.assertEqual(
                valid["phases"],
                [
                    {"name": "verifier_budget_preflight", "status": "passed"},
                    {"name": "single_regular_file_snapshot", "status": "passed"},
                    {"name": "strict_json_parse", "status": "passed"},
                    {"name": "source_collection_bounds", "status": "passed"},
                    {"name": "bounded_json_shape", "status": "passed"},
                    {"name": "exact_schema_routing", "status": "passed"},
                    {"name": "closed_document_schema", "status": "passed"},
                    {"name": "exact_document_types", "status": "passed"},
                    {
                        "name": "document_digest_and_protocol_identity",
                        "status": "passed",
                    },
                    {"name": "registered_document_envelope", "status": "passed"},
                    {"name": "closed_registered_row_preflight", "status": "passed"},
                    {"name": "registered_matrix_preflight", "status": "passed"},
                    {
                        "name": "document_summary_and_family_gate_preflight",
                        "status": "passed",
                    },
                    {"name": "trusted_resource_reservation", "status": "passed"},
                    {
                        "name": "curve_factor_graph_and_expansion_reconstruction",
                        "status": "passed",
                        "expected_units": 1,
                        "completed_units": 1,
                        "failed_units": 0,
                    },
                    {
                        "name": "deterministic_optimizer_replay",
                        "status": "passed",
                        "expected_units": 4,
                        "completed_units": 4,
                        "failed_units": 0,
                    },
                    {
                        "name": "retained_model_transcript_reconstruction",
                        "status": "passed",
                        "expected_units": 4,
                        "completed_units": 4,
                        "failed_units": 0,
                    },
                    {
                        "name": "independent_primary_proof",
                        "status": "passed",
                        "expected_units": 4,
                        "completed_units": 4,
                        "failed_units": 0,
                    },
                    {"name": "row_semantic_verification", "status": "passed"},
                    {
                        "name": "completed_provenance_and_predicate_work_equality",
                        "status": "passed",
                    },
                    {
                        "name": "actual_work_reservation_dominance",
                        "status": "passed",
                    },
                    {
                        "name": "successful_phase_closure_validity",
                        "status": "passed",
                    },
                ],
            )

            path.write_text('{"schema":', encoding="ascii")
            malformed = VERIFIER["verify_document"](path, 100000)
            self.assertEqual(
                malformed["phases"][-1],
                {"name": "strict_json_parse", "status": "failed"},
            )
            self.assertFalse(
                any(phase["name"] == "bounded_json_shape" for phase in malformed["phases"])
            )

            legacy = copy.deepcopy(document)
            legacy["schema"] = "sgcp-embed-002-density-frontier-candidate-v5"
            resign_document(legacy)
            path.write_bytes(VERIFIER["stable_bytes"](legacy))
            legacy_report = VERIFIER["verify_document"](path, 100000)
            self.assertEqual(
                legacy_report["phases"][-2:],
                [
                    {"name": "exact_schema_routing", "status": "passed"},
                    {"name": "unsupported_legacy_rejection", "status": "passed"},
                ],
            )

            invalid_envelope = copy.deepcopy(document)
            invalid_envelope["parameters"]["node_cap_per_cap"] = 99999
            resign_document(invalid_envelope)
            path.write_bytes(VERIFIER["stable_bytes"](invalid_envelope))
            envelope_report = VERIFIER["verify_document"](path, 100000)
            self.assertEqual(
                envelope_report["phases"][-1],
                {"name": "registered_document_envelope", "status": "failed"},
            )
            self.assertFalse(
                any(
                    phase["name"] == "closed_registered_row_preflight"
                    for phase in envelope_report["phases"]
                )
            )

    def test_v18_success_requires_complete_unit_phase_receipts(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_record = verifier_globals["record_phase_unit"]
        suppressed = False

        def suppress_one_primary_receipt(phases, name, status):
            nonlocal suppressed
            if (
                not suppressed
                and name == "independent_primary_proof"
                and status == "passed"
            ):
                suppressed = True
                return
            original_record(phases, name, status)

        verifier_globals["record_phase_unit"] = suppress_one_primary_receipt
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "suppressed-phase.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["record_phase_unit"] = original_record

        self.assertTrue(suppressed)
        self.assertFalse(report["valid"])
        primary_phase = next(
            phase
            for phase in report["phases"]
            if phase["name"] == "independent_primary_proof"
        )
        self.assertEqual(
            primary_phase,
            {
                "name": "independent_primary_proof",
                "status": "incomplete",
                "expected_units": 4,
                "completed_units": 3,
                "failed_units": 0,
            },
        )
        self.assertEqual(
            report["phases"][-1],
            {"name": "successful_phase_closure_validity", "status": "failed"},
        )
        self.assertIn(
            "successful phase 'independent_primary_proof' is not passed",
            report["errors"],
        )

    def test_v18_second_cap_exceptions_preserve_partial_work_and_reservation(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        cases = (
            ("replay_density_search", "deterministic_optimizer_replay"),
            ("independent_density_primary_optimum", "independent_primary_proof"),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for function_name, phase_name in cases:
                with self.subTest(function_name=function_name):
                    original = verifier_globals[function_name]
                    calls = 0

                    def fail_on_second(*args, **kwargs):
                        nonlocal calls
                        calls += 1
                        if calls == 2:
                            raise RuntimeError("injected second-cap failure")
                        return original(*args, **kwargs)

                    verifier_globals[function_name] = fail_on_second
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        verifier_globals[function_name] = original

                    self.assertFalse(report["valid"])
                    self.assertIsNotNone(report["resource_reservation"])
                    self.assertEqual(
                        report["resource_reservation"]["cap_cell_count"], 4
                    )
                    self.assertEqual(report["row_count"], 1)
                    self.assertEqual(len(report["rows"][0]["cap_reports"]), 2)
                    first_cap = report["rows"][0]["cap_reports"][0]
                    self.assertGreater(
                        first_cap["replay_nodes"] + first_cap["primary_nodes"], 0
                    )
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(
                        next(
                            phase["status"]
                            for phase in report["phases"]
                            if phase["name"] == phase_name
                        ),
                        "failed",
                    )
                    self.assertTrue(
                        any(
                            "injected second-cap failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v18_mid_function_failures_preserve_failing_cap_work(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        cases = (
            ("replay_nodes", "deterministic_optimizer_replay"),
            ("independent_primary_nodes", "independent_primary_proof"),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_charge = verifier_globals["charge_actual_work"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for counter_name, phase_name in cases:
                with self.subTest(counter_name=counter_name):
                    observed = 0

                    def fail_after_charge(name, amount=1):
                        nonlocal observed
                        original_charge(name, amount)
                        if name == counter_name:
                            observed += amount
                            if observed >= 2:
                                raise RuntimeError("injected mid-function failure")

                    verifier_globals["charge_actual_work"] = fail_after_charge
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        verifier_globals["charge_actual_work"] = original_charge

                    self.assertFalse(report["valid"])
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(report["actual_work"][counter_name], 2)
                    cap_counter_name = (
                        "primary_nodes"
                        if counter_name == "independent_primary_nodes"
                        else counter_name
                    )
                    self.assertEqual(
                        report["rows"][0]["cap_reports"][0][cap_counter_name], 2
                    )
                    phase = next(
                        value for value in report["phases"] if value["name"] == phase_name
                    )
                    self.assertEqual(
                        phase,
                        {
                            "name": phase_name,
                            "status": "failed",
                            "expected_units": 4,
                            "completed_units": 1,
                            "failed_units": 1,
                        },
                    )
                    self.assertTrue(
                        any(
                            "injected mid-function failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v18_graph_and_expansion_failures_preserve_partial_work(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        counters = (
            "graph_candidate_evaluations",
            "graph_eligible_conflict_checks",
            "expansion_cells",
            "graph_eligible_pair_output_cells",
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_charge = verifier_globals["charge_actual_work"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph-partial-work.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for counter_name in counters:
                with self.subTest(counter_name=counter_name):
                    observed = 0

                    def fail_after_second_charge(name, amount=1):
                        nonlocal observed
                        original_charge(name, amount)
                        if name == counter_name:
                            observed += amount
                            if observed >= 2:
                                raise RuntimeError("injected graph/expansion failure")

                    verifier_globals["charge_actual_work"] = fail_after_second_charge
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        verifier_globals["charge_actual_work"] = original_charge

                    self.assertFalse(report["valid"])
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(report["actual_work"][counter_name], 2)
                    phase = next(
                        value
                        for value in report["phases"]
                        if value["name"]
                        == "curve_factor_graph_and_expansion_reconstruction"
                    )
                    self.assertEqual(
                        phase,
                        {
                            "name": "curve_factor_graph_and_expansion_reconstruction",
                            "status": "failed",
                            "expected_units": 1,
                            "completed_units": 1,
                            "failed_units": 1,
                        },
                    )
                    self.assertTrue(
                        any(
                            "injected graph/expansion failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v18_completed_graph_and_expansion_work_rejects_undercharge(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        expected = {
            "graph_candidate_evaluations": 31,
            "graph_eligible_conflict_checks": 66,
            "graph_eligible_pair_output_cells": 144,
            "expansion_cells": 214,
        }
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_charge = verifier_globals["charge_actual_work"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph-undercharge.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for counter_name, expected_count in expected.items():
                with self.subTest(counter_name=counter_name):

                    def suppress_counter(name, amount=1):
                        if name != counter_name:
                            original_charge(name, amount)

                    verifier_globals["charge_actual_work"] = suppress_counter
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        verifier_globals["charge_actual_work"] = original_charge

                    self.assertFalse(report["valid"])
                    self.assertTrue(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(report["actual_work"][counter_name], 0)
                    self.assertFalse(report["rows"][0]["valid"])
                    self.assertIn(
                        "row[0]: completed graph/expansion actual-work mismatch: "
                        f"{counter_name}=0 != expected={expected_count}",
                        report["errors"],
                    )
                    phase = next(
                        value
                        for value in report["phases"]
                        if value["name"]
                        == "curve_factor_graph_and_expansion_reconstruction"
                    )
                    self.assertEqual(
                        phase,
                        {
                            "name": "curve_factor_graph_and_expansion_reconstruction",
                            "status": "failed",
                            "expected_units": 1,
                            "completed_units": 1,
                            "failed_units": 1,
                        },
                    )

            injected = False

            def overcharge_first_candidate(name, amount=1):
                nonlocal injected
                original_charge(name, amount)
                if name == "graph_candidate_evaluations" and not injected:
                    original_charge(name)
                    injected = True

            verifier_globals["charge_actual_work"] = overcharge_first_candidate
            try:
                report = VERIFIER["verify_document"](path, 100000)
            finally:
                verifier_globals["charge_actual_work"] = original_charge
            self.assertFalse(report["valid"])
            self.assertTrue(report["actual_work"]["actual_work_complete"])
            self.assertEqual(report["actual_work"]["graph_candidate_evaluations"], 32)
            self.assertIn(
                "row[0]: completed graph/expansion actual-work mismatch: "
                "graph_candidate_evaluations=32 != expected=31",
                report["errors"],
            )

    def test_v18_completed_provenance_and_predicate_counts_are_exact(self) -> None:
        rows = canonical_factor_base_transcript_rows()
        expected = VERIFIER[
            "completed_provenance_and_predicate_work_expectations"
        ](rows)
        self.assertEqual(
            expected,
            {
                "registered_prime_candidates": 480,
                "registered_curve_draws": 112,
                "registered_curve_hash_calls": 336,
                "registered_curve_point_enumerations": 218,
                "predicate_hash_calls": 4218,
            },
        )

        verifier_globals = VERIFIER["verify_curve_provenance"].__globals__
        original_charge = verifier_globals["charge_actual_work"]

        def execute_transcript() -> dict[str, int]:
            with verifier_path_test_context() as state:
                state.registered_curve_cache.clear()
                verifier_globals["reset_actual_work"]()
                for row in rows:
                    curve = verifier_globals["verify_curve_provenance"](row["curve"])
                    factors = verifier_globals["verify_factor_base"](
                        curve, curve.points(), row
                    )
                    self.assertEqual(len(factors), row["B"])
                return verifier_globals["actual_work_snapshot"](
                    verifier_globals[
                        "COMPLETED_PROVENANCE_AND_PREDICATE_COUNTER_NAMES"
                    ]
                )

        baseline = execute_transcript()
        self.assertEqual(baseline, expected)
        self.assertTrue(verifier_globals["actual_work_receipt"]([])["actual_work_complete"])

        for counter_name in expected:
            for adjustment in (-1, 1):
                with self.subTest(counter_name=counter_name, adjustment=adjustment):
                    changed = False

                    def alter_one_charge(name, amount=1):
                        nonlocal changed
                        if name == counter_name and not changed:
                            changed = True
                            if adjustment < 0:
                                if amount > 1:
                                    original_charge(name, amount - 1)
                                return
                            original_charge(name, amount + adjustment)
                        else:
                            original_charge(name, amount)

                    verifier_globals["charge_actual_work"] = alter_one_charge
                    try:
                        observed = execute_transcript()
                        receipt = verifier_globals["actual_work_receipt"]([])
                    finally:
                        verifier_globals["charge_actual_work"] = original_charge

                    self.assertTrue(changed)
                    self.assertTrue(receipt["actual_work_complete"])
                    self.assertEqual(
                        observed[counter_name], expected[counter_name] + adjustment
                    )
                    self.assertEqual(
                        VERIFIER[
                            "completed_provenance_and_predicate_work_errors"
                        ](observed, rows),
                        [
                            "completed provenance/predicate actual-work mismatch: "
                            f"{counter_name}={expected[counter_name] + adjustment} "
                            f"!= expected={expected[counter_name]}"
                        ],
                    )

    def test_v18_predicate_exception_preserves_partial_work_as_incomplete(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_factor_base = verifier_globals["verify_factor_base"]

        def interrupted_factor_base(*_args, **_kwargs):
            verifier_globals["charge_actual_work"]("predicate_hash_calls")
            raise RuntimeError("injected predicate interruption")

        verifier_globals["verify_factor_base"] = interrupted_factor_base
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "predicate-interruption.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["verify_factor_base"] = original_factor_base

        self.assertFalse(report["valid"])
        self.assertFalse(report["actual_work"]["actual_work_complete"])
        self.assertEqual(report["actual_work"]["predicate_hash_calls"], 1)
        self.assertTrue(
            any("injected predicate interruption" in error for error in report["errors"])
        )
        self.assertFalse(
            any(
                phase["name"]
                == "completed_provenance_and_predicate_work_equality"
                for phase in report["phases"]
            )
        )

    def test_v18_point_enumeration_calls_are_charged_before_failure(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        curve_class = VERIFIER["Curve"]
        original_points = curve_class.points
        expected_counts = (
            (
                1,
                1,
                0,
                0,
                "curve_factor_graph_and_expansion_reconstruction",
                1,
            ),
            (
                2,
                1,
                1,
                0,
                "curve_factor_graph_and_expansion_reconstruction",
                1,
            ),
            (3, 1, 1, 1, "independent_primary_proof", 4),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "enumeration.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for (
                fail_call,
                frozen_count,
                semantic_count,
                primary_count,
                phase_name,
                expected_units,
            ) in expected_counts:
                with self.subTest(fail_call=fail_call):
                    calls = 0

                    def injected_points(instance):
                        nonlocal calls
                        calls += 1
                        if calls == fail_call:
                            raise RuntimeError("injected point-enumeration failure")
                        return original_points(instance)

                    curve_class.points = injected_points
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        curve_class.points = original_points

                    self.assertFalse(report["valid"])
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(
                        report["actual_work"]["frozen_curve_point_enumerations"],
                        frozen_count,
                    )
                    self.assertEqual(
                        report["actual_work"]["semantic_curve_point_enumerations"],
                        semantic_count,
                    )
                    self.assertEqual(
                        report["actual_work"]["primary_curve_point_enumerations"],
                        primary_count,
                    )
                    phase = next(
                        value
                        for value in report["phases"]
                        if value["name"] == phase_name
                    )
                    self.assertEqual(
                        phase,
                        {
                            "name": phase_name,
                            "status": "failed",
                            "expected_units": expected_units,
                            "completed_units": 1,
                            "failed_units": 1,
                        },
                    )
                    self.assertTrue(
                        any(
                            "injected point-enumeration failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v18_actual_work_overage_invalidates_an_otherwise_valid_document(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_envelope = verifier_globals["resource_envelope"]

        def under_reserve(rows, maximum_nodes, scope):
            receipt, errors = original_envelope(rows, maximum_nodes, scope)
            receipt["replay_nodes_upper_bound"] = 0
            return receipt, errors

        verifier_globals["resource_envelope"] = under_reserve
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "under-reserved.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["resource_envelope"] = original_envelope

        self.assertFalse(report["valid"])
        self.assertTrue(report["actual_work"]["actual_work_complete"])
        self.assertEqual(report["actual_work"]["replay_nodes"], 218)
        self.assertEqual(report["resource_reservation"]["replay_nodes_upper_bound"], 0)
        self.assertIn(
            "actual work exceeds reservation: replay_nodes=218 > "
            "replay_nodes_upper_bound=0",
            report["errors"],
        )
        self.assertEqual(
            report["phases"][-1],
            {"name": "actual_work_reservation_dominance", "status": "failed"},
        )

    def test_v18_completed_work_rejects_exact_enumeration_undercharge(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_charge = verifier_globals["charge_actual_work"]

        def suppress_primary_enumeration(name, amount=1):
            if name != "primary_curve_point_enumerations":
                original_charge(name, amount)

        verifier_globals["charge_actual_work"] = suppress_primary_enumeration
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "undercharged.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["charge_actual_work"] = original_charge

        self.assertFalse(report["valid"])
        self.assertTrue(report["actual_work"]["actual_work_complete"])
        self.assertTrue(report["rows"][0]["valid"], report["rows"][0]["errors"])
        self.assertEqual(report["actual_work"]["primary_curve_point_enumerations"], 0)
        self.assertEqual(
            report["resource_reservation"][
                "primary_curve_point_enumerations_upper_bound"
            ],
            4,
        )
        self.assertIn(
            "actual work exact-count mismatch: "
            "primary_curve_point_enumerations=0 != "
            "primary_curve_point_enumerations_upper_bound=4",
            report["errors"],
        )
        self.assertEqual(
            report["phases"][-1],
            {"name": "actual_work_reservation_dominance", "status": "failed"},
        )

    def test_v18_ordering_contract_is_independently_frozen(self) -> None:
        mutated = copy.deepcopy(self.frozen_density_row)
        mutated["public_model"]["ordering_contract"]["point_labels"] = (
            "affine labels may contain leading zeroes"
        )
        refresh_density_accounting(mutated)
        report = verify_density_row_for_test(
            mutated, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("ordering contract mismatch" in error for error in report["errors"])
        )

    def test_frozen_document_verifies_and_empty_canonical_document_is_rejected(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        errors, reports = verify_v18_document_for_test(document, 100000)
        self.assertEqual(errors, [])
        self.assertTrue(reports[0]["valid"])

        with self.assertRaises(ValueError):
            MODULE["build_document"]([], "canonical", MODULE["canonical_parameters"]())

        empty = copy.deepcopy(document)
        empty.update(
            {
                "scope": "canonical",
                "canonical": True,
                "interpretation": "canonical candidate; coordinator interpretation still required",
                "parameters": MODULE["canonical_parameters"](),
                "rows": [],
                "summary": MODULE["document_summary"]([]),
                "family_gate": {"status": "PASS"},
            }
        )
        resign_document(empty)
        errors, _ = verify_v18_document_for_test(empty, 100000)
        self.assertTrue(errors)
        self.assertIn("canonical document must contain exactly 168 rows", errors)

    def test_v18_document_exact_types_are_closed(self) -> None:
        baseline = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        mutations = (
            (("protocol_version",), 5.0),
            (("canonical",), 0),
            (("claim_status", 0), 1),
            (("summary", "row_count"), False),
            (("family_gate", "status"), False),
        )
        for path, replacement in mutations:
            with self.subTest(path=path):
                document = copy.deepcopy(baseline)
                target = document
                for component in path[:-1]:
                    target = target[component]
                target[path[-1]] = replacement
                resign_document(document)
                errors, _ = verify_v18_document_for_test(
                    document, 100000
                )
                self.assertTrue(errors)

    def test_document_router_uses_v18_strict_path_and_rejects_every_legacy_schema(
        self,
    ) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        def route(value):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "synthetic-document.json"
                path.write_bytes(VERIFIER["stable_bytes"](value))
                return VERIFIER["verify_document"](
                    path, 100000
                )

        strict_report = route(document)
        self.assertTrue(strict_report["valid"], strict_report["errors"])
        self.assertTrue(
            any(
                "closed_document_schema" in check
                for check in strict_report["independent_checks"]
            )
        )

        for legacy_schema in sorted(VERIFIER["LEGACY_SCHEMAS"]):
            with self.subTest(legacy_schema=legacy_schema):
                downgraded = copy.deepcopy(document)
                downgraded["schema"] = legacy_schema
                resign_document(downgraded)
                legacy_report = route(downgraded)
                self.assertFalse(legacy_report["valid"])
                self.assertTrue(
                    any(
                        "unsupported legacy document schema" in error
                        for error in legacy_report["errors"]
                    ),
                    legacy_report["errors"],
                )
                self.assertEqual(legacy_report["row_count"], 0)
                self.assertFalse(
                    any("graph" in check for check in legacy_report["independent_checks"])
                )

        empty_v3 = {
            "schema": "sgcp-embed-002-density-frontier-candidate-v3",
            "canonical": False,
            "rows": [],
        }
        empty_v3["document_sha256"] = VERIFIER["digest"](empty_v3)
        empty_report = route(empty_v3)
        self.assertFalse(empty_report["valid"])
        self.assertEqual(empty_report["row_count"], 0)

        malformed_schema = copy.deepcopy(document)
        malformed_schema["schema"] = []
        resign_document(malformed_schema)
        malformed_report = route(malformed_schema)
        self.assertFalse(malformed_report["valid"])
        self.assertTrue(
            any(
                "document.schema has a non-source container/scalar type" in error
                for error in malformed_report["errors"]
            )
        )

    def test_canonical_matrix_envelope_rejects_every_grid_mutation(self) -> None:
        rows = synthetic_gate_rows()
        self.assertEqual(VERIFIER["canonical_matrix_errors"](rows), [])
        MODULE["validate_canonical_rows"](rows)

        cases = []
        missing = copy.deepcopy(rows[:-1])
        cases.append(("missing", missing, "grid/order"))
        extra = copy.deepcopy(rows)
        extra.append(copy.deepcopy(rows[-1]))
        cases.append(("extra", extra, "grid/order"))
        duplicate = copy.deepcopy(rows)
        duplicate[1] = copy.deepcopy(duplicate[0])
        cases.append(("duplicate", duplicate, "grid/order"))
        reordered = copy.deepcopy(rows)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        cases.append(("reordered", reordered, "grid/order"))
        wrong_public_cap = copy.deepcopy(rows)
        wrong_public_cap[0]["public_model"]["constrained_budget_caps"][0] += 1
        cases.append(("public_cap", wrong_public_cap, "cap schedule"))
        wrong_private_cap = copy.deepcopy(rows)
        wrong_private_cap[0]["private_audit"]["density_frontier"][0][
            "constrained_cap"
        ] += 1
        cases.append(("private_cap", wrong_private_cap, "cap-cell"))
        wrong_node_cap = copy.deepcopy(rows)
        wrong_node_cap[0]["private_audit"]["density_frontier"][0]["optimizer"][
            "node_cap"
        ] = MODULE["CANONICAL_NODE_CAP"] - 1
        cases.append(("node_cap", wrong_node_cap, "node-cap"))
        inconsistent_curve = copy.deepcopy(rows)
        inconsistent_curve[1]["curve"]["p"] += 2
        cases.append(("inconsistent_curve", inconsistent_curve, "inconsistent curve"))
        cross_seed_duplicate = copy.deepcopy(rows)
        source_curve = rows[0]["curve"]
        for row in cross_seed_duplicate:
            if row["curve"]["bits"] == 5 and row["curve"]["seed"] == 211:
                for name in ("p", "a", "b", "q"):
                    row["curve"][name] = source_curve[name]
        cases.append(
            ("cross_seed_duplicate", cross_seed_duplicate, "cross-seed duplicate")
        )

        for label, mutated, expected_fragment in cases:
            with self.subTest(label=label):
                errors = VERIFIER["canonical_matrix_errors"](mutated)
                self.assertTrue(
                    any(expected_fragment in error for error in errors), errors
                )
                with self.assertRaises(ValueError):
                    MODULE["validate_canonical_rows"](mutated)

    def test_family_gate_matches_independent_evaluator_and_refuses_gaps(self) -> None:
        rows = synthetic_gate_rows()
        producer = MODULE["evaluate_family_gate"](rows)
        independent = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(producer, independent)
        self.assertEqual(producer["status"], "PASS")
        self.assertEqual(len(producer["passing_family_cap_pairs"]), 6)

        incomplete = rows[:-1]
        with self.assertRaises(KeyError):
            MODULE["evaluate_family_gate"](incomplete)
        with self.assertRaises(KeyError):
            VERIFIER["independent_family_gate"](incomplete)

        unresolved = copy.deepcopy(rows)
        unresolved[0]["private_audit"]["density_frontier"][0]["optimizer"][
            "primary_exact"
        ] = False
        with self.assertRaises(ValueError):
            MODULE["evaluate_family_gate"](unresolved)
        with self.assertRaises(AssertionError):
            VERIFIER["independent_family_gate"](unresolved)

        gate_mutations = (
            ("primary_exact", False),
            ("full_objective_exact", False),
            ("retained_support_upper_bound", "increment"),
            ("absolute_gap", 1),
            ("absolute_gap", False),
            ("remaining_frontier_nodes", 1),
            ("frontier_states", [{"residual": True}]),
            ("frontier_sha256", "0" * 64),
            ("termination_reason", "node_cap"),
        )
        for field, value in gate_mutations:
            with self.subTest(field=field, value=value):
                mutated = copy.deepcopy(rows)
                optimizer = mutated[0]["private_audit"]["density_frontier"][0][
                    "optimizer"
                ]
                if value == "increment":
                    optimizer[field] += 1
                else:
                    optimizer[field] = value
                if field == "frontier_states":
                    optimizer["frontier_sha256"] = VERIFIER["digest"](value)
                with self.assertRaises(ValueError):
                    MODULE["evaluate_family_gate"](mutated)
                with self.assertRaises(AssertionError):
                    VERIFIER["independent_family_gate"](mutated)

    def test_family_gate_duplicate_null_median_preserves_multiplicity(self) -> None:
        values = [
            VERIFIER["Fraction"](value, 1) for value in (8, 8, 10, 12)
        ]
        self.assertEqual(VERIFIER["independent_median"](values), 9)
        self.assertEqual(
            VERIFIER["independent_median"](sorted(set(values))), 10
        )
        rows = configure_gate_rows()
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        for family in MODULE["COORDINATE_FAMILIES"]:
            for cap_fraction in ("1/2", "3/4"):
                report = gate_cap_report(gate, family, cap_fraction)
                self.assertEqual(report["positive_comparisons"], 24)

    def test_family_gate_persistence_accepts_one_quarter_and_rejects_one_step_below(
        self,
    ) -> None:
        family = "least_x_interval"
        exact = configure_gate_rows()
        for row in exact:
            if row["family"] != family:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = {
                "numerator": 1,
                "denominator": 4,
            }
        exact_gate = VERIFIER["independent_family_gate"](exact)
        self.assertEqual(exact_gate, MODULE["evaluate_family_gate"](exact))
        exact_report = next(
            report for report in exact_gate["families"] if report["family"] == family
        )
        self.assertTrue(exact_report["full_cap_persistence_pass"])

        below = copy.deepcopy(exact)
        for row in below:
            if row["family"] != family or row["curve"]["bits"] != 8:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = {
                "numerator": 999,
                "denominator": 4000,
            }
        below_gate = VERIFIER["independent_family_gate"](below)
        self.assertEqual(below_gate, MODULE["evaluate_family_gate"](below))
        below_report = next(
            report for report in below_gate["families"] if report["family"] == family
        )
        self.assertFalse(below_report["full_cap_persistence_pass"])

    def test_family_gate_collapse_threshold_is_strictly_below_one_tenth(self) -> None:
        rows = configure_gate_rows()
        for row in rows:
            if row["family"] == MODULE["NULL_FAMILY"]:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = {
                "numerator": 1,
                "denominator": 10,
            }
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        self.assertEqual(gate["negative_outcome"], "WEAKEN_OR_REJECT")
        self.assertTrue(
            all(
                report["full_cap_collapse_strata"] == 0
                and not report["full_cap_collapse"]
                for report in gate["families"]
            )
        )

    def test_family_gate_collapse_requires_every_coordinate_family(self) -> None:
        rows = configure_gate_rows()
        collapsing = set(MODULE["COORDINATE_FAMILIES"][:2])
        for row in rows:
            if row["family"] == MODULE["NULL_FAMILY"]:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            below = row["family"] in collapsing and row["curve"]["bits"] in (5, 6, 7)
            full_cap["retention"]["retained_to_balanced_raw"] = (
                {"numerator": 1, "denominator": 11}
                if below
                else {"numerator": 1, "denominator": 10}
            )
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        self.assertEqual(gate["negative_outcome"], "WEAKEN_OR_REJECT")
        collapsed = {
            report["family"]
            for report in gate["families"]
            if report["full_cap_collapse"]
        }
        self.assertEqual(collapsed, collapsing)

    def test_family_gate_hand_derived_18_of_24_and_three_strata_boundary(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        thresholds = {5: 2, 6: 3, 7: 5, 8: 10}
        differences = {
            bits: [thresholds[bits]] * 6 if bits in (5, 6, 7) else [0] * 6
            for bits in MODULE["CANONICAL_BITS"]
        }
        set_gate_differences(rows, family, "1/2", differences)
        producer = MODULE["evaluate_family_gate"](rows)
        independent = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(producer, independent)
        report = gate_cap_report(producer, family, "1/2")
        self.assertEqual(report["positive_comparisons"], 18)
        self.assertEqual(report["passing_bit_strata"], 3)
        self.assertTrue(report["pass"])
        self.assertEqual(
            producer["passing_family_cap_pairs"],
            [{"family": family, "cap_fraction": "1/2"}],
        )
        self.assertEqual(producer["negative_outcome"], "NOT_APPLICABLE")

    def test_family_gate_hand_derived_17_of_24_fails_with_three_strata(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        differences = {
            5: [2] * 6,
            6: [3] * 6,
            7: [5] * 5 + [0],
            8: [0] * 6,
        }
        set_gate_differences(rows, family, "1/2", differences)
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        report = gate_cap_report(gate, family, "1/2")
        self.assertEqual(report["positive_comparisons"], 17)
        self.assertEqual(report["passing_bit_strata"], 3)
        self.assertFalse(report["pass"])
        self.assertEqual(gate["status"], "FAIL")

    def test_family_gate_hand_derived_18_of_24_fails_with_two_strata(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        differences = {
            5: [2] * 6,
            6: [3] * 6,
            7: [1, 1, 1, 0, 0, 0],
            8: [1, 1, 1, 0, 0, 0],
        }
        set_gate_differences(rows, family, "1/2", differences)
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        report = gate_cap_report(gate, family, "1/2")
        self.assertEqual(report["positive_comparisons"], 18)
        self.assertEqual(report["passing_bit_strata"], 2)
        self.assertFalse(report["pass"])
        self.assertEqual(gate["status"], "FAIL")

    def test_family_gate_forbids_cross_cap_splicing_and_classifies_collapse(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        set_gate_differences(
            rows,
            family,
            "1/2",
            {
                5: [2] * 6,
                6: [3] * 6,
                7: [1, 1, 1, 0, 0, 0],
                8: [1, 1, 1, 0, 0, 0],
            },
        )
        set_gate_differences(
            rows,
            family,
            "3/4",
            {5: [2] * 6, 6: [3] * 6, 7: [5] * 5 + [0], 8: [0] * 6},
        )
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        half = gate_cap_report(gate, family, "1/2")
        three_quarters = gate_cap_report(gate, family, "3/4")
        self.assertEqual(
            (half["positive_comparisons"], half["passing_bit_strata"]), (18, 2)
        )
        self.assertEqual(
            (
                three_quarters["positive_comparisons"],
                three_quarters["passing_bit_strata"],
            ),
            (17, 3),
        )
        self.assertEqual(gate["passing_family_cap_pairs"], [])
        self.assertEqual(gate["negative_outcome"], "WEAKEN_OR_REJECT")

        collapsed = configure_gate_rows()
        for row in collapsed:
            if row["family"] == MODULE["NULL_FAMILY"]:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = (
                {"numerator": 1, "denominator": 10}
                if row["curve"]["bits"] == 8
                else {"numerator": 1, "denominator": 20}
            )
        collapse_gate = VERIFIER["independent_family_gate"](collapsed)
        self.assertEqual(collapse_gate, MODULE["evaluate_family_gate"](collapsed))
        self.assertEqual(collapse_gate["status"], "FAIL")
        self.assertEqual(collapse_gate["negative_outcome"], "COLLAPSE")
        self.assertTrue(
            all(
                report["full_cap_collapse"]
                and report["full_cap_collapse_strata"] == 3
                for report in collapse_gate["families"]
            )
        )

    def test_v18_internal_semantic_entrypoints_require_path_permit(self) -> None:
        probes = {
            "registered curve": lambda: VERIFIER["registered_curve_bundle"](5, 101),
            "legacy row": lambda: VERIFIER["_verify_legacy_row_unchecked"]({}, 1),
            "density row": lambda: VERIFIER["_verify_density_row_unchecked"](
                {}, 1, "frozen_fixture", 1
            ),
            "density test wrapper": lambda: VERIFIER[
                "_verify_density_row_for_tests"
            ]({}, 1, "frozen_fixture"),
            "document": lambda: VERIFIER["_verify_v18_document_value_unchecked"](
                {}, 1
            ),
            "document test wrapper": lambda: VERIFIER[
                "_verify_v18_document_value_for_tests"
            ]({}, 1),
            "path worker": lambda: VERIFIER[
                "_verify_document_with_active_path_state"
            ](Path("does-not-matter.json"), 1),
            "path worker body": lambda: VERIFIER[
                "_verify_document_with_active_path_state_body"
            ](Path("does-not-matter.json"), 1, object()),
        }
        for name, probe in probes.items():
            with self.subTest(name=name):
                with self.assertRaisesRegex(PermissionError, "path-only V18 permit"):
                    probe()

    def test_v18_actual_work_charge_is_exact_positive_integer(self) -> None:
        verifier_globals = VERIFIER["charge_actual_work"].__globals__
        with verifier_path_test_context() as state:
            for amount in (False, True, 0, -1, 1.0, "1", None):
                with self.subTest(amount=amount):
                    before = dict(state.actual_work)
                    with self.assertRaisesRegex(
                        TypeError, "exact positive integer"
                    ):
                        verifier_globals["charge_actual_work"](
                            "replay_nodes", amount
                        )
                    self.assertEqual(state.actual_work, before)
            verifier_globals["charge_actual_work"]("replay_nodes", 1)
            self.assertEqual(state.actual_work["replay_nodes"], 1)

    def test_v18_concurrent_verification_receipts_are_invocation_local(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen-v18.json"
            path.write_bytes(MODULE["stable_json"](document))
            baseline = VERIFIER["verify_document"](path, 100000)
            self.assertTrue(baseline["valid"], baseline["errors"])

            verifier_globals = VERIFIER["charge_actual_work"].__globals__
            original_charge = verifier_globals["charge_actual_work"]
            barrier = threading.Barrier(2)
            local = threading.local()

            def synchronized_charge(name, amount=1):
                if (
                    name == "graph_candidate_evaluations"
                    and not getattr(local, "joined", False)
                ):
                    local.joined = True
                    barrier.wait(timeout=10)
                original_charge(name, amount)

            verifier_globals["charge_actual_work"] = synchronized_charge
            try:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(
                            VERIFIER["verify_document"], path, 100000
                        )
                        for _ in range(2)
                    ]
                    reports = [future.result(timeout=30) for future in futures]
            finally:
                verifier_globals["charge_actual_work"] = original_charge

        self.assertEqual(reports, [baseline, baseline])
        self.assertIsNone(
            verifier_globals["_ACTIVE_VERIFICATION_STATE"].get()
        )

    def test_v18_nested_verification_restores_outer_receipt(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen-v18.json"
            path.write_bytes(MODULE["stable_json"](document))
            baseline = VERIFIER["verify_document"](path, 100000)
            verifier_globals = VERIFIER["verify_factor_base"].__globals__
            original_factor_base = verifier_globals["verify_factor_base"]
            nested_reports = []
            nested_started = False

            def verify_factor_base_with_nested_call(*args, **kwargs):
                nonlocal nested_started
                if not nested_started:
                    nested_started = True
                    nested_reports.append(
                        VERIFIER["verify_document"](path, 100000)
                    )
                return original_factor_base(*args, **kwargs)

            verifier_globals["verify_factor_base"] = (
                verify_factor_base_with_nested_call
            )
            try:
                outer = VERIFIER["verify_document"](path, 100000)
            finally:
                verifier_globals["verify_factor_base"] = original_factor_base

        self.assertTrue(nested_started)
        self.assertEqual(nested_reports, [baseline])
        self.assertEqual(outer, baseline)
        self.assertIsNone(
            verifier_globals["_ACTIVE_VERIFICATION_STATE"].get()
        )

    def test_v18_exception_closes_inner_state_and_restores_outer_context(self) -> None:
        verifier_globals = VERIFIER["verify_document"].__globals__
        active_state = verifier_globals["_ACTIVE_VERIFICATION_STATE"]
        outer_state = verifier_globals["_VerificationState"](
            path_permit=verifier_globals["_PATH_VERIFICATION_PERMIT"],
            owner_thread_id=threading.get_ident(),
        )
        original_worker = verifier_globals["_verify_document_with_active_path_state"]
        observed_inner_states = []

        def failing_worker(*_args, **_kwargs):
            observed_inner_states.append(active_state.get())
            raise RuntimeError("injected public-worker failure")

        outer_token = active_state.set(outer_state)
        verifier_globals["_verify_document_with_active_path_state"] = failing_worker
        try:
            with self.assertRaisesRegex(RuntimeError, "public-worker failure"):
                VERIFIER["verify_document"](Path("unused.json"), 1)
            self.assertIs(active_state.get(), outer_state)
        finally:
            verifier_globals["_verify_document_with_active_path_state"] = (
                original_worker
            )
            outer_state.closed = True
            active_state.reset(outer_token)

        self.assertEqual(len(observed_inner_states), 1)
        self.assertIsNot(observed_inner_states[0], outer_state)
        self.assertTrue(observed_inner_states[0].closed)
        self.assertIsNone(active_state.get())

    def test_v18_reentry_and_inherited_contexts_fail_closed(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen-v18-reentry.json"
            path.write_bytes(MODULE["stable_json"](document))
            baseline = VERIFIER["verify_document"](path, 100000)
            verifier_globals = VERIFIER["verify_factor_base"].__globals__
            original_factor_base = verifier_globals["verify_factor_base"]
            callback_errors = []
            copied_contexts = []
            callback_started = False

            def verify_factor_base_with_adversarial_reentry(*args, **kwargs):
                nonlocal callback_started
                if not callback_started:
                    callback_started = True
                    try:
                        VERIFIER["_verify_document_with_active_path_state"](
                            path, 100000
                        )
                    except Exception as error:
                        callback_errors.append(error)
                    copied = contextvars.copy_context()
                    copied_contexts.append(copied)
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(
                            copied.run,
                            VERIFIER["registered_curve_bundle"],
                            5,
                            101,
                        )
                        try:
                            future.result(timeout=10)
                        except Exception as error:
                            callback_errors.append(error)
                return original_factor_base(*args, **kwargs)

            verifier_globals["verify_factor_base"] = (
                verify_factor_base_with_adversarial_reentry
            )
            try:
                outer = VERIFIER["verify_document"](path, 100000)
            finally:
                verifier_globals["verify_factor_base"] = original_factor_base

        self.assertTrue(callback_started)
        self.assertEqual(outer, baseline)
        self.assertEqual(len(callback_errors), 2)
        self.assertIsInstance(callback_errors[0], RuntimeError)
        self.assertIn("re-entrant path verification", str(callback_errors[0]))
        self.assertIsInstance(callback_errors[1], PermissionError)
        self.assertIn("another thread", str(callback_errors[1]))
        with self.assertRaisesRegex(PermissionError, "state is closed"):
            copied_contexts[0].run(
                VERIFIER["registered_curve_bundle"],
                5,
                101,
            )
        self.assertIsNone(
            verifier_globals["_ACTIVE_VERIFICATION_STATE"].get()
        )

    def test_v18_output_receipt_is_descriptor_bound_and_no_overwrite(self) -> None:
        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"])
        directory = Path(
            tempfile.mkdtemp(prefix="v18-output-", dir=development_root)
        )
        try:
            successful = VERIFIER["output_path"](directory / "successful.json")
            publication = VERIFIER["write_json_exclusive"](
                successful, {"valid": True}
            )
            receipt = VERIFIER["publication_receipt_path"](successful)
            self.assertTrue(publication["accepted"])
            self.assertEqual(publication["status"], "accepted")
            self.assertEqual(
                VERIFIER["publication_status"](successful)["status"],
                "accepted",
            )
            standalone_status = independent_publication_status(successful)
            self.assertTrue(standalone_status["accepted"])
            self.assertEqual(
                standalone_status["publication_id"],
                publication["publication_id"],
            )
            self.assertEqual(
                standalone_status["receipt_sha256"],
                publication["receipt_sha256"],
            )
            self.assertEqual(
                successful.read_bytes(),
                VERIFIER["stable_bytes"]({"valid": True}) + b"\n",
            )
            successful_receipt = receipt.read_bytes()
            with self.assertRaises(FileExistsError):
                VERIFIER["write_json_exclusive"](successful, {"valid": False})
            self.assertEqual(
                successful.read_bytes(),
                VERIFIER["stable_bytes"]({"valid": True}) + b"\n",
            )
            self.assertEqual(receipt.read_bytes(), successful_receipt)

            raced = VERIFIER["output_path"](directory / "raced.json")
            writer_globals = VERIFIER["write_json_exclusive"].__globals__
            original_publish = writer_globals["_publish_no_replace"]

            def racing_publish(*args, **kwargs):
                raced.write_bytes(b"racer-owned\n")
                return original_publish(*args, **kwargs)

            writer_globals["_publish_no_replace"] = racing_publish
            try:
                with self.assertRaises(FileExistsError):
                    VERIFIER["write_json_exclusive"](raced, {"valid": True})
            finally:
                writer_globals["_publish_no_replace"] = original_publish
            self.assertEqual(raced.read_bytes(), b"racer-owned\n")
            self.assertEqual(
                VERIFIER["publication_status"](raced)["status"],
                "unaccepted_orphan",
            )
            self.assertEqual(
                list(directory.glob(".*.unpublished")),
                [],
            )

            interrupted = VERIFIER["output_path"](
                directory / "interrupted.json"
            )
            original_write_all = writer_globals["_write_all"]

            def unsupported_publish(*_args, **_kwargs):
                raise OSError(
                    writer_globals["errno"].ENOTSUP,
                    "forced no-rename filesystem",
                )

            write_calls = 0

            def partial_write(fd, payload):
                nonlocal write_calls
                write_calls += 1
                if write_calls == 1:
                    return original_write_all(fd, payload)
                writer_globals["os"].write(fd, payload[:7])
                raise OSError("injected interrupted destination write")

            writer_globals["_publish_no_replace"] = unsupported_publish
            writer_globals["_write_all"] = partial_write
            try:
                with self.assertRaisesRegex(
                    OSError, "interrupted destination write"
                ):
                    VERIFIER["write_json_exclusive"](
                        interrupted, {"valid": True}
                    )
            finally:
                writer_globals["_publish_no_replace"] = original_publish
                writer_globals["_write_all"] = original_write_all
            self.assertEqual(write_calls, 2)
            interrupted_bytes = interrupted.read_bytes()
            self.assertEqual(len(interrupted_bytes), 7)
            self.assertEqual(
                VERIFIER["publication_status"](interrupted)["status"],
                "unaccepted_orphan",
            )
            with self.assertRaises(FileExistsError):
                VERIFIER["write_json_exclusive"](
                    interrupted, {"valid": False}
                )
            self.assertEqual(interrupted.read_bytes(), interrupted_bytes)
            self.assertEqual(
                list(directory.glob(".*.unpublished")),
                [],
            )

            interrupted_receipt = VERIFIER["output_path"](
                directory / "interrupted-receipt.json"
            )
            publish_calls = 0
            write_calls = 0

            def receipt_fallback_publish(*args, **kwargs):
                nonlocal publish_calls
                publish_calls += 1
                if publish_calls == 2:
                    raise OSError(
                        writer_globals["errno"].ENOTSUP,
                        "forced receipt fallback",
                    )
                parent_fd, temporary_name, destination_name = args
                writer_globals["os"].rename(
                    temporary_name,
                    destination_name,
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                )
                return "injected_no_replace_rename", False

            def partial_receipt_write(fd, payload):
                nonlocal write_calls
                write_calls += 1
                if write_calls < 3:
                    return original_write_all(fd, payload)
                writer_globals["os"].write(fd, payload[:9])
                raise OSError("injected interrupted receipt write")

            writer_globals["_publish_no_replace"] = receipt_fallback_publish
            writer_globals["_write_all"] = partial_receipt_write
            try:
                with self.assertRaisesRegex(
                    OSError, "interrupted receipt write"
                ):
                    VERIFIER["write_json_exclusive"](
                        interrupted_receipt, {"valid": True}
                    )
            finally:
                writer_globals["_publish_no_replace"] = original_publish
                writer_globals["_write_all"] = original_write_all
            self.assertEqual(publish_calls, 2)
            self.assertEqual(write_calls, 3)
            self.assertEqual(
                VERIFIER["publication_status"](interrupted_receipt)["status"],
                "unaccepted_invalid_receipt",
            )

            real_parent = directory / "real-parent"
            real_parent.mkdir()
            symlink_parent = directory / "symlink-parent"
            symlink_parent.symlink_to(real_parent, target_is_directory=True)
            blocked = VERIFIER["output_path"](
                symlink_parent / "must-not-publish.json"
            )
            with self.assertRaises(OSError):
                VERIFIER["write_json_exclusive"](blocked, {"valid": True})
            self.assertEqual(
                VERIFIER["publication_status"](blocked)["status"],
                "unaccepted_path",
            )
            with self.assertRaises(OSError):
                VERIFIER["_open_output_parent"](blocked, create_missing=False)
            self.assertFalse((real_parent / "must-not-publish.json").exists())

            successful.write_bytes(b"tampered\n")
            self.assertEqual(
                VERIFIER["publication_status"](successful)["status"],
                "unaccepted_receipt_mismatch",
            )
            self.assertEqual(
                independent_publication_status(successful)["status"],
                "unaccepted_receipt_mismatch",
            )
        finally:
            shutil.rmtree(directory)

    def test_v18_post_commit_fsync_failure_returns_accepted_with_warning(
        self,
    ) -> None:
        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"])
        directory = Path(
            tempfile.mkdtemp(prefix="v18-fsync-", dir=development_root)
        )
        try:
            destination = VERIFIER["output_path"](directory / "fsync.json")
            writer_globals = VERIFIER["write_json_exclusive"].__globals__
            original_fsync = writer_globals["os"].fsync

            def failing_directory_fsync(descriptor):
                observed = writer_globals["os"].fstat(descriptor)
                if writer_globals["stat"].S_ISDIR(observed.st_mode):
                    raise OSError(writer_globals["errno"].EIO, "injected directory fsync")
                return original_fsync(descriptor)

            writer_globals["os"].fsync = failing_directory_fsync
            try:
                publication = VERIFIER["write_json_exclusive"](
                    destination, {"valid": True}
                )
            finally:
                writer_globals["os"].fsync = original_fsync

            self.assertTrue(publication["accepted"])
            self.assertEqual(publication["status"], "accepted")
            self.assertEqual(
                [warning["stage"] for warning in publication["warnings"]],
                ["published_parent_fsync", "published_parent_fsync"],
            )
            self.assertTrue(
                VERIFIER["publication_status"](destination)["accepted"]
            )
        finally:
            shutil.rmtree(directory)

    def test_v18_publication_path_policy_is_exact_across_entries(
        self,
    ) -> None:
        class StringPathLike:
            def __init__(self, value):
                self.value = value

            def __fspath__(self):
                return self.value

        class BytesPathLike:
            def __init__(self, value):
                self.value = value

            def __fspath__(self):
                return os.fsencode(self.value)

        class StringSubclass(str):
            pass

        class SideEffectStringPathLike:
            def __init__(self, value, marker):
                self.value = value
                self.marker = marker

            def __fspath__(self):
                self.marker.write_bytes(b"caller string callback\n")
                return self.value

        class SideEffectBytesPathLike:
            def __init__(self, value, candidate):
                self.value = value
                self.candidate = candidate

            def __fspath__(self):
                self.candidate.write_bytes(b"caller bytes callback\n")
                return os.fsencode(self.value)

        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"])
        directory = Path(
            tempfile.mkdtemp(prefix="v18-normalized-alias-", dir=development_root)
        )
        try:
            normalized = directory / "nested" / "alias.json"
            normalized_string = os.fspath(normalized)
            raw_alias = f"{os.fspath(directory)}/./nested////alias.json"
            aliases = {
                "absolute exact str": normalized_string,
                "pathlib Path": normalized,
                "custom string PathLike": StringPathLike(normalized_string),
                "dot": f"{os.fspath(directory)}/./nested/alias.json",
                "internal double separator": (
                    f"{os.fspath(directory)}/nested//alias.json"
                ),
                "internal four separators": (
                    f"{os.fspath(directory)}/nested////alias.json"
                ),
                "three leading separators": (
                    f"///{normalized_string.lstrip('/')}"
                ),
                "four leading separators": (
                    f"////{normalized_string.lstrip('/')}"
                ),
                "seven leading separators": (
                    f"///////{normalized_string.lstrip('/')}"
                ),
                "combined raw alias": raw_alias,
            }
            expected_receipt = normalized.with_name(
                VERIFIER["_publication_receipt_name"](normalized.name)
            )
            for name, alias in aliases.items():
                with self.subTest(admitted=name):
                    self.assertEqual(VERIFIER["output_path"](alias), normalized)
                    self.assertEqual(
                        VERIFIER["publication_receipt_path"](alias),
                        expected_receipt,
                    )
            self.assertEqual(
                VERIFIER["publication_status"](raw_alias)["status"],
                "absent",
            )
            publication = VERIFIER["write_json_exclusive"](
                raw_alias, {"valid": True}
            )
            self.assertTrue(publication["accepted"])
            self.assertEqual(
                publication["destination_relative_path"],
                normalized.relative_to(development_root).as_posix(),
            )
            for name, alias in aliases.items():
                with self.subTest(accepted=name):
                    self.assertEqual(
                        VERIFIER["publication_status"](alias)["publication_id"],
                        publication["publication_id"],
                    )
                    self.assertEqual(
                        independent_publication_status(alias)["publication_id"],
                        publication["publication_id"],
                    )
                    parent_fd, destination_name = VERIFIER[
                        "_open_output_parent"
                    ](alias, create_missing=False)
                    try:
                        self.assertEqual(destination_name, normalized.name)
                    finally:
                        os.close(parent_fd)

            unique = f"{os.getpid()}-{threading.get_ident()}"
            leading_double = f"//{normalized_string.lstrip('/')}"
            escaped = (
                f"{os.fspath(development_root)}/../v18-escaped-{unique}.json"
            )
            outside = Path("/private/tmp") / (
                f"v18-outside-{unique}.json"
            )
            terminal = f"{os.fspath(directory)}/v18-terminal-{unique}.json/"
            terminal_dot = (
                f"{os.fspath(directory)}/v18-terminal-dot-{unique}.json/."
            )
            relative_in_root = (
                "experiments/EXP-SGCP-EMBED-002/development/"
                f"v18-relative-{unique}.json"
            )
            relative_escape = f"../v18-relative-escape-{unique}.json"
            null_path = f"{os.fspath(directory)}/v18-null-{unique}\x00.json"
            byte_path = os.fsencode(
                f"{os.fspath(directory)}/v18-bytes-{unique}.json"
            )
            cli_parent = directory / f"v18-cli-terminal-{unique}"
            cli_dot_parent = directory / f"v18-cli-dot-{unique}"
            cli_terminal = f"{os.fspath(cli_parent)}/output.json/"
            cli_terminal_dot = f"{os.fspath(cli_dot_parent)}/output.json/."
            for raw_cli_output in (cli_terminal, cli_terminal_dot):
                with self.subTest(cli_preserves=raw_cli_output):
                    verifier_args = VERIFIER["parse_args"](
                        [
                            "--input",
                            os.fspath(SOURCE),
                            "--output",
                            raw_cli_output,
                        ]
                    )
                    producer_args = MODULE["parse_args"](
                        ["--output", raw_cli_output]
                    )
                    self.assertIs(type(verifier_args.output), str)
                    self.assertIs(type(producer_args.output), str)
                    self.assertEqual(verifier_args.output, raw_cli_output)
                    self.assertEqual(producer_args.output, raw_cli_output)

            main_globals = VERIFIER["main"].__globals__
            original_verify_document = main_globals["verify_document"]
            original_write_json_exclusive = main_globals["write_json_exclusive"]
            forbidden_calls = []

            def forbidden_main_stage(*args, **kwargs):
                forbidden_calls.append((args, kwargs))
                raise AssertionError("output preflight did not run first")

            main_globals["verify_document"] = forbidden_main_stage
            main_globals["write_json_exclusive"] = forbidden_main_stage
            try:
                for raw_cli_output, pattern in (
                    (cli_terminal, "terminal separator"),
                    (cli_terminal_dot, "terminal dot component"),
                ):
                    with self.subTest(cli_preflight=raw_cli_output):
                        with self.assertRaisesRegex(ValueError, pattern):
                            VERIFIER["main"](
                                [
                                    "--input",
                                    os.fspath(SOURCE),
                                    "--output",
                                    raw_cli_output,
                                ]
                            )
            finally:
                main_globals["verify_document"] = original_verify_document
                main_globals[
                    "write_json_exclusive"
                ] = original_write_json_exclusive
            self.assertEqual(forbidden_calls, [])
            self.assertFalse(cli_parent.exists())
            self.assertFalse(cli_dot_parent.exists())

            valid_cli_parent = directory / f"v18-cli-valid-{unique}"
            valid_cli_output = (
                f"{os.fspath(valid_cli_parent)}/./nested////output.json"
            )
            observed_writer_paths = []

            def fake_verify_document(path, maximum_nodes):
                self.assertEqual(path, SOURCE)
                self.assertEqual(maximum_nodes, 5000000)
                return {
                    "valid": True,
                    "row_count": 1,
                    "valid_row_count": 1,
                    "total_replay_nodes": 0,
                    "total_primary_nodes": 0,
                }

            def fake_write_json_exclusive(path, report):
                observed_writer_paths.append(path)
                self.assertTrue(report["valid"])
                return {"accepted": True}

            main_globals["verify_document"] = fake_verify_document
            main_globals["write_json_exclusive"] = fake_write_json_exclusive
            try:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(
                        VERIFIER["main"](
                            [
                                "--input",
                                os.fspath(SOURCE),
                                "--output",
                                valid_cli_output,
                            ]
                        ),
                        0,
                    )
            finally:
                main_globals["verify_document"] = original_verify_document
                main_globals[
                    "write_json_exclusive"
                ] = original_write_json_exclusive
            self.assertEqual(observed_writer_paths, [valid_cli_output])
            self.assertFalse(valid_cli_parent.exists())

            string_callback_marker = (
                directory / f"v18-caller-string-marker-{unique}"
            )
            string_callback_destination = (
                directory / f"v18-caller-string-destination-{unique}.json"
            )
            self.assertEqual(
                VERIFIER["output_path"](
                    SideEffectStringPathLike(
                        os.fspath(string_callback_destination),
                        string_callback_marker,
                    )
                ),
                string_callback_destination,
            )
            self.assertTrue(string_callback_marker.is_file())
            self.assertFalse(string_callback_destination.exists())

            bytes_callback_destination = (
                directory / f"v18-caller-bytes-destination-{unique}.json"
            )
            with self.assertRaisesRegex(TypeError, "exact str"):
                VERIFIER["output_path"](
                    SideEffectBytesPathLike(
                        os.fspath(bytes_callback_destination),
                        bytes_callback_destination,
                    )
                )
            self.assertEqual(
                bytes_callback_destination.read_bytes(),
                b"caller bytes callback\n",
            )
            bytes_callback_destination.unlink()

            rejected = {
                "leading double separator": (
                    leading_double,
                    ValueError,
                    "double-separator anchor",
                ),
                "parent traversal": (
                    escaped,
                    ValueError,
                    "parent traversal",
                ),
                "development root": (
                    development_root,
                    ValueError,
                    "below the development directory",
                ),
                "outside root": (
                    outside,
                    ValueError,
                    "below the development directory",
                ),
                "relative in-root spelling": (
                    relative_in_root,
                    ValueError,
                    "absolute POSIX path",
                ),
                "relative escape spelling": (
                    relative_escape,
                    ValueError,
                    "absolute POSIX path",
                ),
                "terminal separator": (
                    terminal,
                    ValueError,
                    "terminal separator",
                ),
                "terminal dot component": (
                    terminal_dot,
                    ValueError,
                    "terminal dot component",
                ),
                "empty string": ("", ValueError, "is empty"),
                "embedded null": (null_path, ValueError, "null byte"),
                "direct bytes": (byte_path, TypeError, "exact str"),
                "byte-valued PathLike": (
                    BytesPathLike(os.fsdecode(byte_path)),
                    TypeError,
                    "exact str",
                ),
                "unsupported null object": (
                    None,
                    TypeError,
                    "str or string-valued",
                ),
                "str subclass": (
                    StringSubclass(normalized_string),
                    TypeError,
                    "exact str",
                ),
            }
            for name, (candidate, error_type, pattern) in rejected.items():
                with self.subTest(rejected=name):
                    with self.assertRaisesRegex(error_type, pattern):
                        VERIFIER["output_path"](candidate)
                    with self.assertRaisesRegex(error_type, pattern):
                        VERIFIER["publication_receipt_path"](candidate)
                    self.assertEqual(
                        VERIFIER["publication_status"](candidate)["status"],
                        "unaccepted_path",
                    )
                    self.assertEqual(
                        independent_publication_status(candidate)["status"],
                        "unaccepted_path",
                    )
                    with self.assertRaisesRegex(error_type, pattern):
                        VERIFIER["write_json_exclusive"](
                            candidate, {"valid": True}
                        )
                    with self.assertRaisesRegex(error_type, pattern):
                        VERIFIER["_open_output_parent"](candidate)

            self.assertFalse(outside.exists())
            normalized_escape = Path(os.path.abspath(escaped))
            self.assertFalse(normalized_escape.exists())
            self.assertFalse(Path(terminal.rstrip("/")).exists())
            self.assertFalse(Path(terminal_dot[:-2]).exists())
        finally:
            shutil.rmtree(directory)

    def test_v18_stale_receipt_blocks_identical_payload_retry(self) -> None:
        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"])
        directory = Path(
            tempfile.mkdtemp(prefix="v18-stale-receipt-", dir=development_root)
        )
        try:
            destination = directory / "stale.json"
            first = VERIFIER["write_json_exclusive"](
                destination, {"valid": True}
            )
            receipt = VERIFIER["publication_receipt_path"](destination)
            receipt_bytes = receipt.read_bytes()
            destination.unlink()

            with self.assertRaises(FileExistsError):
                VERIFIER["write_json_exclusive"](
                    destination, {"valid": True}
                )
            self.assertFalse(destination.exists())
            self.assertEqual(receipt.read_bytes(), receipt_bytes)
            self.assertEqual(
                VERIFIER["publication_status"](destination)["status"],
                "unaccepted_receipt_mismatch",
            )
            self.assertEqual(
                independent_publication_status(destination)["status"],
                "unaccepted_receipt_mismatch",
            )
            self.assertTrue(first["publication_id"])
        finally:
            shutil.rmtree(directory)

    def test_v18_receipt_attempt_and_path_bindings_are_explicit(self) -> None:
        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"]).resolve(strict=True)
        directory = Path(
            tempfile.mkdtemp(prefix="v18-receipt-binding-", dir=development_root)
        )
        try:
            destination = directory / "binding.json"
            publication = VERIFIER["write_json_exclusive"](
                destination, {"valid": True}
            )
            receipt_path = VERIFIER["publication_receipt_path"](destination)
            original_receipt = json.loads(
                receipt_path.read_text(encoding="ascii")
            )

            def independently_resign(receipt):
                payload = dict(receipt)
                payload.pop("receipt_sha256", None)
                receipt["receipt_sha256"] = hashlib.sha256(
                    json.dumps(
                        payload,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=True,
                        allow_nan=False,
                    ).encode("ascii")
                ).hexdigest()
                receipt_path.write_bytes(
                    json.dumps(
                        receipt,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=True,
                        allow_nan=False,
                    ).encode("ascii")
                    + b"\n"
                )

            forged_attempt = copy.deepcopy(original_receipt)
            forged_attempt["publication_id"] = (
                "f" * 64
                if publication["publication_id"] != "f" * 64
                else "e" * 64
            )
            independently_resign(forged_attempt)
            self.assertTrue(VERIFIER["publication_status"](destination)["accepted"])
            self.assertTrue(independent_publication_status(destination)["accepted"])

            parent_fd, destination_name = VERIFIER["_open_output_parent"](
                VERIFIER["output_path"](destination),
                create_missing=False,
            )
            try:
                exact_attempt = VERIFIER["_publication_status_at"](
                    parent_fd,
                    destination_name,
                    destination.relative_to(development_root).as_posix(),
                    publication["publication_id"],
                )
            finally:
                os.close(parent_fd)
            self.assertEqual(
                exact_attempt["status"],
                "unaccepted_attempt_mismatch",
            )

            wrong_path = copy.deepcopy(original_receipt)
            wrong_path["destination_relative_path"] = "other/binding.json"
            independently_resign(wrong_path)
            self.assertEqual(
                VERIFIER["publication_status"](destination)["status"],
                "unaccepted_invalid_receipt",
            )
            self.assertEqual(
                independent_publication_status(destination)["status"],
                "unaccepted_invalid_receipt",
            )

            wrong_type = copy.deepcopy(original_receipt)
            wrong_type["payload_bytes"] = False
            independently_resign(wrong_type)
            self.assertEqual(
                VERIFIER["publication_status"](destination)["status"],
                "unaccepted_invalid_receipt",
            )
            self.assertEqual(
                independent_publication_status(destination)["status"],
                "unaccepted_invalid_receipt",
            )
        finally:
            shutil.rmtree(directory)

    def test_v18_concurrent_same_destination_attributes_only_winning_attempt(
        self,
    ) -> None:
        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"])
        directory = Path(
            tempfile.mkdtemp(prefix="v18-concurrent-output-", dir=development_root)
        )
        destination = directory / "shared.json"
        writer_globals = VERIFIER["write_json_exclusive"].__globals__
        original_preflight = writer_globals["_require_publication_names_absent"]
        original_token_hex = writer_globals["secrets"].token_hex
        barrier = threading.Barrier(2)
        identifier_lock = threading.Lock()
        identifiers = {}

        def synchronized_preflight(parent_fd, names):
            original_preflight(parent_fd, names)
            barrier.wait(timeout=10)

        def deterministic_publication_id(length):
            if length != 32:
                return original_token_hex(length)
            thread_id = threading.get_ident()
            with identifier_lock:
                if thread_id not in identifiers:
                    identifiers[thread_id] = (
                        "a" * 64 if not identifiers else "b" * 64
                    )
                return identifiers[thread_id]

        def attempt():
            thread_id = threading.get_ident()
            try:
                result = VERIFIER["write_json_exclusive"](
                    destination, {"valid": True}
                )
                return thread_id, "accepted", result
            except Exception as error:
                return thread_id, "failed", error

        writer_globals["_require_publication_names_absent"] = (
            synchronized_preflight
        )
        writer_globals["secrets"].token_hex = deterministic_publication_id
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                outcomes = [
                    future.result(timeout=30)
                    for future in [executor.submit(attempt) for _ in range(2)]
                ]
        finally:
            writer_globals["_require_publication_names_absent"] = (
                original_preflight
            )
            writer_globals["secrets"].token_hex = original_token_hex

        try:
            accepted = [outcome for outcome in outcomes if outcome[1] == "accepted"]
            failed = [outcome for outcome in outcomes if outcome[1] == "failed"]
            self.assertEqual(len(accepted), 1, outcomes)
            self.assertEqual(len(failed), 1, outcomes)
            self.assertIsInstance(failed[0][2], FileExistsError)
            status = VERIFIER["publication_status"](destination)
            self.assertTrue(status["accepted"])
            self.assertEqual(
                status["publication_id"],
                accepted[0][2]["publication_id"],
            )
            self.assertNotEqual(
                status["publication_id"],
                identifiers[failed[0][0]],
            )
            self.assertEqual(
                independent_publication_status(destination)["publication_id"],
                status["publication_id"],
            )
        finally:
            shutil.rmtree(directory)

    def test_v18_receipt_commit_exceptions_reconcile_exact_attempt(self) -> None:
        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"])
        writer_globals = VERIFIER["write_json_exclusive"].__globals__

        directory = Path(
            tempfile.mkdtemp(prefix="v18-rename-reconcile-")
        ).resolve(strict=True)
        original_publish = writer_globals["_publish_no_replace"]
        original_development_root = writer_globals["DEVELOPMENT_ROOT"]
        publish_calls = 0

        def publish_then_raise(*args, **kwargs):
            nonlocal publish_calls
            result = original_publish(*args, **kwargs)
            publish_calls += 1
            if publish_calls == 2:
                raise RuntimeError("injected exception after receipt publish")
            return result

        writer_globals["_publish_no_replace"] = publish_then_raise
        writer_globals["DEVELOPMENT_ROOT"] = directory
        try:
            destination = directory / "rename.json"
            publication = VERIFIER["write_json_exclusive"](
                destination, {"valid": True}
            )
            reconciled_status = VERIFIER["publication_status"](destination)
        finally:
            writer_globals["_publish_no_replace"] = original_publish
            writer_globals["DEVELOPMENT_ROOT"] = original_development_root
        try:
            self.assertEqual(publish_calls, 2)
            self.assertEqual(
                publication["receipt_method"],
                "reconciled_after_receipt_exception",
            )
            self.assertIn(
                "receipt_publication_exception_reconciled",
                [warning["stage"] for warning in publication["warnings"]],
            )
            self.assertEqual(
                reconciled_status["publication_id"],
                publication["publication_id"],
            )
        finally:
            shutil.rmtree(directory)

        directory = Path(
            tempfile.mkdtemp(prefix="v18-link-reconcile-")
        ).resolve(strict=True)
        original_development_root = writer_globals["DEVELOPMENT_ROOT"]
        original_cdll = writer_globals["ctypes"].CDLL
        original_link = writer_globals["os"].link
        link_calls = 0

        def no_rename_library(*_args, **_kwargs):
            return object()

        def link_then_raise(*args, **kwargs):
            nonlocal link_calls
            result = original_link(*args, **kwargs)
            link_calls += 1
            if link_calls == 2:
                raise RuntimeError("injected exception after receipt hard link")
            return result

        writer_globals["ctypes"].CDLL = no_rename_library
        writer_globals["os"].link = link_then_raise
        writer_globals["DEVELOPMENT_ROOT"] = directory
        try:
            destination = directory / "link.json"
            publication = VERIFIER["write_json_exclusive"](
                destination, {"valid": True}
            )
            reconciled_status = VERIFIER["publication_status"](destination)
        finally:
            writer_globals["ctypes"].CDLL = original_cdll
            writer_globals["os"].link = original_link
            writer_globals["DEVELOPMENT_ROOT"] = original_development_root
        try:
            self.assertEqual(link_calls, 2)
            self.assertEqual(
                publication["receipt_method"],
                "reconciled_after_receipt_exception",
            )
            self.assertTrue(reconciled_status["accepted"])
            self.assertEqual(
                reconciled_status["publication_id"],
                publication["publication_id"],
            )
        finally:
            shutil.rmtree(directory)

        directory = Path(
            tempfile.mkdtemp(prefix="v18-direct-reconcile-", dir=development_root)
        )
        original_publish = writer_globals["_publish_no_replace"]
        original_direct = writer_globals["_write_destination_exclusive"]
        direct_calls = 0

        def unsupported_publish(*_args, **_kwargs):
            raise OSError(
                writer_globals["errno"].ENOTSUP,
                "forced direct publication",
            )

        def direct_then_raise(*args, **kwargs):
            nonlocal direct_calls
            result = original_direct(*args, **kwargs)
            direct_calls += 1
            if direct_calls == 2:
                raise RuntimeError("injected exception after direct receipt publish")
            return result

        writer_globals["_publish_no_replace"] = unsupported_publish
        writer_globals["_write_destination_exclusive"] = direct_then_raise
        try:
            destination = directory / "direct.json"
            publication = VERIFIER["write_json_exclusive"](
                destination, {"valid": True}
            )
        finally:
            writer_globals["_publish_no_replace"] = original_publish
            writer_globals["_write_destination_exclusive"] = original_direct
        try:
            self.assertEqual(direct_calls, 2)
            self.assertEqual(
                publication["receipt_method"],
                "reconciled_after_receipt_exception",
            )
            self.assertEqual(
                VERIFIER["publication_status"](destination)["publication_id"],
                publication["publication_id"],
            )
        finally:
            shutil.rmtree(directory)

    def test_v18_direct_write_inode_mismatch_fails_closed(self) -> None:
        development_root = Path(VERIFIER["DEVELOPMENT_ROOT"])
        directory = Path(
            tempfile.mkdtemp(prefix="v18-direct-mismatch-", dir=development_root)
        )
        writer_globals = VERIFIER["write_json_exclusive"].__globals__
        original_publish = writer_globals["_publish_no_replace"]
        original_write_all = writer_globals["_write_all"]
        write_calls = 0

        def unsupported_publish(*_args, **_kwargs):
            raise OSError(
                writer_globals["errno"].ENOTSUP,
                "forced direct publication",
            )

        def incomplete_direct_receipt(fd, payload):
            nonlocal write_calls
            write_calls += 1
            if write_calls == 4:
                writer_globals["os"].write(fd, payload[:-1])
                return
            return original_write_all(fd, payload)

        writer_globals["_publish_no_replace"] = unsupported_publish
        writer_globals["_write_all"] = incomplete_direct_receipt
        destination = directory / "incomplete.json"
        try:
            with self.assertRaisesRegex(
                OSError, "expected regular-file size"
            ):
                VERIFIER["write_json_exclusive"](
                    destination, {"valid": True}
                )
        finally:
            writer_globals["_publish_no_replace"] = original_publish
            writer_globals["_write_all"] = original_write_all
        try:
            self.assertEqual(write_calls, 4)
            self.assertEqual(
                VERIFIER["publication_status"](destination)["status"],
                "unaccepted_invalid_receipt",
            )
            self.assertEqual(
                independent_publication_status(destination)["status"],
                "unaccepted_invalid_receipt",
            )
        finally:
            shutil.rmtree(directory)

    def test_v18_hard_link_cleanup_failure_is_accepted_and_reported(self) -> None:
        directory = Path(
            tempfile.mkdtemp(prefix="v18-link-cleanup-")
        ).resolve(strict=True)
        writer_globals = VERIFIER["write_json_exclusive"].__globals__
        original_development_root = writer_globals["DEVELOPMENT_ROOT"]
        try:
            writer_globals["DEVELOPMENT_ROOT"] = directory
            destination = VERIFIER["output_path"](directory / "linked.json")
            original_cdll = writer_globals["ctypes"].CDLL
            original_link = writer_globals["os"].link
            original_unlink = writer_globals["os"].unlink
            cleanup_failed = False
            link_calls = 0

            def no_rename_library(*_args, **_kwargs):
                return object()

            def counted_link(*args, **kwargs):
                nonlocal link_calls
                link_calls += 1
                return original_link(*args, **kwargs)

            def fail_first_temporary_cleanup(path, *args, **kwargs):
                nonlocal cleanup_failed
                if not cleanup_failed and str(path).endswith(".unpublished"):
                    cleanup_failed = True
                    raise OSError(
                        writer_globals["errno"].EIO,
                        "injected temporary unlink failure",
                    )
                return original_unlink(path, *args, **kwargs)

            writer_globals["ctypes"].CDLL = no_rename_library
            writer_globals["os"].link = counted_link
            writer_globals["os"].unlink = fail_first_temporary_cleanup
            try:
                publication = VERIFIER["write_json_exclusive"](
                    destination, {"valid": True}
                )
            finally:
                writer_globals["ctypes"].CDLL = original_cdll
                writer_globals["os"].link = original_link
                writer_globals["os"].unlink = original_unlink

            self.assertTrue(cleanup_failed)
            self.assertEqual(link_calls, 2)
            self.assertTrue(publication["accepted"])
            self.assertEqual(publication["data_method"], "hard_link")
            self.assertEqual(publication["receipt_method"], "hard_link")
            self.assertIn(
                "hard_link_temporary_cleanup",
                [warning["stage"] for warning in publication["warnings"]],
            )
            self.assertTrue(VERIFIER["publication_status"](destination)["accepted"])
            self.assertGreaterEqual(
                len(list(directory.glob(".*.unpublished"))),
                1,
            )
        finally:
            writer_globals["DEVELOPMENT_ROOT"] = original_development_root
            shutil.rmtree(directory)

    def test_main_refuses_canonical_mode(self) -> None:
        with self.assertRaises(PermissionError):
            MODULE["main"](["--output", str(DEVELOPMENT_SENTINEL)])
        with self.assertRaises(PermissionError):
            MODULE["main"](
                ["--development", "--output", str(DEVELOPMENT_SENTINEL)]
            )


DEVELOPMENT_SENTINEL = (
    REPO_ROOT
    / "experiments"
    / "EXP-SGCP-EMBED-002"
    / "development"
    / "must-not-exist.json"
)


if __name__ == "__main__":
    unittest.main()
