#!/usr/bin/env python3
"""Exact number-field seed/grid arithmetic, degree-one reductions and raw GP logs."""
import concurrent.futures
import hashlib
import json
import os
import subprocess
import time
from fractions import Fraction
from pathlib import Path

from finite_math import gray_vectors

GP = '/workspace/solinas-runtime/pari/usr/bin/gp'
LIB = '/workspace/solinas-runtime/pari/usr/lib/x86_64-linux-gnu'

def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

def execute(directory, code, watchdog=180):
    directory.mkdir(parents=True, exist_ok=False)
    inp = directory / 'input.gp'
    inp.write_text(code)
    argv = ['prlimit', '--as=4294967296', '--', GP, '-q', '-f', '-s', '128M', str(inp)]
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = LIB
    write(directory / 'launch.json', {'command_argv': argv, 'script_sha256': hashlib.sha256(code.encode()).hexdigest(),
                                     'watchdog_seconds': watchdog})
    start = time.monotonic()
    timeout = False
    with (directory / 'stdout.log').open('xb') as out, (directory / 'stderr.log').open('xb') as err:
        proc = subprocess.Popen(argv, stdout=out, stderr=err, env=env, start_new_session=True)
        try:
            status = proc.wait(timeout=watchdog)
        except subprocess.TimeoutExpired:
            timeout = True
            proc.kill()
            status = proc.wait()
    text = (directory / 'stdout.log').read_text()
    stderr = (directory / 'stderr.log').read_text()
    errors = [line for line in text.splitlines() if line.startswith('@@ERROR')]
    errors += [line for line in stderr.splitlines() if '***' in line and 'Warning:' not in line]
    result = {'exit_code': status, 'timed_out': timeout, 'elapsed_seconds': time.monotonic() - start,
              'errors': errors, 'terminal_marker': '@@DONE' in text}
    write(directory / 'process.json', result)
    if status != 0 or timeout or errors or not result['terminal_marker']:
        raise RuntimeError(f'GP stage failed: {directory.name}: {result}')
    return text, result

def polynomial(g):
    return '+'.join(f'({c})*y^{i}' for i, c in enumerate(g) if c)

def point_text(point):
    return '[0]' if point is None else '[' + ','.join(str(c) for c in point) + ']'

def prelude():
    return 'default(parisizemax,2000000000);default(nbthreads,1);setrand(1);\n'

