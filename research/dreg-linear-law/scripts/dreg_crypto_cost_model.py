#!/usr/bin/env python3
"""
Crypto-scale + t-family cost model for the boolean Semaev Weil-descent route.

Uses ONLY the VALIDATED semi-regular Hilbert-series recurrence (SIG-005 instrument
'semireg_rank_pred', matched by the random support null for all D < d_reg):

    a[j] = C(nb,j) for j=0..nb
    for each equation of degree d (ascending j): a[j] -= a[j-d]      # divide by (1+z^d)
    d_reg := first D with a[D] <= 0.

t-family (nb, degree distribution) READ + VERIFIED from
experiments/EXP-SIG-005/src/semaev_tree.py (build_chained_system_symbolic +
weil_descend_to_F2):
    k   = ceil(n/t)              # dim V
    nb  = n*(t-2) + k*t          # boolean unknowns
    #deg2 eqs = n                # the single S3 that contains the constant R_X
    #deg3 eqs = n*(t-2)          # all other S3 polys (3 genuine variables each)
    total    = n*(t-1)
Anchors this reproduces exactly:
    t=3 (idealized nb=2n, n deg2 + n deg3): d_reg = 5,6,7,8,9,10 @ n=6,9,12,15,18,24
    t=7 n=161: nb=966, 161 deg2 + 805 deg3
No degree distribution is fabricated: only the two verified points (t=3 family,
t=7 n=161) plus the construction formula literally read from semaev_tree.py.
"""

from math import comb, log2, ceil


# ----------------------------------------------------------------------------
# core: validated semi-regular d_reg via the (1+z^d) division recurrence
# ----------------------------------------------------------------------------
def d_reg_semiregular(nb, eq_degs, cap=3000):
    """eq_degs: list like [2]*n2 + [3]*n3. Returns (d_reg, hilbert_coeffs_up_to_dreg).

    The recurrence a[j] -= a[j-d] only ever READS lower indices, so truncating the
    array to index `top` = min(nb, cap) leaves a[0..top] bitwise-identical to the
    full computation. d_reg is small vs nb here, so this is exact, not an approximation.
    """
    top = min(nb, cap)
    a = [comb(nb, j) for j in range(top + 1)]
    for d in eq_degs:
        for j in range(d, top + 1):
            a[j] -= a[j - d]
    for D in range(top + 1):
        if a[D] <= 0:
            return D, a[:D + 1]
    return None, a  # d_reg exceeds cap (raise cap if this ever triggers)


def log2_int(N):
    """Accurate log2 of an arbitrary-precision positive integer."""
    if N <= 0:
        return float("-inf")
    b = N.bit_length()
    shift = max(0, b - 60)
    return log2(N >> shift) + shift


def n_monomials_leq(nb, D):
    """# boolean (squarefree) monomials of degree <= D in nb vars = sum_{j<=D} C(nb,j)."""
    return sum(comb(nb, j) for j in range(D + 1))


def grobner_bits(nb, d_reg, omega):
    """log2 of (#monomials <= d_reg)^omega."""
    M = n_monomials_leq(nb, d_reg)
    return omega * log2_int(M), M


# ----------------------------------------------------------------------------
# t-family construction parameters (read + verified from semaev_tree.py)
# ----------------------------------------------------------------------------
def family_params(t, n):
    k = ceil(n / t)              # dim V = ceil(n/t)
    nb = n * (t - 2) + k * t
    n_deg2 = n                   # last S3 has constant R_X -> degree 2
    n_deg3 = n * (t - 2)         # every other S3 -> degree 3
    return dict(t=t, n=n, k=k, nb=nb, n_deg2=n_deg2, n_deg3=n_deg3,
                n_eqs=n_deg2 + n_deg3)


def eqdegs_from_params(p):
    return [2] * p["n_deg2"] + [3] * p["n_deg3"]


line = "=" * 78


# ----------------------------------------------------------------------------
# (0) VALIDATION: reproduce the published t=3 idealized anchors
# ----------------------------------------------------------------------------
print(line)
print("(0) VALIDATION  --  reproduce published t=3 idealized d_reg (nb=2n, n deg2 + n deg3)")
print(line)
print(f"{'n':>6} {'nb=2n':>7} {'d_reg':>6}  expected")
expected_t3 = {6: 5, 9: 6, 12: 7, 15: 8, 18: 9, 24: 10, 161: 46}
for n in [6, 9, 12, 15, 18, 24, 161]:
    nb = 2 * n
    dr, _ = d_reg_semiregular(nb, [2] * n + [3] * n)
    exp = expected_t3[n]
    flag = "OK" if dr == exp else "MISMATCH"
    print(f"{n:>6} {nb:>7} {dr:>6}  expected {exp:>4}   [{flag}]")

# large-n asymptotic anchors for t=3 (idealized)
print("\n   asymptotic t=3 anchors (idealized nb=2n):")
for n in [1000, 8000]:
    nb = 2 * n
    dr, _ = d_reg_semiregular(nb, [2] * n + [3] * n)
    print(f"     n={n:>5}: nb={nb:>6}  d_reg={dr:>5}  d_reg/n={dr / n:.4f}  (published: "
          f"{'252' if n == 1000 else '1929'})")


