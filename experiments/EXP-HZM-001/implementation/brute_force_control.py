"""CTRL-HZM-BRUTE-FORCE: independent ground-truth zero-minor check.

Directly enumerates all defect-d column choices from a kernel matrix K and
evaluates the corresponding maximal minors of K by definition (determinant
== 0 mod p), with NO signature hashing and NO duplicate-based shortcut.
This is the independent oracle that signature_enumeration.py's duplicate-
detection result must agree with (CTRL-HZM-BRUTE-FORCE pass_condition:
"Zero discrepancies between signature-search counts and brute-force minor
evaluation on every subset instance").

STATUS UNDER EXP-HZM-001: written and unit-smoke-tested in isolation (see
SELFTEST.md), but NOT invoked as part of a formal protocol run, because
CTRL-HZM-MANUSCRIPT-ALIGNMENT failed in RUN-HZM-001-a and the pre-registered
stopping rule forbids opening the enumeration/control stage (RUN-HZM-001-c)
in that branch. No control-comparison claim is made under this experiment.
"""
from __future__ import annotations

import itertools

import sympy


def zero_minors_by_definition(K: sympy.Matrix, p: int) -> set[tuple[int, ...]]:
    """Return the set of column-index-tuples (size = K.rows) whose maximal
    minor of K is exactly 0 mod p, by direct determinant evaluation.
    """
    ell, two_ell = K.shape
    zero_minors = set()
    K_dm = K.applyfunc(lambda v: int(v) % p)
    for cols in itertools.combinations(range(two_ell), ell):
        sub = K_dm[:, list(cols)]
        det = int(sub.det()) % p
        if det == 0:
            zero_minors.add(cols)
    return zero_minors


def cross_check_against_signature_search(K: sympy.Matrix, p: int,
                                          signature_zero_minors: set[tuple[int, ...]]) -> dict:
    """Compare the brute-force ground truth with the signature-search's
    reported zero-minor index sets (each normalized as a sorted tuple).
    Returns discrepancy counts in both directions.
    """
    brute = zero_minors_by_definition(K, p)
    sig = {tuple(sorted(s)) for s in signature_zero_minors}
    missed_by_signature_search = brute - sig
    false_positives_by_signature_search = sig - brute
    return {
        "brute_force_zero_minor_count": len(brute),
        "signature_search_zero_minor_count": len(sig),
        "missed_by_signature_search": len(missed_by_signature_search),
        "false_positives_by_signature_search": len(false_positives_by_signature_search),
        "discrepancies": len(missed_by_signature_search) + len(false_positives_by_signature_search),
    }
