#!/usr/bin/env python3
"""Run certified-data 2-descent, retain every attempt and honest bounds."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import platform
import resource
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

GP = '/workspace/solinas-runtime/pari/usr/bin/gp'
LIB = '/workspace/solinas-runtime/pari/usr/lib/x86_64-linux-gnu'
RUN = Path(__file__).resolve().parent.parent
SRC = RUN / 'source'

def stamp():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')

def polynomial(coeffs):
    return '+'.join(f'({c})*y^{i}' for i, c in enumerate(coeffs) if c)

def prelude(high_degree=False):
    lines = ['default(realprecision,80);default(parisizemax,2000000000);default(nbthreads,1);']
    for name in ['ellQ.gp', 'ell-certified.gp', 'qfsolve.gp', 'resultant3.gp']:
        lines.append(f'read("{SRC / name}");')
    lines += [
        f'CERTIFY_ALL={0 if high_degree else 1};',
        'rank_bnfinit(P,flag=1)={my(B,C);print("@@BNF_START|",poldegree(P),"|",P);B=bnfinit(P,flag);if(CERTIFY_ALL || poldegree(P)<=12,C=bnfcertify(B);if(C!=1,error("BNF certification failed"));print("@@CERT_OK|",poldegree(P),"|",P),print("@@UNCERT_BNF|",poldegree(P),"|",P));B};',
        'DEBUGLEVEL_ell=0;MAXPROB=100;LIMBIGPRIME=31;setrand(1);',
    ]
    return '\n'.join(lines) + '\n'

def script(job, rational):
    A, B = job['A'], job['B']
    model = f'[0,0,0,{A},{B}]'
    high = not rational and job.get('degree', len(job['g']) - 1) > 3
    lines = [prelude(high), '{rank_main()=', f'my(Eq=ellinit({model}),QR,BN,NR,T,RP,EK);',
             'QR=ellrank(Eq,2);print("@@Q_BOUND|",QR[1],"|",QR[2]);print("@@Q_RAW|",QR);',
             'if(QR[1]!=QR[2],QR=ellrank(Eq,5,QR[4]);print("@@Q_BOUND|",QR[1],"|",QR[2]);print("@@Q_RAW|",QR));']
    if not rational:
        poly = polynomial(job['g'])
        lines += [f'BN=rank_bnfinit({poly},1);',
                  f'T=#nfroots(BN,x^3+({A})*x+({B}));',
                  'if(T!=0 && T!=1 && T!=3,error("Unexpected root count"));',
                  'T=if(T==3,2,if(T==1,1,0));print("@@TORSION_DIM|",T);',
                  f'EK=ellinit({model},BN);RP=QR[4];']
        lines += [f'LIM1={0 if high else 2};LIM3={0 if high else 2};']
        for effort, limit in enumerate([0] if high else [2, 4]):
            if effort:
                lines.append('if(NR[1]<NR[2]-T,')
            lines += [f'LIMTRIV={limit};print("@@DESCENT_START|",LIMTRIV);',
                      f'if(T,print("@@BOUND_METHOD|two-isogeny-S-unit-bound");NR=[0,2*#bnfpSelmer(BN,6*EK.disc,2)[1]-2+T,[]],NR=bnfellrank(BN,{model},RP));',
                      'for(i=1,#NR[3],if(!ellisoncurve(EK,NR[3][i]),error("Point failed curve equation")));',
                      'print("@@NF_BOUND|",LIMTRIV,"|",NR[1],"|",NR[2],"|",T);',
                      'print("@@NF_RAW|",NR);RP=NR[3];']
            if effort:
                lines.append(');')
    lines += ['};', 'iferr(rank_main(),err,print("@@ERROR|",err));', 'print("@@DONE");quit;']
    return '\n'.join(lines) + '\n'

def parse(stdout, stderr, rational):
    q, nf, certs, errors, uncertified = [], [], [], [], []
    points = []
    for line in stdout.splitlines():
        if line.startswith('@@Q_BOUND|'):
            _, low, up = line.split('|')
            q.append([int(low), int(up)])
        elif line.startswith('@@NF_BOUND|'):
            _, lim, low, selmer, tor = line.split('|')
            low, selmer, tor = map(int, [low, selmer, tor])
            nf.append({'limtriv': int(lim), 'descent_lower': low,
                       'candidate_group_dimension': selmer, 'torsion_dimension': tor,
                       'adjusted_upper': selmer - tor})
        elif line.startswith('@@CERT_OK|'):
            _, degree, poly = line.split('|', 2)
            certs.append({'degree': int(degree), 'polynomial': poly})
        elif line.startswith('@@UNCERT_BNF|'):
            _, degree, poly = line.split('|', 2)
            uncertified.append({'degree': int(degree), 'polynomial': poly})
        elif line.startswith('@@ERROR|'):
            errors.append(line.split('|', 1)[1])
        elif line.startswith('@@NF_RAW|'):
            points.append(line.split('|', 1)[1])
    # GP exits zero for many uncaught parser/runtime errors. Do not trust it.
    for line in stderr.splitlines():
        if '***' in line and 'Warning:' not in line:
            errors.append(line.strip())
    qb = [max(x[0] for x in q), min(x[1] for x in q)] if q else None
    nb = None
    if nf:
        nb = [max([x['descent_lower'] for x in nf] + ([qb[0]] if qb else [])),
              min(x['adjusted_upper'] for x in nf)]
    if (qb and qb[0] > qb[1]) or (nb and nb[0] > nb[1]):
        errors.append('Inconsistent rank bounds')
        nb = None
    gain = [max(0, nb[0] - qb[1]), nb[1] - qb[0]] if nb and qb else None
    return {'q_bounds': qb, 'nf_bounds': nb, 'rank_gain_bounds': gain,
            'descent_attempts': nf, 'class_unit_certificates': certs,
            'uncertified_class_unit_data': uncertified,
            'nf_raw_vectors_gp': points, 'errors': errors,
            'terminal_marker': '@@DONE' in stdout,
            'exact': bool((qb if rational else nb) and
                          (qb if rational else nb)[0] == (qb if rational else nb)[1])}

def execute(job, rational=False, area='instances', watchdog=120):
    out = RUN / area / job['id']
    out.mkdir(parents=True, exist_ok=False)
    code = script(job, rational)
    (out / 'input.gp').write_text(code)
    argv = ['prlimit', '--as=4294967296', '--', GP, '-q', '-f', '-s', '128M', str(out / 'input.gp')]
    launch = {'job': job, 'command_argv': argv, 'started_at_utc': stamp(),
              'watchdog_seconds': watchdog, 'script_sha256': hashlib.sha256(code.encode()).hexdigest()}
    write_json(out / 'launch.json', launch)
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = LIB
    start = time.monotonic()
    timed_out = False
    with (out / 'stdout.log').open('xb') as so, (out / 'stderr.log').open('xb') as se:
        proc = subprocess.Popen(argv, cwd=SRC, env=env, stdout=so, stderr=se, start_new_session=True)
        try:
            exit_code = proc.wait(timeout=watchdog)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            exit_code = proc.wait()
    result = parse((out / 'stdout.log').read_text(), (out / 'stderr.log').read_text(), rational)
    # Script/parser errors make a result unusable; a caught refinement error can
    # retain bounds emitted before that failed refinement.
    uncaught = any(e.startswith('***') for e in result['errors'])
    if uncaught:
        result['nf_bounds'] = result['rank_gain_bounds'] = None
        result['exact'] = False
    result.update({'job': job, 'exit_code': exit_code, 'timed_out': timed_out,
                   'finished_at_utc': stamp(), 'elapsed_seconds': time.monotonic() - start})
    b = result['q_bounds'] if rational else result['nf_bounds']
    result['status'] = 'exact' if result['exact'] else 'bounds' if b else 'unfinished' if timed_out else 'error'
    result['bounds_coincide'] = result['exact']
    result['conditional_on_grh'] = bool(result['uncertified_class_unit_data'] and b and not rational)
    if result['conditional_on_grh']:
        result['status'] = 'conditional_exact' if result['exact'] else 'conditional_bounds'
        result['exact'] = False
    write_json(out / 'result.json', result)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['controls', 'campaign'], required=True)
    args = parser.parse_args()
    if args.mode == 'controls':
        controls = [
            {'id': 'quadratic-torsion', 'A': -1, 'B': 0, 'g': [-5, 0, 1], 'degree': 2},
            {'id': 'cubic-first', 'A': -3, 'B': 3, 'g': [-1, -1, 0, 1], 'degree': 3},
        ]
        results = [execute(c, area='controls') for c in controls]
        expected = [1, 3]
        ok = all(r['nf_bounds'] and r['nf_bounds'][0] <= rank <= r['nf_bounds'][1] and not r['errors'] for r,rank in zip(results,expected))
        write_json(RUN / 'controls-result.json', {'passed': ok, 'known_ranks_contained': expected, 'results': results})
        print('CONTROLS', ok, flush=True)
        if not ok:
            raise SystemExit(1)
        return
    assert json.loads((RUN / 'controls-result.json').read_text())['passed']
    plan = json.loads((RUN / 'plan.json').read_text())
    repo = RUN.parents[3]
    launch = {'started_at_utc': stamp(), 'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip(),
              'dirty_tree_before_run': subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo, text=True).strip(),
              'command_argv': ['python3', str(Path(__file__).resolve()), '--mode', args.mode],
              'platform': platform.platform(), 'python': platform.python_version(),
              'pari_version': '2.17.2', 'model': 'GPT-6 (system identity; no provider probe)',
              'requested_policy': 'executor-implementation', 'fallback_used': False,
              'degraded_requirements': [], 'scientific_review_performed': False,
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.iterdir() if p.is_file()}}
    write_json(RUN / 'launch.json', launch)
    start = time.monotonic()
    reused = json.loads((RUN / 'reused-results.json').read_text())
    results = {'q': reused['q'], 'nf': reused['nf'], 'reused_from_run': reused['source_run']}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        for arm, jobs in [('nf', plan['jobs_to_execute'])]:
            futures = [pool.submit(execute, j, rational=arm == 'q', area='rational' if arm == 'q' else 'instances') for j in jobs]
            for i, f in enumerate(concurrent.futures.as_completed(futures), 1):
                r = f.result()
                results[arm].append(r)
                if arm == 'nf' or i % 50 == 0 or i == len(jobs):
                    print(arm, f'{i}/{len(jobs)}', r['job']['id'], r['status'], r['q_bounds'] if arm == 'q' else r['nf_bounds'],
                          f"{r['elapsed_seconds']:.2f}s", flush=True)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    results['process'] = {'finished_at_utc': stamp(), 'elapsed_seconds': time.monotonic() - start,
                          'child_user_cpu_seconds': usage.ru_utime, 'child_system_cpu_seconds': usage.ru_stime,
                          'child_peak_rss_kib': usage.ru_maxrss}
    write_json(RUN / 'raw-result.json', results)
    print('FINISHED', results['process'], flush=True)

if __name__ == '__main__':
    main()
