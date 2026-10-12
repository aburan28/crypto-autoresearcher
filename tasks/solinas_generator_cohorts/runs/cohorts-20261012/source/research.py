#!/usr/bin/env python3
"""Portable fixed-batch research runner, restartable without an agent or GitHub."""
import argparse
import concurrent.futures
import fcntl
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
from metrics import correlation, features
from native import Sampler, build, seed_for
from identity import generator_identity, model_identity

HERE = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':')).encode() + b'\n'


def check_source(output):
    design = json.loads((Path(output)/'design.json').read_text())
    for name, expected in design['source_sha256'].items():
        if not (HERE/name).exists() or digest(HERE/name) != expected:
            raise ValueError('Source differs from frozen design; use this batch\'s source/ copy')
    if digest(Path(output)/'inputs.json') != design['inputs_sha256']:
        raise ValueError('Frozen input checksum differs')
    return design


def immutable(path, data):
    """Atomically publish new bytes. Accept a replay only if bytes are identical."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f'Immutable file differs: {path}')
        return
    temp = path.with_name('.' + path.name + f'.{os.getpid()}.tmp')
    with temp.open('wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    try:
        os.link(temp, path)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ValueError(f'Concurrent immutable file differs: {path}')
    finally:
        temp.unlink(missing_ok=True)


def jobs(inputs, config):
    queue = []
    for anchor in inputs['anchors']:
        case = anchor['case']
        curve = {k: anchor[k] for k in ('p', 'A', 'B', 'N')}
        for mode, blocks, count in [('walk', config['walk_blocks'], config['walk_points']),
                                     ('iid', config['iid_blocks'], config['iid_points'])]:
            for block in range(blocks):
                for cohort in ('published', 'random'):
                    queue.append({'id': f'{case}-{mode}-{block:06d}-{cohort}', 'case': case,
                                  'mode': mode, 'cohort': cohort, 'block': block, 'curve': curve,
                                  'published_G': anchor['G'], 'anchor_identity': anchor['identity'],
                                  'points': count, 'field_id': f'{case}-standard', 'arm': 'standard'})
    for field in inputs['fields']:
        for curve in field['curves']:
            queue.append({'id': f"{field['id']}-model-{curve['index']:03d}", 'case': field['case'],
                          'mode': 'field', 'cohort': 'uniform-affine', 'arm': field['arm'],
                          'field_id': field['id'], 'block': curve['index'], 'curve': curve,
                          'points': config['field_points']})
    # Fixed seed-derived order prevents cohort/run-time confounding.
    return sorted(queue, key=lambda job: seed_for(config['seed'], 'queue', job['id']))


def one_job(job, config, output, library, design_sha):
    started = time.perf_counter(); cpu_started = time.process_time()
    sampler = Sampler(library)
    mode = {'iid': 0, 'walk': 1, 'field': 2}[job['mode']]
    p = job['curve']['p']
    generator = job.get('published_G', [0, 0])
    generator_seed = None
    if job['cohort'] == 'random':
        generator_seed = seed_for(config['seed'], job['case'], job['mode'], job['block'], 'generator')
        raw_g, _ = sampler.sample(job['curve'], job['published_G'], generator_seed, 0, 1)
        width = (p.bit_length() + 7) // 8
        generator = [int.from_bytes(raw_g[:width], 'big'), int.from_bytes(raw_g[width:], 'big')]
    seed = (seed_for(config['seed'], job['id'], 'points') if mode == 2 else
            seed_for(config['seed'], job['case'], job['mode'], job['block'], 'points'))
    raw, used = sampler.sample(job['curve'], generator, seed, mode, job['points'])
    result, normalized = features(raw, p, config['bins'])
    diagnostics = {}
    if job['mode'] == 'walk' and job['block'] < config['diagnostic_blocks']:
        rng = np.random.default_rng(int.from_bytes(seed_for(config['seed'], job['id'], 'shuffle')[:8], 'big'))
        shuffled = normalized[rng.permutation(len(normalized)), 0]
        ordered = np.sort(normalized[:, 0])
        diagnostics = {'shuffled_x_lag1': correlation(shuffled[:-1], shuffled[1:]),
                       'sorted_positive_x_lag1': correlation(ordered[:-1], ordered[1:])}
        # Same points, explicit isomorphic transport (u=2), diagnostic only.
        width = (p.bit_length()+7)//8
        transported = bytearray()
        for offset in range(0, len(raw), 2*width):
            x=int.from_bytes(raw[offset:offset+width], 'big')
            y=int.from_bytes(raw[offset+width:offset+2*width], 'big')
            transported.extend((4*x % p).to_bytes(width, 'big'))
            transported.extend((8*y % p).to_bytes(width, 'big'))
        diagnostics['isomorphic_u2_features'] = features(bytes(transported), p, config['bins'])[0]
        diagnostics['isomorphic_u2_curve'] = {'p': p, 'A': 16*job['curve']['A'] % p,
                                             'B': 64*job['curve']['B'] % p, 'N': job['curve']['N']}
        diagnostics['isomorphic_u2_generator'] = [4*generator[0] % p, 8*generator[1] % p]
    raw_path = Path(output) / 'points' / (job['id'] + '.raw')
    immutable(raw_path, raw)
    record = {'schema': 1, 'design_sha256': design_sha, 'job': job, 'generator': generator if mode != 2 else None,
              'model_uid': model_identity(job['curve']),
              'generator_identity': (job.get('anchor_identity') if job['cohort'] == 'published' else
                                     generator_identity(job['curve'], generator) if mode != 2 else None),
              'generator_seed_hex': generator_seed.hex() if generator_seed else None,
              'point_seed_hex': seed.hex(), 'counter_consumed': used, 'features': result,
              'diagnostics': diagnostics, 'raw': {'path': str(raw_path.relative_to(output)),
              'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
              'encoding': f'fixed-width big-endian x,y, {((p.bit_length()+7)//8)} bytes each; no infinity'},
              'elapsed_seconds': time.perf_counter()-started, 'cpu_seconds': time.process_time()-cpu_started}
    immutable(Path(output) / 'records' / (job['id'] + '.json'), canonical(record))
    return {'id': job['id'], 'seconds': record['elapsed_seconds'], 'points': job['points']}


def initialize(output, config_path, seed, inputs_path):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path(config_path).read_text())
    if seed is not None:
        config['seed'] = seed
    if any(type(config[k]) is not int or config[k] < 1 for k in
           ('walk_blocks', 'walk_points', 'iid_blocks', 'iid_points', 'field_points', 'bins')):
        raise ValueError('Sample counts and bins must be positive integers')
    if config['walk_points'] < 3 or config['iid_points'] < 3 or config['field_points'] < 3:
        raise ValueError('At least three points per unit required')
    sources = {p.name: digest(p) for p in HERE.glob('*') if p.is_file() and p.suffix in ('.py', '.c')}
    design = {'schema': 1, 'config': config, 'inputs_sha256': digest(inputs_path),
              'source_sha256': sources, 'scope': 'Descriptive public point distributions, not a cryptanalytic cost or security claim'}
    immutable(output/'design.json', canonical(design))
    immutable(output/'inputs.json', Path(inputs_path).read_bytes())
    for name in sources:
        immutable(output/'source'/name, (HERE/name).read_bytes())
    for name in ('requirements.txt', 'bootstrap.sh', 'run_batch.sh', 'README.md', 'PROTOCOL.md'):
        immutable(output/'source'/name, (HERE/name).read_bytes())
    immutable(output/'source'/'config.json', canonical(config))
    immutable(output/'source'/'inputs.json', Path(inputs_path).read_bytes())
    return output, config, hashlib.sha256(canonical(design)).hexdigest()


def run(output, config_path, seed, workers, inputs_path):
    output, config, design_sha = initialize(output, config_path, seed, inputs_path)
    with (output/'runner.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        inputs = json.loads((output/'inputs.json').read_text())
        queue = jobs(inputs, config)
        pending = []
        for job in queue:
            record_path = output/'records'/(job['id']+'.json')
            if record_path.exists():
                record = json.loads(record_path.read_text())
                if record['design_sha256'] != design_sha or record['job'] != job:
                    raise ValueError('Resume design or job mismatch')
                if digest(output/record['raw']['path']) != record['raw']['sha256']:
                    raise ValueError('Existing raw checksum mismatch; refusing replay')
            else:
                pending.append(job)
        if not pending:
            print(json.dumps({'status': 'already_complete', 'jobs': len(queue)})); return
        if (output/'receipt.json').exists():
            raise ValueError('Completed receipt exists but jobs are missing')
        library = build(output/'build'/'sampler.so')
        environment_path = output/'environment.json'
        if not environment_path.exists():
            try:
                git_commit = subprocess.check_output(['git', '-C', str(HERE), 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
                git_dirty = subprocess.check_output(['git', '-C', str(HERE), 'status', '--porcelain'], text=True, stderr=subprocess.DEVNULL).splitlines()
            except (FileNotFoundError, subprocess.CalledProcessError):
                git_commit = None; git_dirty = None
            environment = {'python': sys.version, 'platform': platform.platform(), 'numpy': np.__version__,
                           'compiler': subprocess.check_output(['cc', '--version'], text=True).splitlines()[0],
                           'openssl': subprocess.check_output(['openssl', 'version'], text=True).strip(),
                           'command': sys.argv, 'workers': workers, 'recorded_at': time.time(),
                           'git_commit': git_commit, 'git_dirty_tree': git_dirty,
                           'inference': {'runtime': 'codex', 'model_id': None, 'probe_status': 'not_probed',
                                         'notes': 'Runner uses no model or network; model metadata not inferred'}}
            immutable(environment_path, canonical(environment))
        start = time.time(); completed = len(queue)-len(pending)
        print(json.dumps({'status': 'running', 'jobs': len(queue), 'pending': len(pending),
                          'points': sum(j['points'] for j in queue), 'design_sha256': design_sha}), flush=True)
        # Executor.map maintains bounded process concurrency. Three workers fit
        # the measured machine; other hosts can explicitly choose their count.
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(one_job, job, config, str(output), str(library), design_sha): job['id'] for job in pending}
            for future in concurrent.futures.as_completed(futures):
                result = future.result(); completed += 1
                if completed % 128 == 0 or completed == len(queue):
                    progress = {'completed': completed, 'total': len(queue), 'elapsed_seconds': time.time()-start,
                                'last_job': result['id']}
                    temp = output/'progress.tmp'
                    temp.write_bytes(canonical(progress)); os.replace(temp, output/'progress.json')
                    print(json.dumps(progress), flush=True)
        records = [json.loads((output/'records'/(job['id']+'.json')).read_text()) for job in queue]
        receipt = {'status': 'measured_complete', 'design_sha256': design_sha,
                   'jobs': len(queue), 'points': sum(j['points'] for j in queue),
                   'raw_bytes': sum(r['raw']['bytes'] for r in records),
                   'summed_job_cpu_seconds': sum(r['cpu_seconds'] for r in records),
                   'final_invocation_wall_seconds': time.time()-start,
                   'resume_note': 'CPU sums include all immutable records. Wall time is final invocation only; inspect external invocation logs for previous attempts.',
                   'completed_at': time.time(), 'claim_status': 'observations only; no hypothesis promotion'}
        immutable(output/'receipt.json', canonical(receipt))
        print(json.dumps(receipt), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'analyze', 'verify', 'plan'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=HERE/'config.json')
    parser.add_argument('--inputs', type=Path, default=HERE/'inputs.json', help='Prospectively frozen public input pool')
    parser.add_argument('--seed', help='Independent public batch seed; use a new output directory for each seed')
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    if args.command == 'run':
        run(args.output, args.config, args.seed, args.workers, args.inputs)
    elif args.command == 'plan':
        config = json.loads(args.config.read_text())
        queue = jobs(json.loads(args.inputs.read_text()), config)
        print(json.dumps({'jobs': len(queue), 'points': sum(j['points'] for j in queue),
                          'raw_bytes': sum(j['points']*2*((j['curve']['p'].bit_length()+7)//8) for j in queue),
                          'config': config}, indent=2))
    elif args.command == 'verify':
        from verify import verify
        verify(args.output)
    else:
        from analyze import analyze
        analyze(args.output)


if __name__ == '__main__':
    main()
