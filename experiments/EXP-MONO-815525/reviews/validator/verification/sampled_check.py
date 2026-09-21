import json, sys, time
from collections import Counter
sys.path.insert(0, ".")
from ffield import norm, deg, gcdp, derivp, has_root_Fp, factor_shape
from qe_indep import qe_from_my_S4, to_Fp, s3_of_e

RAW="/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-815525/runs/RUN-MONO-815525-1/raw-result.json"
d=json.load(open(RAW))
inst=d["stage_1"]["instances"]
print("sampled instances:", len(inst))
t0=time.time(); agg=Counter(); mism=[]
for r in inst:
    p,A,B,e1,e2,e3 = r["p"],r["A"],r["B"],r["e1"],r["e2"],r["e3"]
    agg["g_irreducible"] += not has_root_Fp([(-e3)%p, e2%p, (-e1)%p, 1], p)
    cs,_F,_a,_b,_c = qe_from_my_S4(p,A,B,e1,e2,e3)
    fp = to_Fp(cs,p)
    agg["lands_in_Fp"] += fp is not None
    q = norm(fp[:],p)
    rec = norm(list(r["Qe_coeffs_low_to_high"]),p)
    if q!=rec: mism.append((r["curve"],e1,e2,e3,q,rec))
    else: agg["Qe_matches_record"] += 1
    agg["c4_is_S3sq"] += ((fp[4]-s3_of_e(p,A,B,e1,e2,e3)**2)%p==0)
    agg["squarefree"] += deg(gcdp(q,derivp(q,p),p))==0
    sh=tuple(factor_shape(q,p))
    agg["shape_deg%d_%s"%(deg(q),"+".join(map(str,sh)))] += 1
    agg["my_pattern_matches_record"] += (("deg%d:%s"%(deg(q),"+".join(map(str,sh))))==r["pattern"])
print("elapsed %.1fs"%(time.time()-t0))
for k in sorted(agg): print("  %-34s %d / %d"%(k,agg[k],len(inst)))
print("  mismatches:",len(mism),mism[:3])
print("  per-curve:",dict(Counter((r["curve"],r["p"]) for r in inst)))
