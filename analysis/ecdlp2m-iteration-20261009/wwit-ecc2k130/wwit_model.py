#!/usr/bin/env python3
"""wwit_model.py -- "What would it take" for closure-based (bounded-degree
Groebner / Macaulay / mutant-closure) point-decomposition index calculus to
beat Pollard rho on ECC2K-130.  ZERO-EXPERIMENT: scripted arithmetic only.
Python 3 standard library only.  Deterministic.  Runs in seconds.

Every constant carries a provenance tag:
  [file:line]   read in the repository in this session (paths relative to the
                crypto-autoresearcher root)
  [paper]       Semaev, ePrint 2015/310, frozen at inputs/SEMAEV-2015-310/
  [ASSUMED]     a modelling choice made here, exposed as a parameter with its
                sensitivity shown
  [derived]     arithmetic on the above, done in this file

Units.  "bits" = log2.  Time is reported in rho steps (one ECC2K-130 Pollard
rho iteration) and in bit operations; memory in bits.  margin = rho - IC in
bits; POSITIVE = index calculus better.

-------------------------------------------------------------------------------
THE MODEL (every parameter exposed; see DEFAULTS)
-------------------------------------------------------------------------------
Curve: ECC2K-130, n = 131, #E = 4r, log2 r = 129.000, prime-order subgroup r.
  [knowledge/findings/KN-FIND-aa2efc.md:59-66; ledger/corrections/CORR-20260928-4cb669.yaml:50-58]
Ambient of the product law: N = #E = 4r = 2^131 (CORR-4cb669 scopes the
  finding's table to the full curve group; the N = r ambient lowers every
  floor by 4/(m+1) bits and every D3 budget by 2 bits -- shown as sensitivity).
Matched rho: rho_1 = sqrt(pi r / (4 * 131)) = 2^60.8090, negation + Frobenius
  already included.  [KN-FIND-aa2efc.md:62-66; CORR-4cb669:61-62]
  KR-RHO-18cc42 quotes 2^60.9 iterations ~ 2^77 bit ops  [knowledge/frontiers/
  ecdlp/generic-rho/KR-RHO-18cc42.yaml:5,13]  ->  2^16.1 bit ops per rho step
  [analysis/ecdlp2m-iteration-20261009/ctrial-harvest/fit.py:42]; and the
  rho step rate 22.45e6 it/s on 4 cores -> 4/22.45e6 s = 2^-22.42 s per step
  [fit.py:21; ctrial-harvest/README.md:21].

Factor base: V an F_2-subspace of dimension l, F_V = {P : x(P) in V},
  |F| = 2^l (the finding's convention charges 2^l relations for 2^l points;
  folding negation halves it and shifts floors by 2m/(m+1) bits -- the
  validator's negation-fold variant [coordination/review/icperf-aa2efc-20260926/
  reviews/TASK-20260926-44629c/checks/j2_budget_d3_capped.py:44-49]; shown as
  sensitivity, not applied).  NO Frobenius factor-base gain on ECC2K-130: the
  only faithful sigma-stable V has dimension n-1 = 130 and the quotient on it is
  a net loss for every m in 2..5 [knowledge/findings/KN-FIND-b9a41d.md:108-118].
  Rho DOES keep its sqrt(2n) (it is inside 2^60.8090).

Decomposition probability per attempt (yield conservation / Semaev eq. 11):
  mu(l) = 2^(ml - n) / m!   [paper: inputs/SEMAEV-2015-310/paper_fulltext.md:
  405-417, eq. (11); tables.yaml derived_checks.section_4_3_probability_model]
  Attempts per relation, "D3 convention": max(1, 1/mu)  [CORR-4cb669:77-80;
  experiments/EXP-BINSTD-a222b4/specification.yaml:251-259, 287-291].
  Poisson alternative A(mu) = 1/(1 - e^-mu) (A(1) = 1.582, 0.662 bit)
  [a222b4 spec:252-253] shown as sensitivity.
Relations needed: 2^l.  Attempts total = 2^l * attempts_per_relation.
Linear algebra on the relation matrix: m * 2^(2l) (sparse Wiedemann, weight m)
  [KN-FIND-aa2efc model as identified in ledger/proposals/IDEA-20260926-4b65e3.yaml:20-27;
  a222b4 spec:258-259 "LA_m(B) = k m B^2", k = 1]; memory m * 2^l * l bits
  (m index entries of l bits per row) [ASSUMED form; a222b4 spec:1200-1204 uses
  8-byte entries + three residue vectors -- within 3 bits of this].

Per-attempt cost: a degree-D closure (Macaulay matrix M_D or mutant closure W_D)
  on the Weil-descended system.  Columns = C(N_var, <= D) = sum_{i<=D} C(N_var, i):
  the pilot's W_4 column counts equal C(N, <= 4) exactly (988 / 4048 / 10903 /
  31931 / 102091 at N = 18 (D=3) / 18 / 23 / 30 / 40 (D=4))
  [analysis/ecdlp2m-iteration-20261009/m3-closure-pilot/aggregate.md:4,13,19,20].
  Two presentations:
   (a) DIRECT S_{m+1} descent: N_var = m*l Boolean variables, n = 131 equations of
       Boolean degree m*min(m-1, l) [experiments/EXP-ICPERF-783e9e/impl/arity.py:60-68
       degree law, measured on 14 cells; metrics.json Q3_degree_law true].
       Monomials present = C(ml, <= deg), density 0.27..0.87 of that bound
       [arity.py:71-82; metrics.json anf_density_range].  At n = 131 and the
       budget's l these are 2^29.02, 2^52.78, 2^79.71, 2^103.13 for m = 3..6
       [EXP-ICPERF-783e9e/runs/RUN-ICPERF-2f36fd/checkpoint/budget_table.json,
       n = 131 cells; ctrial-harvest/fit.py:41].  A degree-D closure on this
       presentation needs D >= deg just to hold the equations.
   (b) CHAINED S_3 with t = m: N_var = m*l + (m-2)*n, degree-3 equations,
       (m-1)*n of them  [paper: fulltext.md:1060-1066 "N = n(t-2) + kt" as
       confirmed in knowledge/open-problems/KN-OPEN-86e7e1.md:33-35; pilot
       README.md:9-10 (m = t = 3: N = n + 3k)].
   (c) SEMAEV BLOCK reading: Semaev writes F4 cost [n(m-1)]^{4 omega} and then
       "we think" a block-structured algorithm with block size n reduces it to
       n^{4 omega} [paper fulltext.md:1067-1073].  Modelled here as a closure on
       one block of N_var = 2n + l variables (the largest S_3 block
       S_3(u_{i-1}, u_i, x_{i+1})).  This is the MOST OPTIMISTIC presentation
       and is Semaev's own unproved heuristic; a mutant closure needs the
       cross-block monomials, so (c) is a bound, not an algorithm.  Because
       every single block S_3(u, u', x) is satisfiable on its own, a refutation
       must touch all m-2 blocks: the block cost is multiplied by (m-2) in the
       WWIT cells (Semaev's literal n^{4 omega} without that factor is kept
       only for the Table-3 / EV-SEMBIN reproductions).
  Elimination cost = cols^omega bit operations, omega in {2, 2.37, 3} dense
  [paper fulltext.md:472, 1088: "2.376 <= omega <= 3"];  sparse alternatives
  (block Wiedemann) cols^2 * w (task convention) and cols * nnz(M_D) =
  cols * rows_M * w (Wiedemann proper on the plain Macaulay rows; a lower
  bound, since the refuting W_D has ~5 cols rows), w = monomials per row.  Row weight w from
  the pilot's plain Macaulay M_4 rows: basis_nnz/rows = 37.1, 74.8, 182.1, 411.1
  at N = 18, 23, 30, 40 [results/n9-poly.jsonl, n11-poly.jsonl, n15-poly.jsonl,
  n19-poly.jsonl; aggregated below], which fits w = N^3/156 (slope 3.0 in
  log-log) -> extrapolated [ASSUMED].  Since w >= 1 the sparse model never beats
  dense omega = 2 in this parametrisation; both are reported.
  Closure iterations: the W_4 refutation closes in 3-5 iterations with final
  rows ~ 3.4-6.3 x cols and rank = cols [pilot results: iters 3/4/5, max_rows
  25481/36893/165554 vs cols 4048/10903/31931].  The iteration count and the
  rows/cols ratio are absorbed into omega (cols^omega brackets rows*cols*rank
  with rows ~ 5 cols).  Memory of the closure matrix: dense cols*min(rows,cols)
  ~ cols^2 bits (rank = cols at refutation); sparse rows_M*w*log2(cols) bits
  with rows_M = (m-1) n * C(N_var, <= D-3) (monomial multiples of the cubics).
  Pilot wall anchors (W_4 refutations, m = t = 3): 0.7 s / 7.2 s / 322 s at
  N = 18 / 23 / 30, cols 4048 / 10903 / 31931 [aggregate.md:38,13,19;
  README.md:22-26]: slope log2(322/0.7)/log2(31931/4048) = 2.97 ~ cols^3.
  SAT attempts cost more than UNSAT: W_4 wall SAT/UNSAT = 1.7 (n=9), 4.4 (n=11)
  [results medians]; task convention 2x [ASSUMED 2, range 1.7-4.4].

Early abort: an UNSAT attempt costs one closure at D (refutation at iteration
  3-5 of ONE closure, counted as one elimination at cols^omega); a SAT attempt
  costs SAT_RATIO x that.  The "cheap filter + full solve" split is
  C = cols(D_f)^omega + p_sat * cols(D_s)^omega, p_sat = 1 - e^-mu.

Large primes (GTTD double large prime) in the product-law convention
  [ledger/hypotheses/H-BINSTD-555991.yaml:40-48; ledger/proposals/
  IDEA-20261001-621974.yaml:101-120]: small base B = 2^l, large base B' = 2^l',
  p_2 = (B^(m-2)/(m-2)!) (B'^2/2)/N capped at 1 -> B' = sqrt(2 (m-2)! N / B^(m-2)),
  attempts A_2 = theta B' (theta in [1/2, 1], 1 adopted), LA = w B^2 (w = m
  adopted); per-attempt budget (R - w B^2)/A_2 maximised at B^2 = (m-2)R/((m+2)w).
  Reproduces 2^8.71 (m=3) and 2^22.34 (m=4).  Infeasible at m = 5 (B' < B).
  The decomposition system for a 2LP attempt has (m-2) l + 2 l' small/large
  leg variables (+ (m-2) n chain variables in presentation (b)).

Comparators.  Time: rho = 2^60.8090.  Time x memory: the program's vOW
  convention (HEUR-VOW-CURVE) T x Mem = 6 n W on the ray w = M
  [ledger/evidence/EV-SEMBIN-4125ec.yaml:80-87; analysis/ecdlp2m-iteration-20261009/
  c1-gaudry-n4-c2pnb/c1_model.py:85,124-126].  The program records
  own_curve_min_product_log2 only at n = 163, 233, 283, 409, 571 (91.2591 at
  163) [experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/arm-b-coherent-baseline.json
  vow_product_excess_per_n] -- there is NO n = 131 row, so the n = 131 figure
  6 * 131 * 2^60.8090 = 2^70.43 is DERIVED HERE with W = matched rho.
"""
import math
import sys
from math import log2, lgamma, exp, factorial, comb

