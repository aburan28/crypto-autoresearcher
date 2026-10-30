"""Certificate replay with explicit polynomial factor identities and triple sums.

Uses supplied published parameters and witnesses, never the searching routines.
This is an independent code path in the same agent/session, not peer review.
"""
import hashlib,itertools,json,sys
from pathlib import Path
from flint import fmpz_mod_poly_ctx
ROOT=Path(__file__).resolve().parent

def point_add(P,Q,p,a):
    if P is None:return Q
    if Q is None:return P
    x,y=P;z,w=Q
    if x==z and (y+w)%p==0:return None
    if P==Q:num,den=3*x*x+a,2*y
    else:num,den=w-y,z-x
    slope=num*pow(den,p-2,p)%p
    X=(slope*slope-x-z)%p
    return (X,(slope*(x-X)-y)%p)

def replay_case(path):
    d=json.loads(path.read_text());q=d['parameters'];p,a,b=q['p'],q['a'],q['b']
    k,c=d['k'],d['terminal_c'];C=fmpz_mod_poly_ctx(p);X=C([0,1]);h=X
    for _ in range(k):h=h*h-2
    h-=c
    radical=(h//h.gcd(h.derivative())).monic();factor=C([1])
    for x in d['domain']:factor*=X-x
    assert factor==radical and len(set(d['domain']))==len(d['domain'])
    if c not in (2,p-2):assert factor==h and factor.degree()==1<<k
    F=[tuple(P) for P in d['signed_base']]
    # Full base membership including exclusions checked without trusting the base.
    expected=[]
    for u in d['domain']:
        x=(d['alpha']*u+d['beta'])%p;v=(x*x*x+a*x+b)%p
        y=pow(v,(p+1)//4,p)
        if y*y%p==v:
            expected.append((x,y))
            if y:expected.append((x,-y%p))
    assert sorted(expected)==F
    for Qdata in d['queries']:
        Q=tuple(Qdata['target']);out=[]
        for i,j,h in itertools.combinations_with_replacement(range(len(F)),3):
            R=point_add(point_add(F[i],F[j],p,a),F[h],p,a)
            if R==Q:out.append([i,j,h])
        assert out==Qdata['complete_signed_decompositions']
    return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'domain_factor_identity':True,'lifted_base_exact':True,
            'exhaustive_signed_triples_per_query':len(F)*(len(F)+1)*(len(F)+2)//6,
            'queries':len(d['queries']),'status':'PASS'}

def main():
    folder=Path(sys.argv[1]);records=[]
    for path in sorted(folder.glob('*-k*.json')):records.append(replay_case(path))
    receipt={'status':'PASS','verifier':'separate code path; same session; no independent review claim',
             'domain_checks':len(records),'complete_query_replays':sum(r['queries'] for r in records),'cases':records}
    (ROOT/'verification-01.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
