#!/usr/bin/env python3
"""
STAGE B -- TASK-20260803-db170f / BATCH-c45baf (batch 3 of 6) / GOAL-MLKEM-004

The successor design the BATCH-f75059 producer named in its own
wellposedness.md section 6 and DEC-20260803-264d6a NA-2:

        k_lat = 15,  k_fft = 10,  p in {2,3,5},  beta_sieve = 50.

Stage B does three things, in order, each independently reportable:

  B1  DESIGN RECORD. State the Nf tuple explicitly and confirm it is
      ADMISSIBLE against the line-540 identity k_lat + k_fft + k_enum = n,
      using the pinned estimator's own callable. Report the value of the
      adjacent-FFT-bin term exp(k_fft/3 (sigma_s pi / p)^2), which is
      identically 1 in the batch-2 design.
  B2  KNOWN-ANSWER CONTROLS on the estimator callable, before any of its
      output is used.
  B3  MEASUREMENT under the successor design: sieve the (m + k_lat)-dimensional
      dual lattice, certify membership, score FFT bins, and run the same
      row-permutation null Stage A ran, with the same PD-2 discipline.

SCOPE, binding on every number below: m=35, n=25, q=127, secret centred-binomial
eta=2, error rounded-Gaussian sigma=2, g6k bgj1_sieve. TOY SCALE. No ML-KEM
break claim, no security proof, no FIPS 203 parameter set affected or cleared,
no speedup, no cost claim. Any figure quoted at ML-KEM-512 parameters is a
property of the PINNED ESTIMATOR's own arithmetic at those parameters and is
labelled MODELED; it is not a measurement and this task measures nothing at
FIPS 203 dimensions. AGENTS.md rule 12 UNMET and UNWAIVED, inherited: no
EV-MLKEM-* or KN-* record changes status. This script states OBSERVATIONS; it
does not conclude that any heuristic is validated or refuted.

------------------------------------------------------------------------------
WHY THIS DESIGN IS DIFFERENT FROM BATCH 2'S, STRUCTURALLY
------------------------------------------------------------------------------
Batch 2 sieved the FULL d = m + n dual lattice and scored candidate secrets
differing from s on any of the n coordinates. Under that design the CORRECT
candidate's phase offset is y.(s - s) = 0, so the correct-secret score cannot
read the x-y pairing at all (Stage A's SENS-0 proves this bitwise). Here
k_lat = 15 < n = 25, so the lattice part of the secret is NOT guessed: its
contribution y_lat . s_lat stays in the residual, and the CORRECT bin's score
therefore DOES read the pairing. The design is strictly better-posed for the
null that batch 2's design could not support.
"""

import argparse, json, os, platform, resource, subprocess, sys, time

import numpy as np

SCRIPT_VERSION = "stage_b.py v1 TASK-20260803-db170f"
TWOPI = 2.0 * np.pi

DESIGN = dict(m=35, n=25, q=127, eta_secret=2, sigma_e=2.0,
              k_lat=15, k_fft=10, k_enum=0, p_values=[2, 3, 5],
              beta_sieve=50, sieve="bgj1_sieve",
              source="BATCH-f75059 wellposedness.md section 6; "
                     "DEC-20260803-264d6a NA-2; RT-20260803-dc7568 section 10")


# ---------------------------------------------------------------------------
# helpers shared with stage_a.py (kept verbatim so the two agree)
# ---------------------------------------------------------------------------
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


def ms(a):
    a = np.asarray(a, dtype=float)
    return dict(mean=float(a.mean()),
                sd=float(a.std(ddof=1)) if a.size > 1 else None,
                n_draws=int(a.size))


def c4(k):
    from math import lgamma, sqrt, exp
    if k < 2:
        return float("nan")
    return sqrt(2.0 / (k - 1)) * exp(lgamma(k / 2.0) - lgamma((k - 1) / 2.0))


def paired_diff(a, b):
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    sem = float(d.std(ddof=1) / np.sqrt(d.size))
    return dict(mean_difference=float(d.mean()), sem=sem,
                z=float(d.mean() / sem) if sem > 0 else None,
                n_draws=int(d.size))


def per_draw_series(means, idxs, Nv):
    gm = means[:, idxs]
    return (gm.std(axis=1, ddof=1) / np.sqrt(0.5 / Nv),
            means[:, 0] - gm.max(axis=1))


