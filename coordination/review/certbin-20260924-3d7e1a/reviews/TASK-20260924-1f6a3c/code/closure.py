"""The mutant closure W_D by the LITERAL rule of EXP-CERTBIN-e94b27
object.mutant_closure_W_D (card BR-4), and W-certificate extraction (card BR-5).

Literal rule:
  W^(0) = rowspace(M_D);
  W^(i+1) = W^(i) + span{ v_j * b : b in a basis of W^(i) cap B_{<=D-1}, j = 0..17 },
  multilinear reduction; stop at the first i with dim W^(i+1) = dim W^(i).
At EVERY iteration a FULL basis of W^(i) cap B_{<=D-1} (snapshotted at the start of
the iteration) is multiplied by every v_j.
"""
import numpy as np

import boolsys as BS
from gf2lin import Space, TrackedSpace

NV = BS.NV


def int_to_bits(v, nbits):
    nbytes = (nbits + 7) // 8
    return np.unpackbits(np.frombuffer(v.to_bytes(nbytes, "little"), dtype=np.uint8),
                         bitorder="little")[:nbits]


def ints_to_matrix(vs, nbits):
    nbytes = (nbits + 7) // 8
    if not vs:
        return np.zeros((0, nbits), dtype=np.uint8)
    buf = b"".join(v.to_bytes(nbytes, "little") for v in vs)
    a = np.frombuffer(buf, dtype=np.uint8).reshape(len(vs), nbytes)
    return np.unpackbits(a, axis=1, bitorder="little")[:, :nbits]


def matrix_to_ints(M):
    P = np.packbits(M, axis=1, bitorder="little")
    return [int.from_bytes(P[i].tobytes(), "little") for i in range(P.shape[0])]


class Multiplier:
    """v_j * g for g in B_{<=D-1}, as a gather: for a target monomial t containing v_j,
    coeff_t(v_j g) = g[t] (if deg t <= D-1) + g[t minus v_j]; other targets are 0."""

    def __init__(self, MI, D):
        self.MI = MI
        self.D = D
        self.Nd = MI.N[D - 1]     # domain bits (deg <= D-1)
        self.Nt = MI.N[D]         # target bits (deg <= D)
        self.nv = MI.nv
        self.tgt, self.srcA, self.srcB = [], [], []
        for j in range(self.nv):
            T, A, Bs = [], [], []
            for b in range(self.Nt):
                m = MI.mono[b]
                if not (m >> j) & 1:
                    continue
                T.append(b)
                A.append(MI.bit[m] if BS.popcount(m) <= D - 1 else self.Nd)  # Nd = zero pad
                Bs.append(MI.bit[m & ~(1 << j)])
            self.tgt.append(np.array(T, dtype=np.int64))
            self.srcA.append(np.array(A, dtype=np.int64))
            self.srcB.append(np.array(Bs, dtype=np.int64))

    def products(self, vecs):
        """Return [[v_0*g, ..., v_{nv-1}*g] for g in vecs] as ints (each g must be in B_{<=D-1})."""
        for g in vecs:
            assert g >> self.Nd == 0, "multiplicand not in B_{<=D-1}"
        X = ints_to_matrix(vecs, self.Nd)
        Xp = np.concatenate([X, np.zeros((X.shape[0], 1), dtype=np.uint8)], axis=1)
        out = [[None] * self.nv for _ in vecs]
        for j in range(self.nv):
            Y = np.zeros((X.shape[0], self.Nt), dtype=np.uint8)
            Y[:, self.tgt[j]] = Xp[:, self.srcA[j]] ^ Xp[:, self.srcB[j]]
            ys = matrix_to_ints(Y)
            for i, y in enumerate(ys):
                out[i][j] = y
        return out

    def product_single_naive(self, g, j):
        """Reference (slow) implementation for self-tests: monomial by monomial."""
        MI = self.MI
        r = 0
        for m in MI.masks_from_vec(g):
            r ^= 1 << MI.bit[m | (1 << j)]
        return r


def literal_closure(Mrows, MI, D, mult, max_iter=64):
    """Returns a dict with the per-iteration dimensions and the final space."""
    Nlow = MI.N[D - 1]
    W = Space()
    for r in Mrows:
        W.insert(r)
    dims = [W.dim]
    low_sizes = []
    first_one = 0 if W.has_one() else None
    it = 0
    while True:
        low = W.low_basis(Nlow)            # FULL basis of W^(it) cap B_{<=D-1}
        low_sizes.append(len(low))
        prods = mult.products(low)
        for row in prods:
            for p in row:
                W.insert(p)
        it += 1
        dims.append(W.dim)
        if first_one is None and W.has_one():
            first_one = it
        if dims[-1] == dims[-2]:
            fix = it - 1
            break
        if it >= max_iter:
            raise RuntimeError("closure did not stabilise within max_iter")
    return {
        "dims": dims,                       # dim W^(0), ..., dim W^(fix+1) (= dim W^(fix))
        "fixpoint_index": fix,              # first i with dim W^(i+1) = dim W^(i)
        "multiplied_basis_sizes": low_sizes,  # |basis of W^(i) cap B_{<=D-1}| multiplied at iteration i
        "first_one_iteration": first_one,
        "final_dim": W.dim,
        "dim_cap": [W.dim_below(MI.N[d]) for d in range(D + 1)],
        "one_in_W": W.has_one(),
        "space": W,
    }


