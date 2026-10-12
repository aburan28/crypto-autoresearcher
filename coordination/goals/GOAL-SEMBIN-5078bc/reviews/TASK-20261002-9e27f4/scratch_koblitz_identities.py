"""SCRATCH (TASK-20261002-9e27f4, validator). Hand-sized toy Koblitz curves only.

Tests four STATEMENTS, nothing else:
  S1 (JR-1). On a [lambda]-closed list, the Frobenius orbit-sum and the Frobenius
      characteristic-polynomial relations are relations that are NOT formal
      identities under COR-GEN's stated exclusion (only F + (-F) = 0), cost
      O(n log l) generic operations to find, and have Q-coefficient identically 0
      in Dai's reduction (gamma = sum of lambda-coefficients == 0 mod l).
  S2 (JR-3 clause 1(a), Koblitz). Inside ONE <+-lambda>-orbit (a property of
      lambda mod l, identical for every orbit, independent of any F_V), how many
      non-excluded 2-sum coincidences a+b = c+d exist? Compare with 2n.
  S3 (JR-4 OPEN-A). The halving trace Tr(x) is constant (= Tr(a)) on the
      prime-order subgroup <P>; on E(F_2^n) it is the E -> E/2E filter (gain 2),
      and for h = 4 one halving gives the exact Z/4 filter (gain 4 = h).
  S4 (JR-4 OPEN-D). For H <= (Z/l)^* with <+-lambda> < H, |H| = e = 2n k, the
      orbit-enumeration canonicaliser is poly(n)-computable for k = O(1) and
      H-invariant -- it settles OPEN-D's literal question with zero gain.

No N_2 or decomposition-count statistic of any F_V is computed. Usage:
    python3 scratch_koblitz_identities.py > scratch_koblitz_identities_output.txt
Deterministic (fixed seeds).
"""
import itertools
import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scratch_gf2n_curves import (GF2n, BinCurve, koblitz_order, is_probable_prime,
                                 sqrt_mod)


