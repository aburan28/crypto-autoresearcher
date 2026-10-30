"""Independent copied-object controls, embedding and content-custody audit."""
import copy
import gzip
import hashlib
import itertools
import json
import os
import random
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path('/workspace/crypto-autoresearcher')
BASE = 'experiments/EXP-ECDLP-a9b6a5'
OUT = BASE+'/reviews/TASK-20261025-2fe077'


def run_controls(reader, g, h):
    check, save, Replay = h['check'], h['save'], h['Replay']
    fixtures = json.loads(reader.read('research/prym_factor_base_width_20261025/fixtures.json'))['fixtures']
    raw = json.loads(reader.read(BASE+'/export-inputs/RUN-ECDLP-967315/raw-result.json'))
    event_bytes = reader.read(BASE+'/export-inputs/RUN-ECDLP-967315/events.jsonl')
    events = [json.loads(line) for line in event_bytes.splitlines()]
    controls = []

    def reject(name, payload, action):
        artifact = save('controls/'+name+'.json', payload)
        try:
            action()
        except (ValueError, AssertionError, IndexError, KeyError, StopIteration) as exc:
            controls.append({'control': name, 'rejected': True, 'reason': str(exc), 'artifact': artifact})
        else:
            raise ValueError('known-false control was accepted: '+name)

    f, cell = fixtures[0], raw['cells'][0]
    row = cell['rows'][0]
    for name, scalar in [('source-a-plus1', (row['source_scalar']+1) % f['r']),
                         ('source-uniform-alternative', None)]:
        other = copy.deepcopy(row)
        if scalar is None:
            draw = random.Random('fresh-independent-width-map-null-20261026').randrange(f['r']-1)
            scalar = draw+int(draw >= row['source_scalar'])
        other['source_scalar'] = scalar
        reject(name, other, lambda other=other: h['verify_row'](f, other, g))
    other = copy.deepcopy(row)
    other['constraints'][1][1] = (other['constraints'][1][1]+1) % f['p']
    reject('modified-native-lift', other, lambda: h['verify_row'](f, other, g))
    for name in ['U', 'anchor', 'pivot', 'kernel', 'affine-rank', 'augmented-rank']:
        other = copy.deepcopy(cell)
        projection = other['projection']
        if name == 'U':
            projection['U'] += 1
        elif name == 'anchor':
            projection['native_to_projected'][0] = ['known', 0]
        elif name == 'pivot':
            projection['pivots'] = {}
        elif name == 'kernel':
            projection['right_kernel'][0][0] = (projection['right_kernel'][0][0]+1) % f['r']
        elif name == 'affine-rank':
            projection['rank'] += 1
        else:
            projection['augmented_rank'] += 1
        reject('wrong-'+name, {'projection': projection}, lambda other=other: h['certificate'](f, other, g))
    block = next(v for v in events if v['schema'] == 'prym-width-source-block/v1')
    for name, statuses in [('dropped-status', block['statuses'][:-1]),
                           ('duplicate-status', block['statuses']+block['statuses'][-1])]:
        other = copy.deepcopy(block)
        other['statuses'] = statuses
        reject(name, other, lambda other=other: h['block_identity'](other, f, block['scalar'], 16))
    other = copy.deepcopy(block)
    other['statuses'] = ('+' if block['statuses'][0] != '+' else 'R')+block['statuses'][1:]
    reject('wrong-status-same-length', other,
           lambda: check(other['statuses'] == block['statuses'], 'status differs from already-complete independent replay'))
    other = copy.deepcopy(block)
    other['attempt_digest'] = '0'*64
    reject('wrong-branch-digest', other,
           lambda: check(other['attempt_digest'] == block['attempt_digest'], 'digest differs from already-complete independent replay'))
    source_blocks = [v for v in events if v['schema'] == 'prym-width-source-block/v1']
    expected_sources = [(f['uid'], s) for f in fixtures for s in f['width_binding']['source_order']]
    for name, changed in [('dropped-source-block', source_blocks[:-1]),
                           ('duplicated-source-block', source_blocks+[source_blocks[-1]]),
                           ('wrong-source-order', list(reversed(source_blocks)))]:
        copied_identities = [(v['curve_uid'], v['scalar']) for v in changed]
        reject(name, {'ordered_source_block_identities': copied_identities},
               lambda copied_identities=copied_identities: check(copied_identities == expected_sources, 'incomplete/duplicate/reordered source support'))
    other = copy.deepcopy(fixtures[0]['factor_base'][:8])
    other[1], other[2] = other[2], other[1]
    reject('broken-old8-prefix', other,
           lambda: check(other == fixtures[0]['factor_base'][:8], 'prefix order/point/lift identity differs'))
    transported_fixture, transported = h['transport'](f, row)
    transported['coefficients'][0] = (transported['coefficients'][0]+1) % f['r']
    reject('broken-transported-encoding', transported,
           lambda: h['verify_row'](transported_fixture, transported, g))

    # A genuinely positive prefix witness on the predeclared p101 software
    # fixture, reconstructed with fresh arithmetic. No p4099 source selection.
    p, a, b = 101, 2, 21
    cg = dict(g)
    def software_sqrt(n, p):
        if p % 4 == 3:
            return g['square_root'](n, p)
        roots = [y for y in range(p) if y*y % p == n % p]
        return min(roots) if roots else None
    cg['square_root'] = software_sqrt
    ec = g['EC'](p, a, b)
    r = ec.cardinality()
    check(g['prime'](r), 'planted fixture order is not prime')
    P = next((x, y) for x in range(p) for y in [software_sqrt(x**3+a*x+b, p)] if y is not None)
    base, seen = [], set()
    for x in range(p):
        y = software_sqrt(x**6+a*x*x+b, p)
        u = x*x % p
        if y is not None and u not in seen:
            base.append({'point': [u, y], 'lift': [x, y]})
            seen.add(u)
            if len(base) == 16:
                break
    planted8 = {'p': p, 'a': a, 'b': b, 'r': r, 'P': list(P),
                'uid': 'fresh-independent-p101-prefix-control', 'factor_base': base[:8]}
    planted16 = dict(planted8, factor_base=base)
    replay8 = Replay(planted8, cg)
    planted, label, tried = None, None, 0
    for scalar in (1, 2, 3, 4):
        if planted is not None:
            break
        for triple in itertools.combinations(range(8), 3):
            if planted is not None:
                break
            for options in itertools.product(range(4), repeat=3):
                tried += 1
                status, ident, candidate = replay8.outcome(scalar, triple, options)
                if candidate is not None:
                    planted, label = candidate, (scalar, triple, options)
                    break
    check(planted is not None, 'planted old8 path failed to find known positive')
    h['verify_row'](planted8, planted, g)
    replay16 = Replay(planted16, cg)
    status16, ident16, row16 = replay16.outcome(*label)
    check(status16 == '+' and row16 is not None, 'planted prefix did not embed')
    h['verify_row'](planted16, row16, g)
    padded = copy.deepcopy(planted)
    padded['coefficients'] += [0]*8
    check(row16 == padded, 'positive prefix geometry/equation differs')
    scalar, triple, options = label
    points, _ = replay8.descriptor(scalar, triple, options)
    original_id = replay8.identity(scalar, triple, options, points)
    opposite = (r-scalar, triple, tuple(op ^ 1 for op in options))
    alias_status, alias_id, alias_row = replay8.outcome(*opposite)
    check(alias_status == 'A' and alias_id == original_id and alias_row is None, 'planted alias did not alias')
    reject('changed-canonical-alias-key', {'actual': original_id, 'copied_wrong': '0'*64},
           lambda: check(original_id == '0'*64, 'copied canonical key differs from independent four-way identity'))
    planted_artifact = save('controls/positive-prefix-and-alias.json',
                            {'fixture8': planted8, 'fixture16': planted16, 'row8': planted,
                             'row16': row16, 'descriptor': label, 'attempts_until_positive': tried,
                             'opposite_descriptor': opposite, 'alias_identity': alias_id})
    result = {'schema': 'prym-fresh-independent-controls/v1', 'generated_at': g['now'](),
              'status': 'passed', 'known_false_copies': controls,
              'positive_prefix': {'passed': True, 'p': p, 'a': a, 'b': b,
                                  'attempts_until_positive': tried, 'artifact': planted_artifact},
              'alias_positive': {'passed': True, 'source': scalar, 'opposite_source': r-scalar},
              'scope': 'Separate copied objects and declared p101 software fixture only; no producer repair or new p4099 scientific workload.'}
    artifact = save('control-verification.json', result)
    print(json.dumps({'controls_done': artifact, 'negative_count': len(controls)}), flush=True)
    return result


