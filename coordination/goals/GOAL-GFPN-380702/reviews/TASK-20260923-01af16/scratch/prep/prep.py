#!/usr/bin/env python3
"""TASK-20260923-01af16 scratch invocation #1 (the plan's "confirm (-7/p) and
construct object A's curve" check), extended with the other light pre-checks the
proves-too-much objects need.  Writes only under this scratch directory.

  1. (-7/p) and p mod 7; object A: E_A: y^2 = x^3 - 35x + 98 over F_p
     (j = -3375, CM by Z[(1+sqrt(-7))/2]); #E_A(F_p) = p+1; supersingular.
     SEA over F_{p^5} (alarm-capped) must give p^5 + 1.
  2. object B: E_0: y^2 = x^3 + 3x + 8 over F_p; #E_0(F_p); SEA over F_{p^5}
     (alarm-capped); divisibility #E_0(F_p) | #E_0(F_{p^5}).
  3. structure of p^5 + 1 (object A's order) and of p^5 (its n - 1).
  4. j-invariants of the two named curves: in F_p or not (subfield test).
  5. GMP-ECM on p^5 and on p^5 + 1: genuine ECM logs used ONLY as the audit
     pipeline's documented --ecm-log-dir factor hints for object A (the
     producer's own D-3 workflow).  They are hints; the pipeline re-verifies
     every factor by exact division and a primality proof.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(HERE)
p = 2**64 - 2**32 + 1
q = p**5

GP = r"""
default(parisizemax, 2000000000);
p = 2^64 - 2^32 + 1; q = p^5;
print("P=", p);
print("P_MOD_7=", p % 7);
print("KRONECKER_MINUS7_P=", kronecker(-7, p));
EA = ellinit([-35, 98], p);
print("EA_J=", lift(EA.j)); print("MINUS3375_MOD_P=", (-3375) % p);
print("EA_DISC_NONZERO=", EA.disc != 0);
print("EA_CARD_FP=", ellcard(EA)); print("P_PLUS_1=", p + 1);
print("EA_SUPERSINGULAR_FP=", ellissupersingular(EA));
z = ffgen(Mod(1,p)*(x^5-3), 'z);
print("Z5M3_IRREDUCIBLE=", polisirreducible(Mod(1,p)*(x^5-3)));
EA5 = ellinit([-35 + 0*z, 98 + 0*z]);
t0 = getwalltime(); r = iferr(alarm(300, ellcard(EA5)), E, E); print("EA_CARD_FP5=", r); print("EA_CARD_FP5_MS=", getwalltime() - t0);
print("EA_CARD_FP5_EQ_Q_PLUS_1=", r == q + 1);
print("EA_SUPERSINGULAR_FP5=", ellissupersingular(EA5));
EB = ellinit([3, 8], p); NB1 = ellcard(EB); print("EB_CARD_FP=", NB1);
EB5 = ellinit([3 + 0*z, 8 + 0*z]);
t0 = getwalltime(); rb = iferr(alarm(300, ellcard(EB5)), E, E); print("EB_CARD_FP5=", rb); print("EB_CARD_FP5_MS=", getwalltime() - t0);
t1 = p + 1 - NB1; tt = vector(6); tt[1] = 2; tt[2] = t1; for(k = 3, 6, tt[k] = t1*tt[k-1] - p*tt[k-2]);
print("EB_CARD_FP5_BY_FROBENIUS_RECURSION=", q + 1 - tt[6]);
print("EB_FP_DIVIDES_FP5=", if(type(rb) == "t_INT", rb % NB1 == 0, "n/a"));
print("EB_T1=", t1); print("EB_T1SQ_MINUS_4P=", t1^2 - 4*p); print("EB_CORE_T1SQ_M4P=", core(t1^2 - 4*p));
print("P_PLUS_1_FACTOR=", factor(p + 1));
phi = p^4 - p^3 + p^2 - p + 1; print("PHI10=", phi); print("PHI10_BITS=", #binary(phi)); print("PHI10_ISPSEUDOPRIME=", ispseudoprime(phi));
t0 = getwalltime(); fphi = iferr(alarm(300, factor(phi)), E, E); print("PHI10_FACTOR=", fphi); print("PHI10_FACTOR_MS=", getwalltime() - t0);
Emas = ellinit([3, 8*z^4]); jm = Emas.j; print("J_MAS_IN_FP=", jm^p == jm);
Egf = ellinit([263*z - 4/3, 16/27 - 2*263*z/3]); jg = Egf.j; print("J_GF_IN_FP=", jg^p == jg);
"""

def main():
    os.makedirs(HERE, exist_ok=True)
    gpf = os.path.join(HERE, "prep.gp")
    open(gpf, "w").write(GP)
    t0 = time.time()
    r = subprocess.run(["gp", "-q", gpf], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1500)
    open(os.path.join(HERE, "prep.gp.out"), "w").write(r.stdout)
    open(os.path.join(HERE, "prep.gp.err"), "w").write(r.stderr)
    print(f"gp rc={r.returncode} wall={time.time()-t0:.1f}s")
    # GMP-ECM hint logs for object A (genuine ecm output)
    ecm_dir = os.path.join(SCR, "ecm_objA")
    os.makedirs(ecm_dir, exist_ok=True)
    for name, N, B1, curves in [("ecm_objA_nm1_p5", q, "11000", "200"), ("ecm_objA_twist_p5plus1", q + 1, "100000", "40")]:
        t1 = time.time()
        rr = subprocess.run(["ecm", "-c", curves, B1], input=f"{N}\n", capture_output=True, text=True, timeout=900)
        open(os.path.join(ecm_dir, f"{name}.out"), "w").write(rr.stdout)
        open(os.path.join(ecm_dir, f"{name}.err"), "w").write(rr.stderr)
        print(f"ecm {name}: rc={rr.returncode} wall={time.time()-t1:.1f}s")
    return 0

if __name__ == "__main__":
    sys.exit(main())
