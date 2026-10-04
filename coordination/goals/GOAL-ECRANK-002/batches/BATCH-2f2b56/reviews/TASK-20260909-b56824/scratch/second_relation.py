#!/usr/bin/env python3
"""Find the second Q-relation among the 8 forced points of the n=8 d=(1..1)
control objects (J3 A.2, rigor step).

The 8 points P_1..P_8 satisfy sum P_i = O (Mestre). The closed-form prediction
is certified total 7. The committed certifier records 6 for the shortfall
tuples (b_index 0,1,7) and 7 for the control (b_index 2), and the shortfall
survives enlarging the good-prime set to 400 primes (certify_windows.py).

To decide whether the shortfall is a GENUINE second Q-relation (Q-rank 6) or
an instrument boundary (Q-rank 7 the certifier fails to extract), find the
second Q-relation directly:
  * For a good prime p, the F_p-relation lattice
        L_p = { (n_1..n_8) in Z^8 : sum n_i (P_i mod p) = O in E(F_p) }
    contains the Q-relation lattice L_Q (a Q-relation reduces mod p).
  * Express each P_i mod p in coordinates (a_i, b_i) of G = <P_i mod p>
    (a finite abelian group, Z/d1 x Z/d2 or Z/N). Then
        L_p = { n : sum n_i a_i == 0 (mod d1), sum n_i b_i == 0 (mod d2) }.
  * A basis of L_p is found via the Smith normal form of the 2x8 matrix
    A = [a_i; b_i] together with the moduli. Every Q-relation is a Z-linear
    combination of the basis; we test basis vectors (and small combinations)
    over Q by exact point arithmetic.
  * A basis vector v (independent of (1,..,1)) that IS a Q-relation proves
    Q-rank <= 6; combined with the certifier's lower bound 6, Q-rank = 6.
"""
import os, sys, json
from fractions import Fraction as Fr
from math import gcd

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
SRC = os.path.join(ROOT, "experiments", "EXP-ECRANK-73275e", "source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", ROOT)
import ecrank_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "b_tuples.json")) as f:
    BT = json.load(f)
N8 = [[Fr(x) for x in row] for row in BT["n8"]]

# ---------------- F_p group law (a1=a3=0) ----------------
def fp_add(ai, p, P, Q):
    if P is None: return Q
    if Q is None: return P
    a2, a4, a6 = ai[1] % p, ai[3] % p, ai[4] % p
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - a2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def fp_neg(p, P):
    if P is None: return None
    return (P[0], (-P[1]) % p)

def fp_mul(ai, p, n, P):
    if n < 0:
        n = -n; P = fp_neg(p, P)
    R = None; Q = P
    while n:
        if n & 1: R = fp_add(ai, p, R, Q)
        Q = fp_add(ai, p, Q, Q)
        n >>= 1
    return R

def _sqrt_table(p):
    tbl = {}
    for y in range(p):
        r = (y * y) % p
        if r not in tbl: tbl[r] = y
    return tbl

def all_points_fp(ai, p):
    a2, a4, a6 = ai[1] % p, ai[3] % p, ai[4] % p
    tbl = _sqrt_table(p)
    pts = []
    for x in range(p):
        f = (x * x * x + a2 * x * x + a4 * x + a6) % p
        y = tbl.get(f)
        if y is not None:
            pts.append((x, y))
            if y != 0: pts.append((x, (-y) % p))
    return pts

def factorize(n):
    out = []; d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0: n //= d; e += 1
            out.append((d, e))
        d += 1 if d == 2 else 2
    if n > 1: out.append((n, 1))
    return out

def point_order_fp(ai, p, P, N, fac):
    if P is None: return 1
    order = N
    for q, e in fac:
        while order % q == 0:
            cand = order // q
            if fp_mul(ai, p, cand, P) is None: order = cand
            else: break
    return order

