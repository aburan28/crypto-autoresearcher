#!/usr/bin/env python3
"""Independent bit-score replay, complete rare-frame inventory, integer EC oracle."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
import numpy as np
from metrics import scores_from_packed
from oracle import add, affine_draw, multiply, scalar_draw
from research import check_record, jobs_for, model_for, put_json


def frames(path,cohorts,width):
    size=28+width+cohorts*256*2*width
    with Path(path).open('rb') as handle:
        while True:
            block=handle.read(size)
            if not block:break
            if len(block)!=size:raise ValueError('Truncated coordinate frame')
            index,sc,gc,flags=struct.unpack('<QQQI',block[:28]);r=int.from_bytes(block[28:28+width],'big')
            values=[int.from_bytes(block[i:i+width],'big') for i in range(28+width,size,width)]
            points=[[tuple(values[(c*256+j)*2:(c*256+j)*2+2]) for j in range(256)] for c in range(cohorts)]
            yield index,sc,gc,flags,r,points


def verify_job(run,job,model,record):
    check_record(run,record);directory=Path(run)/'artifacts'/job['id'];count=job['count'];cohorts=3 if job['named'] else 1
    curve=model['curve'] if job['named'] else {k:model[k] for k in ('p','A','B','N')};p=curve['p'];width=(p.bit_length()+7)//8
    bits=np.fromfile(directory/'bits.bin',dtype=np.uint8).reshape(count,cohorts,32)
    scores=np.fromfile(directory/'scores.bin',dtype='<u4').reshape(count,cohorts,3)
    if not np.array_equal(scores_from_packed(bits),scores):raise ValueError('Independent bit-score mismatch')
    metric=model['metric_index'] if job['named'] else 0;threshold=model['threshold_integer'] if job['named'] else 22
    flags=np.sum((scores[:,:,metric]>=threshold).astype(np.uint32)*(1<<np.arange(cohorts,dtype=np.uint32)),axis=1)
    wanted_events=set(np.flatnonzero(flags));wanted_witness={i for i in (0,1,count//2,count-1) if 0<=i<count}
    invocation=json.loads((directory/'invocation.json').read_text());starts=bytes.fromhex(invocation['start_seed']);generators=bytes.fromhex(invocation['generator_seed'])
    public=np.fromfile(directory/'public-scalars.bin',dtype=np.uint8).reshape(count,width) if job['named'] else None
    checked=set();frame_count=coordinate_count=transitions=starts_checked=scalar_checks=relations=0
    for filename,wanted in (('events.frames',wanted_events),('witness.frames',wanted_witness)):
        seen=set()
        for index,sc,gc,frameflags,r,points in frames(directory/filename,cohorts,width):
            frame_count+=1
            if index not in wanted or index in seen or frameflags!=int(flags[index]):raise ValueError('Rare/witness inventory mismatch')
            seen.add(index)
            if index in checked:continue
            checked.add(index)
            if job['named']:
                k,_=scalar_draw(starts,curve['N'],sc);expected=multiply(curve,tuple(model['published_G']),k)
                expected_r,_=scalar_draw(generators,curve['N'],gc)
                if r!=expected_r or r!=int.from_bytes(public[index].tobytes(),'big'):raise ValueError('Public generator scalar mismatch')
                steps=[tuple(model['G']),tuple(model['published_G']),multiply(curve,tuple(model['published_G']),r)];scalar_checks+=2
            else:
                expected,_=affine_draw(curve,starts,sc);steps=[tuple(model['G'])]
                if r or gc:raise ValueError('Unexpected ordinary generator scalar')
            if any(arm[0]!=expected for arm in points):raise ValueError('Independent uniform-start or paired-start mismatch')
            starts_checked+=1
            for c,arm in enumerate(points):
                bit_values=np.zeros(256,dtype=np.uint8)
                for j,(x,y) in enumerate(arm):
                    if not (0<=x<p and 0<=y<p and (y*y-x*x*x-curve['A']*x-curve['B'])%p==0):raise ValueError('Independent equation mismatch')
                    coordinate_count+=1;bit_values[j]=(x>>64)&1
                    if j and add(curve,arm[j-1],steps[c])!=(x,y):raise ValueError('Independent affine recurrence mismatch')
                    if j:transitions+=1
                    if j>=2:
                        L=arm[j-2][0];X=arm[j-1][0];R=x;u=steps[c][0]
                        if ((L+R)*(X-u)**2-2*((X*u+curve['A'])*(X+u)+2*curve['B']))%p:raise ValueError('Universal triple law mismatch')
                        relations+=1
                if not np.array_equal(np.packbits(bit_values,bitorder='little'),bits[index,c]):raise ValueError('Raw coordinate/bit mismatch')
        if seen!=wanted:raise ValueError('Missing rare or witness frame')
    if record['online_oncurve_checks']!=count*cohorts*256:raise ValueError('Online check count mismatch')
    if record['selected_metric_event_counts']!=np.sum(scores[:,:,metric]>=threshold,axis=0).tolist():raise ValueError('Rare count mismatch')
    return {'windows_with_all_scores_replayed':count*cohorts,'rare_frame_count':len(wanted_events),
            'frame_records':frame_count,'independent_coordinate_checks':coordinate_count,
            'independent_affine_transitions':transitions,'independent_starts':starts_checked,
            'independent_scalar_multiplications':scalar_checks,'universal_relation_checks':relations,
            'online_oncurve_checks':record['online_oncurve_checks']}


def verify(run):
    run=Path(run);design=json.loads((run/'design.json').read_text());inputs=design['inputs'];config=design['config']
    jobs=jobs_for(inputs,config);totals={};rows=[]
    expected={f"{j['id']}.json" for j in jobs}
    if {p.name for p in (run/'records').glob('*.json')}!=expected:raise ValueError('Missing/extra job record')
    for i,job in enumerate(jobs):
        record=json.loads((run/'records'/f"{job['id']}.json").read_text());result=verify_job(run,job,model_for(inputs,job),record)
        rows.append({'job':job['id'],**result})
        for key,value in result.items():totals[key]=totals.get(key,0)+value
        if (i+1)%16==0:print(json.dumps({'verified_jobs':i+1,'requested_jobs':len(jobs)}),flush=True)
    result={'schema':1,'validity':'passed stated checks','totals':totals,'jobs':rows,
        'independence':'Separate Python integer affine arithmetic, SHA-counter draws and bit-feature reconstruction. Same session, not a separate research reviewer.',
        'scope':'Every stored bit string and score checked; every rare and witness frame checked against equations and recurrence. Full transient coordinate hashes recorded, not fully replayed in compact mode.'}
    put_json(run/'verification.json',result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);args=parser.parse_args()
    print(json.dumps(verify(args.run)['totals'],sort_keys=True))
