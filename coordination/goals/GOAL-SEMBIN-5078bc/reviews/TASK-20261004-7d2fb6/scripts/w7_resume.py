#!/usr/bin/env python3
"""w7_resume.py -- joint W7 (5): kill a closure with SIGKILL after its k-th checkpoint, resume it (same ckpt dir, optionally a
different memory cap, optionally killed again), and compare the final record with an uninterrupted run. Also run on the resume
mutants ME / MI to show the harness can see a resume defect. Scratch. Uses the checkpoint header layout of closure.c ckpt_hdr
(magic,hash,ncols,ngens,hist_n,N,D,max_iter,it,md,iters,a,mi,total_new_piv,n_new,n_prod,total_rows,rank,max_rows_seen,dropped).
Usage: w7_resume.py OUT.jsonl STEM VARIANT CAP K1[,K2,...] [RESUME_CAP]   (kills after the K1-th checkpoint state, then K2-th of the next run, ...)"""
import sys, os, json, subprocess, struct, glob, time, shutil, signal
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
out, stem, variant, cap, ks = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), [int(x) for x in sys.argv[5].split(",")]
rcap = float(sys.argv[6]) if len(sys.argv) > 6 else cap
lib = f"{W}/build/libclosure_orig.so" if variant == "orig" else f"{W}/mut/libclosure_{variant}.so"
job = ["python3", f"{WS}/scripts/w5_worker.py", lib, f"{W}/inst/{stem}.json", "4"]
HDR = struct.Struct("<QQqqqiiiiiiqqqqqqqqq")   # 8+8+3*8 + 6*4 + 9*8 ... see below
def read_state(path):
    try:
        b = open(path, "rb").read(136)
        if len(b) < 136: return None
        magic, h, ncols, ngens, hist_n, N, D, mi_, it, md, iters = struct.unpack_from("<QQqqqiiiiii", b, 0)
        a, mi, tnp, n_new, n_prod, total_rows, rank, mrs = struct.unpack_from("<qqqqqqqq", b, 64)
        return (it, a, md, mi), {"it": it, "a": a, "md": md, "mi": mi, "n_new": n_new, "rank": rank}
    except Exception:
        return None

def baseline():
    r = subprocess.run(job + [str(cap)], capture_output=True, text=True, env={**os.environ, "CLOSURE_CKPT_DIR": ""})
    return json.loads(r.stdout.strip().splitlines()[-1])

def run_with_kills():
    d = f"{W}/ckpt_{stem}_{variant}_{'_'.join(map(str, ks))}"
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    env = {**os.environ, "CLOSURE_CKPT_DIR": d}
    states = []
    for n, k in enumerate(ks):
        p = subprocess.Popen(job + [str(cap if n == 0 else rcap)], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        seen = set(); killed = False; t0 = time.time()
        while p.poll() is None:
            for f in glob.glob(f"{d}/ckpt.*.bin"):
                st = read_state(f)
                if st and st[0] not in seen:
                    seen.add(st[0])
                    if len(seen) >= k:
                        os.kill(p.pid, signal.SIGKILL); p.wait(); killed = True; states.append({"after_checkpoint_states": len(seen), **st[1]}); break
            if killed: break
            time.sleep(0.0005)
            if time.time() - t0 > 600: os.kill(p.pid, signal.SIGKILL); break
        if not killed:
            outp = p.stdout.read(); states.append({"finished_before_kill": True, "after_checkpoint_states": len(seen)})
            return states, (json.loads(outp.strip().splitlines()[-1]) if outp.strip() else None), d
    p = subprocess.run(job + [str(rcap)], env=env, capture_output=True, text=True)
    return states, json.loads(p.stdout.strip().splitlines()[-1]), d

base = baseline()
states, fin, d = run_with_kills()
keys = ("rank", "std", "lm_sha256", "contains_one", "ncols", "profile")
rec = {"stem": stem, "variant": variant, "cap": cap, "resume_cap": rcap, "kills_at_checkpoint_state": ks, "kill_states": states, "baseline": {k: base.get(k) for k in keys + ("batches",)},
       "resumed_run": ({k: fin.get(k) for k in keys + ("resumed", "batches")} if fin else None)}
if fin:
    rec["equal"] = {k: base.get(k) == fin.get(k) for k in keys}
    rec["profile_final_iterations_equal"] = base["profile"][-1] == fin["profile"][-1]
    rec["all_equal"] = all(rec["equal"].values())
shutil.rmtree(d, ignore_errors=True)
open(out, "a").write(json.dumps(rec) + "\n")
eq = rec.get("equal")
print(f"{stem:28s} {variant:5s} cap={cap:<8g} rcap={rcap:<8g} kills={ks} at {[ (s.get('it'),s.get('a'),s.get('md'),s.get('mi')) for s in states]} resumes={fin.get('resumed') if fin else None} -> "
      f"rank {base['rank']} vs {fin.get('rank') if fin else None}; std {base['std']} vs {fin.get('std') if fin else None}; lm_sha equal={eq and eq['lm_sha256']}; ALL EQUAL={rec.get('all_equal')}", flush=True)
