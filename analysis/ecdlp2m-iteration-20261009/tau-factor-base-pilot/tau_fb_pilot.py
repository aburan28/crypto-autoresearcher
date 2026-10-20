#!/usr/bin/env python3
"""Exploratory pilot (NOT program evidence): what does the Frobenius tau buy
in index-calculus relation collection on toy Koblitz curves, measured
exhaustively?

For each toy Koblitz curve E_a: y^2 + xy = x^3 + a x^2 + 1 over F_{2^n}
(n prime, #E = h*r, r prime, h in {2,4}), each m in {2,3}, each factor-base
exponent k, and each factor-base family V in {poly, nb, orb}:

  V_poly = {x : deg x < k}                       (polynomial basis; program default)
  V_nb   = span{beta^(2^i) : 0 <= i < k}          (window of a normal basis)
  V_orb  = union of random tau-orbits of x values (matched in point count to V_poly)

the factor base is FB = {P in <G> (the prime-order subgroup) : x(P) in V}, and
for T random targets R in <G> ALL decompositions R = P_1 + ... + P_m with
P_i in FB are enumerated (meet-in-the-middle over FB^(m-1), exact).

Per cell we record the decomposition probability, decompositions per target,
the number of tau-orbits meeting the factor base (the orbit-reduced factor-base
size), and for every decomposition the number of shifts j for which the
conjugate relation tau^j(R) = sum tau^j(P_i) lies entirely inside FB again.

Pure Python 3 + numpy, deterministic seeds. Writes JSONL rows.
"""
import argparse, json, math, os, sys, time
import numpy as np

# ---------------------------------------------------------------- polynomials
IRRED = {11: (1 << 11) | (1 << 2) | 1,
         13: (1 << 13) | (1 << 4) | (1 << 3) | (1 << 1) | 1,
         17: (1 << 17) | (1 << 3) | 1,
         19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
         23: (1 << 23) | (1 << 5) | 1}


def pmulmod(a, b, f, n):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a ^= f
    return r


def is_irreducible_prime_degree(f, n):
    # n prime: f irreducible iff no linear factor and x^(2^n) == x mod f
    if not (f & 1) or bin(f).count('1') % 2 == 0:
        return False
    x = 2
    for _ in range(n):
        x = pmulmod(x, x, f, n)
    return x == 2


