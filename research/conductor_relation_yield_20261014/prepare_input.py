"""Prepare a frozen endpoint/arm input for the exact arity-3 collector.

Seeds are supplied only after implementation hashes are frozen. This tool
never draws a seed itself and never records a seed in its output manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_collector import Curve, add, certify_group, multiply, negative

HERE = Path(__file__).resolve().parent
PROTOCOL = "conductor-relation-yield/v1"
ARMS = ("native", "random", "u2-transport", "u2-native")


def model_for(plan, endpoint_id):
    for panel in plan["primary_panel"]:
        if endpoint_id in (f"{panel['id']}-crater", f"{panel['id']}-floor"):
            role = endpoint_id.rsplit("-", 1)[1]
            return panel, panel[role]
    if endpoint_id in ("P29-E2", "P29-E3"):
        panel = plan["primary_panel"][0]
        model = next(m for m in plan["secondary_same_conductor_panel"]["models"] if m["id"] == endpoint_id)
        return panel, model
    raise ValueError(f"unknown endpoint {endpoint_id}")


def root_mod_prime(value, prime):
    """Return one square root by Tonelli-Shanks, or None for a nonresidue."""
    value %= prime
    if value == 0:
        return 0
    if pow(value, (prime - 1) // 2, prime) != 1:
        return None
    if prime % 4 == 3:
        return pow(value, (prime + 1) // 4, prime)
    q = prime - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    nonresidue = 2
    while pow(nonresidue, (prime - 1) // 2, prime) != prime - 1:
        nonresidue += 1
    c = pow(nonresidue, q, prime)
    x = pow(value, (q + 1) // 2, prime)
    t = pow(value, q, prime)
    m = s
    while t != 1:
        i = 1
        power = (t * t) % prime
        while i < m and power != 1:
            power = (power * power) % prime
            i += 1
        if i == m:
            raise ArithmeticError("Tonelli-Shanks failed")
        b = pow(c, 1 << (m - i - 1), prime)
        x = (x * b) % prime
        t = (t * b * b) % prime
        c = (b * b) % prime
        m = i
    return x


def lift(x, curve):
    root = root_mod_prime((x**3 + curve.a * x + curve.b) % curve.p, curve.p)
    if root is None or root == 0:
        return None
    return x, min(root, curve.p - root)


def draw(seed, panel_id, endpoint_id, arm_id, kind, index, retry, modulus):
    domain = [PROTOCOL, panel_id, endpoint_id, arm_id, kind, index, retry]
    block = hashlib.sha256(seed + b"\0" + json.dumps(domain, separators=(",", ":")).encode()).digest()
    integer = int.from_bytes(block, "big")
    cap = (1 << 256) // modulus * modulus
    return None if integer >= cap else integer % modulus


def next_draw(seed, panel_id, endpoint_id, arm_id, kind, index, modulus, start=0):
    retry = start
    while True:
        value = draw(seed, panel_id, endpoint_id, arm_id, kind, index, retry, modulus)
        if value is not None:
            return value, retry
        retry += 1


def native_base(curve, count):
    points = []
    for x in range(curve.p):
        point = lift(x, curve)
        if point is not None:
            points.extend((point, negative(point, curve)))
            if len(points) == 2 * count:
                return points
    raise ValueError("insufficient liftable abscissae")


def random_base(curve, count, seed, panel_id, endpoint_id):
    points = []
    seen = set()
    for index in range(count):
        retry = 0
        while True:
            x, retry = next_draw(seed, panel_id, endpoint_id, "random", "base-x", index, curve.p, retry)
            point = lift(x, curve)
            if x not in seen and point is not None:
                seen.add(x)
                points.extend((point, negative(point, curve)))
                break
            retry += 1
    return points


def transform(curve, point):
    if point is None:
        return None
    return (4 * point[0]) % curve.p, (8 * point[1]) % curve.p


def transformed_curve(curve):
    return Curve(curve.p, (16 * curve.a) % curve.p, (64 * curve.b) % curve.p, curve.r)


def prepare(plan, endpoint_id, arm, target_seed, k_seed, target_count):
    panel, model = model_for(plan, endpoint_id)
    panel_id = panel["id"]
    curve = Curve(panel["p"], model["a"], model["b"], panel["r"])
    generator = model["gx"], model["gy"]
    certify_group(curve, generator)
    k, _ = next_draw(k_seed, panel_id, endpoint_id, "common", "k", 0, curve.r - 1)
    k += 1
    q = multiply(k, generator, curve)
    if q is None:
        raise ValueError("Q is identity")
    targets = []
    seen = set()
    for index in range(target_count):
        retry = 0
        while True:
            alpha, _ = next_draw(target_seed, panel_id, endpoint_id, "common", "alpha", index, curve.r, retry)
            beta, _ = next_draw(target_seed, panel_id, endpoint_id, "common", "beta", index, curve.r - 1, retry)
            beta += 1
            point = add(multiply(alpha, generator, curve), multiply(beta, q, curve), curve)
            if point is not None and point not in seen:
                seen.add(point)
                targets.append((alpha, beta, point))
                break
            retry += 1
    count = panel["base_abscissae"]
    if arm == "native":
        base = native_base(curve, count)
        result_curve, result_generator, result_q = curve, generator, q
    elif arm == "random":
        base = random_base(curve, count, target_seed, panel_id, endpoint_id)
        result_curve, result_generator, result_q = curve, generator, q
    elif arm == "u2-transport":
        base = [transform(curve, point) for point in native_base(curve, count)]
        result_curve = transformed_curve(curve)
        result_generator, result_q = transform(curve, generator), transform(curve, q)
        targets = [(alpha, beta, transform(curve, point)) for alpha, beta, point in targets]
    elif arm == "u2-native":
        result_curve = transformed_curve(curve)
        base = native_base(result_curve, count)
        result_generator, result_q = transform(curve, generator), transform(curve, q)
        targets = [(alpha, beta, transform(curve, point)) for alpha, beta, point in targets]
    else:
        raise ValueError(f"unknown arm {arm}")
    if len({point[0] for point in base}) != count:
        raise AssertionError("base has duplicate x-orbits")
    if len({point for _, _, point in targets}) != target_count:
        raise AssertionError("targets not distinct")
    rows = [f"curve {result_curve.p} {result_curve.a} {result_curve.b} {result_curve.r} {len(base)} {len(targets)}"]
    rows.extend(f"base {index} {x} {y}" for index, (x, y) in enumerate(base))
    rows.extend(f"target {index} {alpha} {beta} {point[0]} {point[1]}" for index, (alpha, beta, point) in enumerate(targets))
    payload = ("\n".join(rows) + "\n").encode()
    metadata = {
        "schema": "arity3-prepared-input/v1", "endpoint": endpoint_id, "arm": arm,
        "panel": panel_id, "target_count": target_count, "base_abscissae": count,
        "protocol_conformant_target_count": target_count == plan["target_generation"]["targets_per_endpoint"],
        "generator": result_generator, "Q": result_q,
        "target_seed_sha256": hashlib.sha256(target_seed).hexdigest(),
        "k_seed_sha256": hashlib.sha256(k_seed).hexdigest(),
        "input_sha256": hashlib.sha256(payload).hexdigest(),
        "base_sha256": hashlib.sha256(json.dumps(base, separators=(",", ":")).encode()).hexdigest(),
        "target_vector_sha256": hashlib.sha256(json.dumps(targets, separators=(",", ":")).encode()).hexdigest(),
        "source_spec_sha256": (
            plan["secondary_same_conductor_panel"]["source_spec_sha256"]
            if endpoint_id in ("P29-E2", "P29-E3") else panel["source_spec_sha256"]
        ),
        "plan_sha256": hashlib.sha256((HERE / "plan.json").read_bytes()).hexdigest(),
        "preparer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "group_order_certificate": "exact trial-division primality of p and r; rG=O; r in Hasse interval; 2r exceeds Hasse upper bound",
        "limits": "preparation receipt only; conductor and isogeny claims require independent source verification",
    }
    return payload, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--arm", required=True, choices=ARMS)
    parser.add_argument("--target-seed-file", type=Path, required=True)
    parser.add_argument("--k-seed-file", type=Path, required=True)
    parser.add_argument("--targets", type=int, default=32768)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target_seed = bytes.fromhex(args.target_seed_file.read_text().strip())
    k_seed = bytes.fromhex(args.k_seed_file.read_text().strip())
    if len(target_seed) != 32 or len(k_seed) != 32 or target_seed == k_seed or args.targets < 1:
        parser.error("two distinct 256-bit seeds and a positive target count are required")
    plan = json.loads((HERE / "plan.json").read_text())
    payload, metadata = prepare(plan, args.endpoint, args.arm, target_seed, k_seed, args.targets)
    with args.output.open("xb") as output:
        output.write(payload)
    with args.output.with_suffix(args.output.suffix + ".manifest.json").open("x") as output:
        json.dump(metadata, output, indent=2, sort_keys=True)
        output.write("\n")
    print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()
