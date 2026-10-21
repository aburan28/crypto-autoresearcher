#!/usr/bin/env python3
"""Blind, standard-library-only derivation of the frozen ICPERF k11 schedule.

Scientific inputs: the EXP-ICPERF-018b0c target-schedule statement and its
ordinary-binary fixture. This program does not import the experiment emitter.
It performs no solver call or search for a relation.
"""

import argparse
import hashlib
import json
from pathlib import Path


DOMAIN = b"ICPERF-k11-natural-v1\0"
CHANGED_DOMAIN = b"ICPERF-k11-natural-v1-changed\0"
EXPECTED_FIXTURE_SHA256 = "230d941d79152b17697341f65e5a46ddd2e3deb5e58f9ca21be889e49a5df39a"
COUNT = 8
LAST_CANDIDATE = 1023


class BinaryCurve:
    def __init__(self, polynomial, degree, b):
        self.polynomial = polynomial
        self.degree = degree
        self.mask = (1 << degree) - 1
        self.b = b

    def multiply(self, a, b):
        result = 0
        while b:
            if b & 1:
                result ^= a
            b >>= 1
            a <<= 1
            if a >> self.degree:
                a ^= self.polynomial
        return result

    def square(self, a):
        return self.multiply(a, a)

    def inverse(self, a):
        if a == 0:
            raise ZeroDivisionError("zero has no field inverse")
        u, v = a, self.polynomial
        g, h = 1, 0
        while u != 1:
            shift = u.bit_length() - v.bit_length()
            if shift < 0:
                u, v = v, u
                g, h = h, g
                shift = -shift
            u ^= v << shift
            g ^= h << shift
        while g.bit_length() > self.degree:
            g ^= self.polynomial << (g.bit_length() - self.degree - 1)
        return g

    def divide(self, a, b):
        return self.multiply(a, self.inverse(b))

    def on_curve(self, point):
        if point is None:
            return True
        x, y = point
        lhs = self.square(y) ^ self.multiply(x, y)
        rhs = self.multiply(self.square(x), x) ^ self.b
        return lhs == rhs

    @staticmethod
    def neg(point):
        if point is None:
            return None
        x, y = point
        return (x, x ^ y)

    def add(self, p, q):
        if p is None:
            return q
        if q is None:
            return p
        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if y1 != y2 or x1 == 0:
                return None
            slope = x1 ^ self.divide(y1, x1)
            x3 = self.square(slope) ^ slope
            y3 = self.square(x1) ^ self.multiply(slope ^ 1, x3)
        else:
            slope = self.divide(y1 ^ y2, x1 ^ x2)
            x3 = self.square(slope) ^ slope ^ x1 ^ x2
            y3 = self.multiply(slope, x1 ^ x3) ^ x3 ^ y1
        result = (x3, y3)
        assert self.on_curve(result)
        return result

    def scalar(self, k, point):
        if k < 0:
            return self.scalar(-k, self.neg(point))
        result = None
        while k:
            if k & 1:
                result = self.add(result, point)
            point = self.add(point, point)
            k >>= 1
        return result


def xy(point):
    return None if point is None else {"x": point[0], "y": point[1]}


def scalar_from_counter(domain, fixture_hash, counter, r):
    payload = domain + bytes.fromhex(fixture_hash) + counter.to_bytes(4, "big")
    digest = hashlib.sha256(payload).digest()
    return 1 + int.from_bytes(digest, "big") % (r - 1)


def admission_reasons(channels, target, seen, gamma):
    assert len(channels) == 4
    reasons = []
    for c, point in enumerate(channels):
        if point is None:
            reasons.append({"channel": c, "reason": "non_affine"})
        elif point[0] == 0:
            reasons.append({"channel": c, "reason": "zero_x"})
        elif point[0] == gamma:
            reasons.append({"channel": c, "reason": "phi_pole"})
    if target in seen:
        reasons.append({"reason": "duplicate_subgroup_target"})
    return reasons


