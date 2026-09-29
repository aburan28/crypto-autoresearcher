#!/usr/bin/env python3
"""Recompute the WESOVOW vOW charging law without touching frozen inputs.

This file is deliberately standalone.  It reads the committed raw result as
data, performs RG-1 before constructing any corrected table, and writes only
the caller-selected output path after all controls pass.  The two anchors are
kept separate throughout:

* ``fitted_opt`` uses ``per_field[*].optimal.log2T`` and ``log2M`` from the
  committed RUN-WESOVOW-001 raw result;
* ``PAPER_PAIRS`` uses the committed literals in cost_model.py lines 60--65.

All quantities are base-2 logarithms.  The committed/null law is retained only
for RG-1 and RG-3; the reported table uses the corrected law.
"""

import argparse
import json
import math
from pathlib import Path


FIELD_SIZES = (256, 384, 512, 576, 768)
MEMORY_BUDGETS = (30, 40, 50, 60, 70, 80)
OVERHEAD_C = (0.0, 0.5, 1.0, 2.0)
RG1_TOLERANCE = 1e-9
CONTROL_TOLERANCE = 1e-12

# Source: experiments/EXP-WESOVOW-001/cost_model.py:60-65.
PAPER_PAIRS = {
    256: (106.5, 92.5),
    384: (157.5, 138.6),
    512: (204.2, 181.3),
    576: (230.9, 206.0),
    768: (302.4, 272.2),
}


def committed_law(log2_t_full, log2_m, log2_w, overhead_c, log2p):
    """The frozen/null law, in log2 units.

    Source formula: experiments/EXP-WESOVOW-001/cost_model.py:270.
    """

    overhead_bits = overhead_c * math.sqrt(log2p)
    return log2_t_full - 0.5 * min(log2_w, log2_m) + overhead_bits


def corrected_law(log2_t_full, log2_m, log2_w, overhead_c, log2p):
    """The ratio-anchored law, in log2 units.

    The memory penalty is zero at w=M and grows as memory is reduced:
    T(w) = T_full + c*sqrt(log2p) + 0.5*max(0, log2M-log2w).
    """

    overhead_bits = overhead_c * math.sqrt(log2p)
    memory_penalty = 0.5 * max(0.0, log2_m - log2_w)
    return log2_t_full + overhead_bits + memory_penalty


def anchor_records(raw):
    """Return immutable-input anchors in a form used by both controls/table."""

    fitted = {}
    per_field = raw.get("per_field")
    if not isinstance(per_field, dict):
        raise ValueError("raw result lacks per_field mapping")
    for log2p in FIELD_SIZES:
        field = per_field.get(f"log2p={log2p}")
        if not isinstance(field, dict):
            raise ValueError(f"raw result lacks log2p={log2p}")
        optimal = field.get("optimal")
        if not isinstance(optimal, dict):
            raise ValueError(f"raw result lacks optimal anchor for log2p={log2p}")
        fitted[log2p] = (
            float(optimal["log2T"]),
            float(optimal["log2M"]),
        )
    return {
        "fitted_opt": fitted,
        "PAPER_PAIRS": {
            log2p: (float(pair[0]), float(pair[1]))
            for log2p, pair in PAPER_PAIRS.items()
        },
    }


