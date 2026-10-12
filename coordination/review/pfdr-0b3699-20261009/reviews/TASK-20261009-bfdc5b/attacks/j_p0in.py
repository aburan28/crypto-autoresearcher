"""J-P0IN: P0 input provenance. Recomputes n_b (the P0 RULE), mu_b, D_plan, K_plant, S, the
per-curve mu_model and the height-screen list from the declared inputs, and compares with
design.json and power.json. TASK-20261009-bfdc5b.

Declared inputs used (specification.yaml inputs.p0_inputs_by_path_and_field, as transcribed
there or as recorded in design.json inputs_read): D_30, D_32 (transcribed), localise C_R
(transcribed), sum_mj and sum_mu_model per rung (design.json inputs_read; the mj field
itself is not transcribed and 011cd0 calibration.json is outside this card's inputs).
The rule simulation uses this review's own G-NB-R code (common.py), seeds
SeedSequence([0xBFDC5B, 16, multiplier_index]), ONE family of 20000 replicates per
multiplier (declared reduction from 5 x 20000; Monte Carlo SE reported).
"""
import gzip
import json
import random
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C

OUT = sys.argv[2]
ROOT = "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-p0-design"
design = json.load(open(f"{ROOT}/design.json"))
power = json.load(open(f"{ROOT}/power.json"))
cand = [json.loads(l) for l in gzip.open(f"{ROOT}/curves.jsonl.gz", "rt")]

D_decl = {30: 1.0044757033248082, 32: 1.0233614536015576}          # spec transcription
locCR = {30: 521.3333333333334, 32: 513.6666666666666}             # spec transcription
ir = design["inputs_read"]
rho1 = {b: ir[f"G-NB-R[SUB,TT,4,{b}]"]["sum_mj"] / ir[f"G-NB-R[SUB,TT,4,{b}]"]["sum_mu_model_011cd0_curves"] for b in C.RUNGS}
checks = {}
checks["D_in_equals_transcribed"] = {b: design["D_in_b"][str(b)] == D_decl[b] for b in C.RUNGS}
checks["rho1_P0_equals_sum_mj_over_sum_mu"] = {b: abs(design["rho1_hat_b"][str(b)] - rho1[b]) < 1e-12 for b in C.RUNGS}
D_plan = max(D_decl.values()) * 1.2
checks["D_plan"] = {"recomputed": D_plan, "design": design["D_plan"], "equal": abs(D_plan - design["D_plan"]) < 1e-12}
mu_b = {b: locCR[b] / 2000 for b in C.RUNGS}
checks["mu_b"] = {b: {"recomputed": mu_b[b], "design": design["mu_b_localise"][str(b)],
                      "equal": mu_b[b] == design["mu_b_localise"][str(b)]} for b in C.RUNGS}
not_used = {"rho1": 0.9321981854310321, "D_R_hat": 0.8000000000000003, "D_R_ub95": 1.230769230769231}
checks["no_P0_value_equals_a_not_used_estimate"] = {
    "rho1_hat_b": [design["rho1_hat_b"][k] for k in ("30", "32")], "D_plan": design["D_plan"],
    "estimates.TT4": not_used,
    "any_equal": any(abs(v - w) < 1e-9 for v in list(design["rho1_hat_b"].values()) + [design["D_plan"]]
                     for w in not_used.values())}

# per-curve mu_model and the curve list
by = {b: sorted([c for c in cand if c["bits"] == b], key=lambda c: c["curve"]) for b in C.RUNGS}
mu_bad = 0
for c in cand:
    T = c["s_sub"] ** 2
    if abs(T * (T - 1) / (3 * c["N"]) - c["mu_model"]) > 1e-12 * max(1.0, c["mu_model"]):
        mu_bad += 1
checks["candidate_curves_per_rung"] = {b: len(by[b]) for b in C.RUNGS}
checks["mu_model_recompute_mismatches"] = mu_bad
n_b = design["final_n_b"]
dkeys = [(c["bits"], c["curve"], c["p"], c["a"], c["b"], c["N"], c["s_sub"], c["mu_model"], c["x0"]) for c in design["curves"]]
ckeys = [(c["bits"], c["curve"], c["p"], c["a"], c["b"], c["N"], c["s_sub"], c["mu_model"], c["x0"]) for b in C.RUNGS for c in by[b][:n_b]]
checks["design_curves_equal_first_n_b_candidates"] = dkeys == ckeys
K = {b: round(0.15 * n_b * mu_b[b]) for b in C.RUNGS}
checks["K_plant"] = {b: {"recomputed": K[b], "design": design["K_plant_b"][str(b)]} for b in C.RUNGS}
S_ok = {}
for b in C.RUNGS:
    cs = [c["curve"] for c in by[b][:n_b]]
    S_ok[b] = sorted(random.Random(f"plant-target|EXP-PFDR-0b3699|{b}").sample(cs, n_b)[:K[b]]) == design["S"][str(b)]
