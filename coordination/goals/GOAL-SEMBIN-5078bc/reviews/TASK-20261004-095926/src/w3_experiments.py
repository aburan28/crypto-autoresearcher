#!/usr/bin/env python3
"""
W3 experiments (a) and (c) of TASK-20261004-095926, from the card's text.

(a) POLYNOMIAL-RING MACAULAY MATRIX with the field equations as explicit generators and NON-square-free multipliers.
    P = F_2[x_1..x_N]; P_{<=D} = polynomials of total degree <= D, monomials = exponent vectors.
    Rows: mu * g for every generator g (degree d_g in P) and EVERY exponent vector mu with deg mu <= D - d_g
          (non-square-free multipliers included), and mu * (x_i^2 + x_i) for every mu with deg mu <= D - 2.
    U = row space.  Order on P: degree, then grevlex (x_1 largest): key(e) = (deg e, -e_N, ..., -e_1), larger = bigger monomial.
    Compare with the Boolean-ring single-level span B1 = span{mu*g : mu square-free, |mu| <= D - deg_B g} computed in B.
      claim A1: pi(U) = B1   (pi = reduction x_i^2 -> x_i)  when every generator is written square-free (deg_P g = deg_B g)
      claim A2: the SQUARE-FREE leading monomials of U equal LM(B1); every non-square-free monomial of degree <= D is an LM of U
    and a generator written with a non-square-free term where the budgets differ (deg_P g > deg_B pi(g)).
(c) SINGLE-LEVEL span (generators times multipliers only) vs ITERATED closure at small N: ranks, leading monomials, verdicts.

usage: w3_experiments.py a|c OUT.json [params]
"""
import sys, os, json, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system

D = 4


# ---------------------------------------------------------------- polynomial ring machinery
def exps_upto(N, d):
    out = []
    def rec(i, left, cur):
        if i == N:
            out.append(tuple(cur)); return
        for e in range(left + 1):
            cur.append(e); rec(i + 1, left - e, cur); cur.pop()
    rec(0, d, [])
    return out


def pkey(e):
    return (sum(e),) + tuple(-x for x in reversed(e))


def mul_exp(a, b):
    return tuple(x + y for x, y in zip(a, b))


def mask_to_exp(m, N):
    return tuple((m >> j) & 1 for j in range(N))


def poly_from_B(g, N):
    """square-free poly (frozenset of masks) -> dict exp->1"""
    return {mask_to_exp(m, N) for m in g}


def echelon_P(rows_sets, idx):
    """rows as sets of exponent tuples; returns {highest index: bitvec} (idx = ascending order position)"""
    piv = {}
    for r in rows_sets:
        x = 0
        for e in r: x ^= 1 << idx[e]
        while x:
            h = x.bit_length() - 1
            if h in piv: x ^= piv[h]
            else: piv[h] = x; break
    return piv


def macaulay_P(gens_P, N, with_field=True, nonsf_mult=True, d_override=None):
    mons = sorted(exps_upto(N, D), key=pkey)
    idx = {e: i for i, e in enumerate(mons)}
    rows = []
    for g in gens_P:
        dg = max(sum(e) for e in g)
        for mu in exps_upto(N, D - dg):
            if not nonsf_mult and any(x > 1 for x in mu): continue
            rows.append({mul_exp(mu, e) for e in g} if True else None)
    if with_field:
        for i in range(N):
            f = {tuple(2 if j == i else 0 for j in range(N)), tuple(1 if j == i else 0 for j in range(N))}
            for mu in exps_upto(N, D - 2):
                if not nonsf_mult and any(x > 1 for x in mu): continue
                rows.append({mul_exp(mu, e) for e in f})
    # symmetric difference semantics are implicit in echelon_P (xor into bit vectors); rows that cancel inside a set are handled by xor
    rows2 = []
    for g_rows in rows:
        rows2.append(g_rows)
    return mons, idx, rows2


