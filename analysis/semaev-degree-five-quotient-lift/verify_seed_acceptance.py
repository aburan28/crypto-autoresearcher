#!/usr/bin/env python3
"""Candidate binding verifier for historical independent seed acceptance.

This checks custody and byte identity, not algebra. The prior independent
checker result is historical; final D5 independent checking remains mandatory.
"""
import hashlib,json,re
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def target_args(record):
    return list(map(str,[record['n'],record['modulus_hex'],record['a2'],record['a6_hex'],record['z_hex'],*record['V_basis_hex']]))


def verify(capsule_path,request,checker_path,seed_path):
    capsule_path=Path(capsule_path);root=capsule_path.parent.resolve();seed_path=Path(seed_path)
    if sha(capsule_path)!=request['seed_acceptance']['sha256']:
        raise ValueError('historical acceptance capsule hash mismatch')
    capsule=json.loads(capsule_path.read_text())
    if capsule['schema']!='semaev.historical-seed-acceptance/v1':raise ValueError('unsupported capsule schema')
    files={}
    required={'request','manifest','worker','argv','step','stdout','seed_transfer'}
    if set(capsule['evidence'])!=required:raise ValueError('incomplete historical evidence set')
    for key,entry in capsule['evidence'].items():
        path=(root/entry['path']).resolve(strict=True)
        if not path.is_relative_to(root) or path.stat().st_size>16<<20:raise ValueError('evidence path or size invalid')
        if path.stat().st_size!=entry['bytes'] or sha(path)!=entry['sha256']:raise ValueError('historical evidence hash mismatch: '+key)
        files[key]=path
    original=json.loads(files['request'].read_text());manifest=json.loads(files['manifest'].read_text())
    if original['worker_manifest_sha256']!=sha(files['manifest']):raise ValueError('original request/manifest mismatch')
    if manifest['files'][capsule['worker_manifest_key']]!=sha(files['worker']):raise ValueError('original worker binding mismatch')
    if manifest['files']['cert_check.py']!=sha(checker_path):raise ValueError('original checker differs from current independent checker')
    if target_args(original['record'])!=target_args(request['record']):raise ValueError('historical target differs')
    argv=json.loads(files['argv'].read_text())
    if len(argv)<3 or Path(argv[1]).name!='cert_check.py' or Path(argv[2]).name!='seed.bin' or argv[3:]!=target_args(request['record']):
        raise ValueError('historical checker invocation differs')
    step=json.loads(files['step'].read_text())
    if type(step['returncode']) is not int or step['returncode']!=0 or step['timeout'] is not False:
        raise ValueError('historical checker did not complete successfully')
    transfer=json.loads(files['seed_transfer'].read_text());prior_digest=transfer.get('seed_sha256',transfer.get('sha256'))
    if original['seed_sha256']!=request['seed_sha256'] or prior_digest!=request['seed_sha256']:
        raise ValueError('historical seed identity differs')
    if seed_path.stat().st_size!=request['seed_bytes'] or transfer['bytes']!=request['seed_bytes'] or sha(seed_path)!=request['seed_sha256']:
        raise ValueError('current seed differs from historical bytes')
    accepted=re.findall(r'^VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)(?:\s+\[[^\]\n]*\])?\s*$',files['stdout'].read_text(),re.MULTILINE)
    if len(accepted)!=1 or int(accepted[0])!=request['seed_codimension']:
        raise ValueError('historical D4 acceptance missing or codimension differs')
    return dict(schema='semaev.seed-acceptance-reuse/v1',status='historical_acceptance_reused',
        capsule_sha256=sha(capsule_path),seed_sha256=request['seed_sha256'],seed_bytes=request['seed_bytes'],
        accepted_seed_codimension=int(accepted[0]),checker_sha256=sha(checker_path),
        source_provenance=capsule['source_provenance'],evidence=capsule['evidence'],
        scope='Historical independent D4 acceptance, same verified bytes and target; not a fresh check or new bound')