checks["S_equal"] = S_ok
hs = {b: [c["curve"] for c in by[b][:n_b] if c["height_screen_hits"]] for b in C.RUNGS}
checks["height_screen_from_candidates"] = {b: {"list": hs[b], "design": design["height_screen"][str(b)]} for b in C.RUNGS}


# ---------------------------------------------------------------- the P0 RULE (n_b)
class D0:
    pass


def model_for(nb):
    d = {"bits": np.array([b for b in C.RUNGS for _ in range(nb)]),
         "mu_model": np.array([c["mu_model"] for b in C.RUNGS for c in by[b][:nb]])}
    fit = {b: {"rho1_hat": rho1[b], "D": D_plan} for b in C.RUNGS}
    return C.Model(d, fit)


rule = []
for mi, mult in enumerate((1.0, 1.25, 1.5)):
    nb = int(round(3400 * mult))
    mdl = model_for(nb)
    rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 16, mi]))
    CR, V = C.random_bank(mdl, rng, 20000)
    z0 = C.z_from(mdl.null_total(rng, 20000).astype(float), CR, V)
    tA = float(np.quantile(z0, 0.99))
    zD = (mdl.null_total(rng, 20000) - mdl.null_total(rng, 20000)) / np.sqrt(2 * V)
    tD = float(np.quantile(zD, 0.95))
    pw = {}
    for planting in ("poisson", "compound"):
        CA = mdl.struct_total(rng, 20000, 1.10, planting=planting).astype(float)
        pw[planting] = float((C.z_from(CA, CR, V) > tA).mean())
    gov = min(pw.values())
    CA = mdl.struct_total(rng, 20000, 1.10).astype(float)
    CM = mdl.null_total(rng, 20000).astype(float)
    pc = float(((CA - CM) / np.sqrt(2 * V) > tD).mean())
    ev = next(r for r in design["rule_evaluations"] if r["multiplier"] == mult)
    rule.append({"multiplier": mult, "n_b": nb, "t_A_plan": tA, "t_Delta_plan": tD, "power_1.10": pw,
                 "governing": gov, "governing_mc_se": float(np.sqrt(gov * (1 - gov) / 20000)),
                 "power_contrast": pc, "meets": bool(gov >= 0.90 and pc >= 0.80),
                 "producer": {"t_A_plan": ev["t_A_plan"], "governing": ev["power_1.10"]["governing"],
                              "contrast": ev["power_contrast"]["power"], "meets": ev["meets"]}})
    print(rule[-1], flush=True)
chosen = next((r for r in rule if r["meets"]), None)
checks["n_b_rule"] = {"evaluations": rule, "chosen_n_b": chosen["n_b"] if chosen else "none of 1.0..1.5",
                      "design_final_n_b": n_b, "equal": bool(chosen and chosen["n_b"] == n_b),
                      "replicates": "1 family x 20000 per multiplier (declared reduction)"}
res = {"task": "TASK-20261009-bfdc5b", "joint": "J-P0IN", "checks": checks,
       "static_reads": {
           "design_a.py": "no file read except the engine modules curve.py and factor_base.py loaded by path; CLI args only; writes curves.jsonl.gz",
           "analyze_a.py p0 (lines 581-750, 529-578)": [
               "--curves curves.jsonl.gz: every key of every record (read_jsonl)",
               "--arch-calibration 011cd0 calibration.json: generators['G-NB-R'].groups[*].key/.curves/.mj/.D (l.597-605); PC_NULL.known_null_band_cells['known_null_sub|TT4|band'].C_R/.sum_s2/.C_A/.curves_used (l.562-574)",
               "--arch-analysis 011cd0 analysis.json: A_INT['small_x|TT4|band'].SE/.q.q_one_sided_095/.upper95_one_sided/.kappa_rel (l.609-612), recorded only",
               "--arch-design 011cd0 design.json: parsed in full by json.load (l.591); ONLY curves[*] accessed: bits, curve, sizes['4']['s_sub'], N (l.598, 602) and p, a, b (l.631); no access to estimates or any other top-level key",
               "--localise smallx-tt4-localise.json: ['small_x|30'|'small_x|32'].C_R and .curves (l.613, 675)",
               "--sizing replication-sizing.json: cells['small_x|TT4|band'] two power fields (l.614-616), recorded only; design.json gaussian_planning_figures are literals 5244/6801 equal to them",
               "--redteam red-team-report.yaml: red_team_report.joints.J4.computation.d_dispersion (l.617), recorded only; the multiplier is the literal RHO_D_UPPER = 1.307 (l.75), equal to the upper CI in that string",
               "--arch-jobs 011cd0 R12 jobs 4-b30-*, 4-b32-*: rows.jsonl.gz (mode, m, arm, status, N, bits, curve) and harvest-rows.jsonl.gz of the four null arms (P0X-A, l.529-578)"],
           "run_jobs.py / reproduce_check.py": "no reference to 'estimates' or to 011cd0 design.json fields (rg)"}}
C.jdump(res, OUT)
print(json.dumps(checks, indent=1, default=str)[:5000])
