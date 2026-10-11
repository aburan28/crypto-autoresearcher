"""Proves-too-much control for RUN-ICEX-0ad4d8 (TASK-20261001-bd25c1).

Object 1: synthetic per-fixture complete-cost tables with a planted exponent
(0.40, 0.60, plus 0.50 as a reference) on q, using the six frozen fixtures'
q values and bit groups, fed end-to-end through the FROZEN analysis.analyse
(imported read-only from the pinned implementation; no bytecode written).
Noise is multiplicative lognormal at several sigmas, including the run's own
residual scale, and a residual-permutation variant reusing the run's actual
log-residuals.

Object 2: matched rho as a method: the frozen rho cells' measured costs fed
through the frozen ols_slope / bootstrap_slope.

No protocol-labelled run, no frozen-label draw: the synthetic noise uses this
task's own seed; the frozen bootstrap label inside analyse() is the frozen
code's fixed internal seed and is not a frozen-label DRAW of new data.
"""
import itertools
import json
import math
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "experiments/EXP-ICEX-aaccfc/implementation")
import analysis  # noqa: E402  frozen, pinned by TASK-20260929-a7f89b

RUN = "experiments/EXP-ICEX-aaccfc/runs/RUN-ICEX-0ad4d8"
FIXTURES = ["b16-s21", "b16-s22", "b16-s23", "b20-s21", "b20-s22", "b20-s23"]
cells = {f: json.load(open(f"{RUN}/cells/{f}__primary/result.json"))["result"] for f in FIXTURES}
qs = {f: cells[f]["fixture"]["N"] for f in FIXTURES}
bits = {f: cells[f]["fixture"]["bits"] for f in FIXTURES}
ref = lambda q: 13 * 0.886 * math.sqrt(q)