def toy_koblitz_list(nmin=7, nmax=61):
    out = []
    for n in range(nmin, nmax + 1):
        if not is_probable_prime(n):
            continue
        for a in (0, 1):
            N, t = koblitz_order(n, a)
            h = 4 if a == 0 else 2
            if N % h == 0 and is_probable_prime(N // h):
                out.append((n, a, h, N // h, t))
    return out


def setup(n, a, h, l, t, seed):
    rng = random.Random(seed)
    F = GF2n(n)
    E = BinCurve(F, a, 1)
    while True:
        P = E.mul(h, E.random_point(rng))
        if P is not None and E.mul(l, P) is None:
            break
    disc = (t * t - 8) % l
    r = sqrt_mod(disc, l)
    inv2 = pow(2, -1, l)
    roots = [((t + r) * inv2) % l, ((t - r) * inv2) % l]
    piP = E.frob(P)
    lam = [x for x in roots if E.mul(x, P) == piP]
    assert len(lam) == 1, roots
    return rng, F, E, P, lam[0]


def S1(n, a, h, l, t, seed=1):
    rng, F, E, P, lam = setup(n, a, h, l, t, seed)
    print(f"[S1] n={n} a={a} h={h} l={l} (log2 l={math.log2(l):.2f}) t={t} lambda={lam}")
    assert pow(lam, n, l) == 1 and lam != 1
    gamma_orbit = sum(pow(lam, i, l) for i in range(n)) % l
    gamma_char = (lam * lam - t * lam + 2) % l
    print(f"     gamma(orbit-sum) = sum_i lambda^i mod l = {gamma_orbit}")
    print(f"     gamma(char-poly) = lambda^2 - t lambda + 2 mod l = {gamma_char}")
    ok_orbit = ok_char = ok_2sum = 0
    trials = 20
    for _ in range(trials):
        u = E.mul(rng.randrange(1, l), P)
        # orbit sum on the curve
        S, Z = None, u
        for i in range(n):
            S = E.add(S, Z)
            Z = E.frob(Z)
        ok_orbit += S is None
        # char poly: pi^2 u - t pi u + 2u = O
        p1 = E.frob(u)
        p2 = E.frob(p1)
        tp1 = p1 if t == 1 else E.neg(p1)
        lhs = E.add(E.add(p2, E.neg(tp1)), E.dbl(u))
        ok_char += lhs is None
        # 2-sum coincidence form: pi^2 u + u == t pi u + (-u)
        ok_2sum += E.add(p2, u) == E.add(tp1, E.neg(u))
    print(f"     on-curve checks over {trials} random u in <P>: orbit-sum==O {ok_orbit}/{trials}; "
          f"char-poly==O {ok_char}/{trials}; pi^2u+u == t*pi(u)+(-u) {ok_2sum}/{trials}")
    # Dai's reduction with a lambda-closed list: u_j = r_j P + s_j Q (s_j hidden).
    # A relation sum_i 1*[lambda^i]u_j = O has Q-coefficient s_j*gamma = 0 for all s_j.
    x = rng.randrange(1, l)
    Qt = E.mul(x, P)
    r, s = rng.randrange(l), rng.randrange(1, l)
    u = E.add(E.mul(r, P), E.mul(s, Qt))
    Qcoef = (s * gamma_orbit) % l
    Pcoef = (r * gamma_orbit) % l
    print(f"     Dai reduction on orbit-sum relation: P-coef={Pcoef}, Q-coef={Qcoef} -> "
          f"{'NO information on x (fails with probability 1)' if Qcoef == 0 else 'solves x'}")
    # cost of the harvester that outputs it: n-1 applications of [lambda] as scalar mult
    ops = (n - 1) * (2 * math.ceil(math.log2(l)))
    print(f"     harvester cost (n-1 scalar mults by lambda, <= 2 log2 l ops each): <= {ops} "
          f"generic ops vs sqrt(l) = {math.isqrt(l)}")
    return lam


def S2(n, l, t, lam):
    """Count non-excluded 2-sum coincidences inside one <+-lambda> orbit (residues mod l)."""
    orb = sorted({(e * pow(lam, i, l)) % l for i in range(n) for e in (1, -1)})
    assert len(orb) == 2 * n
    S = set(orb)
    pairs = {}
    for a_, b_ in itertools.combinations(orb, 2):
        pairs.setdefault((a_ + b_) % l, []).append((a_, b_))
    coinc = []
    for ssum, lst in pairs.items():
        for p, q in itertools.combinations(lst, 2):
            a_, b_ = p
            c_, d_ = q
            if (a_ + b_) % l == 0 and (c_ + d_) % l == 0:
                continue  # both sides zero: excluded
            coinc.append((p, q))
    # 3-term zero sums inside the orbit (a+b = c, i.e. a cheap 3-term relation)
    three = sum(1 for a_, b_ in itertools.combinations(orb, 2) if (a_ + b_) % l in S
                and (a_ + b_) % l not in (a_, b_))
    # classes under the <+-lambda> action (multiply all four by +-lambda^k)
    def canon(c):
        best = None
        for k in range(n):
            for e in (1, -1):
                m = (e * pow(lam, k, l)) % l
                p, q = c
                pp = tuple(sorted(((m * p[0]) % l, (m * p[1]) % l)))
                qq = tuple(sorted(((m * q[0]) % l, (m * q[1]) % l)))
                key = tuple(sorted((pp, qq)))
                best = key if best is None or key < best else best
        return best
    classes = {canon(c) for c in coinc}
    # char-poly family check: lambda^{i+2} + lambda^i == t*lambda^{i+1} - lambda^i, signs +-
    fam = set()
    for i in range(n):
        for e in (1, -1):
            a_ = (e * pow(lam, i + 2, l)) % l
            b_ = (e * pow(lam, i, l)) % l
            c_ = (e * t * pow(lam, i + 1, l)) % l
            d_ = (-e * pow(lam, i, l)) % l
            assert (a_ + b_ - c_ - d_) % l == 0
            fam.add(tuple(sorted((tuple(sorted((a_, b_))), tuple(sorted((c_, d_)))))))
    allc = {tuple(sorted((tuple(sorted(p)), tuple(sorted(q))))) for p, q in coinc}
    # second family: (X + t)(X^2 - tX + 2) = X^3 + X + 2t, i.e. lambda^3 u + t u = -lambda u - t u
    fam2 = set()
    for i in range(n):
        for e in (1, -1):
            A = (e * pow(lam, i + 3, l)) % l
            B = (e * t * pow(lam, i, l)) % l
            C = (-e * pow(lam, i + 1, l)) % l
            D = (-e * t * pow(lam, i, l)) % l
            assert (A + B - C - D) % l == 0
            fam2.add(tuple(sorted((tuple(sorted((A, B))), tuple(sorted((C, D)))))))
    print(f"[S2] n={n}: one <+-lambda>-orbit has 2n={2*n} elements; non-excluded 2-sum "
          f"coincidences inside it = {len(allc)} = 4n? {len(allc) == 4*n}; "
          f"family X^2-tX+2: {len(fam)} (subset {fam <= allc}); family (X+t)(X^2-tX+2): "
          f"{len(fam2)} (subset {fam2 <= allc}); unexplained = {len(allc - fam - fam2)}; "
          f"classes under <+-lambda> action = {len(classes)}; 3-term zero-sums inside orbit = {three}")
    return len(allc)


def S3(n, a, h, l, t, seed=3):
    rng, F, E, P, lam = setup(n, a, h, l, t, seed)
    tra = F.tr(a)
    sub_ok = 0
    for _ in range(200):
        Q = E.mul(rng.randrange(1, l), P)
        sub_ok += F.tr(Q[0]) == tra
    full_eq = full_in2E = agree = 0
    T2 = (0, 1)  # (0, sqrt(b)) with b = 1
    assert E.on_curve(T2) and E.dbl(T2) is None
    z4_agree = 0
    m = 400
    for _ in range(m):
        R = E.random_point(rng)
        lr = E.mul(l, R)                    # 2-primary component
        in2E = lr is None or (h == 4 and lr == T2)
        eq = F.tr(R[0]) == tra if R[0] != 0 else None
        full_eq += bool(eq)
        full_in2E += in2E
        agree += (eq == in2E)
        if h == 4:
            # Z/4 filter: class of R in E/4E ~ Z/4 is read off lr in {O, T2, T4, -T4}
            # one halving decides 4E membership; here we check it equals [l]R == O.
            pass
    print(f"[S3] n={n} a={a} h={h}: Tr(x(Q)) == Tr(a)={tra} for {sub_ok}/200 random Q in <P> "
          f"(constant on <P>: gain 1 there); on E(F_2^n): Tr(x)==Tr(a) for {full_eq}/{m}, "
          f"Q in 2E for {full_in2E}/{m}, criterion agrees with 2E-membership {agree}/{m} "
          f"(exact filter E->E/2E, gain 2 <= h={h})")
    if h == 4:
        # exact Z/4 filter via one point halving (Knudsen): R in 4E iff R in 2E and a
        # half H of R lies in 2E (both halves H, H+T2 agree because T2 lies in 2E here).
        def fsqrt(s):
            for _ in range(n - 1):
                s = F.sq(s)
            return s
        ok = cnt = 0
        for _ in range(300):
            R = E.random_point(rng)
            if R[0] == 0 or F.tr(R[0]) != tra:
                continue  # not in 2E
            x, y = R
            lm = F.halftrace(x ^ a)          # lm^2 + lm = x + a
            u = fsqrt(y ^ F.mul(x, lm ^ 1))
            v = F.mul(u, lm ^ u)
            H = (u, v)
            assert E.on_curve(H) and E.dbl(H) == R
            cnt += 1
            in4E_direct = E.mul(l, R) is None
            in4E_via_half = (u != 0 and F.tr(u) == tra)
            ok += in4E_direct == in4E_via_half
        print(f"     h=4: exact Z/4 filter via one point halving agrees with 4E-membership "
              f"{ok}/{cnt} (exact gain 4 = h)")


def S4(n, a, h, l, t, seed=4):
    rng, F, E, P, lam = setup(n, a, h, l, t, seed)
    # smallest e with 2n | e | l-1 and e > 2n
    e = None
    for k in range(2, 200):
        if (l - 1) % (2 * n * k) == 0:
            e = 2 * n * k
            break
    if e is None:
        print(f"[S4] n={n}: no e = 2n k (2<=k<200) divides l-1; skip")
        return
    k = e // (2 * n)
    # generator of the order-e subgroup H
    def order_e_gen():
        for g in range(2, 10_000):
            hh = pow(g, (l - 1) // e, l)
            if all(pow(hh, e // q, l) != 1 for q in set(_pf(e))):
                return hh
    def _pf(m):
        out, d = [], 2
        while d * d <= m:
            while m % d == 0:
                out.append(d)
                m //= d
            d += 1
        if m > 1:
            out.append(m)
        return out
    g = order_e_gen()
    Hset = {pow(g, i, l) for i in range(e)}
    assert lam in Hset and (l - 1) in Hset
    # coset representatives of H / <+-lambda>
    small = {(s * pow(lam, i, l)) % l for i in range(n) for s in (1, l - 1)}
    reps, seen = [], set()
    for hh in sorted(Hset):
        if hh in seen:
            continue
        reps.append(hh)
        seen |= {(hh * x) % l for x in small}
    assert len(reps) == k

    ops = {"scalar_mults": 0, "frob": 0}

    def can(Q):
        best = None
        for c in reps:
            R = E.mul(c, Q)
            ops["scalar_mults"] += 1
            for _ in range(n):
                best = R[0] if best is None or R[0] < best else best
                R = E.frob(R)
                ops["frob"] += 1
        return best
    agree = 0
    trials = 25
    for _ in range(trials):
        Q = E.mul(rng.randrange(1, l), P)
        hh = pow(g, rng.randrange(e), l)
        agree += can(Q) == can(E.mul(hh, Q))
    print(f"[S4] n={n} a={a} l={l}: H <= (Z/l)^* of order e={e} = 2n*{k} contains <+-lambda>; "
          f"orbit-enumeration canonicaliser (min x over the H-orbit) is H-invariant on "
          f"{agree}/{trials} random (Q, h); per call: {k} scalar mults (~{k}*{2*math.ceil(math.log2(l))} "
          f"group ops) + {n*k} Frobenius maps = poly(n). Rho gain sqrt(e/2n)=sqrt({k}) "
          f"is consumed by the {k} extra scalar mults per step.")


def main():
    lst = toy_koblitz_list()
    print("Toy Koblitz curves E_a: y^2+xy=x^3+a x^2+1 with #E/h prime, 7<=n<=61:")
    for row in lst:
        n, a, h, l, t = row
        print(f"   n={n:2d} a={a} h={h} l={l} log2(l)={math.log2(l):.2f}")
    picks = [r for r in lst if r[0] in (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61)]
    for row in picks[:6]:
        n, a, h, l, t = row
        lam = S1(*row)
        S2(n, l, t, lam)
    for row in [r for r in lst if r[1] == 1][:2] + [r for r in lst if r[1] == 0][:2]:
        S3(*row)
    for row in lst[:8]:
        S4(*row)


if __name__ == "__main__":
    main()
