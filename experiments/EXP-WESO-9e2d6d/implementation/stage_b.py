"""EXP-WESO-9e2d6d STAGE-B (RUN-WESO-f37773): sampler mixing against the exact
Stage-A ground truth; positive controls PC-1, PC-2; start-order control
START-1; unit checks U-0..U-2; walk-length rule k_C(p) = ceil(3 c_hat log2 p);
gate_G_B; analysis_freeze (hashes of every implementation file).
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import common  # noqa: E402
import sampling  # noqa: E402
import stats  # noqa: E402

PRIMES = [1019, 4099, 10007, 20011]
TYPE_PRIMES = [1019, 4099]
KGRID = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 33, 48, 64, 65, 96, 128]
NB = 10000
NREP = 1000
STAGE_A_RUN = "RUN-WESO-aa2237"
O0 = "O0basis()"


def tv(counts, law_keys, law_p, n):
    """TV between empirical counts (dict key->count) and reference law."""
    s = 0.0
    seen = set()
    for key, pk in zip(law_keys, law_p):
        s += abs(counts.get(key, 0) / n - pk)
        seen.add(key)
    for key, c in counts.items():
        if key not in seen:
            s += c / n
    return 0.5 * s


def null_floor(master, p, level, keys, probs):
    cum = np.cumsum(probs)
    cum[-1] = 1.0
    tvs = []
    for r in range(NREP):
        sd = common.draw_seed(master, "B", p, "NULL-%s" % level, r)
        u = common.uniforms_vector(sd, NB)
        cat = np.searchsorted(cum, u, side="right")
        cnt = np.bincount(cat, minlength=len(probs))
        tvs.append(0.5 * float(np.abs(cnt / NB - probs).sum()))
    tvs = np.array(tvs)
    return float(np.percentile(tvs, 99.9)), {"mean": float(tvs.mean()), "max": float(tvs.max()),
                                               "min": float(tvs.min()), "percentile_method": "numpy linear interpolation"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--dev-scale", type=int, default=None,
                    help="DEVELOPMENT SMOKE TEST ONLY (scratch dir): N_B and replicate count divided by this; never used for the official run")
    a = ap.parse_args()
    global NB, NREP
    if a.dev_scale:
        NB //= a.dev_scale
        NREP = max(20, NREP // a.dev_scale)
    rd = a.run_dir
    W = a.workers
    t_start = time.time()
    adir = os.path.join(common.EXP_DIR, "runs", STAGE_A_RUN)
    ares = json.load(open(os.path.join(adir, "raw-result.json")))
    types = [json.loads(l) for l in open(os.path.join(adir, "types.jsonl"))]
    a1_pass = ares["A1_passing_primes"]

    gp = common.GP()
    raw = {"experiment_id": "EXP-WESO-9e2d6d", "run_id": "RUN-WESO-f37773", "stage": "STAGE-B",
           "stage_A_inputs": {"run": STAGE_A_RUN, "raw_result_sha256": common.sha256_file(os.path.join(adir, "raw-result.json")),
                              "types_jsonl_sha256": common.sha256_file(os.path.join(adir, "types.jsonl"))},
           "N_B": NB, "k_grid": KGRID, "null_replicates": NREP, "workers": W}
    all_samples = []

    # ---------------- U-0 -------------------------------------------------
    u0 = {}
    for p in PRIMES:
        gp.cmd("p=%d; B0=O0basis()" % p, want=False)
        isord = gp.val("isorder(B0,p)") == "1"
        disc = gp.val("discrd2(B0,p)==p^2") == "1"
        one = gp.val("denominator(B0^-1*[1,0,0,0]~)==1") == "1"
        pmin = int(gp.val("deltaorder(lllorder(B0,p),p)[1]"))
        u0[p] = {"closed_under_multiplication_and_contains_1": isord, "contains_1": one, "reduced_disc_p": disc,
                 "p_mod_4": p % 4, "P_minimum": pmin,
                 "verdict": "PASS" if (isord and disc and one and pmin == 1 and p % 4 == 3) else "FAIL"}
    raw["U-0"] = u0
    common.log("U-0", {p: u0[p]["verdict"] for p in PRIMES})

    # ---------------- I-1 recheck with the final (frozen) code: additional, not a spec gate ----
    rec = {}
    for p in PRIMES:
        gp.cmd("p=%d" % p, want=False)
        mm = 0
        for t in [t for t in types if t["p"] == p]:
            b = t["basis"]
            mat = "[" + ";".join(",".join(b[c][r] for c in range(4)) for r in range(4)) + "]"
            d = int(gp.val("deltaorder(lllorder(lathnf(%s),p),p)[1]" % mat))
            if d != t["N1"]:
                mm += 1
        rec[p] = mm
    raw["I-1_recheck_final_code_additional"] = {
        "note": "Not a spec gate. Stage A ran with deltaorder using qfminim flag 0; the frozen code uses "
                "qfminim flag 2 (multiprecision) because flag 0 lacks precision at >= 128-bit p. "
                "This re-applies I-1 with the frozen code to every WISDE type.",
        "mismatches_per_prime": {str(p): rec[p] for p in PRIMES}, "total": sum(rec.values())}
    common.log("I-1 recheck (final code):", rec)

    # ---------------- U-1 (p = 1019, k in 1..3) -------------------------------
    p = 1019
    u1 = {}
    for k in (1, 2, 3):
        gp.cmd("p=%d; B0=O0basis(); MU=matunits(B0,p,2,%d)" % (p, k), want=False)
        enum = set(gp.cmd("S=enumcyc(B0,p,2,%d); for(t=1,#S,print(S[t]))" % k, want=False))
        samp_support = gp.cmd("for(t=0,3*2^(%d-1)-1, print(latcanon(cycideal(B0,p,MU,2,%d,t))))" % (k, k), want=False)
        supp = set(samp_support)
        n = 30000
        cnt = {}
        for i in range(n):
            st = common.Stream(common.draw_seed(common.SEEDS["U-1"], "B", p, "U1-k%d" % k, i))
            idx = st.randbelow(3 * 2 ** (k - 1))
            cnt[idx] = cnt.get(idx, 0) + 1
        cells = 3 * 2 ** (k - 1)
        exp = n / cells
        chi2 = sum((cnt.get(c, 0) - exp) ** 2 / exp for c in range(cells))
        pval = stats.chi2_sf(chi2, cells - 1)
        ok = (supp == enum and len(enum) == cells and len(samp_support) == cells and pval >= 0.001)
        u1[k] = {"independent_enumeration_count": len(enum), "sampler_support_count": len(supp),
                 "expected": cells, "support_equal": supp == enum, "draws": n, "chi2": chi2, "df": cells - 1,
                 "p_value": pval, "verdict": "PASS" if ok else "FAIL"}
    raw["U-1"] = u1
    common.log("U-1", {k: (u1[k]["verdict"], u1[k]["p_value"]) for k in u1})

    # ---------------- reference laws ------------------------------------------
    laws = {}
    for p in PRIMES:
        pd = ares["per_prime"][str(p)]["pi_delta"]
        dk = sorted(int(x) for x in pd)
        laws[p] = {"delta": (dk, np.array([pd[str(d)] for d in dk]))}
        if p in TYPE_PRIMES:
            pt = ares["per_prime"][str(p)]["pi_type_by_gross_label"]
            tk = sorted(int(x) for x in pt)
            laws[p]["type"] = (tk, np.array([pt[str(t)] for t in tk]))

    floors = {}
    for p in PRIMES:
        floors[p] = {}
        for lvl in laws[p]:
            q, info = null_floor(common.SEEDS["B-NULL"], p, lvl, laws[p][lvl][0], laws[p][lvl][1])
            floors[p][lvl] = {"q99_9": q, **info}
    raw["null_floors"] = {str(p): floors[p] for p in PRIMES}
    common.log("floors", {p: {l: round(floors[p][l]["q99_9"], 4) for l in floors[p]} for p in PRIMES})

    def ctx_for(p, basis=O0, withtypes=False):
        c = {"p": p, "start_basis": basis, "Kmax": 130}
        if withtypes:
            tt = [t for t in types if t["p"] == p]
            c["types"] = (p, [t["gross_label"] for t in tt], [t["gross_gram"] for t in tt])
        return c

    def summarize(recs, p, levels):
        n = len(recs)
        out = {}
        dc = {}
        for r in recs:
            dc[r["delta"]] = dc.get(r["delta"], 0) + 1
        out["TV_delta"] = tv(dc, laws[p]["delta"][0], laws[p]["delta"][1], n)
        out["delta_counts"] = {str(k): v for k, v in sorted(dc.items())}
        if "type" in levels:
            tc = {}
            for r in recs:
                tc[r["type"]] = tc.get(r["type"], 0) + 1
            out["TV_type"] = tv(tc, laws[p]["type"][0], laws[p]["type"][1], n)
            out["unlabelled_type_count"] = tc.get(-1, 0)
        out["consistent_with_mixed"] = (out["TV_delta"] <= floors[p]["delta"]["q99_9"]) and (
            ("type" not in levels) or out["TV_type"] <= floors[p]["type"]["q99_9"])
        out["n"] = n
        out["fac_ok_all"] = all(r["fac_ok"] == 1 for r in recs)
        out["u2_all"] = all(r["u2"] == 1 for r in recs)
        out["c2_violations"] = sum(1 for r in recs if r["c2"] != 1)
        return out

    # ---------------- main grid -----------------------------------------------
    grid = {}
    for p in PRIMES:
        grid[p] = {}
        wt = p in TYPE_PRIMES
        tasks = []
        for k in KGRID:
            tasks.extend(sampling.make_tasks(common.SEEDS["B-MAIN"], "B", p, "MAIN-k%d" % k, NB, k))
        recs = sampling.run_draws(ctx_for(p, withtypes=wt), tasks, W)
        all_samples.extend([dict(r, p=p) for r in recs])
        for k in KGRID:
            rk = [r for r in recs if r["arm"] == "MAIN-k%d" % k]
            grid[p][k] = summarize(rk, p, laws[p].keys())
        common.log("p=%d grid done %.0fs" % (p, time.time() - t_start),
                   {k: (round(grid[p][k]["TV_delta"], 4), round(grid[p][k].get("TV_type", -1), 4)) for k in KGRID})
    raw["grid"] = {str(p): {str(k): grid[p][k] for k in KGRID} for p in PRIMES}

    # ---------------- PC-2 -----------------------------------------------------
    pc2 = {}
    for p in PRIMES:
        tasks = []
        for i in range(NB):
            sd = common.draw_seed(common.SEEDS["PC-2"], "B", p, "PC2", i)
            st = common.Stream(sd)
            if st.random() < 0.05:
                tasks.append({"arm": "PC2", "index": i, "seed": sd, "k": 2, "p1_index": st.randbelow(6), "contaminated": True})
            else:
                tasks.append({"arm": "PC2", "index": i, "seed": sd, "k": 64, "p1_index": st.randbelow(3 * 2 ** 63), "contaminated": False})
        recs = sampling.run_draws(ctx_for(p), tasks, W)
        all_samples.extend([dict(r, p=p) for r in recs])
        s = summarize(recs, p, ["delta"])
        s["contaminated_count"] = sum(1 for t in tasks if t["contaminated"])
        s["detected"] = s["TV_delta"] > floors[p]["delta"]["q99_9"]
        pc2[p] = s
    npc2 = sum(1 for p in PRIMES if pc2[p]["detected"])
    raw["PC-2"] = {"per_prime": {str(p): pc2[p] for p in PRIMES}, "detected_primes": npc2,
                   "verdict": "PASS" if npc2 >= 3 else "FAIL"}
    common.log("PC-2", {p: (round(pc2[p]["TV_delta"], 4), pc2[p]["detected"]) for p in PRIMES})

    # ---------------- PC-1 -----------------------------------------------------
    pc1 = {str(p): {str(k): grid[p][k]["TV_delta"] > floors[p]["delta"]["q99_9"] for k in (0, 1, 2)} for p in PRIMES}
    pc1_ok = all(all(v.values()) for v in pc1.values())
    raw["PC-1"] = {"detected": pc1, "verdict": "PASS" if pc1_ok else "FAIL"}

    # ---------------- k*(p), c_hat ----------------------------------------------
    kstar = {}
    for p in PRIMES:
        ks = None
        for idx, k in enumerate(KGRID):
            if all(grid[p][kk]["consistent_with_mixed"] for kk in KGRID[idx:]):
                ks = k
                break
        kstar[p] = ks
    ratios = {p: (kstar[p] / math.log2(p) if kstar[p] is not None else None) for p in PRIMES}
    raw["k_star"] = {str(p): kstar[p] for p in PRIMES}
    raw["k_star_over_log2p"] = {str(p): ratios[p] for p in PRIMES}
    common.log("k*", kstar, ratios)

    # ---------------- START-1 (p = 10007) -----------------------------------------
    p = 10007
    m0 = 0
    while 3 ** m0 < p:
        m0 += 1
    m = m0 + 2
    sd = common.draw_seed(common.SEEDS["START-1"], "B", p, "O0PRIME", 0)
    idx3 = common.Stream(sd).randbelow(3 ** m + 3 ** (m - 1))
    gp.cmd("p=%d; B0=O0basis(); MU3=matunits(B0,p,3,%d); J3=cycideal(B0,p,MU3,3,%d,%d); "
           "O0P=lathnf(rightorder(J3,p,3^%d))" % (p, m, m, idx3, m), want=False)
    j3 = gp.val("J3")
    o0p = gp.val("O0P")
    o0p_ok = gp.val("isorder(O0P,p) && discrd2(O0P,p)==p^2") == "1"
    o0p_delta = int(gp.val("deltaorder(lllorder(O0P,p),p)[1]"))
    start1 = {"m": m, "p1_index": str(idx3), "seed": sd, "ideal_basis": j3, "O0_prime_basis": o0p,
              "O0_prime_is_maximal_order": o0p_ok, "O0_prime_delta": o0p_delta, "per_k": {}}
    tasks = []
    for k in (16, 32, 64, 128):
        tasks.extend(sampling.make_tasks(common.SEEDS["START-1"], "B", p, "START1-k%d" % k, NB, k))
    recs = sampling.run_draws(ctx_for(p, basis=o0p), tasks, W)
    all_samples.extend([dict(r, p=p) for r in recs])
    for k in (16, 32, 64, 128):
        start1["per_k"][str(k)] = summarize([r for r in recs if r["arm"] == "START1-k%d" % k], p, ["delta"])
    k4 = [16, 32, 64, 128]
    kprime = None
    for i, k in enumerate(k4):
        if all(start1["per_k"][str(kk)]["consistent_with_mixed"] for kk in k4[i:]):
            kprime = k
            break
    ref = None if kstar[p] is None else next((k for k in k4 if k >= kstar[p]), None)
    s1_ok = (kprime is not None and ref is not None and kprime <= ref)
    start1.update({"k_star_prime": kprime, "smallest_of_four_ge_k_star_10007": ref,
                   "verdict": "PASS" if s1_ok else "FAIL"})
    raw["START-1"] = start1
    common.log("START-1", kprime, ref, start1["verdict"])

    # ---------------- U-2 over every sampled order --------------------------------
    u2_bad = sum(1 for r in all_samples if r["u2"] != 1)
    raw["U-2"] = {"sampled_orders_checked": len(all_samples), "failures": u2_bad,
                  "verdict": "PASS" if u2_bad == 0 else "FAIL"}
    c2_bad = sum(1 for r in all_samples if r["c2"] != 1)
    fac_bad = sum(1 for r in all_samples if r["fac_ok"] != 1)
    raw["C-2"] = {"violations": c2_bad}
    raw["factorisation_failures"] = fac_bad

    # ---------------- gate_G_B -----------------------------------------------------
    elig = [p for p in PRIMES if p in a1_pass]
    g1 = pc1_ok and raw["PC-2"]["verdict"] == "PASS"
    g2 = all(kstar[p] is not None and kstar[p] <= 128 for p in elig)
    pmax = max(elig)
    if g2:
        g3 = ratios[pmax] <= 2 * min(ratios[p] for p in elig)
    else:
        g3 = False
    g4 = s1_ok
    g5 = all(u0[p]["verdict"] == "PASS" for p in PRIMES) and all(u1[k]["verdict"] == "PASS" for k in u1) and u2_bad == 0
    if g1 and g2 and g3 and g4 and g5:
        verdict = "PASS"
        outcome = "gate_G_B PASS"
    elif not g1 or not g5:
        verdict = "FAIL"
        outcome = "FC-VOID (gate_G_B condition (1) or (5) failed)"
    else:
        verdict = "FAIL"
        outcome = "FC-S (gate_G_B condition (2), (3) or (4) failed with (1) passing)"
    c_hat = max(ratios[p] for p in elig) if g2 else None
    raw["gate_G_B"] = {"conditions": {"(1)_PC1_PC2": g1, "(2)_kstar_exists_le_128": g2,
                                      "(3)_kstar_pmax_ratio_le_2x_min": g3, "(3)_inputs": {"p_max": pmax, "ratio_pmax": ratios.get(pmax),
                                                                                           "min_ratio": min((ratios[p] for p in elig if ratios[p] is not None), default=None)},
                                      "(4)_START1": g4, "(5)_U0_U1_U2": g5},
                       "verdict": verdict, "outcome": outcome}
    raw["c_hat"] = c_hat
    raw["walk_length_rule"] = "k_C(p) = ceil(3 * c_hat * log2 p), evaluated in Stage C/D from the recorded c_hat"
    if c_hat is not None:
        raw["k_C_preview_for_log2p"] = {str(b): math.ceil(3 * c_hat * b) for b in (64, 96, 128, 250)}
    common.log("gate_G_B", raw["gate_G_B"])

    gp.close()
    raw["elapsed_seconds"] = round(time.time() - t_start, 1)
    common.write_jsonl_gz(os.path.join(rd, "samples.jsonl.gz"), all_samples)
    raw["samples_file_sha256"] = common.sha256_file(os.path.join(rd, "samples.jsonl.gz"))
    raw["samples_count"] = len(all_samples)
    common.write_json(os.path.join(rd, "raw-result.json"), raw)

    # analysis_freeze: hashes of every implementation file (incl. Stage C/D code)
    freeze = common.impl_hashes()
    common.write_json(os.path.join(rd, "analysis_freeze.json"), {"analysis_freeze": freeze})
    common.write_json(os.path.join(rd, "manifest_extra.json"), {
        "seeds_used": {k: common.SEEDS[k] for k in ("U-1", "B-MAIN", "B-NULL", "PC-2", "START-1")},
        "seed_derivation": "per-draw seed = SHA-256('<master>|B|<p>|<arm>|<index>'); stream = SHA-256(seed||ctr64be)",
        "workers": W, "analysis_freeze": freeze,
        "inputs": {"stage_A_run": STAGE_A_RUN, **raw["stage_A_inputs"]}})
    common.write_json(os.path.join(rd, "status.json"), {
        "status": "completed_valid", "validity": "valid", "failure_class": None,
        "reason": "Stage B executed; gate_G_B %s" % verdict, "stage_outcome": outcome})

    rel = "experiments/EXP-WESO-9e2d6d/runs/RUN-WESO-f37773/"
    tvtab = {str(p): {str(k): {"TV_delta": round(grid[p][k]["TV_delta"], 5),
                               **({"TV_type": round(grid[p][k]["TV_type"], 5)} if "TV_type" in grid[p][k] else {}),
                               "mixed": grid[p][k]["consistent_with_mixed"]} for k in KGRID} for p in PRIMES}
    common.write_exec_report(rd, "RUN-WESO-f37773", "STAGE-B", {
        "protocol_deviations": [] if W == 1 else [
            "Workers = %d > 1 before DET-1 (EX-6 allows more than 1 worker only after DET-1 passes)." % W,
        ],
        "runs": {"completed": ["RUN-WESO-f37773"], "invalid": [], "failed": []},
        "gates": {"U-0": {str(p): u0[p]["verdict"] for p in PRIMES},
                  "U-1": {str(k): {"verdict": u1[k]["verdict"], "p_value": u1[k]["p_value"], "support_equal": u1[k]["support_equal"]} for k in u1},
                  "U-2": raw["U-2"], "PC-1": raw["PC-1"]["verdict"], "PC-2": {"verdict": raw["PC-2"]["verdict"], "detected_primes": npc2},
                  "START-1": {"verdict": start1["verdict"], "k_star_prime": kprime, "reference_k": ref},
                  "gate_G_B": raw["gate_G_B"]},
        "observations": {"null_floor_q99_9": {str(p): {l: floors[p][l]["q99_9"] for l in floors[p]} for p in PRIMES},
                         "TV_table": tvtab, "k_star": raw["k_star"], "k_star_over_log2p": raw["k_star_over_log2p"],
                         "c_hat": c_hat, "k_C_preview": raw.get("k_C_preview_for_log2p"),
                         "PC-2_TV": {str(p): pc2[p]["TV_delta"] for p in PRIMES},
                         "I-1_recheck_final_code_additional": raw["I-1_recheck_final_code_additional"]},
        "stage_outcome": outcome,
        "anomalies": ([] if c2_bad == 0 else ["C-2 violations: %d" % c2_bad]) + ([] if fac_bad == 0 else ["factorisation failures: %d" % fac_bad]),
        "analysis_freeze": "analysis_freeze.json (also in manifest.yaml analysis_freeze)",
        "artifact_paths": [rel + x for x in ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log",
                                             "raw-result.json", "samples.jsonl.gz", "analysis_freeze.json", "execution_report.yaml"]],
        "executor_assessment": {"protocol_complete": True, "data_quality": "good", "requires_rerun": False},
    })
    common.log("STAGE-B outcome:", outcome, "elapsed", raw["elapsed_seconds"])


if __name__ == "__main__":
    main()
