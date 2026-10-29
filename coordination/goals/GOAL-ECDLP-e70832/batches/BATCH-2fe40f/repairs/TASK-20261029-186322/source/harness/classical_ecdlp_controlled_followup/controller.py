#!/usr/bin/env python3
"""One candidate-only B2 VM, streamed immutable collection, then termination ACK.

No SDK imports on plan/check paths. Source-only release: scientific admission is
external and must bind the exact prospective configuration before run.
"""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

PREFIX = 'harness/classical_ecdlp_controlled_followup'
SCHEMA = 'classical.ecdlp.controlled-followup.'
WORKER = {'curve.py', 'constructor.py', 'cohort.py', 'engine.py', 'worker_runtime.py'}
APP_ID = 'ap-EAHJ6SjvmeY99EQ2I47duh'
IMAGE_ID = 'im-zz2zzbG7JE9xilcBO1QJMh'
HEX = re.compile('[0-9a-f]{64}\\Z')
REV = re.compile('[0-9a-f]{40}\\Z')
RAW = {'attempt-intents.jsonl', 'decoder-cells.jsonl', 'engine-completion.json',
       'engine-summary.json', 'setups.jsonl', 'single-points.jsonl', 'traces.jsonl'}


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def unique(pairs):
    result = {}
    for k, v in pairs:
        need(k not in result, 'duplicate JSON key: ' + k)
        result[k] = v
    return result


def finite_float(value):
    result=float(value)
    need(math.isfinite(result), 'nonfinite JSON number')
    return result


def read(path, limit=64 << 20):
    path = Path(path)
    need(path.is_file() and not path.is_symlink() and path.stat().st_size <= limit, 'bounded regular JSON required')
    return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_float=finite_float,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def safe(root, name):
    need(isinstance(name, str) and name and '\\' not in name, 'unsafe path')
    rel = PurePosixPath(name)
    need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == name and name != '.', 'unsafe path')
    root = Path(root).resolve()
    path = root / name
    need(path.resolve().is_relative_to(root) and not any(p.is_symlink() for p in [path, *path.parents] if p != root.parent), 'path escapes root or symlink')
    return path


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def source_payload(repo, manifest_path, kind):
    """Two-step bootstrap: source code commit first; manifest binds that ancestor.

    The manifest never includes its own bytes, eliminating a hash fixed point.
    """
    manifest = read(manifest_path)
    need(manifest.get('schema') == SCHEMA + kind + '-source-manifest/v1', 'source manifest schema')
    revision = manifest.get('source_revision', '')
    need(isinstance(revision, str) and REV.fullmatch(revision) is not None, 'unbound source manifest: root must supply published code commit')
    files = manifest.get('files', {})
    need(files and isinstance(files, dict), 'source manifest files')
    if kind == 'worker':
        need(set(files) == {PREFIX + '/' + n for n in WORKER}, 'exact five-module worker closure required')
    else:
        need(all((p.startswith(PREFIX + '/') and p.endswith(('.py', '.json'))) or p in {'tools/experiment_protocol.py','schemas/experiment-export.v1.json','schemas/experiment-protocol.v1.json','schemas/experiment-review.v1.json'} for p in files), 'host source path')
        need(not any(p.endswith('/' + n) for p in files for n in ['worker-source-manifest.json', 'host-source-manifest.json']), 'manifests cannot bind themselves')
    subprocess.run(['git', 'merge-base', '--is-ancestor', revision, 'HEAD'], cwd=repo, check=True, capture_output=True)
    payload = {}
    for name, digest in files.items():
        path = safe(repo, name)
        need(isinstance(digest, str) and HEX.fullmatch(digest), 'source digest')
        blob = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=repo)
        need(sha_bytes(blob) == digest and path.read_bytes() == blob, 'committed/live source mismatch: ' + name)
        payload[name] = blob
    if kind == 'worker':
        audit_closure({Path(p).name: b for p, b in payload.items()})
    return manifest, payload


def audit_closure(files):
    """Static import screen, not a sandbox or proof of runtime capability isolation.

    It checks literal imports and direct named dynamic calls only. Aliased,
    reflective and stdlib-mediated dynamic access is outside this screen's
    guarantee; committed-byte closure and OS/provider custody remain separate.
    """
    need(set(files) == WORKER, 'exact worker closure')
    std = set(sys.stdlib_module_names)
    for name, data in files.items():
        tree = ast.parse(data, filename=name)
        for node in ast.walk(tree):
            imports = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else ([node.module.split('.')[0]] if isinstance(node, ast.ImportFrom) and node.module else [])
            need(all(i in std or i + '.py' in WORKER for i in imports), 'worker import outside closure: ' + name)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                need(node.func.id not in {'__import__', 'eval', 'exec'}, 'dynamic worker import/code forbidden')