INF = float("inf")


# ----------------------------------------------------------------------------
# 0. helpers
# ----------------------------------------------------------------------------
def l2add(*xs):
    xs = [x for x in xs if x != -INF]
    if not xs:
        return -INF
    m = max(xs)
    return m + log2(sum(2.0 ** (x - m) for x in xs))


def l2sub(a, b):
    """log2(2^a - 2^b), a > b."""
    if b == -INF:
        return a
    if b >= a:
        return -INF
    return a + log2(1.0 - 2.0 ** (b - a))


def lbinom(N, k):
    """log2 C(N, k) for real N >= k >= 0 (generalised via lgamma)."""
    if k < 0 or N < k:
        return -INF
    if k == 0:
        return 0.0
    return (lgamma(N + 1) - lgamma(k + 1) - lgamma(N - k + 1)) / math.log(2)


def lcols(N, D):
    """log2 sum_{i<=D} C(N, i)."""
    return l2add(*[lbinom(N, i) for i in range(0, int(D) + 1)])


def golden_min(f, a, b, iters=120):
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
    return f(x), x


def grid_then_golden(f, a, b, step=0.5):
    """Coarse grid (guards against non-unimodality from the mu = 1 kink) then golden."""
    best = (INF, a)
    x = a
    while x <= b + 1e-9:
        v = f(x)
        if v < best[0]:
            best = (v, x)
        x += step
    lo, hi = max(a, best[1] - step), min(b, best[1] + step)
    v, x = golden_min(f, lo, hi)
    return (v, x) if v <= best[0] else best


def fmt(x, nd=2):
    if x is None:
        return "-"
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


# ----------------------------------------------------------------------------
# 1. constants with provenance
# ----------------------------------------------------------------------------
N_BITS = 131                       # field degree                        [KN-FIND-aa2efc.md:59-61]
R_PRIME = 680564733841876926932320129493409985129  # subgroup order     [KN-FIND-aa2efc.md:62]
LOG2_R = log2(R_PRIME)             # 129.000                              [derived]
LOG2_N_AMBIENT = log2(4 * R_PRIME) # 131.000 = #E = 4r (product-law ambient) [CORR-4cb669:50-55]
RHO_BITS = 0.5 * log2(math.pi * R_PRIME / (4 * 131))  # 60.8090 matched rho [CORR-4cb669:61-62]
RHO_REF = 60.8090                  # the published reference                  [KN-FIND-aa2efc.md:63]
LOG2_BITOPS_PER_RHO = 77.0 - 60.9  # 16.1  [KR-RHO-18cc42.yaml:5; ctrial-harvest/fit.py:42]
LOG2_SEC_PER_RHO = log2(4 / 22.45e6)  # -22.42 s/step  [ctrial-harvest/fit.py:21; README.md:21]
VOW_BITS_PER_DP_FACTOR = 3         # Mem = 3 n max(w, M) [EV-SEMBIN-4125ec.yaml:81]
VOW_TM_N131 = log2(6 * N_BITS) + RHO_BITS  # 6 n W, W = matched rho: DERIVED HERE (no n=131 row recorded)

FINDING_FLOORS = {2: 89.25, 3: 68.58, 4: 56.40, 5: 48.44, 6: 42.85, 8: 35.61}  # [KN-FIND-aa2efc.md:31-33]
CORR_RECON = lambda m: 2 * N_BITS / (m + 1) + 2 * log2(m)  # [CORR-20260928-2b8f4e.yaml:71-74] (fit, not identification)
A222B4_PINNED_D3 = {4: 11.01, 5: 33.08, 6: 37.39, 8: 42.52, 16: 49.86}  # [EXP-BINSTD-a222b4/specification.yaml:1207-1211 pinned_D3_bits]
A222B4_MU1 = {4: 11.0, 5: 32.4, 6: 36.7, 8: 42.2, 16: 49.7}             # [same lines, record_mu1_bits; IDEA-4b65e3:41-46]
TASK_BUDGETS = {4: 11.0, 5: 32.6, 6: 37.0, 8: 42.0, 16: 50.0}           # as quoted in the brief (32.6/37.0 = "mu = 4" re-optimised, IDEA-4b65e3:42-44)
LP_BUDGETS = {3: 8.71, 4: 22.34}                                          # [H-BINSTD-555991.yaml:26-27,44-46]
ICPERF_MONOMIALS = {3: 29.02, 4: 52.78, 5: 79.71, 6: 103.13}              # [RUN-ICPERF-2f36fd budget_table.json n=131; fit.py:41]
ICPERF_L = {3: 29, 4: 29, 5: 28, 6: 24}                                   # [same; fit.py:32]
ICPERF_RHO = 61.309                                                        # [budget_table.json n=131 log2_rho] = sqrt(pi 2^131/4)/sqrt(262)
PILOT_COLS = {(18, 3): 988, (18, 4): 4048, (23, 4): 10903, (30, 4): 31931, (40, 4): 102091}  # [aggregate.md]
PILOT_WALL_W4 = {18: 0.7, 23: 7.2, 30: 321.7}                             # [aggregate.md:38,13,19]
PILOT_ROW_WEIGHT_M4 = {18: 37.1, 23: 74.8, 30: 182.1, 40: 411.1}          # [results/*.jsonl basis_nnz/rows, M4 UNSAT S3 medians]
PILOT_ROWS_OVER_COLS_W4 = {18: 25481 / 4048, 23: 36893 / 10903, 30: 165554 / 31931}  # [results: max_rows_seen / ncols, W4 UNSAT]
PILOT_SAT_UNSAT_RATIO = {18: 1.075 / 0.636, 23: 28.402 / 6.495}           # [results medians wall_s W4 SAT / UNSAT]
SEMAEV_C = math.sqrt(2 / math.log(2))                                     # 1.6986 [paper fulltext.md:41,118; eq (17)]

