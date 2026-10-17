#!/usr/bin/env python3
"""Blind J0 derivation from the frozen ICPERF specification and curve fixture.

Uses only the Python standard library.  It does not import producer arithmetic,
inspect prepared inputs, or invoke any scientific solver.
"""

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[4]
SPEC = ROOT / "experiments/EXP-ICPERF-018b0c/specification.yaml"
FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
OUTPUT = Path(__file__).with_name("blind_counts.json")
EXPECTED_FIXTURE_SHA256 = "230d941d79152b17697341f65e5a46ddd2e3deb5e58f9ca21be889e49a5df39a"
DOMAIN = "ICPERF-k11-natural-v1"
BASES = ("weighted", "local_random")
INF = None


class BinaryCurve:
    def __init__(self, degree, polynomial, b):
        self.degree = degree
        self.polynomial = polynomial
        self.mask = (1 << degree) - 1
        self.b = b
        assert polynomial.bit_length() == degree + 1

    def mul(self, a, b):
        z = 0
        while b:
            if b & 1:
                z ^= a
            b >>= 1
            a <<= 1
            if a & (1 << self.degree):
                a ^= self.polynomial
        return z

    def square(self, a):
        return self.mul(a, a)

    def inv(self, a):
        if not a:
            raise ZeroDivisionError("field zero has no inverse")
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
            if not u:
                raise ArithmeticError("field polynomial failed inversion")
        while g.bit_length() > self.degree:
            g ^= self.polynomial << (g.bit_length() - self.degree - 1)
        return g

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def on_curve(self, point):
        if point is INF:
            return True
        x, y = point
        return (self.square(y) ^ self.mul(x, y)) == (
            self.mul(self.square(x), x) ^ self.b
        )

    def neg(self, point):
        if point is INF:
            return INF
        x, y = point
        return (x, x ^ y)

    def add(self, p, q):
        if p is INF:
            return q
        if q is INF:
            return p
        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if y1 != y2:
                assert (y1 ^ y2) == x1
                return INF
            if not x1:
                return INF
            slope = x1 ^ self.div(y1, x1)
            x3 = self.square(slope) ^ slope
            y3 = self.square(x1) ^ self.mul(slope ^ 1, x3)
        else:
            slope = self.div(y1 ^ y2, x1 ^ x2)
            x3 = self.square(slope) ^ slope ^ x1 ^ x2
            y3 = self.mul(slope, x1 ^ x3) ^ x3 ^ y1
        result = (x3, y3)
        assert self.on_curve(result)
        return result

    def scale(self, k, point):
        assert k >= 0
        result = INF
        while k:
            if k & 1:
                result = self.add(result, point)
            point = self.add(point, point)
            k >>= 1
        return result

    def phi(self, point, gamma):
        if point is INF:
            raise ValueError("point at infinity")
        x, _ = point
        if x == gamma:
            raise ValueError("pole x=gamma")
        return self.div(gamma, x ^ gamma)


def point_json(point):
    return None if point is INF else [point[0], point[1]]


def candidate_reason(channels, gamma):
    for index, point in enumerate(channels):
        if point is INF:
            return f"channel_{index}_infinity"
        if point[0] == 0:
            return f"channel_{index}_zero_x"
        if point[0] == gamma:
            return f"channel_{index}_pole_x_gamma"
    return None


def scalar(domain, fixture_digest, j, r):
    preimage = domain.encode("ascii") + b"\0" + bytes.fromhex(fixture_digest) + j.to_bytes(4, "big")
    return 1 + int.from_bytes(hashlib.sha256(preimage).digest(), "big") % (r - 1)


def schedule(curve, generator, source, r, gamma, fixture_digest, domain):
    torsion = curve.scale(r, source)
    inverse_four = pow(4, -1, r)
    accepted, rejected, seen = [], [], set()
    for j in range(1024):
        k = scalar(domain, fixture_digest, j, r)
        subgroup = curve.scale(k, generator)
        root = curve.scale(inverse_four, subgroup)
        assert curve.scale(4, root) == subgroup
        channels = [curve.add(root, curve.scale(c, torsion)) for c in range(4)]
        reason = "duplicate_subgroup_point" if subgroup in seen else candidate_reason(channels, gamma)
        if reason:
            rejected.append({"counter": j, "scalar": k, "reason": reason})
            continue
        seen.add(subgroup)
        accepted.append({
            "target_index": len(accepted), "counter": j, "scalar": k,
            "subgroup_point": point_json(subgroup),
            "raw_channels": [point_json(p) for p in channels],
            "phi_coordinates": [curve.phi(p, gamma) for p in channels],
        })
        for point in channels:
            assert curve.scale(4, point) == subgroup
        if len(accepted) == 8:
            break
    return accepted, rejected


