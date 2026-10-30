"""Admit and retain every fixed matched subset-cover collector cell."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter,process_time

import core
from check import check
from crypto_autoresearcher.index_calculus.execution_gate import admit


def write_once(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def phase(path,cell,arm,name,operation):
    started=datetime.now(timezone.utc).isoformat();wall,cpu=perf_counter(),process_time()
    record=dict(cell_id=cell['id'],arm=arm,phase=name,started_at=started,status='complete',wall_valid=False)
    try:return operation()
    except BaseException as error:
        record.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:
        record.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu)
        with path.open('a') as stream:stream.write(json.dumps(record,sort_keys=True)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise ValueError('fresh native output directory required')
    root=core.ROOT;here=Path(__file__).resolve().parent
    admission=admit(root,args.protocol,args.inputs,[here/name for name in ('driver.py','core.py','check.py')]+[
        core.OLD/name for name in ('relations.py','arithmetic.py','independent.py')]+[
        root/'research/prym_factor_base_width_20261025/collect_width.py',
        root/'research/prym_factor_base_width_20261025/check_inputs.py',
        root/'src/crypto_autoresearcher/index_calculus/curve.py',
        root/'src/crypto_autoresearcher/index_calculus/cover_frames.py',
        root/'src/crypto_autoresearcher/index_calculus/relation_quality.py'],core.PARAMETERS,args.release)
    inputs=json.loads(args.inputs.read_text())
    if len(inputs['cells'])!=5 or len({cell['id'] for cell in inputs['cells']})!=5:raise ValueError('all five fixed candidates required')
    args.out.mkdir(parents=True);write_once(args.out/'admission.json',admission)
    for cell in inputs['cells']:
        if Path(cell['id']).name!=cell['id'] or cell['fixture']['p']!=4099 or len(cell['fixture']['factor_base'])!=16 or len(cell['source_order'])!=64:
            raise ValueError('wrong fixed cell identity')
        for arm,h in [('baseline',0),('shifted',cell['shift'])]:
            stem=cell['id']+'-'+arm
            with (args.out/(stem+'.events.jsonl')).open('x') as stream:
                def event(record):stream.write(json.dumps(record,sort_keys=True)+'\n');stream.flush()
                try:result=phase(args.out/'phases.jsonl',cell,arm,'collection',lambda:core.collect(cell,h,arm,event,capability=core._NATIVE_CAPABILITY))
                except BaseException as error:
                    event(dict(kind='failure',error_type=type(error).__name__,error=str(error),complete=False));raise
            result['inputs_sha256']=sha256(args.inputs.read_bytes()).hexdigest()
            write_once(args.out/(stem+'.json'),result)
            verification=phase(args.out/'phases.jsonl',cell,arm,'verification',lambda:check(cell,h,arm,result))
            write_once(args.out/(stem+'.verification.json'),verification)
    print(json.dumps(dict(complete=True,cells=10)))


if __name__=='__main__':main()
