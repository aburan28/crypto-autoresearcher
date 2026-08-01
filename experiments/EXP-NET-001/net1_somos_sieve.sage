# ============================================================================
# net1_somos_sieve.sage — EXP-NET-001 / ledger family NET / candidate B1
# Executor task TASK-20260717-B1 (protocol: experiments/EXP-NET-001/specification.yaml)
#
# Elliptic-net (EDS) relation supply: Somos-collision sieve vs BSGS at equal op
# budget. Measures collision statistics of FB-index net terms vs the birthday
# model, k-yielding relations via exact EDS-index consistency, and the charged
# op arithmetic of net-domain k-recovery. All randomness from seeded
# random.Random streams (deterministic across runs/platforms).
#
# Usage: sage experiments/EXP-NET-001/net1_somos_sieve.sage [out.json] [seeds_csv]
# ============================================================================
import json, os, sys, time, subprocess, platform
from random import Random
from sage.all import *

T0 = time.time()
WALL_LIMIT = 240.0          # internal guard (protocol stopping rule)
MAXC = 600                  # max collisions k-analyzed per instance/scope (deterministic stride sample)

PRIMES = [101, 431, 1601]
SEEDS  = [20260717, 20260718, 20260719, 20260720, 20260721, 20260722]
MIN_N  = 37
MIN_EMBDEG = 7

OUT = sys.argv[1] if len(sys.argv) > 1 else "experiments/EXP-NET-001/runs/RUN-NET-001-a/raw.json"
if len(sys.argv) > 2:
    SEEDS = [int(s) for s in sys.argv[2].split(",")]

deviations = ["PC1 uses reduced Tate pairing (Stange 2007 Thm 1) instead of Weil: toy fields host no independent rational n-torsion pair (n^2 > #E at these p).",
              "k-consistency analysis capped at MAXC=%d collisions per instance/scope (deterministic stride sample); counts reported for the analyzed sample." % MAXC]

def R(seed, p, tag):
    return Random(int((int(seed) * 10000019 + int(p) * 100003 + int(tag) * 97) % (2**63)))

def log(msg):
    print("[%.1fs] %s" % (time.time() - T0, msg), flush=True)

def r4(x):
    return float("%.4f" % float(x))

def r6(x):
    return float("%.6f" % float(x))

def r3(x):
    return float("%.3f" % float(x))

# ---------- EDS (rank-1 elliptic net), integer arithmetic mod p ----------
def eds_init_int(E, P, p):
    a, b = E.a4(), E.a6()
    x, y = P.xy()
    x, y, a, b = int(x), int(y), int(a), int(b)
    w2 = (2*y) % p
    w3 = (3*pow(x,4,p) + 6*a*pow(x,2,p) + 12*b*x - a*a) % p
    w4 = (4*y*(pow(x,6,p) + 5*a*pow(x,4,p) + 20*b*pow(x,3,p) - 5*a*a*pow(x,2,p) - 4*a*b*x - 8*b*b - a*a*a)) % p
    return w2, w3, w4

def eds_extend_int(w2, w3, w4, N, p):
    # W[0..N] as python ints; W[0]=0, W[1]=1
    W = [0]*(N+1)
    W[1] = 1; W[2] = w2 % p; W[3] = w3 % p; W[4] = w4 % p
    w2inv = pow(W[2], p-2, p)
    for t in range(5, N+1):
        if t & 1:
            m = (t+1)//2
            W[t] = (W[m+1]*pow(W[m-1],3,p) - W[m-2]*pow(W[m],3,p)) % p
        else:
            m = t//2
            W[t] = (W[m]*(W[m+2]*pow(W[m-1],2,p) - W[m-2]*pow(W[m+1],2,p))) % p
            W[t] = (W[t]*w2inv) % p
    return W

