import importlib.util, subprocess, itertools, os, sys
SNAP = "/tmp/claude-0/validator2/snap/experiments/EXP-ECDLP-502ae2/msolve_grid.py"
spec = importlib.util.spec_from_file_location("grid", SNAP); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
p = 101
def ms(name, vars_, polys, extra=()):
    open(name + ".ms", "w").write(",".join(vars_) + "\n" + str(p) + "\n" + ",\n".join(polys) + "\n")
    r = subprocess.run(["msolve", "-f", name + ".ms", "-o", name + ".gb", "-g", "2", "-t", "1", *extra], capture_output=True, text=True)
    return r.returncode, open(name + ".gb").read()
# T1: known variety x1 in {1,2}, x2=x1+5, x3^2-x1*x2-7*x3+1=0
rc, gb = ms("t1", ["x1","x2","x3"], ["x1^2-3*x1+2", "x2-x1-5", "x3^2-x1*x2-7*x3+1"])
roots = [(a,b,c) for a in range(p) for b in range(p) for c in range(p)
         if (a*a-3*a+2)%p==0 and (b-a-5)%p==0 and (c*c-a*b-7*c+1)%p==0]
print("T1 rc", rc, "roots over F_p:", roots)
for pt in roots:
    print("  root", pt, "->", g.eval_gb_at(gb, dict(zip(["x1","x2","x3"], pt)), p))
nonroots = [(1,6,0), (2,7,0), (3,8,roots[0][2]), (roots[0][0], roots[0][1], (roots[0][2]+1)%p)]
for pt in nonroots:
    print("  non-root", pt, "->", g.eval_gb_at(gb, dict(zip(["x1","x2","x3"], pt)), p))
# count: fraction of all F_p^3 points accepted must equal number of roots
acc = sum(g.eval_gb_at(gb, {"x1":a,"x2":b,"x3":c}, p) for a in range(0,p,1) for b in range(p) for c in (0,1,roots[0][2]))
print("  exhaustive slice accepted:", acc)
# T2: inconsistent system -> basis [1]
rc, gb = ms("t2", ["x1","x2"], ["x1-1", "x1-2"])
print("T2 inconsistent rc", rc, repr(gb.strip().splitlines()[-1]), "->", g.eval_gb_at(gb, {"x1":1,"x2":0}, p))
# T3: vacuity probes on synthetic text
print("T3 empty basis '[]:' ->", g.eval_gb_at("#c\n[]:\n", {"x1":5}, p), "(vacuous pass if True)")
try:
    print("T3 no bracket ->", g.eval_gb_at("#c\n", {"x1":5}, p))
except Exception as e:
    print("T3 no bracket raises", type(e).__name__)
try:
    print("T3 missing var ->", g.eval_gb_at("[1*x1^1+1*y^1]:", {"x1":5}, p))
except Exception as e:
    print("T3 missing var raises", type(e).__name__)
# T4: msolve constant-term quirk: x1+3+4 should be x1+7 -> root 94
rc, gb = ms("t4", ["x1","x2"], ["x1+3+4", "x2-1"])
print("T4 'x1+3+4' basis:", gb.strip().splitlines()[-2:], "root 94 ->", g.eval_gb_at(gb, {"x1":94,"x2":1}, p), "root 97 ->", g.eval_gb_at(gb, {"x1":97,"x2":1}, p))
rc, gb = ms("t4b", ["x1","x2"], ["3+x1+4", "x2-1"])
print("T4b '3+x1+4' basis:", gb.strip().splitlines()[-2:])
# T5: Singular-style input (implicit coeff 1, negative coeffs, mixed monomials)
rc, gb = ms("t5", ["x1","x2"], ["x1^2*x2-2*x1*x2+x2-x1+1", "-x2^2+3*x2-2"])
sols = [(a,b) for a in range(p) for b in range(p) if (a*a*b-2*a*b+b-a+1)%p==0 and (-b*b+3*b-2)%p==0]
print("T5 singular-style roots", sols, [g.eval_gb_at(gb, {"x1":a,"x2":b}, p) for a,b in sols],
      "accepted count", sum(g.eval_gb_at(gb, {"x1":a,"x2":b}, p) for a in range(p) for b in range(p)))
# T6: A-arm style variable names (w101) and a lin_terms merge check
t = g.lin_terms([(5,"x1"), (-5*7,""), (-1,"x1^2"), (7,"x1"), (-9,"")], p)
print("T6 lin_terms", t, "#const terms", sum(1 for s in t.split("+") if "*" not in s))
rc, gb = ms("t6", ["x1","w101"], ["x1^2-4", "w101*(x1-3)-x1*(x1-3)-2".replace("*(x1-3)","*x1-3*w101").replace("-x1*x1-3*w101","-x1^2+3*x1") if False else "w101*x1-3*w101-x1^2+3*x1-2"])
for a in range(p):
    for b in range(p):
        if (a*a-4)%p==0 and (b*a-3*b-a*a+3*a-2)%p==0:
            print("  T6 root", (a,b), g.eval_gb_at(gb, {"x1":a,"w101":b}, p), "perturbed", g.eval_gb_at(gb, {"x1":a,"w101":(b+1)%p}, p))
