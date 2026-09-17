"""INDEPENDENT verification of the published root lists.

Reads rederivation_results.json and verifies, for every listed root x (read from
the PUBLISHED 131-bit coefficient vector, not from any internal object):

  (i)   x^(2^33) == lambda(x)  in K = F_2[z]/(z^131+z^13+z^2+z+1)
  (ii)  the listed roots are pairwise distinct
  (iii) each orbit is closed under x -> x^2 and has the stated size
  (iv)  the orbit really is a single Frobenius cycle

using TWO checkers with disjoint lineage:

  CHECKER A: sympy.polys.galoistools (foreign code; dense coefficient lists,
             highest degree first; sympy's own gf_mul/gf_rem).
  CHECKER B: textbook coefficient lists (index = degree), schoolbook convolution
             and long division written from scratch here.  No bit packing, no
             import from gf2poly/gfk/method.

Neither checker imports anything from the code that FOUND the roots.
"""
import json, sys

F_EXPS = [131, 13, 2, 1, 0]          # z^131 + z^13 + z^2 + z + 1
N = 131
NPRIME = 33

# ---------------- CHECKER B: textbook coefficient lists ----------------

def b_fromvec(bits_lsb):
    return [int(c) for c in bits_lsb]          # index = degree

def b_trim(a):
    while a and a[-1] == 0:
        a.pop()
    return a

def b_mul(a, b):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    r[i + j] ^= 1
    return b_trim(r)

def b_mod(a, m):
    a = list(a)
    b_trim(a)
    dm = len(m) - 1
    while len(a) - 1 >= dm and a:
        sh = len(a) - 1 - dm
        for i, mi in enumerate(m):
            if mi:
                a[i + sh] ^= 1
        b_trim(a)
    return a

def b_field():
    f = [0] * (N + 1)
    for e in F_EXPS:
        f[e] = 1
    return f

def b_check(lam_packed, root_vec, f):
    x = b_fromvec(root_vec)
    b_trim(x)
    y = list(x)
    for _ in range(NPRIME):
        y = b_mod(b_mul(y, y), f)
    # lambda(x) by Horner
    r = []
    for i in range(lam_packed.bit_length() - 1, -1, -1):
        r = b_mod(b_mul(r, x), f)
        if (lam_packed >> i) & 1:
            if r:
                r[0] ^= 1
                b_trim(r)
            else:
                r = [1]
    return y == r, y, r

# ---------------- CHECKER A: sympy ----------------

from sympy.polys.galoistools import gf_mul, gf_rem, gf_add, gf_strip
from sympy.polys.domains import ZZ

def a_fromvec(bits_lsb):
    hi = [int(c) for c in reversed(bits_lsb)]      # highest degree first
    return gf_strip(hi)

def a_field():
    v = [0] * (N + 1)
    for e in F_EXPS:
        v[N - e] = 1
    return v

def a_check(lam_packed, root_vec, f):
    x = a_fromvec(root_vec)
    y = x
    for _ in range(NPRIME):
        y = gf_rem(gf_mul(y, y, 2, ZZ), f, 2, ZZ)
    r = []
    for i in range(lam_packed.bit_length() - 1, -1, -1):
        r = gf_rem(gf_mul(r, x, 2, ZZ), f, 2, ZZ)
        if (lam_packed >> i) & 1:
            r = gf_add(r, [1], 2, ZZ)
    return gf_strip(y) == gf_strip(r)

def a_sqr(x, f):
    return gf_rem(gf_mul(x, x, 2, ZZ), f, 2, ZZ)

# ---------------- driver ----------------

if __name__ == '__main__':
    data = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'rederivation_results.json'))
    fb, fa = b_field(), a_field()
    total_ok = True
    for ent in data['attaining']:
        lam = ent['lambda_packed']
        print(f"lambda = {ent['lambda']}  (packed {lam})   claimed N = {ent['N']}")
        allvecs = []
        for orb in ent['orbits']:
            vecs = orb['roots_bits_lsb_first']
            allvecs += vecs
            # (iii)/(iv) orbit closed under squaring, single cycle of stated size
            xs = [a_fromvec(v) for v in vecs]
            sq = [gf_strip(a_sqr(x, fa)) for x in xs]
            setxs = {tuple(x) for x in xs}
            closed = all(tuple(s) in setxs for s in sq)
            # single cycle: iterate squaring from the first element
            cyc, cur = [xs[0]], a_sqr(xs[0], fa)
            while gf_strip(cur) != gf_strip(xs[0]) and len(cyc) <= len(xs) + 2:
                cyc.append(gf_strip(cur)); cur = a_sqr(cur, fa)
            print(f"  orbit: stated size {orb['orbit_size']}, listed {len(vecs)}, "
                  f"closed under x->x^2: {closed}, Frobenius cycle length: {len(cyc)}")
            total_ok &= closed and len(cyc) == orb['orbit_size'] == len(vecs)
        # (ii) distinctness -- on the published vectors
        distinct = len(set(allvecs)) == len(allvecs)
        print(f"  {len(allvecs)} listed roots, pairwise distinct (as published vectors): {distinct}")
        total_ok &= distinct and len(allvecs) == ent['N']
        # (i) both checkers
        na = nb = 0
        for v in allvecs:
            assert len(v) == 131, 'root vector is not length 131'
            if a_check(lam, v, fa):
                na += 1
            if b_check(lam, v, fb)[0]:
                nb += 1
        print(f"  CHECKER A (sympy):            x^(2^33) == lambda(x) for {na}/{len(allvecs)}")
        print(f"  CHECKER B (textbook lists):   x^(2^33) == lambda(x) for {nb}/{len(allvecs)}")
        total_ok &= (na == nb == len(allvecs))
        print()
    print('INDEPENDENT ROOT VERIFICATION:', 'ALL PASS' if total_ok else 'FAILURE')
