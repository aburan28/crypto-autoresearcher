#!/usr/bin/env python3
"""
run_impl.py -- RUN-ECTD-001-impl: implement meters, planted control, and the three
null arms; smoke-test on ONE class (still respecting the frozen N-bit-range and
min-class-size thresholds -- "small" refers to running only ONE class rather than
the full >=5-class screen, not to relaxing any frozen parameter).

Writes raw-result.json, run.yaml, environment.json to the run directory given as
argv[1] (stdout/stderr are captured by the caller's shell redirection).
"""
import datetime
import random
import sys
import time
import traceback

from driver import fp, curve, isogeny_class, meters, analysis, nulls, rho_bsgs, run_common

MASTER_SEED = 201
N_BITS_LO, N_BITS_HI = 40, 44  # low end of the frozen [40,56] range, chosen for
                                 # tractability -- see MANIFEST.md "bit-range scoping"
MIN_CLASS_SIZE = 64
FB_SIZE = 8
GB_BUDGET = {"max_pairs": 20000, "max_degree": 60, "wall_seconds": 60.0}
MACAULAY_CAP = 6
N_SAMPLES_DENSITY = 6
N_SAMPLES_PROB = 24
N_OUTSIDE = 6
N_DEGPROFILE_NULL = 6
PERMUTATION_TRIALS = 5
RHO_MAX_STEPS = 100_000_000


def seed_for(tag):
    tags = ["prime", "seedcurve", "bfs", "meters", "planted", "outside",
            "degprofile", "permutation", "rho"]
    return MASTER_SEED * 100 + tags.index(tag)


