#!/usr/bin/env python3
"""TASK-20260923-404bf9 (red team) -- K6 measurement and proves-too-much OBJECT B.

PART B  (object B): run the producer's arm-(iii) path, unchanged, on the
        random_no2torsion ladder curve at p' = 4111, m = 3, constructed-solvable
        (cmd_cell), plus the build step (cmd_build) and the phi-pool builder, and
        record what each does.

PART K6: (1) parse the committed msolve logs of the m = 3 and m = 4 cells and
        recompute the proxy per target from the printed matrix shapes (producer's
        own parser), compare shapes across primes and arms, and collect msolve's
        printed CPU times;
        (2) regenerate, with the producer's own functions and seeds, the m = 3 raw and
        S3 constructed-solvable systems at p' = 4111 (targets 0..4) and one m = 4
        S4 random-target system, confirm they are the committed systems (identical
        per-round F4 shapes), and MEASURE work: user+sys CPU over repeated native
        msolve runs, and executed instructions (valgrind callgrind, total and
        inclusive in libneogb's core_f4) against a trivial-system baseline.
Every msolve / valgrind subprocess is taken under fcntl.flock on the solver lock.
"""
import os, sys, json, time, fcntl, re, subprocess, glob, random, resource, traceback, statistics as st
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
IMPL = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43", "implementation")
RUNS = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43", "runs")
LOCK = "/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/gfpn-solver.lock"
OBJB = os.path.join(os.path.dirname(HERE), "objB")
os.environ["GFPN_CACHE_DIR"] = os.path.join(HERE, "cache")
os.environ["GFPN_MEM_CAP_GB"] = "11"
sys.path.insert(0, IMPL)
import numpy as np
import gfpn5_core, symmetrize, pdp_common, pdp_cell

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)

class Locked:
    def __enter__(self):
        self.fh = open(LOCK, "a"); fcntl.flock(self.fh, fcntl.LOCK_EX); return self
    def __exit__(self, *a):
        fcntl.flock(self.fh, fcntl.LOCK_UN); self.fh.close()

_orig = symmetrize.run_msolve
def locked_run_msolve(*a, **k):
    with Locked():
        return _orig(*a, **k)
pdp_cell.run_msolve = locked_run_msolve; pdp_common.run_msolve = locked_run_msolve

OUT = {"task": "TASK-20260923-404bf9"}

# ============================================================== PART B
def part_b():
    res = {"object": "B", "p": 4111, "shape": "random_no2torsion", "arm": "torsion_S3", "m": 3, "steps": []}
    rung = pdp_common.ladder_entry(4111); cv = rung["curves"]["random_no2torsion"]
    res["curve"] = {k: cv[k] for k in ("model", "a2", "a4", "a6", "has_rational_2torsion", "order", "cofactor")}
    # step 1: the cell path
    rd = os.path.join(OBJB, "run_cell"); os.makedirs(os.path.join(rd, "certificates"), exist_ok=True)
    os.environ["GFPN_RUN_DIR"] = rd
    a = SimpleNamespace(p=4111, shape="random_no2torsion", arm="torsion_S3", m=3, targets=20, target_timeout=900,
                        cell_watchdog=5400, max_consecutive_not_measured=3, target_kind="constructed_solvable")
    try:
        pdp_cell.cmd_cell(a)
        res["steps"].append({"step": "pdp_cell.cmd_cell(torsion_S3, random_no2torsion, constructed_solvable)", "outcome": "RAN (no refusal)",
                             "raw_result": json.load(open(os.path.join(rd, "raw-result.json")))["metrics"]})
    except BaseException as e:
        res["steps"].append({"step": "pdp_cell.cmd_cell(torsion_S3, random_no2torsion, constructed_solvable)", "outcome": "REFUSED",
                             "exception": type(e).__name__, "traceback_tail": traceback.format_exc().strip().splitlines()[-4:]})
    # step 2: the build path (arms=torsion, shapes=random_no2torsion)
    rd2 = os.path.join(OBJB, "run_build"); os.makedirs(rd2, exist_ok=True); os.environ["GFPN_RUN_DIR"] = rd2
    b = SimpleNamespace(p=4111, m_list=[3], force=True, shapes=["random_no2torsion"], arms=["torsion"])
    try:
        pdp_cell.cmd_build(b)
        rr = json.load(open(os.path.join(rd2, "raw-result.json")))
        res["steps"].append({"step": "pdp_cell.cmd_build(arms=torsion, shapes=random_no2torsion, m=3)", "outcome": "RAN",
                             "n_polynomials": rr["metrics"]["n_polynomials"]})
    except BaseException as e:
        res["steps"].append({"step": "pdp_cell.cmd_build(arms=torsion, shapes=random_no2torsion, m=3)", "outcome": "EXCEPTION",
                             "exception": type(e).__name__, "traceback_tail": traceback.format_exc().strip().splitlines()[-4:],
                             "files_written": sorted(os.listdir(rd2))})
    # step 3: the phi-factor-base pool builder
    F = gfpn5_core.Fq(4111, rung["cmod"]); E, _ = pdp_common.make_curve(F, rung, "random_no2torsion")
    try:
        pool = symmetrize.build_pool_t(E, random.Random(0), size_limit=100)
        res["steps"].append({"step": "symmetrize.build_pool_t(random_no2torsion)", "outcome": "RAN", "pool_size": len(pool)})
    except BaseException as e:
        res["steps"].append({"step": "symmetrize.build_pool_t(random_no2torsion)", "outcome": "REFUSED", "exception": type(e).__name__,
                             "traceback_tail": traceback.format_exc().strip().splitlines()[-3:]})
    res["curve_has_rational_2torsion_by_flint_roots"] = bool(E.has_rational_2torsion())
    return res