def main():
    spec = SPEC.read_text(encoding="utf-8")
    assert re.search(r"^\s*domain: ICPERF-k11-natural-v1\s*$", spec, re.M)
    assert "j=0..1023" in spec and "four raw channel" in spec
    assert "First weighted positive, then local_random positive" in spec
    assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == EXPECTED_FIXTURE_SHA256
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    curve = BinaryCurve(fixture["field_degree"], fixture["field_polynomial"], fixture["b_polynomial_bits"])
    generator, source = tuple(fixture["generator"]), tuple(fixture["source_point"])
    r = fixture["prime_order"]
    assert curve.on_curve(generator) and curve.on_curve(source)
    assert curve.scale(4, source) == generator
    assert curve.scale(r, generator) is INF
    torsion = curve.scale(r, source)
    assert torsion is not INF and curve.scale(4, torsion) is INF
    assert curve.scale(2, torsion) is not INF
    # On y^2+xy=x^3+b, the order-four x coordinate obeys x^4=b.
    gamma = torsion[0]
    assert curve.square(curve.square(gamma)) == curve.b
    accepted, rejected = schedule(curve, generator, source, r, gamma, EXPECTED_FIXTURE_SHA256, DOMAIN)
    altered, altered_rejected = schedule(curve, generator, source, r, gamma, EXPECTED_FIXTURE_SHA256, "ICPERF-k11-natural-v2")
    # The allowed statement names gamma but never binds its value.  This
    # alternative field element satisfies the stated pole predicate literally
    # and changes the admission decision for candidate zero.
    alternate_gamma = accepted[0]["raw_channels"][0][0]
    alternate_accepted, alternate_rejected = schedule(
        curve, generator, source, r, alternate_gamma, EXPECTED_FIXTURE_SHA256, DOMAIN
    )
    assert alternate_rejected[0]["counter"] == 0
    assert alternate_rejected[0]["reason"] == "channel_0_pole_x_gamma"
    labels = [
        {"ordinal": 0, "stage": "positive", "base": "weighted"},
        {"ordinal": 1, "stage": "positive", "base": "local_random"},
    ]
    for i in range(8):
        bases = BASES if i % 2 == 0 else BASES[::-1]
        for base in bases:
            for channel in range(4):
                labels.append({"ordinal": len(labels), "stage": "natural", "target_index": i,
                               "candidate_counter": accepted[i]["counter"], "base": base, "channel": channel})
    assert len(labels) == 66
    assert len(accepted) == 8 and len(altered) == 8
    pole_control = candidate_reason([torsion] * 4, gamma)
    assert pole_control == "channel_0_pole_x_gamma"
    assert altered[0]["scalar"] != accepted[0]["scalar"]
    output = {
        "schema": "icperf-j0-independent-schedule-v1", "experiment_id": "EXP-ICPERF-018b0c",
        "task_id": "TASK-20261017-93d17d", "fixture_sha256": EXPECTED_FIXTURE_SHA256,
        "field_polynomial": curve.polynomial, "field_degree": curve.degree, "curve_b": curve.b,
        "prime_order": r, "generator": point_json(generator), "source_point": point_json(source),
        "four_torsion_point": point_json(torsion), "gamma_from_four_torsion": gamma,
        "domain": DOMAIN, "inverse_four_mod_r": pow(4, -1, r),
        "scanned_candidates": accepted[-1]["counter"] + 1, "rejected_candidates": rejected,
        "accepted_targets": accepted,
        "planned_call_count": len(labels), "positive_call_count": 2, "natural_call_count": 64,
        "planned_call_labels": labels,
        "controls": {
            "changed_domain_separator": {
                "domain": "ICPERF-k11-natural-v2", "first_scalar": altered[0]["scalar"],
                "first_subgroup_point": altered[0]["subgroup_point"],
                "first_candidate_counter": altered[0]["counter"],
                "different_from_frozen_first_target": altered[0]["subgroup_point"] != accepted[0]["subgroup_point"],
                "rejected_candidates_before_first": [x for x in altered_rejected if x["counter"] < altered[0]["counter"]],
            },
            "pole_rejection": {
                "constructed_four_torsion_channel": point_json(torsion),
                "candidate_reason": pole_control,
                "phi_raises": None,
            },
            "gamma_binding_gap": {
                "observation": "The permitted specification and fixture do not explicitly define gamma.",
                "natural_four_torsion_gamma": gamma,
                "literal_alternative_gamma": alternate_gamma,
                "alternative_first_rejection": alternate_rejected[0],
                "alternative_first_accepted_counter": alternate_accepted[0]["counter"],
                "alternative_first_eight_counters": [x["counter"] for x in alternate_accepted],
                "alternative_schedule_differs": [x["counter"] for x in alternate_accepted] != [x["counter"] for x in accepted],
            },
        },
    }
    try:
        curve.phi(torsion, gamma)
    except ValueError as exc:
        output["controls"]["pole_rejection"]["phi_raises"] = str(exc)
    assert output["controls"]["pole_rejection"]["phi_raises"] == "pole x=gamma"
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"accepted_scalars": [x["scalar"] for x in accepted],
                      "rejected": len(rejected), "calls": len(labels), "gamma": gamma,
                      "changed_domain_first_scalar": altered[0]["scalar"]}, sort_keys=True))


if __name__ == "__main__":
    main()
