from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum
from typing import Generic as _Generic
from typing import TypeAlias as _TypeAlias
from typing import TypeVar as _TypeVar


class AdditionBranch(_Enum):
    SECANT = "secant"
    TANGENT = "tangent"
    VERTICAL = "vertical"


class CoreApi(_Enum):
    BUILD_CANDIDATE_CORE = "build_candidate_core"


class CoreErrorCode(_Enum):
    TYPE_MISMATCH = "type_mismatch"
    MODULUS_NOT_ODD_PRIME = "modulus_not_odd_prime"
    NONCANONICAL_COEFFICIENT = "noncanonical_coefficient"
    SINGULAR_CURVE = "singular_curve"
    FACTOR_BASE_SIZE = "factor_base_size"
    NONCANONICAL_POINT = "noncanonical_point"
    DUPLICATE_POINT = "duplicate_point"
    FACTOR_BASE_ORDER = "factor_base_order"
    POINT_NOT_ON_CURVE = "point_not_on_curve"
    TWO_TORSION_POINT = "two_torsion_point"
    FACTOR_BASE_NOT_SIGN_COMPLETE = "factor_base_not_sign_complete"
    ZERO_CHART_SCALAR = "zero_chart_scalar"
    NONINVERTIBLE_DENOMINATOR = "noninvertible_denominator"
    INTERCEPT_MISMATCH = "intercept_mismatch"
    INTERNAL_INVARIANT_FAILURE = "internal_invariant_failure"


@_dataclass(frozen=True, slots=True)
class CurveInput:
    p: int
    a: int
    b: int


@_dataclass(frozen=True, slots=True)
class Curve:
    p: int
    a: int
    b: int


@_dataclass(frozen=True, slots=True, order=True)
class AffinePoint:
    x: int
    y: int


@_dataclass(frozen=True, slots=True)
class Infinity:
    pass


@_dataclass(frozen=True, slots=True)
class FactorBase:
    points: tuple[AffinePoint, ...]


@_dataclass(frozen=True, slots=True)
class ChartFixture:
    curve: Curve
    u: int
    factor_base: FactorBase


@_dataclass(frozen=True, slots=True)
class Addition:
    result: AffinePoint | Infinity
    branch: AdditionBranch
    slope: int | None
    intercept: int | None


@_dataclass(frozen=True, slots=True)
class Witness:
    i: int
    j: int
    result: AffinePoint
    slope: int
    intercept: int


@_dataclass(frozen=True, slots=True)
class Fiber:
    result: AffinePoint
    witnesses: tuple[Witness, ...]


@_dataclass(frozen=True, slots=True)
class FiberSet:
    fibers: tuple[Fiber, ...]


@_dataclass(frozen=True, slots=True)
class Representative:
    result: AffinePoint
    witness: Witness


@_dataclass(frozen=True, slots=True)
class RepresentativeTable:
    entries: tuple[Representative, ...]


@_dataclass(frozen=True, slots=True)
class SectionDiagnostics:
    nonidentity_fiber_count: int
    nonsingleton_fiber_count: int
    choice_product: int
    minimum_slope_tie_fibers: int
    slope_collision_pairs: int


@_dataclass(frozen=True, slots=True)
class CandidateCore:
    fixture: ChartFixture
    fibers: FiberSet
    representatives: RepresentativeTable
    diagnostics: SectionDiagnostics


@_dataclass(frozen=True, slots=True)
class CoreOps:
    integer_remainder_tests: int
    field_reductions: int
    field_additions: int
    field_subtractions: int
    field_multiplications: int
    field_squarings: int
    field_negations: int
    field_inversions: int
    point_membership_checks: int
    chart_curve_transforms: int
    chart_point_transforms: int
    unordered_pairs_enumerated: int
    ec_additions: int
    secant_branches: int
    tangent_branches: int
    vertical_pairs_excluded: int
    fiber_witnesses_inserted: int
    sort_keys_emitted: int
    representative_keys_compared: int
    slope_collision_checks: int


