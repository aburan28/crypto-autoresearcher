"""Admitted, prospectively matched direct enumeration and pair-table panel."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter, process_time

import core
from check import check
from common import SOURCES, PARAMETERS
from crypto_autoresearcher.index_calculus.execution_gate import admit


def write_once(path,value):
    with path.open('x') as stream: json.dump(value,stream,indent=2);stream.write('\n')


def phase(path,cell,arm,name,operation):
    wall,cpu=perf_counter(),process_time();record=dict(cell_id=cell['id'],arm=arm,phase=name,started_at=datetime.now(timezone.utc).isoformat(),status='complete',wall_valid=False)
    try: return operation()
    except BaseException as error:
        record.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:
        record.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu)
        with path.open('a') as stream: stream.write(json.dumps(record,sort_keys=True)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists(): raise ValueError('fresh native output required')
    if core.PARAMETERS!=PARAMETERS: raise ValueError('native/admin parameter mismatch')
    admission=admit(core.ROOT,args.protocol,args.inputs,SOURCES,PARAMETERS,args.release)
    data=json.loads(args.inputs.read_text())
    if len(data['cells'])!=2 or {c['id'] for c in data['cells']}!={'b13','b16'} or data['arms']!=PARAMETERS['arms']:
        raise ValueError('both original cells required')
    args.out.mkdir(parents=True);write_once(args.out/'admission.json',admission)
    for cell in data['cells']:
        f=cell['fixture']
        if f['p']!=4099 or len(f['factor_base'])!=16 or len(cell['source_order'])!=64: raise ValueError('wrong fixed panel')
        events=args.out/(cell['id']+'.events.jsonl'); meters=[]
        result=dict(schema='direct-three-sum-cell/v1',cell_id=cell['id'],curve_uid=f['uid'],
                    inputs_sha256=sha256(args.inputs.read_bytes()).hexdigest(),complete=True,arms=[])
        try:
            with events.open('x') as stream:
                def event(record): stream.write(json.dumps(record,sort_keys=True)+'\n');stream.flush()
                for name in PARAMETERS['arms']:
                    value,meter=phase(args.out/'phases.jsonl',cell,name,'collection',lambda name=name:core.collect(cell,name,event,capability=core._NATIVE_CAPABILITY))
                    result['arms'].append(value);meters.append(meter)
            write_once(args.out/(cell['id']+'.collection.json'),result)
            for value,meter in zip(result['arms'],meters,strict=True):
                value['analysis']=phase(args.out/'phases.jsonl',cell,value['arm'],'analysis',lambda value=value,meter=meter:core.analyze(cell,value,meter))
            write_once(args.out/(cell['id']+'.json'),result)
            verification=phase(args.out/'phases.jsonl',cell,None,'verification',lambda:check(cell,result))
            write_once(args.out/(cell['id']+'.verification.json'),verification)
        except BaseException as error:
            with events.open('a') as stream: stream.write(json.dumps(dict(kind='failure',error_type=type(error).__name__,error=str(error),complete=False))+'\n')
            raise
    print(json.dumps(dict(complete=True,curves=2,arm_records=4,physical_panels=1)))


if __name__=='__main__': main()
