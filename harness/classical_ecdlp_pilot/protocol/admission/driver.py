#!/usr/bin/env python3
"""Hash-bound batch adapter for the repository's admitted trial supervisor.

No approval is conferred here. run/check require the real supervisor's launch
record and parent PID. Five C++ modules compile and self-test sequentially, then
their finite observational commands run with at most three module workers.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import gzip
import hashlib
import json
import math
from pathlib import Path
import os
import re
import subprocess
import sys
import time

CHUNK_LIMIT = 60 * 1024
PART_COUNT = 64
MODULES = ('circuit', 'padic_endo', 'sequences', 'algebraic', 'lossy')
TRACKS = {'D', *('L'+str(i) for i in range(1, 10))}


def sha(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def read_json(path: Path):
    return json.loads(path.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON '+x)))


def write_once(path: Path, obj) -> None:
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')


def safe(root: Path, value: str) -> Path:
    p = Path(value)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == value, 'unsafe repository path '+value)
    current = root
    for part in p.parts:
        current /= part
        require(not current.is_symlink(), 'symlink source '+value)
    return current


def finite(value) -> None:
    if isinstance(value, float):
        require(math.isfinite(value), 'nonfinite numerical output')
    elif isinstance(value, dict):
        for item in value.values():
            finite(item)
    elif isinstance(value, list):
        for item in value:
            finite(item)


def context(config_path: Path, directory: Path, command: str):
    root = Path.cwd().resolve()
    config_path = config_path.resolve()
    require(config_path.is_relative_to(root), 'config outside admitted repository')
    config = read_json(config_path)
    require(config.get('schema') == 'classical.ecdlp.batch-config.v1', 'config schema')
    require(config.get('maximum_module_workers') == 3, 'worker contract changed')
    require([x['name'] for x in config.get('modules', [])] == list(MODULES), 'module set/order mismatch')
    expected = root / 'experiments' / config['experiment_id'] / 'runs' / config['run_id']
    require(directory.resolve() == expected.resolve(), 'run directory does not match frozen identity')
    launch = read_json(directory / 'launch.json')
    environment = read_json(directory / 'environment.json')
    require(os.getppid() == launch.get('supervisor_pid'), 'driver/checker must be child of admitted supervisor')
    require(launch.get('run_id') == config['run_id'], 'launch identity mismatch')
    argv = launch.get('argv' if command == 'run' else 'check_argv')
    require(isinstance(argv, list) and argv[1:] == sys.argv, 'argv does not match supervisor launch record')
    bound = environment.get('source_sha256')
    require(isinstance(bound, dict), 'supervisor source bindings missing')
    relative = config_path.relative_to(root).as_posix()
    require(bound.get(relative) == sha(config_path), 'config digest not bound by supervisor')
    for relative, digest in config['source_sha256'].items():
        require(bound.get(relative) == digest and sha(safe(root, relative)) == digest, 'changed/unbound source '+relative)
    for relative, digest in config['input_sha256'].items():
        require(sha(safe(root, relative)) == digest, 'changed input '+relative)
    return root, config, launch


def call(argv: list[str], cwd: Path, out: Path, err: Path, timeout: int) -> dict:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    clock = time.monotonic()
    with out.open('xb') as stdout, err.open('xb') as stderr:
        try:
            p = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, timeout=timeout)
            code, state = p.returncode, 'exited'
        except subprocess.TimeoutExpired:
            code, state = None, 'watchdog_expired'
    return {'argv': argv, 'started_utc': started, 'finished_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
            'wall_seconds': time.monotonic()-clock, 'returncode': code, 'process_state': state,
            'stdout_sha256': sha(out), 'stderr_sha256': sha(err)}


def module_artifacts(name: str) -> list[str]:
    return [name+'-'+stage+'.'+stream+'.txt' for stage in ('build', 'self-test', 'run') for stream in ('stdout', 'stderr')] + [name+'-rescue.jsonl.gz']


def rescue(path: Path, target: Path) -> None:
    if path.exists():
        raw = path.read_bytes()
        target.write_bytes(gzip.compress(raw, mtime=0))
        require(gzip.decompress(target.read_bytes()) == raw, 'rescue gzip failed reconstruction')
        path.unlink()
    elif not target.exists():
        target.touch()


def partition(directory: Path, module: dict, next_slot: int, fixture_ids: set[str]):
    name = module['name']
    source = directory / ('.'+name+'.full.jsonl')
    require(source.is_file(), 'module produced no JSONL '+name)
    original_hash, original_bytes = sha(source), source.stat().st_size
    rows, actual_tracks, parts, buffer = 0, set(), [], bytearray()

    def flush():
        nonlocal next_slot, buffer
        if not buffer:
            return
        require(next_slot < PART_COUNT, 'output exceeds the declared part-slot capacity; full source retained in rescue')
        p = directory / f'rows-part-{next_slot:03}.jsonl'
        with p.open('xb') as stream:
            stream.write(buffer)
        parts.append({'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size})
        next_slot += 1
        buffer = bytearray()

    with source.open('rb') as stream:
        for line in stream:
            require(len(line) <= CHUNK_LIMIT, 'individual JSONL row exceeds part capacity; full source retained in rescue')
            require(line.strip() != b'', 'blank JSONL record '+name)
            obj = json.loads(line, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON '+x)))
            require(isinstance(obj, dict), 'JSONL row must be object')
            finite(obj)
            require(obj.get('track') in module['tracks'], 'unexpected/missing track in '+name)
            require(obj.get('scope') == 'exploratory_toy_diagnostic', 'output scope mismatch '+name)
            require(obj.get('attack_claimed') in (None, False), 'attack claim forbidden in observation-only pilot')
            fixture = obj.get('fixture_id', obj.get('fixture'))
            if fixture is not None:
                require(fixture in fixture_ids or (fixture in module.get('global_fixture_aliases', []) and obj['track'] == 'L4'), 'unknown fixture in '+name)
            actual_tracks.add(obj['track'])
            rows += 1
            if len(buffer)+len(line) > CHUNK_LIMIT:
                flush()
            buffer.extend(line)
    flush()
    require(rows > 0 and actual_tracks == set(module['tracks']), 'missing track output in '+name)
    reconstructed = b''.join((directory/x['path']).read_bytes() for x in parts)
    require(len(reconstructed) == original_bytes and hashlib.sha256(reconstructed).hexdigest() == original_hash, 'partition reconstruction failed')
    source.unlink()
    return {'name': name, 'original_sha256': original_hash, 'original_bytes': original_bytes,
            'row_count': rows, 'tracks': sorted(actual_tracks), 'parts': parts}, next_slot


def execute(root: Path, config: dict, launch: dict, directory: Path) -> int:
    require(not (directory/'raw-result.json').exists(), 'outputs already exist')
    compiler = subprocess.check_output(['g++', '--version'], text=True).splitlines()[0]
    jobs = []
    for module in config['modules']:
        name = module['name']
        require(re.fullmatch('[a-z_]+', name) is not None, 'unsafe module name')
        binary = directory / ('.'+name+'.bin')
        build = call(['g++', *config['compiler_flags'], module['source'], '-o', str(binary)], root,
                     directory/(name+'-build.stdout.txt'), directory/(name+'-build.stderr.txt'), config['watchdog_seconds'])
        entry = {'name': name, 'tracks': module['tracks'], 'build': build}
        if build['returncode'] == 0:
            entry['binary_sha256'] = sha(binary)
            entry['self_test'] = call([str(binary), '--self-test'], root,
                  directory/(name+'-self-test.stdout.txt'), directory/(name+'-self-test.stderr.txt'), config['watchdog_seconds'])
        jobs.append(entry)
    eligible = [j for j in jobs if j['build']['returncode'] == 0 and j.get('self_test', {}).get('returncode') == 0]
    if len(eligible) == len(MODULES):
        def run_module(entry):
            name = entry['name']
            return name, call([str(directory/('.'+name+'.bin')), '--run', config['fixtures'], str(directory/('.'+name+'.full.jsonl'))], root,
                    directory/(name+'-run.stdout.txt'), directory/(name+'-run.stderr.txt'), config['watchdog_seconds'])
        with ThreadPoolExecutor(max_workers=config['maximum_module_workers']) as pool:
            for future in as_completed([pool.submit(run_module, j) for j in jobs]):
                name, result = future.result()
                next(j for j in jobs if j['name'] == name)['measurement'] = result
    errors, module_parts, slot = [], [], 0
    for module, job in zip(config['modules'], jobs):
        name = module['name']
        try:
            require(job.get('measurement', {}).get('returncode') == 0, 'build/self-test/measurement did not complete '+name)
            parts, slot = partition(directory, module, slot, set(config['fixture_ids']))
            module_parts.append(parts)
        except (OSError, ValueError, TypeError) as error:
            errors.append({'module': name, 'reason': str(error)})
        finally:
            rescue(directory/('.'+name+'.full.jsonl'), directory/(name+'-rescue.jsonl.gz'))
            (directory/('.'+name+'.bin')).unlink(missing_ok=True)
            for artifact in module_artifacts(name):
                p = directory/artifact
                if not p.exists():
                    p.touch()
    slots = []
    for i in range(PART_COUNT):
        p = directory/f'rows-part-{i:03}.jsonl'
        if not p.exists():
            p.touch()
        slots.append({'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size})
    parts_manifest = {'schema': 'classical.ecdlp.parts.v1', 'part_bytes_limit': CHUNK_LIMIT, 'part_slots': PART_COUNT,
                      'modules': module_parts, 'slots': slots, 'errors': errors}
    write_once(directory/'parts-manifest.json', parts_manifest)
    metrics = {'modules_requested': len(MODULES), 'modules_with_partitioned_output': len(module_parts),
               'rows': sum(x['row_count'] for x in module_parts), 'tracks': len({t for m in module_parts for t in m['tracks']}), 'errors': len(errors)}
    raw = {'schema': 'classical.ecdlp.batch-result.v1', 'scope': 'exploratory_toy_diagnostic', 'attack_claimed': False,
           'experiment_id': config['experiment_id'], 'run_id': config['run_id'], 'source_commit': launch['authority']['commit'],
           'compiler': compiler, 'module_execution': jobs, 'metrics': metrics, 'errors': errors,
           'parts_manifest_sha256': sha(directory/'parts-manifest.json'), 'scientific_conclusion': None}
    write_once(directory/'raw-result.json', raw)
    # JSON is valid YAML. Only missing factual envelope fields are completed by
    # the genuine repository supervisor; this adapter supplies no authority.
    write_once(directory/'manifest.yaml', {'run': {'attack_claimed': False, 'metrics': metrics,
                'result': {'metrics': metrics, 'raw_result': 'raw-result.json', 'claim_tier': 'toy',
                           'note': 'Observations only; no scientific interpretation or algorithmic advantage.'}}})
    return 0 if not errors else 2


def check(config: dict, directory: Path) -> None:
    raw, parts = read_json(directory/'raw-result.json'), read_json(directory/'parts-manifest.json')
    require(raw.get('schema') == 'classical.ecdlp.batch-result.v1' and raw.get('attack_claimed') is False, 'raw schema/claim')
    require(raw.get('experiment_id') == config['experiment_id'] and raw.get('run_id') == config['run_id'], 'raw identity')
    require(raw.get('errors') == [] and parts.get('errors') == [], 'recorded module failure')
    require(raw.get('parts_manifest_sha256') == sha(directory/'parts-manifest.json'), 'parts binding')
    require(len(parts.get('slots', [])) == PART_COUNT, 'part slot coverage')
    for item in parts['slots']:
        p = directory/item['path']
        require(sha(p) == item['sha256'] and p.stat().st_size == item['bytes'] <= CHUNK_LIMIT, 'part size/hash')
    tracks, row_count = set(), 0
    require([x['name'] for x in parts['modules']] == list(MODULES), 'module part coverage')
    for module, result in zip(config['modules'], parts['modules']):
        data = b''.join((directory/x['path']).read_bytes() for x in result['parts'])
        require(len(data) == result['original_bytes'] and hashlib.sha256(data).hexdigest() == result['original_sha256'], 'source reconstruction')
        rows = [json.loads(line) for line in data.splitlines()]
        require(len(rows) == result['row_count'] and rows, 'row count')
        present = set()
        for obj in rows:
            finite(obj)
            require(obj.get('scope') == 'exploratory_toy_diagnostic' and obj.get('track') in module['tracks'], 'row schema')
            fixture = obj.get('fixture_id', obj.get('fixture'))
            if fixture is not None:
                require(fixture in set(config['fixture_ids']) or (fixture in module.get('global_fixture_aliases', []) and obj['track'] == 'L4'), 'unknown fixture in checked row')
            require(obj.get('attack_claimed') in (None, False), 'attack claim forbidden')
            present.add(obj['track'])
        require(present == set(module['tracks']), 'track coverage')
        tracks.update(present)
        row_count += len(rows)
    require(tracks == TRACKS and raw['metrics']['rows'] == row_count, 'batch coverage')
    require(all(j.get('measurement', {}).get('returncode') == 0 and j['build']['returncode'] == 0 and j.get('self_test', {}).get('returncode') == 0 for j in raw['module_execution']), 'execution code')
    print(json.dumps({'status': 'output_integrity_pass', 'rows': row_count, 'tracks': sorted(tracks), 'scientific_conclusion': None}))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('run', 'check'))
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    root, config, launch = context(args.config, args.run_dir, args.command)
    if args.command == 'check':
        check(config, args.run_dir)
        return 0
    return execute(root, config, launch, args.run_dir)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, KeyError) as error:
        print('classical-pilot driver refused: '+str(error), file=sys.stderr)
        raise SystemExit(2)
