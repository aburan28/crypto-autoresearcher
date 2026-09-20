"""I_direct — assumption-free distinct K-root count for EXP-QSP-70b731.

N = deg gcd(X^{2^n} - X, L) in F_2[X], L = X^{2^{n'}} + lambda(X),
via repeated squaring of X modulo L (char-2). At toy n <= 20 an equivalent
full field enumeration is also provided for cross-checks inside this module.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import gf2_poly as gp
from field_f2n import FieldF2n


def L_poly(lam: int, n_prime: int) -> int:
    return gp.monomial(1 << n_prime) ^ lam


def count_direct(lam: int, n: int, n_prime: int) -> int:
    """Assumption-free N = #{x in F_{2^n} : x^{2^{n'}} = lam(x)} via deg gcd."""
    return gp.gcd_degree_with_L(n, n_prime, lam)


def count_by_enumeration(lam: int, n: int, n_prime: int,
                         field: Optional[FieldF2n] = None) -> Dict[str, Any]:
    """Full enumeration of K (n <= 20). Returns N and root list as ints."""
    if n > 20:
        raise ValueError("enumeration only for n <= 20")
    F = field or FieldF2n.for_n(n)
    roots: List[int] = []
    for x in F.all_elements():
        left = F.pow(x, 1 << n_prime)  # x^{2^{n'}}
        right = F.eval_f2_poly(lam, x)
        if left == right:
            roots.append(x)
    return {"N": len(roots), "roots": roots}


def measure_direct(lam: int, n: int, n_prime: int,
                   want_roots: bool = False) -> Dict[str, Any]:
    """Primary I_direct entry. Roots only via enumeration when n <= 20 and requested."""
    N = count_direct(lam, n, n_prime)
    out: Dict[str, Any] = {
        "instrument": "I_direct",
        "N": N,
        "n": n,
        "n_prime": n_prime,
        "lambda": lam,
        "lambda_hex": format(lam, "x"),
        "certificate_path": None,
        "roots": None,
    }
    if want_roots and n <= 20:
        en = count_by_enumeration(lam, n, n_prime)
        if en["N"] != N:
            out["enumeration_disagreement"] = {"gcd_N": N, "enum_N": en["N"]}
        out["roots"] = en["roots"]
        out["N"] = en["N"]  # prefer enumeration list consistency when both run
        # restore gcd as authoritative count; keep enum roots only if counts match
        out["N"] = N
        if en["N"] == N:
            out["roots"] = en["roots"]
    return out
