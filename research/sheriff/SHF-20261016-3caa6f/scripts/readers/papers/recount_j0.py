# Independent recount: j=0 curves y^2=x^3+b over F_p, 5<=p<500, b in 1..p-1, count (ell,p,b) with ell | #E.
def is_prime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True
res={}
for p in range(5,500):
    if not is_prime(p): continue
    # Euler criterion table for squares
    sq=[0]*p
    for y in range(p): sq[y*y%p]+=1
    cubes=[x*x*x%p for x in range(p)]
    for b in range(1,p):
        n=1+sum(sq[(c+b)%p] for c in cubes)
        for ell in (3,5,7):
            if n%ell==0:
                key=(ell,'ord' if p%3==1 else 'ss', 'fails' if p%ell==ell-1 else 'holds')
                res[key]=res.get(key,0)+1
tot=sum(res.values()); ordn=sum(v for k,v in res.items() if k[1]=='ord')
for k in sorted(res): print(k,res[k])
print('total',tot,'ordinary(p=1 mod 3)',ordn,'ordinary & lemma-applies',sum(v for k,v in res.items() if k[1]=='ord' and k[2]=='holds'))
