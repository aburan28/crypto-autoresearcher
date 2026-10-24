#!/usr/bin/env python3
"""Independent source/order, trial-division, and primality cross-check."""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from sympy import isprime, primerange

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAMPS = {'prime239v3':863711343, 'prime192v2':863966734,
          'P-521':871002724, 'P-256':871696354,
          'P-384':872952608, 'P-224':891607927}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args()
    path = args.run_dir.resolve()
    assert path.is_dir() and path.parent == (HERE/'runs').resolve()
    result = json.loads((path/'analysis.json').read_text())
    receipt = json.loads((path/'receipt.json').read_text())
    for file, digest in receipt['source_sha256'].items():
        p = Path(file) if file.startswith('/') else ROOT/file
        assert sha(p) == digest, file
    for name in ('gp_input','gp_stdout','gp_stderr'):
        ext = '.gp' if name == 'gp_input' else '.log'
        filename = 'gp_input.gp' if name == 'gp_input' else name+'.log'
        assert sha(path/filename) == receipt[name+'_sha256']

    original = {}
    for stream, timestamp in STAMPS.items():
        source = ROOT/f'research/nist_seed_provenance_20261016/census/orders_{timestamp}.txt'
        for line in source.read_text().splitlines():
            index,canonical,other = map(int,line.split())
            for side,u in [('canonical',canonical),('other',other)]:
                if u:
                    key=(stream,index,side)
                    assert key not in original
                    original[key]=u
    assert len(original) == len(result['rows']) == 1854
    residues = {}
    for line in (path/'gp_stdout.log').read_text().splitlines():
        kind,index,value=line.split()
        if kind=='R':
            assert int(index) not in residues
            residues[int(index)]=int(value)
    assert len(residues)==1854

    small=list(primerange(2,256))
    seen=set()
    prime_positions=set()
    for i,row in enumerate(result['rows']):
        key=(row['stream'],row['index'],row['side'])
        assert key not in seen and original[key]==int(row['order'])
        seen.add(key)
        n=original[key]
        smooth=1
        for ell in small:
            while n%ell==0:
                smooth*=ell
                n//=ell
        assert n==int(row['residual']) and smooth==int(row['smooth_cofactor'])
        assert int(isprime(n)) == residues[i] == int(row['residual_isprime_gp'])
        p=int(row['p']);u=original[key]
        accepts=bool(isprime(n) and n>2**160 and u!=p and
                     all(pow(p,k,n)!=1 for k in range(1,21)))
        assert accepts==row['eligible_1997_minimum_255']
        assert (accepts and n*n>16*p)==row['eligible_plus_1998_rmin']
        if accepts:
            prime_positions.add((row['stream'],row['index']))
    assert seen==set(original)
    assert len(prime_positions)==result['summary']['nearprime_1997_positions']==130
    assert result['summary']['nearprime_plus_1998_rmin_positions']==130
    verification={
        'status':'verified', 'run_dir':str(path.relative_to(ROOT)),
        'checked_positive_exact_branches':1854,
        'checked_nearprime_seed_positions':130,
        'independent_primality_crosscheck':'SymPy isprime 1.14.0; probable-prime above 64 bits, GP isprime remains primary classification',
        'analysis_sha256':sha(path/'analysis.json'),
        'receipt_sha256':sha(path/'receipt.json'),
        'gp_stdout_sha256':sha(path/'gp_stdout.log'),
    }
    target=path/'verification.json'
    output=json.dumps(verification,sort_keys=True,indent=2)+'\n'
    if target.exists():assert target.read_text()==output
    else:target.write_text(output)
    print(json.dumps(verification,sort_keys=True))


if __name__=='__main__':main()
