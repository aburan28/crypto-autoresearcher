#!/usr/bin/env python3
"""Pure-Python affine replay of the separate Sage subgroup certificates."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from sympy import isprime

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def add(P,Q,p,a=-3):
    if P is None:return Q
    if Q is None:return P
    x1,y1=P;x2,y2=Q
    if x1==x2 and (y1+y2)%p==0:return None
    if P==Q:
        m=((3*x1*x1+a)*pow(2*y1,-1,p))%p
    else:
        m=((y2-y1)*pow((x2-x1)%p,-1,p))%p
    x3=(m*m-x1-x2)%p
    return x3,(m*(x1-x3)-y1)%p


def mul(k,P,p):
    R=None
    while k:
        if k&1:R=add(R,P,p)
        P=add(P,P,p)
        k>>=1
    return R


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path)
    args=parser.parse_args();path=args.run_dir.resolve()
    assert path.parent==(HERE/'runs').resolve()
    receipt=json.loads((path/'receipt.json').read_text())
    assert receipt['status']=='completed' and sha(path/'points.jsonl')==receipt['points_sha256']
    for file,digest in receipt['source_sha256'].items():
        assert sha(ROOT/file)==digest
    points=[json.loads(line) for line in (path/'points.jsonl').read_text().splitlines()]
    assert len(points)==99
    seen=set()
    for row in points:
        key=row['stream'],row['index']
        assert key not in seen;seen.add(key)
        p,n,u,h=(int(row[k]) for k in ('p','n','order','h'))
        b=int(row['b'],16);r=int(row['r1997'],16)
        P=(int(row['point_x'],16),int(row['point_y'],16))
        assert 0<=P[0]<p and 0<=P[1]<p and (P[1]**2-P[0]**3+3*P[0]-b)%p==0
        assert (r*b*b+27)%p==0
        assert u==h*n and n>2**160 and n*n>16*p
        assert abs(u-(p+1))<=math.isqrt(4*p)
        assert isprime(n)
        assert mul(n,P,p) is None
        assert all(row[k] for k in ('on_curve','n_times_point_identity','hasse_unique_multiple','n_prime_sage_proof'))
    cross=json.loads((ROOT/'research/nist_seed_selection_20261016/raw/full_census_crosscheck_v4.json').read_text())
    published={(name,i) for name,v in cross['streams'].items() for i in v['published']}
    omitted={(name,i) for name,v in cross['streams'].items() for i in v['screen_skipped']}
    assert len(published)==10 and len(omitted)==11 and published|omitted<=seen
    verification={'status':'verified','checked_points':99,'published_controls':10,
                  'omitted_controls':11,'points_sha256':sha(path/'points.jsonl'),
                  'receipt_sha256':sha(path/'receipt.json'),
                  'method':'independent Python affine arithmetic; SymPy primality cross-check'}
    target=path/'verification.json';out=json.dumps(verification,sort_keys=True,indent=2)+'\n'
    if target.exists():assert target.read_text()==out
    else:target.write_text(out)
    print(json.dumps(verification,sort_keys=True))


if __name__=='__main__':main()
