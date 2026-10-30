"""Post-seal width analysis/export from retained native bytes; no relation work.

Missing raw hydration, native identity, seed or complete successful-cell coverage
is refused. Unrecorded producer/host/isolation facts stay explicitly unknown;
all diagnostic clocks are invalid for comparative timing. No network access.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'tools'))
import experiment_protocol as ep

EXPERIMENT = 'EXP-ECDLP-a9b6a5'
PRIMARY = ['attempted', 'accepted', 'U', 'rank', 'augmented_rank', 'nullity']
ARM_NATIVE = {'m16_candidate': 'm16_full35840', 'm8_reference': 'full3584'}
ARM_SOURCE = {'m16_candidate': 'research/prym_factor_base_width_20261025/collect_width.py',
              'm8_reference': 'research/prym_rank_census_20261025/rank_census.py'}
METRIC_SOURCES = dict(attempted='cell.attempts', accepted='len(cell.rows)',
                      U='cell.projection.U', rank='cell.projection.rank',
                      augmented_rank='cell.projection.augmented_rank',
                      nullity='cell.projection.U-cell.projection.rank')
REQUIRED = ['raw-result.json', 'verification.json', 'manifest.yaml', 'execution-receipt.json',
            'environment.json', 'launch.json', 'events.jsonl']


def file_record(path, base, kind='raw'):
    path = Path(path).resolve()
    return dict(path=os.path.relpath(path, base), sha256=ep.sha256_file(path),
                bytes=path.stat().st_size, kind=kind)


def read_package(directory, *, software=False):
    directory = Path(directory).resolve()
    for name in REQUIRED:
        if not (directory/name).is_file():
            raise ep.Refused('genuine native bytes unavailable; hydrate '+str(directory/name))
    raw = ep.read_json(directory/'raw-result.json')
    check = ep.read_json(directory/'verification.json')
    receipt = ep.read_json(directory/'execution-receipt.json')
    environment = ep.read_json(directory/'environment.json')
    launch = ep.read_json(directory/'launch.json')
    manifest = yaml.safe_load((directory/'manifest.yaml').read_text())['run']
    run_id = manifest.get('id')
    commit = manifest.get('code', {}).get('commit')
    if (not run_id or any(v != run_id for v in [receipt.get('run_id'), launch.get('run_id'), raw.get('run_id')]) or
        not isinstance(commit, str) or re.fullmatch('[0-9a-f]{40}', commit) is None or
        environment.get('commit') != commit or launch.get('authority', {}).get('commit') != commit or
        receipt.get('plan_sha256') != launch.get('plan_sha256') or not receipt.get('plan_sha256')):
        raise ep.Refused('missing or contradictory observed native run/source identity')
    if manifest.get('experiment_id') != raw.get('experiment_id'):
        raise ep.Refused('native experiment identity differs')
    for name in REQUIRED:
        if name == 'execution-receipt.json':
            continue
        if receipt.get('artifact_sha256', {}).get(name) != ep.sha256_file(directory/name):
            raise ep.Refused('native receipt/file commitment differs: '+name)
    if check.get('raw_result_sha256') != ep.sha256_file(directory/'raw-result.json'):
        raise ep.Refused('checker/raw identity differs')
    config = manifest.get('inputs', {}).get('config', {})
    fixture_name = config.get('fixture_file')
    if not fixture_name or Path(fixture_name).is_absolute() or '..' in Path(fixture_name).parts:
        raise ep.Refused('missing observed native fixture input identity')
    fixture_path = ROOT/fixture_name
    if (not fixture_path.is_file() or
        manifest.get('inputs', {}).get('sha256', {}).get(fixture_name) != ep.sha256_file(fixture_path)):
        raise ep.Refused('observed fixture bytes/hash unavailable')
    fixtures = ep.read_json(fixture_path)['fixtures']
    if software:
        if not raw.get('software_control') or any(f['p'] > 211 for f in fixtures):
            raise ep.Refused('software export requires explicitly planted small inputs')
    elif not all(f['p'] == 4099 for f in fixtures if f['b'] in [13, 16]):
        raise ep.Refused('wrong target fixture identity')
    return dict(directory=directory, raw=raw, check=check, receipt=receipt,
                environment=environment, launch=launch, manifest=manifest,
                fixtures=fixtures, fixture_path=fixture_path, commit=commit, run_id=run_id)


def validate_protocol(path):
    path = Path(path).resolve()
    protocol = ep.read_json(path)
    findings = ep.schema_errors(protocol, 'experiment.protocol/v1')
    if not findings:
        findings = ep.lint_protocol(protocol, path.parent)
    if findings or protocol['freeze']['status'] != 'frozen':
        raise ep.Refused('frozen protocol validation failed: '+'; '.join(findings))
    if ([a['id'] for a in protocol['arms']] != ['m16_candidate', 'm8_reference'] or
        protocol['sample_size']['instances'] != 2 or protocol['sample_size']['replicates'] != 1 or
        protocol['sample_size']['warmups'] != 0 or
        [m['id'] for m in protocol['metrics']['primary']] != PRIMARY or
        protocol['randomization']['seed_derivation']['method'] != 'harness_drawn' or
        protocol['execution']['timeout_seconds'] != 86400 or
        protocol['execution']['placement'].get('claim_ttl_minutes') != 1500 or
        protocol['execution']['placement'].get('claim_ttl_seconds') != 90000):
        raise ep.Refused('protocol does not match fixed width arm/metric/seed contract')
    script = protocol['analysis_plan']['script']
    if (not script or (path.parent/script['path']).resolve() != Path(__file__).resolve() or
        script['sha256'] != ep.sha256_file(Path(__file__))):
        raise ep.Refused('analysis/export helper is not exactly frozen')
    return protocol


def flatten_counters(value, prefix='', out=None):
    out = {} if out is None else out
    if isinstance(value, dict):
        for key, item in value.items():
            flatten_counters(item, prefix+'.'+str(key) if prefix else str(key), out)
    elif isinstance(value, list):
        out[prefix] = json.dumps(value, sort_keys=True, separators=(',', ':'))
    elif isinstance(value, (int, float, str)) and not isinstance(value, bool):
        out[prefix] = value
    return out


def cell_counts(cell):
    p = cell['projection']
    values = dict(attempted=cell['attempts'], accepted=len(cell['rows']), U=p['U'],
                  rank=p['rank'], augmented_rank=p['augmented_rank'], nullity=p['U']-p['rank'])
    if (any(type(v) is not int or v < 0 for v in values.values()) or
        sum(cell['reasons'].values()) != cell['attempts'] or
        cell['reasons'].get('+', 0) != len(cell['rows'])):
        raise ep.Refused('inconsistent observed finite counts/status coverage')
    return values


def build(protocol_path, candidate_dir, reference_dir, out, *, software=False):
    protocol_path, out = Path(protocol_path).resolve(), Path(out).resolve()
    protocol = validate_protocol(protocol_path)
    packages = {arm: read_package(directory, software=software) for arm, directory in
                [('m16_candidate', candidate_dir), ('m8_reference', reference_dir)]}
    for package in packages.values():
        if out == package['directory'] or package['directory'] in out.parents:
            raise ep.Refused('export/analysis must remain outside sealed native run directories')
    if not software and out.parent != ROOT/f'experiments/{EXPERIMENT}':
        raise ep.Refused('width export must be beside the experiment outside its sealed run')
    result = ep.export_skeleton(protocol, os.path.relpath(protocol_path, out.parent), 'local', 'width-native-export-v1')
    # Do not inherit generic adapter environment defaults as producer evidence.
    candidate = packages['m16_candidate']
    protocol_relative = str(protocol_path.relative_to(ROOT))
    protocol_file_sha = ep.sha256_file(protocol_path)
    expected_binding = dict(path=protocol_relative, file_sha256=protocol_file_sha,
                            canonical_sha256=protocol['freeze']['protocol_sha256'])
    if (candidate['manifest'].get('inputs', {}).get('sha256', {}).get(protocol_relative) != protocol_file_sha or
        (candidate['raw'].get('complete') or 'protocol_binding' in candidate['raw']) and
            candidate['raw'].get('protocol_binding') != expected_binding):
        raise ep.Refused('candidate native protocol file/canonical binding differs')
    observed_producer = candidate['manifest'].get('producer', {})
    result['producer'] = {k: observed_producer.get(k) for k in ['runtime', 'model', 'session', 'role']}
    result['source'] = dict(repo=candidate['manifest']['code'].get('repository') or 'unrecorded',
                            commit=candidate['commit'],
                            dirty=(bool(candidate['manifest']['code']['dirty_tree'])
                                   if 'dirty_tree' in candidate['manifest']['code'] else None))
    host = candidate['environment'].get('host', {})
    result['host'] = dict(path=os.path.relpath(candidate['directory']/'environment.json', out.parent),
                          sha256=ep.sha256_file(candidate['directory']/'environment.json'),
                          class_id=host.get('class_id'), summary={k: host.get(k) for k in
                          ['cpu_model', 'logical_cpus', 'memory_bytes', 'kernel', 'hypervisor', 'isolation_tier_max']})
    result['backend_record'] = dict(metric_source_mapping=METRIC_SOURCES, native_packages={},
                                   conditioning='m8 reference labels already seen; same-curve conditional follow-up.',
                                   clock_policy='Diagnostic clocks retained; wall_valid=false, no clock advantage or per-cell allocation of shared physical run costs.',
                                   partial_S_exclusions=['pow internals', 'Python bookkeeping', 'general byte movement',
                                                         'independent primitive reconciliation', 'complete weighted S'])
    files = [file_record(protocol_path, out.parent, 'protocol'), file_record(Path(__file__), out.parent, 'analysis')]
    for arm, exported_arm in zip(protocol['arms'], result['arms']):
        name = arm['id']
        package = packages[name]
        manifest, raw, checker, receipt = (package[k] for k in ['manifest', 'raw', 'check', 'receipt'])
        source_digest = manifest['code'].get('source_sha256', {}).get(ARM_SOURCE[name])
        if not isinstance(source_digest, str) or re.fullmatch('[0-9a-f]{64}', source_digest) is None:
            raise ep.Refused('missing observed Python executable source identity')
        exported_arm.update(commit=package['commit'], binary_sha256=source_digest)
        artifacts = [file_record(package['directory']/n, out.parent,
                                 'receipt' if n == 'execution-receipt.json' else 'host' if n == 'environment.json' else 'raw') for n in REQUIRED]
        artifacts.append(file_record(package['fixture_path'], out.parent, 'other'))
        for physical in package['directory'].glob('*.blob.json'):
            artifacts.append(file_record(physical, out.parent, 'other'))
        files.extend(artifacts)
        fixture_ids = {}
        for f in package['fixtures']:
            if f['b'] in [13, 16] and (software or f['p'] == 4099):
                label = 'b'+str(f['b'])
                if label in fixture_ids:
                    raise ep.Refused('ambiguous observed fixture instance')
                fixture_ids[label] = f['uid']
        if set(fixture_ids) != {'b13', 'b16'}:
            raise ep.Refused('missing observed fixture instances')
        selected = [c for c in raw['cells'] if c['curve_uid'] in fixture_ids.values() and c['arm'] == ARM_NATIVE[name]]
        if raw.get('complete') and (len(selected) != 2 or len({c['curve_uid'] for c in selected}) != 2):
            raise ep.Refused('missing/duplicate successful native cell coverage')
        result['backend_record']['native_packages'][name] = dict(
            run_id=package['run_id'], directory=os.path.relpath(package['directory'], out.parent),
            source_commit=package['commit'], producer=manifest.get('producer'),
            observed_native_launch_argv=package['launch'].get('argv'),
            environment=package['environment'], physical_timing=manifest.get('timing'),
            receipt_status=receipt.get('status'), checker_status=checker.get('status'),
            raw_input_construction_costs=raw.get('input_construction_costs'),
            producer_artifact_counters=raw.get('producer_artifact_counters'),
            raw_unselected_cell_identities=[dict(curve_uid=c['curve_uid'], arm=c['arm'], seed=c.get('seed'))
                                            for c in raw['cells'] if c not in selected],
            missing_observations=[k for k in ['runtime', 'model', 'session', 'role'] if not manifest.get('producer', {}).get(k)])
        for instance, fixture_uid in sorted(fixture_ids.items()):
            matches = [c for c in selected if c['curve_uid'] == fixture_uid]
            cell = matches[0] if len(matches) == 1 else None
            if cell is not None and (cell.get('seed') != 0 or type(cell.get('seed')) is not int):
                raise ep.Refused('missing/wrong observed seed: fixed seed0 required')
            status = 'succeeded' if (raw.get('complete') and receipt.get('status') == 'output_validated' and
                                      checker.get('status') == 'passed' and cell is not None) else receipt.get('status')
            status = status if status in ['succeeded', 'failed', 'timeout', 'cancelled', 'infra_error', 'interrupted'] else 'infra_error'
            counts = cell_counts(cell) if cell is not None else {}
            verified = 'verified' if checker.get('status') == 'passed' and cell is not None else 'error'
            if verified == 'verified':
                checks = [c for c in checker['cells'] if c['curve_uid'] == fixture_uid and
                          c.get('arm', ARM_NATIVE[name]) == ARM_NATIVE[name]]
                expected = {k: counts[v] for k, v in [('attempts_replayed', 'attempted'), ('rows_verified', 'accepted'),
                                                       ('U', 'U'), ('rank', 'rank'), ('augmented_rank', 'augmented_rank')]}
                if len(checks) != 1 or any(checks[0].get(k) != v for k, v in expected.items()):
                    raise ep.Refused('checker/native cell coverage or metrics differ')
            counters = flatten_counters({k: v for k, v in (cell or {}).items() if k not in
                                         ['rows', 'projection', 'transported_witness_hashes', 'curve_uid', 'arm', 'seed', 'p', 'b']}, 'producer')
            if cell is not None:
                flatten_counters({k: v for k, v in cell['projection'].items() if 'operation' in k or 'units' in k},
                                 'producer.projection', counters)
            flatten_counters({k: v for k, v in checker.items() if k != 'cells'}, 'checker', counters)
            for reason, count in (cell or {}).get('reasons', {}).items():
                counters['reason_'+reason] = count
            resumed = receipt.get('resumed', 0)
            if type(resumed) is not int or resumed < 0:
                raise ep.Refused('invalid observed resume counter')
            if 'resumed' not in receipt:
                counters['resume_observation'] = 'unrecorded; clock invalid'
            isolation = package['environment'].get('isolation', {})
            result['runs'].append(ep.run_row(
                run_id=package['run_id']+'-'+instance, arm=name, instance_id=instance,
                seed=cell.get('seed') if cell else None, replicate=0, warmup=False,
                status=status, resumed=resumed, checkpoint=receipt.get('checkpoint'),
                measurements=dict(counted=counts, wall_seconds=(cell or {}).get('wall_seconds'),
                                  wall_valid=False, cpu_user_seconds=(cell or {}).get('cpu_user_seconds'),
                                  cpu_sys_seconds=(cell or {}).get('cpu_sys_seconds'),
                                  max_rss_bytes=(cell or {}).get('max_rss_bytes'), counters=counters),
                isolation=dict(tier=isolation.get('tier'), contended=isolation.get('contended'),
                               blockers=isolation.get('blockers', [])+['Diagnostic clock excluded; isolation/resume/per-cell timing not certified for comparisons.']),
                verification=dict(status=verified, verifier='retained independent verification.json'),
                exclusion=dict(excluded=status != 'succeeded' or verified != 'verified',
                               rule='native_incomplete_or_invalid' if status != 'succeeded' or verified != 'verified' else None),
                artifacts=deepcopy(artifacts), backend_ref=package['run_id']))
    unique = {f['path']: f for f in files}
    result['files'] = list(unique.values())
    result['flow'] = ep.compute_flow(result['runs'])
    result['analysis']['script'] = file_record(Path(__file__), out.parent, 'analysis')
    result['notes'] = [dict(kind='observation', by='export_width.py', text=text) for text in [
        'Planted software package only.' if software else 'Retained native bytes; no new m8 execution or additional scientific control arm.',
        'Producer/host facts absent from native records remain null or unrecorded; no planned identity, host, isolation or seed fills missing observations.',
        'Failure/censored cells remain rows and are excluded by named rule. Every emitted counter is retained separately; raw vectors remain partial S.']]
    analysis = dict(schema='prym-width-descriptive-analysis/v1', protocol_sha256=result['protocol']['sha256'],
                    metric_source_mapping=METRIC_SOURCES, flow=result['flow'],
                    cells=[dict(run_id=r['run_id'], arm=r['arm'], instance_id=r['instance_id'],
                                status=r['status'], counted=r['measurements']['counted']) for r in result['runs']],
                    clocks_valid_for_advantage=False, inference='Finite conditioned observations only; no verdict, gain or security claim.')
    findings = ep.schema_errors(result, 'experiment.export/v1') or ep.lint_export(result, protocol, out.parent, True)
    if findings:
        raise ep.Refused('export validation failed: '+'; '.join(findings))
    return result, analysis, protocol


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['analysis', 'export'])
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--candidate-run-dir', required=True, type=Path)
    parser.add_argument('--reference-run-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--software', action='store_true')
    args = parser.parse_args(argv)
    if (not args.software and args.mode == 'export' and
            args.output.resolve() != ROOT/f'experiments/{EXPERIMENT}/export.json'):
        raise ep.Refused('native unified export destination is experiments/'+EXPERIMENT+'/export.json')
    result, analysis, protocol = build(args.protocol, args.candidate_run_dir, args.reference_run_dir,
                                       args.output, software=args.software)
    if args.mode == 'analysis':
        ep.write_once(args.output, analysis)
    else:
        if args.output.exists():
            raise ep.Refused('export output already exists')
        analysis_path = args.output.with_name(args.output.stem+'-analysis.json')
        if analysis_path.exists():
            raise ep.Refused('analysis output already exists')
        ep.write_once(analysis_path, analysis)
        result['analysis']['outputs'] = [file_record(analysis_path, args.output.resolve().parent, 'analysis')]
        ep.write_once(args.output, result)
        findings = ep.schema_errors(result, 'experiment.export/v1') or ep.lint_export(result, protocol, args.output.resolve().parent, True)
        if findings:
            raise ep.Refused('written export failed checks: '+'; '.join(findings))
    print(json.dumps(dict(status='passed', mode=args.mode, rows=len(result['runs']), flow=result['flow'])))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ep.Refused as error:
        print('REFUSED: '+str(error), file=sys.stderr)
        raise SystemExit(2)
