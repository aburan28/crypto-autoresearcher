#!/usr/bin/env python3
"""
TASK-20260804-7e6b54 / BATCH-d3a45a (batch 4 of 6) / GOAL-MLKEM-004

T1  the NORM-MATCHED VALID-LATTICE SURROGATE (the deciding check named by
    RT-20260803-d2e23e section 8 and by DEC-20260803-81b778 NA-1)
T2  sd_ratio_to_iid against 1.0 for BOTH arms (NA-2), with a null of the right
    shape and its forced value derived in closed form
T4  Stage B's 10.6x shortfall and the archived null-registry contradiction (NA-4)

SCOPE, binding on every number this script emits: m=35, n=25, d=60, q=127,
secret centred-binomial eta=2, error rounded-Gaussian sigma=2. TOY SCALE.
No ML-KEM break claim, no security proof, no FIPS 203 parameter set affected or
cleared, no speedup, no cost claim, no exponent moved. AGENTS.md rule 12 UNMET
and UNWAIVED, inherited: this script changes the status of no EV-MLKEM-* record
and no KN-* entry. It states OBSERVATIONS. It does not conclude that any
heuristic is validated or refuted.

==============================================================================
PRE-REGISTRATION.  Frozen in this file BEFORE the scoring run.  Not edited
afterwards; the run is scored against it exactly as written.
==============================================================================

WHAT T1 REMOVES AND WHAT IT HOLDS FIXED
    NULL-SIEVE.  Object removed: SIEVE PROVENANCE -- the fact that the vectors
    were produced by g6k bgj1_sieve.  Held fixed: the lattice (the same A, the
    same q), dual-lattice membership y = A^T x mod q (certified by integer
    arithmetic independent of the producing code), the candidate set, the error
    draws, the scoring code, the number of vectors N, and -- row for row -- the
    two norm profiles ||x_i|| and ||y_i||.
    Statistic: excess = sd_ratio_to_iid(family) / mean over row-permutation
    realisations of sd_ratio_to_iid(row-permuted family), near-miss group,
    identical in form to stage_a.py group_stats/per_draw_series.
    Sensitivity demonstration that this statistic can see the object class it
    is being asked about: arm NORMMATCH-RANDDIR, random directions carrying the
    SIEVE'S OWN ||x_i|| and ||y_i|| row for row but NOT in the lattice.  If the
    excess statistic can tell a valid dual family from a norm-identical
    non-lattice family, it has dynamic range on family identity; if it cannot,
    T1's null is inadmissible and is reported as such.

THE FORCED VALUE, DERIVED BEFORE MEASURING (DEC-20260803-81b778)
    Under the null T1 is NOT testing -- H_MEMBERSHIP, the batch-3 red team's
    reading that the excess is forced by y = A^T x mod q at short norms and has
    nothing to do with sieving -- the near-miss score of ANY valid dual family
    is score_k = F(e - a_k) with F(t) = (1/N) sum_i cos(2 pi t.x_i / q), one
    Fourier coefficient of the x-database at a frequency where it is coherent
    because a_k.x_i = Y[i,k] is small.  The size of that coherence is set by
    ||y|| (how small Y is) and the error damping by ||x||.  BOTH are matched row
    for row here.  H_MEMBERSHIP therefore FORCES the matched family to separate,
    at an excess comparable to the sieve arm's.
    Under H_SIEVE -- the excess is a property of sieve-produced vectors -- the
    matched family must NOT separate: excess = 1 within its surrogate spread.

DECISION RULE, declared before the run
    A  H_MEMBERSHIP outcome: matched excess - 1 lies in [0.5, 2.0] x
       (sieve excess - 1) and is significant against the matched family's own
       surrogate-realisation spread.  Reading: the central result of batches
       1-3 is lattice membership, not sieving.
    B  H_SIEVE outcome: sieve excess clearly above 1 while matched excess is
       indistinguishable from 1 (|excess-1| < 2 surrogate sd).  Reading: the
       batch-3 red team is wrong and the effect is about sieving.
    C  neither: matched separates but outside the bracket in A.  Reported as
       partial, with the residual norm mismatch quantified and a norm
       dose-response, and NOT read as either A or B.
    The verdict is emitted mechanically by the code from these thresholds.

T2's NULL AND ITS FORCED VALUE, derived before measuring
    NULL-IID.  Object removed: the SHORTNESS of the candidate-discriminating
    phase offsets.  The dual-attack independence heuristic's own null object is
    "wrong-candidate scores iid N(0, 1/2N)", i.e. phase offsets uniform on the
    circle.  Statistic: sd_ratio_to_iid, near-miss group.
    Sensitivity demonstration: (i) the UNIFORM candidate group of the archived
    producer run already returns 1.000466 pooled over nine instances -- the
    statistic reproduces the iid prediction exactly when offsets are uniform;
    (ii) SENS-1 (y := 0) returns 6.19e-15 -- the statistic reads y.  Dynamic
    range [0, 1] demonstrated on the campaign's own archived data at zero cost.
    Live confirmation arm here: NULL-IID-PHASE, Y replaced by uniform residues
    mod q on the sieve's own X.  Predicted c4(8) = 0.9650304561 (the sample-sd
    bias for k = 8, not 1.0 -- the run is scored against the biased value).
    FORCED VALUE under the null T2 is NOT testing (NULL-ROWPERM, the null the
    campaign spent three batches on):  a row permutation preserves the ||y||
    multiset exactly, and the shortfall below iid is caused by ||y|| being
    short, so the row-permuted arm is FORCED to fail the iid test too:
        sd_ratio_rowperm  ~=  c4(8) . rms(2 pi Y / q) . rms(sin u) / sqrt(1/2),
        rms(sin u)^2 = (1 - exp(-4 a_x)) / 2,   rms(Y)^2 = mean||y||^2 / n.
    Evaluated on the nine archived instances this gives 0.107161 against the
    measured 0.106552 -- 0.6 per cent, 9/9 instances within 1.1 per cent.  The
    campaign's null could never have repaired the quantity that tests the
    heuristic, because it preserves the object that breaks it.

WHAT IS NOT PRE-REGISTERED, STATED PLAINLY
    The T2 derivation above is POST HOC with respect to the nine archived
    instances: those numbers existed before it was written.  It is
    pre-registered only with respect to the arms measured in this run
    (NULL-IID-PHASE, and the matched family's own rowperm arm), whose forced
    values are stated above before the run.
==============================================================================
"""

