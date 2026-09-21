#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import resource
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Sequence


SCRIPT_PATH = Path(__file__).resolve()
NORM_SOURCE = SCRIPT_PATH.with_name("typed_s4_norm_rank.py")
Monomial = tuple[int, int, int]
Polynomial = dict[Monomial, int]
Projective = tuple[int, int, int]
Point = tuple[int, int] | None


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


NORM = load_module("typed_s4_norm_for_direct_prefix", NORM_SOURCE)
TYPED = NORM.TYPED_EC
TT = NORM.TT


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def clean(poly: Polynomial, p: int) -> Polynomial:
    return {
        monomial: coefficient % p
        for monomial, coefficient in poly.items()
        if coefficient % p
    }


def poly_add(left: Polynomial, right: Polynomial, p: int) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = (
            result.get(monomial, 0) + coefficient
        ) % p
    return clean(result, p)


def poly_sub(left: Polynomial, right: Polynomial, p: int) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = (
            result.get(monomial, 0) - coefficient
        ) % p
    return clean(result, p)


def poly_scale(poly: Polynomial, scalar: int, p: int) -> Polynomial:
    return clean(
        {
            monomial: scalar * coefficient % p
            for monomial, coefficient in poly.items()
        },
        p,
    )


def reduce_poly(
    poly: Polynomial, p: int, a: int, b: int
) -> Polynomial:
    pending = list(poly.items())
    result: Polynomial = {}
    while pending:
        (x_power, y_power, z_power), coefficient = pending.pop()
        coefficient %= p
        if coefficient == 0:
            continue
        if x_power < 3:
            monomial = (x_power, y_power, z_power)
            result[monomial] = (
                result.get(monomial, 0) + coefficient
            ) % p
            continue
        pending.extend(
            [
                (
                    (x_power - 3, y_power + 2, z_power + 1),
                    coefficient,
                ),
                (
                    (x_power - 2, y_power, z_power + 2),
                    -a * coefficient,
                ),
                (
                    (x_power - 3, y_power, z_power + 3),
                    -b * coefficient,
                ),
            ]
        )
    return clean(result, p)


def poly_mul(
    left: Polynomial,
    right: Polynomial,
    p: int,
    a: int,
    b: int,
) -> Polynomial:
    product: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_monomial[index] + right_monomial[index]
                for index in range(3)
            )
            product[monomial] = (
                product.get(monomial, 0)
                + left_coefficient * right_coefficient
            ) % p
    return reduce_poly(product, p, a, b)


def constant(value: int, p: int) -> Polynomial:
    return {} if value % p == 0 else {(0, 0, 0): value % p}


def variables() -> tuple[Polynomial, Polynomial, Polynomial]:
    return ({(1, 0, 0): 1}, {(0, 1, 0): 1}, {(0, 0, 1): 1})


def polynomial_degree(poly: Polynomial) -> int | None:
    degrees = {sum(monomial) for monomial in poly}
    if not degrees:
        return None
    if len(degrees) != 1:
        raise AssertionError("polynomial is not homogeneous")
    return next(iter(degrees))


def basis(degree: int) -> list[Monomial]:
    return [
        (x_power, y_power, degree - x_power - y_power)
        for x_power in range(min(2, degree) + 1)
        for y_power in range(degree - x_power + 1)
    ]


def coefficient_vector(
    poly: Polynomial, monomials: Sequence[Monomial]
) -> list[int]:
    allowed = set(monomials)
    if set(poly) - allowed:
        raise AssertionError("polynomial is outside coordinate-ring basis")
    return [poly.get(monomial, 0) for monomial in monomials]


def evaluate_polynomial(
    poly: Polynomial, point: Projective, p: int
) -> int:
    x, y, z = point
    return sum(
        coefficient
        * pow(x, monomial[0], p)
        * pow(y, monomial[1], p)
        * pow(z, monomial[2], p)
        for monomial, coefficient in poly.items()
    ) % p


