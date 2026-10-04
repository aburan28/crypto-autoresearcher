#!/usr/bin/env python3
"""Export the n = 19 orbit-union cell as WDSat ANF instances.

Reproduces the exact instances frob_union_m2.py measured under CaDiCaL: same seed, same
subspace, same generator, same targets, same systems.  The random stream is advanced at
precisely the points the original run advanced it, so target k values coincide.

ANF row format follows crypto/src/cryptanalysis/wdsat_oracle.rs::format_anf:
  header  'p cnf <vars> <rows>'
  row     'x' then each monomial (prefixed '.d' when its degree d > 1) as 1-based ids,
          then 'T' exactly when the row's right-hand side is 0, then '0'.
A row asserts odd parity over its tokens, with T the constant 1, so 'monomials + T' means
the monomials sum to 0 and 'monomials' alone means they sum to 1.
"""
import argparse, json, math, os, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frob_union_m2 import (GF, Koblitz, random_subspace, span, sym_add, sym_sqr,
                           semaev3_sym, weil_descent)

def anf_rows_from_system(n, S):
    """-> (rows, n_monomials, max_degree); each row is (list[tuple[int]], rhs)."""
    rows, mons_seen, maxdeg = [], set(), 1
    for mons, rhs in weil_descent(n, S):
        row = [tuple(sorted(m)) for m in mons]
        for m in row:
            mons_seen.add(m); maxdeg = max(maxdeg, len(m))
        rows.append((row, rhs))
    return rows, mons_seen, maxdeg

def format_anf(n_vars, rows):
    active = [(m, r) for (m, r) in rows if m or r]
    out = [f"p cnf {n_vars} {len(active)}"]
    for mons, rhs in active:
        parts = ["x"]
        for m in mons:
            if len(m) > 1: parts.append(f".{len(m)}")
            parts.extend(str(v) for v in m)
        if not rhs: parts.append("T")
        parts.append("0")
        out.append(" ".join(parts))
    return "\n".join(out) + "\n"

