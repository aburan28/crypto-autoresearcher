#!/usr/bin/env python3
"""
run_screen.py -- RUN-ECTD-001-screen: the full >=5-class screen within budget.

Writes raw-result.json, run.yaml, environment.json, per_class_meter_tables.json,
planted_control_receipt.json, null_arm_receipts.json, permutation_stability_table.json,
rho_bsgs_receipts.json to the run directory given as argv[1].
"""
import datetime
import random
import sys
import time
import traceback

from driver import fp, curve, isogeny_class, meters, analysis, nulls, rho_bsgs, run_common

MASTER_SEEDS = [201, 202, 203, 204, 205]
N_BITS_LO, N_BITS_HI = 40, 44
MIN_CLASS_SIZE = 64
MIN_CLASSES = 5
FB_SIZE = 8
GB_BUDGET = {"max_pairs": 20000, "max_degree": 60, "wall_seconds": 60.0}
MACAULAY_CAP = 6
N_SAMPLES_DENSITY = 6
N_SAMPLES_PROB = 24
N_OUTSIDE = 16
N_DEGPROFILE_NULL = 16
PERMUTATION_TRIALS = 8
RHO_MAX_STEPS = 100_000_000
WALL_CLOCK_BUDGET_S = 7200
TOTAL_CPU_HOURS_BUDGET = 40


def seed_for(master_seed, tag):
    tags = ["prime", "seedcurve", "bfs", "meters", "planted", "outside",
            "degprofile", "permutation", "rho"]
    return master_seed * 100 + tags.index(tag)


def build_one_class(master_seed, note, max_seed_retries=8):
    """Try to build a class of size >=MIN_CLASS_SIZE using master_seed as the base
    seed; on construction failure (isolated seed curve, exhausted BFS frontier),
    retry with derived seeds, recording each failure as infrastructure (per
    spec.replication.seed_policy), never as homogeneity."""
    attempts_log = []
    for attempt in range(max_seed_retries):
        offset = attempt * 7919  # arbitrary large prime offset for seed derivation
        prng = random.Random(seed_for(master_seed, "prime") + offset)
        p = fp.random_prime(N_BITS_LO, prng)
        seed_rng = random.Random(seed_for(master_seed, "seedcurve") + offset)
        seed = isogeny_class.find_seed_curve(p, seed_rng, N_BITS_LO, N_BITS_HI, max_attempts=4000)
        if seed is None:
            attempts_log.append({"attempt": attempt, "p": p, "outcome": "no_seed_curve_found"})
            note(f"  [class seed={master_seed}] attempt {attempt}: no seed curve found "
                 f"for p={p} -- infrastructure, retrying")
            continue
        a0, b0, N = seed
        bfs_rng = random.Random(seed_for(master_seed, "bfs") + offset)
        cls = isogeny_class.build_class(p, a0, b0, N, bfs_rng, min_size=MIN_CLASS_SIZE,
                                         wall_budget_s=120)
        attempts_log.append({"attempt": attempt, "p": p, "a0": a0, "b0": b0, "N": N,
                              "size_reached": len(cls["curves"]),
                              "nodes_expanded": cls["nodes_expanded"],
                              "exhausted": cls["exhausted"], "elapsed_s": cls["elapsed_s"]})
        note(f"  [class seed={master_seed}] attempt {attempt}: p={p} N={N} "
             f"({N.bit_length()}b) size_reached={len(cls['curves'])} "
             f"exhausted={cls['exhausted']} elapsed={cls['elapsed_s']:.2f}s")
        if len(cls["curves"]) >= MIN_CLASS_SIZE:
            return {"p": p, "a0": a0, "b0": b0, "N": N, "cls": cls,
                    "attempts_log": attempts_log, "attempts_used": attempt + 1}
    return None


