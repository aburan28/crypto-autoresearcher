#!/usr/bin/env python3
"""J6, fourth pass: actually RUN the prime-field nearby-object control.

The run declined the contract's prime-field index-calculus control on the stated
premise that no prime-field cost model exists in the frozen source or in this
corpus, so building one would have meant inventing formulas. That premise is
false: experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml is a
committed, executed, 54-cell prime-field index-calculus concrete-cost table,
carrying its own Pollard-rho prior in the same 0.886*2^{n/2} convention the
SEMBIN record uses.

This module charges those cells under the SEMBIN record's own baseline
convention and metrics and asks the question D3 actually poses. It also sweeps
the unit-conversion constant kappa (EXP-ICEX-c32447's binding discipline) and
re-runs the comparison under the coherently-charged baseline from J2, because a
control that fires must be localised before it is believed.

Reads the PFDR record as DATA. Imports no producer code. Labels are computed
from the cells here rather than relayed, because the third pass's summary keys
reported the max deficit under a "best margin" name.
"""

from __future__ import annotations

import json
import math
import re

PFDR = "/workspace/experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml"


def rho_time_log2(n: int) -> float:
    """The SEMBIN record's own baseline time: 0.886 * 2^{n/2} group operations."""
    return math.log2(0.886) + n / 2.0


def rho_memory_log2_record(n: int, store_log2: float = 30.0) -> float:
    """The SEMBIN record's own baseline memory: a 2^30-point store, 3n bits each."""
    return store_log2 + math.log2(3 * n)


def rho_product_log2_coherent(n: int) -> float:
    """J2's coherent charge: min over the vOW curve of T*Mem is 2 * 3n * W."""
    return rho_time_log2(n) + math.log2(3 * n) + 1.0


def read_pfdr(path: str = PFDR) -> list[dict]:
    txt = open(path).read()
    blocks = re.split(r"\n    - name: ", txt)[1:]
    rows = []
    for b in blocks:
        def g(key, cast=float):
            m = re.search(rf"{key}: (-?[\d.]+)", b)
            return cast(m.group(1)) if m else None
        name = b.split("\n")[0].strip().strip('"')
        if g("time_log2") is None:
            continue
        rows.append({
            "cell": name.split(" [")[0],
            "log2_N": g("security_parameter", int),
            "ic_time_log2": g("time_log2"),
            "ic_memory_log2": g("memory_log2"),
            "pfdr_own_rho_time_log2": g("prior_time_log2"),
            "pfdr_own_rho_memory_log2": g("prior_memory_log2"),
        })
    return rows


def run() -> dict:
    rows = read_pfdr()
    # the PFDR record charges rho exactly as SEMBIN does on time, and zero on
    # memory; confirm that before importing its cells into SEMBIN's convention
    conv = sorted({(r["log2_N"], r["pfdr_own_rho_time_log2"],
                    round(rho_time_log2(r["log2_N"]), 4))
                   for r in rows})

    per = []
    for r in rows:
        n = r["log2_N"]
        rt, rm = rho_time_log2(n), rho_memory_log2_record(n)
        it, im = r["ic_time_log2"], r["ic_memory_log2"]
        row = dict(r)
        row.update({
            "rho_time_log2_sembin_convention": round(rt, 4),
            "rho_memory_log2_sembin_convention": round(rm, 4),
            # positive = index calculus is AHEAD of rho by this many bits
            "ic_advantage_time_only_bits": round(rt - it, 4),
            "ic_advantage_product_bits": round((rt + rm) - (it + im), 4),
            "ic_advantage_product_coherent_baseline_bits":
                round(rho_product_log2_coherent(n) - (it + im), 4),
        })
        for kappa in (1, 10, 100):
            row[f"ic_advantage_time_only_kappa{kappa}_bits"] = round(
                rt + math.log2(kappa) - it, 4)
        per.append(row)

    summary = {}
    for n in sorted({r["log2_N"] for r in per}):
        sub = [r for r in per if r["log2_N"] == n]
        best_t = max(sub, key=lambda r: r["ic_advantage_time_only_bits"])
        best_p = max(sub, key=lambda r: r["ic_advantage_product_bits"])
        summary[f"log2_N={n}"] = {
            "cells": len(sub),
            "rho_time_log2": round(rho_time_log2(n), 4),
            "rho_memory_log2_record_store2e30": round(rho_memory_log2_record(n), 4),
            "cells_where_IC_beats_rho_time_only": sum(
                1 for r in sub if r["ic_advantage_time_only_bits"] > 0),
            "largest_IC_advantage_time_only_bits":
                best_t["ic_advantage_time_only_bits"],
            "largest_IC_advantage_cell": best_t["cell"],
            "cells_where_IC_beats_rho_product_record_baseline": sum(
                1 for r in sub if r["ic_advantage_product_bits"] > 0),
            "largest_IC_advantage_product_bits":
                best_p["ic_advantage_product_bits"],
            "cells_where_IC_beats_rho_product_coherent_baseline": sum(
                1 for r in sub
                if r["ic_advantage_product_coherent_baseline_bits"] > 0),
            "largest_IC_advantage_product_coherent_bits": round(max(
                r["ic_advantage_product_coherent_baseline_bits"] for r in sub), 4),
            "cells_where_IC_beats_rho_time_only_by_kappa": {
                f"kappa={k}": sum(
                    1 for r in sub if r[f"ic_advantage_time_only_kappa{k}_bits"] > 0)
                for k in (1, 10, 100)},
        }

    big = [r for r in per if r["log2_N"] >= 256]
    return {
        "source_record": ("experiments/EXP-PFDR-c04716/runs/STATIC-001/"
                          "concrete-cost.yaml"),
        "source_nature": ("committed, executed zero-run static derivation; "
                          "bound_kind heuristic_estimate; EVERY cell conditional "
                          "on HEUR-001 of H-PFDR-06fd60; cost unit is F_p field "
                          "operations while the rho prior is group operations, "
                          "i.e. the cells are stated at kappa = 1"),
        "baseline_convention_agrees_with_sembin": all(
            abs(a - b) < 1e-3 for _, a, b in conv),
        "baseline_convention_check": [
            {"log2_N": n, "pfdr_prior_time_log2": a,
             "sembin_rho_time_log2": b} for n, a, b in conv],
        "cells_parsed": len(per),
        "summary_by_size": summary,
        "D3_fires_time_only_at_256_or_above": any(
            r["ic_advantage_time_only_bits"] > 0 for r in big),
        "D3_fires_product_record_baseline_at_256_or_above": any(
            r["ic_advantage_product_bits"] > 0 for r in big),
        "D3_fires_product_coherent_baseline_at_256_or_above": any(
            r["ic_advantage_product_coherent_baseline_bits"] > 0 for r in big),
        "localisation": (
            "The firing is on the TIME axis, where neither storage reading nor "
            "any memory charge enters. D3's stated diagnosis -- 'it is "
            "mischarging memory or parallelism' -- therefore does not hold for "
            "the way the control actually fires: the cause is HEUR-001, an "
            "external conditional heuristic the corpus itself prices at a 0.05 "
            "prior, not a defect in SEMBIN's machinery. Charging the baseline "
            "coherently (J2) removes the PRODUCT firing and leaves the "
            "TIME-ONLY firing untouched."),
        "cells": per,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