DEFAULTS = dict(
    ambient_bits=LOG2_N_AMBIENT,  # 131 (N = 4r); 129 for the subgroup ambient
    rho_bits=RHO_BITS,
    bitops_per_rho=LOG2_BITOPS_PER_RHO,
    attempt_convention="D3",      # "D3": max(1, 1/mu); "poisson": 1/(1 - e^-mu)
    negation_fold=False,          # True: relations 2^l / 2, LA m (2^l/2)^2 [validator variant]
    sat_ratio=2.0,                # SAT attempt cost / UNSAT attempt cost  [ASSUMED 2; pilot 1.7-4.4]
    row_weight_const=1.0 / 156,   # w = const * N^3 (pilot fit)              [ASSUMED extrapolation]
    rows_over_cols=5.0,           # final W_D rows / cols at refutation      [pilot 3.4-6.3]
    la_weight_mult=1.0,           # multiplies the m in m 2^(2l)
)


# ----------------------------------------------------------------------------
# 2. Product-law pieces (relations, attempts, LA)
# ----------------------------------------------------------------------------
def log_mu(m, l, P):
    return m * l - P["ambient_bits"] - log2(factorial(m))


def log_attempts_per_relation(m, l, P):
    lm = log_mu(m, l, P)
    if P["attempt_convention"] == "D3":
        return max(0.0, -lm)
    if lm > 6:
        return 0.0
    if lm < -40:
        return -lm                      # 1 - e^-mu ~ mu
    mu = 2.0 ** lm
    return -log2(-math.expm1(-mu))


def log_relations(l, P):
    return l - (1.0 if P["negation_fold"] else 0.0)


def log_attempts_total(m, l, P):
    return log_relations(l, P) + log_attempts_per_relation(m, l, P)


def log_LA(m, l, P):
    return log2(m * P["la_weight_mult"]) + 2 * log_relations(l, P)


def log_LA_memory_bits(m, l, P):
    return log2(m) + log_relations(l, P) + log2(max(l, 1.0))


def p_sat(m, l, P):
    lm = log_mu(m, l, P)
    if lm > 6:
        return 1.0
    if lm < -40:
        return 2.0 ** lm
    return -math.expm1(-(2.0 ** lm))


# free-oracle floor (oracle charged 1 group op per attempt) -------------------
def free_oracle_total(m, l, P):
    return l2add(log_attempts_total(m, l, P), log_LA(m, l, P))


def free_oracle_floor(m, P=DEFAULTS):
    return grid_then_golden(lambda l: free_oracle_total(m, l, P), log2(m) + 0.01, 131.0, step=0.25)


# D3 per-attempt budget --------------------------------------------------------
def budget_at_l(m, l, P):
    """log2 of the per-attempt budget (rho steps) at base dimension l: (rho - LA)/attempts."""
    la = log_LA(m, l, P)
    if la >= P["rho_bits"]:
        return -INF
    return l2sub(P["rho_bits"], la) - log_attempts_total(m, l, P)


def d3_budget(m, P=DEFAULTS):
    v, l = grid_then_golden(lambda l: -budget_at_l(m, l, P), log2(m) + 0.01, 131.0, step=0.25)
    return -v, l


# GTTD double-large-prime budget (H-BINSTD-555991 claim C) ---------------------
def lp2_budget(m, theta=1.0, w=None, P=DEFAULTS):
    """Returns (log2 budget per attempt, log2 B, log2 B', log2 attempts) or None if infeasible."""
    w = m if w is None else w
    R = 2.0 ** P["rho_bits"]
    N = 2.0 ** P["ambient_bits"]
    B2 = (m - 2) * R / ((m + 2) * w)             # optimum B^2 = (m-2) R / ((m+2) w)
    lB = 0.5 * log2(B2)
    lBp = 0.5 * (1 + log2(factorial(m - 2)) + P["ambient_bits"] - (m - 2) * lB)  # B' = sqrt(2 (m-2)! N / B^(m-2))
    if lBp < lB + log2(1 / 0.162):               # H-621974-2 needs B <= 0.162 B'
        return None
    lA2 = log2(theta) + lBp
    budget = log2(4 * R / (m + 2)) - lA2         # R - w B^2 = 4R/(m+2)
    return budget, lB, lBp, lA2


# ----------------------------------------------------------------------------
# 3. Closure cost model
# ----------------------------------------------------------------------------
PRESENTATIONS = ("chained", "block", "direct")


def nvar(pres, m, l, n=N_BITS, l_large=None, legs_large=0):
    """Boolean variable count of the descended system."""
    if l_large is None:
        leg_vars = m * l
    else:
        leg_vars = (m - legs_large) * l + legs_large * l_large
    if pres == "direct":
        return leg_vars
    if pres == "chained":
        return leg_vars + (m - 2) * n
    if pres == "block":
        return 2 * n + (l_large if l_large is not None else l)
    raise ValueError(pres)


def min_degree(pres, m, l):
    """Smallest D at which the equations themselves fit in the Macaulay matrix."""
    if pres == "direct":
        return m * min(m - 1, int(math.ceil(l)))   # ICPERF degree law
    return 3                                       # chained / block: cubic S_3 descent


def log_rows_macaulay(pres, m, N, D):
    """Rows of the plain Macaulay matrix at degree D: equations x monomials of degree <= D - deg."""
    if pres == "direct":
        neq = N_BITS
        d0 = D  # at D = deg(system) only the equations themselves
        return log2(neq) + lcols(N, max(0, D - d0))
    neq = (m - 1) * N_BITS if pres == "chained" else N_BITS
    return log2(neq) + lcols(N, D - 3)


def closure_bitops(pres, m, l, D, omega, sparse, P, l_large=None, legs_large=0):
    """log2 bit-ops of ONE degree-D closure (one elimination to full rank) plus memory bits.
    Returns (log2 bitops, log2 memory bits, log2 cols, N_var)."""
    N = nvar(pres, m, l, l_large=l_large, legs_large=legs_large)
    if D < min_degree(pres, m, l):
        return INF, INF, -INF, N
    lc = lcols(N, D)
    if sparse:
        lw = log2(P["row_weight_const"]) + 3 * log2(N)       # w = N^3/156, pilot fit [ASSUMED]
        lw = min(lw, lcols(N, 3))                              # cannot exceed the cubic monomial count
        lrows = log_rows_macaulay(pres, m, N, D)
        if sparse == "nnz":
            cost = lc + lrows + lw                             # Wiedemann: cols iterations x nnz(M_D); M_D rows only (W_D has ~5 cols rows) -> lower bound
        else:
            cost = 2 * lc + lw                                 # task convention: cols^2 x row weight
        mem = lrows + lw + log2(max(lc, 1.0))                  # nnz x index width
    else:
        cost = omega * lc
        mem = 2 * lc                                           # rank = cols at refutation -> cols^2 bits
    if pres == "block":
        cost += log2(max(m - 2, 1))                            # a refutation must touch every one of the m-2 blocks (each block alone is SAT)
    return cost, mem, lc, N


