#!/usr/bin/env python3
"""c1_model.py -- zero-experiment cost model "C1".

Question: does Gaudry/Diem fixed-n=4 index calculus with the Gaudry-Thome-
Theriault-Diem double-large-prime (2LP) variant and a pi_16-Frobenius-orbit
factor base beat rho on the five ANSI X9.62 c2pnb rows
(c2pnb176v1, 208w1, 272w1, 304w1, 368w1) under
  (i)   time only,
  (ii)  the program's time x memory convention (EV-SEMBIN-4125ec /
        HEUR-VOW-CURVE: vOW charged at its own T x Mem minimum 6 n W),
  (iii) area-time: (iii-a) the program's machine model MM-1
        (EXP-BINSTD-f442a9), (iii-b) a Bernstein-style mesh AT model.

Scripted arithmetic only. Deterministic, Python 3 stdlib only, no I/O except
stdout (and, with --verify-repo PATH, read-only re-parsing of four repository
files to confirm the embedded constants). Runs in a few seconds.

Units. Time: rho steps (one Pollard-rho iteration on E(F_{2^{16k}})).
MM-1 is defined in bit operations; both of its arms are divided by the same
t_iter = 10 (16k)^2 bit ops (MM-1 rho_arm), so ratios are unchanged.
Memory: bits. Area: processor-equivalents (1 rho processor = RHO_AREA bits).
All outputs are log2. "margin" = baseline_bits - C1_bits; POSITIVE = C1 better.

Provenance tags used below:
  [cite path:line]   read in this session in the repository
  [brief]            supplied by the task brief (red-team estimate), not
                     verified against a primary source in this session
  [recalled-unverified]  from memory, not opened in this session
  [model]            a modelling choice made here, exposed as a parameter
"""
import math
import sys

LOG2 = math.log2
INF = float("inf")


def l2add(*xs):
    """log2(sum 2^x), ignoring -inf terms."""
    xs = [x for x in xs if x != -INF]
    if not xs:
        return -INF
    m = max(xs)
    return m + LOG2(sum(2.0 ** (x - m) for x in xs))


