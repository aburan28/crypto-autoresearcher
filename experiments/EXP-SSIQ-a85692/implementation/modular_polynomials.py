#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 -- Classical modular polynomials Phi_ell(X, Y) for ell in
L \\ {2} = {3, 5, 7, 11, 13, 17, 19, 23}.

PF-2 FIX APPLIED (spec.inputs.delta_e_computation.modular_polynomial_source_pinned):
coefficients are obtained from a CITED, VERIFIABLE source and NEVER
approximated, truncated, or recalled from memory.

SOURCE: Andrew Sutherland's classical modular polynomial database,
https://math.mit.edu/~drew/ClassicalModPolys.html, "phi_j" files
(https://math.mit.edu/~drew/modpolys/jfiles/phi_j_<ell>.txt), documented in
Sutherland, "Computing modular polynomials in quasi-linear time" and the
isogeny-volcanoes line of work (also referenced as arXiv:1202.3985 in the
frozen contract). Fetched directly over HTTPS during this run; see
source_access_log.yaml for the exact URLs, HTTP statuses, byte counts and
SHA-256 hashes of what was retrieved, and modpoly_data/*.txt for the
byte-identical vendored copies checked into this experiment's
implementation/ directory (write_scope) so re-running from the SAME checked
-in bytes never depends on network availability, while the fetch itself is
still logged as the acquisition route actually used.

FILE FORMAT (Sutherland "phi_j" convention, confirmed against phi_j_2.txt,
which reproduces build_isogeny_graph.py's independently-sourced/verified
Phi_2 nine-term polynomial EXACTLY -- see verify_against_known_phi2 below):
each non-blank line is "[i,j] c" meaning the bivariate coefficient of
X^i Y^j in Phi_ell(X,Y) is the integer c, for i >= j ONLY (the polynomial is
symmetric in X,Y: coefficient of X^i Y^j equals coefficient of X^j Y^i, so
only the i>=j triangle, including the diagonal, is listed). Phi_ell has
degree ell+1 in each variable; the leading term is X^{ell+1} Y^0 with
coefficient 1 (confirmed present in every fetched file).

This module NEVER hand-transcribes a coefficient: parse_modpoly_file reads
the exact integers out of the fetched/vendored file text, and
phi_ell_coeffs_in_X evaluates them via ordinary Fp2 arithmetic (imported
from build_isogeny_graph.Fp2Field, not reimplemented) using the symmetry
relation to fill in the j>i entries.
"""

import os
import re

_LINE_RE = re.compile(r"^\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]\s+(-?\d+)\s*$")

MODPOLY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modpoly_data")


def parse_modpoly_file(path):
    """Parse a Sutherland phi_j_<ell>.txt file into {(i, j): coeff} for
    i >= j, plus the inferred degree (= ell + 1, the largest i seen at j=0
    with coeff 1 on the diagonal-adjacent leading term)."""
    table = {}
    max_i = 0
    with open(path, "r", encoding="ascii") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            m = _LINE_RE.match(line)
            if not m:
                raise ValueError(
                    "%s:%d: line does not match '[i,j] c' format: %r"
                    % (path, line_no, line))
            i, j, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if j > i:
                raise ValueError(
                    "%s:%d: expected i>=j (lower triangle only), got "
                    "[%d,%d]" % (path, line_no, i, j))
            table[(i, j)] = c
            if i > max_i:
                max_i = i
    return table, max_i


_CACHE = {}


def load_modpoly(ell):
    """Load and cache the sourced table for Phi_ell.  ell must be one of the
    pinned L \\ {2} values; the file must already exist under modpoly_data/
    (vendored copy of the fetched bytes -- see module docstring)."""
    if ell in _CACHE:
        return _CACHE[ell]
    path = os.path.join(MODPOLY_DIR, "phi_j_%d.txt" % ell)
    if not os.path.exists(path):
        raise FileNotFoundError(
            "modular polynomial source file missing for ell=%d: %s "
            "(PF-2 requires a cited source file, never a recalled "
            "coefficient)" % (ell, path))
    table, max_i = parse_modpoly_file(path)
    if max_i != ell + 1:
        raise ValueError(
            "Phi_%d: inferred X-degree %d does not match expected ell+1=%d"
            % (ell, max_i, ell + 1))
    if table.get((ell + 1, 0)) != 1:
        raise ValueError(
            "Phi_%d: leading coefficient [%d,0] is %r, expected 1"
            % (ell, ell + 1, table.get((ell + 1, 0))))
    _CACHE[ell] = (table, max_i)
    return table, max_i


def phi_ell_coeffs_in_X(field, ell, j_val):
    """Phi_ell(X, j_val) as an ascending-coefficient list [c0, c1, ..., c_{ell+1}]
    of Fp2 elements, evaluated over `field` (an Fp2Field instance imported
    from build_isogeny_graph.py), using the SOURCED table for `ell` and the
    symmetry coefficient(i,j) = coefficient(j,i) for j > i.

    Ascending-list convention matches build_isogeny_graph.phi2_coeffs_in_X
    and poly_trim's expectation, so find_roots_with_multiplicity (imported
    unchanged) works on this polynomial exactly as it does on Phi_2's."""
    table, deg = load_modpoly(ell)
    coeffs_X = []
    for i in range(deg + 1):
        c = (0, 0)
        jp = field.from_int(1)
        for b in range(deg + 1):
            key = (i, b) if i >= b else (b, i)
            coeff_int = table.get(key)
            if coeff_int:
                c = field.add(c, field.mul(field.from_int(coeff_int), jp))
            jp = field.mul(jp, j_val)
        coeffs_X.append(c)
    return coeffs_X


def verify_against_known_phi2(field_cls):
    """Development/sanity cross-check ONLY (not the PF-2-required
    independent verification, which is velu_verify.py's job for ell=23):
    fetch/vendor phi_j_2.txt through the SAME parser used for ell>2 and
    confirm it reproduces build_isogeny_graph.phi2_coeffs_in_X's
    independently-sourced nine integer coefficients EXACTLY, for a sample
    prime and a sample j.  This checks the PARSER, not the ell=23 table --
    it is not a substitute for the from-scratch Velu-formula check PF-2
    requires."""
    import sys
    sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..",
        "EXP-SSIQ-58b642", "implementation"))
    import build_isogeny_graph as big  # noqa: E402

    path = os.path.join(MODPOLY_DIR, "phi_j_2.txt")
    table, deg = parse_modpoly_file(path)
    if deg != 3:
        return False, "phi_j_2.txt degree %d != 3" % deg

    p = 2437
    field = field_cls(p)
    for j_int in (0, 1, 17, 100, p - 1):
        j = field.from_int(j_int)
        from_source = []
        for i in range(deg + 1):
            c = (0, 0)
            jp = field.from_int(1)
            for b in range(deg + 1):
                key = (i, b) if i >= b else (b, i)
                coeff_int = table.get(key)
                if coeff_int:
                    c = field.add(c, field.mul(field.from_int(coeff_int), jp))
                jp = field.mul(jp, j)
            from_source.append(c)
        known = big.phi2_coeffs_in_X(field, j)
        if from_source != list(known):
            return False, ("mismatch at j=%d: source-parsed %r != "
                            "build_isogeny_graph %r" % (j_int, from_source, known))
    return True, "phi_j_2.txt parsed via the SAME general parser reproduces " \
                 "build_isogeny_graph.phi2_coeffs_in_X exactly for 5 sample j values"
