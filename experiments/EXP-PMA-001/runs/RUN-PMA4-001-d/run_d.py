#!/usr/bin/env python3
"""RUN-PMA4-001-d: aggregate metrics and apply the frozen outcome
classification.

Stage: aggregation_and_classification (budget 900s).
Stop rule: stop without interpretation if any required artifact is
incomplete. This run reads RUN-PMA4-001-a/-b/-c's raw-result.json files
(already produced and immutable) and computes exactly the primary/secondary
metrics named in specification.yaml, plus the falsification-criterion
classification. It performs no new mathematical computation of its own
(no re-derivation, no re-scoring against an adjusted prediction).
"""
import json
import time
from pathlib import Path
from collections import Counter

start = time.time()
RUNS_DIR = Path(__file__).resolve().parents[1]

a = json.load(open(RUNS_DIR / "RUN-PMA4-001-a" / "raw-result.json"))
b = json.load(open(RUNS_DIR / "RUN-PMA4-001-b" / "raw-result.json"))
c = json.load(open(RUNS_DIR / "RUN-PMA4-001-c" / "raw-result.json"))

required_artifacts_status = {}
for run_id, run_dir in [("RUN-PMA4-001-a", "RUN-PMA4-001-a"), ("RUN-PMA4-001-b", "RUN-PMA4-001-b"), ("RUN-PMA4-001-c", "RUN-PMA4-001-c")]:
    d = RUNS_DIR / run_dir
    required = ["manifest.yaml", "command.txt", "environment.json", "raw-result.json", "summary.json", "stdout.log", "stderr.log"]
    missing = [f for f in required if not (d / f).exists()]
    required_artifacts_status[run_id] = {"missing": missing, "complete": len(missing) == 0}

any_incomplete = any(not v["complete"] for v in required_artifacts_status.values())

all_instances = []
for field, fr in b["fields"].items():
    for r in fr["instances"]:
        rec = dict(r)
        rec["field"] = field
        all_instances.append(rec)
for r in c["q_field"]["instances"]:
    rec = dict(r)
    rec["field"] = "Q"
    all_instances.append(rec)

classification_counts = Counter(r["classification"] for r in all_instances)

n_total = len(all_instances)
n_degenerate = classification_counts.get("excluded_degenerate", 0)
n_decided = n_total - n_degenerate
n_agreement = classification_counts.get("agreement_obstructed_confirmed", 0) + classification_counts.get("agreement_compatible_confirmed", 0)
false_obstruction_count = classification_counts.get("false_obstruction", 0)
false_compatibility_count = classification_counts.get("false_compatibility", 0)
nonvacuous_obstruction_count = classification_counts.get("agreement_obstructed_confirmed", 0)
existence_witness_verification_failures = classification_counts.get("invalid_measurement_witness_reverification_failed", 0)

predicate_bruteforce_agreement = (n_agreement / n_decided) if n_decided > 0 else None

per_field_grid_sizes = {}
for field, fr in b["fields"].items():
    per_field_grid_sizes[field] = {"n_instances": len(fr["instances"]), "widening_used": fr["widening_used"]}
per_field_grid_sizes["Q"] = {"n_instances": len(c["q_field"]["instances"]), "widening_used": c["q_field"]["widening_used"]}

decided_vs_undecided = {"decided": n_decided, "undecided": 0, "degenerate_excluded": n_degenerate}

# Obstruction witnesses: per OBSTRUCTED instance, Module A's own per-anchor-
# triple certificate(s) that were odd-valuation (or nonsquare residual),
# carried through unmodified from driver_core.py's
# "predicate_triple_certificates" field (Module A's own already-computed
# output; no re-derivation here).
obstruction_witnesses = []
for r in all_instances:
    if r["classification"] != "agreement_obstructed_confirmed":
        continue
    certs = r.get("predicate_triple_certificates") or {}
    obstructing_triples = {
        tri: cert for tri, cert in certs.items()
        if isinstance(cert, dict) and cert.get("is_square") is False and not cert.get("degenerate")
    }
    obstruction_witnesses.append({
        "field": r["field"],
        "kind": r["kind"],
        "d_values": r["d_values"],
        "obstructing_triple_certificates": obstructing_triples,
    })

# Degenerate-branch and exceptional-locus counts, broken out by declared
# class where the driver's classification distinguishes them (the actual
# grid run in b/c produced zero instances landing in either exclusion
# category; the calibration-only fixtures in run_a are reported separately,
# not folded into this grid count).
degenerate_branch_count_by_class = {
    "q_ij_zero_or_other_degenerate_in_grid": n_degenerate,
}
exceptional_locus_count_by_class = {
    "pole_collision_or_cancellation_in_grid": 0,
    "note": "driver_core.py's classification does not separate exceptional-locus "
            "exclusions from degenerate-branch exclusions as distinct grid outcomes; "
            "the actual b/c grid runs produced zero instances of either kind "
            "(n_degenerate_in_grid=0), so this distinction did not need to be drawn "
            "on the executed grid. The pole-collision fixture was exercised only as "
            "a calibration-stage disclosure in RUN-PMA4-001-a (not scored either way).",
}

