#!/usr/bin/env python3
"""Check that the Macaulay2 and Singular scripts the harness generated for the
same instance encode the SAME polynomial system.

Fairness question this answers: if magma_to_singular emitted a different (or
harder) ideal than magma_to_m2, then Singular's 900 s budget stop would be an
artifact of the conversion rather than an observation about Singular's std.

Method: parse both files' variable lists (ordered, so variable i in one ring
corresponds to variable i in the other), parse each ideal generator into a set
of monomials over F_2 given as frozensets of variable POSITIONS plus a constant
parity, and compare the two sets of generators as unordered sets.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _terms(expr: str, varpos: dict) -> frozenset:
    """Parse an F_2 polynomial written as a '+'-separated sum of products of
    variables and integer constants.  Returns a frozenset of monomials, each a
    frozenset of variable positions; the constant 1 is the empty frozenset.
    Over F_2 a repeated monomial cancels, so we XOR into a set."""
    mons = set()
    for t in expr.split("+"):
        t = t.strip()
        if not t:
            continue
        factors = [f.strip() for f in t.split("*") if f.strip()]
        pos = set()
        const = 1
        for f in factors:
            if re.fullmatch(r"\d+", f):
                const = (const * int(f)) % 2
                continue
            m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)(\^(\d+))?", f)
            if not m:
                raise ValueError(f"unparsed factor {f!r} in term {t!r}")
            name = m.group(1)
            if name not in varpos:
                raise ValueError(f"unknown variable {name!r}")
            pos.add(varpos[name])   # x^k = x over F_2 with field equations
        if const == 0:
            continue
        key = frozenset(pos)
        mons ^= {key}
    return frozenset(mons)


def parse_m2(path: Path):
    txt = path.read_text()
    ring = re.search(r"^R\s*=\s*ZZ/2\[(.*?),\s*MonomialOrder", txt, re.S | re.M)
    names = [v.strip() for v in ring.group(1).split(",")]
    varpos = {n: i for i, n in enumerate(names)}
    body = re.search(r"^I\s*=\s*ideal\((.*?)\);\s*$", txt, re.S | re.M).group(1)
    gens = [_terms(g, varpos) for g in _split_top(body)]
    f = re.search(r"^F\s*=\s*ideal\((.*?)\);\s*$", txt, re.S | re.M).group(1)
    fieldeqs = [_terms(g.replace("-", "+"), varpos) for g in _split_top(f)]
    return names, gens, fieldeqs


def parse_sing(path: Path):
    txt = path.read_text()
    ring = re.search(r"^ring\s+r\s*=\s*2,\s*\((.*?)\)\s*,\s*dp\s*;", txt, re.S | re.M)
    names = [v.strip() for v in ring.group(1).split(",")]
    varpos = {n: i for i, n in enumerate(names)}
    body = re.search(r"^ideal\s+I\s*=\s*(.*?);\s*$", txt, re.S | re.M).group(1)
    gens = [_terms(g, varpos) for g in _split_top(body)]
    f = re.search(r"^ideal\s+F\s*=\s*(.*?);\s*$", txt, re.S | re.M).group(1)
    fieldeqs = [_terms(g.replace("-", "+"), varpos) for g in _split_top(f)]
    return names, gens, fieldeqs


def _split_top(body: str):
    """Split a comma-separated generator list that contains no nested parens."""
    return [g for g in (s.strip() for s in body.split(",")) if g]


def main(m2p, singp):
    n_m2, g_m2, f_m2 = parse_m2(Path(m2p))
    n_sg, g_sg, f_sg = parse_sing(Path(singp))
    print(f"m2      variables: {len(n_m2)}  ideal gens: {len(g_m2)}  field eqs: {len(f_m2)}")
    print(f"sing    variables: {len(n_sg)}  ideal gens: {len(g_sg)}  field eqs: {len(f_sg)}")
    print(f"variable count equal: {len(n_m2) == len(n_sg)}")
    print(f"first 6 m2 names:   {n_m2[:6]}")
    print(f"first 6 sing names: {n_sg[:6]}")
    same_gens = set(g_m2) == set(g_sg)
    same_order = g_m2 == g_sg
    print(f"ideal generators identical as a SET (positionwise variable map): {same_gens}")
    print(f"ideal generators identical in ORDER:                            {same_order}")
    print(f"field equations identical as a set:                             {set(f_m2) == set(f_sg)}")
    print(f"field equations cover every variable (m2 / sing): "
          f"{len(f_m2) == len(n_m2)} / {len(f_sg) == len(n_sg)}")
    if not same_gens:
        only_m2 = set(g_m2) - set(g_sg)
        only_sg = set(g_sg) - set(g_m2)
        print(f"  generators only in m2:   {len(only_m2)}")
        print(f"  generators only in sing: {len(only_sg)}")
    degs_m2 = sorted({len(m) for g in g_m2 for m in g})
    degs_sg = sorted({len(m) for g in g_sg for m in g})
    print(f"monomial degrees present  m2={degs_m2}  sing={degs_sg}")
    print(f"total monomials           m2={sum(len(g) for g in g_m2)}  sing={sum(len(g) for g in g_sg)}")
    return 0 if same_gens else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
