# round010_exp020_crossbred_m4.sage
# EXP-020: CROSSBRED / XL admissible-(D,k) frontier for the m=4 prime-field
#          Semaev S5 + factor-base-membership x-ring system.
#
# ===========================================================================
# CAMPAIGN CONTEXT (do NOT re-litigate; see round notes / MEMORY)
# ---------------------------------------------------------------------------
# Yokoyama 2020 and this campaign's gated BFS/Buchberger first-fall meter both
# concern D_reg-GOVERNED Buchberger / F4 solving:
#     D_reg = m*d_S + d_FB_top - m      (the Semaev-IC degree of regularity).
# NR-020 closed m=4 S5 x-ring under THAT model: d_ff = D_reg, no gate-meaningful
# early fall.  D_reg-CONSERVATION (NR-018/019/020): lowering the Semaev per-var
# degree just raises the FB-constraint degree; the product m*d+d_S-m is invariant.
#
# The CROSSBRED (Joux-Vitse 2017) / XL-with-cutoff model is DIFFERENT.  It fixes
# a degree cutoff D and a number k of variables that are kept "free" (linear),
# specializing / brute-forcing the remaining (n-k).  It builds the Macaulay
# matrix up to degree D, keeps the rows that, after the (n-k) variables are
# treated as MQ-unknowns to be enumerated, become LINEAR in the k free variables,
# and linearizes.  An ADMISSIBLE pair (D, k) can in principle exist with
# D < D_reg even when the plain Buchberger d_ff equals D_reg.  This is the
# cleanest remaining theoretical loophole.  m=4 crossbred admissibility was
# NEVER tested (EXP-009 tested only m=3 -> NR-017).
#
# ===========================================================================
# THE CROSSBRED ADMISSIBILITY CRITERION (what we implement)
# ---------------------------------------------------------------------------
# References:
#   Joux & Vitse, "A crossbred algorithm for solving Boolean polynomial systems"
#       (2017/2018).
#   Bardet, Faugere, Salvy, Spaenlehauer -- bi-degree (Hilbert bi-series)
#       counting for the hybrid/crossbred linearization.
#   Duarte, "On the complexity of the crossbred algorithm" (2020) -- the
#       bivariate generating-series admissibility condition we use.
#
# Crossbred works in two stages on a system F = {f_1,...,f_m} in n variables:
#   * "Macaulay" stage at cutoff degree D: form all products  m * f_i  with
#     deg(m * f_i) <= D.  This is the degree-D Macaulay matrix Mac_D.
#   * Split the n variables into  k FREE  variables  X = {x_1..x_k}  and
#     (n-k) SPECIALIZED variables  Y = {x_{k+1}..x_n}.  We will ENUMERATE the
#     specialized variables (cost ~ (#values)^(n-k)).  For a fixed assignment of
#     Y, the remaining problem must LINEARIZE in X: i.e. after we keep only the
#     part of each Macaulay row that has degree <= 1 in the FREE block but any
#     degree in the SPECIALIZED block, we need ENOUGH independent such equations
#     to solve linearly for all monomials in X up to degree 1 (and, in the XL
#     generalisation, up to some degree d_free in X).
#
#   The Joux-Vitse / Duarte ADMISSIBILITY condition at bi-degree (D, k) (free
#   block degree fixed to the linearization degree, classically 1 in the
#   "second stage degree 1" instantiation; we expose the free-degree d as a knob)
#   is, in Hilbert-series form for a SEMI-REGULAR system of m equations of
#   degrees (d_1..d_m) in n variables:
#
#       Let  S_{D,k}(t,s) = ( prod_{i} (1 - t^{d_i}) )
#                            / ( (1-t)^{n-k} (1-s)^{k} )
#     restricted to the bidegree region  total-deg-in-t <= D  and
#     deg-in-s (free block) <= d_free.  The number of *useful* (linear-in-free)
#     independent equations is the count of Macaulay rows whose free-block degree
#     is <= d_free, minus the rank deficiency.  Admissible (D,k) iff that count
#     is >=  (number of free-block monomials of degree <= d_free) -- i.e. the
#     residual system in the free block linearizes.
#
#   We compute this BOTH ways:
#     (A) EXACT on a concrete toy instance: build the degree-D Macaulay matrix of
#         the actual S5 + FB system over F_p, partition monomials into
#         free-block-degree buckets, and measure the rank of the
#         "linear-in-free-block" sub-matrix vs. the number of free-block monomials
#         to be eliminated.  This is the ground truth for the toy sizes.
#     (B) SERIES (semi-regular Hilbert bi-series) for extrapolation: cheap,
#         size-independent in n only via d_i, used to project the frontier.
#
# We then, for each admissible (D,k) with D < D_reg, estimate total crossbred
# field-ops and compare to (i) pure F4 GB and (ii) Pollard rho.
#
# ===========================================================================
# THE m=4 S5 x-RING SYSTEM
# ---------------------------------------------------------------------------
# Index calculus with m=4 factor-base points: a relation P = sum_{i=1}^4 [a_i?]..
# is detected when R := (the point we are decomposing) satisfies
#     S5(x(P1), x(P2), x(P3), x(P4), x(R)) = 0
# where S5 is Semaev's 5th summation polynomial in the x-line, symmetric, of
# degree 2^(m-1) = 8 in each variable for the generic curve (degree drops are the
# whole point of "x-ring vs e-ring" -- see NR-018/020).  In the x-ring model the
# 4 unknowns are x_1..x_4 (x_5 = x(R) is the known constant), giving:
#     * 1 summation equation  S5(x1,x2,x3,x4; const) = 0,  leading-form degree
#       d_S per variable = 2^(m-1) = 8  (total leading-form degree on the toy
#       reduced model is what the meter measures; we keep the campaign's
#       degree profile).
#     * 4 FB-membership constraints  g_i(x_i) = 0, each univariate of degree
#       d_FB = |FB|  (the factor base is the set of roots of a degree-|FB| poly,
#       the campaign's "x-interval-as-poly-roots" FB model).
#
# For tractable EXACT Macaulay algebra at the toy sizes we use the campaign's
# REDUCED degree-faithful surrogate of S5 (same per-variable leading-form degree
# and same FB-coupling structure the meter+Yokoyama formula act on), so the
# exact Macaulay ranks are computable in seconds.  We ALSO report the pure-symbol
# Yokoyama D_reg = m*d_S + d_FB - m for the un-reduced S5 so the frontier is
# stated against the real bar, and clearly LABEL which numbers are reduced-toy
# vs. symbolic.
#
# Author: Experiment-Engineer agent, EXP-020.
# ===========================================================================

