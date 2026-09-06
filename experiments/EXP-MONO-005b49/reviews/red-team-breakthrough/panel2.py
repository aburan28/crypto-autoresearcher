import json, math, statistics as st
rows=json.load(open("/tmp/claude/panel.json"))
n=20000
def phi_norm(z): return 0.5*(1+math.erf(z/math.sqrt(2)))
print("distinct ord curves:",len({r["p_ord"] for r in rows}),
      " distinct cm curves:",len({(r["p_cm"],r["v"]) for r in rows}))
tt=[r["tau"] for r in rows]
print("tau distribution:",{t:tt.count(t) for t in sorted(set(tt))})

# 1) exact vs closed-form: does (N,tau) determine the exact rate?
diffs=[]
for r in rows:
    if r["tau"]==1: continue
    d=(r["exact_ord"]-r["exact_cm"])/((r["exact_ord"]+r["exact_cm"])/2)
    diffs.append((d,r))
nz=[d for d,_ in diffs if abs(d)>1e-12]
print("\ncells (tau>1):",len(diffs)," with exact_ord != exact_cm:",len(nz))
if nz: print("  |rel diff| range: %.3e .. %.3e"%(min(map(abs,nz)),max(map(abs,nz))))
rel_closed=[ (r["exact_ord"]-r["closed"])/r["closed"] for _,r in diffs]
print("  exact vs Part-B closed form, ordinary curves: rel excess min %.4f max %.4f mean %.4f"%(min(rel_closed),max(rel_closed),sum(rel_closed)/len(rel_closed)))

# 2) calibration: z of observed vs EXACT, per curve-measurement (dedup curves)
seen=set(); zs=[]
for r in rows:
    for side,pk,obs,ex in (("ord",("o",r["p_ord"]),r["obs_ord"],r["exact_ord"]),
                           ("cm",("c",r["p_cm"],r["v"]),r["obs_cm"],r["exact_cm"])):
        if pk in seen or r["tau"]==1: continue
        seen.add(pk)
        mu=ex*n; var=n*ex*(1-ex)   # K in {0,1} approx
        zs.append(((obs-mu)/math.sqrt(var), side, pk, obs, mu))
z_only=[z for z,_,_,_,_ in zs]
print("\nCALIBRATION vs EXACT expectation, %d distinct curve-measurements:"%len(zs))
print("  mean z = %+.4f   sd z = %.4f   (ideal 0, 1)"%(st.mean(z_only),st.pstdev(z_only)))
print("  min %.3f max %.3f ; |z|>1.96: %d (expect %.1f)"%(min(z_only),max(z_only),
      sum(1 for z in z_only if abs(z)>1.96), 0.05*len(z_only)))
zo=[z for z,s,_,_,_ in zs if s=="ord"]; zc=[z for z,s,_,_,_ in zs if s=="cm"]
print("  ordinary curves: n=%d mean %+.4f sd %.4f"%(len(zo),st.mean(zo),st.pstdev(zo)))
print("  CM curves:       n=%d mean %+.4f sd %.4f"%(len(zc),st.mean(zc),st.pstdev(zc)))

# 3) pooled ord-vs-CM transversal log-ratio across DISTINCT curve pairs
usedo=set(); usedc=set(); ind=[]
for r in rows:
    if r["tau"]==1: continue
    ko=r["p_ord"]; kc=(r["p_cm"],r["v"])
    if ko in usedo or kc in usedc: continue
    usedo.add(ko); usedc.add(kc); ind.append(r)
print("\nINDEPENDENT (no shared curve) cross-prime cells: %d"%len(ind))
num=0.0; den=0.0
for r in ind:
    a=r["obs_ord"]; b=r["obs_cm"]
    if a==0 or b==0: continue
    lr=math.log(a/b); v=1.0/a+1.0/b
    num+=lr/v; den+=1.0/v
pl=num/den; se=math.sqrt(1/den); z=pl/se
print("  pooled log(ord/cm) = %+.6f  se=%.6f  z=%+.4f  p=%.4f  ratio=%.4f"%(pl,se,z,2*(1-phi_norm(abs(z))),math.exp(pl)))
print("  (H-MONO-1d50ac predicts a systematic ord-vs-CM difference; cell-1's own")
print("   transversal contribution was log(613/681)=%+.6f, i.e. ratio %.4f)"%(math.log(613/681),613/681))