def invocation_config(repo, paths):
    required={'protocol','image_receipt','engine_plan','prior_exclusions','worker_manifest','host_manifest','engine_interface','host_interface'}
    need(set(paths)==required,'exact invocation input paths')
    bindings={}
    for role,name in paths.items():
        path=safe(repo,name)
        bindings[role]={'path':name,'sha256':sha_file(path)}
    static=read(safe(repo,paths['engine_plan']))
    config=dict(static['transport'])
    config.update(schema=SCHEMA+'transport-config/v1',inputs=bindings)
    return config


def make_plan(repo, config_path):
    config = config_path if isinstance(config_path,dict) else read(config_path)
    need(config.get('schema') == SCHEMA + 'transport-config/v1', 'config schema')
    need(config.get('automatic_retry') is False and config.get('maximum_vms') == 1, 'one VM/no retries')
    need(config.get('wall_valid') is False and config.get('counter_replay_qualified') is False, 'qualification flags')
    bindings = config.get('inputs', {})
    required = {'protocol', 'image_receipt', 'engine_plan', 'prior_exclusions', 'worker_manifest', 'host_manifest', 'engine_interface', 'host_interface'}
    need(set(bindings) == required, 'exact frozen input roles required')
    inputs = {}
    for role, item in bindings.items():
        need(set(item) == {'path', 'sha256'}, 'input binding fields')
        path = safe(repo, item['path'])
        need(HEX.fullmatch(item['sha256']) and sha_file(path) == item['sha256'], 'input hash mismatch: ' + role)
        inputs[role] = read(path)
    wm, workers = source_payload(repo, safe(repo, bindings['worker_manifest']['path']), 'worker')
    hm, hosts = source_payload(repo, safe(repo, bindings['host_manifest']['path']), 'host')
    need(str(Path(__file__).resolve()) == str(safe(repo, PREFIX + '/controller.py')), 'controller path differs')
    need(PREFIX + '/controller.py' in hosts and sha_file(__file__) == hm['files'][PREFIX + '/controller.py'], 'executing controller not bound')
    image = inputs['image_receipt']
    need(image.get('app_id') == APP_ID and image.get('image_id') == IMAGE_ID, 'observed B2 app/image required')
    limits = config.get('limits', {})
    need(set(limits) == {'max_total_bytes', 'max_file_bytes', 'max_jsonl_line_bytes', 'command_seconds', 'sandbox_seconds'}, 'explicit resource bounds')
    need(all(type(v) is int and v > 0 for v in limits.values()), 'positive integer limits')
    need(limits['max_file_bytes'] <= limits['max_total_bytes'] and limits['command_seconds'] + 60 < limits['sandbox_seconds'], 'limits inconsistent')
    plan = inputs['engine_plan']
    sampler=plan.get('sampler',{})
    need(set(sampler)=={'curve_proposal_limit','point_proposal_limit','target_proposal_limit'} and all(type(v)is int and v>0 for v in sampler.values()),'explicit positive sampler caps')
    exclusions=inputs['prior_exclusions'].get('excluded_p_j')
    need(isinstance(exclusions,list) and all(isinstance(x,list) and len(x)==2 and all(type(v)is int and v>=0 for v in x) for x in exclusions),'malformed exposed exclusions')
    need(len({tuple(x) for x in exclusions})==len(exclusions),'duplicate exposed exclusions')
    need(type(plan.get('max_total_orbit_points'))is int and plan['max_total_orbit_points']>0,'explicit orbit resource cap')
    need(plan.get('engine_interface_canonical_sha256') == sha_bytes(canonical(inputs['engine_interface'])), 'engine interface binding')
    need(config.get('seed_rules') == {'worker_nonce_bytes':32,'worker_draw':'after_admission_before_sampling','stage_streams':'domain_separated_SHA256_from_one_public_nonce','host_draw':'after_collection_seal_and_termination_ack','host_seed_bytes':32}, 'explicit prospective seed rules required')
    need(not any(k in config for k in ['public_nonce','stage_seeds','host_seeds']), 'realized seeds cannot appear in static settings')
    need(config.get('schedule') == {'curves': 48, 'calibration_curves': 24, 'calibration_arms': 8, 'confirmation_curves': 24, 'confirmation_arm': 'circuit2.a1', 'targets_per_confirmation_curve': 64, 'blindings_per_target': 8, 'confirmation_traces': 12288, 'confirmation_cells': 73728, 'physical_calls_before_controls': 1033728}, 'fixed production schedule')
    protocol=inputs['protocol']
    need(protocol.get('freeze',{}).get('status')=='frozen' and protocol['freeze'].get('protocol_sha256')==sha_bytes(canonical({k:v for k,v in protocol.items() if k!='freeze'})), 'frozen full protocol binding required')
    extension = protocol.get('extensions', {}).get('controlled_followup', {})
    need(extension.get('static_inputs') == {k:v for k,v in bindings.items() if k != 'protocol'}, 'protocol static input bindings differ')
    result = {'schema': SCHEMA + 'transport-plan/v1', 'config_sha256': sha_bytes(canonical(config)),
              'source_fingerprint': sha_bytes(canonical({'worker': wm, 'host': hm})),
              'source_revisions': {'worker': wm['source_revision'], 'host': hm['source_revision']},
              'inputs': bindings, 'schedule': config['schedule'], 'limits': limits,
              'runtime': {'app_id': APP_ID, 'image_id': IMAGE_ID, 'cpu': [2, 2], 'memory_mib': [12288, 12288], 'runtime': 'vm', 'block_network': True, 'uid': 1000, 'gid': 1000, 'supplementary_groups': [], 'secrets': []},
              'worker_files': sorted(WORKER), 'maximum_vms': 1, 'automatic_retry': False,
              'wall_valid': False, 'counter_replay_qualified': False,
              'measurement_started': False, 'fresh_draws': 0}
    return result, config, inputs, workers


