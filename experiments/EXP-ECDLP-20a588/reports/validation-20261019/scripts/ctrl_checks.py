#!/usr/bin/env python3
"""Validator independent controls for EXP-ECDLP-20a588 (not the producer's checks):
 (C1) variety-membership confusion matrix: for EVERY triple (x1,x2,x3) in V^3 (with w from the chain trace),
      eval_gb_at(basis, point) must equal [S_4(x1,x2,x3,xT) == 0 mod p], for the A_elim_ms basis and the B_ms basis.
      This is a positive AND negative control of the planted-in-variety checker and of each basis.
 (C2) Singular ideal-equality check: eliminate(w) of the chain ideal == <S_4, F_V(x1..x3)> (two-way reduce).
Usage: ctrl_checks.py L inst [inst ...]
"""
import importlib.util, itertools, json, random, hashlib, re, subprocess, sys, tempfile, os
HERE="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588"
spec=importlib.util.spec_from_file_location("bog",HERE+"/block_order_grid.py"); bog=importlib.util.module_from_spec(spec); spec.loader.exec_module(bog)
msg, pkm = bog.msg, bog.pkm
m=3; L=int(sys.argv[1]); insts=[int(x) for x in sys.argv[2:]]
plan=json.load(open(HERE+"/trial-plan.json"))
out=[]
for inst in insts:
    kind="planted" if inst<plan["planted_per_cell"] else "random"
    seed=int(hashlib.sha256(f"{plan['seed']}|{m}|{L}|{inst}".encode()).hexdigest()[:12],16)
    rng=random.Random(seed); p=pkm.find_prime(m,L); a=p-3
    while True:
        b=rng.randrange(1,p)
        if (4*a**3+27*b*b)%p: break
    chain=pkm.build_chain(p,L,rng); rng.sample(range(p),2**L)
    fb=pkm.factor_base(chain["V"],a,b,p)
    trng=random.Random(f"{seed}-False-target")
    if kind=="planted":
        picks=[trng.choice(fb) for _ in range(m)]
        picks=[P if trng.random()<.5 else pkm.ec_neg(P,p) for P in picks]
        T=None
        for P in picks: T=pkm.ec_add(T,P,a,p)
    else:
        while True:
            x=trng.randrange(p); y=pkm.sqrt_mod(x**3+a*x+b,p)
            if y is not None: T=(x,y); break
    S=msg.summation_poly(p,m,a,b,T[0])
    vA,pA=msg.build_system("A",p,m,S,chain)
    vB,pB=msg.build_system("B",p,m,S,dict(coeffs=pkm.poly_from_roots(chain["V"],p)))
    xs,ws=vA[:m],vA[m:]
    tA,tB={},{}
    resA,tA=bog.run_ms(ws+xs,pA,p,["-e",str(len(ws))],600)
    resB,tB=bog.run_ms(vB,pB,p,[],600)
    assert tA and tB
    Sexpr=re.sub(r"\^","**",S)
    V=chain["V"]; tr={x:pkm.chain_eval(x,chain["steps"],p,trace=True) for x in V}
    cm={"A_elim_ms":[0,0,0,0],"B_ms":[0,0,0,0]}  # TP, FP, FN, TN  (checker True/False vs S==0)
    nS0=0
    for t in itertools.product(V,repeat=m):
        env={f"x{i}":t[i-1] for i in range(1,m+1)}
        truth = (eval(Sexpr,{"__builtins__":{}},dict(env))%p==0)
        nS0+=truth
        envA=dict(env)
        for i in range(1,m+1):
            envA.update({f"w{i}{j:02d}":tr[t[i-1]][j] for j in range(1,L)})
        for arm,txt,e in (("A_elim_ms",tA,envA),("B_ms",tB,env)):
            got=msg.eval_gb_at(txt,e,p)
            cm[arm][(0 if truth else 1) if got else (2 if truth else 3)]+=1
    # off-V negative control: x1 shifted off V must fail both bases (when not accidentally in V)
    offfail=0; offtot=0
    for x1 in range(p):
        if x1 in set(V): continue
        env={"x1":x1,"x2":V[0],"x3":V[1]}
        envA=dict(env); 
        for i in range(1,m+1):
            envA.update({f"w{i}{j:02d}":0 for j in range(1,L)})
        offtot+=1; offfail += (not msg.eval_gb_at(tB,env,p))
        if offtot>=200: break
    # C2: Singular two-way ideal equality
    wprod="*".join(ws)
    script=[f"ring r = {p},({','.join(ws+xs)}),(dp({len(ws)}),dp({m}));",
            "ideal IA = "+",".join(pA)+";",
            "ideal IB = "+",".join(pB)+";",
            f"ideal E = eliminate(IA, {wprod});",
            "ideal GB2 = std(IB); ideal GE = std(E);",
            'print("FWD " + string(size(reduce(E,GB2))==0));',   # elim(IA) subset IB
            'print("BWD " + string(size(reduce(IB,GE))==0));',   # IB subset elim(IA)
            'print("SIZEE " + string(size(GE)) + " SIZEB " + string(size(GB2)));', "quit;"]
    with tempfile.NamedTemporaryFile("w",suffix=".sing",delete=False) as f: f.write("\n".join(script)+"\n"); path=f.name
    so=subprocess.run(["Singular","-q","--no-rc",path],capture_output=True,text=True,timeout=1200).stdout; os.unlink(path)
    rec=dict(L=L,inst=inst,kind=kind,p=p,V_size=len(V),triples=len(V)**m,S_zero_triples=nS0,
             confusion_TP_FP_FN_TN=cm,off_V_rejections=f"{offfail}/{offtot}",singular=so.split("\n")[:3])
    print(json.dumps(rec),flush=True)
