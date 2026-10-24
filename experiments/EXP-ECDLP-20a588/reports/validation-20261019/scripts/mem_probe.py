#!/usr/bin/env python3
"""Validator memory probe (informational): rebuild the launcher's msolve input for (m=3,L,inst,arm) and run msolve exactly
as block_order_grid.run_ms does, but via os.wait4 to record ru_maxrss (peak RSS of the msolve process)."""
import importlib.util, hashlib, random, json, os, sys, time, subprocess, resource, re
HERE="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588"
spec=importlib.util.spec_from_file_location("bog",HERE+"/block_order_grid.py"); bog=importlib.util.module_from_spec(spec); spec.loader.exec_module(bog)
msg,pkm=bog.msg,bog.pkm
L,inst,arm=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]; m=3
plan=json.load(open(HERE+"/trial-plan.json"))
kind="planted" if inst<plan["planted_per_cell"] else "random"
seed=int(hashlib.sha256(f"{plan['seed']}|{m}|{L}|{inst}".encode()).hexdigest()[:12],16)
rng=random.Random(seed); p=pkm.find_prime(m,L); a=p-3
while True:
    b=rng.randrange(1,p)
    if (4*a**3+27*b*b)%p: break
chain=pkm.build_chain(p,L,rng); rng.sample(range(p),2**L)
fb=pkm.factor_base(chain["V"],a,b,p); trng=random.Random(f"{seed}-False-target")
if kind=="planted":
    picks=[trng.choice(fb) for _ in range(m)]; picks=[P if trng.random()<.5 else pkm.ec_neg(P,p) for P in picks]
    T=None
    for P in picks: T=pkm.ec_add(T,P,a,p)
else:
    while True:
        x=trng.randrange(p); y=pkm.sqrt_mod(x**3+a*x+b,p)
        if y is not None: T=(x,y); break
S=msg.summation_poly(p,m,a,b,T[0])
vA,pA=msg.build_system("A",p,m,S,chain); vB,pB=msg.build_system("B",p,m,S,dict(coeffs=pkm.poly_from_roots(chain["V"],p)))
xs,ws=vA[:m],vA[m:]
if arm=="A_elim_ms": vars_,polys,extra=ws+xs,pA,["-e",str(len(ws))]
elif arm=="A_drl_ms": vars_,polys,extra=vA,pA,[]
else: vars_,polys,extra=vB,pB,[]
path=msg.write_input(vars_,p,polys); out=path+".gb"
t0=time.monotonic()
logf=path+".log"
with open(logf,"w") as lf:
    pr=subprocess.Popen(["msolve","-f",path,"-o",out]+extra+["-g","2","-v","2","-t","1"],stdout=lf,stderr=subprocess.STDOUT)
    _,status,ru=os.wait4(pr.pid,0)   # per-child rusage (this msolve process only)
wall=time.monotonic()-t0
log=open(logf).read(); os.unlink(logf)
pr.returncode=os.waitstatus_to_exitcode(status)
degs=[int(l.split()[0]) for l in log.splitlines() if re.match(r"^\s*\d+\s+\d+\s+\d+\s+\d+ x \d+",l)]
print(json.dumps(dict(L=L,inst=inst,arm=arm,rc=pr.returncode,wall_s=round(wall,3),maxrss_MB=round(ru.ru_maxrss/1024,1),f4_max_deg=max(degs) if degs else None)))
for f in (path,out):
    if os.path.exists(f): os.unlink(f)