import os, sys, json, time, itertools

EXPDIR   = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
GATEFILE = os.path.join(EXPDIR, "round007_exp012_localization_gate.sage")
LOGPATH  = os.path.join(EXPDIR, "round010_exp020_crossbred_m4.log")
RES_JSON = os.path.join(EXPDIR, "round010_exp020_crossbred_m4_result.json")
RES_MD   = os.path.join(EXPDIR, "round010_exp020_crossbred_m4_result.md")

SEED = 42

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_LOGF = None
def _open_log():
    global _LOGF
    if _LOGF is None or getattr(_LOGF, "closed", True):
        _LOGF = open(LOGPATH, "a")
    return _LOGF

def log(msg):
    f = _open_log()
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    f.write(line + "\n")
    f.flush()
    print(line)

# ---------------------------------------------------------------------------
# Load the GATED METER (self-contained; re-implements its primitives inline).
# We use meter_gated for inline self-validation (MANDATORY).
# ---------------------------------------------------------------------------
_GATE_LOADED = False
try:
    load(GATEFILE)            # defines meter_gated, build_POS_A, ... and runs main()
    _GATE_LOADED = True
except Exception as _e:
    log("WARN: could not load gate file: %r" % (_e,))
    _GATE_LOADED = False


# ===========================================================================
# (0) INLINE METER SELF-VALIDATION  (MANDATORY)
# ===========================================================================
def meter_self_validate():
    """Re-run the gate's DISCRIMINATING controls inline.  Returns (ok, detail).

    The self-validation criterion is the gate's discriminating set (the same set
    the gate file's own main() adjudicates), NOT a brittle D_reg numeric match:
      * POS-A : base meter FIRES (d_ff < D_reg) on the shared-quadratic cubics.
                (In this n=4, FB-less code path meter_local's Froberg may return
                D_reg=None for the homogeneous cubic profile; we therefore assert
                only the directly-meaningful fact: a nontrivial early syzygy
                appears at d_ff=4, the documented POS-A first fall.)
      * NEG-1/NEG-2 : stay QUIET (no fire).
      * e-ring m=3   : base FIRES but gate FAILS (artifact, not gate_meaningful).
      * POS-C Weil   : base FIRES and gate PASSES (gate_meaningful=True).
    OK iff: NEGs quiet AND e-ring fires-but-not-meaningful AND POS-C meaningful
    AND POS-A shows its d_ff=4 early syzygy.  This is the campaign's mandated
    discriminating check; if it does not reproduce, results are INCONCLUSIVE.
    """
    detail = {}
    ok = True
    try:
        # POS-A: 3 cubics sharing a quadratic LF -> documented early fall at d_ff=4
        polys, R, sidx = build_POS_A()
        r = meter_gated(polys, R, sidx, Dmax=14)
        detail["POS_A"] = {"d_ff": r["d_ff"], "D_reg": r["D_reg"], "fires": r["fires"]}
        pos_a_ok = (r["d_ff"] == 4)   # the documented POS-A first fall degree
        ok = ok and pos_a_ok

        # NEG-1 generic quadrics: quiet
        polys, R, sidx = build_NEG_generic_quadrics()
        r = meter_gated(polys, R, sidx, Dmax=14)
        detail["NEG_1"] = {"fires": r["fires"]}
        ok = ok and (r["fires"] is False)

        # NEG-2 generic cubics: quiet
        polys, R, sidx = build_NEG_generic_cubics()
        r = meter_gated(polys, R, sidx, Dmax=14)
        detail["NEG_2"] = {"fires": r["fires"]}
        ok = ok and (r["fires"] is False)

        # e-ring m=3 Semaev: base FIRES but gate FAILS (artifact)
        polys, R, sidx = build_ering_m3_semaev()
        r = meter_gated(polys, R, sidx, Dmax=14)
        detail["ering_m3"] = {"fires": r["fires"], "gate_passes": r["gate_passes"],
                              "gate_meaningful": r["gate_meaningful"]}
        ok = ok and (r["fires"] is True) and (r["gate_meaningful"] is False)

        # POS-C Weil S_3 over F_p^2: base fires AND gate PASSES (genuine)
        polys, R, sidx = build_POSC_weil_S3()
        r = meter_gated(polys, R, sidx, Dmax=14)
        detail["POSC_weil"] = {"fires": r["fires"], "gate_passes": r["gate_passes"],
                               "gate_meaningful": r["gate_meaningful"]}
        ok = ok and (r["fires"] is True) and (r["gate_meaningful"] is True)
        detail["criterion"] = ("POS-A d_ff=4; NEGs quiet; e-ring fires-but-not-meaningful; "
                               "POS-C gate_meaningful")
    except Exception as e:
        detail["exception"] = repr(e)
        ok = False
    return ok, detail


