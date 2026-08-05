#!/usr/bin/env python3
"""
STAGE A -- TASK-20260803-db170f / BATCH-c45baf (batch 3 of 6) / GOAL-MLKEM-004

Replicate or kill the campaign's only positive separation
(RT-20260803-dc7568 section 4) on the NINE REPLICATE INSTANCES already
generated in BATCH-f75059.

SCOPE, binding on every number this script emits: m=35, n=25, d=60, q=127,
secret centred-binomial eta=2, error rounded-Gaussian sigma=2, g6k bgj1_sieve.
TOY SCALE. No ML-KEM break claim, no security proof, no FIPS 203 parameter set
affected or cleared, no speedup, no cost claim. AGENTS.md rule 12 UNMET and
UNWAIVED, inherited: this script changes the status of no EV-MLKEM-* record and
no KN-* entry. This script states OBSERVATIONS. It does not conclude that any
heuristic is validated or refuted.

------------------------------------------------------------------------------
WHAT IS FROZEN BEFORE THE RUN
------------------------------------------------------------------------------
The reference values come from the task card, which took them from
RT-20260803-dc7568 on the SINGLE primary instance:

    near-miss sd ratio            real 0.142888   rowperm 0.105408 +- 0.000991
                                                  (+35.6%)
    correct - best-of-8 near-miss real 0.001522   rowperm 0.001761 +- 0.000011
                                                  (-13.6%)
    1/sqrt(N) decay control, excess = real/rowperm of the near-miss sd ratio:
                                  1.062 / 0.987 / 1.193 / 1.354
                                  at N' = 500 / 2000 / 8000 / 17919

The AGGREGATION RULE below is declared here, before the run, and is not changed
afterwards. It is the executor's, since the card supplied reference values but
no aggregation rule for nine instances.

    Per instance i and statistic T:
      excess_i(T) = T_real,i / mean_over_realisations T_rowperm,i
    Pooled over the 9 instances:
      mean_i excess_i  +-  sd_i excess_i     (sd across INSTANCES, ddof=1)
      sign agreement   = #{i : excess_i on the same side of 1 as batch 2}
      pooled z         = (mean_i excess_i - 1) / (sd_i excess_i / sqrt(9))
    Decay verdict (per instance and pooled): compare excess at N'=500 with
    excess at N'=17919. "Decays like its surrogate" means excess is flat at 1
    across N'; "does not decay like its surrogate" means excess grows with N'.

------------------------------------------------------------------------------
NULL SUFFICIENCY (DEC-20260803-264d6a PD-2)
------------------------------------------------------------------------------
Every null below records THREE things: the OBJECT removed, the STATISTIC used,
and a SENSITIVITY DEMONSTRATION for that pair. Naming the object is necessary
and not sufficient -- batch 2's NULL-V named four objects and used a statistic
containing no y at all.

The sensitivity demonstrations built into this script:

  SENS-0  (ANALYTIC, and it is the proof of batch 2's defect)
          Under any row permutation of Y, the CORRECT candidate's score is
          bitwise unchanged, because its phase offset is y_i.(s - s) = 0 for
          every i regardless of which y sits in row i. Therefore ANY statistic
          built only from the correct-secret score has EXACTLY ZERO power
          against NULL-ROWPERM. Verified numerically to machine precision.
  SENS-1  (ANALYTIC, degenerate) Set y_i := 0 for all i. Then every near-miss
          and every wrong-candidate phase offset is 0, so all candidate scores
          coincide with the correct one: near-miss sd ratio == 0 exactly and
          correct - best-of-group == 0 exactly. The statistics therefore read y.
          Verified numerically.
  SENS-2  (ANALYTIC + measured, inside the null's own object class) Because
          E_e[sin(2 pi x.e/q)] = 0 exactly for a symmetric error, the expected
          score of candidate j under a pairing pi is EXACTLY
          mean_i w_i cos(phi_{pi(i),j}) with w_i = E_e[cos(2 pi x_i.e/q)].
          The REARRANGEMENT INEQUALITY then gives, in closed form, the maximum
          and the minimum of that expectation over the class of ALL N! pairings
          -- every one of which preserves both multisets and every column
          marginal. Both extremal pairings are constructed and MEASURED, and
          the measured differences are compared with the predicted ones.
  SENS-2c (MEASURED) Pairing by matched LENGTH RANK. Reported whatever it shows;
          not relied on.
  SENS-3  (MEASURED, inside the null's own object class) DOSE-RESPONSE: pi_t
          shuffles a random subset of round(t*N) rows and fixes the rest, so t
          is exactly how much of the pairing was removed and every pi_t stays
          in the null's own object class. PRE-DECLARED PREDICTION: a statistic
          that reads the pairing is MONOTONE in t; a statistic blind to the
          pairing is FLAT in t.

Which demonstration serves which (object, statistic) pair is reported in the
results file rather than assumed: SENS-2 is analytic but may have little
dynamic range on a given statistic, and where it does not, that is recorded.

------------------------------------------------------------------------------
EXACTNESS NOTE ON THE FAST SCORING ROUTE
------------------------------------------------------------------------------
Scores are means of cos(2*pi*(x_i.e + y_i.(s-c_j))/q). This script computes
them as

    mean_i [ cos(u_i) cos(phi_ij) - sin(u_i) sin(phi_ij) ],
    u_i = 2*pi*(x_i.e)/q,  phi_ij = 2*pi*(y_i.(s-c_j))/q

which is the cosine addition formula, so it is mathematically identical to
BATCH-f75059's compare.py route cos(2*pi*((x.e + y.(s-c)) mod q)/q). It is used
because it makes every null arm share ONE set of transcendentals, so the arms
are PAIRED on the error draws by construction rather than by seed discipline.
The agreement with the modular route is verified numerically (check "FAST_ROUTE
_AGREES") and the maximum absolute deviation is reported in the results file.
"""

import argparse, json, os, platform, resource, sys, time, hashlib

import numpy as np

SCRIPT_VERSION = "stage_a.py v1 TASK-20260803-db170f"
TWOPI = 2.0 * np.pi

# ---------------------------------------------------------------------------
# frozen reference from the task card (RT-20260803-dc7568, ONE instance)
# ---------------------------------------------------------------------------
FROZEN_REFERENCE = dict(
    source="task card TASK-20260803-db170f, from RT-20260803-dc7568 section 4, "
           "single primary instance of BATCH-f75059",
    near_miss_sd_ratio=dict(real=0.142888, rowperm_mean=0.105408,
                            rowperm_sd=0.000991, excess_pct=+35.6),
    correct_minus_best_of_8_near_miss=dict(real=0.001522, rowperm_mean=0.001761,
                                           rowperm_sd=0.000011,
                                           excess_pct=-13.6),
    decay_excess=dict(N=[500, 2000, 8000, 17919],
                      excess=[1.062, 0.987, 1.193, 1.354]),
    frozen_note="Not adjusted after runs began. Runs are compared against these "
                "values exactly as the card states them.",
)

