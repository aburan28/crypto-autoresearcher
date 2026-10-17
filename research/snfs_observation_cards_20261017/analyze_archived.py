"""Descriptive arithmetic on immutable saved data; no curve/solver reruns.

The additional binary-word calculation is an exact combinatorial reference,
with small independent enumeration checks. It is not a point-density model.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import csv
import hashlib
import json
import subprocess


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
INPUTS = {
    'rotation': 'experiments/EXP-ECDLP-ad27ad/runs/RUN-ECDLP-a5281a/raw-result.json',
    'field_lift': 'experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-e89532/raw-result.json',
    'e3_generic': 'research/snfs_ecdlp_ledger_20261017/snfs-ecdlp-followup/blind-results.json',
    'e3_geometry': 'research/snfs_ecdlp_ledger_20261017/snfs-ecdlp-followup/geometry-results.json',
}


def multiply(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def accepted_binary_words(c, m):
    """Integers 0 <= x < 2^c-1 with a cyclic run of m zero bits.

    The m-state automaton tracks trailing zero-run length below m. Its closed
    walks count cyclic binary strings without m zeroes; all-ones is excluded
    from the field representatives and all-zeroes is accepted.
    """
    if not 1 <= m <= c:
        raise ValueError('Require 1 <= m <= c')
    a = [[0] * m for _ in range(m)]
    for i in range(m):
        a[i][0] += 1
        if i + 1 < m:
            a[i][i+1] += 1
    power = [[int(i == j) for j in range(m)] for i in range(m)]
    exponent = c
    while exponent:
        if exponent & 1:
            power = multiply(power, a)
        a = multiply(a, a)
        exponent //= 2
    trace = sum(power[i][i] for i in range(m))
    return (1 << c) - trace


def direct_binary_count(c, m):
    count = 0
    for x in range((1 << c) - 1):
        bits = format(x, f'0{c}b')
        cyclic = bits + bits[:m-1]
        count += '0' * m in cyclic
    return count


def write_json(name, value):
    with (OUT / name).open('x') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


def write_csv(name, rows):
    with (OUT / name).open('x', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def full_key(cell, include_seed=True):
    key = (tuple(cell['field']['g']), str(cell['field']['p']), str(cell['root_mod_p']),
           str(cell['curve']['A']), str(cell['curve']['B']))
    return key + (cell['seed'],) if include_seed else key


def main():
    data = {k: json.loads((ROOT / path).read_text()) for k, path in INPUTS.items()}
    bindings = {k: {'path': path, 'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
                for k,path in INPUTS.items()}
    finite_checks = []
    for c in range(4, 13):
        for m in (1,2,4):
            formula, direct = accepted_binary_words(c,m), direct_binary_count(c,m)
            assert formula == direct
            finite_checks.append(dict(c=c, m=m, formula_count=formula, enumerated_count=direct))

    rotation_rows = []
    for c in (13,17,19,31,61):
        for m in (1,2,4):
            cells = [x for x in data['rotation']['cells'] if (x['c'],x['m']) == (c,m)]
            assert len(cells) == 6
            assert len({(x['seed'],x['curve']) for x in cells}) == 6
            ref = Fraction(accepted_binary_words(c,m), (1 << c)-1)
            for arm in ('rot','hash','size_random_prime'):
                hits = sum(x[arm]['density_hits'] for x in cells)
                n = sum(x[arm]['density_n'] for x in cells)
                rotation_rows.append(dict(c=c,m=m,arm=arm,cells=len(cells),density_hits=hits,
                    density_draws=n,point_density=hits/n,
                    point_density_min=min(x[arm]['density'] for x in cells),
                    point_density_max=max(x[arm]['density'] for x in cells),
                    exact_x_density_numerator=ref.numerator,
                    exact_x_density_denominator=ref.denominator,
                    exact_x_density=float(ref),nominal_single_interval_density=2**(-m)))

    # Join by the target identity used by the geometry program, which reads the
    # raw generic-input rows. These are 18 targets, not 36 independent targets.
    target_key = lambda row: (row['p'],row['d'],row['mode'],row['trial'])
    geometry = {target_key(row): row for row in data['e3_geometry']['rows']}
    assert len(geometry) == 18
    targets = defaultdict(dict)
    for row in data['e3_generic']['rows']:
        key = target_key(row)
        assert row['method'] not in targets[key]
        targets[key][row['method']] = row
    assert set(targets) == set(geometry)
    e3_rows = []
    for key, methods in sorted(targets.items()):
        assert set(methods) == {'raw','jet'}
        raw, jet, geom = methods['raw'], methods['jet'], geometry[key]
        assert raw['R'] == jet['R']
        e3_rows.append(dict(p=key[0],d=key[1],mode=key[2],trial=key[3],
            target_x=raw['R'][0],target_y=raw['R'][1],raw_status=raw['solver']['status'],
            jet_status=jet['solver']['status'],geometry_status=geom['solver']['status'],
            geometry_verified=geom['solver'].get('verified'),
            raw_wall_cap_seconds=raw['solver'].get('wall_cap_seconds'),
            jet_wall_cap_seconds=jet['solver'].get('wall_cap_seconds')))
    e3_summary = []
    for d in (1,2):
        rows = [r for r in e3_rows if r['d'] == d]
        e3_summary.append(dict(d=d,unique_targets=len(rows),
            raw_statuses=dict(Counter(x['raw_status'] for x in rows)),
            jet_statuses=dict(Counter(x['jet_status'] for x in rows)),
            geometry_statuses=dict(Counter(x['geometry_status'] for x in rows))))

    cells = data['field_lift']['cells']
    groups = defaultdict(list)
    algebraic = defaultdict(list)
    for index, cell in enumerate(cells):
        groups[full_key(cell)].append((index,cell))
        algebraic[full_key(cell,False)].append((index,cell))
    repeat_groups = []
    for key, rows in groups.items():
        if len(rows) < 2:
            continue
        profiles = {json.dumps(c['rungs'],sort_keys=True) for _,c in rows}
        samples = {json.dumps(c['sample_points'],sort_keys=True) for _,c in rows}
        repeat_groups.append(dict(g=list(key[0]),p=key[1],root_mod_p=key[2],
            A=key[3],B=key[4],seed=key[5],multiplicity=len(rows),
            row_indices=[i for i,_ in rows],
            labels=[dict(kind=c['field']['kind'],shape=c['field']['shape'],k=c['field']['k'],
                         curve_index=c['curve_index']) for _,c in rows],
            distinct_saved_rung_profiles=len(profiles),distinct_saved_sample_lists=len(samples)))
    repeat_groups.sort(key=lambda r:(-r['multiplicity'],r['row_indices'][0]))
    field_summary = dict(recorded_rows=len(cells),
        distinct_algebraic_keys=len(algebraic),distinct_seed_inclusive_keys=len(groups),
        additional_rows_beyond_seed_inclusive_keys=len(cells)-len(groups),
        seed_inclusive_repeat_groups=len(repeat_groups),
        largest_multiplicity=max(map(len,groups.values())),
        multiplicity_histogram=dict(sorted(Counter(map(len,groups.values())).items())),
        repeat_groups_with_different_rung_profiles=sum(r['distinct_saved_rung_profiles']>1 for r in repeat_groups),
        repeat_groups_with_different_sample_lists=sum(r['distinct_saved_sample_lists']>1 for r in repeat_groups),
        key_definition=['g coefficients','p','reduction root','curve A','curve B','seed'],
        note='A key partition, not an independence test or a classification up to field isomorphism. Original rows are retained.')
    write_csv('rotation-density.csv',rotation_rows)
    write_csv('e3-target-outcomes.csv',e3_rows)
    write_json('field-lift-repeat-groups.json',repeat_groups)
    write_json('binary-count-checks.json',finite_checks)
    result = dict(scope='Retrospective descriptive arithmetic on archived observations',
        source_checkout_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_bindings=bindings,analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        rotation=rotation_rows,e3_summary=e3_summary,field_lift_summary=field_summary,
        curve_or_solver_reruns=0,binary_identity_checks=len(finite_checks),
        original_run_statuses_changed=False,owner_interpretation_requested=False,
        limitations=['Exploratory summaries, not preregistered significance tests.',
                     'Rotation field-x densities and sampled point densities have different domains.',
                     'Min/max over six cells is spread, not a confidence interval.',
                     'E3 timeouts are censored outcomes under a 4-second wall cap.',
                     'G3/G4 producer and checker returned zero; supervisor retained invalid_output for legacy manifests.'])
    write_json('observations.json',result)
    print(json.dumps({'rotation_groups':15,'e3':e3_summary,'field_lift':field_summary,
                      'binary_identity_checks':len(finite_checks)},indent=2))


if __name__ == '__main__':
    main()
