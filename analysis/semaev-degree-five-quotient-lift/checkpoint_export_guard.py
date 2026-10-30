#!/usr/bin/env python3
"""Candidate export admission hook; requires separate qualification before use.

Hook: checkpoint_export_guard.py SNAPSHOT
Restore prelaunch: checkpoint_export_guard.py --restore SNAPSHOT
Both require SEMAEV_CHECKPOINT_REQUEST and SEMAEV_CHECKPOINT_CONTEXT. The
request's hashed disk_policy fixes dimensions, capacity, reserve and paths.
Exit73 means export deferred; it is never mathematical evidence.
"""
import hashlib
import json
from math import comb
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

from publish_lift_checkpoint import inspect_snapshot


def load_policy():
    request_path = Path(os.environ['SEMAEV_CHECKPOINT_REQUEST'])
    data = request_path.read_bytes()
    context = json.loads(Path(os.environ['SEMAEV_CHECKPOINT_CONTEXT']).read_text())
    if hashlib.sha256(data).hexdigest() != context['request_sha256']:
        raise ValueError('export policy request differs from checkpoint context')
    policy = json.loads(data)['disk_policy']
    for name in ('N','degree','working_coordinates','capacity_bytes','reserve_bytes'):
        if type(policy[name]) is not int or policy[name] < 0:
            raise ValueError('invalid integer policy field: '+name)
    if not (0 < policy['N'] <= 63 and 0 < policy['degree'] <= policy['N']):
        raise ValueError('invalid export dimensions')
    if not (0 < policy['working_coordinates'] and policy['capacity_bytes'] > policy['reserve_bytes']):
        raise ValueError('invalid export capacity')
    root = Path(policy['work_root']).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('work root is not a directory')
    relative = Path(policy['certificate_relative_path'])
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('certificate path escapes work root')
    output = root/relative
    if not output.parent.resolve(strict=True).is_relative_to(root):
        raise ValueError('certificate parent escapes work root')
    if output.exists() or output.is_symlink():
        raise ValueError('certificate output already exists')
    return policy, context, root, output


def check_identity(snapshot, metadata, policy, context):
    with snapshot.open('rb') as f:
        header = struct.unpack('<4Q',f.read(32))
    if header[2:] != (policy['N'],policy['degree']):
        raise ValueError('snapshot dimensions differ from export policy')
    if metadata['working_coordinates'] != policy['working_coordinates']:
        raise ValueError('snapshot coordinate count differs from policy')
    for key in ('seed_sha256','binary_sha256'):
        if metadata[key] != context[key]:
            raise ValueError('snapshot identity differs from context')


def certificate_size(n, degree, work, rank):
    if not 0 <= rank < work:
        raise ValueError('no positive export codimension')
    columns = sum(comb(n,d) for d in range(degree+1))
    return 32 + 8*columns + 8*columns*((work-rank+63)//64)


def work_bytes(root):
    total = 0
    for directory, directories, files in os.walk(root,followlinks=False):
        for name in directories+files:
            path = Path(directory)/name
            if path.is_symlink():
                raise ValueError('symlink in accounted work directory')
        for name in files:
            total += (Path(directory)/name).stat().st_size
    return total


def admit(metadata, policy, root, output, mode):
    if metadata['phase'] != 2:
        return 0
    needed = certificate_size(policy['N'],policy['degree'],metadata['working_coordinates'],metadata['relation_rank'])
    used = work_bytes(root)
    free = shutil.disk_usage(root).free
    # Reserve the decision file itself even when a test policy sets its other
    # overhead reserve to zero. Serialize and bound that file before writing.
    decision_reserve = 65536
    allowed = min(policy['capacity_bytes']-used-policy['reserve_bytes']-decision_reserve,
                  free-policy['reserve_bytes']-decision_reserve)
    decision = dict(schema='semaev.export-admission/v1',
        status='allowed' if needed <= allowed else 'export_deferred', mode=mode,
        snapshot=metadata, certificate_path=str(output), certificate_bytes=needed,
        accounted_work_bytes=used, observed_filesystem_free_bytes=free,
        declared_capacity_bytes=policy['capacity_bytes'],reserve_bytes=policy['reserve_bytes'],
        decision_reserve_bytes=decision_reserve,
        admitted_output_limit_bytes=allowed,
        scope='Observed disk admission only; no certificate acceptance or LFD inference')
    path = output.parent/('export-admission-'+mode+'-'+str(metadata['sequence'])+'.json')
    data = (json.dumps(decision,indent=2,sort_keys=True)+'\n').encode()
    if len(data)>decision_reserve:
        raise ValueError('export decision exceeds reserved bytes')
    with path.open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    fd = os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    print(json.dumps(decision),file=sys.stderr,flush=True)
    return 0 if decision['status']=='allowed' else 73


def main():
    restore = len(sys.argv)==3 and sys.argv[1]=='--restore'
    if not restore and len(sys.argv)!=2:
        raise ValueError('usage: checkpoint_export_guard.py [--restore] SNAPSHOT')
    snapshot = Path(sys.argv[-1]).resolve(strict=True)
    policy,context,root,output = load_policy()
    if not snapshot.is_relative_to(root):
        raise ValueError('snapshot outside accounted work directory')
    # Verify before any mutation. The existing publisher independently verifies
    # the same immutable bytes and performs complete S3 readbacks.
    metadata = inspect_snapshot(snapshot)
    check_identity(snapshot,metadata,policy,context)
    if restore:
        # Phase2 restoration skips the native publication hook; this call is
        # mandatory in the worker before launching that restored child.
        return admit(metadata,policy,root,output,'restored')
    if os.environ.get('SEMAEV_CHECKPOINT_PRUNE_LOCAL')!='1':
        raise ValueError('frontier hook requires verified local pruning')
    publisher = Path(__file__).with_name('publish_lift_checkpoint.py')
    result = subprocess.run([sys.executable,str(publisher),str(snapshot)],stdout=subprocess.PIPE,check=True)
    if result.stdout:
        raise ValueError('publisher contaminated native stdout')
    ack = json.loads(snapshot.with_suffix('.publication.json').read_text())
    if ack['snapshot'] != metadata or snapshot.exists():
        raise ValueError('verified publication/pruning acknowledgment mismatch')
    # Any refusal happens after the completed state is durable. Retain old
    # restore files; their footprint is included in admission.
    return admit(metadata,policy,root,output,'fresh')


if __name__=='__main__':
    raise SystemExit(main())
