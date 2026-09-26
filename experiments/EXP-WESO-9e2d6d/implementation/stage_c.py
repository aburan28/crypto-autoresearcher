"""EXP-WESO-9e2d6d STAGE-C (RUN-WESO-e65afd) and, through heuristic_prime(),
the Stage-D main phase.

Order of operations (spec STAGE-C, SR-4, SR-8, EX-5):
  0. gate_G_B must have passed (Stage-B raw-result); c_hat read from it.
  1. Stage-C primes by the frozen rule (PARI nextprime; proven with isprime).
  2. V-RHO-1..3 and CLS-1 (SR-4 stop on failure).
  3. DET-1 (2000 draws at p_64, 1 worker vs W workers); failure -> 1 worker.
  4. Per prime: admissible-cell table written BEFORE the first sample; all
     arms sampled; nulls drawn/factored; C-2 anchor; reproduction spot-check;
     only then the smoothness statistics.
  5. Mechanical evaluation of IG, success, FC-H1, inconclusive.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath  # noqa: E402

import analysis  # noqa: E402
import common  # noqa: E402
import rho as rhomod  # noqa: E402
import sampling  # noqa: E402

STAGE_B_RUN = "RUN-WESO-f37773"
STAGE_A_RUN = "RUN-WESO-aa2237"
N_HALF = 50000
N_ARM = 20000


def c_hat_exact(braw):
    mpmath.mp.dps = 50
    vals = []
    for p, k in braw["k_star"].items():
        if k is not None:
            vals.append(mpmath.mpf(k) / mpmath.log(int(p), 2))
    return max(vals)


def k_C(c_hat, p):
    mpmath.mp.dps = 50
    return int(mpmath.ceil(3 * c_hat * mpmath.log(p, 2)))


def cls1(gp_workers):
    """CLS-1: 10^4 integers of known factorisation (products of declared primes, seed CLS)."""
    import sympy
    declared = list(sympy.primerange(2, 2000)) + [int(sympy.nextprime(10 ** 6 * j)) for j in range(1, 11)] + \
        [int(sympy.nextprime(2 ** 40 + 1000 * j)) for j in range(1, 11)] + [int(sympy.nextprime(2 ** 61 + j)) for j in range(1, 6)]
    cases = []
    for i in range(10000):
        sd = common.draw_seed(common.SEEDS["CLS"], "C", 0, "CLS", i)
        st = common.Stream(sd)
        t = st.randbelow(6)  # 0..5 distinct primes (0 -> n = 1)
        qs = set()
        while len(qs) < t:
            qs.add(declared[st.randbelow(len(declared))])
        fac = sorted([[q, 1 + st.randbelow(3)] for q in qs])
        n = 1
        for q, e in fac:
            n *= q ** e
        mode = st.randbelow(3)
        if mode == 0 and fac:
            B = float(fac[st.randbelow(len(fac))][0])       # boundary: B equals a prime factor
        elif mode == 1 and fac:
            B = fac[st.randbelow(len(fac))][0] + 0.5         # non-integer B next to a factor
        else:
            B = 2 + st.random() * 2 * (max([q for q, _ in fac], default=2))
        truth = all(q < B for q, _ in fac)
        cases.append({"index": i, "seed": sd, "n": n, "fac": fac, "B": B, "smooth_truth": truth, "mode": mode})
    tasks = [{"arm": "CLS", "index": c["index"], "seed": c["seed"], "n": c["n"]} for c in cases]
    recs = sampling.run_nulls(tasks, gp_workers)
    bad = []
    nboundary = 0
    for c, r in zip(cases, recs):
        pred = analysis.smooth_count([r["ell_max"]], c["B"]) == 1
        okf = (r["fac"] == c["fac"] and r["fac_ok"] == 1)
        if c["mode"] == 0 and c["fac"]:
            nboundary += 1
        if not (okf and pred == c["smooth_truth"]):
            bad.append({"index": c["index"], "n": c["n"], "fac_known": c["fac"], "fac_got": r["fac"], "B": c["B"]})
    return {"cases": len(cases), "boundary_B_equals_factor_cases": nboundary,
            "noninteger_B_cases": sum(1 for c in cases if c["mode"] == 1 and c["fac"]),
            "n_equals_1_cases": sum(1 for c in cases if not c["fac"]), "errors": len(bad), "error_examples": bad[:10],
            "declared_primes": {"count": len(declared), "rule": "primes < 2000; nextprime(10^6 j), j=1..10; nextprime(2^40+1000 j), j=1..10; nextprime(2^61+j), j=1..5"},
            "verdict": "PASS" if not bad else "FAIL"}


def spot_check(ctx, main_tasks_by_key, master, stage, p, workers_note):
    """100 samples re-derived from stored seeds in a FRESH gp process."""
    sel = []
    keys = sorted(main_tasks_by_key.keys())
    for j in range(100):
        st = common.Stream(common.draw_seed(master, stage, p, "SPOT", j))
        sel.append(keys[st.randbelow(len(keys))])
    tasks = []
    for key in sel:
        arm, idx, k = main_tasks_by_key[key]["arm"], main_tasks_by_key[key]["index"], main_tasks_by_key[key]["k"]
        sd = common.draw_seed(main_tasks_by_key[key]["master"], stage, p, arm, idx)
        st = common.Stream(sd)
        tasks.append({"arm": arm, "index": idx, "seed": sd, "k": k, "p1_index": st.randbelow(3 * 2 ** (k - 1))})
    recs = sampling.run_draws(ctx, tasks, 1)
    return sel, recs


def heuristic_prime(label, p, kc, N, masters, stage, W, rd, adm, arms_spec, start_basis, extra_ctx=None):
    """Sample one Stage-C/D prime completely, then analyse.  masters: dict R1, R2, NULL."""
    t0 = time.time()
    ctx = {"p": p, "start_basis": start_basis, "Kmax": max([kc] + [a["k"] for a in arms_spec]) + 2}
    if extra_ctx:
        ctx.update(extra_ctx)
    r1_tasks = sampling.make_tasks(masters["R1"], stage, p, "R1", N_HALF, kc)
    r2_tasks = sampling.make_tasks(masters["R2"], stage, p, "R2", N_HALF, kc)
    for t in r1_tasks:
        t["master"] = masters["R1"]
    for t in r2_tasks:
        t["master"] = masters["R2"]
    main_tasks = r1_tasks + r2_tasks
    clean = [{k: v for k, v in t.items() if k != "master"} for t in main_tasks]
    main = sampling.run_draws(ctx, clean, W)
    common.log("[%s] main arm sampled (%d draws) %.0fs" % (label, len(main), time.time() - t0))
    arms = {}
    for a in arms_spec:
        actx = dict(ctx, start_basis=a.get("start_basis", start_basis))
        tasks = sampling.make_tasks(a["master"], stage, p, a["arm"], a["n"], a["k"])
        arms[a["arm"]] = sampling.run_draws(actx, tasks, W)
        common.log("[%s] arm %s sampled (%d) %.0fs" % (label, a["arm"], len(arms[a["arm"]]), time.time() - t0))
    # nulls
    X = adm["X_max"]
    n1_tasks, n2_tasks = [], []
    for i, r in enumerate(main):
        b = int(r["delta"]).bit_length()
        sd = common.draw_seed(masters["NULL"], stage, p, "NULL1", i)
        st = common.Stream(sd)
        n = (1 << (b - 1)) + st.randbelow(1 << (b - 1)) if b >= 1 else 1
        n1_tasks.append({"arm": "NULL1", "index": i, "seed": sd, "n": n})
    for i in range(N_HALF * 2):
        sd = common.draw_seed(masters["NULL"], stage, p, "NULL2", i)
        st = common.Stream(sd)
        n2_tasks.append({"arm": "NULL2", "index": i, "seed": sd, "n": 1 + st.randbelow(int(X))})
    nwd = (extra_ctx or {}).get("factor_watchdog_s")
    null1 = sampling.run_nulls(n1_tasks, W, watchdog=nwd)
    null2 = sampling.run_nulls(n2_tasks, W, watchdog=nwd)
    common.log("[%s] nulls factored %.0fs" % (label, time.time() - t0))
    # C-2 anchor (not a smoothness statistic)
    c2 = sum(1 for r in main if r["c2"] != 1) + sum(1 for a in arms.values() for r in a if r["c2"] != 1)
    # reproduction spot-check (fresh gp process)
    by_key = {(t["arm"], t["index"]): t for t in main_tasks}
    sel, rec2 = spot_check(ctx, by_key, masters["R1"], stage, p, W)
    orig = {(r["arm"], r["index"]): r for r in main}
    mism = [list(k) for k, r in zip(sel, rec2) if common.det_record(orig[k]) != common.det_record(r)]
    spot = {"selection_rule": "j=0..99: key = sorted(main keys)[randbelow(N) from SHA-256('<R1 master>|%s|<p>|SPOT|j')]" % stage,
            "selected": [list(k) for k in sel], "mismatches": mism, "verdict": "PASS" if not mism else "FAIL"}
    common.log("[%s] spot-check %s; sampling complete %.0fs" % (label, spot["verdict"], time.time() - t0))
    # write per-prime records (checkpoint) BEFORE any smoothness statistic
    allrec = [dict(r, p=str(p), prime_label=label) for r in main] + \
             [dict(r, p=str(p), prime_label=label) for a in arms.values() for r in a]
    common.write_jsonl_gz(os.path.join(rd, "samples.%s.jsonl.gz" % label), allrec)
    common.write_jsonl_gz(os.path.join(rd, "nulls.%s.jsonl.gz" % label),
                          [dict(r, p=str(p), prime_label=label) for r in null1 + null2])
    sampling_seconds = time.time() - t0
    if c2:
        return {"label": label, "p": str(p), "STOP_SR5": True, "C-2_unresolved": c2, "spot_check": spot}
    # ---- statistics (only now) ----
    res = analysis.analyze_prime(p, 2 * N_HALF, adm, main, main[:N_HALF], main[N_HALF:], null1, null2,
                                 arms=arms or None, tc4=(stage == "D"))
    res.update({"label": label, "k_C": kc, "spot_check": spot, "sampling_seconds": round(sampling_seconds, 1),
                "analysis_seconds": round(time.time() - t0 - sampling_seconds, 1)})
    if spot["verdict"] != "PASS":
        res["IV-3_run_invalid"] = True
    return res


def gp_prime_info(gp, setq):
    gp.cmd(setq, want=False)
    return {"p": gp.val("q"), "isprime_flag0": gp.val("isprime(q)"), "p_mod_4": gp.val("q%4"),
            "X_max": gp.val("sqrtnint(q\\2,3)"), "log2p": float(mpmath.log(int(gp.val("q")), 2))}


def evaluate_criteria(results, IG_parts, stage_primes):
    ig = all(v for v in IG_parts.values())
    valid = [r for r in results if r.get("prime_valid") and not r.get("IV-3_run_invalid")]
    nvalid = len(valid)
    succ = ig and nvalid >= 2 and all(r["criteria_inputs"]["a_every_admissible_wilson_upper_ge_rho"] and
                                      r["criteria_inputs"]["b_pass"] and r["criteria_inputs"]["c_pass"] for r in valid)
    fch1_primes = [r["label"] for r in valid if len(r["criteria_inputs"]["fc_h1_cells"]) >= 2]
    fch1 = ig and len(fch1_primes) >= 2
    if not ig:
        code = "FC-VOID"
    elif fch1:
        code = "FC-H1"
    elif succ:
        code = "SUCCESS_CRITERION_MET"
    else:
        code = "INCONCLUSIVE"
    return {"IG": ig, "IG_parts": IG_parts, "valid_primes": [r["label"] for r in valid], "n_valid": nvalid,
            "success_criterion_met": succ, "FC-H1_primes": fch1_primes, "FC-H1": fch1, "outcome_code": code}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--max-workers", type=int, default=3)
    ap.add_argument("--dev-primes", default=None, help="DEVELOPMENT SMOKE TEST ONLY: comma list of bit sizes (non-frozen primes)")
    ap.add_argument("--dev-scale", type=int, default=None, help="DEVELOPMENT SMOKE TEST ONLY")
    ap.add_argument("--dev-stage-b-dir", default=None, help="DEVELOPMENT SMOKE TEST ONLY")
    a = ap.parse_args()
    rd = a.run_dir
    global N_HALF, N_ARM
    t_start = time.time()
    bdir = a.dev_stage_b_dir or os.path.join(common.EXP_DIR, "runs", STAGE_B_RUN)
    braw = json.load(open(os.path.join(bdir, "raw-result.json")))
    araw = json.load(open(os.path.join(common.EXP_DIR, "runs", STAGE_A_RUN, "raw-result.json")))
    raw = {"experiment_id": "EXP-WESO-9e2d6d", "run_id": "RUN-WESO-e65afd", "stage": "STAGE-C",
           "stage_B_input": {"run": STAGE_B_RUN, "raw_result_sha256": common.sha256_file(os.path.join(bdir, "raw-result.json")),
                             "gate_G_B": braw["gate_G_B"]["verdict"]}}
    freeze = json.load(open(os.path.join(bdir, "analysis_freeze.json")))["analysis_freeze"]
    now = common.impl_hashes()
    raw["analysis_freeze_check"] = {"unchanged": freeze == now,
                                    "changed_files": sorted(k for k in set(freeze) | set(now) if freeze.get(k) != now.get(k))}
    if braw["gate_G_B"]["verdict"] != "PASS":
        common.write_json(os.path.join(rd, "status.json"), {"status": "failed", "validity": "invalid", "failure_class": "specification_error",
                                                            "reason": "gate_G_B did not pass; Stage C must not run", "stage_outcome": "NOT_RUN"})
        return
    if a.dev_scale:
        N_HALF //= a.dev_scale
        N_ARM //= a.dev_scale
    ch = c_hat_exact(braw)
    raw["c_hat"] = float(ch)
    gp = common.GP()
    bits = [int(x) for x in a.dev_primes.split(",")] if a.dev_primes else [64, 96, 128]
    primes = {}
    for b in bits:
        info = gp_prime_info(gp, "q=nextprime(2^%d); while(q%%4!=3, q=nextprime(q+1))" % b)
        info["rule"] = "smallest prime p >= 2^%d with p = 3 mod 4 (PARI nextprime; isprime flag 0 = proven)" % b
        info["k_C"] = k_C(ch, int(info["p"]))
        primes["p%d" % b] = info
    raw["primes"] = primes
    common.log("primes", {k: (v["p"], v["isprime_flag0"], v["k_C"]) for k, v in primes.items()})
    if any(v["isprime_flag0"] != "1" or v["p_mod_4"] != "3" for v in primes.values()):
        common.write_json(os.path.join(rd, "status.json"), {"status": "failed", "validity": "invalid", "failure_class": "implementation_error",
                                                            "reason": "prime rule output not proven prime / not 3 mod 4", "stage_outcome": "STOPPED"})
        return
    # V-RHO and CLS-1 (SR-4)
    vr = rhomod.validate()
    raw["V-RHO"] = vr
    cl = cls1(1)
    raw["CLS-1"] = cl
    common.log("V-RHO", vr["V-RHO-1"]["verdict"], vr["V-RHO-2"]["verdict"], vr["V-RHO-3"]["verdict"], "CLS-1", cl["verdict"])
    sr4 = [x for x in ("V-RHO-1", "V-RHO-2", "V-RHO-3") if vr[x]["verdict"] != "PASS"] + (["CLS-1"] if cl["verdict"] != "PASS" else [])
    # DET-1
    p64 = int(primes["p%d" % bits[0]]["p"])
    kc64 = primes["p%d" % bits[0]]["k_C"]
    ctx64 = {"p": p64, "start_basis": "O0basis()", "Kmax": kc64 + 2}
    det_tasks = sampling.make_tasks(common.SEEDS["DET-1"], "C", p64, "DET1", 2000 if not a.dev_scale else 200, kc64)
    t1 = time.time()
    d1 = sampling.run_draws(ctx64, det_tasks, 1)
    t2 = time.time()
    dW = sampling.run_draws(ctx64, det_tasks, a.max_workers)
    t3 = time.time()
    s1 = "\n".join(common.det_record(r) for r in d1)
    sW = "\n".join(common.det_record(r) for r in dW)
    det_ok = s1 == sW
    W = a.max_workers if det_ok else 1
    raw["DET-1"] = {"draws": len(det_tasks), "workers_compared": [1, a.max_workers],
                    "sha256_1worker": common.sha256_str(s1), "sha256_Wworkers": common.sha256_str(sW),
                    "byte_identical_deterministic_fields": det_ok, "wall_1worker_s": round(t2 - t1, 2),
                    "wall_Wworkers_s": round(t3 - t2, 2), "verdict": "PASS" if det_ok else "FAIL",
                    "workers_used_after": W,
                    "comparison_note": "per-sample records compared on every field except wall_s (wall-clock time cannot be byte-identical)"}
    common.log("DET-1", raw["DET-1"]["verdict"], "workers ->", W)
    common.write_jsonl_gz(os.path.join(rd, "det1.jsonl.gz"), [dict(r, det1_workers=1) for r in d1] + [dict(r, det1_workers=a.max_workers) for r in dW])
    if sr4:
        raw["stage_outcome"] = "FC-VOID (SR-4: %s failed)" % sr4
        common.write_json(os.path.join(rd, "raw-result.json"), raw)
        common.write_json(os.path.join(rd, "status.json"), {"status": "completed_valid", "validity": "valid", "failure_class": None,
                                                            "reason": "SR-4 stop", "stage_outcome": raw["stage_outcome"]})
        return
    # per prime
    results = []
    adm_tables = {}
    for b in bits:
        label = "p%d" % b
        p = int(primes[label]["p"])
        kc = primes[label]["k_C"]
        adm = analysis.admissible_table(p, 2 * N_HALF)
        adm["X_max"] = primes[label]["X_max"]
        adm["recorded_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        adm["recorded_before_first_sample"] = True
        common.write_json(os.path.join(rd, "admissible_cells.%s.json" % label), adm)
        adm_tables[label] = adm
        common.log("[%s] admissible-cell table recorded before sampling: admissible u = %s" % (
            label, [c["u"] for c in adm["cells"] if c["admissible"]]))
        pre = "C%d" % b if not a.dev_primes else "C%d" % [64, 96, 128][bits.index(b)]
        masters = {"R1": common.SEEDS[pre + "-R1"], "R2": common.SEEDS[pre + "-R2"], "NULL": common.SEEDS[pre + "-NULL"]}
        arms = []
        if b == bits[0]:
            # O_0' for START-2
            m0 = 0
            while 3 ** m0 < p:
                m0 += 1
            m = m0 + 2
            sd = common.draw_seed(common.SEEDS["C64-START2"], "C", p, "O0PRIME", 0)
            idx3 = common.Stream(sd).randbelow(3 ** m + 3 ** (m - 1))
            gp.cmd("SO=startorder3(O0basis(),%d,%d,%d)" % (p, m, idx3), want=False)
            o0p = gp.val("SO[2]")
            ok = gp.val("isorder(SO[2],%d) && discrd2(SO[2],%d)==%d^2" % (p, p, p)) == "1"
            raw["O0_prime_p64"] = {"m": m, "seed": sd, "p1_index": str(idx3), "ideal_basis": gp.val("SO[1]"),
                                   "O0_prime_basis": o0p, "is_maximal_order": ok}
            arms = [{"arm": "KS1", "master": common.SEEDS["C64-KS1"], "n": N_ARM, "k": 2 * kc},
                    {"arm": "START2", "master": common.SEEDS["C64-START2"], "n": N_ARM, "k": kc, "start_basis": o0p},
                    {"arm": "PC3", "master": common.SEEDS["C64-PC3"], "n": N_ARM, "k": 4}]
        res = heuristic_prime(label, p, kc, 2 * N_HALF, masters, "C", W, rd, adm, arms, "O0basis()")
        results.append(res)
        if res.get("STOP_SR5"):
            raw["stage_outcome"] = "STOPPED (SR-5 unresolved C-2 violation at %s)" % label
            break
        common.log("[%s] analysed" % label)
    gp.close()
    raw["per_prime"] = results
    raw["admissible_tables"] = adm_tables
    if not any(r.get("STOP_SR5") for r in results):
        pc3 = results[0].get("PC-3", {}).get("verdict") == "PASS"
        null2 = all(r["NULL-2_bounds"]["verdict"] == "PASS" for r in results)
        c2none = all(r["C-2_violations"] == 0 for r in results)
        IG = {"I-1": araw["I1_total_mismatches"] == 0, "A-1": len(araw["A1_passing_primes"]) >= 3,
              "gate_G_B": braw["gate_G_B"]["verdict"] == "PASS", "PC-3": pc3,
              "V-RHO-1..3": all(vr[x]["verdict"] == "PASS" for x in ("V-RHO-1", "V-RHO-2", "V-RHO-3")),
              "CLS-1": cl["verdict"] == "PASS", "NULL-2_bounds": null2,
              "DET-1_or_single_worker": det_ok or W == 1, "no_unresolved_C-2": c2none}
        crit = evaluate_criteria(results, IG, bits)
        if any(r.get("IV-3_run_invalid") for r in results):
            crit["IV-3"] = "reproduction spot-check mismatch -> run invalid"
        raw["criteria"] = crit
        raw["stage_outcome"] = crit["outcome_code"]
    raw["workers"] = W
    raw["elapsed_seconds"] = round(time.time() - t_start, 1)
    raw["sample_files"] = {f: common.sha256_file(os.path.join(rd, f)) for f in sorted(os.listdir(rd))
                           if f.startswith(("samples.", "nulls.", "det1."))}
    common.write_json(os.path.join(rd, "raw-result.json"), raw)
    # IV-4 checker in a fresh process
    chk = subprocess.run([sys.executable, "-B", os.path.join(common.IMPL_DIR, "checker.py"), "--run-dir", rd],
                         capture_output=True, text=True)
    chkres = json.load(open(os.path.join(rd, "checker_result.json"))) if os.path.exists(os.path.join(rd, "checker_result.json")) else {"verdict": "ERROR", "stderr": chk.stderr[-3000:]}
    iv5 = not raw["analysis_freeze_check"]["unchanged"]
    invalid = bool(raw.get("criteria", {}).get("IV-3")) or chkres.get("verdict") != "PASS" or iv5
    status = {"status": "completed_valid" if not invalid else "completed_invalid",
              "validity": "valid" if not invalid else "invalid", "failure_class": None if not invalid else "invalid_measurement",
              "reason": "Stage C executed; outcome %s; checker %s; analysis_freeze unchanged %s" % (
                  raw["stage_outcome"], chkres.get("verdict"), not iv5),
              "stage_outcome": raw["stage_outcome"]}
    common.write_json(os.path.join(rd, "status.json"), status)
    common.write_json(os.path.join(rd, "manifest_extra.json"), {
        "seeds_used": {k: common.SEEDS[k] for k in common.SEEDS if k.startswith(("C64", "C96", "C128", "CLS", "DET-1"))},
        "seed_derivation": "per-draw seed = SHA-256('<master>|C|<p>|<arm>|<index>'); stream = SHA-256(seed||ctr64be)",
        "workers": W, "primes": primes, "c_hat": float(ch),
        "admissible_cell_tables": {k: "admissible_cells.%s.json" % k for k in adm_tables},
        "analysis_freeze_check": raw["analysis_freeze_check"],
        "reproduction_spot_check": {r["label"]: r.get("spot_check", {}).get("verdict") for r in results},
        "checker": chkres.get("verdict"),
        "inputs": {"stage_B_run": STAGE_B_RUN, "stage_A_run": STAGE_A_RUN}})
    import report
    devs = []
    if a.max_workers != 4:
        devs.append("DET-1 compared 1 worker with %d workers (not 4) and the stage ran with at most %d workers: the host "
                    "was shared with another executor and the dispatching session capped this task at 3 workers. "
                    "Draws are index-seeded, so results do not depend on worker count." % (a.max_workers, a.max_workers))
    devs.append("Per-sample and per-null records are written per prime as samples.<p-label>.jsonl.gz and "
                "nulls.<p-label>.jsonl.gz (plus det1.jsonl.gz) instead of one samples.jsonl.gz / nulls.jsonl.gz: this "
                "checkpoints each prime as it completes and keeps every artifact under the spec's 50 MiB size_note limit. "
                "Record content is as the spec lists.")
    anomalies = []
    for r in results:
        if r.get("U-2_failures"):
            anomalies.append("%s: U-2 failures %d" % (r["label"], r["U-2_failures"]))
    report.write_stage_report(rd, "RUN-WESO-e65afd", "STAGE-C", raw, chkres, status,
                              extra={"protocol_deviations": devs, "anomalies": anomalies,
                                     "stages_not_run_note": "Stage D is a separate run (RUN-WESO-0b4b33)."})
    common.log("STAGE-C outcome:", raw["stage_outcome"], "elapsed", raw["elapsed_seconds"])


if __name__ == "__main__":
    main()
