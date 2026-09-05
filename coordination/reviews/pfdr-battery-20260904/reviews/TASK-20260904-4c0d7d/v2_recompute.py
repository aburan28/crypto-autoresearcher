#!/usr/bin/env python3
"""V2: raw/summary agreement, recomputed from runs/*/raw-result.json ONLY.

Independent Validator recomputation for TASK-20260904-4c0d7d.
Does not read analysis.json / analysis.md, and does not import the producer's
analyze.py or harness/.
"""
import collections
import json
import math
import os
import sys

ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-fd901a/runs")
SWEEPS = {
    "p4099": "RUN-PFDR-fd901a-sweep-p4099",
    "p64": "RUN-PFDR-fd901a-sweep-p64",
    "p256": "RUN-PFDR-fd901a-sweep-p256",
}
DEGREES = ["3", "4", "5", "6"]
PER_LAYER_INV = ["full_rank", "top_rank", "fall_dim", "syzygy_dim", "deficit_series"]
CUM_INV = ["full_rank", "deficit_series"]


def load(run):
    with open(os.path.join(RUNS, run, "raw-result.json")) as fh:
        return json.load(fh)


def invariants(draw):
    """Every recorded invariant of one draw, as a flat dict."""
    out = {}
    for D in DEGREES:
        pl = draw["per_layer"].get(D)
        if pl is None:
            continue
        for inv in PER_LAYER_INV:
            out[f"{inv}@{D}"] = pl[inv]
    out["d_ff"] = draw["d_ff"]
    cum = draw.get("cumulative") or {}
    for D in DEGREES:
        c = cum.get(D)
        if c is None:
            continue
        for inv in CUM_INV:
            out[f"cum_{inv}@{D}"] = c[inv]
    return out


def key(draw):
    k = [draw["arm"], draw["curve_seed"], draw["target_seed"]]
    if "null_seed" in draw:
        k.append(draw["null_seed"])
    return tuple(k)


def clopper_pearson_upper_zero(n, alpha=0.05):
    """Exact CP two-sided upper limit when 0 of n succeeded: 1-(alpha/2)^(1/n)."""
    return 1.0 - (alpha / 2.0) ** (1.0 / n)


def profile(draw):
    return [[draw["per_layer"][D]["full_rank"], draw["per_layer"][D]["top_rank"]]
            for D in DEGREES if D in draw["per_layer"]]


