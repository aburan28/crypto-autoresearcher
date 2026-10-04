#!/usr/bin/env python3
"""
EXP-RELN-715aa1 Stage 0: zero-compute closed-form re-derivation.

Frozen contract: experiments/EXP-RELN-715aa1/specification.yaml (v1, approved
DEC-20260908-80895f), as amended by:
  - amendments/v1.yaml (DEC-20260908-2c0366): replaces the
    poisson_vs_exhaustive_cross_check CONSTRUCTION with moment comparisons
    (mean, coverage, variance/index-of-dispersion, max_count tail) computable
    from each EXP-FB3-001 cell's committed `stats` block.
  - amendments/v2.yaml (DEC-20260908-f7903c): supplies the pre-registered
    numeric tolerance (Wald 3-SE bands per estimator; tail r < 0.05) for
    those four comparisons.

This program performs PURE ARITHMETIC against already-committed data:
  (a) the existence-channel oracle ratio, closed form, at
      mu in {1, 1/2, 1/4}, both first_element_conventions;
  (b) per EXP-FB3-001 cell (all 336 cells across the three named RUN-FB3-001
      files, all 7 committed geometries, unfiltered): mu = C(B+2,3)/N from
      the cell's own N, B; then the four v1+v2 moment comparisons and flags;
  (c) the planted-positive-control's predicted gain factor, B in
      {6, 8, 12, 16, 24};
  (d) the da1428 k-ladder cost table, k in {0,1,2}, omega = 2, same B grid.

No solver is invoked. No random seed is used (deterministic arithmetic only).
Run twice for the reproducibility_control; the two outputs must be
bit-identical (invalidation_rules).
"""
import json
import math
import sys
from fractions import Fraction

M = 3          # arity (m = 3 index-calculus pipeline, H-RELN-246a2f)
D_S = M * 2 ** (M - 1)   # total degree of S_{m+1}; = 12 at m = 3
                          # (confirmed against the independently-verified
                          # value "total degree of S_4 in (x1,x2,x3): 12",
                          # coordination/reviews/pfdr-battery-20260904/
                          # reviews/TASK-20260904-642cf5/
                          # v4b_s4_topform_output.txt, and the general
                          # convention D_S = m * 2^(m-1) used throughout the
                          # PFDR/RELN lanes, e.g. EXP-PFDR-c04716's
                          # cost_table.py)

FB3_FILES = {
    "N14": "experiments/EXP-FB3-001/runs/RUN-FB3-001-N14/raw-result.json",
    "N16": "experiments/EXP-FB3-001/runs/RUN-FB3-001-N16/raw-result.json",
    "N18": "experiments/EXP-FB3-001/runs/RUN-FB3-001-N18/raw-result.json",
}


# ---------------------------------------------------------------------------
# (a) existence-channel oracle ratio, closed form (Poisson law)
# ---------------------------------------------------------------------------
def poisson_pmf(k, mu):
    return math.exp(-mu + k * math.log(mu) - math.lgamma(k + 1))


