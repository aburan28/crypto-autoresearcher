#!/usr/bin/env python3
"""Reader costmodel (SHF-20261021-477d51), blind re-derivation over the six
ecbench sessions of research/ic_planner_validation_20261020 at crypto b4f056101.

Reads only records.jsonl, spec.json and analysis/band-*.json. Computes, per curve:
  * curve facts (p, a, b, r, #E, j-class, automorphisms_available/used per arm);
  * per arm: verified count, units, lower_bound flags, unpriced-counter names,
    phase names, phase-sum == total_gae, S == total_gae/sqrt(r), mean S;
  * per IC record: oracle_setup GAE vs N(N+1) (cold: charged on every record),
    factor_base GAE (should be 0: construction left to native counters);
  * the §5a band, re-priced from the records with the rule documented in
    crypto src/cryptanalysis/ecbench/band.rs (priced_gae(w) = G + w*U), compared
    to the committed band json;
  * paired, target-clustered bootstrap intervals (own implementation, seed fixed)
    of mean-S ratios at w = 0, 0.1, 1 for every alternative/plan and plan/rho;
  * plan-arm phase shares of S; mean trials, relations, lookups, guard probes
    per IC arm;
  * an exact 3-point fit G(N) = A N^2 + B/N + C over half/plan/double means at
    each weight and its optimum N* = (B/2A)^(1/3), as a cheap pointer to where
    the counted optimum sits relative to the planned N.
Read-only. argv[1] = campaign dir, argv[2] = output json path."""
import json, math, random, re, sys, pathlib, statistics

root = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])
CURVES = ["r24", "r26", "r28", "c24", "c28", "c30"]
WEIGHTS = [0.0, 0.1, 1.0]
B = 4000
SEED = 477051


def unpriced_counts(rec):
    out = {}
    for name in rec["cost"].get("unpriced", []):
        base = name[: -len("_uncharged")] if name.endswith("_uncharged") else name
        if name in rec.get("counters", {}):
            out[name] = rec["counters"][name]
            continue
        tot, found = 0, False
        for ph in rec["phases"]:
            nat = ph.get("native", {}) or {}
            v = nat.get(name, nat.get(base))
            if v is not None:
                tot += v
                found = True
        out[name] = tot if found else None
    return out


def priced_s(rec, w, r):
    u = unpriced_counts(rec)
    if any(v is None for v in u.values()) and w > 0:
        return None
    return (rec["cost"]["total_gae"] + w * sum(v for v in u.values() if v is not None)) / math.sqrt(r)


def cluster_ratio(pairs, nboot=B, seed=SEED):
    """pairs: list of (target, a, b). ratio = mean(b)/mean(a); clusters = targets."""
    by_t = {}
    for t, a, b in pairs:
        by_t.setdefault(t, []).append((a, b))
    targets = sorted(by_t)
    pt = sum(b for _, _, b in pairs) / sum(a for _, a, _ in pairs)
    rng = random.Random(seed)
    boots = []
    for _ in range(nboot):
        sa = sb = 0.0
        for _ in targets:
            for a, b in by_t[rng.choice(targets)]:
                sa += a
                sb += b
        boots.append(sb / sa)
    boots.sort()
    return pt, [boots[int(0.025 * nboot)], boots[int(0.975 * nboot) - 1]]