def attempt_cost_bitops(pres, m, l, D, omega, sparse, P, D_filter=None, **kw):
    """Per-attempt bit-ops: UNSAT = one closure at D (or at D_filter), SAT = sat_ratio x closure at D."""
    c, mem, lc, N = closure_bitops(pres, m, l, D, omega, sparse, P, **kw)
    if c == INF:
        return INF, INF, lc, N
    ps = p_sat(m, l, P)
    if D_filter is None:
        per = c + log2((1 - ps) + ps * P["sat_ratio"])
    else:
        cf, memf, _, _ = closure_bitops(pres, m, l, D_filter, omega, sparse, P, **kw)
        per = l2add(cf, c + log2(ps * P["sat_ratio"])) if ps > 0 else cf
        mem = max(mem, memf)
    return per, mem, lc, N


def total_cost(pres, m, l, D, omega, sparse, P, D_filter=None, **kw):
    """log2 total time (rho steps), log2 peak memory (bits), log2 T x M, pieces."""
    per, mem, lc, N = attempt_cost_bitops(pres, m, l, D, omega, sparse, P, D_filter, **kw)
    if per == INF:
        return INF, INF, INF, dict(N=N)
    rel = log_attempts_total(m, l, P) + per - P["bitops_per_rho"]
    la = log_LA(m, l, P)
    T = l2add(rel, la)
    M = max(mem, log_LA_memory_bits(m, l, P))
    return T, M, T + M, dict(N=N, lcols=lc, per_attempt_bitops=per, per_attempt_rho=per - P["bitops_per_rho"],
                             attempts=log_attempts_total(m, l, P), rel=rel, la=la, mem_closure=mem,
                             mem_la=log_LA_memory_bits(m, l, P))


def optimise_l(pres, m, D, omega, sparse, P, metric="time", D_filter=None):
    def f(l):
        T, M, TM, _ = total_cost(pres, m, l, D, omega, sparse, P, D_filter)
        return T if metric == "time" else TM
    v, l = grid_then_golden(f, max(log2(m) + 0.01, 1.0), 131.0, step=0.5)
    T, M, TM, pieces = total_cost(pres, m, l, D, omega, sparse, P, D_filter)
    return dict(l=l, T=T, M=M, TM=TM, **pieces)


# ----------------------------------------------------------------------------
# 4. Reproduction asserts
# ----------------------------------------------------------------------------
def reproduce(P):
    rows = []
    ok = True
    # rho
    d = abs(RHO_BITS - RHO_REF)
    ok &= d < 0.001
    rows.append(("matched rho sqrt(pi r/(4*131))", fmt(RHO_BITS, 4), "60.8090 [KN-FIND-aa2efc.md:63]", fmt(d, 4), d < 0.001))
    # KN-FIND-aa2efc free-oracle floors (finding convention, N = 4r, oracle = 1)
    floors = {}
    for m, ref in FINDING_FLOORS.items():
        v, l = free_oracle_floor(m, P)
        floors[m] = (v, l)
        d = abs(v - ref)
        ok &= d <= 0.01 if m in (3, 4) else d <= 0.02
        rows.append((f"free-oracle floor m={m} (l*={l:.2f})", fmt(v, 4), f"{ref} [KN-FIND-aa2efc.md:31-33]", fmt(d, 4), d <= 0.02))
        rec = CORR_RECON(m)
        rows.append((f"  CORR-2b8f4e fit 2n/(m+1)+2log2 m, m={m}", fmt(rec, 2), f"{ref}", fmt(abs(rec - ref), 2), abs(rec - ref) <= 0.5))
    # a222b4 pinned D3 budgets (D3 convention) and the mu-Poisson column
    Pp = dict(P, attempt_convention="poisson")
    for m in (4, 5, 6, 8, 16):
        b, l = d3_budget(m, P)
        d = abs(b - A222B4_PINNED_D3[m])
        ok &= d <= 0.05
        rows.append((f"D3 budget m={m} (l*={l:.3f})", fmt(b, 3), f"{A222B4_PINNED_D3[m]} [a222b4 spec:1207-1211 pinned_D3]", fmt(d, 3), d <= 0.05))
        bp, lp = d3_budget(m, Pp)
        d2 = abs(bp - A222B4_MU1[m])
        ok &= d2 <= 0.5
        rows.append((f"  Poisson A(mu) re-optimised, m={m} (l*={lp:.2f})", fmt(bp, 2), f"{A222B4_MU1[m]} [a222b4 record_mu1]; brief {TASK_BUDGETS[m]}", fmt(d2, 2), d2 <= 0.5))
    # m = 3 plain budget -15.55 [H-BINSTD-555991.yaml:98-99]
    b3, l3 = d3_budget(3, P)
    d = abs(b3 - (-15.55))
    ok &= d <= 0.05
    rows.append((f"plain budget m=3 (l*={l3:.3f})", fmt(b3, 3), "-15.55 [H-BINSTD-555991.yaml:98-99]", fmt(d, 3), d <= 0.05))
    # 2LP budgets
    for m, ref in LP_BUDGETS.items():
        r = lp2_budget(m, P=P)
        d = abs(r[0] - ref)
        ok &= d <= 0.05
        rows.append((f"2LP budget m={m} (log2 B={r[1]:.2f}, B'={r[2]:.2f})", fmt(r[0], 3), f"{ref} [H-BINSTD-555991.yaml:26-27]", fmt(d, 3), d <= 0.05))
    assert lp2_budget(5, P=P) is None, "m=5 2LP must be infeasible (proves-too-much control)"
    rows.append(("2LP m=5 infeasible (B' < B/0.162)", "None", "infeasible [IDEA-621974:128-131]", "0", True))
    # ICPERF monomial counts: C(ml, <= m(m-1)) at the budget l
    for m, ref in ICPERF_MONOMIALS.items():
        l = ICPERF_L[m]
        v = lcols(m * l, m * min(m - 1, l))
        d = abs(v - ref)
        ok &= d <= 0.02
        rows.append((f"ICPERF monomials C({m*l}, <= {m*min(m-1,l)}), m={m}", fmt(v, 2), f"{ref} [budget_table.json n=131]", fmt(d, 3), d <= 0.02))
    # pilot columns
    for (N, D), ref in PILOT_COLS.items():
        v = sum(comb(N, i) for i in range(D + 1))
        ok &= v == ref
        rows.append((f"pilot cols C({N}, <= {D})", str(v), f"{ref} [aggregate.md]", str(abs(v - ref)), v == ref))
    # vOW own-curve minimum at n = 163 (the nearest recorded row): 6 n W with W = 0.886 2^(n/2)
    v163 = log2(6 * 163) + log2(0.886) + 163 / 2
    d = abs(v163 - 91.2591)
    ok &= d <= 0.01
    rows.append(("vOW 6nW n=163 (W = 0.886 2^(n/2))", fmt(v163, 4), "91.2591 [arm-b-coherent-baseline.json]", fmt(d, 4), d <= 0.01))
    # Semaev Table 3 crossing (time only, omega = 3, n^12): tables.yaml says 302
    nx = semaev_time_crossing(omega=3.0, block=True, bitops_shift=0.0, start=100)
    ok &= abs(nx - 302) <= 2
    rows.append(("Semaev Table-3 time-only crossing (omega=3, n^12)", str(nx), "302 [tables.yaml derived_checks]", str(abs(nx - 302)), abs(nx - 302) <= 2))
    return ok, rows, floors


