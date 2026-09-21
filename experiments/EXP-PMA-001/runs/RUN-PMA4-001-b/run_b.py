#!/usr/bin/env python3
"""RUN-PMA4-001-b: finite-field grid execution (F_3, F_5, F_7).

Stage: finite_field_grid (budget 1800s).
For each field q in {3,5,7}: 8 deterministic grid instances (grid_data.py)
plus 2 deterministically perturbed candidate-obstruction instances.
Predicate (Module A) and ground-truth decider (Module B, with witness
reverification via witness_verifier.py) are run on every instance;
degenerate instances are excluded from the agreement grid and counted
separately. A single widening fallback (+8 instances, capped by
grid_instance_cap=60 total) is applied per field if that field's base grid
yields zero non-vacuous obstructions, exactly once, within this stage's
budget.
"""
import json
import sys
import time
from pathlib import Path

IMPL_DIR = Path(__file__).resolve().parents[2] / "implementation"
sys.path.insert(0, str(IMPL_DIR))

from common import field_domain
import grid_data as G
from driver_core import run_instance

STAGE_BUDGET_SECONDS = 1800
GRID_INSTANCE_CAP = 60
start = time.time()

results = {"run_id": "RUN-PMA4-001-b", "fields": {}}
total_instances_generated = 0

for field_label in (3, 5, 7):
    domain = field_domain(field_label)
    field_report = {"instances": [], "widening_used": False}

    for m in range(8):
        inst = G.grid_instance(field_label, m)
        field_report["instances"].append(run_instance(inst, domain, field_label, "grid"))
        total_instances_generated += 1
    for m in range(2):
        inst = G.perturbed_instance(field_label, m)
        field_report["instances"].append(run_instance(inst, domain, field_label, "perturbed"))
        total_instances_generated += 1

    nonvacuous = sum(1 for r in field_report["instances"] if r["classification"] == "agreement_obstructed_confirmed")
    if nonvacuous == 0 and (time.time() - start) < STAGE_BUDGET_SECONDS:
        field_report["widening_used"] = True
        for m in range(8, 16):
            if total_instances_generated >= GRID_INSTANCE_CAP:
                break
            inst = G.widening_instance(field_label, m)
            field_report["instances"].append(run_instance(inst, domain, field_label, "widened_grid"))
            total_instances_generated += 1

    results["fields"][str(field_label)] = field_report

    if time.time() - start > STAGE_BUDGET_SECONDS:
        results["stopped_at_budget"] = True
        break

elapsed = time.time() - start
results["elapsed_seconds"] = elapsed
results["total_instances_generated"] = total_instances_generated

out_dir = Path(__file__).resolve().parent
with open(out_dir / "raw-result.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

summary = {"run_id": "RUN-PMA4-001-b", "elapsed_seconds": elapsed, "fields": {}}
for field_label, fr in results["fields"].items():
    counts = {}
    for r in fr["instances"]:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1
    summary["fields"][field_label] = {"counts": counts, "widening_used": fr["widening_used"], "n_instances": len(fr["instances"])}

with open(out_dir / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
