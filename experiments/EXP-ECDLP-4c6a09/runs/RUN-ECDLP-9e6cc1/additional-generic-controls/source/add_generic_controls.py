#!/usr/bin/env python3
"""Fill only missing predeclared generic table sizes; preserve all prior controls."""
import hashlib
import json
import math
import shutil
from collections import Counter
from pathlib import Path

from benchmark import scalar_table, measured
from finite_math import Curve
from shared_relations import solve_batch
from gp_tables import write

RUN=Path(__file__).resolve().parent.parent

def main():
    stage=RUN/'additional-generic-controls'
    stage.mkdir(exist_ok=False)
    (stage/'source').mkdir()
    for name in ['add_generic_controls.py','benchmark.py','finite_math.py','shared_relations.py']:
        shutil.copy2(RUN/'source'/name,stage/'source'/name)
    write(stage/'launch.json',{'command_argv':['python3',str(Path(__file__).resolve())],
                              'addendum_sha256':hashlib.sha256((RUN/'generic-controls-addendum.json').read_bytes()).hexdigest(),
                              'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (stage/'source').iterdir()}})
    prior=json.loads((RUN/'inputs/prior-shared-result.json').read_text())['methods']
    groups=json.loads((RUN/'inputs/prior-cold-result.json').read_text())['public_groups']
    targets=json.loads((RUN/'inputs/targets-public.json').read_text())
    truth={t['id']:t['synthetic_scalar'] for t in json.loads((RUN/'inputs/synthetic-truth.json').read_text()) if 'synthetic_scalar' in t}
    methods=[]
    for public in groups:
        a,b,k,ell=public['A'],public['B'],public['k'],public['ell']
        inherited={m['table_entries_requested'] for m in prior if m['arm'].startswith('bsgs') and (m['A'],m['B'],m['k'])==(a,b,k)}
        sizes={9,81,729,6561,math.isqrt(ell)+(math.isqrt(ell)**2<ell)}
        for size in sorted(sizes-inherited):
            ec=Curve(public['p'],a,b)
            built,timing=measured(lambda:scalar_table(ec,tuple(public['G']),size,ell))
            ts=[t for t in targets if t['curve_uid']==public['identity']['curve_uid']]
            solved=solve_batch(public,[tuple(public['G'])],{0:1},built,ts,size,32768)
            for r in solved['targets']:
                if r['resolved_at_batch_end']:assert r['recovered_scalar']==truth[r['target_id']]
            total=Counter(ec.count)+Counter(solved['query_operations'])
            r={'id':f'bsgs_matched-a{a}-b{b}-k{k}-M{size}','arm':'bsgs_matched',
               'A':a,'B':b,'k':k,'p':public['p'],'ell':ell,'cofactor':public['cofactor'],
               'curve_uid':public['identity']['curve_uid'],'curve_id':public['identity']['curve_id'],
               'table_entries_requested':size,'distinct_subgroup_points':len(built['table']),
               'seed_count':1,'unknown_seed_count':0,'target_count':16,
               'target_recoveries':sum(t['resolved_at_batch_end'] for t in solved['targets']),
               'total_algorithm_operations':dict(total),'table_build_operations':dict(ec.count),
               'table_build_timing':timing,'batch_result':solved,
               'useful_relations_per_1000_group_calls':solved['global_relation_rank']*1000/max(1,total['group_calls']),
               'recoveries_per_1000_group_calls':sum(t['resolved_at_batch_end'] for t in solved['targets'])*1000/max(1,total['group_calls'])}
            methods.append(r)
            print('BSGS',r['id'],'recovered',r['target_recoveries'],'calls',total['group_calls'],flush=True)
    write(stage/'raw-result.json',{'methods':methods,'policy':'Only missing sizes; inherited controls retained unchanged'})

if __name__=='__main__':main()
