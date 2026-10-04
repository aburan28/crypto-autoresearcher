"""Merge the four independent sympy-sweep chunks and compare against the
bit-packed sweep, candidate by candidate."""
import json, glob, sys
mine = {int(k): v for k, v in
        json.load(open('../out/rederivation_results.json'))['all_counts'].items()}
theirs = {}
files = sorted(glob.glob('../out/sympy_chunk_*.json'))
for f in files:
    for k, v in json.load(open(f)).items():
        theirs[int(k)] = v            # [N, deg_g, deg_P]
print(f'chunk files merged: {files}')
print(f'candidates in bit-packed sweep : {len(mine)}')
print(f'candidates in sympy sweep      : {len(theirs)}')
missing = sorted(set(mine) - set(theirs))
extra = sorted(set(theirs) - set(mine))
mism = sorted(l for l in set(mine) & set(theirs) if mine[l] != theirs[l][0])
print(f'missing from sympy sweep       : {len(missing)} {missing if missing else ""}')
print(f'in sympy sweep but not mine    : {len(extra)} {extra if extra else ""}')
print(f'COUNT MISMATCHES               : {len(mism)} {mism if mism else ""}')
if not missing and not extra and not mism:
    h = {}
    for l, v in theirs.items():
        h[v[0]] = h.get(v[0], 0) + 1
    mx = max(v[0] for v in theirs.values())
    arg = sorted(l for l in theirs if theirs[l][0] == mx)
    print()
    print(f'INDEPENDENT (sympy) RESULT: max N = {mx}, argmax = {arg}')
    print(f'INDEPENDENT (sympy) HISTOGRAM: {dict(sorted(h.items()))}')
    print('FULL AGREEMENT on all', len(mine), 'candidates.')
    summary = (f'agrees on all {len(mine)} candidates (0 mismatches); independently '
               f'reproduces max N = {mx}, argmax {arg}, and histogram '
               f'{dict(sorted(h.items()))}.')
else:
    summary = (f'INCOMPLETE OR DISAGREEING: {len(missing)} candidates missing, '
               f'{len(mism)} mismatches {mism}.')
open('../out/sympy_sweep_summary.txt', 'w').write(summary + '\n')
print()
print('wrote ../out/sympy_sweep_summary.txt:', summary)
