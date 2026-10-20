import sys, time, random, itertools
sys.path.insert(0, '../../experiments/EXP-SEMBIN-d9767f/implementation/vendor')
import boolsys as bs
from boolsys import GF2n, modulus_for, fadd, fmul, fsquare, s3, descend, linear_form


def build(n, shape, k, B, basis, z):
    """descended equations list: structural first, then target block. returns (eqs_struct, eqs_target, nvars)"""
    modulus, _ = modulus_for(n)
    F = GF2n(n, modulus)
    alpha = [1 << j for j in range(n)]
    zc = {0: z} if z else {}
    if shape == 'chain3':
        nv = n + 3 * k
        U = linear_form(alpha, 0)
        X = [linear_form(basis, n + i * k) for i in range(3)]
        S = [s3(F, U, X[0], X[1], B)]
        T = [s3(F, U, X[2], zc, B)]
    elif shape == 'bal4':
        nv = 2 * n + 4 * k
        U = [linear_form(alpha, i * n) for i in range(2)]
        X = [linear_form(basis, 2 * n + i * k) for i in range(4)]
        S = [s3(F, X[0], X[1], U[0], B), s3(F, X[2], X[3], U[1], B)]
        T = [s3(F, U[0], U[1], zc, B)]
    es = [e for p in S for e in descend(p, n)]
    et = [e for p in T for e in descend(p, n)]
    return es, et, nv


if __name__ == '__main__':
    n, shape, k = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    basis = [1 << j for j in range(k)]
    B = 0b101
    es, et, nv = build(n, shape, k, B, basis, 0)
    print('vars', nv, 'S gens', len(es), 'deg', sorted({max((m.bit_count() for m in e), default=-1) for e in es}),
          'T gens', len(et), 'deg', sorted({max((m.bit_count() for m in e), default=-1) for e in et}))
    # affinity check
    z1, z2 = 5, 17
    _, t0, _ = build(n, shape, k, B, basis, 0)
    _, a, _ = build(n, shape, k, B, basis, z1)
    _, b, _ = build(n, shape, k, B, basis, z2)
    _, ab, _ = build(n, shape, k, B, basis, z1 ^ z2)
    ok = all((set(a[g]) ^ set(b[g]) ^ set(t0[g])) == set(ab[g]) for g in range(len(a)))
    print('affine in z (3 point check):', ok)
