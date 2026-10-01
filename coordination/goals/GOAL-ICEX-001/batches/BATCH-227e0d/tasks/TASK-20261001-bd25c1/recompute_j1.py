"""Independent J1 recomputation for RUN-ICEX-0ad4d8 (TASK-20261001-bd25c1).

Reads only the run package and the fixture file. Does not import the
producer's implementation. Charging per C-3 (AMD-20260926-ced670), statistic
per C-5, bootstrap reading per OQ-8 as stated in the protocol (resample the 6
fixture points). Certificates are re-verified with this file's own affine
short-Weierstrass arithmetic.
"""
import hashlib
import itertools
import json
import math
import random
import sys
from pathlib import Path

RUN = Path("experiments/EXP-ICEX-aaccfc/runs/RUN-ICEX-0ad4d8")
FIX = Path("experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json")
FIXTURES = ["b16-s21", "b16-s22", "b16-s23", "b20-s21", "b20-s22", "b20-s23"]
KINDS = ["primary", "null_randfb", "stage_cost_m6", "stage_cost_m8", "rho"]
out = {}


def cell(fid, kind):
    return json.load(open(RUN / "cells" / f"{fid}__{kind}" / "result.json"))


# ---------------------------------------------------------------- C-3 units
def units_of(c):
    return 13 * (c["pt_add"] + c["pt_dbl"]) + c["probes"] + c["mul"] + 10 * c["inv"] + c["la_mul"] + 10 * c["la_inv"]


def walk_costs(o, path, acc):
    if isinstance(o, dict):
        if {"pt_add", "pt_dbl", "probes", "mul", "inv", "la_mul", "la_inv", "units"} <= set(o):
            acc.append((path, units_of(o), o["units"]))
        for k, v in o.items():
            walk_costs(v, path + "/" + k, acc)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk_costs(v, path + f"[{i}]", acc)


unit_dicts, unit_mismatch = 0, []
for fid in FIXTURES:
    for kind in KINDS:
        acc = []
        walk_costs(cell(fid, kind), f"{fid}:{kind}", acc)
        unit_dicts += len(acc)
        unit_mismatch += [a for a in acc if a[1] != a[2]]
out["c3_unit_formula"] = {"cost_dicts_checked": unit_dicts, "mismatches": unit_mismatch[:10],
                          "n_mismatches": len(unit_mismatch)}


def attempt_units(log):
    pe = log["probes_each"]
    return sum(13 * k + pe for k in log["pt_ops"])


# ---------------------------------------------- per-fixture complete units
per = []
charging = []
for fid in FIXTURES:
    c = cell(fid, "primary")
    r = c["result"]
    s1 = r["stage1"]
    log = s1["attempt_log"]
    n_att = len(log["pt_ops"])
    att_u = attempt_units(log)
    s1_u = att_u + s1["cost"]["fb_construction"]["units"] + s1["cost"]["forward_table"]["units"]
    s3 = r["stage3"]
    la_from_log = sum(e["la_mul"] + 10 * e["la_inv"] for e in s3["la_log"])
    rk_from_log = sum(e["la_mul"] + 10 * e["la_inv"] for e in s3["rank_log"])
    s3_u = la_from_log + rk_from_log
    d_u, d_att, d_ok = 0, 0, 0
    for t in r["descents"]["targets"]:
        tu = attempt_units(t["attempt_log"])
        d_att += len(t["attempt_log"]["pt_ops"])
        d_ok += int(tu == t["units"] and t["attempts"] == len(t["attempt_log"]["pt_ops"]))
        d_u += tu
    total = s1_u + s3_u + d_u
    member_ones = log["member_bits"].count("1")
    charging.append({
        "fixture": fid,
        "stage1_attempts_logged": n_att, "n_attempts_reported": s1["n_attempts"],
        "n_failed_reported": s1["n_failed_attempts"], "member_bits_ones": member_ones,
        "n_relations": s1["n_relations"],
        "failed_attempts_charged": n_att - member_ones,
        "stage1_attempt_units_recomputed": att_u, "stage1_attempt_units_reported": s1["cost"]["attempts"]["units"],
        "stage1_units_recomputed": s1_u, "stage1_units_reported": s1["units"],
        "stage3_units_recomputed_from_la_log_plus_rank_log": s3_u, "stage3_units_reported": s3["units"],
        "la_cost_units_reported": s3["la_cost"]["units"], "la_from_log": la_from_log,
        "lanczos_tries": s3["la_info"]["lanczos_tries"],
        "descent_targets": len(r["descents"]["targets"]), "descent_attempts": d_att,
        "descent_target_units_consistent": d_ok,
        "descents_units_recomputed": d_u, "descents_units_reported": r["descents"]["units"],
        "complete_units_recomputed": total, "complete_units_reported": r["complete_units"],
        "match": total == r["complete_units"] and s1_u == s1["units"] and s3_u == s3["units"] and d_u == r["descents"]["units"],
    })
    per.append({"fid": fid, "bits": r["fixture"]["bits"], "q": r["fixture"]["N"], "total": total,
                "comp": {"stage1": s1_u, "stage3": s3_u, "descents": d_u}})