def rg1_reproduction(raw):
    """Reproduce all committed van_oorschot_wiener cells before table output."""

    per_field = raw.get("per_field")
    if not isinstance(per_field, dict):
        raise ValueError("RG-1: raw result lacks per_field mapping")
    checked = 0
    mismatches = []
    max_abs_diff = 0.0
    for log2p in FIELD_SIZES:
        field_key = f"log2p={log2p}"
        field = per_field.get(field_key)
        if not isinstance(field, dict):
            raise ValueError(f"RG-1: raw result lacks {field_key}")
        optimal = field.get("optimal")
        committed_rows = field.get("van_oorschot_wiener")
        if not isinstance(optimal, dict) or not isinstance(committed_rows, dict):
            raise ValueError(f"RG-1: incomplete committed cells for {field_key}")
        log2_t_full = float(optimal["log2T"])
        log2_m = float(optimal["log2M"])
        for log2_w in MEMORY_BUDGETS:
            row = committed_rows.get(f"w=2^{log2_w}")
            if not isinstance(row, dict):
                raise ValueError(f"RG-1: missing w=2^{log2_w} for {field_key}")
            for overhead_c in OVERHEAD_C:
                cell_key = f"c={overhead_c}"
                cell = row.get(cell_key)
                if not isinstance(cell, dict) or "log2T_w" not in cell:
                    raise ValueError(f"RG-1: missing {field_key}, {cell_key}")
                expected = float(cell["log2T_w"])
                actual = committed_law(
                    log2_t_full, log2_m, log2_w, overhead_c, log2p
                )
                diff = abs(actual - expected)
                checked += 1
                max_abs_diff = max(max_abs_diff, diff)
                if diff > RG1_TOLERANCE:
                    mismatches.append(
                        {
                            "log2p": log2p,
                            "log2w": log2_w,
                            "overhead_c": overhead_c,
                            "raw": expected,
                            "recomputed": actual,
                            "abs_diff": diff,
                        }
                    )
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "checked_cells": checked,
        "tolerance": RG1_TOLERANCE,
        "max_abs_diff": max_abs_diff,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def rg2_cap_control(anchors):
    """Evaluate both laws at log2(w)=log2(M), for every field and anchor."""

    rows = []
    corrected_cap_ok = True
    committed_not_cap = True
    for anchor_name, values in anchors.items():
        for log2p in FIELD_SIZES:
            log2_t_full, log2_m = values[log2p]
            committed = committed_law(
                log2_t_full, log2_m, log2_m, 0.0, log2p
            )
            corrected = corrected_law(
                log2_t_full, log2_m, log2_m, 0.0, log2p
            )
            corrected_delta = corrected - log2_t_full
            committed_delta = committed - log2_t_full
            corrected_cap_ok &= abs(corrected_delta) <= CONTROL_TOLERANCE
            committed_not_cap &= abs(committed_delta) > CONTROL_TOLERANCE
            rows.append(
                {
                    "anchor": anchor_name,
                    "log2p": log2p,
                    "log2w": log2_m,
                    "committed_log2T_w": committed,
                    "corrected_log2T_w": corrected,
                    "log2T_full": log2_t_full,
                    "committed_minus_full": committed_delta,
                    "corrected_minus_full": corrected_delta,
                }
            )
    return {
        "status": "PASS" if corrected_cap_ok and committed_not_cap else "FAIL",
        "checked_rows": len(rows),
        "corrected_cap_identity": corrected_cap_ok,
        "committed_null_detected_as_non_cap": committed_not_cap,
        "rows": rows,
        "failure_condition": (
            "FAIL if corrected law differs from T_full at any exact w=M row, "
            "or if the committed law is not distinguishable from T_full at any "
            "of those rows."
        ),
    }


def rg3_null_discrimination(anchors):
    """Swap the corrected procedure to the committed law at a low-memory probe."""

    probe_log2w = MEMORY_BUDGETS[0]
    rows = []
    discriminating = True
    for anchor_name, values in anchors.items():
        for log2p in FIELD_SIZES:
            log2_t_full, log2_m = values[log2p]
            committed = committed_law(
                log2_t_full, log2_m, probe_log2w, 0.0, log2p
            )
            corrected = corrected_law(
                log2_t_full, log2_m, probe_log2w, 0.0, log2p
            )
            delta = corrected - committed
            discriminating &= abs(delta) > CONTROL_TOLERANCE
            rows.append(
                {
                    "anchor": anchor_name,
                    "log2p": log2p,
                    "log2w": probe_log2w,
                    "committed_log2T_w": committed,
                    "corrected_log2T_w": corrected,
                    "corrected_minus_committed": delta,
                    "distinguishes_null": abs(delta) > CONTROL_TOLERANCE,
                }
            )
    return {
        "status": "PASS" if discriminating else "FAIL",
        "probe_log2w": probe_log2w,
        "checked_rows": len(rows),
        "all_rows_discriminate": discriminating,
        "rows": rows,
        "failure_condition": (
            "FAIL and discard the output if any corrected/committed pair at the "
            "probe has absolute difference <= 1e-12."
        ),
    }


def crossover(log2_t_full, log2_m, log2p, overhead_c):
    """Uncapped crossing in log2 memory under the corrected law."""

    overhead_bits = overhead_c * math.sqrt(log2p)
    return log2_m - 2.0 * (
        (log2p / 2.0) - log2_t_full - overhead_bits
    )