"""
CHANGELOG (recorded, not hidden -- AGENTS.md rule 8)
  v1  build stage RUN AND RECORDED.  Pool = 260,000 randomised-nearest-plane
      samples over a BKZ-40 basis, 175,351 distinct after de-duplication, of
      which 21 coincided with sieve database vectors and were dropped.  Pool
      ||v||^2: min 275, p05 462, median 749, against the sieve's min 221 /
      median 314 / max 328.  Best injective 2D match therefore left
      mean||x||^2 248.67 vs 181.49 (+37%) and mean||y||^2 226.21 vs 129.08
      (+75%); median |relative error| 20.6% on ||x||, 29.5% on ||y||.
      OBSERVATION, kept: randomised nearest-plane sampling from a BKZ-40 basis
      of this lattice cannot reach the sieve's norm level.  It is better than
      RT-20260803-d2e23e's E3 (470.5 / 331.5) but not norm-matched.
  v2a repaired an output-path bug (repo root was resolved six levels up, not
      seven) that aborted the FIRST scoring run AFTER every arm had been
      measured but BEFORE results.json was written.  The measurement itself
      did not change; the re-run is deterministic and its arm values are
      checked against the aborted run's stdout, which is archived verbatim in
      rebuild_transcript.txt.  Classified implementation_error in the
      reporting path, NOT invalid_measurement.
  v2  (a) rejection sampling: generate in chunks and keep only vectors below a
          norm cut, so the pool concentrates where the sieve's vectors are;
      (b) efficiency fix: the row-permutation realisations were being re-scored
          once per candidate group.  They are now scored once and reused, which
          changes no number, only the cost;
      (c) added arm MATCHED_LONG, a second valid dual family from the same pool
          deliberately built at LONGER norms, giving a norm dose-response so
          that a partial match can still be read.
      The PRE-REGISTRATION block above is UNCHANGED between v1 and v2 and was
      frozen before either run (sha256 of v1: 6b427be2b0286858ba9a34efd3582e9
      edc5e1d0fad54bb39b646bdf3a8e06e11, recorded 2026-08-05T07:02:02Z).
"""

import argparse, hashlib, json, os, platform, resource, sys, time
import numpy as np

SCRIPT_VERSION = "surrogate.py v2 TASK-20260804-7e6b54"
TWOPI = 2.0 * np.pi
Q, M_, N_ = 127, 35, 25
D_ = M_ + N_
SIGMA = 2.0
INSTANCE_SEED = 20260803206          # BATCH-f75059 replicate 0, inherited

# frozen provenance anchors from the archived producer run (replicate 0)
ARCHIVE = dict(
    source="BATCH-c45baf/tasks/TASK-20260803-db170f/stage_a_results.json",
    rep0_seed=20260803206, rep0_n_vectors=17919,
    rep0_a_x=0.888475041394716, rep0_mean_xnorm2=181.49430213739606,
    rep0_mean_ynorm2=129.08153357330208,
    rep0_real_sd_ratio=0.13811512003909213,
    rep0_rowperm_sd_ratio=0.10578664358224973,
    rep0_excess=1.3056007390168005,
    pooled9_real=0.140324, pooled9_rowperm=0.106552, pooled9_excess=1.316946,
    rt_E3_excess_unmatched_bkz=5.4349,
)
PREREG = dict(
    T1_null_id="NULL-SIEVE",
    T1_object_removed="sieve provenance; lattice, dual membership, N, candidates, "
                      "error draws, scoring code and both norm profiles held fixed",
    T1_statistic="near-miss sd_ratio_to_iid excess over the family's own row-permutation arm",
    T1_sensitivity_demonstration="arm NORMMATCH-RANDDIR: the sieve's own ||x_i||,||y_i|| "
                                 "row for row on random directions, NOT in the lattice",
    T1_forced_value_under_H_MEMBERSHIP="matched family MUST separate; excess comparable to the sieve arm",
    T1_forced_value_under_H_SIEVE="matched family must NOT separate; excess = 1",
    T1_decision_rule_A="matched_excess-1 in [0.5,2.0] x (sieve_excess-1) and significant",
    T1_decision_rule_B="sieve separates and |matched_excess-1| < 2 surrogate sd",
    T2_null_id="NULL-IID",
    T2_predicted_iid_arm=0.9650304561473727,
    T2_forced_rowperm_closed_form="c4(8)*rms(2 pi Y/q)*rms(sin u)/sqrt(1/2)",
    T2_forced_rowperm_value_on_archive=0.107161,
    frozen_note="Written into this file before the scoring run and not edited after.",
)


# --------------------------------------------------------------------------
# helpers copied VERBATIM from BATCH-c45baf stage_a.py so the instance
# regenerates bit for bit (identical RNG consumption)
# --------------------------------------------------------------------------
def centered_binomial(rng, eta, size):
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


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


def make_candidates(rng, s, q, n, eta, n_unif, n_sdist, n_near):
    """VERBATIM from BATCH-f75059/compare.py via BATCH-c45baf/stage_a.py."""
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


def c4(k):
    from math import lgamma, sqrt, exp
    return sqrt(2.0 / (k - 1)) * exp(lgamma(k / 2.0) - lgamma((k - 1) / 2.0))


def certify(X, Y, A, q, label):
    """Dual-lattice membership certificate, integer arithmetic, recomputed from A
    and the emitted vectors alone -- independent of whatever produced them."""
    N = X.shape[0]
    resid = np.mod(X.dot(A) - Y, q)
    n_bad = int(np.count_nonzero(resid))
    V = np.concatenate([X, Y], axis=1)
    n_zero = int(np.count_nonzero(np.all(V == 0, axis=1)))
    n_dup = int(N - len(set(map(tuple, V.tolist()))))
    return dict(kind="lattice_membership", family=label,
                statement="every emitted vector v=(x,y) satisfies y == A^T x (mod q)",
                checked_vectors=N, checked_entries=int(N * A.shape[1]),
                violating_entries=n_bad, all_zero_vectors=n_zero,
                duplicate_vectors=n_dup,
                verified=bool(n_bad == 0 and n_zero == 0 and n_dup == 0),
                method="numpy int64 integer arithmetic on A and the emitted vectors",
                solve_claim_certificate="none -- no discrete-log solve and no "
                                        "factor-base relation is claimed")