out["charging"] = charging


# ---------------------------------------------------------- C-5 statistic
def ols(xs, ys):
    n = len(xs)
    xm, ym = sum(xs) / n, sum(ys) / n
    den = sum((x - xm) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / den


def pct_linear(sorted_vals, p):
    # numpy 'linear' percentile definition, implemented by hand
    n = len(sorted_vals)
    h = (n - 1) * p / 100.0
    lo = math.floor(h)
    hi = min(lo + 1, n - 1)
    return sorted_vals[lo] + (h - lo) * (sorted_vals[hi] - sorted_vals[lo])


def exact_bootstrap(xs, ys):
    n = len(xs)
    sl, degen = [], 0
    for idx in itertools.product(range(n), repeat=n):
        s = ols([xs[i] for i in idx], [ys[i] for i in idx])
        if s is None:
            degen += 1
        else:
            sl.append(s)
    sl.sort()
    return {"enumerated": n ** n, "degenerate": degen, "ci95": [pct_linear(sl, 2.5), pct_linear(sl, 97.5)],
            "frac_slopes_below_0p5": sum(s < 0.5 for s in sl) / len(sl)}


def mc_bootstrap(xs, ys, seed, B=2000):
    rnd = random.Random(seed)
    n = len(xs)
    sl = []
    while len(sl) < B:
        idx = [rnd.randrange(n) for _ in range(n)]
        s = ols([xs[i] for i in idx], [ys[i] for i in idx])
        if s is not None:
            sl.append(s)
    sl.sort()
    return [pct_linear(sl, 2.5), pct_linear(sl, 97.5)]


def frozen_seed_bootstrap(xs, ys, label, B=2000):
    """Reproduce the frozen CI: numpy PCG64 seeded from SHA256(label) >> 192 (spec seed rule)."""
    import numpy as np
    seed = int(hashlib.sha256(label.encode("utf-8")).hexdigest(), 16) >> 192
    rng = np.random.Generator(np.random.PCG64(seed))
    n = len(xs)
    sl, red = [], 0
    while len(sl) < B:
        idx = rng.integers(0, n, n)
        s = ols([xs[i] for i in idx], [ys[i] for i in idx])
        if s is None:
            red += 1
            continue
        sl.append(s)
    sl.sort()
    return {"ci95": [pct_linear(sl, 2.5), pct_linear(sl, 97.5)], "degenerate_redraws": red}


def c5(xs, ys, b20_ratios, label=None):
    e = ols(xs, ys)
    ex = exact_bootstrap(xs, ys)
    res = {"exponent": e, "exact_bootstrap": ex,
           "mc_bootstrap_independent_seeds": {s: mc_bootstrap(xs, ys, s) for s in (1, 2, 3)}}
    lo, hi = ex["ci95"]
    if label:
        fz = frozen_seed_bootstrap(xs, ys, label)
        res["frozen_seed_bootstrap"] = fz
        lo, hi = fz["ci95"]
    res["verdict_from_ci_used"] = ("sub_rho_signal" if hi < 0.5 and all(r < 1 for r in b20_ratios)
                                   else "scoped_negative" if lo >= 0.5 else "inconclusive")
    res["verdict_exact_ci"] = ("sub_rho_signal" if ex["ci95"][1] < 0.5 and all(r < 1 for r in b20_ratios)
                               else "scoped_negative" if ex["ci95"][0] >= 0.5 else "inconclusive")
    return res


ref = lambda q: 13 * 0.886 * math.sqrt(q)
xs = [math.log(p["q"]) for p in per]
ys = [math.log(p["total"]) for p in per]
b20 = [p for p in per if p["bits"] == 20]
pooled = {s: sum(p["comp"][s] for p in b20) for s in ("stage1", "stage3", "descents")}
primary = c5(xs, ys, [p["total"] / ref(p["q"]) for p in b20], label="EXP-ICEX-aaccfc/v2|bootstrap")
primary["ratios"] = {p["fid"]: p["total"] / ref(p["q"]) for p in per}
primary["pooled_units_20bit"] = pooled
primary["dominant_stage_20bit"] = max(pooled, key=pooled.get)
primary["dominant_share_20bit"] = pooled[primary["dominant_stage_20bit"]] / sum(pooled.values())
primary["per_fixture_dominant"] = {p["fid"]: max(p["comp"], key=p["comp"].get) for p in per}
keep = [i for i, p in enumerate(per) if p["fid"] != "b16-s21"]
lo_xs, lo_ys = [xs[i] for i in keep], [ys[i] for i in keep]
loo = {"exponent": ols(lo_xs, lo_ys),
       "frozen_seed_bootstrap": frozen_seed_bootstrap(lo_xs, lo_ys, "EXP-ICEX-aaccfc/v2|bootstrap|leave_out|b16-s21"),
       "exact_bootstrap": exact_bootstrap(lo_xs, lo_ys)}
primary["leave_out_b16_s21_nonverdict"] = loo

# diff vs metrics.json
m = json.load(open(RUN / "metrics.json"))
mf = {p["fixture_id"]: p for p in m["per_fixture"]}
diff = {
    "exponent_abs_diff": abs(primary["exponent"] - m["exponent"]),
    "ci_frozen_seed_abs_diff": [abs(a - b) for a, b in zip(primary["frozen_seed_bootstrap"]["ci95"], m["exponent_bootstrap"]["ci95"])],
    "ci_exact_vs_metrics": [primary["exact_bootstrap"]["ci95"], m["exponent_bootstrap"]["ci95"]],
    "complete_units_match_all": all(mf[p["fid"]]["complete_units"] == p["total"] for p in per),
    "components_match_all": all(mf[p["fid"]]["components"] == p["comp"] for p in per),
    "ratio_max_rel_diff": max(abs(mf[p["fid"]]["ratio"] - p["total"] / ref(p["q"])) / mf[p["fid"]]["ratio"] for p in per),
    "pooled_match": m["pooled_units_20bit"] == pooled,
    "dominant_metrics": [m["dominant_stage_20bit"], m["dominant_stage_20bit_diagnostic"]],
    "verdict_metrics": m["verdict"],
    "loo_exponent_abs_diff": abs(loo["exponent"] - m["exponent_leave_out_b16_s21_nonverdict"]["exponent"]),
    "loo_ci_abs_diff": [abs(a - b) for a, b in zip(loo["frozen_seed_bootstrap"]["ci95"], m["exponent_leave_out_b16_s21_nonverdict"]["exponent_bootstrap"]["ci95"])],
    "loo_redraws": [loo["frozen_seed_bootstrap"]["degenerate_redraws"], m["exponent_leave_out_b16_s21_nonverdict"]["exponent_bootstrap"]["degenerate_redraws"]],
}
primary["diff_vs_metrics"] = diff
out["c5_primary"] = primary


# -------------------------------------------------------- EC arithmetic
class EC:
    def __init__(s, p, a, b):
        s.p, s.a, s.b = p, a, b

    def on(s, P):
        return P is None or (P[1] * P[1] - (P[0] ** 3 + s.a * P[0] + s.b)) % s.p == 0

    def neg(s, P):
        return None if P is None else (P[0], (-P[1]) % s.p)

    def add(s, P, Q):
        p = s.p
        if P is None:
            return Q
        if Q is None:
            return P
        if P[0] == Q[0] and (P[1] + Q[1]) % p == 0:
            return None
        if P == Q:
            l = (3 * P[0] * P[0] + s.a) * pow(2 * P[1], -1, p) % p
        else:
            l = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
        x = (l * l - P[0] - Q[0]) % p
        return (x, (l * (P[0] - x) - P[1]) % p)

    def mul(s, k, P):
        R, A = None, P
        while k:
            if k & 1:
                R = s.add(R, A)
            A = s.add(A, A)
            k >>= 1
        return R


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


# fixtures vs fixture file; curve sanity
fx_file = {(f["bits"], f["seed"]): f for f in json.load(open(FIX))["EXP-ICEX-aaccfc"]}
fx_checks = []
for fid in FIXTURES:
    f = cell(fid, "primary")["result"]["fixture"]
    ff = fx_file[(f["bits"], f["seed"])]
    E = EC(f["p"], f["a"], f["b"])
    G = tuple(f["G"])
    fx_checks.append({"fixture": fid, "equals_fixture_file": f == ff,
                      "p_prime": is_prime(f["p"]), "N_prime": is_prime(f["N"]),
                      "nonsingular": (4 * f["a"] ** 3 + 27 * f["b"] ** 2) % f["p"] != 0,
                      "G_on_curve": E.on(G), "NG_is_O": E.mul(f["N"], G) is None,
                      "N_gt_sqrt_p": f["N"] > math.isqrt(f["p"])})
out["fixtures"] = fx_checks

# --------------------------------------------------- certificate sample
pool_rel, pool_desc, pool_logs = [], [], []
for fid in FIXTURES:
    for kind in ("primary", "null_randfb"):
        r = cell(fid, kind)["result"]
        for i in range(len(r["stage1"]["relations"])):
            pool_rel.append((fid, kind, i))
    r = cell(fid, "primary")["result"]
    for i in range(len(r["descents"]["targets"])):
        pool_desc.append((fid, i))
rnd = random.Random("TASK-20261001-bd25c1|cert-sample")
rel_sample = rnd.sample(pool_rel, 30)
desc_sample = rnd.sample(pool_desc, 24)


rel_results = []
for fid, kind, i in rel_sample:
    r = cell(fid, kind)["result"]
    f = r["fixture"]
    E, G, N = EC(f["p"], f["a"], f["b"]), tuple(f["G"]), f["N"]
    Q = tuple(r["target"]["Q"]) if "target" in r else None
    if Q is None:
        # null cells share the primary fixture's target
        Q = tuple(cell(fid, "primary")["result"]["target"]["Q"])
    k = cell(fid, "primary")["result"]["target"]["k"]
    rel = r["stage1"]["relations"][i]
    V = r["factor_base"]["V"]
    R = tuple(rel["R"])
    ok_R = E.on(R) and E.add(E.mul(rel["a"], G), E.mul(rel["b"], Q)) == R
    # sum of +-P(x) over terms equals R for SOME consistent y-orientation per x-class:
    # check by lifting each x with both roots and testing all sign patterns of distinct classes
    xs_used = sorted(set(V[t[0]] for t in rel["terms"]))
    # sqrt by Tonelli-Shanks
    def sqrt_mod(n, p):
        n %= p
        if n == 0:
            return 0
        if pow(n, (p - 1) // 2, p) != 1:
            return None
        if p % 4 == 3:
            return pow(n, (p + 1) // 4, p)
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2; s += 1
        z = 2
        while pow(z, (p - 1) // 2, p) != p - 1:
            z += 1
        mm, c, t, rr = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
        while t != 1:
            i2, t2 = 0, t
            while t2 != 1:
                t2 = t2 * t2 % p; i2 += 1
            b_ = pow(c, 1 << (mm - i2 - 1), p)
            mm, c, t, rr = i2, b_ * b_ % p, t * b_ * b_ % p, rr * b_ % p
        return rr
    lifted = {}
    for x in xs_used:
        y = sqrt_mod(x ** 3 + f["a"] * x + f["b"], f["p"])
        lifted[x] = (x, y) if y is not None else None
    found_orient = False
    if all(lifted[x] is not None for x in xs_used):
        for signs in itertools.product((1, -1), repeat=len(xs_used)):
            orient = {x: (lifted[x] if s == 1 else E.neg(lifted[x])) for x, s in zip(xs_used, signs)}
            S = None
            for idx, e in rel["terms"]:
                P = orient[V[idx]]
                S = E.add(S, P if e == 1 else E.neg(P))
            if S == R:
                found_orient = True
                break
    # x(P) < B for every term
    if r["factor_base"]["kind"] == "random_x":
        in_fb = all(0 <= t[0] < len(V) for t in rel["terms"]) and len(set(V)) == r["factor_base"]["L"]
    else:
        in_fb = all(V[t[0]] < r["factor_base"]["B"] for t in rel["terms"])
    rel_results.append({"fixture": fid, "kind": kind, "rel_index": i, "j": rel["j"],
                        "R_eq_aG_plus_bQ": ok_R, "sum_terms_eq_R_some_orientation": found_orient,
                        "m_terms": len(rel["terms"]), "terms_in_factor_base_x_rule": in_fb})

desc_results = []
for fid, i in desc_sample:
    r = cell(fid, "primary")["result"]
    f = r["fixture"]
    E, G, N = EC(f["p"], f["a"], f["b"]), tuple(f["G"]), f["N"]
    t = r["descents"]["targets"][i]
    Qt = tuple(t["Q_t"])
    logs = r["stage3"]["logs"]
    V = r["factor_base"]["V"]
    # recovered log certificate: k_t * G == Q_t (direct group arithmetic)
    kt_ok = E.mul(t["k_t"] % N, G) == Qt
    khat_ok = t["k_hat"] == t["k_t"]
    # descent identity: Q_t + r G == sum terms, where factor-base point i := logs[col(i)] * G
    desc_results.append({"fixture": fid, "t": t["t"], "attempts": t["attempts"],
                         "kt_G_eq_Qt": kt_ok, "k_hat_eq_k_t": khat_ok, "verified_flag": t["verified"]})

# all logs and target k on every primary cell (complete, not sampled)
log_checks = []
for fid in FIXTURES:
    r = cell(fid, "primary")["result"]
    f = r["fixture"]
    E, G, N = EC(f["p"], f["a"], f["b"]), tuple(f["G"]), f["N"]
    k, Q = r["target"]["k"], tuple(r["target"]["Q"])
    V = r["factor_base"]["V"]
    logs = r["stage3"]["logs"]
    # every factor-base x-class: some log in `logs` maps G to a point with that x
    pts = {}
    for lg in logs:
        P = E.mul(lg % N, G)
        if P is not None:
            pts.setdefault(P[0], []).append(lg)
    fb_cover = all(x in pts for x in V)
    log_checks.append({"fixture": fid, "kG_eq_Q": E.mul(k, G) == Q, "k_recovered_eq_k": r["stage3"]["k_recovered"] == k,
                       "n_logs": len(logs), "L": len(V), "every_fb_x_class_has_log_mapping_to_it": fb_cover,
                       "last_log_eq_k": logs[-1] == k})

# relation-as-log-identity check on sampled primary relations: a + b k == sum e * log(P) mod N
rel_log_ident = []
for fid, kind, i in rel_sample:
    if kind != "primary":
        continue
    r = cell(fid, kind)["result"]
    f = r["fixture"]
    E, G, N = EC(f["p"], f["a"], f["b"]), tuple(f["G"]), f["N"]
    V = r["factor_base"]["V"]
    logs = r["stage3"]["logs"]
    k = r["target"]["k"]
    rel = r["stage1"]["relations"][i]
    # log of the oriented point +P(x) for each x: from the log list, pick the one mapping G to point with that x;
    # orientation: whichever of +/- matches the relation's point identity
    lg_by_x = {}
    for lg in logs:
        P = E.mul(lg % N, G)
        if P is not None and P[0] in V:
            lg_by_x[P[0]] = (lg, P)
    xs_used = sorted(set(V[t[0]] for t in rel["terms"]))
    ok = False
    if all(x in lg_by_x for x in xs_used):
        for signs in itertools.product((1, -1), repeat=len(xs_used)):
            o = {x: s for x, s in zip(xs_used, signs)}
            tot = sum(e * o[V[idx]] * lg_by_x[V[idx]][0] for idx, e in rel["terms"]) % N
            if tot == (rel["a"] + rel["b"] * k) % N:
                ok = True
                break
    rel_log_ident.append({"fixture": fid, "rel_index": i, "log_identity_holds": ok})

out["certificates"] = {
    "sample_rule": "random.Random('TASK-20261001-bd25c1|cert-sample'); 30 relations from primary+null_randfb, 24 descents from primary",
    "relations_pool": len(pool_rel), "descents_pool": len(pool_desc),
    "relations": rel_results, "descents": desc_results,
    "relation_log_identities": rel_log_ident, "all_primary_logs": log_checks,
    "relations_pass": sum(x["R_eq_aG_plus_bQ"] and x["sum_terms_eq_R_some_orientation"] for x in rel_results),
    "descents_pass": sum(x["kt_G_eq_Qt"] and x["k_hat_eq_k_t"] for x in desc_results),
    "log_identities_pass": sum(x["log_identity_holds"] for x in rel_log_ident),
}

# -------------------------------------------- held-out alpha2 gate
a2 = []
for fid in FIXTURES:
    s2 = cell(fid, "primary")["result"]["stage2_alpha2"]
    a2.append({"fixture": fid, "L": s2["L"], "n_heldout": s2["n_heldout"], "mean_units": s2["mean_units"],
               "agree": s2["agreement_with_brute_force"], "units_eq_28L": s2["mean_units"] == 28 * s2["L"],
               "per_point_n": len(s2["per_point"])})
ax = [math.log(x["L"]) for x in a2]
ay = [math.log(x["mean_units"]) for x in a2]
out["alpha2"] = {"per_fixture": a2, "alpha2_recomputed": ols(ax, ay), "alpha2_metrics": m["alpha2"]}

# -------------------------------------------- matched rho (proves-too-much object 2)
rho = []
for fid in FIXTURES:
    r = cell(fid, "rho")["result"]
    tg = r["targets"]
    rho.append({"fixture": fid, "q": r["fixture"]["N"], "n_solved": r["n_solved"],
                "mean_units": sum(t["units"] for t in tg) / len(tg),
                "mean_walk_units": sum(t["walk_units"] for t in tg) / len(tg),
                "all_k_true_matches": all(t["k_true_matches"] for t in tg)})
rx = [math.log(x["q"]) for x in rho]
out["rho"] = {"per_fixture": rho,
              "exponent_walk_units": ols(rx, [math.log(x["mean_walk_units"]) for x in rho]),
              "exponent_walk_ci_exact": exact_bootstrap(rx, [math.log(x["mean_walk_units"]) for x in rho])["ci95"],
              "exponent_mean_units_incl_precompute": ols(rx, [math.log(x["mean_units"]) for x in rho]),
              "exponent_mean_units_ci_exact": exact_bootstrap(rx, [math.log(x["mean_units"]) for x in rho])["ci95"],
              "exponent_reference": 0.5,
              "frozen_ci_code_on_walk": None}

json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({"c3": out["c3_unit_formula"]["n_mismatches"], "charging_all_match": all(c["match"] for c in charging),
                  "exp": primary["exponent"], "ci_frozen_seed": primary["frozen_seed_bootstrap"]["ci95"],
                  "ci_exact": primary["exact_bootstrap"]["ci95"], "dominant": primary["dominant_stage_20bit"],
                  "verdict": primary["verdict_from_ci_used"], "diff": diff,
                  "fixtures_ok": all(all(v for k, v in x.items() if k != "fixture") for x in fx_checks),
                  "rel_pass": out["certificates"]["relations_pass"], "desc_pass": out["certificates"]["descents_pass"],
                  "logid": [out["certificates"]["log_identities_pass"], len(rel_log_ident)],
                  "logs": log_checks, "alpha2": out["alpha2"]["alpha2_recomputed"],
                  "rho": {k: v for k, v in out["rho"].items() if k != "per_fixture"}}, indent=1, default=str))
