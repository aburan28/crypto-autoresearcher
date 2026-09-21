#!/usr/bin/env python3
import json, yaml, hashlib, subprocess, datetime, os
D = "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5"
raw = json.load(open(os.path.join(D, "v1_blind_rederive_output.json")))

def per_layer(pl):
    return {int(k): {"full_rank": v["full_rank"], "top_rank": v["top_rank"],
                     "fall_dim": v["fall_dim"], "n_rows": v["n_rows"]}
            for k, v in pl.items()}

doc = {
 "rederivation": {
  "task_id": "TASK-20260904-642cf5",
  "joint": "V1 blind re-derivation of (d_ff, fall_dim) and the per-layer profile at the deciding cell",
  "phase": "A (blind) -- written before any manifest result block, sidecar or stage0-predictions.yaml was opened",
  "written_at_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
  "derived_from": ("review_plan.blind_rederivation.quantity and .parameters of "
                   "ledger/handoffs/TASK-20260904-642cf5.yaml, plus the run.inputs.parameters "
                   "block of experiments/EXP-PFDR-5726af/runs/RUN-PFDR-5726af-m2-s3/manifest.yaml "
                   "(convention string only). No producer implementation, note or report was read; "
                   "harness/macaulay_fp was neither read nor imported."),
  "conventions_used": {
    "ring": "B = F_p[a_{1,0},a_{1,1},a_{1,2},a_{2,0},a_{2,1},a_{2,2}]/(a_{k,i}^2 - a_{k,i}); 64 squarefree monomials; monomial product = union of variable supports; grading = squarefree degree of the reduced representative",
    "linear_forms": "ell_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}",
    "S3_formula": "S_3(x1,x2,x3) = (x1-x2)^2*x3^2 - 2*((x1+x2)*(x1*x2+a) + 2*b)*x3 + (x1*x2-a)^2 - 4*b*(x1+x2)",
    "generator": "S~ = S_3(ell_1, ell_2, x_R) reduced in B; delta = deg S~ = 4",
    "rows": "PER-LAYER: rows { mu * S~ reduced in B : mu squarefree monomial with deg mu = D - 4 } for D = 4,5,6,7 (1, 6, 15, 20 rows)",
    "full_rank": "rank over F_p of the rows as vectors on all 64 monomial columns",
    "top_rank": "rank over F_p of the same rows restricted to the columns of squarefree degree exactly D",
    "fall_dim": "full_rank(D) - top_rank(D)",
    "d_ff": "least D in {4,...,7} with fall_dim(D) > 0",
    "arithmetic": "exact Gaussian elimination modulo p on Python integers (own code); no floating point; no import of harness/macaulay_fp",
  },
  "self_checks": {
    "C1_boolean_evaluation_identity": "PASS -- for all 12 instances and all 64 digit assignments, S~ evaluated at the assignment equals S_3(x1,x2,x_R) in plain F_p arithmetic with x_k = sum_i 2^i a_{k,i}",
    "C2_top_form": "PASS -- degree-4 part of S~ equals top(ell_1^2)*top(ell_2^2) = (4 a10a11 + 8 a10a12 + 16 a11a12)(4 a20a21 + 8 a20a22 + 16 a21a22) at all 12 instances (9 monomials, leading coefficient 16)",
    "C3_rank_cross_check": "PASS -- rank_mod_p agrees with sympy DomainMatrix(GF(p)).rank() on every row matrix of 4 instances at D = 4..7 (full and top) and on 20 random matrices",
    "script": "v1_selfcheck.py / v1_selfcheck_output.txt",
  },
  "instances_source": ("the 12 (p, curve seed, a, b, target seed, x_R) tuples as DECLARED in "
                       "review_plan.blind_rederivation.parameters; the seed -> (a,b,x_R) derivation "
                       "itself is not independently checkable without the producer's run script, "
                       "which is in blind_from -- see the report's limitation L1"),
  "semaev_arm": [],
  "block_factored_nulls": [],
  "support_matched_nulls": [],
  "summary": {},
  "supplementary_not_part_of_the_assigned_quantity": {
     "description": "40 random non-singular curves with random x_R per prime, same construction, my RNG seed 902642",
     "result": "p = 4099: 40/40 gave (d_ff, fall_dim) = (5, 4) with profile (1,1),(6,2),(15,1); p = 65537: 40/40 identical",
     "script": "v1_supplementary_sweep.py / v1_supplementary_sweep_output.txt",
  },
 }
}

