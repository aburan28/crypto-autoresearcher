#!/usr/bin/env python3
"""EXP-JMV-004 branch (a) run RUN-JMV-004-a -- cost-model grid evaluation.

FROZEN CONTRACT: experiments/EXP-JMV-004/specification.yaml, version 2,
BRANCH (a) ONLY. Authorized_by: DEC-20260906-27fa94 (branch (a) only).
Handoff: TASK-20260906-a29dee.

THIS IS A DETERMINISTIC ANALYTIC EVALUATION OF A MODEL. Zero instances are
tested at any size; q enters only as a model parameter. Claim tier:
not_applicable / theoretical / derivation (condition E3). Every quantitative
statement below is GRH-conditional (Lemma 4.1's bound is GRH-conditional,
per CTRL-GRH); nothing here confirms or disconfirms GRH.

C1 STATUS: PENDING. This script computes the model, the grids, and the
constants table only. No conclusion about vacuity/non-vacuity of the proven
eigenvalue separation, and no conclusion about Corollary 1.2's status, is
drawn here or anywhere in this run's artifacts; that is gated on an
independent C1 (source-transcription-fidelity) review not performed by this
task.

MODEL (transcribed, as held, from experiments/EXP-JMV-004/cost_model.py's
module docstring and research/JMV004_branch_a_scouting_20260726.md -- see
source_statements.md in this run directory for the archived verbatim text
and its UNCHECKED-AGAINST-SOURCE banner):

  m       = (log q)^(2+delta)                        [Thm 1.1, m = p(log q)]
  k       = lambda_triv ~ #{split p <= m} ~ pi(m)/2  [Sec 4.3]  (PRIMARY degree convention)
            alt. degree convention: k = pi(m)         (each split prime contributes
            2 generators rather than 1; see cost_model.md E2 reconciliation)
  c       = C * m^(1/2) * log|mD|,  |D| <= 4q         [Lemma 4.1]  (C UNPINNED, swept)
  r       >= log(2h/|S|^(1/2)) / log(k/c)             [Prop 3.1]
  h       ~ sqrt(|D|) ~ sqrt(q)                        [class number, order of magnitude]
  cost    = r * (per-step isogeny cost at chosen l)

pi(m) is evaluated as the offset logarithmic integral Li(m) = li(m) - li(2)
(mpmath.li(m, offset=True)) at high precision, replacing the scouting
script's numerical-integration approximation of the same standard
number-theoretic estimator with an exact (to working precision) evaluation
of the same closed form. This is a precision improvement of the
IMPLEMENTATION, not a change to the transcribed MODEL.

Precision: mpmath with mp.dps = 60 decimal digits throughout. The headline
quantity (sign of log(k/c)) is obtained from the sign of (k/c - 1) computed
at this precision; a cell is flagged INDETERMINATE_AT_PRECISION if
|log(k/c)| < 10^-40 (far above the ~10^-60 floor of the working precision),
which did not occur in this run (see raw.json "indeterminate_cells").

No randomness anywhere; seeds are not applicable (deterministic arithmetic).
"""
import json
import math
import sys
import time

import mpmath as mp

mp.mp.dps = 60  # 60 decimal digits of working precision throughout

# ---------------------------------------------------------------------------
# Grid (from specification.yaml's inputs block, verbatim values)
# ---------------------------------------------------------------------------
Q_BIT_SIZES = [64, 96, 128, 160, 192, 224, 256, 320, 384, 512]
DELTA_VALUES = [0.25, 0.5, 1.0, 2.0]
LOG_CONVENTIONS = ["bits", "natural"]  # applies ONLY to "log q" inside m = (log q)^(2+delta)
# C: Lemma 4.1's implied constant. The transcribed source states only that it
# is "absolute" and gives no numeric value (see source_statements.md,
# CRITICAL HONESTY NOTE 1). It cannot be pinned without the Bach-Sorenson
# explicit constants (JMV ref [2]), which are NOT held anywhere in this
# repository's corpus. Per stopping_rules ("a needed explicit constant with
# no traceable citation -> not_computable_without_citation, do not proceed
# with an invented value"), a single numeric C is NOT asserted. Instead C is
# SWEPT over this representative set (matching the held scouting precedent)
# and the threshold behaviour in C is reported as-is; this is disclosure of
# non-pin-ability, not an invented value.
C_SWEEP = [mp.mpf("0.5"), mp.mpf(1), mp.mpf(2), mp.mpf(4), mp.mpf(8)]
C_NOT_COMPUTABLE_NOTE = (
    "C is the implied absolute constant of Lemma 4.1 as transcribed; the "
    "source states no numeric value. A single pinned C requires the "
    "Bach-Sorenson explicit constants (JMV ref [2]), not held in this "
    "repository's corpus. Recorded as not_computable_without_citation for "
    "a single value; swept instead over {0.5,1,2,4,8} per the held "
    "scouting precedent."
)

