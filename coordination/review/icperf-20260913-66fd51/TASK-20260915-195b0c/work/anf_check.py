#!/usr/bin/env python3
"""Independent WDSat-ANF parser, shape fingerprint, static sizing, and a
variable-index relabelling generator.

Written for TASK-20260915-195b0c (validator, joint V2) from the format as
implemented in inputs/TRIMOSKA-WDSAT-2024/upstream/src/dimacs.c lines 120-240.
It does not import convert.py or bench.py.

Format:
  header   `p cnf <nvars> <neqs>`
  equation `x <term> <term> ... 0`, the XOR over F_2 of its terms
  terms    `T`          the constant 1 (toggles the equation constant)
           `<k>`        the degree-1 monomial x_k
           `.d v1..vd`  the degree-d monomial x_{v1}*...*x_{vd}
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path


def parse_anf(path: Path) -> dict:
    nv = ne = None
    eqs = []          # list of (const_parity, [monomial as sorted tuple of var ids])
    raw_lines = []
    for raw in path.read_text().splitlines():
        s = raw.strip()
        if not s:
            continue
        raw_lines.append(raw)
        if s.startswith("p "):
            p = s.split()
            nv, ne = int(p[2]), int(p[3])
            continue
        toks = s.split()
        if toks[0] != "x":
            raise ValueError(f"unexpected line start {toks[0]!r} in {path}")
        const = 0
        mons = []
        i = 1
        while i < len(toks):
            t = toks[i]
            if t == "0":
                break
            if t == "T":
                const ^= 1
                i += 1
                continue
            if t.startswith("."):
                d = int(t[1:])
                vs = tuple(sorted(int(x) for x in toks[i + 1:i + 1 + d]))
                if len(vs) != d:
                    raise ValueError(f"truncated degree-{d} monomial in {path}")
                mons.append(vs)
                i += 1 + d
                continue
            mons.append((int(t),))
            i += 1
        eqs.append((const, mons))
    return {"nvars": nv, "neqs_header": ne, "eqs": eqs, "path": str(path)}


def shape(a: dict) -> dict:
    """Structural fingerprint invariant under any relabelling of variable indices."""
    per_eq_degmultiset = []
    const_count = 0
    for const, mons in a["eqs"]:
        const_count += const
        per_eq_degmultiset.append(tuple(sorted(len(m) for m in mons)))
    return {
        "nvars_header": a["nvars"],
        "neqs_header": a["neqs_header"],
        "neqs_parsed": len(a["eqs"]),
        "constant_count": const_count,
        "total_terms": sum(len(m) for _, m in a["eqs"]),
        "degree_multiset_of_degree_multisets":
            sorted(Counter(per_eq_degmultiset).items()),
    }


def shape_digest(a: dict) -> dict:
    s = shape(a)
    return {k: (len(v) if k == "degree_multiset_of_degree_multisets" else v)
            for k, v in s.items()}


def sizing(a: dict) -> dict:
    """WDSat static sizing derived from the ANF.  MAX_ID = (#unary vars) +
    (#distinct monomials of degree > 1) is the quantity the frozen contract's
    invalidation rule checks against each row's wdsat_constants."""
    nv, ne = a["nvars"], len(a["eqs"])
    monos, maxdeg, maxterms = set(), 0, 0
    for _, mons in a["eqs"]:
        maxterms = max(maxterms, len(mons))
        for m in mons:
            if len(m) > 1:
                monos.add(m)
                maxdeg = max(maxdeg, len(m))
    max_id = nv + len(monos)
    return {"MAX_ANF_ID": nv + 1, "MAX_DEGREE": maxdeg + 1, "MAX_ID": max_id,
            "MAX_EQ": sum(len(m) + 1 for m in monos) + 64, "MAX_EQ_SIZE": maxdeg + 2,
            "MAX_XEQ": ne + 1, "MAX_XEQ_SIZE": max_id,
            "_nvars": nv, "_neqs": ne, "_n_monomials_deg_gt_1": len(monos),
            "_max_terms_per_eq": maxterms, "_max_degree_seen": maxdeg}


def permute_text(path: Path, perm: dict) -> str:
    """Relabel every variable index by the bijection `perm`, preserving line order,
    term order, the `T` constants and the `.d` degree prefixes.

    This is an isomorphism of the polynomial system: the same equations with the
    variables renamed.  Satisfiability, the solution count, and every degree and
    support size are preserved exactly."""
    out = []
    for raw in path.read_text().splitlines():
        s = raw.strip()
        if not s:
            out.append(raw)
            continue
        if s.startswith("p "):
            out.append(s)
            continue
        toks = s.split()
        new = [toks[0]]
        i = 1
        while i < len(toks):
            t = toks[i]
            if t == "0":
                new.append("0")
                i += 1
                continue
            if t == "T":
                new.append("T")
                i += 1
                continue
            if t.startswith("."):
                d = int(t[1:])
                vs = [perm[int(x)] for x in toks[i + 1:i + 1 + d]]
                new.append(t)
                new.extend(str(v) for v in vs)
                i += 1 + d
                continue
            new.append(str(perm[int(t)]))
            i += 1
        out.append(" ".join(new))
    return "\n".join(out) + "\n"


def make_perm(nvars: int, seed: int) -> dict:
    """Uniformly random permutation of {1..nvars} from an explicitly recorded seed,
    drawn with random.Random(seed).shuffle over the sorted index list."""
    rng = random.Random(seed)
    src = list(range(1, nvars + 1))
    dst = list(range(1, nvars + 1))
    rng.shuffle(dst)
    return dict(zip(src, dst))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "inspect":
        for p in sys.argv[2:]:
            a = parse_anf(Path(p))
            print(f"== {p}")
            print(json.dumps({"shape": shape_digest(a), "sizing": sizing(a)}, indent=1))
    elif cmd == "permute":
        src, seed, dst = Path(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
        a = parse_anf(src)
        perm = make_perm(a["nvars"], seed)
        assert sorted(perm.keys()) == sorted(perm.values()) == list(range(1, a["nvars"] + 1)), \
            "perm is not a bijection on 1..nvars"
        dst.write_text(permute_text(src, perm))
        b = parse_anf(dst)
        sa, sb = shape(a), shape(b)
        same = sa == sb
        print(json.dumps({
            "source": str(src), "target": str(dst), "seed": seed,
            "nvars": a["nvars"],
            "permutation_is_bijection": True,
            "fixed_points": sum(1 for k, v in perm.items() if k == v),
            "permutation": {str(k): v for k, v in sorted(perm.items())},
            "shape_source": shape_digest(a),
            "shape_permuted": shape_digest(b),
            "shape_identical": same,
            "shape_field_diffs": (None if same else
                                  {k: [sa[k], sb[k]] for k in sa if sa[k] != sb[k]}),
            "sizing_source": sizing(a),
            "sizing_permuted": sizing(b),
            "sizing_identical": sizing(a) == sizing(b),
        }, indent=1))
    else:
        raise SystemExit("usage: anf_check.py inspect FILE... | permute SRC SEED DST")
