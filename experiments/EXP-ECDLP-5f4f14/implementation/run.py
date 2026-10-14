#!/usr/bin/env python3
"""Stage-0 chord-slope fibres for EXP-ECDLP-5f4f14.

One curve over F_53. Not a walk and not an exponent claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


P = 53
A = 1
B_LIMIT = 26
MIN_PRIME_FACTOR = 17
NULL_DRAWS = 500
NULL_REDRAWS = 20
LABEL = "IDEA-20261006-76e571"
EXPERIMENT_ID = "EXP-ECDLP-5f4f14"
RUN_ID = "RUN-ECDLP-42444c"
SENTINEL = "sentinel"


def inv_pow(value: int) -> int:
    return pow(value % P, P - 2, P)


def inv_square(value: int) -> int:
    exponent = P - 2
    result = 1
    base = value % P
    while exponent:
        if exponent & 1:
            result = (result * base) % P
        base = (base * base) % P
        exponent >>= 1
    return result


def on_curve(point: tuple[int, int] | None, coefficient: int) -> bool:
    if point is None:
        return True
    x_value, y_value = point
    rhs = (x_value * x_value * x_value + A * x_value + coefficient) % P
    return (y_value * y_value) % P == rhs


def add(left: tuple[int, int] | None, right: tuple[int, int] | None, coefficient: int) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        slope = ((3 * x1 * x1 + A) % P * inv_pow((2 * y1) % P)) % P
    else:
        slope = ((y2 - y1) % P * inv_pow((x2 - x1) % P)) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)


def mul(scalar: int, point: tuple[int, int] | None, coefficient: int) -> tuple[int, int] | None:
    result = None
    current = point
    while scalar:
        if scalar & 1:
            result = add(result, current, coefficient)
        current = add(current, current, coefficient)
        scalar >>= 1
    return result


def affine_points(coefficient: int) -> list[tuple[int, int]]:
    root: dict[int, int] = {}
    for y_value in range(1, P):
        root.setdefault((y_value * y_value) % P, y_value)
    points: list[tuple[int, int]] = []
    for x_value in range(P):
        rhs = (x_value * x_value * x_value + A * x_value + coefficient) % P
        if rhs == 0:
            points.append((x_value, 0))
            continue
        y_value = root.get(rhs)
        if y_value is None:
            continue
        points.append((x_value, y_value))
        other = (-y_value) % P
        if other != y_value:
            points.append((x_value, other))
    points.sort()
    return points


def largest_prime_factor(value: int) -> int:
    factor = 1
    rest = value
    divisor = 2
    while divisor * divisor <= rest:
        if rest % divisor == 0:
            factor = divisor
            while rest % divisor == 0:
                rest //= divisor
        divisor += 1
    if rest > 1:
        factor = rest
    return factor


def singular(coefficient: int) -> bool:
    return (4 * A * A * A + 27 * coefficient * coefficient) % P == 0


def slope_pair(left: tuple[int, int], right: tuple[int, int]) -> tuple[str, int]:
    if left[0] == right[0]:
        return (SENTINEL, -1)
    difference = (right[0] - left[0]) % P
    rise = (right[1] - left[1]) % P
    first = (rise * inv_pow(difference)) % P
    second = (rise * inv_square(difference)) % P
    if first != second:
        raise RuntimeError("slope implementations disagree")
    return ("field", first)


def subgroup(generator: tuple[int, int], order: int, coefficient: int) -> list[tuple[int, int] | None]:
    points: list[tuple[int, int] | None] = [None]
    current = generator
    for _ in range(order - 1):
        points.append(current)
        current = add(current, generator, coefficient)
    return points


def first_generator(points: list[tuple[int, int]], order: int, coefficient: int) -> tuple[int, int] | None:
    for point in points:
        if point == (0, 0) and order != 2:
            pass
        if mul(order, point, coefficient) is None and point is not None:
            return point
    return None


def score(generator: tuple[int, int], order: int, coefficient: int) -> dict | None:
    points = subgroup(generator, order, coefficient)
    if points[-1] is None or add(points[-1], generator, coefficient) is not None:
        return None
    negative = (generator[0], (-generator[1]) % P)
    members = [point for point in points if point is not None and point != negative]
    member_set = set(members)
    domain = []
    slopes = []
    curve_ok = on_curve(generator, coefficient)
    for point in members:
        image = add(point, generator, coefficient)
        if image not in member_set:
            continue
        curve_ok = curve_ok and on_curve(point, coefficient) and on_curve(image, coefficient)
        domain.append(point)
        slopes.append(slope_pair(point, image))
    sentinel_ok = all(item != ("field", 0) or item[0] != SENTINEL for item in slopes)
    sentinel_ok = all(not (item[0] == SENTINEL and item[1] == 0) for item in slopes)
    image = set(slopes)
    return {
        "domain_size": len(members),
        "sample_size": len(domain),
        "image_size": len(image),
        "slopes": slopes,
        "domain": domain,
        "curve_ok": curve_ok,
        "sentinel_ok": sentinel_ok,
        "empty_image": len(image) == 0,
    }


def loss_ok(domain_size: int, image_size: int) -> bool:
    return 5 * (domain_size - image_size) >= domain_size


def split_count(scored: dict, generator: tuple[int, int], coefficient: int) -> int:
    grouped: dict[tuple[str, int], list[tuple[str, int]]] = {}
    for point, value in zip(scored["domain"], scored["slopes"]):
        translated = add(point, generator, coefficient)
        if translated not in set(scored["domain"]):
            grouped.setdefault(value, [])
            continue
        further = add(translated, generator, coefficient)
        grouped.setdefault(value, []).append(slope_pair(translated, further))
    return sum(1 for values in grouped.values() if len(set(values)) >= 2)


def split_ok(splitting: int, image_size: int) -> bool:
    return image_size > 0 and 2 * splitting >= image_size


def sha_index(slot: int, index: int, modulus: int) -> int:
    digest = hashlib.sha256(f"{LABEL}|null|{slot}|{index}".encode("utf-8")).digest()
    return int.from_bytes(digest, "big") % modulus


def null_usable(domain_size: int, image_size: int) -> bool:
    if domain_size <= 0 or image_size <= 0:
        return False
    order = list(range(domain_size))
    for index in range(domain_size - 1, 0, -1):
        swap = sha_index(10**9, index, index + 1)
        order[index], order[swap] = order[swap], order[index]
    good = 0
    for draw in range(NULL_DRAWS):
        assignment = None
        for attempt in range(NULL_REDRAWS + 1):
            slot = draw * (NULL_REDRAWS + 1) + attempt
            values = [sha_index(slot, index, image_size) for index in range(domain_size)]
            if len(set(values)) == image_size:
                assignment = values
                break
        if assignment is None:
            continue
        buckets: dict[int, list[int]] = {}
        for index, value in enumerate(assignment):
            buckets.setdefault(value, []).append(index)
        splitting = 0
        for indexes in buckets.values():
            images = {assignment[order[index]] for index in indexes}
            if len(images) >= 2:
                splitting += 1
        if 2 * splitting >= image_size:
            good += 1
    return 5 * good >= 4 * NULL_DRAWS


def select() -> dict | None:
    for coefficient in range(1, B_LIMIT + 1):
        if singular(coefficient):
            continue
        points = affine_points(coefficient)
        order_count = len(points) + 1
        if (P + 1 - order_count) % P == 0:
            continue
        prime_factor = largest_prime_factor(order_count)
        if prime_factor < MIN_PRIME_FACTOR:
            continue
        generator = first_generator(points, prime_factor, coefficient)
        if generator is None:
            continue
        return {
            "coefficient": coefficient,
            "point_count": order_count,
            "prime_factor": prime_factor,
            "generator": generator,
        }
    return None


def census() -> dict:
    chosen = select()
    scanner_ok = True
    scored = False
    loss = split = False
    side = "skipped"
    payload: dict = {
        "coefficient": None,
        "point_count": None,
        "prime_factor": None,
        "generator": None,
        "domain_size": None,
        "image_size": None,
        "loss_ok": False,
        "split_ok": False,
        "null_usable": False,
        "side": side,
    }
    if chosen is not None:
        primary = score(chosen["generator"], chosen["prime_factor"], chosen["coefficient"])
        scanner_ok = primary is not None and primary["curve_ok"] and primary["sentinel_ok"]
        if primary is not None and scanner_ok and not primary["empty_image"]:
            splitting = split_count(primary, chosen["generator"], chosen["coefficient"])
            loss = loss_ok(primary["domain_size"], primary["image_size"])
            split = split_ok(splitting, primary["image_size"])
            usable = null_usable(primary["domain_size"], primary["image_size"])
            scored = usable
            doubled = mul(2, chosen["generator"], chosen["coefficient"])
            if doubled is None:
                side = "skipped"
            else:
                secondary = score(doubled, chosen["prime_factor"], chosen["coefficient"])
                if secondary is None or secondary["empty_image"] or not secondary["curve_ok"]:
                    side = "fail"
                else:
                    side_split = split_count(secondary, doubled, chosen["coefficient"])
                    side_loss = loss_ok(secondary["domain_size"], secondary["image_size"])
                    side_pass = side_loss and split_ok(side_split, secondary["image_size"])
                    side = "pass" if side_pass else "fail"
            payload = {
                "coefficient": chosen["coefficient"],
                "point_count": chosen["point_count"],
                "prime_factor": chosen["prime_factor"],
                "generator": list(chosen["generator"]),
                "domain_size": primary["domain_size"],
                "image_size": primary["image_size"],
                "loss_ok": loss,
                "split_ok": split,
                "null_usable": usable,
                "side": side,
            }
    planted_ok = bool(scanner_ok and scored and chosen is not None)
    matrix_holds = planted_ok and loss and split
    return {
        "attack_claimed": False,
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "prime": P,
        "curve_a": A,
        "minimum_prime_factor": MIN_PRIME_FACTOR,
        "loss_numerator": 5,
        "split_numerator": 2,
        "null_draws": NULL_DRAWS,
        "null_redraws": NULL_REDRAWS,
        "seed_label": LABEL,
        "scanner_ok": scanner_ok,
        "scored": planted_ok,
        "planted_ok": planted_ok,
        "matrix_holds": matrix_holds,
        "beyond_matrix": planted_ok and not matrix_holds,
        **payload,
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    scanner_ok: {str(result['scanner_ok']).lower()}\n"
        f"    scored: {str(result['scored']).lower()}\n"
        f"    planted_ok: {str(result['planted_ok']).lower()}\n"
        f"    matrix_holds: {str(result['matrix_holds']).lower()}\n"
        f"    beyond_matrix: {str(result['beyond_matrix']).lower()}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    write_outputs(Path(args.run_dir), census())


if __name__ == "__main__":
    main()
