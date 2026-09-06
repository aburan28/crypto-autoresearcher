#!/usr/bin/env python3
"""Independent point count of a short-Weierstrass curve over F_p (p < 2^25) via Legendre symbols (numpy QR table)."""
import numpy as np, sys, json
def count(p,a,b):
    x=np.arange(p,dtype=np.int64)
    qr=np.zeros(p,dtype=bool); qr[(x*x)%p]=True
    rhs=(x*x%p*x%p + a*x + b)%p
    chi=np.where(rhs==0,0,np.where(qr[rhs],1,-1))
    return int(1+p+chi.sum())
def is_prime(n):
    if n<2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%q==0: return n==q
    d=n-1; s=0
    while d%2==0: d//=2; s+=1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x=pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1: break
        else: return False
    return True
for spec in sys.argv[1:]:
    p,a,b,N=map(int,spec.split(','))
    n=count(p,a,b)
    print(json.dumps({'p':p,'a':a,'b':b,'claimed_N':N,'counted_N':n,'match':n==N,'p_prime':is_prime(p),'N_prime':is_prime(N),'disc_nonzero':(4*a**3+27*b**2)%p!=0}))
