"""Record a planted eight-summand Pphi3 chain and torsion duplicate orbit.

This is a correctness witness for a proposed m=8 formulation. It does not
solve an unseen target or measure a relation collector.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_torsion_coordinate import (FIELD_POLYNOMIAL, add,
                                                    gamma_for, phi_from_x, pphi3,
                                                    scale)  # noqa: E402

BASE = ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json"
FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"


def coords(point):
    return None if point is None else list(point)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_bytes, fixture_bytes = BASE.read_bytes(), FIXTURE.read_bytes()
    base, fixture = json.loads(base_bytes), json.loads(fixture_bytes)
    gamma = gamma_for(fixture["b_polynomial_bits"])
    r = fixture["prime_order"]
    selected = next(row for row in base["candidate_scans"]
                    if row["offset"] == base["selected_offset"])
    rows = selected["selected_representatives"][:8]
    points = [tuple(row[1:]) for row in rows]
    ts = [row[0] for row in rows]
    assert len(set(ts)) == 8 and all(t % 2 == 0 for t in ts)
    assert [phi_from_x(p[0], gamma) for p in points] == ts

    partial = None
    intermediate_points = []
    for index, point in enumerate(points):
        partial = add(partial, point, 31)
        assert partial is not None and partial[0] != gamma
        if 1 <= index <= 6:
            intermediate_points.append(partial)
    raw_sum = partial
    assert len(intermediate_points) == 6
    subgroup_target = scale(4, raw_sum, 31)
    assert subgroup_target is not None and scale(r, subgroup_target, 31) is None
    inverse4 = pow(4, -1, r)
    root = scale(inverse4, subgroup_target, 31)
    t4 = scale(r, tuple(fixture["source_point"]), 31)
    assert t4 is not None and scale(4, t4, 31) is None
    channels = [add(root, scale(j, t4, 31), 31) for j in range(4)]
    assert all(c is not None and c[0] != gamma for c in channels)
    assert all(scale(4, c, 31) == subgroup_target for c in channels)
    assert channels.count(raw_sum) == 1
    channel_index = channels.index(raw_sum)

    us = [phi_from_x(p[0], gamma) for p in intermediate_points]
    channel_ts = [phi_from_x(p[0], gamma) for p in channels]
    triples = [[ts[0], ts[1], us[0]]]
    for i in range(1, 6):
        triples.append([us[i-1], ts[i+1], us[i]])
    triples.append([us[-1], ts[-1], channel_ts[channel_index]])
    assert len(triples) == 7 and all(pphi3(*triple, gamma) == 0 for triple in triples)
    final_channel_values = [pphi3(us[-1], ts[-1], t, gamma) for t in channel_ts]
    assert final_channel_values[channel_index] == 0

    t2 = tuple(base["coordinate"]["two_torsion"])
    assert scale(2, t2, 31) is None
    masks = []
    shifted_tuples = set()
    projected_rows = set()
    for mask in range(1 << 8):
        if mask.bit_count() % 2:
            continue
        transformed = [add(point, t2, 31) if (mask >> i) & 1 else point
                       for i, point in enumerate(points)]
        assert all(p is not None and p[0] != gamma for p in transformed)
        result = None
        for point in transformed:
            result = add(result, point, 31)
        assert result == raw_sum
        t_tuple = tuple(phi_from_x(point[0], gamma) for point in transformed)
        assert t_tuple == tuple(t ^ ((mask >> i) & 1) for i, t in enumerate(ts))
        shifted_tuples.add(t_tuple)
        projected_row = tuple(sorted(scale(4, point, 31) for point in transformed))
        projected_rows.add(projected_row)
        masks.append(mask)
    assert len(masks) == len(shifted_tuples) == 128
    assert len(projected_rows) == 1
    assert len({t for base_t in ts for t in (base_t, base_t ^ 1)}) == 16

    record = {"schema": "icperf-binary-torsion-m8-chain-v1",
              "scope": "planted m=8 chain and duplicate-row identity; no unseen solve or performance claim",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "coordinate_source_sha256": hashlib.sha256((ROOT / "tools/icperf_binary_torsion_coordinate.py").read_bytes()).hexdigest(),
              "curve": base["curve"], "gamma": gamma,
              "selected_offset": base["selected_offset"],
              "base_representatives": rows,
              "raw_points": [list(p) for p in points],
              "raw_sum": coords(raw_sum), "subgroup_target": coords(subgroup_target),
              "intermediate_points": [coords(p) for p in intermediate_points],
              "intermediate_phi": us,
              "torsion_order_four": coords(t4),
              "inverse_cofactor_mod_r": inverse4,
              "target_channels": [coords(p) for p in channels],
              "target_channel_phi": channel_ts,
              "selected_channel": channel_index,
              "chain_triples_phi": triples,
              "final_channel_values": final_channel_values,
              "chain_shape": {"summands": 8, "three_point_equations": 7,
                              "full_field_intermediates": 6,
                              "base_bits_each": 10,
                              "boolean_variables_per_channel_before_lift": 8*10+6*61,
                              "boolean_equations_per_channel_before_lift": 7*61,
                              "target_channels": 4},
              "torsion_duplicate_orbit": {"even_masks": masks,
                                           "distinct_ordered_phi_tuples_checked": len(shifted_tuples),
                                           "unique_projected_coefficient_rows_checked": len(projected_rows),
                                           "ordered_group_tuples_from_permutations_and_even_shifts": math.factorial(8)*len(masks),
                                           "scope_note": "group-level ordered point tuples; finite chain representations may exclude exceptional intermediates"}}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "channel": channel_index,
                      "equations": len(triples), "duplicate_tuples_checked": len(masks)}, sort_keys=True))


if __name__ == "__main__":
    main()
