"""Deterministic public test-input construction; never computes point logs."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from crypto_autoresearcher.index_calculus.curve import is_probable_prime, next_prime

from arithmetic import Elliptic,Field
from relations import uid

HISTORICAL={101:(42,60),211:(127,142),431:(62,120),4099:(4041,4067)}


def describe(p,a,b,base_size):
    if b%p==0 or (4*a*a*a+27*b*b)%p==0:
        return None,{'reason':'singular_or_zero_B','point_tests':0}
    squares=Counter(y*y%p for y in range(p))
    order=1+sum(squares[(x*x*x+a*x+b)%p] for x in range(p))
    trace={'reason':'composite_order','r':order,'point_tests':p}
    if order<=2 or not is_probable_prime(order):
        return None,trace
    f=Field(p);e=Elliptic(f,0,a,b)
    P=next((e_point for x in range(p) if (y:=f.sqrt(e.rhs(x))) is not None
            for e_point in [(x,y)]),None)
    base=[];seen=set();inspected=0
    for x in range(p):
        inspected+=1
        u=x*x%p
        y=f.sqrt((u*u*u+a*u+b)%p)
        if y is None or u in seen:
            continue
        seen.add(u)
        base.append({'point':[u,y],'lift':[x,y]})
        if len(base)==base_size:
            break
    if len(base)!=base_size:
        return None,{**trace,'reason':'insufficient_distinct_factor_base','base_size':len(base)}
    if P is None or e.mul(order,P) is not None:
        raise ArithmeticError('prime-order certificate failed')
    result={'p':p,'a':a,'b':b,'r':order,'P':list(P),'factor_base':base,
            'source_type':'ordinary' if (p+1-order)%p else 'supersingular',
            'field_model':'canonical prime-field integers',
            'curve_family':'y^2=x^6+A*x^2+B; pi1=(x^2,y)',
            'base_rule':'first distinct pi1 norm classes from lexicographic rational C points; no log labels',
            'construction_counts':{'order_point_tests':p,'squares_enumerated':p,
                                   'base_x_inspected':inspected,'field_operations':dict(f.counts)}}
    result['uid']=uid({k:result[k] for k in ['p','a','b','r','P','factor_base']})
    return result,{**trace,'reason':'eligible'}


def witness_fixtures():
    fixtures=[];search=[]
    for p in [101,211,431,4099]:
        found=0
        for a in range(p):
            for b in range(1,p):
                if (a,b)==HISTORICAL[p]:
                    search.append({'p':p,'a':a,'b':b,'reason':'historical_calibration_excluded'})
                    continue
                fixture,trace=describe(p,a,b,8)
                search.append({'p':p,'a':a,'b':b,**trace})
                if fixture is not None:
                    fixtures.append(fixture);found+=1
                    if found==2:
                        break
            if found==2:
                break
        if found!=2:
            raise RuntimeError(f'insufficient W fixture support at p={p}')
    return {'schema':'prym-public-fixtures/v1','purpose':'W prospective immutable public input panel',
            'fixtures':fixtures,'search_trace':search,'secret_labels_present':False}


def recovery_fixtures(config):
    fixtures=[];search=[];used=set()
    for bits in config['subgroup_bits']:
        for index in range(config['instances_per_size']):
            family='j0' if index%2==0 else 'a_minus_3'
            for attempt in range(config['maximum_candidates_per_instance']):
                prefix=f"{config['domain']}|{bits}|{index}|{attempt}"
                h=lambda suffix:int.from_bytes(sha256((prefix+suffix).encode()).digest(),'big')
                p=next_prime((1<<(bits-1))+h('|p')%(1<<(bits-1)))
                if p>=1<<bits or p in used:
                    search.append({'bits':bits,'instance':index,'attempt':attempt,'p':p,
                                   'reason':'field_out_of_band_or_repeated'});continue
                a=0 if family=='j0' else p-3
                b=1+h('|b')%(p-1)
                fixture,trace=describe(p,a,b,config['factor_base_size'])
                search.append({'bits':bits,'instance':index,'attempt':attempt,'p':p,'a':a,'b':b,**trace})
                if fixture is None:
                    continue
                if fixture['r'].bit_length()!=bits or fixture['r']==p:
                    search[-1]['reason']='subgroup_out_of_band_or_anomalous';continue
                fixture.update(subgroup_bits=bits,instance_index=index,family=family)
                fixtures.append(fixture);used.add(p);break
            else:
                raise RuntimeError(f'finite instance search exhausted at bits={bits}, index={index}')
    return {'schema':'prym-public-fixtures/v1','purpose':'E prospective synthetic instance panel',
            'fixtures':fixtures,'search_trace':search,'secret_labels_present':False,
            'source_generation':config,
            'scope':'small analogues of j=0 and a=-3 prime-field families; no deployed-curve inference'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--panel',choices=['witness','recovery'],required=True)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    data=witness_fixtures() if args.panel=='witness' else recovery_fixtures(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:json.dump(data,stream,indent=2);stream.write('\n')
    print(json.dumps({'public_fixtures':len(data['fixtures']),'search_attempts':len(data['search_trace']),
                      'output':str(args.output),'secret_labels_present':False}))


if __name__=='__main__':main()