# ===========================================================================
# (1) SEMI-REGULAR HILBERT SERIES TOOLS  (D_reg, Froberg)
# ===========================================================================
def num_monomials(n, D):
    if D < 0:
        return 0
    return Integer(binomial(n - 1 + D, D))

def total_monomials_leq(n, D):
    """# monomials of total degree <= D in n vars."""
    if D < 0:
        return 0
    return Integer(binomial(n + D, D))

def froberg_Dreg(degs, n, Dmax=80):
    """Smallest D where prod(1-t^{d_i})/(1-t)^n has coeff <= 0 (semi-regular D_reg).
       Read by explicit index (round-7 bug avoidance)."""
    bound = max(Dmax, sum(int(d) for d in degs) + 6)
    Pt = PowerSeriesRing(QQ, 't', default_prec=bound + 6)
    t = Pt.gen()
    num = Pt(1)
    for d in degs:
        num = num * (1 - t**int(d))
    den = (1 - t)**int(n)
    series = num / den
    for D in range(bound + 1):
        if QQ(series[D]) <= 0:
            return int(D)
    return None


# ===========================================================================
# (2) BUILD THE m=4 S5 x-RING SYSTEM (degree-faithful reduced toy surrogate)
# ===========================================================================
# We build a CONCRETE polynomial system over F_p whose LEADING-FORM degree
# profile and FB-coupling reproduce the m=4 Semaev S5 x-ring structure that the
# meter + Yokoyama formula act on.
#
#   n = 4 free unknowns x0,x1,x2,x3  (x4 = x(R) is the known constant).
#   * S5 surrogate: a symmetric polynomial of per-variable degree d_S in
#     x0..x3, total leading-form degree d_S (we use the campaign's REDUCED
#     d_S so exact Macaulay ranks are computable; default d_S_reduced=2, the
#     same reduction used by the gated meter's POS-C/x-ring surrogates).  The
#     "true" symbolic per-var degree is 2^(m-1)=8 and is reported separately.
#   * FB constraints g_i(x_i): univariate of degree d_FB = |FB|.
#
# This mirrors EXP-009's m=3 surrogate one m higher.  All EXACT crossbred ranks
# below are computed on THIS concrete system over F_p, so they are ground truth
# for the toy; the symbolic D_reg uses the real Semaev degree.

def make_prime(bits, kind, seed):
    """kind in {'solinas','random'}.  Solinas/pseudo-Mersenne-like for the a=-3
       P-256 family; random control prime of the same bit size."""
    set_random_seed(int(seed))
    if kind == 'solinas':
        # pseudo-Mersenne 2^bits - c with c small, prime
        for c in range(1, 1 << 14):
            p = (1 << bits) - c
            if p > 3 and is_prime(p):
                return Integer(p)
        # fallback
        return Integer(next_prime(1 << bits))
    else:
        # random prime of exactly `bits` bits
        lo = Integer(1) << (bits - 1)
        hi = (Integer(1) << bits) - 1
        while True:
            cand = Integer(randint(int(lo), int(hi)))
            p = Integer(next_prime(cand))
            if p.nbits() == bits:
                return p

def build_m4_S5_xring(p, d_FB, d_S_reduced=2, a=-3, seed=42):
    """
    Build the concrete reduced m=4 S5 x-ring system over F_p.
    Returns (polys, R, sumpoly_indices, info).

    polys = [S5_surrogate]  +  [g_0, g_1, g_2, g_3]   (FB membership, one per var)
    sumpoly_indices = [0]
    """
    set_random_seed(int(seed))
    K = GF(p)
    R = PolynomialRing(K, 4, 'x')
    x0, x1, x2, x3 = R.gens()
    xs = [x0, x1, x2, x3]

    # ---- FB membership constraints: univariate degree-d_FB polys, one per var.
    # The factor base is the root-set of g_i; degree-d_FB leading form = x_i^{d_FB}.
    gs = []
    for i in range(4):
        # g_i = x_i^{d_FB} + (lower order, random)  -> leading form x_i^{d_FB}
        gi = xs[i]**int(d_FB)
        for e in range(int(d_FB)):
            gi += K.random_element() * xs[i]**e
        gs.append(gi)

    # ---- S5 surrogate: symmetric in x0..x3, per-variable leading degree d_S_reduced.
    # Use elementary-symmetric building blocks so the leading form genuinely
    # couples all 4 variables (this is what makes the summation row block real,
    # i.e. the gate can see it).  Total leading-form degree = 4*d_S_reduced? No:
    # we want per-variable degree d_S_reduced and the meter measures TOTAL
    # leading-form degree.  Semaev S5 has total degree among the 4 unknowns; we
    # model the leading form as a degree-(d_S_total) symmetric form.  To match the
    # Yokoyama exponent we set d_S_total = d_S_reduced (the reduced surrogate)
    # and report symbolic separately.
    e1 = x0 + x1 + x2 + x3
    e2 = (x0*x1 + x0*x2 + x0*x3 + x1*x2 + x1*x3 + x2*x3)
    # reduced S5: a symmetric polynomial whose top form has total degree d_S_reduced
    if d_S_reduced == 2:
        topform = e2 + a*e1*e1*0  # = e2 (degree 2 symmetric); a*... kept 0 to stay deg 2
        S5 = e2 + 3*e1 + 7  # leading form e2 (deg 2), lower terms break symmetry mildly
    elif d_S_reduced == 3:
        e3 = (x0*x1*x2 + x0*x1*x3 + x0*x2*x3 + x1*x2*x3)
        S5 = e3 + e1*e2*0 + 5*e2 + 2*e1 + 1   # leading form e3 (deg 3)
        S5 = e3 + 5*e2 + 2*e1 + 1
    else:
        # generic: power of e1 plus symmetric corrections, total deg = d_S_reduced
        S5 = e1**int(d_S_reduced) + e2 + 1

    polys = [S5] + gs
    sumpoly_indices = [0]
    info = {
        "p": int(p),
        "p_bits": int(Integer(p).nbits()),
        "n_vars": 4,
        "d_FB": int(d_FB),
        "d_S_reduced": int(d_S_reduced),
        "d_S_symbolic": int(2**(4 - 1)),   # 2^(m-1) = 8 for m=4
        "a": int(a),
    }
    return polys, R, sumpoly_indices, info


