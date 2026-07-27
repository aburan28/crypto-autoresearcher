#!/usr/bin/env sage -python
"""Preflight exact root-free quadratic divisors on the frozen PO71 stream."""

from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
import math
import os
import resource
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, Matrix, PolynomialRing, identity_matrix, vector


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1496_root_free_quadratic_divisor.md"
OUT = STATE_DIR / "p1496_root_free_quadratic_divisor.json"
NOTE = RESEARCH_DIR / "p1496_root_free_quadratic_divisor.md"

PO71_CONTRACT = ROOT / "research/PO_transfer_071_rank_balanced_core_walk_contract.md"
PO71_RESULT = ROOT / "experiments/ecdlp_isogeny/po_transfer_071_rank_balanced_core_walk.json"
PO71_WALK = ROOT / "experiments/ecdlp_isogeny/po_transfer_071_independent_verify.sage.py"
PO71_VERIFY_RESULT = ROOT / "experiments/ecdlp_isogeny/po_transfer_071_independent_verify.json"
PO70_SOURCE = ROOT / "experiments/ecdlp_isogeny/po_transfer_070_shared_core_pencil_bundle.sage"
PO70_DIRECT = ROOT / "experiments/ecdlp_isogeny/po_transfer_070_independent_verify.sage"
PO65_SOURCE = ROOT / "experiments/ecdlp_isogeny/po_transfer_065_reusable_target_query.sage"
PO65_DIRECT = ROOT / "experiments/ecdlp_isogeny/po_transfer_065_independent_verify.sage"
PO55_RESULT = ROOT / "experiments/ecdlp_isogeny/po_transfer_055_three_size_scaling.json"
PO54_ORACLE = ROOT / "experiments/ecdlp_isogeny/po_transfer_054_independent_verify.sage"
PO73_RESULT = ROOT / "experiments/ecdlp_isogeny/po_transfer_073_aggregate_missing_divisor_lp.json"

SCHEMA = "ecdlp.p1496_root_free_quadratic_divisor.v1"
NULL_REPLICATES = 32
PASSES = 4
EXPECTED = {
    CONTRACT: "c19d39d45a196e6c9cd7212ed28eadad705ff35dce1329e323327903ee0c485f",
    PO71_CONTRACT: "bd4300af7ad9f5eb14132434ec86880e31ef6aa53aa8e1cdc510a56aa3aaf304",
    PO71_RESULT: "79579cbe2655287286e7c6ac099f530bd06744c95b8555ef13a296b04a9f3b05",
    PO71_WALK: "a3568a0a023c1bb8a6056c33ddef8cbce6c7c790d94e9fb11a55d5d1dc8ef092",
    PO71_VERIFY_RESULT: "a57f3b5c8c510824810b601aa18360f0edbdbe23b83b5e1e803077b4df8556db",
    PO70_SOURCE: "f30dd608f902009002cb9827c8bf873972f33ad4405fadd38d8051ec600c9109",
    PO70_DIRECT: "081898d59060c1c343d32275c4ed10759850c34f6caf07a3f7e3909e814e86a4",
    PO65_SOURCE: "3d6eb9a8ade436f5757d31f0a9702e00fc29551eab4321ca589304ac8d4839b2",
    PO65_DIRECT: "97414a64b4f5b62a7a18dd12a014ad1bfa0df0164d2215b2fd5ceaace0659544",
    PO55_RESULT: "8584c70805314a4aeb6c6770a82936f0b7ac29e509ed2dd90805d59dd43a03ec",
    PO54_ORACLE: "80b8c550d162cfc722d01bf73655a2bbdf77599318ee006a2b4955f239dd76de",
    PO73_RESULT: "3da33a693af1639cd7c6a14f711becdacb6e724cc9ac1216135926b88e2f305b",
}


def compact(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=lambda item: int(item),
    )


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return digest(path.read_bytes())


def relation_hash(records: list[dict[str, Any]]) -> str:
    return digest(compact(records).encode("ascii"))


def load_module(path: Path, name: str) -> Any:
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def raw_point(point: Any) -> tuple[int, int]:
    return int(point[0]), int(point[1])


def raw_label(label: Any) -> tuple[int, int, int]:
    return int(label[0]), int(label[1]), int(label[2])


def polynomial_coefficients(polynomial: Any, length: int) -> list[int]:
    values = list(polynomial.list())
    values.extend([polynomial.base_ring().zero()] * (length - len(values)))
    return [int(value) for value in values[:length]]


def canonical_divisor(u: Any, v: Any) -> tuple[tuple[int, int, int, int], int]:
    u0, u1, _ = polynomial_coefficients(u, 3)
    v0, v1 = polynomial_coefficients(v, 2)
    raw = (u0, u1, v0, v1)
    negative = (u0, u1, int(-v[0]), int(-v[1]))
    if raw <= negative:
        return raw, 1
    return negative, -1


