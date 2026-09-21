#!/usr/bin/env python3
"""
EXP-MONO-005b49: Pre-registered replication at a second, independent
same-prime matched-(N,tau) cell.

Implements experiments/EXP-MONO-005b49/specification.yaml exactly, per the
frozen contract (approved 2026-09-04, coordinator).

CODE REUSE DISCIPLINE (per handoff TASK-20260904-9abe5a and the contract's
own `inputs.reused_unchanged_from_amendment`):

- Stage 0's prime admission rule (prime, not supersingular), curve
  construction (`construct_ordinary`, `construct_cm_j0`,
  `construct_cm_j1728`), the transversal sampler and m=4 construction
  (`measure_curve`, `SIGN_CLASSES`, `NCLASSES`, `build_factor_base`) are
  loaded READ-ONLY, by file path, from EXP-MONO-64aaa4's own
  `implementation/run_experiment.py` -- never copied or edited. This
  script never redefines any of these functions.
- The group-uniform sampler (`sample_group_uniform_v2_corrected`,
  `measure_group_uniform_v2`) is loaded READ-ONLY, by file path, from
  EXP-MONO-cb905d's own `implementation/run_experiment_v2_part_a_corrected.py`
  -- the CORRECTED (2p+1-slot rejection sampling) construction per
  amendments/v1.yaml, never the deprecated v1-biased construction
  (`sample_group_uniform_v1_biased`, defined in that same file but never
  imported or called here).
- Domain separation: this run sets the loaded EXP-MONO-64aaa4 module's
  `DOMAIN` global to "EXP-MONO-005b49/v1" (this contract's own declared
  `inputs.domain`) before any draw, so every seed stream here is disjoint
  from EXP-MONO-64aaa4's and EXP-MONO-cb905d's own draws, exactly as
  EXP-MONO-cb905d's own v2 script did relative to v1's domain.

STAGE ORDER (fixed, per specification.yaml `stage_order`, followed exactly):
  Stage 0: ascending-p scan of [3001,20000] (p=617 excluded; not in range
           anyway, confirmed explicitly below) for the FIRST same-prime
           matched-(N,tau) cell. Report `no_second_cell_found` if none.
  Stage 1: (only if Stage 0 finds a cell) 20000 fresh draws per curve per
           arm (transversal, group-uniform), both curves.
  Stage 2: (only if Stage 0 finds a cell) the SOLE pre-registered log-ratio
           delta-method test, computed exactly as
           `significance_test_pre_registered_before_any_draw` specifies.
           The same-curve-only Fisher-exact test is reported ONLY as an
           explicitly labeled diagnostic/continuity figure (P5), never as
           an alternative or competing headline.

This script performs measurement only. It changes no hypothesis,
experiment, or goal status, and renders no verdict on H-MONO-1d50ac.
"""
import importlib.util
import json
import math
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_ROOT = HERE.parent  # experiments/EXP-MONO-005b49
REPO_ROOT = EXP_ROOT.parent.parent  # crypto-autoresearcher

EXP64_IMPL = REPO_ROOT / "experiments" / "EXP-MONO-64aaa4" / "implementation" / "run_experiment.py"
EXPCB_IMPL = REPO_ROOT / "experiments" / "EXP-MONO-cb905d" / "implementation" / "run_experiment_v2_part_a_corrected.py"

DOMAIN = "EXP-MONO-005b49/v1"
PRIME_LO = 3001
PRIME_HI = 20000
EXCLUDED_PRIME = 617  # already used at EXP-MONO-64aaa4/EXP-MONO-cb905d; not in [3001,20000] anyway
NTUPLES = 20000
SEED_LABEL = 20260904001  # per specification.yaml replication.seeds; nominal label only --
                           # this construction's determinism comes from the domain string and
                           # the declared (prime range, construction rules), not a PRNG seed
                           # (see EXP-MONO-64aaa4/implementation.md item 6).