# eps: a statistical parameter appearing in Prop 3.1's r-formula via
# |S| = eps * h as transcribed/implemented in the scouting script. It is
# NOT a paper-stated numeric constant -- no citation for a specific value is
# held anywhere in this repository's corpus. It is a DECLARED, EXPERIMENTER-
# CHOSEN assumption (a conventional "order-1 fraction" placeholder), not a
# value from Lemma 4.1 or Prop 3.1 themselves. Its effect is disclosed
# below: it enters r only inside a logarithm, and (critically) it has NO
# EFFECT AT ALL on the sign of log(k/c), which depends only on k and c.
EPS_DECLARED = mp.mpf("0.5")
EPS_SENSITIVITY = [mp.mpf("0.1"), mp.mpf("0.5"), mp.mpf("0.9")]

# Per-step cost variants. The FROZEN SPECIFICATION's own method (item 4)
# requires only the root-finding-on-Phi_l cost (JMV Sec 4.1 / Galbraith,
# O(l^3)) at "typical l" and "best-case l=2". The held cost_model.py
# scouting script additionally reports two OPTIMISTIC LOWER-BOUND
# alternatives (plain Velu O(l); sqrt-Velu O(sqrt(l)), BDLS 2020) with an
# explicit caveat that they assume a kernel point is already in hand, which
# the theorem's random-split-prime generator set does NOT generally
# provide (see source_statements.md / cost_model.md "applicability
# caveat"). All three are reported for completeness and transparency
# (strictly more disclosure than the frozen method alone requires), with
# the O(l^3) row marked PRIMARY / APPLICABLE and the other two marked
# OPTIMISTIC / CAVEATED, never as the headline figure.
PER_STEP_ALGOS = {
    "phi_l_O(l^3)_JMV_Sec4.1": (lambda l: l ** 3, "PRIMARY_APPLICABLE"),
    "velu_O(l)_classical": (lambda l: l, "OPTIMISTIC_CAVEATED_kernel_point_assumed"),
    "sqrt_velu_O(sqrt_l)_BDLS2020": (lambda l: mp.sqrt(l), "OPTIMISTIC_CAVEATED_kernel_point_assumed"),
}
L_CHOICES = {
    "typical_l_theta_m": None,  # filled in with m at evaluation time
    "best_case_l_2": mp.mpf(2),
}


def li_offset(x):
    """pi(x) estimator: offset logarithmic integral Li(x) = li(x) - li(2)."""
    return mp.li(x, offset=True)


def sign_of(x):
    if x > 0:
        return "positive"
    if x < 0:
        return "negative"
    return "zero"


def compute_cell(bits, delta, convention, C):
    """Evaluate the model at one (bits, delta, log convention, C) point.

    Returns a dict with both degree conventions computed side by side.
    """
    bits_mp = mp.mpf(bits)
    delta_mp = mp.mpf(str(delta))
    ln2 = mp.log(2)
    ln_q = bits_mp * ln2  # natural log of q = 2^bits, ALWAYS natural log (this
    # is not the ambiguous "log q" of Thm 1.1's m-formula; it is q's actual
    # natural logarithm, needed for c's log|mD| term and for h ~ sqrt(q)).

    q_log_for_m = bits_mp if convention == "bits" else ln_q
    m = q_log_for_m ** (2 + delta_mp)

    if m < 3:
        return {"m": m, "not_computable": "m<3, pi(m) estimator undefined at this scale"}

    k_half = li_offset(m) / 2       # PRIMARY degree convention: split primes as pairs [Sec 4.3]
    k_full = li_offset(m)           # ALTERNATE: each split prime contributes 2 generators

    ln4 = mp.log(4)
    ln_D_m = ln4 + ln_q + mp.log(m)   # log|mD|, |D| <= 4q, natural log throughout [Lemma 4.1]
    c = C * mp.sqrt(m) * ln_D_m

    ratio_half = k_half / c
    ratio_full = k_full / c

    result = {
        "m": m, "k_half": k_half, "k_full": k_full, "c": c,
        "ratio_half": ratio_half, "ratio_full": ratio_full,
        "sign_half": sign_of(ratio_half - 1),
        "sign_full": sign_of(ratio_full - 1),
        "log_kc_half": (mp.log(ratio_half) if ratio_half > 0 else None),
        "log_kc_full": (mp.log(ratio_full) if ratio_full > 0 else None),
    }
    result["degree_convention_flip"] = (result["sign_half"] != result["sign_full"])

    ln_h = mp.mpf("0.5") * ln_q  # h ~ sqrt(q) [class number, order of magnitude]

    def walk_length(ratio, eps):
        if ratio <= 1:
            return None
        ln_S = mp.log(eps) + ln_h
        return (ln2 + ln_h - mp.mpf("0.5") * ln_S) / mp.log(ratio)

    r_half = walk_length(ratio_half, EPS_DECLARED)
    result["r_half"] = r_half

    rho = mp.mpf(2) ** (bits_mp / 2)  # sqrt(n) group operations, Pollard rho
    result["rho"] = rho

    costs = {}
    if r_half is not None:
        for algo_name, (f, status) in PER_STEP_ALGOS.items():
            for l_name, l_fixed in L_CHOICES.items():
                l_val = m if l_fixed is None else l_fixed
                per_step_cost = f(l_val)
                total_cost = r_half * per_step_cost
                variant = f"{algo_name}__{l_name}"
                costs[variant] = {
                    "status": status,
                    "l": l_val,
                    "per_step_cost": per_step_cost,
                    "total_cost": total_cost,
                    "cost_over_rho": total_cost / rho,
                    "cheaper_than_rho": bool(total_cost < rho),
                }
    result["costs"] = costs

    # Precomputation term (E4): storage figure for Phi_l for the typical l
    # actually used at this cell (order of magnitude, per specification.yaml
    # method item 5: "Phi_l has on the order of l^2 coefficients").
    typical_l = m
    result["phi_l_storage_coeffs_order"] = typical_l ** 2  # per specification.yaml's own method text
    # Aggregate storage if the FULL generating set's Phi_l's were all
    # precomputed and cached (one Phi_l per distinct split prime <= m,
    # order-of-magnitude only): ~ k_half distinct primes, each ~ typical_l^2
    # coefficients (since a "typical" split prime <= m is Theta(m)).
    result["phi_l_full_set_storage_coeffs_order"] = k_half * (typical_l ** 2)

    return result


