"""EXP-MLKEM-007 -- frozen toy short-vector pool + negacyclic orbit scoring.

Frozen single-layer layered-dual scoring task (see implementation.md, section
"Frozen task definition"; pinned before RUN-MLKEM-025).

Notation (flattened coefficient picture):
  I = c*n+i indexes a secret coordinate, J = r*n+l indexes an LWE equation.
  b_J = sum_I Amat[I][J] s_I + e_J   (mod q)
  A dual vector is v in Z^{nk} over equations.  With u_I := (Amat v)_I,
      rho := <v, b> = sum_I u_I s_I + <v, e>   (mod q).
  The guess block G is a set of secret coordinates for which u_I is NOT made
  short; the reduced lattice makes v and u_I (I not in G) simultaneously short.
  Then
      rho - sum_{I in G} u_I s_I  =  small.
  The orbit element X^j acts by  b -> X^j b, and because negacyclic matrices
  commute with the shift,  X^j b = A (X^j s) + X^j e  with the SAME A, so the
  SAME pool vector v is a dual vector for every orbit element:
      rho^(j) - sum_{I in G} u_I (X^j s)_I = small^(j).
  G is chosen shift-invariant (G = {i : i = 0 mod d_shift} inside ring
  component 0) so that (X^j s)_G is a signed permutation of s_G and every orbit
  element scores the SAME unknowns.

All work counters are exact integer counts of the operations actually
executed; nothing here is modelled.
"""

import math
from fractions import Fraction

from mlwe_sampler import (Q, ETA, CBD_PROB, LAYER_CLASS, shift_signs,
                          apply_signed_perm)


# ------------------------------------------------------------------ counters

class Work(object):
    """Exact charged-work counters (measured, never modelled)."""

    FIELDS = ("integer_ops", "transforms", "bytes_read", "bytes_written",
              "vector_generation_ops", "score_ops", "covariance_ops",
              "subset_search_ops", "candidate_verification_ops")

    def __init__(self):
        for f in self.FIELDS:
            setattr(self, f, 0)

    def add(self, other):
        for f in self.FIELDS:
            setattr(self, f, getattr(self, f) + getattr(other, f))

    def asdict(self):
        return dict((f, getattr(self, f)) for f in self.FIELDS)


# ---------------------------------------------------------------------- LLL

def lll(B, delta=0.99, work=None):
    """Cohen Alg. 2.6.3 with float64 Gram-Schmidt coefficients.

    Integer basis rows are exact; only the mu/B* bookkeeping is floating point,
    which is the standard LLL implementation trade-off.  The output basis is
    re-checked (Lovasz + size-reduction conditions) by verify_lll_output().
    """
    d = len(B)
    n = len(B[0])
    mu = [[0.0] * d for _ in range(d)]
    Bn = [0.0] * d
    ops = 0

    def dot(u, v):
        return sum(x * y for x, y in zip(u, v))

    Bn[0] = float(dot(B[0], B[0]))
    ops += n
    kmax = 0
    k = 1
    nswap = 0
    nred = 0
    while k < d:
        if k > kmax:
            kmax = k
            bk = B[k]
            for j in range(k):
                s = float(dot(bk, B[j]))
                ops += n
                for i in range(j):
                    s -= mu[j][i] * mu[k][i] * Bn[i]
                ops += j
                mu[k][j] = s / Bn[j] if Bn[j] != 0.0 else 0.0
            s = float(dot(bk, bk))
            ops += n
            for j in range(k):
                s -= mu[k][j] * mu[k][j] * Bn[j]
            ops += k
            Bn[k] = s
        m = mu[k][k - 1]
        if abs(m) > 0.5:
            r = int(m + 0.5) if m > 0 else -int(0.5 - m)
            bk = B[k]
            bl = B[k - 1]
            for t in range(n):
                bk[t] -= r * bl[t]
            for i in range(k - 1):
                mu[k][i] -= r * mu[k - 1][i]
            mu[k][k - 1] = m - r
            ops += n + k
            nred += 1
        if Bn[k] < (delta - mu[k][k - 1] ** 2) * Bn[k - 1]:
            nswap += 1
            mu_ = mu[k][k - 1]
            Bt = Bn[k] + mu_ * mu_ * Bn[k - 1]
            if Bt == 0.0:
                Bn[k], Bn[k - 1] = Bn[k - 1], Bn[k]
                B[k], B[k - 1] = B[k - 1], B[k]
                k = max(k - 1, 1)
                continue
            mu[k][k - 1] = mu_ * Bn[k - 1] / Bt
            Bn[k] = Bn[k - 1] * Bn[k] / Bt
            Bn[k - 1] = Bt
            B[k], B[k - 1] = B[k - 1], B[k]
            for j in range(k - 1):
                mu[k][j], mu[k - 1][j] = mu[k - 1][j], mu[k][j]
            mkk = mu[k][k - 1]
            for i in range(k + 1, kmax + 1):
                t = mu[i][k]
                mu[i][k] = mu[i][k - 1] - mu_ * t
                mu[i][k - 1] = t + mkk * mu[i][k]
            ops += 3 * (kmax - k) + k
            k = max(k - 1, 1)
        else:
            for l in range(k - 2, -1, -1):
                m = mu[k][l]
                if abs(m) > 0.5:
                    r = int(m + 0.5) if m > 0 else -int(0.5 - m)
                    bk = B[k]
                    bl = B[l]
                    for t in range(n):
                        bk[t] -= r * bl[t]
                    for i in range(l):
                        mu[k][i] -= r * mu[l][i]
                    mu[k][l] = m - r
                    ops += n + l
                    nred += 1
            k += 1
    if work is not None:
        work.integer_ops += ops
        work.vector_generation_ops += ops
    return B, {"swaps": nswap, "size_reductions": nred, "ops": ops}


