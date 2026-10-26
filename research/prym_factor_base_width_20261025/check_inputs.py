"""Independent input/descriptor checks; no producer collector or arithmetic imports."""
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from independent import verify_fixture, multiply


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def public_projection(fixture, sources):
    """Independent canonical signed quotient, including zero/equal/opposite atoms."""
    p, r = fixture['p'], fixture['r']
    images, derivations = {}, []
    for scalar in sources:
        point = multiply(p, 0, fixture['a'], scalar, tuple(fixture['P']))
        if point is None:
            continue
        key = (point[0], min(point[1], -point[1] % p))
        value = scalar if point == key else -scalar % r
        if key in images and images[key] != value:
            raise ValueError('inconsistent public sources')
        if key not in images:
            images[key] = value
            derivations.append(dict(point=list(key), scalar=value,
                                    public_source=scalar, sign=1 if point == key else -1))
    keys = []
    for atom in fixture['factor_base']:
        point = atom['point']
        if point is not None:
            key = (point[0], min(point[1], -point[1] % p))
            if key not in images and key not in keys:
                keys.append(key)
    keys.sort()
    mapping = []
    for atom in fixture['factor_base']:
        point = atom['point']
        if point is None:
            mapping.append(['zero'])
            continue
        key = (point[0], min(point[1], -point[1] % p))
        sign = 1 if tuple(point) == key else -1
        mapping.append(['known', sign*images[key] % r] if key in images else
                       ['unknown', keys.index(key), sign])
    used = {tuple(atom['point'])[:1]+(min(atom['point'][1], -atom['point'][1] % p),)
            for atom in fixture['factor_base'] if atom['point'] is not None}
    return dict(U=len(keys), unknown_points=[list(k) for k in keys],
                native_to_projected=mapping,
                public_derivations=[d for d in derivations if tuple(d['point']) in used])