def rows_as_sets(gens_P, N, with_field, nonsf_mult):
    """build rows with proper mod-2 cancellation inside a product (parity of coinciding monomials)"""
    mons = sorted(exps_upto(N, D), key=pkey)
    idx = {e: i for i, e in enumerate(mons)}
    out = []
    def prod(mu, g):
        s = {}
        for e in g:
            m = mul_exp(mu, e); s[m] = s.get(m, 0) ^ 1
        return {m for m, v in s.items() if v}
    for g in gens_P:
        dg = max(sum(e) for e in g)
        for mu in exps_upto(N, D - dg):
            if not nonsf_mult and any(x > 1 for x in mu): continue
            out.append(prod(mu, g))
    if with_field:
        for i in range(N):
            f = [tuple(2 if j == i else 0 for j in range(N)), tuple(1 if j == i else 0 for j in range(N))]
            for mu in exps_upto(N, D - 2):
                if not nonsf_mult and any(x > 1 for x in mu): continue
                out.append(prod(mu, f))
    return mons, idx, out


def pi_reduce_vec(x, mons, S):
    """map a bit vector over P-monomials to a bitset over the Boolean Space S (x_i^e -> x_i, e>=1)"""
    y = 0
    while x:
        low = x & -x; e = mons[low.bit_length() - 1]; x ^= low
        m = 0
        for j, ej in enumerate(e):
            if ej >= 1: m |= 1 << j
        y ^= 1 << S.pos[m]
    return y


def span_rank_and_lm_B(rows_bits):
    piv = {}
    for x in rows_bits:
        while x:
            h = x.bit_length() - 1
            if h in piv: x ^= piv[h]
            else: piv[h] = x; break
    return piv


def exp_a(out):
    rng = random.Random(3)
    results = []; nbad = 0; total = 0
    for trial in range(60):
        N = rng.choice([4, 5, 6, 7])
        M = rng.randint(2, N + 1)
        fam = rng.choice(['quad', 'sparsequad', 'planted', 'cubic'])
        gens = system(fam, N, M, trial)
        if not gens: continue
        gens_P = [poly_from_B(g, N) for g in gens]
        mons, idx, rows = rows_as_sets(gens_P, N, True, True)
        U = echelon_P(rows, idx)
        # squarefree/non-squarefree split of LM(U)
        lmU = [mons[h] for h in U]
        lm_sf = sorted(sum(1 << j for j, x in enumerate(e) if x) for e in lmU if all(x <= 1 for x in e))
        nonsf_all = [e for e in mons if any(x > 1 for x in e)]
        all_nonsf_are_LM = set(nonsf_all) <= set(lmU)
        # Boolean single-level span
        C1 = Closure(gens, N, D, gens_only=True).run()
        lmB1 = sorted(C1.lm_set())
        # pi(U) vs B1: compare subspaces
        S = C1.S
        piU = span_rank_and_lm_B([pi_reduce_vec(U[h], mons, S) for h in U])
        piU_rank = len(piU)
        B1_rank = len(C1.basis)
        both = dict(piU)
        for h, b in C1.basis.items():
            x = b
            while x:
                hh = x.bit_length() - 1
                if hh in both: x ^= both[hh]
                else: both[hh] = x; break
        same_space = (len(both) == piU_rank == B1_rank)
        lm_equal = (lm_sf == lmB1)
        total += 1
        ok = same_space and lm_equal and all_nonsf_are_LM
        if not ok: nbad += 1
        results.append(dict(family=fam, N=N, M=len(gens), seed=trial, rank_U=len(U), rank_piU=piU_rank, rank_B1=B1_rank, pi_U_equals_B1=same_space,
                            squarefree_LM_equal=lm_equal, every_nonsquarefree_monomial_is_LM_of_U=all_nonsf_are_LM))
    print('PART A (square-free generators): systems', total, 'cases where P-Macaulay with field eqs differs from the Boolean single-level span:', nbad)
    # non-square-free generator (budget mismatch): g = x1^2 x2 + x3 (deg_P 3, deg_B 2) etc.
    mism = []
    for trial in range(80):
        N = rng.choice([4, 5, 6])
        gens_P = []
        for _ in range(rng.randint(1, 3)):
            g = set()
            for _ in range(rng.randint(2, 4)):
                e = [0] * N
                for _ in range(rng.randint(1, 4)): e[rng.randrange(N)] += 1
                if sum(e) > D: continue
                e = tuple(e)
                if e in g: g.discard(e)
                else: g.add(e)
            if g: gens_P.append(g)
        if not gens_P: continue
        mons, idx, rows = rows_as_sets(gens_P, N, True, True)
        U = echelon_P(rows, idx)
        lm_sf_U = sorted(sum(1 << j for j, x in enumerate(mons[h]) if x) for h in U if all(x <= 1 for x in mons[h]))
        # Boolean-ring side: gens reduced to B (budget = deg_B of the reduced polynomial)
        gensB = []
        for g in gens_P:
            gm = {}
            for e in g:
                m = sum(1 << j for j, x in enumerate(e) if x >= 1); gm[m] = gm.get(m, 0) ^ 1
            gB = frozenset(m for m, v in gm.items() if v)
            if gB: gensB.append(gB)
        if not gensB: continue
        C1 = Closure(gensB, N, D, gens_only=True).run()
        same = (sorted(C1.lm_set()) == lm_sf_U)
        degP = [max(sum(e) for e in g) for g in gens_P]; degB = [deg(g) if False else max(popcount(m) for m in g) for g in gensB]
        if not same:
            mism.append(dict(N=N, gens_exponents=[sorted(g) for g in gens_P], degP=degP, degB=degB, LM_sf_U=len(lm_sf_U), LM_B1=len(C1.lm_set())))
    print('PART A (non-square-free generators): Boolean single-level LM differs from the P-Macaulay square-free LM in', len(mism), 'of 80 random cases')
    if mism: print(json.dumps(mism[0]))
    json.dump(dict(squarefree=results, nonsquarefree_mismatch=mism, bad=nbad), open(out, 'w'), indent=1)