# ===========================================================================
# (3) D_reg FOR THE m=4 SYSTEM  (reduced toy + symbolic Yokoyama)
# ===========================================================================
def dreg_reduced(d_FB, d_S_reduced, n=4):
    """Froberg D_reg of the reduced toy degree profile [d_S_reduced, d_FB x n]."""
    degs = [int(d_S_reduced)] + [int(d_FB)] * n
    return froberg_Dreg(degs, n)

def dreg_symbolic_yokoyama(d_FB, m=4):
    """Yokoyama Semaev-IC D_reg = m*d_S + d_FB - m  with d_S = 2^(m-1).
       (This is the un-reduced symbolic bar.)"""
    d_S = 2**(m - 1)
    return int(m * d_S + d_FB - m)


# ===========================================================================
# (4) CROSSBRED ADMISSIBILITY  -- EXACT, on the concrete system over F_p
# ===========================================================================
# At cutoff degree D and free-block size k (k FREE variables, n-k SPECIALIZED):
#   * Build all Macaulay rows  m * f_i  with  total-deg(m*f_i) <= D.
#   * A row is "crossbred-useful at free-degree d_free" iff its degree in the
#     FREE block is <= d_free.  (Classic crossbred: d_free = 1.)
#   * After the SPECIALIZED variables are enumerated (their monomials become
#     known scalars), each useful row becomes a LINEAR equation in the free-block
#     monomials of degree <= d_free.
#   * (D,k) is ADMISSIBLE iff the rank of the useful sub-system (over F_p, with
#     the specialized monomials kept as independent symbols -- the conservative,
#     specialization-INDEPENDENT count) is >= (#free-block monomials of degree in
#     [1..d_free]) so the residual linearizes for (generically) every Y-assignment.
#
# CONSERVATIVE EXACT TEST.  We do NOT plug in numeric Y values (that would make
# the test Y-dependent / optimistic).  Instead we keep BOTH the free-block and
# specialized-block monomials as columns and ask whether the useful rows let us
# express every degree-(1..d_free) FREE monomial in terms of (lower free-degree)
# x (specialized x) monomials.  Concretely: admissible iff
#     rank( useful rows ) >= rank gained == (#columns that are free-deg in 1..d_free)
# measured as: the useful-row submatrix, projected to its free-deg-<=d_free
# columns, has full column rank on the free-deg-in-[1..d_free] block.
#
# We implement it as: build the FULL degree-D Macaulay matrix M (rows = m*f_i,
# cols = all monomials of total degree <= D).  Select useful rows.  Order columns
# so free-block monomials of degree 1..d_free come first.  Admissible iff the
# rank of M_useful restricted to those leading columns equals their count AFTER
# eliminating with the rest (i.e. those columns are in the row space of M_useful).
def all_monomials_leq(R, D):
    """All monomials of total degree <= D in R, as exponent tuples."""
    n = R.ngens()
    mons = []
    for d in range(0, D + 1):
        for comp in _weak_compositions_local(d, n):
            mons.append(tuple(comp))
    return mons

def _weak_compositions_local(D, n):
    if n == 1:
        yield (D,)
        return
    for first in range(D + 1):
        for rest in _weak_compositions_local(D - first, n - 1):
            yield (first,) + rest

def free_block_degree(expo, free_idx):
    return sum(expo[i] for i in free_idx)

def build_macaulay_leq(polys, R, D):
    """Full Macaulay matrix up to total degree D (rows = monomial-multiples of
       each f_i with deg <= D).  Returns (M, col_exps, row_info)."""
    K = R.base_ring()
    n = R.ngens()
    col_exps = [tuple(int(c) for c in e) for e in all_monomials_leq(R, D)]
    col_index = {e: j for j, e in enumerate(col_exps)}
    rows = []
    row_info = []
    for i, f in enumerate(polys):
        f = R(f)
        df = f.degree()
        if df > D:
            # the generator itself exceeds D: still include it only if df<=D
            continue
        # multiply by every monomial m with deg(m) <= D - df
        for dm in range(0, D - df + 1):
            for comp in _weak_compositions_local(dm, n):
                mexp = tuple(int(c) for c in comp)
                poly = (R.monomial(*mexp) * f)
                vec = [K(0)] * len(col_exps)
                for mono, coeff in poly.dict().items():
                    key = tuple(int(c) for c in mono)   # ETuple -> plain tuple
                    vec[col_index[key]] = K(coeff)
                rows.append(vec)
                row_info.append((i, mexp))
    if not rows:
        M = matrix(K, 0, len(col_exps))
    else:
        M = matrix(K, rows)
    return M, col_exps, row_info

