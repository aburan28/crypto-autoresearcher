import json, math, statistics as st
def Phi(z): return 0.5*(1+math.erf(z/math.sqrt(2)))
def two(z): return 2*(1-Phi(abs(z)))
rows=json.load(open("/tmp/claude/panel.json"))
n=20000
# supersingular check on panel CM curves
ss=[r for r in rows if r["N"]==r["p_cm"]+1]
print("panel cells whose CM curve is SUPERSINGULAR (N=p_cm+1): %d of %d ; distinct such CM curves: %d"
      %(len(ss),len(rows),len({(r["p_cm"],r["v"]) for r in ss})))
ssord=[r for r in rows if r["N"]==r["p_ord"]+1]
print("panel cells whose ORDINARY curve has N=p_ord+1: %d"%len(ssord))

# calibration split
seen=set(); recs=[]
for r in rows:
    if r["tau"]==1: continue
    for side,pk,obs,ex in (("ord",("o",r["p_ord"]),r["obs_ord"],r["exact_ord"]),
                           ("cm",("c",r["p_cm"],r["v"]),r["obs_cm"],r["exact_cm"])):
        if pk in seen: continue
        seen.add(pk)
        mu=ex*n; var=n*ex*(1-ex)
        recs.append(dict(side=side,tau=r["tau"],z=(obs-mu)/math.sqrt(var),
                         zclosed=(obs-r["closed"]*n)/math.sqrt(n*r["closed"]*(1-r["closed"])),
                         ss=(r["N"]==r["p_cm"]+1) if side=="cm" else False))
zo=[x["z"] for x in recs if x["side"]=="ord"]; zc=[x["z"] for x in recs if x["side"]=="cm"]
d=st.mean(zc)-st.mean(zo); sed=math.sqrt(st.pstdev(zc)**2/len(zc)+st.pstdev(zo)**2/len(zo))
print("\nmean z (vs EXACT): ord %+0.4f (n=%d) cm %+0.4f (n=%d) ; diff %+0.4f +/- %0.4f -> z=%.2f p=%.3f"
      %(st.mean(zo),len(zo),st.mean(zc),len(zc),d,sed,d/sed,two(d/sed)))
zoC=[x["zclosed"] for x in recs if x["side"]=="ord"]; zcC=[x["zclosed"] for x in recs if x["side"]=="cm"]
print("mean z (vs Part-B CLOSED FORM): ord %+0.4f cm %+0.4f  <- systematic positive bias = Part B's missing O(1/N) term"
      %(st.mean(zoC),st.mean(zcC)))
for t in (2,4):
    a=[x["z"] for x in recs if x["side"]=="ord" and x["tau"]==t]
    b=[x["z"] for x in recs if x["side"]=="cm" and x["tau"]==t]
    print("  tau=%d: ord %+0.3f (n=%d)  cm %+0.3f (n=%d)"%(t,st.mean(a),len(a),st.mean(b),len(b)))
b_ss=[x["z"] for x in recs if x["side"]=="cm" and x["ss"]]
b_no=[x["z"] for x in recs if x["side"]=="cm" and not x["ss"]]
print("  CM supersingular %+0.3f (n=%d) ; CM ordinary %+0.3f (n=%d)"%(
    st.mean(b_ss) if b_ss else float('nan'),len(b_ss),st.mean(b_no) if b_no else float('nan'),len(b_no)))

print("\n================ CELLS 1 AND 2: EXACT vs OBSERVED ================")
ex=json.load(open("/tmp/claude/exact_out.json")); gu=json.load(open("/tmp/claude/gu_out.json"))
obs={"cell1_ord":dict(tr=613,gu=1470,gu_tup=1049,tr_tup=613),
     "cell1_cm": dict(tr=681,gu=1405,gu_tup=1005,tr_tup=679),
     "cell2_ord":dict(tr=98, gu=233, gu_tup=167, tr_tup=98),
     "cell2_cm": dict(tr=94, gu=201, gu_tup=151, tr_tup=94)}
def phi_of(total,tup):
    """LOWER BOUND on the overdispersion factor Var(K)/E[K] implied by the
    reported (total pairs, tuples-with-collision) aggregates."""
    twos=total-tup; ones=tup-twos
    if ones<0: return 1.0
    EK=total/n; EK2=(ones+4*twos)/n
    return (EK2-EK*EK)/EK
