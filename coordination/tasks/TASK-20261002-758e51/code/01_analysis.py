"""01 -- THE ANALYSIS ATTEMPT of TASK-20261002-758e51 (the single permitted run;
the identity-check rerun after a located defect is the only permitted retry).

ZERO solver/engine execution: nothing under src/crypto_autoresearcher is
imported or executed (attested in receipt.yaml). Only the archived replica
rows (attacks/out/ptm5_results.jsonl) are read; every slope, aggregate,
bootstrap interval and identity check is computed on them.

Conventions, verbatim from the archive (never invented):
  * ratios and the aggregate T field mapping -- attacks/07_ptm5_analysis.py
    (ratios(): frozen S/(0.5 sqrt(r_frozen N)), rank S/(0.5 sqrt(rank N));
    aggregate_T: num = sum S^2/(N B), den = sum r N/4/(N B)) and
    attacks/ptm5_engine.py snapshot() (S = table_s3 + search_s3; r_frozen =
    relations + sum(rows_fed) on mode; rank = the solver rank; PRIMARY stop =
    first row determining k);
  * the slope fit and its interval -- the frozen stats.py bootstrap_slope
    (stratified-by-rung resampling with replacement, one draw per member,
    percentile endpoints by the stats.py index arithmetic), as loaded by path
    by the validator's calibration/f7.py fit(): reps=20000, level=0.95,
    seed=0. stats.py is READ (to recover the algorithm) and REIMPLEMENTED
    here verbatim; it is never imported or executed;
  * the interval calibration -- calibration/f7.py calibrate() (laws gauss,
    t3, empirical; beta0 in {0, slope}; 1000 series; inner interval reps
    2000 seed 0; kappa_95 = zs[ceil(0.95 n)-1]) and calibration/f7_supp.py
    (within_rung_empirical, rung_sd_gauss; rung_sd = pstdev*sqrt(n/(n-1)));
    calibrated interval = [slope - kap (slope - lo), slope + kap (hi - slope)];
  * the per-rung T interval -- the round's curve bootstrap at the engine's
    five-per-rung design (attacks/09_agg_by_rung.py: np.quantile at
    0.005/0.995, np.random.default_rng(0) per cell), with the replica's
    200-per-cell rows playing the curve role: five instances per rung per
    replicate (the card's MC-5 discipline), 20000 replicates;
  * the coverage calibration structure -- attacks/04_f6_aggregate.py MC-5
    (1000 synthetic designs per decision cell; NULL-P/NULL-G shapes; inner
    interval seeds 10_000+design / 20_000+design). The round's NULL-P needs
    per-class H1 means (mu_TT/mu_TB/mu_SS) the replica rows do not carry, so
    the frozen-convention null here is NULL-B: r* ~ Poisson(4 S^2/N) per
    instance (the L2 pair budget X^2/N with X = 2S, floor attained EXACTLY
    in expectation, T_true = 1) -- an ADAPTATION, recorded in report.md with
    the exact ambiguity. NULL-G (rank) is the round's shape with a per-cell
    kappa_hat (the per-rung analogue of the round's per-cell estimate).

Seeds (all declared here and in receipt.yaml):
  * verbatim decision fits: bootstrap_slope(reps=20000, level=0.95, seed=0)
    -- the archived convention;
  * vectorized cross-check fits: np.default_rng(758510), reps 20000;
  * MC-2: np.default_rng(s) for s in 1..200, reps 2000;
  * MC-5 main masters: random.Random('F7a-replica-cal|<q>|<law>|<beta0:.6f>');
    supp masters: random.Random('F7a-replica-supp|<q>|<law>|<beta0:.6f>');
    inner interval draws: np.default_rng(0), reps 2000, fixed per
    configuration (the round's fixed-seed-0-per-series structure);
  * per-rung T intervals: np.default_rng(0) per cell (09's convention),
    20000 replicates x 5 draws;
  * coverage NULL-B: null draws np.default_rng([758510, m, bits, conv_idx]),
    inner interval np.default_rng(10_000 + design), reps 20000;
    NULL-G: null draws np.default_rng([758510, m, bits, 100]), inner
    np.default_rng(20_000 + design), reps 20000.
"""
import json
import math
import os
import random
import statistics
import sys
import time
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(os.path.dirname(TASK)))
REPL = os.path.join(WT, "coordination/review/pfdr-twfloor-20261001/reviews/"
                        "TASK-20260929-575e80/attacks/out")
ROWS = os.path.join(REPL, "ptm5_results.jsonl")
AGG09B = os.path.join(REPL, "09b_ptm5_agg_by_rung.json")
OUT = os.path.join(TASK, "out")

T0 = time.time()


def stage(msg):
    print(f"[{time.time() - T0:8.1f}s] {msg}", flush=True)


