"""Representative sweep of one-level (split_build.py) and two-level (split2_build.py) sign-pattern guesses.

Usage: python3 run_split_queue.py OUTDIR SAGE_PYTHON MSOLVE TIMEOUT_S KS_JSON
For each k (ascending), one job at a time:
  one-level  planted: true m, true m - 1, true m + 1 (wrong);   random T: m = 3, m = 0
  two-level  planted: true composition, a rearrangement of it (wrong), a composition of another shape (wrong);
             random T: the planted true composition and (1, 1, 1, 3)
The true m / composition is read from a probe build of the planted instance. A role that times out or is
killed at some k is skipped at larger k. Appends one JSON line per job to OUTDIR/results.jsonl; a rerun with
the same OUTDIR resumes after the last recorded job (the container may restart mid-sweep).
"""
import json, os, subprocess, sys
from run_sweep import PRIMES, HERE, run_msolve

P = PRIMES['mult']


def build(sage_py, builder, k, inst, guess, base):
    arg = guess if isinstance(guess, int) else ','.join(map(str, guess))
    script = 'split_build.py' if builder == 'split1' else 'split2_build.py'
    b = subprocess.run([sage_py, os.path.join(HERE, script), str(k), str(P), inst, '1', str(arg), base],
                       capture_output=True, text=True, timeout=3600, cwd=HERE)
    if b.returncode != 0:
        return None, b.stderr[-400:]
    return json.load(open(base + '.json')), None


def rearrange(comp):
    """A different ordering of the same parts (wrong whenever the parts are not all equal)."""
    for shift in (1, 2, 3):
        c = comp[shift:] + comp[:shift]
        if c != comp:
            return c
    return [comp[1], comp[0], comp[3], comp[2]]


def other_shape(comp, k):
    for c in ([1, 1, 1, 3], [2, 2, 1, 1], [3, 3, 0, 0], [2, 1, 2, 1], [4, 2, 0, 0]):
        if sorted(c) != sorted(comp) and max(c) <= 2 ** (k - 2):
            return c


def main():
    outdir, sage_py, msolve, timeout, ks = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), json.loads(sys.argv[5])
    os.makedirs(os.path.join(outdir, 'runs'), exist_ok=True)
    dead = set()
    done = {}  # resume: jobs already recorded in results.jsonl are not rerun
    rp = os.path.join(outdir, 'results.jsonl')
    if os.path.exists(rp):
        for line in open(rp):
            r = json.loads(line); done[r['tag']] = r
    with open(rp, 'a') as fh:
        for k in ks:
            probe, err = build(sage_py, 'split2', k, 'planted', [1, 1, 1, 3], os.path.join(outdir, 'runs', f'probe_k{k}'))
            comp = probe['true_comp']
            p1, _ = build(sage_py, 'split1', k, 'planted', 0, os.path.join(outdir, 'runs', f'probe1_k{k}'))
            m_true = p1['true_m']  # number of planted roots on split_build's '+s' side
            jobs = [('split1', 'planted', 'true', m_true)]
            jobs += [('split1', 'planted', 'wrong_minus', m_true - 1)] if m_true - 1 >= 0 else []
            jobs += [('split1', 'planted', 'wrong_plus', m_true + 1)] if m_true + 1 <= 6 else []
            jobs += [('split1', 'random', 'rand_m3', 3), ('split1', 'random', 'rand_m0', 0)]
            jobs += [('split2', 'planted', 'true', comp), ('split2', 'planted', 'wrong_rearranged', rearrange(comp)),
                     ('split2', 'planted', 'wrong_other_shape', other_shape(comp, k)),
                     ('split2', 'random', 'rand_truecomp', comp), ('split2', 'random', 'rand_1113', [1, 1, 1, 3])]
            for builder, inst, role, guess in jobs:
                label = guess if isinstance(guess, int) else ''.join(map(str, guess))
                tag = f'mult_{builder}_k{k}_{role}_{label}_{inst}_s1'
                rec = dict(arm='mult', enc=builder, k=k, inst=inst, role=role, guess=guess, p=P, tag=tag)
                if tag in done:
                    rec = done[tag]
                    if rec.get('status') == 'timeout' or str(rec.get('status')).startswith('exit_'):
                        dead.add((builder, role))
                    continue
                if (builder, role) in dead:
                    rec['status'] = 'skipped_smaller_k_incomplete'
                else:
                    base = os.path.join(outdir, 'runs', tag)
                    meta, err = build(sage_py, builder, k, inst, guess, base)
                    if meta is None:
                        rec.update(status='build_failed', error=err)
                    else:
                        rec.update({x: meta.get(x) for x in ['nvars', 'neqs', 'maxdeg', 'true_m', 'true_comp', 'witness_checked']})
                        rec = run_msolve(base, msolve, timeout, rec)
                        if rec.get('status') == 'timeout' or str(rec.get('status')).startswith('exit_'):
                            dead.add((builder, role))
                fh.write(json.dumps(rec) + '\n'); fh.flush()
                print(rec['tag'], rec.get('status'), rec.get('nvars'), rec.get('dmax'), rec.get('outcome'),
                      rec.get('n_solutions'), rec.get('wall_s'), rec.get('maxrss_kb'), flush=True)


if __name__ == '__main__':
    main()
