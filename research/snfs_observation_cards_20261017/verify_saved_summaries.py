"""Mechanical recheck of saved descriptive tables, not scientific review."""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import csv
import hashlib
import json


folder = Path(__file__).resolve().parent
root = folder.parents[1]
summary = json.loads((folder/'observations.json').read_text())
data = {}
for name, binding in summary['source_bindings'].items():
    path = root/binding['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256']
    data[name] = json.loads(path.read_text())
assert hashlib.sha256((folder/'analyze_archived.py').read_bytes()).hexdigest() == summary['analysis_source_sha256']

with (folder/'rotation-density.csv').open() as handle:
    rotation = list(csv.DictReader(handle))
assert len(rotation) == 45
for row in rotation:
    c,m = int(row['c']),int(row['m'])
    cells = [x for x in data['rotation']['cells'] if x['c']==c and x['m']==m]
    records = [x[row['arm']] for x in cells]
    assert int(row['density_hits']) == sum(x['density_hits'] for x in records)
    assert int(row['density_draws']) == sum(x['density_n'] for x in records)
    assert float(row['point_density']) == int(row['density_hits'])/int(row['density_draws'])
    assert float(row['point_density_min']) == min(x['density'] for x in records)
    assert float(row['point_density_max']) == max(x['density'] for x in records)
checks = json.loads((folder/'binary-count-checks.json').read_text())
assert len(checks)==27 and all(x['formula_count']==x['enumerated_count'] for x in checks)

with (folder/'e3-target-outcomes.csv').open() as handle:
    e3 = list(csv.DictReader(handle))
assert len(e3)==18
for row in e3:
    key = int(row['p']),int(row['d']),row['mode'],int(row['trial'])
    generic = [x for x in data['e3_generic']['rows'] if (x['p'],x['d'],x['mode'],x['trial'])==key]
    geom = [x for x in data['e3_geometry']['rows'] if (x['p'],x['d'],x['mode'],x['trial'])==key]
    assert len(generic)==2 and len(geom)==1
    for saved in generic:
        assert row[saved['method']+'_status']==saved['solver']['status']
        assert [int(row['target_x']),int(row['target_y'])]==saved['R']
    assert row['geometry_status']==geom[0]['solver']['status']
assert all(x['raw_status']==x['jet_status']=='timeout' for x in e3 if int(x['d'])==2)

indices = defaultdict(list)
for i,cell in enumerate(data['field_lift']['cells']):
    key = json.dumps(dict(g=cell['field']['g'],p=str(cell['field']['p']),
        root=str(cell['root_mod_p']),A=str(cell['curve']['A']),B=str(cell['curve']['B']),
        seed=cell['seed']),sort_keys=True)
    indices[key].append(i)
assert len(indices)==summary['field_lift_summary']['distinct_seed_inclusive_keys']
expected = {tuple(v) for v in indices.values() if len(v)>1}
saved = json.loads((folder/'field-lift-repeat-groups.json').read_text())
assert {tuple(x['row_indices']) for x in saved}==expected
assert dict(sorted(Counter(map(len,indices.values())).items())) == {
    int(k):v for k,v in summary['field_lift_summary']['multiplicity_histogram'].items()}
for rows in indices.values():
    if len(rows)>1:
        assert len({json.dumps(data['field_lift']['cells'][i]['rungs'],sort_keys=True) for i in rows})==1
        assert len({json.dumps(data['field_lift']['cells'][i]['sample_points'],sort_keys=True) for i in rows})==1
assert any(x['g']==[-1,1,0,1] and x['p']=='4111' and x['A']=='-16' and x['B']=='11'
           and x['seed']==3 and x['multiplicity']==10 for x in saved)

result = dict(scope='Mechanical recheck of derived tables only',source_hashes_match=True,
    rotation_rows_checked=len(rotation),e3_target_joins_checked=len(e3),
    repeated_key_groups_checked=len(saved),saved_binary_identity_checks=len(checks),
    all_checks_passed=True,independent_scientific_review=False,original_outputs_modified=False)
parser = argparse.ArgumentParser()
parser.add_argument('--receipt',type=Path,default=folder/'verification.json')
receipt = parser.parse_args().receipt
with receipt.open('x') as handle:
    json.dump(result,handle,indent=2);handle.write('\n')
print(json.dumps(result,indent=2))
