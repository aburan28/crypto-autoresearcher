"""Sign-pattern split sweep: for each k and instance, solve the split system for every m = 0..6.

Usage: python3 run_split.py OUTDIR SAGE_PYTHON MSOLVE TIMEOUT_S GRID_JSON
GRID_JSON: {"ks": [4, 5, 6, 7], "insts": ["planted", "random"], "ms": [0, 1, 2, 3, 4, 5, 6], "seeds": [1]}
One job at a time. Appends one JSON line per (k, inst, seed, m) to OUTDIR/results.jsonl. An (inst, m) cell that
times out or is killed at some k is skipped at larger k.
"""
import json, os, subprocess, sys
from run_sweep import PRIMES, HERE, run_msolve

P = PRIMES['mult']

def one(outdir, sage_py, msolve, timeout, k, inst, seed, m):
    tag = f'mult_split_k{k}_m{m}_{inst}_s{seed}'
    base = os.path.join(outdir, 'runs', tag)
    rec = dict(arm='mult', enc='split', k=k, m=m, inst=inst, seed=seed, p=P, tag=tag)
    b = subprocess.run([sage_py, os.path.join(HERE, 'split_build.py'), str(k), str(P), inst, str(seed), str(m), base],
                       capture_output=True, text=True, timeout=3600, cwd=HERE)
    if b.returncode != 0:
        rec.update(status='build_failed', error=b.stderr[-400:]); return rec
    meta = json.load(open(base + '.json'))
    rec.update({x: meta[x] for x in ['nvars', 'neqs', 'maxdeg', 'true_m', 'witness_checked']})
    return run_msolve(base, msolve, timeout, rec)

def main():
    outdir, sage_py, msolve, timeout, grid = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), json.loads(sys.argv[5])
    os.makedirs(os.path.join(outdir, 'runs'), exist_ok=True)
    dead = set()
    with open(os.path.join(outdir, 'results.jsonl'), 'a') as fh:
        for k in grid['ks']:
            for inst in grid.get('insts', ['planted', 'random']):
                for seed in grid.get('seeds', [1]):
                    for m in grid.get('ms', range(7)):
                        if (inst, m) in dead:
                            rec = dict(arm='mult', enc='split', k=k, m=m, inst=inst, seed=seed, p=P,
                                       tag=f'mult_split_k{k}_m{m}_{inst}_s{seed}', status='skipped_smaller_k_incomplete')
                        else:
                            rec = one(outdir, sage_py, msolve, timeout, k, inst, seed, m)
                            if rec.get('status') == 'timeout' or str(rec.get('status')).startswith('exit_'):
                                dead.add((inst, m))
                        fh.write(json.dumps(rec) + '\n'); fh.flush()
                        print(rec['tag'], rec.get('status'), rec.get('true_m'), rec.get('nvars'), rec.get('dmax'),
                              rec.get('outcome'), rec.get('n_solutions'), rec.get('wall_s'), rec.get('maxrss_kb'), flush=True)

if __name__ == '__main__':
    main()
