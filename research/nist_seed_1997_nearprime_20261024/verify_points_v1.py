#!/usr/bin/env python3
"""Deterministic subgroup certificates for all corrected near-prime positions."""

import datetime as dt
import hashlib
import json
import resource
import signal
import subprocess
import time
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, ZZ, version

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
INPUT=HERE/'runs/positive-20261024T022524Z/analysis.json'
CAND=ROOT/'research/nist_seed_selection_20261016/raw/candidates.jsonl'
POINT_PROTOCOL=HERE/'POINT_PROTOCOL.md'
AMENDMENT=HERE/'AMENDMENT.md'
INPUT_SHA='01b33e08abf1746669ed22d7b1afafbf4175a9d739638cd298194663c5126e33'
CAND_SHA='e854c17a38d5e9f1fca9eb8dd1aa034a6b6cd69d28a2a3acf78b1a187515a441'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def sha1_r(seed,p):
    t=int(p).bit_length();s=(t-1)//160;h=t-160*s
    value=int.from_bytes(hashlib.sha1(seed.to_bytes(20,'big')).digest(),'big')&((1<<(h-1))-1)
    for i in range(1,s+1):
        value=(value<<160)|int.from_bytes(hashlib.sha1(((seed+i)%(1<<160)).to_bytes(20,'big')).digest(),'big')
    return value


def alarm_handler(signum,frame):raise TimeoutError('per-position 10-second watchdog')


def main():
    assert sha(INPUT)==INPUT_SHA and sha(CAND)==CAND_SHA
    frozen=json.loads(INPUT.read_text())
    eligible={}
    for row in frozen['rows']:
        if row['eligible_1997_minimum_255']:
            key=(row['stream'],row['index'])
            eligible.setdefault(key,[]).append(row)
    assert len(eligible)==99
    candidates={}
    for line in CAND.read_text().splitlines():
        c=json.loads(line)
        key=(c['target'],c['index'])
        if key in eligible:
            assert key not in candidates
            candidates[key]=c
    assert set(candidates)==set(eligible)
    start=dt.datetime.now(dt.timezone.utc)
    run_dir=HERE/'runs'/('points-'+start.strftime('%Y%m%dT%H%M%SZ'))
    run_dir.mkdir(parents=True,exist_ok=False)
    raw=run_dir/'points.jsonl'
    t0=time.monotonic()
    signal.signal(signal.SIGALRM,alarm_handler)
    count=0
    try:
        with raw.open('w') as out:
            for key in sorted(eligible):
                signal.alarm(10)
                row=min(eligible[key],key=lambda r:(int(r['smooth_cofactor']),r['side']!='canonical'))
                c=candidates[key]
                p=Integer(row['p']);n=Integer(row['residual']);h=Integer(row['smooth_cofactor']);u=Integer(row['order'])
                assert u==h*n and n*n>16*p and n>2**160
                assert n.is_prime(proof=True)
                seed=int(c['seed'],16)
                roots=c['variants']['nist_fips_186_2']['b_roots']
                assert len(roots)==2
                assert key[0]!='P-224' or row['side']=='canonical'
                b=Integer(int(roots[0 if row['side']=='canonical' else 1],16))
                r=sha1_r(seed,p)
                assert (Integer(r)*b*b+27)%p==0
                assert (Integer(sha1_r(seed^1,p))*b*b+27)%p!=0
                E=EllipticCurve(GF(p),[-3,b])
                P=None;chosen_x=None
                for x in range(1,33):
                    try:Q=E.lift_x(Integer(x))
                    except ValueError:continue
                    candidate=h*Q
                    if candidate.is_zero():continue
                    if not (n*candidate).is_zero():continue
                    P=candidate;chosen_x=x;break
                assert P is not None, f'no certificate within 32 x values: {key}'
                record={'stream':key[0], 'index':key[1], 'side':row['side'],
                        'seed':c['seed'], 'p':str(p), 'b':hex(int(b)),
                        'r1997':hex(r), 'order':str(u), 'n':str(n), 'h':str(h),
                        'first_success_x':chosen_x, 'point_x':hex(int(P[0])),
                        'point_y':hex(int(P[1])), 'on_curve':bool(P in E),
                        'n_times_point_identity':bool((n*P).is_zero()),
                        'hasse_unique_multiple':bool(n*n>16*p),
                        'n_prime_sage_proof':True}
                out.write(json.dumps(record,sort_keys=True)+'\n');out.flush()
                count+=1
                signal.alarm(0)
        assert count==99
        cross=json.loads((ROOT/'research/nist_seed_selection_20261016/raw/full_census_crosscheck_v4.json').read_text())
        certified=set((name,i) for name,v in cross['streams'].items() for i in v['broad_family_both_seeded_roots'])
        published=set((name,i) for name,v in cross['streams'].items() for i in v['published'])
        omitted=set((name,i) for name,v in cross['streams'].items() for i in v['screen_skipped'])
        assert len(certified)==69 and len(published)==10 and len(omitted)==11
        assert certified|published|omitted <= set(eligible)
    except BaseException as exc:
        signal.alarm(0)
        (run_dir/'failure.json').write_text(json.dumps({'status':'failed','completed_positions':count,
                                                       'error_type':type(exc).__name__,'error':str(exc)},indent=2)+'\n')
        raise
    receipt={'status':'completed','started_utc':start.isoformat(),
             'ended_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
             'elapsed_seconds':time.monotonic()-t0,
             'command':['gtimeout','120','sage','-python',str(Path(__file__).resolve())],
             'sage_version':version(),
             'git_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip(),
             'git_status':subprocess.run(['git','status','--porcelain'],cwd=ROOT,text=True,capture_output=True,check=True).stdout,
             'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (INPUT,CAND,POINT_PROTOCOL,AMENDMENT,Path(__file__).resolve())},
             'points_sha256':sha(raw),'checked_positions':count,
             'user_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime,
             'system_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_stime,
             'max_rss_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (run_dir/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'run_dir':str(run_dir.relative_to(ROOT)),'checked_positions':count,
                      'points_sha256':receipt['points_sha256']},sort_keys=True))


if __name__=='__main__':main()