# Sent as trusted root bootstrap, never staged as a sixth worker source module.
# No labels/reference code appears here. Quiescence is observed, not worker asserted.
BOOTSTRAP = r'''
import hashlib,json,os,pathlib,subprocess,sys
root=pathlib.Path('/work'); os.chown(root,0,0); root.chmod(0o755); out=root/'result'; out.mkdir(); tmp=root/'tmp'; tmp.mkdir(exist_ok=True)
for folder in ['source','stage']:
 for p in [root/folder,*(root/folder).rglob('*')]:
  if p.is_symlink(): raise ValueError('symlink in stage')
  os.chown(p,0,0); p.chmod(0o555 if p.is_dir() else 0o444)
os.chown(out,1000,1000); os.chown(tmp,1000,1000)
argv=['env','-i','PATH=/usr/local/bin:/usr/bin:/bin','HOME=/work','TMPDIR=/work/tmp','PYTHONDONTWRITEBYTECODE=1','LC_ALL=C.UTF-8','setpriv','--reuid=1000','--regid=1000','--clear-groups','--no-new-privs','python3','/work/source/worker_runtime.py','--request','/work/stage/request.json','--out','/work/result/raw']
request=json.loads((root/'stage/request.json').read_bytes())
with (root/'worker.stdout').open('xb') as stdout,(root/'worker.stderr').open('xb') as stderr:
 try: code=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True,timeout=request['command_seconds']).returncode
 except subprocess.TimeoutExpired: code=124
pids=[]
for p in pathlib.Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   if any(line.startswith('Uid:') and '1000' in line.split()[1:] for line in (p/'status').read_text().splitlines()): pids.append(int(p.name))
  except (FileNotFoundError,ProcessLookupError,PermissionError): pass
if pids: raise ValueError('UID1000 still active; no collection seal')
for name in ['worker.stdout','worker.stderr']:
 (root/name).rename(out/name)
files=[]
for p in sorted(out.rglob('*')):
 if p.is_symlink() or not (p.is_dir() or p.is_file()): raise ValueError('unsafe output')
 os.chown(p,0,0); p.chmod(0o555 if p.is_dir() else 0o444)
 if p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1048576),b''): h.update(block)
  files.append({'path':str(p.relative_to(out)),'sha256':h.hexdigest(),'size':p.stat().st_size})
os.chown(out,0,0); out.chmod(0o555)
print(json.dumps({'engine_returncode':code,'uid1000_quiescent':True,'files':files},sort_keys=True))
'''


