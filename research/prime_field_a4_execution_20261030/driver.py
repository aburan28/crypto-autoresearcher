"""Admit before any holdout/target generation, retain collections before recovery."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter,process_time
import core
from check import check,check_generation
from common import SOURCES,PARAMETERS
from crypto_autoresearcher.index_calculus.execution_gate import admit


def write(path,value):
    with path.open('x') as stream: json.dump(value,stream,indent=2);stream.write('\n')


def phase(path,cell,name,operation):
    wall,cpu=perf_counter(),process_time();record=dict(cell_id=cell,phase=name,started_at=datetime.now(timezone.utc).isoformat(),status='complete',wall_valid=False)
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
    if core.PARAMETERS!=PARAMETERS: raise ValueError('native/admin parameters differ')
    admission=admit(core.ROOT,args.protocol,args.inputs,SOURCES,PARAMETERS,args.release)
    rules=json.loads(args.inputs.read_text());args.out.mkdir(parents=True);write(args.out/'admission.json',admission)
    with (args.out/'generation.events.jsonl').open('x') as stream:
        def event(v): stream.write(json.dumps(v,sort_keys=True)+'\n');stream.flush()
        generated=phase(args.out/'phases.jsonl',None,'generation',lambda:core.generate(rules,event,capability=core._NATIVE_CAPABILITY))
    generated['inputs_sha256']=sha256(args.inputs.read_bytes()).hexdigest();write(args.out/'generated.json',generated)
    write(args.out/'generation.verification.json',phase(args.out/'phases.jsonl',None,'generation_check',lambda:check_generation(rules,generated)))
    for cell in generated['cells']:
        events=args.out/(cell['id']+'.events.jsonl')
        try:
            with events.open('x') as stream:
                def event(v): stream.write(json.dumps(v,sort_keys=True)+'\n');stream.flush()
                result,meter=phase(args.out/'phases.jsonl',cell['id'],'collection',lambda:core.collect(cell,rules,event,capability=core._NATIVE_CAPABILITY))
            result.update(cell_id=cell['id'],inputs_sha256=sha256(args.inputs.read_bytes()).hexdigest())
            write(args.out/(cell['id']+'.collection.json'),result)
            for count in rules['prefixes']:
                result['prefixes'].append(phase(args.out/'phases.jsonl',cell['id'],'prefix'+str(count),lambda count=count:core.prefix_analysis(cell,rules,result,meter,count)))
            result['total_counters']=meter.counters();write(args.out/(cell['id']+'.json'),result)
            write(args.out/(cell['id']+'.verification.json'),phase(args.out/'phases.jsonl',cell['id'],'check',lambda:check(cell,rules,result)))
        except BaseException as error:
            with events.open('a') as stream: stream.write(json.dumps(dict(kind='failure',error_type=type(error).__name__,error=str(error),complete=False))+'\n')
            raise
    print(json.dumps(dict(complete=True,curves=len(generated['cells']),prefix_records=len(generated['cells'])*len(rules['prefixes']),physical_panels=1)))


if __name__=='__main__': main()
