"""Factorization path A for EXP-AUXIN-7e2e3d.

Budgeted factorization of integers (r-1 / r+1) using sympy.factorint with an
explicit wall-clock budget. Emits prime-power maps, optional unfactored
cofactors, product checks, and BPSW-style primality certificates
(sympy.isprime).

Never recovers a discrete logarithm and never runs Cheon.
"""

from __future__ import annotations

import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from sympy import factorint, isprime

BACKEND_NAME = "sympy.factorint"
BACKEND_VERSION = None  # filled at import from sympy.__version__
try:
    import sympy as _sympy

    BACKEND_VERSION = _sympy.__version__
except Exception:  # pragma: no cover
    BACKEND_VERSION = "unknown"

DEFAULT_TRIAL_LIMIT = 10**7
DEFAULT_DEEP_BIT_CAP = 280


@dataclass
class FactorResult:
    n: int
    prime_powers: Dict[int, int]
    unfactored_cofactor: Optional[int]
    product_check: bool
    primality_certificates: Dict[str, Any]
    wall_seconds: float
    method_trace: list
    complete: bool

    def to_json(self) -> Dict[str, Any]:
        return {
            "n": self.n,
            "n_hex": format(self.n, "x"),
            "n_bits": self.n.bit_length(),
            "prime_powers": {str(p): e for p, e in sorted(self.prime_powers.items())},
            "prime_powers_hex": {
                format(p, "x"): e for p, e in sorted(self.prime_powers.items())
            },
            "unfactored_cofactor": self.unfactored_cofactor,
            "unfactored_cofactor_hex": None
            if self.unfactored_cofactor is None
            else format(self.unfactored_cofactor, "x"),
            "unfactored_cofactor_bits": None
            if self.unfactored_cofactor is None
            else self.unfactored_cofactor.bit_length(),
            "product_check": self.product_check,
            "complete": self.complete,
            "primality_certificates": self.primality_certificates,
            "wall_seconds": self.wall_seconds,
            "method_trace": self.method_trace,
            "backend": {
                "name": BACKEND_NAME,
                "version": BACKEND_VERSION,
                "command": "sympy.factorint / sympy.isprime (BPSW / deterministic MR)",
            },
        }


def _product(prime_powers: Dict[int, int], unfactored: Optional[int]) -> int:
    prod = 1
    for p, e in prime_powers.items():
        prod *= int(p) ** int(e)
    if unfactored is not None:
        prod *= int(unfactored)
    return prod


def _certify_primes(prime_powers: Dict[int, int]) -> Dict[str, Any]:
    certs = {}
    for p in sorted(prime_powers):
        ok = bool(isprime(int(p)))
        certs[str(p)] = {
            "method": "sympy.isprime (BPSW / deterministic Miller-Rabin for this size)",
            "is_prime": ok,
        }
    return certs


def _split_limited(n: int, trial_limit: int) -> Tuple[Dict[int, int], Optional[int], list]:
    """Trial-bounded factorint; classify leftover as prime or unfactored composite."""
    trace = [f"factorint(limit={trial_limit})"]
    raw = factorint(n, limit=trial_limit)
    primes: Dict[int, int] = {}
    rem = n
    for p in sorted(raw):
        p = int(p)
        if not isprime(p):
            continue
        e = 0
        while rem % p == 0:
            rem //= p
            e += 1
        if e:
            primes[p] = e
            trace.append(f"accepted_prime_bits={p.bit_length()} e={e}")
    unfactored = None
    if rem > 1:
        if isprime(rem):
            primes[rem] = primes.get(rem, 0) + 1
            trace.append(f"cofactor_is_prime bits={rem.bit_length()}")
        else:
            unfactored = rem
            trace.append(f"unfactored_composite bits={rem.bit_length()}")
    return primes, unfactored, trace


def _deep_worker(n: int, q: mp.Queue) -> None:
    try:
        q.put(("ok", factorint(n)))
    except Exception as exc:  # pragma: no cover
        q.put(("err", str(exc)))


