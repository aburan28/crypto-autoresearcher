#!/usr/bin/env python3
"""Candidate retained-seed worker with chunked provisional-map custody."""
import argparse
import hashlib
import json
from math import comb
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import zlib

from run_lift_worker_durable import placement, sha, save
from checkpoint_export_guard import work_bytes
from publish_lift_checkpoint import inspect_snapshot


def disk_admit(root, policy, additional):
    used = work_bytes(root)
    free = shutil.disk_usage(root).free
    available = min(policy['capacity_bytes']-used, free)-policy['reserve_bytes']
    if additional > available:
        raise ValueError(f'disk admission refused: need {additional}, available {available}')
    return dict(accounted_bytes=used,filesystem_free_bytes=free,
                additional_bytes=additional,reserve_bytes=policy['reserve_bytes'])


def stream_seed(request, bundle, output):
    """Bound output bytes and hash both compressed and decoded streams, no gzip file."""
    expected = request['seed_bytes']; total = 0; decoded = hashlib.sha256()
    compressed = hashlib.sha256(); compressed_count = 0
    decoder = zlib.decompressobj(16+zlib.MAX_WBITS) if 'seed_url' in request else None
    source = urllib.request.urlopen(request['seed_url'], timeout=120) if decoder else (bundle/request['seed_file']).open('rb')
    with source, output.open('xb') as dest:
        while True:
            block = source.read(1 << 20)
            if not block:break
            if decoder:
                compressed_count += len(block)
                if compressed_count > request['seed_gzip_bytes']:raise ValueError('compressed seed exceeds frozen size')
                compressed.update(block)
            pending = block
            while pending:
                data = decoder.decompress(pending, 1 << 20) if decoder else pending
                pending = decoder.unconsumed_tail if decoder else b''
                total += len(data)
                if total > expected:raise ValueError('seed exceeds frozen size')
                decoded.update(data);dest.write(data)
                if decoder and decoder.unused_data:raise ValueError('trailing or concatenated gzip stream')
        if decoder and (not decoder.eof or decoder.unused_data):raise ValueError('incomplete gzip seed')
        if total != expected or decoded.hexdigest()!=request['seed_sha256']:raise ValueError('seed size/hash mismatch')
        if decoder and (compressed_count!=request['seed_gzip_bytes'] or compressed.hexdigest()!=request['seed_gzip_sha256']):
            raise ValueError('compressed seed size/hash mismatch')
        dest.flush();os.fsync(dest.fileno())


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--request',type=Path,required=True)
    ap.add_argument('--protocol',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--upload',action='store_true');ap.add_argument('--restore-prefix')
    ap.add_argument('--restore-map-only',action='store_true')
    ap.add_argument('--control-source',action='store_true',help='Frozen qualification only: stop after requested saves')
    ap.add_argument('--checkpoint-prefix',help='Local controls only: fake object-store prefix')
    a=ap.parse_args();a.bundle=a.bundle.resolve();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=False)
    req=json.loads(a.request.read_text());protocol=json.loads(a.protocol.read_text())
    if protocol['freeze']['status']!='frozen' or sha(a.request) not in protocol['links']['request_sha256s']:
        raise ValueError('request does not match frozen protocol')
    if sha(a.bundle/'manifest.json')!=req['worker_manifest_sha256']:raise ValueError('manifest mismatch')
    manifest=json.loads((a.bundle/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        path=(a.bundle/name).resolve()
        if not path.is_relative_to(a.bundle) or sha(path)!=digest:raise ValueError('bundle mismatch: '+name)
    if sha(Path(__file__))!=manifest['files']['run_lift_worker_mapcache.py']:raise ValueError('worker source mismatch')
    policy=req['disk_policy'];root=Path(policy['work_root']).resolve(strict=True)
    if not a.out.is_relative_to(root) or not a.bundle.is_relative_to(root):raise ValueError('runtime outside accounted root')
    if a.out/'certificate.bin' != root/policy['certificate_relative_path']:raise ValueError('certificate path mismatch')
    work=policy['working_coordinates'];maximum_snapshot=208+work*((work+63)//64)*8
    if maximum_snapshot>5_000_000_000:raise ValueError('checkpoint exceeds single-PUT interface')
    maximum_map_chunk=9*8+64+min(65536,comb(policy['N'],5))*((work+63)//64)*8+32
    if maximum_map_chunk>maximum_snapshot or maximum_map_chunk>5_000_000_000:
        raise ValueError('map chunk exceeds phase disk or single-PUT envelope')
    if policy['reserve_bytes'] < 16<<20:raise ValueError('insufficient supervisor/log reserve')
    if req['seed_bytes']!=32+8*sum(comb(policy['N'],d) for d in range(policy['degree']))*(1+(req['seed_codimension']+63)//64):
        raise ValueError('seed size disagrees with frozen dimensions')
    if policy['N']!=2*len(req['record']['V_basis_hex']) or policy['degree']!=5:raise ValueError('unsupported target dimensions')
    target=os.environ['ISOLAB_RESULTS_URI'].rstrip('/')+'/lift/' if a.upload else None
    if a.upload and a.checkpoint_prefix:raise ValueError('cloud checkpoint destination must use assigned run prefix')
    prefix=target+'checkpoints' if target else a.checkpoint_prefix
    if not prefix:raise ValueError('checkpoint destination missing')
    map_prefix=req['map_cache_prefix']
    if not re.fullmatch(r's3://[a-z0-9][a-z0-9.-]+/checkpoints/[a-zA-Z0-9._/-]+',map_prefix):
        raise ValueError('invalid frozen map cache prefix')
    if a.restore_map_only and a.restore_prefix:raise ValueError('choose one restore mode')
    snapshots=a.out/'snapshots';snapshots.mkdir()
    map_chunks=a.out/'map-chunks';map_chunks.mkdir()
    context=dict(request_sha256=sha(a.request),protocol_sha256=protocol['freeze']['protocol_sha256'],
                 seed_sha256=req['seed_sha256'],binary_sha256=sha(a.bundle/'bin/quotient_lift_checkpoint'))
    save(a.out/'context.json',context);save(a.out/'request.json',req)
    result=dict(id=req['id'],status='started',steps={},scope='Exact checked computation only; no timing or upper-bound inference')
    env={k:v for k,v in os.environ.items()
         if not k.startswith('SEMAEV_CHECKPOINT_') and not k.startswith('SEMAEV_MAP_')}
    env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',LD_LIBRARY_PATH=str(a.bundle/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH',''),
        SEMAEV_CHECKPOINT_REQUEST=str(a.request.resolve()),SEMAEV_CHECKPOINT_CONTEXT=str(a.out/'context.json'),
        SEMAEV_CHECKPOINT_DIR=str(snapshots),SEMAEV_CHECKPOINT_S3_PREFIX=prefix,
        SEMAEV_CHECKPOINT_PRUNE_LOCAL='1',SEMAEV_CHECKPOINT_PUBLISH=str(a.bundle/'checkpoint_export_guard.py'),
        SEMAEV_MAP_DIR=str(map_chunks),SEMAEV_MAP_CHUNK_ROWS='65536',
        SEMAEV_MAP_PUBLISH=str(a.bundle/'map_chunk_store.py'),
        SEMAEV_MAP_FETCH=str(a.bundle/'map_chunk_store.py'),
        SEMAEV_MAP_PRUNE_LOCAL='1',SEMAEV_MAP_S3_PREFIX=map_prefix)
    if a.restore_prefix or a.restore_map_only:env['SEMAEV_MAP_RESTORE']='1'
    def publish(path):
        if target:subprocess.run(['aws','s3','cp',str(path),target+str(path.relative_to(a.out)),'--only-show-errors'],check=True,timeout=1200)
    def record(name,data):
        path=a.out/name;save(path,data);publish(path)
    def run(label,argv,cap,extra=None):
        def limits():resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
        argv=list(map(str,argv));record(label+'.started.json',dict(argv=argv,memory_bytes=cap,unix_time=time.time()))
        start=time.monotonic();child=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            preexec_fn=limits,start_new_session=True,env=dict(env,**(extra or {})))
        counts={};errors=[]
        def drain(stream,path,key):
            try:
                total=0
                with path.open('xb') as out:
                    while True:
                        block=stream.read(65536)
                        if not block:break
                        if total < 1<<20:out.write(block[:(1<<20)-total])
                        total+=len(block)
                counts[key]=total
            except BaseException as error:errors.append(repr(error))
            finally:stream.close()
        threads=[threading.Thread(target=drain,args=(stream,a.out/(label+'.'+key+'.txt'),key)) for stream,key in [(child.stdout,'stdout'),(child.stderr,'stderr')]]
        for t in threads:t.start()
        timeout=False
        try:child.wait(timeout=req['stage_timeout_seconds'])
        except subprocess.TimeoutExpired:
            timeout=True;os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        for t in threads:t.join()
        step=dict(returncode=child.returncode,timeout=timeout,stream_bytes=counts,log_errors=errors,
                  elapsed_seconds=time.monotonic()-start,wall_valid=False)
        result['steps'][label]=step
        for key in ['stdout','stderr']:publish(a.out/(label+'.'+key+'.txt'))
        record(label+'.finished.json',step)
        if timeout or errors:raise RuntimeError(label+' incomplete')
        return child.returncode,(a.out/(label+'.stdout.txt')).read_text()
    def checked(label,argv,cap):
        code,text=run(label,argv,cap)
        if code:raise RuntimeError(label+' failed')
        return text
    def check(label,cert,degree):
        r=req['record'];text=checked(label,[sys.executable,a.bundle/'cert_check.py',cert,r['n'],r['modulus_hex'],r['a2'],r['a6_hex'],r['z_hex'],*r['V_basis_hex']],req['memory_bytes'])
        match=re.search(r'VALID: 1 is not in W_'+str(degree)+r'\(F\), and codim W_'+str(degree)+r'\(F\) >= (\d+)',text)
        if not match:raise ValueError('original checker acceptance missing')
        return int(match[1])
    try:
        record('environment.json',dict(cgroup=placement(req,a.upload),context=context))
        if a.restore_map_only:
            high=comb(policy['N'],5);start=max(0,high-65536)
            code,_=run('map-probe',[a.bundle/'map_chunk_store.py','probe',start,high],1<<30)
            if code:raise ValueError('map-only restore unavailable; fresh restart forbidden')
        # Before either download, reserve both a possible restore and the next
        # maximum snapshot. Existing bundle/archive/request files are counted.
        record('startup-disk.json',disk_admit(root,policy,req['seed_bytes']+2*maximum_snapshot))
        seed=a.out/'seed.bin';stream_seed(req,a.bundle,seed)
        record('seed-transfer.json',dict(bytes=seed.stat().st_size,sha256=sha(seed)))
        codim=check('check4',seed,4)
        if codim!=req['seed_codimension']:raise ValueError('seed codimension mismatch')
        r=req['record'];count=int(checked('count',[a.bundle/'bin/count_by_sum',r['n'],r['modulus_hex'],r['z_hex'],r['a6_hex'],len(r['V_basis_hex']),*r['V_basis_hex']],1<<30).strip())
        if count!=req['expected_exact_solutions']:raise ValueError('fresh exact count mismatch')
        result.update(seed_codimension=codim,exact_solutions=count)
        restore=None
        if a.restore_prefix:
            receipt=a.out/'restore.json';code,_=run('restore',[sys.executable,a.bundle/'restore_lift_checkpoint.py','--prefix',a.restore_prefix,'--context',a.out/'context.json','--out',snapshots,'--receipt',receipt],1<<30)
            if receipt.exists():publish(receipt)
            if code:raise ValueError('requested restore unavailable; fresh restart forbidden')
            restore=json.loads(receipt.read_text());path=Path(restore['local_path']);meta=inspect_snapshot(path)
            if meta!=restore['snapshot'] or meta['chunk_rows']!=req['chunk_rows']:raise ValueError('restore metadata mismatch')
            env['SEMAEV_CHECKPOINT_RESTORE']=str(path)
            code,_=run('restore-admission',[sys.executable,a.bundle/'checkpoint_export_guard.py','--restore',path],1<<30)
            if code==73:result['status']='export_deferred'
            elif code:raise ValueError('restore admission failed')
        if result['status']!='export_deferred':
            phase=restore['snapshot']['phase'] if restore else None
            record('prelaunch-disk.json',disk_admit(root,policy,0 if phase==2 else maximum_snapshot))
            if a.control_source:
                if not req.get('checkpoint_stop_after') or a.restore_prefix:raise ValueError('control stop not authorized')
                env['SEMAEV_CHECKPOINT_STOP_AFTER']=str(req['checkpoint_stop_after'])
            cert=a.out/'certificate.bin'
            code,text=run('produce5',[a.bundle/'bin/quotient_lift_checkpoint',seed,cert,req['chunk_rows'],req['memory_bytes']],req['memory_bytes'])
            decisions=list(a.out.glob('export-admission-*.json'))
            deferred=[p for p in decisions if json.loads(p.read_text())['status']=='export_deferred']
            if code==2 and deferred and not cert.exists():result['status']='export_deferred'
            elif code==75 and a.control_source:result['status']='checkpointed_control'
            elif code:raise RuntimeError('produce5 failed')
            else:
                produced=json.loads(text)
                if produced['status']=='projection_kills_one':result['status']='projection_kills_one'
                elif produced['status']=='candidate_certificate':
                    codim=check('check5',cert,5)
                    result.update(status='certificate_verified',certified_codimension_lower_bound=codim,certificate_sha256=sha(cert))
                    publish(cert)
                    if codim>count:result['last_fall_degree_lower_bound']=6
                else:raise ValueError('unknown producer result')
    except Exception as error:result.update(status='failed',error=str(error))
    for path in sorted(a.out.glob('export-admission-*.json')):publish(path)
    result['checkpoint_prefix']=prefix
    result['map_cache_prefix']=map_prefix
    for path in sorted(map_chunks.glob('*.publication.json')):publish(path)
    record('result.json',result);print(json.dumps(result),flush=True)
    return 1 if result['status']=='failed' else 0


if __name__=='__main__':raise SystemExit(main())
