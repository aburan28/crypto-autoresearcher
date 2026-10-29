#!/usr/bin/env python3
"""Publish accepted stages of terminal cascades without altering raw attempts."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'semaev-m2-last-fall-degree/submission-20261029'))
from certificate_campaign import digest, save
from publish_certificates import publish


def normalize(args):
    plan_hash = digest(args.plan)
    plan = json.loads(args.plan.read_text())
    planned = {item['id']: item for item in plan['items']}
    count = 0
    for path in sorted(args.run_root.glob('*/attempt-*/result.json')):
        result = json.loads(path.read_text())
        if result['plan_sha256'] != plan_hash or result['parameters'] != planned[result['id']]:
            raise ValueError('Result is not bound to the requested frozen plan')
        for name, entry in result['artifacts'].items():
            source = path.parent/name
            if source.stat().st_size != entry['bytes'] or digest(source) != entry['sha256']:
                raise ValueError('Raw artifact changed: '+str(source))
        for stage in result['stages']:
            degree = stage['degree']
            label = f'check{degree}'
            if result['steps'][label]['returncode'] or result['steps']['count']['returncode']:
                raise ValueError('Stage lacks successful checker and counter')
            cert = path.parent/f'degree{degree}.bin'
            if digest(cert) != stage['certificate_sha256']:
                raise ValueError('Accepted-stage certificate hash mismatch')
            transcript = (path.parent/(label+'.stdout.txt')).read_text()
            expected = rf'VALID: 1 is not in W_{degree}\(F\), and codim W_{degree}\(F\) >= (\d+)'
            match = re.search(expected, transcript)
            if not match or int(match[1]) != stage['certified_codimension']:
                raise ValueError('Checker transcript does not match accepted stage')
            if stage['exact_solutions'] != result['exact_solutions']:
                raise ValueError('Stage count mismatch')
            name = result['id']+f'-D{degree}'
            target = args.normalized_root/name/path.parent.name
            completed = target/'result.json'
            origin = dict(schema='semaev.cascade-publication-origin/v1',
                original_result=str(path.resolve()), original_result_sha256=digest(path),
                original_stage=stage, note='Publication-format projection of a retained accepted stage; no new scientific run.')
            if completed.exists():
                old = json.loads((target/'origin.json').read_text())
                if old != origin:
                    raise ValueError('Publication identity already refers to different evidence')
                count += 1
                continue
            target.mkdir(parents=True, exist_ok=True)
            sources = {p.name:p for p in path.parent.iterdir() if p.is_file() and p.suffix!='.bin' and p.name!='result.json'}
            sources.update({'cascade-result.json':path, 'check.stdout.txt':path.parent/(label+'.stdout.txt'),
                'check.stderr.txt':path.parent/(label+'.stderr.txt'), 'certificate.bin':cert})
            for filename, source in sources.items():
                dest = target/filename
                if dest.exists():
                    if digest(dest) != digest(source):
                        raise ValueError('Partial publication snapshot differs from source')
                elif filename=='certificate.bin':
                    # Both locations are in the retained data volume. Never modify either link.
                    try:
                        os.link(source, dest)
                    except OSError:
                        shutil.copyfile(source, dest)
                else:
                    shutil.copyfile(source, dest)
            if (target/'origin.json').exists():
                if json.loads((target/'origin.json').read_text()) != origin:
                    raise ValueError('Partial publication origin differs from source')
            else:
                save(target/'origin.json', origin)
            record = dict(result['parameters']['record'], name=name)
            projected = dict(schema='semaev.cascade-stage-publication/v1', id=name,
                status='certificate_verified', parameters=dict(chain=False,degree=degree,record=record),
                certificate_sha256=stage['certificate_sha256'],
                certified_codimension_lower_bound=stage['certified_codimension'],
                exact_solutions=stage['exact_solutions'], source_commit=result['source_commit'],
                plan_sha256=plan_hash, provenance=origin,
                last_fall_degree_lower_bound=degree+1 if stage['certified_codimension']>stage['exact_solutions'] else None,
                artifacts={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in target.iterdir() if p.is_file()})
            save(completed, projected)
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('plan','run-root','normalized-root','archive','repo-root'):
        ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--repo',default='isogeny-labs/crypto-autoresearcher')
    ap.add_argument('--tag',default='semaev-closure-certificates-20261029')
    ap.add_argument('--normalize-only',action='store_true')
    args = ap.parse_args()
    args.normalized_root.mkdir(parents=True,exist_ok=True)
    # A single adapter owns this view, independently of the science driver's lock.
    import fcntl
    with open(args.normalized_root/'normalization.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        count = normalize(args)
        print(json.dumps(dict(normalized_accepted_stages=count)),flush=True)
        if args.normalize_only or not count:
            return
        args.run_roots=[args.normalized_root]
        args.store='s3://setec-astronomy-artifacts/store'
        args.region='us-east-2'
        args.python=sys.executable
        publish(args)


if __name__=='__main__':
    main()