for r in raw["instances"]:
    doc["rederivation"]["semaev_arm"].append({
        "p": r["p"], "curve_seed": r["curve_seed"], "a": r["a"], "b": r["b"],
        "target_seed": r["target_seed"], "x_R": r["x_R"],
        "S_tilde_degree": r["S_tilde_degree"],
        "S_tilde_support_size": r["S_tilde_support_size"],
        "S_tilde_support_by_degree": {int(k): v for k, v in r["S_tilde_support_by_degree"].items()},
        "per_layer": per_layer(r["per_layer"]),
        "d_ff": r["d_ff"], "fall_dim_at_d_ff": r["fall_dim_at_d_ff"],
        "profile_full_top_at_D4_D5_D6": r["profile_full_top_D4_D5_D6"],
        "agrees_with_frozen_prediction_5_4": bool(r["d_ff"] == 5 and r["fall_dim_at_d_ff"] == 4),
    })
for r in raw["block_factored_nulls"]:
    doc["rederivation"]["block_factored_nulls"].append({
        "p": r["p"], "draw": r["draw"], "rng_seed": raw["rng_seed"],
        "construction": "g = q1(a_{1,*}) * q2(a_{2,*}), q_k uniformly random homogeneous degree-2 form in its block, reduced in B (my own RNG, not the producer's null seeds)",
        "q1_coeffs": r["q1_coeffs"], "q2_coeffs": r["q2_coeffs"],
        "g_support_size": r["g_support_size"], "g_degrees_present": r["g_degrees_present"],
        "per_layer": per_layer(r["per_layer"]),
        "d_ff": r["d_ff"], "fall_dim_at_d_ff": r["fall_dim_at_d_ff"],
    })
for r in raw["support_matched_nulls"]:
    doc["rederivation"]["support_matched_nulls"].append({
        "p": r["p"], "curve_seed": r["curve_seed"], "target_seed": r["target_seed"],
        "draw": r["draw"], "rng_seed": raw["rng_seed"],
        "construction": "random polynomial on exactly S~'s monomial support with uniformly random NONZERO coefficients (my own RNG)",
        "support_size": r["support_size"],
        "per_layer": per_layer(r["per_layer"]),
        "d_ff": r["d_ff"], "fall_dim_at_d_ff": r["fall_dim_at_d_ff"],
        "fall_dim_at_D6": r["fall_dim_at_6"],
    })

sem = doc["rederivation"]["semaev_arm"]
doc["rederivation"]["summary"] = {
  "n_instances": len(sem),
  "all_twelve_equal_5_4": all(i["agrees_with_frozen_prediction_5_4"] for i in sem),
  "distinct_d_ff_fall_dim_values": sorted({(i["d_ff"], i["fall_dim_at_d_ff"]) for i in sem}),
  "distinct_profiles_D4_D5_D6": sorted({tuple(map(tuple, i["profile_full_top_at_D4_D5_D6"])) for i in sem}),
  "block_factored_nulls_all": sorted({(n["d_ff"], n["fall_dim_at_d_ff"]) for n in doc["rederivation"]["block_factored_nulls"]}),
  "support_matched_nulls_all": sorted({(n["d_ff"], n["fall_dim_at_d_ff"]) for n in doc["rederivation"]["support_matched_nulls"]}),
  "note_on_one_instance": ("p = 65537, curve seed 1102, target 1 (x_R = 47098) has S~ support 48 rather than 49: "
                           "one coefficient of S~ vanishes modulo p at that instance. It does not change the "
                           "per-layer profile or (d_ff, fall_dim). Recorded because it was observed, not because it matters."),
  "predictions_stated_in_the_task_card": {
     "semaev_arm": "(5, 4)", "block_factored_null": "(5, 4)",
     "support_matched_null": "d_ff = 6 with fall_dim(6) = 14"},
  "nothing_was_adjusted_to_match_a_prediction": True,
}
out = os.path.join(D, "rederivation.yaml")
with open(out, "w") as fh:
    fh.write("# Blind re-derivation (PHASE A) -- TASK-20260904-642cf5, joint V1.\n")
    fh.write("# Values below were computed and written before any producer result artifact was opened.\n")
    yaml.safe_dump(doc, fh, sort_keys=False, default_flow_style=False, width=100)
print("wrote", out)
print("sha256", hashlib.sha256(open(out, "rb").read()).hexdigest())
