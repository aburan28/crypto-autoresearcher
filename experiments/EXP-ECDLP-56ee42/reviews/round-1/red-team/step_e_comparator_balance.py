# Independent, minimal-compute check of the COMPARATOR (top_bit_fiber) level-set
# balance on the six frozen ladder rungs, using ONLY public curve parameters
# (p, b) from specification.yaml design/ladder.json (no discrete log k touched,
# no full-subgroup enumeration, no run record created).
#
# top_bit_fiber(x, p) := 1 if x >= 2^(bit_length(p)-1) else 0   (estimator.py:133-137)
#
# We compute the EXACT size of fiber 1 (top bit = 1) among the curve's N points
# by checking, for each of the (few) x values in [top, p), whether
# x^3 + x + b is a QR mod p (2 points), zero (1 point), or non-residue (0 points).
# This does not require k or the point ordering -- it only classifies x by its
# curve membership, which is independent of the discrete log.

curves = [
    (17, 131101, 27, 131113),
    (19, 524309, 80, 525361),
    (21, 2097169, 1, 2098321),
    (23, 8388617, 21, 8391797),
    (25, 33554473, 49, 33557891),
    (27, 134217757, 70, 134234689),
]

def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return 1 if r == 1 else -1

print(f"{'T':>3} {'p':>11} {'N':>11} {'bitlen(p)':>9} {'top':>11} {'high_dom':>9} {'low_dom':>11} "
      f"{'high_pts':>9} {'low_pts':>11} {'high_frac':>12}")
for T, p, b, N in curves:
    L = p.bit_length()
    top = 1 << (L - 1)
    high_dom = p - top       # domain-level count of x in [top, p)
    low_dom = top            # domain-level count of x in [0, top)
    high_pts = 0
    for x in range(top, p):
        rhs = (x * x * x + x + b) % p
        leg = legendre(rhs, p)
        if leg == 0:
            high_pts += 1
        elif leg == 1:
            high_pts += 2
        # leg == -1: not on curve, contributes 0
    # total affine points on curve = N - 1 (N includes O); O is convention (0,0) -> low fiber
    low_pts = (N - 1 - high_pts) + 1   # +1 for O at x=0 (low fiber)
    frac = high_pts / N
    print(f"{T:>3} {p:>11} {N:>11} {L:>9} {top:>11} {high_dom:>9} {low_dom:>11} "
          f"{high_pts:>9} {low_pts:>11} {frac:>12.8f}")