@_dataclass(frozen=True, slots=True)
class CoreError:
    code: CoreErrorCode
    api: CoreApi
    indices: tuple[int, ...]


_T = _TypeVar("_T")


@_dataclass(frozen=True, slots=True)
class Success(_Generic[_T]):
    value: _T
    operations: CoreOps


@_dataclass(frozen=True, slots=True)
class Failure:
    error: CoreError
    operations: CoreOps


CoreResult: _TypeAlias = Success[_T] | Failure


def _zero_ops() -> CoreOps:
    return CoreOps(
        integer_remainder_tests=0,
        field_reductions=0,
        field_additions=0,
        field_subtractions=0,
        field_multiplications=0,
        field_squarings=0,
        field_negations=0,
        field_inversions=0,
        point_membership_checks=0,
        chart_curve_transforms=0,
        chart_point_transforms=0,
        unordered_pairs_enumerated=0,
        ec_additions=0,
        secant_branches=0,
        tangent_branches=0,
        vertical_pairs_excluded=0,
        fiber_witnesses_inserted=0,
        sort_keys_emitted=0,
        representative_keys_compared=0,
        slope_collision_checks=0,
    )


def _tick(
    operations: CoreOps,
    *,
    integer_remainder_tests: int = 0,
    field_reductions: int = 0,
    field_additions: int = 0,
    field_subtractions: int = 0,
    field_multiplications: int = 0,
    field_squarings: int = 0,
    field_negations: int = 0,
    field_inversions: int = 0,
    point_membership_checks: int = 0,
    chart_curve_transforms: int = 0,
    chart_point_transforms: int = 0,
    unordered_pairs_enumerated: int = 0,
    ec_additions: int = 0,
    secant_branches: int = 0,
    tangent_branches: int = 0,
    vertical_pairs_excluded: int = 0,
    fiber_witnesses_inserted: int = 0,
    sort_keys_emitted: int = 0,
    representative_keys_compared: int = 0,
    slope_collision_checks: int = 0,
) -> CoreOps:
    return CoreOps(
        integer_remainder_tests=(
            operations.integer_remainder_tests + integer_remainder_tests
        ),
        field_reductions=operations.field_reductions + field_reductions,
        field_additions=operations.field_additions + field_additions,
        field_subtractions=operations.field_subtractions + field_subtractions,
        field_multiplications=(
            operations.field_multiplications + field_multiplications
        ),
        field_squarings=operations.field_squarings + field_squarings,
        field_negations=operations.field_negations + field_negations,
        field_inversions=operations.field_inversions + field_inversions,
        point_membership_checks=(
            operations.point_membership_checks + point_membership_checks
        ),
        chart_curve_transforms=(
            operations.chart_curve_transforms + chart_curve_transforms
        ),
        chart_point_transforms=(
            operations.chart_point_transforms + chart_point_transforms
        ),
        unordered_pairs_enumerated=(
            operations.unordered_pairs_enumerated + unordered_pairs_enumerated
        ),
        ec_additions=operations.ec_additions + ec_additions,
        secant_branches=operations.secant_branches + secant_branches,
        tangent_branches=operations.tangent_branches + tangent_branches,
        vertical_pairs_excluded=(
            operations.vertical_pairs_excluded + vertical_pairs_excluded
        ),
        fiber_witnesses_inserted=(
            operations.fiber_witnesses_inserted + fiber_witnesses_inserted
        ),
        sort_keys_emitted=operations.sort_keys_emitted + sort_keys_emitted,
        representative_keys_compared=(
            operations.representative_keys_compared
            + representative_keys_compared
        ),
        slope_collision_checks=(
            operations.slope_collision_checks + slope_collision_checks
        ),
    )


def _failure(
    code: CoreErrorCode,
    indices: tuple[int, ...],
    operations: CoreOps,
) -> Failure:
    return Failure(
        error=CoreError(
            code=code,
            api=CoreApi.BUILD_CANDIDATE_CORE,
            indices=indices,
        ),
        operations=operations,
    )