def class_point_from_uv(u: Any, v: Any, curve: Any) -> Any:
    field = u.base_ring()
    coefficients_u = list(u.list()) + [field.zero()] * 3
    coefficients_v = list(v.list()) + [field.zero()] * 2
    u1 = coefficients_u[1]
    v0, v1 = coefficients_v[:2]
    x_sum = v1**2 + u1
    y_sum = -(v1 * x_sum + v0)
    return curve((x_sum, y_sum))


def divisor_from_points(first: Any, second: Any, ring: Any, curve: Any) -> dict[str, Any] | None:
    if first.is_zero() or second.is_zero() or first[0] == second[0]:
        return None
    field = ring.base_ring()
    x = ring.gen()
    x1, y1 = field(first[0]), field(first[1])
    x2, y2 = field(second[0]), field(second[1])
    u = ((x - x1) * (x - x2)).monic()
    slope = (y1 - y2) / (x1 - x2)
    v = ring(y1 - slope * x1 + slope * x)
    label, sign = canonical_divisor(u, v)
    class_point = class_point_from_uv(u, v, curve)
    if class_point != first + second:
        raise RuntimeError("point-built divisor class mismatch")
    return {
        "label": label,
        "sign": sign,
        "u": u,
        "v": v,
        "class_point": class_point,
    }


def root_free_record(
    anchor_index: int,
    core_index: int,
    variant_index: int,
    anchor: list[Any],
    parameter: int,
    residual: set[tuple[int, int]],
    quotient: Any,
    first: Any,
    second: Any,
    factor_base: list[Any],
    curve: Any,
    field: Any,
    frozen: dict[str, Any],
    oracle: Any,
    independent: Any,
) -> tuple[dict[str, Any] | None, str]:
    anchor_points = {raw_point(label) for label in anchor}
    known = anchor_points | residual
    if len(residual) != 3 or len(known) != 10:
        return None, "known_support"
    ring = PolynomialRing(field, f"p1496_x_{field.order()}_{anchor_index}_{parameter}")
    x = ring.gen()
    specialized = oracle.specialize(quotient, field(parameter), ring)
    known_product = ring.one()
    for point in sorted(residual):
        known_product *= x - field(point[0])
    remaining, remainder = specialized.quo_rem(known_product)
    if remainder or remaining.degree() != 2:
        return None, "residual_not_quadratic"
    u = remaining.monic()
    coefficients = vector(
        field,
        [first[index] + field(parameter) * second[index] for index in range(9)],
    )
    curve_polynomial = x**3 + curve.a4() * x + curve.a6()
    norm_a, norm_b = oracle.norm_pair(
        coefficients,
        field,
        ring,
        curve_polynomial,
        field(frozen["gamma"]),
    )
    a_mod = norm_a % u
    b_mod = norm_b % u
    branch_mode = "regular_inverse"
    try:
        inverse_b = b_mod.inverse_mod(u)
        v = (-a_mod * inverse_b) % u
    except (ArithmeticError, ZeroDivisionError, ValueError):
        # A common linear factor of B and u makes both y branches norm zeros.
        # A known point above that root selects the missing opposite branch.
        # This uses only public known x-values and linear division; u is never
        # factored or rooted.
        common = b_mod.gcd(u).monic()
        if common.degree() not in (1, 2):
            return None, "singular_branch_unresolved"
        known_by_x: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for point in sorted(known):
            if common(field(point[0])) == 0:
                known_by_x[int(point[0])].append(point)
        selected = []
        known_factor = ring.one()
        for x_integer, points_above in sorted(known_by_x.items()):
            if len(points_above) != 1:
                return None, "singular_branch_ambiguous_known_fiber"
            known_point = curve(points_above[0])
            selected.append(-known_point)
            known_factor *= x - field(x_integer)
        quotient_common, common_remainder = common.quo_rem(known_factor)
        if common_remainder or quotient_common.degree() != 0:
            return None, "singular_branch_missing_known_root"
        regular_factor, factor_remainder = u.quo_rem(common)
        if factor_remainder:
            return None, "singular_branch_gcd_division_failure"
        if regular_factor.degree() == 1:
            root = -regular_factor[0] / regular_factor[1]
            denominator = b_mod(root)
            if not denominator:
                return None, "singular_branch_regular_denominator_zero"
            y_value = -a_mod(root) / denominator
            selected.append(curve((root, y_value)))
        elif regular_factor.degree() != 0:
            return None, "singular_branch_remaining_degree"
        if len(selected) != 2 or selected[0][0] == selected[1][0]:
            return None, "singular_branch_non_graph_divisor"
        x1, y1 = field(selected[0][0]), field(selected[0][1])
        x2, y2 = field(selected[1][0]), field(selected[1][1])
        slope = (y1 - y2) / (x1 - x2)
        v = ring(y1 - slope * x1 + slope * x)
        branch_mode = "known_linear_singular_branch"
    curve_congruence = (v**2 - curve_polynomial) % u == 0
    norm_congruence = (a_mod + b_mod * v) % u == 0
    if not curve_congruence or not norm_congruence:
        return None, "congruence_failure"
    class_point = class_point_from_uv(u, v, curve)
    known_sum = curve(0)
    for point in sorted(known):
        known_sum += curve(point)
    if class_point != -known_sum:
        return None, "class_failure"
    factor_index = {raw_point(label): index for index, label in enumerate(factor_base)}
    row = independent.row_from_points(known, factor_index, len(factor_base))
    if independent.row_sum(row, factor_base, curve) + class_point != curve(0):
        return None, "row_class_failure"
    label, sign = canonical_divisor(u, v)
    support_points = [list(point) for point in sorted(known)]
    identity = [int(anchor_index), int(parameter)]
    return {
        "anchor_index": int(anchor_index),
        "core_index": int(core_index),
        "variant_index": int(variant_index),
        "parameter": int(parameter),
        "identity": identity,
        "support_hash": digest(compact(support_points).encode("ascii")),
        "support_points": support_points,
        "label": list(label),
        "sign": int(sign),
        "row": [int(value) for value in row],
        "class_point": list(raw_point(class_point)),
        "certificate": {
            "branch_mode": branch_mode,
            "u": polynomial_coefficients(u, 3),
            "v": polynomial_coefficients(v, 2),
            "a_mod_u": polynomial_coefficients(a_mod, 2),
            "b_mod_u": polynomial_coefficients(b_mod, 2),
            "curve_congruence": bool(curve_congruence),
            "norm_congruence": bool(norm_congruence),
        },
    }, "accepted" if branch_mode == "regular_inverse" else "accepted_singular_branch"