# ---------------------------------------------------------------------------
# The frozen stats.py algorithm, REIMPLEMENTED VERBATIM from the read of
# src/crypto_autoresearcher/index_calculus/stats.py (bootstrap_slope /
# ols_slope). Never imported, never executed from there.
# ---------------------------------------------------------------------------
def ols_slope(xs, ys):
    if len(xs) < 2 or len(set(xs)) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def bootstrap_slope(xs, ys, groups=None, reps=2000, level=0.95, seed=0):
    """{"slope", "lo", "hi", "n"}: OLS slope and its percentile interval."""
    slope = ols_slope(xs, ys)
    out = {"slope": slope, "lo": None, "hi": None, "n": len(xs)}
    if slope is None:
        return out
    strata = defaultdict(list)
    for i, g in enumerate(groups if groups is not None else xs):
        strata[g].append(i)
    rng = random.Random(seed)
    boots = []
    for _ in range(reps):
        idx = [rng.choice(members) for members in strata.values() for _ in members]
        s = ols_slope([xs[i] for i in idx], [ys[i] for i in idx])
        if s is not None:
            boots.append(s)
    if boots:
        boots.sort()
        tail = (1 - level) / 2
        out["lo"] = boots[int(math.floor(tail * (len(boots) - 1)))]
        out["hi"] = boots[int(math.ceil((1 - tail) * (len(boots) - 1)))]
    return out


def residual_sd(xs, ys):
    """(slope, residuals, sd) -- verbatim calibration/f7.py residual_sd()."""
    b = ols_slope(xs, ys)
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    res = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
    return b, res, statistics.pstdev(res) * math.sqrt(len(res) / (len(res) - 2))


# ---------------------------------------------------------------------------
# Vectorized stratified bootstrap -- SAME SEMANTICS as the frozen
# bootstrap_slope (each stratum resampled at its own size with replacement;
# percentile endpoints by the stats.py index arithmetic), numpy PCG64 with
# the declared seeds. No bit-identical prior run exists on these rows. All
# rows of a rung share log2 N (asserted; 00_field_check), so the
# per-replicate slope is the EXACT linear form sum_s (x_s - mx) Y_s / den;
# self-checked against direct OLS below.
# ---------------------------------------------------------------------------
class SlopeDesign:
    def __init__(self, xs, ys, gs):
        self.xs, self.ys, self.gs = list(xs), list(ys), list(gs)
        order = sorted(set(gs))
        self.x_s, self.n_s, self.idx_s = [], [], []
        for g in order:
            idx = [i for i, gg in enumerate(gs) if gg == g]
            xg = {xs[i] for i in idx}
            assert len(xg) == 1, f"rung {g} has mixed log2N"
            self.x_s.append(xs[idx[0]])
            self.n_s.append(len(idx))
            self.idx_s.append(idx)
        n_tot = len(xs)
        mx = sum(n * x for n, x in zip(self.n_s, self.x_s)) / n_tot
        self.c = np.array([x - mx for x in self.x_s])
        self.den = float(sum(n * (x - mx) ** 2 for n, x in zip(self.n_s, self.x_s)))
        self.n = n_tot
        self._selfcheck()

    def _ys_by_stratum(self, ys):
        return [np.array([ys[i] for i in idx]) for idx in self.idx_s]

    def _selfcheck(self):
        """Linear form == direct OLS on the same hand-built replicate."""
        rng = np.random.default_rng(758510)
        ys = self.ys
        gx, gy, Y = [], [], []
        for s, idx in enumerate(self.idx_s):
            draw = rng.integers(0, self.n_s[s], size=self.n_s[s])
            yv = np.array([ys[i] for i in idx])
            Y.append(float(yv[draw].sum()))
            gx.extend(self.x_s[s] for _ in draw)
            gy.extend(float(v) for v in yv[draw])
        direct = ols_slope(gx, gy)
        linear = float(self.c @ np.array(Y)) / self.den
        assert abs(direct - linear) < 1e-12, (direct, linear)
        self.selfcheck = {"direct_ols": direct, "linear_form": linear,
                          "absdiff": abs(direct - linear)}

    def slopes(self, ys, reps, seed):
        rng = np.random.default_rng(seed)
        Y = np.empty((len(self.x_s), reps))
        for s, idx in enumerate(self.idx_s):
            draws = rng.integers(0, self.n_s[s], size=(reps, self.n_s[s]))
            Y[s] = np.array([ys[i] for i in idx])[draws].sum(axis=1)
        return (self.c @ Y) / self.den

    def interval(self, ys, reps, seed, level=0.95):
        sl = np.sort(self.slopes(ys, reps, seed))
        n = len(sl)
        tail = (1 - level) / 2
        return float(sl[int(math.floor(tail * (n - 1)))]), \
            float(sl[int(math.ceil((1 - tail) * (n - 1)))])

    def preslopes(self, draws, ys_by_stratum):
        """Slopes under PRECOMPUTED per-stratum draw matrices (fixed-seed
        structure, as the round's seed-0-per-series inner bootstrap)."""
        Y = np.empty((len(self.x_s), draws[0].shape[0]))
        for s in range(len(self.x_s)):
            Y[s] = ys_by_stratum[s][draws[s]].sum(axis=1)
        return (self.c @ Y) / self.den

    def preinterval(self, draws, ys_by_stratum, level=0.95):
        sl = np.sort(self.preslopes(draws, ys_by_stratum))
        n = len(sl)
        tail = (1 - level) / 2
        return float(sl[int(math.floor(tail * (n - 1)))]), \
            float(sl[int(math.ceil((1 - tail) * (n - 1)))])


