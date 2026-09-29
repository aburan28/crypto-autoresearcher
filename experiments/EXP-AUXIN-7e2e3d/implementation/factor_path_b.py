"""Independent arithmetic path B for EXP-AUXIN-7e2e3d.

Does NOT import factor_path_a or its factorizer. Accepts factor lists and:
  1. recomputes the product of reported prime powers (+ optional cofactor);
  2. re-proves primality of each reported factor with an independent call;
  3. recomputes E(r) / E_bound from the factor lists with its own Decimal evaluator.

Never recovers a discrete logarithm and never runs Cheon.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from math import isqrt
from typing import Any, Dict, List, Optional

from sympy import isprime as sympy_isprime

getcontext().prec = 96  # independent precision setting from e_eval.py (80)


def _is_probable_prime(n: int) -> bool:
    """Second primality check: sympy.isprime (independent call site from path A)."""
    if n <= 1:
        return False
    return bool(sympy_isprime(int(n)))


def _divisors(prime_powers: Dict[int, int], unfactored: Optional[int]) -> List[int]:
    primes = sorted(prime_powers)
    divs = [1]
    for p in primes:
        e = int(prime_powers[p])
        growth = []
        pe = 1
        for _ in range(e):
            pe *= int(p)
            for d in divs:
                growth.append(d * pe)
        divs.extend(growth)
    if unfactored is not None:
        c = int(unfactored)
        divs = sorted(set(divs + [d * c for d in divs]))
    else:
        divs = sorted(divs)
    return divs


def _expr(d: int, m: int) -> Decimal:
    dd = Decimal(d)
    return (Decimal(m) / dd).sqrt() + dd.sqrt()


def _E(expr: Decimal, r: int) -> Decimal:
    log2 = Decimal(2).ln()
    return (expr.ln() / log2) / (Decimal(r).ln() / log2)


def verify_factorization_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Independently verify one branch factorization record from path A JSON."""
    n = int(record["n"])
    prime_powers = {int(p): int(e) for p, e in record["prime_powers"].items()}
    unfactored = record.get("unfactored_cofactor")
    if unfactored is not None:
        unfactored = int(unfactored)

    prod = 1
    prime_ok = True
    prime_results = {}
    for p, e in sorted(prime_powers.items()):
        ok = _is_probable_prime(p)
        prime_results[str(p)] = ok
        if not ok or e < 1:
            prime_ok = False
        prod *= p**e
    if unfactored is not None:
        prod *= unfactored
        # Cofactor must be composite under stated tests when present.
        cof_prime = _is_probable_prime(unfactored)
        cofactor_ok = unfactored > 1 and (not cof_prime)
    else:
        cof_prime = None
        cofactor_ok = True

    product_ok = prod == n
    return {
        "n": n,
        "product_recomputed": prod,
        "product_check": product_ok,
        "all_reported_factors_prime": prime_ok,
        "factor_primality": prime_results,
        "unfactored_cofactor": unfactored,
        "unfactored_is_prime": cof_prime,
        "unfactored_declared_composite_ok": cofactor_ok,
        "accepted": product_ok and prime_ok and cofactor_ok,
    }


def recompute_E(
    r: int,
    r_minus_1_record: Dict[str, Any],
    r_plus_1_record: Dict[str, Any],
) -> Dict[str, Any]:
    """Recompute E(r) or E_bound from factor lists without importing e_eval."""
    v_m = verify_factorization_record(r_minus_1_record)
    v_p = verify_factorization_record(r_plus_1_record)

    pp_m = {int(p): int(e) for p, e in r_minus_1_record["prime_powers"].items()}
    pp_p = {int(p): int(e) for p, e in r_plus_1_record["prime_powers"].items()}
    uf_m = r_minus_1_record.get("unfactored_cofactor")
    uf_p = r_plus_1_record.get("unfactored_cofactor")
    if uf_m is not None:
        uf_m = int(uf_m)
    if uf_p is not None:
        uf_p = int(uf_p)

    best = None
    largest = 1
    sqrt_r = isqrt(r)
    branch_mins = {}
    for branch, m, pp, uf in (
        ("r-1", r - 1, pp_m, uf_m),
        ("r+1", r + 1, pp_p, uf_p),
    ):
        local_best = None
        for d in _divisors(pp, uf):
            if d <= sqrt_r and d > largest:
                largest = d
            ex = _expr(d, m)
            e_val = _E(ex, r)
            cand = {
                "branch": branch,
                "d": d,
                "expr": str(ex),
                "E": str(e_val),
                "E_float64": float(e_val),
            }
            if local_best is None or e_val < Decimal(local_best["E"]):
                local_best = cand
            if best is None or e_val < Decimal(best["E"]):
                best = cand
        branch_mins[branch] = local_best

    complete = uf_m is None and uf_p is None and v_m["accepted"] and v_p["accepted"]
    out: Dict[str, Any] = {
        "r": r,
        "verification_r_minus_1": v_m,
        "verification_r_plus_1": v_p,
        "factor_lists_accepted": v_m["accepted"] and v_p["accepted"],
        "minimizing": best,
        "branch_minimizing": branch_mins,
        "largest_divisor_le_sqrt_r": largest,
        "largest_divisor_le_sqrt_r_bits": largest.bit_length(),
        "complete_factorizations": complete,
        "quantity_kind": "E(r)" if complete else "E_bound",
        "precision_decimal_digits": getcontext().prec,
        "evaluator": "factor_path_b.recompute_E (independent Decimal path)",
    }
    if best is not None:
        if complete:
            out["E_r"] = best["E"]
            out["E_r_float64"] = best["E_float64"]
        else:
            out["E_bound"] = best["E"]
            out["E_bound_float64"] = best["E_float64"]
    return out


def agree_with_primary(primary: Dict[str, Any], recomputed: Dict[str, Any], *, atol: float = 1e-12) -> Dict[str, Any]:
    """Compare primary e_eval result with path-B recomputation."""
    if not recomputed.get("factor_lists_accepted"):
        return {
            "agree": False,
            "reason": "factor_list_rejected_by_path_b",
            "recomputed": recomputed,
        }
    pk = primary.get("quantity_kind")
    rk = recomputed.get("quantity_kind")
    if pk != rk:
        return {"agree": False, "reason": f"quantity_kind_mismatch {pk} vs {rk}"}

    def _val(doc: Dict[str, Any]) -> float:
        if doc.get("quantity_kind") == "E(r)":
            return float(doc.get("E_r_float64", doc.get("E_r")))
        return float(doc.get("E_bound_float64", doc.get("E_bound")))

    pv = _val(primary)
    rv = _val(recomputed)
    pmin = primary.get("minimizing", {})
    rmin = recomputed.get("minimizing", {})
    d_match = int(pmin.get("d", -1)) == int(rmin.get("d", -2))
    branch_match = pmin.get("branch") == rmin.get("branch")
    e_match = abs(pv - rv) <= atol
    return {
        "agree": bool(e_match and d_match and branch_match and recomputed.get("factor_lists_accepted")),
        "primary_value": pv,
        "recomputed_value": rv,
        "abs_diff": abs(pv - rv),
        "minimizing_d_match": d_match,
        "minimizing_branch_match": branch_match,
        "atol": atol,
    }
