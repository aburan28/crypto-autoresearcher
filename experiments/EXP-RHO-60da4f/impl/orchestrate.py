#!/usr/bin/env python3
"""
Orchestrates EXP-RHO-60da4f execution: controls C1-C5 and the escape-rule x r
x dp_bits x seed grid, at the sizes and coverage actually completed within
this session's real wall-clock budget (a real, disclosed infrastructure
constraint distinct from the specification's nominal 240 CPU-hour /
900000-second budget -- see implementation.md).

Writes raw per-run JSON lines into experiments/EXP-RHO-60da4f/runs/<batch>/raw-result.jsonl
plus a manifest.yaml per batch directory.
"""
import subprocess, json, time, os, sys, statistics, random

HERE = os.path.dirname(os.path.abspath(__file__))
RHO = os.path.join(HERE, "rho")
EXP_DIR = os.path.dirname(HERE)
RUNS_DIR = os.path.join(EXP_DIR, "runs")

CURVES = json.load(open(os.path.join(EXP_DIR, "curves.json")))["curves"]
CURVE_BY_SIZE = {c["subgroup_size_log2"]: c for c in CURVES}

SEEDS_FULL = [1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597]

ESCAPE_SETTINGS = [
    ("none", None),
    ("det", None),
    ("periodic", 2), ("periodic", 4), ("periodic", 8), ("periodic", 16), ("periodic", 32),
    ("lookahead", None),
    ("reselect", None),
]
R_VALUES = [4,8,16,20,32]
DP_BITS = [8,12,16]

def run_rho(args, timeout=120):
    t0=time.time()
    p = subprocess.run([RHO]+args, capture_output=True, text=True, timeout=timeout)
    dt=time.time()-t0
    if p.returncode!=0:
        return None, dt, p.stderr
    try:
        return json.loads(p.stdout.strip()), dt, p.stderr
    except Exception as e:
        return None, dt, f"parse-error: {e}; stdout={p.stdout!r}"

def curve_args(c):
    return ["--p",str(c["p"]),"--a",str(c["a"]),"--b",str(c["b"]),
            "--N",str(c["N"]),"--gx",str(c["Gx"]),"--gy",str(c["Gy"])]

def write_batch(name, records, extra_manifest=None):
    d = os.path.join(RUNS_DIR, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d,"raw-result.jsonl"),"w") as f:
        for r in records:
            f.write(json.dumps(r)+"\n")
    man = {
        "batch": name,
        "n_records": len(records),
        "note": "Batched immutable run record: one directory per (size, escape_rule or control) group, per-cell provenance embedded in each JSONL row (seed, r, dp_bits). Disclosed compromise from one-directory-per-cell, recorded as a protocol deviation in implementation.md given the full grid's run count (thousands of cells).",
    }
    if extra_manifest: man.update(extra_manifest)
    with open(os.path.join(d,"manifest.yaml"),"w") as f:
        import yaml
        yaml.safe_dump(man, f, sort_keys=False)
    print(f"wrote {len(records)} records -> {d}", file=sys.stderr)

