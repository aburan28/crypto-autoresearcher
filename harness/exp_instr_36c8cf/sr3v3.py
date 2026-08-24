"""THE SR3 v3 REFERENCE CHARACTERISATION for EXP-INSTR-36c8cf, contract v2.

WHAT THIS MEASURES, AND WHAT IT DELIBERATELY DOES NOT.

The frozen contract's `characterisation_procedure` says: "For each density row:
re-measure THE REFERENCE RUN at ITS OWN frozen parameters (its declared
factor-base sizes, target count, sampler, class selection rule) across the
declared seed set; record the empirical sampling distribution of the
variance-ratio statistic AT THAT ROW". The reference runs are named explicitly
by `refvalues_v2.sr3v3_reference_runs()` and every parameter used here is read
from their own records at run time.

THE SAMPLER IS THEREFORE THE REFERENCE RUN'S OWN SAMPLER, `exp_icinv.
targets_uniform`, called unmodified through the committed reference driver's own
code path. See CONFLICT-1 in the run record and in the execution report: the
dispatching envelope carries a standing control "targets_B, never
targets_uniform", which cannot apply to a faithful RE-MEASUREMENT of a run whose
statistic is defined by the sampler it used -- substituting a different sampler
would characterise a different estimand and would make C-SELF-CONSISTENCY
vacuous. The conflict is RECORDED FOR COORDINATOR ADJUDICATION, not resolved by
silently choosing, and no sampler other than the reference run's own is used
anywhere in this module.

COST SHARING. The exact m = 3 sum sets are seed-independent and are computed
ONCE per (curve, factor-base size) and reused across every seed -- which the
contract states is what bounds the cost. Because that is a departure in CODE
PATH (not in arithmetic) from the reference driver's own loop, this module
VERIFIES equality against `harness.run_saturation.measure_at_density`, called
unmodified, at every one of the thirteen rows at declared check seeds. A
mismatch is fatal.

NOTHING HERE PLANTS A SIGNAL, DRAWS A CURVE-SIDE CONCLUSION, OR USES NULL-C.
"""
from __future__ import annotations

import math
import statistics
import time
from statistics import NormalDist

from harness import exp_icinv as ex
from harness import isogeny_class as ic
from harness import run_saturation as rs


# --------------------------------------------------------------------------
# class selection -- the reference driver's own rule, re-executed
# --------------------------------------------------------------------------


def select_class(p: int) -> dict:
    """`run_saturation.run`'s own class-selection rule, re-executed here.

    The rule is: certify the census, then take the largest ordinary class under
    `sorted(((len(v), t) ...), reverse=True)[0]`. Copied in BEHAVIOUR from the
    reference driver and then CHECKED against the reference run's own recorded
    target_trace, order and n_curves by the caller; a disagreement is fatal.
    """
    classes = ic.isogeny_classes(p)
    cens = ic.class_census(p, classes)
    if any(not c.agrees for c in cens):
        raise RuntimeError(f"census failed at p={p}: enumeration incomplete")
    ordinary = sorted(((len(v), t) for t, v in classes.items() if t % p != 0),
                      reverse=True)
    trace = ordinary[0][1]
    recs = classes[trace]
    return {"p": p, "target_trace": trace, "order": recs[0].order,
            "n_curves": len(recs), "recs": recs}


# --------------------------------------------------------------------------
# the measurement
# --------------------------------------------------------------------------


def measure(recs, fb_sizes: list[int], T: int, seeds: list[int],
            progress=None) -> dict:
    """hits[(fb_size, seed)] -> per-curve hit counts, sharing the sum sets.

    Also returns each curve's r = #{x : x^3 + ax + b = 0} stratum and each
    (curve, fb) |3V|/#E density, so every row can be reported stratified by r
    (a standing control of this batch: report the strata wherever a target is
    drawn).
    """
    hits: dict[tuple[int, int], list[int]] = {(fb, s): [] for fb in fb_sizes
                                              for s in seeds}
    dens: dict[int, list[float]] = {fb: [] for fb in fb_sizes}
    strata: list[int] = []
    for idx, rec in enumerate(recs):
        E = rec.curve()
        strata.append(ex.two_torsion_x_count(rec.p, rec.a, rec.b))
        tg = {s: ex.targets_uniform(E, rec.order, T, s) for s in seeds}
        for fb_size in fb_sizes:
            fb = ex.factor_base_fixed_size(E, fb_size)
            _, _, three = _sumset_m3(E, fb)
            dens[fb_size].append(len(three) / rec.order)
            for s in seeds:
                hits[(fb_size, s)].append(sum(1 for q in tg[s] if q in three))
        if progress is not None:
            progress(idx + 1, len(recs))
    return {"hits": hits, "densities": dens, "strata": strata,
            "n_curves": len(recs), "T": T, "seeds": list(seeds),
            "fb_sizes": list(fb_sizes)}