result = {}
for c in CURVES:
    sess = root / "sessions" / c
    spec = json.loads((sess / "spec.json").read_text())
    recs = [json.loads(l) for l in open(sess / "records.jsonl")]
    meas = [x for x in recs if not x["warmup"]]
    cs = meas[0]["workload"]["curve_spec"]
    cv = meas[0]["workload"]["curve"]
    p, a, b = cs.get("p"), cs.get("a"), cs.get("b")
    if p is None:  # prime_search: the record carries only the construction; p from the ICV1 id
        m = re.search(r"ICV1:fp-(\d+):", cv.get("icv1", ""))
        p = int(m.group(1)) if m else None
    r = cv["r"]
    E = cv["group_order"]
    if a is None:
        jclass = "unknown from record (a, b not recorded); ecbench automorphisms_available decides"
    else:
        jclass = "j0" if a == 0 else ("j1728" if b == 0 else "generic")
    arms = {}
    for x in meas:
        arms.setdefault(x["arm"], []).append(x)
    plan_N = int(next(A for A in spec["arms"] if A["name"] == "plan")["method"]["params"]["factor_base"].split("=")[1])
    info = {"p": p, "a": a, "b": b, "r": r, "group_order": E, "log2_r": math.log2(r), "j_class": jclass,
            "p_mod_3": p % 3 if p else None, "p_mod_4": p % 4 if p else None,
            "automorphisms_available": sorted({x["boundaries"]["automorphisms_available"] for x in meas}),
            "plan_N_in_spec": plan_N, "arms": {}}
    # per-arm checks
    for arm, xs in arms.items():
        s_ok = all(abs(x["cost"]["s"] - x["cost"]["total_gae"] / math.sqrt(r)) < 1e-9 * max(1, x["cost"]["s"]) for x in xs)
        sum_ok = all(abs(sum(ph["gae"] for ph in x["phases"]) - x["cost"]["total_gae"]) < 1e-6 for x in xs)
        d = {
            "n": len(xs), "verified": sum(x["outcome"]["status"] == "verified" for x in xs),
            "matches_planted": sum(bool(x["outcome"].get("matches_planted")) for x in xs),
            "units": sorted({x["cost"]["unit"] for x in xs}),
            "lower_bound": sorted({x["cost"]["lower_bound"] for x in xs}),
            "unpriced": sorted({u for x in xs for u in x["cost"].get("unpriced", [])}),
            "automorphisms_used": sorted({x["boundaries"].get("automorphisms_used") for x in xs}),
            "phases": sorted({ph["name"] for x in xs for ph in x["phases"]}),
            "s_equals_total_over_sqrt_r": s_ok, "phase_sum_equals_total": sum_ok,
            "mean_s_w": [statistics.mean(priced_s(x, w, r) for x in xs) for w in WEIGHTS],
            "calibration_pinned_units": sorted({u for x in xs for u in (x.get("detail") or {}).get("calibration_pinned_units", [])}),
            "mean_unpriced_counts": {k: statistics.mean(unpriced_counts(x).get(k) or 0 for x in xs) for k in sorted({u for x in xs for u in x["cost"].get("unpriced", [])})},
        }
        if arm != "rho-neg":
            N = int(xs[0]["method"]["params"]["factor_base"].split("=")[1])
            phase_g = {}
            for x in xs:
                for ph in x["phases"]:
                    phase_g.setdefault(ph["name"], []).append(ph["gae"])
            d["N"] = N
            d["oracle_setup_gae_equals_N(N+1)_every_record"] = all(
                next(ph["gae"] for ph in x["phases"] if ph["name"] == "oracle_setup") == N * (N + 1) for x in xs) if "rootfind" not in arm else None
            d["oracle_setup_gae_values"] = sorted({next(ph["gae"] for ph in x["phases"] if ph["name"] == "oracle_setup") for x in xs})
            d["factor_base_gae_values"] = sorted({next(ph["gae"] for ph in x["phases"] if ph["name"] == "factor_base") for x in xs})
            d["linear_algebra_gae_values"] = sorted({next(ph["gae"] for ph in x["phases"] if ph["name"] == "linear_algebra") for x in xs})
            tot = statistics.mean(x["cost"]["total_gae"] for x in xs)
            d["mean_total_gae"] = tot
            d["phase_share_of_total"] = {k: statistics.mean(v) / tot for k, v in phase_g.items()}
            d["mean_trials"] = statistics.mean(x["counters"].get("targets_tried", 0) for x in xs)
            d["mean_relations"] = statistics.mean(x["counters"].get("relations_found", 0) for x in xs)
            d["mean_relations_per_column"] = statistics.mean(x["counters"].get("relations_found", 0) / x["factor_base"]["columns"] for x in xs)
        info["arms"][arm] = d
    # committed band
    band = json.loads((root / "analysis" / f"band-{c}.json").read_text())
    band_rows = {row["arm"]: row["mean_s"] for row in band["rows"]}
    info["band_recomputed_vs_committed_max_abs_diff"] = max(
        abs(info["arms"][arm]["mean_s_w"][i] - band_rows[arm][i]) for arm in band_rows for i in range(3))
    # paired ratios
    def key(x):
        return (x["workload"]["target_index"], x["round"])
    idx = {arm: {key(x): x for x in xs} for arm, xs in arms.items()}
    ratios = {}
    for alt in ["half-base", "double-base", "rootfind", "full-rank", "random-targets", "plan-aa"]:
        ratios[f"{alt}/plan"] = {}
        for i, w in enumerate(WEIGHTS):
            pairs = [(k[0], priced_s(idx["plan"][k], w, r), priced_s(idx[alt][k], w, r)) for k in idx["plan"] if k in idx[alt]]
            pt, ci = cluster_ratio(pairs)
            ratios[f"{alt}/plan"][str(w)] = {"ratio": pt, "ci95": ci, "pairs": len(pairs)}
    ratios["plan/rho-neg"] = {}
    for i, w in enumerate(WEIGHTS):
        pairs = [(k[0], priced_s(idx["rho-neg"][k], w, r), priced_s(idx["plan"][k], w, r)) for k in idx["plan"] if k in idx["rho-neg"]]
        pt, ci = cluster_ratio(pairs)
        ratios["plan/rho-neg"][str(w)] = {"ratio": pt, "ci95": ci, "pairs": len(pairs)}
    info["paired_ratios"] = ratios
    # rho S against its theory value sqrt(pi/4)
    info["rho_mean_s_over_theory"] = info["arms"]["rho-neg"]["mean_s_w"][0] / math.sqrt(math.pi / 4)
    # 3-point fit of total GAE (priced at w) over N/2, N, 2N
    fits = {}
    for i, w in enumerate(WEIGHTS):
        Ns, Gs = [], []
        for arm in ["half-base", "plan", "double-base"]:
            Ns.append(info["arms"][arm]["N"])
            Gs.append(info["arms"][arm]["mean_s_w"][i] * math.sqrt(r))
        # solve [N^2, 1/N, 1] x = G
        M = [[n * n, 1.0 / n, 1.0] for n in Ns]
        # Cramer's rule
        def det3(m):
            return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
        D = det3(M)
        sol = []
        for col in range(3):
            Mc = [row[:] for row in M]
            for rr in range(3):
                Mc[rr][col] = Gs[rr]
            sol.append(det3(Mc) / D)
        A_, B_, C_ = sol
        nstar = (B_ / (2 * A_)) ** (1 / 3) if A_ > 0 and B_ > 0 else None
        fits[str(w)] = {"A": A_, "B": B_, "C": C_, "N_star": nstar, "N_star_over_plan": nstar / plan_N if nstar else None,
                        "S_at_N_star_over_S_plan": ((A_ * nstar ** 2 + B_ / nstar + C_) / Gs[1]) if nstar else None,
                        "predicted_S_kN_over_S_N": {str(k): (A_ * (k * plan_N) ** 2 + B_ / (k * plan_N) + C_) / Gs[1] for k in (1.125, 1.25, 1.5)}}
    info["three_point_fit"] = fits
    result[c] = info