def calibrate_ops(reps=200000):
    """Time raw modmul/modsqr/modinv via a microbenchmark using the C1 baseline
    harness at trivial scale is not directly exposed; instead time via a tiny
    standalone C snippet compiled on the fly."""
    src = os.path.join(HERE,"calib.c")
    with open(src,"w") as f:
        f.write(r'''
#include <stdio.h>
#include <stdint.h>
#include <time.h>
typedef unsigned __int128 u128;
typedef uint64_t u64;
static u64 P=2381327587ULL;
static inline u64 mmul(u64 a,u64 b){ return (u64)(((u128)a*b)%P); }
static inline u64 msqr(u64 a){ return (u64)(((u128)a*a)%P); }
static u64 minv(u64 a){
    int64_t t=0,newt=1; int64_t r=(int64_t)P, newr=(int64_t)a;
    while(newr!=0){ int64_t q=r/newr; int64_t tmp=t-q*newt; t=newt; newt=tmp; tmp=r-q*newr; r=newr; newr=tmp; }
    if(t<0) t+=(int64_t)P; return (u64)t;
}
int main(){
    u64 x=123456789%P, y=987654321%P, acc=0;
    struct timespec t0,t1;
    long N=20000000;
    clock_gettime(CLOCK_MONOTONIC,&t0);
    for(long i=0;i<N;i++){ acc^=mmul(x,y); x=(x+1)%P; }
    clock_gettime(CLOCK_MONOTONIC,&t1);
    double mul_ns=((t1.tv_sec-t0.tv_sec)*1e9+(t1.tv_nsec-t0.tv_nsec))/N;
    clock_gettime(CLOCK_MONOTONIC,&t0);
    x=123456789%P;
    for(long i=0;i<N;i++){ acc^=msqr(x); x=(x+1)%P; }
    clock_gettime(CLOCK_MONOTONIC,&t1);
    double sqr_ns=((t1.tv_sec-t0.tv_sec)*1e9+(t1.tv_nsec-t0.tv_nsec))/N;
    long M=2000000;
    clock_gettime(CLOCK_MONOTONIC,&t0);
    x=123456789%P;
    for(long i=0;i<M;i++){ acc^=minv((x%(P-1))+1); x=(x+1)%P; }
    clock_gettime(CLOCK_MONOTONIC,&t1);
    double inv_ns=((t1.tv_sec-t0.tv_sec)*1e9+(t1.tv_nsec-t0.tv_nsec))/M;
    printf("{\"mul_ns\":%f,\"sqr_ns\":%f,\"inv_ns\":%f,\"checksum\":%llu}\n", mul_ns, sqr_ns, inv_ns, (unsigned long long)acc);
    return 0;
}
''')
    subprocess.run(["clang","-O2","-o",os.path.join(HERE,"calib"),src], check=True)
    p = subprocess.run([os.path.join(HERE,"calib")], capture_output=True, text=True, check=True)
    return json.loads(p.stdout.strip())

