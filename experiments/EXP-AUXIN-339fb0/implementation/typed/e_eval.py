"""Typed cost evaluator for EXP-AUXIN-339fb0 (stdlib Decimal, >= 150 digits).

Implements definitions.typed_costs, analytic_floors_and_ceiling, depth, bins,
minimiser_and_ties, and floor_invariant checks from the frozen successor contract.

Path-B arithmetic (and packaging scaffolding) uses this module. Path A may call
the same closed forms or evaluate via PARI at the same precision floor; both
paths must agree within 10^-50 absolute on reported exponents/bounds.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from math import isqrt
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# definitions.precision: at least 150 significant decimal digits.
getcontext().prec = 160

TAU = Decimal("1e-45")
TIE_REL = Decimal("1e-100")
FLOOR_SLACK = Decimal("1e-45")
PATH_TOL = Decimal("1e-50")
LOG2 = Decimal(2).ln()


def _D(x: Any) -> Decimal:
    if isinstance(x, Decimal):
        return x
    return Decimal(int(x)) if isinstance(x, int) else Decimal(str(x))


def log2(x: Decimal) -> Decimal:
    return x.ln() / LOG2


def T_minus(d: int, m_minus: int) -> Decimal:
    """T_minus(d) = sqrt(m/d) + sqrt(d)."""
    d = int(d)
    m = int(m_minus)
    if d <= 0 or m % d != 0:
        raise ValueError("d must be a positive divisor of m_minus")
    dd = _D(d)
    return (Decimal(m) / dd).sqrt() + dd.sqrt()


def T_plus(d: int, m_plus: int) -> Decimal:
    """T_plus(d) = sqrt(m/d) + d  (Theorem 2 leading expression)."""
    d = int(d)
    m = int(m_plus)
    if d <= 0 or m % d != 0:
        raise ValueError("d must be a positive divisor of m_plus")
    dd = _D(d)
    return (Decimal(m) / dd).sqrt() + dd


def e_of(T: Decimal, r: int) -> Decimal:
    """e = log2(T) / log2(r)."""
    r = int(r)
    if r <= 1 or T <= 0:
        raise ValueError("bad e_of arguments")
    return log2(T) / log2(_D(r))


def F_minus(r: int) -> Decimal:
    """Analytic floor on the minus branch."""
    r = int(r)
    return (Decimal(1) + log2(_D(r - 1)) / 4) / log2(_D(r))


def F_plus(r: int) -> Decimal:
    """Analytic floor on the plus branch (T_plus optimum)."""
    r = int(r)
    return (log2(Decimal(3)) - Decimal(2) / 3 + log2(_D(r + 1)) / 3) / log2(_D(r))


def C_branch(r: int, m_b: int) -> Decimal:
    """Ceiling value at d=1: log2(sqrt(m)+1)/log2(r)."""
    r = int(r)
    return log2(_D(m_b).sqrt() + Decimal(1)) / log2(_D(r))


def depth(e: Decimal, r: int, branch: str) -> Decimal:
    m = (r - 1) if branch == "minus" else (r + 1)
    F = F_minus(r) if branch == "minus" else F_plus(r)
    C = C_branch(r, m)
    denom = C - F
    if denom == 0:
        raise ValueError("degenerate depth denominator")
    return (C - e) / denom


def bin_exact(s: Decimal) -> Tuple[str, str, bool]:
    """Return (bin, bin_at_least, boundary_flag) for an EXACT depth s."""
    boundary = abs(s - Decimal("0.25")) <= TAU or abs(s - Decimal("0.75")) <= TAU
    if s >= Decimal("0.75") + TAU:
        return "NEAR_FLOOR", "NEAR_FLOOR", boundary
    if s <= Decimal("0.25") - TAU:
        return "NEAR_CEILING", "NEAR_CEILING", boundary
    if abs(s - Decimal("0.75")) <= TAU:
        return "INTERMEDIATE", "INTERMEDIATE", True
    if abs(s - Decimal("0.25")) <= TAU:
        return "NEAR_CEILING", "NEAR_CEILING", True
    return "INTERMEDIATE", "INTERMEDIATE", boundary


def bin_bound(s: Decimal) -> Tuple[str, str, bool]:
    """BOUND binning per corrective.bin_by_status / D3."""
    _, exact_bin, boundary = bin_exact(s)
    if (not boundary) and s >= Decimal("0.75") + TAU:
        return "NEAR_FLOOR", "NEAR_FLOOR", False
    return "UNDETERMINED", exact_bin, boundary


def divisors_from_prime_powers(
    prime_powers: Dict[int, int],
    recorded_parts: Optional[Sequence[int]] = None,
) -> List[int]:
    """Enumerate positive divisors from certified prime powers.

    If recorded_parts (BOUND composite parts) is given, build W_b =
    {e * prod(S) : e|F, S subset of parts} with F = product of prime powers.
    """
    primes = sorted(int(p) for p in prime_powers.keys())
    divs = [1]
    for p in primes:
        e = int(prime_powers[p])
        growth: List[int] = []
        pe = 1
        for _ in range(e):
            pe *= p
            for d in divs:
                growth.append(d * pe)
        divs.extend(growth)
    if not recorded_parts:
        return sorted(divs)
    parts = [int(c) for c in recorded_parts]
    # All subset products of parts.
    subset_prods = [1]
    for c in parts:
        subset_prods = subset_prods + [s * c for s in subset_prods]
    out: Set[int] = set()
    for e in divs:
        for sp in subset_prods:
            out.add(e * sp)
    return sorted(out)


def choose_minimiser(
    candidates: Iterable[Tuple[int, Decimal]],
) -> Tuple[int, Decimal]:
    """Smallest tied divisor under relative tie tolerance TIE_REL."""
    items = list(candidates)
    if not items:
        raise ValueError("empty candidate set")
    e_star = min(e for _, e in items)
    tied = [d for d, e in items if e - e_star <= TIE_REL * e_star]
    d_star = min(tied)
    return d_star, e_star


def evaluate_branch(
    r: int,
    branch: str,
    prime_powers: Dict[int, int],
    recorded_parts: Optional[Sequence[int]] = None,
    status_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate one branch (minus|plus) under EXACT or BOUND divisor sets."""
    r = int(r)
    if branch not in ("minus", "plus"):
        raise ValueError("branch must be minus|plus")
    m = r - 1 if branch == "minus" else r + 1
    complete = not recorded_parts
    status = status_hint or ("EXACT" if complete else "BOUND")
    divs = divisors_from_prime_powers(prime_powers, recorded_parts)
    scored: List[Tuple[int, Decimal]] = []
    for d in divs:
        T = T_minus(d, m) if branch == "minus" else T_plus(d, m)
        if branch == "plus" and T < _D(d) - FLOOR_SLACK:
            raise ValueError(f"floor_invariant T_plus(d)<d at d={d}")
        scored.append((d, e_of(T, r)))
    d_star, e_star = choose_minimiser(scored)
    F = F_minus(r) if branch == "minus" else F_plus(r)
    if e_star < F - FLOOR_SLACK:
        raise ValueError(f"floor_invariant e < F on {branch}")
    s = depth(e_star, r, branch)
    if status == "EXACT":
        b, bal, bf = bin_exact(s)
        return {
            "branch": branch,
            "status": "EXACT",
            "exponent": str(e_star),
            "minimiser_d": d_star,
            "bits_of_d": d_star.bit_length(),
            "floor": str(F),
            "depth": str(s),
            "bin": b,
            "bin_at_least": bal,
            "boundary_flag": bf,
            "witness_set_size": len(divs),
        }
    # BOUND: upper = e_star, lower = F
    b, bal, bf = bin_bound(s)
    return {
        "branch": branch,
        "status": "BOUND",
        "upper_bound": str(e_star),
        "lower_bound": str(F),
        "witness_d": d_star,
        "bits_of_d": d_star.bit_length(),
        "depth": str(s),
        "bin": b,
        "bin_at_least": bal,
        "boundary_flag": bf,
        "witness_set": divs,
        "witness_set_size": len(divs),
    }


def agree_within(a: Decimal, b: Decimal, tol: Decimal = PATH_TOL) -> bool:
    return abs(a - b) <= tol