def _deep_factor(n: int, budget_seconds: float) -> Optional[Dict[int, int]]:
    if budget_seconds <= 1.0:
        return None
    q: mp.Queue = mp.Queue()
    proc = mp.Process(target=_deep_worker, args=(n, q))
    proc.start()
    proc.join(budget_seconds)
    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
            proc.join(2)
        return None
    if q.empty():
        return None
    status, payload = q.get()
    if status != "ok" or not isinstance(payload, dict):
        return None
    out: Dict[int, int] = {}
    for p, e in payload.items():
        p = int(p)
        e = int(e)
        if not isprime(p):
            return None
        out[p] = e
    return out


def factor_integer(
    n: int,
    *,
    budget_seconds: float = 3600.0,
    trial_limit: int = DEFAULT_TRIAL_LIMIT,
    deep_bit_cap: int = DEFAULT_DEEP_BIT_CAP,
) -> FactorResult:
    """Factor n under a wall-clock budget. Partial factorizations are allowed."""
    if n <= 0:
        raise ValueError("n must be positive")
    t0 = time.perf_counter()
    primes, unfactored, trace = _split_limited(n, trial_limit)

    if unfactored is not None and unfactored.bit_length() <= deep_bit_cap:
        elapsed = time.perf_counter() - t0
        remaining = budget_seconds - elapsed
        # Spend up to remaining budget (cap deep attempt reasonably inside budget).
        deep_budget = max(0.0, remaining)
        if deep_budget > 1.0:
            trace.append(
                f"deep_factorint bits={unfactored.bit_length()} budget_s={deep_budget:.1f}"
            )
            deep = _deep_factor(unfactored, deep_budget)
            if deep is not None:
                rem = unfactored
                ok = True
                for p, e in sorted(deep.items()):
                    for _ in range(e):
                        if rem % p != 0:
                            ok = False
                            break
                        rem //= p
                    if not ok:
                        break
                    primes[p] = primes.get(p, 0) + e
                if ok and rem == 1:
                    unfactored = None
                    trace.append("deep_factor_complete")
                elif ok and rem > 1 and isprime(rem):
                    primes[rem] = primes.get(rem, 0) + 1
                    unfactored = None
                    trace.append("deep_factor_complete_with_prime_rem")
                elif ok and rem > 1:
                    unfactored = rem
                    trace.append(f"deep_partial rem_bits={rem.bit_length()}")
                else:
                    trace.append("deep_factor_rejected")
            else:
                trace.append("deep_factor_timeout_or_fail")

    # Enforce budget: even if deep returned, we stop here.
    wall = time.perf_counter() - t0
    if wall > budget_seconds and unfactored is None:
        # Should not happen often; keep result.
        trace.append(f"note_wall_exceeded_after_complete wall={wall:.2f}")

    prod = _product(primes, unfactored)
    product_check = prod == n
    complete = unfactored is None and product_check
    certs = _certify_primes(primes)
    if unfactored is not None:
        certs["unfactored_cofactor"] = {
            "method": "sympy.isprime",
            "is_prime": bool(isprime(unfactored)),
            "declared_composite": not bool(isprime(unfactored)),
            "value_bits": unfactored.bit_length(),
        }

    return FactorResult(
        n=n,
        prime_powers=primes,
        unfactored_cofactor=unfactored,
        product_check=product_check,
        primality_certificates=certs,
        wall_seconds=wall,
        method_trace=trace,
        complete=complete,
    )


def factor_r_pm_1(
    r: int,
    *,
    budget_seconds_per_integer: float = 3600.0,
) -> Dict[str, Any]:
    """Factor both r-1 and r+1. Returns a JSON-serializable record."""
    rm = factor_integer(r - 1, budget_seconds=budget_seconds_per_integer)
    rp = factor_integer(r + 1, budget_seconds=budget_seconds_per_integer)
    return {
        "r": r,
        "r_hex": format(r, "x"),
        "r_minus_1": rm.to_json(),
        "r_plus_1": rp.to_json(),
    }
