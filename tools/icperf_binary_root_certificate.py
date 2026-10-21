"""Check whether a binary m=8 Boolean root yields a full-point relation.

The input is a primary-variable assignment for the frozen torsion-phi XCNF
arm. This checks the field equations independently of the circuit emitter,
lifts each base coordinate, enumerates all signs, and emits only exact group
relations against the frozen raw target channel. It does not search for roots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_koblitz_subgroup_fixture import inv, mul  # noqa: E402
from tools.icperf_ordinary_binary_fixture import (FIELD_POLYNOMIAL, add,
                                                   lift_x, on_curve, scale)  # noqa: E402

BASE = ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
MANIFEST = ROOT / "research/icperf_binary_circuit_xcnf_20261017/manifest.json"
N = 61


def product(a: int, b: int) -> int:
    return mul(a, b, FIELD_POLYNOMIAL)


def phi3(a: int, b: int, c: int, gamma: int) -> int:
    def q(t: int) -> int:
        return product(t, t) ^ t
    return product(product(q(a), q(b)), q(c)) ^ product(gamma, product(a ^ b ^ c, a ^ b ^ c))


def neg(p: tuple[int, int]) -> tuple[int, int]:
    return p[0], p[0] ^ p[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certificate(assignment: int, base: dict, chain: dict, arm: dict) -> dict:
    width, offset = arm["base_dimension"], arm["offset"]
    assert arm["kind"] == "torsion_phi" and arm["primary_variables"] == 8 * width + 6 * N
    assert 0 <= assignment < (1 << arm["primary_variables"])
    mask = (1 << width) - 1
    ts = [((assignment >> (i * width)) & mask) ^ offset for i in range(8)]
    us = [(assignment >> (8 * width + i * N)) & ((1 << N) - 1) for i in range(6)]
    scan = next(row for row in base["candidate_scans"] if row["offset"] == offset)
    allowed = set(scan["accepted_phi"])
    membership = all(t in allowed for t in ts)
    gamma, b, r = chain["gamma"], chain["curve"]["b_polynomial_bits"], chain["curve"]["prime_order"]
    target_t = arm["target_coordinate"]
    triples = [[ts[0], ts[1], us[0]]]
    triples += [[us[i - 1], ts[i + 1], us[i]] for i in range(1, 6)]
    triples += [[us[-1], ts[-1], target_t]]
    values = [phi3(*row, gamma) for row in triples]
    equation_zero = all(value == 0 for value in values)
    result = {"membership_holds": membership, "equations_zero": equation_zero,
              "equation_values": values, "base_phi": ts, "intermediate_phi": us,
              "target_channel": chain["selected_channel"], "full_point_certificates": []}
    if not membership or not equation_zero:
        return result
    lifts = []
    for t in ts:
        if t == 0:
            return {**result, "rejection": "zero phi coordinate"}
        x = product(gamma, 1 ^ inv(t, FIELD_POLYNOMIAL))
        if x == 0 or x == gamma:
            return {**result, "rejection": "exceptional x coordinate"}
        p = lift_x(x, b)
        if p is None or not on_curve(p, b):
            return {**result, "rejection": "coordinate has no curve lift"}
        lifts.append(p)
    reps = scan["selected_representatives"]
    columns = {row[0]: (i, scale(4, tuple(row[1:]), b)) for i, row in enumerate(reps)}
    assert len(columns) == len(reps)
    choices = []
    for t, p in zip(ts, lifts):
        index, canonical = columns[t & ~1]
        image = scale(4, p, b)
        assert canonical is not None and image in (canonical, neg(canonical))
        choices.append((index, canonical, image))
    target = tuple(chain["target_channels"][chain["selected_channel"]])
    projected_target = tuple(chain["subgroup_target"])
    assert scale(4, target, b) == projected_target and scale(r, projected_target, b) is None
    for sign_mask in range(1 << 8):
        points = [neg(p) if sign_mask & (1 << i) else p for i, p in enumerate(lifts)]
        total = None
        for p in points:
            total = add(total, p, b)
        if total != target:
            continue
        coeffs: dict[int, int] = {}
        for i, p in enumerate(points):
            index, canonical, _ = choices[i]
            image = scale(4, p, b)
            coeffs[index] = coeffs.get(index, 0) + (1 if image == canonical else -1)
        row = [[i, coeffs[i]] for i in sorted(coeffs) if coeffs[i]]
        check = None
        for index, coefficient in row:
            canonical = choices[next(i for i, c in enumerate(choices) if c[0] == index)][1]
            term = scale(abs(coefficient), canonical, b)
            check = add(check, neg(term) if coefficient < 0 else term, b)
        assert check == projected_target
        result["full_point_certificates"].append({"sign_mask": sign_mask,
                                                   "points": [list(p) for p in points],
                                                   "projected_row": row})
    result["unique_projected_rows"] = len({tuple(map(tuple, c["projected_row"]))
                                            for c in result["full_point_certificates"]})
    result["certified"] = bool(result["full_point_certificates"])
    if not result["certified"]:
        result["rejection"] = "no sign assignment sums to the exact raw target"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignment-hex", help="Primary input bits; defaults to frozen planted control")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base, chain, manifest = [json.loads(path.read_bytes()) for path in (BASE, CHAIN, MANIFEST)]
    arm = next(row for row in manifest["arms"] if row["kind"] == "torsion_phi")
    assert digest(BASE) == chain["base_sha256"]
    assert digest(CHAIN) == manifest["parent_sha256"][str(CHAIN.relative_to(ROOT))]
    assert arm["target_coordinate"] == chain["target_channel_phi"][chain["selected_channel"]]
    assignment_hex = args.assignment_hex or arm["planted_witness"]["primary_assignment_hex"]
    assignment = int(assignment_hex, 16)
    checked = certificate(assignment, base, chain, arm)
    controls = {}
    if args.assignment_hex is None:
        for label, bit in (("flip_first_base_bit", 0),
                           ("flip_first_intermediate_bit", 8 * arm["base_dimension"])):
            altered = certificate(assignment ^ (1 << bit), base, chain, arm)
            assert not altered.get("certified", False)
            controls[label] = {"membership_holds": altered["membership_holds"],
                               "equations_zero": altered["equations_zero"],
                               "certified": altered.get("certified", False)}
    record = {"schema": "icperf-binary-root-certificate-v1",
              "scope": "full-point check of one frozen planted primary assignment; no solver search or E2E measurement",
              "source_sha256": digest(Path(__file__)),
              "input_sha256": {"base": digest(BASE), "chain": digest(CHAIN), "manifest": digest(MANIFEST)},
              "assignment_hex": hex(assignment), "result": checked,
              "bit_flip_controls": controls}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"certified": checked.get("certified", False),
                      "sign_certificates": len(checked["full_point_certificates"]),
                      "unique_projected_rows": checked.get("unique_projected_rows", 0)}, sort_keys=True))


if __name__ == "__main__":
    main()
