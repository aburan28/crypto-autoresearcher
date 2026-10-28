#!/usr/bin/env python3
"""Independent public-input arithmetic and transfer-study record validation.

No candidate imports, producer scalar labels, scientific execution, or cost
replay. The primary oracle builds a validator-only cumulative public-orbit
coefficient table. Small full slope sums and fixed right-to-left binary-chain
checks are controls; all constructions share registered cocycle mathematics.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import isqrt
from pathlib import Path
import re
from typing import Any, Iterable

Point = tuple[int, int] | None
SMALL_ORACLE_MAX_R = 127
ORBIT_COEFFICIENT_MAX_R = 8191
FIXED_CIRCUITS = ((1, -4), (-2, -1))
ODD_NULL_DOMAIN = b"\x00transfer-study/odd-anchor-null/v1\x00"
ODD_NULL_RULE = {
    "hash": "SHA256",
    "hash_input": "nonce32 || domain || curve_id.UTF8 || 00 || seed_index.u32be || x.fixed_fieldwidth_be",
    "domain_hex": ODD_NULL_DOMAIN.hex(),
    "hash_bit": "digest[0] & 1",
    "field_width_bytes": "ceil(bit_length(p)/8)",
    "sign_y": "int(y > floor(p/2))",
    "raw_h": "sign_y(R) XOR hash_bit(seed_index,x(R))",
    "normalized_h": "raw_h(R) XOR raw_h(P_prime) for finite R; H(O)=0",
    "seed_indices": list(range(16)),
    "raw_functions_per_curve": 16,
    "base_views": "same 16 raw functions normalized separately at a in {1,2,3,5}; correlated views",
    "matches": ["oddness", "anchor"],
    "coordinate_covariant": False,
    "coordinate_scope": "one canonical fresh-cohort view; coordinate covariance excluded from this null",
    "small_recovery_coverage": "all nonidentity transformed targets on the registered exact panel, r<=127",
    "larger_recovery_coverage": "same observed Q_b and repetitions as each actual candidate arm; no larger all-r null recovery census",
}


def point(value: Any, p: int) -> Point:
    if value is None:
        return None
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("point must be null or two canonical field integers")
    if any(type(x) is not int or not 0 <= x < p for x in value):
        raise ValueError("point coordinates are not canonical field integers")
    return value[0], value[1]


def encoded(value: Point) -> list[int] | None:
    return None if value is None else list(value)


def prime64(n: int) -> bool:
    """Deterministic Miller--Rabin on unsigned 64-bit inputs, never probable-prime."""
    if type(n) is not int or not 2 <= n < 2**64:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % n == 0:
            continue
        x = pow(base, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


class Group:
    """Own affine formulas and double-and-add; counts are validator work only."""

    def __init__(self, model: dict[str, int]):
        if any(type(model.get(k)) is not int for k in ("p", "a", "b", "r")):
            raise ValueError("curve model requires integer p,a,b,r")
        self.p, self.a, self.b, self.r = (model[k] for k in ("p", "a", "b", "r"))
        if self.p <= 3 or self.p % 4 != 3 or not prime64(self.p):
            raise ValueError("requires prime 3 mod 4 field below 2^64")
        if self.r <= 2 or self.r == self.p or not prime64(self.r):
            raise ValueError("requires odd prime r!=p below 2^64")
        if not 0 <= self.a < self.p or not 0 <= self.b < self.p:
            raise ValueError("curve coefficients must be canonical")
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("singular model")
        self.model = {k: model[k] for k in ("p", "a", "b", "r")}
        self.counts: Counter[str] = Counter()

    def on_curve(self, value: Point) -> bool:
        self.counts["point_membership"] += 1
        if value is None:
            return True
        x, y = value
        return 0 <= x < self.p and 0 <= y < self.p and (y*y-x*x*x-self.a*x-self.b) % self.p == 0

    def neg(self, value: Point) -> Point:
        self.counts["group_negation"] += 1
        return None if value is None else (value[0], -value[1] % self.p)

    def slope(self, left: Point, right: Point) -> int:
        self.counts["slope"] += 1
        if left is None or right is None:
            return 0
        x, y = left
        u, v = right
        if x == u:
            if (y + v) % self.p == 0:
                return 0
            numerator, denominator = 3*x*x+self.a, 2*y
        else:
            numerator, denominator = v-y, u-x
        self.counts["field_inverse"] += 1
        return numerator * pow(denominator, -1, self.p) % self.p

    def add(self, left: Point, right: Point) -> Point:
        self.counts["group_add"] += 1
        if left is None:
            return right
        if right is None:
            return left
        if left[0] == right[0] and (left[1]+right[1]) % self.p == 0:
            return None
        lam = self.slope(left, right)
        x = (lam*lam-left[0]-right[0]) % self.p
        return x, (lam*(left[0]-x)-left[1]) % self.p

    def mul(self, n: int, value: Point) -> Point:
        if type(n) is not int:
            raise ValueError("scalar must be integer")
        self.counts["scalar_multiply"] += 1
        if n < 0:
            return self.mul(-n, self.neg(value))
        acc, current = None, value
        while n:
            if n & 1:
                acc = self.add(acc, current)
            n //= 2
            if n:
                current = self.add(current, current)
        return acc

    def certify_base(self, base: Point) -> dict[str, Any]:
        if base is None or not self.on_curve(base) or self.mul(self.r, base) is not None:
            raise ValueError("base must be a nonidentity point of prime order r")
        # Lagrange plus Hasse forces the full curve order when precisely one
        # multiple of r lies in the Hasse interval, and that multiple is r.
        radius = isqrt(4*self.p)
        low, high = self.p+1-radius, self.p+1+radius
        minimum, maximum = (low+self.r-1)//self.r, high//self.r
        if minimum != 1 or maximum != 1:
            raise ValueError("Hasse/subgroup witness does not certify full prime curve order")
        trace = self.p+1-self.r
        if trace % self.p == 0:
            raise ValueError("supersingular curve excluded")
        return {"prime_order": True, "ordinary": True, "hasse_interval": [low, high], "trace": trace}

    def orbit(self, base: Point) -> list[Point]:
        if self.r > SMALL_ORACLE_MAX_R:
            raise ValueError("full-group oracle restricted to registered small tiers")
        self.certify_base(base)
        values, current = [None], None
        for _ in range(1, self.r):
            current = self.add(current, base)
            values.append(current)
        if len(set(values)) != self.r or self.add(current, base) is not None:
            raise ValueError("invalid subgroup orbit")
        self.counts["validator_only_orbit_entries"] += len(values)
        return values


class Primitive:
    """Validator-only Z oracle, with explicit bounded full-orbit scope."""

    def __init__(self, group: Group, base: Point, mode: str = "auto"):
        self.group = group
        group.certify_base(base)
        if mode not in ("auto", "slope_sum", "addition_chain", "orbit_coefficient"):
            raise ValueError("unrecognized primitive mode")
        self.mode = "orbit_coefficient" if mode == "auto" else mode
        self.orbit = group.orbit(base) if self.mode == "slope_sum" else None
        self.cache: dict[Point, int] = {}
        self.scalar_points: list[Point] | None = None
        if self.mode == "orbit_coefficient":
            if group.r > ORBIT_COEFFICIENT_MAX_R:
                raise ValueError("registered cumulative-orbit primitive limited to r<=8191")
            # Linear public path, independently of either binary chain.
            current, coefficient, path = None, 0, []
            for scalar in range(1, group.r+1):
                coefficient = (coefficient+group.slope(current, base)) % group.p
                current = group.add(current, base)
                if scalar < group.r:
                    path.append((current, scalar, coefficient))
            if current is not None or len({q for q, _, _ in path}) != group.r-1:
                raise ValueError("cumulative primitive failed complete subgroup witness")
            z_base = -coefficient*pow(group.r, -1, group.p) % group.p
            self.cache = {None: 0, **{q: (scalar*z_base+d) % group.p for q, scalar, d in path}}
            self.scalar_points = [None]+[q for q, _, _ in path]
            group.counts["primitive_orbit_builds"] += 1
            group.counts["primitive_orbit_steps"] += group.r
            group.counts["primitive_table_entries"] += len(self.cache)
            group.counts["primitive_coefficient_updates"] += group.r
            group.counts["primitive_normalization_inverse"] += 1
            group.counts["primitive_table_entry_evaluations"] += group.r-1
            group.counts["validator_public_orbit_point_entries"] += group.r

    def scalar_point(self, scalar: int) -> Point:
        if self.scalar_points is None or type(scalar) is not int or not 0 <= scalar < self.group.r:
            raise ValueError("validator public orbit index unavailable")
        self.group.counts["validator_public_orbit_index_reads"] += 1
        return self.scalar_points[scalar]

    def z(self, target: Point) -> int:
        g, p = self.group, self.group.p
        if target in self.cache:
            g.counts["primitive_table_reads"] += 1
            return self.cache[target]
        if self.mode == "orbit_coefficient":
            raise ValueError("primitive target outside registered full subgroup table")
        if not g.on_curve(target):
            raise ValueError("primitive target is off curve")
        if target is None:
            value = 0
        elif self.orbit is not None:
            if target not in self.orbit:
                raise ValueError("primitive target outside subgroup")
            g.counts["slope_sum_queries"] += 1
            g.counts["slope_sum_terms"] += len(self.orbit)
            value = -sum(g.slope(target, other) for other in self.orbit) * pow(g.r, -1, p) % p
        else:
            # D_(m+n)=D_m+D_n+lambda(mR,nR), evaluated from low
            # scalar bits rather than the producer's high-bit recurrence.
            n, acc, acc_d, power, power_d = g.r, None, 0, target, 0
            while n:
                if n & 1:
                    acc_d = (acc_d+power_d+g.slope(acc, power)) % p
                    acc = g.add(acc, power)
                n //= 2
                if n:
                    power_d = (2*power_d+g.slope(power, power)) % p
                    power = g.add(power, power)
            if acc is not None:
                raise ValueError("primitive target outside r-torsion")
            g.counts["independent_coefficient_queries"] += 1
            value = -acc_d * pow(g.r, -1, p) % p
        self.cache[target] = value
        return value


class ValidatorLabels:
    """Own BSGS labels for diagnostics only, never passed to producer APIs."""

    def __init__(self, group: Group, base: Point):
        group.certify_base(base)
        self.group, self.base = group, base
        self.width = isqrt(group.r)+1
        self.babies: dict[Point, int] = {}
        current = None
        for index in range(self.width):
            self.babies[current] = index
            current = group.add(current, base)
        self.step = group.neg(group.mul(self.width, base))

    def scalar(self, target: Point) -> int:
        current, group = target, self.group
        for giant in range(self.width+1):
            if current in self.babies:
                scalar = giant*self.width+self.babies[current]
                if scalar < group.r and group.mul(scalar, self.base) == target:
                    return scalar
            current = group.add(current, self.step)
        raise ValueError("validator could not label subgroup point")


def answer(primitive: Primitive, base: Point, target: Point, alpha: int, beta: int) -> dict[str, Any]:
    """Re-derive circuit answer from public points, without scalar labels."""
    g, p = primitive.group, primitive.group.p
    if base is None or not g.on_curve(base) or not g.on_curve(target):
        raise ValueError("invalid circuit input")
    common = {"bit": None, "g": None, "anchor": None, "normalized": None, "z": None}
    if base[1] == 0:
        return dict(common, status="UNDEFINED", reason="ZERO_BASE_Y")
    zp = primitive.z(base)
    if zp == 0:
        return dict(common, status="UNDEFINED", reason="ZERO_BASE_Z")
    anchor = (1+alpha)*zp % p
    if anchor == 0:
        return dict(common, anchor=anchor, status="UNDEFINED", reason="ZERO_ANCHOR")
    if target is None:
        return dict(common, z=0, anchor=anchor, status="BIT", bit=0, reason=None)
    c = zp*pow(base[1], -1, p) % p
    z = primitive.z(target)
    numerator = (z+c*target[1]*(alpha+beta*c*(target[0]-base[0]))) % p
    values = dict(common, anchor=anchor, z=z, g=numerator)
    if numerator == 0:
        return dict(values, status="UNDEFINED", reason="ZERO_NUMERATOR")
    normalized = numerator*pow(anchor, -1, p) % p
    symbol = pow(normalized, (p-1)//2, p)
    if symbol not in (1, p-1):
        raise ValueError("invalid Legendre result")
    return dict(values, normalized=normalized, status="BIT", bit=int(symbol == p-1), reason=None)


def interval_candidate(r: int, digits: list[int]) -> dict[str, Any]:
    """Exact half-open interval, including empty arbitrary-bit intervals."""
    if type(r) is not int or r < 3 or any(type(b) is not int or b not in (0, 1) for b in digits):
        raise ValueError("requires odd-order positive r and exact binary digits")
    v = 0
    for bit in digits:
        v = 2*v+bit
    denominator = 1 << len(digits)
    lower, upper = r*v, r*(v+1)
    candidate = (lower+denominator-1)//denominator
    valid = 0 <= candidate < r and candidate*denominator < upper
    return {"candidate": candidate, "value": v, "lower_numerator": lower,
            "upper_numerator": upper, "denominator": denominator, "nonempty": valid}


class OddAnchorNull:
    """Validator-only odd/anchored functions, with no coordinate-covariance claim.

    Coordinates determine all raw bits. The independent public orbit is used
    solely to implement doubling, interval recovery and public point equations.
    Its labels never determine a null bit and never enter a producer API.
    """

    def __init__(self, group: Group, primitive: Primitive, nonce_hex: str, curve_id: str):
        if not isinstance(nonce_hex, str) or not re.fullmatch(r"[0-9a-f]{64}", nonce_hex):
            raise ValueError("odd null requires a public 32-byte nonce")
        if primitive.scalar_points is None or primitive.group is not group:
            raise ValueError("odd null requires the independent validator orbit")
        self.group, self.points, self.curve_id = group, primitive.scalar_points, curve_id
        self.labels = {q: k for k, q in enumerate(self.points)}
        self.counts: Counter[str] = Counter()
        self.counts["null_validator_point_index_entries"] += len(self.labels)
        self.raw_bits: list[bytearray] = []
        width = (group.p.bit_length()+7)//8
        prefix = bytes.fromhex(nonce_hex)+ODD_NULL_DOMAIN+curve_id.encode()+b"\x00"
        for seed_index in range(16):
            bits, x_hashes = bytearray(group.r), {}
            for scalar, q in enumerate(self.points[1:], 1):
                if q is None or q[1] == 0:
                    raise ValueError("odd null requires nonzero y at every finite subgroup point")
                x, y = q
                if x not in x_hashes:
                    digest = hashlib.sha256(prefix+seed_index.to_bytes(4, "big")+x.to_bytes(width, "big")).digest()
                    x_hashes[x] = digest[0] & 1
                    self.counts["null_hash256_calls"] += 1
                bits[scalar] = int(y > group.p//2) ^ x_hashes[x]
                self.counts["null_raw_bit_entries"] += 1
            self.raw_bits.append(bits)
        self.candidate_cache: dict[tuple[int, int, int], tuple[int, bool]] = {}
        self.inverse_cache: dict[int, int] = {}

    def bit(self, seed_index: int, base_multiplier: int, target: Point) -> int:
        if type(seed_index) is not int or not 0 <= seed_index < 16:
            raise ValueError("odd null seed index must be in 0..15")
        if type(base_multiplier) is not int or base_multiplier not in (1, 2, 3, 5):
            raise ValueError("odd null base multiplier outside frozen four values")
        if target is None:
            self.counts["null_identity_bit_reads"] += 1
            return 0
        scalar = self.labels[target]
        self.counts["null_raw_bit_reads"] += 2
        return self.raw_bits[seed_index][scalar] ^ self.raw_bits[seed_index][base_multiplier]

    def attempt(self, seed_index: int, base_multiplier: int, transformed_target: Point,
                original_target: Point, target_multiplier: int) -> dict[str, Any]:
        group, r = self.group, self.group.r
        if transformed_target is None or original_target is None or type(target_multiplier) is not int or not 1 <= target_multiplier < r:
            raise ValueError("odd null primary attempt requires nonidentity points and nonzero b")
        label, original_label = self.labels[transformed_target], self.labels[original_target]
        if label != target_multiplier*original_label % r:
            raise ValueError("odd null public blinded target relation mismatch")
        key = seed_index, base_multiplier, label
        if key not in self.candidate_cache:
            digits, current = [], label
            length = r.bit_length()+1
            for index in range(length):
                digits.append(self.bit(seed_index, base_multiplier, self.points[current]))
                if index+1 < length:
                    current = 2*current % r
                    self.counts["null_validator_doubling_index_steps"] += 1
            interval = interval_candidate(r, digits)
            self.candidate_cache[key] = interval["candidate"], interval["nonempty"]
            self.counts["null_interval_reductions"] += 1
            self.counts["null_candidate_cache_entries"] += 1
        else:
            self.counts["null_candidate_cache_reads"] += 1
        scalar_prime, nonempty = self.candidate_cache[key]
        self.counts["null_attempt_events"] += 1
        if not nonempty:
            return {"success": False, "status": "EMPTY_INTERVAL", "candidate_scalar_prime": scalar_prime,
                    "candidate_scalar": None, "public_checks": {"transformed": None, "original": None}}
        if target_multiplier not in self.inverse_cache:
            self.inverse_cache[target_multiplier] = pow(target_multiplier, -1, r)
            self.counts["null_order_inverse_calls"] += 1
        else:
            self.counts["null_order_inverse_cache_reads"] += 1
        scalar = base_multiplier*self.inverse_cache[target_multiplier]*scalar_prime % r
        # Independent, certified public multiples implement the same two point
        # equations; this is validator table work, not a fresh producer solve.
        transformed_check = self.points[base_multiplier*scalar_prime % r] == transformed_target
        original_check = self.points[scalar] == original_target
        self.counts["null_public_equation_point_table_reads"] += 2
        self.counts["null_scalar_conversion_events"] += 1
        success = transformed_check and original_check
        return {"success": success, "status": "RECOVERED" if success else "REJECTED_FINAL_VERIFICATION",
                "candidate_scalar_prime": scalar_prime, "candidate_scalar": scalar,
                "public_checks": {"transformed": transformed_check, "original": original_check}}


def retained_bit_exact_census(group: Group, primitive: Primitive, base_multiplier: int,
                              bits: dict[Point, int | None]) -> dict[str, Any]:
    """Exact small validator census from retained diagnostic bits, no fresh calls."""
    if group.r > 127 or primitive.scalar_points is None:
        raise ValueError("retained-bit exact census is restricted to the small panel")
    if base_multiplier not in (1, 2, 3, 5):
        raise ValueError("retained-bit census base outside frozen four values")
    statuses, counts = Counter(), Counter()
    length, r = group.r.bit_length()+1, group.r
    for label in range(1, r):
        digits, current, defined = [], label, True
        for index in range(length):
            bit = bits.get(primitive.scalar_points[current])
            counts["retained_exact_bit_reads"] += 1
            if type(bit) is not int or bit not in (0, 1):
                defined = False
            else:
                digits.append(bit)
            if index+1 < length:
                current = 2*current % r
                counts["retained_exact_doubling_index_steps"] += 1
        counts["retained_exact_validator_attempts"] += 1
        if not defined:
            statuses["UNDEFINED"] += 1
            continue
        interval = interval_candidate(r, digits)
        counts["retained_exact_interval_reductions"] += 1
        if not interval["nonempty"]:
            statuses["EMPTY_INTERVAL"] += 1
            continue
        scalar_prime, target = interval["candidate"], primitive.scalar_points[label]
        scalar = base_multiplier*scalar_prime % r  # The census uses b=1, Q=R.
        transformed = primitive.scalar_points[base_multiplier*scalar_prime % r] == target
        original = primitive.scalar_points[scalar] == target
        counts["retained_exact_public_equation_table_reads"] += 2
        counts["retained_exact_scalar_conversion_events"] += 1
        statuses["RECOVERED" if transformed and original else "REJECTED_FINAL_VERIFICATION"] += 1
    successes = statuses["RECOVERED"]
    return {"schema": "classical.ecdlp.transfer-study.retained-bit-exact-census/v1",
            "validator_only": True, "coverage_mode": "small_exact_nonidentity",
            "input_bit_coverage_complete": len(bits) == r and set(bits) == set(primitive.scalar_points),
            "attempts": r-1, "successes": successes, "q_numerator": successes, "q_denominator": r-1,
            "status_counts": dict(statuses), "zero_success_retained": successes == 0,
            "fresh_constructor_calls": 0, "primary_attempt_counts_changed": False,
            "public_checks": "x_prime*P_prime=R and x*P=R via independent validator public-multiple table, b=1",
            "validator_work_counts": dict(counts)}


def evaluate_odd_anchor_null(cohort: dict[str, Any], groups: dict[str, Group],
                             primitives: dict[str, Primitive], rows: dict[tuple[Any, ...], dict[str, Any]],
                             checked: list[dict[str, Any]],
                             exact_candidate_censuses: dict[tuple[str, str], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Same-shape diagnostics; adds no primary rows, draws or priced work."""
    rule_bytes = json.dumps(ODD_NULL_RULE, sort_keys=True, separators=(",", ":")).encode()
    checked_lookup = {(v["curve_id"], v["target_id"], v["arm_id"], v["replicate_index"]): v for v in checked}
    per_base, work_counts = [], Counter()
    for fixture in cohort["fixtures"]:
        curve_id, group = fixture["curve_id"], groups[fixture["curve_id"]]
        null = OddAnchorNull(group, primitives[curve_id], cohort["public_nonce_hex"], curve_id)
        exact = fixture.get("panel") == "exact" and group.r <= 127
        original_base = point(fixture["base"], group.p)
        for a in (1, 2, 3, 5):
            exact_seeds = []
            if exact:
                for seed_index in range(16):
                    status_counts: Counter[str] = Counter()
                    for label in range(1, group.r):
                        outcome = null.attempt(seed_index, a, null.points[label], original_base, label)
                        status_counts[outcome["status"]] += 1
                    successes = status_counts["RECOVERED"]
                    exact_seeds.append({"seed_index": seed_index, "successes": successes,
                                        "attempts": group.r-1, "q_numerator": successes,
                                        "q_denominator": group.r-1, "status_counts": dict(status_counts),
                                        "zero_success_retained": successes == 0})
            comparisons, observed_targets = [], set()
            for circuit_index in (1, 2):
                arm_id = f"circuit{circuit_index}.a{a}"
                matching = [(key, row) for key, row in rows.items() if key[0] == curve_id and key[2] == arm_id]
                candidate_successes = sum(checked_lookup[key]["success"] and checked_lookup[key].get("arithmetic_record_pass", True) for key, _ in matching)
                all_records_pass = all(checked_lookup[key].get("arithmetic_record_pass", True) for key, _ in matching)
                null_seeds = []
                for seed_index in range(16):
                    statuses: Counter[str] = Counter()
                    for _, row in matching:
                        transformed, original = point(row["transformed_target"], group.p), point(row["original_target"], group.p)
                        observed_targets.add(transformed)
                        outcome = null.attempt(seed_index, a, transformed, original, row["target_multiplier"])
                        statuses[outcome["status"]] += 1
                    successes, n = statuses["RECOVERED"], len(matching)
                    null_seeds.append({"seed_index": seed_index, "successes": successes, "attempts": n,
                                       "q_numerator": successes, "q_denominator": n,
                                       "status_counts": dict(statuses), "zero_success_retained": successes == 0,
                                       "candidate_minus_null_q": {"numerator": candidate_successes-successes, "denominator": n} if n else None})
                exact_candidate = (exact_candidate_censuses or {}).get((curve_id, arm_id))
                exact_differences = None
                if exact and exact_candidate is not None:
                    exact_differences = [{"seed_index": seed["seed_index"],
                                          "numerator": exact_candidate["successes"]-seed["successes"],
                                          "denominator": group.r-1} for seed in exact_seeds]
                comparisons.append({"arm_id": arm_id, "matched_attempts": len(matching),
                                    "candidate_successes": candidate_successes,
                                    "candidate_q_numerator": candidate_successes, "candidate_q_denominator": len(matching),
                                    "candidate_records_arithmetic_pass": all_records_pass,
                                    "same_observed_blinded_target_events": True, "seed_outcomes": null_seeds,
                                    "candidate_retained_bit_exact_census": exact_candidate,
                                    "candidate_exact_minus_null_exact_q": exact_differences})
            per_base.append({"curve_id": curve_id, "base_multiplier": a,
                             "coverage_mode": "small_exact_nonidentity" if exact else "larger_matched_observed_blinded_targets",
                             "exact_nonidentity_seed_outcomes": exact_seeds if exact else None,
                             "all_r_null_recovery_claim": exact,
                             "distinct_matched_transformed_targets": len(observed_targets),
                             "matched_candidate_arms": comparisons,
                             "independent_raw_null_functions": 16,
                             "repeated_comparisons_are_not_additional_independent_null_samples": True})
        work_counts.update(null.counts)
    return {"schema": "classical.ecdlp.transfer-study.odd-anchor-null/v1",
            "rule": ODD_NULL_RULE, "rule_canonical_sha256": hashlib.sha256(rule_bytes).hexdigest(),
            "per_curve_base": per_base, "validator_work_counts": dict(work_counts),
            "primary_attempt_counts_changed": False, "priced_performance_claim": False,
            "candidate_api_receives_null_bits_or_labels": False,
            "independent_function_unit": "one curve/seed raw function; all base normalizations and circuit comparisons share it",
            "aa_comparison": "A/A is a duplicate of circuit1.a1 and is not added as another null sample",
            "public_check_implementation": "Same transformed/original equations via independently certified validator public-multiple table",
            "inference_scope": "16-seed descriptive distribution only; no strong-tail, familywise-discovery, global novelty or exponent claim"}