def main(run_dir):
    t_start = time.time()
    budget = run_common.Budget(wall_clock_seconds_per_run=7200, total_cpu_hours=40,
                                maximum_memory_gb=16, maximum_runs=2)
    log = []

    def note(msg):
        line = f"[{time.time()-t_start:8.2f}s] {msg}"
        print(line)
        log.append(line)

    note(f"RUN-ECTD-001-impl starting. master_seed={MASTER_SEED} "
         f"N_bits=[{N_BITS_LO},{N_BITS_HI}] min_class_size={MIN_CLASS_SIZE} fb_size={FB_SIZE}")

    result = {
        "run_id": "RUN-ECTD-001-impl",
        "experiment_id": "EXP-ECTD-001",
        "master_seed": MASTER_SEED,
        "seeds_used": {},
        "params": {
            "n_bits_lo": N_BITS_LO, "n_bits_hi": N_BITS_HI,
            "min_class_size": MIN_CLASS_SIZE, "fb_size": FB_SIZE,
            "gb_budget": GB_BUDGET, "macaulay_cap": MACAULAY_CAP,
            "n_samples_density": N_SAMPLES_DENSITY, "n_samples_prob": N_SAMPLES_PROB,
            "n_outside": N_OUTSIDE, "n_degprofile_null": N_DEGPROFILE_NULL,
            "permutation_trials": PERMUTATION_TRIALS, "rho_max_steps": RHO_MAX_STEPS,
        },
        "factor_base_rule_hash": run_common.factor_base_rule_hash(FB_SIZE),
        "certificate": {"kind": "none", "note": "meter computation is a pure "
                        "measurement run; rho/bsgs sub-certificates (kind: "
                        "discrete_log) are nested under baselines.rho/bsgs.certificate"},
    }

    try:
        # --- 1. prime + seed curve ---
        prng = random.Random(seed_for("prime"))
        p = fp.random_prime(N_BITS_LO, prng)
        result["p"] = p
        note(f"p = {p} ({p.bit_length()} bits)")

        seed_rng = random.Random(seed_for("seedcurve"))
        seed = isogeny_class.find_seed_curve(p, seed_rng, N_BITS_LO, N_BITS_HI, max_attempts=4000)
        seed_attempts_extra = 0
        while seed is None and seed_attempts_extra < 3:
            seed_attempts_extra += 1
            prng2 = random.Random(seed_for("prime") + 1000 * seed_attempts_extra)
            p = fp.random_prime(N_BITS_LO, prng2)
            seed_rng = random.Random(seed_for("seedcurve") + 1000 * seed_attempts_extra)
            seed = isogeny_class.find_seed_curve(p, seed_rng, N_BITS_LO, N_BITS_HI, max_attempts=4000)
            note(f"seed curve retry {seed_attempts_extra}: p={p}")
        if seed is None:
            result["decision_branch"] = "resource_incomplete"
            result["failure"] = {"stage": "seed_curve_search", "type": "infrastructure_error",
                                  "detail": "could not find any curve with prime order in "
                                            "range after retries"}
            note("FAILED: no seed curve found")
            return result
        a0, b0, N = seed
        note(f"seed curve a={a0} b={b0} N={N} ({N.bit_length()} bits, prime={fp.is_probable_prime(N)})")
        result["seed_curve"] = {"a": a0, "b": b0, "N": N, "p": p}

        # --- 2. isogeny class BFS ---
        bfs_rng = random.Random(seed_for("bfs"))
        cls_attempts = 0
        cls = isogeny_class.build_class(p, a0, b0, N, bfs_rng, min_size=MIN_CLASS_SIZE,
                                         wall_budget_s=120)
        while len(cls["curves"]) < MIN_CLASS_SIZE and cls_attempts < 6:
            cls_attempts += 1
            note(f"class construction attempt {cls_attempts} yielded size "
                 f"{len(cls['curves'])} (<{MIN_CLASS_SIZE}); drawing a new seed curve "
                 f"[infrastructure, not homogeneity]")
            seed_rng = random.Random(seed_for("seedcurve") + 5000 * cls_attempts)
            seed = isogeny_class.find_seed_curve(p, seed_rng, N_BITS_LO, N_BITS_HI, max_attempts=4000)
            if seed is None:
                continue
            a0, b0, N = seed
            bfs_rng = random.Random(seed_for("bfs") + 5000 * cls_attempts)
            cls = isogeny_class.build_class(p, a0, b0, N, bfs_rng, min_size=MIN_CLASS_SIZE,
                                             wall_budget_s=120)
        result["class_construction_attempts"] = cls_attempts + 1
        if len(cls["curves"]) < MIN_CLASS_SIZE:
            result["decision_branch"] = "resource_incomplete"
            result["failure"] = {"stage": "class_bfs", "type": "infrastructure_error",
                                  "detail": f"best class size reached: {len(cls['curves'])} "
                                            f"< required {MIN_CLASS_SIZE} after "
                                            f"{cls_attempts+1} seed attempts"}
            note("FAILED: could not reach min_class_size")
            return result
        class_curves = cls["curves"][:MIN_CLASS_SIZE]
        note(f"class built: size={len(cls['curves'])} (using first {MIN_CLASS_SIZE}), "
             f"nodes_expanded={cls['nodes_expanded']}, elapsed={cls['elapsed_s']:.2f}s")
        result["class"] = {"a0": a0, "b0": b0, "N": N, "p": p,
                            "size_reached": len(cls["curves"]),
                            "size_used": len(class_curves),
                            "nodes_expanded": cls["nodes_expanded"],
                            "elapsed_s": cls["elapsed_s"],
                            "edges_count": len(cls["edges"])}

        # --- 3. meters per curve (last curve is the designated planted-outlier curve) ---
        planted_index = len(class_curves) - 1
        curve_records = []
        meters_rng = random.Random(seed_for("meters"))
        for i, (ca, cb) in enumerate(class_curves):
            sub_seed = seed_for("meters") * 1000 + i
            is_planted = (i == planted_index)
            rec = meters.compute_curve_meters(
                ca, cb, p, FB_SIZE, random.Random(sub_seed),
                n_samples_density=N_SAMPLES_DENSITY, n_samples_prob=N_SAMPLES_PROB,
                gb_budget=GB_BUDGET, macaulay_cap=MACAULAY_CAP, planted=is_planted)
            rec_summary = {
                "curve_index": i, "a": ca, "b": cb, "planted": is_planted,
                "semaev_m3_relation_density": rec["semaev_m3_relation_density"],
                "semaev_m4_relation_density": rec["semaev_m4_relation_density"],
                "fb_decomposition_probability": rec["fb_decomposition_probability"],
                "groebner_solving_degree_d_reg": rec["groebner_solving_degree_d_reg"],
                "groebner_timed_out": rec["groebner_timed_out"],
                "macaulay_rank_defect_at_first_fall": rec["macaulay_rank_defect_at_first_fall"],
                "macaulay_observed": rec["macaulay_observed"],
            }
            curve_records.append(rec_summary)
            if i % 16 == 0 or is_planted:
                note(f"  curve {i}/{len(class_curves)} meters: "
                     f"m3={rec_summary['semaev_m3_relation_density']:.5f} "
                     f"m4={rec_summary['semaev_m4_relation_density']:.5f} "
                     f"prob={rec_summary['fb_decomposition_probability']:.3f} "
                     f"d_reg={rec_summary['groebner_solving_degree_d_reg']} "
                     f"mac_defect={rec_summary['macaulay_rank_defect_at_first_fall']} "
                     f"planted={is_planted}")
        result["curve_records"] = curve_records
        result["planted_index"] = planted_index

        # --- 4. analysis: planted control gate ---
        stats = analysis.per_meter_stats(curve_records)
        planted_check = analysis.check_planted_recovered(stats, planted_index)
        result["primary_meter_stats"] = stats
        result["planted_control"] = planted_check
        note(f"planted control recovered={planted_check['recovered']} "
             f"via meters={planted_check['meters_showing_it']}")

        if not planted_check["recovered"]:
            result["decision_branch"] = "instrument_void"
            note("STOPPING per spec.stopping_rules: planted control failed -> "
                 "instrument_void, no further homogeneity/heavy-tail analysis")
            return result

        # --- 5. null arms (reduced sample sizes for the smoke run) ---
        outside_rng = random.Random(seed_for("outside"))
        outside_curves, outside_attempts = nulls.outside_class_curves(
            p, N, N_BITS_LO, N_BITS_HI, outside_rng, N_OUTSIDE)
        note(f"outside-class null: {len(outside_curves)}/{N_OUTSIDE} curves found "
             f"in {outside_attempts} attempts")
        outside_records = []
        for i, (oa, ob, oN) in enumerate(outside_curves):
            sub_seed = seed_for("outside") * 1000 + i
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
        result["outside_class_null"] = {"curves": outside_records, "attempts": outside_attempts,
                                         "gate": outside_gate["gates"] if outside_gate else None}

        degprofile_rng = random.Random(seed_for("degprofile"))
        degprofile_records = []
        for i in range(N_DEGPROFILE_NULL):
            sub_seed = seed_for("degprofile") * 1000 + i
            rec = nulls.degree_profile_null_meters(FB_SIZE, p, random.Random(sub_seed),
                                                     GB_BUDGET, MACAULAY_CAP)
            degprofile_records.append(rec)
        degprofile_gate = analysis.degree_profile_null_gate(stats, degprofile_records)
        result["degree_profile_null"] = {"records": degprofile_records,
                                          "gate": degprofile_gate["gates"],
                                          "null_stats": degprofile_gate["null_stats"]}
        note(f"degree-profile null: {len(degprofile_records)} systems computed")

        # --- 6. permutation stability ---
        perm_rng = random.Random(seed_for("permutation"))
        perm_results = {}
        for m in analysis.ALL_PRIMARY:
            perm_results[m] = analysis.permutation_stability_check(
                curve_records, m, perm_rng, n_trials=PERMUTATION_TRIALS)
        result["permutation_stability"] = perm_results
        note(f"permutation stability: " +
             ", ".join(f"{m}={perm_results[m]['stable']}" for m in analysis.ALL_PRIMARY))

        # --- 7. matched rho/bsgs baseline ---
        rho_result = rho_bsgs.run_matched_baselines(a0, b0, p, N, seed=seed_for("rho"),
                                                      rho_max_steps=RHO_MAX_STEPS)
        result["rho_bsgs"] = rho_result
        note(f"rho: verified={rho_result['rho']['certificate']['verified']} "
             f"ops={rho_result['rho']['group_ops']} | "
             f"bsgs: verified={rho_result['bsgs']['certificate']['verified']} "
             f"ops={rho_result['bsgs']['group_ops']}")

        # --- 8. decision (restricted to the four pre-registered branches; see
        # MANIFEST.md "decision_branch on a 1-class smoke run" for why
        # scoped_homogeneity is not reachable here) ---
        confirmed = analysis.confirmed_outlier_meters(
            stats, planted_index, perm_results,
            outside_gate_gates=(outside_gate["gates"] if outside_gate else None),
            degprofile_gate_gates=degprofile_gate["gates"])
        result["confirmed_non_planted_outlier_meters"] = confirmed

        if confirmed:
            # spec.decision_table.heavy_tail_hit's condition is literally
            # ">=1 class with R>=100 ..., permutation-stable, nulls pass, planted
            # control recovered" -- no explicit class-count floor -- so a single
            # class clearing every gate legitimately reaches this branch. It is
            # reported and scoped honestly below; it is NOT a family-wide claim
            # (that needs RUN-ECTD-001-screen's >=5 classes) and asserts nothing
            # beyond claim_tier: toy.
            result["decision_branch"] = "heavy_tail_hit"
            note(f"heavy_tail_hit: confirmed non-planted, permutation-stable, "
                 f"null-passing outlier meters on this class: {confirmed}. SCOPE: "
                 f"single-class smoke run (RUN-ECTD-001-impl); toy-scale only; "
                 f"licenses nothing beyond spec.decision_table's stated "
                 f"interpretation (a follow-on path-hiding/detection EXP, never a "
                 f"trapdoor claim).")
        else:
            # spec.decision_table.scoped_homogeneity's condition explicitly requires
            # ">=5 classes factor-10 homogeneous"; this run has exactly 1 class by
            # design (its purpose is instrumentation smoke-test, not the family
            # screen), so that branch's own stated condition is not met here even
            # though this one class IS homogeneous. resource_incomplete ("budget
            # exhaustion before >=5 classes complete") is the closest pre-registered
            # label for "fewer than the required class count completed"; it is
            # emphasized below that this is the DESIGNED scope of the impl run, not
            # an unexpected failure.
            result["decision_branch"] = "resource_incomplete"
            note("This single class is factor-10 homogeneous on every primary meter "
                 "(excluding the deliberately planted curve), but "
                 "spec.decision_table.scoped_homogeneity requires >=5 classes; this "
                 "run intentionally covers only 1 class (smoke-test scope), so "
                 "resource_incomplete is recorded -- NOT a failure, the designed "
                 "scope of RUN-ECTD-001-impl. The >=5-class determination is made by "
                 "RUN-ECTD-001-screen.")

        result["wall_seconds"] = time.time() - t_start
        note(f"RUN-ECTD-001-impl complete in {result['wall_seconds']:.2f}s")
        return result

    except Exception as e:
        result["decision_branch"] = "resource_incomplete"
        result["failure"] = {
            "stage": "unhandled_exception", "type": "implementation_error",
            "detail": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        }
        note(f"EXCEPTION: {e}")
        note(traceback.format_exc())
        return result
    finally:
        result["log"] = log
        result["wall_seconds_total"] = time.time() - t_start


