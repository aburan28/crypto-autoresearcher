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


def _combine(left: CoreOps, right: CoreOps) -> CoreOps:
    return CoreOps(
        integer_remainder_tests=(
            left.integer_remainder_tests + right.integer_remainder_tests
        ),
        field_reductions=left.field_reductions + right.field_reductions,
        field_additions=left.field_additions + right.field_additions,
        field_subtractions=left.field_subtractions + right.field_subtractions,
        field_multiplications=(
            left.field_multiplications + right.field_multiplications
        ),
        field_squarings=left.field_squarings + right.field_squarings,
        field_negations=left.field_negations + right.field_negations,
        field_inversions=left.field_inversions + right.field_inversions,
        point_membership_checks=(
            left.point_membership_checks + right.point_membership_checks
        ),
        chart_curve_transforms=(
            left.chart_curve_transforms + right.chart_curve_transforms
        ),
        chart_point_transforms=(
            left.chart_point_transforms + right.chart_point_transforms
        ),
        unordered_pairs_enumerated=(
            left.unordered_pairs_enumerated
            + right.unordered_pairs_enumerated
        ),
        ec_additions=left.ec_additions + right.ec_additions,
        secant_branches=left.secant_branches + right.secant_branches,
        tangent_branches=left.tangent_branches + right.tangent_branches,
        vertical_pairs_excluded=(
            left.vertical_pairs_excluded + right.vertical_pairs_excluded
        ),
        fiber_witnesses_inserted=(
            left.fiber_witnesses_inserted
            + right.fiber_witnesses_inserted
        ),
        sort_keys_emitted=left.sort_keys_emitted + right.sort_keys_emitted,
        representative_keys_compared=(
            left.representative_keys_compared
            + right.representative_keys_compared
        ),
        slope_collision_checks=(
            left.slope_collision_checks + right.slope_collision_checks
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


def _reduce(value: int, p: int) -> tuple[int, CoreOps]:
    operations = _tick(_zero_ops(), field_reductions=1)
    return value % p, operations


def _add(
    left: int,
    right: int,
    p: int,
) -> tuple[int, CoreOps]:
    operations = _tick(_zero_ops(), field_additions=1)
    return (left + right) % p, operations


def _subtract(
    left: int,
    right: int,
    p: int,
) -> tuple[int, CoreOps]:
    operations = _tick(_zero_ops(), field_subtractions=1)
    return (left - right) % p, operations


def _multiply(
    left: int,
    right: int,
    p: int,
) -> tuple[int, CoreOps]:
    operations = _tick(_zero_ops(), field_multiplications=1)
    return (left * right) % p, operations


def _square(
    value: int,
    p: int,
) -> tuple[int, CoreOps]:
    operations = _tick(_zero_ops(), field_squarings=1)
    return (value * value) % p, operations


def _negate(
    value: int,
    p: int,
) -> tuple[int, CoreOps]:
    operations = _tick(_zero_ops(), field_negations=1)
    return (-value) % p, operations


def _invert(
    value: int,
    p: int,
) -> tuple[int, CoreOps]:
    operations = _tick(_zero_ops(), field_inversions=1)
    return pow(value, -1, p), operations


def _membership(
    curve: Curve,
    point: AffinePoint,
) -> tuple[bool, CoreOps]:
    operations = _tick(_zero_ops(), point_membership_checks=1)
    y2, event = _square(point.y, curve.p)
    operations = _combine(operations, event)
    x2, event = _square(point.x, curve.p)
    operations = _combine(operations, event)
    x3, event = _multiply(x2, point.x, curve.p)
    operations = _combine(operations, event)
    ax, event = _multiply(curve.a, point.x, curve.p)
    operations = _combine(operations, event)
    rhs, event = _add(x3, ax, curve.p)
    operations = _combine(operations, event)
    rhs, event = _add(rhs, curve.b, curve.p)
    operations = _combine(operations, event)
    difference, event = _subtract(y2, rhs, curve.p)
    operations = _combine(operations, event)
    return difference == 0, operations


def build_candidate_core(
    raw: CurveInput,
    points: tuple[AffinePoint, ...],
    u: int,
) -> CoreResult[CandidateCore]:
    operations = _zero_ops()
    phase_operations = _zero_ops()

    if type(raw) is not CurveInput:
        return _failure(CoreErrorCode.TYPE_MISMATCH, (), operations)
    for field_index, field_value in ((0, raw.p), (1, raw.a), (2, raw.b)):
        if type(field_value) is not int:
            return _failure(
                CoreErrorCode.TYPE_MISMATCH,
                (field_index,),
                operations,
            )

    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()
    if raw.p <= 3:
        return _failure(
            CoreErrorCode.MODULUS_NOT_ODD_PRIME,
            (0,),
            operations,
        )
    phase_operations = _tick(
        phase_operations,
        integer_remainder_tests=1,
    )
    if raw.p % 2 == 0:
        return _failure(
            CoreErrorCode.MODULUS_NOT_ODD_PRIME,
            (0,),
            _combine(operations, phase_operations),
        )
    divisor = 3
    while divisor * divisor <= raw.p:
        phase_operations = _tick(
            phase_operations,
            integer_remainder_tests=1,
        )
        if raw.p % divisor == 0:
            return _failure(
                CoreErrorCode.MODULUS_NOT_ODD_PRIME,
                (0,),
                _combine(operations, phase_operations),
            )
        divisor += 2

    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()
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

    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()
    a2, event = _square(raw.a, raw.p)
    phase_operations = _combine(phase_operations, event)
    a3, event = _multiply(a2, raw.a, raw.p)
    phase_operations = _combine(phase_operations, event)
    term_a, event = _multiply(4, a3, raw.p)
    phase_operations = _combine(phase_operations, event)
    b2, event = _square(raw.b, raw.p)
    phase_operations = _combine(phase_operations, event)
    term_b, event = _multiply(27, b2, raw.p)
    phase_operations = _combine(phase_operations, event)
    discriminant, event = _add(term_a, term_b, raw.p)
    phase_operations = _combine(phase_operations, event)
    if discriminant == 0:
        return _failure(
            CoreErrorCode.SINGULAR_CURVE,
            (1, 2),
            _combine(operations, phase_operations),
        )
    curve = Curve(p=raw.p, a=raw.a, b=raw.b)
    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()

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
        if point.x < 0 or point.x >= curve.p:
            return _failure(
                CoreErrorCode.NONCANONICAL_POINT,
                (point_index,),
                operations,
            )
        if type(point.y) is not int:
            return _failure(
                CoreErrorCode.TYPE_MISMATCH,
                (3, point_index, 1),
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
        is_member, event = _membership(curve, point)
        phase_operations = _combine(phase_operations, event)
        if not is_member:
            return _failure(
                CoreErrorCode.POINT_NOT_ON_CURVE,
                (point_index,),
                _combine(operations, phase_operations),
            )
    for point_index, point in enumerate(points):
        if point.y == 0:
            return _failure(
                CoreErrorCode.TWO_TORSION_POINT,
                (point_index,),
                _combine(operations, phase_operations),
            )
    for point_index, point in enumerate(points):
        negative_y, event = _negate(point.y, curve.p)
        phase_operations = _combine(phase_operations, event)
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
                _combine(operations, phase_operations),
            )

    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()
    if type(u) is not int:
        return _failure(CoreErrorCode.TYPE_MISMATCH, (4,), operations)
    u0, event = _reduce(u, curve.p)
    phase_operations = _combine(phase_operations, event)
    if u0 == 0:
        return _failure(
            CoreErrorCode.ZERO_CHART_SCALAR,
            (4,),
            _combine(operations, phase_operations),
        )

    phase_operations = _tick(
        phase_operations,
        chart_curve_transforms=1,
    )
    u2, event = _square(u0, curve.p)
    phase_operations = _combine(phase_operations, event)
    u3, event = _multiply(u2, u0, curve.p)
    phase_operations = _combine(phase_operations, event)
    u4, event = _square(u2, curve.p)
    phase_operations = _combine(phase_operations, event)
    u6, event = _multiply(u4, u2, curve.p)
    phase_operations = _combine(phase_operations, event)
    chart_a, event = _multiply(u4, curve.a, curve.p)
    phase_operations = _combine(phase_operations, event)
    chart_b, event = _multiply(u6, curve.b, curve.p)
    phase_operations = _combine(phase_operations, event)
    chart_curve = Curve(p=curve.p, a=chart_a, b=chart_b)

    transformed_points = []
    for point in points:
        phase_operations = _tick(
            phase_operations,
            chart_point_transforms=1,
        )
        chart_x, event = _multiply(u2, point.x, curve.p)
        phase_operations = _combine(phase_operations, event)
        chart_y, event = _multiply(u3, point.y, curve.p)
        phase_operations = _combine(phase_operations, event)
        transformed_points.append(AffinePoint(x=chart_x, y=chart_y))
    transformed_points.sort()
    phase_operations = _tick(phase_operations, sort_keys_emitted=6)
    sorted_chart_points = tuple(transformed_points)
    fixture = ChartFixture(
        curve=chart_curve,
        u=u0,
        factor_base=FactorBase(points=sorted_chart_points),
    )
    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()

    fiber_groups: list[tuple[AffinePoint, list[Witness]]] = []
    for i in range(6):
        for j in range(i, 6):
            phase_operations = _tick(
                phase_operations,
                unordered_pairs_enumerated=1,
            )
            phase_operations = _tick(
                phase_operations,
                ec_additions=1,
            )
            left = sorted_chart_points[i]
            right = sorted_chart_points[j]

            if i == j:
                phase_operations = _tick(
                    phase_operations,
                    tangent_branches=1,
                )
                x2, event = _square(left.x, chart_curve.p)
                phase_operations = _combine(phase_operations, event)
                three_x2, event = _multiply(3, x2, chart_curve.p)
                phase_operations = _combine(phase_operations, event)
                numerator, event = _add(
                    three_x2, chart_curve.a, chart_curve.p
                )
                phase_operations = _combine(phase_operations, event)
                denominator, event = _multiply(2, left.y, chart_curve.p)
                phase_operations = _combine(phase_operations, event)
                branch = AdditionBranch.TANGENT
            elif left.x == right.x:
                vertical_sum, event = _add(
                    left.y, right.y, chart_curve.p
                )
                phase_operations = _combine(phase_operations, event)
                if vertical_sum == 0:
                    phase_operations = _tick(
                        phase_operations,
                        vertical_pairs_excluded=1,
                    )
                    continue
                return _failure(
                    CoreErrorCode.INTERNAL_INVARIANT_FAILURE,
                    (i, j),
                    _combine(operations, phase_operations),
                )
            else:
                phase_operations = _tick(
                    phase_operations,
                    secant_branches=1,
                )
                numerator, event = _subtract(
                    right.y, left.y, chart_curve.p
                )
                phase_operations = _combine(phase_operations, event)
                denominator, event = _subtract(
                    right.x, left.x, chart_curve.p
                )
                phase_operations = _combine(phase_operations, event)
                branch = AdditionBranch.SECANT

            if denominator == 0:
                return _failure(
                    CoreErrorCode.NONINVERTIBLE_DENOMINATOR,
                    (i, j),
                    _combine(operations, phase_operations),
                )
            denominator_inverse, event = _invert(
                denominator, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            slope, event = _multiply(
                numerator,
                denominator_inverse,
                chart_curve.p,
            )
            phase_operations = _combine(phase_operations, event)
            slope2, event = _square(slope, chart_curve.p)
            phase_operations = _combine(phase_operations, event)
            result_x, event = _subtract(
                slope2, left.x, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            result_x, event = _subtract(
                result_x, right.x, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            x_difference, event = _subtract(
                left.x, result_x, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            result_y, event = _multiply(
                slope, x_difference, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            result_y, event = _subtract(
                result_y, left.y, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            result = AffinePoint(x=result_x, y=result_y)

            slope_x_left, event = _multiply(
                slope, left.x, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            intercept_left, event = _subtract(
                left.y, slope_x_left, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            negative_result_y, event = _negate(
                result.y, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            slope_x_result, event = _multiply(
                slope, result.x, chart_curve.p
            )
            phase_operations = _combine(phase_operations, event)
            intercept_right, event = _subtract(
                negative_result_y,
                slope_x_result,
                chart_curve.p,
            )
            phase_operations = _combine(phase_operations, event)

            is_member, event = _membership(chart_curve, result)
            phase_operations = _combine(phase_operations, event)
            if not is_member:
                return _failure(
                    CoreErrorCode.INTERNAL_INVARIANT_FAILURE,
                    (i, j),
                    _combine(operations, phase_operations),
                )
            if intercept_left != intercept_right:
                return _failure(
                    CoreErrorCode.INTERCEPT_MISMATCH,
                    (i, j),
                    _combine(operations, phase_operations),
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
                    _combine(operations, phase_operations),
                )
            witness = Witness(
                i=i,
                j=j,
                result=addition.result,
                slope=slope,
                intercept=intercept_left,
            )
            group_found = False
            for group_result, group_witnesses in fiber_groups:
                if group_result == result:
                    group_witnesses.append(witness)
                    group_found = True
                    break
            if not group_found:
                fiber_groups.append((result, [witness]))
            phase_operations = _tick(
                phase_operations,
                fiber_witnesses_inserted=1,
            )

    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()
    fiber_groups.sort()
    phase_operations = _tick(
        phase_operations,
        sort_keys_emitted=len(fiber_groups),
    )
    fibers_list = []
    for result, witnesses in fiber_groups:
        fibers_list.append(
            Fiber(
                result=result,
                witnesses=tuple(witnesses),
            )
        )
    fibers = tuple(fibers_list)
    operations = _combine(operations, phase_operations)
    phase_operations = _zero_ops()

    representatives_list = []
    nonsingleton_fiber_count = 0
    choice_product = 1
    minimum_slope_tie_fibers = 0
    slope_collision_pairs = 0
    for fiber in fibers:
        witness_count = len(fiber.witnesses)
        if witness_count >= 2:
            nonsingleton_fiber_count += 1
        choice_product *= witness_count

        best = fiber.witnesses[0]
        for witness in fiber.witnesses[1:]:
            phase_operations = _tick(
                phase_operations,
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
                phase_operations = _tick(
                    phase_operations,
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
    operations = _combine(operations, phase_operations)
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
