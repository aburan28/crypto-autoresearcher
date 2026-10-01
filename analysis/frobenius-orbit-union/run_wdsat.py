#!/usr/bin/env python3
"""Build one WDSat binary per arm and solve the exported n = 19 instances.

Reports the solver's own conflict counter on refutation, which is the quantity
H-FROB-a5bf86 preregisters.  Every arm is solved by the same source at the same
commit, differing only in the static capacity its config.h declares.
"""
import argparse, json, re, shutil, subprocess, sys, time
from pathlib import Path

CONFIG = """#define __XG_ENHANCED__
#define __MAX_ANF_ID__ {anf_id}
#define __MAX_DEGREE__ {degree}
#define __MAX_ID__ {max_id}
#define __MAX_BUFFER_SIZE__ {buffer}
#define __MAX_EQ__ {eq}
#define __MAX_EQ_SIZE__ {eq_size}
#define __MAX_XEQ__ {xeq}
#define __MAX_XEQ_SIZE__ {xeq_size}
"""

def capacity_for(cap, scale=1):
    # every distinct monomial becomes an internal id, as do the declared variables
    ids = (cap['monomials'] + cap['n_vars'] + 64) * scale
    return dict(anf_id=cap['n_vars'] + 1, degree=cap['max_degree'] + 1, max_id=ids,
                buffer=max(4096, 40 * ids), eq=max(256, 8 * ids), eq_size=16,
                xeq=max(32, cap['rows'] + 16), xeq_size=ids + 1)

def build(source: Path, out: Path, cap: dict, scale=1) -> Path:
    if out.exists(): shutil.rmtree(out)
    shutil.copytree(source / 'src', out / 'src')
    (out / 'src' / 'config.h').write_text(CONFIG.format(**capacity_for(cap, scale)))
    subprocess.run(['make', '-C', 'src', 'clean'], cwd=out, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r = subprocess.run(['make', '-C', 'src'], cwd=out, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:], file=sys.stderr)
        raise SystemExit(f"build failed for {out}")
    binary = out / 'wdsat_solver'
    if not binary.exists(): raise SystemExit(f"no binary at {binary}")
    return binary

def build_fitting(source: Path, out: Path, cap: dict, probe: Path) -> Path:
    """Build, then grow the static capacity until the instance actually loads."""
    for scale in (1, 2, 4, 8):
        binary = build(source, out, cap, scale)
        r = subprocess.run([str(binary), '-i', str(probe)], capture_output=True, text=True)
        if r.returncode == 0:
            return binary
        if 'Assertion' not in r.stderr:
            print(r.stdout[-800:], r.stderr[-800:], file=sys.stderr)
            raise SystemExit(f"{out.name}: solver failed for a reason other than capacity")
    raise SystemExit(f"{out.name}: capacity still insufficient at scale 8")

CONF_RE = re.compile(r'^(\d+)$', re.M)