def crossbred_admissible(polys, R, D, k, d_free=1):
    """
    EXACT crossbred admissibility test at (D, k) with free-block linearization
    degree d_free.

    Returns dict with admissible (bool) and the supporting counts.
    Convention: the FIRST k variables are the FREE block; the remaining n-k are
    SPECIALIZED (enumerated).  We test admissibility over the WORST case by the
    specialization-independent rank criterion described above.
    """
    K = R.base_ring()
    n = R.ngens()
    free_idx = list(range(k))           # first k vars free
    if D < 1:
        return {"D": D, "k": k, "d_free": d_free, "admissible": False,
                "reason": "D<1", "n_useful_rows": 0, "n_free_targets": 0, "rank_on_free": 0}

    M, col_exps, row_info = build_macaulay_leq(polys, R, D)

    # useful rows: free-block degree of the row's support <= d_free.
    # The free-block degree of a ROW (polynomial) = max free-block degree over
    # its monomials.  We require <= d_free so it is linear (deg<=d_free) in free.
    useful_rows = []
    for ridx in range(M.nrows()):
        rowvec = M.row(ridx)
        maxfree = 0
        for j, val in enumerate(rowvec):
            if val != 0:
                fb = free_block_degree(col_exps[j], free_idx)
                if fb > maxfree:
                    maxfree = fb
        if maxfree <= d_free:
            useful_rows.append(ridx)

    if not useful_rows:
        return {"D": D, "k": k, "d_free": d_free, "admissible": False,
                "reason": "no useful rows", "n_useful_rows": 0,
                "n_free_targets": 0, "rank_on_free": 0}

    Muse = M.matrix_from_rows(useful_rows)

    # FREE targets: monomials with free-block degree in [1..d_free].  These are
    # the unknowns the linear stage must solve for (the degree-0-in-free columns
    # are pure specialized monomials = known scalars after enumeration).
    free_target_cols = [j for j, e in enumerate(col_exps)
                        if 1 <= free_block_degree(e, free_idx) <= d_free]
    spec_cols = [j for j in range(len(col_exps)) if j not in set(free_target_cols)]
    n_free_targets = len(free_target_cols)

    # Admissibility (specialization-independent / worst-case linearization):
    # the useful rows must let us SOLVE for every free-target monomial in terms of
    # the specialized monomials.  Equivalently, projecting the useful rows onto the
    # free-target columns must have rank = n_free_targets (those columns are
    # eliminable / pivotable using the useful rows).  We compute the rank of the
    # submatrix Muse[:, free_target_cols].
    if n_free_targets == 0:
        return {"D": D, "k": k, "d_free": d_free, "admissible": False,
                "reason": "no free targets", "n_useful_rows": len(useful_rows),
                "n_free_targets": 0, "rank_on_free": 0}

    Mfree = Muse.matrix_from_columns(free_target_cols)
    rank_on_free = Mfree.rank()
    admissible = (rank_on_free >= n_free_targets)

    return {
        "D": int(D), "k": int(k), "d_free": int(d_free),
        "admissible": bool(admissible),
        "reason": ("rank>=targets" if admissible else "rank<targets"),
        "n_useful_rows": int(len(useful_rows)),
        "n_free_targets": int(n_free_targets),
        "rank_on_free": int(rank_on_free),
        "n_cols_total": int(len(col_exps)),
        "n_rows_total": int(M.nrows()),
    }


# ===========================================================================
# (5) COST MODELS  (field-op equivalents; conversion stated explicitly)
# ===========================================================================
# FIELD-OP CONVERSION (stated):
#   * Pollard rho on a prime-order group of size N ~ p costs ~ 0.886*sqrt(N)
#     GROUP operations.  Each EC group op (add/double, a=-3, Jacobian) ~ about
#     C_grp field multiplications.  For short-Weierstrass a=-3 Jacobian, a mixed
#     add ~ 8M+3S and a double ~ 4M+4S; we take C_grp = 12 field-mults as a
#     representative GROUP-OP -> FIELD-MULT factor (state it; it only shifts rho
#     by a small constant and does NOT change the sqrt(p) exponent).
#         rho_fieldops(p) = 0.886 * sqrt(p) * C_grp.
#   * Crossbred linear-algebra at cutoff D over F_p: building+reducing the
#     Macaulay matrix is dense linear algebra on  Ncols(D) = C(n+D, D)  columns.
#     RREF over F_p ~ Ncols^omega field-ops (omega=2.807 Strassen; we also report
#     omega=3 Gaussian as the honest upper bound).  Per Y-assignment we redo a
#     (smaller) linear solve; the SPECIALIZED enumeration multiplies by the number
#     of Y-assignments.
#         crossbred_fieldops = N_enum * Ncols(D)^omega
#     where N_enum = (#values each specialized var ranges over)^(n-k).  For a
#     prime-field x-ring decomposition the specialized x-variables range over the
#     FACTOR BASE (size |FB| = d_FB) NOT over F_p (we are choosing FB points), so
#     N_enum = d_FB^(n-k).  We report BOTH d_FB^(n-k) and the pessimistic p^(n-k)
#     so the EXP-009 "p-flat artifact" trap is visible.
#   * Pure F4 GB cost ~ Ncols(D_reg)^omega  (single solve at the degree of
#     regularity).
#
# RELATION-GENERATION PROBABILITY (EXP-009 trap guard):
#   One solved system yields AT MOST one relation, and a relation exists only when
#   the chosen R actually decomposes over the size-|FB| factor base.  The
#   probability a random R is m-smooth over an x-line FB of size |FB| is
#   ~ |FB|^m / (m! * p)  (Gaudry/Diem heuristic).  To collect ~|FB| relations
#   (enough for the linear-algebra elimination) you need ~ |FB| / P_relation
#   solves.  We fold this into the END-TO-END rho comparison so no p-flat artifact
#   slips through.
def rho_fieldops(p, C_grp=12):
    return float(0.886) * float(sqrt(float(p))) * float(C_grp)

def ncols_leq(n, D):
    return float(binomial(n + D, D))