def _sumset_m3(E, fb):
    """The exact m = 3 sum set, built exactly as the reference driver builds it
    (`run_saturation.decomposition_rate_m3_with_size`), factored so it can be
    computed once per (curve, fb) and scored against every seed."""
    pts = []
    for x in fb:
        P = E.lift_x(x)
        if P is not None:
            pts.append(P)
            pts.append(E.negate(P))
    two = set()
    for i in range(len(pts)):
        for jx in range(i, len(pts)):
            S = E.add(pts[i], pts[jx])
            if S is not None:
                two.add(S)
    three = set()
    for S in two:
        for R in pts:
            Tp = E.add(S, R)
            if Tp is not None:
                three.add(Tp)
    return pts, two, three


def row_statistic(hits: list[int], T: int) -> dict:
    """THE VARIANCE-RATIO STATISTIC, from the committed NULL-B verdict function
    called unmodified -- the same call `run_saturation.measure_at_density`
    makes."""
    v = ex.binomial_null_verdict("decomp_rate_m3", hits, T)
    return {"variance_ratio": v.ratio, "mean_rate": v.mean,
            "observed_variance": v.variance, "binomial_null_variance": v.null_variance,
            "verdict": v.verdict, "detail": v.detail, "n_curves": v.n_curves}


def stratified_row(hits: list[int], strata: list[int], T: int) -> dict:
    """Per-r-stratum descriptive statistics for one row. REPORTING ONLY: no
    gate, no threshold and no verdict of this contract reads it."""
    out = {}
    for r in sorted(set(strata)):
        h = [x for x, s in zip(hits, strata) if s == r]
        if len(h) < 2:
            out[str(r)] = {"n_curves": len(h), "note": "fewer than 2 curves; "
                                                       "no variance defined"}
            continue
        v = ex.binomial_null_verdict(f"decomp_rate_m3|r={r}", h, T)
        out[str(r)] = {"n_curves": v.n_curves, "mean_rate": v.mean,
                       "variance_ratio": v.ratio, "verdict": v.verdict}
    return out


# --------------------------------------------------------------------------
# the estimator (amendment change G3, E1) and the rung logic (E2, E3)
# --------------------------------------------------------------------------


def z_from_coverage(upper_num: int, upper_den: int) -> dict:
    """z = Phi^{-1}(upper quantile), COMPUTED AT RUN TIME from the frozen exact
    fraction. Transcribing z at any precision is prohibited (standing rule A4);
    the amendment's own approximate value is NOT read and NOT used."""
    q = upper_num / upper_den
    return {"upper_quantile_fraction": f"{upper_num}/{upper_den}",
            "upper_quantile": q,
            "z": NormalDist().inv_cdf(q),
            "computed_by": "statistics.NormalDist().inv_cdf, at run time",
            "transcribed": False}


def interval_for_rung(ratios: list[float], z: float) -> dict:
    """mean +- z * sd over the rung's seeds, with the tail check the contract
    requires (the extreme per-seed ratios at the row, listed not trusted)."""
    finite = [r for r in ratios if math.isfinite(r)]
    n = len(ratios)
    if len(finite) != n:
        return {"n_seeds": n, "non_finite_ratios": n - len(finite),
                "status": "not_computable",
                "reason": "a per-seed variance ratio was not finite"}
    mean = statistics.mean(finite)
    sd = statistics.stdev(finite) if n > 1 else 0.0
    half = z * sd
    return {
        "n_seeds": n,
        "mean": mean,
        "sd_sample_n_minus_1": sd,
        "z": z,
        "half_width": half,
        "interval_low": mean - half,
        "interval_high": mean + half,
        "min_per_seed_ratio": min(finite),
        "max_per_seed_ratio": max(finite),
        "argmin_seed": None,
        "argmax_seed": None,
        "status": "computed",
    }


def rung_seed_sets(contract_seeds: list[int], rungs: list[int],
                   r2_range: list[int], r3_range: list[int]) -> list[dict]:
    """E2. Rung 1 is the contract's twelve declared seeds, unchanged; rung 2
    adds the first declared extension range; rung 3 adds the second."""
    s1 = list(contract_seeds)
    s2 = s1 + list(range(r2_range[0], r2_range[1] + 1))
    s3 = s2 + list(range(r3_range[0], r3_range[1] + 1))
    out = []
    for want, seeds in zip(rungs, (s1, s2, s3)):
        if len(seeds) != want:
            raise RuntimeError(
                f"rung seed set has {len(seeds)} seeds where the amendment "
                f"declares {want}; refusing to proceed on a seed set that does "
                f"not match the frozen declaration")
        if len(set(seeds)) != len(seeds):
            raise RuntimeError("rung seed set contains a duplicate seed")
        out.append({"rung": len(out) + 1, "declared_size": want, "seeds": seeds})
    return out