def on_curve_point(E, p, a, b, rng):
    F = GF(p)
    while True:
        x = rng.randrange(p)
        rhs = (pow(x,3,p) + a*x + b) % p
        if rhs == 0:
            continue
        if pow(rhs, (p-1)//2, p) == 1:
            y = pow(rhs, (p+1)//4, p) if p % 4 == 3 else None
            if y is None or (y*y) % p != rhs:
                y = GF(p)(rhs).sqrt()
                y = int(y)
            if rng.randrange(2):
                y = (-y) % p
            return E(F(x), F(y))

def find_instance(p, seed, tag_base, require_embdeg=True):
    rng = R(seed, p, tag_base)
    tries = 0
    while tries < 400:
        tries += 1
        a, b = rng.randrange(p), rng.randrange(p)
        if (4*a**3 + 27*b**2) % p == 0:
            continue
        E = EllipticCurve(GF(p), [a, b])
        N = int(E.cardinality())
        if N == p + 1:
            continue
        cand = [int(q) for q, e in factor(N) if q >= MIN_N]
        if not cand:
            continue
        n = max(cand)
        emb = int(Mod(p, n).multiplicative_order())
        if require_embdeg and emb < MIN_EMBDEG:
            continue
        prng = R(seed, p, tag_base + 1)
        P = None
        for t in range(40):
            G = on_curve_point(E, p, a, b, prng)
            P = (N // n) * G
            if not P.is_zero():
                break
        if P is None or P.is_zero():
            continue
        assert (n * P).is_zero()
        return dict(E=E, N=N, n=n, h=N // n, embdeg=emb, P=P, a=a, b=b, tries=tries)
    return None

# ---------- sieve ----------
def enumerate_collisions(items):
    # items: list of (value:int, tag:tuple). returns list of collision pairs.
    d = {}
    for v, tag in items:
        d.setdefault(v, []).append(tag)
    cols = []
    for v, tags in d.items():
        if len(tags) > 1:
            for i in range(len(tags)):
                for j in range(i+1, len(tags)):
                    cols.append((v, tags[i], tags[j]))
    return cols

def fam(tag):
    return tag[0]

def fam_pair(t1, t2):
    return tuple(sorted([t1[0], t2[0]]))

def birthday_expect(fam_sizes, p):
    exp = {}
    fams = list(fam_sizes)
    for i in range(len(fams)):
        for j in range(i, len(fams)):
            X, Y = fams[i], fams[j]
            key = tuple(sorted([X, Y]))
            if X == Y:
                M = fam_sizes[X]
                exp[key] = M*(M-1)/2.0/p
            else:
                exp[key] = fam_sizes[X]*fam_sizes[Y]*1.0/p
    return exp

def count_by_fampair(cols):
    c = {}
    for v, t1, t2 in cols:
        key = "".join(fam_pair(t1, t2))
        c[key] = c.get(key, 0) + 1
    return c

def enrich(counts, expect):
    out = {}
    for key, e in expect.items():
        k = "".join(key)
        out[k] = r4(counts.get(k, 0) / e) if e > 0 else None
    return out

# ---------- k-consistency analysis ----------
def item_form(tag):
    # returns (const_list, lin_list, sq_exp) with value = prod W_P(const) * prod W_P(lin*k') * W_P(k')^sq_exp
    f = tag[0]
    if f == "P":   return ([tag[1]], [], 0)
    if f == "Q":   return ([], [tag[1]], -tag[1]**2)
    if f == "PP":  return ([tag[1], tag[2]], [], 0)
    if f == "QQ":  return ([], [tag[1], tag[2]], -(tag[1]**2 + tag[2]**2))
    if f == "PQ":  return ([tag[1]], [tag[2]], -tag[2]**2)
    raise ValueError(f)

def analyze_collisions(cols, WP, n, p, k_true, assert_k=True):
    # cols involving >=1 Q-term only. Returns classification stats.
    qcols = [c for c in cols if any(fam(t) in ("Q", "QQ", "PQ") for t in c[1:])]
    qcols.sort(key=lambda c: (c[0], str(c[1]), str(c[2])))
    total = len(qcols)
    sampled = total > MAXC
    if sampled:
        stride = total / MAXC
        qcols = [qcols[int(i*stride)] for i in range(MAXC)]
    pm1 = p - 1
    n1 = n - 1
    universal = yielding = narrowing = 0
    sumS = 0
    maxS = 0
    first_yield_rank = None
    amb = None  # global ambiguity set (intersection), capped tracking
    amb_size = n1
    for idx, (v, t1, t2) in enumerate(qcols, start=1):
        cL, lL, sL = item_form(t1)
        cR, lR, sR = item_form(t2)
        AL = 1
        for c in cL: AL = AL * WP[c] % p
        AR = 1
        for c in cR: AR = AR * WP[c] % p
        eLR = (sL - sR) % pm1   # consistent iff sLval * wk^(sL-sR) == sRval
        S_size = 0
        k_in = False
        for kpr in range(1, n):
            wk = WP[kpr]
            sLv = AL
            for l in lL: sLv = sLv * WP[l*kpr] % p
            sRv = AR
            for l in lR: sRv = sRv * WP[l*kpr] % p
            if (sLv * pow(wk, eLR, p)) % p == sRv:
                S_size += 1
                if kpr == k_true: k_in = True
        if assert_k and not k_in:
            raise RuntimeError("true k missing from consistency set: %s" % str((v, t1, t2)))
        sumS += S_size
        maxS = max(maxS, S_size)
        if S_size == n1:
            universal += 1
        elif S_size == 1:
            yielding += 1
            if first_yield_rank is None:
                first_yield_rank = idx
        else:
            narrowing += 1
    return dict(total_q_collisions=total, analyzed=len(qcols), sampled=sampled,
                universal=universal, yielding=yielding, narrowing=narrowing,
                mean_S=r4(sumS/float(len(qcols))) if qcols else None,
                max_S=maxS, first_yielding_rank=first_yield_rank)

# ---------- op accounting (protocol policy) ----------
import math
def ilog2(x):
    return max(1, math.ceil(math.log2(max(2, x))))

def op_accounting(n, B, p):
    M_PP = B*(B+1)//2
    M_PQ = B*B
    M = 2*M_PP + M_PQ
    ops_fb = 2*(25 + 10 + 6*max(0, B-4))
    ops_enum_s1 = 2*B*ilog2(2*B)
    ops_enum_s2 = M + M*ilog2(M)
    ops_pre = 6*max(0, B*(n-1) - 4)
    ops_verify_per_col = 15*(n-1)
    bsgs = 2*int(math.ceil(math.sqrt(n)))*16 + int(math.ceil(math.sqrt(n)))*ilog2(int(math.ceil(math.sqrt(n))))
    return dict(M_PP=M_PP, M_QQ=M_PP, M_PQ=M_PQ, M_total=M,
                ops_fb=ops_fb, ops_enum_s1=ops_enum_s1, ops_enum_s2=ops_enum_s2,
                ops_pre=ops_pre, ops_verify_per_collision=ops_verify_per_col,
                bsgs_ops=bsgs, bsgs_exponent=r4(math.log(bsgs)/math.log(n)))

# ---------- pairing control (PC1) ----------
def pairing_control(p, seed):
    rng = R(seed, p, 21)
    F = GF(p)
    cand_ns = [int(q) for q, e in factor(p-1) if q >= 5]
    rec = dict(p=p, status="no_instance", tries=0)
    best = None
    for tries in range(1, 201):
        rec["tries"] = tries
        a, b = rng.randrange(p), rng.randrange(p)
        if (4*a**3 + 27*b**2) % p == 0:
            continue
        E = EllipticCurve(F, [a, b])
        N = int(E.cardinality())
        good = [n for n in cand_ns if N % n == 0]
        if not good:
            continue
        n = max(good)
        prng = R(seed, p, 22)
        P = None
        for t in range(40):
            G = on_curve_point(E, p, a, b, prng)
            cand = (N // n) * G
            if not cand.is_zero() and (n * cand).is_zero():
                P = cand
                break
        if P is None:
            continue
        qrng = R(seed, p, 23)
        for t in range(40):
            Q = on_curve_point(E, p, a, b, qrng)
            tau_sage = P.tate_pairing(Q, n, 1)
            if tau_sage == 1:
                continue
            w2, w3, w4 = eds_init_int(E, P, p)
            WPn = eds_extend_int(w2, w3, w4, n + 2, p)
            xP, yP = int(P.xy()[0]), int(P.xy()[1])
            Rpt = P + Q
            if Rpt.is_zero():
                continue   # Q = -P: net term W(2,1) undefined for pairing; try next Q
            xR, yR = int(Rpt.xy()[0]), int(Rpt.xy()[1])
            xQ = int(Q.xy()[0])
            D = [1, 1, (xP - xR) % p]
            D.append((4*yP*yR - (xQ - xP)*D[2]*D[2]) % p)   # D(3)
            W2v, W3v = WPn[2], WPn[3]
            ok = True
            for i in range(2, n):
                if D[i-2] == 0:
                    ok = False
                    break
                nxt = (D[i+1]*D[i-1]*W2v*W2v - W3v*D[i]*D[i]) % p
                nxt = nxt * pow(D[i-2], p-2, p) % p
                D.append(nxt)
            if not ok:
                continue
            tau_net = pow(D[n+1] * pow(WPn[n+1], p-2, p) % p, (p-1)//n, p)
            this = dict(p=p, status="done", tries=tries, n=n, a=a, b=b, N=N,
                        tau_net=int(tau_net), tau_sage=int(tau_sage),
                        nonvacuous=(int(tau_sage) != 1), passed=(int(tau_net) == int(tau_sage)))
            if best is None or n > best["n"]:
                best = this
            if n == max(cand_ns):
                break   # cannot do better than the largest prime divisor of p-1
    if best is not None:
        return best
    return rec

# ---------- main ----------
def main():
    log("EXP-NET-001 net1_somos_sieve starting; primes=%s seeds=%s" % (PRIMES, SEEDS))
    try:
        sage_ver = subprocess.check_output(["sage", "--version"], text=True).strip()
    except Exception:
        sage_ver = "unknown"
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        git_dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        git_dirty_n = len([l for l in git_dirty.splitlines() if l.strip()])
    except Exception:
        git_commit, git_dirty_n = "unknown", -1

    results = dict(
        experiment_id="EXP-NET-001", run_id="RUN-NET-001-a",
        script="experiments/EXP-NET-001/net1_somos_sieve.sage",
        protocol=dict(primes=PRIMES, seeds=SEEDS, min_n=MIN_N, min_embdeg=MIN_EMBDEG,
                      B_rule="ceil(sqrt(n))", MAXC=MAXC,
                      specification="experiments/EXP-NET-001/specification.yaml"),
        environment=dict(sage_version=sage_ver, python_version=sys.version.split()[0],
                         platform=platform.platform(), machine=platform.machine(),
                         git_commit=git_commit, git_dirty_entries=git_dirty_n),
        timestamps=dict(started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(T0))),
        deviations=list(deviations),
        positive_controls={}, instances=[], aggregates={}, validity_selfcheck={},
    )

    # ---- PC1 pairing control (dedicated embedding-degree-1 instances) ----
    pc1 = []
    for p in PRIMES:
        rec = pairing_control(p, SEEDS[0])
        pc1.append(rec)
        log("PC1 p=%d -> %s" % (p, {k: rec[k] for k in ("status", "n", "passed") if k in rec}))
    results["positive_controls"]["PC1_pairing"] = pc1

    pc2_all = True
    k_in_S_ok = True
    skipped = []

    # ---- main instances ----
    for p in PRIMES:
        for seed in SEEDS:
            tinst = time.time()
            inst = find_instance(p, seed, 1)
            if inst is None:
                results["instances"].append(dict(p=p, seed=seed, status="no_instance_found"))
                continue
            E, N, n, h, emb, P = inst["E"], inst["N"], inst["n"], inst["h"], inst["embdeg"], inst["P"]
            B = int(math.ceil(math.sqrt(n)))
            krng = R(seed, p, 3)
            k = krng.randrange(2, n - 1)
            Q = k * P
            L = B * (n - 1)
            w2, w3, w4 = eds_init_int(E, P, p)
            WP = eds_extend_int(w2, w3, w4, L, p)
            u2, u3, u4 = eds_init_int(E, Q, p)
            WQ = eds_extend_int(u2, u3, u4, B, p)
            assert all(WP[i] != 0 for i in range(1, B+1)), "zero FB term in WP"
            assert all(WQ[i] != 0 for i in range(1, B+1)), "zero FB term in WQ"

            # ---- PC2 exactness on this instance ----
            pc2 = {}
            crng = R(seed, p, 4)
            hi = min(2*B, n - 3)
            xs = [crng.randrange(2, hi) for _ in range(8)]
            xP = int(P.xy()[0])
            pc2["x_mP_identity"] = all(int((m*P).xy()[0]) == (xP - WP[m-1]*WP[m+1]*pow(WP[m]*WP[m] % p, p-2, p)) % p for m in xs)
            WPk = WP[k]
            pc2["translation_identity"] = all((WQ[i]*pow(WPk, i*i, p)) % p == WP[i*k] for i in range(1, B+1))
            somos_ok = True
            for _ in range(8):
                i = crng.randrange(4, B)
                j = crng.randrange(2, i)
                if (WP[i+j]*WP[i-j] - (WP[i+1]*WP[i-1]*WP[j]*WP[j] - WP[j+1]*WP[j-1]*WP[i]*WP[i])) % p != 0:
                    somos_ok = False
            pc2["somos_identity"] = somos_ok
            pc2["passed"] = all(pc2.values())
            pc2_all = pc2_all and pc2["passed"]

            # ---- S1 sieve (single terms) ----
            items1 = [(WP[i], ("P", i)) for i in range(1, B+1)] + [(WQ[j], ("Q", j)) for j in range(1, B+1)]
            cols1 = enumerate_collisions(items1)
            c1 = count_by_fampair(cols1)
            e1 = birthday_expect({"P": B, "Q": B}, p)
            s1 = dict(collisions=len(cols1), by_fampair=c1, expected={"".join(kk): r4(v) for kk, v in e1.items()},
                      enrichment=enrich(c1, e1))

            # ---- S2 sieve (pairwise products) ----
            items2 = []
            for a in range(1, B+1):
                Wa = WP[a]
                for b in range(a, B+1):
                    items2.append((Wa*WP[b] % p, ("PP", a, b)))
            for a in range(1, B+1):
                Ua = WQ[a]
                for b in range(a, B+1):
                    items2.append((Ua*WQ[b] % p, ("QQ", a, b)))
            for a in range(1, B+1):
                Wa = WP[a]
                for b in range(1, B+1):
                    items2.append((Wa*WQ[b] % p, ("PQ", a, b)))
            cols2 = enumerate_collisions(items2)
            c2 = count_by_fampair(cols2)
            M_PP = B*(B+1)//2
            e2 = birthday_expect({"PP": M_PP, "QQ": M_PP, "PQ": B*B}, p)
            s2 = dict(collisions=len(cols2), by_fampair=c2, expected={"".join(kk): r4(v) for kk, v in e2.items()},
                      enrichment=enrich(c2, e2))

            # ---- k-consistency analysis (S1 + S2), with wall guard ----
            if time.time() - T0 > WALL_LIMIT:
                skipped.append(dict(p=p, seed=seed, reason="wall_guard_before_k_analysis"))
                ka1 = ka2 = None
            else:
                ka1 = analyze_collisions(cols1, WP, n, p, k)
                ka2 = analyze_collisions(cols2, WP, n, p, k)

            # ---- negative controls ----
            # NC1: independent curve
            nc1_inst = find_instance(p, seed, 11)
            nc1 = None
            if nc1_inst is not None:
                E2, n2 = nc1_inst["E"], nc1_inst["n"]
                B2 = int(math.ceil(math.sqrt(n2)))
                Rpt = nc1_inst["P"]
                v2, v3, v4 = eds_init_int(E2, Rpt, p)
                WR = eds_extend_int(v2, v3, v4, B2, p)
                it_s = [(WR[j], ("R", j)) for j in range(1, B2+1)]
                cols_nc1_s = [(v, t1, t2) for (v, t1, t2) in enumerate_collisions([(WP[i], ("P", i)) for i in range(1, B+1)] + it_s)
                              if fam(t1) != fam(t2)]
                exp_s = B*B2/float(p)
                it_pp = [(WP[a]*WP[b] % p, ("PP", a, b)) for a in range(1, B+1) for b in range(a, B+1)]
                it_rr = [(WR[c]*WR[d] % p, ("RR", c, d)) for c in range(1, B2+1) for d in range(c, B2+1)]
                cols_nc1_p = [(v, t1, t2) for (v, t1, t2) in enumerate_collisions(it_pp + it_rr)
                              if fam(t1) != fam(t2)]
                M_R = B2*(B2+1)//2
                exp_p = M_PP*M_R/float(p)
                nc1 = dict(n2=n2, B2=B2,
                           singles_cross=len(cols_nc1_s), singles_expected=r4(exp_s),
                           singles_enrichment=r4(len(cols_nc1_s)/exp_s) if exp_s > 0 else None,
                           products_cross=len(cols_nc1_p), products_expected=r4(exp_p),
                           products_enrichment=r4(len(cols_nc1_p)/exp_p) if exp_p > 0 else None)

            # NC2: permuted WQ (k-structure destroyed)
            prng2 = R(seed, p, 12)
            perm = list(range(1, B+1))
            prng2.shuffle(perm)
            WQp = [0] + [WQ[perm[j-1]] for j in range(1, B+1)]
            items2p = []
            for a in range(1, B+1):
                Wa = WP[a]
                for b in range(1, B+1):
                    items2p.append((Wa*WQp[b] % p, ("PQ", a, b)))
            for a in range(1, B+1):
                Ua = WQp[a]
                for b in range(a, B+1):
                    items2p.append((Ua*WQp[b] % p, ("QQ", a, b)))
            cols2p = enumerate_collisions(items2p)
            qcols_main = len([c for c in cols2 if any(fam(t) in ("QQ", "PQ") for t in c[1:])])
            qcols_perm = len([c for c in cols2p if any(fam(t) in ("QQ", "PQ") for t in c[1:])])
            nc2 = dict(qinvolving_collisions_main=qcols_main, qinvolving_collisions_permuted=qcols_perm,
                       ratio=r4(qcols_perm/float(qcols_main)) if qcols_main else None)
            if ka2 is not None and time.time() - T0 <= WALL_LIMIT:
                kap = analyze_collisions(cols2p, WP, n, p, k, assert_k=False)
                nc2.update(permuted_yielding=kap["yielding"], main_yielding=ka2["yielding"],
                           permuted_analyzed=kap["analyzed"], main_analyzed=ka2["analyzed"])

            # NC3: random oracle calibration
            rrng = R(seed, p, 13)
            RP = [0] + [rrng.randrange(1, p) for _ in range(B)]
            RQ = [0] + [rrng.randrange(1, p) for _ in range(B)]
            it3 = []
            for a in range(1, B+1):
                for b in range(a, B+1):
                    it3.append((RP[a]*RP[b] % p, ("PP", a, b)))
                    it3.append((RQ[a]*RQ[b] % p, ("QQ", a, b)))
            for a in range(1, B+1):
                for b in range(1, B+1):
                    it3.append((RP[a]*RQ[b] % p, ("PQ", a, b)))
            cols3 = enumerate_collisions(it3)
            c3 = count_by_fampair(cols3)
            nc3 = dict(collisions=len(cols3), by_fampair=c3, enrichment=enrich(c3, e2))

            # ---- op accounting + recovery arithmetic ----
            oa = op_accounting(n, B, p)
            rec_block = None
            if ka2 is not None:
                checked_opt = 1 if ka2["yielding"] > 0 else ka2["analyzed"]
                ops_opt = oa["ops_fb"] + oa["ops_enum_s2"] + oa["ops_pre"] + checked_opt*oa["ops_verify_per_collision"]
                ops_full = oa["ops_fb"] + oa["ops_enum_s2"] + oa["ops_pre"] + ka2["analyzed"]*oa["ops_verify_per_collision"]
                ln = math.log(n)
                rank_ratio = (ka2["yielding"]/float(ops_full)) / (1.0/oa["bsgs_ops"])
                rec_block = dict(
                    k_recovered=(ka2["yielding"] > 0),
                    yielding_relations=ka2["yielding"],
                    ops_recovery_optimistic=ops_opt, ops_recovery_fullscan=ops_full,
                    exponent_optimistic=r4(math.log(ops_opt)/ln),
                    exponent_fullscan=r4(math.log(ops_full)/ln),
                    bsgs_ops=oa["bsgs_ops"], bsgs_exponent=oa["bsgs_exponent"],
                    rank_per_op_ratio_vs_bsgs=r6(rank_ratio),
                    first_yielding_rank=ka2["first_yielding_rank"])

            results["instances"].append(dict(
                p=p, seed=seed, status="ok",
                curve=dict(a=inst["a"], b=inst["b"], N=N, n=n, h=h, embdeg=emb, curve_search_tries=inst["tries"]),
                k=k, B=B, pc2=pc2, s1=s1, s2=s2,
                k_analysis_s1=ka1, k_analysis_s2=ka2,
                nc1=nc1, nc2=nc2, nc3=nc3,
                op_accounting=oa, recovery=rec_block,
                wall_seconds=r3(time.time() - tinst)))
            log("p=%d seed=%d n=%d B=%d S2cols=%d Qcols=%s yielding=%s" % (
                p, seed, n, B, len(cols2),
                ka2["total_q_collisions"] if ka2 else "skip",
                ka2["yielding"] if ka2 else "skip"))

    if skipped:
        results["deviations"].append("wall guard skipped k-analysis on: %s" % skipped)

    # ---- aggregates per prime ----
    for p in PRIMES:
        sub = [i for i in results["instances"] if i.get("p") == p and i.get("status") == "ok"]
        if not sub:
            continue
        def mean(keyfn):
            vals = [keyfn(i) for i in sub if keyfn(i) is not None]
            return r4(sum(vals)/len(vals)) if vals else None
        agg = dict(
            n_values=[i["curve"]["n"] for i in sub],
            B_values=[i["B"] for i in sub],
            s2_collisions=[i["s2"]["collisions"] for i in sub],
            s2_enrichment_PQPQ=mean(lambda i: i["s2"]["enrichment"].get("PQPQ")),
            s2_enrichment_overall=mean(lambda i: (sum(i["s2"]["by_fampair"].values())/sum(i["s2"]["expected"].values())) if sum(i["s2"]["expected"].values()) > 0 else None),
            s1_enrichment_overall=mean(lambda i: (sum(i["s1"]["by_fampair"].values())/sum(i["s1"]["expected"].values())) if sum(i["s1"]["expected"].values()) > 0 else None),
            yielding_total=sum(i["k_analysis_s2"]["yielding"] for i in sub if i["k_analysis_s2"]),
            analyzed_total=sum(i["k_analysis_s2"]["analyzed"] for i in sub if i["k_analysis_s2"]),
            universal_total=sum(i["k_analysis_s2"]["universal"] for i in sub if i["k_analysis_s2"]),
            k_recovered_count=sum(1 for i in sub if i["recovery"] and i["recovery"]["k_recovered"]),
            exponent_optimistic=mean(lambda i: i["recovery"]["exponent_optimistic"] if i["recovery"] else None),
            exponent_fullscan=mean(lambda i: i["recovery"]["exponent_fullscan"] if i["recovery"] else None),
            bsgs_exponent=mean(lambda i: i["recovery"]["bsgs_exponent"] if i["recovery"] else None),
            rank_per_op_ratio_vs_bsgs=mean(lambda i: i["recovery"]["rank_per_op_ratio_vs_bsgs"] if i["recovery"] else None),
            nc1_products_enrichment=mean(lambda i: i["nc1"]["products_enrichment"] if i["nc1"] else None),
            nc2_permuted_yielding=sum(i["nc2"].get("permuted_yielding", 0) for i in sub),
            nc3_enrichment_overall=mean(lambda i: (sum(i["nc3"]["by_fampair"].values())/sum(i["s2"]["expected"].values())) if sum(i["s2"]["expected"].values()) > 0 else None),
        )
        results["aggregates"][str(p)] = agg

    # ---- validity self-check ----
    pc1_pass = all(r.get("passed") for r in pc1)
    nc1_enr = [results["aggregates"][str(p)]["nc1_products_enrichment"] for p in PRIMES if str(p) in results["aggregates"]]
    nc3_enr = [results["aggregates"][str(p)]["nc3_enrichment_overall"] for p in PRIMES if str(p) in results["aggregates"]]
    results["validity_selfcheck"] = dict(
        pc1_all_pass=pc1_pass, pc2_all_pass=pc2_all, k_in_S_assertions="passed (RuntimeError not raised)",
        nc1_products_enrichment_per_size=nc1_enr, nc3_enrichment_per_size=nc3_enr)

    results["timestamps"]["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    results["timestamps"]["wall_seconds"] = r3(time.time() - T0)

    def J(o):
        from sage.rings.integer import Integer as SInt
        from sage.rings.rational import Rational as SRat
        if isinstance(o, dict):   return {str(k): J(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [J(v) for v in o]
        if isinstance(o, (bool, str, int, float)) or o is None: return o
        if isinstance(o, SInt): return int(o)
        if isinstance(o, SRat): return float(o)
        try: return int(o)
        except Exception:
            try: return float(o)
            except Exception: return str(o)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(J(results), f, indent=1)
    log("wrote %s (wall %.1fs)" % (OUT, time.time() - T0))

main()
