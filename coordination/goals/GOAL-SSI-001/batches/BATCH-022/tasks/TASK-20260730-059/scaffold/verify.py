"""Verify(x, k_prime) scaffolding predicate for FC0-EXT-PKG-SSI-001.

Implements the frozen signature Verify(x, k_prime) -> bool as a total
deterministic *no-crypto* predicate over opaque scaffolding tokens.

This is NOT cryptographic verification, NOT a CollimationSieve API, and
does NOT clear QM-ERROR or QUERY_MEMORY. Curve/isogeny evaluation is
explicitly absent (deferred_to_implementation_spike in verify_interface).
"""

from __future__ import annotations

from .types import CandidateSecret, FailureChannel, PublicInstance


class VerificationFault(Exception):
    """Malformed buffers / role violation during predicate evaluation."""

    maps_to = FailureChannel.F_verify


def Verify(x: PublicInstance, k_prime: CandidateSecret) -> bool:
    """Total deterministic scaffolding Verify(x, k_prime) -> bool.

    Semantics (scaffolding only):
    - Malformed x or k_prime raises VerificationFault (maps to F_verify /
      verification_fault; never success).
    - If x.scaffold_accept_token is set and equals k_prime.token, return True
      (synthetic unit-test accept path; not crypto).
    - Otherwise return False (F_verify constituent; not success).

    No curve, isogeny, or quantum-circuit evaluation is performed.
    """
    if not isinstance(x, PublicInstance) or not isinstance(k_prime, CandidateSecret):
        raise VerificationFault("role_type_violation")
    if not x.well_formed or not k_prime.well_formed:
        raise VerificationFault("malformed_candidate_or_instance_buffer")
    if x.scaffold_accept_token is not None and x.scaffold_accept_token == k_prime.token:
        return True
    return False


def classify_verify_outcome(result: bool | Exception) -> FailureChannel | str:
    """Map Verify outcome to success or F_verify / F (checklist only)."""
    if isinstance(result, Exception):
        return FailureChannel.F_verify
    if result is True:
        return "success_exit"
    return FailureChannel.F_verify