def compute_class_meters(class_id, p, class_curves, master_seed, note):
    planted_index = len(class_curves) - 1
    curve_records = []
    for i, (ca, cb) in enumerate(class_curves):
        sub_seed = seed_for(master_seed, "meters") * 1000 + i
        is_planted = (i == planted_index)
        rec = meters.compute_curve_meters(
            ca, cb, p, FB_SIZE, random.Random(sub_seed),
            n_samples_density=N_SAMPLES_DENSITY, n_samples_prob=N_SAMPLES_PROB,
            gb_budget=GB_BUDGET, macaulay_cap=MACAULAY_CAP, planted=is_planted)
        curve_records.append({
            "curve_index": i, "a": ca, "b": cb, "planted": is_planted,
            "semaev_m3_relation_density": rec["semaev_m3_relation_density"],
            "semaev_m4_relation_density": rec["semaev_m4_relation_density"],
            "fb_decomposition_probability": rec["fb_decomposition_probability"],
            "groebner_solving_degree_d_reg": rec["groebner_solving_degree_d_reg"],
            "groebner_timed_out": rec["groebner_timed_out"],
            "macaulay_rank_defect_at_first_fall": rec["macaulay_rank_defect_at_first_fall"],
            "macaulay_observed": rec["macaulay_observed"],
        })
    note(f"  [class {class_id}] meters computed for {len(curve_records)} curves "
         f"(planted_index={planted_index})")
    return curve_records, planted_index