if __name__=="__main__":
    os.makedirs(RUNS_DIR, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv)>1 else "all"

    if mode in ("all","calib"):
        calib = calibrate_ops()
        print("CALIBRATION:", calib, file=sys.stderr)
        json.dump(calib, open(os.path.join(EXP_DIR,"op_ratio_calibration.json"),"w"), indent=2)

    if mode in ("all","c1"):
        recs=[]
        for size, c in CURVE_BY_SIZE.items():
            for seed in SEEDS_FULL:
                res, dt, err = run_rho(["run-vw"]+curve_args(c)+
                    ["--seed",str(seed),"--r","20","--dpbits","12","--mode","0","--escape","det","--budget-mult","64"], timeout=300)
                if res is None:
                    recs.append({"size":size,"seed":seed,"error":err}); continue
                res.update({"size":size,"seed":seed,"r":20,"dp_bits":12,"wall_s":dt,
                            "methodology":"vw_multiwalk_session2_corrected"})
                recs.append(res)
        write_batch("C1_baseline_reproduction_v2_vw", recs,
            {"note2":"Session-2 corrected methodology: true multi-walk van Oorschot-Wiener collision search (impl/rho.c run-vw, mode=0), replacing session-1's single-walk self-collision measurement which was a genuine sqrt(2) methodological mismatch against the 0.886*sqrt(n) convention. The original C1_baseline_reproduction batch is left in place, unmodified, as the immutable session-1 record; this is a NEW batch, not an edit."})

    if mode in ("all","c2"):
        recs=[]
        for size, c in CURVE_BY_SIZE.items():
            for seed in SEEDS_FULL:
                res, dt, err = run_rho(["run-oracle"]+curve_args(c)+
                    ["--seed",str(seed),"--dpbits","12","--budget-mult","64"], timeout=300)
                if res is None:
                    recs.append({"size":size,"seed":seed,"error":err}); continue
                res.update({"size":size,"seed":seed,"dp_bits":12,"wall_s":dt})
                recs.append(res)
        write_batch("C2_random_oracle_walk", recs)

    if mode in ("all","c3"):
        recs=[]
        for size, c in CURVE_BY_SIZE.items():
            for seed in SEEDS_FULL[:4]:
                for r in [8,20]:
                    res, dt, err = run_rho(["run"]+curve_args(c)+
                        ["--seed",str(seed),"--r",str(r),"--dpbits","12","--escape","none","--budget-mult","64"],
                        timeout=600)
                    if res is None:
                        recs.append({"size":size,"seed":seed,"r":r,"error":err}); continue
                    res.update({"size":size,"seed":seed,"r":r,"dp_bits":12,"escape":"none","wall_s":dt})
                    recs.append(res)
        write_batch("C3_no_escape_positive_control", recs)

    if mode in ("all","c3vw"):
        recs=[]
        for size, c in CURVE_BY_SIZE.items():
            for seed in SEEDS_FULL[:4]:
                for r in [8,20]:
                    res, dt, err = run_rho(["run-vw"]+curve_args(c)+
                        ["--seed",str(seed),"--r",str(r),"--dpbits","12","--mode","1","--escape","none","--budget-mult","64"],
                        timeout=600)
                    if res is None:
                        recs.append({"size":size,"seed":seed,"r":r,"error":err}); continue
                    res.update({"size":size,"seed":seed,"r":r,"dp_bits":12,"escape":"none","wall_s":dt})
                    recs.append(res)
        write_batch("C3_no_escape_positive_control_v2_vw", recs)

    if mode in ("all","c4"):
        c = CURVE_BY_SIZE[32]
        resc, dtc, errc = run_rho(["run"]+curve_args(c)+
            ["--seed","1","--r","8","--dpbits","12","--escape","det","--budget-mult","0.01"])
        pyres = subprocess.run(["python3", os.path.join(HERE,"rho_ref.py")]+curve_args(c)+
            ["--seed","1","--r","8","--dpbits","12","--escape","det","--budget-mult","0.01"],
            capture_output=True, text=True)
        py_json = json.loads(pyres.stdout.strip())
        agree = (resc == py_json)
        write_batch("C4_two_implementations", [{"c_impl":resc,"python_impl":py_json,"agree_exactly":agree}])
        print("C4 agree_exactly:", agree, file=sys.stderr)

    def run_grid(size, seeds, timeout, batch_name, extra_note=None, escapes=None, rvals=None, dpvals=None):
        # Writes INCREMENTALLY (append per cell) so a mid-run interruption
        # keeps whatever cells completed so far, rather than losing them
        # (session-2 lesson: an earlier grid40 attempt was killed mid-run and
        # its 120 already-computed cells were lost because the old version
        # only wrote at the very end -- disclosed in implementation.md).
        d = os.path.join(RUNS_DIR, batch_name)
        os.makedirs(d, exist_ok=True)
        jsonl_path = os.path.join(d, "raw-result.jsonl")
        c = CURVE_BY_SIZE[size]
        t0=time.time()
        n=0
        esc_list = escapes if escapes is not None else ESCAPE_SETTINGS
        r_list = rvals if rvals is not None else R_VALUES
        dp_list = dpvals if dpvals is not None else DP_BITS
        with open(jsonl_path, "a") as jf:
            for esc,k in esc_list:
                for r in r_list:
                    for dpb in dp_list:
                        for seed in seeds:
                            args = ["run-vw"]+curve_args(c)+["--seed",str(seed),"--r",str(r),
                                    "--dpbits",str(dpb),"--mode","1","--escape",esc,"--budget-mult","64"]
                            if k: args += ["--k",str(k)]
                            res, dt, err = run_rho(args, timeout=timeout)
                            n+=1
                            if res is None:
                                rec = {"escape":esc,"k":k,"r":r,"dp_bits":dpb,"seed":seed,"error":err}
                            else:
                                res.update({"escape":esc,"k":k,"r":r,"dp_bits":dpb,"seed":seed,"wall_s":dt})
                                rec = res
                            jf.write(json.dumps(rec)+"\n"); jf.flush()
                print(f"...size={size} done escape={esc} cumulative_n={n} elapsed={time.time()-t0:.1f}s", file=sys.stderr)
        man = {"batch": batch_name, "n_records": n, "subgroup_size_log2":size,
               "n_configs_x_seeds":n,"methodology":"vw_multiwalk_run-vw_mode1",
               "note": "Batched immutable run record, written incrementally per cell."}
        if extra_note: man["coverage_note"]=extra_note
        with open(os.path.join(d,"manifest.yaml"),"w") as f:
            import yaml
            yaml.safe_dump(man, f, sort_keys=False)
        print(f"wrote {n} records (incremental) -> {d}", file=sys.stderr)

    if mode in ("all","grid32"):
        run_grid(32, SEEDS_FULL, 120, "grid_size32_full_vw")

    if mode in ("grid40",):
        # First attempt at the FULL 9x5x3x4 factorial (540 cells) was killed
        # mid-run after ~28 minutes (only "none" and "det" -- 120 cells --
        # had completed; periodic's 5 k-sub-settings alone were pacing at
        # >600s each, projecting several more hours for the remaining 7
        # settings). Same disclosed reduction as L=48: skip escape=none
        # (redundant with the dedicated C3 control at this size), restrict to
        # dp_bits=8 (only granularity that resolved acceptably at L=32),
        # restrict r to {20,32} (best-resolving at L=32), 2 seeds. This
        # sacrifices exhaustiveness for actually finishing within session
        # time, matching the L=48 tradeoff for consistency across sizes.
        reduced_escapes = [e for e in ESCAPE_SETTINGS if e[0] != "none"]
        run_grid(40, SEEDS_FULL[:2], 300, "grid_size40_reduced_coverage_vw",
                  "SEVERE coverage reduction, disclosed: escape=none excluded (see C3 at L=40 instead), "
                  "dp_bits restricted to {8}, r restricted to {20,32}, 2 seeds (1,2) instead of 16. "
                  "A first full-factorial attempt (5r x 3dp x 4seed per escape setting) was killed after "
                  "~28 minutes; escape={none,det} (120 cells) had genuinely completed in-process but were "
                  "NOT persisted to disk (the run_grid version at that time wrote only at the very end, "
                  "since fixed to write incrementally -- see implementation.md). Those 120 cells' compute "
                  "is lost, not fabricated back; no grid_size40 directory existed before this batch.",
                  escapes=reduced_escapes, rvals=[20,32], dpvals=[8])

    if mode in ("grid48",):
        # L=48's escape=none cells alone cost ~130-200s EACH (measured directly:
        # a single such cell took >60s and did not finish; full budget is
        # 630M steps regardless of dp_bits since escape=none always runs to
        # the censoring cap). The L=32 grid showed 92% of ALL cells (not just
        # escape=none) end up >10% censored -- i.e. most cells at any size are
        # likely to run to a large fraction of the step budget. Running the
        # full 9-escape x 5-r x 3-dp x 4-seed factorial at L=48 (540 cells)
        # would cost multiple hours, which is not available in this session.
        # Disclosed coverage tradeoff (per Coordinator guidance: prioritize
        # breadth over exhaustive seeds/replication at this size): skip
        # escape=none here (already characterized at L=48 by C3's dedicated
        # control run); restrict to dp_bits=8 (the only granularity that
        # resolved with acceptable censoring at L=32); restrict to r in
        # {20,32} (the two best-resolving r values at L=32); 2 seeds instead
        # of 16 or even 4. This is a much smaller, honestly-labeled slice, not
        # a silent truncation.
        # SECOND cut: the first attempt at this reduced scope (8 non-none
        # settings x 2r x 1dp x 2seed = 32 cells) was itself too slow at
        # L=48's per-cell pace (~160s/cell observed for det and periodic
        # k=2) and was killed after det+periodic(k=2) (8 cells) -- lost
        # again because it predated the incremental-write fix (see
        # implementation.md). Cutting further to a genuinely tractable slice:
        # 4 representative escape settings (det, periodic at a single
        # mid-range k=8, lookahead, reselect) x r in {20,32} x dp_bits=8 x
        # 2 seeds = 16 cells. This is now written incrementally, so even a
        # further interruption preserves whatever completes.
        reduced_escapes = [("det",None), ("periodic",8), ("lookahead",None), ("reselect",None)]
        run_grid(48, SEEDS_FULL[:2], 400, "grid_size48_reduced_coverage_vw",
                  "SEVERE coverage reduction, disclosed, applied TWICE at this size (see implementation.md "
                  "for the full sequence of cuts): escape=none excluded (see C3 at L=48 instead); only 4 of "
                  "8 remaining escape settings run (det, periodic@k=8 only, lookahead, reselect -- periodic "
                  "at k in {2,4,16,32} NOT run at this size); dp_bits restricted to {8}; r restricted to "
                  "{20,32}; 2 seeds (1,2) instead of 16. This trades exhaustiveness for actually finishing "
                  "within session time; also, C1's blocking check fails at L=48 (see controls_analysis.json), "
                  "so any net_gain_ratio here is reported as raw data with that control status attached, not "
                  "as a blocking-cleared result.",
                  escapes=reduced_escapes, rvals=[20,32], dpvals=[8])

    print("DONE", mode, file=sys.stderr)
