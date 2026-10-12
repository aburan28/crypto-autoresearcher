"""Full hashes/on-curve/replayed features plus a separate affine EC oracle."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
from research import canonical, check_source, digest, immutable, jobs
from metrics import features, decode
from oracle import add, multiply, scalar_draw
from native import seed_for


def x_triple_relation(curve, xs, generator_x):
    # For Q-H, Q, Q+H on any short Weierstrass curve. Derived by adding
    # the two affine addition formulas; no assumption about Solinas p.
    left, middle, right = xs; p = curve['p']; u = generator_x
    return ((left+right)*(middle-u)**2 - 2*((middle*u+curve['A'])*(middle+u)+2*curve['B'])) % p == 0


def verify_job(job, output, config, design_sha):
    output = Path(output); record = json.loads((output/'records'/(job['id']+'.json')).read_text())
    if record['job'] != job or record['design_sha256'] != design_sha: raise ValueError('Provenance differs')
    raw = (output/record['raw']['path']).read_bytes(); curve = job['curve']; p = curve['p']; width = (p.bit_length()+7)//8
    if len(raw) != job['points']*2*width or hashlib.sha256(raw).hexdigest() != record['raw']['sha256']:
        raise ValueError('Raw dimensions/hash differ')
    coords = decode(raw, p)
    for x, y in coords:
        if not (0 <= x < p and 0 <= y < p) or (y*y-x*x*x-curve['A']*x-curve['B']) % p:
            raise ValueError('Raw point outside curve')
    totals = {'points': len(coords), 'raw_bytes': len(raw), 'unit_feature_replays': 0,
              'affine_transitions': 0, 'scalar_checks': 0, 'generator_checks': 0,
              'triple_relations': 0, 'wrong_step_hits': 0, 'wrong_step_trials': 0,
              'shuffled_triple_hits': 0, 'shuffled_triple_trials': 0, 'transport_points': 0}
    end = 0
    for unit in record['units']:
        begin, count = unit['offset_points'], unit['points']
        if begin != end: raise ValueError('Units do not partition raw bytes')
        end = begin+count; selected = coords[begin:end]; part = raw[begin*2*width:end*2*width]
        if features(part, p) != unit['features']: raise ValueError('Features fail full raw replay')
        totals['unit_feature_replays'] += 1
        if unit['generator'] is not None:
            h = tuple(unit['generator']); x, y = h
            if not (0 <= x < p and 0 <= y < p) or (y*y-x*x*x-curve['A']*x-curve['B']) % p:
                raise ValueError('Generator outside curve')
            totals['generator_checks'] += 1
        if unit['mode'] in (1, 3):
            positions = sorted({i*(count-3)//7 for i in range(8)})
            for position in positions:
                if add(curve, selected[position], h) != selected[position+1]: raise ValueError('Wrong affine recurrence')
                totals['affine_transitions'] += 1
                if not x_triple_relation(curve, [selected[position+j][0] for j in range(3)], h[0]):
                    raise ValueError('Universal x-coordinate triple relation failed')
                totals['triple_relations'] += 1
            check_start = ((job['kind'] == 'walk' and job['block'] < config['diagnostic_blocks']) or
                           job['kind'] in ('prefix', 'target') or
                           (job['kind'] == 'bank' and unit['generator_index'] % 256 == 0))
            if check_start:
                k = config['prefix_skip']+1 if unit['mode'] == 3 else scalar_draw(bytes.fromhex(unit['seed_hex']), curve['N'])[0]
                if multiply(curve, h, k) != selected[0]: raise ValueError('Independent scalar/start differs')
                totals['scalar_checks'] += 1
                if unit.get('generator_seed_hex'):
                    r, used = scalar_draw(bytes.fromhex(unit['generator_seed_hex']), curve['N'])
                    if multiply(curve, tuple(job['published_G']), r) != h: raise ValueError('Random generator scalar differs')
                    totals['scalar_checks'] += 1
        if 'isomorphic_u2' in unit:
            for x, y in selected:
                tx, ty = 4*x % p, 8*y % p
                if (ty*ty-tx*tx*tx-16*curve['A']*tx-64*curve['B']) % p:
                    raise ValueError('Isomorphic point transport fails')
            totals['transport_points'] += len(selected)
        if job['kind'] == 'walk' and job['block'] < config['diagnostic_blocks']:
            # These controls reuse the same points; they are diagnostics, not
            # independent samples or an ECDLP advantage.
            double_g = multiply(curve, tuple(job['published_G']), 2)
            wrong_x = double_g[0]
            if wrong_x == h[0]: raise ValueError('Wrong-step control accidentally has the correct x')
            rng = __import__('numpy').random.default_rng(int.from_bytes(seed_for(config['seed'], job['id'], unit['label'], 'shuffle')[:8], 'big'))
            shuffled = [selected[i] for i in rng.permutation(len(selected))]
            for i in range(16):
                totals['wrong_step_trials'] += 1
                totals['wrong_step_hits'] += int(x_triple_relation(curve, [selected[i+j][0] for j in range(3)], wrong_x))
                totals['shuffled_triple_trials'] += 1
                totals['shuffled_triple_hits'] += int(x_triple_relation(curve, [shuffled[i+j][0] for j in range(3)], h[0]))
            if record['diagnostics'][unit['label']]['sorted']['perm_gap'] < 2.58:
                raise ValueError('Structured positive control missed')
    if end != len(coords): raise ValueError('Unused or duplicated points')
    if job['kind'] == 'bank' and job['block'] % 32 == 0:
        counter = 0; seed = bytes.fromhex(record['diagnostics']['generator_bank_seed_hex'])
        for unit in record['units'][:2]:
            r, counter = scalar_draw(seed, curve['N'], counter)
            if multiply(curve, tuple(job['published_G']), r) != tuple(unit['generator']):
                raise ValueError('Independent bank generator draw differs')
            totals['scalar_checks'] += 1
    return totals


def verify(output, workers=3):
    output = Path(output); design = check_source(output); config = design['config']
    if not (output/'receipt.json').exists(): raise ValueError('Incomplete data')
    queue = jobs(json.loads((output/'inputs.json').read_text()), json.loads((output/'targets.json').read_text()), config)
    if {p.name for p in (output/'records').glob('*.json')} != {j['id']+'.json' for j in queue}:
        raise ValueError('Missing/extra records')
    design_sha = hashlib.sha256(canonical(design)).hexdigest(); totals = {}; completed = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(verify_job, j, str(output), config, design_sha) for j in queue]
        for future in concurrent.futures.as_completed(futures):
            result = future.result(); completed += 1
            for k, v in result.items(): totals[k] = totals.get(k, 0)+v
            if completed % 512 == 0: print(json.dumps({'stage': 'verification', 'completed': completed, 'total': len(queue)}), flush=True)
    receipt = json.loads((output/'receipt.json').read_text())
    if receipt['points'] != totals['points'] or receipt['raw_bytes'] != totals['raw_bytes']:
        raise ValueError('Receipt totals differ')
    result = {'schema': 1, 'status': 'passed', 'records': len(queue), 'counts': totals, 'all_raw_sha256_verified': True,
              'same_session': True, 'feature_check': 'Full raw replay with the same locked feature code; separate synthetic tests check formulas',
              'arithmetic_check': 'Separate Python integer affine oracle; not an independent research review',
              'scope': 'Integrity and exact universal identities only; no security or performance claim'}
    immutable(output/'verification.json', canonical(result)); print(json.dumps(result), flush=True)
