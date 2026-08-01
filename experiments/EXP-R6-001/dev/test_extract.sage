import time, sys
sys.argv = ["x"]
src = open("experiments/EXP-R6-001/R6_run.sage").read()
head = src.split("# ------------------------------------------------------------------- modes")[0]
exec(head.split("T0 = time.time()")[0].replace("import time, json, sys, os, subprocess, resource","import time, json, sys, os, subprocess, resource\nT0=time.time()"))
for fsize in (12, 14):
    c = find_curve_with_subgroup(2**13, int(1.15*2**13), 16, seed=101)
    E = EllipticCurve(GF(c["p"]), [c["a4"], c["a6"]])
    xs, pts = fb_random(E, fsize, seed=1000+fsize)
    R = pts[0]+pts[3]+pts[min(7,fsize-1)]
    xR = R.xy()[0]
    Rp, gens, eqs = build_system(E.base_field(), E.a4(), E.a6(), xs, xR, 3)
    t0=time.time(); I=Rp.ideal(eqs); gb=I.groebner_basis(); tgb=time.time()-t0
    t0=time.time(); vd=int(I.vector_space_dimension())
    lex=I.transformed_basis("fglm"); sols=back_substitute(lex, E.base_field()); tex=time.time()-t0
    nv = sum(1 for s in sols if verify_solution(E,R,s,gens,3)=="verified")
    print(f"F={fsize}: gb={tgb:.2f}s extract={tex:.2f}s vdim={vd} nsols={len(sols)} verified={nv}", flush=True)