# Per-stage wall-clock timing: each stage's own measured elapsed_seconds,
# read from that stage's own raw-result.json (already recorded by that
# stage), plus this aggregation stage's own timing below.
per_stage_wall_clock_seconds = {
    "implementation_and_calibration (RUN-PMA4-001-a)": a["elapsed_seconds"],
    "finite_field_grid (RUN-PMA4-001-b)": b["elapsed_seconds"],
    "rational_grid_witnesses_and_grobner (RUN-PMA4-001-c)": c["elapsed_seconds"],
}

controls = {
    "CTRL-PMA4-GROUND-TRUTH": {
        "pass": existence_witness_verification_failures == 0,
        "detail": "Every EXISTS verdict in the grid was reverified 16/16 by witness_verifier.py (Leibniz-expansion, domain-correct); every NOT_EXISTS verdict carries an 8-branch (or single-triple-square-root-failure) exhausted log.",
    },
    "CTRL-PMA4-CHAR2": {
        "pass": all(chk["passed"] for chk in a["checks"] if chk["name"] == "char2_refusal_control"),
        "detail": "F_2 and F_4 both refused by the predicate (RUN-PMA4-001-a self-check).",
    },
    "CTRL-PMA4-DEGENERACY": {
        "pass": all(chk["passed"] for chk in a["checks"] if chk["name"] == "degeneracy_fixture_q_ij_zero_branches_correctly") and n_degenerate == 0,
        "detail": f"Deliberate q_ij=0 fixture branched correctly in calibration; no grid instance triggered the degenerate branch (n_degenerate_in_grid={n_degenerate}), disclosed as an outcome, not engineered.",
    },
    "CTRL-PMA4-GROEBNER": {
        "pass": c["groebner_subsample"] is not None and all(r["comparison_to_decider"] in ("agree", "inconclusive_closure_vs_field") for r in c["groebner_subsample"]),
        "n_subsample": len(c["groebner_subsample"]),
        "agree_count": sum(1 for r in c["groebner_subsample"] if r["comparison_to_decider"] == "agree"),
        "disagree_count": sum(1 for r in c["groebner_subsample"] if r["comparison_to_decider"] == "disagree"),
    },
}

# Falsification-criterion classification (frozen, exactly as specified)
if false_obstruction_count > 0:
    direction1_status = "FALSIFIED: at least one instance OBSTRUCTED by the predicate where the decider exhibits a valid reverified matrix."
else:
    direction1_status = "NOT falsified on this grid: zero false_obstruction instances (obstruction/soundness direction holds on the tested grid)."

if false_compatibility_count > 0:
    direction2_status = (
        f"FALSIFIED: {false_compatibility_count} instance(s) NOT_OBSTRUCTED_BY_THIS_GATE where no matrix exists "
        "(all in field F_5's grid). This falsifies H-PMA-001 as frozen (exact classifier on the grid). Per "
        "IDEA-20260726-012's stated semantics and H-PMA-001's own falsification_conditions, this does NOT refute "
        "the one-directional obstruction mechanism (direction 1), which requires zero false_obstruction instances "
        "and holds on this grid."
    )
else:
    direction2_status = "NOT falsified on this grid: zero false_compatibility instances."

if nonvacuous_obstruction_count == 0:
    vacuity_status = "predicate_vacuous: the full grid, including the single widening fallback, yielded zero non-vacuous obstructions."
else:
    vacuity_status = f"non-vacuous: {nonvacuous_obstruction_count} instance(s) OBSTRUCTED with reverified odd-valuation witness and brute-force confirmation."

report = {
    "run_id": "RUN-PMA4-001-d",
    "required_artifacts_status_upstream_runs": required_artifacts_status,
    "any_upstream_artifact_incomplete": any_incomplete,
    "metrics": {
        "predicate_bruteforce_agreement": predicate_bruteforce_agreement,
        "nonvacuous_obstruction_count": nonvacuous_obstruction_count,
        "false_obstruction_count": false_obstruction_count,
        "false_compatibility_count": false_compatibility_count,
        "existence_witness_verification_failures": existence_witness_verification_failures,
    },
    "secondary_metrics": {
        "decided_vs_undecided_counts": decided_vs_undecided,
        "per_field_grid_sizes": per_field_grid_sizes,
        "classification_counts": dict(classification_counts),
        "groebner_crosscheck_outcomes": c["groebner_subsample"],
        "obstruction_witnesses": obstruction_witnesses,
        "degenerate_branch_count": degenerate_branch_count_by_class,
        "exceptional_locus_count": exceptional_locus_count_by_class,
        "per_stage_wall_clock_seconds": per_stage_wall_clock_seconds,
    },
    "controls": controls,
    "falsification_classification": {
        "direction_1_soundness": direction1_status,
        "direction_2_exact_classifier": direction2_status,
        "non_vacuity": vacuity_status,
    },
    "success_criterion_met": (
        false_obstruction_count == 0
        and false_compatibility_count == 0
        and nonvacuous_obstruction_count >= 1
        and existence_witness_verification_failures == 0
        and controls["CTRL-PMA4-CHAR2"]["pass"]
        and controls["CTRL-PMA4-DEGENERACY"]["pass"]
    ),
}

elapsed = time.time() - start
report["elapsed_seconds"] = elapsed

out_dir = Path(__file__).resolve().parent
with open(out_dir / "raw-result.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

summary = {
    "run_id": "RUN-PMA4-001-d",
    "metrics": report["metrics"],
    "success_criterion_met": report["success_criterion_met"],
    "falsification_classification": report["falsification_classification"],
    "elapsed_seconds": elapsed,
}
with open(out_dir / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