# --------------------------------------------------------------------------
# the two vector families
# --------------------------------------------------------------------------
def run_sieve(A, q, m, n, sieve_name, fpylll_seed, sieve_seed):
    """VERBATIM from stage_a.py. g6k is used HERE ONLY, to regenerate the
    reference arm. The surrogate family below uses fpylll only."""
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
    return V[:, :m], V[:, m:], dict(lll_seconds=round(t_lll, 3),
                                    sieve_seconds=round(t_sieve, 3))


def bkz_basis(A, q, m, n, seed, schedule, say):
    """fpylll only. KN-TECH-14efa5: BKZ.DEFAULT_STRATEGY is broken in the wheel,
    so pruning-free strategies are built in process."""
    from fpylll import LLL, BKZ, FPLLL, GSO
    from fpylll.fplll.bkz_param import Strategy
    d = m + n
    Bfp = to_intmat(build_dual_basis(A, q, m, n))
    FPLLL.set_random_seed(seed)
    Bfp = LLL.reduction(Bfp)
    strat = [Strategy(b) for b in range(41)]
    prof = []
    for blk, lp in schedule:
        t = time.time()
        Bfp = BKZ.reduction(Bfp, BKZ.Param(block_size=blk, strategies=strat,
                                           max_loops=lp, flags=BKZ.MAX_LOOPS))
        Bn = from_intmat(Bfp)
        nr = (Bn * Bn).sum(axis=1)
        prof.append(dict(block=blk, loops=lp, seconds=round(time.time() - t, 2),
                         b0_norm2=int(nr[0]), min_norm2=int(nr.min()),
                         mean_norm2=float(nr.mean())))
        say("    BKZ-%d x%d %.1fs ||b0||^2=%d min=%d mean=%.0f"
            % (blk, lp, prof[-1]["seconds"], nr[0], nr.min(), nr.mean()))
    Mg = GSO.Mat(Bfp, float_type="d")
    Mg.update_gso()
    mu = np.array([[Mg.get_mu(i, j) if j < i else (1.0 if i == j else 0.0)
                    for j in range(d)] for i in range(d)])
    r = np.array([Mg.get_r(i, i) for i in range(d)])
    return from_intmat(Bfp), mu, r, prof


def sample_pool(Bn, mu, r, windows, per_window, rng, say):
    """Randomised nearest-plane sampling (Schnorr random-sampling style) over the
    BKZ-reduced basis. fpylll produced the basis; the sampler is integer/float
    numpy. NO PAIR REDUCTION IS PERFORMED ANYWHERE -- pair reduction is what a
    sieve does, and this family must not be sieve-produced.

    For a free window [k0, d): draw the top coefficients, then choose every
    lower coefficient by nearest plane, giving ||v||^2 = sum_j t_j^2 r_j with
    |t_j| <= 1/2 below the window. Varying k0 varies the norm level, which is
    how the pool is made to cover the sieve's own (||x||^2,||y||^2) region."""
    d = Bn.shape[0]
    return _sample(Bn, mu, windows, per_window, rng, say, cut=None,
                   time_cap=1e9)[0]


def _one_chunk(Bn, mu, k0, pmass, P, rng):
    d = Bn.shape[0]
    C = np.zeros((P, d), dtype=np.int64)
    w = d - k0
    draw = rng.choice(np.array([-1, 0, 1]), size=(P, w),
                      p=[pmass / 2, 1.0 - pmass, pmass / 2])
    bad = ~draw.any(axis=1)
    if bad.any():
        draw[bad, rng.integers(0, w, size=int(bad.sum()))] = 1
    C[:, k0:] = draw
    acc = C[:, k0:].astype(np.float64).dot(mu[k0:, :])
    for j in range(k0 - 1, -1, -1):
        cj = -np.rint(acc[:, j])
        C[:, j] = cj.astype(np.int64)
        if j:
            acc[:, :j] += cj[:, None] * mu[j, :j][None, :]
    return C.dot(Bn)


def _sample(Bn, mu, windows, per_window, rng, say, cut, time_cap):
    """rejection-sampling variant: keep only vectors with ||v||^2 <= cut, so the
    pool concentrates in the sieve's own norm region. Returns (kept, n_drawn)."""
    out, drawn, t0 = [], 0, time.time()
    for (k0, pmass) in windows:
        done, kept_here = 0, 0
        while done < per_window and time.time() - t0 < time_cap:
            P = min(50000, per_window - done)
            V = _one_chunk(Bn, mu, k0, pmass, P, rng)
            drawn += P
            done += P
            if cut is not None:
                nv = (V * V).sum(axis=1)
                V = V[nv <= cut]
            kept_here += V.shape[0]
            if V.shape[0]:
                out.append(V)
        say("    window k0=%d p=%.2f drew %d kept %d" % (k0, pmass, done, kept_here))
    return (np.concatenate(out, axis=0) if out
            else np.zeros((0, Bn.shape[0]), dtype=np.int64)), drawn


def canonical_keys(V):
    """sign-canonical byte keys, so v and -v collide (they carry the same score
    information: cos is even)."""
    Vc = V.copy()
    nz = np.argmax(Vc != 0, axis=1)
    lead = Vc[np.arange(Vc.shape[0]), nz]
    Vc[lead < 0] *= -1
    return [bytes(row) for row in Vc.astype(np.int64).view(np.uint8).reshape(
        Vc.shape[0], -1)]


def greedy_match(tx, ty, px, py, rng, say):
    """Injective assignment of pool rows to sieve rows minimising the 2D
    normalised mismatch in (||x||^2, ||y||^2), greedy nearest-available in a
    sliding window on ||x||^2."""
    N = tx.size
    ux, uy = float(tx.std()), float(ty.std())
    order_p = np.argsort(px, kind="stable")
    pxs, pys = px[order_p], py[order_p]
    avail = np.ones(pxs.size, dtype=bool)
    # hardest targets (most extreme ||x||^2) first
    tgt_order = np.argsort(-np.abs(tx - tx.mean()), kind="stable")
    assign = np.full(N, -1, dtype=np.int64)
    W0 = 800
    for t in tgt_order:
        pos = int(np.searchsorted(pxs, tx[t]))
        W = W0
        while True:
            lo, hi = max(0, pos - W), min(pxs.size, pos + W)
            sl = np.nonzero(avail[lo:hi])[0]
            if sl.size >= 8 or (lo == 0 and hi == pxs.size):
                break
            W *= 4
        if sl.size == 0:
            continue
        idx = sl + lo
        cost = ((pxs[idx] - tx[t]) / ux) ** 2 + ((pys[idx] - ty[t]) / uy) ** 2
        k = idx[int(np.argmin(cost))]
        avail[k] = False
        assign[t] = order_p[k]
    say("    matched %d/%d targets" % (int((assign >= 0).sum()), N))
    return assign