def stability_check(prev: dict, cur: dict, pct: float) -> dict:
    """E3. The half-width changes by less than `pct`% relative to the previous
    rung at EVERY row -> the characterisation MAY stop at this rung."""
    rows = {}
    for fb in cur:
        p_hw = prev[fb]["half_width"]
        c_hw = cur[fb]["half_width"]
        rel = abs(c_hw - p_hw) / p_hw if p_hw > 0 else float("inf")
        rows[str(fb)] = {"previous_half_width": p_hw, "half_width": c_hw,
                         "relative_change": rel,
                         "within_rule": bool(rel < pct / 100.0)}
    return {"threshold_relative": pct / 100.0,
            "rows": rows,
            "met_at_every_row": all(v["within_rule"] for v in rows.values()),
            "rows_failing": sorted(int(k) for k, v in rows.items()
                                   if not v["within_rule"])}


# --------------------------------------------------------------------------
# faithfulness of the shared-sum-set path against the reference driver
# --------------------------------------------------------------------------


def verify_against_reference_driver(recs, fb_sizes: list[int], T: int,
                                    seed: int, measured: dict) -> dict:
    """Call `run_saturation.measure_at_density` UNMODIFIED at every row and
    require exact equality of the variance ratio with the shared-sum-set path.

    This is what licenses the cost sharing: the two code paths are then known to
    compute the same number, not merely intended to.
    """
    rows = []
    ok = True
    for fb in fb_sizes:
        ref = rs.measure_at_density(recs, fb, T, seed)
        mine = row_statistic(measured["hits"][(fb, seed)], T)
        same = ref["variance_ratio"] == mine["variance_ratio"]
        ok = ok and same
        rows.append({"fb_size": fb, "seed": seed,
                     "reference_driver_variance_ratio": ref["variance_ratio"],
                     "shared_sumset_variance_ratio": mine["variance_ratio"],
                     "exact_match": bool(same),
                     # REPORTED, NOT GATED: the reference driver reports the row
                     # mean as statistics.mean(rates) while the NULL-B verdict
                     # object it also returns computes sum(rates)/n. Those two
                     # aggregations differ in the last bits on some rows in the
                     # reference driver ITSELF; the equality tested above is on
                     # the variance ratio, which is the statistic this
                     # characterisation is of.
                     "reference_driver_mean_rate_statistics_mean": ref["mean_rate"],
                     "verdict_object_mean_rate_sum_over_n": mine["mean_rate"],
                     "mean_rate_absolute_difference":
                         abs(ref["mean_rate"] - mine["mean_rate"])})
    return {"seed": seed, "rows": rows, "all_rows_exact": bool(ok),
            "equality_tested_on": "the variance ratio, bit-exactly",
            "reference_driver": "harness.run_saturation.measure_at_density, "
                                "called unmodified"}


def compare_with_committed(committed_rows: dict, measured: dict, T: int,
                           seed: int) -> dict:
    """The reference run's OWN recorded per-row variance ratios against this
    run's re-measurement at the reference run's own declared seed."""
    rows = []
    ok = True
    for fb, vr in sorted(committed_rows.items()):
        mine = row_statistic(measured["hits"][(int(fb), seed)], T)
        same = vr == mine["variance_ratio"]
        ok = ok and same
        rows.append({"fb_size": int(fb), "committed_variance_ratio": vr,
                     "re_measured_variance_ratio": mine["variance_ratio"],
                     "delta": mine["variance_ratio"] - vr,
                     "relative_delta": (abs(mine["variance_ratio"] - vr) / vr
                                        if vr else None),
                     "exact_match": bool(same)})
    return {"seed_of_the_committed_run": seed, "rows": rows,
            "all_rows_exact": bool(ok),
            "max_relative_delta": max((r["relative_delta"] for r in rows
                                       if r["relative_delta"] is not None),
                                      default=None),
            "note": ("BIT-EXACTNESS ACROSS MACHINES IS NOT ASSERTED AND IS NOT "
                     "GATED ON. The committed reference run was executed on a "
                     "different platform and Python build (see its own "
                     "environment.json); the per-row deltas are reported as "
                     "measured. C-SELF-CONSISTENCY compares THIS RUN'S faithful "
                     "re-measurement against the interval, which is what the "
                     "contract's characterisation_procedure specifies.")}


def timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")
