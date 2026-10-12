#!/usr/bin/env python3
"""Portable fixed-size, agent-free rare/higher-order point study.

Run: python research.py batch --output runs/<new-seed-name> --prior <old-run>
Subcommands allow safe restart of every stage. All coordinates/scalars are public.
"""
import argparse
import concurrent.futures
import fcntl
import gzip
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import numpy as np
from native import Sampler, build, seed_for
from metrics import features, decode, transport, WALK_METRICS, FIELD_METRICS
from identity import generator_identity, model_identity

HERE = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()+b'\n'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''): h.update(block)
    return h.hexdigest()


def immutable(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data: raise ValueError(f'Immutable content differs: {path}')
        return
    temp = path.with_name('.'+path.name+f'.{os.getpid()}.tmp')
    with temp.open('wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    try:
        os.link(temp, path)
    except FileExistsError:
        if path.read_bytes() != data: raise ValueError('Concurrent immutable write mismatch')
    finally: temp.unlink(missing_ok=True)


def validate_config(config):
    for name in ('walk_blocks', 'walk_points', 'field_points', 'bank_generators', 'bank_chunk', 'prefix_points',
                 'prefix_skip', 'targets_per_region', 'target_starts', 'target_points', 'primary_tests'):
        if type(config[name]) is not int or config[name] < 1: raise ValueError('Counts must be positive integers')
    if min(config[k] for k in ('walk_points', 'field_points', 'prefix_points', 'target_points')) < 64:
        raise ValueError('Feature windows require 64 points')
    if config['bank_generators'] % config['bank_chunk']: raise ValueError('Bank chunk must divide generator count')
    if config['walk_metrics'] != WALK_METRICS or config['field_metrics'] != FIELD_METRICS:
        raise ValueError('Feature list differs from the defined contract')
    if config['primary_tests'] != len(config['cases'])*(3*len(WALK_METRICS)+2*len(FIELD_METRICS)+1):
        raise ValueError('Multiplicity contract differs')


def initialize(output, config_path, seed=None):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path(config_path).read_text())
    if seed: config['seed'] = seed
    validate_config(config)
    source_paths = [p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py', '.c', '.json', '.md', '.txt', '.sh')]
    source_paths = [p for p in source_paths if p.name not in ('config.json', 'validation-before-run.json')]
    design = {'schema': 1, 'config': config, 'source_sha256': {p.name: digest(p) for p in source_paths},
              'scope': 'Public point-distribution observations only; no group-rank, ECDLP cost, security, or official scientific-state claim'}
    immutable(output/'design.json', canonical(design))
    for p in source_paths: immutable(output/'source'/p.name, p.read_bytes())
    immutable(output/'source'/'config.json', canonical(config))
    immutable(output/'inputs.json', (HERE/'inputs.json').read_bytes())
    immutable(output/'targets.json', (HERE/'targets.json').read_bytes())
    return output, config, hashlib.sha256(canonical(design)).hexdigest()


def check_source(output):
    output = Path(output); design = json.loads((output/'design.json').read_text())
    for name, expected in design['source_sha256'].items():
        if digest(HERE/name) != expected: raise ValueError('Use this batch\'s frozen source/ copy; live source differs')
    for name in ('inputs.json', 'targets.json'):
        if digest(output/name) != design['source_sha256'][name]: raise ValueError('Frozen input differs')
    return design


def jobs(inputs, targets, config):
    queue = []
    for anchor in inputs['anchors']:
        case = anchor['case']; curve = {k: anchor[k] for k in ('p', 'A', 'B', 'N')}
        shared = {'case': case, 'curve': curve, 'published_G': anchor['G'], 'anchor_identity': anchor['identity']}
        for block in range(config['walk_blocks']):
            queue.append(shared | {'id': f'{case}-walk-{block:06d}', 'kind': 'walk', 'block': block,
                                   'points': 2*config['walk_points']})
        for chunk in range(config['bank_generators']//config['bank_chunk']):
            queue.append(shared | {'id': f'{case}-bank-{chunk:06d}', 'kind': 'bank', 'block': chunk,
                                   'points': config['bank_chunk']*config['prefix_points']})
        queue.append(shared | {'id': f'{case}-published-prefix', 'kind': 'prefix', 'block': 0,
                               'points': config['prefix_points']})
        for target in targets['targets']:
            if target['case'] != case: continue
            queue.append(shared | {'id': f"{case}-target-{target['region']}-{target['index']:04d}", 'kind': 'target',
                                   'target': target, 'block': target['index'],
                                   'points': config['prefix_points']+2*config['target_starts']*config['target_points']})
    for field in inputs['fields']:
        for curve in field['curves']:
            queue.append({'id': f"{field['id']}-model-{curve['index']:03d}", 'kind': 'field',
                          'case': field['case'], 'curve': curve, 'arm': field['arm'], 'field_id': field['id'],
                          'block': curve['index'], 'points': config['field_points']})
    return sorted(queue, key=lambda job: seed_for(config['seed'], 'job-order', job['id']))


def one_job(job, config, output, library, design_sha):
    start = time.perf_counter(); cpu = time.process_time()
    sampler = Sampler(library); curve = job['curve']; p = curve['p']; seed_root = config['seed']
    width = (p.bit_length()+7)//8; chunks = []; units = []; diagnostics = {}

    def draw_g(domain):
        seed = seed_for(seed_root, job['id'], domain)
        raw, used = sampler.sample(curve, job['published_G'], seed, 0, 1)
        return list(decode(raw, p)[0]), seed.hex(), used

    def capture(g, seed, mode, count, label, **metadata):
        raw, used = sampler.sample(curve, g, seed, mode, count+(config['prefix_skip'] if mode == 3 else 0))
        if mode == 3: raw = raw[config['prefix_skip']*2*width:]
        unit = {'label': label, 'generator': g if mode != 2 else None, 'seed_hex': seed.hex(), 'mode': mode,
                'counter_used': used, 'offset_points': sum(len(c)//(2*width) for c in chunks), 'points': count,
                'features': features(raw, p)} | metadata
        chunks.append(raw); units.append(unit)
        return raw, unit

    if job['kind'] == 'walk':
        random_g, gs, used = draw_g('random-generator')
        point_seed = seed_for(seed_root, job['id'], 'common-start')
        for label, g in [('published', job['published_G']), ('random', random_g)]:
            raw, unit = capture(g, point_seed, 1, config['walk_points'], label,
                                generator_seed_hex=gs if label == 'random' else None,
                                generator_identity=job['anchor_identity'] if label == 'published' else generator_identity(curve, g))
            if job['block'] < config['diagnostic_blocks']:
                array = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 2*width)
                rng = np.random.default_rng(int.from_bytes(seed_for(seed_root, job['id'], label, 'shuffle')[:8], 'big'))
                shuffled = array[rng.permutation(len(array))].tobytes()
                # Lexicographic integer-byte sort is exact; deliberately structured positive control.
                ordered = sorted(decode(raw, p))
                from metrics import encode
                diagnostics[label] = {'shuffled': features(shuffled, p), 'sorted': features(encode(ordered, p), p),
                                      'isomorphic_u2': features(transport(raw, p), p)}
    elif job['kind'] == 'bank':
        seed = seed_for(seed_root, job['id'], 'generator-bank')
        graw, generator_counter = sampler.sample(curve, job['published_G'], seed, 0, config['bank_chunk'])
        diagnostics['generator_bank_seed_hex'] = seed.hex()
        diagnostics['generator_bank_counter_used'] = generator_counter
        for index, g in enumerate(decode(graw, p)):
            global_index = job['block']*config['bank_chunk']+index
            raw, unit = capture(list(g), seed_for(seed_root, job['id'], index, 'prefix'), 3, config['prefix_points'],
                                'bank', generator_index=global_index)
            if global_index < config['transport_bank_generators']:
                unit['isomorphic_u2'] = features(transport(raw, p), p)
    elif job['kind'] == 'prefix':
        raw, unit = capture(job['published_G'], seed_for(seed_root, job['id'], 'prefix'), 3,
                            config['prefix_points'], 'published-prefix')
        unit['isomorphic_u2'] = features(transport(raw, p), p)
    elif job['kind'] == 'target':
        g = job['target']['G']
        raw, unit = capture(g, seed_for(seed_root, job['id'], 'target-prefix'), 3, config['prefix_points'], 'target-prefix')
        unit['isomorphic_u2'] = features(transport(raw, p), p)
        for start_index in range(config['target_starts']):
            rg, gs, used = draw_g(f'control-generator-{start_index}')
            seed = seed_for(seed_root, job['id'], start_index, 'common-start')
            for label, h in [('target', g), ('random', rg)]:
                capture(h, seed, 1, config['target_points'], label, start_index=start_index,
                        generator_seed_hex=gs if label == 'random' else None)
    elif job['kind'] == 'field':
        capture([0, 0], seed_for(seed_root, job['id'], 'affine-points'), 2, config['field_points'], 'uniform-affine')
    else: raise ValueError('Unknown job kind')
    raw = b''.join(chunks)
    if len(raw) != job['points']*2*width: raise ValueError('Produced point count differs')
    path = Path(output)/'points'/(job['id']+'.raw'); immutable(path, raw)
    record = {'schema': 1, 'design_sha256': design_sha, 'job': job, 'model_uid': model_identity(curve),
              'units': units, 'diagnostics': diagnostics, 'raw': {'path': str(path.relative_to(output)),
              'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'encoding': f'big-endian x,y, {width} bytes each'},
              'cpu_seconds': time.process_time()-cpu, 'elapsed_seconds': time.perf_counter()-start}
    immutable(Path(output)/'records'/(job['id']+'.json'), canonical(record))
    return {'id': job['id'], 'points': job['points']}


def old_records(prior):
    prior = Path(prior)
    for path in sorted((prior/'record-shards').glob('*.jsonl.gz')):
        with gzip.open(path, 'rt') as stream:
            for line in stream: yield json.loads(line)


def discover_job(record, prior, output, design_sha, walk_points):
    start = time.perf_counter()
    path = Path(prior)/record['raw']['path']; raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['raw']['sha256']: raise ValueError('Prior raw checksum differs')
    result = {'id': record['job']['id'], 'job': {k: record['job'].get(k) for k in ('case', 'mode', 'cohort', 'arm', 'block', 'field_id')},
              'prior_record_sha256': hashlib.sha256(canonical(record)).hexdigest(), 'raw_sha256': record['raw']['sha256'],
              'points': record['job']['points'], 'features': features(raw, record['job']['curve']['p']), 'design_sha256': design_sha}
    if record['job']['mode'] == 'walk':
        if record['job']['points'] < walk_points: raise ValueError('Prior training walks shorter than confirmation walks')
        width = (record['job']['curve']['p'].bit_length()+7)//8
        result['ml_points'] = walk_points
        result['ml_features'] = features(raw[:walk_points*2*width], record['job']['curve']['p'])
    immutable(Path(output)/'discovery'/'records'/(result['id']+'.json'), canonical(result))
    return time.perf_counter()-start


def discover(output, prior, workers):
    design = check_source(output); design_sha = hashlib.sha256(canonical(design)).hexdigest()
    prior = Path(prior).resolve()
    if not prior.is_dir(): raise ValueError('Prior data directory required for discovery/training')
    files = [prior/n for n in ('receipt.json', 'verification.json', 'design.json', 'record-shards.json')]
    files += sorted((prior/'record-shards').glob('*.jsonl.gz'))
    if len(files) <= 4: raise ValueError('Prior lossless record shards missing')
    provenance = {'schema': 1, 'prior_run_name': prior.name, 'source_files_sha256': {str(p.relative_to(prior)): digest(p) for p in files},
                  'design_sha256': design_sha, 'status': 'exploratory; primary confirmation uses fresh data'}
    immutable(Path(output)/'discovery'/'provenance.json', canonical(provenance))
    queue = list(old_records(prior)); pending = []
    for record in queue:
        path = Path(output)/'discovery'/'records'/(record['job']['id']+'.json')
        if path.exists():
            saved = json.loads(path.read_text())
            if saved['design_sha256'] != design_sha or saved['prior_record_sha256'] != hashlib.sha256(canonical(record)).hexdigest():
                raise ValueError('Discovery resume mismatch')
        else: pending.append(record)
    start = time.time(); completed = len(queue)-len(pending)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(discover_job, r, str(prior), str(output), design_sha, design['config']['walk_points']) for r in pending]
        for future in concurrent.futures.as_completed(futures):
            future.result(); completed += 1
            if completed % 512 == 0: print(json.dumps({'stage': 'discovery', 'completed': completed, 'total': len(queue)}), flush=True)
    receipt = {'schema': 1, 'records': len(queue), 'points': sum(r['job']['points'] for r in queue),
               'final_invocation_seconds': time.time()-start, 'seed_status': 'previous-run public points; not new independent confirmation'}
    path = Path(output)/'discovery'/'receipt.json'
    if not path.exists(): immutable(path, canonical(receipt))
    print(json.dumps({'stage': 'discovery-complete', 'records': len(queue)}), flush=True)


def reuse_discovery(output, source):
    """Reuse the frozen old-data features; no download/re-scan of old raw needed."""
    source = Path(source); source = source/'discovery' if (source/'discovery').is_dir() else source
    design = check_source(output); design_sha = hashlib.sha256(canonical(design)).hexdigest()
    if (source/'records').is_dir():
        rows = [json.loads(p.read_text()) for p in sorted((source/'records').glob('*.json'))]
    else:
        rows = []
        for path in sorted((source/'record-shards').glob('*.jsonl.gz')):
            with gzip.open(path, 'rt') as stream: rows.extend(json.loads(line) for line in stream)
    if not rows: raise ValueError('Prior discovery feature records missing')
    receipt = json.loads((source/'receipt.json').read_text())
    if receipt['records'] != len(rows): raise ValueError('Prior discovery count mismatch')
    for row in rows:
        if row['job']['mode'] == 'walk' and row.get('ml_points') != design['config']['walk_points']:
            raise ValueError('Reused training window length differs; scan original raw for this configuration')
    identity = hashlib.sha256(b''.join(canonical(r) for r in rows)).hexdigest()
    immutable(Path(output)/'discovery'/'provenance.json', canonical({'schema': 1, 'reuse_of_frozen_discovery': identity,
              'prior_receipt_sha256': digest(source/'receipt.json'), 'design_sha256': design_sha,
              'status': 'Reused old-data features only; confirmation generated with the new run seed'}))
    for row in rows:
        derived = row | {'design_sha256': design_sha, 'reused_from_sha256': hashlib.sha256(canonical(row)).hexdigest()}
        immutable(Path(output)/'discovery'/'records'/(row['id']+'.json'), canonical(derived))
    immutable(Path(output)/'discovery'/'receipt.json', canonical({'schema': 1, 'records': len(rows),
              'points': sum(r['points'] for r in rows), 'reuse_sha256': identity, 'seed_status': 'Old features reused, not independent new samples'}))
    print(json.dumps({'stage': 'discovery-reused', 'records': len(rows)}), flush=True)


def run(output, workers):
    design = check_source(output); config = design['config']; design_sha = hashlib.sha256(canonical(design)).hexdigest()
    output = Path(output); inputs = json.loads((output/'inputs.json').read_text()); targets = json.loads((output/'targets.json').read_text())
    queue = jobs(inputs, targets, config); pending = []
    for job in queue:
        path = output/'records'/(job['id']+'.json')
        if path.exists():
            record = json.loads(path.read_text())
            if record['job'] != job or record['design_sha256'] != design_sha: raise ValueError('Run resume mismatch')
            if digest(output/record['raw']['path']) != record['raw']['sha256']: raise ValueError('Run resume checksum mismatch')
        else: pending.append(job)
    if not pending:
        if (output/'receipt.json').exists():
            print(json.dumps({'stage': 'already-complete', 'jobs': len(queue)}), flush=True); return
    if (output/'receipt.json').exists(): raise ValueError('Completed receipt with missing records')
    library = build(output/'build'/'sampler.so')
    if not (output/'environment.json').exists():
        try:
            commit = subprocess.check_output(['git', '-C', str(HERE), 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
            dirty = subprocess.check_output(['git', '-C', str(HERE), 'status', '--porcelain'], text=True, stderr=subprocess.DEVNULL).splitlines()
        except (FileNotFoundError, subprocess.CalledProcessError): commit = None; dirty = None
        immutable(output/'environment.json', canonical({'python': sys.version, 'platform': platform.platform(), 'numpy': np.__version__,
                    'openssl': subprocess.check_output(['openssl', 'version'], text=True).strip(), 'workers': workers, 'command': sys.argv,
                    'git_commit': commit, 'git_dirty_tree': dirty, 'recorded_at': time.time(), 'agent_required': False}))
    start = time.time(); completed = len(queue)-len(pending)
    print(json.dumps({'stage': 'running', 'jobs': len(queue), 'points': sum(j['points'] for j in queue), 'pending': len(pending)}), flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(one_job, j, config, str(output), str(library), design_sha) for j in pending]
        for future in concurrent.futures.as_completed(futures):
            result = future.result(); completed += 1
            if completed % 128 == 0 or completed == len(queue):
                progress = {'stage': 'sampling', 'completed': completed, 'total': len(queue), 'elapsed_seconds': time.time()-start, 'last_job': result['id']}
                tmp = output/'progress.tmp'; tmp.write_bytes(canonical(progress)); os.replace(tmp, output/'progress.json')
                print(json.dumps(progress), flush=True)
    records = [json.loads((output/'records'/(j['id']+'.json')).read_text()) for j in queue]
    receipt = {'schema': 1, 'status': 'measured_complete', 'design_sha256': design_sha, 'jobs': len(queue),
               'points': sum(j['points'] for j in queue), 'raw_bytes': sum(r['raw']['bytes'] for r in records),
               'summed_job_cpu_seconds': sum(r['cpu_seconds'] for r in records), 'final_invocation_wall_seconds': time.time()-start,
               'failures': 0, 'completed_at': time.time(), 'scope': 'Public point statistics; observations only'}
    immutable(output/'receipt.json', canonical(receipt)); print(json.dumps(receipt), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'discover', 'run', 'verify', 'analyze', 'batch'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=HERE/'config.json')
    parser.add_argument('--seed', help='Use a new independent seed AND a new output directory')
    parser.add_argument('--prior', type=Path, help='Previous immutable generator-cohort run, including raw points')
    parser.add_argument('--reuse-discovery', type=Path, help='Reuse archived old-data features from a completed higher-order run (same walk window length)')
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    if args.workers < 1: parser.error('workers must be positive')
    if args.command == 'plan':
        config = json.loads(args.config.read_text()); validate_config(config)
        queue = jobs(json.loads((HERE/'inputs.json').read_text()), json.loads((HERE/'targets.json').read_text()), config)
        print(json.dumps({'jobs': len(queue), 'points': sum(j['points'] for j in queue),
                          'raw_bytes': sum(j['points']*2*((j['curve']['p'].bit_length()+7)//8) for j in queue), 'config': config}, indent=2)); return
    output, config, sha = initialize(args.output, args.config, args.seed)
    with (output/'runner.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command in ('discover', 'batch'):
            if args.reuse_discovery: reuse_discovery(output, args.reuse_discovery)
            else: discover(output, args.prior, args.workers)
        if args.command in ('run', 'batch'): run(output, args.workers)
        if args.command in ('verify', 'batch'):
            from verify import verify
            verify(output, args.workers)
        if args.command in ('analyze', 'batch'):
            from analyze import analyze
            analyze(output)


if __name__ == '__main__': main()