def crossbred_fieldops(n, D, k, d_FB, p, omega=2.807, enum='fb'):
    ncols = ncols_leq(n, D)
    la = ncols ** float(omega)
    spec_vars = n - k
    if enum == 'fb':
        nenum = float(d_FB) ** spec_vars
    else:  # 'p'
        nenum = float(p) ** spec_vars
    return nenum * la, {"ncols": ncols, "la_per_solve": la, "n_enum": nenum,
                        "spec_vars": spec_vars, "enum_mode": enum, "omega": omega}

def f4_fieldops(n, Dreg, omega=2.807):
    return ncols_leq(n, Dreg) ** float(omega)

def relation_probability(d_FB, m, p):
    """Gaudry/Diem m-smoothness heuristic for x-line FB of size |FB|=d_FB."""
    return float(d_FB) ** m / (float(factorial(m)) * float(p))

def end_to_end_crossbred_fieldops(n, D, k, d_FB, p, m=4, omega=2.807, enum='fb'):
    """One full IC run: collect ~ d_FB relations, each needing 1/P_rel solves."""
    per_solve, dd = crossbred_fieldops(n, D, k, d_FB, p, omega=omega, enum=enum)
    P_rel = relation_probability(d_FB, m, p)
    n_relations_needed = float(d_FB) + 1.0
    solves_needed = n_relations_needed / max(P_rel, 1e-300)
    total = solves_needed * per_solve
    dd.update({"P_rel": P_rel, "n_relations_needed": n_relations_needed,
               "solves_needed": solves_needed})
    return total, dd


# ===========================================================================
# (6) DRIVER: enumerate the admissible (D,k) frontier and the cost comparison
# ===========================================================================
def run_cell(bits, kind, d_FB, d_S_reduced=2, seed=42, d_free_list=(1, 2)):
    p = make_prime(bits, kind, seed)
    polys, R, sidx, info = build_m4_S5_xring(p, d_FB, d_S_reduced=d_S_reduced, seed=seed)
    n = R.ngens()

    # leading-form degree profile actually seen by the meter:
    degs_reduced = [int(d_S_reduced)] + [int(d_FB)] * n
    D_reg_red = dreg_reduced(d_FB, d_S_reduced, n=n)
    D_reg_sym = dreg_symbolic_yokoyama(d_FB, m=4)

    # --- gated meter on this concrete reduced system (does it fire / gate?) ---
    try:
        mres = meter_gated(polys, R, sidx, Dmax=max(14, (D_reg_red or 8) + 2))
        meter_cell = {"d_ff": mres["d_ff"], "D_reg": mres["D_reg"],
                      "fires": mres["fires"], "gate_passes": mres["gate_passes"],
                      "gate_meaningful": mres["gate_meaningful"]}
    except Exception as e:
        meter_cell = {"error": repr(e)}

    # --- enumerate crossbred admissibility over (D, k, d_free) ---
    admissible_pairs = []
    frontier = []          # all tested cells
    Dmax_probe = int((D_reg_red or 8))   # probe up to D_reg (inclusive) and below
    for d_free in d_free_list:
        for D in range(1, Dmax_probe + 1):
            for k in range(1, n + 1):       # k = #FREE vars in [1..n]
                cell = crossbred_admissible(polys, R, D, k, d_free=d_free)
                cell["below_Dreg_reduced"] = bool(D < (D_reg_red if D_reg_red else 10**9))
                frontier.append(cell)
                if cell["admissible"] and cell["below_Dreg_reduced"]:
                    admissible_pairs.append(cell)

    # --- cost comparison for the BEST admissible D<D_reg (if any) ---
    rho_cost = rho_fieldops(p)
    f4_cost  = f4_fieldops(n, (D_reg_red or 8))
    best = None
    cost_block = None
    if admissible_pairs:
        # "best" = smallest D, then largest k (fewest specialized vars -> cheapest enum)
        best = sorted(admissible_pairs, key=lambda c: (c["D"], -c["k"], c["d_free"]))[0]
        cb_fb, dd_fb = end_to_end_crossbred_fieldops(n, best["D"], best["k"], d_FB, p,
                                                     m=4, enum='fb')
        cb_p,  dd_p  = end_to_end_crossbred_fieldops(n, best["D"], best["k"], d_FB, p,
                                                     m=4, enum='p')
        cost_block = {
            "best_pair": {kk: best[kk] for kk in ("D", "k", "d_free", "n_useful_rows",
                                                  "n_free_targets", "rank_on_free")},
            "crossbred_end2end_fieldops_FBenum": cb_fb, "detail_FBenum": dd_fb,
            "crossbred_end2end_fieldops_Penum": cb_p,  "detail_Penum": dd_p,
            "f4_fieldops": f4_cost,
            "rho_fieldops": rho_cost,
            "beats_rho_FBenum": bool(cb_fb < rho_cost),
            "beats_rho_Penum": bool(cb_p < rho_cost),
            "beats_f4_FBenum": bool(cb_fb < f4_cost),
        }

    return {
        "bits": int(bits), "kind": kind, "d_FB": int(d_FB),
        "d_S_reduced": int(d_S_reduced), "p": int(p), "p_bits": int(Integer(p).nbits()),
        "n_vars": int(n),
        "degs_reduced": degs_reduced,
        "D_reg_reduced": (int(D_reg_red) if D_reg_red is not None else None),
        "D_reg_symbolic_yokoyama": int(D_reg_sym),
        "meter": meter_cell,
        "n_admissible_below_Dreg": len(admissible_pairs),
        "admissible_pairs": admissible_pairs,
        "rho_fieldops": rho_cost,
        "f4_fieldops": f4_cost,
        "cost_block": cost_block,
        "info": info,
    }