RUN_DIR = EXP_ROOT / "runs" / "RUN-MONO-005b49-1"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    t_start = time.time()
    hard_deadline = t_start + 3600  # budget.maximum_wall_seconds
    stage0_soft_deadline = t_start + 2700  # leave >=900s for stage1/2 if a cell is found

    m64 = load_module(EXP64_IMPL, "exp_mono_64aaa4_impl_005b49")
    mcb = load_module(EXPCB_IMPL, "exp_mono_cb905d_v2_impl_005b49")
    m64.DOMAIN = DOMAIN  # domain separation from EXP-MONO-64aaa4's own runs

    result = {
        "run": "RUN-MONO-005b49-1",
        "seed_label": SEED_LABEL,
        "domain": DOMAIN,
        "prime_range": [PRIME_LO, PRIME_HI],
        "excluded_prime": EXCLUDED_PRIME,
        "stage0": {},
        "stage1": {},
        "stage2": {},
        "status": None,
        "timing": {},
    }

    if EXCLUDED_PRIME >= PRIME_LO and EXCLUDED_PRIME <= PRIME_HI:
        # Should never trigger; explicit confirmation per the contract's own instruction.
        raise RuntimeError("EXCLUDED_PRIME unexpectedly falls inside [PRIME_LO,PRIME_HI]")
    result["excluded_prime_in_range_check"] = "p=617 confirmed NOT in [3001,20000]; no exclusion needed in practice"

    # ---------------- STAGE 0: ascending-p same-prime matched-cell search ----------------
    primes = m64.primes_in_range(PRIME_LO, PRIME_HI)
    scan_order_note = (
        "Ascending order over primes_in_range(3001,20000) (smallest p first), "
        "fixed here before any search; the FIRST match under this order is "
        "reported, never a later or 'better' one."
    )
    found = None
    primes_scanned = 0
    stage0_stopped_early = False
    last_prime_scanned = None

    for p in primes:
        if p == EXCLUDED_PRIME:
            continue
        primes_scanned += 1
        last_prime_scanned = p
        if time.time() > stage0_soft_deadline:
            stage0_stopped_early = True
            break
        ordc = m64.construct_ordinary(p)
        if ordc is None:
            continue
        cm0 = m64.construct_cm_j0(p)
        cm1728 = m64.construct_cm_j1728(p)
        match = None
        for cm, label in ((cm0, "j0"), (cm1728, "j1728")):
            if cm is None:
                continue
            if ordc["N"] == cm["N"] and ordc["tau"] == cm["tau"]:
                match = {"p": p, "N": ordc["N"], "tau": ordc["tau"],
                         "ord": ordc, "cm": cm, "cm_variant": label}
                break
        if match is not None:
            found = match
            break

    result["stage0"]["scan_order"] = scan_order_note
    result["stage0"]["primes_scanned"] = primes_scanned
    result["stage0"]["last_prime_scanned"] = last_prime_scanned
    result["stage0"]["stopped_early_on_soft_deadline"] = stage0_stopped_early
    result["stage0"]["cell_found"] = found is not None
    result["timing"]["stage0_seconds"] = time.time() - t_start

    if found is None:
        result["status"] = "no_second_cell_found"
        result["stage0"]["disposition"] = (
            "No same-prime matched (N,tau) cell found within the declared "
            f"range [{PRIME_LO},{PRIME_HI}] (excluding p={EXCLUDED_PRIME})"
            + (" -- stopped early on the 2700s Stage-0 soft deadline; see "
               "stopped_early_on_soft_deadline and last_prime_scanned."
               if stage0_stopped_early else
               ", full range scanned exhaustively.")
            + " This is the valid, reportable terminal outcome per the "
              "contract's own stage_0.terminates_the_run_if clause: a "
              "scarcity fact about the declared range, not itself "
              "supporting or refuting H-MONO-1d50ac."
        )
        result["timing"]["total_seconds"] = time.time() - t_start
        return result

    p = found["p"]
    ordc = found["ord"]
    cm = found["cm"]
    N = found["N"]
    tau = found["tau"]
    cm_variant = found["cm_variant"]

    result["stage0"]["cell"] = {
        "p": p, "N": N, "tau": tau, "cm_variant": cm_variant,
        "ord": {k: ordc[k] for k in ("A", "B", "N", "tau", "trials")},
        "cm": {k: cm[k] for k in ("A", "B", "N", "tau", "trials")},
    }

    # ---------------- STAGE 1: fresh transversal + group-uniform measurement ----------------
    curve_ord = dict(ordc)
    curve_ord["role"] = "ord"
    curve_ord["j"] = None
    curve_cm = dict(cm)
    curve_cm["role"] = "cm"
    curve_cm["j"] = cm_variant

    fb_ord = m64.build_factor_base(curve_ord["A"], curve_ord["B"], p)
    fb_cm = m64.build_factor_base(curve_cm["A"], curve_cm["B"], p)

    stage1_deadline = hard_deadline - 60

    # Transversal arm ("random" sign convention; per EXP-MONO-64aaa4's own
    # implementation.md item 4, the fixed-sign and random-sign arms are
    # provably identical for this construction -- a single arm suffices as
    # the transversal measurement).
    tr_ord = m64.measure_curve(curve_ord, fb_ord, NTUPLES, "random", budget_deadline=stage1_deadline)
    tr_cm = m64.measure_curve(curve_cm, fb_cm, NTUPLES, "random", budget_deadline=stage1_deadline)

    # Group-uniform arm (corrected v2 construction per amendments/v1.yaml).
    gu_ord = mcb.measure_group_uniform_v2(m64, curve_ord, NTUPLES, budget_deadline=stage1_deadline)
    gu_cm = mcb.measure_group_uniform_v2(m64, curve_cm, NTUPLES, budget_deadline=stage1_deadline)

    result["stage1"] = {
        "p": p, "N": N, "tau": tau,
        "ntuples_per_curve_per_arm": NTUPLES,
        "transversal_ord": tr_ord,
        "transversal_cm": tr_cm,
        "group_uniform_ord": gu_ord,
        "group_uniform_cm": gu_cm,
        "raw_counts": {
            "tr_ord_pairs_colliding": tr_ord["total_pairs_colliding"],
            "tr_cm_pairs_colliding": tr_cm["total_pairs_colliding"],
            "gu_ord_pairs_colliding": gu_ord["total_pairs_colliding"],
            "gu_cm_pairs_colliding": gu_cm["total_pairs_colliding"],
        },
    }
    result["timing"]["stage1_seconds"] = time.time() - t_start - result["timing"]["stage0_seconds"]

    # ---------------- STAGE 2: the SOLE pre-registered headline test ----------------
    tr_ord_count = tr_ord["total_pairs_colliding"]
    tr_cm_count = tr_cm["total_pairs_colliding"]
    gu_ord_count = gu_ord["total_pairs_colliding"]
    gu_cm_count = gu_cm["total_pairs_colliding"]

    tr_ord_rate = tr_ord_count / NTUPLES
    tr_cm_rate = tr_cm_count / NTUPLES
    gu_ord_rate = gu_ord_count / NTUPLES
    gu_cm_rate = gu_cm_count / NTUPLES

    stage2 = {
        "raw_counts": {
            "gu_ord_count": gu_ord_count, "tr_ord_count": tr_ord_count,
            "gu_cm_count": gu_cm_count, "tr_cm_count": tr_cm_count,
        },
        "rates": {
            "gu_ord_rate": gu_ord_rate, "tr_ord_rate": tr_ord_rate,
            "gu_cm_rate": gu_cm_rate, "tr_cm_rate": tr_cm_rate,
        },
    }

    zero_count_note = None
    if tr_ord_count == 0 or gu_ord_count == 0 or tr_cm_count == 0 or gu_cm_count == 0:
        zero_count_note = (
            "At least one raw count is zero; P1/P2/log-ratio and/or the "
            "delta-method variance terms are undefined (division by zero "
            "and/or log(0)). Reported explicitly below; no substitute "
            "test applied."
        )

    if zero_count_note is None:
        P1 = gu_ord_rate / tr_ord_rate
        P2 = gu_cm_rate / tr_cm_rate
        P3_ratio_of_ratios = P1 / P2
        log_ratio = math.log(P1 / P2)
        var_logP1 = 1.0 / gu_ord_count + 1.0 / tr_ord_count
        var_logP2 = 1.0 / gu_cm_count + 1.0 / tr_cm_count
        se = math.sqrt(var_logP1 + var_logP2)
        z = log_ratio / se
        two_sided_p = 2.0 * (1.0 - _phi(abs(z)))
        stage2.update({
            "P1_ordinary_gu_over_tr": P1,
            "P2_cm_gu_over_tr": P2,
            "P3_ratio_of_ratios_P1_over_P2": P3_ratio_of_ratios,
            "log_ratio": log_ratio,
            "var_logP1": var_logP1,
            "var_logP2": var_logP2,
            "se": se,
            "z": z,
            "two_sided_p_value": two_sided_p,
            "note": (
                "THE SOLE headline P3 statistic, computed exactly per "
                "specification.yaml significance_test_pre_registered_"
                "before_any_draw. Two-sided, genuinely open per the "
                "pre-registered prediction."
            ),
        })
        stage2["P4_direction_matches_first_cell"] = bool(P1 > P2)
        stage2["P4_note"] = (
            f"First cell (p=617) found P1={2.398} > P2 (ordinary above CM; "
            "see source_refs EV-MONO-c0bf6d / CORR-20260904-d0205d). This "
            f"cell: P1={P1}, P2={P2} -> P1>P2 is {P1 > P2}."
        )
    else:
        stage2["undefined_note"] = zero_count_note
        stage2["P1_ordinary_gu_over_tr"] = None
        stage2["P2_cm_gu_over_tr"] = None
        stage2["P3_ratio_of_ratios_P1_over_P2"] = None
        stage2["z"] = None
        stage2["two_sided_p_value"] = None
        stage2["P4_direction_matches_first_cell"] = None

    # Diagnostic-only, explicitly labeled per the contract: same-curve-only
    # Fisher-exact "any collision per tuple" test. NEVER a headline. Uses the
    # GROUP-UNIFORM arm counts (the arm this diagnostic was originally applied
    # to at EXP-MONO-cb905d/RUN-2), tuple-level any-collision indicator.
    a_gu = gu_ord["tuples_with_collision"]
    b_gu = gu_ord["ntuples"] - a_gu
    c_gu = gu_cm["tuples_with_collision"]
    d_gu = gu_cm["ntuples"] - c_gu
    gu_odds_ratio, gu_pvalue = m64.fisher_exact_2x2(a_gu, b_gu, c_gu, d_gu)
    stage2["P5_diagnostic_only_KNOWN_DEFECTIVE_per_CORR_20260904_d0205d"] = {
        "label": (
            "KNOWN-DEFECTIVE, DIAGNOSTIC ONLY, per CORR-20260904-d0205d. "
            "NOT a headline. NOT an alternative to P3. Reported for "
            "continuity with EXP-MONO-cb905d/RUN-2's own defective "
            "methodology only."
        ),
        "test": "fisher_exact_2x2 on {any-collision, no-collision} per tuple, group-uniform arm, ord vs cm",
        "table": {"ord_collision": a_gu, "ord_no_collision": b_gu,
                  "cm_collision": c_gu, "cm_no_collision": d_gu},
        "odds_ratio": gu_odds_ratio,
        "p_value": gu_pvalue,
        "significant_at_0.05": bool(gu_pvalue < 0.05),
    }

    result["stage2"] = stage2
    result["status"] = "completed_valid"
    result["timing"]["total_seconds"] = time.time() - t_start
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result["timing"]["peak_rss_bytes"] = peak_rss * 1024 if sys.platform != "darwin" else peak_rss
    return result


def _phi(x):
    """Standard normal CDF via math.erf (no scipy dependency needed here)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


if __name__ == "__main__":
    try:
        res = main()
        print(json.dumps(res, indent=2))
        if res.get("status") not in ("completed_valid", "no_second_cell_found"):
            sys.exit(3)
    except TimeoutError as e:
        print(json.dumps({"status": "failed_infrastructure",
                           "error": "TimeoutError", "message": str(e)}, indent=2))
        sys.exit(2)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "failed_infrastructure",
                           "error": type(e).__name__, "message": str(e),
                           "traceback": traceback.format_exc()}, indent=2))
        sys.exit(1)