def validate_entries(entries, limits):
    need(isinstance(entries, list) and len(entries) <= 64, 'bounded output tree')
    seen = set(); total = 0
    for e in entries:
        need(set(e) == {'path', 'sha256', 'size'}, 'output entry schema')
        safe('/work/result', e['path'])
        need(e['path'] not in seen and HEX.fullmatch(e['sha256']), 'duplicate path/digest')
        need(type(e['size']) is int and 0 <= e['size'] <= limits['max_file_bytes'], 'file resource cap exceeded; no truncation')
        total += e['size']; seen.add(e['path'])
    need(total <= limits['max_total_bytes'], 'total resource cap exceeded; no truncation')
    return sorted(entries, key=lambda e: e['path'])


def collect_stream(sandbox, output, entries, limits):
    entries = validate_entries(entries, limits)
    output = Path(output); output.mkdir()
    for e in entries:
        dest = safe(output, e['path']); dest.parent.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256(); size = 0
        with sandbox.open('/work/result/' + e['path'], 'rb') as source, dest.open('xb') as target:
            while True:
                block = source.read(1 << 20)
                if not block: break
                size += len(block)
                need(size <= e['size'], 'stream exceeds sealed size')
                h.update(block); target.write(block)
            target.flush(); os.fsync(target.fileno())
        need(size == e['size'] and h.hexdigest() == e['sha256'] and sha_file(dest) == e['sha256'], 'stream/readback mismatch')
        dest.chmod(0o444)
    return entries


def custody_for(output, record):
    """Convert authenticated parent/provider events; never trust a worker boolean."""
    need(record.get('collection_complete') is True and record.get('uid1000_quiescent') is True, 'collection/quiescence incomplete')
    ack = record.get('termination_ack') or {}
    need(ack.get('acknowledged') is True and ack.get('transport_id') and ack.get('uid') == 1000, 'actual termination ACK missing')
    entries = validate_entries(record['files'], record['plan']['limits'])
    need({'host-plan.json', 'public-cohort.json'} <= {e['path'] for e in entries}, 'required public custody entries missing')
    raw = []
    for e in entries:
        path = safe(output, e['path'])
        need(path.is_file() and path.stat().st_size == e['size'] and sha_file(path) == e['sha256'], 'custody readback')
        if e['path'].startswith('raw/'):
            need(e['path'][4:] in RAW, 'extra candidate output field/file')
            raw.append({**e, 'path': e['path'][4:]})
    need({e['path'] for e in raw} == RAW, 'complete seven candidate files required')
    raw.sort(key=lambda e:e['path'])
    return {'schema': SCHEMA + 'host-custody/v1', 'collection_complete': True, 'sealed': True,
            'uid1000_quiescent': True, 'termination_ack': ack, 'files': raw,
            'tree_sha256': sha_bytes(canonical(raw))}


def snapshot_inputs(repo, config_path, config, inputs, out):
    # Retain original bytes, not a reserialized approximation of frozen inputs.
    with (out/'config.json').open('xb') as target: target.write(canonical(config)+b'\n')
    for role, binding in config['inputs'].items():
        blob=safe(repo,binding['path']).read_bytes()
        need(sha_bytes(blob)==binding['sha256'],'input changed during snapshot')
        with (out/(role+'.json')).open('xb') as target: target.write(blob)


def bindings_protocol_sha(config):
    return config['inputs']['protocol']['sha256']


