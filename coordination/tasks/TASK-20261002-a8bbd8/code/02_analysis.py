"""02 -- THE ANALYSIS of TASK-20261002-a8bbd8 (the single analysis attempt).

ZERO solver/engine execution: nothing under src/crypto_autoresearcher is
imported or executed (attested in receipt.yaml). The rows analyzed are (a) the
archived 12..24 segment, READ from the round's ptm5_results.jsonl (never
regenerated), and (b) this task's new 26..28 rows from out/replica_rows.jsonl.

TRUNCATION DISCLOSURE (recorded in every output): the pre-registered primary
discriminator of DEC-20261002-0df88e is the 26..32 SEGMENT SLOPE of log2
T_frozen vs log2 N at m = 4 on-mode. Rungs 30 and 32 were STOPPED by the
pre-registered machine-protection RSS stop (2.5e9 bytes per process; peaks
2737.1 MB (m4) and 2737.6 MB (m5) within 0.6 s of rung 30; the archived
construction's encoding store needs ~2.3-4.0 KB per recorded encoding and
grows ~B^2, so rungs 30 (m4 B=151, m5 B=67) and 32 cannot fit under the stop
as constructed). A stop is blocked, never a finding; n was not changed; no
rung was relaunched. The segment actually fit is therefore 26..28 (2 rungs,
n = 400), and the pre-registered outcome branches are evaluated on the
TRUNCATED 26..28 calibrated interval; whether a 2-rung segment supports any
branch reading is the Coordinator's call, not this executor's.

Conventions, verbatim from the archive (never invented):
  * ratios and the aggregate T field mapping -- attacks/07_ptm5_analysis.py
    (ratios(): frozen S/(0.5 sqrt(r_frozen N)), rank S/(0.5 sqrt(rank N));
    aggregate_T: num = sum S^2/(N B), den = sum r N/4/(N B)) and
    attacks/ptm5_engine.py snapshot() (S = table_s3 + search_s3; r_frozen =
    relations + sum(rows_fed) on mode; rank = the solver rank; PRIMARY stop =
    first row determining k);
  * the r, r_frozen, r_rank symbol map -- attacks/f3-lemma-map.yaml;
  * the reading rules -- AMD-20261002-2bc8cf C-1..C-4 (weights w = 1/(N B),
    both r conventions, premise state recorded, no per-instance predicate);
  * the slope fit and its interval -- the frozen stats.py bootstrap_slope
    (stratified-by-rung resampling with replacement, one draw per member,
    percentile endpoints by the stats.py index arithmetic), reimplemented
    verbatim (NEVER imported), reps=20000, level=0.95, seed=0, exactly as
    TASK-20261002-758e51/code/01_analysis.py ran it;
  * the interval calibration -- calibration/f7.py calibrate() + f7_supp.py
    (laws gauss, t3, empirical; beta0 in {0, slope}; 1000 series; inner
    interval reps 2000 seed 0; kappa_95 = zs[ceil(0.95 n)-1]); calibrated
    interval = [slope - kap (slope - lo), slope + kap (hi - slope)];
  * the per-rung T interval -- the round's curve bootstrap at the engine's
    five-per-rung design (attacks/09_agg_by_rung.py: np.quantile at
    0.005/0.995, np.random.default_rng(0) per cell), five instances per rung
    per replicate, 20000 replicates;
  * the coverage calibration structure -- attacks/04_f6_aggregate.py MC-5
    (1000 synthetic designs per decision cell; NULL-B budget-Poisson null --
    the F7(a) adaptation, labelled there and here; NULL-G the round's shape
    with a per-cell kappa_hat), inner interval seeds 10_000+design /
    20_000+design.

NAMING NOTE (recorded, not silently resolved): the card and DEC-20261002-0df88e
call the discriminator "log2 T_frozen"; the archived 12..24 value they read it
against (-0.038062, calibrated [-0.041782, -0.034385]) is, to every digit,
TASK-20261002-758e51's per-instance log2 ratio_frozen fit (ratio = S/(0.5
sqrt(r_frozen N)), the per-instance form of the floor bound; slopes.json
replica_fits_20000_seed0.ratio_frozen). The 26..28 segment slope is therefore
computed with exactly that fit; no other reading of "log2 T_frozen" reproduces
the archived reference values. "Weighted OLS" is likewise the F7(a) per-instance
OLS (at the balanced 200-per-rung design it weights rungs equally); no other
weighting is recoverable from the archive.

Seeds (all declared here and in receipt.yaml):
  * verbatim decision fits: bootstrap_slope(reps=20000, level=0.95, seed=0)
    -- the archived convention;
  * vectorized cross-check fits: np.default_rng(11058136) (= 0xA8BBD8, the
    task token), reps 20000; SlopeDesign self-check the same seed;
  * MC-2: np.default_rng(s) for s in 1..200, reps 2000;
  * MC-5 NEW-fit masters: random.Random('F7b-replica-cal|<q>|<law>|<beta0:.6f>')
    and random.Random('F7b-replica-supp|<q>|<law>|<beta0:.6f>'); inner interval
    draws np.default_rng(0), reps 2000, fixed per configuration;
  * MC-5 REPRODUCTION masters (the 12..24 machinery cross-check only):
    F7(a)'s exact strings 'F7a-replica-cal|...' / 'F7a-replica-supp|...' and
    self-check seed 758510, to reproduce F7(a)'s archived numbers exactly;
  * per-rung T intervals: np.default_rng(0) per cell (09's convention),
    20000 replicates x 5 draws;
  * coverage NULL-B: null draws np.default_rng([11058136, m, bits, conv_idx]),
    inner interval np.default_rng(10_000 + design), reps 20000; NULL-G: null
    draws np.default_rng([11058136, m, bits, 100]), inner
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
ROWS_ARCH = os.path.join(REPL, "ptm5_results.jsonl")
ROWS_NEW = os.path.join(TASK, "out", "replica_rows.jsonl")
F7A_SLOPES = os.path.join(WT, "coordination/tasks/TASK-20261002-758e51/out/slopes.json")
F7A_PER_RUNG = os.path.join(WT, "coordination/tasks/TASK-20261002-758e51/out/per_rung_T.json")
OUT = os.path.join(TASK, "out")

ARCH_RUNGS = tuple(range(12, 25, 2))
NEW_RUNGS = (26, 28)          # rungs 30, 32: STOPPED by the RSS guard (recorded)
STOPPED_RUNGS = (30, 32)
T0 = time.time()

TRUNCATION = {
    "pre_registered_discriminator": "the 26..32 segment slope of log2 T_frozen "
                                    "vs log2 N at m = 4 on-mode "
                                    "(DEC-20261002-0df88e power rule)",
    "actual_segment": "26..28 (2 rungs, n = 400)",
    "why_truncated": "rungs 30 and 32 were stopped by the pre-registered "
                     "machine-protection RSS stop (2.5e9 bytes per process): "
                     "peak 2737.1 MB (m4 b30) and 2737.6 MB (m5 b30) within "
                     "0.6 s; the archived construction's encoding store "
                     "(~2.3-4.0 KB per recorded encoding, ~B^2 encodings per "
                     "instance) cannot fit under the stop at B = 151 (m4) / "
                     "67 (m5) and above as constructed",
    "stop_semantics": "a stop is blocked, never a finding; n unchanged; no "
                      "rung relaunched; rung 32 never attempted (ascending "
                      "order, the stop at 30 ends the phase)",
    "reading_status": "the outcome branches below are evaluated on the "
                      "TRUNCATED 26..28 calibrated interval; whether a "
                      "2-rung segment supports a branch reading is the "
                      "Coordinator's call (NA-2), not this executor's",
}


def stage(msg):
    print(f"[{time.time() - T0:8.1f}s] {msg}", flush=True)


# ---------------------------------------------------------------------------
# The frozen stats.py algorithm, REIMPLEMENTED VERBATIM (as F7(a) did; never
# imported from src/).
# ---------------------------------------------------------------------------
def ols_slope(xs, ys):
    if len(xs) < 2 or len(set(xs)) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def bootstrap_slope(xs, ys, groups=None, reps=2000, level=0.95, seed=0):
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
    b = ols_slope(xs, ys)
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    res = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
    return b, res, statistics.pstdev(res) * math.sqrt(len(res) / (len(res) - 2))


# ---------------------------------------------------------------------------
# Vectorized stratified bootstrap -- SAME SEMANTICS as the frozen
# bootstrap_slope (F7(a)'s SlopeDesign, verbatim).
# ---------------------------------------------------------------------------
class SlopeDesign:
    def __init__(self, xs, ys, gs, selfcheck_seed=11058136):
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
        self._selfcheck(selfcheck_seed)

    def _selfcheck(self, seed):
        rng = np.random.default_rng(seed)
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

    def _ys_by_stratum(self, ys):
        return [np.array([ys[i] for i in idx]) for idx in self.idx_s]

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
# Series construction (F7(a)'s build_series, bits range parameterized).
# ---------------------------------------------------------------------------
QUANTITIES = ("ratio_rank", "ratio_frozen", "r_frozen_over_B", "r_rank_over_B",
              "multiplicity")


def build_series(recs, m, quantity, lo, hi):
    xs, ys, gs = [], [], []
    for r in recs:
        if r["m"] != m or r["mode"] != "on" or not lo <= r["bits"] <= hi:
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
# MC-5 calibration (F7(a)'s calibrate, master tag parameterized).
# ---------------------------------------------------------------------------
def inner_draws(design, reps, seed):
    rng = np.random.default_rng(seed)
    return [rng.integers(0, design.n_s[s], size=(reps, design.n_s[s]))
            for s in range(len(design.x_s))]


def calibrate(design, ys, q, supp=False, tag_prefix="F7b-replica"):
    b, res, sd = residual_sd(design.xs, ys)
    draws = inner_draws(design, 2000, 0)
    out = []
    if not supp:
        laws = ("gauss", "t3", "empirical")
        tag = f"{tag_prefix}-cal"
    else:
        laws = ("within_rung_empirical", "rung_sd_gauss")
        tag = f"{tag_prefix}-supp"
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
    arch = [json.loads(l) for l in open(ROWS_ARCH)]
    new = [json.loads(l) for l in open(ROWS_NEW)]
    stage(f"loaded {len(arch)} archived rows (12..24, READ) + {len(new)} new rows (26..28)")

    f7a_slopes = json.load(open(F7A_SLOPES))
    f7a_per_rung = json.load(open(F7A_PER_RUNG))

    # ---- field check (F7(a)'s 00_field_check, folded here) ----------------
    fc = {"rows": {"archived": len(arch), "new": len(new)},
          "cells": {}, "all_ok": True}
    for src, recs in (("archived", arch), ("new", new)):
        for m in (4, 5):
            for bits in (ARCH_RUNGS if src == "archived" else NEW_RUNGS):
                rows = [r for r in recs if r["m"] == m and r["bits"] == bits
                        and r["mode"] == "on"]
                ok = len(rows) == 200 and all(
                    r["primary"] is not None and r["primary"]["rank"] >= 1
                    and r["primary"]["r_frozen"] >= 1 for r in rows)
                nb = {(r["N"], r["B"]) for r in rows}
                fc["cells"][f"{src}|m{m}|b{bits}"] = {
                    "n": len(rows), "primary_present_with_r_ge_1": ok,
                    "N_B_pairs": sorted(nb)}
                fc["all_ok"] &= ok and len(nb) == 1
    json.dump(fc, open(os.path.join(OUT, "field_check.json"), "w"),
              indent=1, sort_keys=True)
    stage(f"field check: all_ok={fc['all_ok']}")
    if not fc["all_ok"]:
        stage("FIELD CHECK FAILED -- aborting (analysis defect, not a finding)")
        return 1

    # ---- (a) per-rung aggregate T, combined 12..28, both conventions -----
    cells, flags = {}, []
    for m in (4, 5):
        for bits in list(ARCH_RUNGS) + list(NEW_RUNGS):
            src = "archived" if bits in ARCH_RUNGS else "new"
            recs = arch if src == "archived" else new
            rows = [r for r in recs if r["m"] == m and r["bits"] == bits
                    and r["mode"] == "on" and r["primary"]]
            num = sum(r["primary"]["S"] ** 2 / (r["N"] * r["B"]) for r in rows)
            a = np.array([r["primary"]["S"] ** 2 / (r["N"] * r["B"]) for r in rows])
            Nv = np.array([float(r["N"]) for r in rows])
            Bv = np.array([float(r["B"]) for r in rows])
            Sv = np.array([float(r["primary"]["S"]) for r in rows])
            lam = 4.0 * Sv ** 2 / Nv
            cell = {"n": len(rows), "row_source": src}
            for ci, (conv, key) in enumerate((("frozen", "r_frozen"), ("rank", "rank"))):
                den = sum(r["primary"][key] * r["N"] / 4 / (r["N"] * r["B"]) for r in rows)
                T = num / den
                b = np.array([r["primary"][key] * r["N"] / 4 / (r["N"] * r["B"])
                              for r in rows])
                rng = np.random.default_rng(0)
                idx = rng.integers(0, len(rows), size=(20000, 5))
                Tb = a[idx].sum(axis=1) / b[idx].sum(axis=1)
                lo99, hi99 = (float(v) for v in np.quantile(Tb, [0.005, 0.995]))
                excl_below = bool(hi99 < 1.0)
                if excl_below:
                    flags.append(f"m{m}|b{bits}|{conv}")
                entry = {
                    "T": T, "ci99_5per_rung": [lo99, hi99], "replicates": 20000,
                    "draws_per_replicate": 5, "seed": 0,
                    "quantile_method": "np.quantile 0.005/0.995 (09_agg_by_rung.py)",
                    "excludes_1_from_below": excl_below,
                }
                if src == "archived":
                    ref = f7a_per_rung["cells"][f"m{m}|b{bits}"][conv]
                    entry["ref_F7a_T"] = ref["T"]
                    entry["absdiff_T_vs_F7a"] = abs(T - ref["T"])
                    entry["ref_F7a_ci99"] = ref["ci99_5per_rung"]
                    entry["absdiff_ci99_vs_F7a"] = [
                        abs(lo99 - ref["ci99_5per_rung"][0]),
                        abs(hi99 - ref["ci99_5per_rung"][1])]
                    entry["coverage"] = {
                        "source": "restated from TASK-20261002-758e51 "
                                  "out/per_rung_T.json (READ, not recomputed)",
                        "NULL_B": ref["coverage_NULL_B"],
                        **({"NULL_G": ref["coverage_NULL_G"]}
                           if "coverage_NULL_G" in ref else {})}
                else:
                    master = np.random.default_rng([11058136, m, bits, ci])
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
                    entry["coverage"] = {
                        "null": "NULL-B: r* ~ Poisson(4 S^2/N) per instance, S "
                                "fixed; T_true = 1 (the L2 pair budget attained "
                                "exactly in expectation); ADAPTATION of the "
                                "round's NULL-P (per-class H1 means not "
                                "recoverable from the replica rows), as in "
                                "F7(a)",
                        "master_seed": [11058136, m, bits, ci],
                        "designs": 1000, "inner_reps": 20000,
                        "inner_seed_scheme": "10_000 + design",
                        "coverage_of_true_T": hit / 1000,
                        "false_flag_rate_hi_below_1": false_flag / 1000}
                cell[conv] = entry
                stage(f"m{m} b{bits} {conv} [{src}]: T={T:.4f} "
                      f"ci99=[{lo99:.4f}, {hi99:.4f}] excl_below={excl_below}")
            if src == "new":
                rk = np.array([float(r["primary"]["rank"]) for r in rows])
                q1 = rk + 1.0
                kh = float(q1.sum() / lam.sum())
                num_g = ((q1 / kh) / (4.0 * Bv)).sum()
                den_g = (rk / (4.0 * Bv)).sum()
                T_true_g = float(num_g / den_g)
                master = np.random.default_rng([11058136, m, bits, 100])
                hitg = 0
                for d in range(1000):
                    u = master.gamma(q1, 1.0 / kh)
                    aS = u / (4.0 * Bv)
                    ii = np.random.default_rng(20_000 + d).integers(
                        0, len(rows), size=(20000, 5))
                    Td = aS[ii].sum(axis=1) / (rk / (4.0 * Bv))[ii].sum(axis=1)
                    clo, chi = (float(v) for v in np.quantile(Td, [0.005, 0.995]))
                    hitg += clo <= T_true_g <= chi
                cell["rank"]["coverage_NULL_G"] = {
                    "null": "NULL-G: u* ~ Gamma(rank+1, 1/kappa_hat), S*^2 = "
                            "u* N/4, r = rank fixed (04_f6_aggregate.py's "
                            "shape); kappa_hat estimated per cell "
                            "= sum(rank+1)/sum(4 S^2/N)",
                    "master_seed": [11058136, m, bits, 100],
                    "kappa_hat": kh, "T_true_g": T_true_g, "designs": 1000,
                    "inner_reps": 20000, "inner_seed_scheme": "20_000 + design",
                    "coverage_of_true_T": hitg / 1000}
                stage(f"m{m} b{bits} NULL-G: kh={kh:.4f} T_true_g={T_true_g:.4f} "
                      f"cov={hitg / 1000:.3f}")
            cells[f"m{m}|b{bits}"] = cell

    per_rung_out = {
        "task": "TASK-20261002-a8bbd8",
        "truncation": TRUNCATION,
        "reading_rules": "AMD-20261002-2bc8cf C-1..C-4 (weights w = 1/(N B); "
                         "both r conventions; premise state recorded; no "
                         "per-instance predicate adopted)",
        "premise_audit": {
            "state": "the replica is exactly generic BY CONSTRUCTION (base "
                     "logs uniform distinct nonzero +-classes; x-key equality "
                     "= +-equality; the floor's premise holds EXACTLY)",
            "source": "attacks/ptm5_engine.py module docstring; the "
                      "construction-fidelity check out/fidelity_check.json "
                      "(exact reproduction of archived rows on m4 b12, m5 "
                      "b12, m4 b24 probes)",
            "per_arm_audit": "not applicable: no arms; every row is the "
                             "exactly generic replica",
        },
        "weights": "w_i = 1/(N_i B_i) per instance (deterministic)",
        "conventions_reported": {
            "frozen": "r_frozen = relations + sum(rows_fed) before the stop "
                      "(the lemma's step-(ii) pair count; compound, "
                      "overdispersed)",
            "rank": "r_rank = the solver rank (the lemma's step-(iii) "
                    "independent-relation count)"},
        "per_instance_predicate_adopted": False,
        "interval_discipline": "99% curve bootstrap at the engine's "
                               "five-per-rung design: five instances per rung "
                               "per replicate, 20000 replicates, "
                               "np.default_rng(0) per cell, np.quantile "
                               "0.005/0.995 (09_agg_by_rung.py); coverage "
                               "per the round's MC-5 structure "
                               "(04_f6_aggregate.py): 1000 synthetic designs "
                               "per cell, inner seeds 10_000+design (NULL-B) "
                               "/ 20_000+design (NULL-G); archived rungs' "
                               "coverage RESTATED from F7(a) (read, not "
                               "recomputed), their T and ci99 recomputed only "
                               "as an exact-arithmetic reconciliation",
        "cells": cells,
        "flags_excluding_1_from_below": flags,
        "archived_flags_F7a": f7a_per_rung["flags_excluding_1_from_below"],
        "flag_rule": "any rung whose 99% interval excludes 1 from below is "
                     "TW-BREAK-shaped and routes to the Coordinator untouched, "
                     "never self-interpreted by the executor "
                     "(DEC-20261002-0df88e T-POINT RULE)",
    }
    json.dump(per_rung_out, open(os.path.join(OUT, "per_rung_T.json"), "w"),
              indent=1, sort_keys=True)
    stage("per_rung_T.json written")

    # ---- (b) segment slopes ------------------------------------------------
    seg = {}
    for q in ("ratio_frozen", "ratio_rank"):
        xs, ys, gs = build_series(new, 4, q, 26, 28)
        design = SlopeDesign(xs, ys, gs, selfcheck_seed=11058136)
        fit = bootstrap_slope(xs, ys, gs, reps=20000, level=0.95, seed=0)
        fit["impl"] = "verbatim stats.py bootstrap_slope reimplemented " \
                      "(random.Random(0))"
        lo_v, hi_v = design.interval(ys, 20000, 11058136)
        xcheck = {"vec_lo": lo_v, "vec_hi": hi_v,
                  "verbatim_lo": fit["lo"], "verbatim_hi": fit["hi"],
                  "absdiff_lo": abs(lo_v - fit["lo"]),
                  "absdiff_hi": abs(hi_v - fit["hi"])}
        ref_excl = (fit["hi"] < 0) or (fit["lo"] > 0)
        los, his, flips = [], [], 0
        for s in range(1, 201):
            lo2, hi2 = design.interval(ys, 2000, s)
            los.append(lo2)
            his.append(hi2)
            if ((hi2 < 0) or (lo2 > 0)) != ref_excl:
                flips += 1
        mc2 = {"seeds": "1..200", "reps": 2000,
               "lo_mean_sd": [statistics.mean(los), statistics.stdev(los)],
               "hi_mean_sd": [statistics.mean(his), statistics.stdev(his)],
               "flip_fraction_of_excludes_0": flips / 200}
        cfg_main, b, res, sd = calibrate(design, ys, q, supp=False,
                                         tag_prefix="F7b-replica")
        cfg_supp, _, _, _ = calibrate(design, ys, q, supp=True,
                                      tag_prefix="F7b-replica")
        cfgs = cfg_main + cfg_supp
        kap = max(c["kappa_95"] for c in cfgs)
        lo_c = fit["slope"] - kap * (fit["slope"] - fit["lo"])
        hi_c = fit["slope"] + kap * (fit["hi"] - fit["slope"])
        seg[q] = {
            "segment": "26..28 (TRUNCATED from the pre-registered 26..32; "
                       "rungs 30, 32 stopped by the RSS machine-protection "
                       "stop)",
            "n": len(xs), "rungs": {str(g): design.n_s[i]
                                    for i, g in enumerate(sorted(set(gs)))},
            "fit_20000_seed0": fit,
            "vectorized_crosscheck_20000": xcheck,
            "linear_form_selfcheck": design.selfcheck,
            "MC2_200seeds": mc2,
            "MC5_calibration": cfgs,
            "kappa_95_worst": kap,
            "calibrated_interval": [lo_c, hi_c],
            "excludes_0": (hi_c < 0) or (lo_c > 0),
            "levels_min_max": [min(2 ** y for y in ys), max(2 ** y for y in ys)],
        }
        stage(f"segment {q}: slope={fit['slope']:.6f} "
              f"nominal=[{fit['lo']:.6f}, {fit['hi']:.6f}] "
              f"calibrated=[{lo_c:.6f}, {hi_c:.6f}] kappa={kap:.4f}")

    # 12..24 reproduction cross-check (machinery validation; F7(a)'s exact
    # seeds; the archived values remain the reference)
    repro = {}
    for q in ("ratio_frozen", "ratio_rank"):
        xs, ys, gs = build_series(arch, 4, q, 12, 24)
        design = SlopeDesign(xs, ys, gs, selfcheck_seed=758510)
        fit = bootstrap_slope(xs, ys, gs, reps=20000, level=0.95, seed=0)
        cfg_main, _, _, _ = calibrate(design, ys, q, supp=False,
                                      tag_prefix="F7a-replica")
        cfg_supp, _, _, _ = calibrate(design, ys, q, supp=True,
                                      tag_prefix="F7a-replica")
        cfgs = cfg_main + cfg_supp
        kap = max(c["kappa_95"] for c in cfgs)
        lo_c = fit["slope"] - kap * (fit["slope"] - fit["lo"])
        hi_c = fit["slope"] + kap * (fit["hi"] - fit["slope"])
        ref = f7a_slopes["replica_fits_20000_seed0"][q]
        ref_cal = f7a_slopes["calibrated"][q]["calibrated_interval"]
        repro[q] = {
            "purpose": "machinery validation: reproduce F7(a)'s archived "
                       "12..24 fit exactly (same rows, same seeds, same "
                       "algorithm); the archived value remains the reference",
            "n": len(xs),
            "fit_20000_seed0": fit,
            "kappa_95_worst": kap,
            "calibrated_interval": [lo_c, hi_c],
            "F7a_reference": {"slope": ref["slope"], "lo": ref["lo"],
                             "hi": ref["hi"],
                             "calibrated_interval": ref_cal},
            "absdiff": {"slope": abs(fit["slope"] - ref["slope"]),
                        "lo": abs(fit["lo"] - ref["lo"]),
                        "hi": abs(fit["hi"] - ref["hi"]),
                        "cal_lo": abs(lo_c - ref_cal[0]),
                        "cal_hi": abs(hi_c - ref_cal[1])},
            "exact_reproduction": (
                abs(fit["slope"] - ref["slope"]) < 1e-12
                and abs(lo_c - ref_cal[0]) < 1e-12
                and abs(hi_c - ref_cal[1]) < 1e-12),
        }
        stage(f"reproduction {q}: slope={fit['slope']:.6f} "
              f"exact={repro[q]['exact_reproduction']}")

    # ---- (c) the outcome rule (DEC-20261002-0df88e, fixed before data) -----
    A_precise = f7a_slopes["replica_fits_20000_seed0"]["ratio_frozen"]["slope"]
    A_dec = -0.038062  # the decision's rounded quote (recorded)
    A_cal = f7a_slopes["calibrated"]["ratio_frozen"]["calibrated_interval"]
    seg_lo, seg_hi = seg["ratio_frozen"]["calibrated_interval"]
    contains_A = seg_lo <= A_precise <= seg_hi
    contains_A_rounded = seg_lo <= A_dec <= seg_hi
    contains_0 = seg_lo <= 0.0 <= seg_hi
    if not contains_A:
        outcome = "FLAT"
        direction = ("above (shallower than the 12..24 slope; flattening-shaped)"
                     if seg_lo > A_precise else
                     "below (steeper than the 12..24 slope)")
    elif contains_A and not contains_0:
        outcome = "CONT"
        direction = "overlaps the 12..24 slope and excludes 0"
    else:
        outcome = "AMBIG"
        direction = "overlaps both the 12..24 slope and 0"
    cross = len(flags) > 0
    overlap_arch_cal = not (seg_hi < A_cal[0] or seg_lo > A_cal[1])

    # naive-continuation context: measured T_frozen at 26/28 vs the 12..24
    # slope projection from T(24) (arithmetic on measured + archived values).
    # Stopped rungs (30, 32) have no rows; their N is the deterministic rung
    # prime the rung would have used (the driver's rung_launch records
    # confirm it), recovered from the task's own generator module.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_a8bbd8_ctx", os.path.join(HERE, "01_generator.py"))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    T24 = cells["m4|b24"]["frozen"]["T"]
    slope_1224 = A_precise
    x24 = math.log2([r for r in arch if r["m"] == 4 and r["bits"] == 24
                     and r["mode"] == "on"][0]["N"])
    proj = {}
    for bits in (26, 28, 30, 32):
        cell = cells.get(f"m4|b{bits}")
        rows_x = [r for r in (arch if bits in ARCH_RUNGS else new)
                  if r["m"] == 4 and r["bits"] == bits and r["mode"] == "on"]
        if rows_x:
            x = math.log2(rows_x[0]["N"])
            N_used = rows_x[0]["N"]
            N_source = "rows"
        else:
            N_used = gen.rung_prime(bits)
            x = math.log2(N_used)
            N_source = "rung_prime(bits) (deterministic; the stopped rung's N)"
        p = {"log2N": x, "N": N_used, "N_source": N_source,
             "projected_T_frozen_under_1224_slope":
             T24 * 2 ** (slope_1224 * (x - x24))}
        if cell:
            p["measured_T_frozen"] = cell["frozen"]["T"]
            p["measured_over_projection"] = (cell["frozen"]["T"]
                                             / p["projected_T_frozen_under_1224_slope"])
        else:
            p["measured_T_frozen"] = None
            p["note"] = ("rung stopped by the RSS machine-protection stop; "
                         "no measurement exists")
        proj[f"b{bits}"] = p

    outcome_block = {
        "rule": "DEC-20261002-0df88e power_rule_fixed_before_data / the card's "
                "OUTCOME RULE (FLAT / CONT / AMBIG / CROSS), fixed before data",
        "truncation": TRUNCATION,
        "primary_discriminator_status": "TRUNCATED: the pre-registered 26..32 "
                                        "segment slope could not be completed "
                                        "(rungs 30, 32 stopped by the RSS "
                                        "machine-protection stop); the "
                                        "branches are evaluated on the "
                                        "TRUNCATED 26..28 calibrated interval",
        "archived_1224_slope": {"precise": A_precise, "decision_quote": A_dec,
                                "calibrated_interval": A_cal},
        "segment_2628": {"slope": seg["ratio_frozen"]["fit_20000_seed0"]["slope"],
                         "nominal_95_20000": [seg["ratio_frozen"]["fit_20000_seed0"]["lo"],
                                              seg["ratio_frozen"]["fit_20000_seed0"]["hi"]],
                         "calibrated_interval": [seg_lo, seg_hi],
                         "kappa_95_worst": seg["ratio_frozen"]["kappa_95_worst"]},
        "interval_contains_1224_slope": contains_A,
        "interval_contains_1224_slope_rounded_quote": contains_A_rounded,
        "interval_contains_0": contains_0,
        "interval_overlaps_archived_calibrated_interval": overlap_arch_cal,
        "outcome_on_truncated_segment": outcome,
        "direction": direction,
        "T_point_tripwire": {
            "rule": "any rung whose calibrated 99% interval excludes 1 from "
                    "below is TW-BREAK-shaped and routes to the Coordinator "
                    "untouched, never self-interpreted",
            "new_rung_flags": flags,
            "archived_rung_flags_F7a": f7a_per_rung["flags_excluding_1_from_below"],
            "cross_fired": cross},
        "naive_continuation_context": {
            "note": "arithmetic context, not the discriminator: the measured "
                    "m4 frozen T at the new rungs against the naive 12..24 "
                    "slope projection from T(24) (the decision's own "
                    "projection method)",
            "T_frozen_24": T24, "slope_used": slope_1224, "rungs": proj},
    }
    if cross:
        outcome_block["cross_routing"] = (
            "CROSS fired: at least one rung's calibrated 99% T interval "
            "excludes 1 from below; per the rule this is TW-BREAK-shaped and "
            "routes to the Coordinator (review-breakthrough at max) "
            "untouched, never self-interpreted by this executor")

    seg_out = {
        "task": "TASK-20261002-a8bbd8",
        "truncation": TRUNCATION,
        "field_mapping": {
            "S_3": "stop['S'] (= table_s3 + search_s3, table included)",
            "r_frozen": "stop['r_frozen'] (= relations + sum(rows_fed), on mode)",
            "r_rank": "stop['rank'] (the solver rank)",
            "N, B": "row['N'], row['B']", "stop": "row['primary']",
            "x": "log2(N)", "groups": "the rung (bits)",
            "ratio": "S / (0.5 * sqrt(r * N)) (07_ptm5_analysis.py ratios())",
            "licensed_by": "attacks/07_ptm5_analysis.py; attacks/ptm5_engine.py "
                           "snapshot(); attacks/f3-lemma-map.yaml; "
                           "TASK-20261002-758e51/code/01_analysis.py",
        },
        "naming_note": "the card's 'log2 T_frozen' is the F7(a) per-instance "
                       "log2 ratio_frozen series (the archived 12..24 value "
                       "-0.038062 calibrated [-0.041782, -0.034385] is that "
                       "fit to every digit); 'weighted OLS' is the F7(a) "
                       "per-instance OLS (balanced 200-per-rung design)",
        "conventions": {
            "slope_fit": "frozen stats.py bootstrap_slope (stratified by "
                         "rung, one draw per member with replacement, "
                         "percentile endpoints by the stats.py index "
                         "arithmetic), reps=20000, level=0.95, seed=0 -- "
                         "reimplemented verbatim; never imported",
            "interval_calibration": "calibration/f7.py calibrate + f7_supp.py "
                                    "(gauss/t3/empirical + "
                                    "within_rung_empirical/rung_sd_gauss; "
                                    "beta0 in {0, slope}; 1000 series; inner "
                                    "reps 2000 seed 0); masters "
                                    "'F7b-replica-cal|<q>|<law>|<beta0:.6f>' "
                                    "for the new fit",
        },
        "segment_2628": seg,
        "reproduction_1224_crosscheck": repro,
        "outcome_rule_evaluation": outcome_block,
    }
    json.dump(seg_out, open(os.path.join(OUT, "segment_slopes.json"), "w"),
              indent=1, sort_keys=True)
    stage("segment_slopes.json written")

    stage("DONE")
    print(json.dumps({
        "truncated_segment_2628_ratio_frozen": {
            "slope": seg["ratio_frozen"]["fit_20000_seed0"]["slope"],
            "nominal": [seg["ratio_frozen"]["fit_20000_seed0"]["lo"],
                        seg["ratio_frozen"]["fit_20000_seed0"]["hi"]],
            "calibrated": seg["ratio_frozen"]["calibrated_interval"]},
        "reproduction_exact": {q: repro[q]["exact_reproduction"]
                               for q in repro},
        "outcome_on_truncated_segment": outcome,
        "direction": direction,
        "T_point_flags": flags,
        "cross_fired": cross,
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
