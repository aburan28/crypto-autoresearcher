"""Exact semantic controls for the opt-in wide packed tail table."""

import itertools
import json
from pathlib import Path

import pytest

from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.factor_base import FactorBase
from crypto_autoresearcher.index_calculus.tails import TailTable, wide_packed_table

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n50_seed20261017.json"


def _oracle(E, fb, h):
    """Independent point-addition enumeration, including every suffix check."""
    out = {}
    B = 2 * len(fb)
    for inds in itertools.combinations_with_replacement(range(len(fb)), h):
        for suffix_signs in itertools.product((1, -1), repeat=h - 1):
            signs = (1,) + suffix_signs
            vals = []
            valid = True
            for start in range(h - 1, -1, -1):
                point = fb.points[inds[start]]
                if signs[start] < 0:
                    point = E.neg(point)
                vals.insert(0, E.add(point, vals[0] if vals else None))
                if vals[0] is None:
                    valid = False
                    break
            if not valid:
                continue
            x, y = vals[0]
            digits = sum((2 * i + int(s < 0)) * B**j
                         for j, (i, s) in enumerate(zip(inds, signs)))
            code = (digits << 1) | int(y > E.p // 2)
            out.setdefault(x, []).append(code)
    return {x: sorted(cs) for x, cs in out.items()}


@pytest.mark.parametrize("wide", [False, True])
@pytest.mark.parametrize("h", [2, 3, 4])
def test_wide_table_full_small_controls(tmp_path, wide, h):
    if wide:
        fixture = json.loads(FIXTURE.read_text())["curve"]
        E = Curve(**{k: fixture[k] for k in ("p", "a", "b", "order")})
    else:
        E = Curve(1019, 2, 3)
    fb = FactorBase.small_x(E, 8)
    reference = TailTable(E, fb, h, accelerate=False)
    expected = _oracle(E, fb, h)
    table = wide_packed_table(E, fb, h, tmp_path / "wide",
                              min_free_bytes=0, chunk_entries=73)
    got = {x: sorted(cs) for x, cs in table.iter_keys()}
    assert got == expected == {x: list(cs) for x, cs in reference.as_dict().items()}
    assert table.entries == reference.entries == sum(map(len, expected.values()))
    assert table.s3_solves == reference.s3_solves
    assert table.metrics["payload_bytes"] == 16 * table.entries
    for x, cs in expected.items():
        for lo in range(9):
            assert sorted(table.codes(x, lo)) == sorted(reference.codes(x, lo))
        for code in cs:
            tail, ybit = table.decode(code)
            assert tail[0][1] == 1 and ybit == (code & 1)
            y = E.lift_x(x)[1]
            for orient_y in {y, (-y) % E.p}:
                signed = table.orient(code, orient_y)
                acc = None
                for i, s in signed:
                    P = fb.points[i]
                    acc = E.add(acc, P if s > 0 else E.neg(P))
                assert acc == (x, orient_y)
    assert table.codes(E.p, 0) == []
    assert table.codes(-1, 0) == []
    table.close()


def test_wide_table_rejects_altered_codes_and_points(tmp_path):
    E = Curve(1019, 2, 3)
    fb = FactorBase.small_x(E, 8)
    table = wide_packed_table(E, fb, 4, tmp_path / "wide",
                              min_free_bytes=0, chunk_entries=73)
    x, codes = next(table.iter_keys())
    code = codes[0]
    signed = table.orient(code, E.lift_x(x)[1])
    def total(items):
        acc = None
        for i, s in items:
            P = fb.points[i]
            acc = E.add(acc, P if s > 0 else E.neg(P))
        return acc
    assert total(signed) == E.lift_x(x)
    assert total(signed[:-1] + [(signed[-1][0], -signed[-1][1])]) != E.lift_x(x)
    assert total(table.orient(code ^ 2, E.lift_x(x)[1])) != E.lift_x(x)
    assert total(signed) != E.lift_x((x + 1) % E.p)
    table.close()
