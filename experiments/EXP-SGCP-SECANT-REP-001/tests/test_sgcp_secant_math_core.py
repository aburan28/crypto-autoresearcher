"""Independent public-API tests derived only from pure-core API V6/V7.

Author principal: 019fac44-cb7d-78c1-baa6-a1d224f398d0

This module intentionally contains no implementation inspection, private access,
dynamic introspection, fault injection, external input, or nondeterminism.

Static invariant proof obligations
==================================

NONINVERTIBLE_DENOMINATOR
    A retained tangent has denominator 2*y.  The validated modulus is an odd
    prime and factor-base validation excludes y == 0, so that denominator is a
    nonzero field element.  A retained secant is selected only when the two
    canonical x coordinates differ, so x_j - x_i is nonzero in the field.
    Every nonzero element of the validated prime field is invertible.

INTERCEPT_MISMATCH
    The affine result definition gives
        y_R = lambda*(x_i - x_R) - y_i.
    Rearrangement in the field gives
        y_i - lambda*x_i = -y_R - lambda*x_R.
    Both reported intercept expressions are canonical reductions of these two
    equal field elements, hence they cannot differ.

INTERNAL_INVARIANT_FAILURE
    For distinct validated points with equal x, curve membership gives equal
    y-squares.  Over an odd prime field the two roots are y and -y; duplicates
    are excluded and sign completeness supplies the partner, so their y-sum is
    zero and the pair is vertical.  For every retained pair, the standard
    affine chord/tangent formulas over a nonsingular curve with an invertible
    denominator produce another curve point.  Witness indices are emitted only
    by the closed six-point lexicographic pair enumeration.  Thus each public
    path protected by this invariant is closed after successful validation.

These obligations are deliberately not executable tests: V6/V7 make the three
codes unreachable through accepted public inputs.
"""

from dataclasses import FrozenInstanceError
from itertools import combinations
from types import MappingProxyType
import unittest

from sgcp_secant_math_core import (
    AffinePoint,
    CandidateCore,
    ChartFixture,
    CoreApi,
    CoreError,
    CoreErrorCode,
    CoreOps,
    Curve,
    CurveInput,
    FactorBase,
    Failure,
    Fiber,
    FiberSet,
    Representative,
    RepresentativeTable,
    SectionDiagnostics,
    Success,
    Witness,
    build_candidate_core,
)


_PRIMES = (7, 11, 13, 17, 19, 23)

_REMAINDER_COUNTS = MappingProxyType({
    2: 0,
    5: 1,
    7: 1,
    8: 1,
    9: 2,
    11: 2,
    13: 2,
    17: 2,
    19: 2,
    23: 2,
})

_RECIPROCALS = MappingProxyType({
    7: (None, 1, 4, 5, 2, 3, 6),
    11: (None, 1, 6, 4, 3, 9, 2, 8, 7, 5, 10),
    13: (None, 1, 7, 9, 10, 8, 11, 2, 5, 3, 4, 6, 12),
    17: (None, 1, 9, 6, 13, 7, 3, 5, 15, 2, 12, 14, 10, 4, 11, 8, 16),
    19: (
        None, 1, 10, 13, 5, 4, 16, 11, 12, 17,
        2, 7, 8, 3, 15, 14, 6, 9, 18,
    ),
    23: (
        None, 1, 12, 8, 6, 14, 4, 10, 3, 18, 7, 21,
        2, 16, 5, 20, 13, 19, 9, 17, 15, 11, 22,
    ),
})


def _remainder_count_for(modulus):
    try:
        return _REMAINDER_COUNTS[modulus]
    except KeyError as error:
        raise AssertionError(
            "no hand-derived remainder count for control modulus"
        ) from error


def _modular_reciprocal(value, modulus):
    canonical = value % modulus
    try:
        table = _RECIPROCALS[modulus]
    except KeyError as error:
        raise AssertionError(
            "no hand-derived reciprocal table for control modulus"
        ) from error
    if canonical == 0:
        raise ArithmeticError("reference denominator is not invertible")
    try:
        reciprocal = table[canonical]
    except IndexError as error:
        raise AssertionError(
            "control denominator is outside its reciprocal table"
        ) from error
    if reciprocal is None:
        raise AssertionError("control reciprocal table has an empty entry")
    return reciprocal