def evaluate_basis(
    monomials: Sequence[Monomial], point: Projective, p: int
) -> list[int]:
    x, y, z = point
    return [
        pow(x, monomial[0], p)
        * pow(y, monomial[1], p)
        * pow(z, monomial[2], p)
        % p
        for monomial in monomials
    ]


def rcb_add_polynomial(
    left: tuple[Polynomial, Polynomial, Polynomial],
    right: Projective,
    p: int,
    a: int,
    b: int,
) -> tuple[Polynomial, Polynomial, Polynomial]:
    X1, Y1, Z1 = left
    X2, Y2, Z2 = (constant(value, p) for value in right)
    mul = lambda x, y: poly_mul(x, y, p, a, b)
    add = lambda x, y: poly_add(x, y, p)
    sub = lambda x, y: poly_sub(x, y, p)
    b3 = 3 * b % p
    t0 = mul(X1, X2)
    t1 = mul(Y1, Y2)
    t2 = mul(Z1, Z2)
    t3 = add(X1, Y1)
    t4 = add(X2, Y2)
    t3 = mul(t3, t4)
    t4 = add(t0, t1)
    t3 = sub(t3, t4)
    t4 = add(X1, Z1)
    t5 = add(X2, Z2)
    t4 = mul(t4, t5)
    t5 = add(t0, t2)
    t4 = sub(t4, t5)
    t5 = add(Y1, Z1)
    X3 = add(Y2, Z2)
    t5 = mul(t5, X3)
    X3 = add(t1, t2)
    t5 = sub(t5, X3)
    Z3 = poly_scale(t4, a, p)
    X3 = poly_scale(t2, b3, p)
    Z3 = add(X3, Z3)
    X3 = sub(t1, Z3)
    Z3 = add(t1, Z3)
    Y3 = mul(X3, Z3)
    t1 = add(t0, t0)
    t1 = add(t1, t0)
    t2 = poly_scale(t2, a, p)
    t4 = poly_scale(t4, b3, p)
    t1 = add(t1, t2)
    t2 = sub(t0, t2)
    t2 = poly_scale(t2, a, p)
    t4 = add(t4, t2)
    t0 = mul(t1, t4)
    Y3 = add(Y3, t0)
    t0 = mul(t5, t4)
    X3 = mul(t3, X3)
    X3 = sub(X3, t0)
    t0 = mul(t3, t1)
    Z3 = mul(t5, Z3)
    Z3 = add(Z3, t0)
    return X3, Y3, Z3


def locator_components(
    output: tuple[Polynomial, Polynomial, Polynomial],
    p: int,
    a: int,
    b: int,
    nu: int,
) -> list[Polynomial]:
    x, y, z = output
    mul = lambda u, v: poly_mul(u, v, p, a, b)
    return [
        poly_sub(mul(x, x), poly_scale(mul(y, y), nu, p), p),
        poly_scale(mul(x, z), -2, p),
        poly_scale(mul(y, z), 2 * nu, p),
        mul(z, z),
    ]


def target_weights(target: Point, p: int, nu: int) -> list[int]:
    xq, yq, zq = NORM.affine_to_projective(target)
    return [
        zq * zq % p,
        zq * xq % p,
        zq * yq % p,
        (xq * xq - nu * yq * yq) % p,
    ]


def combine_components(
    components: Sequence[Polynomial],
    weights: Sequence[int],
    p: int,
) -> Polynomial:
    result: Polynomial = {}
    for component, weight in zip(components, weights):
        result = poly_add(result, poly_scale(component, weight, p), p)
    return result


def prefix_projective(
    points: Sequence[Point], p: int, a: int, b: int
) -> Projective:
    result = NORM.affine_to_projective(points[0])
    for point in points[1:]:
        result = TT.rcb_add(
            result, NORM.affine_to_projective(point), p, a, b
        )
    return result


def derive_suffix_components(
    suffix_points: Sequence[Point],
    p: int,
    a: int,
    b: int,
    nu: int,
) -> list[Polynomial]:
    state = variables()
    for point in suffix_points:
        state = rcb_add_polynomial(
            state, NORM.affine_to_projective(point), p, a, b
        )
    return locator_components(state, p, a, b, nu)


