#!/usr/bin/env python3
"""
Analytic (saddle-point) constant c* for the boolean Semaev t=3 d_reg linear law.

A(z) = B(z)^n,  B(z) = (1+z)^2/((1+z^2)(1+z^3)) = (1+z)/((1+z^2)(1-z+z^2)).
d_reg(n) = first D with [z^D] A(z) <= 0.

Coefficient extraction (Cauchy):
    [z^{cn}] B(z)^n = (1/2πi) ∮ exp( n * g(z) ) dz/z ,  g(z)=log B(z) - c log z.
Saddle:  g'(z)=0  <=>  ψ(z) := z B'(z)/B(z) = c.
On (0,1), ψ rises from 0, peaks at z*, falls to ψ(1)=-3/2.
For c<ψ(z*) two real saddles; they COALESCE at c=c*=max ψ (double saddle,
g'=g''=0 <=> ψ'(z*)=0) and become a complex-conjugate pair for c>c*.
Two real saddles -> coefficient sign-definite (positive, real saddle dominates);
complex pair -> oscillatory coefficient -> sign changes appear.
=> c* = max_{z in (0,1)} ψ(z), located by ψ'(z*)=0  (Airy coalescing saddle).
"""
import mpmath as mp
mp.mp.dps = 50

def B(z):
    return (1+z)/((1+z**2)*(1-z+z**2))

def B2(z):  # alternate form, for cross-check
    return (1+z)**2/((1+z**2)*(1+z**3))

def logB(z):
    return mp.log(1+z) - mp.log(1+z**2) - mp.log(1-z+z**2)

def psi(z):        # z * (log B)'(z)  = z B'/B
    return z*mp.diff(logB, z)

def psip(z):       # ψ'(z)
    return mp.diff(psi, z)

# cross-check the two closed forms agree
for t in [0.1, 0.2, 0.5, 0.9]:
    assert abs(B(mp.mpf(t))-B2(mp.mpf(t))) < mp.mpf(10)**-40
print("B forms agree.")

# --- locate z* = argmax ψ on (0,1) via ψ'(z*)=0 ---
# scan to bracket
prev=None; brack=None
zz=mp.mpf('0.001')
best=(-mp.inf,None)
import numpy as np
grid=[mp.mpf(k)/1000 for k in range(1,1000)]
vals=[psi(z) for z in grid]
imax=max(range(len(vals)), key=lambda i: vals[i])
z_seed=grid[imax]
print("grid argmax z* ~", mp.nstr(z_seed,6), " psi ~", mp.nstr(vals[imax],8))

zstar = mp.findroot(psip, z_seed)
cstar = psi(zstar)
print()
print("=== Airy / coalescing-saddle constant ===")
print("z*   =", mp.nstr(zstar, 16))
print("c*   =", mp.nstr(cstar, 16))
print("psi'(z*) =", mp.nstr(psip(zstar), 6), " (should be ~0)")
print("psi''(z*)=", mp.nstr(mp.diff(psi,zstar,2), 6), " (should be <0: a max)")

# --- Independent cross-check: full complex-saddle Stokes system ---
# just PAST c*, the two real saddles have merged into a complex pair with
# Re g(complex) crossing Re g(real). At c* they coincide (the double saddle).
# Confirm: solve g'(w)=0 for complex w at c=c* -> should return w=z* (real, double).
def gp(z, c):
    return mp.diff(logB, z) - c/z
# second derivative zero too:
print("g''(z*) with c=c*:", mp.nstr(mp.diff(logB, zstar, 2) + cstar/zstar**2, 6),
      " (double saddle => also ~0)")

# --- exponential-rate view: Lambda(c) = g(z0(c)); first sign change where
#     the real saddle's dominance is lost = c* (density of d_reg). ---

# save
with open("saddle_out.txt","w") as f:
    f.write("z*=%s\nc*=%s\n" % (mp.nstr(zstar,20), mp.nstr(cstar,20)))
print("\nc* to 12 digits:", mp.nstr(cstar,12))
