"""CP6-782 (Zexe / arkworks ark-cp6-782 G1): endomorphism-ring facts, cheapest chain by the
endosweep cost model, and the explicit chain built and verified on points."""
import json, sys, time
import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from harness.endosweep.targets import Target, verify
from harness.endosweep import quadorder as QO
from harness.endosweep.sweep import SweepOptions, build_catalogue
from harness.endosweep.explicit import build_chain_endomorphism

p = 22369874298875696930346742206501054934775599465297184582183496627646774052458024540232479018147881220178054575403841904557897715222633333372134756426301062487682326574958588001132586331462553235407484089304633076250782629492557320825577
b = 17764315118651679038286329069295091506801468118146712649886336045535808055361274148466772191243305528312843236347777260247138934336850548243151534538734724191505953341403463040067571652261229308333392040104884438208594329793895206056414
r = 258664426012969094010652733694893533536393512754914660539884262666720468348340822774968888139573360124440321458177
h = 86482221941698704497288378992285180119495364068003923046442785886272123124361700722982503222189455144364945735564951561028
gx = 5511163824921585887915590525772884263960974614921003940645351443740084257508990841338974915037175497689287870585840954231884082785026301437744745393958283053278991955159266640440849940136976927372133743626748847559939620888818486853646
gy = 7913123550914612057135582061699117755797758113868200992327595317370485234417808273674357776714522052694559358668442301647906991623400754234679697332299689255516547752391831738454121261248793568285885897998257357202903170202349380518443

assert (gy*gy - (gx**3 + 5*gx + b)) % p == 0, "arkworks generator not on curve"
T = Target("CP6-782 G1", p, "weierstrass", {"a": 5, "b": b}, r, h,
           cost_model="weierstrass_jacobian_generic_a",
           notes="Zexe CP6-782 (arkworks ark-cp6-782), y^2 = x^3 + 5x + b, Fr = BLS12-377 Fq")
from harness.endosweep.toyverify import Curve
from math import isqrt
E = Curve(p, 5, b)
assert abs(p + 1 - h*r - 0) <= 2*isqrt(p) + 1, "h*n outside Hasse interval"
from sympy import isprime
assert isprime(p) and isprime(r)
G = (gx, gy)
assert E.mul(h*r, G) is None, "(h*n)*G != O"
P = E.mul(h, G)
assert P is not None and E.mul(r, P) is None, "h*G does not have order n"
print("order checks: h*n in Hasse interval; (h*n)*G = O; h*G has prime order n", flush=True)
Dfrob = QO.frobenius_discriminant(T.q, T.trace)
scan = QO.small_discriminant_scan(Dfrob, 2_000_000)
print("trace bits", T.trace.bit_length(), "D_K", scan.found, "conductor bits", scan.conductor.bit_length() if scan.conductor else None, flush=True)
D = scan.found
roots = QO.omega_eigenvalues(D, T.n)
print("omega eigenvalues mod n found:", len(roots), flush=True)
t0 = time.time()
gens, cheap, _ = build_catalogue(T, D, roots[0], SweepOptions())
iso = sorted((c for c in cheap if c["kind"] == "isogeny"), key=lambda c: c["cost_M"])
print(f"catalogue {time.time()-t0:.1f}s; isogeny candidates by cost:", flush=True)
for c in iso[:8]:
    print("  ", c["name"], "a=%d b=%d" % (c["a"], c["b"]), "degree", c["degree"], "cost_M", c["cost_M"], flush=True)
best = iso[0]
el = (best["a"], best["b"])
print("building chain for element", el, "degree", best["degree"], flush=True)
t0 = time.time()
res = build_chain_endomorphism(T.p, 5, b, T.n, T.h, D, el, curve_name=T.name)
print(f"chain build {time.time()-t0:.1f}s found={res.found} note={res.note!r}", flush=True)
out = {"target": T.name, "p_bits": p.bit_length(), "n_bits": r.bit_length(), "D_K": D,
       "conductor": scan.conductor, "class_number": None, "cheapest_by_cost": iso[:8], **res.__dict__}
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({k: (v if len(str(v)) < 300 else str(v)[:300] + "...") for k, v in out.items()}, indent=1, default=str))
