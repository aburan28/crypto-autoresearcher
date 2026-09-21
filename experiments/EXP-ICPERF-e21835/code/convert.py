#!/usr/bin/env python3
"""Format converters for the Trimoska benchmark set.

* magma_to_m2      : *.in (Magma BooleanPolynomialRing) -> Macaulay2 script, ZZ/2 + field equations
* magma_to_singular: *.in -> Singular script, GF(2) + field equations
* anf_null_object  : *.anf -> matched random ANF of identical shape (same variable count,
                     same equation count, per equation the same number of terms of each
                     degree, uniformly random variable choices and constant), seeded.
* parse_anf_header : number of unary variables / equations in a WDSat ANF file
"""
from __future__ import annotations

import random
import re
from typing import List, Tuple

VAR_RE = re.compile(r"\b([xe])_(\d+)_(\d+)\b")


def _rename(t: str) -> str:
    # Macaulay2 reads x_1_0 as an indexed variable; use plain identifiers.
    return VAR_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}v{m.group(3)}", t)


def parse_magma(src: str) -> Tuple[List[str], List[str]]:
    m = re.search(r"R<([^>]*)>\s*:=\s*BooleanPolynomialRing\((\d+)", src)
    if not m:
        raise ValueError("not a Magma BooleanPolynomialRing file")
    vars_ = [v.strip() for v in m.group(1).split(",")]
    if len(vars_) != int(m.group(2)):
        raise ValueError("variable count mismatch")
    start = src.index("B := [") + len("B := [")
    body = src[start: src.index("];", start)]
    polys = [p.strip().replace("\n", " ") for p in body.split("\n,")]
    polys = [p for p in polys if p]
    return vars_, polys


def magma_to_m2(src: str, strategy: str = "F4") -> str:
    vars_, polys = parse_magma(src)
    vars_ = [_rename(v) for v in vars_]
    polys = [_rename(p) for p in polys]
    lines = [
        f"R = ZZ/2[{','.join(vars_)}, MonomialOrder => GRevLex];",
        "I = ideal(" + ",\n".join(polys) + ");",
        "F = ideal(" + ",".join(f"{v}^2-{v}" for v in vars_) + ");",
        "J = I + F;",
        "t0 = cpuTime();",
        ('G = groebnerBasis(J, Strategy => "F4");' if strategy == "F4" else "G = gens gb J;"),
        "t1 = cpuTime();",
        # D1: Macaulay2 parses a trailing underscore as its subscript operator, so
        # `gens_` is a parse error at this line, raised only after F4 completes.
        # The identifier changes; the RESULT line's byte format does not, because
        # bench.py parses it with a fixed regex.
        'gensG = flatten entries G;',
        '<< "RESULT gb_size=" << #gensG << " cpu_s=" << (t1 - t0)'
        ' << " maxdeg_gb=" << max apply(gensG, f -> first degree f)'
        ' << " is_unit=" << (any(gensG, f -> f == 1_R)) << endl;',
        "exit 0;",
    ]
    return "\n".join(lines) + "\n"


def magma_to_singular(src: str, algo: str = "std") -> str:
    vars_, polys = parse_magma(src)
    lines = [
        f"ring r = 2,({','.join(vars_)}),dp;",
        "option(redSB);",
        "ideal I = " + ",\n".join(polys) + ";",
        "ideal F = " + ",".join(f"{v}^2-{v}" for v in vars_) + ";",
        "I = I + F;",
        "int t0 = timer;",
        (f"ideal G = {algo}(I);"),
        "int t1 = timer;",
        'printf("RESULT gb_size=%s cpu_ticks=%s ticks_per_sec=%s vdim=%s maxdeg_gb=%s", '
        'size(G), t1-t0, system("--ticks-per-sec"), vdim(G), deg(G[size(G)]));',
        "quit;",
    ]
    return "\n".join(lines) + "\n"


def parse_anf_header(src: str) -> Tuple[int, int]:
    for ln in src.splitlines():
        if ln.startswith("p cnf"):
            _, _, nv, ne = ln.split()
            return int(nv), int(ne)
    raise ValueError("no header")


def _parse_anf_equation(tokens: List[str]) -> Tuple[List[List[int]], bool]:
    """tokens after the leading 'x' and before the trailing '0'. Returns (terms, constant)."""
    terms: List[List[int]] = []
    const = False
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "T":
            const = not const
            i += 1
        elif t.startswith("."):
            d = int(t[1:])
            terms.append([int(v) for v in tokens[i + 1: i + 1 + d]])
            i += 1 + d
        else:
            terms.append([int(t)])
            i += 1
    return terms, const


def anf_null_object(src: str, seed: int) -> str:
    """Random ANF with the same shape as `src`: same header, and per equation the same
    multiset of term degrees; variables drawn uniformly without repetition inside a
    term; constant term a fair coin. Duplicate monomials inside one equation are
    re-drawn so the term count is preserved exactly."""
    rng = random.Random(seed)
    nv, ne = parse_anf_header(src)
    out = []
    count = 0
    for ln in src.splitlines():
        if ln.startswith("p cnf"):
            out.append(ln)
            continue
        toks = ln.split()
        if not toks or toks[0] != "x":
            out.append(ln)
            continue
        assert toks[-1] == "0"
        terms, _const = _parse_anf_equation(toks[1:-1])
        seen = set()
        new_terms = []
        for term in terms:
            d = len(term)
            while True:
                mono = tuple(sorted(rng.sample(range(1, nv + 1), d)))
                if mono not in seen:
                    seen.add(mono)
                    break
            new_terms.append(list(mono))
        pieces = ["x"]
        for mono in new_terms:
            if len(mono) == 1:
                pieces.append(str(mono[0]))
            else:
                pieces.append(f".{len(mono)}")
                pieces.extend(str(v) for v in mono)
        if rng.random() < 0.5:
            pieces.append("T")
        pieces.append("0")
        out.append(" ".join(pieces))
        count += 1
    if count != ne:
        raise ValueError(f"equation count {count} != header {ne}")
    return "\n".join(out) + "\n"


def anf_shape(src: str) -> dict:
    """Shape descriptor used to check that a null object matches its template."""
    nv, ne = parse_anf_header(src)
    profile = []
    for ln in src.splitlines():
        toks = ln.split()
        if toks and toks[0] == "x":
            terms, _ = _parse_anf_equation(toks[1:-1])
            profile.append(sorted(len(t) for t in terms))
    return {"n_vars": nv, "n_eqs": ne, "degree_profile": profile}


if __name__ == "__main__":
    import sys

    cmd, path = sys.argv[1], sys.argv[2]
    src = open(path).read()
    if cmd == "m2":
        print(magma_to_m2(src), end="")
    elif cmd == "singular":
        print(magma_to_singular(src, sys.argv[3] if len(sys.argv) > 3 else "std"), end="")
    elif cmd == "null":
        print(anf_null_object(src, int(sys.argv[3])), end="")
    else:
        raise SystemExit("usage: convert.py m2|singular|null FILE [arg]")
