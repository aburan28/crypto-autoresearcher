"""Hybrid sweep: guess g of the five unknowns and record F4 degrees of the specialised systems.

Usage: python3 run_hybrid.py OUTDIR SAGE_PYTHON MSOLVE TIMEOUT_S GRID_JSON
GRID_JSON: {"ks": [...], "gs": [1, 2], "arms": ["mult"], "cells": [["planted", "true"], ["planted", "wrong"], ["random", "wrong"]], "seeds": [1]}
Runs one job at a time (F4 memory is the binding resource). Appends to OUTDIR/results.jsonl.
"""
import json, os, subprocess, sys
from run_sweep import PRIMES, HERE, run_msolve

def one(outdir, sage_py, msolve, timeout, arm, k, g, inst, guess, seed):
    tag = f'{arm}_circuit_k{k}_g{g}_{inst}_{guess}_s{seed}'
    base = os.path.join(outdir, 'runs', tag)
    rec = dict(arm=arm, enc='circuit', k=k, g=g, inst=inst, guess=guess, seed=seed, p=PRIMES[arm], tag=tag)
    b = subprocess.run([sage_py, os.path.join(HERE, 'hybrid.py'), arm, str(k), str(PRIMES[arm]), inst, str(seed),
                        'circuit', str(g), guess, base], capture_output=True, text=True, timeout=3600, cwd=HERE)
    if b.returncode != 0:
        rec.update(status='build_failed', error=b.stderr[-400:]); return rec
    meta = json.load(open(base + '.json'))
    rec.update({x: meta[x] for x in ['nvars', 'neqs', 'fb_size_x', 'fb_points', 'witness_checked', 'fixed', 'fixed_values']})
    return run_msolve(base, msolve, timeout, rec)

def main():
    outdir, sage_py, msolve, timeout, grid = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), json.loads(sys.argv[5])
    os.makedirs(os.path.join(outdir, 'runs'), exist_ok=True)
    dead = set()  # (g, inst, guess) that failed to complete at a smaller k
    with open(os.path.join(outdir, 'results.jsonl'), 'a') as fh:
        for k in grid['ks']:
            for g in grid['gs']:
                for arm in grid.get('arms', ['mult']):
                    for inst, guess in grid['cells']:
                        for seed in grid.get('seeds', [1]):
                            key = (arm, g, inst, guess)
                            if key in dead:
                                rec = dict(arm=arm, enc='circuit', k=k, g=g, inst=inst, guess=guess, seed=seed,
                                           p=PRIMES[arm], tag=f'{arm}_circuit_k{k}_g{g}_{inst}_{guess}_s{seed}',
                                           status='skipped_smaller_k_incomplete')
                            else:
                                rec = one(outdir, sage_py, msolve, timeout, arm, k, g, inst, guess, seed)
                                if rec.get('status') != 'ok':
                                    dead.add(key)
                            fh.write(json.dumps(rec) + '\n'); fh.flush()
                            print(rec['tag'], rec.get('status'), rec.get('nvars'), rec.get('dmax'), rec.get('outcome'),
                                  rec.get('n_solutions'), rec.get('wall_s'), rec.get('maxrss_kb'), flush=True)

if __name__ == '__main__':
    main()
