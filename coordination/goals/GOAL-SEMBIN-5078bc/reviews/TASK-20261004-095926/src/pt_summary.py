#!/usr/bin/env python3
"""Aggregate PT-1..PT-3 outputs into results/pt/pt_summary.json; adds the structural up-set flag K (non-LM monomials of size<=4 that contain a proper LM member)
for every PT-1 mutant system (K>0 means LM(W) is not an up-set inside sizes<=4, which an unmutated closure under the stated order never exhibits)."""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.path.join(OUT, 'results', 'pt')
def K_of(C, N):
    lms = set(C.lm_set()); K = 0
    for m in C.S.mons:
        if m in lms: continue
        bits = [j for j in range(N) if (m >> j) & 1]
        hit = False
        for k in range(len(bits)):
            for sub in itertools.combinations(bits, k):
                if sum(1 << j for j in sub) in lms: hit = True; break
            if hit: break
        K += hit
    return K
MUT = {'a_budget_minus_1': dict(budget_shift=1), 'b_only_new_lm': dict(only_new_lm=True), 'c_generators_only': dict(gens_only=True),
       'd_drop_last_batch': dict(drop_last_batch=True), 'd2_drop_last_chunk64': dict(drop_last_chunk=64)}
cases = json.load(open(P + '/pt1_abc.json'))['pt1'] + json.load(open(P + '/pt1_d.json'))['pt1']
table = {}
for c in cases:
    gens = system(c['family'], c['N'], c['M'], c['seed'])
    C = Closure(gens, c['N'], 4, **MUT[c['mutant']]).run()
    K = K_of(C, c['N'])
    t = table.setdefault(c['mutant'], dict(systems=0, argument_passes=0, S1=0, S2=0, S3=0, F1_flags=0, F2_flags=0, K_flags=0, verdict_mutant_insufficient=0, verdict_unmutated_sufficient=0, cases=[]))
    t['systems'] += 1; t['argument_passes'] += c['ARGUMENT_PASSES']; t['S1'] += c['S1']; t['S2'] += c['S2']; t['S3'] += c['S3']
    t['F1_flags'] += c['F1_LM_differs_from_unmutated']; t['F2_flags'] += c['F2_saturation_flags']; t['K_flags'] += (K > 0)
    t['verdict_mutant_insufficient'] += (c['verdict_mutant'] == 'insufficient'); t['verdict_unmutated_sufficient'] += (c['verdict_unmutated'] == 'sufficient')
    t['cases'].append(dict(family=c['family'], N=c['N'], M=c['M'], seed=c['seed'], V=c['V'], verdict_mutant=c['verdict_mutant'], verdict_unmutated=c['verdict_unmutated'], K=K,
                           N_std_mutant=c['F3_Nstd_mutant'], N_std_unmutated=c['F3_Nstd_unmutated'], rank_mutant=c['rank_mutant'], rank_unmutated=c['rank_unmutated']))
summ = dict(PT1=table)
summ['PT2_bulk_and_one_row'] = json.load(open(P + '/pt2.json'))
summ['PT2_sweep'] = json.load(open(P + '/pt2_sweep.json'))
summ['PT2_false_sufficient'] = json.load(open(P + '/pt2_false.json'))
summ['PT3a_v2'] = json.load(open(P + '/pt3a_v2.json'))
summ['PT3b'] = dict(systems=json.load(open(P + '/pt3.json'))['PT-3b_GB_element_above_degree_4'], sympy=json.load(open(P + '/pt3_sympy.json')))
json.dump(summ, open(P + '/pt_summary.json', 'w'), indent=1)
for k, t in table.items():
    print(k, {x: v for x, v in t.items() if x != 'cases'})