def _is_nonsingular(p, a, b):
    return (4 * a * a * a + 27 * b * b) % p != 0


def _is_on_curve(p, a, b, point):
    x, y = point
    return (y * y - x * x * x - a * x - b) % p == 0


def _affine_points(p, a, b):
    return tuple(
        (x, y)
        for x in range(p)
        for y in range(p)
        if _is_on_curve(p, a, b, (x, y))
    )


def _public_ops(
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
):
    return CoreOps(
        integer_remainder_tests=integer_remainder_tests,
        field_reductions=field_reductions,
        field_additions=field_additions,
        field_subtractions=field_subtractions,
        field_multiplications=field_multiplications,
        field_squarings=field_squarings,
        field_negations=field_negations,
        field_inversions=field_inversions,
        point_membership_checks=point_membership_checks,
        chart_curve_transforms=chart_curve_transforms,
        chart_point_transforms=chart_point_transforms,
        unordered_pairs_enumerated=unordered_pairs_enumerated,
        ec_additions=ec_additions,
        secant_branches=secant_branches,
        tangent_branches=tangent_branches,
        vertical_pairs_excluded=vertical_pairs_excluded,
        fiber_witnesses_inserted=fiber_witnesses_inserted,
        sort_keys_emitted=sort_keys_emitted,
        representative_keys_compared=representative_keys_compared,
        slope_collision_checks=slope_collision_checks,
    )


def _ops_values(ops):
    """Explicit field inventory; deliberately avoids reflective field discovery."""
    return (
        ops.integer_remainder_tests,
        ops.field_reductions,
        ops.field_additions,
        ops.field_subtractions,
        ops.field_multiplications,
        ops.field_squarings,
        ops.field_negations,
        ops.field_inversions,
        ops.point_membership_checks,
        ops.chart_curve_transforms,
        ops.chart_point_transforms,
        ops.unordered_pairs_enumerated,
        ops.ec_additions,
        ops.secant_branches,
        ops.tangent_branches,
        ops.vertical_pairs_excluded,
        ops.fiber_witnesses_inserted,
        ops.sort_keys_emitted,
        ops.representative_keys_compared,
        ops.slope_collision_checks,
    )


def _post_discriminant_prefix(p, membership_visits=0, sign_visits=0, reductions=0):
    return _public_ops(
        integer_remainder_tests=_remainder_count_for(p),
        field_reductions=reductions,
        field_additions=1 + 2 * membership_visits,
        field_subtractions=membership_visits,
        field_multiplications=3 + 2 * membership_visits,
        field_squarings=2 + 2 * membership_visits,
        field_negations=sign_visits,
        point_membership_checks=membership_visits,
    )


def _reference_pair_sum(curve, left, right):
    p, a = curve.p, curve.a
    x_left, y_left = left
    x_right, y_right = right
    if left == right:
        top = (3 * x_left * x_left + a) % p
        bottom = (2 * y_left) % p
        branch = "tangent"
    elif x_left == x_right:
        if (y_left + y_right) % p != 0:
            raise AssertionError("reference equal-x pair is not vertical")
        return None
    else:
        top = (y_right - y_left) % p
        bottom = (x_right - x_left) % p
        branch = "secant"

    slope = (top * _modular_reciprocal(bottom, p)) % p
    result_x = (slope * slope - x_left - x_right) % p
    result_y = (slope * (x_left - result_x) - y_left) % p
    intercept = (y_left - slope * x_left) % p
    result = (result_x, result_y)
    if not _is_on_curve(p, curve.a, curve.b, result):
        raise AssertionError("independent affine formula left the curve")
    return branch, result, slope, intercept