def to_jsonable(obj):
    if isinstance(obj, mp.mpf):
        return mp.nstr(obj, 30)
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    return obj


def main():
    t0 = time.time()
    grid = []
    indeterminate_cells = []
    for bits in Q_BIT_SIZES:
        for delta in DELTA_VALUES:
            for convention in LOG_CONVENTIONS:
                for C in C_SWEEP:
                    cell = compute_cell(bits, delta, convention, C)
                    row = {
                        "bits": bits, "delta": delta,
                        "log_convention": convention, "C": mp.nstr(C, 6),
                        **cell,
                    }
                    if cell.get("log_kc_half") is not None:
                        if abs(cell["log_kc_half"]) < mp.mpf("1e-40"):
                            indeterminate_cells.append((bits, delta, convention, mp.nstr(C, 6)))
                    grid.append(row)

    # log-convention flip check: for each (bits, delta, C), compare sign_half
    # between the two log conventions.
    log_conv_flips = []
    index = {}
    for row in grid:
        key = (row["bits"], row["delta"], row["C"])
        index.setdefault(key, {})[row["log_convention"]] = row["sign_half"]
    for key, byconv in index.items():
        if "bits" in byconv and "natural" in byconv and byconv["bits"] != byconv["natural"]:
            log_conv_flips.append(key)

    # smallest delta with sign_half positive at bits=256, per (log_convention, C)
    smallest_delta_256 = {}
    for convention in LOG_CONVENTIONS:
        for C in C_SWEEP:
            cname = mp.nstr(C, 6)
            candidates = sorted(
                (r for r in grid
                 if r["bits"] == 256 and r["log_convention"] == convention and r["C"] == cname
                 and r["sign_half"] == "positive"),
                key=lambda r: r["delta"])
            key = f"{convention}__C={cname}"
            smallest_delta_256[key] = (candidates[0]["delta"] if candidates else None)

    elapsed = time.time() - t0

    raw = {
        "grid": to_jsonable(grid),
        "log_convention_flips": [list(k) for k in log_conv_flips],
        "smallest_delta_with_positive_sign_at_bits_256": smallest_delta_256,
        "indeterminate_cells": indeterminate_cells,
        "eps_declared": mp.nstr(EPS_DECLARED, 6),
        "eps_sensitivity_note": "eps enters r only inside a log; it does not affect sign(log(k/c)).",
        "precision_dps": mp.mp.dps,
        "elapsed_seconds": elapsed,
        "grid_dims": {
            "q_bit_sizes": Q_BIT_SIZES, "delta_values": DELTA_VALUES,
            "log_conventions": LOG_CONVENTIONS, "C_sweep": [mp.nstr(c, 6) for c in C_SWEEP],
        },
        "cell_count": len(grid),
    }
    with open("raw.json", "w") as f:
        json.dump(raw, f, indent=1)

    print(f"cells computed: {len(grid)}", file=sys.stderr)
    print(f"elapsed: {elapsed:.3f}s", file=sys.stderr)
    print(f"indeterminate_at_precision cells: {len(indeterminate_cells)}", file=sys.stderr)
    print(f"log-convention sign flips (bits vs natural), count: {len(log_conv_flips)}", file=sys.stderr)
    n_degree_flips = sum(1 for r in grid if r.get("degree_convention_flip"))
    print(f"degree-convention sign flips (half vs full), count: {n_degree_flips}", file=sys.stderr)


if __name__ == "__main__":
    main()