class Field:
    """F_{2^n} with log/antilog tables; elements are ints < 2^n."""

    def __init__(self, n):
        self.n = n
        self.f = IRRED[n]
        assert is_irreducible_prime_degree(self.f, n), n
        self.N = (1 << n) - 1
        q = 1 << n
        # find a primitive element g (try z, z+1, ...)
        for g in range(2, 64):
            exp = np.zeros(self.N, dtype=np.int64)
            x = 1
            ok = True
            for i in range(self.N):
                exp[i] = x
                x = pmulmod(x, g, self.f, n)
                if x == 1 and i != self.N - 1:
                    ok = False
                    break
            if ok and x == 1:
                break
        else:
            raise RuntimeError("no primitive element found")
        self.g = g
        self.exp = exp
        log = np.zeros(q, dtype=np.int64)
        log[exp] = np.arange(self.N, dtype=np.int64)
        self.log = log
        idx = np.arange(q, dtype=np.int64)
        self.sq = self.mul(idx, idx)
        # trace table: Tr(x) = sum_{i<n} x^(2^i)
        t = idx.copy()
        acc = idx.copy()
        for _ in range(n - 1):
            t = self.sq[t]
            acc ^= t
        assert set(np.unique(acc).tolist()) <= {0, 1}
        self.tr = acc.astype(np.int8)

    def mul(self, a, b):
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        out = self.exp[(self.log[a] + self.log[b]) % self.N]
        return np.where((a == 0) | (b == 0), 0, out)

    def inv(self, a):
        a = np.asarray(a, dtype=np.int64)
        return self.exp[(self.N - self.log[a]) % self.N]  # caller ensures a != 0

    def frob(self, a, j=1):
        a = np.asarray(a, dtype=np.int64)
        for _ in range(j % self.n):
            a = self.sq[a]
        return a

    def half_trace(self, w):
        # n odd: HT(w) = sum_{i=0}^{(n-1)/2} w^(2^(2i)); HT^2 + HT = w + Tr(w)
        w = np.asarray(w, dtype=np.int64)
        acc = w.copy()
        t = w.copy()
        for _ in range((self.n - 1) // 2):
            t = self.sq[self.sq[t]]
            acc ^= t
        return acc


# ---------------------------------------------------------------- curve
class Koblitz:
    def __init__(self, F, a):
        self.F, self.a = F, a
        n = F.n
        # trace recursion from #E_a(F_2): a=0 -> 4 points, a=1 -> 2 points
        t1 = 3 - (4 if a == 0 else 2)
        t_prev, t = 2, t1
        for _ in range(n - 1):
            t_prev, t = t, t1 * t - 2 * t_prev
        self.order = (1 << n) + 1 - t
        self.h = 4 if a == 0 else 2
        assert self.order % self.h == 0
        self.r = self.order // self.h
        self.t1 = t1
        self.mu = None   # set by find_mu() once the field tables exist

    def find_mu(self, rng):
        """mu with tau(P) = mu*P on the order-r subgroup: a root of
        X^2 - t1*X + 2 = 0 mod r, selected by checking on random points."""
        r = self.r
        roots = [u for u in range(r) if (u * u - self.t1 * u + 2) % r == 0]
        G = self.random_subgroup_points(rng, 8)
        TG = (self.F.sq[G[0]], self.F.sq[G[1]], G[2])
        for u in roots:
            M = self.smul(u, G)
            if np.all((M[0] == TG[0]) & (M[1] == TG[1]) & ~M[2]):
                self.mu = u
                return u
        raise RuntimeError('no mu found')

    # points: (x, y, inf) int64 arrays; inf is bool
    def neg(self, P):
        x, y, inf = P
        return (x, x ^ y, inf)

    def dbl(self, P):
        F = self.F
        x, y, inf = P
        x_safe = np.where(x == 0, 1, x)
        lam = x ^ F.mul(y, F.inv(x_safe))
        x3 = F.sq[lam] ^ lam ^ self.a
        y3 = F.sq[x] ^ F.mul(lam ^ 1, x3)
        inf3 = inf | (x == 0)
        return (np.where(inf3, 0, x3), np.where(inf3, 0, y3), inf3)

    def add(self, P, Q):
        F = self.F
        x1, y1, i1 = P
        x2, y2, i2 = Q
        x1, x2 = np.broadcast_arrays(x1, x2)
        y1, y2 = np.broadcast_arrays(y1, y2)
        i1, i2 = np.broadcast_arrays(i1, i2)
        same_x = (x1 == x2)
        dx = x1 ^ x2
        dx_safe = np.where(same_x, 1, dx)
        lam = F.mul(y1 ^ y2, F.inv(dx_safe))
        x3 = F.sq[lam] ^ lam ^ x1 ^ x2 ^ self.a
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        D = self.dbl((x1, y1, i1))
        is_dbl = same_x & (y1 == y2) & ~i1 & ~i2
        is_inf = (same_x & (y1 != y2) & ~i1 & ~i2) | (i1 & i2)
        x3 = np.where(is_dbl, D[0], x3)
        y3 = np.where(is_dbl, D[1], y3)
        inf3 = is_inf | (is_dbl & D[2])
        # one operand at infinity
        x3 = np.where(i1 & ~i2, x2, x3)
        y3 = np.where(i1 & ~i2, y2, y3)
        x3 = np.where(i2 & ~i1, x1, x3)
        y3 = np.where(i2 & ~i1, y1, y3)
        return (np.where(inf3, 0, x3), np.where(inf3, 0, y3), inf3)

    def smul(self, s, P):
        x, y, inf = P
        R = (np.zeros_like(x), np.zeros_like(y), np.ones_like(inf, dtype=bool))
        for bit in bin(s)[2:]:
            R = self.dbl(R)
            if bit == '1':
                R = self.add(R, P)
        return R

    def on_curve(self, P):
        F = self.F
        x, y, inf = P
        lhs = F.sq[y] ^ F.mul(x, y)
        rhs = F.mul(F.sq[x], x) ^ (F.sq[x] if self.a else 0) ^ 1
        return inf | (lhs == rhs)

    def points_over_x(self, xs):
        """Return (x, y) for all affine points with x in xs (both signs), x != 0."""
        F = self.F
        xs = np.asarray(xs, dtype=np.int64)
        xs = xs[xs != 0]
        x2 = F.sq[xs]
        c = F.mul(x2, xs) ^ (x2 if self.a else 0) ^ 1          # x^3 + a x^2 + 1
        w = F.mul(c, F.inv(x2))                                 # y = x*u, u^2+u = w
        ok = F.tr[w] == 0
        xs, w = xs[ok], w[ok]
        u = F.half_trace(w)
        y = F.mul(xs, u)
        X = np.concatenate([xs, xs])
        Y = np.concatenate([y, y ^ xs])
        P = (X, Y, np.zeros(len(X), dtype=bool))
        assert np.all(self.on_curve(P))
        return P

    def in_subgroup(self, P):
        R = self.smul(self.r, P)
        return R[2]

    def random_subgroup_points(self, rng, count):
        F = self.F
        out_x, out_y = [], []
        while sum(len(v) for v in out_x) < count:
            xs = rng.integers(1, 1 << F.n, size=2 * count, dtype=np.int64)
            P = self.points_over_x(xs)
            Q = P
            for _ in range(int(math.log2(self.h))):
                Q = self.dbl(Q)
            keep = ~Q[2]
            out_x.append(Q[0][keep])
            out_y.append(Q[1][keep])
        X = np.concatenate(out_x)[:count]
        Y = np.concatenate(out_y)[:count]
        P = (X, Y, np.zeros(count, dtype=bool))
        assert np.all(self.in_subgroup(P))
        return P


# ---------------------------------------------------------------- factor bases
def span(F, basis):
    V = np.zeros(1, dtype=np.int64)
    for b in basis:
        V = np.concatenate([V, V ^ int(b)])
    return V


def find_normal_element(F, rng):
    n = F.n
    while True:
        beta = int(rng.integers(2, 1 << n))
        conj = [beta]
        for _ in range(n - 1):
            conj.append(int(F.sq[conj[-1]]))
        # rank over F_2 by elimination
        rows = list(conj)
        rank = 0
        for bit in range(n - 1, -1, -1):
            piv = next((i for i, r_ in enumerate(rows) if (r_ >> bit) & 1), None)
            if piv is None:
                continue
            p = rows.pop(piv)
            rows = [r_ ^ p if (r_ >> bit) & 1 else r_ for r_ in rows]
            rank += 1
        if rank == n:
            return beta, conj


def tau_orbit_reps(F, xs):
    """Canonical representative (min over the orbit) of each x under squaring."""
    xs = np.asarray(xs, dtype=np.int64)
    rep = xs.copy()
    t = xs.copy()
    for _ in range(F.n - 1):
        t = F.sq[t]
        rep = np.minimum(rep, t)
    return rep


def build_V(F, E, name, k, rng, match_points=None):
    n = F.n
    info = {}
    if name == 'poly':
        V = np.arange(1 << k, dtype=np.int64)
    elif name == 'nb':
        beta, conj = find_normal_element(F, rng)
        V = span(F, conj[:k])
        info['beta'] = beta
    elif name == 'orb':
        # random tau-orbits of x values (x outside F_2), chosen so that the
        # resulting factor base is as close as possible to match_points points
        chosen, used = [], set()
        pts = 0
        while True:
            x = int(rng.integers(2, 1 << n))
            r0 = int(tau_orbit_reps(F, np.array([x]))[0])
            if r0 in used:
                continue
            used.add(r0)
            orb = [x]
            for _ in range(n - 1):
                orb.append(int(F.sq[orb[-1]]))
            orb = sorted(set(orb))
            assert len(orb) == n
            P = E.points_over_x(np.array(orb))
            cnt = int(np.sum(E.in_subgroup(P))) if len(P[0]) else 0
            if pts > 0 and pts + cnt > match_points and abs(pts - match_points) <= abs(pts + cnt - match_points):
                break
            chosen.append(orb)
            pts += cnt
            if pts >= match_points and pts > 0:
                break
        V = np.array(sorted(set(sum(chosen, []))), dtype=np.int64)
        info['orbits'] = len(chosen)
    else:
        raise ValueError(name)
    return V, info


# ---------------------------------------------------------------- enumeration
def decompose_all(E, FB, R, m, inV, chunk=1 << 16):
    """All multisets {i_1..i_m} of FB indices with sum = R. Exact.
    FB = (X, Y, inf) arrays; inV: boolean table over the field of x in V;
    xpos: map x,y -> index via dict."""
    F = E.F
    X, Y = FB[0], FB[1]
    nF = len(X)
    key = {(int(x), int(y)): i for i, (x, y) in enumerate(zip(X.tolist(), Y.tolist()))}
    Rb = (np.full(nF, R[0]), np.full(nF, R[1]), np.zeros(nF, dtype=bool))
    sols = set()
    if m == 2:
        Q = E.add(Rb, E.neg((X, Y, np.zeros(nF, dtype=bool))))
        hit = ~Q[2] & inV[Q[0]]
        for i in np.nonzero(hit)[0].tolist():
            j = key.get((int(Q[0][i]), int(Q[1][i])))
            if j is not None:
                sols.add(tuple(sorted((i, j))))
    elif m == 3:
        negFB = E.neg((X, Y, np.zeros(nF, dtype=bool)))
        T = E.add(Rb, negFB)                      # T_i = R - P_i
        for i in range(nF):
            if T[2][i]:
                continue
            Ti = (np.full(nF, T[0][i]), np.full(nF, T[1][i]), np.zeros(nF, dtype=bool))
            Q = E.add(Ti, negFB)                  # Q_ij = R - P_i - P_j
            hit = ~Q[2] & inV[Q[0]]
            for j in np.nonzero(hit)[0].tolist():
                l = key.get((int(Q[0][j]), int(Q[1][j])))
                if l is not None:
                    sols.add(tuple(sorted((i, j, l))))
    else:
        raise ValueError(m)
    return sols


def usable_shifts(F, xs, inV):
    """Number of j in [0,n) such that x^(2^j) in V for every x in xs."""
    xs = np.asarray(xs, dtype=np.int64)
    cnt = 0
    t = xs.copy()
    for _ in range(F.n):
        if np.all(inV[t]):
            cnt += 1
        t = F.sq[t]
    return cnt


# ---------------------------------------------------------------- main
def run_cell(E, m, k, vname, targets, rng, out, match_points=None, time_limit=None, rep=0, seed=None):
    F = E.F
    n = F.n
    t0 = time.time()
    V, vinfo = build_V(F, E, vname, k, rng, match_points=match_points)
    inV = np.zeros(1 << n, dtype=bool)
    inV[V] = True
    P = E.points_over_x(V)
    keep = E.in_subgroup(P)
    FB = (P[0][keep], P[1][keep], np.zeros(int(keep.sum()), dtype=bool))
    nF = len(FB[0])
    xs = np.unique(FB[0])
    reps = tau_orbit_reps(F, xs)
    n_orbits = int(len(np.unique(reps)))
    # how many conjugates of each FB x lie back in V (self-overlap of V under tau)
    t = xs.copy()
    overlap = np.zeros(len(xs), dtype=np.int64)
    for _ in range(n):
        overlap += inV[t]
        t = F.sq[t]
    extra = {}
    if vname == 'nb':
        # the union of the n shifted windows tau^j(V_nb) is an orbit union; size it
        U = V.copy()
        t = V.copy()
        for _ in range(n - 1):
            t = F.sq[t]
            U = np.union1d(U, t)
        PU = E.points_over_x(U)
        extra['nb_union_size'] = int(len(U))
        extra['nb_union_FB_points'] = int(E.in_subgroup(PU).sum())
    # projection data: for every FB point, (orbit representative x, shift j, sign)
    # such that P = sign * tau^j(P_rep) where P_rep = (rep, min y over rep).
    # representative = min over the orbit INSIDE FB_x (the full-orbit min may lie outside V)
    xset = set(xs.tolist())
    rep_of = {}
    for x in xs.tolist():
        best, t = x, x
        for _ in range(n):
            t = int(F.sq[t])
            if t in xset and t < best:
                best = t
        rep_of[x] = best
    assert len(set(rep_of.values())) == n_orbits
    ymin = {}
    for x, y in zip(FB[0].tolist(), FB[1].tolist()):
        ymin[x] = min(y, ymin.get(x, y))
    proj = []
    for x, y in zip(FB[0].tolist(), FB[1].tolist()):
        rp = rep_of[x]
        t, yt, j = rp, ymin[rp], 0
        while t != x:
            t, yt, j = int(F.sq[t]), int(F.sq[yt]), j + 1
        proj.append((rp, j, 1 if y == yt else -1))
    mu, rr = E.mu, E.r

    def reduced_row(sol):
        acc = {}
        for i in sol:
            rp, j, sg = proj[i]
            acc[rp] = (acc.get(rp, 0) + sg * pow(mu, j, rr)) % rr
        return tuple(sorted((a_, b_) for a_, b_ in acc.items() if b_))

    R = E.random_subgroup_points(rng, targets)
    n_succ, n_dec, n_rows = 0, 0, 0
    shifts = []
    sizes = []
    done = 0
    for ti in range(targets):
        if time_limit is not None and time.time() - t0 > time_limit:
            break
        sols = decompose_all(E, FB, (int(R[0][ti]), int(R[1][ti])), m, inV)
        done += 1
        if sols:
            n_succ += 1
            n_dec += len(sols)
            n_rows += len({reduced_row(s_) for s_ in sols})
            for s in sols:
                shifts.append(usable_shifts(F, FB[0][list(s)], inV))
                sizes.append(len(set(FB[0][list(s)].tolist())))
    lam = math.comb(nF, m) / E.r
    row = dict(n=n, a=E.a, h=E.h, r=E.r, order=E.order, m=m, k=k, V=vname, rep=rep, seed=seed,
               V_size=int(len(V)), FB_points=nF, FB_x=int(len(xs)),
               tau_orbits=n_orbits, mean_conjugates_in_V=float(overlap.mean()) if len(xs) else None,
               targets=done, successes=n_succ, decompositions=n_dec, reduced_rows=n_rows,
               rows_per_attempt=n_rows / done if done else None, mu=mu,
               p_success=n_succ / done if done else None,
               dec_per_success=(n_dec / n_succ) if n_succ else None,
               rel_per_attempt=n_dec / done if done else None,
               heuristic_lambda_r=lam, heuristic_lambda_E=math.comb(nF, m) / E.order,
               heuristic_p_success=1 - math.exp(-lam),
               mean_usable_shifts=float(np.mean(shifts)) if shifts else None,
               usable_shift_hist={str(s): int(c) for s, c in zip(*np.unique(shifts, return_counts=True))} if shifts else {},
               seconds=round(time.time() - t0, 2), censored=done < targets, **extra, **{('V_' + a_): b_ for a_, b_ in vinfo.items()})
    out.write(json.dumps(row) + '\n')
    out.flush()
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ns', default='11,13,17,19,23')
    ap.add_argument('--targets2', type=int, default=4000)
    ap.add_argument('--targets3', type=int, default=1500)
    ap.add_argument('--seed', type=int, default=20261017)
    ap.add_argument('--out', default='results/cells.jsonl')
    ap.add_argument('--curves', default='results/curves.jsonl')
    ap.add_argument('--cell-seconds', type=float, default=420.0)
    ap.add_argument('--wall', type=float, default=80 * 60)
    ap.add_argument('--reps', type=int, default=3)
    args = ap.parse_args()
    T0 = time.time()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = open(args.out, 'w')
    cur = open(args.curves, 'w')
    for n in [int(s) for s in args.ns.split(',')]:
        F = Field(n)
        # choose a: the one with prime r
        choice = None
        for a in (0, 1):
            E = Koblitz(F, a)
            r = E.r
            isp = r > 1 and all(r % p for p in range(2, int(r ** 0.5) + 1))
            # exact point count over the whole field as a check of the trace recursion
            P = E.points_over_x(np.arange(1, 1 << n, dtype=np.int64))
            count = len(P[0]) + 1 + 1          # affine x!=0, plus (0,1), plus O
            cur.write(json.dumps(dict(n=n, a=a, order=E.order, h=E.h, r=r, r_prime=isp,
                                      order_by_point_count=int(count), irreducible=hex(F.f),
                                      primitive_element=F.g)) + '\n')
            assert count == E.order, (n, a, count, E.order)
            if isp and choice is None:
                choice = E
        cur.flush()
        E = choice
        E.find_mu(np.random.default_rng([args.seed, n, 99]))
        print(f'n={n}: a={E.a} #E={E.order}={E.h}*{E.r} mu={E.mu} (root of X^2-({E.t1})X+2 mod r)', flush=True)
        for m in (2, 3):
            k0 = math.ceil(n / m)
            ks = (k0 - 1, k0, k0 + 1) if m == 2 else (k0 - 1, k0, k0 + 1, k0 + 2)
            for k in ks:
                targets = args.targets2 if m == 2 else args.targets3
                match = None
                for vname, rep in [('poly', 0)] + [(v, r_) for r_ in range(args.reps) for v in ('nb', 'orb')]:
                    if time.time() - T0 > args.wall:
                        print('wall budget exhausted; stopping', flush=True)
                        return
                    seed = [args.seed, n, m, k, {'poly': 0, 'nb': 1, 'orb': 2}[vname], rep]
                    rng = np.random.default_rng(seed)
                    row = run_cell(E, m, k, vname, targets, rng, out,
                                   match_points=match, time_limit=args.cell_seconds, rep=rep, seed=seed)
                    if vname == 'poly':
                        match = row['FB_points']
                    print(f"  m={m} k={k} V={vname:4s} rep={rep} |V|={row['V_size']:5d} |FB|={row['FB_points']:5d} "
                          f"orbits={row['tau_orbits']:5d} p={row['p_success']:.3f} rpa={row['rel_per_attempt']:.3f} "
                          f"rows={row['rows_per_attempt']:.3f} lam={row['heuristic_lambda_r']:.3f} shifts={row['mean_usable_shifts']} t={row['seconds']}s"
                          + (' CENSORED' if row['censored'] else ''), flush=True)
    out.close()


if __name__ == '__main__':
    main()