def _reduce(value: int, p: int, operations: CoreOps) -> tuple[int, CoreOps]:
    operations = _tick(operations, field_reductions=1)
    return value % p, operations


def _add(
    left: int,
    right: int,
    p: int,
    operations: CoreOps,
) -> tuple[int, CoreOps]:
    operations = _tick(operations, field_additions=1)
    return (left + right) % p, operations


def _subtract(
    left: int,
    right: int,
    p: int,
    operations: CoreOps,
) -> tuple[int, CoreOps]:
    operations = _tick(operations, field_subtractions=1)
    return (left - right) % p, operations


def _multiply(
    left: int,
    right: int,
    p: int,
    operations: CoreOps,
) -> tuple[int, CoreOps]:
    operations = _tick(operations, field_multiplications=1)
    return (left * right) % p, operations


def _square(
    value: int,
    p: int,
    operations: CoreOps,
) -> tuple[int, CoreOps]:
    operations = _tick(operations, field_squarings=1)
    return (value * value) % p, operations


def _negate(
    value: int,
    p: int,
    operations: CoreOps,
) -> tuple[int, CoreOps]:
    operations = _tick(operations, field_negations=1)
    return (-value) % p, operations


def _invert(
    value: int,
    p: int,
    operations: CoreOps,
) -> tuple[int, CoreOps]:
    operations = _tick(operations, field_inversions=1)
    return pow(value, -1, p), operations


def _membership(
    curve: Curve,
    point: AffinePoint,
    operations: CoreOps,
) -> tuple[bool, CoreOps]:
    operations = _tick(operations, point_membership_checks=1)
    y2, operations = _square(point.y, curve.p, operations)
    x2, operations = _square(point.x, curve.p, operations)
    x3, operations = _multiply(x2, point.x, curve.p, operations)
    ax, operations = _multiply(curve.a, point.x, curve.p, operations)
    rhs, operations = _add(x3, ax, curve.p, operations)
    rhs, operations = _add(rhs, curve.b, curve.p, operations)
    difference, operations = _subtract(y2, rhs, curve.p, operations)
    return difference == 0, operations