# BATCH-f75059 results.json -> S9_replicate_instances -> per_instance.
# Used ONLY as a reproduction check that this task regenerates the SAME nine
# instances. a_x is a deterministic function of the instance (no error draws),
# so it must agree to all printed digits if the instances are identical.
F75059_REPLICATES = {
    0: dict(seed=20260803206, n_vectors=17919, a_x_measured=0.888475041394716),
    1: dict(seed=20260804206, n_vectors=17919, a_x_measured=0.8876366140975788),
    2: dict(seed=20260805206, n_vectors=17919, a_x_measured=0.890787614568475),
    3: dict(seed=20260806206, n_vectors=17919, a_x_measured=0.8902010706105234),
    4: dict(seed=20260807206, n_vectors=17919, a_x_measured=0.8881015874634072),
    5: dict(seed=20260808206, n_vectors=17919, a_x_measured=0.8874147819159967),
    6: dict(seed=20260809206, n_vectors=17919, a_x_measured=0.889417281781756),
    7: dict(seed=20260810206, n_vectors=17919, a_x_measured=0.8877150202996896),
    8: dict(seed=20260811206, n_vectors=17919, a_x_measured=0.8901152882151825),
}
# BATCH-f75059's own per-instance near-miss statistic, on ITS 500 error draws
# with ITS seeds. Recorded for context; this task's draws are its own, so exact
# agreement is neither expected nor required.
F75059_NEAR_MISS_DELTA_VS_BEST = {
    0: 0.0015857845802429227, 1: 0.0015570294948348486, 2: 0.0015564424248562796,
    3: 0.0015685948400936006, 4: 0.0015887810920553016, 5: 0.0015828549106025353,
    6: 0.001573797909310941, 7: 0.0016474640292849347, 8: 0.0014825186143113767,
}

# ---------------------------------------------------------------------------
# helpers copied VERBATIM from BATCH-f75059/compare.py so the nine replicate
# instances regenerate bit-for-bit (identical RNG consumption)
# ---------------------------------------------------------------------------
def centered_binomial(rng, eta, size):
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


