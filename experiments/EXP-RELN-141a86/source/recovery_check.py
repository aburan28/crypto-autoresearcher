"""
Stage 0c recovery-check machinery for EXP-RELN-141a86: parses the
`grammar_expr*` notation strings from candidate-list.yaml /
control-tables/recovery-controls-closed-form.yaml into grammar_engine.py's
tuple representation, confirms their node count matches the pre-stated
canonical count, checks STRUCTURAL PRESENCE in the exhaustively enumerated
candidate set at or below that complexity (when the enumeration reaches
that complexity within budget), and NUMERICALLY VERIFIES the expression
against a real generated table with free CONST placeholders fit by a
small, disclosed rational search grid (not a full nonlinear least-squares
search over every enumerated candidate, which is computationally
infeasible at the scale measured in Stage 0c -- see implementation.md).
"""

from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

import grammar_engine as ge

# Small, disclosed rational search grid used ONLY to fit the (<=2) free
# CONST placeholders of a SPECIFIC, already-known target expression against
# real data (never used to brute-force-fit the full enumerated candidate
# set, which numbers in the hundreds of thousands to millions at these
# complexities -- see implementation.md for the measured infeasibility of
# doing that generally).
CONST_SEARCH_GRID = [Fraction(n, d) for d in range(1, 5) for n in range(-8, 13)]
CONST_SEARCH_GRID = sorted(set(CONST_SEARCH_GRID))


def parse_expr(s: str) -> Tuple:
    """Parses strings like 'div(binomial(sub(add(B,m),CONST[1]),m),N)' into
    grammar_engine tuple form. CONST[k] (any k) maps to the single unbound
    ('CONST',) tag (numbered only for human readability in the source
    yaml); bare integers map to ('const', value); identifiers map to
    ('leaf', name)."""
    s = s.strip()
    pos = 0

    def peek():
        return s[pos] if pos < len(s) else ''

    def parse_atom():
        nonlocal pos
        m = re.match(r'CONST(\[\d+\])?', s[pos:])
        if m:
            pos += m.end()
            return ("CONST",)
        m = re.match(r'-?\d+', s[pos:])
        if m and (pos == 0 or s[pos-1] in '(,'):
            pos += m.end()
            return ("const", int(m.group(0)))
        m = re.match(r'[A-Za-z_][A-Za-z_0-9]*', s[pos:])
        if m:
            name = m.group(0)
            pos += m.end()
            if peek() == '(':
                pos += 1  # consume '('
                args = [parse_expr_inner()]
                while peek() == ',':
                    pos += 1
                    args.append(parse_expr_inner())
                assert peek() == ')', f"expected ')' at {pos} in {s!r}"
                pos += 1
                if len(args) == 1:
                    return (name, args[0])
                elif len(args) == 2:
                    return (name, args[0], args[1])
                else:
                    raise ValueError(f"unexpected arity {len(args)} for {name}")
            else:
                return ("leaf", name)
        raise ValueError(f"cannot parse at position {pos} in {s!r}: {s[pos:pos+20]!r}")

    def parse_expr_inner():
        return parse_atom()

    result = parse_expr_inner()
    # skip trailing whitespace, ensure fully consumed
    while pos < len(s) and s[pos] == ' ':
        pos += 1
    return result


def const_placeholders(expr) -> int:
    """Count of CONST leaves in the tree (order of appearance)."""
    tag = expr[0]
    if tag == "CONST":
        return 1
    if tag in ("leaf", "const"):
        return 0
    if tag in ge.UNARY_OPS:
        return const_placeholders(expr[1])
    if tag in ge.BINARY_OPS:
        return const_placeholders(expr[1]) + const_placeholders(expr[2])
    raise ValueError(tag)