# ----------------------------------------------------------------------------
# (1) semi-regular d_reg for the ACTUAL crypto target t=7, n=161
# ----------------------------------------------------------------------------
print("\n" + line)
print("(1) CRYPTO TARGET  --  t=7, n=161  (nb=966, 161 deg-2 + 805 deg-3)")
print(line)
p7 = family_params(7, 161)
assert p7["nb"] == 966 and p7["n_deg2"] == 161 and p7["n_deg3"] == 805, p7
print(f"   construction (from semaev_tree.py): k=ceil(161/7)={p7['k']},  "
      f"nb=n*(t-2)+k*t = 161*5 + 23*7 = {p7['nb']}")
print(f"   equations: {p7['n_deg2']} deg-2 + {p7['n_deg3']} deg-3 = {p7['n_eqs']} total")
dr7, _ = d_reg_semiregular(p7["nb"], eqdegs_from_params(p7))
print(f"   ==> semi-regular d_reg = {dr7}    (task expected: 150)")


# ----------------------------------------------------------------------------
# (2) Grobner linear-algebra cost at t=7, n=161
# ----------------------------------------------------------------------------
print("\n" + line)
print("(2) GROBNER LINEAR-ALGEBRA COST  = (#monomials of deg <= d_reg in nb vars)^omega")
print(line)
M7 = n_monomials_leq(p7["nb"], dr7)
log2M7 = log2_int(M7)
print(f"   #monomials <= d_reg({dr7}) in nb={p7['nb']} boolean vars "
      f"= sum_(j<=150) C(966,j)")
print(f"   log2(#monomials) = {log2M7:.2f}   (i.e. ~2^{log2M7:.1f} monomials / matrix dimension)")
for omega in (2.0, 2.37):
    bits = omega * log2M7
    print(f"   omega={omega:<4}:  Grobner cost ~ 2^{bits:.1f}   (log2 = {bits:.2f})")


# ----------------------------------------------------------------------------
# (3) Rho baseline + the bit gap
# ----------------------------------------------------------------------------
print("\n" + line)
print("(3) RHO BASELINE  and  Grobner-vs-rho BIT GAP  @ n=161")
print(line)
rho_bits = 161 / 2.0
print(f"   rho on E(GF(2^161)) ~ 2^(n/2) = 2^{rho_bits:.1f}")
for omega in (2.0, 2.37):
    gbits = omega * log2M7
    print(f"   omega={omega:<4}:  Grobner 2^{gbits:.1f}  vs  rho 2^{rho_bits:.1f}   "
          f"-->  Grobner LOSES by {gbits - rho_bits:.1f} BITS")


# ----------------------------------------------------------------------------
# (4) t=3 vs t=7 density d_reg/nb
# ----------------------------------------------------------------------------
print("\n" + line)
print("(4) DENSITY d_reg/nb :  t=3  vs  t=7")
print(line)
# t=3 idealized crypto point n=161 (nb=2n=322)
nb3 = 2 * 161
dr3, _ = d_reg_semiregular(nb3, [2] * 161 + [3] * 161)
print(f"   t=3, n=161 (idealized nb=2n=322): d_reg={dr3:>4}, "
      f"d_reg/nb = {dr3 / nb3:.4f},  d_reg/n = {dr3 / 161:.4f}")
print(f"   t=7, n=161 (nb={p7['nb']})       : d_reg={dr7:>4}, "
      f"d_reg/nb = {dr7 / p7['nb']:.4f},  d_reg/n = {dr7 / 161:.4f}")


# ----------------------------------------------------------------------------
# (5) ROBUSTNESS: t=3..7 at a common scale n=161, using the VERIFIED construction
# ----------------------------------------------------------------------------
print("\n" + line)
print("(5) ROBUSTNESS  --  t = 3..7 at common scale n=161")
print("     (nb & degree-distribution from the construction READ in semaev_tree.py;")
print("      NOT a fabricated t-law -- each row is the literal Weil-descent count.)")
print(line)
hdr = f"{'t':>2} {'k':>3} {'nb':>5} {'#deg2':>6} {'#deg3':>6} {'d_reg':>6} " \
      f"{'log2#mon':>9} {'G(w=2)':>9} {'G(w=2.37)':>10} {'rho':>6} {'gap(w=2)':>9}"
print(hdr)
print("-" * len(hdr))
for t in [3, 4, 5, 6, 7]:
    p = family_params(t, 161)
    dr, _ = d_reg_semiregular(p["nb"], eqdegs_from_params(p))
    lm = log2_int(n_monomials_leq(p["nb"], dr))
    g2, g237 = 2.0 * lm, 2.37 * lm
    gap2 = g2 - rho_bits
    print(f"{t:>2} {p['k']:>3} {p['nb']:>5} {p['n_deg2']:>6} {p['n_deg3']:>6} "
          f"{dr:>6} {lm:>9.1f} 2^{g2:>7.0f} 2^{g237:>8.0f} 2^{rho_bits:>4.1f} "
          f"{gap2:>+9.0f}")

print("\n" + line)
print("HEADLINE CHECK")
print(line)
g2_head = 2.0 * log2M7
print(f"   t=7 n=161 semi-regular Grobner cost (omega=2)   = 2^{g2_head:.0f}")
print(f"   t=7 n=161 semi-regular Grobner cost (omega=2.37) = 2^{2.37 * log2M7:.0f}")
print(f"   rho                                              = 2^{rho_bits:.0f}")
print(f"   Grobner >= 2^1000 ?  {'YES' if g2_head >= 1000 else 'NO'} "
      f"(2^{g2_head:.0f})")
print(f"   Grobner astronomically worse than rho ?  "
      f"{'YES' if g2_head > rho_bits + 500 else 'NO'} "
      f"(loses {g2_head - rho_bits:.0f} bits even at omega=2)")
