"""Product-route integer check for EXP-BINSTD-fdd2d9.

Uses multiplication and integer division. Must not import route_difference.
No encoding. No Magma/Sage/AUXIN/Bedrock.
"""
from __future__ import annotations

N_LIST = (17, 19, 23)
ELL_LO = 3
ELL_HI = 4
CATALOG = 12
CELLS = 6
BOUND_HUNDREDTHS = 70
HALF_HUNDREDTHS = 50
DISTINCT_FLOOR = 3
HOUR_CAP = 6


def compute() -> dict:
    n0, n1, n2 = N_LIST
    n_sum = n0 + n1 + n2
    n_product = n0 * n1 * n2
    span = n2 - n0
    gap_ab = n1 - n0
    gap_bc = n2 - n1
    gap_product = gap_ab * gap_bc
    ell_product = ELL_LO * ELL_HI
    slots = CELLS * CATALOG
    slot_quot = slots // CATALOG
    hundredths_excess = BOUND_HUNDREDTHS - HALF_HUNDREDTHS
    catalog_quot = ell_product // DISTINCT_FLOOR
    excess_product = hundredths_excess * catalog_quot
    cross_two_thirds = 7 * 3 - 10 * 2
    cross_three_fifths = 7 * 5 - 10 * 3
    hour_ok = slot_quot == HOUR_CAP
    return {
        "route": "product",
        "n_list": list(N_LIST),
        "n_sum": n_sum,
        "n_product": n_product,
        "gap_ab": gap_ab,
        "gap_bc": gap_bc,
        "gap_product": gap_product,
        "span": span,
        "ell_lo": ELL_LO,
        "ell_hi": ELL_HI,
        "ell_product": ell_product,
        "cells": CELLS,
        "catalog": CATALOG,
        "slots": slots,
        "hour_cap": HOUR_CAP,
        "slot_quot": slot_quot,
        "hour_ok": hour_ok,
        "bound_hundredths": BOUND_HUNDREDTHS,
        "half_hundredths": HALF_HUNDREDTHS,
        "hundredths_excess": hundredths_excess,
        "distinct_floor": DISTINCT_FLOOR,
        "catalog_quot": catalog_quot,
        "excess_product": excess_product,
        "cross_two_thirds": cross_two_thirds,
        "cross_three_fifths": cross_three_fifths,
        "arithmetic": "multiplication_division",
        "encoding_run": False,
    }
