#!/usr/bin/env python3
"""J6/J2 joint pass: localise the prime-field control's verdict to the store size.

The prime-field nearby-object control the run declined is instantiable: the
corpus carries a committed 54-cell prime-field index-calculus concrete-cost
table at experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml, and it
charges its Pollard-rho prior in exactly the SEMBIN record's 0.886*2^{n/2}
convention, so the two are directly comparable.

Running it answers a question neither J2 nor J6 can answer alone. KN-OPEN-001
and KN-TECH-003 record the ordering for prime fields -- index calculus does NOT
beat rho -- so this is a KNOWN-FALSE object in the sense the review architecture
requires for a proves-too-much control. The sweep below asks at what baseline
store size the SEMBIN record's own memory convention inverts that known
ordering.

Reads the PFDR record as DATA; imports no producer code.
"""

from __future__ import annotations

import json
import math
import re

PFDR = "/workspace/experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml"
STORES = [0, 1, 10, 20, 30, 40, 60]


def rho_time_log2(n: int) -> float:
    return math.log2(0.886) + n / 2.0


def rho_memory_log2(n: int, store_log2: float) -> float:
    return store_log2 + math.log2(3 * n)


def read_pfdr(path: str = PFDR) -> list[dict]:
    txt = open(path).read()
    rows = []
    for b in re.split(r"\n    - name: ", txt)[1:]:
        def g(key, cast=float):
            m = re.search(rf"{key}: (-?[\d.]+)", b)
            return cast(m.group(1)) if m else None
        if g("time_log2") is None:
            continue
        rows.append({
            "cell": b.split("\n")[0].strip().strip('"').split(" [")[0],
            "log2_N": g("security_parameter", int),
            "ic_time_log2": g("time_log2"),
            "ic_memory_log2": g("memory_log2"),
            "pfdr_own_rho_time_log2": g("prior_time_log2"),
        })
    return rows


def run() -> dict:
    rows = read_pfdr()
    sizes = sorted({r["log2_N"] for r in rows})

    sweep = {}
    for s in STORES:
        block = {}
        for n in sizes:
            sub = [r for r in rows if r["log2_N"] == n]
            rt, rm = rho_time_log2(n), rho_memory_log2(n, s)
            # positive = index calculus AHEAD of rho under the product
            margins = [(rt + rm) - (r["ic_time_log2"] + r["ic_memory_log2"])
                       for r in sub]
            block[f"log2_N={n}"] = {
                "rho_memory_log2": round(rm, 4),
                "cells_where_prime_field_IC_wins_the_PRODUCT":
                    sum(1 for m in margins if m > 0),
                "best_product_margin_for_IC_bits": round(max(margins), 4),
                "ordering_known_from_KN_OPEN_001_is_inverted": max(margins) > 0,
            }
        sweep[f"store_log2={s}"] = block

    # the store size at which the ordering inverts, solved exactly: the product
    # margin is linear in store_log2 with unit slope
    invert = {}
    for n in sizes:
        sub = [r for r in rows if r["log2_N"] == n]
        rt = rho_time_log2(n)
        base = max((rt + math.log2(3 * n))
                   - (r["ic_time_log2"] + r["ic_memory_log2"]) for r in sub)
        invert[f"log2_N={n}"] = round(-base, 3)

    return {
        "sweep": sweep,
        "smallest_store_log2_at_which_the_prime_field_ordering_inverts": invert,
        "record_charges_store_log2": 30,
        "reading": (
            "The prime-field control passes at every store size the baseline "
            "actually needs at M = 1 and fails at the size the record charges. "
            "J2 and J6 are therefore the same defect: the 2^30-point store is a "
            "memory charge the baseline neither needs nor can use at the "
            "single-processor time the record also charges it."),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