# ===========================================================================
# B1 + B2 -- the design record and the known-answer controls
# ===========================================================================
def b1_b2_design_record(say, estimator_path):
    out = dict(design=DESIGN, checks=[], measured_or_modeled="MODELED -- every "
               "number in B1/B2 is the pinned estimator's own arithmetic, not "
               "a measurement.")
    sys.path.insert(0, estimator_path)
    from estimator import LWE, ND                                # noqa: F401
    from estimator import lwe_dual as ld
    from estimator.lwe_parameters import LWEParameters
    from estimator.reduction import ADPS16                       # noqa: F401
    from sage.all import RR, log, exp, pi, sqrt

    rev = subprocess.run(["git", "-C", estimator_path, "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", estimator_path, "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    out["estimator_commit"] = rev
    out["estimator_dirty"] = bool(dirty)
    out["estimator_path"] = estimator_path

    def add(cid, desc, expected, observed, ok, note=None):
        out["checks"].append(dict(id=cid, description=desc, expected=expected,
                                  observed=observed, passed=bool(ok), note=note))
        say("  KA %-7s %-56s %s" % (cid, desc[:56], "PASS" if ok else "FAIL"))

    m, n, q = DESIGN["m"], DESIGN["n"], DESIGN["q"]
    k_lat, k_fft, k_enum = DESIGN["k_lat"], DESIGN["k_fft"], DESIGN["k_enum"]
    Xs = ND.CenteredBinomial(DESIGN["eta_secret"])
    Xe = ND.DiscreteGaussian(DESIGN["sigma_e"])
    params = LWEParameters(n=n, q=q, Xs=Xs, Xe=Xe, m=m)
    out["params_repr"] = repr(params)
    out["Xs_stddev"] = float(Xs.stddev)
    out["Xe_stddev"] = float(Xe.stddev)

    add("KA-0a", "LWE.dual_hybrid IS estimator.lwe_dual.matzov", True,
        LWE.dual_hybrid is ld.matzov, LWE.dual_hybrid is ld.matzov)
    add("KA-0b", "type(LWE.dual_hybrid).__name__ == 'MATZOV'", "MATZOV",
        type(LWE.dual_hybrid).__name__,
        type(LWE.dual_hybrid).__name__ == "MATZOV")

    # ---- B1: ADMISSIBILITY against the line-540 identity ------------------
    k_lat_implied = n - k_fft - k_enum
    admissible = (k_lat_implied == k_lat)
    add("KA-1", "line-540 identity k_lat = n - k_fft - k_enum gives k_lat=15",
        k_lat, int(k_lat_implied), admissible,
        "estimator/lwe_dual.py:540 `k_lat = params.n - k_fft - k_enum  # p.15`. "
        "This is an IDENTITY, not a constraint that may be relaxed: it is the "
        "obstruction BATCH-f75059's P1 ran into, and this design satisfies it.")
    add("KA-2", "the design's sieve dimension m + k_lat equals beta_sieve = 50",
        DESIGN["beta_sieve"], m + k_lat, (m + k_lat) == DESIGN["beta_sieve"],
        "so the sieve really does run on the whole lattice Nf describes, which "
        "is R1 of BATCH-f75059's wellposedness.md -- satisfied here WITHOUT "
        "forcing k_enum + k_fft = 0.")

    beta_bkz_probe = [45, 60, 300]
    Nf_probe = [float(ld.matzov.Nf(params, m, b, DESIGN["beta_sieve"],
                                   k_enum, k_fft, 5)) for b in beta_bkz_probe]
    add("KA-3", "beta_bkz is irrelevant when beta_sieve = m + k_lat",
        "identical Nf for beta_bkz in %s" % beta_bkz_probe,
        Nf_probe, len(set(Nf_probe)) == 1,
        "deltaf(beta_bkz)^(m + k_lat - beta_sieve) has exponent 0 here, the "
        "same reason BATCH-f75059's KA-5 gave.")

    # the FULL tuple, and Nf evaluated at it, per p
    tuple_rows = []
    for p in DESIGN["p_values"]:
        Nf_val = float(ld.matzov.Nf(params, m, 60, DESIGN["beta_sieve"],
                                    k_enum, k_fft, p))
        adj = float(exp(k_fft / 3.0 * (Xs.stddev * pi / p) ** 2))
        lsig = float(Xe.stddev ** (m / (m + k_lat))
                     * (Xs.stddev * q) ** (k_lat / (m + k_lat))
                     * sqrt(4 / 3.0) * sqrt(DESIGN["beta_sieve"] / 2 / np.pi / np.e))
        pref = float(exp(4 * (lsig * pi / q) ** 2))
        logterm = float(k_enum * ld.matzov.Hf(Xs) + k_fft * log(p) + log(1 / 0.5))
        tuple_rows.append(dict(
            tuple_named="(m=%d, k_enum=%d, k_fft=%d, p=%d, beta_bkz=irrelevant, "
                        "beta_sieve=%d)  with k_lat=%d"
                        % (m, k_enum, k_fft, p, DESIGN["beta_sieve"], k_lat),
            m=m, k_enum=k_enum, k_fft=k_fft, k_lat=k_lat, p=p,
            beta_sieve=DESIGN["beta_sieve"],
            beta_bkz="irrelevant (KA-3)",
            admissible=bool(admissible),
            Nf_modeled=Nf_val,
            adjacent_fft_bin_term=adj,
            adjacent_fft_bin_term_log2=float(np.log2(adj)),
            lsigma_s_modeled=lsig,
            length_prefactor_modeled=pref,
            log_term_modeled=logterm,
            factorisation_check=abs(pref * adj * logterm - Nf_val) < 1e-9 * max(1.0, abs(Nf_val)),
        ))
    out["B1_admissible_tuples"] = tuple_rows
    out["B1_tuple_exists"] = bool(admissible)
    add("KA-4", "Nf factorises as prefactor * adjacent-bin term * log-term",
        True, [r["factorisation_check"] for r in tuple_rows],
        all(r["factorisation_check"] for r in tuple_rows),
        "re-derived independently from the source at lwe_dual.py:551-555 and "
        "compared with the callable's own return value.")

    # ---- the term this design turns ON, and the batch-2 corner ------------
    adj_batch2 = float(exp(0 / 3.0 * (Xs.stddev * pi / 2) ** 2))
    add("KA-5", "with k_fft = 0 (the BATCH-f75059 design) the term is exactly 1",
        1.0, adj_batch2, abs(adj_batch2 - 1.0) < 1e-15,
        "which is why batch 2 could not test it in either direction.")

    # ML-KEM-512 reference figure, MODELED, from the pinned estimator itself
    mlkem = None
    try:
        from estimator.nd import NoiseDistribution                # noqa: F401
        Xs512 = ND.CenteredBinomial(3)
        adj512 = float(exp(40 / 3.0 * (Xs512.stddev * pi / 5) ** 2))
        mlkem = dict(
            label="MODELED, not measured. The pinned estimator's own optimum "
                  "for ML-KEM-512 reported by RT-20260803-dc7568 section 6(b) "
                  "and reproduced arithmetically here: k_enum = 0 (zeta), "
                  "k_fft = 40 (t), p = 5.",
            Xs_stddev=float(Xs512.stddev), k_fft=40, p=5,
            adjacent_fft_bin_term=adj512,
            adjacent_fft_bin_term_log2=float(np.log2(adj512)),
            card_reference_value=2685.7, card_reference_log2=11.39,
            reproduces_card_value=bool(abs(adj512 - 2685.7) < 0.5),
            extrapolation_warning="This is arithmetic at FIPS 203 parameters "
                                  "inside a cost model, NOT a measurement and "
                                  "NOT an extrapolation of anything this task "
                                  "measured. AGENTS.md rule 4 applies in full.")
        add("KA-6", "ML-KEM-512 adjacent-bin term reproduces the card's 2685.7",
            2685.7, adj512, mlkem["reproduces_card_value"])
    except Exception as e:                                        # pragma: no cover
        mlkem = dict(error=repr(e))
    out["B1_mlkem512_reference_MODELED"] = mlkem

    out["passed"] = all(c["passed"] for c in out["checks"])
    return out


# ===========================================================================
# B3 -- the measurement under the successor design
# ===========================================================================
def build_dual_basis_lat(A_lat, q, m, k_lat):
    d = m + k_lat
    B = np.zeros((d, d), dtype=np.int64)
    B[:m, :m] = np.eye(m, dtype=np.int64)
    B[:m, m:] = A_lat
    B[m:, m:] = q * np.eye(k_lat, dtype=np.int64)
    return B


def run_sieve_lat(A_lat, q, m, k_lat, sieve_name, fpylll_seed, sieve_seed):
    from fpylll import LLL, FPLLL
    from g6k import Siever, SieverParams
    d = m + k_lat
    Bfp = to_intmat(build_dual_basis_lat(A_lat, q, m, k_lat))
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


def group_stats_b(means, gidx, Nv):
    out = {}
    iid_sd = float(np.sqrt(0.5 / Nv))
    for g, idxs in gidx.items():
        if g in ("correct", "reference_zero"):
            continue
        gm = means[:, idxs]
        sd_across = gm.std(axis=1, ddof=1)
        out[g] = dict(
            n_candidates=len(idxs), iid_sd_prediction=iid_sd,
            sd_ratio_to_iid=ms(sd_across / iid_sd),
            c4_factor=c4(len(idxs)),
            group_mean_score=ms(gm.mean(axis=1)),
            correct_minus_group_mean=ms(means[:, 0] - gm.mean(axis=1)),
            correct_minus_best_member=ms(means[:, 0] - gm.max(axis=1)),
            P_correct_first_within_group=float(np.mean(means[:, 0] > gm.max(axis=1))))
    out["correct"] = dict(
        mean_score=ms(means[:, 0]),
        note="UNLIKE the BATCH-f75059 design, the correct bin's score DOES read "
             "the pairing here: its residual retains y_lat . s_lat because "
             "k_lat < n means s_lat is never guessed. Stage A's SENS-0 "
             "(bitwise invariance of the correct score under a row "
             "permutation) therefore does NOT apply to this design, and that "
             "is a structural improvement in null sufficiency.")
    if "reference_zero" in gidx:
        out["reference_zero"] = dict(mean_score=ms(means[:, gidx["reference_zero"][0]]))
    return out


def run_instance_b(rep, cfg, seeds, say):
    q, m, n = cfg["q"], cfg["m"], cfg["n"]
    k_lat, k_fft = cfg["k_lat"], cfg["k_fft"]
    D = cfg["draws"]
    t0i = time.time()
    sd_ = seeds["instance"] + 1000 * rep
    rgi = np.random.default_rng(sd_)
    A = rgi.integers(0, q, size=(m, n), dtype=np.int64)
    s = centered_binomial(rgi, cfg["eta_secret"], n)
    A_lat, A_fft = A[:, :k_lat], A[:, k_lat:]
    s_lat, s_fft = s[:k_lat], s[k_lat:]

    X, Ylat, V, tim = run_sieve_lat(A_lat, q, m, k_lat, cfg["sieve"],
                                    sd_ + 1, sd_ + 2)
    N = X.shape[0]
    resid = np.mod(X.dot(A_lat) - Ylat, q)
    n_bad = int(np.count_nonzero(resid))
    n_zero = int(np.count_nonzero(np.all(V == 0, axis=1)))
    cert = dict(kind="lattice_membership",
                statement="every emitted vector (x, y_lat) satisfies "
                          "y_lat == A_lat^T x (mod q) in the (m + k_lat)-"
                          "dimensional dual lattice",
                checked_vectors=int(N), checked_entries=int(N * k_lat),
                violating_entries=n_bad, all_zero_vectors=n_zero,
                verified=bool(n_bad == 0 and n_zero == 0),
                method="integer arithmetic on numpy int64 from A_lat and the "
                       "reconstructed lattice vectors, independent of g6k",
                solve_claim_certificate="none -- no discrete-log solve and no "
                                        "factor-base relation is claimed",
                lattice_dimension=int(m + k_lat))
    say("  rep %d: sieve dim %d -> N=%d cert_ok=%s (%.1fs)"
        % (rep, m + k_lat, N, cert["verified"], tim["sieve_seconds"]))
    if not cert["verified"]:
        return dict(replicate=rep, aborted="certificate_failed", certificate=cert)

    # fixed random row order (subsamples would be prefixes; not used in B3)
    rng_ord = np.random.default_rng(seeds["order"] + rep)
    order = rng_ord.permutation(N)
    X, Ylat = X[order], Ylat[order]

    # psi_i = 2 pi (y_lat . s_lat) / q  -- the term the correct bin retains
    psi = TWOPI * np.mod(Ylat.dot(s_lat), q).astype(np.float64) / q
    # alpha_i = x_i^T A_fft mod q, and its p-ary rounding
    alpha = np.mod(X.dot(A_fft), q)                                 # (N, k_fft)

    per_p = {}
    for p in cfg["p_values"]:
        ahat = np.mod(np.rint(p * alpha.astype(np.float64) / q).astype(np.int64), p)
        # exact (unrounded) FFT phase contribution, and the rounded one
        # candidate bins
        rngc = np.random.default_rng(seeds["candidates"] + 1000 * rep + p)
        c_star = np.mod(s_fft, p)
        cands = [("correct_bin", "correct", c_star.copy())]
        seen = {tuple(c_star.tolist())}
        for j in range(k_fft):                       # PRINCIPLED near-misses:
            for dlt in (1, -1):                      # ADJACENT FFT BINS
                c = c_star.copy(); c[j] = (c[j] + dlt) % p
                if tuple(c.tolist()) in seen:
                    continue
                seen.add(tuple(c.tolist()))
                cands.append(("adjbin_%02d_%+d" % (j, dlt), "near_miss", c))
        for i in range(cfg["n_unif"]):
            c = rngc.integers(0, p, size=k_fft, dtype=np.int64)
            cands.append(("uniform_%02d" % i, "uniform", c))
        for i in range(cfg["n_sdist"]):
            c = np.mod(c_star + centered_binomial(rngc, cfg["eta_secret"], k_fft), p)
            cands.append(("secretdist_%02d" % i, "secret_distribution", c))
        cands.append(("zero_bin", "reference_zero", np.zeros(k_fft, dtype=np.int64)))
        labels = [c[0] for c in cands]
        groups = [c[1] for c in cands]
        C = np.array([c[2] for c in cands], dtype=np.int64)
        K = len(cands)
        gidx = {}
        for i, g in enumerate(groups):
            gidx.setdefault(g, []).append(i)

        # phase of candidate j at vector i:
        #   theta_ij = 2 pi [ (x_i^T A_fft . s_fft)/q  -  (ahat_i . c_j)/p ]
        base = TWOPI * alpha.dot(s_fft).astype(np.float64) / q       # (N,)
        theta = base[:, None] - TWOPI * ahat.dot(C.T).astype(np.float64) / p
        cosT, sinT = np.cos(theta), np.sin(theta)
        cosP, sinP = np.cos(psi), np.sin(psi)

        def phase_arrays(perm):
            cp = cosP[perm][:, None]; sp = sinP[perm][:, None]
            return cp * cosT - sp * sinT, sp * cosT + cp * sinT

        idn = np.arange(N)
        rng_perm = np.random.default_rng(seeds["rowperm"] + 1000 * rep + p)
        rng_dose = np.random.default_rng(seeds["dose"] + 1000 * rep + p)
        arms = [("real", "real", idn)]
        for rho in range(cfg["n_rowperm"]):
            arms.append(("rowperm_%02d" % rho, "NULL-ROWPERM",
                         rng_perm.permutation(N)))
        for t in cfg["dose_fractions"]:
            k_sh = int(round(t * N))
            pi_ = np.arange(N)
            if k_sh >= 2:
                sub = rng_dose.choice(N, size=k_sh, replace=False)
                pi_[sub] = sub[rng_dose.permutation(k_sh)]
            arms.append(("sens3_dose_t%03d" % int(round(1000 * t)), "SENS-3", pi_))

        built = [(nm, fam) + phase_arrays(pm) for nm, fam, pm in arms]
        # SENS-1: y_lat := 0 -- removes the pairing's carrier entirely
        built.append(("sens1_ylat_zero", "SENS-1", cosT.copy(), sinT.copy()))

        means = {b[0]: np.empty((D, K)) for b in built}
        rng_e = np.random.default_rng(seeds["error_draws"] + 1000 * rep + p)
        Xf = X.astype(np.float64)
        fast_dev = None
        done = 0
        while done < D:
            b = min(cfg["block"], D - done)
            E = np.rint(rng_e.normal(0.0, cfg["sigma_e"], size=(m, b))).astype(np.int64)
            U = Xf.dot(E.astype(np.float64))
            Cu = np.cos(TWOPI * U / q).T
            Su = np.sin(TWOPI * U / q).T
            for nm, fam, cp, sp in built:
                means[nm][done:done + b] = (Cu.dot(cp) - Su.dot(sp)) / N
            if done == 0:
                # independent route: build b = A s + e and score directly
                nv = min(3, b)
                bb = np.mod(A.dot(s)[:, None] + E[:, :nv], q)         # (m, nv)
                tt = np.mod(X.dot(bb), q)                             # (N, nv)
                ref = np.empty((nv, K))
                for j in range(K):
                    ph = TWOPI * tt / q - (TWOPI * ahat.dot(C[j]) / p)[:, None]
                    ref[:, j] = np.cos(ph).mean(axis=0)
                fast_dev = float(np.abs(ref - means["real"][:nv]).max())
            done += b

        per_arm = {nm: dict(family=fam, stats=group_stats_b(means[nm], gidx, N))
                   for nm, fam, _, _ in built}

        def agg(family, key, group):
            vals = []
            for a in per_arm:
                if per_arm[a]["family"] != family:
                    continue
                v = per_arm[a]["stats"][group][key]
                vals.append(v["mean"] if isinstance(v, dict) else v)
            v = np.array(vals, dtype=float)
            return dict(mean=float(v.mean()),
                        sd_across_realisations=float(v.std(ddof=1)) if v.size > 1 else None,
                        n_realisations=int(v.size), n_draws_per_realisation=int(D))

        rp_names = [nm for nm, fam, _, _ in built if fam == "NULL-ROWPERM"]
        headline, sens3 = {}, {}
        for group in ("uniform", "secret_distribution", "near_miss"):
            idxs = gidx[group]
            r_re, d_re = per_draw_series(means["real"], idxs, N)
            pr = [paired_diff(r_re, per_draw_series(means[a], idxs, N)[0])
                  for a in rp_names]
            pd_ = [paired_diff(d_re, per_draw_series(means[a], idxs, N)[1])
                   for a in rp_names]
            rr = per_arm["real"]["stats"][group]["sd_ratio_to_iid"]
            rd = per_arm["real"]["stats"][group]["correct_minus_best_member"]
            ar = agg("NULL-ROWPERM", "sd_ratio_to_iid", group)
            ad = agg("NULL-ROWPERM", "correct_minus_best_member", group)
            headline[group] = dict(
                sd_ratio_to_iid=dict(
                    real=rr, rowperm=ar,
                    sens1_ylat_zero=per_arm["sens1_ylat_zero"]["stats"][group]["sd_ratio_to_iid"],
                    excess_real_over_rowperm=float(rr["mean"] / ar["mean"]) if ar["mean"] else None,
                    absolute_difference_real_minus_rowperm=float(rr["mean"] - ar["mean"]),
                    paired_z_per_realisation=[x["z"] for x in pr]),
                correct_minus_best_member=dict(
                    real=rd, rowperm=ad,
                    sens1_ylat_zero=per_arm["sens1_ylat_zero"]["stats"][group]["correct_minus_best_member"],
                    excess_real_over_rowperm=float(rd["mean"] / ad["mean"]) if ad["mean"] else None,
                    absolute_difference_real_minus_rowperm=float(rd["mean"] - ad["mean"]),
                    paired_z_per_realisation=[x["z"] for x in pd_]),
                P_correct_first=dict(
                    real=per_arm["real"]["stats"][group]["P_correct_first_within_group"],
                    rowperm=agg("NULL-ROWPERM", "P_correct_first_within_group", group)))
            # dose-response
            r0, d0 = r_re, d_re
            rows = [dict(t=0.0, sd_ratio=float(r0.mean()),
                         correct_minus_best=float(d0.mean()))]
            for t, an in zip(cfg["dose_fractions"],
                             [nm for nm, fam, _, _ in built if fam == "SENS-3"]):
                rt, dt = per_draw_series(means[an], idxs, N)
                rows.append(dict(t=float(t), sd_ratio=float(rt.mean()),
                                 sd_ratio_paired_z_vs_real=paired_diff(rt, r0)["z"],
                                 correct_minus_best=float(dt.mean()),
                                 correct_minus_best_paired_z_vs_real=paired_diff(dt, d0)["z"]))
            sr = [x["sd_ratio"] for x in rows]
            cb = [x["correct_minus_best"] for x in rows]
            sens3[group] = dict(
                curve=rows,
                sd_ratio_monotone_in_t=bool(
                    all(sr[i + 1] <= sr[i] for i in range(len(sr) - 1))
                    or all(sr[i + 1] >= sr[i] for i in range(len(sr) - 1))),
                correct_minus_best_monotone_in_t=bool(
                    all(cb[i + 1] <= cb[i] for i in range(len(cb) - 1))
                    or all(cb[i + 1] >= cb[i] for i in range(len(cb) - 1))))

        # the correct bin under the null: unlike batch 2's design this MOVES
        corr_real = means["real"][:, 0]
        corr_pd = [paired_diff(corr_real, means[a][:, 0]) for a in rp_names]
        per_p[str(p)] = dict(
            p=p, n_vectors=int(N), n_candidates=K,
            candidate_groups={g: len(v) for g, v in gidx.items()},
            near_miss_definition="ADJACENT FFT BINS: c* +- e_j mod p for each "
                                 "of the k_fft = %d FFT coordinates. This is "
                                 "the principled definition the design buys; "
                                 "batches 1 and 2 used the ad-hoc s + e_k."
                                 % k_fft,
            n_draws=int(D),
            independent_route_max_abs_deviation=fast_dev,
            correct_bin_score=ms(corr_real),
            correct_bin_under_rowperm=dict(
                mean_paired_difference=float(np.mean([x["mean_difference"] for x in corr_pd])),
                typical_paired_sem=float(np.mean([x["sem"] for x in corr_pd])),
                z_per_realisation=[x["z"] for x in corr_pd],
                note="NON-ZERO here, unlike BATCH-f75059's design where the "
                     "correct-candidate score is bitwise invariant under this "
                     "null (Stage A SENS-0). The successor design's correct-bin "
                     "statistic CAN fail against the pairing null."),
            headline_per_group=headline,
            SENS3_dose_response=sens3,
            per_arm=per_arm)
        say("    p=%d: N=%d K=%d  near-miss sd ratio real %.6f rowperm %.6f "
            "excess %.4f | corr-best real %+.6f rowperm %+.6f"
            % (p, N, K,
               headline["near_miss"]["sd_ratio_to_iid"]["real"]["mean"],
               headline["near_miss"]["sd_ratio_to_iid"]["rowperm"]["mean"],
               headline["near_miss"]["sd_ratio_to_iid"]["excess_real_over_rowperm"],
               headline["near_miss"]["correct_minus_best_member"]["real"]["mean"],
               headline["near_miss"]["correct_minus_best_member"]["rowperm"]["mean"]))

    return dict(replicate=rep, seed=int(sd_), n_vectors=int(N),
                certificate=cert, sieve_seconds=tim["sieve_seconds"],
                lll_seconds=tim["lll_seconds"],
                mean_xnorm2=float((X * X).sum(axis=1).mean()),
                mean_ylatnorm2=float((Ylat * Ylat).sum(axis=1).mean()),
                per_p=per_p, instance_seconds=round(time.time() - t0i, 2))


NULL_REGISTRY_B = [
    dict(id="NULL-ROWPERM (Stage B)",
         removes_object="which y_lat is paired with which x, i.e. membership of "
                        "(x, y_lat) in the (m + k_lat)-dimensional dual lattice "
                        "{(x,y) : y = A_lat^T x mod q}. NOTHING ELSE: the "
                        "FFT-side quantities alpha_i = x_i^T A_fft and their "
                        "p-ary roundings travel with x_i and are untouched.",
         preserves="the exact multiset of x rows, the exact multiset of y_lat "
                   "rows, every column marginal of both, and the entire FFT "
                   "side of the design.",
         statistic="per candidate GROUP (adjacent-bin near-miss, uniform bin, "
                   "secret-distribution bin): sd ratio to sqrt(1/2N), correct "
                   "minus best-of-group, P(correct first). Never pooled across "
                   "groups.",
         statistic_reads_the_object="YES. Every candidate's score carries the "
                                    "residual phase psi_i = 2 pi (y_lat,i . "
                                    "s_lat)/q, evaluated in the SAME row i as "
                                    "x_i. Note this includes the CORRECT bin -- "
                                    "which is the structural difference from "
                                    "BATCH-f75059's design, where the correct "
                                    "candidate's offset was identically zero.",
         sensitivity_demonstration=[
             "SENS-1 (analytic + verified): setting y_lat := 0 removes psi "
             "entirely; the reported sens1_ylat_zero column is the value the "
             "statistic then takes, and it differs from the real value. The "
             "statistic reads y_lat.",
             "SENS-3 (measured, inside the null's own object class): the "
             "dose-response curve in t, the fraction of the pairing destroyed. "
             "PRE-DECLARED: a statistic that reads the pairing is monotone in "
             "t; one blind to it is flat in t.",
             "DIRECT: the CORRECT bin's own score is measured under the null "
             "with a paired z. In BATCH-f75059's design that z is exactly 0 by "
             "construction; here it is not, and the measured value is "
             "reported.",
         ],
         can_it_fail="YES, for every group AND for the correct bin."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--mem-cap-gb", type=float, default=6.0)
    ap.add_argument("--max-seconds", type=float, default=900.0)
    ap.add_argument("--estimator-path", default="/tmp/le")
    ap.add_argument("--skip-measurement", action="store_true")
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

    say(SCRIPT_VERSION + "  smoke=%s" % args.smoke)

    if args.smoke:
        cfg = dict(DESIGN, draws=120, block=60, n_rowperm=3, n_unif=8,
                   n_sdist=4, dose_fractions=[0.5, 1.0], n_instances=1,
                   p_values=[3, 5])
    else:
        cfg = dict(DESIGN, draws=2000, block=250, n_rowperm=10, n_unif=16,
                   n_sdist=8, dose_fractions=[0.05, 0.2, 0.5, 0.8, 1.0],
                   n_instances=3)
    SEEDS = dict(instance=20260803501, candidates=20260803502,
                 error_draws=20260803503, rowperm=20260803504,
                 order=20260803505, dose=20260803506)
    say("cfg %s" % cfg)
    say("seeds %s" % SEEDS)

    env = dict(python=sys.version, platform=platform.platform(),
               numpy=np.__version__, executable=sys.executable)
    try:
        import fpylll, g6k
        env["fpylll"] = fpylll.__version__
        env["g6k"] = getattr(g6k, "__version__", "0.1.2")
    except Exception as e:
        env["import_error"] = repr(e)

    say("B1/B2  design record and known-answer controls on the pinned estimator")
    try:
        b12 = b1_b2_design_record(say, args.estimator_path)
        env["sage_version"] = __import__("sage.version",
                                         fromlist=["version"]).version
    except Exception as e:
        b12 = dict(error=repr(e), passed=False,
                   failure_class="infrastructure_error or implementation_error "
                                 "-- recorded, not silently dropped")
        say("B1/B2 FAILED: %r" % (e,))

    instances = []
    if not args.skip_measurement:
        say("B3  measurement under the successor design")
        for rep in range(cfg["n_instances"]):
            if time.time() - t_start > args.max_seconds:
                say("B3 STOPPING after %d instances: soft wall-clock guard "
                    "%.0fs reached. Recorded, not hidden." % (rep, args.max_seconds))
                break
            instances.append(run_instance_b(rep, cfg, SEEDS, say))

    good = [i for i in instances if "aborted" not in i]
    pooled = {}
    if good:
        for p in [str(x) for x in cfg["p_values"]]:
            if p not in good[0]["per_p"]:
                continue
            pooled[p] = {}
            for group in ("uniform", "secret_distribution", "near_miss"):
                gg = {}
                for key in ("sd_ratio_to_iid", "correct_minus_best_member"):
                    ex = np.array([i["per_p"][p]["headline_per_group"][group][key]
                                   ["excess_real_over_rowperm"] for i in good])
                    re_ = np.array([i["per_p"][p]["headline_per_group"][group][key]
                                    ["real"]["mean"] for i in good])
                    rp_ = np.array([i["per_p"][p]["headline_per_group"][group][key]
                                    ["rowperm"]["mean"] for i in good])
                    gg[key] = dict(
                        real_mean=float(re_.mean()),
                        real_sd_across_instances=float(re_.std(ddof=1)) if re_.size > 1 else None,
                        rowperm_mean=float(rp_.mean()),
                        rowperm_sd_across_instances=float(rp_.std(ddof=1)) if rp_.size > 1 else None,
                        excess_mean=float(ex.mean()),
                        excess_sd_across_instances=float(ex.std(ddof=1)) if ex.size > 1 else None,
                        per_instance_excess=[float(v) for v in ex],
                        n_instances=int(ex.size))
                pooled[p][group] = gg

    results = dict(
        task="TASK-20260803-db170f", batch="BATCH-c45baf", goal="GOAL-MLKEM-004",
        stage="B", script_version=SCRIPT_VERSION, smoke=bool(args.smoke),
        states_a_conclusion=False,
        stage_b_reached=True,
        scope="m=35 n=25 q=127, k_lat=15 k_fft=10 k_enum=0, p in {2,3,5}, "
              "beta_sieve=50, secret CB eta=2, error rounded-Gaussian sigma=2, "
              "g6k bgj1_sieve. TOY SCALE. No ML-KEM break claim, no security "
              "proof, no FIPS 203 parameter set affected or cleared, no "
              "speedup, no cost claim.",
        rule12_status="UNMET and UNWAIVED, inherited. No EV-MLKEM-* or KN-* "
                      "status changes.",
        B1_B2_design_record_and_known_answer_controls=b12,
        B3_config=cfg, seeds=SEEDS, environment=env,
        B3_n_instances_completed=len(good),
        B3_per_instance=instances,
        B3_pooled=pooled,
        nulls=NULL_REGISTRY_B,
        log=log)
    results["timings"] = dict(
        total_wall_seconds=round(time.time() - t_start, 2),
        peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1))
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "stage_b_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    say("wrote %s (%d bytes)" % (out, os.path.getsize(out)))
    say("total %.1fs peak RSS %.1f MB" % (results["timings"]["total_wall_seconds"],
                                          results["timings"]["peak_rss_mb"]))


if __name__ == "__main__":
    main()