# ---------------------------------------------------------------------------
# Series construction (field mapping licensed by 07_ptm5_analysis.py /
# ptm5_engine.py; x = log2 N as the engine's log2N; groups = the rung).
# ---------------------------------------------------------------------------
QUANTITIES = ("ratio_rank", "ratio_frozen", "r_frozen_over_B", "r_rank_over_B",
              "multiplicity")


def build_series(recs, m, quantity):
    xs, ys, gs = [], [], []
    for r in recs:
        if r["m"] != m or r["mode"] != "on" or not 12 <= r["bits"] <= 24:
            continue
        p = r["primary"]
        if p is None:
            continue
        N, B = r["N"], r["B"]
        S, rf, rk = p["S"], p["r_frozen"], p["rank"]
        if quantity == "ratio_rank":
            if not rk:
                continue
            y = math.log2(S / (0.5 * math.sqrt(rk * N)))
        elif quantity == "ratio_frozen":
            if not rf:
                continue
            y = math.log2(S / (0.5 * math.sqrt(rf * N)))
        elif quantity == "r_frozen_over_B":
            y = math.log2(rf / B)
        elif quantity == "r_rank_over_B":
            if not rk:
                continue
            y = math.log2(rk / B)
        elif quantity == "multiplicity":
            if not rk:
                continue
            y = math.log2(rf / rk)
        else:
            raise ValueError(quantity)
        xs.append(math.log2(N))
        ys.append(y)
        gs.append(r["bits"])
    return xs, ys, gs


# ---------------------------------------------------------------------------
# MC-5 calibration (verbatim f7.py calibrate / f7_supp.py, vectorized inner).
# ---------------------------------------------------------------------------
def inner_draws(design, reps, seed):
    rng = np.random.default_rng(seed)
    return [rng.integers(0, design.n_s[s], size=(reps, design.n_s[s]))
            for s in range(len(design.x_s))]


