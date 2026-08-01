# EXP-JET-001 / H-JET-001 -- tangent-split summation (first-jet / dual-number
# decomposition of the addition relation) vs serial-S3 harvester.
# Frozen protocol: experiments/EXP-JET-001/specification.yaml (authoritative).
#
# Per instance (prime p, seed): fresh ordinary prime-order curve, standard x-interval
# factor base FB of size B (one point per x), target R = k*G. For every unordered pair
# {P1,P2} (candidate (m-1)-tuple, m=3):
#   (i)  TANGENT SCREEN: exact formal solve (Cramer) of the F_p-linear eps-block of the
#        chained S3 system over F_p[eps]/eps^2 -- counted -> C_lin, survival sigma.
#        eps-block, unknowns = jets (w of intermediate u, v3 of completion x3), RHS free
#        in jets (v1,v2) of the known points:
#           duF0*w                 = -(dx1F0*v1 + dx2F0*v2)
#           duF1*w + dx3F1*v3      = 0            (x_R fixed => v_R = 0)
#        Triangular in (w,v3); consistent for ALL RHS iff Delta = duF0*dx3F1 != 0.
#   (ii) EXACT ZEROTH-ORDER S3-CHAIN TEST ("serial-S3 harvester"): Sylvester resultant
#        H(X) = Res_u(S3(x1,x2,u), S3(u,X,xR)) + Horner evaluation on FB_x -> C_nonlin.
#   (iii) POS-1a cross-check: sign-symmetric EC membership test (Sage EC arithmetic).
# NEG-1: 200 seeded random EC-verified non-relation pairs through screen + chain (leakage).
# Metrics: sigma, C_lin, C_nonlin, p_m, charged-cost exponent fit (3 gate sizes, 95% CI),
# per-relation cost ratio at equal hit rate, sigma_w (jet-degenerate relation fraction).
# All F_p arithmetic in the polynomial route is instrumented (mul/add counted, schoolbook).
# Deterministic: set_random_seed(seed + p) per instance.

import time, json, sys, math, itertools

T_START = time.time()

# ---------------- instrumented F_p arithmetic ----------------
OPS = {"mul": 0, "add": 0, "inv": 0}
def ops_sum(): return OPS["mul"] + OPS["add"] + 10*OPS["inv"]

def fadd(a, b, p): OPS["add"] += 1; return int(a + b) % p
def fsub(a, b, p): OPS["add"] += 1; return int(a - b) % p
def fmul(a, b, p): OPS["mul"] += 1; return int(a * b) % p
def fneg(a, p):    OPS["add"] += 1; return int(-a) % p

# polys: python list of int coeffs, index = power, no trailing zeros; zero poly = []
def pnorm(P, p):
    Q = [int(c) % p for c in P]
    while Q and Q[-1] == 0:
        Q.pop()
    return Q

def is_zero(P): return len(P) == 0

def p_add(P, Q, p):
    if not P: return list(Q)
    if not Q: return list(P)
    n = max(len(P), len(Q)); OPS["add"] += n
    R = [0]*n
    for i in range(n):
        a = P[i] if i < len(P) else 0
        b = Q[i] if i < len(Q) else 0
        R[i] = (a + b) % p
    return pnorm(R, p)

def p_sub(P, Q, p):
    if not Q: return list(P)
    n = max(len(P), len(Q)); OPS["add"] += n
    R = [0]*n
    for i in range(n):
        a = P[i] if i < len(P) else 0
        b = Q[i] if i < len(Q) else 0
        R[i] = (a - b) % p
    return pnorm(R, p)

def p_mul(P, Q, p):
    if not P or not Q: return []
    OPS["mul"] += len(P)*len(Q); OPS["add"] += len(P)*len(Q)
    R = [0]*(len(P)+len(Q)-1)
    for i, a in enumerate(P):
        if a == 0: continue
        for j, b in enumerate(Q):
            if b == 0: continue
            R[i+j] = (R[i+j] + a*b) % p
    return pnorm(R, p)