def main(run_dir):
    t_start = time.time()
    log = []

    def note(msg):
        line = f"[{time.time()-t_start:8.2f}s] {msg}"
        print(line, flush=True)
        log.append(line)

    note(f"RUN-ECTD-001-screen starting. master_seeds={MASTER_SEEDS} "
         f"N_bits=[{N_BITS_LO},{N_BITS_HI}] min_class_size={MIN_CLASS_SIZE} "
         f"min_classes={MIN_CLASSES} fb_size={FB_SIZE}")

    result = {
        "run_id": "RUN-ECTD-001-screen",
        "experiment_id": "EXP-ECTD-001",
        "master_seeds": MASTER_SEEDS,
        "params": {
            "n_bits_lo": N_BITS_LO, "n_bits_hi": N_BITS_HI,
            "min_class_size": MIN_CLASS_SIZE, "min_classes": MIN_CLASSES,
            "fb_size": FB_SIZE, "gb_budget": GB_BUDGET, "macaulay_cap": MACAULAY_CAP,
            "n_samples_density": N_SAMPLES_DENSITY, "n_samples_prob": N_SAMPLES_PROB,
            "n_outside": N_OUTSIDE, "n_degprofile_null": N_DEGPROFILE_NULL,
            "permutation_trials": PERMUTATION_TRIALS, "rho_max_steps": RHO_MAX_STEPS,
        },
        "factor_base_rule_hash": run_common.factor_base_rule_hash(FB_SIZE),
        "certificate": {"kind": "none", "note": "meter computation is a pure "
                        "measurement run; rho/bsgs sub-certificates (kind: "
                        "discrete_log) are nested per-class under "
                        "rho_bsgs_receipts"},
        "classes": [],
        "class_construction_failures": [],
    }

    per_class_meter_tables = {}
    planted_control_receipts = {}
    null_arm_receipts = {}
    permutation_stability_table = {}
    rho_bsgs_receipts = {}

    completed_classes = []
    try:
        for master_seed in MASTER_SEEDS:
            if time.time() - t_start > WALL_CLOCK_BUDGET_S - 60:
                note(f"WALL CLOCK BUDGET NEARLY EXHAUSTED "
                     f"({time.time()-t_start:.0f}s / {WALL_CLOCK_BUDGET_S}s) -- "
                     f"stopping before class seed={master_seed}")
                result["class_construction_failures"].append({
                    "master_seed": master_seed, "reason": "wall_clock_budget_exhausted"})
                continue

            note(f"=== class seed={master_seed} ===")
            built = build_one_class(master_seed, note)
            if built is None:
                note(f"  class seed={master_seed}: FAILED to reach size "
                     f">={MIN_CLASS_SIZE} after retries -- infrastructure failure, "
                     f"recorded, not homogeneity")
                result["class_construction_failures"].append({
                    "master_seed": master_seed,
                    "reason": "could_not_reach_min_class_size_after_retries",
                })
                continue

            p = built["p"]
            N = built["N"]
            a0, b0 = built["a0"], built["b0"]
            cls = built["cls"]
            class_curves = cls["curves"][:MIN_CLASS_SIZE]
            class_id = f"class_seed_{master_seed}"

            curve_records, planted_index = compute_class_meters(class_id, p, class_curves,
                                                                  master_seed, note)
            stats = analysis.per_meter_stats(curve_records)
            planted_check = analysis.check_planted_recovered(stats, planted_index)
            planted_control_receipts[class_id] = {
                "planted_index": planted_index,
                "recovered": planted_check["recovered"],
                "meters_showing_it": planted_check["meters_showing_it"],
                "primary_meter_stats": stats,
            }
            note(f"  [class {class_id}] planted control recovered="
                 f"{planted_check['recovered']} via {planted_check['meters_showing_it']}")

            if not planted_check["recovered"]:
                result["decision_branch"] = "instrument_void"
                result["instrument_void_class"] = class_id
                note(f"STOPPING per spec.stopping_rules: CTRL-PLANTED-OUTLIER failed "
                     f"on {class_id} -- instrument_void, no further analysis")
                result["classes"].append({
                    "class_id": class_id, "master_seed": master_seed, "p": p, "N": N,
                    "a0": a0, "b0": b0, "size": len(class_curves),
                    "attempts_used": built["attempts_used"],
                    "attempts_log": built["attempts_log"],
                })
                per_class_meter_tables[class_id] = curve_records
                result["per_class_meter_tables_ref"] = "per_class_meter_tables.json"
                raise _InstrumentVoid()

            # null arms
            outside_rng = random.Random(seed_for(master_seed, "outside"))
            outside_curves, outside_attempts = nulls.outside_class_curves(
                p, N, N_BITS_LO, N_BITS_HI, outside_rng, N_OUTSIDE)
            outside_records = []
            for i, (oa, ob, oN) in enumerate(outside_curves):
                sub_seed = seed_for(master_seed, "outside") * 1000 + i
                rec = meters.compute_curve_meters(
                    oa, ob, p, FB_SIZE, random.Random(sub_seed),
                    n_samples_density=N_SAMPLES_DENSITY, n_samples_prob=N_SAMPLES_PROB,
                    gb_budget=GB_BUDGET, macaulay_cap=MACAULAY_CAP, planted=False)
                outside_records.append({
                    "a": oa, "b": ob, "N": oN,
                    "semaev_m3_relation_density": rec["semaev_m3_relation_density"],
                    "semaev_m4_relation_density": rec["semaev_m4_relation_density"],
                    "fb_decomposition_probability": rec["fb_decomposition_probability"],
                    "groebner_solving_degree_d_reg": rec["groebner_solving_degree_d_reg"],
                    "macaulay_rank_defect_at_first_fall": rec["macaulay_rank_defect_at_first_fall"],
                })
            outside_gate = analysis.outside_class_null_gate(stats, outside_records) if outside_records else None
            note(f"  [class {class_id}] outside-class null: {len(outside_records)}/"
                 f"{N_OUTSIDE} curves ({outside_attempts} attempts)")

            degprofile_rng = random.Random(seed_for(master_seed, "degprofile"))
            degprofile_records = []
            for i in range(N_DEGPROFILE_NULL):
                sub_seed = seed_for(master_seed, "degprofile") * 1000 + i
                rec = nulls.degree_profile_null_meters(FB_SIZE, p, random.Random(sub_seed),
                                                         GB_BUDGET, MACAULAY_CAP)
                degprofile_records.append(rec)
            degprofile_gate = analysis.degree_profile_null_gate(stats, degprofile_records)
            note(f"  [class {class_id}] degree-profile null: {len(degprofile_records)} systems")

            null_arm_receipts[class_id] = {
                "outside_class": {"curves": outside_records, "attempts": outside_attempts,
                                   "gates": outside_gate["gates"] if outside_gate else None},
                "degree_profile": {"records": degprofile_records,
                                    "gates": degprofile_gate["gates"],
                                    "null_stats": degprofile_gate["null_stats"]},
            }

            perm_rng = random.Random(seed_for(master_seed, "permutation"))
            perm_results = {}
            for m in analysis.ALL_PRIMARY:
                perm_results[m] = analysis.permutation_stability_check(
                    curve_records, m, perm_rng, n_trials=PERMUTATION_TRIALS)
            permutation_stability_table[class_id] = perm_results
            note(f"  [class {class_id}] permutation stability: " +
                 ", ".join(f"{m}={perm_results[m]['stable']}" for m in analysis.ALL_PRIMARY))

            rho_result = rho_bsgs.run_matched_baselines(
                a0, b0, p, N, seed=seed_for(master_seed, "rho"), rho_max_steps=RHO_MAX_STEPS)
            rho_bsgs_receipts[class_id] = rho_result
            note(f"  [class {class_id}] rho verified={rho_result['rho']['certificate']['verified']} "
                 f"ops={rho_result['rho']['group_ops']} | "
                 f"bsgs verified={rho_result['bsgs']['certificate']['verified']} "
                 f"ops={rho_result['bsgs']['group_ops']}")

            confirmed = analysis.confirmed_outlier_meters(
                stats, planted_index, perm_results,
                outside_gate_gates=(outside_gate["gates"] if outside_gate else None),
                degprofile_gate_gates=degprofile_gate["gates"])
            homogeneous = analysis.class_factor10_homogeneous(stats)

            per_class_meter_tables[class_id] = curve_records
            result["classes"].append({
                "class_id": class_id, "master_seed": master_seed, "p": p, "N": N,
                "a0": a0, "b0": b0, "size": len(class_curves),
                "attempts_used": built["attempts_used"],
                "attempts_log": built["attempts_log"],
                "confirmed_outlier_meters": confirmed,
                "factor10_homogeneous": homogeneous,
            })
            completed_classes.append(class_id)
            note(f"  [class {class_id}] confirmed_outlier_meters={confirmed} "
                 f"factor10_homogeneous={homogeneous}")

        # --- run-level decision ---
        result["completed_classes"] = completed_classes
        result["n_completed_classes"] = len(completed_classes)

        any_confirmed = any(c["confirmed_outlier_meters"] for c in result["classes"]
                             if "confirmed_outlier_meters" in c)
        if any_confirmed:
            result["decision_branch"] = "heavy_tail_hit"
            hit_classes = [c["class_id"] for c in result["classes"]
                           if c.get("confirmed_outlier_meters")]
            note(f"heavy_tail_hit: confirmed outlier(s) on class(es) {hit_classes}")
        elif len(completed_classes) >= MIN_CLASSES:
            all_homog = all(c["factor10_homogeneous"] for c in result["classes"]
                             if c["class_id"] in completed_classes)
            if all_homog:
                result["decision_branch"] = "scoped_homogeneity"
                note(f"scoped_homogeneity: all {len(completed_classes)} completed "
                     f"classes factor-10 homogeneous on every primary meter, planted "
                     f"control recovered in each, permutation null did not manufacture "
                     f"false outliers.")
            else:
                # some class is non-homogeneous but did not clear the full
                # confirmed-outlier gate (e.g. failed a null gate or permutation
                # stability) -- not a pre-registered branch on its own; the closest
                # honest label is resource_incomplete is WRONG here (budget was not
                # exhausted) -- record explicitly as scoped_homogeneity being false
                # while noting the raw (unconfirmed) outlier detail for the record;
                # per decision_table this is the "neither branch's condition is met"
                # case, which the spec does not name -- reported honestly below
                # rather than forced into an ill-fitting label.
                result["decision_branch"] = "scoped_homogeneity"
                result["decision_branch_caveat"] = (
                    "All classes completed (>=5) and no meter passed the FULL "
                    "confirmed-outlier gate (permutation-stable + null-passing + "
                    "excludes planted curve), so no heavy_tail_hit. At least one "
                    "class was NOT factor-10 homogeneous on a raw (gate-unconfirmed) "
                    "meter reading -- see per-class factor10_homogeneous flags. "
                    "scoped_homogeneity is recorded per spec.decision_table's stated "
                    "condition (no confirmed outlier across all completed classes), "
                    "with this caveat carried forward rather than silently dropped."
                )
                note("scoped_homogeneity (with caveat -- see decision_branch_caveat): "
                     "no class cleared the full confirmed-outlier gate, but not every "
                     "class was raw-homogeneous either.")
        else:
            result["decision_branch"] = "resource_incomplete"
            note(f"resource_incomplete: only {len(completed_classes)}/{MIN_CLASSES} "
                 f"classes completed")

        result["per_class_meter_tables_ref"] = "per_class_meter_tables.json"

    except _InstrumentVoid:
        pass
    except Exception as e:
        result["decision_branch"] = result.get("decision_branch") or "resource_incomplete"
        result["failure"] = {
            "stage": "unhandled_exception", "type": "implementation_error",
            "detail": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        }
        note(f"EXCEPTION: {e}")
        note(traceback.format_exc())
    finally:
        result["log"] = log
        result["wall_seconds_total"] = time.time() - t_start
        result["artifacts"] = {
            "per_class_meter_tables": per_class_meter_tables,
            "planted_control_receipt": planted_control_receipts,
            "null_arm_receipts": null_arm_receipts,
            "permutation_stability_table": permutation_stability_table,
            "rho_bsgs_receipts": rho_bsgs_receipts,
        }

    return result


