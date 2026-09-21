#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-cell occupancy regression -- TASK-20260803-f7a12c, BATCH-017,
GOAL-MLKEM-003, EXP-MLKEM-011.

OBSERVATIONS ONLY.  Toy tier.  Raw undivided score scale.  NO ML-KEM security
claim in either direction.  AGENTS.md rule 12 stays UNMET and UNWAIVED.
ZERO NEW SAMPLING of the physical system: no G6K, no network, no new .out
bytes.  The only randomness is seeded pseudo-randomness used to build this
script's own synthetic NULL OBJECTS; it is never reported as a measurement of
the archived system.  Every seed is derived from MASTER_SEED below by the
printed rule and is recorded in results.json.

WHAT THIS SCRIPT DOES, and nothing else
---------------------------------------
It executes, verbatim and without redesign, the check specified by the
BATCH-016 red team (RT-20260803-cd747d, objection O-1, field `cheapest_check`):

    "Rerun the archived degree-5 fit on scores 551-851 of the n=43 file, keep
     the 301 per-cell terms t_T = (D_T - mu_T)^2 / (mu_T (1 - h_T)) instead of
     only their mean, and regress them on mu_T/4000.  The floor predicts slope
     -1; Poisson predicts 0.  Calibrate with the producer's own N1 and N2
     generators at the same mu."

plus the same regression on the n=50 file as a second instance, plus the
addition made binding by AMEND-BATCH-017-001 in the BATCH-017 dispatch queue:
report the slope as a FUNCTION OF THE RATE-MODEL DEGREE rather than at the
archived degree alone, because t_T is defined against a FITTED rate model and
therefore inherits the degree choice through both mu_T and h_T.

IMPORTED, NOT RETYPED
---------------------
The rate model, the estimator and both null generators are IMPORTED from the
archived BATCH-015 producer script

  coordination/goals/GOAL-MLKEM-003/batches/BATCH-015/tasks/
      TASK-20260803-d9afbd/anom5_investigation.py

by file path (the directory names contain hyphens, so importlib is used).
Imported and used unmodified: ingest, regions, increments, glm, phi_of,
floors, pearson_residuals, autocorr, poisson_sample (N1), binomial_sample
(N2), FILES, DATA.  Its sha256 is recorded in results.json.  Nothing in that
module is monkey-patched; `main()` is never called (it is guarded by
`if __name__ == "__main__"`).

The REGRESSION step itself is implemented here because it does not exist in
the archive.  Established by

    find coordination/goals/GOAL-MLKEM-003/batches/BATCH-016 -type f

which returns exactly two files, objections.md and red_team_report.yaml, and
no script; and by

    find coordination/goals/GOAL-MLKEM-003/batches/BATCH-015 -type f