def solve(binary: Path, anf: Path, xg: bool, n_vars: int, order=None, timeout=300):
    cmd = [str(binary), '-i', str(anf)]
    if xg: cmd.append('-x')
    if order: cmd += ['-g', ','.join(map(str, order))]
    t0 = time.perf_counter()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    dt = time.perf_counter() - t0
    out = r.stdout
    if r.returncode != 0:
        return dict(unsat=False, sat=False, conflicts=None, seconds=dt, returncode=r.returncode,
                    capacity_warning=False, error=(r.stderr or out)[:200], stdout=out[:400], model=None)
    lines = [l.strip() for l in out.splitlines()]
    unsat = 'UNSAT' in out
    # a satisfied instance prints its assignment; on some paths without any 'SAT:' marker,
    # and a bare conflict count can also be all 0/1, so the model is found by length
    model_at, model = None, None
    for i, l in enumerate(lines):
        if l and set(l) <= {'0', '1'} and len(l) >= n_vars:
            model_at, model = i, l; break
    sat = (not unsat) and ('SAT:' in out or model is not None)
    conf = None
    m = re.search(r'conf:(\d+)', out)
    if m:
        conf = int(m.group(1))
    else:
        after = lines[model_at + 1:] if model_at is not None else lines
        tail = [int(x) for x in after if re.fullmatch(r'\d+', x)]
        if tail: conf = tail[-1]
        elif unsat: conf = 0   # refuted during XORGAUSS setup or initial propagation: no search
    warn = 'Running times are not optimal' in out
    return dict(unsat=bool(unsat), sat=bool(sat), conflicts=conf, seconds=dt,
                returncode=r.returncode, capacity_warning=warn, stdout=out[:400], model=model)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--anf', type=Path, required=True)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--timeout', type=float, default=300)
    ap.add_argument('--skip', default='', help='comma-separated arms to leave out')
    args = ap.parse_args()
    skip = {s for s in args.skip.split(',') if s}

    man = json.loads((args.anf / 'manifest.json').read_text())
    n, lp, B = man['n'], man['lprime'], man['B']
    t0 = man['instances'][0]['target']
    probe = {'single': args.anf / 'single' / f"t{t0:03d}_j00.anf",
             'onehot': args.anf / 'onehot' / f"t{t0:03d}.anf",
             'binary': args.anf / 'binary' / f"t{t0:03d}.anf"}
    binaries = {arm: build_fitting(args.source, args.work / arm, cap, probe[arm])
                for arm, cap in man['capacity'].items() if arm not in skip}
    print('built:', {k: str(v) for k, v in binaries.items()}, flush=True)

    shift_first = list(range(2 * lp + 1, 2 * lp + n + 1)) + list(range(1, 2 * lp + 1))
    results = []
    for inst in man['instances']:
        tix = inst['target']
        rec = dict(target=tix, xR=inst['xR'], gt_sat=inst['gt_sat'], arms={})
        for xg in (False, True):
            tag = 'xg' if xg else 'plain'
            if 'single' not in skip:
                acc = dict(conflicts=0, seconds=0.0, ok=True, any_sat=False)
                for j in range(n):
                    p = args.anf / 'single' / f"t{tix:03d}_j{j:02d}.anf"
                    r = solve(binaries['single'], p, xg, 2 * lp, timeout=args.timeout)
                    if r['conflicts'] is None: acc['ok'] = False
                    acc['any_sat'] = acc['any_sat'] or r['sat']
                    acc['conflicts'] += r['conflicts'] or 0
                    acc['seconds'] += r['seconds']
                # the n systems refute the target exactly when the target does not decompose
                acc['ok'] = acc['ok'] and (acc['any_sat'] == inst['gt_sat'])
                rec['arms'][f'single_{tag}'] = acc
            nv = {'onehot': 2 * lp + n, 'binary': 2 * lp + B}
            for arm, order in (('onehot', None), ('onehot', shift_first), ('binary', None)):
                if arm in skip: continue
                p = args.anf / arm / f"t{tix:03d}.anf"
                r = solve(binaries[arm], p, xg, nv[arm], order=order, timeout=args.timeout)
                key = f"{arm}{'_shiftfirst' if order else ''}_{tag}"
                rec['arms'][key] = dict(conflicts=r['conflicts'], seconds=r['seconds'],
                                        ok=(r['conflicts'] is not None and r['sat'] == inst['gt_sat']),
                                        warn=r['capacity_warning'],
                                        stdout=r.get('error') or (r['stdout'] if r['conflicts'] is None else None))
        results.append(rec)
        print(json.dumps(rec), flush=True)
    args.out.write_text(json.dumps(dict(meta=man['capacity'] | {'n': n}, results=results), indent=2))

    keys = list(results[0]['arms'].keys())
    print("\n%-28s %12s %12s %9s" % ('arm', 'conflicts', 'seconds', 'verdicts'))
    for k in keys:
        vals = [r['arms'][k] for r in results if r['arms'][k].get('conflicts') is not None]
        okc = sum(1 for r in results if r['arms'][k].get('ok'))
        if not vals: print("%-28s %12s %12s %9s" % (k, 'n/a', 'n/a', f"{okc}/{len(results)}")); continue
        print("%-28s %12.1f %12.4f %9s" % (k, sum(v['conflicts'] for v in vals) / len(vals),
                                           sum(v['seconds'] for v in vals) / len(vals),
                                           f"{okc}/{len(results)}"))

if __name__ == '__main__':
    main()
