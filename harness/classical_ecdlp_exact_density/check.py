#!/usr/bin/env python3
"""Fail-closed strict JSON, source, payload, complete-stream and integer checks.

This is the producer's structural checker. Independent mathematical validation
remains a separate required step; it never labels a run scientifically valid.
"""
import argparse
import base64
from collections import Counter
import hashlib
from math import comb
from pathlib import Path
import sys

from driver import (HERE,SOURCES,RUNTIME_SOURCES,MEMBERS,STATUSES,PRIMARY,CELLS,strict,sha,canon,
                    same_sources,summary_rows,verify_payloads,open_binary,open_logical,digest_size)

def need(condition,reason):
    if not condition: raise ValueError(reason)

def check_snapshot(snap,expected,include_binary=False):
    need(set(snap['files'])==set((*SOURCES,*RUNTIME_SOURCES))|({'census.bin'} if include_binary else set()),'source snapshot closure')
    for n,item in snap['files'].items():
        data=base64.b64decode(item['base64'],validate=True)
        need(len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],'source bytes/hash: '+n)
        need(item['sha256']==expected[n],'executed source mismatch: '+n)

def validate(out,repo=None):
    out=Path(out); repo=Path(repo) if repo else HERE.parents[1]
    __import__('driver').RUNTIME_REPO=repo
    envelope=strict(out/'manifest.yaml'); need(set(envelope)=={'run'},'manifest envelope')
    body=envelope['run']; raw=strict(out/'raw-result.json'); bundle=strict(out/'export.json');export=bundle['backend_record']
    need(bundle['schema']=='experiment.export/v1' and bundle['flow']==dict(planned=1,attempted=1,completed=1,not_completed=0,interrupted=0,resumed=0,excluded=[]),'unified export flow')
    need(raw['schema']=='classical.ecdlp.exact-density.result/v1','raw schema')
    need(raw['status']=='complete' and raw['attack_claimed'] is False and raw['metrics']=={'complete':True},'incomplete or claimed attack')
    need(export['schema']=='exact-density.export-seal/v1' and export['status']=='complete','export schema/status')
    need(raw['export_sha256']==sha(out/'export.json')==body['exact_density']['export_sha256'],'export seal mismatch')
    need(body['exact_density']['raw_result_sha256']==sha(out/'raw-result.json'),'raw seal mismatch')
    need(body['status']=='completed' and body['attack_claimed'] is False and body['result']['certificate']['kind']=='none','manifest status/claim')
    need(set(export['members'])==set(MEMBERS),'missing/extra export member')
    for name,binding in export['members'].items():
        p=out/name; need(not p.is_symlink(),'missing/unsafe member: '+name)
        need(digest_size(p)==(binding['sha256'],binding['bytes']),'member hash/size: '+name)
    expected_files=[dict(path=n,sha256=b['sha256'],bytes=b['bytes'],kind='raw') for n,b in export['members'].items()]
    need(bundle['files']==expected_files and len(bundle['runs'])==1 and bundle['runs'][0]['artifacts']==expected_files and bundle['runs'][0]['status']=='succeeded' and bundle['runs'][0]['measurements']['wall_valid'] is False,'unified export files/status')
    need(bundle['host']['sha256']==sha(out/'process.json.gz'),'unified host seal')
    source_hashes={**{n:sha(HERE/n) for n in SOURCES},**{n:sha(repo/n) for n in RUNTIME_SOURCES}}
    need(export['source_sha256']==source_hashes,'source changed')
    sm=strict(HERE/'source-manifest.json')
    need(set(sm['sources'])==set(SOURCES)-{'source-manifest.json'},'manifest no-cycle closure')
    for n,b in sm['sources'].items(): need(b==dict(bytes=(HERE/n).stat().st_size,sha256=sha(HERE/n)),'pinned source mismatch: '+n)
    need(set(sm['runtime_sources'])==set(RUNTIME_SOURCES),'runtime closure')
    for n,b in sm['runtime_sources'].items():need(digest_size(repo/n)==(b['sha256'],b['bytes']),'runtime source mismatch: '+n)
    expected=source_hashes|{'census.bin':sha(out/'census.bin')}
    before=strict(out/'provenance.before.json.gz'); after=strict(out/'provenance.after.json.gz')
    check_snapshot(before,expected);check_snapshot(after,expected,True)
    proc=strict(out/'process.json.gz')
    need(proc['returncode'] is None and proc['termination']=='pending_outer_supervisor_exit' and proc['computation_status']=='complete' and proc['source_unchanged'] is True,'abnormal driver termination')
    need(proc['compiler']['returncode']==0 and proc['compiler']['executable'],'compiler provenance')
    for event in proc['children']:
        need(event['returncode']==0 and event['signal'] is None and event['sources_unchanged'] is True,'abnormal child/source termination')
        check_snapshot(event['source_before'],expected,'census.bin' in event['source_before']['files'])
        check_snapshot(event['source_after'],expected,'census.bin' in event['source_after']['files'])
        data=base64.b64decode(event['stdin_base64'],validate=True)
        need(hashlib.sha256(data).hexdigest()==event['stdin_sha256'],'invocation input hash')
    need(proc['children'][0]['argv'][-2]=='-o' and Path(proc['children'][0]['argv'][-1]).name=='census.bin','compiled binary destination')
    partial=strict(out/'partial.json'); need(partial['status']=='complete' and partial['missing_data'] is None,'partial output')
    summary=strict(out/'summary.json.gz'); need(summary['status']=='complete' and summary['wall_valid'] is False,'summary completeness/clock')
    need(raw['summary_sha256']==sha(out/'summary.json.gz'),'summary seal')
    inputs=strict(out/'inputs.json'); mode=raw['mode'];need(mode==inputs['mode']==partial['mode'],'mode mismatch')
    if mode=='fixtures':
        from driver import FIXTURE
        curves=[FIXTURE|dict(curve_id=FIXTURE['curve_id']+'/'+o) for o in inputs['oracle_variants']]
        need(strict(out/'controls.json')['status']=='complete','missing fixed controls')
    else:
        curves=inputs['curves']
        payload=strict(out/'payload-verification.json')
        actual=verify_payloads(repo,[x['path'] for x in payload['verified'] if x['kind']!='storage_metadata'])
        need(actual==payload,'input inventory mismatch')
        need(len(curves)==48 and len({c['curve_id'] for c in curves})==48 and sum(c['model']['r']-1 for c in curves)==821638,'frozen curve coverage')
    if mode=='regression':
        need(strict(out/'regression.json.gz')['status']=='complete' and summary['rows']==summary['curves']==[],'retained regression incomplete')
        with open_logical(out/'states.jsonl.gz') as f:need(f.read()==b'','unexpected census states in regression')
        expected_children=1
    else:
        recomputed=[]; bindings=[]; total_states=0; prep=[]
        with open_logical(out/'census.stdout.log') as refs:stdout_refs=[__import__('json').loads(line) for line in refs]
        need(len(stdout_refs)==len(curves),'native stdout references coverage')
        with open_logical(out/'preparations.jsonl.gz') as f:
            for line in f: prep.append(__import__('json').loads(line,object_pairs_hook=__import__('driver').unique))
        need(len(prep)==len(curves),'preparation coverage')
        with open_logical(out/'states.jsonl.gz') as f:
            for ci,curve in enumerate(curves):
                r=curve['model']['r']; L=r.bit_length()+1; D=1<<L
                p=prep[ci]
                need(p['curve_index']==ci and p['curve_id']==curve['curve_id'] and p['model']==curve['model'] and p['base']==curve['base'] and p['arm']==PRIMARY,'wrong curve/base/arm')
                need(p['orbit_points']==r and p['identity_count']==1 and len(p['labels'])==r and set(p['labels'])<=set('01u'),'orbit label coverage')
                event=proc['children'][ci+1]
                data=base64.b64decode(event['stdin_base64']).decode().split()
                need(data[:3]==[str(r),str(L),str(ci)] and data[3:]==[str(-1 if b=='u' else int(b)) for b in p['labels']],'native input/label mismatch')
                records=[]; h=hashlib.sha256()
                for s in range(1,r):
                    line=f.readline(); need(bool(line),'partial scalar stream')
                    row=__import__('json').loads(line);need(canon(row).encode()+b'\n'==line,'noncanonical stream')
                    need(len(row)==7 and row[0]==ci and row[1]==s,'wrong/missing/duplicate scalar')
                    _,_,V,mask,e,hd,cells=row
                    need(all(type(n) is int for n in (V,mask,e,hd)) and 0<=V<D and 0<=mask<D and V&mask==0 and e==mask.bit_count() and 0<=hd<=L-e,'state representation')
                    need(len(cells)==6,'cell coverage')
                    # Reconstruct trace from paid labels, including exact doubling indices.
                    u=s; word=emask=distance=0
                    for i in range(L):
                        b=p['labels'][u]; shift=L-1-i
                        if b=='u': emask|=1<<shift
                        else: word|=int(b)<<shift;distance+=int(b)!=int(u>r//2)
                        u=2*u%r
                    need((V,mask,hd)==(word,emask,distance),'trace index/bit/mask mismatch')
                    for j,(t,ec) in enumerate(CELLS):
                        c=cells[j];need(len(c)==14 and all(type(n) is int and n>=0 for n in c),'cell representation')
                        status,w,legal,empty,zero,M,hit,tt,tf,ot,of,w0,w1,w2=c
                        capped=e>ec; expected=0 if capped else (1<<e)*sum(comb(L-e,jj) for jj in range(min(t,L-e)+1))
                        need(status<len(STATUSES) and w==expected and legal+empty==w and tt+tf==ot+of==legal and tt==ot==hit and tf==of and hit in (0,1) and zero in (0,1) and M==legal-zero and M<=r-1 and w0+w1+w2==w,'cell count geometry')
                        need(zero==int(not capped and V.bit_count()<=t),'zero check omitted/included in M')
                        true_word=D*s//r
                        need(hit==int(not capped and ((true_word^V)&~mask).bit_count()<=t),'both public equations/success mismatch')
                        expected_status=1 if j==0 and e else 4 if capped else 0 if hit else 2 if w and legal==0 else 3
                        need(status==expected_status,'status/cap/strict override')
                        need(w0==(0 if capped else 1<<e) and w1==(0 if capped or t<1 else (1<<e)*(L-e)) and w2==(0 if capped or t<2 else (1<<e)*comb(L-e,2)),'completion weight counts')
                    h.update(line);records.append(row[1:]);total_states+=1
                recomputed.extend(summary_rows([curve],[records]))
                need(event['stdout_sha256']==h.hexdigest() and event['stdout_lines']==r-1,'exact native stdout binding')
                need(stdout_refs[ci]==dict(curve_index=ci,curve_id=curve['curve_id'],artifact='states.jsonl.gz',compressed_start=event['stdout_stored_start'],compressed_end=event['stdout_stored_end'],uncompressed_bytes=event['stdout_bytes'],lines=event['stdout_lines'],sha256=event['stdout_sha256']),'native stdout exact references')
                bindings.append(dict(curve_id=curve['curve_id'],curve_index=ci,states=r-1,sha256=h.hexdigest()))
            need(f.read()==b'','extra scalar stream')
        need(summary['rows']==recomputed and summary['curves']==bindings,'integer summaries/histograms/curve seals')
        need(len(summary['rows'])==len(curves)*6,'curve/cell summary coverage')
        need(partial['completed_curves']==len(curves),'incomplete curve count')
        expected_children=1+len(curves)
    need(len(proc['children'])==expected_children,'invocation coverage')
    return dict(status='complete_output_checked',mode=mode,scientific_validity='not_assessed',attack_claimed=False,export_sha256=sha(out/'export.json'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--repo');a=p.parse_args()
    print(canon(validate(Path(a.out),Path(a.repo) if a.repo else None)));return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,TypeError) as e:
        print('exact-density check refused: '+str(e),file=sys.stderr);sys.exit(1)