def export_seeds(run, stage):
    inherited = json.loads((run / 'inputs/inherited-points.json').read_text())
    matched = json.loads((run / 'matched-ranks-result.json').read_text())
    q_vectors = {}
    for q in inherited['q']:
        text = (run / 'inputs' / (q['job']['id'] + '.stdout.log')).read_text()
        q_vectors[(q['job']['A'], q['job']['B'])] = [line.split('|', 1)[1] for line in text.splitlines()
                                                  if line.startswith('@@Q_RAW|')][-1]
    specs = []
    for r in inherited['nf'] + matched['nf']:
        if not r['nf_raw_vectors_gp']:
            raise RuntimeError('Matched descent supplied no checked points')
        j = r['job']
        field = j.get('field', 'solinas')
        spec = {'id': f"{field}-a{j['A']}-b{j['B']}", 'field': field, 'g': j['g'],
                'A': j['A'], 'B': j['B'], 'rank_bounds': r['nf_bounds'],
                'rank_status': r['status'], 'rank_seed_discovery_elapsed_seconds': r['elapsed_seconds'],
                'rank_source_run': r.get('derived_source_run', run.name),
                'nr_gp': r['nf_raw_vectors_gp'][-1], 'qr_gp': q_vectors[(j['A'], j['B'])]}
        specs.append(spec)
    # Exact rational baseline, evaluated inside the same Solinas field only to share instrumentation.
    for q in inherited['q']:
        a, b = q['job']['A'], q['job']['B']
        specs.append({'id': f'rational-a{a}-b{b}', 'field': 'rational', 'g': [-1, -1, 0, 1],
                      'A': a, 'B': b, 'rank_bounds': q['q_bounds'], 'rank_status': 'exact',
                      'rank_source_run': 'RUN-ECDLP-aba670',
                      'rank_seed_discovery_elapsed_seconds': q['elapsed_seconds'],
                      'nr_gp': None, 'qr_gp': q_vectors[(a, b)]})
    for spec in specs:
        g, a, b = spec['g'], spec['A'], spec['B']
        model = f'[0,0,0,{a},{b}]'
        code = prelude() + '\n'.join([
            '{main()=',
            f'my(N=nfinit({polynomial(g)}),EQ=ellinit({model}),EK=ellinit({model},N),QR={spec["qr_gp"]},S,NR,F,EP,C,L,H,G,RP,R,PI,MR,found);',
            f'NR={spec["nr_gp"]};S=NR[3];' if spec['nr_gp'] else 'S=QR[4];',
            'for(i=1,#S,if(!ellisoncurve(EK,S[i]),error("Seed fails exact curve equation")));',
            'for(i=1,#S,if(S[i]==QR[4][1],if(i>1,S=concat([S[i]],vector(#S-1,j,S[if(j<i,j,j+1)])));break));',
            'for(i=1,#S,print("@@SEED|",i,"|",vector(3,j,polcoef(lift(S[i][1]),j-1)),"|",vector(3,j,polcoef(lift(S[i][2]),j-1))));',
            'for(j=1,3,',
            f'R=2^([6,7,12][j]);PI=R^3-R-1;EP=ellinit({model},PI);C=ellcard(EP);F=factor(C);L=F[#F[,1],1];if(F[#F[,1],2]!=1,error("Repeated largest subgroup prime"));H=C/L;',
            'RP=QR[4][1];G=ellmul(EP,[Mod(RP[1],PI),Mod(RP[2],PI)],H);if(#G==1,G=ellmul(EP,ellgroup(EP,,1)[3][1],H));if(#G==1,error("Zero generator"));',
            'print("@@GROUP|",j,"|",PI,"|",C,"|",L,"|",H,"|",lift(G[1]),"|",lift(G[2]));',
            'MR=polrootsmod(N.pol,PI);',
            'if(!#MR,print("@@NO_ROOT|",j);next);',
            'R=' + ('R;' if spec['field'] in ('solinas', 'rational') else 'vecmin(lift(MR));'),
            'if(subst(N.pol,y,Mod(R,PI))!=0,error("Chosen root invalid"));',
            'PI=idealprimedec(N,PI);found=0;for(i=1,#PI,if(PI[i][4]==1 && lift(nfmodpr(N,Mod(y,N.pol),PI[i]))==R,found=i;break));if(!found,error("Degree-one prime missing"));',
            'print("@@ROOT|",j,"|",R,"|",found);',
            'for(i=1,#S,RP=[nfmodpr(N,S[i][1],PI[found]),nfmodpr(N,S[i][2],PI[found])];if(!ellisoncurve(EP,RP),error("Reduced seed off curve"));print("@@REDUCED_SEED|",j,"|",i,"|",lift(RP[1]),"|",lift(RP[2])));',
            ');};',
            'iferr(main(),E,print("@@ERROR|",E));print("@@DONE");quit;']) + '\n'
        text, process = execute(stage / 'seed-export' / spec['id'], code)
        spec['seeds_coefficients'], spec['reductions'] = [], {}
        for line in text.splitlines():
            parts = line.split('|')
            if parts[0] == '@@SEED':
                co = [[Fraction(x.strip()) for x in s.strip('[]').split(',')] for s in parts[2:4]]
                spec['seeds_coefficients'].append([[[x.numerator, x.denominator] for x in v] for v in co])
            elif parts[0] == '@@GROUP':
                j, p, n, ell, h, gx, gy = map(int, parts[1:])
                spec['reductions'][str(j)] = {'k': [6, 7, 12][j-1], 'p': p, 'group_order': n,
                                              'ell': ell, 'cofactor': h, 'G': [gx, gy], 'seeds_full': []}
            elif parts[0] == '@@ROOT':
                spec['reductions'][parts[1]].update({'root': int(parts[2]), 'prime_index': int(parts[3]), 'eligible': True})
            elif parts[0] == '@@NO_ROOT':
                spec['reductions'][parts[1]]['eligible'] = False
            elif parts[0] == '@@REDUCED_SEED':
                spec['reductions'][parts[1]]['seeds_full'].append([int(parts[3]), int(parts[4])])
        spec['export_process'] = process
    write(stage / 'seed-specs.json', specs)
    return specs