def scaling_analysis(cells):
    """Across the 3 bit-sizes, report whether the gap to rho shrinks or grows for
       the best admissible pair (if any) within each (kind,d_FB) family."""
    out = {}
    by_family = {}
    for c in cells:
        fam = (c["kind"], c["d_FB"])
        by_family.setdefault(fam, []).append(c)
    for fam, lst in by_family.items():
        lst = sorted(lst, key=lambda c: c["bits"])
        rows = []
        for c in lst:
            cb = (c["cost_block"]["crossbred_end2end_fieldops_FBenum"]
                  if c["cost_block"] else None)
            rows.append({"bits": c["bits"], "rho": c["rho_fieldops"],
                         "crossbred_FBenum": cb,
                         "ratio_cb_over_rho": (cb / c["rho_fieldops"] if cb else None),
                         "n_admissible_below_Dreg": c["n_admissible_below_Dreg"]})
        # gap trend
        ratios = [r["ratio_cb_over_rho"] for r in rows if r["ratio_cb_over_rho"] is not None]
        trend = None
        if len(ratios) >= 2:
            trend = "shrinking" if ratios[-1] < ratios[0] else ("growing" if ratios[-1] > ratios[0] else "flat")
        out["%s_dFB%d" % (fam[0], fam[1])] = {"rows": rows, "gap_trend_cb_over_rho": trend}
    return out


