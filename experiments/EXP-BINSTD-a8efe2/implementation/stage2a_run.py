#!/usr/bin/env python3
"""Stage 2a encoder-level clause-width / substitution-variable summaries.

l in {6,7,8}, m=3, n=9; >=5 seeds; solver-free. Records MEASURED distributions
and keeps naive 5-vs-3 MODELED ratio in a separate column.
"""
from __future__ import annotations

import json
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from encoder import encode_pdp_full, eval_s3_coords
from gf2n import MODULI, N, Field, poly_to_string
from runpack import EXP_ROOT, dump_json, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-53d976"
SEEDS = [20261001, 20261002, 20261003, 20261004, 20261005]
L_VALUES = [6, 7, 8]
B_CURVE = 1
# Instance grid: >=10 UNSAT and >=10 planted-SAT when constructible — at
# encoder-only Stage 2a we emit 10 of each label per (l, arm) across seeds
# (2 per seed × 5 seeds = 10).
INSTANCES_PER_SEED_PER_STATUS = 2


def main() -> int:
    fixture = EXP_ROOT / "stage1" / "structural-fixture-report.yaml"
    if not fixture.exists():
        raise SystemExit("REFUSE: Stage 1 fixture missing")
    # Check halt flag lightly via text
    if "structural_fixture_pass: false" in fixture.read_text().lower():
        raise SystemExit("REFUSE: Stage 1 structural fixture failed")

    t0 = time.perf_counter()
    started = utc_now()

    records = []
    for l in L_VALUES:
        for arm_name, mod in MODULI.items():
            field = Field(N, mod)
            for seed in SEEDS:
                rng = random.Random(seed + 1000 * l + (0 if arm_name == "trinomial" else 1))
                for status in ("planted_SAT", "UNSAT"):
                    for inst in range(INSTANCES_PER_SEED_PER_STATUS):
                        if status == "planted_SAT":
                            planted = tuple(rng.randrange(1 << l) for _ in range(3))
                            target = eval_s3_coords(field, planted, l, B_CURVE)
                        else:
                            planted = None
                            target = rng.randrange(1 << N)
                        sys_enc = encode_pdp_full(
                            field,
                            3,
                            l,
                            target,
                            arm_name,
                            status,
                            planted=planted,
                            b_curve=B_CURVE,
                        )
                        records.append(
                            {
                                "l": l,
                                "arm": arm_name,
                                "seed": seed,
                                "instance_status": status,
                                "instance_index": inst,
                                "target": target,
                                "clause_width_mean_measured": sys_enc.clause_width_mean(),
                                "clause_width_max_measured": sys_enc.clause_width_max(),
                                "clause_width_histogram_measured": sys_enc.clause_width_histogram(),
                                "substitution_variable_count_measured": sys_enc.substitution_variable_count,
                                "core_variable_count": sys_enc.core_variable_count,
                                "monomial_support_size": sys_enc.monomial_support_size,
                                "n_xor_clauses": len(sys_enc.xor_clauses),
                            }
                        )

    # Summaries per (l, arm)
    def subset(l, arm, status=None):
        out = [r for r in records if r["l"] == l and r["arm"] == arm]
        if status:
            out = [r for r in out if r["instance_status"] == status]
        return out

    clause_summary = {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": "2a",
        "n": N,
        "m": 3,
        "l_values": L_VALUES,
        "seeds": SEEDS,
        "instances_per_seed_per_status": INSTANCES_PER_SEED_PER_STATUS,
        "instances_per_arm_status_target": ">=10 UNSAT and >=10 planted-SAT",
        "solver": None,
        "note": "Encoder-level only; no SAT solve. All widths/counts MEASURED.",
        "naive_term_ratio_modeled": {"label": "MODELED", "value": 5 / 3},
        "by_cell": [],
        "ratios": [],
        "seed_spread": [],
        "tail_checks": [],
    }
    subst_summary = {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": "2a",
        "n": N,
        "m": 3,
        "l_values": L_VALUES,
        "seeds": SEEDS,
        "naive_term_ratio_modeled": {"label": "MODELED", "value": 5 / 3},
        "by_cell": [],
        "ratios": [],
        "seed_spread": [],
    }

    for l in L_VALUES:
        for arm_name in MODULI:
            rows = subset(l, arm_name)
            means = [r["clause_width_mean_measured"] for r in rows]
            maxes = [r["clause_width_max_measured"] for r in rows]
            substs = [r["substitution_variable_count_measured"] for r in rows]
            n_sat = len(subset(l, arm_name, "planted_SAT"))
            n_unsat = len(subset(l, arm_name, "UNSAT"))
            cell_cw = {
                "l": l,
                "arm": arm_name,
                "modulus": poly_to_string(MODULI[arm_name]),
                "n_instances": len(rows),
                "n_planted_SAT": n_sat,
                "n_UNSAT_intent": n_unsat,
                "clause_width_mean_measured": statistics.mean(means),
                "clause_width_mean_stdev_measured": statistics.pstdev(means) if len(means) > 1 else 0.0,
                "clause_width_max_measured_tail": max(maxes),
                "core_variable_count": rows[0]["core_variable_count"],
            }
            clause_summary["by_cell"].append(cell_cw)
            subst_summary["by_cell"].append(
                {
                    "l": l,
                    "arm": arm_name,
                    "n_instances": len(rows),
                    "substitution_variable_count_mean_measured": statistics.mean(substs),
                    "substitution_variable_count_stdev_measured": statistics.pstdev(substs) if len(substs) > 1 else 0.0,
                    "substitution_variable_count_max_measured": max(substs),
                    "substitution_variable_count_min_measured": min(substs),
                }
            )
            # seed spread
            per_seed_means = []
            for seed in SEEDS:
                sm = [r["clause_width_mean_measured"] for r in rows if r["seed"] == seed]
                per_seed_means.append(statistics.mean(sm))
            clause_summary["seed_spread"].append(
                {
                    "l": l,
                    "arm": arm_name,
                    "per_seed_clause_width_mean_measured": per_seed_means,
                    "spread_max_minus_min_measured": max(per_seed_means) - min(per_seed_means),
                }
            )
            per_seed_subst = []
            for seed in SEEDS:
                sm = [r["substitution_variable_count_measured"] for r in rows if r["seed"] == seed]
                per_seed_subst.append(statistics.mean(sm))
            subst_summary["seed_spread"].append(
                {
                    "l": l,
                    "arm": arm_name,
                    "per_seed_subst_mean_measured": per_seed_subst,
                    "spread_max_minus_min_measured": max(per_seed_subst) - min(per_seed_subst),
                }
            )

        tri_cell = next(c for c in clause_summary["by_cell"] if c["l"] == l and c["arm"] == "trinomial")
        pent_cell = next(c for c in clause_summary["by_cell"] if c["l"] == l and c["arm"] == "pentanomial")
        cw_ratio = pent_cell["clause_width_mean_measured"] / tri_cell["clause_width_mean_measured"]
        clause_summary["ratios"].append(
            {
                "l": l,
                "clause_width_ratio_measured": cw_ratio,
                "direction_gt_1": cw_ratio > 1,
                "naive_term_ratio_modeled": 5 / 3,
            }
        )
        clause_summary["tail_checks"].append(
            {
                "l": l,
                "trinomial_clause_width_max_measured": tri_cell["clause_width_max_measured_tail"],
                "pentanomial_clause_width_max_measured": pent_cell["clause_width_max_measured_tail"],
            }
        )
        tri_s = next(c for c in subst_summary["by_cell"] if c["l"] == l and c["arm"] == "trinomial")
        pent_s = next(c for c in subst_summary["by_cell"] if c["l"] == l and c["arm"] == "pentanomial")
        subst_summary["ratios"].append(
            {
                "l": l,
                "substitution_variable_count_ratio_measured": (
                    pent_s["substitution_variable_count_mean_measured"]
                    / tri_s["substitution_variable_count_mean_measured"]
                    if tri_s["substitution_variable_count_mean_measured"]
                    else None
                ),
                "naive_term_ratio_modeled": 5 / 3,
            }
        )

    clause_summary["n_records"] = len(records)
    subst_summary["n_records"] = len(records)
    # Keep raw records for audit (may be sizable but fine)
    clause_summary["raw_records"] = records
    subst_summary["raw_records_ref"] = "clause-width-summary.json raw_records (shared grid)"

    dump_json(EXP_ROOT / "stage2a" / "clause-width-summary.json", clause_summary)
    dump_json(EXP_ROOT / "stage2a" / "substitution-variable-summary.json", subst_summary)

    wall = time.perf_counter() - t0
    finished = utc_now()
    metrics = {
        "n_records": len(records),
        "clause_width_ratios_measured": clause_summary["ratios"],
        "substitution_variable_ratios_measured": subst_summary["ratios"],
        "naive_term_ratio_modeled": 5 / 3,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
    }
    stdout = "Stage 2a complete\n" + json.dumps(clause_summary["ratios"], indent=2) + "\n"
    write_run_package(
        RUN_ID,
        stage="2a",
        arm="encoder-clause-width",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-a8efe2/implementation/stage2a_run.py",
        parameters={"n": N, "m": 3, "l": L_VALUES, "seeds": SEEDS},
        metrics=metrics,
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none"},
    )
    print(stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