def golden_min(f, a, b, iters=90):
    """Minimise a unimodal f on [a, b]; returns (fmin, xmin)."""
    g = (math.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(iters):
        if fc <= fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    x = (a + b) / 2
    cands = [(f(x), x), (f(a), a), (f(b), b)]
    return min(cands)


def grid_min(f, a, b, step=0.05):
    best = (INF, None)
    x = a
    while x <= b + 1e-12:
        v = f(x)
        if v < best[0]:
            best = (v, x)
        x += step
    return best


# =============================================================================
# 1. Program conventions, embedded with citations and re-derived
# =============================================================================
REPO_CITES = {
    "t_h": "analysis/binstd-curve-audit/audit-certificate.txt:1-15 (t, cofactor)",
    "r": "experiments/EXP-BINSTD-9d1b8e/stage0/five-row-symmetry-certificate.yaml:17,52,87,122,157 (r_from_dump)",
    "rho_formula": "experiments/EXP-BINSTD-9d1b8e/specification.yaml:77-81,246-248 (corrected_rho = log2 sqrt(pi r/(4k)))",
    "rho_frozen": "ledger/evidence/EV-BINSTD-f541ea.yaml:91-95 (O-stage0: within +-0.01 of frozen [78.10,93.98,125.78,141.71,173.57])",
    "vow": "ledger/evidence/EV-SEMBIN-4125ec.yaml:80-87 (HEUR-VOW-CURVE T=W(1/M+1/w), Mem=3n max(w,M), W=0.886 2^{n/2}; T x Mem = 6nW on w=M)",
    "vow_json": "experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/arm-b-coherent-baseline.json:1569-1600 (own_curve_min_product_log2)",
    "vow_record_pt": "ledger/evidence/EV-SEMBIN-4125ec.yaml:180-183 (T_v = 204.33, Mem_v = 40.26 at n=409 record point)",
    "vow_src": "knowledge/literature/KN-LIT-73f7e1.md:103-114,133-147 (0.886 = sqrt(pi/4) includes negation; 3n bits/DP upper bound)",
    "mm1": "experiments/EXP-BINSTD-f442a9/specification.yaml:579-605,621-623 (MM-1: FC=(P+mem/RHO_AREA)*wall per phase; RHO_AREA=2^16; P_REF=2^20; rho 10 N^2 bitops/iter, P*2^10 DPs at 3 log2 l bits; Wiedemann D^2(3w log2 l + 7 (log2 l)^2); LA memory D(w(log2 D+1)+4 log2 l); P_LA_MAX=2^10)",
    "mm1_grid": "experiments/EXP-BINSTD-f442a9/specification.yaml:359 (P in {2^10,2^20,2^30}, RHO_AREA in {2^10,2^16,2^22})",
    "holdd": "analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-6cf862.yaml:56-69 (product-law floor min_l m! 2^(N-(m-1)l) + m 2^(2l); orbit variant relations/k, LA/k^2)",
    "kn_open": "knowledge/open-problems/KN-OPEN-86e7e1.md:130-148 (explicit metric; compare against vOW parallel rho incl. DP storage)",
}

# name, k, trace t over F_{2^16}, cofactor h, r (decimal), frozen rho bits
ROWS = [
    ("c2pnb176v1", 11, 147, 65390,
     "1464764815784035076424479112383122688505483765421", 78.10),
    ("c2pnb208w1", 13, 441, 65096,
     "6319530221984476934661765632900719012846431750114578083741", 93.98),
    ("c2pnb272w1", 17, 251, 65286,
     "116235492452543488393823301680748870034491124166583946466668991869818652235041", 125.78),
    ("c2pnb304w1", 19, 467, 65070,
     "500884825900595933307132795674658837818095809137913478977332553047879960661308247049501", 141.71),
    ("c2pnb368w1", 23, 145, 65392,
     "9194196556002283250851893699199753471497656173851998515361706855000304737080699826013007012009780734318951", 173.57),
]
Q0 = 2 ** 16  # coefficient field F_{2^16}


def weil_order(t, q, k):
    """#E(F_{q^k}) from the trace t of E/F_q (s_0=2, s_1=t, s_{i+1}=t s_i - q s_{i-1})."""
    s_prev, s_cur = 2, t
    for _ in range(k - 1):
        s_prev, s_cur = s_cur, t * s_cur - q * s_prev
    return q ** k + 1 - s_cur


def rho_bits(r, k):
    """Program convention (CORR-20260922-81aeab): log2 sqrt(pi r / (4k))."""
    return 0.5 * (LOG2(math.pi) + LOG2(r) - LOG2(4 * k))


def vow_minprod_bits(nbits, W_bits):
    """HEUR-VOW-CURVE: on the ray w = M, T = 2W/M, Mem = 3 n M -> T*Mem = 6 n W."""
    return LOG2(6 * nbits) + W_bits


def reproduce_program_numbers():
    out = []
    ok = True
    derived = []
    for name, k, t, h, r_s, frozen in ROWS:
        r_dump = int(r_s)
        Nk = weil_order(t, Q0, k)
        assert h == Q0 + 1 - t, name
        assert Nk % h == 0, name
        r = Nk // h
        assert r == r_dump, name
        assert math.gcd(h, r) == 1, name
        rb = rho_bits(r, k)
        d = abs(rb - frozen)
        ok &= d <= 0.05
        out.append((f"rho {name}", f"{rb:.4f}", f"{frozen:.2f}", f"{d:.4f}", d <= 0.05))
        derived.append(dict(name=name, k=k, t=t, h=h, r=r, rho=rb))
    # vOW own-curve product minimum, arm-b JSON lines 1569-1600 (n = FIPS label)
    arm_b = {163: 91.2591, 233: 126.7745, 283: 152.055, 409: 215.5863, 571: 297.0677}
    for n, v in arm_b.items():
        mine = vow_minprod_bits(n, LOG2(0.886) + n / 2)
        d = abs(mine - v)
        ok &= d <= 0.05
        out.append((f"vOW 6nW n={n}", f"{mine:.4f}", f"{v:.4f}", f"{d:.5f}", d <= 0.05))
        rec = mine + 29.0  # record point M=1, w=2^30: excess 30-1 = 29.0 bits (O-3)
        recj = v + 29.0
        out.append((f"vOW record-pt n={n}", f"{rec:.4f}", f"{recj:.4f}", f"{abs(rec-recj):.5f}", True))
    # record point at n = 409: T_v = W/M = W, Mem_v = 3 n 2^30 (EV-SEMBIN-4125ec:182)
    Tv = LOG2(0.886) + 409 / 2
    Mv = LOG2(3 * 409) + 30
    for lab, mine, ref in (("vOW T_v n=409", Tv, 204.33), ("vOW Mem_v n=409", Mv, 40.26)):
        d = abs(mine - ref)
        ok &= d <= 0.05
        out.append((lab, f"{mine:.4f}", f"{ref:.2f}", f"{d:.4f}", d <= 0.05))
    # HOLD-D product-law floors (IDEA-20260922-6cf862.yaml:59-66), N = 16(k-1)
    holdd = {(160, 3): (83.1, 77.9), (160, 4): (68.0, 62.5), (160, 5): (58.1, 52.3),
             (192, 3): (99.1, 93.5), (192, 4): (80.8, 74.9), (192, 5): (68.8, 62.6),
             (192, 6): (60.3, 53.9), (256, 4): (106.4, 99.9), (256, 5): (90.1, 83.3)}
    kof = {160: 11, 192: 13, 256: 17}
    for (N, m), (ref_plain, ref_orb) in holdd.items():
        kk = kof[N]
        fp = holdd_floor(N, m, 1)
        fo = holdd_floor(N, m, kk)
        d1, d2 = abs(fp - ref_plain), abs(fo - ref_orb)
        ok &= d1 <= 0.05 and d2 <= 0.05
        out.append((f"HOLD-D floor N={N} m={m}", f"{fp:.2f}/{fo:.2f}",
                    f"{ref_plain}/{ref_orb}", f"{max(d1, d2):.3f}", d1 <= 0.05 and d2 <= 0.05))
    return ok, out, derived


def holdd_floor(N, m, korb):
    """min over real l of m! 2^(N-(m-1)l)/korb + m 2^(2l)/korb^2 (HOLD-D convention)."""
    f = lambda l: l2add(LOG2(math.factorial(m)) + N - (m - 1) * l - LOG2(korb),
                        LOG2(m) + 2 * l - 2 * LOG2(korb))
    return golden_min(f, 0.0, float(N))[0]


# =============================================================================
# 2. The C1 model
# =============================================================================
# Every parameter, its default and its provenance.
DEFAULTS = dict(
    n=4,               # Weil-descent degree: F_{2^{16k}} = F_{Q^4}, Q = 2^{4k} [brief]
    p_dec=1.0 / 24,    # H0: decomposition probability per trial = 1/n! [heuristic H0]
    kappa=1.0,         # H2: edges needed = kappa * N/2 (percolation constant) [heuristic H2]
    c_trial=2.0 ** 30, # per-trial decomposition cost, rho-step units [brief band 2^27..2^32.5]
    c_gen=1.0,         # cost to generate the next target aP+bQ (one group op) [model]
    B=3.0,             # Wiedemann passes: 3 s matrix-vector products [MM-1 shape, recalled-unverified constant]
    w=8.0,             # H3: row weight after 2LP path combination [heuristic H3]
    coef="orbit",      # 'orbit': Frobenius-twisted coefficients mu^j -> one Z/r mult per nonzero
                       # 'small': MM-1 literal (one log2 l addition per nonzero)
                       # 'pess' : B rho steps per nonzero
    D=4096,            # FGLM dimension 2^{n(n-1)} [brief; Bezout bound for n=4, recalled-unverified]
    fb_factor=1.0,     # multiplier on the factor-base orbit count N (H1 realisation) [model]
    orbit=True,        # pi_16 x negation orbits of size 2k; False -> negation only
    RHO_AREA=2.0 ** 16,# bits per processor-equivalent [cite mm1]
    P_MM1=2.0 ** 20,   # MM-1 reference processor count [cite mm1]
    P_LA_MAX=2.0 ** 10,# MM-1 LA node cap [cite mm1]
    DP_PER_PROC=2.0 ** 10,  # MM-1 rho table holds P*2^10 DPs [cite mm1]
    RHO_MULTS=10.0,    # MM-1 rho iteration = 10 F_{2^N} mults = 10 N^2 bitops [cite mm1]
    c_route=1.0,       # mesh: routing steps per matvec = c_route * sqrt(cells) [model, recalled-unverified]
    P_MESH_MAX=2.0 ** 40,  # mesh / SEMBIN processor ceiling [cite EV-SEMBIN-4125ec processors_log2 grid {0,20,40}]
    lp="2LP",          # '2LP' (GTTD), '1LP' (Theriault-type, q^{14/9}), 'none' (basic Gaudry)
    LA_mult=1.0,       # sensitivity multiplier on the LA constant (1 = no change) [model]
    vow_bits_mode="3n",# vOW bits per DP: '3n' (HEUR-VOW-CURVE, n = 16k) or '3L' (MM-1, 3 log2 r)
)

RHO_STEP_FQ_MULTS = (45.0, 54.0)  # [brief] 1 rho step ~ 45-54 F_Q mults (F_Q = F_{2^{4k}})
ROOT_FLOOR_FQ_OPS = 2.0 ** 21     # [brief] root-extraction floor per trial, F_Q ops


def c_trial_band():
    lo_m, hi_m = RHO_STEP_FQ_MULTS
    floor = (LOG2(ROOT_FLOOR_FQ_OPS / hi_m), LOG2(ROOT_FLOOR_FQ_OPS / lo_m))
    fglm_ops = DEFAULTS["n"] * DEFAULTS["D"] ** 3  # n D^3 F_Q ops (dense FGLM)
    fglm = (LOG2(fglm_ops / hi_m), LOG2(fglm_ops / lo_m))
    return floor, fglm, LOG2(fglm_ops)


class Row:
    def __init__(self, d, prm):
        self.name, self.k, self.r, self.rho = d["name"], d["k"], d["r"], d["rho"]
        self.prm = prm
        k = self.k
        self.nf = 16 * k                    # field bits of F_{2^{16k}}
        self.L = LOG2(self.r)               # log2 r
        self.Qb = 4 * k                     # log2 Q, Q = 2^{4k}
        osz = 2 * k if prm["orbit"] else 2  # orbit size (x in F_{2^4}: 16 x-values, negligible)
        self.osz = osz
        # #factor-base points ~ Q (about half of x in F_Q give 2 points); N orbits ~ Q/osz
        self.logN = self.Qb - LOG2(osz) + LOG2(prm["fb_factor"])
        self.t_rho_bitops = prm["RHO_MULTS"] * self.nf ** 2
        L = self.L
        coef = prm["coef"]
        if coef == "orbit":
            per_s2 = prm["B"] * prm["w"] * L * L + 7 * L * L
            self.LAc = LOG2(per_s2 / self.t_rho_bitops)
        elif coef == "small":
            per_s2 = prm["B"] * prm["w"] * L + 7 * L * L
            self.LAc = LOG2(per_s2 / self.t_rho_bitops)
        elif coef == "pess":
            self.LAc = LOG2(prm["B"] * prm["w"])
        else:
            raise ValueError(coef)
        self.LAc += LOG2(prm["LA_mult"])  # sensitivity multiplier (1 by default)
        self.u_mul = LOG2(L * L / self.t_rho_bitops)    # one Z/r mult, rho units
        self.ws = LOG2(prm["D"] ** 2 * self.Qb)           # model (c): D^2 F_Q elements, bits
        self.W = self.rho                                  # rho iterations (program convention)

    # ---- trial counts --------------------------------------------------------
    # 2LP derivation. Factor base F of N orbits; small primes S of size s, the
    # rest "large". A trial decomposes with probability p (H0) into n = 4
    # factor-base orbits, each small with probability s/N (H1: uniform). The
    # probability that EXACTLY two of four are large is C(4,2)(s/N)^2(1-s/N)^2
    # ~ 6 (s/N)^2 for s << N, so a trial yields a 2LP edge with probability
    # 6 p (s/N)^2 (the code uses the exact C(4,2) x^2 (1-x)^2, x = s/N, and
    # N - s large vertices). The large primes form a random graph on N vertices; the
    # cycle space becomes linear in N once the edge count passes the
    # percolation threshold N/2 (average degree 1); kappa*N/2 edges are
    # assumed to yield >= s independent small-prime relations (H2; near the
    # threshold the giant component's excess grows like ~(2/3) eps^3 N for
    # kappa = 1+eps, so kappa slightly above 1 suffices when s << N --
    # recalled-unverified random-graph fact; constant flagged). Hence
    #   trials_2LP(s) = kappa (N/2) / (6 p (s/N)^2) = kappa N^3 / (12 p s^2).
    # Time(s) = trials(s) (c_trial + c_gen) + LAc s^2; d/ds = 0 gives
    #   s*^4 = kappa N^3 c / (12 p LAc),  T* = 2 sqrt(kappa N^3 c LAc / (12 p))
    # i.e. T* ~ N^{3/2} = (Q/2k)^{3/2} = Q^{2-2/n} at n = 4 (GTTD exponent).
    # The s/3 one-large-prime and s^2/(12N) full relations produced on the way
    # are ignored (slightly pessimistic for C1).
    def log_trials(self, x):  # x = log2 s
        p = self.prm
        lN = self.logN
        lx = x - lN                      # log2 (s/N)
        l1mx = LOG2(max(1.0 - 2.0 ** lx, 1e-300))  # log2 (1 - s/N)
        lNs = lN + l1mx                  # log2 (N - s): number of large-prime vertices
        if p["lp"] == "2LP":
            # exact: rate = C(4,2) p x^2 (1-x)^2, edges = kappa (N - s)/2
            return LOG2(p["kappa"]) + lNs - 1 - LOG2(6 * p["p_dec"]) - 2 * lx - 2 * l1mx
        if p["lp"] == "1LP":
            # one large prime: rate 4 p x^3 (1-x); R such relations give R^2/(2(N-s))
            # matches; need s: R = sqrt(2 (N-s) s). For s << N:
            # trials = sqrt(2Ns) N^3/(4 p s^3) -> optimum s ~ N^{7/9}, cost ~ N^{14/9}.
            return 0.5 * (1 + lNs + x) - LOG2(4 * p["p_dec"]) - 3 * lx - l1mx
        if p["lp"] == "none":
            # basic Gaudry: s = N, need ~N relations, 1/p trials each
            return lN - LOG2(p["p_dec"])
        raise ValueError(p["lp"])

    def analytic_time(self):
        """s << N closed form: s*^4 = kappa N^3 c / (12 p LAc); T* = 2 sqrt(kappa N^3 c LAc / (12 p))."""
        p = self.prm
        c = LOG2(p["c_trial"] + p["c_gen"])
        core = LOG2(p["kappa"]) + 3 * self.logN + c - LOG2(12 * p["p_dec"])
        return 1 + 0.5 * (core + self.LAc), (core - self.LAc) / 4

    def log_RC(self, x):
        c = self.prm["c_trial"] + self.prm["c_gen"]
        if c <= 0:
            return -INF
        return self.log_trials(x) + LOG2(c)

    def log_LA(self, x):
        return self.LAc + 2 * x

    def log_time(self, x):
        return l2add(self.log_RC(x), self.log_LA(x))

    # ---- memory models ------------------------------------------------------
    def idx_bits(self, x):
        return x + LOG2(self.osz)  # small-orbit index + Frobenius exponent/sign

    def mem_a(self, x):
        """(a) relation store minimum = s rows: s (w idx + 4 log2 r) bits (MM-1 LA-memory form)."""
        return x + LOG2(self.prm["w"] * self.idx_bits(x) + 4 * self.L)

    def mem_b(self, x):
        """(b) graph store ~ kappa N/2 edges, each 2 large + 2 small entries; peak with (a)."""
        edge = 2 * (self.logN + LOG2(self.osz)) + 2 * self.idx_bits(x)
        g = LOG2(self.prm["kappa"]) + self.logN - 1 + LOG2(edge)
        return max(g, self.mem_a(x))

    def mem(self, x, model):
        return self.mem_a(x) if model == "a" else self.mem_b(x)

    def xrange(self):
        return 0.0, self.logN - 1e-3

    # ---- metrics: return (C1 bits, baseline bits, aux) ----------------------
    def opt(self, f):
        a, b = self.xrange()
        if self.prm["lp"] == "none":
            return f(self.logN), self.logN
        return golden_min(f, a, b)

    def m_time(self):
        v, x = self.opt(self.log_time)
        return v, self.W, x

    def m_tmem_f(self, model, plog2):
        """SEMBIN convention (EV-SEMBIN-4125ec O-1/O-3; RUN-SEMBIN-3ae91c implementation.md:9):
        parallel IC wall time = time - p, memory = log2add(store, ws + p); product T x Mem."""
        def f(x):
            return (self.log_time(x) - plog2) + l2add(self.mem(x, model), self.ws + plog2)
        return f

    def m_tmem(self, model, plog2):
        v, x = self.opt(self.m_tmem_f(model, plog2))
        nb = self.nf if self.prm["vow_bits_mode"] == "3n" else self.L
        return v, vow_minprod_bits(nb, self.W), x  # baseline: vOW own-curve minimum 6 n W

    def m_mm1_f(self, model):
        """MM-1 full cost FC = sum over phases (P + mem/RHO_AREA) * wall (P charged in every phase)."""
        p = self.prm
        P, RA = LOG2(p["P_MM1"]), LOG2(p["RHO_AREA"])
        PLA = min(P, LOG2(p["P_LA_MAX"]))

        def f(x):
            rc_wall = self.log_RC(x) - P
            rc_mem = l2add(self.mem(x, model), self.ws + P)
            fc_rc = l2add(P, rc_mem - RA) + rc_wall
            la_wall = self.log_LA(x) - PLA
            fc_la = l2add(P, self.mem_a(x) - RA) + la_wall
            return l2add(fc_rc, fc_la)
        return f

    def m_mm1(self, model):
        p = self.prm
        P, RA = LOG2(p["P_MM1"]), LOG2(p["RHO_AREA"])
        v, x = self.opt(self.m_mm1_f(model))
        # rho arm (MM-1 literal): (P + P 2^10 3L / RA) (W/P + 1/theta), theta W = P 2^10
        dp = LOG2(p["DP_PER_PROC"])
        base = l2add(P, P + dp + LOG2(3 * self.L) - RA) + l2add(self.W - P, self.W - P - dp)
        return v, base, x

    def m_mesh_f(self, model):
        """Bernstein-style mesh area-time. Area in processor-equivalents, time in rho steps.
        RC: each worker = 1 processor + per-worker FGLM state ws (model c); the store sits
        in memory for RC/P_w with P_w = min(P_MESH_MAX, trials) workers. LA: mesh with one
        cell per nonzero / vector entry, area cells*cell_bits/RA, time
        B s c_route sqrt(cells) u_mul (one Z/r mult per routing step)."""
        p = self.prm
        RA = LOG2(p["RHO_AREA"])
        Pw = LOG2(p["P_MESH_MAX"])

        def f(x):
            rc = self.log_RC(x)
            at_rc = l2add(rc + l2add(0.0, self.ws - RA),
                          self.mem(x, model) - RA + rc - min(Pw, self.log_trials(x)))
            cells = l2add(x + LOG2(p["w"]), x + 2)
            cell_bits = LOG2(self.idx_bits(x) + self.L)
            area = cells + cell_bits - RA
            tla = (LOG2(p["B"]) + x + LOG2(p["c_route"]) + 0.5 * cells + self.u_mul
                   + LOG2(p["LA_mult"]))
            return l2add(at_rc, area + tla)
        return f

    def m_mesh(self, model):
        p = self.prm
        v, x = self.opt(self.m_mesh_f(model))
        a = 3 * self.L / p["RHO_AREA"]
        # rho: min over theta of (P + W theta 3L/RA)(W/P + 1/theta) = W (1 + a + 2 sqrt(a))
        base = self.W + LOG2(1 + a + 2 * math.sqrt(a))
        return v, base, x


METRICS = [
    ("time", "(i) time only vs rho", lambda R: R.m_time()),
    ("TxM-a-p0", "(ii) TxMem, mem (a), p=0 vs vOW 6nW", lambda R: R.m_tmem("a", 0)),
    ("TxM-b-p0", "(ii) TxMem, mem (b), p=0 vs vOW 6nW", lambda R: R.m_tmem("b", 0)),
    ("TxM-a-best", "(ii) TxMem, mem (a), best p in {0,20,40}", None),
    ("TxM-b-best", "(ii) TxMem, mem (b), best p in {0,20,40}", None),
    ("MM1-a", "(iii-a) MM-1 full cost, mem (a)", lambda R: R.m_mm1("a")),
    ("MM1-b", "(iii-a) MM-1 full cost, mem (b)", lambda R: R.m_mm1("b")),
    ("mesh-a", "(iii-b) mesh area-time, mem (a)", lambda R: R.m_mesh("a")),
    ("mesh-b", "(iii-b) mesh area-time, mem (b)", lambda R: R.m_mesh("b")),
]


def eval_metric(key, R):
    if key in ("TxM-a-best", "TxM-b-best"):
        model = key[4]
        res = [R.m_tmem(model, p) + (p,) for p in (0, 20, 40)]
        best = min(res, key=lambda t: t[0] - t[1])
        return best[0], best[1], best[2]
    fn = dict((m[0], m[2]) for m in METRICS)[key]
    return fn(R)


def margin(key, d, prm):
    R = Row(d, prm)
    c, b, _ = eval_metric(key, R)
    return b - c


def with_(prm, **kw):
    q = dict(prm)
    q.update(kw)
    return q


# =============================================================================
# 3. Driver
# =============================================================================
def fmt(x, nd=2):
    if x == INF:
        return "inf"
    if x == -INF:
        return "-inf"
    return f"{x:.{nd}f}"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def breakeven_ctrial(key, d, prm):
    """log2 c_trial at which margin = 0 (margin decreases in c_trial)."""
    m0 = margin(key, d, with_(prm, c_trial=0.0))
    if m0 < 0:
        return None, m0  # loses even with a free oracle
    lo, hi = -10.0, 200.0
    if margin(key, d, with_(prm, c_trial=2.0 ** hi)) > 0:
        return INF, m0
    for _ in range(70):
        mid = (lo + hi) / 2
        if margin(key, d, with_(prm, c_trial=2.0 ** mid)) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2, m0


# single-parameter perturbations: name -> (function(prm, delta_log2) -> prm, plausible log2 range)
def _scale(name):
    return lambda prm, dl: with_(prm, **{name: prm[name] * 2.0 ** dl})


PERTURB = [
    ("c_trial", _scale("c_trial"), (27 - 30, 32.5 - 30), "brief band 2^27..2^32.5 (floor 2^15.5 separate)"),
    ("p_dec", _scale("p_dec"), (-1.0, 1.0), "H0: 1/24 within x2 either way"),
    ("kappa", _scale("kappa"), (0.0, 2.0), "H2: kappa in [1, 4]"),
    ("LA_unit", None, None, "H3: coef small .. pess (row-specific range)"),
    ("D_fglm", _scale("D"), (-2.0, 0.0), "H3: FGLM state D in [2^10, 2^12] (ws = D^2 F_Q elts)"),
    ("RHO_AREA", _scale("RHO_AREA"), (-6.0, 6.0), "MM-1 grid 2^10..2^22"),
    ("N_orbits", _scale("fb_factor"), (0.0, 1.0), "H1: orbit count N x[1,2] (partial orbit gain)"),
    ("P_MM1", _scale("P_MM1"), (-10.0, 10.0), "MM-1 grid P in 2^10..2^30"),
]


def la_unit_perturb(prm, dl):
    # scales the whole LA constant per s^2 (B, w, coefficient-op cost together) via LA_mult
    return with_(prm, LA_mult=prm["LA_mult"] * 2.0 ** dl)


def la_unit_range(d, prm):
    lo = Row(d, with_(prm, coef="small")).LAc
    hi = Row(d, with_(prm, coef="pess")).LAc
    c = Row(d, prm).LAc
    return lo - c, hi - c


def flip_point(key, d, prm, fn):
    """Smallest |delta log2| in [-80, 80] at which the margin sign flips (outward scan + bisection)."""
    m0 = margin(key, d, prm)
    s0 = m0 > 0
    best = None
    for direction in (+1, -1):
        prev = 0.0
        step = 0.5
        x = 0.0
        found = None
        while abs(x) < 80:
            x = prev + direction * step
            try:
                mx = margin(key, d, fn(prm, x))
            except (ValueError, OverflowError, ZeroDivisionError):
                break
            if (mx > 0) != s0:
                lo, hi = prev, x
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if (margin(key, d, fn(prm, mid)) > 0) == s0:
                        lo = mid
                    else:
                        hi = mid
                found = (lo + hi) / 2
                break
            prev = x
            step = min(step * 1.5, 8.0)
        if found is not None and (best is None or abs(found) < abs(best)):
            best = found
    return best


def elasticity(key, d, prm, fn, h=0.25):
    return (margin(key, d, fn(prm, h)) - margin(key, d, fn(prm, -h))) / (2 * h)


def main(argv):
    if "--verify-repo" in argv:
        verify_repo(argv[argv.index("--verify-repo") + 1])
    ok, repro, derived = reproduce_program_numbers()
    print("## T0. Reproduction of the program's numbers (assert |diff| <= 0.05 bit)\n")
    print(table(["quantity", "this script", "program record", "|diff|", "pass"], repro))
    assert ok, "reproduction failed"
    print("\nALL REPRODUCTION ASSERTIONS PASSED\n")

    fl, fg, fglm_ops = c_trial_band()
    print("## T1. c_trial band (rho-step units)\n")
    print(table(["source", "log2 c_trial", "provenance"], [
        ("root-extraction floor 2^21 F_Q ops / (45..54)", f"{fl[0]:.2f} .. {fl[1]:.2f}", "brief; used as 'floor' = 2^15.5"),
        (f"dense FGLM n D^3 = 2^{fglm_ops:.0f} F_Q ops / (45..54)", f"{fg[0]:.2f} .. {fg[1]:.2f}", "brief; band top 2^32.5"),
        ("Granger Asiacrypt 2010, 247 s per char-2 n=4 decomposition (Magma)", "27 .. 32.5, central 30", "brief red-team estimate; NOT in KN-LIT-41fe5c (abstract only); unverified"),
    ]))

    prm = dict(DEFAULTS)
    CT = [("floor", 2.0 ** 15.5), ("2^27", 2.0 ** 27), ("2^30", 2.0 ** 30), ("2^32.5", 2.0 ** 32.5)]

    print("\n## T2. Per-row derived quantities (defaults)\n")
    rows = []
    for d in derived:
        R = Row(d, prm)
        Rp = Row(d, with_(prm, orbit=False, coef="small"))
        rows.append((d["name"], d["k"], R.Qb, fmt(R.logN), fmt(Rp.logN), fmt(R.L), fmt(R.W),
                     fmt(vow_minprod_bits(R.nf, R.W)), fmt(vow_minprod_bits(R.L, R.W)),
                     fmt(R.m_mm1("a")[1]), fmt(R.m_mesh("a")[1]), fmt(R.LAc), fmt(R.ws)))
    print(table(["row", "k", "log2 Q", "log2 N (orbit)", "log2 N (plain)", "log2 r", "rho W",
                 "vOW 6nW (n=16k)", "vOW 6LW (3 log2 r/DP)", "MM-1 rho FC", "mesh rho AT",
                 "log2 LA const/s^2", "log2 ws bits (c)"], rows))

    print("\n## T2b. Optimal s, time only, c_trial = 2^30: analytic (s << N) vs numeric (exact 2LP rates)\n")
    rows = []
    for d in derived:
        R = Row(d, prm)
        Ta, xa = R.analytic_time()
        Tn, Wb, xn = R.m_time()
        rows.append((d["name"], fmt(xa), fmt(xn), fmt(xn - R.logN), fmt(Ta), fmt(Tn), fmt(Tn - Ta)))
    print(table(["row", "log2 s* analytic", "log2 s* numeric", "log2 (s*/N)", "T* analytic",
                 "T* numeric", "numeric - analytic"], rows))
    # unimodality check: golden-section optimum equals a 0.05-step grid optimum
    worst = 0.0
    for d in derived:
        for c in (2.0 ** 15.5, 2.0 ** 30, 0.0):
            R = Row(d, with_(prm, c_trial=c))
            fs = [R.log_time, lambda x, R=R: R.m_tmem_f("a", 0)(x), lambda x, R=R: R.m_tmem_f("b", 40)(x),
                  R.m_mm1_f("a"), R.m_mm1_f("b"), R.m_mesh_f("a"), R.m_mesh_f("b")]
            for f in fs:
                g = golden_min(f, *R.xrange())[0]
                gr = grid_min(f, *R.xrange(), step=0.05)[0]
                worst = max(worst, g - gr)
    assert worst < 1e-3, worst
    print(f"\nOptimiser check: golden-section minus 0.05-grid minimum, worst case over rows x c_trial x"
          f" metrics = {worst:.2e} bits (assert < 1e-3)")

    # ---- main tables -------------------------------------------------------
    all_results = {}
    for key, title, _ in METRICS:
        print(f"\n## T3[{key}]. {title}: C1 bits / baseline bits / margin (+ = C1 better)\n")
        hdr = ["row", "baseline"]
        for lab, _ in CT:
            hdr += [f"C1 @{lab}", f"margin @{lab}"]
        hdr += ["C1 free-oracle (c_trial=0)", "margin free", "log2 s* @2^30"]
        rows = []
        for d in derived:
            line = [d["name"]]
            base = None
            for lab, c in CT:
                R = Row(d, with_(prm, c_trial=c))
                v, b, *aux = eval_metric(key, R)
                base = b
                line += [fmt(v), fmt(b - v)]
                all_results[(key, d["name"], lab)] = (v, b, b - v)
            R = Row(d, with_(prm, c_trial=0.0))
            vf, bf, *_ = eval_metric(key, R)
            all_results[(key, d["name"], "free")] = (vf, bf, bf - vf)
            Rc = Row(d, prm)
            res = eval_metric(key, Rc)
            line.insert(1, fmt(base))
            line += [fmt(vf), fmt(bf - vf), fmt(res[2]) + (f" (p={res[3]})" if len(res) > 3 else "")]
            rows.append(line)
        print(table(hdr, rows))

    # ---- degenerate LA-only floor -----------------------------------------
    print("\n## T4. Degenerate floor with c_trial = c_gen = 0 (graph bookkeeping only)\n")
    rows = []
    for d in derived:
        R = Row(d, prm)
        rows.append((d["name"], fmt(LOG2(prm["kappa"]) + R.logN - 1), fmt(R.W),
                     fmt(R.W - (LOG2(prm["kappa"]) + R.logN - 1))))
    print(table(["row", "log2 (kappa N/2) edge insertions", "rho", "margin"], rows))
    print("\n(With trials free AND target generation free, s -> 1 and the only cost left is touching"
          " ~N/2 edges; this is a degenerate bound, not an attack. The 'free-oracle' columns above keep"
          " c_gen = 1 rho step per trial.)")

    # ---- cross-check variants (time only) ----------------------------------
    print("\n## T5. Cross-check variants, time only, c_trial = 2^30 (C1 bits; margin vs rho)\n")
    rows = []
    for d in derived:
        R2 = Row(d, prm)
        v2 = R2.m_time()
        R1 = Row(d, with_(prm, lp="1LP"))
        v1 = R1.m_time()
        R0 = Row(d, with_(prm, lp="none"))
        v0 = R0.m_time()
        Rp = Row(d, with_(prm, orbit=False, coef="small"))
        vp = Rp.m_time()
        Rpo = Row(d, with_(prm, orbit=True, coef="small"))
        vpo = Rpo.m_time()
        rows.append((d["name"], f"{fmt(v2[0])} ({fmt(v2[1]-v2[0])})", f"{fmt(v1[0])} ({fmt(v1[1]-v1[0])})",
                     f"{fmt(v0[0])} ({fmt(v0[1]-v0[0])})", f"{fmt(vp[0])} ({fmt(vp[1]-vp[0])})",
                     fmt(vp[0] - v2[0]), fmt(vp[0] - vpo[0])))
    print(table(["row", "2LP orbit (default)", "1LP orbit (q^{14/9})", "no LP (basic Gaudry)",
                 "2LP plain (no orbit, +-1 coeffs)", "orbit gain (plain - default)",
                 "orbit gain, same coef model"], rows))
    # exponent check on a synthetic N ladder
    def slope(lp):
        pts = []
        for lN in (60.0, 120.0):
            q = with_(prm, lp=lp, fb_factor=1.0)
            dd = dict(derived[0])
            R = Row(dd, q)
            R.logN = lN
            pts.append(R.m_time()[0])
        return (pts[1] - pts[0]) / 60.0
    print(f"\nExponent check (d log2 T / d log2 N, N 2^60 -> 2^120): 2LP = {slope('2LP'):.4f} "
          f"(theory 1.5 = Q^(2-2/4)); 1LP = {slope('1LP'):.4f} (theory 14/9 = {14/9:.4f}); "
          f"none = {slope('none'):.4f} (theory 2, LA-dominated)")

    # HOLD-D floors at the five rows for context
    print("\n## T6. Context: HOLD-D product-law floor at m = 4 (free decomposition oracle, subspace base"
          " of free size 2^l, N = 16(k-1)) vs C1 free-oracle time (c_trial = 0, c_gen = 1)\n")
    rows = []
    for d in derived:
        N = 16 * (d["k"] - 1)
        R = Row(d, with_(prm, c_trial=0.0))
        rows.append((d["name"], N, fmt(holdd_floor(N, 4, 1)), fmt(holdd_floor(N, 4, d["k"])),
                     fmt(R.m_time()[0]), fmt(d["rho"])))
    print(table(["row", "N", "HOLD-D m=4 plain", "HOLD-D m=4 orbit", "C1 free-oracle time", "rho"], rows))
    print("\n(HOLD-D lets the base size float (2^l) and divides relations by k, LA by k^2; C1 fixes the base"
          " at the F_Q-rational x-coordinates, Q = 2^{4k}, and divides the orbit count by 2k.)")

    # ---- break-even -------------------------------------------------------
    print("\n## T7. Break-even log2 c_trial (C1 = baseline); 'never' = loses even at c_trial = 0\n")
    keys = [m[0] for m in METRICS]
    rows = []
    be = {}
    for d in derived:
        line = [d["name"]]
        for key in keys:
            b, m0 = breakeven_ctrial(key, d, prm)
            be[(key, d["name"])] = b
            line.append("never" if b is None else (">200" if b == INF else fmt(b)))
        rows.append(line)
    print(table(["row"] + keys, rows))

    # ---- single-parameter flips -------------------------------------------
    print("\n## T8. Single-parameter sign flips at the central point (c_trial = 2^30)\n")
    print("Entry = log2 multiplier on that parameter (alone) that flips the sign of the margin;"
          " '-' = no flip within 2^+-80; [in] = flip lies inside the plausible range.\n")
    hdr = ["metric", "row", "margin @2^30"] + [p[0] for p in PERTURB]
    rows = []
    elast = {}
    for key in keys:
        for d in derived:
            m = margin(key, d, prm)
            line = [key, d["name"], fmt(m)]
            for name, fn, rng, _ in PERTURB:
                if name == "LA_unit":
                    fn_, rng_ = la_unit_perturb, la_unit_range(d, prm)
                else:
                    fn_, rng_ = fn, rng
                fp = flip_point(key, d, prm, fn_)
                e = elasticity(key, d, prm, fn_)
                elast[(key, d["name"], name)] = (e, rng_)
                if fp is None:
                    line.append("-")
                else:
                    inside = rng_[0] - 1e-9 <= fp <= rng_[1] + 1e-9
                    line.append(f"{fp:+.2f}" + (" [in]" if inside else ""))
            rows.append(line)
    print(table(hdr, rows))
    print("\nPlausible ranges (log2 multiplier): " + "; ".join(
        f"{n}: {('row-specific ' + r) if rng is None else f'[{rng[0]:+.1f}, {rng[1]:+.1f}]'} ({r})"
        for n, _, rng, r in PERTURB))

    # ---- sensitivity ranking ----------------------------------------------
    print("\n## T9. Sensitivity ranking: |d margin / d log2 param| x plausible log2 width"
          " (max over rows), top 3 per metric\n")
    rows = []
    for key in keys:
        sw = {}
        for name, *_ in PERTURB:
            vals = []
            for d in derived:
                e, rng_ = elast[(key, d["name"], name)]
                vals.append((abs(e) * (rng_[1] - rng_[0]), e))
            sw[name] = max(vals)
        top = sorted(sw.items(), key=lambda t: -t[1][0])[:3]
        rows.append([key] + [f"{n} (swing {v[0]:.2f}, slope {v[1]:+.2f})" for n, v in top])
    print(table(["metric", "1st", "2nd", "3rd"], rows))

    # ---- verdict lines ----------------------------------------------------
    print("\n## T10. Verdict per metric (rows with margin > 0 at each c_trial)\n")
    rows = []
    for key in keys:
        line = [key]
        for lab, _ in CT + [("free", None)]:
            win = [n for (k2, n, l2), (_, _, mg) in all_results.items() if k2 == key and l2 == lab and mg > 0]
            line.append(", ".join(w.replace("c2pnb", "") for w in win) or "none")
        rows.append(line)
    print(table(["metric"] + [f"@{l}" for l, _ in CT] + ["@free-oracle"], rows))

    print("\n## T11. Parameter values used (defaults)\n")
    print(table(["parameter", "value"], [(k, v) for k, v in DEFAULTS.items()]))
    print("\nCitations embedded in this script:")
    for k, v in REPO_CITES.items():
        print(f"- {k}: {v}")
    return 0


def verify_repo(root):
    """Optional: re-read the four source files and confirm embedded constants (read-only)."""
    import os
    import re
    cert = open(os.path.join(root, "analysis/binstd-curve-audit/audit-certificate.txt")).read()
    for name, k, t, h, r_s, _ in ROWS:
        m = re.search(name + r".*?cofactor=(\d+) -> t=(\d+)", cert, re.S)
        assert m and int(m.group(1)) == h and int(m.group(2)) == t, name
    five = open(os.path.join(root, "experiments/EXP-BINSTD-9d1b8e/stage0/five-row-symmetry-certificate.yaml")).read()
    for name, k, t, h, r_s, _ in ROWS:
        assert f"r_from_dump: '{r_s}'" in five, name
    js = open(os.path.join(root, "experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/arm-b-coherent-baseline.json")).read()
    for v in ("91.2591", "126.7745", "152.055", "215.5863", "297.0677"):
        assert f'"own_curve_min_product_log2": {v}' in js, v
    spec = open(os.path.join(root, "experiments/EXP-BINSTD-f442a9/specification.yaml")).read()
    for s in ("RHO_AREA = 2^16", "P_REF = 2^20", "P_LA_MAX = 2^10", "10 N^2 bit operations",
              "D^2 (3 w log2 l + 7 (log2 l)^2)"):
        assert s in spec, s
    print("verify-repo: embedded constants match the repository files\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