def subgroup_structure(ai, p, gens):
    """Return (N, is_cyclic, G_list, order_of) for G = <gens> in E(F_p).
    G_list: list of all elements of G (None = O). order_of: dict elem->order."""
    # generate G explicitly (small)
    G = {None}
    changed = True
    while changed:
        changed = False
        for g in list(G):
            for h in gens:
                t = fp_add(ai, p, g, h)
                if t not in G: G.add(t); changed = True
                t2 = fp_add(ai, p, g, fp_neg(p, h))
                if t2 not in G: G.add(t2); changed = True
    Glist = list(G)
    N = len(Glist)
    fac = factorize(N)
    order_of = {}
    for P in Glist:
        order_of[P] = point_order_fp(ai, p, P, N, fac)
    # find a generator (order N) -> cyclic
    gen = None
    for P in Glist:
        if order_of[P] == N:
            gen = P; break
    return N, (gen is not None), Glist, order_of, gen

def coords_cyclic(ai, p, gen, N, P):
    """discrete log of P in <gen> (cyclic). Returns m with P = m*gen, or None."""
    Q = None
    for m in range(N):
        if Q == P: return m
        Q = fp_add(ai, p, Q, gen)
    return None

def snf_kernel_basis(A, moduli):
    """A: list of rows (each a list of ints), moduli: list of moduli (one per
    row). Returns a list of integer vectors forming a Z-basis of
        { n in Z^k : for each row r, sum_j A[r][j] n_j == 0 (mod moduli[r]) }.
    Method: homogenize to a homogeneous integer system. For row r with modulus
    m_r, the congruence sum_j A[r][j] n_j == 0 (mod m_r) is equivalent to
    sum_j A[r][j] n_j - m_r * k_r = 0 for some integer k_r. So the solution
    set is the integer kernel of the (rows x (k + rows)) matrix
        M = [ A[0]  -m_0  0   ... 0 ;
              A[1]   0   -m_1 ... 0 ; ... ]
    and we project the kernel basis to the first k coordinates.
    The kernel of an r x (k+r) integer matrix M is a lattice of rank k in
    Z^(k+r); we compute a Z-basis via the Smith normal form of M.
    """
    r = len(A); k = len(A[0])
    # build M (r x (k+r))
    M = []
    for i in range(r):
        row = list(A[i]) + [0] * r
        row[k + i] = -moduli[i]
        M.append(row)
    # Smith normal form of M: find unimodular U (r x r), V ((k+r) x (k+r))
    # with U M V = D diagonal. Kernel of M = V * { x in Z^(k+r) : D x = 0 }.
    # D x = 0 => d_i x_i = 0 => x_i = 0 for d_i != 0, free for d_i == 0.
    U, D, V = _snf(M)
    ncols = k + r
    # D is r x ncols; diagonal entries D[i][i]
    diag = [D[i][i] for i in range(r)]
    free = [j for j in range(ncols) if (j >= r or diag[j] == 0)]
    # careful: D has r rows; D[i][j] for i in range(r), j in range(ncols).
    # D x = 0 means for each i: D[i][0]*x_0 + ... + D[i][ncols-1]*x_{ncols-1} = 0.
    # In SNF, D is diagonal: D[i][j] = 0 unless i == j, and D[i][i] = d_i.
    # So D x = 0 => d_i x_i = 0 for i in range(r) => x_i = 0 if d_i != 0.
    # x_j for j >= r are always free (no row constrains them).
    basis_m = []
    for i in range(r):
        if diag[i] == 0:
            e = [0] * ncols; e[i] = 1; basis_m.append(e)
    for j in range(r, ncols):
        e = [0] * ncols; e[j] = 1; basis_m.append(e)
    # transform by V: basis of kernel = { V * e : e in basis_m }
    basis = []
    for e in basis_m:
        v = [0] * k
        for j in range(ncols):
            if e[j]:
                for i in range(k):
                    v[i] += V[i][j]
        basis.append(v)
    return basis

