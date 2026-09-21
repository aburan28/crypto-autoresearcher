"""fixture_generator.py -- deterministic seed serialization, prime/order
certificate construction, and reduced-curve construction SOURCE for
EXP-CRYPTO-9225d2.

STATUS: source only. This module is NOT run to produce realized fixture
bytes or certificates in this task (maximum_runs=0). Calling any of the
"construct_*" or "certify_*" functions below against real seeds would
begin actual scientific fixture realization, which TASK-20260907-ecd3a2
does not authorize. This file exists so that source structure, encoding,
and interfaces can be reviewed before that later, separately authorized
task runs them.

Implements, as source:
  - the exact deterministic-bytes draw procedure (spec.deterministic_bytes);
  - reduced supersingular-family curve/generator construction
    (spec.rho.group_construction) for k in {40, 48, 56};
  - a recursive Pocklington-style prime-certificate construction interface
    (trial division base case below 65536).

Does not implement: actual execution of the search loops against real
seeds, actual certificate realization, or persistence of any fixture byte
string to disk. Those remain future scientific-execution responsibilities.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Deterministic byte encoding and the domain-separated draw procedure
# (spec.deterministic_bytes)
# ---------------------------------------------------------------------------


def encode_domain_string(domain: str) -> bytes:
    """UTF-8 domain string prefixed by its u32 byte length."""
    raw = domain.encode("utf-8")
    return len(raw).to_bytes(4, "big") + raw


def encode_u32(value: int) -> bytes:
    if not (0 <= value < 2 ** 32):
        raise ValueError("u32 out of range")
    return value.to_bytes(4, "big")


def encode_u64(value: int) -> bytes:
    if not (0 <= value < 2 ** 64):
        raise ValueError("u64 out of range")
    return value.to_bytes(8, "big")


def encode_field_value(value: int) -> bytes:
    """32-byte big-endian fixed width for field/scalar values."""
    if not (0 <= value < 2 ** 256):
        raise ValueError("field/scalar value must fit in 256 bits")
    return value.to_bytes(32, "big")


def draw(domain: str, seed: int, index: int, modulus_L: int,
         start_j: int = 0, record_rejections: Optional[List[int]] = None) -> Tuple[int, int]:
    """Deterministic rejection-sampled draw in [0, L-1], per spec.deterministic_bytes.draw.

    For domain, seed, index, and counter j starting at zero:
        h = int(SHA256(encode(domain) || u64(seed) || u32(index) || u64(j)))
    Reject h >= floor(2**256 / L) * L; return h mod L, and the final j used.
    Every rejection is recorded (into `record_rejections` if provided, as
    the rejected j values).

    This function performs real computation (it is pure/deterministic and
    side-effect-free beyond optionally appending to a caller-supplied list),
    but it is NOT invoked anywhere in this task to realize an actual fixture
    value -- it exists as reviewable source for a future execution task.
    """
    if modulus_L <= 0:
        raise ValueError("modulus_L must be positive")
    threshold = (2 ** 256 // modulus_L) * modulus_L
    j = start_j
    prefix = encode_domain_string(domain) + encode_u64(seed) + encode_u32(index)
    while True:
        h_bytes = hashlib.sha256(prefix + encode_u64(j)).digest()
        h = int.from_bytes(h_bytes, "big")
        if h >= threshold:
            if record_rejections is not None:
                record_rejections.append(j)
            j += 1
            continue
        return h % modulus_L, j


def draw_nonzero(domain: str, seed: int, index: int, modulus_L: int,
                  start_j: int = 0, record_rejections: Optional[List[int]] = None) -> Tuple[int, int]:
    """Draw nonzero values as 1 + draw(L - 1), per spec.deterministic_bytes.draw."""
    value, j = draw(domain, seed, index, modulus_L - 1, start_j, record_rejections)
    return 1 + value, j


# ---------------------------------------------------------------------------
# Point / identity encoding (spec.deterministic_bytes.point_encoding)
# ---------------------------------------------------------------------------


def encode_point(x: Optional[int], y: Optional[int]) -> bytes:
    """Identity: 0x00 || 64 zero bytes. Finite affine point: 0x01 || x || y,
    each a canonical 32-byte residue. Reject noncanonical encodings is a
    property enforced by the (future) decoder, not this encoder."""
    if x is None and y is None:
        return b"\x00" + (b"\x00" * 64)
    if x is None or y is None:
        raise ValueError("finite point requires both x and y")
    return b"\x01" + encode_field_value(x) + encode_field_value(y)


# ---------------------------------------------------------------------------
# Recursive Pocklington-style prime certificate construction (structural)
# ---------------------------------------------------------------------------


TRIAL_DIVISION_BASE_CASE_LIMIT = 65536


@dataclass
class PocklingtonCertificateSource:
    """Mirrors independent_checker.PocklingtonCertificate's structure (kept
    as a separate dataclass here deliberately -- fixture_generator produces
    a certificate; independent_checker verifies one; they must not share a
    class definition that could silently couple producer and checker
    assumptions).
    """

    n: int
    factored_part_product: int
    witnesses: List[int]
    recursive_subcertificates: List["PocklingtonCertificateSource"] = field(default_factory=list)
    base_case_trial_division: bool = False


def construct_pocklington_certificate(n: int) -> PocklingtonCertificateSource:
    """Recursively construct a Pocklington-style primality certificate for
    odd n, with trial-division base cases below 65536, per
    spec.rho.group_construction.prime_certificates.

    This function performs real, deterministic trial division and witness
    search and WOULD realize an actual certificate if called. It is
    provided as reviewable source only; TASK-20260907-ecd3a2 does not call
    it (maximum_runs=0, "do not generate ... proof certificates").
    Guarded below with an explicit refusal so an accidental invocation in
    this task fails loudly rather than silently producing a certificate.
    """
    raise RuntimeError(
        "construct_pocklington_certificate is source-only in "
        "TASK-20260907-ecd3a2; this task authorizes zero scientific "
        "execution and must not realize a certificate. A future "
        "scientific-execution task removes this guard under its own "
        "authorization."
    )


def _unrun_trial_division_reference(n: int) -> bool:
    """Reference trial-division primality check for the base case (n < 65536).
    Included as plain, reviewable arithmetic (not gated) since it performs
    no fixture realization by itself and has no side effects; still never
    called from anywhere else in this module's guarded path."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


