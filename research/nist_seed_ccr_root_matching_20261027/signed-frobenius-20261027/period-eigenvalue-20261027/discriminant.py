"""Muller1995 source-route check via exact Frobenius discriminant square classes."""
import json,math,pathlib
P=pathlib.Path(__file__).resolve().parent
def primes():
    n=3
    while True:
        if all(n%d for d in range(3,math.isqrt(n)+1,2)):yield n
        n+=2
def first_phase(p,m):
    for ell in primes():
        m*=ell
        if m*m>=16*p:return ell,m
def flags(p,n):
    t=p+1-n;k=4*p-t*t
    if p<=3 or k<=0:raise ValueError('source input outside ordinary prime-field Hasse range')
    if t==0:return [1,0,0]
    def sqdiv(d):return int(k%d==0 and math.isqrt(k//d)**2==k//d)
    return [0,sqdiv(3),sqdiv(4)]
def count(p,a,b):return 1+sum(sum((y*y-x*x*x-a*x-b)%p==0 for y in range(p)) for x in range(p))
def valid_small(p,a,b,n):return (4*a**3+27*b*b)%p!=0 and count(p,a,b)==n
def controls():
    fixtures=json.loads((P/'CONTROLS.json').read_text())
    for c in fixtures:
        p,a,b,n=[c[k] for k in ['p','A','b','n']]
        assert valid_small(p,a,b,n)
        assert flags(p,n)==c['expected']
        assert flags(p,n)==flags(p,n)
        if 'generic' in c['name']:
            j=1728*4*a**3*pow(4*a**3+27*b*b,-1,p)%p
            assert j not in (0,1728%p)
    assert not valid_small(5,0,0,6)
    assert not valid_small(5,4,1,7)
def main():
    controls()
    for i,r in enumerate(json.loads((P/'INPUTS.json').read_text())['rows']):
        p,n=int(r['p']),int(r['n']);t=p+1-n
        s1,m1=first_phase(p,1);s2,m2=first_phase(p,2)
        print(json.dumps([i,p,n,t,4*p-t*t]+flags(p,n)+[s1,m1,s2,m2]),flush=True)
if __name__=='__main__':main()