def exp_c(out):
    rng = random.Random(9)
    rows = []
    strictly = 0; verdict_changes = 0; total = 0
    for fam in ['quad', 'sparsequad', 'cubic', 'bilinear', 'toeplitz', 'planted']:
        for N in range(10, 17):
            for seed in range(4):
                M = max(2, N + rng.choice([-3, -2, -1, 0, 0, 1])) if fam != 'planted' else max(2, N - rng.choice([2, 3, 4]))
                gens = system(fam, N, M, seed)
                if not gens: continue
                pts = points_of_system(N, gens); nV = len(pts)
                S1 = Closure(gens, N, D, gens_only=True).run()
                IT = Closure(gens, N, D).run()
                n1 = count_std(N, S1.lm_set()); n2 = count_std(N, IT.lm_set())
                v1, v2 = verdict(n1, nV), verdict(n2, nV)
                total += 1
                if len(IT.basis) > len(S1.basis): strictly += 1
                if v1 != v2: verdict_changes += 1
                rows.append(dict(family=fam, N=N, M=len(gens), seed=seed, V=nV, rank_single=len(S1.basis), rank_iterated=len(IT.basis), verdict_single=v1, verdict_iterated=v2,
                                 N_std_single=n1, N_std_iterated=n2, strictly_larger=len(IT.basis) > len(S1.basis), verdict_changes=(v1 != v2),
                                 opposite_verdicts=((v1 == 'sufficient') != (v2 == 'sufficient')) and (v1 == 'sufficient')))
    opp = [r for r in rows if r['opposite_verdicts']]
    print('PART C: systems', total, '| iterated strictly larger than single-level:', strictly, '| verdict changes (single -> iterated):', verdict_changes,
          '| single-level says sufficient but iterated insufficient (impossible by polarity):', len(opp))
    json.dump(dict(rows=rows, strictly_larger=strictly, verdict_changes=verdict_changes, total=total), open(out, 'w'), indent=1)


if __name__ == '__main__':
    dict(a=exp_a, c=exp_c)[sys.argv[1]](sys.argv[2])
