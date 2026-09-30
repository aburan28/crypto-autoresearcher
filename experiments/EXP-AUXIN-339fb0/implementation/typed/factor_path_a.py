"""Factorization path A for EXP-AUXIN-339fb0 (PARI/cypari2 + GMP-ECM).

Implements change.D6_factoring stages F0–F3 and certificate production hooks
(change.D7_certificates.producing_library). Third-party imports (cypari2,
cysignals) are LAZY so packaging-check runs without requiring them installed.

Never imports factor_path_b factorization internals.
Never recovers a discrete logarithm and never runs Cheon.
Never opens any path under experiments/EXP-AUXIN-7e2e3d/.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass, field
from math import isqrt
from typing import Any, Dict, List, Optional, Tuple

# Declared ECM ladder (change.D6_factoring.ecm_curves_per_level).
ECM_LADDER: List[Tuple[int, int]] = [
    (2_000, 25),
    (11_000, 90),
    (50_000, 300),
    (250_000, 700),
    (1_000_000, 1800),
    (3_000_000, 5100),
    (11_000_000, 10600),
    (43_000_000, 19300),
    (110_000_000, 49000),
    (260_000_000, 124000),
    (850_000_000, 210000),
]

TRIAL_BOUND = 1 << 24
F2_BIT_ROUTE = 272
FACTORING_BUDGET_S = 3600
PARI_STACK_SIZE = 2**27
PARI_STACK_MAX = 2**32


@dataclass
class FactorPart:
    value: int
    stage: str
    seconds: float = 0.0
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FactorResult:
    n: int
    prime_powers: Dict[int, int]
    recorded_parts: List[int]
    complete: bool
    product_check: bool
    wall_seconds: float
    parts_trace: List[Dict[str, Any]]
    ecm_curves: List[Dict[str, Any]]
    method_trace: List[str]

    def to_json(self) -> Dict[str, Any]:
        return {
            "n": self.n,
            "n_bits": self.n.bit_length(),
            "prime_powers": {str(p): e for p, e in sorted(self.prime_powers.items())},
            "recorded_parts": self.recorded_parts,
            "complete": self.complete,
            "product_check": self.product_check,
            "wall_seconds": self.wall_seconds,
            "parts_trace": self.parts_trace,
            "ecm_curves": self.ecm_curves,
            "method_trace": self.method_trace,
            "path": "A",
            "backend": "cypari2+gmp-ecm",
        }


def _product(prime_powers: Dict[int, int], parts: List[int]) -> int:
    prod = 1
    for p, e in prime_powers.items():
        prod *= int(p) ** int(e)
    for c in parts:
        prod *= int(c)
    return prod


def _small_primes_upto(limit: int) -> List[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]


_SMALL_PRIMES: Optional[List[int]] = None


def small_primes() -> List[int]:
    global _SMALL_PRIMES
    if _SMALL_PRIMES is None:
        # Packaging / F0 uses primes below 2^16 for sieve build; F0 itself
        # trial-divides by every prime below 2^24 via incremental generation.
        _SMALL_PRIMES = _small_primes_upto(1 << 16)
    return _SMALL_PRIMES


def _get_pari():
    """Lazy cypari2 Pari(size=2**27, sizemax=2**32) per RI-7."""
    import cypari2  # class-b third-party; recorded in manifest.yaml

    return cypari2.Pari(size=PARI_STACK_SIZE, sizemax=PARI_STACK_MAX)


def trial_divide_f0(n: int) -> Tuple[Dict[int, int], int]:
    """F0: trial division by every prime below 2^24."""
    n = int(n)
    powers: Dict[int, int] = {}
    # Incremental sieve / wheel for primes < 2^24 without storing all of them.
    if n % 2 == 0:
        e = 0
        while n % 2 == 0:
            n //= 2
            e += 1
        powers[2] = e
    p = 3
    bound = TRIAL_BOUND
    while p < bound and p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            powers[p] = powers.get(p, 0) + e
        p += 2
    # Finish primes between isqrt(n) and bound when n still large.
    while p < bound and n > 1:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            powers[p] = powers.get(p, 0) + e
        p += 2
    return powers, n


def is_perfect_power(n: int) -> Optional[Tuple[int, int]]:
    """Return (base, exp) if n = base**exp with exp>=2, else None."""
    n = int(n)
    if n < 4:
        return None
    max_e = n.bit_length()
    for e in range(max_e, 1, -1):
        # integer e-th root via binary search
        lo, hi = 1, 1 << ((n.bit_length() // e) + 2)
        while lo < hi:
            mid = (lo + hi) // 2
            pwr = mid**e
            if pwr == n:
                return mid, e
            if pwr < n:
                lo = mid + 1
            else:
                hi = mid
    return None


def factor_budgeted(n: int, budget_s: float = FACTORING_BUDGET_S) -> FactorResult:
    """Run F0–F3 under the monotonic wall-clock budget.

    Packaging note: full F2/F3 require cypari2 and the ecm binary. Callers that
    only need packaging-check must not invoke this function.
    """
    t0 = time.monotonic()
    remaining = float(budget_s)
    method: List[str] = []
    parts_trace: List[Dict[str, Any]] = []
    ecm_curves: List[Dict[str, Any]] = []
    prime_powers: Dict[int, int] = {}
    composites: List[int] = []

    def charged(dt: float) -> None:
        nonlocal remaining
        remaining -= dt
        if remaining < 0:
            remaining = 0.0

    # F0
    t_f0 = time.monotonic()
    pp, rem = trial_divide_f0(n)
    dt = time.monotonic() - t_f0
    charged(dt)
    prime_powers.update(pp)
    method.append(f"F0:{dt:.6f}s")
    parts_trace.append(
        {"value": rem if rem > 1 else n, "stage": "F0", "seconds": dt, "removed": pp}
    )
    if rem == 1:
        wall = time.monotonic() - t0
        return FactorResult(
            n=n,
            prime_powers=prime_powers,
            recorded_parts=[],
            complete=True,
            product_check=_product(prime_powers, []) == n,
            wall_seconds=wall,
            parts_trace=parts_trace,
            ecm_curves=ecm_curves,
            method_trace=method,
        )
    work = [rem]

    pari = _get_pari()
    while work and remaining >= 1.0:
        part = work.pop(0)
        # Perfect power
        ppw = is_perfect_power(part)
        if ppw is not None:
            base, exp = ppw
            work.append(base)
            method.append(f"F1-perfect-power:{part}={base}^{exp}")
            # Defer multiplicity: factor base once, multiply exponents later by
            # re-inserting base exp times conceptually via recorded multiplicity.
            for _ in range(exp - 1):
                work.append(base)
            continue
        # Primality screen + certificate deferred to caller; here use PARI isprime.
        t_p = time.monotonic()
        try:
            is_p = bool(pari.isprime(part))
        except Exception as exc:  # pragma: no cover - infra
            method.append(f"F1-isprime-error:{exc}")
            composites.append(part)
            break
        dt = time.monotonic() - t_p
        charged(dt)
        if is_p:
            prime_powers[part] = prime_powers.get(part, 0) + 1
            method.append(f"F1-prime:{part}")
            continue
        bits = part.bit_length()
        if bits <= F2_BIT_ROUTE:
            # F2: alarm(A, factor(n))
            A = int(remaining)
            if A < 1:
                composites.append(part)
                break
            t_f2 = time.monotonic()
            try:
                from cysignals.signals import AlarmInterrupt

                fac = pari(f"alarm({A}, factor({part}))")
                dt = time.monotonic() - t_f2
                charged(dt)
                method.append(f"F2:{dt:.6f}s")
                # Parse PARI factor matrix
                mat = fac
                nrows = int(mat.nrows())
                for i in range(nrows):
                    p_i = int(mat[i, 0])
                    e_i = int(mat[i, 1])
                    prime_powers[p_i] = prime_powers.get(p_i, 0) + e_i
            except AlarmInterrupt:
                dt = time.monotonic() - t_f2
                charged(dt)
                method.append(f"F2-alarm:{dt:.6f}s")
                composites.append(part)
            except Exception as exc:
                dt = time.monotonic() - t_f2
                charged(dt)
                method.append(f"F2-error:{exc}")
                composites.append(part)
        else:
            # F3: GMP-ECM ladder
            if shutil.which("ecm") is None:
                method.append("F3-ecm-absent")
                composites.append(part)
                break
            cur = part
            ladder_idx = 0
            while cur > 1 and remaining >= 1.0:
                if ladder_idx < len(ECM_LADDER):
                    B1, curves = ECM_LADDER[ladder_idx]
                else:
                    B1, curves = ECM_LADDER[-1]
                t_f3 = time.monotonic()
                try:
                    proc = subprocess.run(
                        ["ecm", "-one", "-c", str(curves), str(B1)],
                        input=f"{cur}\n",
                        capture_output=True,
                        text=True,
                        timeout=max(1.0, remaining),
                    )
                except subprocess.TimeoutExpired:
                    dt = time.monotonic() - t_f3
                    charged(dt)
                    method.append(f"F3-kill:{dt:.6f}s")
                    composites.append(cur)
                    cur = 1
                    break
                dt = time.monotonic() - t_f3
                charged(dt)
                ecm_curves.append(
                    {
                        "B1": B1,
                        "curves": curves,
                        "seconds": dt,
                        "returncode": proc.returncode,
                        "stdout_tail": (proc.stdout or "")[-500:],
                    }
                )
                # Parse decimal factors from stdout.
                found = []
                for line in (proc.stdout or "").splitlines():
                    line = line.strip()
                    if line.isdigit():
                        fac_n = int(line)
                        if 1 < fac_n < cur and cur % fac_n == 0:
                            found.append(fac_n)
                if found:
                    for fac_n in found:
                        other = cur // fac_n
                        work.append(fac_n)
                        if other > 1:
                            work.append(other)
                        cur = 1
                    break
                ladder_idx += 1
            if cur > 1:
                composites.append(cur)

    wall = time.monotonic() - t0
    complete = len(composites) == 0
    prod_ok = _product(prime_powers, composites) == n
    return FactorResult(
        n=n,
        prime_powers=prime_powers,
        recorded_parts=composites,
        complete=complete,
        product_check=prod_ok,
        wall_seconds=wall,
        parts_trace=parts_trace,
        ecm_curves=ecm_curves,
        method_trace=method,
    )


def packaging_surface() -> Dict[str, Any]:
    """Symbols and constants exposed for packaging-check (no factoring)."""
    return {
        "path": "A",
        "trial_bound": TRIAL_BOUND,
        "f2_bit_route": F2_BIT_ROUTE,
        "factoring_budget_s": FACTORING_BUDGET_S,
        "ecm_ladder_levels": len(ECM_LADDER),
        "pari_stack": {"size": PARI_STACK_SIZE, "sizemax": PARI_STACK_MAX},
        "lazy_third_party": ["cypari2", "cysignals"],
    }
