#!/usr/bin/env python3
"""
Independent parser / emitter for the Trimoska ECICB Weil-descent instances.

Written for REVIEW-ICPERF-20260915-a33cda joint R6 (TASK-20260915-abf147).
This is the reviewer's OWN conversion route. It reads only the upstream
instance files shipped under inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/
and was written from the WDSAT README (ANF format) and the upstream generator
Weil_descent.sage, both of which the assignment permits.

Polynomials over GF(2) are represented as a set of monomials; a monomial is a
frozenset of 0-based variable indices (frozenset() is the constant 1).
Addition is symmetric difference. Because every engine run adds the field
equations v^2 + v, monomials are kept multilinear throughout.

Semantics used for the ANF encoding (from the WDSAT README and the generator):
  * a line  `x <terms> 0`  is an XOR clause that must evaluate to TRUE;
  * `T` is the constant true;
  * `.d v1 ... vd` is the degree-d monomial v1*...*vd; a bare integer is a
    degree-1 monomial;
  * hence the polynomial that must vanish is  sum(terms) + 1, where T counts
    as 1 -- i.e. `x T ...` has no constant term and `x ...` (no T) has +1.

Variable numbering (from get_ANF_output_X / get_ANF_output_E in the generator):
  ANF 1..15  <-> x_1_0..x_1_4, x_2_0..x_2_4, x_3_0..x_3_4  (Magma order)
  ANF 16..42 <-> e_1_0..e_1_4, e_2_0..e_2_8, e_3_0..e_3_12 (Magma order)
This correspondence is CHECKED, not assumed: the two encodings are parsed
separately and compared polynomial by polynomial.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path

Monomial = frozenset
Poly = set  # set of Monomial


# ----------------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------------
def parse_anf(path: Path) -> tuple[int, list[Poly]]:
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    header = lines[0].split()
    assert header[0] == "p" and header[1] == "cnf", header
    nvars, neqs = int(header[2]), int(header[3])
    polys: list[Poly] = []
    for ln in lines[1:]:
        toks = ln.split()
        assert toks[0] == "x", ln
        assert toks[-1] == "0", ln
        body = toks[1:-1]
        has_T = False
        poly: Poly = set()
        i = 0
        while i < len(body):
            t = body[i]
            if t == "T":
                has_T = True
                i += 1
            elif t.startswith("."):
                d = int(t[1:])
                vs = body[i + 1 : i + 1 + d]
                assert len(vs) == d, ln
                idx = [int(v) - 1 for v in vs]
                assert all(0 <= k < nvars for k in idx), ln
                assert len(set(idx)) == d, ("repeated variable inside a conjunction", ln)
                poly ^= {Monomial(idx)}
                i += 1 + d
            else:
                k = int(t) - 1
                assert 0 <= k < nvars, ln
                poly ^= {Monomial([k])}
                i += 1
        if not has_T:
            poly ^= {Monomial()}
        polys.append(poly)
    assert len(polys) == neqs, (len(polys), neqs)
    return nvars, polys


def parse_magma(path: Path) -> tuple[list[str], list[Poly]]:
    text = path.read_text()
    m = re.search(r"R<([^>]*)>\s*:=\s*BooleanPolynomialRing\((\d+)\s*,\s*\"(\w+)\"\)", text)
    assert m, "ring declaration not found"
    names = [s.strip() for s in m.group(1).split(",")]
    assert len(names) == int(m.group(2)), (len(names), m.group(2))
    order = m.group(3)
    index = {nm: i for i, nm in enumerate(names)}
    mb = re.search(r"B\s*:=\s*\[(.*?)\];", text, re.S)
    assert mb, "B := [...] block not found"
    polys: list[Poly] = []
    zero_terms_seen = 0
    for chunk in mb.group(1).split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        poly: Poly = set()
        for term in chunk.split("+"):
            term = term.strip()
            assert term, chunk
            if term == "1":
                poly ^= {Monomial()}
                continue
            if term == "0":
                # Shipped .in files carry a literal leading "0 + ..." in several
                # descent equations (generator printing artifact).  A zero term
                # contributes no monomial.  Counted so the report can say so.
                zero_terms_seen += 1
                continue
            factors = [f.strip() for f in term.split("*")]
            assert all("^" not in f for f in factors), ("unexpected power", term)
            idx = [index[f] for f in factors]
            assert len(set(idx)) == len(idx), ("repeated variable in term", term)
            poly ^= {Monomial(idx)}
        polys.append(poly)
    parse_magma.zero_terms_seen = zero_terms_seen  # type: ignore[attr-defined]
    return names, polys, order


# ----------------------------------------------------------------------------
# Evaluation / brute force
# ----------------------------------------------------------------------------
def eval_poly(poly: Poly, assignment: list[int]) -> int:
    s = 0
    for mono in poly:
        prod = 1
        for k in mono:
            if not assignment[k]:
                prod = 0
                break
        s ^= prod
    return s


def split_system(polys: list[Poly], n_x: int):
    """Split into (defining equations e_j + f_j(x), descent equations in e only).

    A defining equation contains exactly one monomial that is a single e-variable
    and every other monomial uses x-variables only.
    """
    defs: dict[int, Poly] = {}
    rest: list[Poly] = []
    for p in polys:
        e_lin = [m for m in p if len(m) == 1 and next(iter(m)) >= n_x]
        others = [m for m in p if not (len(m) == 1 and next(iter(m)) >= n_x)]
        if len(e_lin) == 1 and all(all(k < n_x for k in m) for m in others):
            j = next(iter(e_lin[0]))
            assert j not in defs
            defs[j] = set(others)
        else:
            rest.append(p)
    return defs, rest


def brute_force(polys: list[Poly], nvars: int, n_x: int):
    defs, rest = split_system(polys, n_x)
    e_indices = sorted(defs)
    solutions = []
    for bits in itertools.product((0, 1), repeat=n_x):
        a = list(bits) + [0] * (nvars - n_x)
        for j in e_indices:
            a[j] = eval_poly(defs[j], a)
        if all(eval_poly(p, a) == 0 for p in rest):
            # full re-check of every polynomial, including the defining ones
            assert all(eval_poly(p, a) == 0 for p in polys)
            solutions.append(tuple(a))
    return solutions, len(defs), len(rest)


# ----------------------------------------------------------------------------
# Emission
# ----------------------------------------------------------------------------
def default_names(names_magma: list[str]) -> list[str]:
    """Engine-safe names: x_1_0 -> xa0, e_3_12 -> ec12 (no underscores; M2 parses
    `x_1_0` as a subscript expression)."""
    out = []
    for nm in names_magma:
        kind, grp, pos = nm.split("_")
        out.append(f"{kind}{'abc'[int(grp) - 1]}{pos}")
    assert len(set(out)) == len(out)
    return out


def poly_to_str(poly: Poly, names: list[str], mul: str = "*") -> str:
    if not poly:
        return "0"
    terms = []
    for mono in sorted(poly, key=lambda m: (-len(m), sorted(m))):
        if len(mono) == 0:
            terms.append("1")
        else:
            terms.append(mul.join(names[k] for k in sorted(mono)))
    return " + ".join(terms)


def apply_perturbation(polys: list[Poly], spec: str | None, names: list[str]) -> tuple[list[Poly], str]:
    """spec forms:
        None                       -> unchanged
        add:<eq_index_1based>:<mono>  e.g. add:28:xa0  or add:16:xa0*xb0
        del:<eq_index_1based>
    """
    polys = [set(p) for p in polys]
    if spec is None:
        return polys, "none"
    kind, *rest = spec.split(":")
    if kind == "add":
        eq = int(rest[0]) - 1
        mono = Monomial(names.index(v) for v in rest[1].split("*"))
        before = poly_to_str(polys[eq], names)
        polys[eq] ^= {mono}
        after = poly_to_str(polys[eq], names)
        return polys, f"added monomial {rest[1]} to equation #{eq + 1}: [{before}] -> [{after}]"
    if kind == "del":
        eq = int(rest[0]) - 1
        removed = poly_to_str(polys[eq], names)
        del polys[eq]
        return polys, f"deleted equation #{eq + 1}: [{removed}]"
    raise SystemExit(f"unknown perturbation {spec}")


def emit_m2(polys: list[Poly], names: list[str], order: str, var_order: list[int], also_default_gb: bool, strategy: str = "F4") -> str:
    vn = [names[k] for k in var_order]
    lines = []
    lines.append("-- Emitted by parse_instance.py (TASK-20260915-abf147, reviewer's own conversion).")
    lines.append(f"-- {len(polys)} instance polynomials + {len(names)} field equations over ZZ/2.")
    lines.append(f"R = ZZ/2[{', '.join(vn)}, MonomialOrder => {order}];")
    lines.append("F = {")
    lines.append(",\n".join("  " + poly_to_str(p, names) for p in polys))
    lines.append("};")
    lines.append("FE = apply(gens R, v -> v^2 + v);")
    lines.append("I = ideal(F | FE);")
    lines.append('<< "NUM_INPUT_POLYS " << #F << endl;')
    lines.append('<< "NUM_VARS " << numgens R << endl;')
    lines.append('<< "MONOMIAL_ORDER " << toString (options R).MonomialOrder << endl;')
    lines.append("t0 = cpuTime();")
    lines.append(f'G = groebnerBasis(I, Strategy => "{strategy}");')
    lines.append("t1 = cpuTime();")
    lines.append("gl = flatten entries G;")
    lines.append('<< "F4_CPU_SECONDS " << (t1 - t0) << endl;')
    lines.append('<< "GB_CARDINALITY " << #gl << endl;')
    lines.append('<< "GB_MAXDEG " << max apply(gl, g -> first degree g) << endl;')
    lines.append('<< "GB_IS_UNIT " << toString any(gl, g -> g == 1_R) << endl;')
    lines.append('<< "GB_DEGREE_HISTOGRAM " << toString tally apply(gl, g -> first degree g) << endl;')
    lines.append('<< "GB_LEADTERMS_LINEAR " << #select(gl, g -> first degree leadTerm g == 1) << endl;')
    lines.append("-- quotient dimension from the F4 basis, installed as a GB via forceGB")
    lines.append("t2 = cpuTime();")
    lines.append("Gf = forceGB G;")
    lines.append("J = ideal G;")
    lines.append('<< "GB_KRULL_DIM " << dim J << endl;')
    lines.append('<< "GB_QUOTIENT_DIM " << (if dim J == 0 then degree J else "not_zero_dimensional") << endl;')
    lines.append('<< "DEGREE_CPU_SECONDS " << (cpuTime() - t2) << endl;')
    if also_default_gb:
        lines.append("-- reducedness cross-check: rerun the default engine on the F4 output and compare")
        lines.append("t3 = cpuTime();")
        lines.append("J2 = ideal matrix {gl};")
        lines.append("G2 = flatten entries gens gb J2;")
        lines.append('<< "DEFAULT_GB_CPU_SECONDS " << (cpuTime() - t3) << endl;')
        lines.append('<< "DEFAULT_GB_CARDINALITY " << #G2 << endl;')
        lines.append('<< "DEFAULT_GB_EQUALS_F4_AS_SET " << toString (set G2 === set gl) << endl;')
    lines.append('<< "GB_ELEMENTS_BEGIN" << endl;')
    lines.append("scan(gl, g -> << toString g << endl);")
    lines.append('<< "GB_ELEMENTS_END" << endl;')
    lines.append("exit 0;")
    return "\n".join(lines) + "\n"


def emit_singular(polys: list[Poly], names: list[str], order: str, var_order: list[int], algo: str) -> str:
    vn = [names[k] for k in var_order]
    lines = []
    lines.append("// Emitted by parse_instance.py (TASK-20260915-abf147, reviewer's own conversion).")
    lines.append(f"// {len(polys)} instance polynomials + {len(names)} field equations over GF(2).")
    lines.append(f"ring r = 2, ({', '.join(vn)}), {order};")
    lines.append("ideal I;")
    for i, p in enumerate(polys, 1):
        lines.append(f"I[{i}] = {poly_to_str(p, names)};")
    lines.append(f"int nF = {len(polys)};")
    lines.append("int k;")
    lines.append("for (k = 1; k <= nvars(r); k++) { I[nF + k] = var(k)^2 + var(k); }")
    lines.append("option(redSB);")
    lines.append('print("NUM_INPUT_POLYS " + string(nF));')
    lines.append('print("NUM_VARS " + string(nvars(r)));')
    lines.append("int t0 = timer;")
    lines.append(f"ideal G = {algo}(I);")
    lines.append('print("GB_CPU_SECONDS_INTEGER " + string(timer - t0));')
    lines.append("G = simplify(G, 2);")  # drop zero generators, if any
    lines.append('print("GB_CARDINALITY " + string(size(G)));')
    lines.append("int md = 0;")
    lines.append("for (k = 1; k <= size(G); k++) { if (deg(G[k]) > md) { md = deg(G[k]); } }")
    lines.append('print("GB_MAXDEG " + string(md));')
    lines.append("int isunit = 0;")
    lines.append("for (k = 1; k <= size(G); k++) { if (G[k] == 1) { isunit = 1; } }")
    lines.append('print("GB_IS_UNIT " + string(isunit));')
    lines.append('print("GB_KRULL_DIM " + string(dim(G)));')
    lines.append('print("GB_QUOTIENT_DIM " + string(vdim(G)));')
    lines.append('print("GB_ELEMENTS_BEGIN");')
    lines.append("for (k = 1; k <= size(G); k++) { print(string(G[k])); }")
    lines.append('print("GB_ELEMENTS_END");')
    lines.append("quit;")
    return "\n".join(lines) + "\n"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------
# GB post-checks on engine output.
#
# The engine works in the POLYNOMIAL ring GF(2)[v_1..v_n] with the field
# equations v^2+v added as ordinary generators, so its reduced basis may
# contain non-multilinear elements (e.g. v^2+v itself).  Here a monomial is an
# exponent tuple in RING ORDER (position 0 = first generator), a polynomial is
# a set of such tuples (all coefficients are 1 over GF(2)), and addition is
# symmetric difference.
# ----------------------------------------------------------------------------
ExpMono = tuple


def parse_engine_polys(text: str, names: list[str], var_order: list[int]) -> list[set]:
    """Read the polynomials printed between GB_ELEMENTS_BEGIN/END (M2 or Singular
    textual form: terms joined by '+', factors by '*', powers as v^k)."""
    nvars = len(names)
    pos_of_var = {names[k]: i for i, k in enumerate(var_order)}  # ring position
    block = text.split("GB_ELEMENTS_BEGIN", 1)[1].split("GB_ELEMENTS_END", 1)[0]
    out: list[set] = []
    for ln in block.strip().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        poly: set = set()
        for term in ln.replace("-", "+").split("+"):
            term = term.strip()
            if not term:
                continue
            exps = [0] * nvars
            if term != "1":
                for f in term.split("*"):
                    f = f.strip()
                    mm = re.fullmatch(r"([a-z]+\d+)(?:\^(\d+))?", f)
                    assert mm, (f, ln)
                    exps[pos_of_var[mm.group(1)]] += int(mm.group(2) or 1)
            poly ^= {ExpMono(exps)}
        out.append(poly)
    return out


def grevlex_key(mono: ExpMono):
    """Higher key = larger monomial under graded reverse lexicographic order:
    first total degree, then the LAST position with a differing exponent decides
    and the SMALLER exponent there is the LARGER monomial."""
    return (sum(mono), tuple(-e for e in reversed(mono)))


def lex_key(mono: ExpMono):
    return tuple(mono)


def lead_monomial(poly: set, key):
    return max(poly, key=key)


def divides(a: ExpMono, b: ExpMono) -> bool:
    return all(x <= y for x, y in zip(a, b))


def mono_str(m: ExpMono, ring_names: list[str]) -> str:
    fs = [f"{ring_names[i]}" + (f"^{e}" if e > 1 else "") for i, e in enumerate(m) if e]
    return "*".join(fs) if fs else "1"


def check_reduced_gb(polys: list[set], ring_names: list[str], order: str) -> dict:
    key = grevlex_key if order == "grevlex" else lex_key
    lts = [lead_monomial(p, key) for p in polys]
    problems = []
    for i, a in enumerate(lts):
        for j, b in enumerate(lts):
            if i != j and divides(a, b):
                problems.append(f"LT(#{i}) = {mono_str(a, ring_names)} divides LT(#{j}) = {mono_str(b, ring_names)} -> basis not minimal")
    for i, p in enumerate(polys):
        for m in p:
            for j, b in enumerate(lts):
                if j != i and divides(b, m):
                    problems.append(
                        f"monomial {mono_str(m, ring_names)} of element #{i} is divisible by LT(#{j}) = {mono_str(b, ring_names)} -> not reduced"
                    )
    degs = [max(sum(m) for m in p) for p in polys]
    return {
        "cardinality": len(polys),
        "max_total_degree": max(degs) if degs else 0,
        "degree_histogram": {str(d): degs.count(d) for d in sorted(set(degs))},
        "contains_1": any(p == {ExpMono([0] * len(ring_names))} for p in polys),
        "num_field_equations_present": sum(1 for p in polys if len(p) == 2 and all(sum(m) in (1, 2) for m in p) and len([m for m in p if max(m) == 2]) == 1 and all(len([e for e in m if e]) == 1 for m in p)),
        "num_linear_lead_terms": sum(1 for lt in lts if sum(lt) == 1),
        "num_nonmultilinear_elements": sum(1 for p in polys if any(max(m) > 1 for m in p)),
        "minimal_and_reduced": not problems,
        "problems": problems[:20],
        "order_checked": order,
    }


def s_poly_reduces_to_zero(polys: list[set], order: str) -> tuple[bool, int]:
    """Buchberger criterion over GF(2) in the polynomial ring, exponent-tuple
    arithmetic.  Returns (all_S_polys_reduce_to_zero, pairs_checked)."""
    key = grevlex_key if order == "grevlex" else lex_key
    basis = [set(p) for p in polys]
    lts = [lead_monomial(p, key) for p in basis]

    def mul(m: ExpMono, f: set) -> set:
        return {ExpMono(a + b for a, b in zip(m, g)) for g in f}

    def reduce(f: set) -> set:
        f = set(f)
        while f:
            progressed = False
            for m in sorted(f, key=key, reverse=True):
                for g, lt in zip(basis, lts):
                    if divides(lt, m):
                        q = ExpMono(a - b for a, b in zip(m, lt))
                        f ^= mul(q, g)
                        progressed = True
                        break
                if progressed:
                    break
            if not progressed:
                break
        return f

    pairs = 0
    for i in range(len(basis)):
        for j in range(i + 1, len(basis)):
            a, b = lts[i], lts[j]
            # Buchberger's first criterion: coprime leading terms reduce to zero
            if all(x == 0 or y == 0 for x, y in zip(a, b)):
                continue
            l = ExpMono(max(x, y) for x, y in zip(a, b))
            s = mul(ExpMono(x - y for x, y in zip(l, a)), basis[i]) ^ mul(ExpMono(x - y for x, y in zip(l, b)), basis[j])
            pairs += 1
            if reduce(s):
                return False, pairs
    return True, pairs


def normal_form_zero(f_multilinear: Poly, var_order: list[int], gb: list[set], order: str) -> bool:
    """Is the input polynomial (multilinear representation, instance indices) in
    the ideal generated by the printed GB together with the field equations?
    Reduce modulo GB U {v^2+v} in the polynomial ring."""
    key = grevlex_key if order == "grevlex" else lex_key
    nvars = len(var_order)
    rank = {k: i for i, k in enumerate(var_order)}
    f: set = set()
    for m in f_multilinear:
        e = [0] * nvars
        for k in m:
            e[rank[k]] = 1
        f ^= {ExpMono(e)}
    basis = [set(p) for p in gb]
    for i in range(nvars):
        sq = [0] * nvars
        sq[i] = 2
        lin = [0] * nvars
        lin[i] = 1
        basis.append({ExpMono(sq), ExpMono(lin)})
    lts = [lead_monomial(p, key) for p in basis]

    def mul(m: ExpMono, g: set) -> set:
        return {ExpMono(a + b for a, b in zip(m, h)) for h in g}

    while f:
        progressed = False
        for m in sorted(f, key=key, reverse=True):
            for g, lt in zip(basis, lts):
                if divides(lt, m):
                    f ^= mul(ExpMono(a - b for a, b in zip(m, lt)), g)
                    progressed = True
                    break
            if progressed:
                break
        if not progressed:
            return False
    return True


def buchberger_reduced(gens: list[set], nvars: int, order: str) -> list[set]:
    """Own Buchberger over GF(2) with exponent tuples; returns the REDUCED GB
    (minimal, tail-reduced, sorted by decreasing leading monomial).  Field
    equations are added so the result is the reduced GB of <gens> + <v^2+v>."""
    key = grevlex_key if order == "grevlex" else lex_key

    def mul(m: ExpMono, g: set) -> set:
        return {ExpMono(a + b for a, b in zip(m, h)) for h in g}

    def lt(p: set) -> ExpMono:
        return max(p, key=key)

    def normal_form(f: set, basis: list[set]) -> set:
        f = set(f)
        result: set = set()
        lts = [lt(g) for g in basis]
        while f:
            m = lt(f)
            for g, l in zip(basis, lts):
                if divides(l, m):
                    f ^= mul(ExpMono(a - b for a, b in zip(m, l)), g)
                    break
            else:
                f.discard(m)
                result ^= {m}
        return result

    G: list[set] = [set(g) for g in gens if g]
    for i in range(nvars):
        sq = [0] * nvars
        sq[i] = 2
        li = [0] * nvars
        li[i] = 1
        G.append({ExpMono(sq), ExpMono(li)})
    pairs = [(i, j) for i in range(len(G)) for j in range(i)]
    while pairs:
        i, j = pairs.pop()
        a, b = lt(G[i]), lt(G[j])
        if all(x == 0 or y == 0 for x, y in zip(a, b)):
            continue
        l = ExpMono(max(x, y) for x, y in zip(a, b))
        s = mul(ExpMono(x - y for x, y in zip(l, a)), G[i]) ^ mul(ExpMono(x - y for x, y in zip(l, b)), G[j])
        r = normal_form(s, G)
        if r:
            G.append(r)
            pairs.extend((len(G) - 1, k) for k in range(len(G) - 1))
    # minimalise
    lts = [lt(g) for g in G]
    keep = [i for i, a in enumerate(lts) if not any(j != i and divides(lts[j], a) and (lts[j] != a or j < i) for j in range(len(G)))]
    G = [G[i] for i in keep]
    # tail-reduce
    reduced: list[set] = []
    for i, g in enumerate(G):
        others = G[:i] + G[i + 1 :]
        reduced.append(normal_form(g, others) if others else set(g))
    reduced.sort(key=lambda p: key(lt(p)), reverse=True)
    return reduced


def eval_exp_poly(poly: set, assignment_ring_order: list[int]) -> int:
    s = 0
    for m in poly:
        if all(assignment_ring_order[i] for i, e in enumerate(m) if e):
            s ^= 1
    return s


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default="/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks")
    ap.add_argument("--instance", default="n15l5-1-S")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("inspect", help="parse both encodings, compare, brute-force solutions")
    s1.add_argument("--perturb", default=None)
    s1.add_argument("--out", required=True)

    s2 = sub.add_parser("emit", help="emit engine input")
    s2.add_argument("--engine", choices=["m2", "singular"], required=True)
    s2.add_argument("--order", default=None, help="M2: GRevLex|Lex ; Singular: dp|lp")
    s2.add_argument("--var-order", choices=["magma", "reversed", "e-first"], default="magma")
    s2.add_argument("--perturb", default=None)
    s2.add_argument("--singular-algo", default="std")
    s2.add_argument("--also-default-gb", action="store_true")
    s2.add_argument("--m2-strategy", default="F4", help='M2 groebnerBasis Strategy: "F4" or "MGB"')
    s2.add_argument("--out", required=True)

    s3 = sub.add_parser("check-output", help="verify a printed GB is minimal+reduced, recompute (1),(2),(3)")
    s3.add_argument("--engine-output", required=True)
    s3.add_argument("--var-order", choices=["magma", "reversed", "e-first"], default="magma")
    s3.add_argument("--order", choices=["grevlex", "lex"], default="grevlex")
    s3.add_argument("--perturb", default=None)
    s3.add_argument("--buchberger", action="store_true")
    s3.add_argument("--out", required=True)

    s4 = sub.add_parser("own-gb", help="own Buchberger: reduced GB in another order, starting from a verified engine basis")
    s4.add_argument("--engine-output", required=True)
    s4.add_argument("--source-var-order", choices=["magma", "reversed", "e-first"], default="magma")
    s4.add_argument("--target-order", choices=["grevlex", "lex"], required=True)
    s4.add_argument("--target-var-order", choices=["magma", "reversed", "e-first"], required=True)
    s4.add_argument("--perturb", default=None)
    s4.add_argument("--out", required=True)

    args = ap.parse_args()
    bench = Path(args.bench)
    anf_path = bench / f"X{args.instance}.anf"
    magma_path = bench / f"{args.instance}.in"
    info_path = bench / f"INFO{args.instance}.dimacs"

    nvars, anf_polys = parse_anf(anf_path)
    names_magma, magma_polys, magma_order = parse_magma(magma_path)
    assert len(names_magma) == nvars
    names = default_names(names_magma)
    n_x = sum(1 for nm in names_magma if nm.startswith("x_"))

    same_order = anf_polys == magma_polys
    same_set = {frozenset(p) for p in anf_polys} == {frozenset(p) for p in magma_polys}

    def var_order_of(kind: str) -> list[int]:
        if kind == "magma":
            return list(range(nvars))
        if kind == "reversed":
            return list(range(nvars))[::-1]
        if kind == "e-first":
            return list(range(n_x, nvars)) + list(range(n_x))
        raise SystemExit(kind)

    if args.cmd == "inspect":
        polys, pdesc = apply_perturbation(anf_polys, args.perturb, names)
        sols, ndefs, nrest = brute_force(polys, nvars, n_x)
        info = info_path.read_text().splitlines()
        planted = None
        if len(info) >= 5 and info[3].strip() == "S":
            bits = "".join(info[4].strip().split("-"))
            planted = [int(c) for c in bits]
        planted_is_solution = None
        if planted is not None:
            planted_full = [s[:n_x] for s in sols]
            planted_is_solution = tuple(planted) in {tuple(x) for x in planted_full}
        # the system is symmetric under permuting the three x-blocks; report orbit structure
        rec = {
            "instance": args.instance,
            "files": {
                "anf": {"path": str(anf_path), "sha256": sha256_file(anf_path)},
                "magma_in": {"path": str(magma_path), "sha256": sha256_file(magma_path)},
                "info": {"path": str(info_path), "sha256": sha256_file(info_path), "content": info},
            },
            "nvars": nvars,
            "n_x_vars": n_x,
            "n_e_vars": nvars - n_x,
            "num_polys_anf": len(anf_polys),
            "num_polys_magma": len(magma_polys),
            "magma_declared_order": magma_order,
            "magma_literal_zero_terms_seen": getattr(parse_magma, "zero_terms_seen", None),
            "anf_and_magma_identical_in_order": same_order,
            "anf_and_magma_identical_as_sets": same_set,
            "anf_polys_with_constant_term_1": sum(1 for p in anf_polys if Monomial() in p),
            "first_differing_equation_index_1based": next((i + 1 for i, (a, b) in enumerate(zip(anf_polys, magma_polys)) if a != b), None),
            "degree_histogram_of_input": {
                str(d): sum(1 for p in anf_polys if max(len(m) for m in p) == d) for d in range(0, 5)
            },
            "perturbation": pdesc,
            "num_defining_equations": ndefs,
            "num_descent_equations": nrest,
            "brute_force_num_solutions_over_GF2": len(sols),
            "brute_force_solutions_x_bits": ["".join(map(str, s[:n_x])) for s in sols],
            "brute_force_solutions_full": ["".join(map(str, s)) for s in sols],
            "planted_solution_from_INFO_x_bits": "".join(map(str, planted)) if planted else None,
            "planted_solution_is_a_solution": planted_is_solution,
            "variable_names_engine": names,
            "variable_names_magma": names_magma,
        }
        Path(args.out).write_text(json.dumps(rec, indent=2) + "\n")
        print(json.dumps({k: v for k, v in rec.items() if k not in ("brute_force_solutions_full", "variable_names_engine", "variable_names_magma")}, indent=2))
        return

    if args.cmd == "emit":
        polys, pdesc = apply_perturbation(anf_polys, args.perturb, names)
        vo = var_order_of(args.var_order)
        if args.engine == "m2":
            text = emit_m2(polys, names, args.order or "GRevLex", vo, args.also_default_gb, args.m2_strategy)
        else:
            text = emit_singular(polys, names, args.order or "dp", vo, args.singular_algo)
        header = f"{'--' if args.engine == 'm2' else '//'} perturbation: {pdesc}\n{'--' if args.engine == 'm2' else '//'} variable order: {args.var_order} ({[names[k] for k in vo][:3]} ... {[names[k] for k in vo][-3:]})\n"
        out = Path(args.out)
        out.write_text(header + text)
        print(json.dumps({"emitted": str(out), "sha256": sha256_file(out), "perturbation": pdesc, "num_polys": len(polys)}))
        return

    if args.cmd == "check-output":
        text = Path(args.engine_output).read_text()
        vo = var_order_of(args.var_order)
        ring_names = [names[k] for k in vo]
        gb = parse_engine_polys(text, names, vo)
        rec = check_reduced_gb(gb, ring_names, args.order)
        if args.buchberger:
            ok, pairs = s_poly_reduces_to_zero(gb, args.order)
            rec["buchberger_all_s_polys_reduce_to_zero"] = ok
            rec["buchberger_pairs_checked_after_coprime_criterion"] = pairs
        rec["engine_output"] = str(args.engine_output)
        rec["engine_output_sha256"] = sha256_file(Path(args.engine_output))
        # the GB must vanish on every brute-force GF(2) solution of the (possibly
        # perturbed) input system; this ties the engine's basis back to the
        # instance files through a route that never touches the engine.
        polys, pdesc = apply_perturbation(anf_polys, args.perturb, names)
        sols, _, _ = brute_force(polys, nvars, n_x)
        rec["perturbation"] = pdesc
        rec["brute_force_num_solutions"] = len(sols)
        rec["gb_vanishes_on_all_brute_force_solutions"] = all(
            eval_exp_poly(g, [s[k] for k in vo]) == 0 for g in gb for s in sols
        )
        # Ideal equality without trusting the engine: (a) every input polynomial
        # reduces to zero modulo GB U field equations  =>  I + FE  subset of (GB);
        # (b) GB vanishes on every GF(2) zero of I  =>  (GB) subset of  I + FE,
        # because I + FE is radical with all zeros in GF(2)^n.
        rec["all_input_polys_reduce_to_zero_mod_gb"] = all(normal_form_zero(p, vo, gb, args.order) for p in polys)
        rec["ideal_equality_established"] = bool(
            rec["all_input_polys_reduce_to_zero_mod_gb"] and rec["gb_vanishes_on_all_brute_force_solutions"]
        )
        Path(args.out).write_text(json.dumps(rec, indent=2) + "\n")
        print(json.dumps(rec, indent=2))
        return

    if args.cmd == "own-gb":
        import time as _time

        text = Path(args.engine_output).read_text()
        src_vo = var_order_of(args.source_var_order)
        tgt_vo = var_order_of(args.target_var_order)
        src_gb = parse_engine_polys(text, names, src_vo)
        # re-index exponent tuples from source ring positions to target ring positions
        tgt_rank = {k: i for i, k in enumerate(tgt_vo)}

        def reindex(p: set) -> set:
            out = set()
            for m in p:
                e = [0] * nvars
                for pos, ex in enumerate(m):
                    if ex:
                        e[tgt_rank[src_vo[pos]]] = ex
                out ^= {ExpMono(e)}
            return out

        gens = [reindex(p) for p in src_gb]
        t0 = _time.time()
        gb = buchberger_reduced(gens, nvars, args.target_order)
        elapsed = _time.time() - t0
        ring_names = [names[k] for k in tgt_vo]
        rec = check_reduced_gb(gb, ring_names, args.target_order)
        ok, pairs = s_poly_reduces_to_zero(gb, args.target_order)
        rec["buchberger_all_s_polys_reduce_to_zero"] = ok
        rec["buchberger_pairs_checked_after_coprime_criterion"] = pairs
        polys, pdesc = apply_perturbation(anf_polys, args.perturb, names)
        sols, _, _ = brute_force(polys, nvars, n_x)
        rec["perturbation"] = pdesc
        rec["brute_force_num_solutions"] = len(sols)
        rec["gb_vanishes_on_all_brute_force_solutions"] = all(eval_exp_poly(g, [s[k] for k in tgt_vo]) == 0 for g in gb for s in sols)
        rec["all_input_polys_reduce_to_zero_mod_gb"] = all(normal_form_zero(p, tgt_vo, gb, args.target_order) for p in polys)
        rec["ideal_equality_established"] = bool(rec["all_input_polys_reduce_to_zero_mod_gb"] and rec["gb_vanishes_on_all_brute_force_solutions"])
        rec["method"] = "own Buchberger (Python, exponent tuples over GF(2)) started from the verified engine basis plus field equations; NOT an engine run"
        rec["source_engine_output"] = str(args.engine_output)
        rec["source_engine_output_sha256"] = sha256_file(Path(args.engine_output))
        rec["target_order"] = args.target_order
        rec["target_var_order"] = args.target_var_order
        rec["ring_variable_order"] = ring_names
        rec["own_buchberger_seconds"] = round(elapsed, 3)
        rec["elements"] = [
            " + ".join(mono_str(m, ring_names) for m in sorted(p, key=(grevlex_key if args.target_order == "grevlex" else lex_key), reverse=True))
            for p in gb
        ]
        Path(args.out).write_text(json.dumps(rec, indent=2) + "\n")
        print(json.dumps({k: v for k, v in rec.items() if k != "elements"}, indent=2))
        print("nonlinear elements:", [e for e in rec["elements"] if "*" in e or "^" in e])
        return


if __name__ == "__main__":
    main()