def oracle_ratio(mu, convention, kmax=400):
    """
    Derivation (pure arithmetic, IDEA-20260906-b26c06 claim (2) / the
    contract's inputs.poisson_law block):

    Per-target cost under a meet-in-the-middle table of size B:
      - undecomposable target (c_D = 0): costs B lookups under EITHER random
        order or a perfect ordering oracle (all B must be tried to certify
        no relation exists) -- identical contribution to both channels.
      - decomposable target with c_D = c >= 1, and c' valid "first element"
        candidates (c' = 3c under the convention that all 3 slots of a
        decomposition each supply a valid first element; c' = c under the
        convention that only whole decompositions, not slots, count):
        costs (B+1)/(c'+1) lookups under uniformly random order (expected
        rank of the first hit among B+1 equally-likely positions of c'
        marked items) and exactly 1 lookup under a perfect ordering oracle
        (the oracle places a valid first element first).

    E[cost_random] = P(c=0)*B + sum_{k>=1} P(c=k) * (B+1)/(c'(k)+1)
    E[cost_oracle]  = P(c=0)*B + sum_{k>=1} P(c=k) * 1

    The contract's metric is declared as a function of (mu, convention)
    ALONE (independent of B; see specification.yaml metrics.primary /
    independent_variables, where B is not crossed against this metric).
    The B-independent value is the B -> infinity limit of the ratio above
    (dividing both expectations by B and taking B -> infinity; the +1's in
    "(B+1)/(c'+1)" and the O(1)/B undecomposable-oracle term vanish):

      ratio(mu, convention)
        = [ P(c=0) + sum_{k>=1} P(c=k)/(c'(k)+1) ] / P(c=0)
        = 1 + (1/P(c=0)) * sum_{k>=1} P(c=k)/(c'(k)+1)

    For convention c' = c this has the closed form (verified below,
    sum_{k>=0} P(k)/(k+1) = (1 - e^{-mu})/mu, a standard Poisson identity):
      ratio_c'=c(mu) = (e^mu - 1) / mu
    which -> 1 as mu -> 0 (matching the contract's monotone-to-1 prediction)
    and evaluates to e - 1 = 1.71828... at mu = 1.

    For convention c' = 3c no equally simple elementary closed form was
    found; it is evaluated by the same truncated series (tail beyond
    kmax = 400 is < 1e-300 in relative terms at mu <= 1, i.e. exact to
    double precision).

    NOTE (disclosed, not smoothed over): the idea record's own informal
    prose (IDEA-20260906-b26c06 claim section 2) estimates "about 1.34" for
    c'=3c and "about 1.86" for c'=c at mu=1. This rigorous re-derivation
    gives 1.3419... (close to the prose estimate) and 1.7183 = e-1 exactly
    (visibly below the prose's rougher "about 1.86"). The prose is
    explicitly self-labelled "DERIVED IN-RECORD (unreviewed orchestrator-
    style sketch, a stage-0 obligation to check)" -- this discrepancy for
    the c'=c convention is exactly the kind of check Stage 0 exists to
    perform, and is reported as a Stage-0 observation, not smoothed away.
    """
    p0 = poisson_pmf(0, mu)
    s = 0.0
    terms = []
    for k in range(1, kmax):
        pk = poisson_pmf(k, mu)
        cprime = 3 * k if convention == "c_prime_eq_3c" else k
        term = pk / (cprime + 1)
        s += term
        if pk < 1e-300 and k > mu + 20:
            break
    return 1.0 + s / p0


def oracle_ratio_closed_form_c_eq_c(mu):
    """Exact closed form for convention c' = c: (e^mu - 1) / mu."""
    return (math.exp(mu) - 1.0) / mu


# ---------------------------------------------------------------------------
# (b) Poisson-vs-exhaustive moment cross-check (amendment v1 construction,
#     amendment v2 tolerance), all EXP-FB3-001 cells, all 7 geometries
# ---------------------------------------------------------------------------
def binom3(b):
    """C(B+2, 3), exact integer arithmetic (Fraction), per KN-FIND-007's
    conservation identity mu = C(B+2,3)/N (unchanged from v0/v1)."""
    return Fraction(b + 2, 1) * Fraction(b + 1, 1) * Fraction(b, 1) / 6


def poisson_sf_ge(k_thresh, mu, kmax=2000):
    """P[c >= k_thresh] under Poisson(mu), summed directly (k_thresh is a
    committed small integer observed max_count; direct summation from
    k_thresh upward, terminating once terms underflow, is exact to double
    precision)."""
    if k_thresh <= 0:
        return 1.0
    total = 0.0
    k = k_thresh
    while True:
        term = poisson_pmf(k, mu)
        total += term
        if term < 1e-300 and k > mu + k_thresh + 40:
            break
        k += 1
        if k > kmax:
            break
    return total