def run_reference(reader, g, h):
    check, save, Replay = h['check'], h['save'], h['Replay']
    fixtures = json.loads(reader.read('research/prym_factor_base_width_20261025/fixtures.json'))['fixtures']
    old_panel = json.loads(reader.read('research/prym_rank_census_20261025/fixtures.json'))
    old_config = json.loads(reader.read('research/prym_rank_census_20261025/config.json'))
    raw = json.loads(reader.read(BASE+'/export-inputs/RUN-ECDLP-ea49a6/raw-result.json'))
    all_records = [json.loads(line) for line in reader.read(BASE+'/export-inputs/RUN-ECDLP-ea49a6/events.jsonl').splitlines()]
    checks = []
    for new in fixtures:
        uid = new['width_binding']['old_fixture_uid']
        old = next(f for f in old_panel['fixtures'] if f['uid'] == uid)
        check(all(old[k] == new[k] for k in ('p','a','b','r','P')), 'changed source curve/P')
        check(old['factor_base'] == new['factor_base'][:8], 'old8 prefix differs from archived public fixture')
        order = list(range(1, 65))
        random.Random(old_config['domain']+'|sources|'+uid+'|0').shuffle(order)
        check(order == new['width_binding']['source_order'], 'historical UID/domain source order changed')
        records = [v for v in all_records if v['curve_uid'] == uid and v['arm'] == 'full3584' and v['seed'] == 0]
        check([v['scalar'] for v in records] == order and len(records) == 64, 'historical source coverage differs')
        cell = next(c for c in raw['cells'] if c['curve_uid'] == uid and c['arm'] == 'full3584' and c['seed'] == 0)
        ref, extension = Replay(old, g), Replay(new, g)
        # Compare canonical identities only after explicit fixture-label transport.
        identity_transport = Replay(dict(old, uid=new['uid']), g)
        attempts, accepted, descriptors, keys = 0, 0, 0, 0
        counts = Counter()
        digests = []
        for scalar, block in zip(order, records):
            ref.interpolation_plans.clear()
            commitment = hashlib.sha256()
            check(len(block['statuses']) == 3584, 'old8 status coverage differs')
            for t, triple in enumerate(itertools.combinations(range(8), 3)):
                for option in range(64):
                    options = (option//16, option//4 % 4, option % 4)
                    branch = 64*t+option
                    attempts += 1
                    status, ident, row = ref.outcome(scalar, triple, options)
                    check(status == block['statuses'][branch], 'old8 validation replay status differs')
                    commitment.update(json.dumps([scalar, branch, ident, status], separators=(',', ':')).encode()+b'\n')
                    counts[status] += 1
                    accepted += int(row is not None)
                    points8, reason8 = ref.descriptor(scalar, triple, options)
                    points16, reason16 = extension.descriptor(scalar, triple, options)
                    check((points8, reason8) == (points16, reason16), 'old8 descriptor geometry not embedded')
                    descriptors += 1
                    if points8 is not None:
                        check(identity_transport.identity(scalar, triple, options, points8) ==
                              extension.identity(scalar, triple, options, points16), 'canonical key differs under old-to-new fixture transport')
                        keys += 1
            check(commitment.hexdigest() == block['attempt_digest'], 'old8 branch digest differs')
            digests.append(commitment.hexdigest())
        check(attempts == cell['attempts'] == 229376 and counts == Counter(cell['reasons']), 'historical totals differ')
        check(accepted == len(cell['rows']) == 0, 'historical zero-row observation differs')
        check(len(ref.seen) == cell['distinct_candidates'], 'historical alias count differs')
        check(cell['projection']['U'] == 7 and cell['projection']['rank'] == cell['projection']['augmented_rank'] == 0, 'historical finite rank differs')
        check(len(cell['nullspace']) == 7 and h['rank'](cell['nullspace'], old['r']) == 7, 'historical empty-matrix kernel differs')
        checks.append({'b': old['b'], 'old_fixture_uid': uid, 'attempts_validation_replayed': attempts,
                       'accepted_rows': accepted, 'U': 7, 'rank': 0,
                       'descriptor_inclusions_checked': descriptors,
                       'canonical_keys_checked_under_fixture_UID_transport': keys,
                       'full_source_digests': digests, 'old8_empirical_accepted_embedding': 'vacuous: zero recorded old8 rows'})
        print(json.dumps({'reference_b': old['b'], 'attempts': attempts, 'descriptor_embedding': descriptors}), flush=True)
    result = {'schema': 'prym-fresh-independent-reference/v1', 'generated_at': g['now'](),
              'status': 'passed', 'cells': checks,
              'validation_attempts': sum(c['attempts_validation_replayed'] for c in checks),
              'new_scientific_m8_attempts': 0,
              'limitation': 'Reference validation replay is restricted to the two frozen p4099 full3584 cells. Other historical cells are bound as raw bytes but not independently replayed.'}
    print(json.dumps({'reference_done': save('reference-verification.json', result)}), flush=True)
    return result


def run_custody(reader, g, h):
    check, save = h['check'], h['save']
    handoff = yaml.safe_load(reader.read('ledger/handoffs/TASK-20261025-2fe077.yaml'))['handoff']
    allowed = handoff['review_plan']['blind_rederivation']['phased_release']['phase2_allowed']
    records, failures, cache_accesses = [], [], []

    def read(path):
        path = str((ROOT/path).resolve().relative_to(ROOT))
        check(any(path == p.rstrip('/') or (p.endswith('/') and path.startswith(p)) for p in allowed), 'custody source outside allowlist: '+path)
        body = reader.read(path)
        records.append({'path': path, 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)})
        return body

    trial_bytes = read(BASE+'/trial-plan.json')
    trial = json.loads(trial_bytes)
    bindings = json.loads(read('research/prym_factor_base_width_20261025/source-bindings.json'))
    bound = {}
    for kind in ('source_sha256', 'input_sha256'):
        for path, expected in trial[kind].items():
            body = read(path)
            check(hashlib.sha256(body).hexdigest() == expected, 'native bound content differs: '+path)
            bound[path] = expected
        for path, expected in bindings[kind].items():
            check(trial[kind].get(path) == expected, 'source binding omitted from native plan: '+path)
    check(trial['execution_plan']['protocol_hashes'] == [{'path': BASE+'/protocol.json', 'sha256': bound[BASE+'/protocol.json']}], 'protocol full-file binding differs')
    runs = []
    for runid, exp in [('RUN-ECDLP-967315', 'EXP-ECDLP-a9b6a5'), ('RUN-ECDLP-ea49a6', 'EXP-ECDLP-d6d8e8')]:
        cache = BASE+'/export-inputs/'+runid
        native = 'experiments/'+exp+'/runs/'+runid
        delivery = 'experiments/'+exp+'/artifact-deliveries/'+runid
        logical = {name: read(cache+'/'+name) for name in
                   ('raw-result.json','events.jsonl','manifest.yaml','execution-receipt.json','launch.json','environment.json','verification.json')}
        receipt = json.loads(logical['execution-receipt.json'])
        manifest = yaml.safe_load(logical['manifest.yaml'])['run']
        launch = json.loads(logical['launch.json'])
        environment = json.loads(logical['environment.json'])
        verify = json.loads(logical['verification.json'])
        custody_bytes = read(delivery+'/custody.json')
        custody = json.loads(custody_bytes)
        store_manifest = json.loads(read(delivery+'/.artifacts.json'))
        check(custody['execution_receipt_sha256'] == hashlib.sha256(logical['execution-receipt.json']).hexdigest(), 'custody receipt differs')
        check(receipt['status'] == 'output_validated' and receipt['returncode'] == receipt['check_returncode'] == 0, 'native receipt unsuccessful')
        check(receipt['run_id'] == manifest['id'] == launch['run_id'] == runid, 'run identity differs')
        check(receipt['manifest_completion']['driver_manifest_sha256'] == hashlib.sha256(logical['manifest.yaml']).hexdigest(), 'native manifest digest differs')
        check(manifest['code']['commit'] == receipt['authority']['commit'] == launch['authority']['commit'], 'native revision differs')
        check(manifest['code']['dirty_tree'] == '', 'native run not clean')
        check(receipt['authority'] == launch['authority'], 'launch/receipt authority differs')
        check(verify['status'] == 'passed', 'native checker failed')
        if runid == 'RUN-ECDLP-967315':
            check(receipt['plan_sha256'] == launch['plan_sha256'] == hashlib.sha256(trial_bytes).hexdigest(), 'native plan differs')
            check(manifest['code']['source_sha256'] == trial['source_sha256'], 'manifest source closure differs')
            for key, value in trial['input_sha256'].items():
                check(manifest['inputs']['sha256'].get(key) == value, 'manifest input binding differs: '+key)
            check(launch['argv'][1:] == manifest['code']['command'], 'actual argv differs')
        for name, expected in receipt['artifact_sha256'].items():
            body = logical[name] if name in logical else read(native+'/'+name)
            check(hashlib.sha256(body).hexdigest() == expected, 'receipt artifact content differs: '+name)
            check(custody['artifact_sha256'].get(name) == expected, 'custody artifact content differs: '+name)
        storage_checks = []
        for name, storage in receipt['artifact_storage'].items():
            check(custody['artifact_storage'][name] == storage, 'custody storage metadata differs')
            body = logical[name]
            check(len(body) == storage['content_size'] and hashlib.sha256(body).hexdigest() == storage['content_sha256'], 'logical raw content differs')
            if storage['path'].endswith('.blob.json'):
                pointer = json.loads(read(native+'/'+storage['path']))
                check(all(pointer.get(k) == storage.get(k) for k in ('sha256','size','content_sha256','content_size','encoding','uri')), 'pointer/receipt metadata differs')
                cachepath = Path('/tmp/prym-current-native-blob-cache/sha256') / storage['sha256'][:2] / storage['sha256']
                # Public stored-byte cache is outside attested repository scope.
                stored = cachepath.read_bytes()
                cache_accesses.append({'path': str(cachepath), 'sha256': hashlib.sha256(stored).hexdigest(), 'bytes': len(stored), 'access': 'existing public local cache; no remote GET'})
                object_entry = next(o for o in custody['objects'] if o['sha256'] == storage['sha256'])
                check(object_entry['fresh_get_sha256_verified'] is True, 'producer GET attestation absent')
                entry = store_manifest['files'][object_entry['manifest_name']]
                check(entry == {'sha256': storage['sha256'], 'bytes': storage['size']}, 'object manifest differs')
            else:
                stored = read(native+'/'+storage['path'])
            check(len(stored) == storage['size'] and hashlib.sha256(stored).hexdigest() == storage['sha256'], 'stored raw bytes differ')
            check(gzip.decompress(stored) == body, 'stored/raw decompression differs')
            # Independent false pointer/content copies, never mutate originals.
            false_pointer = copy.deepcopy(storage)
            false_pointer['content_sha256'] = '0'*64
            payload = save('controls/false-pointer-'+runid+'-'+name.replace('.', '-')+'.json', false_pointer)
            try:
                check(hashlib.sha256(body).hexdigest() == false_pointer['content_sha256'], 'copied logical-content digest rejected')
            except ValueError as exc:
                rejected = str(exc)
            else:
                raise ValueError('wrong pointer accepted')
            storage_checks.append({'name': name, 'logical_sha256': storage['content_sha256'],
                                   'logical_bytes': len(body), 'stored_sha256': storage['sha256'],
                                   'stored_bytes': len(stored), 'decompressed_equal': True,
                                   'false_pointer_copy': payload, 'false_pointer_rejected': rejected})
        runs.append({'run_id': runid, 'receipt_sha256': hashlib.sha256(logical['execution-receipt.json']).hexdigest(),
                     'manifest_sha256': hashlib.sha256(logical['manifest.yaml']).hexdigest(),
                     'source_commit': manifest['code']['commit'], 'clean_native_manifest': True,
                     'artifact_count': len(receipt['artifact_sha256']), 'storage': storage_checks,
                     'native_environment': environment, 'producer_recorded_fresh_GET': custody['fresh_object_readback_verified'],
                     'own_fresh_remote_GET': False,
                     'historical_source_closure_limit': None if runid == 'RUN-ECDLP-967315' else
                        'Historical source/input maps retained and digest-bound in manifest; only the current prospective exact allowed closure was content-rechecked. Excluded historical private fixture/helper paths were not read.'})
    export_bytes = read(BASE+'/export.json')
    export = json.loads(export_bytes)
    protocol = json.loads(read(BASE+'/protocol.json'))
    canonical = hashlib.sha256(h['text_bytes']({k:v for k,v in protocol.items() if k != 'freeze'})).hexdigest()
    check(canonical == protocol['freeze']['protocol_sha256'] == export['protocol']['sha256'], 'canonical protocol digest differs')
    files = []
    for item in export['files'] + export['analysis']['outputs'] + [export['analysis']['script']]:
        path = str((ROOT/BASE/item['path']).resolve().relative_to(ROOT))
        body = read(path)
        check(hashlib.sha256(body).hexdigest() == item['sha256'] and len(body) == item['bytes'], 'export file differs: '+path)
        files.append(path)
    check(len(export['runs']) == 4 and len({v['run_id'] for v in export['runs']}) == 4, 'export row coverage differs')
    check(export['flow'] == {'planned':4,'attempted':4,'completed':4,'not_completed':0,'interrupted':0,'resumed':0,'excluded':[]}, 'export flow differs')
    check(all(v is None for v in export['producer'].values()), 'missing producer metadata silently populated')
    result = {'schema': 'prym-fresh-independent-custody/v1', 'generated_at': g['now'](),
              'status': 'passed', 'current_source_input_files_rehashed': len(bound),
              'current_source_input_sha256': bound, 'native_runs': runs,
              'public_stored_byte_cache_accesses': cache_accesses,
              'actual_repository_content_reads': records,
              'export_sha256': hashlib.sha256(export_bytes).hexdigest(), 'export_id': export['export_id'],
              'export_rows': 4, 'export_file_hashes_verified': len(files),
              'protocol_canonical_sha256': canonical, 'producer_metadata_missing': list(export['producer']),
              'own_fresh_remote_GET': False,
              'limitations': ['Local cached and stored-byte equality is independently checked. Producer remote-GET records are not reviewer remote requests.',
                              'Content binding and local chronology do not authenticate publication time, execution prescription or absence of undisclosed reads.',
                              'Recorded native counters remain partial and are not independently instrumented primitive costs.'],
              'prescribed_execution_proof': False}
    artifact = save('custody-verification.json', result)
    print(json.dumps({'custody_done': artifact, 'bound_files': len(bound), 'export_files': len(files)}), flush=True)
    return result