def derive(fixture_path):
    fixture_bytes = fixture_path.read_bytes()
    fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
    if fixture_hash != EXPECTED_FIXTURE_SHA256:
        raise ValueError("fixture digest differs from the frozen specification")
    fixture = json.loads(fixture_bytes)
    degree = fixture["field_degree"]
    polynomial = fixture["field_polynomial"]
    b = fixture["b_polynomial_bits"]
    r = fixture["prime_order"]
    h = fixture["cofactor"]
    if degree != 61 or h != 4 or polynomial != (1 << 61) | 0x27:
        raise ValueError("unexpected fixture parameters")
    curve = BinaryCurve(polynomial, degree, b)
    generator = tuple(fixture["generator"])
    source = tuple(fixture["source_point"])
    assert curve.on_curve(generator) and curve.on_curve(source)
    assert curve.scalar(h, source) == generator
    assert curve.scalar(r, generator) is None

    torsion = curve.scalar(r, source)
    assert torsion is not None
    assert curve.scalar(4, torsion) is None
    assert curve.scalar(2, torsion) is not None
    gamma = torsion[0]
    # A point of order four has x^4=b on y^2+xy=x^3+b.
    assert curve.square(curve.square(gamma)) == b
    inv4 = pow(4, -1, r)

    candidates = []
    admitted = []
    seen = set()
    for counter in range(LAST_CANDIDATE + 1):
        scalar = scalar_from_counter(DOMAIN, fixture_hash, counter, r)
        target = curve.scalar(scalar, generator)
        root = curve.scalar(inv4, target)
        channels = [curve.add(root, curve.scalar(c, torsion)) for c in range(4)]
        assert len(set(channels)) == 4
        checks = admission_reasons(channels, target, seen, gamma)
        channel_rows = []
        for c, point in enumerate(channels):
            phi = None
            if point is not None and point[0] != gamma:
                phi = curve.divide(gamma, point[0] ^ gamma)
            channel_rows.append({"channel": c, "point": xy(point), "phi": phi})
            assert curve.scalar(4, point) == target
        candidate = {
            "counter": counter,
            "scalar": scalar,
            "target": xy(target),
            "raw_channels": channel_rows,
            "admitted": len(checks) == 0,
            "rejection_reasons": checks,
        }
        candidates.append(candidate)
        if not checks:
            candidate["target_index"] = len(admitted)
            admitted.append(counter)
            seen.add(target)
        if len(admitted) == COUNT:
            break
    else:
        raise ValueError("fewer than eight targets admitted by counter 1023")

    changed_domain_rows = []
    for candidate in candidates:
        counter = candidate["counter"]
        changed_scalar = scalar_from_counter(CHANGED_DOMAIN, fixture_hash, counter, r)
        changed_target = curve.scalar(changed_scalar, generator)
        row = {"counter": counter, "scalar": changed_scalar, "target": xy(changed_target),
               "differs_from_frozen_scalar": changed_scalar != candidate["scalar"],
               "differs_from_frozen_target": xy(changed_target) != candidate["target"]}
        changed_domain_rows.append(row)
    assert all(row["differs_from_frozen_scalar"] and row["differs_from_frozen_target"]
               for row in changed_domain_rows)

    first = candidates[0]
    first_target = (first["target"]["x"], first["target"]["y"])
    synthetic_channels = [(row["point"]["x"], row["point"]["y"])
                          for row in first["raw_channels"]]
    synthetic_channels[0] = torsion  # A valid curve point at the phi pole.
    synthetic_reasons = admission_reasons(synthetic_channels, first_target, set(), gamma)
    assert synthetic_reasons == [{"channel": 0, "reason": "phi_pole"}]

    natural_order = []
    for target_index in range(COUNT):
        bases = ["weighted", "local_random"] if target_index % 2 == 0 else ["local_random", "weighted"]
        for base in bases:
            for channel in range(4):
                natural_order.append({"call_index": len(natural_order) + 2, "target_index": target_index,
                                      "base": base, "channel": channel})
    assert len(natural_order) == COUNT * 4 * 2
    return {
        "schema": "icperf-k11-independent-blind-schedule-v1",
        "fixture_sha256": fixture_hash,
        "field": {"degree": degree, "polynomial": polynomial, "b": b},
        "group": {"prime_order": r, "cofactor": h, "generator": xy(generator), "source": xy(source),
                  "torsion_order4": xy(torsion), "gamma": gamma, "inverse_4_mod_r": inv4},
        "domain": DOMAIN.decode("ascii").rstrip("\0"),
        "candidate_scan": {"maximum_counter": LAST_CANDIDATE, "scanned": len(candidates),
                           "admitted": len(admitted), "rejected": len(candidates) - len(admitted),
                           "candidates": candidates},
        "controls": {
            "changed_domain": {
                "kind": "synthetic_domain_change",
                "domain": CHANGED_DOMAIN.decode("ascii").rstrip("\0"),
                "comparison": "Same fixture digest and counters; changed only the domain separator.",
                "rows": changed_domain_rows,
                "all_scanned_scalars_and_targets_differ": True,
            },
            "rejected_candidate": {
                "kind": "synthetic_channel_mutation",
                "source_counter": first["counter"],
                "mutated_channel": 0,
                "replacement_point": xy(torsion),
                "replacement_is_on_curve": curve.on_curve(torsion),
                "admitted": False,
                "rejection_reasons": synthetic_reasons,
                "scope": "Admission predicate only; deliberately not a valid generated channel for the source target.",
            },
        },
        "positive_order": [{"call_index": 0, "base": "weighted"},
                           {"call_index": 1, "base": "local_random"}],
        "natural_order": natural_order,
        "call_counts": {"positive": 2, "subgroup_targets": COUNT,
                        "raw_channels_per_target": 4, "bases": 2,
                        "natural": len(natural_order), "maximum_total": 2 + len(natural_order)},
        "scope": "Deterministic target and call schedule only; no solver call or relation assessment.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=Path("research/icperf_ordinary_binary_fixture_20261017/fixture.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = json.dumps(derive(args.fixture), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
