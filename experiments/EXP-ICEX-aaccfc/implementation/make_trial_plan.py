"""Write trial-plan-v2.json for EXP-ICEX-aaccfc protocol v3 (file name kept) (deterministic, no
timestamps): 6 fixtures x 5 cells (primary, null_randfb, stage_cost_m6,
stage_cost_m8, rho) = 30 cells, one run, one worker.

  python3 make_trial_plan.py [--out trial-plan-v2.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
import hostinfo  # noqa: E402
from verify import VCurve  # noqa: E402

CELL_KINDS = ("primary", "null_randfb", "stage_cost_m6", "stage_cost_m8", "rho")


def fixture_derived(fx) -> dict:
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    out = {}
    for m in (5, 6, 8):
        B = common.fb_bound(fx["p"], m)
        out[f"m{m}"] = {"B": B, "L": sum(1 for x in range(B) if vc.liftable(x))}
    return out


def build_plan() -> dict:
    fixtures = sorted(common.load_fixtures(), key=lambda f: (f["bits"], f["seed"]))
    cells = []
    for fx in fixtures:
        for kind in CELL_KINDS:
            cells.append({"cell_id": f"{common.fixture_id(fx)}:{kind}", "bits": fx["bits"], "seed": fx["seed"],
                          "kind": kind, "params": {}})
    return {
        "experiment_id": common.EXPERIMENT_ID,
        "protocol_version": common.PROTOCOL_VERSION,
        "protocol": {
            "specification": str(common.SPECIFICATION.relative_to(common.REPO_ROOT)),
            "specification_sha256": common.sha256_file(common.SPECIFICATION),
            "amendment": str(common.AMENDMENT.relative_to(common.REPO_ROOT)),
            "amendment_sha256": common.sha256_file(common.AMENDMENT),
            "amendment_v3": str(common.AMENDMENT_V3.relative_to(common.REPO_ROOT)),
            "amendment_v3_sha256": common.sha256_file(common.AMENDMENT_V3),
            "amendment_v3_decision": "DEC-20260929-a8d594",
            "b0_definition": str(common.B0_AMENDMENT.relative_to(common.REPO_ROOT)) + " C-4",
            "b0_definition_sha256": common.sha256_file(common.B0_AMENDMENT),
            "fixtures": str(common.FIXTURE_JSON.relative_to(common.REPO_ROOT)),
            "fixtures_sha256": common.sha256_file(common.FIXTURE_JSON),
            "fixture_generator": str(common.FIXTURE_GEN.relative_to(common.REPO_ROOT)),
            "fixture_generator_sha256": common.sha256_file(common.FIXTURE_GEN),
        },
        "namespace": common.FROZEN_NS,
        "fixtures": [{**fx, "fixture_id": common.fixture_id(fx), "derived": fixture_derived(fx)} for fx in fixtures],
        "cells": cells,
        "n_cells": len(cells),
        "parameters": {
            "m_primary": common.M_PRIMARY, "m_stage_cost_only": list(common.M_STAGE_COST_ONLY),
            "factor_base_rule": "F = {P : x(P) < B}, B = ceil(p^(1/m)) (exact integer ceiling)",
            "n_heldout_alpha2": common.N_HELDOUT, "excess_rows": common.EXCESS_ROWS,
            "n_descents": common.N_DESCENTS, "n_rho_targets": common.N_RHO_TARGETS,
            "rho": "negation map, r = 32 adding walk, fruitless-cycle escape",
            "bootstrap_resamples": common.BOOTSTRAP_RESAMPLES,
            "audit": "attempt j replayed iff SHA256('<ns>|audit|<bits>|<seed>|<j>') % 10 == 0; all LA steps; every descent",
            "cost_units_C3": {"fp_mul": common.UNIT_MUL, "fp_inv": common.UNIT_INV,
                              "affine_point_addition": common.UNIT_POINT_ADD, "hash_probe": common.UNIT_PROBE,
                              "la_modmul": common.UNIT_LA_MUL, "la_inv_reading": common.UNIT_INV},
            "complete_cost_C5": "stage 1 + stage 3 + 16 descents (stage 2 and controls excluded)",
            "ratio_denominator_C5": "13 * 0.886 * sqrt(q)",
            "verdict_C5": ("sub_rho_signal iff exponent upper CI < 0.5 AND ratio < 1 on every 20-bit fixture; "
                           "scoped_negative (dominant stage at 20 bits) iff exponent lower CI >= 0.5; "
                           "otherwise inconclusive"),
            "fxa_nonverdict": ("AMD-20260929-143d11 FX-A: complete_units_rj_incremental = complete_units - "
                               "13 * sum over stage-1 attempts (rj_ops_j - 1); descriptive, not a verdict input; "
                               "supplementary figure also substitutes descent attempts (OQ-15)"),
            "max_attempts_machine_cap": 5_000_000, "max_descent_attempts_machine_cap": 1_000_000,
        },
        "labels": {
            "target": "<ns>|target|<bits>|<seed>", "attempt": "<ns>|attempt|<bits>|<seed>|<j> (a=hi128, b=lo128)",
            "heldout": "<ns>|heldout|<bits>|<seed>|<i>", "descent": "<ns>|descent|<bits>|<seed>|<t>",
            "descent_r": "<ns>|descent_r|<bits>|<seed>|<t>|<i>", "randfb": "<ns>|randfb|<bits>|<seed>|<i>",
            "rho": "<ns>|rho|<bits>|<seed>|<t>", "rho_walk": "<ns>|rho_walk|<bits>|<seed>|<t>|<restart>.<tag>",
            "scramble": "<ns>|scramble|<bits>|<seed>|<fbkind>|<redraw>.<i>",
            "lanczos": "<ns>|lanczos|<bits>|<seed>|<fbkind>|<try>|<i>",
            "audit": "<ns>|audit|<bits>|<seed>|<j>", "bootstrap": "<ns>|bootstrap",
        },
        "machine_protection_C7": {"load_15min_max": hostinfo.MAC_LOAD_MAX,
                                  "system_volume_free_min_gib": hostinfo.MAC_SYS_FREE_MIN_GIB,
                                  "repo_volume_free_min_gib": hostinfo.MAC_REPO_FREE_MIN_GIB,
                                  "maximum_memory_gb": 8, "maximum_workers": 1, "maximum_runs": 1,
                                  "host": "macOS (repository Mac) only"},
        "admission": "driver refuses unless --admission-decision names a coordinator_decision with "
                     "execution_admission.currently_admitted true and EXP-ICEX-aaccfc in target_ids",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "trial-plan-v2.json"))
    args = ap.parse_args(argv)
    Path(args.out).write_text(json.dumps(build_plan(), indent=1, sort_keys=True) + "\n")
    print(common.sha256_file(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
