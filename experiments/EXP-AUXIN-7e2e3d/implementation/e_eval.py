"""Primary E(r) evaluator for EXP-AUXIN-7e2e3d (path A arithmetic).

E(r) = min over admissible (m, d) of log2(sqrt(m/d) + sqrt(d)) / log2(r)
with m in {r-1, r+1} and d a positive divisor of m.

Uses decimal arithmetic at >= 80 bits of precision. MODELLED quantity:
applies the frozen DEC-20260802-204 closed form to measured divisor lattices.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from math import isqrt
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# >= 80 bits (~24 decimal digits); use 80 decimal digits for headroom.
getcontext().prec = 80

BranchName = str  # "r-1" | "r+1"


def expr_decimal(d: int, m: int) -> Decimal:
    """expr(d, m) = sqrt(m/d) + sqrt(d), Decimal."""
    if d <= 0 or m <= 0 or m % d != 0:
        raise ValueError("d must be a positive divisor of m")
    dd = Decimal(d)
    md = Decimal(m) / dd
    return md.sqrt() + dd.sqrt()


def e_from_expr(expr: Decimal, r: int) -> Decimal:
    """log2(expr) / log2(r)."""
    if r <= 1:
        raise ValueError("r must be > 1")
    if expr <= 0:
        raise ValueError("expr must be positive")
    log2 = Decimal(2).ln()
    return (expr.ln() / log2) / (Decimal(r).ln() / log2)


def modelled_log_cofactor(expr: Decimal, r: int) -> Decimal:
    """Optional MODELLED column: log2(log2(r) * expr) / log2(r). Never mixed into E(r)."""
    log2 = Decimal(2).ln()
    log2_r = Decimal(r).ln() / log2
    return ((log2_r * expr).ln() / log2) / log2_r


def divisors_from_prime_powers(
    prime_powers: Dict[int, int],
    unfactored_cofactor: Optional[int] = None,
) -> List[int]:
    """Enumerate positive divisors from a partial factorization.

    If an unfactored cofactor C remains with m = F * C, the known divisor
    set is {d : d|F} ∪ {d*C : d|F}. C itself is included (d=1 case).
    """
    primes = sorted(int(p) for p in prime_powers.keys())
    expos = [int(prime_powers[p]) for p in primes]
    divs = [1]
    for p, e in zip(primes, expos):
        if e < 0 or p <= 1:
            raise ValueError("invalid prime power")
        growth: List[int] = []
        pe = 1
        for _ in range(e):
            pe *= p
            for d in divs:
                growth.append(d * pe)
        divs.extend(growth)
    if unfactored_cofactor is not None:
        c = int(unfactored_cofactor)
        if c <= 1:
            raise ValueError("unfactored cofactor must be > 1")
        extra = [d * c for d in divs]
        divs = sorted(set(divs + extra))
    else:
        divs = sorted(divs)
    return divs


def evaluate_branch(
    r: int,
    branch: BranchName,
    m: int,
    prime_powers: Dict[int, int],
    unfactored_cofactor: Optional[int],
) -> Dict[str, Any]:
    """Evaluate expr/E over known divisors of one branch."""
    divs = divisors_from_prime_powers(prime_powers, unfactored_cofactor)
    sqrt_r = isqrt(r)
    best: Optional[Dict[str, Any]] = None
    largest_div_le_sqrt: int = 1
    per_divisor: List[Dict[str, Any]] = []
    for d in divs:
        if d <= sqrt_r and d > largest_div_le_sqrt:
            largest_div_le_sqrt = d
        ex = expr_decimal(d, m)
        e_val = e_from_expr(ex, r)
        row = {
            "d": d,
            "d_hex": format(d, "x"),
            "d_bits": d.bit_length(),
            "expr": str(ex),
            "E": str(e_val),
            "E_float64": float(e_val),
        }
        per_divisor.append(row)
        if best is None or e_val < Decimal(best["E"]):
            best = {
                "branch": branch,
                "d": d,
                "d_hex": format(d, "x"),
                "d_bits": d.bit_length(),
                "expr": str(ex),
                "E": str(e_val),
                "E_float64": float(e_val),
                "MODELLED_LOG_COFACTOR": str(modelled_log_cofactor(ex, r)),
            }
    assert best is not None
    return {
        "branch": branch,
        "m": m,
        "m_hex": format(m, "x"),
        "divisor_count_known": len(divs),
        "unfactored_cofactor": unfactored_cofactor,
        "unfactored_cofactor_bits": None if unfactored_cofactor is None else unfactored_cofactor.bit_length(),
        "complete_divisor_lattice": unfactored_cofactor is None,
        "minimizing": best,
        "largest_divisor_le_sqrt_r": largest_div_le_sqrt,
        "largest_divisor_le_sqrt_r_bits": largest_div_le_sqrt.bit_length(),
        # Keep per-divisor detail out of default table; available for audits.
        "per_divisor_count": len(per_divisor),
    }


def evaluate_E(
    r: int,
    factorization_r_minus_1: Dict[str, Any],
    factorization_r_plus_1: Dict[str, Any],
) -> Dict[str, Any]:
    """Combine both branches into E(r) or E_bound.

    factorization_* must carry:
      prime_powers: {p: e} with int keys/values (or stringified ints)
      unfactored_cofactor: int | None
      product_check: bool
    """
    def _pp(raw: Dict[Any, Any]) -> Dict[int, int]:
        return {int(p): int(e) for p, e in raw.items()}

    rm = r - 1
    rp = r + 1
    pp_m = _pp(factorization_r_minus_1["prime_powers"])
    pp_p = _pp(factorization_r_plus_1["prime_powers"])
    uf_m = factorization_r_minus_1.get("unfactored_cofactor")
    uf_p = factorization_r_plus_1.get("unfactored_cofactor")
    if uf_m is not None:
        uf_m = int(uf_m)
    if uf_p is not None:
        uf_p = int(uf_p)

    b_m = evaluate_branch(r, "r-1", rm, pp_m, uf_m)
    b_p = evaluate_branch(r, "r+1", rp, pp_p, uf_p)

    cand = [b_m["minimizing"], b_p["minimizing"]]
    overall = min(cand, key=lambda x: Decimal(x["E"]))

    complete = (
        uf_m is None
        and uf_p is None
        and bool(factorization_r_minus_1.get("product_check"))
        and bool(factorization_r_plus_1.get("product_check"))
    )
    e_float = float(Decimal(overall["E"]))
    result: Dict[str, Any] = {
        "r": r,
        "r_hex": format(r, "x"),
        "r_bits": r.bit_length(),
        "rho_baseline": 0.5,
        "branches": {"r-1": b_m, "r+1": b_p},
        "minimizing": overall,
        "complete_factorizations": complete,
        "quantity_kind": "E(r)" if complete else "E_bound",
        "bound_direction": None
        if complete
        else (
            "upper_bound_on_true_E_r: min over known divisors only; "
            "true E(r) <= reported value (unknown factors of cofactors "
            "could only add divisors and possibly lower E)"
        ),
    }
    if complete:
        result["E_r"] = overall["E"]
        result["E_r_float64"] = e_float
    else:
        result["E_bound"] = overall["E"]
        result["E_bound_float64"] = e_float
    # Largest divisor below sqrt(r) across both branches.
    largest = max(
        b_m["largest_divisor_le_sqrt_r"],
        b_p["largest_divisor_le_sqrt_r"],
    )
    result["largest_divisor_le_sqrt_r"] = largest
    result["largest_divisor_le_sqrt_r_bits"] = largest.bit_length()
    return result


def recover_planted_d(r: int, d_expected: int, factorization_r_minus_1: Dict[str, Any]) -> bool:
    """True if d_expected divides r-1 in the reported factorization lattice."""
    pp = {int(p): int(e) for p, e in factorization_r_minus_1["prime_powers"].items()}
    uf = factorization_r_minus_1.get("unfactored_cofactor")
    if uf is not None:
        uf = int(uf)
    return d_expected in divisors_from_prime_powers(pp, uf)