def exact_grid(stage, spec, bounds=(1, 2, 4), repetitions=3):
    n = len(spec['seeds_coefficients'])
    seeds = []
    for point in spec['seeds_coefficients']:
        coords = []
        for v in point:
            coords.append('Mod(' + '+'.join(f'({a}/{b})*y^{j}' for j, (a, b) in enumerate(v)) + ',N.pol)')
        seeds.append('[' + ','.join(coords) + ']')
    # Generate radix digits and index changes in GP, matching the independent Python traversal.
    code = prelude() + '\n'.join([
        'bitheight(P)={my(H=0,V);if(#P==1,return(0));for(i=1,2,for(j=0,2,V=polcoef(lift(P[i]),j);H=max(H,if(numerator(V),logint(abs(numerator(V)),2)+1,0));H=max(H,logint(denominator(V),2)+1)));H};',
        'reduce_point(N,P,PR,MP)={if(#P==1,return([0]));if(nfeltval(N,P[1],PR)<0,return([0]));[lift(nfmodpr(N,P[1],MP)),lift(nfmodpr(N,P[2],MP))]};',
        '{main()=',
        f'my(N=nfinit({polynomial(spec["g"])}),EK=ellinit([0,0,0,{spec["A"]},{spec["B"]}],N),S=[{",".join(seeds)}],D,IDX,DIR,STEPS,TAB,P,I,DELTA,OLD,T,B,NB,MAXBITS,PI,PR,MP,RED,HASH,DT,EP);',
        'for(bi=1,3,B=[1,2,4][bi];D=concat([0],vector(2*B,j,if(j%2,(j+1)/2,-j/2)));NB=#D^#S;',
        'for(rep=1,3,',
        'gettime();STEPS=vector(#S,i,vector(4*B+1,j,ellmul(EK,S[i],j-2*B-1)));DT=gettime();print("@@NF_PRECOMPUTE|",B,"|",rep,"|",DT,"|",#S*4*B);',
        'IDX=vector(#S,i,1);DIR=vector(#S,i,1);TAB=vector(NB);P=[0];MAXBITS=0;',
        'gettime();for(ti=1,NB,TAB[ti]=P;MAXBITS=max(MAXBITS,bitheight(P));I=#S;while(I>0 && (IDX[I]+DIR[I]<1 || IDX[I]+DIR[I]>#D),DIR[I]=-DIR[I];I--);if(!I,break);OLD=D[IDX[I]];IDX[I]+=DIR[I];DELTA=D[IDX[I]]-OLD;P=elladd(EK,P,STEPS[I][DELTA+2*B+1]));',
        'DT=gettime();print("@@NF_GENERATE|",B,"|",rep,"|",NB,"|",NB-1,"|",DT,"|",MAXBITS);',
        'for(kj=1,3,PI=(2^([6,7,12][kj]))^3-2^([6,7,12][kj])-1;',
        'if(!#polrootsmod(N.pol,PI),next);',
        'OLD=' + ('2^([6,7,12][kj]);' if spec['field'] in ('solinas', 'rational') else 'vecmin(lift(polrootsmod(N.pol,PI)));'),
        'PR=idealprimedec(N,PI);I=0;for(j=1,#PR,if(PR[j][4]==1 && lift(nfmodpr(N,Mod(y,N.pol),PR[j]))==OLD,I=j;break));if(!I,error("Missing chosen prime"));PR=PR[I];MP=nfmodprinit(N,PR);',
        f'EP=ellinit([0,0,0,{spec["A"]},{spec["B"]}],PI);',
        'HASH=0;gettime();for(ti=1,NB,RED=reduce_point(N,TAB[ti],PR,MP);if(!ellisoncurve(EP,RED),error("Grid reduction off curve"));HASH=(HASH*1000003+if(#RED==1,0,RED[1]+PI*RED[2]+1))%2305843009213693951;if(rep==1,print("@@POINT|",B,"|",kj,"|",ti,"|",if(#RED==1,"O",Str(RED[1],",",RED[2])))));DT=gettime();print("@@NF_REDUCE|",B,"|",rep,"|",kj,"|",NB,"|",DT,"|",HASH);',
        ');););};',
        'iferr(main(),E,print("@@ERROR|",E));print("@@DONE");quit;']) + '\n'
    text, process = execute(stage / 'exact-grids' / spec['id'], code)
    tables, timings = {}, []
    for line in text.splitlines():
        parts = line.split('|')
        if parts[0] == '@@POINT':
            bound, kj, ti = map(int, parts[1:4])
            key = f'{bound}:{kj}'
            table = tables.setdefault(key, [])
            assert ti == len(table) + 1
            table.append(None if parts[4] == 'O' else list(map(int, parts[4].split(','))))
        elif parts[0] in ('@@NF_PRECOMPUTE', '@@NF_GENERATE', '@@NF_REDUCE'):
            timings.append({'kind': parts[0][2:], 'values': list(map(int, parts[1:]))})
    for bound in bounds:
        for kj, red in spec['reductions'].items():
            if red['eligible']:
                assert len(tables[f'{bound}:{kj}']) == (2*bound+1)**n
                hashes = [t['values'][-1] for t in timings if t['kind'] == 'NF_REDUCE'
                          and t['values'][0] == bound and t['values'][2] == int(kj)]
                assert len(hashes) == repetitions and len(set(hashes)) == 1
    result = {'spec_id': spec['id'], 'seed_count': n, 'tables': tables, 'timings': timings, 'process': process}
    write(stage / 'exact-grids' / spec['id'] / 'tables.json', result)
    print('EXACT_GRID', spec['id'], 'seeds', n, f"{process['elapsed_seconds']:.2f}s", flush=True)
    return result
