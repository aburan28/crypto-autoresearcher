"""count_predictor.py -- formula/branch-recurrence count predictor and
commitment/blinding interface for EXP-CRYPTO-9225d2.

AUTHORSHIP NOTE: this file was authored in the same executor session as
arithmetic.py (see independent_checker.py's disclosure for the full
statement). It therefore does NOT satisfy specification.arithmetic.checker.
count_predictor's requirement to "Independently implement the declared
branch/formula cost recurrence from public inputs; do not consume measured
counters or producer operation traces until the predictor report is
frozen" as an INDEPENDENT artifact -- it satisfies only the structural
half (a formula recurrence kept in a file separate from the producer's
traces). A genuinely independent predictor author/review remains an
outstanding admission requirement; see preparation-report.yaml.

Scope: this module predicts M/S/I counts from the *declared branch trace*
of a scalar multiplication (i.e. from the scalar's bit pattern and which
addition/doubling exceptional branches fire), using the exact formula
constants in the frozen specification. It does not read or import any
counters produced by arithmetic.py, and it is not evaluated against any
real fixture, seed, or scalar value in this task -- no predicted numerical
counts are computed now (per handoff constraint). Everything below is
therefore INTERFACE + FORMULA, callable but unexercised in this delivery.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Per-operation cost constants, taken verbatim from the frozen specification
# (never refit after observation, per goe_ruler.primitive_reporting).
# ---------------------------------------------------------------------------

# Generic (non-exceptional) full ADD via common-Z rescaling: 12 M, 4 S.
GENERIC_ADD_M = 12
GENERIC_ADD_S = 4

# Doubling specializations (spec.arithmetic.doubling.specializations):
DOUBLE_A0_M = 1
DOUBLE_A0_S = 7  # secp256k1, a=0
DOUBLE_A1_M = 1
DOUBLE_A1_S = 8  # reduced rho curves, a=1

# Final normalization (spec.arithmetic.normalization): 3 M, 1 S, 1 I.
NORMALIZE_M = 3
NORMALIZE_S = 1
NORMALIZE_I = 1

# model_256 generic-step constants (spec.model_256.arithmetic), used only
# for the modeled 256-bit resource rows, never for a measured scalar count:
MODEL_ADD_M = 15
MODEL_ADD_S = 5
MODEL_ADD_I = 1
MODEL_DOUBLE_A0_M = 4
MODEL_DOUBLE_A0_S = 8
MODEL_DOUBLE_A0_I = 1
# equally-weighted branch mean (34M + 18S + 3I)/3 = 22/3 GOE per transition,
# where 34 = 15(add)+15(add? -- see spec text) ... reproduced exactly as the
# frozen numerator/denominator triple, not re-derived arithmetically here:
MODEL_MEAN_NUMERATOR = (34, 18, 3)  # (M, S, I) summed across 3 equally-weighted branches
MODEL_MEAN_DENOMINATOR = 3
MODEL_MEAN_GOE_PER_TRANSITION = (22, 3)  # exact rational 22/3, per spec text


@dataclass
class BranchTrace:
    """The declared per-scalar branch trace the predictor consumes: which of
    the 256 doubling steps are exceptional (Y=0 or identity-input), and
    which of the (up to 256) conditional ADD steps are exceptional
    (identity input, or the equal-U exceptional cases after rescaling).

    This is a PUBLIC, input-derived trace (bit pattern + which points are
    identity along the way for the fixed algorithm) -- not a measured
    producer counter. Constructing a real instance requires a realized
    scalar and curve, which this task does not produce.
    """

    scalar_bit_length_used: int  # always 256 per spec.arithmetic.scalar_algorithm
    doubling_branches: List[str]  # one of {"generic", "identity_input", "y_zero"}
    add_branches: List[Optional[str]]  # one of {None (bit=0, no ADD), "generic",
                                        # "identity_input", "equal_u_equal_v",
                                        # "equal_u_opposite_v"}
    doubling_a: int  # 0 or 1, selects the specialization


def predict_counts_from_trace(trace: BranchTrace) -> Tuple[int, int, int]:
    """Deterministically fold the branch/formula cost recurrence declared by
    the frozen specification into (M, S, I) totals, INCLUDING the fixed
    final normalization charge. This is the count_predictor's core formula
    interface; it is not evaluated against any real trace in this task.
    """
    if trace.scalar_bit_length_used != 256:
        raise ValueError("spec.arithmetic.scalar_algorithm fixes exactly 256 bits")
    if len(trace.doubling_branches) != 256:
        raise ValueError("expected exactly 256 doubling steps")
    if len(trace.add_branches) != 256:
        raise ValueError("expected exactly 256 conditional-add slots (one per bit)")

    m_total = 0
    s_total = 0
    i_total = 0

    for db in trace.doubling_branches:
        if db == "generic":
            if trace.doubling_a == 0:
                m_total += DOUBLE_A0_M
                s_total += DOUBLE_A0_S
            elif trace.doubling_a == 1:
                m_total += DOUBLE_A1_M
                s_total += DOUBLE_A1_S
            else:
                raise ValueError("doubling_a must be 0 or 1")
        elif db in ("identity_input", "y_zero"):
            pass  # branch/copy work only, no field calls (spec)
        else:
            raise ValueError(f"unknown doubling branch label: {db}")

    for ab in trace.add_branches:
        if ab is None:
            continue
        if ab == "generic":
            m_total += GENERIC_ADD_M
            s_total += GENERIC_ADD_S
        elif ab == "identity_input":
            pass
        elif ab == "equal_u_equal_v":
            # retains the rescale cost (7M + 2S) then performs a DOUBLE;
            # charge rescale plus a generic doubling at the caller's `a`.
            m_total += 7
            s_total += 2
            if trace.doubling_a == 0:
                m_total += DOUBLE_A0_M
                s_total += DOUBLE_A0_S
            else:
                m_total += DOUBLE_A1_M
                s_total += DOUBLE_A1_S
        elif ab == "equal_u_opposite_v":
            # retains the rescale cost, returns identity, no further field calls.
            m_total += 7
            s_total += 2
        else:
            raise ValueError(f"unknown add branch label: {ab}")

    # final normalization (identity output has none; predictor assumes a
    # finite-output trace here since exceptional all-identity traces are a
    # separate declared case).
    m_total += NORMALIZE_M
    s_total += NORMALIZE_S
    i_total += NORMALIZE_I

    return m_total, s_total, i_total


def predicted_raw_goe_rational(m: int, s: int, i: int) -> Tuple[int, int]:
    """Same exact-rational GOE formula as arithmetic.OperationCounters,
    reimplemented independently here (no import) so the predictor's own
    GOE rendering does not depend on the producer module."""
    return (m + s + 100 * i), 16


def predict_model_256_transition_goe(total_transitions_L: int) -> Tuple[int, int]:
    """Modeled transition GOE = L * 22/3, exact rational (numerator, denom).
    Interface only; L is supplied by a future model-row computation, never
    invented here."""
    numerator = total_transitions_L * MODEL_MEAN_GOE_PER_TRANSITION[0]
    denominator = MODEL_MEAN_GOE_PER_TRANSITION[1]
    return numerator, denominator


# ---------------------------------------------------------------------------
# Commitment / blinding interface (spec.arithmetic.checker.blinding)
# ---------------------------------------------------------------------------


@dataclass
class BlindPredictionCommitment:
    """A commitment to a predicted count/factor made before a producer trace
    is revealed, per spec.arithmetic.checker.blinding. `commitment_digest`
    binds the predictor's claimed (M, S, I) triple and a random blinding
    nonce so it cannot be silently changed after the fact; `nonce` is
    revealed only at the unblinding step.
    """

    commitment_digest: bytes
    committed_at_domain: str  # e.g. "GOE9225/predictor/commitment/<label>"


def commit_prediction(m: int, s: int, i: int, nonce: bytes, domain: str) -> BlindPredictionCommitment:
    """Build a binding commitment to a predicted (M, S, I) triple.

    digest = SHA256(domain || u64(M) || u64(S) || u64(I) || nonce)
    following the deterministic_bytes integer-encoding convention (u64 for
    counters). Not evaluated against a real prediction in this task.
    """
    if m < 0 or s < 0 or i < 0:
        raise ValueError("counts must be non-negative")
    payload = (
        domain.encode("utf-8")
        + m.to_bytes(8, "big")
        + s.to_bytes(8, "big")
        + i.to_bytes(8, "big")
        + nonce
    )
    digest = hashlib.sha256(payload).digest()
    return BlindPredictionCommitment(commitment_digest=digest, committed_at_domain=domain)


def verify_unblinded_prediction(commitment: BlindPredictionCommitment, m: int, s: int,
                                 i: int, nonce: bytes) -> bool:
    """Recompute the commitment digest from the revealed (M, S, I, nonce)
    and compare. Returns False on any mismatch; raises nothing. Not invoked
    against real data in this task."""
    recomputed = commit_prediction(m, s, i, nonce, commitment.committed_at_domain)
    return recomputed.commitment_digest == commitment.commitment_digest


@dataclass
class BlindReviewPacket:
    """Structural container for the redacted packet a blind reviewer
    receives, per spec.arithmetic.checker.blinding: only the unplanted
    API/formula definitions, actual scalar inputs, opaque per-input M/S/I
    outputs for all routines, and the request to derive baseline counts and
    estimate overhead by opaque label. Excludes the full hypothesis/
    specification, planted source, multiplier, and label map.

    This task does not construct a populated instance (no fixtures exist);
    it defines the container so a future admission task can populate and
    archive it, and so the read-access attestation field is not forgotten.
    """

    unplanted_formula_definitions_ref: str
    scalar_inputs_ref: str
    opaque_per_input_outputs_ref: str
    reviewer_eligibility_attestation: Optional[str]  # None until obtained
    read_access_attestation: Optional[str]  # None until obtained


__all__ = [
    "BranchTrace",
    "predict_counts_from_trace",
    "predicted_raw_goe_rational",
    "predict_model_256_transition_goe",
    "BlindPredictionCommitment",
    "commit_prediction",
    "verify_unblinded_prediction",
    "BlindReviewPacket",
]

# NOTE: no numerical prediction is evaluated against a real fixture anywhere
# in this module or by importing it. Only `python3 -m py_compile` static
# syntax checking has been run against this file under TASK-20260907-ecd3a2.