def _reference_candidate(raw, source_points, raw_u):
    p = raw.p
    u0 = raw_u % p
    u2 = u0 * u0 % p
    u3 = u2 * u0 % p
    u4 = u2 * u2 % p
    u6 = u4 * u2 % p
    chart_curve = Curve(p, u4 * raw.a % p, u6 * raw.b % p)
    transformed_in_source_order = tuple(
        (u2 * point.x % p, u3 * point.y % p) for point in source_points
    )
    chart_points = tuple(sorted(transformed_in_source_order))

    grouped = {}
    vertical_pairs = []
    tangent_count = 0
    secant_count = 0
    for i in range(6):
        for j in range(i, 6):
            addition = _reference_pair_sum(chart_curve, chart_points[i], chart_points[j])
            if addition is None:
                vertical_pairs.append((i, j))
                continue
            branch, result, slope, intercept = addition
            if branch == "tangent":
                tangent_count += 1
            else:
                secant_count += 1
            witness = Witness(i, j, AffinePoint(*result), slope, intercept)
            grouped.setdefault(result, []).append(witness)

    fibers = tuple(
        Fiber(AffinePoint(*result), tuple(grouped[result]))
        for result in sorted(grouped)
    )
    representatives = tuple(
        Representative(
            fiber.result,
            min(fiber.witnesses, key=lambda witness: (witness.slope, witness.i, witness.j)),
        )
        for fiber in fibers
    )

    nonsingleton = 0
    choice_product = 1
    minimum_ties = 0
    collision_pairs = 0
    collision_checks = 0
    for fiber in fibers:
        count = len(fiber.witnesses)
        choice_product *= count
        if count >= 2:
            nonsingleton += 1
        minimum_slope = min(witness.slope for witness in fiber.witnesses)
        if sum(witness.slope == minimum_slope for witness in fiber.witnesses) >= 2:
            minimum_ties += 1
        for left_index in range(count):
            for right_index in range(left_index + 1, count):
                collision_checks += 1
                if (
                    fiber.witnesses[left_index].slope
                    == fiber.witnesses[right_index].slope
                ):
                    collision_pairs += 1

    diagnostics = SectionDiagnostics(
        nonidentity_fiber_count=len(fibers),
        nonsingleton_fiber_count=nonsingleton,
        choice_product=choice_product,
        minimum_slope_tie_fibers=minimum_ties,
        slope_collision_pairs=collision_pairs,
    )
    expected = CandidateCore(
        fixture=ChartFixture(
            curve=chart_curve,
            u=u0,
            factor_base=FactorBase(tuple(AffinePoint(*point) for point in chart_points)),
        ),
        fibers=FiberSet(fibers),
        representatives=RepresentativeTable(representatives),
        diagnostics=diagnostics,
    )
    branch_counts = (tangent_count, secant_count, len(vertical_pairs))
    return (
        expected,
        tuple(vertical_pairs),
        tuple(AffinePoint(*point) for point in transformed_in_source_order),
        collision_checks,
        branch_counts,
    )


def _successful_ops(raw, expected, collision_checks):
    fiber_count = len(expected.fibers.fibers)
    return _public_ops(
        integer_remainder_tests=_remainder_count_for(raw.p),
        field_reductions=1,
        field_additions=58,
        field_subtractions=156,
        field_multiplications=151,
        field_squarings=76,
        field_negations=24,
        field_inversions=18,
        point_membership_checks=24,
        chart_curve_transforms=1,
        chart_point_transforms=6,
        unordered_pairs_enumerated=21,
        ec_additions=21,
        secant_branches=12,
        tangent_branches=6,
        vertical_pairs_excluded=3,
        fiber_witnesses_inserted=18,
        sort_keys_emitted=6 + fiber_count,
        representative_keys_compared=18 - fiber_count,
        slope_collision_checks=collision_checks,
    )