def center_mod(v, q):
    r = np.mod(v, q)
    return np.where(r > q // 2, r - q, r).astype(np.int64)


def to_intmat(M):
    from fpylll import IntegerMatrix
    A = IntegerMatrix(M.shape[0], M.shape[1])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            A[i, j] = int(M[i, j])
    return A


def from_intmat(A):
    return np.array([[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
                    dtype=np.int64)


def build_dual_basis(A, q, m, n):
    d = m + n
    B = np.zeros((d, d), dtype=np.int64)
    B[:m, :m] = np.eye(m, dtype=np.int64)
    B[:m, m:] = A
    B[m:, m:] = q * np.eye(n, dtype=np.int64)
    return B


def run_sieve(A, q, m, n, sieve_name, fpylll_seed, sieve_seed):
    from fpylll import LLL, FPLLL
    from g6k import Siever, SieverParams
    d = m + n
    Bfp = to_intmat(build_dual_basis(A, q, m, n))
    FPLLL.set_random_seed(fpylll_seed)
    t0 = time.time()
    Bred = LLL.reduction(Bfp)
    t_lll = time.time() - t0
    g = Siever(Bred, SieverParams(threads=1), seed=sieve_seed)
    g.initialize_local(0, 0, d)
    t0 = time.time()
    getattr(g, sieve_name)()
    t_sieve = time.time() - t0
    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    V = coeffs.dot(from_intmat(g.M.B))
    return V[:, :m], V[:, m:], V, dict(lll_seconds=round(t_lll, 3),
                                       sieve_seconds=round(t_sieve, 3))


def make_candidates(rng, s, q, n, eta, n_unif, n_sdist, n_near):
    """VERBATIM from BATCH-f75059/compare.py."""
    cands = [("correct", "correct", s.copy())]
    for i in range(n_unif):
        cands.append(("uniform_%02d" % i, "uniform",
                      rng.integers(0, q, size=n, dtype=np.int64)))
    for i in range(n_sdist):
        cands.append(("secretdist_%02d" % i, "secret_distribution",
                      centered_binomial(rng, eta, n)))
    for i in range(n_near):
        c = s.copy()
        c[i % n] = c[i % n] + 1
        cands.append(("nearmiss_%02d" % i, "near_miss", c))
    cands.append(("zero_vector", "reference_zero", np.zeros(n, dtype=np.int64)))
    return cands


def ms(a):
    a = np.asarray(a, dtype=float)
    return dict(mean=float(a.mean()),
                sd=float(a.std(ddof=1)) if a.size > 1 else None,
                n_draws=int(a.size))


def c4(k):
    """Sample-sd bias factor E[s]/sigma for k iid normal samples (D2, batch 2)."""
    from math import lgamma, sqrt, exp
    if k < 2:
        return float("nan")
    return sqrt(2.0 / (k - 1)) * exp(lgamma(k / 2.0) - lgamma((k - 1) / 2.0))


def exact_char_fn_weights(X, q, sigma, tail=12):
    """w_i = E_e[cos(2 pi x_i.e / q)] EXACTLY, for e a rounded Gaussian N(0,sigma)
    rounded to integers, drawn independently per coordinate.

    Since e is symmetric, E_e[sin(2 pi x_i.e/q)] = 0 EXACTLY, so for any phase
    offset phi,   E_e[cos(2 pi x_i.e/q + phi)] = w_i cos(phi).
    That identity is what makes the SENS-2 rearrangement bound below analytic.

    w_i factorises over coordinates: w_i = prod_j phi(2 pi X[i,j]/q) with
    phi(theta) = sum_v p_v cos(theta v), p_v the rounding probabilities.
    """
    from math import erf, sqrt as msqrt
    lo, hi = int(X.min()), int(X.max())
    vmax = int(np.ceil(tail * sigma))
    vs = np.arange(-vmax, vmax + 1)
    edges = (vs[:, None] + np.array([-0.5, 0.5])[None, :]) / (sigma * msqrt(2.0))
    pv = np.array([0.5 * (erf(b) - erf(a)) for a, b in edges])
    dropped = float(1.0 - pv.sum())
    pv = pv / pv.sum()
    vals = np.arange(lo, hi + 1)
    theta = TWOPI * vals / q
    phi_tab = (pv[None, :] * np.cos(theta[:, None] * vs[None, :])).sum(axis=1)
    w = phi_tab[(X - lo)].prod(axis=1)
    return w, dict(truncation_sigma=tail,
                   truncated_probability_mass_dropped=dropped,
                   x_entry_range=[lo, hi],
                   note="w_i is exact up to the truncated tail mass reported "
                        "here; the exponential form exp(-2 pi^2 sigma^2 "
                        "||x||^2/q^2) is NOT used, because it is the "
                        "continuous-Gaussian idealisation whose error is "
                        "BATCH-f75059's D1 (Sheppard's correction).")


# ---------------------------------------------------------------------------
# scoring core -- one set of transcendentals shared by every null arm
# ---------------------------------------------------------------------------
def draw_blocks(D, block):
    done = 0
    while done < D:
        b = min(block, D - done)
        yield done, b
        done += b


def per_draw_series(means, idxs, Nv):
    """The two headline statistics as PER-DRAW series, so that two arms sharing
    an error-draw sequence can be differenced draw by draw (paired)."""
    gm = means[:, idxs]
    ratio = gm.std(axis=1, ddof=1) / np.sqrt(0.5 / Nv)
    delta_best = means[:, 0] - gm.max(axis=1)
    return ratio, delta_best


def paired_diff(a, b):
    """mean +- sem and z of the PAIRED per-draw difference a - b."""
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    sem = float(d.std(ddof=1) / np.sqrt(d.size))
    return dict(mean_difference=float(d.mean()), sem=sem,
                z=float(d.mean() / sem) if sem > 0 else None,
                n_draws=int(d.size),
                pairing_note="the two arms consume the SAME error-draw "
                             "sequence, so this difference is paired and its "
                             "sem is not the sem of either arm alone")


def group_stats(means, gidx, Nv, group_sizes):
    """Per-group statistics. NEVER pooled across groups."""
    out = {}
    iid_sd = float(np.sqrt(0.5 / Nv))
    for g, idxs in gidx.items():
        if g in ("correct", "reference_zero"):
            continue
        gm = means[:, idxs]
        sd_across = gm.std(axis=1, ddof=1)
        ratio = sd_across / iid_sd
        k = len(idxs)
        out[g] = dict(
            n_candidates=k,
            iid_sd_prediction=iid_sd,
            sd_ratio_to_iid=ms(ratio),
            sd_ratio_to_iid_c4_corrected=ms(ratio / c4(k)),
            c4_factor=c4(k),
            group_mean_score=ms(gm.mean(axis=1)),
            correct_minus_group_mean=ms(means[:, 0] - gm.mean(axis=1)),
            correct_minus_best_member=ms(means[:, 0] - gm.max(axis=1)),
            P_correct_first_within_group=float(
                np.mean(means[:, 0] > gm.max(axis=1))),
        )
    out["correct"] = dict(
        mean_score=ms(means[:, 0]),
        sd_of_correct_score_over_draws=float(means[:, 0].std(ddof=1)),
        note="the correct-secret score has phase offset y.(s-s)=0 for every "
             "vector, so it is INVARIANT under any row permutation of Y. It "
             "cannot test the pairing. Reported as SENS-0, never as evidence "
             "about the pairing.")
    if "reference_zero" in gidx:
        out["reference_zero"] = dict(
            mean_score=ms(means[:, gidx["reference_zero"][0]]),
            note="reference candidate c=0 (reading R-A). Reported separately, "
                 "never pooled into a wrong-candidate group.")
    return out


def run_instance(rep, cfg, seeds, say, verify_fast_route):
    q, m, n = cfg["q"], cfg["m"], cfg["n"]
    D = cfg["draws"]
    t_inst = time.time()

    # --- regenerate BATCH-f75059's replicate instance r, bit-for-bit ---------
    sd_ = seeds["replicates"] + 1000 * rep
    rgi = np.random.default_rng(sd_)
    A = rgi.integers(0, q, size=(m, n), dtype=np.int64)
    s = centered_binomial(rgi, cfg["eta_secret"], n)
    X, Y, V, tim = run_sieve(A, q, m, n, cfg["sieve"], sd_ + 1, sd_ + 2)
    N = X.shape[0]

    # --- certificate, re-verified independently of g6k ----------------------
    t0 = time.time()
    resid = np.mod(X.dot(A) - Y, q)
    n_bad = int(np.count_nonzero(resid))
    n_zero = int(np.count_nonzero(np.all(V == 0, axis=1)))
    n_dup_y = int(N - len(set(map(tuple, Y.tolist()))))
    cert = dict(kind="lattice_membership",
                statement="every emitted vector v=(x,y) satisfies "
                          "y == A^T x (mod q)",
                checked_vectors=int(N), checked_entries=int(N * n),
                violating_entries=n_bad, all_zero_vectors=n_zero,
                duplicate_y_parts=n_dup_y,
                verified=bool(n_bad == 0 and n_zero == 0),
                method="integer arithmetic on numpy int64 from A and the "
                       "reconstructed lattice vectors, independent of g6k's "
                       "internal representation",
                solve_claim_certificate="none -- no discrete-log solve and no "
                                        "factor-base relation is claimed",
                check_seconds=round(time.time() - t0, 3))
    say("  rep %d: N=%d cert_ok=%s (violating=%d zero=%d dup_y=%d) sieve %.1fs"
        % (rep, N, cert["verified"], n_bad, n_zero, n_dup_y,
           tim["sieve_seconds"]))
    if not cert["verified"]:
        return dict(replicate=rep, aborted="certificate_failed",
                    certificate=cert)

    xn2 = (X * X).sum(axis=1).astype(np.float64)
    yn2 = (Y * Y).sum(axis=1).astype(np.float64)
    a_x = float(2 * np.pi ** 2 * cfg["sigma"] ** 2 * xn2.mean() / q ** 2)
    a_y = float(2 * np.pi ** 2 * 1.0 * yn2.mean() / q ** 2)

    # --- candidates, VERBATIM group sizes of BATCH-f75059's replicates ------
    rgc = np.random.default_rng(sd_ + 3)
    cands = make_candidates(rgc, s, q, n, cfg["eta_secret"],
                            max(4, cfg["n_unif"] // 2),
                            max(2, cfg["n_sdist"] // 2), cfg["n_near"])
    labels = [c[0] for c in cands]
    groups = [c[1] for c in cands]
    C = np.array([c[2] for c in cands], dtype=np.int64)
    K = len(cands)
    gidx = {}
    for i, g in enumerate(groups):
        gidx.setdefault(g, []).append(i)
    group_sizes = {g: len(v) for g, v in gidx.items()}

    # --- fixed random ordering of the rows; subsamples are PREFIXES ---------
    rng_ord = np.random.default_rng(seeds["order"] + rep)
    order = rng_ord.permutation(N)
    X = X[order]; Y = Y[order]; xn2 = xn2[order]; yn2 = yn2[order]

    # --- phase offsets and their trig, for the REAL pairing -----------------
    Dph = np.mod(Y.dot((s[None, :] - C).T), q).astype(np.float64)   # (N, K)
    cosPhi = np.cos(TWOPI * Dph / q)
    sinPhi = np.sin(TWOPI * Dph / q)

    # =======================================================================
    # arms.  Every arm is a re-pairing of the SAME x-multiset with the SAME
    # y-multiset unless stated otherwise, so they share cos(u), sin(u).
    # =======================================================================
    rng_perm = np.random.default_rng(seeds["rowperm"] + rep)
    rng_col = np.random.default_rng(seeds["colperm"] + rep)
    rng_dir = np.random.default_rng(seeds["randdir"] + rep)

    # exact per-vector weights w_i = E_e[cos(2 pi x_i.e/q)] (see SENS-2)
    w, w_meta = exact_char_fn_weights(X, q, cfg["sigma"])

    arms = []           # (name, family, cosPhi, sinPhi)  -- share cos/sin(u)
    arms.append(("real", "real", cosPhi, sinPhi))
    for rho in range(cfg["n_rowperm"]):
        pi = rng_perm.permutation(N)
        arms.append(("rowperm_%02d" % rho, "NULL-ROWPERM",
                     cosPhi[pi], sinPhi[pi]))

    # ---- SENS-2: the REARRANGEMENT pairings -------------------------------
    # E_e[score_j] = mean_i w_i cos(phi_{pi(i),j})  EXACTLY.  So over the class
    # of all pairings (all N! permutations, every one of which preserves both
    # multisets and every column marginal) the expected near-miss-0 score is
    # MAXIMISED by co-sorting w with cos(phi_{.,0}) and MINIMISED by
    # anti-sorting them -- the rearrangement inequality.  Both extremes are
    # computed in closed form below and then MEASURED, so this exhibits
    # pairings for which the statistic provably differs.
    nm0 = gidx["near_miss"][0]
    idx_w = np.argsort(w, kind="stable")
    idx_c = np.argsort(cosPhi[:, nm0], kind="stable")
    pi_max = np.empty(N, dtype=np.int64); pi_max[idx_w] = idx_c
    pi_min = np.empty(N, dtype=np.int64); pi_min[idx_w] = idx_c[::-1]
    arms.append(("sens2_rearrangement_max", "SENS-2",
                 cosPhi[pi_max], sinPhi[pi_max]))
    arms.append(("sens2_rearrangement_min", "SENS-2",
                 cosPhi[pi_min], sinPhi[pi_min]))
    # SENS-2c: pairing by matched length rank (kept because its outcome is
    # informative either way; it is NOT relied on as the demonstration)
    ordx = np.argsort(xn2, kind="stable")
    ordy = np.argsort(yn2, kind="stable")
    inv = np.empty(N, dtype=np.int64); inv[ordx] = np.arange(N)
    pi_sorted = ordy[inv]
    arms.append(("sens2c_length_sorted_pairing", "SENS-2c",
                 cosPhi[pi_sorted], sinPhi[pi_sorted]))
    # ---- SENS-3: DOSE-RESPONSE in the amount of pairing destroyed ----------
    # pi_t permutes a uniformly random subset of round(t*N) rows and fixes the
    # rest. EVERY pi_t preserves the exact multiset of x, the exact multiset of
    # y and every column marginal; t is exactly "how much of the pairing was
    # removed". PRE-DECLARED PREDICTION: a statistic that reads the pairing is
    # MONOTONE in t between its t=0 (real) and t=1 (full row-permutation)
    # values; a statistic blind to the pairing is FLAT in t. The shape between
    # the endpoints is an observation, not a prediction.
    rng_dose = np.random.default_rng(seeds["dose"] + rep)
    for t in cfg["dose_fractions"]:
        k_sh = int(round(t * N))
        pi = np.arange(N)
        if k_sh >= 2:
            sub = rng_dose.choice(N, size=k_sh, replace=False)
            pi[sub] = sub[rng_dose.permutation(k_sh)]
        arms.append(("sens3_dose_t%03d" % int(round(1000 * t)), "SENS-3",
                     cosPhi[pi], sinPhi[pi]))
    # SENS-1: y := 0 (analytic: all candidate scores collapse onto the correct)
    arms.append(("sens1_y_zero", "SENS-1",
                 np.ones((N, K)), np.zeros((N, K))))
    # NULL-COLPERM: permute each column of Y independently
    for rho in range(cfg["n_colperm"]):
        Yc = np.empty_like(Y)
        for k in range(n):
            Yc[:, k] = Y[rng_col.permutation(N), k]
        Dc = np.mod(Yc.dot((s[None, :] - C).T), q).astype(np.float64)
        arms.append(("colperm_%02d" % rho, "NULL-COLPERM",
                     np.cos(TWOPI * Dc / q), np.sin(TWOPI * Dc / q)))

    # -----------------------------------------------------------------------
    # main draw loop: cos(u), sin(u) computed ONCE, shared by every arm above
    # -----------------------------------------------------------------------
    Ns = [Np for Np in cfg["N_decay"] if Np <= N] + [N]
    Ns = sorted(set(Ns))
    means = {a[0]: np.empty((D, K)) for a in arms}
    # decay needs the permutation restricted to the SUBSAMPLE, otherwise the
    # surrogate's y-multiset would not match the subsample's own y-multiset and
    # the comparison would confound the null with the subsampling.
    dec_arms = {}
    rng_pd = np.random.default_rng(seeds["rowperm_decay"] + rep)
    for Np in Ns:
        if Np == N:
            continue
        dec_arms[("real", Np)] = (cosPhi[:Np], sinPhi[:Np])
        for rho in range(cfg["n_rowperm_decay"]):
            pi = rng_pd.permutation(Np)
            dec_arms[("rowperm_%02d" % rho, Np)] = (cosPhi[:Np][pi],
                                                    sinPhi[:Np][pi])
    means_dec = {k: np.empty((D, K)) for k in dec_arms}

    rng_e = np.random.default_rng(seeds["error_draws"] + rep)
    Xf = X.astype(np.float64)      # entries are small ints; products are exact
    fast_max_dev = None
    for off, b in draw_blocks(D, cfg["block"]):
        E = np.rint(rng_e.normal(0.0, cfg["sigma"], size=(m, b))).astype(np.int64)
        U = Xf.dot(E.astype(np.float64))                    # (N, b) exact ints
        Cu = np.cos(TWOPI * U / q).T                        # (b, N)
        Su = np.sin(TWOPI * U / q).T
        for name, fam, cp, sp in arms:
            means[name][off:off + b] = (Cu.dot(cp) - Su.dot(sp)) / N
        for (name, Np), (cp, sp) in dec_arms.items():
            means_dec[(name, Np)][off:off + b] = (
                Cu[:, :Np].dot(cp) - Su[:, :Np].dot(sp)) / Np
        if off == 0 and verify_fast_route:
            # BATCH-f75059's exact modular route, on the first few draws only
            nv = min(5, b)
            Dint = np.mod(Y.dot((s[None, :] - C).T), q).astype(np.int64)  # (N,K)
            Uint = X.dot(E[:, :nv])                                      # (N,nv)
            Pm = np.mod(Uint[:, :, None] + Dint[:, None, :], q)          # (N,nv,K)
            ref = np.cos(TWOPI * Pm / q).mean(axis=0)                    # (nv,K)
            fast_max_dev = float(np.abs(ref - means["real"][off:off + nv]).max())
            del Pm, ref, Uint, Dint

    # -----------------------------------------------------------------------
    # NULL-RANDDIR: random directions of matched ||x|| AND matched ||y||.
    # Its u differs, so it gets its own (paired) error sequence.
    # -----------------------------------------------------------------------
    randdir = []
    for rho in range(cfg["n_randdir"]):
        Gx = rng_dir.normal(size=(N, m)); Gx /= np.linalg.norm(Gx, axis=1, keepdims=True)
        Xs = Gx * np.sqrt(xn2)[:, None]
        Gy = rng_dir.normal(size=(N, n)); Gy /= np.linalg.norm(Gy, axis=1, keepdims=True)
        Ys = Gy * np.sqrt(yn2)[:, None]
        Dr = Ys.dot((s[None, :] - C).T.astype(np.float64))
        cpr = np.cos(TWOPI * Dr / q); spr = np.sin(TWOPI * Dr / q)
        mr = np.empty((D, K))
        rng_er = np.random.default_rng(seeds["error_draws"] + rep)   # PAIRED
        for off, b in draw_blocks(D, cfg["block"]):
            E = np.rint(rng_er.normal(0.0, cfg["sigma"], size=(m, b))).astype(np.int64)
            Ur = Xs.dot(E.astype(np.float64))
            mr[off:off + b] = (np.cos(TWOPI * Ur / q).T.dot(cpr) -
                               np.sin(TWOPI * Ur / q).T.dot(spr)) / N
        randdir.append(("randdir_%02d" % rho, mr))
        del Gx, Gy, Xs, Ys, Dr, cpr, spr

    # -----------------------------------------------------------------------
    # statistics
    # -----------------------------------------------------------------------
    per_arm = {}
    for name, fam, _, _ in arms:
        per_arm[name] = dict(family=fam,
                             stats=group_stats(means[name], gidx, N, group_sizes))
    for name, mr in randdir:
        per_arm[name] = dict(family="NULL-RANDDIR",
                             stats=group_stats(mr, gidx, N, group_sizes))

    def agg(family, key, group="near_miss"):
        """mean +- sd ACROSS surrogate realisations of a per-realisation value
        that is itself a mean over all D error draws."""
        vals = []
        for a in per_arm:
            if per_arm[a]["family"] != family:
                continue
            v = per_arm[a]["stats"][group][key]
            vals.append(v["mean"] if isinstance(v, dict) else v)
        v = np.array(vals, dtype=float)
        return dict(mean=float(v.mean()),
                    sd_across_realisations=float(v.std(ddof=1)) if v.size > 1 else None,
                    n_realisations=int(v.size),
                    n_draws_per_realisation=int(D))

    # SENS-0: the correct score must be BITWISE invariant under NULL-ROWPERM
    sens0_dev = max(float(np.abs(means[a][:, 0] - means["real"][:, 0]).max())
                    for a, f, _, _ in arms if f == "NULL-ROWPERM")

    # -----------------------------------------------------------------------
    # SENS-2 report: the analytic rearrangement bound, and its verification.
    # -----------------------------------------------------------------------
    def predicted(cp):
        return w.dot(cp) / N                       # (K,) exact E_e[score]

    cp_of = {a: c for a, f, c, s in arms}
    sw = np.sort(w); sc = np.sort(cosPhi[:, nm0])
    analytic_max = float(sw.dot(sc) / N)
    analytic_min = float(sw.dot(sc[::-1]) / N)
    sem = lambda a: float(a.std(ddof=1) / np.sqrt(len(a)))
    rp_names = [a for a, f, _, _ in arms if f == "NULL-ROWPERM"]
    sens2 = dict(
        identity="E_e[score_j] = mean_i w_i cos(phi_{pi(i),j}) exactly, with "
                 "w_i = E_e[cos(2 pi x_i.e/q)] and E_e[sin(2 pi x_i.e/q)] = 0 "
                 "by symmetry of the rounded Gaussian.",
        weights_meta=w_meta,
        candidate_used="near-miss candidate %d (%s), whose phase offset is "
                       "exactly -Y[.,0]" % (nm0, labels[nm0]),
        analytic_rearrangement_max_over_ALL_pairings=analytic_max,
        analytic_rearrangement_min_over_ALL_pairings=analytic_min,
        analytic_spread_max_minus_min=analytic_max - analytic_min,
        predicted_and_measured={
            nm: dict(predicted=float(predicted(cp_of[an])[nm0]),
                     measured_mean=float(means[an][:, nm0].mean()),
                     measured_sem=sem(means[an][:, nm0]))
            for nm, an in (("real", "real"),
                           ("rowperm_first_realisation", rp_names[0]),
                           ("rearrangement_max", "sens2_rearrangement_max"),
                           ("rearrangement_min", "sens2_rearrangement_min"))},
        why_differences_not_levels=(
            "Every arm shares one error-draw sequence, so the deviation of a "
            "measured mean from its exact expectation is COMMON to all arms. "
            "The quantity that tests the identity is therefore the DIFFERENCE "
            "between arms, which is paired and low-noise. Levels are reported "
            "too, and their common offset is exactly the finite-draw "
            "fluctuation of the shared error sequence."),
        verdict_note="If the measured means track the analytic values and the "
                     "max/min pairings differ from each other, the statistic is "
                     "DEMONSTRABLY sensitive to which y pairs with which x -- "
                     "which is exactly the object NULL-ROWPERM removes. All "
                     "four pairings preserve both multisets and every column "
                     "marginal, so the demonstration lives inside the null's "
                     "own object class.")
    # (a) the analytic anchor: predicted vs measured DIFFERENCES from the real
    #     arm, which are paired and therefore carry no common-mode offset.
    pm = sens2["predicted_and_measured"]
    sens2["difference_from_real_arm"] = {}
    for nm, an in (("rowperm_first_realisation", rp_names[0]),
                   ("rearrangement_max", "sens2_rearrangement_max"),
                   ("rearrangement_min", "sens2_rearrangement_min")):
        pd = paired_diff(means[an][:, nm0], means["real"][:, nm0])
        sens2["difference_from_real_arm"][nm] = dict(
            predicted=float(pm[nm]["predicted"] - pm["real"]["predicted"]),
            measured=pd["mean_difference"], measured_sem=pd["sem"],
            predicted_minus_measured=float(
                pm[nm]["predicted"] - pm["real"]["predicted"]
                - pd["mean_difference"]))
    sens2["max_abs_predicted_minus_measured_difference"] = max(
        abs(v["predicted_minus_measured"])
        for v in sens2["difference_from_real_arm"].values())

    # (b) the demonstration proper: PAIRED per-draw difference of each HEADLINE
    #     statistic between the two extremal pairings, per candidate group.
    sens2["headline_statistic_response_to_the_pairing"] = {}
    for group in ("uniform", "secret_distribution", "near_miss"):
        idxs = gidx[group]
        r_hi, d_hi = per_draw_series(means["sens2_rearrangement_max"], idxs, N)
        r_lo, d_lo = per_draw_series(means["sens2_rearrangement_min"], idxs, N)
        r_re, d_re = per_draw_series(means["real"], idxs, N)
        r_rp, d_rp = per_draw_series(means[rp_names[0]], idxs, N)
        sens2["headline_statistic_response_to_the_pairing"][group] = dict(
            sd_ratio_max_minus_min=paired_diff(r_hi, r_lo),
            sd_ratio_real_minus_rowperm=paired_diff(r_re, r_rp),
            correct_minus_best_max_minus_min=paired_diff(d_hi, d_lo),
            correct_minus_best_real_minus_rowperm=paired_diff(d_re, d_rp))
    nmr = sens2["headline_statistic_response_to_the_pairing"]["near_miss"]
    sens2["sensitivity_demonstrated_on_near_miss_sd_ratio"] = bool(
        nmr["sd_ratio_max_minus_min"]["z"] is not None
        and abs(nmr["sd_ratio_max_minus_min"]["z"]) > 5.0)
    sens2["sensitivity_demonstrated_on_correct_minus_best"] = bool(
        nmr["correct_minus_best_max_minus_min"]["z"] is not None
        and abs(nmr["correct_minus_best_max_minus_min"]["z"]) > 5.0)
    sens2["sensitivity_criterion"] = (
        "|z| > 5 on the PAIRED per-draw difference between the two extremal "
        "rearrangement pairings. Declared before the run.")

    # -----------------------------------------------------------------------
    # SENS-3 report: the dose-response curve, per candidate group.
    # -----------------------------------------------------------------------
    dose_names = [a for a, f, _, _ in arms if f == "SENS-3"]
    sens3 = dict(
        construction="pi_t shuffles a uniformly random subset of round(t*N) "
                     "rows and fixes the rest; every pi_t preserves both "
                     "multisets and every column marginal, so t is exactly the "
                     "fraction of the pairing removed.",
        pre_declared_prediction="a statistic that reads the pairing is MONOTONE "
                                "in t between its t=0 (real) and t=1 (full "
                                "row-permutation) values; a statistic blind to "
                                "the pairing is FLAT in t.",
        t_values=list(cfg["dose_fractions"]), groups={})
    for group in ("uniform", "secret_distribution", "near_miss"):
        idxs = gidx[group]
        r0, d0 = per_draw_series(means["real"], idxs, N)
        rows = [dict(t=0.0, arm="real",
                     sd_ratio=float(r0.mean()),
                     sd_ratio_paired_diff_vs_real=0.0,
                     correct_minus_best=float(d0.mean()),
                     correct_minus_best_paired_diff_vs_real=0.0)]
        for t, an in zip(cfg["dose_fractions"], dose_names):
            rt, dt = per_draw_series(means[an], idxs, N)
            rows.append(dict(
                t=float(t), arm=an,
                sd_ratio=float(rt.mean()),
                sd_ratio_paired_diff_vs_real=paired_diff(rt, r0)["mean_difference"],
                sd_ratio_paired_z_vs_real=paired_diff(rt, r0)["z"],
                correct_minus_best=float(dt.mean()),
                correct_minus_best_paired_diff_vs_real=paired_diff(dt, d0)["mean_difference"],
                correct_minus_best_paired_z_vs_real=paired_diff(dt, d0)["z"]))
        sr = [x["sd_ratio"] for x in rows]
        sd_mono = all(sr[i + 1] <= sr[i] for i in range(len(sr) - 1)) or \
            all(sr[i + 1] >= sr[i] for i in range(len(sr) - 1))
        cb = [x["correct_minus_best"] for x in rows]
        cb_mono = all(cb[i + 1] <= cb[i] for i in range(len(cb) - 1)) or \
            all(cb[i + 1] >= cb[i] for i in range(len(cb) - 1))
        sens3["groups"][group] = dict(
            curve=rows,
            sd_ratio_monotone_in_t=bool(sd_mono),
            correct_minus_best_monotone_in_t=bool(cb_mono),
            sd_ratio_total_swing=float(sr[-1] - sr[0]),
            correct_minus_best_total_swing=float(cb[-1] - cb[0]))

    headline = {}
    for group in ("uniform", "secret_distribution", "near_miss"):
        idxs = gidx[group]
        r_re, d_re = per_draw_series(means["real"], idxs, N)
        pr = [paired_diff(r_re, per_draw_series(means[a], idxs, N)[0])
              for a in rp_names]
        pd_ = [paired_diff(d_re, per_draw_series(means[a], idxs, N)[1])
               for a in rp_names]
        paired_vs_rowperm = dict(
            sd_ratio=dict(
                mean_paired_difference_across_realisations=float(
                    np.mean([x["mean_difference"] for x in pr])),
                sd_across_realisations=float(
                    np.std([x["mean_difference"] for x in pr], ddof=1)),
                typical_paired_sem=float(np.mean([x["sem"] for x in pr])),
                z_per_realisation=[x["z"] for x in pr]),
            correct_minus_best=dict(
                mean_paired_difference_across_realisations=float(
                    np.mean([x["mean_difference"] for x in pd_])),
                sd_across_realisations=float(
                    np.std([x["mean_difference"] for x in pd_], ddof=1)),
                typical_paired_sem=float(np.mean([x["sem"] for x in pd_])),
                z_per_realisation=[x["z"] for x in pd_]))
        real_r = per_arm["real"]["stats"][group]["sd_ratio_to_iid"]
        real_d = per_arm["real"]["stats"][group]["correct_minus_best_member"]
        rp_r = agg("NULL-ROWPERM", "sd_ratio_to_iid", group)
        rp_d = agg("NULL-ROWPERM", "correct_minus_best_member", group)
        headline[group] = dict(
            sd_ratio_to_iid=dict(
                real=real_r, rowperm=rp_r,
                randdir=agg("NULL-RANDDIR", "sd_ratio_to_iid", group),
                colperm=agg("NULL-COLPERM", "sd_ratio_to_iid", group),
                sens2_rearrangement_max=per_arm["sens2_rearrangement_max"]["stats"][group]["sd_ratio_to_iid"],
                sens2_rearrangement_min=per_arm["sens2_rearrangement_min"]["stats"][group]["sd_ratio_to_iid"],
                sens2c_length_sorted=per_arm["sens2c_length_sorted_pairing"]["stats"][group]["sd_ratio_to_iid"],
                sens1_y_zero=per_arm["sens1_y_zero"]["stats"][group]["sd_ratio_to_iid"],
                excess_real_over_rowperm=float(real_r["mean"] / rp_r["mean"])
                if rp_r["mean"] else None,
                absolute_difference_real_minus_rowperm=float(
                    real_r["mean"] - rp_r["mean"])),
            correct_minus_best_member=dict(
                real=real_d, rowperm=rp_d,
                randdir=agg("NULL-RANDDIR", "correct_minus_best_member", group),
                colperm=agg("NULL-COLPERM", "correct_minus_best_member", group),
                sens2_rearrangement_max=per_arm["sens2_rearrangement_max"]["stats"][group]["correct_minus_best_member"],
                sens2_rearrangement_min=per_arm["sens2_rearrangement_min"]["stats"][group]["correct_minus_best_member"],
                sens2c_length_sorted=per_arm["sens2c_length_sorted_pairing"]["stats"][group]["correct_minus_best_member"],
                sens1_y_zero=per_arm["sens1_y_zero"]["stats"][group]["correct_minus_best_member"],
                excess_real_over_rowperm=float(real_d["mean"] / rp_d["mean"])
                if rp_d["mean"] else None,
                absolute_difference_real_minus_rowperm=float(
                    real_d["mean"] - rp_d["mean"])),
            P_correct_first=dict(
                real=per_arm["real"]["stats"][group]["P_correct_first_within_group"],
                rowperm=agg("NULL-ROWPERM", "P_correct_first_within_group", group),
                randdir=agg("NULL-RANDDIR", "P_correct_first_within_group", group),
                colperm=agg("NULL-COLPERM", "P_correct_first_within_group", group),
                sens2_rearrangement_max=per_arm["sens2_rearrangement_max"]["stats"][group]["P_correct_first_within_group"],
                sens2c_length_sorted=per_arm["sens2c_length_sorted_pairing"]["stats"][group]["P_correct_first_within_group"],
                sens1_y_zero=per_arm["sens1_y_zero"]["stats"][group]["P_correct_first_within_group"]),
            paired_real_minus_rowperm=paired_vs_rowperm,
        )

    # decay control, per instance
    decay = {}
    for Np in Ns:
        if Np == N:
            r_real = per_arm["real"]["stats"]["near_miss"]["sd_ratio_to_iid"]
            rp = [per_arm[a]["stats"]["near_miss"]["sd_ratio_to_iid"]["mean"]
                  for a in per_arm if per_arm[a]["family"] == "NULL-ROWPERM"]
        else:
            r_real = group_stats(means_dec[("real", Np)], gidx, Np,
                                 group_sizes)["near_miss"]["sd_ratio_to_iid"]
            rp = [group_stats(means_dec[("rowperm_%02d" % rho, Np)], gidx, Np,
                              group_sizes)["near_miss"]["sd_ratio_to_iid"]["mean"]
                  for rho in range(cfg["n_rowperm_decay"])]
        rpm = float(np.mean(rp))
        decay[str(Np)] = dict(
            N_prime=int(Np),
            real_near_miss_sd_ratio=r_real,
            rowperm_near_miss_sd_ratio=dict(
                mean=rpm,
                sd_across_realisations=float(np.std(rp, ddof=1)) if len(rp) > 1 else None,
                n_realisations=len(rp)),
            excess_real_over_rowperm=float(r_real["mean"] / rpm))

    # --- reproduction check: is this the SAME instance BATCH-f75059 made? ---
    ref = F75059_REPLICATES.get(rep) if not cfg.get("smoke_scale") else None
    if ref is not None:
        repro = dict(
            f75059_seed=ref["seed"], this_seed=int(sd_),
            seed_matches=bool(ref["seed"] == sd_),
            f75059_n_vectors=ref["n_vectors"], this_n_vectors=int(N),
            n_vectors_matches=bool(ref["n_vectors"] == N),
            f75059_a_x=ref["a_x_measured"], this_a_x=a_x,
            a_x_abs_difference=abs(ref["a_x_measured"] - a_x),
            a_x_matches_to_1e_12=bool(abs(ref["a_x_measured"] - a_x) < 1e-12),
            note="a_x is a deterministic function of the instance and consumes "
                 "no error draws, so identical instances must agree to all "
                 "printed digits. This is the check that this task measured "
                 "BATCH-f75059's nine instances and not nine new ones.",
            f75059_near_miss_delta_vs_best_on_ITS_own_500_draws=(
                F75059_NEAR_MISS_DELTA_VS_BEST.get(rep)),
            near_miss_delta_note="BATCH-f75059's value used ITS seeds and 500 "
                                 "draws; this task uses its own %d draws, so "
                                 "exact agreement is neither expected nor "
                                 "required." % D)
    else:
        repro = None

    out = dict(
        replicate=rep, seed=int(sd_), n_vectors=int(N), certificate=cert,
        reproduction_check_vs_BATCH_f75059=repro,
        sieve_seconds=tim["sieve_seconds"], lll_seconds=tim["lll_seconds"],
        mean_xnorm2=float(xn2.mean()), mean_ynorm2=float(yn2.mean()),
        a_x_measured=a_x, a_y_measured=a_y,
        candidate_groups=group_sizes,
        n_error_draws=int(D),
        fast_route_max_abs_deviation_from_modular_route=fast_max_dev,
        SENS0_correct_score_max_abs_change_under_rowperm=sens0_dev,
        SENS2_rearrangement_sensitivity_demonstration=sens2,
        SENS3_dose_response_sensitivity_demonstration=sens3,
        headline_per_group=headline,
        decay_control_near_miss=decay,
        per_arm=per_arm,
        instance_seconds=round(time.time() - t_inst, 2),
    )
    say("  rep %d: near-miss sd ratio real %.6f  rowperm %.6f +- %.6f  "
        "excess %.4f | corr-best real %.6f rowperm %.6f excess %.4f  (%.1fs)"
        % (rep, headline["near_miss"]["sd_ratio_to_iid"]["real"]["mean"],
           headline["near_miss"]["sd_ratio_to_iid"]["rowperm"]["mean"],
           headline["near_miss"]["sd_ratio_to_iid"]["rowperm"]["sd_across_realisations"],
           headline["near_miss"]["sd_ratio_to_iid"]["excess_real_over_rowperm"],
           headline["near_miss"]["correct_minus_best_member"]["real"]["mean"],
           headline["near_miss"]["correct_minus_best_member"]["rowperm"]["mean"],
           headline["near_miss"]["correct_minus_best_member"]["excess_real_over_rowperm"],
           out["instance_seconds"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--mem-cap-gb", type=float, default=6.0)
    ap.add_argument("--max-seconds", type=float, default=1400.0)
    args = ap.parse_args()

    t_start = time.time()
    if args.mem_cap_gb > 0:
        cap = int(args.mem_cap_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    log = []

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        print(line, flush=True)
        log.append(line)

    if args.smoke:
        cfg = dict(m=24, n=16, q=127, sieve="bgj1_sieve", eta_secret=2,
                   sigma=2.0, n_unif=8, n_sdist=4, n_near=8,
                   draws=120, block=60, n_rowperm=3, n_colperm=2, n_randdir=2,
                   n_rowperm_decay=2, N_decay=[200, 800],
                   dose_fractions=[0.25, 0.5, 1.0],
                   n_instances=2, smoke_scale=True)
    else:
        cfg = dict(m=35, n=25, q=127, sieve="bgj1_sieve", eta_secret=2,
                   sigma=2.0, n_unif=16, n_sdist=8, n_near=8,
                   draws=2000, block=250, n_rowperm=10, n_colperm=5,
                   n_randdir=5, n_rowperm_decay=5,
                   dose_fractions=[0.05, 0.2, 0.5, 0.8, 1.0],
                   N_decay=[500, 2000, 8000], n_instances=9)

    SEEDS = dict(
        # INHERITED from BATCH-f75059 -- these regenerate the SAME 9 instances
        replicates=20260803206,
        # this task's own randomness
        error_draws=20260803401,
        rowperm=20260803402,
        colperm=20260803403,
        randdir=20260803404,
        order=20260803405,
        rowperm_decay=20260803406,
        dose=20260803407,
    )

    say(SCRIPT_VERSION + "  smoke=%s" % args.smoke)
    say("cfg %s" % cfg)
    say("seeds %s" % SEEDS)
    say("NOTE: seeds['replicates'] is BATCH-f75059's own value; the instance, "
        "sieve, fpylll and candidate seeds are therefore inherited and the 9 "
        "instances regenerate bit-for-bit. Only the error draws and the "
        "surrogate randomness are this task's.")

    import numpy as _np
    env = dict(python=sys.version, platform=platform.platform(),
               numpy=_np.__version__, executable=sys.executable)
    try:
        import fpylll, g6k
        env["fpylll"] = fpylll.__version__
        env["g6k"] = getattr(g6k, "__version__", "0.1.2 (no __version__ attr)")
    except Exception as e:                                   # pragma: no cover
        env["import_error"] = repr(e)
    say("env %s" % env)

    instances = []
    for rep in range(cfg["n_instances"]):
        if time.time() - t_start > args.max_seconds:
            say("STOPPING after %d instances: soft wall-clock guard %.0fs "
                "reached. Recorded, not hidden." % (rep, args.max_seconds))
            break
        instances.append(run_instance(rep, cfg, SEEDS, say,
                                      verify_fast_route=(rep == 0)))

    good = [i for i in instances if "aborted" not in i]

    # -----------------------------------------------------------------------
    # POOLED across instances -- the declared aggregation rule
    # -----------------------------------------------------------------------
    def pooled(group, key):
        ex = np.array([i["headline_per_group"][group][key]["excess_real_over_rowperm"]
                       for i in good], dtype=float)
        ab = np.array([i["headline_per_group"][group][key]["absolute_difference_real_minus_rowperm"]
                       for i in good], dtype=float)
        real = np.array([i["headline_per_group"][group][key]["real"]["mean"]
                         for i in good], dtype=float)
        rp = np.array([i["headline_per_group"][group][key]["rowperm"]["mean"]
                       for i in good], dtype=float)
        sd = float(ex.std(ddof=1)) if ex.size > 1 else None
        sda = float(ab.std(ddof=1)) if ab.size > 1 else None
        return dict(
            per_instance_absolute_difference=[float(v) for v in ab],
            absolute_difference_mean=float(ab.mean()),
            absolute_difference_sd_across_instances=sda,
            absolute_difference_pooled_z_vs_zero=float(
                ab.mean() / (sda / np.sqrt(ab.size))) if sda else None,
            per_instance_excess=[float(v) for v in ex],
            excess_mean=float(ex.mean()),
            excess_sd_across_instances=sd,
            excess_sem=float(sd / np.sqrt(ex.size)) if sd else None,
            pooled_z_vs_unity=float((ex.mean() - 1.0) / (sd / np.sqrt(ex.size)))
            if sd else None,
            n_instances=int(ex.size),
            n_instances_excess_above_1=int((ex > 1).sum()),
            n_instances_excess_below_1=int((ex < 1).sum()),
            real_mean=float(real.mean()),
            real_sd_across_instances=float(real.std(ddof=1)) if real.size > 1 else None,
            rowperm_mean=float(rp.mean()),
            rowperm_sd_across_instances=float(rp.std(ddof=1)) if rp.size > 1 else None,
        )

    pooled_out = {}
    for group in ("uniform", "secret_distribution", "near_miss"):
        pooled_out[group] = dict(
            sd_ratio_to_iid=pooled(group, "sd_ratio_to_iid"),
            correct_minus_best_member=pooled(group, "correct_minus_best_member"),
        )

    # pooled decay
    Nkeys = sorted({k for i in good for k in i["decay_control_near_miss"]},
                   key=int)
    pooled_decay = {}
    for k in Nkeys:
        ex = np.array([i["decay_control_near_miss"][k]["excess_real_over_rowperm"]
                       for i in good if k in i["decay_control_near_miss"]],
                      dtype=float)
        rr = np.array([i["decay_control_near_miss"][k]["real_near_miss_sd_ratio"]["mean"]
                       for i in good if k in i["decay_control_near_miss"]])
        rp = np.array([i["decay_control_near_miss"][k]["rowperm_near_miss_sd_ratio"]["mean"]
                       for i in good if k in i["decay_control_near_miss"]])
        pooled_decay[k] = dict(
            N_prime=int(k),
            per_instance_excess=[float(v) for v in ex],
            excess_mean=float(ex.mean()),
            excess_sd_across_instances=float(ex.std(ddof=1)) if ex.size > 1 else None,
            real_ratio_mean=float(rr.mean()),
            real_ratio_sd_across_instances=float(rr.std(ddof=1)) if rr.size > 1 else None,
            rowperm_ratio_mean=float(rp.mean()),
            rowperm_ratio_sd_across_instances=float(rp.std(ddof=1)) if rp.size > 1 else None,
            n_instances=int(ex.size))

    results = dict(
        task="TASK-20260803-db170f", batch="BATCH-c45baf", goal="GOAL-MLKEM-004",
        stage="A", script_version=SCRIPT_VERSION, smoke=bool(args.smoke),
        states_a_conclusion=False,
        scope="m=35 n=25 d=60 q=127, secret CB eta=2, error rounded-Gaussian "
              "sigma=2, g6k bgj1_sieve. TOY SCALE. No ML-KEM break claim, no "
              "security proof, no FIPS 203 parameter set affected or cleared, "
              "no speedup, no cost claim.",
        rule12_status="UNMET and UNWAIVED, inherited. No EV-MLKEM-* or KN-* "
                      "status changes.",
        frozen_reference=FROZEN_REFERENCE,
        aggregation_rule_declared_before_run=(
            "excess_i = T_real,i / mean_rho T_rowperm,i,rho ; pooled = mean_i "
            "excess_i +- sd_i excess_i (ddof=1) over the 9 instances; pooled z "
            "= (mean-1)/(sd/sqrt(9)); decay verdict compares excess at N'=500 "
            "with excess at N'=full."),
        config=cfg, seeds=SEEDS, environment=env,
        n_instances_completed=len(good),
        per_instance=instances,
        pooled=pooled_out,
        pooled_decay_control_near_miss=pooled_decay,
        nulls=NULL_REGISTRY,
        log=log,
    )
    results["timings"] = dict(
        total_wall_seconds=round(time.time() - t_start, 2),
        peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                          / 1024.0, 1))

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "stage_a_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    say("wrote %s (%d bytes)" % (out, os.path.getsize(out)))
    say("total %.1fs peak RSS %.1f MB" % (results["timings"]["total_wall_seconds"],
                                          results["timings"]["peak_rss_mb"]))


# ---------------------------------------------------------------------------
# NULL REGISTRY -- PD-2 requires OBJECT, STATISTIC and SENSITIVITY DEMONSTRATION
# for every null. Naming the object is necessary and NOT sufficient.
# ---------------------------------------------------------------------------
NULL_REGISTRY = [
    dict(
        id="NULL-ROWPERM",
        removes_object="which y is paired with which x, i.e. membership of the "
                       "pair (x_i, y_i) in the dual lattice L = {(x,y) : "
                       "y = A^T x mod q}. NOTHING ELSE.",
        preserves="the exact multiset of x rows, the exact multiset of y rows, "
                  "every column marginal of X and of Y, every ||x||, every "
                  "||y||, and the joint distribution of y across its own "
                  "coordinates.",
        statistic="(a) near-miss sd ratio to the iid prediction sqrt(1/2N); "
                  "(b) correct minus best-of-group; (c) P(correct first). Each "
                  "is computed per candidate group and never pooled.",
        statistic_reads_the_object=(
            "YES, and here is why. Near-miss candidate k has c = s + e_k, so "
            "its phase offset is y_i.(s-c) = -Y[i,k]: the statistic is a "
            "function of Y evaluated in the SAME row i as x_i. Change the "
            "pairing and every near-miss score changes. This is the property "
            "batch 2's NULL-V lacked."),
        sensitivity_demonstration=[
            "SENS-1 (analytic + verified): with y := 0 the near-miss sd ratio "
            "is exactly 0 and correct-minus-best is exactly 0, against ~0.14 "
            "and ~1.5e-3 on the real database. So the statistic reads y.",
            "SENS-2 (ANALYTIC + measured, INSIDE the null's own object class). "
            "E_e[score_j] = mean_i w_i cos(phi_{pi(i),j}) exactly, where "
            "w_i = E_e[cos(2 pi x_i.e/q)] and E_e[sin(.)] = 0 by symmetry of "
            "the rounded Gaussian. By the REARRANGEMENT INEQUALITY the "
            "expected near-miss-0 score over the class of ALL N! pairings is "
            "maximised by co-sorting w with cos(phi_{.,0}) and minimised by "
            "anti-sorting them. Both extremal pairings preserve the exact "
            "multiset of x, the exact multiset of y and every column marginal "
            "-- they are permutations, exactly like the null -- and the two "
            "closed-form extremes are then MEASURED and compared with their "
            "predictions. This exhibits pairings for which the statistic "
            "provably differs, so the statistic is sensitive to the pairing "
            "itself. Field: SENS2_rearrangement_sensitivity_demonstration.",
            "SENS-2c (measured, reported whatever it shows): pairing by matched "
            "LENGTH RANK. Not relied on as the demonstration; recorded because "
            "a null result here is informative about what the statistic reads.",
        ],
        can_it_fail="YES for (a),(b),(c). NO for any statistic built only from "
                    "the correct-secret score: SENS-0 proves that score is "
                    "bitwise invariant under this null.",
    ),
    dict(
        id="NULL-RANDDIR",
        removes_object="everything about the vector family except the two "
                       "length multisets: x and y are both replaced by random "
                       "directions with matched ||x_i|| and ||y_i||.",
        preserves="the multiset of ||x||, the multiset of ||y||, and the "
                  "per-vector pairing of those two lengths.",
        statistic="identical to NULL-ROWPERM's.",
        statistic_reads_the_object="YES -- see NULL-ROWPERM. It additionally "
                                   "reads the integrality and the column "
                                   "structure of Y, which this null also "
                                   "destroys.",
        sensitivity_demonstration=["SENS-1 and SENS-2 as above; both apply "
                                   "unchanged because the statistic is the "
                                   "same."],
        can_it_fail="YES.",
    ),
    dict(
        id="NULL-COLPERM",
        removes_object="the joint structure of Y ACROSS its own coordinates "
                       "(and the x-y pairing with it): each column of Y is "
                       "permuted independently across vectors.",
        preserves="the exact empirical marginal of every single y coordinate, "
                  "and the whole of X.",
        statistic="identical to NULL-ROWPERM's.",
        statistic_reads_the_object="YES. Near-miss candidate k reads column k "
                                   "of Y in row i; permuting that column "
                                   "changes the value in row i.",
        sensitivity_demonstration=["SENS-1 and SENS-2 as above."],
        can_it_fail="YES.",
    ),
    dict(
        id="SENS-0 (a negative control, recorded as a demonstration of the "
           "PD-2 defect, NEVER as evidence about the pairing)",
        removes_object="the x-y pairing (NULL-ROWPERM again).",
        statistic="the CORRECT-secret score mean_i cos(2 pi x_i.e / q) and any "
                  "function of it -- batch 2's NULL-V statistic.",
        statistic_reads_the_object=(
            "NO, PROVABLY. The correct candidate's phase offset is "
            "y_i.(s - s) = 0 for every i, whatever y sits in row i. So the "
            "correct-secret score is BITWISE unchanged by any row permutation "
            "of Y, and its power against this null is exactly zero. Verified "
            "numerically: field SENS0_correct_score_max_abs_change_under_rowperm."),
        sensitivity_demonstration="NONE EXISTS, and that is the point. This "
                                  "pair (object, statistic) admits no "
                                  "sensitivity demonstration, so under PD-2 it "
                                  "is not an admissible null.",
        can_it_fail="NO.",
    ),
]


if __name__ == "__main__":
    main()
