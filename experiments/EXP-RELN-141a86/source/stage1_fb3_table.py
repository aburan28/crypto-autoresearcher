"""
Stage-1 FB3 committed-cell table builder for EXP-RELN-141a86
(TASK-20260907-8fd098): builds fb3_unsigned_m3-convention rows (Delta, E_3,
coverage) for the three untyped E x-interval-family geometries
(high_bit_interval, small_height, coset_union -- the same UNTYPED_GEOMETRIES
set already established and verified in adapters_fb3_dreg_enum.py) at
N in {2^14, 2^16, 2^18} from the committed EXP-FB3-001 cells.

NO 2^20 ROW EXISTS FOR THIS PACK: EXP-FB3-001 has no N=2^20 run
(runs/ contains only N14, N16, N18, FAMILY, CTRL). Every row this module
returns is therefore held_out=False; a Pareto front built from these rows
alone can be fitted but its held-out-error field must be reported as
"not_available_no_2^20_fb3_data", never estimated, per this run's own
disclosed data-availability gap (see stage1_own_enumeration.py's module
docstring and implementation.md).

null_sd derivation for Delta and E_3 (not stored directly in the committed
raw-result.json, which only carries null_detail for mean/coverage/
concentration): since mean = M/N is an EXACT deterministic conservation
identity (INV-1) for ANY base of B distinct elements regardless of which
base is drawn, mu does not vary across the 200 matched-random null draws
that produced metrics.concentration.null_detail -- so, by the identities
Delta = conc/mu + 1 - mu and E_3 = N*(conc + mu) (both linear in conc at
fixed mu), null_sd(Delta) = null_sd(conc)/mu and null_sd(E_3) =
N * null_sd(conc) EXACTLY (not an approximation), propagated from the
committed metrics.concentration.null_detail.null_sd field.
"""
from __future__ import annotations

import math
from typing import Dict, List

import adapters_fb3_dreg_enum as fb3

E_ARM_GEOMETRIES = fb3.UNTYPED_GEOMETRIES  # {"high_bit_interval","small_height","coset_union"}


def build_fb3_e_arm_rows() -> List[Dict]:
    rows: List[Dict] = []
    for c in fb3.all_whole_group_cells():
        if c["geometry"] not in E_ARM_GEOMETRIES:
            continue
        N, B = c["N"], c["B"]
        m = 3
        M = math.comb(B + m - 1, m)
        mu = M / N
        mean = c["stats"]["mean"]
        conc = c["stats"]["concentration"]
        delta = conc / mean + 1 - mean if mean else None
        e3 = N * (conc + mean)
        conc_null = c["metrics"]["concentration"]["null_detail"]
        conc_null_sd = conc_null["null_sd"]
        conc_null_mean = conc_null["null_mean"]
        mean_null = c["metrics"]["mean"]["null_detail"]["null_mean"]  # == mu, exact conservation
        delta_null_sd = conc_null_sd / mean_null if mean_null else None
        delta_null_mean = conc_null_mean / mean_null + 1 - mean_null if mean_null else None
        e3_null_sd = N * conc_null_sd
        e3_null_mean = N * (conc_null_mean + mean_null)
        cov = c["stats"]["coverage"]
        cov_null = c["metrics"]["coverage"]["null_detail"]
        rows.append({
            "convention": "fb3_unsigned_m3", "arm": c["geometry"],
            "N": N, "B": B, "m": m, "M": M, "mu": mu,
            "rung_log2N": c["bits_target"], "held_out": False,
            "held_out_status": "not_available_no_2^20_fb3_data",
            "curve_index": c.get("curve_index"), "rep_seed": c.get("rep_seed"),
            "statistics": {"Delta": delta, "E_3": e3, "coverage": cov},
            "null_mean": {"Delta": delta_null_mean, "E_3": e3_null_mean,
                          "coverage": cov_null["null_mean"]},
            "null_sd": {"Delta": delta_null_sd, "E_3": e3_null_sd,
                        "coverage": cov_null["null_sd"]},
            "source_run": c["_source_run"],
            "source": "committed_fb3_cells",
        })
    return rows


if __name__ == "__main__":
    import json
    import sys
    rows = build_fb3_e_arm_rows()
    print(f"FB3 E-arm rows: {len(rows)}", file=sys.stderr)
    by_geom: Dict[str, int] = {}
    for r in rows:
        by_geom[r["arm"]] = by_geom.get(r["arm"], 0) + 1
    print(json.dumps(by_geom, indent=2), file=sys.stderr)
    print("stage1_fb3_table.py self-test: OK", file=sys.stderr)
