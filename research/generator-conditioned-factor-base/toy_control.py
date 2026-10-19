#!/usr/bin/env python3
"""Exact toy control for generator-conditioned factor bases; standard library only.

Enumerates prime-order groups on short-Weierstrass curves over small F_p.
This is an exact 3-sum census, NOT a summation-polynomial solver or ECDLP attack.
"""
from collections import Counter
import json

def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    x,y=P; u,v=Q
    if x==u and (y+v)%p==0: return None
    if P==Q:
        if y%p==0: return None
        s=((3*x*x+a)*pow(2*y,-1,p))%p
    else:
        s=((v-y)*pow((u-x)%p,-1,p))%p
    z=(s*s-x-u)%p
    return (z,(s*(x-z)-y)%p)

def mul(k,P,p,a):
    R=None
    while k:
        if k&1: R=add(R,P,p,a)
        P=add(P,P,p,a); k>>=1
    return R

def prime(n):
    return n>=2 and all(n%d for d in range(2,int(n**.5)+1))

def main():
    for p in (97,101,103,107,109,127,131,137,139,149,157,163,173,179,181,191,193,197,199,211):
        for a in range(p):
            for b in range(p):
                if (4*a*a*a+27*b*b)%p==0: continue
                pts=[(x,y) for x in range(p) for y in range(p)
                     if (y*y-x*x*x-a*x-b)%p==0]
                n=len(pts)+1
                if not prime(n) or n<80: continue
                G=[None]+pts
                F=[P for P in pts if P[0]<max(2,p//5)]
                if len(F)<3: continue
                # Exact ordered triples; signs and repeated points are allowed.
                counts=Counter()
                for A in F:
                    for B in F:
                        AB=add(A,B,p,a)
                        for C in F:
                            counts[add(AB,C,p,a)]+=1
                conditioned=next((R for R in counts if R is not None),None)
                if conditioned is None: continue
                control=next(P for P in pts if P!=conditioned)
                # Prime-order group: every nonidentity point is a generator.
                assert mul(n,conditioned,p,a) is None
                assert mul(n,control,p,a) is None
                # The target distribution is a permutation of G for every generator.
                histograms=[]
                for generator in (conditioned,control):
                    histograms.append(Counter(counts[mul(k,generator,p,a)] for k in range(n)))
                assert histograms[0]==histograms[1]
                print(json.dumps({
                    "p":p,"a":a,"b":b,"group_order":n,"factor_base_size":len(F),
                    "conditioned_generator":conditioned,"control_generator":control,
                    "conditioned_triples":counts[conditioned],
                    "uniform_target_hit_probability":sum(counts[R]>0 for R in G)/n,
                    "exact_histogram_invariant":True,
                    "interpretation":"exact fixed-F control only; no solver timing or ECDLP advantage"
                },sort_keys=True))
                return
    raise RuntimeError("no suitable curve found")

if __name__=="__main__":
    main()