def eval_with_consts(expr, env: Dict[str, float], const_values: List[Fraction]):
    """Evaluate expr, substituting successive CONST leaves (in left-to-right
    traversal order) with const_values[0], const_values[1], ... ."""
    idx = [0]

    def _ev(e):
        tag = e[0]
        if tag == "leaf":
            return env[e[1]]
        if tag == "const":
            return e[1]
        if tag == "CONST":
            v = const_values[idx[0]]
            idx[0] += 1
            return v
        if tag in ge.UNARY_OPS:
            v = _ev(e[1])
            if v is None:
                return None
            if tag == "log":
                return math.log(float(v)) if float(v) > 0 else None
            if tag == "exp":
                try:
                    return math.exp(float(v))
                except OverflowError:
                    return None
            if tag == "floor":
                return math.floor(float(v))
            if tag == "ceil":
                return math.ceil(float(v))
        if tag in ge.BINARY_OPS:
            a = _ev(e[1])
            b = _ev(e[2])
            if a is None or b is None:
                return None
            if tag == "add":
                return a + b
            if tag == "sub":
                return a - b
            if tag == "mul":
                return a * b
            if tag == "div":
                if b == 0:
                    return None
                return a / b
            if tag == "pow":
                try:
                    return float(a) ** float(b)
                except OverflowError:
                    return None
            if tag == "binomial":
                # a, b may be arbitrarily large exact ints/Fractions here
                # (e.g. binomial(n,B) with n in the thousands): compare and
                # convert without forcing an intermediate float, which can
                # OverflowError on a huge-but-exact integer long before the
                # actual math.comb result would.
                try:
                    ai = int(a) if (isinstance(a, (int, Fraction)) and a == int(a)) else None
                    bi = int(b) if (isinstance(b, (int, Fraction)) and b == int(b)) else None
                except (OverflowError, ValueError):
                    ai = bi = None
                if ai is None or bi is None or ai < 0 or bi < 0 or bi > ai:
                    return None
                return math.comb(ai, bi)
        raise ValueError(tag)

    return _ev(expr)


def verify_expression_on_table(expr, rows: List[Dict[str, float]], target_key: str,
                                tol: float = 1e-9) -> Dict:
    """
    Numerically verifies `expr` (with 0, 1 or 2 CONST placeholders) against
    a table of dict rows (each providing the leaf values under their names
    and the target value under `target_key`), by searching
    CONST_SEARCH_GRID (cartesian product over the placeholders present)
    for an assignment achieving max |predicted-target| <= tol on EVERY
    row. Returns the first such assignment found (grid is small and
    ordered, so this is deterministic) plus the max residual, or reports
    no_exact_match if the grid is exhausted, with the best (nearest)
    residual found for reporting.
    """
    n_const = const_placeholders(expr)
    if n_const > 2:
        return {"error": f"expression has {n_const} > 2 free constants; out of scope"}

    def max_residual(const_values):
        max_r = 0.0
        for row in rows:
            pred = eval_with_consts(expr, row, const_values)
            if pred is None:
                return None
            r = abs(float(pred) - float(row[target_key]))
            if r > max_r:
                max_r = r
        return max_r

    best = None
    if n_const == 0:
        r = max_residual([])
        return {"n_const": 0, "const_values": [], "max_residual": r,
                "exact_match": (r is not None and r <= tol)}

    if n_const == 1:
        for c0 in CONST_SEARCH_GRID:
            r = max_residual([c0])
            if r is not None and (best is None or r < best[1]):
                best = ([c0], r)
            if r is not None and r <= tol:
                return {"n_const": 1, "const_values": [str(c0)], "max_residual": r, "exact_match": True}
        return {"n_const": 1, "const_values": [str(best[0][0])] if best else None,
                "max_residual": best[1] if best else None, "exact_match": False}

    # n_const == 2
    for c0 in CONST_SEARCH_GRID:
        for c1 in CONST_SEARCH_GRID:
            r = max_residual([c0, c1])
            if r is not None and (best is None or r < best[1]):
                best = ([c0, c1], r)
            if r is not None and r <= tol:
                return {"n_const": 2, "const_values": [str(c0), str(c1)], "max_residual": r, "exact_match": True}
    return {"n_const": 2, "const_values": [str(v) for v in best[0]] if best else None,
            "max_residual": best[1] if best else None, "exact_match": False}


if __name__ == "__main__":
    # self-test: parse and node-count the pre-stated targets, confirm they
    # match candidate-list.yaml's contract_pre_stated_summary exactly.
    tests = [
        ("div(binomial(sub(add(B,m),CONST[1]),m),N)", 9),
        ("div(binomial(sub(n,B),B),binomial(n,B))", 9),
        ("sub(CONST[1],div(binomial(sub(n,B),B),binomial(n,B)))", 11),
        ("ceil(div(add(mul(m,sub(B,CONST[1])),D_S),CONST[2]))", 10),
        ("div(binomial(add(B,CONST[2]),CONST[3]),N)", 7),
        ("sub(CONST[1],mu)", 3),
        ("sub(add(div(conc,mu),CONST[1]),mu)", 7),
    ]
    for s, expected in tests:
        e = parse_expr(s)
        nc = ge.node_count(e)
        status = "OK" if nc == expected else "MISMATCH"
        print(f"{status}: {s!r} -> node_count={nc} (expected {expected})")
        assert nc == expected, (s, nc, expected)
    print("recovery_check.py self-test: all node counts match")