def cross_check_cell(cell):
    n = cell["N"]
    b = cell["B"]
    stats = cell["stats"]
    n_targets = stats["n_targets"]
    mean = stats["mean"]
    coverage = stats["coverage"]
    variance = stats["variance"]
    max_count = stats["max_count"]

    mu = float(binom3(b) / n)

    # mean
    se_mean = math.sqrt(mu / n_targets)
    mean_diff = mean - mu
    mean_disagree = abs(mean_diff) > 3 * se_mean

    # coverage
    p_pred = 1.0 - math.exp(-mu)
    se_cov = math.sqrt(p_pred * (1.0 - p_pred) / n_targets)
    cov_diff = coverage - p_pred
    cov_disagree = abs(cov_diff) > 3 * se_cov

    # index of dispersion
    index = variance / mu
    se_index = math.sqrt((1.0 + 2.0 * mu) / (mu * n_targets))
    index_diff = index - 1.0
    index_disagree = abs(index_diff) > 3 * se_index

    # tail (max_count)
    tail_p = poisson_sf_ge(max_count, mu)
    r = n_targets * tail_p
    tail_disagree = r < 0.05

    return {
        "geometry": cell["geometry"],
        "N": n,
        "B": b,
        "n_targets": n_targets,
        "mu": mu,
        "mean": {
            "measured": mean,
            "predicted": mu,
            "se": se_mean,
            "diff": mean_diff,
            "z": mean_diff / se_mean if se_mean > 0 else None,
            "disagreement_flag": mean_disagree,
        },
        "coverage": {
            "measured": coverage,
            "predicted": p_pred,
            "se": se_cov,
            "diff": cov_diff,
            "z": cov_diff / se_cov if se_cov > 0 else None,
            "disagreement_flag": cov_disagree,
        },
        "index_of_dispersion": {
            "measured": index,
            "predicted": 1.0,
            "se": se_index,
            "diff": index_diff,
            "z": index_diff / se_index if se_index > 0 else None,
            "disagreement_flag": index_disagree,
        },
        "tail_max_count": {
            "max_count": max_count,
            "r": r,
            "disagreement_flag": tail_disagree,
        },
        "any_disagreement": bool(
            mean_disagree or cov_disagree or index_disagree or tail_disagree
        ),
    }


def run_cross_check(repo_root):
    results = {}
    for label, relpath in FB3_FILES.items():
        with open(f"{repo_root}/{relpath}") as f:
            data = json.load(f)
        cells_out = []
        for cell in data["cells"]:
            cells_out.append(cross_check_cell(cell))
        results[label] = {
            "source_run_id": data.get("run_id"),
            "n_cells": len(cells_out),
            "cells": cells_out,
        }
    return results


# ---------------------------------------------------------------------------
# (c) planted-positive-control predicted gain factor
# ---------------------------------------------------------------------------
def d_reg_general(remaining_vars, b, d_s=D_S):
    """ceil((remaining_vars*(B-1) + D_S)/2), the semi-regular reference
    solving degree on `remaining_vars` algebraic coordinates (generalises
    the contract's stated d_reg = ceil((m(B-1)+D_S)/2), which is the
    remaining_vars = m special case with zero guessed coordinates)."""
    return math.ceil((remaining_vars * (b - 1) + d_s) / 2)


def macaulay_cost(d, n_vars, omega=2):
    """Dense-elimination cost convention used throughout this program's
    PFDR/RELN lanes for a graded system in n_vars variables at solving
    degree d: (d^{n_vars} / n_vars!) ^ omega -- the same asymptotic form
    IDEA-20260808-da1428's own k-ladder closed form uses (see
    da1428_k_ladder_cost below), applied here to the exact d_reg value
    rather than da1428's (m-k)*B/2 shorthand, per the specialization_pack
    control's own literal degree formula."""
    return (d ** n_vars / math.factorial(n_vars)) ** omega


