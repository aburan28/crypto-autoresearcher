"""Executor for EXP-ICINV-180a0d and EXP-INSTR-2d32ba (GOAL-ENDO-001, BATCH-cb71b5).

EXP-INSTR-2d32ba runs FIRST and is blocking: the variance instrument must
detect a planted signal of known size and must reject a matched null. A failed
instrument makes every downstream number `attempted_and_inconclusive`, never
negative evidence (AGENTS.md rule 5, and the RQ-INSTR-f8faa0 two-directional
control).

EXP-ICINV-180a0d then measures, over a COMPLETELY enumerated isogeny class
whose completeness is certified against the Hurwitz-Kronecker class number,
whether any of five attack-cost functionals has within-class variance above its
own null.

Usage:
    python3 -m harness.run_icinv --p 4001 --fb-m2 40 --fb-m3 13 --targets 400
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from dataclasses import asdict

from . import isogeny_class as ic
from . import exp_icinv as ex
from .runner import RunResult, curve_id, write_run

EXP_ICINV = "EXP-ICINV-9b1f7c"   # supersedes EXP-ICINV-180a0d (confounded sampler)
EXP_INSTR = "EXP-INSTR-2d32ba"


# --------------------------------------------------------------------------
# EXP-INSTR: two-directional instrument control (blocking)
# --------------------------------------------------------------------------


def instrument_control(n_curves: int, trials: int, true_rate: float,
                       planted_spread: float, seed: int) -> dict:
    """Does the over-dispersion test detect a planted effect and reject a null?

    NEGATIVE DIRECTION: n_curves curves all with the SAME true rate. The test
    must return "invariant" -- if it fires here it cannot support a positive.

    POSITIVE DIRECTION: the same setup but with per-curve rates spread by
    +-planted_spread. The test must return "over-dispersed" -- if it misses
    here it cannot support a negative, which is the direction this campaign
    most needs, since its expected result is invariance.
    """
    rng = random.Random(seed)

    null_hits = [sum(1 for _ in range(trials) if rng.random() < true_rate)
                 for _ in range(n_curves)]
    v_null = ex.binomial_null_verdict("planted:null", null_hits, trials)

    planted_hits = []
    planted_rates = []
    for i in range(n_curves):
        r = true_rate + planted_spread * (2 * ((i % 2)) - 1)
        r = min(max(r, 0.001), 0.999)
        planted_rates.append(r)
        planted_hits.append(sum(1 for _ in range(trials) if rng.random() < r))
    v_planted = ex.binomial_null_verdict("planted:signal", planted_hits, trials)

    detects = v_planted.verdict == "over-dispersed"
    rejects = v_null.verdict == "invariant"
    return {
        "n_curves": n_curves, "trials": trials, "true_rate": true_rate,
        "planted_spread": planted_spread, "seed": seed,
        "null_direction": asdict(v_null),
        "signal_direction": asdict(v_planted),
        "detects_planted_signal": detects,
        "rejects_matched_null": rejects,
        "instrument_passes": bool(detects and rejects),
        "minimum_detectable_spread_note": (
            "The planted spread is the smallest effect this control demonstrates "
            "the instrument can see at this (n_curves, trials). A null result in "
            "EXP-ICINV bounds within-class variation only BELOW this spread; it "
            "does not establish exact invariance."),
    }


def sensitivity_floor(n_curves: int, trials: int, true_rate: float,
                      seed: int, spreads: list[float]) -> dict:
    """Smallest planted spread the test detects at this configuration.

    Reported so the EXP-ICINV negative can be stated as a BOUND rather than as
    "no effect", which would be an overclaim.
    """
    out = {}
    for s in spreads:
        r = instrument_control(n_curves, trials, true_rate, s, seed)
        out[f"{s:.4f}"] = r["detects_planted_signal"]
    detected = [float(k) for k, v in out.items() if v]
    return {"by_spread": out,
            "smallest_detected_spread": min(detected) if detected else None}


# --------------------------------------------------------------------------
# EXP-ICINV: within-class variance
# --------------------------------------------------------------------------


def _largest_prime_factor(n: int) -> int:
    return max(ex._factor(n))


def pick_classes(p: int, n_control: int = 3) -> tuple[int, list[int], dict]:
    """Target class = the ordinary class with the most curves; controls = the
    next largest classes with a DIFFERENT trace. Selection is by class size
    only -- never by any measured functional, which would be selection on the
    outcome."""
    classes = ic.isogeny_classes(p)
    cens = ic.class_census(p, classes)
    failures = [c for c in cens if not c.agrees]
    ordinary = [(len(v), t) for t, v in classes.items() if t % p != 0]
    ordinary.sort(reverse=True)
    target = ordinary[0][1]
    controls = [t for _, t in ordinary[1:1 + n_control]]
    census = {
        "traces_checked": len(cens),
        "census_failures": len(failures),
        "failed_traces": [c.trace for c in failures][:10],
        "target_trace": target,
        "target_class_size": len(classes[target]),
        "target_class_weighted": sum(2.0 / r.aut_order for r in classes[target]),
        "target_class_predicted_weighted":
            ic.hurwitz_class_number(4 * p - target * target),
        "control_traces": controls,
    }
    return target, controls, {"classes": classes, "census": census}


def measure_class(recs, fb_m2: int, fb_m3: int, window: int, targets: int,
                  seed: int) -> list[dict]:
    out = []
    for i, rec in enumerate(recs):
        E = rec.curve()
        fb2 = ex.factor_base_fixed_size(E, fb_m2)
        fb3 = ex.factor_base_fixed_size(E, fb_m3)
        # UNIFORM sampler: the hash-and-lift sampler encodes #E and so
        # confounds every between-class comparison (CORR-20260807-a05e1e).
        tg = ex.targets_uniform(E, rec.order, targets, seed)
        h2, t2 = ex.decomposition_rate_m2(E, fb2, tg)
        h3, t3 = ex.decomposition_rate_m3(E, fb3, tg)
        out.append({
            "a": rec.a, "b": rec.b, "j": rec.j, "trace": rec.trace,
            "order": rec.order, "aut_order": rec.aut_order,
            "fb_m2": len(fb2), "fb_m3": len(fb3), "targets": len(tg),
            "hits_m2": h2, "rate_m2": h2 / t2 if t2 else float("nan"),
            "hits_m3": h3, "rate_m3": h3 / t3 if t3 else float("nan"),
            "liftable_density": ex.liftable_density(E, window),
            "window_fb_size": len(ex.factor_base_window(E, window)),
            "s3_support": ex.s3_monomial_support(rec.p, rec.a, rec.b),
            "two_torsion_x": ex.two_torsion_x_count(rec.p, rec.a, rec.b),
            "full_liftable": len(ex.factor_base_window(E, rec.p)),
            "eff_m2": ex.decomposition_efficiency(
                h2 / t2 if t2 else float("nan"), rec.order, len(fb2), 2),
            "eff_m3": ex.decomposition_efficiency(
                h3 / t3 if t3 else float("nan"), rec.order, len(fb3), 3),
        })
    return out


def analyse(rows: list[dict], trials: int) -> dict:
    verdicts = {}
    verdicts["decomp_rate_m2"] = asdict(ex.binomial_null_verdict(
        "decomp_rate_m2", [r["hits_m2"] for r in rows], trials))
    verdicts["decomp_rate_m3"] = asdict(ex.binomial_null_verdict(
        "decomp_rate_m3", [r["hits_m3"] for r in rows], trials))
    verdicts["liftable_density"] = asdict(ex.exact_null_verdict(
        "liftable_density", [r["liftable_density"] for r in rows]))
    verdicts["window_fb_size"] = asdict(ex.exact_null_verdict(
        "window_fb_size", [float(r["window_fb_size"]) for r in rows]))
    verdicts["s3_support"] = asdict(ex.exact_null_verdict(
        "s3_support", [float(r["s3_support"]) for r in rows]))
    verdicts["order"] = asdict(ex.exact_null_verdict(
        "order", [float(r["order"]) for r in rows]))
    verdicts["two_torsion_x"] = asdict(ex.exact_null_verdict(
        "two_torsion_x", [float(r["two_torsion_x"]) for r in rows]))
    # The liftable-count identity is a DERIVATION, checked here rather than
    # assumed: it is what reduces the full-field liftable variance to the
    # 2-torsion structure and thereby drains it of attack content.
    ok = all(r["full_liftable"] == ex.liftable_count_identity(
        r["order"], r["two_torsion_x"]) for r in rows)
    verdicts["_liftable_identity_holds"] = {
        "functional": "#liftable_x == (#E - 1 + z)/2",
        "n_curves": len(rows), "holds_on_all": bool(ok),
        "verdict": "identity_verified" if ok else "IDENTITY_FAILED",
        "detail": ("full-field liftable density is a function of (#E, z) alone; "
                   "#E is class-invariant and z is not, so the entire "
                   "within-class variation is the 2-torsion structure"),
    }
    return verdicts


def window_decay(p: int, traces: list[int], classes, windows: list[int],
                 seed: int) -> dict:
    """Decay test for the liftable-density signal (the campaign's sharpest control).

    #E(F_p) = p + 1 + sum_{x in F_p} chi(x^3+ax+b), so over the FULL field the
    liftable count is an exact function of the trace and is therefore class-
    invariant BY DEFINITION. Over a window of size W < p it is only partially
    determined by the trace. Any apparent "isogeny class predicts liftable
    density" signal must therefore STRENGTHEN as W -> p and vanish as W -> 0,
    purely arithmetically and with no attack content whatsoever.

    Running this is what distinguishes a trivial restatement of the trace from a
    structural finding. A signal that did NOT behave this way would be the
    interesting one.
    """
    out = {}
    for W in windows:
        groups, within = {}, []
        for t in traces:
            vals = [ex.liftable_density(r.curve(), W) for r in classes[t]]
            groups[t] = vals
            if len(vals) > 1:
                within.append(statistics.variance(vals))
        obs, nullmean, pval = ex.permutation_null(groups, iterations=1000,
                                                  seed=seed)
        # variance of the count, not the rate, is the scale-free comparison
        cnt_var = [statistics.variance([v * W for v in groups[t]])
                   for t in traces if len(groups[t]) > 1]
        out[str(W)] = {
            "window": W, "window_fraction_of_p": W / p,
            "mean_within_class_rate_variance": sum(within) / len(within),
            "mean_within_class_count_variance": sum(cnt_var) / len(cnt_var),
            "permutation_p_value": pval,
            "observed_mean_within_variance": obs,
            "null_mean": nullmean,
        }
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=4001)
    ap.add_argument("--fb-m2", type=int, default=40)
    ap.add_argument("--fb-m3", type=int, default=13)
    ap.add_argument("--window", type=int, default=400)
    ap.add_argument("--targets", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--controls", type=int, default=3)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)

    suffix = args.suffix or f"p{args.p}s{args.seed}"
    cmd = "python3 -m harness.run_icinv " + " ".join(sys.argv[1:])

    # ---------------- EXP-INSTR (blocking) ----------------
    started = time.time()
    print("== EXP-INSTR-2d32ba: two-directional instrument control ==")
    ctrl = instrument_control(n_curves=40, trials=args.targets,
                              true_rate=0.35, planted_spread=0.05,
                              seed=args.seed)
    ctrl["sensitivity_floor"] = sensitivity_floor(
        40, args.targets, 0.35, args.seed,
        [0.005, 0.01, 0.02, 0.03, 0.05, 0.08])
    print(json.dumps({k: v for k, v in ctrl.items()
                      if k in ("detects_planted_signal", "rejects_matched_null",
                               "instrument_passes")}, indent=1))
    print(" sensitivity floor:", ctrl["sensitivity_floor"]["smallest_detected_spread"])
    finished = time.time()

    if not args.no_write:
        rid = write_run(EXP_INSTR, "INSTR", RunResult(
            run_suffix=suffix, curve_id="n/a (synthetic instrument control)",
            seed=args.seed,
            parameters={"n_curves": 40, "trials": args.targets,
                        "true_rate": 0.35, "planted_spread": 0.05},
            metrics={"detects_planted_signal": ctrl["detects_planted_signal"],
                     "rejects_matched_null": ctrl["rejects_matched_null"],
                     "instrument_passes": ctrl["instrument_passes"],
                     "smallest_detected_spread":
                         ctrl["sensitivity_floor"]["smallest_detected_spread"]},
            certificate={"kind": "none"},
            valid=True,
            stdout=json.dumps(ctrl, indent=1), raw=ctrl),
            status="completed", command=cmd, started=started, finished=finished)
        print(" wrote", rid)

    if not ctrl["instrument_passes"]:
        print("INSTRUMENT FAILED ITS CONTROL -- downstream measurement is "
              "attempted_and_inconclusive, not evidence.")
        return 2

    # ---------------- EXP-ICINV ----------------
    started = time.time()
    print(f"\n== EXP-ICINV-180a0d: within-class variance at p={args.p} ==")
    target, controls, meta = pick_classes(args.p, args.controls)
    census = meta["census"]
    classes = meta["classes"]
    print(" census:", json.dumps(census, default=str))
    if census["census_failures"]:
        print("CENSUS FAILED -- enumeration incomplete; run is invalid.")
        return 3

    per_class = {}
    for t in [target] + controls:
        rows = measure_class(classes[t], args.fb_m2, args.fb_m3,
                             args.window, args.targets, args.seed)
        per_class[t] = {"rows": rows, "verdicts": analyse(rows, args.targets),
                        "n_curves": len(rows), "order": classes[t][0].order,
                        "largest_prime_factor":
                            _largest_prime_factor(classes[t][0].order)}
        print(f"\n trace={t:5d} order={classes[t][0].order} n_curves={len(rows)}")
        for name, v in per_class[t]["verdicts"].items():
            if "mean" not in v:
                print(f"   {name:20s} {v['verdict']} (n={v['n_curves']})")
                continue
            print(f"   {name:20s} mean={v['mean']:.5g} var={v['variance']:.4g} "
                  f"null={v['null_variance']:.4g} ratio={v['ratio']:.3f} "
                  f"-> {v['verdict']}  [{v['detail']}]")

    # NULL-C: does the isogeny-class grouping carry information?
    perm = {}
    # NULL-C is run on the ORDER-NORMALISED efficiency, not the raw rate. A raw
    # rate is ~ |mV| / #E and #E differs between classes by construction, so a
    # permutation null on raw rates detects the group order and reports it as
    # structure. Both are reported; only the efficiency rows are evidence.
    for fn, key in (("decomp_efficiency_m2", "eff_m2"),
                    ("decomp_efficiency_m3", "eff_m3"),
                    ("decomp_rate_m2_RAW_confounded_by_order", "rate_m2"),
                    ("decomp_rate_m3_RAW_confounded_by_order", "rate_m3"),
                    ("liftable_density", "liftable_density")):
        groups = {t: [r[key] for r in per_class[t]["rows"]]
                  for t in per_class}
        obs, nullmean, pval = ex.permutation_null(groups, iterations=2000,
                                                  seed=args.seed)
        perm[fn] = {"observed_mean_within_variance": obs,
                    "null_mean": nullmean, "p_value": pval,
                    "is_evidence": not fn.endswith("RAW_confounded_by_order"),
                    "interpretation":
                        (("class grouping reduces within-group variance"
                          if pval < 0.05 else
                          "class grouping carries no detectable information")
                         + ("" if not fn.endswith("RAW_confounded_by_order") else
                            " -- BUT THIS ROW IS NOT EVIDENCE: the raw rate is "
                            "confounded by #E, which differs between classes by "
                            "construction; read the efficiency row instead"))}
        print(f"\n NULL-C {fn}: obs={obs:.6g} null={nullmean:.6g} p={pval:.4f} "
              f"-> {perm[fn]['interpretation']}")
    # DECAY TEST: is the liftable-density class signal just the trace?
    wins = sorted({max(8, args.p // 32), args.p // 16, args.p // 8,
                   args.p // 4, args.p // 2, args.p})
    decay = window_decay(args.p, [target] + controls, classes, wins, args.seed)
    print("\n== decay test: liftable_density vs window size ==")
    for k in sorted(decay, key=int):
        d = decay[k]
        print(f"  W={d['window']:6d} ({d['window_fraction_of_p']:.3f} p)  "
              f"within-class count-var={d['mean_within_class_count_variance']:10.3f}  "
              f"perm p={d['permutation_p_value']:.4f}")
    # The identity is #liftable_x = (#E - 1 + z)/2 with z the 2-torsion count.
    # #E is class-invariant and z is not, so the full-field within-class variance
    # of the COUNT is predicted to be Var(z)/4 -- NOT zero. The first version of
    # this check tested `< 1e-9` and therefore printed "NOT explained by the
    # trace identity -- investigate" on runs where the identity in fact held to
    # 3e-14. The threshold was wrong, not the identity. See CORR-20260807-2c9ae4.
    full = decay[str(args.p)]
    zvars = [statistics.variance([r["two_torsion_x"] for r in per_class[t]["rows"]])
             for t in per_class if len(per_class[t]["rows"]) > 1]
    predicted = (sum(zvars) / len(zvars) / 4.0) if zvars else 0.0
    observed = full["mean_within_class_count_variance"]
    residual = abs(observed - predicted)
    decay_verdict = (
        f"FULLY EXPLAINED by the liftable-count identity: observed within-class "
        f"count variance {observed:.12g} matches the predicted Var(z)/4 = "
        f"{predicted:.12g} to {residual:.3g}. The full-field liftable count is a "
        f"function of (#E, z) alone; #E is the class invariant and z is the "
        f"2-torsion structure, so the quantity carries no attack content."
        if residual < 1e-9 else
        f"NOT explained by the identity: observed {observed:.12g} vs predicted "
        f"Var(z)/4 = {predicted:.12g}, residual {residual:.3g} -- investigate")
    decay["identity_check"] = {"observed": observed, "predicted_var_z_over_4":
                               predicted, "residual": residual,
                               "holds": residual < 1e-9}
    print("  verdict:", decay_verdict)
    finished = time.time()

    raw = {"p": args.p, "params": vars(args), "census": census,
           "target_sampler": "targets_uniform (multiples of a base point)",
           "supersedes": "EXP-ICINV-180a0d, which used the confounded "
                         "hash-and-lift sampler; see CORR-20260807-a05e1e",
           "per_class": per_class, "permutation_null": perm,
           "window_decay": decay, "decay_verdict": decay_verdict,
           "instrument_control_ref": EXP_INSTR}

    metrics = {
        "target_trace": target,
        "target_class_size": census["target_class_size"],
        "census_failures": census["census_failures"],
        "verdicts_target": {k: v["verdict"]
                            for k, v in per_class[target]["verdicts"].items()},
        "verdicts_controls": {str(t): {k: v["verdict"]
                                       for k, v in per_class[t]["verdicts"].items()}
                              for t in controls},
        "permutation_p_values": {k: v["p_value"] for k, v in perm.items()},
        "decay_verdict": decay_verdict,
        "full_field_liftable_within_class_count_variance":
            decay[str(args.p)]["mean_within_class_count_variance"],
    }
    print("\n== summary ==")
    print(json.dumps(metrics, indent=1, default=str))

    if not args.no_write:
        rid = write_run(EXP_ICINV, "ICINV", RunResult(
            run_suffix=suffix,
            curve_id=f"CLASS-p{args.p}-t{target}",
            seed=args.seed,
            parameters={k: v for k, v in vars(args).items()
                        if k not in ("suffix", "no_write")},
            metrics=metrics,
            certificate={"kind": "none"},
            valid=True,
            stdout="", raw=raw),
            status="completed", command=cmd, started=started, finished=finished)
        print("wrote", rid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
