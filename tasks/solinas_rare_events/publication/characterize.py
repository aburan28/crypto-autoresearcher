#!/usr/bin/env python3
"""Descriptive retained-window characterization; no new trial or test."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research import jobs_for,put_json
from verify import frames
from oracle import scalar_draw


def characterize(run,output):
    run=Path(run);design=json.loads((run/'design.json').read_text())
    model=next(c for c in design['inputs']['candidates'] if c['metric_index']==0)
    maximum=[0,0,0];examples=[]
    for job in jobs_for(design['inputs'],design['config']):
        if job['model']!=model['id']:continue
        directory=run/'artifacts'/job['id'];scores=np.fromfile(directory/'scores.bin',dtype='<u4').reshape(job['count'],3,3)
        maximum=[max(maximum[c],int(scores[:,c,0].max())) for c in range(3)]
        selected=set(np.flatnonzero(scores[:,0,0]>=32))
        if not selected:continue
        invocation=json.loads((directory/'invocation.json').read_text())
        bits=np.fromfile(directory/'bits.bin',dtype=np.uint8).reshape(job['count'],3,32)
        for index,sc,gc,flags,r,points in frames(directory/'events.frames',3,28):
            if index not in selected:continue
            seq=np.unpackbits(bits[index,0],bitorder='little').tolist();runs=[];start=0
            for end in range(1,257):
                if end==256 or seq[end]!=seq[start]:
                    if end-start>=32:runs.append({'offset':start,'length':end-start,'bit':seq[start]})
                    start=end
            k,_=scalar_draw(bytes.fromhex(invocation['start_seed']),model['curve']['N'],sc)
            examples.append({'job':job['id'],'local_window':index,'global_window':job['offset']+index,'run_segments':runs,
                'scores_by_cohort':scores[index].tolist(),'same_uniform_start_Q':points[0][0],'public_start_k':k,'public_random_generator_r':r,
                'selected_bit_sequence':''.join(map(str,seq)),'events_frame_file':str(directory/'events.frames'),
                'frame_file_sha256':hashlib.sha256((directory/'events.frames').read_bytes()).hexdigest()})
    record={'schema':1,'scope':'Post-sampling descriptive characterization of the predeclared >=32 tail; no new significance test, sample, or family redefinition.',
        'candidate':model['id'],'max_observed_longrun_by_selected_published_random':maximum,'examples':examples,
        'interpretation':'A single extreme observed window is preserved; compare the fixed tail-spectrum confidence intervals before inferring a generator effect.'}
    put_json(output,record);return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(characterize(args.run,args.output),sort_keys=True))
