import sys, random
sys.path.insert(0,"/tmp/claude-0/-home-user-crypto-autoresearcher/74014664-c8be-5466-9b08-3527be9a0cb4/scratchpad/rt")
from rt_instruments import *

# (1) Is in_linearized_code a FUNCTION of message_difference in the strict key?
#     i.e. does dropping it lose ANY discrimination while dv is present?
print("(1) FLAG REDUNDANCY: in_linearized_code == sha1_in_linearized_code(dv) ?")
bad=0; tested=0
rng=random.Random(4242)
for e in SHADOW:
    if e.primitive!="sha1": continue
    for k in (1,2,4,8,16,64):
        for _ in range(20):
            pos=sorted(rng.sample(range(2560),k))
            o=CP.perturb_message_difference(e.obj,pos,"red")
            tested+=1
            if o.in_linearized_code != P.sha1_in_linearized_code(list(o.dv)): bad+=1
print("    objects tested %d, flag != f(dv): %d  -> flag is a DETERMINISTIC FUNCTION of dv"%(tested,bad))

# (2) O-D known-falsity witness: the E6 re-indexed image (block_index 3)
honest=Instr("honest", lambda k,p:k)
od    =Instr("O-D",    proj_drop(["block_index"]))
hits_h=hits_d=0
for e in SHADOW:
    img=EQ.act_E6_reindex(e.obj,3)
    if honest.verdict(img)[0]=="MEMBER": hits_h+=1
    if od.verdict(img)[0]=="MEMBER": hits_d+=1
print("\n(2) O-D KNOWN-FALSITY WITNESS: E6-reindexed images (block_index 0 -> 3), n=%d"%len(SHADOW))
print("    honest adjudicator MEMBER: %d/%d ; O-D (block_index-blind) MEMBER: %d/%d"%(hits_h,len(SHADOW),hits_d,len(SHADOW)))
print("    => O-D identifies the same difference pattern at two different block positions; no declared family presents such an object to CTL-NULL-D.")

# (3) O-E known-falsity witness detail: codeword weights of the sub-arm objects
rng2=random.Random(CP.SEEDS["null_draw_message_difference_perturbed"]); ws=[]; dvdiff=[]
oe=Instr("O-E", proj_drop_on_primitive(["message_difference"],"sha1"))
mh=mo=0
for e in SHADOW:
    if e.primitive!="sha1": continue
    plan=[tuple([1]+[0]*15)]+[tuple(rng2.getrandbits(32) for _ in range(16)) for _ in range(CP.R_SEEDED)]
    for w16 in plan:
        if not any(w16): continue
        o=CP.perturb_by_codeword(e.obj,w16,"rt")
        ws.append(o.path_data["codeword_hamming_weight"])
        dvdiff.append(sum(bin((a^b)&P.MASK32).count("1") for a,b in zip(o.dv,e.obj.dv)))
        if honest.verdict(o)[0]=="MEMBER": mh+=1
        if oe.verdict(o)[0]=="MEMBER": mo+=1
        assert o.in_linearized_code is True
print("\n(3) O-E KNOWN-FALSITY WITNESS: in-code perturbed SHA-1 objects, n=%d"%len(ws))
print("    dv Hamming distance from source: min %d max %d mean %.1f ; flag stays True on all"%(min(dvdiff),max(dvdiff),sum(dvdiff)/len(dvdiff)))
print("    honest MEMBER %d/%d ; O-E MEMBER %d/%d  -> O-E identifies %d SHA-1 objects whose message differences differ from the census entry's in a mean of %.0f bits."%(mh,len(ws),mo,len(ws),mo,sum(dvdiff)/len(dvdiff)))

# (4) md5 primary-arm attribution on the honest adjudicator
skeys={e.id: ADJ.canonical(e.obj,STRICT) for e in SHADOW}
rng3=random.Random(CP.SEEDS["null_draw_message_difference_perturbed"]); attr={}
for e in SHADOW:
    src=e.obj; nbits=CP.md_bits(src)
    for k in CP.K_VALUES:
        plan=[("deterministic",tuple(range(k)))]
        if k>=1: plan+=[("seeded",tuple(sorted(rng3.sample(range(nbits),k)))) for _ in range(CP.R_SEEDED)]
        for dt,pos in plan:
            if k==0 or e.primitive!="md5": continue
            o=CP.perturb_message_difference(src,pos,"a")
            a="+".join(CP.attribution(ADJ.canonical(o,STRICT),skeys[e.id])) or "(none)"
            attr[a]=attr.get(a,0)+1
print("\n(4) MD5 primary-arm attribution (honest adjudicator, k>=1):",attr)

# (5) the deterministic draw only ever touches WORD 0
print("\n(5) DETERMINISTIC DRAW COVERAGE: positions=range(k) for k in",CP.K_VALUES,
      "-> words touched:",sorted({p//32 for k in CP.K_VALUES for p in range(k)}),
      "of 16 (md5) / 80 (sha1). The deterministic arm can never probe blindness to any other word.")
