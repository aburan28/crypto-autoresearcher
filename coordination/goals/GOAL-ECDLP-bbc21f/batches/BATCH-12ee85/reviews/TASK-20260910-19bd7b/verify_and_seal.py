#!/usr/bin/env python3
"""Verify blind-rederivation.yaml against results.json value-by-value, then
seal: compute sha256 of every sealed file and write seal.json.

Runs BEFORE any read outside the packet allowlist. Part of the sealed set."""

import hashlib
import json
import os
import re
from datetime import datetime, timezone

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'results.json')))
Y = yaml.safe_load(open(os.path.join(HERE, 'blind-rederivation.yaml')))['blind_rederivation']

EX = re.compile(r'^exact: (-?\d+)/(\d+)')


def exact_str(v):
    """Render a Fraction-valued results.json entry as it appears in the report."""
    return f"exact: {v['__fraction__']}   (~= {float(v['__float__']):.10g})"


def cmpf(field, got, want):
    if got != want:
        raise SystemExit(f"MISMATCH {field}: report={got!r} results={want!r}")


# ---- frozen cells, in the blind-input order ----
# The report lists all N=2^20 cells before the N=2^24 cells (prohibitions.md
# s4 ordering); within each scale the blind-input order is preserved for the
# a=1/8 seeds, with the a=1/16 cell of that scale following them. This tuple
# list matches the report's actual cell order.
frozen_input_cells = [(1048576, '1/8', 1), (1048576, '1/8', 7),
                      (1048576, '1/8', 13), (1048576, '1/16', 5),
                      (16777216, '1/8', 3), (16777216, '1/8', 11),
                      (16777216, '1/8', 25), (16777216, '1/16', 17)]

assert len(Y['frozen_cells']) == 8 == len(R['frozen_cells'])
for (rep, res, ident) in zip(Y['frozen_cells'], R['frozen_cells'], frozen_input_cells):
    N, a, seed = ident
    assert rep['cell'] == {'N': N, 'a': a, 'seed': seed}, (rep['cell'], ident)
    f, pr, sh, nu, po, p = (rep['fields'], rep['parameters_used'],
                            res['shares'], res['nulls'], res['pool'],
                            res['partition'])
    cmpf('share_top_Tsel', f['share_top_Tsel'], exact_str(sh['share_top_Tsel']))
    cmpf('cov_static', f['cov_static'], exact_str(res['cov_static']))
    cmpf('margin', f['margin'], exact_str(res['margin']))
    cmpf('share_top_T', f['share_top_T'], exact_str(sh['share_top_T']))
    cmpf('share_top_Tover4', f['share_top_Tover4'], exact_str(sh['share_top_Tover4']))
    cmpf('share_top_Tover8', f['share_top_Tover8'], exact_str(sh['share_top_Tover8']))
    cmpf('rho_ORACLE', f['rho_ORACLE'], exact_str(res['rho_ORACLE']))
    cmpf('n_dps', f['n_dps'], p['n_dps'])
    cmpf('cycle_mass', f['cycle_mass'], p['cycle_mass'])
    cmpf('capped_mass', f['capped_mass'], p['capped_mass'])
    cmpf('cap', f['cap'], pr['cap'])
    cmpf('capped_walks', f['capped_walks'], po['capped_walks'])
    cmpf('residual_fraction', f['residual_fraction'],
         exact_str(p['residual_fraction']))
    assert f['accounting_identity_holds'] is True
    assert p['accounting_identity_holds'] is True
    cmpf('min_basin_size', f['min_basin_size'], p['min_basin_size'])
    cmpf('n_tied_at_Tth_weight', f['n_tied_at_Tth_weight'],
         po['n_tied_at_Tth_weight'])
    cmpf('margin_null_oracle_rand_uniform', f['margin_null_oracle_rand_uniform'],
         exact_str(nu['margin_null_oracle_rand_uniform']))
    cmpf('margin_null_oracle_rand_sizebiased',
         f['margin_null_oracle_rand_sizebiased'],
         exact_str(nu['margin_null_oracle_rand_sizebiased']))
    cmpf('margin_null_randsel', f['margin_null_randsel'],
         exact_str(nu['margin_null_randsel']))
    cmpf('cov_static_shuf', f['cov_static_shuf'], exact_str(nu['cov_static_shuf']))
    # parameters
    cmpf('T', pr['T'], res['params']['T'])
    cmpf('T_sel', pr['T_sel'], res['params']['T_sel'])
    cmpf('r', pr['r'], res['params']['r'])
    cmpf('cap_check', pr['cap'], res['params']['cap'])
    cmpf('dp_threshold', pr['dp_threshold'], res['params']['dp_threshold'])

# ---- control families ----
keys = {(1048576, '1/4'): '1048576_1_4', (16777216, '1/4'): '16777216_1_4'}
for fam in Y['control_a_quarter']:
    k = keys[(fam['cell_family']['N'], fam['cell_family']['a'])]
    v = R['control_a_quarter'][k]
    ag = v['aggregate_reading_A']
    cmpf('k_25', fam['k_25'], ag['k_25'])
    cmpf('verdict_25', fam['verdict_25'], ag['verdict_25'])
    cmpf('k_5', fam['k_5'], ag['k_5'])
    cmpf('verdict_5', fam['verdict_5'], ag['verdict_5'])
    cmpf('mean_margin', fam['mean_margin'], exact_str(ag['mean_margin']))
    cmpf('max_residual_fraction', fam['max_residual_fraction'],
         exact_str(ag['max_residual_fraction']))
    assert fam['identity_or_min_basin_violations'] == []

print('report vs results.json: all values verified identical (8 frozen cells,'
      ' 2 control families)')

# ---- seal ----
SEAL_FILES = ['rederive.py', 'check_params.py', 'gen_report.py', 'verify_and_seal.py',
              'results.json', 'blind-rederivation.yaml']


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


seal = dict(
    seal_id='SEAL-TASK-20260910-19bd7b',
    task_id='TASK-20260910-19bd7b',
    phase='1-frozen',
    sealed_at=datetime.now(timezone.utc).isoformat(),
    procedure='MANIFEST.yaml seal_procedure; hashes + UTC timestamp recorded'
              ' before any read outside the four packet files + blind-input.yaml',
    files={name: sha256(os.path.join(HERE, name)) for name in SEAL_FILES},
    pre_seal_correction_note=(
        'blind-rederivation.yaml was regenerated twice BEFORE this seal to fix '
        'YAML formatting defects in my own draft (invalid plain scalars '
        'containing ": " and two under-indented block scalars). No value '
        'changed between the two drafts; the second generation ran from the '
        'same results.json, and verify_and_seal.py then checked every reported '
        'value against results.json before hashing. The sealed artifact is the '
        'file hashed here.'),
    files_read_before_seal=[
        'experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/MANIFEST.yaml',
        'experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/quantity.md',
        'experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/deliverables.md',
        'experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/prohibitions.md',
        'coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/blind-input.yaml',
    ],
)
with open(os.path.join(HERE, 'seal.json'), 'w') as fh:
    json.dump(seal, fh, indent=2)
print('wrote seal.json; sealed files:')
for name, h in seal['files'].items():
    print(' ', name, h)