HEX64 = re.compile(r"[0-9a-f]{64}\Z")
ANSWER_FIELDS = ("status", "bit", "reason", "z", "g", "anchor", "normalized")


def count_map(value: Any) -> bool:
    return isinstance(value, dict) and all(isinstance(k, str) and type(v) is int and v >= 0 for k, v in value.items())


def strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(strict_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(strict_equal(a, b) for a, b in zip(left, right))
    return left == right


def load_json(path: Path) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in pairs:
            if k in out:
                raise ValueError(f"duplicate JSON key: {k}")
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=reject_duplicates)


def load_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    with path.open() as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.endswith("\n") or not line.strip():
                raise ValueError(f"{path.name}:{line_number} truncated or blank row")
            row = json.loads(line, object_pairs_hook=reject_duplicates)
            if not isinstance(row, dict):
                raise ValueError(f"{path.name}:{line_number} row is not an object")
            yield row


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_sample(nonce_hex: str, role: str, draw_id: str, bound: int) -> dict[str, Any]:
    """Own domain-separated SHA256 rejection sampler for public draw replay."""
    if not isinstance(nonce_hex, str) or not HEX64.fullmatch(nonce_hex):
        raise ValueError("public nonce must be exactly 32 bytes of lowercase hex")
    if type(bound) is not int or not 1 <= bound < 2**64:
        raise ValueError("invalid public sampler bound")
    prefix = bytes.fromhex(nonce_hex)+b"\x00transfer-study/v1/"+role.encode()+b"\x00"+draw_id.encode()
    threshold = (2**256//bound)*bound
    for counter in range(10000):
        digest = hashlib.sha256(prefix+counter.to_bytes(8, "big")).digest()
        value = int.from_bytes(digest, "big")
        if value < threshold:
            return {"role": role, "draw_id": draw_id, "rejection_counter": counter,
                    "digest_hex": digest.hex(), "bound": bound, "value": value % bound}
    raise ValueError("public sampler exceeded verifier software limit")


def check_source_manifest(manifest: dict[str, Any], source_root: Path) -> dict[str, str]:
    """Bind exact bytes; source binding does not establish executed-source proof."""
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("source manifest requires nonempty files map")
    root, checked = source_root.resolve(), {}
    for name, digest in files.items():
        if not isinstance(name, str) or not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise ValueError("source manifest file/hash malformed")
        path = (root / name).resolve()
        if path == root or root not in path.parents:
            raise ValueError("source manifest path escapes source root")
        observed = sha256_file(path)
        if observed != digest:
            raise ValueError(f"source hash mismatch: {name}")
        checked[name] = observed
    return checked


def verify_trace(group: Group, primitive: Primitive, original_base: Any,
                 transformed_base: Any, target: Any, multiplier: int,
                 alpha: int, beta: int, result: dict[str, Any], *,
                 target_multiplier: int = 1, transformed_target: Any = None) -> dict[str, Any]:
    """Arithmetic integrity is separate from whether a candidate succeeds.

    All L answers are checked, including answers following an undefined value.
    A correctly retained undefined/failure attempt is a valid record.
    """
    errors: list[str] = []
    p, r = group.p, group.r
    base, base_prime, q_original = point(original_base, p), point(transformed_base, p), point(target, p)
    if type(multiplier) is not int or not 1 <= multiplier < r:
        raise ValueError("base multiplier must be canonical nonzero integer")
    if base_prime != group.mul(multiplier, base):
        errors.append("transformed base is not [a]P")
    if type(target_multiplier) is not int or not 1 <= target_multiplier < r:
        raise ValueError("target multiplier must be canonical nonzero integer")
    expected_q = group.mul(target_multiplier, q_original)
    q = expected_q if transformed_target is None else point(transformed_target, p)
    if q != expected_q:
        errors.append("transformed target is not [b]Q")
    if (alpha, beta) not in FIXED_CIRCUITS:
        errors.append("circuit is outside fixed two-template family")
    length = r.bit_length()+1
    trace = result.get("predicate_trace")
    if not isinstance(trace, list):
        return {"pass": False, "errors": errors+["missing predicate_trace"], "success": False}
    if len(trace) != length:
        errors.append("trace does not contain exactly L fresh answer records")
    for field in ("L", "predicate_evaluations"):
        if type(result.get(field)) is not int or result[field] != length:
            errors.append(f"{field} does not equal L")
    if type(result.get("retained_bit_reads")) is not int or result["retained_bit_reads"] != 0:
        errors.append("recovery must declare zero retained-bit reads")
    if result.get("gate") is not None or result.get("gated") not in (None, False):
        errors.append("primary attempt must be ungated")
    current, digits, undefined, evaluation_counts, per_query_counters, undefined_reasons = q, [], [], Counter(), [], []
    for index, entry in enumerate(trace):
        try:
            if not isinstance(entry, dict):
                raise ValueError("trace entry is not an object")
            if type(entry.get("index")) is not int or entry["index"] != index:
                errors.append(f"trace[{index}] index mismatch")
            if point(entry["target"], p) != current:
                errors.append(f"trace[{index}] public doubling target mismatch")
            observed = entry["answer"]
            expected = answer(primitive, base_prime, current, alpha, beta)
            if not isinstance(observed, dict):
                raise ValueError("answer is not an object")
            for field in ANSWER_FIELDS:
                if observed.get(field) != expected.get(field) or (type(observed.get(field)) is not type(expected.get(field))):
                    errors.append(f"trace[{index}].answer.{field} mismatch")
            for field in ("z", "g", "anchor", "normalized"):
                v = observed.get(field)
                if v is not None and (type(v) is not int or not 0 <= v < p):
                    errors.append(f"trace[{index}].answer.{field} noncanonical")
            if observed.get("status") == "BIT" and type(observed.get("bit")) is int and observed["bit"] in (0, 1):
                digits.append(observed["bit"])
            else:
                undefined.append(index)
                undefined_reasons.append(expected["reason"])
            per_query_counters.append("counters" in entry)
            if "counters" in entry and not count_map(entry["counters"]):
                errors.append(f"trace[{index}] counters malformed")
            elif "counters" in entry:
                evaluation_counts.update(entry["counters"])
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append(f"trace[{index}] malformed: {exc}")
            undefined.append(index)
        if index+1 < length:
            current = group.add(current, current)
    counts = result.get("counts", {})
    sum_checked = bool(per_query_counters) and all(per_query_counters)
    if any(per_query_counters) and not sum_checked:
        errors.append("per-query counter coverage must be all or none")
    if not count_map(counts.get("evaluate")) or (sum_checked and dict(evaluation_counts) != counts["evaluate"]):
        errors.append("counts.evaluate malformed or does not sum the full trace")
    for phase in ("reduction", "blinding", "conversion"):
        if not count_map(counts.get(phase)):
            errors.append(f"counts.{phase} malformed")
    if undefined or len(trace) != length:
        expected_status, success, scalar_prime, scalar = "UNDEFINED", False, None, None
        interval = {"value": None, "denominator": 1 << length, "lower_numerator": None, "upper_numerator": None, "nonempty": False}
        prime_equation, original_equation = None, None
        expected_reason = ",".join(sorted(set(reason for reason in undefined_reasons if isinstance(reason, str))))
    else:
        interval = interval_candidate(r, digits)
        scalar_prime = interval["candidate"]
        scalar = multiplier*pow(target_multiplier, -1, r)*scalar_prime % r if interval["nonempty"] else None
        prime_equation = group.mul(scalar_prime, base_prime) == q if interval["nonempty"] else None
        original_equation = group.mul(scalar, base) == q_original if interval["nonempty"] else None
        success = interval["nonempty"] and prime_equation and original_equation
        expected_status = "RECOVERED" if success else "EMPTY_INTERVAL" if not interval["nonempty"] else "REJECTED_FINAL_VERIFICATION"
        expected_reason = None if success else "EMPTY_BINARY_INTERVAL" if not interval["nonempty"] else "FINAL_VERIFICATION_FAILED"
    if result.get("status") != expected_status:
        errors.append("recovery status mismatch")
    if result.get("reason") != expected_reason:
        errors.append("recovery reason mismatch")
    if not strict_equal(result.get("interval"), {k: v for k, v in interval.items() if k != "candidate"}):
        errors.append("interval mismatch")
    expected_checks = {"transformed": prime_equation, "original": original_equation}
    if not strict_equal(result.get("public_checks"), expected_checks):
        errors.append("public_checks mismatch")
    if not strict_equal(result.get("target_multiplier_inverse"), pow(target_multiplier, -1, r)):
        errors.append("target multiplier inverse mismatch")
    expected_fields = {"candidate_scalar_prime": scalar_prime, "candidate_scalar": scalar,
                       "scalar_prime": scalar_prime if success else None,
                       "scalar": scalar if success else None}
    for field, expected in expected_fields.items():
        if result.get(field) != expected or type(result.get(field)) is not type(expected):
            errors.append(f"{field} mismatch")
    return {"pass": not errors, "errors": errors, "success": success,
            "undefined_indices": undefined, "interval": interval,
            "candidate_scalar_prime": scalar_prime, "candidate_scalar": scalar,
            "public_final_check": success, "predicate_evaluations": len(trace),
            "source_counters_replayed": False, "aggregate_sum_check_performed": sum_checked,
            "source_evaluate_counts": counts.get("evaluate")}


def check_scalar_witness(group: Group, base: Any, target: Any, result: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    scalar = result.get("scalar")
    valid = type(scalar) is int and 0 <= scalar < group.r
    if valid:
        valid = group.mul(scalar, point(base, group.p)) == point(target, group.p)
    declared_success = result.get("status") == "RECOVERED"
    if declared_success != valid:
        errors.append("scalar/status public witness mismatch")
    if not declared_success and scalar is not None:
        errors.append("unsuccessful baseline must retain null scalar")
    return {"pass": not errors, "errors": errors, "success": valid}


def summarize_attempts(checked: Iterable[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, Any] = {}
    for arm, rows in _group_by_arm(checked).items():
        successes = sum(row["success"] for row in rows)
        totals[arm] = {"attempts": len(rows), "successes": successes,
                       "q_numerator": successes, "q_denominator": len(rows),
                       "zero_success_retained": successes == 0,
                       "zero_observed_is_not_proven_zero_probability": True,
                       "cost_over_q": None if successes == 0 else "producer-counter totals/successes; requires external complete-cost qualification",
                       "cost_over_q_status": "ZERO_OBSERVED_ESTIMATE_UNDEFINED" if successes == 0 else "COUNTER_VECTOR_ONLY_UNREPLAYED"}
    return totals


def _group_by_arm(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["arm_id"]].append(row)
    return grouped


def canonical_arms() -> dict[str, dict[str, Any]]:
    arms: dict[str, dict[str, Any]] = {}
    for index, (alpha, beta) in enumerate(FIXED_CIRCUITS, 1):
        for a in (1, 2, 3, 5):
            key = f"circuit{index}.a{a}"
            arms[key] = {"kind": "candidate", "a": a, "alpha": alpha, "beta": beta, "reference_id": key}
    arms["uniform_candidate"] = {"kind": "uniform_candidate", "a": 1}
    arms["bsgs_reference"] = {"kind": "bsgs_reference", "a": 1}
    arms["aa_circuit1_a1"] = dict(arms["circuit1.a1"], kind="aa_replay")
    return arms


def _fixture_model(fixture: dict[str, Any]) -> dict[str, int]:
    return {k: fixture[k] for k in ("p", "a", "b", "r")}


def verify_records(cohort: dict[str, Any], attempts: Iterable[dict[str, Any]],
                   setups: Iterable[dict[str, Any]], diagnostics: Iterable[dict[str, Any]],
                   *, require_complete: bool = True, expected_bindings: dict[str, str] | None = None) -> dict[str, Any]:
    """Independently derive exact Cartesian coverage from the frozen public cohort.

    require_complete=False is solely a synthetic-test helper. Production CLI
    always requires complete streams, including unsuccessful attempts.
    """
    arms, fixtures, errors, seen_curve_keys = canonical_arms(), {}, [], set()
    groups: dict[str, Group] = {}
    primitives: dict[str, Primitive] = {}
    expected_attempts, expected_setups, expected_diagnostics = set(), set(), set()
    targets: dict[tuple[str, str], Point] = {}
    nonce = cohort.get("public_nonce_hex")
    if not isinstance(nonce, str) or not HEX64.fullmatch(nonce):
        raise ValueError("cohort must bind a public 32-byte nonce")
    for fixture in cohort["fixtures"]:
        curve_id = fixture["curve_id"]
        if not isinstance(curve_id, str) or not curve_id or curve_id in fixtures:
            raise ValueError("missing or duplicate curve_id")
        fixtures[curve_id] = fixture
        group = Group(_fixture_model(fixture))
        j = 1728*4*group.a**3*pow((4*group.a**3+27*group.b**2) % group.p, -1, group.p) % group.p
        curve_key = group.p, j
        if curve_key in seen_curve_keys:
            raise ValueError("duplicate field/j-invariant curve or coordinate view")
        seen_curve_keys.add(curve_key)
        base = point(fixture["base"], group.p)
        group.certify_base(base)
        groups[curve_id], primitives[curve_id] = group, Primitive(group, base)
        seen_points = set()
        for target in fixture["targets"]:
            target_id, q = target["target_id"], point(target["point"], group.p)
            key = curve_id, target_id
            if not isinstance(target_id, str) or not target_id or key in targets or q in seen_points:
                raise ValueError("duplicate or invalid public target")
            if q is None or not group.on_curve(q) or group.mul(group.r, q) is not None:
                raise ValueError("primary target must be nonidentity r-torsion")
            targets[key] = q
            seen_points.add(q)
            for arm_id in arms:
                for rep in range(1 if arm_id == "bsgs_reference" else 4):
                    expected_attempts.add((curve_id, target_id, arm_id, rep))
        for arm_id, arm in arms.items():
            expected_setups.add((curve_id, arm_id))
            if fixture.get("panel") == "exact" and arm["kind"] == "candidate":
                if group.r > 127 or len(fixture["targets"]) != group.r-1:
                    raise ValueError("exact panel must be a registered small full nonidentity subgroup")
                for q in group.orbit(base):
                    expected_diagnostics.add((curve_id, arm_id, q))
    observed_attempts, observed_setups, observed_diagnostics = set(), set(), set()
    checked, aa_rows, source_costs, diagnostic_bits = [], {}, defaultdict(Counter), defaultdict(dict)
    setup_costs_by_domain, online_costs_by_domain = defaultdict(Counter), defaultdict(Counter)

    def check_binding(row: dict[str, Any]) -> None:
        if expected_bindings:
            for name, digest in expected_bindings.items():
                if row.get(name) != digest:
                    raise ValueError(f"{name} does not bind exact supplied bytes")

    for index, row in enumerate(setups):
        try:
            check_binding(row)
            if row.get("schema") != "classical.ecdlp.transfer-study.setup/v1":
                raise ValueError("setup schema mismatch")
            curve_id, arm_id = row["curve_id"], row["arm_id"]
            key = curve_id, arm_id
            if key not in expected_setups or key in observed_setups:
                raise ValueError("unexpected or duplicate setup")
            observed_setups.add(key)
            fixture, arm, group = fixtures[curve_id], arms[arm_id], groups[curve_id]
            if row.get("kind") != arm["kind"]:
                raise ValueError("setup kind mismatch")
            base = point(fixture["base"], group.p)
            base_prime = group.mul(arm["a"], base)
            if not strict_equal(row["model"], group.model) or point(row["original_base"], group.p) != base or not strict_equal(row["base_multiplier"], arm["a"]) or point(row["transformed_base"], group.p) != base_prime:
                raise ValueError("setup public model/base transformation mismatch")
            circuit = {"alpha": arm["alpha"], "beta": arm["beta"]} if "alpha" in arm else None
            if not strict_equal(row.get("circuit"), circuit) or row.get("shared_across_targets") is not True:
                raise ValueError("setup circuit or amortization declaration mismatch")
            expected = answer(primitives[curve_id], base_prime, None, arm["alpha"], arm["beta"]) if circuit else {"status": "BIT", "reason": None}
            if row.get("status") != ("UNDEFINED" if expected["status"] == "UNDEFINED" else "READY") or row.get("reason") != expected["reason"]:
                raise ValueError("setup status/reason mismatch")
            expected_entries = isqrt(group.r-1)+1 if arm_id == "bsgs_reference" else 0
            if not strict_equal(row.get("reference_state_entries"), expected_entries):
                raise ValueError("baseline table-entry count mismatch")
            for phase in ("base_transform", "constructor_setup", "reference_setup"):
                if not count_map(row["counts"].get(phase)):
                    raise ValueError("setup counter map malformed")
                source_costs[arm_id].update(row["counts"][phase])
                setup_costs_by_domain[key].update(row["counts"][phase])
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append({"stream": "setups", "index": index, "error": str(exc)})
    for index, row in enumerate(attempts):
        try:
            check_binding(row)
            if row.get("schema") != "classical.ecdlp.transfer-study.attempt/v1":
                raise ValueError("attempt schema mismatch")
            curve_id, target_id, arm_id, rep = row["curve_id"], row["target_id"], row["arm_id"], row["replicate_index"]
            key = curve_id, target_id, arm_id, rep
            if type(rep) is not int or key not in expected_attempts or key in observed_attempts:
                raise ValueError("unexpected or duplicate attempt")
            observed_attempts.add(key)
            fixture, arm, group, q = fixtures[curve_id], arms[arm_id], groups[curve_id], targets[(curve_id, target_id)]
            if row.get("kind") != arm["kind"]:
                raise ValueError("attempt kind mismatch")
            base = point(fixture["base"], group.p)
            base_prime = group.mul(arm["a"], base)
            expected_id = f"{curve_id}/{target_id}/{arm_id}/rep{rep}"
            if row.get("attempt_id") != expected_id or not strict_equal(row["model"], group.model) or point(row["original_base"], group.p) != base or point(row["original_target"], group.p) != q or not strict_equal(row["base_multiplier"], arm["a"]) or point(row["transformed_base"], group.p) != base_prime:
                raise ValueError("attempt identity/public input mismatch")
            result = row["result"]
            if "alpha" in arm:
                draw_id = f"{curve_id}/{target_id}/{arm['reference_id']}/rep{rep}"
                sample = expected_sample(nonce, "target-blinding", draw_id, group.r-1)
                b = sample["value"]+1
                if not strict_equal(row.get("sampling"), sample) or type(row.get("target_multiplier")) is not int or row["target_multiplier"] != b:
                    raise ValueError("target-blinding sampler replay mismatch")
                checked_row = verify_trace(group, primitives[curve_id], row["original_base"], row["transformed_base"], row["original_target"], arm["a"], arm["alpha"], arm["beta"], result, target_multiplier=b, transformed_target=row["transformed_target"])
            else:
                if not strict_equal(row.get("target_multiplier"), 1) or point(row["transformed_target"], group.p) != q:
                    raise ValueError("baseline must retain original public target")
                checked_row = check_scalar_witness(group, base, q, result)
                if result.get("L") is not None or type(result.get("predicate_evaluations")) is not int or result.get("predicate_evaluations") != 0 or result.get("predicate_trace") != [] or result.get("interval") is not None or type(result.get("retained_bit_reads")) is not int or result.get("retained_bit_reads") != 0:
                    raise ValueError("baseline predicate/interval fields mismatch")
                if arm_id == "uniform_candidate":
                    sample = expected_sample(nonce, "uniform-candidate", expected_id, group.r-1)
                    candidate = sample["value"]+1
                    if not strict_equal(row.get("sampling"), sample) or not strict_equal(result.get("candidate_scalar"), candidate):
                        raise ValueError("uniform-candidate sample mismatch")
                    expected_success = group.mul(candidate, base) == q
                    if checked_row["success"] != expected_success:
                        raise ValueError("uniform-candidate final check mismatch")
                    if result.get("status") != ("RECOVERED" if expected_success else "REJECTED_FINAL_VERIFICATION"):
                        raise ValueError("uniform-candidate status mismatch")
                elif not checked_row["success"]:
                    raise ValueError("working BSGS reference failed its public target")
                elif row.get("sampling") is not None:
                    raise ValueError("BSGS reference must have no random sampling")
                candidate = result.get("candidate_scalar")
                if not strict_equal(result.get("candidate_scalar_prime"), candidate):
                    raise ValueError("baseline scalar coordinate mismatch")
                if not strict_equal(result.get("scalar_prime"), result.get("scalar")):
                    raise ValueError("baseline verified scalar coordinate mismatch")
                expected_checks = {"transformed": checked_row["success"], "original": checked_row["success"]}
                if not strict_equal(result.get("public_checks"), expected_checks):
                    raise ValueError("baseline public_checks mismatch")
                if result.get("reason") != (None if checked_row["success"] else "FINAL_VERIFICATION_FAILED"):
                    raise ValueError("baseline reason mismatch")
                if not count_map(result.get("counts", {}).get("online")):
                    raise ValueError("baseline counts.online missing")
            if not checked_row["pass"]:
                errors.append({"stream": "attempts", "index": index, "errors": checked_row["errors"]})
            for phase, counts in result.get("counts", {}).items():
                if not count_map(counts):
                    raise ValueError(f"attempt counts.{phase} malformed")
                source_costs[arm_id].update(counts)
                online_costs_by_domain[(curve_id, arm_id)].update(counts)
            checked.append({"curve_id": curve_id, "target_id": target_id, "replicate_index": rep,
                            "arm_id": arm_id, "success": checked_row["success"], "status": result["status"],
                            "arithmetic_record_pass": checked_row["pass"]})
            aa_rows[key] = row
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append({"stream": "attempts", "index": index, "error": str(exc)})
    for index, row in enumerate(diagnostics):
        try:
            check_binding(row)
            if row.get("schema") != "classical.ecdlp.transfer-study.diagnostic/v1":
                raise ValueError("diagnostic schema mismatch")
            curve_id, arm_id = row["curve_id"], row["arm_id"]
            group, arm = groups[curve_id], arms[arm_id]
            q = point(row["target"], group.p)
            key = curve_id, arm_id, q
            if key not in expected_diagnostics or key in observed_diagnostics:
                raise ValueError("unexpected or duplicate diagnostic")
            observed_diagnostics.add(key)
            base_prime = group.mul(arm["a"], point(fixtures[curve_id]["base"], group.p))
            if not strict_equal(row["model"], group.model) or not strict_equal(row["base_multiplier"], arm["a"]) or point(row["transformed_base"], group.p) != base_prime:
                raise ValueError("diagnostic public input mismatch")
            if row.get("used_to_gate_primary") is not False or row.get("shared_setup_reused") is not True:
                raise ValueError("diagnostic must remain separate from primary gating")
            expected = answer(primitives[curve_id], base_prime, q, arm["alpha"], arm["beta"])
            if any(row["answer"].get(k) != expected.get(k) or type(row["answer"].get(k)) is not type(expected.get(k)) for k in ANSWER_FIELDS):
                raise ValueError("diagnostic independent arithmetic mismatch")
            if not count_map(row.get("counters")):
                raise ValueError("diagnostic counter map malformed")
            diagnostic_bits[(curve_id, arm_id)][q] = expected["bit"]
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append({"stream": "diagnostics", "index": index, "error": str(exc)})
    for key, row in aa_rows.items():
        if key[2] != "aa_circuit1_a1":
            continue
        reference = aa_rows.get((key[0], key[1], "circuit1.a1", key[3]))
        if reference is None or any(row.get(k) != reference.get(k) for k in ("result", "sampling", "transformed_target", "target_multiplier")):
            errors.append({"stream": "attempts", "attempt_id": row["attempt_id"], "error": "A/A exact replay mismatch"})
    coverage = {}
    for name, expected, observed in (("attempts", expected_attempts, observed_attempts), ("setups", expected_setups, observed_setups), ("diagnostics", expected_diagnostics, observed_diagnostics)):
        missing = expected-observed
        coverage[name] = {"expected": len(expected), "observed": len(observed), "missing": len(missing), "complete": not missing}
        if require_complete and missing:
            errors.append({"stream": name, "error": "incomplete frozen coverage", "missing_count": len(missing), "first_missing": repr(min(missing, key=repr))})
    summary = summarize_attempts(checked)
    for arm_id, totals in summary.items():
        successes = totals["successes"]
        totals["producer_counter_totals_including_setup"] = dict(source_costs[arm_id])
        totals["producer_counter_cost_over_q"] = None if successes == 0 else {k: {"numerator": v, "denominator": successes} for k, v in source_costs[arm_id].items()}
    per_domain = []
    for curve_id in fixtures:
        for arm_id in arms:
            domain_rows = [row for row in checked if row["curve_id"] == curve_id and row["arm_id"] == arm_id]
            n, successes = len(domain_rows), sum(row["success"] for row in domain_rows)
            setup, online = setup_costs_by_domain[(curve_id, arm_id)], online_costs_by_domain[(curve_id, arm_id)]
            keys = setup.keys() | online.keys()
            per_domain.append({"curve_id": curve_id, "arm_id": arm_id, "attempts": n, "successes": successes,
                               "q_numerator": successes, "q_denominator": n,
                               "source_setup_counters_once": dict(setup), "source_online_counters_all_attempts": dict(online),
                               "observed_batch_counter_cost_per_success": None if not successes else {k: {"numerator": setup[k]+online[k], "denominator": successes} for k in keys},
                               "cold_retry_counter_estimate_reusing_setup": None if not successes else {k: {"numerator": successes*setup[k]+online[k], "denominator": successes} for k in keys},
                               "cold_retry_model": "S + mean(online)/q; producer counters unreplayed; common input/generation costs reported separately",
                               "zero_observed_is_not_proven_zero_probability": True})
    diagnostic_reports, cocycle_pairs, primitive_controls = [], 0, []
    exact_candidate_censuses, retained_census_counts = {}, Counter()
    for curve_id, group in groups.items():
        primitive = primitives[curve_id]
        original_base = point(fixtures[curve_id]["base"], group.p)
        rtl, control_points = Primitive(group, original_base, "addition_chain"), []
        reindexed = Primitive(group, group.mul(2, original_base), "orbit_coefficient")
        for index in range(12):
            scalar = index*group.r//12
            q = primitive.scalar_point(scalar)
            control_points.append(encoded(q))
            if primitive.z(q) != rtl.z(q):
                errors.append({"curve_id": curve_id, "error": "cumulative primitive/right-to-left chain mismatch", "public_control_index": index})
            if primitive.z(q) != reindexed.z(q):
                errors.append({"curve_id": curve_id, "error": "cumulative primitive/base-2P rebuild mismatch", "public_control_index": index})
        if fixtures[curve_id].get("panel") != "exact":
            for index in range(12):
                left = primitive.scalar_point(index*group.r//12)
                right = primitive.scalar_point(((5*index+1) % 12)*group.r//12)
                if primitive.z(group.add(left, right)) != (primitive.z(left)+primitive.z(right)+group.slope(left, right)) % group.p:
                    errors.append({"curve_id": curve_id, "error": "large fixed-pair cocycle mismatch", "public_control_index": index})
            primitive_controls.append({"curve_id": curve_id, "right_to_left_points_checked": control_points, "base_2P_rebuild_points_checked": 12, "fixed_cocycle_pairs_checked": 12, "full_slope_sum_points_checked": 0})
            continue
        orbit = group.orbit(original_base)
        summed = Primitive(group, original_base, "slope_sum")
        for q in orbit:
            if primitive.z(q) != summed.z(q):
                errors.append({"curve_id": curve_id, "error": "cumulative primitive/full slope-sum mismatch", "target": encoded(q)})
        primitive_controls.append({"curve_id": curve_id, "right_to_left_points_checked": control_points, "base_2P_rebuild_points_checked": 12, "fixed_cocycle_pairs_checked": group.r**2, "full_slope_sum_points_checked": group.r})
        for left in orbit:
            if primitive.z(group.neg(left)) != -primitive.z(left) % group.p:
                errors.append({"curve_id": curve_id, "error": "independent primitive oddness failure"})
            for right in orbit:
                cocycle_pairs += 1
                if primitive.z(group.add(left, right)) != (primitive.z(left)+primitive.z(right)+group.slope(left, right)) % group.p:
                    errors.append({"curve_id": curve_id, "error": "independent primitive cocycle failure"})
        for arm_id, arm in arms.items():
            if arm["kind"] != "candidate":
                continue
            base_prime = group.mul(arm["a"], original_base)
            relative_orbit = group.orbit(base_prime)
            bits = diagnostic_bits[(curve_id, arm_id)]
            exact_census = retained_bit_exact_census(group, primitive, arm["a"], bits)
            exact_candidate_censuses[(curve_id, arm_id)] = exact_census
            retained_census_counts.update(exact_census["validator_work_counts"])
            undefined, mismatches, residual = [], [], []
            for scalar, q in enumerate(relative_orbit):
                bit = bits.get(q)
                if bit not in (0, 1):
                    undefined.append(encoded(q))
                elif bit != int(scalar > (group.r-1)//2):
                    mismatches.append({"target": encoded(q), "observed_bit": bit, "expected_bit": int(scalar > (group.r-1)//2)})
                following = bits.get(group.add(q, base_prime))
                pulse = int(scalar == (group.r-1)//2)-int(scalar == group.r-1)
                residual.append(None if bit not in (0, 1) or following not in (0, 1) else following-bit-pulse)
            diagnostic_reports.append({"curve_id": curve_id, "arm_id": arm_id,
                                       "validator_only": True, "primary_attempts_gated": False,
                                       "all_r_coverage": len(bits) == group.r,
                                       "undefined_count": len(undefined), "undefined_targets": undefined,
                                       "truth_mismatch_count": len(mismatches),
                                       "retained_bit_exact_recovery_census": exact_census,
                                       "first_counterexample": mismatches[0] if mismatches else None,
                                       "two_pulse_target_order": [encoded(q) for q in relative_orbit],
                                       "two_pulse_residual": residual})
    null_report = evaluate_odd_anchor_null(cohort, groups, primitives, aa_rows, checked, exact_candidate_censuses)
    return {"schema": "classical.ecdlp.transfer-study.verification/v1", "pass": not errors,
            "arithmetic_and_coverage_pass": not errors, "errors": errors, "coverage": coverage,
            "arm_outcomes": summary, "small_all_r_diagnostics": diagnostic_reports,
            "per_curve_arm_outcomes": per_domain,
            "validator_odd_anchor_null": null_report,
            "retained_bit_exact_census_validator_work_counts": dict(retained_census_counts),
            "validator_primitive_controls": primitive_controls,
            "full_cocycle_pairs_checked": cocycle_pairs,
            "validator_work_counts": dict(sum((g.counts for g in groups.values()), Counter())),
            "validator_work_counter_scope": "Exact algorithm events, orbit entries/reads, affine group/slope/inversion calls across primary oracle and controls; not complete machine or field-operation costs",
            "source_counters_replayed": False, "machine_cost_qualified": False,
            "complete_attack_cost_qualified": False,
            "q_sampling_model": "Registered random public nonce and domain-separated SHA256 PRG rejection draws; independence/uniformity is a model assumption, not proven by traces",
            "fresh_execution_proven_by_traces": False, "scientific_execution_performed_by_verifier": False,
            "primitive_scope": {"primary": "validator-only O(r) cumulative public-orbit coefficient table, r<=8191",
                                "small_controls": "full independent slope sum and full cocycle, exact panel only",
                                "all_curve_controls": "12 predefined right-to-left coefficient-chain points; 12 fixed cocycle pairs on larger curves",
                                "limitation": "all constructions share registered cocycle mathematics; internal full-orbit primitive/label coverage is not larger all-r bit coverage"}}


def verify_controls(control: dict[str, Any]) -> dict[str, Any]:
    """Check the separately recorded, fixed prior F11 instrument controls."""
    errors: list[str] = []
    model = {"p": 11, "a": 1, "b": 6, "r": 13}
    group, base, q = Group(model), (2, 7), (7, 2)
    expected = {"schema": "classical.ecdlp.transfer-study.legacy-control/v1", "model": model,
                "original_base": [2, 7], "target": [7, 2], "base_multiplier": 5,
                "target_multiplier": 1, "transformed_base": encoded(group.mul(5, base)),
                "transformed_target": [7, 2], "wrong_scalar": 8,
                "fresh_cohort_generated": False, "included_in_primary_attempt_counts": False}
    for key, value in expected.items():
        if not strict_equal(control.get(key), value):
            errors.append(f"legacy control {key} mismatch")
    try:
        candidate = verify_trace(group, Primitive(group, base), list(base), expected["transformed_base"], list(q), 5, 1, -4, control["candidate_result"], target_multiplier=1, transformed_target=list(q))
        if not candidate["pass"] or not candidate["success"] or candidate["candidate_scalar_prime"] != 4 or candidate["candidate_scalar"] != 7:
            errors.append({"candidate_control_errors": candidate["errors"]})
        bsgs = check_scalar_witness(group, list(base), list(q), control["bsgs_result"])
        if not bsgs["pass"] or not bsgs["success"] or control["bsgs_result"].get("scalar") != 7:
            errors.append("legacy BSGS witness mismatch")
        rejected = group.mul(8, base) != q
        if not rejected or control.get("wrong_scalar_rejected") is not True or control.get("passed") is not True:
            errors.append("legacy wrong-scalar rejection or pass flag mismatch")
        if not count_map(control.get("negative_equation_counts")) or not isinstance(control.get("separate_setup_counts"), dict) or any(not count_map(v) for v in control["separate_setup_counts"].values()):
            errors.append("legacy separate cost map malformed")
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return {"pass": not errors, "errors": errors, "included_in_primary_attempt_counts": False,
            "producer_counters_replayed": False, "validator_work_counts": dict(group.counts)}


def verify_cohort_schedule(plan: dict[str, Any], cohort: dict[str, Any], exclusions: dict[str, Any]) -> dict[str, Any]:
    """Check locked public strata and exclusions, without trusting census labels."""
    if exclusions.get("schema") != "classical.ecdlp.transfer-study.exclusions/v1":
        raise ValueError("prior exclusion schema mismatch")
    canonical_plan = json.dumps(plan, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if cohort.get("plan_canonical_sha256") != hashlib.sha256(canonical_plan).hexdigest():
        raise ValueError("public cohort does not bind canonical frozen compute plan")
    excluded = {(v["p"], v["j"]) for v in exclusions["curve_keys"]}
    fields = set(exclusions.get("excluded_fields", []))
    strata = {s["id"]: s for s in plan["cohort"]["strata"]}
    if len(strata) != len(plan["cohort"]["strata"]):
        raise ValueError("duplicate frozen stratum IDs")
    observed: Counter[str] = Counter()
    for fixture in cohort["fixtures"]:
        sid = fixture["stratum_id"]
        if sid not in strata:
            raise ValueError("fixture outside frozen stratum IDs")
        stratum, model = strata[sid], _fixture_model(fixture)
        group = Group(model)
        certificate = group.certify_base(point(fixture["base"], group.p))
        if not stratum["p_min"] <= group.p <= stratum["p_max"] or (stratum.get("r_bits") is not None and group.r.bit_length() != stratum["r_bits"]) or (stratum.get("target_order") is not None and group.r != stratum["target_order"]):
            raise ValueError("fixture violates frozen field/order stratum")
        j = 1728*4*group.a**3*pow((4*group.a**3+27*group.b**2) % group.p, -1, group.p) % group.p
        if group.p in fields or (group.p, j) in excluded:
            raise ValueError("fresh fixture violates frozen prior field/j exclusions")
        exact = stratum["target_mode"] == "all_nonidentity"
        if stratum["target_mode"] not in ("all_nonidentity", "sampled_unique"):
            raise ValueError("unsupported frozen target mode")
        if fixture["panel"] != ("exact" if exact else "sampled") or len(fixture["targets"]) != (group.r-1 if exact else stratum["target_count"]):
            raise ValueError("fixture target coverage violates frozen stratum")
        digest = hashlib.sha256(json.dumps(model, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]
        expected_id = f"transfer-{sid}-{observed[sid]:03d}-{digest}"
        if fixture["curve_id"] != expected_id:
            raise ValueError("fixture ID/model/accepted ordinal mismatch")
        expected_certificate = {"point_count": group.r, "x_values_counted": group.p, "trace": certificate["trace"], "j": j,
                                "full_order_prime": True, "base_nonidentity": True, "base_r_multiple_is_identity": True}
        supplied = fixture["generation_certificate"]
        if any(not strict_equal(supplied.get(k), v) for k, v in expected_certificate.items()):
            raise ValueError("generation certificate disagrees with independent public witness")
        if type(supplied.get("proposal_ordinal")) is not int or not 0 <= supplied["proposal_ordinal"] < stratum["max_proposals"]:
            raise ValueError("accepted proposal ordinal outside frozen cap")
        if exact and [t["point"] for t in fixture["targets"]] != sorted(t["point"] for t in fixture["targets"]):
            raise ValueError("exact target coordinate order changed")
        for index, target in enumerate(fixture["targets"]):
            if target["target_id"] != f"{expected_id}-q{index:05d}":
                raise ValueError("public target ID/ordinal mismatch")
        observed[sid] += 1
    if any(observed[sid] != stratum["curve_count"] for sid, stratum in strata.items()):
        raise ValueError("fresh fixture strata are incomplete")
    if cohort.get("scalar_truth_generated") is not False or cohort.get("shortfalls") != []:
        raise ValueError("public cohort contains scalar truth or incomplete generation")
    return {"pass": True, "stratum_counts": dict(observed), "prior_field_and_j_exclusions_checked": True,
            "public_order_witness_independently_checked": True,
            "proposal_stream_replayed": False, "census_cost_counters_replayed": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("protocol", "cohort", "source-manifest", "source-root", "prior-exclusions", "attempts", "setups", "diagnostics", "controls", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan, cohort, manifest = load_json(args.protocol), load_json(args.cohort), load_json(args.source_manifest)
        if plan.get("schema") != "classical.ecdlp.transfer-study.compute-plan/v1" or plan.get("status") != "frozen":
            raise ValueError("production verification requires the exact frozen transfer compute plan")
        source_hash, cohort_hash, protocol_hash = sha256_file(args.source_manifest), sha256_file(args.cohort), sha256_file(args.protocol)
        if plan.get("source_manifest_sha256") != source_hash:
            raise ValueError("plan source manifest hash does not match supplied exact bytes")
        if cohort.get("schema") != "classical.ecdlp.transfer-study.public-cohort/v1" or cohort.get("generation_status") != "complete":
            raise ValueError("complete public cohort required")
        if set(manifest.get("files", {})) != {"curve.py", "constructor.py", "cohort.py", "compute.py", "verify.py", "controller.py", "driver.py"}:
            raise ValueError("source manifest must bind the exact seven production modules")
        source_files = check_source_manifest(manifest, args.source_root)
        if sha256_file(args.prior_exclusions) != plan["cohort"]["exclusion_file_sha256"]:
            raise ValueError("prior-exclusion file differs from frozen hash")
        schedule = verify_cohort_schedule(plan, cohort, load_json(args.prior_exclusions))
        controls = verify_controls(load_json(args.controls))
        report = verify_records(cohort, load_jsonl(args.attempts), load_jsonl(args.setups), load_jsonl(args.diagnostics),
                                expected_bindings={"source_fingerprint": source_hash,
                                                   "protocol_sha256": protocol_hash,
                                                   "cohort_sha256": cohort_hash})
        report["legacy_controls"] = controls
        report["cohort_schedule_and_exclusions"] = schedule
        if not controls["pass"]:
            report["errors"].append({"error": "legacy control verification failed", "details": controls["errors"]})
            report["pass"] = report["arithmetic_and_coverage_pass"] = False
        expected = plan.get("expected", {})
        derived = {"candidate_attempts_planned": sum(v["attempts"] for k, v in report["arm_outcomes"].items() if k not in ("uniform_candidate", "bsgs_reference")),
                   "baseline_attempts_planned": sum(v["attempts"] for k, v in report["arm_outcomes"].items() if k in ("uniform_candidate", "bsgs_reference")),
                   "total_attempts_planned": report["coverage"]["attempts"]["expected"],
                   "fixture_count_planned": len(cohort["fixtures"]), "arm_ids": list(canonical_arms())}
        if not strict_equal(expected, derived):
            report["errors"].append({"error": "frozen plan expected workload differs from independently derived complete public workload", "derived": derived})
            report["pass"] = report["arithmetic_and_coverage_pass"] = False
        report.update(protocol_sha256=protocol_hash, cohort_sha256=cohort_hash,
                      source_manifest_sha256=source_hash, source_files_checked=source_files,
                      input_stream_sha256={name: sha256_file(getattr(args, name)) for name in ("attempts", "setups", "diagnostics", "controls", "prior_exclusions")})
        with args.output.open("x") as handle:
            json.dump(report, handle, sort_keys=True, indent=2)
            handle.write("\n")
        print(json.dumps({"pass": report["pass"], "output": str(args.output), "error_count": len(report["errors"])}))
        return 0 if report["pass"] else 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"pass": False, "configuration_error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
