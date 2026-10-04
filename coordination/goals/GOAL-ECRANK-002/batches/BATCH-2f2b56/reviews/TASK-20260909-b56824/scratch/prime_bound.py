#!/usr/bin/env python3
"""Prime-bound analysis for the n=8 d=(1..1) control objects (J3, A.2). EFFICIENT.

For each tuple (b_index 0,1,7 shortfall; 2 control): Weierstrass model ainv
(integers) + 8 forced points (rational), Mestre relation sum P_i = O verified.
Closed-form prediction = certified total 7 (n-1). Committed certifier recorded
6 (shortfall tuples) / 7 (control).

DECISIVE QUESTION: true Q-rank of the 8 points = 7 (shortfall forced by the
certifier's prime window -> instrument-boundary holds) or 6 (genuine second
relation -> control-failure revives)?

METHOD (exact, stdlib, O(p) per prime):
  * usable prime p: odd, p |!= disc, all 8 points p-integral.
  * Reduction mod p is a group homomorphism; a Q-relation reduces to an F_p-
    relation. Contrapositive: k points independent in E(F_p) (order-product
    criterion: |<them>| == prod of their orders) are independent over Q.
  * The 8 points satisfy sum=O -> span rank <= 7. Work with P_1..P_7.
  * For each usable p: compute N_p=#E(F_p), determine E(F_p) structure, find a
    generator (cyclic case), discrete-log the 7 points, compute the
    independence rank and the relation lattice. If rank 7 at ANY usable p,
    Q-rank = 7. If rank 6 at ALL usable p (and a stable second relation lifts
    to Q), Q-rank = 6.
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
    """dict: quadratic residue -> one sqrt (the smaller), for F_p. O(p)."""
    tbl = {}
    for y in range(p):
        r = (y * y) % p
        if r not in tbl:
            tbl[r] = y
    return tbl

def all_points_fp(ai, p):
    """list of all affine points (x,y) in E(F_p). Exact, O(p) via sqrt table."""
    a2, a4, a6 = ai[1] % p, ai[3] % p, ai[4] % p
    tbl = _sqrt_table(p)
    pts = []
    for x in range(p):
        f = (x * x * x + a2 * x * x + a4 * x + a6) % p
        y = tbl.get(f)
        if y is not None:
            pts.append((x, y))
            if y != 0:
                pts.append((x, (-y) % p))
    return pts

def tonelli(n, p):
    n %= p
    if n == 0: return 0
    if pow(n, (p - 1) // 2, p) != 1: return None
    if p % 8 == 5:
        t = pow(n, (p - 1) // 4, p)
        if (t * t) % p == n: return t
        return (t * pow(2, (p - 1) // 4, p)) % p
    Q = p - 1; S = 0
    while Q % 2 == 0: Q //= 2; S += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    c = pow(z, Q, p); R = pow(n, (Q + 1) // 2, p); t = pow(n, Q, p); m = S
    while t != 1:
        i = 1; t2i = (t * t) % p
        while t2i != 1: t2i = (t2i * t2i) % p; i += 1
        b = pow(c, 1 << (m - i - 1), p)
        R = (R * b) % p; c = (c * c) % p; t = (t * c * c) % p; m = i
    return R

def count_points_fp(ai, p):
    return len(all_points_fp(ai, p)) + 1  # + O

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
            if fp_mul(ai, p, cand, P) is None:
                order = cand
            else:
                break
    return order

def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(sieve[i * i::i])
    return [i for i, b in enumerate(sieve) if b]

def usable_primes(ainv, pts, bound):
    disc = E.disc_from_ainv(ainv)
    dens = set()
    for (x, y) in pts:
        dens.add(Fr(x).denominator); dens.add(Fr(y).denominator)
    bad = set()
    for d in dens:
        for q, e in factorize(d): bad.add(q)
    out = []
    for p in primes_upto(bound):
        if p == 2: continue
        if disc % p == 0: continue
        if p in bad: continue
        out.append(p)
    return out

def analyze_prime(ai, p, red7):
    """red7: 7 reduced points (x,y) in F_p. Returns dict with N_p, structure,
    independence rank of the 7, and (if rank<7) a relation vector mod p."""
    pts = all_points_fp(ai, p)
    N = len(pts) + 1
    fac = factorize(N)
    # order of each point
    orders = [point_order_fp(ai, p, P, N, fac) for P in red7]
    # find a generator (point of order N) -> cyclic
    G = None
    for P in pts:
        if point_order_fp(ai, p, P, N, fac) == N:
            G = P; break
    if G is not None:
        # cyclic: discrete log table
        table = {}
        Q = None
        for m in range(N):
            table[Q] = m
            Q = fp_add(ai, p, Q, G)
        ms = [table[P] for P in red7]
        # subgroup <m_1..m_7> in Z/N has order N / gcd(N, m_1..m_7)
        g = N
        for m in ms: g = gcd(g, m)
        subord = N // g
        prod_orders = 1
        for o in orders: prod_orders *= o
        indep = (subord == prod_orders)
        # relation lattice: { (n_i) : sum n_i m_i == 0 mod N }
        # find a basis: it's rank 6 (one equation). Find one nontrivial relation
        # beyond the trivial per-coordinate ones. We'll find the full lattice
        # rank = 7 - (rank of the m_i in Z/N as a Z-module image).
        # The image of Z^7 -> Z/N, (n_i)->sum n_i m_i, has size N/g, so the
        # kernel (relation lattice) has "rank" 7 and index N/g in Z^7... we
        # report the gcd g: the single relation is sum (m_i / g) n_i ... 
        # Simpler: report g and ms; the relation structure is determined.
        return {"N_p": N, "cyclic": True, "orders": orders, "ms": ms,
                "subgroup_order": subord, "prod_orders": prod_orders,
                "independent": indep, "gcd": g}
    else:
        # non-cyclic: fall back to explicit span for the 7 points
        # (rare; do explicit generation, bounded)
        S = {None}; Sord = 1
        chosen = []
        for i, P in enumerate(red7):
            oP = orders[i]
            # |S ∩ <P>|
            inter = 0
            Q = None
            for t in range(oP):
                if Q in S: inter += 1
                Q = fp_add(ai, p, Q, P)
            neword = Sord * oP // inter
            if inter == 1:
                chosen.append(i)
                newS = set(S)
                Q = P
                for _ in range(oP):
                    for s in list(S):
                        newS.add(fp_add(ai, p, Q, s))
                    Q = fp_add(ai, p, Q, P)
                S = newS; Sord = neword
        return {"N_p": N, "cyclic": False, "orders": orders,
                "indep_rank": len(chosen), "chosen": chosen,
                "subgroup_order": Sord}

def main():
    report = {}
    for bi in (0, 1, 7, 2):
        b = N8[bi]
        p_, g, s = E.mestre_polys(list(b))
        r = [E.peval(g, x) for x in b]
        ainv, Wpts = E.cubic_to_weierstrass(s, [(b[i], r[i]) for i in range(8)])
        ainv = [int(z) for z in ainv]
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
        for (x, y) in Wpts:
            S = fr_add(S, (Fr(x), Fr(y)))
        sum_is_O = (S is None)
        disc = E.disc_from_ainv(ainv)
        UP = usable_primes(ainv, Wpts, 6000)
        committed = UP[:60]
        rec = {
            "b": [str(x) for x in b],
            "ainv": ainv,
            "disc": str(disc),
            "points": [[str(x), str(y)] for (x, y) in Wpts],
            "mestre_sum_is_O": sum_is_O,
            "n_usable_le_6000": len(UP),
            "committed_60_max": committed[-1] if len(committed) >= 60 else None,
            "committed_60_all_below_1500": (len(committed) >= 60 and committed[-1] < 1500),
        }
        # reduce the 7 points at each prime (proper modular reduction)
        def mod_frac(fr, p):
            return (fr.numerator * pow(fr.denominator, -1, p)) % p
        def reduce7(p):
            out = []
            for (x, y) in Wpts[:7]:
                out.append((mod_frac(Fr(x), p), mod_frac(Fr(y), p)))
            return out
        # sample: all committed 60 + a spread beyond 1500
        beyond = [p for p in UP if p > 1500]
        # take up to 12 spread across (1500, 6000]
        if beyond:
            step = max(1, len(beyond) // 12)
            sample_beyond = beyond[::step][:12]
        else:
            sample_beyond = []
        scan = {}
        for p in committed + sample_beyond:
            scan[p] = analyze_prime(ainv, p, reduce7(p))
        # histogram of independence (cyclic case) / indep_rank (non-cyclic)
        hist = {}
        for p, d in scan.items():
            key = d.get("independent", d.get("indep_rank"))
            hist[key] = hist.get(key, 0) + 1
        rec["histogram"] = {str(k): v for k, v in hist.items()}
        # examples
        ex = {}
        for p in (committed[:2] + sample_beyond[:4]):
            ex[str(p)] = scan[p]
        rec["examples"] = ex
        report[str(bi)] = rec
        print("=== b_index %d ===" % bi)
        print("  ainv =", ainv)
        print("  mestre sum = O:", sum_is_O)
        print("  usable primes <= 6000:", len(UP))
        print("  committed 60 all < 1500:", rec["committed_60_all_below_1500"],
              " (60th =", rec["committed_60_max"], ")")
        print("  independence histogram (committed 60 + beyond-1500 sample):",
              rec["histogram"])
        print()
    with open(os.path.join(HERE, "prime_bound.json"), "w") as f:
        json.dump(report, f, indent=1)
    print("wrote prime_bound.json")

if __name__ == "__main__":
    main()
