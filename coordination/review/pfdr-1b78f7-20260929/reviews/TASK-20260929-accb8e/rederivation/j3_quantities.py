"""J3 blind re-derivation, Q2-Q5, Q7, Q8 and gates G4-G7, from the text of
specification.yaml v1 + AMD-20260929-1de84f + AMD-20260929-430f44 applied to my own
J2a canonical sets (R11, R12, R14, R16) and the frozen R10 root rows.
Conventions: rederivation/conventions.yaml (CV-1 .. CV-15).

stats.py is loaded by file path (RV-3/RV-7). No engine module is imported.
TW-FLOOR (Q8) is evaluated in memory; only the boolean, count and keys leave this
process (RV-4)."""
import collections, gzip, importlib.util, json, math, os, random, statistics, sys
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (RUNS, RUN, WT, OUT, MAIN_BITS, J0_BITS, MAIN_ARMS, J0_ARMS, MODES,
                    STRUCT, RAND, read_jsonl_gz, read_json, row_m, is_rho, dump, rl)

MC_SEEDS = list(range(0, 21))  # seed 0 = the frozen/declared seed; 1..20 for Monte Carlo error


def load_stats():
    path = os.path.join(WT, "src", "crypto_autoresearcher", "index_calculus", "stats.py")
    rl.opened(path, "J3: frozen stats.py loaded by file path")
    spec = importlib.util.spec_from_file_location("stats_frozen_1b78f7", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_rows():
    rows = {}
    rows["R10"] = read_jsonl_gz(os.path.join(RUNS, RUN["R10"], "rows.jsonl.gz"), "J3 input: R10 root rows")
    for lab in ["R11", "R12", "R14", "R16"]:
        p = os.path.join(OUT, f"canonical-{lab}-rows.jsonl.gz")
        rl.opened(p, f"J3 input: my own J2a canonical {lab} rows")
        with gzip.open(p, "rt") as f:
            rows[lab] = [json.loads(l) for l in f if l.strip()]
    return rows


def index(rows):
    idx = {}
    for r in rows:
        if is_rho(r):
            continue
        k = (r.get("panel"), row_m(r), r["bits"], r["curve"], r.get("arm"), r.get("mode"))
        assert k not in idx, k
        idx[k] = r
    return idx


def h(r):
    return r.get("harvest") or {}


def count(r, cls, which="pairs_nonformal"):
    hb = h(r)
    if cls == "SS":
        return hb["SS"]["at_A_fix"][which]
    return hb[cls]["at_stop"][which]


def censored(r):
    return bool(h(r).get("SS", {}).get("at_A_fix", {}).get("censored"))


def cens_crosscheck(r):
    hb = h(r)
    a_fix = hb.get("attempt_budget_A_fix")
    if a_fix is None or r.get("attempts") is None:
        return None
    return (r["attempts"] < a_fix) == censored(r)


def status_ok(r):
    return r is not None and r.get("status") == "completed_valid"


def a1_cell(idx, panel, m, b, curves, A, R, cls, mode="census", size_check=True):
    """Returns dict with C_A, C_R, kappa, V, SD, z, resolved, raw kappa, used/dropped."""
    used, dropped = [], []
    nA, nR, nA_raw, nR_raw, log2N = {}, {}, {}, {}, {}
    for j in curves:
        rA = idx.get((panel, m, b, j, A, mode))
        rR = [idx.get((panel, m, b, j, a, mode)) for a in R]
        reasons = []
        for a, r in [(A, rA)] + list(zip(R, rR)):
            if not status_ok(r):
                reasons.append(f"failed:{a}:{None if r is None else r.get('status')}")
            elif censored(r):
                reasons.append(f"censored:{a}")
        if size_check:
            rsz = [r.get("fb_size") for r in rR if r is not None and r.get("fb_size") is not None]
            if rA is not None and rsz and rA.get("fb_size") is not None:
                if len(set(rsz)) > 1:
                    reasons.append("random_sizes_disagree")
                if rA["fb_size"] != rsz[0]:
                    reasons.append(f"unmatched_size:{rA['fb_size']}!={rsz[0]}")
        if rA is not None and rA.get("log2N") is not None:
            log2N[j] = rA["log2N"]
        if reasons:
            dropped.append({"curve": j, "reasons": reasons})
            continue
        used.append(j)
        nA[j] = count(rA, cls)
        nR[j] = [count(r, cls) for r in rR]
        nA_raw[j] = count(rA, cls, "pairs_raw")
        nR_raw[j] = [count(r, cls, "pairs_raw") for r in rR]
    res = {"panel": panel, "m": m, "bits": b, "class": cls, "arm": A, "curves_used": used,
           "curves_dropped": dropped, "counts_A": [nA[j] for j in used],
           "counts_R": [nR[j] for j in used], "log2N_by_curve": log2N}
    res.update(stats_from(nA, nR, used))
    raw = stats_from(nA_raw, nR_raw, used)
    res["raw_kappa"] = raw["kappa"]
    res["raw_z"] = raw["z"]
    res["raw_C_A"] = raw["C_A"]
    res["raw_C_R"] = raw["C_R"]
    return res


def stats_from(nA, nR, used):
    C_A = sum(nA[j] for j in used)
    C_R = Fraction(sum(sum(nR[j]) for j in used), 3)
    s2 = Fraction(0)
    for j in used:
        xs = nR[j]
        mu = Fraction(sum(xs), 3)
        s2 += sum((Fraction(x) - mu) ** 2 for x in xs) / 2
    V = max(s2, C_R)
    out = {"C_A": C_A, "C_R": float(C_R), "C_R_exact": f"{C_R.numerator}/{C_R.denominator}",
           "sum_s2": float(s2), "V": float(V)}
    if C_R > 0:
        out["kappa"] = float(Fraction(C_A) / C_R)
    else:
        out["kappa"] = None
    if V > 0:
        sd = math.sqrt(float(V) * 4 / 3)
        out["SD_null"] = sd
        out["z"] = float(Fraction(C_A) - C_R) / sd
    else:
        out["SD_null"] = None
        out["z"] = None
    out["resolved"] = bool(C_R >= 10)
    return out


def y_of(C_A, C_R, V):
    if C_R <= 0:
        return None
    kappa = C_A / C_R
    sd = math.sqrt(V * 4 / 3)
    val = max(kappa - 1, sd / C_R)
    if val <= 0:
        return None
    return math.log2(val)


def ols(xs, ys):
    if len(xs) < 2 or len(set(xs)) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def q_lo_hi(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return None, None
    return s[int(math.floor(0.025 * (n - 1)))], s[int(math.ceil(0.975 * (n - 1)))]


def a2_test(cells_by_rung, xb_mode="all", seed=0, reps=2000):
    """cells_by_rung: {bits: cell dict} for rungs 20..32 of one (A, c, m)."""
    rungs = sorted(b for b, c in cells_by_rung.items() if b >= 20 and c["resolved"])
    if len(rungs) < 4:
        return {"resolved_rungs": rungs, "status": "UNRESOLVED", "p_one_sided": 1.0,
                "slope": None, "lo": None, "hi": None}
    xs, ys = [], []
    data = []
    for b in rungs:
        c = cells_by_rung[b]
        if xb_mode == "all":
            vals = list(c["log2N_by_curve"].values())
        else:
            vals = [c["log2N_by_curve"][j] for j in c["curves_used"]]
        xb = sum(vals) / len(vals)
        xs.append(xb)
        ys.append(y_of(c["C_A"], c["C_R"], c["V"]))
        data.append((c["counts_A"], c["counts_R"]))
    slope = ols(xs, ys)
    rng = random.Random(seed)
    boots, undefined = [], 0
    for _ in range(reps):
        yb = []
        ok = True
        for (cA, cR), x in zip(data, xs):
            n = len(cA)
            members = list(range(n))
            idx = [rng.choice(members) for _ in members]
            CA = sum(cA[i] for i in idx)
            tot = sum(sum(cR[i]) for i in idx)
            CR = tot / 3
            s2 = 0.0
            for i in idx:
                a, b_, c_ = cR[i]
                mu = (a + b_ + c_) / 3
                s2 += ((a - mu) ** 2 + (b_ - mu) ** 2 + (c_ - mu) ** 2) / 2
            V = max(s2, CR)
            y = y_of(CA, CR, V)
            if y is None:
                ok = False
                break
            yb.append(y)
        if not ok:
            undefined += 1
            continue
        boots.append(ols(xs, yb))
    lo, hi = q_lo_hi(boots)
    p = (1 + sum(1 for s in boots if s <= 0)) / 2001
    return {"resolved_rungs": rungs, "status": "resolved", "x_b": xs, "y_b": ys, "slope": slope,
            "lo": lo, "hi": hi, "p_one_sided": p, "replicates_used": len(boots),
            "replicates_undefined": undefined}


def holm(pvals):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    n = len(items)
    adj, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        v = min(1.0, (n - i) * p)
        running = max(running, v)
        adj[k] = running
    return adj


def phi(z):
    return 0.5 * math.erfc(-z / math.sqrt(2))


def main():
    stats = load_stats()
    rows = load_rows()
    idx_main = {}
    for lab in ["R10", "R11", "R12"]:
        for k, r in index(rows[lab]).items():
            assert k not in idx_main
            idx_main[k] = r
    idx_j0 = index(rows["R14"])
    idx_r16 = index(rows["R16"])
    result = {}

    # ---------------- gates G4-G7 from rows (all harvest instances) -------------
    gates = {"G4_fail": [], "G5_fail": [], "G6_fail": [], "G7_fail": [], "G5_recomputed_fail": [],
             "checks_keys_seen": collections.Counter(), "instances": 0, "cens_crosscheck_disagree": []}
    all_solver = []
    for lab in ["R10", "R11", "R12", "R14", "R16"]:
        for r in rows[lab]:
            if is_rho(r):
                continue
            all_solver.append((lab, r))
    for lab, r in all_solver:
        key = [lab, r.get("panel"), row_m(r), r["bits"], r["curve"], r.get("arm"), r.get("mode")]
        if r.get("status") != "completed_valid":
            continue
        hb = h(r)
        gates["instances"] += 1
        for cls in ["TT", "TB", "SS"]:
            st = hb[cls]["at_stop"]
            if st["cert_fail"] != 0 or st["cert_pass"] != st["rows_emitted"]:
                gates["G4_fail"].append(key + [cls])
        if r.get("k_found") and not r.get("k_verified"):
            gates["G4_fail"].append(key + ["k_not_verified"])
        if r.get("arm") != "known_log" and not r.get("k_found"):
            gates["G4_fail"].append(key + ["main_arm_without_k"])
        ss = hb["ss_store"]
        if not ss.get("identity_ok"):
            gates["G5_fail"].append(key)
        if ss["encodings_recorded"] != 2 * (r["s3_solves"] - r["table_s3_solves"]) - ss["degenerate_roots"] \
                or ss["search_s3_charged"] != r["s3_solves"] - r["table_s3_solves"] \
                or r.get("search_s3") != r["s3_solves"] - r["table_s3_solves"]:
            gates["G5_recomputed_fail"].append(key)
        ch = r.get("checks") or {}
        for ck, v in ch.items():
            gates["checks_keys_seen"][ck] += 1
            if ck.startswith("G6") and v is not True:
                gates["G6_fail"].append(key + [ck])
            if ck.startswith("G7") and v is not True:
                gates["G7_fail"].append(key + [ck])
        if r.get("panel") == "j0" and r.get("arm") == "j0_coset":
            if hb.get("formal_basis_rank") * 3 != 2 * r["fb_size"]:
                gates["G6_fail"].append(key + ["formal_rank!=2F/3"])
            if "G6_j0_lambda_on_P" not in ch:
                gates["G6_fail"].append(key + ["no_lambda_check_recorded"])
        if r.get("panel") == "j0" and "G6_j0_lambda_on_P" not in ch:
            gates["G6_fail"].append(key + ["no_lambda_check_recorded"])
        if r.get("arm") == "known_log":
            if hb.get("formal_basis_rank") != r["fb_size"] - 1:
                gates["G6_fail"].append(key + ["known_log_rank!=F-1"])
        if r.get("arm") in ("subgroup", "dickson", "j0_coset"):
            if not any(ck.startswith("G7") for ck in ch):
                gates["G7_fail"].append(key + ["no_G7_check_recorded"])
        cc = cens_crosscheck(r)
        if cc is False:
            gates["cens_crosscheck_disagree"].append(key)
    gates["checks_keys_seen"] = dict(gates["checks_keys_seen"])
    for g in ["G4", "G5", "G6", "G7"]:
        gates[f"{g}_pass"] = (len(gates[f"{g}_fail"]) == 0) and (g != "G5" or len(gates["G5_recomputed_fail"]) == 0)
    result["gates_G4_G7"] = gates

    # ---------------- Q2: A1 over every (m, rung, class, A) --------------------------
    cells = {}
    for m in [3, 4, 5]:
        for b in MAIN_BITS:
            for cls in ["TT", "TB", "SS"]:
                for A in STRUCT:
                    cells[(A, cls, m, b)] = a1_cell(idx_main, "main", m, b, range(5), A, RAND[A], cls)
    result["A1_cells"] = [cells[k] for k in sorted(cells, key=lambda k: (k[2], k[3], k[1], k[0]))]
    # sensitivity: censoring drop in SS only (CV-1 alternative), reported, not primary
    sens = {}
    for (A, cls, m, b), c in cells.items():
        if cls == "SS":
            continue
        has_cens_only = [d for d in c["curves_dropped"] if all(x.startswith("censored") for x in d["reasons"])]
        if has_cens_only:
            idx2 = idx_main
            used = []
            # recompute without the censoring drop for TT/TB
            alt = a1_cell_nocens(idx2, "main", m, b, range(5), A, RAND[A], cls)
            sens[f"{A}|{cls}|m{m}|b{b}"] = {"primary_z": c["z"], "alt_z": alt["z"],
                                           "primary_resolved": c["resolved"], "alt_resolved": alt["resolved"],
                                           "primary_used": c["curves_used"], "alt_used": alt["curves_used"]}
    result["A1_sensitivity_censoring_SS_only"] = sens

    # ---------------- Q3: excursions, A2, Holm, A3, tail, outcome -------------------
    exc = []
    resolved_family = []
    for (A, cls, m, b), c in cells.items():
        if cls in ("TT", "SS") and c["resolved"]:
            resolved_family.append((A, cls, m, b, c["z"]))
            if abs(c["z"]) > 3:
                exc.append({"arm": A, "class": cls, "m": m, "bits": b, "z": c["z"],
                            "sign": "+" if c["z"] > 0 else "-", "kappa": c["kappa"], "C_A": c["C_A"],
                            "C_R": c["C_R"]})
    exc.sort(key=lambda e: (e["m"], e["bits"], e["class"], e["arm"]))
    result["excursions"] = exc
    result["resolved_family_size"] = len(resolved_family)
    result["cells_total_TT_SS"] = sum(1 for k in cells if k[1] in ("TT", "SS"))
    # tail check
    zmax = max(resolved_family, key=lambda t: abs(t[4]))
    k = len(resolved_family)
    zo = abs(zmax[4])
    result["A2_tail_check"] = {"max_abs_z_cell": list(zmax[:4]), "z": zmax[4], "k": k,
                               "P_max_ge": 1 - (1 - 2 * (1 - phi(zo))) ** k}
    # largest / smallest resolved kappa
    rk = [(c["kappa"], key) for key, c in cells.items() if c["resolved"] and c["kappa"] is not None]
    kmax, kmin = max(rk), min(rk)
    result["tail_largest_kappa"] = {"cell": list(kmax[1]), "kappa": kmax[0],
                                    "counts_A": cells[kmax[1]]["counts_A"], "counts_R": cells[kmax[1]]["counts_R"],
                                    "curves_used": cells[kmax[1]]["curves_used"]}
    result["tail_smallest_kappa"] = {"cell": list(kmin[1]), "kappa": kmin[0],
                                     "counts_A": cells[kmin[1]]["counts_A"], "counts_R": cells[kmin[1]]["counts_R"],
                                     "curves_used": cells[kmin[1]]["curves_used"]}
    # A2
    a2 = {}
    for A in STRUCT:
        for cls in ["TT", "SS", "TB"]:
            for m in [3, 4, 5]:
                cb = {b: cells[(A, cls, m, b)] for b in MAIN_BITS}
                res = a2_test(cb, "all", seed=0)
                res_alt = a2_test(cb, "used", seed=0)
                res["xb_used_sensitivity"] = {k2: res_alt.get(k2) for k2 in ("slope", "lo", "hi", "p_one_sided")}
                # Monte Carlo error over seeds 1..20
                if res["status"] == "resolved":
                    los, his, ps = [], [], []
                    for s in MC_SEEDS[1:]:
                        rr = a2_test(cb, "all", seed=s)
                        los.append(rr["lo"]); his.append(rr["hi"]); ps.append(rr["p_one_sided"])
                    res["mc_sd"] = {"lo": statistics.stdev(los), "hi": statistics.stdev(his),
                                    "p": statistics.stdev(ps), "seeds": "1..20"}
                    res["mc_range"] = {"lo": [min(los), max(los)], "hi": [min(his), max(his)],
                                       "p": [min(ps), max(ps)]}
                a2[f"{A}|{cls}|m{m}"] = res
    fam = {k2: v["p_one_sided"] for k2, v in a2.items() if not k2.split("|")[1] == "TB"}
    assert len(fam) == 18
    adj = holm(fam)
    for k2 in fam:
        a2[k2]["holm_adjusted_p"] = adj[k2]
    result["A2"] = a2
    # A3 (census instances, main panel) and prediction (4)
    unmatched = unmatched_instances(idx_main)
    a3 = collections.defaultdict(list)
    a3_by_m = collections.defaultdict(list)
    h3 = collections.Counter()
    for k2, r in idx_main.items():
        panel, m, b, j, arm, mode = k2
        if mode != "census" or not status_ok(r) or (m, b, j, arm) in unmatched:
            continue
        for cls in ["TT", "TB", "SS"]:
            st = h(r)[cls]["at_stop"]
            n = st["rows_emitted"]
            if n >= 10:
                rho = st["informative_rank"] / min(n, h(r)["U"])
                a3[(arm, cls)].append(rho)
                a3_by_m[(arm, cls, m)].append(rho)
                ok = st["informative_rank"] >= min(n, h(r)["U"]) / 1.05
                h3[(arm, cls, "rank_ge_min_over_1.05", ok)] += 1
    pred4 = {}
    for (arm, cls), v in sorted(a3.items()):
        ent = {"qualifying": len(v), "median": statistics.median(v) if v else None,
               "min": min(v), "max": max(v)}
        if arm == "known_log":
            if cls in ("TT", "TB"):
                ent["all_le_0.05"] = all(x <= 0.05 for x in v)
            else:
                ent["note"] = "reported, not evaluated"
        else:
            ent["evaluated"] = len(v) >= 5
            ent["median_ge_0.95"] = (statistics.median(v) >= 0.95) if len(v) >= 5 else None
        pred4[f"{arm}|{cls}"] = ent
    result["A3_prediction4"] = pred4
    result["A3_median_by_arm_class_m"] = {f"{a}|{c}|m{m}": {"n": len(v), "median": statistics.median(v)}
                                          for (a, c, m), v in sorted(a3_by_m.items())}
    result["H3_rank_ratio_tally"] = {f"{a}|{c}|{t}|{ok}": n for (a, c, t, ok), n in sorted(h3.items())}
    # O-ALIVE
    alive = []
    for A in STRUCT:
        for cls in ["TT", "SS"]:
            for m in [3, 4, 5]:
                c30, c32 = cells[(A, cls, m, 30)], cells[(A, cls, m, 32)]
                t = a2[f"{A}|{cls}|m{m}"]
                med = result["A3_median_by_arm_class_m"].get(f"{A}|{cls}|m{m}", {}).get("median")
                cond = {"z30_gt3": bool(c30["resolved"] and c30["z"] is not None and c30["z"] > 3),
                        "z32_gt3": bool(c32["resolved"] and c32["z"] is not None and c32["z"] > 3),
                        "slope_lo_gt0": bool(t.get("lo") is not None and t["lo"] > 0),
                        "holm_lt_0.05": bool(t.get("holm_adjusted_p", 1) < 0.05),
                        "median_rho_ge_0.95": bool(med is not None and med >= 0.95)}
                alive.append({"arm": A, "class": cls, "m": m, "conditions": cond, "all": all(cond.values())})
    result["O_ALIVE_conditions"] = alive

    # ---------------- Q4 Stage R ----------------------------------------------------
    stage_r = []
    for e in exc:
        c = a1_cell(idx_r16, "main", e["m"], e["bits"], range(5, 10), e["arm"], RAND[e["arm"]], e["class"])
        rep = (c["z"] is not None and abs(c["z"]) > 3 and (c["z"] > 0) == (e["z"] > 0) and c["resolved"])
        stage_r.append({"cell": {k2: e[k2] for k2 in ("arm", "class", "m", "bits")}, "discovery_z": e["z"],
                        "stage_r": c, "replicated": rep})
    result["stage_r"] = stage_r
    layout = {(e["m"], e["bits"], e["arm"]) for e in exc}
    result["stage_r_layout_vs_my_excursions"] = sorted([list(x) for x in layout])

    # ---------------- Q7 PC-1, PC-2 ---------------------------------------------------
    pc1 = a1_cell_pooled(idx_main, "main", 3, [b for b in J0_BITS], range(5), "known_log", RAND["subgroup"], "TT",
                         size_check=True)
    kl_q = pred4.get("known_log|TT", {}), pred4.get("known_log|TB", {})
    kl_ok = bool(kl_q[0].get("all_le_0.05", True) and kl_q[1].get("all_le_0.05", True))
    pc1_pass = (pc1["raw_kappa"] is not None and pc1["raw_kappa"] >= 5 and kl_ok)
    result["PC1"] = {"cell": pc1, "raw_kappa_TT": pc1["raw_kappa"], "rho_TT_TB_le_0.05_all": kl_ok,
                     "known_log_qualifying": {"TT": kl_q[0].get("qualifying"), "TB": kl_q[1].get("qualifying")},
                     "pass": pc1_pass}
    pc2 = a1_cell_pooled(idx_j0, "j0", 3, J0_BITS, range(5), "j0_coset", ["j0_random_r0", "j0_random_r1", "j0_random_r2"],
                         "TB", size_check=True)
    g6rank = all(h(r)["formal_basis_rank"] * 3 == 2 * r["fb_size"] for k2, r in idx_j0.items() if k2[4] == "j0_coset")
    pc2_pass = (pc2["raw_kappa"] is not None and pc2["raw_kappa"] >= 5 and pc2["resolved"] and pc2["z"] is not None
                and abs(pc2["z"]) <= 3 and g6rank)
    result["PC2"] = {"cell": pc2, "kappa_TB_before": pc2["raw_kappa"], "z_nonformal": pc2["z"],
                     "resolved": pc2["resolved"], "G6_rank_2F_over_3_all_j0_coset": g6rank, "pass": pc2_pass}

    # ---------------- outcome id ------------------------------------------------------
    g47 = all(gates[f"{g}_pass"] for g in ["G4", "G5", "G6", "G7"])
    any_alive = any(a["all"] for a in alive)
    if not g47:
        oid = "O-INVALID (G4-G7)"
    elif not (pc1_pass and pc2_pass):
        oid = "O-NO-DYNAMIC-RANGE"
    elif any_alive:
        oid = "O-ALIVE"
    elif not exc:
        oid = "O-NULL"
    else:
        oid = "O-EXCURSION"
    result["R15_outcome_id"] = {"id": oid, "conditional_on": "G1, G2 and G3 passing (J1, after the seal)"}
    reps = [s for s in stage_r if s["replicated"]]
    if oid == "O-EXCURSION":
        result["final_structural_reading"] = ("O-NULL with the excursion list attached" if not reps
                                              else "REPLICATED ANOMALY (TW-ALIVE)")
    else:
        result["final_structural_reading"] = oid

    # ---------------- Q5 A4 -----------------------------------------------------------
    result["A4"] = a4(idx_main, unmatched, stats)

    # ---------------- Q8 TW-FLOOR (in memory; boolean, count, keys only) -------------
    result["TW_FLOOR"] = tw_floor(rows, unmatched)
    result["unmatched_size_instances"] = sorted([list(x) for x in unmatched])
    dump("j3-results.json", result)
    print("done; outcome", oid, "excursions", len(exc), "stage_r replicated", len(reps))


def a1_cell_nocens(idx, panel, m, b, curves, A, R, cls):
    """CV-1 sensitivity: A1 without the censoring drop (failed and unmatched still drop)."""
    used = []
    nA, nR = {}, {}
    for j in curves:
        rA = idx.get((panel, m, b, j, A, "census"))
        rR = [idx.get((panel, m, b, j, a, "census")) for a in R]
        bad = any(not status_ok(r) for r in [rA] + rR)
        rsz = [r.get("fb_size") for r in rR if r is not None]
        if not bad and rA.get("fb_size") != rsz[0]:
            bad = True
        if bad:
            continue
        used.append(j)
        nA[j] = count(rA, cls)
        nR[j] = [count(r, cls) for r in rR]
    out = stats_from(nA, nR, used)
    out["curves_used"] = used
    return out


def a1_cell_pooled(idx, panel, m, bits_list, curves, A, R, cls, size_check=True):
    """A1 formula with units = (rung, curve) pairs pooled over bits_list (A5)."""
    nA, nR, nA_raw, nR_raw = {}, {}, {}, {}
    used, dropped = [], []
    for b in bits_list:
        for j in curves:
            rA = idx.get((panel, m, b, j, A, "census"))
            rR = [idx.get((panel, m, b, j, a, "census")) for a in R]
            reasons = []
            for a, r in [(A, rA)] + list(zip(R, rR)):
                if not status_ok(r):
                    reasons.append(f"failed:{a}")
                elif censored(r):
                    reasons.append(f"censored:{a}")
            if size_check and rA is not None:
                rsz = [r.get("fb_size") for r in rR if r is not None]
                if rsz and rA.get("fb_size") != rsz[0]:
                    reasons.append("unmatched_size")
            u = (b, j)
            if reasons:
                dropped.append({"unit": list(u), "reasons": reasons})
                continue
            used.append(u)
            nA[u] = count(rA, cls)
            nR[u] = [count(r, cls) for r in rR]
            nA_raw[u] = count(rA, cls, "pairs_raw")
            nR_raw[u] = [count(r, cls, "pairs_raw") for r in rR]
    out = stats_from(nA, nR, used)
    raw = stats_from(nA_raw, nR_raw, used)
    out["raw_kappa"] = raw["kappa"]
    out["raw_C_A"] = raw["C_A"]
    out["raw_C_R"] = raw["C_R"]
    out["units_used"] = len(used)
    out["units_dropped"] = dropped
    return out


def unmatched_instances(idx_main):
    """C-4 unmatched_size instances (m, bits, curve, arm) on the main panel."""
    out = set()
    for m in [3, 4, 5]:
        for b in MAIN_BITS:
            for j in range(5):
                for A in STRUCT:
                    rA = idx_main.get(("main", m, b, j, A, "census"))
                    rR = [idx_main.get(("main", m, b, j, a, "census")) for a in RAND[A]]
                    rsz = [r.get("fb_size") for r in rR if r is not None and r.get("fb_size") is not None]
                    if rA is not None and rsz and rA.get("fb_size") is not None and rA["fb_size"] != rsz[0]:
                        out.add((m, b, j, A))
    return out


def a4(idx_main, unmatched, stats):
    bases = {"subgroup": ["subgroup"], "dickson": ["dickson"], "small_x": ["small_x"],
             "random_sub": ["random_sub_r0", "random_sub_r1", "random_sub_r2"],
             "random_dick": ["random_dick_r0", "random_dick_r1", "random_dick_r2"]}
    out = {"medians": {}, "fits": {}, "excluded": []}
    paired = collections.defaultdict(list)
    for m in [3, 4, 5]:
        for b in MAIN_BITS:
            for j in range(5):
                for base, arms in bases.items():
                    for arm in arms:
                        rc = idx_main.get(("main", m, b, j, arm, "census"))
                        ro = idx_main.get(("main", m, b, j, arm, "on"))
                        ok = all(r is not None and r.get("status") == "completed_valid" and r.get("k_found")
                                 and r.get("k_verified") for r in (rc, ro))
                        if (m, b, j, arm) in unmatched:
                            out["excluded"].append([m, b, j, arm, "unmatched_size"])
                            continue
                        if not ok:
                            out["excluded"].append([m, b, j, arm, "not both solved and verified"])
                            continue
                        paired[(m, base)].append({"bits": b, "curve": j, "arm": arm, "log2N": rc["log2N"],
                                                  "s3_census": rc["s3_solves"], "s3_on": ro["s3_solves"]})
    one_a = []
    for m in [3, 5]:
        for base in bases:
            for b in [24, 26, 28, 30, 32]:
                ratios = [p["s3_census"] / p["s3_on"] for p in paired[(m, base)] if p["bits"] == b]
                med = statistics.median(ratios) if ratios else None
                out["medians"][f"m{m}|{base}|b{b}"] = {"n": len(ratios), "median": med}
                one_a.append(med is not None and med >= 1.3)
    out["pred_1a"] = "met" if all(one_a) else "not met"
    out["pred_1a_count_ge_1.3"] = sum(one_a)
    one_b = []
    for m in [3, 4, 5]:
        for base in bases:
            ps = sorted(paired[(m, base)], key=lambda p: (p["bits"], p["curve"], p["arm"]))
            rc = [{"bits": p["bits"], "log2N": p["log2N"], "s3_solves": p["s3_census"]} for p in ps]
            ro = [{"bits": p["bits"], "log2N": p["log2N"], "s3_solves": p["s3_on"]} for p in ps]
            fc = stats.fit_exponent(rc, "s3_solves")
            fo = stats.fit_exponent(ro, "s3_solves")
            delta = fo["slope"] - fc["slope"]
            dci = paired_delta(ps, seed=0)
            ent = {"n": len(ps), "census": fc, "on": fo, "delta": delta, "delta_ci": dci,
                   "bits_range": [min(p["bits"] for p in ps), max(p["bits"] for p in ps)]}
            # Monte Carlo error over seeds 1..20
            los_c, his_c, los_o, his_o, dlo, dhi = [], [], [], [], [], []
            for s in MC_SEEDS[1:]:
                a = stats.fit_exponent(rc, "s3_solves", seed=s)
                b_ = stats.fit_exponent(ro, "s3_solves", seed=s)
                d = paired_delta(ps, seed=s)
                los_c.append(a["lo"]); his_c.append(a["hi"]); los_o.append(b_["lo"]); his_o.append(b_["hi"])
                dlo.append(d[0]); dhi.append(d[1])
            ent["mc_sd"] = {"census_lo": statistics.stdev(los_c), "census_hi": statistics.stdev(his_c),
                            "on_lo": statistics.stdev(los_o), "on_hi": statistics.stdev(his_o),
                            "delta_lo": statistics.stdev(dlo), "delta_hi": statistics.stdev(dhi), "seeds": "1..20"}
            out["fits"][f"m{m}|{base}"] = ent
            if m in (3, 5):
                one_b.append(abs(delta) <= 0.03)
    out["pred_1b"] = "met" if all(one_b) else "not met"
    out["pred_1b_count_within_0.03"] = sum(one_b)
    f2 = out["fits"]["m4|small_x"]["on"]
    out["pred_2"] = {"slope": f2["slope"], "lo": f2["lo"], "hi": f2["hi"],
                     "reading": ("falsified" if f2["lo"] > 0.66 else ("met" if f2["slope"] <= 0.66 else "not met"))}
    return out


def paired_delta(ps, seed=0, reps=2000):
    strata = collections.OrderedDict()
    for i, p in enumerate(ps):
        strata.setdefault(p["bits"], []).append(i)
    xs = [p["log2N"] for p in ps]
    yc = [math.log2(p["s3_census"]) for p in ps]
    yo = [math.log2(p["s3_on"]) for p in ps]
    rng = random.Random(seed)
    boots = []
    for _ in range(reps):
        idx = [rng.choice(members) for members in strata.values() for _ in members]
        xi = [xs[i] for i in idx]
        sc = ols(xi, [yc[i] for i in idx])
        so = ols(xi, [yo[i] for i in idx])
        if sc is not None and so is not None:
            boots.append(so - sc)
    return list(q_lo_hi(boots))


def tw_floor(rows, unmatched):
    """RV-4: evaluate in memory; return ONLY boolean, count and keys."""
    fired_keys, not_eval, evaluated = [], [], 0
    fired_r16, eval_r16 = [], 0
    for lab in ["R10", "R11", "R12", "R14", "R16"]:
        for r in rows[lab]:
            if is_rho(r) or r.get("status") != "completed_valid":
                continue
            m = row_m(r)
            if r.get("panel") == "main" and (m, r["bits"], r["curve"], r.get("arm")) in unmatched:
                continue
            hb = h(r)
            rr = r.get("relations") or 0
            if r.get("mode") == "on":
                fed = (hb.get("on") or {}).get("rows_fed") or {}
                rr = rr + fed.get("TT", 0) + fed.get("TB", 0) + fed.get("SS", 0)
            key = [r["bits"], r["curve"], m, r.get("arm"), r.get("mode")]
            if rr <= 0:
                not_eval.append([lab] + key)
                continue
            fires = r["s3_solves"] < 0.9 * 0.5 * math.sqrt(rr * r["N"])
            if lab == "R16":
                eval_r16 += 1
                if fires:
                    fired_r16.append(key)
            else:
                evaluated += 1
                if fires:
                    fired_keys.append([r.get("panel")] + key)
    return {"fired_R10_R14": bool(fired_keys), "count_R10_R14": len(fired_keys), "keys_R10_R14": fired_keys,
            "instances_evaluated_R10_R14": evaluated, "not_evaluable_r_zero": not_eval,
            "fired_R16": bool(fired_r16), "count_R16": len(fired_r16), "keys_R16": fired_r16,
            "instances_evaluated_R16": eval_r16}


if __name__ == "__main__":
    main()