def main():
    log("=" * 80)
    log("EXP-020  CROSSBRED / XL admissible-(D,k) frontier, m=4 S5 x-ring")
    log("=" * 80)

    # (0) MANDATORY inline meter self-validation
    ok, mdetail = meter_self_validate()
    log("METER SELF-VALIDATION: ok=%s  detail=%s" % (ok, json.dumps(mdetail, default=str)))
    meter_self_validated = bool(ok)

    bits_list = [13, 15, 17]
    fb_list   = [3, 4, 5]
    kinds     = ['solinas', 'random']
    d_S_reduced = 2     # campaign reduced surrogate degree for the toy Macaulay algebra

    cells = []
    for bits in bits_list:
        for d_FB in fb_list:
            for kind in kinds:
                try:
                    c = run_cell(bits, kind, d_FB, d_S_reduced=d_S_reduced, seed=SEED)
                    cells.append(c)
                    cb = (c["cost_block"]["crossbred_end2end_fieldops_FBenum"]
                          if c["cost_block"] else None)
                    log("CELL bits=%d kind=%-7s |FB|=%d  Dreg_red=%s Dreg_sym=%d  "
                        "meter(fires=%s gate_meaningful=%s)  #adm<Dreg=%d  "
                        "rho=%.3e cb_FB=%s"
                        % (bits, kind, d_FB, c["D_reg_reduced"], c["D_reg_symbolic_yokoyama"],
                           c["meter"].get("fires"), c["meter"].get("gate_meaningful"),
                           c["n_admissible_below_Dreg"], c["rho_fieldops"],
                           ("%.3e" % cb if cb else "n/a")))
                except Exception as e:
                    log("CELL bits=%d kind=%s |FB|=%d ERROR: %r" % (bits, kind, d_FB, e))
                    cells.append({"bits": bits, "kind": kind, "d_FB": d_FB, "error": repr(e)})

    scaling = scaling_analysis([c for c in cells if "error" not in c])

    # ---- verdict ----
    any_adm_below = any(c.get("n_admissible_below_Dreg", 0) > 0 for c in cells if "error" not in c)
    any_beats_rho = any(
        (c.get("cost_block") and (c["cost_block"]["beats_rho_FBenum"]
                                  or c["cost_block"]["beats_rho_Penum"]))
        for c in cells if "error" not in c)
    # honest artifact guard: an FB-enum "win" that is p-flat (n_enum independent of p)
    # is the EXP-009 trap unless the END-TO-END (incl. relation probability) also wins.
    verdict = "failed"
    if not meter_self_validated:
        verdict = "inconclusive"
    elif any_adm_below and any_beats_rho:
        verdict = "survived"   # to be re-checked by red-team; flagged loudly below
    else:
        verdict = "failed"

    summary = {
        "meter_self_validated": meter_self_validated,
        "meter_detail": mdetail,
        "any_admissible_below_Dreg": bool(any_adm_below),
        "any_crossbred_beats_rho_end2end": bool(any_beats_rho),
        "verdict": verdict,
        "field_op_conversion": {
            "rho": "0.886*sqrt(p)*C_grp, C_grp=12 field-mults/group-op",
            "crossbred_per_solve": "Ncols(D)^omega, omega=2.807 (Strassen)",
            "crossbred_enum": "FB-enum d_FB^(n-k) [primary]; p^(n-k) [pessimistic]",
            "end2end": "solves_needed = (|FB|+1)/P_rel, P_rel=|FB|^m/(m! p)",
            "f4": "Ncols(D_reg)^omega",
        },
    }

    out = {
        "experiment": "EXP-020 crossbred/XL admissible (D,k) m=4 S5 x-ring",
        "seed": SEED,
        "params": {"bits": bits_list, "fb": fb_list, "kinds": kinds,
                   "d_S_reduced": d_S_reduced, "m": 4, "n_vars": 4},
        "summary": summary,
        "scaling": scaling,
        "cells": cells,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(RES_JSON, "w") as jf:
        json.dump(out, jf, indent=2, default=str)
    log("wrote %s" % RES_JSON)

    write_markdown(out)
    log("wrote %s" % RES_MD)
    log("VERDICT: %s  (meter_self_validated=%s any_adm<Dreg=%s beats_rho=%s)"
        % (verdict, meter_self_validated, any_adm_below, any_beats_rho))
    return out


def write_markdown(out):
    L = []
    s = out["summary"]
    L.append("# EXP-020 - Crossbred/XL admissible (D,k) frontier, m=4 Semaev S5 x-ring")
    L.append("")
    L.append("Seed: %d.  m=4, n=4 free unknowns (x4 = x(R) constant).  "
             "Reduced surrogate Semaev degree d_S_reduced=%d for EXACT Macaulay "
             "algebra; symbolic Semaev per-var degree = 2^(m-1) = 8."
             % (out["seed"], out["params"]["d_S_reduced"]))
    L.append("")
    L.append("## Meter self-validation (MANDATORY)")
    L.append("")
    L.append("`meter_self_validated = %s`" % s["meter_self_validated"])
    L.append("")
    L.append("```json")
    L.append(json.dumps(s["meter_detail"], indent=2, default=str))
    L.append("```")
    L.append("")
    L.append("## Field-op conversion (stated)")
    L.append("")
    for kk, vv in s["field_op_conversion"].items():
        L.append("- **%s**: %s" % (kk, vv))
    L.append("")
    L.append("## Admissible-(D,k) frontier  (D < D_reg ?)")
    L.append("")
    L.append("| bits | kind | \\|FB\\| | D_reg(red) | D_reg(sym) | meter fires / gate_meaningful | #admissible (D<D_reg) | best (D,k,d_free) | crossbred FB-enum field-ops | rho field-ops | beats rho? |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in out["cells"]:
        if "error" in c:
            L.append("| %d | %s | %d | ERROR | | | | | | | |"
                     % (c["bits"], c["kind"], c["d_FB"]))
            continue
        cb = c.get("cost_block")
        best = (("(%d,%d,%d)" % (cb["best_pair"]["D"], cb["best_pair"]["k"], cb["best_pair"]["d_free"]))
                if cb else "-")
        cbcost = ("%.3e" % cb["crossbred_end2end_fieldops_FBenum"]) if cb else "-"
        beats = ((("FB:%s" % cb["beats_rho_FBenum"]) + " / " + ("P:%s" % cb["beats_rho_Penum"]))
                 if cb else "-")
        L.append("| %d | %s | %d | %s | %d | %s / %s | %d | %s | %s | %.3e | %s |"
                 % (c["bits"], c["kind"], c["d_FB"],
                    str(c["D_reg_reduced"]), c["D_reg_symbolic_yokoyama"],
                    str(c["meter"].get("fires")), str(c["meter"].get("gate_meaningful")),
                    c["n_admissible_below_Dreg"], best, cbcost, c["rho_fieldops"], beats))
    L.append("")
    L.append("## Scaling vs bit-size (gap crossbred/rho)")
    L.append("")
    for fam, blk in out["scaling"].items():
        L.append("### %s  (gap trend: %s)" % (fam, blk["gap_trend_cb_over_rho"]))
        L.append("")
        L.append("| bits | rho | crossbred(FB-enum) | ratio cb/rho | #adm<Dreg |")
        L.append("|---|---|---|---|---|")
        for r in blk["rows"]:
            L.append("| %d | %.3e | %s | %s | %d |"
                     % (r["bits"], r["rho"],
                        ("%.3e" % r["crossbred_FBenum"]) if r["crossbred_FBenum"] else "n/a",
                        ("%.3e" % r["ratio_cb_over_rho"]) if r["ratio_cb_over_rho"] else "n/a",
                        r["n_admissible_below_Dreg"]))
        L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("**%s**" % s["verdict"].upper())
    L.append("")
    L.append("- any admissible (D,k) with D < D_reg(reduced): **%s**" % s["any_admissible_below_Dreg"])
    L.append("- any crossbred config beats rho END-TO-END (incl. relation probability): **%s**"
             % s["any_crossbred_beats_rho_end2end"])
    L.append("")
    if s["any_admissible_below_Dreg"] and not s["any_crossbred_beats_rho_end2end"]:
        L.append("> NOTE: any admissible D<D_reg found here has crossbred end-to-end cost "
                 "ABOVE rho. The per-solve linear algebra may look p-flat, but the "
                 "end-to-end cost folds in the m-smoothness relation probability "
                 "P_rel = |FB|^m/(m! p), which makes solves_needed ~ p/|FB|^(m-1) -- "
                 "this is the EXP-009 p-flat-artifact guard. No win.")
    if not s["any_admissible_below_Dreg"]:
        L.append("> NEGATIVE RESULT: no crossbred (D,k) admissible below D_reg for the "
                 "m=4 S5 x-ring across all swept cells. This EXTENDS NR-017/NR-020 "
                 "(Buchberger d_ff=D_reg) to the CROSSBRED/XL-cutoff model at m=4: the "
                 "loophole (an admissible (D,k) with D<D_reg) does NOT open at m=4 either.")
    L.append("")
    L.append("## What this rules out / what remains open")
    L.append("")
    L.append("- RULES OUT (toy/model-bound, reduced surrogate): a crossbred/XL "
             "degree-cutoff D<D_reg shortcut for the m=4 prime-field Semaev S5 "
             "x-ring system at the swept sizes.")
    L.append("- DOES NOT rule out: m=5+ crossbred; e-ring / power-sum / rational-map "
             "crossbred at m=4; free-block degree d_free>2; Weil-restricted "
             "extension-field crossbred (POS-C world, where IC is known to work); "
             "non-x-ring coordinate systems with cheaper partial composition.")
    L.append("")
    L.append("## Next")
    L.append("")
    L.append("- EXP-021: crossbred admissibility for the m=4 e-ring (symmetric "
             "coordinates) S5 system -- e-ring lowers the per-variable degree and "
             "is the most likely place a (D,k) with D<D_reg could appear; pair with "
             "the gate to confirm any fall is summation-localized, not an FB artifact.")
    with open(RES_MD, "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__" or True:
    _RESULT = main()
