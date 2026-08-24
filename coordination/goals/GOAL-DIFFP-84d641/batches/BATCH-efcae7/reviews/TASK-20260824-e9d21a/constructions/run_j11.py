import sys, json, random
sys.path.insert(0,"/tmp/claude-0/-home-user-crypto-autoresearcher/74014664-c8be-5466-9b08-3527be9a0cb4/scratchpad/rt")
from rt_instruments import *

# ---- census shape ----
print("CENSUS shadow:", len(SHADOW))
for e in SHADOW:
    o = e.obj
    print(" ", e.id, o.primitive, "step_range", o.step_range,
          "block_index", o.block_index,
          "in_code", o.in_linearized_code,
          "dm_weight", (sum(bin(x).count('1') for x in o.delta_m) if o.primitive=="md5" else None),
          "dm_words", ([i for i,x in enumerate(o.delta_m) if x] if o.primitive=="md5" else None),
          "dv_len", (len(o.dv) if o.dv else None))
print("readable:", len(census.readable))

# ---- J11: does the flag move at every k?  MY prediction P-RT-1/2 ----
rng = random.Random(CP.SEEDS["null_draw_message_difference_perturbed"])
flag = {}
for e in SHADOW:
    if e.primitive != "sha1": continue
    src = e.obj; nbits = CP.md_bits(src)
    for k in CP.K_VALUES:
        plan=[("deterministic", tuple(range(k)))]
        if k>=1:
            plan += [("seeded", tuple(sorted(rng.sample(range(nbits),k)))) for _ in range(CP.R_SEEDED)]
        for dt,pos in plan:
            o = CP.perturb_message_difference(src,pos,f"k{k}")
            c = flag.setdefault((k,dt), {"draws":0,"flag_moved":0,"src_flag_true":0})
            c["draws"]+=1
            c["src_flag_true"] += 1 if src.in_linearized_code else 0
            c["flag_moved"] += 1 if (o.in_linearized_code != src.in_linearized_code) else 0
print("\nJ11 FLAG MOVEMENT (sha1 primary arm, per k and draw_type):")
for kk in sorted(flag): print("  k=%s %-13s draws=%4d flag_moved=%4d src_flag_true=%4d"%(kk[0],kk[1],flag[kk]["draws"],flag[kk]["flag_moved"],flag[kk]["src_flag_true"]))

# ---- J11b: is the perturbation vector ever a codeword? (mechanism check) ----
def is_cw(words): return P.sha1_expand(list(words)[:16],80)==list(words)
cnt={"tested":0,"e_is_codeword":0}
rng=random.Random(999)
for _ in range(2000):
    k=random.Random(_).choice([1,2,4,8,16])
    pos=sorted(rng.sample(range(2560),k))
    e=[0]*80
    for p in pos: e[p//32]^=1<<(p%32)
    cnt["tested"]+=1
    if is_cw(e): cnt["e_is_codeword"]+=1
print("\nJ11 MECHANISM: perturbation vector e itself a codeword?", cnt)

# ---- J11c: PD-4 counterfactual -- HOLD the flag fixed instead of recomputing ----
class Held:
    pass
def perturb_hold_flag(obj,pos,tag):
    o = CP.perturb_message_difference(obj,pos,tag)
    o.in_linearized_code = obj.in_linearized_code   # counterfactual: held fixed
    return o
for label, fn in (("RECOMPUTED (as committed)", CP.perturb_message_difference),
                  ("HELD FIXED (counterfactual)", perturb_hold_flag)):
    rng = random.Random(CP.SEEDS["null_draw_message_difference_perturbed"])
    attr={}
    honest = ADJ.Adjudicator(census, STRICT)
    skeys={e.id: ADJ.canonical(e.obj,STRICT) for e in SHADOW}
    memb=0; draws=0
    for e in SHADOW:
        if e.primitive!="sha1": continue
        src=e.obj; nbits=CP.md_bits(src)
        for k in CP.K_VALUES:
            plan=[("deterministic",tuple(range(k)))]
            if k>=1: plan+=[("seeded",tuple(sorted(rng.sample(range(nbits),k)))) for _ in range(CP.R_SEEDED)]
            for dt,pos in plan:
                o=fn(src,pos,f"cf{k}")
                if k==0: continue
                draws+=1
                sk=ADJ.canonical(o,STRICT)
                if sk in {skeys[x.id] for x in SHADOW}: memb+=1
                a="+".join(CP.attribution(sk,skeys[e.id]))
                attr[a]=attr.get(a,0)+1
    print("\nJ11 PD-4 COUNTERFACTUAL, sha1 k>=1, flag %s: draws=%d strict-member=%d"%(label,draws,memb))
    for a,n in sorted(attr.items(), key=lambda x:-x[1]): print("     %-60s %d"%(a,n))