# --------------------------------------------------------------------------
# scoring core -- identical in form to stage_a.py
# --------------------------------------------------------------------------
def group_index(groups):
    gidx = {}
    for i, g in enumerate(groups):
        gidx.setdefault(g, []).append(i)
    return gidx


def score_family(Xf, cosPhi, sinPhi, D, block, seed, m, q, sigma):
    """means[draw, candidate]. The error draws are reset from `seed` for every
    family, so families with different X are PAIRED on the error sequence -- the
    convention stage_a.py uses for its NULL-RANDDIR arm."""
    N, K = cosPhi.shape
    means = np.empty((D, K))
    rng = np.random.default_rng(seed)
    off = 0
    while off < D:
        b = min(block, D - off)
        E = np.rint(rng.normal(0.0, sigma, size=(m, b))).astype(np.int64)
        U = Xf.dot(E.astype(np.float64))
        Cu = np.cos(TWOPI * U / q).T
        Su = np.sin(TWOPI * U / q).T
        means[off:off + b] = (Cu.dot(cosPhi) - Su.dot(sinPhi)) / N
        off += b
    return means


def sd_ratio(means, idxs, N):
    gm = means[:, idxs]
    return gm.std(axis=1, ddof=1) / np.sqrt(0.5 / N)


def arm_stats(X, Y, s, C, gidx, cfg, seeds, tag, integer_Y=True):
    """family's own pairing plus n_rowperm row-permuted realisations."""
    N = X.shape[0]
    Xf = X.astype(np.float64)
    off = Y.dot((s[None, :] - C).T)
    if integer_Y:
        off = np.mod(off, cfg["q"]).astype(np.float64)
    cosPhi = np.cos(TWOPI * off / cfg["q"])
    sinPhi = np.sin(TWOPI * off / cfg["q"])
    res = {}
    m_real = score_family(Xf, cosPhi, sinPhi, cfg["draws"], cfg["block"],
                          seeds["error_draws"], cfg["m"], cfg["q"], cfg["sigma"])
    # the row-permutation realisations are scored ONCE and reused across the
    # candidate groups (v2 efficiency fix; changes no number, only the cost)
    rng = np.random.default_rng(seeds["rowperm"] + (sum(map(ord, tag)) % 10 ** 6))
    m_rp = []
    for _ in range(cfg["n_rowperm"]):
        pi = rng.permutation(N)
        m_rp.append(score_family(Xf, cosPhi[pi], sinPhi[pi], cfg["draws"],
                                 cfg["block"], seeds["error_draws"], cfg["m"],
                                 cfg["q"], cfg["sigma"]))
    per_group = {}
    for g in ("uniform", "secret_distribution", "near_miss"):
        idxs = gidx[g]
        real = float(sd_ratio(m_real, idxs, N).mean())
        rp = np.array([float(sd_ratio(mm, idxs, N).mean()) for mm in m_rp])
        per_group[g] = dict(
            real_sd_ratio_to_iid=real,
            rowperm_sd_ratio_to_iid_mean=float(rp.mean()),
            rowperm_sd_ratio_to_iid_sd_across_realisations=float(rp.std(ddof=1)),
            n_rowperm_realisations=int(rp.size),
            excess_real_over_rowperm=float(real / rp.mean()),
            excess_z_vs_surrogate_spread=float((real - rp.mean()) /
                                               (rp.std(ddof=1) + 1e-300)),
            factor_below_iid_real=float(1.0 / real) if real > 0 else None,
            factor_below_iid_rowperm=float(1.0 / rp.mean()),
        )
    res["per_group"] = per_group
    res["correct_score_mean"] = float(m_real[:, 0].mean())
    return res


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["build", "score"], required=True)
    ap.add_argument("--work", default="/tmp/t7e6b54_work.npz")
    ap.add_argument("--out", default=None)
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--n-rowperm", type=int, default=6)
    ap.add_argument("--pool-per-window", type=int, default=1200000)
    ap.add_argument("--pool-seconds", type=float, default=110.0)
    ap.add_argument("--mem-cap-gb", type=float, default=6.0)
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

    say(SCRIPT_VERSION + "  stage=" + args.stage)

    cfg = dict(m=M_, n=N_, q=Q, sigma=SIGMA, eta_secret=2,
               draws=args.draws, block=250, n_rowperm=args.n_rowperm,
               sieve="bgj1_sieve")
    seeds = dict(instance=INSTANCE_SEED, error_draws=20260804401,
                 rowperm=20260804402, pool=20260804403, match=20260804404,
                 randdir=20260804405, iidphase=20260804406, bkz=20260804407)

    rgi = np.random.default_rng(INSTANCE_SEED)
    A = rgi.integers(0, Q, size=(M_, N_), dtype=np.int64)
    s = centered_binomial(rgi, 2, N_)

    # ---------------------------------------------------------------- BUILD
    if args.stage == "build":
        say("regenerating BATCH-f75059 replicate 0 (seed %d)" % INSTANCE_SEED)
        Xs, Ys, tim = run_sieve(A, Q, M_, N_, cfg["sieve"],
                                INSTANCE_SEED + 1, INSTANCE_SEED + 2)
        N = Xs.shape[0]
        cert_s = certify(Xs, Ys, A, Q, "SIEVE")
        xs2 = (Xs * Xs).sum(axis=1).astype(np.float64)
        ys2 = (Ys * Ys).sum(axis=1).astype(np.float64)
        a_x = float(2 * np.pi ** 2 * SIGMA ** 2 * xs2.mean() / Q ** 2)
        say("SIEVE  N=%d  cert=%s  mean||x||^2=%.4f mean||y||^2=%.4f a_x=%.15f"
            % (N, cert_s["verified"], xs2.mean(), ys2.mean(), a_x))
        say("  provenance vs archive: a_x delta = %.3e  N match = %s"
            % (abs(a_x - ARCHIVE["rep0_a_x"]), N == ARCHIVE["rep0_n_vectors"]))
        say("  sieve %.1fs lll %.3fs" % (tim["sieve_seconds"], tim["lll_seconds"]))

        say("BKZ (fpylll only, no g6k, no sieve) on the SAME dual basis")
        Bn, mu, r, prof = bkz_basis(A, Q, M_, N_, seeds["bkz"],
                                    [(20, 4), (30, 8), (40, 6)], say)
        say("  GS: r0=%.1f r59=%.3f sum_r=%.1f" % (r[0], r[-1], r.sum()))

        rngp = np.random.default_rng(seeds["pool"])
        wins = [(k0, p) for k0 in (30, 36, 42, 48, 54) for p in (0.25, 0.5)]
        sv2 = xs2 + ys2
        cut = float(sv2.max() * 1.30)
        say("  rejection sampling with cut ||v||^2 <= %.0f (sieve max %.0f)"
            % (cut, sv2.max()))
        Vp, n_drawn = _sample(Bn, mu, wins, args.pool_per_window, rngp, say,
                              cut=cut, time_cap=args.pool_seconds)
        say("  drew %d, kept %d below cut (%.3f%%)"
            % (n_drawn, Vp.shape[0], 100.0 * Vp.shape[0] / max(1, n_drawn)))
        # a deliberately LONGER family from the same construction, for the norm
        # dose-response that lets a partial match still be read
        rngl = np.random.default_rng(seeds["pool"] + 1)
        Vlong, _ = _sample(Bn, mu, [(42, 0.5), (48, 0.5)], 12000, rngl, say,
                           cut=None, time_cap=60.0)
        say("  long family raw %d" % Vlong.shape[0])
        keys = canonical_keys(Vp)
        seen, keep = set(), []
        skeys = set(canonical_keys(np.concatenate([Xs, Ys], axis=1)))
        n_collide = 0
        for i, k in enumerate(keys):
            if k in seen:
                continue
            seen.add(k)
            if k in skeys:
                n_collide += 1
                continue                      # DISJOINTNESS: drop sieve members
            keep.append(i)
        Vp = Vp[np.array(keep, dtype=np.int64)]
        nzero = int(np.count_nonzero(np.all(Vp == 0, axis=1)))
        if nzero:
            Vp = Vp[~np.all(Vp == 0, axis=1)]
        say("  distinct non-zero pool %d (dropped %d that ARE sieve vectors, "
            "%d zero)" % (Vp.shape[0], n_collide, nzero))
        Xp, Yp = Vp[:, :M_], Vp[:, M_:]
        cert_p = certify(Xp, Yp, A, Q, "POOL")
        xp2 = (Xp * Xp).sum(axis=1).astype(np.float64)
        yp2 = (Yp * Yp).sum(axis=1).astype(np.float64)
        say("  POOL cert=%s  mean||x||^2=%.1f mean||y||^2=%.1f  "
            "||v||^2 min=%.0f p05=%.0f med=%.0f"
            % (cert_p["verified"], xp2.mean(), yp2.mean(),
               (xp2 + yp2).min(), np.percentile(xp2 + yp2, 5),
               np.median(xp2 + yp2)))
        say("  SIEVE ||v||^2 min=%.0f med=%.0f max=%.0f"
            % ((xs2 + ys2).min(), np.median(xs2 + ys2), (xs2 + ys2).max()))
        if Vp.shape[0] < N:
            say("  POOL TOO SMALL for N=%d -- recorded, not hidden" % N)

        rngm = np.random.default_rng(seeds["match"])
        assign = greedy_match(xs2, ys2, xp2, yp2, rngm, say)
        ok = assign >= 0
        Xm, Ym = Xp[assign[ok]], Yp[assign[ok]]
        Xs2, Ys2 = Xs[ok], Ys[ok]
        say("MATCH quality on %d rows:" % Xm.shape[0])
        dx = np.sqrt((Xm * Xm).sum(axis=1)) - np.sqrt(xs2[ok])
        dy = np.sqrt((Ym * Ym).sum(axis=1)) - np.sqrt(ys2[ok])
        rx = dx / np.sqrt(xs2[ok])
        ry = dy / np.sqrt(ys2[ok])
        say("  ||x||: mean rel err %+.4f  rms rel err %.4f  median |rel| %.4f"
            % (rx.mean(), np.sqrt((rx ** 2).mean()), np.median(np.abs(rx))))
        say("  ||y||: mean rel err %+.4f  rms rel err %.4f  median |rel| %.4f"
            % (ry.mean(), np.sqrt((ry ** 2).mean()), np.median(np.abs(ry))))
        say("  mean||x||^2 sieve %.2f matched %.2f | mean||y||^2 sieve %.2f "
            "matched %.2f" % (xs2[ok].mean(), (Xm * Xm).sum(axis=1).mean(),
                              ys2[ok].mean(), (Ym * Ym).sum(axis=1).mean()))
        cert_m = certify(Xm, Ym, A, Q, "MATCHED")
        say("  MATCHED cert verified=%s violating=%d dup=%d"
            % (cert_m["verified"], cert_m["violating_entries"],
               cert_m["duplicate_vectors"]))
        # LONG family: same construction, same lattice, no norm matching
        kl, sl = [], set()
        for i, k in enumerate(canonical_keys(Vlong)):
            if k not in sl and k not in skeys:
                sl.add(k); kl.append(i)
        Vlong = Vlong[np.array(kl, dtype=np.int64)][:Xm.shape[0]]
        Xl, Yl = Vlong[:, :M_], Vlong[:, M_:]
        cert_l = certify(Xl, Yl, A, Q, "MATCHED_LONG")
        say("  LONG family N=%d cert=%s mean||x||^2=%.1f mean||y||^2=%.1f"
            % (Xl.shape[0], cert_l["verified"], (Xl * Xl).sum(axis=1).mean(),
               (Yl * Yl).sum(axis=1).mean()))
        np.savez_compressed(
            args.work, A=A, s=s, Xs=Xs2, Ys=Ys2, Xm=Xm, Ym=Ym, Xl=Xl, Yl=Yl,
            xs2=xs2[ok], ys2=ys2[ok], bkz_profile=json.dumps(prof),
            cert_s=json.dumps(cert_s), cert_p=json.dumps(cert_p),
            cert_m=json.dumps(cert_m), cert_l=json.dumps(cert_l),
            tim=json.dumps(tim), n_drawn=n_drawn,
            match_rx=rx, match_ry=ry, pool_size=Vp.shape[0],
            n_collide=n_collide, a_x=a_x, log=json.dumps(log))
        say("wrote %s" % args.work)
        return

    # ---------------------------------------------------------------- SCORE
    Z = np.load(args.work, allow_pickle=False)
    Xs, Ys, Xm, Ym = Z["Xs"], Z["Ys"], Z["Xm"], Z["Ym"]
    N = Xs.shape[0]
    say("loaded work: N=%d sieve, %d matched" % (N, Xm.shape[0]))
    for lbl, Xa, Ya in (("SIEVE", Xs, Ys), ("MATCHED", Xm, Ym)):
        c = certify(Xa, Ya, A, Q, lbl)
        say("  re-certified %s: verified=%s violating=%d/%d dup=%d"
            % (lbl, c["verified"], c["violating_entries"],
               c["checked_entries"], c["duplicate_vectors"]))
        if not c["verified"]:
            say("CERTIFICATE FAILED for %s -- run is invalid_measurement" % lbl)
            return

    rgc = np.random.default_rng(INSTANCE_SEED + 3)
    cands = make_candidates(rgc, s, Q, N_, 2, 8, 4, 8)
    labels = [c[0] for c in cands]
    groups = [c[1] for c in cands]
    C = np.array([c[2] for c in cands], dtype=np.int64)
    gidx = group_index(groups)
    say("candidates: %s" % {g: len(v) for g, v in gidx.items()})

    xs2 = (Xs * Xs).sum(axis=1).astype(np.float64)
    ys2 = (Ys * Ys).sum(axis=1).astype(np.float64)

    arms = {}
    t = time.time()
    arms["SIEVE"] = arm_stats(Xs, Ys, s, C, gidx, cfg, seeds, "SIEVE")
    say("SIEVE arm done %.1fs  near-miss real %.6f rowperm %.6f EXCESS %.4f"
        % (time.time() - t,
           arms["SIEVE"]["per_group"]["near_miss"]["real_sd_ratio_to_iid"],
           arms["SIEVE"]["per_group"]["near_miss"]["rowperm_sd_ratio_to_iid_mean"],
           arms["SIEVE"]["per_group"]["near_miss"]["excess_real_over_rowperm"]))

    t = time.time()
    arms["MATCHED_BKZ"] = arm_stats(Xm, Ym, s, C, gidx, cfg, seeds, "MATCHED")
    say("MATCHED arm done %.1fs  near-miss real %.6f rowperm %.6f EXCESS %.4f"
        % (time.time() - t,
           arms["MATCHED_BKZ"]["per_group"]["near_miss"]["real_sd_ratio_to_iid"],
           arms["MATCHED_BKZ"]["per_group"]["near_miss"]["rowperm_sd_ratio_to_iid_mean"],
           arms["MATCHED_BKZ"]["per_group"]["near_miss"]["excess_real_over_rowperm"]))

    Xl, Yl = Z["Xl"], Z["Yl"]
    cl = certify(Xl, Yl, A, Q, "MATCHED_LONG")
    say("  re-certified MATCHED_LONG: verified=%s violating=%d"
        % (cl["verified"], cl["violating_entries"]))
    t = time.time()
    arms["MATCHED_LONG"] = arm_stats(Xl, Yl, s, C, gidx, cfg, seeds, "LONG")
    say("MATCHED_LONG arm done %.1fs  near-miss EXCESS %.4f  mean||x||^2=%.1f "
        "mean||y||^2=%.1f  (norm dose-response point)"
        % (time.time() - t,
           arms["MATCHED_LONG"]["per_group"]["near_miss"]["excess_real_over_rowperm"],
           (Xl * Xl).sum(axis=1).mean(), (Yl * Yl).sum(axis=1).mean()))

    # sensitivity demonstration for T1's null: the sieve's OWN norms row for
    # row, random directions, NOT in the lattice.
    rngd = np.random.default_rng(seeds["randdir"])
    Gx = rngd.normal(size=(N, M_)); Gx /= np.linalg.norm(Gx, axis=1, keepdims=True)
    Gy = rngd.normal(size=(N, N_)); Gy /= np.linalg.norm(Gy, axis=1, keepdims=True)
    Xr = Gx * np.sqrt(xs2)[:, None]
    Yr = Gy * np.sqrt(ys2)[:, None]
    t = time.time()
    arms["NORMMATCH_RANDDIR"] = arm_stats(Xr, Yr, s, C, gidx, cfg, seeds,
                                          "RANDDIR", integer_Y=False)
    say("RANDDIR arm done %.1fs  near-miss EXCESS %.4f"
        % (time.time() - t,
           arms["NORMMATCH_RANDDIR"]["per_group"]["near_miss"]["excess_real_over_rowperm"]))

    # sensitivity demonstration for T2's null: uniform phase offsets.
    rngi = np.random.default_rng(seeds["iidphase"])
    Yi = rngi.integers(0, Q, size=(N, N_), dtype=np.int64)
    t = time.time()
    arms["NULL_IID_PHASE"] = arm_stats(Xs, Yi, s, C, gidx, cfg, seeds, "IIDPHASE")
    nm = arms["NULL_IID_PHASE"]["per_group"]["near_miss"]
    say("IID-PHASE arm done %.1fs  near-miss sd_ratio %.6f (prereg c4(8)=%.6f)"
        % (time.time() - t, nm["real_sd_ratio_to_iid"], c4(8)))

    # ---------------- T1 verdict, emitted mechanically from the prereg rule
    se = arms["SIEVE"]["per_group"]["near_miss"]["excess_real_over_rowperm"]
    me = arms["MATCHED_BKZ"]["per_group"]["near_miss"]["excess_real_over_rowperm"]
    msd = arms["MATCHED_BKZ"]["per_group"]["near_miss"][
        "rowperm_sd_ratio_to_iid_sd_across_realisations"]
    mreal = arms["MATCHED_BKZ"]["per_group"]["near_miss"]["real_sd_ratio_to_iid"]
    mrp = arms["MATCHED_BKZ"]["per_group"]["near_miss"]["rowperm_sd_ratio_to_iid_mean"]
    mz = (mreal - mrp) / (msd + 1e-300)
    lo, hi = 0.5 * (se - 1.0), 2.0 * (se - 1.0)
    if lo <= (me - 1.0) <= hi and mz > 5.0:
        verdict = "A_MEMBERSHIP"
    elif se > 1.10 and abs(mz) < 2.0:
        verdict = "B_SIEVING"
    else:
        verdict = "C_NEITHER"
    say("T1 VERDICT (mechanical, from the frozen decision rule): %s" % verdict)
    say("   sieve excess %.4f   matched excess %.4f   bracket [%.4f, %.4f]  "
        "matched z vs its own surrogate spread %.1f"
        % (se, me, 1 + lo, 1 + hi, mz))

    # ---------------- T2: archive arithmetic, zero compute
    root = os.path.dirname(os.path.abspath(__file__))
    while root != "/" and not os.path.exists(os.path.join(root, "AGENTS.md")):
        root = os.path.dirname(root)
    ARCH_DIR = os.path.join(root, "coordination/goals/GOAL-MLKEM-004/batches/"
                                  "BATCH-c45baf/tasks/TASK-20260803-db170f")
    arch = json.load(open(os.path.join(ARCH_DIR, "stage_a_results.json")))
    from math import exp, sqrt, pi
    t2_rows = []
    for inst in arch["per_instance"]:
        h = inst["headline_per_group"]["near_miss"]["sd_ratio_to_iid"]
        rmsY = sqrt(inst["mean_ynorm2"] / N_)
        rphi = 2 * pi * rmsY / Q
        ax = inst["a_x_measured"]
        rsin = sqrt((1.0 - exp(-4 * ax)) / 2.0)
        pred = c4(8) * rphi * rsin / sqrt(0.5)
        t2_rows.append(dict(replicate=inst["replicate"],
                            real_sd_ratio_to_iid=h["real"]["mean"],
                            rowperm_sd_ratio_to_iid=h["rowperm"]["mean"],
                            factor_below_iid_real=1.0 / h["real"]["mean"],
                            factor_below_iid_rowperm=1.0 / h["rowperm"]["mean"],
                            forced_rowperm_closed_form=pred,
                            closed_form_over_measured=pred / h["rowperm"]["mean"]))
    po = arch["pooled"]["near_miss"]["sd_ratio_to_iid"]
    t2 = dict(
        status="reported",
        null_id="NULL-IID",
        object_removed="the SHORTNESS of the candidate-discriminating phase "
                       "offsets; the heuristic's own null object is wrong-candidate "
                       "scores iid N(0,1/2N), i.e. uniform phase offsets",
        statistic="sd_ratio_to_iid on the near-miss group, sd across the 8 "
                  "candidates divided by sqrt(1/2N)",
        sensitivity_demonstration=[
            "ARCHIVED, zero compute: the UNIFORM candidate group's real arm "
            "returns %.6f pooled over nine instances -- the statistic "
            "reproduces the iid prediction when offsets are uniform"
            % arch["pooled"]["uniform"]["sd_ratio_to_iid"]["real_mean"],
            "ARCHIVED, zero compute: SENS-1 (y := 0) returns %.3e -- the "
            "statistic reads y"
            % arch["per_instance"][0]["headline_per_group"]["near_miss"][
                "sd_ratio_to_iid"]["sens1_y_zero"]["mean"],
            "LIVE this run: NULL_IID_PHASE arm, uniform residues mod q on the "
            "sieve's own X",
        ],
        prediction_under_the_heuristic=1.0,
        prediction_with_sample_sd_bias_k8=c4(8),
        pooled_real_sd_ratio_to_iid=po["real_mean"],
        pooled_rowperm_sd_ratio_to_iid=po["rowperm_mean"],
        pooled_factor_below_iid_real=1.0 / po["real_mean"],
        pooled_factor_below_iid_rowperm=1.0 / po["rowperm_mean"],
        live_iid_phase_arm=nm["real_sd_ratio_to_iid"],
        per_instance=t2_rows,
        forced_value_derivation=PREREG["T2_forced_rowperm_closed_form"],
        forced_value_pooled=float(np.mean([r["forced_rowperm_closed_form"]
                                           for r in t2_rows])),
        forced_value_max_rel_error=float(max(
            abs(r["closed_form_over_measured"] - 1.0) for r in t2_rows)),
        archived_arms_that_preserve_the_y_multiset={
            k: arch["per_instance"][0]["headline_per_group"]["near_miss"][
                "sd_ratio_to_iid"][k]["mean"]
            for k in ("real", "rowperm", "randdir", "colperm",
                      "sens2_rearrangement_max", "sens2_rearrangement_min",
                      "sens2c_length_sorted")},
    )

    # ---------------- T4
    sb = json.load(open(os.path.join(ARCH_DIR, "stage_b_results.json")))
    tup = sb["B1_B2_design_record_and_known_answer_controls"]["B1_admissible_tuples"]
    nvec = sb["B3_per_instance"][0]["n_vectors"]
    t4 = dict(
        T4a_stage_b_shortfall=dict(
            status="recorded",
            measured_N_vectors=nvec,
            per_instance_N=[i["n_vectors"] for i in sb["B3_per_instance"]],
            modelled_Nf_by_p={str(t["p"]): t["Nf_modeled"] for t in tup},
            shortfall_factor_by_p={str(t["p"]): t["Nf_modeled"] / nvec
                                   for t in tup},
            note="p=2 is the arm carrying the largest deviation (excess "
                 "0.9607 +- 0.0187) and is the only p whose modelled vector "
                 "requirement exceeds what was measured. MODELLED vs MEASURED: "
                 "Nf is a cost-model output, N is a count of sieve vectors.",
            raised_by="VAL-20260803-3fc363 DEF-5; EV-MLKEM-b43de0 OBS-1",
        ),
        T4b_null_registry_contradiction=dict(
            status="resolved",
            json_field=sb["nulls"][0]["statistic_reads_the_object"],
            json_can_it_fail=sb["nulls"][0]["can_it_fail"],
            report_section_5_3="'I have not demonstrated that those group "
                               "statistics can read the pairing in this design'",
            resolution="Both statements are true, of DIFFERENT statistics, and "
                       "the registry entry is wrong because it is unqualified. "
                       "The Stage B null lists three statistics under one "
                       "`statistic` field: the correct-bin score, which DOES "
                       "read the pairing carrier psi_i (paired |z| medians "
                       "14.8-31.3), and the across-candidate GROUP contrasts, "
                       "which do not at first order because psi_i is "
                       "candidate-independent and multiplies every candidate's "
                       "row-i term identically. `statistic_reads_the_object` is "
                       "a property of an (object, statistic) PAIR and must be "
                       "recorded once per statistic, never once per null. A "
                       "consumer reading the JSON reaches the opposite "
                       "conclusion from a consumer reading section 5.3.",
            correction_direction="The JSON field is the defective one. Section "
                                 "5.3 is correct and is the producer applying "
                                 "PD-2 to its own result.",
            archived_and_not_edited=True,
            raised_by="VAL-20260803-3fc363 DEF-4; EV-MLKEM-b43de0 OBS-2",
        ),
    )

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "results.json")
    results = dict(
        task="TASK-20260804-7e6b54", batch="BATCH-d3a45a", goal="GOAL-MLKEM-004",
        script_version=SCRIPT_VERSION, states_a_conclusion=False,
        scope="m=35 n=25 d=60 q=127, secret CB eta=2, error rounded-Gaussian "
              "sigma=2, ONE instance (BATCH-f75059 replicate 0). TOY SCALE. No "
              "ML-KEM break claim, no security proof, no FIPS 203 parameter set "
              "affected or cleared, no speedup, no cost claim, no exponent moved.",
        rule12_status="UNMET and UNWAIVED, inherited. No EV-MLKEM-* or KN-* "
                      "status change.",
        preregistration=PREREG, archive_anchors=ARCHIVE,
        config=cfg, seeds=seeds,
        T1=dict(
            status="completed",
            null_id="NULL-SIEVE",
            object_removed=PREREG["T1_object_removed"],
            statistic=PREREG["T1_statistic"],
            sensitivity_demonstration=PREREG["T1_sensitivity_demonstration"],
            verdict=verdict,
            sieve_excess=se, matched_excess=me,
            bracket_low=1 + lo, bracket_high=1 + hi,
            matched_z_vs_own_surrogate_spread=float(mz),
            arms=arms,
            bkz_profile=json.loads(str(Z["bkz_profile"])),
            certificates=dict(sieve=json.loads(str(Z["cert_s"])),
                              pool=json.loads(str(Z["cert_p"])),
                              matched=json.loads(str(Z["cert_m"])),
                              matched_long=json.loads(str(Z["cert_l"]))),
            pool_size=int(Z["pool_size"]),
            pool_vectors_drawn=int(Z["n_drawn"]),
            pool_vectors_dropped_because_they_ARE_sieve_vectors=int(Z["n_collide"]),
            disjoint_from_sieve_database=True,
            match_quality=dict(
                n_rows=int(Xm.shape[0]),
                xnorm_rel_err_mean=float(Z["match_rx"].mean()),
                xnorm_rel_err_rms=float(np.sqrt((Z["match_rx"] ** 2).mean())),
                xnorm_rel_err_median_abs=float(np.median(np.abs(Z["match_rx"]))),
                ynorm_rel_err_mean=float(Z["match_ry"].mean()),
                ynorm_rel_err_rms=float(np.sqrt((Z["match_ry"] ** 2).mean())),
                ynorm_rel_err_median_abs=float(np.median(np.abs(Z["match_ry"]))),
                sieve_mean_xnorm2=float(xs2.mean()),
                matched_mean_xnorm2=float((Xm * Xm).sum(axis=1).mean()),
                sieve_mean_ynorm2=float(ys2.mean()),
                matched_mean_ynorm2=float((Ym * Ym).sum(axis=1).mean()),
            ),
            norm_dose_response=[
                dict(family="MATCHED_BKZ (best norm match)",
                     mean_xnorm2=float((Xm * Xm).sum(axis=1).mean()),
                     mean_ynorm2=float((Ym * Ym).sum(axis=1).mean()),
                     excess=me),
                dict(family="MATCHED_LONG (same construction, longer)",
                     mean_xnorm2=float((Xl * Xl).sum(axis=1).mean()),
                     mean_ynorm2=float((Yl * Yl).sum(axis=1).mean()),
                     excess=arms["MATCHED_LONG"]["per_group"]["near_miss"][
                         "excess_real_over_rowperm"]),
                dict(family="SIEVE (g6k bgj1)",
                     mean_xnorm2=float(xs2.mean()),
                     mean_ynorm2=float(ys2.mean()), excess=se),
                dict(family="RT-20260803-d2e23e E3 (archived, BKZ sparse +-1)",
                     mean_xnorm2=470.5, mean_ynorm2=331.5,
                     excess=ARCHIVE["rt_E3_excess_unmatched_bkz"],
                     note="archived third-party number, not measured here"),
            ],
            provenance_a_x=float(Z["a_x"]),
            provenance_a_x_delta_vs_archive=float(abs(float(Z["a_x"])
                                                      - ARCHIVE["rep0_a_x"])),
            sieve_timings=json.loads(str(Z["tim"])),
        ),
        T2=t2, T4=t4,
        environment=dict(python=sys.version, platform=platform.platform(),
                         numpy=np.__version__, executable=sys.executable),
        build_log=json.loads(str(Z["log"])), log=log,
    )
    try:
        import fpylll, g6k
        results["environment"]["fpylll"] = fpylll.__version__
        results["environment"]["g6k"] = getattr(g6k, "__version__", "0.1.2")
    except Exception as e:
        results["environment"]["import_error"] = repr(e)
    results["timings"] = dict(
        total_wall_seconds=round(time.time() - t_start, 2),
        peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                          / 1024.0, 1))
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    say("wrote %s (%d bytes)  total %.1fs peak RSS %.1f MB"
        % (out, os.path.getsize(out), results["timings"]["total_wall_seconds"],
           results["timings"]["peak_rss_mb"]))


if __name__ == "__main__":
    main()
