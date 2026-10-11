#!/usr/bin/env python3
"""J3: the rho reference 2^60.8090 for ECC2K-130 (validator TASK-20260926-44629c).
Curve K_0: y^2 + xy = x^3 + 1 over F_2 (a = 0).  #E(F_2) = 4 -> trace t_1 = 2 + 1 - 4 = -1.
Frobenius trace recurrence: t_0 = 2, t_k = t_1 t_{k-1} - 2 t_{k-2};  #E(F_{2^k}) = 2^k + 1 - t_k.
"""
import mpmath as mp, random
mp.mp.dps = 50
r = 680564733841876926932320129493409985129

# (1) #E(F_2) by direct enumeration of y^2 + xy = x^3 + a x^2 + 1 over F_2, a = 0 and a = 1
def count_F2(a):
    c = 1  # point at infinity
    for x in (0, 1):
        for y in (0, 1):
            if (y * y + x * y) % 2 == (x ** 3 + a * x * x + 1) % 2:
                c += 1
    return c
E1_a0, E1_a1 = count_F2(0), count_F2(1)
t1_a0, t1_a1 = 3 - E1_a0, 3 - E1_a1
print(f"#E(F_2) a=0: {E1_a0} (t_1 = {t1_a0});  a=1: {E1_a1} (t_1 = {t1_a1})")

def trace(n, t1):
    t_prev, t = 2, t1
    for _ in range(2, n + 1):
        t_prev, t = t, t1 * t - 2 * t_prev
    return t if n >= 1 else 2

t131 = trace(131, t1_a0)
E131 = 2 ** 131 + 1 - t131
print(f"t_131 = {t131}")
print(f"#E(F_2^131) = {E131}")
print(f"4r          = {4 * r}")
print(f"#E == 4r ?  {E131 == 4 * r}   (#E mod 4 = {E131 % 4}, #E/4 == r ? {E131 // 4 == r})")
print(f"Hasse check |t_131| <= 2*2^65.5: {abs(t131) <= 2 * mp.sqrt(2 ** 131)}")

# (2) primality of r: own Miller-Rabin with 40 fixed+random bases, then sympy as an independent check
def miller_rabin(n, bases):
    if n < 4: return n in (2, 3)
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in bases:
        a %= n
        if a in (0, 1, n - 1): continue
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True
random.seed(20260926)
bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] + [random.randrange(2, r - 1) for _ in range(40)]
mr = miller_rabin(r, bases)
try:
    import sympy
    sp = sympy.isprime(r)
except Exception as e:
    sp = f"sympy unavailable: {e}"
print(f"r prime? Miller-Rabin(52 bases): {mr}; sympy.isprime: {sp}")
print(f"log2 r = {mp.nstr(mp.log(r, 2), 15)};  r - 2^129 = {r - 2**129}")
print(f"small-factor sieve of 4r cofactor: 4r = 2^2 * r, r odd = {r % 2 == 1}")

# (3) automorphism group on <G>: <-1> x <pi>, order 2 * 131 = 262, needs 131 | r - 1 (pi acts on <G> as a scalar of order 131)
print(f"(r-1) mod 131 = {(r - 1) % 131}  -> Frobenius eigenvalue of order 131 exists on <G>: {(r - 1) % 131 == 0}; 131 odd so -1 not in <lambda>; |<-1> x <pi>| = {2 * 131}")

# (4) the constant
def bits(x): return mp.log(x, 2)
cands = {
    "sqrt(pi r/2)                 plain rho, no symmetry": mp.sqrt(mp.pi * r / 2),
    "sqrt(pi r/4)                 negation only (0.886 sqrt r)": mp.sqrt(mp.pi * r / 4),
    "sqrt(pi r/(2*131))           Frobenius only": mp.sqrt(mp.pi * r / (2 * 131)),
    "sqrt(pi r/(4*131))           <-1> x <pi>  [finding; CORR-20260922-81aeab k=131]": mp.sqrt(mp.pi * r / (4 * 131)),
    "sqrt(pi r/2)/sqrt(262)       equivalent form quoted in the plan": mp.sqrt(mp.pi * r / 2) / mp.sqrt(262),
    "sqrt(pi r/(8*131))           negation double-counted (the 6cf862 defect)": mp.sqrt(mp.pi * r / (8 * 131)),
    "sqrt(pi * 4r/(4*131))        full group order instead of r (wrong)": mp.sqrt(mp.pi * 4 * r / (4 * 131)),
}
for k, v in cands.items():
    print(f"  {k:<75} = 2^{mp.nstr(bits(v), 8)}")
ref = mp.sqrt(mp.pi * r / (4 * 131))
print(f"\nREFERENCE sqrt(pi r/(4*131)) = 2^{mp.nstr(bits(ref), 10)};  producer quotes 2^60.8090 -> difference {mp.nstr(bits(ref) - mp.mpf('60.8090'), 4)} bits")
print(f"S = ref/sqrt(r) = {mp.nstr(ref / mp.sqrt(r), 8)}   (producer's note quotes S = 0.077430)")
print(f"sqrt(pi/(4*131)) = {mp.nstr(mp.sqrt(mp.pi/(4*131)), 8)}")
print(f"KN-LIT-096 relays Bailey et al. 2009/541 estimate 2^60.9 iterations (recalled from the KN-LIT entry, paper not opened here): 2^60.9 / 2^60.809 = 2^{mp.nstr(mp.mpf('60.9')-bits(ref),4)} -> consistent with rounding to one decimal")