def _snf(M):
    """Smith normal form of a small integer matrix M (list of rows). Returns
    (U, D, V) with U M V = D, U and V unimodular (integer, det +-1), D
    diagonal. Standard algorithm via elementary row/col ops."""
    import copy
    M = [row[:] for row in M]
    r = len(M); c = len(M[0])
    U = [[1 if i == j else 0 for j in range(r)] for i in range(r)]
    V = [[1 if i == j else 0 for j in range(c)] for i in range(c)]
    def row_op(i, j, f):  # R_i <- R_i + f R_j
        for cc in range(c): M[i][cc] += f * M[j][cc]
        for cc in range(r): U[i][cc] += f * U[j][cc]
    def col_op(i, j, f):  # C_i <- C_i + f C_j
        for rr in range(r): M[rr][i] += f * M[rr][j]
        for rr in range(c): V[rr][i] += f * V[rr][j]
    def row_swap(i, j):
        M[i], M[j] = M[j], M[i]; U[i], U[j] = U[j], U[i]
    def col_swap(i, j):
        for rr in range(r): M[rr][i], M[rr][j] = M[rr][j], M[rr][i]
        V[i], V[j] = V[j], V[i]
    def row_scale(i, s):
        for cc in range(c): M[i][cc] *= s
        for cc in range(r): U[i][cc] *= s
    def col_scale(i, s):
        for rr in range(r): M[rr][i] *= s
        for rr in range(c): V[rr][i] *= s
    def absmin_submatrix(i0, j0):
        best = None
        for i in range(i0, r):
            for j in range(j0, c):
                a = abs(M[i][j])
                if a and (best is None or a < best): best = a
        return best
    for i0 in range(min(r, c)):
        # find nonzero in submatrix [i0:, j0=i0:]
        while True:
            # find entry with smallest abs value in submatrix
            best = None; bi = bj = None
            for i in range(i0, r):
                for j in range(i0, c):
                    a = abs(M[i][j])
                    if a and (best is None or a < best):
                        best = a; bi, bj = i, j
            if best is None: break
            if bi != i0: row_swap(bi, i0)
            if bj != i0: col_swap(bj, i0)
            # now M[i0][i0] = +-best, nonzero
            if M[i0][i0] < 0:
                row_scale(i0, -1)
            # reduce other entries in row i0 and col i0 using M[i0][i0]
            progress = False
            for j in range(c):
                if j == i0: continue
                if M[i0][j] != 0:
                    q, rem = divmod(M[i0][j], M[i0][i0])
                    if rem != 0:
                        col_op(j, i0, -q)
                        progress = True
            for i in range(r):
                if i == i0: continue
                if M[i][i0] != 0:
                    q, rem = divmod(M[i][i0], M[i0][i0])
                    if rem != 0:
                        row_op(i, i0, -q)
                        progress = True
            if not progress:
                break
            # after reduction, some off-diagonal entry in row/col i0 may be
            # smaller than M[i0][i0]; loop to re-select
            # (the while loop re-finds the min)
            # but if M[i0][i0] now divides all, progress False next iter
        # ensure M[i0][i0] divides all entries in submatrix (SNF condition)
        # (the loop above already does this via the min-selection)
    # make D nonnegative and ordered
    for i in range(min(r, c)):
        if M[i][i] < 0:
            row_scale(i, -1)
    return U, M, V