def extract_certificate(Mrows, macaulay, MI, D, mult):
    """Build a W-certificate for 1 in W_D (card BR-5 semantics).

    Generators: every M_D row (id = row index) and products v_j * g_e for
    certificate elements e. Level s: S_s = span(rows, products of elements of
    levels < s). Q_s = rowspace(rows with deg mu <= D-3) + span(elements of
    levels < s); every product of an element of Q_s already lies in S_s (for a
    row mu*f_k with deg mu <= D-3, v_j*mu*f_k is an M_D row). The new elements of
    level s are the echelon basis vectors of S_s cap B_{<=D-1} that are
    independent modulo Q_s; their products give S_{s+1}. By induction
    S_s = W^(s), so the per-level dimensions must equal the literal ones (a
    cross-check recorded by the caller). Each element is a basis vector of
    S_s with its tracked expression in generators.
    Returns None if the closure stabilises without 1."""
    Nlow = MI.N[D - 1]
    nrows = len(Mrows)
    S = TrackedSpace()
    gens = []  # generator id -> ("row", r) or ("prod", j, elem)
    for r, v in enumerate(Mrows):
        S.insert(v, 1 << r)
        gens.append(("row", r))
    Q = Space()
    nq = len(BS.row_mu_order(D - 3, MI.nv)) * macaulay.neq if D >= 3 else 0
    for r in range(nq):
        Q.insert(Mrows[r])
    elems = []   # (vec, track, level)
    level_dims = [S.dim]
    level = 0
    while not S.has_one():
        low = S.low_basis(Nlow)
        newE = []
        for v, tr in low:
            if Q.insert(v):
                newE.append(len(elems))
                elems.append((v, tr, level))
        if not newE:
            return {"certificate": None, "level_dims": level_dims}
        prods = mult.products([elems[e][0] for e in newE])
        for idx, e in enumerate(newE):
            for j in range(MI.nv):
                gid = len(gens)
                gens.append(("prod", j, e))
                S.insert(prods[idx][j], 1 << gid)
        level += 1
        level_dims.append(S.dim)
    one_vec, one_tr = S.basis[0]
    assert one_vec == 1

    def decode(tr):
        rows, prods_ = [], []
        g = 0
        while tr:
            low_bit = tr & -tr
            g = low_bit.bit_length() - 1
            tr ^= low_bit
            desc = gens[g]
            if desc[0] == "row":
                mu, k = macaulay.row_key(desc[1])
                rows.append((mu, k))
            else:
                prods_.append((desc[1], desc[2]))
        return rows, prods_

    # prune to the elements reachable from the output
    out_rows, out_prods = decode(one_tr)
    need = set()
    stack = [p for _, p in out_prods]
    decoded = {}
    while stack:
        e = stack.pop()
        if e in need:
            continue
        need.add(e)
        decoded[e] = decode(elems[e][1])
        for _, p in decoded[e][1]:
            if p not in need:
                stack.append(p)
    order = sorted(need)
    newid = {e: i for i, e in enumerate(order)}
    elements = []
    for e in order:
        rows, prods_ = decoded[e]
        elements.append({
            "id": newid[e],
            "rows": [[mu, k] for mu, k in rows],
            "products": [[j, newid[p]] for j, p in prods_],
        })
    out_id = len(order)
    elements.append({
        "id": out_id,
        "rows": [[mu, k] for mu, k in out_rows],
        "products": [[j, newid[p]] for j, p in out_prods],
    })
    return {
        "certificate": {"D": D, "elements": elements, "output_id": out_id},
        "level_dims": level_dims,
        "levels_used": level,
        "elements_before_prune": len(elems),
        "elements_after_prune": len(order) + 1,
    }


def complement_closure(Mrows, macaulay, MI, D, mult, max_iter=64):
    """Cross-check of the literal iterates by a DIFFERENT generating set: at each
    step multiply only the basis vectors of W^(s) cap B_{<=D-1} that are independent
    modulo Q_s = rowspace(rows with deg mu <= D-3) + span(previously multiplied
    vectors) (see extract_certificate for why this yields the same W^(s+1)).
    Runs to the fixpoint without tracking; returns the dimension list."""
    Nlow = MI.N[D - 1]
    S = Space()
    for r in Mrows:
        S.insert(r)
    Q = Space()
    nq = len(BS.row_mu_order(D - 3, MI.nv)) * macaulay.neq if D >= 3 else 0
    for r in range(nq):
        Q.insert(Mrows[r])
    dims = [S.dim]
    first_one = 0 if S.has_one() else None
    multiplied = []
    it = 0
    while True:
        newv = [v for v in S.low_basis(Nlow) if Q.insert(v)]
        multiplied.append(len(newv))
        if newv:
            for row in mult.products(newv):
                for p in row:
                    S.insert(p)
        it += 1
        dims.append(S.dim)
        if first_one is None and S.has_one():
            first_one = it
        if dims[-1] == dims[-2]:
            break
        if it >= max_iter:
            raise RuntimeError("no fixpoint")
    return {"dims": dims, "first_one_iteration": first_one, "multiplied_counts": multiplied,
            "dim_cap": [S.dim_below(MI.N[d]) for d in range(D + 1)]}