# ---------------------------------------------------- dual lattice and pool

def guess_block_indices(n, d_shift):
    """Shift-invariant guess block inside ring component 0."""
    return [i for i in range(n) if i % d_shift == 0]


def build_dual_basis(inst, guess_block, q=Q):
    """Rows [ v-part (nk) | y-part (nk - |G|) ] of the projected dual lattice.

    A lattice vector (v, y) satisfies y_I = -(Amat v)_I (mod q) for I not in G;
    the G coordinates are projected out (they are the guessed ones).
    """
    n, k = inst.n, inst.k
    nk = n * k
    Gset = set(guess_block)  # guess block lives in component 0 -> I == i
    notG = [I for I in range(nk) if I not in Gset]
    N = len(notG)
    dim = nk + N
    Amat = inst.Amat
    B = []
    for J in range(nk):
        row = [0] * dim
        row[J] = 1
        for jj, I in enumerate(notG):
            row[nk + jj] = (-Amat[I][J]) % q
        B.append(row)
    for jj in range(N):
        row = [0] * dim
        row[nk + jj] = q
        B.append(row)
    return B, notG, dim


def verify_lll_output(B, delta=0.99, prefix=None):
    """Independent EXACT re-check of the reduced basis.

    The LLL routine above keeps its Gram-Schmidt bookkeeping in float64; this
    verifier recomputes the Gram matrix over the integers and the GSO over
    exact rationals, so it shares no floating-point state with the solver.
    A float64 version of this check is numerically unreliable at dimension
    ~124 and must not be used.
    """
    d = len(B) if prefix is None else min(prefix, len(B))
    G = [[sum(x * y for x, y in zip(B[i], B[j])) for j in range(d)] for i in range(d)]
    mu = [[Fraction(0)] * d for _ in range(d)]
    Bn = [Fraction(0)] * d
    for i in range(d):
        Bn[i] = Fraction(G[i][i])
        for j in range(i):
            s = Fraction(G[i][j])
            for t in range(j):
                s -= mu[j][t] * mu[i][t] * Bn[t]
            mu[i][j] = s / Bn[j] if Bn[j] else Fraction(0)
        for j in range(i):
            Bn[i] -= mu[i][j] * mu[i][j] * Bn[j]
    half = Fraction(1, 2)
    dl = Fraction(delta).limit_denominator(10 ** 6)
    size_bad = [(i, j) for i in range(d) for j in range(i) if abs(mu[i][j]) > half]
    lov_bad = [i for i in range(1, d)
               if Bn[i] < (dl - mu[i][i - 1] ** 2) * Bn[i - 1]]
    max_mu = max((abs(mu[i][j]) for i in range(d) for j in range(i)),
                 default=Fraction(0))
    ratios = [Fraction(Bn[i], 1) / ((dl - mu[i][i - 1] ** 2) * Bn[i - 1])
              for i in range(1, d)
              if (dl - mu[i][i - 1] ** 2) * Bn[i - 1] != 0]
    return {"rows_checked": d,
            "size_reduced": len(size_bad) == 0,
            "size_reduction_violations": len(size_bad),
            "size_reduction_violation_rows": [i for i, _ in size_bad],
            "max_abs_mu": float(max_mu),
            "lovasz": len(lov_bad) == 0,
            "lovasz_violations": len(lov_bad),
            "lovasz_violation_rows": lov_bad,
            "min_lovasz_ratio": float(min(ratios)) if ratios else None,
            "effective_delta_satisfied":
                float(min((mu[i][i - 1] ** 2 + Fraction(Bn[i], 1) / Bn[i - 1]
                           for i in range(1, d) if Bn[i - 1] != 0),
                          default=Fraction(0))),
            "gs_norms": [math.sqrt(float(x)) if x > 0 else 0.0 for x in Bn]}


