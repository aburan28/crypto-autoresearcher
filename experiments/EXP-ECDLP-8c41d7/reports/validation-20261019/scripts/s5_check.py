#!/usr/bin/env python3
"""Check 3b: S_5 vanishes on planted decompositions (own computation) + degenerate-target audit.

Instances (p, b, chain V, FB, picks, T) are regenerated with the COMMITTED construction code (pkm.find_prime,
build_chain, factor_base; the seed/rng stream copied literally from block_order_grid.run_instance and checked against
the raw rows' p, b).  Everything that is *checked* uses my own code:
  * elliptic-curve arithmetic (affine, own implementation) -> picks on curve, sum == T, T != O (or == O for degenerate rows)
  * Semaev S_3 written from the textbook formula; S_5 evaluated numerically as
        Res_X( S3(x1,x2,X), Res_Y( S3(X,x3,Y), S3(x4,xT,Y) ) )   via my own Sylvester-determinant code over GF(p) (not Singular, not sympy)
  * sign-enumeration oracle: exists signs s_i with sum s_i P_i = +/-T  (no resultants at all)
  * negative control: S_5 at a perturbed point (x1 -> x1 + delta) must be nonzero (when no decomposition exists)
  * agreement of the producer's expanded S_5 string (what the solvers received) with my numeric S_5 at random points
"""
import sys, json, hashlib, importlib, random, itertools, subprocess, os
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7")

variant = sys.argv[1]            # base | p19
cells = [tuple(map(int, c.split(","))) for c in sys.argv[2:]]   # L,inst
mod = importlib.import_module("block_order_m4" if variant == "base" else "block_order_m4_p19")
bog = mod.base.bog if variant == "p19" else mod.bog
pkm = bog.pkm
msg = bog.msg
plan = json.load(open("/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7/trial-plan.json"))


# ---- own EC arithmetic (affine; None = infinity) ----
def add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    if P == Q: lam = (3 * P[0] * P[0] + a) * pow(2 * P[1], -1, p) % p
    else: lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x3 = (lam * lam - P[0] - Q[0]) % p
    return (x3, (lam * (P[0] - x3) - P[1]) % p)


def neg(P, p): return None if P is None else (P[0], (-P[1]) % p)


def S3(x1, x2, x3, a, b):   # Semaev (textbook)
    return ((x1 - x2) ** 2 * x3 ** 2 - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3 + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2))


def det_mod(M, p):
    n = len(M); M = [r[:] for r in M]; d = 1
    for c in range(n):
        piv = next((r for r in range(c, n) if M[r][c] % p), None)
        if piv is None: return 0
        if piv != c: M[c], M[piv] = M[piv], M[c]; d = -d
        d = d * M[c][c] % p; inv = pow(M[c][c], -1, p)
        for r in range(c + 1, n):
            f = M[r][c] * inv % p
            if f:
                for k in range(c, n): M[r][k] = (M[r][k] - f * M[c][k]) % p
    return d % p


def syl(f, g, p):   # coefficient lists high->low, formal degrees len-1
    m, n = len(f) - 1, len(g) - 1
    N = m + n; M = [[0] * N for _ in range(N)]
    for i in range(n):
        for j, c in enumerate(f): M[i][i + j] = c % p
    for i in range(m):
        for j, c in enumerate(g): M[n + i][i + j] = c % p
    return det_mod(M, p)


def s3coef(u, v, a, b, p):   # S3(u,v,t) as quadratic in t, coefficients high->low
    return [(u - v) ** 2 % p, (-2 * ((u + v) * (u * v + a) + 2 * b)) % p, ((u * v - a) ** 2 - 4 * b * (u + v)) % p]


def interp(xs, ys, p):   # Lagrange, returns coeffs high->low (degree len(xs)-1)
    n = len(xs); coeffs = [0] * n
    for i in range(n):
        num = [1]; den = 1
        for j in range(n):
            if j == i: continue
            num = [(a_ - xs[j] * b_) % p for a_, b_ in zip(num + [0], [0] + num)]   # multiply by (t - xs[j])
            den = den * (xs[i] - xs[j]) % p
        scale = ys[i] * pow(den, -1, p) % p
        coeffs = [(c + scale * q) % p for c, q in zip(coeffs, num)]
    return coeffs


def S5_num(p, a, b, x1, x2, x3, x4, xT):
    """own implementation: Res_X(S3(x1,x2,X), Res_Y(S3(X,x3,Y), S3(x4,xT,Y))) with formal Sylvester resultants mod p"""
    g = s3coef(x4, xT, a, b, p)
    X0s = list(range(5))
    inner_vals = [syl(s3coef(X0, x3, a, b, p), g, p) for X0 in X0s]
    inner = interp(X0s, inner_vals, p)          # degree-4 polynomial in X, high->low
    return syl(s3coef(x1, x2, a, b, p), inner, p)


