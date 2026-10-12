#!/usr/bin/env python3
"""Freeze additive, public toy point-coverage/relation measurements."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/workspace/solinas-run')
BASE = REPO / 'experiments/EXP-ECDLP-4c6a09'
RUN = BASE / 'runs/RUN-ECDLP-6d910b'
TOOL = Path(__file__).resolve().parent

def save(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    RUN.mkdir(exist_ok=False)
    (RUN / 'source').mkdir()
    oldsrc = BASE / 'runs/RUN-ECDLP-7cfef7/source'
    for p in oldsrc.iterdir():
        if p.is_file():
            shutil.copy2(p, RUN / 'source' / p.name)
    shutil.copy2('/usr/share/common-licenses/GPL-2', RUN / 'source/GPL-2.txt')
    combined_path = BASE / 'reports/rank-20261011T0207Z/combined-ranks.json'
    combined = json.loads(combined_path.read_text())
    selected = [(-3, 3), (7, 1)]
    inherited_nf = [r for r in combined['nf'] if (r['job']['A'], r['job']['B']) in selected
                    and r['job']['g'] == [-1, -1, 0, 1]]
    inherited_q = [r for r in combined['q'] if (r['job']['A'], r['job']['B']) in selected]
    assert len(inherited_nf) == len(inherited_q) == 2
    (RUN / 'inputs').mkdir()
    save(RUN / 'inputs/inherited-points.json', {'nf': inherited_nf, 'q': inherited_q,
                                               'source': str(combined_path.relative_to(REPO)),
                                               'source_sha256': sha(combined_path)})
    for r in inherited_q:
        origin = BASE / 'runs/RUN-ECDLP-aba670/rational' / r['job']['id'] / 'stdout.log'
        shutil.copy2(origin, RUN / 'inputs' / (r['job']['id'] + '.stdout.log'))
    fields = [{'name': 'solinas', 'g': [-1, -1, 0, 1], 'root_rule': '2^k'},
              {'name': 'random_low_weight', 'g': [-1, 1, 0, 1], 'root_rule': 'least root; record absent roots'},
              {'name': 'pure_cubic', 'g': [-3, 0, 0, 1], 'root_rule': 'least root'},
              {'name': 'isomorphic_sign_control', 'g': [1, -1, 0, 1],
               'root_rule': '-2^k; transform inherited points by alpha=-beta'}]
    jobs = []
    for a, b in selected:
        for field in fields[1:3]:
            g = field['g']
            digest = hashlib.sha256(json.dumps([g, a, b], separators=(',', ':')).encode()).hexdigest()[:16]
            jobs.append({'id': 'NF-' + digest, 'A': a, 'B': b, 'g': g, 'degree': 3,
                         'field': field['name'], 'seed': 1})
    plan = {
        'run_id': RUN.name, 'experiment_id': 'EXP-ECDLP-4c6a09',
        'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
        'authorization': 'User: Yes measure this point coverage and useful relations per unit',
        'purpose': 'Additive public toy benchmark; no hypothesis or frontier promotion',
        'models': [{'A': a, 'B': b} for a, b in selected],
        'selection': 'Two previously highlighted exact rank-gain examples; not a representative curve sample',
        'k_values': [6, 7, 12], 'prime_rule': 'p=(2^k)^3-2^k-1',
        'subgroup_rule': 'largest prime divisor ell of #E(F_p), multiplicity one; h=#E/ell',
        'base_generator_rule': 'h times first inherited rational generator if nonzero; otherwise GP group generator',
        'fields': fields, 'jobs': jobs, 'rank_process_watchdog_seconds': 120,
        'grid_bounds': [1, 2, 4], 'grid_rule': 'Reflected radix Gray traversal of [-B,B]^s, starts at zero',
        'point_seeds': 'Returned checked descent point representatives; not claimed saturated bases',
        'timing_repetitions': 3, 'target_seed': 2026101101, 'target_count_per_curve_prime': 16,
        'query_step_cap': 32768, 'target_query_rule': 'Q-j*M*G; M=number of table entries',
        'relations': {
            'factorbase': 'Collision of two coefficient vectors: difference dot F=O',
            'target': 'Hit Q-j*M*G=c dot F: c dot u-q=-j*M modulo ell',
            'useful': 'New independent modular equation; target recovery only if q is uniquely determined',
            'unknowns': 'All seed discrete logs except coordinates provably equal to G or -G; oracle logs never supplied',
            'verification': 'Check every emitted relation with finite-field arithmetic and all recovered targets',
            'excluded_successes': 'Repeated coefficient vectors, zero equations, dependent equations; a hit alone is not recovery'},
        'matched_controls': [
            'Same model, p, subgroup and target list for every eligible field',
            'Q generator set from the exact rational rank record',
            'Known-scalar and hidden-scalar random finite-field seed sets, same seed count and box',
            'Direct BSGS table of same entry count, plus ceil(sqrt(ell)) entry BSGS',
            'Isomorphic sign-change control must match Solinas coverage and relations exactly'],
        'work_units': ['finite-field group additions/doublings', 'modular inversions and multiplications',
                       'independent relation rank', 'verified target recoveries', 'CPU and wall seconds',
                       'number-field additions, coordinate bit sizes; not equated with finite-field additions'],
        'cost_policy': 'Separate prior seed-discovery cost, exact-K generation, cached reduced generation, table algebra and target queries. Include setup and amortization explicitly.',
        'missing_root_policy': 'No degree-one reduction at same p => ineligible, never replace p or silently drop',
        'validity': ['Exact seed curve checks', 'GP versus Python point/group checks',
                     'Exact-K table reduction equals cached finite-field table',
                     'Isomorphic control equality', 'Truth withheld from solving algorithms',
                     'Meaningful rank-deficient collision and target-recovery controls'],
        'resources': {'max_parallel_gp': 2, 'gp_address_space_bytes': 4294967296,
                      'gp_stack_initial': '128M', 'gp_stack_max_bytes': 2000000000,
                      'exact_grid_process_watchdog_seconds': 180},
        'interpretation': 'Observations at toy subgroups only; no complexity claim, deployed NIST claim, or causal Solinas advantage.'}
    save(RUN / 'plan.json', plan)
    shutil.copy2(Path(__file__), RUN / 'source/prepare.py')
    print(RUN)

if __name__ == '__main__':
    main()