def _find_positive_control():
    """Choose the first small control that makes all mutation checks material."""
    for p in _PRIMES:
        for a in range(p):
            for b in range(p):
                if not _is_nonsingular(p, a, b):
                    continue
                by_x = {}
                for x, y in _affine_points(p, a, b):
                    if y != 0:
                        by_x.setdefault(x, []).append(y)
                sign_pairs = tuple(
                    ((x, min(ys)), (x, max(ys)))
                    for x, ys in sorted(by_x.items())
                    if len(ys) == 2 and (min(ys) + max(ys)) % p == 0
                )
                for three_pairs in combinations(sign_pairs, 3):
                    raw_points = tuple(
                        AffinePoint(*point)
                        for pair in three_pairs
                        for point in pair
                    )
                    raw = CurveInput(p, a, b)
                    for u in range(2, p):
                        model = _reference_candidate(raw, raw_points, u)
                        expected, _, transformed_order, _, _ = model
                        reordered = transformed_order != expected.fixture.factor_base.points
                        meaningful_choice = any(
                            len(fiber.witnesses) > 1
                            and min(
                                fiber.witnesses,
                                key=lambda witness: (
                                    witness.slope,
                                    witness.i,
                                    witness.j,
                                ),
                            )
                            != fiber.witnesses[0]
                            for fiber in expected.fibers.fibers
                        )
                        if reordered and meaningful_choice:
                            return raw, raw_points, u, model
    raise AssertionError("fixed finite control search found no mutation-sensitive case")


def _replace_point(points, index, replacement):
    return points[:index] + (replacement,) + points[index + 1 :]


def _off_curve_control(raw, points):
    existing = tuple((point.x, point.y) for point in points)
    for index in range(6):
        for x in range(raw.p):
            for y in range(raw.p):
                candidate = (x, y)
                if candidate in existing or _is_on_curve(raw.p, raw.a, raw.b, candidate):
                    continue
                trial = _replace_point(points, index, AffinePoint(x, y))
                keys = tuple((point.x, point.y) for point in trial)
                if keys == tuple(sorted(keys)) and len(set(keys)) == 6:
                    return trial, index
    raise AssertionError("fixed control search found no ordered off-curve replacement")


def _two_torsion_control():
    for p in _PRIMES:
        for a in range(p):
            for b in range(p):
                if not _is_nonsingular(p, a, b):
                    continue
                all_points = _affine_points(p, a, b)
                zeros = tuple(point for point in all_points if point[1] == 0)
                if not zeros or len(all_points) < 6:
                    continue
                for zero in zeros:
                    chosen = tuple(sorted((zero,) + tuple(
                        point for point in all_points if point != zero
                    )[:5]))
                    if len(chosen) == 6:
                        index = chosen.index(zero)
                        return (
                            CurveInput(p, a, b),
                            tuple(AffinePoint(*point) for point in chosen),
                            index,
                        )
    raise AssertionError("fixed control search found no six-point two-torsion case")


def _missing_sign_control():
    for p in _PRIMES:
        for a in range(p):
            for b in range(p):
                if not _is_nonsingular(p, a, b):
                    continue
                nonzero = tuple(
                    point for point in _affine_points(p, a, b) if point[1] != 0
                )
                for chosen in combinations(nonzero, 6):
                    chosen_set = set(chosen)
                    first_missing = next(
                        (
                            index
                            for index, (x, y) in enumerate(chosen)
                            if (x, (-y) % p) not in chosen_set
                        ),
                        None,
                    )
                    if first_missing is not None:
                        return (
                            CurveInput(p, a, b),
                            tuple(AffinePoint(*point) for point in chosen),
                            first_missing,
                        )
    raise AssertionError("fixed control search found no incomplete-sign case")