# ============================================================== PART K6 (1): committed logs
ROW = re.compile(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+) x (\d+)\s+([\d.]+)%\s+(\d+) new\s+(\d+) zero\s+([\d.]+) \| ([\d.]+)")
def shapes_of(text):
    return [tuple(m.groups()[:8]) for m in (ROW.match(l) for l in text.splitlines()) if m]

def committed_logs():
    out = {}
    cells = {"S4_p4111": "RUN-GFPN-f888a7", "torsionS4_p4111": "RUN-GFPN-fb0726", "S4_p262151": "RUN-GFPN-26a539",
             "torsionS4_p262151": "RUN-GFPN-2926e7", "S4_p16777291": "RUN-GFPN-9172cf", "torsionS4_p16777291": "RUN-GFPN-adaec1",
             "S3cs_p4111": "RUN-GFPN-49f7c5", "torsionS3cs_p4111": "RUN-GFPN-5f9840", "rawcs_m3_p4111": "RUN-GFPN-cdf887"}
    for key, rid in cells.items():
        rr = json.load(open(os.path.join(RUNS, rid, "raw-result.json")))
        per = []
        for t in rr["targets"]:
            if t.get("status") != "measured": continue
            i = t["target"]
            lg = glob.glob(os.path.join(RUNS, rid, f"*_t{i}.ms.log"))
            txt = open(lg[0]).read() if lg else ""
            stt = symmetrize.parse_msolve_log(txt)
            per.append({"target": i, "n_rounds": len(stt["f4_rounds"]),
                        "proxy_red_recomputed": stt["f4_summary"]["ops_proxy_reduction_total"],
                        "proxy_nnz_recomputed": stt["f4_summary"]["ops_proxy_rows_cols_density"],
                        "proxy_red_committed": t.get("fp_ops_f4_proxy"), "cpu": stt["timings"].get("overall_cpu"),
                        "sum_round_cpu": sum(r["sec_cpu"] for r in stt["f4_rounds"])})
        out[key] = {"run": rid, "n": len(per), "targets": per,
                    "cpu_sum": sum(p["cpu"] or 0 for p in per), "proxy_red_sum": sum(p["proxy_red_recomputed"] for p in per),
                    "proxy_nnz_sum": sum(p["proxy_nnz_recomputed"] for p in per),
                    "recompute_matches_committed": all(abs(p["proxy_red_recomputed"] - (p["proxy_red_committed"] or 0)) < 1e-6 * max(1, p["proxy_red_recomputed"]) for p in per),
                    "fp_operations_per_pdp_committed": rr["metrics"].get("fp_operations_per_pdp")}
    # shape identity across primes / arms, target 0 (first measured)
    def seq(rid, pat):
        lg = sorted(glob.glob(os.path.join(RUNS, rid, pat)))
        return shapes_of(open(lg[0]).read()) if lg else None
    s0 = {k: seq(v, "*_t0.ms.log") for k, v in cells.items()}
    out["shape_identity_target0"] = {
        "S4_4111_vs_262151_rows_cols_new_zero_equal": [r[3:5] + r[6:8] for r in s0["S4_p4111"]] == [r[3:5] + r[6:8] for r in s0["S4_p262151"]],
        "S4_4111_vs_16777291_rows_cols_new_zero_equal": [r[3:5] + r[6:8] for r in s0["S4_p4111"]] == [r[3:5] + r[6:8] for r in s0["S4_p16777291"]],
        "S4_vs_torsionS4_4111_rows_cols_new_zero_equal": [r[3:5] + r[6:8] for r in s0["S4_p4111"]] == [r[3:5] + r[6:8] for r in s0["torsionS4_p4111"]],
        "n_rounds": {k: (len(v) if v else None) for k, v in s0.items()}}
    return out

