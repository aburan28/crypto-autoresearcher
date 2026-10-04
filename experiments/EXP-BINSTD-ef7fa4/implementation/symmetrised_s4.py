"""Symmetrised S_4 in elementary-symmetric coordinates (char 2).

Verified identity (RC-1 B):
  S4_sym(e1,e2,e3,xR) =
      B^2 * e1^4
    + B   * e1^2 * e3 * xR
    +       e1^2 * e3^2 * xR^2
    + B   * e2^2 * xR^2
    +       e2^2 * e3 * xR^3
    +       e2^4 * xR^4
    + B   * e3^2
    + B   * e3 * xR^3
    +       e3^2 * xR^4
    +       e3^3 * xR
    +       e3^4
    + B^2 * xR^4

equals S4(x1,x2,x3,xR) whenever e_k = e_k(x1,x2,x3).
"""
from __future__ import annotations


def s3_field(F, B, x1, x2, x3):
    s = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.mul(s, s) ^ F.mul(F.mul(x1, x2), x3) ^ B


def s3_coeffs_field(F, B, x, y):
    xy = F.mul(x, y)
    xp = x ^ y
    alpha = F.mul(xp, xp)
    beta = xy
    gamma = F.mul(xy, xy) ^ B
    return alpha, beta, gamma


def s4_field(F, B, x1, x2, x3, x4):
    a1, b1, c1 = s3_coeffs_field(F, B, x1, x2)
    a2, b2, c2 = s3_coeffs_field(F, B, x3, x4)
    t1 = F.mul(a1, c2) ^ F.mul(a2, c1)
    t2 = F.mul(a1, b2) ^ F.mul(a2, b1)
    t3 = F.mul(b1, c2) ^ F.mul(b2, c1)
    return F.mul(t1, t1) ^ F.mul(t2, t3)


def elementary_symmetric(F, x1, x2, x3):
    e1 = x1 ^ x2 ^ x3
    e2 = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    e3 = F.mul(F.mul(x1, x2), x3)
    return e1, e2, e3


def s4_sym(F, B, e1, e2, e3, xR):
    """Evaluate symmetrised S_4 at (e1,e2,e3,xR). Returns field element."""
    B2 = F.mul(B, B)
    e1_2 = F.mul(e1, e1)
    e1_4 = F.mul(e1_2, e1_2)
    e2_2 = F.mul(e2, e2)
    e2_4 = F.mul(e2_2, e2_2)
    e3_2 = F.mul(e3, e3)
    e3_3 = F.mul(e3_2, e3)
    e3_4 = F.mul(e3_2, e3_2)
    xR_2 = F.mul(xR, xR)
    xR_3 = F.mul(xR_2, xR)
    xR_4 = F.mul(xR_2, xR_2)
    acc = 0
    acc ^= F.mul(B2, e1_4)
    acc ^= F.mul(B, F.mul(e1_2, F.mul(e3, xR)))
    acc ^= F.mul(e1_2, F.mul(e3_2, xR_2))
    acc ^= F.mul(B, F.mul(e2_2, xR_2))
    acc ^= F.mul(e2_2, F.mul(e3, xR_3))
    acc ^= F.mul(e2_4, xR_4)
    acc ^= F.mul(B, e3_2)
    acc ^= F.mul(B, F.mul(e3, xR_3))
    acc ^= F.mul(e3_2, xR_4)
    acc ^= F.mul(e3_3, xR)
    acc ^= e3_4
    acc ^= F.mul(B2, xR_4)
    return acc


def s4_sym_batch_e3(F, B, e1, e2, e3_arr, xR):
    """Vectorised s4_sym over a numpy int64 array of e3 values."""
    import numpy as np

    e3 = np.asarray(e3_arr, dtype=np.int64)
    B2 = F.mul(B, B)
    e1_2 = F.mul(e1, e1)
    e1_4 = F.mul(e1_2, e1_2)
    e2_2 = F.mul(e2, e2)
    e2_4 = F.mul(e2_2, e2_2)
    xR_2 = F.mul(xR, xR)
    xR_3 = F.mul(xR_2, xR)
    xR_4 = F.mul(xR_2, xR_2)
    e3_2 = F.vmul(e3, e3)
    e3_3 = F.vmul(e3_2, e3)
    e3_4 = F.vmul(e3_2, e3_2)
    acc = np.full(e3.shape, F.mul(B2, e1_4) ^ F.mul(B2, xR_4) ^ F.mul(B, F.mul(e2_2, xR_2)) ^ F.mul(e2_4, xR_4), dtype=np.int64)
    # B * e1^2 * e3 * xR
    acc ^= F.vmul(np.full_like(e3, F.mul(B, F.mul(e1_2, xR))), e3)
    # e1^2 * e3^2 * xR^2
    acc ^= F.vmul(np.full_like(e3, F.mul(e1_2, xR_2)), e3_2)
    # e2^2 * e3 * xR^3
    acc ^= F.vmul(np.full_like(e3, F.mul(e2_2, xR_3)), e3)
    # B * e3^2
    acc ^= F.vmul(np.full_like(e3, B), e3_2)
    # B * e3 * xR^3
    acc ^= F.vmul(np.full_like(e3, F.mul(B, xR_3)), e3)
    # e3^2 * xR^4
    acc ^= F.vmul(np.full_like(e3, xR_4), e3_2)
    # e3^3 * xR
    acc ^= F.vmul(np.full_like(e3, xR), e3_3)
    # e3^4
    acc ^= e3_4
    return acc


def verify_s4_sym_identity(F, B, trials: int = 200, seed: int = 0) -> dict:
    import numpy as np

    rng = np.random.default_rng(seed)
    fails = 0
    for _ in range(trials):
        xs = [int(rng.integers(0, F.q)) for _ in range(3)]
        xR = int(rng.integers(0, F.q))
        e1, e2, e3 = elementary_symmetric(F, *xs)
        if s4_sym(F, B, e1, e2, e3, xR) != s4_field(F, B, xs[0], xs[1], xs[2], xR):
            fails += 1
    return {"trials": trials, "failures": fails, "pass": fails == 0}