def canonical_row(row: list[int], modulus: int) -> tuple[int, ...]:
    reduced = tuple(int(value) % modulus for value in row)
    negative = tuple((-value) % modulus for value in reduced)
    return min(reduced, negative)


def close_divisor_labels(
    records: list[dict[str, Any]],
    factor_base: list[Any],
    curve: Any,
    order: int,
    independent: Any,
) -> dict[str, Any]:
    buckets: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        buckets[tuple(record["label"])].append(record)
    rows: list[list[int]] = []
    closures: list[dict[str, Any]] = []
    keys: set[tuple[int, ...]] = set()
    duplicate_support_skips = 0
    zero_row_skips = 0
    replay_failures = 0
    for label, bucket in sorted(buckets.items()):
        ordered = sorted(bucket, key=lambda item: tuple(item["identity"]))
        if len(ordered) < 2:
            continue
        first = ordered[0]
        for second in ordered[1:]:
            if first["support_hash"] == second["support_hash"]:
                duplicate_support_skips += 1
                continue
            row = [
                int(first["sign"]) * int(left) - int(second["sign"]) * int(right)
                for left, right in zip(first["row"], second["row"])
            ]
            key = canonical_row(row, order)
            if not any(key):
                zero_row_skips += 1
                continue
            if key in keys:
                continue
            keys.add(key)
            replay = independent.row_sum(row, factor_base, curve).is_zero()
            replay_failures += int(not replay)
            rows.append(row)
            closures.append({
                "label": list(label),
                "left": list(first["identity"]),
                "right": list(second["identity"]),
                "row": row,
                "replay_zero": bool(replay),
            })
    occupancy = Counter(len(bucket) for bucket in buckets.values())
    return {
        "label_count": len(buckets),
        "duplicate_label_bucket_count": sum(size >= 2 for size in occupancy.elements()),
        "maximum_bucket_size": max(occupancy.elements(), default=0),
        "occupancy_histogram": {str(size): int(count) for size, count in sorted(occupancy.items())},
        "usable_collision_rows": len(rows),
        "duplicate_support_skips": duplicate_support_skips,
        "zero_row_skips": zero_row_skips,
        "replay_failures": replay_failures,
        "rows": rows,
        "closures": closures,
        "row_hash": relation_hash([{"row": row} for row in rows]),
    }


def matrix_rank(rows: list[list[int]], order: int, width: int) -> int:
    if not rows:
        return 0
    return int(Matrix(GF(order), len(rows), width, rows).rank())


def null_scalar(p: int, replicate: int, record: dict[str, Any], retry: int, order: int) -> int:
    payload = compact([
        "p1496-same-class-random-fiber-v1",
        p,
        replicate,
        record["identity"],
        retry,
    ]).encode("ascii")
    return 1 + int.from_bytes(hashlib.sha256(payload).digest(), "big") % (order - 1)