def vector_rank(vectors: list[list[int]], p: int) -> int:
    if not vectors:
        return 0
    return NORM.rank_mod(
        [value for vector in vectors for value in vector],
        [len(vectors), len(vectors[0])],
        1,
        p,
    )["rank"]


def run_cut(
    cut: int,
    p: int,
    a: int,
    b: int,
    a_points: list[Point],
    r_points: list[Point],
    targets: dict[str, Point],
) -> dict[str, Any]:
    suffix_count = 5 - cut
    degree = 2 ** (6 - cut)
    monomials = basis(degree)
    expected_dimension = 3 * degree
    if len(monomials) != expected_dimension:
        raise AssertionError("unexpected coordinate-ring dimension")
    nu = NORM.nonsquare(p)
    prefix_indices = list(
        itertools.product(
            range(len(a_points)),
            *(range(len(r_points)) for _ in range(cut - 1)),
        )
    )
    suffix_indices = list(
        itertools.product(
            *(range(len(r_points)) for _ in range(suffix_count))
        )
    )
    prefix_points = [
        prefix_projective(
            [
                a_points[indices[0]],
                *(r_points[index] for index in indices[1:]),
            ],
            p,
            a,
            b,
        )
        for indices in prefix_indices
    ]
    u_vectors = [
        evaluate_basis(monomials, point, p) for point in prefix_points
    ]
    component_vectors = []
    component_nnz = []
    component_degrees = set()
    for indices in suffix_indices:
        components = derive_suffix_components(
            [r_points[index] for index in indices], p, a, b, nu
        )
        component_degrees.update(
            polynomial_degree(component) for component in components
        )
        vectors = [
            coefficient_vector(component, monomials)
            for component in components
        ]
        component_vectors.append(vectors)
        component_nnz.extend(
            sum(value != 0 for value in vector) for vector in vectors
        )
    target_rows = {}
    for target_name, target in targets.items():
        weights = target_weights(target, p, nu)
        v_vectors = [
            [
                sum(
                    weights[component] * vectors[component][position]
                    for component in range(4)
                )
                % p
                for position in range(len(monomials))
            ]
            for vectors in component_vectors
        ]
        component_mismatches = 0
        for suffix_index, indices in enumerate(suffix_indices):
            components = derive_suffix_components(
                [r_points[index] for index in indices], p, a, b, nu
            )
            combined_vector = coefficient_vector(
                combine_components(components, weights, p), monomials
            )
            component_mismatches += int(
                combined_vector != v_vectors[suffix_index]
            )
        mismatches = 0
        zero_mismatches = 0
        exact_values = []
        factor_values = []
        for prefix_index, left_indices in enumerate(prefix_indices):
            for suffix_index, right_indices in enumerate(suffix_indices):
                factor_value = sum(
                    x * y
                    for x, y in zip(
                        u_vectors[prefix_index],
                        v_vectors[suffix_index],
                    )
                ) % p
                output = prefix_points[prefix_index]
                for index in right_indices:
                    output = TT.rcb_add(
                        output,
                        NORM.affine_to_projective(r_points[index]),
                        p,
                        a,
                        b,
                    )
                exact_value = NORM.locator_tensors(
                    {
                        "outputs_internal": [output],
                        "affine_sums_internal": [
                            TT.projective_to_affine(output, p)
                        ],
                    },
                    target,
                    p,
                    nu,
                    [1],
                )["tensors_internal"]["h^1"][0]
                expected_point = TT.projective_to_affine(output, p)
                factor_values.append(factor_value)
                exact_values.append(exact_value)
                mismatches += int(factor_value != exact_value)
                zero_mismatches += int(
                    (factor_value == 0) != (expected_point == target)
                )
        word_bytes = max(1, (p.bit_length() + 7) // 8)
        target_rows[target_name] = {
            "target": TYPED.point_json(target),
            "weights": weights,
            "v_rank": vector_rank(v_vectors, p),
            "v_digest": canonical_digest(v_vectors),
            "target_dependent_advice_field_elements": (
                len(v_vectors) * len(monomials)
            ),
            "target_dependent_advice_bytes": (
                len(v_vectors) * len(monomials) * word_bytes
            ),
            "target_specialization_multiplications": (
                4 * len(v_vectors) * len(monomials)
            ),
            "pair_verifications": len(prefix_indices)
            * len(suffix_indices),
            "factor_mismatches": mismatches,
            "component_mismatches": component_mismatches,
            "zero_set_mismatches": zero_mismatches,
            "factor_digest": canonical_digest(factor_values),
            "exact_digest": canonical_digest(exact_values),
        }
    word_bytes = max(1, (p.bit_length() + 7) // 8)
    return {
        "cut": cut,
        "degree": degree,
        "basis_dimension": len(monomials),
        "basis_digest": canonical_digest(monomials),
        "prefix_count": len(prefix_indices),
        "suffix_count": len(suffix_indices),
        "u_rank": vector_rank(u_vectors, p),
        "u_digest": canonical_digest(u_vectors),
        "component_count": 4,
        "component_degrees": sorted(component_degrees),
        "component_nnz_min": min(component_nnz),
        "component_nnz_median": statistics.median(component_nnz),
        "component_nnz_max": max(component_nnz),
        "component_digest": canonical_digest(component_vectors),
        "target_independent_advice_field_elements": (
            4 * len(suffix_indices) * len(monomials)
        ),
        "target_independent_advice_bytes": (
            4 * len(suffix_indices) * len(monomials) * word_bytes
        ),
        "targets": target_rows,
    }


def build_targets(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
    a_points: list[Point],
    r_points: list[Point],
) -> dict[str, Point]:
    shape = [len(a_points)] + [len(r_points)] * 4
    planted_indices = NORM.hashed_indices(
        (
            "EXP-ECDLP-COORD-EXPANSION-001|DIRECT-PREFIX-FACTOR|"
            f"{curve_record['id']}|{family_record['family']}"
        ),
        shape,
    )
    planted = NORM.sum_affine(
        [
            a_points[planted_indices[0]],
            *(r_points[planted_indices[index]] for index in range(1, 5)),
        ],
        curve_record["p"],
        curve_record["a"],
    )
    curve = TYPED.Curve(
        curve_record["p"], curve_record["a"], curve_record["b"]
    )
    held_out, _, _ = TYPED.hash_to_curve_point(
        curve,
        curve_record["q"],
        family_record["run_seed"] ^ 0x452821E6,
        (
            "DIRECT-PREFIX-FACTOR|HELD-OUT|"
            f"{curve_record['id']}|{family_record['family']}"
        ),
        set(a_points) | set(r_points),
    )
    return {"planted": planted, "held_out": held_out}


def run_family(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
) -> dict[str, Any]:
    p = curve_record["p"]
    a = curve_record["a"]
    b = curve_record["b"]
    a_points = [
        NORM.point_from_json(value)
        for value in family_record["progression"]["points"]
    ]
    r_points = [
        NORM.point_from_json(value)
        for value in family_record["factor_base"]["points"]
    ]
    targets = build_targets(
        curve_record, family_record, a_points, r_points
    )
    cuts = [
        run_cut(
            cut, p, a, b, a_points, r_points, targets
        )
        for cut in (2, 3)
    ]
    valid = all(
        row["basis_dimension"] == 3 * row["degree"]
        and row["component_degrees"] == [row["degree"]]
        and all(
            target["factor_mismatches"] == 0
            and target["component_mismatches"] == 0
            and target["zero_set_mismatches"] == 0
            and target["factor_digest"] == target["exact_digest"]
            for target in row["targets"].values()
        )
        for row in cuts
    )
    return {
        "curve_id": curve_record["id"],
        "p": p,
        "q": curve_record["q"],
        "family": family_record["family"],
        "a_size": len(a_points),
        "r_size": len(r_points),
        "cuts": cuts,
        "valid": valid,
        "peak_rss_bytes_after_family": rss_bytes(),
    }


def fit_exponent(points: list[tuple[int, int]]) -> float:
    xs = [math.log(q) for q, _ in points]
    ys = [math.log(value) for _, value in points]
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    return sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    ) / sum((x - x_mean) ** 2 for x in xs)


def algebra_controls() -> dict[str, Any]:
    p, a, b = 101, 2, 3
    x, y, z = variables()
    cubic = poly_sub(
        poly_add(
            poly_mul(x, poly_mul(x, x, p, a, b), p, a, b),
            poly_add(
                poly_scale(
                    poly_mul(
                        x, poly_mul(z, z, p, a, b), p, a, b
                    ),
                    a,
                    p,
                ),
                poly_scale(
                    poly_mul(
                        z, poly_mul(z, z, p, a, b), p, a, b
                    ),
                    b,
                    p,
                ),
                p,
            ),
            p,
        ),
        poly_mul(poly_mul(y, y, p, a, b), z, p, a, b),
        p,
    )
    point = (1, 39, 1)
    right = (3, 6, 1)
    symbolic = rcb_add_polynomial(variables(), right, p, a, b)
    evaluated = tuple(
        evaluate_polynomial(poly, point, p) for poly in symbolic
    )
    numeric = TT.rcb_add(point, right, p, a, b)
    return {
        "cubic_reduces_to_zero": not cubic,
        "symbolic_rcb_matches_numeric": evaluated == numeric,
        "symbolic_rcb_degrees": [
            polynomial_degree(poly) for poly in symbolic
        ],
    }


def run(result_path: Path, families: list[str]) -> dict[str, Any]:
    source_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    controls = algebra_controls()
    if not all(
        (
            controls["cubic_reduces_to_zero"],
            controls["symbolic_rcb_matches_numeric"],
            controls["symbolic_rcb_degrees"] == [2, 2, 2],
        )
    ):
        raise AssertionError("algebra control failed")
    rows = []
    for instance in source_result["instances"]:
        by_family = {
            record["family"]: record for record in instance["families"]
        }
        for family in families:
            rows.append(
                run_family(instance["curve"], by_family[family])
            )
    scaling = {}
    for cut in (2, 3):
        scaling[f"cut_{cut}"] = {
            "target_independent_advice_field_elements": fit_exponent(
                [
                    (
                        row["q"],
                        next(
                            item
                            for item in row["cuts"]
                            if item["cut"] == cut
                        )["target_independent_advice_field_elements"],
                    )
                    for row in rows
                    if row["family"] == families[0]
                ]
            ),
            "target_dependent_advice_field_elements": fit_exponent(
                [
                    (
                        row["q"],
                        next(
                            item
                            for item in row["cuts"]
                            if item["cut"] == cut
                        )["targets"]["planted"][
                            "target_dependent_advice_field_elements"
                        ],
                    )
                    for row in rows
                    if row["family"] == families[0]
                ]
            ),
        }
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-direct-prefix-factor-v1"
        ),
        "claim_status": [
            "RESTRICTED THEOREM",
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "direct_prefix_factor_sha256": sha256_file(SCRIPT_PATH),
            "typed_s4_norm_rank_sha256": sha256_file(NORM_SOURCE),
            "typed_five_ec_sha256": sha256_file(NORM.TYPED_EC_SOURCE),
            "tt_norm_rank_sha256": sha256_file(NORM.TT_SOURCE),
            "input_result_sha256": sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
        },
        "controls": controls,
        "rows": rows,
        "scaling": scaling,
        "summary": {
            "family_rows": len(rows),
            "all_controls_valid": all(
                (
                    controls["cubic_reduces_to_zero"],
                    controls["symbolic_rcb_matches_numeric"],
                    controls["symbolic_rcb_degrees"] == [2, 2, 2],
                )
            ),
            "all_factorizations_valid": all(
                row["valid"] for row in rows
            ),
            "direct_factor_gate": all(row["valid"] for row in rows),
            "zero_index_constructed": False,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": (
                "Exact direct factor compiler only. Explicit suffix "
                "component state and target specialization remain above "
                "the required central-join cost."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run(args.result, args.families),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