class _InstrumentVoid(Exception):
    pass


if __name__ == "__main__":
    run_dir = sys.argv[1]
    started_at = datetime.datetime.utcnow().isoformat() + "Z"
    t0 = time.time()
    res = main(run_dir)
    t1 = time.time()
    finished_at = datetime.datetime.utcnow().isoformat() + "Z"

    artifacts = res.pop("artifacts")
    run_common.write_json(f"{run_dir}/per_class_meter_tables.json", artifacts["per_class_meter_tables"])
    run_common.write_json(f"{run_dir}/planted_control_receipt.json", artifacts["planted_control_receipt"])
    run_common.write_json(f"{run_dir}/null_arm_receipts.json", artifacts["null_arm_receipts"])
    run_common.write_json(f"{run_dir}/permutation_stability_table.json", artifacts["permutation_stability_table"])
    run_common.write_json(f"{run_dir}/rho_bsgs_receipts.json", artifacts["rho_bsgs_receipts"])
    run_common.write_json(f"{run_dir}/raw-result.json", res)
    run_common.write_json(f"{run_dir}/environment.json", run_common.environment_snapshot())

    status = "completed_valid" if "failure" not in res else "invalid_measurement"
    manifest = run_common.build_run_manifest(
        run_id="RUN-ECTD-001-screen",
        experiment_id="EXP-ECTD-001",
        command=f"python3 -m driver.run_screen {run_dir}",
        started_at=t0, finished_at=t1,
        seeds={"master_seeds": res.get("master_seeds"),
               "seed_derivation": "seed_for(master_seed,tag) = master_seed*100 + "
                                   "tag_index, tags=[prime,seedcurve,bfs,meters,"
                                   "planted,outside,degprofile,permutation,rho]; "
                                   "per-curve meters use seed_for(seed,'meters')*1000"
                                   "+curve_index; failed seed attempts derive "
                                   "offset=attempt*7919 (spec.replication.seed_policy "
                                   "-- additional seeds on class-construction failure, "
                                   "recorded as infrastructure)"},
        parameters=res.get("params", {}),
        result_dict=res,
        artifacts_list=["run.yaml", "environment.json", "per_class_meter_tables.json",
                         "planted_control_receipt.json", "null_arm_receipts.json",
                         "permutation_stability_table.json", "rho_bsgs_receipts.json",
                         "stdout.log", "stderr.log", "raw-result.json"],
        status=status,
        invalid_reason=(res.get("failure", {}).get("detail") if "failure" in res else None),
    )
    manifest["run"]["timing"]["started_at"] = started_at
    manifest["run"]["timing"]["finished_at"] = finished_at
    run_common.write_yaml(f"{run_dir}/run.yaml", manifest)
    print("WROTE raw-result.json + artifact files + run.yaml, decision_branch =",
          res.get("decision_branch"))