which returns anom5_investigation.py, report.md, results.json (plus the
validator's two files and the two archive receipts).  So the BATCH-016
regression code is not in the archive and cannot be imported; the BATCH-015
rate model and generators are, and are imported.

HETEROSCEDASTICITY AND THE SHARED RATE MODEL
--------------------------------------------
The 301 (resp. 496) per-cell terms t_T are neither homoscedastic nor
independent:

  * Var(t_T) = (2 + 1/mu_T) / (1 - h_T)^2 under the Poisson null, which varies
    across the band by two orders of magnitude in mu_T; and
  * every t_T is computed against ONE fitted rate model, so the fit residuals
    are constrained (P linear constraints for a degree P-1 basis) and the
    leverages h_T couple the cells.  The terms are correlated by construction
    even if the underlying counts are independent.

An ordinary-least-squares standard error for the slope assumes neither
condition and would be WRONG.  This script therefore:

  1. reports the OLS standard error only as a labelled diagnostic, marked
     INVALID_DO_NOT_QUOTE, together with the ratio of the true (calibrated)
     null sd to it, so the size of the error is visible; and
  2. obtains the slope's standard error EMPIRICALLY, by pushing each null
     replicate through the IDENTICAL instrument -- generate counts at the
     fitted mu, REFIT the same-degree GLM to the replicate, recompute mu*, h*,
     t*, occupancy*, and regress -- so the null slope distribution carries the
     same heteroscedasticity, the same fit-induced dependence, the same
     leverage and the same edge asymmetry as the observed statistic.  The
     standard deviation of that distribution IS the reported standard error,
     separately under N1 and under N2.

No closed-form variance formula for the slope is used anywhere.

REGRESSOR CONVENTION
--------------------
Primary ("identical instrument"): x_T = mu_T / nb_iteration with mu_T taken
from the fit of whatever data set is being analysed -- the archived counts for
the observation, the replicate's own refit for a null replicate.  Secondary
diagnostic: x_T from the GENERATING mu for null replicates.  Both are
reported; they answer slightly different questions and neither is hidden.

nb_iteration is 4000 for the n=43 file (the "mu_T/4000" of the specification)
and 6000 for the n=50 file; the general form mu_T/nb_iteration is used so the
second instance is the same statistic.

Usage:  python3 percell_occupancy_regression.py [--reps 400] [--out results.json]
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import random
import subprocess
import sys
import time

REPO = "/home/user/crypto-autoresearcher"
B15_SCRIPT = os.path.join(
    REPO,
    "coordination/goals/GOAL-MLKEM-003/batches/BATCH-015/tasks/"
    "TASK-20260803-d9afbd/anom5_investigation.py",
)

# Seeds.  Chosen by this execution (attempt 2); disclosed here and in
# results.json.  MASTER_SEED is today's date, 2026-08-06.  Every stream seed is
#     MASTER_SEED + 100000 * file_index + 1000 * degree + null_index
# with file_index 0 for n43 and 1 for n50, and null_index 1 for N1 and 2 for N2.
MASTER_SEED = 20260806

DEGREES = [2, 3, 4, 5, 6, 7, 8]
ARCHIVED_DEGREE = {"n43": 5, "n50": 3}   # BATCH-014 forward selection; used by
                                         # BATCH-015 and BATCH-016.


# --------------------------------------------------------------------------
# import the archived producer module
# --------------------------------------------------------------------------

def load_batch015():
    spec = importlib.util.spec_from_file_location("anom5_b015", B15_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    try:
        return subprocess.run(["git", "-C", REPO] + list(args),
                              capture_output=True, text=True,
                              timeout=60).stdout.strip()
    except Exception as exc:                                # pragma: no cover
        return "unavailable: %r" % (exc,)


# --------------------------------------------------------------------------
# the regression (the only new arithmetic in this task)
# --------------------------------------------------------------------------

def percell_terms(D, mu, h):
    """t_T = (D_T - mu_T)^2 / (mu_T (1 - h_T)).

    Identical, term by term, to the summands of BATCH-015's phi_of(); their
    mean is phi.  Kept instead of collapsed, which is the whole point."""
    return [(D[i] - mu[i]) ** 2 / (mu[i] * (1.0 - h[i])) for i in range(len(D))]


def ols(x, y, w=None):
    """Slope and intercept of y on x.

    `w` weights the POINT ESTIMATE only (secondary diagnostic).  The returned
    `se_*` are the textbook homoscedastic-independent OLS standard errors and
    are INVALID for this problem -- see the module docstring.  They are
    returned solely so the report can quantify how wrong they are."""
    n = len(x)
    if w is None:
        w = [1.0] * n
    sw = sum(w)
    mx = sum(w[i] * x[i] for i in range(n)) / sw
    my = sum(w[i] * y[i] for i in range(n)) / sw
    sxx = sum(w[i] * (x[i] - mx) ** 2 for i in range(n))
    sxy = sum(w[i] * (x[i] - mx) * (y[i] - my) for i in range(n))
    if sxx <= 0.0:
        return None, None, None, None
    b = sxy / sxx
    a = my - b * mx
    resid = [y[i] - (a + b * x[i]) for i in range(n)]
    if n > 2:
        s2 = sum(w[i] * resid[i] ** 2 for i in range(n)) / (n - 2)
        se_b = math.sqrt(s2 / sxx)
        se_a = math.sqrt(s2 * (1.0 / sw + mx * mx / sxx))
    else:
        se_b = se_a = None
    return b, a, se_b, se_a


def regress_dataset(D, lo, hi, degree, nb, A, x_override=None):
    """Fit the rate model, form the per-cell terms, regress them on occupancy.

    Returns None if the GLM does not converge (a non-converged fit is reported
    as a discard, never as a reading)."""
    try:
        _b, mu, h, _P = A.glm(D, lo, hi, degree)
    except (FloatingPointError, ZeroDivisionError, OverflowError):
        return None
    if min(mu) <= 0.0 or max(h) >= 1.0:
        return None
    t = percell_terms(D, mu, h)
    x = [m / nb for m in mu] if x_override is None else list(x_override)
    b, a, se_b, se_a = ols(x, t)
    if b is None:
        return None
    # variance-weighted point estimate (secondary diagnostic only): the
    # Poisson-null variance of t_T is (2 + 1/mu_T)/(1-h_T)^2.
    w = [(1.0 - h[i]) ** 2 / (2.0 + 1.0 / mu[i]) for i in range(len(D))]
    bw, aw, _sb, _sa = ols(x, t, w)
    phi = sum(t) / len(t)
    e = A.pearson_residuals(D, mu, h)
    r1 = A.autocorr(e, 1)[0]
    out = dict(slope=b, intercept=a, slope_weighted=bw, intercept_weighted=aw,
               ols_se_slope_INVALID_DO_NOT_QUOTE=se_b,
               ols_se_intercept_INVALID_DO_NOT_QUOTE=se_a,
               phi=phi, residual_lag1_autocorrelation=r1)
    if x_override is None:
        out["_mu"] = mu
        out["_h"] = h
    return out


def mean_sd(v):
    n = len(v)
    if n == 0:
        return None, None
    m = sum(v) / n
    s = math.sqrt(sum((z - m) ** 2 for z in v) / (n - 1)) if n > 1 else 0.0
    return m, s


def quantile(sorted_v, p):
    if not sorted_v:
        return None
    return sorted_v[min(len(sorted_v) - 1,
                        max(0, int(round(p * (len(sorted_v) - 1)))))]


def calibrate(mu_fit, lo, hi, degree, nb, gen, reps, seed, A, observed):
    """Push `reps` null replicates through the IDENTICAL instrument.

    gen(m, rng) draws one cell's count at fitted rate m.  Each replicate is
    REFIT at the same degree, so mu*, h*, the per-cell terms, the occupancy
    regressor and the regression are all recomputed exactly as for the
    observation.  The sd of the resulting slope distribution is the reported
    standard error; no closed form is used."""
    rng = random.Random(seed)
    x_gen = [m / nb for m in mu_fit]
    slopes, inters, slopes_w, slopes_alt, phis, r1s = [], [], [], [], [], []
    discarded = 0
    for _ in range(reps):
        Ds = [gen(m, rng) for m in mu_fit]
        r = regress_dataset(Ds, lo, hi, degree, nb, A)
        if r is None or not math.isfinite(r["slope"]):
            discarded += 1
            continue
        ralt = regress_dataset(Ds, lo, hi, degree, nb, A, x_override=x_gen)
        slopes.append(r["slope"])
        inters.append(r["intercept"])
        slopes_w.append(r["slope_weighted"])
        phis.append(r["phi"])
        r1s.append(r["residual_lag1_autocorrelation"])
        if ralt is not None and math.isfinite(ralt["slope"]):
            slopes_alt.append(ralt["slope"])
    if not slopes:
        return dict(replicates=0, replicates_discarded=discarded,
                    note="every replicate discarded; no calibration available")
    ms, ss = mean_sd(slopes)
    mi, si = mean_sd(inters)
    mw, sw = mean_sd(slopes_w)
    ma, sa = mean_sd(slopes_alt)
    mp, sp = mean_sd(phis)
    mr, _sr = mean_sd(r1s)
    srt = sorted(slopes)
    obs = observed["slope"]
    n_ge = sum(1 for s in slopes if s >= obs)
    n_le = sum(1 for s in slopes if s <= obs)
    z = (obs - ms) / ss if ss else None
    # Deflation convention carried over from BATCH-016 for comparability only:
    # it inflates the null sd by sqrt(1 + 2 rho_1) using the OBSERVED residual
    # lag-1 autocorrelation.  It is a heuristic for a mean-like statistic, not
    # a derived correction for a slope, and is labelled as such.
    r1obs = observed["residual_lag1_autocorrelation"]
    defl = math.sqrt(1.0 + 2.0 * r1obs) if (1.0 + 2.0 * r1obs) > 0 else None
    return dict(
        replicates=len(slopes), replicates_discarded=discarded, seed=seed,
        slope_mean=ms, slope_sd_CALIBRATED_STANDARD_ERROR=ss,
        slope_p05=quantile(srt, 0.05), slope_p95=quantile(srt, 0.95),
        slope_min=srt[0], slope_max=srt[-1],
        intercept_mean=mi, intercept_sd_CALIBRATED_STANDARD_ERROR=si,
        slope_weighted_mean=mw, slope_weighted_sd=sw,
        slope_mean_regressor_from_generating_mu=ma,
        slope_sd_regressor_from_generating_mu=sa,
        z_of_observed_slope=z,
        z_of_observed_slope_after_lag1_deflation=(
            (obs - ms) / (ss * defl) if (ss and defl) else None),
        lag1_deflation_factor_applied=defl,
        empirical_fraction_of_null_slopes_ge_observed=n_ge / float(len(slopes)),
        empirical_fraction_of_null_slopes_le_observed=n_le / float(len(slopes)),
        mean_phi_of_null=mp, sd_phi_of_null=sp,
        mean_residual_lag1_of_null=mr,
        ratio_calibrated_sd_to_ols_se=(
            ss / observed["ols_se_slope_INVALID_DO_NOT_QUOTE"]
            if observed["ols_se_slope_INVALID_DO_NOT_QUOTE"] else None),
    )


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=400)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    out_path = args.out or os.path.join(here, "results.json")

    t0 = time.time()
    A = load_batch015()

    R = dict(
        task_id="TASK-20260803-f7a12c",
        batch_id="BATCH-017",
        goal_id="GOAL-MLKEM-003",
        experiment_id="EXP-MLKEM-011",
        title=("Per-cell occupancy regression of the Pearson terms "
               "t_T = (D_T - mu_T)^2 / (mu_T (1 - h_T)) on per-iteration "
               "occupancy mu_T / nb_iteration, calibrated under BATCH-015's "
               "N1 and N2 null generators, as a function of the rate-model "
               "degree"),
        execution_attempt=2,
        execution_attempt_note=(
            "Attempt 1 of this task was lost to a session container reset "
            "before any snapshot commit; it produced no surviving artifact. "
            "Under AGENTS.md rule 5 that loss is not evidence in any "
            "direction, and under rule 9 its unarchived numbers are not "
            "recorded, cited or compared against here.  This run was executed "
            "from the archived inputs alone, with seeds chosen by this "
            "execution and disclosed below.  See AMEND-BATCH-017-001."),
        specification_source=(
            "BATCH-016 RT-20260803-cd747d objection O-1 field cheapest_check, "
            "executed verbatim; plus AMEND-BATCH-017-001 (degree sensitivity) "
            "in coordination/goals/GOAL-MLKEM-003/batches/BATCH-017/"
            "dispatch_queue.json"),
        scope=dict(
            tier="toy",
            parameters="q=241, m=40, n=43 (nb_iteration 4000) and n=50 (nb_iteration 6000)",
            scale="raw undivided score scale",
            band="mid band 1000 <= C_T < 1e5, as defined by BATCH-015 regions()",
            mlkem_security_claim="NONE, in either direction",
            rule_12="UNMET and UNWAIVED; EV-MLKEM-011/013/017 keep their "
                    "status; KN-FIND-031 stays withdrawn",
            role="executor: OBSERVATIONS ONLY; no adjudication of whether the "
                 "floor is the right reference point, and no statement about "
                 "Approximation 4.9"),
        new_sampling_of_physical_system=(
            "NONE.  No G6K, no network, no new .out bytes.  The three archived "
            "files were read; only the two Pwrong files were used."),
        seeded_randomness=dict(
            master_seed=MASTER_SEED,
            rule=("stream seed = MASTER_SEED + 100000*file_index + "
                  "1000*degree + null_index, file_index 0=n43 1=n50, "
                  "null_index 1=N1 2=N2"),
            generator="python random.Random (Mersenne Twister)",
            declared=("SYNTHETIC and SEEDED.  Used only to build this script's "
                      "own null objects.  Never a measurement of the archived "
                      "system."),
            chosen_by=("this execution, attempt 2.  The seeds of the lost "
                       "attempt 1 are unknown to this run and were not sought.")),
        imported_from=dict(
            path=os.path.relpath(B15_SCRIPT, REPO),
            sha256=sha256_file(B15_SCRIPT),
            functions=["ingest", "regions", "increments", "glm", "phi_of",
                       "floors", "pearson_residuals", "autocorr",
                       "poisson_sample (N1)", "binomial_sample (N2)",
                       "FILES", "DATA"],
            note=("imported unmodified by file path; main() not called.  The "
                  "regression step is implemented in this script because it "
                  "is not in the archive: `find coordination/goals/"
                  "GOAL-MLKEM-003/batches/BATCH-016 -type f` returns only "
                  "objections.md and red_team_report.yaml.")),
        heteroscedasticity_and_dependence=dict(
            problem=("the per-cell terms are heteroscedastic "
                     "(Var(t_T) = (2 + 1/mu_T)/(1-h_T)^2 under the Poisson "
                     "null) and are NOT independent: they are all formed "
                     "against one fitted rate model, which imposes P linear "
                     "constraints on the residuals and couples the cells "
                     "through the leverages h_T."),
            treatment=("the slope's standard error is MEASURED, not derived: "
                       "each null replicate is generated at the fitted mu and "
                       "then pushed through the identical instrument -- refit "
                       "at the same degree, recompute mu*, h*, t*, the "
                       "occupancy regressor and the regression -- so the null "
                       "slope distribution inherits the same "
                       "heteroscedasticity, the same fit-induced dependence "
                       "and the same edge/leverage geometry.  Its standard "
                       "deviation is the reported standard error."),
            ols_se=("reported ONLY as a labelled diagnostic under the key "
                    "ols_se_slope_INVALID_DO_NOT_QUOTE, together with "
                    "ratio_calibrated_sd_to_ols_se.  It assumes homoscedastic "
                    "independent errors, which is false here, and it is not "
                    "used for any inference in this package.")),
        environment=dict(
            python_version=sys.version,
            platform=platform.platform(),
            git_commit=git("rev-parse", "HEAD"),
            git_dirty_tree=bool(git("status", "--porcelain")),
            git_status_porcelain=git("status", "--porcelain"),
            replicates_per_null_per_degree=args.reps,
            degrees_swept=DEGREES,
            archived_degrees=ARCHIVED_DEGREE),
        files=[],
    )

    print("percell_occupancy_regression.py -- TASK-20260803-f7a12c (BATCH-017)")
    print("OBSERVATIONS ONLY.  Toy tier.  No ML-KEM security claim.  "
          "Zero new sampling of the physical system.")
    print("master seed %d ; %d replicates per null per degree ; degrees %s"
          % (MASTER_SEED, args.reps, DEGREES))
    print("")

    for fi, spec in enumerate(A.FILES):
        d = A.ingest(spec)
        reg = A.regions(d)
        lo, hi = reg["mid"]
        D = A.increments(d, lo, hi)
        nb = d["nb_iteration"]
        tag = d["tag"]
        fout = dict(
            tag=tag, name=d["name"], sha256=d["sha256"],
            nb_iteration=nb, M=d["M"],
            mid_band_score_range=[lo, hi], n_cells=len(D),
            archived_degree=ARCHIVED_DEGREE[tag],
            total_increment_events=sum(D),
            min_increment=min(D), max_increment=max(D),
            per_degree=[])
        print("=== %s : mid band scores %d..%d, %d cells, nb_iteration=%d"
              % (tag, lo, hi, len(D), nb))

        for deg in DEGREES:
            obs = regress_dataset(D, lo, hi, deg, nb, A)
            if obs is None:
                fout["per_degree"].append(dict(
                    degree=deg, converged=False,
                    note="GLM did not converge; reported as a failure, not as "
                         "a reading"))
                print("  degree %d: GLM DID NOT CONVERGE" % deg)
                continue
            mu = obs.pop("_mu")
            h = obs.pop("_h")
            fl = A.floors(mu, nb, d["M"])
            occ = [m / nb for m in mu]
            row = dict(
                degree=deg, converged=True,
                is_archived_degree=bool(deg == ARCHIVED_DEGREE[tag]),
                phi_whole_band=obs["phi"],
                floor_independent_iterations=fl["floor_independent_iterations"],
                floor_applicable=fl["floor_independent_iterations_applicable"],
                max_per_iteration_occupancy=fl["max_per_iteration_occupancy"],
                mean_per_iteration_occupancy=fl["mean_per_iteration_occupancy"],
                min_per_iteration_occupancy=min(occ),
                min_fitted_rate=min(mu), max_leverage=max(h),
                observed=dict(
                    slope=obs["slope"], intercept=obs["intercept"],
                    slope_variance_weighted_SECONDARY=obs["slope_weighted"],
                    intercept_variance_weighted_SECONDARY=obs["intercept_weighted"],
                    ols_se_slope_INVALID_DO_NOT_QUOTE=obs["ols_se_slope_INVALID_DO_NOT_QUOTE"],
                    ols_se_intercept_INVALID_DO_NOT_QUOTE=obs["ols_se_intercept_INVALID_DO_NOT_QUOTE"],
                    residual_lag1_autocorrelation=obs["residual_lag1_autocorrelation"]),
                nulls=dict())

            print("  degree %d: phi=%.5f floor=%.5f (applicable %s, max occ "
                  "%.4f)  observed slope=%+.4f intercept=%+.4f"
                  % (deg, obs["phi"], fl["floor_independent_iterations"],
                     fl["floor_independent_iterations_applicable"],
                     fl["max_per_iteration_occupancy"],
                     obs["slope"], obs["intercept"]))

            # ---- N1: independent Poisson at the fitted rate ----------------
            seed1 = MASTER_SEED + 100000 * fi + 1000 * deg + 1
            n1 = calibrate(mu, lo, hi, deg, nb,
                           lambda m, rng: A.poisson_sample(m, rng),
                           args.reps, seed1, A, obs)
            n1["generator"] = ("N1 independent Poisson at the fitted rate "
                               "(BATCH-015 poisson_sample); predicts slope 0")
            row["nulls"]["N1_independent_poisson"] = n1
            print("      N1 slope %+0.4f +/- %0.4f  z=%s  (intercept %+0.4f "
                  "+/- %0.4f)"
                  % (n1["slope_mean"], n1["slope_sd_CALIBRATED_STANDARD_ERROR"],
                     ("%+.2f" % n1["z_of_observed_slope"])
                     if n1["z_of_observed_slope"] is not None else "n/a",
                     n1["intercept_mean"],
                     n1["intercept_sd_CALIBRATED_STANDARD_ERROR"]))

            # ---- N2: minimum-variance independent iterations ---------------
            if fl["floor_independent_iterations_applicable"]:
                seed2 = MASTER_SEED + 100000 * fi + 1000 * deg + 2
                n2 = calibrate(mu, lo, hi, deg, nb,
                               lambda m, rng: A.binomial_sample(nb, m / nb, rng),
                               args.reps, seed2, A, obs)
                n2["generator"] = (
                    "N2 minimum-variance independent-iteration member, "
                    "Binomial(nb_iteration, mu_T/nb_iteration) (BATCH-015 "
                    "binomial_sample) -- the floor-attaining member; predicts "
                    "slope -1")
                row["nulls"]["N2_minimum_variance_independent_iterations"] = n2
                print("      N2 slope %+0.4f +/- %0.4f  z=%s  (intercept "
                      "%+0.4f +/- %0.4f)"
                      % (n2["slope_mean"],
                         n2["slope_sd_CALIBRATED_STANDARD_ERROR"],
                         ("%+.2f" % n2["z_of_observed_slope"])
                         if n2["z_of_observed_slope"] is not None else "n/a",
                         n2["intercept_mean"],
                         n2["intercept_sd_CALIBRATED_STANDARD_ERROR"]))
            else:
                row["nulls"]["N2_minimum_variance_independent_iterations"] = None
                row["nulls"]["N2_not_run_reason"] = fl[
                    "floor_independent_iterations_note"]
                print("      N2 NOT RUN: %s"
                      % fl["floor_independent_iterations_note"])

            fout["per_degree"].append(row)

        # reproduction check at the archived degree, stated as what it is
        arch = [r for r in fout["per_degree"]
                if r.get("is_archived_degree") and r.get("converged")]
        if arch:
            fout["archived_degree_reproduction"] = dict(
                degree=arch[0]["degree"],
                phi=arch[0]["phi_whole_band"],
                floor=arch[0]["floor_independent_iterations"],
                note=("phi and the floor are recomputed with BATCH-015's own "
                      "glm/phi_of/floors, deliberately reused so the per-cell "
                      "terms are the same object the producer summed.  This "
                      "agreement is NOT an independent check -- it is the same "
                      "route by construction.  The new content is the "
                      "decomposition."))
        R["files"].append(fout)
        print("")

    # ---------------- degree-sensitivity summary --------------------------
    summary = dict()
    for f in R["files"]:
        rows = [r for r in f["per_degree"] if r.get("converged")]
        slopes = [r["observed"]["slope"] for r in rows]
        zs_n1, zs_n2 = [], []
        for r in rows:
            n1 = r["nulls"].get("N1_independent_poisson")
            n2 = r["nulls"].get("N2_minimum_variance_independent_iterations")
            if n1 and n1.get("z_of_observed_slope") is not None:
                zs_n1.append((r["degree"], n1["z_of_observed_slope"]))
            if n2 and n2.get("z_of_observed_slope") is not None:
                zs_n2.append((r["degree"], n2["z_of_observed_slope"]))
        summary[f["tag"]] = dict(
            degrees=[r["degree"] for r in rows],
            observed_slope_by_degree=dict(
                (str(r["degree"]), r["observed"]["slope"]) for r in rows),
            observed_intercept_by_degree=dict(
                (str(r["degree"]), r["observed"]["intercept"]) for r in rows),
            slope_min_over_degrees=min(slopes) if slopes else None,
            slope_max_over_degrees=max(slopes) if slopes else None,
            slope_range_over_degrees=(max(slopes) - min(slopes)) if slopes else None,
            slope_sign_constant_over_degrees=bool(
                slopes and (all(s > 0 for s in slopes) or all(s < 0 for s in slopes))),
            z_vs_N1_by_degree=dict((str(k), v) for k, v in zs_n1),
            z_vs_N2_by_degree=dict((str(k), v) for k, v in zs_n2),
            z_vs_N2_min=min([v for _k, v in zs_n2]) if zs_n2 else None,
            z_vs_N2_max=max([v for _k, v in zs_n2]) if zs_n2 else None,
            z_vs_N1_min=min([v for _k, v in zs_n1]) if zs_n1 else None,
            z_vs_N1_max=max([v for _k, v in zs_n1]) if zs_n1 else None,
        )
    R["degree_sensitivity_summary"] = summary
    R["non_claims"] = [
        "No statement is made about whether the occupancy floor is or is not "
        "the right reference point; that adjudication belongs to the "
        "Coordinator.",
        "No statement is made about Approximation 4.9 being validated or "
        "refuted.",
        "No ML-KEM or Kyber security claim, in either direction.",
        "The lost attempt-1 outputs are not reconstructed, quoted or compared "
        "against; they do not exist on disk.",
        "A minimum over a family is not the expected value of the statistic: "
        "the floor value is a minimum, and N2 is the member attaining it, not "
        "a preferred description of the process.",
    ]
    R["elapsed_seconds"] = time.time() - t0

    with open(out_path, "w") as fh:
        json.dump(R, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print("wrote %s  (%.1f s)" % (out_path, R["elapsed_seconds"]))


if __name__ == "__main__":
    main()