def p_mul_mixed(F, G, p):
    # F, G: lists of polys (bivariate as poly-in-u with poly-in-X coeffs)
    if not F or not G: return []
    R = [[] for _ in range(len(F)+len(G)-1)]
    for i, fi in enumerate(F):
        if is_zero(fi): continue
        for j, gj in enumerate(G):
            if is_zero(gj): continue
            R[i+j] = p_add(R[i+j], p_mul(fi, gj, p), p)
    while R and is_zero(R[-1]): R.pop()
    return R

def p_deriv(P, p):
    if len(P) <= 1: return []
    OPS["mul"] += len(P)-1
    return pnorm([(i*P[i]) % p for i in range(1, len(P))], p)

def p_eval(P, x, p):
    if not P: return 0
    OPS["mul"] += len(P)-1; OPS["add"] += len(P)-1
    acc = P[-1]
    for i in range(len(P)-2, -1, -1):
        acc = (acc*x + P[i]) % p
    return acc

def perm_sign(perm):
    inv = 0
    for i in range(len(perm)):
        for j in range(i+1, len(perm)):
            if perm[i] > perm[j]: inv += 1
    return -1 if inv % 2 else 1

def det4(M, p):
    acc = []
    for perm in itertools.permutations(range(4)):
        term = None
        for i in range(4):
            e = M[i][perm[i]]
            if is_zero(e):
                term = None; break
            term = list(e) if term is None else p_mul(term, e, p)
        if term is None: continue
        acc = p_add(acc, term, p) if perm_sign(perm) > 0 else p_sub(acc, term, p)
    return acc

# ---------------- Semaev S3 structures ----------------
# S3(x1,x2,x3) = (x1-x2)^2*x3^2 - 2*((x1+x2)*(x1*x2+a)+2*b)*x3 + ((x1*x2-a)^2 - 4*b*(x1+x2))

def s3_plain(x1, x2, x3, a, b, p):
    return ((x1-x2)**2 * x3**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*x3
            + ((x1*x2-a)**2 - 4*b*(x1+x2))) % p

def f0_coeffs(x1, x2, a, b, p, ctx):
    # F0(u) = S3(x1,x2,u): scalar coeffs [c0, c1, c2], counted
    dx = fsub(x1, x2, p); c2 = fmul(dx, dx, p)
    x1x2 = fmul(x1, x2, p); s = fadd(x1, x2, p)
    t1 = fmul(s, fadd(x1x2, a, p), p); t1 = fadd(t1, ctx["b2"], p)
    c1 = fneg(fadd(t1, t1, p), p)
    w = fsub(x1x2, a, p)
    c0 = fsub(fmul(w, w, p), fmul(ctx["b4"], s, p), p)
    return [c0, c1, c2]

def make_ctx(xR, a, b, p):
    # F1(u,X) = S3(u,X,xR) as poly in u with coeffs polys in X (per-target precompute).
    s0 = ops_sum()
    b2 = fadd(b, b, p); b4 = fadd(b2, b2, p)
    xR2 = fmul(xR, xR, p); a2 = fmul(a, a, p)
    d2 = [xR2, fneg(fadd(xR, xR, p), p), 1]                       # (X - xR)^2
    d1 = [fsub(fneg(b4, p), fmul(fadd(a, a, p), xR, p), p),       # -4b - 2a xR
          fsub(fneg(fadd(xR2, xR2, p), p), fadd(a, a, p), p),     # -2xR^2 - 2a
          fneg(fadd(xR, xR, p), p)]                               # -2xR
    d0 = [fsub(a2, fmul(b4, xR, p), p),                           # a^2 - 4b xR
          fsub(fneg(fmul(fadd(a, a, p), xR, p), p), b4, p),       # -2a xR - 4b
          xR2]                                                    # xR^2
    ctx = {"b2": b2, "b4": b4, "xR2": xR2, "d0": d0, "d1": d1, "d2": d2,
           # duF1  = d/du F1  = [d1, 2*d2]
           "duF1": [d1, p_mul([2], d2, p)],
           # dx3F1 = d/dX F1  = [d0', d1', d2']
           "dx3F1": [p_deriv(d0, p), p_deriv(d1, p), p_deriv(d2, p)]}
    ctx["ops_pre"] = ops_sum() - s0
    return ctx