def build_table(anchors, rg1, rg2, rg3):
    """Build the two-anchor, 5-by-6-by-4 corrected comparison table."""

    rows = []
    anchor_sources = {
        "fitted_opt": (
            "experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:"
            "per_field[log2p=*].optimal.log2T,optimal.log2M"
        ),
        "PAPER_PAIRS": (
            "experiments/EXP-WESOVOW-001/cost_model.py:60-65"
        ),
    }
    for anchor_name, values in anchors.items():
        for log2p in FIELD_SIZES:
            log2_t_full, log2_m = values[log2p]
            baseline = log2p / 2.0
            for log2_w in MEMORY_BUDGETS:
                for overhead_c in OVERHEAD_C:
                    overhead_bits = overhead_c * math.sqrt(log2p)
                    corrected = corrected_law(
                        log2_t_full, log2_m, log2_w, overhead_c, log2p
                    )
                    committed_null = committed_law(
                        log2_t_full, log2_m, log2_w, overhead_c, log2p
                    )
                    speedup = baseline - corrected
                    rows.append(
                        {
                            "anchor": anchor_name,
                            "anchor_source": anchor_sources[anchor_name],
                            "field_size_log2p": log2p,
                            "log2w": log2_w,
                            "overhead_c": overhead_c,
                            "log2T_full_anchor": log2_t_full,
                            "log2M_anchor": log2_m,
                            "log2T_DG": baseline,
                            "overhead_bits": overhead_bits,
                            "log2T_w_corrected": corrected,
                            "log2speedup_vs_DG_corrected": speedup,
                            "beats_DG_corrected": speedup > 0.0,
                            "log2w_star_corrected": crossover(
                                log2_t_full, log2_m, log2p, overhead_c
                            ),
                            "corrected_crossover_at_or_below_M": crossover(
                                log2_t_full, log2_m, log2p, overhead_c
                            ) <= log2_m,
                            "log2T_w_committed_null": committed_null,
                        }
                    )
    expected_rows = len(anchors) * len(FIELD_SIZES) * len(MEMORY_BUDGETS) * len(
        OVERHEAD_C
    )
    if len(rows) != expected_rows:
        raise AssertionError(f"table row count {len(rows)} != {expected_rows}")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    raw = json.loads(args.raw.read_text())

    # RG-1 is deliberately first.  No output table is opened before it passes.
    rg1 = rg1_reproduction(raw)
    print(
        "RG-1 "
        f"{rg1['status']}: checked={rg1['checked_cells']} "
        f"max_abs_diff={rg1['max_abs_diff']:.17g} "
        f"tolerance={rg1['tolerance']:.17g} "
        f"mismatches={rg1['mismatch_count']}"
    )
    if rg1["status"] != "PASS":
        print("RG-1 failed; corrected table was not written.")
        return 2

    anchors = anchor_records(raw)
    rg2 = rg2_cap_control(anchors)
    print(
        "RG-2 "
        f"{rg2['status']}: checked_rows={rg2['checked_rows']} "
        f"corrected_cap_identity={rg2['corrected_cap_identity']} "
        f"committed_null_detected_as_non_cap="
        f"{rg2['committed_null_detected_as_non_cap']}"
    )
    for row in rg2["rows"]:
        print(
            "RG-2 row "
            f"anchor={row['anchor']} log2p={row['log2p']} "
            f"log2M={row['log2w']:.17g} "
            f"committed={row['committed_log2T_w']:.17g} "
            f"corrected={row['corrected_log2T_w']:.17g} "
            f"full={row['log2T_full']:.17g}"
        )

    rg3 = rg3_null_discrimination(anchors)
    print(
        "RG-3 "
        f"{rg3['status']}: probe_log2w={rg3['probe_log2w']} "
        f"checked_rows={rg3['checked_rows']} "
        f"all_rows_discriminate={rg3['all_rows_discriminate']}"
    )
    for row in rg3["rows"]:
        print(
            "RG-3 row "
            f"anchor={row['anchor']} log2p={row['log2p']} "
            f"committed={row['committed_log2T_w']:.17g} "
            f"corrected={row['corrected_log2T_w']:.17g} "
            f"delta={row['corrected_minus_committed']:.17g}"
        )

    if rg2["status"] != "PASS" or rg3["status"] != "PASS":
        print("RG-2 or RG-3 failed; corrected table was not written.")
        return 3

    rows = build_table(anchors, rg1, rg2, rg3)
    result = {
        "schema": "crypto-autoresearcher.wesovow.corrected_charging.v1",
        "task_id": "TASK-20260824-dd5b5c",
        "experiment_id": "EXP-WESOVOW-001",
        "run_id": "RUN-WESOVOW-001",
        "units": {
            "time": "log2(F_{p^2}-operations)",
            "memory": "log2(table entries)",
        },
        "inputs": {
            "raw_result": str(args.raw),
            "field_sizes_log2p": list(FIELD_SIZES),
            "memory_budgets_log2w": list(MEMORY_BUDGETS),
            "overhead_c": list(OVERHEAD_C),
        },
        "laws": {
            "committed_null": (
                "log2T_full - 0.5*min(log2w, log2M) + c*sqrt(log2p)"
            ),
            "corrected": (
                "log2T_full + c*sqrt(log2p) + "
                "0.5*max(0, log2M-log2w)"
            ),
            "baseline": "log2T_DG = log2p/2",
        },
        "controls": {"RG-1": rg1, "RG-2": rg2, "RG-3": rg3},
        "anchor_sources": {
            "fitted_opt": (
                "experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/"
                "raw-result.json:per_field[log2p=*].optimal"
            ),
            "PAPER_PAIRS": "experiments/EXP-WESOVOW-001/cost_model.py:60-65",
        },
        "row_count": len(rows),
        "rows": rows,
        "citation_boundary": (
            "P=512 crossover value and w=2^80 sign are NOT citation-eligible; "
            "this task does not lift that prohibition."
        ),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"WROTE {args.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