def calibrate(design, ys, q, supp=False):
    b, res, sd = residual_sd(design.xs, ys)
    draws = inner_draws(design, 2000, 0)  # fixed per config: the round's seed-0-per-series
    out = []
    if not supp:
        laws = ("gauss", "t3", "empirical")
        tag = "F7a-replica-cal"
    else:
        laws = ("within_rung_empirical", "rung_sd_gauss")
        tag = "F7a-replica-supp"
        by_rung = {}
        for g, e in zip(design.gs, res):
            by_rung.setdefault(g, []).append(e)
        rung_sd = {g: statistics.pstdev(v) * math.sqrt(len(v) / max(1, len(v) - 1))
                   for g, v in by_rung.items()}
    for law in laws:
        for beta0 in (0.0, b):
            rng = random.Random(f"{tag}|{q}|{law}|{beta0:.6f}")
            cover, zs, false_excl = 0, [], 0
            for _ in range(1000):
                if law == "gauss":
                    eps = [rng.gauss(0, sd) for _ in design.xs]
                elif law == "t3":
                    eps = []
                    for _ in design.xs:
                        z = rng.gauss(0, 1)
                        chi = sum(rng.gauss(0, 1) ** 2 for _ in range(3))
                        eps.append(sd * z / math.sqrt(chi / 3) / math.sqrt(3.0))
                elif law == "empirical":
                    eps = [rng.choice(res) for _ in design.xs]
                elif law == "within_rung_empirical":
                    eps = [rng.choice(by_rung[g]) for g in design.gs]
                else:  # rung_sd_gauss
                    eps = [rng.gauss(0, rung_sd[g]) for g in design.gs]
                yy = [beta0 * x + e for x, e in zip(design.xs, eps)]
                ybs = design._ys_by_stratum(yy)
                bh = ols_slope(design.xs, yy)
                lo, hi = design.preinterval(draws, ybs)
                cover += lo <= beta0 <= hi
                hw = (bh - lo) if beta0 < bh else (hi - bh)
                zs.append(abs(bh - beta0) / hw if hw > 0 else float("inf"))
                if beta0 == 0 and (hi < 0 or lo > 0):
                    false_excl += 1
            zs.sort()
            out.append({"quantity": q, "law": law, "beta0": beta0,
                        "n_series": 1000, "coverage": cover / 1000,
                        "coverage_se": math.sqrt((cover / 1000) * (1 - cover / 1000) / 1000),
                        "kappa_95": zs[int(math.ceil(0.95 * len(zs))) - 1],
                        "false_exclusion_rate_of_0": (false_excl / 1000) if beta0 == 0 else None,
                        "residual_sd": sd})
    return out, b, res, sd


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    recs = [json.loads(l) for l in open(ROWS)]
    stage(f"loaded {len(recs)} replica rows")

    # ---- (a) slopes on the m = 4 on-mode series (primary stop) ------------
    series = {}
    designs = {}
    for q in QUANTITIES:
        xs, ys, gs = build_series(recs, 4, q)
        series[q] = {"xs": xs, "ys": ys, "gs": gs}
        designs[q] = SlopeDesign(xs, ys, gs)
    n_series = len(series["ratio_rank"]["xs"])
    stage(f"series built: n = {n_series} (7 rungs x 200)")

    fits = {}
    for q in QUANTITIES:
        t0 = time.time()
        f = bootstrap_slope(series[q]["xs"], series[q]["ys"], series[q]["gs"],
                            reps=20000, level=0.95, seed=0)
        f["wall_seconds"] = round(time.time() - t0, 1)
        f["impl"] = "verbatim stats.py bootstrap_slope reimplemented (random.Random(0))"
        fits[q] = f
        stage(f"verbatim fit {q}: slope={f['slope']:.6f} [{f['lo']:.6f}, {f['hi']:.6f}] "
              f"({f['wall_seconds']}s)")

    # vectorized cross-check of the same semantics (validates the machinery
    # used for MC-2 / MC-5 below)
    xcheck = {}
    for q in ("ratio_rank", "ratio_frozen"):
        lo, hi = designs[q].interval(series[q]["ys"], 20000, 758510)
        xcheck[q] = {"vec_lo": lo, "vec_hi": hi,
                     "verbatim_lo": fits[q]["lo"], "verbatim_hi": fits[q]["hi"],
                     "absdiff_lo": abs(lo - fits[q]["lo"]),
                     "absdiff_hi": abs(hi - fits[q]["hi"])}
        stage(f"vectorized cross-check {q}: [{lo:.6f}, {hi:.6f}] "
              f"(diff lo {abs(lo - fits[q]['lo']):.2e}, hi {abs(hi - fits[q]['hi']):.2e})")

    # MC-2: 200 seeds x 2000 reps, endpoint means/sds, flip fraction
    mc2 = {}
    for q in ("ratio_rank", "ratio_frozen"):
        d = designs[q]
        ref = fits[q]
        ref_excl = (ref["hi"] < 0) or (ref["lo"] > 0)
        los, his, flips = [], [], 0
        for s in range(1, 201):
            lo, hi = d.interval(series[q]["ys"], 2000, s)
            los.append(lo)
            his.append(hi)
            if ((hi < 0) or (lo > 0)) != ref_excl:
                flips += 1
        mc2[q] = {"seeds": "1..200", "reps": 2000,
                   "lo_mean_sd": [statistics.mean(los), statistics.stdev(los)],
                   "hi_mean_sd": [statistics.mean(his), statistics.stdev(his)],
                   "flip_fraction_of_excludes_0": flips / 200}
        stage(f"MC-2 {q}: hi mean/sd {mc2[q]['hi_mean_sd']}, flips {flips}/200")

    # MC-5 calibration: main + supp laws, kappa_worst, calibrated intervals
    mc5, calib = {}, {}
    for q in ("ratio_rank", "ratio_frozen"):
        cfg_main, b, res, sd = calibrate(designs[q], series[q]["ys"], q, supp=False)
        cfg_supp, _, _, _ = calibrate(designs[q], series[q]["ys"], q, supp=True)
        cfgs = cfg_main + cfg_supp
        kap = max(c["kappa_95"] for c in cfgs)
        d = fits[q]
        lo_c = d["slope"] - kap * (d["slope"] - d["lo"])
        hi_c = d["slope"] + kap * (d["hi"] - d["slope"])
        calib[q] = {"kappa_95_worst": kap, "calibrated_interval": [lo_c, hi_c],
                    "excludes_0": (hi_c < 0) or (lo_c > 0),
                    "n_configs": len(cfgs)}
        mc5[q] = cfgs
        stage(f"MC-5 {q}: kappa_worst={kap:.4f} calibrated [{lo_c:.6f}, {hi_c:.6f}] "
              f"excludes_0={calib[q]['excludes_0']}")

    # levels under r_rank (engine: 2.10-3.63, EV-PFDR-d90ccd OBS-8)
    rr_vals = [2 ** y for y in series["ratio_rank"]["ys"]]
    rf_vals = [2 ** y for y in series["ratio_frozen"]["ys"]]
    levels = {"ratio_rank_min_max": [min(rr_vals), max(rr_vals)],
              "ratio_frozen_min_max": [min(rf_vals), max(rf_vals)],
              "engine_level_range_r_rank_OBS8": [2.10, 3.63]}

    # engine F7 values restated from EV-PFDR-d90ccd OBS-8 (+ f7.stdout precise)
    engine = {
        "restated_from": "ledger/evidence/EV-PFDR-d90ccd.yaml OBS-8; precise values "
                         "from coordination/review/pfdr-twfloor-20261001/reviews/"
                         "TASK-20260929-fd1a9f/calibration/out/f7.stdout",
        "ratio_rank": {"slope": -0.01491, "slope_precise": -0.014906729994066411,
                       "calibrated_interval": [-0.0242, -0.0053],
                       "kappa_worst_34cfg": 1.349,
                       "nominal_95_20000": [-0.02182, -0.00781]},
        "ratio_frozen": {"slope": -0.03384, "slope_precise": -0.03383844969209488,
                         "nominal_95_20000": [-0.04169, -0.02558],
                         "calibrated_own_worst_kappa_OBS8": [-0.0434, -0.0238]},
        "level_range_r_rank": [2.10, 3.63],
        "components": {"r_frozen_over_F": 0.04082209815404258,
                       "r_rank_over_F": 0.0029586587579856403},
        "card_sign_note": "the card's COMPUTE (c) lists 'r_rank/|F| -0.002959'; the "
                          "archive (f7.stdout r_rank_over_F slope +0.0029586587579856403; "
                          "EV-PFDR-d90ccd F7 '+0.0030') records POSITIVE +0.002959, and "
                          "the identity arithmetic requires +. The archive is followed; "
                          "the discrepancy is recorded, not silently resolved.",
    }

    # decision rule evaluation (DEC-20261002-bed082 pre_registered_decision_rule)
    eng_lo, eng_hi = -0.0242, -0.0053
    eng_pt = -0.01491
    branch = {}
    for tag, iv in (("calibrated", calib["ratio_rank"]["calibrated_interval"]),
                    ("nominal_95_20000", [fits["ratio_rank"]["lo"], fits["ratio_rank"]["hi"]])):
        rlo, rhi = iv
        cond = {
            "(i)A_inside": (rlo >= eng_lo) and (rhi <= eng_hi),
            "(i)B_overlap_engine_point_inside": (rlo <= eng_hi and rhi >= eng_lo
                                                 and rlo <= eng_pt <= rhi),
            "(ii)_contains_0": (rlo <= 0.0 <= rhi),
            "(iii)_entirely_below_engine_calibrated": (rhi < eng_lo),
        }
        fired = [k for k, v in cond.items() if v]
        branch[tag] = {"interval": [rlo, rhi], "conditions": cond, "fired": fired}
    stage(f"decision-rule branches: calibrated fired={branch['calibrated']['fired']}, "
          f"nominal fired={branch['nominal_95_20000']['fired']}")

    slopes_out = {
        "task": "TASK-20261002-758e51",
        "rows": {"source": ROWS, "selection": "m = 4, mode = on, bits 12..24, "
                 "primary stop present, r > 0 (none excluded)", "n": n_series,
                 "rungs": {str(b): 200 for b in range(12, 25, 2)}},
        "field_mapping": {
            "S_3": "stop['S'] (= table_s3 + search_s3, table included)",
            "r_frozen": "stop['r_frozen'] (= relations + sum(rows_fed), on mode)",
            "r_rank": "stop['rank'] (the solver rank)",
            "N": "row['N']", "B": "row['B']", "stop": "row['primary']",
            "x": "log2(N)", "groups": "the rung (bits)",
            "licensed_by": "attacks/07_ptm5_analysis.py ratios() and aggregate_T "
                           "block; attacks/ptm5_engine.py snapshot() and "
                           "run_instance() docstring; attacks/09b_ptm5_agg_by_rung.py"},
        "conventions": {
            "slope_fit": "frozen stats.py bootstrap_slope (stratified by rung, "
                         "one draw per member with replacement, percentile "
                         "endpoints by the stats.py index arithmetic), "
                         "reps=20000, level=0.95, seed=0 -- reimplemented "
                         "verbatim from the read of stats.py; never imported",
            "interval_calibration": "calibration/f7.py calibrate + f7_supp.py "
                                    "(gauss/t3/empirical + within_rung_empirical/"
                                    "rung_sd_gauss; beta0 in {0, slope}; 1000 "
                                    "series; inner reps 2000 seed 0)",
            "engine_values": "restated from EV-PFDR-d90ccd OBS-8",
        },
        "engine_F7_restated": engine,
        "replica_fits_20000_seed0": fits,
        "vectorized_crosscheck_20000": xcheck,
        "linear_form_selfcheck": designs["ratio_rank"].selfcheck,
        "MC2_200seeds": mc2,
        "MC5_calibration": mc5,
        "calibrated": calib,
        "levels": levels,
        "decision_rule_evaluation": {
            "rule": "DEC-20261002-bed082 pre_registered_decision_rule",
            "engine_calibrated_interval": [eng_lo, eng_hi],
            "engine_point": eng_pt,
            "interval_used_for_reading": "calibrated (the round's discipline: the F6 "
                                        "and F7 decisions use calibrated intervals, "
                                        "EV-PFDR-d90ccd unresolved_confounds)",
            "calibrated": branch["calibrated"],
            "nominal_95_20000": branch["nominal_95_20000"],
        },
    }
    json.dump(slopes_out, open(os.path.join(OUT, "slopes.json"), "w"),
              indent=1, sort_keys=True)
    stage("slopes.json written")

    # ---- (b) per-rung aggregate T, m = 4 and m = 5, both conventions ------
    agg09b = json.load(open(AGG09B))
    cells, flags = {}, []
    for m in (4, 5):
        for bits in range(12, 25, 2):
            rows = [r for r in recs if r["m"] == m and r["bits"] == bits
                    and r["mode"] == "on" and r["primary"]]
            # point T: the exact 09b expression (reconciliation is exact)
            num = sum(r["primary"]["S"] ** 2 / (r["N"] * r["B"]) for r in rows)
            a = np.array([r["primary"]["S"] ** 2 / (r["N"] * r["B"]) for r in rows])
            Nv = np.array([float(r["N"]) for r in rows])
            Bv = np.array([float(r["B"]) for r in rows])
            Sv = np.array([float(r["primary"]["S"]) for r in rows])
            lam = 4.0 * Sv ** 2 / Nv  # the X^2/N pair budget, X = 2S
            cell = {"n": len(rows)}
            for ci, (conv, key) in enumerate((("frozen", "r_frozen"), ("rank", "rank"))):
                den = sum(r["primary"][key] * r["N"] / 4 / (r["N"] * r["B"]) for r in rows)
                T = num / den
                b = np.array([r["primary"][key] * r["N"] / 4 / (r["N"] * r["B"])
                              for r in rows])
                # 99% curve bootstrap: five instances per rung per replicate,
                # 20000 replicates, np.default_rng(0) per cell (09's convention)
                rng = np.random.default_rng(0)
                idx = rng.integers(0, len(rows), size=(20000, 5))
                Tb = a[idx].sum(axis=1) / b[idx].sum(axis=1)
                lo99, hi99 = (float(v) for v in np.quantile(Tb, [0.005, 0.995]))
                excl_below = bool(hi99 < 1.0)
                if excl_below:
                    flags.append(f"m{m}|b{bits}|{conv}")
                # coverage, NULL-B (budget Poisson; adaptation, see report):
                # r* ~ Poisson(4 S^2/N), S fixed, T_true = 1
                master = np.random.default_rng([758510, m, bits, ci])
                hit = 0
                false_flag = 0
                for d in range(1000):
                    rstar = master.poisson(lam)
                    bs = rstar / (4.0 * Bv)
                    ii = np.random.default_rng(10_000 + d).integers(
                        0, len(rows), size=(20000, 5))
                    Td = a[ii].sum(axis=1) / bs[ii].sum(axis=1)
                    clo, chi = (float(v) for v in np.quantile(Td, [0.005, 0.995]))
                    hit += clo <= 1.0 <= chi
                    false_flag += chi < 1.0
                cov = {"null": "NULL-B: r* ~ Poisson(4 S^2/N) per instance, S fixed; "
                               "T_true = 1 (the L2 pair budget attained exactly in "
                               "expectation); ADAPTATION of the round's NULL-P "
                               "(per-class H1 means not recoverable from the "
                               "replica rows)",
                       "designs": 1000, "inner_reps": 20000,
                       "inner_seed_scheme": "10_000 + design",
                       "coverage_of_true_T": hit / 1000,
                       "false_flag_rate_hi_below_1": false_flag / 1000}
                cell[conv] = {
                    "T": T, "ref_09b": agg09b[f"m{m}|b{bits}"][conv],
                    "absdiff_vs_09b": abs(T - agg09b[f"m{m}|b{bits}"][conv]),
                    "ci99_5per_rung": [lo99, hi99], "replicates": 20000,
                    "draws_per_replicate": 5, "seed": 0,
                    "quantile_method": "np.quantile 0.005/0.995 (09_agg_by_rung.py)",
                    "excludes_1_from_below": excl_below,
                    "coverage_NULL_B": cov,
                }
                stage(f"m{m} b{bits} {conv}: T={T:.4f} ci99=[{lo99:.4f}, {hi99:.4f}] "
                      f"excl_below={excl_below} cov={hit / 1000:.3f} "
                      f"falseflag={false_flag / 1000:.3f}")
            # NULL-G coverage (rank only; the round's shape, per-cell kappa_hat)
            rk = np.array([float(r["primary"]["rank"]) for r in rows])
            q1 = rk + 1.0
            kh = float(q1.sum() / lam.sum())
            # T_true_g over the cell's rows (fixed): sum(w (rank+1)/kh N/4)/sum(w rank N/4)
            num_g = ((q1 / kh) / (4.0 * Bv)).sum()
            den_g = (rk / (4.0 * Bv)).sum()
            T_true_g = float(num_g / den_g)
            master = np.random.default_rng([758510, m, bits, 100])
            hitg = 0
            for d in range(1000):
                u = master.gamma(q1, 1.0 / kh)
                aS = u / (4.0 * Bv)  # S*^2/(N B) = (u N/4)/(N B)
                ii = np.random.default_rng(20_000 + d).integers(
                    0, len(rows), size=(20000, 5))
                Td = aS[ii].sum(axis=1) / (rk / (4.0 * Bv))[ii].sum(axis=1)
                clo, chi = (float(v) for v in np.quantile(Td, [0.005, 0.995]))
                hitg += clo <= T_true_g <= chi
            cell["rank"]["coverage_NULL_G"] = {
                "null": "NULL-G: u* ~ Gamma(rank+1, 1/kappa_hat), S*^2 = u* N/4, "
                        "r = rank fixed (04_f6_aggregate.py's shape); kappa_hat "
                        "estimated per cell = sum(rank+1)/sum(4 S^2/N) over the "
                        "cell's rows (the per-rung analogue of the round's "
                        "per-cell estimate)",
                "kappa_hat": kh, "T_true_g": T_true_g, "designs": 1000,
                "inner_reps": 20000, "inner_seed_scheme": "20_000 + design",
                "coverage_of_true_T": hitg / 1000}
            stage(f"m{m} b{bits} NULL-G: kh={kh:.4f} T_true_g={T_true_g:.4f} "
                  f"cov={hitg / 1000:.3f}")
            cells[f"m{m}|b{bits}"] = cell

    per_rung_out = {
        "task": "TASK-20261002-758e51",
        "reading_rules": "AMD-20261002-2bc8cf C-1..C-4 (weights w = 1/(N B); both r "
                         "conventions; premise state recorded; no per-instance "
                         "predicate adopted)",
        "premise_audit": {
            "state": "the replica is exactly generic BY CONSTRUCTION (base logs "
                     "uniform distinct nonzero +-classes; x-key equality = "
                     "+-equality; the floor's premise holds EXACTLY)",
            "source": "attacks/ptm5_engine.py module docstring; EV-PFDR-d90ccd "
                      "OBS-6 (PTM-5); DEC-20261002-bed082 context",
            "per_arm_audit": "not applicable: no arms; every row is the exactly "
                             "generic replica (the card's premise-audit instruction)"},
        "weights": "w_i = 1/(N_i B_i) per instance (deterministic)",
        "conventions_reported": {
            "frozen": "r_frozen = relations + sum(rows_fed) before the stop (the "
                       "lemma's step-(ii) pair count; compound, overdispersed)",
            "rank": "r_rank = the solver rank (the lemma's step-(iii) "
                    "independent-relation count)"},
        "per_instance_predicate_adopted": False,
        "interval_discipline": "99% curve bootstrap at the engine's five-per-rung "
                               "design: five instances per rung per replicate "
                               "(the replica's 200-per-cell rows playing the "
                               "curve role), 20000 replicates, np.default_rng(0) "
                               "per cell, np.quantile 0.005/0.995 "
                               "(09_agg_by_rung.py's convention); coverage "
                               "calibrated per the round's MC-5 structure "
                               "(04_f6_aggregate.py): 1000 synthetic designs per "
                               "cell, inner seeds 10_000+design (NULL-B) / "
                               "20_000+design (NULL-G)",
        "cells": cells,
        "flags_excluding_1_from_below": flags,
        "flag_rule": "any rung whose 99% interval excludes 1 from below is "
                     "TW-BREAK-shaped and routes to the Coordinator untouched, "
                     "never self-interpreted by the executor "
                     "(DEC-20261002-bed082 pre_registered_decision_rule)",
    }
    json.dump(per_rung_out, open(os.path.join(OUT, "per_rung_T.json"), "w"),
              indent=1, sort_keys=True)
    stage("per_rung_T.json written")

    # ---- (c) the identity's decomposition ---------------------------------
    s_rr = fits["ratio_rank"]["slope"]
    s_rf = fits["ratio_frozen"]["slope"]
    s_rfb = fits["r_frozen_over_B"]["slope"]
    s_rkb = fits["r_rank_over_B"]["slope"]
    s_mult = fits["multiplicity"]["slope"]
    lhs = s_rr
    rhs = s_rf + 0.5 * (s_rfb - s_rkb)
    rhs_alt = s_rf + 0.5 * s_mult
    residual = lhs - rhs
    tol = 1e-9
    eng_rf, eng_rk = engine["components"]["r_frozen_over_F"], engine["components"]["r_rank_over_F"]
    eng_identity = -0.03383844969209488 + 0.5 * (eng_rf - eng_rk)
    ident_out = {
        "task": "TASK-20261002-758e51",
        "rows": "same as slopes.json (m = 4 on-mode, 12..24 bits, primary stop)",
        "identity": "slope(log2 ratio_rank) = slope(log2 ratio_frozen) + "
                    "0.5 * (slope(log2 r_frozen/B) - slope(log2 r_rank/B))",
        "why_exact": "per instance log2 ratio_rank - log2 ratio_frozen = "
                     "0.5 log2(r_frozen/r_rank); OLS is linear in y; the "
                     "log2 B terms cancel in the difference of the r/B "
                     "component slopes (EV-PFDR-d90ccd cross_joint_reading)",
        "components": {
            "slope_log2_ratio_rank": {"value": s_rr, "nominal_95_20000":
                                      [fits["ratio_rank"]["lo"], fits["ratio_rank"]["hi"]]},
            "slope_log2_ratio_frozen": {"value": s_rf, "nominal_95_20000":
                                        [fits["ratio_frozen"]["lo"], fits["ratio_frozen"]["hi"]]},
            "slope_log2_r_frozen_over_B": {"value": s_rfb, "nominal_95_20000":
                                            [fits["r_frozen_over_B"]["lo"], fits["r_frozen_over_B"]["hi"]]},
            "slope_log2_r_rank_over_B": {"value": s_rkb, "nominal_95_20000":
                                          [fits["r_rank_over_B"]["lo"], fits["r_rank_over_B"]["hi"]]},
            "slope_log2_multiplicity_r_frozen_over_r_rank": {
                "value": s_mult, "nominal_95_20000":
                [fits["multiplicity"]["lo"], fits["multiplicity"]["hi"]]},
        },
        "identity_residual": residual,
        "residual_alt_form": lhs - rhs_alt,
        "component_difference_check": s_rfb - s_rkb - s_mult,
        "tolerance": tol,
        "identity_holds": bool(abs(residual) <= tol),
        "engine_comparison": {
            "engine_components": {"r_frozen_over_F": eng_rf, "r_rank_over_F": eng_rk},
            "engine_identity_check": {"lhs_engine_F7_slope": -0.014906729994066411,
                                      "rhs_engine": eng_identity,
                                      "residual": -0.014906729994066411 - eng_identity,
                                      "source": "EV-PFDR-d90ccd cross_joint_reading; "
                                                "f7.stdout"},
            "replica_minus_engine": {
                "r_frozen_over_B": s_rfb - eng_rf,
                "r_rank_over_B": s_rkb - eng_rk,
                "multiplicity_0_5x_contribution": 0.5 * (s_rfb - s_rkb) - 0.5 * (eng_rf - eng_rk)},
            "card_sign_discrepancy": engine["card_sign_note"],
        },
    }
    json.dump(ident_out, open(os.path.join(OUT, "identity_decomposition.json"), "w"),
              indent=1, sort_keys=True)
    stage(f"identity_decomposition.json written: residual={residual:.3e} "
          f"(tolerance {tol:.0e})")

    stage("DONE")
    print(json.dumps({
        "replica_ratio_rank": {"slope": s_rr, "nominal": [fits["ratio_rank"]["lo"], fits["ratio_rank"]["hi"]],
                               "calibrated": calib["ratio_rank"]["calibrated_interval"]},
        "replica_ratio_frozen": {"slope": s_rf, "nominal": [fits["ratio_frozen"]["lo"], fits["ratio_frozen"]["hi"]],
                                 "calibrated": calib["ratio_frozen"]["calibrated_interval"]},
        "branch_calibrated": branch["calibrated"]["fired"],
        "branch_nominal": branch["nominal_95_20000"]["fired"],
        "identity_residual": residual,
        "flags": flags,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