json.dump(result, open(out_path, "w"), indent=1, default=float)
# compact console summary
for c, info in result.items():
    print(f"== {c} p={info['p']} a={info['a']} b={info['b']} j={info['j_class']} aut={info['automorphisms_available']} log2r={info['log2_r']:.3f} N={info['plan_N_in_spec']} band_diff={info['band_recomputed_vs_committed_max_abs_diff']:.2e} rhoS/theory={info['rho_mean_s_over_theory']:.3f}")
    for arm, d in info["arms"].items():
        print(f"   {arm:15s} n={d['n']} ver={d['verified']} planted={d['matches_planted']} lb={d['lower_bound']} aut_used={d['automorphisms_used']} S(w)={[round(v,3) for v in d['mean_s_w']]} s_ok={d['s_equals_total_over_sqrt_r']} sum_ok={d['phase_sum_equals_total']} phases={d['phases']}")
    for k, v in info["paired_ratios"].items():
        print(f"   {k:22s} " + "  ".join(f"w={w}: {v[w]['ratio']:.3f} [{v[w]['ci95'][0]:.3f},{v[w]['ci95'][1]:.3f}]" for w in v))
    for w, f in info["three_point_fit"].items():
        print(f"   fit w={w}: A={f['A']:.3f} B={f['B']:.4g} N*/N={f['N_star_over_plan']:.3f} S(N*)/S(N)={f['S_at_N_star_over_S_plan']:.3f} pred S(kN)/S(N)=" + str({k: round(v, 3) for k, v in f['predicted_S_kN_over_S_N'].items()}))
    pl = info["arms"]["plan"]
    print(f"   plan: N={pl['N']} setup==N(N+1): {pl['oracle_setup_gae_equals_N(N+1)_every_record']} fb_gae={pl['factor_base_gae_values']} la_gae={pl['linear_algebra_gae_values']} shares={ {k: round(v,3) for k,v in pl['phase_share_of_total'].items()} } trials={pl['mean_trials']:.0f} rel/col={pl['mean_relations_per_column']:.3f}")
    print(f"   plan unpriced means: { {k: round(v,1) for k,v in pl['mean_unpriced_counts'].items()} }; rho unpriced: { {k: round(v,1) for k,v in info['arms']['rho-neg']['mean_unpriced_counts'].items()} }")
    for arm in ('half-base','double-base','full-rank'):
        d = info['arms'][arm]
        print(f"   {arm}: N={d['N']} trials={d['mean_trials']:.0f} rel/col={d['mean_relations_per_column']:.3f} setup={d['oracle_setup_gae_values'][:2]}")
