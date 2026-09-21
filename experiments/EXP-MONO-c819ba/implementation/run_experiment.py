#!/usr/bin/env python3
"""
EXP-MONO-c819ba executor: verify Var_R N_m(R) = N^-2 sum_{chi!=1}|Shat(chi)|^{2m}
and measure the real x-coordinate factor base's character bias against matched
random symmetric nulls, with subgroup/coset-union positive controls.

Usage: python3 run_experiment.py <master_seed> <output_dir>
"""
import sys
import os
import json
import hashlib
import math
import time
import platform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fields import ec_add, ec_scal, legendre  # noqa
from curve import (
    construct_prime, curve_discriminant_ok, count_E_points, count_Z,
    enumerate_points, group_structure, build_coordinate_map,
    factor_base_x_coords, ConstructionFailure,
)
from groupstate import CurveState
from panel import build_panel, PANEL_DOMAIN
from conv import (
    convolution_tower, exact_stats, character_spectrum,
    var_from_character_side, max_C, indicator_grid,
)
from controls import draw_symmetric_null, subgroup_control, coset_union_control


def sha256_of(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# STAGE 0: exact identity gate on one frozen fixture cell (chosen by the
# Executor per the contract's own explicit permission: "you choose concrete
# small values, e.g. p=101 with some symmetric FB").
# ---------------------------------------------------------------------------
FIXTURE_P, FIXTURE_A, FIXTURE_B = 101, 1, 1


def stage0_fixture_gate():
    assert curve_discriminant_ok(FIXTURE_A, FIXTURE_B, FIXTURE_P)
    cs = CurveState(FIXTURE_P, FIXTURE_A, FIXTURE_B)
    N = cs.N
    F = N // 2
    fb = cs.fb_full[:F]
    fbset = set(fb)
    symmetric = all((x, (-y) % FIXTURE_P) in fbset for (x, y) in fb)
    coords = cs.coords_of(fb)

    tower = convolution_tower(coords, cs.n1, cs.n2, 2)
    N1, N2 = tower[1], tower[2]

    # m=1: Var must equal F(N-F)/N^2 EXACTLY (Parseval, holds for every subset).
    st1 = exact_stats(N1, N, F, 1)
    var1_formula = (F * (N - F)) / (N * N)
    m1_exact_match = abs(st1["var_ordered_exact"] - var1_formula) < 1e-12

    # m=2: sum_R N_2(R)^2 = F^4/N + (1/N) sum_{chi!=1} |Shat(chi)|^4
    Shat = character_spectrum(coords, cs.n1, cs.n2)
    sumsq_N2 = int((N2.astype(object) ** 2).sum())
    rhs_char = (F ** 4) / N + var_from_character_side(Shat, N, 2) * N  # since Var2 = (1/N^2)*sum|Shat|^4(nontriv)
    # rearrange properly: Var2 = (1/N^2) sum_{chi!=1}|Shat|^4  => sum_{chi!=1}|Shat|^4 = Var2 * N^2
    sum_nontrivial_4 = var_from_character_side(Shat, N, 2) * (N ** 2)
    additive_quadruple_rhs = (F ** 4) / N + sum_nontrivial_4 / N
    additive_quadruple_lhs = sumsq_N2
    m2_rel_residual = abs(additive_quadruple_lhs - additive_quadruple_rhs) / additive_quadruple_lhs

    st2 = exact_stats(N2, N, F, 2)
    var2_char = var_from_character_side(Shat, N, 2)
    m2_var_rel_residual = abs(st2["var_ordered_exact"] - var2_char) / st2["var_ordered_exact"]

    result = {
        "fixture": {"p": FIXTURE_P, "A": FIXTURE_A, "B": FIXTURE_B, "N": N,
                    "n1": cs.n1, "n2": cs.n2, "F": F, "fb_symmetric": symmetric},
        "m1": {"var_exact_integer_side": st1["var_ordered_exact"],
               "var_formula_F(N-F)/N^2": var1_formula,
               "match": m1_exact_match},
        "m2_additive_quadruple": {
            "sum_R_N2(R)^2_exact": additive_quadruple_lhs,
            "F^4/N_plus_sum_nontrivial_Shat^4_over_N": additive_quadruple_rhs,
            "relative_residual": m2_rel_residual,
        },
        "m2_variance_identity": {
            "var_exact_integer_side": st2["var_ordered_exact"],
            "var_character_side_float": var2_char,
            "relative_residual": m2_var_rel_residual,
        },
        "gate_pass": bool(m1_exact_match and m2_rel_residual < 1e-9 and m2_var_rel_residual < 1e-9),
    }
    return result


# ---------------------------------------------------------------------------
# STAGE 1: verbatim quotations of the seven relayed records (gathered by the
# Executor by direct repository read; see implementation.md for the search).
# ---------------------------------------------------------------------------
STAGE1_QUOTATIONS = {
    "KN-FIND-007": {
        "path": "knowledge/findings/KN-FIND-007.md",
        "obtained": True,
        "quote_mean_formula": (
            "Let `G` be a finite abelian group of order `N` and `D ⊆ G \\ {0}` a "
            "factor base of `B` distinct elements. For `m ≥ 1` and `r ∈ G`, let "
            "`c_D(r)` be the number of size-`m` multisets from `D` summing to `r`. Then\n\n"
            "```\nsum over r in G of c_D(r)  =  binomial(B + m - 1, m)\n```\n\n"
            "exactly, because every size-`m` multiset sums to exactly one target. Hence "
            "the mean per-target decomposition yield is\n\n"
            "```\nE_r[c_D(r)] = binomial(B + m - 1, m) / N\n```\n\n"
            "for **every** base of size `B`, independently of how `D` is chosen."
        ),
        "convention_finding": (
            "KN-FIND-007's conservation mean is C(B+m-1,m)/N, the UNORDERED-MULTISET "
            "mean (c_D(r) counts multisets, i.e. unordered selections with repetition), "
            "NOT literally F^m/N (the ORDERED-tuple mean this contract's (I1) proves). "
            "These are NOT related by a single, m-independent multiplicative convention "
            "factor: C(B+m-1,m) = B(B+1)...(B+m-1)/m! differs from B^m/m! by lower-order "
            "terms in B that do not vanish for finite B (they agree only asymptotically "
            "as B -> infinity with m fixed). H-MONO-663fb4 mechanism step (4) already "
            "anticipated exactly this gap, calling F^m/N 'the ordered-convention ANALOGUE' "
            "of KN-FIND-007's multiset mean, not asserting equality, and pre-committing to "
            "report both conventions at every cell for this reason."
        ),
        "stage1_disposition": (
            "This does NOT trigger the Stage-1 stop condition, because that condition "
            "asks whether the mean is 'the ordered mean F^m/N under any reasonable "
            "convention' -- and this contract's own Stage 0 gate proves (I1) mean_R "
            "N_m(R) = F^m/N as an EXACT identity for the ORDERED convention, independent "
            "of and prior to reading KN-FIND-007. KN-FIND-007 is a DIFFERENT, "
            "self-consistent conservation identity for the MULTISET convention "
            "(C(B+m-1,m)/N), not a contradiction of (I1); the two are related but not "
            "identical, exactly as mechanism step (4) flagged. The identification of "
            "N_m with 'the relation event' therefore stands for the ORDERED convention "
            "this contract's (I1)/(I2)/(I3) are stated in, and the multiset convention "
            "reported at every cell (N_m(R)/m!, this contract's declared combinatorial "
            "factor) is an approximation to KN-FIND-007's exact multiset count that "
            "becomes exact only when no repeated-element m-tuple sums to the same "
            "target -- a discrepancy reported as a finding, not silently reconciled."
        ),
    },
    "KN-FIND-d4f820": {
        "path": "knowledge/findings/KN-FIND-d4f820.md",
        "obtained": True,
        "quote": (
            "The constant C = max|hat{1_F}(k)| / sqrt(B) (full k-range DFT):\n\n"
            "| p | C (mean) | log2(p) |\n|---|---------|---------|\n"
            "| 1009 | 3.0 | 10.0 |\n| 4001 | 3.5 | 11.9 |\n| 9001 | 3.7 | 13.1 |\n"
            "| 50021 | 3.84 | 15.6 |\n\n"
            "**Best fit: C(p) ~ p^{0.055}** (very slow power law, consistent with "
            "O((log p)^{0.5}) or O(log log p))."
        ),
        "alpha_value": "0.055 (mean C over random curves, small-x factor base, full-range DFT)",
    },
    "KN-FIND-4c9e71": {
        "path": "knowledge/findings/KN-FIND-4c9e71.md",
        "obtained": True,
        "quote": (
            "Adversarial maximum of C = max_k |hat{1_F}(k)| / sqrt(B) across all tested "
            "random curves:\n\n| p | n measurements | max C | mean C |\n|---|---|---|---|\n"
            "| 1009 | 152 | 3.90 | 2.99 |\n| 4001 | 26 | 3.87 | 3.47 |\n| 9001 | 12 | 4.11 | 3.63 |\n\n"
            "**The adversarial maximum is BOUNDED ~ 4 and NOT growing significantly with p.**\n"
            "No counter-example to H-PSEUDO found in 190+ measurements.\n\n"
            "## CORRECTION (BATCH-107)\n\nAt p=50021: max C = 5.182 (6 measurements), "
            "consistent with p^{0.079} scaling (prediction: 5.31). The adversarial max "
            "DOES grow with p, following the same C ~ p^{0.079} as the mean. Earlier claim "
            "of \"O(1) max C\" was premature (too narrow p range: 1009..9001 spans only 9x).\n\n"
            "**Revised finding**: BOTH mean C AND adversarial max C scale as ~ p^{0.079}."
        ),
        "alpha_value": (
            "0.079 (adversarial-max C, AFTER the BATCH-107 self-correction superseding "
            "the record's own earlier, in-document 'O(1) max C' claim)"
        ),
    },
    "DEC-20260804-0a4bc2": {
        "path": "ledger/decisions/DEC-20260804-0a4bc2.yaml",
        "obtained": True,
        "quote": (
            "H-PSEUDO-83817b REVISED: The empirical evidence now supports the STRONGER "
            "form: C = O(1) (constant, not growing with p), not just C = O(p^{0.079}).\n\n"
            "Evidence:\n- Mean C ~ p^{0.079} (from BATCH-073..079 random curve measurements)\n"
            "- Adversarial max C ~ 4 across p=1009..9001 (this batch + BATCH-104)\n"
            "- The adversarial max is NOT growing with p (3.90 -> 3.87 -> 4.11)\n\n"
            "H-PSEUDO with C <= 5 (universal constant) is STRONGLY empirically supported."
        ),
        "max_c_verdict": "O(1), constant ~4, dated 2026-08-04, batch 105/104 data only (p up to 9001).",
    },
    "DEC-20260804-4f3a3b": {
        "path": "ledger/decisions/DEC-20260804-4f3a3b.yaml",
        "obtained": True,
        "quote": (
            "KN-FIND-4c9e71 promoted. H-PSEUDO-83817b updated: predictions now state "
            "adversarial max C ~ O(1) ~= 4 (revised from C ~ p^{0.079}).\n\n"
            "THE CENTRAL REMAINING QUESTION: does the adversarial max C stay bounded at "
            "p=50021? ... This measurement would discriminate."
        ),
        "max_c_verdict": (
            "Same as DEC-20260804-0a4bc2 (O(1)/~4), BUT this decision explicitly flags "
            "the p=50021 measurement as the discriminating test still to be run -- and "
            "KN-FIND-4c9e71's OWN 'CORRECTION (BATCH-107)' section (quoted above) reports "
            "that test came back at max C=5.182, consistent with GROWTH (p^0.079), "
            "superseding the O(1) verdict this decision records. Both DEC-20260804-0a4bc2 "
            "and DEC-20260804-4f3a3b therefore record a verdict (O(1)) that the promoted "
            "finding's own later correction (still within the same KN-FIND-4c9e71 record) "
            "reverses; neither decision record itself was updated to reflect the "
            "correction. Reported as-is, not resolved, per this contract's Stage-1 scope."
        ),
    },
    "DEC-20260804-53c89f": {
        "path": "ledger/decisions/DEC-20260804-53c89f.yaml",
        "obtained": True,
        "quote": (
            "CORRECTED EMPIRICAL DESCRIPTION: |hat{1_F}(k)| ~ sqrt(B) * p^{0.079} (not "
            "sqrt(N) * constant as previously hypothesized in BATCH-080). This means "
            "C = max|hat|/sqrt(B) ~ p^{0.079} is genuine p-growth, not a B_frac "
            "normalization artifact."
        ),
        "max_c_verdict": (
            "'genuine p-growth' (p^{0.079}), directly contradicting DEC-20260804-0a4bc2 "
            "and DEC-20260804-4f3a3b's 'C = O(1)' verdict recorded the SAME DAY "
            "(2026-08-04). This is the two-way max-C disagreement H-MONO-663fb4 mechanism "
            "step (7) reports and does not resolve."
        ),
    },
    "DEC-20260804-f320c2": {
        "path": "ledger/decisions/DEC-20260804-f320c2.yaml",
        "obtained": True,
        "quote": (
            "BGS spectral gap direction: CLOSED with named obstruction (abelian spectral "
            "gap obstruction: E(F_p) ≅ Z/N is cyclic abelian, BGS requires non-abelian; "
            "even if a spectral gap existed, birthday collision threshold is orthogonal "
            "to mixing time)."
        ),
        "spectral_gap_scope_note": (
            "This record closes the Cay(Z/N,S) spectral-gap ROUTE for |S|=O(1) generating "
            "sets, on the abelian-group obstruction; it does not itself state the |S|=O(1) "
            "scope boundary in those words (that paraphrase in H-MONO-663fb4 mechanism "
            "step (7), attributed to this record as '(R2) closes the spectral-gap route "
            "for Cay(Z/N,S) at |S|=O(1)', is a reasonable reading of the abelian_spectral_"
            "gap_obstruction clause but is NOT a verbatim phrase in this record -- the "
            "record's own words are quoted above in full for independent judgement)."
        ),
    },
}


def write_stage1_file(path):
    with open(path, "w") as f:
        f.write("# Stage-1 verbatim quotations (EXP-MONO-c819ba)\n\n")
        for k, v in STAGE1_QUOTATIONS.items():
            f.write(f"## {k}\n\npath: {v['path']}\nobtained: {v['obtained']}\n\n")
            for kk, vv in v.items():
                if kk in ("path", "obtained"):
                    continue
                f.write(f"### {kk}\n\n{vv}\n\n")
            f.write("\n")


def stage1_termination_check():
    """Per stopping_rules: stop only if the mean is NOT F^m/N under ANY reasonable
    convention. Judgment recorded above (KN-FIND-007 disposition): NOT triggered,
    because (I1) is independently, exactly proved for the ordered convention in
    Stage 0, and KN-FIND-007's multiset convention is a distinct, non-contradictory
    conservation identity, exactly as H-MONO-663fb4 mechanism step (4) anticipated."""
    return {"terminates": False,
            "reason": STAGE1_QUOTATIONS["KN-FIND-007"]["stage1_disposition"]}


# ---------------------------------------------------------------------------
# STAGE 2: exact identity at m=3,4 on >=2 panel curves.
# ---------------------------------------------------------------------------
def stage2_identity_check(cs, F, curve_role):
    fb = cs.fb_full[:F]
    coords = cs.coords_of(fb)
    tower = convolution_tower(coords, cs.n1, cs.n2, 4)
    Shat = character_spectrum(coords, cs.n1, cs.n2)
    out = {"role": curve_role, "p": cs.p, "N": cs.N, "F": F, "cells": {}}
    for m in (3, 4):
        st = exact_stats(tower[m], cs.N, F, m)
        var_char = var_from_character_side(Shat, cs.N, m)
        rel_res = abs(st["var_ordered_exact"] - var_char) / st["var_ordered_exact"] if st["var_ordered_exact"] != 0 else 0.0
        out["cells"][f"m={m}"] = {
            "var_exact_integer": st["var_ordered_exact"],
            "var_character_float": var_char,
            "relative_residual": rel_res,
            "within_1e-9": rel_res < 1e-9,
        }
    return out


# ---------------------------------------------------------------------------
# Ladder construction: "first F x-coordinates in increasing scan order" applied
# UNIFORMLY to all four ladder rungs {N/16,N/8,N/4,N/2} as prefixes of the
# full QR-x point stream, grouped in (x,y),(x,-y) pairs so every rung stays
# exactly symmetric. See implementation.md interpretation note 1 for why the
# literal "full factor base retains every QR x" text (which alone would give
# F ~ N, not N/2) is read this way.
# ---------------------------------------------------------------------------
def ladder_fb(cs, denom):
    target = max(2, cs.N // denom)
    target -= target % 2  # force even, so the (x,y)/(x,-y) pairing stays exact
    return cs.fb_full[:target]


def cell_stats(coords, cs, F, m_list=(1, 2, 3, 4)):
    tower = convolution_tower(coords, cs.n1, cs.n2, max(m_list))
    Shat = character_spectrum(coords, cs.n1, cs.n2)
    Cval, _ = max_C(Shat)
    per_m = {}
    for m in m_list:
        st = exact_stats(tower[m], cs.N, F, m)
        var_char = var_from_character_side(Shat, cs.N, m)
        rel_res = (abs(st["var_ordered_exact"] - var_char) / st["var_ordered_exact"]
                   if st["var_ordered_exact"] != 0 else 0.0)
        fact_m = math.factorial(m)
        per_m[m] = {
            "var_ordered": st["var_ordered_exact"],
            "var_multiset": st["var_ordered_exact"] / (fact_m ** 2),
            "mean_ordered": st["mean_ordered"],
            "mean_multiset": st["mean_ordered"] / fact_m,
            "max_rel_dev": st["max_rel_dev_ordered"],
            "var_character_float": var_char,
            "l1_relative_residual": rel_res,
        }
    return {"F": F, "C": Cval, "C_over_F": Cval / F if F else None, "per_m": per_m}


def main():
    t_start = time.time()
    master_seed = int(sys.argv[1])
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    sampling_domain = f"{PANEL_DOMAIN}/run-{master_seed}"

    result = {"master_seed": master_seed, "sampling_domain": sampling_domain,
              "panel_domain": PANEL_DOMAIN}

    # ---------------- STAGE 0 ----------------
    stage0 = stage0_fixture_gate()
    result["stage0"] = stage0
    if not stage0["gate_pass"]:
        result["halted_at"] = "stage0"
        result["reason"] = "Stage-0 exact identity gate failed; per stopping_rules, no further compute spent."
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 1 ----------------
    write_stage1_file(os.path.join(out_dir, "stage1_quotations.md"))
    stage1 = stage1_termination_check()
    result["stage1"] = {"quotations_file": "stage1_quotations.md", "termination_check": stage1}
    if stage1["terminates"]:
        result["halted_at"] = "stage1"
        _finish(result, out_dir, t_start)
        return

    # ---------------- PANEL CONSTRUCTION ----------------
    panel = build_panel()
    result["panel"] = {"prime_transcript_summary": {b: panel["prime_transcript"][b]["p"]
                                                     for b in panel["prime_transcript"]},
                        "curves": panel["curves"]}

    curve_states = {}
    construction_errors = {}
    for c in panel["curves"]:
        role = c["role"]
        try:
            cs = CurveState(c["p"], c["A"], c["B"])
            curve_states[role] = cs
        except ConstructionFailure as e:
            construction_errors[role] = str(e)
    result["panel"]["construction_errors"] = construction_errors
    result["panel"]["group_structures"] = {
        role: {"N": cs.N, "n1": cs.n1, "n2": cs.n2,
               "fb_full_size": len(cs.fb_full), "fb_full_symmetric": cs.fb_full_symmetric,
               "excluded_zero": cs.excluded_zero}
        for role, cs in curve_states.items()
    }

    # ---------------- SUBGROUP-AVAILABILITY PRECONDITION ----------------
    subgroup_capable = [role for role, cs in curve_states.items() if cs.n2 % 4 == 0]
    result["subgroup_availability"] = {
        "capable_roles": subgroup_capable,
        "precondition_met": len(subgroup_capable) >= 2,
        "note": ("Subgroup control needs 4 | n2 (the larger invariant factor of "
                 "E(F_p) = Z/n1 x Z/n2). H_k = {(a,b): b == 0 mod k} in that "
                 "coordinate system has order n1*(n2/k) = N/k EXACTLY for any k | n2, "
                 "regardless of cyclic/non-cyclic structure. NOTE: the image of the "
                 "scalar mult-by-k map is NOT used for this, because for a NON-cyclic "
                 "group (n1>1 even) its kernel is the full k-torsion (order "
                 "gcd(k,n1)*gcd(k,n2), which can exceed gcd(k,N)), so that image can be "
                 "SMALLER than N/k -- caught during implementation via a wrong h=N/4 "
                 "value returned for a requested h=N/2 subgroup on curves with even n1; "
                 "see implementation.md interpretation note 2."),
    }
    if len(subgroup_capable) < 2:
        result["stage4_subgroup_and_coset_controls"] = (
            "SKIPPED: fewer than two panel curves have 4 | n2 "
            f"(capable: {subgroup_capable}).")
        result["interpretation_note"] = "No arm may be interpreted per stopping_rules."
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 2 ----------------
    stage2_roles = subgroup_capable[:2] if len(subgroup_capable) >= 2 else (
        list(curve_states.keys())[:2])
    stage2_out = []
    for role in stage2_roles:
        cs = curve_states[role]
        F = max(2, cs.N // 2)
        F -= F % 2
        stage2_out.append(stage2_identity_check(cs, F, role))
    result["stage2"] = stage2_out
    stage2_pass = all(cell["within_1e-9"] for r in stage2_out for cell in r["cells"].values())
    result["stage2_gate_pass"] = stage2_pass

    # ---------------- STAGE 4 PRE-TREATMENT: nulls + positive controls ----------
    pretreatment = {"nulls": {}, "subgroup_controls": {}, "coset_union_controls": {},
                     "calibration": {}}
    F_LADDER_DENOMS = {"N/16": 16, "N/8": 8, "N/4": 4, "N/2": 2}
    N_NULL_DRAWS = 30

    for role, cs in curve_states.items():
        pretreatment["nulls"][role] = {}
        for label, denom in F_LADDER_DENOMS.items():
            fb = ladder_fb(cs, denom)
            F = len(fb)
            draws = []
            for di in range(N_NULL_DRAWS):
                pts = draw_symmetric_null(cs, F, sampling_domain, m=0, draw_index=di)
                draws.append([list(p) if p is not None else None for p in pts])
            pretreatment["nulls"][role][label] = {"F": F, "draws_serialized": draws}

    for role in subgroup_capable:
        cs = curve_states[role]
        for h_label, k in (("h=N/2", 2), ("h=N/4", 4)):
            coords, h = subgroup_control(cs, k)
            pretreatment["subgroup_controls"].setdefault(role, {})[h_label] = {
                "h": h, "coords_digest": hashlib.sha256(
                    json.dumps(sorted(coords)).encode()).hexdigest()}
        cu = coset_union_control(cs, sampling_domain, m=0, draw_index=0)
        if cu is not None:
            pretreatment["coset_union_controls"][role] = {
                "h": cu["h"], "fb_size": cu["fb_size"], "g": list(cu["g"]) if cu["g"] else None,
                "coords_digest": hashlib.sha256(
                    json.dumps(sorted(cu["coords"])).encode()).hexdigest()}

    pretreatment_commit = sha256_of(pretreatment)
    committed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    result["stage4_pretreatment_commitment"] = {
        "sha256": pretreatment_commit, "committed_at": committed_at,
        "note": ("Nulls, subgroup controls and coset-union controls generated and "
                 "SHA-256-committed before any Stage-3 treatment cell (real FB) is "
                 "computed below."),
    }

    # ---------------- ORDERING CONTROL: frozen decision rule on null-vs-null FIRST ----
    # Applies the same in-band/out-of-band decision rule to a null-vs-remaining-nulls
    # comparison before applying it to real-vs-null, per ordering_control.
    def band_label(ratio, lo, hi):
        return "IN_BAND" if lo <= ratio <= hi else ("ABOVE_BAND" if ratio > hi else "BELOW_BAND")

    # ---------------- STAGE 4 SUBGROUP CONTROL EVALUATION (exact, forced) --------
    stage4_subgroup = {}
    for role in subgroup_capable:
        cs = curve_states[role]
        stage4_subgroup[role] = {}
        for h_label, k in (("h=N/2", 2), ("h=N/4", 4)):
            coords, h = subgroup_control(cs, k)
            if coords is None:
                stage4_subgroup[role][h_label] = {"skipped": True, "reason": f"{k} does not divide n2={cs.n2}"}
                continue
            F = h
            cstats = cell_stats(coords, cs, F, m_list=(2,))
            forced_rel_dev = cs.N / h - 1
            measured_rel_dev = cstats["per_m"][2]["max_rel_dev"]
            stage4_subgroup[role][h_label] = {
                "h": h, "N": cs.N, "forced_relative_deviation": forced_rel_dev,
                "measured_relative_deviation_m2": measured_rel_dev,
                "exact_match": abs(measured_rel_dev - forced_rel_dev) < 1e-9,
                "C_over_F": cstats["C_over_F"],
                "C_over_F_exact_match_1": abs(cstats["C_over_F"] - 1.0) < 1e-9,
            }
    result["stage4_subgroup_control"] = stage4_subgroup
    positive_control_1_pass = all(
        v.get("skipped") or (v["exact_match"] and v["C_over_F_exact_match_1"])
        for role in stage4_subgroup for v in stage4_subgroup[role].values())
    result["positive_control_1_pass"] = positive_control_1_pass
    if not positive_control_1_pass:
        result["halted_at"] = "stage4_positive_control_1"
        result["reason"] = "Positive control 1 did not return exactly N/h-1; per stopping_rules, no arm may be interpreted."
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 4 COSET-UNION CONTROL EVALUATION --------------------
    stage4_coset = {}
    for role, cs in curve_states.items():
        cu = coset_union_control(cs, sampling_domain, m=0, draw_index=0)
        if cu is None:
            continue
        h = cu["h"]
        coords = cu["coords"]
        Shat_measured = character_spectrum(coords, cs.n1, cs.n2)
        # forced prediction via delta-function FFT trick: Shat_pred = Shat_H + Shat_H * chi_g
        H4_coords = subgroup_control(cs, 4)[0]
        Shat_H = character_spectrum(H4_coords, cs.n1, cs.n2)
        delta = indicator_grid([cu["g_coord"]], cs.n1, cs.n2).astype(complex)
        import numpy as np
        chi_g = np.fft.fft2(delta)
        Shat_pred = Shat_H + Shat_H * chi_g
        max_abs_diff = float(np.max(np.abs(Shat_measured - Shat_pred)))
        max_abs_val = float(np.max(np.abs(Shat_measured)))
        Cval, _ = max_C(Shat_measured)
        F = cu["fb_size"]
        stage4_coset[role] = {
            "h": h, "F": F, "C": Cval, "C_over_F": Cval / F,
            "forced_spectrum_max_abs_diff": max_abs_diff,
            "forced_spectrum_relative_tolerance": max_abs_diff / max_abs_val if max_abs_val else None,
            "matches_forced_spectrum": (max_abs_diff / max_abs_val) < 1e-8 if max_abs_val else None,
        }
    result["stage4_coset_union_control"] = stage4_coset

    # ---------------- STAGE 3: treatment vs matched nulls, all curves x F-ladder --
    stage3 = {}
    for role, cs in curve_states.items():
        stage3[role] = {}
        for label, denom in F_LADDER_DENOMS.items():
            fb = ladder_fb(cs, denom)
            F = len(fb)
            coords = cs.coords_of(fb)
            real_stats = cell_stats(coords, cs, F)

            null_draws_raw = pretreatment["nulls"][role][label]["draws_serialized"]
            null_stats_list = []
            for draw in null_draws_raw:
                pts = [tuple(p) if p is not None else None for p in draw]
                ncoords = cs.coords_of(pts)
                null_stats_list.append(cell_stats(ncoords, cs, F))

            # ordering control: null-vs-null-population ratio first
            null1 = null_stats_list[0]
            rest = null_stats_list[1:]
            def agg(field, m, population):
                vals = [ns["per_m"][m]["var_ordered"] for ns in population]
                return sum(vals) / len(vals), (sum((v - sum(vals) / len(vals)) ** 2 for v in vals) / len(vals)) ** 0.5

            null_vs_null = {}
            real_vs_null = {}
            for m in (1, 2, 3, 4):
                # ordering control compares the held-out null against the rest;
                # the primary L2 baseline uses the full contracted null population,
                # matching the L3 baseline below.
                mean_var_rest, _ = agg("var_ordered", m, rest)
                mean_var_null, sd_var_null = agg("var_ordered", m, null_stats_list)
                mean_C_null = sum(ns["C_over_F"] for ns in null_stats_list) / len(null_stats_list)
                sd_C_null = (sum((ns["C_over_F"] - mean_C_null) ** 2 for ns in null_stats_list) / len(null_stats_list)) ** 0.5

                null_vs_null[m] = {
                    "null1_var_over_meanrest": (null1["per_m"][m]["var_ordered"] / mean_var_rest
                                                 if mean_var_rest else None),
                    "label": band_label(null1["per_m"][m]["var_ordered"] / mean_var_rest, 0.7, 1.4)
                    if mean_var_rest else None,
                }
                real_var = real_stats["per_m"][m]["var_ordered"]
                l2 = real_var / mean_var_null if mean_var_null else None
                real_vs_null[m] = {
                    "L2_var_real_over_var_null_mean": l2,
                    "null_mean_var": mean_var_null, "null_sd_var": sd_var_null,
                    "L2_label": band_label(l2, 0.7, 1.4) if l2 is not None and m >= 2 else "CALIBRATION_EXCLUDED" if m == 1 else None,
                }
            L3 = real_stats["C_over_F"] / mean_C_null if mean_C_null else None
            stage3[role][label] = {
                "F": F, "real": real_stats,
                "null_mean_C_over_F": mean_C_null, "null_sd_C_over_F": sd_C_null,
                "L3_C_over_F_ratio": L3,
                "L3_label": band_label(L3, 0.85, 1.15) if L3 is not None else None,
                "null_vs_null_ordering_control": null_vs_null,
                "real_vs_null": real_vs_null,
                "n_null_draws": len(null_stats_list),
            }
    result["stage3"] = stage3

    # ---------------- GRADED CONTROL 3: prime ladder (RO curves) ----------------
    ro_roles = [r for r in ("RO1", "RO2", "RO3", "RO4") if r in curve_states]
    prime_ladder = []
    for role in ro_roles:
        cs = curve_states[role]
        fb = ladder_fb(cs, 2)
        F = len(fb)
        coords = cs.coords_of(fb)
        Shat = character_spectrum(coords, cs.n1, cs.n2)
        Cval, _ = max_C(Shat)
        prime_ladder.append({"role": role, "p": cs.p, "N": cs.N, "F": F,
                              "C": Cval, "C_over_sqrtF": Cval / math.sqrt(F)})
    if len(prime_ladder) >= 2:
        xs = [math.log(c["N"]) for c in prime_ladder]
        ys = [math.log(c["C_over_sqrtF"]) for c in prime_ladder if c["C_over_sqrtF"] > 0]
        if len(ys) == len(xs) and len(xs) >= 2:
            n = len(xs)
            mx = sum(xs) / n
            my = sum(ys) / n
            num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            den = sum((x - mx) ** 2 for x in xs)
            fitted_exponent = num / den if den else None
        else:
            fitted_exponent = None
    else:
        fitted_exponent = None
    result["graded_control_3_prime_ladder"] = {
        "points": prime_ladder,
        "fitted_exponent_of_N_in_C_over_sqrtF": fitted_exponent,
        "note": "toy-scale trend over <=4 primes; never extrapolated (HEUR-CHR-2 measurement).",
    }

    result["completed"] = True
    _finish(result, out_dir, t_start)


def _finish(result, out_dir, t_start):
    result["wall_seconds"] = time.time() - t_start
    result["environment"] = {"python_version": platform.python_version(),
                              "platform": platform.platform()}
    with open(os.path.join(out_dir, "raw-result.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(json.dumps({"wall_seconds": result["wall_seconds"],
                       "completed": result.get("completed", False),
                       "halted_at": result.get("halted_at")}, indent=2))


if __name__ == "__main__":
    main()