class TestSgcpSecantMathCore(unittest.TestCase):
    def test_chart_witnesses_fibers_representatives_diagnostics_and_ops(self):
        raw, points, u, model = _find_positive_control()
        expected, vertical_pairs, transformed_order, collision_checks, branches = model

        result = build_candidate_core(raw, points, u)
        self.assertIsInstance(result, Success)
        self.assertEqual(result.value.fixture, expected.fixture)
        self.assertEqual(result.value.fibers, expected.fibers)
        self.assertEqual(result.value.representatives, expected.representatives)
        self.assertEqual(result.value.diagnostics, expected.diagnostics)

        actual_witnesses = tuple(
            witness
            for fiber in result.value.fibers.fibers
            for witness in fiber.witnesses
        )
        expected_witnesses = tuple(
            witness
            for fiber in expected.fibers.fibers
            for witness in fiber.witnesses
        )
        self.assertEqual(actual_witnesses, expected_witnesses)
        self.assertEqual(len(actual_witnesses), 18)

        retained_pairs = {(witness.i, witness.j) for witness in actual_witnesses}
        all_pairs = {(i, j) for i in range(6) for j in range(i, 6)}
        self.assertEqual(all_pairs - retained_pairs, set(vertical_pairs))
        self.assertEqual(len(vertical_pairs), 3)
        for i, j in vertical_pairs:
            left = result.value.fixture.factor_base.points[i]
            right = result.value.fixture.factor_base.points[j]
            self.assertLess(i, j)
            self.assertEqual(left.x, right.x)
            self.assertEqual((left.y + right.y) % raw.p, 0)

        self.assertEqual(branches, (6, 12, 3))
        expected_ops = _successful_ops(raw, expected, collision_checks)
        self.assertEqual(result.operations, expected_ops)
        self.assertEqual(_ops_values(result.operations), _ops_values(expected_ops))
        self.assertEqual(result.operations.tangent_branches, 6)
        self.assertEqual(result.operations.secant_branches, 12)
        self.assertEqual(result.operations.vertical_pairs_excluded, 3)
        self.assertEqual(result.operations.fiber_witnesses_inserted, 18)
        self.assertEqual(result.operations.unordered_pairs_enumerated, 21)
        self.assertEqual(result.operations.ec_additions, 21)

        chart_points = result.value.fixture.factor_base.points
        self.assertEqual(chart_points, tuple(sorted(chart_points)))
        self.assertNotEqual(transformed_order, chart_points)
        for witness in actual_witnesses:
            reference = _reference_pair_sum(
                result.value.fixture.curve,
                (chart_points[witness.i].x, chart_points[witness.i].y),
                (chart_points[witness.j].x, chart_points[witness.j].y),
            )
            self.assertIsNotNone(reference)
            _, point, slope, intercept = reference
            self.assertEqual(witness.result, AffinePoint(*point))
            self.assertEqual(witness.slope, slope)
            self.assertEqual(witness.intercept, intercept)

        self.assertEqual(
            sum(len(fiber.witnesses) for fiber in result.value.fibers.fibers),
            18,
        )
        self.assertEqual(
            result.operations.representative_keys_compared,
            18 - len(result.value.fibers.fibers),
        )
        self.assertEqual(
            result.operations.sort_keys_emitted,
            6 + len(result.value.fibers.fibers),
        )

    def test_chart_scalar_congruence_and_least_slope_selection(self):
        raw, points, u, model = _find_positive_control()
        expected, _, _, _, _ = model
        base = build_candidate_core(raw, points, u)
        congruent = build_candidate_core(raw, points, u + raw.p)

        self.assertIsInstance(base, Success)
        self.assertIsInstance(congruent, Success)
        self.assertEqual(base, congruent)
        self.assertEqual(base.value.fixture.u, u % raw.p)
        self.assertEqual(base.value, expected)

        meaningful_choices = 0
        for fiber, representative in zip(
            base.value.fibers.fibers,
            base.value.representatives.entries,
        ):
            chosen = min(
                fiber.witnesses,
                key=lambda witness: (witness.slope, witness.i, witness.j),
            )
            self.assertEqual(representative.result, fiber.result)
            self.assertEqual(representative.witness, chosen)
            if len(fiber.witnesses) > 1 and chosen != fiber.witnesses[0]:
                meaningful_choices += 1
        self.assertGreater(meaningful_choices, 0)

    def test_public_results_and_inputs_are_immutable(self):
        raw, points, u, _ = _find_positive_control()
        raw_snapshot = CurveInput(raw.p, raw.a, raw.b)
        points_snapshot = tuple(AffinePoint(point.x, point.y) for point in points)
        result = build_candidate_core(raw, points, u)

        self.assertIsInstance(result, Success)
        self.assertEqual(raw, raw_snapshot)
        self.assertEqual(points, points_snapshot)
        witness = next(
            witness
            for fiber in result.value.fibers.fibers
            for witness in fiber.witnesses
        )
        with self.assertRaises(FrozenInstanceError):
            result.value.fixture.u = 0
        with self.assertRaises(FrozenInstanceError):
            result.value.fixture.factor_base.points = ()
        with self.assertRaises(FrozenInstanceError):
            witness.slope = 0
        with self.assertRaises(FrozenInstanceError):
            result.operations.ec_additions = 0
        with self.assertRaises(TypeError):
            result.value.fixture.factor_base.points[0] = AffinePoint(0, 0)

    def test_every_reachable_domain_error_and_charged_prefix(self):
        raw, points, _, _ = _find_positive_control()
        off_curve_points, off_curve_index = _off_curve_control(raw, points)
        torsion_raw, torsion_points, torsion_index = _two_torsion_control()
        sign_raw, sign_points, sign_index = _missing_sign_control()

        duplicate_points = _replace_point(points, 1, points[0])
        unordered_points = (points[1], points[0]) + points[2:]
        bad_point_object = points[:2] + (None,) + points[3:]
        bad_x_type = _replace_point(points, 2, AffinePoint(True, points[2].y))
        bad_y_type = _replace_point(points, 2, AffinePoint(points[2].x, False))
        bad_x_range = _replace_point(points, 2, AffinePoint(-1, points[2].y))
        bad_y_range = _replace_point(points, 2, AffinePoint(points[2].x, raw.p))

        after_curve = _post_discriminant_prefix(raw.p)
        after_factor_base = _post_discriminant_prefix(
            raw.p, membership_visits=6, sign_visits=6
        )
        cases = (
            (
                "raw_exact_type",
                None,
                points,
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (),
                _public_ops(),
            ),
            (
                "p_exact_type",
                CurveInput(True, raw.a, raw.b),
                points,
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (0,),
                _public_ops(),
            ),
            (
                "a_exact_type",
                CurveInput(raw.p, False, raw.b),
                points,
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (1,),
                _public_ops(),
            ),
            (
                "b_exact_type",
                CurveInput(raw.p, raw.a, False),
                points,
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (2,),
                _public_ops(),
            ),
            (
                "modulus_too_small",
                CurveInput(2, 0, 0),
                points,
                1,
                CoreErrorCode.MODULUS_NOT_ODD_PRIME,
                (0,),
                _public_ops(integer_remainder_tests=0),
            ),
            (
                "modulus_even",
                CurveInput(8, 0, 1),
                points,
                1,
                CoreErrorCode.MODULUS_NOT_ODD_PRIME,
                (0,),
                _public_ops(integer_remainder_tests=1),
            ),
            (
                "modulus_odd_composite",
                CurveInput(9, 0, 1),
                points,
                1,
                CoreErrorCode.MODULUS_NOT_ODD_PRIME,
                (0,),
                _public_ops(integer_remainder_tests=2),
            ),
            (
                "noncanonical_a",
                CurveInput(raw.p, raw.p, raw.b),
                points,
                1,
                CoreErrorCode.NONCANONICAL_COEFFICIENT,
                (1,),
                _public_ops(integer_remainder_tests=_remainder_count_for(raw.p)),
            ),
            (
                "noncanonical_b",
                CurveInput(raw.p, raw.a, raw.p),
                points,
                1,
                CoreErrorCode.NONCANONICAL_COEFFICIENT,
                (2,),
                _public_ops(integer_remainder_tests=_remainder_count_for(raw.p)),
            ),
            (
                "singular",
                CurveInput(5, 0, 0),
                points,
                1,
                CoreErrorCode.SINGULAR_CURVE,
                (1, 2),
                _public_ops(
                    integer_remainder_tests=1,
                    field_additions=1,
                    field_multiplications=3,
                    field_squarings=2,
                ),
            ),
            (
                "points_exact_tuple",
                raw,
                list(points),
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (3,),
                after_curve,
            ),
            (
                "factor_base_length",
                raw,
                points[:-1],
                1,
                CoreErrorCode.FACTOR_BASE_SIZE,
                (5,),
                after_curve,
            ),
            (
                "point_exact_type",
                raw,
                bad_point_object,
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2),
                after_curve,
            ),
            (
                "x_exact_type",
                raw,
                bad_x_type,
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2, 0),
                after_curve,
            ),
            (
                "y_exact_type",
                raw,
                bad_y_type,
                1,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2, 1),
                after_curve,
            ),
            (
                "x_canonical_range",
                raw,
                bad_x_range,
                1,
                CoreErrorCode.NONCANONICAL_POINT,
                (2,),
                after_curve,
            ),
            (
                "y_canonical_range",
                raw,
                bad_y_range,
                1,
                CoreErrorCode.NONCANONICAL_POINT,
                (2,),
                after_curve,
            ),
            (
                "duplicate_second_occurrence",
                raw,
                duplicate_points,
                1,
                CoreErrorCode.DUPLICATE_POINT,
                (1,),
                after_curve,
            ),
            (
                "factor_base_order",
                raw,
                unordered_points,
                1,
                CoreErrorCode.FACTOR_BASE_ORDER,
                (1,),
                after_curve,
            ),
            (
                "point_membership",
                raw,
                off_curve_points,
                1,
                CoreErrorCode.POINT_NOT_ON_CURVE,
                (off_curve_index,),
                _post_discriminant_prefix(
                    raw.p, membership_visits=off_curve_index + 1
                ),
            ),
            (
                "two_torsion",
                torsion_raw,
                torsion_points,
                1,
                CoreErrorCode.TWO_TORSION_POINT,
                (torsion_index,),
                _post_discriminant_prefix(
                    torsion_raw.p, membership_visits=6
                ),
            ),
            (
                "sign_completeness",
                sign_raw,
                sign_points,
                False,
                CoreErrorCode.FACTOR_BASE_NOT_SIGN_COMPLETE,
                (sign_index,),
                _post_discriminant_prefix(
                    sign_raw.p,
                    membership_visits=6,
                    sign_visits=sign_index + 1,
                ),
            ),
            (
                "chart_scalar_exact_type",
                raw,
                points,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (4,),
                after_factor_base,
            ),
            (
                "zero_chart_scalar",
                raw,
                points,
                raw.p,
                CoreErrorCode.ZERO_CHART_SCALAR,
                (4,),
                _post_discriminant_prefix(
                    raw.p,
                    membership_visits=6,
                    sign_visits=6,
                    reductions=1,
                ),
            ),
        )

        reached_codes = set()
        for (
            label,
            case_raw,
            case_points,
            case_u,
            code,
            indices,
            expected_ops,
        ) in cases:
            with self.subTest(label=label):
                result = build_candidate_core(case_raw, case_points, case_u)
                self.assertIsInstance(result, Failure)
                self.assertEqual(
                    result.error,
                    CoreError(code, CoreApi.BUILD_CANDIDATE_CORE, indices),
                )
                self.assertEqual(result.operations, expected_ops)
                self.assertEqual(
                    _ops_values(result.operations),
                    _ops_values(expected_ops),
                )
                reached_codes.add(code)

        self.assertEqual(
            reached_codes,
            {
                CoreErrorCode.TYPE_MISMATCH,
                CoreErrorCode.MODULUS_NOT_ODD_PRIME,
                CoreErrorCode.NONCANONICAL_COEFFICIENT,
                CoreErrorCode.SINGULAR_CURVE,
                CoreErrorCode.FACTOR_BASE_SIZE,
                CoreErrorCode.NONCANONICAL_POINT,
                CoreErrorCode.DUPLICATE_POINT,
                CoreErrorCode.FACTOR_BASE_ORDER,
                CoreErrorCode.POINT_NOT_ON_CURVE,
                CoreErrorCode.TWO_TORSION_POINT,
                CoreErrorCode.FACTOR_BASE_NOT_SIGN_COMPLETE,
                CoreErrorCode.ZERO_CHART_SCALAR,
            },
        )

    def test_first_error_precedence(self):
        raw, points, _, _ = _find_positive_control()
        torsion_raw, torsion_points, torsion_index = _two_torsion_control()
        sign_raw, sign_points, sign_index = _missing_sign_control()
        both_bad_coordinates = _replace_point(
            points, 2, AffinePoint(False, False)
        )
        earlier_bad_y = _replace_point(
            points, 1, AffinePoint(points[1].x, False)
        )
        earlier_and_later_bad_points = _replace_point(
            earlier_bad_y, 4, AffinePoint(False, points[4].y)
        )
        wrong_point_with_coordinate_payload = _replace_point(
            points, 2, (-1, False)
        )
        bad_x_type_and_range = _replace_point(
            points, 2, AffinePoint(-1.5, points[2].y)
        )
        bad_x_type_and_y_range = _replace_point(
            points, 2, AffinePoint(False, raw.p)
        )
        bad_x_range_and_y_type = _replace_point(
            points, 2, AffinePoint(-1, False)
        )
        bad_y_type_and_range = _replace_point(
            points, 2, AffinePoint(points[2].x, raw.p + 0.5)
        )
        earlier_bad_y_range = _replace_point(
            points, 1, AffinePoint(points[1].x, raw.p)
        )
        earlier_complete_and_later_bad_x = _replace_point(
            earlier_bad_y_range, 4, AffinePoint(False, points[4].y)
        )

        cases = (
            (
                "p_type_before_a_and_b_type",
                CurveInput(False, False, False),
                None,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (0,),
                _public_ops(),
            ),
            (
                "a_type_before_b_type",
                CurveInput(raw.p, False, False),
                None,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (1,),
                _public_ops(),
            ),
            (
                "modulus_before_coefficients",
                CurveInput(9, 9, 9),
                None,
                False,
                CoreErrorCode.MODULUS_NOT_ODD_PRIME,
                (0,),
                _public_ops(integer_remainder_tests=2),
            ),
            (
                "a_before_b_coefficient",
                CurveInput(raw.p, raw.p, raw.p),
                None,
                False,
                CoreErrorCode.NONCANONICAL_COEFFICIENT,
                (1,),
                _public_ops(integer_remainder_tests=_remainder_count_for(raw.p)),
            ),
            (
                "singularity_before_factor_base",
                CurveInput(5, 0, 0),
                None,
                False,
                CoreErrorCode.SINGULAR_CURVE,
                (1, 2),
                _public_ops(
                    integer_remainder_tests=1,
                    field_additions=1,
                    field_multiplications=3,
                    field_squarings=2,
                ),
            ),
            (
                "point_type_before_coordinate_payload",
                raw,
                wrong_point_with_coordinate_payload,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "x_type_before_x_range",
                raw,
                bad_x_type_and_range,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2, 0),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "x_type_before_y_range",
                raw,
                bad_x_type_and_y_range,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2, 0),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "x_range_before_y_type",
                raw,
                bad_x_range_and_y_type,
                False,
                CoreErrorCode.NONCANONICAL_POINT,
                (2,),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "y_type_before_y_range",
                raw,
                bad_y_type_and_range,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2, 1),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "earlier_point_y_range_before_later_point_x_type",
                raw,
                earlier_complete_and_later_bad_x,
                False,
                CoreErrorCode.NONCANONICAL_POINT,
                (1,),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "x_field_before_y_field_within_point",
                raw,
                both_bad_coordinates,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 2, 0),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "point_index_before_later_coordinate_field",
                raw,
                earlier_and_later_bad_points,
                False,
                CoreErrorCode.TYPE_MISMATCH,
                (3, 1, 1),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "duplicate_before_order_membership_and_u",
                raw,
                _replace_point(points, 1, points[0]),
                False,
                CoreErrorCode.DUPLICATE_POINT,
                (1,),
                _post_discriminant_prefix(raw.p),
            ),
            (
                "two_torsion_before_sign_and_u",
                torsion_raw,
                torsion_points,
                False,
                CoreErrorCode.TWO_TORSION_POINT,
                (torsion_index,),
                _post_discriminant_prefix(
                    torsion_raw.p, membership_visits=6
                ),
            ),
            (
                "sign_before_u",
                sign_raw,
                sign_points,
                False,
                CoreErrorCode.FACTOR_BASE_NOT_SIGN_COMPLETE,
                (sign_index,),
                _post_discriminant_prefix(
                    sign_raw.p,
                    membership_visits=6,
                    sign_visits=sign_index + 1,
                ),
            ),
        )

        for label, case_raw, case_points, case_u, code, indices, operations in cases:
            with self.subTest(label=label):
                result = build_candidate_core(case_raw, case_points, case_u)
                self.assertIsInstance(result, Failure)
                self.assertEqual(
                    result.error,
                    CoreError(code, CoreApi.BUILD_CANDIDATE_CORE, indices),
                )
                self.assertEqual(result.operations, operations)