def same_class_null_records(
    source_records: list[dict[str, Any]],
    p: int,
    replicate: int,
    order: int,
    generator: Any,
    curve: Any,
    field: Any,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    ring = PolynomialRing(field, f"p1496_null_x_{p}_{replicate}")
    records = []
    retries = 0
    for source in source_records:
        class_point = curve(tuple(source["class_point"]))
        built = None
        for retry in range(order + 1):
            scalar = null_scalar(p, replicate, source, retry, order)
            first = scalar * generator
            second = class_point - first
            built = divisor_from_points(first, second, ring, curve)
            if built is not None:
                retries += retry
                break
        if built is None:
            raise RuntimeError("same-class null failed to find a nondegenerate divisor")
        if built["class_point"] != class_point:
            raise RuntimeError("same-class null changed the aggregate class")
        records.append({
            "identity": list(source["identity"]),
            "support_hash": source["support_hash"],
            "label": list(built["label"]),
            "sign": int(built["sign"]),
            "row": list(source["row"]),
            "class_point": list(source["class_point"]),
        })
    return records, {"degeneracy_retries": retries}


def conventional_cross_checks(
    root_records: list[dict[str, Any]],
    conventional: list[dict[str, Any]],
    field: Any,
    curve: Any,
) -> dict[str, Any]:
    by_identity = {tuple(record["identity"]): record for record in root_records}
    ring = PolynomialRing(field, f"p1496_conventional_x_{field.order()}")
    checked = 0
    missing_root_record = 0
    missing_root_identities = []
    degenerate_pair = 0
    label_mismatches = 0
    sign_mismatches = 0
    for record in conventional:
        identity = (int(record["anchor_index"]), int(record["parameter"]))
        root_record = by_identity.get(identity)
        if root_record is None:
            missing_root_record += 1
            missing_root_identities.append(list(identity))
            continue
        points = [curve(tuple(point)) for point in record["missing_points"]]
        built = divisor_from_points(points[0], points[1], ring, curve)
        if built is None:
            degenerate_pair += 1
            continue
        checked += 1
        label_mismatches += int(tuple(root_record["label"]) != tuple(built["label"]))
        sign_mismatches += int(int(root_record["sign"]) != int(built["sign"]))
        root_record["conventional_missing_points"] = [list(point) for point in record["missing_points"]]
    return {
        "conventional_record_count": len(conventional),
        "checked": checked,
        "missing_root_record": missing_root_record,
        "missing_root_identities": missing_root_identities,
        "degenerate_pair": degenerate_pair,
        "label_mismatches": label_mismatches,
        "sign_mismatches": sign_mismatches,
    }


def mutation_control(record: dict[str, Any], field: Any, curve: Any) -> dict[str, Any]:
    ring = PolynomialRing(field, f"p1496_mutation_x_{field.order()}")
    x = ring.gen()
    u = ring([field(value) for value in record["certificate"]["u"]])
    v = ring([field(value) for value in record["certificate"]["v"]])
    a_mod = ring([field(value) for value in record["certificate"]["a_mod_u"]])
    b_mod = ring([field(value) for value in record["certificate"]["b_mod_u"]])
    mutated = v + 1
    curve_polynomial = x**3 + curve.a4() * x + curve.a6()
    curve_ok = (mutated**2 - curve_polynomial) % u == 0
    norm_ok = (a_mod + b_mod * mutated) % u == 0
    return {
        "mutation": "v0_plus_one",
        "curve_congruence_after_mutation": bool(curve_ok),
        "norm_congruence_after_mutation": bool(norm_ok),
        "rejected": bool(not (curve_ok and norm_ok)),
    }


def synthetic_closure_control(
    full_records: list[dict[str, Any]],
    factor_base: list[Any],
    curve: Any,
    order: int,
    independent: Any,
) -> dict[str, Any]:
    if not full_records:
        return {"passed": False, "reason": "no_full_relation"}
    relation = list(full_records[0]["row"])
    zero = [0] * len(relation)
    records = [
        {
            "identity": [-1, 0],
            "support_hash": "synthetic-left",
            "label": [0, 0, 0, 0],
            "sign": 1,
            "row": relation,
        },
        {
            "identity": [-1, 1],
            "support_hash": "synthetic-right",
            "label": [0, 0, 0, 0],
            "sign": 1,
            "row": zero,
        },
    ]
    closed = close_divisor_labels(records, factor_base, curve, order, independent)
    passed = (
        closed["usable_collision_rows"] == 1
        and closed["replay_failures"] == 0
        and canonical_row(closed["rows"][0], order) == canonical_row(relation, order)
    )
    return {
        "passed": bool(passed),
        "usable_collision_rows": int(closed["usable_collision_rows"]),
        "replay_failures": int(closed["replay_failures"]),
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1496 Root-Free Quadratic-Divisor Fingerprint",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Result",
        "",
        (
            "The `(u,v)` divisor is computed exactly from the specialized norm "
            "without factoring the quadratic or reconstructing either missing point. "
            "Correctness is separate from collision concentration and factor rank."
        ),
        "",
        "| p | attempts | exact labels | duplicate buckets | collision rows | marginal rank | null max rows/rank | cap |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in payload["field_records"]:
        candidate = record["candidate"]
        null = record["same_class_null"]
        lines.append(
            "| {p} | {attempts} | {labels} | {buckets} | {rows} | {rank} | {null_rows}/{null_rank} | {cap} |".format(
                p=record["p"],
                attempts=record["extraction"]["attempts"],
                labels=candidate["label_count"],
                buckets=candidate["duplicate_label_bucket_count"],
                rows=candidate["usable_collision_rows"],
                rank=record["rank"]["candidate_marginal"],
                null_rows=null["maximum_collision_rows"],
                null_rank=null["maximum_marginal_rank"],
                cap=record["memory"]["cap_records"],
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "A clean algebraic replay establishes a valid representation only. It is not "
        "evidence of a Shoup-bound or Pollard-rho improvement.",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    started = time.time()
    hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        str(path.relative_to(ROOT)): hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1496 frozen hash mismatch: {hash_gates}")
    po71_verified = json.loads(PO71_VERIFY_RESULT.read_text(encoding="ascii"))
    if not po71_verified.get("verified") or not all(po71_verified.get("correctness_gates", {}).values()):
        raise RuntimeError("P1496 requires a fully verified PO71 input")

    po71_result = json.loads(PO71_RESULT.read_text(encoding="ascii"))
    po71_by_p = {int(record["p"]): record for record in po71_result["field_records"]}
    po55 = json.loads(PO55_RESULT.read_text(encoding="ascii"))
    po71 = load_module(PO71_WALK, "p1496_po71_walk")
    po70 = load_module(PO70_SOURCE, "p1496_po70_relations")
    direct = load_module(PO70_DIRECT, "p1496_po70_direct")
    independent = load_module(PO65_DIRECT, "p1496_po65_independent")
    oracle = load_module(PO54_ORACLE, "p1496_po54_oracle")
    field_records = []

    for frozen in po55["records"]:
        field_started = time.perf_counter()
        independent.configure_oracle(oracle, frozen)
        p = int(frozen["p"])
        order = int(frozen["order"])
        field = GF(p)
        curve = EllipticCurve(field, [field(frozen["curve_a"]), field(frozen["curve_b"])])
        generator = curve.gens()[0]
        omega = next(value for value in field if value != 1 and value**3 == 1)
        points = oracle.finite_points(field)
        factor_base = oracle.factor_base_from(oracle.canonical_labels(field, points))
        expected = po71_by_p[p]
        core = po71.initial_core(factor_base)
        matrix, basis = direct.independent_core_basis(core, field, oracle)
        right_inverse = matrix.solve_right(identity_matrix(field, 6))
        usage = Counter(raw_label(label) for label in core)
        counters = Counter()
        full_records: list[dict[str, Any]] = []
        one_partials: list[dict[str, Any]] = []
        conventional_two: list[dict[str, Any]] = []
        root_records: list[dict[str, Any]] = []
        extraction_rejections: list[dict[str, Any]] = []
        extraction = Counter()
        anchor_identities = []
        seen = set()
        anchor_index = 0
        transitions = 0

        while True:
            step = transitions
            transition = None
            if transitions < PASSES * len(factor_base):
                transition = po71.choose_transition(
                    core,
                    matrix,
                    right_inverse,
                    basis,
                    transitions % 6,
                    usage,
                    factor_base,
                    field,
                    oracle,
                    counters,
                )
            variants = po71.choose_variants(
                core,
                factor_base,
                p,
                step,
                transition["incoming"] if transition else None,
            )
            retained = None
            for variant_index, seventh in enumerate(variants):
                anchor = core + [seventh]
                anchor_key = tuple(sorted(raw_label(label) for label in anchor))
                retain = transition is not None and variant_index == 0
                duplicate = anchor_key in seen
                if duplicate and not retain:
                    continue
                constraint = [oracle.evaluation_row(seventh, field) * item for item in basis]
                section = po71.counted_section(constraint, basis, field, counters)
                if section is None:
                    raise RuntimeError("P1496 found an empty retained section")
                pivot, _, sections = section
                if duplicate:
                    retained = {"pivot": pivot, "sections": sections}
                    continue
                seen.add(anchor_key)
                bins, _ = direct.direct_bins(
                    anchor,
                    sections[0],
                    sections[1],
                    factor_base,
                    field,
                    omega,
                    independent,
                )
                quotient = po70.build_quotient(
                    sections[0], sections[1], anchor, field, frozen, oracle
                )
                classified = direct.classify_direct(
                    anchor_index,
                    anchor,
                    sections[0],
                    sections[1],
                    bins,
                    factor_base,
                    points,
                    curve,
                    field,
                    frozen,
                    independent,
                    oracle,
                )
                full_records.extend(classified["full_records"])
                one_partials.extend(classified["one_partials"])
                conventional_two.extend(classified["two_partials"])
                anchor_points = {raw_point(label) for label in anchor}
                threshold3 = {parameter for parameter, support in bins.items() if len(support) >= 3}
                threshold4 = {parameter for parameter, support in bins.items() if len(support) >= 4}
                for parameter in sorted(threshold3 - threshold4):
                    extraction["attempts"] += 1
                    residual = set(bins[parameter])
                    record, reason = root_free_record(
                        anchor_index,
                        step,
                        variant_index,
                        anchor,
                        int(parameter),
                        residual,
                        quotient,
                        sections[0],
                        sections[1],
                        factor_base,
                        curve,
                        field,
                        frozen,
                        oracle,
                        independent,
                    )
                    extraction[reason] += 1
                    if record is not None:
                        if set(tuple(point) for point in record["support_points"]) != anchor_points | residual:
                            raise RuntimeError("P1496 support certificate mismatch")
                        root_records.append(record)
                    else:
                        extraction_rejections.append({
                            "identity": [int(anchor_index), int(parameter)],
                            "reason": reason,
                        })
                anchor_identities.append({
                    "anchor_index": int(anchor_index),
                    "core_index": int(step),
                    "variant_index": int(variant_index),
                    "seventh": list(raw_label(seventh)),
                    "anchor_hash": digest(
                        compact([list(raw_label(label)) for label in anchor]).encode("ascii")
                    ),
                })
                if retain:
                    retained = {"pivot": pivot, "sections": sections}
                anchor_index += 1
            if transitions == int(expected["transition_count"]):
                break
            if retained is None or transition is None:
                raise RuntimeError("P1496 transition lost its retained section")
            right_inverse, basis = po71.apply_transition(
                transition,
                retained,
                basis,
                right_inverse,
                len(factor_base),
                field,
                counters,
            )
            core = list(core)
            core[transition["slot"]] = transition["incoming"]
            usage[raw_label(transition["incoming"])] += 1
            matrix = Matrix(field, matrix)
            matrix.set_row(transition["slot"], transition["new_row"])
            transitions += 1

        relation_gates = {
            "transition_count_match": transitions == int(expected["transition_count"]),
            "anchor_count_match": anchor_index == int(expected["anchor_count"]),
            "anchor_identity_hash_match": relation_hash(anchor_identities)
            == relation_hash([
                {key: record[key] for key in (
                    "anchor_index", "core_index", "variant_index", "seventh", "anchor_hash"
                )}
                for record in expected["anchor_records"]
            ]),
            "full_hash_match": relation_hash(full_records) == expected["full_record_hash"],
            "one_lp_hash_match": relation_hash(one_partials) == expected["one_lp_hash"],
            "two_lp_hash_match": relation_hash(conventional_two) == expected["two_lp_hash"],
        }
        if not all(relation_gates.values()):
            raise RuntimeError(f"P1496 PO71 transcript mismatch p={p}: {relation_gates}")

        cross_checks = conventional_cross_checks(root_records, conventional_two, field, curve)
        candidate = close_divisor_labels(root_records, factor_base, curve, order, independent)
        one_rows, one_closures, one_bucket_count = independent.one_lp_closure(
            one_partials, factor_base, curve, order
        )
        baseline_rows = [list(record["row"]) for record in full_records] + one_rows
        baseline_rank = matrix_rank(baseline_rows, order, len(factor_base))
        candidate_rank = matrix_rank(
            baseline_rows + candidate["rows"], order, len(factor_base)
        )
        candidate_marginal = candidate_rank - baseline_rank

        null_records = []
        for replicate in range(NULL_REPLICATES):
            generated, null_generation = same_class_null_records(
                root_records,
                p,
                replicate,
                order,
                generator,
                curve,
                field,
            )
            closed = close_divisor_labels(generated, factor_base, curve, order, independent)
            rank = matrix_rank(
                baseline_rows + closed["rows"], order, len(factor_base)
            )
            null_records.append({
                "replicate": replicate,
                "collision_rows": int(closed["usable_collision_rows"]),
                "duplicate_label_bucket_count": int(closed["duplicate_label_bucket_count"]),
                "marginal_rank": int(rank - baseline_rank),
                "replay_failures": int(closed["replay_failures"]),
                "row_hash": closed["row_hash"],
                **null_generation,
            })
        null_collision_values = [record["collision_rows"] for record in null_records]
        null_rank_values = [record["marginal_rank"] for record in null_records]
        collision_tail = (1 + sum(value >= candidate["usable_collision_rows"] for value in null_collision_values)) / (NULL_REPLICATES + 1)
        rank_tail = (1 + sum(value >= candidate_marginal for value in null_rank_values)) / (NULL_REPLICATES + 1)
        same_class_null = {
            "replicates": null_records,
            "maximum_collision_rows": max(null_collision_values, default=0),
            "mean_collision_rows": statistics.mean(null_collision_values) if null_collision_values else 0.0,
            "maximum_marginal_rank": max(null_rank_values, default=0),
            "mean_marginal_rank": statistics.mean(null_rank_values) if null_rank_values else 0.0,
            "candidate_collision_plus_one_tail": float(collision_tail),
            "candidate_rank_plus_one_tail": float(rank_tail),
            "candidate_strictly_beats_all_collision_controls": bool(
                candidate["usable_collision_rows"] > max(null_collision_values, default=-1)
            ),
            "candidate_strictly_beats_all_rank_controls": bool(
                candidate_marginal > max(null_rank_values, default=-1)
            ),
        }

        mutation = mutation_control(root_records[0], field, curve) if root_records else {
            "rejected": False,
            "reason": "no_root_free_record",
        }
        synthetic = synthetic_closure_control(
            full_records, factor_base, curve, order, independent
        )
        cap_records = int(math.floor(4 * math.sqrt(order)))
        retained_records = int(candidate["label_count"] + candidate["usable_collision_rows"])
        accepted_total = extraction["accepted"] + extraction["accepted_singular_branch"]
        algebra_exact = (
            accepted_total == len(root_records)
            and extraction["congruence_failure"] == 0
            and extraction["class_failure"] == 0
            and extraction["row_class_failure"] == 0
            and candidate["replay_failures"] == 0
        )
        conventional_exact = (
            cross_checks["missing_root_record"] == 0
            and cross_checks["degenerate_pair"] == 0
            and cross_checks["label_mismatches"] == 0
            and cross_checks["sign_mismatches"] == 0
        )
        field_records.append({
            "p": p,
            "order": order,
            "holdout": p == 1009,
            "curve": {"a": int(curve.a4()), "b": int(curve.a6())},
            "generator": list(raw_point(generator)),
            "factor_base": [list(raw_point(label)) for label in factor_base],
            "factor_base_size": len(factor_base),
            "relation_gates": relation_gates,
            "relation_hashes": {
                "anchors": relation_hash(anchor_identities),
                "full": relation_hash(full_records),
                "one_lp": relation_hash(one_partials),
                "two_lp": relation_hash(conventional_two),
            },
            "extraction": {key: int(value) for key, value in sorted(extraction.items())},
            "extraction_rejections": extraction_rejections,
            "root_free_records": root_records,
            "root_free_record_hash": relation_hash(root_records),
            "candidate": candidate,
            "baseline": {
                "full_rows": [list(record["row"]) for record in full_records],
                "one_lp_rows": one_rows,
                "one_lp_closures": one_closures,
                "one_lp_bucket_count": int(one_bucket_count),
                "row_hash": relation_hash([{"row": row} for row in baseline_rows]),
            },
            "rank": {
                "baseline": baseline_rank,
                "candidate": candidate_rank,
                "candidate_marginal": candidate_marginal,
                "target": len(factor_base) - 1,
            },
            "same_class_null": same_class_null,
            "controls": {
                "algebra_exact": bool(algebra_exact),
                "conventional_pair_cross_check": cross_checks,
                "mutation": mutation,
                "synthetic_closure": synthetic,
            },
            "memory": {
                "retained_candidate_labels_plus_rows": retained_records,
                "cap_records": cap_records,
                "within_cap": retained_records <= cap_records,
            },
            "cost_boundary": {
                "root_extractions": 0,
                "square_root_calls": 0,
                "individual_missing_points_reconstructed_on_candidate_path": 0,
                "quadratic_divisions": int(extraction["attempts"]),
                "modular_polynomial_inversions": int(extraction["accepted"]),
                "known_linear_singular_branch_recoveries": int(
                    extraction["accepted_singular_branch"]
                ),
                "po71_shared_source_group_equivalents": float(
                    expected["cumulative"][-1]["cost"]["shared_source_group_equivalents"]
                ),
                "po71_one_lp_group_equivalents": float(
                    expected["cumulative"][-1]["cost"]["one_lp_group_equivalents"]
                ),
                "po71_rho_mean_group_operations": float(
                    expected["cumulative"][-1]["cost"]["rho_mean_group_operations"]
                ),
            },
            "wall_seconds": float(time.perf_counter() - field_started),
        })

    tuning = [record for record in field_records if not record["holdout"]]
    correctness = all(
        all(record["relation_gates"].values())
        and record["controls"]["algebra_exact"]
        and record["controls"]["conventional_pair_cross_check"]["missing_root_record"] == 0
        and record["controls"]["conventional_pair_cross_check"]["degenerate_pair"] == 0
        and record["controls"]["conventional_pair_cross_check"]["label_mismatches"] == 0
        and record["controls"]["conventional_pair_cross_check"]["sign_mismatches"] == 0
        and record["controls"]["mutation"]["rejected"]
        and record["controls"]["synthetic_closure"]["passed"]
        and all(item["replay_failures"] == 0 for item in record["same_class_null"]["replicates"])
        for record in field_records
    )
    positive_rank_tuning = all(record["rank"]["candidate_marginal"] > 0 for record in tuning)
    beats_null_tuning = all(
        record["same_class_null"]["candidate_strictly_beats_all_collision_controls"]
        and record["same_class_null"]["candidate_strictly_beats_all_rank_controls"]
        for record in tuning
    )
    memory_tuning = all(record["memory"]["within_cap"] for record in tuning)
    follow_on = correctness and positive_rank_tuning and beats_null_tuning and memory_tuning
    if not correctness:
        status = "REVIEW_REQUIRED_P1496_ROOT_FREE_DIVISOR_REPLAY_MISMATCH"
        interpretation = "At least one frozen transcript or algebraic control failed; no cryptanalytic interpretation is licensed."
    elif not positive_rank_tuning:
        status = "NEGATIVE_RESULT_P1496_EXACT_DIVISOR_LABELS_NO_TUNING_RANK"
        interpretation = "The exact root-free divisor representation is correct, but it does not add factor rank on every tuning field."
    elif not beats_null_tuning:
        status = "NEGATIVE_RESULT_P1496_EXACT_DIVISOR_NO_COVER_CONCENTRATION"
        interpretation = "The exact root-free divisor representation is correct, but its collisions or rank do not beat every same-class random-fiber control."
    elif not memory_tuning:
        status = "NEGATIVE_RESULT_P1496_EXACT_DIVISOR_MEMORY_GATE"
        interpretation = "The representation passes algebra and concentration gates but exceeds the frozen retained-record cap."
    else:
        status = "MIXED_RESULT_P1496_ROOT_FREE_DIVISOR_FOLLOW_ON_JUSTIFIED"
        interpretation = "The preflight clears its registered follow-on gates; a fully charged target-blind successor is justified, not yet a generic breakthrough."

    payload = {
        "schema": SCHEMA,
        "status": status,
        "claim_status": "TOY PREFLIGHT / REPRESENTATION TEST / NO GENERIC BREAKTHROUGH",
        "source": str(Path(__file__).resolve()),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "contract": str(CONTRACT),
        "contract_sha256": sha256_file(CONTRACT),
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "construction": {
            "label": "canonical signed Mumford-style (u,v) degree-two divisor",
            "u": "monic residual quadratic after three known x-roots",
            "v": "-A/B modulo u from A(x)+B(x)y=0",
            "class_formula": "S=(v1^2+u1, -(v1*(v1^2+u1)+v0))",
            "candidate_root_free": True,
            "null": "32 SHA256-seeded exact divisors in the same Abel-Jacobi class",
        },
        "field_records": field_records,
        "gates": {
            "all_frozen_hashes_match": all(hash_gates.values()),
            "all_transcripts_and_algebra_exact": correctness,
            "positive_marginal_rank_all_tuning_fields": positive_rank_tuning,
            "beats_all_same_class_nulls_all_tuning_fields": beats_null_tuning,
            "retained_records_within_cap_all_tuning_fields": memory_tuning,
            "follow_on_justified": follow_on,
            "generic_shoup_breakthrough": False,
            "beats_pollard_rho": False,
        },
        "interpretation": interpretation,
        "limitations": [
            "All fields are toy-scale and reuse the frozen PO71 source stream.",
            "The direct conventional two-point reconstruction is a correctness control and is excluded from the candidate path.",
            "The same-class null tests cover concentration inside Abel-Jacobi fibers, not every possible auxiliary-Jacobian correspondence.",
            "A clean divisor replay proves correctness only; it does not imply an asymptotic improvement.",
        ],
        "next_action": (
            "If negative, close exact (u,v) degree-two fingerprints on the PO71 stream and move to a genuinely non-scalar auxiliary-Jacobian or quotient invariant that retains rank while reducing the label dimension. If mixed, build a fully charged target-blind successor before any promotion claim."
        ),
        "peak_rss_raw": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "wall_seconds": float(time.time() - started),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "fields": [
            {
                "p": record["p"],
                "attempts": record["extraction"]["attempts"],
                "accepted": record["extraction"]["accepted"]
                + record["extraction"].get("accepted_singular_branch", 0),
                "collision_rows": record["candidate"]["usable_collision_rows"],
                "marginal_rank": record["rank"]["candidate_marginal"],
                "null_max_rows": record["same_class_null"]["maximum_collision_rows"],
                "null_max_rank": record["same_class_null"]["maximum_marginal_rank"],
            }
            for record in field_records
        ],
    }, indent=2, sort_keys=True))
    return 1 if status.startswith("REVIEW_REQUIRED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