# ============================================================== PART K6 (2): regenerate + measure
def cpu_children():
    r = resource.getrusage(resource.RUSAGE_CHILDREN); return r.ru_utime + r.ru_stime

def native_cpu(fn, reps, threads=1):
    t0 = cpu_children()
    with Locked():
        for _ in range(reps):
            subprocess.run(["/usr/bin/msolve", "-v", "0", "-t", str(threads), "-f", fn, "-o", fn + ".nat.out", "-P", "1"], capture_output=True)
    return (cpu_children() - t0) / reps

def callgrind(fn, tag, threads=1):
    cg = os.path.join(HERE, f"callgrind.{tag}.out")
    with Locked():
        r = subprocess.run(["valgrind", "--tool=callgrind", f"--callgrind-out-file={cg}", "/usr/bin/msolve", "-v", "2", "-t", str(threads),
                            "-f", fn, "-o", fn + ".cg.out", "-P", "1"], capture_output=True, text=True)
    tot = None
    m = re.search(r"Collected\s*:\s*(\d+)", r.stderr)
    if m: tot = int(m.group(1))
    ann = subprocess.run(["callgrind_annotate", "--inclusive=yes", cg], capture_output=True, text=True).stdout
    f4 = None
    for line in ann.splitlines():
        if re.search(r"\bcore_f4\b", line) and "core_f4sat" not in line:
            mm = re.match(r"\s*([\d,]+)", line)
            if mm: f4 = int(mm.group(1).replace(",", "")); break
    with open(os.path.join(HERE, f"callgrind.{tag}.annotate.txt"), "w") as fh:
        fh.write("\n".join(ann.splitlines()[:80]))
    os.remove(cg)
    return {"Ir_total": tot, "Ir_inclusive_core_f4": f4, "msolve_stdout_shapes": shapes_of(r.stdout)}