# ----------------------------------------------------------------------------
# 5. Asymptotics (Semaev cost family, general n)
# ----------------------------------------------------------------------------
def semaev_stage1(n, m, omega, block, bitops_shift, D=4, k_rule="literal"):
    """log2 first-stage cost in rho-step units: attempts x closure cost, closure = cols^omega bit ops.
    block=True: Semaev's n^{4 omega} reading (cols = n^D);  block=False: cols = C((m-1) n + mk, <= D).
    k_rule="literal": Semaev eq. (15) with k = n/m, attempts = m! 2^k  [paper fulltext.md:1076-1086];
    k_rule="cap":     k = (n + log2 m!)/m (mu = 1), attempts = 2^k  [the product-law cap, IDEA-4b65e3 (B)].
    bitops_shift = log2 bit-ops per rho step credited (0 = Semaev's own unit convention)."""
    if k_rule == "literal":
        k = n / m
        latt = log2(factorial(m)) + k
    else:
        k = (n + log2(factorial(m))) / m
        latt = k
    if block:
        lc = D * log2(n)
        bm = 0.0 if k_rule == "literal" else log2(max(m - 2, 1))   # literal = Semaev's own n^{4w} (for reproduction); cap rule charges every block
    else:
        lc = lcols((m - 2) * n + m * k, D)
        bm = 0.0
    return latt + omega * lc + bm - bitops_shift, k


def semaev_total_time(n, omega, block, bitops_shift, D=4, m_range=None, k_rule="literal"):
    best = (INF, None)
    if m_range is None:
        m_range = range(2, 40) if k_rule == "literal" else range(2, 17)   # cap rule: same m grid as the cells (<= 16)
    for m in m_range:
        s1, k = semaev_stage1(n, m, omega, block, bitops_shift, D, k_rule)
        t = l2add(s1, 2 * k)
        if t < best[0]:
            best = (t, m)
    return best


def rho_generic_bits(n):
    return 0.5 * n + log2(0.886)  # W = 0.886 2^(n/2) [EV-SEMBIN-4125ec.yaml:81-82]


def semaev_time_crossing(omega, block, bitops_shift, D=4, start=50, stop=3000, k_rule="literal"):
    """First n (persistent to `stop`) where min_m Semaev total time < 2^(n/2) (Table 3 compares to 2^(n/2))."""
    last_above = None
    for n in range(start, stop + 1):
        t, m = semaev_total_time(n, omega, block, bitops_shift, D, k_rule=k_rule)
        if t >= 0.5 * n:
            last_above = n
    return (last_above + 1) if last_above is not None else start


def semaev_tm_crossing(omega, storage, bitops_shift, D=4, start=100, stop=1000, block=True, k_rule="literal"):
    """Time x memory vs vOW 6 n W (W = 0.886 2^(n/2)); storage in {'dense', 'sparse_semaev'}.
    Time = Semaev stage 1 (block n^{4 omega} as in Table 3 unless block=False) + 2^(2k).
    Memory = relation store 2^ceil(n/m) (m k + 2 n) bits log-summed with the F4 working set
    (dense: width^2 with width = C((m-2) n + m k, <= 4); sparse: Semaev's (nm)^4/24 x n^3/m).
    Reproduction target: 520 (dense) / 460 (sparse) at omega = 3 [EV-SEMBIN-4125ec.yaml:84-85, 106-109]."""
    last_above = None
    for n in range(start, stop + 1):
        best = INF
        for m in (range(2, 40) if k_rule == "literal" else range(2, 17)):
            s1, k = semaev_stage1(n, m, omega, block, bitops_shift, D, k_rule)
            kc = math.ceil(n / m)
            N = (m - 2) * n + m * k
            lc = lcols(N, D)
            t = l2add(s1, 2 * k)
            store = kc + log2(m * kc + 2 * n)
            if storage == "dense":
                ws = 2 * lc
            else:  # Semaev's own sparse answer (n m)^4/24 x n^3/m bits [KN-OPEN-86e7e1.md:33]
                ws = 4 * log2(n * m) - log2(24) + 3 * log2(n) - log2(m)
            mem = l2add(store, ws)
            best = min(best, t + mem)
        if best >= log2(6 * n) + rho_generic_bits(n):
            last_above = n
    return (last_above + 1) if last_above is not None else start


