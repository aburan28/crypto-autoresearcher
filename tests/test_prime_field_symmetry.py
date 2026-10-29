"""Small public algebra controls for symmetry/domain/rank distinctions."""
from copy import deepcopy

import pytest

from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations
from crypto_autoresearcher.index_calculus.symmetry import (
    audit_orbit_rows, certify_diagonal, diagonal_point, project_public_translation)


def cubic_fixture():
    curve, P, order = Curve(7, 0, 3), (1, 2), 13
    base = [curve.mul(k, P) for k in [1, 3, 9, 2, 6, 5]]
    return curve, P, order, base


def test_cubic_orbit_rows_carry_no_new_information_after_known_action():
    curve, P, r, base = cubic_fixture()
    rows = [dict(coefficients=[1, 0, 0, 1, 0, 0], rhs=3)]
    result = audit_orbit_rows(curve, P, r, base, 4, 3, rows)
    assert result['action']['known_constraint_rank'] == 4
    assert result['rank_with_action_before'] == result['rank_after'] == 5  # six base logs remain unresolved
    assert result['additional_rank_after_known_action'] == 0
    seed_only = AffineRelations(r, 6)
    seed_only.add(rows[0]['coefficients'], rows[0]['rhs'])
    transformed = result['transported_rows'][0]
    assert seed_only.add(transformed['coefficients'], transformed['rhs'])  # naive extra-rank counter would grow
    before = [row+[0] for row in result['action']['known_log_constraints']]+[rows[0]['coefficients']+[0]]
    weights = transformed['original_row_weights']
    assert [sum(w*row[j] for w, row in zip(weights, before)) % r for j in range(7)] == transformed['coefficients']+[0]


def test_target_coefficient_is_transported_too():
    curve, P, r, base = cubic_fixture()
    Q = curve.mul(7, P)
    row = dict(coefficients=[1, 0, 0, 1, 0, 0], rhs=-4, target_coefficient=1)
    result = audit_orbit_rows(curve, P, r, base, 4, 3, [row], target=Q)
    assert result['transported_rows'][0]['target_coefficient'] == 3
    bad = deepcopy(row); bad['rhs'] += 1
    with pytest.raises(ValueError, match='group equation'):
        audit_orbit_rows(curve, P, r, base, 4, 3, [bad], target=Q)


def test_quartic_action_signs_and_rejections():
    curve, P, r = Curve(13, 1, 0), (4, 4), 5
    base = [P, curve.mul(2, P)]
    action = certify_diagonal(curve, P, r, base, 5, 2)
    assert action['signed_mapping'] == [[1, 1], [0, -1]]
    assert action['known_constraint_rank'] == 1
    for u, eigenvalue in [(5, 3), (2, 2), (0, 1), (1, 0)]:
        with pytest.raises(ValueError):
            certify_diagonal(curve, P, r, base, u, eigenvalue)
    # A rational torsion translation leaves the prime-order subgroup.
    T = (0, 0)
    assert curve.mul(r, curve.add(P, T)) == T
    with pytest.raises(ValueError, match='outside'):
        certify_diagonal(curve, P, r, [curve.add(P, T)], 5, 2)


def test_membership_sign_does_not_imply_curve_symmetry():
    curve = Curve(101, 2, 21)
    P = curve.lift_x(0)
    with pytest.raises(ValueError, match='not an automorphism'):
        certify_diagonal(curve, P, 107, [P], 10, 1)  # u²=-1, but generic b != 0
    result = certify_diagonal(curve, P, 107, [P], -1, -1)
    assert result['known_constraint_rank'] == 0
    assert result['signed_mapping'] == [[0, -1]]


def test_partial_closure_keeps_valid_edges_but_rejects_escaping_rows():
    curve, P, r, base = cubic_fixture()
    base = base[:2]
    action = certify_diagonal(curve, P, r, base, 4, 3)
    assert not action['closed_for_full_row_transport']
    assert action['signed_mapping'] == [[1, 1], None]
    assert action['known_constraint_rank'] == 1
    assert audit_orbit_rows(curve, P, r, base, 4, 3, [dict(coefficients=[1, 0], rhs=1)])['rank_after'] == 2
    with pytest.raises(ValueError, match='escapes'):
        audit_orbit_rows(curve, P, r, base, 4, 3, [dict(coefficients=[0, 1], rhs=3)])


def test_diagonal_group_law_on_every_small_curve_point():
    curve, P, r, base = cubic_fixture()
    points = [None]+[curve.mul(k, P) for k in range(1, r)]
    for left in points:
        for right in points:
            assert diagonal_point(curve, 4, curve.add(left, right)) == curve.add(
                diagonal_point(curve, 4, left), diagonal_point(curve, 4, right))


def test_public_translation_is_an_affine_log_frame():
    curve, P, r = Curve(101, 2, 21), (0, 18), 107
    assert curve.is_on_curve(P)
    base = [P, curve.mul(2, P)]
    Q = curve.mul(7, P)
    frame = project_public_translation(curve, P, r, base, 3,
        dict(coefficients=[1, 1], rhs=2, target_coefficient=1), target=Q)
    assert frame['new_unknown_columns'] == 0
    assert frame['projected_row']['rhs'] == -4 % r
    # A translated point can be zero; keep its original log column accounted for.
    frame = project_public_translation(curve, P, r, base, -1, dict(coefficients=[1, 1], rhs=1))
    assert frame['zero_atoms'] == [0]
    assert frame['projected_row']['rhs'] == 3
    with pytest.raises(ValueError, match='group equation'):
        project_public_translation(curve, P, r, base, 3, dict(coefficients=[1, 1], rhs=3))
