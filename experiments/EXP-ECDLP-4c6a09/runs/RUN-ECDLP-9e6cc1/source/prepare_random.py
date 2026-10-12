#!/usr/bin/env python3
"""Freeze and draw new random cubic fields without consulting rank outcomes."""
import hashlib
import json
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/workspace/solinas-run')
BASE = REPO / 'experiments/EXP-ECDLP-4c6a09'
OLD = BASE / 'runs/RUN-ECDLP-6d910b'
RUN = BASE / 'runs/RUN-ECDLP-9e6cc1'
TOOL = Path(__file__).resolve().parent

def write(p, obj):
    with p.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    RUN.mkdir(exist_ok=False)
    (RUN/'source').mkdir()
    for p in (OLD/'source').iterdir():
        if p.is_file():
            shutil.copy2(p, RUN/'source'/p.name)
    for name in ['prepare_random.py', 'random_campaign.py']:
        shutil.copy2(TOOL/name, RUN/'source'/name)
    shutil.copytree(OLD/'inputs', RUN/'inputs')
    inherited = [('benchmark-attempt-01/raw-result.json', 'prior-cold-result.json'),
                 ('benchmark-shared-attempt-01/raw-result.json', 'prior-shared-result.json'),
                 ('benchmark-attempt-01/targets-public.json', 'targets-public.json'),
                 ('benchmark-attempt-01/validation/synthetic-truth.json', 'synthetic-truth.json'),
                 ('point-preparation-attempt-02/seed-specs.json', 'prior-seed-specs.json')]
    provenance = []
    for src, dst in inherited:
        shutil.copy2(OLD/src, RUN/'inputs'/dst)
        provenance.append({'source':str((OLD/src).relative_to(REPO)), 'destination':'inputs/'+dst,
                           'sha256':sha(OLD/src)})
    plan = {
        'run_id':RUN.name, 'experiment_id':'EXP-ECDLP-4c6a09',
        'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
        'authorization':'User: Run random seed fields',
        'scope':'Additive random cubic number-field control extension of RUN-ECDLP-6d910b',
        'sampling':{'python_rng':'random.Random (CPython 3.12)',
                    'seeds':[2026101102,2026101103,2026101104],
                    'accepted_fields_per_seed':8, 'candidate_draw_limit_per_seed':400,
                    'draw':'monic t^3+a2*t^2+a1*t+a0; a2,a1 uniform integers [-4,4], a0 uniform [-4,-3,-2,-1,1,2,3,4]',
                    'accept':'irreducible; new polredabs canonical polynomial across all draws; exclude the three prior control field classes',
                    'uniformity':'Uniform draws of bounded polynomials before rejection, not uniform sampling of number-field isomorphism classes',
                    'outcome_blind':'No rank, points, roots, coverage or relations used to select fields',
                    'duplicates':'Every rejected draw retained; pairwise nfisisom verification of accepted fields'},
        'models':[{'A':-3,'B':3},{'A':7,'B':1}],
        'model_selection':'Previously highlighted rank-gain examples, not a random curve sample',
        'k_values':[6,7,12], 'prime_rule':'p=(2^k)^3-2^k-1',
        'comparison_inputs':provenance,
        'rank':{'runner':'run_rank.py copied unchanged from RUN-ECDLP-6d910b',
                'pari_seed':1, 'process_watchdog_seconds':120, 'class_unit_data':'certified',
                'unresolved':'Retain emitted bounds and points; do not impute a rank'},
        'point_selection':{'max_seed_points':4,
                           'rule':'Anchor the inherited first rational point, then checked returned descent points in their emitted order; remove exact duplicates and sign duplicates; cap at four; preserve every raw descent point',
                           'fallback':'If descent emits no point vector, use inherited rational points and label seed-discovery unavailable',
                           'independence':'Point representatives are not claimed a saturated or independent basis; finite-field collisions measured'},
        'grid':{'bounds':[4], 'order':'same reflected Gray traversal as prior run',
                'exact_K_timing_repetitions':3, 'process_watchdog_seconds':180,
                'maximum_entries':6561},
        'reduction':{'root':'least integer root of original polynomial modulo the unchanged p',
                     'missing':'No degree-one prime => unavailable for that fixed cohort; do not change p or redraw',
                     'coordinate_poles':'Good reduction sends a point with negative x valuation to infinity'},
        'targets':{'source':'identical 96 public synthetic targets from RUN-ECDLP-6d910b',
                   'count_per_cohort':16, 'query_step_cap':32768,
                   'sharing':'one global relation system per field/model/prime over seed logs and all targets',
                   'query':'Q-j*M*G, M=number of coefficient vectors',
                   'oracle':'Synthetic truth only checks returned scalar answers; solver receives public points only'},
        'metrics':['distinct subgroup points','coverage fraction','coverage per build group call',
                   'global independent relation rank','useful relations per 1000 group calls',
                   'verified target recoveries','group calls','modular multiplication and inversion counts',
                   'rank bounds','seed-discovery elapsed seconds','exact-K CPU timings and coordinate bit sizes'],
        'controls':'Reuse immutable Solinas, rational and BSGS observations on identical groups and targets; compare supplied seed-count strata separately',
        'costs':'Report cached finite-field work separately from discovery and exact-K generation; no universal CPU conversion',
        'resources':{'max_concurrent_gp':2,'gp_address_space_bytes':4294967296,
                     'gp_stack_initial':'128M','gp_stack_max_bytes':2000000000},
        'stopping':'24 accepted fields, 48 field/model descents, all 144 fixed field/model/prime statuses; fixed watchdogs, no outcome-dependent resampling',
        'interpretation':'Toy observations only; no scientific status transition or deployed-curve security claim; limited coefficient ensemble and two selected models'
    }
    write(RUN/'plan.json', plan)
    candidates = []
    for seed in plan['sampling']['seeds']:
        rng = random.Random(seed)
        for draw in range(1,401):
            candidates.append({'seed':seed, 'draw':draw,
                               'g':[rng.choice([-4,-3,-2,-1,1,2,3,4]),rng.randint(-4,4),rng.randint(-4,4),1]})
    write(RUN/'sampling-candidates.json', candidates)
    write(RUN/'source-reuse.json',{'prior_run':OLD.name,
                                  'copied_source_hashes':{p.name:sha(p) for p in (OLD/'source').iterdir() if p.is_file()},
                                  'input_provenance':provenance})
    print(RUN, flush=True)

if __name__ == '__main__':
    main()