# ----------------------------------------------------------------------------
# 6. Driver
# ----------------------------------------------------------------------------
def main():
    P = dict(DEFAULTS)
    out = []
    pr = out.append

    pr("# WWIT: closure-based point-decomposition index calculus vs rho on ECC2K-130 (zero-experiment model)\n")
    pr(f"Constants: n = {N_BITS}; log2 r = {LOG2_R:.3f}; ambient log2 N = {P['ambient_bits']:.3f} (N = 4r); "
       f"rho = 2^{RHO_BITS:.4f} rho steps; 2^{LOG2_BITOPS_PER_RHO:.1f} bit-ops per rho step; "
       f"2^{LOG2_SEC_PER_RHO:.2f} s per rho step; rho in bit-ops = 2^{RHO_BITS + LOG2_BITOPS_PER_RHO:.2f}; "
       f"rho wall at the 2009 rate = 2^{RHO_BITS + LOG2_SEC_PER_RHO:.2f} s = {2 ** (RHO_BITS + LOG2_SEC_PER_RHO) / 3.15576e7:.3g} core-years.")
    pr(f"Time x memory comparator (DERIVED HERE, no n = 131 row in the program): 6 n W = 6 x 131 x 2^{RHO_BITS:.4f} = 2^{VOW_TM_N131:.2f} (rho-step x bit).\n")

    # --- T0 reproduction
    ok, rows, floors = reproduce(P)
    pr("## T0. Reproduction of the program's numbers (asserted)\n")
    pr(table(["quantity", "this script", "program record [cite]", "|diff|", "pass"], rows))
    assert ok, "REPRODUCTION FAILED"
    pr("\nALL REPRODUCTION ASSERTIONS PASSED (floors 68.58 / 56.40 to 0.01 bit; a222b4 pinned D3 to 0.05 bit; mu-column to 0.5 bit; 2LP 8.71 / 22.34 to 0.05 bit).\n")

    # --- T1 pilot-derived constants
    pr("## T1. Pilot-derived closure constants (m = t = 3 chained S_3, W_4 / M_4; analysis/ecdlp2m-iteration-20261009/m3-closure-pilot/results)\n")
    rows = []
    for N in (18, 23, 30, 40):
        w = PILOT_ROW_WEIGHT_M4[N]
        fitw = N ** 3 * P["row_weight_const"]
        rows.append((N, PILOT_COLS.get((N, 4)), fmt(w, 1), fmt(fitw, 1), fmt(PILOT_ROWS_OVER_COLS_W4.get(N), 2),
                     fmt(PILOT_WALL_W4.get(N), 1), fmt(PILOT_SAT_UNSAT_RATIO.get(N), 2)))
    pr(table(["N_var", "cols C(N,<=4)", "M_4 row weight w (nnz/row)", "fit N^3/156", "W_4 rows/cols at refutation", "W_4 UNSAT median wall s", "W_4 SAT/UNSAT wall"], rows))
    xs = [(log2(N), log2(PILOT_ROW_WEIGHT_M4[N])) for N in (18, 23, 30, 40)]
    sl = (xs[-1][1] - xs[0][1]) / (xs[-1][0] - xs[0][0])
    pc = [(log2(PILOT_COLS[(N, 4)]), log2(PILOT_WALL_W4[N])) for N in (18, 23, 30)]
    slw = (pc[-1][1] - pc[0][1]) / (pc[-1][0] - pc[0][0])
    pr(f"\nRow-weight log-log slope N=18->40: {sl:.2f} (cubic fill; w ~ N^3/156, ASSUMED to extrapolate). "
       f"W_4 wall vs cols slope N=18->30: {slw:.2f} (i.e. wall ~ cols^{slw:.2f}; supports omega near 3 for the M4RI closure as run). "
       f"Implied bit-ops at N=30: wall 321.7 s = 2^{log2(321.7) - LOG2_SEC_PER_RHO:.1f} rho steps = 2^{log2(321.7) - LOG2_SEC_PER_RHO + LOG2_BITOPS_PER_RHO:.1f} bit-ops vs cols^3 = 2^{3*log2(31931):.1f}, cols^2 = 2^{2*log2(31931):.1f}.\n")

    # --- T2 budgets per m (the c*(m) column) with system sizes
    pr("## T2. Per-attempt budget c*(m) at the optimal l (D3 convention: one attempt per relation above the cap), and system sizes\n")
    rows = []
    budgets = {}
    for m in (3, 4, 5, 6, 8, 10, 12, 16):
        b, l = d3_budget(m, P)
        budgets[m] = (b, l)
        la = log_LA(m, l, P)
        att = log_attempts_total(m, l, P)
        rows.append((m, fmt(l, 2), fmt((N_BITS + log2(factorial(m))) / m, 2), fmt(la, 2), fmt(att, 2), fmt(b, 2), fmt(b + LOG2_BITOPS_PER_RHO, 2),
                     fmt(b + LOG2_SEC_PER_RHO, 2), int(round(nvar("direct", m, l))), int(round(nvar("chained", m, l))), int(round(nvar("block", m, l))),
                     min_degree("direct", m, l), fmt(p_sat(m, l, P), 2)))
    pr(table(["m", "l*", "l_cap=(131+log2 m!)/m", "log2 LA", "log2 attempts", "c*(m) log2 rho steps", "c*(m) log2 bit-ops", "c*(m) log2 seconds", "N_var direct (ml)", "N_var chained (ml+(m-2)n)", "N_var block (2n+l)", "direct deg", "p_sat"], rows))
    pr("\nc*(m) in rho steps equals the pinned D3 column (CORR-4cb669 D3; a222b4). m = 3 is negative: no oracle, however cheap, ties rho there.")
    r3 = lp2_budget(3, P=P); r4 = lp2_budget(4, P=P)
    pr(f"2LP (GTTD) budgets: m=3 2^{r3[0]:.2f} at log2 B={r3[1]:.2f}, B'={r3[2]:.2f}, attempts 2^{r3[3]:.2f}; m=4 2^{r4[0]:.2f} at log2 B={r4[1]:.2f}, B'={r4[2]:.2f}, attempts 2^{r4[3]:.2f}. "
       f"System sizes for a 2LP attempt (chained): m=3 N_var = l + 2l' + n = {1*r3[1] + 2*r3[2] + 131:.0f}; m=4 N_var = 2l + 2l' + 2n = {2*r4[1] + 2*r4[2] + 262:.0f}. In bit-ops: {r3[0]+LOG2_BITOPS_PER_RHO:.2f} (m=3), {r4[0]+LOG2_BITOPS_PER_RHO:.2f} (m=4).\n")

    # --- T3 D_max table
    pr("## T3. D_max(m, omega): largest closure degree D whose ONE dense elimination cols^omega fits c*(m) (bit-ops). Also omega_max at D = 4 and the margin at D = 4.\n")
    pr("A cell reads 'none' when even D = 3 (the equations themselves, which refute nothing: pilot W_3 0/60, 0/40, 0/40; Semaev proves first fall degree 4) does not fit. "
       "D = 3 is structurally non-refuting, so the operative requirement is D_max >= 4.\n")
    for pres in PRESENTATIONS:
        rows = []
        for m in (3, 4, 5, 6, 8, 10, 12, 16):
            b, l = budgets[m]
            cb = b + LOG2_BITOPS_PER_RHO
            N = nvar(pres, m, l)
            dmin = min_degree(pres, m, l)
            line = [pres, m, fmt(cb, 1), int(round(N)), dmin]
            lc4 = lcols(N, max(4, dmin))
            bm = log2(max(m - 2, 1)) if pres == "block" else 0.0
            for omega in (2.0, 2.37, 3.0):
                dmax = None
                for D in range(dmin, 60):
                    if omega * lcols(N, D) + bm <= cb:
                        dmax = D
                    else:
                        break
                line.append("none" if dmax is None else str(dmax) + ("(nonref)" if dmax == 3 and pres != "direct" else ""))
            line.append(fmt(lc4, 1))
            line.append(fmt((cb - bm) / lc4, 2) if cb > -INF else "-")
            line.append(fmt(cb - 2.0 * lc4 - bm, 1))
            rows.append(line)
        pr(f"### Presentation: {pres}  (N_var = " + {"direct": "m l; D must be >= m*min(m-1,l)", "chained": "m l + (m-2) n; cubic", "block": "2n + l; cubic (Semaev's unproved block heuristic), cost x (m-2) blocks"}[pres] + ")\n")
        pr(table(["pres", "m", "c*(m) bit-ops", "N_var", "D_min", "D_max omega=2", "D_max omega=2.37", "D_max omega=3", "log2 cols at D=max(4,D_min)", "omega_max at that D", "margin at D=4, omega=2 (bits)"], rows))
        pr("")
    # LP variants
    pr("### D_max under the 2LP (GTTD) budgets, chained presentation (large legs widen the system)\n")
    rows = []
    for m in (3, 4):
        r = lp2_budget(m, P=P)
        cb = r[0] + LOG2_BITOPS_PER_RHO
        N = nvar("chained", m, r[1], l_large=r[2], legs_large=2)
        line = [m, fmt(cb, 1), int(round(N))]
        for omega in (2.0, 2.37, 3.0):
            dmax = None
            for D in range(3, 60):
                if omega * lcols(N, D) <= cb:
                    dmax = D
                else:
                    break
            line.append("none" if dmax is None else str(dmax) + ("(nonref)" if dmax == 3 else ""))
        line.append(fmt(lcols(N, 4), 1)); line.append(fmt(cb / lcols(N, 4), 2))
        rows.append(line)
    pr(table(["m", "2LP budget bit-ops", "N_var chained", "D_max omega=2", "D_max omega=2.37", "D_max omega=3", "log2 cols D=4", "omega_max at D=4"], rows))
    pr("")

    # --- T4 the full cell table, l optimised for time
    pr("## T4. Full charged cost per (presentation, m, D, omega, sparsity), l optimised for TIME. Columns: l*, N_var, log2 cols, per-attempt bit-ops, total time (rho steps), margin vs rho, peak memory (bits), T x M, margin vs 6nW = 2^70.43\n")
    winners = []
    all_cells = []
    for pres in PRESENTATIONS:
        rows = []
        for m in (3, 4, 5, 6, 8, 10, 12, 16):
            for D in (3, 4, 5, 6):
                for omega, sparse, lab in ((2.0, False, "dense w=2"), (2.37, False, "dense w=2.37"), (3.0, False, "dense w=3"), (2.0, "w", "sparse cols^2 w"), (2.0, "nnz", "sparse cols x nnz(M_D)")):
                    if D < min_degree(pres, m, 1.0) and pres == "direct":
                        continue
                    res = optimise_l(pres, m, D, omega, sparse, P)
                    if res["T"] == INF:
                        continue
                    mT = RHO_BITS - res["T"]
                    mTM = VOW_TM_N131 - res["TM"]
                    nonref = (D == 3 and pres != "direct")
                    rows.append((m, D, lab, fmt(res["l"], 2), int(round(res["N"])), fmt(res["lcols"], 1), fmt(res["per_attempt_bitops"], 1),
                                 fmt(res["attempts"], 1), fmt(res["T"], 2), fmt(mT, 2) + (" BEATS" if mT > 0 else ""), fmt(res["M"], 1), fmt(res["TM"], 1),
                                 fmt(mTM, 1) + (" BEATS" if mTM > 0 else ""), "non-refuting" if nonref else ""))
                    all_cells.append((pres, m, D, lab, res, mT, mTM, nonref))
                    if mT > 0 or mTM > 0:
                        winners.append((pres, m, D, lab, res, mT, mTM, nonref))
        pr(f"### Presentation: {pres}\n")
        if pres == "direct":
            pr("(direct: only D >= m*min(m-1,l) is defined; rows at smaller D are omitted. At the optimal l the degree is m(m-1): 6, 12, 20, 30, 56, ... so D = 6 appears only at m = 3.)\n")
        pr(table(["m", "D", "elim", "l*", "N_var", "log2 cols", "per-attempt bit-ops", "log2 attempts", "T (log2 rho steps)", "margin vs rho", "mem bits", "T x M", "margin vs 6nW", "note"], rows))
        pr("")

    # --- T5 winners
    pr("## T5a. REFUTING cells (D >= 4) under which the total charged cost drops below rho (time) or below 6nW (time x memory)\n")
    ref_w = [w for w in winners if not w[7]]
    if not ref_w:
        pr("NONE.")
    else:
        rows = []
        for (pres, m, D, lab, res, mT, mTM, nonref) in sorted(ref_w, key=lambda t: -t[5]):
            rows.append((pres, m, D, lab, fmt(res["l"], 2), fmt(res["lcols"], 1), fmt(res["per_attempt_bitops"], 1), fmt(res["T"], 2), fmt(mT, 2), fmt(res["M"], 1), fmt(res["TM"], 1), fmt(mTM, 1),
                         fmt(l2sub(RHO_BITS, res["la"]) - res["attempts"], 2),
                         "Semaev block heuristic (closure on 2n+l vars), unproved; omega = 2 is the dense-elimination floor" if pres == "block" else ""))
        pr(table(["pres", "m", "D", "elim", "l*", "log2 cols", "per-attempt bit-ops", "T (log2 rho steps)", "margin vs rho", "mem bits", "T x M", "margin vs 6nW", "per-attempt budget left (log2 rho steps)", "caveat"], rows))
    pr("")
    pr("## T5b. D = 3 rows that come in under rho (listed for completeness; NON-REFUTING: D = 3 is the cubic equations with no multiplier, pilot W_3 refuted 0 of 140 UNSAT instances, Semaev proves first fall degree 4)\n")
    nr = [w for w in winners if w[7]]
    rows = [(pres, m, D, lab, fmt(res["l"], 2), fmt(res["T"], 2), fmt(mT, 2), fmt(mTM, 1)) for (pres, m, D, lab, res, mT, mTM, nonref) in sorted(nr, key=lambda t: -t[5])]
    pr(table(["pres", "m", "D", "elim", "l*", "T", "margin vs rho", "margin vs 6nW"], rows) if rows else "NONE.")
    pr(f"\nWinning cells in all: {len(winners)}; D = 3 non-refuting: {len(nr)}; refuting D >= 4: {len(ref_w)} (block heuristic: {len([w for w in ref_w if w[0] == 'block'])}, full presentations: {len([w for w in ref_w if w[0] != 'block'])}). "
       f"Time x memory winners (any D): {len([w for w in winners if w[6] > 0])}.\n")

    # --- T6 per-attempt budget left in each candidate cell; required omega
    pr("## T6. For D = 4 (the smallest refuting degree; pilot's flat W_4 and Semaev's Assumption 1): the omega needed to tie rho, by presentation and m, and the gap at realistic omega\n")
    rows = []
    for pres in PRESENTATIONS:
        for m in (4, 5, 6, 8, 10, 12, 16):
            b, l = budgets[m]
            N = nvar(pres, m, l)
            D = max(4, min_degree(pres, m, l))
            lc = lcols(N, D)
            cb = b + LOG2_BITOPS_PER_RHO
            bm = log2(max(m - 2, 1)) if pres == "block" else 0.0
            cw, _, _, _ = closure_bitops(pres, m, l, D, 2.0, "w", P)
            cn, _, _, _ = closure_bitops(pres, m, l, D, 2.0, "nnz", P)
            rows.append((pres, m, D, fmt(lc, 1), fmt(cb, 1), fmt((cb - bm) / lc, 3), fmt(cb - 2 * lc - bm, 1), fmt(cb - 2.37 * lc - bm, 1), fmt(cb - 3 * lc - bm, 1),
                         fmt(cb - cw, 1), fmt(cb - cn, 1)))
    pr(table(["pres", "m", "D used", "log2 cols", "c*(m) bit-ops", "omega needed to tie", "gap omega=2", "gap omega=2.37", "gap omega=3", "gap sparse cols^2 w", "gap sparse cols x nnz(M_D)"], rows))
    pr("\n(negative gap = the closure is that many bits too expensive per attempt at the l that maximises the budget; T4 re-optimises l per cell and the verdicts agree.)\n")

    # --- T7 early-abort split
    pr("## T7. Early-abort 'cheap filter + full solve' split (chained, omega = 2): filter at D_f refutes UNSAT, full solve at D_s = 4 only on the p_sat survivors\n")
    rows = []
    for m in (4, 5, 6, 8, 16):
        for Df in (3, 4):
            res = optimise_l("chained", m, 4, 2.0, False, P, D_filter=Df)
            rows.append((m, Df, 4, fmt(res["l"], 2), fmt(p_sat(m, res["l"], P), 2), fmt(res["per_attempt_bitops"], 1), fmt(res["T"], 2), fmt(RHO_BITS - res["T"], 2)))
    pr(table(["m", "D_filter", "D_solve", "l*", "p_sat", "per-attempt bit-ops", "T", "margin vs rho"], rows))
    pr("\nA D_f = 3 filter refutes nothing (pilot), so its row is a lower bound that no algorithm attains; with D_f = 4 the filter IS the full closure and the split saves only the SAT_RATIO factor. At the cap p_sat ~ 0.63, so early abort cannot buy more than ~1 bit there.\n")

    # --- T8 sensitivity
    pr("## T8. Sensitivity: which parameter flips the sign. Reference cell = the best refuting cell per presentation (D = 4, omega = 2, dense, l optimised for time)\n")
    best_by_pres = {}
    for pres in PRESENTATIONS:
        cands = [c for c in all_cells if c[0] == pres and not c[7] and c[2] >= 4 and c[3] == "dense w=2"]
        if cands:
            best_by_pres[pres] = max(cands, key=lambda c: c[5])
    rows = []
    for pres, (p_, m, D, lab, res, mT, mTM, nonref) in best_by_pres.items():
        base = mT
        def margin_with(**kw):
            Q = dict(P, **kw)
            r = optimise_l(pres, m, D, 2.0, False, Q)
            return Q["rho_bits"] - r["T"]
        # flips
        lc = res["lcols"]
        omega_tie = (l2sub(RHO_BITS, res["la"]) - res["attempts"] + LOG2_BITOPS_PER_RHO) / lc if res["la"] < RHO_BITS else None
        bitops_tie = LOG2_BITOPS_PER_RHO - base  # bit-ops/rho-step exponent needed to tie (holding l)
        rows.append((pres, m, D, fmt(base, 2),
                     fmt(omega_tie, 3),
                     fmt(bitops_tie, 1),
                     fmt(margin_with(ambient_bits=LOG2_R) - base, 2),
                     fmt(margin_with(negation_fold=True) - base, 2),
                     fmt(margin_with(attempt_convention="poisson") - base, 2),
                     fmt(margin_with(sat_ratio=1.0) - base, 2) + " / " + fmt(margin_with(sat_ratio=4.4) - base, 2),
                     fmt(margin_with(la_weight_mult=3.0) - base, 2),
                     ("n/a (D<D_min)" if 5 < min_degree(pres, m, res["l"]) else fmt(RHO_BITS - optimise_l(pres, m, 5, 2.0, False, P)["T"] - base, 1))))
    pr(table(["pres", "m", "D", "margin (bits)", "omega that ties (D=4)", "log2 bit-ops/rho-step that ties", "d margin: ambient N=r", "d: negation fold", "d: Poisson A(mu)", "d: SAT ratio 1 / 4.4", "d: LA k=3", "d: D=5 instead of 4"], rows))
    pr("\nReading: the sign is set by (1) omega (the D = 4 column count is fixed by N_var, so cost = omega x log2 cols), (2) the degree D (one step adds ~log2(N/5) ~ 6-8 bits of columns, times omega), and (3) the presentation (block vs full N_var changes log2 cols at D = 4 by 10-12 bits at m >= 8). Convention shifts (ambient, negation fold, Poisson, SAT ratio, LA constant) move margins by at most ~3 bits and flip nothing.\n")

    # --- T9 asymptotics
    pr("## T9. Asymptotic reading (D = 4 bounded for all m; Semaev cost family), general n, compared with 2^(n/2) as Table 3 does\n")
    rows = []
    for k_rule in ("literal", "cap"):
        for block in (True, False):
            for omega in (2.0, 2.37, 3.0):
                for shift in (0.0, LOG2_BITOPS_PER_RHO):
                    nx = semaev_time_crossing(omega, block, shift, k_rule=k_rule)
                    t131, m131 = semaev_total_time(131, omega, block, shift, k_rule=k_rule)
                    rows.append(("Semaev eq.(15) k=n/m, attempts m! 2^k" if k_rule == "literal" else "cap k=(n+log2 m!)/m, attempts 2^k",
                                 "n^{4w} block" if block else "full C((m-1)n+mk,<=4)", omega, fmt(shift, 1), nx, fmt(t131, 1), m131, fmt(0.5 * 131 - t131, 1), fmt(RHO_BITS - t131, 1)))
    pr(table(["k / attempts rule", "closure cols", "omega", "bit-ops/rho-step credited (log2)", "time-only crossover n (persistent, vs 2^(n/2))", "min_m total time at n=131 (log2)", "m*", "margin vs 2^65.5 at n=131", "margin vs matched rho 2^60.81"], rows))
    pr("\nTable-3 reproduction: literal rule, omega = 3, n^12, no unit credit -> crossover 302 (tables.yaml derived_checks: 302; the paper states n > 310). "
       "Semaev's literal k = n/m overcharges attempts by log2(m!)(1 - 1/m) bits relative to the mu = 1 cap at finite n (the cap rule is the one the WWIT cells above use, with m <= 16 and the (m-2) block multiplier on the block reading), so the cap rows are the fair finite-n reading of the same family. "
       "The full variable count moves every crossover up; crediting 2^16.1 bit-ops per rho step moves it down. "
       f"The optimum m grows like sqrt(2 ln2 n / ln n) and the exponent is {SEMAEV_C:.4f} sqrt(n ln n) (eq. 17; c = sqrt(2/ln 2)); at n = 131 that is 2^{SEMAEV_C*math.sqrt(131*math.log(131)):.1f} before the polynomial factors -- the polynomial factors (cols^omega ~ 2^56-2^84 at omega 2-3) are what decide the finite-n verdict.\n")
    rows = []
    for storage in ("dense", "sparse_semaev"):
        for omega in (3.0, 2.37, 2.0):
            nx = semaev_tm_crossing(omega, storage, 0.0)
            nx_cap = semaev_tm_crossing(omega, storage, 0.0, k_rule="cap")
            nx_cap_credit = semaev_tm_crossing(omega, storage, LOG2_BITOPS_PER_RHO, k_rule="cap")
            rows.append((storage, omega, nx, nx_cap, nx_cap_credit, "520 (dense) / 460 (sparse) at omega=3 [EV-SEMBIN-4125ec O-1/O-3]" if omega == 3.0 else ""))
    pr(table(["storage reading", "omega", "T x M crossover n, Semaev literal (reproduction)", "T x M crossover, cap rule", "T x M crossover, cap rule + 2^16.1 credit", "program record"], rows))
    pr("\nThe T x M reproduction uses: stage 1 = m! 2^(n/m) n^(4 omega) (Table 3), stage 2 = 2^(2n/m), relation store 2^ceil(n/m) (mk+2n) bits log-summed with the working set (cols^2 for dense, (nm)^4/24 x n^3/m for Semaev-sparse), m = argmin of the product; vOW = 6 n x 0.886 2^(n/2). "
       "EV-SEMBIN-4125ec O-2 says the exact store convention is load-bearing for a bit-exact reproduction; a 0-5 unit difference in n is that convention.\n")

    # --- Headline
    pr("## HEADLINE\n")
    full_ref = [w for w in winners if not w[7] and w[0] != "block"]
    block_ref = [w for w in winners if not w[7] and w[0] == "block"]
    tm_ref = [w for w in winners if not w[7] and w[6] > 0]
    pr(f"1. Under the full variable count (direct or chained S_3), NO cell (m in 3..16, D in 3..6, omega in {{2, 2.37, 3}}, dense or sparse) beats rho 2^60.81 on ECC2K-130 with a refuting degree D >= 4: winners = {len(full_ref)}.")
    blk = sorted(block_ref, key=lambda w: -w[5])
    blk_desc = "; ".join(f"m={w[1]} {w[3]} +{w[5]:.1f} bits" for w in blk) if blk else "none"
    pr(f"2. Under Semaev's unproved block heuristic (closure on 2n + l variables, charged once per block) with D = 4: winners = {len(block_ref)} cells, all at omega = 2 (the dense-elimination floor) or the cols x nnz(M_D) sparse lower bound, all at m >= 10, none at omega = 2.37 or 3: {blk_desc}. At omega = 2.37 the best block cell is within 4-5 bits of rho (T6, T9).")
    pr(f"3. Time x memory: NO refuting cell beats 6nW = 2^{VOW_TM_N131:.2f}: winners = {len(tm_ref)}. The closure matrix alone (cols^2 bits at D = 4) is 2^55-2^80 bits per attempt; the best refuting cell is 26-40 bits above 6nW.")
    pr("4. The only 'winning' cells in the full presentations are D = 3, which is the equations themselves (no multiplication) and refutes nothing (pilot W_3: 0 of 140 UNSAT instances; Semaev proves first fall degree 4).")
    t3b = {m: None for m in (8, 10, 12, 16)}
    for m in t3b:
        b, l = budgets[m]; cb = b + LOG2_BITOPS_PER_RHO; N = nvar("block", m, l)
        t3b[m] = cb - 2.0 * lcols(N, 4) - log2(m - 2)
    pr(f"5. D_max(m) at realistic omega (>= 2.37) is 'none' (below 4) for every m under the full presentations and under the block heuristic alike; the m = 4/5 pilot would have to show a refuting closure at D <= 3 to matter, which is impossible by the first-fall-degree theorem. At omega = 2 the block heuristic admits D = 4 at m >= 8 with margins {', '.join(f'{t3b[m]:+.1f} (m={m})' for m in t3b)} bits per attempt (T3), and 2.2-5.9 bits in total time after l re-optimisation (T5a).")
    nx_lit = semaev_time_crossing(3.0, True, 0.0)
    nx_best = semaev_time_crossing(2.0, True, LOG2_BITOPS_PER_RHO, k_rule="cap")
    nx_b237 = semaev_time_crossing(2.37, True, LOG2_BITOPS_PER_RHO, k_rule="cap")
    nx_full = semaev_time_crossing(2.0, False, LOG2_BITOPS_PER_RHO, k_rule="cap")
    pr(f"6. Asymptotically, if D = 4 stayed bounded for all m, the family is Semaev's 2^(1.6986 sqrt(n ln n)) and the finite-n verdict is set by the polynomial cofactor cols^omega. Time-only it crosses 2^(n/2) at n = {nx_lit} in Semaev's own units (omega = 3, n^12 block, k = n/m). Under the single most IC-favourable reading here (block heuristic AND omega = 2 AND 2^16.1 bit-ops per rho step credited, cap rule) the crossing is n = {nx_best}, i.e. n = 131 is ~6 bits PAST it -- that is exactly the T5a block cells; raise omega to 2.37 and the crossing moves to n = {nx_b237} (margin -4.5 at 131); use the full variable count at omega = 2 and it is n = {nx_full}. Under time x memory the crossing against 6nW is n ~ 460-520 in the program's convention (reproduced: 518 / 460) and n >= 244 under every cap-rule variant; n = 131 is below all of them.")
    pr("7. What would it take, in one line: a closure that refutes UNSAT descended systems at degree 4 with an elimination that costs no more than cols^2.0 bit operations (omega = 2) AND whose cost scales with one 2n-variable block rather than with the full (m-1)n-variable chain AND m >= 10 (factor base 2^11-2^15, chain of 8-14 auxiliary field elements), AND the time x memory metric waived. Remove any one of the three conjuncts and no cell beats rho 2^60.81 on ECC2K-130.")
    return "\n".join(out)


if __name__ == "__main__":
    text = main()
    print(text)
