#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from typing import Any


SELECTOR_NAME = "pair_sum_orbit_multiplicity"
SELECTOR_DEFINITION = "sort by descending x-orbit multiplicity, diagonal-first, index-distance, (x,y), original_index"


def order_from_suffix_points(points: list[Any]) -> list[int]:
    x_counts = Counter(None if point is None else int(point[0]) for point in points)
    size = max(1, int(len(points) ** 0.5))

    def key(index: int) -> tuple[int, int, int, int, int, int]:
        point = points[index]
        left, right = divmod(index, size)
        if point is None:
            return (0, 1, abs(left - right), 0, 0, index)
        return (
            -x_counts[int(point[0])],
            0 if left == right else 1,
            abs(left - right),
            int(point[0]),
            int(point[1]),
            index,
        )

    return sorted(range(len(points)), key=key)

