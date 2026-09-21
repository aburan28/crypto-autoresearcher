#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


SELECTOR_NAME = "pair_sum_x_ascending"
SELECTOR_DEFINITION = "sort source-only suffix pair sums by (infinity, x, y, original_index)"


def order_from_suffix_points(points: list[Any]) -> list[int]:
    def key(index: int) -> tuple[int, int, int, int]:
        point = points[index]
        if point is None:
            return (1, 0, 0, index)
        return (0, int(point[0]), int(point[1]), index)

    return sorted(range(len(points)), key=key)