def trivially_unsat(rows):
    return any(not m and r for m, r in rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=19)
    ap.add_argument('--targets', type=int, default=16)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--lprime', type=int, default=None)
    ap.add_argument('--a', type=int, default=None)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    n = args.n
    F = GF(n)
    a = args.a if args.a is not None else max((Koblitz(F, x).r, x) for x in (0, 1))[1]
    lprime = args.lprime if args.lprime is not None else max(1, math.ceil(n / 2) - math.ceil(math.log2(n)))
    llin = None
    E = Koblitz(F, a)

    # --- replicate frob_union_m2.run()'s random stream exactly -----------------
    rng = random.Random(args.seed)
    basis = random_subspace(F, lprime, rng)
    Vp = span(basis)
    S = set()
    for j in range(n):
        S |= {F.frob(v, j) for v in Vp}
    llin = math.ceil(math.log2(len(S)))
    _lin_basis = random_subspace(F, llin, rng)      # drawn in the original run too
    B = max(1, math.ceil(math.log2(n)))
    while True:
        x = rng.randrange(1, F.hi)
        if not E.on_curve_x(x): continue
        P = E.lift(x); G = E.smul(E.h, P)
        if G is not None: break
    assert E.smul(E.r, G) is None

    vt = list(range(1, lprime + 1)); vu = list(range(lprime + 1, 2 * lprime + 1))
    X1 = {frozenset([vt[k]]): basis[k] for k in range(lprime)}
    def X2_single(j): return {frozenset([vu[k]]): F.frob(basis[k], j) for k in range(lprime)}
    vs = list(range(2 * lprime + 1, 2 * lprime + n + 1))
    X2_onehot = {}
    for j in range(n):
        for k in range(lprime):
            X2_onehot[frozenset([vs[j], vu[k]])] = F.frob(basis[k], j)
    vb = list(range(2 * lprime + 1, 2 * lprime + B + 1))
    U = {frozenset([vu[k]]): basis[k] for k in range(lprime)}
    for i in range(B):
        add = {}
        for m, c in U.items():
            d = F.frob(c, 1 << i) ^ c
            if d: add[m | {vb[i]}] = d
        U = sym_add(U, add)
    X2_binary = U

    root = args.out; root.mkdir(parents=True, exist_ok=True)
    manifest = dict(n=n, a=a, r=E.r, h=E.h, lprime=lprime, S=len(S), B=B, seed=args.seed,
                    vars_single=2 * lprime, vars_onehot=2 * lprime + n, vars_binary=2 * lprime + B,
                    instances=[])
    cap = {}
    def note(arm, nv, mons, maxdeg, nrows):
        c = cap.setdefault(arm, dict(n_vars=nv, monomials=0, max_degree=1, rows=0))
        c['monomials'] = max(c['monomials'], len(mons)); c['max_degree'] = max(c['max_degree'], maxdeg)
        c['rows'] = max(c['rows'], nrows)

    for tix in range(args.targets):
        k = rng.randrange(1, E.r); R = E.smul(k, G); c = R[0]
        if c == 0: continue
        # ground truth over V' x S, identical to the CaDiCaL run
        sols = []
        for x1 in Vp:
            A = F.sqr(x1) ^ F.sqr(c); Bq = F.mul(x1, c); C = F.mul(F.sqr(x1), F.sqr(c)) ^ 1
            for x2 in F.solve_quadratic(A, Bq, C):
                if x2 in S: sols.append((x1, x2))
        rec = dict(target=tix, xR=c, gt_sat=bool(sols), gt_nsol=len(sols), files={})

        for j in range(n):
            rows, mons, md = anf_rows_from_system(n, semaev3_sym(F, X1, X2_single(j), c))
            assert not trivially_unsat(rows)
            note('single', 2 * lprime, mons, md, len(rows))
            p = root / 'single' / f"t{tix:03d}_j{j:02d}.anf"
            p.parent.mkdir(parents=True, exist_ok=True); p.write_text(format_anf(2 * lprime, rows))
        rec['files']['single'] = f"single/t{tix:03d}_j*.anf"

        rows, mons, md = anf_rows_from_system(n, semaev3_sym(F, X1, X2_onehot, c))
        rows.append(([tuple([v]) for v in vs], 1))                       # exactly one shift: XOR = 1
        for i in range(n):
            for j in range(i + 1, n):
                rows.append(([tuple(sorted((vs[i], vs[j])))], 0))        # s_i s_j = 0
                mons.add(tuple(sorted((vs[i], vs[j]))))
        assert not trivially_unsat(rows)
        note('onehot', 2 * lprime + n, mons, max(md, 2), len(rows))
        p = root / 'onehot' / f"t{tix:03d}.anf"
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(format_anf(2 * lprime + n, rows))
        rec['files']['onehot'] = f"onehot/t{tix:03d}.anf"

        rows, mons, md = anf_rows_from_system(n, semaev3_sym(F, X1, X2_binary, c))
        for val in range(n, 1 << B):                                     # forbid shift >= n
            mon = tuple(sorted(vb[i] for i in range(B) if (val >> i) & 1))
            # product over selected bits of b_i and (1 + b_i) for the rest: expand
            zero = [i for i in range(B) if not ((val >> i) & 1)]
            # forbid the assignment b = val:  prod_i (b_i + val_i + 1) = 0
            terms = [tuple()]
            for i in range(B):
                nxt = []
                for t in terms:
                    if (val >> i) & 1: nxt.append(tuple(sorted(t + (vb[i],))))
                    else:
                        nxt.append(t); nxt.append(tuple(sorted(t + (vb[i],))))
                terms = nxt
            agg = {}
            for t in terms: agg[t] = agg.get(t, 0) ^ 1
            mm = [t for t, v in agg.items() if v and t]
            const = agg.get(tuple(), 0)
            for t in mm: mons.add(t); md = max(md, len(t))
            rows.append((mm, const ^ 0))   # polynomial = 0  ->  sum(mm) = const
        assert not trivially_unsat(rows)
        note('binary', 2 * lprime + B, mons, md, len(rows))
        p = root / 'binary' / f"t{tix:03d}.anf"
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(format_anf(2 * lprime + B, rows))
        rec['files']['binary'] = f"binary/t{tix:03d}.anf"
        manifest['instances'].append(rec)
        # the measured run drew a shuffle once per target; replicate it so the
        # target scalars downstream stay identical
        order = list(range(n)); rng.shuffle(order)

    manifest['capacity'] = cap
    (root / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps(dict(cells=len(manifest['instances']), capacity=cap,
                          sat=sum(1 for i in manifest['instances'] if i['gt_sat'])), indent=2))

if __name__ == '__main__':
    main()