def is_q_relation(ainv, Wpts, v):
    """Check sum v_i P_i == O over Q (exact). v: list of 8 ints."""
    a2, a4, a6 = Fr(ainv[1]), Fr(ainv[3]), Fr(ainv[4])
    def fr_add(P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if y1 + y2 == 0: return None
            lam = (3 * x1 * x1 + 2 * a2 * x1 + a4) / (2 * y1)
        else:
            lam = (y2 - y1) / (x2 - x1)
        x3 = lam * lam - a2 - x1 - x2
        y3 = lam * (x1 - x3) - y1
        return (x3, y3)
    S = None
    for i in range(8):
        if v[i]:
            P = (Fr(Wpts[i][0]), Fr(Wpts[i][1]))
            if v[i] != 1:
                P = fr_mul(a2, a4, a6, v[i], P)
            S = fr_add(S, P)
    return S is None

def fr_mul(a2, a4, a6, n, P):
    if n < 0:
        n = -n; P = (P[0], -P[1])
    R = None; Q = P
    while n:
        if n & 1: R = fr_add_local(a2, a4, a6, R, Q)
        Q = fr_add_local(a2, a4, a6, Q, Q)
        n >>= 1
    return R

def fr_add_local(a2, a4, a6, P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 + y2 == 0: return None
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - a2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)

def main():
    report = {}
    for bi in (0, 1, 7, 2):
        b = N8[bi]
        p_, g, s = E.mestre_polys(list(b))
        r = [E.peval(g, x) for x in b]
        ainv, Wpts = E.cubic_to_weierstrass(s, [(b[i], r[i]) for i in range(8)])
        ainv = [int(z) for z in ainv]
        # find a good prime (first usable)
        disc = E.disc_from_ainv(ainv)
        dens = set()
        for (x, y) in Wpts:
            dens.add(Fr(x).denominator); dens.add(Fr(y).denominator)
        bad = set()
        for d in dens:
            for q, e in factorize(d): bad.add(q)
        p = None
        cand = 3
        while p is None:
            if cand > 2 and disc % cand != 0 and cand not in bad and _is_prime(cand):
                p = cand
            cand += 1
        # reduce the 8 points
        def mf(fr, pp): return (fr.numerator * pow(fr.denominator, -1, pp)) % pp
        red = [(mf(Fr(x), p), mf(Fr(y), p)) for (x, y) in Wpts]
        N, cyclic, Glist, order_of, gen = subgroup_structure(ainv, p, red)
        rec = {"b": [str(x) for x in b], "p": p, "N_G": N, "cyclic": cyclic}
        if cyclic:
            ms = [coords_cyclic(ainv, p, gen, N, P) for P in red]
            rec["ms"] = ms
            # L_p = { n : sum n_i m_i == 0 (mod N) }
            basis = snf_kernel_basis([ms], [N])
        else:
            # non-cyclic: find two generators g1 (order d1), g2 (order d2)
            # with G = <g1, g2>. Use the structure: G ~ Z/d1 x Z/d2.
            # Find g1 of maximal order d1, then g2 such that <g1,g2> = G.
            d1 = max(order_of.values())
            g1 = [P for P in Glist if order_of[P] == d1][0]
            # find g2: an element not in <g1>
            g1cyc = set()
            Q = None
            for _ in range(d1):
                g1cyc.add(Q); Q = fp_add(ainv, p, Q, g1)
            g2 = None
            for P in Glist:
                if P not in g1cyc:
                    g2 = P; break
            d2 = order_of[g2]
            # coordinates: P = a*g1 + b*g2. Build a table.
            table = {}
            for a in range(d1):
                A = fp_mul(ainv, p, a, g1)
                for bb in range(d2):
                    B = fp_add(ainv, p, A, fp_mul(ainv, p, bb, g2))
                    table[B] = (a, bb)
            coords = [table[P] for P in red]
            rec["d1"] = d1; rec["d2"] = d2
            rec["coords"] = coords
            A = [[c[0] for c in coords], [c[1] for c in coords]]
            basis = snf_kernel_basis(A, [d1, d2])
        rec["basis_len"] = len(basis)
        # test each basis vector (and the Mestre vector) over Q
        mestre = [1] * 8
        rec["mestre_is_q_relation"] = is_q_relation(ainv, Wpts, mestre)
        q_rels = []
        for v in basis:
            if is_q_relation(ainv, Wpts, v):
                q_rels.append(v)
        rec["q_relation_basis_vectors"] = q_rels
        # also test small integer combinations of basis vectors
        extra = []
        if len(basis) >= 2:
            for i in range(len(basis)):
                for j in range(i + 1, len(basis)):
                    for c1 in (-1, 1):
                        for c2 in (-1, 1):
                            v = [c1 * basis[i][t] + c2 * basis[j][t] for t in range(8)]
                            if is_q_relation(ainv, Wpts, v):
                                extra.append(v)
        rec["q_relation_combinations"] = extra
        report[str(bi)] = rec
        print("=== b_index %d ===" % bi)
        print("  p=%d  N_G=%d  cyclic=%s" % (p, N, cyclic))
        print("  mestre is Q-relation:", rec["mestre_is_q_relation"])
        print("  basis len:", len(basis))
        print("  Q-relation basis vectors:", len(q_rels))
        for v in q_rels[:4]:
            print("    ", v)
        print("  Q-relation combinations:", len(extra))
        for v in extra[:4]:
            print("    ", v)
        print()
    with open(os.path.join(HERE, "second_relation.json"), "w") as f:
        json.dump(report, f, indent=1)
    print("wrote second_relation.json")

def _is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0: return False
        d += 2
    return True

if __name__ == "__main__":
    main()