def main():
    out = {}
    data = {k: load(v) for k, v in SWEEPS.items()}

    # ---- 1. draw counts -------------------------------------------------
    counts = {}
    for pk, d in data.items():
        c = collections.Counter(x["arm"] for x in d["raw"]["draws"])
        counts[pk] = {"per_arm": dict(sorted(c.items())),
                      "total": len(d["raw"]["draws"]),
                      "valid_flag_all_true": all(x.get("valid") is True
                                                 for x in d["raw"]["draws"]),
                      "manifest_metrics_draw_count": d["metrics"]["draw_count"],
                      "manifest_metrics_per_arm": d["metrics"]["draws_per_arm"]}
    out["draw_counts"] = counts

    # ---- 2. duplicate-key check -----------------------------------------
    dups = {}
    for pk, d in data.items():
        ks = [key(x) for x in d["raw"]["draws"]]
        dd = [k for k, n in collections.Counter(ks).items() if n > 1]
        dups[pk] = dd
    out["duplicate_draw_keys"] = dups

    # ---- 3. modal profiles per arm --------------------------------------
    modal = {}
    for pk, d in data.items():
        m = {}
        for arm in sorted({x["arm"] for x in d["raw"]["draws"]}):
            draws = [x for x in d["raw"]["draws"] if x["arm"] == arm]
            hist = collections.Counter(json.dumps(profile(x)) for x in draws)
            dhist = collections.Counter(x["d_ff"] for x in draws)
            fhist = collections.Counter(json.dumps(x["profile_fall_dim"])
                                        for x in draws)
            m[arm] = {"profile_hist": dict(hist), "d_ff_hist": dict(dhist),
                      "fall_dim_hist": dict(fhist), "n": len(draws)}
        modal[pk] = m
    out["modal_profiles"] = modal

    # ---- 4. flatness pairing 64-bit vs P-256 -----------------------------
    pairing = {}
    d64 = {key(x): x for x in data["p64"]["raw"]["draws"]}
    d256 = {key(x): x for x in data["p256"]["raw"]["draws"]}
    for arm in sorted({k[0] for k in d64} | {k[0] for k in d256}):
        k64 = {k for k in d64 if k[0] == arm}
        k256 = {k for k in d256 if k[0] == arm}
        common = sorted(k64 & k256)
        identical = 0
        per_inv = collections.Counter()
        differing = []
        for k in common:
            a, b = invariants(d64[k]), invariants(d256[k])
            keys = sorted(set(a) | set(b))
            same = True
            for kk in keys:
                if a.get(kk) == b.get(kk):
                    per_inv[kk] += 1
                else:
                    same = False
            if same:
                identical += 1
            else:
                differing.append(list(k))
        pairing[arm] = {
            "n_64": len(k64), "n_256": len(k256), "paired": len(common),
            "unpaired_64_only": len(k64 - k256), "unpaired_256_only": len(k256 - k64),
            "identical_on_every_invariant": identical,
            "differing_draws": differing,
            "per_invariant_identical": dict(sorted(per_inv.items())),
        }
    out["flatness_pairing_64_vs_256"] = pairing

    # arm purity: no flatness label mixes arms (invalidation rule 5)
    out["arm_purity"] = {
        "pairing_is_within_arm": True,
        "planted_arms": ["semaev", "semaev_named_p256", "noncurve_cubic",
                         "secondary_direct_B8"],
        "unplanted_arms": ["null_support", "null_support_named_p256"],
        "note": ("each pairing bucket above is keyed on arm as its first "
                 "component, so no bucket contains draws from two arms"),
    }

    # ---- 5. rank-drop events at 4099 vs the 64-bit modal profile ---------
    rank_drop = {}
    for arm in ["semaev", "null_support", "noncurve_cubic"]:
        d64a = [x for x in data["p64"]["raw"]["draws"] if x["arm"] == arm]
        mode64 = collections.Counter(
            json.dumps(profile(x)) for x in d64a).most_common(1)[0][0]
        mode64 = json.loads(mode64)
        d4099a = [x for x in data["p4099"]["raw"]["draws"] if x["arm"] == arm]
        drops = 0
        anydiff = 0
        by_degree = {D: 0 for D in DEGREES}
        drop_draws = []
        for x in d4099a:
            pr = profile(x)
            is_drop = False
            is_diff = False
            for i, D in enumerate(DEGREES):
                if pr[i] != mode64[i]:
                    is_diff = True
                if pr[i][0] < mode64[i][0] or pr[i][1] < mode64[i][1]:
                    is_drop = True
                    by_degree[D] += 1
            drops += int(is_drop)
            anydiff += int(is_diff)
            if is_drop:
                drop_draws.append(list(key(x)))
        n = len(d4099a)
        rank_drop[arm] = {
            "n": n, "mode_64bit": mode64, "drop_events": drops,
            "any_difference_events": anydiff, "rate": drops / n,
            "drops_by_degree": by_degree,
            "clopper_pearson_95_upper_for_0_of_n":
                clopper_pearson_upper_zero(n) if drops == 0 else None,
            "drop_draws": drop_draws,
        }
    out["rank_drop_at_4099"] = rank_drop
    out["clopper_pearson_check"] = {
        "0_of_40": clopper_pearson_upper_zero(40),
        "0_of_200": clopper_pearson_upper_zero(200),
        "formula": "1 - (0.05/2)**(1/n)",
    }

    # ---- 6. Semaev-minus-null table at each prime -----------------------
    smn = {}
    for pk, d in data.items():
        sem = [x for x in d["raw"]["draws"] if x["arm"] == "semaev"]
        nul = [x for x in d["raw"]["draws"] if x["arm"] == "null_support"]

        def modal_inv(draws):
            allinv = [invariants(x) for x in draws]
            keys = sorted(allinv[0])
            mv, unanimous = {}, {}
            for kk in keys:
                cnt = collections.Counter(a[kk] for a in allinv)
                v, n = cnt.most_common(1)[0]
                mv[kk] = v
                unanimous[kk] = (n == len(allinv))
            return mv, unanimous

        ms, us = modal_inv(sem)
        mn, un = modal_inv(nul)
        diff = {kk: ms[kk] - mn[kk] for kk in sorted(ms)}
        smn[pk] = {"semaev_modal": ms, "null_modal": mn, "difference": diff,
                   "nonzero_differences": {kk: v for kk, v in diff.items() if v != 0},
                   "semaev_unanimous": all(us.values()),
                   "null_unanimous": all(un.values()),
                   "n_semaev": len(sem), "n_null": len(nul)}
    out["semaev_minus_null"] = smn
    tables = {pk: json.dumps(v["difference"], sort_keys=True)
              for pk, v in smn.items()}
    out["semaev_minus_null_identical_across_primes"] = len(set(tables.values())) == 1
    out["semaev_minus_null_identical_large_primes_only"] = (
        tables["p64"] == tables["p256"])

    # ---- 7. null RNG seed distinctness -----------------------------------
    nulls = {}
    for pk, d in data.items():
        for arm in ["null_support", "null_support_named_p256"]:
            draws = [x for x in d["raw"]["draws"] if x["arm"] == arm]
            if not draws:
                continue
            mixed = [x["rng_seed_mixed"] for x in draws]
            cnt = collections.Counter(mixed)
            per_ct = collections.defaultdict(set)
            for x in draws:
                per_ct[(x["curve_seed"], x["target_seed"])].add(x["rng_seed_mixed"])
            nulls[f"{pk}:{arm}"] = {
                "n": len(draws),
                "distinct_rng_seed_mixed": len(cnt),
                "collisions": [s for s, c in cnt.items() if c > 1],
                "distinct_null_seed_labels": sorted({x["null_seed"] for x in draws}),
                "seeds_per_curve_target_min": min(len(v) for v in per_ct.values()),
                "curve_target_cells": len(per_ct),
            }
        # cross-prime: are the mixed seeds different at different p?
    allmixed = {}
    for pk, d in data.items():
        allmixed[pk] = {x["rng_seed_mixed"]
                        for x in d["raw"]["draws"] if x["arm"] == "null_support"}
    out["null_rng_seeds"] = nulls
    out["null_rng_seed_overlap_across_primes"] = {
        "p4099_p64": len(allmixed["p4099"] & allmixed["p64"]),
        "p64_p256": len(allmixed["p64"] & allmixed["p256"]),
    }

    # ---- 8. certificates recorded in raw ---------------------------------
    certs = {}
    for pk, d in data.items():
        draws = d["raw"]["draws"]
        withc = [x for x in draws if "certificate_verified" in x]
        certs[pk] = {
            "draws_with_certificate_field": len(withc),
            "certificate_verified_true": sum(1 for x in withc
                                             if x["certificate_verified"]),
            "certificate_verified_false": sum(1 for x in withc
                                              if not x["certificate_verified"]),
            "manifest_planted_certificates_total":
                d["metrics"]["planted_certificates_total"],
            "manifest_planted_certificates_failed":
                d["metrics"]["planted_certificates_failed"],
            "generator_vanishes_all_true": all(
                x.get("stilde_vanishes_at_planted_point",
                      x.get("generator_vanishes_at_planted_point",
                            x.get("system_vanishes_at_planted_point", True)))
                for x in draws),
        }
    out["certificates_in_raw"] = certs

    # ---- 9. positive control from raw ------------------------------------
    pos = {}
    for run, label in [("RUN-PFDR-fd901a-posctrl-p4099", "p4099"),
                       ("RUN-PFDR-fd901a-posctrl-p16411", "p16411")]:
        d = load(run)
        draws = d["raw"]["draws"]
        pos[label] = {
            "n": len(draws),
            "B": sorted({x.get("B") for x in draws}),
            "d_ff_hist": dict(collections.Counter(x["d_ff"] for x in draws)),
            "d_top_full_hist": dict(collections.Counter(x.get("d_top_full")
                                                        for x in draws)),
            "series_d_reg_hist": dict(collections.Counter(x.get("series_d_reg")
                                                          for x in draws)),
            "cert_verified_all": all(x.get("certificate_verified") for x in draws),
            "curve_seeds": sorted({x["curve_seed"] for x in draws}),
            "target_seeds": sorted({x["target_seed"] for x in draws}),
        }
        # recompute d_ff from per_layer: first D with fall_dim > 0
        recomputed = []
        for x in draws:
            pl = x["per_layer"]
            ds = sorted(int(k) for k in pl)
            ff = next((D for D in ds if pl[str(D)]["fall_dim"] > 0), None)
            recomputed.append(ff)
        pos[label]["d_ff_recomputed_from_per_layer"] = dict(
            collections.Counter(recomputed))
    # secondary direct arm from the sweeps
    for pk, d in data.items():
        draws = [x for x in d["raw"]["draws"] if x["arm"] == "secondary_direct_B8"]
        rec = []
        for x in draws:
            pl = x["per_layer"]
            ds = sorted(int(k) for k in pl)
            rec.append(next((D for D in ds if pl[str(D)]["fall_dim"] > 0), None))
        pos[f"secondary_B8@{pk}"] = {
            "n": len(draws),
            "B": sorted({x.get("B") for x in draws}),
            "d_ff_hist": dict(collections.Counter(x["d_ff"] for x in draws)),
            "d_ff_recomputed": dict(collections.Counter(rec)),
            "d_top_full_hist": dict(collections.Counter(x.get("d_top_full")
                                                        for x in draws)),
            "series_d_reg_hist": dict(collections.Counter(x.get("series_d_reg")
                                                          for x in draws)),
        }
    out["positive_control"] = pos

    # ---- 10. d_ff consistency with per_layer for the sweep arms ----------
    mismatch = []
    for pk, d in data.items():
        for x in d["raw"]["draws"]:
            pl = x["per_layer"]
            ds = sorted(int(k) for k in pl)
            ff = next((D for D in ds if pl[str(D)]["fall_dim"] > 0), None)
            if ff != x["d_ff"]:
                mismatch.append([pk] + list(key(x)) + [ff, x["d_ff"]])
    out["d_ff_recomputation_mismatches"] = mismatch

    json.dump(out, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()
