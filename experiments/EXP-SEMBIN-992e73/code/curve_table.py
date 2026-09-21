#!/usr/bin/env python3
"""Per-curve Semaev-2015 cost table for the Certicom binary challenge curves
and the FIPS binary curves, by direct evaluation of the FROZEN, already-accepted
joint-balance instrument (EXP-SEMBIN-81dc96, RUN-SEMBIN-aa5161).

No new cost model is written here. The only new thing is WHICH n are evaluated.

CONVENTION. The frozen run's own crossover figures use
solve="block_n4w", use_stage1_only=True, constrain_t_eq_m=True -- Section
4.5.2's own convention, since it observes stage 1 dominates. That convention is
reproduced EXACTLY here (verified cell-by-cell against curve_charged), and the
joint (m,t) total-cost convention is reported beside it, not instead of it.
"""
import json
import sys
import math
import importlib.util
import hashlib
import pathlib

SRC = pathlib.Path("experiments/EXP-SEMBIN-81dc96/code/joint_balance.py")
spec = importlib.util.spec_from_file_location("jb", SRC)
jb = importlib.util.module_from_spec(spec)
sys.modules["jb"] = jb  # dataclasses resolves __module__ through sys.modules
spec.loader.exec_module(jb)

INSTRUMENT_SHA256 = hashlib.sha256(SRC.read_bytes()).hexdigest()

# Field extension degrees, READ FROM FROZEN SOURCES, not recalled.
#   Certicom: inputs/BAILEY-2009-541-ECC2K130/talk-35minutes_text.md, the
#   level-1 and level-2 challenge tables. The "Bits" column is the field
#   extension degree (ECC2K-130 at 131 matches the independently known
#   GF(2^131)). NOTE: the 359-bit level-2 entry is ECCp-359, a PRIME-field
#   curve, so there is NO binary Certicom challenge at 359.
#   FIPS: inputs/SAFECURVES-20260825/specs/sp800-186.txt, "Curve K-163" ...
#   "Curve K-571"; the B- family shares each degree (sect163r2 ... sect571r1 in
#   inputs/SAFECURVES-20260825/specs/sec2-v2.txt).
CURVES = [
    (97,  "Certicom", "ECC2K-95, ECC2-97"),
    (109, "Certicom", "ECC2K-108, ECC2-109"),
    (131, "Certicom", "ECC2K-130, ECC2-131"),
    (163, "both",     "ECC2K-163, ECC2-163; FIPS K-163, B-163"),
    (191, "Certicom", "ECC2-191"),
    (233, "FIPS",     "K-233, B-233"),
    (239, "Certicom", "ECC2K-238, ECC2-238"),
    (283, "FIPS",     "K-283, B-283"),
    (409, "FIPS",     "K-409, B-409"),
    (571, "FIPS",     "K-571, B-571"),
]

# vOW coherent baseline, H-SEMBIN-97ea23 (status: supported), heuristic
# HEUR-VOW-CURVE (status: unvalidated): total work W = 0.886 * 2^{n/2}.
VOW_CONST_BITS = math.log2(0.886)

PAPER = jb.Model(solve="block_n4w", charge_cofactor=True)
PAPER_ABS = jb.Model(solve="block_n4w", charge_cofactor=False)


def stage1_only_min(n, mo, t_eq_m, m_hi=30):
    """Section 4.5.2's convention: minimize STAGE 1 alone over the grid."""
    best = None
    for m in range(2, min(m_hi, n) + 1):
        ts = [m] if t_eq_m else range(2, m + 1)
        for t in ts:
            s1, _ = jb.stage_costs(n, m, t, mo)
            if best is None or s1 < best[0]:
                best = (s1, m, t)
    return {"log2_cost": round(best[0], 3), "m_star": best[1], "t_star": best[2],
            "at_m_grid_cap": best[1] == min(m_hi, n)}


# ---- reproduction check against the frozen run, before anything is reported --
frozen = json.load(open(
    "experiments/EXP-SEMBIN-81dc96/runs/RUN-SEMBIN-aa5161/raw-result.json"))
fc = {c["n"]: c for c in frozen["correction_2_charged_cofactor"]["curve_charged"]}
repro = []
for n in (250, 300, 302, 400, 571):
    if n not in fc:
        continue
    mine = stage1_only_min(n, PAPER, t_eq_m=True)
    repro.append({"n": n, "frozen_log2": fc[n]["log2_cost"],
                  "mine_log2": mine["log2_cost"],
                  "frozen_m": fc[n]["m"], "mine_m": mine["m_star"],
                  "agrees": abs(fc[n]["log2_cost"] - mine["log2_cost"]) < 1e-3
                            and fc[n]["m"] == mine["m_star"]})
assert all(r["agrees"] for r in repro), repro

