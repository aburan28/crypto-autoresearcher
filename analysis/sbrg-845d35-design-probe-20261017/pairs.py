import sys,time,random
sys.path.insert(0,'.')
exec(open('scan.py').read().split("t=time.time(); ref=[]")[0])   # reuse setup (builds NF, c1, solve, Nz, sat)
unsat=[z for z in range(1<<n) if z not in sat]
random.seed(7)
ncol=M.ncol
cc=c1|(c1<<ncol)
res=[]
for _ in range(int(sys.argv[5])):
    z,w=random.sample(unsat,2)
    Nz1,Nz2=Nz(z),Nz(w)
    cat=[a|(b<<ncol) for a,b in zip(Nz1,Nz2)]
    t=time.time(); lam,kern=solve(cat,cc)
    res.append(lam is not None)
    print('pair',z,w,'share',lam is not None,'cat-kernel dim',len(kern),round(time.time()-t,1),'s',flush=True)
print('shared',sum(res),'of',len(res))
