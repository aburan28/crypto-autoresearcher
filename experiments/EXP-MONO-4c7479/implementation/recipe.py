"""The character-triple (S6) recipe check: a THIRD, cheap check computed
alongside arm (a), predicting the D_4 class from
chi = Legendre symbol of (D, f(t1), f(t2)) in the split regime, or
(D, c0) in the inert regime. This is explicitly allowed to use quantities
from both arms (it is not itself one of the two independence-bound arms);
see `arms_and_controls.character_triple_recipe_check`.
"""
from __future__ import annotations

import fp_common as fc


def predict_split(f1: int, f2: int, p: int) -> str:
    c1 = fc.legendre(f1, p)
    c2 = fc.legendre(f2, p)
    if c1 == 1 and c2 == 1:
        return "identity"
    if c1 == -1 and c2 == -1:
        return "sigma1_sigma2"
    return "sigma_i"


def predict_inert(c0: int, p: int) -> str:
    return "block_swap_involution" if fc.legendre(c0, p) == 1 else "four_cycle"