def synth_primary(costs):
    out = []
    for f in FIXTURES:
        tot = int(round(costs[f]))
        comp = {"stage1": tot - 2 * (tot // 3), "stage3": tot // 3, "descents": tot // 3}
        out.append({"fixture_id": f, "fixture": {"N": qs[f], "bits": bits[f]},
                    "complete_units": tot, "complete_units_components": comp,
                    "peak_rss_bytes": 0, "stage2_alpha2": {"mean_units": 28.0 * 5}, "factor_base": {"L": 5}})
    return out


def run_frozen(costs):
    m = analysis.analyse(synth_primary(costs), sensitivity=False)
    return m["exponent"], m["exponent_bootstrap"]["ci95"], m["verdict"]


# real residual scale
xs = [math.log(qs[f]) for f in FIXTURES]
ys = [math.log(cells[f]["complete_units"]) for f in FIXTURES]
b = analysis.ols_slope(xs, ys)
a = sum(ys) / 6 - b * sum(xs) / 6
resid = [y - (a + b * x) for x, y in zip(xs, ys)]
sigma_run = math.sqrt(sum(r * r for r in resid) / (6 - 2))

res = {"run_fit": {"exponent": b, "intercept": a, "residuals": dict(zip(FIXTURES, resid)),
                   "residual_sd_df4": sigma_run}}

# noiseless sanity: planted law recovered exactly
res["noiseless"] = {}
for beta in (0.40, 0.50, 0.60):
    for level in ("low_ratio", "run_level"):
        # low_ratio: cost = 0.5 * reference at the 20-bit geometric mean (ratio < 1); run_level: run's intercept scale
        if level == "low_ratio":
            q0 = math.exp(sum(math.log(qs[f]) for f in FIXTURES if bits[f] == 20) / 3)
            C = 0.5 * ref(q0) / q0 ** beta
        else:
            C = math.exp(a + (b - beta) * sum(xs) / 6)
        costs = {f: C * qs[f] ** beta for f in FIXTURES}
        e, ci, v = run_frozen(costs)
        res["noiseless"][f"{beta}_{level}"] = {"exponent": e, "ci95": ci, "verdict": v}

# noisy replicates
rnd = random.Random("TASK-20261001-bd25c1|proves-too-much")
REPS = 400
sigmas = [0.05, 0.10, 0.20, sigma_run]
res["noisy"] = {}
for beta in (0.40, 0.50, 0.60):
    q0 = math.exp(sum(math.log(qs[f]) for f in FIXTURES if bits[f] == 20) / 3)
    C = 0.5 * ref(q0) / q0 ** beta  # ratio < 1 at 20 bits so the ratio clause never masks the CI clause
    for s in sigmas:
        n_upper_lt_half = n_lower_ge_half = n_sub = n_neg = n_inc = 0
        exps = []
        for _ in range(REPS):
            costs = {f: C * qs[f] ** beta * math.exp(rnd.gauss(0, s)) for f in FIXTURES}
            e, (lo, hi), v = run_frozen(costs)
            exps.append(e)
            n_upper_lt_half += hi < 0.5
            n_lower_ge_half += lo >= 0.5
            n_sub += v == "sub_rho_signal"
            n_neg += v == "scoped_negative"
            n_inc += v == "inconclusive"
        exps.sort()
        res["noisy"][f"beta={beta}|sigma={s:.4f}"] = {
            "reps": REPS, "frac_ci_upper_lt_0.5": n_upper_lt_half / REPS,
            "frac_ci_lower_ge_0.5": n_lower_ge_half / REPS,
            "verdicts": {"sub_rho_signal": n_sub, "scoped_negative": n_neg, "inconclusive": n_inc},
            "exponent_median": exps[REPS // 2]}
    # residual-permutation variant: the run's own residuals, all 720 permutations
    n_up = n_lo = 0
    vs = {"sub_rho_signal": 0, "scoped_negative": 0, "inconclusive": 0}
    perms = list(itertools.permutations(resid))
    for pr in perms:
        costs = {f: C * qs[f] ** beta * math.exp(r) for f, r in zip(FIXTURES, pr)}
        e, (lo, hi), v = run_frozen(costs)
        n_up += hi < 0.5
        n_lo += lo >= 0.5
        vs[v] += 1
    res["noisy"][f"beta={beta}|run_residual_permutations"] = {
        "reps": len(perms), "frac_ci_upper_lt_0.5": n_up / len(perms), "frac_ci_lower_ge_0.5": n_lo / len(perms),
        "verdicts": vs}

# structural property of the fixture-level bootstrap: share of resamples drawn from one bit group only
n_one_group = 0
grp = [bits[f] for f in FIXTURES]
for idx in itertools.product(range(6), repeat=6):
    if len(set(grp[i] for i in idx)) == 1 and len(set(idx)) > 1:
        n_one_group += 1
xr16 = max(xs[:3]) - min(xs[:3])
xr20 = max(xs[3:]) - min(xs[3:])
res["bootstrap_structure"] = {
    "resamples_total": 6 ** 6, "single_bit_group_nondegenerate": n_one_group,
    "share": n_one_group / 6 ** 6,
    "log_q_range_within_16bit": xr16, "log_q_range_within_20bit": xr20,
    "log_q_gap_between_groups_mean": sum(xs[3:]) / 3 - sum(xs[:3]) / 3,
    "note": "single-group resamples estimate the slope over a log-q range of ~0.3-0.5 instead of ~2.6; their share exceeds each 2.5% tail"}

# object 2: matched rho through the frozen slope/CI code
rho = {f: json.load(open(f"{RUN}/cells/{f}__rho/result.json"))["result"] for f in FIXTURES}
rx = [math.log(rho[f]["fixture"]["N"]) for f in FIXTURES]
for key in ("mean_walk_units", "mean_units"):
    ry = [math.log(rho[f][key]) for f in FIXTURES]
    res[f"rho_{key}"] = {"exponent": analysis.ols_slope(rx, ry),
                         "frozen_bootstrap": analysis.bootstrap_slope(rx, ry, "TASK-20261001-bd25c1|rho|" + key)}
pre = [sum(t["precompute_units"] for t in rho[f]["targets"]) / len(rho[f]["targets"]) for f in FIXTURES]
res["rho_precompute_share"] = {f: p / rho[f]["mean_units"] for f, p in zip(FIXTURES, pre)}

json.dump(res, open(sys.argv[1], "w"), indent=1)
print(json.dumps(res, indent=1))