def chain_test(x1, x2, a, b, p, ctx, FBx_list):
    # exact zeroth-order S3-chain test; returns (completions, H(X))
    c0, c1, c2 = f0_coeffs(x1, x2, a, b, p, ctx)
    c0p = [c0] if c0 else []; c1p = [c1] if c1 else []; c2p = [c2] if c2 else []
    d0, d1, d2 = ctx["d0"], ctx["d1"], ctx["d2"]
    M = [[c2p, c1p, c0p, []],
         [[],  c2p, c1p, c0p],
         [d2,  d1,  d0,  []],
         [[],  d2,  d1,  d0]]
    H = det4(M, p)
    comps = sorted(x3 for x3 in FBx_list if p_eval(H, x3, p) == 0)
    return comps, H

def tangent_screen(x1, x2, a, b, p, ctx):
    # exact formal solve (Cramer) of the linear eps-block; returns (survived, info)
    dx = fsub(x1, x2, p); two_dx = fadd(dx, dx, p)
    x1x2 = fmul(x1, x2, p); s = fadd(x1, x2, p)
    c2 = fmul(dx, dx, p); two_c2 = fadd(c2, c2, p)
    t1 = fmul(s, fadd(x1x2, a, p), p); t1 = fadd(t1, ctx["b2"], p)
    c1 = fneg(fadd(t1, t1, p), p)
    w0 = fsub(x1x2, a, p); two_w0 = fadd(w0, w0, p)
    # dx1F0(u) = dS3/dx1 (x1,x2,u): scalars [e0, e1, e2]
    e2 = two_dx
    tmp = fadd(fadd(x1x2, a, p), fmul(s, x2, p), p)
    e1 = fneg(fadd(tmp, tmp, p), p)
    e0 = fsub(fmul(two_w0, x2, p), ctx["b4"], p)
    # dx2F0(u) = dS3/dx2 (x1,x2,u): scalars [f0c, f1c, f2c]
    f2c = fneg(two_dx, p)
    tmp2 = fadd(fmul(s, x1, p), fadd(x1x2, a, p), p)
    f1c = fneg(fadd(tmp2, tmp2, p), p)
    f0c = fsub(fmul(two_w0, x1, p), ctx["b4"], p)
    G = p_add([e0, e1, e2], [f0c, f1c, f2c], p)          # RHS numerator (generic jets)
    Gw = [[g] for g in G]
    duF0b = [[c1], [two_c2]]
    delta_M = p_mul_mixed(duF0b, ctx["dx3F1"], p)       # Cramer determinant (triangular)
    num_w = p_mul_mixed(ctx["dx3F1"], Gw, p)            # w numerator
    num_v3 = p_mul_mixed(ctx["duF1"], Gw, p)            # v3 numerator (sign omitted, cost-identical)
    survived = not is_zero(delta_M)
    return survived, {"delta_deg": (len(delta_M)-1 if delta_M else -1),
                      "num_w_deg": (len(num_w)-1 if num_w else -1),
                      "num_v3_deg": (len(num_v3)-1 if num_v3 else -1)}

