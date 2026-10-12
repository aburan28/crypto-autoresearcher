"""Independent replay of the archived one-edge 2-isogeny control."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def primes_below_256():
    return [n for n in range(7, 256) if n > 1 and all(n % d for d in range(2, n))]


def points(p, a2, a4, a6):
    return [(x, y) for x in range(p) for y in range(p)
            if (y * y - x**3 - a2 * x * x - a4 * x - a6) % p == 0]


def j_short(p, a2, a4, a6):
    # Translate x by -a2/3, then use the short-Weierstrass formula.
    inv3 = pow(3, -1, p)
    inv27 = pow(27, -1, p)
    a = (a4 - a2 * a2 * inv3) % p
    b = (a6 - a2 * a4 * inv3 + 2 * a2**3 * inv27) % p
    denominator = (4 * a**3 + 27 * b * b) % p
    assert denominator != 0
    return 1728 * 4 * a**3 * pow(denominator, -1, p) % p


def check(path):
    raw = json.loads((path / "raw-result.json").read_text())
    assert raw["experiment_id"] == "EXP-ECTD-cb23c5"
    assert raw["run_id"] == "RUN-ECTD-f96d04"
    selected = None
    expected_trace = []
    for p in primes_below_256():
        roots = [x for x in range(p) if (x**3 - 2 * x + 1) % p == 0]
        discriminant = (-5) % p
        eligible = discriminant != 0 and len(roots) == 1
        expected_trace.append({"p": p, "prime": True,
                               "discriminant_factor": discriminant,
                               "roots": roots, "eligible": eligible})
        if eligible:
            selected = (p, roots[0])
            break
    assert raw["selection_trace"] == expected_trace
    first_three_root = next(
        ({"p": q, "roots": roots, "rejected": True}
         for q in primes_below_256()
         for roots in [[x for x in range(q) if (x**3 - 2 * x + 1) % q == 0]]
         if len(roots) == 3), None
    )
    assert raw["three_root_rejection_control"] == first_three_root
    if selected is None:
        assert raw["selected_p"] is None and raw["kernel_root"] is None
        assert raw["reading_row"] == "negative_no_eligible_prime"
        assert raw["valid"] is True
        return
    p, r = selected
    assert raw["selected_p"] == p and raw["kernel_root"] == r
    assert raw["kernel"] == [r, 0]
    assert raw["double_T"] == "O"  # y=0 on a nonsingular odd-characteristic model.
    A = 3 * r % p
    B = (3 * r * r - 2) % p
    assert B != 0
    codomain = [(-2 * A) % p, (A * A - 4 * B) % p, 0]
    assert raw["quotient"]["translated_source"] == [A, B, 0]
    assert raw["quotient"]["source_shift"] == r
    assert raw["quotient"]["kernel"] == [["O"], [r, 0]]
    assert raw["quotient"]["degree"] == 2
    assert raw["quotient"]["codomain"] == codomain
    src_points = points(p, 0, -2, 1)
    translated_points = points(p, A, B, 0)
    dst_points = points(p, *codomain)
    assert len(src_points) == raw["source_order"] - 1
    assert len(dst_points) == raw["codomain_order"] - 1
    assert len(translated_points) == raw["translated_order"] - 1 == len(src_points)
    assert raw["source_j"] == j_short(p, 0, -2, 1)
    assert raw["codomain_j"] == j_short(p, *codomain)
    assert raw["translated_j"] == j_short(p, A, B, 0) == raw["source_j"]
    assert raw["orders_equal"] == (len(src_points) == len(dst_points))
    assert raw["j_different"] == (raw["source_j"] != raw["codomain_j"])
    assert raw["kernel_affine"] == [[r, 0]]
    assert len(raw["source_point_rows"]) == p
    assert len(raw["codomain_point_rows"]) == p
    assert len(raw["translated_point_rows"]) == p
    assert sorted((row["x"], y) for row in raw["source_point_rows"] for y in row["y"]) == src_points
    assert sorted((row["x"], y) for row in raw["codomain_point_rows"] for y in row["y"]) == dst_points
    assert sorted((row["x"], y) for row in raw["translated_point_rows"] for y in row["y"]) == translated_points
    assert len(raw["source_character_rows"]) == p
    assert sum(row["fiber_size"] for row in raw["source_character_rows"]) + 1 == len(src_points) + 1
    for row in raw["source_character_rows"]:
        x = row["x"]
        assert row["rhs"] == (x**3 - 2 * x + 1) % p
        assert row["fiber_size"] == sum(1 for sx, _ in src_points if sx == x)
    image = {"O"}
    for X in range(1, p):
        inv = pow(X, -1, p)
        u = (X + A + B * inv) % p
        lhs = (X**3 + A * X * X + B * X) * (1 - B * inv * inv) ** 2 % p
        rhs = (u**3 + codomain[0] * u * u + codomain[1] * u) % p
        assert lhs == rhs
    for x, y in src_points:
        X = (x - r) % p
        if X == 0:
            assert y == 0
            continue
        u = (X + A + B * pow(X, -1, p)) % p
        v = y * (1 - B * pow(X * X % p, -1, p)) % p
        assert (u, v) in dst_points
        image.add((u, v))
    assert raw["mapped_affine_points"] == len(src_points) - 1
    assert raw["map_image_size"] == len(image) == (len(src_points) + 1) // 2
    assert raw["valid"] is True
    assert all(raw["controls"].values())
    if len(src_points) != len(dst_points):
        reading = "order_contradiction_requires_review"
    elif raw["source_j"] == raw["codomain_j"]:
        reading = "negative_same_j"
    else:
        reading = "positive"
    assert raw["reading_row"] == reading


if __name__ == "__main__":
    check(Path(sys.argv[1]))