def validate(config, panel):
    if (config['p'], config['a'], config['curves'], config['reference_width'],
        config['factor_base_size'], config['public_source_max'], config['seeds'],
        config['arms'], config['branches_per_source'], config['new_attempts_per_curve'],
        config['new_attempts_total'], config['new_m8_attempts'], config['early_stop_at_full_rank']) != (
        4099, 2, [{'b': 13, 'r': 4021}, {'b': 16, 'r': 4111}], 8, 16, 64, [0],
        ['m16_full35840'], 35840, 2293760, 4587520, 0, False):
        raise ValueError('wrong fixed width workload')
    if panel['secret_labels_present'] or panel['relation_acceptance_observed']:
        raise ValueError('unlawful public-input metadata')
    old_config = json.loads((ROOT/config['historical_config_file']).read_text())
    old = json.loads((ROOT/config['historical_fixture_file']).read_text())['fixtures']
    if len(panel['fixtures']) != 2:
        raise ValueError('wrong fixture panel')
    checks = []
    for f, expected in zip(panel['fixtures'], config['curves']):
        prior = next(v for v in old if (v['p'], v['a'], v['b']) == (4099, 2, expected['b']))
        if any(f[k] != prior[k] for k in ['p', 'a', 'b', 'r', 'P', 'ec1']):
            raise ValueError('historical curve/generator identity changed')
        verify_fixture(f)
        if f['uid'] != digest({k: f[k] for k in ['p', 'a', 'b', 'r', 'P', 'factor_base']}):
            raise ValueError('new fixture UID mismatch')
        roots = {}
        for y in range(f['p']):
            roots.setdefault(y*y % f['p'], y)
        base, trace, seen = [], [], set()
        for x in range(f['p']):
            u = x*x % f['p']
            y = roots.get((u**3+f['a']*u+f['b']) % f['p'])
            reason = 'not_rational' if y is None else 'norm_already_seen' if u in seen else 'append'
            t = dict(x=x, norm_x=u, canonical_y=y, reason=reason)
            if reason == 'append':
                t['atom_index'] = len(base)
                base.append(dict(point=[u, y], lift=[x, y]))
                seen.add(u)
            trace.append(t)
            if len(base) == 16:
                break
        w = f['width_binding']
        sources = list(range(1, 65))
        derivation = f"{old_config['domain']}|sources|{prior['uid']}|0"
        random.Random(derivation).shuffle(sources)
        required = dict(old_fixture_uid=prior['uid'], old_prefix_sha256=digest(prior['factor_base']),
                        new_base_sha256=digest(base), old_to_new_atoms=list(range(8)),
                        source_order=sources, source_order_sha256=digest(sources),
                        source_order_derivation=derivation, source_order_domain=old_config['domain'],
                        source_order_seed=0, construction_trace=trace,
                        construction_trace_sha256=digest(trace), inherited_x_zero_atom_preserved=True)
        if f['factor_base'] != base or base[:8] != prior['factor_base'] or w != required:
            raise ValueError('wrong append trace, prefix, or historical source schedule')
        new_triples = {triple: j for j, triple in enumerate(combinations(range(16), 3))}
        mapping = []
        for old_index, triple in enumerate(combinations(range(8), 3)):
            for option in range(64):
                mapping.append([64*old_index+option, 64*new_triples[triple]+option])
        if len(mapping) != 3584 or len({x[1] for x in mapping}) != 3584:
            raise ValueError('descriptor inclusion failed')
        checks.append(dict(curve_uid=f['ec1']['curve_uid'], fixture_uid=f['uid'],
                           old_fixture_uid=prior['uid'], old_prefix_sha256=digest(base[:8]),
                           new_base_sha256=digest(base), source_order_sha256=digest(sources),
                           construction_trace_sha256=digest(trace),
                           descriptor_inclusion_count=len(mapping),
                           descriptor_inclusion_map_sha256=digest(mapping),
                           branches_per_source=comb(16, 3)*4**3,
                           projection=public_projection(f, sources),
                           target_relation_acceptance_observed=False))
    run = ROOT/config['historical_run']
    custody_path = ROOT/config['historical_custody']
    expected_paths = {str((run/name).relative_to(ROOT)) for name in [
        'verification.json', 'execution-receipt.json', 'raw-result.json.gz.blob.json', 'events.jsonl.gz.blob.json']}
    expected_paths.update(str(p.relative_to(ROOT)) for p in [custody_path, custody_path.parent/'.artifacts.json'])
    if set(panel['historical_reference_sha256']) != expected_paths:
        raise ValueError('missing/extra historical custody bindings')
    for path, expected in panel['historical_reference_sha256'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError('historical metadata/custody pointer changed')
    historical = json.loads((run/'verification.json').read_text())
    custody = json.loads(custody_path.read_text())
    storage = json.loads((custody_path.parent/'.artifacts.json').read_text())
    if (custody['execution_receipt_sha256'] != sha256((run/'execution-receipt.json').read_bytes()).hexdigest() or
        custody['artifact_sha256']['verification.json'] != sha256((run/'verification.json').read_bytes()).hexdigest()):
        raise ValueError('historical receipt/checker custody mismatch')
    for name in ['raw-result.json', 'events.jsonl']:
        pointer = json.loads((run/(name+'.gz.blob.json')).read_text())
        entry = custody['artifact_storage'][name]
        if any(pointer[k] != entry[k] for k in ['content_sha256', 'content_size', 'encoding', 'sha256', 'size', 'uri']):
            raise ValueError('historical native/canonical storage pointer mismatch')
        if (custody['artifact_sha256'][name] != pointer['content_sha256'] or
            storage['files'][pointer['sha256']+'.bin'] != {'sha256': pointer['sha256'], 'bytes': pointer['size']}):
            raise ValueError('historical logical/stored hash custody mismatch')
    if historical['raw_result_sha256'] != custody['artifact_sha256']['raw-result.json']:
        raise ValueError('historical checker/raw logical content mismatch')
    for c in checks:
        ref = next(v for v in historical['cells'] if v['curve_uid'] == c['old_fixture_uid'] and v['arm'] == 'full3584')
        if (ref['attempts_replayed'], ref['rows_verified'], ref['rank'], ref['U']) != (229376, 0, 0, 7):
            raise ValueError('historical finite reference differs')
    return dict(schema='prym-width-input-validation/v1', status='passed', cells=checks,
                derived_new_attempts_total=4587520, target_relation_acceptance_observed=False,
                constructor_invoked=False, raw_historical_blobs_rehydrated=False,
                historical_positive_embedding='vacuous: zero old m8 rows; separate planted positive test required',
                producer_arithmetic_imported=False)


if __name__ == '__main__':
    result = validate(json.loads((HERE/'config.json').read_text()), json.loads((HERE/'fixtures.json').read_text()))
    with (HERE/'input-validation.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], cells=len(result['cells']), constructor_invoked=False)))
