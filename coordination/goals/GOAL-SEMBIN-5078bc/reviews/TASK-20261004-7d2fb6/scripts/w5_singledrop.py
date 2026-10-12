#!/usr/bin/env python3
"""w5_singledrop.py -- joint W5 (2)(3)(4): drop exactly ONE product (mutant MJ) at many positions and ask three questions of each
variant: (A) did the closure outcome (rank, LM list, standard count) leave the reference closure? (B) does my independent
saturation verifier flag it? (C) does the PRODUCER'S OWN cross-check procedure flag it (a second elimination routine,
mzd_echelonize, at a different memory cap, plus the evaluation check at a verified common zero)?
Usage: w5_singledrop.py OUT.jsonl STEM IT NPOS CAP_RECORD CAP_XCHECK [seed] [LEN]     (D = 4; LEN consecutive products dropped at each position, default 1)
Everything runs in fresh child processes via child mode: w5_singledrop.py --child ...  . SCRATCH, TASK-20261004-7d2fb6."""
import sys, os, json, subprocess, random, tempfile
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
sys.path.insert(0, f"{WS}/scripts")

def child():
    import vclos, ctypes
    mode, lib, stem, it, p, cap, rows_out, method, witness, LEN = sys.argv[2:12]
    s = json.load(open(f"{W}/inst/{stem}.json"))
    c = vclos.Clos(lib)
    if int(it) >= 0:
        c.L.closure_mut_skip.argtypes = [ctypes.c_int, ctypes.c_long, ctypes.c_long]; c.L.closure_mut_skip(int(it), int(p), int(LEN))
    if mode == "xcheck":
        c.L.closure_set_witness(int(witness)); c.L.closure_set_method(int(method))
    saved = os.dup(2); tf = tempfile.TemporaryFile(); os.dup2(tf.fileno(), 2)
    try:
        r = c.run(s["N"], 4, s["equations"], mem_cap_gb=float(cap), want_rows=(rows_out != "-"))
    finally:
        os.dup2(saved, 2)
    out = {k: v for k, v in r.items() if k not in ("rows", "lm")}
    if mode == "xcheck":
        a, b, d = ctypes.c_long(), ctypes.c_long(), ctypes.c_long()
        c.L.closure_ech_stats(ctypes.byref(a), ctypes.byref(b), ctypes.byref(d))
        out["ech_calls"], out["evalcheck_bad_calls"] = a.value, b.value
    if "lm" in r: out["lm"] = r["lm"]
    if rows_out != "-" and "rows" in r: vclos.write_rows_bin(r["rows"], rows_out)
    print(json.dumps(out))

def run_child(mode, lib, stem, it, p, cap, rows_out="-", method=1, witness=0, LEN=1):
    r = subprocess.run(["python3", __file__, "--child", mode, lib, stem, str(it), str(p), str(cap), rows_out, str(method), str(witness), str(LEN)], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-500:])
    return json.loads(r.stdout.strip().splitlines()[-1])