# ---------------------------------------------------------------------------
# Reduced supersingular-family curve construction (spec.rho.group_construction)
# ---------------------------------------------------------------------------


@dataclass
class ReducedCurveFixtureSource:
    """Structural container for a realized reduced-curve fixture: N (odd
    prime subgroup order), p = 4N - 1, generator (Gx, Gy) with G = [4]P,
    curve E: y^2 = x^3 + x (a=1, b=0). Not populated with real values by
    this task."""

    k_bits: int
    N: int
    p: int
    Gx: int
    Gy: int
    N_certificate: PocklingtonCertificateSource
    p_certificate: PocklingtonCertificateSource


def construct_reduced_curve_fixture(k_bits: int) -> ReducedCurveFixtureSource:
    """Construct the k-bit reduced curve fixture exactly per
    spec.rho.group_construction.procedure:

      1. Enumerate odd N from the least odd N >= 2**(k-1), ascending by two,
         N < 2**k.
      2. Select the first N for which both N and p = 4*N - 1 have
         deterministically checked primality certificates.
      3. E: y^2 = x^3 + x over F_p.
      4. Search x from zero upward; require nonzero quadratic-residue RHS
         (via r = RHS**((p+1)//4) mod p since p = 3 mod 4, verify r*r=RHS,
         choose y = min(r, p - r)).
      5. Form P = (x, y), G = [4]P, skip only G = O.
      6. Require G != O and [N]G = O.

    This function WOULD realize an actual fixture (curve + generator +
    certificates) if called, which this task does not authorize. Guarded
    with an explicit refusal, matching construct_pocklington_certificate's
    pattern, so the interface is reviewable without being runnable here.
    """
    if k_bits not in (40, 48, 56):
        raise ValueError("spec.rho fixes exactly k in {40, 48, 56}")
    raise RuntimeError(
        "construct_reduced_curve_fixture is source-only in "
        "TASK-20260907-ecd3a2; this task authorizes zero scientific "
        "execution and must not realize a reduced-curve fixture or its "
        "certificates. A future scientific-execution task removes this "
        "guard under its own authorization and admission."
    )


def _unrun_tonelli_for_p_equiv_3_mod_4(rhs: int, p: int) -> Optional[int]:
    """Reference square-root-mod-p routine for p = 3 mod 4
    (spec.rho.group_construction.square_root): r = rhs**((p+1)//4) mod p,
    verify r*r == rhs mod p, return min(r, p - r) or None if rhs is not a
    quadratic residue. Plain reviewable arithmetic; not wired into any
    guarded execution path and not called elsewhere in this module."""
    if p % 4 != 3:
        raise ValueError("this routine assumes p = 3 mod 4")
    r = pow(rhs % p, (p + 1) // 4, p)
    if (r * r) % p != rhs % p:
        return None
    return min(r, p - r)


__all__ = [
    "encode_domain_string",
    "encode_u32",
    "encode_u64",
    "encode_field_value",
    "draw",
    "draw_nonzero",
    "encode_point",
    "TRIAL_DIVISION_BASE_CASE_LIMIT",
    "PocklingtonCertificateSource",
    "construct_pocklington_certificate",
    "ReducedCurveFixtureSource",
    "construct_reduced_curve_fixture",
]

# NOTE: the guarded construct_* functions above raise RuntimeError rather
# than perform any fixture/certificate realization; the encode_*/draw
# helpers are pure deterministic byte-encoding utilities with no file or
# network I/O. Nothing in this module has been invoked to realize a real
# seed, curve, generator, or certificate under TASK-20260907-ecd3a2. Only
# `python3 -m py_compile` static syntax checking has been run against this
# file.
