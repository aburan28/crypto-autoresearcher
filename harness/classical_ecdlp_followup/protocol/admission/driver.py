#!/usr/bin/env python3
"""Hash-bound batch adapter for the repository's admitted trial supervisor.

No approval is conferred here. run/check require the real supervisor's launch
record and parent PID. Five logical jobs compile and self-test sequentially, then
their finite observational commands run with at most three module workers.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import os
import re
import subprocess
import sys
import time

CHUNK_LIMIT = 60 * 1024
PART_COUNT = 256
VERIFICATION_PART_COUNT = 32
MODULES = ('projection_scale_0', 'projection_scale_1', 'projection_scale_2', 'decoder', 'basis_audit')
TRACKS = {'L9-scale', 'L9-decoder', 'L4-audit'}
SCOPE = 'exploratory_toy_followup'


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
    require(config.get('schema') == 'classical.ecdlp.followup-config.v1', 'config schema')
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


def module_name_valid(name: str) -> bool:
    return re.fullmatch('[a-z_][a-z_0-9]*', name) is not None


def module_artifacts(name: str) -> list[str]:
    return [name+'-'+stage+'.'+stream+'.txt' for stage in ('build', 'self-test', 'run') for stream in ('stdout', 'stderr')] + [name+'-rescue.jsonl.gz']


def rescue(path: Path, target: Path) -> None:
    if path.exists():
        raw = path.read_bytes()
        with target.open('xb') as stream:
            stream.write(gzip.compress(raw, mtime=0))
        require(gzip.decompress(target.read_bytes()) == raw, 'rescue gzip failed reconstruction')
        path.unlink()
    elif not target.exists():
        target.touch()


def fixture_name(row: dict) -> str:
    value = row.get('fixture_id', row.get('fixture'))
    require(isinstance(value, str), 'missing fixture identity')
    return value


def validate_rows(module: dict, rows: list[dict], config: dict) -> None:
    """Exact registered coverage, not merely one row per track."""
    fixture_meta = {x['id']: x for x in config['fixture_meta']}
    fixtures = set(module.get('fixture_ids', fixture_meta))
    for row in rows:
        finite(row)
        require(row.get('track') in module['tracks'] and row.get('scope') == SCOPE, 'row scope/track')
        require(row.get('attack_claimed') in (None, False), 'unqualified attack claim')
        f = fixture_name(row)
        require(f in fixtures or (f in module.get('global_fixture_aliases', []) and module['name'] == 'basis_audit'), 'unknown fixture')
        require(row.get('outcome', 'complete_valid') in ('complete_valid', 'complete_control', 'not_applicable'), 'failed/unknown row outcome')

    def unique_add(seen, key):
        require(key not in seen, 'duplicate coverage key '+str(key))
        seen.add(key)

    if module.get('kind',module['name']) == 'projection_scale':
        wanted = {(f, name) for f in fixtures for name in module['features']}
        seen = set()
        for row in rows:
            key = (fixture_name(row), row.get('projection'))
            unique_add(seen, key)
            require(key in wanted, 'unexpected scale projection')
            applicable = key[1] != 'power_residue_5' or fixture_meta[key[0]]['p'] % 5 == 1
            require((row.get('outcome') == 'not_applicable') is (not applicable), 'power-residue applicability mismatch')
        require(seen == wanted, 'incomplete scale fixture/projection coverage')
    elif module['name'] == 'decoder':
        kernels, cases, na = set(), set(), set()
        target_map = {x['target_id']: x['fixture_id'] for x in config['target_meta']}
        wanted_kernels = {(f, feature) for f in fixtures for feature in module['features'] if feature != 'power_residue_5' or fixture_meta[f]['p'] % 5 == 1}
        wanted_na = {(f, 'power_residue_5') for f in fixtures if fixture_meta[f]['p'] % 5 != 1}
        wanted_cases = {(x['fixture_id'], feature, x['target_id'], mode, width) for x in config['target_meta'] for feature in module['features'] for mode in ('model','exact') for width in (1, 8) if (x['fixture_id'], feature) in wanted_kernels}
        for row in rows:
            f, feature, kind = fixture_name(row), row.get('feature'), row.get('row_kind')
            require(feature in module['features'], 'unknown decoder feature')
            if kind == 'not_applicable':
                unique_add(na, (f, feature))
                require(row.get('outcome') == 'not_applicable', 'NA row outcome')
            elif kind == 'kernel':
                unique_add(kernels, (f, feature))
                require(row.get('training_samples') == 2048 and row.get('heldout_samples') == 512, 'kernel sample contract')
                require(row.get('calibration_used_for_tuning') is False, 'held-out calibration used for tuning')
            elif kind == 'target':
                target, mode, width = row.get('target_id'), row.get('prefix_mode'), row.get('beam_width')
                require(target_map.get(target) == f and mode in ('model','exact') and width in (1, 8), 'target/beam identity')
                unique_add(cases, (f, feature, target, mode, width))
                candidates = row.get('candidates')
                require(isinstance(candidates, list) and 0 < len(candidates) <= width, 'candidate list size')
                require(all(type(k) is int and 0 <= k < fixture_meta[f]['r'] for k in candidates) and len(set(candidates)) == len(candidates), 'candidate scalar range/duplicates')
                require(row.get('candidate_count') == len(candidates), 'candidate count mismatch')
                hits, scalar = row.get('candidate_verification_hits'), row.get('verified_scalar')
                require(type(hits) is int and hits in (0, 1), 'candidate hit count')
                require((hits == 0 and scalar is None) or (hits == 1 and type(scalar) is int and scalar in candidates), 'verified scalar consistency')
            else:
                raise ValueError('unknown decoder row kind '+str(kind))
        require(kernels == wanted_kernels and cases == wanted_cases and na == wanted_na, 'incomplete decoder kernel/target/NA coverage')
    elif module['name'] == 'basis_audit':
        summaries, certificates, actual = [], [], {'Q': set(), 'F2': set()}
        wanted = {}
        for field, values in [('Q', range(-2, 3)), ('F2', range(2))]:
            wanted[field] = {m for m in itertools.product(values, repeat=4) if (m[0]*m[3]-m[1]*m[2] != 0 if field == 'Q' else (m[0]*m[3]-m[1]*m[2]) % 2 != 0)}
        for row in rows:
            kind = row.get('row_kind')
            if kind == 'summary':
                summaries.append(row)
            elif kind == 'symbolic_identity_certificate':
                certificates.append(row)
            elif kind == 'per_basis':
                field, matrix = row.get('field'), row.get('matrix')
                require(field in actual and isinstance(matrix, list), 'basis field/matrix')
                if len(matrix) == 2 and all(isinstance(r, list) and len(r) == 2 for r in matrix):
                    matrix = matrix[0]+matrix[1]
                require(len(matrix) == 4 and all(type(x) is int for x in matrix), 'basis integer entries')
                key = tuple(matrix)
                require(key in wanted[field], 'basis outside frozen grammar')
                unique_add(actual[field], key)
            else:
                raise ValueError('unknown basis row kind '+str(kind))
        require(len(summaries) == len(certificates) == 1 and actual == wanted, 'incomplete basis/certificate coverage')
        summary, certificate = summaries[0], certificates[0]
        require(summary.get('rational_matrices_pre_filter') == 625 and summary.get('rational_invertible_matrices') == len(wanted['Q']), 'rational basis count')
        require(summary.get('gf2_invertible_matrices') == 6 and summary.get('independent_gf2_triples') == 216, 'GF2 coverage')
        require(certificate.get('variables') == 20 and certificate.get('residual_monomials') == [] and certificate.get('boolean_exponent_reduction') is False and certificate.get('lhs_monomials') == certificate.get('rhs_monomials') and len(certificate.get('lhs_monomials', [])) == 32, 'symbolic identity certificate contract')
    else:
        raise ValueError('unknown module coverage')


def verify_public_candidates(config: dict, directory: Path, parts: dict, *, replay: bool = False) -> dict:
    """Recheck recorded candidates using separately coded Jacobian arithmetic."""
    root = Path.cwd().resolve()
    module = next(x for x in parts['modules'] if x['name'] == 'decoder')
    rows = [json.loads(line) for item in module['parts'] for line in (directory/item['path']).read_text().splitlines()]
    cases = {(fixture_name(x), x['target_id'], x['feature'], x['prefix_mode'], x['beam_width']): x for x in rows if x.get('row_kind') == 'target'}
    prefix = 'verification-check' if replay else 'verification'
    source = directory/('.'+prefix+'-input.tsv')
    output = directory/('.'+prefix+'-output.tsv')
    binary = directory/('.'+prefix+'.bin')
    success = False
    try:
        with source.open('x') as stream:
            stream.write('fixture_id\ttarget_id\tfeature\tprefix_mode\tbeam_width\tcandidate\n')
            for key, row in sorted(cases.items()):
                f, target, feature, mode, width = key
                for candidate in row['candidates']:
                    stream.write(f'{f}\t{target}\t{feature}\t{mode}\t{width}\t{candidate}\n')
        build = call(['g++', *config['compiler_flags'], config['verifier_source'], '-o', str(binary)], root,
            directory/(prefix+'-build.stdout.txt'), directory/(prefix+'-build.stderr.txt'), config['watchdog_seconds'])
        require(build['returncode'] == 0, 'independent verifier compilation failed')
        result = call([str(binary), '--verify', config['fixtures'], config['public_targets'], str(source), str(output)], root,
            directory/(prefix+'-run.stdout.txt'), directory/(prefix+'-run.stderr.txt'), config['watchdog_seconds'])
        require(result['returncode'] == 0 and output.is_file(), 'independent public-point verifier failed')
        verified = []
        lines = output.read_text().splitlines()
        require(lines and lines[0] == 'fixture_id\ttarget_id\tfeature\tprefix_mode\tbeam_width\tcandidate_count\tverification_hits\tverified_scalar', 'verification header')
        seen = set()
        for line in lines[1:]:
            f, target, feature, mode, width_text, count_text, hits_text, scalar_text = line.split('\t')
            width, count, hits, scalar = map(int, (width_text, count_text, hits_text, scalar_text))
            key = (f, target, feature, mode, width)
            require(key in cases and key not in seen, 'verification case coverage')
            seen.add(key)
            row = cases[key]
            actual_scalar = None if scalar == -1 else scalar
            require(count == len(row['candidates']) and hits == row['candidate_verification_hits'] and actual_scalar == row['verified_scalar'], 'independent public-point verification contradicts decoder')
            verified.append({'fixture': f, 'target_id': target, 'feature': feature, 'prefix_mode':mode, 'beam_width': width,
                'candidate_count': count, 'verification_hits': hits, 'verified_scalar': actual_scalar})
        require(seen == set(cases), 'missing independent candidate verification')
        if replay:
            initial = read_json(directory/'verification-manifest.json')
            require(sha(source) == initial['input_sha256'] and sha(output) == initial['output_sha256'], 'independent checker replay differs from certified verification')
            value = {'schema':'classical.ecdlp.public-verification-replay.v1', 'verification_manifest_sha256':sha(directory/'verification-manifest.json'), 'input_sha256':sha(source), 'output_sha256':sha(output), 'build':build, 'verification':result, 'candidate_cases':len(verified), 'recovered_cases':sum(x['verification_hits'] for x in verified), 'independent_review_session':False}
            write_once(directory/'verification-replay.json',value)
            success=True
            return value
        slots, next_slot, buffer = [], 0, bytearray()
        for row in verified:
            line = (json.dumps(row, separators=(',', ':'), allow_nan=False)+'\n').encode()
            require(len(line) <= CHUNK_LIMIT, 'verification row too large')
            if len(buffer)+len(line) > CHUNK_LIMIT:
                require(next_slot < VERIFICATION_PART_COUNT, 'verification output capacity')
                with (directory/f'verification-part-{next_slot:03}.jsonl').open('xb') as stream:
                    stream.write(buffer)
                next_slot += 1; buffer = bytearray()
            buffer.extend(line)
        if buffer:
            require(next_slot < VERIFICATION_PART_COUNT, 'verification output capacity')
            with (directory/f'verification-part-{next_slot:03}.jsonl').open('xb') as stream:
                stream.write(buffer)
            next_slot += 1
        for i in range(VERIFICATION_PART_COUNT):
            p = directory/f'verification-part-{i:03}.jsonl'
            if not p.exists():
                p.touch()
            slots.append({'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size})
        manifest = {'schema': 'classical.ecdlp.public-verification.v1', 'input_derivation': 'Sorted decoder target rows and their recorded candidate order; exact TSV header is source-bound.',
            'input_sha256': sha(source), 'input_bytes': source.stat().st_size, 'output_sha256': sha(output), 'output_bytes': output.stat().st_size,
            'build': build, 'verification': result, 'candidate_cases': len(verified), 'recovered_cases': sum(x['verification_hits'] for x in verified), 'unique_recovered_targets':len({(x['fixture'],x['target_id']) for x in verified if x['verification_hits']}),
            'arithmetic': 'independently coded Jacobian; imports no producer common arithmetic', 'hidden_scalar_labels_read': False, 'parts': slots}
        write_once(directory/'verification-manifest.json', manifest)
        success = True
        return {'candidate_cases': len(verified), 'recovered_cases': manifest['recovered_cases'], 'unique_recovered_targets':manifest['unique_recovered_targets'], 'source': 'verification-manifest.json', 'scientific_review_verified': False}
    finally:
        binary.unlink(missing_ok=True)
        for path, name in [(source, prefix+'-input-rescue.tsv.gz'), (output, prefix+'-output-rescue.tsv.gz')]:
            if success:
                path.unlink(missing_ok=True)
                (directory/name).touch(exist_ok=False)
            else:
                rescue(path, directory/name)


def partition(directory: Path, module: dict, next_slot: int, config: dict):
    fixture_ids = set(config['fixture_ids'])
    name = module['name']
    source = directory / ('.'+name+'.full.jsonl')
    require(source.is_file(), 'module produced no JSONL '+name)
    original_hash, original_bytes = sha(source), source.stat().st_size
    rows, actual_tracks, parts, buffer = 0, set(), [], bytearray()
    objects = []

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
            require(obj.get('scope') == SCOPE, 'output scope mismatch '+name)
            require(obj.get('attack_claimed') in (None, False), 'unqualified row-level attack claim; typed instance certificate belongs in main manifest')
            fixture = obj.get('fixture_id', obj.get('fixture'))
            if fixture is not None:
                require(fixture in fixture_ids or (fixture in module.get('global_fixture_aliases', []) and obj['track'] == 'L4-audit'), 'unknown fixture in '+name)
            actual_tracks.add(obj['track'])
            objects.append(obj)
            rows += 1
            if len(buffer)+len(line) > CHUNK_LIMIT:
                flush()
            buffer.extend(line)
    flush()
    require(rows > 0 and actual_tracks == set(module['tracks']), 'missing track output in '+name)
    reconstructed = b''.join((directory/x['path']).read_bytes() for x in parts)
    require(len(reconstructed) == original_bytes and hashlib.sha256(reconstructed).hexdigest() == original_hash, 'partition reconstruction failed')
    validate_rows(module, objects, config)
    source.unlink()
    return {'name': name, 'original_sha256': original_hash, 'original_bytes': original_bytes,
            'row_count': rows, 'tracks': sorted(actual_tracks), 'parts': parts}, next_slot


def execute(root: Path, config: dict, launch: dict, directory: Path) -> int:
    require(not (directory/'raw-result.json').exists(), 'outputs already exist')
    compiler = subprocess.check_output(['g++', '--version'], text=True).splitlines()[0]
    jobs = []
    for module in config['modules']:
        name = module['name']
        require(module_name_valid(name), 'unsafe module name')
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
            module = next(m for m in config['modules'] if m['name']==name)
            argv = [str(directory/('.'+name+'.bin')), '--run', module.get('fixtures',config['fixtures'])]
            if name == 'decoder':
                argv.append(config['public_targets'])
            argv.append(str(directory/('.'+name+'.full.jsonl')))
            return name, call(argv, root,
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
            parts, slot = partition(directory, module, slot, config)
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
    equations = None
    if not errors:
        try:
            equations = verify_public_candidates(config, directory, parts_manifest)
        except (OSError,ValueError,TypeError,KeyError) as error:
            errors.append({'module':'independent_public_point_verifier','reason':str(error)})
    write_once(directory/'parts-manifest.json', parts_manifest)
    attack = equations is not None and equations['recovered_cases'] > 0
    certificate = ({'kind':'discrete_log','verified':True,'claim_tier':'toy','scope':'Per-instance public scalar witnesses only, including chance-control hits; no general solver or advantage claim.', 'verified_case_witnesses':equations['recovered_cases'],'unique_recovered_targets':equations['unique_recovered_targets'],'verifier':'verification-manifest.json','verifier_manifest_sha256':sha(directory/'verification-manifest.json'),'verifier_source':config['verifier_source'],'verifier_source_sha256':sha(safe(root,config['verifier_source'])),'public_inputs_sha256':{'fixtures':sha(safe(root,config['fixtures'])),'public_targets':sha(safe(root,config['public_targets']))},'independent_arithmetic_implementation':True,'independent_scientific_review_session':False} if attack else {'kind':'none','verified':None,'note':'No independently verified instance recovery is claimed.'})
    metrics = {'modules_requested': len(MODULES), 'modules_with_partitioned_output': len(module_parts),
               'rows': sum(x['row_count'] for x in module_parts), 'tracks': len({t for m in module_parts for t in m['tracks']}), 'errors': len(errors), 'verified_case_witnesses':equations['recovered_cases'] if equations else None, 'unique_recovered_targets':equations['unique_recovered_targets'] if equations else None}
    raw = {'schema': 'classical.ecdlp.followup-result.v1', 'scope': SCOPE, 'attack_claimed': attack, 'attack_advantage_claimed':False, 'certificate':certificate,
           'experiment_id': config['experiment_id'], 'run_id': config['run_id'], 'source_commit': launch['authority']['commit'],
           'compiler': compiler, 'module_execution': jobs, 'metrics': metrics, 'errors': errors,
           'parts_manifest_sha256': sha(directory/'parts-manifest.json'), 'scientific_conclusion': None}
    write_once(directory/'raw-result.json', raw)
    # JSON is valid YAML. Only missing factual envelope fields are completed by
    # the genuine repository supervisor; this adapter supplies no authority.
    write_once(directory/'manifest.yaml', {'run': {'attack_claimed': attack, 'attack_advantage_claimed':False, 'metrics': metrics,
                'result': {'metrics': metrics, 'raw_result': 'raw-result.json', 'claim_tier': 'toy', 'certificate':certificate,
                           'note': 'Descriptive observations plus independently checked public per-instance witnesses when present; no advantage, novelty or general solver claim.'}}})
    return 0 if not errors else 2


def check(config: dict, directory: Path) -> None:
    raw, parts = read_json(directory/'raw-result.json'), read_json(directory/'parts-manifest.json')
    require(raw.get('schema') == 'classical.ecdlp.followup-result.v1' and type(raw.get('attack_claimed')) is bool and raw.get('attack_advantage_claimed') is False, 'raw schema/claim')
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
            require(obj.get('scope') == SCOPE and obj.get('track') in module['tracks'], 'row schema')
            fixture = obj.get('fixture_id', obj.get('fixture'))
            if fixture is not None:
                require(fixture in set(config['fixture_ids']) or (fixture in module.get('global_fixture_aliases', []) and obj['track'] == 'L4-audit'), 'unknown fixture in checked row')
            require(obj.get('attack_claimed') in (None, False), 'unqualified row-level attack claim')
            present.add(obj['track'])
        validate_rows(module, rows, config)
        require(present == set(module['tracks']), 'track coverage')
        tracks.update(present)
        row_count += len(rows)
    require(tracks == TRACKS and raw['metrics']['rows'] == row_count, 'batch coverage')
    require(all(j.get('measurement', {}).get('returncode') == 0 and j['build']['returncode'] == 0 and j.get('self_test', {}).get('returncode') == 0 for j in raw['module_execution']), 'execution code')
    public_equations = verify_public_candidates(config, directory, parts, replay=True)
    initial = read_json(directory/'verification-manifest.json')
    claimed = initial['recovered_cases'] > 0
    require(raw['attack_claimed'] is claimed, 'typed witness claim mismatch')
    cert=raw.get('certificate',{})
    require(cert.get('kind') == ('discrete_log' if claimed else 'none') and (not claimed or cert.get('verified') is True), 'typed certificate mismatch')
    if claimed:
        require(cert.get('verifier_manifest_sha256') == sha(directory/'verification-manifest.json') and cert.get('verifier_source_sha256') == sha(safe(Path.cwd(),config['verifier_source'])), 'witness certificate binding')
    import yaml
    manifest=yaml.safe_load((directory/'manifest.yaml').read_text())['run']
    require(manifest['attack_claimed'] is claimed and manifest['result']['certificate'] == cert, 'manifest/raw certificate mismatch')
    print(json.dumps({'independent_point_verification': public_equations, 'status': 'output_integrity_pass', 'rows': row_count, 'tracks': sorted(tracks), 'scientific_conclusion': None}))


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
