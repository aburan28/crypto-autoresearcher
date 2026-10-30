"""Finite algebra and public-point controls, never natural recovery evidence."""
from copy import deepcopy
from itertools import product

import pytest

from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations
from crypto_autoresearcher.index_calculus.target_relations import TargetRelations, hash_public_target


@pytest.mark.parametrize('p', [5, 7])
def test_combination_identifies_target_with_base_logs_unresolved(p):
    base = AffineRelations(p, 3)
    base.add([1, 1, 1], 9)
    system = TargetRelations(base)
    # Planted software values z=(2,3,4), k=3. Neither row alone suffices.
    assert system.add([1, 0, 0], -1, 1)['single_row_scalar'] is None
    assert not system.identify()['identifiable']
    assert system.add([0, 1, 1], 4, 1)['single_row_scalar'] is None
    result = system.identify()
    assert result['identifiable'] and result['value'] == 3
    assert system.augmented.rank < system.augmented.columns
    candidates = [z for z in product(range(p), repeat=4)
                  if all(sum(x*y for x, y in zip(row, z)) % p == b
                         for row, b in zip(system.augmented.rows, system.augmented.rhs))]
    assert {z[-1] for z in candidates} == {3}
    assert len({z[0] for z in candidates}) == 1
    assert len({z[1] for z in candidates}) == p  # still no full base solution
    weights = result['row_weights']
    assert [sum(w*row[j] for w, row in zip(weights, system.augmented.rows)) % p
            for j in range(4)] == [0, 0, 0, 1]
    assert sum(w*b for w, b in zip(weights, system.augmented.rhs)) % p == 3


def test_target_rejections_atomicity_and_snapshot():
    base = AffineRelations(7, 2)
    base.add([1, 1], 3)
    system = TargetRelations(base)
    base.add([1, 0], 2)  # later preprocessing mutation must not leak
    assert system.base.rank == 1
    system.add([1, 1], 3, 0)
    assert not system.identify()['identifiable']
    system.add([1, 1], 1, 1)
    assert system.identify()['value'] == 2
    before = deepcopy(system.__dict__)
    with pytest.raises(ValueError, match='inconsistent'):
        system.add([1, 1], 2, 1)
    assert system.target_rows == before['target_rows']
    assert system.augmented.rows == before['augmented'].rows
    for row, offset, t in [([1], 0, 1), ([1, 1], 0.5, 1), ([1, 1], 0, True)]:
        with pytest.raises(ValueError):
            system.add(row, offset, t)


def test_public_verification_of_combined_target():
    curve, p = Curve(101, 2, 21), 107
    P = curve.lift_x(0)
    assert 1+sum(1 if curve.rhs(x) == 0 else 2 if curve.lift_x(x) else 0 for x in range(101)) == p
    base = AffineRelations(p, 3)
    base.add([1, 1, 1], 10)
    system = TargetRelations(base)
    system.add([1, 0, 0], -10, 1)
    system.add([0, 1, 1], -4, 1)
    assert system.verify(curve, P, curve.mul(12, P))['scalar'] == 12
    with pytest.raises(ValueError, match='public verification'):
        system.verify(curve, P, curve.mul(13, P))
    with pytest.raises(ValueError, match='invalid public'):
        system.verify(curve, None, curve.mul(12, P))
    with pytest.raises(ValueError, match='invalid public'):
        system.verify(curve, P, (1, 1))


def test_public_hash_recipe_replay_and_bounds():
    from hashlib import sha256
    curve = Curve(101, 2, 21)
    result = hash_public_target(curve, 107, 'software-curve', 0)
    assert not result['scalar_label_generated']
    for row in result['rejected']+[result['selected']]:
        payload = f"{result['domain']}|software-curve|0|{row['counter']}".encode()
        digest = sha256(payload).digest()
        assert row['sha256'] == digest.hex()
        assert row['x'] == int.from_bytes(digest, 'big') % 101
    assert result['point'] == list(curve.lift_x(result['selected']['x']))
    assert curve.mul(107, tuple(result['point'])) is None
    assert result == hash_public_target(curve, 107, 'software-curve', 0)
    for index, bound, order, uid in [(-1, 10, 107, 'x'), (0, 0, 107, 'x'),
                                     (0, 10, 9, 'x'), (0, 10, 107, 'bad|uid')]:
        with pytest.raises(ValueError):
            hash_public_target(curve, order, uid, index, max_counters=bound)


def test_hash_exhaustion_retains_each_rejected_attempt(monkeypatch):
    curve = Curve(101, 2, 21)
    monkeypatch.setattr(curve, 'lift_x', lambda x: None)
    events = []
    with pytest.raises(ValueError, match='counter bound exhausted'):
        hash_public_target(curve, 107, 'software-exhaustion', 0,
                           max_counters=3, on_attempt=events.append)
    assert [row['counter'] for row in events] == [0, 1, 2]
    assert all(row['status'] == 'not_rational' for row in events)