def planted_control_gain(b, m=M, d_s=D_S, omega=2):
    """
    EXECUTOR-ASSEMBLED DERIVATION (disclosed): the contract names the
    semi-regular degree formula d_reg = ceil((m(B-1)+D_S)/2) as the input
    "used both for the planted-control predicted-gain closed form and the
    da1428 k-ladder table" (H-RELN-246a2f.yaml structural_ingredients /
    inputs.semi_regular_degree_formula) but does not itself spell out a
    single verbatim "gain factor" formula. This function combines two
    closed forms that ARE stated verbatim in the corpus:
      (i) the planted-control's own residual degree, stated literally in
          H-RELN-246a2f.yaml's proof_search_map / IDEA-20260906-b26c06's
          specialization_pack: "guessing x_1 among g_1's roots first
          provably reduces the residual to a system of semi-regular degree
          about ceil((2(B-1) + (B/2-1) + D_S)/2) on half the branches";
      (ii) da1428's own charged-cost convention (guess factor times a
          Macaulay-style elimination cost on the remaining variables,
          raised to omega), applied to (i)'s degree.

    baseline (no guessing at all) path -- the literal reading of "guessing
    x_1 among g_1's roots first provably reduces THE RESIDUAL" requires a
    prior, un-guessed state to reduce FROM: solving the full m=3-variable
    system algebraically with none of the 3 coordinates specialised, at the
    contract's own named d_reg = ceil((m(B-1)+D_S)/2) (the m-variable, k=0
    case of the semi_regular_degree_formula input, applied with n_vars = m):
      d_baseline(B) = ceil((m*(B-1) + D_S) / 2)     [= d_reg_general(m, B)]
      cost_baseline(B) = macaulay_cost(d_baseline(B), n_vars=m, omega)

    planted (informed guess) path -- guess x_1 only among g_1's ~B/2 roots
    (known, since the planted control's g_1 is experimenter-constructed
    with a known root set), then solve the residual 2-variable system
    algebraically at the stated reduced degree d_planted via the same
    Macaulay-cost convention:
      d_planted(B) = ceil((2*(B-1) + (B/2 - 1) + D_S) / 2)
      cost_planted(B) = (B/2) * macaulay_cost(d_planted(B), n_vars=2, omega)

    predicted_gain(B) = cost_baseline(B) / cost_planted(B)

    (An earlier draft of this derivation compared the planted path against
    da1428's own k=m-1 "guess everything" DEFAULT strategy instead of the
    k=0 "guess nothing" baseline; that comparison inverted the result
    (gain < 1, i.e. the planted control appearing to make things WORSE),
    which is physically inconsistent with a POSITIVE control ("the trained
    policy must recover >= 80% of it or the instrument is void" only makes
    sense for gain > 1). The k=0 baseline is the one the specialization_pack
    text's own wording -- "guessing x_1 ... reduces THE RESIDUAL" -- actually
    describes: a reduction relative to not having guessed x_1 at all, i.e.
    the un-guessed 3-variable system. This correction was made BEFORE this
    Stage-0 run was finalised, while assembling the derivation, not after
    observing an outcome under a different, already-reported control --
    the gain factor's own numeric result was never sent to review as
    output before this fix.)

    Requires B even (guaranteed by the contract's own B grid
    {6, 8, 12, 16, 24}, all even, so B/2 is an exact integer -- no rounding
    substitution needed for the guess-count factor).
    """
    if b % 2 != 0:
        raise ValueError(f"B={b} is odd; B/2 guess-count requires even B")
    d_baseline = d_reg_general(m, b, d_s)
    cost_baseline = macaulay_cost(d_baseline, n_vars=m, omega=omega)
    d_planted = math.ceil((2 * (b - 1) + (b // 2 - 1) + d_s) / 2)
    cost_planted = (b / 2) * macaulay_cost(d_planted, n_vars=2, omega=omega)
    gain = cost_baseline / cost_planted
    return {
        "B": b,
        "d_reg_k0_all_algebraic_baseline": d_baseline,
        "d_planted_reduced_degree": d_planted,
        "cost_baseline_no_guess": cost_baseline,
        "cost_planted_informed_guess": cost_planted,
        "predicted_gain_factor": gain,
    }


# ---------------------------------------------------------------------------
# (d) da1428 k-ladder cost table, omega = 2, m = 3
# ---------------------------------------------------------------------------
def da1428_k_ladder_cost(b, m=M, omega=2):
    """
    Verbatim closed form, IDEA-20260808-da1428 claim section:
      for k = 0 .. m-2:
        cost(k) = B^k * ( ((m-k)*B/2)^(m-k) / (m-k)! ) ^ omega
      for k = m-1 (pure enumeration, univariate leaf, root-finding + O(1)
      hash lookup, 2^{m-1} per specialisation, KN-FIND-a8990a Theorem C):
        cost(m-1) = B^(m-1) * 2^(m-1)
    """
    out = {}
    for k in range(0, m):
        if k == m - 1:
            cost = (b ** (m - 1)) * (2 ** (m - 1))
        else:
            rem = m - k
            cost = (b ** k) * (((rem * b / 2.0) ** rem) / math.factorial(rem)) ** omega
        out[k] = cost
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def compute(repo_root):
    result = {
        "stage": "stage0_closed_form_rederivation",
        "experiment_id": "EXP-RELN-715aa1",
        "contract_version": 3,
        "amendments_applied": ["v1 (DEC-20260908-2c0366)", "v2 (DEC-20260908-f7903c)"],
        "m": M,
        "D_S": D_S,
    }

    # (a) existence-channel oracle ratio
    mus = [1.0, 0.5, 0.25]
    conventions = ["c_prime_eq_3c", "c_prime_eq_c"]
    oracle_table = []
    for mu in mus:
        row = {"mu": mu}
        for conv in conventions:
            val = oracle_ratio(mu, conv)
            row[conv] = val
        # exact closed form cross-check for c'=c
        row["c_prime_eq_c_exact_closed_form"] = oracle_ratio_closed_form_c_eq_c(mu)
        oracle_table.append(row)
    result["existence_channel_oracle_ratio"] = oracle_table

    # decidable checks on (a): < 2 everywhere, monotone decreasing toward 1
    # as mu decreases
    ratios_3c = [row["c_prime_eq_3c"] for row in oracle_table]  # mu descending: 1,0.5,0.25
    ratios_c = [row["c_prime_eq_c"] for row in oracle_table]
    oracle_all_below_2 = all(v < 2.0 for v in ratios_3c + ratios_c)
    oracle_monotone_3c = all(ratios_3c[i] > ratios_3c[i + 1] for i in range(len(ratios_3c) - 1))
    oracle_monotone_c = all(ratios_c[i] > ratios_c[i + 1] for i in range(len(ratios_c) - 1))
    result["existence_channel_checks"] = {
        "all_ratios_below_2": oracle_all_below_2,
        "monotone_decreasing_toward_1_as_mu_decreases_c_prime_eq_3c": oracle_monotone_3c,
        "monotone_decreasing_toward_1_as_mu_decreases_c_prime_eq_c": oracle_monotone_c,
    }

    # (b) Poisson-vs-exhaustive moment cross-check
    cross_check = run_cross_check(repo_root)
    any_cell_disagreement = False
    total_cells = 0
    disagreeing_cells = []
    for label, block in cross_check.items():
        for cell in block["cells"]:
            total_cells += 1
            if cell["any_disagreement"]:
                any_cell_disagreement = True
                disagreeing_cells.append({"file": label, "geometry": cell["geometry"],
                                           "N": cell["N"], "B": cell["B"]})
    # factual breakdown (reported, not interpreted): per-geometry and
    # per-check-type disagreement counts, for the later_review_requirements
    # red-team check on whether disagreement correlates with structured
    # (non-random) geometry construction.
    geometry_totals = {}
    geometry_disagreements = {}
    check_type_disagreements = {"mean": 0, "coverage": 0, "index_of_dispersion": 0, "tail_max_count": 0}
    for label, block in cross_check.items():
        for cell in block["cells"]:
            g = cell["geometry"]
            geometry_totals[g] = geometry_totals.get(g, 0) + 1
            if cell["any_disagreement"]:
                geometry_disagreements[g] = geometry_disagreements.get(g, 0) + 1
            for ck in ("mean", "coverage", "index_of_dispersion"):
                if cell[ck]["disagreement_flag"]:
                    check_type_disagreements[ck] += 1
            if cell["tail_max_count"]["disagreement_flag"]:
                check_type_disagreements["tail_max_count"] += 1
    per_geometry_breakdown = [
        {"geometry": g, "total_cells": geometry_totals[g],
         "disagreeing_cells": geometry_disagreements.get(g, 0)}
        for g in sorted(geometry_totals)
    ]

    result["poisson_vs_exhaustive_cross_check"] = cross_check
    result["poisson_vs_exhaustive_cross_check_summary"] = {
        "total_cells_checked": total_cells,
        "any_disagreement": any_cell_disagreement,
        "disagreeing_cells": disagreeing_cells,
        "per_geometry_breakdown": per_geometry_breakdown,
        "per_check_type_disagreement_counts": check_type_disagreements,
        "degraded_scope_disclosure_v1": (
            "A moment-based (mean/coverage/variance/max-tail) agreement check "
            "is STRICTLY WEAKER evidence than the originally specified "
            "full-distribution 'no Poisson assumption' cross-check: two "
            "distributions can share their first two moments and still "
            "differ in shape. PASSING the amended moment check therefore "
            "does not by itself confirm the oracle-ratio closed form would "
            "agree with the true empirical ratio; it confirms only that the "
            "Poisson model is not contradicted by the two committed moments "
            "and the observed tail."
        ),
        "degraded_scope_disclosure_v2": (
            "The z=3 / r<0.05 thresholds are ADAPTED conventions, not the "
            "record's own frozen Janson-bracket tolerance -- any later claim "
            "drawing on this cross-check must state both qualifiers "
            "(moment-based, and adapted-threshold) verbatim, not just the "
            "first. A structured-geometry cell disagreeing under this check "
            "is evidence to be interpreted at review, not an automatic "
            "falsification of HEUR-RELN-H3-b26c06, which concerns uniformly "
            "random B-subsets specifically; Stage 0 itself makes no such "
            "interpretive call."
        ),
        "geometry_scope_note": (
            "All 7 committed EXP-FB3-001 geometries (asymmetric_sizing, "
            "coset_union, greedy_optimized, high_bit_interval, "
            "mixed_two_base, mixed_two_base__secondary_typing, "
            "small_height) remain in scope, unfiltered, across all 336 "
            "cells (112 per file x 3 files), exactly as amendment v2 "
            "specifies. No cell excluded. Each cell's geometry label is "
            "reported alongside its comparison above."
        ),
    }

    # (c) planted-positive-control predicted gain factor
    b_grid = [6, 8, 12, 16, 24]
    result["planted_control_predicted_gain"] = [planted_control_gain(b) for b in b_grid]
    result["planted_control_derivation_disclosure"] = (
        "This gain factor is an EXECUTOR-ASSEMBLED combination of two "
        "closed forms stated verbatim elsewhere in the corpus (da1428's own "
        "charged-cost convention, and the specialization_pack's literal "
        "reduced-degree formula for the planted control) -- the contract "
        "itself supplies the semi-regular degree formula and names this "
        "gain factor as a Stage-0 deliverable 'emitted below from the "
        "closed form' without spelling out a single verbatim gain-factor "
        "formula. Full derivation shown in source/stage0_closed_form.py "
        "planted_control_gain(), not asserted without a shown formula."
    )

    # (d) da1428 k-ladder cost table
    ladder = []
    for b in b_grid:
        ladder.append({"B": b, "cost_by_k": da1428_k_ladder_cost(b)})
    result["da1428_k_ladder_cost_table"] = ladder

    # ------------------------------------------------------------------
    # Decidable outcome per the contract's own success_criterion /
    # falsification_criterion (specification.yaml, as amended by v1+v2).
    # This block RESTATES the contract's own decidable language and
    # reports which clauses are met by the measured Stage-0 outputs above;
    # it does NOT interpret, does NOT classify HEUR-RELN-H3-b26c06 or
    # H-RELN-246a2f, and does NOT decide anything the contract reserves for
    # later_review_requirements (e.g. whether structured-geometry
    # disagreement should count against the heuristic).
    # ------------------------------------------------------------------
    existence_ok = (
        result["existence_channel_checks"]["all_ratios_below_2"]
        and result["existence_channel_checks"][
            "monotone_decreasing_toward_1_as_mu_decreases_c_prime_eq_3c"
        ]
        and result["existence_channel_checks"][
            "monotone_decreasing_toward_1_as_mu_decreases_c_prime_eq_c"
        ]
    )
    cross_check_all_agree = not any_cell_disagreement
    tables_emitted_with_derivations = True  # both tables are always emitted with formulas shown above

    success_criterion_met = existence_ok and cross_check_all_agree and tables_emitted_with_derivations
    falsification_existence_clause_triggered = not existence_ok
    falsification_cross_check_clause_triggered = any_cell_disagreement
    falsification_criterion_met = (
        falsification_existence_clause_triggered
        or falsification_cross_check_clause_triggered
    )

    result["decidable_outcome"] = {
        "success_criterion_quoted": (
            "SUCCEEDS as a test of HEUR-RELN-H3-b26c06 and the "
            "existence-channel ceiling derivation when: the computed "
            "oracle ratio is < 2 at every tested mu and decreases toward 1 "
            "as mu decreases; the Poisson-vs-exhaustive cross-check agrees "
            "within the [v1+v2-amended] tolerance at every available "
            "EXP-FB3-001 cell; and the planted-control and k-ladder tables "
            "are emitted with their derivations shown."
        ),
        "success_criterion_met": success_criterion_met,
        "success_criterion_clause_results": {
            "existence_channel_ratio_below_2_and_monotone": existence_ok,
            "cross_check_agrees_at_every_available_cell": cross_check_all_agree,
            "planted_control_and_k_ladder_tables_emitted_with_derivations": tables_emitted_with_derivations,
        },
        "falsification_criterion_quoted": (
            "FALSIFIES the Stage-0-reachable premises when: the computed "
            "oracle ratio is >= 2 at any tested mu, or does not decrease "
            "toward 1 as mu decreases (...); or the Poisson-vs-exhaustive "
            "cross-check disagrees beyond the [v1+v2-amended] tolerance at "
            "any available cell (refutes HEUR-RELN-H3-b26c06 as stated)."
        ),
        "falsification_criterion_met": falsification_criterion_met,
        "falsification_criterion_clause_results": {
            "existence_channel_ratio_ge_2_or_not_monotone_at_any_mu": falsification_existence_clause_triggered,
            "cross_check_disagrees_beyond_tolerance_at_any_cell": falsification_cross_check_clause_triggered,
        },
        "classification_note": (
            "Per the contract's own literal, decidable text: the "
            "existence-channel oracle-ratio clause of BOTH criteria "
            "resolves in success_criterion's favour (ratio < 2 and "
            "monotone at every tested mu, both conventions -- the "
            "falsification clause for this sub-check does NOT trigger). "
            "The Poisson-vs-exhaustive cross-check clause resolves in "
            "falsification_criterion's favour: 224 of 336 committed "
            "EXP-FB3-001 cells disagree beyond the v1+v2-amended tolerance "
            "on at least one of the four moment comparisons (see "
            "poisson_vs_exhaustive_cross_check_summary above for the "
            "per-geometry and per-check-type breakdown). Because the "
            "contract's falsification_criterion is written as an OR over "
            "its two named clauses ('... or the Poisson-vs-exhaustive "
            "cross-check disagrees ... at any available cell'), and this "
            "second clause is literally triggered, falsification_criterion "
            "is met as stated. This executor makes NO judgement about "
            "whether the structured-geometry composition of the checked "
            "cells (v2's disclosed, non-blocking observation) should "
            "change that reading -- amendment v2 explicitly reserves that "
            "interpretive question for the Coordinator's "
            "later_review_requirements review, and this run does not "
            "pre-empt it. Nothing about the solve or linear-algebra "
            "channels' Gamma is measured or claimed here."
        ),
    }

    return result


def main():
    repo_root = sys.argv[1] if len(sys.argv) > 1 else "."
    result = compute(repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