def signs_oracle(picks_x, xT, a, b, p):
    """x-only: exists P_i with x(P_i)=x_i (either y) and signs with sum == +/-T ?  (True iff S_5 must vanish)"""
    def pts(x):
        y = pkm.sqrt_mod((x ** 3 + a * x + b) % p, p)
        return [] if y is None else [(x, y)]
    yT = pkm.sqrt_mod((xT ** 3 + a * xT + b) % p, p)
    T = (xT, yT)
    Ps = [pts(x)[0] if pts(x) else None for x in picks_x]
    if any(P is None for P in Ps) or yT is None: return None
    for sg in itertools.product((1, -1), repeat=len(Ps)):
        S = None
        for s, P in zip(sg, Ps):
            S = add(S, P if s == 1 else neg(P, p), a, p)
        if S is not None and (S == T or S == neg(T, p)):
            return True
    return False


def producer_S_eval(Sstr, p, pt):
    # evaluate the expanded polynomial string at integer point mod p (python eval; ^ -> **)
    return eval(Sstr.replace("^", "**"), {"__builtins__": {}}, dict(pt)) % p


out = []
for (L, inst) in cells:
    seed = int(hashlib.sha256(f"{plan['seed']}|4|{L}|{inst}".encode()).hexdigest()[:12], 16)
    rng = random.Random(seed)
    p = pkm.find_prime(4, L); a = p - 3
    while True:
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p: break
    chain = pkm.build_chain(p, L, rng)
    rng.sample(range(p), 2 ** L)
    fb = pkm.factor_base(chain["V"], a, b, p)
    trng = random.Random(f"{seed}-False-target")
    kind = "planted" if inst < 4 else "random"
    rec = dict(L=L, inst=inst, kind=kind, p=p, b=b, seed=seed, fb_size=len(fb), V_size=len(chain["V"]))
    if kind == "planted":
        picks = [trng.choice(fb) for _ in range(4)]
        picks = [P if trng.random() < .5 else pkm.ec_neg(P, p) for P in picks]
        rec["picks_on_curve"] = all((P[1] ** 2 - P[0] ** 3 - a * P[0] - b) % p == 0 for P in picks)
        rec["picks_x_in_V"] = all(P[0] in set(chain["V"]) for P in picks)
        rec["picks_chain_eval_eq_c"] = all(pkm.chain_eval(P[0], chain["steps"], p) == chain["c"] for P in picks)
        T = None
        for P in picks: T = add(T, P, a, p)
        rec["T_is_infinity"] = T is None
        if T is None:
            rec["note"] = "degenerate: sum of picks = O (S_5 undefined for x(T)); solvers rightly skipped"
        else:
            xs = [P[0] for P in picks]
            rec["T_on_curve"] = (T[1] ** 2 - T[0] ** 3 - a * T[0] - b) % p == 0
            rec["S5_planted"] = S5_num(p, a, b, *xs, T[0])
            rec["oracle_decomposition_exists"] = signs_oracle(xs, T[0], a, b, p)
            # negative controls: perturb x1 to other x-coordinates; S_5 must be nonzero exactly when the oracle says no decomposition
            neg_ctrl = []
            r2 = random.Random(f"val-{seed}")
            for _ in range(6):
                d = r2.randrange(1, p)
                xs2 = [(xs[0] + d) % p] + xs[1:]
                s5 = S5_num(p, a, b, *xs2, T[0])
                orc = signs_oracle(xs2, T[0], a, b, p)
                neg_ctrl.append(dict(S5=s5, oracle=orc))
            rec["perturbed"] = neg_ctrl
            # agreement with producer's expanded polynomial at random points (what the solvers consumed)
            Sstr = msg.summation_poly(p, 4, a, b, T[0])
            rec["producer_S_len_terms"] = Sstr.count("+") + Sstr.count("-")
            rec["producer_S_at_planted"] = producer_S_eval(Sstr, p, dict(x1=xs[0], x2=xs[1], x3=xs[2], x4=xs[3]))
            ratios = []
            for _ in range(6):
                pt = [r2.randrange(p) for _ in range(4)]
                mine = S5_num(p, a, b, *pt, T[0])
                theirs = producer_S_eval(Sstr, p, dict(zip(["x1", "x2", "x3", "x4"], pt)))
                ratios.append((mine, theirs, (theirs * pow(mine, -1, p)) % p if mine else None))
            rec["producer_vs_mine_random_points(mine,theirs,theirs/mine)"] = ratios
            rec["producer_S_equals_mine_at_random_points"] = all(m_ == t_ for m_, t_, _ in ratios)
    out.append(rec)
    print(json.dumps(rec), flush=True)
