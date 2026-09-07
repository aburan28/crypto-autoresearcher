#!/usr/bin/env python3
"""
Read-only re-analysis of RUN-MONO-cb905d-1's Part B 100-cell panel.

Partitions cells into CLEAN (CM side genuinely ordinary) and CONTAMINATED
(CM side supersingular, N_cm == p_cm + 1), per TASK-20260904-bf0b03 /
CORR-20260904-30a8ce / DEC-20260904-d79f75 next_action (2).

Does NOT modify the archived run record. Recomputes A_cm, B_cm
deterministically from the archived (p_cm, cm_variant) using the exact,
unmodified construct_cm_j0/construct_cm_j1728 code from
experiments/EXP-MONO-64aaa4/implementation/run_experiment.py (these
functions are pure functions of (p, DOMAIN) with no run-specific seed
input -- DOMAIN is a fixed module constant, so re-deriving them here
reproduces the exact curve the archived run used, only for the purpose of
recovering (A,B) which was not itself archived in the panel cells).
"""
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/Volumes/SSD990/crypto-autoresearcher")
IMPL_PATH = REPO_ROOT / "experiments/EXP-MONO-64aaa4/implementation/run_experiment.py"
RAW_RESULT_PATH = REPO_ROOT / "experiments/EXP-MONO-cb905d/runs/RUN-MONO-cb905d-1/raw-result.json"
OUT_DIR = REPO_ROOT / "experiments/EXP-MONO-64aaa4/analysis/panel-partition-20260904"

# Load the archived implementation module by path (read-only import; we do
# not modify it and do not re-run its Part B sampling).
spec = importlib.util.spec_from_file_location("m64_impl", IMPL_PATH)
m64 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m64)


def load_cells():
    with open(RAW_RESULT_PATH) as f:
        d = json.load(f)
    return d["part_b"]["cells"]


def recompute_cm_curve(p_cm, cm_variant):
    """Recompute (A,B,N,tau) for the CM curve at p_cm using the archived,
    unmodified constructor for that variant. Deterministic, no seed
    dependence beyond (DOMAIN, p, variant label) which are fixed constants
    in the implementation module."""
    if cm_variant == "j0":
        rec = m64.construct_cm_j0(p_cm)
    elif cm_variant == "j1728":
        rec = m64.construct_cm_j1728(p_cm)
    else:
        raise ValueError(f"unknown cm_variant {cm_variant!r}")
    if rec is None:
        raise RuntimeError(f"construct_cm_{cm_variant} failed for p={p_cm}")
    return rec


def main():
    cells = load_cells()
    assert len(cells) == 100, f"expected 100 cells, got {len(cells)}"

    clean = []
    contaminated = []
    contaminated_curves = {}  # (p_cm, A, B, N) -> count of cells referencing it
    mismatches = []

    for idx, c in enumerate(cells):
        p_cm = c["p_cm"]
        N = c["N"]
        cm_variant = c["cm_variant"]

        # Direct numeric supersingularity check using ONLY the archived
        # (p_cm, N) fields, per step 2 of the task -- no curve construction
        # needed for this check itself.
        is_ss_by_archived_fields = (N == p_cm + 1)

        # Independent recomputation of the actual (A,B,N) the CM
        # constructor would have produced for this (p_cm, cm_variant), to
        # (a) cross-check the archived N field against a from-scratch
        # rebuild, and (b) recover A,B for the contaminated-curve list.
        rec = recompute_cm_curve(p_cm, cm_variant)
        if rec["N"] != N:
            mismatches.append({
                "cell_index": idx, "p_cm": p_cm, "cm_variant": cm_variant,
                "archived_N": N, "rebuilt_N": rec["N"],
            })
        is_ss_rebuilt = (rec["N"] == p_cm + 1)

        cell_out = dict(c)
        cell_out["cell_index"] = idx
        cell_out["is_supersingular_archived_fields"] = is_ss_by_archived_fields
        cell_out["is_supersingular_rebuilt"] = is_ss_rebuilt
        cell_out["A_cm_rebuilt"] = rec["A"]
        cell_out["B_cm_rebuilt"] = rec["B"]
        cell_out["N_cm_rebuilt"] = rec["N"]

        if is_ss_by_archived_fields:
            contaminated.append(cell_out)
            key = (p_cm, rec["A"], rec["B"], rec["N"])
            contaminated_curves[key] = contaminated_curves.get(key, 0) + 1
        else:
            clean.append(cell_out)

    return cells, clean, contaminated, contaminated_curves, mismatches


if __name__ == "__main__":
    cells, clean, contaminated, contaminated_curves, mismatches = main()
    print(f"total cells: {len(cells)}")
    print(f"clean: {len(clean)}")
    print(f"contaminated: {len(contaminated)}")
    print(f"distinct contaminated curves: {len(contaminated_curves)}")
    print(f"N-field rebuild mismatches: {len(mismatches)}")
    if mismatches:
        print(json.dumps(mismatches, indent=2))

    # Save partition and distinct curve list for the report script to reuse.
    with open(OUT_DIR / "clean_cells.json", "w") as f:
        json.dump(clean, f, indent=2)
    with open(OUT_DIR / "contaminated_cells.json", "w") as f:
        json.dump(contaminated, f, indent=2)
    with open(OUT_DIR / "distinct_contaminated_curves.json", "w") as f:
        json.dump(
            [{"p": k[0], "A": k[1], "B": k[2], "N": k[3], "cell_count": v}
             for k, v in sorted(contaminated_curves.items())],
            f, indent=2,
        )