def jet_degeneracy(x1, x2, u_star, x3_star, a, b, p, ctx):
    # Delta = duF0(u*) * duF1(u*,x3*) * dx3F1(u*,x3*) at an actual solution; counted
    s0 = ops_sum()
    dx = fsub(x1, x2, p); c2 = fmul(dx, dx, p)
    x1x2 = fmul(x1, x2, p); s = fadd(x1, x2, p)
    t1 = fmul(s, fadd(x1x2, a, p), p); t1 = fadd(t1, ctx["b2"], p)
    c1 = fneg(fadd(t1, t1, p), p)
    v1 = fadd(fmul(fadd(c2, c2, p), u_star, p), c1, p)              # duF0(u*)
    A1 = p_eval(ctx["duF1"][1], x3_star, p)
    A0 = p_eval(ctx["duF1"][0], x3_star, p)
    v2 = fadd(fmul(A1, u_star, p), A0, p)                           # duF1(u*,x3*)
    B2 = p_eval(ctx["dx3F1"][2], x3_star, p)
    B1 = p_eval(ctx["dx3F1"][1], x3_star, p)
    B0 = p_eval(ctx["dx3F1"][0], x3_star, p)
    u2 = fmul(u_star, u_star, p)
    v3 = fadd(fadd(fmul(B2, u2, p), fmul(B1, u_star, p), p), B0, p) # dx3F1(u*,x3*)
    Delta = fmul(fmul(v1, v2, p), v3, p)
    return Delta, ops_sum() - s0

# ---------------- EC side (Sage arithmetic; op-equivalents by stated convention) ----------------
EC_ADD_EQUIV = 19   # 1 inv (10) + 3 mul + 6 add
EC_NEG_EQUIV = 1

def ec_test(P1, P2, R, FBx_set):
    # sign-symmetric membership: hits among R - T for T in {+-(P1+P2), +-(P1-P2)}
    T1 = P1 + P2; T2 = P1 - P2
    hits = []
    for T in (T1, -T1, T2, -T2):
        Q = R - T
        if Q.is_zero(): continue
        xq = int(Q.xy()[0])
        if xq in FBx_set:
            hits.append((T, Q, xq))
    return hits, 6*EC_ADD_EQUIV + 2*EC_NEG_EQUIV

# ---------------- startup self-checks (implementation controls) ----------------
def self_checks():
    res = {}
    p = 101
    # SC1: F1 expansion (d0,d1,d2) matches direct S3 evaluation
    ok = True
    set_random_seed(7)
    for _ in range(12):
        a, b, xR = randint(0, p-1), randint(0, p-1), randint(0, p-1)
        u0, X0 = randint(0, p-1), randint(0, p-1)
        ctx = make_ctx(xR, a, b, p)
        val = (p_eval(ctx["d2"], X0, p)*u0*u0 + p_eval(ctx["d1"], X0, p)*u0
               + p_eval(ctx["d0"], X0, p)) % p
        if val != s3_plain(u0, X0, xR, a, b, p): ok = False
    res["SC1_F1_expansion"] = ok
    # SC2: duF1 / dx3F1 match Sage symbolic partial derivatives of S3
    Rs = PolynomialRing(QQ, ['a','b','x1','x2','x3'])
    aa, bb, y1, y2, y3 = Rs.gens()
    S3sym = ((y1-y2)**2*y3**2 - 2*((y1+y2)*(y1*y2+aa)+2*bb)*y3
             + ((y1*y2-aa)**2 - 4*bb*(y1+y2)))
    d1sym = S3sym.derivative(y1); d2sym = S3sym.derivative(y2)
    ok = True
    for _ in range(12):
        a, b, xR = randint(0, p-1), randint(0, p-1), randint(0, p-1)
        u0, X0 = randint(0, p-1), randint(0, p-1)
        ctx = make_ctx(xR, a, b, p)
        # duF1(u,X) should equal dS3/dx1 (u, X, xR)
        lhs = (p_eval(ctx["duF1"][1], X0, p)*u0 + p_eval(ctx["duF1"][0], X0, p)) % p
        rhs = int(d1sym.subs({aa:a, bb:b, y1:u0, y2:X0, y3:xR})) % p
        if lhs != rhs: ok = False
        lhs2 = (p_eval(ctx["dx3F1"][2], X0, p)*u0*u0 + p_eval(ctx["dx3F1"][1], X0, p)*u0
                + p_eval(ctx["dx3F1"][0], X0, p)) % p
        rhs2 = int(d2sym.subs({aa:a, bb:b, y1:u0, y2:X0, y3:xR})) % p
        if lhs2 != rhs2: ok = False
    res["SC2_jet_partials"] = ok
    # SC3: Sylvester det4 matches Sage resultant
    Ru = PolynomialRing(GF(p), ['u','X']); uu, XX = Ru.gens()
    ok = True
    for _ in range(6):
        a, b, xR = randint(0, p-1), randint(0, p-1), randint(0, p-1)
        x1, x2 = randint(0, p-1), randint(0, p-1)
        if x1 == x2: continue
        F0b = ((x1-x2)**2)*uu**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*uu + ((x1*x2-a)**2 - 4*b*(x1+x2))
        F1b = ((uu-XX)**2)*xR**2 - 2*((uu+XX)*(uu*XX+a)+2*b)*xR + ((uu*XX-a)**2 - 4*b*(uu+XX))
        res_sage = F0b.resultant(F1b, uu)
        ctx = make_ctx(xR, a, b, p)
        comps_H = None
        c0, c1, c2 = f0_coeffs(x1, x2, a, b, p, ctx)
        c0p = [c0] if c0 else []; c1p = [c1] if c1 else []; c2p = [c2] if c2 else []
        M = [[c2p, c1p, c0p, []], [[], c2p, c1p, c0p],
             [ctx["d2"], ctx["d1"], ctx["d0"], []], [[], ctx["d2"], ctx["d1"], ctx["d0"]]]
        H = det4(M, p)
        for _ in range(8):
            X0 = randint(0, p-1)
            if int(res_sage.subs({uu: 0, XX: X0})) % p != p_eval(H, X0, p) % p:
                ok = False
    res["SC3_sylvester_resultant"] = ok
    return res

