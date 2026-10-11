"""One pinned worker; exact arithmetic output checks precede timed comparisons."""
import argparse, hashlib, json, os, platform, random, time
from pathlib import Path
from common import Stream, sqrt_mod, write
from finite_math import Curve
from curve_identity import curve_identity


class FoldCurve(Curve):
    def __init__(self,p,a,b):
        super().__init__(p,a,b);self.bits=p.bit_length();self.mask=(1<<self.bits)-1;self.replacement=(1<<self.bits)-p
    def reduce(self,value):
        if value<0:return -self.reduce(-value)%self.p
        while value>>self.bits:value=(value&self.mask)+(value>>self.bits)*self.replacement
        return value-self.p if value>=self.p else value
    def mult_field(self,a,b):
        self.count['field_multiplications']+=1;return self.reduce(a*b)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prep',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);moduli=json.loads((a.prep/'prime-sample.json').read_text())['moduli']
    cpus=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpus[0]});random.Random(2026101187).shuffle(moduli)
    observations=[];identities=[];started=time.monotonic()
    for m in moduli:
        p=m['p'];row=json.loads((a.prep/'curves'/m['id']/'curves.json').read_text())['curves'][0]
        rng=Stream('nist-arithmetic/2026101187/'+m['id']);products=[(rng.below(p),rng.below(p))for _ in range(256)]
        invs=[1+rng.below(p-1)for _ in range(64)];G=None
        for attempt in range(20000):
            x=rng.below(p);y=sqrt_mod((x**3+row['A']*x+row['B'])%p,p)
            if y is not None:G=(x,y);break
        if G is None:raise RuntimeError('arithmetic point limit')
        generic=Curve(p,row['A'],row['B']);fold=FoldCurve(p,row['A'],row['B']);point=None;points=[]
        for i in range(131):points.append(point);point=generic.add(point,G)
        pairs=list(zip(points[:128],points[3:131]));expected={'products':[x*y%p for x,y in products],
          'inversions':[pow(x,-1,p)for x in invs],'point_additions':[generic.add(x,y)for x,y in pairs]}
        assert [fold.reduce(x*y)for x,y in products]==expected['products']and [fold.add(x,y)for x,y in pairs]==expected['point_additions']
        schedule=[(backend,rep,work)for backend in (['builtin','fold']if m['arm']=='S'else['builtin'])for rep in range(5)for work in expected]
        random.Random('nist-arith-order/'+m['id']).shuffle(schedule)
        for backend,rep,work in schedule:
            begin=time.process_time();wall=time.perf_counter()
            if work=='products':actual=[x*y%p for x,y in products]if backend=='builtin'else[fold.reduce(x*y)for x,y in products]
            elif work=='inversions':actual=[pow(x,-1,p)for x in invs]
            else:
                ec=generic if backend=='builtin'else fold;actual=[ec.add(x,y)for x,y in pairs]
            elapsed=time.process_time()-begin;wall=time.perf_counter()-wall;assert actual==expected[work]
            observations.append({'modulus_id':m['id'],'case':m['case'],'arm':m['arm'],'backend':backend,'workload':work,'batch':rep,
                'operations':len(actual),'cpu_seconds':elapsed,'wall_seconds':wall,'seconds_per_operation':elapsed/len(actual),'outputs_exactly_equal':True})
        field={'characteristic':p,'degree':1,'representation':'prime field, canonical integer residues','element_encoding':'integers 0..p-1','modulus':p}
        cm={'model':'short-Weierstrass','a4':row['A'],'a6':row['B'],'subgroup_order':row['N'],'cofactor':1,
            'generator':{'point':list(G),'role':'arithmetic seed only; point order unresolved; not claimed generator'},'target_group':'E(F_p), full group; supplied point not asserted generator'}
        identities.append({'modulus_id':m['id'],'field':field,'curve':cm,'identity':curve_identity(field,cm,'nistarithmetic')})
        write(out/(m['id']+'-inputs.json'),{'modulus':m,'A':row['A'],'B':row['B'],'products':products,'inversions':invs,'point_pairs':pairs,'expected_output_SHA256':hashlib.sha256(json.dumps(expected,separators=(',',':')).encode()).hexdigest()})
        if len(identities)%48==0:print('ARITHMETIC',len(identities),'/',len(moduli),flush=True)
    write(out/'observations.json',observations);write(out/'curve-identities.json',identities)
    write(out/'arithmetic-result.json',{'complete':True,'moduli':len(moduli),'observations':len(observations),'all_outputs_exactly_equal':True,
          'elapsed_seconds':time.monotonic()-started,'CPU':cpus[0],'python':platform.python_version(),'scope':'Python prototypes; inversions same built-in pow in both backends; intervals conditional on fixed S median, control-field variation only'})

if __name__=='__main__':main()