def regen_and_measure():
    p = 4111; shape = "ecgfp5_shaped"; rung = pdp_common.ladder_entry(p); F = gfpn5_core.Fq(p, rung["cmod"])
    E, cv = pdp_common.make_curve(F, rung, shape)
    G, n = pdp_common.base_point(E, cv, p, shape)
    wd = os.path.join(HERE, "systems"); os.makedirs(wd, exist_ok=True)
    res = {"p": p, "systems": {}}
    # baseline: trivial zero-dimensional system in 3 unknowns
    base = os.path.join(wd, "baseline_m3.ms")
    open(base, "w").write("x1,x2,x3\n4111\nx1-1,\nx2-2,\nx3-3\n")
    # --- m = 3 raw (cmd_raw's construction) and S3 (cmd_build + cmd_cell's construction), constructed-solvable targets
    pool_raw = symmetrize.build_pool_x(E, random.Random(f"{pdp_common.SEED_CURVES}:raw:{p}:{shape}:3"), size_limit=pdp_cell.POOL_LIMIT)
    stg_raw = pdp_cell.solvable_targets(E, cv, p, shape, "raw", 3, pool_raw, None, 5, n)
    rngb = random.Random(f"{pdp_common.SEED_CURVES}:build:{p}:{shape}:S3:3")
    pool_b = symmetrize.build_pool_x(E, rngb, size_limit=pdp_cell.POOL_LIMIT)
    polS3 = symmetrize.build_arm_polynomial(E, "S3", 3, rngb, pool_b, log=lambda *a: None)
    pool_c = symmetrize.build_pool_x(E, random.Random(f"{pdp_common.SEED_CURVES}:pool:{p}:{shape}:S3"), size_limit=pdp_cell.POOL_LIMIT)
    stg_s3 = pdp_cell.solvable_targets(E, cv, p, shape, "S3", 3, pool_c, None, 5, n)
    rng_nodes = random.Random(1)
    committed_raw = {i: shapes_of(open(os.path.join(RUNS, "RUN-GFPN-cdf887", f"raw_t{i}.ms.log")).read()) for i in range(5)}
    committed_s3 = {i: shapes_of(open(os.path.join(RUNS, "RUN-GFPN-49f7c5", f"cell_t{i}.ms.log")).read()) for i in range(5)}
    for (i, k, R, _G, _n, _xs) in stg_raw:
        C, nodes = symmetrize.build_raw_polynomial_at_target(E, 3, R[0], pool=pool_raw, rng=rng_nodes, log=lambda *a: None)
        fn = os.path.join(wd, f"raw_m3_t{i}.ms"); symmetrize.descend_raw_and_write(C, pdp_cell.XVARS[3], p, fn)
        res["systems"][f"raw_m3_t{i}"] = {"file": fn}
    for (i, k, R, _G, _n, _xs) in stg_s3:
        sp = polS3.specialise(F, R[0]); fn = os.path.join(wd, f"S3_m3_t{i}.ms")
        symmetrize.descend_and_write(sp, polS3.monos, pdp_cell.VARS[3], p, fn)
        res["systems"][f"S3_m3_t{i}"] = {"file": fn}
    # --- m = 4 S4 random target 0 (contract cell RUN-GFPN-f888a7 target 0)
    rng4 = random.Random(f"{pdp_common.SEED_CURVES}:build:{p}:{shape}:S4:4")
    pool4 = symmetrize.build_pool_x(E, rng4, size_limit=pdp_cell.POOL_LIMIT)
    polS4 = symmetrize.build_arm_polynomial(E, "S4", 4, rng4, pool4, log=lambda *a: None)
    tg = pdp_common.targets(E, G, n, p, shape, 1)
    sp4 = polS4.specialise(F, tg[0][2][0]); fn4 = os.path.join(wd, "S4_m4_t0.ms")
    symmetrize.descend_and_write(sp4, polS4.monos, pdp_cell.VARS[4], p, fn4)
    committed_s4 = shapes_of(open(os.path.join(RUNS, "RUN-GFPN-f888a7", "cell_t0.ms.log")).read())
    # --- measurements
    res["baseline_m3"] = {"native_cpu_s": native_cpu(base, 50), **{k: v for k, v in callgrind(base, "baseline").items() if k != "msolve_stdout_shapes"}}
    for key, rec in res["systems"].items():
        fn = rec["file"]
        rec["native_cpu_s_per_run_t1"] = native_cpu(fn, 50)
        with Locked():
            r = subprocess.run(["/usr/bin/msolve", "-v", "2", "-t", "1", "-f", fn, "-o", fn + ".v.out", "-P", "1"], capture_output=True, text=True)
        stt = symmetrize.parse_msolve_log(r.stdout + r.stderr)
        rec["proxy_red"] = stt["f4_summary"]["ops_proxy_reduction_total"]; rec["proxy_nnz"] = stt["f4_summary"]["ops_proxy_rows_cols_density"]
        rec["D"] = stt["dimension_of_quotient"]
        i = int(key.split("_t")[1])
        cref = committed_raw[i] if key.startswith("raw") else committed_s3[i]
        rec["shapes_equal_committed"] = [s[3:5] + s[6:8] for s in shapes_of(r.stdout)] == [s[3:5] + s[6:8] for s in cref]
        rec.update({k: v for k, v in callgrind(fn, key).items() if k != "msolve_stdout_shapes"})
        log(key, {k: v for k, v in rec.items() if k != "file"})
    # m = 4: one callgrind run (single thread) and a native CPU measurement
    rec4 = {"file": fn4, "native_cpu_s_per_run_t1": native_cpu(fn4, 2)}
    with Locked():
        r = subprocess.run(["/usr/bin/msolve", "-v", "2", "-t", "1", "-f", fn4, "-o", fn4 + ".v.out", "-P", "1"], capture_output=True, text=True)
    stt = symmetrize.parse_msolve_log(r.stdout + r.stderr)
    rec4.update({"proxy_red": stt["f4_summary"]["ops_proxy_reduction_total"], "proxy_nnz": stt["f4_summary"]["ops_proxy_rows_cols_density"],
                 "D": stt["dimension_of_quotient"], "no_solution": stt["no_solution"],
                 "shapes_equal_committed": [s[3:5] + s[6:8] for s in shapes_of(r.stdout)] == [s[3:5] + s[6:8] for s in committed_s4]})
    rec4.update({k: v for k, v in callgrind(fn4, "S4_m4_t0").items() if k != "msolve_stdout_shapes"})
    res["systems"]["S4_m4_t0"] = rec4
    log("S4_m4_t0", {k: v for k, v in rec4.items() if k != "file"})
    for f in glob.glob(os.path.join(wd, "*.out")): os.remove(f)
    # ratios, m = 3 raw over S3, target by target (targets 0..4 of each committed cell)
    b = res["baseline_m3"]; S = res["systems"]; rat = []
    for i in range(5):
        r_, s_ = S.get(f"raw_m3_t{i}"), S.get(f"S3_m3_t{i}")
        if not r_ or not s_: continue
        def q(a, c): return (a / c) if (a is not None and c) else None
        rat.append({"target": i,
                    "proxy_red_F4_only": q(r_["proxy_red"], s_["proxy_red"]),
                    "native_cpu": q(r_["native_cpu_s_per_run_t1"], s_["native_cpu_s_per_run_t1"]),
                    "native_cpu_minus_baseline": q(r_["native_cpu_s_per_run_t1"] - b["native_cpu_s"], s_["native_cpu_s_per_run_t1"] - b["native_cpu_s"]),
                    "Ir_total": q(r_["Ir_total"], s_["Ir_total"]),
                    "Ir_total_minus_baseline": q((r_["Ir_total"] or 0) - (b["Ir_total"] or 0), (s_["Ir_total"] or 0) - (b["Ir_total"] or 0)),
                    "Ir_core_f4": q(r_["Ir_inclusive_core_f4"], s_["Ir_inclusive_core_f4"])})
    res["ratios_raw_over_S3_m3"] = rat
    res["committed_fp_ops_ratio_raw_over_sym_S3_p4111"] = 39.630283668439446
    s4 = S["S4_m4_t0"]
    res["m4_proxy_over_Ir_core_f4"] = (s4["proxy_red"] / s4["Ir_inclusive_core_f4"]) if s4.get("Ir_inclusive_core_f4") else None
    res["m4_nnz_proxy_over_Ir_core_f4"] = (s4["proxy_nnz"] / s4["Ir_inclusive_core_f4"]) if s4.get("Ir_inclusive_core_f4") else None
    return res

if __name__ == "__main__":
    t0 = time.time()
    OUT["object_B"] = part_b(); log("object B", json.dumps(OUT["object_B"], default=str)[:2000])
    json.dump(OUT, open(os.path.join(HERE, "k6_objB_summary.json"), "w"), indent=1, default=str)
    OUT["k6_committed_logs"] = committed_logs(); log("committed logs parsed")
    json.dump(OUT, open(os.path.join(HERE, "k6_objB_summary.json"), "w"), indent=1, default=str)
    OUT["k6_measured"] = regen_and_measure()
    OUT["wall_seconds"] = round(time.time() - t0, 1)
    json.dump(OUT, open(os.path.join(HERE, "k6_objB_summary.json"), "w"), indent=1, default=str)
    log("done", OUT["wall_seconds"])