# ---------------- instance generation ----------------
def gen_curve(p):
    F = GF(p)
    while True:
        a = F.random_element(); b = F.random_element()
        if 4*a**3 + 27*b**2 == 0: continue
        E = EllipticCurve(F, [a, b])
        n = int(E.order())
        if n == p or n == p + 1: continue      # anomalous / supersingular excluded
        if not is_prime(n): continue            # prime-order group (cofactor 1)
        return E, int(a), int(b), n

def build_fb(E, B):
    F = E.base_field(); FB = []; xv = 0
    while len(FB) < B:
        try:
            P = E.lift_x(F(xv))
            if not P.is_zero(): FB.append(P)
        except Exception:
            pass
        xv += 1
    return FB

# ---------------- main experiment ----------------
def main():
    out = {"experiment_id": "EXP-JET-001", "run_id": "RUN-JET-001-a",
           "primes": [101, 211, 431], "stress_prime": 1009,
           "seeds": [20260717, 20260718, 20260719, 20260720, 20260721, 20260722],
           "B_map": {"101": 14, "211": 20, "431": 28, "1009": 40}, "m": 3,
           "op_convention": {"poly_mul": "schoolbook (d1+1)*(d2+1) muls + same-order adds",
                              "horner": "deg muls + deg adds", "inv": "1 inv = 10 mul-equiv",
                              "ec_add": "19 op-equiv", "ec_neg": "1 op-equiv",
                              "zero_poly_ops": "structural, not counted"}}
    print("running startup self-checks...", file=sys.stderr, flush=True)
    sc = self_checks()
    out["self_checks"] = sc
    print("self_checks: %s" % sc, file=sys.stderr, flush=True)
    if not all(sc.values()):
        print("FATAL: self-check failed; aborting (infrastructure/implementation failure, not evidence)",
              file=sys.stderr, flush=True)
        out["aborted"] = True
        print(json.dumps(out))
        return

    instances = []
    for p in [101, 211, 431, 1009]:
        B = out["B_map"][str(p)]
        for seed in out["seeds"]:
            t_inst = time.time()
            set_random_seed(seed + p)
            E, a, b, n = gen_curve(p)
            F = E.base_field()
            FB = build_fb(E, B)
            FBx_list = [int(P.xy()[0]) for P in FB]
            FBx_set = set(FBx_list)
            x_to_point = {}
            for P in FB:
                x_to_point[int(P.xy()[0])] = P
            G = E.gens()[0]
            while True:
                k = randint(1, n-1)
                R = k*G
                if R.is_zero(): continue
                xR = int(R.xy()[0])
                if xR not in FBx_set: break
            ctx = make_ctx(xR, a, b, p)

            pairs = 0
            rel_pairs = 0
            branch_hits = 0
            screen_survived_pairs = 0
            ops_c = 0; ops_t_screen = 0; ops_sigw = 0; ec_ops = 0
            pos1_mismatch = 0
            sigw_degenerate = 0
            rel_witness_verified = 0
            delta_degs = set()
            t_h0 = time.time()
            for i in range(B):
                for j in range(i+1, B):
                    pairs += 1
                    x1, x2 = FBx_list[i], FBx_list[j]
                    s0 = ops_sum()
                    comps, H = chain_test(x1, x2, a, b, p, ctx, FBx_list)
                    s1 = ops_sum()
                    survived, info = tangent_screen(x1, x2, a, b, p, ctx)
                    s2 = ops_sum()
                    ops_c += s1 - s0; ops_t_screen += s2 - s1
                    delta_degs.add(info["delta_deg"])
                    if survived:
                        screen_survived_pairs += 1
                    # POS-1a: EC cross-check
                    hits, ecop = ec_test(FB[i], FB[j], R, FBx_set)
                    ec_ops += ecop
                    ec_set = sorted(set(xq for (_, _, xq) in hits))
                    if ec_set != comps:
                        pos1_mismatch += 1
                    if hits:
                        rel_pairs += 1
                        branch_hits += len(hits)
                        # witness verification (verifier-independent EC arithmetic)
                        for (T, Q, xq) in hits:
                            P3 = x_to_point[xq]
                            if T + P3 == R or T - P3 == R:
                                rel_witness_verified += 1
                        # sigma_w: jet-degeneracy at the first hitting branch
                        T, Q, xq = hits[0]
                        u_star = int(T.xy()[0])
                        Delta, dops = jet_degeneracy(x1, x2, u_star, xq, a, b, p, ctx)
                        ops_sigw += dops
                        if Delta == 0:
                            sigw_degenerate += 1
            t_h1 = time.time()

            # NEG-1: random non-relation tuples through screen + full pipeline
            neg_tested = 0; neg_screen_survived = 0; neg_chain_rel = 0; neg_resamples = 0
            ops_neg = 0
            while neg_tested < 200:
                k1 = randint(1, n-1); k2 = randint(1, n-1)
                Q1 = k1*G; Q2 = k2*G
                if Q1.is_zero() or Q2.is_zero(): continue
                xq1 = int(Q1.xy()[0]); xq2 = int(Q2.xy()[0])
                if xq1 == xq2: continue
                hits, _ = ec_test(Q1, Q2, R, FBx_set)
                if hits:
                    neg_resamples += 1
                    continue          # keep only verified non-relations
                neg_tested += 1
                s0 = ops_sum()
                survived, _ = tangent_screen(xq1, xq2, a, b, p, ctx)
                s1 = ops_sum()
                comps_neg, _ = chain_test(xq1, xq2, a, b, p, ctx, FBx_list)
                s2 = ops_sum()
                ops_neg += (s1 - s0)   # screen ops only
                if survived: neg_screen_survived += 1
                if comps_neg: neg_chain_rel += 1
            t_h2 = time.time()

            pm = rel_pairs / float(pairs)
            sigma = screen_survived_pairs / float(pairs)   # measured screen survival rate
            sigma_meas = sigma
            C_lin = ops_t_screen / float(pairs)
            C_nonlin = ops_c / float(pairs)
            candidates_needed = (B / pm) if pm > 0 else None
            LA = B*B
            charged_c = (candidates_needed * C_nonlin + LA) if candidates_needed else None
            charged_t = (candidates_needed * (C_lin + 1.0 * C_nonlin) + LA) if candidates_needed else None
            nx = (n - 1) / 2.0
            pos1b_pred = pairs * 4 * (B / nx)
            inst = {
                "p": p, "seed": seed, "a": a, "b": b, "n": n, "B": B, "xR": xR,
                "pairs": pairs, "relation_pairs": rel_pairs, "branch_hits": branch_hits,
                "p_m": pm, "p_m_costmodel_est": (B*B) / (2.0*n),
                "sigma": sigma, "screen_survived_pairs": screen_survived_pairs,
                "delta_degs": sorted(delta_degs),
                "sigma_w_degenerate_relations": sigw_degenerate,
                "sigma_w": (sigw_degenerate / float(rel_pairs)) if rel_pairs else None,
                "C_lin": C_lin, "C_nonlin": C_nonlin,
                "ops_c_total": ops_c, "ops_screen_total": ops_t_screen,
                "ops_sigw_total": ops_sigw, "ops_pre": ctx["ops_pre"],
                "ec_op_equiv_total": ec_ops,
                "rel_witness_verified": rel_witness_verified,
                "candidates_needed_for_B_relations": candidates_needed,
                "LA_toy": LA, "descent_toy": 0,
                "charged_classical": charged_c, "charged_tangent": charged_t,
                "per_relation_cost_classical": (ops_c / float(rel_pairs)) if rel_pairs else None,
                "per_relation_cost_tangent": ((ops_c + ops_t_screen) / float(rel_pairs)) if rel_pairs else None,
                "per_relation_cost_ratio": ((ops_c / float(ops_c + ops_t_screen))) if rel_pairs else None,
                "yield_per_op_classical": (rel_pairs / float(ops_c)) if ops_c else None,
                "yield_per_op_tangent": (rel_pairs / float(ops_c + ops_t_screen)) if (ops_c + ops_t_screen) else None,
                "pos1_mismatches": pos1_mismatch,
                "pos1b_branch_hits_pred": pos1b_pred,
                "pos1b_ratio": (branch_hits / pos1b_pred) if pos1b_pred else None,
                "neg1": {"tested": neg_tested, "screen_survived": neg_screen_survived,
                         "survival_rate": neg_screen_survived / float(neg_tested),
                         "chain_relations_claimed": neg_chain_rel,
                         "resamples_relation_pairs": neg_resamples,
                         "ops_screen_total": ops_neg},
                "wall_seconds": {"harvest": t_h1 - t_h0, "neg_control": t_h2 - t_h1,
                                 "instance_total": t_h2 - t_inst},
            }
            instances.append(inst)
            print("p=%-5d seed=%d n=%-5d B=%-3d pairs=%-4d rel=%-3d pm=%.3f sigma=%.3f C_lin=%.1f C_nonlin=%.1f ratio=%.3f pos1_mis=%d neg1=%d/%d t=%.1fs"
                  % (p, seed, n, B, pairs, rel_pairs, pm, sigma, C_lin, C_nonlin,
                     inst["per_relation_cost_ratio"] or -1, pos1_mismatch,
                     neg_screen_survived, neg_tested, t_h2 - t_inst),
                  file=sys.stderr, flush=True)

    # ---------------- fits and gate arithmetic ----------------
    def ols(points):
        N = len(points)
        mx = sum(x for x, _ in points)/N; my = sum(y for _, y in points)/N
        sxx = sum((x-mx)**2 for x, _ in points)
        sxy = sum((x-mx)*(y-my) for x, y in points)
        syy = sum((y-my)**2 for x, y in points)
        slope = sxy/sxx
        s2 = sum((y - (my + slope*(x-mx)))**2 for x, y in points)/(N-2)
        se = math.sqrt(s2/sxx)
        tcrit = 2.120 if N == 18 else 2.074
        return {"n_points": N, "slope": slope, "se": se,
                "ci95": [slope - tcrit*se, slope + tcrit*se],
                "r2": (sxy*sxy)/(sxx*syy) if sxx*syy > 0 else None}

    pts3_c = [(math.log(float(i["n"])), math.log(i["charged_classical"]))
              for i in instances if i["p"] != 1009 and i["charged_classical"]]
    pts3_t = [(math.log(float(i["n"])), math.log(i["charged_tangent"]))
              for i in instances if i["p"] != 1009 and i["charged_tangent"]]
    pts4_c = [(math.log(float(i["n"])), math.log(i["charged_classical"]))
              for i in instances if i["charged_classical"]]
    pts4_t = [(math.log(float(i["n"])), math.log(i["charged_tangent"]))
              for i in instances if i["charged_tangent"]]
    fit = {"three_sizes_classical": ols(pts3_c), "three_sizes_tangent": ols(pts3_t),
           "four_sizes_stress_included_classical": ols(pts4_c),
           "four_sizes_stress_included_tangent": ols(pts4_t)}

    by_prime = {}
    for p in [101, 211, 431, 1009]:
        rows = [i for i in instances if i["p"] == p]
        def mean(key):
            vals = [r[key] for r in rows if r[key] is not None]
            return sum(vals)/float(len(vals)) if vals else None
        by_prime[str(p)] = {
            "n_mean": mean("n"), "B": rows[0]["B"], "pairs": rows[0]["pairs"],
            "relation_pairs_mean": mean("relation_pairs"),
            "p_m_mean": mean("p_m"), "sigma_mean": mean("sigma"),
            "sigma_w_mean": mean("sigma_w"),
            "C_lin_mean": mean("C_lin"), "C_nonlin_mean": mean("C_nonlin"),
            "per_relation_cost_ratio_mean": mean("per_relation_cost_ratio"),
            "per_relation_cost_ratio_min": min(r["per_relation_cost_ratio"] for r in rows),
            "per_relation_cost_ratio_max": max(r["per_relation_cost_ratio"] for r in rows),
            "charged_classical_mean": mean("charged_classical"),
            "charged_tangent_mean": mean("charged_tangent"),
            "yield_per_op_classical_mean": mean("yield_per_op_classical"),
            "yield_per_op_tangent_mean": mean("yield_per_op_tangent"),
            "pos1_mismatches_total": sum(r["pos1_mismatches"] for r in rows),
            "pos1b_ratio_mean": mean("pos1b_ratio"),
            "neg1_survival_mean": mean("neg1") if False else None,
        }
        by_prime[str(p)]["neg1_survival_mean"] = sum(
            r["neg1"]["survival_rate"] for r in rows)/float(len(rows))
        by_prime[str(p)]["neg1_chain_relations_claimed_total"] = sum(
            r["neg1"]["chain_relations_claimed"] for r in rows)

    gate = {
        "exponent_threshold": 0.49, "ratio_threshold": 4.0,
        "three_sizes_exponent": {"classical": fit["three_sizes_classical"],
                                 "tangent": fit["three_sizes_tangent"]},
        "per_relation_cost_ratio_by_prime": {
            p: {"mean": by_prime[p]["per_relation_cost_ratio_mean"],
                "min": by_prime[p]["per_relation_cost_ratio_min"],
                "max": by_prime[p]["per_relation_cost_ratio_max"]}
            for p in by_prime},
        "ratio_sustained_ge_4x": all(
            by_prime[p]["per_relation_cost_ratio_mean"] >= 4.0 for p in by_prime),
        "note": "ratio = classical per-relation cost / tangent per-relation cost at equal hit rate"
    }

    out["instances"] = instances
    out["fit"] = fit
    out["by_prime"] = by_prime
    out["gate"] = gate
    out["totals"] = {"wall_seconds": time.time() - T_START,
                     "ops_mul": OPS["mul"], "ops_add": OPS["add"]}
    print("total wall %.1fs" % (time.time() - T_START), file=sys.stderr, flush=True)

    def _ser(o):
        # Sage Integers -> int; Sage RealNumber/other numerics -> float (never truncate)
        try:
            f = float(o)
            i = int(f)
            return i if i == f else f
        except Exception:
            return str(o)
    print(json.dumps(out, default=_ser))

main()