# ---- the defect in the frozen run's own derived absorbed crossover ----------
absorbed_floor_probe = []
for n_lo in (20, 100, 250):
    c = jb.crossover(PAPER_ABS, n_lo=n_lo, n_hi=max(n_lo + 60, 300),
                     use_stage1_only=True, constrain_t_eq_m=True)
    absorbed_floor_probe.append({"n_lo": n_lo, "crossover_n": c["crossover_n"],
                                 "first_cell_margin_bits":
                                     c["curve"][0]["margin_bits"]})
charged_floor_probe = []
for n_lo in (20, 250):
    c = jb.crossover(PAPER, n_lo=n_lo, n_hi=650,
                     use_stage1_only=True, constrain_t_eq_m=True)
    charged_floor_probe.append({"n_lo": n_lo, "crossover_n": c["crossover_n"]})

rows = []
for n, family, names in CURVES:
    paper_conv = stage1_only_min(n, PAPER, t_eq_m=True)
    joint_s1 = stage1_only_min(n, PAPER, t_eq_m=False)
    joint_tot = jb.optimize(n, PAPER)
    rho = n / 2.0
    vow = rho + VOW_CONST_BITS
    rows.append({
        "n": n, "family": family, "curves": names,
        "log2_rho_naive": rho,
        "log2_rho_vow_total_work": round(vow, 3),
        "paper_convention_t_eq_m_stage1_only": {
            **paper_conv,
            "margin_vs_naive_rho_bits": round(paper_conv["log2_cost"] - rho, 3),
            "margin_vs_vow_bits": round(paper_conv["log2_cost"] - vow, 3),
            "beats_naive_rho": paper_conv["log2_cost"] < rho,
        },
        "joint_mt_stage1_only": {
            **joint_s1,
            "margin_vs_naive_rho_bits": round(joint_s1["log2_cost"] - rho, 3),
            "t_star_below_m_star": joint_s1["t_star"] < joint_s1["m_star"],
        },
        "joint_mt_total_cost": {
            "log2_cost": round(joint_tot["log2_total"], 3),
            "m_star": joint_tot["m_star"], "t_star": joint_tot["t_star"],
            "at_m_grid_cap": joint_tot["m_star"] == min(30, n),
            "margin_vs_naive_rho_bits":
                round(joint_tot["log2_total"] - rho, 3),
        },
    })

out = {
    "what_this_is": (
        "Per-curve evaluation of the frozen EXP-SEMBIN-81dc96 joint (m,t) balance "
        "at the field extension degrees of the Certicom binary challenge curves and "
        "the FIPS binary curves. DERIVATION ONLY: no curve, no factor base, no "
        "Groebner computation, no measurement, and no security statement about any "
        "curve in either direction."),
    "instrument": {
        "path": str(SRC), "sha256": INSTRUMENT_SHA256,
        "accepted_by_run": "RUN-SEMBIN-aa5161", "experiment": "EXP-SEMBIN-81dc96",
    },
    "reproduction_check_against_frozen_run": repro,
    "defect_found_in_frozen_derived_figure": {
        "figure": "correction_2_charged_cofactor.crossover_cofactor_absorbed = 250, "
                  "and the derived shift_upward_from_charging = 52",
        "finding": "Both are SEARCH-FLOOR ARTIFACTS, not measurements. The absorbed "
                   "reading charges NO solve cost at all (charge_cofactor=False sets "
                   "solve=0), so its stage-1 cost is below 2^{n/2} at every n in "
                   "range; crossover() therefore returns its own n_lo whatever that "
                   "is. The probe below shows it returning 20, 100 and 250 for the "
                   "three floors tried.",
        "absorbed_floor_probe": absorbed_floor_probe,
        "charged_is_robust": charged_floor_probe,
        "consequence": "The charged crossover of 302 stands and is floor-independent. "
                       "The claim that charging the cofactor moves the crossover UP BY "
                       "52 is unsupported: there is no absorbed crossover in range to "
                       "shift from. The honest statement is that the absorbed reading "
                       "has no crossover because it prices no solving.",
        "not_edited": "RUN-SEMBIN-aa5161 is immutable and is NOT modified. This is "
                      "reported for a superseding correction record.",
    },
    "conditional_on": [
        "Semaev 2015 Assumption 1 (d_F4 <= 4). EV-ICPERF-a8080e reports it "
        "reproduces at every cell n <= 21 on the subspace family it actually names, "
        "and that this program's existing ladder measured a different family. "
        "Nothing is known at any n in this table.",
        "Semaev's published yield law eq. (11).",
        "HEUR-VOW-CURVE (unvalidated) for the vOW total-work column.",
    ],
    "rows": rows,
}
json.dump(out, sys.stdout, indent=1)
print()