res={}
for tag in obs:
    E_tr=ex[tag]["E_tr_exact"]; E_gu=gu[tag]["E_gu_analytic"]
    o=obs[tag]
    p_tr=phi_of(o["tr"],o["tr_tup"]); p_gu=phi_of(o["gu"],o["gu_tup"])
    mu_tr=E_tr*n; mu_gu=E_gu*n
    z_tr=(o["tr"]-mu_tr)/math.sqrt(n*p_tr*E_tr); z_gu=(o["gu"]-mu_gu)/math.sqrt(n*p_gu*E_gu)
    res[tag]=dict(E_tr=E_tr,E_gu=E_gu,P_exact=E_gu/E_tr,mu_tr=mu_tr,mu_gu=mu_gu,
                  obs_tr=o["tr"],obs_gu=o["gu"],z_tr=z_tr,z_gu=z_gu,phi_tr=p_tr,phi_gu=p_gu,
                  P_obs=(o["gu"]/n)/(o["tr"]/n))
    print("%-11s  E_tr=%.8f (exp %7.2f, obs %5d, z=%+5.2f)   E_gu=%.8f (exp %7.2f, obs %5d, z=%+5.2f)  P_exact=%.6f  P_obs=%.6f  phi_tr=%.3f phi_gu=%.3f"
          %(tag,E_tr,mu_tr,o["tr"],z_tr,E_gu,mu_gu,o["gu"],z_gu,E_gu/E_tr,(o["gu"]/o["tr"]),p_tr,p_gu))
for c,(a,b) in (("cell 1 (p=617) ",("cell1_ord","cell1_cm")),("cell 2 (p=3541)",("cell2_ord","cell2_cm"))):
    P3e=res[a]["P_exact"]/res[b]["P_exact"]; P3o=res[a]["P_obs"]/res[b]["P_obs"]
    print("%s  EXACT P3 = %.8f   (log = %+0.8f)   |   OBSERVED P3 = %.6f (log = %+0.6f)"
          %(c,P3e,math.log(P3e),P3o,math.log(P3o)))

print("\n================ VARIANCE-MODEL CORRECTION TO THE POOLED HEADLINE ================")
def cell(a,b,lr):
    va=res[a]["phi_gu"]/res[a]["obs_gu"]+res[a]["phi_tr"]/res[a]["obs_tr"]
    vb=res[b]["phi_gu"]/res[b]["obs_gu"]+res[b]["phi_tr"]/res[b]["obs_tr"]
    v0=1/res[a]["obs_gu"]+1/res[a]["obs_tr"]+1/res[b]["obs_gu"]+1/res[b]["obs_tr"]
    return lr,va+vb,v0
c1=cell("cell1_ord","cell1_cm",math.log((1470/613)/(1405/681)))
c2=cell("cell2_ord","cell2_cm",math.log((233/98)/(201/94)))
for nm,(lr,v,v0) in (("cell1",c1),("cell2",c2)):
    print("%s log-ratio %+0.6f  se(program, Poisson)=%.6f z=%+.4f p=%.4f  |  se(overdispersion-corrected)=%.6f z=%+.4f p=%.4f"
          %(nm,lr,math.sqrt(v0),lr/math.sqrt(v0),two(lr/math.sqrt(v0)),math.sqrt(v),lr/math.sqrt(v),two(lr/math.sqrt(v))))
for label,idx in (("PROGRAM (Poisson var)",2),("OVERDISPERSION-CORRECTED",1)):
    w1=1/c1[idx]; w2=1/c2[idx]
    pl=(w1*c1[0]+w2*c2[0])/(w1+w2); se=math.sqrt(1/(w1+w2)); z=pl/se
    print("pooled %-26s logr=%+0.6f se=%.6f z=%+.4f p=%.6f   (cell1 weight %.1f%%)"%(label,pl,se,z,two(z),100*w1/(w1+w2)))
w1=1/c1[2]; w2=1/c2[2]; se_prog=math.sqrt(1/(w1+w2))
w1c=1/c1[1]; w2c=1/c2[1]; se_corr=math.sqrt(1/(w1c+w2c))
infl=se_corr/se_prog
print("\nSE understatement factor = %.4f ; true size of the nominal alpha=0.05 pooled test = %.4f"%(infl,two(1.959964/infl)))

print("\n================ DECOMPOSITION OF THE POOLED SIGNAL ================")
for nm,(go,to,gc,tc) in (("cell1",(1470,613,1405,681)),("cell2",(233,98,201,94))):
    A=math.log(go/gc); B=math.log(tc/to)
    print("%s  log P3 = %+0.6f = [group-uniform arm %+0.6f] + [transversal arm %+0.6f]  (transversal share %.1f%%)"
          %(nm,A+B,A,B,100*B/(A+B)))
lr1,lr2=c1[0],c2[0]; w1=1/c1[2]; w2=1/c2[2]
print("cell 1 carries %.1f%% of the pooled weight; the transversal arm carries %.1f%% of cell 1's own log-signal"
      %(100*w1/(w1+w2),100*math.log(681/613)/lr1))
print("=> share of the POOLED signal contributed by the p=617 transversal-arm asymmetry alone: %.1f%%"
      %(100*(w1/(w1+w2))*(math.log(681/613)/lr1)*lr1/((w1*lr1+w2*lr2)/(w1+w2))))