def run(repo, config_path, out, sdk=None, supervisor_identity=None):
    if supervisor_identity is not None:
        need(set(supervisor_identity) == {'experiment_id', 'run_id'} and isinstance(supervisor_identity['experiment_id'], str) and supervisor_identity['experiment_id'].startswith('EXP-') and isinstance(supervisor_identity['run_id'], str) and supervisor_identity['run_id'].startswith('RUN-'), 'allocated supervisor identity')
    plan, config, inputs, workers = make_plan(repo, config_path)
    if supervisor_identity is not None:
        need(inputs['protocol']['protocol_id'] == supervisor_identity['experiment_id'], 'controller protocol/allocated experiment mismatch')
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    write(out/'plan.json', plan)
    snapshot_inputs(repo, config_path, config, inputs, out)
    snapshot=out/'staged-source';snapshot.mkdir()
    for name,blob in workers.items():
        with (snapshot/Path(name).name).open('xb') as target:target.write(blob)
    record = {'schema': SCHEMA+'controller-receipt/v1', 'plan': plan, 'vm_creates': 0, 'engine_execs': 0,
              'files': [], 'collection_complete': False, 'uid1000_quiescent': False,
              'termination_ack': None, 'automatic_retry': False, 'wall_valid': False}
    if supervisor_identity is not None:
        record['supervisor_identity'] = dict(supervisor_identity)
    sb = None
    try:
        if sdk is None:
            import modal as sdk
        need(sdk.__version__ == '1.6.2', 'reviewed Modal SDK1.6.2 required')
        image = inputs['image_receipt']
        app = sdk.App.lookup(image['app_name'], environment_name=image['environment_name'], create_if_missing=False)
        need(app.app_id == APP_ID, 'actual app identity')
        native = sdk.Image.from_id(IMAGE_ID)
        record['vm_creates'] = 1; write(out/'create-intent.json', record)
        sb = sdk.Sandbox.create('sleep', str(plan['limits']['sandbox_seconds']), app=app, image=native,
            runtime='vm', block_network=True, cpu=(2,2), memory=(12288,12288), secrets=[],
            include_oidc_identity_token=False, timeout=plan['limits']['sandbox_seconds'], workdir='/work')
        record['sandbox_id'] = sb.object_id
        for remote,key in [('build-info.json','build_info_sha256'),('adapter-manifest.json','adapter_manifest_sha256'),('modal-image-build.json','build_provenance_sha256')]:
            with sb.open('/opt/study/'+remote,'rb') as source: blob=source.read((1<<20)+1)
            need(len(blob)<=1<<20 and sha_bytes(blob)==image[key], 'actual B2 image metadata differs')
            with (out/remote).open('xb') as target: target.write(blob)
        # Only public data and the exact worker source closure enter this VM.
        request = {'schema': SCHEMA+'worker-request/v1', 'engine_plan': inputs['engine_plan'],
                   'sampler': inputs['engine_plan']['sampler'], 'prior_exclusions': inputs['prior_exclusions'],
                   'seed_rules': config['seed_rules'],
                   'provenance': {'protocol_sha256': bindings_protocol_sha(config), 'source_fingerprint': plan['source_fingerprint']},
                   'source_files': {Path(k).name: sha_bytes(v) for k,v in workers.items()},
                   'command_seconds': plan['limits']['command_seconds']}
        sb.exec('mkdir','-p','/work/source','/work/stage').wait()
        for name, blob in {**{'/work/source/'+Path(k).name:v for k,v in workers.items()}, '/work/stage/request.json': canonical(request)}.items():
            with sb.open(name,'wb') as target: target.write(blob)
        record['engine_execs'] = 1; write(out/'engine-intent.json', record)
        proc = sb.exec('python3','-c',BOOTSTRAP, timeout=plan['limits']['command_seconds']+60)
        rc = proc.wait()
        stdout = proc.stdout.read(); stderr = proc.stderr.read()
        (out/'bootstrap.stdout').write_text(stdout); (out/'bootstrap.stderr').write_text(stderr)
        need(rc == 0, 'trusted root bootstrap failed; partial remote tree retained')
        seal = json.loads(stdout, object_pairs_hook=unique)
        record['engine_returncode'] = seal['engine_returncode']
        record['uid1000_quiescent'] = seal['uid1000_quiescent'] is True
        record['files'] = validate_entries(seal['files'], plan['limits'])
        write(out/'remote-seal.json', seal)
        record['files'] = collect_stream(sb, out/'collected', record['files'], plan['limits'])
        record['collection_complete'] = True
        # Blocking provider acknowledgement. Merely issuing terminate is insufficient.
        terminated_returncode=sb.terminate(wait=True)
        record['termination_ack'] = {'acknowledged': True, 'transport_id': sb.object_id + '/terminate-wait-returned', 'uid': 1000, 'provider_returncode':terminated_returncode}
        write(out/'custody.json', custody_for(out/'collected', record))
    except Exception as error:
        record['error'] = {'type': type(error).__name__, 'message': str(error)}
        record['remote_preserved_for_collection'] = sb is not None and not record['collection_complete']
    record['status'] = 'complete' if not record.get('error') and record.get('engine_returncode') == 0 and record.get('termination_ack') else 'failed'
    write(out/'controller-receipt.json', record)
    return record