def main():
    out, stem, it, npos, cap_rec, cap_x = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
    seed = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    LEN = int(sys.argv[8]) if len(sys.argv) > 8 else 1
    s = json.load(open(f"{W}/inst/{stem}.json")); V = s["V"]
    from math import comb
    ncols = sum(comb(s["N"], d) for d in range(5))
    st = dict(kv.split("=") for kv in open(f"{W}/ref/{stem}.D4.stats").read().split())
    ref_rank, ref_std = int(st["rank"]), int(st["std"]); ref_lm = [int(x) for x in open(f"{W}/ref/{stem}.D4.lm").read().split()]
    # a verified zero (truth table, independent of every instrument)
    sys.path.insert(0, f"{WS}/scripts"); import gen_small
    ok = gen_small.zeros_count(s["N"], s["equations"])[1]
    import numpy as np
    zeros = np.nonzero(ok)[0]; witness = int(zeros[0]) if len(zeros) else None
    # unmutated profile -> number of products in iteration IT
    base = run_child("plain", f"{W}/build/libclosure_orig.so", stem, -1, -1, cap_rec)
    prof = base["profile"]
    if it >= len(prof): print("iteration", it, "does not exist; profile", prof); return
    rank_before = prof[it - 1][1]
    nprod = prof[it][0] - rank_before
    print(f"{stem}: V={V} ref rank {ref_rank} std {ref_std} iterations {len(prof)} profile {prof}; iteration {it} has {nprod} products; witness={witness}", flush=True)
    rng = random.Random(seed)
    Ps = sorted({0, max(0, nprod - LEN), nprod // 2} | {rng.randrange(max(1, nprod - LEN + 1)) for _ in range(max(0, npos - 3))})
    fh = open(out, "a")
    # control: the UNMUTATED procedure must not flag (same instance)
    for P in [-1] + Ps:
        rec = {"stem": stem, "iteration": it, "P": P, "LEN": LEN, "nprod_in_iteration": nprod, "V": V, "witness": witness, "cap_record": cap_rec, "cap_xcheck": cap_x}
        lib_plain = f"{W}/build/libclosure_orig.so" if P < 0 else f"{W}/mut/libclosure_MJ.so"
        lib_ev = f"{W}/build/libclosure_orig_evalcheck.so" if P < 0 else f"{W}/mut/libclosure_MJ_ev.so"
        itx = -1 if P < 0 else it
        rows = f"{W}/rows_sd_{stem}.bin" if s["N"] <= 22 else "-"
        a = run_child("plain", lib_plain, stem, itx, P, cap_rec, rows, LEN=LEN)
        lm = a["lm"] if "lm" in a else []
        rec["record"] = {"rank": a["rank"], "std": a["std"], "lm_sha256": a["lm_sha256"], "profile": a["profile"], "contains_one": a["contains_one"]}
        rec["outcome_changed"] = (a["rank"] != ref_rank) or (a["std"] != ref_std) or (lm != ref_lm)
        if rows != "-" and os.path.exists(rows):
            q = subprocess.run([f"{W}/refclos", "saturate", f"{W}/inst/{stem}.sys", "4", rows], capture_output=True, text=True).stdout.strip()
            kv = dict(x.split("=") for x in q.split()); rec["verifier_violations"] = int(kv["saturation_violations"]); rec["verifier_flags"] = rec["verifier_violations"] > 0
            os.remove(rows)
        # producer's cross-check procedure (needs a witness): second routine (mzd_echelonize = method 0), other cap, evalcheck at the zero
        if witness is not None:
            b = run_child("xcheck", lib_ev, stem, itx, P, cap_x, "-", 0, witness, LEN=LEN)
            rec["xcheck"] = {"rank": b["rank"], "std": b["std"], "lm_sha256": b["lm_sha256"], "profile": b["profile"], "evalcheck_bad_calls": b["evalcheck_bad_calls"], "ech_calls": b["ech_calls"], "rc": b["rc"]}
            diffs = [k for k in ("rank", "std", "lm_sha256", "profile") if rec["xcheck"][k] != rec["record"][k]]
            rec["xcheck_disagreements"] = diffs
            rec["producer_procedure_flags"] = bool(diffs) or b["evalcheck_bad_calls"] > 0
        fh.write(json.dumps(rec) + "\n"); fh.flush()
        print(f"  P={P:>7} outcome_changed={rec['outcome_changed']!s:5} verifier_flags={rec.get('verifier_flags')} producer_procedure_flags={rec.get('producer_procedure_flags')} "
              f"(record rank {rec['record']['rank']}, std {rec['record']['std']}; xcheck diffs {rec.get('xcheck_disagreements')}; evalcheck bad {rec.get('xcheck', {}).get('evalcheck_bad_calls')})", flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child": child()
    else: main()
