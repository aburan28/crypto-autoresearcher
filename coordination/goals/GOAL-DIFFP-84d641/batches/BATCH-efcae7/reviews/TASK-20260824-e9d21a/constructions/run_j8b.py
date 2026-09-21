import sys, json, random, time
sys.path.insert(0,"/tmp/claude-0/-home-user-crypto-autoresearcher/74014664-c8be-5466-9b08-3527be9a0cb4/scratchpad/rt")
from rt_instruments import *
t0=time.time()
# ---- compute the committed STRICT variant-key lists ONCE, reuse for every instrument
entry_keys = {e.id: (vkeys(e.obj), e.obj.primitive) for e in SHADOW}
plant_keys=[]
for e in SHADOW:
    for o in [e.obj]+list(ADJ.orbit_images(e.obj, STRICT)):
        plant_keys.append((vkeys(o), o.primitive))
null_keys={}
for fam,d in CP.null_draws(census, n=1000).items():
    null_keys[fam]=[(vkeys(o), o.primitive) for o in d["draws"]]
rng = random.Random(CP.SEEDS["null_draw_message_difference_perturbed"])
d_keys=[]   # (primitive, k, keys)
for e in SHADOW:
    src=e.obj; nbits=CP.md_bits(src)
    for k in CP.K_VALUES:
        plan=[("deterministic",tuple(range(k)))]
        if k>=1: plan+=[("seeded",tuple(sorted(rng.sample(range(nbits),k)))) for _ in range(CP.R_SEEDED)]
        for dt,pos in plan:
            o=CP.perturb_message_difference(src,pos,f"k{k}")
            d_keys.append((e.primitive,k,dt,vkeys(o),e.id))
rng2 = random.Random(CP.SEEDS["null_draw_message_difference_perturbed"])
sub_keys=[]
for e in SHADOW:
    if e.primitive!="sha1": continue
    plan=[tuple([1]+[0]*15)]+[tuple(rng2.getrandbits(32) for _ in range(16)) for _ in range(CP.R_SEEDED)]
    for w16 in plan:
        if not any(w16): continue
        o=CP.perturb_by_codeword(e.obj,w16,"rt")
        sub_keys.append((vkeys(o), e.id))
print("keys built in %.1fs; plant=%d null=%d d=%d subarm=%d"%(time.time()-t0,len(plant_keys),sum(len(v) for v in null_keys.values()),len(d_keys),len(sub_keys)))

def canon(keys, prim, proj): return min(proj(k,prim) for k in keys)

INSTRUMENTS = [
 ("HONEST (control)",                                    lambda k,p: k),
 ("R2  md-blind BOTH primitives  [= contract row 2]",    proj_drop(["message_difference"])),
 ("O-E md-blind on SHA1 ONLY     [plan candidate v]",    proj_drop_on_primitive(["message_difference"],"sha1")),
 ("O-E' md-blind on MD5 ONLY",                           proj_drop_on_primitive(["message_difference"],"md5")),
 ("O-A lossy: differing-WORD-INDEX SET",                 proj_lossy_wordset),
 ("O-A' lossy: Hamming WEIGHT only",                     proj_lossy_weight),
 ("O-D block_index-blind",                               proj_drop(["block_index"])),
 ("O-C d2: block_index+length blind",                    proj_drop(["block_index","length"])),
 ("O-C' d2: block_index+in_linearized_code blind",       proj_drop(["block_index","in_linearized_code"])),
 ("O-C'' d3: block_index+length+in_linearized_code",     proj_drop(["block_index","length","in_linearized_code"])),
 ("O-RT2 SHA1 md := SEED WINDOW dv[:16] only",           proj_seed16_sha1),
 ("O-RT2' SHA1 md := dv[:16], flag-blind",               proj_seed16_sha1_noflag),
 ("O-B  SHA1 md-blind AND flag-blind",
    lambda k,p: tuple(x for x in k if not (p=="sha1" and x[0] in ("message_difference","in_linearized_code")))),
 ("O-RT3 md-blind SHA1 + lossy WEIGHT on MD5",
    lambda k,p: (tuple(x for x in k if x[0]!="message_difference") if p=="sha1"
                 else proj_lossy_weight(k,p))),
]
out=[]
for name,proj in INSTRUMENTS:
    idx={}
    for eid,(keys,prim) in entry_keys.items(): idx.setdefault(canon(keys,prim,proj),[]).append(eid)
    hits=sum(1 for keys,prim in plant_keys if canon(keys,prim,proj) in idx)
    fp={f:sum(1 for keys,prim in v if canon(keys,prim,proj) in idx) for f,v in null_keys.items()}
    cells={}
    for prim,k,dt,keys,eid in d_keys:
        c=cells.setdefault((prim,k),{"draws":0,"member":0}); c["draws"]+=1
        if canon(keys,prim,proj) in idx: c["member"]+=1
    md5m=sum(c["member"] for (p,k),c in cells.items() if p=="md5" and k>=1)
    s1m =sum(c["member"] for (p,k),c in cells.items() if p=="sha1" and k>=1)
    k0m =sum(c["member"] for (p,k),c in cells.items() if k==0)
    k0d =sum(c["draws"]  for (p,k),c in cells.items() if k==0)
    subm=sum(1 for keys,eid in sub_keys if canon(keys,"sha1",proj) in idx)
    fptot=sum(fp.values())
    passes = (hits==len(plant_keys)) and fptot==0 and md5m==0 and s1m==0 and k0m==k0d
    detected = "DETECTED" if (hits!=len(plant_keys) or fptot>0 or md5m+s1m>0 or k0m!=k0d) else "NOT DETECTED"
    old = "DETECTED" if (hits!=len(plant_keys) or fptot>0) else "NOT DETECTED"
    out.append(dict(name=name,plant=f"{hits}/{len(plant_keys)}",null_fp=fp,null_fp_total=fptot,
                    d_md5_k_ge_1_member=md5m,d_sha1_k_ge_1_member=s1m,k0=f"{k0m}/{k0d}",
                    subarm_incode_member=f"{subm}/{len(sub_keys)}",
                    passes_strengthened_suite=passes,OLD=old,STRENGTHENED=detected,
                    per_cell={f"{p}|k={k}":c for (p,k),c in sorted(cells.items())}))
    print("%-52s PLANT %-7s NULLabc %-4d  D md5>=1 %-5d sha1>=1 %-5d k0 %-9s SUBARM %-8s PASSES=%-5s OLD=%-12s STR=%s"%(
        name,f"{hits}/{len(plant_keys)}",fptot,md5m,s1m,f"{k0m}/{k0d}",f"{subm}/{len(sub_keys)}",passes,old,detected))
json.dump(out,open("/tmp/claude-0/-home-user-crypto-autoresearcher/74014664-c8be-5466-9b08-3527be9a0cb4/scratchpad/rt/j8_results.json","w"),indent=1,default=str)
print("\nPER-CELL for the decisive rows:")
for r in out:
    if r["name"].startswith(("R2","O-E m")):
        print(" ",r["name"],{k:v for k,v in r["per_cell"].items()})
print("elapsed %.1fs"%(time.time()-t0))