if __name__ == "__main__":
    run_dir = sys.argv[1]
    started_at = datetime.datetime.utcnow().isoformat() + "Z"
    t0 = time.time()
    res = main(run_dir)
    t1 = time.time()
    finished_at = datetime.datetime.utcnow().isoformat() + "Z"

    run_common.write_json(f"{run_dir}/raw-result.json", res)
    run_common.write_json(f"{run_dir}/environment.json", run_common.environment_snapshot())

    status = "completed_valid" if "failure" not in res else "invalid_measurement"
    if res.get("decision_branch") == "instrument_void":
        status = "completed_valid"  # a valid, harness-void determination -- not a
        # crash; see docs/claims-and-verification.md "certificate discipline"
    manifest = run_common.build_run_manifest(
        run_id="RUN-ECTD-001-impl",
        experiment_id="EXP-ECTD-001",
        command=f"python3 -m driver.run_impl {run_dir}",
        started_at=t0, finished_at=t1,
        seeds={"master_seed": res.get("master_seed"),
               "seed_derivation": "seed_for(tag) = master_seed*100 + tag_index, "
                                   "tags=[prime,seedcurve,bfs,meters,planted,outside,"
                                   "degprofile,permutation,rho]; per-curve meters use "
                                   "seed_for('meters')*1000+curve_index"},
        parameters=res.get("params", {}),
        result_dict=res,
        artifacts_list=["run.yaml", "environment.json", "stdout.log", "stderr.log",
                         "raw-result.json"],
        status=status,
        invalid_reason=(res.get("failure", {}).get("detail") if "failure" in res else None),
    )
    manifest["run"]["timing"]["started_at"] = started_at
    manifest["run"]["timing"]["finished_at"] = finished_at
    run_common.write_yaml(f"{run_dir}/run.yaml", manifest)
    print("WROTE raw-result.json, environment.json, run.yaml, decision_branch =",
          res.get("decision_branch"))
