"""Sweep k for the six-point Riemann-Roch / 2-adic-chain system and record F4 degrees.

Usage: python3 run_sweep.py OUTDIR SAGE_PYTHON MSOLVE TIMEOUT_S JOBS [GRID_JSON]
GRID_JSON (optional) overrides the grid: {"ks": {"circuit": [4, 5]}, "arms": [...], "insts": [...], "seeds": [...]}
Appends one JSON line per (arm, k, encoding, instance, seed) to OUTDIR/results.jsonl
and keeps every msolve input and log under OUTDIR/runs/.
"""
import itertools, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

PRIMES = {'mult': 268496897, 'dickson': 268562431}   # 2^12 | p-1, 2^12 | p+1
KS = {'circuit': range(3, 11), 'direct': range(3, 7)}
SEEDS = [1, 2, 3]
INSTS = ['planted', 'random']
HERE = os.path.dirname(os.path.abspath(__file__))

def parse_log(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r'\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+) x (\d+)\s', line)
        if m:
            rows.append([int(m.group(i)) for i in range(1, 6)])
    return rows

def outcome(path):
    try:
        s = open(path).read()
    except OSError:
        return None, None
    if s.startswith('[-1]'):
        return 'inconsistent', 0
    m = re.match(r'\[0, \[(\d+),\s*(\d+),\s*(\d+),', s)
    if m:
        return 'solutions', int(m.group(3))
    if s.startswith('[1,'):
        return 'positive_dimensional', None
    return 'unparsed', None

def one(args):
    outdir, sage_py, msolve, timeout, arm, enc, k, inst, seed = args
    tag = f'{arm}_{enc}_k{k}_{inst}_s{seed}'
    base = os.path.join(outdir, 'runs', tag)
    rec = dict(arm=arm, enc=enc, k=k, inst=inst, seed=seed, p=PRIMES[arm], tag=tag)
    b = subprocess.run([sage_py, os.path.join(HERE, 'build_systems.py'), arm, str(k), str(PRIMES[arm]), inst,
                        str(seed), enc, base], capture_output=True, text=True, timeout=3600)
    if b.returncode != 0:
        rec.update(status='build_failed', error=b.stderr[-400:]); return rec
    meta = json.load(open(base + '.json'))
    rec.update({x: meta[x] for x in ['nvars', 'neqs', 'maxdeg', 'fb_size_x', 'fb_points', 'witness_checked']})
    return run_msolve(base, msolve, timeout, rec)

def run_msolve(base, msolve, timeout, rec):
    """Run msolve on base.ms with a wall-clock limit; record F4 trace, resources and outcome in rec."""
    status = None
    t0 = time.time()
    with open(base + '.log', 'w') as lf:
        pr = subprocess.Popen([msolve, '-v', '2', '-f', base + '.ms', '-o', base + '.out'],
                              stdout=lf, stderr=subprocess.STDOUT)
        timed_out = False
        while True:  # reap with wait4 to keep the child's rusage
            pid, st, ru = os.wait4(pr.pid, os.WNOHANG)
            if pid:
                break
            if time.time() - t0 > timeout and not timed_out:
                pr.kill(); timed_out = True
            time.sleep(0.2)
        pr.returncode = os.waitstatus_to_exitcode(st)
        rec['cpu_s'] = round(ru.ru_utime + ru.ru_stime, 3); rec['maxrss_kb'] = ru.ru_maxrss
        status = 'timeout' if timed_out else ('ok' if pr.returncode == 0 else f'exit_{pr.returncode}')
    rec['wall_s'] = round(time.time() - t0, 3)
    log = open(base + '.log').read()
    steps = parse_log(log)
    rec['status'] = status
    rec['f4_degrees'] = [s[0] for s in steps]
    rec['dmax'] = max(rec['f4_degrees']) if steps else None
    # a step whose pairs were selected but whose matrix never finished (killed or timed out)
    pend = [int(m.group(1)) for m in re.finditer(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s*$', log, re.M)]
    rec['deg_entered_at_stop'] = pend[-1] if (pend and status != 'ok') else None
    rec['max_matrix'] = max(((s[3], s[4]) for s in steps), key=lambda t: t[0] * t[1]) if steps else None
    rec['outcome'], rec['n_solutions'] = outcome(base + '.out') if status == 'ok' else (None, None)
    return rec

def main():
    outdir, sage_py, msolve, timeout, jobs = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    os.makedirs(os.path.join(outdir, 'runs'), exist_ok=True)
    global KS, SEEDS, INSTS
    arms = list(PRIMES)
    if len(sys.argv) > 6:
        g = json.loads(sys.argv[6])
        KS = {e: list(v) for e, v in g.get('ks', KS).items()}
        arms = g.get('arms', arms); INSTS = g.get('insts', INSTS); SEEDS = g.get('seeds', SEEDS)
    dead = set()  # (arm, enc) whose every run at the previous k timed out
    with open(os.path.join(outdir, 'results.jsonl'), 'a') as fh, ThreadPoolExecutor(jobs) as ex:
        for k in sorted({k for v in KS.values() for k in v}):
            tasks, skipped = [], []
            for enc in ['circuit', 'direct']:
                if k not in KS.get(enc, ()):
                    continue
                for arm in arms:
                    for inst in INSTS:
                        for seed in SEEDS:
                            t = (outdir, sage_py, msolve, timeout, arm, enc, k, inst, seed)
                            (skipped if (arm, enc) in dead else tasks).append(t)
            recs = list(ex.map(one, tasks))
            recs += [dict(arm=t[4], enc=t[5], k=t[6], inst=t[7], seed=t[8], p=PRIMES[t[4]],
                          tag=f'{t[4]}_{t[5]}_k{t[6]}_{t[7]}_s{t[8]}', status='skipped_prior_k_all_timeout')
                     for t in skipped]
            for rec in recs:
                fh.write(json.dumps(rec) + '\n'); fh.flush()
                print(rec['tag'], rec.get('status'), rec.get('dmax'), rec.get('outcome'), rec.get('n_solutions'),
                      rec.get('wall_s'), flush=True)
            for arm in PRIMES:
                for enc in KS:
                    rs = [r for r in recs if r['arm'] == arm and r['enc'] == enc]
                    if rs and all(r['status'] in ('timeout', 'skipped_prior_k_all_timeout') for r in rs):
                        dead.add((arm, enc))

if __name__ == '__main__':
    main()