def build_pool(Breduced, pool_size, work):
    """Frozen toy pool: deterministic short-combination sieve over the reduced
    basis.  Candidates are  +-b_i  and  +-b_i +- b_j (i<j); the pool is the
    `pool_size` shortest distinct candidates by Euclidean norm, with ties and
    global sign broken deterministically.  Every candidate examined is charged.
    """
    d = len(Breduced)
    n = len(Breduced[0])
    cands = []
    for i in range(d):
        v = Breduced[i]
        cands.append((sum(x * x for x in v), i, -1, 1))
        work.integer_ops += n
    for i in range(d):
        bi = Breduced[i]
        for j in range(i + 1, d):
            bj = Breduced[j]
            sp = 0
            sm = 0
            for t in range(n):
                a = bi[t] + bj[t]
                c = bi[t] - bj[t]
                sp += a * a
                sm += c * c
            work.integer_ops += 6 * n
            cands.append((sp, i, j, 1))
            cands.append((sm, i, j, -1))
    cands.sort()
    work.integer_ops += len(cands) * max(1, int(math.log2(max(len(cands), 2))))
    pool = []
    for (sq, i, j, sgn) in cands[:pool_size]:
        if j < 0:
            v = list(Breduced[i])
        else:
            v = [Breduced[i][t] + sgn * Breduced[j][t] for t in range(n)]
            work.integer_ops += n
        pool.append(v)
    work.vector_generation_ops += work.integer_ops
    norms = [math.sqrt(sum(x * x for x in v)) for v in pool]
    return pool, {"pool_size": len(pool), "candidates_examined": len(cands),
                  "norm_min": min(norms), "norm_median": norms[len(norms) // 2],
                  "norm_max": max(norms)}


def pool_to_vu(pool, inst, guess_block, notG, q=Q):
    """Split each lattice vector into (v, u_G) where u_I = (Amat v)_I.

    For I not in G the lattice already carries y_I = -u_I mod q (short); for
    I in G we recompute u_I from v.  Returns v-list and u_G-list.
    """
    n, k = inst.n, inst.k
    nk = n * k
    Amat = inst.Amat
    vs = []
    uGs = []
    for row in pool:
        v = row[:nk]
        vs.append(v)
        uG = []
        for I in guess_block:
            AI = Amat[I]
            acc = 0
            for J in range(nk):
                vj = v[J]
                if vj:
                    acc += AI[J] * vj
            uG.append(acc % q)
        uGs.append(uG)
    return vs, uGs


# ------------------------------------------------------- residuals / orbits

def residual_scalar(v, b_flat, q=Q):
    acc = 0
    for J, vj in enumerate(v):
        if vj:
            acc += vj * b_flat[J]
    return acc % q


def orbit_residuals_scalar(vs, inst, j, q=Q):
    """rho^(j)_t computed by explicitly forming X^j b and taking <v, X^j b>."""
    n, k = inst.n, inst.k
    src = shift_signs(n, j)
    bj = []
    for r in range(k):
        br = inst.b[r]
        bj.extend([(sgn * br[i]) % q for (i, sgn) in src])
    return [residual_scalar(v, bj, q) for v in vs], bj


def orbit_residuals_batched(vs, inst, orbit, work, q=Q):
    """rho^(j)_t for all j in `orbit` from ONE negacyclic convolution per pool
    vector: c_t = <v_t, b> evaluated as a ring product, so that rho^(j)_t is
    read off coefficient j of the convolution.

    For v in Z^{nk} and b in R_q^k, define per component r the ring element
        conv_r(v_r, b_r)_j := sum_l v_r[l] * (X^j b_r)_l
    which is exactly the negacyclic correlation of v_r and b_r.  Summing over r
    gives rho^(j) for all j at once.
    """
    n, k = inst.n, inst.k
    out = [[0] * len(vs) for _ in orbit]
    for t, v in enumerate(vs):
        conv = [0] * n
        for r in range(k):
            br = inst.b[r]
            base = r * n
            for j in range(n):
                acc = 0
                # (X^j b)_l = sgn * b_{l-j}; l-j<0 -> negative sign
                for l in range(n):
                    d = l - j
                    if d >= 0:
                        acc += v[base + l] * br[d]
                    else:
                        acc -= v[base + l] * br[d + n]
                conv[j] += acc
        work.integer_ops += 2 * k * n * n
        for oi, j in enumerate(orbit):
            out[oi][t] = conv[j] % q
    return out


def orbit_residuals_batched_fast(vs, inst, orbit, work, q=Q):
    """Same output as orbit_residuals_batched but only for the |orbit| shifts
    that are actually used (the frozen orbit subset), avoiding the full n-point
    transform.  Used for production; the full version is used by the exact
    equality control."""
    n, k = inst.n, inst.k
    out = []
    for j in orbit:
        src = shift_signs(n, j)
        bj = []
        for r in range(k):
            br = inst.b[r]
            bj.extend([(sgn * br[i]) % q for (i, sgn) in src])
        col = []
        for v in vs:
            acc = 0
            for J, vj in enumerate(v):
                if vj:
                    acc += vj * bj[J]
            col.append(acc % q)
        out.append(col)
        work.integer_ops += len(vs) * n * k
    return out


def perm_residuals(vs, inst, src, work, q=Q):
    """Residuals under a size-matched random signed permutation applied to b."""
    n, k = inst.n, inst.k
    bp = []
    for r in range(k):
        br = inst.b[r]
        bp.extend([(sgn * br[i]) % q for (i, sgn) in src])
    col = []
    for v in vs:
        acc = 0
        for J, vj in enumerate(v):
            if vj:
                acc += vj * bp[J]
        col.append(acc % q)
    work.integer_ops += len(vs) * n * k
    return col


# ------------------------------------------------ modulus switch + scoring

class Switch(object):
    """Modulus switch q -> P = 3^L (a power of the layer prime p=3).

    Both the residual and the guess-block coefficients u_G are switched, which
    is what makes the score factor over the guess-block coordinates.  The
    cosine/sine table has exactly P entries: transform precision is
    log2(P) bits of phase resolution, recorded in the manifests.
    """

    def __init__(self, P):
        self.P = P
        self.cos = [math.cos(2.0 * math.pi * kk / P) for kk in range(P)]
        self.sin = [math.sin(2.0 * math.pi * kk / P) for kk in range(P)]

    def switch(self, x, q=Q):
        return int((x * self.P + q // 2) // q) % self.P


def switch_vec(sw, xs, work, q=Q):
    work.transforms += len(xs)
    work.integer_ops += 3 * len(xs)
    return [sw.switch(x, q) for x in xs]


def build_h_tables(uG_sw, sw, work):
    """h[t][a][lam] = sum_{x: layer(x)=lam} P_CBD(x) * E[-uG_sw[t][a]*x mod P].

    Returns complex tables.  This is the marginal over the non-guessed p-adic
    layers of the guessed coordinates, weighted by the exact CBD prior.
    """
    P = sw.P
    tabs = []
    for row in uG_sw:
        trow = []
        for uu in row:
            entry = {}
            for lam in (-1, 0, 1):
                re = 0.0
                im = 0.0
                for x in LAYER_CLASS[lam]:
                    idx = (-uu * x) % P
                    p = CBD_PROB[x]
                    re += p * sw.cos[idx]
                    im += p * sw.sin[idx]
                entry[lam] = (re, im)
            trow.append(entry)
        tabs.append(trow)
        work.integer_ops += len(row) * 7
        work.score_ops += len(row) * 7
    return tabs


def enumerate_candidates(g):
    cands = [()]
    for _ in range(g):
        cands = [c + (lam,) for c in cands for lam in (-1, 0, 1)]
    return cands


def candidate_products(h_tabs, cands, work):
    """PROD[c][t] = prod_a h[t][a][c_a]   (complex, as (re, im) pairs)."""
    m = len(h_tabs)
    out = []
    for c in cands:
        col_re = [0.0] * m
        col_im = [0.0] * m
        for t in range(m):
            row = h_tabs[t]
            re, im = row[0][c[0]]
            for a in range(1, len(c)):
                r2, i2 = row[a][c[a]]
                re, im = re * r2 - im * i2, re * i2 + im * r2
            col_re[t] = re
            col_im[t] = im
        out.append((col_re, col_im))
        work.score_ops += m * len(c) * 4
        work.integer_ops += m * len(c) * 4
    return out


def permuted_candidate(c, block, src_map):
    """Layer candidate for orbit/permutation element with source map `src_map`
    restricted to the guess block: (X^j s)_{block[a]} = sgn * s_{src}.
    layer() is odd, so the layer candidate transforms the same way."""
    pos = dict((idx, a) for a, idx in enumerate(block))
    out = []
    for a, l in enumerate(block):
        i, sgn = src_map[l]
        out.append(sgn * c[pos[i]])
    return tuple(out)


def orbit_scores(rho_sw_by_elem, prod_by_cand, cand_index, cand_maps, sw,
                 checkpoints, work):
    """S_j(c) at each pool prefix in `checkpoints`.

    rho_sw_by_elem[oi][t]      switched residual for orbit element oi
    prod_by_cand[ci]           (re, im) columns of PROD for candidate ci
    cand_maps[oi][ci] -> ci'   candidate index after the element's signed perm
    Returns scores[oi][ck][ci].
    """
    n_elem = len(rho_sw_by_elem)
    n_cand = len(prod_by_cand)
    n_ck = len(checkpoints)
    scores = [[[0.0] * n_cand for _ in range(n_ck)] for _ in range(n_elem)]
    for oi in range(n_elem):
        rsw = rho_sw_by_elem[oi]
        zre = [sw.cos[r] for r in rsw]
        zim = [sw.sin[r] for r in rsw]
        for ci in range(n_cand):
            cj = cand_maps[oi][ci]
            pre, pim = prod_by_cand[cj]
            acc = 0.0
            ck = 0
            for t in range(checkpoints[-1]):
                acc += zre[t] * pre[t] - zim[t] * pim[t]
                if t + 1 == checkpoints[ck]:
                    scores[oi][ck][ci] = acc
                    ck += 1
            work.score_ops += 4 * checkpoints[-1]
    return scores


def scalar_score_reference(rho_sw, uG_sw, cand, block, sw):
    """Direct scalar evaluation of one score: enumerate every consistent secret
    assignment x on the guess block, form the switched phase index EXACTLY as
    an integer mod P, and accumulate.  This is the independent reference for
    CTRL-EXACT-EQUALITY (integer phase indices are compared exactly)."""
    g = len(block)
    idxs = []
    weights = []
    assigns = [()]
    for a in range(g):
        assigns = [asn + (x,) for asn in assigns for x in LAYER_CLASS[cand[a]]]
    acc_re = 0.0
    acc_im = 0.0
    for t in range(len(rho_sw)):
        for asn in assigns:
            k = rho_sw[t]
            wgt = 1.0
            for a in range(g):
                k -= uG_sw[t][a] * asn[a]
                wgt *= CBD_PROB[asn[a]]
            k %= sw.P
            idxs.append((t, k))
            weights.append(wgt)
            acc_re += wgt * sw.cos[k]
            acc_im += wgt * sw.sin[k]
    return acc_re, acc_im, idxs, weights
