#!/usr/bin/env python3
"""Stage-0 square-bias worksheet for EXP-ECDLP-20ac31.

One frozen public point on y^2 = x^3 + 6x + 2. Not a discrete logarithm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


A = 6
B = 2
P_MIN = 23
P_MAX = 120
MIN_POINTS = 24
SHUFFLES = 300
RANK = 285
SEED_LABEL = "IDEA-20261006-30b5f6"
EXPERIMENT_ID = "EXP-ECDLP-20ac31"
RUN_ID = "RUN-ECDLP-08e0d9"


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def legendre_pow(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    return pow(residue, (prime - 1) // 2, prime)


def legendre_square(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    exponent = (prime - 1) // 2
    result = 1
    base = residue
    while exponent:
        if exponent & 1:
            result = (result * base) % prime
        base = (base * base) % prime
        exponent >>= 1
    return result


def inv(value: int, prime: int) -> int:
    return pow(value % prime, prime - 2, prime)


def on_curve(point: tuple[int, int], prime: int) -> bool:
    x_value, y_value = point
    rhs = (x_value * x_value * x_value + A * x_value + B) % prime
    return (y_value * y_value - rhs) % prime == 0


def ec_add(
    left: tuple[int, int] | None,
    right: tuple[int, int] | None,
    prime: int,
) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if left == right:
        slope = ((3 * x1 * x1 + A) % prime * inv(2 * y1, prime)) % prime
    else:
        slope = ((y2 - y1) % prime * inv((x2 - x1) % prime, prime)) % prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    return (x3, y3)


def nonzero_points(prime: int) -> list[tuple[int, int]]:
    root: dict[int, int] = {}
    for y_value in range(1, prime):
        root.setdefault((y_value * y_value) % prime, y_value)
    points: list[tuple[int, int]] = []
    for x_value in range(prime):
        rhs = (x_value * x_value * x_value + A * x_value + B) % prime
        y_value = root.get(rhs)
        if y_value is None or y_value == 0:
            continue
        points.append((x_value, y_value))
        other = (-y_value) % prime
        if other != y_value:
            points.append((x_value, other))
    points.sort()
    return points


def eligible(prime: int) -> tuple[bool, list[tuple[int, int]]]:
    if not is_prime(prime):
        return False, []
    if (4 * A * A * A + 27 * B * B) % prime == 0:
        return False, []
    points = nonzero_points(prime)
    return len(points) >= MIN_POINTS, points


def sample(points: list[tuple[int, int]], public: tuple[int, int], prime: int) -> list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]:
    negative = (public[0], (-public[1]) % prime)
    rows = []
    for point in points:
        if point == public or point == negative or point[0] == public[0]:
            continue
        total = ec_add(point, public, prime)
        difference = ec_add(point, negative, prime)
        if total is None or difference is None:
            continue
        rows.append((point, total, difference))
    return rows


def element(x_point: int, x_public: int, x_sum: int, x_difference: int, prime: int) -> int:
    return (x_sum * x_difference - x_point * x_public) % prime


def nonzero_square(value: int, prime: int) -> tuple[bool, bool]:
    left = legendre_pow(value, prime)
    right = legendre_square(value, prime)
    return left == right, value != 0 and left == 1


class Stream:
    def __init__(self, label: str) -> None:
        self.seed = hashlib.sha256(label.encode("utf-8")).digest()
        self.counter = 0
        self.buffer = b""

    def _byte(self) -> int:
        if not self.buffer:
            self.buffer = hashlib.sha256(self.seed + self.counter.to_bytes(8, "big")).digest()
            self.counter += 1
        value = self.buffer[0]
        self.buffer = self.buffer[1:]
        return value

    def below(self, bound: int) -> int:
        if bound <= 1:
            return 0
        limit = (1 << 32) // bound * bound
        while True:
            drawn = 0
            for _ in range(4):
                drawn = (drawn << 8) | self._byte()
            if drawn < limit:
                return drawn % bound


def shuffle_counts(
    rows: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]],
    public: tuple[int, int],
    prime: int,
) -> tuple[list[int], bool]:
    vertices: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for point, total, difference in rows:
        for vertex in (point, public, total, difference):
            if vertex not in seen:
                seen.add(vertex)
                vertices.append(vertex)
    vertices.sort()
    labels = [vertex[0] for vertex in vertices]
    index = {vertex: position for position, vertex in enumerate(vertices)}
    stream = Stream(SEED_LABEL)
    counts: list[int] = []
    agree = True
    for _ in range(SHUFFLES):
        order = labels[:]
        for cursor in range(len(order) - 1, 0, -1):
            swap = stream.below(cursor + 1)
            order[cursor], order[swap] = order[swap], order[cursor]
        squares = 0
        for point, total, difference in rows:
            value = element(
                order[index[point]],
                order[index[public]],
                order[index[total]],
                order[index[difference]],
                prime,
            )
            same, square = nonzero_square(value, prime)
            agree = agree and same
            squares += int(square)
        counts.append(squares)
    return counts, agree


def score_rows(
    rows: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]],
    public: tuple[int, int],
    prime: int,
) -> tuple[int, bool, bool]:
    squares = 0
    agree = True
    curve_ok = on_curve(public, prime)
    for point, total, difference in rows:
        curve_ok = curve_ok and on_curve(point, prime) and on_curve(total, prime) and on_curve(difference, prime)
        value = element(point[0], public[0], total[0], difference[0], prime)
        same, square = nonzero_square(value, prime)
        agree = agree and same
        squares += int(square)
    return squares, agree, curve_ok


def census() -> dict:
    selected_prime = None
    selected_points: list[tuple[int, int]] = []
    rejected_earlier = True
    for prime in range(P_MIN, P_MAX + 1):
        ok, points = eligible(prime)
        if ok:
            selected_prime = prime
            selected_points = points
            break
    premise = selected_prime is not None and len(selected_points) >= MIN_POINTS
    public = selected_points[0] if premise else None
    side = selected_points[1] if premise and len(selected_points) > 1 else None
    rows: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = []
    side_rows: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = []
    if premise and public is not None and selected_prime is not None:
        rows = sample(selected_points, public, selected_prime)
    if premise and side is not None and selected_prime is not None:
        side_rows = sample(selected_points, side, selected_prime)
    prime = selected_prime or 0
    squares, agree, curve_ok = (0, True, False)
    side_squares, side_agree, side_curve = (0, True, False)
    shuffle_abs: list[int] = []
    if premise and public is not None:
        squares, agree, curve_ok = score_rows(rows, public, prime)
        counts, shuffle_agree = shuffle_counts(rows, public, prime)
        agree = agree and shuffle_agree
        shuffle_abs = [abs(2 * count - len(rows)) for count in counts]
    if premise and side is not None:
        side_squares, side_agree, side_curve = score_rows(side_rows, side, prime)
        agree = agree and side_agree
    denominator = len(rows)
    abs_num = abs(2 * squares - denominator) if denominator else 0
    ordered = sorted(shuffle_abs)
    cutoff = ordered[RANK - 1] if len(ordered) == SHUFFLES else None
    exceeds = cutoff is not None and abs_num > cutoff
    planted_ok = bool(
        premise
        and rejected_earlier
        and public is not None
        and curve_ok
        and agree
        and denominator > 0
        and len(shuffle_abs) == SHUFFLES
        and cutoff is not None
        and RANK == 285
    )
    matrix_holds = planted_ok and exceeds
    return {
        "attack_claimed": False,
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "curve_a": A,
        "curve_b": B,
        "prime": prime,
        "public_point": list(public) if public is not None else None,
        "side_point": list(side) if side is not None else None,
        "sample_size": denominator,
        "nonzero_square_count": squares,
        "abs_numerator": abs_num,
        "shuffle_abs": shuffle_abs,
        "rank": RANK,
        "cutoff": cutoff,
        "exceeds": exceeds,
        "side_sample_size": len(side_rows),
        "side_nonzero_square_count": side_squares,
        "side_on_curve": side_curve,
        "success_consults_side": False,
        "seed_label": SEED_LABEL,
        "shuffles": SHUFFLES,
        "points_on_curve": curve_ok,
        "implementations_agree": agree,
        "premise_ok": premise,
        "planted_ok": planted_ok,
        "matrix_holds": matrix_holds,
        "beyond_matrix": planted_ok and not matrix_holds,
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
