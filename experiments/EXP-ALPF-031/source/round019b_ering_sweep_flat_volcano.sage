#!/usr/bin/env sage
# ===========================================================================
# round019b_ering_sweep_flat_volcano.sage  --  push #2 (T2 fine-metric residual)
# e-ring crossbred-cutoff sweep across the flat-volcano isogeny class.
#
# The e-ring m=3 model (round016 fixture_ERING) is the structured factor base
# whose membership loci share a common factor -- the configuration most likely
# to open a crossbred cutoff below D_reg. Prime-field IC has NEVER shown a
# gate_meaningful=True here (NR-027). Question: does ANY horizontal Cl(O_K)
# neighbor of a flat-volcano curve open a gate_meaningful=True e-ring fall the
# start curve lacks? (If yes -> a class member is crossbred-weak -> headline
# falsified at the finer-than-solving-degree metric.)
#
# Run: sage round019b_ering_sweep_flat_volcano.sage
# ===========================================================================
import json
load("round016_gated_meter.sage")   # _semaev3, meter_gated, fixture_POSC

def ering_system(p, a, b):
    """e-ring m=3: [S_3(a,b), x0*x1, x0*x2] -- FB rows share common factor x0."""
    F = GF(p)
    R = PolynomialRing(F, 3, names=['x0','x1','x2']); x = R.gens()
    S3 = _semaev3(R, F(a), F(b))
    return [S3, x[0]*x[1], x[0]*x[2]], R, [0]

# ---- flat-volcano curve + horizontal neighbors (same as round019) ----
p = 4099; Fp = GF(p)
set_random_seed(20260601)
def flat_volcano_prime_curve(Fp, want_h=4):
    p = Fp.cardinality()
    for _ in range(6000):
        a=Fp.random_element(); b=Fp.random_element()
        if 4*a^3+27*b^2==0: continue
        E=EllipticCurve(Fp,[a,b]); N=E.order()
        if not N.is_prime(): continue
        D=(p+1-N)^2-4*p
        if D==fundamental_discriminant(D) and QuadraticField(D,'w').class_number()>=want_h:
            return E,N,D
    return None,None,None
E0,N,D = flat_volcano_prime_curve(Fp)
print("flat-volcano E0: y^2=x^3+%s x+%s /F_%d  N=%d(prime) D=%d(f=1)" % (E0.a4(),E0.a6(),p,N,D))
neighbors=[("E0",E0)]
for l in [2,3,5,7,11,13]:
    for phi in E0.isogenies_prime_degree(l):
        C=phi.codomain().short_weierstrass_model()
        if C.order()==N and all((C.a4(),C.a6())!=(E.a4(),E.a6()) for _,E in neighbors):
            neighbors.append(("l=%d"%l,C))
    if len(neighbors)>=6: break
Ec,Nc,_=flat_volcano_prime_curve(Fp,want_h=1)
while Nc==N: Ec,Nc,_=flat_volcano_prime_curve(Fp,want_h=1)
neighbors.append(("CTRL(diff-order)",Ec))

# ---- sweep the e-ring gated meter across the class ----
print()
print("  curve            | d_ff | D_reg | fires | summation_support | gate_meaningful")
print("  "+"-"*72)
rows=[]
for tag,E in neighbors:
    polys,R,si = ering_system(p, int(E.a4()), int(E.a6()))
    mg = meter_gated(polys, R, si, Dmax=12)
    supp = mg['gate_detail']['summation_support']
    rows.append({"tag":tag,"a":int(E.a4()),"b":int(E.a6()),
                 "d_ff":(int(mg['d_ff']) if mg['d_ff'] is not None else None),
                 "D_reg":(int(mg['D_reg']) if mg['D_reg'] is not None else None),
                 "fires":bool(mg['fires']),
                 "summation_support":(int(supp) if supp is not None else None),
                 "gate_meaningful":bool(mg['gate_meaningful'])})
    print("  %-16s| %4s | %5s | %5s | %17s | %s"
          % (tag, mg['d_ff'], mg['D_reg'], mg['fires'], supp, mg['gate_meaningful']))

# positive control: the meter CAN fire (Weil/extension setting) -- proves not always-False
pc_polys, pcR, pcsi = fixture_POSC(101)
pc = meter_gated(pc_polys, pcR, pcsi, Dmax=12)
print("  %-16s| %4s | %5s | %5s | %17s | %s   <- POS control (meter CAN fire)"
      % ("POS-C(WeilS3)", pc['d_ff'], pc['D_reg'], pc['fires'],
         pc['gate_detail']['summation_support'], pc['gate_meaningful']))

same=[r for r in rows if not r["tag"].startswith("CTRL")]
any_meaningful = any(r["gate_meaningful"] for r in same)
gm_set = sorted(set(r["gate_meaningful"] for r in same))
print()
print("  same-order curves: gate_meaningful set = %s ; d_ff set = %s" %
      (gm_set, sorted(set(r['d_ff'] for r in same), key=lambda v:(v is None, v))))
print("  ANY class member crossbred-weak (gate_meaningful=True)? %s" % any_meaningful)
print("  meter positive control fired? %s  (=> a False below is a real negative, not a dead meter)"
      % pc['gate_meaningful'])
print("  VERDICT: %s" % ("FALSIFIED -- investigate" if any_meaningful else
      "e-ring crossbred fall is gate_meaningful=False ACROSS the whole flat-volcano class (NR-027 holds class-wide)"))

json.dump({"start":{"p":int(p),"N":int(N),"D":int(D)},"rows":rows,
           "any_gate_meaningful":bool(any_meaningful),
           "pos_control_fired":bool(pc['gate_meaningful'])},
          open("round019b_ering_sweep_result.json","w"), indent=2)
print("\nwrote round019b_ering_sweep_result.json")
