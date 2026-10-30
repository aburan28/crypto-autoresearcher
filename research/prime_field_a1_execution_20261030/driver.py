"""Admitted fixed residual-pool census, shared nested arms and full separate replay."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter,process_time

import core
from check import check
from common import SOURCES,PARAMETERS
from crypto_autoresearcher.index_calculus.execution_gate import admit


def write_once(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')


def phase(path,cell,arm,name,operation):
    wall,cpu=perf_counter(),process_time();record=dict(cell_id=cell['id'],arm=arm,phase=name,started_at=datetime.now(timezone.utc).isoformat(),status='complete',wall_valid=False)
    try:return operation()
    except BaseException as error:
        record.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:
        record.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu)
        with path.open('a') as f:f.write(json.dumps(record,sort_keys=True)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise ValueError('fresh native output required')
    if PARAMETERS!=core.PARAMETERS:raise ValueError('administrative/native parameters differ')
    admission=admit(core.ROOT,a.protocol,a.inputs,SOURCES,PARAMETERS,a.release)
    data=json.loads(a.inputs.read_text())
    if (len(data['cells'])!=2 or {c['id'] for c in data['cells']}!={'b13','b16'} or data['pool_prefixes']!=PARAMETERS['pool_prefixes']):
        raise ValueError('complete fixed two-curve panel required')
    a.out.mkdir(parents=True);write_once(a.out/'admission.json',admission)
    for cell in data['cells']:
        f=cell['fixture']
        if f['p']!=4099 or len(f['factor_base'])!=16 or len(cell['source_order'])!=64 or cell['pool_curve_uid']!=f['ec1']['curve_uid']:
            raise ValueError('wrong fixed curve/base/source identity')
        events=a.out/(cell['id']+'.events.jsonl')
        try:
            with events.open('x') as stream:
                def event(record):stream.write(json.dumps(record,sort_keys=True)+'\n');stream.flush()
                pool=phase(a.out/'phases.jsonl',cell,None,'pool_generation',lambda:core.generate_pool(cell,data['pool_recipe'],event,capability=core._NATIVE_CAPABILITY))
                event(dict(kind='pool_complete',pool=pool))
                result=phase(a.out/'phases.jsonl',cell,None,'collection',lambda:core.collect(cell,pool,event,capability=core._NATIVE_CAPABILITY))
            result['inputs_sha256']=sha256(a.inputs.read_bytes()).hexdigest()
            write_once(a.out/(cell['id']+'.collection.json'),result)
            for prefix in PARAMETERS['pool_prefixes']:
                arm='smooth' if prefix==0 else 'pool'+str(prefix)
                result['arms'].append(phase(a.out/'phases.jsonl',cell,arm,'elimination',lambda prefix=prefix:core.analyze_arm(cell,result,prefix)))
            write_once(a.out/(cell['id']+'.json'),result)
            verification=phase(a.out/'phases.jsonl',cell,None,'verification',lambda:check(cell,result,data['pool_recipe']))
            write_once(a.out/(cell['id']+'.verification.json'),verification)
        except BaseException as error:
            with events.open('a') as stream:stream.write(json.dumps(dict(kind='failure',error_type=type(error).__name__,error=str(error),complete=False))+'\n')
            raise
    print(json.dumps(dict(complete=True,curves=2,nested_arm_records=6,physical_panels=1)))


if __name__=='__main__':main()
