"""Replay retained basis certificates with separate sparse modular division.

This code does not call SymPy or its polynomial reduction routines. It checks
original reductions, all critical pairs, all retained exact points, and a finite
standard-monomial count, including the nontrivial 56-point membership algebra.
"""
import gzip,hashlib,itertools,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=2**256-2**224+2**192+2**96-1

def monorder(m):return (sum(m),)+tuple(-x for x in reversed(m))
def loadpoly(rows):return {tuple(m):int(c)%p for m,c in rows if int(c)%p}
def plus(a,b):return tuple(x+y for x,y in zip(a,b))
def difference(a,b):return tuple(x-y for x,y in zip(a,b))
def divides(a,b):return all(x<=y for x,y in zip(a,b))
def shift_scaled(f,m,c):return {plus(t,m):a*c%p for t,a in f.items() if a*c%p}
def merge(f,g,scale=1):
    out=f.copy()
    for m,c in g.items():
        out[m]=(out.get(m,0)+scale*c)%p
        if not out[m]:del out[m]
    return out

def normal(f,G,leads):
    f=f.copy();out={}
    while f:
        lead=max(f,key=monorder);c=f[lead]
        for g,m in zip(G,leads):
            if divides(m,lead):
                f=merge(f,shift_scaled(g,difference(lead,m),c),-1);break
        else:out[lead]=f.pop(lead)
    return out

def value(f,point):
    total=0
    for m,c in f.items():
        v=c
        for x,e in zip(point,m):v=v*pow(x,e,p)%p
        total=(total+v)%p
    return total

def read(path):
    if path.exists():raw=path.read_bytes()
    else:raw=gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())
    return raw,json.loads(raw)

def main():
    checks=[]
    for folder in ['attempts-01','attempts-02']:
        receiptpath=ROOT/folder/'receipt.json'
        if not receiptpath.exists():continue
        for r in json.loads(receiptpath.read_text()):
            if r['status']!='PASS':continue
            path=ROOT/folder/(r['label']+'.json');raw,d=read(path)
            assert hashlib.sha256(raw).hexdigest()==r['result_sha256']
            inputs=list(map(loadpoly,d['equations']));G=list(map(loadpoly,d['groebner_basis']))
            leads=[]
            for i,g in enumerate(G):
                lead=max(g,key=monorder);inv=pow(g[lead],-1,p)
                G[i]={m:c*inv%p for m,c in g.items()};leads.append(lead)
            assert all(not normal(f,G,leads) for f in inputs)
            count=0
            for i,j in itertools.combinations(range(len(G)),2):
                lcm=tuple(max(x,y) for x,y in zip(leads[i],leads[j]))
                s=merge(shift_scaled(G[i],difference(lcm,leads[i]),1),
                        shift_scaled(G[j],difference(lcm,leads[j]),1),-1)
                assert not normal(s,G,leads);count+=1
            pts=d['complete_stratum_points']
            assert all(value(f,pt)==0 for f in G for pt in pts)
            n=len(leads[0]);std=[]
            if not any(not any(m) for m in leads):
                bounds=[min(m[j] for m in leads if m[j] and all(m[i]==0 for i in range(n) if i!=j)) for j in range(n)]
                std=[m for m in itertools.product(*(range(b) for b in bounds))
                     if not any(divides(t,m) for t in leads)]
            assert len(std)==len(pts)==d['certificate']['standard_monomial_count']
            checks.append({'file':str(path.relative_to(ROOT)),'status':'PASS','critical_pairs':count,
                           'points':len(pts),'quotient_dimension':len(std)})
    out={'status':'PASS','verifier':'independent sparse polynomial arithmetic; same session, not peer review',
         'basis_certificates_replayed':len(checks),'checks':checks}
    (ROOT/'basis-replay-01.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'PASS','basis_certificates_replayed':len(checks),
                     'critical_pairs_checked':sum(r['critical_pairs'] for r in checks)}),flush=True)

if __name__=='__main__':main()
