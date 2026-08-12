import json,math,sys
D=json.JSONDecoder()
def load(fn):
    s=open(fn).read(); i=0; out=[]
    while True:
        while i<len(s) and s[i] in " \n\t\r": i+=1
        if i>=len(s): break
        o,i=D.raw_decode(s,i); out.append(o)
    return out
NP=json.load(open(__file__.rsplit('/',1)[0]+"/NULL_PROBS.json"))
Q={1:NP["G1"]["P_max_ge_k_over_4_words"],2:NP["G2"]["P_max_ge_k_over_4_words"],
   3:NP["G3"]["P_max_ge_k_over_4_words"],4:NP["G4"]["P_max_ge_k_over_4_words"]}
def pois_tail(k,lam):
    # P(X>=k) for Poisson(lam), stable
    if k<=0: return 1.0
    if lam<=0: return 0.0
    t=math.exp(-lam); s=t
    for i in range(1,k):
        t*=lam/i; s+=t
    return max(0.0,1.0-s)
def zscore(obs,exp):
    return (obs-exp)/math.sqrt(exp) if exp>0 else float('nan')
def rrare(N): return math.log2(N/3.0)
def rrel(N,q): return 4.0/math.sqrt(N*q)
def line(d,g=0,k=4):
    N=d['N']; obs=d['g%d'%k][g]; exp=N*Q[k]
    return dict(label=d['label'],r=d['r'],prp=d['prp'],N=N,gen=g+1,k=k,obs=obs,exp=exp,
                ratio=obs/exp if exp else float('nan'),z=zscore(obs,exp),
                logp=math.log10(max(pois_tail(obs,exp),1e-300)) if obs>exp else 0.0,
                res_bits=rrare(N),rel_res=rrel(N,Q[k]))