def build_candidate_core(
    raw: CurveInput,
    points: tuple[AffinePoint, ...],
    u: int,
) -> CoreResult[CandidateCore]:
    operations = _zero_ops()

    if type(raw) is not CurveInput:
        return _failure(CoreErrorCode.TYPE_MISMATCH, (), operations)
    for field_index, field_value in ((0, raw.p), (1, raw.a), (2, raw.b)):
        if type(field_value) is not int:
            return _failure(
                CoreErrorCode.TYPE_MISMATCH,
                (field_index,),
                operations,
            )

    if raw.p <= 3:
        return _failure(
            CoreErrorCode.MODULUS_NOT_ODD_PRIME,
            (0,),
            operations,
        )
    operations = _tick(operations, integer_remainder_tests=1)
    if raw.p % 2 == 0:
        return _failure(
            CoreErrorCode.MODULUS_NOT_ODD_PRIME,
            (0,),
            operations,
        )
    divisor = 3
    while divisor * divisor <= raw.p:
        operations = _tick(operations, integer_remainder_tests=1)
        if raw.p % divisor == 0:
            return _failure(
                CoreErrorCode.MODULUS_NOT_ODD_PRIME,
                (0,),
                operations,
            )
        divisor += 2

    if raw.a < 0 or raw.a >= raw.p:
        return _failure(
            CoreErrorCode.NONCANONICAL_COEFFICIENT,
            (1,),
            operations,
        )
    if raw.b < 0 or raw.b >= raw.p:
        return _failure(
            CoreErrorCode.NONCANONICAL_COEFFICIENT,
            (2,),
            operations,
        )

    a2, operations = _square(raw.a, raw.p, operations)
    a3, operations = _multiply(a2, raw.a, raw.p, operations)
    term_a, operations = _multiply(4, a3, raw.p, operations)
    b2, operations = _square(raw.b, raw.p, operations)
    term_b, operations = _multiply(27, b2, raw.p, operations)
    discriminant, operations = _add(term_a, term_b, raw.p, operations)
    if discriminant == 0:
        return _failure(
            CoreErrorCode.SINGULAR_CURVE,
            (1, 2),
            operations,
        )
    curve = Curve(p=raw.p, a=raw.a, b=raw.b)

    if type(points) is not tuple:
        return _failure(CoreErrorCode.TYPE_MISMATCH, (3,), operations)
    if len(points) != 6:
        return _failure(
            CoreErrorCode.FACTOR_BASE_SIZE,
            (len(points),),
            operations,
        )
    for point_index, point in enumerate(points):
        if type(point) is not AffinePoint:
            return _failure(
                CoreErrorCode.TYPE_MISMATCH,
                (3, point_index),
                operations,
            )
        if type(point.x) is not int:
            return _failure(
                CoreErrorCode.TYPE_MISMATCH,
                (3, point_index, 0),
                operations,
            )
        if type(point.y) is not int:
            return _failure(
                CoreErrorCode.TYPE_MISMATCH,
                (3, point_index, 1),
                operations,
            )
        if point.x < 0 or point.x >= curve.p:
            return _failure(
                CoreErrorCode.NONCANONICAL_POINT,
                (point_index,),
                operations,
            )
        if point.y < 0 or point.y >= curve.p:
            return _failure(
                CoreErrorCode.NONCANONICAL_POINT,
                (point_index,),
                operations,
            )

    for point_index in range(6):
        for previous_index in range(point_index):
            if points[point_index] == points[previous_index]:
                return _failure(
                    CoreErrorCode.DUPLICATE_POINT,
                    (point_index,),
                    operations,
                )
    for point_index in range(1, 6):
        if points[point_index - 1] >= points[point_index]:
            return _failure(
                CoreErrorCode.FACTOR_BASE_ORDER,
                (point_index,),
                operations,
            )
    for point_index, point in enumerate(points):
        is_member, operations = _membership(curve, point, operations)
        if not is_member:
            return _failure(
                CoreErrorCode.POINT_NOT_ON_CURVE,
                (point_index,),
                operations,
            )
    for point_index, point in enumerate(points):
        if point.y == 0:
            return _failure(
                CoreErrorCode.TWO_TORSION_POINT,
                (point_index,),
                operations,
            )
    for point_index, point in enumerate(points):
        negative_y, operations = _negate(point.y, curve.p, operations)
        inverse_point = AffinePoint(x=point.x, y=negative_y)
        inverse_found = False
        for candidate in points:
            if candidate == inverse_point:
                inverse_found = True
                break
        if not inverse_found:
            return _failure(
                CoreErrorCode.FACTOR_BASE_NOT_SIGN_COMPLETE,
                (point_index,),
                operations,
            )

    if type(u) is not int:
        return _failure(CoreErrorCode.TYPE_MISMATCH, (4,), operations)
    u0, operations = _reduce(u, curve.p, operations)
    if u0 == 0:
        return _failure(
            CoreErrorCode.ZERO_CHART_SCALAR,
            (4,),
            operations,
        )

    operations = _tick(operations, chart_curve_transforms=1)
    u2, operations = _square(u0, curve.p, operations)
    u3, operations = _multiply(u2, u0, curve.p, operations)
    u4, operations = _square(u2, curve.p, operations)
    u6, operations = _multiply(u4, u2, curve.p, operations)
    chart_a, operations = _multiply(u4, curve.a, curve.p, operations)
    chart_b, operations = _multiply(u6, curve.b, curve.p, operations)
    chart_curve = Curve(p=curve.p, a=chart_a, b=chart_b)

    transformed_points = []
    for point in points:
        operations = _tick(operations, chart_point_transforms=1)
        chart_x, operations = _multiply(u2, point.x, curve.p, operations)
        chart_y, operations = _multiply(u3, point.y, curve.p, operations)
        transformed_points.append(AffinePoint(x=chart_x, y=chart_y))
    transformed_points.sort()
    operations = _tick(operations, sort_keys_emitted=6)
    sorted_chart_points = tuple(transformed_points)
    fixture = ChartFixture(
        curve=chart_curve,
        u=u0,
        factor_base=FactorBase(points=sorted_chart_points),
    )

    fiber_map: dict[AffinePoint, list[Witness]] = {}
    for i in range(6):
        for j in range(i, 6):
            operations = _tick(
                operations,
                unordered_pairs_enumerated=1,
                ec_additions=1,
            )
            left = sorted_chart_points[i]
            right = sorted_chart_points[j]

            if i == j:
                operations = _tick(operations, tangent_branches=1)
                x2, operations = _square(left.x, chart_curve.p, operations)
                three_x2, operations = _multiply(
                    3,
                    x2,
                    chart_curve.p,
                    operations,
                )
                numerator, operations = _add(
                    three_x2,
                    chart_curve.a,
                    chart_curve.p,
                    operations,
                )
                denominator, operations = _multiply(
                    2,
                    left.y,
                    chart_curve.p,
                    operations,
                )
                branch = AdditionBranch.TANGENT
            elif left.x == right.x:
                vertical_sum, operations = _add(
                    left.y,
                    right.y,
                    chart_curve.p,
                    operations,
                )
                if vertical_sum == 0:
                    operations = _tick(
                        operations,
                        vertical_pairs_excluded=1,
                    )
                    continue
                return _failure(
                    CoreErrorCode.INTERNAL_INVARIANT_FAILURE,
                    (i, j),
                    operations,
                )
            else:
                operations = _tick(operations, secant_branches=1)
                numerator, operations = _subtract(
                    right.y,
                    left.y,
                    chart_curve.p,
                    operations,
                )
                denominator, operations = _subtract(
                    right.x,
                    left.x,
                    chart_curve.p,
                    operations,
                )
                branch = AdditionBranch.SECANT

            if denominator == 0:
                return _failure(
                    CoreErrorCode.NONINVERTIBLE_DENOMINATOR,
                    (i, j),
                    operations,
                )
            denominator_inverse, operations = _invert(
                denominator,
                chart_curve.p,
                operations,
            )
            slope, operations = _multiply(
                numerator,
                denominator_inverse,
                chart_curve.p,
                operations,
            )
            slope2, operations = _square(
                slope,
                chart_curve.p,
                operations,
            )
            result_x, operations = _subtract(
                slope2,
                left.x,
                chart_curve.p,
                operations,
            )
            result_x, operations = _subtract(
                result_x,
                right.x,
                chart_curve.p,
                operations,
            )
            x_difference, operations = _subtract(
                left.x,
                result_x,
                chart_curve.p,
                operations,
            )
            result_y, operations = _multiply(
                slope,
                x_difference,
                chart_curve.p,
                operations,
            )
            result_y, operations = _subtract(
                result_y,
                left.y,
                chart_curve.p,
                operations,
            )
            result = AffinePoint(x=result_x, y=result_y)

            slope_x_left, operations = _multiply(
                slope,
                left.x,
                chart_curve.p,
                operations,
            )
            intercept_left, operations = _subtract(
                left.y,
                slope_x_left,
                chart_curve.p,
                operations,
            )
            negative_result_y, operations = _negate(
                result.y,
                chart_curve.p,
                operations,
            )
            slope_x_result, operations = _multiply(
                slope,
                result.x,
                chart_curve.p,
                operations,
            )
            intercept_right, operations = _subtract(
                negative_result_y,
                slope_x_result,
                chart_curve.p,
                operations,
            )

            is_member, operations = _membership(
                chart_curve,
                result,
                operations,
            )
            if not is_member:
                return _failure(
                    CoreErrorCode.INTERNAL_INVARIANT_FAILURE,
                    (i, j),
                    operations,
                )
            if intercept_left != intercept_right:
                return _failure(
                    CoreErrorCode.INTERCEPT_MISMATCH,
                    (i, j),
                    operations,
                )

            addition = Addition(
                result=result,
                branch=branch,
                slope=slope,
                intercept=intercept_left,
            )
            if type(addition.result) is not AffinePoint:
                return _failure(
                    CoreErrorCode.INTERNAL_INVARIANT_FAILURE,
                    (i, j),
                    operations,
                )
            witness = Witness(
                i=i,
                j=j,
                result=addition.result,
                slope=slope,
                intercept=intercept_left,
            )
            if result not in fiber_map:
                fiber_map[result] = []
            fiber_map[result].append(witness)
            operations = _tick(
                operations,
                fiber_witnesses_inserted=1,
            )

    ordered_results = sorted(fiber_map)
    operations = _tick(
        operations,
        sort_keys_emitted=len(ordered_results),
    )
    fibers_list = []
    for result in ordered_results:
        fibers_list.append(
            Fiber(
                result=result,
                witnesses=tuple(fiber_map[result]),
            )
        )
    fibers = tuple(fibers_list)

    representatives_list = []
    nonsingleton_fiber_count = 0
    choice_product = 1
    minimum_slope_tie_fibers = 0
    slope_collision_pairs = 0
    for fiber in fibers:
        witness_count = len(fiber.witnesses)
        if witness_count == 0:
            return _failure(
                CoreErrorCode.INTERNAL_INVARIANT_FAILURE,
                (),
                operations,
            )
        if witness_count >= 2:
            nonsingleton_fiber_count += 1
        choice_product *= witness_count

        best = fiber.witnesses[0]
        for witness in fiber.witnesses[1:]:
            operations = _tick(
                operations,
                representative_keys_compared=1,
            )
            if (
                witness.slope,
                witness.i,
                witness.j,
            ) < (
                best.slope,
                best.i,
                best.j,
            ):
                best = witness
        representatives_list.append(
            Representative(result=fiber.result, witness=best)
        )

        minimum_slope_count = 0
        for witness in fiber.witnesses:
            if witness.slope == best.slope:
                minimum_slope_count += 1
        if minimum_slope_count >= 2:
            minimum_slope_tie_fibers += 1

        for left_index in range(witness_count):
            for right_index in range(left_index + 1, witness_count):
                operations = _tick(
                    operations,
                    slope_collision_checks=1,
                )
                if (
                    fiber.witnesses[left_index].slope
                    == fiber.witnesses[right_index].slope
                ):
                    slope_collision_pairs += 1

    diagnostics = SectionDiagnostics(
        nonidentity_fiber_count=len(fibers),
        nonsingleton_fiber_count=nonsingleton_fiber_count,
        choice_product=choice_product,
        minimum_slope_tie_fibers=minimum_slope_tie_fibers,
        slope_collision_pairs=slope_collision_pairs,
    )
    value = CandidateCore(
        fixture=fixture,
        fibers=FiberSet(fibers=fibers),
        representatives=RepresentativeTable(
            entries=tuple(representatives_list)
        ),
        diagnostics=diagnostics,
    )
    return Success(value=value, operations=operations)


__all__ = (
    "Addition",
    "AdditionBranch",
    "AffinePoint",
    "CandidateCore",
    "ChartFixture",
    "CoreApi",
    "CoreError",
    "CoreErrorCode",
    "CoreOps",
    "CoreResult",
    "Curve",
    "CurveInput",
    "FactorBase",
    "Failure",
    "Fiber",
    "FiberSet",
    "Infinity",
    "Representative",
    "RepresentativeTable",
    "SectionDiagnostics",
    "Success",
    "Witness",
    "build_candidate_core",
)
