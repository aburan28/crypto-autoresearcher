"""Cold active-support PC search with the frozen result schema.

Prime p and the frozen BoolRing arithmetic are premises. Support extraction
and common validation have separate event diagnostics, outside the kernel.
"""
from collections.abc import Mapping
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "research/prime_sat_five_tests_20261029/core.py"
sys.path.insert(0, str(CORE_PATH.parent))
import core
if Path(core.__file__).resolve() != CORE_PATH:
    raise ImportError("unexpected core module")


def _validate(ring, generators, degree_cap, row_cap):
    for name, value, minimum in (("p", ring.p, 2), ("n", ring.n, 0),
                                 ("degree_cap", degree_cap, 0), ("row_cap", row_cap, 0)):
        if type(value) is not int or value < minimum:
            raise ValueError("invalid integer " + name)
    if not isinstance(generators, (list, tuple)):
        raise TypeError("generators must be a finite ordered list or tuple")
    counts = {"generator_count": len(generators), "term_count": 0,
              "mask_type_range_checks": 0, "coefficient_type_checks": 0}
    for polynomial in generators:
        if not isinstance(polynomial, Mapping):
            raise TypeError("each generator must be a mapping")
        for mask, coefficient in polynomial.items():
            counts["term_count"] += 1
            counts["mask_type_range_checks"] += 1
            if type(mask) is not int or mask < 0 or mask.bit_length() > ring.n:
                raise ValueError("noncanonical monomial mask")
            counts["coefficient_type_checks"] += 1
            if type(coefficient) is not int:
                raise ValueError("noninteger coefficient")
    return counts


def _support(ring, generators):
    active = set()
    counts = dict.fromkeys(("generators_scanned", "input_terms_scanned",
                           "coefficient_mod_reductions", "zero_coefficients_discarded",
                           "nonzero_terms_scanned", "set_bit_visits", "active_variable_count"), 0)
    for polynomial in generators:
        counts["generators_scanned"] += 1
        for mask, coefficient in polynomial.items():
            counts["input_terms_scanned"] += 1
            counts["coefficient_mod_reductions"] += 1
            if coefficient % ring.p == 0:
                counts["zero_coefficients_discarded"] += 1
                continue
            counts["nonzero_terms_scanned"] += 1
            remaining = mask
            while remaining:
                bit = remaining & -remaining
                active.add(bit.bit_length() - 1)
                counts["set_bit_visits"] += 1
                remaining ^= bit
    indices = sorted(active)
    counts["active_variable_count"] = len(indices)
    return indices, counts


def checked_refute(mode, ring, generators, degree_cap, row_cap=4096, *, diagnostics=None):
    if mode not in ("baseline", "active_support"):
        raise ValueError("unknown refuter mode")
    if diagnostics is not None and not isinstance(diagnostics, dict):
        raise TypeError("diagnostics must be a dict or None")
    validation = _validate(ring, generators, degree_cap, row_cap)
    details = {"mode": mode, "input_validation": validation,
               "support_setup": {"performed": False}, "active_indices": None}
    if mode == "baseline":
        if diagnostics is not None:
            diagnostics.update(details)
        return core.refute(ring, generators, degree_cap, row_cap)
    indices, counts = _support(ring, generators)
    details.update(active_indices=indices, support_setup={"performed": True, **counts})
    if diagnostics is not None:
        diagnostics.update(details)
    return _kernel(ring, generators, degree_cap, row_cap, indices)


def refute_active(ring, generators, degree_cap, row_cap=4096, *, diagnostics=None):
    return checked_refute("active_support", ring, generators, degree_cap, row_cap,
                          diagnostics=diagnostics)


def _kernel(ring, generators, degree_cap, row_cap, active_indices):
    """Degree-bounded PC search with exact multiplier certificates.

    Every accepted row is recursively multiplied by every variable, so this
    is a bounded Boolean polynomial-calculus search, not just XL's initial
    generator multiples. This selected echelon-row strategy is not proved
    complete for all degree-bounded PC derivations. Exhausting its queue or
    resources returns unknown, never a non-refutability assertion.
    """
    basis, queue = {}, []
    attempted = 0
    max_degree = -1
    multipliers_degree = -1
    answer = None

    def insert(poly, cert):
        nonlocal attempted, max_degree, multipliers_degree, answer
        attempted += 1
        if attempted > row_cap:
            raise OverflowError("row cap")
        poly = ring.clean(poly)
        if ring.degree(poly) > degree_cap:
            return
        max_degree = max(max_degree, ring.degree(poly))
        while poly:
            pivot = max(poly, key=lambda m: (m.bit_count(), m))
            if pivot not in basis:
                inv = pow(poly[pivot], -1, ring.p)
                poly = ring.scale(poly, inv)
                cert = [ring.scale(c, inv) for c in cert]
                basis[pivot] = (poly, cert)
                queue.append((poly, cert))
                multipliers_degree = max(multipliers_degree, *(ring.degree(c) for c in cert))
                if pivot == 0:
                    answer = cert
                return
            old, oldcert = basis[pivot]
            c = poly[pivot]
            poly = ring.sub(poly, ring.scale(old, c))
            cert = [ring.sub(x, ring.scale(y, c)) for x, y in zip(cert, oldcert)]

    capped = False
    try:
        for i, f in enumerate(generators):
            cert = [{} for _ in generators]
            cert[i] = {0: 1}
            insert(f, cert)
            if answer is not None:
                break
        cursor = 0
        while answer is None and cursor < len(queue):
            poly, cert = queue[cursor]
            cursor += 1
            for i in active_indices:
                v = ring.var(i)
                insert(ring.mul(poly, v), [ring.mul(c, v) for c in cert])
                if answer is not None:
                    break
    except OverflowError:
        capped = True
    return {"status": "refuted" if answer is not None else "unknown",
            "closure_complete": not capped and answer is None,
            "closure_complete_meaning": "stored_echelon_row_strategy_exhausted_not_complete_degree_D_PC",
            "resource_capped": capped, "degree_cap": degree_cap,
            "max_accepted_row_degree": max_degree,
            "max_multiplier_degree": multipliers_degree,
            "rank": len(basis), "attempted_rows": attempted,
            "certificate": answer}
